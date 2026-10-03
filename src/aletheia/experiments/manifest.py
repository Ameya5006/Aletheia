"""Build and validate the Phase 4 training-only run manifest."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy
import pandas
import sklearn

from aletheia.contracts import (
    BaselineExperimentConfig,
    DatasetContract,
    ExperimentError,
    FeaturePolicy,
)
from aletheia.ml.models import model_configuration
from aletheia.ml.preprocess import expected_transformed_schema

MANIFEST_SCHEMA_VERSION = "1.0"


def sha256_file(path: str | Path) -> str:
    """Hash a small experiment configuration file."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _git_output(arguments: list[str]) -> bytes:
    result = subprocess.run(["git", *arguments], capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ExperimentError(f"Git metadata command failed: {detail}")
    return result.stdout


def source_control_identity() -> dict[str, Any]:
    """Record HEAD and a checksum covering tracked diffs plus untracked files."""
    base_commit = _git_output(["rev-parse", "HEAD"]).decode().strip()
    status = _git_output(["status", "--porcelain=v1", "-z", "--untracked-files=all"])
    diff = _git_output(["diff", "--binary", "HEAD", "--"])
    digest = hashlib.sha256()
    digest.update(b"tracked-diff\0")
    digest.update(diff)
    entries = [entry for entry in status.split(b"\0") if entry]
    for entry in sorted(entries):
        digest.update(b"status\0")
        digest.update(entry)
        path_text = entry[3:].decode("utf-8", errors="strict")
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        path = Path(path_text)
        if entry.startswith(b"??") and path.is_file():
            digest.update(b"untracked-content\0")
            digest.update(path.read_bytes())
    return {
        "base_git_commit": base_commit,
        "working_tree_dirty": bool(entries),
        "diff_checksum": digest.hexdigest(),
    }


def build_manifest(
    *,
    run_id: str,
    config: BaselineExperimentConfig,
    config_path: str | Path,
    dataset: DatasetContract,
    policy: FeaturePolicy,
    split_membership_checksum: str,
    training_membership_checksum: str,
    results: dict[str, Any],
    source_control: dict[str, Any],
    created_at: str | None = None,
) -> dict[str, Any]:
    """Create the complete immutable evidence record without a fitted model."""
    schema = expected_transformed_schema(config)
    manifest = {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "run_id": run_id,
        "experiment_identifier": config.identifier,
        "dataset": {"identifier": dataset.identifier, "sha256": dataset.raw_sha256},
        "feature_policy_version": policy.version,
        "split_membership_checksum": split_membership_checksum,
        "training_membership_checksum": training_membership_checksum,
        "experiment_configuration": {
            "path": Path(config_path).as_posix(),
            "sha256": sha256_file(config_path),
        },
        "target": {
            "mapping_identifier": dataset.target_mapping_identifier,
            "positive_class": config.positive_class,
        },
        "preprocessing_configuration": {
            "implementation": "ColumnTransformer inside Pipeline",
            "quantitative_features": list(config.quantitative_features),
            "quantitative_transform": "StandardScaler",
            "categorical_features": list(config.categorical_features),
            "categorical_transform": "OneHotEncoder",
            "categories": {
                name: list(values) for name, values in config.category_domains.items()
            },
            "unknown_category": config.categorical_unknown_policy,
            "imputation": None,
            "resampling": None,
            "fit_scope": "each cross-validation training fold only",
        },
        "model_configuration": model_configuration(config),
        "cross_validation_configuration": {
            "method": config.cv_method,
            "folds": config.cv_folds,
            "shuffle": config.cv_shuffle,
            "random_state": config.cv_seed,
            "threshold": config.threshold,
            "threshold_purpose": "descriptive confusion metrics only",
        },
        "metrics": {
            "primary": config.primary_metric,
            "supporting": [
                metric for metric in config.metrics if metric != config.primary_metric
            ],
        },
        "fold_membership_checksums": results["fold_membership_checksums"],
        "results": results,
        "transformed_features": {
            "count": len(schema.names),
            "names": list(schema.names),
            "original_feature_mapping": schema.original_feature_by_name,
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": numpy.__version__,
            "pandas": pandas.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "source_control": source_control,
        "created_at": created_at or datetime.now(UTC).isoformat(),
        "limitations": [
            "Only the locked 800-row training partition was evaluated by "
            "cross-validation.",
            "No held-out prediction or metric was calculated.",
            "Threshold 0.5 is descriptive and is not an operational lending "
            "recommendation.",
            "ROC-AUC does not establish calibration.",
            "The dataset oversamples adverse cases, limiting precision, "
            "average-precision, and probability interpretation.",
            "No final fitted model is stored by this Phase 4 run.",
        ],
        "held_out_evaluation_performed": False,
        "fitted_model_artifact": None,
    }
    validate_manifest(manifest)
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> None:
    """Fail closed on incomplete, inconsistent, or held-out Phase 4 evidence."""
    required = {
        "manifest_schema_version",
        "run_id",
        "experiment_identifier",
        "dataset",
        "feature_policy_version",
        "split_membership_checksum",
        "training_membership_checksum",
        "experiment_configuration",
        "target",
        "preprocessing_configuration",
        "model_configuration",
        "cross_validation_configuration",
        "metrics",
        "fold_membership_checksums",
        "results",
        "transformed_features",
        "environment",
        "source_control",
        "created_at",
        "limitations",
        "held_out_evaluation_performed",
        "fitted_model_artifact",
    }
    missing = sorted(required - set(manifest))
    if missing:
        raise ExperimentError(f"manifest is missing required field {missing[0]!r}")
    if manifest["manifest_schema_version"] != MANIFEST_SCHEMA_VERSION:
        raise ExperimentError("unsupported manifest schema version")
    if manifest["held_out_evaluation_performed"] is not False:
        raise ExperimentError("Phase 4 manifest refuses held-out evaluation")
    if manifest["fitted_model_artifact"] is not None:
        raise ExperimentError("Phase 4 manifest refuses a fitted model artifact")
    results = manifest["results"]
    expected_scope = "locked_training_partition_cross_validation"
    if (
        not isinstance(results, dict)
        or results.get("evaluation_scope") != expected_scope
    ):
        raise ExperimentError("manifest results must be training-only cross-validation")
    if results.get("evaluated_row_count") != 800:
        raise ExperimentError("authoritative Phase 4 manifest must evaluate 800 rows")
    if set(results.get("models", {})) != {"dummy", "logistic_regression"}:
        raise ExperimentError("manifest must contain exactly the two baseline models")
    shared_folds = results.get("fold_membership_checksums")
    if not isinstance(shared_folds, list) or len(shared_folds) != 5:
        raise ExperimentError("manifest must contain five fold checksums")
    for model in results["models"].values():
        if model.get("fold_membership_checksums") != shared_folds:
            raise ExperimentError("baseline models did not use identical folds")
    forbidden_keys = {"held_out_metrics", "test_metrics", "held_out_predictions"}
    if forbidden_keys & _recursive_keys(manifest):
        raise ExperimentError("manifest contains forbidden held-out result fields")


def _recursive_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        result = set(value)
        for item in value.values():
            result.update(_recursive_keys(item))
        return result
    if isinstance(value, list):
        result: set[str] = set()
        for item in value:
            result.update(_recursive_keys(item))
        return result
    return set()


def canonical_result_payload(results: dict[str, Any]) -> bytes:
    """Serialize deterministic calculation output for exact rerun comparison."""
    return json.dumps(
        results, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
