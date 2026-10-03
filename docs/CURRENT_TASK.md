# MILESTONE

Phase 4 — Leakage-Safe Baseline Pipeline

# SUPERVISOR DECISION

Phase 3 — Reproducible Data Foundation and its architecture-state repair are externally supervisor-approved.

Approved commits:

- Phase 3 implementation: `f19f86944d24f6220a04b732968aa1377363eb23`
- Architecture-state repair: `65f83c668a4f745ffd6dc74a9e21b81cb059712c`

Phase 4 may implement only the bounded training-only baseline described below.

# GOAL

Implement and verify a leakage-safe baseline experiment using:

1. the approved 15 prediction features;
2. fold-local preprocessing;
3. a trivial dummy reference;
4. regularized Logistic Regression;
5. fixed training-only cross-validation;
6. predeclared metrics and threshold semantics;
7. a versioned experiment configuration and immutable run manifest.

Do not evaluate the locked 200-row held-out test partition.

# STARTING STATE

Before editing, verify:

1. branch is `main`;
2. `HEAD` is `65f83c668a4f745ffd6dc74a9e21b81cb059712c`;
3. `HEAD` and `origin/main` are synchronized;
4. the only working-tree change is:

```text
 M docs/CURRENT_TASK.md
```

`docs/CURRENT_TASK.md` is modified because the user installed this approved Phase 4 task. Do not modify it again.

If any additional path appears, stop without editing and explain it.

# REQUIRED READING

Read completely:

- `AGENTS.md`
- `CLAUDE.md`
- `prompt.txt`
- `docs/CURRENT_TASK.md`
- `docs/SUPERVISOR_HANDOFF.md`
- `docs/PROJECT_REPORT.md`
- `docs/ARCHITECTURE.md`
- `docs/EXECUTION_PLAN.md`
- `docs/DATASET_AUDIT.md`
- all ADRs
- `pyproject.toml`
- `requirements.lock.txt`
- all existing configuration, source and test files

Inspect the latest two commits and the complete repository tree.

# FIXED DATA AND LEAKAGE BOUNDARY

Use the approved Phase 3 contracts without changing their meanings:

- 1,000 verified source rows
- 800 locked training rows
- 200 locked held-out rows
- `adverse_event=1` is the positive/adverse class
- 15 prediction features only
- audit-only, excluded, target and metadata fields prohibited from model input

The held-out partition must not influence:

- encoding;
- scaling;
- preprocessing design;
- cross-validation;
- model configuration;
- metric selection;
- threshold choice;
- feature selection;
- interpretation;
- documentation conclusions.

Do not calculate, display, store or document held-out predictions or metrics.

Loading and verifying the Phase 3 split contract is allowed. After membership verification, Phase 4 evaluation must use only training-row keys.

# PREPROCESSING CONTRACT

Use one scikit-learn `ColumnTransformer` inside one `Pipeline`.

Quantitative prediction features:

- `laufzeit`
- `hoehe`

Apply `StandardScaler` to these features.

Treat all remaining approved prediction fields as categorical for this baseline, including fields documented as ordinal or discretized.

Use `OneHotEncoder` with categories explicitly derived from the approved dataset contract and fail on undocumented categories.

The transformed schema must remain stable even for documented but unobserved purpose code `verw=7`.

Do not:

- infer category domains from the complete dataset;
- fit preprocessing before cross-validation;
- impute values;
- resample classes;
- use audit-only fields;
- treat integer category codes as continuous magnitudes;
- add target encoding;
- add feature selection;
- add polynomial features.

Produce a deterministic mapping from transformed columns back to original features.

# MODEL CONTRACT

Implement exactly two models:

## Dummy reference

`DummyClassifier(strategy="prior")`

## Interpretable baseline

Regularized Logistic Regression with explicit fixed configuration:

- L2 regularization
- `C=1.0`
- `solver="lbfgs"`
- `class_weight=None`
- `max_iter=1000`

Do not perform hyperparameter search.

Do not add Decision Tree, Random Forest, Gradient Boosting, XGBoost, neural networks or any other estimator.

Do not fit or serialize a final production model.

# CROSS-VALIDATION CONTRACT

Use only the locked 800-row training partition.

Use:

- `StratifiedKFold`
- 5 folds
- `shuffle=True`
- `random_state=42`
- identical folds for both models

Every fold must fit its own preprocessing pipeline using only that fold’s training rows.

Record deterministic validation-membership checksums for each fold without committing feature or target values.

# METRICS AND THRESHOLD

Primary comparison metric:

- ROC-AUC

Supporting metrics:

- average precision
- balanced accuracy
- adverse-class recall
- specificity
- precision
- F1
- log loss
- Brier score

Use `adverse_event=1` consistently as the positive class.

Use probability column corresponding to class `1`.

Use threshold `0.5` only for descriptive cross-validation confusion metrics.

Do not tune the threshold.

Document:

- false negative: an actually adverse case predicted non-adverse;
- false positive: an actually non-adverse case predicted adverse;
- both errors matter;
- no defensible monetary cost ratio exists;
- threshold `0.5` is not an operational lending recommendation;
- ROC-AUC does not prove calibration;
- precision, average precision and probability interpretation are limited by the dataset’s oversampled adverse rate.

# EXPERIMENT CONFIGURATION AND MANIFEST

Create:

- `configs/experiments/baseline_v1.toml`

It must freeze:

- experiment schema/version;
- dataset identity;
- feature-policy version;
- split-contract identity/checksum;
- target mapping;
- preprocessing policy;
- model configurations;
- CV method/folds/seed;
- metrics;
- threshold;
- positive class.

Implement a small versioned JSON manifest containing at least:

- manifest schema version;
- experiment identifier;
- dataset SHA-256;
- feature-policy version;
- split membership checksum;
- training-membership checksum;
- experiment-configuration checksum;
- model configuration;
- preprocessing configuration;
- CV configuration;
- fold-membership checksums;
- per-fold metrics;
- aggregate mean and standard deviation;
- transformed feature names and original-feature mapping;
- Python and relevant package versions;
- base Git commit;
- working-tree dirty state and diff checksum;
- creation time;
- limitations;
- explicit confirmation that no held-out metric was calculated.

Generated run directories belong under `artifacts/runs/` and must remain ignored.

Publish a run atomically and refuse overwriting an existing run identifier.

Do not persist a fitted model in Phase 4.

# PROBLEMS AND RECOVERY REPORTING

Update `AGENTS.md` with a concise permanent rule requiring every meaningful milestone to update `docs/PROJECT_REPORT.md` with verified problems encountered and recovery evidence.

For each meaningful problem record:

- problem and symptom;
- affected milestone/component;
- impact;
- root cause;
- failed or incomplete attempts;
- final solution;
- why it worked;
- verification;
- prevention or future improvement;
- relevant code/files;
- interview/viva explanation.

Include environment, tooling, implementation, ML-methodology and governance problems when they affected progress, correctness or reproducibility.

Do not fabricate problems. If none occurred, say so.

Backfill the important verified Phase 3 problems, including:

- UCI certificate-chain failure and verified Schannel fallback;
- pytest temporary-directory permission failure;
- PowerShell syntax initially executed in Command Prompt;
- stray untracked `git` file detected by the status gate;
- initial failing test construction/validation ordering;
- stale architecture wording;
- confusion between checksum identity and explicit quantitative-range validation.

Keep this material concise and study-oriented.

# FUTURE CODE-GRAPH REQUIREMENT

Update `docs/EXECUTION_PLAN.md` to preserve a future milestone named approximately:

`Developer Code Intelligence and System Traceability`

Place it only after core data, modelling, evaluation/XAI and basic application boundaries are stable.

Record it as proposed and unimplemented.

Its future first version should use:

- Python `ast`;
- lightweight graph contracts;
- NetworkX or an equally lightweight internal representation only when authorized;
- JSON/GraphML export;
- pytest fixtures;
- deterministic dependency, reverse-dependency, impact and cycle analysis;
- optional visualization only after graph correctness.

Record that:

- unresolved static calls must not be presented as certain;
- code graph and ML lineage graph are separate concepts;
- no Neo4j, GraphRAG, vector database, cloud infrastructure, microservices or mandatory LLM belongs in the first version;
- implementation requires its own future approved `CURRENT_TASK.md`.

Do not implement the code graph in Phase 4 and do not add its dependencies.

# EXPECTED IMPLEMENTATION FILES

Authorized modifications:

- `AGENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/CURRENT_TASK.md` — user-owned modification only; Codex must not edit
- `docs/EXECUTION_PLAN.md`
- `docs/PROJECT_REPORT.md`
- `docs/SUPERVISOR_HANDOFF.md`
- `src/aletheia/config.py`
- `src/aletheia/contracts.py`
- `tests/conftest.py`

Authorized new files:

- `configs/experiments/baseline_v1.toml`
- `docs/decisions/0002-training-only-baseline-protocol.md`
- `src/aletheia/ml/__init__.py`
- `src/aletheia/ml/preprocess.py`
- `src/aletheia/ml/models.py`
- `src/aletheia/ml/evaluate.py`
- `src/aletheia/ml/baseline.py`
- `src/aletheia/experiments/__init__.py`
- `src/aletheia/experiments/manifest.py`
- `src/aletheia/experiments/artifacts.py`
- `tests/unit/test_preprocess.py`
- `tests/unit/test_models.py`
- `tests/unit/test_evaluate.py`
- `tests/unit/test_manifest.py`
- `tests/integration/test_baseline_pipeline.py`

If another implementation file is genuinely required, stop before creating it and explain why.

Do not modify:

- Phase 3 dataset, feature or split contracts;
- Phase 3 data modules;
- dependency files;
- `prompt.txt`;
- `CLAUDE.md`;
- `docs/DATASET_AUDIT.md`;
- ADR 0001.

No new dependency is authorized.

# REQUIRED TESTS

Test at least:

- exact preprocessing feature allocation;
- explicit category domains;
- stable output columns including `verw=7`;
- undocumented category refusal;
- targets, audit-only fields, excluded fields and row keys absent from model input;
- scaler/encoder fit only within each training fold;
- exact five-fold membership coverage and disjointness;
- identical folds for both models;
- held-out keys absent from CV inputs and metrics;
- positive-class orientation;
- known metric fixtures;
- probability column for class `1`;
- deterministic repeated results;
- dummy-model sanity behavior;
- Logistic Regression constructor configuration;
- transformed-to-original feature mapping;
- manifest required fields and cross-reference checks;
- manifest refusal of held-out metrics;
- artifact atomic publication and overwrite refusal;
- integration flow from verified Phase 3 data through training-only baseline manifest.

Tests must use synthetic fixtures unless the explicitly executed local baseline requires the verified ignored raw dataset.

No ordinary test may require network access.

# REQUIRED EXECUTION AND VERIFICATION

Use the existing Python 3.12 environment.

Run:

```text
python -m pip check
python -m ruff check .
python -m ruff format --check .
python -m pytest -m "not live_data"
```

Use Windows-compatible temporary pytest and cache directories if the repository path has permission problems.

Run the approved baseline experiment against the verified local dataset.

Run the deterministic calculation twice before publishing and compare the result payloads, excluding explicitly nondeterministic metadata such as creation time and output path.

Verify:

- only 800 training rows were evaluated;
- both models used identical five-fold membership;
- no held-out metric exists;
- no final model artifact exists;
- generated run artifacts remain ignored;
- no raw data or generated output appears in Git status.

Record exact commands and results.

# DOCUMENTATION

Update `docs/PROJECT_REPORT.md` as Aletheia’s concise technical learning, interview, viva and project-defence guide.

Explain:

- preprocessing design;
- why categorical codes were one-hot encoded;
- fold-local fitting;
- model configurations;
- dummy versus logistic purpose;
- metric meanings;
- positive-class orientation;
- threshold limitation;
- CV results;
- overfitting evidence that can and cannot be inferred;
- dataset prevalence/calibration limitations;
- implementation flow;
- important functions and files;
- tests;
- problems and recovery;
- limitations;
- likely interview follow-up questions.

Do not claim held-out, production, fairness, XAI or deployment results.

Update architecture and execution-plan status truthfully.

Replace `docs/SUPERVISOR_HANDOFF.md` with complete Phase 4 evidence.

Do not claim external supervisor approval.

# EXPECTED FINAL GIT STATUS

The final status should contain only:

```text
 M AGENTS.md
 M docs/ARCHITECTURE.md
 M docs/CURRENT_TASK.md
 M docs/EXECUTION_PLAN.md
 M docs/PROJECT_REPORT.md
 M docs/SUPERVISOR_HANDOFF.md
 M src/aletheia/config.py
 M src/aletheia/contracts.py
 M tests/conftest.py
?? configs/experiments/baseline_v1.toml
?? docs/decisions/0002-training-only-baseline-protocol.md
?? src/aletheia/experiments/__init__.py
?? src/aletheia/experiments/artifacts.py
?? src/aletheia/experiments/manifest.py
?? src/aletheia/ml/__init__.py
?? src/aletheia/ml/baseline.py
?? src/aletheia/ml/evaluate.py
?? src/aletheia/ml/models.py
?? src/aletheia/ml/preprocess.py
?? tests/integration/test_baseline_pipeline.py
?? tests/unit/test_evaluate.py
?? tests/unit/test_manifest.py
?? tests/unit/test_models.py
?? tests/unit/test_preprocess.py
```

If an additional path appears, stop and explain it before recommending a commit.

# FINAL RESPONSE

Report:

1. milestone status;
2. verified starting state;
3. preprocessing contract;
4. baseline models;
5. CV protocol;
6. metrics and threshold semantics;
7. exact CV results;
8. confirmation that held-out evaluation did not occur;
9. manifest/run identity;
10. transformed feature count and mapping;
11. tests and exact results;
12. deterministic rerun result;
13. problems encountered, failed attempts and fixes;
14. files created;
15. files modified;
16. files intentionally unchanged;
17. documentation changes;
18. future code-graph placement;
19. unresolved issues and limitations;
20. what the user should understand;
21. confirmation that Phase 5 did not begin;
22. confirmation that Codex did not commit or push;
23. actual final `git status --short --untracked-files=all`;
24. recommended commit message.

If successful, recommend exactly:

`feat: establish leakage-safe Aletheia baseline`

# STOP RULE

Stop after Phase 4.

Do not:

- inspect held-out performance;
- tune models or thresholds;
- implement nonlinear comparators;
- implement XAI;
- implement counterfactuals;
- implement stability or fairness analysis;
- implement code-graph functionality;
- build an API, UI, database, Docker setup or deployment;
- commit or push.

The user will inspect Git status, commit and push the completed attempt, and return it for independent external supervisor review.