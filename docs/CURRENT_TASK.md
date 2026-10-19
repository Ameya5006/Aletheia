# CURRENT TASK — Azure Cloud Deployment Continuation and Project Closure

## 0. Revision-control and supersession notice

This 2026-10-17 revision completely supersedes every earlier Azure task, DNS-only credit exception and stopped-preflight network decision.

The following are historical findings, not current instructions:

- that one paid Private DNS zone was authorized;
- that PostgreSQL had to use private VNet integration;
- that changing Container Apps outbound IPs made the public PostgreSQL design automatically unacceptable.

There is now **no Private DNS or promotional-credit exception**. Paid private networking is prohibited. The currently authorized design is PostgreSQL public network access restricted to the Container Apps environment's exact reported outbound IP addresses, with verified TLS, least-privilege credentials, idempotent firewall reconciliation and a pre-demonstration connectivity check.

Do not stop merely because Container Apps outbound IPs can change. That risk is explicitly accepted for this bounded, non-sensitive student showcase and must be mitigated by the required reconciliation workflow. Stop only if Azure does not expose a finite exact list, an exact-IP firewall cannot be enforced, TLS verification cannot be maintained, or another stop condition in Section 14 applies.

Historical reports in `artifacts/azure-preflight/`, `docs/PROJECT_REPORT.md` or `docs/SUPERVISOR_HANDOFF.md` must remain preserved as evidence of earlier stopped attempts, but they do not override this file. Update those documents to distinguish historical blockers from the current authorized design.

## 1. Milestone objective

Deploy the approved Aletheia interactive case-prediction application to Microsoft Azure so that it runs independently of the developer laptop and can be shown through an Azure-managed HTTPS URL.

This is the final implementation milestone before project closure.

The deployment must use active Azure for Students free-service allowances for the bounded one-user showcase workload. The intended cash payment is INR 0 and the planned promotional-credit consumption is INR 0. No paid VNet integration, load balancer, public-IP resource, Private DNS zone, Private Endpoint, NAT Gateway or equivalent paid networking component is authorized.

Azure Database for PostgreSQL may use its public endpoint only under the tightly restricted firewall design in this task. This is a bounded student-showcase exception, not a production or clinical deployment pattern. The database must require TLS, reject unrestricted network access and accept traffic only from the exact currently reported outbound IP addresses of the deployed Azure Container Apps environment. Because those addresses can change, the deployment must include tested detection, reconciliation and pre-demonstration health-check procedures.

The deployed application must preserve the approved frozen model, preprocessing, calibration, explanations, evidence identities, persistence semantics, audit behavior, RBAC and interactive case workflow.

This milestone must not redesign the UI, retrain the model, add an LLM-generated prediction, implement public Signup, or access held-out data.

Stop for external supervisor review before committing or pushing.

---

## 2. Approved starting state

Original milestone starting state:

- Branch: `main`
- HEAD and upstream: `07415aaf9eb58b028e2f629d884199016ccbe13f`
- Upstream divergence: `0 ahead / 0 behind`
- Original Git status before the Azure milestone:

```text
 M docs/CURRENT_TASK.md
```

- Existing stash must remain unchanged:
  `c6b91a13bf4338e559dfaad49f850dd719f5ca47`
- The approved interactive workflow commit is:
  `feat: add interactive case prediction workflow`
- Local Docker and Stage 3 evidence must remain intact throughout this milestone.
- No local images, containers, volumes, databases, artifacts or source files may be deleted during this task.

The Azure account is an active `Azure for Students` subscription in the Bennett University tenant.

Known account state supplied by the user on 2026-10-16:

- Available promotional credit: INR 9,599 of INR 9,599.
- Recorded October cost at inspection: INR 0.
- Student credit expiry: 2027-06-26.
- The portal displayed free eligibility for PostgreSQL `Standard_B1ms` up to 750 hours and 32 GiB storage.
- The subscription Overview displayed current cost `0.00`, forecast `0.00`, zero free-service limits exceeded, no active resource usage and an `Upgrade` action, confirming that it had not been converted to Pay-As-You-Go at inspection.
- The strict zero-credit preflight completed without provisioning or deleting anything.
- Final Azure inventory after that preflight: zero resources.
- The first continuation preflight found that private PostgreSQL VNet integration requires a Private DNS zone. The second continuation preflight confirmed that a customer VNet for Container Apps also creates separately billed public-IP and load-balancer resources. No resources were provisioned in either attempt.
- The supervisor has rejected that paid private-network topology for this bounded showcase and has instead authorized the controlled public PostgreSQL design specified in this task.
- Container Apps outbound public IP addresses can change. The resulting availability risk is accepted only with exact-IP firewall rules, automated reconciliation, TLS, strong credentials, a pre-demonstration check and honest documentation.
- The preflight findings are preserved under `artifacts/azure-preflight/` and in the supervisor/project documentation.
- Documentation and dry-run cleanup changes produced by the stopped preflight are authorized task work. Record the exact current Git status; do not discard or overwrite those findings.
- The latest stopped continuation may therefore contain additional authorized modifications to `docs/PROJECT_REPORT.md`, `docs/SUPERVISOR_HANDOFF.md`, `artifacts/azure-preflight/PREFLIGHT.md` and related preflight evidence. Inspect and preserve the actual current state. Do not require the working tree to match the original one-file status above, and do not revert authorized preflight documentation merely to obtain a clean baseline.

Reverify this state before provisioning. Never record the subscription ID, tenant ID, access tokens, account email, passwords or private signing material in tracked files or verification artifacts.

---

## 3. Mandatory zero-cash and free-allowance boundary

Use the existing Azure for Students subscription only.

Promotional credit is not an authorized deployment budget. The architecture must have no intentionally metered paid component and must remain inside verified Azure for Students free-service allowances. No cash payment is authorized.

Mandatory safeguards:

1. Confirm the selected subscription is named `Azure for Students` and is enabled.
2. Confirm the subscription has not been upgraded to Pay-As-You-Go. Preserve sanitized portal evidence showing `Azure for Students`, current/forecast cost and the available `Upgrade` action. If Azure exposes an explicit spending-limit field, confirm it is enabled. Absence of that field or the inability of Azure CLI to query it is not by itself a blocker when the subscription still shows the Student offer and an unused `Upgrade` action.
3. Never upgrade the subscription to Pay-As-You-Go.
4. Never remove or weaken the spending limit.
5. Do not add a payment method as part of this milestone.
6. Inspect remaining credit, expiry, free-service eligibility, regional availability, quotas and displayed estimates before creating resources.
7. Provision no SKU unless its exact service class, tier, capacity and region are covered by an active free-service allowance or are intrinsically free.
8. Use consumption, burstable and scale-to-zero configurations.
9. Do not enable high availability, paid replicas, premium storage, geo-redundancy, dedicated Container Apps compute, paid private endpoints, NAT Gateway, static public IP, premium ingress, paid custom domains or unnecessary paid monitoring.
10. Configure a monthly Cost Management budget of INR 100, with notifications at 50%, 80% and 100%, if the subscription supports those values. This is an early-warning guardrail, not permission to spend INR 100.
11. Record that budget notifications are warnings and not hard spending caps.
12. Use the Azure-generated HTTPS domain. A purchased/custom domain is out of scope.

Azure may display a list price beside a free-service indicator. Acceptable free-eligibility evidence, in descending order, is: an account-specific portal free-service indicator; the subscription's free-services usage list together with the exact matching SKU/capacity; or the current official Azure for Students allowance together with proof that this subscription is still on that offer. Azure CLI's inability to expose account-specific free-benefit metadata is not by itself a blocker. Preserve the strongest available sanitized evidence and require exact SKU/capacity matching.

Stop before provisioning if free eligibility is missing or ambiguous for any resource. Stop if the complete deployment has a known nonzero planned charge. Do not silently substitute a paid resource.

### 3.0 No authorized paid infrastructure

- Do not create a Private DNS zone, custom VNet for Container Apps, Standard Load Balancer, standalone public-IP resource, NAT Gateway, Private Endpoint, DNS Private Resolver or Azure Firewall.
- Do not treat available promotional credit as authorization for any of those resources.
- If Azure will automatically create a separately billed managed resource for the chosen topology, stop before deployment and report it.
- Usage covered by an active free grant is acceptable only when the exact SKU and limits are verified and recorded.

Preferred region: `centralindia`. Verify that every required free-tier-compatible service and SKU is available there. Use the nearest single alternative region only if necessary, still free-tier eligible, and documented before provisioning.

### 3.1 PostgreSQL free-tier requirements

Use exactly one Azure Database for PostgreSQL Flexible Server:

- Compute tier: `Burstable`.
- Exact compute SKU: `Standard_B1ms`.
- Capacity: 1 vCore and 2 GiB RAM.
- Storage: no more than 32 GiB.
- Free allowance: up to 750 compute hours per month, 32 GiB data storage and included backup storage as displayed by the subscription.
- High availability: disabled.
- Zonal redundancy: disabled.
- Geo-redundant backup: disabled.
- Read replicas: none.
- Backup retention: the lowest defensible supported value, no more than seven days unless the free offer requires otherwise.
- One server must host the separate application and MLflow databases or schemas; do not provision a second PostgreSQL server.

Before creation, confirm the portal or CLI result corresponds to `Standard_B1ms`, not `B2s`, General Purpose, Memory Optimized or another SKU. The portal must show the applicable free-compute and free-storage indicators. Stop on any mismatch.

### 3.2 Container Registry free-tier requirements

- Use the single Standard-tier Azure Container Registry included with Azure for Students for 12 months.
- Do not create a separately charged Basic registry when the included Standard registry is available.
- Create only one registry.
- Keep total registry storage below the included 100 GB.
- Use authenticated access; do not enable anonymous pulls.
- Prefer managed identity from Container Apps over permanent registry credentials.
- Preserve only the final immutable images and any preceding image required for demonstrated rollback.
- Stop if the subscription does not show the Standard registry free benefit as active.

### 3.3 Container Apps free-tier requirements

- Use an Azure Container Apps environment with the Consumption workload profile.
- Do not create a Dedicated workload profile.
- Configure each long-running application with `minReplicas: 0` and `maxReplicas: 1` initially.
- Use the smallest supported CPU/memory combination that passes startup, health, prediction, persistence and browser verification without CPU starvation or OOM termination.
- Do not use an always-running paid replica to hide cold-start behavior.
- Keep aggregate use within the monthly free grant of 180,000 vCPU-seconds, 360,000 GiB-seconds and 2 million requests.
- Expose only the frontend through external HTTPS ingress.
- Give the backend and MLflow internal HTTP ingress or another free activation path that can wake them from zero replicas.
- Do not disable ingress on a service that needs an HTTP request to scale from zero unless a tested free custom scaler is supplied.
- Do not configure CPU-only or memory-only scaling rules that prevent scale-to-zero.
- Use the default Azure-managed HTTPS domain.

### 3.4 Persistent artifact storage requirements

- Do not create a separate Azure Storage account, Azure Files share or Blob container unless a future task explicitly authorizes it.
- Package only the approved frozen MLflow model/release artifacts into a release-specific, read-only MLflow image stored in the already authorized Azure Container Registry.
- Bind the artifact bundle to its SHA-256 identity and immutable image digest. Do not use `latest`.
- Keep MLflow registry/metadata state in the managed PostgreSQL database. Configure artifact URIs and container paths reproducibly so the MLflow service can serve the packaged artifacts after scale-from-zero and revision replacement.
- The cloud application must not train, register, overwrite or upload model artifacts at runtime. Cloud model publication is out of scope; a new model requires a separately reviewed image/release.
- Run the MLflow process and artifact directory read-only wherever the image/runtime permits. Use writable ephemeral space only for bounded temporary runtime files, never as the authoritative artifact store.
- Verify that the backend retrieves the exact approved artifact through MLflow after cold start, restart, revision replacement and rollback.
- If the existing MLflow/runtime contract cannot operate with immutable packaged artifacts without weakening integrity, changing the frozen model/release or requiring a paid persistent store, stop and report the exact incompatibility.

### 3.5 Monitoring requirements

- Use only included Azure Monitor and Log Analytics allowances.
- Minimize application, ingress and diagnostic log volume.
- Do not log tokens, secrets, private keys, complete user submissions or sensitive database values.
- Use no more than 30 days of retention, or the shortest supported free retention value.
- Do not enable paid Application Insights features, continuous export, premium monitoring or unnecessary diagnostic categories.
- Record ingestion volume and free allowance at handoff.

### 3.6 Network and cost requirements

- Do not purchase a NAT Gateway, Application Gateway, Front Door, static public IP, Private Link endpoint, DNS Private Resolver or paid public DNS service.
- Prefer free same-region service communication.
- Do not create a customer VNet for the Container Apps environment.
- Deploy PostgreSQL with public network access enabled only so its firewall can accept the Container Apps environment's exact outbound IP addresses.
- Never use `0.0.0.0/0`, `0.0.0.0` through `255.255.255.255`, an unnecessarily broad CIDR/range, or “Allow public access from any Azure service within Azure.”
- Create one single-address PostgreSQL firewall rule per currently reported Container Apps outbound IPv4 address. Each rule's start and end address must be identical.
- Re-query the Container Apps environment after deployment and immediately before every cloud verification. Treat Azure's reported outbound-IP list as the source of truth.
- Implement an idempotent PowerShell reconciliation script that adds missing exact-IP rules, removes obsolete deployment-managed rules and leaves unrelated rules untouched. It must support dry-run output and must never broaden a rule to recover connectivity.
- Tag or name deployment-managed firewall rules unambiguously so reconciliation cannot delete user-managed rules.
- Require PostgreSQL TLS with full certificate and hostname verification where supported by the selected drivers. Never disable certificate validation to fix connectivity.
- Use strong generated administrator and application credentials, store them only in Azure-native secret configuration or transient local process memory, and create least-privilege application and MLflow roles.
- Do not persist database credentials in tracked files, command transcripts, shell history, image layers, Bicep parameter files or evidence.
- Add a pre-demonstration command that rechecks outbound IPs, performs a dry run, reconciles only after an explicit confirmation flag, verifies DNS/TLS/database connectivity, warms the application and reports readiness without printing secrets.
- Record that an Azure outbound-IP change can temporarily interrupt database connectivity until reconciliation is run. Do not claim automatic self-healing unless a free, tested Azure-native mechanism is actually implemented.
- Keep the Container Apps environment on the Consumption workload profile and avoid any topology that creates billed Dedicated compute or billed network resources.

---

## 4. Required preflight

Before changing implementation or creating cloud resources:

1. Read completely:
   - `AGENTS.md`
   - this task
   - `docs/SUPERVISOR_HANDOFF.md`
   - `docs/PROJECT_REPORT.md`
   - `docs/ARCHITECTURE.md`
   - existing deployment Dockerfiles, Compose files, entrypoints and verification helpers
2. Record:
   - branch, HEAD and upstream
   - divergence
   - exact Git status
   - stash identity
   - Docker context and health
   - Azure CLI version
   - selected Azure subscription name and enabled state
   - remaining credit and expiry without recording account identifiers
3. Confirm the subscription remains on the Azure for Students offer and no Pay-As-You-Go conversion is requested. Use the evidence hierarchy in Section 3; do not repeat the previous stop solely because Azure CLI lacks an explicit spending-limit property.
4. Inventory every proposed Azure resource with exact region, tier, SKU, capacity, free allowance and displayed estimate.
5. Preserve sanitized evidence, using Section 3's evidence hierarchy, that each proposed resource is covered by an active free allowance or is intrinsically free.
6. Do not record Azure subscription or tenant IDs in repository files.
7. Calculate and preserve hashes for all previously protected evidence and task inputs.
8. Inspect the existing production architecture, authentication verifier, JWKS/public-key requirements, MLflow storage, database migrations, release provisioning, reverse proxy, readiness and backup/restore behavior.
9. Verify the cloud deployment can preserve the existing security boundary without introducing a parallel authentication system.
10. Check the repository and Git history for accidentally tracked credentials before provisioning.
11. Extend the existing preflight record rather than concealing or replacing its stopped-run findings.
12. Confirm the proposed Bicep deployment contains no Private DNS zone, customer Container Apps VNet, Standard Load Balancer, standalone public-IP resource, NAT Gateway, Private Endpoint, DNS Private Resolver or other intentionally paid resource.
13. Calculate worst-case first-month and normal-month usage against each free allowance. Stop if planned use exceeds an allowance or has a known nonzero charge.
14. Query and record the Container Apps environment's complete outbound-IP list before creating PostgreSQL firewall rules. If Azure does not expose a finite exact list, stop rather than widening database access.
15. Review the firewall-reconciliation algorithm and its deletion scope before allowing it to mutate any rule.

Do not create Azure resources until architecture, identity, security and free-allowance continuation preflight all pass. The inability to use paid private VNet integration is already resolved by the authorized design in this task and must not trigger the old Private-DNS stop condition again.

---

## 5. Target Azure architecture

Implement the smallest secure architecture satisfying the existing contracts and Section 3.

Required service classes:

- One Student-included Standard Azure Container Registry for immutable backend, frontend and MLflow images.
- One Azure Container Apps environment using only its Consumption workload profile and no customer VNet.
- One externally reachable frontend/NGINX app using Azure-managed HTTPS, `minReplicas: 0`, `maxReplicas: 1`.
- One backend API app reachable only through the frontend reverse proxy/internal Container Apps networking, `minReplicas: 0`, `maxReplicas: 1`.
- One MLflow app reachable only by the backend over internal networking, `minReplicas: 0`, `maxReplicas: 1`.
- One free-eligible PostgreSQL Flexible Server `Standard_B1ms` with 32 GiB maximum storage, using its public endpoint with mandatory TLS and exact Container Apps outbound-IP firewall rules only.
- Separate application and MLflow databases or schemas on that one server, with least-privilege credentials.
- Immutable frozen MLflow artifacts packaged in a release-specific read-only image and persisted through Azure Container Registry; no separate Azure storage resource.
- Conservative free-allowance logging.
- Container Apps secrets or an equally secure Azure-native secret mechanism.
- A migration/provisioning Container Apps job that runs once, fails closed and is safe to repeat.
- Cost budget notifications where supported.
- An idempotent exact-IP PostgreSQL firewall reconciliation and pre-demonstration health/warm-up script.

Codex may choose a tightly coupled multi-container Container App only if it preserves private service boundaries, persistence and independent health behavior and is demonstrably more reliable within free allowances. Document the decision. No topology may expose backend, MLflow or PostgreSQL without strict network restriction.

Use infrastructure as code, preferably Bicep, plus small PowerShell orchestration scripts suitable for Windows.

Use a reproducible two-phase deployment because PostgreSQL firewall rules depend on the created Container Apps environment's outbound IPs:

1. Deploy only the verified free resources needed to create the Container Apps environment and registry integration.
2. Query the environment's complete outbound-IP list and fail if it is empty, malformed or not finite.
3. Deploy PostgreSQL and one exact single-address firewall rule for each current outbound IP.
4. Deploy migration/provisioning jobs and application revisions.
5. Query the outbound-IP list again before verification; reconcile only deployment-managed exact-IP rules if it changed.

Both phases and reconciliation must be safe to repeat. A failed second phase must leave an inventory that can be inspected without automatically deleting resources or hiding possible cost exposure.

Expected repository area:

```text
deployment/azure/
```

Include, as applicable:

- Bicep templates/modules
- non-secret parameter examples
- free-tier preflight script
- deployment script
- verification and cold-start script
- reviewer-token helper
- status/warm-up helper
- Azure resource teardown script
- operating, cost and recovery documentation

The teardown script must never run automatically.

---

## 6. Container image requirements

1. Build deployment images from the reviewed commit and authorized working tree only.
2. Use local Docker builds and push to the included registry unless Azure remote build is explicitly confirmed to incur no charge under this subscription.
3. Remote build must not be used merely to avoid local storage if it can consume promotional credit.
4. Use immutable commit-based tags and record resulting registry digests.
5. Never use mutable `latest` as deployment evidence.
6. Preserve existing pinned dependencies and frozen model identities.
7. Do not include `.git`, local artifacts, test-only fixtures, credentials, private keys, ignored evidence or local databases.
8. Scan changed cloud images and generate matching SBOM and licence inventories.
9. Bind every scan/SBOM/licence result to the exact deployed image digest.
10. Do not claim that an image is vulnerability-free.
11. Preserve and document existing vulnerability dispositions where components are unchanged.
12. Keep registry usage within the included 100 GB and document the final total.
13. Build the MLflow image with the exact approved frozen artifact bundle, record the bundle hash before and after the build, and prove that no extra model/test fixture is included.
14. Run the deployed artifact path read-only where supported and prove that runtime operation does not mutate the packaged artifact bundle.

---

## 7. Database and persistence

1. Use the single managed free-eligible PostgreSQL server specified in Section 3, with public network access restricted to the exact current Container Apps outbound IPs.
2. Require encrypted PostgreSQL connections.
3. Require certificate and hostname verification where supported; do not use a TLS mode that accepts an unverified server certificate.
4. Do not allow unrestricted public database access or the broad Azure-services exception.
5. Create least-privilege application and MLflow database identities.
6. Run Alembic migrations exactly once through a controlled Container Apps job or equivalent process that originates from the allowlisted environment.
7. Provision the approved application release without retraining, refitting or recalibrating.
8. Confirm prediction, audit, idempotency and analysis-history records survive:
   - Container App revision replacement
   - replica restart
   - automatic scale-to-zero and scale-from-zero
9. Confirm MLflow metadata and model artifacts survive the same operations.
10. Keep PostgreSQL backup/retention within included limits.
11. Produce and verify one recoverable logical backup or included Azure-native recovery checkpoint without paid storage.
12. Verify that a source IP not present in the firewall allowlist cannot connect, without attempting password brute force or disruptive probing.
13. Never import held-out data, local test fixtures or patient-identifiable data.

Only non-identifiable manually entered showcase cases may be used.

---

## 8. Authentication and access

Full Login, Signup and external application-level OIDC remain deferred.

The cloud deployment must preserve the existing provisioned-token and RBAC behavior unless an Azure infrastructure access layer can be added for free without replacing or weakening application authorization.

Requirements:

1. No anonymous user may run predictions, save analyses, access history, record reviews or access protected audit data.
2. Public evidence routes may remain public only if they reveal no protected records, secrets or user case data.
3. Use fresh deployment-specific signing/verification material.
4. Never commit or embed a private signing key.
5. Do not write access tokens to tracked files, images, shell history, logs or verification evidence.
6. Provide only public verification material to the verifier.
7. Provide a documented secure command for generating a fresh short-lived reviewer token.
8. The command must not require exposing private material in Git.
9. Test expired, malformed, wrong-audience, wrong-issuer and insufficient-role tokens.
10. Preserve existing role enforcement.
11. Do not build a custom password database or superficial Signup system.
12. If secure provisioned-token operation cannot be achieved without exposing signing material or weakening authorization, stop before exposing the application.

Microsoft Entra protection may be used only if it is free for this subscription and works for teacher review. It must not silently replace application RBAC or create unsupported completion claims.

---

## 9. Networking, HTTPS and automatic operation

1. Expose only the frontend ingress publicly.
2. Require HTTPS and redirect or reject insecure HTTP where supported.
3. Proxy API requests through the frontend same-origin route.
4. Keep backend and MLflow ingress internal.
5. Keep PostgreSQL inaccessible from arbitrary public sources: its public endpoint may accept only exact current Container Apps outbound IPs and must still require valid TLS and database credentials.
6. Preserve security headers, request limits and timeout semantics unless a change is justified and tested.
7. Verify browser and API CORS behavior.
8. Verify that guessed public backend, MLflow and database addresses cannot be used.
9. Do not weaken the fixed registry deadline merely to hide cold-start failures.
10. Do not use a paid always-on replica or scheduled keep-alive.
11. Configure the application so the user does not manually start or stop Azure resources.
12. The public frontend request must activate the frontend automatically.
13. Frontend/backend traffic must activate the backend automatically.
14. Backend/MLflow traffic must activate MLflow automatically.
15. Eligible Container Apps must return to zero replicas after inactivity.
16. Provide a free status/warm-up command for use two to three minutes before a planned demonstration.
17. Record the final public URL without credentials or tokens.
18. Run the pre-demonstration networking command from a clean state and prove that unchanged IPs produce no firewall mutation.
19. In a safe test scope, prove reconciliation removes an obsolete deployment-managed firewall rule while preserving unrelated rules.

---

## 10. Required cloud workflow and cold-start verification

Perform the following against the actual Azure deployment:

1. Query and record the current Container Apps outbound-IP list.
2. Dry-run firewall reconciliation and confirm no broad or unrelated rule is proposed.
3. Reconcile deployment-managed rules if necessary, then prove every managed rule is one exact current outbound IP and no obsolete managed rule remains.
4. Verify PostgreSQL TLS certificate and hostname validation from the deployed application/job context.
5. Confirm frontend, backend and MLflow use `minReplicas: 0` and `maxReplicas: 1`.
6. Leave the application unused long enough for all eligible apps to reach zero replicas.
7. Record the zero-replica state.
8. Open the Azure HTTPS URL from a real browser without manually starting resources.
9. Record time until the frontend is usable and time until the first authenticated prediction succeeds.
10. Confirm public evidence reveals no protected case data.
11. Connect with a fresh reviewer token.
12. Open an empty New Analysis form.
13. Enter one reasonable, non-identifiable 13-field case.
14. Run the frozen model prediction.
15. Display calibrated probability, descriptive threshold category, influential reference contrasts, model-level stability evidence, model/release/evidence identities, and prediction/audit identifiers.
16. If a cold-start timeout occurs, verify the existing Retry and idempotency behavior resolves the outcome without producing an undisclosed duplicate. Do not conceal the timeout.
17. Save the analysis.
18. Open Analysis History and reopen the immutable record.
19. Load its inputs into a new analysis, change one value and rerun.
20. Confirm a new prediction and audit identifier and confirm the original remains unchanged.
21. Reset browser form state without deleting saved history.
22. Replace or restart the application revision.
23. Confirm saved history, audit records, MLflow metadata and model artifacts remain available.
24. Re-query outbound IPs after revision replacement, perform reconciliation if needed and confirm connectivity without broadening access.
25. Allow the apps to scale back to zero and record the final state.
26. Confirm no user-facing synthetic/demo/demonstration wording or preloaded case is rendered.
27. Confirm no LLM generated the prediction or authoritative explanation.

Document that the reviewer should open or warm the application two to three minutes before a presentation because zero-cost scale-to-zero can introduce cold-start latency.

---

## 11. Verification requirements

Run and record exact commands, durations and exit codes.

### Repository and implementation

- Git whitespace check.
- Ruff check and formatting verification for changed Python.
- Relevant Python unit/integration/deployment tests.
- Frontend tests.
- Frontend typecheck, lint, formatting and production build.
- OpenAPI contract verification.
- Compose validation for unchanged local deployment compatibility.
- Infrastructure-as-code validation/lint.
- Secret scanning of changed and staged files.

### Local regression policy

The previously completed offline regression may be reused only if every bound Python/model/data input remains byte-identical.

If any Python application, model-loading, preprocessing, persistence, migration, authentication or prediction input changes, rerun the complete offline regression once.

Do not combine focused runs into a claimed complete regression.

### Azure verification

- Resource deployment state and exact resource inventory.
- Free-entitlement evidence for every resource.
- Exact tier, SKU, capacity and region.
- Image digest identity.
- HTTPS, health and readiness.
- Internal-service isolation.
- Exact PostgreSQL firewall rules matching the current Container Apps outbound-IP list.
- Idempotent firewall reconciliation, safe obsolete-rule removal and preservation of unrelated rules.
- TLS certificate/hostname verification and rejection of a non-allowlisted source.
- Authentication rejection/acceptance cases.
- Real browser prediction journey from a zero-replica cold state.
- Measured cold-start timings.
- Automatic scale-from-zero and return-to-zero.
- Persistence after restart/revision replacement.
- Database migration state.
- MLflow metadata and artifact retrieval.
- Backup/recovery evidence.
- Logs, metrics and ingestion volume.
- No secret leakage.
- Accessibility across required states and widths.
- Changed-image scans, SBOMs and licence inventories.
- Spending-limit state and budget notifications.
- Current Cost Management result.
- Rollback to the preceding known-good image/revision, followed by restoration of the final revision.

A retry or focused rerun may validate a diagnosed failure, but failed attempts must remain documented.

### Cost verification record

Preserve sanitized evidence of:

- Azure for Students subscription name and enabled state.
- Spending limit enabled.
- Remaining credit and expiry before and after provisioning.
- PostgreSQL `Standard_B1ms`, 32 GiB and free-offer indicators.
- Included Standard Container Registry and final storage usage.
- Container Apps Consumption profile, CPU/memory allocations and replica limits.
- MLflow artifact-image digest, embedded bundle hash, registry storage usage and proof that no separate storage resource was created.
- Monitoring retention and ingestion volume.
- Budget notifications.
- Azure displayed estimates and current Cost Management result.

Explicitly distinguish:

- cash charged, which must remain INR 0,
- promotional credit consumed and forecast, with planned consumption of INR 0,
- free-tier usage,
- forecast normal monthly usage,
- any delayed Azure cost reporting.

The milestone is not complete merely because no bank payment was taken. Every deployed resource must be covered by a verified free allowance or be intrinsically free, and the design must have no known planned charge. Delayed cost reporting must be disclosed.

---

## 12. Documentation requirements

Update:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/PROJECT_REPORT.md`
- `docs/SUPERVISOR_HANDOFF.md`

Document:

- Azure architecture and data flow
- purpose of every Azure resource
- why Azure Container Apps Consumption was selected
- every free allowance used and its expiry/limits
- why the paid private-network topology was rejected after preflight
- why tightly restricted public PostgreSQL access was accepted for this bounded non-sensitive showcase
- the exact outbound-IP firewall model, TLS controls, reconciliation procedure and residual availability/security risks
- public/private network boundaries
- secrets and authentication approach
- database and artifact persistence
- migration process
- deployment and rollback commands
- backup and recovery
- monitoring and logs
- automatic scale-to-zero and cold-start trade-offs
- measured cold-start timings
- exact image/release/model identities
- exact cloud verification results
- cash cost, credit consumption and free-tier usage separately
- unresolved limitations
- full Login/Signup/OIDC as future scope
- no clinical validation claim
- no vulnerability-free claim
- all failures encountered and their fixes
- operating instructions for teacher review
- how to generate a fresh reviewer token securely
- how to warm the application before a presentation
- how to inspect costs and free-tier consumption
- how to remove all Azure resources when no longer needed

`PROJECT_REPORT.md` must remain suitable for interviews, viva and project defence.

---

## 13. Local laptop cleanup boundary

The user ultimately wants to free local laptop storage, but cleanup is not authorized in this milestone.

During this task:

- Do not delete local Docker images.
- Do not delete containers.
- Do not delete volumes.
- Do not prune Docker.
- Do not delete the repository or `.venv`.
- Do not remove local evidence.
- Do not delete the existing stash.

Prepare a separate dry-run cleanup inventory showing:

- stopped Aletheia containers
- Aletheia-specific images
- Aletheia-specific volumes
- approximate reclaimable storage
- items that must be preserved
- exact reversible backup requirements

Do not execute cleanup.

Local cleanup will be authorized only after:

1. Azure deployment passes external supervisor review.
2. Cloud changes are committed and pushed.
3. Persistence and recovery are verified.
4. Repository is safely present on GitHub.
5. Required local evidence is backed up.
6. The user explicitly approves the exact deletion list.

---

## 14. Stop conditions

Stop safely before creating or changing the affected resource if:

- The Azure for Students subscription is not enabled.
- The spending limit is disabled or Azure requests conversion to Pay-As-You-Go.
- An exact required SKU is not covered by an active free allowance.
- The design has a known nonzero planned charge or can exceed a verified free allowance.
- PostgreSQL is not `Standard_B1ms` with no more than 32 GiB storage.
- The portal does not display the applicable PostgreSQL free indicators.
- The included Standard Container Registry benefit is unavailable.
- A Dedicated Container Apps profile or nonzero minimum replica is required.
- Secure persistence requires paid storage.
- Secure operation requires a paid gateway, load balancer, public-IP resource, endpoint, VNet integration, resolver or paid DNS resource.
- Azure does not expose a finite exact Container Apps outbound-IP list suitable for PostgreSQL firewall rules.
- PostgreSQL connectivity requires `0.0.0.0`, “Allow Azure services,” an unrestricted range or any rule broader than a single exact authorized IP.
- Full TLS certificate and hostname verification cannot be maintained by the deployed clients.
- Firewall reconciliation cannot prove that it changes only deployment-managed exact-IP rules.
- Required regional quota or provider registration is unavailable.
- PostgreSQL would require unrestricted public access.
- Backend or MLflow would require public external ingress.
- Authentication requires committing or exposing private signing material.
- A protected artifact differs unexpectedly.
- Held-out data access would be required.
- Frozen model, release or evidence identity would change unexpectedly.
- Deployment would require weakening security or timeout semantics without approval.
- A secret appears in Git, logs or generated evidence.
- Recovery, persistence, scale-from-zero or scale-to-zero cannot be demonstrated.
- A destructive local cleanup action would be required.
- Any Azure action requires adding a payment method or removing spending protection.

Do not conceal partial resources after a failure. Report their names, deployment state and possible cost exposure without printing secrets. If a partial paid resource was accidentally created, stop and request explicit approval before destructive cleanup unless the infrastructure deployment can safely roll it back automatically as part of the same failed transaction.

---

## 15. Acceptance criteria

The milestone is acceptable only when:

- Azure architecture is reproducible through tracked infrastructure code.
- Every deployed resource is covered by an active free allowance or is intrinsically free.
- Cash cost is INR 0 and planned promotional-credit use is INR 0; delayed Azure cost reporting is disclosed.
- PostgreSQL is exactly free-eligible `Standard_B1ms` with no more than 32 GiB.
- The single included Standard Container Registry is used and remains below 100 GB.
- Container Apps use the Consumption profile with minimum zero and maximum one replica.
- Frontend, backend and MLflow automatically scale from zero and return to zero.
- Only the frontend has public external ingress.
- The public URL uses Azure-managed HTTPS.
- Backend and MLflow are internal. PostgreSQL's public endpoint is protected by exact current Container Apps outbound-IP firewall rules, mandatory verified TLS and least-privilege credentials.
- No customer Container Apps VNet, Private DNS zone, Standard Load Balancer, standalone public-IP resource, NAT Gateway, Private Endpoint or DNS Private Resolver exists.
- The firewall reconciliation and pre-demonstration health/warm-up commands are documented, idempotent and tested.
- Secrets and private signing material are absent from Git and images.
- Managed PostgreSQL is encrypted and persistent.
- MLflow metadata and artifacts are persistent.
- Database migrations and release provisioning are reproducible.
- A real cloud browser workflow passes end to end from a cold state.
- Cold-start behavior and timings are documented honestly.
- Authentication and RBAC remain enforced.
- Saved analyses survive revision replacement/restart and scale-to-zero.
- Backup/recovery and rollback are demonstrated.
- Exact deployed image digests are recorded.
- Changed images have digest-bound scans, SBOMs and licence inventories.
- Spending protection, budget notifications and cost-inspection instructions are documented.
- Current Cost Management and remaining-credit evidence are preserved without account identifiers.
- No product-facing synthetic/demo wording or preloaded case appears.
- No model retraining, refitting, recalibration or held-out access occurred.
- Local Docker data remains untouched.
- Protected evidence remains unchanged.
- Final Git status is exact and fully reported.
- No commit or push occurs.
- Work stops for external supervisor review.

Recommended eventual commit message:

```text
feat: deploy Aletheia on Azure
```
