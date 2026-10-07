# Supervisor Handoff — Macro Milestone 2

## 1. Current milestone and status

Macro Milestone 2's implementation and one locked-holdout evaluation are locally verified; external supervisor review is pending. The required global git diff --check remains failing only on trailing whitespace in user-owned CURRENT_TASK.md, which Codex may not change. Starting HEAD and local origin/main were both 9073c4531bcd01f70050450425c2e25b8b508abb on main. No commit or push was made. The user-owned CURRENT_TASK.md modification and WIP stash were not changed.

## 2. Implemented work and files

The frozen UCI 296 foundation feeds fold-local preprocessing, four bounded candidates, five outer and three inner patient-group folds, group-OOF sigmoid calibration, deterministic training repeat, immutable nested-CV and selection records, a checksum-bound trusted-local joblib artifact, and one guarded held-out evaluation with patient-cluster intervals. The healthcare CLI calls the experiment. The production records are ignored under artifacts/healthcare-model-v1.

Modified: README.md; docs/ARCHITECTURE.md; docs/EXECUTION_PLAN.md; docs/PROJECT_REPORT.md; docs/SUPERVISOR_HANDOFF.md; src/aletheia/domains/healthcare/__main__.py. The existing modification to docs/CURRENT_TASK.md is user-owned. Created: configs/experiments/healthcare_model_v1.toml; docs/decisions/0006-healthcare-model-selection-protocol.md; docs/model_cards/healthcare_readmission_v1.md; src/aletheia/domains/healthcare/modeling.py, evaluation.py and experiment.py; tests/healthcare/test_modeling.py and test_experiment.py.

## 3. Decisions and architecture

The 13 frozen predictors receive fold-fitted median imputation and scaling for eight numeric fields, and constant missing imputation plus one-hot encoding for five categorical fields. Unknown categories map to all-zero indicators for their field. Patient grouping is required at every CV and calibration fold; histogram boosting disables its internal row-level early stopping and uses a checked dense fold-local transform. Average precision is primary; candidates within 0.005 use Brier, ROC-AUC and log loss. Threshold 0.5 is descriptive. The evaluator checks complete nested-CV evidence, selection/config/split identities and artifact hashes before an exclusive holdout claim. No credit, API, registry, database, frontend or deployment boundary changed. See ADR 0006 and ARCHITECTURE.md.

## 4. Exact experiment evidence

Training: 79,808 encounters, 56,178 patients, 70,734 negatives and 9,074 positives. Two full training-only calculations agreed excluding wall-clock timing. Outer mean AP: dummy 0.113698, Logistic Regression 0.197312, Random Forest 0.196374, Histogram Gradient Boosting 0.199591. The selected histogram plus sigmoid had outer mean ROC-AUC 0.635554, Brier 0.097624 and log loss 0.340964. Final inner selection chose 15 leaves, 30 iterations and minimum leaf size 40. Forest training versus validation AP was 0.235960 versus 0.196374; selected histogram was 0.215586 versus 0.199591. No captured convergence warnings occurred.

Selection SHA-256: 85db5e79faacc80d9818b235c4e8338be0aeb10fbcf89da2f3bc56e87172e9a7. Deterministic training-results SHA-256: 152b87cc3e0bc2ccaa365d7ea7de192f3f128214203ce38a1b88704a8a576aa4. Fitted artifact SHA-256: 8c3a99dd8dfe20d2a3a0a721637b4be500ee1b32843f7cefc3af265f07262f7a. Recorded runtime versions: Python 3.12.10, scikit-learn 1.9.0, pandas 3.0.5, numpy 2.5.3 and SciPy 1.18.1.

One held-out evaluation: 19,535 encounters, 13,812 patients, 17,295 negatives and 2,240 positives. ROC-AUC 0.639473 [0.626640, 0.653593]; AP 0.202633 [0.184091, 0.221497]; balanced accuracy 0.502418 [0.500125, 0.505621]; recall 0.005357 [0.000452, 0.012309]; specificity 0.999480 [0.998931, 0.999858]; precision 0.571429 [0.200000, 0.693429]; F1 0.010615 [0.000902, 0.024124]; log loss 0.342237 [0.331423, 0.352035]; Brier 0.098255 [0.094170, 0.101733]. These are 95% intervals from 500 seeded patient-cluster resamples, seed 4242. At threshold 0.5: TN 17,286, FP 9, FN 2,228, TP 12. Calibration intercept 0.133640, slope 1.058929; curve points are in holdout.json. This threshold misses almost all positive encounters and is not clinically approved.

## 5. Checks actually executed

Final Python 3.12.10 checks: pip check exited 0, “No broken requirements found”; Ruff check exited 0, “All checks passed”; Ruff format check exited 0, “61 files already formatted”; targeted healthcare modelling tests exited 0, 10 passed in 2.91s; complete offline suite exited 0, 87 passed, 1 live-data test deselected, 25 existing scikit-learn deprecation warnings in 10.24s. The runner's deterministic training repeat matched. Read-only record comparison confirmed training completeness, selection recomputation, config/training/selection/artifact/holdout hash links, artifact version match and trusted-local load. Synthetic tests covered artifact checksum/version refusal and an existing holdout claim. A real second CLI invocation exited 1 before data loading with “experiment directory exists; refusing rerun.” No second held-out prediction occurred.

The required global git diff --check reports trailing whitespace on line 20 of user-owned docs/CURRENT_TASK.md. The scoped check excluding that file exits 0; the file is intentionally untouched. Final exact Git status is recorded below after all edits.

## 6. Problems and recovery

An earlier manually interrupted roughly 55-minute training run left no production checkpoint or claim; it was restarted. Histogram boosting's default internal row validation was discovered before selection, so early_stopping=False and a regression test were added. During recovery, an unnecessary interruption followed a mistaken reading of the already complete Brier metric list; no config edit or output resulted. The final training repeat and model fit completed, but the strengthened holdout guard initially refused before any claim because JSON key sorting changed selection option-list order. A canonical candidate-order enumeration fixed this without changing the winner or rule. The complete training record, selection and artifact were verified, then only guarded evaluation resumed once. No holdout retry or selection based on held-out results occurred.

Initial parallel shell launches failed with CreateProcessWithLogonW error 1056;
sequential inspection commands succeeded and no output was affected.

## 7. Limits, evidence, and next step

The historical UCI sample lacks hospital and encounter dates, external validation and clinical timestamp proof. The split is patient-disjoint but not temporal or hospital-disjoint. Unknown-category zero mapping loses detail. The 0.5 cutoff has extremely low recall and no clinical utility validation. Cluster intervals express sampling uncertainty in this cohort, not future or external uncertainty. No XAI, fairness, counterfactual, API, UI or deployment work began.

Inspect the versioned experiment TOML, modelling/evaluation/experiment modules, the two healthcare test files, ADR 0006, the model card, the report, and the ignored nested_cv.json, selection.json, artifact.json, holdout.claim and holdout.json. Unresolved: external review, clinical data-timing and transportability, a justified operational threshold, and the user-owned task-file whitespace check. Suggested next step: external supervisor review of Macro Milestone 2; any later milestone requires a replacement CURRENT_TASK.md.

## Final Git status

```text
 M README.md
 M docs/ARCHITECTURE.md
 M docs/CURRENT_TASK.md
 M docs/EXECUTION_PLAN.md
 M docs/PROJECT_REPORT.md
 M docs/SUPERVISOR_HANDOFF.md
 M src/aletheia/domains/healthcare/__main__.py
?? configs/experiments/healthcare_model_v1.toml
?? docs/decisions/0006-healthcare-model-selection-protocol.md
?? docs/model_cards/healthcare_readmission_v1.md
?? src/aletheia/domains/healthcare/evaluation.py
?? src/aletheia/domains/healthcare/experiment.py
?? src/aletheia/domains/healthcare/modeling.py
?? tests/healthcare/test_experiment.py
?? tests/healthcare/test_modeling.py
```
