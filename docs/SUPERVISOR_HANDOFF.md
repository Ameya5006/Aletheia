# Supervisor handoff — GitHub presentation (2026-10-20)

## Current milestone and status

**PASS WITH MINOR FIXES for external review.** The approved presentation files, design explanations, privacy-reviewed live media and fresh-clone checks are prepared. They remain uncommitted. No application, model, migration, deployment, Azure resource, CI workflow, protected evidence or Docker data changed. Supervisor review is the task boundary.

Public frontend: https://frontend.whiteflower-9d03c62c.southeastasia.azurecontainerapps.io/ (HTTPS 200 on 2026-10-20). Prediction, history and audit actions require a provisioned short-lived identity. Public Signup and external organizational OIDC are deferred. The [reviewer-access guide](REVIEWER_ACCESS.md) documents safe operator steps; no credential is published.

Latest live GitHub [run 39417029251](https://github.com/Ameya5006/Aletheia/actions/runs/39417029251) completed **successfully** at source 963050edb817b634c9a69fd692ab839c26121bd3. Earlier hosted closure checks and their limits remain in the [project report](PROJECT_REPORT.md). This presentation did not trigger another hosted run.

## Implemented and why

- Replaced the stale README with a scannable entry point, accurate access model, current architecture, prediction path, technology/storage responsibilities, verified project journey, security limits, local commands and documentation index.
- Added [HLD](HIGH_LEVEL_DESIGN.md), [LLD](LOW_LEVEL_DESIGN.md) and candid [SOLID assessment](SOLID_AND_MAINTAINABILITY.md). The LLD diagrams use actual database table names.
- Added [cleanup manifest](REPOSITORY_CLEANUP.md) and [local guide](LOCAL_DEVELOPMENT.md). All tracked root files were classified. No file was moved or deleted; operational and evidence files remain in place. No project licence was added.
- Added [GitHub metadata proposal](GITHUB_PRESENTATION.md), [temporary access guide](REVIEWER_ACCESS.md), sanitized [media](assets/demo/README.md) and reproducible scripts under scripts/presentation. Description, homepage, topics, social preview, release and pinned links are **proposed**, not remotely applied.
- Reconciled current snapshots in ARCHITECTURE.md, DEPLOYMENT_ARCHITECTURE.md, EXECUTION_PLAN.md and the learning/defence record in PROJECT_REPORT.md. Historical sections remain labeled and preserved.

**Files modified:** README.md, docs/ARCHITECTURE.md, docs/DEPLOYMENT_ARCHITECTURE.md, docs/EXECUTION_PLAN.md, docs/PROJECT_REPORT.md, docs/SUPERVISOR_HANDOFF.md. Supervisor-owned docs/CURRENT_TASK.md was already modified at the start and was not changed by this milestone.

**Files created:** docs/GITHUB_PRESENTATION.md, docs/HIGH_LEVEL_DESIGN.md, docs/LOCAL_DEVELOPMENT.md, docs/LOW_LEVEL_DESIGN.md, docs/REPOSITORY_CLEANUP.md, docs/REVIEWER_ACCESS.md, docs/SOLID_AND_MAINTAINABILITY.md, docs/assets/demo/README.md, 13 numbered sanitized JPEGs, docs/assets/demo/poster.jpg, docs/assets/demo/walkthrough.webm, and six scripts/presentation/*.mjs files. No files moved or deleted.

## Live demonstration and privacy

The bounded public-browser run captured 13 scenes at 1440 × 900, composed a **69-second**, **1,959,921-byte** WebM and reused its real result frame as the poster. The illustrative example produced probability 0.16546872246399696 (16.55% displayed). The script asserted sign-in, HTTP 201 prediction, save, history, reopen, distinct rerun, unchanged original probability and reset; audit events loaded. This is workflow evidence, not a new ML evaluation. Edge decoded the video at 1440 × 900 and a playback frame was visually inspected. Key result, explanation, history, rerun and audit stills were inspected. Fourteen JPEGs including the poster have 1440 × 900 dimensions and zero EXIF entries. The largest media binary is below 2 MiB. View [the video](assets/demo/walkthrough.webm) before any future commit.

The recorder accepts only the approved public origin, reads token material from an ignored local file, omits token entry, redacts identifiers/accounts/digests before every screenshot and builds the video from those images. A linked real-interface poster was chosen over a small animated GIF so the README preview remains readable. No private patient information, raw video, token, key, trace, browser storage or account identifier is included in public media. Demonstration requests created illustrative records in the existing application database; no Azure resource or configuration mutation occurred.

## Checks actually executed

| Check | Exact outcome |
|---|---|
| Public URL | HTTPS HEAD 200 after capture; live authenticated browser flow completed |
| GitHub | Live API returned run 39417029251 success at HEAD; shallow remote clone succeeded at the same SHA with clean status |
| Privacy helper | Four focused Node tests passed, zero failed |
| Media playback | Edge decoded WebM, 1440 × 900, playback advanced to 1.53 seconds; 13 scenes and poster reviewed |
| Documentation links | Final check script found 237 local links and zero missing across 14 documents |
| Mermaid diagrams | Official Mermaid 11 parsed and browser-rendered all 15 diagrams, zero invalid; one sequence-label separator corrected |
| Fresh-clone frontend | npm lock installed 343 packages; lint and typecheck passed; 81/81 Vitest tests in seven files; production build passed |
| Fresh-clone Python | Python 3.12 isolated venv; lock and editable installs passed; pip check found zero broken requirements; project Ruff scopes passed; fixture unit/data tests 64 passed, 15 warnings |
| Compose | Config rendered from example plus explicit non-secret placeholder values; no image/container build or start |
| Credentials | Existing scanner passed 53 deployable files in working tree and 52 in fresh clone, zero findings |
| Git and protected files | git diff --check passed; 252 protected original files match start-of-task SHA-256 baselines, none missing; supervisor task file unchanged since start; zero staged files, 0 ahead/0 behind |

The fresh clone was created outside this checkout and overlaid with only intended public working-tree files. Ignored secrets, frozen model bundles and backups were absent. The raw environment example deliberately omits required release/identity values and cannot alone render or start a full stack. Complete local serving needs an authorized frozen release and private configuration; it was not repeated.

## Problems, trade-offs and limits

- PowerShell blocked the npm.ps1 shim; npm.cmd worked. Git's Windows CRLF checkout made unchanged frontend files fail default Prettier (48 reported); format:check with end-of-line auto passed. No application source was reformatted.
- An overbroad Ruff check of all deployment helpers reported 45 existing style errors. Project source scopes and the hosted deployment F-rule scope passed. The local guide now specifies the actual gates.
- Pytest's shared temp location was inaccessible; an ignored clone-local base temp yielded 64 passing fixture tests. The initial example-only Compose config failed on intentionally empty required values; explicit non-secret placeholders rendered it.
- Direct Chromium egress timed out while Node HTTPS to the public host worked. Live response interception on the exact public origin enabled recording. A cold-start sign-in timeout led to bounded readiness warmup and at most three login attempts in the recorder; no inference deadline or Azure sizing changed. Frame review corrected result framing, audit loading and a redacted-link selector.
- Historical-data generalization is unproven, the descriptive threshold has low documented recall, explanations are noncausal and reference-dependent, public onboarding is restricted, monitoring is limited and backend image findings remain. No clinical or vulnerability-free claim is made. The newer deployed frontend digest is not treated as covered by the older zero-finding exact-image scan.

No ML experiment, model comparison, calibration, hold-out evaluation or architecture change occurred. Prior reported Azure state was 13 resources, student spending limit enabled, INR 100 warning budget and month-to-date pre-tax INR 11.7066685215817; billing can lag and was not freshly queried for this presentation. The original zero-cost objective is not demonstrated.

## Deployment and protected boundaries

The last preserved Azure readback has 100% traffic on API api--0000006 at sha256:c15f8346e7316cb16f53a950630a69850c6ceaa0b03623531652cc19c1c3ffb9, frontend frontend--0000005 at sha256:1cecb7b183bf00883f411a27a92dfb26e027f0cbd401c5cad7b7c4f5ee0f9056, and MLflow at sha256:062f3fb2700fa152d6cab44aeec154f44ade7c2116f63038dca1ccd38342ab5d. API and MLflow ingress remain private; no-ingress release-operator--0000012 is stopped. The presentation made no infrastructure changes and did not touch the protected stash c6b91a13bf4338e559dfaad49f850dd719f5ca47.

## Unresolved questions and suggested next step

Supervisor: review README claims and [the video](assets/demo/walkthrough.webm), inspect HLD/LLD/SOLID, confirm the licence remains undecided, and assess retained security/cost limitations. If accepted, the owner can commit the prepared files and apply the [proposed GitHub metadata](GITHUB_PRESENTATION.md). Suggested commit message: **docs: complete Aletheia portfolio presentation**. No commit, push, release, metadata change, Azure deletion or Docker cleanup is authorized by this handoff.
