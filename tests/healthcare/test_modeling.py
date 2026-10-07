"""Patient-fold and preprocessing safety tests using synthetic encounters."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from aletheia.domains.healthcare.evaluation import cluster_intervals, metrics
from aletheia.domains.healthcare.experiment import load_config
from aletheia.domains.healthcare.foundation import HealthcareDataError, load_contracts
from aletheia.domains.healthcare.modeling import fit_predict, group_folds, pipeline


def synthetic() -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    contracts = load_contracts()
    rows = []
    for patient in range(60):
        for encounter in range(2):
            row = {}
            for column in contracts.features["semantic_types"]["quantitative"]:
                row[column] = str(1 + patient % 7 + encounter)
            row.update(
                admission_type_id=str(1 + patient % 3),
                admission_source_id=str(1 + patient % 2),
                max_glu_serum="None",
                A1Cresult="Norm",
                diabetesMed="Yes" if patient % 2 else "No",
            )
            rows.append(row)
    x = pd.DataFrame(rows)[contracts.features["roles"]["prediction"]]
    outcomes = [patient % 5 == 0 for patient in range(60) for _ in range(2)]
    y = pd.Series(outcomes).astype(int)
    groups = pd.Series([str(patient) for patient in range(60) for _ in range(2)])
    return x, y, groups


def test_all_outer_and_inner_folds_are_patient_disjoint() -> None:
    _, y, groups = synthetic()
    for outer_train, outer_valid in group_folds(y, groups, 5, 42):
        assert not set(groups.iloc[outer_train]) & set(groups.iloc[outer_valid])
        inner_y = y.iloc[outer_train].reset_index(drop=True)
        inner_groups = groups.iloc[outer_train].reset_index(drop=True)
        for inner_train, inner_valid in group_folds(inner_y, inner_groups, 3, 1042):
            assert not set(inner_groups.iloc[inner_train]) & set(
                inner_groups.iloc[inner_valid]
            )
            assert set(inner_y.iloc[inner_valid]) == {0, 1}


def test_frozen_features_and_fold_local_categories() -> None:
    contracts = load_contracts()
    config = load_config()
    x, y, _ = synthetic()
    x_valid = x.iloc[100:110].copy()
    x_valid["admission_type_id"] = "999"
    fitted, _, probability, evidence = fit_predict(
        contracts,
        config,
        "logistic",
        {"C": 0.1, "class_weight": None},
        x.iloc[:100],
        y.iloc[:100],
        x_valid,
        seed=42,
    )
    assert np.isfinite(probability).all()
    assert not any("999" in name for name in evidence["transformed_features"])
    assert len(fitted.named_steps["preprocess"].get_feature_names_out()) == len(
        evidence["transformed_features"]
    )
    with pytest.raises(HealthcareDataError, match="predictor order"):
        fit_predict(
            contracts,
            config,
            "dummy",
            {"strategy": "prior"},
            x.iloc[:100].assign(patient_nbr="1"),
            y.iloc[:100],
            x_valid,
            seed=42,
        )


def test_dense_budget_refuses_oversized_histogram() -> None:
    contracts = load_contracts()
    config = load_config()
    config["preprocessing"]["max_dense_bytes"] = 1
    x, y, _ = synthetic()
    with pytest.raises(HealthcareDataError, match="dense histogram"):
        fit_predict(
            contracts,
            config,
            "histogram",
            {"max_leaf_nodes": 15, "max_iter": 10, "min_samples_leaf": 2},
            x.iloc[:100],
            y.iloc[:100],
            x.iloc[100:],
            seed=42,
        )


def test_histogram_never_uses_internal_row_validation() -> None:
    fitted = pipeline(
        load_contracts(),
        "histogram",
        {"max_leaf_nodes": 15, "max_iter": 10, "min_samples_leaf": 2},
        seed=42,
        dense=True,
    )
    assert fitted.named_steps["model"].early_stopping is False


def test_patient_cluster_bootstrap_is_seeded() -> None:
    _, y, groups = synthetic()
    probability = np.where(y.to_numpy() == 1, 0.7, 0.15)
    first = cluster_intervals(y, probability, groups, repetitions=30, seed=4242)
    assert first == cluster_intervals(y, probability, groups, repetitions=30, seed=4242)
    assert first["average_precision"][0] <= metrics(y, probability)["average_precision"]
