"""Fold-local healthcare preprocessing, bounded candidates, and group CV."""

from __future__ import annotations

import time
import warnings
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .foundation import Contracts, HealthcareDataError


def group_folds(
    y: pd.Series, groups: pd.Series, n_splits: int, seed: int
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Materialize and verify patient-disjoint, two-class validation folds."""
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    folds = list(splitter.split(np.zeros(len(y)), y, groups))
    for train, valid in folds:
        if set(groups.iloc[train]) & set(groups.iloc[valid]):
            raise HealthcareDataError("patient crossed a CV fold")
        if set(y.iloc[train]) != {0, 1} or set(y.iloc[valid]) != {0, 1}:
            raise HealthcareDataError("both classes required in each CV partition")
    return folds


def candidates(config: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grid = config["candidates"]
    return {
        "dummy": [{"strategy": "prior"}],
        "logistic": [
            {"C": c, "class_weight": None if weight == "none" else weight}
            for c in grid["logistic_c"]
            for weight in grid["logistic_class_weight"]
        ],
        "forest": [
            {
                "max_depth": depth,
                "n_estimators": grid["forest_n_estimators"],
                "min_samples_leaf": grid["forest_min_samples_leaf"],
            }
            for depth in grid["forest_max_depth"]
        ],
        "histogram": [
            {
                "max_leaf_nodes": leaves,
                "max_iter": grid["hist_max_iter"],
                "min_samples_leaf": grid["hist_min_samples_leaf"],
            }
            for leaves in grid["hist_max_leaf_nodes"]
        ],
    }


def pipeline(
    contracts: Contracts,
    family: str,
    params: dict[str, Any],
    seed: int,
    *,
    dense: bool = False,
) -> Pipeline:
    types = contracts.features["semantic_types"]
    numeric = Pipeline(
        [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    )
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="constant", fill_value="__MISSING__")),
            (
                "encode",
                OneHotEncoder(handle_unknown="ignore", sparse_output=not dense),
            ),
        ]
    )
    preprocessor = ColumnTransformer(
        [
            ("numeric", numeric, types["quantitative"]),
            ("categorical", categorical, types["categorical"]),
        ],
        sparse_threshold=0.0 if dense else 1.0,
        remainder="drop",
    )
    if family == "dummy":
        estimator = DummyClassifier(**params)
    elif family == "logistic":
        estimator = LogisticRegression(
            **params, max_iter=300, solver="lbfgs", random_state=seed
        )
    elif family == "forest":
        estimator = RandomForestClassifier(**params, random_state=seed, n_jobs=1)
    elif family == "histogram":
        estimator = HistGradientBoostingClassifier(
            **params, random_state=seed, early_stopping=False
        )
    else:
        raise HealthcareDataError(f"unknown candidate family: {family}")
    return Pipeline([("preprocess", preprocessor), ("model", estimator)])


def fit_predict(
    contracts: Contracts,
    config: dict[str, Any],
    family: str,
    params: dict[str, Any],
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_valid: pd.DataFrame,
    *,
    seed: int,
) -> tuple[Pipeline, np.ndarray, np.ndarray, dict[str, Any]]:
    if list(x_train) != contracts.features["roles"]["prediction"] or list(
        x_valid
    ) != list(x_train):
        raise HealthcareDataError("model matrix violates frozen predictor order")
    dense = family == "histogram"
    if dense:
        # A conservative bound includes all rows and every possible observed category.
        categorical = contracts.features["semantic_types"]["categorical"]
        upper_columns = 8 + sum(
            x_train[name].nunique(dropna=False) + 1 for name in categorical
        )
        estimated = (len(x_train) + len(x_valid)) * upper_columns * 8
        if estimated > config["preprocessing"]["max_dense_bytes"]:
            raise HealthcareDataError(
                f"dense histogram matrix exceeds budget: {estimated}"
            )
    fitted = pipeline(contracts, family, params, seed, dense=dense)
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always", ConvergenceWarning)
        start = time.perf_counter()
        fitted.fit(x_train, y_train)
        fit_seconds = time.perf_counter() - start
    start = time.perf_counter()
    train_probability = fitted.predict_proba(x_train)[:, 1]
    valid_probability = fitted.predict_proba(x_valid)[:, 1]
    predict_seconds = time.perf_counter() - start
    feature_names = list(fitted.named_steps["preprocess"].get_feature_names_out())
    return (
        fitted,
        train_probability,
        valid_probability,
        {
            "fit_seconds": fit_seconds,
            "predict_seconds": predict_seconds,
            "convergence_warnings": [
                str(item.message)
                for item in captured
                if issubclass(item.category, ConvergenceWarning)
            ],
            "transformed_features": feature_names,
            "dense_estimated_bytes": estimated if dense else 0,
        },
    )
