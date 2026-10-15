"""Intake boundary, full calibrated callable, and independent attribution oracles."""

import math

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from aletheia.application.case_input import OPTIONS, CaseInput, field_mapping


def values(release):
    return {k: int(v) if k not in OPTIONS else v for k, v in release.case.items()}


def test_complete_mapping_and_canonicalization(release):
    case = CaseInput.model_validate(values(release))
    assert list(case.raw()) == release.features
    assert case.raw() == release.case
    mapping = field_mapping()["fields"]
    assert [f["field"] for f in mapping] == release.features
    assert all(f["required"] and f["label"] for f in mapping)


@pytest.mark.parametrize("name", list(CaseInput.model_fields))
def test_missing_and_every_boundary(release, name):
    payload = values(release)
    del payload[name]
    with pytest.raises(ValidationError):
        CaseInput.model_validate(payload)
    payload = values(release)
    if name in OPTIONS:
        for option in OPTIONS[name]:
            assert (
                CaseInput.model_validate(dict(payload, **{name: option})).raw()[name]
                == option
            )
        invalid = ["unrecognized", "", None, 1]
    else:
        rule = CaseInput.model_json_schema()["properties"][name]
        low, high = rule["minimum"], rule["maximum"]
        for bound in (low, high):
            assert CaseInput.model_validate(dict(payload, **{name: bound})).raw()[
                name
            ] == str(bound)
        invalid = [
            low - 1,
            high + 1,
            True,
            "1",
            1.5,
            math.nan,
            math.inf,
            -math.inf,
            None,
        ]
    for value in invalid:
        with pytest.raises(ValidationError):
            CaseInput.model_validate(dict(payload, **{name: value}))


@pytest.mark.parametrize("name", ["patient_nbr", "name", "notes", "readmitted", "age"])
def test_unrelated_and_pii_fields_refused(release, name):
    with pytest.raises(ValidationError):
        CaseInput.model_validate(dict(values(release), **{name: "forbidden"}))


def test_frozen_calibration_and_reference_contrast(release, monkeypatch):
    from sklearn.pipeline import Pipeline

    def no_fit(*args, **kwargs):
        raise AssertionError("prediction attempted to fit")

    monkeypatch.setattr(Pipeline, "fit", no_fit)
    case = CaseInput.model_validate(values(release))
    frame = pd.DataFrame([case.raw()], columns=release.features)
    base = release.bundle["model"].predict_proba(frame)[0, 1]
    a = release.bundle["calibrator"].coef_[0, 0]
    b = release.bundle["calibrator"].intercept_[0]
    clipped = np.clip(base, 1e-6, 1 - 1e-6)
    independent = 1 / (1 + np.exp(-(a * np.log(clipped / (1 - clipped)) + b)))
    original = release.analyze(case)
    assert original["probability"] == pytest.approx(independent, abs=1e-12)
    assert original["probability"] == pytest.approx(release.score(), abs=1e-12)
    assert all(f["contribution"] == 0 for f in original["explanation"]["features"])
    case = case.model_copy(update={"number_inpatient": 4})
    changed = release.analyze(case)
    assert release.analyze(case) == changed
    factors = {f["field"]: f for f in changed["explanation"]["features"]}
    difference = changed["probability"] - original["probability"]
    assert factors["number_inpatient"]["contribution"] == pytest.approx(
        difference, abs=1e-12
    )
    assert factors["number_inpatient"]["direction"] == (
        "raises" if difference > 0 else "lowers"
    )
    assert all(
        f["contribution"] == 0 for k, f in factors.items() if k != "number_inpatient"
    )
    assert changed["stability"]["scope"] == "model_level"
    assert changed["class_at_threshold"] == int(changed["probability"] >= 0.5)


@pytest.mark.parametrize("score,expected", [(0.499, 0), (0.5, 1), (0.501, 1)])
def test_descriptive_threshold_boundary(release, monkeypatch, score, expected):
    # A constant software fixture makes the exact boundary reachable, independent
    # of the real classifier's measured probabilities. No artifact is changed.
    monkeypatch.setattr(
        release.bundle["model"],
        "predict_proba",
        lambda frame: np.tile([1 - score, score], (len(frame), 1)),
    )
    monkeypatch.setitem(release.bundle, "calibrator", None)
    output = release.analyze(CaseInput.model_validate(values(release)))
    assert output["probability"] == score
    assert output["threshold"] == 0.5
    assert output["class_at_threshold"] == expected
