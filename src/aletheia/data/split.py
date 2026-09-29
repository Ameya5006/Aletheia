"""Deterministic, locked train/test membership without preprocessing or fitting."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import sklearn
from sklearn.model_selection import StratifiedShuffleSplit

from aletheia.contracts import SplitContractError

SPLIT_CONTRACT_VERSION = "1.0"
SPLITTER_NAME = "StratifiedShuffleSplit"
TEST_FRACTION = 0.20
RANDOM_SEED = 42
STRATIFICATION_TARGET = "adverse_event"


@dataclass(frozen=True)
class SplitMembership:
    """Explicit row-key membership for the two fixed partitions."""

    train_keys: tuple[str, ...]
    test_keys: tuple[str, ...]


def validate_membership(
    all_keys: tuple[str, ...] | list[str],
    train_keys: tuple[str, ...] | list[str],
    test_keys: tuple[str, ...] | list[str],
) -> None:
    """Reject duplicate, unknown, overlapping, or incomplete membership."""
    all_list, train_list, test_list = list(all_keys), list(train_keys), list(test_keys)
    if len(all_list) != len(set(all_list)):
        raise SplitContractError("source row keys are not unique")
    if len(train_list) != len(set(train_list)):
        raise SplitContractError("training membership contains a duplicate key")
    if len(test_list) != len(set(test_list)):
        raise SplitContractError("test membership contains a duplicate key")
    all_set, train_set, test_set = set(all_list), set(train_list), set(test_list)
    unknown = sorted((train_set | test_set) - all_set)
    if unknown:
        raise SplitContractError(f"membership contains unknown key {unknown[0]!r}")
    overlap = sorted(train_set & test_set)
    if overlap:
        raise SplitContractError(f"partition overlap at row key {overlap[0]!r}")
    missing = sorted(all_set - (train_set | test_set))
    if missing:
        raise SplitContractError(f"membership does not cover row key {missing[0]!r}")


def generate_membership(
    row_keys: pd.Series,
    adverse_target: pd.Series,
    *,
    test_fraction: float = TEST_FRACTION,
    seed: int = RANDOM_SEED,
) -> SplitMembership:
    """Create membership only, using the approved target for stratification."""
    if len(row_keys) != len(adverse_target):
        raise SplitContractError("row keys and stratification target are not aligned")
    if row_keys.isna().any() or not row_keys.is_unique:
        raise SplitContractError("row keys must be unique and non-null")
    splitter = StratifiedShuffleSplit(
        n_splits=1, test_size=test_fraction, random_state=seed
    )
    train_index, test_index = next(
        splitter.split([[0]] * len(row_keys), adverse_target)
    )
    train_keys = tuple(sorted(str(row_keys.iloc[index]) for index in train_index))
    test_keys = tuple(sorted(str(row_keys.iloc[index]) for index in test_index))
    validate_membership(tuple(row_keys.astype(str)), train_keys, test_keys)
    return SplitMembership(train_keys=train_keys, test_keys=test_keys)


def canonical_membership_serialization(membership: SplitMembership) -> bytes:
    """Serialize sorted partition keys as canonical UTF-8 JSON without whitespace."""
    payload = {
        "test_row_keys": sorted(membership.test_keys),
        "train_row_keys": sorted(membership.train_keys),
    }
    return json.dumps(
        payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def membership_checksum(membership: SplitMembership) -> str:
    """Return SHA-256 of the exact canonical membership serialization."""
    return hashlib.sha256(canonical_membership_serialization(membership)).hexdigest()


def _class_counts(
    keys: tuple[str, ...], row_keys: pd.Series, target: pd.Series
) -> dict[str, int]:
    by_key = dict(zip(row_keys.astype(str), target.astype(int), strict=True))
    counts = {"0": 0, "1": 0}
    for key in keys:
        value = str(by_key[key])
        counts[value] = counts.get(value, 0) + 1
    return counts


def create_split_contract(
    membership: SplitMembership,
    row_keys: pd.Series,
    adverse_target: pd.Series,
    *,
    dataset_sha256: str,
    feature_policy_version: str,
    target_mapping_identifier: str,
) -> dict[str, Any]:
    """Create the compact versioned lock; training keys remain a complement."""
    validate_membership(
        tuple(row_keys.astype(str)), membership.train_keys, membership.test_keys
    )
    return {
        "contract_version": SPLIT_CONTRACT_VERSION,
        "dataset_sha256": dataset_sha256,
        "feature_policy_version": feature_policy_version,
        "target_mapping_identifier": target_mapping_identifier,
        "splitter": {
            "name": SPLITTER_NAME,
            "scikit_learn_version": sklearn.__version__,
            "test_fraction": TEST_FRACTION,
            "seed": RANDOM_SEED,
            "stratification_target": STRATIFICATION_TARGET,
        },
        "partition_counts": {
            "train": len(membership.train_keys),
            "test": len(membership.test_keys),
        },
        "class_counts": {
            "train": _class_counts(membership.train_keys, row_keys, adverse_target),
            "test": _class_counts(membership.test_keys, row_keys, adverse_target),
        },
        "test_row_keys": list(membership.test_keys),
        "membership_checksum": membership_checksum(membership),
    }


def write_split_contract(contract: dict[str, Any], path: str | Path) -> None:
    """Write a new lock deterministically; never overwrite existing membership."""
    contract_path = Path(path)
    if contract_path.exists():
        raise SplitContractError(f"split contract already exists: {contract_path}")
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def load_split_contract(path: str | Path) -> dict[str, Any]:
    """Load a JSON split lock and reject non-object or malformed content."""
    contract_path = Path(path)
    try:
        result = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SplitContractError(
            f"cannot load split contract {contract_path}: {exc}"
        ) from exc
    if not isinstance(result, dict):
        raise SplitContractError("split contract must be a JSON object")
    return result


def verify_split_contract(
    contract: dict[str, Any],
    row_keys: pd.Series,
    adverse_target: pd.Series,
    *,
    dataset_sha256: str,
    feature_policy_version: str,
    target_mapping_identifier: str,
) -> SplitMembership:
    """Recreate and verify every identity, membership, count, and checksum field."""
    required = {
        "contract_version",
        "dataset_sha256",
        "feature_policy_version",
        "target_mapping_identifier",
        "splitter",
        "partition_counts",
        "class_counts",
        "test_row_keys",
        "membership_checksum",
    }
    missing_fields = sorted(required - set(contract))
    if missing_fields:
        raise SplitContractError(f"split contract is missing {missing_fields[0]!r}")
    expected_scalars = {
        "contract_version": SPLIT_CONTRACT_VERSION,
        "dataset_sha256": dataset_sha256,
        "feature_policy_version": feature_policy_version,
        "target_mapping_identifier": target_mapping_identifier,
    }
    for field, expected in expected_scalars.items():
        if contract.get(field) != expected:
            raise SplitContractError(
                f"split contract {field} mismatch: expected {expected!r}, "
                f"got {contract.get(field)!r}"
            )

    splitter = contract.get("splitter")
    if not isinstance(splitter, dict):
        raise SplitContractError("splitter must be an object")
    expected_splitter = {
        "name": SPLITTER_NAME,
        "test_fraction": TEST_FRACTION,
        "seed": RANDOM_SEED,
        "stratification_target": STRATIFICATION_TARGET,
    }
    for field, expected in expected_splitter.items():
        if splitter.get(field) != expected:
            raise SplitContractError(f"splitter {field} mismatch")
    if not isinstance(splitter.get("scikit_learn_version"), str):
        raise SplitContractError("splitter scikit_learn_version is missing")

    test_keys_value = contract.get("test_row_keys")
    if not isinstance(test_keys_value, list) or not all(
        isinstance(key, str) for key in test_keys_value
    ):
        raise SplitContractError("test_row_keys must be a list of strings")
    all_keys = tuple(row_keys.astype(str))
    test_keys = tuple(test_keys_value)
    if len(test_keys) != len(set(test_keys)):
        raise SplitContractError("test membership contains a duplicate key")
    unknown = sorted(set(test_keys) - set(all_keys))
    if unknown:
        raise SplitContractError(f"test membership contains unknown key {unknown[0]!r}")
    train_keys = tuple(sorted(set(all_keys) - set(test_keys)))
    membership = SplitMembership(
        train_keys=train_keys, test_keys=tuple(sorted(test_keys))
    )
    validate_membership(all_keys, membership.train_keys, membership.test_keys)

    expected_membership = generate_membership(row_keys, adverse_target)
    if membership != expected_membership:
        raise SplitContractError(
            "locked test membership differs from deterministic generation"
        )
    expected_counts = {
        "train": len(membership.train_keys),
        "test": len(membership.test_keys),
    }
    if contract.get("partition_counts") != expected_counts:
        raise SplitContractError("partition counts do not match membership")
    expected_class_counts = {
        "train": _class_counts(membership.train_keys, row_keys, adverse_target),
        "test": _class_counts(membership.test_keys, row_keys, adverse_target),
    }
    if contract.get("class_counts") != expected_class_counts:
        raise SplitContractError("class counts do not match membership")
    expected_checksum = membership_checksum(membership)
    if contract.get("membership_checksum") != expected_checksum:
        raise SplitContractError(
            "membership checksum does not match canonical membership"
        )
    return membership
