# ADR 0008 — Application and MLOps contract for frozen healthcare evidence

Status: proposed contract frozen for external Stage 0 review, not permission to
implement. CURRENT_TASK.md records Macro Milestone 3 approval at
`ff9dce291f63a6d4241360997ef0aff2308597f9`. No service or package is added here.

## Context

Research now has a verified calibrated model and responsible-audit evidence.
Reviewers need a usable evidence workflow; engineers need exact model lifecycle
identity; administrators need controlled release/access history. Previous broad
deployment design left input privacy, live XAI, model approval, registry outages
and transactional audit semantics unresolved. Planning these first avoids a
frontend or HTTP schema committing the system to unsupported patient processing.

## Decision

1. Retain one Python modular monolith; delivery adapters point into the research
   core. Preserve every bound research module/config/test/model/audit byte.
2. Serve verified aggregate evidence and one fixed synthetic local explanation.
   Authenticated live scoring accepts only server-owned `synthetic-discharge-v1`;
   no arbitrary patient/de-identified input, editable features, raw uploads,
   training reference, live XAI, recourse search or similar-case retrieval.
3. Import the existing pipeline **and sigmoid calibrator** into local self-hosted
   MLflow with PostgreSQL metadata and private filesystem artifact proxy.
   Use a guarded reviewed pyfunc wrapper and byte-exact existing joblib artifact.
   A new release manifest binds provenance, wrapper, environment and package;
   no reserialization or rewrite of original evidence. Historical metrics remain
   tagged historical. Synthetic parity only; never reopen the holdout.
4. Use numeric registry versions, candidate/approved/previous aliases and
   administrator-operated release events. API deployment pins an approved
   version/digest, with independently trusted release anchor and read-only cache.
   Registry/DB disagreement blocks activation. Registry outage blocks lifecycle
   changes but not a valid pinned cached release with current DB approval.
5. Use `/api/v1` FastAPI schemas and external OIDC access JWTs. Roles are explicit
   engineer/reviewer/administrator with local entitlement intersection, resource
   authorization and no custom password system. Public endpoints read evidence;
   authenticated POSTs are synthetic only. No HTTP artifact upload or promotion.
   JWT maximum lifetime is configurable and validated against the selected issuer,
   retaining strict signature/issuer/audience/expiry/skew/algorithm checks; no
   public provider is selected. Reviewer event access is limited to authorized
   prediction/review resources; engineer events are own-only and administrators
   may inspect release/entitlement/system-wide events.
6. Use PostgreSQL app tables for identity references, roles, model versions,
   explanation references, predictions, append-only reviewer/release/audit events,
   chain head and idempotency. Prediction/review plus audit plus deduplication
   commit together. Audit failure suppresses success. Hash chains detect changes
   under a trusted checkpoint; a DB owner can still rewrite storage.
   An explicit one-time post-migration operator command bootstraps the configured
   initial administrator with a system-attributed grant and append-only event.
   Only that grant permits NULL granted_by; later grants require an active
   administrator actor. A permanent unique bootstrap event and transactional
   conflict checks prohibit repetition, including after revocation. No public
   bootstrap endpoint, custom passwords or automatic startup seed is permitted.
7. Use React/TypeScript static evidence workbench with accessible charts/tables,
   honest empty/support states and persistent caveats. Local non-root Compose has
   frontend/proxy, API, one PostgreSQL instance with two databases, MLflow,
   filesystem volumes and bounded one-shot jobs; no cloud/Kubernetes or extra DB.
8. Stage 1 combines backend packaging → MLflow verification → PostgreSQL
   migrations → explicit bootstrap → FastAPI/OIDC/RBAC → transactional audit and
   backend tests; Stage 2 is React/TypeScript and complete API integration;
   Stage 3 is Compose, E2E/security/accessibility/resource verification and release
   readiness. Preserve every gate in EXECUTION_PLAN.md; no activation/successful
   POST before atomic audit/release checks. Each stage requires its own task.
   Future milestones use 95% implementation/testing and 5% concise documentation.

## Alternatives considered and accepted trade-offs

Precomputed-only serving would be safest and cheapest, but would not demonstrate
calibrated inference and transactional review. Arbitrary synthetic/de-identified
feature entry would make the demo richer but creates unsupported intake/XAI
privacy and methodology boundaries. The fixed-case hybrid provides an auditable
workflow with a narrow, testable input contract.

Logging only the sklearn base model would lose external calibration. Refitting,
ONNX conversion or rewriting frozen hashes would change evidence. A guarded
pyfunc keeps existing bytes and the complete callable, accepting trusted joblib
execution risk and exact runtime constraints. Models-from-code does not make the
inner pickle safe; outer code and inner bytes both need independent trust checks.

Hosted MLflow/object storage adds cost, credentials and privacy review before
local workflow need is proved. Local self-hosting accepts maintenance and laptop
limits. JSON-only lifecycle would be simpler but lacks reviewed versions and
alias workflow. PostgreSQL rather than SQLite supports concurrent transaction,
idempotency and privileges; two logical databases reuse one server without mixing
MLflow-owned schema with application migrations. No unrelated database is needed.

Per-request registry reads fail on outages and risk mutable alias drift; a pinned
cache accepts operator-controlled restart and local integrity checks. There is
no distributed transaction across registry and app DB, so reconciliation is an
explicit gate. Append-only privileges plus hash chain are bounded integrity
controls, not physical WORM or proof against privileged administrators.

React adds a toolchain compared with static/server-rendered pages, justified by
review states, version context and accessible evidence interaction. One API worker
and filesystem volumes keep the 8 GB topology modest, accepting local-only scale.
OIDC avoids custom password storage but adds issuer/JWKS availability constraints.

## Verification and reconsideration

The endpoint/role/schema/failure tables and diagrams are in
[ARCHITECTURE.md](../ARCHITECTURE.md); screens are in
[PRODUCT_REQUIREMENTS.md](../PRODUCT_REQUIREMENTS.md); resources/dependencies are
in [DEPLOYMENT_ARCHITECTURE.md](../DEPLOYMENT_ARCHITECTURE.md); stage test gates are
in [EXECUTION_PLAN.md](../EXECUTION_PLAN.md). Stage 0 checks documents only.

Later acceptance requires exact-copy/runtime/synthetic parity, JWT/RBAC/object
access, PostgreSQL transaction/concurrency/migration/tamper, frontend accessibility,
synthetic E2E, non-root Compose/restore and existing offline regression evidence.
No test trains the frozen model or accesses holdout data.

Reconsider if clinically reviewed input/reference policy becomes available,
compatibility/security blocks the pinned runtime, measured concurrency exceeds
one-worker capacity, measured artifact storage needs object storage, or separately
approved public deployment defines provider/region/retention. New training needs
a new protocol and independent test population. LLM/LangChain/OpenRouter, vectors,
Redis, Kafka/queues, microservices, Kubernetes, collaborative filtering, tool
calling, cloud and multiple database technologies remain deferred.
