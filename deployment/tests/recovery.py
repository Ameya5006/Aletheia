"""Reversible failures in the synthetic project, never in user-owned resources."""

import json
import subprocess
import time
import uuid

import httpx
from verify import BASE, EVIDENCE, compose, headers, refresh, wait_ready


def sql(statement):
    return compose(
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        "postgres",
        "-d",
        "aletheia_app",
        "-X",
        "-v",
        "ON_ERROR_STOP=1",
        "-Atc",
        statement,
    ).strip()


def snapshot():
    return sql(
        "SELECT json_build_object('predictions',"
        "(SELECT count(*) FROM prediction_events),"
        "'keys',(SELECT count(*) FROM idempotency_records),"
        "'events',(SELECT count(*) FROM audit_events),"
        "'head',(SELECT last_hash FROM audit_chain_heads));"
    )


def run():
    refresh()
    checks = []
    with httpx.Client(timeout=15, trust_env=False) as client:
        wait_ready(client)
        before = snapshot()
        sql("REVOKE INSERT ON audit_events FROM aletheia_runtime;")
        try:
            response = client.post(
                BASE + "/api/v1/predictions",
                json={
                    "schema_version": "application-v1",
                    "case_id": "synthetic-discharge-v1",
                    "model_version": "1",
                },
                headers=headers("engineer", uuid.uuid4()),
            )
            assert response.status_code == 503
            assert snapshot() == before
        finally:
            sql("GRANT INSERT ON audit_events TO aletheia_runtime;")
        checks.append(
            "failed audit INSERT suppresses HTTP success and rolls back all rows/head"
        )
        # Use an absent database, with the real secret read only inside the job.
        migration_head = sql("SELECT version_num FROM alembic_version;")
        failed_migration = (
            "import os,runpy; from pathlib import Path; "
            "from sqlalchemy.engine import make_url; "
            "u=make_url(Path('/run/secrets/owner_db_url').read_text().strip()); "
            "u=u.set(database='stage3_absent_database'); "
            "u=u.render_as_string(hide_password=False); "
            "os.environ['ALETHEIA_MIGRATION_URL']=u; "
            "import sys; sys.argv=['alembic','upgrade','head']; "
            "runpy.run_module('alembic',run_name='__main__')"
        )
        try:
            compose(
                "run",
                "--rm",
                "--no-deps",
                "--entrypoint",
                "python",
                "migrate",
                "-c",
                failed_migration,
            )
        except RuntimeError as error:
            failure = (EVIDENCE / str(error).split()[-1]).read_text()
            assert 'database "stage3_absent_database" does not exist' in failure
            assert sql("SELECT version_num FROM alembic_version;") == migration_head
        else:
            raise AssertionError("migration against absent database succeeded")
        wait_ready(client)
        checks.append("failed migration job leaves serving schema and data unchanged")
        # A bad trust anchor is confined to a one-shot container; serving stays pinned.
        try:
            compose(
                "run",
                "--rm",
                "--no-deps",
                "-e",
                "APP_RELEASE_SHA256=" + "0" * 64,
                "api",
            )
        except RuntimeError as error:
            failure = (EVIDENCE / str(error).split()[-1]).read_text()
            assert "release anchor mismatch" in failure
            checks.append("mismatched release container refuses startup")
        else:
            raise AssertionError("mismatched release started")
        wait_ready(client)
        for path in ("/mlflow", "/postgres", "/internal", "/openapi.json"):
            assert client.get(BASE + path).status_code == 404
        assert (
            client.post(BASE + "/api/v1/predictions", content=b"x" * 5000).status_code
            == 413
        )
        checks.append("internal route isolation and bounded proxy body")
        compose("stop", "frontend", "api", "mlflow", "postgres", "identity")
        start = time.monotonic()
        compose(
            "up", "-d", "--wait", "postgres", "identity", "mlflow", "api", "frontend"
        )
        wait_ready(client)
        healthy_seconds = time.monotonic() - start
        assert snapshot() == before
        checks.append(
            "graceful shutdown/restart retains data without operator side effects"
        )
        compose("stop", "api")
        compose("stop", "postgres")
        try:
            # Compose start repairs dependencies; direct start isolates this failure.
            subprocess.run(
                ["docker", "start", "aletheia-stage3-test-api-1"],
                check=True,
                capture_output=True,
                timeout=60,
            )
            wait_ready(client, 503)
        finally:
            compose("start", "postgres")
        wait_ready(client)
        checks.append("interrupted dependency startup fails closed and recovers")
    (EVIDENCE / "recovery.json").write_text(
        json.dumps(
            {
                "passed": checks,
                "healthy_restart_seconds": healthy_seconds,
            },
            indent=2,
        )
    )
    print(json.dumps({"passed": checks, "healthy_restart_seconds": healthy_seconds}))


if __name__ == "__main__":
    run()
