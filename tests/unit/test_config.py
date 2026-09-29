from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from aletheia.config import (
    load_dataset_contract,
    load_feature_policy,
    validate_feature_policy,
)
from aletheia.contracts import ConfigurationError


def test_repository_contracts_load_and_agree() -> None:
    dataset = load_dataset_contract()
    policy = load_feature_policy(dataset=dataset)

    assert dataset.raw_sha256 == (
        "5f363343f356ca38a0236baab849e472846399b2176ccc5bd686483dd8a7562f"
    )
    assert dataset.row_count == 1000
    assert dataset.categorical_domains["verw"] == frozenset(range(11))
    assert set(policy.raw_role_fields) == set(dataset.columns)


def test_invalid_toml_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.toml"
    path.write_text("[broken", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="cannot load configuration"):
        load_dataset_contract(path)


def test_overlapping_policy_is_rejected(feature_policy) -> None:
    invalid = replace(
        feature_policy,
        audit_only=feature_policy.audit_only + (feature_policy.prediction[0],),
    )

    with pytest.raises(ConfigurationError, match="overlaps"):
        validate_feature_policy(invalid)
