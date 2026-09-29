"""Explicit raw-to-adverse target mapping."""

from __future__ import annotations

import pandas as pd

from aletheia.contracts import DatasetContract, SchemaError


def map_adverse_target(raw_target: pd.Series, contract: DatasetContract) -> pd.Series:
    """Map raw 0/bad to analytical 1/adverse while refusing unknown labels."""
    observed = set(int(value) for value in raw_target.unique())
    invalid = sorted(observed - set(contract.allowed_target_values))
    if invalid:
        raise SchemaError(
            f"invalid raw target value {invalid[0]!r}; "
            f"allowed values are {sorted(contract.allowed_target_values)}"
        )
    mapped = raw_target.eq(contract.adverse_raw_value).astype("int64")
    mapped.name = contract.derived_target
    return mapped


def add_adverse_target(frame: pd.DataFrame, contract: DatasetContract) -> pd.DataFrame:
    """Return a copy containing the derived target and unchanged raw target."""
    if contract.raw_target not in frame.columns:
        raise SchemaError(f"raw target column {contract.raw_target!r} is missing")
    result = frame.copy()
    before = result[contract.raw_target].copy()
    result[contract.derived_target] = map_adverse_target(before, contract)
    if not result[contract.raw_target].equals(before):
        raise SchemaError("raw target changed while deriving the adverse target")
    return result
