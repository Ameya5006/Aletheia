# CURRENT TASK — Macro Milestone 3: Explainability and Responsible-AI Audit

## Status

AUTHORIZED FOR IMPLEMENTATION.

This task begins only after the committed and pushed Macro Milestone 2 calibrated healthcare model.

Starting repository requirements:

- branch must be `main`;
- local `HEAD` must equal `origin/main`;
- the committed starting point should be the Macro Milestone 2 commit beginning with `49a1a8c`;
- the working tree may contain only the user-owned modification to `docs/CURRENT_TASK.md`;
- the existing stash must remain untouched.

If the starting state differs, stop before editing and report the discrepancy.

## Objective

Implement Aletheia’s first complete, reproducible and technically defensible Explainable AI and Responsible-AI audit layer for the frozen healthcare readmission model.

This milestone must establish:

1. global model explanations;
2. local prediction explanations;
3. explanation stability analysis;
4. subgroup fairness evaluation;
5. a bounded counterfactual/scenario-analysis prototype;
6. immutable, reproducible audit evidence;
7. documentation sufficient for interviews, viva preparation and technical defence.

Do not begin the application backend, frontend, LLM/RAG layer, database, deployment or MLOps milestones.

## Mandatory preparation

Before editing:

1. Read `AGENTS.md` completely.
2. Read this file completely.
3. Read:
   - `README.md`;
   - `docs/ARCHITECTURE.md`;
   - `docs/EXECUTION_PLAN.md`;
   - `docs/PROJECT_REPORT.md`;
   - `docs/SUPERVISOR_HANDOFF.md`;
   - `docs/HEALTHCARE_DATASET_AUDIT.md`;
   - `docs/model_cards/healthcare_readmission_v1.md`;
   - healthcare-related ADRs;
   - healthcare dataset, feature, split and experiment configurations.
4. Inspect the healthcare foundation, modelling, evaluation and experiment implementations.
5. Inspect the complete healthcare test suite.
6. Inspect the preserved Macro Milestone 2 run, manifest, model-selection record and holdout-evaluation record.
7. Verify hashes, configuration bindings, model identity and split identity before using any artifact.
8. Inspect official documentation for any new dependency before adding it.

Repository evidence takes priority over documentation claims.

## Methodology gate

Before calculating audit results, create and test versioned audit protocols covering:

- explanation method and reference/background data;
- global and local explanation semantics;
- model-output scale being explained;
- sampling strategy and random seeds;
- stability perturbations and comparison metrics;
- protected/audit-only attributes;
- subgroup inclusion and minimum-support rules;
- uncertainty estimation;
- counterfactual mutability and feasibility constraints;
- privacy and artifact-publication rules.

Do not inspect final audit outcomes before the protocol is frozen.

If the selected explanation method cannot validly explain the calibrated healthcare pipeline, stop and document the methodological blocker. Do not silently explain a different estimator while presenting it as the calibrated model.

If the base estimator and calibrated probability layer require different explanations, distinguish clearly between:

- features influencing the underlying model score; and
- the calibration layer converting scores into probabilities.

## Global explanations

Implement reproducible global explanation evidence for the frozen selected model.

At minimum:

- calculate a defensible global feature-importance or attribution summary;
- retain human-readable source-feature mappings after preprocessing;
- distinguish categorical encodings from original clinical fields;
- document the explained output and attribution baseline;
- include uncertainty or repeated-sample stability where feasible;
- verify that audit-only, excluded, identifier and target fields never enter the prediction feature matrix;
- do not describe association as causation.

Prefer SHAP when it is valid and computationally practical, but do not force SHAP if the calibrated pipeline is unsupported or the resulting interpretation would be misleading. A documented, tested model-agnostic alternative is acceptable.

## Local explanations

Implement local explanations for individual predictions.

Each local explanation must include:

- model and dataset identity;
- prediction probability;
- explanation method and output scale;
- influential features with direction and magnitude where supported;
- original human-readable feature values;
- limitations and non-causal wording;
- explicit indication that the output is educational research evidence and not medical advice.

Tests must verify deterministic behaviour under fixed configuration and correct mapping from transformed features back to source fields.

Do not publish raw patient records or directly identifying values.

## Explanation stability

Implement stability analysis showing whether explanations remain reasonably consistent under controlled, clinically plausible perturbations.

The protocol must define:

- which fields may be perturbed;
- perturbation ranges or categories;
- which fields must remain immutable;
- number of repetitions;
- fixed random seeds;
- comparison metrics such as rank correlation, top-k overlap or attribution-distance measures;
- interpretation thresholds without pretending they are universal clinical standards.

Report instability honestly. Do not tune the model after observing stability results.

## Fairness audit

Use race, gender and age only as audit attributes unless an already-approved contract states otherwise. They must not silently become prediction features.

Evaluate the frozen model across defensible subgroups using appropriate metrics, including where support permits:

- sample and positive counts;
- prevalence;
- average precision;
- ROC-AUC;
- Brier score or calibration evidence;
- sensitivity/recall;
- specificity;
- false-positive rate;
- false-negative rate;
- positive prediction rate.

Requirements:

- handle undefined metrics explicitly;
- enforce minimum-support rules;
- report uncertainty intervals where feasible;
- distinguish observed performance differences from discrimination or causality;
- document missingness and historical-data limitations;
- do not claim legal, clinical or ethical fairness certification.

A guarded post-selection audit of the locked holdout is permitted only if it is pre-registered, performed once, append-only, and cannot influence model selection or hyperparameters. Record the access and prove that the model remains frozen.

## Counterfactual or scenario analysis

Implement only a bounded research prototype if defensible.

Requirements:

- distinguish counterfactual explanation from clinical recommendation;
- classify fields as immutable, conditionally mutable or excluded;
- prohibit changes to identifiers, demographics, outcomes and clinically impossible fields;
- avoid recommending medication or treatment changes;
- enforce valid categorical domains and observed constraints;
- report when no feasible scenario is found;
- label generated scenarios as model-sensitivity evidence, not guaranteed real-world interventions.

If clinically meaningful counterfactuals cannot be justified from repository evidence, implement and document a feasibility assessment instead of fabricating recourse.

## Artifacts and reproducibility

Create versioned configuration and immutable audit evidence.

Artifacts must contain:

- dataset, split, model, protocol and configuration hashes;
- software versions;
- random seeds;
- timestamps;
- method metadata;
- aggregate results;
- explicit holdout-access status;
- limitations.

Do not publish:

- raw healthcare data;
- row-level identifying data;
- unrestricted patient-level predictions;
- secrets;
- caches;
- temporary outputs;
- downloaded archives.

Publication must refuse overwriting an existing immutable audit run.

## Tests

Add meaningful unit and integration tests covering:

- feature-name mapping;
- global explanation reproducibility;
- local explanation structure and determinism;
- forbidden-feature exclusion;
- calibrated-versus-base-estimator semantics;
- stability calculations;
- fairness subgroup calculations;
- minimum-support and undefined-metric handling;
- counterfactual constraint enforcement;
- infeasible-scenario handling;
- artifact hashes and manifest bindings;
- overwrite refusal;
- holdout audit guard;
- no raw or patient-identifying data in published evidence.

Tests must verify actual behaviour rather than merely asserting that files exist.

Do not rerun expensive model selection or retrain the model unless repository evidence proves it is technically unavoidable. If unavoidable, stop and explain before doing so.

## Documentation

Update truthfully:

- `README.md`;
- `docs/ARCHITECTURE.md`;
- `docs/EXECUTION_PLAN.md`;
- `docs/PROJECT_REPORT.md`;
- `docs/SUPERVISOR_HANDOFF.md`;
- the healthcare model card;
- relevant ADRs.

Create a new ADR for the explanation and responsible-audit protocol.

`docs/PROJECT_REPORT.md` must become a study and defence guide for this milestone. Explain:

- what each XAI/fairness/stability/counterfactual component does;
- why it exists;
- how data flows through it;
- which model output is explained;
- global versus local explanations;
- attribution baselines;
- feature transformations and source-feature mapping;
- fairness metrics and their limitations;
- explanation-stability methodology;
- counterfactual assumptions and restrictions;
- alternatives considered;
- trade-offs;
- important functions and files;
- tests;
- results;
- interpretation;
- unresolved limitations;
- likely interview and viva questions.

Add a clearly structured problem-and-recovery record for every meaningful issue encountered:

- symptom;
- root cause;
- investigation;
- rejected approaches;
- final resolution;
- verification;
- lesson learned.

Do not fabricate problems, decisions, metrics, results or implementation.

## Authorized paths

Codex may modify existing healthcare ML, experiment, contract, documentation, testing and dependency files only where required by this milestone.

Codex may create:

- versioned audit configuration under `configs/audit/`;
- healthcare XAI, fairness, stability, counterfactual and audit modules;
- corresponding healthcare tests;
- one responsible-AI/XAI ADR;
- immutable generated audit evidence only in the already-approved ignored artifact location.

Do not modify unrelated projects, credit-domain implementation, `prompt.txt`, raw data or the existing stash.

Do not modify this `docs/CURRENT_TASK.md` file.

## Required verification

Run and report:

1. dependency consistency check;
2. Ruff lint;
3. Ruff formatting check;
4. targeted new unit tests;
5. targeted healthcare integration tests;
6. complete offline test suite;
7. artifact and manifest inspection;
8. hash/configuration/model/split binding checks;
9. privacy inspection of published audit evidence;
10. `git diff --check`;
11. `git status --short --untracked-files=all`.

Use repository-safe temporary locations and ensure no cache, raw data, temporary audit output or generated healthcare record appears in Git status.

## Stop conditions

Stop immediately if:

- starting Git state is inconsistent;
- frozen model, split or experiment hashes do not match;
- valid explanation semantics cannot be established;
- completing the task would require model reselection;
- holdout access cannot be guarded;
- counterfactual constraints cannot be defended;
- a required command fails and the task specifically prohibits a fallback;
- an unauthorized file appears in status.

Preserve completed valid work and report the blocker precisely.

## Final response

Report:

1. milestone status;
2. starting commit and repository state;
3. explanation methods implemented;
4. global explanation results;
5. local explanation behaviour;
6. explanation stability results;
7. fairness methods and results;
8. counterfactual/scenario-analysis outcome;
9. model-output semantics;
10. holdout-access record;
11. artifacts and hashes;
12. tests and exact results;
13. files created;
14. files modified;
15. files intentionally unchanged;
16. problems encountered and resolutions;
17. limitations;
18. what the user should understand for interviews;
19. confirmation that no later milestone began;
20. confirmation that Codex did not commit or push;
21. exact final `git status --short --untracked-files=all`;
22. recommended commit message.

If successful, recommend:

`feat: add healthcare XAI and responsible audit`

Do not claim external supervisor approval.

## Final stop rule

Stop after Macro Milestone 3.

Do not begin:

- FastAPI product APIs;
- PostgreSQL application persistence;
- authentication;
- React frontend;
- LLM or RAG integration;
- MLflow;
- Docker deployment;
- CI/CD;
- monitoring;
- Kubernetes;
- cloud infrastructure;
- or additional model training.

Do not commit or push.