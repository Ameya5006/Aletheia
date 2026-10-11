## Starting-State Gate — Supervisor Repair

This is a continuation and repair of the existing uncommitted Stage 1 implementation.

Before editing:

1. Read `AGENTS.md` and this file completely.
2. Confirm branch is `main`.
3. Confirm `HEAD` and local `origin/main` equal:

`c00ba51fbc055085b44858eee0cd1b3c053bb2c7`

4. Confirm the existing stash remains unchanged.
5. Confirm Git status contains exactly the following existing Stage 1 work:

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
These files constitute the authorized incomplete Stage 1 implementation. Preserve valid work and repair it in place.
If any additional path appears, stop and explain it.
docs/CURRENT_TASK.md is user-owned and must not be modified by Codex.

Then add this section:

```markdown
## Supervisor-Directed Stage 1 Repair

Independent review found implementation defects. Stage 1 remains incomplete until all are repaired and verified.

This is implementation work, not a documentation phase. Maintain the 95% implementation/testing and 5% concise-documentation policy.

Required repairs:

1. Make the dependency lock portable to Linux containers:
   - `pywin32` must be Windows-only through a valid PEP 508 marker or removed if unnecessary.
   - Parse requirements with `packaging.requirements.Requirement`.
   - Evaluate platform markers correctly.
   - Verify exact versions only for applicable requirements.
   - Preserve frozen scientific pins and valid markers in MLflow requirements.

2. Make MLflow import and approval crash-safe:
   - create model versions in `verifying`, not `verified`;
   - mark verified only after independent download, package/hash verification, calibrated parity, durable receipt and completed run;
   - quarantine unverifiable partial imports;
   - provide deterministic recovery for valid interrupted imports;
   - make PostgreSQL model registration idempotent for an identical identity and fail closed for conflicts;
   - make approval publication safely retryable without duplicate model, release or audit rows.

3. Complete lifecycle reconciliation:
   - activation, rollback and revocation must reconcile PostgreSQL state, MLflow tags/aliases and the explicit deployment pin;
   - prevent contradictory active identities;
   - aliases alone must never authorize serving;
   - test interrupted lifecycle operations and retries.

4. Replace the localhost-only MLflow rule with typed trusted-endpoint configuration:
   - allow exact loopback endpoints in development/test;
   - allow an explicitly configured private Compose hostname such as `mlflow`;
   - reject arbitrary hosts, URLs, redirects and unconfigured endpoints.

5. Enforce reverse audit integrity:
   - every committed `prediction_created` event must reference exactly one matching prediction;
   - every committed `review_created` event must reference exactly one matching review;
   - preserve typed bindings for release/bootstrap/grant events;
   - runtime credentials must be unable to commit orphan or mismatched events;
   - add direct PostgreSQL negative tests.

6. Correct timeout handling:
   - do not assume async cancellation terminates synchronous thread-pool work;
   - a deadline response must not be followed by a late prediction/audit/idempotency commit;
   - preserve internal deadlines, PostgreSQL timeouts and ambiguous-commit idempotent recovery;
   - test the database again after waiting beyond the returned timeout.

7. Complete operator RBAC lifecycle:
   - expose authenticated, audited `revoke-role` and `disable-subject` commands;
   - refuse unauthorized, repeated, conflicting and unsafe self-lockout operations;
   - disabled subjects must lose access immediately and before transaction commit;
   - do not add public administrative write endpoints.

8. Make MLflow integration evidence reproducible:
   - use a clean disposable MLflow backend with no prior version for the tested release;
   - prove fresh import, verified download/parity and duplicate idempotency;
   - do not rely on existing version 7;
   - stop disposable services afterward.

Add meaningful fault-injection, concurrency, security and cross-platform requirement tests for every repair.

Keep documentation updates limited to concise corrections in `docs/PROJECT_REPORT.md` and `docs/SUPERVISOR_HANDOFF.md`. Do not create new documentation or modify broader planning documents.

Run:

- dependency consistency;
- Ruff lint and formatting;
- focused repair tests;
- real PostgreSQL migration/integration tests;
- clean disposable MLflow integration;
- complete offline regression suite;
- global `git diff --check`;
- protected/frozen hash verification.

No generated database, registry, release, cache, credential or service output may appear in Git status.

Stop after Stage 1 repair verification. Do not commit, push or begin Stage 2.