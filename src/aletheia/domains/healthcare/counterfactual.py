"""Fail-closed feasibility assessment; no unsupported clinical recourse search."""

from __future__ import annotations

from typing import Any

import pandas as pd

from .explain import check_features
from .foundation import Contracts, HealthcareDataError


def assess(contracts: Contracts, config: dict[str, Any]) -> dict[str, Any]:
    if config["mode"] != "feasibility assessment only" or (
        config["mutable"] or config["conditionally_mutable"]
    ):
        raise HealthcareDataError("clinical recourse constraints are not approved")
    roles = contracts.features["roles"]
    return {
        "status": "no_defensible_recourse",
        "reason": config["reason"],
        "immutable": roles["prediction"] + roles["audit_only"] + roles["metadata"],
        "excluded": roles["excluded"] + roles["raw_target"] + roles["derived_target"],
        "conditionally_mutable": [],
        "mutable": [],
        "distance_cost": None,
        "distance_reason": "No admissible intervention set; cost would be invented.",
        "limitations": (
            "Model sensitivity is not a clinical recommendation or outcome guarantee."
        ),
    }


def validate_scenario(
    contracts: Contracts,
    config: dict[str, Any],
    original: pd.DataFrame,
    proposed: pd.DataFrame,
) -> bool:
    assess(contracts, config)
    check_features(contracts, original)
    check_features(contracts, proposed)
    if len(original) != 1 or len(proposed) != 1 or not original.equals(proposed):
        raise HealthcareDataError("scenario changes an immutable discharge observation")
    return True


def scenario_result(contracts: Contracts, config: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "no_feasible_scenario",
        "search_performed": False,
        "candidates": [],
        "assessment": assess(contracts, config),
        "worked_example": (
            "For the fixed synthetic discharge encounter, reducing prior inpatient "
            "visits or medication count rewrites history/care. Both changes are "
            "forbidden; no scenario is returned."
        ),
    }
