"""Deterministic training-only cross-validation and metric calculation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold

from aletheia.contracts import BaselineExperimentConfig, ExperimentError
from aletheia.ml.models import MODEL_NAMES, build_pipeline
from aletheia.ml.preprocess import validate_fitted_schema


@dataclass(frozen=True)
class FoldMembership:
    """Indices and non-sensitive identity checksum for one validation fold."""

    train_indices: tuple[int, ...]
    validation_indices: tuple[int, ...]
    validation_checksum: str


def key_membership_checksum(keys: list[str] | tuple[str, ...]) -> str:
    """Hash sorted row keys using canonical JSON without feature/target values."""
    payload = json.dumps(
        sorted(str(key) for key in keys),
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def make_folds(
    row_keys: pd.Series,
    target: pd.Series,
    config: BaselineExperimentConfig,
) -> tuple[FoldMembership, ...]:
    """Create the single shared five-fold training-only membership."""
    if len(row_keys) != len(target) or row_keys.isna().any() or not row_keys.is_unique:
        raise ExperimentError("CV row keys and targets must be aligned and unique")
    splitter = StratifiedKFold(
        n_splits=config.cv_folds,
        shuffle=config.cv_shuffle,
        random_state=config.cv_seed,
    )
    folds = []
    validation_seen: set[int] = set()
    for train_index, validation_index in splitter.split(np.zeros(len(target)), target):
        train_tuple = tuple(int(index) for index in train_index)
        validation_tuple = tuple(int(index) for index in validation_index)
        if set(train_tuple) & set(validation_tuple):
            raise ExperimentError("CV training and validation membership overlap")
        if validation_seen & set(validation_tuple):
            raise ExperimentError("a row appears in multiple CV validation folds")
        validation_seen.update(validation_tuple)
        validation_keys = [str(row_keys.iloc[index]) for index in validation_tuple]
        folds.append(
            FoldMembership(
                train_indices=train_tuple,
                validation_indices=validation_tuple,
                validation_checksum=key_membership_checksum(validation_keys),
            )
        )
    if validation_seen != set(range(len(target))):
        raise ExperimentError("CV validation folds do not cover all training rows")
    return tuple(folds)


def probability_for_class_one(pipeline, features: pd.DataFrame) -> np.ndarray:
    """Select probabilities by locating class 1, never by assuming column order."""
    classes = list(pipeline.named_steps["model"].classes_)
    if 1 not in classes:
        raise ExperimentError("fitted estimator does not expose positive class 1")
    return np.asarray(pipeline.predict_proba(features)[:, classes.index(1)])


def classification_metrics(
    target: pd.Series | np.ndarray,
    probability: np.ndarray,
    *,
    threshold: float,
) -> dict[str, float]:
    """Compute the frozen probability and threshold metrics for adverse class 1."""
    truth = np.asarray(target, dtype=int)
    scores = np.asarray(probability, dtype=float)
    predicted = (scores >= threshold).astype(int)
    return {
        "roc_auc": float(roc_auc_score(truth, scores)),
        "average_precision": float(average_precision_score(truth, scores)),
        "balanced_accuracy": float(balanced_accuracy_score(truth, predicted)),
        "adverse_recall": float(recall_score(truth, predicted, pos_label=1)),
        "specificity": float(recall_score(truth, predicted, pos_label=0)),
        "precision": float(
            precision_score(truth, predicted, pos_label=1, zero_division=0)
        ),
        "f1": float(f1_score(truth, predicted, pos_label=1, zero_division=0)),
        "log_loss": float(log_loss(truth, scores, labels=[0, 1])),
        "brier_score": float(brier_score_loss(truth, scores, pos_label=1)),
    }


def _aggregate(per_fold: list[dict[str, float]]) -> dict[str, dict[str, float]]:
    return {
        metric: {
            "mean": float(np.mean([fold[metric] for fold in per_fold])),
            "standard_deviation": float(
                np.std([fold[metric] for fold in per_fold], ddof=0)
            ),
        }
        for metric in per_fold[0]
    }


def evaluate_models(
    features: pd.DataFrame,
    target: pd.Series,
    row_keys: pd.Series,
    config: BaselineExperimentConfig,
) -> dict:
    """Evaluate both baselines on identical folds with a new pipeline per fold."""
    folds = make_folds(row_keys, target, config)
    results: dict[str, dict] = {}
    for model_name in MODEL_NAMES:
        per_fold: list[dict[str, float]] = []
        for fold in folds:
            pipeline = build_pipeline(model_name, config)
            train_index = list(fold.train_indices)
            validation_index = list(fold.validation_indices)
            pipeline.fit(features.iloc[train_index], target.iloc[train_index])
            validate_fitted_schema(pipeline.named_steps["preprocess"], config)
            probability = probability_for_class_one(
                pipeline, features.iloc[validation_index]
            )
            per_fold.append(
                classification_metrics(
                    target.iloc[validation_index],
                    probability,
                    threshold=config.threshold,
                )
            )
        results[model_name] = {
            "fold_membership_checksums": [fold.validation_checksum for fold in folds],
            "per_fold_metrics": per_fold,
            "aggregate_metrics": _aggregate(per_fold),
        }
    return {
        "evaluation_scope": "locked_training_partition_cross_validation",
        "evaluated_row_count": len(features),
        "fold_membership_checksums": [fold.validation_checksum for fold in folds],
        "models": results,
    }
