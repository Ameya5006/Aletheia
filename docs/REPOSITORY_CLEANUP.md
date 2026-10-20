# Repository content audit

Presentation audit of the tracked tree at `963050e` (2026-10-20), before the
presentation additions. This is a content classification, not authorization to
delete local resources. **No files were moved or deleted.**

## Every tracked root file

| File | Classification | Reason |
|---|---|---|
| `.dockerignore` | Keep publicly visible; operational | Allowlisted build context excludes local evidence, secrets and browser output. |
| `.gitattributes` | Protected and untouchable | Preserves the frozen split-lock line endings; normalization can break byte identities. |
| `.gitignore` | Keep publicly visible; operational | Excludes local data, artifacts, environments and secrets. |
| `AGENTS.md` | Protected and untouchable | Permanent governance and Git authority. |
| `CLAUDE.md` | Keep publicly visible | Directs another coding tool to the same governing instructions; not a duplicate implementation. |
| `README.md` | Keep publicly visible; revise presentation | Public entry point; detailed setup and design belong under `docs/`. |
| `alembic.ini` | Keep publicly visible; operational | Migration discovery and source path; used by the operator and tests. |
| `prompt.txt` | Protected and untouchable | Permanent original vision, explicitly referenced by governance and the report. |
| `pyproject.toml` | Keep publicly visible; operational | Package metadata, Python version, CLI and test/lint configuration. |
| `requirements.lock.txt` | Protected dependency/release input | Exact dependencies participate in runtime release verification. |

All ten tracked root files have a distinct purpose. Moving package, migration,
Git or container configuration would break established tool discovery or require
behavior changes. No objectively accidental root file was found.

## Documentation hierarchy

| Location | Classification and purpose |
|---|---|
| `docs/CURRENT_TASK.md` | Protected supervisor authority; retain the current approved task. |
| `docs/PRODUCT_REQUIREMENTS.md`, `docs/EXECUTION_PLAN.md` | Keep; approved scope and sequencing, with historical sections retained. |
| `docs/ARCHITECTURE.md`, `docs/DEPLOYMENT_ARCHITECTURE.md` | Keep; approved architecture and deployment record. New HLD/LLD provide a navigable current view. |
| `docs/PROJECT_REPORT.md` | Keep; canonical engineering, learning and evidence history. Incremental updates only. |
| `docs/SUPERVISOR_HANDOFF.md` | Keep; concise current review state, rewritten for each meaningful milestone. |
| `docs/DATASET_AUDIT.md` | Keep; secondary credit benchmark provenance, still referenced by the project report and execution plan. |
| `docs/HEALTHCARE_DATASET_AUDIT.md` | Keep; primary healthcare data and feature provenance. |
| `docs/LOCAL_CLEANUP_DRY_RUN.md` | Keep; historical inventory and preservation conditions, not a current deletion list. |
| `docs/decisions/0001-*.md` through `0008-*.md` | Keep all eight decision records; preserve rationale and supersession context. |
| `docs/model_cards/healthcare_readmission_v1.md` | Protected release input; do not edit or move as presentation cleanup. |
| `docs/history/SUPERVISOR_HANDOFF_20261017.md` | Preserve under history; original cloud checkpoint. |
| `docs/history/SUPERVISOR_HANDOFF_20261018_PRE_REPAIR.md` | Preserve under history; pre-repair checkpoint and link to the preceding handoff. |
| `docs/history/SUPERVISOR_HANDOFF_20261018_EXPRESS_REPAIR.md` | Preserve under history; referenced by architecture and project report. |
| New HLD, LLD, maintainability, local-development and presentation documents | Keep under `docs/`; link from the public entry point rather than enlarge the root. |
| Sanitized screenshots and compressed walkthrough | Keep under documentation assets only after inspection; raw recordings remain ignored. |

History was checked with `git log -- docs/history docs/LOCAL_CLEANUP_DRY_RUN.md`;
these records entered the tracked deployment history in `aa8c517`. References
were checked in README, governance and documentation. Their age is not evidence
of obsolescence. No existing document needs a move to achieve a logical hierarchy.

## Operational and protected content

Keep `.github/workflows/`, `deployment/`, `migrations/`, `tests/`, `frontend/`,
`src/` and `configs/`. They contain workflow, local/cloud deployment, migration,
security, recovery, contract and model-verification responsibilities. A
presentation cleanup must not remove them to shorten the file listing.

Preserve frozen source/configuration bindings, approved release manifests and
pins, all model/audit artifacts, one-time holdout claim files, backup manifests
and dumps, scan/SBOM evidence, Docker data and the protected Git stash. Ignored
does not mean disposable.

| Category | Decision |
|---|---|
| Move under a logical documentation folder | None required for existing tracked files. New documents start under `docs/`. |
| Preserve under `docs/history/` | Retain the three existing handoffs in place; no historical evidence is discarded. |
| Ignore as generated local evidence | `artifacts/`, raw/processed data, generated reports, environments/caches, browser traces/storage and raw recordings remain untracked. |
| Candidate for deletion | None established by this audit. |
| Actual moves/deletions | None. Consequently no relocation link repairs are needed. |

No Docker cleanup was performed. The [existing dry run](LOCAL_CLEANUP_DRY_RUN.md)
remains historical; its counts must not be presented as a fresh inventory.

## Licence state

The tracked tree contains no project `LICENSE`, `LICENCE` or `COPYING` file,
and neither Python nor frontend package metadata declares a project licence.
Dependency licence inventories and dataset attribution are separate from a
licence for this repository's source. No licence was added or changed.
Recommendation: the owner should choose explicit source-code licence terms
after reviewing third-party obligations; this requires separate approval.
