"""Frozen input verification permits Git newline conversion, not edits."""

import hashlib
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "ci_frozen_check",
    Path(__file__).resolve().parents[2] / "deployment/azure/ci-frozen-check.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@pytest.mark.parametrize("checkout", [b"one\ntwo\n", b"one\r\ntwo\r\n"])
def test_git_line_endings_match_approved_windows_bytes(tmp_path, checkout):
    source = tmp_path / "input.txt"
    source.write_bytes(checkout)
    approved = hashlib.sha256(b"one\r\ntwo\r\n").hexdigest()
    assert MODULE.matches_approved(source, approved)


def test_content_change_does_not_match_approved_hash(tmp_path):
    source = tmp_path / "input.txt"
    source.write_bytes(b"one\nchanged\n")
    approved = hashlib.sha256(b"one\r\ntwo\r\n").hexdigest()
    assert not MODULE.matches_approved(source, approved)
