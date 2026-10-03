from __future__ import annotations

import pandas as pd
import pytest
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from aletheia.ml.evaluate import evaluate_models
from aletheia.ml.preprocess import (
    build_preprocessor,
    expected_transformed_schema,
    validate_fitted_schema,
)


def test_exact_feature_allocation_and_explicit_domains(baseline_config) -> None:
    transformer = build_preprocessor(baseline_config)
    quantitative = transformer.transformers[0]
    categorical = transformer.transformers[1]
    encoder = categorical[1]

    assert quantitative[2] == ["laufzeit", "hoehe"]
    assert categorical[2] == list(baseline_config.categorical_features)
    assert encoder.handle_unknown == "error"
    assert encoder.categories == [
        list(baseline_config.category_domains[name])
        for name in baseline_config.categorical_features
    ]
    forbidden = {
        "famges",
        "alter",
        "gastarb",
        "telef",
        "bishkred",
        "kredit",
        "adverse_event",
        "row_key",
    }
    assert forbidden.isdisjoint(quantitative[2] + categorical[2])


def test_schema_is_stable_and_contains_unobserved_purpose_seven(
    baseline_config, baseline_training_data
) -> None:
    features, _target, _keys = baseline_training_data
    without_seven = features.loc[features["verw"] != 7]
    transformer = build_preprocessor(baseline_config).fit(without_seven)

    schema = validate_fitted_schema(transformer, baseline_config)

    assert len(schema.names) == 59
    assert "categorical__verw_7" in schema.names
    assert schema.original_feature_by_name["categorical__verw_7"] == "verw"
    assert tuple(transformer.get_feature_names_out()) == schema.names


def test_undocumented_category_is_refused(
    baseline_config, baseline_training_data
) -> None:
    features, _target, _keys = baseline_training_data
    transformer = build_preprocessor(baseline_config).fit(features)
    invalid = features.iloc[[0]].copy()
    invalid.loc[:, "verw"] = 99

    with pytest.raises(ValueError, match="Found unknown categories"):
        transformer.transform(invalid)


def test_every_fold_fits_scaler_and_encoder_on_fold_training_rows_only(
    baseline_config, baseline_training_data, monkeypatch
) -> None:
    features, target, keys = baseline_training_data
    features, target, keys = features.iloc[:100], target.iloc[:100], keys.iloc[:100]
    target = pd.Series(([1] * 30) + ([0] * 70), name="adverse_event")
    scaler_sizes: list[int] = []
    encoder_sizes: list[int] = []
    original_scaler_fit = StandardScaler.fit
    original_encoder_fit = OneHotEncoder.fit

    def scaler_fit(self, data, y=None, sample_weight=None):
        scaler_sizes.append(len(data))
        return original_scaler_fit(self, data, y, sample_weight=sample_weight)

    def encoder_fit(self, data, y=None):
        encoder_sizes.append(len(data))
        return original_encoder_fit(self, data, y)

    monkeypatch.setattr(StandardScaler, "fit", scaler_fit)
    monkeypatch.setattr(OneHotEncoder, "fit", encoder_fit)

    evaluate_models(features, target, keys, baseline_config)

    assert scaler_sizes == [80] * 10
    assert encoder_sizes == [80] * 10


def test_mapping_covers_every_transformed_column_once(baseline_config) -> None:
    schema = expected_transformed_schema(baseline_config)

    assert set(schema.original_feature_by_name) == set(schema.names)
    assert set(schema.original_feature_by_name.values()) == set(
        baseline_config.quantitative_features + baseline_config.categorical_features
    )
