"""Bounded recording perturbations; paired paths isolate input sensitivity."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .explain import attributions, check_features
from .foundation import Contracts, HealthcareDataError


def compare(first: np.ndarray, second: np.ndarray, top_k: int) -> dict[str, Any]:
    # Stable sort resolves top-k ties in the frozen source-field order.
    a = np.argsort(-np.abs(first), kind="stable")[:top_k]
    b = np.argsort(-np.abs(second), kind="stable")[:top_k]
    constant = np.ptp(np.abs(first)) == 0 or np.ptp(np.abs(second)) == 0
    rank = (
        None if constant else float(spearmanr(np.abs(first), np.abs(second)).statistic)
    )
    denominator = float(np.abs(first).sum())
    return {
        "top_k_overlap": len(set(a) & set(b)) / top_k,
        "absolute_rank_correlation": rank,
        "normalized_l1": float(np.abs(first - second).sum() / denominator)
        if denominator
        else None,
        "undefined_reason": "constant ranking or zero attribution norm"
        if constant or not denominator
        else None,
    }


def perturb(
    contracts: Contracts,
    case: pd.DataFrame,
    config: dict[str, Any],
    bounds: dict[str, list[int]],
    rng: np.random.Generator,
) -> pd.DataFrame:
    check_features(contracts, case)
    if (
        len(case) != 1
        or config["fields"] != ["num_lab_procedures", "num_procedures"]
        or config["integer_delta"] != 1
    ):
        raise HealthcareDataError("unapproved recording perturbation")
    result = case.copy()
    for field in config["fields"]:
        low, high = bounds[field]
        original = int(case.iloc[0][field])
        if not 0 <= low <= original <= high:
            raise HealthcareDataError("recording value outside observed bounds")
        value = int(np.clip(original + rng.choice([-1, 1]), low, high))
        result.loc[:, field] = str(value)
    return result


def analyze_stability(
    contracts: Contracts,
    bundle: dict[str, Any],
    training: pd.DataFrame,
    background: pd.DataFrame,
    explanation: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    sample = training.sample(
        n=config["sample_size"], random_state=config["sample_seed"]
    )
    bounds = {
        field: [
            int(training[field].astype(int).min()),
            int(training[field].astype(int).max()),
        ]
        for field in config["fields"]
    }
    rng = np.random.default_rng(config["seed"])
    comparisons = []
    deltas = []
    crossings = 0
    unchanged = 0
    for index in range(len(sample)):
        case = sample.iloc[[index]]
        first, _, p = attributions(
            contracts,
            bundle,
            case,
            background,
            permutations=explanation["permutations"],
            seed=explanation["path_seed"],
        )
        for _ in range(config["repetitions"]):
            changed = perturb(contracts, case, config, bounds, rng)
            second, _, q = attributions(
                contracts,
                bundle,
                changed,
                background,
                permutations=explanation["permutations"],
                seed=explanation["path_seed"],
            )
            crossing = bool((p[0] >= 0.5) != (q[0] >= 0.5))
            crossings += int(crossing)
            unchanged += int(case.equals(changed))
            comparisons.append(
                (crossing, compare(first[0], second[0], config["top_k"]))
            )
            deltas.append(float(abs(p[0] - q[0])))

    def summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
        result = {}
        for name in ("top_k_overlap", "absolute_rank_correlation", "normalized_l1"):
            values = [row[name] for row in rows if row[name] is not None]
            result[name] = {
                "mean": float(np.mean(values)) if values else None,
                "min": float(np.min(values)) if values else None,
                "max": float(np.max(values)) if values else None,
                "undefined": len(rows) - len(values),
            }
        return result

    return {
        "population": (
            "training encounter recording sensitivity, not intervention feasibility"
        ),
        "comparisons": len(comparisons),
        "boundary_crossings": crossings,
        "unchanged_at_bound": unchanged,
        "bounds": bounds,
        "all": summary([row for _, row in comparisons]),
        "same_class": summary([row for cross, row in comparisons if not cross]),
        "crossed_class": summary([row for cross, row in comparisons if cross]),
        "mean_absolute_probability_change": float(np.mean(deltas)),
        "max_absolute_probability_change": float(np.max(deltas)),
        "below_overlap_reference": sum(
            row["top_k_overlap"] < config["overlap_reference"] for _, row in comparisons
        ),
        "above_distance_reference": sum(
            row["normalized_l1"] is not None
            and row["normalized_l1"] > config["distance_reference"]
            for _, row in comparisons
        ),
        "limitations": (
            "Protocol reference flags are descriptive, not universal clinical "
            "standards. Two +/-1 recording fields, small training sample, fixed "
            "paths; no causal or broad robustness claim."
        ),
    }
