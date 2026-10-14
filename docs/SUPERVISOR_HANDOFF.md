# Supervisor Handoff - Stage 3 release-evidence repair

**Status:** focused repair complete; all applicable local Stage 3 gates pass.
One complete isolated offline container regression exited 0: 276 collected,
275 passed, zero skipped, one live-data deselected, 63 warnings in 2251.04s.
Defensible to commit for local Stage 3, subject to supervisor review of retained
security dispositions; no public deployment approval. No next milestone began.

**Implemented:** backend retains Python 3.12.10 and all Python pins, but replaces
Debian SQLite with checksum-pinned, separately compiled SQLite 3.54.0. Compilers
remain outside runtime. PostgreSQL removes unused gosu and continues as UID 70.
Git remains solely in the test-only image. The runner always executes the full
offline suite. Scanner supports preserving unchanged frontend evidence;
security.py records each high/critical disposition, native library/licence
inventory and exact image bindings. README's duplicate token refresh was removed.
No schema, API, model artifact or approved deployment topology changed.

**Final image identities (OCI index / scanned config):**

| Image | OCI index digest | Scanned config digest |
|---|---|---|
| Backend | sha256:7b5d9500f3eb3ffa27f27c14d3692babe3957f38c77a2ae3a74f8063c6d259c4 | sha256:9fe4ea73549252d6e3dd37d2b6f4b0a3ca566ed09ac236bd5bd42770deff7c62 |
| Frontend, unchanged | sha256:d5bf7a0b7fa90087a969dc072730a0a25d7c53c99e1cf5e1b12ce5b7330f8f8e | sha256:1d376d77cbe40f8b13b4624612b2a6cec80f7c2327d204b43c3dae02352dd824 |
| Local PostgreSQL | sha256:3a53d82d19ffeb494281b3cb4c17193b4ba09311f265e916ae1acb711dbbce7c | sha256:cac4acadcaad1f5030f707ab6de7cd810b8cfa66e265a90623ed60fb7baf5780 |
| Test-only regression | sha256:da2911c0235bd9ea74d082fc2607b886b7eb73e00b84b48db67ef69cf05ed5a1 | sha256:b351e069dd04aee188c88088e99d485a1cb982f416db70dcfcf1bf566a26bfe5 |

Archives/config digests/layers match runtime inspection. All four SBOM image IDs
match scanned configs. Native SQLite was not auto-detected: the SBOM explicitly
supplements its observed version/binary hash and upstream source/licence.
Backend/frontend/PostgreSQL inspect sizes: 545,425,493 / 31,274,769 /
123,006,689 bytes. These are inspect content sizes, not unpacked disk totals.

**Security findings (critical/high/medium/low/unknown):** backend
1/55/116/105/1 (before 2/57/119/108/1); frontend 0/0/0/0/0, unchanged scan bytes;
PostgreSQL 0/0/0/0/0 (before 1/24/27/3/5); regression 1/65/135/135/4
(before 2/67/138/138/4). No vulnerability-free claim or scanner suppression.

CVE-2025-7458, CVE-2026-11822 and CVE-2026-11824 disappear after replacing
SQLite 3.40.1-2+deb12u2 with 3.54.0 and verifying Python linkage. Remaining
critical CVE-2023-45853 is zlib1g 1:1.2.13.dfsg-1: no fixed Bookworm version;
Debian documents that affected contrib/MiniZip is not built in this binary.
Runtime inspection finds no MiniZip files or affected exported function.
Reconsider on introducing MiniZip; non-root is not the basis of disposition.
CVE-2025-68121 and 24 Go highs disappear by removing local PostgreSQL's unused
gosu helper. Root-switch startup is intentionally unsupported. Future cloud uses
managed PostgreSQL; regression image must never deploy.

Remaining distro highs have no fixed installed-distro version reported. Four
pip-vendor highs remain: msgpack 1.1.2 -> 1.2.1 (GHSA-6v7p-g79w-8964),
setuptools 70.3.0 -> 78.1.1 (CVE-2025-47273), urllib3 2.7.0 -> 2.8.0
(CVE-2026-97687/CVE-2026-97689). Top-level setuptools 84.0.0/urllib3 2.8.0
are already fixed. PyPI's latest pip remains 26.2.1 on 2026-10-14; no compatible
released vendor update exists. Configured runtime never invokes pip on untrusted
inputs. Per-advisory exposure/mitigation/layer/version/fix records cover all
153 previous and 122 final high/critical entries; test-only curl/LDAP/XML/Perl
packages have separate private-network/input-boundary dispositions.

**Checks actually executed during repair:**

| Check | Actual result |
|---|---|
| Compose config; backend/PostgreSQL/regression builds | exit 0; native SQLite 3.54.0 import/SQL assertion passes |
| scan.py --only-changed; security.py | exit 0; new three-image scans/SBOMs; unchanged frontend preserved; four identities/layer sets and SBOM bindings match |
| Licence inventory | backend 771, frontend 103, PostgreSQL 71 scanner entries; regression 122 Debian copyright records plus inherited backend Python metadata; native public-domain SQLite supplemented, all digest-bound |
| Full isolated regression | exit 0; 276 collected, 275 passed, 0 skipped, 1 live-data deselected, 63 warnings, 2251.04s; this invocation alone |
| pytest tests/deployment -q | latest exit 0; 5 passed in 1.25s after test-budget/diagnostic-mount change; earlier 5 passed in 3.80s and 0.83s |
| Host/final-image pip check and exact backend pins | exit 0; no broken requirements; all 102 Linux pins match; read-only pip cache warning retained |
| Ruff check / format | exit 0; all checks pass; 105 files already formatted |
| Frontend type/lint/format/build/OpenAPI/licences/tree | wrapper exit 0; 394 modules, 5.39s build; 10 public responses/OpenAPI match; all 29 direct licence records; consistent npm tree |
| Production npm audit --omit=dev --audit-level=high --json | exit 0; total 0 vulnerabilities |
| verify.py --checks-only | exit 0; six E2E/outage groups pass on final images |
| recovery.py | exit 0; six groups pass; healthy restart 74.031s |
| restore.py | exit 0; both databases/three volumes restore with matching file hashes/modes, prediction/audit/readiness and isolated revoked-release refusal |
| resources.py | exit 0; non-root/capabilities/private ports/privacy/release/pin controls; 3 idle and 7 workload samples, 10 synthetic requests |
| browser.mjs | exit 0; 33 real proxy route/viewport axe checks, zero violations; keyboard/dark/reduced-motion smoke |
| Protected hashes; whitespace | all 158 protected hashes match; git diff --check passes; 24 deployment files pass trailing-whitespace inspection |

Unchanged frontend unit-test evidence is reused: 59 passed in four files, 45.32s.
No new ML experiment, metric, training/reselection or held-out evaluation.

**Exact clean regression invocation:** the new project had no containers or
volumes before launch. The ignored override binds its two services to the final
immutable image IDs above. This is one complete invocation, without exclusions
other than the live-data marker:

```powershell
docker compose --env-file artifacts/stage3-local/config.env -p aletheia-stage3-repair-20261014b -f deployment/compose.yaml -f deployment/compose.test.yaml -f artifacts/stage3-verification/repair-regression.override.yaml --profile test --profile regression run --rm regression
```

**Measurements/limitations:** fresh-container readiness 266.360s (cached images,
existing approved volumes); three idle totals 595.755/603.010/596.024 MiB and
42.76/36.67/54.05% CPU; seven workload samples 595.846-622.763 MiB and
41.45-312.84% CPU (100% = one core). Ten synthetic HTTP requests 563-2906ms.
Regression ran concurrently and is excluded from totals; host contention and
health probes affect results. No sustained-load, clinical or production-scale
claim. API/MLflow three-second probes briefly timed out, then recovered;
resource check passed without budget changes. Slower measurement root cause
unproved. Real external OIDC/login/logout and cloud TLS remain unverified.
Native-library advisory coverage needs continued maintenance beyond auto scans.

**Problems:** initial Docker pipe was absent; stopped without edits, resumed only
when engine responded. Build invocation initially omitted test identity profile;
first regression launch used unsupported run --no-build, failing before collection.
Both command failures are retained. Explicit security inventory caught missing
util-linux-extra; corrected completeness check passes. Host diagnostic SQLite
HTTPS request failed expired-certificate validation; container build succeeded
with TLS verification and pinned source hash. No TLS bypass or source substitution.
First complete repair regression exited 1: 274 passed, 1 failed, 1 deselected,
60 warnings, 3075.28s. Registry reconciliation GET hit the unchanged ten-second
deadline; other registry cases passed. Scheduling pressure is plausible, not
proved as sole cause. Serving workloads now stopped (volumes retained), test-only
CPU budget raised from two to three cores, and a narrowly scoped diagnostics
mount saves MLflow service logs/cgroup counters. Complete fresh-project rerun
passed: 275 passed/0 skipped/1 deselected/63 warnings, 2251.04s, exit 0.
No assertion/deadline was weakened and no offline test excluded. Diagnosis of
perceived stall found all nine registry tests passed, runnable pytest, no PG
blockers, and MLflow health/metadata GETs HTTP 200 in 0.331/0.349s. Final logs:
3,121 HTTP records, 1,451 artifact GETs; no CPU throttling/OOM, peak memory
733,487,104 bytes. Existing run completed; no duplicate or deliberate stop.
MLflow child inherited fixture-start test label, not the current pytest node. Failed evidence:
repair-regression-full-failed.log and repair-regression-full-failed-exit.txt.

**Files created by repair:** deployment/tests/security.py.
**Files modified by repair:** deployment/Dockerfile.api, Dockerfile.postgres,
deployment/compose.test.yaml, deployment/tests/regression.py, scan.py, README.md,
PROJECT_REPORT.md, this handoff.
Earlier Stage 3 Docker/Compose/proxy/helpers/tests remain in the working tree.
No architecture document, dependency lock or protected artifact changed.

**Evidence to inspect:** ignored artifacts/stage3-verification/{scan-summary.json,
repair-image-identities.json,repair-security-disposition.json,
repair-license-inventory.json,*-scan.json,*-sbom.json,repair-regression-full.log,
repair-regression-exit.txt,repair-regression-summary.json,
repair-regression.override.yaml,regression-diagnostics/,e2e.json,recovery.json,
restore.json,resources.json,proxy-browser.json,repair-*.log}. Previous reports
are preserved in pre-repair-security and pre-repair-functional. Accepted restore:
backup-aletheia-stage3-restore-626c3a4b; isolated restore stopped, volumes retained.

**Protection/governance:** main; HEAD/local origin/main
107636b38cb3b2c85669de645dca98f1a1d27576; stash
c6b91a13bf4338e559dfaad49f850dd719f5ca47 unchanged and contents uninspected.
CURRENT_TASK byte identity and frozen model/split/research/audit hashes match.
Generated evidence, scans, SBOMs, archives, secrets, caches, raw data and Docker
state remain ignored. No Git mutation, commit/push, stash restoration, research
audit rerun, synthetic case builder, cloud, CI/CD or monitoring implementation.

**Unresolved questions/next step:** external supervisor reviews the retained
security dispositions, native-library maintenance and local measurements. The
synthetic case builder belongs after this repair and before managed-PostgreSQL/
real-OIDC cloud deployment; both require separate authorization. No subsequent
milestone is authorized. Recommended commit message after review:
`feat: deploy Aletheia local application stack`. Codex did not commit or push.
