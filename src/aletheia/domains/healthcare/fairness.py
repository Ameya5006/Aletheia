"""Supported source-category subgroup metrics with patient-cluster uncertainty."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

from .foundation import HealthcareDataError

GROUPS = {
    "race": [
        "AfricanAmerican",
        "Asian",
        "Caucasian",
        "Hispanic",
        "Other",
        "__MISSING__",
    ],
    "gender": ["Female", "Male", "Unknown/Invalid", "__MISSING__"],
    "age": [f"[{start}-{start + 10})" for start in range(0, 100, 10)] + ["__MISSING__"],
}
METRICS = (
    "prevalence",
    "average_precision",
    "roc_auc",
    "brier_score",
    "recall",
    "specificity",
    "false_positive_rate",
    "false_negative_rate",
    "positive_prediction_rate",
)


def subgroup_metrics(y: np.ndarray, p: np.ndarray, threshold: float) -> dict[str, Any]:
    y, p = np.asarray(y), np.asarray(p)
    if len(y) == 0:
        return {name: None for name in METRICS}
    prediction = p >= threshold
    positive, negative = y == 1, y == 0
    recall = float(prediction[positive].mean()) if positive.any() else None
    specificity = float((~prediction[negative]).mean()) if negative.any() else None
    return {
        "prevalence": float(positive.mean()),
        "average_precision": float(average_precision_score(y, p))
        if positive.any()
        else None,
        "roc_auc": float(roc_auc_score(y, p))
        if positive.any() and negative.any()
        else None,
        "brier_score": float(brier_score_loss(y, p)),
        "recall": recall,
        "specificity": specificity,
        "false_positive_rate": None if specificity is None else 1 - specificity,
        "false_negative_rate": None if recall is None else 1 - recall,
        "positive_prediction_rate": float(prediction.mean()),
    }


def subgroup_intervals(
    y: np.ndarray,
    p: np.ndarray,
    patients: np.ndarray,
    config: dict[str, Any],
) -> dict[str, Any]:
    _, inverse = np.unique(patients.astype(str), return_inverse=True)
    members = [np.flatnonzero(inverse == i) for i in range(inverse.max() + 1)]
    rng = np.random.default_rng(config["bootstrap_seed"])
    samples: dict[str, list[float]] = {name: [] for name in METRICS}
    for _ in range(config["bootstrap_repetitions"]):
        rows = np.concatenate(
            [members[i] for i in rng.integers(len(members), size=len(members))]
        )
        values = subgroup_metrics(y[rows], p[rows], config["threshold"])
        for name, value in values.items():
            if value is not None:
                samples[name].append(value)
    alpha = (1 - config["confidence"]) / 2
    return {
        name: {
            "interval": np.quantile(values, [alpha, 1 - alpha]).tolist()
            if values
            else None,
            "valid_replicates": len(values),
            "undefined_replicates": config["bootstrap_repetitions"] - len(values),
        }
        for name, values in samples.items()
    }


def audit_subgroups(
    audit: pd.DataFrame,
    y: pd.Series,
    p: pd.Series,
    patients: pd.Series,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    if (
        list(audit) != config["attributes"]
        or any(not audit.index.equals(item.index) for item in (y, p, patients))
        or not audit.index.is_unique
    ):
        raise HealthcareDataError("subgroup row alignment mismatch")
    if (
        not set(y.unique()) <= {0, 1}
        or not np.isfinite(p).all()
        or not p.between(0, 1).all()
    ):
        raise HealthcareDataError("invalid subgroup truth/probability")
    records = []
    for attribute in config["attributes"]:
        values = audit[attribute].fillna("__MISSING__")
        if not set(values.unique()) <= set(GROUPS[attribute]):
            raise HealthcareDataError("unknown audit category")
        for group in GROUPS[attribute]:
            mask = values.eq(group)
            truth, predicted = y[mask].to_numpy(), p[mask].to_numpy()
            group_patients = patients[mask].to_numpy()
            counts = {
                "encounters": int(mask.sum()),
                "patients": int(len(np.unique(group_patients))),
                "positive": int((truth == 1).sum()),
                "negative": int((truth == 0).sum()),
            }
            supported = all(
                counts[name] >= config[f"minimum_{name}"] for name in counts
            )
            safe_counts = {
                name: count
                if count >= config["privacy_count_floor"]
                else f"<{config['privacy_count_floor']}"
                for name, count in counts.items()
            }
            records.append(
                {
                    "attribute": attribute,
                    "group": group,
                    "counts": safe_counts,
                    "status": "supported" if supported else "insufficient_support",
                    "reason": None
                    if supported
                    else (
                        "minimum encounter/patient/positive/negative support "
                        "not met; metrics withheld"
                    ),
                    "metrics": subgroup_metrics(truth, predicted, config["threshold"])
                    if supported
                    else None,
                    "uncertainty": subgroup_intervals(
                        truth, predicted, group_patients, config
                    )
                    if supported
                    else None,
                }
            )
    return records
