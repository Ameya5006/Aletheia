"""Controlled acquisition of the one approved UCI archive member."""

from __future__ import annotations

import base64
import hashlib
import os
import shutil
import ssl
import subprocess
import tempfile
import urllib.error
import urllib.request
import zipfile
from collections.abc import Callable
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from aletheia.contracts import (
    AcquisitionError,
    DatasetContract,
    IntegrityError,
)

Opener = Callable[[str], AbstractContextManager[BinaryIO]]


def sha256_bytes(content: bytes) -> str:
    """Return the lowercase SHA-256 digest of bytes."""
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: str | Path) -> str:
    """Hash a file without loading it all into memory."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_file_identity(
    path: str | Path, expected_size: int, expected_sha256: str, label: str
) -> None:
    """Fail if a file's byte size or digest differs from its contract."""
    file_path = Path(path)
    try:
        actual_size = file_path.stat().st_size
    except OSError as exc:
        raise IntegrityError(f"{label} cannot be read at {file_path}: {exc}") from exc
    if actual_size != expected_size:
        raise IntegrityError(
            f"{label} size mismatch: expected {expected_size}, got {actual_size}"
        )
    actual_sha256 = sha256_file(file_path)
    if actual_sha256 != expected_sha256:
        raise IntegrityError(
            f"{label} SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}"
        )


def _python_tls_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    enum_certificates = getattr(ssl, "enum_certificates", None)
    if enum_certificates is not None:
        native_roots = [
            ssl.DER_cert_to_PEM_cert(certificate)
            for certificate, encoding, _trust in enum_certificates("ROOT")
            if encoding == "x509_asn"
        ]
        if native_roots:
            context.load_verify_locations(cadata="\n".join(native_roots))
    return context


@contextmanager
def _default_opener(url: str):
    """Use verified Python TLS, with Windows Schannel as a narrow trust fallback."""
    try:
        with urllib.request.urlopen(  # noqa: S310 - URL is fixed by the contract
            url, timeout=30, context=_python_tls_context()
        ) as response:
            yield response
            return
    except urllib.error.URLError as exc:
        certificate_failure = "CERTIFICATE_VERIFY_FAILED" in str(exc)
        if os.name != "nt" or not certificate_failure:
            raise

    descriptor, download_name = tempfile.mkstemp(
        prefix="aletheia-schannel-", suffix=".download"
    )
    os.close(descriptor)
    download_path = Path(download_name)
    try:
        escaped_url = url.replace("'", "''")
        escaped_path = str(download_path).replace("'", "''")
        script = (
            "Invoke-WebRequest -UseBasicParsing "
            f"-Uri '{escaped_url}' -OutFile '{escaped_path}'"
        )
        encoded_script = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
        command = [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-EncodedCommand",
            encoded_script,
        ]
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=60, check=False
        )
        if result.returncode != 0:
            detail = (
                result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ""
            )
            raise OSError(
                f"Windows certificate-validated download failed with exit "
                f"{result.returncode}: {detail}"
            )
        with download_path.open("rb") as response:
            yield response
    finally:
        download_path.unlink(missing_ok=True)


def _is_safe_member(name: str) -> bool:
    member = PurePosixPath(name.replace("\\", "/"))
    return not member.is_absolute() and ".." not in member.parts and bool(member.parts)


def _read_approved_member(archive_path: Path, contract: DatasetContract) -> bytes:
    try:
        with zipfile.ZipFile(archive_path) as archive:
            entries = archive.infolist()
            unsafe = [
                entry.filename
                for entry in entries
                if not _is_safe_member(entry.filename)
            ]
            if unsafe:
                raise AcquisitionError(
                    f"archive contains unsafe member name {unsafe[0]!r}; "
                    "extraction refused"
                )
            approved = [
                entry
                for entry in entries
                if entry.filename == contract.archive_member and not entry.is_dir()
            ]
            if len(approved) != 1:
                raise AcquisitionError(
                    "archive must contain exactly one approved member "
                    f"{contract.archive_member!r}; found {len(approved)}"
                )
            return archive.read(approved[0])
    except (OSError, zipfile.BadZipFile, NotImplementedError, RuntimeError) as exc:
        raise AcquisitionError(f"approved archive could not be read: {exc}") from exc


def _verify_bytes(
    content: bytes, expected_size: int, expected_sha256: str, label: str
) -> None:
    if len(content) != expected_size:
        raise IntegrityError(
            f"{label} size mismatch: expected {expected_size}, got {len(content)}"
        )
    actual_sha256 = sha256_bytes(content)
    if actual_sha256 != expected_sha256:
        raise IntegrityError(
            f"{label} SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}"
        )


def acquire_dataset(
    contract: DatasetContract,
    destination: str | Path,
    opener: Opener = _default_opener,
) -> Path:
    """Download, verify, and atomically publish only the approved raw member."""
    destination_path = Path(destination)
    raw_path = destination_path / contract.raw_filename
    if raw_path.exists():
        try:
            verify_file_identity(
                raw_path, contract.raw_size, contract.raw_sha256, "existing raw file"
            )
        except IntegrityError as exc:
            raise AcquisitionError(
                f"existing destination is invalid and will not be replaced: {exc}"
            ) from exc
        return raw_path

    destination_path.mkdir(parents=True, exist_ok=True)
    archive_stage: Path | None = None
    raw_stage: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=".aletheia-archive-",
            suffix=".part",
            dir=destination_path,
            delete=False,
        ) as staging:
            archive_stage = Path(staging.name)
            try:
                with opener(contract.archive_url) as response:
                    shutil.copyfileobj(response, staging)
            except Exception as exc:
                raise AcquisitionError(
                    f"official dataset download failed: {exc}"
                ) from exc
            staging.flush()
            os.fsync(staging.fileno())

        verify_file_identity(
            archive_stage,
            contract.archive_size,
            contract.archive_sha256,
            "downloaded archive",
        )
        raw_content = _read_approved_member(archive_stage, contract)
        _verify_bytes(raw_content, contract.raw_size, contract.raw_sha256, "raw member")

        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=".aletheia-raw-",
            suffix=".part",
            dir=destination_path,
            delete=False,
        ) as staging:
            raw_stage = Path(staging.name)
            staging.write(raw_content)
            staging.flush()
            os.fsync(staging.fileno())
        os.replace(raw_stage, raw_path)
        raw_stage = None
        return raw_path
    except (AcquisitionError, IntegrityError):
        raise
    except OSError as exc:
        raise AcquisitionError(f"dataset could not be published safely: {exc}") from exc
    finally:
        for staging_path in (archive_stage, raw_stage):
            if staging_path is not None:
                staging_path.unlink(missing_ok=True)
