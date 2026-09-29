from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest
from conftest import contract_for_raw

from aletheia.contracts import SchemaError
from aletheia.data.load import load_raw_data
from aletheia.data.validate import validate_raw_data


def _write_and_load(tmp_path: Path, content: bytes, contract):
    path = tmp_path / contract.raw_filename
    path.write_bytes(content)
    return load_raw_data(path, contract)


def _contract_matching(content: bytes, contract):
    return replace(
        contract,
        raw_size=len(content),
        raw_sha256=hashlib.sha256(content).hexdigest(),
    )


def test_valid_synthetic_contract_fixture(
    raw_file, dataset_contract, feature_policy
) -> None:
    frame = load_raw_data(raw_file, dataset_contract)

    assert validate_raw_data(frame, dataset_contract, feature_policy) is frame
    assert frame.shape == (10, 22)
    assert frame["row_key"].iloc[0] == "sgc-0001"
    assert frame["row_key"].iloc[-1] == "sgc-0010"
    assert frame["row_key"].is_unique


def test_row_keys_are_repeatable(raw_file, dataset_contract) -> None:
    first = load_raw_data(raw_file, dataset_contract)
    second = load_raw_data(raw_file, dataset_contract)

    assert first["row_key"].tolist() == second["row_key"].tolist()


@pytest.mark.parametrize("mode", ["wrong_name", "wrong_order"])
def test_wrong_header_or_order_is_rejected(
    tmp_path: Path, raw_bytes: bytes, dataset_contract, mode: str
) -> None:
    lines = raw_bytes.decode("ascii").splitlines()
    header = lines[0].split()
    if mode == "wrong_name":
        header[0] = "unknown"
    else:
        header[0], header[1] = header[1], header[0]
    content = (" ".join(header) + "\n" + "\n".join(lines[1:]) + "\n").encode()
    contract = _contract_matching(content, dataset_contract)

    with pytest.raises(SchemaError, match="header/order mismatch"):
        _write_and_load(tmp_path, content, contract)


def test_malformed_row_is_rejected(
    tmp_path: Path, raw_bytes: bytes, dataset_contract
) -> None:
    lines = raw_bytes.decode("ascii").splitlines()
    lines[1] = " ".join(lines[1].split()[:-1])
    content = ("\n".join(lines) + "\n").encode()
    contract = _contract_matching(content, dataset_contract)

    with pytest.raises(SchemaError, match="malformed row sgc-0001"):
        _write_and_load(tmp_path, content, contract)


def test_non_integer_token_is_rejected(
    tmp_path: Path, raw_bytes: bytes, dataset_contract
) -> None:
    lines = raw_bytes.decode("ascii").splitlines()
    tokens = lines[1].split()
    tokens[1] = "6.5"
    lines[1] = " ".join(tokens)
    content = ("\n".join(lines) + "\n").encode()
    contract = _contract_matching(content, dataset_contract)

    with pytest.raises(SchemaError, match="non-integer token"):
        _write_and_load(tmp_path, content, contract)


def test_missing_value_is_rejected(raw_file, dataset_contract, feature_policy) -> None:
    frame = load_raw_data(raw_file, dataset_contract)
    frame.loc[0, "hoehe"] = pd.NA

    with pytest.raises(SchemaError, match="missing value"):
        validate_raw_data(frame, dataset_contract, feature_policy)


def test_incorrect_row_count_is_rejected(
    tmp_path: Path, raw_bytes: bytes, dataset_contract
) -> None:
    lines = raw_bytes.decode("ascii").splitlines()[:-1]
    content = ("\n".join(lines) + "\n").encode()
    contract = _contract_matching(content, dataset_contract)

    with pytest.raises(SchemaError, match="row-count mismatch"):
        _write_and_load(tmp_path, content, contract)


def test_undocumented_category_is_rejected(
    raw_file, dataset_contract, feature_policy
) -> None:
    frame = load_raw_data(raw_file, dataset_contract)
    frame.loc[0, "laufkont"] = 99

    with pytest.raises(SchemaError, match="undocumented category.*laufkont"):
        validate_raw_data(frame, dataset_contract, feature_policy)


def test_documented_unobserved_purpose_code_seven_is_accepted(
    raw_file, dataset_contract, feature_policy
) -> None:
    frame = load_raw_data(raw_file, dataset_contract)
    frame.loc[0, "verw"] = 7

    assert validate_raw_data(frame, dataset_contract, feature_policy) is frame


def test_invalid_target_is_rejected(raw_file, dataset_contract, feature_policy) -> None:
    frame = load_raw_data(raw_file, dataset_contract)
    frame.loc[0, "kredit"] = 2

    with pytest.raises(SchemaError, match="invalid raw target"):
        validate_raw_data(frame, dataset_contract, feature_policy)


@pytest.mark.parametrize("predictor_only", [False, True])
def test_duplicate_detection(
    raw_file, dataset_contract, feature_policy, predictor_only: bool
) -> None:
    frame = load_raw_data(raw_file, dataset_contract)
    frame.loc[1, list(dataset_contract.columns)] = frame.loc[
        0, list(dataset_contract.columns)
    ]
    if predictor_only:
        frame.loc[1, "kredit"] = 1 - int(frame.loc[0, "kredit"])
        message = "duplicate predictor-only"
    else:
        message = "duplicate complete"

    with pytest.raises(SchemaError, match=message):
        validate_raw_data(frame, dataset_contract, feature_policy)


def test_contract_helper_counts_rows(raw_bytes: bytes) -> None:
    contract = contract_for_raw(raw_bytes)

    assert contract.row_count == 10
    assert contract.expected_target_counts == {0: 5, 1: 5}
