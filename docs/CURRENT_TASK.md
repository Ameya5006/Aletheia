# CURRENT TASK — Macro Milestone 4 Stage 0: Application and MLOps Contract Freeze

## Status

AUTHORIZED FOR PLANNING ONLY.

Macro Milestone 3 was externally approved at commit:

`ff9dce291f63a6d4241360997ef0aff2308597f9`

This task defines the exact implementation contract for Macro Milestone 4. It does not authorize application implementation.

## Starting-State Gate

Before editing, verify:

- branch is `main`;
- `HEAD` equals `origin/main`;
- starting commit is `ff9dce291f63a6d4241360997ef0aff2308597f9`;
- working tree contains only the user-owned modification to `docs/CURRENT_TASK.md`;
- the existing stash remains untouched.

Stop if the starting state differs.

## Mandatory Reading

Read completely:

- `AGENTS.md`;
- this file;
- `README.md`;
- `docs/PRODUCT_REQUIREMENTS.md`;
- `docs/ARCHITECTURE.md`;
- `docs/DEPLOYMENT_ARCHITECTURE.md`;
- `docs/EXECUTION_PLAN.md`;
- `docs/PROJECT_REPORT.md`;
- `docs/SUPERVISOR_HANDOFF.md`;
- healthcare model card;
- healthcare ADRs;
- healthcare foundation, model, experiment and audit modules;
- existing configuration and tests.

Repository evidence overrides documentation claims.

## Objective

Freeze a technically coherent and implementable contract for Macro Milestone 4:

- model lifecycle and MLflow integration;
- FastAPI application boundary;
- PostgreSQL persistence and append-only audit trail;
- authentication and RBAC;
- React/TypeScript reviewer interface;
- Docker/Compose local environment;
- testing, security and observability;
- safe use of the existing frozen model and audit evidence.

This task must remove important design ambiguity before implementation begins.

## Required Decisions

### 1. Product Boundary

Define the exact supported user journeys for:

- ML engineer;
- reviewer;
- administrator;
- public portfolio visitor.

Separate:

- implemented research evidence;
- synthetic demonstration;
- authenticated reviewer functionality;
- future clinical or production functionality.

The public application must not accept or persist identifiable patient information.

### 2. Model and MLflow Lifecycle

Define:

- how the existing frozen model is imported without retraining;
- MLflow experiment, run, model-version and alias conventions;
- checksum and configuration validation before registration;
- artifact storage;
- promotion and rollback rules;
- how the API selects an approved model;
- behaviour when MLflow is unavailable;
- prohibition on loading user-supplied pickle/joblib files;
- prohibition on new holdout evaluation.

Do not migrate or rewrite existing evidence during this planning task.

### 3. Explanation-Serving Boundary

Define which evidence can safely be served:

- global aggregate explanation;
- fixed synthetic local explanation;
- stability summary;
- subgroup summary;
- counterfactual feasibility result;
- model-card and limitation metadata.

Do not assume arbitrary local explanations can be publicly generated unless their reference data, privacy, computational cost and methodology are defensibly specified.

Decide whether the first deployed application should use:

- precomputed verified audit evidence;
- on-demand inference with restricted synthetic inputs;
- or both.

Document the trade-off.

### 4. FastAPI Contract

Specify endpoint paths, methods, roles, input/output schemas, error responses and versioning for at least:

- liveness;
- readiness;
- current model metadata;
- model card;
- prediction for approved synthetic/de-identified input;
- global explanation;
- synthetic local explanation;
- stability results;
- subgroup audit;
- counterfactual-feasibility result;
- audit-event lookup;
- reviewer decision;
- administrator model-version lookup.

Define:

- correlation/request IDs;
- idempotency where required;
- schema/model version fields;
- timeout and fail-closed behaviour;
- OpenAPI exposure;
- rate limiting boundary;
- no raw healthcare-record logging.

### 5. PostgreSQL Contract

Design tables and relationships for:

- users or external subject references;
- roles;
- model versions;
- prediction events;
- explanation references;
- reviewer decisions;
- append-only audit events;
- integrity/hash-chain metadata where justified.

Specify:

- primary and foreign keys;
- timestamps;
- immutable fields;
- retention boundary;
- migration strategy;
- transaction boundary;
- what must never be stored;
- audit-write failure behaviour.

Do not add unrelated databases merely for resume value. Redis, MongoDB, vector databases, graph databases and time-series databases remain deferred unless a real measured requirement emerges.

### 6. Authentication and RBAC

Define:

- external OIDC/JWT validation boundary;
- engineer, reviewer and administrator roles;
- endpoint permission matrix;
- token claims required;
- authentication failures;
- development/test identity strategy;
- secret management;
- prohibition on committed credentials.

Do not implement a custom production password system.

### 7. Frontend Product Contract

Define React/TypeScript routes and screens for:

- project/evidence overview;
- model card;
- synthetic encounter demonstration;
- prediction explanation;
- global feature evidence;
- stability results;
- subgroup audit;
- reviewer decision;
- audit history;
- administrator model metadata.

The visual direction must be professional, functional and portfolio-quality—not a generic AI-generated dashboard.

Use:

- strong typography and spacing;
- restrained healthcare visual language;
- accessible contrast;
- meaningful charts;
- subtle micro-interactions;
- responsive layouts;
- loading, empty and error states;
- reduced-motion support.

Avoid animation-heavy presentation, fake real-time activity, glassmorphism everywhere, excessive gradients and decorative 3D that reduces readability.

### 8. Docker and Local Runtime

Design a laptop-conscious Compose topology for:

- API;
- frontend;
- PostgreSQL;
- MLflow;
- required artifact storage.

Define:

- health checks;
- startup order;
- volumes;
- ports;
- resource considerations for an 8 GB laptop;
- non-root containers;
- configuration and secrets;
- development versus test profiles;
- clean shutdown and recovery.

Kubernetes remains deferred until a measured orchestration requirement exists.

### 9. Testing and Quality Gates

Define required:

- unit tests;
- API contract tests;
- database integration tests;
- migration tests;
- RBAC/security tests;
- model/artifact identity tests;
- frontend component tests;
- frontend accessibility tests;
- end-to-end synthetic workflow;
- Docker smoke test;
- existing 122-test regression suite.

No test may retrain the frozen model or inspect the holdout again.

### 10. Observability and Security

Define:

- structured logs;
- correlation IDs;
- health/readiness;
- request duration and error metrics;
- model-version tagging;
- audit-write monitoring;
- secret handling;
- dependency scanning;
- container scanning;
- CORS and security headers;
- input-size limits;
- request-log redaction;
- trusted artifact loading;
- failure behaviour.

Monitoring must not claim implemented production drift detection during this planning task.

### 11. Deferred Technologies

Explicitly keep these outside the first Macro Milestone 4 implementation unless independently justified:

- LLM or LangChain narration;
- OpenRouter;
- vector databases;
- collaborative filtering;
- Redis;
- Kafka or queues;
- microservices;
- Kubernetes;
- multiple database technologies;
- tool calling;
- cloud deployment;
- new model training.

Record where they could fit later without claiming they are already used.

## Required Architecture Evidence

Update the appropriate documentation with:

- component diagram;
- online request flow;
- model-registration flow;
- database ER diagram;
- authentication/RBAC matrix;
- API endpoint table;
- artifact lifecycle;
- failure-mode table;
- threat boundaries;
- frontend route/component map;
- Docker topology;
- implementation order.

Create one ADR for the Macro Milestone 4 application and MLOps contract.

## Implementation Order

Define a gated implementation sequence inside Macro Milestone 4:

1. packaging/configuration and artifact import;
2. MLflow registration and verification;
3. PostgreSQL schema and migrations;
4. FastAPI core and RBAC;
5. audit persistence;
6. React/TypeScript interface;
7. Docker/Compose integration;
8. complete tests, security checks and documentation.

Each stage must preserve the frozen research evidence.

## Documentation

Update only where necessary:

- `README.md`;
- `docs/PRODUCT_REQUIREMENTS.md`;
- `docs/ARCHITECTURE.md`;
- `docs/DEPLOYMENT_ARCHITECTURE.md`;
- `docs/EXECUTION_PLAN.md`;
- `docs/PROJECT_REPORT.md`;
- `docs/SUPERVISOR_HANDOFF.md`;
- one new ADR.

`PROJECT_REPORT.md` must explain the planned components, decisions, alternatives, trade-offs, data flow, security boundaries, failure modes and implementation order in interview-ready language.

Do not claim any planned technology is implemented.

## Prohibited Work

Do not create or modify:

- Python application source;
- frontend source;
- API routes;
- database migrations;
- Dockerfiles or Compose files;
- dependencies or lockfiles;
- CI workflows;
- MLflow records;
- model artifacts;
- tests;
- raw data;
- experiment or audit evidence;
- `prompt.txt`;
- the existing stash.

Do not modify `docs/CURRENT_TASK.md`.

## Verification

Run:

- `git diff --check`;
- documentation contradiction searches;
- link/path consistency checks where available;
- `git status --short --untracked-files=all`.

No implementation test run is required because implementation files must remain unchanged.

## Expected Git Status

Only the following may appear:

- `M docs/CURRENT_TASK.md` — user-owned;
- modifications to the authorized documentation files;
- one new ADR under `docs/decisions/`.

No source, dependency, test, data, model, artifact, frontend, database, container or workflow file may appear.

## Final Response

Report:

1. planning status;
2. starting commit;
3. product boundary;
4. model/MLflow lifecycle;
5. API contract;
6. PostgreSQL design;
7. authentication/RBAC design;
8. frontend contract;
9. Docker topology;
10. security and observability;
11. testing strategy;
12. implementation sequence;
13. deferred technologies;
14. files modified and created;
15. checks and results;
16. unresolved decisions;
17. what the user should understand;
18. confirmation that no implementation began;
19. confirmation that Codex did not commit or push;
20. exact final Git status;
21. recommended commit message.

If successful, recommend:

`docs: freeze Aletheia application contract`

## Stop Rule

Stop after completing the Macro Milestone 4 contract.

Do not implement the application, change dependencies, retrain models, access the holdout, commit or push.