"""Strict raw loader with source-bound row identities."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from aletheia.contracts import DatasetContract, SchemaError
from aletheia.data.acquire import verify_file_identity

_INTEGER_TOKEN = re.compile(r"[+-]?\d+")


def make_row_keys(row_count: int) -> tuple[str, ...]:
    """Create transparent one-based source-row keys with at least four digits."""
    if row_count < 1:
        raise SchemaError("row count must be positive before row keys are created")
    width = max(4, len(str(row_count)))
    return tuple(f"sgc-{position:0{width}d}" for position in range(1, row_count + 1))


def load_raw_data(path: str | Path, contract: DatasetContract) -> pd.DataFrame:
    """Verify and parse the raw file without coercion, repair, or target mapping."""
    raw_path = Path(path)
    verify_file_identity(raw_path, contract.raw_size, contract.raw_sha256, "raw file")
    try:
        text = raw_path.read_text(encoding="ascii")
    except (OSError, UnicodeDecodeError) as exc:
        raise SchemaError(f"raw file is not readable ASCII: {exc}") from exc

    lines = text.splitlines()
    if not lines:
        raise SchemaError("raw file is empty")
    header = tuple(lines[0].split())
    if header != contract.columns:
        raise SchemaError(
            f"raw header/order mismatch: expected {contract.columns}, got {header}"
        )
    data_lines = lines[1:]
    if len(data_lines) != contract.row_count:
        raise SchemaError(
            f"raw row-count mismatch: expected {contract.row_count}, "
            f"got {len(data_lines)}"
        )

    row_keys = make_row_keys(contract.row_count)
    rows: list[list[int]] = []
    for position, line in enumerate(data_lines, start=1):
        row_key = row_keys[position - 1]
        tokens = line.split()
        if len(tokens) != len(contract.columns):
            raise SchemaError(
                f"malformed row {row_key}: expected {len(contract.columns)} tokens, "
                f"got {len(tokens)}"
            )
        for column, token in zip(contract.columns, tokens, strict=True):
            if _INTEGER_TOKEN.fullmatch(token) is None:
                raise SchemaError(
                    f"non-integer token at row {row_key}, column {column!r}"
                )
        rows.append([int(token) for token in tokens])

    frame = pd.DataFrame(rows, columns=contract.columns, dtype="int64")
    frame.insert(0, "row_key", row_keys)
    return frame
