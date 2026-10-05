"""Verified UCI 296 acquisition, fail-closed data views, and patient split."""

from __future__ import annotations

import csv
import hashlib
import json
import tomllib
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

DATASET_CONFIG = Path("configs/datasets/healthcare_uci296_v1.toml")
FEATURE_CONFIG = Path("configs/features/healthcare_uci296_v1.toml")
SPLIT_CONFIG = Path("configs/splits/healthcare_uci296_v1.toml")
SPLIT_LOCK = Path("configs/splits/healthcare_uci296_v1.lock.json")
ROLES = (
    "prediction",
    "audit_only",
    "excluded",
    "raw_target",
    "derived_target",
    "metadata",
)


class HealthcareDataError(ValueError):
    """A healthcare source, policy, or lock is incompatible with its contract."""


@dataclass(frozen=True)
class Contracts:
    dataset: dict[str, Any]
    features: dict[str, Any]
    split: dict[str, Any]


def _toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as stream:
            return tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise HealthcareDataError(f"cannot load {path}: {exc}") from exc


def load_contracts(
    dataset_path: Path = DATASET_CONFIG,
    features_path: Path = FEATURE_CONFIG,
    split_path: Path = SPLIT_CONFIG,
) -> Contracts:
    """Check cross-references and exhaustive roles before touching any data."""
    dataset, features, split = map(_toml, (dataset_path, features_path, split_path))
    try:
        identity, schema, target = (
            dataset["identity"],
            dataset["schema"],
            dataset["target"],
        )
        policy, roles = features["policy"], features["roles"]
        splitter = split["split"]
        columns = schema["columns"]
        if (
            identity["identifier"],
            identity["uci_id"],
            identity["doi"],
            identity["licence"],
        ) != ("uci-diabetes-296-v1", 296, "10.24432/C5230J", "CC BY 4.0"):
            raise HealthcareDataError("official UCI identity mismatch")
        if not identity["archive_url"].startswith(
            "https://archive.ics.uci.edu/static/public/296/"
        ):
            raise HealthcareDataError("archive URL must use the official UCI 296 host")
        for name in ("archive", "raw", "mapping"):
            digest = identity[f"{name}_sha256"]
            if len(digest) != 64 or any(
                char not in "0123456789abcdef" for char in digest
            ):
                raise HealthcareDataError(f"invalid {name} SHA-256")
            if (
                type(identity[f"{name}_size"]) is not int
                or identity[f"{name}_size"] <= 0
            ):
                raise HealthcareDataError(f"invalid {name} size")
        if (
            len(columns) != 50
            or len(set(columns)) != 50
            or columns[0] != "encounter_id"
            or columns[-1] != "readmitted"
        ):
            raise HealthcareDataError("invalid raw schema")
        if (
            target["raw"] != "readmitted"
            or target["derived"] != "readmitted_30d"
            or target["positive_raw"] != "<30"
            or set(target["negative_raw"]) != {">30", "NO"}
        ):
            raise HealthcareDataError("invalid target truth table")
        if (
            set(target["raw_counts"]) != {"<30", ">30", "NO"}
            or sum(target["raw_counts"].values()) != identity["raw_rows"]
        ):
            raise HealthcareDataError("target counts conflict with raw rows")
        if any(
            name not in roles
            or not isinstance(roles[name], list)
            or len(roles[name]) != len(set(roles[name]))
            for name in ROLES
        ):
            raise HealthcareDataError("missing or duplicated feature roles")
        all_roles = sum((roles[name] for name in ROLES), [])
        if len(all_roles) != len(set(all_roles)) or set(all_roles) != set(columns) | {
            target["derived"],
            "row_key",
        }:
            raise HealthcareDataError("feature roles must be exhaustive and disjoint")
        if (
            roles["raw_target"] != [target["raw"]]
            or roles["derived_target"] != [target["derived"]]
            or set(roles["metadata"]) != {"encounter_id", "patient_nbr", "row_key"}
        ):
            raise HealthcareDataError("target or identifier role mismatch")
        if set(roles["prediction"]) & {
            "race",
            "gender",
            "age",
            "discharge_disposition_id",
            "encounter_id",
            "patient_nbr",
        }:
            raise HealthcareDataError("sensitive, leakage, or ID field in prediction")
        if (
            set(roles["audit_only"]) != {"race", "gender", "age"}
            or "discharge_disposition_id" not in roles["excluded"]
        ):
            raise HealthcareDataError("sensitive or discharge policy mismatch")
        semantics = features["semantic_types"]
        if set(semantics["quantitative"] + semantics["categorical"]) != set(
            roles["prediction"]
        ) or set(semantics["audit_categorical"]) != set(roles["audit_only"]):
            raise HealthcareDataError("semantic types do not cover allowed predictors")
        if (
            policy["dataset_identifier"] != identity["identifier"]
            or splitter["dataset_identifier"] != identity["identifier"]
            or splitter["feature_policy_version"] != policy["version"]
            or splitter["target_mapping_version"] != target["mapping_version"]
        ):
            raise HealthcareDataError(
                "dataset, policy, split, or target version mismatch"
            )
        if (
            splitter["method"] != "patient-sha256-threshold"
            or splitter["seed"] != 42
            or splitter["test_fraction"] != 0.2
            or splitter["positive_class"] != 1
        ):
            raise HealthcareDataError("split protocol mismatch")
        if schema["missing_token"] != "?" or not set(schema["missing_columns"]) <= set(
            columns
        ) - set(roles["metadata"]):
            raise HealthcareDataError("invalid missing-token policy")
    except (KeyError, TypeError, ValueError) as exc:
        raise HealthcareDataError(f"invalid healthcare configuration: {exc}") from exc
    return Contracts(dataset, features, split)


def _check_file(path: Path, size: int, digest: str) -> None:
    try:
        actual_size = path.stat().st_size
        with path.open("rb") as stream:
            actual_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    except OSError as exc:
        raise HealthcareDataError(f"cannot read {path}: {exc}") from exc
    if actual_size != size or actual_hash != digest:
        raise HealthcareDataError(f"checksum/size mismatch: {path}")


def acquire(contracts: Contracts, destination: Path) -> Path:
    """Download over HTTPS to a temporary file, verify, then publish locally."""
    identity = contracts.dataset["identity"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        _check_file(destination, identity["archive_size"], identity["archive_sha256"])
        return destination
    temporary = destination.with_suffix(destination.suffix + ".partial")
    try:
        with (
            urllib.request.urlopen(identity["archive_url"], timeout=60) as response,
            temporary.open("wb") as output,
        ):
            if response.geturl() != identity["archive_url"]:
                raise HealthcareDataError("unexpected archive redirect")
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
                if output.tell() > identity["archive_size"]:
                    raise HealthcareDataError("archive exceeds contracted size")
        _check_file(temporary, identity["archive_size"], identity["archive_sha256"])
        temporary.replace(destination)
    except (OSError, ValueError) as exc:
        temporary.unlink(missing_ok=True)
        raise HealthcareDataError(f"archive acquisition failed: {exc}") from exc
    return destination


def extract(
    contracts: Contracts, archive: Path, destination: Path
) -> tuple[Path, Path]:
    """Accept exactly the contracted flat members; never trust archive paths."""
    identity = contracts.dataset["identity"]
    _check_file(archive, identity["archive_size"], identity["archive_sha256"])
    names = (identity["raw_member"], identity["mapping_member"])
    try:
        with zipfile.ZipFile(archive) as source:
            if (
                set(source.namelist()) != set(names)
                or len(source.namelist()) != 2
                or any(Path(name).name != name for name in names)
            ):
                raise HealthcareDataError(
                    "archive must contain exactly the two flat official files"
                )
            payloads = [source.read(name) for name in names]
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise HealthcareDataError(f"invalid archive: {exc}") from exc
    for kind, payload in zip(("raw", "mapping"), payloads, strict=True):
        if (
            len(payload) != identity[f"{kind}_size"]
            or hashlib.sha256(payload).hexdigest() != identity[f"{kind}_sha256"]
        ):
            raise HealthcareDataError(f"{kind} member checksum mismatch")
    destination.mkdir(parents=True, exist_ok=True)
    paths = tuple(destination / name for name in names)
    for path, payload in zip(paths, payloads, strict=True):
        if path.exists():
            kind = "raw" if path == paths[0] else "mapping"
            _check_file(path, identity[f"{kind}_size"], identity[f"{kind}_sha256"])
        else:
            path.write_bytes(payload)
    return paths


def load_raw(contracts: Contracts, path: Path) -> pd.DataFrame:
    """Enforce byte identity, CSV column order, source counts, and unique keys."""
    identity, schema, target = (
        contracts.dataset[name] for name in ("identity", "schema", "target")
    )
    _check_file(path, identity["raw_size"], identity["raw_sha256"])
    try:
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.reader(stream)
            header = next(reader)
            if header != schema["columns"]:
                raise HealthcareDataError("raw CSV header/order mismatch")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error, StopIteration) as exc:
        raise HealthcareDataError(f"cannot parse raw CSV: {exc}") from exc
    if len(rows) != identity["raw_rows"] or any(
        len(row) != len(header) for row in rows
    ):
        raise HealthcareDataError("raw CSV row count or width mismatch")
    frame = pd.DataFrame(rows, columns=header, dtype="string")
    if (
        frame["encounter_id"].isna().any()
        or frame["encounter_id"].eq("").any()
        or not frame["encounter_id"].is_unique
    ):
        raise HealthcareDataError("encounter key must be present and unique")
    if (
        frame["patient_nbr"].isna().any()
        or frame["patient_nbr"].eq("").any()
        or frame["patient_nbr"].eq("?").any()
    ):
        raise HealthcareDataError("patient grouping key is missing")
    if any(
        not frame[key].str.fullmatch(r"\d+").all()
        for key in ("encounter_id", "patient_nbr")
    ):
        raise HealthcareDataError("identifier format mismatch")
    if frame["readmitted"].value_counts().to_dict() != target["raw_counts"]:
        raise HealthcareDataError("raw target counts mismatch")
    for column in header:
        if column not in schema["missing_columns"] and frame[column].eq("?").any():
            raise HealthcareDataError(f"unexpected missing token in {column}")
        if frame[column].eq("").any():
            raise HealthcareDataError(f"empty token in {column}")
    frame["row_key"] = "uci296-" + frame["encounter_id"]
    for column in schema["missing_columns"]:
        frame[column] = frame[column].replace("?", pd.NA)
    for column in contracts.features["semantic_types"]["quantitative"]:
        if not frame[column].str.fullmatch(r"\d+").all():
            raise HealthcareDataError(f"nonnegative integer required in {column}")
    for column in (
        "admission_type_id",
        "admission_source_id",
        "discharge_disposition_id",
    ):
        if not frame[column].str.fullmatch(r"\d+").all():
            raise HealthcareDataError(
                f"numeric administrative code required in {column}"
            )
    categorical_domains = {
        "max_glu_serum": {"None", "Norm", ">200", ">300"},
        "A1Cresult": {"None", "Norm", ">7", ">8"},
        "diabetesMed": {"Yes", "No"},
    }
    for column, allowed in categorical_domains.items():
        if not set(frame[column].unique()) <= allowed:
            raise HealthcareDataError(f"invalid categorical value in {column}")
    frame[target["derived"]] = (
        frame[target["raw"]].eq(target["positive_raw"]).astype("int8")
    )
    return frame


def cohort(contracts: Contracts, frame: pd.DataFrame) -> pd.DataFrame:
    rules = contracts.dataset["cohort"]
    result = frame.loc[
        ~frame["discharge_disposition_id"].isin(rules["excluded_discharge_codes"])
    ].copy()
    if (
        len(result) != rules["expected_rows"]
        or int(result["readmitted_30d"].sum()) != rules["expected_positive"]
        or result["patient_nbr"].nunique() != rules["expected_patients"]
    ):
        raise HealthcareDataError("cohort counts conflict with frozen contract")
    return result


def feature_views(
    contracts: Contracts, frame: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    roles = contracts.features["roles"]
    return frame.loc[:, roles["prediction"]].copy(), frame.loc[
        :, roles["audit_only"]
    ].copy()


def _membership(frame: pd.DataFrame, seed: int) -> dict[str, str]:
    patients = sorted(frame["patient_nbr"].astype(str).unique())
    return {
        patient: (
            "test"
            if int.from_bytes(
                hashlib.sha256(f"{seed}:{patient}".encode()).digest(), "big"
            )
            < 2**256 // 5
            else "train"
        )
        for patient in patients
    }


def build_split_lock(contracts: Contracts, frame: pd.DataFrame) -> dict[str, Any]:
    """Freeze deterministic patient membership and descriptive class counts."""
    splitter = contracts.split["split"]
    membership = _membership(frame, splitter["seed"])
    partitions = frame["patient_nbr"].astype(str).map(membership)
    counts = {
        name: {
            "encounters": int((partitions == name).sum()),
            "patients": sum(part == name for part in membership.values()),
            "class_0": int(
                ((partitions == name) & frame["readmitted_30d"].eq(0)).sum()
            ),
            "class_1": int(
                ((partitions == name) & frame["readmitted_30d"].eq(1)).sum()
            ),
        }
        for name in ("train", "test")
    }
    if any(
        counts[name]["class_0"] == 0 or counts[name]["class_1"] == 0 for name in counts
    ):
        raise HealthcareDataError("both classes required in each partition")
    canonical = json.dumps(membership, sort_keys=True, separators=(",", ":"))
    return {
        "version": splitter["version"],
        "dataset_identifier": splitter["dataset_identifier"],
        "dataset_sha256": contracts.dataset["identity"]["raw_sha256"],
        "feature_policy_version": splitter["feature_policy_version"],
        "target_mapping_version": splitter["target_mapping_version"],
        "seed": splitter["seed"],
        "method": splitter["method"],
        "membership_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "counts": counts,
    }


def write_split_lock(lock: dict[str, Any], path: Path) -> None:
    if path.exists():
        raise HealthcareDataError("split lock already exists; verify it instead")
    path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_split_lock(
    contracts: Contracts, frame: pd.DataFrame, path: Path
) -> dict[str, Any]:
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise HealthcareDataError(f"cannot read split lock: {exc}") from exc
    expected = build_split_lock(contracts, frame)
    if saved != expected:
        raise HealthcareDataError("split lock identity, membership, or counts mismatch")
    return saved


def partition(
    contracts: Contracts, frame: pd.DataFrame, lock_path: Path
) -> tuple[pd.DataFrame, pd.DataFrame]:
    verify_split_lock(contracts, frame, lock_path)
    membership = _membership(frame, contracts.split["split"]["seed"])
    test_mask = frame["patient_nbr"].astype(str).map(membership).eq("test")
    train, test = frame.loc[~test_mask].copy(), frame.loc[test_mask].copy()
    if set(train["patient_nbr"]) & set(test["patient_nbr"]) or set(
        train["row_key"]
    ) & set(test["row_key"]):
        raise HealthcareDataError("patient or encounter overlaps partitions")
    return train, test
