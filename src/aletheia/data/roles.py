"""Construct aligned feature-role views under a default-deny policy."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from aletheia.config import validate_feature_policy
from aletheia.contracts import DatasetContract, FeaturePolicy, FeatureRoleError


@dataclass(frozen=True)
class FeatureViews:
    """Aligned role views; only ``model_input`` is suitable for estimators."""

    prediction: pd.DataFrame
    audit_only: pd.DataFrame
    excluded: pd.DataFrame
    target: pd.DataFrame
    metadata: pd.DataFrame
    prediction_columns: tuple[str, ...]

    def model_input(self) -> pd.DataFrame:
        """Return only approved predictors, never row keys or audit/target fields."""
        return self.prediction.loc[:, list(self.prediction_columns)].copy()


def build_feature_views(
    frame: pd.DataFrame,
    policy: FeaturePolicy,
    dataset: DatasetContract | None = None,
) -> FeatureViews:
    """Build row-key-aligned views and reject every unapproved input field."""
    try:
        validate_feature_policy(policy, dataset)
    except ValueError as exc:
        raise FeatureRoleError(str(exc)) from exc
    actual = set(frame.columns)
    approved = set(policy.all_role_fields)
    unknown = sorted(actual - approved)
    missing = sorted(approved - actual)
    if unknown:
        raise FeatureRoleError(f"unknown field has no approved role: {unknown[0]!r}")
    if missing:
        raise FeatureRoleError(f"approved role field is missing: {missing[0]!r}")

    row_key = policy.metadata[0]
    views = FeatureViews(
        prediction=frame.loc[:, [row_key, *policy.prediction]].copy(),
        audit_only=frame.loc[:, [row_key, *policy.audit_only]].copy(),
        excluded=frame.loc[:, [row_key, *policy.excluded]].copy(),
        target=frame.loc[
            :, [row_key, *policy.raw_target, *policy.derived_target]
        ].copy(),
        metadata=frame.loc[:, list(policy.metadata)].copy(),
        prediction_columns=policy.prediction,
    )
    expected_keys = tuple(frame[row_key])
    for name in ("prediction", "audit_only", "excluded", "target", "metadata"):
        view = getattr(views, name)
        if tuple(view[row_key]) != expected_keys:
            raise FeatureRoleError(f"row-key alignment failed for {name} view")
    return views
