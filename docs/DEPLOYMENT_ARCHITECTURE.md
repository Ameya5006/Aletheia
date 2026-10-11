# Deployable architecture and tooling decision

Status: Macro Milestones 1 and 2 are completed. Macro Milestone 3 is implemented and locally verified, pending external review. The local Python research core includes healthcare modelling/calibration, the frozen model, global/local calibrated-probability XAI, recording stability, guarded subgroup audit, counterfactual feasibility and immutable local experiment/audit records. Counterfactual feasibility found no defensible recourse; no search or actionable scenarios exist. The credit foundation and training-only baseline remain intact.

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
