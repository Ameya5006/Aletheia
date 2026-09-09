# ADR 0001: Research-First Modular Monolith

## Status

Proposed pending external supervisor review.

## Context

Aletheia must produce reproducible evidence about model performance,
explanations, constrained counterfactuals, stability, and conditional subgroup
behaviour. Phase 1 established a small, fixed tabular dataset with strict target,
feature-role, split, fairness, and recourse limitations. No software or
deployment architecture exists yet.

The immediate problem is to keep ML validity and experiment evidence independent
from future HTTP, UI, database, and deployment choices while retaining an
understandable path to a semester application. The project is single-user,
laptop-bound, and does not need independently scaled or deployed components.

## Decision

Use one Python **modular monolith** whose research core contains small modules
for data contracts/acquisition, validation and roles, splitting/preprocessing,
training/evaluation, audit methods, and immutable local experiment artifacts.
A command-line/composition entry point will orchestrate these modules.

Dependency direction is inward:

- contracts and configuration do not depend on delivery frameworks;
- data, ML, XAI, and artifact modules depend on explicit contracts;
- orchestration composes those modules;
- report, future API, and future UI adapters call the research use cases or load
  validated artifacts;
- research modules never depend on API, UI, database, or deployment code.

Training and inference share one fitted preprocessing/model pipeline and one
feature-policy contract. Later delivery components must reuse those boundaries
and may not implement their own feature mapping, preprocessing, or inference.

Use a lightweight immutable filesystem run store for the Research MVP. Add
platform infrastructure only after research evidence and approved user
workflows establish a need.

## Alternatives Considered

### Notebook-Centric Research

Fast for exploration, but hidden state, cell order, duplicated transformations,
and weak tests make it an unsuitable canonical pipeline. Optional notebooks may
call package code for exploration or presentation.

### Heavily Layered Clean Architecture

Domain/application/infrastructure layers and interfaces around every dependency
could isolate frameworks, but the current project has few implementations and
simple local boundaries. It would add files and indirection without improving
the most important leakage and reproducibility controls. Explicit contracts and
small modules provide the useful separation.

### Framework-First Web Monolith

Starting with FastAPI/Django and a database could create an early demo, but it
would make research validity depend on HTTP/persistence concerns and encourage
duplicate training/inference logic. Delivery should consume proven research
artifacts later.

### Microservices

Independent data, training, explanation, and prediction services could scale
separately, but there is no workload, team, availability, or deployment evidence
requiring that complexity. Network contracts, distributed failure modes, queues,
observability, and deployment overhead would weaken an 8 GB laptop project.

### External Experiment Platform First

MLflow or a database supplies search and lifecycle features, but local immutable
manifests are enough for the expected run count and are easier to inspect and
defend. Migration remains possible if later workflows require concurrency,
remote storage, or registry stages.

## Reasons

- The research question is answered by valid, reproducible evidence rather than
  platform scale.
- One process and package minimize training/inference divergence.
- Module and feature-policy boundaries directly address Phase 1 leakage risks.
- Local manifests keep every result inspectable without a service dependency.
- The structure remains teachable and testable by one CSE student.
- API/UI integration remains possible through stable use cases and explicit run
  artifacts.

## Trade-offs

- Module discipline is enforced by tests/review rather than network boundaries.
- A filesystem store provides less querying, concurrency, and lifecycle support
  than MLflow or a database.
- Direct pandas/scikit-learn use creates some library coupling; wrappers are
  reserved for unsafe persistence or genuinely substitutable methods.
- A later application may require adapters and migrations not designed in
  detail now.
- The modular monolith can still become over-segmented; simple functions should
  remain simple.

## Consequences

Positive:

- dataset invariants and feature roles have one source of truth;
- CV, final fitting, inference, and XAI can share the same pipeline identity;
- research can complete without frontend/backend infrastructure;
- each run can be reproduced and audited from an explicit manifest;
- future delivery layers remain thin.

Costs and constraints:

- every module must accept/return documented contracts and fail closed;
- report generation must consume artifacts rather than rerun work;
- artifact publication needs checksum, completeness, collision, and
  compatibility checks;
- future API/UI work must adapt to the research core rather than fork it.

## Deferred Decisions

Exact dependency versions and lock format; model serialization; final feature
policy; split seed/folds; metrics/threshold; model set; SHAP adoption;
counterfactual algorithm/library; stability protocol; fairness authorization;
API/frontend/database/MLflow/container/deployment technologies; and
authentication/RBAC.

## When to Reconsider

Revisit the architecture if evidence shows:

- independently scaling or isolating training/inference is necessary;
- multiple teams require separately owned/deployed boundaries;
- concurrent users or large run volumes exceed safe filesystem artifacts;
- remote artifact storage, approval workflows, or strong transactional audit
  records become approved requirements;
- another domain requires plugins or alternate implementations that justify
  stable interfaces; or
- security/deployment requirements require a separate serving runtime.

Reconsideration must preserve target/feature/split contracts, exact fitted
pipeline identity, immutable experiment evidence, and the rule that delivery
layers do not duplicate research logic.
