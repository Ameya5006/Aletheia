"""Small immutable contracts and data-foundation errors."""

from __future__ import annotations

from dataclasses import dataclass


class DataFoundationError(ValueError):
    """Base error for safe, expected data-foundation refusals."""


class ConfigurationError(DataFoundationError):
    """A versioned configuration is missing or inconsistent."""


class IntegrityError(DataFoundationError):
    """Downloaded or local bytes do not match the approved identity."""


class AcquisitionError(DataFoundationError):
    """The approved dataset could not be safely acquired."""


class SchemaError(DataFoundationError):
    """Raw data violates its fixed schema or semantic domains."""


class FeatureRoleError(DataFoundationError):
    """Feature roles overlap, omit fields, or admit an unknown field."""


class SplitContractError(DataFoundationError):
    """Split membership is incomplete, changed, or incompatible."""


class ExperimentError(DataFoundationError):
    """An experiment configuration, calculation, or manifest is invalid."""


class ArtifactError(ExperimentError):
    """A run artifact could not be published without mutation or ambiguity."""


@dataclass(frozen=True)
class DatasetContract:
    """Identity and raw semantic rules for one approved dataset version."""

    contract_version: str
    identifier: str
    name: str
    record_url: str
    doi: str
    licence: str
    archive_url: str
    archive_size: int
    archive_sha256: str
    archive_member: str
    raw_filename: str
    raw_size: int
    raw_sha256: str
    row_count: int
    columns: tuple[str, ...]
    categorical_domains: dict[str, frozenset[int]]
    raw_target: str
    derived_target: str
    target_mapping_identifier: str
    allowed_target_values: frozenset[int]
    adverse_raw_value: int
    expected_target_counts: dict[int, int]
    observed_ranges: dict[str, tuple[int, int]]


@dataclass(frozen=True)
class FeaturePolicy:
    """Versioned, default-deny role and semantic-type policy."""

    version: str
    prediction: tuple[str, ...]
    audit_only: tuple[str, ...]
    excluded: tuple[str, ...]
    raw_target: tuple[str, ...]
    derived_target: tuple[str, ...]
    metadata: tuple[str, ...]
    quantitative: tuple[str, ...]
    ordinal_or_discretized: tuple[str, ...]
    nominal_categorical_integer: tuple[str, ...]
    decisions: dict[str, str]

    @property
    def raw_role_fields(self) -> tuple[str, ...]:
        return self.prediction + self.audit_only + self.excluded + self.raw_target

    @property
    def all_role_fields(self) -> tuple[str, ...]:
        return self.raw_role_fields + self.derived_target + self.metadata

    @property
    def raw_semantic_fields(self) -> tuple[str, ...]:
        return (
            self.quantitative
            + self.ordinal_or_discretized
            + self.nominal_categorical_integer
            + self.raw_target
        )


@dataclass(frozen=True)
class BaselineExperimentConfig:
    """Frozen Phase 4 protocol loaded from the versioned TOML file."""

    schema_version: str
    identifier: str
    dataset_identifier: str
    dataset_sha256: str
    feature_policy_version: str
    split_contract_path: str
    split_membership_checksum: str
    target_mapping_identifier: str
    positive_class: int
    quantitative_features: tuple[str, ...]
    categorical_features: tuple[str, ...]
    category_domains: dict[str, tuple[int, ...]]
    categorical_unknown_policy: str
    scale_quantitative: bool
    dummy_strategy: str
    logistic_penalty: str
    logistic_c: float
    logistic_solver: str
    logistic_class_weight: str | None
    logistic_max_iter: int
    cv_method: str
    cv_folds: int
    cv_shuffle: bool
    cv_seed: int
    metrics: tuple[str, ...]
    primary_metric: str
    threshold: float
