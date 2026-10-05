

```markdown
# MILESTONE

Macro Milestone 1 — Healthcare Realignment, Data Foundation, and Deployable Product Architecture

# SUPERVISOR DECISION

The following earlier work is externally supervisor-approved:

- Phase 3 data foundation:
  `f19f86944d24f6220a04b732968aa1377363eb23`
- Phase 3 architecture repair:
  `65f83c668a4f745ffd6dc74a9e21b81cb059712c`
- Phase 4 baseline:
  `1edaedd031c8cdd6a59bf2575bc74f96f74cdc66`
- Phase 4 locked-boundary repair:
  `46abca7e4e4ff9e07e4cc3e0a6026c20620bd6dc`

The previous accelerated credit research-core attempt was interrupted and preserved in:

`stash@{0}: On main: wip: credit research core before healthcare realignment`

Do not apply or pop the stash wholesale.

The stash may be inspected read-only to classify work as:

- generic and reusable;
- credit-benchmark specific;
- healthcare incompatible;
- incomplete and deferred.

Healthcare becomes Aletheia’s primary deployed demonstration. South German Credit remains a supported secondary benchmark.

# REQUIRED STARTING STATE

Before editing, verify:

- branch: `main`
- HEAD: `46abca7e4e4ff9e07e4cc3e0a6026c20620bd6dc`
- local `origin/main`: `46abca7e4e4ff9e07e4cc3e0a6026c20620bd6dc`
- working tree contains only the user-owned modification to `docs/CURRENT_TASK.md`
- the named WIP stash exists

If any additional modified or untracked path exists, stop and report it.

# PRODUCT DEFINITION

Realign Aletheia as:

> An enterprise-style Explainable AI platform that trains, evaluates, tracks,
> deploys and audits high-stakes tabular machine-learning models, demonstrated
> primarily through hospital readmission risk and secondarily through credit
> risk.

The primary healthcare demonstration should investigate 30-day hospital readmission risk using a defensible public dataset.

The product must eventually demonstrate:

- reproducible ML;
- model comparison;
- calibration;
- global and local XAI;
- constrained counterfactuals;
- explanation stability;
- conditional fairness analysis;
- similar-case retrieval;
- experiment tracking and model registry;
- FastAPI;
- React and TypeScript;
- PostgreSQL audit persistence;
- Docker;
- CI/CD;
- deployment;
- monitoring;
- security;
- complete interview and viva documentation.

This milestone implements the healthcare data foundation and designs the complete deployable system. It does not train healthcare models or build the application.

# INTERNAL GATES

Complete the milestone continuously in this order.

## Gate A — Repository and Stash Analysis

Inspect:

- `AGENTS.md`;
- `prompt.txt`;
- all documentation;
- all ADRs;
- all committed configuration;
- all committed source and tests;
- recent Git history;
- the WIP stash using read-only Git inspection.

Do not apply the stash.

Produce a reuse assessment covering every stashed path:

- reusable generic logic;
- credit-specific logic;
- future healthcare adaptation;
- work that should be discarded later;
- work that requires independent verification.

Preserve this assessment in project documentation.

## Gate B — Product Realignment

Freeze:

- product vision;
- primary users;
- user journeys;
- healthcare use case;
- secondary credit benchmark;
- final capability boundaries;
- deployment goal;
- non-clinical disclaimer;
- revised five-milestone roadmap.

## Gate C — Healthcare Dataset Audit

Investigate the official UCI Diabetes 130-US Hospitals for Years 1999–2008 dataset as the primary candidate.

Authoritative identity:

- UCI dataset ID: 296
- DOI: `10.24432/C5230J`
- licence: CC BY 4.0
- intended problem: early readmission within 30 days
- observation unit: inpatient encounter involving a patient diagnosed with diabetes

Use official UCI records and the associated paper.

Audit before implementation:

- source and licence;
- archive and file identities;
- row and column counts;
- file structure;
- data dictionary;
- missing-value encodings;
- duplicated encounters;
- repeated patients;
- target values and counts;
- observation unit;
- prediction timestamp;
- target availability;
- patient identifiers;
- class imbalance;
- feature cardinality;
- rare categories;
- sensitive attributes;
- post-outcome variables;
- administrative codes;
- temporal limitations;
- subgroup support;
- memory and runtime feasibility on an 8 GB Windows laptop;
- fairness feasibility;
- counterfactual feasibility;
- similar-case retrieval feasibility;
- deployment limitations;
- historical and clinical-validity limitations.

If this dataset cannot support a defensible educational readmission-risk audit, stop after a documented candidate comparison. Do not force its selection.

## Gate D — Freeze Healthcare Contracts

If the dataset passes the audit, freeze:

- dataset identity;
- target definition;
- positive class;
- prediction timestamp;
- cohort rules;
- exclusion rules;
- stable encounter row key;
- patient grouping key;
- feature-role policy;
- semantic types;
- missing-value policy;
- split policy;
- sensitive/audit-only policy;
- data version;
- configuration version.

The likely analytical target is:

`readmitted within 30 days = 1`

Do not finalize this mapping without verifying the original target semantics.

Do not treat `>30` readmission as equivalent to `<30` without documenting the binary mapping.

## Gate E — Patient-Level Split

Repeated encounters from one patient must not appear across training and held-out partitions.

Implement a deterministic group-aware split using `patient_nbr` or the verified patient identifier.

Require:

- approximately 80% training and 20% locked held-out data;
- no patient overlap;
- no encounter overlap;
- class support in both partitions;
- deterministic membership;
- stable membership checksum;
- dataset/config/target cross-references;
- explicit partition and class counts.

Do not optimize the split after inspecting model performance.

Future training CV must also be group-aware.

If exact stratification and group isolation conflict, document the algorithm and accepted class-balance tolerance.

## Gate F — Healthcare Data Foundation

Implement:

- verified acquisition;
- archive/file hash checking;
- controlled extraction;
- strict loading;
- schema validation;
- missing-token normalization according to the frozen contract;
- target mapping;
- encounter row-key construction;
- patient-group validation;
- feature-role views;
- group-aware locked split;
- configuration loading;
- clear project-specific errors;
- deterministic CLI commands.

Raw healthcare data must remain ignored.

Do not commit:

- downloaded archives;
- CSV files;
- extracted raw files;
- processed tables;
- temporary audit outputs.

Avoid adding a dataset-client dependency when secure standard-library acquisition is sufficient.

## Gate G — Deployable Architecture

Design the final system around:

- Python and scikit-learn ML core;
- MLflow experiment tracking and model registry;
- DagsHub-hosted MLflow or a documented self-hosted alternative;
- DVC or a justified data-versioning alternative;
- FastAPI backend;
- PostgreSQL;
- React and TypeScript frontend;
- Docker and Docker Compose;
- GitHub Actions CI/CD;
- managed public deployment;
- monitoring and drift checks;
- Hugging Face model/dataset cards;
- optional Hugging Face demonstration;
- optional OpenRouter explanation narrator;
- secrets and environment management;
- authentication and RBAC;
- immutable audit logging.

For each tool record:

- what it does;
- why Aletheia needs it;
- where it sits;
- what calls it;
- inputs and outputs;
- configuration;
- dependencies;
- security considerations;
- failure modes;
- alternatives;
- trade-offs;
- implementation milestone;
- whether it is implemented, selected, provisional or rejected.

Do not install future application/MLOps dependencies during this milestone.

Explicitly reject RunwayML unless a genuine product requirement emerges.

Do not label similar-case retrieval as collaborative filtering.

Plan collaborative filtering as a separate recommendation-system project if it remains a CV goal.

## Gate H — Verification and Documentation

Run all tests and checks required by this milestone.

Reconcile:

- README;
- architecture;
- product requirements;
- execution plan;
- dataset audit;
- ADRs;
- project report;
- supervisor handoff.

Stop for external review.

# FEATURE-ROLE REQUIREMENTS

Create a default-deny healthcare feature policy.

Every raw field must receive exactly one role:

- prediction;
- audit-only;
- excluded;
- raw target;
- derived target;
- identifier/metadata.

Investigate carefully:

- `encounter_id`;
- `patient_nbr`;
- race;
- gender;
- age;
- weight;
- admission type;
- discharge disposition;
- admission source;
- diagnoses;
- medication fields;
- prior inpatient/outpatient/emergency counts;
- laboratory results;
- hospital-stay information;
- readmission target.

Do not automatically use all available columns.

Identifiers must never enter the model.

Sensitive attributes require an explicit prediction-versus-audit decision.

Fields unavailable at the declared prediction timestamp must be excluded.

Fields encoding death, hospice, discharge outcome or target-adjacent information require specific leakage analysis.

# MULTI-DOMAIN ARCHITECTURE

Preserve the working South German Credit benchmark.

Do not rewrite working credit modules merely to rename them.

Introduce a clear domain boundary supporting:

- shared generic contracts and utilities;
- credit-domain configuration;
- healthcare-domain configuration;
- reusable experiment, XAI and serving interfaces;
- domain-specific target, feature and constraint policies.

Avoid premature generic abstractions. Extract shared logic only where both domains genuinely need it.

# TESTING REQUIREMENTS

Add meaningful offline tests for:

- official identity configuration;
- checksum mismatch refusal;
- controlled archive extraction;
- exact raw schema;
- column order where applicable;
- required fields;
- missing-token handling;
- target truth table;
- encounter-key uniqueness;
- repeated-patient detection;
- exhaustive/disjoint feature roles;
- identifiers excluded from model input;
- sensitive-field policy;
- leakage-field exclusion;
- deterministic group split;
- no patient overlap;
- no encounter overlap;
- full membership coverage;
- class support;
- checksum stability;
- split-contract mismatch refusal;
- configuration validation;
- synthetic end-to-end healthcare data-foundation flow;
- preservation of existing credit tests.

Ordinary tests must:

- be synthetic;
- be offline;
- avoid network access;
- avoid requiring the ignored raw dataset.

A separately marked live-data test may verify official acquisition only when explicitly enabled.

# README REQUIREMENTS

Rewrite `README.md` as the accurate public entry point for recruiters, engineers and reviewers.

It must contain:

1. project name and concise flagship description;
2. healthcare-first vision;
3. secondary credit benchmark;
4. problem statement;
5. intended users;
6. implemented capabilities;
7. planned capabilities clearly labelled;
8. architecture diagram;
9. end-to-end data flow;
10. complete technology and tooling table;
11. repository structure;
12. healthcare dataset summary;
13. target and observation unit;
14. leakage and patient-level split strategy;
15. ML lifecycle;
16. XAI roadmap;
17. MLOps architecture;
18. backend/frontend/database plan;
19. CI/CD plan;
20. deployment plan;
21. monitoring plan;
22. security and privacy boundaries;
23. installation;
24. configuration;
25. acquisition commands;
26. test commands;
27. current milestone status;
28. limitations and disclaimer;
29. licence and dataset attribution;
30. documentation links.

For every tool, framework or service mentioned, explain:

- what it is;
- why it was selected;
- exactly where Aletheia uses or will use it;
- how it connects to other components;
- relevant configuration or environment variables;
- data or artifacts passing through it;
- alternatives considered;
- meaningful limitations;
- implementation status.

Do not list technologies that are neither implemented nor approved.

Clearly distinguish:

- implemented;
- selected for a future milestone;
- provisional/under evaluation;
- rejected.

Do not claim that planned APIs, UI, MLflow, DagsHub, deployment or monitoring already exist.

# PROJECT REPORT REQUIREMENTS

Update `docs/PROJECT_REPORT.md` as the complete interview, viva and project-defence guide.

Document:

- why the project drifted toward credit;
- why healthcare became primary;
- why existing work was preserved;
- dataset-selection reasoning;
- observation unit;
- target semantics;
- prediction timestamp;
- group leakage;
- patient-level splitting;
- missing data;
- feature roles;
- sensitive attributes;
- alternatives and trade-offs;
- architecture;
- selected tools and their roles;
- deployment strategy;
- tests;
- important files and functions;
- limitations;
- interview questions and answers;
- implementation order.

Record every meaningful problem:

- symptom;
- root cause;
- investigation;
- failed attempts;
- correction;
- verification;
- lesson;
- interview explanation.

Do not fabricate implementation, bugs, metrics or results.

# CODE-GRAPH REQUIREMENT

Preserve the user’s requirement for enterprise-style codebase analysis.

Plan a later CI/developer-quality feature that:

- parses Python and TypeScript imports;
- produces a dependency graph;
- detects cycles;
- detects forbidden architectural dependency directions;
- publishes a CI artifact;
- links architectural components to code.

Do not implement it during this milestone unless required to verify the new domain architecture.

# REQUIRED DOCUMENTS

Update:

- `README.md`
- `AGENTS.md` only if governance needs clarification
- `docs/ARCHITECTURE.md`
- `docs/CURRENT_TASK.md` is user-owned and must not be modified by Codex
- `docs/DATASET_AUDIT.md` only to preserve/reference the credit audit
- `docs/EXECUTION_PLAN.md`
- `docs/PROJECT_REPORT.md`
- `docs/SUPERVISOR_HANDOFF.md`

Create:

- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/HEALTHCARE_DATASET_AUDIT.md`
- `docs/DEPLOYMENT_ARCHITECTURE.md`
- `docs/decisions/0003-healthcare-primary-multi-domain-platform.md`
- `docs/decisions/0004-healthcare-target-and-patient-split.md`
- `docs/decisions/0005-flagship-tooling-and-deployment-strategy.md`

ADR numbering must be reconciled with committed ADRs. Stashed uncommitted ADR numbers do not reserve permanent identifiers.

# AUTHORIZED CONFIGURATION

Codex may create clearly named versioned healthcare files under:

- `configs/datasets/`
- `configs/features/`
- `configs/splits/`

Do not overwrite the working credit configurations.

# AUTHORIZED SOURCE

Codex may modify shared files only when required:

- `src/aletheia/config.py`
- `src/aletheia/contracts.py`

Codex may create:

- `src/aletheia/domains/__init__.py`
- modules under `src/aletheia/domains/healthcare/`

Shared generic utilities may be created only when justified by both domains.

Do not restore the stashed comparator/XAI/counterfactual/stability files during this milestone.

# AUTHORIZED TESTS

Codex may modify:

- `tests/conftest.py` only when required without breaking existing tests.

Codex may create:

- healthcare tests under `tests/healthcare/`;
- one healthcare data-foundation integration test under `tests/integration/`.

Do not delete or weaken existing credit tests.

# DEPENDENCIES

No new runtime or development dependency is authorized unless the healthcare data foundation cannot be implemented safely with the existing environment.

If a new dependency is genuinely required:

1. document why;
2. compare alternatives;
3. verify licence and Python 3.12 compatibility;
4. update `pyproject.toml`;
5. update `requirements.lock.txt`;
6. verify a clean installation;
7. record exact results.

Do not add MLflow, DagsHub, DVC, FastAPI, React, PostgreSQL clients, OpenRouter or deployment dependencies yet.

# REQUIRED VERIFICATION

Run:

```text
python -m pip check
python -m ruff check .
python -m ruff format --check .
python -m pytest -m "not live_data"
git diff --check
```

If a live acquisition test is added, verify its default skipped state.

Run the live test only after explicit network authorization.

Verify:

- existing credit tests remain passing;
- healthcare synthetic tests pass;
- no patient crosses partitions;
- no identifier enters model input;
- no raw or processed healthcare data appears in Git status;
- no stashed WIP file was restored;
- no model was trained;
- no held-out outcome was inspected for modelling;
- documentation distinguishes implemented and planned components;
- README contains no false implementation claim.

# EXPECTED FINAL GIT STATUS

The final status may contain only:

```text
 M README.md
 M docs/ARCHITECTURE.md
 M docs/CURRENT_TASK.md
 M docs/EXECUTION_PLAN.md
 M docs/PROJECT_REPORT.md
 M docs/SUPERVISOR_HANDOFF.md
 M src/aletheia/config.py
 M src/aletheia/contracts.py
 M tests/conftest.py
?? configs/datasets/
?? configs/features/
?? configs/splits/
?? docs/PRODUCT_REQUIREMENTS.md
?? docs/HEALTHCARE_DATASET_AUDIT.md
?? docs/DEPLOYMENT_ARCHITECTURE.md
?? docs/decisions/0003-healthcare-primary-multi-domain-platform.md
?? docs/decisions/0004-healthcare-target-and-patient-split.md
?? docs/decisions/0005-flagship-tooling-and-deployment-strategy.md
?? src/aletheia/domains/
?? tests/healthcare/
?? tests/integration/test_healthcare_data_foundation.py
```

A subset is acceptable where an authorized file was unnecessary.

`AGENTS.md`, `docs/DATASET_AUDIT.md`, dependency files and additional shared utilities may appear only with a specific documented justification.

No raw data, archive, CSV, environment, cache, generated artifact, fitted model, notebook, API, frontend, database, Docker or deployment file may appear.

# FINAL RESPONSE

Report:

1. milestone status;
2. product realignment outcome;
3. stash inventory and reuse conclusions;
4. selected healthcare dataset or investigation outcome;
5. authoritative source and licence;
6. target;
7. observation unit;
8. prediction timestamp;
9. cohort and exclusions;
10. feature roles;
11. leakage findings;
12. missing-data findings;
13. sensitive-attribute decisions;
14. patient-level split;
15. exact partition and class counts;
16. fairness feasibility;
17. counterfactual feasibility;
18. similar-case feasibility;
19. multi-domain architecture;
20. final tooling decisions;
21. complete README changes;
22. healthcare data-foundation implementation;
23. tests and exact results;
24. existing credit regression-test results;
25. files created;
26. files modified;
27. files intentionally unchanged;
28. problems encountered;
29. failed attempts and recovery;
30. limitations;
31. unresolved questions;
32. what the user should understand;
33. confirmation that no model was trained;
34. confirmation that no raw data was committed;
35. confirmation that no stashed WIP file was restored;
36. confirmation that later milestones did not begin;
37. confirmation that Codex did not commit or push;
38. exact final `git status --short --untracked-files=all`;
39. recommended commit message.

Recommend:

`feat: establish Aletheia healthcare foundation`

# STOP RULE

Stop after completing and verifying Macro Milestone 1.

Do not:

- apply or pop the WIP stash;
- train healthcare models;
- implement comparator evaluation;
- implement XAI;
- implement counterfactuals;
- implement stability or fairness metrics;
- add MLflow or DagsHub;
- build FastAPI;
- build React;
- create a database;
- create Docker or CI/CD files;
- deploy;
- modify `docs/CURRENT_TASK.md`;
- commit or push.

The user will inspect the result, commit and push it, and return it for independent external supervisor review.
```