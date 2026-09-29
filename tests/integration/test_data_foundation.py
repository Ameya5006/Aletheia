from __future__ import annotations

import io
import os
from contextlib import contextmanager
from pathlib import Path

import pytest
from conftest import contract_for_archive, zip_bytes

from aletheia.config import load_dataset_contract, load_feature_policy
from aletheia.data.acquire import acquire_dataset
from aletheia.data.load import load_raw_data
from aletheia.data.roles import build_feature_views
from aletheia.data.split import (
    create_split_contract,
    generate_membership,
    load_split_contract,
    verify_split_contract,
)
from aletheia.data.target import add_adverse_target
from aletheia.data.validate import validate_raw_data


def test_offline_data_foundation_flow(tmp_path: Path, raw_bytes: bytes) -> None:
    archive = zip_bytes("fixture.asc", raw_bytes)
    dataset = contract_for_archive(raw_bytes, archive)
    policy = load_feature_policy(dataset=dataset)

    @contextmanager
    def opener(_url: str):
        yield io.BytesIO(archive)

    path = acquire_dataset(dataset, tmp_path / "raw", opener)
    raw = load_raw_data(path, dataset)
    validate_raw_data(raw, dataset, policy)
    mapped = add_adverse_target(raw, dataset)
    views = build_feature_views(mapped, policy, dataset)
    membership = generate_membership(
        views.metadata["row_key"], views.target[dataset.derived_target]
    )
    contract = create_split_contract(
        membership,
        views.metadata["row_key"],
        views.target[dataset.derived_target],
        dataset_sha256=dataset.raw_sha256,
        feature_policy_version=policy.version,
        target_mapping_identifier=dataset.target_mapping_identifier,
    )

    verified = verify_split_contract(
        contract,
        views.metadata["row_key"],
        views.target[dataset.derived_target],
        dataset_sha256=dataset.raw_sha256,
        feature_policy_version=policy.version,
        target_mapping_identifier=dataset.target_mapping_identifier,
    )
    assert verified == membership
    assert views.model_input().shape == (10, 15)


@pytest.mark.live_data
@pytest.mark.skipif(
    os.environ.get("ALETHEIA_RUN_LIVE_DATA") != "1",
    reason="set ALETHEIA_RUN_LIVE_DATA=1 to authorize official network acquisition",
)
def test_authoritative_data_foundation_end_to_end(tmp_path: Path) -> None:
    dataset = load_dataset_contract()
    policy = load_feature_policy(dataset=dataset)
    path = acquire_dataset(dataset, tmp_path / "raw")
    raw = load_raw_data(path, dataset)
    validate_raw_data(raw, dataset, policy)
    mapped = add_adverse_target(raw, dataset)
    views = build_feature_views(mapped, policy, dataset)
    contract = load_split_contract(Path("configs/splits/south_german_credit_v1.json"))
    membership = verify_split_contract(
        contract,
        views.metadata["row_key"],
        views.target[dataset.derived_target],
        dataset_sha256=dataset.raw_sha256,
        feature_policy_version=policy.version,
        target_mapping_identifier=dataset.target_mapping_identifier,
    )

    assert path.stat().st_size == 47_940
    assert raw["row_key"].iloc[0] == "sgc-0001"
    assert raw["row_key"].iloc[-1] == "sgc-1000"
    assert mapped["adverse_event"].value_counts().to_dict() == {0: 700, 1: 300}
    assert views.model_input().shape == (1000, 15)
    assert len(membership.train_keys) == 800
    assert len(membership.test_keys) == 200
