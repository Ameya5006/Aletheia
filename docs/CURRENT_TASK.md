```markdown
# MILESTONE

Phase 4 Repair — Verify the Locked Data Boundary

# SUPERVISOR DECISION

Phase 4 implementation exists at commit:

`1edaedd031c8cdd6a59bf2575bc74f96f74cdc66`

External supervisor review found two blocking test gaps. Phase 4 is not approved until they are repaired. Phase 5 remains blocked.

# REQUIRED STARTING STATE

Before editing, verify:

- branch: `main`
- HEAD: `1edaedd031c8cdd6a59bf2575bc74f96f74cdc66`
- local `origin/main`: `1edaedd031c8cdd6a59bf2575bc74f96f74cdc66`
- working tree contains only the user-owned modification to `docs/CURRENT_TASK.md`

If any other path is modified or untracked, stop and report it.

# GOAL

Repair the Phase 4 integration test so it proves that verified split membership controls model evaluation.

# BLOCKING FINDING 1 — FALSE SEQUENTIAL HOLDOUT ASSUMPTION

`tests/integration/test_baseline_pipeline.py` currently invents this held-out partition:

`sgc-0801` through `sgc-1000`

This is not Aletheia’s approved split. The real locked held-out keys are scattered throughout the 1,000 source rows.

Replace this assumption with membership produced and verified through the Phase 3 split-contract functions.

The repaired test must prove that:

- the evaluation input contains every verified training key;
- the evaluation input contains no verified held-out key;
- exactly 800 rows enter cross-validation;
- a sequential row-number assumption cannot make the test pass accidentally.

# BLOCKING FINDING 2 — INCOMPLETE INTEGRATION PATH

The current integration test starts with prepared prediction features and calls `evaluate_models()` directly.

Add an offline synthetic integration test that exercises the actual Phase 3-to-Phase 4 orchestration through `run_baseline()`, or through `calculate_baseline()` followed by manifest publication:

1. raw-data loading;
2. schema validation;
3. target mapping;
4. feature-role enforcement;
5. split-contract loading and verification;
6. training-key selection;
7. training-only cross-validation;
8. manifest creation;
9. immutable artifact publication.

Use synthetic data and temporary files. Do not require network access or committed raw data.

Capture the row keys supplied to evaluation and compare them directly with the verified split membership.

# REQUIRED ASSERTIONS

The repaired integration test must demonstrate that:

- the split contains exactly 800 training keys and 200 held-out keys;
- the split is based on verified membership rather than row-number ranges;
- the evaluation keys equal the complete verified training-key set;
- evaluation keys are disjoint from the verified held-out-key set;
- exactly 800 rows enter cross-validation;
- the two models use identical fold membership;
- repeated calculations remain deterministic;
- the manifest records training-only cross-validation;
- `held_out_evaluation_performed` remains `false`;
- `fitted_model_artifact` remains `null`;
- no held-out metric or prediction field exists;
- the published run contains only `manifest.json`;
- no fitted model file is created;
- publishing over an existing run remains refused.

The test should fail if:

- any verified held-out key enters evaluation;
- any verified training key is missing;
- evaluated row count differs from 800;
- the manifest contains held-out predictions or metrics;
- a fitted model artifact is published.

# HELD-OUT RESTRICTIONS

Synthetic row keys and target values may be used only to construct and verify synthetic split membership.

Do not:

- calculate held-out predictions;
- calculate held-out metrics;
- fit preprocessing on held-out rows;
- tune any setting using held-out rows;
- inspect the real held-out partition for model performance;
- change the approved production split;
- change the preserved Phase 4 run;
- change previously recorded Phase 4 metrics.

# AUTHORIZED FILES

Codex may modify only:

- `tests/conftest.py`
- `tests/integration/test_baseline_pipeline.py`
- `docs/PROJECT_REPORT.md`
- `docs/SUPERVISOR_HANDOFF.md`

`docs/CURRENT_TASK.md` is user-owned and must remain unchanged by Codex.

No ML source, experiment configuration, architecture, dependency, dataset, generated artifact, API, frontend, database or deployment file is authorized.

If the repaired test exposes an actual source-code defect, stop and report the evidence before modifying source code.

# PROJECT REPORT REQUIREMENTS

Update `docs/PROJECT_REPORT.md` with this verified problem and recovery:

- the original test assumed that the final 200 row numbers formed the held-out partition;
- the actual stratified split uses scattered row keys;
- why the original assertion did not prove the real leakage boundary;
- how verified split membership replaced the row-number assumption;
- how the repaired integration test exercises the Phase 3-to-Phase 4 path;
- what could have gone wrong if the false assumption remained;
- how an interviewer should understand testing for data leakage;
- which code and test files demonstrate the correction.

Keep the report concise, technically accurate and useful for interview, viva and project-defence preparation.

Do not alter or fabricate earlier results, problems, metrics or implementation claims.

# SUPERVISOR HANDOFF REQUIREMENTS

Update `docs/SUPERVISOR_HANDOFF.md` with:

- repair status;
- root cause;
- old invalid assumption;
- corrected membership approach;
- integration path exercised;
- files changed;
- exact commands and checks run;
- exact results;
- confirmation that held-out predictions and metrics were not calculated;
- confirmation that the preserved Phase 4 metrics were unchanged;
- confirmation that Phase 5 did not begin;
- unresolved issues;
- exact final Git status;
- recommended commit message.

Do not claim external supervisor approval.

# REQUIRED VERIFICATION

Run:

```text
python -m pip check
python -m ruff check .
python -m ruff format --check .
python -m pytest -m "not live_data"
git diff --check
```

Use Windows-compatible temporary pytest and cache directories if the repository location causes permission errors.

Inspect the generated temporary test run and verify that it contains only `manifest.json`.

Confirm that no raw dataset, generated run, cache file or temporary output appears in Git status.

# EXPECTED FINAL GIT STATUS

The final status may contain only:

```text
 M docs/CURRENT_TASK.md
 M docs/PROJECT_REPORT.md
 M docs/SUPERVISOR_HANDOFF.md
 M tests/conftest.py
 M tests/integration/test_baseline_pipeline.py
```

`docs/CURRENT_TASK.md` is the user-owned task replacement and must not be modified again by Codex.

If any additional file appears, stop and explain it before recommending a commit.

# FINAL CODEX RESPONSE

Report:

1. repair status;
2. root cause;
3. old invalid holdout assumption;
4. corrected verified-membership approach;
5. complete integration path exercised;
6. tests added or changed;
7. files modified;
8. commands and checks run;
9. exact results;
10. confirmation that all and only verified training keys entered evaluation;
11. confirmation that held-out predictions and metrics were not calculated;
12. confirmation that preserved Phase 4 metrics did not change;
13. documentation updates;
14. unresolved issues and limitations;
15. confirmation that Phase 5 did not begin;
16. confirmation that Codex did not commit or push;
17. exact final `git status --short --untracked-files=all`;
18. recommended commit message.

Recommend:

`test: verify Phase 4 locked data boundary`

# STOP RULE

Stop after completing and verifying this Phase 4 repair.

Do not begin Phase 5.

Do not modify `docs/CURRENT_TASK.md`.

Do not commit or push.

The user will inspect the final Git status, commit and push the repair, and return it for independent external supervisor review.
```