"""Fail-closed schema and semantic validation for raw South German Credit."""

from __future__ import annotations

import pandas as pd

from aletheia.contracts import DatasetContract, FeaturePolicy, SchemaError
from aletheia.data.load import make_row_keys


def validate_raw_data(
    frame: pd.DataFrame,
    contract: DatasetContract,
    policy: FeaturePolicy,
) -> pd.DataFrame:
    """Validate fixed identity-derived structure, categories, keys, and duplicates."""
    expected_columns = ("row_key",) + contract.columns
    actual_columns = tuple(frame.columns)
    if actual_columns != expected_columns:
        raise SchemaError(
            f"loaded column/order mismatch: expected {expected_columns}, "
            f"got {actual_columns}"
        )
    if len(frame) != contract.row_count:
        raise SchemaError(
            f"validated row-count mismatch: expected {contract.row_count}, "
            f"got {len(frame)}"
        )
    if frame.isna().any().any():
        first_column = str(frame.columns[frame.isna().any()][0])
        raise SchemaError(f"missing value detected in column {first_column!r}")

    for column in contract.columns:
        if not pd.api.types.is_integer_dtype(frame[column].dtype):
            raise SchemaError(f"column {column!r} is not integer typed")

    expected_keys = make_row_keys(contract.row_count)
    actual_keys = tuple(frame["row_key"].astype(str))
    if actual_keys != expected_keys:
        mismatch = next(
            (
                expected
                for expected, actual in zip(expected_keys, actual_keys, strict=False)
                if expected != actual
            ),
            "unknown",
        )
        raise SchemaError(f"row-key sequence mismatch near expected key {mismatch}")
    if frame["row_key"].isna().any() or not frame["row_key"].is_unique:
        raise SchemaError("row keys must be unique and non-null")

    for column, domain in contract.categorical_domains.items():
        if column == contract.raw_target:
            continue
        observed = set(int(value) for value in frame[column].unique())
        invalid = sorted(observed - set(domain))
        if invalid:
            raise SchemaError(
                f"undocumented category in column {column!r}: {invalid[0]!r}"
            )

    target_values = set(int(value) for value in frame[contract.raw_target].unique())
    invalid_target = sorted(target_values - set(contract.allowed_target_values))
    if invalid_target:
        raise SchemaError(
            f"invalid raw target in column {contract.raw_target!r}: "
            f"{invalid_target[0]!r}"
        )
    if frame.duplicated(subset=list(contract.columns)).any():
        duplicate_key = str(
            frame.loc[
                frame.duplicated(subset=list(contract.columns), keep=False), "row_key"
            ].iloc[0]
        )
        raise SchemaError(
            f"duplicate complete raw row detected at row key {duplicate_key}"
        )
    predictors = [
        column for column in contract.columns if column != contract.raw_target
    ]
    if frame.duplicated(subset=predictors).any():
        duplicate_key = str(
            frame.loc[frame.duplicated(subset=predictors, keep=False), "row_key"].iloc[
                0
            ]
        )
        raise SchemaError(
            f"duplicate predictor-only row detected at row key {duplicate_key}"
        )

    actual_target_counts = {
        int(value): int(count)
        for value, count in frame[contract.raw_target].value_counts().items()
    }
    if actual_target_counts != contract.expected_target_counts:
        raise SchemaError(
            "raw target count mismatch: "
            f"expected {contract.expected_target_counts}, got {actual_target_counts}"
        )

    if set(policy.raw_role_fields) != set(contract.columns):
        raise SchemaError("feature-role policy does not exhaust the raw schema")
    return frame
