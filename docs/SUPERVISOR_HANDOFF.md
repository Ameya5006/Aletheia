# Aletheia — Supervisor Handoff

## 1. Current Milestone and Status

Phase 4 Repair — Verify the Locked Data Boundary, 2026-10-03.
Implemented and verified locally; independent external supervisor review remains
pending. Phase 4 is not claimed approved. Phase 5 did not begin.

Starting checks confirmed branch main, HEAD and local origin/main both
1edaedd031c8cdd6a59bf2575bc74f96f74cdc66, and only the user-owned modification
to docs/CURRENT_TASK.md. AGENTS.md and CURRENT_TASK.md were read completely.
No commit, push, staging, merge, branch change, or remote mutation was performed.

## 2. Root Cause, Old Assumption, and Correction

The old test invented sgc-0801 through sgc-1000 as held-out membership and
sent prepared first-800-row predictors directly to evaluate_models(). Actual
stratified membership is scattered throughout the source file. Disjointness
from an invented suffix did not prove the locked leakage boundary or exercise
training selection. This was a test-evidence defect, not a demonstrated leak in
production source.

The new fixture creates 1,000 synthetic raw rows, a temporary checksum-bound
dataset identity, temporary experiment TOML, and a temporary split lock using
Phase 3 generation, writing, loading, and verification. Only the orchestration's
dataset identity provider is replaced; the fixed protocol is loaded and
validated by the real experiment loader. No source logic is stubbed out.

The integration test calls real run_baseline() through:

raw-data loading → schema validation → target mapping → feature-role enforcement
→ split-contract loading/verification → training-key selection → training-only
cross-validation → manifest construction → immutable artifact publication.

Before each real evaluator call, the capture guard requires all and only the
800 verified unique training keys, no verified held-out key, and exact aligned
predictor/target rows. The split has 800 training and 200 held-out keys, with
both partitions crossing the old row-800 boundary. Both calculations must be
deterministic and both models must use identical five-fold membership. The
stored manifest must record training-only CV, false held-out evaluation, null
fitted model, and no nested held-out result or prediction fields. Publication
must contain only manifest.json; an overwrite attempt is refused and leaves
the manifest unchanged.

## 3. Files Changed, Decisions, and Documentation

- tests/conftest.py: adds the synthetic raw/config/verified-split fixture;
  existing unit-test fixtures are unchanged.
- tests/integration/test_baseline_pipeline.py: replaces the prepared-feature
  test with the full offline orchestration test and membership/publication guards.
- docs/PROJECT_REPORT.md: narrows current authorization, adds repair evidence,
  timeline/rationale, verified problem and recovery, interview and viva answers.
- docs/SUPERVISOR_HANDOFF.md: replaces the prior milestone's handoff with
  current repair evidence.

Decision: verify actual membership at the orchestrator/evaluator boundary.
Synthetic temporary data avoids network and committed/local raw-data dependence;
its metrics are software-test output and do not support empirical ML claims.
No architecture, dependency, source, production config/split, or dataset changed.
ARCHITECTURE.md and EXECUTION_PLAN.md remain unchanged because this repair adds
verification within the existing architecture and authorized sequence.
CURRENT_TASK.md is user-owned and was not edited by Codex.

## 4. Commands and Exact Results

Commands used the repository's .venv interpreter (Python 3.12.10).
Ignored data/processed basetemp paths and disabled pytest cache follow the
previously verified Windows workaround. All checks below exited 0.

    git status --short --untracked-files=all
      starting result: only " M docs/CURRENT_TASK.md"
    git branch --show-current
      main
    git rev-parse HEAD
      1edaedd031c8cdd6a59bf2575bc74f96f74cdc66
    git rev-parse origin/main
      1edaedd031c8cdd6a59bf2575bc74f96f74cdc66

    .\.venv\Scripts\python.exe -m ruff format tests/conftest.py tests/integration/test_baseline_pipeline.py
      1 file reformatted, 1 file left unchanged
    .\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp data/processed/pytest-phase4-repair-targeted tests/integration/test_baseline_pipeline.py
      1 passed, 10 warnings in 1.50s
    .\.venv\Scripts\python.exe -m pip check
      No broken requirements found.
    .\.venv\Scripts\python.exe -m ruff check .
      All checks passed!
    .\.venv\Scripts\python.exe -m ruff format --check .
      43 files already formatted
    .\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp data/processed/pytest-phase4-repair-final -m "not live_data"
      66 passed, 1 deselected, 25 warnings in 5.88s
    git diff --check
      no whitespace errors; LF-to-CRLF advisory warnings only
    git diff -- tests/conftest.py tests/integration/test_baseline_pipeline.py
      reviewed the test-only implementation diff
    git diff --name-only
      only CURRENT_TASK.md and the four authorized repair paths

All 25 suite warnings are the existing scikit-learn deprecation for the approved
explicit L2 parameter (integration 10, evaluation unit tests 10, preprocessing
unit tests 5). The live-data test was deselected; no network test was run.

Temporary run inspection command:

    Get-ChildItem -Recurse -File data/processed/pytest-phase4-repair-final -Filter manifest.json | ForEach-Object { $_.FullName; Get-ChildItem -LiteralPath $_.DirectoryName -Force | Select-Object Name, Length }

The orchestration integration run was
data/processed/pytest-phase4-repair-final/test_training_only_baseline_to0/runs/baseline-v1-20261003T054708184850Z-6ed815c15f/.
It contained only manifest.json, 15,872 bytes. The separate publication unit
test run also contained only manifest.json, 15,311 bytes. The integration test
asserted no other run/staging entry or fitted model file and verified that the
stored manifest equals the returned manifest after overwrite refusal.

Preservation commands (executed before and after implementation):

    Get-FileHash docs/CURRENT_TASK.md | Select-Object -ExpandProperty Hash
    Get-FileHash artifacts/runs/baseline-v1-20261003T044245447896Z-f528b34971/manifest.json | Select-Object -ExpandProperty Hash

Unchanged SHA-256 identities:

- User-owned CURRENT_TASK.md:
  8ede7881e9bcfb5644e1788e579c320d55e17c388fef22d9979ea7a7dd2c244e.
- Preserved Phase 4 manifest:
  58c60af7143f0df09f429cb282e544f897cb7940bce526284fbc595d513e0229.

The preserved Phase 4 run and previously recorded metrics are unchanged. No
production baseline was rerun. No held-out predictions or metrics were
calculated, no held-out preprocessing was fitted, and no setting was tuned on
held-out rows. Synthetic keys/targets were used for split construction and
verification; only the verified training subset entered model evaluation.

## 5. Problems, Limitations, and Unresolved Questions

External review identified the false sequential holdout assumption and incomplete
integration path; both are repaired and verified. An initial patch was rejected
because it requested two operations on the same file; status confirmed no
changes and separate valid updates succeeded. A delete-based handoff rewrite
also failed without changing the file; an in-place update replaced its contents.
No source-code defect was exposed and no additional ML correctness issue was found.

This test proves the synthetic locked-membership orchestration boundary. It
does not establish real held-out performance or prove every semantic, temporal,
entity, or feature leakage risk absent. Existing fold-local fit tests remain
complementary. Existing dataset representativeness and deprecation limitations
remain; no new ML experiment claim is made. No unresolved repair issue is known.
External acceptance is pending; the supervisor determines any next task.

## 6. Final Git Status and Review Boundary

git status --short --untracked-files=all:

     M docs/CURRENT_TASK.md
     M docs/PROJECT_REPORT.md
     M docs/SUPERVISOR_HANDOFF.md
     M tests/conftest.py
     M tests/integration/test_baseline_pipeline.py

No raw dataset, generated run, cache, or temporary output appears in status.
Only the four authorized paths were changed by Codex; CURRENT_TASK.md retains
the user's pre-existing modification. Git branch/HEAD/local origin/main remain
at the verified starting identities. No commit or push was made.

Review evidence: inspect the fixture and capture guard, split verification in
src/aletheia/data/split.py, selection in src/aletheia/ml/baseline.py, the
temporary manifest above, test/check outputs, and the incremental report diff.

Recommended commit message: test: verify Phase 4 locked data boundary.
Suggested next step: user inspection, user commit/push, then independent external
supervisor review. This suggestion does not authorize Phase 5 or another task.
