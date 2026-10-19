# Supervisor Handoff — Azure continuation (2026-10-18)

## 1. Current milestone and status

Azure cloud deployment continuation is **incomplete and stopped for external
supervisor review** at the private-ingress security gate. The temporary database
bootstrap and Alembic migration completed, but no authenticated public Azure
prediction or persistence journey was run. The HTTPS frontend hostname is
reserved; all four Container Apps are currently stopped.

The supervisor's bounded showcase authorization allowed PostgreSQL's
Azure-services firewall rule after exact Container Apps outbound IPs proved
unavailable. It did not waive `docs/CURRENT_TASK.md` sections 3.3, 5 and 14,
which require backend and MLflow to remain unreachable directly from outside
the Container Apps environment. The previous 2026-10-17 handoff is preserved
byte-for-byte at `docs/history/SUPERVISOR_HANDOFF_20261017.md`.

## 2. Implemented and verified

- Reused the existing Southeast Asia resource group, Consumption Express
  environment, Standard ACR, registry-pull identity and frontend app. One
  PostgreSQL Flexible Server already existed; no duplicate was created.
- Used a temporary controlled `db-bootstrap` Container App. Express rejected
  Secret volumes, so the revision used Azure secret-backed environment
  references and mandatory PostgreSQL TLS. MLflow metadata restore initially
  failed on `permission denied for schema public`; granting the MLflow role
  `USAGE, CREATE` there fixed the restore. The application owner received the
  corresponding schema grant for migrations.
- Ran `python -m alembic upgrade head` through a temporary backend-image
  revision. A separate read-only `alembic current` log reported
  `0004_case_input (head)`. The completion log reported approved MLflow
  metadata ready. The app-user permission matrix and persistent cloud
  prediction data were **not** verified.
- Deployed backend at 1 vCPU/2 GiB, min 0/max 1, and MLflow at 0.5 vCPU/1 GiB,
  min 0/max 1, each by immutable ACR digest. A small entrypoint creates a
  private `/run/secrets` directory before dropping to UID 10001 because Express
  mounts a fresh `/run` and has no Secret-volume support.
- Updated the existing frontend to proxy `/api/v1/` to the backend over HTTPS
  with certificate validation. Nginx's default upstream verification depth
  caused 502 for Azure's three-certificate chain. Depth 3 passed `nginx -t`
  and the public frontend `/api/v1/health/live` request returned HTTP 200
  with client TLS verification result 0.
- A direct external request to the backend's own FQDN also returned HTTP 200
  while Azure reported `ingress.external=false`. Explicitly updating ingress
  to internal did not change this. Deny-all IP ingress returned 403 both
  directly and through the frontend. The `.internal.` FQDN returned 404 from
  the frontend replica. Allowing either the environment ingress IP or the
  observed frontend egress IP still yielded 403 through the proxy. These
  measurements cannot establish a private working route.
- Applied `Deny 0.0.0.0/0` ingress restrictions to `api` and `mlflow` and
  stopped `frontend`, `api`, `mlflow` and `db-bootstrap`. The PostgreSQL server,
  databases, ACR, images, app configurations and logs were retained.

## 3. Files and decisions

New or changed implementation is under `deployment/azure/`: bootstrap and
migration Bicep/scripts, backend and MLflow app Bicep/deployment scripts,
runtime wrapper, frontend proxy/deployment scripts. The current report was
updated in `docs/PROJECT_REPORT.md`; this handoff replaces the long prior
snapshot while preserving it under `docs/history/`. The frozen Python model,
preprocessing and XAI inputs were not changed.

The approved four-app topology was retained. Express sidecars are unsupported;
co-hosting services in one process/container would change the approved private
service boundaries and independent health behavior without sizing evidence.
A shared application header would not satisfy the network-isolation requirement.
No paid VNet, NAT, private DNS, load balancer, separate storage or logging
workspace was created. No Git commit, push, branch mutation, or local Docker
cleanup occurred.

## 4. Checks and exact results

| Check | Observed result |
|---|---|
| Bootstrap recovery logs | `database roles, databases, verified TLS and approved MLflow metadata ready`; no errors in the final observed log tail |
| Alembic verification log | `0004_case_input (head)` |
| Frontend image `nginx -t` | Exit 0, syntax OK |
| Public frontend to backend liveness, before security stop | HTTP 200; client TLS verification 0 |
| Direct public backend liveness with `external:false` | HTTP 200; security gate failed |
| Direct and proxied backend liveness with deny-all restriction | HTTP 403 and 403 |
| Narrow allow probes | Direct 403; proxied 403 |
| Final app running states | frontend Stopped; api Stopped; mlflow Stopped; db-bootstrap Stopped |
| Final backend/MLflow ingress restrictions | One `Deny 0.0.0.0/0` rule on each |
| PostgreSQL control-plane status | Ready, PG18, Burstable Standard_B1ms, HA Disabled, seven-day backup |
| PostgreSQL transport/firewall | `require_secure_transport=ON`; sole rule `AllowAzureServicesShowcase` from 0.0.0.0 to 0.0.0.0 |

No Python regression, browser prediction, save/history/reopen/rerun/reset,
audit persistence, cold start, CI/CD workflow, or final end-to-end check was
run during this continuation. The prior accepted local backend sizing test was
not repeated because its bound Python/model inputs did not change. No new ML
experiment or model metric is claimed.

## 5. Inventory, images, cost and limitations

The resource group contains exactly eight resources: `cae-aletheia-sea-01`
(Consumption Express environment), `acraletheiasea1017` (Standard registry,
admin disabled), `id-aletheia-pull-sea-01` (registry pull identity), Container
Apps `frontend`, `api`, `mlflow`, `db-bootstrap`, and PostgreSQL
`pg-aletheia-sea-1017`. The last app is temporary but retained pending safe
secret/evidence transfer and supervisor review. ACR usage reported 697,407,530
bytes against a 107,374,182,400-byte quota. All application replicas are
stopped; PostgreSQL remains Ready. Azure for Students spending-limit On was
checked by the deployment scripts. Free-tier eligibility was established in
earlier portal/preflight evidence, but this handoff does not assert zero actual
cost or a numeric future forecast; a fresh Cost Management amount was not
obtained.

Deployed image digests: frontend
`sha256:b8920e2338c285ba564e8a96c33b1dea208c6a580c2e1f49de1b87ad1d1fe073`;
backend `sha256:dcaa62439a3330f436fa0715f8559dd7310b13e3edec1a987210c7bbb3b60a86`;
MLflow `sha256:89e8c942fa146c61cbd9b2b7232d70509b584b458676d4d7ba6af0a498af08c8`.
The stopped temporary app currently points to the original backend digest
`sha256:4cddaada14267b60279364368d512a834e919ca19fe75523158872c5bbf37338`
for the migration verification command. Its last bootstrap image was
`sha256:a0b200958a71e8265f85f1dc86c0df57e80530e7110ceba5295d14b481df7a7a`.

Known limitations: the current Express environment returned an externally
reachable backend FQDN despite `external:false`; an ordinary frontend proxy
cannot bypass a deny-all ingress rule. MLflow's public UI was not confirmed
reachable, but isolation was not proved, so it is both denied and stopped.
PostgreSQL's Azure-services exception is a bounded showcase decision and
admits other Azure-origin traffic to the firewall layer; TLS and least-privilege
database authentication remain mandatory. Application-user permissions,
metadata artifact retrieval after a cloud restart, deployment pin, provisioned
reviewer token, CI/CD, and end-to-end persistence remain unverified or undone.

## 6. Evidence, unresolved questions and suggested next step

Inspect `deployment/azure/`, the current `docs/PROJECT_REPORT.md`, preserved
preflight evidence, the archived 2026-10-17 handoff, Azure ingress configuration
and restrictions, bootstrap/migration replica logs, ACR manifests, and current
Git status. The current public hostname is
`https://frontend.greenpond-767543dc.southeastasia.azurecontainerapps.io`,
but it is **not a verified application URL** while the apps are stopped.

The unresolved decision is how to obtain an Azure-supported, free private
activation route in this Express environment while retaining separate backend
and MLflow service boundaries. The external supervisor should review this
security gate and authorize a supported topology or a revised task before
the stopped apps are reopened. Do not delete the temporary app until Azure
secret references and migration evidence are safely retained. No commit or
push is authorized. A suitable future commit message, after a completed and
reviewed deployment, would be `feat: deploy audited showcase to Azure`.
