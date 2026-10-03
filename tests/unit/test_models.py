from __future__ import annotations

import pytest
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression

from aletheia.contracts import ExperimentError
from aletheia.ml.models import build_estimator, build_pipeline


def test_dummy_configuration_is_exact(baseline_config) -> None:
    estimator = build_estimator("dummy", baseline_config)

    assert isinstance(estimator, DummyClassifier)
    assert estimator.strategy == "prior"


def test_logistic_configuration_is_exact(baseline_config) -> None:
    estimator = build_estimator("logistic_regression", baseline_config)

    assert isinstance(estimator, LogisticRegression)
    assert estimator.penalty == "l2"
    assert estimator.C == 1.0
    assert estimator.solver == "lbfgs"
    assert estimator.class_weight is None
    assert estimator.max_iter == 1000


def test_each_pipeline_has_distinct_unfitted_components(baseline_config) -> None:
    first = build_pipeline("dummy", baseline_config)
    second = build_pipeline("dummy", baseline_config)

    assert first is not second
    assert first.named_steps["preprocess"] is not second.named_steps["preprocess"]
    assert first.named_steps["model"] is not second.named_steps["model"]


def test_unapproved_estimator_is_refused(baseline_config) -> None:
    with pytest.raises(ExperimentError, match="unsupported"):
        build_estimator("random_forest", baseline_config)
