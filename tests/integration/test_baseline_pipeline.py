from __future__ import annotations

import json

import pandas as pd
import pytest

from aletheia.contracts import ArtifactError
from aletheia.experiments.artifacts import publish_run
from aletheia.experiments.manifest import canonical_result_payload
from aletheia.ml import baseline
from aletheia.ml.evaluate import evaluate_models, key_membership_checksum


def _assert_no_held_out_results(value) -> None:
    """Inspect nested fields, allowing only the explicit false held-out flag."""
    if isinstance(value, dict):
        for key, item in value.items():
            assert "prediction" not in key
            if key != "held_out_evaluation_performed":
                assert not key.startswith(("held_out", "test_"))
            _assert_no_held_out_results(item)
    elif isinstance(value, list):
        for item in value:
            _assert_no_held_out_results(item)


def test_training_only_baseline_to_immutable_manifest(
    tmp_path, monkeypatch, synthetic_baseline_run
) -> None:
    raw_path, config_path, dataset, policy, membership, views = synthetic_baseline_run
    training_keys = set(membership.train_keys)
    held_out_keys = set(membership.test_keys)
    assert len(training_keys) == 800
    assert len(held_out_keys) == 200
    assert training_keys.isdisjoint(held_out_keys)
    assert training_keys | held_out_keys == set(views.metadata["row_key"])

    # Both partitions cross the old row-800 boundary: a prefix/suffix cannot pass.
    sequential_training = {f"sgc-{index:04d}" for index in range(1, 801)}
    sequential_holdout = {f"sgc-{index:04d}" for index in range(801, 1001)}
    assert held_out_keys & sequential_training
    assert training_keys & sequential_holdout
    assert held_out_keys != sequential_holdout
    expected_mask = views.metadata["row_key"].isin(training_keys)
    captured_keys = []
    captured_results = []

    def capture_evaluation(features, target, row_keys, config):
        # Check before invoking real CV so a regression cannot fit held-out rows.
        assert len(features) == len(target) == len(row_keys) == 800
        assert row_keys.is_unique
        assert set(row_keys) == training_keys
        assert set(row_keys).isdisjoint(held_out_keys)
        pd.testing.assert_series_equal(
            row_keys,
            views.metadata.loc[expected_mask, "row_key"].reset_index(drop=True),
        )
        pd.testing.assert_frame_equal(
            features, views.model_input().loc[expected_mask].reset_index(drop=True)
        )
        pd.testing.assert_series_equal(
            target,
            views.target.loc[expected_mask, dataset.derived_target].reset_index(
                drop=True
            ),
        )
        assert tuple(features.columns) == policy.prediction
        captured_keys.append(tuple(row_keys))
        result = evaluate_models(features, target, row_keys, config)
        captured_results.append(result)
        return result

    monkeypatch.setattr(baseline, "evaluate_models", capture_evaluation)
    published, manifest = baseline.run_baseline(
        raw_path, config_path, tmp_path / "runs"
    )
    assert len(captured_keys) == len(captured_results) == 2
    assert captured_keys[0] == captured_keys[1]
    assert canonical_result_payload(captured_results[0]) == canonical_result_payload(
        captured_results[1]
    )
    stored = json.loads((published / "manifest.json").read_text(encoding="utf-8"))
    assert stored == manifest
    assert stored["dataset"]["sha256"] == dataset.raw_sha256
    assert (
        stored["split_membership_checksum"]
        == json.loads((tmp_path / "synthetic_split.json").read_text(encoding="utf-8"))[
            "membership_checksum"
        ]
    )
    assert stored["training_membership_checksum"] == key_membership_checksum(
        membership.train_keys
    )
    assert stored["results"]["evaluation_scope"] == (
        "locked_training_partition_cross_validation"
    )
    assert stored["results"]["evaluated_row_count"] == 800
    assert stored["held_out_evaluation_performed"] is False
    assert stored["fitted_model_artifact"] is None
    shared_folds = stored["results"]["fold_membership_checksums"]
    assert len(shared_folds) == len(set(shared_folds)) == 5
    for model in stored["results"]["models"].values():
        assert model["fold_membership_checksums"] == shared_folds
    assert stored["fold_membership_checksums"] == shared_folds
    _assert_no_held_out_results(stored)
    assert list(published.iterdir()) == [published / "manifest.json"]
    assert list((tmp_path / "runs").iterdir()) == [published]
    with pytest.raises(ArtifactError, match="already exists"):
        publish_run(manifest, tmp_path / "runs")
    assert list(published.iterdir()) == [published / "manifest.json"]
    assert (
        json.loads((published / "manifest.json").read_text(encoding="utf-8")) == stored
    )
