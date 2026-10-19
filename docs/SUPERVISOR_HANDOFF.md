# Supervisor Handoff - final Azure closure checks (2026-10-19)

## 1. Current milestone and status

Azure application acceptance and the remaining local/evidence gates are verified,
with the retained security findings below. **The milestone remains open until
the actual hosted GitHub Actions run passes.** The user explicitly granted a
one-time exception to the no-commit/no-push restrictions for this reviewed Azure
closure. Permanent governing files remain unchanged by that exception.

Public URL: https://frontend.whiteflower-9d03c62c.southeastasia.azurecontainerapps.io

Hosted continuation: reviewed commit `aa8c5179704956bc1964fed6e16ca1591678a154`
was pushed. [Run 39261782677](https://github.com/Ameya5006/Aletheia/actions/runs/39261782677)
failed before Azure login/deployment because approved Windows CRLF hashes differ
from Linux checkout LF bytes. A bounded checker repair preserves all approved
hashes and accepts only newline conversion; three regression cases pass. The
three non-secret Azure identifiers now also have encrypted repository settings
for automatic log masking, and the workflow reads those masked settings. Required
variables remain configured; no long-lived Azure credential was introduced.
The second [run 39262552221](https://github.com/Ameya5006/Aletheia/actions/runs/39262552221)
passed frozen checks, then had 7 passing tests / 39 errors because ignored frozen
fixtures were absent. No Azure deployment ran. The bounded repair retains the
deployment application tests, retrieves ten immutable-image fixtures after OIDC,
verifies all 42 release-file hashes, pins Python 3.12.10, and supplies disposable
runner PostgreSQL 18. PR checks remain artifact-free and cannot access Azure.
The isolated fixture-preparation check matched all hashes and rejected tampering.
The third [run 39263626020](https://github.com/Ameya5006/Aletheia/actions/runs/39263626020)
failed before checkout: runner parsing preserved single quotes around Docker's
health command (`unknown shorthand flag: 'U' in -U`, exit 125). A one-line double
quote correction preserves the health command; Azure was unchanged. Corrected
hosted execution is pending.

The fourth [run 39263931188](https://github.com/Ameya5006/Aletheia/actions/runs/39263931188)
passed runner setup/frozen checks but Azure OIDC returned `AADSTS700213` because
the trust used a name-only subject. GitHub emits the immutable owner/repository-ID
subject. Existing authenticated tooling updated the single trust to the exact
observed main subject after confirming repository IDs; issuer/audience and RBAC
were preserved. Readback matches `deployment/azure/github-oidc.json`; old trust
and failure evidence remain preserved. Hosted login must still be rerun.

## 2. What changed and why

- Formatted only `frontend/browser/cloud.spec.ts`; frontend formatting now passes.
- Finished API, MLflow and stopped-operator scans/SBOMs/licence inventories. The
  API archive was reused after blob/config/layer/ACR binding; only missing archives
  were exported. No image rebuild, push or app deployment occurred in this closure.
- Fixed `deployment/azure/ci-deploy.sh` to snapshot the revision actually serving
  100% traffic, rather than a possibly failed latest revision. Missing/ambiguous
  traffic fails before migration/update. Added three command-boundary regression
  tests in `tests/deployment/test_ci_rollback.py` and included them in the workflow.
- Removed literal non-secret Azure account identifiers from the pending workflow
  and role templates to follow CURRENT_TASK's handling rule. The workflow reads
  masked repository settings `AZURE_CLIENT_ID`, `AZURE_TENANT_ID` and
  `AZURE_SUBSCRIPTION_ID`; matching required Actions variables are verified.
  Role JSON templates require in-memory substitution of
  `${AZURE_SUBSCRIPTION_ID}`. Live identities, permissions and architecture did
  not change. All three required GitHub repository Actions variables were absent,
  were configured through existing authenticated tooling, and were read back to
  match the approved Azure identity. Their values were never printed or recorded.
- Reconciled README, PROJECT_REPORT, DEPLOYMENT_ARCHITECTURE and this handoff.
  Prior handoffs, original scan bytes, failed candidates and attempts are preserved.

## 3. Exact security evidence

| Image | Critical / High / Medium / Low / Unknown | Complete SBOM / licence entries |
|---|---|---|
| Frontend (preserved verified result) | 0 / 0 / 0 / 0 / 0 | 71 / 103 |
| api | 1 / 63 / 112 / 105 / 1 | 240 / 772 |
| mlflow | 1 / 63 / 112 / 105 / 1 | 240 / 772 |
| ci_operator | 1 / 63 / 112 / 105 / 1 | 240 / 772 |

All six remaining Trivy scan/SBOM commands exited 0. These are successful
evidence-generation commands, **not clean backend scans**. All 282 findings per
backend-family image remain recorded, without suppression. Raw CycloneDX 1.7
outputs contain 239 components and 771 licence entries each; separate complete
inventories add native SQLite 3.54.0 with its actual SHA-256 and public-domain
licence/source reference. Component/reference and exact-digest binding checks
passed. An external JSON-schema validator was not installed/run; licence
inventory is not legal clearance.

The critical zlib finding concerns MiniZip; the inspected binary/library and
affected symbol are absent, consistent with Debian Bookworm's published note.
Six fix-version findings (four HIGH, two MEDIUM) are pip-vendored packages.
Installed top-level setuptools 84.0.0 and urllib3 2.8.0 are fixed; pip 26.2.1
is still the latest official release checked. No user-directed installer path
exists in reviewed serving entrypoints. Other distribution findings have no
fixed Bookworm version reported and remain residual risk. No unsupported vendor
surgery or unrelated dependency upgrade was made. Inspect every disposition in
`artifacts/azure-preflight/final-closure-20261019/*-dispositions.json`.

Exact current ACR index digests:

- Frontend: `sha256:12176c6a16302f1f4208c7878ead164701c08704ad3620fddc744ada63547416`
- API: `sha256:06f7bb2229fb1c77b6561afaeccdbf51c9a0243005fb0ea647a8d6de44f683ab`
- MLflow: `sha256:062f3fb2700fa152d6cab44aeec154f44ade7c2116f63038dca1ccd38342ab5d`
- Stopped operator: `sha256:3f6b5f2fc264d26c57da3d9b87174eae37438c7bfdbc2f0ef22164ddb65ec8dd`

Frontend scan SHA-256, corrected from an earlier 65-character transcription:
`78e3cdf93a18350b1d6b6c4da2a9cd38bc56ebdbf74a5b445c8bfa4f9b72d344`.
Its 194,958-byte JSON and original timestamp are unchanged. Frontend SBOM hash:
`99b867cf4a7ec05e2275c84a8f38e716c00d49fe14dbb9a26827b2720c8c108b`.

## 4. Tests actually executed and preserved acceptance

| Check | Exact result |
|---|---|
| Frontend formatting | Passed after Prettier-only correction |
| Rollback regression before fix | 2 failed, 1 passed; correct failures reproduced |
| Rollback regression after fix | 3 passed; local command simulation only |
| Focused deployment unit suite | 8 passed in 2.67s; no real backup/restore/cloud workflow |
| Local CI static checks | 1 workflow, 3 rendered role templates, 7 Python files, 6 shell scripts and 12 PowerShell scripts parsed; Ruff passed |
| Credential-pattern/source review | Zero findings across the 74 reviewed candidate paths; 50 deployable source/asset files also passed; no files staged |
| Frozen/protected inputs | 32 tracked frozen inputs, entrypoint and pin passed; accessible protection result below |
| Fresh read-only Azure guard | Spending limit On, Consumption-only mode, exact inventory, internal ingress, min/max and current image digests passed |
| Fresh federation/RBAC read | One exact main-branch trust, zero application password/certificate credentials, nine scoped role assignments; custom role actions match templates |
| Preserved public acceptance | HTTPS/live/ready 200; public API/MLflow 404; unauthorized history 401; engineer/admin boundary 403 |
| Preserved prediction/workflow | 201; probability `0.16546872246399696`; sign-in/manual case/save/history/reopen/changed rerun/immutable original/reset/review/audit passed |
| Preserved restart/cold persistence | Saved predictions/audits retained; actual zero replicas observed; readiness 504, 504, then 200 |
| Preserved manual live rollback | MLflow previous `0000001` ready, then current `0000002` restored ready; attempted API previous `0000002` live 200/ready 503, then current `0000003` restored ready |
| Hosted CI / OIDC / automated rollback | **Not run; no run URL or hosted success claimed** |

The current traffic query selected API `api--0000003` and repaired frontend
`frontend--0000002` as CI rollback bases. The preserved older frontend
`frontend--0000001` retains its baseline findings. Manual and simulated rollback
evidence does not establish hosted execution of the rollback branch.

Frozen model: `8c3a99dd8dfe20d2a3a0a721637b4be500ee1b32843f7cefc3af265f07262f7a`;
release: `65f2302cc9c4795142567296cc6b16143fad5abfe4df7b04152975748c2ec271`;
evidence: `2d073fa0d0bbbd4debfdf445cd80ec478fef0f7098c7ef356dbb3edd28894ea8`.
No model training, fitting, calibration, held-out analysis or full offline
regression was repeated. Application OIDC/Signup and clinical validation remain
outside this educational showcase.

## 5. Protection report resolution

The 2,193-path baseline has 1,744 immutable matches, six authorized edits,
four classified mutable credential paths and 439 inaccessible generated runtime
paths. None of those 439 is tracked repository input. They remain UNVERIFIED;
no content or ACL change was made. **Zero unexplained accessible mismatches**
is the gate, and it passes. Original manifests/policies remain preserved; the
reviewed README status correction has a separate exact-hash/diff classification.
The inaccessible runtime class is a disclosed evidence limitation, not a mismatch.

## 6. Backup/restore and PostgreSQL

Fresh backup `artifacts/azure-preflight/final-local-backup-20261019T051444Z`
still matches all five full SHA-256 values and sizes in its manifest. Reused
isolated restore evidence confirms `0004_case_input`, approved active release,
one registered model, readiness 200, prediction 201 and matching restored volume
contents; the initial cold prediction 504 and successful retry are retained.
Only that temporary restore project was removed earlier. The original expired
identity certificate, 13 October Stage 3 backup, fresh archives and original
source volumes remain preserved. No restore or backup operation was repeated.

Fresh PostgreSQL control-plane read: Ready, version 18, Standard_B1ms, 32 GiB,
seven-day backup, HA Disabled, `require_secure_transport=ON`. Its sole firewall
rule remains `AllowAzureServicesShowcase` (0.0.0.0/0.0.0.0), the approved bounded
Azure-services exception. Prior verified migration head is `0004_case_input`;
application/MLflow roles, TLS and persistence semantics remain unchanged.

## 7. Exact Azure inventory, budget and cost

There are 13 approved group resources, all in Southeast Asia:

- `rg-aletheia-showcase-sea-01` (8): `cae-aletheia-sea-01` (Express environment),
  `acraletheiasea1017` (Standard ACR), `id-aletheia-pull-sea-01` (pull identity),
  `pg-aletheia-sea-1017` (PostgreSQL), and stopped apps `frontend`, `api`,
  `mlflow`, `db-bootstrap`.
- `rg-aletheia-workload-sea-01` (5): `cae-aletheia-workload-sea-01`
  (WorkloadProfiles/Consumption only), serving apps `frontend`, `api`, `mlflow`,
  and stopped no-ingress `release-operator`.

Only frontend is external HTTPS. API is 1 vCPU/2 GiB; all three serving apps
are min 0/max 1. API/MLflow retain `.internal.` FQDNs and `http://api` /
`http://mlflow` discovery. No Dedicated profile, VNet, NAT, Private DNS,
load balancer or paid monitoring workspace was introduced. No Azure resource
or persistent Docker data was deleted.

The additional subscription warning budget `aletheia-showcase-warning` now
exists: INR 100 monthly, enabled 50/80/100 notifications, one contact per alert.
The earlier `RBACAccessDenied` is preserved as historical evidence and is no
longer an active budget limitation. A budget warns; spending limit remains On
separately. Fresh Cost Management month-to-date pre-tax cost remains
**INR 11.7066685215817**. No numeric zero forecast, future free-tier guarantee,
cash-versus-credit settlement or fresh remaining-credit amount is asserted;
billing can lag. Existing student benefits do not erase the reported cost.

## 8. Evidence, Git state and next action

Inspect ignored `artifacts/azure-preflight/final-closure-20261019/`: summary,
exact archive bindings, raw and complete SBOM/licence inventories, complete
findings/dispositions, component applicability, preserved acceptance hashes,
protection resolution, cost/budget readback, federation/scopes, static checks,
and the explicit reviewed source list. Original failed attempts and earlier
handoffs remain preserved. Generated evidence, archives, dumps, tokens,
certificates, keys and local secrets are excluded from Git.

Branch `main`; HEAD `07415aaf9eb58b028e2f629d884199016ccbe13f`; live upstream was read at the same SHA,
0 ahead / 0 behind. **12 modified tracked paths, 62 untracked
paths, zero staged files.** The exact status and reviewed source lists are
stored as ignored closure evidence. Existing stash remains
`c6b91a13bf4338e559dfaad49f850dd719f5ca47`. This describes the pre-commit review
snapshot; the authorized commit/push and subsequent hosted attempt are recorded
at the top of this handoff.

Next action under the user's explicit one-time exception: selectively stage the
74 reviewed source/documentation paths, verify the index, commit and push main,
then observe a real hosted run through OIDC, tests, image builds/digest deployment,
controlled migration and smoke checks. Variable configuration is now verified.
The required commit message is:
`feat: deploy Aletheia to Azure with secure CI/CD`.
Stop for external supervisor review only after the hosted gate passes, or
report a reproduced external permission/security blocker without claiming closure.
