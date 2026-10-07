"""Probability metrics, calibration diagnostics, and patient-cluster intervals."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)


def _clip(probability: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(probability, dtype=float), 1e-6, 1 - 1e-6)


def logit(probability: np.ndarray) -> np.ndarray:
    clipped = _clip(probability)
    return np.log(clipped / (1 - clipped)).reshape(-1, 1)


def sigmoid_fit(
    y: pd.Series | np.ndarray, probability: np.ndarray
) -> LogisticRegression:
    """Fit Platt's two-parameter sigmoid to predictions from disjoint folds."""
    return LogisticRegression(C=1e6, solver="lbfgs", max_iter=300).fit(
        logit(probability), np.asarray(y)
    )


def sigmoid_predict(
    calibrator: LogisticRegression, probability: np.ndarray
) -> np.ndarray:
    return calibrator.predict_proba(logit(probability))[:, 1]


def metrics(
    y: pd.Series | np.ndarray, probability: np.ndarray
) -> dict[str, float | int]:
    truth = np.asarray(y, dtype=int)
    prediction = (_clip(probability) >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(truth, prediction, labels=[0, 1]).ravel()
    return {
        "average_precision": float(average_precision_score(truth, probability)),
        "roc_auc": float(roc_auc_score(truth, probability)),
        "balanced_accuracy": float(balanced_accuracy_score(truth, prediction)),
        "recall": float(recall_score(truth, prediction, zero_division=0)),
        "specificity": float(tn / (tn + fp)),
        "precision": float(precision_score(truth, prediction, zero_division=0)),
        "f1": float(f1_score(truth, prediction, zero_division=0)),
        "log_loss": float(log_loss(truth, _clip(probability), labels=[0, 1])),
        "brier_score": float(brier_score_loss(truth, probability)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "class_0": int((truth == 0).sum()),
        "class_1": int((truth == 1).sum()),
    }


def calibration_diagnostics(
    y: pd.Series | np.ndarray, probability: np.ndarray
) -> dict[str, object]:
    truth = np.asarray(y, dtype=int)
    observed, predicted = calibration_curve(
        truth, probability, n_bins=10, strategy="uniform"
    )
    # Diagnostic regression; it never modifies predictions or model selection.
    slope_model = LogisticRegression(C=1e6, solver="lbfgs", max_iter=300).fit(
        logit(probability), truth
    )
    return {
        "fraction_positive": observed.tolist(),
        "mean_predicted": predicted.tolist(),
        "intercept": float(slope_model.intercept_[0]),
        "slope": float(slope_model.coef_[0, 0]),
    }


def cluster_intervals(
    y: pd.Series,
    probability: np.ndarray,
    patients: pd.Series,
    *,
    repetitions: int,
    seed: int,
) -> dict[str, list[float]]:
    """Resample patients, retaining every encounter within each selected cluster."""
    groups = patients.astype(str).to_numpy()
    patient_codes, inverse = np.unique(groups, return_inverse=True)
    member_indices = [
        np.flatnonzero(inverse == index) for index in range(len(patient_codes))
    ]
    truth = np.asarray(y, dtype=int)
    rng = np.random.default_rng(seed)
    names = (
        "average_precision",
        "roc_auc",
        "balanced_accuracy",
        "recall",
        "specificity",
        "precision",
        "f1",
        "log_loss",
        "brier_score",
    )
    samples: dict[str, list[float]] = {name: [] for name in names}
    for _ in range(repetitions):
        chosen = rng.integers(0, len(patient_codes), size=len(patient_codes))
        rows = np.concatenate([member_indices[index] for index in chosen])
        if len(np.unique(truth[rows])) != 2:
            continue
        measured = metrics(truth[rows], probability[rows])
        for name in names:
            samples[name].append(float(measured[name]))
    if any(len(values) != repetitions for values in samples.values()):
        raise ValueError("cluster bootstrap lost a class")
    return {
        name: [float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))]
        for name, values in samples.items()
    }
