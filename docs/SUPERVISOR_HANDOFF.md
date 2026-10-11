# Supervisor Handoff — Macro Milestone 4 Stage 1 migration repair

The remaining migration-reproducibility defect is implemented and verified.
Stop for supervisor review; no next stage is authorized. All other valid Stage 1
work was preserved. No open implementation issue within this tested repair scope.

Changed in this repair only:

- migrations/versions/0001_backend.py
- migrations/versions/0003_integrity.py
- tests/application/test_postgres_api.py
- docs/PROJECT_REPORT.md
- docs/SUPERVISOR_HANDOFF.md

Historical revisions now contain fixed local SQL; no application-schema import,
metadata.create_all or live table object controls replay. Existing columns,
constraints, indexes, seed rows, trigger/function bodies, privileges, sequences and
deployment projection are retained; destructive downgrade refusal remains.
No business schema, architecture or public API change was introduced. Keeping the
DDL in each revision prevents a future live-model edit from rewriting history;
future schema changes require a new forward migration. No planning doc changed.

## Exact checks and evidence

Python commands below used .\.venv\Scripts\python.exe; tests used the disposable
PostgreSQL 18.6 loopback cluster through ALETHEIA_TEST_PG_ADMIN_URL.

`-m pytest tests/application/test_postgres_api.py -k 'historical_migrations or frozen_contract' -q -p no:cacheprovider --basetemp artifacts/stage1-repair/migration-focused-final`
**3 passed, 9 deselected, 1 warning in 9.57s.** Blocks historical application imports,
rejects create_all, verifies downgrade refusal, and runs empty-to-head and 0001-to-head
with empty/absent live schema objects. PostgreSQL catalog fingerprints match the
pre-repair contract at 0001 and head, including privilege and seed evidence:
0001: `d07c4c3d4a7ea9ad7679c5e7eec7a96d7085733e1147124fb2b198afd5cc5578`
head: `e795a550f0ce7c5b63a9c7a5cb841beba725df3107fa7618d99e7e89d3b93ddf`

`-m pytest tests/application/test_postgres_api.py tests/application/test_repair_postgres.py -q -p no:cacheprovider --basetemp artifacts/stage1-repair/migration-pg-integration`
**61 passed, 1 warning in 346.13s.** Runtime SQL privilege/audit negatives, append-only
chain and concurrent sequencing, API/RBAC, deadline rollback, ambiguous retries and
publication fault/retry tests remain valid. No skipped integration gate.

`-m pytest -m 'not live_data' -q -s -p no:cacheprovider --basetemp artifacts/stage1-repair/migration-offline`
**270 passed, 1 deselected, 63 warnings in 1056.03s.** Includes 148 application and
122 preserved offline tests. Clean disposable MLflow 3.17.0 integration is included
in the nine registry tests: empty registry, fresh import/download/parity/duplicate,
registered API reconciliation and six real crash-recovery cases. No prior version 7
was reused. Fresh test version **1**, run `0feb6fbb2c0349649aaeb8379c55f3cf`;
release `9983f7b574fb8e2bfe43df4a12b5900f061bcbef28d9efc3203f4f25ccb83b22`;
package `9910c70bf347ade2b31bc8cc0d3e344fd663a2d0128d388407011fcc7b8502bb`.
These identities are disposable test evidence, not production deployment.

`-m pip check`: no broken requirements. Windows/Linux transitive metadata checks:
102 applicable exact pins each, passed. `ruff check .`: passed.
`ruff format --check .`: 91 files already formatted. `git diff --check`: passed;
separate whitespace checks for all 22 existing new Stage 1 files passed.
90 protected SHA-256 hashes unchanged, including all ten frozen model/audit files;
CURRENT_TASK hash separately unchanged; all 20 original exact lock pins preserved.
Working-tree hash comparison proves all other existing Stage 1 files unchanged;
Git path inventory is identical to this repair's starting inventory.
Disposable application/MLflow databases and HTTP services were verified removed;
the owned temporary PostgreSQL cluster was stopped and its data removed.

## Limitations and review boundary

No research experiment or new dependency. No retraining/refit, holdout-record access,
research audit rerun, stash restore, commit, push, frontend, Compose or deployment
work. Existing regression fixture fits are software tests. Catalog fingerprints use
PostgreSQL 18 output; another major version would need equivalent contract checks.
Actual Linux container/public OIDC integration remains unverified and outside this
repair. Warnings: framework/scientific deprecations, MLflow explicit-signature hints
and the deliberate negative HMAC fixture. Windows PostgreSQL startup/service cleanup
required approved execution outside the sandbox; no test or cleanup issue remains.

Branch main; HEAD = origin/main = c00ba51fbc055085b44858eee0cd1b3c053bb2c7;
stash unchanged c6b91a13bf4338e559dfaad49f850dd719f5ca47. Nothing staged.
CURRENT_TASK's existing Git modification is user-owned and was not changed by Codex.
Exact final git status --short --untracked-files=all (no generated output):

```text
 M docs/CURRENT_TASK.md
 M docs/PROJECT_REPORT.md
 M docs/SUPERVISOR_HANDOFF.md
 M pyproject.toml
 M requirements.lock.txt
?? alembic.ini
?? migrations/env.py
?? migrations/versions/0001_backend.py
?? migrations/versions/0002_deadlines.py
?? migrations/versions/0003_integrity.py
?? src/aletheia/application/__init__.py
?? src/aletheia/application/api.py
?? src/aletheia/application/auth.py
?? src/aletheia/application/config.py
?? src/aletheia/application/operator.py
?? src/aletheia/application/pyfunc_model.py
?? src/aletheia/application/registry.py
?? src/aletheia/application/release.py
?? src/aletheia/application/schema.py
?? src/aletheia/application/store.py
?? tests/application/__init__.py
?? tests/application/conftest.py
?? tests/application/test_postgres_api.py
?? tests/application/test_registry.py
?? tests/application/test_release_auth.py
?? tests/application/test_repair_postgres.py
?? tests/application/test_repair_unit.py
```

Suggested next step: supervisor review, with no automatic Stage 2 progression.
Recommended user-performed commit after review:
`feat: implement Aletheia backend and MLOps foundation`.
