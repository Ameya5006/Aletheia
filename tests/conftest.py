from __future__ import annotations

import hashlib
import io
import zipfile
from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest

from aletheia.config import (
    load_baseline_experiment_config,
    load_dataset_contract,
    load_feature_policy,
)
from aletheia.contracts import (
    BaselineExperimentConfig,
    DatasetContract,
    FeaturePolicy,
)
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
from aletheia.ml import baseline


@pytest.fixture
def synthetic_baseline_run(tmp_path: Path, monkeypatch):
    """Use real loaders and split verification with temporary synthetic identities."""
    raw = synthetic_raw_bytes(1000)
    dataset = contract_for_raw(raw)
    policy = load_feature_policy(dataset=dataset)
    raw_path = tmp_path / dataset.raw_filename
    raw_path.write_bytes(raw)
    loaded = load_raw_data(raw_path, dataset)
    validate_raw_data(loaded, dataset, policy)
    views = build_feature_views(add_adverse_target(loaded, dataset), policy, dataset)
    row_keys = views.metadata["row_key"]
    target = views.target[dataset.derived_target]
    contract = create_split_contract(
        generate_membership(row_keys, target),
        row_keys,
        target,
        dataset_sha256=dataset.raw_sha256,
        feature_policy_version=policy.version,
        target_mapping_identifier=dataset.target_mapping_identifier,
    )
    split_path = tmp_path / "synthetic_split.json"
    write_split_contract(contract, split_path)
    membership = verify_split_contract(
        load_split_contract(split_path),
        row_keys,
        target,
        dataset_sha256=dataset.raw_sha256,
        feature_policy_version=policy.version,
        target_mapping_identifier=dataset.target_mapping_identifier,
    )
    # Replace identities only; the real experiment loader validates the fixed protocol.
    config_text = Path("configs/experiments/baseline_v1.toml").read_text(
        encoding="utf-8"
    )
    original = load_baseline_experiment_config()
    config_text = (
        config_text.replace(original.dataset_sha256, dataset.raw_sha256)
        .replace(original.split_contract_path, split_path.as_posix())
        .replace(original.split_membership_checksum, contract["membership_checksum"])
    )
    config_path = tmp_path / "synthetic_baseline.toml"
    config_path.write_text(config_text, encoding="utf-8")
    # Only the dataset identity provider is substituted, never data/split/ML logic.
    monkeypatch.setattr(baseline, "load_dataset_contract", lambda: dataset)
    return raw_path, config_path, dataset, policy, membership, views


def synthetic_raw_bytes(row_count: int = 10) -> bytes:
    contract = load_dataset_contract()
    lines = [" ".join(contract.columns)]
    for index in range(row_count):
        values = {
            "laufkont": index % 4 + 1,
            "laufzeit": 6 + index,
            "moral": index % 5,
            "verw": index % 11,
            "hoehe": 1000 + index,
            "sparkont": index % 5 + 1,
            "beszeit": index % 5 + 1,
            "rate": index % 4 + 1,
            "famges": index % 4 + 1,
            "buerge": index % 3 + 1,
            "wohnzeit": index % 4 + 1,
            "verm": index % 4 + 1,
            "alter": 25 + index,
            "weitkred": index % 3 + 1,
            "wohn": index % 3 + 1,
            "bishkred": index % 4 + 1,
            "beruf": index % 4 + 1,
            "pers": index % 2 + 1,
            "telef": index % 2 + 1,
            "gastarb": index % 2 + 1,
            "kredit": index % 2,
        }
        lines.append(" ".join(str(values[column]) for column in contract.columns))
    return ("\n".join(lines) + "\n").encode("ascii")


def zip_bytes(member: str, raw: bytes, extras: dict[str, bytes] | None = None) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_BZIP2) as archive:
        archive.writestr(member, raw)
        for name, content in (extras or {}).items():
            archive.writestr(name, content)
    return stream.getvalue()


def contract_for_raw(raw: bytes, *, filename: str = "fixture.asc") -> DatasetContract:
    base = load_dataset_contract()
    row_count = len(raw.decode("ascii").splitlines()) - 1
    zeros = sum(
        line.split()[-1] == "0" for line in raw.decode("ascii").splitlines()[1:]
    )
    return replace(
        base,
        raw_filename=filename,
        raw_size=len(raw),
        raw_sha256=hashlib.sha256(raw).hexdigest(),
        row_count=row_count,
        expected_target_counts={0: zeros, 1: row_count - zeros},
    )


def contract_for_archive(raw: bytes, archive: bytes) -> DatasetContract:
    return replace(
        contract_for_raw(raw),
        archive_size=len(archive),
        archive_sha256=hashlib.sha256(archive).hexdigest(),
        archive_member="fixture.asc",
    )


@pytest.fixture
def raw_bytes() -> bytes:
    return synthetic_raw_bytes()


@pytest.fixture
def dataset_contract(raw_bytes: bytes) -> DatasetContract:
    return contract_for_raw(raw_bytes)


@pytest.fixture
def feature_policy(dataset_contract: DatasetContract) -> FeaturePolicy:
    return load_feature_policy(dataset=dataset_contract)


@pytest.fixture
def raw_file(tmp_path: Path, raw_bytes: bytes) -> Path:
    path = tmp_path / "fixture.asc"
    path.write_bytes(raw_bytes)
    return path


@pytest.fixture
def baseline_config() -> BaselineExperimentConfig:
    dataset = load_dataset_contract()
    policy = load_feature_policy(dataset=dataset)
    return load_baseline_experiment_config(dataset=dataset, policy=policy)


@pytest.fixture
def baseline_training_data(baseline_config):
    row_count = 800
    values: dict[str, list[int]] = {}
    for offset, feature in enumerate(baseline_config.quantitative_features):
        values[feature] = [100 + offset + index for index in range(row_count)]
    for feature in baseline_config.categorical_features:
        domain = baseline_config.category_domains[feature]
        values[feature] = [domain[index % len(domain)] for index in range(row_count)]
    features = pd.DataFrame(values).loc[
        :,
        [
            "laufkont",
            "laufzeit",
            "moral",
            "verw",
            "hoehe",
            "sparkont",
            "beszeit",
            "rate",
            "buerge",
            "wohnzeit",
            "verm",
            "weitkred",
            "wohn",
            "beruf",
            "pers",
        ],
    ]
    target = pd.Series([1] * 240 + [0] * 560, name="adverse_event")
    keys = pd.Series(
        [f"sgc-{index:04d}" for index in range(1, row_count + 1)],
        name="row_key",
    )
    return features, target, keys
