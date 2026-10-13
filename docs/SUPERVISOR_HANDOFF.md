# Supervisor Handoff — Macro Milestone 4 Stage 2

**Status:** implemented and verified locally; ready for external supervisor review.
Stage 3 is unimplemented and not authorized. No commit or push was performed.

**Starting state:** resumed the authorized partial frontend on `main`, HEAD and
local origin/main both `55a248e52e9a037a20719fea2ca1861c4cc63eed`
(`feat: implement Aletheia backend and MLOps foundation`). Initial status was the
user-owned CURRENT_TASK modification, 43 authorized frontend files and the
explicitly identified accidental `~/.codex/hooks.json`. The file was confirmed
as the permission-notification hook and removed with only its empty local parents.
Real user configuration was neither inspected nor changed. Stash remains
`stash@{0}: On main: wip: credit research core before healthcare realignment`;
its contents were not inspected, restored or changed.

**Implemented:** React/strict TypeScript/Vite static SPA with centralized tokens,
light/dark appearance, reduced motion, responsive sidebar/mobile navigation,
keyboard/focus/skip link, bounded error/loading/empty states and route modules.
Overview; fixed read-only Case Analysis and persisted predictions; local/global
Explanation with text alternatives; stability/subgroup/no-recourse Reliability;
review checklist/coded reasons/revisions/stable retry keys/history/audit links;
role-scoped audit list/detail/cursor/loading-page filter; Model Card; sign-in;
read-only administrator release list/detail. Runtime contains no fixture mode or
API-failure fallback. All seven primary screens and their secondary routes exist.

**Flow and decisions:** Router → session/context → page → Zod-validated API
client → Stage 1 `/api/v1` → existing registry/serving/PostgreSQL/audit boundaries.
OIDC code/PKCE uses memory-only access-token storage and transient session PKCE
state. Viewer is public; reviewer/engineer/administrator are independent UI hints,
with backend JWT/local-entitlement/object authorization remaining authoritative.
Review uses the actual coded `reason_code`, not unsupported free-text comments.
Model Card/release routes defer Markdown code through lazy/Suspense; no backend,
DB, model artifact or public API architecture migration. ARCHITECTURE was not
changed because this implements its approved browser boundary.

**Real endpoints integrated:** GET health/live, health/ready, models/current,
models/current/card, demo/cases, explanations/global,
explanations/local/synthetic-discharge-v1, audits/stability, audits/subgroups,
counterfactuals/feasibility, predictions/{id}, predictions/{id}/reviews,
audit-events, audit-events/{id}, admin/model-versions and
admin/model-versions/{version}; POST predictions and predictions/{id}/reviews.
All paths use `/api/v1`. Public integration is verified against fresh real
FastAPI projections/OpenAPI; private UI and OIDC browser tests use HTTP-boundary
fixtures. Live organization-provider/deployed full-stack integration is unverified.

**Files:** 44 new frontend files: manifests/lock/tool configs/env template,
entrypoints, 3 API modules, session provider, 4 reusable UI modules, 8 page modules,
2 stylesheets, 3 contract/licence scripts, OpenAPI snapshot, 7 test/support files,
2 browser specs. Exact paths are in final Git status. Modified README (setup and
commands), PROJECT_REPORT (incremental Stage 2 evidence/defence record) and this
handoff. CURRENT_TASK remains the user's pre-existing modification, untouched by
Codex. Backend/Python/research/config/model/holdout/planning documents remain unchanged.

**Dependencies:** 10 pinned runtime and 19 development direct packages.
React/Router supply UI/routing, oidc-client-ts supplies approved SSO, Zod validates
JSON, react-markdown/remark-gfm render the published card without HTML, Fontsource
provides local typography. Vite/TypeScript/ESLint/Prettier and Vitest/Testing Library/
jsdom/Playwright/axe support build and verification. No new dependency was added
in this continuation. All 29 installed versions/licenses match the manifest:
MIT, Apache-2.0, OFL-1.1; axe-core development tooling is MPL-2.0.

**Final commands and exact results:** frontend commands ran in `frontend`;
Python and Git commands ran at repository root.

| Command | Exact final result |
|---|---|
| `npm.cmd ls --all` (output redirected to `../artifacts/stage2-verification/npm-tree-final.log`) | exit 0; consistent dependency tree |
| `npm.cmd run typecheck` | exit 0; strict TypeScript, including browser specs |
| `npm.cmd run lint` | exit 0; ESLint with `--max-warnings 0` |
| `npm.cmd run format:check` | exit 0; All matched files use Prettier code style! |
| `npm.cmd test` | exit 0; 4 files passed, 59 tests passed, 24.32s |
| `npm.cmd run build` | exit 0; 394 modules, built in 792ms; no bundle warning |
| `npm.cmd run test:browser` | exit 0; 7 passed (1.5m), one Edge worker, zero retries |
| `npm.cmd run contract:check` | exit 0; real OpenAPI and 10 public FastAPI responses exported; both snapshots match |
| `npm.cmd run licenses` | exit 0; all 29 exact direct versions and licence metadata present |
| `.\.venv\Scripts\python.exe -m pip check` | exit 0; No broken requirements found. |
| `.\.venv\Scripts\python.exe -m ruff check .` | exit 0; All checks passed! |
| `.\.venv\Scripts\python.exe -m ruff format --check .` | exit 0; 92 files already formatted |
| `git diff --check` | exit 0; no whitespace diagnostics; Git reports the existing LF-to-CRLF checkout convention for this handoff |
| `git -c core.autocrlf=false diff --no-index --check -- /dev/null <file>` for all 44 untracked frontend files | no whitespace diagnostics; expected addition exit 1 for each |
| `git check-ignore --no-index <sentinel paths>` | all 14 build/dependency/browser/coverage/cache/env/raw-data paths ignored; env example deliberately not ignored (exit 1) |
| SHA-256 comparison with `artifacts/stage2-verification/starting-hashes.json`, excluding README/report/handoff | 113 baseline file hashes unchanged, including CURRENT_TASK |
| `git branch --show-current`; `git rev-parse HEAD origin/main`; `git stash list` | main; both unchanged starting SHA; original stash remains |
| `Test-Path -LiteralPath 'C:\code\xai-decision-auditor\~'` | False |
| `pg_ctl.exe -D artifacts/stage2-verification/pgdata status` | no server running (exit 3 from pg_ctl; PowerShell wrapper exit 1) |

**Preserved earlier Stage 2 Python evidence:** offline command
`.\.venv\Scripts\python.exe -m pytest -m 'not live_data' -q -p no:cacheprovider --basetemp artifacts/stage2-verification/offline`
with disposable PostgreSQL on 127.0.0.1:55442 and disabled MLflow progress/hints:
**270 passed, 1 deselected, 63 warnings in 867.97s (0:14:27)**.
`artifacts/stage2-verification/offline.log` is the evidence. No Python/backend/
research file changed in this continuation, so the suite was not repeated.
Includes the existing Stage 1 application tests; no new ML experiment occurred.

**Problems/fixes:** seven long Markdown hash codes caused mobile/tablet overflow;
wrap code rather than hide content, and focusable named table regions preserve
keyboard scrolling. Bundle split reduced initial JS from 566.51 kB/171.15 kB gzip
to 407.38 kB/123.65 kB gzip plus deferred 159.32 kB/47.80 kB gzip (CSS 19.92 kB/
4.44 kB gzip). Tests now await deferred content; Node fixtures use JSON import
attributes; review assertions identify success separately from loading. Initial
browser reproduction was 2 failed/2 passed; intermediate component runs were
58 passed/1 failed before deferred waits; expanded browser setup initially failed
on JSON import, then 3 tests failed on an ambiguous status locator. A frontend
config edit during automation caused one destroyed-context failure (6 passed/1
failed); stable final files pass all seven. A sandboxed completed run could not
clean up Windows Vite; inspected only owned processes and stopped PID 20492's
server tree with approval. Later browser runs cleanly stop their own server.

**Evidence/limitations:** screenshots include case/model-card/review at
375/768/1440 and dark-unavailable under ignored `frontend/test-results`.
Public routes: 11 × 3 sizes; authenticated route states: 7 × 3 sizes; axe WCAG
checks, control bounds, no page horizontal overflow, focus/table/menu/skip-link,
review success and reduced-motion checks passed. Browser fixtures do not certify
real-provider or PostgreSQL browser E2E; automated accessibility/Edge coverage
is bounded. Model raw score/transformed lineage, actor role snapshot and chain
verification verdict are not published by Stage 1 and are not invented. Loaded
page audit filtering is labelled. Model serving-unavailable does not imply a
specific revocation cause. Historical research/clinical/fairness limitations persist.

**Review evidence:** inspect App/Shell/ModelCard/styles for overflow/lazy loading;
api/client, api/contracts, session, Review and both browser specs for boundaries;
README setup, PROJECT_REPORT learning/defence, OpenAPI/real-response snapshots,
preserved offline log and exact final Git status. Generated outputs, raw data,
coverage, caches, local env/credentials/temporary files do not enter status;
only the public `.env.example` template is included.

**Unresolved questions and suggested next step:** no remaining Stage 2 local
acceptance failure. External supervisor reviews Stage 2; real OIDC selection and
Stage 3 Compose/deployment/E2E/security/resource gates require a separate approval.
No training, holdout access/evaluation, responsible-audit rerun, protected evidence
modification, stash restoration, Stage 3 work or Git mutation occurred.
Recommended user-performed commit: `feat: implement Aletheia frontend application`.
