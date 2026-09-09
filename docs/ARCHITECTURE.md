# Aletheia — Proposed System Architecture

## Status and Approval Boundary

**Status: proposed pending external supervisor review.**

This document is the Phase 2 design, not an implemented system. Phase 1 and the
choice of South German Credit are externally supervisor-approved only for an
academic Research MVP. That approval does not establish model performance,
calibration, fairness, explanation stability, modern-lending validity, or
production suitability.

No source package, dependency file, test, dataset, split, model, experiment,
API, database, frontend, container, or deployment exists yet. Every
implementation milestone remains blocked until a replacement CURRENT_TASK.md
authorizes it.

## Architecture Decision

Aletheia will be a **research-first modular monolith**: one small Python package
contains the evidence-producing data, ML, XAI, and experiment modules. A command
line entry point will eventually compose them. Later API and reviewer-interface
layers may call the same research use cases and load the same approved artifacts;
they may not duplicate preprocessing, feature interpretation, inference, or
explanation logic.

This is a modular monolith in dependency and deployment terms, not a claim that
every conceptual step needs a class or service. A small pure function is
preferred when it provides a sufficient boundary.

## Architecture Principles

1. **Research validity first.** Dataset identity, feature semantics, leakage
   controls, evaluation discipline, and traceable evidence precede delivery.
2. **One research core.** Training, inference, and explanations share the same
   data contracts and fitted preprocessing/model artifact.
3. **Dependencies point inward.** UI and HTTP adapters depend on stable research
   use cases; research modules never import UI, API, database, or deployment
   frameworks.
4. **Explicit contracts at risky boundaries.** Dataset schema, target mapping,
   feature roles, split identity, fitted-pipeline identity, and run manifests
   are validated and testable.
5. **Configuration is data.** Dataset policy, seeds, candidate models,
   explanation settings, and counterfactual constraints are versioned inputs,
   not hidden constants or notebook state.
6. **Artifacts are reproducible evidence.** A result must identify its exact
   data, policy, split, code revision, environment, fitted pipeline, and
   configuration.
7. **Core logic is not notebook-only.** Notebooks may explore or present results
   later, but must call package code and cannot become the canonical pipeline.
8. **No premature platform.** A filesystem artifact store is sufficient for the
   Research MVP. Databases, MLflow, web applications, containers, and
   distributed systems wait for evidence-backed need.
9. **Small, understandable modules.** Do not create generic repositories,
   dependency-injection frameworks, or interfaces without a real substitution
   or test boundary.

## System Context and Delivery Stages

~~~mermaid
flowchart LR
    UCI[Official UCI source] --> RC[Research core]
    CFG[Versioned configuration] --> RC
    RC --> RUN[Immutable local run artifacts]
    RUN --> REP[Human-readable research report]
    REVIEWER[ML engineer / reviewer] --> REP

    API[Future thin API] --> RC
    API --> RUN
    UI[Future reviewer interface] --> API

    DB[(Future persistence)] -. deferred .-> API
    MLF[MLflow / registry] -. deferred .-> RC
~~~

### Research MVP

The Research MVP is the evidence-producing core. It will verify and load the
selected data, enforce its feature policy, create reproducible split membership,
fit preprocessing only on training data, train approved candidates, evaluate
them, generate bounded audit evidence, and write versioned local artifacts.
Its success does not depend on an API, browser, database, or deployment.

### Semester Application

A later thin delivery layer may expose an explicitly approved run through an
API and reviewer-facing interface, present predictions/explanations/
counterfactuals, and record minimal audit events. It must call the research core
or consume its validated artifacts. It must never reimplement feature codes,
preprocessing, model inference, or explanation logic.

### Enterprise Extensions

Microservices, Kubernetes, RBAC, workflow engines, distributed queues,
production registries, monitoring platforms, scheduled retraining, drift
systems, cloud infrastructure, and real-lender integration are deferred. They
do not answer the current research question.

## Logical Modules and Dependency Direction

~~~mermaid
flowchart TB
    UI[Future reviewer UI] --> API[Future API adapter]
    API --> USE[Research use cases / orchestration]
    CLI[Research CLI and report adapter] --> USE
    USE --> AUDIT[XAI and audit modules]
    USE --> ML[Training, preprocessing, evaluation]
    USE --> DATA[Acquisition, validation, policy, split]
    AUDIT --> ML
    AUDIT --> CONTRACTS[Contracts and configuration]
    ML --> CONTRACTS
    DATA --> CONTRACTS
    USE --> ART[Manifest and artifact writer]
    ART --> CONTRACTS
    REP[Report generator] --> ART
~~~

Allowed direction is from delivery/composition toward research modules and
stable contracts. Contracts contain simple typed values and rules and do not
import pandas, scikit-learn, FastAPI, React, or storage systems unless a concrete
data representation genuinely requires it. Research modules may directly use
pandas and scikit-learn; wrapping those libraries is justified only around
unsafe persistence, artifact compatibility, or a method that needs multiple
implementations.

Reports read completed manifests/results; generating a report must never trigger
training. A future API selects an explicit run identifier, validates its
manifest and hashes, then calls the same inference/explanation functions. A UI
talks to that API and contains display logic only. This direction prevents HTTP
schemas, database models, or browser code from becoming a second source of truth
and prevents training/inference preprocessing drift.

## Component Responsibilities

Names below are conceptual module boundaries, not files already created.

### Data and Model Components

| Component | Responsibility; inputs → outputs | Dependencies; callers | Prohibited responsibility | Important failure modes | Planned verification |
|---|---|---|---|---|---|
| Dataset acquisition/integrity | Fetch the approved URL into a controlled raw location and verify archive/raw SHA-256; manifest → verified file reference | Standard HTTP/file/hash facilities; called by data-foundation use case | Parsing data, silently accepting a new version, or committing raw data | Network failure, checksum mismatch, partial download, unexpected archive member | Known-hash test, mismatch refusal, temporary-file cleanup, exact filename test |
| Raw-data loader | Read verified SouthGermanCredit.asc without changing meanings; verified file → raw table plus stable source-row key | pandas and dataset contract; called by schema validator | Target remapping, imputation, encoding, or feature selection | delimiter/header drift, malformed row, coercion loss | exact 1,000 × 21 shape, header, integer-token, row-key stability tests |
| Schema validator | Check columns, order/allowed categories, types, required values, and dataset identity; raw table → validated raw table | dataset contract; called after loading and at inference boundary | Learning statistics or repairing undocumented values silently | missing/extra column, unknown code, null, invalid range | valid fixture and one failure test per contract rule |
| Target mapper | Preserve raw kredit and explicitly derive adverse_event = (kredit == 0); validated table → raw target plus binary analytical target | target contract; called before splitting/evaluation | Reversing labels, choosing threshold, or exposing target to predictors | missing/unknown label, inconsistent mapping, target in feature matrix | mapping truth table, class arithmetic, target-exclusion tests |
| Feature-role policy | Produce disjoint prediction, audit-only, excluded, target, and unresolved views while retaining row alignment; validated table + policy version → role-tagged views | feature-policy contract; called by split, training, audit | Promoting audit-only/unresolved fields automatically | overlap between roles, missing role, forbidden column in model matrix | set-disjointness, exhaustive-role, forbidden-feature tests |
| Split manager | Create/load deterministic stratified membership tied to dataset hash, row keys, target and seed; role-tagged rows → train/test membership artifact | standard hashing and scikit-learn splitter; called by training orchestration | Transforming features, inspecting model performance, or temporal claims | nondeterminism, overlap, missing rows, class loss, dataset-hash mismatch | same-seed equality, different-seed identity, full coverage, no-overlap, class-support tests |
| Preprocessing | Fit declared encoders/scalers on a supplied training partition and transform other partitions with the fitted object; raw approved predictors → transformed matrix plus feature map | pandas/scikit-learn pipeline; called by CV, final fit, inference and XAI | Loading full data, deciding split, refitting during inference, treating category codes as continuous by default | unknown category, train/test fit leakage, changed column order, lost feature lineage | fit-spy boundary test, unknown-category policy, train/inference shape and feature-name tests |
| Model definitions | Construct only approved estimators from validated configuration; model config → unfitted estimator | scikit-learn; called by CV/final trainer | Loading data, preprocessing, selecting a winner, or hiding defaults | unsupported model/config, uncontrolled randomness | constructor/config/seed and interface tests |
| Training orchestrator | Coordinate declared data, split, preprocessing, candidate evaluation and final fit; run config → candidate records and final fitted pipeline | data, preprocessing, model, CV, evaluation, artifact components; called by CLI/use case | Implementing algorithms, opening held-out results early, or producing reports implicitly | incomplete config, failed component, partial artifact, test-set reuse | orchestration integration test with small fixture and call-order assertions |
| Cross-validation/bounded tuning | Evaluate predeclared candidates inside training data with preprocessing refit per fold; training rows + search config → fold results and selected config | split/preprocessing/model/metric functions; called by orchestrator | Seeing final test data or unbounded/ad-hoc searches | fold leakage, unsupported scoring, failed candidate, stochastic drift | fold-disjointness, preprocessor-per-fold, fixed-search and seed tests |
| Final model fit | Fit the selected declared pipeline once on all approved training rows; selected config + training membership → fitted pipeline | preprocessing/model components; called by orchestrator | Re-selecting based on final test or fitting audit-only attributes | config mismatch, missing rows, random-state drift | membership/config identity and forbidden-column tests |
| Held-out evaluator | Apply the frozen pipeline once to isolated test rows and compute predeclared metrics; fitted pipeline + test membership → final result record | metric functions only; called after selection/final fit | Tuning, refitting, changing threshold after inspecting results | repeat access used for tuning, label orientation error, undefined metric | one-gate access, known-confusion-matrix, adverse-label and metric tests |

### Evidence, Audit, and Delivery Components

| Component | Responsibility; inputs → outputs | Dependencies; callers | Prohibited responsibility | Important failure modes | Planned verification |
|---|---|---|---|---|---|
| Experiment metadata | Validate a complete run manifest tying data, policy, split, code, environment, model and analyses together; records → manifest | contracts; called by orchestrator/artifact writer/report/API | Inventing missing values or using mutable “latest” references | absent field, conflicting hashes, unsupported schema version | manifest schema, required-field and cross-reference tests |
| Artifact storage | Stage, checksum, validate, then atomically publish an immutable local run directory; run outputs → published run ID | filesystem/hash utilities; called by orchestrator and audit modules | Running training, overwriting a run, or loading untrusted executable artifacts | collision, partial write, checksum mismatch, incompatible library versions | atomic publish, collision refusal, incomplete-run rejection, hash verification |
| Global explanations | Produce predeclared population/model-level evidence with original-feature mapping; frozen run + allowed analysis partition → explanation artifact | exact fitted pipeline, feature map and approved explainer; called by audit orchestration | Causal claims, model selection on final evidence, or ungrouped dummy-column claims | wrong run/model, inappropriate background, correlated-feature distortion | run association, raw-feature permutation/grouping and deterministic-config tests |
| Local explanations | Explain a preselected held-out case relative to recorded training-only reference data; run + case key → local attribution artifact | exact pipeline, feature map, explainer config; called by audit/API | Explaining another model/version or presenting attribution as a human reason | row mismatch, background drift, class/output mismatch | case/run/model/output identity and additive/grouping checks where applicable |
| Counterfactual/constraint boundary | Search in original feature space, validate allowed changes and dependencies, transform with frozen pipeline, and report valid class-changing candidates or none; run + case + constraint spec → result | schema/policy, fitted pipeline, prediction function; called by audit/API | Altering immutable/audit-only/history/target fields or guaranteeing real recourse | impossible category, broken term dependency, invalid cost, no valid candidate | immutable/direction/range/dependency/class-change and no-result tests |
| Stability analysis | Repeatedly generate valid seeded perturbations for preselected held-out cases and compare prediction/explanation changes; run + stability config → stability artifact | local explanation, constraint-aware perturbation, exact pipeline; called by audit orchestration | Inventing a stable/unstable threshold or mixing boundary crossings with unchanged-class cases | invalid perturbation, nondeterminism, background mismatch, metric undefined | seed repeatability, immutable protection, metric fixtures, crossing separation |
| Conditional fairness | Guard and, only when authorized, compute subgroup support and predeclared outcome/error measures from aligned audit data; run + group definition → refusal/warning or result | row keys, test predictions/labels, audit-only view; called by audit orchestration | Passing group fields to model, inferring identities, or issuing fair/unfair verdicts | lost alignment, tiny cells, arbitrary regrouping, undefined rate | disabled-by-default, minimum-support guard, alignment and known-rate tests |
| Report/presentation adapter | Render recorded manifests and result artifacts into tables/figures/Markdown; completed run → human-readable report | artifact reader and plotting; called by CLI/reviewer | Rerunning training, recalculating hidden metrics, or hiding limitations | incomplete run, stale reference, inconsistent units | golden minimal report, missing-artifact failure, no-training-call test |
| Future API | Validate requests, select an explicit approved run, invoke research inference/audit use cases, and shape responses | research core and artifact validator; called by future UI/client | Preprocessing, model training, feature-code interpretation, or arbitrary artifact loading | invalid request, unapproved run, incompatibility, sensitive logging | API schema/integration/auth tests in a later milestone |
| Future reviewer interface | Present run, prediction, explanation, counterfactual and caveat evidence obtained from API | API contract; called by human reviewer | Computing metrics, transforming features, direct model loading, or causal/fairness claims | stale run display, mismatched evidence, misleading visualization | UI contract/accessibility/end-to-end tests in a later milestone |

## South German Credit Invariants

These are hard design inputs from the approved Phase 1 audit, not inferred model
findings.

| Invariant | Enforcement point | Required behaviour/test |
|---|---|---|
| Raw kredit 0 = bad/non-compliant; 1 = good/compliant | Schema and target mapper | Preserve raw value and test explicit adverse_event mapping |
| Target never enters predictors | Feature policy and preprocessing | Fail on any target/predictor overlap |
| Age, personal-status/sex, foreign-worker are audit-only candidates | Versioned feature policy | Keep aligned by row key; fail if supplied to model matrix |
| Telephone is excluded | Feature policy | Reject from prediction and recourse sets |
| bishkred is unresolved | Feature policy | Default deny; training cannot start while role is unresolved |
| Integer category codes are not continuous magnitudes | Schema/preprocessing contract | Declare each semantic type; encode nominal/ordinal fields deliberately |
| The 30% adverse rate is an oversampled file rate | Report validation and limitations | Prohibit wording that treats it as source-population prevalence or calibrated population risk |
| Amount is an unknown monotonic transform | Schema, reports, counterfactual constraints | Do not label as currency or compute literal financial cost |
| No row dates or entity IDs exist | Split manager and report | Permit current fixed stratified split only; record inability to test temporal/entity generalisation |
| Learned transformations fit on training data only | CV/final-fit/inference boundaries | Fit-spy tests; inference exposes transform/predict only |
| Audit rows remain aligned without becoming features | Feature policy/split/artifact contract | Stable row key and membership checks across prediction/audit views |

Because bishkred remains unresolved, the next data-foundation milestone must
either obtain defensible timing evidence or keep it excluded. It cannot silently
become a model input.

## Future Training Flow

~~~mermaid
flowchart TD
    S[Official source] --> D[Download to controlled location]
    D --> H{Archive and raw hashes match?}
    H -- no --> STOP[Refuse run]
    H -- yes --> RAW[Immutable raw file reference]
    RAW --> V[Schema and semantic validation]
    V --> T[Explicit target mapping]
    T --> P[Feature-role enforcement]
    P --> SPLIT[Fixed stratified membership]
    SPLIT --> TRAIN[Training rows]
    SPLIT --> TEST[Sealed held-out rows]
    TRAIN --> CV[Fold-local preprocessing + bounded CV]
    CV --> SEL[Select declared configuration]
    SEL --> FIT[Fit pipeline on all training rows]
    FIT --> EVAL[One held-out evaluation]
    TEST --> EVAL
    FIT --> XAI[XAI and bounded audit analyses]
    EVAL --> ART[Stage and validate run artifacts]
    XAI --> ART
    ART --> REPORT[Render human-readable report]
~~~

Acquisition, parsing, validation, target mapping, role enforcement, and split
assignment do not learn feature transformations. Split assignment may use the
target only to stratify. Each CV fold fits its own preprocessor on that fold's
training subset. After candidate selection, one pipeline is fitted on all
approved training rows. The held-out test is revealed only after the candidate,
preprocessing policy, search space, threshold rule, metrics, and audit
configurations are frozen.

The held-out partition may be transformed by the frozen pipeline, scored once,
and used for the predeclared final evaluation and audit analyses; it may not
alter model choice or preprocessing. Training-only data supplies explainer
background/reference values and scaling statistics. Audit-only columns travel
in a separate row-keyed view with identical membership so conditional audits
can join predictions without entering fit or predict.

Leakage controls occur at four gates: semantic validation rejects unavailable
fields; feature policy denies target/audit/excluded/unresolved roles; split
membership is fixed before fitting; and orchestration prevents held-out access
until the run configuration is frozen.

## Future Inference Flow

~~~mermaid
flowchart LR
    REQ[Raw request] --> SV[Schema validation]
    SV --> FP[Approved feature policy]
    FP --> PIPE[Frozen preprocessing + model pipeline]
    PIPE --> PRED[Prediction / score]
    PRED --> EX[Optional exact-run explanation]
    PRED --> CF[Optional constrained counterfactual]
    EX --> AUD[Audit event]
    CF --> AUD
    PRED --> AUD
    AUD --> RESP[Response]
~~~

Inference loads one explicitly identified, checksum-verified run. It validates
raw feature codes using the same contract as training and invokes the exact
fitted preprocessing/model pipeline; it never fits. Feature policy constructs
the model input and prevents target, audit-only, excluded, unresolved, or
unknown fields from leaking into prediction. Audit-only request values, if a
later approved use accepts them, remain separate.

Explanations identify the exact pipeline hash, output/class, original record,
transformed feature map, and training-only reference artifact. Counterfactual
candidates are changed in original feature space, revalidated, then passed
through that same pipeline. Application code must not map German codes,
reconstruct dummy columns, or load model and preprocessor separately.

## Experiment and Artifact Contract

The Research MVP will use a lightweight local filesystem store rather than
MLflow or a database:

~~~text
artifacts/
  runs/
    <run-id>/
      manifest.json
      dataset.json
      feature-policy.json
      split-membership.json
      config-snapshot.toml
      environment.json
      fitted-pipeline.<format-to-be-approved>
      validation-results.json
      final-test-results.json
      explanations/
      counterfactuals/
      stability/
      fairness/
      report.md
~~~

This is a planned contract; the directories do not exist. A run ID will combine
a UTC timestamp with a short digest of dataset hash, feature-policy version,
split identity, run configuration, and code revision. The manifest records:

- manifest schema version and run ID;
- dataset source, filename, byte size, SHA-256, and row/schema identity;
- raw and analytical target mappings;
- feature-policy version and exact role lists;
- split method, seed, membership checksum, and partition counts;
- preprocessing configuration and transformed-feature map;
- algorithms, hyperparameters, random states, and bounded search;
- Python/library/platform versions and source-control revision/dirty state;
- validation/CV and final-test results with metric definitions and partitions;
- fitted-pipeline filename, format, SHA-256, and compatibility information;
- explanation method, class/output, background/reference identity, seeds, and
  case keys;
- counterfactual constraint version, distance configuration, and failures;
- stability configuration/repeats and conditional-fairness group definitions;
- creation timestamps and known limitations.

Outputs are first written to a staging directory. Publication validates required
files and hashes, then atomically renames the directory. Existing run IDs are
never overwritten; failed/incomplete staging is not a valid run. Reports refer
to an explicit run ID and artifact hashes, never “latest.” A later API may load
only an explicitly approved, complete run whose dataset/policy/pipeline hashes
and library compatibility pass validation.

The executable serialization format remains provisional. Pickle/joblib can run
arbitrary code and is acceptable only for locally produced, trusted,
checksum-verified artifacts in an identical recorded environment. skops is a
safer candidate because it requires review of unknown types, but it adds a
dependency and still needs compatibility testing. ONNX is deferred because it
does not naturally preserve every preprocessing/XAI capability. The baseline
milestone must approve one format before artifacts are persisted.

## XAI Architecture

The architecture distinguishes:

- **Native global evidence:** logistic coefficients and a constrained tree's
  rules/structure, interpreted with preprocessing and scaling visible.
- **Model-agnostic global evidence:** permutation importance performed on
  original columns through the full fitted pipeline, using a predeclared
  evaluation partition and metric.
- **Local evidence:** attribution for a fixed held-out case, output/class,
  fitted pipeline, and training-only background/reference set.
- **Post-hoc candidates:** SHAP is provisional; LIME and partial dependence are
  deferred unless they answer a defined comparison question.

SHAP can provide additive local and aggregate evidence across linear and tree
models and currently publishes Windows/Python 3.12 support. It is not selected
solely for popularity: its explainer/model-specific semantics, background-data
dependence, correlated-feature limitations, transformed feature mapping,
runtime, and package compatibility must pass a bounded experiment first. LIME
adds stochastic local-surrogate choices and is not needed unless comparison
with SHAP becomes a research question.

The fitted preprocessor must expose a transformation map from each original
feature to its derived columns. Raw-feature permutation happens before the
pipeline. When an additive attribution method permits grouping, one-hot
contributions are grouped back to the original feature with the aggregation
rule recorded; category-level detail may also be shown. Explanations record the
pipeline hash, explainer version/configuration, training-only reference hash,
held-out case key, output scale/class, random seed, and feature mapping.

Attribution describes association with a fitted model output. Correlated inputs
can redistribute apparent importance; no output is a causal explanation,
historical human reason, fairness proof, or guarantee of stability.

## Counterfactual Boundary

Counterfactual search operates in validated original feature space behind one
small constraint contract. Each feature is declared immutable, audit-only,
non-actionable historical, mutable, constrained mutable, excluded, or
unresolved, with allowed categories/range/direction, time horizon, and any
cross-feature rule.

For this dataset:

- age, personal-status/sex, foreign-worker status, target, and audit-only values
  cannot change;
- purpose cannot change merely to game a result;
- credit/employment/residence history, dependants, housing/property/job and
  existing obligations are not immediate recourse;
- amount, duration, and instalment-rate band require joint validation;
- guarantor changes require an explicit practicality constraint and must not be
  presented as easy;
- checking/savings changes, if allowed, are longer-horizon hypotheticals;
- the transformed amount supports only dataset-scale distance, not literal
  currency or financial cost.

Candidate generation → raw-schema validation → role/constraint validation →
dependency validation → exact fitted-pipeline scoring → class-change check →
cost/distance calculation. Invalid candidates are rejected. “No valid
counterfactual found within the declared search” is a valid result, not an
exception and not proof that real-world recourse is impossible.

A small custom constrained search is provisional because only a few variables
are candidates and transparent rules are central to the research. DiCE offers
multiple search methods and feature ranges/weights, but its compatibility and
ability to enforce these dependent, temporal, and semantic rules must be tested
before adoption. No counterfactual library is selected in Phase 2.

## Explanation-Stability Boundary

Stability is a later experiment, not a measured property. A versioned stability
configuration will define:

- a seeded, predeclared held-out case-selection rule;
- perturbable features and valid original-domain perturbation distributions;
- immutable/audit-only protection and categorical/dependency validation;
- exact fitted pipeline and training-only explanation reference data;
- repeated-run count and seeds;
- top-k feature overlap, rank correlation, and normalized attribution change;
- separate reporting for prediction-boundary crossings and unchanged-class
  perturbations; and
- stored per-case/repeat artifacts plus aggregate summaries and limitations.

Thresholds for “stable” are deliberately not invented. Perturbation magnitude,
case count, top-k, repeat count, similarity thresholds, and handling of ties
remain future experimental decisions. Stability results will be bound to one
model, explainer, reference set, output, and perturbation design.

## Conditional Fairness Boundary

Fairness is disabled by default. No South German Credit fairness experiment is
currently authorized because personal-status/sex combines concepts,
foreign-worker support is only 37 rows with four adverse cases, and age has no
source-defined groups.

An authorized future path would preserve audit-only attributes in a separate
row-keyed test view, join them to predictions/labels after inference, compute
group and class cell counts first, and apply a predeclared support rule.
Insufficient groups must cause refusal or a prominent warning, never silent
metric output. Only source-supported group definitions are allowed; proxy-based
identity inference and arbitrary regrouping are prohibited.

If enabled later, reports may contain selection/prediction rates, error rates,
precision/recall and calibration measures where denominators are valid, with
counts and uncertainty. They must record group definitions, dataset/split/run
identity, missingness, support decisions, and limitations. The component never
returns a binary “fair/unfair” verdict.

## Technology Decision Matrix

No dependency is installed or pinned in Phase 2. “Selected” means the technology
is justified for a future authorized research milestone; its exact compatible
version will be locked and tested then. Compatibility evidence was checked on
2026-09-09.

| Problem | Decision/status | Alternatives considered | Reason, trade-offs, compatibility/licence | Reconsider when |
|---|---|---|---|---|
| Core language/runtime | **Selected:** CPython 3.12 series | 3.11; newer Python; R | Matches the Windows environment and ML ecosystem; PSF licence; 64-bit Windows support. Fix exact patch version in the implementation environment | A required package drops/breaks 3.12 or deployment requires another supported runtime |
| Environment/install | **Selected:** standard venv + pip for the first research environment | conda, Poetry, uv | Built into/familiar with Python and adequate for a small laptop; exact dependency/lock format awaits authorized setup | Reproducible locking or native binary resolution proves inadequate |
| Tabular data | **Selected:** pandas | Python csv + arrays; Polars | Clear labelled schema/categorical handling and strong scikit-learn integration; BSD-3-Clause; current Windows CPython 3.12 wheels. More memory than Polars but trivial for 1,000 rows | Data scale or memory becomes material |
| Classical ML/preprocessing | **Selected:** scikit-learn Pipeline/ColumnTransformer and estimators | custom algorithms; XGBoost; deep learning | Provides splitters, preprocessing, baselines, ensembles and metrics in one BSD-3-Clause stack; current Windows/Python 3.12 wheels; CPU-suitable for 8 GB | A distinct research question cannot be answered by its model families |
| Configuration | **Selected:** TOML read with Python tomllib; JSON for machine artifacts | YAML/PyYAML; custom Python config | Standard-library parsing, explicit/versionable text, no runtime code execution; tomllib is read-only, so JSON handles generated manifests | Configuration nesting becomes genuinely awkward |
| Schema validation | **Selected:** small explicit contracts plus pandas checks | Pandera; Pydantic; Great Expectations | Dataset is fixed and small; explicit checks are easiest to defend and avoid framework coupling. Pydantic may later validate API schemas | Multiple datasets or complex runtime schemas make manual validation repetitive |
| Serialization | **Provisional:** evaluate skops; trusted checksum-verified joblib fallback | pickle/cloudpickle; ONNX | skops reduces pickle execution risk but adds a dependency/type review; joblib is already in the scikit-learn stack but unsafe for untrusted files. Exact-version loading is required | Baseline compatibility/security spike chooses a format or cross-language serving appears |
| Testing | **Selected:** pytest | unittest | Readable parametrization/fixtures and suitable data/ML integration tests; MIT; current releases support Python 3.12 | A non-Python delivery layer needs its own test runner |
| Lint/format | **Selected:** Ruff | Black + isort + Flake8; pylint | One fast MIT tool, Windows binaries and Python 3.12 target support; keeps setup small | Required analysis rule is unsupported |
| Static typing | **Provisional:** standard type hints; evaluate mypy after core contracts exist | pyright; no checker | Avoids selecting a checker before code shape exists; type hints still document contracts | Boundary errors show a checker would materially help |
| Plots/reports | **Selected for research:** Matplotlib + JSON/Markdown reports | seaborn; Plotly; notebook-only output | Static reproducible figures and portable evidence; Matplotlib PSF-based licence and Windows/Python 3.12 wheels; less interactive than Plotly | Semester UI needs interactive visualization |
| XAI | **Selected foundation:** native evidence + scikit-learn permutation importance. **Provisional:** SHAP | LIME; PDP; InterpretML | Native evidence is closest to model mechanics; raw-feature permutation is common across models. SHAP is MIT with Windows/Python 3.12 wheels but has background/correlation/runtime semantics to validate | Local nonlinear comparison cannot be answered defensibly or compatibility test fails |
| Counterfactuals | **Provisional:** small transparent constrained search | DiCE; unconstrained optimization | Dataset has few plausibly changeable features and dependent rules; custom logic is inspectable. DiCE is MIT/Python 3.12-labelled but adds behavior/compatibility to validate | Custom search lacks coverage, diversity, or reproducible convergence |
| Experiment metadata | **Selected:** immutable local run directories + versioned JSON manifest | MLflow; database; DVC | Smallest auditable solution; transparent files and no service overhead on 8 GB Windows laptop | Concurrent users, large run volume, remote artifacts, or lifecycle workflows appear |
| Future API | **Deferred/provisional candidate:** FastAPI | Flask; Django; no API | Typed validation/OpenAPI may suit the semester layer, but no API is needed to produce research evidence | An approved application milestone defines endpoints and deployment constraints |
| Future frontend | **Deferred/unselected:** evaluate thin server-rendered/static UI before React/Next | React; Next.js; Streamlit | Avoids a second toolchain before reviewer workflows exist | Approved UI requirements need richer client interaction |
| Future persistence | **Deferred:** filesystem now; later evaluate SQLite/PostgreSQL | MLflow DB; document store | Research artifacts are file-shaped and single-user. PostgreSQL has no current problem to solve | Multi-user transactions/querying/audit retention become approved requirements |
| Containerization/deployment | **Deferred:** no Docker/cloud now | Docker/Compose; native venv | Local research does not need deployment infrastructure; avoids resource/tooling burden on 8 GB laptop | Reproducible handoff or approved application deployment requires it |

Primary compatibility/licence evidence:

- Python 3.12 and Windows: https://docs.python.org/3.12/using/windows.html
- pandas package metadata: https://pypi.org/project/pandas/
- scikit-learn install/metadata: https://scikit-learn.org/stable/install.html
  and https://pypi.org/project/scikit-learn/
- model-persistence security/compatibility:
  https://scikit-learn.org/stable/model_persistence.html
- pytest support/licence:
  https://docs.pytest.org/en/stable/backwards-compatibility.html and
  https://docs.pytest.org/en/7.1.x/license.html
- Ruff metadata/licence: https://pypi.org/project/ruff/
- Matplotlib metadata/licence: https://pypi.org/project/matplotlib/
- SHAP metadata and method documentation: https://pypi.org/project/shap/ and
  https://shap.readthedocs.io/en/latest/
- DiCE methods/licence/metadata: https://github.com/interpretml/DiCE and
  https://pypi.org/project/dice-ml/

These checks establish published support, not project compatibility; compatible
versions still require installation and tests in a later authorized milestone.

## Planned Repository Structure

Nothing in this tree is created by Phase 2:

~~~text
pyproject.toml                         # future dependency/tool configuration
configs/
  dataset.toml                         # dataset identity/schema/target policy
  features.toml                        # role and semantic policy
  experiments/                         # later run configurations
src/aletheia/
  contracts.py                         # simple typed contract values
  config.py
  data/
    acquire.py
    load.py
    validate.py
    target.py
    roles.py
    split.py
  ml/
    preprocess.py
    models.py
    train.py
    evaluate.py
  audit/
    explain.py
    counterfactual.py
    stability.py
    fairness.py
  experiments/
    manifest.py
    artifacts.py
    report.py
  cli.py
tests/
  unit/
  data/
  integration/
  end_to_end/
artifacts/runs/                        # generated and ignored; never committed
reports/generated/                     # generated summaries; policy to decide
notebooks/                             # optional exploration/presentation only
apps/api/                              # future-only
apps/web/                              # future-only
docs/
  decisions/
~~~

Only configuration, the minimal source package data-foundation modules, and
their unit/data tests are candidates for the next implementation milestone.
ML training/audit modules appear only in their separately approved roadmap
milestones. artifacts, reports, notebooks, API, and web paths are future-only.
The exact packaging and dependency files require the next task; this design does
not authorize creating them.

## Testing Strategy

| Test class | Planned scope | Key evidence |
|---|---|---|
| Unit | Target truth table; role-set disjointness; categorical policy; metric fixtures; constraint rules; manifest validation | Small deterministic functions reject invalid values and preserve declared meanings |
| Data/ML contract | Dataset/archive checksum; exact schema/categories/shape; split reproducibility/coverage/no overlap; fold-local fitting; transformed feature mapping; audit alignment | Known data identity and leakage boundaries fail closed |
| Integration | Acquisition → validation → roles → split; preprocessing → model; artifact publish/load; explainer/model association; counterfactual validator; fairness guard | Components exchange the documented contracts and detect incompatible artifacts |
| End-to-end research | One tiny approved configuration from acquisition through immutable report | Same environment/config reproduces membership and expected artifact identities; no hidden notebook step |
| Later application | API validation, exact-run loading, UI/API contract, audit-event handling | Delivery calls research core without duplicate preprocessing/inference |

Specific mandatory future tests include checksum mismatch, extra/missing schema
column, every target label, forbidden audit/target/excluded/unresolved feature,
nominal code handling, same-seed split identity, train/test disjointness,
preprocessor fit boundaries, training/inference transformed-column consistency,
estimator interface/random seed, metric orientation, artifact/library
compatibility, explanation pipeline/case/background identity, all
counterfactual constraints, insufficient fairness support, and one complete
research flow. Coverage percentage is secondary to these failure boundaries.

## Error Handling and Observability

Use typed exceptions or structured error results at module boundaries and simple
structured console/file logs containing run ID, component, event, and safe
context. Do not add a monitoring service.

| Condition | Required future behaviour |
|---|---|
| Checksum mismatch or partial download | Delete/ignore staging file, emit expected/actual identity, stop |
| Schema drift, missing/malformed value, undocumented category | Identify row/column/value safely; refuse validation; never coerce silently |
| Invalid target mapping | Refuse before split; show allowed mapping |
| Forbidden or unresolved prediction feature | Refuse policy construction/training/inference |
| Split overlap/incomplete coverage or wrong dataset hash | Refuse run and invalidate staging |
| Failed model load or incompatible pipeline/library | Do not predict; report run/artifact/version mismatch |
| Unsupported explanation or mismatched model/background | Refuse explanation without affecting stored prediction |
| No valid counterfactual | Return a bounded no-result with constraints/search recorded |
| Insufficient fairness support | Keep path disabled or return refusal/warning with counts |
| Corrupt/incomplete run directory | Never publish/load it as valid; identify failed manifest/hash |

Logs must not include unnecessary raw feature values, audit-only sensitive
attributes, credentials, or executable artifact contents. Expected research
limitations are stored in manifests/reports, not hidden in debug logs.

## Security and Privacy Boundaries

- Never store credentials or secrets in the repository or run configuration.
- Use only the approved public historical dataset; it does not make the system
  production-safe or authorize real-person decisions.
- Validate filenames, hashes, schema, configuration, and later request bodies.
- Load executable/pickle-derived model artifacts only from a trusted,
  checksum-verified local run with compatible recorded versions; never accept an
  uploaded arbitrary model.
- Keep raw/audit-only values out of logs unless a later approved audit design
  proves necessity and protection.
- Future API authentication/authorization and RBAC are deferred to an
  application/security milestone.
- Every user-facing result must state that it is model/dataset evidence, not
  lending advice, a causal account, or a real-world guarantee.

## Deferred and Unresolved Decisions

Before modelling: resolve or exclude bishkred; freeze the prediction feature
set and categorical/ordinal encodings; set split seed/folds; predeclare primary
metric, threshold rule and error-cost interpretation; approve model candidates
and bounded search; choose/pin serialization.

Before XAI: choose held-out cases and analysis partitions; validate SHAP or
another local method; specify background/reference data, output scale, feature
grouping and comparison rules.

Before counterfactuals: approve mutable features, direction/ranges,
amount-duration-rate dependencies, guarantor practicality, time horizons and a
distance/cost definition appropriate to transformed amount.

Before stability: define perturbations, cases, repeats, top-k, handling of ties
and any interpretation threshold.

Before fairness: obtain separate authorization, define legitimate groups and
minimum cell support/uncertainty rules; current evidence may justify no
experiment.

Before application work: validate reviewer workflows and decide whether an API,
frontend, persistence, container, authentication, or deployment is needed.

## Architecture Risks and Limitations

- A 1,000-row, old, selected, oversampled dataset limits model and subgroup
  conclusions regardless of architecture.
- No date/entity ID means stratification cannot test time or repeated-customer
  generalisation.
- The amount transformation and coarse expert codes constrain explanation and
  recourse meaning.
- A local manifest store relies on disciplined atomic publication and may not
  suit concurrent users; that is acceptable for the Research MVP.
- Cross-model explanations are not automatically comparable because native and
  post-hoc methods answer different questions.
- Correlation can redistribute importance and make counterfactual combinations
  implausible despite schema validity.
- Serialization and XAI packages are version-sensitive; manifests and
  compatibility checks reduce but do not remove this risk.
- A modular monolith can still become coupled if modules exchange pandas frames
  without explicit contracts; boundary tests and narrow inputs are required.
- The detailed planned structure may change after implementation feedback. The
  dependency rules and data-validity invariants matter more than folder names.
