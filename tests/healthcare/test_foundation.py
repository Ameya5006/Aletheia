"""Offline tests of the healthcare contract and source-bound foundation."""

from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

import pandas as pd
import pytest

from aletheia.domains.healthcare.foundation import (
    Contracts,
    HealthcareDataError,
    acquire,
    build_split_lock,
    cohort,
    extract,
    feature_views,
    load_contracts,
    load_raw,
    partition,
    verify_split_lock,
    write_split_lock,
)


@pytest.fixture
def sample(tmp_path: Path) -> tuple[Contracts, Path, Path]:
    source = load_contracts()
    contracts = Contracts(
        *[
            copy.deepcopy(part)
            for part in (source.dataset, source.features, source.split)
        ]
    )
    columns = contracts.dataset["schema"]["columns"]
    rows = []
    for index, target in enumerate(("<30", "NO", ">30", "<30", "NO", "<30"), 1):
        row = dict.fromkeys(columns, "No")
        for column in contracts.features["semantic_types"]["quantitative"]:
            row[column] = "0"
        row.update(
            encounter_id=str(index),
            patient_nbr=str((index + 1) // 2),
            readmitted=target,
            discharge_disposition_id="1",
            admission_type_id="1",
            admission_source_id="1",
            max_glu_serum="None",
            A1Cresult="None",
            race="?" if index == 1 else "Caucasian",
            time_in_hospital="2",
        )
        rows.append(row)
    content = io.StringIO(newline="")
    writer = csv.DictWriter(content, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
    raw_bytes = content.getvalue().encode()
    mapping_bytes = b"code,description\n1,home\n"
    archive = tmp_path / "source.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("diabetic_data.csv", raw_bytes)
        output.writestr("IDS_mapping.csv", mapping_bytes)
    identity = contracts.dataset["identity"]
    for kind, payload in (
        ("archive", archive.read_bytes()),
        ("raw", raw_bytes),
        ("mapping", mapping_bytes),
    ):
        identity[f"{kind}_size"] = len(payload)
        identity[f"{kind}_sha256"] = hashlib.sha256(payload).hexdigest()
    identity["raw_rows"] = 6
    contracts.dataset["target"]["raw_counts"] = {"<30": 3, "NO": 2, ">30": 1}
    contracts.dataset["cohort"].update(
        expected_rows=6, expected_positive=3, expected_patients=3
    )
    return contracts, archive, tmp_path / "extracted"


def test_official_identity_and_default_deny_roles() -> None:
    contracts = load_contracts()
    assert contracts.dataset["identity"]["uci_id"] == 296
    assert contracts.dataset["identity"]["doi"] == "10.24432/C5230J"
    assert contracts.dataset["identity"]["licence"] == "CC BY 4.0"
    roles = contracts.features["roles"]
    assert set(roles["prediction"]).isdisjoint(
        {
            "encounter_id",
            "patient_nbr",
            "race",
            "gender",
            "age",
            "discharge_disposition_id",
        }
    )
    assert set(roles["audit_only"]) == {"race", "gender", "age"}
    assert set(roles["excluded"]) >= {"discharge_disposition_id", "diag_1", "weight"}


def test_configuration_mismatch_refused(tmp_path: Path) -> None:
    for source_name, old, new in (
        ("dataset", 'doi = "10.24432/C5230J"', 'doi = "wrong"'),
        ("features", '"patient_nbr", "row_key"', '"row_key"'),
        ("split", "seed = 42", "seed = 43"),
    ):
        paths = [
            Path("configs/datasets/healthcare_uci296_v1.toml"),
            Path("configs/features/healthcare_uci296_v1.toml"),
            Path("configs/splits/healthcare_uci296_v1.toml"),
        ]
        position = {"dataset": 0, "features": 1, "split": 2}[source_name]
        replacement = tmp_path / f"{source_name}.toml"
        replacement.write_text(
            paths[position].read_text().replace(old, new), encoding="utf-8"
        )
        paths[position] = replacement
        with pytest.raises(HealthcareDataError):
            load_contracts(*paths)


def test_checksum_and_extraction_refusal(sample: tuple[Contracts, Path, Path]) -> None:
    contracts, archive, destination = sample
    raw, mapping = extract(contracts, archive, destination)
    assert raw.exists() and mapping.exists()
    archive.write_bytes(archive.read_bytes() + b"tamper")
    with pytest.raises(HealthcareDataError, match="mismatch"):
        extract(contracts, archive, destination)


def test_synthetic_end_to_end_and_lock(
    sample: tuple[Contracts, Path, Path], tmp_path: Path
) -> None:
    contracts, archive, destination = sample
    raw, _ = extract(contracts, archive, destination)
    frame = cohort(contracts, load_raw(contracts, raw))
    assert frame["readmitted_30d"].tolist() == [1, 0, 0, 1, 0, 1]
    assert frame["race"].isna().sum() == 1
    assert frame["patient_nbr"].duplicated().sum() == 3
    predictors, audit = feature_views(contracts, frame)
    assert "patient_nbr" not in predictors and "encounter_id" not in predictors
    assert list(audit) == ["race", "gender", "age"]
    lock = build_split_lock(contracts, frame)
    path = tmp_path / "lock.json"
    write_split_lock(lock, path)
    assert verify_split_lock(contracts, frame, path) == lock
    train, test = partition(contracts, frame, path)
    assert len(train) + len(test) == 6
    assert not set(train["patient_nbr"]) & set(test["patient_nbr"])
    assert not set(train["row_key"]) & set(test["row_key"])
    assert (
        build_split_lock(contracts, frame)["membership_sha256"]
        == lock["membership_sha256"]
    )
    tampered = json.loads(path.read_text())
    tampered["dataset_sha256"] = "0" * 64
    path.write_text(json.dumps(tampered))
    with pytest.raises(HealthcareDataError, match="split lock"):
        partition(contracts, frame, path)


def test_raw_schema_and_key_refusal(sample: tuple[Contracts, Path, Path]) -> None:
    contracts, archive, destination = sample
    raw, _ = extract(contracts, archive, destination)
    altered = copy.deepcopy(contracts)
    altered.dataset["schema"]["columns"][0:2] = ["patient_nbr", "encounter_id"]
    with pytest.raises(HealthcareDataError, match="header/order"):
        load_raw(altered, raw)
    frame = load_raw(contracts, raw)
    frame.loc[1, "encounter_id"] = frame.loc[0, "encounter_id"]
    assert not frame["encounter_id"].is_unique


def test_duplicate_encounter_and_invalid_category_refused(
    sample: tuple[Contracts, Path, Path],
) -> None:
    contracts, archive, destination = sample
    raw, _ = extract(contracts, archive, destination)
    original = raw.read_bytes()
    for column, value, error in (
        ("encounter_id", "1", "encounter key"),
        ("max_glu_serum", "impossible", "invalid categorical"),
    ):
        reader = list(csv.DictReader(io.StringIO(original.decode())))
        reader[1][column] = value
        output = io.StringIO(newline="")
        writer = csv.DictWriter(
            output, fieldnames=contracts.dataset["schema"]["columns"]
        )
        writer.writeheader()
        writer.writerows(reader)
        payload = output.getvalue().encode()
        raw.write_bytes(payload)
        altered = copy.deepcopy(contracts)
        altered.dataset["identity"]["raw_size"] = len(payload)
        altered.dataset["identity"]["raw_sha256"] = hashlib.sha256(payload).hexdigest()
        with pytest.raises(HealthcareDataError, match=error):
            load_raw(altered, raw)


def test_archive_extra_member_refused(sample: tuple[Contracts, Path, Path]) -> None:
    contracts, archive, destination = sample
    with zipfile.ZipFile(archive, "a") as output:
        output.writestr("../unexpected.csv", b"bad")
    altered = copy.deepcopy(contracts)
    payload = archive.read_bytes()
    altered.dataset["identity"]["archive_size"] = len(payload)
    altered.dataset["identity"]["archive_sha256"] = hashlib.sha256(payload).hexdigest()
    with pytest.raises(HealthcareDataError, match="two flat official files"):
        extract(altered, archive, destination)


def test_cohort_excludes_every_frozen_death_hospice_code() -> None:
    contracts = load_contracts()
    excluded = contracts.dataset["cohort"]["excluded_discharge_codes"]
    assert set(excluded) == {"11", "13", "14", "19", "20", "21"}
    frame = pd.DataFrame(
        {
            "row_key": [f"case-{index}" for index in range(8)],
            "patient_nbr": [str(index) for index in range(8)],
            "discharge_disposition_id": [*excluded, "1", "2"],
            "readmitted_30d": [0, 1, 0, 1, 0, 1, 1, 0],
        }
    )
    synthetic = copy.deepcopy(contracts)
    synthetic.dataset["cohort"].update(
        expected_rows=2, expected_positive=1, expected_patients=2
    )
    result = cohort(synthetic, frame)
    assert result["row_key"].tolist() == ["case-6", "case-7"]
    assert result["discharge_disposition_id"].tolist() == ["1", "2"]


def test_existing_split_lock_cannot_be_overwritten(tmp_path: Path) -> None:
    path = tmp_path / "split.lock.json"
    write_split_lock({"version": "original"}, path)
    original = path.read_bytes()
    with pytest.raises(HealthcareDataError, match="already exists"):
        write_split_lock({"version": "replacement"}, path)
    assert path.read_bytes() == original


@pytest.mark.parametrize("failure", ["redirect", "byte_identity"])
def test_acquire_refuses_bad_response_and_cleans_partial(
    sample: tuple[Contracts, Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    contracts, source_archive, _ = sample
    expected_url = contracts.dataset["identity"]["archive_url"]
    payload = source_archive.read_bytes()
    if failure == "byte_identity":
        payload = bytes([payload[0] ^ 1]) + payload[1:]

    class FakeResponse(io.BytesIO):
        def geturl(self) -> str:
            return (
                expected_url
                if failure == "byte_identity"
                else "https://other.example/archive.zip"
            )

    def fake_urlopen(url: str, timeout: int) -> FakeResponse:
        assert url == expected_url
        assert timeout == 60
        return FakeResponse(payload)

    monkeypatch.setattr(
        "aletheia.domains.healthcare.foundation.urllib.request.urlopen",
        fake_urlopen,
    )
    destination = tmp_path / "downloaded.zip"
    partial = destination.with_suffix(".zip.partial")
    with pytest.raises(HealthcareDataError, match="archive acquisition failed"):
        acquire(contracts, destination)
    assert not destination.exists()
    assert not partial.exists()
