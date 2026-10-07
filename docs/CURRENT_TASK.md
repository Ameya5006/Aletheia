# CURRENT TASK

## Macro Milestone 2 — Leakage-Safe Healthcare Modelling, Calibration, and Locked Holdout Evaluation

## Supervisor Decision

Macro Milestone 1 passed external review at commit:

`9073c4531bcd01f70050450425c2e25b8b508abb`

This task authorizes healthcare modelling only under the protocol below.

Do not begin XAI, counterfactual generation, fairness measurement, similar-case retrieval, MLflow services, API, UI, database, Docker, CI/CD, deployment or monitoring.

## Required Starting State

Before editing:

- branch must be `main`;
- `HEAD` and local `origin/main` must both equal  `9073c4531bcd01f70050450425c2e25b8b508abb`;
- Git status may contain only the user modification to `docs/CURRENT_TASK.md`;
- `stash@{0}: wip: credit research core before healthcare realignment` must remain present;
- do not apply, pop, drop or modify the stash;
- no raw data, generated artifact, cache or temporary output may appear in Git status.

Stop if these conditions do not hold.

## Objective

Build a reproducible healthcare modelling pipeline that:

1. uses only the verified healthcare training partition for development;
2. preserves patient groups in every validation fold;
3. fits preprocessing only on fold-training rows;
4. compares a dummy baseline, regularized logistic regression and bounded nonlinear tree models;
5. performs bounded hyperparameter selection using nested patient-group-aware CV;
6. evaluates uncalibrated and sigmoid-calibrated probabilities without leakage;
7. freezes the selected model and calibration protocol before accessing the locked holdout;
8. evaluates the locked holdout exactly once;
9. reports discrimination, calibration, classification and uncertainty evidence;
10. creates a reproducible manifest, checksum-bound trusted-local model artifact and model card;
11. updates the report with complete interview, viva, failure and recovery material.

This is an educational research result, not clinical validation.

## Non-Negotiable Data Boundary

Use the existing:

- UCI 296 source identity;
- eligible 99,343-encounter cohort;
- frozen 13-predictor policy;
- `readmitted_30d` target;
- `patient_nbr` grouping;
- locked 79,808/19,535 train/holdout partition;
- split membership checksum;
- existing feature, target and split versions.

Do not alter the frozen dataset, target, cohort, feature roles or split lock.

The 13-feature policy is the conservative baseline policy, not a claim that richer clinically reviewed policies could not perform better.

## Holdout Protection

The locked holdout must not influence:

- model candidates;
- hyperparameters;
- preprocessing;
- calibration method;
- feature selection;
- model selection;
- threshold selection;
- stopping decisions;
- retry decisions.

Implement a programmatic evaluation guard.

Before any held-out prediction:

1. complete all training-only nested-CV results;
2. select the winning protocol using only training evidence;
3. create and persist an immutable selection record;
4. verify dataset, feature-policy, target and split identities;
5. verify the selected protocol checksum;
6. refuse evaluation if the holdout has already been evaluated for that experiment identity.

Perform one held-out evaluation only after these conditions pass.

Do not rerun the holdout merely because its result is disappointing.

## Cross-Validation Protocol

Use deterministic patient-group-aware splitting.

Required outer evaluation:

- `StratifiedGroupKFold`;
- five folds;
- shuffle enabled;
- seed 42;
- every patient entirely contained in one fold;
- both classes required in every validation fold.

Required inner selection:

- `StratifiedGroupKFold`;
- three folds;
- deterministic seed derived from the frozen experiment seed;
- only the outer-training partition may enter inner selection.

Tests must prove patient disjointness for every inner and outer fold.

If the installed scikit-learn API cannot implement this exactly, stop and document the incompatibility rather than silently substituting row-level splitting.

## Preprocessing

Build preprocessing from the frozen semantic types:

- eight quantitative predictors;
- five categorical predictors;
- explicit missing/unknown handling;
- categorical codes treated as categorical, never continuous quantities;
- one-hot encoding with unknown-category refusal or an explicitly documented safe policy;
- numeric transformation/scaling selected and documented;
- all learned preprocessing fitted only within the relevant training fold;
- stable raw-to-transformed feature mapping;
- identifiers, target, audit-only and excluded fields must never enter the model matrix.

Do not fit any data-derived transformation on the complete training partition before cross-validation.

## Candidate Models

At minimum compare:

1. `DummyClassifier` using the training prior;
2. regularized Logistic Regression;
3. Random Forest;
4. Histogram Gradient Boosting, if compatible with the approved preprocessing and laptop limits.

Use bounded, versioned hyperparameter grids. Keep the search small enough for the 8 GB Windows laptop but large enough to compare meaningful regularization, class weighting and model complexity.

Do not use:

- deep learning;
- unbounded AutoML;
- SMOTE or synthetic oversampling;
- arbitrary feature elimination;
- the locked holdout for early stopping;
- the old credit WIP stash as implementation.

Every stochastic estimator must use an explicit seed.

If Histogram Gradient Boosting cannot consume the chosen transformed representation safely, document and test a separate compatible fold-local transformer or exclude it with evidence. Do not densify an unexpectedly large matrix without a memory check.

## Model Selection

Primary selection metric:

- average precision.

Required secondary metrics:

- ROC-AUC;
- balanced accuracy;
- adverse/positive recall;
- specificity;
- precision;
- F1;
- log loss;
- Brier score.

Record:

- per-fold values;
- mean;
- standard deviation;
- training-versus-validation evidence;
- class support;
- fit and prediction time;
- convergence warnings;
- selected hyperparameters.

Use ROC-AUC, Brier score and log loss as documented tie-breakers/guards. Do not select a worse-calibrated model solely for a negligible average-precision improvement without documenting the trade-off.

Accuracy must not be used as the primary metric.

## Calibration

Evaluate raw and sigmoid-calibrated probability outputs using only training groups.

Calibration must be trained using precomputed patient-disjoint folds. Record:

- Brier score;
- log loss;
- calibration curve data;
- calibration intercept and slope where valid;
- discrimination before and after calibration.

Do not use the locked holdout to select whether calibration is applied.

Treat threshold `0.5` as descriptive only. Do not claim it is a clinically approved decision threshold.

## Final Training and Holdout Evaluation

After freezing the selection record:

1. fit the selected preprocessing/model/calibration protocol using only the full training partition and patient-group-aware calibration folds;
2. save a trusted-local artifact under an ignored artifact directory;
3. record its SHA-256, Python/package versions and exact protocol identity;
4. reject loading artifacts whose checksum or recorded versions do not match;
5. generate held-out probabilities exactly once;
6. publish one immutable evaluation record.

Held-out reporting must include:

- ROC-AUC;
- average precision;
- balanced accuracy;
- recall;
- specificity;
- precision;
- F1;
- log loss;
- Brier score;
- calibration evidence;
- confusion matrix at descriptive threshold 0.5;
- class and patient counts.

Compute 95% uncertainty intervals by seeded patient-cluster bootstrap so repeated encounters from one patient remain together. Document bootstrap repetitions and seed.

Do not report only encounter-level bootstrap intervals.

Do not inspect individual held-out explanations, fairness groups or counterfactuals in this milestone.

## Experiment and Artifact Contract

Create a versioned experiment configuration containing:

- dataset identity and raw hash;
- cohort version;
- feature-policy version;
- target version;
- split version and membership checksum;
- CV methods, folds and seeds;
- preprocessing specification;
- candidate models and bounded grids;
- calibration protocol;
- primary/secondary metrics;
- selection rule;
- bootstrap protocol;
- software versions.

Create immutable manifests for:

- training-only nested-CV evidence;
- frozen model selection;
- final fitted artifact identity;
- one-time held-out evaluation.

Generated models and run outputs must remain ignored and must not appear in Git status.

Never load an untrusted user-supplied pickle/joblib artifact. If joblib is used, document that it is restricted to checksum-verified project-generated local artifacts.

## Required Documentation

Update:

- `README.md`;
- `docs/ARCHITECTURE.md`;
- `docs/EXECUTION_PLAN.md`;
- `docs/PROJECT_REPORT.md`;
- `docs/SUPERVISOR_HANDOFF.md`.

Create:

- one ADR for the healthcare modelling, calibration and holdout protocol;
- one healthcare model card.

`PROJECT_REPORT.md` must explain:

- preprocessing and feature meanings;
- patient-group nested CV;
- model candidates and hyperparameters;
- class imbalance;
- metrics;
- calibration;
- selection reasoning;
- holdout governance;
- overfitting evidence;
- uncertainty;
- exact results;
- limitations;
- every problem encountered, failed attempt, cause and fix;
- important code locations and tests;
- interview explanations and follow-up questions;
- why results are not clinical validation.

Never fabricate a result, bug, metric or experiment.

## Authorized Paths

Codex may modify:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/EXECUTION_PLAN.md`
- `docs/PROJECT_REPORT.md`
- `docs/SUPERVISOR_HANDOFF.md`
- `src/aletheia/domains/healthcare/__main__.py`

Codex may create:

- `configs/experiments/healthcare_model_v1.toml`
- `docs/decisions/0006-healthcare-model-selection-protocol.md`
- `docs/model_cards/healthcare_readmission_v1.md`
- `src/aletheia/domains/healthcare/modeling.py`
- `src/aletheia/domains/healthcare/evaluation.py`
- `src/aletheia/domains/healthcare/experiment.py`
- `tests/healthcare/test_modeling.py`
- `tests/healthcare/test_experiment.py`
- generated ignored artifacts under existing ignored artifact paths

Codex may modify another existing source/test file only if strictly required and must stop first to explain why.

Codex must not modify `docs/CURRENT_TASK.md`.

No dependency file may change unless an unavoidable incompatibility is found. Stop and report before changing dependencies.

## Required Verification

Run:

1. `python -m pip check`
2. `python -m ruff check .`
3. `python -m ruff format --check .`
4. targeted healthcare modelling tests
5. complete offline test suite
6. deterministic repeat of the training-only experiment
7. manifest/result equality checks
8. artifact checksum/load refusal tests
9. holdout one-time-evaluation refusal test
10. `git diff --check`
11. `git status --short --untracked-files=all`

Use ignored Windows-safe temporary directories.

No raw dataset, cache, model binary, experiment output or temporary file may appear in Git status.

## Expected Final Git Status

Expected modified files:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/CURRENT_TASK.md` — user-owned task replacement only
- `docs/EXECUTION_PLAN.md`
- `docs/PROJECT_REPORT.md`
- `docs/SUPERVISOR_HANDOFF.md`
- `src/aletheia/domains/healthcare/__main__.py`

Expected created files:

- `configs/experiments/healthcare_model_v1.toml`
- `docs/decisions/0006-healthcare-model-selection-protocol.md`
- `docs/model_cards/healthcare_readmission_v1.md`
- `src/aletheia/domains/healthcare/modeling.py`
- `src/aletheia/domains/healthcare/evaluation.py`
- `src/aletheia/domains/healthcare/experiment.py`
- `tests/healthcare/test_modeling.py`
- `tests/healthcare/test_experiment.py`

Stop if additional tracked or untracked files are required or appear.

## Final Response

Report:

1. milestone status;
2. starting commit;
3. training and held-out population;
4. preprocessing;
5. CV design;
6. candidates and hyperparameters;
7. calibration protocol;
8. training-only results;
9. selection decision;
10. frozen selection identity;
11. held-out metrics and patient-cluster confidence intervals;
12. overfitting analysis;
13. one-time holdout protection evidence;
14. artifact and manifest identities;
15. tests and exact results;
16. files created;
17. files modified;
18. problems encountered and fixes;
19. limitations;
20. what the user should understand;
21. confirmation that XAI/application work did not begin;
22. confirmation that the stash was untouched;
23. confirmation that Codex did not commit or push;
24. exact final Git status;
25. recommended commit message.

Recommended commit message:

`feat: establish calibrated healthcare model`

## Stop Rule

Stop after Macro Milestone 2.

Do not begin:

- XAI explanations;
- SHAP;
- counterfactuals;
- stability;
- fairness;
- similar-case retrieval;
- MLflow service integration;
- API;
- frontend;
- database;
- Docker;
- CI/CD;
- deployment;
- monitoring;
- code-graph implementation;
- or another milestone.

Do not commit or push.