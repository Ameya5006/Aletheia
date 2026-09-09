# Aletheia — Supervisor Handoff

## Current Milestone and Status

**Phase 2 — System Architecture, Technology Selection, and Implementation
Roadmap.**

Completed by Codex and **proposed pending external supervisor review**. This is
a design milestone, not an implemented or approved architecture. Every
implementation milestone remains blocked.

Phase 1 is externally supervisor-approved. South German Credit is approved only
as suitable for an academic Research MVP; this does not validate model
performance, calibration, fairness, explanation stability, production use, or
modern-lending validity.

## Verified Starting State

- Latest commit: e60d6ef docs: select and audit Aletheia dataset.
- Starting status: only M docs/CURRENT_TASK.md, reflecting the user-installed
  Phase 2 task.
- The Phase 1 commit contains the selected-dataset audit and documentation.
- ARCHITECTURE.md contained only the unapproved placeholder.
- Repository inspection found no raw data, source package, dependency file,
  notebook, test, split, model, experiment, API, database, frontend, container,
  CI/CD, or deployment artifact.

## Proposed Architecture

Aletheia is designed as a **research-first modular monolith**. One future Python
package owns dataset contracts, loading/validation, target and feature policy,
splitting/preprocessing, training/evaluation, XAI/audit methods, and local
experiment evidence. Small functions are preferred over ceremonial services or
interfaces.

A future CLI/report adapter composes the research core. A later API and reviewer
interface may call the same use cases and load explicit validated run artifacts;
they must not duplicate source-code mappings, preprocessing, inference,
explanations, or metrics. Microservices and platform infrastructure are
deferred.

The ADR rejects notebook-only core logic, heavy Clean Architecture ceremony,
framework-first web development, microservices, and an external experiment
platform at this stage. The chosen trade-off favors one testable source of ML
truth and laptop simplicity over built-in distribution, concurrency, and
artifact querying.

## Key Component and Dependency Boundaries

The proposed architecture defines components for:

- acquisition/integrity, loading, schema validation, explicit target mapping,
  feature roles, and deterministic split membership;
- preprocessing, model construction, training orchestration, fold-local
  cross-validation, final fit, and one held-out evaluation;
- manifest validation, atomic immutable artifact publication, global/local
  explanations, counterfactual constraints/search, stability, conditional
  fairness, and report generation; and
- future API and UI adapters.

Each component in ARCHITECTURE.md states responsibility, input/output,
dependencies/caller, prohibited work, failure modes, and planned tests.
Dependency direction is delivery adapters → research orchestration → data/ML/
audit/artifact modules → simple contracts. Research code does not depend on
FastAPI, frontend, database, or deployment code. Reports read completed
artifacts and cannot start training.

## Training and Inference Flows

Proposed training:

official source → checksum verification → immutable raw reference → schema and
semantic validation → explicit adverse-target mapping → feature-role
enforcement → fixed stratified membership → fold-local preprocessing/bounded
CV → selected final pipeline fit on all training rows → one held-out evaluation
→ predeclared XAI/audit analyses → validated immutable run → report.

Only fold-training/all-training data fits transformations. The held-out
partition cannot choose preprocessing, models, thresholds, metrics, or
explanation settings. Training data supplies explanation background/reference
data. Audit-only fields remain in a separate aligned row-keyed view.

Proposed inference:

raw request → same schema/policy → exact checksum-verified fitted
preprocessing/model pipeline → prediction/score → optional exact-run explanation
and constrained counterfactual → audit event → response.

Inference never refits, reconstructs encodings, or interprets raw German codes
inside application code. Explanations and counterfactuals identify and invoke
the exact pipeline used for the prediction.

## Dataset Invariants

The design fails closed on these Phase 1 facts:

- raw kredit 0 = bad/non-compliant and 1 = good/compliant; adverse_event is
  derived explicitly while raw target stays traceable;
- target cannot enter predictors;
- age, personal-status/sex, and foreign-worker status remain audit-only
  candidates and separate from model inputs;
- telephone is excluded;
- bishkred is unresolved/default-deny;
- categorical integer codes are not automatically continuous;
- the file's oversampled 30% adverse rate cannot be reported as source-population
  prevalence or population-calibrated risk;
- transformed amount cannot be described as literal currency;
- absent dates/entity IDs permit the current fixed stratified strategy but no
  temporal/entity-generalisation claim; and
- all learned transforms fit on training data only.

Schema, target, role, split, preprocessing, report, and counterfactual
components each own a corresponding refusal/test boundary.

## Experiment and Artifact Strategy

The Research MVP uses planned local artifacts/runs/<run-id> directories and a
versioned JSON manifest rather than MLflow or a database. The manifest binds
dataset/source/hash, target and feature policy, split seed/membership,
preprocessing/feature map, models/configuration, code/environment, validation
and held-out results, fitted-pipeline hash/compatibility, XAI reference/cases,
counterfactual/stability/fairness configuration, timestamps, and limitations.

Runs are written to staging, validated/checksummed, atomically published, and
never overwritten. Reports and later APIs name explicit run IDs and hashes, not
“latest.” Serialization remains provisional: evaluate skops; use joblib only as
a trusted, checksummed, exact-environment fallback if approved.

## XAI, Counterfactual, Stability, and Fairness Boundaries

- **XAI:** native coefficients/tree evidence and original-feature permutation
  importance are the selected foundation. SHAP is provisional pending bounded
  compatibility/methodology tests; LIME/PDP are deferred. Every explanation
  records model/pipeline, transformed-to-original feature map, output/class,
  held-out case, training-only reference, configuration, and limitations.
- **Counterfactuals:** a transparent custom constrained search is provisional;
  DiCE is deferred pending compatibility and rule-coverage testing. Search
  occurs in raw feature space and validates immutable/audit/history/mutable/
  dependent rules before exact-pipeline scoring. Amount-duration-rate
  dependencies, purpose prohibition, guarantor practicality, and transformed
  amount limitations are explicit. No valid candidate is an allowed result.
- **Stability:** later seeded valid perturbations, repeated runs, top-k overlap,
  rank correlation and normalized attribution change are planned; boundary
  crossings are reported separately. No threshold or result exists.
- **Fairness:** disabled and not authorized for South German Credit. A future
  path must check source-supported groups and cell counts before metrics,
  preserve aligned audit-only data, represent uncertainty, and refuse weak
  support. It cannot infer identities or return a fair/unfair verdict.

## Technology Decisions

Selected for a future authorized research implementation:

- CPython 3.12 on Windows using venv/pip;
- pandas for labelled tabular data;
- scikit-learn pipelines, classical models, splitting and metrics;
- TOML via tomllib for human configuration and JSON for generated manifests;
- small explicit schema/feature contracts rather than a validation framework;
- pytest;
- Ruff;
- Matplotlib plus JSON/Markdown research reports;
- native explanation evidence and scikit-learn permutation importance; and
- immutable local run directories.

Current project compatibility was not tested because installation is out of
scope. Official metadata checked on 2026-09-09 publishes Python 3.12/Windows
support for the selected ecosystem, with permissive PSF/BSD/MIT-family licences.

Provisional: exact versions/lock format, model serialization, optional mypy,
SHAP, and a small custom counterfactual search.

Deferred/unselected: DiCE dependency, FastAPI, React/Next or another frontend,
SQLite/PostgreSQL, MLflow/DVC, Docker, cloud/deployment, authentication/RBAC,
microservices, XGBoost and deep learning.

## Planned Structure and Tests

ARCHITECTURE.md proposes—but Phase 2 did not create—configs, one
src/aletheia package with data/ML/audit/experiment modules, focused unit/data/
integration/end-to-end tests, ignored run artifacts, optional presentation
notebooks, and future-only API/web directories. Only configuration, minimal
data-foundation modules, and their tests are candidates for the next separately
authorized milestone.

Planned tests cover dataset checksums/schema/target, disjoint/forbidden roles,
categorical semantics, deterministic disjoint splits, fold-local fitting,
training/inference transformed-feature consistency, estimator/metric contracts,
artifact compatibility/atomicity, explainer/run association, counterfactual
constraints, fairness guards, and later API/end-to-end flows. Phase 2 created no
tests because it created no implementation.

## Proposed Roadmap

Every item is blocked and requires external review plus a replacement current
task:

1. reproducible data foundation;
2. leakage-safe dummy/logistic baseline;
3. bounded classical comparator evaluation;
4. global/local explanation evidence;
5. constrained counterfactual proof of concept;
6. explanation-stability experiment;
7. conditional fairness authorization gate;
8. research synthesis;
9. later thin API;
10. later reviewer interface/minimal persistence;
11. optional evidence-driven enterprise extensions.

The next advisory milestone is deliberately small: acquisition/checksums,
schema/target/feature roles, deterministic split membership, and tests—no model
training.

## ADR

Created docs/decisions/0001-research-first-modular-monolith.md with context,
decision, alternatives, reasons, trade-offs, consequences, deferred decisions,
and reconsideration conditions.

## Exact Files Changed

User-provided existing change:

- docs/CURRENT_TASK.md — Phase 2 authorization; Codex did not replace it.

Modified by Codex:

- docs/DATASET_AUDIT.md — Phase 1 approval-status wording only;
- docs/ARCHITECTURE.md — rewritten as the proposed Phase 2 design;
- docs/EXECUTION_PLAN.md — approved history, Phase 2 gate, and blocked roadmap;
- docs/PROJECT_REPORT.md — concise Phase 2 learning/defence record;
- docs/SUPERVISOR_HANDOFF.md — this current handoff.

Created by Codex:

- docs/decisions/0001-research-first-modular-monolith.md.

Intentionally unchanged: AGENTS.md, prompt.txt, README.md, and .gitignore.

## Checks Actually Run

Starting-state inspection:

- git status --short → M docs/CURRENT_TASK.md only.
- git log -3 --oneline → e60d6ef Phase 1 commit followed by the two Phase 0
  documentation commits.
- rg --files and git ls-files inspection → documentation plus .gitignore only;
  no implementation/artifact files.
- git show --stat e60d6ef → Phase 1 changed its five required documents and
  created DATASET_AUDIT.md.

Final design/repository checks:

- git diff --check → exit 0; no whitespace errors (line-ending warnings only).
- protected-file diff for AGENTS.md, prompt.txt, README.md, and .gitignore →
  exit 0; unchanged.
- git status --short → six expected modified-document entries plus the untracked
  docs/decisions/ directory entry; the untracked-file listing resolves that
  directory to the single expected ADR.
- git ls-files --others --exclude-standard → only the ADR.
- prohibited-artifact extension/path scan → 0.
- component-contract check → all 21 required component boundaries found; each
  table defines responsibility/I-O, dependency/caller, prohibition, failure,
  and planned test.
- architecture invariant checks → target mapping, role exclusions, training-only
  fit, exact fitted pipeline, oversampling/population warning, disabled
  fairness, delivery-to-core direction, and blocked roadmap all found.
- document-status consistency check → Phase 1 approved; Phase 2 pending external
  review; no implementation claim across the architecture, plan, report, audit,
  ADR, and handoff.
- Markdown fence check → balanced in architecture, execution plan, and ADR.
- complete final diff inspected; only authorized documentation changed.

No automated implementation tests were applicable or run. No experiment,
metric, model, fairness result, explanation, counterfactual, or stability result
was produced.

## Unresolved Decisions

bishkred treatment; final predictor/encoding policy; exact package versions and
lock format; split seed/folds; primary metric, threshold and error costs; bounded
model search; serialization; SHAP/background/case/grouping method;
counterfactual constraints/cost/library; stability cases/perturbations/repeats/
interpretation; whether fairness can be authorized; and all application,
persistence, security, container and deployment choices.

## Risks and Limitations

The dataset is small, old, regional, granted-only, oversampled, unidentifiable
by time/entity, weak for fairness, and has transformed amount/coarse categories.
Architecture cannot remove those limitations. A filesystem store lacks
concurrency/query features; post-hoc explanations remain correlation- and
configuration-sensitive; recourse may be mathematically valid but unrealistic;
model persistence is version/security-sensitive; and module discipline still
requires tests. All technology compatibility remains unverified in this project
until an authorized dependency milestone.

## Architecture and Implementation Status

Architecture changed from an unapproved placeholder to a detailed **proposal
pending external supervisor review**. No source code, package structure,
dependency/configuration file, raw/processed data, split, test, model, result,
run artifact, API, database, frontend, container, CI/CD, or deployment was
created. Codex did not commit or push.

## Evidence for Supervisor Inspection

1. ARCHITECTURE.md — complete boundaries, flows, invariants, technology matrix,
   planned tests/errors/security and risks.
2. decisions/0001-research-first-modular-monolith.md — the major decision and
   alternatives/trade-offs.
3. EXECUTION_PLAN.md — Phase 2 completion criteria and blocked gated roadmap.
4. PROJECT_REPORT.md — concise learning/interview/viva defence.
5. DATASET_AUDIT.md — only its Phase 1 approval status changed.
6. The final diff/status and protected/prohibited-artifact checks.

## Suggested Next Action

External supervisor review of Phase 2 only. If approved, the supervisor may
authorize the bounded reproducible-data-foundation milestone through a
replacement CURRENT_TASK.md. This handoff and roadmap do not authorize it.
