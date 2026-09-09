# Aletheia — Execution Plan

## Status and Authority

This research-first sequence is not blanket authorization. `docs/CURRENT_TASK.md`
is the sole current task; every later milestone remains blocked until external
review, user commit/push, and approval of a replacement task. `prompt.txt`
remains the permanent original vision.

Phase 0 and its repair are externally supervisor-approved. Phase 1 dataset
selection/audit is completed by Codex and pending external supervisor review;
this status does not authorize architecture or implementation.

## Proposed Research-First Sequence

1. **Phase 0 — Project Analysis and Scope Validation**
2. **Phase 0 Repair — Documentation and Governance Consistency Repair**
3. **Phase 1 — Dataset Selection and Data Audit** *(completed by Codex; pending
   external supervisor review)*
4. **Architecture, technology, and detailed implementation-roadmap planning**
   *(future and blocked)*
5. **Reproducible ML and later implementation milestones** *(future and
   blocked)*

Dataset evidence comes before architecture because it determines target
semantics, prediction/audit feature roles, leakage controls, temporal or group
split needs, preprocessing, fairness feasibility, counterfactual constraints,
and XAI/model compatibility. Selecting an API, database, tracking tool, or
application shape first would build around assumptions that the data may reject.

## Phase 0 — Project Analysis and Scope Validation

### Objective

Propose a coherent, academically defensible research scope for Aletheia before
dataset selection, architecture, technology selection, or implementation.

### Prerequisites

- Permanent project vision available in `prompt.txt`.
- Repository governance available in `AGENTS.md`.
- No implementation or prior architecture approval required.

### Concepts Involved

High-stakes tabular classification, reproducibility, data leakage,
cross-validation and held-out evaluation, intrinsic/post-hoc explainability,
counterfactual feasibility, explanation stability, and conditional fairness.

### In-Scope Work

- Define the proposed problem, users, boundaries, requirements, research
  questions, model families, evaluation direction, XAI direction, risks, and
  local-hardware constraints.
- Define Research MVP, later semester application/demo scope, and enterprise
  extensions without selecting technologies.
- State unresolved decisions that require dataset evidence.

### Out-of-Scope Work

Dataset selection/download/EDA; actual feature roles, positive class,
threshold, metric, or split selection; architecture/module design; dependency
selection/install; code; tests; experiments; deployment; and any Phase 1 work.

### Expected Affected Files

`docs/PROJECT_REPORT.md` and `docs/SUPERVISOR_HANDOFF.md`. A repair may also
correct this plan and permanent governance where an inconsistency is found.

### Required Checks and Evidence

- Repository evidence confirms no dataset, code, dependencies, experiments, or
  approved architecture were introduced.
- Planning documents distinguish proposed work from verified evidence and do
  not claim a dataset, metric, experiment, or approval.
- Scope contains a primary research question, boundaries, risks, a baseline
  direction, reproducibility expectations, and conditional fairness treatment.

### Measurable Definition of Done

Phase 0 is complete **by Codex** only when all of the following are documented:

- a distinct XAI/auditing purpose rather than a prediction-dashboard purpose;
- users, functional/non-functional boundaries, and hardware constraint;
- research questions, dataset requirements, candidate model/baseline direction,
  and leakage-safe evaluation direction;
- global/local explanation distinction, constrained counterfactual direction,
  stability research direction, and conditional fairness scope;
- Research MVP, later application/demo scope, and enterprise extensions;
- unresolved data-dependent decisions and major ML/engineering risks;
- an updated report and handoff containing no fabricated implementation,
  experiment, metric, result, or approval claim.

**Verified from repository evidence:** the Phase 0 report documents these items
and no implementation artifacts were introduced. **Supervisor-approved:** Phase
0 and its repair, as recorded by the externally approved Phase 1 task.

### Required Documentation Updates

Update `PROJECT_REPORT.md` with factual planning outcomes and limitations;
rewrite `SUPERVISOR_HANDOFF.md` for the current review state. Preserve
unapproved architecture in `ARCHITECTURE.md`.

## Phase 0 Repair — Documentation and Governance Consistency Repair

This documentation-only repair reconciled the Phase 0 record, milestone order,
task authority, and Git authority. It is externally supervisor-approved.

## Phase 1 — Dataset Selection and Data Audit

### Objective and Prerequisites

Select and audit one public tabular credit-risk dataset capable of supporting
the Research MVP. Prerequisites were the approved Phase 0 scope/repair, no prior
dataset or implementation, and an unapproved architecture; repository evidence
confirmed that state.

### Concepts and Scope

Concepts: provenance/licensing, file identity, target/observation semantics,
structural profiling, feature timing and roles, leakage, split families,
subgroup support, and counterfactual feasibility.

In scope: compare authoritative candidates; inspect permitted raw files outside
the repository; select through explicit gates; record checksum/schema/counts,
feature roles, leakage risks, a future split recommendation, and conditional
fairness/counterfactual feasibility. Out of scope: preprocessing, train/test
file creation, model training/metrics, fairness measurement, counterfactual
generation, architecture, technology selection, application work, and
dependencies persisted in the project.

### Evidence and Affected Files

Four UCI candidates were compared and their official files inspected. South
German Credit was selected pending review. The detailed evidence is in
`docs/DATASET_AUDIT.md`; the concise learning record is in
`docs/PROJECT_REPORT.md`; this plan and `docs/SUPERVISOR_HANDOFF.md` record the
gate. `AGENTS.md` received the authorized report-guide clarification.

### Measurable Definition of Done and Status

- at least three authoritative candidates compared using transparent gates;
- selected dataset has verified source/licence, original filename, retrieval
  date, byte size, SHA-256, shape, target, observation unit, and reacquisition;
- computed missingness, duplicates, identifier/repeated-entity evidence, class
  arithmetic, categories/ranges, and legitimate subgroup support recorded;
- every selected feature has meaning, semantic type, timing, proposed role,
  leakage concern, and counterfactual category;
- leakage/chronology review and evidence-based split-family recommendation
  recorded;
- fairness and counterfactual feasibility assessed without implementing either;
- no raw data, model, code, architecture, project dependency, or future task
  introduced; protected documents unchanged; final documentation checks pass.

These criteria are completed by Codex and verified from the evidence recorded in
the audit and handoff. Phase 1 remains **pending external supervisor review** and
is not supervisor-approved.

### Required Documentation Updates

Created `docs/DATASET_AUDIT.md`; incrementally updated the project report and
this plan; rewrote the supervisor handoff. `prompt.txt`, `ARCHITECTURE.md`, and
the approved current task remain unchanged.

## Scope Vocabulary

### Research MVP

The minimum evidence-producing ML/XAI prototype: one approved documented
dataset; leakage-safe reproducible preprocessing/splitting; an interpretable
baseline and justified nonlinear comparators; cross-validated selection inside
training data; untouched held-out evaluation; global/local explanations; a
constrained counterfactual proof of concept; traceable experiment metadata; and
a concise research comparison or prediction-inspection presentation.

Explanation stability remains part of Aletheia's complete research question,
but it is **not required** to complete this initial Research MVP. It is required
before claiming that the complete research question, including stability, has
been answered. Its perturbations, eligible features, cases, background data,
similarity metrics, and boundary-crossing treatment must be designed after
dataset inspection. Fairness remains conditional on legitimate audit attributes,
adequate subgroup support, and appropriate methodology.

Finishing the Research MVP neither completes the original platform vision nor
automatically completes the semester application/demo.

### Semester Application/Demo Scope

A later usable application, built only after reliable research evidence exists.
Subject to separate approval and justification, it may add a minimal API,
reviewer-facing interface, experiment tracking or appropriate persistence,
targeted tests, audit records, and local reproducibility/containerization.
FastAPI, MLflow, PostgreSQL, React/Next, and Docker are unselected technologies
until their respective decisions are approved. Application components must
present verified research evidence, not conceal weak methodology.

### Enterprise Extensions

Explicitly deferred: unnecessary early microservices, Kubernetes, RBAC,
production monitoring, CI/CD, cloud infrastructure, approval workflows,
scheduled retraining, production registry, drift/explanation-drift monitoring,
and real-lender integration.

## Future Blocked Milestones

Architecture, technology decisions, the detailed roadmap, and all reproducible
ML/application work remain blocked until Phase 1 is externally reviewed and a
replacement `CURRENT_TASK.md` explicitly authorizes one next milestone. Their
precise scopes are intentionally not defined here.
