"""Freeze tested methodology, then publish one privacy-bounded healthcare audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from .counterfactual import assess, scenario_result
from .experiment import (
    CONFIG as MODEL_CONFIG,
)
from .experiment import (
    OUTPUT as MODEL_RUN,
)
from .experiment import (
    digest,
    load_trusted_artifact,
    read_record,
    select_protocol,
    verify_identity,
    verify_training_record,
    versions,
    write_once,
)
from .experiment import (
    load_config as load_model_config,
)
from .explain import (
    feature_mapping,
    global_explanation,
    local_explanation,
    probability,
)
from .fairness import GROUPS, METRICS, audit_subgroups
from .foundation import (
    DATASET_CONFIG,
    FEATURE_CONFIG,
    SPLIT_CONFIG,
    SPLIT_LOCK,
    HealthcareDataError,
    cohort,
    feature_views,
    load_contracts,
    load_raw,
    partition,
    verify_split_lock,
)
from .stability import analyze_stability

CONFIG = Path("configs/audit/healthcare_audit_v1.toml")
OUTPUT = Path("artifacts/healthcare-audit-v1")
SOURCE = Path("src/aletheia/domains/healthcare")
RESULT_KEYS = {
    "identity",
    "mapping",
    "global",
    "synthetic_local",
    "stability",
    "fairness",
    "counterfactual",
    "calibration",
    "holdout_access",
    "limitations",
}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bindings() -> dict[str, str]:
    paths = [
        CONFIG,
        MODEL_CONFIG,
        DATASET_CONFIG,
        FEATURE_CONFIG,
        SPLIT_CONFIG,
        SPLIT_LOCK,
    ]
    paths += sorted(SOURCE.glob("*.py"))
    paths += sorted(Path("tests/healthcare").glob("test_audit*.py"))
    paths += [
        MODEL_RUN / name
        for name in (
            "artifact.json",
            "model.joblib",
            "selection.json",
            "nested_cv.json",
            "holdout.json",
            "holdout.claim",
        )
    ]
    return {path.as_posix(): file_hash(path) for path in paths}


def load_protocol() -> dict[str, Any]:
    with CONFIG.open("rb") as stream:
        config = tomllib.load(stream)
    contracts = load_contracts()
    assess(contracts, config["counterfactual"])
    if (
        config["audit"]["version"] != "healthcare-audit-v1"
        or config["explanation"]["output"]
        != "calibrated probability of readmitted_30d=1"
        or config["explanation"]["permutations"] < 1
        or config["fairness"]["attributes"] != ["race", "gender", "age"]
        or config["fairness"]["threshold"] != 0.5
        or config["fairness"]["confidence"] != 0.95
        or any(
            config["privacy"][name]
            for name in (
                "real_local_records",
                "patient_predictions",
                "identifiers",
                "raw_records",
            )
        )
        or set(config["synthetic_example"])
        != set(contracts.features["roles"]["prediction"])
    ):
        raise HealthcareDataError("invalid audit protocol")
    if any(
        config["fairness"][f"minimum_{name}"] < 20
        for name in ("encounters", "patients", "positive", "negative")
    ):
        raise HealthcareDataError("unsafe minimum support")
    return config


def verify_model(config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    model_config = load_model_config()
    contracts = load_contracts()
    lock = read_record(SPLIT_LOCK)
    verify_identity(model_config, contracts, lock)
    nested = read_record(MODEL_RUN / "nested_cv.json")
    selection = read_record(MODEL_RUN / "selection.json")
    manifest = read_record(MODEL_RUN / "artifact.json")
    holdout = read_record(MODEL_RUN / "holdout.json")
    verify_training_record(nested, model_config)
    protocol = selection["protocol"]
    if (
        selection["selection_sha256"] != digest(protocol)
        or selection["selection_sha256"] != config["audit"]["selection_sha256"]
        or selection["identity_sha256"] != digest(model_config["experiment"])
        or protocol["config_sha256"] != file_hash(MODEL_CONFIG)
        or protocol["nested_cv_sha256"] != nested["deterministic_sha256"]
        or selection["selection_evidence"]
        != select_protocol(nested["results"], model_config)
        or protocol["family"] != "histogram"
        or protocol["calibration"] != "sigmoid"
        or manifest["sha256"] != config["audit"]["model_sha256"]
        or holdout["artifact_sha256"] != manifest["sha256"]
        or holdout["selection_sha256"] != selection["selection_sha256"]
        or not (MODEL_RUN / "holdout.claim").exists()
    ):
        raise HealthcareDataError("frozen model/evidence binding mismatch")
    bundle = load_trusted_artifact(MODEL_RUN / "model.joblib", manifest, protocol)
    mapping = feature_mapping(contracts, bundle["model"])
    if (
        [row["transformed"] for row in mapping] != manifest["transformed_features"]
        or (
            list(bundle["model"].feature_names_in_)
            != contracts.features["roles"]["prediction"]
        )
        or bundle["calibrator"] is None
    ):
        raise HealthcareDataError("frozen pipeline/feature/calibration mismatch")
    return bundle, {
        "dataset": model_config["experiment"],
        "model_sha256": manifest["sha256"],
        "selection_sha256": selection["selection_sha256"],
        "split_lock_sha256": file_hash(SPLIT_LOCK),
    }


def freeze() -> dict[str, Any]:
    """This reads no patient inputs and calculates no audit outcomes."""
    config = load_protocol()
    _, identity = verify_model(config)
    if OUTPUT.exists():
        raise HealthcareDataError("audit run exists; refusing protocol overwrite")
    OUTPUT.mkdir(parents=True, exist_ok=False)
    record = {
        "config": config,
        "config_sha256": file_hash(CONFIG),
        "protocol_sha256": digest(config),
        "bindings": bindings(),
        "identity": identity,
        "versions": versions(),
        "created_at": datetime.now(UTC).isoformat(),
        "git_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "holdout_access": (
            "not accessed by this audit; existing model evaluation preserved"
        ),
    }
    write_once(OUTPUT / "protocol.json", record)
    return record


def verified_protocol() -> dict[str, Any]:
    frozen = read_record(OUTPUT / "protocol.json")
    config = load_protocol()
    if (
        frozen["config"] != config
        or frozen["config_sha256"] != file_hash(CONFIG)
        or (frozen["protocol_sha256"] != digest(config))
        or frozen["bindings"] != bindings()
        or frozen["versions"] != versions()
    ):
        raise HealthcareDataError("audit protocol/config/code/model binding mismatch")
    _, identity = verify_model(config)
    if identity != frozen["identity"]:
        raise HealthcareDataError("audit identity mismatch")
    return frozen


def claim_holdout(frozen: dict[str, Any]) -> None:
    """Exclusive persistent claim; failure consumes access; no alternate run path."""
    if frozen != verified_protocol():
        raise HealthcareDataError("unverified protocol at holdout claim")
    try:
        write_once(
            OUTPUT / "holdout.claim",
            {
                "protocol_sha256": frozen["protocol_sha256"],
                "model_sha256": frozen["identity"]["model_sha256"],
                "created_at": datetime.now(UTC).isoformat(),
                "purpose": (
                    "one post-selection subgroup audit; "
                    "no fitting, selection or threshold tuning"
                ),
            },
        )
    except FileExistsError as exc:
        raise HealthcareDataError("holdout audit already claimed; no retry") from exc


def _keys(value: dict[str, Any], expected: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise HealthcareDataError("publication schema/privacy violation")


def validate_publication(result: dict[str, Any], config: dict[str, Any]) -> None:
    """Allowlist result shape and synthetic values before publication."""
    _keys(result, RESULT_KEYS)
    contracts = load_contracts()
    fields = contracts.features["roles"]["prediction"]
    for row in result["mapping"]:
        _keys(row, {"source", "transformed"})
        if row["source"] not in fields:
            raise HealthcareDataError("forbidden mapping field")
    global_result = result["global"]
    _keys(
        global_result,
        {
            "method",
            "output",
            "population",
            "sample_size_per_repeat",
            "seeds",
            "baselines",
            "features",
            "limitations",
        },
    )
    if [row["field"] for row in global_result["features"]] != fields:
        raise HealthcareDataError("global source-field mismatch")
    for row in global_result["features"]:
        _keys(
            row,
            {
                "field",
                "mean_absolute_contribution",
                "repeat_min",
                "repeat_max",
                "repeat_values",
            },
        )
        if len(row["repeat_values"]) != len(config["explanation"]["sample_seeds"]):
            raise HealthcareDataError("unrestricted attribution vector")
    local = result["synthetic_local"]
    _keys(
        local,
        {
            "identity",
            "method",
            "output",
            "baseline",
            "probability",
            "features",
            "limitations",
        },
    )
    if (
        local["identity"] != result["identity"]
        or [row["field"] for row in local["features"]] != fields
    ):
        raise HealthcareDataError("local identity/source mismatch")
    for row in local["features"]:
        _keys(row, {"field", "value", "contribution", "direction"})
        if row["value"] != config["synthetic_example"][row["field"]]:
            raise HealthcareDataError("real patient values cannot be published")
    if result["counterfactual"] != scenario_result(contracts, config["counterfactual"]):
        raise HealthcareDataError("unapproved counterfactual evidence")
    stability = result["stability"]
    _keys(
        stability,
        {
            "population",
            "comparisons",
            "boundary_crossings",
            "unchanged_at_bound",
            "bounds",
            "all",
            "same_class",
            "crossed_class",
            "mean_absolute_probability_change",
            "max_absolute_probability_change",
            "below_overlap_reference",
            "above_distance_reference",
            "limitations",
        },
    )
    _keys(stability["bounds"], set(config["stability"]["fields"]))
    for name in ("all", "same_class", "crossed_class"):
        _keys(
            stability[name],
            {"top_k_overlap", "absolute_rank_correlation", "normalized_l1"},
        )
        for values in stability[name].values():
            _keys(values, {"mean", "min", "max", "undefined"})
    groups = result["fairness"]
    expected_groups = [
        (attr, group)
        for attr in config["fairness"]["attributes"]
        for group in GROUPS[attr]
    ]
    if [(row["attribute"], row["group"]) for row in groups] != expected_groups:
        raise HealthcareDataError("unexpected subgroup publication")
    for row in groups:
        _keys(
            row,
            {
                "attribute",
                "group",
                "counts",
                "status",
                "reason",
                "metrics",
                "uncertainty",
            },
        )
        _keys(row["counts"], {"encounters", "patients", "positive", "negative"})
        for count in row["counts"].values():
            if (
                not (
                    isinstance(count, int)
                    and count >= config["fairness"]["privacy_count_floor"]
                )
                and count != f"<{config['fairness']['privacy_count_floor']}"
            ):
                raise HealthcareDataError("small exact subgroup count")
        if row["status"] == "supported":
            _keys(row["metrics"], set(METRICS))
            _keys(row["uncertainty"], set(METRICS))
            for values in row["uncertainty"].values():
                _keys(values, {"interval", "valid_replicates", "undefined_replicates"})
        elif (
            row["status"] != "insufficient_support"
            or row["metrics"] is not None
            or row["uncertainty"] is not None
        ):
            raise HealthcareDataError("unsupported subgroup metrics")
    _keys(
        result["calibration"],
        {"input", "output", "coefficient", "intercept", "semantics"},
    )
    _keys(
        result["holdout_access"],
        {"status", "purpose", "claim_sha256", "encounters", "patients"},
    )

    # Values in aggregate numeric slots must not smuggle arrays or row dictionaries.
    def numeric(value: Any) -> None:
        if value is not None and (
            type(value) not in (float, int) or not np.isfinite(value)
        ):
            raise HealthcareDataError("nonnumeric aggregate/privacy violation")

    for row in global_result["features"]:
        for name in ("mean_absolute_contribution", "repeat_min", "repeat_max"):
            numeric(row[name])
        for value in row["repeat_values"]:
            numeric(value)
    for row in groups:
        if row["metrics"] is not None:
            for value in row["metrics"].values():
                numeric(value)
            for entry in row["uncertainty"].values():
                if entry["interval"] is not None:
                    if (
                        not isinstance(entry["interval"], list)
                        or len(entry["interval"]) != 2
                    ):
                        raise HealthcareDataError("unrestricted uncertainty vector")
                    for value in entry["interval"]:
                        numeric(value)
                numeric(entry["valid_replicates"])
                numeric(entry["undefined_replicates"])
    if len(global_result["baselines"]) != len(config["explanation"]["sample_seeds"]):
        raise HealthcareDataError("unrestricted baseline vector")
    for value in global_result["baselines"]:
        numeric(value)
    numeric(local["probability"])
    numeric(local["baseline"])
    for row in local["features"]:
        numeric(row["contribution"])
    for name in ("all", "same_class", "crossed_class"):
        for entry in stability[name].values():
            for value in entry.values():
                numeric(value)
    for name in (
        "comparisons",
        "boundary_crossings",
        "unchanged_at_bound",
        "mean_absolute_probability_change",
        "max_absolute_probability_change",
        "below_overlap_reference",
        "above_distance_reference",
    ):
        numeric(stability[name])
    json.dumps(result, allow_nan=False)


def run() -> dict[str, Any]:
    frozen = verified_protocol()
    if (OUTPUT / "results.json").exists() or (OUTPUT / "holdout.claim").exists():
        raise HealthcareDataError("audit already performed or claimed; refusing rerun")
    config = frozen["config"]
    contracts = load_contracts()
    bundle, identity = verify_model(config)
    frame = cohort(
        contracts, load_raw(contracts, Path("data/raw/healthcare/diabetic_data.csv"))
    )
    verify_split_lock(contracts, frame, SPLIT_LOCK)
    training, _ = partition(contracts, frame, SPLIT_LOCK)
    x, _ = feature_views(contracts, training)
    background = x.sample(
        n=config["explanation"]["background_size"],
        random_state=config["explanation"]["background_seed"],
    )
    synthetic = pd.DataFrame([config["synthetic_example"]])[list(x)]
    with threadpool_limits(limits=1):
        global_result = global_explanation(
            contracts, bundle, x, background, config["explanation"]
        )
        local = local_explanation(
            contracts, bundle, synthetic, background, config["explanation"], identity
        )
        stability = analyze_stability(
            contracts, bundle, x, background, config["explanation"], config["stability"]
        )
        claim_holdout(frozen)
        _, holdout = partition(contracts, frame, SPLIT_LOCK)
        predictors, audit = feature_views(contracts, holdout)
        p = probability(bundle, predictors)
        fairness = audit_subgroups(
            audit,
            holdout["readmitted_30d"],
            pd.Series(p, index=holdout.index),
            holdout["patient_nbr"],
            config["fairness"],
        )
    # Prove original model, split, config and evidence still match frozen bindings.
    verified_protocol()
    calibrator = bundle["calibrator"]
    result = {
        "identity": identity,
        "mapping": feature_mapping(contracts, bundle["model"]),
        "global": global_result,
        "synthetic_local": local,
        "stability": stability,
        "fairness": fairness,
        "counterfactual": scenario_result(contracts, config["counterfactual"]),
        "calibration": {
            "input": "clipped base probability logit",
            "output": config["explanation"]["output"],
            "coefficient": float(calibrator.coef_[0, 0]),
            "intercept": float(calibrator.intercept_[0]),
            "semantics": (
                "g(p)=sigmoid(a*logit(clip(p,1e-6,1-1e-6))+b). "
                "Attributions explain g(base_pipeline(x)); coefficients are "
                "calibration parameters, not feature effects."
            ),
        },
        "holdout_access": {
            "status": "one guarded post-selection subgroup audit",
            "purpose": config["audit"]["holdout"],
            "claim_sha256": file_hash(OUTPUT / "holdout.claim"),
            "encounters": len(holdout),
            "patients": int(holdout["patient_nbr"].nunique()),
        },
        "limitations": (
            "Educational historical research only. No medical advice, causality, "
            "discrimination finding or fairness certification. Training-only "
            "XAI/stability and a single holdout subgroup audit; no model or "
            "threshold tuning. Aggregate release is not formal differential privacy."
        ),
    }
    validate_publication(result, config)
    write_once(OUTPUT / "results.json", result)
    # Hash the persisted bytes: Windows text output may translate LF to CRLF.
    result_hash = file_hash(OUTPUT / "results.json")
    write_once(
        OUTPUT / "manifest.json",
        {
            "schema_version": "healthcare-audit-manifest-v1",
            "created_at": datetime.now(UTC).isoformat(),
            "protocol_file_sha256": file_hash(OUTPUT / "protocol.json"),
            "protocol_sha256": frozen["protocol_sha256"],
            "config_sha256": frozen["config_sha256"],
            "results_sha256": result_hash,
            "bindings": frozen["bindings"],
            "identity": identity,
            "versions": versions(),
            "seeds": {
                name: config[name] for name in ("explanation", "stability", "fairness")
            },
            "holdout_access": result["holdout_access"],
            "privacy": config["privacy"],
            "limitations": result["limitations"],
        },
    )
    return inspect()


def inspect() -> dict[str, Any]:
    frozen = verified_protocol()
    manifest = read_record(OUTPUT / "manifest.json")
    result = read_record(OUTPUT / "results.json")
    if set(path.name for path in OUTPUT.iterdir()) != {
        "protocol.json",
        "results.json",
        "manifest.json",
        "holdout.claim",
    }:
        raise HealthcareDataError("unexpected audit output")
    if (
        manifest["results_sha256"] != file_hash(OUTPUT / "results.json")
        or manifest["protocol_file_sha256"] != file_hash(OUTPUT / "protocol.json")
        or manifest["bindings"] != frozen["bindings"]
        or manifest["identity"] != frozen["identity"]
        or result["identity"] != frozen["identity"]
        or manifest["protocol_sha256"] != frozen["protocol_sha256"]
        or manifest["config_sha256"] != frozen["config_sha256"]
        or manifest["versions"] != frozen["versions"]
        or manifest["holdout_access"] != result["holdout_access"]
        or result["holdout_access"]["claim_sha256"]
        != file_hash(OUTPUT / "holdout.claim")
    ):
        raise HealthcareDataError("audit manifest binding mismatch")
    validate_publication(result, frozen["config"])
    return {
        "status": "verified",
        "protocol_sha256": frozen["protocol_sha256"],
        "results_sha256": manifest["results_sha256"],
        "model_sha256": frozen["identity"]["model_sha256"],
        "holdout_access": result["holdout_access"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Frozen healthcare audit research")
    parser.add_argument("command", choices=("freeze", "run", "inspect"))
    command = parser.parse_args().command
    result = (
        freeze() if command == "freeze" else run() if command == "run" else inspect()
    )
    print(
        json.dumps(
            {"status": "protocol frozen; no audit outcomes calculated"}
            if command == "freeze"
            else result,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
