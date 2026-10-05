# Supervisor Handoff — Macro Milestone 1 review repair

Status: Macro Milestone 1 was committed at `49753d5` and received an external
**PASS WITH MINOR FIXES** verdict. This narrow documentation and offline-test
repair is implemented locally; review of the repair is pending. Macro Milestone 2
has not begun or been authorized.

## Current result
Aletheia is healthcare-primary with South German Credit retained as the secondary approved benchmark. The official UCI 296 dataset (DOI 10.24432/C5230J; CC BY 4.0) passed an educational, non-clinical audit. At discharge, raw <30 means positive 30-day readmission; >30 and NO are negative. Death/hospice disposition codes 11, 13, 14, 19, 20, 21 are excluded. The 99,343-row cohort contains 69,990 patients and 11,314 positives. No healthcare model was trained.

Implemented verified archive/member hashes, two-member controlled extraction, 50-column strict loader, seven-field ? normalization, target/cohort/key validation, default-deny 13-predictor role policy, separate audit-only race/gender/age, deterministic patient-level 80/20 split and cross-referenced JSON lock. Training: 79,808 encounters, 56,178 patients, class 0 70,734, class 1 9,074. Held out: 19,535 encounters, 13,812 patients, class 0 17,295, class 1 2,240. Membership SHA-256: 6879c9e652887c4a8b59797dd2260ad79795958fb3eebff1b22c3fe33b075316. No patient/encounter overlap. Class counts are integrity metadata, not modelling results.

## Decisions and architecture
The credit code and training-only baseline stay in place. Healthcare policy is isolated under src/aletheia/domains/healthcare. Future shared use cases will be extracted only where both domains need them. Patient grouping prevents entity leakage; discharge timing permits encounter summaries, while disposition itself is excluded. SHA-256 group assignment favors isolation and stability over exact stratification. No credit migration. Future selected stack: Python/scikit-learn, MLflow, FastAPI, PostgreSQL, React/TypeScript, Docker/Compose, GitHub Actions, monitoring, cards, RBAC and append-only audit. DagsHub hosting, DVC and managed host are provisional. RunwayML rejected; similar-case retrieval is not collaborative filtering. No future dependency installed.

## Files and evidence
This repair modifies only README.md, docs/PROJECT_REPORT.md,
docs/SUPERVISOR_HANDOFF.md, and tests/healthcare/test_foundation.py. It adds
synthetic tests for all six frozen death/hospice exclusions, eligible-row
preservation, split-lock overwrite refusal, and redirect/byte-identity
acquisition cleanup. It does not change healthcare source, contracts, split
algorithm/lock, dependencies, credit implementation, or docs/CURRENT_TASK.md.
Inspect the new tests beside foundation.py `cohort`, `write_split_lock`, and
`acquire`, then the current overview and README status. The committed milestone
evidence remains in the dataset audit, contracts, lock, ADRs, and report.

## Executed checks
Repair checks used repository `.venv` Python 3.12.10 and exited 0:
- `.\.venv\Scripts\python.exe -m pip check`: No broken requirements found.
- `.\.venv\Scripts\python.exe -m ruff check .`: All checks passed.
- `.\.venv\Scripts\python.exe -m ruff format --check .`: 54 files already formatted.
- `.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp data/processed/pytest-healthcare-review-final tests/healthcare/test_foundation.py`: 11 passed in 0.66s.
- `.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp data/processed/pytest-healthcare-review-suite -m 'not live_data'`: 77 passed, 1 deselected, 25 warnings in 7.82s. All 66 pre-existing credit/offline tests passed; the 25 warnings are the existing scikit-learn LogisticRegression penalty deprecation.
- `git diff --check`: passed; LF-to-CRLF notices are advisory.
- `git show --check --oneline HEAD`: passed at the clean start of this repair.

The committed milestone's healthcare CLI acquire, lock, and verify checks
reported training 79,808 and held-out 19,535 encounters; they were not rerun
for this review repair.
No live-data pytest was run. No held-out prediction, model selection, or training
was performed in this repair.

## Problems and limits
The earlier pre-commit `git diff --check` exited 2 because of a trailing blank
line in user-owned docs/CURRENT_TASK.md. The user removed that line before
committing `49753d5`; the final committed `git diff --check` passed. This is a
**resolved** discrepancy, not an outstanding milestone failure. No source
defect was exposed by the new refusal tests.

Python urllib failed TLS chain verification on this Windows environment after network permission. Windows curl with verified TLS retrieved the official archive; byte hashes and file content were checked. The CLI's Python downloader fails closed if trust is broken. An initial config patch required creating the authorized directories; Ruff fixed initial long lines. No leakage bug or model failure was observed. Historical 1999–2008 data lack encounter dates and hospital IDs; no external/clinical validation or fairness measurement exists. Discharge-time availability of each selected input needs operational confirmation. Sparse/unknown subgroups limit fairness, and treatment changes cannot be presented as clinically actionable counterfactuals.

Unresolved: review of this minor repair; later model protocol, registry host,
DVC adoption, cloud host/cost, clinical timestamp verification, and data/privacy
governance. Suggested next step is supervisor review of this repair, then a
separate authorization before any Macro Milestone 2 work. The user performs
commit/push. Recommended repair commit message:
`docs: finalize healthcare foundation review`.
