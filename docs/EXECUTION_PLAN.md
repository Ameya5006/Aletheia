# Aletheia — Execution Plan

## Status and Authority

This research-first roadmap is proposed sequencing, not blanket authorization.
CURRENT_TASK.md remains the sole executable task. Every milestone below requires
the previous milestone's external review and a supervisor-approved replacement
CURRENT_TASK.md. Codex does not advance merely because a milestone appears here.

- Phase 0 and its repair: externally supervisor-approved.
- Phase 1 dataset selection/audit: externally supervisor-approved.
- South German Credit: approved only as suitable for an academic Research MVP;
  no model, calibration, fairness, stability, production, or modern-lending
  claim is approved.
- Phase 2 architecture/technology/roadmap: completed by Codex and **pending
  external supervisor review**.
- Every implementation and delivery milestone: future and blocked.

prompt.txt remains the permanent vision. The proposed architecture does not
authorize implementation, dependencies, dataset download, modelling, XAI, or
application work.

## Gate Rules

For every future milestone:

1. a replacement CURRENT_TASK.md must define its exact scope and acceptance
   evidence;
2. only that milestone may be executed;
3. implementation, relevant tests, leakage checks, documentation, and the
   supervisor handoff must agree;
4. Codex stops after verification without committing or pushing; and
5. external supervisor review decides whether the next milestone may begin.

A failure, unsupported assumption, or invalid ML boundary is recorded as
incomplete/investigate, not hidden to preserve schedule.

## Completed Planning Milestones

### Phase 0 — Project Analysis and Scope Validation

**Status:** externally supervisor-approved.

Established Aletheia as an XAI/model-auditing research project rather than a
prediction dashboard; defined users, research questions, requirements, risks,
Research MVP, semester application, and deferred enterprise scope. No dataset,
architecture, or implementation was authorized.

### Phase 0 Repair — Governance and Scope Consistency

**Status:** externally supervisor-approved.

Reconciled the research-first order, scope vocabulary, task/Git authority,
stability boundary, and measurable approval gates.

### Phase 1 — Dataset Selection and Data Audit

**Status:** externally supervisor-approved.

Compared four authoritative public candidates, selected South German Credit,
and recorded its identity, target/observation semantics, schema, feature roles,
leakage/split constraints, and limited fairness/counterfactual feasibility in
DATASET_AUDIT.md. Approval is limited to academic dataset suitability.

### Phase 2 — System Architecture, Technology Selection, and Roadmap

**Status:** completed by Codex; proposed pending external supervisor review.

**Goal:** define an evidence-producing research architecture based on Phase 1
without implementing it.

**In scope:** research-first modular-monolith decision; research/delivery
separation; component contracts/dependencies; training/inference flows;
dataset invariants; local artifact contract; XAI, counterfactual, stability and
conditional-fairness boundaries; technology decisions; planned structure;
testing/errors/security; gated roadmap; one ADR.

**Out of scope:** source/tests/dependencies, raw data/splits, preprocessing,
models/metrics/experiments, explanations/counterfactuals/fairness/stability,
API/UI/database/MLflow/container/deployment, and the next executable task.

**Completion evidence:**

- ARCHITECTURE.md contains the required component, dependency, flow, invariant,
  artifact, research-method, technology, testing, error, security, risk and
  deferred-decision sections;
- the research core is independent of future delivery layers;
- training, inference, and explanations share one exact fitted pipeline;
- audit-only/target/excluded/unresolved features fail closed;
- the oversampled 30% adverse rate cannot be presented as population
  prevalence;
- local immutable manifests are selected while serialization remains
  provisional and platform infrastructure deferred;
- one ADR records alternatives/trade-offs;
- this roadmap bounds each future milestone without authorizing it;
- PROJECT_REPORT.md and SUPERVISOR_HANDOFF.md contain consistent, non-fabricated
  records; and
- final diff/status/scope/consistency checks pass with no implementation
  artifacts.

## Proposed Post-Architecture Roadmap

All milestones below are **blocked**. Dependencies describe logical order, not
permission.

~~~mermaid
flowchart LR
    P2[Phase 2 design] --> P3[Data foundation]
    P3 --> P4[Baseline]
    P4 --> P5[Comparators]
    P5 --> P6[XAI]
    P6 --> P7[Counterfactuals]
    P6 --> P8[Stability]
    P5 --> P9[Conditional fairness gate]
    P7 --> P10[Research synthesis]
    P8 --> P10
    P9 --> P10
    P10 --> P11[Thin API]
    P11 --> P12[Reviewer interface]
    P12 --> P13[Optional enterprise extensions]
~~~

### Phase 3 — Reproducible Data Foundation

**Dependency:** Phase 2 external approval and a replacement current task.

**Bounded goal:** create the smallest tested package/configuration needed to
reacquire, verify, load, validate, map and split the approved dataset.

**In scope:** dependency/tool configuration approved for this phase; UCI
acquisition manifest; archive/raw SHA-256 verification; raw loader; exact schema
and category contract; explicit kredit/adverse-event mapping; disjoint feature
roles; default-deny bishkred; stable row keys; deterministic fixed stratified
split membership; unit/data tests; ignored local raw/generated paths.

**Out of scope:** learned preprocessing, estimator fitting, model metrics, XAI,
counterfactuals, fairness/stability, artifact model serialization, API/UI and
infrastructure.

**Completion evidence:** clean-environment acquisition or documented offline
fixture approach; expected checksum/schema/shape/target tests; mismatch and
unknown-category failures; forbidden-role tests; same-seed split identity, full
coverage, no overlap and class support; exact commands/results; updated report
and handoff.

### Phase 4 — Leakage-Safe Baseline Pipeline

**Dependency:** approved Phase 3 data foundation.

**Bounded goal:** establish a reproducible preprocessing/evaluation contract and
simple reference performance before nonlinear comparison.

**In scope:** final approved prediction features; categorical/ordinal treatment;
fold-local ColumnTransformer/Pipeline; dummy sanity reference and regularized
Logistic Regression; fixed CV/final-test protocol; predeclared primary/supporting
metrics and threshold rule; bounded configuration; first versioned run manifest.

**Out of scope:** nonlinear winner selection, SHAP, counterfactuals, stability,
fairness, API/UI and deployment.

**Completion evidence:** train-only/fold-only fit tests; transformed-column
identity; target orientation and metric fixture tests; reproducible run/config/
split/environment record; CV results with interpretation; one gated held-out
evaluation only if the approved task permits it; no test-set tuning.

### Phase 5 — Bounded Comparator Evaluation

**Dependency:** approved baseline and frozen evaluation contract.

**Bounded goal:** determine whether justified nonlinear tabular models improve
meaningfully over the interpretable baseline.

**In scope:** only preapproved Decision Tree, Random Forest and Gradient
Boosting candidates needed by the research question; bounded search inside
training CV; common splits/preprocessing/metrics; calibration analysis if
methodologically supported; runtime/complexity evidence.

**Out of scope:** algorithm catalogues, XGBoost/deep learning without a distinct
question, XAI conclusions, application work.

**Completion evidence:** recorded objectives/configurations/fold results,
held-out comparison under the frozen protocol, performance versus
interpretability discussion, selected research candidates with reasons, and no
unbounded or final-test tuning.

### Phase 6 — Global and Local Explanation Evidence

**Dependency:** approved frozen model runs and feature maps from Phase 5.

**Bounded goal:** generate reproducible, correctly associated explanation
evidence for selected models.

**In scope:** native coefficients/tree evidence; original-feature permutation
importance; a bounded SHAP compatibility/methodology decision if authorized;
training-only background/reference data; preselected held-out cases; one-hot
group mapping; explicit correlation/causality limitations.

**Out of scope:** arbitrary explainability score, counterfactuals, stability
claims, fairness claims, dashboard.

**Completion evidence:** exact run/pipeline/case/background/config associations;
determinism and feature-group tests; global/local distinction; method-specific
limitations; comparison that does not claim post-hoc explanations are internal
reasoning.

### Phase 7 — Constrained Counterfactual Proof of Concept

**Dependency:** approved prediction/explanation interface and frozen model.

**Bounded goal:** demonstrate auditable model recourse for a small predeclared
case set without implying financial advice.

**In scope:** approved raw-domain constraint contract; immutable,
non-actionable, mutable, constrained and dependent feature rules; transparent
custom-search versus DiCE decision; validity/class-change/distance evidence; a
worked example and no-result handling.

**Out of scope:** real approval advice, causal recourse, unrestricted feature
search, production endpoint.

**Completion evidence:** tests for every feature/range/direction/dependency,
purpose prohibition, amount limitation, exact-pipeline scoring, reproducible
search, valid candidate or explicit bounded failure, and documented example.

### Phase 8 — Explanation-Stability Experiment

**Dependency:** approved local explanation method/configuration.

**Bounded goal:** measure, not assume, how local prediction explanations respond
to small valid perturbations.

**In scope:** predeclared held-out cases; valid seeded perturbations; repeated
runs; top-k overlap, rank correlation and normalized attribution change;
separate boundary-crossing analysis; immutable protections and artifacts.

**Out of scope:** invented universal threshold, adversarial robustness platform,
monitoring/drift infrastructure.

**Completion evidence:** reproducible perturbations/repeats, metric tests,
case-level and aggregate records, separate crossing results, honest method/
sample limitations, no unsupported stability verdict.

### Phase 9 — Conditional Fairness Authorization Gate

**Dependency:** approved model predictions and aligned audit-only test view.

**Bounded goal:** decide whether any narrowly defined subgroup experiment is
semantically and statistically defensible; run it only if separately authorized.

**In scope:** source-supported group definitions; group/class cell counts;
predeclared minimum-support/uncertainty rule; disabled/refusal behavior; if
authorized and supported, bounded selection/error/precision/recall/calibration
measurements with counts and uncertainty.

**Out of scope:** proxy identity inference, arbitrary age bins, audit attributes
as model inputs, legal compliance, binary fair/unfair conclusion.

**Completion evidence:** default-disabled guard and row-alignment tests; explicit
support decision. Given current evidence, a documented refusal/no experiment is
a valid outcome.

### Phase 10 — Research Synthesis and Model-Audit Conclusion

**Dependency:** approved baseline/comparator/XAI/counterfactual work, stability
if the complete research question is claimed, and the fairness gate outcome.

**Bounded goal:** answer the approved research questions from immutable run
evidence without expanding the implementation.

**In scope:** reconcile predictive and auditability evidence; compare limitations;
identify the preferred research model versus numerical winner; reproduce final
tables/figures from artifacts; update report, viva, and resume evidence.

**Out of scope:** new tuning, new test-set decisions, API/UI, production claims.

**Completion evidence:** every claim traces to an approved run/partition/method;
no report-triggered training; limitations and negative results retained;
research question answered only to the evidence's scope.

### Phase 11 — Thin Prediction/Audit API

**Dependency:** approved research synthesis plus a demonstrated reviewer/API
need and a new architecture/security review.

**Bounded goal:** expose one approved frozen run without duplicating research
logic.

**In scope:** technology decision; validated request/response schemas; explicit
run loading; inference/explanation/counterfactual calls; minimal audit event;
API unit/integration tests and safe logging.

**Out of scope:** training endpoint, arbitrary model upload, frontend, RBAC,
microservices, cloud deployment.

**Completion evidence:** identical core/API predictions, no refitting or code
mapping in routes, invalid/unapproved artifact rejection, documented OpenAPI
contract if FastAPI is chosen.

### Phase 12 — Reviewer Interface and Minimal Persistence

**Dependency:** approved API and validated reviewer workflows.

**Bounded goal:** present existing evidence clearly; add persistence only if a
specific workflow requires it.

**In scope:** technology choice based on interaction needs; run comparison and
prediction/explanation/counterfactual views; visible caveats; accessibility and
API/UI end-to-end tests; optional minimal audit persistence.

**Out of scope:** ML logic in browser, generic CRUD administration, enterprise
workflow/monitoring/cloud.

**Completion evidence:** UI values trace to API/run IDs, misleading visual
guards, no duplicated transformations/metrics, tested primary reviewer flow.

### Phase 13 — Optional Enterprise Extensions

**Dependency:** completed semester application plus separately evidenced
production requirements.

**Goal:** consider—not presume—authentication/RBAC, approval workflows, remote
registry/storage, monitoring/drift, CI/CD, containers, cloud, scaling or service
separation.

Each extension requires its own problem statement, threat/operations model,
trade-off analysis, architecture migration, tests, and supervisor authorization.
It is not part of the Research MVP or automatically part of the semester
application.

## Advisory Next Step

External supervisor review of Phase 2 only. If approved, the supervisor may
replace CURRENT_TASK.md with a bounded Phase 3 data-foundation task. This file
does not create or authorize that task.
