from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from aletheia.ml.evaluate import (
    classification_metrics,
    evaluate_models,
    make_folds,
    probability_for_class_one,
)


def test_known_metric_fixture_uses_adverse_class_one() -> None:
    truth = pd.Series([0, 0, 1, 1])
    probability = np.array([0.1, 0.6, 0.4, 0.9])

    metrics = classification_metrics(truth, probability, threshold=0.5)

    assert metrics["roc_auc"] == pytest.approx(0.75)
    assert metrics["average_precision"] == pytest.approx(5 / 6)
    assert metrics["balanced_accuracy"] == pytest.approx(0.5)
    assert metrics["adverse_recall"] == pytest.approx(0.5)
    assert metrics["specificity"] == pytest.approx(0.5)
    assert metrics["precision"] == pytest.approx(0.5)
    assert metrics["f1"] == pytest.approx(0.5)
    assert metrics["brier_score"] == pytest.approx(0.185)


def test_probability_column_is_selected_by_class_label_one() -> None:
    model = SimpleNamespace(classes_=np.array([1, 0]))
    pipeline = SimpleNamespace(
        named_steps={"model": model},
        predict_proba=lambda _features: np.array([[0.8, 0.2], [0.3, 0.7]]),
    )

    result = probability_for_class_one(pipeline, pd.DataFrame({"x": [1, 2]}))

    assert result.tolist() == [0.8, 0.3]


def test_five_folds_cover_training_once_and_are_disjoint(
    baseline_config, baseline_training_data
) -> None:
    _features, target, keys = baseline_training_data
    folds = make_folds(keys, target, baseline_config)

    assert len(folds) == 5
    assert sorted(index for fold in folds for index in fold.validation_indices) == list(
        range(800)
    )
    assert all(
        set(fold.train_indices).isdisjoint(fold.validation_indices) for fold in folds
    )
    assert all(len(fold.validation_indices) == 160 for fold in folds)


def test_models_share_folds_and_repeated_results_are_deterministic(
    baseline_config, baseline_training_data
) -> None:
    features, target, keys = baseline_training_data
    first = evaluate_models(features, target, keys, baseline_config)
    second = evaluate_models(features, target, keys, baseline_config)

    assert first == second
    assert (
        first["models"]["dummy"]["fold_membership_checksums"]
        == first["models"]["logistic_regression"]["fold_membership_checksums"]
    )
    assert first["models"]["dummy"]["aggregate_metrics"]["roc_auc"][
        "mean"
    ] == pytest.approx(0.5)
