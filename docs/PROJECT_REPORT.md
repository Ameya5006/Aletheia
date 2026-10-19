# Aletheia — Project Report

## Current Azure Workload Profiles deployment and CI preparation (2026-10-19)

### Final closure continuation (2026-10-19)

**First hosted run and bounded repair.** Commit
`aa8c5179704956bc1964fed6e16ca1591678a154` was pushed successfully under the
explicit one-time exception. [Hosted run 39261782677](https://github.com/Ameya5006/Aletheia/actions/runs/39261782677)
failed at frozen-input verification before Azure login or deployment. The
approved manifest hashes Windows CRLF bytes for two text inputs; Linux Git
checkout uses LF. The checker now accepts only the exact LF-to-CRLF conversion
against the unchanged approved hash. Three focused regression cases verify LF,
CRLF and rejection of content changes. Frozen manifests, model and evidence
bytes remain unchanged. GitHub also echoed job environment identifiers, so the
same three non-secret IDs were encrypted into repository secret settings for
automatic log masking. Required repository variables remain configured; no
Azure client secret, certificate or long-lived Azure credential was added.
The workflow reads masked settings and continues to use OIDC federation.

The second [hosted run 39262552221](https://github.com/Ameya5006/Aletheia/actions/runs/39262552221)
passed the frozen check but reported 7 tests passed and 39 fixture errors: the
model/aggregate release files are intentionally ignored and absent from a fresh
checkout. No deployment ran. The repair retrieves only the ten approved frozen
fixture files from the existing backend digest after OIDC login, verifies all
42 approved release-file hashes, and restores the two original text newline
representations only in the disposable runner checkout. It pins test Python to
the approved 3.12.10 and provides pinned PostgreSQL 18 in the GitHub runner for
the existing real-transaction tests. All application test selections are retained
for deployment runs; untrusted pull requests run artifact-free CI unit/frontend
checks without Azure access. A local isolated-checkout check matched all 42
hashes and rejected a deliberately damaged fixture; original inputs were unchanged.
The preliminary incomplete patch was rejected by automatic approval review
before applying; the completed patch supplies retrieval and retains deployment
test coverage. No application behavior or Azure topology changed.

The third [run 39263626020](https://github.com/Ameya5006/Aletheia/actions/runs/39263626020)
failed during runner service initialization, before checkout or Azure login:
the runner passed single quotes literally in Docker's health command and Docker
reported `unknown shorthand flag: 'U' in -U` (exit 125). Replacing the option's
single quotes with double quotes preserves the same health check and corrects
runner argument parsing. The failed log is retained; Azure was unchanged.

The fourth [run 39263931188](https://github.com/Ameya5006/Aletheia/actions/runs/39263931188)
passed service initialization and frozen checks, then Azure returned
`AADSTS700213`: its single federated credential used the old name-only subject.
The actual GitHub assertion uses the documented immutable owner/repository-ID
format. Authenticated repository metadata confirmed both IDs. The existing
credential was updated to the exact `main` subject in `github-oidc.json`;
readback confirmed one credential, unchanged issuer/audience, and no new Azure
password/certificate or role assignment. The original trust and failed run are
preserved. See [GitHub's OIDC reference](https://docs.github.com/en/actions/reference/security/oidc).

The fifth [run 39264655113](https://github.com/Ameya5006/Aletheia/actions/runs/39264655113)
verified OIDC, frozen fixture retrieval and all 46 focused backend tests (2
warnings, 6.60 seconds); frontend lint/type checks and all 81 tests also passed.
The contract exporter then failed with `spawnSync .../.venv/bin/python ENOENT`:
hosted setup-python supplies Python on PATH rather than a repository `.venv`.
The workflow now uses the exporter's existing `ALETHEIA_PYTHON=python` override.
The real contract comparison remains mandatory before deployment; untrusted PRs
cannot fetch the private frozen fixtures and run only artifact-free checks.
No frontend application/image change or Azure deployment occurred in these runs.

The sixth [run 39265385717](https://github.com/Ameya5006/Aletheia/actions/runs/39265385717)
passed OIDC, backend/frontend tests, real contract export, frontend build,
credential scanning and immutable ACR image builds/pushes. The live topology
guard and Bicep validation passed. What-if then supplied human-formatted output
despite `-o json`, causing the JSON parser to stop before migration or app update.
Azure CLI help confirms `--no-pretty-print` is required to use the output format.
The shell boundary reproduced two failing cases before adding that one flag;
the previous failed image attempts remain in ACR and no resource was deleted.

During [run 39266540207](https://github.com/Ameya5006/Aletheia/actions/runs/39266540207),
the structured what-if gate passed and the controlled migration emitted
`aletheia-migration-complete 0004_case_input`, independently read without
printing raw logs. Its controller did not advance. Installed CLI implementation
and provider operations show console logs first call
`Microsoft.App/containerApps/getAuthToken/action`; the existing CI role granted
logstream data access but omitted this action. A new custom role grants only
that action at the release-operator app scope. Fresh verification matches all
four role templates and ten exact assignments; the previous nine assignments
and main-only federation remain unchanged. No API/frontend/MLflow token scope,
exec/secret-list/delete action, client credential or paid service was added.
The running hosted controller still needs to demonstrate successful completion.

The new operator backend digest
`sha256:b4b741f0ab70c22a055400b249b13cfea52c3057f3976d610a50ee16434ea2ec`
has fresh exact-digest vulnerability/SBOM commands exiting 0, with the same
1 critical / 63 high / 112 medium / 105 low / 1 unknown retained findings.
Its raw/complete inventories contain 239/240 components and 771/772 licence
entries. Native SQLite 3.54.0 still matches the approved binary hash. The first
new scan wrapper failed while saving a Unicode log on Windows; its JSON and
empty log are retained, and the UTF-8 retry records successful command exits.

Run 39266540207 eventually reported the controller's missing completion marker,
stopped the operator in `finally`, and invoked the real hosted rollback branch.
Both already-active healthy revisions remained at 100% traffic; Azure's
`RevisionAlreadyInRequestedState` activation responses were handled. This proves
hosted recovery execution on a pre-update failure, separately from the earlier
completed manual live revision rollback. Run 39269266858 again reached migration
with all tests/builds passing; an independent read found its head marker, but
the controller still discarded its underlying CLI errors. The obsolete run was
cancelled for replacement and the operator explicitly stopped; API/frontend
images and traffic remained the approved `api--0000003` / `frontend--0000002`.

The bounded `ci-log-marker.py` observer now captures CLI output privately with a
30-second per-read timeout, checks for credential-like content before disclosure,
and returns only completion/probability or sanitized error classification/action
names. The controller addresses its exact new revision, enforces its intended
15-minute wall-clock polling bound, stops on authorization/security failures,
and retains `finally` cleanup. Four focused tests first failed, then passed
(0.10s); lint/format and PowerShell parsing passed. A read-only observation of
revision 5 returned only `{"status": "complete"}`. No inference deadline or
application behavior changed. Hosted execution of this repair is still pending.

The bounded observer in [run 39272451787](https://github.com/Ameya5006/Aletheia/actions/runs/39272451787)
reported `ERROR: Could not find a replica for this app`, while the owner read
the running replica's migration marker. The diagnostic run was cancelled to
retrieve its log; the operator was stopped and serving images/traffic preserved.
Static CLI validator inspection shows log access first lists revision replicas,
and the provider registers `Microsoft.App/containerApps/revisions/replicas/read`.
That required read was also absent from CI's scoped grants. The existing
operator-only role now includes this read plus getAuthToken; no new role or
assignment was created, and the count remains ten. The next hosted run must
verify replica discovery, migration observation and the remaining deployment.

**Completed scope and sequence.** The remaining work reused the completed
frontend, cloud/browser/persistence, live rollback and isolated backup/restore
checks. Five backup file sizes and SHA-256 values still match their manifest;
the preserved restore result reaches `0004_case_input`, the approved active
release, one registry model, readiness 200 and prediction 201. No new backup,
restore, cloud prediction, browser journey, persistence restart, live rollback,
frontend build or frontend vulnerability scan was run. Prettier made only the
requested layout correction to `frontend/browser/cloud.spec.ts`; the complete
frontend formatting check now passes.

**Exact deployed-image security evidence.** The existing API image archive was
validated and reused. Only missing MLflow/operator archives were exported.
For each image, the effective Azure image, ACR index, linux/amd64 child,
config hash, exported blobs/layers and scanner ImageID matched. All three
Trivy 0.75.0 vulnerability/licence and CycloneDX commands exited 0. Findings
were retained without suppression; command success does not mean a clean scan.

| Image | Critical / High / Medium / Low / Unknown | SBOM components | Licence inventory entries |
|---|---|---|---|
| Repaired frontend, preserved verified result | 0 / 0 / 0 / 0 / 0 | 71 | 103 |
| Current API | 1 / 63 / 112 / 105 / 1 | 240 | 772 |
| Current MLflow | 1 / 63 / 112 / 105 / 1 | 240 | 772 |
| Stopped CI/operator | 1 / 63 / 112 / 105 / 1 | 240 | 772 |

The latter three raw scanner SBOMs each contain 239 components and 771 licence
entries. Separate complete inventories add the already-approved native SQLite
3.54.0 binary, its actual SHA-256 and public-domain source/licence reference.
The raw reports remain unchanged. Complete CycloneDX 1.7 files explicitly bind
the ACR index/child/config and archive hashes, and pass JSON/component-reference
checks; a separate external JSON-schema validator was not installed or run.
Every reported finding has a retained disposition in ignored
`artifacts/azure-preflight/final-closure-20261019/`.

The critical zlib finding concerns MiniZip, which is absent from the inspected
images, including its affected function; the
[Debian tracker](https://security-tracker.debian.org/tracker/CVE-2023-45853)
explains the Bookworm source-package classification. Six findings with upstream
fixed versions (four HIGH, two MEDIUM) concern pip-vendored msgpack, setuptools
and urllib3. Runtime checks found top-level setuptools 84.0.0 and urllib3 2.8.0,
with msgpack present only in pip's vendor tree. Official PyPI metadata still
reported the installed pip 26.2.1 as latest. The reviewed serving entrypoints do
not expose user-directed package installation. These bundled copies remain in
the findings; unsupported vendor surgery was not performed. See
[pip's vendoring policy](https://pip.pypa.io/en/stable/development/vendoring-policy/).
Other distribution findings have no fixed Bookworm version reported by this
scan and remain residual risk, rather than being called non-applicable.
No unrelated dependency upgrade, image rebuild or redeployment was made.

**A CI rollback defect caught before push.** The script previously captured
`latestRevisionName`; after a failed deployment this can identify an unhealthy
candidate while an older revision still serves traffic. A real-shell test
with controlled Azure/PowerShell command boundaries reproduced two failures
and one passing case. `deployment/azure/ci-deploy.sh` now captures the single
revision receiving 100% traffic and refuses migration/update if that snapshot
is missing or ambiguous. The three regression cases then passed, and all
eight focused deployment unit tests passed. Read-only Azure queries selected
the current `api--0000003` and repaired `frontend--0000002`. This is local
orchestration verification; the completed manual live rollback was not repeated,
and hosted automated rollback remains unverified. The workflow now includes
`tests/deployment/test_ci_rollback.py`.

**Protection and credential review.** The 2,193-path audit has 1,744 immutable
matches, six explicitly authorized edits, four classified mutable credential
paths and 439 inaccessible generated runtime paths. None of those 439 paths
is tracked repository input. They remain **unverified**, with no permission or
content changes; they are not mismatches. The gate requires zero unexplained
accessible mismatches and passes. The separate frozen-source check covers 32
tracked inputs, the entrypoint and approved pin. Pre-commit review also removed
literal Azure account identifiers from the pending workflow/role templates:
the workflow reads three repository Actions variables, and role templates use
an explicit subscription placeholder. Live federation and roles were unchanged;
a fresh read verified one main-branch trust, no application password/certificate
credentials and nine exact role assignments matching the reviewed actions/scopes.
The three required GitHub repository Actions variables were initially absent.
Existing authenticated tooling created them and read them back to verify the
approved identity, without printing or recording values. Hosted OIDC login
remains unverified until the real workflow executes.

**Cost and budget correction.** Fresh Cost Management still reports month-to-date
pre-tax **INR 11.7066685215817**. Spending limit is On. Both group inventories
and a subscription-wide read contain the same 13 approved group resources;
all four Express apps remain stopped. The subscription warning budget now
actually exists: INR 100 monthly with enabled 50%, 80% and 100% notifications,
each with one configured contact. The earlier budget `RBACAccessDenied` is
preserved as historical failure, and is no longer an active budget blocker.
No numeric zero forecast or cash-versus-credit settlement is asserted.

**Evidence-recording lesson.** A preserved frontend scan hash was transcribed
with 65 characters in the earlier narrative. The unchanged 194,958-byte JSON
still has its original timestamp and the original tool-reported 64-character
SHA-256 `78e3cdf93a18350b1d6b6c4da2a9cd38bc56ebdbf74a5b445c8bfa4f9b72d344`.
The current record corrects the narrative; original scan bytes and failed
attempts remain preserved. Validate hash length as well as value before
treating a documentation comparison failure as an evidence-integrity incident.

**Git authority and hosted verification.** The user subsequently granted an
explicit one-time exception to the no-commit/no-push restrictions for this
reviewed Azure closure. The governing files themselves were not changed to
self-authorize. The reviewed implementation is prepared for the requested
`feat: deploy Aletheia to Azure with secure CI/CD` commit; hosted results will be
reported only after the actual pushed workflow executes.
No new ML experiment, retraining, held-out analysis or architecture change
occurred during these closure checks.

**Frontend image security repair (2026-10-19).** The deployed frontend index
`sha256:b6a73249020616b236ff3ff2590ad2cd1f11ed9edfce072ac01d10ac8dc023fa`
had one HIGH (`CVE-2026-77214`) and one MEDIUM (`CVE-2026-102633`)
Trivy finding in Alpine `libexpat 2.8.5-r0`. Both listed `2.9.0-r0` as fixed.
The original JSON, SBOM, scan retry failure log and image bindings were copied
to ignored evidence before changing the Dockerfile. The later retry had failed
on a Trivy cache lock; that failure does not count as a passing retry. The
Alpine v3.23 x86_64 package source supplied `2.9.0-r0`, confirmed by a
successful build and direct runtime inspection.

The first candidate replaced the Dockerfile's existing OS upgrade with only
the targeted package add. Its scan exposed 34 HIGH, 49 MEDIUM, 25 LOW and two
UNKNOWN findings in older base packages; that image was neither pushed nor
deployed. The final change in `deployment/Dockerfile.frontend` keeps the
existing upgrade and adds one exact `libexpat=2.9.0-r0` package step. The
distinct final frontend image index is
`sha256:12176c6a16302f1f4208c7878ead164701c08704ad3620fddc744ada63547416`,
linux/amd64 child
`sha256:fe6d6e57d8d9f72ae12031ddd85bcc5d96f2d6136658270068d4f0e34a2c1ed5`,
config `sha256:964d28ec5ffae6455a878c49fe6e232b7f51cdc86c6856e652ed9fa875977ac7`.
Archive, local layers, Trivy ImageID and ACR child config matched. Final
Trivy vulnerability/licence scan and CycloneDX SBOM each exited 0: zero
reported vulnerabilities, 103 licence entries and 71 SBOM components,
including `libexpat 2.9.0-r0`. This is a result for the pinned scanner and
database, not a claim that the software has no vulnerabilities or that every
licence has legal clearance. Trivy calls the OS `3.23.4` while direct runtime
`/etc/alpine-release` reads `3.23.6`; the package inventory and digest
binding were checked separately, and the patch-level discrepancy remains
unexplained. Exact hashes, sizes, attempts and logs are in ignored
`artifacts/azure-preflight/frontend-libexpat-20261019/RESULTS.md`.

Only the replacement frontend Container App was updated by final digest.
`frontend--0000002` became ready at 100% traffic, with previous
`frontend--0000001` active at 0% as rollback target. The public HTTPS path,
private API/MLflow isolation (404 direct), readiness, authentication, synthetic
prediction (`0.16546872246399696`), save/history/reopen, changed rerun,
immutable original, review, audit and browser reset passed. A previously
saved row from before this frontend revision and the newly saved row remained
retrievable through the new revision; creation/save audit events were visible.
The cloud browser test passed 1/1. Frontend lint, typecheck, 81/81 unit tests,
production build and the OpenAPI/10-public-response snapshot check passed.
All 51 runtime static assets and the runtime configuration fields matched
the preserved baseline; credential-pattern checks found zero matches in the
candidate assets/metadata and the 73 changed working-tree paths.
At that earlier frontend-repair checkpoint, `format:check` failed on the existing
untracked `frontend/browser/cloud.spec.ts`, which this image-only repair left
untouched. The first authenticated post-deploy request returned 401 because
the 14-minute local synthetic test tokens had expired; refreshing only those
ignored tokens with the existing key restored the passing workflow. This
distinguishes credential freshness from an application regression. No model,
backend, MLflow, PostgreSQL, architecture, or inference deadline changed.
The Dockerfile's pre-existing `apk upgrade` still consults a mutable package
repository, so the exact deployed digest, not a future rebuild of the tag,
identifies what was tested. The workload deployment helper's frontend digest
was updated to the verified image so a later invocation cannot restore the
old vulnerable frontend. Hosted CI is still unverified pending user push.

**Preserved recovery evidence.** The fresh local backup at
`artifacts/azure-preflight/final-local-backup-20261019T051444Z` contains the
application and MLflow database dumps plus registry, release and state
archives. Its manifest records full SHA-256 values and sizes for all five
files. The earlier isolated restore reached migration `0004_case_input`, the
same active frozen release, one registered MLflow model, readiness 200 and
an authenticated prediction 201 with probability `0.16546872246399696`.
The original expired identity certificate stayed unchanged; a renewed
certificate was confined to that temporary project. Only the successful
temporary restore project was removed. The 13 October backup, fresh files
and original source volumes remain preserved. This frontend repair reused
that completed verification rather than repeating it.

**Milestone and why it followed the Express audit.** The preserved Express
environment could not establish genuine private ingress: it stored
`external:false` yet retained public-style service hostnames. The supervisor
froze a replacement topology using a Workload Profiles environment with only
the serverless Consumption profile. The Express environment and its four apps
remain stopped, with the API and MLflow deny rules retained. The replacement
reuses the existing Southeast Asia PostgreSQL Flexible Server, Standard ACR,
pull identity and frozen release; it adds one environment and four Container
Apps (`frontend`, `api`, `mlflow`, and a stopped, no-ingress release operator).
No Dedicated profile, custom VNet, NAT, private DNS, load balancer or paid
monitoring workspace was created. See `docs/ARCHITECTURE.md` for the actual
request path and `artifacts/azure-preflight/PREFLIGHT.md` for ARM and quota
evidence.

**Implemented flow and reason.** Browser HTTPS reaches the public frontend;
its NGINX proxy uses `http://api` within the environment. The API uses
`http://mlflow`, the approved activated frozen model and the least-privileged
`aletheia_app` database role over verified PostgreSQL TLS. API and MLflow have
genuine `.internal.` FQDNs. External requests to their public-style hostnames
return 404, while frontend-proxied API liveness and readiness return 200.
The API runs at 1 vCPU/2 GiB, and all three serving apps are configured with
minimum zero and maximum one replica. Multiple revision mode retains a
working revision for rollback. This was implemented after private ingress
was verified because `external:false` alone failed as a security proof in
Express. A shared application header or deny-all ingress rule would not give
the frontend a reliable private path.

**Verified result.** An invented case submitted through the real public Azure
URL returned probability `0.16546872246399696`, model SHA-256
`8c3a99dd8dfe20d2a3a0a721637b4be500ee1b32843f7cefc3af265f07262f7a`,
release SHA-256 `65f2302cc9c4795142567296cc6b16143fad5abfe4df7b04152975748c2ec271`,
and evidence SHA-256 `2d073fa0d0bbbd4debfdf445cd80ec478fef0f7098c7ef356dbb3edd28894ea8`.
Authenticated save, history, reopening, changed rerun, immutable original,
review, audit and browser reset passed. An unauthenticated history request
returned 401; an engineer request to an administrator route returned 403.
PostgreSQL remained Ready, PostgreSQL 18/B1ms/32 GiB, TLS required, and
Alembic reported `0004_case_input (head)` through a controlled no-ingress
migration revision. Saved predictions and audit rows remained visible after
an API restart and a measured scale-to-zero cold start. The cold start gave
two transient 504 responses before readiness returned 200; callers need a
bounded retry. The fixed inference deadline was not increased. Evidence is
in `cloud-workflow.json`, `cloud-browser.json`, `cloud-persistence-restart.json`
and `cloud-persistence-scale-zero.json` under ignored `artifacts/azure-preflight/`.
The real browser test passed once; focused backend checks passed 35 with five
PostgreSQL-dependent skips, and frontend unit checks passed 81 in seven files.
Frozen Python/model inputs were not changed or retrained.
The original protected-evidence verifier flagged the task-required
`docs/ARCHITECTURE.md` and `README.md` updates. A separate exact-hash and
diff-count classification left zero unexplained changes without modifying
the original manifests. An earlier audit reported reading and verifying the
439 generated runtime paths that the original Windows check could not access.
The final frontend repair audit could not reproduce that read access: both
host and read-only Docker-mount checks returned permission errors for all 439.
The classified host audit still has zero unexplained changes among accessible
paths; fresh verification of those generated paths remains incomplete.
Earlier successful and failed attempts are preserved, and no ACL or evidence
bytes were changed.

**CI/CD status and decision.** `.github/workflows/azure-showcase.yml` now runs
focused tests and frozen-input checks before Azure deployment. A GitHub
federated credential trusts only `Ameya5006/Aletheia` on `refs/heads/main`;
its service principal has ACR-scoped push/read, identity-operator scope on the
existing pull identity, deployment validate/what-if permissions in the new
resource group, a separate subscription-policy read-only permission, and app
update permissions on the four named existing apps.
No client secret or long-lived Azure credential is stored in GitHub. The
workflow builds immutable image digests, validates and previews the existing
topology, runs migrations in the stopped-by-default no-ingress operator,
updates only API/frontend by digest, runs a synthetic authenticated smoke
prediction with an Azure-managed signing-key secret reference, and restores
the previous traffic revisions if verification fails. The migration and smoke
commands both passed manually in Azure using the CI backend overlay digest
`sha256:3f6b5f2fc264d26c57da3d9b87174eae37438c7bfdbc2f0ef22164ddb65ec8dd`;
the operator was stopped after each run. YAML, Bash, PowerShell, frozen-input
and static Python checks passed locally. The GitHub workflow itself has **not
run** because the governing task forbids this agent from committing or pushing;
federated login and automated rollback are therefore implemented but not
end-to-end verified by GitHub Actions. The workflow never builds or deploys
the regression image.
The repeat synthetic smoke run also scanned its live console-log window for
private-key, JWT and PostgreSQL-URL patterns and found none; the CLI did not
retrieve the stopped replica's full historical console log afterward.

**Important problems and lessons.** A cold MLflow import and first approval
request timed out before their dependencies warmed; a retry after readiness
succeeded. An early NGINX dynamic DNS resolver returned 502; static
same-environment `api` resolution at startup fixed the proxy. The secure
operator update first failed because ARM `listSecrets` required a JSON content
type, then an accepted PATCH did not change the effective configuration. A
bounded Bicep validation/what-if/deployment succeeded. PowerShell's
`Get-Content -Raw` attached file metadata to the signing-key string, causing
deep JSON serialization to stall; copying to a plain string removed the
metadata. The signing key stayed in ignored local evidence and Azure secure
parameters/secret references, and ARM deployment history reports no secure
value. The failed attempts were retained as evidence. Interview explanation:
control-plane success, application health, network isolation and persistence
are separate checks, and a successful write must be followed by effective
ARM readback and external probes.

**Cost and limits.** The Azure for Students spending limit is On. The
Consumption-core quota is 100; a read during warm replicas showed 1.75 in
use. Standard ACR reported 697,631,382 bytes against its 100 GiB limit.
At the 2026-10-19 Cost Management read, month-to-date pre-tax cost was
**INR 11.7066685215817**, mostly historical Express Container Apps usage;
the existing ACR and PostgreSQL rows each reported INR 0 at that read.
This is reported cost, not a future forecast or a statement about cash versus
student-credit settlement. Billing can lag. PostgreSQL's sole Azure-services
firewall rule remains a bounded showcase exception; it accepts other Azure
origins at the firewall layer, while TLS and least-privilege authentication
still apply. No real patient data is used. Full GitHub CI execution, automated
rollback behavior and a numeric future cost forecast remain unverified. A
manual live rollback to MLflow `mlflow--0000001` passed readiness, followed by
restoration of `mlflow--0000002`. An attempted API rollback to
`api--0000002` returned liveness 200 but readiness 503; current
`api--0000003` was restored and readiness returned 200. That failed attempt
must remain distinguishable from the successful MLflow rollback.
The initial task-authorized subscription INR 100 monthly warning budget was attempted
with 50%, 80% and 100% actual-cost alerts and the signed-in user's email held
only in process memory. Azure returned `RBACAccessDenied` for the budget PUT;
`az consumption budget list` then returned `[]`. That attempt lacked
subscription budget-write authority, so it created no budget or notification.
This was an external authorization blocker, not a spending-cap failure or a
reason to broaden application permissions. The final closure read now verifies
that the budget exists with the three enabled notifications; the earlier
denial is historical evidence. Microsoft's
[budget guidance](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/quick-create-budget-bicep)
states that an Owner or Cost Management Contributor can create budgets, and
that a budget warns but does not stop resources. The student spending limit
remains On independently.
Microsoft's [Azure for Students offer](https://azure.microsoft.com/en-us/free/students/)
lists one Standard ACR/100 GiB, PG B1ms/32 GiB/750 hours for 12 months, and
Container Apps monthly allowances. The [Container Apps billing guide](https://learn.microsoft.com/en-us/azure/container-apps/billing)
states 180,000 vCPU-seconds, 360,000 GiB-seconds and two million requests per
subscription per month are free. These published grants do not erase the
nonzero Cost Management result; its precise cause and credit settlement are
not established by this project.

## Azure private-ingress repair audit (2026-10-18)

**Objective and outcome:** The supervisor authorized one bounded attempt to
repair private Container Apps ingress in the existing environment. The attempt
did not reach the required security gate. No app was started, no image or data
was replaced, and no cloud prediction is claimed. The earlier direct HTTP 200
from the API's own public-style hostname remains the relevant exposure
observation; no repeat external request to a running app was made in this
repair. The four apps remain stopped, with deny-all ingress restrictions on
API and MLflow.

**What was tested:** First, the effective 2025-07-01 ARM response and Azure CLI
both showed `external: false` and a hostname without `.internal.` for each
app. Both were in Single revision mode, with `traffic: null` and no active
revision reported while stopped. Disabling ingress and re-enabling it with
`--type internal` on each existing app left the same public-style FQDN.
Disabling also removed the temporary deny rule, so the rule was immediately
restored while each app was stopped. A direct 2025-07-01 ARM JSON Merge Patch
for `external: false` was accepted (HTTP 202) on both apps, with the deny rule
included. The subsequent ARM GET reported provisioning Succeeded and still
returned `api.greenpond-767543dc.southeastasia.azurecontainerapps.io` and
`mlflow.greenpond-767543dc.southeastasia.azurecontainerapps.io`. Neither
contained `.internal.`. No revisions or persistent resources were deleted.

**Why the configuration cannot advance:** Microsoft's general Container Apps
guide describes `.internal.` FQDNs and same-environment `http://<APP_NAME>`
routing, but its Express-specific guide says Express app-to-app traffic uses
public app URLs and built-in short-name discovery is unsupported. This
environment also rejected an environment route configuration as an Express
unsupported resource in the earlier investigation. The control-plane
observation and Express guide therefore conflict with the proposed standard
Container Apps repair path. `external: false` alone is insufficient evidence
of isolation here. The precise platform cause of the mismatch is unproven;
it may require Azure support or a different, separately approved environment
topology. In particular, an accepted ARM write is not proof that the intended
route exists or is private.

**Decision and limitations:** The frontend proxy was not switched to
`http://api`, and the backend MLflow endpoint was not switched to
`http://mlflow`, because the current Express environment does not advertise
short-name discovery and the prerequisite internal FQDN was not obtained.
Deploying those unverified routes would knowingly break the application or
weaken its isolation. The deny rules were not removed, and MLflow, API and
frontend were not started. Authentication, prediction, save/history, audit,
artifact retrieval, cold-start and CI/CD checks remain pending. The same
eight Azure resources, PostgreSQL data, image digests and prior evidence are
preserved. A later decision must either identify an Azure-supported private
route in this exact no-paid-network environment or explicitly authorize a
different architecture; this repair does not authorize one.

**Engineering lesson and viva answer:** What does `external: false` prove? It
proves the desired control-plane field was stored, not that every external
route was removed. A secure deployment verifies the generated hostname and
tests reachability from outside and inside the environment. Why was
`http://api` not deployed? Service discovery is a capability of the specific
Container Apps environment mode; the general service guide and the Express
feature matrix differ. Tests must follow the deployed mode rather than assume
one document applies to every mode. The exact evidence for that historical
checkpoint is in `docs/history/SUPERVISOR_HANDOFF_20261018_EXPRESS_REPAIR.md`.

## Azure deployment continuation: secured stop at Express ingress (2026-10-18)

**Current status:** The Azure end-to-end milestone is incomplete. The external
supervisor's bounded showcase decision allowed PostgreSQL's Azure-services
firewall exception when exact Container Apps outbound IPs remained unavailable.
That decision supersedes the exact-IP stop described in the historical section
below. It did not authorize a public backend or MLflow service. The current
task explicitly stops if either service requires public external ingress.

**What was implemented and why now:** On the existing Southeast Asia resource
group, a controlled temporary Container App revision performed the one-time
PostgreSQL bootstrap. Azure Express rejected Secret volumes, so the bootstrap
was changed to use Azure secret-backed environment references; credentials were
kept in Azure secret handling and transient process memory. The first metadata
restore then failed because the MLflow role lacked `CREATE` on its `public`
schema. A targeted grant and repeatable restore resolved that. The application
owner received the same schema permission for Alembic. A separate migration
revision ran `alembic upgrade head`; a subsequent read-only `alembic current`
reported `0004_case_input (head)`. PostgreSQL was Ready at PG18/B1ms with
mandatory TLS, seven-day backup and HA disabled. Its only firewall rule was
the approved Azure-services exception (`0.0.0.0` to `0.0.0.0`), not a broad
public-internet range. Application-user permission and actual prediction
persistence were not yet verified.

The existing frontend was updated to proxy `/api/v1/` over certificate-verified
HTTPS to an API app sized at the previously accepted 1 vCPU/2 GiB. Express
mounts a fresh `/run`, hiding image-created directories; a small entrypoint
creates a private directory before dropping to UID 10001 and writing only the
needed Azure-managed secret there. Both backend and MLflow images were rebuilt
and pinned by digest. Nginx initially returned 502 because its default upstream
certificate verification depth was too shallow for Azure's served chain; setting
depth three fixed it. The public frontend route then returned HTTP 200 for the
backend liveness endpoint with TLS verification enabled. No real prediction,
save, history, rerun, reset, audit persistence, cold start, or CI/CD workflow
was completed, so this is not an operational cloud deployment.

**Security blocker:** Azure reported `external: false` for the API and MLflow
ingress, but a direct request from outside Azure to the API's own hostname
returned HTTP 200. Reapplying `--type internal` did not remove that route. A
deny-all ingress rule returned 403 to both direct callers and the frontend.
The expected `.internal.` hostname returned 404 from the frontend replica;
allowing either the environment's ingress IP or the measured frontend egress
IP still blocked the frontend route. These probes do not establish a private,
working path, and the measured egress IP is not a stable Azure-reported list.
The API and MLflow now each have `Deny 0.0.0.0/0` ingress restrictions, and
frontend, API, MLflow and temporary bootstrap apps are stopped. Their apps,
secrets, images, PostgreSQL data and logs remain for review. The temporary app
was retained because its Azure secret references and migration evidence are
still needed for a safe continuation; it must not be deleted blindly.

**Decision and trade-off:** The four-app topology is preserved rather than
silently co-hosting services or buying private networking. Express does not
support sidecars, and a one-container multi-process replacement would change
the approved private-service and independent-health contracts without sizing
or failure-behavior evidence. A shared header would guard application requests
but would not make backend ingress internal. Supervisor review is required for
a supported free private route or an explicitly revised architecture. No
model, preprocessing, XAI, or training input changed, so the expensive offline
regression and prior sizing test were not repeated.

**Interview/viva explanation:** Why was an Azure control-plane `external:false`
field insufficient? A security property needs an external probe: the direct API
URL still returned 200. Why retain a failed temporary app? It holds controlled
Azure secret references and migration evidence; cleanup before a secure
handoff could remove the only safe recovery path. Why is schema `CREATE`
different from database ownership? A role can own its database yet lack rights
on a separately owned `public` schema, causing `pg_restore` or Alembic to fail.
The relevant implementation is under `deployment/azure/`; review evidence
for that historical checkpoint is in
`docs/history/SUPERVISOR_HANDOFF_20261018_EXPRESS_REPAIR.md`. The account's free-service
allowances are eligibility evidence, not a guaranteed zero bill; current
month-to-date actual cost and future forecast were not re-established here.

## Azure continuation: incident resolution and partial cloud gate (2026-10-17)

**Current status:** the local sizing and protected-evidence incident described
below are historical. The supervisor authorized a forensic classification.
The four changed files were generated, expiring local test tokens, not model
or immutable project evidence. The original hash manifests were preserved;
the token bytes were retained in place but were not duplicated. Windows-native
rehashing found 439 inaccessible ignored pytest/runtime paths, which remain
**unverified**, and no unexplained mismatches. Four additional changed hashes
belong to authorized tracked task/source edits. The classified check is
reproducible with `artifacts/azure-preflight/verify-protected-classified.py`;
the detailed metadata is in the ignored timestamped incident directory.
The accepted 1 vCPU/2 GiB backend and browser result was not rerun because its
bound inputs did not change.

**Why the next gate matters:** the approved public PostgreSQL topology depends
on a complete, exact list of Azure-reported Container Apps outbound IPs. Each
address would become one narrow firewall rule, with verified TLS and
idempotent reconciliation when Azure changes the list. The alternative paid
VNet/NAT/private-DNS design is prohibited by the current zero-cost task, as
are broad `0.0.0.0` or “Allow Azure services” rules. An observed source IP
from one request cannot prove all possible egress addresses.

**Cloud work and result:** live subscription policy rejected UAE North even
though its service listings and environment quota appeared compatible.
Southeast Asia was the nearest allowed one-region candidate. A default
Consumption environment, Standard ACR, registry-scoped AcrPull managed
identity and 0.25 vCPU/0.5 GiB frontend app were deployed there. The app is
pinned to an immutable image digest and returned 200 from its Azure-managed
HTTPS health route. This establishes only static frontend reachability.
No PostgreSQL server, backend, MLflow app, schema migration, prediction, cloud
persistence or production CI/CD has been deployed or verified. The account
remains Azure for Students/Enabled with spending limit On; the active
account-specific Standard ACR and PostgreSQL B1ms/32 GiB free indicators were
recorded, while Cost Management's numeric forecast remains unavailable.

**Current hard problem:** the Running external Container App's
`outboundIpAddresses` property is present but `null` through CLI and multiple
ARM API versions, including after outbound HTTPS from a live replica. The
environment has no usable reported egress list either. Without that input,
the mandated exact-IP PostgreSQL firewall cannot be built or reconciled.
The delayed read over ten minutes later also returned null, so the explicit
stop condition in `docs/CURRENT_TASK.md` applies. The stopped database mutation and all Azure resource names,
image digest, API observations and safe alternatives are recorded in the
ignored `artifacts/azure-preflight/EGRESS_GATE_20261017.md`. The existing
frontend endpoint must not be presented as a deployed decision-auditor URL.

**Engineering lesson and viva answer:** provider location support, account
quota, subscription policy and runtime control-plane data are separate gates.
An apparently deployable region can fail policy validation, and a working
HTTPS Container App can still lack the egress metadata required to secure its
database. For a cost-bound showcase, the correct response is to stop before
creating a database that needs an unapproved firewall exception. This is a
deployment/security limitation, not a change to the frozen ML system.

## Azure continuation: local sizing and evidence-integrity stop (2026-10-17)

**Current status:** Azure deployment is incomplete. The supervisor's new
directive authorized continuing past recoverable preflight issues, so the
earlier regional quota stop below is historical. Registering the free
`Microsoft.App` resource provider changed sampled `ManagedEnvironmentCount`
quotas from 0/0 to 0/1. Central India remains excluded by the directive;
South India reports subscription-restricted PostgreSQL provisioning; Jio India
West lacks an ACR location listing. UAE North is the nearest remaining
single-region candidate with 0/1 App environment quota, a B1ms SKU listing,
and App/ACR location support. These are candidate checks, not deployed
capacity. The Azure inventory remained empty at the final read-only query.
Cost Management's forecast remains unavailable, not zero.

**Why this work followed preflight:** A provider's unregistered state can make
its quota response misleading for deployment decisions. Registration is a
free control-plane action and was necessary to distinguish a genuine regional
limit from an uninitialized provider. South India's PostgreSQL restriction
then required evaluating the next single-region alternatives before changing
application architecture. The active Student free meters cover one Standard
registry, B1ms compute/storage/backup and published Container Apps usage;
exact regional pricing and environment-level core quota remain unverified.

**Local sizing:** An isolated Docker stack reused the byte-identical approved
release while generating new test-only identity material. The old development
identity certificate had expired, so the existing protected stack could not
serve as a clean current test. The first isolated browser attempt used an old
frontend image and failed its empty-Overview assertion. With the repaired
frontend at 0.25 vCPU/0.5 GiB and the backend at the preferred 0.75
vCPU/1.5 GiB, the first authenticated prediction returned HTTP 504
`inference_deadline_exceeded`; the fixed deadline was not raised. The allowed
1 vCPU/2 GiB backend fallback then passed a real browser journey: 13-field
manual input, prediction, Save, history, reopen, changed rerun, immutable
original, Reset preserving history, and 18 accessibility state/viewport
checks with no violations. The passing browser command took 27.547 seconds,
reported one Playwright test passed, and used distinct prediction IDs. The
backend/frontend reported no OOM kill or automatic restart. Sampled peaks
were 178.9 MiB/100.08% CPU and 5.6 MiB/8.44% CPU respectively; sampling
does not prove absolute peaks. At the fallback plus provisional MLflow
0.5 vCPU/1 GiB, 1.75 vCPU/3.5 GiB permits 28.57 shared active hours under
either monthly free compute meter, or 28 hours after a two-hour job reserve.
This is a planning bound, not measured cloud usage.

**Immutable artifact concept and result:** The local MLflow metadata database
contained one run and one registered model version; its secrets table had zero
rows. A reviewed artifact directory was copied into a read-only MLflow image.
An operator retrieved and verified the same frozen package through that image;
`docker diff` showed only the mounted secret path. A restart check initially
failed because MLflow had not yet opened port 5000 after 20 seconds; waiting
for its health endpoint and rerunning the same verification passed. This
demonstrates local feasibility of read-only artifact serving, not Azure
metadata restore, scale-to-zero, or a cloud-ready backend. The frontend was
also adapted to accept a provisioned token in a release build by validating
it through the existing protected history endpoint. The API still enforces
signed claims and database entitlements; unverified browser-decoded roles are
only display hints. A focused frontend test, typecheck, lint and production
build passed. Full cloud authentication, CI/CD and deployment remain undone.

**Important problem and hard stop:** The existing token-refresh helper was
invoked against the protected prior interactive evidence tree. It replaced
four short-lived `administrator`, `engineer`, `operator` and `reviewer` token
files. Their SHA-256 values now differ from the preserved manifest. No token
value was printed, but the original bytes were not saved, so the protected
record cannot be claimed unchanged. A separate 439 paths under the old Stage 3
`offline-host` snapshot were inaccessible under Windows ACLs even on a
read-only retry outside the sandbox; no result is claimed for them. The
manifest comparison found no missing paths and eight changed paths in all:
the four tokens and four intentionally edited task/report/handoff/Dockerfile
paths. This was a governance failure in local test setup: an apparently safe
refresh helper still wrote into a protected evidence tree. Future sizing
fixtures must isolate secrets as well as databases and images before any
helper runs. The current directive makes any protected-file hash mismatch a
hard stop, so no Azure application resource was provisioned after discovery.
The mismatch does **not** prove that a secure zero-cost Azure design is
impossible; the supervisor must decide how to preserve or repair this evidence
before deployment resumes. See the current ignored preflight record for
commands and preserved failed attempts. No clinical or cloud success is
claimed.

**Viva explanation:** Why can registration change a quota result? An
unregistered provider may report no available allocation even when a region
is listed as supported; account-specific quota must be rechecked after
registration. Why did 0.75 CPU fail despite modest sampled memory? The first
prediction exceeded the fixed end-to-end inference deadline; a low average
memory sample says nothing about enough CPU within that deadline. Why stop
after a known token refresh? Evidence integrity is a separate requirement:
knowing the cause does not make the original protected bytes reappear.

## Azure deployment preflight: regional quota stop (2026-10-17; historical)

The current task authorizes an Azure for Students showcase only inside active
free allowances. After the supervisor clarified the pre-deployment cost
forecast rule, all five portal images were reinspected. The replacement
PostgreSQL image is sanitized and still shows Central India, Burstable
`Standard_B1ms`, 1 vCore/2 GiB, 32 GiB storage, and green 750-hour/32-GiB
free indicators. The account panel shows an unused Standard registry unit and
PostgreSQL compute, data and backup meters. The Student offer remains Enabled
with spending limit On, and the live Azure inventory is empty. A fresh
month-to-date Cost Management query returned no rows. The portal's `--`
forecast is **unavailable before deployment because no usable cost history
exists**, not a numeric zero forecast; Azure says forecasts can be absent with
insufficient history and free-service usage may lag one to two days. The
credit image uses `$`, so its 9,599 balance is not relabelled INR. None of
these observations is a future bill or permission to use promotional credit.

The decisive new finding is a read-only Central India Container Apps regional
usage query: `ManagedEnvironmentCount` has current use **0** and limit **0**.
This is a subscription/region quota, so even the minimum planned environment
cannot be created under the current quota. `Microsoft.App`,
`Microsoft.ContainerRegistry` and `Microsoft.OperationalInsights` also return
`NotRegistered`; the PostgreSQL provider is Registered. Provider metadata lists
Central India for the proposed resource types, and PostgreSQL's live SKU
listing includes B1ms, but those facts do not grant registration or capacity.
The task's provider/quota stop applies before any environment creation. The
environment-level Consumption-core quota can be checked only after an
environment exists, so that check was not reached. No registration, quota
increase, cloud resource, image or application change was made.

**Sizing and cost reasoning:** the source plan proposes frontend 0.25
vCPU/0.5 GiB and backend 1 vCPU/1.5 GiB, each min 0/max 1. Microsoft's
[Consumption sizing table](https://learn.microsoft.com/en-us/azure/container-apps/containers#vcpu-and-memory-allocation-requirements)
does **not** permit the backend's 1/1.5 pair. The smallest published memory
allocation at 1 vCPU is 2 GiB; this is a candidate, not an approved or tested
change. The original invalid plan would mathematically allow 40 CPU-bound and
50 memory-bound common active hours, but cannot be deployed as written. With
the valid 1/2 candidate, frontend + backend would use 1.25 vCPU/2.5 GiB and
exhaust either published monthly grant after **40 simultaneous active hours**
if nothing else ran. Including provisional MLflow (0.5 vCPU/1 GiB) gives
28.57 hours by either grant; reserving two hours for the proposed migration
job leaves **28.00 hours**. These are allocation calculations, not measured
cloud usage or a zero-cost guarantee. The complete conditional matrix,
including registry, PostgreSQL, logs, monitoring, data transfer, omitted paid
network resources, DNS and artifact storage, is in the current ignored
`artifacts/azure-preflight/PREFLIGHT.md`. No `deployment/azure/` implementation
exists. The planned public PostgreSQL exact-IP/TLS design remains approved in
principle; the superseded private-network stop remains historical below.
If all three candidate replicas stayed active for a 31-day month, the proposed
two-hour job reserve would bring usage to 4,690,800 vCPU-seconds and
9,381,600 GiB-seconds, far beyond the free grants. Minimum zero and maximum
one do not cap monthly consumption; bounded operation and monitoring remain
necessary before a zero-credit deployment claim.

**Problem, recovery and lesson:** the quota check returned a zero environment
limit despite Central India appearing in provider location metadata. Location
support and free-service advertising are not a subscription quota allocation.
Creating first and asking for capacity later would violate the preflight gate,
so the run stopped. Two initial local JSON projections falsely showed no B1ms,
and an empty-array PowerShell projection briefly counted one resource; field
inspection and explicit empty-array handling corrected these, with final
results of one B1ms listing and zero resources. The 2,190 protected manifest
paths still match their stored SHA-256 values. No meaningful ML or runtime bug
occurred. For a viva: **Why did a free-eligible architecture not deploy?**
Because a free allowance concerns billing, while a regional quota controls
whether a resource may exist; here that quota is zero. A valid free meter also
does not make an invalid CPU/memory configuration deployable. The supervisor
must review this stop, and no quota increase was requested.

## Historical Azure deployment task revision (2026-10-17; before resumed quota check)

### First portal preflight review (historical)

Five fresh Azure portal captures were checked against the approved deployment
gate. They confirm an active Azure for Students offer with an Upgrade action,
an unused displayed credit balance expiring 2027-06-26, an unused Standard
Container Registry unit, and account-level PostgreSQL free meters. The Central
India PostgreSQL form specifically shows Burstable `Standard_B1ms`, 1 vCore,
2 GiB RAM, 32 GiB storage, and green indicators for up to 750 compute hours
and 32 GiB storage. This resolves the earlier missing PostgreSQL portal
indicator and registry-unit evidence; it does not mean a server was created.

The Cost Management image says no cost was reported for October, but renders
both actual cost and forecast as `--` and budget as `NONE`. The credit capture
uses a `$` symbol, whereas the task's historical amount is labelled INR; the
currency cannot be silently inferred. No image establishes the full
Container Apps/monitoring allowances, exact resource estimates or regional
quotas. The PostgreSQL screenshot also contains an account identifier in its
header, so it must be replaced with a correctly redacted copy before it is
shared as sanitized evidence. No identifier is reproduced in this report.

**Current result and why this order matters:** the approved public PostgreSQL
firewall design is still the intended architecture. Implementation and
provisioning remain stopped under the task's preflight rules because the full
free-allowance/estimate and quota evidence is incomplete. Starting resources
first would make it impossible to guarantee the zero-credit boundary before
costs or unsafe substitutions arise. Read-only checks found the selected
subscription enabled and the Azure resource inventory empty; 2,190 protected
manifest entries were unchanged, while the three expected revised task/report/
handoff documents differ. No new ML experiment, deployment, runtime defect or
clinical performance result occurred. The engineering lesson is that portal
free indicators must be matched to the complete resource inventory, and a
blank cost forecast is unknown rather than zero. See the per-image map in
`artifacts/azure-preflight/PREFLIGHT.md` and the current supervisor handoff.

**Interview/viva follow-up:** Why did the new screenshots not unblock Azure?
They establish key account and PostgreSQL entitlements, but do not establish
every proposed resource's free allowance, region/quota and estimate; one
capture also needs identifier redaction. How do you distinguish cost evidence?
An unused free meter is an allowance, a list-price estimate is not a bill,
and a cost view with `--` has no numeric forecast. No meaningful software bug
occurred in this evidence-review step.

The current approved task's Section 0 supersedes the DNS-only credit exception
and the earlier stopped private-network decision recorded below. The approved
design for this bounded, non-sensitive student showcase is now one public
PostgreSQL Flexible Server endpoint with TLS certificate/hostname verification,
one exact firewall rule per currently reported Container Apps outbound IPv4
address, and an idempotent operator reconciliation command. Azure may change
those addresses, so connectivity can pause until reconciliation; this is an
accepted availability limitation, not an automatic self-healing claim. Broad
Azure-service or internet firewall access remains forbidden. Private DNS,
customer Container Apps VNet integration and its paid managed networking are
not authorized.

The revised task also proposes packaging only the approved frozen MLflow
artifacts into an immutable registry image and storing MLflow metadata in the
single managed PostgreSQL server. This removes the need for a separately
charged Azure Files/Blob resource but requires explicit package hash, registry
digest and cold-start/revision retrieval proof. The local Docker-volume
implementation has not yet been migrated; no cloud resources, image, URL,
runtime verification or new ML experiment exist. The earlier stopped records
remain valid accounts of what was known then, not current deployment decisions.

**Decision and trade-off:** the supervisor selected a lower-cost public
endpoint with exact-IP defense, verified TLS and credentials over a private VNet
that brings billed managed IP/load-balancer resources. This saves the planned
credit but accepts a bounded exposure surface and manual pre-demonstration
reconciliation after Azure egress-IP changes. Reconsider this design for any
sensitive or production use, any failure to obtain a finite exact IP list, or
any need for automatic recovery that cannot be provided inside the free grants.

**Viva question:** Why can a public database endpoint be allowed for this
showcase? Because the firewall is restricted to the current exact Container
Apps egress addresses, clients must verify the TLS server identity, credentials
are least-privilege, and only non-identifiable showcase cases are allowed.
This is a task-specific constraint, not a general clinical deployment pattern.

**Preflight evidence and limitation:** A corrected read-only Azure Cost
Management query returned no reported month-to-date cost rows. This does not
establish a zero future forecast or rule out delayed metering. Published
free-service limits support a bounded operating estimate, but current portal
credit/expiry, applicable PostgreSQL free indicators, Standard registry
benefit and resource estimates still need rechecking before provisioning.
The approved two-phase approach must obtain a finite exact outbound IPv4 list
from the actual Container Apps and jobs before creating PostgreSQL firewall
rules. The reconciliation design limits mutations to a deployment-owned rule
prefix, uses one address per rule, and preserves unrelated rules. Neither
cloud connectivity nor this algorithm has been implemented or tested yet.

## Azure deployment preflight continuation: DNS-only exception (2026-10-16)

The user permitted promotional credit for exactly one PostgreSQL Private DNS
zone, with total planned credit use capped at INR 100/month and zero cash
payment. This reopened the cost question, but the deployment still stopped
before resource creation. Azure Resource Manager now confirms the selected
`Azure for Students` subscription is enabled, its offer is
`AzureForStudents_2018-01-01`, and its spending limit is **On**. A fresh
sanitized resource inventory is empty. Central India lists the required
`Standard_B1ms` PostgreSQL capability at 1 vCore and 2 GiB RAM; a capability
listing alone does not prove this subscription's free entitlement or quota.

The selected private PostgreSQL route needs a customer VNet for Container Apps
to reach it. [Microsoft's Container Apps VNet guidance](https://learn.microsoft.com/en-us/azure/container-apps/custom-virtual-networks)
says that this deployment creates separately billed managed public IP and load
balancer resources, including with Consumption apps. The authorized DNS zone
does not cover those resources. The alternative public PostgreSQL endpoint
still lacks a demonstrated durable, exact Container Apps egress-IP firewall;
opening access to all Azure services would violate the security boundary.
There is also no subscription-specific proof that a persistent MLflow artifact
store is free: the [student offer](https://azure.microsoft.com/en-us/free/students/)
labels its 5 GB Azure Files entry under Cloud Shell, whose [pricing guidance](https://learn.microsoft.com/en-us/azure/cloud-shell/pricing)
says underlying storage incurs regular charges. No storage substitute was
silently adopted.

**Decision and order:** keep the gate closed before writing deployment code or
provisioning. The network topology must include every Azure-managed supporting
resource in the cost inventory, even when the VNet itself is free. The option
of allowing only one DNS charge was considered and accepted by the user, but
the actual private-network topology exceeds that permission. Reconsider only
with a verified secure topology and account-specific entitlement/cost proof
for all other resources, or a newly approved task. The old stopped-preflight
record below is preserved as the earlier state, including its then-unknown
spending-limit value; that value is now verified above.

**Verified result:** subscription policy read, B1ms capability lookup and
empty resource inventory succeeded. No new ML experiment, model or application
change, held-out access, cloud image, public URL, or Azure resource exists.
The final SHA-256 recheck found zero mismatches among 2,182 protected
artifact/evidence files; the two changed documentation files were correctly
excluded from that protected-file count.
No deployment cost, security, persistence, cold-start, browser, backup or
rollback result can be claimed. No meaningful runtime bug occurred. The
engineering lesson is that a service's free compute allowance does not make
its network dependencies free. The ignored continuation record is
`artifacts/azure-preflight/PREFLIGHT.md`.

**Viva/interview question:** Why did a DNS-only cost exception not unblock the
deployment? Because private PostgreSQL requires Container Apps VNet integration,
which brings additional billed managed IP/load-balancer resources; the allowed
zone pays only for name resolution, not that network path.

## Azure free-tier deployment preflight stopped (2026-10-16)

**Status:** the authorized cloud milestone did not pass its mandatory cost and
security preflight. No Azure resource was created, no cloud image was built or
pushed, and no Azure URL or cloud verification result exists. The local system
and frozen model/release/evidence identities remain unchanged. This is a blocked
milestone, not a deployment result; the external supervisor must review before
any further implementation or revised scope.

The local architecture is still React/NGINX → FastAPI → PostgreSQL/MLflow with
provisioned JWT/RBAC, explicit Alembic migration and immutable release
provisioning. The proposed cloud equivalent needs persistent artifacts and a
database network boundary before it can expose an HTTPS frontend. This ordering
matters: deploying a free app first would create pressure to add a billed DNS,
storage or network resource, or to open PostgreSQL broadly to make it work.
The task explicitly forbids those substitutions. Azure CLI 2.91.0 confirms the
selected `Azure for Students` subscription is enabled and contains zero
resources; it does not establish the current spending-limit state, current
credit/expiry, exact per-resource free indicators or displayed estimates.

Published Microsoft material advertises the requested PostgreSQL B1ms,
Standard ACR and Container Apps Consumption allowances. Those are general
benefits, not proof that the exact selected region/SKU is active for this
subscription. The 5 GB Azure Files item is labelled under Cloud Shell and was
not assumed to fund an MLflow artifact share. A private PostgreSQL route
normally requires a Private DNS zone, for which Azure documents a per-zone
charge. A public PostgreSQL firewall could instead list Container Apps outbound
addresses, but Azure says those addresses can change; a durable exact-address
solution has not been verified. No safe, confirmed zero-credit persistence and
network plan was available, so resource creation stopped.

This is an engineering lesson about **entitlement versus list price**: a general
free-service page and an account's promotional credit are not evidence that a
particular dependency is free. A service chain costs money if one required
supporting resource is billed. A fail-closed preflight keeps authentication,
database isolation and budget rules ahead of a public demonstration. The
alternative of paying a small amount from student credit was rejected by the
approved zero-credit boundary. Reconsider only after account-specific free
screens/estimates and a reliable free network/storage route are documented, or
after the supervisor authorizes a different task.

**Verification actually performed:** CLI subscription name/state and a zero
resource inventory; Git branch/HEAD/upstream/divergence/stash/status;
Docker context/engine/read-only inventory; SHA-256 manifests for 893 Stage 3,
frozen and task-input files plus 1,300 preceding interactive evidence files;
the corrected final rehash checked all 2,182 protected files with zero
mismatches; `git diff --check` passed. An initial comparison falsely reported
mismatches because PowerShell treated two decoded JSON arrays as nested objects.
Checking the parsed type/count and flattening the arrays fixed the verification
script; no protected file was repaired or rewritten. These are preflight checks,
not deployment or
application regression tests. Cash charged, promotional credit used, current
free-tier consumption and cost forecast are unknown. The user's earlier
INR 9,599 credit, INR 0 October cost and 2027-06-26 expiry observations have not
been independently reverified. Exact ignored evidence and sources are in
`artifacts/azure-preflight/PREFLIGHT.md`; the separate Docker cleanup dry run is
`docs/LOCAL_CLEANUP_DRY_RUN.md`. No meaningful runtime bug occurred; the
meaningful blockers were missing account-level entitlement evidence and an
unproven free network/artifact path.

**Viva/interview follow-up:** Why stop with an enabled student subscription?
Because subscription eligibility alone does not cover supporting resources,
and even a small promotional-credit charge violates this milestone. How would
you resume? Verify spending protection and each exact SKU in the portal,
establish free persistent storage and a reliable restricted PostgreSQL path,
then provision and measure the real cold-start, persistence, security and cost
behavior. No cloud performance or clinical validation claim can be made yet.

## Supervisor UI acceptance repair (2026-10-15)

This repair follows the interactive workflow milestone below. Its previous
verification did not establish acceptance of the Overview: an old component test
actually expected the preloaded 12.78% reference result. The supervisor correctly
identified that result and remaining product copy as acceptance blockers. The
historical test counts below remain historical; they do not validate this repair.

### What changed, why now, and alternatives

`frontend/src/pages/Overview.tsx` now says **No analysis is selected**, offers New
Analysis and Analysis History, and fetches only model/readiness metadata. It
neither fetches nor presents a case, prediction or attribution. This remains
truthful even when saved history exists. Automatically selecting a most recent
record would add selection and ownership behavior; the neutral state meets the
current task with less scope. The manual form still begins empty. Without this
repair, users could mistake a published reference result for their own analysis.

The legacy unselected case route redirects to New Analysis. `CaseAnalysis.tsx`
can still read an explicitly selected archived prediction without recalculation;
entered-case records use the existing analysis page. The sidebar no longer
promotes the legacy fixed-case creation screen. Sign-in and review guidance use
neutral case-analysis language.

`components/ui.tsx` centralizes presentation labels for historical protocol words.
Provenance, model-card text, reliability worked-example text, readable audit
payloads and review/history labels apply that formatter. Stored/API identifiers,
review enums, model-card source bytes, hashes, numeric outputs and audit records
are unchanged. The audit disclosure explicitly says it shows presentation labels.
This is a display boundary, not an evidence rewrite. A raw-byte search still finds
11 internal protocol/schema/compatibility/formatter occurrences in the generated
bundle; these were inspected rather than deleted. Source AST tests and rendered
route tests cover visible text, including expanded metadata. Test fixtures retain
their legitimate internal terminology and exact bytes, and remain excluded from
production imports and the frontend Docker context.

No module boundary, public API, schema, RBAC policy, frozen model, preprocessing,
explanation method, persistence or audit semantics changed in this repair. No
ML experiment, dependency, data access or new research claim was introduced.
The original 13-field mapping and prediction path below remain authoritative.

### Verification and evidence

Fresh evidence is ignored under
`artifacts/interactive-verification/ui-repair-20261015/`; the entire earlier
`resume-20261015b` verification tree is preserved. Docker Desktop's updated
`desktop-linux` engine is 29.8.2. Only the changed frontend was rebuilt and
recreated in `aletheia-interactive-20261015b`; old Stage 3/restore stacks were not
used as the review environment. The new frontend image index is
`sha256:7845f8c0f1ec7897c65c373da9af490c37c55119d60985f2534da2b26e1af185`,
with scanned config
`sha256:0ba668fa91b5dc2233e7ea3d5e8b724973052016dba03247d6232547e9f57807`.
Its exported layers match the runtime image. Fresh Trivy scan found no reported
vulnerabilities; fresh SBOM and licence inventory contain 103 licence entries.
This is not a claim of production safety. Existing backend 1 critical/55 high
and test-image 1 critical/65 high findings remain disclosed for unchanged digests.

| Final check | Actual result |
|---|---|
| Focused Vitest app/product-copy selection | 38 passed, 2 files, 36.86s, exit 0 |
| Complete `npm.cmd test -- --maxWorkers=1` (one invocation) | 80 passed, 6 files, 46.92s; wrapper 50.084s, exit 0 |
| Playwright workbench + authenticated boundary suites | 7 passed, 4.1m; wrapper 260.297s, exit 0 |
| Playwright real interactive suite against port 18081 | 1 passed, 20.0s; wrapper 21.813s, exit 0 |
| Real-journey accessibility | 18 state/viewport checks at 375/768/1440px, zero violations |
| Real persistence assertions | New/rerun identifiers differ, original immutable, Reset preserves history |
| Ruff check + format check on changed `deployment/tests/scan.py` | Passed |
| Compose validation; changed frontend build/serve/scan/SBOM/licences | Passed |

The final static command results are recorded individually in
`final-static-results.json`: typecheck, lint, formatting, production build,
OpenAPI compatibility and direct dependency licences all exited 0. The final
build used 397 modules; OpenAPI plus 10 public responses match, and 29 direct
dependency licence entries were checked. The scan helper's added
`--only-frontend` option was directly exercised and checked with Ruff; no old
Python regression result is claimed for that changed helper.

CURRENT_TASK requires one complete applicable offline regression after focused
gates. The changed frontend received the complete 80-test run above. The prior
Python regression remains 304 collected, 303 passed, 0 failed, 0 skipped,
1 live-data test deselected, 63 warnings, 3378.28s, exit 0, one invocation of
`docker compose ... --profile regression run --rm regression` (exact argument
array is in `python-regression-reuse.json`). All 104 bound input files match and
the unchanged test-image config/rootfs binding was verified. This evidence is
reused only for unchanged Python scope; it does not validate changed frontend
code or the scan option. Unchanged PostgreSQL, restore and recovery verification
was not repeated, following the task's evidence-reuse/efficiency rules.

### Important Problems Encountered - acceptance and verification repair

The main defect was a mismatch between product intent and a happy-path test:
the Overview test preserved a reference probability rather than requiring an
empty user context. The new test asserts the empty state, links, absence of the
reference probability and absence of reference-case requests. Static copy tests
plus rendered-route tests prevent checking only one visible heading while
missing expanded provenance or model-card text.

Focused test attempts exposed cold lazy model-card loading and an ambiguous
heading query. Preloading the real lazy module and allowing its legitimate
multiple headings fixed test setup without increasing timeouts. Browser tests
then exposed duplicate New Analysis links after adding the Overview CTA; desktop
navigation now scopes its locator to the sidebar. A Windows npm/Vite cleanup
chain also lingered across a user interruption; its reported 2.9h was not browser
performance. A direct owned-node harness now stops only its own Vite process in
`finally`; the final boundary suites exit cleanly.

The first real-browser attempt did not await successful session connection.
An explicit HTTP-200 wait fixes that race. A subsequent inference returned HTTP
504, while the UI retained input and offered safe retry. Its root cause was not
established; readiness and container inspection showed no restart. The test now
asserts HTTP 201 before reading response data. A fresh serial run passed without
changing application limits or restarting the backend. Failure logs are retained;
short-lived local credentials remain ignored and are not documentation evidence.

### Concepts Learned Through This Project - truthful presentation

A reference result is evidence about a published example, not a user's active
analysis. Overview state must reflect that distinction. Presentation labels can
be clearer than historical wire enums while preserving those enums and numeric
values at the API/storage boundary. Tests should assert the product requirement,
not simply reproduce the implementation they happen to receive.

### Project Defence and Interview Preparation - repair follow-ups

- **Basic: Why is Overview empty?** No analysis is selected; a user must enter
  values or explicitly open permitted saved history.
- **Intermediate: Did changing labels change the evidence?** No. Formatting acts
  on displayed strings; source bytes, hashes, stored payloads and numbers remain.
- **Difficult: Why not repeat the old Python regression?** Its complete bound
  inputs and image are unchanged. We verified those bindings and reran all
  affected frontend regression, browser, static and image checks instead.

Final protection checks found no unexplained edits: 1,338 baseline files checked,
924 original protected artifacts unchanged, all 1,148 preceding milestone evidence
files unchanged, and all three frontend fixture files byte-identical. The task
SHA-256, branch/HEAD/upstream, 0/0 divergence and stash are preserved.

The remaining scope is external supervisor review. Login, Signup, real external
OIDC, public deployment and clinical/commercial validation remain deferred.


## Interactive case input and prediction workflow (2026-10-15)

**Current milestone:** an authorized user can enter all 13 approved raw features,
run the frozen calibrated model, inspect a version-bound result, save it, reopen
it and load its inputs for a new run. Reset clears unsaved browser state. No
preloaded case is needed. 304 collected; 303 passed, 1 deselected, 63 warnings in 3378.28s (0:56:18); 0 failed, 0 skipped; exit 0 (one invocation). Supervisor review is required;
no next milestone, commit, push or public deployment is authorized.

### Purpose, sequencing and decisions

Stage 3 established local serving, release approval, database integrity and
identity verification. This milestone adds independent case input around those
boundaries. Replacing the fixed protocol-case request without strict mapping
would risk silently changing the fitted model's meaning. Inspection, mapping,
focused contract/transaction tests and UI checks therefore preceded image
security verification and the one complete offline regression.

The modular monolith, React/TypeScript, FastAPI, PostgreSQL, MLflow, frozen
joblib bundle and existing dependencies remain. No dependency was introduced.
The alternative of loading rows or fixtures into the form was rejected because
the user must supply an independent row. CSV, arbitrary columns, PII, training,
reselection and held-out access remain excluded. Form controls start empty;
loading a saved result is an explicit user action. The test-only
`frontend/tests/case-fixtures.json` is imported by component tests, never product
code. Docker excludes frontend tests/browser tests; a 50-file production asset
check found no fixture filename or fixture prediction/audit identifiers.

**Authoritative schema and field mapping.** `case-input-v1` requires an explicit
model version and all fields below; unknown properties, missing values, numeric
strings, booleans, fractions, NaN/infinity and invalid categories are rejected.
Sources are the bound feature-role configuration, fitted feature signature,
dataset documentation and UCI `IDS_mapping.csv` administrative metadata. No
patient row was opened to establish the mapping. Every field is required.

| User-facing field | Raw feature | Control and accepted values | Conversion / unit |
|---|---|---|---|
| Admission type | `admission_type_id` | Select codes `1,2,3,4,5,6,7,8` with source labels | Exact selected code string; category |
| Admission source | `admission_source_id` | Select codes `1..15,17..26`; 16 excluded | Exact selected code string; category |
| Time in hospital | `time_in_hospital` | Integer 1..14 | Base-10 string; days |
| Laboratory procedures | `num_lab_procedures` | Integer 1..2147483647 | Base-10 string; count |
| Procedures | `num_procedures` | Integer 0..2147483647 | Base-10 string; count |
| Distinct medications | `num_medications` | Integer 1..2147483647 | Base-10 string; count |
| Outpatient visits in the preceding year | `number_outpatient` | Integer 0..2147483647 | Base-10 string; visits |
| Emergency visits in the preceding year | `number_emergency` | Integer 0..2147483647 | Base-10 string; visits |
| Inpatient visits in the preceding year | `number_inpatient` | Integer 0..2147483647 | Base-10 string; visits |
| Diagnoses | `number_diagnoses` | Integer 1..2147483647 | Base-10 string; count |
| Maximum glucose result | `max_glu_serum` | Select `None,Norm,>200,>300` | Exact source string; source category |
| A1C result | `A1Cresult` | Select `None,Norm,>7,>8` | Exact source string; source percent-threshold category |
| Diabetes medication prescribed | `diabetesMed` | Select `Yes,No` | Exact source string; category |

Complete human-readable administrative option labels are centralized in
`application/case_input.py` and returned by authenticated `GET /analyses/schema`;
the UI uses that metadata directly. `None` means not measured, not a default.
Administrative NULL/unknown labels are actual source categories. The 32-bit
count ceiling is an explicit computation/transport bound, **not an observed
training maximum or clinical normal range**. Broad count acceptance does not
establish generalization at extreme values. Some valid source categories may
be unseen by the fitted encoder; the original `handle_unknown=ignore` policy
remains, with no new fitted categories or clinical interpretation.

### Input-to-result flow and architecture

`NewAnalysis` loads protected field metadata and approved serving context, then
sends a complete typed row plus UUID idempotency key to `POST /api/v1/analyses`.
The existing JWT verifier and local entitlements authorize it; rate limits,
readiness, concurrency and deadline controls apply. Strict Pydantic validation
produces deterministic source strings. `VerifiedRelease.analyze` verifies exact
feature names/order, builds one independent DataFrame row and calls the loaded
frozen preprocessing/model/calibrator through the existing probability callable.
Eight numeric features use fitted median imputation/scaling and five categorical
features use fitted one-hot encoding (43 transformed features). Required intake
values mean no meaningful missing value is silently invented. No `fit` occurs.

The model is Histogram Gradient Boosting with the existing external sigmoid
Logistic Regression calibrator. Target is recorded readmission within 30 days;
positive class is 1. The existing 0.5 threshold is descriptive, with low recall,
not a clinical action rule. The response contains probability, threshold,
category, signed factors, immutable canonical inputs, timestamp, prediction/audit
IDs, model version, frozen model hash, application release hash and audit-evidence
hash. No LLM participates. A future optional narrative would require separate
approval and could not change authoritative values.

**Identity:** model SHA-256
`8c3a99dd8dfe20d2a3a0a721637b4be500ee1b32843f7cefc3af265f07262f7a`;
new application release
`65f2302cc9c4795142567296cc6b16143fad5abfe4df7b04152975748c2ec271`;
audit results
`2d073fa0d0bbbd4debfdf445cd80ec478fef0f7098c7ef356dbb3edd28894ea8`.
The isolated local registry explicitly imported, approved and activated version
1. The wrapper changes serving code, not the six model/four audit artifact bytes.
Loading still verifies the release manifest and runtime compatibility; no fallback
release is silently substituted.

**Explanation decision:** reuse the tested probability-space paired-permutation
algorithm with 32 permutation pairs (64 paths) and seed 3105, but label this new output `case-reference-v1`.
Its single reference is the published protocol case, exposed in the result. It
is a model-agnostic local contrast against that reference, not the original frozen
research study's training-background local explanation. Fetching patient
background rows was rejected because it would expand the data boundary. The
accepted trade-offs are reference dependence, finite-path approximation and
potentially unlikely hybrid feature combinations. Signed contributions explain
changes in model probability; they do not prove causes or feasible interventions.
Frozen stability remains **model-level research evidence**, with
`per_case_score: null`; it does not validate the new contrast for an individual.
Reconsider a richer background only through a separately approved evidence task.

**Persistence decision:** running already creates an immutable prediction/audit
record, needed for retry safety and traceability; Save appends a marker that makes
it appear in Analysis History. Unsaved means absent from that history, not absent
from the audit database. Migration `0004_case_input` adds canonical inputs/result
JSONB to prediction events and an append-only saved-analysis table; old rows
remain valid. The original transaction stores output, identity, input hash,
model/evidence references and idempotency response atomically with audit. A failed
audit rolls back prediction. Save locks/authorizes the owner and is repeat-safe;
database grants/triggers reject history mutation and validate save/audit links.
Reopening reads the stored snapshot without inference. Reviews remain separate
append-only revisions. Loading inputs creates editable browser state; a successful
new submission creates new prediction/audit IDs. Reset cannot delete records.
History uses UUID keyset pagination, not chronological sorting.

**RBAC:** engineers read their own records; reviewers/administrators retain wider
read/review scope. Saving is owner-only. Legacy prediction/review routes preserve
their scope and show entered-record evidence correctly. The optional local token
screen is compiled only with `VITE_LOCAL_IDENTITY=true`; backend `/session` also
requires test/development identity mode. It verifies existing signed provisioned
tokens and intersects claims with current database grants. Tokens stay in memory;
refresh needs reconnection. No password, registration, issuer or parallel auth
system was added. Login, Signup and real external OIDC remain future scope.

### Important Problems Encountered and recovery

| Problem / symptom | Root cause, repair and verification | Lesson / prevention |
|---|---|---|
| Legacy prediction tests failed after adding nullable snapshots | JSONB serialized Python `None` as JSON null, violating SQL-null compatibility; `none_as_null=True` restores old-row semantics. Focused real-PG suites pass. | JSON null and SQL NULL differ; test existing callers and old records. |
| Calibration oracle failed before the main integration run | The frozen calibrator is a sklearn estimator, not a coefficient tuple; independent sigmoid math now reads its fitted coefficient/intercept. | Inspect actual serialized object shape; do not alter the artifact to satisfy a test. |
| Historical migration replay/current-head checks disagreed | Explicitly replay historical catalog tests to 0003, update simulated current head to 0004, and test a real 0003 record through 0004. | Preserve historical evidence while adding a separate forward-compatibility test. |
| Docker unavailable/updated during interrupted work | Resume required engine health and source/diff/protection review; current engine is desktop-linux 29.8.2, previous 29.7.2. Fresh project separates this milestone from old restore containers. | Engine/context and project identity belong in verification evidence. |
| Host PostgreSQL focused connection stalled | The isolated internal Compose network did not accept host-loopback connections; stopped only the owned test processes and ran focused tests inside that network. | Test through the intended network boundary; the incomplete host run is not a pass. |
| Frontend lazy-component tests timed out under contention | Serial final run passed 66 tests without relaxing assertions or timeouts; concurrency was implicated, no deeper root cause proved. | Separate resource contention from behavior defects. |
| An unfinished browser harness imported test helpers incorrectly | Replaced it with a compatibility entrypoint to the real isolated-stack browser runner. The real browser journey passed. | Verify production paths rather than building a second fixture-only application. |
| Generated OpenAPI snapshots failed formatting | Format only those snapshots, then rerun format/contract checks successfully. | Generated contracts still follow repository formatting. |
| Complete regression spent substantial time in registry integration | Live fixture logs showed repeated successful local artifact requests and no HTTP 500 responses during observed progress; memory remained below the existing 1.5 GiB limit. The exact cause of elapsed-time differences was not established. Retained the same complete invocation without skipping tests, changing limits or restarting. | Distinguish slow integration work from a stalled process; preserve one complete result rather than combining partial runs. |

The scanner refreshed its database over a slow network before scanning; no cached
old backend/frontend result was substituted. Original failed/incomplete logs are
retained under ignored interactive-verification evidence. No model, preprocessing,
held-out split or research conclusion was repaired or changed.

### Verification and resume evidence

Evidence root: `artifacts/interactive-verification/resume-20261015b`; fresh Compose
project `aletheia-interactive-20261015b`. All generated secrets/logs/scans/databases
remain ignored. Unchanged PostgreSQL/test image evidence is reused only after
exact digest/layer verification; All 914 Stage 3 evidence files and 1079 protected files in total match their starting hashes; zero mismatches. Task hash, HEAD, stash and upstream alignment remain unchanged. New backend
and frontend have fresh scans, SBOMs and licence inventories. Current scan reports
backend critical/high/medium/low/unknown 1/55/116/105/1 and frontend zero findings.
All 122 retained backend/test-image high/critical entries have dispositions;
native SQLite 3.54.0 linkage/hash/public-domain licence are explicitly supplemented.
MiniZip absence supports the retained zlib critical disposition; no vulnerability-
free or public deployment claim. The pip latest-release lookup is historical
2026-10-14 metadata, not a new lookup. See new security JSON for exact advisory,
component, installed/fixed versions, layer, exposure and mitigation.

| Executed check | Exact result |
|---|---|
| Real-PG focused files `test_case_input.py test_case_workflow.py test_postgres_api.py test_repair_postgres.py`, disposable container, `python -m pytest ... -p no:cacheprovider` | 84 collected/passed; 0 failed/skipped/deselected; 1 warning; 98.75s; exit 0 |
| Final focused three files (same command, excluding repair file) | 40 collected/passed; 0 failed/skipped/deselected; 1 warning; 38.07s; exit 0 |
| `pytest tests/deployment -q` with ignored cache | 5 passed; 0 failed/skipped/deselected/warnings; 6.50s; exit 0 |
| Frontend `npm test -- --maxWorkers=1` | 66 passed in 5 files; 0 failed; 41.22s; exit 0 |
| `python deployment/tests/interactive_browser.py` | 1 real browser journey passed; 22.0s total; 15 axe state/width checks, zero violations; overflow checks pass; exit 0 |
| Ruff check / format; `pip check` | All checks pass; 111 Python files formatted; no broken requirements; exit 0; new helper subsequently checked again |
| Frontend typecheck/lint/format/build/contract/licences/tree | All exit 0; 397 production modules; real OpenAPI and 10 public responses match; 29 direct licence records; consistent dependency tree |
| `npm audit --omit=dev --audit-level=high --json` | 0 vulnerabilities at every severity; exit 0 |
| Compose validation; two changed-image builds; migration/stage/import/approve/activate | All exit 0; fresh serving stack healthy before regression |
| `interactive_stack.py scan` / `security` | Both exit 0; four image/SBOM bindings pass; new changed-image reports and licence inventory |
| Complete offline regression | 304 collected; 303 passed, 1 deselected, 63 warnings in 3378.28s (0:56:18); 0 failed, 0 skipped; exit 0 (one invocation) |

Focused runs overlap and are not summed into a full-suite count. The single full
invocation and runner details are recorded in the current supervisor handoff.
Warnings include Starlette/httpx deprecation, MLflow type-hint notices, sklearn
penalty deprecation and the deliberately rejected short-HMAC test fixture; no
dependency was changed merely to silence them. This milestone adds software checks, **no new ML
experiment or generalization metric**. Local Compose verification is not cloud,
load, commercial, financial or clinical validation. Old Stage 3 restore evidence
is preserved and is not presented as a new schema-0004 restore exercise.

### Concepts learned, Project Defence and Interview Preparation

**Canonicalization and preprocessing parity:** map a typed UI integer such as 4
to the exact source string `"4"`, preserve category strings and column order,
then use the fitted transformer. Explain why fitting again at inference would
change model semantics and why an independent sigmoid oracle is stronger than
comparing two calls to the same wrapper.

**Immutable snapshots and append-only events:** store the original result once;
Save and review append state transitions. Explain the transaction boundary,
idempotency versus a deliberately new run, SQL NULL versus JSON null, and why
resetting UI state is unrelated to database deletion.

**Reference-dependent attribution:** changing only `number_inpatient` from 1 to 4
in a software check changes probability from 0.1278216918809014 to
0.23085593739625732. The one changed feature receives the probability difference;
all unchanged features receive zero. This is a model contrast, not a patient
outcome estimate, causal recommendation or validated recourse example. For
multiple changes, averaged permutation paths allocate model interactions.

**Semester viva â€” Basic:** What are the 13 inputs? See the mapping above. Why
reject names? They are outside the approved fitted feature schema and privacy
boundary. Does reopening run the model? No, it reads a stored snapshot.

**Intermediate:** How do retries avoid duplicates? Same canonical body and
idempotency key reuse the committed response; edited inputs/new runs use a new
key. What makes the result authoritative? Verified frozen model/calibrator and
explicit model/release/evidence identities, not a browser fixture or LLM.

**Difficult:** Does model-level stability prove this case explanation is reliable?
No; it describes the frozen research protocol, not individual validation of the
new reference contrast. Why retain run records before Save? To bind prediction,
audit and retry semantics atomically; Save controls membership in user history.
How does migration preserve old evidence? Leave old migrations/records intact,
test historical 0003 catalog separately, then test forward migration of a stored
legacy prediction to 0004.

**Limitations and future work:** historical dataset generalization, descriptive
low-recall threshold, source categories unseen during fitting, extreme count
inputs and reference dependence remain. No individual stability score or clinical
decision is claimed. Login, Signup, external OIDC and optional carefully bounded
LLM narration need later approval. Useful next work begins with external
supervisor review; richer explanation research and cloud deployment are separate
future tasks, not work started here.


## Stage 3 release-evidence repair (2026-10-14)

**Current repair status:** focused repair complete. Image/security and
functional checks pass; one complete isolated container regression exited 0:
276 collected, 275 passed, zero skipped, one live-data deselected, 63 warnings
in 2251.04s. Local Stage 3 is defensible for commit and supervisor review;
this is not approval for public deployment. This section
supersedes the image/security counts and measurements in the retained checkpoint
below. No cloud or synthetic-case-builder work was authorized or implemented.

**Decision and implementation:** `deployment/Dockerfile.api` keeps frozen Python
3.12.10 and every Python pin, but builds upstream SQLite 3.54.0 in a separate
compiler stage. The download is pinned by SQLite's published SHA3-256; only its
shared library enters the runtime, replacing vulnerable Debian SQLite. This fixes
CVE-2025-7458 and the two reported SQLite high findings without retraining or
changing artifact versions. Moving to another Python/distro or retaining the
vulnerable library was less suitable; the accepted cost is maintaining a native
library outside Debian's package inventory. Python linkage and synthetic scoring
pass; `security.py` supplements the SBOM/licence inventory explicitly rather than
pretending Trivy detected that library. PostgreSQL removes unused `gosu` because
Compose already enforces UID 70. Git remains exclusively in the test image.

**Security and deployment context:** backend changes from 2 critical/57 high to
1 critical/55 high; regression from 2/67 to 1/65. PostgreSQL's gosu critical and
24 high findings disappear; final scan reports zero findings, as does the
unchanged frontend. These are scanner results, not vulnerability-free claims.
The retained critical CVE-2023-45853 concerns MiniZip, which Debian Bookworm does
not build into this zlib binary; runtime inspection finds neither MiniZip files
nor its affected exported function. No fixed Bookworm zlib package is reported.
Residual risk must be reconsidered if MiniZip is introduced. Remaining OS highs
have no fixed Bookworm version reported. Four pip-vendor highs have upstream
fixes, but pip 26.2.1 is still the latest released pip; top-level setuptools and
urllib3 already have fixed pins. Configured services do not run pip on untrusted
input. Avoid unsupported vendor surgery; monitor a future compatible pip release.
Non-root execution alone was never a disposition. Local PostgreSQL is verification
infrastructure; cloud will use managed PostgreSQL. Regression must never deploy.
Exact advisory/component/version/layer/fix/exposure/disposition records and image
bindings are in `artifacts/stage3-verification/repair-security-disposition.json`.
Sources: [Debian SQLite](https://security-tracker.debian.org/tracker/CVE-2025-7458),
[Debian zlib](https://security-tracker.debian.org/tracker/CVE-2023-45853), and
[SQLite source/checksum](https://www.sqlite.org/download.html).

**Verified behavior and problems:** six E2E groups, six recovery groups, restored
databases/three volumes and identical prediction/audit/readiness checks pass on
final images. Proxy browser checks pass 33 route/viewport cases with zero axe
violations. All 102 applicable Python pins match. Fresh-container readiness is
266.360s; healthy restart 74.031s; ten synthetic HTTP requests span 563-2906ms.
Three idle samples total 595.755/603.010/596.024 MiB; seven workload samples span
595.846-622.763 MiB. Regression ran concurrently; these are local observations,
not production latency or peak-load claims. Three-second API/MLflow probes timed
out during the resource rehearsal, then recovered without weakening budgets;
the rehearsal exited 0. Root cause of the slower measurement is not established.
Initial build invocation omitted the overlay's identity profile, and the first
regression launch used unsupported `run --no-build`; neither collected tests.
Their logs remain preserved. The security helper's explicit package list caught
a missing util-linux subpackage; corrected inventory passes without hiding a CVE.
The first complete repair regression exited 1: 274 passed, one failed, one
live-data deselected, 60 warnings in 3075.28s. The reconciliation test's MLflow
metadata GET exceeded the unchanged ten-second deadline; other registry cases
passed. Concurrent serving/recovery/resource checks and transient health-probe
timeouts establish scheduling pressure as a plausible contributor, not a proved
sole cause. The complete rerun uses a new isolated project, three test-only CPU
cores and stopped serving workloads, preserving every assertion/deadline and
all volumes. A test-only diagnostics mount retains MLflow logs/cgroup counters
after runner disposal. The original failure log is retained. The new complete invocation passes
275 tests with one live-data deselected, zero skipped and 63 warnings in
2251.04s; exit 0. Acceptance uses this run alone, never combined coverage.
A perceived stall at 4% was diagnosed live: all nine registry tests had passed,
PostgreSQL had no blocking PIDs, pytest was runnable, and MLflow health/metadata
GETs returned 200 in 0.331/0.349s. Its log contains 3,121 HTTP records and 1,451
artifact GETs from repeated package-integrity checks. Cgroup counters show zero
CPU throttling/OOM events and 733,487,104-byte peak memory. The MLflow child
inherited its fixture-start test label; that label is not the live pytest node.
The run completed without a duplicate invocation, forced termination or timeout
weakening. Duration and request volume explain why progress must be assessed
from multiple live signals; they do not prove the first run timeout's sole cause.

**Learning/defence:** an image tag is mutable; config/layer digests bind a scan to
the actual software. Why can a reported critical remain? Package matching must be
checked against the affected binary code and permitted request path; retain the
finding and evidence, rather than suppressing it or relying on UID. What changes
invalidate that answer? Different image contents, introducing MiniZip, or allowing
untrusted SQL/tool/archive inputs. Native ABI compatibility also needs runtime
linkage and integration evidence, not just a successful compiler invocation.
No ML experiment or metric was added. Real external OIDC, cloud/TLS/CI/monitoring
and a synthetic case builder remain unimplemented and require later approval.

### Previous Stage 3 verification checkpoint

## Macro Milestone 4 Stage 3 - local deployment verification (2026-10-13 to 2026-10-14)

**Purpose, sequence and implementation:** package the already-tested Stage 1
API/operator contract and Stage 2 UI before considering any public delivery.
`deployment/compose.yaml` runs private PostgreSQL, MLflow and FastAPI behind a
loopback-only non-root NGINX static frontend. Separate application owner/runtime
and MLflow roles limit database access. Operator-profile migration, release-stage
and release-import jobs make state-changing actions explicit. Synthetic HTTPS
JWKS and the isolated PostgreSQL regression network exist only in the test
overlay. No schema, public API, research method or approved architecture changed.
Images came first, then synthetic E2E, reversible failures, backup/restore and
resource/security evidence: each later check requires the previous boundary to
work. Initial interrupted results are retained as historical evidence below.

**Flow and decisions:** browser -> bounded same-origin proxy -> existing API ->
verified frozen release -> synthetic inference -> one PostgreSQL transaction
covering prediction, idempotency and audit -> response. Explicit import copies
unchanged model bytes into MLflow; approval/activation establish the deployment
pin. Neither aliases nor service startup authorize a model. Compose was chosen
over host setup drift or unnecessary Kubernetes. One backend image uses the
existing complete lock for API, MLflow and jobs, with a derived test-only Git
image for isolated regression; this avoids
new dependency resolution but retains test/tool packages and increases size.
Multi-stage frontend packaging leaves Node/build dependencies out of its runtime.
Digest-pinned bases plus OS security upgrades were chosen over leaving fixable
base findings untouched. OS repositories change, so base pins and Python/Node
locks do not guarantee identical rebuilt image bytes; final IDs identify tested
images. Python 3.12.10 and frozen-library pins remain unchanged. Reconsider the
shared backend image or pinned Python only under an approved compatibility task.

**Verified behavior:** saved E2E evidence covers public routes, SPA fallback,
authenticated fixed-case prediction, SQL persistence, reviewer/audit linkage,
RBAC, administrator evidence, idempotency and rejection of arbitrary submissions.
MLflow outage retains approved pinned serving; PostgreSQL/audit failure suppresses
success, and API outage preserves static UI without fabricated evidence. Recovery
checks verify an absent-database migration failure, a mismatched release anchor,
interrupted startup, bounded body/internal routes and graceful persistent restart.
The accepted healthy-restart measurement is 43.734 seconds. `restore.py` quiesces
writers, dumps both databases and archives registry/state/release volumes. A
unique isolated restore verifies file hashes/permissions, the identical saved
prediction, review audit link and approved readiness; revocation then blocks
readiness/prediction there. This is a local rehearsal, not remote disaster recovery.

**Problems, fixes and learning:** a three-second test identity probe timed out
under constrained CPU; Docker health history verified timeout rather than bad
TLS. Test-only CPU/probe allowances were adjusted, without relaxing authentication.
Restore initially compared whole tar bytes, then exposed safe extraction changing
ordinary permissions. The final implementation compares paths/types/content
hashes/modes and preserves ordinary permissions through a safe path filter;
special permission bits and unexpected member types are not restored. All failed
backup attempts remain in ignored evidence. A new unit test proves timestamp
changes are harmless while byte/permission changes are detected. The migration
failure probe initially had a harness assignment error; reading its log prevented
false acceptance. It was corrected and both negative probes now assert the exact
intended error. Container regression's repeated full MLflow verification is slow;
its isolated runner allowance increased from one to two of eight engine CPUs.
Failures, recovery and final evidence remain distinguishable. One-shot jobs now disable the inherited API health probe; a regression process does not serve port 8000, so its exit result is the relevant check.

**Security evidence and limits:** final Trivy 0.75.0 scan/SBOM/licence commands
completed for all three images. Frontend: zero reported vulnerabilities. Backend:
57 high/2 critical; PostgreSQL: 24 high/1 critical. Backend critical OS findings
are CVE-2025-7458 and CVE-2023-45853, with no fixed version reported for the
installed Debian packages. PostgreSQL's critical CVE-2025-68121 is in the base
image's Go-built `gosu`, despite running PostgreSQL directly as UID 70. Vendored
Python packages are also scanned; installed top-level pins must be checked
separately. These are findings requiring review, not a clean security gate or
proof of exploitability. SBOM/licence entries support inventory, not legal clearance.
Release readiness remains subject to supervisor disposition of findings and real
OIDC integration. HTTP-only local proxy emits no HSTS; TLS hosting, provider
login/logout, public delivery, CI/CD and monitoring remain unimplemented.

**Concepts and defence:** an image is software; a named volume holds durable
state; a health probe reports service liveness; application readiness additionally
checks approval, integrity and database availability. A backup exists only when
it can be restored and its contents/behavior checked. Basic viva: why does `stop`
retain predictions? PostgreSQL named volumes persist independently of containers.
Intermediate: why can MLflow be offline while predictions work? Serving verifies
the local approved pin rather than promoting an alias. Difficult: why did two
negative tests need log assertions? Any nonzero exit could otherwise be mistaken
for the intended failure. Why not claim the model became better? Packaging and
synthetic integration introduce no new research experiment or clinical evidence.

**Measured boundaries:** fresh containers with cached images/existing approved
volumes reached application readiness in 49.375 seconds. Three five-container
idle snapshots used 576.416/587.248/576.754 MiB; the one workload snapshot used
582.038 MiB. Aggregate CPU was 0.45/95.29/0.41% idle and 88.69% workload
(100% = one core); health probes cause bursts. Ten sequential synthetic HTTP
requests took 109-250 ms including authentication, inference and transactional
audit, not model-only inference. Isolated regression ran concurrently. These
are laptop measurements, not sustained-load/peak or clinical latency claims.
Image inspect content sizes were 538,823,213 backend, 31,274,769 frontend and
123,006,605 PostgreSQL bytes; Docker displayed combined local storage as
1.87 GB/110 MB/444 MB. Both conventions are retained. Runtime checks verified
non-root UIDs, ALL capabilities dropped, private ports, release integrity,
absence of patient identifier columns/logged fields and 102 exact Linux pins.
The final proxy browser smoke passed 33 route/viewport accessibility checks
with zero axe violations plus keyboard/dark/reduced-motion checks. Five
deployment boundary/restore-integrity unit tests passed; full container
regression's exact final result belongs in the handoff, not an assumed count.

**Container test-environment recovery:** the initial full offline container run
finished with 263 passed, one failed, ten setup errors, one live-data deselected
and 63 warnings in 3393.19s. Every failed/error case needed Git for provenance,
which the minimal production image intentionally lacked. The nine registry cases
all passed, including six real crash-recovery boundaries. `Dockerfile.regression`
adds Git only to a test image; `workspace.py` copies 189 existing HEAD objects and
the index into detached, read-only test metadata, without branches, parent
history, stash or actual repository mutation. No fake Git executable or invented
revision is used. Verification resumes with the other tests plus the new backup
unit test while preserving the nine successful registry cases. The repaired run passed 266 tests, deselected one live-data test and emitted 27
warnings in 265.58s. With the nine previously passing registry cases, all 275
current offline tests have passing coverage. Exact results are in the handoff; this is coverage across runs, not a claim of a single
clean full-container run. The future default command runs the entire suite.

**Scanner recovery:** the combined test-image scan hit a 15-minute layer-analysis
timeout; the log named Git copyright metadata. A vulnerability-only Windows-cache
retry also remained slow and was explicitly stopped; both logs are retained.
Observed memory use was 26.5 MiB and host free disk about 21.7 GB, so exhaustion
was not observed. A labelled, project-owned Linux cache volume and staged archive
then completed vulnerability scanning and CycloneDX SBOM generation. A direct
Debian inventory records 123 package versions, copyright hashes and licence
headers; the timed-out licence analyser is not reported as successful. Cache/I/O
was a suspected contributor, not a proved sole root cause. Test image findings:
67 high/2 critical, alongside inherited/backend findings. All four exported
config digests and layer inventories match runtime images. The scanner cache
volume and earlier cache/logs are retained; production images/pins did not change.

**Review evidence:** `artifacts/stage3-verification` contains E2E, recovery,
restore, proxy-browser and final scanner/SBOM outputs; exact remaining checks and
measurements are recorded in `SUPERVISOR_HANDOFF.md`. All 158 protected baseline
hashes, including task bytes and frozen research files, match. No held-out access,
training/reselection, responsible audit rerun, stash modification, later stage,
branch/history change, commit or push occurred.

### Historical interrupted Stage 3 checkpoint

**Status at that checkpoint:** incomplete; Docker storage failure blocked container
verification. Stage 3 follows stable backend/frontend contracts so packaging can
be checked against actual behavior. Configuration, not a running deployment, is
now written in `deployment`: multi-stage API/static frontend images, non-root
proxy, private database/MLflow network, separate database roles and secret files,
explicit migration/release staging/import jobs, persistent volumes and bounded
resources/restart policies. No backend/frontend or frozen source file changed.

**Flow/decisions:** proposed browser -> same-origin NGINX -> existing FastAPI ->
existing approved release/PostgreSQL transactions. Operator explicitly migrates,
stages verified bytes, bootstraps, imports, approves and activates; startup does
none of those actions automatically. Python 3.12.10 remains exact because the
protected loader compares complete runtime versions. All four base images are
digest-pinned. The existing full dependency lock is retained; no Python/Node pin
changed. Linux `libgomp1` supplies the existing classifier's OpenMP runtime, not
a new ML method. Static proxy and one worker avoid additional resident services.
CSP keeps scripts restricted and permits style attributes for the existing
probability/contribution bars. Budgets are targets, not measurements. A test-only
HTTPS JWKS fixture and isolated trust-auth regression database are excluded from
production images/network. Real external OIDC/logout remains unverified.

**Verified preparation:** existing Stage 1 release builder produced digest
`9983f7b574fb8e2bfe43df4a12b5900f061bcbef28d9efc3203f4f25ccb83b22`, copying frozen
bytes without model reserialization. The offline test workspace copies 94
software/evidence files with byte equality and no raw data. Three deployment
boundary tests pass. Final Compose config validation passes. Host Python offline
run: 205 passed, 68 PostgreSQL/MLflow tests skipped, 1 live-data test deselected,
27 warnings in 110.64s; this does not satisfy database/container acceptance.
Frontend typecheck/lint/format/build/contract/license/dependency checks pass;
production npm audit finds zero vulnerabilities. Full exact results and remaining
gates are in SUPERVISOR_HANDOFF.md. No new research metric is recorded.

**Important problems and recovery evidence:** Docker was initially stopped;
permission-approved startup exposed a 3.72 GiB Linux engine. Compose's initial
build booted its own `buildx_buildkit_default` helper; explicitly selecting the
existing default builder let the build progress, but both paths later failed.
API wheel download hit a read-only filesystem; frontend/scanner layer commits
hit containerd I/O errors. Host free disk was 1,196,371,968 bytes on a
254,500,925,440-byte C: volume. Low space is a possible contributor, not a proven
root cause. The approved restart remained in starting status with API 500 errors;
only its confirmed waiting CLI PID was stopped. No Docker data was pruned,
reset or deleted; the helper's state must be inspected before any later cleanup.
Scout required account login; the pinned Trivy fallback failed during image pull,
so neither produced a scan or SBOM. Initial frontend tests had two lazy-page
timeouts during concurrent checks (root cause unproved); a serial rerun passed all 59 without changing
code/timeouts, although redirected npm notices produced a PowerShell wrapper
error. Direct `npm.cmd test -- --maxWorkers=1; exit $LASTEXITCODE` then exited 0:
59 passed in 45.32s. Lesson/viva: distinguish
configuration, successful image build, running services and measured acceptance;
resource failures and skipped tests cannot be reported as completed deployment.

**Limits/next step:** supervisor/user restores disk capacity and Docker storage
health, then resumes this same Stage 3 task. Container E2E, migrations/registry
integration, proxy browser/accessibility, outage/revocation/audit failure,
backup/restore, security scans/SBOM and actual resource/image measurements remain
unverified; backup/restore tooling still needs implementation. Protected research,
CURRENT_TASK and stash remain unchanged. No model training/reselection, holdout
access, responsible audit rerun, public hosting, CI/CD, later feature, commit or
push occurred. This partial record authorizes no subsequent milestone.

## Stage 2 supervisor repair (2026-10-13)

**Discrepancy and correction:** five current-state documents still described
FastAPI/PostgreSQL/MLflow, RBAC and React as future work after their local Stage 1/2
implementation. Updated summaries/roadmap/tool statuses and labelled retained
Stage 0 and earlier designs historical. No architecture, API or UI behavior changed;
absent Stage 1 evidence still reads "Not published". The existing report below
preserves the original implementation and verification history.

**Dependency decision:** npm marks ESLint 9.39.1 unsupported; the official ESLint
support policy lists v9 as EOL. Registry metadata confirmed compatible exact pins:
`eslint` 10.12.0, `@eslint/js` 10.0.1, `eslint-plugin-react-hooks` 7.1.1 and `globals`
17.13.0. `typescript-eslint` 8.71.2 already supports ESLint 10 and remains unchanged.
Node 24.20.0/npm 12.0.2 were used. npm regenerated the lock; 25 other direct pins
are unchanged and all 50 changed package entries belong to the lint dependency
graph. Existing flat configuration passes without editing or suppressing rules.

**Commands/results:** `npm.cmd install --save-dev --save-exact eslint@10.12.0
@eslint/js@10.0.1 eslint-plugin-react-hooks@7.1.1 globals@17.13.0` succeeded;
`npm.cmd ci` installed 343 packages/audited 344 with zero vulnerabilities.
`npm.cmd ls --all`, `run typecheck`, `run lint`, `run format:check`, `test`,
`run build`, `run contract:check` and `run licenses` all exited 0. Tests: 4 files,
59 passed in 103.42s. Build: 394 modules, 6.84s; unchanged 407.38 kB initial and
159.32 kB deferred JS (123.65/47.80 kB gzip); a plugin-timing advisory was printed.
Contract: real OpenAPI and ten public responses match. Licenses: all 29 direct
versions/metadata present. Production audit with `--omit=dev --audit-level=high`
exited 0, zero vulnerabilities. Seven-document checks resolve 60 local links,
balance all fences and count 14 Mermaid blocks (not rendered); contextual stale
status review and lint-only lock scope pass. `git diff --check` passes. Exact
commands, final scope and limitations are in SUPERVISOR_HANDOFF.md.

**Problems/recovery and lesson:** sandbox registry queries failed with EACCES;
approved outside-sandbox npm queries/install/audit succeeded. An initial patch
context mismatch and PowerShell Unicode-pipe conversion interrupted doc edits;
inspection followed by ASCII-safe replacements preserved scope. The initial doc
check incorrectly sliced summaries before their status text; checking the first
35 lines resolves that tooling error. Current-state facts, historical contracts
and verified runtime support must be checked separately; a passing build alone
does not establish dependency support or accurate documentation.

**Limits and boundary:** real external OIDC-provider integration remains unverified;
sign-out clears local state only. Live OIDC logout remains a Stage 3 verification
item. Docker Compose, CI/CD, public hosting and production monitoring remain
unimplemented. No new ML result, retraining/reselection, holdout access, responsible
research audit rerun, protected artifact change, stash restoration or Git mutation
occurred. Browser/Python suites were not rerun for this documentation/lint-only
repair; their earlier evidence is historical. Stage 3 did not begin. Starting
main/HEAD/local origin/main were `9a6831205f50643c12a92020a0c4e03879d49904`, with a
clean tree; the existing stash object remains `c6b91a13bf4338e559dfaad49f850dd719f5ca47`.

## Macro Milestone 4 Stage 2 — Frontend application (2026-10-13)

**Current overview and milestone:** the local Stage 1 FastAPI/PostgreSQL/MLflow
foundation now has a React/TypeScript evidence workbench. Overview, Case Analysis,
local/global Explanation, Reliability (stability/subgroups/feasibility), Review,
Audit Trail, Model Card, organization sign-in and read-only administrator release
views are implemented. Public visitors inspect published evidence; authorized
users request the fixed synthetic prediction and review its evidence. No patient
intake, clinical advice, new research experiment or deployment was added. Earlier
dated sections preserve history rather than the current application status.

**Why now and architecture flow:** Stage 1 established the real serving and
transaction contracts, so UI work can display their evidence without inventing
ML behavior. `frontend/src/main.tsx` connects BrowserRouter, SessionProvider and
the application; `components/Shell.tsx` provides navigation, focus, appearance and
route loading. Page modules call `api/context.tsx` resources and `api/client.ts`;
Zod schemas in `api/contracts.ts` validate versioned envelopes/data and required
evidence identities. Requests carry correlation IDs, bounded cancellation and,
for private paths, access JWTs. The API remains responsible for authorization,
calibrated inference, PostgreSQL persistence, idempotency and audit writes. The
browser computes no model/explanation/fairness results. This implements the
approved architecture without changing backend modules, schema or public APIs.

**Decisions and trade-offs:** React Router handles a static SPA; local component
state/context avoids an unnecessary state-management dependency. Zod guards
runtime JSON because TypeScript alone cannot validate a server response. OIDC
code flow with PKCE uses `oidc-client-ts`; tokens/user records stay in memory,
with only transient login state in sessionStorage. Reload therefore requires
sign-in again. UI role hints do not grant backend permission. Viewer is public;
Clinical Reviewer maps to `reviewer`, Model-Risk Auditor to `engineer`, and
administrator permissions remain separate. Without provider configuration the
sign-in control is explicitly unavailable. A homemade login/token persistence
scheme was rejected in favor of the approved identity boundary.

**Evidence and request paths:** public health/model/card/case/XAI/stability/
subgroup/feasibility projections supply actual values and provenance. The fixed
case is read-only. Contributions explain the complete calibrated probability;
calibration is not an additive feature, and unavailable raw scores/lineage remain
explicit. Subgroup support, suppressed counts and uncertainty are preserved;
no fairness certification is claimed. `no_feasible_scenario` is a valid
no-search/no-candidate result, never advice. Prediction and review POSTs use a
stable key/body during uncertain retries; changed revision/version conflicts
require refresh. Reviews use the actual coded-reason contract, not unsupported
free-text comments. Audit uses bounded cursor pages and clearly labels filtering
as applying to the loaded page. Actor roles and full-chain verification are not
published by Stage 1; the UI reports that limitation instead of inventing them.

**Important problems and recovery:** the interrupted browser suite failed Model
Card at mobile/tablet. DOM inspection isolated seven inline SHA-256 code strings:
their right edges were 528.625px on a 375px viewport and 788.625px on 768px.
`styles/app.css` now wraps inline code without clipping or changing evidence.
Markdown tables retain local scrolling and gain a named keyboard-focusable
region. A 566.51 kB (171.15 kB gzip) initial JS chunk produced a build warning;
lazy loading Model Card/release routes splits the Markdown renderer into a
159.32 kB (47.80 kB gzip) chunk, leaving 407.38 kB (123.65 kB gzip) initially.
No warning threshold was raised. Component tests now await deferred rendering.
Sharing JSON fixtures with Node browser tests required an explicit JSON import
attribute; review success assertions distinguish success from concurrent loading.
Windows sandbox restrictions prevented Playwright's server-tree cleanup; the
owned Vite tree was stopped with approval and later browser runs used permitted
cleanup. Editing tsconfig during a browser run triggered Vite navigation and
invalidated one accessibility evaluation; final verification uses stable files.
The user-authorized accidental repository-local notification hook was confirmed
and removed with its empty parents; real user configuration was not accessed.

**Verification and resume evidence:** 59 frontend unit/component/client/contract/
session tests pass in four files. The final browser suite passed **7 tests in
1.5 minutes with zero retries**. Browser checks cover 11 public routes and seven
authenticated route states at 375/768/1440px, with WCAG-tagged axe checks, viewport
and control bounds, keyboard navigation, table focus, review submission, dark
appearance and reduced motion. Exact final commands/results are in the handoff.
The real FastAPI export matches OpenAPI and ten public response snapshots; it
builds a temporary verified release without source data or research execution.
Dependency consistency, strict TypeScript (including browser tests), ESLint,
Prettier, build and all 29 direct-dependency licence/version checks pass.
Python/backend/research files were not changed: preserve the earlier continuation
suite's **270 passed, 1 deselected, 63 warnings in 867.97s**, rather than repeat it.
Python pip/Ruff checks were rerun. 113 baseline file hashes remain unchanged
outside the three authorized documentation updates. No new ML metric is claimed.

**Concept learning and defence:** runtime contracts validate untrusted data;
idempotency resolves an unknown transaction outcome without duplicating writes;
route splitting defers code rather than hiding a size warning. Basic viva: why
cannot TypeScript validate HTTP JSON? Types disappear at runtime. Intermediate:
why retain a retry key/body? The first request may already have committed.
Difficult: why cannot a filtered audit page prove chain integrity? Hidden events
and the trusted checkpoint are unavailable to that browser view. Inspect the
client, Review page, session provider and both browser specs for worked paths.

**Limitations and advisory next step:** tests use real public FastAPI exports and
boundary mocks for private UI/identity flows, not a live organization provider or
deployed end-to-end stack. Automated accessibility checks and screenshots do not
prove complete assistive-technology coverage; browser execution used Edge only.
Published metrics remain historical and educational. No browser fixture fallback
exists in runtime source. Stage 3 Compose/hosting/CI, real-provider validation and
deployment resource/security gates remain unimplemented. Stop for external Stage 2
review; the supervisor alone authorizes progression.

## Macro Milestone 4 Stage 1 — Backend implementation (2026-10-11)

The existing backend foundation was preserved and repaired under the supervisor's
Stage 1 task. Earlier Stage 0 entries are planning history; this work does not
authorize Stage 2 or represent production deployment.

**Implemented flow and locations:** [release.py](../src/aletheia/application/release.py)
verifies approved original inventories/bindings before joblib loading, copies bytes,
binds application code/dependencies in a separate manifest and checks the fixed
synthetic probability within 1e-10. [registry.py](../src/aletheia/application/registry.py)
imports the complete calibrated models-from-code adapter and historical metrics.
New versions remain `verifying` until independent download, inventory/hash checks,
calibrated synthetic parity, durable receipt and completed run. An independent
intent permits deterministic crash recovery; conflicts are quarantined. Exact
PostgreSQL registration is idempotent. Approval and lifecycle publication reconcile
the same database event, MLflow tags/aliases and atomic deployment pin. Pending
publication fails readiness; a registry alias cannot authorize serving. Valid
pinned cached serving does not query MLflow per request.

[api.py](../src/aletheia/application/api.py) rejects extra/patient fields and accepts
only synthetic-discharge-v1. Access JWT verification plus active local entitlements
precedes inference; [store.py](../src/aletheia/application/store.py) rechecks permissions
and approval, then commits result/review, canonical chained audit event and
idempotency reference together. Lost acknowledgements retry the same key; changed
payloads conflict. Reviews append revisions; reviewer event visibility is scoped.
[migrations](../migrations/env.py) enforce PostgreSQL constraints, restrictive FKs,
append-only history and attributed grants with separate owner/runtime privileges.
Migration `0003_integrity` adds deferred reverse audit bindings and one deployment
projection: orphan or mismatched business events cannot commit. Internal operation
deadlines, inference checks and PostgreSQL statement/lock timeouts roll back expired
commands before a response; async cancellation alone cannot stop a worker thread.
The explicit bootstrap works once after migrations; its permanent audited system
exception prevents repetition even after revocation. Audited `revoke-role` and
`disable-subject` CLI commands require an administrator, refuse repeated/unsafe
states and recheck authorization before commit. Disabled access is checked on each
private request. No public administrative write endpoint was added.

**Tools and rationale:** FastAPI/Pydantic provide strict request/versioned envelope
contracts; SQLAlchemy/psycopg/Alembic provide real PostgreSQL transactions/migrations;
PyJWT/cryptography/httpx verify RS256 access tokens and bounded trusted JWKS.
MLflow supplies registry identity without training. Typed trusted endpoints permit
exact loopback hosts or an explicitly configured private hostname such as `mlflow`;
scheme/host/port mismatches and redirects are rejected. PEP 508 requirement parsing
checks exact applicable versions and preserves MLflow markers: pywin32 is Windows
only; MLflow's gunicorn dependency is pinned for Linux. Ten direct dependencies and
83 additional lock pins were added; all 20 previous pins are unchanged.

**Meaningful problems and recovery:** unconditional Windows dependencies and naive
lock splitting broke portable verification; marker-aware exact parsing fixes this.
Premature verified tags, non-idempotent registration and separate publication writes
made crashes unsafe; durable identities and retryable publication now converge
without duplicate model/release/audit rows. Forward-only audit checks admitted
orphans; deferred reverse constraints close that gap. Async request cancellation
could leave synchronous work committing after a timeout; deadlines now live inside
the transaction. Real MLflow testing also exposed adapter execution creating
`__pycache__` inside the immutable release: executing a verified temporary byte copy
preserves the inventory. The SDK reports a missing alias with an unexpected error
code; checking the registered model's alias map fixes revocation retries. Windows
service cleanup required approved process-tree execution; disposable backends are
removed after testing. Lesson for viva: a database transaction cannot atomically
commit MLflow metadata and a file, so pending publication must fail closed and
retry the same durable event. See the two repair test modules for fault boundaries.

**Migration reproducibility repair:** the supervisor found that revisions 0001
and 0003 still imported live schema objects; filtering metadata had fixed the
immediate table boundary but future application edits could change historical replay.
Both revisions now own fixed SQL with the existing schema, privileges, seeds and
triggers preserved. Tests block application imports and reproduce the pre-repair
PostgreSQL catalog after replacing live schema objects, for empty-to-head and
0001-to-head paths. Trade-off: intentional DDL duplication; future schema changes
must use a new forward revision. Runtime correctness alone does not prove replay
reproducibility. No new architecture or research change was needed.

**Evidence and limitations:** the final offline suite passed 270 tests, one
live-data test deselected, 63 warnings in 1056.03s; focused migration tests
passed 3 tests and real PostgreSQL integration passed 61. Exact commands and fresh
registry identity are in the handoff. Real PostgreSQL 18.6 tests cover
empty/previous-to-head migrations, runtime
SQL negatives, concurrent sequencing, interrupted publication, ambiguous retries,
deadline rollback and RBAC removal. Clean MLflow integration starts without model
versions, proves fresh version 1 plus duplicate identity and six real import crash
recoveries. Dependency metadata checks cover 102 applicable exact pins on each
Windows/Linux environment; an actual Linux container was not run. Ruff and pip
checks pass. Protected research evidence remains unchanged. Public OIDC integration
and later deployment/resource/accessibility gates remain unverified. No frozen
fitting, holdout records/scoring or research audit rerun occurred; regression fixture
fits are software tests. No frontend/Stage 2 or Git mutation.

## Macro Milestone 4 Stage 0 — Application contract planning (2026-10-11)

**Current state and authority:** Macro Milestones 1–3 are completed.
CURRENT_TASK.md records external Macro Milestone 3 approval at
`ff9dce291f63a6d4241360997ef0aff2308597f9`. Stage 0 is documentation only,
prepared for supervisor review; all application/MLOps components below remain
planned and unimplemented. Earlier milestone/repair sections retain historical
approval states and verification results, not new commands or current authority.
Neither planning completion nor the longer original vision authorizes Stage 1.

### Milestone, rationale and decisions

**What was accomplished:** defined the first product journeys, exact HTTP/role
schemas, transactional database model, trusted artifact/registry lifecycle,
OIDC boundary, React screens, local runtime, failure/security/observability rules
and gated implementation tests/order. ADR 0008 records the major alternatives.
No technology was installed, model registered, source changed or service started.

**Why now:** research already fixes what the model and its explanations mean.
Delivery planning can now use those real interfaces rather than invent new
inference/XAI semantics. Without a contract, frontend feature entry or model
registration might accidentally expose patients, omit calibration or rewrite
frozen evidence. The original platform vision remains in prompt.txt; the first
application is deliberately bounded and does not complete that entire vision.

**Product choice:** public visitors inspect aggregate evidence and the existing
fixed synthetic local case. Engineers request its authenticated prediction and
inspect their history; reviewers record coded evidence-review decisions;
administrators manage approved releases/access through private operator tools
and inspect metadata. Only `case_id=synthetic-discharge-v1` can be submitted;
there is no editable patient form, free text or arbitrary de-identified input.
This sacrifices breadth for a defensible privacy and explanation boundary.
Precomputed-only serving was simpler but would omit inference/audit transaction
demonstration; unrestricted live XAI needs an approved reference and cost/privacy
design that the repository does not supply. The published local explanation
stays precomputed. No clinical recommendation or actionable recourse is added.

**Lifecycle choice:** import the unchanged `model` plus `calibrator` dictionary
into local self-hosted MLflow through a guarded calibrated pyfunc adapter.
`explain.probability` calls the exact fitted preprocessing/base classifier and
the external sigmoid. Registering only a sklearn estimator would serve a different
output. Keep original six model/four audit files and every bound provenance byte;
add a distinct release manifest and package identity. Copy original Windows bytes
without newline conversion; the prior CRLF bug shows why Linux checkout text
cannot replace frozen byte-bound files. Import historical metrics, not a new
evaluation; synthetic probability parity at tolerance `1e-10` is a software gate.
No research reference data or raw source is needed online.

Numeric registry versions and candidate/approved/previous aliases give operators
review and rollback conventions. API pins exact approved version/digest rather
than resolving `latest` per request. Cached verified bytes permit availability
through an MLflow outage; missing cache or DB approval fails closed. Hosted
MLflow was deferred to reduce credentials/cost and laptop-network dependence.
Registry and DB cannot share a local transaction, so both must reconcile before
a release pin becomes deployable. No MLflow record exists yet.

**Persistence choice:** PostgreSQL supplies concurrency, foreign keys and one
transaction for prediction/review, append-only audit and idempotency. Store only
opaque subjects, synthetic case IDs/hashes, model/evidence identities, probability,
coded review/release actions and timestamps; never patient records/tokens/free
notes. Audit-write failure suppresses success. Same idempotency key with same
payload returns the prior result; changed payload conflicts. Review revisions
append new records. Privileges/triggers and a serialized hash chain detect
bounded history tampering; they cannot prove physical immutability against an
owner who rewrites both history and checkpoints. SQLite/JSON would be simpler
but weaker for the intended concurrent review workflow. Other DB types have no
measured need. One PostgreSQL instance uses separate app/MLflow databases/roles.

**Identity and UI choice:** external OIDC/PKCE supplies login and API access JWTs;
API checks signature/issuer/audience/expiry and role plus local entitlement on
every private request. Administrator and reviewer are separate permissions.
No custom production passwords, browser token persistence or arbitrary issuer
URL. React/TypeScript presents API data with an accessible evidence workbench,
saved model context, support/uncertainty captions, no-recourse result and honest
loading/empty/error states. It computes no ML and records no real encounters.
This adds a browser toolchain compared with static documents but supports review
state, version conflicts and audit navigation.

### Planned system/data flow and files to inspect

Existing research dependencies point inward and remain unchanged. Proposed
delivery consists of FastAPI adapters/use cases, new registry/verified-release
adapter, DB persistence and static React UI. Component/request/registration/ER
diagrams, API/RBAC schemas, transactions, artifact lifecycle, threat boundaries
and failure tables are in [ARCHITECTURE.md](ARCHITECTURE.md). Screen/component
map and role journeys are in [PRODUCT_REQUIREMENTS.md](PRODUCT_REQUIREMENTS.md).
Compose volumes/ports/resources, dependency rationale and recovery are in
[DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md). These are specifications,
not source paths that already exist.

Online flow: browser access token → role/case/version validation → server-owned
synthetic features in exact frozen order → complete calibrated probability →
saved explanation reference → transaction rechecks approval/role and commits
prediction + audit + idempotency → response. Review appends a coded decision
and event similarly. Public evidence is projected from verified saved results
without new calculations. Model import verifies originals → copies exact bytes
→ checks package/synthetic parity → registers candidate → records administrator
approval → reconciles alias/DB → pins release → API verifies cache at startup.
No step invokes the model/audit runner or reopens the holdout.

### Why implementation follows this order

Packaging/runtime and byte-preserving import preparation come first because an
unloadable or mismatched model invalidates every later screen. MLflow verification
then establishes registered identity. Schema/migrations precede HTTP writes;
API/RBAC precedes audit persistence so permissions and atomic success are defined.
UI follows stable APIs; Compose follows known service boundaries; full security,
regression, synthetic E2E and documentation gates close the sequence. Stages
1–3 and their definitions of done are in [EXECUTION_PLAN.md](EXECUTION_PLAN.md).
Stage 1 combines backend packaging/registry/migrations/API/RBAC/audit and tests
in that dependency order; activation and successful POSTs wait for verified
atomic release/audit transactions. Stage 2 integrates the React/TypeScript UI;
Stage 3 integrates Compose and completes E2E/security/accessibility/resource and
release gates. Each executable stage still needs its own supervisor-approved task.
Future milestones use 95% implementation/testing and 5% concise documentation,
retaining all required verification and evidence.

**Supervisor contract corrections:** JWT lifetime now has a configurable maximum
validated against the selected OIDC issuer; strict signature/issuer/audience/
expiry/skew/algorithm validation remains, without choosing a public provider.
The initial administrator uses a one-time post-migration operator command with
configured identity and one system-attributed grant/event; subsequent grants
require an active administrator. A permanent unique append-only bootstrap event
prevents repetition after revocation and resolves the first grant's circular FK
dependency. Reviewers see only audit events for authorized predictions/reviews;
administrators inspect release/entitlement/system-wide history and engineers only
their own events. These corrections make the contract executable and limit event
disclosure; all remain planned, not implemented.

### Important problems encountered and learning

**Documentation-state ambiguity:** current README/product/execution/architecture
passages still said Macro Milestone 3 awaited review although the replacement
task explicitly records its approval. Cause: those files recorded the earlier
review state. Update current summaries; preserve dated history and the immutable
model card/ADRs (outside authorized edit paths) with explicit historical context.
Verification uses targeted contradiction searches and diff review. Lesson:
current authorization and historical evidence have different responsibilities.

**Patch context failure:** an initial multi-hunk README patch could not match a
prediction-flow sentence embedded in a longer paragraph. Diff/text inspection
confirmed README had not changed; smaller matching hunks completed the status
edit. No implementation, task content or evidence was affected. Prevention:
inspect whole paragraph boundaries and use small patches; a failed patch is not
verification. No new ML-methodology, model, dependency or environment failure
occurred in this planning milestone. Pinned-package/image compatibility remains
a future gate, not a failed test invented here.

### Concepts learned through this planning task

**Model registration versus training:** registration catalogs already fitted
bytes with version/approval identity. Used in the proposed MLflow import; matters
because adding MLOps must not spend the holdout again. Explain historical metrics,
numeric versions, mutable aliases versus immutable hashes and rollback pins.

**Atomic audit and idempotency:** a request either commits result/event/key
together or returns no successful result; an uncertain response can be retried
with its original key. Used in planned POST transactions. Explain uniqueness
under concurrent retries, ambiguous commit, changed-payload conflict and why
idempotency is not implemented by merely caching responses in process memory.

**OIDC and authorization:** an identity provider proves a token's issuer/subject;
application permissions additionally restrict role, entitlement and resource.
Used at FastAPI boundary. Explain access token versus ID token, JWKS/expiry,
PKCE, 401 versus 403, and why a hidden frontend button cannot secure an API.

**Append-only versus tamper-evident:** database privileges restrict ordinary edits;
hash chains expose changed history against a trusted anchor, but an owner can
rewrite storage. Used in planned audit events. Explain canonical bytes, concurrent
chain locking, checkpoint trust and why neither is physical WORM.

### Project defence and semester viva preparation

Why fixed synthetic input? Only that case has published local evidence and known
privacy/method semantics; arbitrary records need separately reviewed boundaries.
Why include the calibrator? The displayed probability is sigmoid of clipped
base-probability logit, not base `predict_proba` alone. Why not always call MLflow?
An exact reviewed local pin keeps requests stable and lets a registry outage
block promotion rather than change the model. Why audit before response? A
successful result without its durable trace defeats the project's purpose.
Why not Kafka/Redis/Kubernetes? No measured asynchronous, shared-cache or
orchestration requirement exists. What remains unproved? All application runtime,
security, accessibility, resource and latency behaviour until implementation tests.

**Basic:** What is a model version? An immutable registry identity for a package.
What does RBAC restrict? Which authenticated role can perform each operation.
**Intermediate:** What if commit succeeded but the response was lost? Retry the
same key and retrieve the stored event/result. Why keep source hashes and release
hashes separate? One identifies frozen research; the other identifies its delivery
packaging. **Difficult:** Can registry/DB promotion be atomic? No; reconcile and
publish a pin only after agreement. Can hashes alone authorize pickle loading?
No; the expected digest and code origin must already be trusted. Can a DB owner
forge the chain? Yes without an external trusted checkpoint.

**Resume evidence and limitations:** Stage 0 adds documentation only, one ADR and
a three-stage implementation contract after Stage 0; there is no new endpoint, registered
model, migration, UI, deployment, test count, measured latency or ML experiment.
Existing 122-test evidence is historical, not rerun here. Research limitations
remain unchanged. Provider/host/region/real-user retention and clinical validation
remain future work; package/image compatibility and laptop budgets require later
verification. No production drift detector is implemented. Required Stage 0
checks and exact repository evidence are recorded in SUPERVISOR_HANDOFF.md.
Next step is supervisor review of this contract; no implementation begins here.

**Initial Stage 0 verification (before supervisor repair):** `git diff --check` exited 0. Read-only link/fence
checks exited 0 across eight changed/new documents: 64 local links resolved,
no unbalanced fences; 14 Mermaid blocks counted but not rendered. Targeted
contradiction searches and current/historical context review passed. Snapshot
comparison found all 87 protected files unchanged, including user-owned task
and ten frozen model/audit files. Branch remains main, HEAD equals origin/main
at `ff9dce291f63a6d4241360997ef0aff2308597f9`, stash unchanged and staged file
list empty. Only seven authorized docs, one new ADR and user-owned CURRENT_TASK
appear in status; the handoff records the exact inventory. No implementation
tests, training, inference, holdout access, artifact writes, commit or push occurred.

## Historical completed milestone and repair records

Review/authorization statements below preserve the state at the recorded dates.
Current status is the Stage 0 section above and current-state overview below.

## Macro Milestone 3 final reproducibility repair (2026-10-11)

**Symptom and root cause:** external review passed the saved audit's technical,
chronology, metric, binding and privacy checks, but the split-lock byte hash
depended on Git checkout line endings. The frozen Windows working copy used CRLF;
the committed Git blob used LF. JSON parsers treat those whitespace differences
equally, while SHA-256 hashes every byte, so a default LF checkout would fail the
existing audit binding despite having identical split meaning.

**Independent proof:** Python `subprocess.check_output(['git', 'show',
'HEAD:configs/splits/healthcare_uci296_v1.lock.json'])` read committed bytes without
PowerShell text conversion. Its SHA-256 was
`9543d65d1dc4fc2ef3e3f6a4f43fa88828550241a78291876d289d3e83755ecd`.
Converting LF to CRLF in memory reproduced the frozen working-copy hash exactly:
`a3ca2af19215bcf965afecaa75a1c6ec2912f3cf832f2aaec82562ec7855446d`.
The committed, converted and existing working-copy JSON objects were equal.
Their `membership_sha256` remained
`6879c9e652887c4a8b59797dd2260ad79795958fb3eebff1b22c3fe33b075316`.
No split content, membership, model, threshold or result changed.

**Resolution and alternatives:** repository-root `.gitattributes` now contains
only `configs/splits/healthcare_uci296_v1.lock.json text eol=crlf`. This makes the
one bound file's checkout representation explicit across platforms while Git
retains its normalized LF blob. No repository-wide CRLF rule was added and no
existing split bytes were rewritten. Rewriting frozen protocol/manifests/hashes
was rejected because it would alter already reviewed evidence rather than fix
checkout reproducibility. No code/configuration/test or experiment migration
occurred; the frozen model and all four audit records remain untouched.

**Prevention and learning:** future structured-artifact protocols should define
canonical JSON serialization and semantic hashes (explicit ordering, encoding,
numeric and whitespace rules), alongside file-byte hashes when exact storage
integrity is required. This is a recommendation, not a change to the current
protocol. Viva answer: byte identity and semantic identity differ; preserve a
frozen byte-bound experiment and make its required checkout representation
explicit instead of silently changing its evidence.

**Documentation consistency:** README, this report, PRODUCT_REQUIREMENTS,
DEPLOYMENT_ARCHITECTURE, ARCHITECTURE, EXECUTION_PLAN and SUPERVISOR_HANDOFF agree
that Macro Milestones 1–2 are completed and Macro Milestone 3 is implemented,
pending external review. Historical foundation/credit states are labelled.
Application, MLOps and deployment remain unimplemented. No additional current-state
contradiction required correction. Final repair checks and the portable complete
review patch are recorded in SUPERVISOR_HANDOFF.md. This repair authorizes no
Macro Milestone 4, audit/model run or new holdout access.

**Final verification:** `git check-attr text eol --
configs/splits/healthcare_uci296_v1.lock.json` returned `text: set`, `eol: crlf`.
Read-only `audit inspect` exited 0 with `status: verified`. Pip check exited 0
with no broken requirements; Ruff lint exited 0 with all checks passed; Ruff
format check exited 0 with 69 files already formatted. Complete offline pytest
with cache disabled and ignored `data/processed/pytest-m3-final-repro-offline`
storage exited 0: **122 passed, 1 deselected, 25 existing credit Logistic Regression
deprecation warnings in 33.50s**. `git diff --check` passed. Four audit file hashes
matched the frozen values before/after, as did all 79 protected files in this
repair's snapshot, including the unchanged model and split bytes. No real-data
test or prediction was run. The only index change was authorized `git add -N --
.gitattributes`; a sandbox index-lock permission failure was resolved through
command escalation. `git diff --cached --name-only` was empty: no contents staged.
The complete working-tree review patch is exported outside the repository at
`%TEMP%\aletheia-macro3-final-review.patch`, including existing milestone changes,
both product/deployment documentation repairs and the narrow attributes rule.

## Macro Milestone 3 external-review documentation repair (2026-10-11)

**Status and boundary:** Macro Milestones 1 and 2 are completed; Macro Milestone
3 is implemented and locally verified, pending external review. This repair
changes current-state documentation only and authorizes no Macro Milestone 4.
The implementation record below describes the earlier completed audit, not
commands repeated during this repair.

**Problem and recovery:** product requirements and deployment design still
presented healthcare modelling/calibration/XAI/stability/subgroup methods as
planned. README understated the engineer workflow, and foundation/credit report
passages used historical "current" or "future" language without sufficiently
local labels. The documents had evolved at different milestones, so readers
could mistake an old state for today's implementation. Reconciled README,
PRODUCT_REQUIREMENTS, DEPLOYMENT_ARCHITECTURE, ARCHITECTURE, EXECUTION_PLAN and
this report against the existing model card, ADRs and saved audit bindings.
Retained earlier decisions/results with explicit historical labels. Feasibility
assessment is implemented; actionable recourse/search is not. Application/API,
UI, databases, MLflow, authentication, deployment, CI/CD, monitoring, LLM/RAG and
later operations remain unimplemented. No scientific method, evidence or metric
was changed. A context-sensitive documentation patch failed; inspecting the
actual text before smaller follow-up patches preserved already applied edits.
Lesson/viva answer: distinguish a historical design decision, current verified
implementation and future delivery plan; documentation consistency is part of
evidence integrity, and a failed edit must be checked before retrying.

**Verification in this repair:** branch `main`, HEAD and origin/main remained
`49a1a8c7fdc5cbfb197b7533d3d40a8e9aa6f2eb`. The initial file inventory matched
the reported Macro Milestone 3 changes, including the user-owned CURRENT_TASK
modification. The credit WIP stash was preserved. Read-only `audit inspect`
returned `verified`, checking saved artifact hashes, bindings, inventory and
publication schema without patient-data loading or new predictions. Pip check
found no broken requirements; Ruff lint passed; Ruff format check reported 69
files already formatted. Complete offline pytest with cache disabled and ignored
`data/processed/pytest-m3-review-repair-offline` temporary storage passed:
**122 passed, 1 deselected, 25 existing credit L2-deprecation warnings in 33.94s**.
The live-data test was excluded. No audit freeze/run, model selection, retraining
or new holdout access occurred. Final whitespace, protected-file, ZIP and status
evidence is recorded in SUPERVISOR_HANDOFF.md and the external-review bundle.

**Review delivery:** the portable bundle at
`%TEMP%\aletheia-macro3-review-evidence.zip` contains the four existing aggregate
audit records and a plain-text verification file. It excludes raw data, fitted
joblib, real patient-level records, secrets and caches. This provides reviewable
saved evidence without regenerating a claimed experiment. Remaining statistical,
clinical, privacy and local-filesystem limitations are unchanged. External review
is still required; no later milestone, commit or push is authorized.

Bundle verification confirmed exactly the four copied audit files and
VERIFICATION.txt, all copy hashes matching, and identical Git status before/after
creation. All 74 protected files matched the pre-repair snapshot and the stash
object remained unchanged. The first PowerShell packaging attempt failed before
creating the ZIP because the compression assembly was not loaded. Loading both
System.IO.Compression and System.IO.Compression.FileSystem explicitly resolved
the runtime issue; archive inventory/copy hash checks passed. This was a tooling
failure, not an audit rerun or evidence failure. Lesson: load .NET types explicitly
in Windows PowerShell and verify portable copies by bytes rather than filenames.

## Macro Milestone 3 — Explainability and responsible audit (2026-10-11)

This is the current healthcare audit record. Older milestone/credit sections
preserve the state at those earlier times; their future-work statements are
historical. Starting `main`, `HEAD` and `origin/main` all identified
`49a1a8c7fdc5cbfb197b7533d3d40a8e9aa6f2eb`; only user-owned CURRENT_TASK.md was
modified, and the existing credit WIP stash was preserved. No Git mutation is
authorized. The model, 13 predictors, calibration, patient split, thresholds,
source and earlier measurements remain frozen.

### Purpose, sequencing and data flow

The model milestone answered how a bounded model comparison ranked and
calibrated risk. This milestone asks what influences the selected probability,
how explanations respond to a small recording change, and what error patterns
are observed across supported groups. A probability alone cannot answer those
questions. Audit results cannot select or improve the model after its holdout
has been evaluated. We inspected the original source/roles/configs, complete
healthcare tests, saved nested CV, selection, fitted manifest and prior holdout
record, then verified their hashes and selection bindings before implementation.

The order is: choose and test versioned methodology using synthetic data →
exclusively freeze config/code/test/model/data/split/software bindings → verify
source bytes and actual patient membership → sample training references/cases →
explain the complete calibrated callable → measure recording sensitivity →
claim one post-selection holdout subgroup access → predict once and compute
guarded aggregate subgroup metrics → prove original bindings unchanged →
validate the privacy schema → exclusively publish results/manifest → inspect
saved evidence. Counterfactual feasibility is assessed under fixed discharge
semantics. No estimator, imputer, encoder or calibrator is fitted by this flow.
The full source loader and split verifier necessarily inspect source structure
and already-frozen class counts; the exclusive audit claim guards new holdout
predictions and subgroup outcome calculations.

### Components and code ownership

| Component and important functions | Purpose, callers and dependencies | Failure boundary and evidence |
|---|---|---|
| `explain.py`: `probability`, `feature_mapping`, `attributions`, `local_explanation`, `global_explanation` | Audit orchestrator calls the original fitted pipeline plus `sigmoid_predict`; fitted encoder categories map transformed columns to source fields; paired paths provide signed probability contributions | Exact predictor order, class orientation, finite probability, lineage and additive reconstruction; calibrated-versus-base, additive toy, mapping and seeded tests |
| `stability.py`: `perturb`, `compare`, `analyze_stability` | Orchestrator samples training cases, perturbs two recording counts and calls the same explainer with identical paths; SciPy rank correlation and NumPy summaries | Bounded nonnegative integers, immutable remaining fields, explicit undefined rank/distance, threshold crossings and unchanged cases; known-metric and perturbation tests |
| `fairness.py`: `subgroup_metrics`, `subgroup_intervals`, `audit_subgroups` | Guarded orchestrator supplies one aligned holdout probability Series, separate audit view, outcomes and patient groups | Exact index alignment, supported original categories, minimum support, null undefined values, patient resampling and suppressed small counts; metric/support/alignment/cluster tests |
| `counterfactual.py`: `assess`, `validate_scenario`, `scenario_result` | Orchestrator publishes fixed feasibility assessment; tests attempt prohibited changes | All care/history and demographics/IDs immutable, targets/excluded fields forbidden, no invented cost/search or treatment change; every-source-field refusal and no-result tests |
| `audit.py`: `bindings`, `verify_model`, `freeze`, `verified_protocol`, `claim_holdout`, `validate_publication`, `run`, `inspect` | Research CLI composes modules, reuses foundation/experiment contracts, and exclusively writes ignored local evidence | Model/source/split/config/software checks, immutable claim/overwrite refusal, persisted-byte hashing, allowlisted aggregate schema and fixed synthetic values; synthetic integration and tamper/privacy tests |

Configuration is `configs/audit/healthcare_audit_v1.toml`; tests are
`tests/healthcare/test_audit.py` and `test_audit_integration.py`. Architecture
and alternatives are recorded in ADR 0007. No new dependency or hosted service
is installed. Existing pandas/NumPy/scikit-learn/SciPy and its already locked
threadpoolctl runtime are used, with inference threads limited to one.

### What the explanation means

The base Histogram Gradient Boosting pipeline produces a raw positive-class
probability `p`. The external calibration layer computes
`sigmoid(a * logit(clip(p, 1e-6, 1-1e-6)) + b)`. Calibration parameters `a` and
`b` convert scores into probabilities; they are not clinical feature effects.
Our attributions explain this entire composite probability. We do not present
base tree scores as calibrated risk. The score remains an observed historical
30-day readmission estimate, not an individual's guaranteed outcome.

There are 13 players, one per original field. The eight quantitative fields
mean hospital days, laboratory procedure count, procedure count, medication
count, prior outpatient/emergency/inpatient utilization, and diagnosis count.
The five categorical fields are admission type/source, maximum glucose serum
category, A1C category and diabetes medication indicator. Numeric administrative
codes are labels: the synthetic example's admission type `1` is Emergency and
source `1` is Physician Referral in the verified UCI mapping. Fitted
imputation/scaling and one-hot encoding produce 43 estimator columns. A whole
categorical field is replaced as a unit before preprocessing, preventing
impossible one-hot combinations such as two admission types at once. Fitted
encoder categories, not string splitting on underscores, provide lineage.
Identifiers, outcomes, disposition, demographics and excluded care fields
never enter this matrix.

For each case, 32 random orders and their reverses start with a sampled training
reference, then insert the case's fields one at a time. Each model-output
increment is assigned to the field just inserted. Averaging these increments
gives a Monte Carlo estimate of interventional Shapley contributions. A positive
contribution raises the model probability relative to the reference, while a
negative contribution lowers it. Every path telescopes, so contributions plus
the average sampled reference probability reconstruct the case's calibrated
probability. This arithmetic identity is tested; it does not prove causal
faithfulness or that the finite estimate equals exact Shapley values.

The 64-row background is sampled from training encounters with seed 3101.
One reference is sampled per paired path; the baseline is the mean probability
over those path references, not the prediction at mean clinical values and not
necessarily the exact mean of all 64 rows. Seed 3105 fixes local paths. Global
samples use seeds 3102/3103/3104, 128 encounters each, and corresponding path
seeds `3105 + sample_seed`. Global importance is mean absolute probability
contribution per field, averaged across three repeats. Repeat min/max capture
both case and path variation; three repeats are not a confidence interval.
This is training-population descriptive importance, not held-out generalization.

Local explanations include model/dataset/split identity, calibrated probability,
method/output/baseline, original feature values, signed contributions and
educational/non-causal limitations. They can explain an individual input in
memory. Publication is restricted to the protocol-fixed synthetic case; real
patient records, row keys and unrestricted patient predictions are omitted.
Using a public historical dataset does not justify publishing its patients.

SHAP's model-agnostic permutation approach inspired the transparent sampled
estimator, but the SHAP package was not installed. Tree-specific explanations
would need a separate treatment of external calibration. Global permutation
importance is an alternative measure of score degradation and would not supply
signed local additive contributions. LIME would require surrogate-fidelity
checks; exact coalition enumeration has exponential cost. The chosen approach
trades library optimizations and exactness for readable, tested calculations
on existing dependencies. Marginal replacements can still combine correlated
fields unrealistically; a clinically justified conditional model is absent.

### Stability methodology and interpretation

Sixteen training cases use seed 3201. Five perturbations per case use seed 3202
and adjust lab/procedure counts independently by +/-1 within training-observed
integer bounds. These are small plausible recording corrections, with all other
fields fixed. Schema plausibility is not clinician validation or an actionable
intervention. Identical reference/path seeds before and after isolate input
sensitivity from newly drawn explanation noise.

Top-3 overlap counts common influential fields divided by three, with ties
resolved in frozen field order. Spearman correlation compares ranks of absolute
contributions; constant vectors yield null. Normalized L1 divides absolute
contribution changes by the original attribution L1; zero norms yield null.
Prediction changes are measured separately, and comparisons crossing the
unchanged descriptive 0.5 cutoff are summarized separately. Overlap below 2/3
or normalized L1 above 0.25 is a predeclared descriptive flag, not a clinical
stability pass/fail standard. Bounds may produce unchanged cases, which are
counted. Limited fields, small sample and fixed paths cannot prove robustness.

### Fairness methodology and metric meanings

Race, gender and original ten age bands remain audit-only. Their source
categories, missing race and unknown gender are retained; no proxy identity,
intersections or arbitrary age bins are introduced. Index equality and unique
indices preserve alignment between predictions, outcomes, patients and the
separate audit view. Inclusion requires 200 encounters, 100 patients, 20
positive and 20 negative encounters. Unsupported groups have no metrics;
counts below 20 are displayed as `<20` rather than exact values.

Prevalence is the observed outcome fraction. AP summarizes positive ranking
and changes with prevalence; ROC-AUC measures two-class ranking. Brier is mean
squared probability error, not a complete calibration certificate. At 0.5,
recall is the fraction of positives flagged, specificity the fraction of
negatives unflagged, FPR the fraction of negatives flagged, FNR the fraction of
positives missed, and positive prediction rate the fraction of all group cases
flagged. Undefined AP/recall for no positives, ROC-AUC for one class and
specificity for no negatives are null. Support gating prevents such groups
from receiving headline performance estimates.

Two hundred draws with seed 3301 resample patients within each supported group,
keeping that patient's subgroup encounters together. The percentile 95%
intervals are marginal within-group uncertainty; undefined draws are omitted
per metric and counted. They are not uncertainty intervals for paired group
differences, adjusted multiple-comparison tests, clinical uncertainty, evidence
of discrimination or an ethical/legal fairness certificate. Historical care,
readmission ascertainment, missing race and sparse groups limit comparisons.
The original threshold's extremely low recall must remain visible in every
subgroup interpretation; no threshold is tuned against these outcomes.

### Counterfactual feasibility and worked no-result example

A model counterfactual would be a feasible changed input that changes the fitted
model's class. At discharge, prior utilization and administered care are already
historical. Changing identifiers, demographics or outcomes is prohibited;
changing medications/treatment would require clinical review, a time horizon,
joint feasibility and an intervention model that this dataset does not supply.
There are therefore zero mutable or conditionally mutable fields. All predictor
and demographic/identifier fields are immutable; excluded/target fields remain
forbidden. A distance/cost function is explicitly undefined because there is no
admissible intervention space. Search is not performed and no candidate is
fabricated. Tests reject changes to every predictor, including invalid categories.

Worked example: the synthetic case has one prior inpatient visit and twelve
medications. Reducing either value rewrites history or care rather than providing
defensible discharge recourse. Both proposals are refused; the result is
`no_feasible_scenario`. Recording-sensitivity perturbations in the stability
study do not make historical care mutable for a clinical recommendation.
Clinical counterfactual search may be reconsidered only with reviewed evidence.

### Important problems encountered and recovery

**Persisted JSON hash mismatch.** Symptom: all nine initial synthetic audit
integration setups failed `audit manifest binding mismatch`; 20 unit tests
passed. Investigation compared publication and inspection hash paths. Root
cause: existing `experiment.write_once` returns the digest of LF text before
Windows translates it to CRLF. Using that return value for the new result
manifest therefore disagreed with persisted bytes. The original experiment
records were not changed. Rejected approach: weaken the hash guard or replace
prior evidence. Resolution: the new audit hashes the persisted result file
after exclusive writing. The real synthetic publication/inspection path and
artifact-tamper test pass. Prevention: compute evidence hashes from saved bytes,
and test the writer-to-reader flow on the actual platform. Interview explanation:
serialization is a byte contract; equivalent JSON content can have different
file hashes when newline handling differs. No real holdout claim existed.

**Tooling and documentation recovery.** Creating the protocol initially failed
because `configs/audit` did not exist. Status showed no changes; creation of
only that authorized directory allowed the patch. Initial Ruff findings were
long literals and import/fixture formatting, resolved before tests/freezing.
A later multi-file documentation patch reported a context failure even though
README changes were visible. Inspection of current text/diff preserved those
valid changes, then a smaller patch updated the remaining documents. Do not
assume a reported patch failure implies no changes; inspect state before retry.
An early multiline Python inspection transported through PowerShell produced
no output, so it was not counted as successful verification. A readable `--%`
command returned explicit successful binding checks before implementation.
These tooling issues changed no data, method, frozen model or empirical result.

### Concepts learned, interview defence and viva

**Interventional Shapley sampling:** share probability change across fields by
averaging their increments in many insertion orders. Used in `attributions` to
explain the full callable without a tree/calibration mismatch. Explain the
reference distribution, paired paths, additivity, finite sampling and correlated
hybrid limitations. Global mean absolute contribution describes a population;
signed local contributions describe one prediction relative to a reference.

**Explanation versus calibration:** calibrating a score changes magnitudes,
so base-estimator contributions cannot be relabelled probability contributions.
Used in `probability` and the manifest's separate calibration metadata. Explain
the logit/sigmoid composition and why coefficients `a,b` are not feature effects.

**Conditional subgroup measurement:** an aggregate model score can conceal
group-specific prevalence and errors. Used in `audit_subgroups` with support,
alignment and patient uncertainty. Explain undefined denominators, AP/prevalence,
threshold effects, clustering and why removing race from inputs cannot prove
fairness or remove proxies.

**Explainability stability:** local importance can change with small input
corrections even if a probability changes little. Used in `analyze_stability`.
Explain top-k ties, undefined ranks, normalized L1, fixed-path comparisons and
why a descriptive reference flag is not a universal clinical standard.

**Recourse feasibility:** valid categories alone do not make a change an
available intervention. Used in `assess` and `validate_scenario`. Explain
observation time, history, mutable versus immutable fields, missing clinical
constraints and why no-result evidence can be the defensible outcome.

**Project defence:** Why did you avoid tree-only SHAP? The selected output is
an externally calibrated probability; we explain the complete callable. Does
additivity prove causality? No, it checks reconstruction of a model output under
the chosen reference. Why publish synthetic locals? Real patient values are
unnecessary for demonstrating the explanation structure. Why use a second
holdout claim? It registers one new post-selection subgroup audit, preserves
the original model evaluation and prevents accidental audit retries. Why no
counterfactual search? No clinical intervention set is defensible at discharge.
What would you improve? Pre-register larger independent samples, clinically
review recording/joint plausibility, and obtain contemporary external evidence.

**Semester viva — Basic:** What is a global/local explanation? A global summary
describes typical contribution magnitudes; a local one assigns signed change
for a case against a baseline. What is FNR? One minus recall. What is the
positive class? `<30` readmission. **Intermediate:** Why group one-hot fields?
They are one source variable, and independent dummy switching can violate valid
encoding. Why fix paths in stability? To reduce new sampling noise. Why suppress
small subgroup results? Estimates and privacy are weak at sparse support.
**Difficult:** What does marginal masking assume? It replaces fields from an
empirical training reference, without modelling conditional clinical dependence.
Why is a zero-norm distance undefined? There is no original magnitude to divide
by. Why are marginal subgroup intervals not a disparity significance test?
They do not estimate the paired difference or adjust multiple comparisons.
Can an exclusive filesystem claim prevent a malicious administrator? No; stronger
storage/governance is outside the current local research boundary.

### Empirical results and completion evidence

Implemented and verified locally; external supervisor review is pending. The
protocol was frozen at `2026-10-11T05:15:09.910670+00:00`, before outcomes. The
completed manifest timestamp is `2026-10-11T05:17:30.784462+00:00`. The audit
claimed one post-selection subgroup access to 19,535 encounters/13,812 patients.
The original model holdout evaluation and claim were preserved; there was no
model reselection, fitting, calibration fitting or threshold tuning.

Global mean absolute contributions are in calibrated probability units, not
percentages of causal influence. Prior inpatient utilization was largest in
all three repeats; its mean 0.032975 is approximately 3.30 probability percentage
points. The baseline probabilities for the three repeats were 0.107816,
0.110666 and 0.105843. Results reflect the frozen model and sampled reference.

| Source field | Mean absolute contribution | Three-repeat range |
|---|---:|---:|
| Prior inpatient visits | 0.032975 | 0.028624–0.036702 |
| Time in hospital | 0.007839 | 0.007793–0.007901 |
| Diagnosis count | 0.005413 | 0.005119–0.005659 |
| Diabetes medication indicator | 0.003951 | 0.003747–0.004136 |
| Medication count | 0.003593 | 0.003352–0.004053 |
| Prior emergency visits | 0.002866 | 0.002491–0.003075 |
| A1C result | 0.002245 | 0.001861–0.002634 |
| Lab procedure count | 0.001953 | 0.001896–0.002046 |
| Procedure count | 0.001707 | 0.001665–0.001738 |
| Prior outpatient visits | 0.001074 | 0.000840–0.001203 |
| Admission type | 0.000962 | 0.000914–0.001024 |
| Admission source | 0.000543 | 0.000395–0.000763 |
| Maximum glucose serum category | 0.000388 | 0.000115–0.000625 |

The fixed synthetic local probability was 0.127821691881, against baseline
0.108475507333. The signed contributions sum to 0.019346184548. Largest positive
contributions were prior inpatient visits +0.016184960386 and procedure count
+0.005361225860; diagnosis count contributed -0.008901138329. The complete local
record contains all 13 original synthetic values and contributions. These are
reference-dependent model associations, not patient evidence or care advice.
The frozen calibration coefficients are `a=1.046740791844`,
`b=0.093210594239`; these are the fitted mapping parameters, distinct from the
Milestone 2 held-out diagnostic calibration regression's slope/intercept.

Eighty stability comparisons had mean top-3 overlap 0.95 (minimum 1/3), mean
absolute-attribution Spearman correlation 0.945536 (minimum 0.631868), and mean
normalized L1 change 0.077479 (maximum 0.516299). Mean absolute probability change
was 0.002753, maximum 0.033485. Three comparisons fell below overlap 2/3 and five
exceeded normalized L1 0.25. There were zero 0.5 boundary crossings, zero wholly
unchanged perturbations and zero undefined comparison metrics. Observed bounds
were labs 1–132 and procedures 0–6. Good average overlap therefore coexists with
material local attribution changes; no universal stability conclusion follows.
The crossed-class summary is null because there were no such comparisons.

Fifteen of 21 predeclared subgroup slots met support: five race categories
including missing, two genders and eight source age bands. Asian, unknown/missing
gender, the two youngest age bands and missing age were withheld. Missing race
comprised 410 encounters, including 40 positives. Counts below 20 are suppressed.
All supported metrics had 200 valid bootstrap replicates and zero undefined
replicates. The following values are descriptive subgroup point estimates; the
complete result retains nine metrics and 95% intervals for every supported group.

| Attribute/group | Encounters | Patients | Positives | Prevalence | AP | ROC-AUC | Brier | Recall at 0.5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Race/AfricanAmerican | 3,631 | 2,500 | 398 | 0.109612 | 0.221488 | 0.642704 | 0.093631 | 0.015075 |
| Race/Caucasian | 14,685 | 10,362 | 1,709 | 0.116377 | 0.195458 | 0.635365 | 0.099950 | 0.003511 |
| Race/Hispanic | 404 | 301 | 47 | 0.116337 | 0.341211 | 0.698820 | 0.094700 | 0 |
| Race/Other | 280 | 233 | 28 | 0.100000 | 0.223538 | 0.653132 | 0.086358 | 0 |
| Race/Missing | 410 | 362 | 40 | 0.097561 | 0.198620 | 0.605000 | 0.085954 | 0 |
| Gender/Female | 10,343 | 7,255 | 1,177 | 0.113797 | 0.196189 | 0.629115 | 0.097973 | 0.007647 |
| Gender/Male | 9,192 | 6,557 | 1,063 | 0.115644 | 0.210509 | 0.650909 | 0.098574 | 0.002822 |
| Age/[20-30) | 292 | 224 | 29 | 0.099315 | 0.240104 | 0.715353 | 0.084597 | 0 |
| Age/[30-40) | 738 | 534 | 87 | 0.117886 | 0.367450 | 0.795981 | 0.091777 | 0.068966 |
| Age/[40-50) | 1,835 | 1,336 | 193 | 0.105177 | 0.245566 | 0.668772 | 0.088911 | 0.025907 |
| Age/[50-60) | 3,386 | 2,501 | 354 | 0.104548 | 0.194858 | 0.652099 | 0.090417 | 0 |
| Age/[60-70) | 4,426 | 3,166 | 510 | 0.115228 | 0.200782 | 0.636677 | 0.098762 | 0 |
| Age/[70-80) | 4,871 | 3,569 | 547 | 0.112297 | 0.179552 | 0.609731 | 0.097658 | 0.001828 |
| Age/[80-90) | 3,289 | 2,294 | 432 | 0.131347 | 0.190385 | 0.600354 | 0.112380 | 0 |
| Age/[90-100) | 527 | 385 | 80 | 0.151803 | 0.207096 | 0.587109 | 0.128457 | 0 |

Observed differences include gender ROC-AUC 0.629115 versus 0.650909, and age
ROC-AUC 0.795981 for [30-40) versus 0.587109 for [90-100). The corresponding
95% patient intervals are Female [0.608449, 0.648161], Male [0.632397, 0.673503],
[30-40) [0.729181, 0.849195], and [90-100) [0.514392, 0.660598]. These intervals
describe separate group estimates; no adjusted statistical disparity test or
causal discrimination claim was implemented. Hispanic AP 0.341211 has a broad
interval [0.197289, 0.478389] with only 47 positives. Non-overlapping or
overlapping marginal intervals alone are not the registered disparity test.

At 0.5, supported-group recall ranges from zero to 0.068966, specificity from
0.993856 to 1, FPR from zero to 0.006144, FNR from 0.931034 to 1, and positive
prediction rate from zero to 0.013550. Many groups have zero alerts and recall.
The audit reinforces the existing threshold limitation, not threshold selection.
Bootstrap intervals of [0,0] for zero observed events are an empirical-bootstrap
limitation: resampling cannot create an unseen event and does not prove true
population error is zero. No group is described as unbiased or certified fair.

The recourse result is `no_defensible_recourse` / `no_feasible_scenario`, with
no search and no candidates. This implements the authorized feasibility branch;
clinically actionable counterfactual generation is not an accomplishment.

Evidence lives only in ignored `artifacts/healthcare-audit-v1`, containing the
four intended files. Full SHA-256 identities:

- Model: `8c3a99dd8dfe20d2a3a0a721637b4be500ee1b32843f7cefc3af265f07262f7a`.
- Selection: `85db5e79faacc80d9818b235c4e8338be0aeb10fbcf89da2f3bc56e87172e9a7`.
- Split membership: `6879c9e652887c4a8b59797dd2260ad79795958fb3eebff1b22c3fe33b075316`.
- Audit configuration bytes: `36c0a12c710a2cf04ce650a780d165d72eea281479db3aa34ae7433f96b8804c`.
- Canonical protocol: `fae9acd4c95da774faa1e20a84129146faeeeef1ac866d809ac95df77a7aa04f`.
- Protocol file: `2f5ed6f4427ee64c145a8e72a1f89c398e1303ae12a8386ecf2ff28e71b49cb2`.
- Results file: `2d073fa0d0bbbd4debfdf445cd80ec478fef0f7098c7ef356dbb3edd28894ea8`.
- Audit claim: `8844e211c51259ffee18e81514f4aac6974ca1e7c1d867054a258de477a0e9fd`.
- Manifest: `3fbbf27c0d3489768bc457f21cc5e1ec7b4f2326c7b5b5a35b3d54ab20e12b01`.

The manifest binds source/feature/split/config/code/test/model-run file hashes,
software, seeds, timestamps, method metadata, limitations and explicit access.
Privacy inspection uses the strict publication schema and matching synthetic
values; raw records, identifying values and real prediction/attribution vectors
are absent. Aggregate release is not formal differential privacy. Local file
immutability prevents accidental overwrites; it does not prevent malicious deletion.

**Verification and resume evidence.** Python 3.12.10 pip check and Ruff lint
passed; formatting reports 69 files already formatted. New unit tests: 25 passed
in 2.48s; new integration tests: 10 passed in 9.06s; all healthcare tests: 56
passed in 13.29s. Complete offline suite: 122 passed, 1 live test deselected,
25 existing credit L2-deprecation warnings in 17.46s. One seeded empirical audit
completed; it checked original frozen bindings again and inspected saved
manifest/privacy successfully. No clinical latency or deployment was measured.
There is one sampled attribution method serving global and local explanations,
80 recording comparisons, 15 supported subgroup estimates and one feasibility
assessment; do not claim multiple XAI techniques or clinical recourse.

**Remaining limits and next step.** The sample/reference and marginal hybrids
restrict XAI; the recording probe has no clinician validation; sparse historical
groups and empirical-bootstrap zero-event intervals restrict fairness evidence;
recourse lacks a feasible intervention space. The next step is external
supervisor review of this milestone. No later milestone, similar-case retrieval,
application, LLM/RAG, registry, database or deployment was begun. No commit/push
was made; review authorization is not inferred from completion.

## Macro Milestone 2 — Patient-safe healthcare modelling (2026-10-06)

**Historical milestone record:** the model/results below remain valid frozen
evidence. Statements about future XAI/audits describe the end of Macro Milestone
2; those methods are now implemented in Macro Milestone 3 above.

**Scope and order.** After the UCI 296 identity, target, 99,343-encounter
eligible cohort, 13-field feature policy and patient split were frozen in
Milestone 1, this milestone adds a healthcare research experiment. Source
validation must come before modelling because a strong score on an invalid
cohort or a patient-leaking split would be misleading. The older credit-first
and Milestone 1 text below remains historical; statements there that say
healthcare modelling is future work describe the state at that earlier time.
The complete numerical record is stored in ignored immutable local manifests
and summarized in the model card and supervisor handoff.

**Component path and data flow.** `configs/experiments/healthcare_model_v1.toml`
freezes identities, grids, seeds, metrics and selection. `foundation.py` verifies
source bytes and split membership; `modeling.py` constructs only the 13 approved
predictors, fold-local pipelines, bounded candidates and verified group folds;
`evaluation.py` computes probability/classification metrics, calibration data
and patient-cluster intervals; `experiment.py` orchestrates nested CV, repeat,
selection, final fit, artifact validation and one-time holdout evaluation. The
CLI `python -m aletheia.domains.healthcare model` calls that orchestration.
The `tests/healthcare/test_modeling.py` and `test_experiment.py` files exercise
group isolation, feature refusal, dense-memory refusal, seeded bootstrap,
immutable records, checksum/version refusal and a previously claimed holdout.

**Predictors and preprocessing.** The eight quantitative inputs are length of
hospital stay, lab procedure count, procedure count, medication count, prior
outpatient visits, emergency visits, inpatient visits and diagnosis count.
They are converted from validated nonnegative source integer strings, median
imputed and standardized using the fold's training rows. The five categorical
inputs are admission type code, admission source code, maximum glucose serum
category, A1C result category and diabetes medication flag. Code values are
one-hot categories, never continuous magnitudes; a missing categorical value
uses `__MISSING__`, and an unseen validation category becomes an all-zero block
for that field. This policy preserves inference but cannot distinguish every
unseen category from a dropped/missing block without further review. The
transformed feature names carry `numeric__` or `categorical__` plus source field
names. Identifiers, target, race, gender, age, disposition and all excluded
fields are refused by exact predictor-order checking. All learned imputation,
scaling and encoding is inside a fresh fit per fold. A global prefit transform
was rejected because validation statistics would leak into training.

**Nested CV and candidates.** Five shuffled `StratifiedGroupKFold` outer folds
with seed 42 assess candidate protocols; three patient-disjoint inner folds
with seeds derived from 42 select bounded hyperparameters using average
precision. Every patient is wholly in one side of each fold, and both classes
must be present. The prior dummy shows prevalence-only performance. L2
Logistic Regression tries C=0.1 or 1 and unweighted or balanced classes; it is
compact and interpretable but linear in transformed features. Random Forest
tries depth 6 or 10 with 50 trees and leaf size 20, testing nonlinear
interactions at higher fit cost. Histogram Gradient Boosting tries 15 or 31
leaves, 30 iterations and leaf size 40, with a fold-local dense representation
guarded by a 256 MiB byte budget. These are research comparisons, not exhaustive
tuning. No synthetic resampling, deep learning or feature elimination occurs.

**Metrics, calibration and selection.** Early readmission is about 11% of the
training encounters, so accuracy can reward nearly always predicting negative.
Average precision measures how well positives are ranked as a precision-recall
summary and is prevalence-sensitive. ROC-AUC measures ranking across both
classes; neither proves probability quality. Brier score is mean squared
probability error, and log loss penalizes confident wrong probabilities.
Balanced accuracy averages sensitivity and specificity. Recall, specificity,
precision and F1 at 0.5 describe one arbitrary threshold; 0.5 is not a
clinical decision threshold. Per-fold training and validation scores, class
support, times, warnings and chosen parameters are retained. Sigmoid
calibration fits a logistic mapping on out-of-fold base probabilities from
patient-disjoint training folds, then applies it to outer validation. Both raw
and calibrated outputs are compared on outer folds. Calibration curves, slope
and intercept are diagnostic descriptions, not proof of transportability.
The highest mean outer average precision wins unless alternatives lie within
0.005; among those, lower Brier, higher ROC-AUC, lower log loss and a stable
name order decide. This guard prevents a tiny ranking gain from automatically
outweighing probability quality. Final hyperparameters are reselected by
three-fold CV on all training patients, and the complete protocol is frozen
before final fit or holdout prediction.

**Holdout governance and uncertainty.** An exclusively created selection JSON
binds the exact protocol to the config and nested-CV evidence. The final fit
uses training patients only. A local joblib artifact is bound to a SHA-256,
software versions and protocol hash; loading a user-supplied or mismatched
artifact is forbidden because joblib deserialization can execute code.
`evaluate_once` checks selection, source/policy/target/split identity and the
artifact manifest, then creates an exclusive claim before generating a single
held-out probability vector. A claim remains after failure to force review,
not an automatic retry. The holdout record reports a 0.5 confusion matrix,
discrimination, calibration and classification metrics. Its 95% bootstrap
intervals resample patients, keeping all of each selected patient's encounters
together; encounter-level resampling would understate dependence. These
intervals describe sampling variability under this cohort, not external or
clinical uncertainty.

### Verified training and held-out results

The verified training side contains 79,808 encounters from 56,178 patients:
70,734 negative and 9,074 positive. Both full training-only calculations
agreed after excluding wall-clock timings. Five outer folds contained disjoint
validation patients. The table gives the mean of the five outer validation
folds; AP is average precision, and lower Brier and log loss are better.

| Family | AP mean ± SD | ROC-AUC mean | Raw Brier | Sigmoid Brier | Sigmoid log loss | Training AP mean |
|---|---:|---:|---:|---:|---:|---:|
| Prior dummy | 0.113698 ± 0.000040 | 0.500000 | 0.100771 | 0.100771 | 0.354177 | 0.113698 |
| Logistic Regression | 0.197312 ± 0.009194 | 0.631704 | 0.206511 | 0.097854 | 0.342020 | 0.198916 |
| Random Forest | 0.196374 ± 0.009054 | 0.633537 | 0.098015 | 0.097783 | 0.341516 | 0.235960 |
| Histogram Gradient Boosting | 0.199591 ± 0.008761 | 0.635554 | 0.097638 | 0.097624 | 0.340964 | 0.215586 |

Sigmoid is monotonic here, so AP and ROC-AUC are unchanged within each family;
its benefit is probability quality. Balanced class weighting made some raw
Logistic Regression probabilities poorly calibrated (Brier 0.206511), while
group-OOF sigmoid improved Brier to 0.097854. This does not establish that
calibration will transfer to another hospital or period. The five histogram
outer AP values were 0.20771, 0.19627, 0.20434, 0.18582 and 0.20381. The
record retains every inner fold, all required secondary metrics, supports,
timings, selected parameters, and calibration curves. There were zero captured
convergence warnings across all candidate fits. Transformed feature counts
varied between 42 and 43 because vocabularies were learned within folds.

Histogram boosting had the highest outer AP. Logistic Regression and Random
Forest were inside the predeclared 0.005 AP equivalence margin, so lower Brier
decided. Histogram plus sigmoid had the lowest eligible Brier (0.097624 versus
forest 0.097783 and logistic 0.097854). Final three-fold training-only tuning
selected 15 leaves, 30 iterations and minimum leaf size 40; the 31-leaf option
had lower inner AP (0.197452 versus 0.199450). The selected protocol is bound
to training checksum `152b87cc3e0bc2ccaa365d7ea7de192f3f128214203ce38a1b88704a8a576aa4`
and selection checksum `85db5e79faacc80d9818b235c4e8338be0aeb10fbcf89da2f3bc56e87172e9a7`.
The numerically best candidate was also the selected system candidate here;
the Brier guard still mattered because it evaluated near-tied alternatives.

The single locked holdout contains 19,535 encounters from 13,812 patients,
including 2,240 positives. Its 500-repetition patient-cluster bootstrap used
seed 4242. Values below are encounter-level estimates with 95% intervals
formed by resampling whole patients:

| Metric | Held-out estimate | Patient-cluster 95% interval |
|---|---:|---:|
| Average precision | 0.202633 | 0.184091–0.221497 |
| ROC-AUC | 0.639473 | 0.626640–0.653593 |
| Balanced accuracy | 0.502418 | 0.500125–0.505621 |
| Recall | 0.005357 | 0.000452–0.012309 |
| Specificity | 0.999480 | 0.998931–0.999858 |
| Precision | 0.571429 | 0.200000–0.693429 |
| F1 | 0.010615 | 0.000902–0.024124 |
| Log loss | 0.342237 | 0.331423–0.352035 |
| Brier score | 0.098255 | 0.094170–0.101733 |

At descriptive threshold 0.5 the confusion matrix is TN 17,286, FP 9,
FN 2,228, TP 12. Thus the apparently high specificity and 57.1% precision
coexist with only 0.54% positive recall; this threshold would miss almost
all early readmissions and has no clinical authorization. Held-out calibration
intercept was 0.133640 and slope 1.058929. The six nonempty ten-bin curve
points are stored in `holdout.json`; a near-one slope on this cohort is a
descriptive diagnostic, not proof of future calibration.

**Overfitting and uncertainty.** Forest's training AP 0.235960 exceeded its
outer validation AP 0.196374 by 0.039586, the largest gap. Histogram's gap
was 0.015995 and Logistic Regression's was 0.001604. These are same-fold
training-versus-unseen-patient comparisons, not a formal significance test.
The selected histogram's held-out AP 0.202633 and ROC-AUC 0.639473 were near
its outer means 0.199591 and 0.635554, respectively; holdout Brier 0.098255
was slightly worse than outer sigmoid mean 0.097624. This one historical
patient split cannot demonstrate external, temporal, or clinical validity.

**Artifact and one-time evidence.** The fitted local joblib SHA-256 is
`8c3a99dd8dfe20d2a3a0a721637b4be500ee1b32843f7cefc3af265f07262f7a`.
`nested_cv.json`, `selection.json`, `artifact.json`, `holdout.claim` and
`holdout.json` are ignored local records; all cross-record hashes and recorded
software versions matched in the recovery check. The claim preceded the
held-out prediction, and a subsequent CLI invocation refused the existing
experiment directory before data loading. This is one held-out evaluation,
not a retry based on its score.

**Implementation timeline — Macro Milestone 2.** First, the frozen source and
patient split were reused so models could be compared on a valid population.
Next, fold-local preprocessing and four bounded candidates established
training-only comparison; nested group CV was needed before any honest model
choice. Group-OOF sigmoid and probability diagnostics followed because ranking
alone does not tell whether reported risks are usable probabilities. The
deterministic repeat, immutable selection, final fit and checksum-bound local
artifact then made the protocol reviewable before the one-time holdout. Finally,
patient-cluster intervals and the model card described uncertainty and limits.
The result is a reproducible educational comparison, not a deployed system.

**Interview follow-ups.** Why not select the forest with better training AP?
Its unseen-patient outer AP was lower and its train–validation gap larger.
Why did sigmoid leave AP unchanged? A strictly monotonic score mapping keeps
rank order, while changing probability magnitude. Why is threshold 0.5 a poor
headline? It detected only 12 of 2,240 positive encounters. Why not tune the
threshold on the holdout? That would turn the independent test into training
data. How can a completed model still fail before test evaluation? The
selection serialization guard found a list-order mismatch; verifying the
saved record and fixing canonical order allowed safe continuation without a
second training or held-out evaluation.

**Resume evidence for this milestone.** Four healthcare model families and
eight raw/calibrated protocols were compared on 79,808 training encounters;
one 19,535-encounter patient-disjoint holdout was evaluated once. Best outer
mean AP was 0.199591 and held-out AP was 0.202633. The model uses one
calibration technique, no XAI technique, and no deployed application. The
offline suite passed 87 tests after the guard addition; final verification
counts are recorded in the current supervisor handoff. No inference-latency
claim was measured.

**Decision record.** [ADR 0006](decisions/0006-healthcare-model-selection-protocol.md)
records the choice over row-level CV, a single split, isotonic calibration,
oversampling and unconstrained search, along with the trade-offs and conditions
for reconsideration. The held-out score may not be used to choose another
model, grid, calibration method, threshold or retry. A new scientifically
independent test population would be needed for a revised protocol.

**Concepts learned through this milestone.** Group-aware nested CV separates
hyperparameter search (inner folds) from comparison (outer folds); I should be
able to explain why a patient, rather than an encounter, is the sampling unit
for separation, and why outer variance is not a confidence interval. Fold-local
preprocessing means imputation, scaling and one-hot vocabulary are learned only
from the fitting subset; I should be able to identify where a global fit would
leak. Calibration maps scores toward observed frequencies and may improve
Brier/log loss without improving ranking; I should distinguish ranking from
probability quality and explain why calibration needs held-back groups.
Cluster bootstrap repeats patient sampling with replacement; I should be able
to explain how repeat encounters remain correlated and why the interval does
not validate another hospital or decade.

**Important problem encountered and recovery.** The first real training-only
attempt was interrupted before any manifest, model selection or holdout access
when code review found that `HistGradientBoostingClassifier` defaults to
automatic internal early stopping on large data. Its hidden validation split
is row-level and could place a patient's encounters on both sides. This was a
methodology bug in the candidate constructor, not an observed held-out result.
The incomplete attempt was stopped; no selection or holdout claim existed.
`modeling.py` now forces `early_stopping=False`, the versioned grid records it,
and `test_histogram_never_uses_internal_row_validation` verifies the setting.
The complete training-only calculation was restarted. Lesson: group-aware
outer CV alone does not guarantee that an estimator's own internal validation
respects groups. In an interview, explain why the hidden row split mattered
even though the locked final holdout was still protected.

**Interrupted-run recovery (2026-10-06).** A later nested-CV attempt was
manually interrupted after roughly 55 minutes. Inspection found no production
`artifacts/healthcare-model-v1` directory, training manifest, selection record,
artifact, or holdout claim; only ignored synthetic test outputs existed. Since
the runner persists no fold checkpoint before both complete training passes,
none of that partial computation could be proved complete or reused. The
recovery restarted the unchanged folds, seeds, grids, calibration and selection
rules. Review of the resume path also found that `evaluate_once` trusted the
caller's selection record without independently checking that the saved nested
CV record contained every family, fold and grid. It now verifies completeness,
the deterministic evidence hash, and the selection's binding to that evidence
and config before the holdout claim. A targeted incomplete-record refusal test
and the full offline suite passed. The key lesson is to distinguish an
in-memory partial calculation from a published complete experiment, and to
make the final evaluation guard validate its own prerequisites.

A later review interruption exposed a process mistake: I misread the TOML
secondary-metrics list and stopped another training-only attempt to add Brier
score, although Brier was already declared and computed. Inspection of the
exact line corrected the assumption before any edit to the config; the
interrupted attempt had published no record or holdout claim and was restarted
from scratch. This cost computation time but changed no methodology or result.
The prevention lesson is to inspect the precise configuration text before
interrupting a long running experiment for a suspected omission.

At the start of this recovery, three simultaneous shell process creations
failed with `CreateProcessWithLogonW failed: 1056`; the independent commands
then succeeded sequentially. This was a tooling concurrency problem during
inspection, not a data or modelling failure, and produced no experiment output.
Keeping process launches sequential made the audit reproducible.

**Selection-record order mismatch and recovery.** The completed repeat and
final fit produced `nested_cv.json`, `selection.json`, `artifact.json` and a
checksummed model, but `evaluate_once` refused before creating `holdout.claim`.
The symptom was `selection is not bound to complete training evidence`. The
saved JSON sorts family keys alphabetically, while the in-memory selection
listed candidates in the frozen config order; the winner and numerical values
were identical, but list equality failed. The first diagnosis checked each
binding separately and found only the ordered `selection_evidence` comparison
false. `select_protocol` now enumerates families in config order regardless of
JSON key order, and a regression test reverses the input dictionary order.
Completeness, selection hash, config hash, artifact hash, protocol, software
versions and absence of a holdout claim were verified before reusing the
published training and fitted artifact records. Then only the guarded
`evaluate_once` stage was resumed, creating one claim and one result. This
recovery changed serialization order handling, not the frozen selection rule
or metrics. The lesson is that deterministic persistence needs a canonical
sequence for lists derived from dictionaries, even when JSON keys are sorted.

**Project defence and interview preparation.** Why compare a dummy? It reveals
what the observed training prevalence alone achieves. Why is average precision
primary? Positive cases are uncommon, and the task needs useful positive
ranking, while Brier/log loss guard probability quality. Why not simply use the
highest AP model? A difference under the prespecified 0.005 margin may be less
important than a meaningful calibration loss. Why calibrate with OOF scores?
The calibrator should learn from predictions for patients unseen by the base
model that generated those scores. What would change for clinical use?
Contemporary external/temporal validation, clinical threshold and harm analysis,
workflow timestamp verification, governance, privacy and prospective monitoring.
The current results are educational research only.

**Semester viva preparation.** Basic: What is the positive class, and why is
accuracy weak here? Intermediate: How do inner and outer group folds differ?
Why do unseen category indicators become zero? Why can calibration change Brier
without changing ROC-AUC? Difficult: What leakage occurs if the calibrator is
trained on in-sample predictions? Why does a patient bootstrap differ from an
encounter bootstrap? Why does an immutable claim remain after a failed
evaluation? How does the selection record stop retrospective model shopping?


## Macro Milestone 1 — Healthcare realignment and evidence (2026-10-05)

**Historical foundation record:** all implementation-status, review and next-step
statements in this section describe Macro Milestone 1 at that date. Macro
Milestones 1 and 2 are now completed; the healthcare model and Macro Milestone 3
XAI, stability, subgroup audit and feasibility assessment now exist. Macro
Milestone 3 awaits external review. API/UI/database/registry/deployment remain
unimplemented. The source/cohort/split measurements below remain unchanged.

**Interpretation at Macro Milestone 1:** Aletheia remained a high-stakes tabular XAI platform, demonstrated primarily with hospital readmission risk and secondarily with the approved South German Credit benchmark. The original `prompt.txt` named credit first, so the early approved phases built a credit data foundation and training-only baseline. The supervisor then selected healthcare as the flagship. Preserving credit avoided discarding tested methods and supplied a second domain against which later shared interfaces could be judged. At that foundation stage, no healthcare model, API, UI, database, registry or deployment existed yet.

### What was built, why now, and how it works

This foundation precedes model work because a wrong target, a post-outcome field, or shared patients across train/test would make later metrics untrustworthy. The official UCI 296 archive is pinned by archive and member hashes in `configs/datasets/healthcare_uci296_v1.toml`; `foundation.py` verifies bytes before extracting exactly two flat files, strictly loads 50 ordered columns, rejects count/key/target mismatches and normalizes only documented `?` tokens. It maps `<30` to 1 and `>30`/`NO` to 0, removes death/hospice discharges, creates `uci296-<encounter_id>`, and returns separate predictor/audit views. `configs/features/healthcare_uci296_v1.toml` assigns every raw field exactly one role. The CLI `python -m aletheia.domains.healthcare acquire|verify` calls these functions. Alternative loose pandas loading would be shorter but could silently alter schema or missingness; a dataset-client library would add a dependency without improving this fixed source's byte verification.

The prediction timestamp is **discharge**, after the disposition is known and before 30-day follow-up. This timing makes encounter stay/lab/medication-count values plausibly observable; real workflow timestamps remain unverified. Disposition is used only to define the eligible cohort and is then excluded from predictors because death/hospice/transfer codes make the outcome structurally different or target-adjacent. `race`, `gender`, `age` are audit-only; IDs are metadata. The initial 13 predictors are deliberately narrow. Weight is 96.86% `?`; payer/specialty and diagnosis codes have substantial missingness/high cardinality. Detailed medication fields require later timing/recourse review. This default-deny choice reduces leakage and sparse-category risk at the cost of leaving possible signal unused.

`patient_nbr` groups repeated encounters. A seeded SHA-256 threshold assigns a patient to one partition independent of outcome, then a JSON lock binds the raw dataset SHA, feature/target versions, class/partition counts and membership digest. `verify_split_lock` recomputes and refuses mismatch; `partition` checks both patient and encounter disjointness. Alternative encounter-random splitting risks entity leakage; first-encounter-only would change the cohort; group stratification might improve balance but add target-dependent selection. The observed lock has train 79,808 encounters/56,178 patients (class 0 70,734; class 1 9,074), held out 19,535/13,812 (class 0 17,295; class 1 2,240). This is approximately 80/20, and group-aware CV remains a later requirement. It is not temporal/hospital validation. No held-out outcome was used for modelling or tuning; class counts are split-integrity evidence only.

The dataset was selected because the official UCI record and Strack et al. paper give a traceable public early-readmission outcome; 101,766 encounters and repeated patients make leakage controls meaningful on an 8 GB laptop (~263 MB all-string pandas inspection). MIMIC-style data could supply dates and deeper clinical variables but adds controlled access/privacy/compute demands. UCI data are from 1999–2008, omit hospital/date identity and cannot establish clinical validity. The paper's narrower study sample is not claimed to match this cohort. See [HEALTHCARE_DATASET_AUDIT.md](HEALTHCARE_DATASET_AUDIT.md) for full source, counts, dictionary and missingness.

### System path and future boundaries

The existing credit code and manifests remain in place; healthcare lives in `src/aletheia/domains/healthcare`. Future shared experiment, XAI and serving use cases should depend on domain contracts. Selected future architecture is MLflow registry, FastAPI, PostgreSQL audit, React/TypeScript, Docker/Compose, GitHub Actions, managed deployment, monitoring, cards and RBAC. DagsHub, DVC, managed host and optional OpenRouter narration remain provisional. RunwayML is rejected. Data/version identities and secrets must be separated; public demonstrations must use synthetic/de-identified examples. Similar-case retrieval will use training cases and a versioned distance metric, not collaborative filtering. A Python/TypeScript import graph with cycle/direction checks is planned for later CI. See [DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md) for caller, artifact, alternative, security and failure details.

**Milestone order:** (1) foundation/design committed and externally reviewed, with this minor repair pending; (2) healthcare models and calibration; (3) explanations/conditional audits; (4) application/MLOps; (5) delivery/monitoring/code graph. This order prevents a polished UI from hiding invalid evidence. Only the first milestone exists as implemented work. Exact software-test evidence and unresolved questions are in the current [SUPERVISOR_HANDOFF.md](SUPERVISOR_HANDOFF.md). No healthcare ML experiment or fairness result exists.

### WIP stash reuse assessment (read-only inventory)

`stash@{0}` was inspected, never applied. Tracked changes: `docs/CURRENT_TASK.md` is obsolete task text and must be discarded, not restored; `src/aletheia/experiments/manifest.py` and `src/aletheia/ml/baseline.py` contain credit research-core changes requiring independent verification before any later reuse. Untracked stash contents: `configs/experiments/comparator_v1.toml`, `src/aletheia/ml/comparator.py`, `comparator_run.py`, `protocol.py`, `selection.py`, `tests/integration/test_comparator_pipeline.py`, `tests/unit/test_comparator.py`, and ADR 0003 are credit-comparator specific, deferred and must be re-versioned/reverified; `configs/audit/explanation_v1.toml`, `src/aletheia/xai/{__init__,audit_run,evidence}.py`, and ADR 0004 contain potentially reusable explanation ideas but require healthcare adaptation and independent verification; `configs/audit/counterfactual_v1.toml`, `src/aletheia/counterfactual/{__init__,search}.py`, and ADR 0005 are credit-constraint specific and must not be reused as clinical recourse; `configs/audit/stability_v1.toml`, `src/aletheia/stability/{__init__,metrics,perturb}.py`, and ADR 0006 have potentially generic metric/perturbation ideas but require healthcare feasibility checks. No stashed file was restored. Stashed ADR numbers do not reserve committed identifiers.

### Concepts, trade-offs and defence notes

**Observation unit versus group:** one row is an encounter, but one patient may have many encounters. Grouping by patient prevents near-related rows in train and holdout. Be able to explain why encounter uniqueness does not imply independent samples, why group CV must follow the same rule, and why this still lacks external validity.

**Target semantics and decision time:** `<30` is early readmission; `>30` is a negative for this binary question but remains distinct in raw data. At discharge, treatment summaries may exist, while follow-up outcome does not. Be able to explain why excluding a death/hospice row changes the population and why using a discharge disposition as a model predictor would be problematic.

**Missingness and role policy:** `?` is an explicit source token only in seven fields; unknown administrative labels are categories, not automatically missing. Roles are exhaustive and disjoint, so new columns fail until reviewed. Be able to explain how a fit-on-all-data imputer would leak validation information and why this milestone performs no fitted imputation.

**Stable split identity:** patient hash assignment is deterministic and label-independent; the lock verifies source/config/target and counts. It sacrifices exact stratification. Be able to explain why the held-out class counts may be checked for support without tuning a model on them, and why class balance alone cannot prove leakage absence.

**Interview prompts:** Why healthcare after credit? The supervisor changed the primary demonstration while preserving approved credit research as a benchmark. Why not the highest-accuracy model? Accuracy alone can hide class imbalance, calibration and audit limitations; no healthcare model comparison has yet happened. What is the hardest current problem? Reconciling source semantics, repeated patients and discharge-time leakage before training. How would you deploy? Through versioned core artifacts, authenticated FastAPI, PostgreSQL audit, registry and CI, all still future work. What remains before real care use? Contemporary external validation, operational timestamp proof, clinician review, privacy/security governance, prospective monitoring and regulatory assessment.

**Semester viva — Basic:** What is a row? An inpatient encounter. What is positive? `<30` readmission. **Intermediate:** Why patient-group splitting? Repeated encounters can leak patient-specific patterns. Why only seven `?` fields? Those are the observed source encodings, and normalization is contract-bound. **Difficult:** Does a random patient split test temporal transfer? No, dates are absent. Can a counterfactual medication change be called actionable? Not without clinical and temporal constraints; none is implemented.

**Resume evidence:** verified healthcare raw 101,766 encounters, eligible 99,343, 69,990 eligible patients, 50 raw fields, 13 approved predictors, one frozen split; model families, healthcare metrics, deployment status and inference latency remain unmeasured. The previously documented credit baseline evidence remains separate. **Useful next step:** only after supervisor approval, design group-aware healthcare training CV and fit preprocessing within folds. **Research extension:** external/temporal validation if a suitable lawful dataset becomes available.

### Important problems encountered in this milestone

**Python TLS retrieval failure:** direct `urllib` against the official archive failed with an expired certificate chain on this Windows environment after sandbox network permission was granted. Inspection with Windows `curl.exe -I` succeeded over verified TLS; download via `curl.exe` succeeded, and archive/member hashes were recorded. No TLS verification was disabled. The code's downloader remains fail-closed; a user with the same Python trust-store issue can place a TLS-verified official archive in ignored raw storage and use the normal verifier. Lesson: network reachability and certificate trust are separate failure modes; never bypass identity checks. A first config patch failed because new directories were absent; after creating only authorized directories, the patch succeeded. Initial code lint found long lines, fixed by Ruff formatter. No ML leakage or model failure was observed because no model was trained.

### External review repair after commit 49753d5

The external supervisor passed Macro Milestone 1 with minor fixes. The public
overview and handoff still carried pre-commit or credit-first wording, and the
healthcare tests lacked direct assertions for all six death/hospice codes,
eligible-row preservation, existing-lock overwrite refusal, and cleanup after
a rejected download. The cause was incomplete review coverage and stale
documentation, not an observed source failure. Focused synthetic, offline tests
now exercise these boundaries through `cohort`, `write_split_lock`, and a
monkeypatched `acquire`; all pass without a source or contract change. The
current overview and README identify healthcare as flagship and credit as
secondary, while the detailed credit methods below remain historical evidence.
The earlier `git diff --check` failure was a trailing blank line in user-owned
`CURRENT_TASK.md`; the user removed it before committing, and the committed
check passed. This repair's check also passes. The lesson is to test exclusion
and cleanup rules directly and to distinguish an unresolved check from a
resolved pre-commit problem. No model or later milestone was started.

## Project Overview

Current local application: authorized manual entry of 13 model-compatible fields, frozen calibrated prediction and disclosed reference-contrast evidence, immutable prediction/audit records, saved history and reviewer workflows. Login, Signup and real external OIDC remain deferred. See the interactive milestone above.

Aletheia is an Explainable AI (XAI) decision-auditing project for
structured classification in high-stakes contexts. Hospital readmission risk
is the primary flagship demonstration: its patient-group-safe data and
retrospective model comparison now support a bounded educational audit.
South German Credit remains a retained secondary benchmark with its
approved data foundation and training-only baseline. Intended users are ML
engineers or data scientists comparing experiments, human reviewers inspecting
predictions, and future administrators managing access and audit evidence.

This is not a normal prediction dashboard. A dashboard can show a class and
probability. Aletheia's purpose is to compare predictive models using
performance *and* auditable evidence: global/local explanations, constrained
counterfactuals, explanation stability, and, only when valid data exists,
measured subgroup differences. It will not certify clinical or lending decisions,
prove causality or fairness, replace a human reviewer, or claim a new XAI method.

## Problem Statement

Aggregate metrics can conceal opaque decision logic, unstable explanations, and
different error patterns across groups. A high-stakes prediction alone does not
show a reviewer what inputs influenced it, whether a feasible change could
alter it, or whether observed subgroups have materially different outcomes.
Accuracy alone is especially weak when classes or false-positive/false-negative
costs are imbalanced.

Aletheia will investigate performance-versus-auditability trade-offs. An
explanation is evidence about a fitted model output, not a causal or human
reason. A counterfactual changes the model output, not reality. Fairness metrics
measure selected properties, not legal compliance or universal fairness.

## Scope, Users, and Assumptions

**Established scope:** Macro Milestone 1 passed external review at `9073c453`.
Macro Milestone 2 is the preserved committed model prerequisite at `49a1a8c`.
Macro Milestone 3 adds the locally verified explanation/stability/subgroup audit
and no-recourse assessment documented above, externally approved at `ff9dce291`
as recorded by CURRENT_TASK.md.
Earlier approved credit phases provide the secondary benchmark,
including a training-only dummy/Logistic Regression baseline. Healthcare now has a local Compose application with independent case entry; its research result remains retrospective educational evidence. Credit remains research-only; training CV is not held-out or production evidence.

**Assumptions requiring validation:** the selected data must have a clear
target, source/licence, data dictionary, sufficient observations/minority-class
support, and feature semantics adequate for realistic counterfactual constraints.
Fairness is possible only where legitimate audit attributes and adequate
subgroup support exist; protected attributes must not be inferred from proxies.
The positive class, threshold, and decision/error-cost framing cannot be chosen
before the dataset is understood.

### Permanent Vision and Current Authorization

`prompt.txt` preserves Aletheia's permanent original vision. It describes the
complete platform ambition, not permission to implement every feature now.
`docs/CURRENT_TASK.md` authorizes only Macro Milestone 4 Stage 0 documentation
planning. Macro Milestone 3's completed audit is externally approved at
`ff9dce291`. Planning completion does not authorize implementation. The frozen
contracts, split, source, model, dependencies, preserved credit work and earlier
metrics remain unchanged. Application, MLOps, LLM/RAG and later work remain
outside implementation authority for this task.

## Functional Requirements

Current healthcare implementation satisfies the source, preprocessing, model
comparison, class-aware evaluation, global/local XAI, stability, subgroup audit
and reproducible evidence requirements. Counterfactual feasibility is implemented
with an explicit no-recourse result; candidate generation is not justified.
Stability uses training cases, not another holdout access. The list below preserves
the original research requirements rather than claiming every item is future work:

1. preserve an approved dataset's source, licence, version, schema, and data
   dictionary;
2. validate data and create reproducible training-only preprocessing;
3. train a small predeclared model set under common split rules;
4. compare class-aware metrics, confusion matrices, and validation evidence
   without tuning on final test data;
5. produce global and selected-case local explanations, labelling native and
   post-hoc methods;
6. assess counterfactual feasibility and generate constrained candidates only
   where defensible (healthcare currently has no admissible recourse);
7. run a predeclared explanation-stability study for authorized cases
   (implemented healthcare study uses training-only cases);
8. perform subgroup analysis only when defensible; and
9. record data version, seed, split, preprocessing, feature schema, algorithm,
   hyperparameters, environment where practical, and metrics.

An API, dashboard, database, and audit log may later present this evidence, but
are not prerequisites for answering the research question.

## Non-Functional Requirements

- **Reproducibility:** fixed seeds where supported, reproducible/recorded split
  membership, and all learned transforms fitted on training partitions only.
- **Validity and traceability:** each result names its data version, model,
  partition, metric definitions, and explanation configuration; leakage control
  takes priority.
- **Interpretability:** reports must not imply causal, stable, or fair behaviour
  that was not measured.
- **Efficiency:** work must run locally on a normal student laptop; no high-end
  GPU, cloud service, or distributed infrastructure is required.
- **Safety and privacy:** public/de-identified data only; no credentials; no
  representation that the prototype is suitable for real lending.
- **Testability:** later transformations, metrics, constraints, and experiment
  metadata should be independently testable.

## Research Questions

**Primary current question:** For the documented healthcare readmission cohort,
how can later model families trade predictive performance, calibration,
interpretability, explanation stability, and conditional subgroup evidence in a
human-auditable workflow? Macro Milestones 2 and 3 now supply bounded model,
calibration and audit evidence; contemporary external and clinical validity
remain unresolved.
The earlier credit-specific version of this question remains a secondary-domain
research record for the approved benchmark.

**Secondary:**

- Does a complex model make a material, consistent validation/held-out
  improvement over an interpretable baseline?
- For identical held-out cases, how do local explanations differ in important
  features and direction across models?
- Under small valid perturbations, how do predictions and explanations change?
- How far must mutable, bounded features move to alter a model class, and are
  those candidates plausible under documented constraints?
- If a defensible audit attribute exists, what selection-rate, error-rate,
  precision/recall, and calibration differences are measured by subgroup?

These are planning questions, not empirical conclusions. The remaining Phase 1–4
details below document the approved credit benchmark and its learning history;
their former credit-first scope and tool-selection language is historical, not
the current healthcare-first product roadmap.

## Dataset Requirements

Before selection, assess source/licence, observation unit, target meaning,
collection period, feature semantics, missingness, class distribution,
duplicates, leakage-prone/post-outcome columns, and temporal/entity structure.
The data needs adequate minority and, if applicable, subgroup support for a
defensible held-out study; the threshold for adequacy must follow inspection,
not be invented now. Synthetic data could later test software mechanics but
cannot support the study's empirical claims. Reject data with unclear
provenance/target, unusable feature semantics, likely leakage, or inadequate
support.

### Phase 1 Dataset Decision

South German Credit was selected after comparing four official UCI candidates.
Phase 1 and dataset suitability for the academic Research MVP are externally
supervisor-approved, within the limitations above.
It passed the gates for traceable provenance, CC BY 4.0 usage, explicit contract-
compliance target, corrected feature meanings, modest minority-class support,
laptop size, and constrained counterfactual semantics. The official raw file
has 1,000 granted credit contracts, 20 predictors, and target `kredit` (`0=bad`
contract compliance, `1=good`); 300 cases are bad and 700 good. The adverse
event for future evaluation is the raw `0` value and must be mapped explicitly.

Dataset audit came before architecture because the data determines target
semantics, observable feature timing, leakage controls, split feasibility,
audit-only attributes, counterfactual constraints, and the kind of XAI evidence
that can be defended. Detailed sources, hashes, computed profiles, candidate
rejections, and feature roles are in `docs/DATASET_AUDIT.md`.

The alternatives were Default of Credit Card Clients (larger and better for
potential subgroup study, but dominated by historical/lender-controlled inputs
and undocumented raw codes), the older Statlog German Credit entry (known
code-table defects), and Credit Approval (anonymized features and undefined
label meaning). For the selected data, age, combined personal-status/sex, and
foreign-worker status are proposed audit-only—not prediction—attributes;
telephone and the current-credit count `bishkred` are excluded. `bishkred` is a
default-deny decision because its safe observation cutoff is not established,
not a claim that target leakage was proved.

A future stratified random split is recommended because no dates or entity IDs
support temporal or group splitting. It cannot control undisclosed repeated
borrowers or test forward-time generalisation. Only constrained contract terms
make a limited counterfactual proof possible; immutable and historical fields
must not become recourse. Fairness analysis is not yet justified because sex is
not recoverable cleanly and the foreign-worker group has only 37 observations,
including four bad outcomes.

## Planned ML and Evaluation Strategy

**Historical credit-first planning:** the strategy below preceded healthcare
selection. Current healthcare modelling/calibration is completed under the
patient-group protocol in Macro Milestone 2 above and ADR 0006; it does not use
the credit random-split defaults described here.

**Candidate models:** Regularised Logistic Regression is the required,
interpretable baseline: fast, reproducible, and directly inspectable through
coefficients. A shallow constrained Decision Tree is an optional native
baseline: rule-like but vulnerable to instability/overfitting. Random Forest
and Gradient Boosting are principal nonlinear tabular comparators: they test
whether added flexibility is worth reduced direct interpretability. A dummy
classifier may provide a class-imbalance sanity reference. SVM, k-NN, AdaBoost,
and a small MLP are not commitments; an ANN belongs only in a later
strong-semester comparison if data and runtime justify it.

**Baseline and selection:** Complex models face the logistic baseline with the
same split and preprocessing discipline. The model cannot be chosen by accuracy
alone. After target/error costs are known, predeclare a primary class-aware
metric (possibly F1, recall, or PR-AUC), supported by ROC-AUC, precision,
recall, confusion matrices, calibration where feasible, and inference cost.

**Evaluation:** The default is a reproducible stratified train/test split with
the test set untouched until final comparison. Use stratified cross-validation
inside training data for candidate selection and only a bounded predeclared
search. Fit imputation, encoding, scaling, selection, and resampling within
each training fold. If review finds chronology or repeated entities, use
temporal or group-aware splits instead. Record seed, folds, schema,
preprocessing, algorithms, hyperparameters, library versions, and metric
definitions. This protects against target, temporal, preprocessing, duplicate,
and entity leakage.

## Explainability and Audit Requirements

**Current healthcare boundary:** global/local sampled Shapley probability
explanations, training-only recording stability, guarded subgroup metrics and
counterfactual feasibility are completed and externally approved at `ff9dce291`.
The conceptual credit-first requirements below are historical planning; their
deferred methods do not describe missing healthcare implementation. The exact
current method, samples, limitations and evidence are recorded in Macro Milestone
3 above and ADR 0007. No actionable counterfactual search is implemented.

**Global vs local:** Global explanations ask which inputs generally influence a
model over a stated population; native coefficients/tree structure and
permutation importance or SHAP summary evidence are candidates. They do not
explain one decision, prove causality, or prove fairness. Local explanations ask
which inputs are associated with raising/lowering output for one record relative
to a stated reference. Prefer native evidence where faithful; SHAP is a
candidate common post-hoc method. LIME is unnecessary unless it serves a defined
comparison. Post-hoc evidence depends on background data, correlation,
preprocessing, and settings.

**Counterfactual strategy:** A counterfactual is a valid, minimally changed
input that changes the *fitted model's* class. Future constraint specifications
must label features immutable (such as age/protected attributes), mutable, or
constrained mutable with ranges, categories, direction, and dependency rules.
Cost should prefer sparse, scaled-small changes. Outputs are model-recourse
candidates—not financial advice or an approval guarantee. Custom constrained
search versus a library such as DiCE remains open until licence, constraints,
reproducibility, and testing are evaluated.

**Explanation stability:** For selected held-out cases, create small valid and
plausible perturbations, recompute prediction/explanation, and report both
prediction changes and explanation similarity. Predeclare measures such as
top-k overlap/rank correlation and normalized attribution change. Cases crossing
a decision boundary are separate because identical explanations are not
expected. Perturbation size, eligible features, background data, and samples
await dataset review. This is a strong-semester feature after core MVP evidence.

**Fairness:** Only with valid audit attributes and adequate group support,
report counts, selection/positive-prediction rates, false-positive and
false-negative rates, precision/recall, and calibration where meaningful, with
uncertainty or warnings for small groups. Do not infer sensitive identity, add a
protected feature for convenience, remove one and call the model fair, or issue
a binary fairness claim. Conflicting fairness definitions and data limitations
must be explicit.

## Risks and Controls

ML risks: target/temporal/post-outcome leakage; transforms fitted outside
training data; repeated-entity leakage; class imbalance; public data not
representing real lending; misleading explanations; implausible
counterfactuals; and fragile subgroup results. Controls: semantic/source review,
leakage checks, pipeline isolation, appropriate splitting, class-aware metrics,
documented limitations, feature constraints, and conditional fairness analysis.

Engineering risks: premature dashboards/APIs/databases/MLflow/Docker,
unnecessary microservices/abstractions, experiment-result drift, XAI dependency
compatibility, misleading visuals, and future sensitive-data logging. Controls:
research-first sequencing, minimal dependencies, recorded runs, clear caveats,
and later privacy-conscious audit design.

## Scope Boundaries

The following Research MVP and semester-application boundaries describe the
earlier **credit-first phases**. The current healthcare-first capability and
tooling boundaries are in the Macro Milestone 2–3 records above, the current
five-milestone execution plan and product requirements. Every status statement
in the credit-first boundaries below is historical, including the then-unselected
tools and then-unimplemented stability study.

**Research MVP:** the minimum evidence-producing ML/XAI prototype: one approved
documented dataset; leakage-safe reproducible preprocessing and splitting; an
interpretable baseline and justified nonlinear comparators; cross-validated
selection within training data; untouched held-out evaluation; global/local
explanation evidence; a constrained counterfactual proof of concept; traceable
experiment metadata; and a concise research comparison or prediction-inspection
presentation. Fairness remains conditional on legitimate audit attributes,
adequate subgroup support, and appropriate methodology.

Explanation stability remains part of Aletheia's complete research question but
is not required to complete the initial Research MVP. It is required before
claiming that the complete research question, including stability, has been
answered. Its perturbation rules, eligible features, sample selection,
background/reference data, similarity metrics, and boundary-crossing treatment
must follow dataset inspection; it is not implemented, measured, or validated.

**Semester application/demo scope:** a later usable application built only after
reliable Research MVP evidence exists. Subject to separate approval and
justification, it may add a minimal API, reviewer-facing interface, experiment
tracking or appropriate persistence, targeted tests, audit records, and local
reproducibility/containerization. FastAPI, MLflow, PostgreSQL, React/Next, and
Docker are unselected technologies. Finishing the Research MVP neither completes
the original platform vision nor automatically completes this application scope;
application features must present verified research evidence rather than conceal
weak methodology.

**Enterprise extensions:** explicitly deferred are unnecessary early
microservices, Kubernetes, RBAC, CI/CD, cloud infrastructure, approval
workflows, production monitoring, scheduled retraining, production registry,
drift/explanation-drift monitoring, real-lender integration, large deep
learning, and local LLMs.

## Decisions Finalized for the Baseline and Deferred Work

**Historical secondary credit baseline decisions:** the deferred healthcare
model/XAI status is superseded by Macro Milestones 2–3. Future application tools
are selected/provisional in the current deployment design, still unimplemented.

Phase 2 selects a research-first modular monolith, Python 3.12, pandas,
scikit-learn, standard TOML/JSON configuration/artifacts, pytest, Ruff,
Matplotlib/Markdown reporting, and an immutable local run-store concept. Phase
3 verified and pinned the subset it uses: Python 3.12.10, pandas 3.0.5,
scikit-learn 1.9.0, pytest 9.1.1, Ruff 0.16.6, pip 26.2.1, setuptools 84.0.0,
and the transitive packages in `requirements.lock.txt`.

Phase 4 retains the `bishkred` exclusion and 15-feature prediction role set. It
freezes two scaled quantitative fields, 13 explicitly one-hot-encoded fields,
five-fold shuffled stratified training CV with seed 42, ROC-AUC as primary,
eight supporting metrics, and threshold 0.5 for descriptive confusion metrics
only. It performs no search and stores no fitted model. Comparator search,
serialization, held-out evaluation, SHAP, counterfactual search, fairness,
stability, FastAPI, frontend frameworks, MLflow, databases, Docker, deployment,
authentication, and enterprise infrastructure remain deferred or unselected.

## System Architecture

**Current implementation:** the healthcare Python research core now includes
foundation, patient-group modelling/evaluation, frozen calibrated inference,
global/local XAI, recording stability, guarded subgroup audit and fail-closed
recourse feasibility, with immutable local model/audit records. See
[ARCHITECTURE.md](ARCHITECTURE.md) and the Macro Milestone 2–3 component/data-flow
records above. FastAPI, React UI, PostgreSQL, MLflow, JWT/local entitlements and local Compose serving now wrap this research core; see the interactive milestone and current ARCHITECTURE. Real external OIDC, public/cloud deployment, CI/CD, monitoring and LLM/RAG remain unimplemented.

**Historical credit Phase 2–4 architecture:** the following description and its
future-method statements preserve the secondary benchmark's earlier state.

**Externally supervisor-approved Phase 2 design:** a research-first modular
monolith. One Python research core contains small components for verified data
acquisition/loading, schema/target/feature policy, and deterministic splitting;
later approved phases may add preprocessing, model training/evaluation, audit
methods, and immutable local experiment evidence. A CLI/report adapter will
eventually compose the complete core. Future
API and UI layers may call the same use cases and load explicit validated runs;
they may not duplicate preprocessing, feature-code mapping, model inference, or
explanation logic.

Dependencies point from delivery/orchestration toward the research modules and
simple contracts. Research code must not import HTTP, UI, database, or deployment
frameworks. The exact fitted preprocessing/model pipeline, transformed-feature
map, feature-policy version, and run hash bind training, inference, and
explanations together. Local run directories are staged, checksummed, validated,
published atomically, and never overwritten; reports consume them without
implicitly rerunning training.

The component boundaries, failure modes, tests, technology matrix, and diagrams
are in `docs/ARCHITECTURE.md`. ADR 0001 records the modular-monolith decision;
ADR 0002 records the training-only baseline protocol. The Phase 3 data boundary
and Phase 4 training-only baseline described below are implemented.

Important planned failure boundaries are checksum/schema/category mismatch,
invalid target or forbidden feature roles, split overlap, preprocessing fitted
outside training data, incompatible pipeline artifacts, explanation/run
mismatch, invalid or absent counterfactuals, and insufficient fairness support.
Phase 3 tests exercise its refusals, target mapping, and deterministic splits.
Phase 4 tests now cover transformed-feature consistency, fold-local fitting,
metric fixtures, class orientation, shared CV membership, deterministic reruns,
manifest guards, and atomic publication. Exact explainer association and
counterfactual constraint guards remain future work.

## Implemented Phase 3 Data Foundation

Phase 3 was implemented before preprocessing and modelling because every learned
step must depend on a verified dataset identity, correct label orientation,
approved features, and immutable test membership. Without this boundary, later
results could silently use different bytes, reverse the adverse class, admit an
audit/leakage-risk field, or drift to a more favourable test split.

`configs/dataset.toml` is the source identity/schema contract: official UCI and
DOI references, archive/member/raw sizes and SHA-256 digests, exact 21-column
order, row count, target mapping, category domains (including documented but
unobserved purpose code 7), and observed-only quantitative ranges.
`configs/features.toml` independently records semantic types and the versioned
role policy: 15 predictors; `famges`, `alter`, and `gastarb` audit-only;
`telef` and `bishkred` excluded; raw/derived targets; and `row_key` metadata.
Observed ranges describe this fixed file and are not future inference limits.

The main implementation paths are:

| Location | Responsibility and caller | Dependencies and important refusal |
|---|---|---|
| `config.py` / `load_dataset_contract`, `load_feature_policy` | CLI and tests load immutable value contracts | `tomllib`; refuses malformed hashes, missing tables, duplicate/overlapping fields, and incomplete role/semantic coverage |
| `data/acquire.py` / `acquire_dataset` | CLI/live test stages the official archive and atomically publishes only the approved raw member | standard HTTP/TLS, hashing, ZIP/BZIP2, paths; refuses size/hash mismatch, unsafe/missing/duplicate member, partial download, and invalid existing destination |
| `data/load.py` / `load_raw_data` | validation flow loads only checksum-verified ASCII | pandas plus integrity check; refuses header/order/row/token drift and creates source-position keys rather than using pandas index |
| `data/validate.py` / `validate_raw_data` | CLI/integration tests enforce raw invariants | explicit contract checks; refuses nulls, non-integer columns, bad keys/categories/counts, and complete or predictor-only duplicates |
| `data/target.py` / `add_adverse_target` | role/split flow preserves `kredit` and adds `adverse_event` | explicit truth table; refuses labels outside `{0,1}` |
| `data/roles.py` / `build_feature_views` | CLI creates aligned prediction/audit/excluded/target/metadata views | versioned feature policy; unknown or unassigned fields fail closed and `model_input()` returns predictors only |
| `data/split.py` / generation and verification functions | CLI creates/verifies membership; Phase 4 may later consume it after approval | scikit-learn splitter plus canonical JSON/SHA-256; refuses identity, membership, count, coverage, overlap, or checksum drift |
| `data/__main__.py` | `python -m aletheia.data` composes only acquire, validate, and split commands | calls the modules above; it exposes no preprocessing, fitting, metrics, XAI, or application command |

Acquisition writes to a temporary archive, verifies 13,130 bytes and archive
SHA-256 `0b40d40e…4551`, inspects safe ZIP names, reads only
`SouthGermanCredit.asc`, verifies 47,940 bytes and raw SHA-256
`5f363343…562f`, then atomically publishes the raw file. An existing valid file
is reused; an invalid one is refused rather than replaced. Failed staging files
are removed. Errors state the failed rule and safe identity/context without
printing records.

The raw target remains `kredit` (`0=bad`, `1=good`). `adverse_event` deliberately
inverts that coding (`0→1`, `1→0`) so the analytical positive class is the
adverse outcome. Label orientation matters because reversing it would reverse
the meaning of later recall, precision, errors, and explanations. The verified
file contains 300 adverse and 700 non-adverse rows; these are dataset counts,
not model results or source-population prevalence.

Rows receive `sgc-0001` through `sgc-1000` from one-based source position only
after raw-hash verification. The key is stable across repeated loads and all
role/split views, but `model_input()` excludes it. `StratifiedShuffleSplit`
with test fraction 0.20 and seed 42 locks 800 training and 200 test keys. The
training partition has 240 adverse/560 non-adverse rows; test has 60/140.
Stratification preserves minority-class support, while the canonical sorted
train/test-key JSON checksum
`af26b6036c6958a2dec48362fb1bfb075fca2ad7e482ed48ee7a49d7ec6d994b`
detects membership drift. The contract commits test keys only; training is the
complement, and no row-level feature or target value is stored.

This random split cannot establish temporal generalisation or entity
generalisation: the source has neither dates nor customer/account identifiers.
The locked held-out membership may not influence encoding, preprocessing,
models, metrics, thresholds, or other choices. Phase 3 creates membership only
and does not inspect model performance.

The ordinary suite uses clearly synthetic data and in-memory BZIP2 archives, so
48 tests run without network access. Boundary tests cover configuration, both
target labels, roles, forbidden model fields, acquisition and cleanup,
schema/categories/duplicates, key stability/alignment, canonical serialization,
deterministic partition counts and all split-lock rejection paths. One
explicitly enabled `live_data` integration test runs official acquisition
through locked split verification. Two clean Python 3.12 environments installed
the exact lock; the second installed Aletheia with `--no-deps
--no-build-isolation` before repeating pip, lint, format, and offline checks.

## Implemented Phase 4 Training-Only Baseline

Phase 4 comes after the data foundation because learned transforms and model
scores are meaningful only after dataset identity, target orientation, feature
roles, and split membership are fixed. Without fold-local preprocessing, each
validation fold could influence its own scaling and produce optimistic evidence.
Without a dummy reference, a learned score would lack a no-signal sanity check.

`configs/experiments/baseline_v1.toml` freezes dataset, policy, split, target,
preprocessing, model, CV, metric, and threshold choices. `config.py` validates
those values against the Phase 3 contracts. `ml/preprocess.py` constructs one
`ColumnTransformer`: `StandardScaler` handles `laufzeit` and `hoehe`, while
`OneHotEncoder(handle_unknown="error")` handles the other 13 approved fields.
Integer category codes are labels or coarse ordered bands, not justified
equal-distance quantities, so one-hot encoding is the conservative baseline.
Categories come from the approved contract, not observed full-data values; the
documented but unobserved `verw=7` therefore keeps a stable output column.

The transformed schema contains 59 columns: two scaled values and 57 indicator
columns. `expected_transformed_schema()` deterministically maps every output
name back to one of the 15 original predictors. Audit-only fields (`famges`,
`alter`, `gastarb`), excluded fields (`telef`, `bishkred`), both targets, and
`row_key` never enter the estimator matrix.

`ml/models.py` exposes exactly two unfitted choices. The dummy uses the training
fold's class prior and tests whether a learned model extracts signal beyond
prevalence. Logistic Regression uses L2 regularization, `C=1.0`, `lbfgs`, no
class weights, and `max_iter=1000`. L2 regularization discourages excessively
large coefficients; it does not make the model causal or automatically
calibrated. No hyperparameter or threshold search occurred.

`ml/evaluate.py` builds one shared `StratifiedKFold` assignment with five folds,
shuffle enabled, and seed 42. Each model/fold receives a fresh pipeline, fitted
on 640 fold-training rows and evaluated on 160 validation rows. Validation row
keys are recorded only as SHA-256 membership checksums. Class-1 probabilities
are selected by finding label `1` in `classes_`, not by assuming a column
position. `ml/baseline.py` verifies the complete Phase 3 split, selects only its
800 training keys, calculates the result twice, requires exact deterministic
payload equality, and only then publishes a manifest.

`experiments/manifest.py` records data/config/split/training/fold identities,
all fold and aggregate metrics, transformed-feature lineage, environment, Git
state, limitations, and explicit absence of held-out evaluation/fitted model.
`experiments/artifacts.py` writes and validates in a staging directory, flushes
the JSON, then atomically renames it; an existing run ID is refused. The run
directory is ignored and contains only `manifest.json`.

### Phase 4 Verification Evidence

Recovery preserved the existing configuration, source, tests, ADR, and published
run. On Python 3.12.10, the final required checks were:

```text
python -m pip check
  exit 0: No broken requirements found.
python -m ruff check .
  exit 0: All checks passed!
python -m ruff format --check .
  exit 0: 43 files already formatted
python -m pytest -p no:cacheprovider --basetemp data/processed/pytest-phase4-final -m "not live_data"
  exit 0: 66 passed, 1 deselected, 25 warnings in 6.52s
python -m aletheia.ml.baseline --raw-file data/raw/SouthGermanCredit.asc
  exit 0 in the preceding recovery: two identical calculations before publication
```

All 25 pytest warnings concern the task's explicit L2 parameter deprecation.
The ordinary integration fixture exercises synthetic predictors through CV and
manifest publication; the explicitly executed local baseline additionally
exercises verified Phase 3 loading, validation, roles, and locked membership.
Tests inspect exact feature allocation/domains, unknown-category refusal,
`verw=7`, fold-local fitting, fold coverage/disjointness, class orientation,
known metrics, model settings, deterministic reruns, manifest scope and shared
folds, and atomic publication/overwrite refusal. Inspect `tests/unit/test_*.py`
for these boundaries and `tests/integration/test_baseline_pipeline.py` for the
synthetic CV-to-manifest path.

Two fresh calculations during final recovery matched each other and the
preserved manifest exactly. A temporary in-memory evaluation guard verified two
800-row inputs, 15 predictors, and no locked held-out key. Deterministic result
payload SHA-256:
`84f5a13a12ee8a7d01df0959659deeab0f609f724869dd8cccf9fd2b8aa0bf1b`.
The run contains only `manifest.json`; its held-out flag is false and fitted-model
reference is null. `git check-ignore -v` confirms the raw file and run manifest
are ignored. `git diff --check` passes; only authorized paths appear in status.
Exact final replay and review commands are in `SUPERVISOR_HANDOFF.md`.

The manifest's Git diff checksum records its creation state, before subsequent
documentation edits. It is preserved as historical evidence rather than changed
to pretend it describes the later documentation state. Base HEAD remains
`65f83c668a4f745ffd6dc74a9e21b81cb059712c`.

### Phase 4 Repair Verification (2026-10-03)

The repaired offline integration test now calls `run_baseline()` with 1,000
synthetic raw rows and temporary dataset/configuration/split identities. The
fixture uses actual Phase 3 loading, schema validation, target mapping, feature
views, split generation, writing/loading, and verification. Only the dataset
identity provider is replaced; experiment validation, orchestration, CV,
manifest construction, and publication execute their real code. Before each of
the two evaluator calls, a guard requires exactly the complete verified set of
800 unique training keys, no verified held-out key, and aligned predictor/target
rows. The synthetic 200-key holdout crosses the old row-800 boundary, making a
prefix/suffix substitution fail. Both calculations produce identical payloads;
both models share five fold checksums. Nested manifest checks exclude held-out
results and prediction fields, retain the false held-out flag and null model
reference, and require a run containing only `manifest.json`. Republishing the
same run is refused without changing its manifest.

Verification: pip check and Ruff lint passed; format check reported 43 files
already formatted. The targeted test passed (1 passed, 10 warnings in 1.50s);
the complete offline suite passed (66 passed, 1 deselected, 25 warnings in
5.88s). Warnings are the existing approved L2 deprecation. Temporary publication
was inspected directly. No production baseline was rerun, held-out performance
calculated, or preserved metric changed. This repair is pending external review;
it supplies software-boundary evidence, not new empirical ML evidence.

## Data Flow

**Current healthcare flow:** verified source/cohort/roles → locked patient split
→ training-only nested group CV and calibration → frozen selection/fitted artifact
→ one locked model evaluation → unchanged calibrated model with training-only
XAI/stability and feasibility assessment → one separately guarded subgroup audit
→ aggregate evidence and checksummed manifest. This documentation repair reads
saved evidence only; it repeats none of these empirical stages.

**Historical credit flow:** the Phase 3–4 flows below and their deferred final
fit/holdout/XAI statements describe the secondary benchmark only.

The implemented Phase 3 flow is: official source → temporary download → archive
size/hash verification → exact safe member read → raw size/hash verification →
atomic raw publication → strict load/schema/domain validation → explicit
adverse-target mapping → aligned feature-role views → stable row keys → locked
stratified membership. Each stage exists to prevent an unverified earlier
assumption from contaminating all later work.

The implemented Phase 4 training flow continues with: verified fixed membership
→ select the 800 training keys → create shared five-fold membership → build a
fresh preprocessing/model pipeline per fold → fit only on that fold's 640
training rows → score its 160 validation rows → calculate class-1 metrics →
repeat the complete calculation → compare deterministic payloads → publish an
immutable manifest. Every stage exists to prevent validation or held-out
information from entering a learned transform or choice. Final fitting,
held-out evaluation, XAI/audit analysis, and model serialization remain future
work requiring separate approval.

The future inference flow is: raw request → the same schema and feature policy →
the exact frozen preprocessing/model pipeline → score/prediction → optional
exact-run explanation/counterfactual → audit event → response. Inference never
refits or independently interprets source codes.

## Implementation Timeline

### Phase 0 — Project Analysis and Scope Validation

The broad enterprise proposal was narrowed before architecture/tool commitments
because dataset validity and research design must govern later work. Established:
users, requirements, research questions, data/model criteria, evaluation/XAI
boundaries, risks, MVP, and deferred work. Concepts: supervised tabular
classification, held-out evaluation, cross-validation, leakage,
intrinsic/post-hoc interpretability, counterfactuals, stability, and subgroup
measurement. Result: a coherent research scope was documented without
implementation. Phase 0 is externally supervisor-approved.

### Phase 0 Repair — Documentation and Governance Consistency Repair

This repair followed an external `FAIL — FIX BEFORE CONTINUING` finding on the
first Phase 0 attempt. It reconciles scope terminology, research-first order,
stability status, task authority, Git authority, and the measurable Phase 0
record. A Definition of Done and external approval gate matter because written
planning is only trustworthy when it names the evidence needed to advance and
does not silently authorize later work. The repair is externally
supervisor-approved.

### Phase 1 — Dataset Selection and Data Audit

**What was accomplished:** Four official UCI candidates were compared using
explicit gates, their permitted raw files were inspected outside the repository,
and South German Credit was selected and audited. Its identity,
structure, target, feature roles, leakage risks, split direction, and conditional
fairness/counterfactual feasibility were documented.

**Why this came now:** Dataset evidence is needed before architecture or
modelling so later decisions use the actual target, semantics, chronology, and
constraints rather than guesses.

**Concepts involved:** provenance and licensing, observation unit, selection
bias, outcome timing, audit-only versus prediction features, leakage review,
stratified splitting, subgroup support, and counterfactual feasibility.

**Result:** Phase 1 and South German Credit's academic Research MVP suitability
are externally supervisor-approved. The approval does not validate any future
model or real-lending use.

### Phase 2 — System Architecture, Technology Selection, and Roadmap

**What was accomplished:** A proposed research-first modular-monolith design was
documented with component contracts, dependency direction, shared
training/inference preprocessing, dataset invariants, local artifact manifests,
XAI/counterfactual/stability/fairness boundaries, a minimal technology matrix,
planned repository structure, tests/errors/security, a gated roadmap, and one
ADR.

**Why this came now:** The approved data audit supplies the target, feature
roles, split limitations, and semantic constraints needed to design correct
boundaries. Designing them earlier would have encoded guesses.

**Alternatives/trade-offs:** Notebook-centric work was rejected as the canonical
pipeline because of hidden state; a heavily layered architecture would add
ceremony; framework-first web design would couple evidence to delivery; and
microservices/MLflow/database infrastructure have no present scale or workflow
need. The modular monolith trades built-in distributed isolation and query
features for simplicity, inspectability, and one source of ML truth.

**Result:** Phase 2 was completed without implementation and subsequently
externally supervisor-approved at commit
`52be4130c8c4745c9f86f3b26a93497c3beeb2ff`.

### Phase 3 — Reproducible Data Foundation

**What was accomplished:** The fixed dataset/configuration contracts, controlled
official acquisition, strict loader/validator, explicit adverse mapping,
disjoint role views, stable keys, deterministic locked split, data-only CLI,
minimal Python package, exact dependency lock, and offline/live tests were
implemented and verified.

**Why this came now:** The approved architecture requires trustworthy data and
membership before any learned transform or estimator. This milestone turns the
Phase 1 audit into executable refusal boundaries while leaving modelling sealed.

**Alternatives/trade-offs:** Requests was unnecessary; standard-library
acquisition plus a certificate-validating Windows system fallback handled the
actual environment. Content-derived row hashes could hide duplicates or change
when values change, so transparent source-position keys were selected and bound
to the approved raw hash. Storing both partitions would duplicate information,
so the contract stores test keys and derives training as the complement. A
random stratified split preserves class support but accepts the inability to
test time/entity generalisation.

**Concepts and result:** cryptographic identity, fail-closed validation,
semantic versus storage type, label orientation, audit-only separation,
deterministic stratification, canonical serialization, dependency locking, and
offline/live integration testing. The project can reproduce and verify the
exact data boundary consumed by Phase 4.

### Phase 4 — Leakage-Safe Baseline Pipeline

**What was accomplished:** A fixed training-only experiment configuration,
explicit preprocessing schema, dummy reference, regularized Logistic
Regression, shared five-fold CV, predeclared metrics, deterministic calculation,
and immutable manifest publication were implemented and verified. The verified
local run is `baseline-v1-20261003T044245447896Z-f528b34971`.

**Why this came now:** Phase 3 had already frozen identity, label orientation,
feature roles, and the 800/200 boundary. Phase 4 could therefore establish a
simple reference without spending the held-out evidence or adding nonlinear
models. Without it, later models would have no interpretable or no-signal
comparison.

**Alternatives and trade-offs:** Fitting preprocessing once before CV was
rejected as leakage. Inferring categories from observations was rejected because
the schema would lose documented empty levels. Numeric ordinal treatment was
rejected because equal spacing is not source-supported. Search, threshold
tuning, final fitting, and held-out evaluation were deferred. One-hot encoding
expands 15 fields to 59 columns, but provides stable, explicit semantics.

**Concepts and result:** fold-local fitting, one-hot encoding, feature scaling,
regularization, stratified cross-validation, ROC-AUC, calibration-sensitive
losses, deterministic evidence, and atomic immutable publication. The project
now has a verified training-CV reference, not a final model or held-out result.
Phase 5 remains unauthorized.

### Phase 4 Repair — Verify the Locked Data Boundary

**Milestone and ordering:** External review blocked Phase 4 on a false holdout
assumption and an incomplete integration path. Repairing those checks comes
before any further modelling because passing tests must actually defend the
approved split. `tests/conftest.py` adds temporary synthetic raw/config/split
inputs; `tests/integration/test_baseline_pipeline.py` replaces direct prepared-
feature evaluation with complete `run_baseline()` orchestration and guards.

**Choice and alternatives:** Membership from the Phase 3 verified lock replaces
invented row ranges. Calling only `evaluate_models()` would leave training-row
selection untested; using real raw data would make the ordinary test dependent
on local data availability. Synthetic temporary inputs exercise the complete
path offline while accepting that they do not establish real model performance.
No architecture or dependency changes were needed. Reconsider only if a future
approved dataset/protocol changes the contract or orchestration boundary.

**Concepts and result:** Contract verification, exact set equality, row alignment,
integration testing, and immutable publication. The test now proves that all and
only verified training keys reach CV; Phase 4 still awaits supervisor approval
and Phase 5 remains blocked.

## Technical Decisions

**Research-first, not platform-first:** Data and ML/XAI evidence precede APIs,
dashboards, persistence, tracking, and deployment. Trade-off: a full-stack demo
is postponed; reconsider after reproducible results exist.

**Credit-risk tabular reference:** supports understandable audits and local
classical ML, while conclusions remain dataset-bound and not production lending
validation. Reconsider if no dataset meets the criteria.

**Logistic baseline plus limited nonlinear models:** provides a real
performance/transparency comparison without an algorithm catalogue; extend only
when another family answers a distinct question.

**Conditional fairness:** avoids proxy-based or underpowered claims, but the
first study may have no fairness result.

**Research-first modular monolith:** one package and process keep data, fitted
pipeline, evaluation, and audit evidence consistent while future delivery
adapters depend on the core. The accepted trade-off is fewer built-in
concurrency/scale boundaries; reconsider only when real workload, team, or
deployment evidence requires them.

**Immutable local experiment artifacts before MLflow/database:** a versioned
JSON manifest and checksummed run directory are sufficient for inspectable
single-user research. Reports name exact runs and never trigger training.
Reconsider when concurrent users, remote storage, query volume, or approval
workflows appear.

**Locked test membership before modelling:** test row keys are committed once
and tied to the raw hash, role-policy version, target mapping, split parameters,
class counts, and canonical membership checksum. A fresh random split was an
alternative, but it could permit accidental split shopping or drift. The cost
is that a later authoritative data revision needs an explicit new contract.

**Training-only baseline protocol:** exactly one prior dummy and one fixed L2
Logistic Regression use identical five-fold training membership and a fresh
pipeline per fold. Explicit contract categories keep the schema stable and
unknown values fail. The accepted trade-offs are a wider 59-column matrix, no
ordinal-distance assumption, no tuning, and no final fitted artifact. Reconsider
only through a new approved experiment version; ADR 0002 contains the full
decision record.

## ML Experiments

### Healthcare model v1 — Nested patient-group CV and locked holdout

The full verified experiment record, including dataset identity, 13 predictor
meanings, fold-local preprocessing, four bounded model families, grids, five
outer and three inner patient folds, raw/sigmoid calibration, metrics, result
interpretation and limitations, is in the Macro Milestone 2 section above.
The selected protocol was sigmoid-calibrated Histogram Gradient Boosting with
15 leaves, 30 iterations and minimum leaf size 40. Outer mean AP was 0.199591;
the one held-out AP was 0.202633. The historical holdout is an independent
patient split for this one frozen protocol, not clinical validation. The
machine-readable per-fold and calibration evidence is in the ignored
`artifacts/healthcare-model-v1` records, not copied into this document.

### Baseline v1 — Training-Only Cross-Validation

**Objective and identity:** Determine whether fixed Logistic Regression extracts
signal beyond a class-prior dummy without using the held-out partition. Dataset:
South German Credit raw SHA-256 `5f363343…562f`; feature policy 1.0; split
checksum `af26b603…94b`; training checksum `f528b349…53e`; 800 training rows
(240 adverse, 560 non-adverse); positive class `adverse_event=1`.

**Features and preprocessing:** 15 approved prediction features. `laufzeit` and
`hoehe` are standardized within each fold. Thirteen categorical/ordinal fields
are one-hot encoded from explicit approved domains. There is no imputation,
resampling, target encoding, feature selection, or polynomial expansion.

**Models and validation:** `DummyClassifier(strategy="prior")`; Logistic
Regression with L2, `C=1.0`, `lbfgs`, `class_weight=None`, and
`max_iter=1000`. Five-fold `StratifiedKFold`, shuffled with seed 42, supplies
the same memberships to both models. Threshold 0.5 is descriptive only.

Aggregate values are mean ± population standard deviation across five
validation folds:

| Metric | Dummy | Logistic Regression | Meaning in this experiment |
|---|---:|---:|---|
| ROC-AUC | 0.5000 ± 0.0000 | 0.7718 ± 0.0340 | Ranking of adverse above non-adverse; not calibration |
| Average precision | 0.3000 ± 0.0000 | 0.6048 ± 0.0653 | Precision-recall ranking, prevalence-sensitive |
| Balanced accuracy | 0.5000 ± 0.0000 | 0.6676 ± 0.0339 | Mean of adverse recall and specificity at 0.5 |
| Adverse recall | 0.0000 ± 0.0000 | 0.4708 ± 0.0339 | Fraction of actual adverse cases flagged |
| Specificity | 1.0000 ± 0.0000 | 0.8643 ± 0.0363 | Fraction of non-adverse cases correctly not flagged |
| Precision | 0.0000 ± 0.0000 | 0.6034 ± 0.0812 | Adverse predictions that were adverse; prevalence-sensitive |
| F1 | 0.0000 ± 0.0000 | 0.5282 ± 0.0513 | Harmonic mean of adverse precision and recall at 0.5 |
| Log loss | 0.6109 ± 0.0000 | 0.5216 ± 0.0419 | Penalizes wrong/confident probabilities; lower is better |
| Brier score | 0.2100 ± 0.0000 | 0.1715 ± 0.0167 | Mean squared probability error; lower is better |

The dummy assigns the 0.30 fold-training adverse prior, so threshold 0.5 labels
every validation row non-adverse: recall, precision, and F1 are zero while
specificity is one. Logistic Regression ranks cases materially better within
these training folds and improves both probability losses. This is reference
evidence, not final selection: no nonlinear model was compared and the held-out
200 rows were not scored.

Fold-to-fold standard deviations show variability, not a confidence interval or
guarantee. Because training-fold scores were not recorded, this experiment
cannot quantify a train/validation generalization gap and cannot diagnose
overfitting conclusively. CV variation and regularization offer limited evidence
only. The source deliberately oversamples adverse outcomes from its historical
population, so precision, average precision, Brier/log loss interpretation, and
raw probability calibration do not transfer directly to population lending.

**Error semantics and conclusion:** A false negative is an actually adverse
contract predicted non-adverse; a false positive is an actually non-adverse
contract predicted adverse. Both matter, but no defensible monetary cost ratio
exists here. Threshold 0.5 was not tuned and is not an operational lending
recommendation. The result justifies retaining Logistic Regression as the
interpretable reference for a separately approved comparator phase.

## Important Problems Encountered

### Macro Milestone 2 recovery and selection serialization

The Macro Milestone 2 section above documents the actual symptoms, causes,
failed attempts, fixes and verification for three material issues: histogram
boosting's hidden row-level early stopping, interrupted training calculations
without reusable checkpoints, and a JSON family-key ordering mismatch that
made the strengthened selection guard refuse before a holdout claim. It also
records an unnecessary interruption caused by misreading a configuration
line. No incomplete output was promoted to a completed result; the final
guarded evaluation used verified training, selection and artifact records.

### Phase 4 Integration Test Used a False Holdout Boundary

**Problem/symptom:** The original integration test invented `sgc-0801` through
`sgc-1000` as held-out keys and supplied prepared first-800-row features directly
to `evaluate_models()`. Its disjointness assertion passed without checking the
locked membership. The actual stratified lock scatters held-out keys throughout
the source file. A training-selection regression could therefore include real
held-out rows, omit training rows, and still pass that test; resulting evidence
could be contaminated without detection. Review found a test gap, not evidence
that production evaluation had leaked.

**Root cause/fix:** The test conflated stable source-row numbering with random
partition membership and bypassed the code responsible for selecting rows.
Phase 3 split-contract generation/loading/verification now supplies the expected
membership. `run_baseline()` executes raw loading → schema validation → target
mapping → role enforcement → locked split verification → training selection →
real training-only CV → manifest creation → immutable publication. A capture
guard checks set equality, uniqueness, 800 rows, held-out disjointness, and
feature/target alignment before allowing evaluation. Both synthetic partitions
cross row 800. Directly prepared predictors alone were insufficient evidence;
the real orchestration test passed targeted and full checks noted above.

**Recovery and lesson:** No source defect was exposed and no production artifact
or metric changed. An initial repair patch was rejected because two operations
targeted one file; status confirmed no changes, then separate valid updates
succeeded. A delete-based handoff rewrite failed without changing its file;
an in-place patch completed the rewrite. A later documentation patch also
failed on unmatched context and was corrected without changing earlier results.
Prevent recurrence by testing the selection boundary against verified
membership rather than plausible-looking IDs. Inspect `data/split.py`,
`ml/baseline.py`, `tests/conftest.py`, and
`tests/integration/test_baseline_pipeline.py` to explain the correction.

During Phase 1, Windows `Expand-Archive` could not extract BZIP2 entries, so
Python's standard `zipfile`
was used in the temporary audit directory. An initially guessed South German
archive URL returned 404 before the official `+update` URL was used. More
importantly, one sentence in the linked report appears to reverse the target
codes; UCI's distributed code table, R reader, and observed 300/700 counts agree
on `0=bad`, `1=good`. The lesson is to cross-check narrative documentation
against the exact distributed artifact rather than silently choosing a label.

Phase 2 identified model serialization as an architectural risk rather than
silently selecting pickle/joblib. Such formats can execute code and are not
supported across mismatched scikit-learn versions. The design therefore requires
trusted checksummed artifacts, exact environment metadata, and a later
compatibility decision between skops and a restricted local joblib fallback.

During Phase 3, Python's OpenSSL trust path rejected the official UCI HTTPS
chain as expired even after native roots were added, while Windows'
certificate-validating `Invoke-WebRequest` downloaded bytes with the approved
hash. Acquisition now tries verified Python TLS first and uses a Windows
Schannel-backed PowerShell fallback only for certificate-verification failure;
TLS verification is never disabled. This preserves the fixed URL and avoids
adding Requests/certifi for one platform-specific trust issue.

The first offline test run exposed two test/validation-order mistakes: an
archive mutation changed size before the checksum boundary could be exercised,
and aggregate target counts masked a duplicate-row refusal. The test now changes
one archive byte without changing size, and duplicate checks run before target
count arithmetic. The lesson is that a negative test must reach the exact
boundary it names, and validation order should return the most specific useful
failure.

Phase 3 also exposed several environment and governance failures. Pytest could
not create its default temporary directory under the repository on this Windows
environment; using explicit `--basetemp data/processed/...` and disabling the
cache kept temporary writes in an approved ignored path. PowerShell syntax was
initially sent to Command Prompt, producing a syntax failure rather than running
the intended check; subsequent commands named the correct shell. A stray
untracked file literally named `git` appeared in the status gate and was removed
before continuing because it was outside the approved task. These symptoms did
not change data or results. The prevention lesson is to treat the exact shell,
temporary-write location, and Git status as reproducibility inputs, not setup
details.

The Phase 3 handoff initially retained stale architecture wording that described
implemented paths as future work. A repair reconciled `ARCHITECTURE.md` with the
committed source. That repair then overclaimed quantitative-range enforcement:
the configuration loads observed ranges, but validation enforces exact file
identity through byte size/SHA-256 and does not compare general quantitative
values with those ranges. Code inspection and targeted text searches verified
the correction. The interview lesson is that a checksum proves byte identity;
it is not the same control as an explicit per-field range rule.

No meaningful Phase 4 correctness bug was found in the recovered implementation:
all offline tests passed before documentation completion and the real training-
only run reproduced exactly. The recovery did expose tooling and documentation
problems: simultaneous shell creation failed with `CreateProcessWithLogonW
failed: 1056`; sequential read-only calls succeeded. Several patches failed
because PowerShell's default decoding displayed UTF-8 symbols as mojibake, and
the copied context did not match the file. The failed patches made no changes;
explicit `Get-Content -Encoding UTF8`, fresh surrounding lines, and smaller
`apply_patch` edits resolved the mismatch within the sandbox. The user required
stopping on patch failure, and work resumed only after renewed direction.
Verification used Git diffs and whitespace checks. The lesson is to separate
display decoding from actual file corruption and inspect current text before
patching; do not bypass a failed patch with an unsandboxed write. A later inline
Python verification command also failed before running with `SyntaxError:
invalid decimal literal` because Windows PowerShell stripped nested quotes.
Transporting the code as byte values worked; a readable replay using PowerShell
`--%` then passed and is recorded in the handoff. This was shell argument
handling, not a model/data defect; no result was produced by the failed command.

Scikit-learn 1.9 emitted a deprecation warning for
the explicitly required `penalty="l2"` argument. Phase 4 preserves the approved
configuration; a later approved version must revisit the equivalent API before
scikit-learn 1.10 rather than silently changing this experiment.

## Concepts Learned Through This Project

**Patient-group nested CV.** Simple explanation: inner folds choose settings;
outer folds estimate performance on patients unseen by that selection.
Where used: `modeling.group_folds` and `experiment.training_evidence`.
Why it mattered: repeated encounters from one patient would otherwise leak
between fitting and validation. Be able to explain group disjointness, the
five/three-fold roles, why fold SD is not a confidence interval, and why this
still lacks hospital/time validation.

**Probability calibration and ranking.** Simple explanation: sigmoid maps a
model's raw probabilities toward observed frequencies using predictions for
patients excluded from the base fit. Where used: `oof_sigmoid` and
`evaluation.sigmoid_fit`. Why it mattered: class-weighted Logistic Regression
ranked reasonably but had raw Brier 0.206511; sigmoid reduced it to 0.097854.
Be able to explain Brier/log loss, why monotonic mapping preserved AP/ROC-AUC,
why in-sample calibration leaks, and why held-out calibration is still not
clinical validation.

**Patient-cluster bootstrap.** Simple explanation: repeatedly sample patients
with replacement and retain all their encounters together. Where used:
`evaluation.cluster_intervals` on the single held-out vector, with 500 repeats
and seed 4242. Why it mattered: encounters from one person are dependent.
Be able to explain the sampling unit, interval interpretation, and why the
interval cannot measure transport to a new hospital or decade.

**Immutable selection and artifact identity.** Simple explanation: save the
training-based choice before test prediction, then bind the fitted model to
protocol and software hashes. Where used: `experiment.run`, `evaluate_once`
and `load_trusted_artifact`. Why it mattered: it prevents accidental reruns,
silent result replacement and loading an unrelated model. Be able to explain
what the claim protects, why a failed claim must remain, why joblib requires
trusted-local checksum verification, and what the JSON-order recovery taught.

**Contract-based integration testing:** test the real caller-to-component flow
against a verified contract, rather than preparing inputs that skip the risky
boundary. The repaired baseline test captures evaluation inputs before CV.
This matters because a correct evaluator can still receive the wrong rows.
Be able to explain why source-row identity differs from partition membership,
why set equality must be paired with uniqueness/count, and why synthetic
software evidence does not establish real-world model performance.

**Intrinsic vs post-hoc interpretability:** coefficients/rules expose model
structure directly; feature attribution estimates influence for a fitted model.
Neither proves causality. Planned in the comparison.

**Data leakage:** training gets unavailable future/target information and
evaluation becomes falsely optimistic. Prevent with training-only transforms,
untouched tests, and time/group splits where appropriate.

**Global vs local explanation:** global evidence describes general model
patterns; local evidence concerns one prediction. A global ranking cannot
explain an individual decision.

**Counterfactual:** constrained feature changes that alter a model class; not a
guarantee of a real-world outcome.

**Dataset selection before architecture:** the selected data fixes what one row
and the target mean and exposes timing, feature, fairness, and recourse limits.
Architecture designed earlier could encode the wrong target or unsupported
capabilities. Phase 1 uses this ordering without designing architecture.

**Prediction feature versus audit-only attribute:** a field may be retained to
measure subgroup behaviour without being supplied to the classifier. In the
Phase 3 policy, age, combined personal-status/sex, and foreign-worker status are
audit-only; that does not make their fairness use automatically valid.

**Modular monolith:** independently understandable modules run in one package
and process. Here it prevents unnecessary distributed infrastructure while
preserving data, ML, audit, and delivery boundaries.

**Dependency direction:** outer delivery code may call the research core, but
the core cannot import API/UI/database code. This keeps research results usable
without a web application and prevents duplicate preprocessing.

**Fitted pipeline contract:** preprocessing and the estimator form one
versioned artifact. Training, inference, and explanations identify the same
pipeline and feature map, preventing a separately reimplemented inference path.

**Immutable run manifest:** every result records its dataset hash, target/feature
policy, split, configuration, environment, code revision, artifact hashes, and
limitations. Publishing a new run instead of overwriting avoids result drift.

**Cryptographic data identity:** size catches truncation cheaply and SHA-256
binds processing to exact bytes. Phase 3 checks both archive and raw member so
the same filename cannot silently mean different data.

**Label orientation:** the numerical source code is not automatically the
analytical positive class. Here raw `0` means bad, so explicit inversion makes
`adverse_event=1`; tests preserve the truth table and original `kredit`.

**Canonical serialization:** logically identical membership must produce the
same bytes before hashing. Phase 3 sorts train/test keys and uses UTF-8 JSON with
sorted keys and no optional whitespace, then tests the exact byte string.

**Stratified holdout:** random partitioning preserves target proportions so both
partitions retain adverse cases. It improves class support but cannot substitute
for temporal or entity-aware evaluation.

**Fold-local preprocessing:** each validation fold must behave like unseen data.
Phase 4 creates a new scaler, encoder, and model for every fold, fitting them on
640 fold-training rows only. Fitting once on all 800 rows would leak validation
statistics even without using the held-out test set.

**One-hot encoding with explicit domains:** one indicator represents each
approved category instead of treating integer codes as equally spaced numbers.
Phase 4 supplies contract categories, so `verw=7` keeps a column even though the
approved file does not observe it, and unknown codes fail instead of silently
changing meaning.

**Regularized Logistic Regression:** the model combines transformed inputs into
a linear log-odds score; L2 regularization penalizes large coefficients. It is
an interpretable reference with a stable fixed configuration, not a causal model
or proof that its probabilities are calibrated.

**Feature scaling:** `StandardScaler` subtracts the fold-training mean and divides
by its standard deviation for duration and transformed amount. This prevents
their different numerical scales from distorting the L2 penalty. The fitted
statistics come only from that fold's training rows; validation uses transform
without refitting. Be able to explain why scaling categories as numeric values
would not replace one-hot encoding and why scaling before CV would leak data.

**Cross-validation and metric roles:** five stratified folds reuse training data
for five separate validation checks while keeping each check out of its own fit.
ROC-AUC measures ranking across thresholds. Average precision emphasizes adverse
ranking and is prevalence-sensitive. Recall/specificity/precision/F1 use the
descriptive 0.5 threshold. Log loss and Brier score assess probability error but
do not by themselves prove population calibration.

**False negatives and false positives:** here a false negative misses an
actually adverse case, while a false positive flags an actually non-adverse
case. Neither can be declared more costly without a defensible domain cost
model, which this historical dataset does not provide.

## Project Defence and Interview Preparation

**Why did the healthcare model win?** Histogram boosting had the highest
five-fold outer mean AP (0.199591); among protocols within the predeclared
0.005 AP margin, its sigmoid output had the lowest mean Brier (0.097624).
Follow-up: did the holdout select it? No; selection and final parameters were
frozen before its one-time held-out prediction.

**What does the held-out result actually mean?** It ranked positives above
negatives better than the prior dummy (AP 0.202633 versus training dummy outer
AP 0.113698), within one historical patient-disjoint split. At threshold 0.5,
it found only 12 of 2,240 positives, so it is not a usable clinical alert
rule. Follow-up: why not tune 0.5 after seeing this? That would use the locked
holdout for development and invalidate its independent-test role.

**What was the hardest recovery bug?** The strengthened guard compared an
ordered option list saved before JSON serialization with a recomputed list
after JSON had alphabetized dictionary keys. It refused before the holdout
claim. Candidate-order enumeration and a reordering regression test fixed
the false mismatch; hashes and complete records were verified before
continuing. Follow-up: why not rerun training? The complete saved training,
selection and artifact identities were independently proven, so only the
never-started held-out evaluation needed resumption.

**What must happen before clinical use?** Verify feature availability at the
actual discharge workflow, obtain contemporary external and temporal data,
define harm/cost-based thresholds with clinicians, prospectively validate,
and establish privacy, monitoring, governance and regulatory controls. None
is established by this retrospective model card.

**How do you test the held-out leakage boundary?** Capture the keys passed by
the actual orchestrator to evaluation and require exact equality with verified
training membership, uniqueness, the expected count, and disjointness from
verified holdout membership before fitting. Row numbers identify records;
they do not define a random split. Follow-up: why is disjointness alone weak?
It can miss omitted training rows; exact set equality plus row count detects
omissions and duplicates. This software test complements fold-local fit tests
and semantic feature review; it does not prove every kind of leakage is absent.

**Why is this not a prediction dashboard?** It compares performance with
explanation, constrained recourse, stability, and conditional subgroup evidence;
the interface is secondary.

**Why not highest accuracy?** Accuracy can hide class/error-cost trade-offs;
model choice needs a context-aware primary metric and audit trade-offs.

**How will leakage be prevented?** Review source semantics, split before
learned preprocessing, fit transforms only within training folds, and reserve
test data for final evaluation.

**Can it prove fairness or causality?** No; it reports bounded, dataset-specific
measurements and model-output explanations with limitations.

**Why choose South German Credit over the larger Taiwanese default dataset?**
The Taiwanese data has stronger sample and target chronology, but most useful
financial variables are historical at prediction time and its raw codes contain
undocumented categories. South German Credit has corrected, human-readable
contract features that better support the XAI and constrained-counterfactual
Research MVP, accepting age and representativeness limitations.

**What does one selected row represent?** One granted credit contract from a
1973–1975 southern German bank sample. It is not a rejected application, so the
data has historical screening/selection bias.

**Why use stratified random splitting?** The target is 70/30, but the file
has no dates or entity identifiers needed for temporal/group-aware splitting.
Stratification preserves class support; it cannot solve undisclosed repeated-
borrower or forward-time generalisation risks.

**Why a modular monolith instead of microservices?** The current research is
single-user and laptop-bound. Networked services would add contracts,
deployment, and failure modes without answering the research question. Small
modules in one Python package give testable boundaries and one source of ML
truth.

**How do training and inference stay consistent?** Both use one checksummed
fitted preprocessing/model pipeline and the same schema/feature-policy contract.
Inference may transform and predict but must never refit or recreate encodings.

**Why not start with MLflow, a database, or FastAPI?** Immutable local manifests
already provide the traceability the Research MVP needs. Those tools become
useful only when approved workflows require querying, concurrency, serving, or
lifecycle management.

**How are audit-only attributes kept out of predictions?** The versioned
feature policy creates disjoint model and audit views joined only by a stable
row key. Construction fails if audit-only, target, excluded, or unresolved
columns enter the model matrix.

**What should be inspected for Phase 2?** docs/ARCHITECTURE.md contains the
complete design, docs/decisions/0001-research-first-modular-monolith.md records
the decision trade-offs, docs/EXECUTION_PLAN.md contains the gates, and this
report is the concise defence record.

**Why verify both the archive and extracted raw file?** Archive identity proves
the downloaded package is approved; raw identity proves the exact member passed
to the loader is also approved. Both checks happen before publication.

**Why invert `kredit` into `adverse_event`?** The source uses `0` for bad and
`1` for good. Evaluation normally treats `1` as the event of interest, so an
explicit derived column prevents later metric-orientation errors while keeping
the source label traceable.

**Why exclude `bishkred`?** Its definition includes the current credit, but the
source does not establish when the count was recorded. Default-deny exclusion
avoids an unsupported availability assumption; it does not prove leakage.

**How is accidental test-split drift detected?** Verification regenerates the
seed-42 stratified membership and checks test keys, complement coverage, class
counts, dataset/policy/mapping identity, and canonical SHA-256.

**Does the fixed split prove future or customer-level generalisation?** No. The
source lacks dates and entity IDs, so it supports neither a temporal test nor a
grouped-by-customer test.

**Why one-hot encode the ordinal-looking integer fields?** Their source codes
represent categories or coarse bands; equal numeric distance is not established.
One-hot encoding avoids imposing that assumption and explicit domains keep all
59 transformed columns stable.

**How do you prove preprocessing stayed inside each fold?** Each fold constructs
a fresh `Pipeline(ColumnTransformer, estimator)`. Tests spy on both
`StandardScaler.fit` and `OneHotEncoder.fit` and observe ten fits of 80 rows in a
100-row synthetic test: five folds for each of two models, never a full-data fit.
The real protocol analogously fits 640 of 800 rows per fold.

**Why compare a dummy with Logistic Regression?** The prior dummy exposes what
class prevalence alone achieves: ROC-AUC 0.5 and no adverse predictions at the
0.5 threshold. Logistic Regression tests whether the approved features add
ranking signal while remaining a simple interpretable baseline.

**Why is ROC-AUC primary, and what does it miss?** It compares ranking over all
thresholds and is less tied to one 0.5 cutoff. It does not prove probability
calibration, choose an operational threshold, encode error costs, or remove the
dataset's prevalence limitation.

**What overfitting conclusion can Phase 4 support?** Only that validation scores
vary across five fold-local fits. Training scores were not recorded and the
held-out partition remains sealed, so a train/validation gap and final
generalization cannot be claimed.

**How is the run reproducible and auditable?** The ignored manifest records
dataset/config/split/training/fold checksums, model/preprocessing/CV settings,
per-fold and aggregate metrics, transformed lineage, environment, Git state,
limitations, and explicit absence of held-out evaluation or a fitted artifact.
The complete calculation ran twice and had to match before atomic publication.

## Semester Viva Preparation

**Healthcare basic:** What is the positive class? Why does a prior dummy's AP
roughly equal prevalence? What do TP=12 and FN=2,228 mean at threshold 0.5?
What does Brier score measure?

**Healthcare intermediate:** Why use `StratifiedGroupKFold` in both outer and
inner loops? Where are imputation and one-hot vocabularies fitted? Why does
sigmoid improve Brier without changing AP here? Why did class weighting hurt
raw Logistic Regression probability quality?

**Healthcare difficult:** Why must calibration scores be out-of-fold by
patient? Why is the 500-repeat patient bootstrap preferable to encounter
resampling? How could JSON key order trigger a false selection mismatch?
What evidence proves the one-time holdout was protected, and what cannot be
proved about generalization to a different hospital or decade?

**Repair questions:** Basic—does a row key specify its partition? No, the lock
does. Intermediate—why test the orchestrator? It selects the rows before CV;
testing the evaluator alone misses that boundary. Difficult—why combine exact
set equality, uniqueness, and count? Sets detect missing/extra membership but
discard duplicates, so all three checks are necessary.

**Basic:** Why can accuracy be insufficient? What is leakage? Why is raw
`kredit=0` mapped to analytical `adverse_event=1`? What does a prior dummy
predict? What do adverse recall, specificity, and precision measure?

**Intermediate:** Why Logistic Regression as a baseline? How do global/local
explanations differ? Why constrain counterfactuals? Why use stratification and
lock row membership before preprocessing? Why scale only two fields? How does
fold-local fitting prevent leakage? Why keep a column for unobserved `verw=7`?

**Difficult:** Why can explanations vary near a decision boundary? Why can
fairness metrics conflict? When is temporal/group-aware splitting necessary?
How would an immutable run manifest prevent result drift? Why must an explainer
identify the exact fitted preprocessor as well as the estimator? How does
canonical serialization make a membership checksum reproducible?
How does adverse oversampling affect probability interpretation? Why does ROC-AUC
not prove calibration? Why can CV standard deviation not diagnose overfitting
or serve as a confidence interval?

## Resume Evidence

Current interactive milestone: 13 explicitly mapped inputs, 28 new backend software tests, 66 frontend unit tests, one real browser journey and 15 accessibility state/width checks with zero violations. Complete regression: 304 collected; 303 passed, 1 deselected, 63 warnings in 3378.28s (0:56:18); 0 failed, 0 skipped; exit 0 (one invocation). No new empirical ML experiment. New image identities, security limits and exact checks are recorded above and in the handoff.

Historical Stage 3 snapshot: Current local Stage 3 evidence: three built/scanned images; five serving/test-identity containers; synthetic prediction/review/audit persistence and backup/restore; 33 proxy accessibility checks; five deployment unit tests; measured local startup/resources/HTTP latency. Exact counts, scope and remaining security findings are in the Stage 3 record and handoff above. Earlier research-only statements below are historical and do not describe current application deployment.

Current healthcare evidence: four model families, eight raw/calibrated
protocols, 79,808 training and 19,535 single held-out encounters, outer best
mean AP 0.199591, held-out AP 0.202633 and ROC-AUC 0.639473, one sigmoid
calibration technique, one sampled Shapley method used globally/locally,
80 recording-sensitivity comparisons, 15 supported subgroup estimates,
one no-recourse feasibility assessment, and 122 passing offline tests. These research-only facts predate the separately recorded local deployment measurements above. They support a bounded educational result, not a
clinical-performance resume claim. The figures below are **secondary South
German Credit benchmark evidence** from earlier phases.

Verified evidence: four official dataset candidates compared; one selected raw
file verified at 1,000 rows × 21 columns; one externally approved architecture
and two ADRs (ADR 0002 pending review); 15 prediction, three audit-only, and two
excluded fields; one locked 800/200 split; two fixed reference estimators compared
in five training-only folds; 59 transformed columns; Logistic Regression CV
ROC-AUC 0.7718 versus dummy 0.5000; 66 offline tests passed and one live-data test
deselected in the recovery check; two clean environments verified during Phase 3.
No held-out score, measured inference latency, implemented XAI method,
application, or deployment is claimed.

## Limitations

The healthcare evaluation is one retrospective, patient-disjoint split from
1999–2008 data. It lacks hospital IDs and encounter dates, so it cannot test
hospital transfer or future-time performance. Discharge-time availability of
each predictor still needs clinical workflow verification. The conservative
13-feature policy can omit useful signal; unknown-category zero encoding
loses detail. AP and precision depend on prevalence. The chosen 0.5 cutoff
has very low recall and no clinical cost justification. Calibration slope and
patient-cluster intervals describe this cohort only. The sampled XAI and
subgroup/stability evidence above is limited to its registered reference,
samples and methods; marginal hybrids, sparse groups, bootstrap zero-event
intervals and absent clinical recourse remain unresolved. No prospective
validation, clinical utility, fairness certification or deployment is established.

The paragraph below preserves limitations of the secondary credit benchmark.

South German Credit is old (1973–1975), geographically narrow, contains only
granted credits, oversamples bad contracts, has no row dates or identifiers,
and uses an unknown monotonic transformation for amount. Sex cannot be recovered
cleanly from its combined field, and only 37 rows are foreign workers, so robust
fairness analysis is not currently justified. Future results remain dataset- and
method-bound. Phase 4 validates training CV only; no held-out or production
validation exists. Its fixed random split cannot measure temporal or entity
generalisation. No final fitted model is retained. Threshold 0.5 has no validated
operational cost basis. A local artifact store has limited concurrency/querying;
cross-model explanations remain method-dependent; and dependency/version
controls reduce but cannot eliminate reproducibility risk.

## Future Work

**Useful next step, subject to approval:** external supervisor review of Macro
Milestone 4 Stage 0 and its implementation contract. A later task could examine clinically reviewed
feasibility or external validation with appropriate data and approval. This
report authorizes neither a later milestone nor the stashed credit work.

**Research extensions:** larger pre-registered XAI/stability samples, justified
conditional attribution, clinician-reviewed intervention feasibility, and
contemporary external/temporal evaluation. Existing subgroup evidence does not
remove the need for a reviewed disparity methodology.
Developer Code Intelligence and System Traceability is proposed and
unimplemented, placed after core data, modelling, evaluation/XAI, and basic
application boundaries stabilize; it requires its own approved task.

**Later extensions:** richer fairness/robustness methodology, monitoring,
deployment workflows, multi-user controls, integrations, and cloud operations.
