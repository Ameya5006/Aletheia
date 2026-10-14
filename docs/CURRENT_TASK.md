# CURRENT TASK — MACRO MILESTONE 4, STAGE 3

## Objective

Implement and verify Aletheia’s complete local Docker Compose deployment and release-readiness boundary.

This is an implementation milestone. Spend approximately 95% of effort on implementation, integration, testing and verification, and no more than 5% on concise documentation.

Do not begin public cloud deployment, CI/CD, LLM integration or future product enhancements.

## Required starting state

Before editing:

1. Read `AGENTS.md` and this file completely.
2. Confirm branch `main`.
3. Confirm `HEAD` equals local `origin/main`.
4. Confirm the latest commit is:

   `107636b chore: finalize Aletheia frontend review`

5. Confirm `git status --short --untracked-files=all` contains only:

   `M docs/CURRENT_TASK.md`

6. Record the full starting commit and stash list.
7. Preserve the existing credit-research stash without inspecting, applying, dropping or modifying it.
8. Stop without editing if the state differs materially.

## Required reading

Read the implementation-relevant portions of:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/DEPLOYMENT_ARCHITECTURE.md`
- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/EXECUTION_PLAN.md`
- `docs/PROJECT_REPORT.md`
- `docs/SUPERVISOR_HANDOFF.md`
- `docs/decisions/0008-application-mlops-contract.md`
- Stage 1 application, migrations, registry and operator code
- Stage 2 frontend configuration and API contracts

Treat the implemented backend/frontend and actual repository as the source of truth.

## Scope

### 1. Container images

Implement:

- multi-stage production API image;
- multi-stage React build and non-root static reverse-proxy image;
- exact supported base-image versions, with digests where reproducibly available;
- non-root runtime users;
- minimal runtime packages;
- useful OCI labels;
- container health checks;
- `.dockerignore`;
- no raw datasets, research scratch data, ignored artifacts, credentials, caches, tests or development environments copied into production images;
- deterministic dependency installation from existing lock files.

Do not retrain, repackage or change the frozen model.

### 2. Docker Compose topology

Implement the approved local topology:

- PostgreSQL;
- separate application and MLflow databases/roles;
- migration one-shot job;
- MLflow tracking/registry service;
- explicit release-import job/profile;
- FastAPI service;
- frontend/reverse proxy;
- optional explicit test-only identity support if required for automated E2E verification.

Requirements:

- PostgreSQL and MLflow must not be publicly exposed by default;
- any development MLflow port must bind only to loopback;
- frontend proxy provides the public local entry point;
- `/api/v1` is same-origin proxied to FastAPI;
- persistent named volumes;
- health-dependent startup order;
- bounded restart policies;
- resource limits suitable for an 8 GB laptop;
- no automatic administrator bootstrap;
- no automatic release registration, approval or activation;
- migrations, bootstrap and release import remain explicit operator actions;
- normal shutdown must retain persistent data.

### 3. Configuration and secrets

Implement:

- a safe example environment file containing no real secrets;
- environment validation;
- Docker secrets or mounted ignored secret files for database and operator credentials;
- explicit development/test/release profiles;
- no private keys, tokens, passwords or real provider configuration in Git;
- no fallback to insecure default credentials in release mode;
- clear failure when required configuration is missing.

### 4. Proxy and browser security

Implement and verify:

- SPA deep-route fallback;
- same-origin API proxying;
- CSP compatible with the configured OIDC authority;
- HSTS only where HTTPS is actually enabled;
- `X-Content-Type-Options`;
- frame protection;
- referrer policy;
- permissions policy;
- bounded request/body/time limits;
- correct forwarding headers;
- no exposure of internal MLflow/PostgreSQL services;
- no fabricated frontend data when services fail.

### 5. Full-stack synthetic E2E

Prove through the running Compose stack:

- migrations from an empty database;
- explicit initial administrator bootstrap;
- explicit frozen-release import;
- model verification and activation;
- health/readiness;
- public evidence routes;
- frontend loading;
- authenticated fixed-synthetic prediction;
- PostgreSQL persistence;
- reviewer decision;
- audit-event linkage;
- role restrictions;
- idempotent retries;
- administrator release evidence;
- no arbitrary patient submission;
- no raw patient data in images, volumes, logs or responses.

Use only synthetic identities and the fixed synthetic case.

### 6. Failure and recovery verification

Test:

- PostgreSQL unavailable;
- MLflow unavailable;
- API unavailable;
- revoked or mismatched release;
- migration failure;
- interrupted startup;
- restart with persistent volumes;
- graceful shutdown;
- failed audit write suppressing success;
- backup and restore of application/MLflow databases and approved-release metadata;
- valid pinned serving behaviour during MLflow outage;
- no fallback to an unapproved model.

Do not intentionally destroy user-owned Docker resources. Use project-scoped names and disposable test volumes.

### 7. Resource and security evidence

Measure and record:

- image sizes;
- cold-start time;
- healthy-start time;
- idle and bounded-workload memory;
- container CPU use;
- named volumes;
- exposed ports;
- runtime users;
- Linux capabilities;
- production dependency consistency;
- image vulnerability scan;
- SBOM if supported by the selected tooling;
- licence inventory.

Measurements describe only the tested local machine and are not production-scale claims.

### 8. Testing

Run all relevant checks:

- Compose config validation;
- container builds;
- migration tests;
- Stage 1 application/PostgreSQL/MLflow tests;
- Stage 2 frontend tests;
- frontend TypeScript, lint, format and build;
- OpenAPI contract verification;
- synthetic container E2E tests;
- accessibility/browser smoke through the proxy;
- full offline Python suite;
- pip consistency;
- Ruff lint and format;
- npm dependency consistency and audit;
- image/security checks;
- backup/restore test;
- restart/outage checks;
- `git diff --check`;
- final Git status.

Do not claim a check passed unless it actually ran successfully.

## Documentation policy

Implementation remains the priority.

Update only:

- `README.md` when necessary for exact Compose setup and operator commands;
- `docs/PROJECT_REPORT.md` with concise architecture flow, implementation decisions, important problems/fixes, measurements, tests, limitations and interview defence;
- `docs/SUPERVISOR_HANDOFF.md` with exact review evidence.

Modify another architecture document only if implementation exposes a genuine contradiction, and keep the change minimal.

## Protected boundaries

Do not:

- modify `docs/CURRENT_TASK.md`;
- retrain or reselect the model;
- access or reevaluate held-out data;
- rerun the responsible research audit;
- change frozen research evidence;
- fabricate deployment measurements;
- restore or modify the stash;
- add OpenRouter, LangChain, RAG or tool calling;
- add Redis, Kafka, Kubernetes or microservices;
- implement public cloud hosting;
- implement GitHub Actions or public CI/CD;
- add production monitoring infrastructure;
- commit or push.

Docker Compose is the approved orchestration boundary for this stage. Kubernetes belongs to a separate future project or separately approved enhancement.

## Expected repository status

The starting status must be exactly:

```text
 M docs/CURRENT_TASK.md
 The final status may contain only:
- the unchanged user-owned docs/CURRENT_TASK.md;
- new or modified Docker/Compose/proxy/deployment configuration;
- new deployment/E2E tests and tightly scoped test helpers;
- minimal backend/frontend configuration changes genuinely required for containers;
- README.md;
- docs/PROJECT_REPORT.md;
- docs/SUPERVISOR_HANDOFF.md;
- dependency manifests only if an unavoidable, justified runtime/testing dependency is required.
No raw data, model artifacts, generated releases, databases, volumes, logs, screenshots, reports, caches, virtual environments, node_modules, build output, secrets or temporary files may appear.
If another path appears, stop and explain it.
Completion response
Report:
1. Stage status;
2. architecture implemented;
3. services and one-shot jobs;
4. image identities and sizes;
5. startup/shutdown behaviour;
6. synthetic E2E flow;
7. security controls;
8. failure/recovery results;
9. backup/restore result;
10. measured resource use;
11. files created;
12. files modified;
13. tests and exact results;
14. unresolved issues;
15. limitations;
16. what the user should understand;
17. confirmation that research evidence was untouched;
18. confirmation that later work did not begin;
19. confirmation that Codex did not commit or push;
20. exact final git status --short --untracked-files=all;
21. recommended commit message.
Recommended commit message after external review:
feat: deploy Aletheia local application stack
Stop after Stage 3.