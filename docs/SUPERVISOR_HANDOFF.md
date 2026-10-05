# Supervisor Handoff — Macro Milestone 1

Status: implemented and locally verified; independent external review pending. No later milestone authorized or begun.

## Current result
Aletheia is healthcare-primary with South German Credit retained as the secondary approved benchmark. The official UCI 296 dataset (DOI 10.24432/C5230J; CC BY 4.0) passed an educational, non-clinical audit. At discharge, raw <30 means positive 30-day readmission; >30 and NO are negative. Death/hospice disposition codes 11, 13, 14, 19, 20, 21 are excluded. The 99,343-row cohort contains 69,990 patients and 11,314 positives. No healthcare model was trained.

Implemented verified archive/member hashes, two-member controlled extraction, 50-column strict loader, seven-field ? normalization, target/cohort/key validation, default-deny 13-predictor role policy, separate audit-only race/gender/age, deterministic patient-level 80/20 split and cross-referenced JSON lock. Training: 79,808 encounters, 56,178 patients, class 0 70,734, class 1 9,074. Held out: 19,535 encounters, 13,812 patients, class 0 17,295, class 1 2,240. Membership SHA-256: 6879c9e652887c4a8b59797dd2260ad79795958fb3eebff1b22c3fe33b075316. No patient/encounter overlap. Class counts are integrity metadata, not modelling results.

## Decisions and architecture
The credit code and training-only baseline stay in place. Healthcare policy is isolated under src/aletheia/domains/healthcare. Future shared use cases will be extracted only where both domains need them. Patient grouping prevents entity leakage; discharge timing permits encounter summaries, while disposition itself is excluded. SHA-256 group assignment favors isolation and stability over exact stratification. No credit migration. Future selected stack: Python/scikit-learn, MLflow, FastAPI, PostgreSQL, React/TypeScript, Docker/Compose, GitHub Actions, monitoring, cards, RBAC and append-only audit. DagsHub hosting, DVC and managed host are provisional. RunwayML rejected; similar-case retrieval is not collaborative filtering. No future dependency installed.

## Files and evidence
Modified: README.md, docs/ARCHITECTURE.md, docs/EXECUTION_PLAN.md, docs/PROJECT_REPORT.md, docs/SUPERVISOR_HANDOFF.md. User-owned docs/CURRENT_TASK.md was already modified and was not edited by Codex.
Created: configs/datasets/healthcare_uci296_v1.toml; configs/features/healthcare_uci296_v1.toml; configs/splits/healthcare_uci296_v1.toml and .lock.json; docs/PRODUCT_REQUIREMENTS.md, HEALTHCARE_DATASET_AUDIT.md, DEPLOYMENT_ARCHITECTURE.md; ADRs 0003–0005; src/aletheia/domains/__init__.py and healthcare foundation/CLI; tests/healthcare/test_foundation.py.
Inspect the three contracts and lock, foundation.py functions load_contracts/acquire/extract/load_raw/cohort/feature_views/build_split_lock/verify_split_lock/partition, offline tests, dataset audit, README, and deployment decision. The named WIP stash was inventoried read-only in PROJECT_REPORT.md; no stashed file was restored.

## Executed checks
Repository .venv Python 3.12.10:
- python -m pip check: No broken requirements found.
- python -m ruff check .: All checks passed.
- python -m ruff format --check .: 54 files already formatted.
- python -m pytest -m "not live_data" with cache disabled and ignored Windows basetemp: 73 passed, 1 deselected, 25 warnings in 9.25s. Seven new healthcare tests and all 66 pre-existing credit/offline tests passed. The 25 warnings are the pre-existing scikit-learn LogisticRegression penalty deprecation.
- Healthcare CLI acquire, lock and verify completed against the official archive; verify reported train 79,808 and test 19,535.
- git diff --check exited 2 and flags only a pre-existing trailing blank line in user-owned docs/CURRENT_TASK.md:746, which Codex is forbidden to edit. The same check excluding that path exited 0 for Codex's tracked modifications. LF-to-CRLF notices are advisory.
No live-data pytest was run. No held-out prediction, model selection or training was performed.

## Problems and limits
Python urllib failed TLS chain verification on this Windows environment after network permission. Windows curl with verified TLS retrieved the official archive; byte hashes and file content were checked. The CLI's Python downloader fails closed if trust is broken. An initial config patch required creating the authorized directories; Ruff fixed initial long lines. No leakage bug or model failure was observed. Historical 1999–2008 data lack encounter dates and hospital IDs; no external/clinical validation or fairness measurement exists. Discharge-time availability of each selected input needs operational confirmation. Sparse/unknown subgroups limit fairness, and treatment changes cannot be presented as clinically actionable counterfactuals.

Unresolved: external supervisor acceptance; later model protocol, registry host, DVC adoption, cloud host/cost, clinical timestamp verification, data/privacy governance. Suggested next step is supervisor review, then separate authorization for Macro Milestone 2. User performs commit/push. Recommended message: feat: establish Aletheia healthcare foundation.
