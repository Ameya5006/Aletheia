# Deployable architecture and tooling decision

Status: Macro Milestones 1–3 are completed; Macro Milestone 3 external approval
at `ff9dce291f63a6d4241360997ef0aff2308597f9` is recorded in CURRENT_TASK.md.
Stage 0 documents the local application runtime contract only, pending review.
The research model/audit and retained credit baseline remain unchanged.

## Macro Milestone 4 local runtime contract — unimplemented

Choose self-hosted local MLflow with a PostgreSQL backend and filesystem artifact
volume. This resolves DagsHub versus self-hosting for the first implementation;
hosted storage is deferred to Macro Milestone 5. MLflow artifacts use its private
HTTP artifact proxy so clients do not need direct volume access. No S3 emulator,
object-storage service or unrelated database is needed for this workload.
The application remains one API modular monolith plus a static frontend; MLflow
and PostgreSQL are infrastructure, not independently distributed business services.

```mermaid
flowchart LR
  H[Browser localhost 8080] --> W[Non-root frontend and API proxy]
  W --> A[API 8000 internal]
  A --> P[PostgreSQL 5432 internal]
  O[Local operator] --> M[MLflow loopback 5000]
  M --> P
  M --> V[Private mlflow-artifacts volume]
  R[One-shot release verifier] --> M
  R --> C[Approved release volume]
  C --> A
  D[One-shot migrations] --> P
  B[Explicit one-time operator bootstrap after migrations] --> P
  J[Development JWKS fixture] --> A
```

| Compose service/job | Health and startup | Volumes and ports | Initial resource budget |
|---|---|---|---|
| `postgres` | `pg_isready`, then authenticated queries to separate app/MLflow databases | named `pgdata`; 5432 internal only | 512 MiB RAM, 1 CPU, small connection pool |
| `migrate` | one-shot app owner job after healthy PostgreSQL; API depends on successful exit | migration code from image; secrets read-only; no host port | 256 MiB temporary |
| `mlflow` | DB schema initialized by single server startup; `/health` plus operator registry query | named `mlflow-artifacts`; container 5000 to `127.0.0.1:5000` for dev operator only | 768 MiB, 1 CPU, one worker |
| `release-import` | explicit operator profile; after healthy MLflow and migrated app DB; verification and import only | original evidence read-only bind; new `approved-release` volume write; no raw data | 768 MiB temporary; stop after import |
| `api` | liveness and readiness; healthy DB, completed migration, approved verified release required | `approved-release` read-only; 8000 internal only; writable temporary directory on tmpfs | 768 MiB, 1 CPU, one worker and one inference thread |
| `frontend` | HTTP static readiness; proxy propagates API health errors | compiled static files in image, writable tmpfs if needed; container 8080 to `127.0.0.1:8080` | 128 MiB, 0.5 CPU |
| `dev-identity` | local signed-token/JWKS fixture health; development/test profiles only | ignored generated key mounted read-only; private network; optional loopback test port | 128 MiB |

Budgets total about 2.25 GiB for steady application services and dev identity,
plus Docker/OS overhead; these are targets for an 8 GB laptop, not measurements.
Run imports and browser test/build jobs sequentially, not alongside training or
many workers. Static frontend avoids a resident Node dev server in the normal
Compose stack. Do not add Grafana/Prometheus or an identity platform just for
presentation. Later smoke tests must measure actual RAM/startup and adjust
budgets openly if the laptop cannot run this topology.

Startup: PostgreSQL healthy → migration completes; MLflow healthy → explicit
import/approval creates release; API verifies pin/DB → readiness; frontend
remains available to show an unready API. `depends_on` health/completion
conditions order startup but do not provide runtime availability; API connection
retry is bounded and requests still fail closed. See [Compose startup ordering](https://docs.docker.com/compose/how-tos/startup-order/).
On a fresh environment readiness stays false until explicit approved import and
entitlement bootstrap via the one-time operator command specified in
[ARCHITECTURE.md](ARCHITECTURE.md). Bootstrap requires configured synthetic/deployment
issuer/subject, completed migrations and no prior/conflicting state; grant and
append-only system event commit together. It is never automatic or public.
Restarting the stack must not automatically bootstrap, re-register,
change aliases or regenerate research evidence.

Every long-running container runs as a non-root UID; bind high ports and
pre-create owned volume directories in a bounded initialization job. Pin tested
image digests during implementation, drop unnecessary capabilities, no Docker
socket, read-only root filesystem where supported, limited tmpfs and private
networks. Package only approved byte-preserving provenance and the exact model
bundle, never the raw archive/CSV. Git-normalized Linux source is not a substitute
for the original byte-bound evidence snapshot. Mount original artifacts read-only
even for imports; output belongs to a new release volume. MLflow artifact volume
is private; API has only the approved release copy and cannot modify registry data.

Configuration names: `APP_ENV`, `DATABASE_URL`, `MLFLOW_TRACKING_URI`,
`MLFLOW_REGISTRY_URI`, `APP_MODEL_VERSION`, `APP_RELEASE_SHA256`,
`APP_RELEASE_ROOT`, `OIDC_ISSUER`, `OIDC_AUDIENCE`, `OIDC_JWKS_URI`,
`OIDC_CLIENT_ID`, `OIDC_MAX_TOKEN_LIFETIME_SECONDS`, `CORS_ALLOWED_ORIGINS`;
operator-only bootstrap configuration uses `BOOTSTRAP_OIDC_ISSUER` and
`BOOTSTRAP_OIDC_SUB`. The JWT maximum is validated against the selected issuer's
access-token configuration and signed-token tests in Stage 1; no public provider
is selected. Frontend public configuration uses
same-origin `/api/v1` and public OIDC settings only. DB passwords/registry
credentials/dev signing keys use mounted ignored secret files or environment
injection, not image build arguments. API startup rejects missing secrets or
development identity in release mode. DB owner and MLflow roles are separate
from runtime app credentials. No credentials/default production password is
committed; future templates may contain placeholders only.

Profiles: `dev` has loopback bindings/dev identity and optional frontend hot
reload; `test` uses separate ephemeral DB/artifact/release volumes, synthetic
subjects/cases and contract-test runner. Test fixtures never mount raw or
holdout data. Approved artifact parity tests may read the frozen model and saved
synthetic example but do not train or score holdout. Host `venv` remains a
fallback for research inspection, not a substitute claim for Compose verification.

Shutdown drains API for at most 15 seconds and closes DB connections; Compose
grace period 30 seconds lets PostgreSQL flush. Normal stop retains named volumes;
no automatic volume deletion. Restart verifies hashes, migrations, chain head,
approval and idempotency records before readiness. Backup/restore both DBs and
artifact/release volumes with a consistent inventory; restore rehearsals verify
release hashes and audit sequence/head, with no holdout access. A corrupt release
is quarantined and replaced from verified backup, never regenerated by a runner.

## Dependencies and alternatives — selected for later verification only

No dependency or service is installed in Stage 0. Later stages must review
official license metadata, pin compatible versions/lockfiles and test this plan
before adoption. Published license families include
[MLflow Apache-2.0](https://github.com/mlflow/mlflow),
[FastAPI MIT](https://github.com/fastapi/fastapi),
[Pydantic MIT](https://github.com/pydantic/pydantic),
[SQLAlchemy MIT](https://github.com/sqlalchemy/sqlalchemy),
[Alembic MIT](https://github.com/sqlalchemy/alembic),
[PyJWT MIT](https://github.com/jpadilla/pyjwt),
[psycopg LGPL-3.0](https://github.com/psycopg/psycopg),
[PostgreSQL License](https://www.postgresql.org/about/licence/),
[axe-core MPL-2.0](https://github.com/dequelabs/axe-core) and
[Playwright Apache-2.0](https://github.com/microsoft/playwright).
This is a planning inventory, not legal clearance; browser toolchain, exact
distributions, container/base-image and transitive notices require separate
version-specific review before adoption. Exact
package/image versions remain Stage 1/2/3 compatibility gates; the frozen ML
runtime may not be silently upgraded.

MLflow is needed for reviewed version/alias lifecycle; local JSON alone lacks
multi-user registry workflow. FastAPI/Pydantic provide typed HTTP schemas over
existing functions; Flask/manual schemas are possible but add contract work.
SQLAlchemy with psycopg and Alembic provides explicit transactions/migrations;
raw SQL is simpler initially but repeats mapping/migration machinery. PostgreSQL
is needed for concurrent review/idempotency/audit writes; SQLite remains suitable
for small tests but cannot replace PostgreSQL integration evidence. PyJWT with
crypto and a reviewed OIDC browser client supply standard signature/PKCE plumbing;
custom cryptography/passwords are rejected. React/TypeScript with Vite supports
the planned evidence/review interaction; server-rendered pages would reduce the
toolchain but make these stateful flows less convenient. Vitest/Testing Library,
axe-core and Playwright are proposed component/accessibility/E2E tools. A small
SVG chart layer with accessible tables avoids a large chart dependency initially.
Docker/Compose and a non-root static proxy make the local topology reproducible;
native host services are a fallback but lose the same packaging evidence.

Local software has no hosted subscription requirement; CPU, memory, disk and
operator maintenance remain costs. External OIDC provider/host cost and region
are unresolved for future public hosting. If dependency compatibility fails,
pause that implementation stage and report the blocker; existing read-only
research evidence remains usable. Do not add another service or change the
frozen model merely to work around it.

## Deferred placement

CI/CD, cloud/public hosting and measured drift monitoring belong to Macro
Milestone 5 under separate approval. LLM/LangChain/OpenRouter narration could
later format already computed safe evidence, but deterministic prose suffices.
Vector databases/tool calling require a genuine retrieval/tool workflow;
similar-case retrieval itself needs privacy/method review first. Collaborative
filtering belongs to a different recommendation problem. Redis/shared rate
limiting, Kafka/queues, microservices and Kubernetes need measured concurrency,
asynchronous work or orchestration evidence. Multiple database technologies,
DVC/object stores/hosted MLflow and new model training are deferred; training
would need a new protocol and independent test population. None is implemented.

## Earlier broad tooling map — historical design context

The matrix below preserves the previous multi-milestone design. Where it differs,
the Stage 0 contract above and ARCHITECTURE.md govern the first application:
fixed synthetic input, precomputed local explanation, local self-hosted MLflow,
no automatic training/evaluation and no similar-case retrieval.

No API/server, UI, database, MLflow registry/service, authentication/RBAC, containerized deployment, CI/CD, monitoring, LLM/RAG or later operations is implemented. Similar-case retrieval is also unimplemented. Selected and provisional tools below are future architecture decisions, not installed or deployed components. Macro Milestones 4 and 5 require separate authorization; no clinical readiness, fairness certification, production scale or deployment is claimed.

The diagram describes the **future delivery architecture**, not a running system:

```mermaid
flowchart LR
  U[Reviewer / engineer] --> UI[React TypeScript UI]
  UI --> API[FastAPI modular monolith]
  API --> CORE[Shared ML and XAI use cases]
  CORE --> HC[Healthcare contracts]
  CORE --> CR[Credit contracts]
  API --> PG[PostgreSQL audit store]
  CORE --> MF[MLflow registry and artifacts]
  CI[GitHub Actions] --> IMG[Docker image]
  IMG --> API
```

The current credit package remains at `src/aletheia/data`, `ml`, and `experiments`. Healthcare policy is at `src/aletheia/domains/healthcare`. Shared use cases may be extracted only once both domains need them. Domain target, roles, split and future recourse constraints cannot be shared blindly. HTTP and UI call validated use cases; they never reimplement transformations. Future prediction flow: authenticated request → role/schema validation → registered fitted pipeline → probability/calibration → local explanation and similar training cases → append-only audit event → response. The API must not accept raw identifiable health records in the public demo.

## Tooling matrix

Each row states status, role and connection, configuration and artifact, risks and alternative. Milestone numbers refer to `PRODUCT_REQUIREMENTS.md`.

| Tool | Status / milestone | Role, caller, input → output | Config, security, failure and alternative |
|---|---|---|---|
| Python 3.12, pandas, scikit-learn | Implemented / 1–3 data, model/calibration and research audit | CLI research use cases consume validated tables and the frozen fitted pipeline → metrics and aggregate explanations/audits | `pyproject.toml`, lockfile, TOML contracts. Fit preprocessing only in group folds. 8 GB limits wide one-hot tables. Polars is an alternative but increases migration cost. |
| Local immutable manifests | Implemented for credit and healthcare / 1–3 | Research runs → inspectable JSON identities and results | Ignored `artifacts/runs`, `artifacts/healthcare-model-v1`, `artifacts/healthcare-audit-v1`; no concurrency/remote registry. Future MLflow migration requires approval and preserved evidence. |
| MLflow | Selected / 4 | Training use case logs parameters, metrics, artifacts and model versions → registry IDs consumed by API | `MLFLOW_TRACKING_URI`, credentials in secret store. Avoid PHI in runs; registry availability and artifact compatibility are risks. Local manifests alone lack approval lifecycle. |
| DagsHub-hosted MLflow | Provisional / 4 | Remote MLflow backend for public non-sensitive experiment metadata | Endpoint/credentials secret; pricing, availability, retention and access must be reviewed. Self-hosted MLflow with object storage is fallback. No patient-level data uploaded. |
| DVC | Provisional / 2–4 | Version data pointers and checksums alongside Git; training consumes pinned source identity | `dvc.yaml` only after adoption; remote storage/access/cost must be evaluated. Current pinned UCI bytes + Git contracts/lock are a justified lightweight alternative for one public immutable source. |
| FastAPI | Selected / 4 | Typed REST adapter calls validated model/audit use cases → versioned response/OpenAPI | `DATABASE_URL`, registry URI, auth issuer/audience, model stage. Prevent identifier leakage, validate input, rate limit. Django REST is heavier; direct notebook serving is unsafe. |
| PostgreSQL | Selected / 4 | API records model version, request hash/reference, prediction, explanation ID and append-only review event | `DATABASE_URL` secret, migrations, encryption, least privilege, retention. Transaction/connection failures must fail closed for audited prediction. SQLite lacks intended concurrent managed operation. No raw clinical record storage. |
| React + TypeScript | Selected / 4 | Browser reviewer dashboard consumes API JSON → comparison and encounter review | `VITE_API_BASE_URL`; avoid storing health data in browser/local storage. Next.js adds server complexity without a current need. |
| Docker + Compose | Selected / 4 | Package API and local development dependencies → reproducible containers | Image pinning, secret injection, nonroot runtime, health checks; Compose is local only. Direct host installs drift; Kubernetes unjustified. |
| GitHub Actions | Selected / 5 | CI runs tests, formatting, security checks, image build → evidence and deploy gate | OIDC/short-lived secrets, protected environment, no raw data. Hosted runner limits/network failures; local command fallback. Future code graph parses Python/TypeScript imports, detects cycles/forbidden directions, publishes CI artifact and maps nodes to architecture. |
| Managed public deployment | Provisional / 5 | Host API/UI and managed PostgreSQL, use registry artifact → public demonstration | Vendor, region, cost and availability unresolved; use only synthetic/de-identified examples. Self-hosted VPS is fallback with more operations burden. Deployment is blocked until auth/audit/privacy checks. |
| Monitoring/drift checks | Selected / 5 | API operational metrics + approved aggregate feature/prediction distributions → alerts and review | No raw identifiers in logs; thresholds/baselines versioned. Drift is a signal, not proof of model harm. Manual periodic review is fallback. |
| Hugging Face cards | Selected / 2–5 | Publish model/dataset documentation, provenance and limitations → inspectable public evidence | No fitted model or sensitive data upload without approval; licenses and provenance required. Markdown in repo is fallback. Optional hosted demonstration is provisional and must remain synthetic. |
| OpenRouter narrator | Provisional / 5 | Optional text rendering of already computed explanation evidence → reviewer prose | API key secret; no patient values sent; hallucination and cost risk. Deterministic templates are default fallback. Narration cannot create evidence. |
| Authentication + RBAC | Selected / 4 | Identity provider claims → engineer/reviewer/admin permissions | OIDC issuer/audience, server-side policy, short sessions. Simplified demo auth still needs enforced roles; unauthenticated public predictions are rejected for real data. |
| Immutable audit logging | Selected / 4 | API writes append-only event and hash chain/version → replayable decision trace | PostgreSQL transaction, restricted writes, retention/export checks. DB administrator can still alter storage without external anchoring; cryptographic anchoring may follow. |
| RunwayML | Rejected | No legitimate tabular audit role | Media-generation cost/dependency would not solve a requirement. Reconsider only for a genuine visual media need. |

Implemented flow: official HTTPS archive → SHA-256 verification → controlled two-member extraction → strict CSV/schema/target validation → discharge-eligible cohort → feature and audit views → locked patient split → training-only nested group CV/model comparison and calibration → frozen selection and trusted local joblib artifact → one locked holdout evaluation. The completed audit then uses the unchanged calibrated model, training-only XAI/stability, counterfactual feasibility and one separately guarded post-selection subgroup audit → aggregate evidence and checksummed manifest. This repair only inspects existing records; no part of either run is repeated.

Registry and serving remain designed only. The current artifact is local checksummed joblib, not a deployed registry object; any migration needs later approval. Secrets belong in future deployment secret managers/environment, never TOML or Git. Host vendor, DagsHub versus self-hosting and DVC adoption remain unresolved. Future network outages, registry unavailability, schema/version mismatch and audit-write failure must prevent untracked serving. The five-milestone statuses and definitions of done agree with [PRODUCT_REQUIREMENTS.md](PRODUCT_REQUIREMENTS.md) and [EXECUTION_PLAN.md](EXECUTION_PLAN.md); existing evidence is in the [model card](model_cards/healthcare_readmission_v1.md), [PROJECT_REPORT.md](PROJECT_REPORT.md) and [SUPERVISOR_HANDOFF.md](SUPERVISOR_HANDOFF.md).
