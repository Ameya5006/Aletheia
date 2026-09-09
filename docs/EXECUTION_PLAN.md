# Aletheia — Execution Plan

## Status and Authority

This is the proposed, research-first milestone sequence. It is not a blanket
authorization to start work. `docs/CURRENT_TASK.md` is the sole current task;
each later milestone remains blocked until the external supervisor reviews the
previous work, the user commits/pushes it, and a replacement current task is
approved. `prompt.txt` remains the permanent original vision.

Current state: Phase 0 was attempted and received **FAIL — FIX BEFORE
CONTINUING**. The current Phase 0 Repair is complete only after its documented
checks; it remains **proposed pending external supervisor review**, not
supervisor-approved.

## Proposed Research-First Sequence

1. **Phase 0 — Project Analysis and Scope Validation**
2. **Phase 0 Repair — Documentation and Governance Consistency Repair**
3. **Phase 1 — Dataset Selection and Data Audit** *(future and blocked)*
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

**Verified from repository evidence:** the prior Phase 0 report documents these
items, while no implementation artifacts exist. **Pending external supervisor
approval:** whether the Phase 0 scope and its repair are accepted. **Not
supervisor-approved:** Phase 0 and every later phase.

### Required Documentation Updates

Update `PROJECT_REPORT.md` with factual planning outcomes and limitations;
rewrite `SUPERVISOR_HANDOFF.md` for the current review state. Preserve
unapproved architecture in `ARCHITECTURE.md`.

## Phase 0 Repair — Documentation and Governance Consistency Repair

This is the current documentation-only task. It reconciles the Phase 0 record,
milestone order, task authority, and Git authority; it does not execute Phase
1. Its acceptance criteria and verification evidence are in
`docs/CURRENT_TASK.md` and the repair handoff.

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

**Phase 1 — Dataset Selection and Data Audit** will be defined only in a future
approved `CURRENT_TASK.md`. It may investigate data provenance, target,
semantics, missingness, leakage risk, candidate split strategy, feature roles,
and fairness feasibility. It is not authorized or executable now.

Architecture, technology decisions, detailed roadmap, and reproducible ML work
follow only after Phase 1 evidence and external review. Their precise milestones
are intentionally not defined yet.
