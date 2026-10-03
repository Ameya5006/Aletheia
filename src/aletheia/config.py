"""Load and validate Aletheia's versioned TOML contracts."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

from aletheia.contracts import (
    BaselineExperimentConfig,
    ConfigurationError,
    DatasetContract,
    FeaturePolicy,
)

DEFAULT_DATASET_CONFIG = Path("configs/dataset.toml")
DEFAULT_FEATURE_CONFIG = Path("configs/features.toml")
DEFAULT_BASELINE_CONFIG = Path("configs/experiments/baseline_v1.toml")
_SHA256 = re.compile(r"[0-9a-f]{64}")


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as stream:
            value = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigurationError(f"cannot load configuration {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ConfigurationError(f"configuration {path} must contain a TOML table")
    return value


def _table(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name)
    if not isinstance(value, dict):
        raise ConfigurationError(f"missing or invalid [{name}] table")
    return value


def _strings(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigurationError(f"{field} must be a list of strings")
    result = tuple(value)
    if len(result) != len(set(result)):
        raise ConfigurationError(f"{field} contains duplicate names")
    return result


def _positive_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ConfigurationError(f"{field} must be a positive integer")
    return value


def _number(value: Any, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ConfigurationError(f"{field} must be numeric")
    return float(value)


def _digest(value: Any, field: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ConfigurationError(f"{field} must be a lowercase SHA-256 digest")
    return value


def load_dataset_contract(path: str | Path = DEFAULT_DATASET_CONFIG) -> DatasetContract:
    """Load the fixed dataset identity and schema without applying data repairs."""
    data = _read_toml(Path(path))
    contract = _table(data, "contract")
    dataset = _table(data, "dataset")
    archive = _table(data, "archive")
    raw = _table(data, "raw")
    target = _table(data, "target")
    domains_data = _table(data, "categorical_domains")
    ranges_data = _table(data, "observed_ranges")

    columns = _strings(raw.get("columns"), "raw.columns")
    domains: dict[str, frozenset[int]] = {}
    for name, values in domains_data.items():
        if name not in columns:
            raise ConfigurationError(f"categorical domain has unknown column {name!r}")
        if (
            not isinstance(values, list)
            or not values
            or not all(
                isinstance(value, int) and not isinstance(value, bool)
                for value in values
            )
        ):
            raise ConfigurationError(f"categorical domain for {name!r} is invalid")
        if len(values) != len(set(values)):
            raise ConfigurationError(f"categorical domain for {name!r} has duplicates")
        domains[name] = frozenset(values)

    expected_counts_data = target.get("expected_raw_counts")
    if not isinstance(expected_counts_data, dict):
        raise ConfigurationError("target.expected_raw_counts must be a table")
    try:
        expected_counts = {
            int(key): _positive_int(value, f"target.expected_raw_counts.{key}")
            for key, value in expected_counts_data.items()
        }
    except (TypeError, ValueError) as exc:
        raise ConfigurationError("target count keys must be integer strings") from exc

    allowed_values_data = target.get("allowed_raw_values")
    if not isinstance(allowed_values_data, list) or not all(
        isinstance(value, int) and not isinstance(value, bool)
        for value in allowed_values_data
    ):
        raise ConfigurationError("target.allowed_raw_values must be integer values")
    allowed_values = frozenset(allowed_values_data)

    observed_ranges: dict[str, tuple[int, int]] = {}
    for name, bounds in ranges_data.items():
        if name == "scope":
            continue
        if name not in columns or not isinstance(bounds, dict):
            raise ConfigurationError(f"observed range for {name!r} is invalid")
        minimum, maximum = bounds.get("minimum"), bounds.get("maximum")
        if not isinstance(minimum, int) or not isinstance(maximum, int):
            raise ConfigurationError(f"observed range for {name!r} must be integer")
        if minimum > maximum:
            raise ConfigurationError(f"observed range for {name!r} is reversed")
        observed_ranges[name] = (minimum, maximum)

    result = DatasetContract(
        contract_version=str(contract.get("version", "")),
        identifier=str(dataset.get("identifier", "")),
        name=str(dataset.get("name", "")),
        record_url=str(dataset.get("record_url", "")),
        doi=str(dataset.get("doi", "")),
        licence=str(dataset.get("licence", "")),
        archive_url=str(archive.get("url", "")),
        archive_size=_positive_int(archive.get("size_bytes"), "archive.size_bytes"),
        archive_sha256=_digest(archive.get("sha256"), "archive.sha256"),
        archive_member=str(archive.get("required_member", "")),
        raw_filename=str(raw.get("filename", "")),
        raw_size=_positive_int(raw.get("size_bytes"), "raw.size_bytes"),
        raw_sha256=_digest(raw.get("sha256"), "raw.sha256"),
        row_count=_positive_int(raw.get("row_count"), "raw.row_count"),
        columns=columns,
        categorical_domains=domains,
        raw_target=str(target.get("raw_column", "")),
        derived_target=str(target.get("derived_column", "")),
        target_mapping_identifier=str(target.get("mapping_identifier", "")),
        allowed_target_values=allowed_values,
        adverse_raw_value=target.get("adverse_raw_value"),
        expected_target_counts=expected_counts,
        observed_ranges=observed_ranges,
    )
    _validate_dataset_contract(result)
    return result


def _validate_dataset_contract(contract: DatasetContract) -> None:
    required_text = {
        "contract.version": contract.contract_version,
        "dataset.identifier": contract.identifier,
        "dataset.name": contract.name,
        "archive.url": contract.archive_url,
        "archive.required_member": contract.archive_member,
        "raw.filename": contract.raw_filename,
        "target.raw_column": contract.raw_target,
        "target.derived_column": contract.derived_target,
        "target.mapping_identifier": contract.target_mapping_identifier,
    }
    for field, value in required_text.items():
        if not value:
            raise ConfigurationError(f"{field} must not be empty")
    if contract.raw_target not in contract.columns:
        raise ConfigurationError("raw target is not in raw.columns")
    if contract.derived_target in contract.columns:
        raise ConfigurationError("derived target must not replace a raw column")
    if contract.adverse_raw_value not in contract.allowed_target_values:
        raise ConfigurationError("adverse raw value is outside the target domain")
    if set(contract.expected_target_counts) != set(contract.allowed_target_values):
        raise ConfigurationError(
            "expected target counts do not cover the target domain"
        )
    if sum(contract.expected_target_counts.values()) != contract.row_count:
        raise ConfigurationError("expected target counts do not total raw.row_count")
    target_domain = contract.categorical_domains.get(contract.raw_target)
    if target_domain != contract.allowed_target_values:
        raise ConfigurationError("target domain conflicts with categorical domain")


def load_feature_policy(
    path: str | Path = DEFAULT_FEATURE_CONFIG,
    dataset: DatasetContract | None = None,
) -> FeaturePolicy:
    """Load and validate the fail-closed feature-role and semantic policy."""
    data = _read_toml(Path(path))
    policy = _table(data, "policy")
    roles = _table(data, "roles")
    semantics = _table(data, "semantic_types")
    decisions_data = _table(data, "decisions")
    if not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in decisions_data.items()
    ):
        raise ConfigurationError("feature decisions must map strings to strings")

    result = FeaturePolicy(
        version=str(policy.get("version", "")),
        prediction=_strings(roles.get("prediction"), "roles.prediction"),
        audit_only=_strings(roles.get("audit_only"), "roles.audit_only"),
        excluded=_strings(roles.get("excluded"), "roles.excluded"),
        raw_target=_strings(roles.get("raw_target"), "roles.raw_target"),
        derived_target=_strings(roles.get("derived_target"), "roles.derived_target"),
        metadata=_strings(roles.get("metadata"), "roles.metadata"),
        quantitative=_strings(
            semantics.get("quantitative"), "semantic_types.quantitative"
        ),
        ordinal_or_discretized=_strings(
            semantics.get("ordinal_or_discretized"),
            "semantic_types.ordinal_or_discretized",
        ),
        nominal_categorical_integer=_strings(
            semantics.get("nominal_categorical_integer"),
            "semantic_types.nominal_categorical_integer",
        ),
        decisions=dict(decisions_data),
    )
    validate_feature_policy(result, dataset)
    return result


def validate_feature_policy(
    policy: FeaturePolicy, dataset: DatasetContract | None = None
) -> None:
    """Reject overlaps and any raw field without one role and semantic type."""
    if not policy.version:
        raise ConfigurationError("policy.version must not be empty")
    role_groups = {
        "prediction": policy.prediction,
        "audit_only": policy.audit_only,
        "excluded": policy.excluded,
        "raw_target": policy.raw_target,
        "derived_target": policy.derived_target,
        "metadata": policy.metadata,
    }
    _require_disjoint(role_groups, "feature role")
    semantic_groups = {
        "quantitative": policy.quantitative,
        "ordinal_or_discretized": policy.ordinal_or_discretized,
        "nominal_categorical_integer": policy.nominal_categorical_integer,
        "raw_target": policy.raw_target,
        "derived_target": policy.derived_target,
        "metadata": policy.metadata,
    }
    _require_disjoint(semantic_groups, "semantic type")
    if set(policy.all_role_fields) != set(
        policy.raw_semantic_fields + policy.derived_target + policy.metadata
    ):
        raise ConfigurationError("role and semantic-type coverage do not match")
    if dataset is not None:
        if set(policy.raw_role_fields) != set(dataset.columns):
            raise ConfigurationError("feature roles do not exhaust the raw schema")
        if policy.raw_target != (dataset.raw_target,):
            raise ConfigurationError("feature policy raw target conflicts with dataset")
        if policy.derived_target != (dataset.derived_target,):
            raise ConfigurationError(
                "feature policy derived target conflicts with dataset"
            )
        if policy.metadata != ("row_key",):
            raise ConfigurationError("feature policy must define row_key metadata")


def _require_disjoint(groups: dict[str, tuple[str, ...]], label: str) -> None:
    seen: dict[str, str] = {}
    for group, fields in groups.items():
        for field in fields:
            if field in seen:
                raise ConfigurationError(
                    f"{label} field {field!r} overlaps {seen[field]!r} and {group!r}"
                )
            seen[field] = group


def load_baseline_experiment_config(
    path: str | Path = DEFAULT_BASELINE_CONFIG,
    *,
    dataset: DatasetContract | None = None,
    policy: FeaturePolicy | None = None,
) -> BaselineExperimentConfig:
    """Load and strictly validate the one approved Phase 4 protocol."""
    data = _read_toml(Path(path))
    experiment = _table(data, "experiment")
    dataset_table = _table(data, "dataset")
    target = _table(data, "target")
    preprocessing = _table(data, "preprocessing")
    categories = preprocessing.get("categories")
    if not isinstance(categories, dict):
        raise ConfigurationError("missing or invalid [preprocessing.categories] table")
    models = _table(data, "models")
    dummy = models.get("dummy")
    logistic = models.get("logistic_regression")
    if not isinstance(dummy, dict):
        raise ConfigurationError("missing or invalid [models.dummy] table")
    if not isinstance(logistic, dict):
        raise ConfigurationError(
            "missing or invalid [models.logistic_regression] table"
        )
    cv = _table(data, "cross_validation")
    evaluation = _table(data, "evaluation")

    class_weight = logistic.get("class_weight")
    if class_weight == "none":
        class_weight = None
    elif class_weight is not None:
        raise ConfigurationError(
            "models.logistic_regression.class_weight must be 'none'"
        )

    category_domains: dict[str, tuple[int, ...]] = {}
    for name, values in categories.items():
        if (
            not isinstance(values, list)
            or not values
            or not all(
                isinstance(value, int) and not isinstance(value, bool)
                for value in values
            )
        ):
            raise ConfigurationError(f"category domain for {name!r} is invalid")
        category_domains[name] = tuple(values)

    result = BaselineExperimentConfig(
        schema_version=str(experiment.get("schema_version", "")),
        identifier=str(experiment.get("identifier", "")),
        dataset_identifier=str(dataset_table.get("identifier", "")),
        dataset_sha256=_digest(dataset_table.get("sha256"), "dataset.sha256"),
        feature_policy_version=str(dataset_table.get("feature_policy_version", "")),
        split_contract_path=str(dataset_table.get("split_contract", "")),
        split_membership_checksum=_digest(
            dataset_table.get("split_membership_checksum"),
            "dataset.split_membership_checksum",
        ),
        target_mapping_identifier=str(target.get("mapping_identifier", "")),
        positive_class=target.get("positive_class"),
        quantitative_features=_strings(
            preprocessing.get("quantitative_features"),
            "preprocessing.quantitative_features",
        ),
        categorical_features=_strings(
            preprocessing.get("categorical_features"),
            "preprocessing.categorical_features",
        ),
        category_domains=category_domains,
        categorical_unknown_policy=str(preprocessing.get("unknown_category", "")),
        scale_quantitative=preprocessing.get("scale_quantitative"),
        dummy_strategy=str(dummy.get("strategy", "")),
        logistic_penalty=str(logistic.get("penalty", "")),
        logistic_c=_number(logistic.get("c"), "models.logistic_regression.c"),
        logistic_solver=str(logistic.get("solver", "")),
        logistic_class_weight=class_weight,
        logistic_max_iter=_positive_int(
            logistic.get("max_iter"), "models.logistic_regression.max_iter"
        ),
        cv_method=str(cv.get("method", "")),
        cv_folds=_positive_int(cv.get("folds"), "cross_validation.folds"),
        cv_shuffle=cv.get("shuffle"),
        cv_seed=cv.get("seed"),
        metrics=_strings(evaluation.get("metrics"), "evaluation.metrics"),
        primary_metric=str(evaluation.get("primary_metric", "")),
        threshold=_number(evaluation.get("threshold"), "evaluation.threshold"),
    )
    _validate_baseline_config(result, dataset, policy)
    return result


def _validate_baseline_config(
    config: BaselineExperimentConfig,
    dataset: DatasetContract | None,
    policy: FeaturePolicy | None,
) -> None:
    expected_metrics = (
        "roc_auc",
        "average_precision",
        "balanced_accuracy",
        "adverse_recall",
        "specificity",
        "precision",
        "f1",
        "log_loss",
        "brier_score",
    )
    fixed_values = {
        "experiment.schema_version": (config.schema_version, "1.0"),
        "experiment.identifier": (config.identifier, "baseline-v1"),
        "target.positive_class": (config.positive_class, 1),
        "preprocessing.unknown_category": (
            config.categorical_unknown_policy,
            "error",
        ),
        "preprocessing.scale_quantitative": (config.scale_quantitative, True),
        "models.dummy.strategy": (config.dummy_strategy, "prior"),
        "models.logistic_regression.penalty": (config.logistic_penalty, "l2"),
        "models.logistic_regression.c": (config.logistic_c, 1.0),
        "models.logistic_regression.solver": (config.logistic_solver, "lbfgs"),
        "models.logistic_regression.class_weight": (
            config.logistic_class_weight,
            None,
        ),
        "models.logistic_regression.max_iter": (config.logistic_max_iter, 1000),
        "cross_validation.method": (config.cv_method, "StratifiedKFold"),
        "cross_validation.folds": (config.cv_folds, 5),
        "cross_validation.shuffle": (config.cv_shuffle, True),
        "cross_validation.seed": (config.cv_seed, 42),
        "evaluation.primary_metric": (config.primary_metric, "roc_auc"),
        "evaluation.metrics": (config.metrics, expected_metrics),
        "evaluation.threshold": (config.threshold, 0.5),
    }
    for field, (actual, expected) in fixed_values.items():
        if actual != expected:
            raise ConfigurationError(f"{field} must be {expected!r}, got {actual!r}")
    if dataset is not None:
        dataset_checks = {
            "dataset.identifier": (config.dataset_identifier, dataset.identifier),
            "dataset.sha256": (config.dataset_sha256, dataset.raw_sha256),
            "target.mapping_identifier": (
                config.target_mapping_identifier,
                dataset.target_mapping_identifier,
            ),
        }
        for field, (actual, expected) in dataset_checks.items():
            if actual != expected:
                raise ConfigurationError(f"{field} conflicts with dataset contract")
        expected_domains = {
            name: tuple(sorted(dataset.categorical_domains[name]))
            for name in config.categorical_features
        }
        if config.category_domains != expected_domains:
            raise ConfigurationError(
                "experiment category domains conflict with dataset contract"
            )
    if policy is not None:
        if config.feature_policy_version != policy.version:
            raise ConfigurationError(
                "experiment feature policy version conflicts with policy"
            )
        if config.quantitative_features != ("laufzeit", "hoehe"):
            raise ConfigurationError(
                "baseline quantitative features must be laufzeit and hoehe"
            )
        expected_categorical = tuple(
            field
            for field in policy.prediction
            if field not in config.quantitative_features
        )
        if config.categorical_features != expected_categorical:
            raise ConfigurationError(
                "baseline categorical features conflict with prediction policy"
            )
        if set(config.quantitative_features + config.categorical_features) != set(
            policy.prediction
        ):
            raise ConfigurationError(
                "baseline preprocessing does not cover prediction features"
            )
