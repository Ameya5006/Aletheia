"""Behavioral tests for calibrated explanations and bounded responsible audits."""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from aletheia.domains.healthcare import audit
from aletheia.domains.healthcare.counterfactual import (
    assess,
    scenario_result,
    validate_scenario,
)
from aletheia.domains.healthcare.evaluation import sigmoid_fit, sigmoid_predict
from aletheia.domains.healthcare.explain import (
    attributions,
    feature_mapping,
    global_explanation,
    local_explanation,
    probability,
)
from aletheia.domains.healthcare.fairness import (
    audit_subgroups,
    subgroup_intervals,
    subgroup_metrics,
)
from aletheia.domains.healthcare.foundation import HealthcareDataError, load_contracts
from aletheia.domains.healthcare.modeling import pipeline
from aletheia.domains.healthcare.stability import compare, perturb


@pytest.fixture
def fitted():
    contracts = load_contracts()
    rows = []
    for i in range(80):
        row = {
            name: str(1 + i % 9)
            for name in contracts.features["semantic_types"]["quantitative"]
        }
        row.update(
            admission_type_id=str(1 + i % 2),
            admission_source_id="1",
            max_glu_serum="None",
            A1Cresult="Norm",
            diabetesMed="Yes" if i % 2 else "No",
        )
        rows.append(row)
    x = pd.DataFrame(rows)[contracts.features["roles"]["prediction"]]
    y = pd.Series([int(i % 3 == 0) for i in range(80)])
    model = pipeline(contracts, "logistic", {"C": 0.1, "class_weight": None}, 42)
    model.fit(x, y)
    # Deliberately nonidentity sigmoid proves that base values are insufficient.
    calibrator = sigmoid_fit(y, np.linspace(0.05, 0.95, len(y)))
    return contracts, x, {"model": model, "calibrator": calibrator}


def tiny_config():
    config = audit.load_protocol()
    config["explanation"].update(
        sample_size=3, sample_seeds=[1, 2], permutations=2, background_size=4
    )
    config["stability"].update(sample_size=2, repetitions=2)
    config["fairness"].update(bootstrap_repetitions=5)
    return config


def test_fitted_mapping_preserves_source_and_categories(fitted):
    contracts, _, bundle = fitted
    mapping = feature_mapping(contracts, bundle["model"])
    assert [row["transformed"] for row in mapping] == list(
        bundle["model"].named_steps["preprocess"].get_feature_names_out()
    )
    assert set(row["source"] for row in mapping) == set(
        contracts.features["roles"]["prediction"]
    )
    assert sum(row["source"] == "admission_type_id" for row in mapping) == 2
    assert sum(row["source"] == "num_lab_procedures" for row in mapping) == 1


def test_calibrated_not_base_probability(fitted):
    _, x, bundle = fitted
    base = bundle["model"].predict_proba(x)[:, 1]
    assert np.allclose(
        probability(bundle, x), sigmoid_predict(bundle["calibrator"], base)
    )
    assert not np.allclose(probability(bundle, x), base)


def test_additivity_determinism_and_local_structure(fitted):
    contracts, x, bundle = fitted
    config = tiny_config()["explanation"]
    first = local_explanation(
        contracts, bundle, x.iloc[[0]], x.iloc[:4], config, {"model": "synthetic"}
    )
    assert first == local_explanation(
        contracts, bundle, x.iloc[[0]], x.iloc[:4], config, {"model": "synthetic"}
    )
    assert first["probability"] == pytest.approx(
        first["baseline"] + sum(row["contribution"] for row in first["features"])
    )
    assert first["probability"] == pytest.approx(probability(bundle, x.iloc[[0]])[0])
    assert [row["value"] for row in first["features"]] == x.iloc[0].astype(str).tolist()
    assert "not medical advice" in first["limitations"]
    assert first["output"] == "calibrated probability of readmitted_30d=1"


def test_global_repeated_sample_determinism(fitted):
    contracts, x, bundle = fitted
    config = tiny_config()["explanation"]
    first = global_explanation(contracts, bundle, x, x.iloc[:4], config)
    assert first == global_explanation(contracts, bundle, x, x.iloc[:4], config)
    for row in first["features"]:
        assert row["mean_absolute_contribution"] == pytest.approx(
            np.mean(row["repeat_values"])
        )
        assert (
            row["repeat_min"] <= row["mean_absolute_contribution"] <= row["repeat_max"]
        )


@pytest.mark.parametrize(
    "field",
    [
        "race",
        "gender",
        "age",
        "patient_nbr",
        "encounter_id",
        "readmitted",
        "readmitted_30d",
        "discharge_disposition_id",
        "insulin",
    ],
)
def test_forbidden_features_refused(fitted, field):
    contracts, x, bundle = fitted
    with pytest.raises(HealthcareDataError, match="predictor order"):
        attributions(
            contracts,
            bundle,
            x.iloc[[0]].assign(**{field: "1"}),
            x.iloc[:4],
            permutations=2,
            seed=1,
        )


def test_exact_additive_callable_and_null_feature(fitted):
    contracts, x, _ = fitted

    class Additive:
        classes_ = np.array([0, 1])

        def predict_proba(self, frame):
            p = (
                0.01 * frame["num_lab_procedures"].astype(float).to_numpy()
                + 0.02 * frame["num_procedures"].astype(float).to_numpy()
            )
            return np.column_stack([1 - p, p])

    bundle = {"model": Additive(), "calibrator": None}
    background = x.iloc[[0]]
    values, baseline, predicted = attributions(
        contracts, bundle, x.iloc[[1]], background, permutations=4, seed=42
    )
    expected = np.zeros(13)
    expected[list(x).index("num_lab_procedures")] = 0.01
    expected[list(x).index("num_procedures")] = 0.02
    assert np.allclose(values[0], expected)
    assert baseline == pytest.approx(0.03)
    assert predicted[0] == pytest.approx(0.06)


def test_stability_metrics_known_values_and_undefined():
    first = np.array([3.0, 2.0, 1.0])
    assert compare(first, first, 2)["top_k_overlap"] == 1
    assert compare(first, first, 2)["normalized_l1"] == 0
    reverse = compare(first, first[::-1], 2)
    assert reverse["absolute_rank_correlation"] == -1
    assert reverse["top_k_overlap"] == 0.5
    assert reverse["normalized_l1"] == pytest.approx(4 / 6)
    assert compare(np.zeros(3), np.zeros(3), 2)["normalized_l1"] is None


def test_perturb_bounds_seed_and_immutable_fields(fitted):
    contracts, x, _ = fitted
    config = tiny_config()["stability"]
    bounds = {field: [1, 9] for field in config["fields"]}
    first = perturb(contracts, x.iloc[[0]], config, bounds, np.random.default_rng(9))
    assert first.equals(
        perturb(contracts, x.iloc[[0]], config, bounds, np.random.default_rng(9))
    )
    for field in x:
        if field in bounds:
            assert 1 <= int(first.iloc[0][field]) <= 9
            assert abs(int(first.iloc[0][field]) - int(x.iloc[0][field])) <= 1
        else:
            assert first[field].equals(x.iloc[[0]][field])
    config["fields"] = ["num_medications"]
    with pytest.raises(HealthcareDataError, match="unapproved"):
        perturb(contracts, x.iloc[[0]], config, bounds, np.random.default_rng(9))


def test_fairness_confusion_metrics_and_undefined():
    result = subgroup_metrics(
        np.array([0, 0, 1, 1]), np.array([0.1, 0.8, 0.2, 0.9]), 0.5
    )
    assert (
        result["recall"]
        == result["specificity"]
        == result["false_positive_rate"]
        == result["false_negative_rate"]
        == 0.5
    )
    assert result["positive_prediction_rate"] == 0.5
    assert result["roc_auc"] == 0.75
    single = subgroup_metrics(np.array([0, 0]), np.array([0.1, 0.2]), 0.5)
    assert single["roc_auc"] is single["recall"] is single["average_precision"] is None
    assert single["specificity"] == 1


def test_fairness_support_missingness_alignment_and_cluster_seed():
    config = tiny_config()["fairness"]
    n = 240
    groups = pd.DataFrame(
        {"race": [pd.NA] * n, "gender": ["Female"] * n, "age": ["[50-60)"] * n}
    )
    y = pd.Series([0, 1] * (n // 2))
    p = pd.Series(np.where(y == 1, 0.8, 0.2))
    patients = pd.Series([str(i // 2) for i in range(n)])
    first = audit_subgroups(groups, y, p, patients, config)
    assert first == audit_subgroups(groups, y, p, patients, config)
    missing = next(
        row
        for row in first
        if row["attribute"] == "race" and row["group"] == "__MISSING__"
    )
    assert missing["status"] == "supported" and missing["metrics"]["roc_auc"] == 1
    unsupported = next(row for row in first if row["group"] == "Unknown/Invalid")
    assert (
        unsupported["metrics"] is None and unsupported["counts"]["encounters"] == "<20"
    )
    with pytest.raises(HealthcareDataError, match="alignment"):
        audit_subgroups(groups, y.iloc[::-1], p, patients, config)
    bootstrap = subgroup_intervals(
        y.to_numpy(), p.to_numpy(), patients.to_numpy(), config
    )
    assert bootstrap["prevalence"]["interval"] == [
        0.5,
        0.5,
    ]  # paired outcomes remain together
    assert all(row["valid_replicates"] == 5 for row in bootstrap.values())


def test_counterfactual_no_result_and_every_feature_immutable(fitted):
    contracts, x, _ = fitted
    config = tiny_config()["counterfactual"]
    assert scenario_result(contracts, config)["status"] == "no_feasible_scenario"
    assert scenario_result(contracts, config)["candidates"] == []
    assert validate_scenario(contracts, config, x.iloc[[0]], x.iloc[[0]])
    for field in x:
        proposed = x.iloc[[0]].copy()
        proposed.loc[:, field] = "impossible"
        with pytest.raises(HealthcareDataError, match="immutable"):
            validate_scenario(contracts, config, x.iloc[[0]], proposed)
    with pytest.raises(HealthcareDataError, match="predictor order"):
        validate_scenario(
            contracts, config, x.iloc[[0]], x.iloc[[0]].assign(age="[30-40)")
        )
    bad = copy.deepcopy(config)
    bad["mutable"] = ["num_medications"]
    with pytest.raises(HealthcareDataError, match="not approved"):
        assess(contracts, bad)


@pytest.mark.parametrize("positive_count", [0, 10, 230, 240])
def test_minimum_class_support_withholds_metrics(positive_count):
    config = tiny_config()["fairness"]
    groups = pd.DataFrame(
        {
            "race": ["Caucasian"] * 240,
            "gender": ["Female"] * 240,
            "age": ["[50-60)"] * 240,
        }
    )
    truth = pd.Series([1] * positive_count + [0] * (240 - positive_count))
    p = pd.Series([0.2] * 240)
    patients = pd.Series([str(i) for i in range(240)])
    records = audit_subgroups(groups, truth, p, patients, config)
    assert all(
        row["metrics"] is None and row["status"] == "insufficient_support"
        for row in records
    )


def test_undefined_bootstrap_replicates_are_counted():
    config = tiny_config()["fairness"]
    result = subgroup_intervals(np.zeros(40), np.full(40, 0.2), np.arange(40), config)
    assert result["roc_auc"]["interval"] is None
    assert result["roc_auc"]["undefined_replicates"] == 5
    assert result["brier_score"]["valid_replicates"] == 5


def test_exclusive_holdout_claim_and_protocol_guard(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(audit, "OUTPUT", tmp_path)
    frozen = {"protocol_sha256": "frozen", "identity": {"model_sha256": "model"}}
    monkeypatch.setattr(audit, "verified_protocol", lambda: frozen)
    audit.claim_holdout(frozen)
    original = (tmp_path / "holdout.claim").read_bytes()
    with pytest.raises(HealthcareDataError, match="no retry"):
        audit.claim_holdout(frozen)
    assert (tmp_path / "holdout.claim").read_bytes() == original
    with pytest.raises(HealthcareDataError, match="unverified"):
        audit.claim_holdout({})
