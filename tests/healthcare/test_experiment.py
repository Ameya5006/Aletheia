"""Immutable evidence and trusted-local artifact refusal tests."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

import aletheia.domains.healthcare.experiment as experiment
from aletheia.domains.healthcare.experiment import (
    deterministic_projection,
    digest,
    evaluate_once,
    load_config,
    load_trusted_artifact,
    save_artifact,
    select_protocol,
    verify_training_record,
    write_once,
)
from aletheia.domains.healthcare.foundation import HealthcareDataError, load_contracts


def test_immutable_manifest_and_artifact_refusal(tmp_path: Path) -> None:
    path = tmp_path / "record.json"
    write_once(path, {"version": 1})
    with pytest.raises(FileExistsError):
        write_once(path, {"version": 2})
    local = tmp_path / "healthcare-model-v1" / "model.joblib"
    identity = {"family": "dummy"}
    manifest = save_artifact(local, object(), None, identity)
    assert load_trusted_artifact(local, manifest, identity)["calibrator"] is None
    with pytest.raises(HealthcareDataError, match="protocol mismatch"):
        load_trusted_artifact(local, manifest, {"family": "forest"})
    with pytest.raises(HealthcareDataError, match="checksum mismatch"):
        local.write_bytes(local.read_bytes() + b"tamper")
        load_trusted_artifact(local, manifest, identity)
    changed = copy.deepcopy(manifest)
    changed["versions"]["scikit_learn"] = "0.0"
    with pytest.raises(HealthcareDataError, match="version"):
        load_trusted_artifact(local, changed, identity)


def test_selection_ap_margin_uses_calibration_guard() -> None:
    config = load_config()

    def summary(ap: float, brier: float) -> dict:
        return {
            name: {"mean": value}
            for name, value in (
                ("average_precision", ap),
                ("brier_score", brier),
                ("roc_auc", 0.7),
                ("log_loss", 0.4),
            )
        }

    evidence = {
        "families": {
            "logistic": {
                "raw_summary": summary(0.20, 0.09),
                "sigmoid_summary": summary(0.199, 0.08),
            },
            "forest": {
                "raw_summary": summary(0.18, 0.07),
                "sigmoid_summary": summary(0.18, 0.07),
            },
        }
    }
    assert select_protocol(evidence, config)["winner"]["calibration"] == "sigmoid"
    reordered = {"families": dict(reversed(list(evidence["families"].items())))}
    assert select_protocol(evidence, config) == select_protocol(reordered, config)


def test_deterministic_repeat_compares_results_not_wall_clock() -> None:
    first = {
        "families": {
            "dummy": {
                "folds": [
                    {
                        "fit_seconds": 1.0,
                        "predict_seconds": 2.0,
                        "raw": {"average_precision": 0.2},
                        "inner": [
                            {
                                "folds": [
                                    {
                                        "fit_seconds": 0.1,
                                        "predict_seconds": 0.2,
                                        "validation": {"average_precision": 0.2},
                                    }
                                ]
                            }
                        ],
                    }
                ]
            }
        }
    }
    second = copy.deepcopy(first)
    second["families"]["dummy"]["folds"][0]["fit_seconds"] = 9.0
    assert deterministic_projection(first) == deterministic_projection(second)
    second["families"]["dummy"]["folds"][0]["raw"]["average_precision"] = 0.3
    assert deterministic_projection(first) != deterministic_projection(second)


def test_partial_training_record_is_refused() -> None:
    config = load_config()
    with pytest.raises(HealthcareDataError, match="incomplete training families"):
        verify_training_record(
            {"identity": config["experiment"], "results": {"families": {}}}, config
        )


def test_holdout_guard_refuses_existing_claim_before_prediction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "healthcare-model-v1"
    output.mkdir()
    config = load_config()
    training = {"families": {}}
    for family in ("dummy", "logistic", "forest", "histogram"):
        training["families"][family] = {
            "folds": [],
            "raw_summary": {
                "average_precision": {"mean": 0.2},
                "brier_score": {"mean": 0.1},
                "roc_auc": {"mean": 0.5},
                "log_loss": {"mean": 0.4},
            },
            "sigmoid_summary": {
                "average_precision": {"mean": 0.2},
                "brier_score": {"mean": 0.1},
                "roc_auc": {"mean": 0.5},
                "log_loss": {"mean": 0.4},
            },
        }
    training_record = {
        "identity": config["experiment"],
        "results": training,
        "deterministic_sha256": digest(training),
    }
    write_once(output / "nested_cv.json", training_record)
    chosen = select_protocol(training, config)
    protocol = {
        "family": chosen["winner"]["family"],
        "calibration": chosen["winner"]["calibration"],
        "config_sha256": hashlib.sha256(experiment.CONFIG.read_bytes()).hexdigest(),
        "nested_cv_sha256": training_record["deterministic_sha256"],
    }
    selection = {
        "protocol": protocol,
        "selection_sha256": digest(protocol),
        "identity_sha256": digest(config["experiment"]),
        "selection_evidence": chosen,
    }
    write_once(output / "selection.json", selection)
    artifact = {"sha256": "unused"}
    write_once(output / "artifact.json", artifact)
    (output / "holdout.claim").touch()
    monkeypatch.setattr(experiment, "verify_training_record", lambda *_: None)
    monkeypatch.setattr(
        experiment,
        "verify_split_lock",
        lambda *_: {
            "dataset_identifier": config["experiment"]["dataset_identifier"],
            "dataset_sha256": config["experiment"]["raw_sha256"],
            "feature_policy_version": config["experiment"]["feature_policy_version"],
            "target_mapping_version": config["experiment"]["target_version"],
            "version": config["experiment"]["split_version"],
            "membership_sha256": config["experiment"]["membership_sha256"],
        },
    )
    # No model or frame is provided. The existing claim must reject before prediction.
    with pytest.raises(HealthcareDataError):
        evaluate_once(output, config, load_contracts(), None, selection, artifact)
    assert json.loads((output / "selection.json").read_text()) == selection
