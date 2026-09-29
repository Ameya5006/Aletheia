from __future__ import annotations

import hashlib
import io
import zipfile
from dataclasses import replace
from pathlib import Path

import pytest

from aletheia.config import load_dataset_contract, load_feature_policy
from aletheia.contracts import DatasetContract, FeaturePolicy


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
