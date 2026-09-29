# Aletheia — Supervisor Handoff

## 1. Milestone and Status

**Phase 3 — Reproducible Data Foundation.**

Completed by Codex and pending external supervisor review. Phase 3 is not
externally approved by this document. Phase 4 and every later milestone remain
blocked.

## 2. Base and Resulting Commit State

- Branch: `main`.
- Verified base/HEAD/origin before implementation:
  `52be4130c8c4745c9f86f3b26a93497c3beeb2ff`.
- Current HEAD and `origin/main` remain that commit.
- Result: an uncommitted working-tree implementation; Codex made no commit,
  push, merge, branch, or history mutation.
- The starting status contained only the supervisor-supplied
  `M docs/CURRENT_TASK.md`; Codex did not modify that task.

## 3. Phase 2 Approval Recorded

Phase 2's research-first modular-monolith architecture is recorded as externally
supervisor-approved at commit `52be4130c8c4745c9f86f3b26a93497c3beeb2ff` in
ARCHITECTURE.md, EXECUTION_PLAN.md, PROJECT_REPORT.md, and ADR 0001.

## 4. Implemented and Verified

The Phase 3 package provides versioned configuration loading, controlled UCI
acquisition, archive/raw integrity checks, strict raw loading and schema/domain
validation, explicit adverse-target derivation, fail-closed feature-role views,
source-bound row keys, deterministic stratified membership, locked membership
verification, and a data-only `python -m aletheia.data` interface. It contains no
learned preprocessing, estimator, evaluation, or later application/audit work.

## 5. Dataset Identity

- Dataset: South German Credit, UCI record 573.
- Record: `https://archive.ics.uci.edu/dataset/573/south+german+credit`.
- DOI: `https://doi.org/10.24432/C5QG88`.
- Licence: CC BY 4.0.
- Fixed archive URL:
  `https://archive.ics.uci.edu/static/public/573/south+german+credit+update.zip`.
- Archive: 13,130 bytes; SHA-256
  `0b40d40eb7321693d559e247a556f88a6cc8df8489c3cb2ae084db7592584551`.
- Approved member: `SouthGermanCredit.asc`.
- Raw member: 47,940 bytes; SHA-256
  `5f363343f356ca38a0236baab849e472846399b2176ccc5bd686483dd8a7562f`.

The live acquisition and integration test verified both identities. Raw/archive
files remain ignored and untracked.

## 6. Environment and Exact Dependencies

Both clean environments used CPython 3.12.10 on Windows. The final project
environment used pip 26.2.1. `requirements.lock.txt` contains only exact index
packages, with no editable entry, `file://` reference, absolute path, or global
environment package:

```text
cloudpickle 3.1.2; colorama 0.4.6; iniconfig 2.3.0; joblib 1.6.0;
narwhals 2.26.0; numpy 2.5.3; packaging 26.3; pandas 3.0.5; pip 26.2.1;
pluggy 1.6.0; Pygments 2.21.0; pytest 9.1.1;
python-dateutil 2.9.0.post0; Ruff 0.16.6; scikit-learn 1.9.0;
SciPy 1.18.1; setuptools 84.0.0; six 1.17.0;
threadpoolctl 3.6.0; tzdata 2026.3
```

Direct runtime dependencies are pandas and scikit-learn. The development extra
contains pytest and Ruff. The standard library handles TOML, hashing, JSON,
paths, ZIP/BZIP2, argument parsing, and primary HTTP/TLS acquisition. Setuptools
is the build backend. No Requests or later-phase dependency was added.

## 7. Configuration and Validation Decisions

`configs/dataset.toml` fixes source identity, exact raw schema/order, row count,
target mapping, categorical domains, and observed-only quantitative ranges.
Purpose code 7 is accepted as documented despite being unobserved. Observed
ranges are explicitly not a future inference policy.

`configs/features.toml` separates semantic type from operational role. Its
disjoint exhaustive roles are:

- prediction: 15 approved fields;
- audit-only: `famges`, `alter`, `gastarb`;
- excluded: `telef`, `bishkred`;
- raw/derived target: `kredit`, `adverse_event`;
- metadata: `row_key`.

Unknown fields, missing role fields, overlap, or role/semantic coverage mismatch
fail closed. `model_input()` returns only the 15 prediction fields.

## 8. Acquisition and Checksum Result

Acquisition downloads into a temporary `.part` file, verifies archive size/hash
before opening it, rejects unsafe member paths, reads only the exact approved
BZIP2 member, verifies raw size/hash, then atomically publishes it. Failures
clean staging. A valid existing raw file is reused; an invalid one is refused
rather than overwritten. Unit tests verify hash mismatches, missing/unsafe/safe
extra members, partial cleanup, and both existing-file paths.

Python's OpenSSL trust path reported an expired certificate for the UCI chain,
while Windows Schannel validated the same fixed HTTPS URL and returned the
approved bytes. The implementation retains verified Python TLS as primary and
uses certificate-validating Windows `Invoke-WebRequest` only after that specific
verification failure. TLS verification is never disabled.

Final data-command output:

```text
verified raw dataset: data\raw\SouthGermanCredit.asc (47940 bytes, sha256=5f363343f356ca38a0236baab849e472846399b2176ccc5bd686483dd8a7562f)
validated 1000 rows, 21 raw columns; adverse_event counts={0: 700, 1: 300}; prediction_features=15
verified split: train=800, test=200, membership_sha256=af26b6036c6958a2dec48362fb1bfb075fca2ad7e482ed48ee7a49d7ec6d994b
```

## 9. Schema, Target, Roles, Keys, and Split

- Schema: exactly 1,000 data rows and 21 ordered integer raw columns; no nulls,
  undocumented categories, full-row duplicates, or predictor-only duplicates.
- Raw target is preserved: `kredit=0` bad/non-compliant and `kredit=1`
  good/compliant.
- Derived orientation: `adverse_event=1` for raw 0 and 0 for raw 1.
- Counts: 300 adverse and 700 non-adverse.
- `bishkred`: excluded by default because its “includes current credit” meaning
  lacks a safe authoritative observation cutoff. This is not proof of leakage.
- Keys: `sgc-0001` through `sgc-1000`, based on one-based post-header source
  position only after raw-hash verification; unique, repeatable, non-null, and
  aligned across all views.
- Split: `StratifiedShuffleSplit`, scikit-learn 1.9.0, test fraction 0.20,
  seed 42, stratified on `adverse_event`.
- Training: 800 rows, 240 adverse and 560 non-adverse.
- Test: 200 rows, 60 adverse and 140 non-adverse.
- Membership checksum:
  `af26b6036c6958a2dec48362fb1bfb075fca2ad7e482ed48ee7a49d7ec6d994b`.
- The committed lock contains aggregate counts and deterministic test keys, but
  no per-row feature or target values. Training is the complement.

## 10. Files Created

Configuration/package:

- `configs/dataset.toml`, `configs/features.toml`,
  `configs/splits/south_german_credit_v1.json`;
- `pyproject.toml`, `requirements.lock.txt`;
- `src/aletheia/__init__.py`, `config.py`, `contracts.py`;
- `src/aletheia/data/__init__.py`, `__main__.py`, `acquire.py`, `load.py`,
  `validate.py`, `target.py`, `roles.py`, `split.py`.

Tests:

- `tests/conftest.py`;
- `tests/unit/test_config.py`, `test_target.py`, `test_roles.py`,
  `test_split.py`;
- `tests/data/test_acquire.py`, `test_load_validate.py`;
- `tests/integration/test_data_foundation.py`.

## 11. Documentation Modified

- `.gitignore`: environments, caches, build metadata, raw/processed data,
  archives, generated artifacts/reports, and local secret/config patterns.
- `docs/ARCHITECTURE.md`: Phase 2 approval and Phase 3 implementation status.
- `docs/DATASET_AUDIT.md`: `bishkred`, stable keys, fixed split, references,
  and limitations; Phase 1 computed evidence was preserved.
- `docs/EXECUTION_PLAN.md`: Phase 2 approved, Phase 3 pending review, later
  phases blocked.
- `docs/PROJECT_REPORT.md`: implementation, rationale, modules/flows, tests,
  problems, concepts, interview/viva material, evidence, and limitations.
- `docs/decisions/0001-research-first-modular-monolith.md`: accepted status and
  implemented/deferred boundary.
- `docs/SUPERVISOR_HANDOFF.md`: replaced with this Phase 3 evidence.

`AGENTS.md`, `prompt.txt`, `CLAUDE.md`, and `README.md` are intentionally
unchanged. `docs/CURRENT_TASK.md` remains only the user/supervisor-installed
task change.

## 12. Commands and Exact Verification Results

Meaningful setup/implementation commands included `python -m venv .venv`,
installation of `.[dev]`, `pip freeze --all --exclude-editable`, the three data
commands, split-contract creation, Ruff formatting, offline pytest, and the
explicit live test. Network-dependent installs/acquisition were rerun only after
the sandbox correctly required authorization.

Final clean project environment:

```text
python --version                         -> Python 3.12.10
python -m pip --version                  -> pip 26.2.1 (.venv, Python 3.12)
python -m pip check                      -> No broken requirements found.
python -m ruff check .                   -> All checks passed!
python -m ruff format --check .          -> 29 files already formatted
python -m pytest -m "not live_data"      -> 48 passed, 1 deselected in 7.63s
```

Explicit live integration test, using `ALETHEIA_RUN_LIVE_DATA=1` and an ignored
workspace-local pytest temp directory:

```text
python -m pytest -p no:cacheprovider --basetemp data/processed/pytest-live -m live_data
-> 1 passed, 48 deselected in 13.71s
```

Second clean Python 3.12 environment:

```text
python -m pip install -r requirements.lock.txt
-> all 20 exact packages installed successfully
python -m pip install --no-deps --no-build-isolation .
-> aletheia-decision-auditor 0.1.0 built and installed successfully
python -m pip check
-> No broken requirements found.
python -m ruff check .
-> All checks passed!
python -m ruff format --check .
-> 29 files already formatted
python -m pytest -m "not live_data"
-> 48 passed, 1 deselected in 19.05s
```

Repository checks after documentation and handoff:

```text
git diff --check
-> exit 0; no whitespace errors; LF-to-CRLF working-copy warnings only
git diff --stat
-> exit 0; eight tracked files reported (Git omits the authorized untracked
   source/config/test files from this statistic)
git status --short --untracked-files=all
-> exit 0; exact output recorded below
```

## 13. Problems Encountered and Fixes

1. Sandboxed network access was initially denied. Required package and UCI
   operations were rerun through the explicit approval path.
2. Python TLS rejected the UCI certificate chain. A fixed-URL, Windows
   certificate-validating fallback was added; disabling TLS was rejected.
3. The first offline run had two failures: a checksum test changed archive size,
   and target-count validation masked duplicate detection. The test now mutates
   one byte without changing size, and duplicate validation precedes aggregate
   target counts. The next offline run passed all 48 selected tests.
4. The first elevated live-test attempt could not access the user pytest temp
   directory; the next lacked its parent directory. An ignored
   `data/processed` base temp and disabled pytest cache isolated the live run;
   it then passed.

## 14. Limitations and Unresolved Issues

- External supervisor review of Phase 3 is unresolved.
- The dataset is old, regional, granted-only, intentionally oversamples adverse
  cases, has transformed amount, and has no dates or entity identifiers.
- The split preserves class proportions but cannot measure temporal or
  customer/entity generalisation and cannot rule out undisclosed repeat people.
- The 30% adverse rate is not source-population prevalence or calibrated risk.
- Fairness remains unsupported/disabled; no group metric was calculated.
- Future encoding, learned preprocessing, CV folds, model/metric/threshold
  choices, persistence, XAI, and application technology remain unimplemented.
- The Windows TLS fallback depends on built-in Windows PowerShell/Schannel when
  Python's verified TLS path fails. Other platforms keep the Python path and
  fail closed on certificate errors.

## 15. Scope Confirmation

No imputation, encoding, scaling, feature engineering/selection, resampling,
cross-validation, model definition/training/serialization, metric, threshold,
held-out performance inspection, or experiment-run store was implemented.

No SHAP, permutation importance, local explanation, counterfactual, stability,
fairness, notebook, API, UI, database, MLflow/DVC, Docker, deployment,
authentication, or monitoring work began.

Codex did not commit or push.

## 16. Actual Final Git Status

```text
 M .gitignore
 M docs/ARCHITECTURE.md
 M docs/CURRENT_TASK.md
 M docs/DATASET_AUDIT.md
 M docs/EXECUTION_PLAN.md
 M docs/PROJECT_REPORT.md
 M docs/SUPERVISOR_HANDOFF.md
 M docs/decisions/0001-research-first-modular-monolith.md
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

No raw data, archive, environment, cache, build output, generated report, model,
notebook, API, frontend, database, container, or deployment path appears.

## 17. Supervisor Evidence and Suggested Next Step

Inspect the two TOML contracts, locked split JSON, `src/aletheia/data/`, the 49
tests, PROJECT_REPORT.md, and the exact final diff/status. The recommended user
commit message after inspection is:

`feat: build reproducible Aletheia data foundation`

Advisory only: if Phase 3 is externally approved, a replacement
CURRENT_TASK.md may define a bounded Phase 4 leakage-safe dummy/logistic
baseline with training-only/fold-local preprocessing and a predeclared
evaluation contract. This handoff does not authorize Phase 4.
