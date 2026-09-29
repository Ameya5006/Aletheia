# Aletheia — Project Report

## Project Overview

Aletheia is an Explainable AI (XAI) decision-auditing project for
structured classification in high-stakes contexts. Credit/loan risk is the
reference use case: it makes individual decisions and recourse understandable,
but does not make this a banking product. Intended users are an ML engineer or
data scientist comparing experiments and a risk analyst reviewing a prediction;
an administrator role is a later extension.

This is not a normal prediction dashboard. A dashboard can show a class and
probability. Aletheia's purpose is to compare predictive models using
performance *and* auditable evidence: global/local explanations, constrained
counterfactuals, explanation stability, and, only when valid data exists,
measured subgroup differences. It will not certify lending decisions, prove
causality, prove fairness, replace a human reviewer, or claim a new XAI method.

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

**Established scope:** South German Credit is externally supervisor-approved as
suitable for the academic Research MVP, and the Phase 2 research-first modular
monolith architecture is externally approved. Phase 3 implements the bounded
data foundation and is pending external supervisor review. These facts do not
establish model performance, calibration, fairness, stability, production
suitability, or modern-lending validity. No model, experiment metric,
application, or deployment exists. Deep learning is optional, not central.

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
`docs/CURRENT_TASK.md` authorizes exactly one bounded task and cannot override
the project's safety, ML-validity, evidence, or governance rules. The current
authorization is Phase 3's data foundation only. Its completion does not
authorize preprocessing, modelling, XAI, or application work; every later
milestone remains blocked pending external review and a replacement task. This
distinction prevents a broad vision from being mistaken for implementation
permission.

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

**Primary:** For a documented tabular credit-risk classification dataset, how do
selected model families trade predictive performance against interpretability,
local-explanation stability, and—where valid subgroup data exists—measured
group disparities needed for a human-auditable workflow?

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

These are planning questions, not empirical conclusions.

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

## Decisions to Finalize Before Modelling and Later Work

Phase 2 selects a research-first modular monolith, Python 3.12, pandas,
scikit-learn, standard TOML/JSON configuration/artifacts, pytest, Ruff,
Matplotlib/Markdown reporting, and an immutable local run-store concept. Phase
3 verified and pinned the subset it uses: Python 3.12.10, pandas 3.0.5,
scikit-learn 1.9.0, pytest 9.1.1, Ruff 0.16.6, pip 26.2.1, setuptools 84.0.0,
and the transitive packages in `requirements.lock.txt`.

Before modelling, later approved work must retain the Phase 3 `bishkred`
exclusion and prediction role set; choose categorical/ordinal encoding and CV
folds; predeclare the primary metric, threshold rule and error-cost
interpretation; bound model search; and approve serialization. SHAP and a small
custom counterfactual search are provisional. DiCE, FastAPI, frontend
frameworks, MLflow, databases, Docker, deployment, authentication, and enterprise
infrastructure remain deferred or unselected.

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

The proposed components, inputs/outputs/callers/prohibitions, failure modes,
tests, technology matrix, and diagrams are in docs/ARCHITECTURE.md. The major
decision and alternatives are recorded in
docs/decisions/0001-research-first-modular-monolith.md. Those documents remain
architecture evidence; the Phase 3 data subset described below is implemented.

Important planned failure boundaries are checksum/schema/category mismatch,
invalid target or forbidden feature roles, split overlap, preprocessing fitted
outside training data, incompatible pipeline artifacts, explanation/run
mismatch, invalid or absent counterfactuals, and insufficient fairness support.
Phase 3 unit/data/integration tests exercise its refusals plus target mapping
and deterministic splits. Future tests will cover transformed-feature consistency, metric fixtures,
atomic artifact publication, exact explainer association, and constraint guards.

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

## Data Flow

The implemented Phase 3 flow is: official source → temporary download → archive
size/hash verification → exact safe member read → raw size/hash verification →
atomic raw publication → strict load/schema/domain validation → explicit
adverse-target mapping → aligned feature-role views → stable row keys → locked
stratified membership. Each stage exists to prevent an unverified earlier
assumption from contaminating all later work.

The unimplemented future training flow continues with: fixed stratified
membership → fold-local preprocessing and bounded validation → final training
fit → one held-out evaluation → predeclared XAI/audit analysis → immutable run
artifacts → human-readable report. Only training folds fit transforms; the
held-out set cannot choose models or settings. Audit-only columns stay aligned
by a non-feature row key.

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
offline/live integration testing. The project can now reproduce and verify the
exact data boundary needed by a future approved baseline; Phase 4 is not
authorized.

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

## ML Experiments

No ML experiments, model metrics, or model results exist. Phase 1 performed a
structural dataset audit only; its class and subgroup counts are data facts, not
model-performance metrics.

## Important Problems Encountered

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

## Concepts Learned Through This Project

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

## Project Defence and Interview Preparation

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

## Semester Viva Preparation

**Basic:** Why can accuracy be insufficient? What is leakage? Why is raw
`kredit=0` mapped to analytical `adverse_event=1`?

**Intermediate:** Why Logistic Regression as a baseline? How do global/local
explanations differ? Why constrain counterfactuals? Why use stratification and
lock row membership before preprocessing?

**Difficult:** Why can explanations vary near a decision boundary? Why can
fairness metrics conflict? When is temporal/group-aware splitting necessary?
How would an immutable run manifest prevent result drift? Why must an explainer
identify the exact fitted preprocessor as well as the estimator? How does
canonical serialization make a membership checksum reproducible?

## Resume Evidence

Verified evidence: four official dataset candidates compared; one selected raw
file verified at 1,000 rows × 21 columns; one externally approved architecture
and ADR; 15 prediction, three audit-only, and two excluded fields under a
versioned policy; one locked 800/200 split; 49 tests comprising 48 offline tests
and one explicitly enabled live-data test; two clean Python 3.12 environments;
zero model comparisons, model metrics, implemented XAI techniques, application
tests, or deployments.

## Limitations

South German Credit is old (1973–1975), geographically narrow, contains only
granted credits, oversamples bad contracts, has no row dates or identifiers,
and uses an unknown monotonic transformation for amount. Sex cannot be recovered
cleanly from its combined field, and only 37 rows are foreign workers, so robust
fairness analysis is not currently justified. Future results remain dataset- and
method-bound. No model or production validation exists. Phase 3 does not
validate preprocessing or a model, and its fixed random split cannot measure
temporal or entity generalisation. A local artifact store has limited concurrency/querying;
cross-model explanations remain method-dependent; and dependency/version
controls reduce but cannot eliminate reproducibility risk.

## Future Work

**Useful next step, subject to approval:** external supervisor review of Phase 3
implementation, tests, locked membership, documentation, and handoff. If
approved, a replacement current task may authorize a bounded leakage-safe
baseline milestone. This report does not authorize Phase 4.

**Later extensions:** richer fairness/robustness methodology, monitoring,
deployment workflows, multi-user controls, integrations, and cloud operations.
