"""Offline synthetic orchestration, publication privacy and binding refusals."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from test_audit import fitted, tiny_config  # noqa: F401

from aletheia.domains.healthcare import audit
from aletheia.domains.healthcare.experiment import read_record
from aletheia.domains.healthcare.foundation import HealthcareDataError


@pytest.fixture
def published(tmp_path: Path, monkeypatch, fitted):  # noqa: F811
    contracts, x, bundle = fitted
    config = tiny_config()
    identity = {
        "dataset": {"identifier": "synthetic"},
        "model_sha256": "synthetic-model",
        "selection_sha256": "synthetic-selection",
        "split_lock_sha256": "synthetic-lock",
    }
    output = tmp_path / "healthcare-audit-v1"
    monkeypatch.setattr(audit, "OUTPUT", output)
    model_run = tmp_path / "healthcare-model-v1"
    model_run.mkdir()
    for name in (
        "artifact.json",
        "model.joblib",
        "selection.json",
        "nested_cv.json",
        "holdout.json",
        "holdout.claim",
    ):
        (model_run / name).write_bytes(b"synthetic binding fixture")
    monkeypatch.setattr(audit, "MODEL_RUN", model_run)
    monkeypatch.setattr(audit, "load_protocol", lambda: config)
    monkeypatch.setattr(audit, "verify_model", lambda _: (bundle, identity))
    frame = x.assign(
        readmitted_30d=[int(i % 3 == 0) for i in range(len(x))],
        patient_nbr=[str(i) for i in range(len(x))],
        race="Caucasian",
        gender="Female",
        age="[50-60)",
    )
    # Source/partition providers are synthetic; audit functions, freeze, claim,
    # full calibrated inference, aggregate metrics and publication execute for real.
    monkeypatch.setattr(audit, "load_raw", lambda *_: frame)
    monkeypatch.setattr(audit, "cohort", lambda *_: frame)
    monkeypatch.setattr(audit, "verify_split_lock", lambda *_: {})
    monkeypatch.setattr(
        audit, "partition", lambda *_: (frame.iloc[:60], frame.iloc[60:])
    )
    frozen = audit.freeze()
    assert not (output / "holdout.claim").exists()
    assert not (output / "results.json").exists()
    assert frozen["holdout_access"].startswith("not accessed")
    result = audit.run()
    assert result["status"] == "verified"
    return output, config


def test_complete_synthetic_audit_and_overwrite_refusal(published):
    output, config = published
    saved = read_record(output / "results.json")
    assert saved["holdout_access"]["encounters"] == 20
    assert saved["stability"]["comparisons"] == 4
    assert saved["synthetic_local"]["identity"] == saved["identity"]
    assert {
        row["field"]: row["value"] for row in saved["synthetic_local"]["features"]
    } == config["synthetic_example"]
    before = {p.name: p.read_bytes() for p in output.iterdir()}
    with pytest.raises(HealthcareDataError, match="refusing rerun"):
        audit.run()
    with pytest.raises(HealthcareDataError, match="overwrite"):
        audit.freeze()
    assert before == {p.name: p.read_bytes() for p in output.iterdir()}


@pytest.mark.parametrize(
    "mutation",
    [
        "raw_records",
        "local_value",
        "patient_predictions",
        "mapping",
        "small_count",
        "aggregate_vector",
    ],
)
def test_privacy_refuses_real_values_or_identifiers(published, mutation):
    output, config = published
    saved = read_record(output / "results.json")
    if mutation == "raw_records":
        saved["raw_records"] = [{"encounter_id": "private"}]
    elif mutation == "local_value":
        saved["synthetic_local"]["features"][0]["value"] = "private"
    elif mutation == "patient_predictions":
        saved["global"]["features"][0]["patient_predictions"] = [0.4]
    elif mutation == "mapping":
        saved["mapping"][0]["source"] = "patient_nbr"
    elif mutation == "small_count":
        saved["fairness"][0]["counts"]["patients"] = 1
    else:
        saved["stability"]["all"]["normalized_l1"]["mean"] = [0.1, 0.2]
    with pytest.raises(HealthcareDataError):
        audit.validate_publication(saved, config)


def test_artifact_tamper_refusal(published):
    output, _ = published
    path = output / "results.json"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(HealthcareDataError, match="manifest binding"):
        audit.inspect()


def test_protocol_config_code_binding_refusal(published, monkeypatch):
    _, _ = published
    original = audit.bindings()
    changed = copy.deepcopy(original)
    changed["configs/splits/healthcare_uci296_v1.lock.json"] = "tampered"
    monkeypatch.setattr(audit, "bindings", lambda: changed)
    with pytest.raises(HealthcareDataError, match="binding mismatch"):
        audit.verified_protocol()


def test_existing_claim_stops_before_prediction(published, monkeypatch):
    monkeypatch.setattr(
        audit, "probability", lambda *_: pytest.fail("prediction attempted after claim")
    )
    with pytest.raises(HealthcareDataError, match="refusing rerun"):
        audit.run()
