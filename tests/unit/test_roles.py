from __future__ import annotations

import pandas as pd
import pytest

from aletheia.contracts import FeatureRoleError
from aletheia.data.load import load_raw_data
from aletheia.data.roles import build_feature_views
from aletheia.data.target import add_adverse_target


def _mapped(raw_file, dataset_contract):
    return add_adverse_target(
        load_raw_data(raw_file, dataset_contract), dataset_contract
    )


def test_roles_are_disjoint_and_exhaustive(dataset_contract, feature_policy) -> None:
    groups = [
        set(feature_policy.prediction),
        set(feature_policy.audit_only),
        set(feature_policy.excluded),
        set(feature_policy.raw_target),
    ]

    assert set.union(*groups) == set(dataset_contract.columns)
    assert sum(len(group) for group in groups) == len(set.union(*groups))


def test_model_input_excludes_every_non_prediction_role(
    raw_file, dataset_contract, feature_policy
) -> None:
    views = build_feature_views(_mapped(raw_file, dataset_contract), feature_policy)
    model_input = views.model_input()

    forbidden = {
        *feature_policy.audit_only,
        *feature_policy.excluded,
        *feature_policy.raw_target,
        *feature_policy.derived_target,
        *feature_policy.metadata,
    }
    assert forbidden.isdisjoint(model_input.columns)
    assert "telef" not in model_input
    assert "bishkred" not in model_input
    assert tuple(model_input.columns) == feature_policy.prediction


def test_prediction_and_audit_views_keep_identical_keys(
    raw_file, dataset_contract, feature_policy
) -> None:
    views = build_feature_views(_mapped(raw_file, dataset_contract), feature_policy)

    assert views.prediction["row_key"].tolist() == views.audit_only["row_key"].tolist()
    assert views.target["row_key"].tolist() == views.metadata["row_key"].tolist()


def test_unknown_field_fails_closed(raw_file, dataset_contract, feature_policy) -> None:
    frame = _mapped(raw_file, dataset_contract)
    frame["surprise"] = pd.Series(range(len(frame)))

    with pytest.raises(FeatureRoleError, match="unknown field"):
        build_feature_views(frame, feature_policy)
