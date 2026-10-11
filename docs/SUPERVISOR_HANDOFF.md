# Supervisor Handoff — Macro Milestone 3

## 1. Current milestone and status

Current task: final Macro Milestone 3 reproducibility repair. Macro Milestones
1–2 are completed; Macro Milestone 3 remains implemented, pending external review.
The supervisor reports that uploaded evidence passed internal technical,
chronology, metric, binding and privacy review. This does not authorize Macro
Milestone 4. Starting `main`, HEAD and origin/main remained
`49a1a8c7fdc5cbfb197b7533d3d40a8e9aa6f2eb`; status matched the authorized inventory
and stash remained `c6b91a13bf4338e559dfaad49f850dd719f5ca47`.

Files changed in this final repair: new repository-root `.gitattributes`,
docs/PROJECT_REPORT.md and this handoff only. Documentation consistency inspection
found the seven requested documents agree on completed Macro Milestones 1–2,
implemented Macro Milestone 3 pending review, and unimplemented application/MLOps/
deployment; earlier foundation/credit states are explicitly historical.

Symptom: an LF checkout produces a different split-lock byte digest from the
frozen Windows CRLF file. Root cause: SHA-256 includes line-ending bytes even
when parsed JSON is identical. Independently read the committed Git blob as
bytes: LF SHA-256
`9543d65d1dc4fc2ef3e3f6a4f43fa88828550241a78291876d289d3e83755ecd`;
in-memory CRLF conversion exactly reproduces the frozen/current working-copy
SHA-256 `a3ca2af19215bcf965afecaa75a1c6ec2912f3cf832f2aaec82562ec7855446d`.
Committed/converted/working JSON objects are equal; `membership_sha256` remains
`6879c9e652887c4a8b59797dd2260ad79795958fb3eebff1b22c3fe33b075316`.

Resolution: `.gitattributes` contains the single narrow rule
`configs/splits/healthcare_uci296_v1.lock.json text eol=crlf`.
Rewriting frozen evidence was rejected: it would alter reviewed bindings rather
than fix checkout representation. No split bytes/membership, model, results,
threshold, configuration, implementation or tests changed. Future structured
artifacts should specify canonical JSON hashes alongside exact-byte integrity
hashes; this is advisory and does not change current methodology or architecture.

Final repair verification commands/results (all exit 0):

- `git check-attr text eol -- configs/splits/healthcare_uci296_v1.lock.json`:
  `text: set`, `eol: crlf`.
- `.\.venv\Scripts\python.exe -m aletheia.domains.healthcare.audit inspect`:
  `status: verified`, no patient-data loading, predictions or new holdout access.
- `.\.venv\Scripts\python.exe -m pip check`: no broken requirements.
- `.\.venv\Scripts\python.exe -m ruff check .`: all checks passed.
- `.\.venv\Scripts\python.exe -m ruff format --check .`: 69 files formatted.
- `.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp data/processed/pytest-m3-final-repro-offline -m "not live_data"`:
  **122 passed, 1 deselected, 25 existing credit deprecation warnings in 33.50s**.
- `git diff --check`: passed; `git diff --cached --name-only`: empty.
- Independent committed-byte LF/CRLF hash and JSON-equality assertions passed;
  all 79 protected files matched the pre-repair snapshot. All four audit hashes
  before/after matched exactly (full unchanged hashes in section 8).

Only authorized `git add -N -- .gitattributes` exposed the new file in the diff;
no contents were staged. The first attempt was blocked by sandbox permission on
`.git/index.lock`; command escalation succeeded without additional Git changes.
Complete review export: `%TEMP%\aletheia-macro3-final-review.patch`, generated
from `git diff --binary --full-index HEAD --` with byte-preserving subprocess
output. It includes every current milestone change, PRODUCT_REQUIREMENTS.md,
DEPLOYMENT_ARCHITECTURE.md and .gitattributes; it is outside repository status.
The existing evidence ZIP/artifacts remain untouched. No audit freeze/run,
retraining/reselection, production predictions, new holdout access, later
milestone, commit or push occurred. Remaining historical-data, sparse-group,
XAI/stability sampling, no-recourse and absent deployment limitations remain.
Advisory next step: external supervisor review of the complete patch. Future
canonical JSON hashing requires a separately approved protocol; do not retrofit
it into frozen evidence.

### Earlier documentation repair record (historical)

Current task: external-supervisor-directed Macro Milestone 3 documentation-only
review repair. Macro Milestones 1 and 2 are completed; Macro Milestone 3 remains
implemented and locally verified, pending external review. The starting file
inventory matched the reported Macro Milestone 3 work; new files retained their
existing intent-to-add index state. Repair edits only README.md,
docs/PRODUCT_REQUIREMENTS.md, docs/DEPLOYMENT_ARCHITECTURE.md,
docs/ARCHITECTURE.md, docs/EXECUTION_PLAN.md, docs/PROJECT_REPORT.md and this handoff.
Stale planned/current statements are reconciled and earlier states labelled
historical. There is no architecture or methodology change in this repair.

Fresh repair verification: pip check exit 0 (no broken requirements); Ruff lint
exit 0 (all checks passed); Ruff format check exit 0 (69 files already formatted);
complete offline pytest exit 0, **122 passed, 1 deselected, 25 existing credit
L2-deprecation warnings in 33.94s**. Command:
`.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp data/processed/pytest-m3-review-repair-offline -m "not live_data"`.
Read-only `.\.venv\Scripts\python.exe -m aletheia.domains.healthcare.audit inspect`
exit 0, status `verified`; no new predictions or holdout access. No freeze/run,
model fitting or selection occurred during the repair. The sections below retain
the implementation evidence; their freeze/run and earlier test commands are
historical, not fresh repair commands.

Implemented and locally verified; external supervisor review pending. Starting main, HEAD and origin/main: 49a1a8c7fdc5cbfb197b7533d3d40a8e9aa6f2eb. Only user-owned CURRENT_TASK.md was modified. Its contents and the existing credit WIP stash remain untouched. No commit, push, branch/remote mutation or later milestone began.

## 2. What was implemented

Complete calibrated-probability source-field sampled Shapley explanations; fitted transformed/source lineage; repeated-sample global evidence; deterministic local structure with a fixed synthetic publication example; bounded recording stability; support-guarded race/gender/source-age subgroup metrics with patient uncertainty; explicit no-recourse feasibility; frozen protocol and exclusive aggregate audit artifacts. No audit function fits preprocessing, model or calibration, reselects a model, or tunes a threshold.

## 3. Files created/modified and preserved

Created: configs/audit/healthcare_audit_v1.toml; docs/decisions/0007-healthcare-explanation-responsible-audit.md; healthcare audit.py, explain.py, fairness.py, stability.py, counterfactual.py; tests/healthcare/test_audit.py and test_audit_integration.py.

Modified: README.md; docs/ARCHITECTURE.md; EXECUTION_PLAN.md; PROJECT_REPORT.md; SUPERVISOR_HANDOFF.md; HEALTHCARE_DATASET_AUDIT.md; model_cards/healthcare_readmission_v1.md; decisions/0006-healthcare-model-selection-protocol.md. CURRENT_TASK.md is a preserved user modification.

Intentionally unchanged: AGENTS.md, prompt.txt, task contents, dataset/feature/split/model configs and lock, original model/joblib and all original experiment files/claim, foundation/modelling/experiment code, dependencies, credit code and stash. Generated audit evidence is ignored under artifacts/healthcare-audit-v1 only.

## 4. Important decisions

Explain the entire sigmoid-calibrated callable, with 13 original fields and 43 transformed columns. Paired permutation Monte Carlo interventional Shapley uses existing packages; SHAP was considered, not installed. Reference: 64 seeded training encounters, 32 orders plus reverses, sampled reference-probability baseline. Three 128-encounter training samples give descriptive repeat ranges, not confidence intervals. Stability fixes explanation paths for 16 cases × five +/-1 lab/procedure recording corrections. Fairness retains source categories; support requires 200 encounters/100 patients/20 positives/20 negatives; threshold stays 0.5; 200 subgroup patient-cluster draws give marginal 95% intervals. Exact counts below 20 are suppressed. No clinically reviewed mutable field or cost exists, so recourse is refused. See ADR 0007.

## 5. Historical implementation tests/checks actually executed

All use .venv/Scripts/python.exe. Pytest disables cache and uses ignored data/processed temporary paths.

- pip check: exit 0, No broken requirements found.
- ruff check .: exit 0, All checks passed!
- ruff format --check .: exit 0, 69 files already formatted.
- pytest -p no:cacheprovider --basetemp data/processed/pytest-m3-final-unit tests/healthcare/test_audit.py: exit 0, 25 passed in 2.48s.
- pytest -p no:cacheprovider --basetemp data/processed/pytest-m3-final-integration tests/healthcare/test_audit_integration.py: exit 0, 10 passed in 9.06s.
- pytest -p no:cacheprovider --basetemp data/processed/pytest-m3-final-healthcare tests/healthcare: exit 0, 56 passed in 13.29s.
- pytest -p no:cacheprovider --basetemp data/processed/pytest-m3-final-offline -m "not live_data": exit 0, 122 passed, 1 deselected, 25 existing credit L2-deprecation warnings in 17.46s.
- audit freeze: exit 0, protocol frozen, no audit outcomes calculated.
- audit run: exit 0, status verified, original model unchanged and one guarded subgroup access.
- audit inspect: exit 0, status verified; saved hashes, bindings, inventory and privacy passed without new predictions.
- git diff --check: exit 0. Exact final git status is in the user response; no data, caches, temporary output or generated healthcare record appears there.

## 6. Exact result evidence

Global mean absolute probability contributions: prior inpatient visits 0.032975 (range 0.028624–0.036702), stay 0.007839, diagnoses 0.005413, diabetes medication indicator 0.003951, medication count 0.003593. All 13 fields/repeats are recorded. Synthetic local probability 0.127821691881, baseline 0.108475507333, summed signed contributions 0.019346184548. Fitted sigmoid coefficients a=1.046740791844, b=0.093210594239 convert clipped base-probability logits; they are not clinical feature effects or the previous holdout diagnostic regression.

Stability: 80 comparisons; mean top-3 overlap 0.95 (minimum 1/3), absolute-rank correlation 0.945536 (minimum 0.631868), normalized L1 0.077479 (maximum 0.516299). Mean absolute probability change 0.002753, maximum 0.033485. Three comparisons below overlap reference 2/3, five above distance reference 0.25; zero class crossings, unchanged perturbations or undefined metrics. Bounds: labs 1–132, procedures 0–6. Average similarity coexists with local instability.

Fairness: 15/21 subgroup slots supported: five race categories including missing, two genders, eight age bands. Asian, unknown/missing gender, youngest two bands and missing age withheld. Missing race: 410 encounters/40 positives. Nine metrics with all 200 valid interval replicates per supported group. Female/Male ROC-AUC 0.629115 [0.608449,0.648161] / 0.650909 [0.632397,0.673503]; AfricanAmerican/Caucasian AP 0.221488 [0.166015,0.291205] / 0.195458 [0.176630,0.215708]; age [30-40)/[90-100) ROC-AUC 0.795981 [0.729181,0.849195] / 0.587109 [0.514392,0.660598]. These are separate estimates, not adjusted disparity tests. Recall ranges 0–0.068966, specificity 0.993856–1, FPR 0–0.006144, FNR 0.931034–1, positive prediction rate 0–0.013550. Many groups have no alerts. No threshold tuning or fairness certification followed.

Counterfactual: no_defensible_recourse / no_feasible_scenario, no search, zero candidates. The worked synthetic example refuses reducing prior inpatient visits or medication count because it rewrites history/care.

## 7. Holdout access and reproducibility

Protocol frozen at 2026-10-11T05:15:09.910670+00:00 before outcomes; manifest completed 2026-10-11T05:17:30.784462+00:00. One exclusive audit claim preceded predictions on 19,535 holdout encounters/13,812 patients. The original model evaluation/claim is preserved. A failed audit claim consumes access; no automatic retry or alternate production path exists. Source/schema/split integrity and already-frozen structural counts precede new prediction. Original bindings were verified again afterward. Software: Python 3.12.10, scikit-learn 1.9.0, pandas 3.0.5, NumPy 2.5.3, SciPy 1.18.1; seeds/config/code/test/data/split/model hashes are in the manifest.

## 8. Artifacts and hashes

Exactly four ignored audit files: protocol.json, holdout.claim, results.json, manifest.json. Full SHA-256:

- Model: 8c3a99dd8dfe20d2a3a0a721637b4be500ee1b32843f7cefc3af265f07262f7a
- Selection: 85db5e79faacc80d9818b235c4e8338be0aeb10fbcf89da2f3bc56e87172e9a7
- Split membership: 6879c9e652887c4a8b59797dd2260ad79795958fb3eebff1b22c3fe33b075316
- Audit config: 36c0a12c710a2cf04ce650a780d165d72eea281479db3aa34ae7433f96b8804c
- Canonical protocol: fae9acd4c95da774faa1e20a84129146faeeeef1ac866d809ac95df77a7aa04f
- Protocol file: 2f5ed6f4427ee64c145a8e72a1f89c398e1303ae12a8386ecf2ff28e71b49cb2
- Results file: 2d073fa0d0bbbd4debfdf445cd80ec478fef0f7098c7ef356dbb3edd28894ea8
- Audit claim: 8844e211c51259ffee18e81514f4aac6974ca1e7c1d867054a258de477a0e9fd
- Manifest file: 3fbbf27c0d3489768bc457f21cc5e1ec7b4f2326c7b5b5a35b3d54ab20e12b01

## 9. Privacy inspection

Strict schema inspection passed. Real raw records, row/identifier values and unrestricted patient predictions/attributions are absent. Only aggregates and the protocol-fixed synthetic local example are published. Exact counts below 20 are suppressed. This is not formal differential privacy or physical WORM storage. Local exclusive writes prevent accidental overwrite, not malicious administrator deletion.

## 10. Problems and recovery

Initial synthetic integration: 20 unit tests passed, nine setups failed manifest binding. Existing write_once returned an LF-payload digest while Windows persisted CRLF bytes. The new audit hashes persisted bytes after exclusive publication; original experiment code/evidence was preserved. Recovery and final tamper/privacy tests pass; no real holdout claim existed during the fix.

The first protocol patch lacked configs/audit; creating only that authorized directory resolved it. Ruff import/long-literal findings were fixed before freezing. A documentation patch reported context failure after README edits were visible; current diff inspection preserved valid work, then smaller patches completed remaining files. A multiline Python/PowerShell inspection produced no output and was not counted as verification; explicit --% transport yielded successful bindings. The report documents actual symptoms, cause, investigation, rejected approaches, fixes, tests and lessons. No empirical method/model failure occurred.

## 11. Known limitations

Historical data without time/hospital external validation; missing/sparse groups and prevalence/case-mix dependence; marginal hybrids and finite XAI samples; recording sensitivity without clinician validation; no defensible intervention space; empirical-bootstrap zero-event intervals cannot prove zero population rates; no paired disparity or multiple-comparison inference, clinical validation or fairness certification. No latency/security/deployment claim.

## 12. Architecture changes

Five healthcare-only research modules call existing foundation/model contracts. No public API, database schema, fitted artifact migration, new package or hosted service. Similar-case retrieval, backend, frontend, LLM/RAG, registry, deployment and additional training remain outside this task.

## 13. Documentation and evidence to inspect

Repair review should also inspect PRODUCT_REQUIREMENTS.md and
DEPLOYMENT_ARCHITECTURE.md: they now agree with the five-milestone roadmap and
existing model/audit evidence. Selected future tools remain unimplemented;
counterfactual feasibility does not imply actionable recourse. The external
portable bundle is `%TEMP%\aletheia-macro3-review-evidence.zip`; its verification
file records inspect output, all four audit file hashes, HEAD, exact status and
the verification commands. No raw data or fitted model is included.

Bundle created and verified at
`C:\Users\agarw\AppData\Local\Temp\aletheia-macro3-review-evidence.zip`.
Exactly five entries: protocol.json, holdout.claim, results.json, manifest.json
under `artifacts/healthcare-audit-v1/`, plus VERIFICATION.txt. Each copied entry's
SHA-256 matches its existing source (full hashes in section 8). ZIP SHA-256:
`0be3b3792f11579cbb064001132a09a160751b66af29dfdee33a367e1593caf6`.
Git status immediately before/after ZIP creation matched exactly. All 74 protected
source/test/config/governing/dependency/model/audit files matched the pre-repair
snapshot; refs/stash remained `c6b91a13bf4338e559dfaad49f850dd719f5ca47`.
The first packaging attempt failed before ZIP creation because Windows PowerShell
had not loaded System.IO.Compression; explicitly loading that assembly and
System.IO.Compression.FileSystem succeeded. No repository artifact was changed.
Repair `git diff --check` passed; exact final status is supplied to the user and
in the bundle. CURRENT_TASK.md remains the original user-owned modification.

README, architecture, execution plan, project report, dataset-audit context, model card, ADR 0006 status/addendum, new ADR 0007 and this handoff are current. Inspect the audit TOML, five modules, two new tests, four audit files and unchanged six original model-run files. The report includes component responsibilities, every global field, supported subgroup point estimates, uncertainty, the no-result example, recovery evidence and viva/interview notes. Use python -m aletheia.domains.healthcare.audit inspect; do not rerun/delete a claimed audit/model experiment.

## 14. Unresolved questions

External supervisor review; contemporary external data; clinical recording/intervention/joint feasibility; better pre-registered attribution samples/conditional reference; reviewed operational threshold and disparity inference. None is automatically authorized by completion.

## 15. Advisory next step and Git recommendation

Stop after Macro Milestone 3. External supervisor reviews evidence and determines any future task. Recommended user-performed commit message: feat: add healthcare XAI and responsible audit. Codex did not commit or push.
