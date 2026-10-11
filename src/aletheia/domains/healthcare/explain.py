"""Source-field sampled Shapley evidence for the complete calibrated callable."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .evaluation import sigmoid_predict
from .foundation import Contracts, HealthcareDataError

LIMITATIONS = (
    "Educational research evidence, not medical advice. Associations are not causal. "
    "Marginal replacement can create unlikely combinations of correlated fields. "
    "Finite paths and a small training reference approximate interventional Shapley "
    "values; they do not expose perfect internal reasoning."
)


def check_features(contracts: Contracts, x: pd.DataFrame) -> None:
    if list(x) != contracts.features["roles"]["prediction"] or x.empty:
        raise HealthcareDataError("audit matrix violates frozen predictor order")


def probability(bundle: dict[str, Any], x: pd.DataFrame) -> np.ndarray:
    model = bundle["model"]
    labels = list(model.classes_)
    if labels != [0, 1]:
        raise HealthcareDataError("unexpected class orientation")
    base = model.predict_proba(x)[:, labels.index(1)]
    result = (
        sigmoid_predict(bundle["calibrator"], base)
        if bundle["calibrator"] is not None
        else base
    )
    if not np.isfinite(result).all() or np.any((result < 0) | (result > 1)):
        raise HealthcareDataError("invalid probability")
    return result


def feature_mapping(contracts: Contracts, model: Any) -> list[dict[str, str]]:
    """Use fitted encoder categories, never split ambiguous underscore names."""
    transform = model.named_steps["preprocess"]
    types = contracts.features["semantic_types"]
    sources = list(types["quantitative"])
    categories = (
        transform.named_transformers_["categorical"].named_steps["encode"].categories_
    )
    for field, values in zip(types["categorical"], categories, strict=True):
        sources.extend([field] * len(values))
    names = list(transform.get_feature_names_out())
    if len(names) != len(sources) or set(sources) != set(
        contracts.features["roles"]["prediction"]
    ):
        raise HealthcareDataError("transformed feature mapping mismatch")
    return [
        {"transformed": str(name), "source": field}
        for name, field in zip(names, sources, strict=True)
    ]


def attributions(
    contracts: Contracts,
    bundle: dict[str, Any],
    x: pd.DataFrame,
    background: pd.DataFrame,
    *,
    permutations: int,
    seed: int,
) -> tuple[np.ndarray, float, np.ndarray]:
    """Average paired telescoping paths; same reference/paths for every case."""
    check_features(contracts, x)
    check_features(contracts, background)
    if permutations < 1:
        raise HealthcareDataError("positive permutation count required")
    rng = np.random.default_rng(seed)
    paths = []
    for _ in range(permutations):
        reference = int(rng.integers(len(background)))
        order = rng.permutation(len(x.columns))
        paths.extend([(reference, order), (reference, order[::-1])])
    values = np.zeros((len(x), len(x.columns)))
    baselines = []
    for case_index, (_, case) in enumerate(x.iterrows()):
        inputs = []
        for reference, order in paths:
            hybrid = background.iloc[reference].copy()
            inputs.append(hybrid.copy())
            for field_index in order:
                hybrid.iloc[field_index] = case.iloc[field_index]
                inputs.append(hybrid.copy())
        scored = probability(bundle, pd.DataFrame(inputs, columns=x.columns))
        scored = scored.reshape(len(paths), len(x.columns) + 1)
        for path_index, (_, order) in enumerate(paths):
            values[case_index, order] += np.diff(scored[path_index]) / len(paths)
        baselines.append(float(scored[:, 0].mean()))
    predicted = probability(bundle, x)
    baseline = baselines[0]
    if not np.allclose(baselines, baseline, atol=1e-12) or not np.allclose(
        baseline + values.sum(axis=1), predicted, atol=1e-10
    ):
        raise HealthcareDataError("attribution additivity failed")
    return values, baseline, predicted


def local_explanation(
    contracts: Contracts,
    bundle: dict[str, Any],
    case: pd.DataFrame,
    background: pd.DataFrame,
    config: dict[str, Any],
    identity: dict[str, Any],
) -> dict[str, Any]:
    if len(case) != 1:
        raise HealthcareDataError("one local case required")
    values, baseline, predicted = attributions(
        contracts,
        bundle,
        case,
        background,
        permutations=config["permutations"],
        seed=config["path_seed"],
    )
    return {
        "identity": identity,
        "method": config["method"],
        "output": config["output"],
        "baseline": baseline,
        "probability": float(predicted[0]),
        "features": [
            {
                "field": field,
                "value": str(case.iloc[0][field]),
                "contribution": float(values[0, index]),
                "direction": "raises"
                if values[0, index] > 0
                else ("lowers" if values[0, index] < 0 else "zero"),
            }
            for index, field in enumerate(case.columns)
        ],
        "limitations": LIMITATIONS,
    }


def global_explanation(
    contracts: Contracts,
    bundle: dict[str, Any],
    training: pd.DataFrame,
    background: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    repetitions, baselines = [], []
    for seed in config["sample_seeds"]:
        sample = training.sample(n=config["sample_size"], random_state=seed)
        values, baseline, _ = attributions(
            contracts,
            bundle,
            sample,
            background,
            permutations=config["permutations"],
            seed=config["path_seed"] + seed,
        )
        repetitions.append(np.abs(values).mean(axis=0))
        baselines.append(baseline)
    measured = np.asarray(repetitions)
    return {
        "method": config["method"],
        "output": config["output"],
        "population": "training encounters; descriptive, not generalization",
        "sample_size_per_repeat": config["sample_size"],
        "seeds": config["sample_seeds"],
        "baselines": baselines,
        "features": [
            {
                "field": field,
                "mean_absolute_contribution": float(measured[:, index].mean()),
                "repeat_min": float(measured[:, index].min()),
                "repeat_max": float(measured[:, index].max()),
                "repeat_values": measured[:, index].tolist(),
            }
            for index, field in enumerate(training.columns)
        ],
        "limitations": LIMITATIONS + " Repeat ranges are not confidence intervals.",
    }
