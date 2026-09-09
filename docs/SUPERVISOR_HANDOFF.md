# Aletheia — Supervisor Handoff

## Current Milestone

Phase 0 — Project Analysis and Scope Validation.

## Status

Complete for supervisor review. No architecture design, application code,
dataset selection, dependency installation, experiment, or deployment began.

## Analysis Performed

- Read governance, prompt, report, architecture status, execution plan, and
  previous handoff.
- Narrowed the proposal to a research-first audit of tabular credit-risk
  classifiers rather than a generic prediction dashboard or enterprise platform.
- Defined users, requirements, research questions, dataset/model/evaluation
  criteria, XAI boundaries, risks, MVP, strong semester scope, and deferrals.

## Files Changed

- `docs/PROJECT_REPORT.md`
- `docs/SUPERVISOR_HANDOFF.md`

No application, architecture, execution-plan, dependency, infrastructure, or
dataset files were changed.

## Important Decisions and Why

- Research and reproducibility precede APIs, dashboards, databases, tracking,
  and deployment, so platform work cannot hide invalid or absent evidence.
- Credit-risk tabular classification is a laptop-feasible reference use case,
  not a banking deployment claim.
- Regularised Logistic Regression is the interpretable baseline, with only a
  limited set of nonlinear comparators to make a real trade-off study.
- Fairness analysis is conditional on legitimate audit attributes and adequate
  subgroup support; no fairness result is promised.
- Technology choices (including FastAPI, MLflow, PostgreSQL, React/Next,
  Docker, XAI/counterfactual libraries, and MLP) remain unfinalized.

## Unresolved Questions

1. Which public dataset meets provenance/licence, target, semantics, leakage,
   class-support, and possible subgroup-audit requirements?
2. What are the positive class, error-cost framing, primary metric, and correct
   split strategy (stratified, temporal, or group-aware)?
3. Which features are prediction, audit-only, excluded, immutable, mutable, or
   constrained?
4. Which minimal XAI/counterfactual tools are compatible, reproducible, and
   justified after model/data review?
5. Are stability and fairness feasible in the approved schedule after MVP work?

## Risks Identified

Target/temporal/preprocessing/entity leakage; class imbalance; unrepresentative
public data; causal or fairness overclaims; implausible counterfactuals;
underpowered subgroup analysis; XAI dependency compatibility; premature
infrastructure; and premature microservice/abstraction complexity.

## Verification Performed

- Cross-checked documentation against `AGENTS.md`, `prompt.txt`,
  `docs/ARCHITECTURE.md`, and `docs/EXECUTION_PLAN.md`.
- Inspected repository files: there is no application source, test suite,
  dataset, or implementation artifact.
- No automated tests were applicable or run. No ML experiment or metric exists.

## Documentation Changed

`docs/PROJECT_REPORT.md` now records planning facts, alternatives, constraints,
and explicit conditional/deferred work. `docs/ARCHITECTURE.md` and
`docs/EXECUTION_PLAN.md` remain intentionally unchanged.

## Evidence the Supervisor Should Inspect

Review the report sections Scope, Users, and Assumptions; Research Questions;
Dataset Requirements; Planned ML and Evaluation Strategy; Explainability and
Audit Requirements; Risks and Controls; Scope Boundaries; and Decisions to
Finalize Before Implementation. Confirm that architecture remains unapproved
and later execution-plan phases remain provisional.

## Known Limitations

No data-based conclusion, technology selection, implementation, experiment,
architecture approval, or production validation exists. Scope depends on finding
a vetted dataset that supports the study.

## Suggested Next Step

If the supervisor approves Phase 0, conduct a separate dataset-selection and
data-audit milestone before architecture or implementation. Resolve provenance,
target, feature roles, leakage, splitting, and fairness feasibility there.

The suggested next step is advisory only; the external supervisor determines
whether the project advances.
