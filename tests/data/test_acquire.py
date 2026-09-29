from __future__ import annotations

import io
from contextlib import contextmanager
from pathlib import Path

import pytest
from conftest import contract_for_archive, zip_bytes

from aletheia.contracts import AcquisitionError, IntegrityError
from aletheia.data.acquire import acquire_dataset, verify_file_identity


def opener_for(content: bytes):
    @contextmanager
    def opener(_url: str):
        yield io.BytesIO(content)

    return opener


def test_valid_archive_and_raw_hashes_are_published(
    tmp_path: Path, raw_bytes: bytes
) -> None:
    archive = zip_bytes("fixture.asc", raw_bytes)
    contract = contract_for_archive(raw_bytes, archive)

    path = acquire_dataset(contract, tmp_path, opener_for(archive))

    assert path.read_bytes() == raw_bytes
    verify_file_identity(path, len(raw_bytes), contract.raw_sha256, "fixture")
    assert not list(tmp_path.glob("*.part"))


def test_archive_checksum_mismatch_is_rejected(
    tmp_path: Path, raw_bytes: bytes
) -> None:
    archive = zip_bytes("fixture.asc", raw_bytes)
    contract = contract_for_archive(raw_bytes, archive)

    changed_archive = archive[:-1] + bytes([archive[-1] ^ 1])
    with pytest.raises(IntegrityError, match="archive SHA-256 mismatch"):
        acquire_dataset(contract, tmp_path, opener_for(changed_archive))
    assert not (tmp_path / contract.raw_filename).exists()
    assert not list(tmp_path.glob("*.part"))


def test_raw_checksum_mismatch_is_rejected(tmp_path: Path, raw_bytes: bytes) -> None:
    changed_raw = raw_bytes[:-2] + (b"0" if raw_bytes[-2:-1] != b"0" else b"1") + b"\n"
    archive = zip_bytes("fixture.asc", changed_raw)
    contract = contract_for_archive(raw_bytes, archive)

    with pytest.raises(IntegrityError, match="raw member SHA-256 mismatch"):
        acquire_dataset(contract, tmp_path, opener_for(archive))


def test_missing_approved_member_is_rejected(tmp_path: Path, raw_bytes: bytes) -> None:
    archive = zip_bytes("other.asc", raw_bytes)
    contract = contract_for_archive(raw_bytes, archive)

    with pytest.raises(AcquisitionError, match="exactly one approved member"):
        acquire_dataset(contract, tmp_path, opener_for(archive))


def test_unsafe_archive_member_is_rejected(tmp_path: Path, raw_bytes: bytes) -> None:
    archive = zip_bytes("fixture.asc", raw_bytes, {"../escape.txt": b"unsafe"})
    contract = contract_for_archive(raw_bytes, archive)

    with pytest.raises(AcquisitionError, match="unsafe member"):
        acquire_dataset(contract, tmp_path, opener_for(archive))
    assert not (tmp_path.parent / "escape.txt").exists()


def test_unrelated_safe_member_is_ignored(tmp_path: Path, raw_bytes: bytes) -> None:
    archive = zip_bytes("fixture.asc", raw_bytes, {"codetable.txt": b"metadata"})
    contract = contract_for_archive(raw_bytes, archive)

    path = acquire_dataset(contract, tmp_path, opener_for(archive))

    assert path.read_bytes() == raw_bytes
    assert not (tmp_path / "codetable.txt").exists()


def test_partial_download_is_cleaned_up(tmp_path: Path, raw_bytes: bytes) -> None:
    archive = zip_bytes("fixture.asc", raw_bytes)
    contract = contract_for_archive(raw_bytes, archive)

    class FailingStream(io.BytesIO):
        def read(self, size: int = -1) -> bytes:
            if self.tell() > 0:
                raise OSError("simulated connection loss")
            return super().read(10 if size < 0 else min(size, 10))

    @contextmanager
    def opener(_url: str):
        yield FailingStream(archive)

    with pytest.raises(AcquisitionError, match="download failed"):
        acquire_dataset(contract, tmp_path, opener)
    assert not list(tmp_path.glob("*.part"))
    assert not (tmp_path / contract.raw_filename).exists()


def test_existing_invalid_destination_is_not_replaced(
    tmp_path: Path, raw_bytes: bytes
) -> None:
    archive = zip_bytes("fixture.asc", raw_bytes)
    contract = contract_for_archive(raw_bytes, archive)
    destination = tmp_path / contract.raw_filename
    destination.write_bytes(b"invalid")

    with pytest.raises(AcquisitionError, match="will not be replaced"):
        acquire_dataset(contract, tmp_path, opener_for(archive))
    assert destination.read_bytes() == b"invalid"


def test_existing_valid_destination_avoids_download(
    tmp_path: Path, raw_bytes: bytes
) -> None:
    archive = zip_bytes("fixture.asc", raw_bytes)
    contract = contract_for_archive(raw_bytes, archive)
    destination = tmp_path / contract.raw_filename
    destination.write_bytes(raw_bytes)

    def forbidden_opener(_url: str):
        raise AssertionError("network should not be called")

    assert acquire_dataset(contract, tmp_path, forbidden_opener) == destination
