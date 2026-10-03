from __future__ import annotations

import json

from aletheia.config import load_dataset_contract, load_feature_policy
from aletheia.experiments.artifacts import publish_run
from aletheia.experiments.manifest import build_manifest, canonical_result_payload
from aletheia.ml.evaluate import evaluate_models, key_membership_checksum


def test_training_only_baseline_to_immutable_manifest(
    tmp_path, baseline_config, baseline_training_data
) -> None:
    features, target, training_keys = baseline_training_data
    held_out_keys = {f"sgc-{index:04d}" for index in range(801, 1001)}
    assert set(training_keys).isdisjoint(held_out_keys)

    first = evaluate_models(features, target, training_keys, baseline_config)
    second = evaluate_models(features, target, training_keys, baseline_config)
    assert canonical_result_payload(first) == canonical_result_payload(second)

    dataset = load_dataset_contract()
    policy = load_feature_policy(dataset=dataset)
    manifest = build_manifest(
        run_id="baseline-v1-integration",
        config=baseline_config,
        config_path="configs/experiments/baseline_v1.toml",
        dataset=dataset,
        policy=policy,
        split_membership_checksum=baseline_config.split_membership_checksum,
        training_membership_checksum=key_membership_checksum(list(training_keys)),
        results=first,
        source_control={
            "base_git_commit": "b" * 40,
            "working_tree_dirty": True,
            "diff_checksum": "c" * 64,
        },
        created_at="2026-09-30T00:00:00+00:00",
    )
    published = publish_run(manifest, tmp_path / "runs")
    stored = json.loads((published / "manifest.json").read_text(encoding="utf-8"))

    assert stored["results"]["evaluated_row_count"] == 800
    assert stored["held_out_evaluation_performed"] is False
    assert stored["fitted_model_artifact"] is None
    assert (
        stored["results"]["models"]["dummy"]["fold_membership_checksums"]
        == stored["results"]["models"]["logistic_regression"][
            "fold_membership_checksums"
        ]
    )
    assert not any(
        path.suffix in {".joblib", ".pkl", ".pickle"} for path in published.iterdir()
    )
