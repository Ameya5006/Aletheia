import copy
import hashlib
import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from aletheia.application import schema as s
from aletheia.application.api import create_app
from aletheia.application.auth import Identity, ServiceError
from aletheia.application.release import CASE
from aletheia.application.store import audit, verify_chain

ISSUER = "https://identity.example.test"
ENGINEER = Identity(ISSUER, "synthetic-engineer", frozenset({"engineer"}))
REVIEWER = Identity(ISSUER, "synthetic-reviewer", frozenset({"reviewer"}))
BODY = {"schema_version": "application-v1", "case_id": CASE, "model_version": "1"}


def predict(runtime, release, key=None, **kwargs):
    return runtime.command(
        ENGINEER, BODY, key or uuid.uuid4(), uuid.uuid4(), "1", release, **kwargs
    )


def test_migrations_bootstrap_once_and_conflict(db):
    owner, runtime = db
    with owner.engine.begin() as conn:
        assert owner.migrated(conn)
    sid = owner.bootstrap(ISSUER, "synthetic-admin")
    with owner.engine.begin() as conn:
        grant = conn.execute(sa.select(s.grants)).mappings().one()
        assert grant["subject_id"] == sid and grant["granted_by"] is None
        assert (
            conn.execute(sa.select(s.events.c.event_type)).scalar()
            == "initial_administrator_bootstrap"
        )
    with pytest.raises(ServiceError) as exc:
        owner.bootstrap(ISSUER, "synthetic-admin")
    assert exc.value.status == 409
    with pytest.raises(ServiceError) as exc:
        runtime.bootstrap(ISSUER, "synthetic-other")
    assert exc.value.status == 403


def test_runtime_privileges_and_constraints(prepared, release):
    owner, runtime, _, _, _ = prepared
    value = predict(runtime, release)
    for table in (s.events, s.predictions, s.reviews, s.models, s.releases, s.keys):
        with pytest.raises(SQLAlchemyError), runtime.engine.begin() as conn:
            conn.execute(table.delete())
        with pytest.raises(SQLAlchemyError), runtime.engine.begin() as conn:
            conn.execute(sa.text(f"TRUNCATE {table.name} CASCADE"))
    with pytest.raises(SQLAlchemyError), runtime.engine.begin() as conn:
        conn.execute(s.subjects.insert().values(issuer=ISSUER, sub="forged"))
    for number in (float("nan"), float("inf"), -0.1, 1.1):
        changed = dict(value, id=uuid.uuid4(), probability=number)
        with pytest.raises(SQLAlchemyError), owner.engine.begin() as conn:
            changed["audit_event_id"] = audit(
                conn,
                value["actor_id"],
                "prediction_created",
                changed["id"],
                uuid.uuid4(),
                {"case_id": CASE},
            )
            conn.execute(s.predictions.insert().values(**changed))
    with pytest.raises(SQLAlchemyError), owner.engine.begin() as conn:
        conn.execute(s.events.update().values(event_hash="a" * 64))


def test_idempotency_concurrency_and_chain(prepared, release):
    _, runtime, _, _, _ = prepared
    key = uuid.uuid4()
    with ThreadPoolExecutor(max_workers=4) as pool:
        values = list(pool.map(lambda _: predict(runtime, release, key), range(4)))
    assert len({x["id"] for x in values}) == 1
    assert predict(runtime, release, key)["id"] == values[0]["id"]
    different = dict(BODY, model_version="2")
    with pytest.raises(ServiceError) as exc:
        runtime.command(ENGINEER, different, key, uuid.uuid4(), "1", release)
    assert exc.value.status == 409
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: predict(runtime, release), range(4)))
    with runtime.engine.begin() as conn:
        events = [
            dict(x)
            for x in conn.execute(
                sa.select(s.events).order_by(s.events.c.sequence)
            ).mappings()
        ]
        head = conn.execute(sa.select(s.heads)).mappings().one()
        assert verify_chain(events) == (head["last_sequence"], head["last_hash"])
        assert (
            conn.execute(sa.select(sa.func.count()).select_from(s.predictions)).scalar()
            == 5
        )
    damaged = copy.deepcopy(events)
    damaged[-1]["payload"]["probability"] = "0.99"
    with pytest.raises(ValueError):
        verify_chain(damaged)


def test_rollback_on_audit_failure_and_deadline(prepared, release, monkeypatch):
    _, runtime, _, _, _ = prepared
    import aletheia.application.store as module

    original = module.audit

    def failed(*args, **kwargs):
        original(*args, **kwargs)
        raise ServiceError(503, "injected_commit_failure")

    monkeypatch.setattr(module, "audit", failed)
    with pytest.raises(ServiceError):
        predict(runtime, release)
    with runtime.engine.begin() as conn:
        assert (
            conn.execute(sa.select(sa.func.count()).select_from(s.predictions)).scalar()
            == 0
        )
        assert (
            conn.execute(sa.select(sa.func.count()).select_from(s.keys)).scalar() == 0
        )
        assert (
            conn.execute(
                sa.select(sa.func.count())
                .select_from(s.events)
                .where(s.events.c.event_type == "prediction_created")
            ).scalar()
            == 0
        )
    monkeypatch.setattr(module, "audit", original)
    with pytest.raises(ServiceError) as exc:
        predict(runtime, release, deadline=time.monotonic() - 1)
    assert exc.value.status == 504


def test_review_races_permissions_and_scoped_history(prepared, release):
    owner, runtime, admin, _, _ = prepared
    prediction = predict(runtime, release)
    body = dict(
        schema_version="application-v1",
        decision="acknowledged",
        reason_code="evidence_reviewed",
        expected_revision=0,
    )

    def review():
        try:
            return runtime.command(
                REVIEWER,
                body,
                uuid.uuid4(),
                uuid.uuid4(),
                "1",
                release,
                prediction["id"],
            )
        except ServiceError as exc:
            return exc.status

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: review(), range(2)))
    assert sum(isinstance(x, dict) for x in results) == 1
    assert 409 in results
    with pytest.raises(ServiceError) as exc:
        runtime.command(
            ENGINEER, body, uuid.uuid4(), uuid.uuid4(), "1", release, prediction["id"]
        )
    assert exc.value.status == 403
    with runtime.engine.begin() as conn:
        visible = list(conn.execute(runtime.audit_query(conn, REVIEWER)).mappings())
        assert {x["event_type"] for x in visible} == {
            "prediction_created",
            "review_created",
        }
        own = list(conn.execute(runtime.audit_query(conn, ENGINEER)).mappings())
        assert len(own) == 1 and own[0]["event_type"] == "prediction_created"
        assert len(list(conn.execute(runtime.audit_query(conn, admin)))) > len(visible)
    with owner.engine.begin() as conn:
        conn.execute(
            s.subjects.update()
            .where(s.subjects.c.sub == "synthetic-engineer")
            .values(disabled_at=sa.func.now())
        )
    with pytest.raises(ServiceError):
        predict(runtime, release)


def test_api_all_routes_rbac_body_redaction(
    prepared, release, settings, tokens, caplog
):
    _, runtime, _, _, _ = prepared
    token, verifier, _, _ = tokens
    app = create_app(settings, release, runtime, verifier)
    client = TestClient(app)
    headers = {
        "Authorization": "Bearer " + token(),
        "Idempotency-Key": str(uuid.uuid4()),
    }
    caplog.set_level("INFO", logger="aletheia.http")
    public = [
        "health/live",
        "health/ready",
        "models/current",
        "models/current/card",
        "demo/cases",
        "explanations/global",
        "explanations/local/" + CASE,
        "audits/stability",
        "audits/subgroups",
        "counterfactuals/feasibility",
    ]
    for endpoint in public:
        result = client.get("/api/v1/" + endpoint)
        assert result.status_code == 200, result.text
        assert result.json()["schema_version"] == "application-v1"
        assert result.headers["X-Request-ID"] == result.json()["request_id"]
    result = client.post("/api/v1/predictions", json=BODY, headers=headers)
    assert result.status_code == 201, result.text
    prediction = result.json()["data"]["prediction_id"]
    assert (
        client.post("/api/v1/predictions", json=BODY, headers=headers).json()["data"]
        == result.json()["data"]
    )
    assert (
        client.get("/api/v1/predictions/" + prediction, headers=headers).status_code
        == 200
    )
    other = {"Authorization": "Bearer " + token(sub="synthetic-other")}
    assert (
        client.get("/api/v1/predictions/" + prediction, headers=other).status_code
        == 404
    )
    reviewer = {
        "Authorization": "Bearer "
        + token(sub="synthetic-reviewer", roles=["reviewer"]),
        "Idempotency-Key": str(uuid.uuid4()),
    }
    body = dict(
        schema_version="application-v1",
        decision="acknowledged",
        reason_code="evidence_reviewed",
        expected_revision=0,
    )
    assert (
        client.post(
            f"/api/v1/predictions/{prediction}/reviews", json=body, headers=headers
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"/api/v1/predictions/{prediction}/reviews", json=body, headers=reviewer
        ).status_code
        == 201
    )
    assert (
        client.get(
            f"/api/v1/predictions/{prediction}/reviews", headers=reviewer
        ).status_code
        == 200
    )
    events = client.get("/api/v1/audit-events", headers=reviewer).json()["data"][
        "items"
    ]
    assert {x["event_type"] for x in events} == {"prediction_created", "review_created"}
    for event in events:
        assert (
            client.get(
                "/api/v1/audit-events/" + event["id"], headers=reviewer
            ).status_code
            == 200
        )
    admin = {
        "Authorization": "Bearer "
        + token(sub="synthetic-admin", roles=["administrator"])
    }
    assert client.get("/api/v1/admin/model-versions", headers=admin).status_code == 200
    assert (
        client.get("/api/v1/admin/model-versions/1", headers=admin).status_code == 200
    )
    assert (
        client.get("/api/v1/admin/model-versions", headers=headers).status_code == 403
    )
    system_events = client.get("/api/v1/audit-events", headers=admin).json()["data"][
        "items"
    ]
    system = next(
        x for x in system_events if x["event_type"] == "initial_administrator_bootstrap"
    )
    assert (
        client.get("/api/v1/audit-events/" + system["id"], headers=reviewer).status_code
        == 404
    )
    assert client.get("/api/v1/audit-events").status_code == 401
    assert (
        client.post(
            "/api/v1/predictions",
            json=dict(BODY, patient_name="DO_NOT_LOG_THIS_PATIENT"),
            headers=headers,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/predictions",
            content="X" * 4097,
            headers=dict(headers, **{"Content-Type": "application/json"}),
        ).status_code
        == 413
    )
    assert (
        client.post("/api/v1/predictions", content="file", headers=headers).status_code
        == 415
    )
    bad = client.get("/api/v1/predictions/not-uuid", headers=headers)
    assert bad.status_code == 400 and "error" in bad.json()
    assert "DO_NOT_LOG_THIS_PATIENT" not in caplog.text and token() not in caplog.text
    assert not any(
        "Authorization" in r.__dict__ or "sub" in r.__dict__ for r in caplog.records
    )


def test_ambiguous_commit_retry_and_dependency_failure(
    prepared, release, settings, tokens, monkeypatch
):
    owner, runtime, admin, _, _ = prepared
    token, verifier, _, _ = tokens
    client = TestClient(create_app(settings, release, runtime, verifier))
    headers = {
        "Authorization": "Bearer " + token(),
        "Idempotency-Key": str(uuid.uuid4()),
    }
    original = runtime.command

    def uncertain(*args, **kwargs):
        original(*args, **kwargs)
        raise SQLAlchemyError("simulated lost commit acknowledgement")

    monkeypatch.setattr(runtime, "command", uncertain)
    assert (
        client.post("/api/v1/predictions", json=BODY, headers=headers).status_code
        == 503
    )
    monkeypatch.setattr(runtime, "command", original)
    assert (
        client.post("/api/v1/predictions", json=BODY, headers=headers).status_code
        == 201
    )
    with runtime.engine.begin() as conn:
        assert (
            conn.execute(sa.select(sa.func.count()).select_from(s.predictions)).scalar()
            == 1
        )
        assert (
            conn.execute(sa.select(sa.func.count()).select_from(s.keys)).scalar() == 1
        )
    owner.release_action(admin, "1", release.digest, "revoked")
    assert client.get("/api/v1/health/ready").status_code == 503
    assert client.get("/api/v1/explanations/global").status_code == 200
    assert (
        client.post("/api/v1/predictions", json=BODY, headers=headers).status_code
        == 503
    )


def test_bootstrap_concurrency_and_permanent_marker(db):
    owner, _ = db

    def attempt():
        try:
            return owner.bootstrap(ISSUER, "synthetic-admin")
        except ServiceError as exc:
            return exc.status

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: attempt(), range(2)))
    assert sum(isinstance(x, uuid.UUID) for x in results) == 1 and 409 in results
    identity = Identity(ISSUER, "synthetic-admin", frozenset({"administrator"}))
    owner.grant(identity, ISSUER, "replacement-admin", "administrator")
    replacement = Identity(ISSUER, "replacement-admin", frozenset({"administrator"}))
    owner.revoke_role(replacement, ISSUER, "synthetic-admin", "administrator")
    with pytest.raises(ServiceError) as exc:
        owner.bootstrap(ISSUER, "synthetic-admin")
    assert exc.value.status == 409


def test_bootstrap_migration_and_conflicting_subject(db):
    owner, _ = db
    with owner.engine.begin() as conn:
        conn.execute(sa.text("UPDATE alembic_version SET version_num='0001_backend'"))
    with pytest.raises(ServiceError) as exc:
        owner.bootstrap(ISSUER, "synthetic-admin")
    assert exc.value.status == 503
    with owner.engine.begin() as conn:
        conn.execute(sa.text("UPDATE alembic_version SET version_num='0003_integrity'"))
        conn.execute(
            s.subjects.insert().values(issuer=ISSUER, sub="conflicting-subject")
        )
    with pytest.raises(ServiceError) as exc:
        owner.bootstrap(ISSUER, "synthetic-admin")
    assert exc.value.status == 409


def test_historical_migrations_are_self_contained(monkeypatch):
    import ast
    import builtins
    import runpy
    from pathlib import Path

    importing = builtins.__import__

    def guarded(name, *args, **kwargs):
        if name.startswith("aletheia"):
            raise AssertionError("historical migration imported live application code")
        return importing(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    for path in sorted(Path("migrations/versions").glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("aletheia")
            if isinstance(node, ast.Import):
                assert not any(
                    alias.name.startswith("aletheia") for alias in node.names
                )
            if isinstance(node, ast.Attribute):
                assert node.attr != "create_all"
        revision = runpy.run_path(str(path))
        with pytest.raises(RuntimeError, match="destructive downgrade refused"):
            revision["downgrade"]()


# Captured from the pre-repair PostgreSQL 18 Stage 1 contract. This includes
# columns/defaults, constraint definitions, indexes, triggers/functions, privileges,
# sequence properties, seed rows and head role timeouts; no live metadata oracle.
MIGRATION_CATALOG_QUERIES = {
    "columns": """SELECT c.relname,a.attname,format_type(a.atttypid,a.atttypmod),
        a.attnotnull,pg_get_expr(d.adbin,d.adrelid)
        FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        JOIN pg_attribute a ON a.attrelid=c.oid
        LEFT JOIN pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum
        WHERE n.nspname='public' AND c.relkind='r' AND c.relname<>'alembic_version'
        AND a.attnum>0 AND NOT a.attisdropped ORDER BY c.relname,a.attnum""",
    "constraints": """SELECT r.relname,c.contype,pg_get_constraintdef(c.oid)
        FROM pg_constraint c JOIN pg_class r ON r.oid=c.conrelid
        JOIN pg_namespace n ON n.oid=r.relnamespace
        WHERE n.nspname='public' AND r.relname<>'alembic_version'
        ORDER BY r.relname,c.contype,pg_get_constraintdef(c.oid)""",
    "indexes": """SELECT tablename,indexname,indexdef FROM pg_indexes
        WHERE schemaname='public' AND tablename<>'alembic_version'
        ORDER BY tablename,indexname""",
    "triggers": """SELECT c.relname,t.tgname,pg_get_triggerdef(t.oid)
        FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid
        JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='public' AND NOT t.tgisinternal ORDER BY c.relname,t.tgname""",
    "functions": """SELECT p.proname,pg_get_functiondef(p.oid)
        FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
        WHERE n.nspname='public' ORDER BY p.proname""",
    "table_privileges": """SELECT table_name,privilege_type,is_grantable
        FROM information_schema.role_table_grants WHERE grantee='aletheia_runtime'
        AND table_schema='public' ORDER BY table_name,privilege_type""",
    "column_privileges": """SELECT table_name,column_name,privilege_type,is_grantable
        FROM information_schema.role_column_grants WHERE grantee='aletheia_runtime'
        AND table_schema='public' ORDER BY table_name,column_name,privilege_type""",
    "schema_privileges": "SELECT nspacl::text FROM pg_namespace WHERE nspname='public'",
    "sequences": """SELECT c.relname,s.seqtypid::regtype::text,s.seqstart,
        s.seqincrement,s.seqmax,s.seqmin,s.seqcache,s.seqcycle FROM pg_sequence s
        JOIN pg_class c ON c.oid=s.seqrelid JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='public' ORDER BY c.relname""",
    "roles": "SELECT code FROM roles ORDER BY code",
    "heads": "SELECT chain_id,last_sequence,last_hash FROM audit_chain_heads",
}


def migration_catalog(conn, head):
    queries = dict(MIGRATION_CATALOG_QUERIES)
    if head:
        queries["deployment"] = (
            "SELECT singleton,active_model_id,release_event_id,published "
            "FROM deployment_state"
        )
        queries["timeouts"] = (
            "SELECT rolconfig FROM pg_roles WHERE rolname='aletheia_runtime'"
        )
    return {
        name: [list(row) for row in conn.execute(sa.text(sql))]
        for name, sql in queries.items()
    }


def catalog_digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@pytest.mark.parametrize(
    "stepped", [False, True], ids=["empty-to-head", "0001-to-head"]
)
def test_migrations_reproduce_frozen_contract_with_changed_live_schema(
    monkeypatch, stepped
):
    import os

    from alembic import command
    from alembic.config import Config

    admin_url = os.environ.get("ALETHEIA_TEST_PG_ADMIN_URL")
    if not admin_url:
        pytest.skip("real disposable PostgreSQL URL required")
    admin = sa.create_engine(admin_url, isolation_level="AUTOCOMMIT")
    name = "aletheia_test_migration_" + uuid.uuid4().hex
    url = (
        sa.engine.make_url(admin_url)
        .set(database=name)
        .render_as_string(hide_password=False)
    )
    with admin.connect() as conn:
        conn.execute(sa.text(f'CREATE DATABASE "{name}"'))
    engine = sa.create_engine(url)
    try:
        monkeypatch.setenv("ALETHEIA_MIGRATION_URL", url)
        # Simulate a future application refactor without touching the source file.
        monkeypatch.setattr(s, "metadata", sa.MetaData())
        for attribute in ("heads", "roles", "deployment", "IMMUTABLE"):
            monkeypatch.setattr(s, attribute, None)
        config = Config("alembic.ini")
        if stepped:
            command.upgrade(config, "0001_backend")
            with engine.connect() as conn:
                assert catalog_digest(migration_catalog(conn, False)) == (
                    "d07c4c3d4a7ea9ad7679c5e7eec7a96d7085733e1147124fb2b198afd5cc5578"
                )
                assert (
                    conn.execute(
                        sa.text("SELECT to_regclass('public.deployment_state')")
                    ).scalar()
                    is None
                )
        command.upgrade(config, "head")
        with engine.connect() as conn:
            assert (
                conn.execute(
                    sa.text("SELECT version_num FROM alembic_version")
                ).scalar()
                == "0003_integrity"
            )
            assert (
                catalog_digest(migration_catalog(conn, True))
                == "e795a550f0ce7c5b63a9c7a5cb841beba725df3107fa7618d99e7e89d3b93ddf"
            )
    finally:
        engine.dispose()
        with admin.connect() as conn:
            conn.execute(sa.text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        admin.dispose()
