# Supervisor Handoff - recovered final Azure/CI closure (2026-10-20)

## 1. Current milestone and status

**PASS: hosted CI and final Azure readback.** External supervisor acceptance is
still required. Nonzero reported cost and retained backend security findings
remain explicit limitations; the original zero-cost objective and production
security acceptance are not established.

Public URL: https://frontend.whiteflower-9d03c62c.southeastasia.azurecontainerapps.io

Final deployed commit: `929b10deb901c715bee05aaba52ac1db3ccbeb80`.
[Hosted run 39277474682](https://github.com/Ameya5006/Aletheia/actions/runs/39277474682)
completed **successfully**, with every job step successful. Recovery found this
existing green run through GitHub's live API; no replacement run, new deployment,
CI correction, commit or push was necessary. The previous handoff is preserved
as ignored `final-closure-20261019/handoff-before-recovery-20261020.md`.

## 2. Implemented and verified

- Hosted OIDC, frozen-input verification and verified fixture retrieval.
- 58 backend tests, 81 frontend tests, Ruff, frontend lint/typecheck, contract,
  production build and deployable credential scan.
- Immutable ACR builds/pushes, Bicep validation/structured what-if, migration
  marker observation at `0004_case_input`, controlled API/frontend deployment.
- Authenticated public prediction HTTP 201, probability `0.165468722464`,
  matching frozen identities; save, reopen, history and audit checks passed.
- Anonymous history 401, engineer/admin boundary 403; real internal API and
  MLflow health 200, outside effective-host and alias probes 404.
- Final hosted topology/digest guard; operator stopped after migration and smoke.
- Fresh readback: healthy serving revisions at 100% traffic; private ingress,
  resource inventory, student spending limit, cost and budget verified.
- Exact changed-image security/SBOM/licence reconciliation; unchanged evidence
  reused after identity checks.

## 3. Files changed during this recovery

Only tracked documentation changed: `docs/PROJECT_REPORT.md`,
`docs/SUPERVISOR_HANDOFF.md`, `docs/ARCHITECTURE.md`, and
`docs/DEPLOYMENT_ARCHITECTURE.md`. Ignored evidence helpers/reports were added or
updated under `artifacts/azure-preflight/final-closure-20261019/`.
No governing file, source, workflow, model, deployment configuration or test changed.

## 4. Decisions and problems

The interrupted controller problem was already fixed: CLI replica discovery
needed `Microsoft.App/containerApps/revisions/replicas/read` in the existing
operator-only role, alongside `getAuthToken/action`. Ten assignments remain in
the preserved verified role evidence. Final commit `929b10d` then tested the
real MLflow `/health` endpoint instead of an API route that could misleadingly
return an application 404. Successful hosted execution proves both repairs.

Recovery reused the green run. Only changed digests received new scans; the old
frontend scan cannot validate a new digest. Backup/restore, full regression,
browser, persistence and live rollback were not repeated.

The first readback's HTTPS assertion failed without saving individual probe
statuses. All six independent retry probes passed. The local ignored helper
now saves results before asserting; its full rerun passed. The exact original
failing endpoint/cause is unknown. No inference deadline or runtime limit changed.
Sandbox access initially prevented reading existing sessions; approved elevated
read/verification commands succeeded without adding credentials.

## 5. Checks actually executed and exact results

| Check | Result |
|---|---|
| Live GitHub run/jobs and sanitized log | Run 39277474682 success; job 118145469698; all steps success |
| Hosted backend | 58 passed, 2 warnings, 4.22s |
| Hosted frontend | 81 passed across 7 files; lint/typecheck/contract/build passed |
| Hosted credential scan | 52 deployable source/asset files passed |
| Fresh local frozen check | 32 tracked inputs plus entrypoint/pin passed |
| Fresh local credential scan | 53 deployable source/asset files passed |
| Preserved acceptance hash check | 5 backup files' sizes/SHA-256 match; restore/browser/workflow/persistence evidence consistent; original frontend scan/SBOM hashes match |
| Changed deployed images | Backend/frontend vulnerability and SBOM commands all exit 0; exact config bindings match |
| Native backend inventory | SQLite 3.54.0 and binary hash match; 240 components / 772 licence entries |
| Full final readback retry | Exit 0; frontend/live/ready 200, anonymous history 401, direct API/MLflow health 404 |
| Recovery evidence validator | Exit 0; 14 unchanged MLflow reports hash-match; changed scan/config/digest bindings and final Azure state agree; credential checks have zero findings |
| Git checks | HEAD, origin/main and live remote main match; 0 ahead / 0 behind; whitespace check passes; zero staged files |

Rollback evidence is preserved from hosted run `39266540207`, which stopped the
operator and executed the actual recovery branch on a pre-update observation
failure while healthy API/frontend traffic remained 100%. Earlier manual live
revision rollback/restoration also passed. The green final run did not inject
a failure after switching traffic; these checks have different scopes.

## 6. ML and immutable deployed identities

No new ML experiment, training, calibration or held-out access occurred.
Prediction probability is a frozen model output, not clinical validation.

| App | Revision at 100% traffic | Digest |
|---|---|---|
| Frontend | `frontend--0000004` | `sha256:c71d3fc586fb41cc7796287ed7f35a0528fc24fa6adb44ecf52042697f763410` |
| API | `api--0000005` | `sha256:aaa14ef48a2db5f28647bc1599e7d1fdd90c9962d484cc417d32d59b2c1f54e3` |
| MLflow | `mlflow--0000002` | `sha256:062f3fb2700fa152d6cab44aeec154f44ade7c2116f63038dca1ccd38342ab5d` |

Stopped no-ingress `release-operator--0000010` uses the API digest.
All three serving apps remain min 0/max 1.

Frozen model: `8c3a99dd8dfe20d2a3a0a721637b4be500ee1b32843f7cefc3af265f07262f7a`;
release: `65f2302cc9c4795142567296cc6b16143fad5abfe4df7b04152975748c2ec271`;
evidence: `2d073fa0d0bbbd4debfdf445cd80ec478fef0f7098c7ef356dbb3edd28894ea8`.

## 7. Security and limitations

Frontend: zero vulnerabilities; 71 SBOM components / 103 licence entries.
API/operator: 1 critical / 63 high / 112 medium / 105 low / 1 unknown;
240 complete SBOM components / 772 licence entries. Unchanged MLflow retains
the same severity counts and complete inventory counts. Findings are preserved.
Prior MiniZip applicability and pip-vendoring dispositions remain supporting
evidence, not a clean backend scan or legal clearance. No external CycloneDX
schema validation was performed.

Earlier protection resolution retains 439 inaccessible generated runtime paths
as UNVERIFIED, none tracked, and zero unexplained accessible mismatches. No ACL
or content workaround was made. Provisioned JWT access, cold-start latency,
the accepted database firewall exception and historical-data/clinical limits
remain. Current remaining credit and a numeric forecast are not freshly verified.

## 8. Azure resources, budget and cost

Readback 2026-10-20: 13 resources, all Southeast Asia, in
`rg-aletheia-showcase-sea-01` (8) and `rg-aletheia-workload-sea-01` (5).
All four old Express apps are stopped. Current environment is WorkloadProfiles,
Consumption only, Succeeded, with no customer networking or paid log destination.
PostgreSQL is Ready, version 18, Standard_B1ms, 32 GiB, secure transport ON.
No Azure resource or existing Docker data was deleted.

Azure for Students is Enabled; spending limit is **On**. Fresh Cost Management
month-to-date pre-tax cost is **INR 11.7066685215817**. The INR 100 monthly
warning budget exists with enabled 50/80/100 percent notifications. Notifications
are not a hard cap. Billing can lag; no zero-cost, zero-forecast, fresh credit
balance or cash-versus-credit settlement claim is made.

## 9. Architecture and documentation

No architecture change during recovery. Both architecture documents now reflect
successful hosted execution. PROJECT_REPORT records recovery order, actual
results, controller diagnosis, evidence reuse, security, billing, observation
failure and viva explanations. This handoff replaces the stale current-state
summary; earlier details remain in the report and preserved handoff.

## 10. Evidence to inspect

Under ignored `artifacts/azure-preflight/final-closure-20261019/`:

- `hosted-jobs-39277474682.json` and `hosted-job-118145469698-sanitized.log`.
- `post-ci-azure-readback.json`, control-plane and completed probe-attempt reports.
- `hosted-security-39277474682/`: exact digest/config bindings, raw scans/SBOMs,
  complete backend inventories, native SQLite proof and hashed summary.
- `recovered-closure-verification.json`: final cross-evidence/credential/Git checks.
- `preserved-acceptance-evidence.json`, original manifests and earlier rollback logs.

Generated evidence, archives, dumps, keys, certificates and tokens are not staged.

## 11. Git status, unresolved questions and suggested next step

Branch `main`; HEAD/origin/main/live remote main:
`929b10deb901c715bee05aaba52ac1db3ccbeb80`; **0 ahead / 0 behind**.
Existing stash: `c6b91a13bf4338e559dfaad49f850dd719f5ca47`.
Exact working-tree status after recovery, with zero staged or untracked paths:

```text
 M docs/ARCHITECTURE.md
 M docs/DEPLOYMENT_ARCHITECTURE.md
 M docs/PROJECT_REPORT.md
 M docs/SUPERVISOR_HANDOFF.md
```

The existing green run made another CI repair/push unnecessary. Suggested next
step: supervisor review of nonzero cost, retained security findings and closure
evidence, then human review/commit of these documentation updates. Suggested
message: `docs: reconcile verified Azure CI closure`. No further milestone is
authorized; no new external permission blocker remains for the CI closure.
