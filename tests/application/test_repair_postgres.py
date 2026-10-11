"""Real PostgreSQL repair proofs, with publication faults at external boundaries."""

import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import mlflow
import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from mlflow.protos.databricks_pb2 import RESOURCE_DOES_NOT_EXIST
from sqlalchemy.exc import SQLAlchemyError

from aletheia.application import schema as s
from aletheia.application.api import create_app
from aletheia.application.auth import Identity, ServiceError
from aletheia.application.registry import NAME, Registry
from aletheia.application.store import audit, verify_chain
from tests.application.test_postgres_api import (
    BODY,
    ENGINEER,
    ISSUER,
    REVIEWER,
    predict,
)


class FakeRegistryClient:
    """Only publication SDK boundaries are simulated; transactions use PostgreSQL."""

    def __init__(self, identity):
        self.models = {
            identity["version"]: SimpleNamespace(
                version=identity["version"],
                tags={"import_state": "verified", "approval_status": "candidate"},
            )
        }
        self.aliases = {}

    def set_model_version_tag(self, name, version, key, value):
        self.models[str(version)].tags[key] = value

    def get_model_version(self, name, version):
        return self.models[str(version)]

    def search_model_versions(self, query):
        return list(self.models.values())

    def get_registered_model(self, name):
        return SimpleNamespace(aliases=dict(self.aliases))

    def set_registered_model_alias(self, name, alias, version):
        self.aliases[alias] = str(version)

    def delete_registered_model_alias(self, name, alias):
        self.aliases.pop(alias, None)

    def get_model_version_by_alias(self, name, alias):
        if alias not in self.aliases:
            raise mlflow.exceptions.MlflowException("absent", RESOURCE_DOES_NOT_EXIST)
        return self.models[self.aliases[alias]]


@pytest.fixture
def publishing(db, release, tmp_path, monkeypatch):
    owner, runtime = db
    owner.bootstrap(ISSUER, "synthetic-admin")
    admin = Identity(ISSUER, "synthetic-admin", frozenset({"administrator"}))
    identity = {
        "name": NAME,
        "version": "1",
        "run_id": "synthetic-run",
        "package_sha256": "a" * 64,
        "release_sha256": release.digest,
    }
    registry = Registry("http://127.0.0.1:5000", tmp_path / "receipts")
    registry.client = FakeRegistryClient(identity)
    monkeypatch.setattr(registry, "download_verified", lambda *args: identity)
    return owner, runtime, admin, registry, identity


def counts(store):
    with store.engine.begin() as conn:
        return tuple(
            conn.execute(sa.select(sa.func.count()).select_from(t)).scalar_one()
            for t in (s.models, s.releases, s.events)
        )


def fail_once_after(monkeypatch, target, method, predicate=lambda args: True):
    original = getattr(target, method)
    fired = False

    def failing(*args, **kwargs):
        nonlocal fired
        result = original(*args, **kwargs)
        if not fired and predicate(args):
            fired = True
            raise RuntimeError("simulated lost acknowledgement")
        return result

    monkeypatch.setattr(target, method, failing)


@pytest.mark.parametrize(
    "boundary", ["postgres_commit", "status_tag", "event_tag", "alias"]
)
def test_approval_retry_converges_without_duplicate_rows(
    publishing, release, monkeypatch, boundary
):
    owner, _, admin, registry, identity = publishing
    if boundary == "postgres_commit":
        fail_once_after(monkeypatch, owner, "register")
    elif boundary == "alias":
        fail_once_after(monkeypatch, registry.client, "set_registered_model_alias")
    else:
        key = "approval_status" if boundary == "status_tag" else "approver_event_id"
        fail_once_after(
            monkeypatch,
            registry.client,
            "set_model_version_tag",
            lambda args: args[2] == key,
        )
    with pytest.raises(RuntimeError):
        registry.publish_approval(owner, admin, release, identity)
    after = counts(owner)
    assert registry.publish_approval(owner, admin, release, identity) == identity
    assert counts(owner) == after == (1, 1, 2)
    with owner.engine.begin() as conn, pytest.raises(ServiceError):
        owner.approved(conn, "1", release.digest)


def test_registration_identity_and_concurrent_retries(publishing, release):
    owner, _, admin, _, identity = publishing
    with ThreadPoolExecutor(max_workers=3) as pool:
        mids = list(
            pool.map(lambda _: owner.register(admin, release, identity), range(3))
        )
    assert len(set(mids)) == 1 and counts(owner) == (1, 1, 2)
    for field in ("name", "version", "run_id", "package_sha256"):
        changed = dict(identity, **{field: "2" if field == "version" else "b" * 64})
        with pytest.raises(ServiceError) as exc:
            owner.register(admin, release, changed)
        assert exc.value.status == 409
    assert counts(owner) == (1, 1, 2)


@pytest.mark.parametrize("action", ["activated", "rolled_back", "revoked"])
@pytest.mark.parametrize(
    "boundary",
    [
        "postgres_commit",
        "status_tag",
        "event_tag",
        "active_tag",
        "alias",
        "pin",
        "finish_before",
        "finish_after",
    ],
)
def test_lifecycle_faults_retry_same_event_and_fail_closed(
    publishing, release, monkeypatch, action, boundary
):
    import aletheia.application.registry as module

    owner, runtime, admin, registry, identity = publishing
    registry.publish_approval(owner, admin, release, identity)
    if action != "activated":
        registry.publish_lifecycle(owner, admin, release, identity, "activated")
    if boundary == "postgres_commit":
        fail_once_after(monkeypatch, owner, "release_action")
    elif boundary in {"status_tag", "event_tag", "active_tag"}:
        key = {
            "status_tag": "approval_status",
            "event_tag": "release_event_id",
            "active_tag": "deployment_status",
        }[boundary]
        fail_once_after(
            monkeypatch,
            registry.client,
            "set_model_version_tag",
            lambda args: args[2] == key,
        )
    elif boundary == "alias":
        fail_once_after(
            monkeypatch,
            registry.client,
            "delete_registered_model_alias"
            if action == "revoked"
            else "set_registered_model_alias",
        )
    elif boundary == "pin":
        fail_once_after(monkeypatch, module, "durable_json")
    elif boundary == "finish_after":
        fail_once_after(monkeypatch, owner, "finish_publication")
    else:
        original = owner.finish_publication

        def failed(*args):
            monkeypatch.setattr(owner, "finish_publication", original)
            raise RuntimeError("before final commit")

        monkeypatch.setattr(owner, "finish_publication", failed)
    with pytest.raises(RuntimeError):
        registry.publish_lifecycle(owner, admin, release, identity, action)
    after = counts(owner)
    if boundary != "finish_after" or action == "revoked":
        with runtime.engine.begin() as conn, pytest.raises(ServiceError):
            runtime.approved(conn, "1", release.digest)
    pin = registry.publish_lifecycle(owner, admin, release, identity, action)
    assert counts(owner) == after
    assert pin["action"] == action
    with runtime.engine.begin() as conn:
        if action == "revoked":
            with pytest.raises(ServiceError):
                runtime.approved(conn, "1", release.digest)
        else:
            assert runtime.approved(conn, "1", release.digest)["version"] == "1"
        events = list(
            conn.execute(sa.select(s.events).order_by(s.events.c.sequence)).mappings()
        )
        verify_chain(events)


@pytest.mark.parametrize("kind", ["prediction_created", "review_created"])
def test_runtime_cannot_commit_orphan_business_audit(prepared, kind):
    _, runtime, _, engineer_id, _ = prepared
    before = counts(runtime)
    with (
        pytest.raises(SQLAlchemyError, match="reverse business audit mismatch"),
        runtime.engine.begin() as conn,
    ):
        audit(conn, engineer_id, kind, uuid.uuid4(), uuid.uuid4(), {})
    assert counts(runtime) == before


@pytest.mark.parametrize(
    "mismatch", ["resource", "actor", "probability", "case", "version"]
)
def test_runtime_cannot_commit_mismatched_prediction_audit(prepared, release, mismatch):
    _, runtime, _, _, reviewer_id = prepared
    prediction = predict(runtime, release)
    changed = dict(prediction, id=uuid.uuid4())
    payload = {
        "case_id": changed["case_id"],
        "probability": format(changed["probability"], ".17g"),
        "model_version": "1",
    }
    actor, resource = changed["actor_id"], changed["id"]
    if mismatch == "resource":
        resource = uuid.uuid4()
    elif mismatch == "actor":
        actor = reviewer_id
    else:
        payload[
            {
                "probability": "probability",
                "case": "case_id",
                "version": "model_version",
            }[mismatch]
        ] = "0.99" if mismatch == "probability" else "other"
    with pytest.raises(SQLAlchemyError), runtime.engine.begin() as conn:
        changed["audit_event_id"] = audit(
            conn, actor, "prediction_created", resource, uuid.uuid4(), payload
        )
        conn.execute(s.predictions.insert().values(**changed))


def test_timeout_response_has_no_late_commit(
    prepared, release, settings, tokens, monkeypatch
):
    _, runtime, _, _, _ = prepared
    token, verifier, _, _ = tokens
    client = TestClient(
        create_app(
            settings.model_copy(update={"operation_timeout_seconds": 0.05}),
            release,
            runtime,
            verifier,
        )
    )
    original = release.score

    def slow():
        time.sleep(0.15)
        return original()

    monkeypatch.setattr(release, "score", slow)
    response = client.post(
        "/api/v1/predictions",
        json=BODY,
        headers={
            "Authorization": "Bearer " + token(),
            "Idempotency-Key": str(uuid.uuid4()),
        },
    )
    assert response.status_code == 504
    time.sleep(0.3)
    with runtime.engine.begin() as conn:
        for table in (s.predictions, s.keys):
            assert (
                conn.execute(sa.select(sa.func.count()).select_from(table)).scalar_one()
                == 0
            )
        assert (
            conn.execute(
                sa.select(sa.func.count())
                .select_from(s.events)
                .where(s.events.c.event_type == "prediction_created")
            ).scalar_one()
            == 0
        )


def test_role_revocation_and_disable_are_authorized_audited_and_immediate(
    prepared, release
):
    owner, runtime, admin, _, _ = prepared
    with pytest.raises(ServiceError):
        owner.revoke_role(ENGINEER, ISSUER, "synthetic-reviewer", "reviewer")
    with pytest.raises(ServiceError):
        owner.disable_subject(ENGINEER, ISSUER, "synthetic-reviewer")
    for method in (
        lambda: owner.revoke_role(admin, ISSUER, "synthetic-admin", "administrator"),
        lambda: owner.disable_subject(admin, ISSUER, "synthetic-admin"),
    ):
        with pytest.raises(ServiceError) as exc:
            method()
        assert exc.value.status == 409
    owner.revoke_role(admin, ISSUER, "synthetic-engineer", "engineer")
    with pytest.raises(ServiceError):
        predict(runtime, release)
    with pytest.raises(ServiceError):
        owner.revoke_role(admin, ISSUER, "synthetic-engineer", "engineer")
    owner.disable_subject(admin, ISSUER, "synthetic-reviewer")
    with pytest.raises(ServiceError):
        owner.disable_subject(admin, ISSUER, "synthetic-reviewer")
    with owner.engine.begin() as conn:
        events = list(
            conn.execute(sa.select(s.events).order_by(s.events.c.sequence)).mappings()
        )
        assert [e["event_type"] for e in events[-2:]] == [
            "role_revoked",
            "subject_disabled",
        ]
        verify_chain(events)


def test_disable_during_inference_is_rechecked_before_commit(
    prepared, release, monkeypatch
):
    owner, runtime, admin, _, _ = prepared
    original = release.score

    def disable():
        owner.disable_subject(admin, ISSUER, "synthetic-engineer")
        return original()

    monkeypatch.setattr(release, "score", disable)
    with pytest.raises(ServiceError) as exc:
        predict(runtime, release)
    assert exc.value.status == 403
    with runtime.engine.begin() as conn:
        assert (
            conn.execute(
                sa.select(sa.func.count()).select_from(s.predictions)
            ).scalar_one()
            == 0
        )


@pytest.mark.parametrize(
    "mismatch", ["resource", "actor", "prediction", "revision", "decision", "reason"]
)
def test_runtime_cannot_commit_mismatched_review_audit(prepared, release, mismatch):
    _, runtime, _, engineer_id, _ = prepared
    prediction = predict(runtime, release)
    body = {
        "schema_version": "application-v1",
        "decision": "acknowledged",
        "reason_code": "evidence_reviewed",
        "expected_revision": 0,
    }
    review = runtime.command(
        REVIEWER, body, uuid.uuid4(), uuid.uuid4(), "1", release, prediction["id"]
    )
    changed = dict(review, id=uuid.uuid4(), revision=2)
    payload = {
        "prediction_id": str(prediction["id"]),
        "revision": 2,
        "decision": review["decision"],
        "reason_code": review["reason_code"],
    }
    actor, resource = changed["reviewer_id"], changed["id"]
    if mismatch == "resource":
        resource = uuid.uuid4()
    elif mismatch == "actor":
        actor = engineer_id
    else:
        field, value = {
            "prediction": ("prediction_id", str(uuid.uuid4())),
            "revision": ("revision", 3),
            "decision": ("decision", "dismissed_demo"),
            "reason": ("reason_code", "identity_issue"),
        }[mismatch]
        payload[field] = value
    with pytest.raises(SQLAlchemyError), runtime.engine.begin() as conn:
        changed["audit_event_id"] = audit(
            conn, actor, "review_created", resource, uuid.uuid4(), payload
        )
        conn.execute(s.reviews.insert().values(**changed))


def test_multiversion_rollback_reconciles_previous_alias_and_single_pin(
    publishing, release, monkeypatch
):
    owner, runtime, admin, registry, identity = publishing
    other = SimpleNamespace(
        digest="b" * 64, manifest=release.manifest, protocol=release.protocol
    )
    second = dict(
        identity,
        version="2",
        run_id="synthetic-second-run",
        release_sha256=other.digest,
        package_sha256="c" * 64,
    )
    registry.client.models["2"] = SimpleNamespace(
        version="2", tags={"import_state": "verified", "approval_status": "candidate"}
    )
    monkeypatch.setattr(
        registry,
        "download_verified",
        lambda version, *args: identity if version == "1" else second,
    )
    registry.publish_approval(owner, admin, release, identity)
    registry.publish_lifecycle(owner, admin, release, identity, "activated")
    registry.publish_approval(owner, admin, other, second)
    # A registry alias grants no serving authority to the unactivated second model.
    with runtime.engine.begin() as conn, pytest.raises(ServiceError):
        runtime.approved(conn, "2", other.digest)
    registry.publish_lifecycle(owner, admin, other, second, "activated")
    assert registry.client.aliases == {"approved": "2", "previous": "1"}
    with runtime.engine.begin() as conn, pytest.raises(ServiceError):
        runtime.approved(conn, "1", release.digest)
    fail_once_after(
        monkeypatch,
        registry.client,
        "set_registered_model_alias",
        lambda args: args[1] == "previous",
    )
    with pytest.raises(RuntimeError):
        registry.publish_lifecycle(owner, admin, release, identity, "rolled_back")
    after = counts(owner)
    for version, digest in (("1", release.digest), ("2", other.digest)):
        with runtime.engine.begin() as conn, pytest.raises(ServiceError):
            runtime.approved(conn, version, digest)
    registry.publish_lifecycle(owner, admin, release, identity, "rolled_back")
    assert counts(owner) == after
    assert registry.client.aliases == {"approved": "1", "previous": "2"}
    assert [
        v.version
        for v in registry.client.models.values()
        if v.tags.get("deployment_status") == "active"
    ] == ["1"]
    with runtime.engine.begin() as conn:
        runtime.approved(conn, "1", release.digest)
    registry.client.aliases["previous"] = "1"
    with pytest.raises(ValueError, match="previous alias"):
        registry.reconcile_lifecycle(owner, release, identity)
    registry.client.aliases["previous"] = "2"
    owner.pin_path.write_text("{}")
    with runtime.engine.begin() as conn, pytest.raises(ServiceError):
        runtime.approved(conn, "1", release.digest)


@pytest.mark.parametrize("command", ["revoke-role", "disable-subject"])
def test_operator_commands_require_admin_and_remove_access_immediately(
    prepared, release, settings, tokens, monkeypatch, tmp_path, command
):
    import sys

    from aletheia.application import operator

    owner, runtime, _, _, _ = prepared
    token, verifier, _, _ = tokens
    token_path = tmp_path / "operator-token"
    monkeypatch.setattr(operator.Settings, "from_env", lambda: settings)
    monkeypatch.setattr(operator, "Store", lambda *args: owner)
    monkeypatch.setattr(operator, "TokenVerifier", lambda *args: verifier)
    args = [
        "aletheia-admin",
        command,
        "--token-file",
        str(token_path),
        "--issuer",
        ISSUER,
        "--subject",
        "synthetic-engineer",
    ]
    if command == "revoke-role":
        args += ["--role", "engineer"]
    monkeypatch.setattr(sys, "argv", args)
    token_path.write_text(token())
    with pytest.raises(ServiceError) as exc:
        operator.main()
    assert exc.value.status == 403
    token_path.write_text(token(sub="synthetic-admin", roles=["administrator"]))
    operator.main()
    with pytest.raises(ServiceError):
        operator.main()
    client = TestClient(create_app(settings, release, runtime, verifier))
    assert (
        client.get(
            "/api/v1/audit-events", headers={"Authorization": "Bearer " + token()}
        ).status_code
        == 403
    )
    assert client.post("/api/v1/admin/" + command, json={}).status_code == 404
    with runtime.engine.begin() as conn:
        latest = conn.execute(
            sa.select(s.events.c.event_type)
            .order_by(s.events.c.sequence.desc())
            .limit(1)
        ).scalar_one()
        assert latest == (
            "role_revoked" if command == "revoke-role" else "subject_disabled"
        )


def test_database_lock_deadline_rolls_back_without_late_writes(prepared, release):
    from aletheia.application.store import lock

    owner, runtime, _, _, _ = prepared
    with owner.engine.begin() as blocked, ThreadPoolExecutor(max_workers=1) as pool:
        lock(blocked)
        future = pool.submit(predict, runtime, release, deadline=time.monotonic() + 0.1)
        with pytest.raises((SQLAlchemyError, ServiceError)):
            future.result(timeout=3)
    time.sleep(0.15)
    with runtime.engine.begin() as conn:
        assert (
            conn.execute(
                sa.select(sa.func.count()).select_from(s.predictions)
            ).scalar_one()
            == 0
        )
        assert (
            conn.execute(sa.select(sa.func.count()).select_from(s.keys)).scalar_one()
            == 0
        )
