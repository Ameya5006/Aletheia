# Aletheia — Project Report

## Macro Milestone 1 — Healthcare realignment and evidence (2026-10-05)

**Current interpretation:** Aletheia remains a high-stakes tabular XAI platform, now demonstrated primarily with hospital readmission risk and secondarily with the approved South German Credit benchmark. The original `prompt.txt` named credit first, so the early approved phases built a credit data foundation and training-only baseline. The supervisor then selected healthcare as the flagship. Preserving credit avoids discarding tested methods and supplies a second domain against which later shared interfaces can be judged. Older credit-first wording below is historical; this section, the new ADRs, and the healthcare audit state the current scope. No healthcare model, API, UI, database, registry or deployment exists yet.

### What was built, why now, and how it works

This foundation precedes model work because a wrong target, a post-outcome field, or shared patients across train/test would make later metrics untrustworthy. The official UCI 296 archive is pinned by archive and member hashes in `configs/datasets/healthcare_uci296_v1.toml`; `foundation.py` verifies bytes before extracting exactly two flat files, strictly loads 50 ordered columns, rejects count/key/target mismatches and normalizes only documented `?` tokens. It maps `<30` to 1 and `>30`/`NO` to 0, removes death/hospice discharges, creates `uci296-<encounter_id>`, and returns separate predictor/audit views. `configs/features/healthcare_uci296_v1.toml` assigns every raw field exactly one role. The CLI `python -m aletheia.domains.healthcare acquire|verify` calls these functions. Alternative loose pandas loading would be shorter but could silently alter schema or missingness; a dataset-client library would add a dependency without improving this fixed source's byte verification.

The prediction timestamp is **discharge**, after the disposition is known and before 30-day follow-up. This timing makes encounter stay/lab/medication-count values plausibly observable; real workflow timestamps remain unverified. Disposition is used only to define the eligible cohort and is then excluded from predictors because death/hospice/transfer codes make the outcome structurally different or target-adjacent. `race`, `gender`, `age` are audit-only; IDs are metadata. The initial 13 predictors are deliberately narrow. Weight is 96.86% `?`; payer/specialty and diagnosis codes have substantial missingness/high cardinality. Detailed medication fields require later timing/recourse review. This default-deny choice reduces leakage and sparse-category risk at the cost of leaving possible signal unused.

`patient_nbr` groups repeated encounters. A seeded SHA-256 threshold assigns a patient to one partition independent of outcome, then a JSON lock binds the raw dataset SHA, feature/target versions, class/partition counts and membership digest. `verify_split_lock` recomputes and refuses mismatch; `partition` checks both patient and encounter disjointness. Alternative encounter-random splitting risks entity leakage; first-encounter-only would change the cohort; group stratification might improve balance but add target-dependent selection. The observed lock has train 79,808 encounters/56,178 patients (class 0 70,734; class 1 9,074), held out 19,535/13,812 (class 0 17,295; class 1 2,240). This is approximately 80/20, and group-aware CV remains a later requirement. It is not temporal/hospital validation. No held-out outcome was used for modelling or tuning; class counts are split-integrity evidence only.

The dataset was selected because the official UCI record and Strack et al. paper give a traceable public early-readmission outcome; 101,766 encounters and repeated patients make leakage controls meaningful on an 8 GB laptop (~263 MB all-string pandas inspection). MIMIC-style data could supply dates and deeper clinical variables but adds controlled access/privacy/compute demands. UCI data are from 1999–2008, omit hospital/date identity and cannot establish clinical validity. The paper's narrower study sample is not claimed to match this cohort. See [HEALTHCARE_DATASET_AUDIT.md](HEALTHCARE_DATASET_AUDIT.md) for full source, counts, dictionary and missingness.

### System path and future boundaries

The existing credit code and manifests remain in place; healthcare lives in `src/aletheia/domains/healthcare`. Future shared experiment, XAI and serving use cases should depend on domain contracts. Selected future architecture is MLflow registry, FastAPI, PostgreSQL audit, React/TypeScript, Docker/Compose, GitHub Actions, managed deployment, monitoring, cards and RBAC. DagsHub, DVC, managed host and optional OpenRouter narration remain provisional. RunwayML is rejected. Data/version identities and secrets must be separated; public demonstrations must use synthetic/de-identified examples. Similar-case retrieval will use training cases and a versioned distance metric, not collaborative filtering. A Python/TypeScript import graph with cycle/direction checks is planned for later CI. See [DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md) for caller, artifact, alternative, security and failure details.

**Milestone order:** (1) foundation/design committed and externally reviewed, with this minor repair pending; (2) healthcare models and calibration; (3) explanations/conditional audits; (4) application/MLOps; (5) delivery/monitoring/code graph. This order prevents a polished UI from hiding invalid evidence. Only the first milestone exists as implemented work. Exact software-test evidence and unresolved questions are in the current [SUPERVISOR_HANDOFF.md](SUPERVISOR_HANDOFF.md). No healthcare ML experiment or fairness result exists.

### WIP stash reuse assessment (read-only inventory)

`stash@{0}` was inspected, never applied. Tracked changes: `docs/CURRENT_TASK.md` is obsolete task text and must be discarded, not restored; `src/aletheia/experiments/manifest.py` and `src/aletheia/ml/baseline.py` contain credit research-core changes requiring independent verification before any later reuse. Untracked stash contents: `configs/experiments/comparator_v1.toml`, `src/aletheia/ml/comparator.py`, `comparator_run.py`, `protocol.py`, `selection.py`, `tests/integration/test_comparator_pipeline.py`, `tests/unit/test_comparator.py`, and ADR 0003 are credit-comparator specific, deferred and must be re-versioned/reverified; `configs/audit/explanation_v1.toml`, `src/aletheia/xai/{__init__,audit_run,evidence}.py`, and ADR 0004 contain potentially reusable explanation ideas but require healthcare adaptation and independent verification; `configs/audit/counterfactual_v1.toml`, `src/aletheia/counterfactual/{__init__,search}.py`, and ADR 0005 are credit-constraint specific and must not be reused as clinical recourse; `configs/audit/stability_v1.toml`, `src/aletheia/stability/{__init__,metrics,perturb}.py`, and ADR 0006 have potentially generic metric/perturbation ideas but require healthcare feasibility checks. No stashed file was restored. Stashed ADR numbers do not reserve committed identifiers.

### Concepts, trade-offs and defence notes

**Observation unit versus group:** one row is an encounter, but one patient may have many encounters. Grouping by patient prevents near-related rows in train and holdout. Be able to explain why encounter uniqueness does not imply independent samples, why group CV must follow the same rule, and why this still lacks external validity.

**Target semantics and decision time:** `<30` is early readmission; `>30` is a negative for this binary question but remains distinct in raw data. At discharge, treatment summaries may exist, while follow-up outcome does not. Be able to explain why excluding a death/hospice row changes the population and why using a discharge disposition as a model predictor would be problematic.

**Missingness and role policy:** `?` is an explicit source token only in seven fields; unknown administrative labels are categories, not automatically missing. Roles are exhaustive and disjoint, so new columns fail until reviewed. Be able to explain how a fit-on-all-data imputer would leak validation information and why this milestone performs no fitted imputation.

**Stable split identity:** patient hash assignment is deterministic and label-independent; the lock verifies source/config/target and counts. It sacrifices exact stratification. Be able to explain why the held-out class counts may be checked for support without tuning a model on them, and why class balance alone cannot prove leakage absence.

**Interview prompts:** Why healthcare after credit? The supervisor changed the primary demonstration while preserving approved credit research as a benchmark. Why not the highest-accuracy model? Accuracy alone can hide class imbalance, calibration and audit limitations; no healthcare model comparison has yet happened. What is the hardest current problem? Reconciling source semantics, repeated patients and discharge-time leakage before training. How would you deploy? Through versioned core artifacts, authenticated FastAPI, PostgreSQL audit, registry and CI, all still future work. What remains before real care use? Contemporary external validation, operational timestamp proof, clinician review, privacy/security governance, prospective monitoring and regulatory assessment.

**Semester viva — Basic:** What is a row? An inpatient encounter. What is positive? `<30` readmission. **Intermediate:** Why patient-group splitting? Repeated encounters can leak patient-specific patterns. Why only seven `?` fields? Those are the observed source encodings, and normalization is contract-bound. **Difficult:** Does a random patient split test temporal transfer? No, dates are absent. Can a counterfactual medication change be called actionable? Not without clinical and temporal constraints; none is implemented.

**Resume evidence:** verified healthcare raw 101,766 encounters, eligible 99,343, 69,990 eligible patients, 50 raw fields, 13 approved predictors, one frozen split; model families, healthcare metrics, deployment status and inference latency remain unmeasured. The previously documented credit baseline evidence remains separate. **Useful next step:** only after supervisor approval, design group-aware healthcare training CV and fit preprocessing within folds. **Research extension:** external/temporal validation if a suitable lawful dataset becomes available.

### Important problems encountered in this milestone

**Python TLS retrieval failure:** direct `urllib` against the official archive failed with an expired certificate chain on this Windows environment after sandbox network permission was granted. Inspection with Windows `curl.exe -I` succeeded over verified TLS; download via `curl.exe` succeeded, and archive/member hashes were recorded. No TLS verification was disabled. The code's downloader remains fail-closed; a user with the same Python trust-store issue can place a TLS-verified official archive in ignored raw storage and use the normal verifier. Lesson: network reachability and certificate trust are separate failure modes; never bypass identity checks. A first config patch failed because new directories were absent; after creating only authorized directories, the patch succeeded. Initial code lint found long lines, fixed by Ruff formatter. No ML leakage or model failure was observed because no model was trained.

### External review repair after commit 49753d5

The external supervisor passed Macro Milestone 1 with minor fixes. The public
overview and handoff still carried pre-commit or credit-first wording, and the
healthcare tests lacked direct assertions for all six death/hospice codes,
eligible-row preservation, existing-lock overwrite refusal, and cleanup after
a rejected download. The cause was incomplete review coverage and stale
documentation, not an observed source failure. Focused synthetic, offline tests
now exercise these boundaries through `cohort`, `write_split_lock`, and a
monkeypatched `acquire`; all pass without a source or contract change. The
current overview and README identify healthcare as flagship and credit as
secondary, while the detailed credit methods below remain historical evidence.
The earlier `git diff --check` failure was a trailing blank line in user-owned
`CURRENT_TASK.md`; the user removed it before committing, and the committed
check passed. This repair's check also passes. The lesson is to test exclusion
and cleanup rules directly and to distinguish an unresolved check from a
resolved pre-commit problem. No model or later milestone was started.

## Project Overview

Aletheia is an Explainable AI (XAI) decision-auditing project for
structured classification in high-stakes contexts. Hospital readmission risk
is the primary flagship demonstration: it tests whether patient-group-safe
data, later models, and review evidence can support a defensible educational
audit. South German Credit remains a retained secondary benchmark with its
approved data foundation and training-only baseline. Intended users are ML
engineers or data scientists comparing experiments, human reviewers inspecting
predictions, and future administrators managing access and audit evidence.

This is not a normal prediction dashboard. A dashboard can show a class and
probability. Aletheia's purpose is to compare predictive models using
performance *and* auditable evidence: global/local explanations, constrained
counterfactuals, explanation stability, and, only when valid data exists,
measured subgroup differences. It will not certify clinical or lending decisions,
prove causality or fairness, replace a human reviewer, or claim a new XAI method.

## Problem Statement

Aggregate metrics can conceal opaque decision logic, unstable explanations, and
different error patterns across groups. A high-stakes prediction alone does not
show a reviewer what inputs influenced it, whether a feasible change could
alter it, or whether observed subgroups have materially different outcomes.
Accuracy alone is especially weak when classes or false-positive/false-negative
costs are imbalanced.

Aletheia will investigate performance-versus-auditability trade-offs. An
explanation is evidence about a fitted model output, not a causal or human
reason. A counterfactual changes the model output, not reality. Fairness metrics
measure selected properties, not legal compliance or universal fairness.

## Scope, Users, and Assumptions

**Established scope:** Macro Milestone 1 is committed at `49753d5` and passed
external review with this minor documentation and test repair requested. Its
healthcare dataset audit, source-bound foundation, feature roles, patient split,
and deployable design are the current flagship foundation. Earlier approved
credit phases provide the secondary benchmark, including a bounded training-only
dummy/Logistic Regression baseline. Neither domain has a deployed application;
healthcare has no trained model, and credit's training CV is not held-out or
production evidence.

**Assumptions requiring validation:** the selected data must have a clear
target, source/licence, data dictionary, sufficient observations/minority-class
support, and feature semantics adequate for realistic counterfactual constraints.
Fairness is possible only where legitimate audit attributes and adequate
subgroup support exist; protected attributes must not be inferred from proxies.
The positive class, threshold, and decision/error-cost framing cannot be chosen
before the dataset is understood.

### Permanent Vision and Current Authorization

`prompt.txt` preserves Aletheia's permanent original vision. It describes the
complete platform ambition, not permission to implement every feature now.
`docs/CURRENT_TASK.md` records the completed Macro Milestone 1 authorization;
it is not an authorization for Macro Milestone 2. The current review repair is
limited to the README, this report, the supervisor handoff, and focused
healthcare foundation tests. It leaves the frozen contracts, split, source,
dependencies, preserved credit work, and earlier metrics unchanged. Held-out
evaluation, final fitting, comparators, XAI, fairness, stability, and application
work remain outside this repair.

## Functional Requirements

The planned research prototype must:

1. preserve an approved dataset's source, licence, version, schema, and data
   dictionary;
2. validate data and create reproducible training-only preprocessing;
3. train a small predeclared model set under common split rules;
4. compare class-aware metrics, confusion matrices, and validation evidence
   without tuning on final test data;
5. produce global and selected-case local explanations, labelling native and
   post-hoc methods;
6. generate valid constrained counterfactual candidates;
7. run a predeclared explanation-stability study for selected held-out cases;
8. perform subgroup analysis only when defensible; and
9. record data version, seed, split, preprocessing, feature schema, algorithm,
   hyperparameters, environment where practical, and metrics.

An API, dashboard, database, and audit log may later present this evidence, but
are not prerequisites for answering the research question.

## Non-Functional Requirements

- **Reproducibility:** fixed seeds where supported, reproducible/recorded split
  membership, and all learned transforms fitted on training partitions only.
- **Validity and traceability:** each result names its data version, model,
  partition, metric definitions, and explanation configuration; leakage control
  takes priority.
- **Interpretability:** reports must not imply causal, stable, or fair behaviour
  that was not measured.
- **Efficiency:** work must run locally on a normal student laptop; no high-end
  GPU, cloud service, or distributed infrastructure is required.
- **Safety and privacy:** public/de-identified data only; no credentials; no
  representation that the prototype is suitable for real lending.
- **Testability:** later transformations, metrics, constraints, and experiment
  metadata should be independently testable.

## Research Questions

**Primary current question:** For the documented healthcare readmission cohort,
how can later model families trade predictive performance, calibration,
interpretability, explanation stability, and conditional subgroup evidence in a
human-auditable workflow? No healthcare model has yet been trained or compared.
The earlier credit-specific version of this question remains a secondary-domain
research record for the approved benchmark.

**Secondary:**

- Does a complex model make a material, consistent validation/held-out
  improvement over an interpretable baseline?
- For identical held-out cases, how do local explanations differ in important
  features and direction across models?
- Under small valid perturbations, how do predictions and explanations change?
- How far must mutable, bounded features move to alter a model class, and are
  those candidates plausible under documented constraints?
- If a defensible audit attribute exists, what selection-rate, error-rate,
  precision/recall, and calibration differences are measured by subgroup?

These are planning questions, not empirical conclusions. The remaining Phase 1–4
details below document the approved credit benchmark and its learning history;
their former credit-first scope and tool-selection language is historical, not
the current healthcare-first product roadmap.

## Dataset Requirements

Before selection, assess source/licence, observation unit, target meaning,
collection period, feature semantics, missingness, class distribution,
duplicates, leakage-prone/post-outcome columns, and temporal/entity structure.
The data needs adequate minority and, if applicable, subgroup support for a
defensible held-out study; the threshold for adequacy must follow inspection,
not be invented now. Synthetic data could later test software mechanics but
cannot support the study's empirical claims. Reject data with unclear
provenance/target, unusable feature semantics, likely leakage, or inadequate
support.

### Phase 1 Dataset Decision

South German Credit was selected after comparing four official UCI candidates.
Phase 1 and dataset suitability for the academic Research MVP are externally
supervisor-approved, within the limitations above.
It passed the gates for traceable provenance, CC BY 4.0 usage, explicit contract-
compliance target, corrected feature meanings, modest minority-class support,
laptop size, and constrained counterfactual semantics. The official raw file
has 1,000 granted credit contracts, 20 predictors, and target `kredit` (`0=bad`
contract compliance, `1=good`); 300 cases are bad and 700 good. The adverse
event for future evaluation is the raw `0` value and must be mapped explicitly.

Dataset audit came before architecture because the data determines target
semantics, observable feature timing, leakage controls, split feasibility,
audit-only attributes, counterfactual constraints, and the kind of XAI evidence
that can be defended. Detailed sources, hashes, computed profiles, candidate
rejections, and feature roles are in `docs/DATASET_AUDIT.md`.

The alternatives were Default of Credit Card Clients (larger and better for
potential subgroup study, but dominated by historical/lender-controlled inputs
and undocumented raw codes), the older Statlog German Credit entry (known
code-table defects), and Credit Approval (anonymized features and undefined
label meaning). For the selected data, age, combined personal-status/sex, and
foreign-worker status are proposed audit-only—not prediction—attributes;
telephone and the current-credit count `bishkred` are excluded. `bishkred` is a
default-deny decision because its safe observation cutoff is not established,
not a claim that target leakage was proved.

A future stratified random split is recommended because no dates or entity IDs
support temporal or group splitting. It cannot control undisclosed repeated
borrowers or test forward-time generalisation. Only constrained contract terms
make a limited counterfactual proof possible; immutable and historical fields
must not become recourse. Fairness analysis is not yet justified because sex is
not recoverable cleanly and the foreign-worker group has only 37 observations,
including four bad outcomes.

## Planned ML and Evaluation Strategy

**Candidate models:** Regularised Logistic Regression is the required,
interpretable baseline: fast, reproducible, and directly inspectable through
coefficients. A shallow constrained Decision Tree is an optional native
baseline: rule-like but vulnerable to instability/overfitting. Random Forest
and Gradient Boosting are principal nonlinear tabular comparators: they test
whether added flexibility is worth reduced direct interpretability. A dummy
classifier may provide a class-imbalance sanity reference. SVM, k-NN, AdaBoost,
and a small MLP are not commitments; an ANN belongs only in a later
strong-semester comparison if data and runtime justify it.

**Baseline and selection:** Complex models face the logistic baseline with the
same split and preprocessing discipline. The model cannot be chosen by accuracy
alone. After target/error costs are known, predeclare a primary class-aware
metric (possibly F1, recall, or PR-AUC), supported by ROC-AUC, precision,
recall, confusion matrices, calibration where feasible, and inference cost.

**Evaluation:** The default is a reproducible stratified train/test split with
the test set untouched until final comparison. Use stratified cross-validation
inside training data for candidate selection and only a bounded predeclared
search. Fit imputation, encoding, scaling, selection, and resampling within
each training fold. If review finds chronology or repeated entities, use
temporal or group-aware splits instead. Record seed, folds, schema,
preprocessing, algorithms, hyperparameters, library versions, and metric
definitions. This protects against target, temporal, preprocessing, duplicate,
and entity leakage.

## Explainability and Audit Requirements

**Global vs local:** Global explanations ask which inputs generally influence a
model over a stated population; native coefficients/tree structure and
permutation importance or SHAP summary evidence are candidates. They do not
explain one decision, prove causality, or prove fairness. Local explanations ask
which inputs are associated with raising/lowering output for one record relative
to a stated reference. Prefer native evidence where faithful; SHAP is a
candidate common post-hoc method. LIME is unnecessary unless it serves a defined
comparison. Post-hoc evidence depends on background data, correlation,
preprocessing, and settings.

**Counterfactual strategy:** A counterfactual is a valid, minimally changed
input that changes the *fitted model's* class. Future constraint specifications
must label features immutable (such as age/protected attributes), mutable, or
constrained mutable with ranges, categories, direction, and dependency rules.
Cost should prefer sparse, scaled-small changes. Outputs are model-recourse
candidates—not financial advice or an approval guarantee. Custom constrained
search versus a library such as DiCE remains open until licence, constraints,
reproducibility, and testing are evaluated.

**Explanation stability:** For selected held-out cases, create small valid and
plausible perturbations, recompute prediction/explanation, and report both
prediction changes and explanation similarity. Predeclare measures such as
top-k overlap/rank correlation and normalized attribution change. Cases crossing
a decision boundary are separate because identical explanations are not
expected. Perturbation size, eligible features, background data, and samples
await dataset review. This is a strong-semester feature after core MVP evidence.

**Fairness:** Only with valid audit attributes and adequate group support,
report counts, selection/positive-prediction rates, false-positive and
false-negative rates, precision/recall, and calibration where meaningful, with
uncertainty or warnings for small groups. Do not infer sensitive identity, add a
protected feature for convenience, remove one and call the model fair, or issue
a binary fairness claim. Conflicting fairness definitions and data limitations
must be explicit.

## Risks and Controls

ML risks: target/temporal/post-outcome leakage; transforms fitted outside
training data; repeated-entity leakage; class imbalance; public data not
representing real lending; misleading explanations; implausible
counterfactuals; and fragile subgroup results. Controls: semantic/source review,
leakage checks, pipeline isolation, appropriate splitting, class-aware metrics,
documented limitations, feature constraints, and conditional fairness analysis.

Engineering risks: premature dashboards/APIs/databases/MLflow/Docker,
unnecessary microservices/abstractions, experiment-result drift, XAI dependency
compatibility, misleading visuals, and future sensitive-data logging. Controls:
research-first sequencing, minimal dependencies, recorded runs, clear caveats,
and later privacy-conscious audit design.

## Scope Boundaries

The following Research MVP and semester-application boundaries describe the
earlier **credit-first phases**. The current healthcare-first capability and
tooling boundaries are in the Macro Milestone 1 record above and its ADRs.

**Research MVP:** the minimum evidence-producing ML/XAI prototype: one approved
documented dataset; leakage-safe reproducible preprocessing and splitting; an
interpretable baseline and justified nonlinear comparators; cross-validated
selection within training data; untouched held-out evaluation; global/local
explanation evidence; a constrained counterfactual proof of concept; traceable
experiment metadata; and a concise research comparison or prediction-inspection
presentation. Fairness remains conditional on legitimate audit attributes,
adequate subgroup support, and appropriate methodology.

Explanation stability remains part of Aletheia's complete research question but
is not required to complete the initial Research MVP. It is required before
claiming that the complete research question, including stability, has been
answered. Its perturbation rules, eligible features, sample selection,
background/reference data, similarity metrics, and boundary-crossing treatment
must follow dataset inspection; it is not implemented, measured, or validated.

**Semester application/demo scope:** a later usable application built only after
reliable Research MVP evidence exists. Subject to separate approval and
justification, it may add a minimal API, reviewer-facing interface, experiment
tracking or appropriate persistence, targeted tests, audit records, and local
reproducibility/containerization. FastAPI, MLflow, PostgreSQL, React/Next, and
Docker are unselected technologies. Finishing the Research MVP neither completes
the original platform vision nor automatically completes this application scope;
application features must present verified research evidence rather than conceal
weak methodology.

**Enterprise extensions:** explicitly deferred are unnecessary early
microservices, Kubernetes, RBAC, CI/CD, cloud infrastructure, approval
workflows, production monitoring, scheduled retraining, production registry,
drift/explanation-drift monitoring, real-lender integration, large deep
learning, and local LLMs.

## Decisions Finalized for the Baseline and Deferred Work

Phase 2 selects a research-first modular monolith, Python 3.12, pandas,
scikit-learn, standard TOML/JSON configuration/artifacts, pytest, Ruff,
Matplotlib/Markdown reporting, and an immutable local run-store concept. Phase
3 verified and pinned the subset it uses: Python 3.12.10, pandas 3.0.5,
scikit-learn 1.9.0, pytest 9.1.1, Ruff 0.16.6, pip 26.2.1, setuptools 84.0.0,
and the transitive packages in `requirements.lock.txt`.

Phase 4 retains the `bishkred` exclusion and 15-feature prediction role set. It
freezes two scaled quantitative fields, 13 explicitly one-hot-encoded fields,
five-fold shuffled stratified training CV with seed 42, ROC-AUC as primary,
eight supporting metrics, and threshold 0.5 for descriptive confusion metrics
only. It performs no search and stores no fitted model. Comparator search,
serialization, held-out evaluation, SHAP, counterfactual search, fairness,
stability, FastAPI, frontend frameworks, MLflow, databases, Docker, deployment,
authentication, and enterprise infrastructure remain deferred or unselected.

## System Architecture

**Externally supervisor-approved Phase 2 design:** a research-first modular
monolith. One Python research core contains small components for verified data
acquisition/loading, schema/target/feature policy, and deterministic splitting;
later approved phases may add preprocessing, model training/evaluation, audit
methods, and immutable local experiment evidence. A CLI/report adapter will
eventually compose the complete core. Future
API and UI layers may call the same use cases and load explicit validated runs;
they may not duplicate preprocessing, feature-code mapping, model inference, or
explanation logic.

Dependencies point from delivery/orchestration toward the research modules and
simple contracts. Research code must not import HTTP, UI, database, or deployment
frameworks. The exact fitted preprocessing/model pipeline, transformed-feature
map, feature-policy version, and run hash bind training, inference, and
explanations together. Local run directories are staged, checksummed, validated,
published atomically, and never overwritten; reports consume them without
implicitly rerunning training.

The component boundaries, failure modes, tests, technology matrix, and diagrams
are in `docs/ARCHITECTURE.md`. ADR 0001 records the modular-monolith decision;
ADR 0002 records the training-only baseline protocol. The Phase 3 data boundary
and Phase 4 training-only baseline described below are implemented.

Important planned failure boundaries are checksum/schema/category mismatch,
invalid target or forbidden feature roles, split overlap, preprocessing fitted
outside training data, incompatible pipeline artifacts, explanation/run
mismatch, invalid or absent counterfactuals, and insufficient fairness support.
Phase 3 tests exercise its refusals, target mapping, and deterministic splits.
Phase 4 tests now cover transformed-feature consistency, fold-local fitting,
metric fixtures, class orientation, shared CV membership, deterministic reruns,
manifest guards, and atomic publication. Exact explainer association and
counterfactual constraint guards remain future work.

## Implemented Phase 3 Data Foundation

Phase 3 was implemented before preprocessing and modelling because every learned
step must depend on a verified dataset identity, correct label orientation,
approved features, and immutable test membership. Without this boundary, later
results could silently use different bytes, reverse the adverse class, admit an
audit/leakage-risk field, or drift to a more favourable test split.

`configs/dataset.toml` is the source identity/schema contract: official UCI and
DOI references, archive/member/raw sizes and SHA-256 digests, exact 21-column
order, row count, target mapping, category domains (including documented but
unobserved purpose code 7), and observed-only quantitative ranges.
`configs/features.toml` independently records semantic types and the versioned
role policy: 15 predictors; `famges`, `alter`, and `gastarb` audit-only;
`telef` and `bishkred` excluded; raw/derived targets; and `row_key` metadata.
Observed ranges describe this fixed file and are not future inference limits.

The main implementation paths are:

| Location | Responsibility and caller | Dependencies and important refusal |
|---|---|---|
| `config.py` / `load_dataset_contract`, `load_feature_policy` | CLI and tests load immutable value contracts | `tomllib`; refuses malformed hashes, missing tables, duplicate/overlapping fields, and incomplete role/semantic coverage |
| `data/acquire.py` / `acquire_dataset` | CLI/live test stages the official archive and atomically publishes only the approved raw member | standard HTTP/TLS, hashing, ZIP/BZIP2, paths; refuses size/hash mismatch, unsafe/missing/duplicate member, partial download, and invalid existing destination |
| `data/load.py` / `load_raw_data` | validation flow loads only checksum-verified ASCII | pandas plus integrity check; refuses header/order/row/token drift and creates source-position keys rather than using pandas index |
| `data/validate.py` / `validate_raw_data` | CLI/integration tests enforce raw invariants | explicit contract checks; refuses nulls, non-integer columns, bad keys/categories/counts, and complete or predictor-only duplicates |
| `data/target.py` / `add_adverse_target` | role/split flow preserves `kredit` and adds `adverse_event` | explicit truth table; refuses labels outside `{0,1}` |
| `data/roles.py` / `build_feature_views` | CLI creates aligned prediction/audit/excluded/target/metadata views | versioned feature policy; unknown or unassigned fields fail closed and `model_input()` returns predictors only |
| `data/split.py` / generation and verification functions | CLI creates/verifies membership; Phase 4 may later consume it after approval | scikit-learn splitter plus canonical JSON/SHA-256; refuses identity, membership, count, coverage, overlap, or checksum drift |
| `data/__main__.py` | `python -m aletheia.data` composes only acquire, validate, and split commands | calls the modules above; it exposes no preprocessing, fitting, metrics, XAI, or application command |

Acquisition writes to a temporary archive, verifies 13,130 bytes and archive
SHA-256 `0b40d40e…4551`, inspects safe ZIP names, reads only
`SouthGermanCredit.asc`, verifies 47,940 bytes and raw SHA-256
`5f363343…562f`, then atomically publishes the raw file. An existing valid file
is reused; an invalid one is refused rather than replaced. Failed staging files
are removed. Errors state the failed rule and safe identity/context without
printing records.

The raw target remains `kredit` (`0=bad`, `1=good`). `adverse_event` deliberately
inverts that coding (`0→1`, `1→0`) so the analytical positive class is the
adverse outcome. Label orientation matters because reversing it would reverse
the meaning of later recall, precision, errors, and explanations. The verified
file contains 300 adverse and 700 non-adverse rows; these are dataset counts,
not model results or source-population prevalence.

Rows receive `sgc-0001` through `sgc-1000` from one-based source position only
after raw-hash verification. The key is stable across repeated loads and all
role/split views, but `model_input()` excludes it. `StratifiedShuffleSplit`
with test fraction 0.20 and seed 42 locks 800 training and 200 test keys. The
training partition has 240 adverse/560 non-adverse rows; test has 60/140.
Stratification preserves minority-class support, while the canonical sorted
train/test-key JSON checksum
`af26b6036c6958a2dec48362fb1bfb075fca2ad7e482ed48ee7a49d7ec6d994b`
detects membership drift. The contract commits test keys only; training is the
complement, and no row-level feature or target value is stored.

This random split cannot establish temporal generalisation or entity
generalisation: the source has neither dates nor customer/account identifiers.
The locked held-out membership may not influence encoding, preprocessing,
models, metrics, thresholds, or other choices. Phase 3 creates membership only
and does not inspect model performance.

The ordinary suite uses clearly synthetic data and in-memory BZIP2 archives, so
48 tests run without network access. Boundary tests cover configuration, both
target labels, roles, forbidden model fields, acquisition and cleanup,
schema/categories/duplicates, key stability/alignment, canonical serialization,
deterministic partition counts and all split-lock rejection paths. One
explicitly enabled `live_data` integration test runs official acquisition
through locked split verification. Two clean Python 3.12 environments installed
the exact lock; the second installed Aletheia with `--no-deps
--no-build-isolation` before repeating pip, lint, format, and offline checks.

## Implemented Phase 4 Training-Only Baseline

Phase 4 comes after the data foundation because learned transforms and model
scores are meaningful only after dataset identity, target orientation, feature
roles, and split membership are fixed. Without fold-local preprocessing, each
validation fold could influence its own scaling and produce optimistic evidence.
Without a dummy reference, a learned score would lack a no-signal sanity check.

`configs/experiments/baseline_v1.toml` freezes dataset, policy, split, target,
preprocessing, model, CV, metric, and threshold choices. `config.py` validates
those values against the Phase 3 contracts. `ml/preprocess.py` constructs one
`ColumnTransformer`: `StandardScaler` handles `laufzeit` and `hoehe`, while
`OneHotEncoder(handle_unknown="error")` handles the other 13 approved fields.
Integer category codes are labels or coarse ordered bands, not justified
equal-distance quantities, so one-hot encoding is the conservative baseline.
Categories come from the approved contract, not observed full-data values; the
documented but unobserved `verw=7` therefore keeps a stable output column.

The transformed schema contains 59 columns: two scaled values and 57 indicator
columns. `expected_transformed_schema()` deterministically maps every output
name back to one of the 15 original predictors. Audit-only fields (`famges`,
`alter`, `gastarb`), excluded fields (`telef`, `bishkred`), both targets, and
`row_key` never enter the estimator matrix.

`ml/models.py` exposes exactly two unfitted choices. The dummy uses the training
fold's class prior and tests whether a learned model extracts signal beyond
prevalence. Logistic Regression uses L2 regularization, `C=1.0`, `lbfgs`, no
class weights, and `max_iter=1000`. L2 regularization discourages excessively
large coefficients; it does not make the model causal or automatically
calibrated. No hyperparameter or threshold search occurred.

`ml/evaluate.py` builds one shared `StratifiedKFold` assignment with five folds,
shuffle enabled, and seed 42. Each model/fold receives a fresh pipeline, fitted
on 640 fold-training rows and evaluated on 160 validation rows. Validation row
keys are recorded only as SHA-256 membership checksums. Class-1 probabilities
are selected by finding label `1` in `classes_`, not by assuming a column
position. `ml/baseline.py` verifies the complete Phase 3 split, selects only its
800 training keys, calculates the result twice, requires exact deterministic
payload equality, and only then publishes a manifest.

`experiments/manifest.py` records data/config/split/training/fold identities,
all fold and aggregate metrics, transformed-feature lineage, environment, Git
state, limitations, and explicit absence of held-out evaluation/fitted model.
`experiments/artifacts.py` writes and validates in a staging directory, flushes
the JSON, then atomically renames it; an existing run ID is refused. The run
directory is ignored and contains only `manifest.json`.

### Phase 4 Verification Evidence

Recovery preserved the existing configuration, source, tests, ADR, and published
run. On Python 3.12.10, the final required checks were:

```text
python -m pip check
  exit 0: No broken requirements found.
python -m ruff check .
  exit 0: All checks passed!
python -m ruff format --check .
  exit 0: 43 files already formatted
python -m pytest -p no:cacheprovider --basetemp data/processed/pytest-phase4-final -m "not live_data"
  exit 0: 66 passed, 1 deselected, 25 warnings in 6.52s
python -m aletheia.ml.baseline --raw-file data/raw/SouthGermanCredit.asc
  exit 0 in the preceding recovery: two identical calculations before publication
```

All 25 pytest warnings concern the task's explicit L2 parameter deprecation.
The ordinary integration fixture exercises synthetic predictors through CV and
manifest publication; the explicitly executed local baseline additionally
exercises verified Phase 3 loading, validation, roles, and locked membership.
Tests inspect exact feature allocation/domains, unknown-category refusal,
`verw=7`, fold-local fitting, fold coverage/disjointness, class orientation,
known metrics, model settings, deterministic reruns, manifest scope and shared
folds, and atomic publication/overwrite refusal. Inspect `tests/unit/test_*.py`
for these boundaries and `tests/integration/test_baseline_pipeline.py` for the
synthetic CV-to-manifest path.

Two fresh calculations during final recovery matched each other and the
preserved manifest exactly. A temporary in-memory evaluation guard verified two
800-row inputs, 15 predictors, and no locked held-out key. Deterministic result
payload SHA-256:
`84f5a13a12ee8a7d01df0959659deeab0f609f724869dd8cccf9fd2b8aa0bf1b`.
The run contains only `manifest.json`; its held-out flag is false and fitted-model
reference is null. `git check-ignore -v` confirms the raw file and run manifest
are ignored. `git diff --check` passes; only authorized paths appear in status.
Exact final replay and review commands are in `SUPERVISOR_HANDOFF.md`.

The manifest's Git diff checksum records its creation state, before subsequent
documentation edits. It is preserved as historical evidence rather than changed
to pretend it describes the later documentation state. Base HEAD remains
`65f83c668a4f745ffd6dc74a9e21b81cb059712c`.

### Phase 4 Repair Verification (2026-10-03)

The repaired offline integration test now calls `run_baseline()` with 1,000
synthetic raw rows and temporary dataset/configuration/split identities. The
fixture uses actual Phase 3 loading, schema validation, target mapping, feature
views, split generation, writing/loading, and verification. Only the dataset
identity provider is replaced; experiment validation, orchestration, CV,
manifest construction, and publication execute their real code. Before each of
the two evaluator calls, a guard requires exactly the complete verified set of
800 unique training keys, no verified held-out key, and aligned predictor/target
rows. The synthetic 200-key holdout crosses the old row-800 boundary, making a
prefix/suffix substitution fail. Both calculations produce identical payloads;
both models share five fold checksums. Nested manifest checks exclude held-out
results and prediction fields, retain the false held-out flag and null model
reference, and require a run containing only `manifest.json`. Republishing the
same run is refused without changing its manifest.

Verification: pip check and Ruff lint passed; format check reported 43 files
already formatted. The targeted test passed (1 passed, 10 warnings in 1.50s);
the complete offline suite passed (66 passed, 1 deselected, 25 warnings in
5.88s). Warnings are the existing approved L2 deprecation. Temporary publication
was inspected directly. No production baseline was rerun, held-out performance
calculated, or preserved metric changed. This repair is pending external review;
it supplies software-boundary evidence, not new empirical ML evidence.

## Data Flow

The implemented Phase 3 flow is: official source → temporary download → archive
size/hash verification → exact safe member read → raw size/hash verification →
atomic raw publication → strict load/schema/domain validation → explicit
adverse-target mapping → aligned feature-role views → stable row keys → locked
stratified membership. Each stage exists to prevent an unverified earlier
assumption from contaminating all later work.

The implemented Phase 4 training flow continues with: verified fixed membership
→ select the 800 training keys → create shared five-fold membership → build a
fresh preprocessing/model pipeline per fold → fit only on that fold's 640
training rows → score its 160 validation rows → calculate class-1 metrics →
repeat the complete calculation → compare deterministic payloads → publish an
immutable manifest. Every stage exists to prevent validation or held-out
information from entering a learned transform or choice. Final fitting,
held-out evaluation, XAI/audit analysis, and model serialization remain future
work requiring separate approval.

The future inference flow is: raw request → the same schema and feature policy →
the exact frozen preprocessing/model pipeline → score/prediction → optional
exact-run explanation/counterfactual → audit event → response. Inference never
refits or independently interprets source codes.

## Implementation Timeline

### Phase 0 — Project Analysis and Scope Validation

The broad enterprise proposal was narrowed before architecture/tool commitments
because dataset validity and research design must govern later work. Established:
users, requirements, research questions, data/model criteria, evaluation/XAI
boundaries, risks, MVP, and deferred work. Concepts: supervised tabular
classification, held-out evaluation, cross-validation, leakage,
intrinsic/post-hoc interpretability, counterfactuals, stability, and subgroup
measurement. Result: a coherent research scope was documented without
implementation. Phase 0 is externally supervisor-approved.

### Phase 0 Repair — Documentation and Governance Consistency Repair

This repair followed an external `FAIL — FIX BEFORE CONTINUING` finding on the
first Phase 0 attempt. It reconciles scope terminology, research-first order,
stability status, task authority, Git authority, and the measurable Phase 0
record. A Definition of Done and external approval gate matter because written
planning is only trustworthy when it names the evidence needed to advance and
does not silently authorize later work. The repair is externally
supervisor-approved.

### Phase 1 — Dataset Selection and Data Audit

**What was accomplished:** Four official UCI candidates were compared using
explicit gates, their permitted raw files were inspected outside the repository,
and South German Credit was selected and audited. Its identity,
structure, target, feature roles, leakage risks, split direction, and conditional
fairness/counterfactual feasibility were documented.

**Why this came now:** Dataset evidence is needed before architecture or
modelling so later decisions use the actual target, semantics, chronology, and
constraints rather than guesses.

**Concepts involved:** provenance and licensing, observation unit, selection
bias, outcome timing, audit-only versus prediction features, leakage review,
stratified splitting, subgroup support, and counterfactual feasibility.

**Result:** Phase 1 and South German Credit's academic Research MVP suitability
are externally supervisor-approved. The approval does not validate any future
model or real-lending use.

### Phase 2 — System Architecture, Technology Selection, and Roadmap

**What was accomplished:** A proposed research-first modular-monolith design was
documented with component contracts, dependency direction, shared
training/inference preprocessing, dataset invariants, local artifact manifests,
XAI/counterfactual/stability/fairness boundaries, a minimal technology matrix,
planned repository structure, tests/errors/security, a gated roadmap, and one
ADR.

**Why this came now:** The approved data audit supplies the target, feature
roles, split limitations, and semantic constraints needed to design correct
boundaries. Designing them earlier would have encoded guesses.

**Alternatives/trade-offs:** Notebook-centric work was rejected as the canonical
pipeline because of hidden state; a heavily layered architecture would add
ceremony; framework-first web design would couple evidence to delivery; and
microservices/MLflow/database infrastructure have no present scale or workflow
need. The modular monolith trades built-in distributed isolation and query
features for simplicity, inspectability, and one source of ML truth.

**Result:** Phase 2 was completed without implementation and subsequently
externally supervisor-approved at commit
`52be4130c8c4745c9f86f3b26a93497c3beeb2ff`.

### Phase 3 — Reproducible Data Foundation

**What was accomplished:** The fixed dataset/configuration contracts, controlled
official acquisition, strict loader/validator, explicit adverse mapping,
disjoint role views, stable keys, deterministic locked split, data-only CLI,
minimal Python package, exact dependency lock, and offline/live tests were
implemented and verified.

**Why this came now:** The approved architecture requires trustworthy data and
membership before any learned transform or estimator. This milestone turns the
Phase 1 audit into executable refusal boundaries while leaving modelling sealed.

**Alternatives/trade-offs:** Requests was unnecessary; standard-library
acquisition plus a certificate-validating Windows system fallback handled the
actual environment. Content-derived row hashes could hide duplicates or change
when values change, so transparent source-position keys were selected and bound
to the approved raw hash. Storing both partitions would duplicate information,
so the contract stores test keys and derives training as the complement. A
random stratified split preserves class support but accepts the inability to
test time/entity generalisation.

**Concepts and result:** cryptographic identity, fail-closed validation,
semantic versus storage type, label orientation, audit-only separation,
deterministic stratification, canonical serialization, dependency locking, and
offline/live integration testing. The project can reproduce and verify the
exact data boundary consumed by Phase 4.

### Phase 4 — Leakage-Safe Baseline Pipeline

**What was accomplished:** A fixed training-only experiment configuration,
explicit preprocessing schema, dummy reference, regularized Logistic
Regression, shared five-fold CV, predeclared metrics, deterministic calculation,
and immutable manifest publication were implemented and verified. The verified
local run is `baseline-v1-20261003T044245447896Z-f528b34971`.

**Why this came now:** Phase 3 had already frozen identity, label orientation,
feature roles, and the 800/200 boundary. Phase 4 could therefore establish a
simple reference without spending the held-out evidence or adding nonlinear
models. Without it, later models would have no interpretable or no-signal
comparison.

**Alternatives and trade-offs:** Fitting preprocessing once before CV was
rejected as leakage. Inferring categories from observations was rejected because
the schema would lose documented empty levels. Numeric ordinal treatment was
rejected because equal spacing is not source-supported. Search, threshold
tuning, final fitting, and held-out evaluation were deferred. One-hot encoding
expands 15 fields to 59 columns, but provides stable, explicit semantics.

**Concepts and result:** fold-local fitting, one-hot encoding, feature scaling,
regularization, stratified cross-validation, ROC-AUC, calibration-sensitive
losses, deterministic evidence, and atomic immutable publication. The project
now has a verified training-CV reference, not a final model or held-out result.
Phase 5 remains unauthorized.

### Phase 4 Repair — Verify the Locked Data Boundary

**Milestone and ordering:** External review blocked Phase 4 on a false holdout
assumption and an incomplete integration path. Repairing those checks comes
before any further modelling because passing tests must actually defend the
approved split. `tests/conftest.py` adds temporary synthetic raw/config/split
inputs; `tests/integration/test_baseline_pipeline.py` replaces direct prepared-
feature evaluation with complete `run_baseline()` orchestration and guards.

**Choice and alternatives:** Membership from the Phase 3 verified lock replaces
invented row ranges. Calling only `evaluate_models()` would leave training-row
selection untested; using real raw data would make the ordinary test dependent
on local data availability. Synthetic temporary inputs exercise the complete
path offline while accepting that they do not establish real model performance.
No architecture or dependency changes were needed. Reconsider only if a future
approved dataset/protocol changes the contract or orchestration boundary.

**Concepts and result:** Contract verification, exact set equality, row alignment,
integration testing, and immutable publication. The test now proves that all and
only verified training keys reach CV; Phase 4 still awaits supervisor approval
and Phase 5 remains blocked.

## Technical Decisions

**Research-first, not platform-first:** Data and ML/XAI evidence precede APIs,
dashboards, persistence, tracking, and deployment. Trade-off: a full-stack demo
is postponed; reconsider after reproducible results exist.

**Credit-risk tabular reference:** supports understandable audits and local
classical ML, while conclusions remain dataset-bound and not production lending
validation. Reconsider if no dataset meets the criteria.

**Logistic baseline plus limited nonlinear models:** provides a real
performance/transparency comparison without an algorithm catalogue; extend only
when another family answers a distinct question.

**Conditional fairness:** avoids proxy-based or underpowered claims, but the
first study may have no fairness result.

**Research-first modular monolith:** one package and process keep data, fitted
pipeline, evaluation, and audit evidence consistent while future delivery
adapters depend on the core. The accepted trade-off is fewer built-in
concurrency/scale boundaries; reconsider only when real workload, team, or
deployment evidence requires them.

**Immutable local experiment artifacts before MLflow/database:** a versioned
JSON manifest and checksummed run directory are sufficient for inspectable
single-user research. Reports name exact runs and never trigger training.
Reconsider when concurrent users, remote storage, query volume, or approval
workflows appear.

**Locked test membership before modelling:** test row keys are committed once
and tied to the raw hash, role-policy version, target mapping, split parameters,
class counts, and canonical membership checksum. A fresh random split was an
alternative, but it could permit accidental split shopping or drift. The cost
is that a later authoritative data revision needs an explicit new contract.

**Training-only baseline protocol:** exactly one prior dummy and one fixed L2
Logistic Regression use identical five-fold training membership and a fresh
pipeline per fold. Explicit contract categories keep the schema stable and
unknown values fail. The accepted trade-offs are a wider 59-column matrix, no
ordinal-distance assumption, no tuning, and no final fitted artifact. Reconsider
only through a new approved experiment version; ADR 0002 contains the full
decision record.

## ML Experiments

### Baseline v1 — Training-Only Cross-Validation

**Objective and identity:** Determine whether fixed Logistic Regression extracts
signal beyond a class-prior dummy without using the held-out partition. Dataset:
South German Credit raw SHA-256 `5f363343…562f`; feature policy 1.0; split
checksum `af26b603…94b`; training checksum `f528b349…53e`; 800 training rows
(240 adverse, 560 non-adverse); positive class `adverse_event=1`.

**Features and preprocessing:** 15 approved prediction features. `laufzeit` and
`hoehe` are standardized within each fold. Thirteen categorical/ordinal fields
are one-hot encoded from explicit approved domains. There is no imputation,
resampling, target encoding, feature selection, or polynomial expansion.

**Models and validation:** `DummyClassifier(strategy="prior")`; Logistic
Regression with L2, `C=1.0`, `lbfgs`, `class_weight=None`, and
`max_iter=1000`. Five-fold `StratifiedKFold`, shuffled with seed 42, supplies
the same memberships to both models. Threshold 0.5 is descriptive only.

Aggregate values are mean ± population standard deviation across five
validation folds:

| Metric | Dummy | Logistic Regression | Meaning in this experiment |
|---|---:|---:|---|
| ROC-AUC | 0.5000 ± 0.0000 | 0.7718 ± 0.0340 | Ranking of adverse above non-adverse; not calibration |
| Average precision | 0.3000 ± 0.0000 | 0.6048 ± 0.0653 | Precision-recall ranking, prevalence-sensitive |
| Balanced accuracy | 0.5000 ± 0.0000 | 0.6676 ± 0.0339 | Mean of adverse recall and specificity at 0.5 |
| Adverse recall | 0.0000 ± 0.0000 | 0.4708 ± 0.0339 | Fraction of actual adverse cases flagged |
| Specificity | 1.0000 ± 0.0000 | 0.8643 ± 0.0363 | Fraction of non-adverse cases correctly not flagged |
| Precision | 0.0000 ± 0.0000 | 0.6034 ± 0.0812 | Adverse predictions that were adverse; prevalence-sensitive |
| F1 | 0.0000 ± 0.0000 | 0.5282 ± 0.0513 | Harmonic mean of adverse precision and recall at 0.5 |
| Log loss | 0.6109 ± 0.0000 | 0.5216 ± 0.0419 | Penalizes wrong/confident probabilities; lower is better |
| Brier score | 0.2100 ± 0.0000 | 0.1715 ± 0.0167 | Mean squared probability error; lower is better |

The dummy assigns the 0.30 fold-training adverse prior, so threshold 0.5 labels
every validation row non-adverse: recall, precision, and F1 are zero while
specificity is one. Logistic Regression ranks cases materially better within
these training folds and improves both probability losses. This is reference
evidence, not final selection: no nonlinear model was compared and the held-out
200 rows were not scored.

Fold-to-fold standard deviations show variability, not a confidence interval or
guarantee. Because training-fold scores were not recorded, this experiment
cannot quantify a train/validation generalization gap and cannot diagnose
overfitting conclusively. CV variation and regularization offer limited evidence
only. The source deliberately oversamples adverse outcomes from its historical
population, so precision, average precision, Brier/log loss interpretation, and
raw probability calibration do not transfer directly to population lending.

**Error semantics and conclusion:** A false negative is an actually adverse
contract predicted non-adverse; a false positive is an actually non-adverse
contract predicted adverse. Both matter, but no defensible monetary cost ratio
exists here. Threshold 0.5 was not tuned and is not an operational lending
recommendation. The result justifies retaining Logistic Regression as the
interpretable reference for a separately approved comparator phase.

## Important Problems Encountered

### Phase 4 Integration Test Used a False Holdout Boundary

**Problem/symptom:** The original integration test invented `sgc-0801` through
`sgc-1000` as held-out keys and supplied prepared first-800-row features directly
to `evaluate_models()`. Its disjointness assertion passed without checking the
locked membership. The actual stratified lock scatters held-out keys throughout
the source file. A training-selection regression could therefore include real
held-out rows, omit training rows, and still pass that test; resulting evidence
could be contaminated without detection. Review found a test gap, not evidence
that production evaluation had leaked.

**Root cause/fix:** The test conflated stable source-row numbering with random
partition membership and bypassed the code responsible for selecting rows.
Phase 3 split-contract generation/loading/verification now supplies the expected
membership. `run_baseline()` executes raw loading → schema validation → target
mapping → role enforcement → locked split verification → training selection →
real training-only CV → manifest creation → immutable publication. A capture
guard checks set equality, uniqueness, 800 rows, held-out disjointness, and
feature/target alignment before allowing evaluation. Both synthetic partitions
cross row 800. Directly prepared predictors alone were insufficient evidence;
the real orchestration test passed targeted and full checks noted above.

**Recovery and lesson:** No source defect was exposed and no production artifact
or metric changed. An initial repair patch was rejected because two operations
targeted one file; status confirmed no changes, then separate valid updates
succeeded. A delete-based handoff rewrite failed without changing its file;
an in-place patch completed the rewrite. A later documentation patch also
failed on unmatched context and was corrected without changing earlier results.
Prevent recurrence by testing the selection boundary against verified
membership rather than plausible-looking IDs. Inspect `data/split.py`,
`ml/baseline.py`, `tests/conftest.py`, and
`tests/integration/test_baseline_pipeline.py` to explain the correction.

During Phase 1, Windows `Expand-Archive` could not extract BZIP2 entries, so
Python's standard `zipfile`
was used in the temporary audit directory. An initially guessed South German
archive URL returned 404 before the official `+update` URL was used. More
importantly, one sentence in the linked report appears to reverse the target
codes; UCI's distributed code table, R reader, and observed 300/700 counts agree
on `0=bad`, `1=good`. The lesson is to cross-check narrative documentation
against the exact distributed artifact rather than silently choosing a label.

Phase 2 identified model serialization as an architectural risk rather than
silently selecting pickle/joblib. Such formats can execute code and are not
supported across mismatched scikit-learn versions. The design therefore requires
trusted checksummed artifacts, exact environment metadata, and a later
compatibility decision between skops and a restricted local joblib fallback.

During Phase 3, Python's OpenSSL trust path rejected the official UCI HTTPS
chain as expired even after native roots were added, while Windows'
certificate-validating `Invoke-WebRequest` downloaded bytes with the approved
hash. Acquisition now tries verified Python TLS first and uses a Windows
Schannel-backed PowerShell fallback only for certificate-verification failure;
TLS verification is never disabled. This preserves the fixed URL and avoids
adding Requests/certifi for one platform-specific trust issue.

The first offline test run exposed two test/validation-order mistakes: an
archive mutation changed size before the checksum boundary could be exercised,
and aggregate target counts masked a duplicate-row refusal. The test now changes
one archive byte without changing size, and duplicate checks run before target
count arithmetic. The lesson is that a negative test must reach the exact
boundary it names, and validation order should return the most specific useful
failure.

Phase 3 also exposed several environment and governance failures. Pytest could
not create its default temporary directory under the repository on this Windows
environment; using explicit `--basetemp data/processed/...` and disabling the
cache kept temporary writes in an approved ignored path. PowerShell syntax was
initially sent to Command Prompt, producing a syntax failure rather than running
the intended check; subsequent commands named the correct shell. A stray
untracked file literally named `git` appeared in the status gate and was removed
before continuing because it was outside the approved task. These symptoms did
not change data or results. The prevention lesson is to treat the exact shell,
temporary-write location, and Git status as reproducibility inputs, not setup
details.

The Phase 3 handoff initially retained stale architecture wording that described
implemented paths as future work. A repair reconciled `ARCHITECTURE.md` with the
committed source. That repair then overclaimed quantitative-range enforcement:
the configuration loads observed ranges, but validation enforces exact file
identity through byte size/SHA-256 and does not compare general quantitative
values with those ranges. Code inspection and targeted text searches verified
the correction. The interview lesson is that a checksum proves byte identity;
it is not the same control as an explicit per-field range rule.

No meaningful Phase 4 correctness bug was found in the recovered implementation:
all offline tests passed before documentation completion and the real training-
only run reproduced exactly. The recovery did expose tooling and documentation
problems: simultaneous shell creation failed with `CreateProcessWithLogonW
failed: 1056`; sequential read-only calls succeeded. Several patches failed
because PowerShell's default decoding displayed UTF-8 symbols as mojibake, and
the copied context did not match the file. The failed patches made no changes;
explicit `Get-Content -Encoding UTF8`, fresh surrounding lines, and smaller
`apply_patch` edits resolved the mismatch within the sandbox. The user required
stopping on patch failure, and work resumed only after renewed direction.
Verification used Git diffs and whitespace checks. The lesson is to separate
display decoding from actual file corruption and inspect current text before
patching; do not bypass a failed patch with an unsandboxed write. A later inline
Python verification command also failed before running with `SyntaxError:
invalid decimal literal` because Windows PowerShell stripped nested quotes.
Transporting the code as byte values worked; a readable replay using PowerShell
`--%` then passed and is recorded in the handoff. This was shell argument
handling, not a model/data defect; no result was produced by the failed command.

Scikit-learn 1.9 emitted a deprecation warning for
the explicitly required `penalty="l2"` argument. Phase 4 preserves the approved
configuration; a later approved version must revisit the equivalent API before
scikit-learn 1.10 rather than silently changing this experiment.

## Concepts Learned Through This Project

**Contract-based integration testing:** test the real caller-to-component flow
against a verified contract, rather than preparing inputs that skip the risky
boundary. The repaired baseline test captures evaluation inputs before CV.
This matters because a correct evaluator can still receive the wrong rows.
Be able to explain why source-row identity differs from partition membership,
why set equality must be paired with uniqueness/count, and why synthetic
software evidence does not establish real-world model performance.

**Intrinsic vs post-hoc interpretability:** coefficients/rules expose model
structure directly; feature attribution estimates influence for a fitted model.
Neither proves causality. Planned in the comparison.

**Data leakage:** training gets unavailable future/target information and
evaluation becomes falsely optimistic. Prevent with training-only transforms,
untouched tests, and time/group splits where appropriate.

**Global vs local explanation:** global evidence describes general model
patterns; local evidence concerns one prediction. A global ranking cannot
explain an individual decision.

**Counterfactual:** constrained feature changes that alter a model class; not a
guarantee of a real-world outcome.

**Dataset selection before architecture:** the selected data fixes what one row
and the target mean and exposes timing, feature, fairness, and recourse limits.
Architecture designed earlier could encode the wrong target or unsupported
capabilities. Phase 1 uses this ordering without designing architecture.

**Prediction feature versus audit-only attribute:** a field may be retained to
measure subgroup behaviour without being supplied to the classifier. In the
Phase 3 policy, age, combined personal-status/sex, and foreign-worker status are
audit-only; that does not make their fairness use automatically valid.

**Modular monolith:** independently understandable modules run in one package
and process. Here it prevents unnecessary distributed infrastructure while
preserving data, ML, audit, and delivery boundaries.

**Dependency direction:** outer delivery code may call the research core, but
the core cannot import API/UI/database code. This keeps research results usable
without a web application and prevents duplicate preprocessing.

**Fitted pipeline contract:** preprocessing and the estimator form one
versioned artifact. Training, inference, and explanations identify the same
pipeline and feature map, preventing a separately reimplemented inference path.

**Immutable run manifest:** every result records its dataset hash, target/feature
policy, split, configuration, environment, code revision, artifact hashes, and
limitations. Publishing a new run instead of overwriting avoids result drift.

**Cryptographic data identity:** size catches truncation cheaply and SHA-256
binds processing to exact bytes. Phase 3 checks both archive and raw member so
the same filename cannot silently mean different data.

**Label orientation:** the numerical source code is not automatically the
analytical positive class. Here raw `0` means bad, so explicit inversion makes
`adverse_event=1`; tests preserve the truth table and original `kredit`.

**Canonical serialization:** logically identical membership must produce the
same bytes before hashing. Phase 3 sorts train/test keys and uses UTF-8 JSON with
sorted keys and no optional whitespace, then tests the exact byte string.

**Stratified holdout:** random partitioning preserves target proportions so both
partitions retain adverse cases. It improves class support but cannot substitute
for temporal or entity-aware evaluation.

**Fold-local preprocessing:** each validation fold must behave like unseen data.
Phase 4 creates a new scaler, encoder, and model for every fold, fitting them on
640 fold-training rows only. Fitting once on all 800 rows would leak validation
statistics even without using the held-out test set.

**One-hot encoding with explicit domains:** one indicator represents each
approved category instead of treating integer codes as equally spaced numbers.
Phase 4 supplies contract categories, so `verw=7` keeps a column even though the
approved file does not observe it, and unknown codes fail instead of silently
changing meaning.

**Regularized Logistic Regression:** the model combines transformed inputs into
a linear log-odds score; L2 regularization penalizes large coefficients. It is
an interpretable reference with a stable fixed configuration, not a causal model
or proof that its probabilities are calibrated.

**Feature scaling:** `StandardScaler` subtracts the fold-training mean and divides
by its standard deviation for duration and transformed amount. This prevents
their different numerical scales from distorting the L2 penalty. The fitted
statistics come only from that fold's training rows; validation uses transform
without refitting. Be able to explain why scaling categories as numeric values
would not replace one-hot encoding and why scaling before CV would leak data.

**Cross-validation and metric roles:** five stratified folds reuse training data
for five separate validation checks while keeping each check out of its own fit.
ROC-AUC measures ranking across thresholds. Average precision emphasizes adverse
ranking and is prevalence-sensitive. Recall/specificity/precision/F1 use the
descriptive 0.5 threshold. Log loss and Brier score assess probability error but
do not by themselves prove population calibration.

**False negatives and false positives:** here a false negative misses an
actually adverse case, while a false positive flags an actually non-adverse
case. Neither can be declared more costly without a defensible domain cost
model, which this historical dataset does not provide.

## Project Defence and Interview Preparation

**How do you test the held-out leakage boundary?** Capture the keys passed by
the actual orchestrator to evaluation and require exact equality with verified
training membership, uniqueness, the expected count, and disjointness from
verified holdout membership before fitting. Row numbers identify records;
they do not define a random split. Follow-up: why is disjointness alone weak?
It can miss omitted training rows; exact set equality plus row count detects
omissions and duplicates. This software test complements fold-local fit tests
and semantic feature review; it does not prove every kind of leakage is absent.

**Why is this not a prediction dashboard?** It compares performance with
explanation, constrained recourse, stability, and conditional subgroup evidence;
the interface is secondary.

**Why not highest accuracy?** Accuracy can hide class/error-cost trade-offs;
model choice needs a context-aware primary metric and audit trade-offs.

**How will leakage be prevented?** Review source semantics, split before
learned preprocessing, fit transforms only within training folds, and reserve
test data for final evaluation.

**Can it prove fairness or causality?** No; it reports bounded, dataset-specific
measurements and model-output explanations with limitations.

**Why choose South German Credit over the larger Taiwanese default dataset?**
The Taiwanese data has stronger sample and target chronology, but most useful
financial variables are historical at prediction time and its raw codes contain
undocumented categories. South German Credit has corrected, human-readable
contract features that better support the XAI and constrained-counterfactual
Research MVP, accepting age and representativeness limitations.

**What does one selected row represent?** One granted credit contract from a
1973–1975 southern German bank sample. It is not a rejected application, so the
data has historical screening/selection bias.

**Why use stratified random splitting?** The target is 70/30, but the file
has no dates or entity identifiers needed for temporal/group-aware splitting.
Stratification preserves class support; it cannot solve undisclosed repeated-
borrower or forward-time generalisation risks.

**Why a modular monolith instead of microservices?** The current research is
single-user and laptop-bound. Networked services would add contracts,
deployment, and failure modes without answering the research question. Small
modules in one Python package give testable boundaries and one source of ML
truth.

**How do training and inference stay consistent?** Both use one checksummed
fitted preprocessing/model pipeline and the same schema/feature-policy contract.
Inference may transform and predict but must never refit or recreate encodings.

**Why not start with MLflow, a database, or FastAPI?** Immutable local manifests
already provide the traceability the Research MVP needs. Those tools become
useful only when approved workflows require querying, concurrency, serving, or
lifecycle management.

**How are audit-only attributes kept out of predictions?** The versioned
feature policy creates disjoint model and audit views joined only by a stable
row key. Construction fails if audit-only, target, excluded, or unresolved
columns enter the model matrix.

**What should be inspected for Phase 2?** docs/ARCHITECTURE.md contains the
complete design, docs/decisions/0001-research-first-modular-monolith.md records
the decision trade-offs, docs/EXECUTION_PLAN.md contains the gates, and this
report is the concise defence record.

**Why verify both the archive and extracted raw file?** Archive identity proves
the downloaded package is approved; raw identity proves the exact member passed
to the loader is also approved. Both checks happen before publication.

**Why invert `kredit` into `adverse_event`?** The source uses `0` for bad and
`1` for good. Evaluation normally treats `1` as the event of interest, so an
explicit derived column prevents later metric-orientation errors while keeping
the source label traceable.

**Why exclude `bishkred`?** Its definition includes the current credit, but the
source does not establish when the count was recorded. Default-deny exclusion
avoids an unsupported availability assumption; it does not prove leakage.

**How is accidental test-split drift detected?** Verification regenerates the
seed-42 stratified membership and checks test keys, complement coverage, class
counts, dataset/policy/mapping identity, and canonical SHA-256.

**Does the fixed split prove future or customer-level generalisation?** No. The
source lacks dates and entity IDs, so it supports neither a temporal test nor a
grouped-by-customer test.

**Why one-hot encode the ordinal-looking integer fields?** Their source codes
represent categories or coarse bands; equal numeric distance is not established.
One-hot encoding avoids imposing that assumption and explicit domains keep all
59 transformed columns stable.

**How do you prove preprocessing stayed inside each fold?** Each fold constructs
a fresh `Pipeline(ColumnTransformer, estimator)`. Tests spy on both
`StandardScaler.fit` and `OneHotEncoder.fit` and observe ten fits of 80 rows in a
100-row synthetic test: five folds for each of two models, never a full-data fit.
The real protocol analogously fits 640 of 800 rows per fold.

**Why compare a dummy with Logistic Regression?** The prior dummy exposes what
class prevalence alone achieves: ROC-AUC 0.5 and no adverse predictions at the
0.5 threshold. Logistic Regression tests whether the approved features add
ranking signal while remaining a simple interpretable baseline.

**Why is ROC-AUC primary, and what does it miss?** It compares ranking over all
thresholds and is less tied to one 0.5 cutoff. It does not prove probability
calibration, choose an operational threshold, encode error costs, or remove the
dataset's prevalence limitation.

**What overfitting conclusion can Phase 4 support?** Only that validation scores
vary across five fold-local fits. Training scores were not recorded and the
held-out partition remains sealed, so a train/validation gap and final
generalization cannot be claimed.

**How is the run reproducible and auditable?** The ignored manifest records
dataset/config/split/training/fold checksums, model/preprocessing/CV settings,
per-fold and aggregate metrics, transformed lineage, environment, Git state,
limitations, and explicit absence of held-out evaluation or a fitted artifact.
The complete calculation ran twice and had to match before atomic publication.

## Semester Viva Preparation

**Repair questions:** Basic—does a row key specify its partition? No, the lock
does. Intermediate—why test the orchestrator? It selects the rows before CV;
testing the evaluator alone misses that boundary. Difficult—why combine exact
set equality, uniqueness, and count? Sets detect missing/extra membership but
discard duplicates, so all three checks are necessary.

**Basic:** Why can accuracy be insufficient? What is leakage? Why is raw
`kredit=0` mapped to analytical `adverse_event=1`? What does a prior dummy
predict? What do adverse recall, specificity, and precision measure?

**Intermediate:** Why Logistic Regression as a baseline? How do global/local
explanations differ? Why constrain counterfactuals? Why use stratification and
lock row membership before preprocessing? Why scale only two fields? How does
fold-local fitting prevent leakage? Why keep a column for unobserved `verw=7`?

**Difficult:** Why can explanations vary near a decision boundary? Why can
fairness metrics conflict? When is temporal/group-aware splitting necessary?
How would an immutable run manifest prevent result drift? Why must an explainer
identify the exact fitted preprocessor as well as the estimator? How does
canonical serialization make a membership checksum reproducible?
How does adverse oversampling affect probability interpretation? Why does ROC-AUC
not prove calibration? Why can CV standard deviation not diagnose overfitting
or serve as a confidence interval?

## Resume Evidence

The figures below are **secondary South German Credit benchmark evidence** from
earlier phases. The healthcare dataset and split facts are recorded in the
Macro Milestone 1 section above; no healthcare model metric exists.

Verified evidence: four official dataset candidates compared; one selected raw
file verified at 1,000 rows × 21 columns; one externally approved architecture
and two ADRs (ADR 0002 pending review); 15 prediction, three audit-only, and two
excluded fields; one locked 800/200 split; two fixed reference estimators compared
in five training-only folds; 59 transformed columns; Logistic Regression CV
ROC-AUC 0.7718 versus dummy 0.5000; 66 offline tests passed and one live-data test
deselected in the recovery check; two clean environments verified during Phase 3.
No held-out score, measured inference latency, implemented XAI method,
application, or deployment is claimed.

## Limitations

South German Credit is old (1973–1975), geographically narrow, contains only
granted credits, oversamples bad contracts, has no row dates or identifiers,
and uses an unknown monotonic transformation for amount. Sex cannot be recovered
cleanly from its combined field, and only 37 rows are foreign workers, so robust
fairness analysis is not currently justified. Future results remain dataset- and
method-bound. Phase 4 validates training CV only; no held-out or production
validation exists. Its fixed random split cannot measure temporal or entity
generalisation. No final fitted model is retained. Threshold 0.5 has no validated
operational cost basis. A local artifact store has limited concurrency/querying;
cross-model explanations remain method-dependent; and dependency/version
controls reduce but cannot eliminate reproducibility risk.

## Future Work

**Useful next step, subject to approval:** complete the external supervisor's
minor Macro Milestone 1 review repair, then await a separately authorized task.
The healthcare modelling roadmap is planned only; this report does not authorize
Macro Milestone 2 or resumption of the stashed credit comparator work.

**Research extensions:** the separately gated global/local XAI, constrained
counterfactual, stability, and conditional-fairness studies in the roadmap.
Developer Code Intelligence and System Traceability is proposed and
unimplemented, placed after core data, modelling, evaluation/XAI, and basic
application boundaries stabilize; it requires its own approved task.

**Later extensions:** richer fairness/robustness methodology, monitoring,
deployment workflows, multi-user controls, integrations, and cloud operations.
