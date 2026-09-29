"""Load and validate Aletheia's versioned TOML contracts."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

from aletheia.contracts import ConfigurationError, DatasetContract, FeaturePolicy

DEFAULT_DATASET_CONFIG = Path("configs/dataset.toml")
DEFAULT_FEATURE_CONFIG = Path("configs/features.toml")
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
