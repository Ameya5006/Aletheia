"""Data-only command interface for the approved Phase 3 foundation."""

from __future__ import annotations

import argparse
from pathlib import Path

from aletheia.config import load_dataset_contract, load_feature_policy
from aletheia.contracts import DataFoundationError
from aletheia.data.acquire import acquire_dataset
from aletheia.data.load import load_raw_data
from aletheia.data.roles import build_feature_views
from aletheia.data.split import (
    create_split_contract,
    generate_membership,
    load_split_contract,
    verify_split_contract,
    write_split_contract,
)
from aletheia.data.target import add_adverse_target
from aletheia.data.validate import validate_raw_data


def _validated_data(raw_file: Path):
    dataset = load_dataset_contract()
    policy = load_feature_policy(dataset=dataset)
    frame = load_raw_data(raw_file, dataset)
    validate_raw_data(frame, dataset, policy)
    mapped = add_adverse_target(frame, dataset)
    views = build_feature_views(mapped, policy, dataset)
    return dataset, policy, mapped, views


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m aletheia.data")
    commands = parser.add_subparsers(dest="command", required=True)
    acquire = commands.add_parser("acquire", help="download and verify approved data")
    acquire.add_argument("--destination", type=Path, required=True)
    validate = commands.add_parser("validate", help="validate an approved raw file")
    validate.add_argument("--raw-file", type=Path, required=True)
    split = commands.add_parser("split", help="create or verify the locked split")
    split.add_argument("--raw-file", type=Path, required=True)
    split.add_argument("--contract", type=Path, required=True)
    split.add_argument("--verify", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run one bounded data command; no preprocessing or model work is available."""
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "acquire":
            dataset = load_dataset_contract()
            raw_path = acquire_dataset(dataset, args.destination)
            print(
                f"verified raw dataset: {raw_path} "
                f"({dataset.raw_size} bytes, sha256={dataset.raw_sha256})"
            )
            return 0

        dataset, policy, mapped, views = _validated_data(args.raw_file)
        target_counts = (
            mapped[dataset.derived_target].value_counts().sort_index().to_dict()
        )
        if args.command == "validate":
            print(
                f"validated {len(mapped)} rows, {len(dataset.columns)} raw columns; "
                f"adverse_event counts={target_counts}; "
                f"prediction_features={len(views.prediction_columns)}"
            )
            return 0

        membership = generate_membership(
            views.metadata["row_key"], views.target[dataset.derived_target]
        )
        if args.verify:
            locked = load_split_contract(args.contract)
            verify_split_contract(
                locked,
                views.metadata["row_key"],
                views.target[dataset.derived_target],
                dataset_sha256=dataset.raw_sha256,
                feature_policy_version=policy.version,
                target_mapping_identifier=dataset.target_mapping_identifier,
            )
            checksum = locked["membership_checksum"]
            action = "verified"
        else:
            locked = create_split_contract(
                membership,
                views.metadata["row_key"],
                views.target[dataset.derived_target],
                dataset_sha256=dataset.raw_sha256,
                feature_policy_version=policy.version,
                target_mapping_identifier=dataset.target_mapping_identifier,
            )
            write_split_contract(locked, args.contract)
            checksum = locked["membership_checksum"]
            action = "created"
        print(
            f"{action} split: train={len(membership.train_keys)}, "
            f"test={len(membership.test_keys)}, membership_sha256={checksum}"
        )
        return 0
    except DataFoundationError as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
