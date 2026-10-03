"""Execute the approved Phase 4 baseline without touching held-out outcomes."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from aletheia.config import (
    DEFAULT_BASELINE_CONFIG,
    load_baseline_experiment_config,
    load_dataset_contract,
    load_feature_policy,
)
from aletheia.contracts import DataFoundationError, ExperimentError
from aletheia.data.load import load_raw_data
from aletheia.data.roles import build_feature_views
from aletheia.data.split import load_split_contract, verify_split_contract
from aletheia.data.target import add_adverse_target
from aletheia.data.validate import validate_raw_data
from aletheia.experiments.artifacts import publish_run
from aletheia.experiments.manifest import (
    build_manifest,
    canonical_result_payload,
    source_control_identity,
)
from aletheia.ml.evaluate import evaluate_models, key_membership_checksum


def calculate_baseline(
    raw_file: str | Path,
    config_path: str | Path = DEFAULT_BASELINE_CONFIG,
) -> tuple[dict, dict]:
    """Verify all identities, then calculate CV metrics on training keys only."""
    dataset = load_dataset_contract()
    policy = load_feature_policy(dataset=dataset)
    config = load_baseline_experiment_config(
        config_path, dataset=dataset, policy=policy
    )
    raw = load_raw_data(raw_file, dataset)
    validate_raw_data(raw, dataset, policy)
    mapped = add_adverse_target(raw, dataset)
    views = build_feature_views(mapped, policy, dataset)
    split_contract = load_split_contract(config.split_contract_path)
    if split_contract.get("membership_checksum") != config.split_membership_checksum:
        raise ExperimentError("experiment and split membership checksums disagree")
    membership = verify_split_contract(
        split_contract,
        views.metadata["row_key"],
        views.target[dataset.derived_target],
        dataset_sha256=dataset.raw_sha256,
        feature_policy_version=policy.version,
        target_mapping_identifier=dataset.target_mapping_identifier,
    )
    train_key_set = set(membership.train_keys)
    source_keys = views.metadata["row_key"].astype(str)
    training_mask = source_keys.isin(train_key_set)
    training_keys = source_keys.loc[training_mask].reset_index(drop=True)
    if set(training_keys) != train_key_set or len(training_keys) != 800:
        raise ExperimentError("training subset does not match locked membership")
    if set(training_keys) & set(membership.test_keys):
        raise ExperimentError("held-out keys entered the training subset")
    model_input = views.model_input().loc[training_mask].reset_index(drop=True)
    target = (
        views.target.loc[training_mask, dataset.derived_target]
        .astype("int64")
        .reset_index(drop=True)
    )
    results = evaluate_models(model_input, target, training_keys, config)
    context = {
        "dataset": dataset,
        "policy": policy,
        "config": config,
        "split_membership_checksum": split_contract["membership_checksum"],
        "training_membership_checksum": key_membership_checksum(list(training_keys)),
    }
    return results, context


def run_baseline(
    raw_file: str | Path,
    config_path: str | Path = DEFAULT_BASELINE_CONFIG,
    artifact_root: str | Path = Path("artifacts/runs"),
) -> tuple[Path, dict]:
    """Calculate twice, require exact equality, then publish one manifest."""
    first, context = calculate_baseline(raw_file, config_path)
    second, second_context = calculate_baseline(raw_file, config_path)
    if canonical_result_payload(first) != canonical_result_payload(second):
        raise ExperimentError("deterministic baseline recalculation did not match")
    comparable_context = (
        context["split_membership_checksum"],
        context["training_membership_checksum"],
    )
    if comparable_context != (
        second_context["split_membership_checksum"],
        second_context["training_membership_checksum"],
    ):
        raise ExperimentError("deterministic identity recalculation did not match")
    timestamp = datetime.now(UTC)
    short_identity = context["training_membership_checksum"][:10]
    run_id = f"baseline-v1-{timestamp:%Y%m%dT%H%M%S%fZ}-{short_identity}"
    manifest = build_manifest(
        run_id=run_id,
        config=context["config"],
        config_path=config_path,
        dataset=context["dataset"],
        policy=context["policy"],
        split_membership_checksum=context["split_membership_checksum"],
        training_membership_checksum=context["training_membership_checksum"],
        results=first,
        source_control=source_control_identity(),
        created_at=timestamp.isoformat(),
    )
    return publish_run(manifest, artifact_root), manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m aletheia.ml.baseline")
    parser.add_argument("--raw-file", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_BASELINE_CONFIG)
    parser.add_argument("--artifact-root", type=Path, default=Path("artifacts/runs"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        run_path, manifest = run_baseline(
            args.raw_file, args.config, args.artifact_root
        )
    except DataFoundationError as exc:
        raise SystemExit(f"error: {exc}") from exc
    summary = {
        "run_id": manifest["run_id"],
        "run_path": str(run_path),
        "evaluated_rows": manifest["results"]["evaluated_row_count"],
        "held_out_evaluation_performed": manifest["held_out_evaluation_performed"],
        "aggregate_metrics": {
            model: values["aggregate_metrics"]
            for model, values in manifest["results"]["models"].items()
        },
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
