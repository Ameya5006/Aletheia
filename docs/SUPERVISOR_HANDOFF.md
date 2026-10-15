# Supervisor Handoff - Interactive workflow UI acceptance repair

1. **Current milestone/status:** repair of the existing post-Stage-3 interactive
   case-input/prediction milestone. Implementation and affected verification pass;
   external supervisor acceptance remains pending. No next milestone authorized.
2. **Implemented:** authenticated Overview is a neutral **No analysis is selected**
   state linking New Analysis and Analysis History. No preloaded prediction,
   probability, case fetch or attribution appears. Sign-in, navigation and review
   guidance use neutral wording. Legacy unselected case route redirects to the
   empty manual form; explicitly selected archived records remain read-only.
   Presentation-only labels cover frozen provenance/model-card/reliability and
   historical review/audit strings. Stored evidence, enums, numbers and hashes
   are unchanged. The existing 13-field prediction/save/reopen/rerun/reset workflow
   and authentication/RBAC remain intact.
3. **Repair files:** `frontend/src/pages/{Overview,CaseAnalysis,SignIn,Review,
   ModelCard,Reliability,AuditTrail,Analyses}.tsx`, `components/{Shell,ui}.tsx`,
   `frontend/tests/app.test.tsx`, new `tests/product-copy.test.ts`, browser
   workbench/authenticated/interactive tests; `deployment/tests/scan.py` adds an
   exercised `--only-frontend` option. README and PROJECT_REPORT updated. Other
   working-tree files belong to the preceding authorized milestone; see the exact
   final status below/in the ignored evidence file. No test fixture was renamed
   or changed for this repair.
4. **Decisions/why:** an empty selected-analysis state is truthful even with saved
   history and avoids adding automatic record selection. Historical protocol
   terminology is translated only when displayed, rather than changing frozen
   evidence or API contracts. Static AST copy checks and rendered route checks
   include expanded metadata. Internal protocol terms remain legitimate in source,
   API schemas and fixtures; generated-asset inspection classifies 11 occurrences
   as internal identifiers/compatibility/formatter code, not product copy.
5. **Executed verification:** commands below passed on the final repair. Full
   frontend unit regression ran once after focused checks. No results are summed
   across partial runs. Browser boundary tests use HTTP fixtures; the separate
   interactive browser test uses the real stack and no API interception.
6. **Model/ML:** no new experiment, fitting, calibration, model selection or held-out
   access. Frozen Histogram Gradient Boosting plus sigmoid calibration, threshold
   0.5, 13 raw string fields / 43 transformed columns remain. Model SHA-256
   `8c3a99dd8dfe20d2a3a0a721637b4be500ee1b32843f7cefc3af265f07262f7a`;
   backend release
   `65f2302cc9c4795142567296cc6b16143fad5abfe4df7b04152975748c2ec271`;
   audit results
   `2d073fa0d0bbbd4debfdf445cd80ec478fef0f7098c7ef356dbb3edd28894ea8`.
   Original exact field mapping, preprocessing, persistence and explanation flow
   are in PROJECT_REPORT's interactive milestone section. New Analysis applies
   strict versioned validation, canonical raw row, frozen preprocessing/model/
   calibrator, signed reference-contrast explanation, version-bound immutable
   prediction/audit snapshot, then optional Save history membership. Stability
   remains model-level; no attribution is causal. No LLM supplies values.
7. **Problems:** the old Overview test asserted 12.78%, preserving the acceptance
   defect. New tests assert no selected case/probability/reference-case requests.
   Focused tests needed real lazy-module preload and a nonambiguous heading query;
   desktop browser locator needed sidebar scope after adding a duplicate CTA.
   A Windows npm cleanup chain lingered across user interruption; final harness
   owns/stops its direct Vite child. Its earlier 2.9h summary is not a latency
   measurement. Real browser first needed an explicit successful session wait;
   another attempt returned HTTP 504 (root cause unestablished, inputs preserved).
   Final serial real journey passed without backend restart or weakened limits.
   Failed logs are retained; see PROJECT_REPORT for verified lessons.
8. **Known limitations/security:** local review only, no clinical/commercial/public
   deployment claim. Login, Signup and real external OIDC are deferred. No
   case-specific stability, causal recourse, arbitrary upload or LLM narrative.
   The fresh frontend vulnerability scan reports zero findings; unchanged backend
   retains 1 critical/55 high and test image 1 critical/65 high findings with their
   existing digest-bound dispositions. Do not interpret this as vulnerability-free
   infrastructure or production approval.
9. **Architecture:** no new architecture, API, migration, dependency, authentication,
   RBAC, database, audit or ML change in this repair. Existing architecture notes
   still describe the preceding milestone. Raw model-card/audit evidence is not
   altered by its human-readable presentation.
10. **Documentation:** README describes neutral Overview and empty input;
    PROJECT_REPORT incrementally records rationale, alternatives, tests, failures,
    evidence reuse, limitations and viva questions. This handoff replaces the old
    state. CURRENT_TASK is not edited.
11. **Evidence to inspect:** new ignored root
    `artifacts/interactive-verification/ui-repair-20261015/`: final-static-results,
    frontend-complete log/result, focused-pass log, browser-boundaries-final
    log/result, browser-real-verified log/result, browser.json, scan-summary,
    frontend scan/SBOM/licence inventory, frontend-html + image-asset-inspection,
    python-regression-reuse, protection-final and git-status-final. Logs can hold
    local credentials; they are ignored and must not be committed. The entire
    previous `resume-20261015b` evidence root is preserved.
12. **Environment/images:** Docker Desktop updated, healthy `desktop-linux` server
    29.8.2. Review project `aletheia-interactive-20261015b`, port 18081; old Stage 3
    restore containers are separate. Only frontend rebuilt/recreated, tagged
    `aletheia-interactive-20261015b-frontend:ui-repair-20261015`. New index digest
    `sha256:7845f8c0f1ec7897c65c373da9af490c37c55119d60985f2534da2b26e1af185`,
    scanned config
    `sha256:0ba668fa91b5dc2233e7ea3d5e8b724973052016dba03247d6232547e9f57807`.
    Fresh scan/SBOM/103-entry licence inventory bind matching runtime layers.
    Backend unchanged index
    `sha256:0063dfacebdbd22e5a09fc0efebe686e0be40841d89e7bc0245044372e41e406`;
    regression unchanged index
    `sha256:da2911c0235bd9ea74d082fc2607b886b7eb73e00b84b48db67ef69cf05ed5a1`.
    PostgreSQL unchanged index
    `sha256:3a53d82d19ffeb494281b3cb4c17193b4ba09311f265e916ae1acb711dbbce7c`.
    Unchanged image evidence is reused only for matching digests/inputs.
13. **Protection/Git:** initial milestone branch `main`, HEAD/upstream
    `a5e64dc3839435e6ef03f6efd2a3aed2eb5be418`, divergence 0/0; original status
    only `M docs/CURRENT_TASK.md`. This repair resumed inspected authorized
    in-progress changes (not an empty tree); starting status is recorded separately.
    Task SHA-256 remains
    `AB2FE7FA54652B733A6F64E3B0A1D27720CDF21F14C6ED0D0B516F10B190B652`.
    Existing stash remains `c6b91a13bf4338e559dfaad49f850dd719f5ca47`, caption
    `On main: wip: credit research core before healthcare realignment`.
    Final protection evidence checks 1,338 repair-baseline files, permits only
    named repair edits, and checks 924 original protected artifacts (914 Stage 3
    plus 10 frozen model/audit files). All 1,148 prior milestone evidence files
    and all three frontend fixture files are byte-identical; no protected or unexplained mismatch was found.
    See recorded final results. No staged changes, commit, push, branch/history/stash mutation.
14. **Unresolved questions:** external supervisor must accept the repaired UI.
    The transient HTTP-504 cause is not established. No additional implementation
    milestone is authorized by passing these checks.
15. **Suggested next step:** manually inspect Overview, sign-in, New Analysis,
    saved history and expanded evidence in the running review stack, then decide
    acceptance. Commit recommendation, if accepted:
    `feat: add interactive case prediction workflow`. User performs Git mutations.

| Command (from frontend unless noted) | Exact final result |
|---|---|
| `npm.cmd test -- --maxWorkers=1 tests/app.test.tsx tests/product-copy.test.ts` | 38 passed / 2 files, 36.86s, exit 0 |
| `npm.cmd test -- --maxWorkers=1` (complete, once) | 80 collected/passed, 0 failed/skipped/deselected, 6 files, 46.92s (wrapper 50.084s), exit 0 |
| `node node_modules/@playwright/test/cli.js test browser/workbench.spec.ts browser/authenticated.spec.ts` | 7 passed, 4.1m (wrapper 260.297s), exit 0; responsive/keyboard/dark/reduced-motion/axe/copy checks |
| `node node_modules/@playwright/test/cli.js test browser/interactive.spec.ts` | 1 passed, 20.0s (wrapper 21.813s), exit 0; real prediction/save/reopen/changed rerun/immutable original/reset + evidence copy checks |
| Real browser axe | 18 checks, 6 states x 3 viewports, zero violations |
| `npm.cmd run typecheck` | exit 0, 23.954s |
| `npm.cmd run lint` | exit 0, 14.948s, zero allowed warnings |
| `npm.cmd run format:check` | exit 0, 10.002s |
| `npm.cmd run build` | exit 0, 28.846s wrapper; Vite build 1.05s |
| `npm.cmd run contract:check` | exit 0, 61.810s; real OpenAPI + 10 responses match |
| `npm.cmd run licenses` | exit 0, 2.549s; 29 direct entries |
| `python -m ruff check deployment/tests/scan.py`; `python -m ruff format --check deployment/tests/scan.py` | passed, 1 file; new frontend-only scan option directly exercised |
| Compose config / frontend build / frontend-only up / frontend scan + SBOM + licences | exit 0; fresh frontend findings 0, licence entries 103; runtime/export binding matches |

The complete **unchanged Python** result remains 304 collected, 303 passed,
0 failed, 0 skipped, 1 `live_data` deselected, 63 warnings, 3378.28s, exit 0;
one invocation, not combined partial runs. Exact Compose regression command is
recorded in `python-regression-reuse.json` (`docker compose ... --profile regression
run --rm regression`), wrapper 3428.969s. All 104 regression input files and the
immutable test-image config/rootfs match. CURRENT_TASK permits reuse for unchanged
inputs and prohibits unnecessary unchanged PostgreSQL/restore/recovery reruns.
This Python evidence validates neither changed frontend nor the changed scan
helper. The changed frontend's complete regression and affected gates were run
fresh above. No old frontend regression is claimed for this repair.

Exact retained Python regression command (not rerun for this UI repair):

```text
docker compose --env-file C:\code\xai-decision-auditor\artifacts\interactive-verification\resume-20261015b\local\config.env -f deployment/compose.yaml -f deployment/compose.test.yaml --profile test --profile operator -f C:\code\xai-decision-auditor\artifacts\interactive-verification\resume-20261015b\override.json --profile regression run --rm regression
```

Exact final `git status --short --untracked-files=all` (includes preceding authorized work):

```text
 M README.md
 M deployment/Dockerfile.frontend
 M deployment/compose.yaml
 M deployment/tests/scan.py
 M deployment/tests/verify.py
 M deployment/tests/workspace.py
 M docs/ARCHITECTURE.md
 M docs/CURRENT_TASK.md
 M docs/PROJECT_REPORT.md
 M docs/SUPERVISOR_HANDOFF.md
 M frontend/browser/authenticated.spec.ts
 M frontend/browser/workbench.spec.ts
 M frontend/contracts/openapi.json
 M frontend/playwright.config.ts
 M frontend/src/App.tsx
 M frontend/src/api/contracts.ts
 M frontend/src/auth/session.tsx
 M frontend/src/components/Shell.tsx
 M frontend/src/components/ui.tsx
 M frontend/src/pages/AuditTrail.tsx
 M frontend/src/pages/CaseAnalysis.tsx
 M frontend/src/pages/ModelCard.tsx
 M frontend/src/pages/Overview.tsx
 M frontend/src/pages/Reliability.tsx
 M frontend/src/pages/Review.tsx
 M frontend/src/pages/SignIn.tsx
 M frontend/src/styles/app.css
 M frontend/tests/app.test.tsx
 M src/aletheia/application/api.py
 M src/aletheia/application/release.py
 M src/aletheia/application/schema.py
 M src/aletheia/application/store.py
 M tests/application/test_postgres_api.py
?? deployment/tests/interactive_browser.py
?? deployment/tests/interactive_stack.py
?? frontend/browser/interactive.spec.ts
?? frontend/src/api/analyses.ts
?? frontend/src/pages/Analyses.tsx
?? frontend/src/pages/LocalSession.tsx
?? frontend/tests/analyses.test.tsx
?? frontend/tests/case-fixtures.json
?? frontend/tests/product-copy.test.ts
?? migrations/versions/0004_case_input.py
?? src/aletheia/application/case_input.py
?? tests/application/test_case_input.py
?? tests/application/test_case_workflow.py
```
