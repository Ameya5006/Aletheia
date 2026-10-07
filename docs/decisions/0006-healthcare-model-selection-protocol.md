# ADR 0006 — Healthcare modelling, calibration and holdout protocol

Status: implemented for Macro Milestone 2; external review pending.

## Context and choice

The frozen UCI 296 cohort contains repeated encounters per patient and about 11% early readmissions. A row-random CV would put related encounters on both sides of a fold. A single held-out score used during tuning would cease to be an independent check. We therefore use five outer and three inner `StratifiedGroupKFold` folds with fixed seeds. Inner folds select bounded hyperparameters; outer folds estimate candidate and calibration behavior. All learned preprocessing is inside each fitted pipeline. Only after two deterministic training-only calculations agree is a winner frozen and the locked holdout claimed once.

The candidate families are a prevalence dummy, L2 Logistic Regression, bounded Random Forest, and bounded Histogram Gradient Boosting. The first two give a no-signal reference and a compact linear model; the trees test nonlinear effects. We use median imputation and scaling for eight quantitative fields, and constant imputation plus one-hot encoding for five categorical fields. Unknown categories receive an all-zero block and are documented as such. Histogram boosting gets a separate dense fold-local representation with a byte-budget check. This avoids silently densifying a large matrix.

Histogram boosting has `early_stopping=False`. Its automatic internal validation is row-level on a large dataset and would violate the patient-group rule even when outer and inner folds are group-aware. A first training-only attempt was stopped before selection or holdout access when this default was found; the constructor and an explicit test now enforce the policy.

Average precision is primary because the positive outcome is uncommon. An AP difference at most 0.005 is treated as practically tied, then lower Brier score, higher ROC-AUC and lower log loss decide. The rule is frozen in the versioned config. Balanced accuracy, recall, specificity, precision and F1 are also reported at descriptive threshold 0.5. This rule trades a negligible ranking gain for materially better probability quality; it is not a clinical utility function.

Sigmoid calibration fits a two-parameter logistic mapping to out-of-fold base probabilities from patient-disjoint training folds. Each outer validation fold sees a base model and calibrator fitted entirely from its outer training patients. Final calibration similarly uses only full-training groups. Calibration diagnostics and discrimination are recorded for raw and calibrated output. A calibration fit cannot prove that probabilities will be reliable at another hospital or time.

The selection record includes the exact chosen family, final inner-selected hyperparameters, calibration method, config hash and nested-evidence hash. It is exclusively created before final fitting. A local joblib artifact is loaded only after project-directory, SHA-256, protocol and package-version checks. Joblib is executable serialization, so untrusted or user-supplied files are never accepted. The evaluator verifies identities and the frozen selection, creates an exclusive holdout claim before prediction, and refuses subsequent evaluation. A failed evaluation leaves the claim in place for supervisor review rather than automatically retrying.

The evaluator also reads the saved nested-CV record and refuses missing
families, outer folds, inner-grid entries, inner folds, summaries, or a mismatched
deterministic checksum. It checks that the frozen protocol's configuration and
evidence hashes match those saved records. An interrupted training calculation
without a complete published record cannot be promoted to selection or holdout
evaluation. This guard was added during interrupted-run recovery without
changing the experiment design.

The completed training-only comparison selected sigmoid-calibrated Histogram
Gradient Boosting: outer mean AP 0.199591, mean Brier 0.097624, and final
training-only choice of 15 leaves, 30 iterations and minimum leaf size 40.
The single held-out AP was 0.202633 and Brier 0.098255. Its 0.5-threshold
recall was only 0.005357, so the ranking result must not be recast as a useful
clinical alert rule. During final evaluation the strengthened guard initially
refused before claiming the holdout because sorted JSON family keys changed the
order of selection option lists. Canonical candidate-order enumeration fixed
that serialization mismatch; the saved evidence, selection and artifact passed
checksum checks before the guarded evaluation resumed. No selection rule,
candidate, or held-out score was changed by this recovery.

## Alternatives and trade-offs

Row-level CV was rejected for patient leakage. A single training/validation split wastes evidence and hides variability. Isotonic calibration was deferred because its flexible mapping can overfit limited positive events; sigmoid is bounded and easier to reproduce. SMOTE changes the observed class distribution and complicates probability interpretation. Accuracy and a tuned threshold were rejected as selection criteria without clinical cost evidence. A fully sparse histogram input is unsupported by this estimator; the checked dense branch adds memory cost. The model set and grids are deliberately small enough for an 8 GB Windows laptop, so they cannot claim exhaustive optimization.

Reconsider this decision if a clinically reviewed richer feature policy, external hospital/time data, validated operational cost function, or stronger hardware becomes available. Any such change needs a new experiment identity and a new independent holdout; this locked holdout cannot be recycled for tuning.
