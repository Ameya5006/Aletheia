"""Restore integrity distinguishes file changes from archive metadata changes."""

import importlib
import io
import tarfile
from pathlib import Path


def archive(payload=b"approved evidence", mtime=1, mode=0o644):
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode="w") as output:
        item = tarfile.TarInfo("manifest.json")
        item.size, item.mtime, item.mode = len(payload), mtime, mode
        output.addfile(item, io.BytesIO(payload))
    return data.getvalue()


def test_restore_integrity_ignores_archive_timestamps_but_detects_corruption(
    monkeypatch,
):
    monkeypatch.syspath_prepend(
        str(Path(__file__).resolve().parents[2] / "deployment/tests")
    )
    contents = importlib.import_module("restore").contents
    assert contents(archive()) == contents(archive(mtime=2))
    assert contents(archive()) != contents(archive(payload=b"changed evidence"))
    assert contents(archive()) != contents(archive(mode=0o666))
