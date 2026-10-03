"""Build the fixed Phase 4 preprocessor and its feature-lineage contract."""

from __future__ import annotations

from dataclasses import dataclass

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from aletheia.contracts import BaselineExperimentConfig, ExperimentError


@dataclass(frozen=True)
class TransformedSchema:
    """Stable transformed names and their originating raw prediction fields."""

    names: tuple[str, ...]
    original_feature_by_name: dict[str, str]


def build_preprocessor(config: BaselineExperimentConfig) -> ColumnTransformer:
    """Create an unfitted transformer with explicit, contract-derived categories."""
    categories = [
        list(config.category_domains[name]) for name in config.categorical_features
    ]
    return ColumnTransformer(
        transformers=[
            (
                "quantitative",
                StandardScaler(),
                list(config.quantitative_features),
            ),
            (
                "categorical",
                OneHotEncoder(
                    categories=categories,
                    handle_unknown=config.categorical_unknown_policy,
                    sparse_output=False,
                ),
                list(config.categorical_features),
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )


def expected_transformed_schema(
    config: BaselineExperimentConfig,
) -> TransformedSchema:
    """Derive deterministic output lineage without inspecting any data partition."""
    names: list[str] = []
    mapping: dict[str, str] = {}
    for feature in config.quantitative_features:
        transformed = f"quantitative__{feature}"
        names.append(transformed)
        mapping[transformed] = feature
    for feature in config.categorical_features:
        for category in config.category_domains[feature]:
            transformed = f"categorical__{feature}_{category}"
            names.append(transformed)
            mapping[transformed] = feature
    return TransformedSchema(tuple(names), mapping)


def validate_fitted_schema(
    transformer: ColumnTransformer, config: BaselineExperimentConfig
) -> TransformedSchema:
    """Ensure a fitted transformer exposes exactly the frozen output schema."""
    expected = expected_transformed_schema(config)
    actual = tuple(str(name) for name in transformer.get_feature_names_out())
    if actual != expected.names:
        raise ExperimentError(
            "fitted transformed columns differ from the approved baseline schema"
        )
    return expected
