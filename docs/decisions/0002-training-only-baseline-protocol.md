# ADR 0002: Training-Only Baseline Protocol

## Status

Implemented in Phase 4 and pending external supervisor review. This record does
not authorize held-out evaluation or a later milestone.

## Context

Phase 3 fixed the dataset, adverse-class orientation, 15-feature policy, and
800/200 membership. A first modelling result now needs a comparison that is
simple enough to inspect, prevents preprocessing leakage, and cannot be tuned
against the locked 200-row test partition. Integer category codes must not be
mistaken for continuous magnitudes, and documented but unobserved purpose code
`verw=7` must retain a stable transformed column.

## Decision

Evaluate exactly two reference models on the locked 800 training rows:

- `DummyClassifier(strategy="prior")` as the no-signal reference;
- L2 Logistic Regression with `C=1.0`, `solver="lbfgs"`, no class weights, and
  `max_iter=1000` as the interpretable baseline.

Use one `ColumnTransformer` inside each model `Pipeline`. Standardize only
`laufzeit` and `hoehe`; one-hot encode every other approved predictor using
explicit category lists from the dataset contract and reject unknown values.
Use one shared five-fold `StratifiedKFold` membership with shuffle and seed 42.
Each fold creates and fits a fresh pipeline only on its training subset.

ROC-AUC is primary. Supporting metrics are average precision, balanced
accuracy, adverse recall, specificity, precision, F1, log loss, and Brier
score. Class `1` is always adverse. Threshold 0.5 is used only for descriptive
confusion-derived metrics and is not tuned.

Publish a versioned JSON manifest atomically under ignored `artifacts/runs/`.
It records configuration/data/split/code/environment identities, fold
membership checksums, metrics, and feature lineage, but no row values or fitted
model. Calculate twice and require identical deterministic result payloads
before publication.

## Alternatives Considered

- **Fit preprocessing once before CV:** simpler and faster, but scaling would
  learn validation-fold statistics and violate the leakage boundary.
- **Infer encoder categories from training observations:** common, but would
  drop documented unobserved categories and make output shape sample-dependent.
- **Treat ordinal codes as numbers:** fewer columns, but assumes equal numeric
  distances that the source semantics do not justify for this baseline.
- **Tune Logistic Regression or the threshold:** potentially stronger CV
  scores, but would turn the first reference into a selection exercise without
  an approved search or cost model.
- **Fit and serialize a final model:** useful later for inference, but Phase 4
  is limited to training-only comparison and has no approved serialization
  decision.
- **Evaluate the held-out partition now:** would give a final estimate, but the
  approved task explicitly keeps it sealed for later frozen comparison.

## Reasons

The dummy model shows whether the learned baseline extracts signal beyond class
prevalence. Logistic Regression is CPU-light and its later coefficients can be
inspected, while regularization controls coefficient magnitude. Explicit
categories provide stable 59-column lineage. Shared folds isolate model choice
from sampling differences. The manifest creates inspectable evidence without
introducing MLflow, a database, or unsafe model persistence.

## Trade-offs

- One-hot encoding expands 15 raw predictors to 59 columns.
- Treating all non-quantitative predictors as categorical discards possible
  ordinal-distance information but avoids unjustified equal-spacing claims.
- Five-fold CV estimates training-partition variability but is not held-out,
  temporal, entity-level, or production validation.
- Threshold 0.5 may not reflect real error costs.
- The oversampled 30% adverse rate limits probability, precision, and
  average-precision interpretation.
- Explicit `penalty="l2"` satisfies the frozen protocol but scikit-learn 1.9
  warns that this parameter form will change in 1.10.

## Consequences

Phase 4 now has a reproducible reference performance record and a stable
transformed-feature map. Nonlinear comparators can be considered only in a
separately approved later task using the frozen evaluation boundary. No
held-out result, production model, XAI result, fairness result, or application
capability follows from this decision.

## When to Reconsider

Reconsider encoding, model settings, metrics, threshold, or serialization only
through a new approved experiment version. Reconsider this baseline if the
dataset, feature-policy, target-mapping, or split identity changes; never mutate
the existing `baseline-v1` evidence in place.
