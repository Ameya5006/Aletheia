"""Real PostgreSQL transactions, RBAC and immutable reruns through HTTP."""

import copy
import time
import uuid

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from aletheia.application import schema as s
from aletheia.application.api import create_app
from aletheia.application.auth import ServiceError
from aletheia.application.store import audit, verify_chain
from tests.application.test_case_input import values


def client_for(prepared, release, settings, tokens):
    _, runtime, _, _, _ = prepared
    token, verifier, _, _ = tokens
    client = TestClient(create_app(settings, release, runtime, verifier))
    return client, token


def headers(token, role="engineer", key=None):
    return {
        "Authorization": "Bearer " + token(sub="synthetic-" + role, roles=[role]),
        "Idempotency-Key": str(key or uuid.uuid4()),
    }


def test_run_save_open_rerun_and_review(prepared, release, settings, tokens, caplog):
    client, token = client_for(prepared, release, settings, tokens)
    body = {
        "schema_version": "case-input-v1",
        "model_version": "1",
        "inputs": values(release),
    }
    caplog.set_level("INFO", logger="aletheia.http")
    key = uuid.uuid4()
    first = client.post("/api/v1/analyses", json=body, headers=headers(token, key=key))
    assert first.status_code == 201, first.text
    original = first.json()["data"]
    pid = original["prediction_id"]
    assert not original["saved"] and original["review_history"] == []
    assert original["model_sha256"] == release.protocol["identity"]["model_sha256"]
    assert original["release_sha256"] == release.digest
    assert (
        original["evidence_sha256"]
        == release.manifest["files"]["artifacts/healthcare-audit-v1/results.json"]
    )
    assert (
        client.post(
            "/api/v1/analyses", json=body, headers=headers(token, key=key)
        ).json()["data"]
        == original
    )
    assert (
        client.get("/api/v1/analyses", headers=headers(token)).json()["data"]["items"]
        == []
    )
    saved = client.post(f"/api/v1/analyses/{pid}/save", json={}, headers=headers(token))
    assert saved.status_code == 200, saved.text
    saved = saved.json()["data"]
    assert saved["saved"] and saved["save_event_id"] != saved["event_id"]
    assert (
        client.post(
            f"/api/v1/analyses/{pid}/save", json={}, headers=headers(token)
        ).json()["data"]
        == saved
    )
    assert (
        client.get(f"/api/v1/analyses/{pid}", headers=headers(token)).json()["data"]
        == saved
    )
    assert client.get("/api/v1/analyses", headers=headers(token)).json()["data"][
        "items"
    ] == [saved]
    second_body = copy.deepcopy(body)
    second_body["inputs"]["number_inpatient"] = 4
    rerun = client.post(
        "/api/v1/analyses", json=second_body, headers=headers(token)
    ).json()["data"]
    assert rerun["prediction_id"] != pid and rerun["event_id"] != saved["event_id"]
    assert (
        client.get(f"/api/v1/analyses/{pid}", headers=headers(token)).json()["data"]
        == saved
    )
    review = client.post(
        f"/api/v1/predictions/{pid}/reviews",
        headers=headers(token, "reviewer"),
        json={
            "schema_version": "application-v1",
            "decision": "acknowledged",
            "reason_code": "evidence_reviewed",
            "expected_revision": 0,
        },
    )
    assert review.status_code == 201, review.text
    opened = client.get(f"/api/v1/analyses/{pid}", headers=headers(token)).json()[
        "data"
    ]
    assert (
        opened["review_state"] == "acknowledged" and len(opened["review_history"]) == 1
    )
    for k in (
        "inputs",
        "probability",
        "explanation",
        "stability",
        "release_sha256",
        "created_at",
        "event_id",
    ):
        assert opened[k] == original[k]
    _, runtime, _, _, _ = prepared
    with runtime.engine.begin() as conn:
        events = list(
            conn.execute(sa.select(s.events).order_by(s.events.c.sequence)).mappings()
        )
        verify_chain(events)
        assert all("inputs" not in e["payload"] for e in events)
    assert "Bearer" not in caplog.text and "num_medications" not in caplog.text
    for table in (s.predictions, s.saved):
        with pytest.raises(SQLAlchemyError), runtime.engine.begin() as conn:
            conn.execute(table.delete())


def test_intake_api_and_authorization(prepared, release, settings, tokens):
    client, token = client_for(prepared, release, settings, tokens)
    body = {
        "schema_version": "case-input-v1",
        "model_version": "1",
        "inputs": values(release),
    }
    assert client.post("/api/v1/analyses", json=body).status_code == 401
    expired = token(iat=int(time.time()) - 500, exp=int(time.time()) - 100)
    assert (
        client.get(
            "/api/v1/analyses", headers={"Authorization": "Bearer " + expired}
        ).status_code
        == 401
    )
    for mutation in (
        {"name": "never logged"},
        {"num_procedures": -1},
        {"diabetesMed": "maybe"},
    ):
        invalid = dict(body, inputs=dict(body["inputs"], **mutation))
        assert (
            client.post(
                "/api/v1/analyses", json=invalid, headers=headers(token)
            ).status_code
            == 422
        )
    for role in ("engineer", "reviewer", "admin"):
        effective = "administrator" if role == "admin" else role
        h = headers(token, effective)
        if role == "admin":
            h["Authorization"] = "Bearer " + token(
                sub="synthetic-admin", roles=[effective]
            )
        created = client.post("/api/v1/analyses", json=body, headers=h)
        assert created.status_code == 201, created.text
    own = client.post("/api/v1/analyses", json=body, headers=headers(token)).json()[
        "data"
    ]
    pid = own["prediction_id"]
    client.post(f"/api/v1/analyses/{pid}/save", json={}, headers=headers(token))
    other = {"Authorization": "Bearer " + token(sub="synthetic-other")}
    assert client.get(f"/api/v1/analyses/{pid}", headers=other).status_code == 404
    assert client.get("/api/v1/analyses", headers=other).json()["data"]["items"] == []
    assert (
        client.post(
            f"/api/v1/analyses/{pid}/save", json={}, headers=headers(token, "reviewer")
        ).status_code
        == 403
    )
    assert (
        client.get(
            f"/api/v1/analyses/{pid}", headers=headers(token, "reviewer")
        ).status_code
        == 200
    )
    assert (
        client.get("/api/v1/analyses/schema", headers=headers(token)).json()["data"][
            "schema_version"
        ]
        == "case-input-v1"
    )
    assert (
        "AnalysisRequest" in client.get("/openapi.json").json()["components"]["schemas"]
    )


def test_audit_rollback_and_model_failure(
    prepared, release, settings, tokens, monkeypatch
):
    client, token = client_for(prepared, release, settings, tokens)
    body = {
        "schema_version": "case-input-v1",
        "model_version": "1",
        "inputs": values(release),
    }
    import aletheia.application.store as module

    def fail(*args, **kwargs):
        raise ServiceError(503, "injected_audit_failure")

    with monkeypatch.context() as patch:
        patch.setattr(module, "audit", fail)
        assert (
            client.post(
                "/api/v1/analyses", json=body, headers=headers(token)
            ).status_code
            == 503
        )
    _, runtime, _, _, _ = prepared
    with runtime.engine.begin() as conn:
        assert (
            conn.execute(sa.select(sa.func.count()).select_from(s.predictions)).scalar()
            == 0
        )
    with monkeypatch.context() as patch:
        patch.setattr(runtime, "approved", fail)
        assert (
            client.post(
                "/api/v1/analyses", json=body, headers=headers(token)
            ).status_code
            == 503
        )
    with pytest.raises(SQLAlchemyError), runtime.engine.begin() as conn:
        audit(conn, prepared[3], "prediction_saved", uuid.uuid4(), uuid.uuid4(), {})


def test_local_session_and_save_contract(prepared, release, settings, tokens):
    _, runtime, _, _, _ = prepared
    token, verifier, _, _ = tokens
    disabled = TestClient(create_app(settings, release, runtime, verifier))
    assert disabled.get("/api/v1/session", headers=headers(token)).status_code == 404
    local = TestClient(
        create_app(
            settings.model_copy(update={"development_identity": True}),
            release,
            runtime,
            verifier,
        )
    )
    assert local.get("/api/v1/session").status_code == 401
    h = {"Authorization": "Bearer " + token(roles=["engineer", "administrator"])}
    assert local.get("/api/v1/session", headers=h).json()["data"] == {
        "roles": ["engineer"]
    }
    body = {
        "schema_version": "case-input-v1",
        "model_version": "1",
        "inputs": values(release),
    }
    result = local.post("/api/v1/analyses", json=body, headers=headers(token)).json()[
        "data"
    ]
    assert (
        local.post(
            "/api/v1/analyses/" + result["prediction_id"] + "/save",
            json={"name": "forbidden"},
            headers=headers(token),
        ).status_code
        == 422
    )


def test_forward_migration_preserves_legacy_record(release, monkeypatch, tmp_path):
    import os

    from alembic import command
    from alembic.config import Config

    import aletheia.application.store as module
    from aletheia.application.auth import Identity

    admin_url = os.environ.get("ALETHEIA_TEST_PG_ADMIN_URL")
    if not admin_url:
        pytest.skip("real disposable PostgreSQL URL required")
    database = "aletheia_forward_" + uuid.uuid4().hex
    admin_engine = sa.create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(sa.text(f'CREATE DATABASE "{database}"'))
    url = (
        sa.engine.make_url(admin_url)
        .set(database=database)
        .render_as_string(hide_password=False)
    )
    owner = module.Store(url, tmp_path / "pin.json")
    monkeypatch.setenv("ALETHEIA_MIGRATION_URL", url)
    try:
        command.upgrade(Config("alembic.ini"), "0003_integrity")
        with monkeypatch.context() as patch:
            patch.setattr(module, "HEAD", "0003_integrity")
            actor = owner.bootstrap("https://identity.example.test", "legacy-admin")
        identity = Identity(
            "https://identity.example.test",
            "legacy-admin",
            frozenset({"administrator"}),
        )
        mid = owner.register(
            identity,
            release,
            {
                "name": "aletheia-healthcare-readmission",
                "version": "1",
                "run_id": "legacy-migration-fixture",
                "package_sha256": "a" * 64,
            },
        )
        pid = uuid.uuid4()
        score = release.score()
        with owner.engine.begin() as conn:
            ref = conn.execute(
                sa.select(s.explanations.c.id).where(
                    s.explanations.c.model_version_id == mid,
                    s.explanations.c.kind == "synthetic_local",
                )
            ).scalar_one()
            eid = audit(
                conn,
                actor,
                "prediction_created",
                pid,
                uuid.uuid4(),
                {
                    "case_id": "synthetic-discharge-v1",
                    "probability": format(score, ".17g"),
                    "model_version": "1",
                },
            )
            conn.execute(
                sa.text("""INSERT INTO prediction_events
                (id,actor_id,model_version_id,case_id,input_sha256,probability,
                 threshold,class_at_threshold,explanation_ref_id,audit_event_id)
                VALUES (:pid,:actor,:mid,'synthetic-discharge-v1',
                        :hash,:score,0.5,0,:ref,:eid)"""),
                {
                    "pid": pid,
                    "actor": actor,
                    "mid": mid,
                    "hash": "a" * 64,
                    "score": score,
                    "ref": ref,
                    "eid": eid,
                },
            )
        command.upgrade(Config("alembic.ini"), "head")
        with owner.engine.begin() as conn:
            stored = owner.accessible(conn, identity, pid)
            assert stored["probability"] == score and stored["audit_event_id"] == eid
            assert stored["inputs"] is None and stored["result_snapshot"] is None
            assert owner.migrated(conn)
    finally:
        owner.engine.dispose()
        with admin_engine.connect() as conn:
            conn.execute(sa.text(f'DROP DATABASE "{database}" WITH (FORCE)'))
        admin_engine.dispose()
