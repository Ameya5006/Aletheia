# MILESTONE

Phase 3 — Reproducible Data Foundation

# SUPERVISOR DECISION

Phase 2 — System Architecture, Technology Selection, and Implementation Roadmap is externally supervisor-approved at commit:

`52be4130c8c4745c9f86f3b26a93497c3beeb2ff`

The approved architectural direction is a research-first Python modular monolith.

This approval covers the proposed architecture and roadmap only. It does not approve any model, preprocessing result, metric, explanation, fairness result, API, UI, database, deployment, or production claim.

# GOAL

Implement and verify the smallest reproducible data foundation needed to:

1. configure the approved dataset;
2. reacquire it from the authoritative UCI source;
3. verify archive and raw-file identity;
4. load its raw schema without changing meanings;
5. validate its schema and categorical domains;
6. preserve and explicitly map the target;
7. enforce disjoint feature roles;
8. create stable row keys;
9. create and lock one deterministic stratified train/test membership;
10. expose a small data-only command interface;
11. test all important failure boundaries;
12. document the implementation as engineering, learning, interview and viva evidence.

Do not implement preprocessing, model training or any later milestone.

# REQUIRED STARTING STATE

Before editing, verify:

1. the current branch is `main`;
2. `HEAD` is `52be4130c8c4745c9f86f3b26a93497c3beeb2ff`;
3. the branch is synchronized with `origin/main`;
4. Phase 2 documentation and ADR exist;
5. Phase 1 dataset evidence remains present;
6. no implementation already exists;
7. `git status --short --untracked-files=all` contains only:

```text
 M docs/CURRENT_TASK.md
```

`docs/CURRENT_TASK.md` is modified because the user replaced the Phase 2 task with this externally approved Phase 3 task.

Do not modify `docs/CURRENT_TASK.md` again.

If the starting status contains any additional modified, staged or untracked path, stop and explain it before making changes.

# FILES TO READ COMPLETELY

Read:

* `AGENTS.md`
* `prompt.txt`
* `docs/CURRENT_TASK.md`
* `docs/SUPERVISOR_HANDOFF.md`
* `docs/PROJECT_REPORT.md`
* `docs/ARCHITECTURE.md`
* `docs/EXECUTION_PLAN.md`
* `docs/DATASET_AUDIT.md`
* `docs/decisions/0001-research-first-modular-monolith.md`

Also inspect:

* Git status;
* recent Git history;
* the Phase 2 commit and diff;
* the complete repository tree;
* all repository instructions.

Treat repository evidence as authoritative.

# BEFORE EDITING

Provide a concise working update containing:

1. verified starting commit and Git status;
2. Phase 2 approval being recorded;
3. proposed Phase 3 modules;
4. dependency and environment approach;
5. acquisition and checksum strategy;
6. schema and target controls;
7. feature-role policy;
8. row-key and split strategy;
9. test strategy;
10. expected changed and new files;
11. principal risks and stop conditions.

Do not begin editing until the repository state is verified.

# FIXED DATASET IDENTITY

Use only:

* Dataset: South German Credit
* UCI dataset record: `https://archive.ics.uci.edu/dataset/573/south+german+credit`
* DOI: `https://doi.org/10.24432/C5QG88`
* Official archive: `https://archive.ics.uci.edu/static/public/573/south+german+credit+update.zip`
* Expected archive size: `13,130` bytes
* Expected archive SHA-256: `0b40d40eb7321693d559e247a556f88a6cc8df8489c3cb2ae084db7592584551`
* Required raw archive member: `SouthGermanCredit.asc`
* Expected raw size: `47,940` bytes
* Expected raw SHA-256: `5f363343f356ca38a0236baab849e472846399b2176ccc5bd686483dd8a7562f`
* Expected shape: 1,000 rows × 21 raw columns
* Licence: CC BY 4.0

Do not silently accept an updated archive, alternative mirror, renamed dataset, different checksum, or different raw member.

A mismatch must stop processing.

Do not commit the archive or extracted raw dataset.

# FIXED RAW COLUMN ORDER

The raw header must be exactly:

1. `laufkont`
2. `laufzeit`
3. `moral`
4. `verw`
5. `hoehe`
6. `sparkont`
7. `beszeit`
8. `rate`
9. `famges`
10. `buerge`
11. `wohnzeit`
12. `verm`
13. `alter`
14. `weitkred`
15. `wohn`
16. `bishkred`
17. `beruf`
18. `pers`
19. `telef`
20. `gastarb`
21. `kredit`

All raw values must parse as integers. Do not silently coerce malformed, missing, floating-point or unknown values.

Preserve the source column names in the raw layer. Human-readable names may exist in configuration or documentation, but must not replace raw names silently.

# TARGET CONTRACT

Preserve raw `kredit`.

The authoritative mapping is:

* raw `kredit = 0`: bad/non-compliant credit;
* raw `kredit = 1`: good/compliant credit.

Derive the analytical positive/adverse target explicitly:

```text
adverse_event = 1 when kredit == 0
adverse_event = 0 when kredit == 1
```

Do not overwrite `kredit`.

Do not encode `1` as the adverse event merely because it is the raw numeric value.

Tests must verify:

* the complete mapping truth table;
* exactly 300 adverse and 700 non-adverse rows;
* target exclusion from prediction features;
* refusal of any raw target outside `{0, 1}`.

Keep the known documentation discrepancy about target coding visible in the project documentation.

# FEATURE-ROLE CONTRACT

Implement one versioned, machine-readable feature policy.

## Prediction features

Exactly:

* `laufkont`
* `laufzeit`
* `moral`
* `verw`
* `hoehe`
* `sparkont`
* `beszeit`
* `rate`
* `buerge`
* `wohnzeit`
* `verm`
* `weitkred`
* `wohn`
* `beruf`
* `pers`

## Audit-only features

Exactly:

* `famges`
* `alter`
* `gastarb`

They must remain aligned by row key but must never enter the prediction matrix.

## Excluded features

Exactly:

* `telef`
* `bishkred`

Resolve `bishkred` conservatively by excluding it because authoritative evidence does not establish a safe observation cutoff for a value defined as including the current credit.

Record that this is a default-deny leakage decision, not proof that `bishkred` is target leakage.

`telef` remains excluded because it is an obsolete socioeconomic proxy with weak modern meaning.

## Target

* `kredit`
* derived `adverse_event`

## Metadata

* stable `row_key`

The role sets must be disjoint and exhaustive.

Unknown fields and fields without an approved role must fail closed.

# SEMANTIC-TYPE CONTRACT

Machine-readable configuration must distinguish:

* quantitative fields;
* ordinal or discretized fields;
* nominal categorical fields represented by integers;
* audit-only fields;
* excluded fields;
* raw target;
* derived target;
* metadata.

Do not treat every integer-coded feature as a continuous number.

Documented categorical domains must be enforced.

Purpose code `7` is documented but unobserved. It must be accepted by the category contract even though the approved file contains no row using it.

Unknown or undocumented category codes must be rejected.

Clearly distinguish:

* observed minimum/maximum values in this fixed dataset;
* semantic category domains;
* any future inference input policy.

Do not incorrectly turn an observed dataset minimum or maximum into a universal real-world rule.

# ROW-KEY POLICY

Implement a transparent deterministic row key bound to the verified source file.

Use one-based source data-row position after the header:

```text
sgc-0001
sgc-0002
...
sgc-1000
```

The key is valid only when the approved raw-file SHA-256 matches.

The row key:

* must not be passed to a model;
* must remain identical across raw, prediction, audit and split views;
* must be unique and non-null;
* must not depend on pandas’ mutable index;
* must not change between repeated loads of the same verified file.

Test the first key, final key, uniqueness, repeatability and alignment.

# SPLIT CONTRACT

Create and lock one deterministic stratified split:

* method: `StratifiedShuffleSplit`;
* test fraction: `0.20`;
* random seed: `42`;
* stratification target: `adverse_event`;
* expected training rows: `800`;
* expected test rows: `200`;
* expected training class counts: 240 adverse, 560 non-adverse;
* expected test class counts: 60 adverse, 140 non-adverse.

Use the split only to create membership. Do not preprocess or train anything.

Store a compact versioned split contract at:

`configs/splits/south_german_credit_v1.json`

It must contain at least:

* contract/schema version;
* approved raw-file SHA-256;
* feature-policy version;
* target mapping identifier;
* splitter name;
* scikit-learn version used to generate it;
* test fraction;
* seed;
* partition counts;
* class counts;
* deterministic test row keys;
* canonical membership checksum.

Training membership is the complement of the locked test keys.

Do not include feature values or target values for individual rows in the committed split contract.

Define and test the exact canonical serialization used for the membership checksum.

A different dataset hash, missing key, duplicate key, overlapping membership, incomplete coverage, class-count mismatch or changed membership checksum must be rejected.

The held-out test membership is now locked. Do not calculate model results or use it for model, preprocessing, metric or threshold decisions.

# PACKAGE AND ENVIRONMENT

Use the approved Python 3.12 direction.

Create a minimal `src`-layout Python package.

Use only dependencies needed in this phase:

Runtime:

* pandas;
* scikit-learn.

Development:

* pytest;
* Ruff.

Use standard-library functionality for:

* HTTP download where practical;
* SHA-256;
* ZIP handling;
* paths;
* JSON;
* TOML reading;
* dataclasses or similarly simple contracts;
* command-line parsing.

Do not add Requests merely for one download unless a demonstrated standard-library failure makes it necessary.

Do not add:

* Matplotlib;
* SHAP;
* DiCE;
* joblib as a direct persistence dependency;
* MLflow;
* DVC;
* notebook packages;
* FastAPI;
* Flask;
* Django;
* Streamlit;
* React/Node tooling;
* database drivers;
* Docker tooling;
* deployment dependencies;
* authentication packages;
* model serialization packages.

Create:

* `pyproject.toml`
* `requirements.lock.txt`

`pyproject.toml` must include:

* package metadata;
* Python requirement compatible with the approved Python 3.12 series;
* minimal runtime dependencies;
* a development extra containing pytest and Ruff;
* pytest configuration where appropriate;
* Ruff configuration where appropriate;
* the selected build backend.

Generate `requirements.lock.txt` from the actually tested clean environment with exact versions.

The lock file must not contain:

* editable local project entries;
* `file://` references;
* absolute local paths;
* unrelated globally installed packages.

Verify that a second clean Python 3.12 environment can install the lock, install Aletheia without resolving additional dependencies, and run the offline tests.

Record the exact Python, pip and package versions actually tested.

# ACQUISITION REQUIREMENTS

Implement controlled acquisition that:

1. downloads to a temporary staging file;
2. handles network failure without presenting partial content as valid;
3. verifies archive byte size and SHA-256 before extraction;
4. opens the ZIP using Python’s ZIP support, including its BZIP2 member;
5. reads or extracts only the exact approved archive member;
6. prevents path traversal or arbitrary member extraction;
7. verifies raw byte size and SHA-256;
8. publishes the verified raw file only after all checks pass;
9. does not overwrite an existing valid raw file unnecessarily;
10. refuses an existing invalid raw file instead of silently replacing it;
11. cleans or clearly isolates failed staging files;
12. produces useful errors without dumping raw records.

The normal local destination may be:

`data/raw/SouthGermanCredit.asc`

The archive and raw-data paths must be ignored by Git.

# LOADING AND VALIDATION

Implement small, understandable functions for:

* configuration loading;
* file hashing;
* verified acquisition;
* raw loading;
* schema validation;
* target mapping;
* feature-role view construction;
* split generation;
* split-contract loading and verification.

Validation must check at least:

* verified raw-file identity;
* exact header and column order;
* exactly 1,000 data rows;
* exactly 21 raw columns;
* integer tokens only;
* no missing values;
* target domain;
* categorical domains;
* expected target counts;
* zero duplicate complete rows;
* zero duplicate predictor-only rows;
* stable row-key creation;
* feature-role disjointness and exhaustiveness.

Do not silently repair schema drift.

Errors must identify the failing rule and safe context such as column, row key or invalid value.

# DATA-ONLY COMMAND INTERFACE

Provide a minimal data-only command interface through:

`python -m aletheia.data`

Support bounded commands equivalent to:

```powershell
python -m aletheia.data acquire --destination data/raw
python -m aletheia.data validate --raw-file data/raw/SouthGermanCredit.asc
python -m aletheia.data split --raw-file data/raw/SouthGermanCredit.asc --contract configs/splits/south_german_credit_v1.json --verify
```

The exact option parsing may remain small.

The command must not:

* train a model;
* preprocess learned features;
* evaluate metrics;
* start an API;
* create a UI;
* write a model artifact;
* perform XAI, fairness, stability or counterfactual work.

# EXPECTED SOURCE FILES

Create exactly:

* `src/aletheia/__init__.py`
* `src/aletheia/config.py`
* `src/aletheia/contracts.py`
* `src/aletheia/data/__init__.py`
* `src/aletheia/data/__main__.py`
* `src/aletheia/data/acquire.py`
* `src/aletheia/data/load.py`
* `src/aletheia/data/validate.py`
* `src/aletheia/data/target.py`
* `src/aletheia/data/roles.py`
* `src/aletheia/data/split.py`

Prefer functions and small immutable value objects.

Do not create empty architectural layers, repositories, services, dependency-injection containers, abstract base classes or interfaces without a real need.

If an additional source file is genuinely necessary, stop before creating it and explain why the approved file boundary is insufficient.

# EXPECTED TEST FILES

Create exactly:

* `tests/conftest.py`
* `tests/unit/test_config.py`
* `tests/unit/test_target.py`
* `tests/unit/test_roles.py`
* `tests/unit/test_split.py`
* `tests/data/test_acquire.py`
* `tests/data/test_load_validate.py`
* `tests/integration/test_data_foundation.py`

Use clearly synthetic values and temporary directories for offline tests.

Do not commit copied rows from the raw dataset as test fixtures.

The ordinary test suite must not require internet access.

Mark the authoritative end-to-end download test as `live_data` and require explicit authorization/environment configuration before it uses the network.

Tests must cover at least:

## Acquisition

* valid archive and raw hashes;
* archive checksum mismatch;
* raw checksum mismatch;
* missing approved member;
* unexpected or unsafe archive member handling;
* failed or partial download cleanup;
* existing invalid destination refusal.

## Loader and schema

* valid synthetic contract fixture;
* wrong header;
* wrong column order;
* malformed row;
* non-integer token;
* missing value;
* incorrect row count;
* undocumented category;
* documented but unobserved purpose code `7`;
* invalid target;
* duplicate detection.

## Target and roles

* complete target truth table;
* actual 300/700 target arithmetic in the live-data test;
* prediction/audit/excluded/target/metadata disjointness;
* exhaustive raw-feature coverage;
* audit-only fields absent from model input;
* `telef` and `bishkred` absent from model input;
* target and row key absent from model input;
* unknown fields fail closed.

## Row identity and split

* exact first and last row keys;
* unique keys;
* repeatable keys;
* aligned prediction and audit views;
* same-seed membership equality;
* locked membership checksum;
* exact 800/200 partition sizes;
* exact class counts;
* no overlap;
* complete coverage;
* changed dataset-hash refusal;
* missing/duplicate/unknown test-key refusal;
* different generated membership detected rather than silently accepted.

## Integration

One explicitly enabled live-data test must perform:

official acquisition → archive verification → raw verification → load → schema validation → target mapping → role enforcement → row-key alignment → locked split verification.

# GITIGNORE

Update `.gitignore` to exclude at least:

* `.venv/`
* Python bytecode and `__pycache__/`
* `.pytest_cache/`
* `.ruff_cache/`
* build/distribution metadata;
* `*.egg-info/`
* downloaded archives;
* `data/raw/`
* `data/processed/`
* generated artifacts and reports;
* local environment/configuration files that may contain secrets.

Do not ignore committed configuration, source code, tests or documentation.

After acquisition and testing, verify that no raw data, archive, environment, cache, build output or generated report appears in Git status.

# DOCUMENTATION UPDATES

## Architecture and ADR

Update only their approval/implementation status where necessary:

* mark Phase 2 architecture externally supervisor-approved;
* change ADR 0001 from proposed to accepted/approved;
* record Phase 3 implementation truthfully;
* do not redesign the approved architecture unless implementation evidence exposes a genuine problem.

If a genuine architectural contradiction appears, stop and report it instead of silently changing the architecture.

## DATASET_AUDIT.md

Preserve all Phase 1 evidence.

Add or update only what is now established by implementation:

* `bishkred` was conservatively excluded;
* the fixed split policy is 80/20 stratified with seed 42;
* stable row-key policy;
* implementation/config/test references;
* limitations of this split.

Do not rewrite computed Phase 1 evidence or imply that a model exists.

## EXECUTION_PLAN.md

Record:

* Phase 2 externally supervisor-approved;
* Phase 3 completed by Codex and pending external supervisor review only if all acceptance checks pass;
* later phases remain blocked.

Do not authorize Phase 4.

## PROJECT_REPORT.md

Update it incrementally as Aletheia’s evidence-backed engineering, learning, interview, viva and project-defence guide.

For Phase 3, explain concisely but technically:

* what the data foundation does;
* why it was implemented before preprocessing and modelling;
* authoritative acquisition and checksum flow;
* configuration files and their roles;
* important modules/functions and where to inspect them;
* callers and dependencies;
* raw schema validation;
* target mapping and why label orientation matters;
* prediction versus audit-only versus excluded fields;
* why `bishkred` was excluded;
* stable row identity;
* deterministic stratified splitting;
* why stratification is appropriate here;
* why the split cannot establish temporal or entity generalisation;
* how the locked test membership prevents accidental split drift;
* failure modes and their error handling;
* tests that verify each boundary;
* dependency and clean-environment decisions;
* any real problems encountered and how they were fixed;
* important concepts learned;
* concise interview/viva explanations and likely follow-up questions;
* limitations.

Do not turn the report into a raw command log or repeat entire source files.

Do not invent bugs, metrics, experiments or lessons that did not occur.

## SUPERVISOR_HANDOFF.md

Replace the previous Phase 2 handoff with an evidence-based Phase 3 handoff containing:

1. milestone and status;
2. base and resulting commit state;
3. Phase 2 approval recorded;
4. implementation summary;
5. dataset identity;
6. exact environment and dependencies;
7. configuration decisions;
8. acquisition and checksum results;
9. schema and target results;
10. feature-role result;
11. `bishkred` decision;
12. row-key design;
13. split design and exact counts;
14. source files created;
15. tests created;
16. documentation modified;
17. commands actually run;
18. exact test/lint/format results;
19. live-data verification result;
20. clean-environment recreation result;
21. meaningful problems encountered;
22. unresolved issues;
23. limitations;
24. confirmation that preprocessing and modelling did not begin;
25. confirmation that XAI, fairness, counterfactual, API, UI and deployment work did not begin;
26. confirmation that Codex did not commit or push;
27. actual final `git status --short --untracked-files=all`;
28. recommended commit message;
29. recommended Phase 4 direction as advisory only.

Do not claim external supervisor approval for Phase 3.

# REQUIRED VERIFICATION

Run and record the exact results of:

```powershell
git diff --check
git status --short --untracked-files=all
git diff --stat
```

Using the clean project environment, run:

```powershell
python --version
python -m pip --version
python -m pip check
python -m ruff check .
python -m ruff format --check .
python -m pytest -m "not live_data"
```

Run the data commands against the authoritative dataset:

```powershell
python -m aletheia.data acquire --destination data/raw
python -m aletheia.data validate --raw-file data/raw/SouthGermanCredit.asc
python -m aletheia.data split --raw-file data/raw/SouthGermanCredit.asc --contract configs/splits/south_german_credit_v1.json --verify
```

Run the explicitly authorized live-data integration test using the environment switch chosen by the implementation.

Then verify in a second clean Python 3.12 environment that:

1. `requirements.lock.txt` installs successfully;
2. the project installs without resolving unrecorded dependencies;
3. `pip check` passes;
4. Ruff passes;
5. offline tests pass.

Do not report a command as passed unless it actually ran successfully.

A skipped live-data test does not satisfy the live acquisition acceptance criterion.

# ACCEPTANCE CRITERIA

Phase 3 passes only if:

1. authoritative acquisition succeeds;
2. both approved SHA-256 values match;
3. partial or mismatched downloads fail closed;
4. the exact raw schema is enforced;
5. categorical domains are explicit;
6. integer category codes remain categorical/ordinal according to policy;
7. raw `kredit` is preserved;
8. `adverse_event` orientation is correct;
9. target counts are exactly 300/700;
10. feature roles are disjoint and exhaustive;
11. audit-only, excluded, target and metadata fields cannot enter prediction features;
12. `bishkred` is excluded;
13. row keys are stable, unique and aligned;
14. split membership is deterministic and locked;
15. split counts and class counts are exact;
16. train and test membership are complete and non-overlapping;
17. the committed split contract contains no raw feature or per-row target values;
18. ordinary tests work without internet;
19. the live-data integration test passes;
20. a second clean environment reproduces the tested setup;
21. Ruff, formatting, pytest and `pip check` pass;
22. no raw data, downloaded archive, environment, cache or generated output is tracked;
23. documentation matches the actual implementation;
24. no preprocessing, model, XAI, fairness, counterfactual, API, UI, database or deployment work exists;
25. Codex does not commit or push.

If any acceptance criterion fails, report Phase 3 as incomplete and do not recommend a commit as successful work.

# OUT OF SCOPE

Do not implement:

* missing-value imputation;
* encoding;
* scaling;
* feature engineering;
* feature selection;
* class weighting or resampling;
* model definitions;
* Logistic Regression;
* Decision Trees;
* ensemble models;
* cross-validation;
* model metrics;
* threshold selection;
* model serialization;
* experiment-run storage;
* SHAP;
* permutation importance;
* local explanations;
* counterfactual generation;
* stability analysis;
* fairness metrics;
* notebooks;
* API;
* frontend or Stitch-generated UI;
* database;
* MLflow or DVC;
* Docker;
* deployment;
* authentication;
* monitoring.

Do not inspect held-out performance.

# EXPECTED GIT STATUS BEFORE USER COMMIT

Use:

```powershell
git status --short --untracked-files=all
```

Expected modified files:

```text
 M .gitignore
 M docs/ARCHITECTURE.md
 M docs/CURRENT_TASK.md
 M docs/DATASET_AUDIT.md
 M docs/EXECUTION_PLAN.md
 M docs/PROJECT_REPORT.md
 M docs/SUPERVISOR_HANDOFF.md
 M docs/decisions/0001-research-first-modular-monolith.md
```

Expected new files:

```text
?? configs/dataset.toml
?? configs/features.toml
?? configs/splits/south_german_credit_v1.json
?? pyproject.toml
?? requirements.lock.txt
?? src/aletheia/__init__.py
?? src/aletheia/config.py
?? src/aletheia/contracts.py
?? src/aletheia/data/__init__.py
?? src/aletheia/data/__main__.py
?? src/aletheia/data/acquire.py
?? src/aletheia/data/load.py
?? src/aletheia/data/roles.py
?? src/aletheia/data/split.py
?? src/aletheia/data/target.py
?? src/aletheia/data/validate.py
?? tests/conftest.py
?? tests/data/test_acquire.py
?? tests/data/test_load_validate.py
?? tests/integration/test_data_foundation.py
?? tests/unit/test_config.py
?? tests/unit/test_roles.py
?? tests/unit/test_split.py
?? tests/unit/test_target.py
```

Expected intentionally unchanged tracked files include:

* `AGENTS.md`
* `prompt.txt`
* `CLAUDE.md`
* `README.md`

No raw dataset, ZIP archive, virtual environment, cache, build output, generated artifact, notebook, model, API, frontend, database, container or deployment file may appear.

If Git status contains any additional path, stop and explain it before recommending a commit.

Line-ending warnings saying LF will later be replaced by CRLF are not themselves whitespace errors if `git diff --check` exits successfully, but record them accurately.

# FINAL CODEX RESPONSE

Report:

1. milestone status;
2. verified starting state;
3. implementation summary;
4. dataset source and identity;
5. environment and dependency versions;
6. configuration decisions;
7. acquisition results;
8. checksum results;
9. schema results;
10. target mapping and counts;
11. feature-role result;
12. `bishkred` decision;
13. row-key result;
14. split method, seed, sizes and class counts;
15. split membership checksum;
16. commands run;
17. test results;
18. lint and formatting results;
19. clean-environment reproduction result;
20. files created;
21. files modified;
22. files intentionally unchanged;
23. problems encountered and fixes;
24. unresolved issues;
25. limitations;
26. what the user should understand;
27. confirmation that preprocessing and modelling did not begin;
28. confirmation that later XAI/application work did not begin;
29. confirmation that Codex did not commit or push;
30. actual final `git status --short --untracked-files=all`;
31. recommended commit message;
32. advisory Phase 4 direction.

If Phase 3 completes successfully, recommend exactly:

`feat: build reproducible Aletheia data foundation`

Do not claim external supervisor approval.

# STOP RULE

Stop after implementing and verifying Phase 3.

Do not begin Phase 4.

Do not modify `docs/CURRENT_TASK.md`.

Do not commit or push.

The user will inspect Git status and verification evidence, commit and push the Phase 3 attempt, and return it for independent external supervisor review.
