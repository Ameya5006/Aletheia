"""Construct only the two estimators authorized for the Phase 4 baseline."""

from __future__ import annotations

from sklearn.base import ClassifierMixin
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from aletheia.contracts import BaselineExperimentConfig, ExperimentError
from aletheia.ml.preprocess import build_preprocessor

MODEL_NAMES = ("dummy", "logistic_regression")


def build_estimator(name: str, config: BaselineExperimentConfig) -> ClassifierMixin:
    """Return one explicitly configured, unfitted baseline estimator."""
    if name == "dummy":
        return DummyClassifier(strategy=config.dummy_strategy)
    if name == "logistic_regression":
        return LogisticRegression(
            penalty=config.logistic_penalty,
            C=config.logistic_c,
            solver=config.logistic_solver,
            class_weight=config.logistic_class_weight,
            max_iter=config.logistic_max_iter,
        )
    raise ExperimentError(f"unsupported Phase 4 model {name!r}")


def build_pipeline(name: str, config: BaselineExperimentConfig) -> Pipeline:
    """Bind a fresh preprocessor to a fresh estimator for one fold."""
    return Pipeline(
        steps=[
            ("preprocess", build_preprocessor(config)),
            ("model", build_estimator(name, config)),
        ]
    )


def model_configuration(config: BaselineExperimentConfig) -> dict[str, dict]:
    """Return the explicit estimator settings stored in the run manifest."""
    return {
        "dummy": {"strategy": config.dummy_strategy},
        "logistic_regression": {
            "penalty": config.logistic_penalty,
            "C": config.logistic_c,
            "solver": config.logistic_solver,
            "class_weight": config.logistic_class_weight,
            "max_iter": config.logistic_max_iter,
        },
    }
