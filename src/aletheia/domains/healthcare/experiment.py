"""Reproducible nested patient CV and one-time locked holdout orchestration."""

from __future__ import annotations

import hashlib
import json
import platform
import tomllib
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import scipy
import sklearn

from .evaluation import (
    calibration_diagnostics,
    cluster_intervals,
    metrics,
    sigmoid_fit,
    sigmoid_predict,
)
from .foundation import (
    SPLIT_LOCK,
    Contracts,
    HealthcareDataError,
    cohort,
    extract,
    feature_views,
    load_contracts,
    load_raw,
    partition,
    verify_split_lock,
)
from .modeling import candidates, fit_predict, group_folds

CONFIG = Path("configs/experiments/healthcare_model_v1.toml")
OUTPUT = Path("artifacts/healthcare-model-v1")


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def write_once(path: Path, value: Any) -> str:
    """Exclusive creation prevents accidental rewriting of published evidence."""
    payload = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(payload)
    return hashlib.sha256(payload.encode()).hexdigest()


def read_record(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def versions() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "scikit_learn": sklearn.__version__,
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
    }


def load_config(path: Path = CONFIG) -> dict[str, Any]:
    with path.open("rb") as stream:
        config = tomllib.load(stream)
    expected = config["software"]
    actual = versions()
    if actual["python"].split(".")[:2] != expected["python"].split(".") or any(
        actual[name] != expected[name] for name in expected if name != "python"
    ):
        raise HealthcareDataError(f"software versions differ: {actual}")
    return config


def verify_identity(
    config: dict[str, Any], contracts: Contracts, lock: dict[str, Any]
) -> None:
    experiment = config["experiment"]
    expected = {
        "dataset_identifier": lock["dataset_identifier"],
        "raw_sha256": lock["dataset_sha256"],
        "feature_policy_version": lock["feature_policy_version"],
        "target_version": lock["target_mapping_version"],
        "split_version": lock["version"],
        "membership_sha256": lock["membership_sha256"],
    }
    if any(experiment[name] != value for name, value in expected.items()):
        raise HealthcareDataError("experiment identity conflicts with split lock")
    if experiment["cohort_version"] != "discharge-alive-v1" or (
        contracts.dataset["cohort"]["expected_rows"] != 99343
    ):
        raise HealthcareDataError("cohort identity mismatch")


def _mean(records: list[dict[str, Any]], name: str) -> float:
    return float(np.mean([row[name] for row in records]))


def _summary(records: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    names = (
        "average_precision",
        "roc_auc",
        "balanced_accuracy",
        "recall",
        "specificity",
        "precision",
        "f1",
        "log_loss",
        "brier_score",
    )
    return {
        name: {
            "mean": _mean(records, name),
            "std": float(np.std([row[name] for row in records], ddof=1)),
        }
        for name in names
    }


def choose_grid(
    contracts: Contracts,
    config: dict[str, Any],
    family: str,
    x: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    folds = group_folds(y, groups, config["cv"]["inner_folds"], seed)
    grid_records = []
    for params in candidates(config)[family]:
        fold_records = []
        for train, valid in folds:
            _, train_p, valid_p, timing = fit_predict(
                contracts,
                config,
                family,
                params,
                x.iloc[train],
                y.iloc[train],
                x.iloc[valid],
                seed=config["experiment"]["seed"],
            )
            fold_records.append(
                {
                    "validation": metrics(y.iloc[valid], valid_p),
                    "training": metrics(y.iloc[train], train_p),
                    "fit_seconds": timing["fit_seconds"],
                    "predict_seconds": timing["predict_seconds"],
                    "convergence_warnings": timing["convergence_warnings"],
                    "validation_patients": int(groups.iloc[valid].nunique()),
                    "transformed_feature_count": len(timing["transformed_features"]),
                    "dense_estimated_bytes": timing["dense_estimated_bytes"],
                }
            )
        valid_rows = [row["validation"] for row in fold_records]
        grid_records.append(
            {
                "params": params,
                "folds": fold_records,
                "validation_summary": _summary(valid_rows),
            }
        )
    ranked = sorted(
        grid_records,
        key=lambda record: (
            -record["validation_summary"]["average_precision"]["mean"],
            record["validation_summary"]["brier_score"]["mean"],
            -record["validation_summary"]["roc_auc"]["mean"],
            record["validation_summary"]["log_loss"]["mean"],
            canonical(record["params"]),
        ),
    )
    return ranked[0]["params"], grid_records


def oof_sigmoid(
    contracts: Contracts,
    config: dict[str, Any],
    family: str,
    params: dict[str, Any],
    x: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    seed: int,
) -> Any:
    oof = np.full(len(y), np.nan)
    for train, valid in group_folds(y, groups, config["cv"]["calibration_folds"], seed):
        _, _, predicted, _ = fit_predict(
            contracts,
            config,
            family,
            params,
            x.iloc[train],
            y.iloc[train],
            x.iloc[valid],
            seed=config["experiment"]["seed"],
        )
        oof[valid] = predicted
    if not np.isfinite(oof).all():
        raise HealthcareDataError("incomplete calibration OOF predictions")
    return sigmoid_fit(y, oof)


def training_evidence(
    contracts: Contracts,
    config: dict[str, Any],
    training: pd.DataFrame,
) -> dict[str, Any]:
    x, _ = feature_views(contracts, training)
    y = training["readmitted_30d"].reset_index(drop=True)
    groups = training["patient_nbr"].reset_index(drop=True)
    x = x.reset_index(drop=True)
    result: dict[str, Any] = {
        "families": {},
        "training_counts": {
            "encounters": len(y),
            "patients": int(groups.nunique()),
            "class_0": int((y == 0).sum()),
            "class_1": int((y == 1).sum()),
        },
    }
    outer = group_folds(
        y, groups, config["cv"]["outer_folds"], config["cv"]["outer_seed"]
    )
    for family in candidates(config):
        family_folds = []
        for index, (train, valid) in enumerate(outer):
            inner_seed = (
                config["experiment"]["seed"] + config["cv"]["inner_seed_offset"] + index
            )
            params, inner = choose_grid(
                contracts,
                config,
                family,
                x.iloc[train].reset_index(drop=True),
                y.iloc[train].reset_index(drop=True),
                groups.iloc[train].reset_index(drop=True),
                inner_seed,
            )
            _, train_p, valid_p, timing = fit_predict(
                contracts,
                config,
                family,
                params,
                x.iloc[train],
                y.iloc[train],
                x.iloc[valid],
                seed=config["experiment"]["seed"],
            )
            calibrator = oof_sigmoid(
                contracts,
                config,
                family,
                params,
                x.iloc[train].reset_index(drop=True),
                y.iloc[train].reset_index(drop=True),
                groups.iloc[train].reset_index(drop=True),
                config["experiment"]["seed"]
                + config["cv"]["calibration_seed_offset"]
                + index,
            )
            calibrated_p = sigmoid_predict(calibrator, valid_p)
            family_folds.append(
                {
                    "fold": index + 1,
                    "selected_params": params,
                    "inner": inner,
                    "raw": metrics(y.iloc[valid], valid_p),
                    "sigmoid": metrics(y.iloc[valid], calibrated_p),
                    "training_raw": metrics(y.iloc[train], train_p),
                    "raw_calibration": calibration_diagnostics(y.iloc[valid], valid_p),
                    "sigmoid_calibration": calibration_diagnostics(
                        y.iloc[valid], calibrated_p
                    ),
                    "fit_seconds": timing["fit_seconds"],
                    "predict_seconds": timing["predict_seconds"],
                    "convergence_warnings": timing["convergence_warnings"],
                    "validation_patients": int(groups.iloc[valid].nunique()),
                    "training_patients": int(groups.iloc[train].nunique()),
                    "transformed_features": timing["transformed_features"],
                    "dense_estimated_bytes": timing["dense_estimated_bytes"],
                }
            )
        result["families"][family] = {
            "folds": family_folds,
            "raw_summary": _summary([row["raw"] for row in family_folds]),
            "sigmoid_summary": _summary([row["sigmoid"] for row in family_folds]),
            "training_raw_summary": _summary(
                [row["training_raw"] for row in family_folds]
            ),
        }
    return result


def deterministic_projection(evidence: dict[str, Any]) -> dict[str, Any]:
    """Remove wall-clock timings; retain every deterministic result and warning."""
    copied = json.loads(json.dumps(evidence))
    for family in copied["families"].values():
        for fold in family["folds"]:
            fold.pop("fit_seconds")
            fold.pop("predict_seconds")
            for grid in fold["inner"]:
                for inner_fold in grid["folds"]:
                    inner_fold.pop("fit_seconds")
                    inner_fold.pop("predict_seconds")
    return copied


def verify_training_record(record: dict[str, Any], config: dict[str, Any]) -> None:
    """Refuse partial or unrelated nested-CV evidence before holdout use."""
    if record.get("identity") != config["experiment"]:
        raise HealthcareDataError("training evidence identity mismatch")
    results = record.get("results", {})
    families = results.get("families", {})
    expected = candidates(config)
    if set(families) != set(expected):
        raise HealthcareDataError("incomplete training families")
    for family, data in families.items():
        folds = data.get("folds", [])
        if len(folds) != config["cv"]["outer_folds"] or {
            fold.get("fold") for fold in folds
        } != set(range(1, config["cv"]["outer_folds"] + 1)):
            raise HealthcareDataError("incomplete outer folds")
        for fold in folds:
            inner = fold.get("inner", [])
            if len(inner) != len(expected[family]) or {
                canonical(item.get("params")) for item in inner
            } != {canonical(params) for params in expected[family]}:
                raise HealthcareDataError("incomplete inner grid")
            if any(
                len(item.get("folds", [])) != config["cv"]["inner_folds"]
                for item in inner
            ):
                raise HealthcareDataError("incomplete inner folds")
            if any(name not in fold for name in ("raw", "sigmoid", "training_raw")):
                raise HealthcareDataError("incomplete outer metrics")
        if any(
            name not in data
            for name in ("raw_summary", "sigmoid_summary", "training_raw_summary")
        ):
            raise HealthcareDataError("incomplete training summaries")
    if record.get("deterministic_sha256") != digest(deterministic_projection(results)):
        raise HealthcareDataError("training evidence checksum mismatch")


def select_protocol(evidence: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    options = []
    for family in candidates(config):
        if family not in evidence["families"]:
            continue
        record = evidence["families"][family]
        for method in ("raw", "sigmoid"):
            summary = record[f"{method}_summary"]
            options.append(
                {"family": family, "calibration": method, "summary": summary}
            )
    best_ap = max(option["summary"]["average_precision"]["mean"] for option in options)
    margin = config["selection"]["ap_equivalence_margin"]
    eligible = [
        option
        for option in options
        if best_ap - option["summary"]["average_precision"]["mean"] <= margin
    ]
    winner = min(
        eligible,
        key=lambda option: (
            option["summary"]["brier_score"]["mean"],
            -option["summary"]["roc_auc"]["mean"],
            option["summary"]["log_loss"]["mean"],
            option["family"],
            option["calibration"],
        ),
    )
    return {"winner": winner, "best_ap": best_ap, "eligible": eligible, "all": options}


def save_artifact(
    path: Path, model: Any, calibrator: Any, identity: dict[str, Any]
) -> dict[str, Any]:
    if path.exists():
        raise HealthcareDataError("fitted artifact already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "calibrator": calibrator}, path)
    return {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "versions": versions(),
        "protocol_sha256": digest(identity),
        "path": path.name,
    }


def load_trusted_artifact(
    path: Path, manifest: dict[str, Any], identity: dict[str, Any]
) -> dict[str, Any]:
    """Only load a project-generated local joblib after hash/version/protocol checks."""
    if path.name != manifest["path"] or path.parent.name != "healthcare-model-v1":
        raise HealthcareDataError("artifact is outside trusted project run")
    if manifest["versions"] != versions() or manifest["protocol_sha256"] != digest(
        identity
    ):
        raise HealthcareDataError("artifact version or protocol mismatch")
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["sha256"]:
        raise HealthcareDataError("artifact checksum mismatch")
    return joblib.load(path)


def evaluate_once(
    output: Path,
    config: dict[str, Any],
    contracts: Contracts,
    frame: pd.DataFrame,
    selection: dict[str, Any],
    artifact_manifest: dict[str, Any],
) -> dict[str, Any]:
    """Reserve evaluation before any held-out prediction; a failure consumes the run."""
    saved = read_record(output / "selection.json")
    if saved != selection or saved["selection_sha256"] != digest(saved["protocol"]):
        raise HealthcareDataError("frozen selection checksum mismatch")
    training_record = read_record(output / "nested_cv.json")
    verify_training_record(training_record, config)
    protocol = saved["protocol"]
    if (
        protocol["config_sha256"] != hashlib.sha256(CONFIG.read_bytes()).hexdigest()
        or protocol["nested_cv_sha256"] != training_record["deterministic_sha256"]
        or saved["selection_evidence"]
        != select_protocol(training_record["results"], config)
        or protocol["family"] != saved["selection_evidence"]["winner"]["family"]
        or protocol["calibration"]
        != saved["selection_evidence"]["winner"]["calibration"]
    ):
        raise HealthcareDataError(
            "selection is not bound to complete training evidence"
        )
    lock = verify_split_lock(contracts, frame, SPLIT_LOCK)
    verify_identity(config, contracts, lock)
    if saved["identity_sha256"] != digest(config["experiment"]) or (
        artifact_manifest != read_record(output / "artifact.json")
    ):
        raise HealthcareDataError("evaluation identity mismatch")
    marker = output / "holdout.claim"
    try:
        marker.open("x").close()
    except FileExistsError as exc:
        raise HealthcareDataError("holdout already evaluated or reserved") from exc
    # The holdout frame is materialized only after the irreversible claim.
    _, holdout = partition(contracts, frame, SPLIT_LOCK)
    x, _ = feature_views(contracts, holdout)
    trusted = load_trusted_artifact(
        output / "model.joblib", artifact_manifest, saved["protocol"]
    )
    probability = trusted["model"].predict_proba(x)[:, 1]
    if trusted["calibrator"] is not None:
        probability = sigmoid_predict(trusted["calibrator"], probability)
    truth = holdout["readmitted_30d"]
    record = {
        "experiment": config["experiment"]["version"],
        "selection_sha256": saved["selection_sha256"],
        "artifact_sha256": artifact_manifest["sha256"],
        "counts": {
            "encounters": len(holdout),
            "patients": int(holdout["patient_nbr"].nunique()),
        },
        "metrics": metrics(truth, probability),
        "calibration": calibration_diagnostics(truth, probability),
        "patient_cluster_bootstrap": {
            "repetitions": config["bootstrap"]["repetitions"],
            "seed": config["bootstrap"]["seed"],
            "intervals_95": cluster_intervals(
                truth,
                probability,
                holdout["patient_nbr"],
                repetitions=config["bootstrap"]["repetitions"],
                seed=config["bootstrap"]["seed"],
            ),
        },
    }
    write_once(output / "holdout.json", record)
    return record


def run_training_only(
    contracts: Contracts, config: dict[str, Any], frame: pd.DataFrame
) -> tuple[dict[str, Any], pd.DataFrame]:
    lock = verify_split_lock(contracts, frame, SPLIT_LOCK)
    verify_identity(config, contracts, lock)
    train, _ = partition(contracts, frame, SPLIT_LOCK)
    return training_evidence(contracts, config, train), train


def run(output: Path = OUTPUT) -> dict[str, Any]:
    """Run two training-only calculations, freeze selection, then one holdout."""
    if output.exists():
        raise HealthcareDataError("experiment directory exists; refusing rerun")
    config = load_config()
    contracts = load_contracts()
    archive = Path("data/raw/healthcare/diabetes_130_us_hospitals_1999_2008.zip")
    raw, _ = extract(contracts, archive, archive.parent)
    frame = cohort(contracts, load_raw(contracts, raw))
    first, train = run_training_only(contracts, config, frame)
    second, _ = run_training_only(contracts, config, frame)
    if deterministic_projection(first) != deterministic_projection(second):
        raise HealthcareDataError("training-only deterministic repeat differs")
    evidence = {
        "identity": config["experiment"],
        "results": first,
        "deterministic_sha256": digest(deterministic_projection(first)),
    }
    verify_training_record(evidence, config)
    write_once(output / "nested_cv.json", evidence)
    selection = select_protocol(first, config)
    family = selection["winner"]["family"]
    x, _ = feature_views(contracts, train)
    y = train["readmitted_30d"].reset_index(drop=True)
    groups = train["patient_nbr"].reset_index(drop=True)
    x = x.reset_index(drop=True)
    final_params, final_grid = choose_grid(
        contracts,
        config,
        family,
        x,
        y,
        groups,
        config["experiment"]["seed"] + config["cv"]["inner_seed_offset"] + 99,
    )
    protocol = {
        "family": family,
        "params": final_params,
        "calibration": selection["winner"]["calibration"],
        "config_sha256": hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        "nested_cv_sha256": evidence["deterministic_sha256"],
    }
    frozen = {
        "protocol": protocol,
        "selection_sha256": digest(protocol),
        "identity_sha256": digest(config["experiment"]),
        "selection_evidence": selection,
        "final_inner_grid": final_grid,
    }
    write_once(output / "selection.json", frozen)
    fitted, _, _, timing = fit_predict(
        contracts,
        config,
        family,
        final_params,
        x,
        y,
        x.iloc[:1],
        seed=config["experiment"]["seed"],
    )
    calibrator = None
    if protocol["calibration"] == "sigmoid":
        calibrator = oof_sigmoid(
            contracts,
            config,
            family,
            final_params,
            x,
            y,
            groups,
            config["experiment"]["seed"] + config["cv"]["calibration_seed_offset"] + 99,
        )
    artifact = save_artifact(output / "model.joblib", fitted, calibrator, protocol)
    artifact["transformed_features"] = timing["transformed_features"]
    write_once(output / "artifact.json", artifact)
    holdout = evaluate_once(output, config, contracts, frame, frozen, artifact)
    return {
        "nested_cv": evidence,
        "selection": frozen,
        "artifact": artifact,
        "holdout": holdout,
    }
