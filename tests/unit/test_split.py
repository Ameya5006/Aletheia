from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pandas as pd
import pytest

from aletheia.contracts import SplitContractError
from aletheia.data.split import (
    SplitMembership,
    canonical_membership_serialization,
    create_split_contract,
    generate_membership,
    load_split_contract,
    membership_checksum,
    validate_membership,
    verify_split_contract,
)

DATASET_SHA = "a" * 64
POLICY_VERSION = "1.0"
MAPPING_ID = "kredit-0-is-adverse-v1"


@pytest.fixture
def split_inputs():
    keys = pd.Series([f"sgc-{index:04d}" for index in range(1, 1001)])
    target = pd.Series([1] * 300 + [0] * 700, name="adverse_event")
    membership = generate_membership(keys, target)
    contract = create_split_contract(
        membership,
        keys,
        target,
        dataset_sha256=DATASET_SHA,
        feature_policy_version=POLICY_VERSION,
        target_mapping_identifier=MAPPING_ID,
    )
    return keys, target, membership, contract


def _verify(contract, keys, target):
    return verify_split_contract(
        contract,
        keys,
        target,
        dataset_sha256=DATASET_SHA,
        feature_policy_version=POLICY_VERSION,
        target_mapping_identifier=MAPPING_ID,
    )


def test_canonical_membership_serialization_is_exact() -> None:
    membership = SplitMembership(
        train_keys=("sgc-0002", "sgc-0001"), test_keys=("sgc-0004", "sgc-0003")
    )

    assert canonical_membership_serialization(membership) == (
        b'{"test_row_keys":["sgc-0003","sgc-0004"],'
        b'"train_row_keys":["sgc-0001","sgc-0002"]}'
    )
    assert len(membership_checksum(membership)) == 64


def test_repository_split_lock_has_exact_checksum_and_compact_schema() -> None:
    contract = load_split_contract(Path("configs/splits/south_german_credit_v1.json"))
    assert contract["membership_checksum"] == (
        "af26b6036c6958a2dec48362fb1bfb075fca2ad7e482ed48ee7a49d7ec6d994b"
    )
    assert set(contract) == {
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
    assert len(contract["test_row_keys"]) == 200


def test_same_seed_membership_is_equal_and_has_exact_counts(split_inputs) -> None:
    keys, target, first, contract = split_inputs
    second = generate_membership(keys, target)

    assert first == second
    assert len(first.train_keys) == 800
    assert len(first.test_keys) == 200
    assert set(first.train_keys).isdisjoint(first.test_keys)
    assert set(first.train_keys) | set(first.test_keys) == set(keys)
    assert contract["class_counts"] == {
        "train": {"0": 560, "1": 240},
        "test": {"0": 140, "1": 60},
    }


def test_valid_locked_contract_verifies(split_inputs) -> None:
    keys, target, membership, contract = split_inputs

    assert _verify(contract, keys, target) == membership


def test_changed_dataset_hash_is_rejected(split_inputs) -> None:
    keys, target, _membership, contract = split_inputs

    with pytest.raises(SplitContractError, match="dataset_sha256 mismatch"):
        verify_split_contract(
            contract,
            keys,
            target,
            dataset_sha256="b" * 64,
            feature_policy_version=POLICY_VERSION,
            target_mapping_identifier=MAPPING_ID,
        )


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "unknown"])
def test_invalid_test_keys_are_rejected(split_inputs, mutation: str) -> None:
    keys, target, _membership, original = split_inputs
    contract = deepcopy(original)
    test_keys = contract["test_row_keys"]
    if mutation == "missing":
        test_keys.pop()
        expected = "deterministic generation|partition counts"
    elif mutation == "duplicate":
        test_keys[-1] = test_keys[0]
        expected = "duplicate key"
    else:
        test_keys[-1] = "sgc-9999"
        expected = "unknown key"

    with pytest.raises(SplitContractError, match=expected):
        _verify(contract, keys, target)


def test_changed_generated_membership_is_detected(split_inputs) -> None:
    keys, target, membership, original = split_inputs
    test_keys = list(membership.test_keys)
    train_keys = list(membership.train_keys)
    target_by_key = dict(zip(keys, target, strict=True))
    test_position, train_position = next(
        (test_index, train_index)
        for test_index, test_key in enumerate(test_keys)
        for train_index, train_key in enumerate(train_keys)
        if target_by_key[test_key] == target_by_key[train_key]
    )
    test_keys[test_position], train_keys[train_position] = (
        train_keys[train_position],
        test_keys[test_position],
    )
    changed = SplitMembership(tuple(sorted(train_keys)), tuple(sorted(test_keys)))
    contract = deepcopy(original)
    contract["test_row_keys"] = list(changed.test_keys)
    contract["membership_checksum"] = membership_checksum(changed)

    with pytest.raises(SplitContractError, match="differs from deterministic"):
        _verify(contract, keys, target)


def test_changed_membership_checksum_is_rejected(split_inputs) -> None:
    keys, target, _membership, original = split_inputs
    contract = deepcopy(original)
    contract["membership_checksum"] = "0" * 64

    with pytest.raises(SplitContractError, match="checksum"):
        _verify(contract, keys, target)


def test_changed_class_counts_are_rejected(split_inputs) -> None:
    keys, target, _membership, original = split_inputs
    contract = deepcopy(original)
    contract["class_counts"]["test"]["1"] = 59

    with pytest.raises(SplitContractError, match="class counts"):
        _verify(contract, keys, target)


@pytest.mark.parametrize(
    ("train", "test", "message"),
    [
        (("a", "b"), ("b", "c"), "overlap"),
        (("a",), ("b",), "does not cover"),
        (("a", "a", "b"), ("c",), "duplicate"),
    ],
)
def test_membership_boundary_rejects_overlap_incomplete_and_duplicates(
    train, test, message
) -> None:
    with pytest.raises(SplitContractError, match=message):
        validate_membership(("a", "b", "c"), train, test)
