# Aletheia — Supervisor Handoff

## 1. Current Milestone and Status

Phase 4 — Leakage-Safe Baseline Pipeline: implemented and verified by Codex,
pending external supervisor review. Phase 5 and later work remain blocked.
No external approval of Phase 4 is claimed.

## 2. Verified Recovery State

Branch `main`, HEAD and local `origin/main` both resolve to
`65f83c668a4f745ffd6dc74a9e21b81cb059712c`. Latest two commits:
`65f83c6 docs: reconcile Phase 3 architecture state` and
`f19f869 feat: build reproducible Aletheia data foundation`.

This was a continuation with authorized Phase 4 changes already present, not a
clean initial attempt. Every changed/untracked path matched CURRENT_TASK's
allowlist; no unexpected path was present. The original clean-start state was
not re-created or inferred. Existing source/configuration/tests/ADR/run and valid
report edits were preserved. CURRENT_TASK was read but not edited by Codex;
its SHA-256 remained
`a4a9afcd53f297686e44b77849f5a4f29d7f45b4f451cdc9f34b03a6155ad989`.

## 3. Implemented and Verified Requirements

- Versioned `baseline_v1.toml` freezes dataset/policy/split/target identity,
  preprocessing, two model configurations, CV, metrics, threshold and class.
- One ColumnTransformer inside each fresh Pipeline scales only `laufzeit` and
  `hoehe`; the other 13 fields use explicit contract-derived one-hot categories
  with unknown-category refusal. Output is 59 columns with original-field
  mapping, including documented but unobserved `verw=7`.
- Prior dummy and L2 Logistic Regression (`C=1.0`, `lbfgs`, no class weights,
  `max_iter=1000`) use identical five-fold StratifiedKFold membership, shuffled
  with seed 42. Every fit uses 640 fold-training rows and scores 160 validation
  rows from the locked 800-row training partition.
- ROC-AUC is primary; eight supporting metrics use adverse class 1.
  Probability column selection finds label 1 in `classes_`.
  Threshold 0.5 is fixed and descriptive; no threshold/model search occurred.
- A versioned JSON manifest records required identities, configurations,
  fold/per-fold/aggregate evidence, feature lineage, environment, source-control
  state, time, and limitations. Publication stages and validates JSON, flushes,
  atomically renames, and refuses an existing run ID.
- Permanent problems/recovery rule is in AGENTS. PROJECT_REPORT contains
  implementation/data flow, decisions, CV interpretations, concepts, Phase 3
  problems, Phase 4 recovery, interview/viva notes, resume evidence and limits.
- Architecture reflects actual Phase 4 scope. EXECUTION_PLAN keeps the proposed,
  unimplemented code-intelligence milestone after core research and basic
  application boundaries, requiring its own authorization and dependencies.

No held-out predictions/metrics or final fitted model were produced.

## 4. Files Created and Modified

Created during the interrupted Phase 4 attempt and preserved:

```text
configs/experiments/baseline_v1.toml
docs/decisions/0002-training-only-baseline-protocol.md
src/aletheia/ml/__init__.py
src/aletheia/ml/preprocess.py
src/aletheia/ml/models.py
src/aletheia/ml/evaluate.py
src/aletheia/ml/baseline.py
src/aletheia/experiments/__init__.py
src/aletheia/experiments/manifest.py
src/aletheia/experiments/artifacts.py
tests/unit/test_preprocess.py
tests/unit/test_models.py
tests/unit/test_evaluate.py
tests/unit/test_manifest.py
tests/integration/test_baseline_pipeline.py
```

Modified: AGENTS.md; docs/ARCHITECTURE.md; docs/EXECUTION_PLAN.md;
docs/PROJECT_REPORT.md; docs/SUPERVISOR_HANDOFF.md; src/aletheia/config.py;
src/aletheia/contracts.py; tests/conftest.py.
CURRENT_TASK is the separate user-owned modification.

This continuation completed report/handoff work and corrected architecture
manifest details, the fit-spy description, and the stale roadmap advisory.
It did not rewrite the recovered implementation.

Intentionally unchanged: prompt.txt, CLAUDE.md, DATASET_AUDIT.md, ADR 0001,
Phase 3 dataset/feature/split contracts and data modules, dependency files.
No new dependency or later-phase implementation was added.

## 5. Decisions and Architecture Implications

Explicit domains avoid treating integer codes as equally spaced quantities and
preserve empty documented levels. Fold-local fitting prevents validation
statistics from influencing their own fit. Shared folds make model comparisons
consistent. A prior dummy provides a no-signal reference; fixed Logistic
Regression supplies the simple interpretable reference without search.

Only the approved research modules and manifest publication slice were added.
No API/schema, database, tracking service, deployment, or model-serialization
migration occurred. Fitted persistence remains a later decision. The local
JSON store is sufficient for current single-user evidence.

## 6. Tests and Exact Results

Executed using the existing Python 3.12.10 environment:

```text
python -m pip check
exit 0: No broken requirements found.

python -m ruff check .
exit 0: All checks passed!

python -m ruff format --check .
exit 0: 43 files already formatted

python -m pytest -p no:cacheprovider --basetemp data/processed/pytest-phase4-final -m "not live_data"
exit 0: 66 passed, 1 deselected, 25 warnings in 6.52s
```

The 25 warnings concern scikit-learn's deprecated explicit `penalty="l2"`
argument, retained because the task fixes it. Live-data/network tests were
deselected. Earlier recovery also passed 66 tests (27.95s); final recovery
verified the same recovered source and tests.

Tests cover feature allocation, explicit domains, stable schema/verw=7, unknown
categories, forbidden model fields, fold-local scaler/encoder fits, five-fold
coverage/disjointness, shared folds, class orientation, known metrics, class-1
probability selection, deterministic repetitions, dummy sanity, logistic
constructor, mapping, manifest scope/shared-fold refusal, and atomic publish/
overwrite refusal. The synthetic integration test starts from approved-style
prediction fixtures and writes a manifest. The explicit local baseline below
additionally exercises actual verified Phase 3 loading/validation/roles/split.

## 7. Local Baseline, Identity and Determinism

Executed in the preceding recovery:

```text
python -m aletheia.ml.baseline --raw-file data/raw/SouthGermanCredit.asc
exit 0; two equal complete calculations before one atomic publication
```

Preserved run:
`artifacts/runs/baseline-v1-20261003T044245447896Z-f528b34971/manifest.json`.

Identity:

- Dataset SHA-256:
  `5f363343f356ca38a0236baab849e472846399b2176ccc5bd686483dd8a7562f`.
- Split checksum:
  `af26b6036c6958a2dec48362fb1bfb075fca2ad7e482ed48ee7a49d7ec6d994b`.
- Training checksum:
  `f528b349719ac43b420aa1b3aea1499af784129a0efd4f977f355bbeba8b153e`.
- Experiment configuration SHA-256:
  `ce2e5cbdf0f7c5e349c61212a41eda5d4ee52b7a6f9df6a150674e70e3bd92bc`.
- Deterministic result payload SHA-256:
  `84f5a13a12ee8a7d01df0959659deeab0f609f724869dd8cccf9fd2b8aa0bf1b`.

Final recovery ran two fresh calculations and compared them with the preserved
run using this exact Windows PowerShell command:

```powershell
python --% -c "import hashlib,json; from pathlib import Path; from aletheia.ml.baseline import calculate_baseline; from aletheia.experiments.manifest import canonical_result_payload,validate_manifest; run=Path('artifacts/runs/baseline-v1-20261003T044245447896Z-f528b34971'); stored=json.loads((run/'manifest.json').read_text(encoding='utf-8')); a,_=calculate_baseline('data/raw/SouthGermanCredit.asc'); b,_=calculate_baseline('data/raw/SouthGermanCredit.asc'); assert canonical_result_payload(a)==canonical_result_payload(b)==canonical_result_payload(stored['results']); validate_manifest(stored); assert a['evaluated_row_count']==800; assert a['models']['dummy']['fold_membership_checksums']==a['models']['logistic_regression']['fold_membership_checksums']; assert stored['held_out_evaluation_performed'] is False; assert stored['fitted_model_artifact'] is None; assert [p.name for p in run.iterdir()]==['manifest.json']; print('PASS: two calculations equal preserved run; 800 rows; identical folds; manifest only; SHA256='+hashlib.sha256(canonical_result_payload(a)).hexdigest())"
```

Exit 0:
`PASS: two calculations equal preserved run; 800 rows; identical folds; manifest only; SHA256=84f5a13a12ee8a7d01df0959659deeab0f609f724869dd8cccf9fd2b8aa0bf1b`.

An additional in-memory evaluation guard independently asserted two inputs of
800 rows, 15 predictors, and disjointness from all locked held-out keys.
Only allowed Phase 3 identity/membership verification read the complete data;
held-out records were not examined for modelling or scored.

The manifest records creation time `2026-10-03T04:42:45.447896+00:00`,
base commit `65f83c668a4f745ffd6dc74a9e21b81cb059712c`, dirty state true,
and creation-state diff checksum
`d0d3cc20b02b93e7de03bad3d70eea991862a1988831c7330ce640460e95ac3b`.
Subsequent documentation edits naturally change the working-tree checksum.
The immutable run was preserved; it does not claim to capture later report text.

## 8. CV Results and Interpretation

Mean and population standard deviation across the five training validation
folds; full per-fold results are in the manifest:

| Metric | Dummy mean / SD | Logistic mean / SD |
|---|---|---|
| ROC-AUC | 0.5 / 0.0 | 0.7717633928571429 / 0.0339551982114617 |
| Average precision | 0.3 / 0.0 | 0.6047913914108355 / 0.0653266429439531 |
| Balanced accuracy | 0.5 / 0.0 | 0.6675595238095238 / 0.03388938840195412 |
| Adverse recall | 0.0 / 0.0 | 0.4708333333333334 / 0.03385016001931651 |
| Specificity | 1.0 / 0.0 | 0.8642857142857144 / 0.036333910623885364 |
| Precision | 0.0 / 0.0 | 0.6034170516236514 / 0.08121231916540307 |
| F1 | 0.0 / 0.0 | 0.5282096715023175 / 0.05128400365335037 |
| Log loss | 0.6108643020548935 / 1.1102230246251565e-16 | 0.5215789553988919 / 0.04189046412704899 |
| Brier score | 0.20999999999999996 / 0.0 | 0.17146090326447186 / 0.016688446381985626 |

Logistic Regression improves adverse/non-adverse ranking and both probability
losses relative to prior-only predictions within these training folds. At 0.5
it catches fewer than half of adverse validation cases on average. The dummy
predicts every validation case non-adverse. Undefined dummy precision is
reported as zero by explicit zero-division policy.

A false negative misses an actually adverse case; a false positive flags an
actually non-adverse case. Both matter; no defensible monetary cost ratio exists.
Threshold 0.5 is descriptive and not a lending recommendation. ROC-AUC measures
ranking, not calibration. Precision, average precision and probabilities are
limited by adverse oversampling. Standard deviations are fold variation, not
confidence intervals. No training-score gap was measured, so overfitting cannot
be conclusively diagnosed. No final model was selected.

## 9. Problems and Recovery

PROJECT_REPORT backfills the required verified Phase 3 problems: UCI TLS-chain
failure and certificate-validating Schannel fallback; temporary-directory
permissions; PowerShell syntax in Command Prompt; stray untracked git file;
negative-test construction/validation order; stale architecture wording; and
the distinction between file identity and explicit quantitative-range checks.

Phase 4 recovery encountered simultaneous shell creation failure (1056),
patch-context failures caused by incorrectly decoded UTF-8 symbols, and one
Python command quoting failure (`SyntaxError: invalid decimal literal`) before
any calculation ran. Sequential reads, explicit UTF-8 decoding, small patches,
and Windows-safe Python argument transport resolved these. Patch failures made
no changes; no unsandboxed file-write fallback was used. The user-requested stop
on patch failure was honored and work continued after renewed instruction.

No meaningful model-correctness failure occurred. The fixed Logistic Regression
argument produces the documented deprecation warning; an approved future
version must revisit its equivalent API before scikit-learn 1.10.

## 10. Limitations and Unresolved Questions

External supervisor acceptance is pending. The old, geographically narrow,
granted-credit-only, adverse-oversampled dataset has no dates/entity IDs and an
unknown amount transform; it cannot establish modern lending or temporal/
customer generalization. The combined personal-status/sex field and sparse
foreign-worker subgroup constrain later fairness analysis.

Held-out evidence remains sealed. XAI, recourse, stability, fairness, serving,
latency, final fitting, serialization and deployment remain unimplemented.
The current small manifest validator checks required top-level fields, scope,
row count, two model identities, shared folds, and prohibited held-out fields;
it is not a generic untrusted-artifact validator or full metric recomputation.
Concurrent publication and larger manifest-schema hardening remain future
engineering considerations.

## 11. Scope, Ignore and Documentation Checks

```text
git check-ignore -v data/raw/SouthGermanCredit.asc artifacts/runs/baseline-v1-20261003T044245447896Z-f528b34971/manifest.json
exit 0: .gitignore line 16 data/raw/; line 18 artifacts/

git diff --check
exit 0: no whitespace errors; LF-to-CRLF advisory warnings only
```

Run directory inspection found only manifest.json (16,494 bytes), no fitted
model or held-out output. Git status contains no raw or generated file.
PROJECT_REPORT, ARCHITECTURE, EXECUTION_PLAN, ADR 0002 and the permanent AGENTS
rule now agree on the Phase 4 boundary. No later phase began.

## 12. Final Git Status and Suggested Next Step

`git status --short --untracked-files=all`:

```text
 M AGENTS.md
 M docs/ARCHITECTURE.md
 M docs/CURRENT_TASK.md
 M docs/EXECUTION_PLAN.md
 M docs/PROJECT_REPORT.md
 M docs/SUPERVISOR_HANDOFF.md
 M src/aletheia/config.py
 M src/aletheia/contracts.py
 M tests/conftest.py
?? configs/experiments/baseline_v1.toml
?? docs/decisions/0002-training-only-baseline-protocol.md
?? src/aletheia/experiments/__init__.py
?? src/aletheia/experiments/artifacts.py
?? src/aletheia/experiments/manifest.py
?? src/aletheia/ml/__init__.py
?? src/aletheia/ml/baseline.py
?? src/aletheia/ml/evaluate.py
?? src/aletheia/ml/models.py
?? src/aletheia/ml/preprocess.py
?? tests/integration/test_baseline_pipeline.py
?? tests/unit/test_evaluate.py
?? tests/unit/test_manifest.py
?? tests/unit/test_models.py
?? tests/unit/test_preprocess.py
```

Codex did not stage, commit, push, merge or mutate branches. Recommended commit:

`feat: establish leakage-safe Aletheia baseline`

Supervisor evidence: inspect the complete authorized diff and new files, the
preserved manifest (particularly fold identity, per-fold metrics, feature map
and scope flags), tests, report, and ADR 0002. Suggested next step is external
review of Phase 4; the supervisor alone decides progression through a replacement
CURRENT_TASK. No further milestone is authorized by this handoff.
