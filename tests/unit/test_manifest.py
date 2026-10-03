from __future__ import annotations

from copy import deepcopy

import pytest

from aletheia.config import load_dataset_contract, load_feature_policy
from aletheia.contracts import ArtifactError, ExperimentError
from aletheia.experiments.artifacts import publish_run
from aletheia.experiments.manifest import build_manifest, validate_manifest


def _results() -> dict:
    metrics = {
        name: 0.5
        for name in (
            "roc_auc",
            "average_precision",
            "balanced_accuracy",
            "adverse_recall",
            "specificity",
            "precision",
            "f1",
            "log_loss",
            "brier_score",
        )
    }
    aggregate = {
        name: {"mean": value, "standard_deviation": 0.0}
        for name, value in metrics.items()
    }
    checksums = [str(index) * 64 for index in range(1, 6)]
    model = {
        "fold_membership_checksums": checksums,
        "per_fold_metrics": [metrics] * 5,
        "aggregate_metrics": aggregate,
    }
    return {
        "evaluation_scope": "locked_training_partition_cross_validation",
        "evaluated_row_count": 800,
        "fold_membership_checksums": checksums,
        "models": {"dummy": model, "logistic_regression": deepcopy(model)},
    }


@pytest.fixture
def valid_manifest(baseline_config):
    dataset = load_dataset_contract()
    policy = load_feature_policy(dataset=dataset)
    return build_manifest(
        run_id="baseline-v1-test",
        config=baseline_config,
        config_path="configs/experiments/baseline_v1.toml",
        dataset=dataset,
        policy=policy,
        split_membership_checksum=baseline_config.split_membership_checksum,
        training_membership_checksum="a" * 64,
        results=_results(),
        source_control={
            "base_git_commit": "b" * 40,
            "working_tree_dirty": True,
            "diff_checksum": "c" * 64,
        },
        created_at="2026-09-30T00:00:00+00:00",
    )


def test_manifest_has_required_cross_references(valid_manifest) -> None:
    validate_manifest(valid_manifest)

    assert valid_manifest["dataset"]["sha256"] == (
        "5f363343f356ca38a0236baab849e472846399b2176ccc5bd686483dd8a7562f"
    )
    assert valid_manifest["target"]["positive_class"] == 1
    assert valid_manifest["transformed_features"]["count"] == 59
    assert valid_manifest["held_out_evaluation_performed"] is False
    assert valid_manifest["fitted_model_artifact"] is None


def test_manifest_refuses_held_out_metrics(valid_manifest) -> None:
    invalid = deepcopy(valid_manifest)
    invalid["results"]["held_out_metrics"] = {"roc_auc": 0.9}

    with pytest.raises(ExperimentError, match="held-out"):
        validate_manifest(invalid)


def test_manifest_refuses_nonidentical_model_folds(valid_manifest) -> None:
    invalid = deepcopy(valid_manifest)
    invalid["results"]["models"]["dummy"]["fold_membership_checksums"][0] = "f" * 64

    with pytest.raises(ExperimentError, match="identical folds"):
        validate_manifest(invalid)


def test_atomic_publication_and_overwrite_refusal(tmp_path, valid_manifest) -> None:
    published = publish_run(valid_manifest, tmp_path / "runs")

    assert published.name == valid_manifest["run_id"]
    assert (published / "manifest.json").is_file()
    assert list(published.iterdir()) == [published / "manifest.json"]
    assert not list((tmp_path / "runs").glob(".aletheia-run-*"))
    with pytest.raises(ArtifactError, match="already exists"):
        publish_run(valid_manifest, tmp_path / "runs")
