"""Transactional serving, review and operator commands on PostgreSQL."""

import json
import time
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

import sqlalchemy as sa

from . import schema as s
from .auth import ServiceError
from .release import CASE, canonical, safe_file, sha

HEAD = "0003_integrity"


def row(conn, query):
    result = conn.execute(query).mappings().first()
    return dict(result) if result else None


def lock(conn):
    return row(
        conn,
        sa.select(s.heads).where(s.heads.c.chain_id == "application").with_for_update(),
    )


def event_bytes(event):
    def floats(value):
        if isinstance(value, float):
            raise ValueError("floats forbidden in canonical audit payload")
        if isinstance(value, dict):
            for v in value.values():
                floats(v)
        elif isinstance(value, list):
            for v in value:
                floats(v)

    floats(event)
    return canonical(event)


def verify_chain(values, checkpoint_sequence=0, checkpoint_hash="0" * 64):
    """Verify a complete ordered suffix against an independently trusted checkpoint."""
    sequence, previous = checkpoint_sequence, checkpoint_hash
    for value in values:
        data = {
            "chain_id": value["chain_id"],
            "sequence": value["sequence"],
            "actor_id": str(value["actor_id"]) if value["actor_id"] else None,
            "request_id": str(value["request_id"]),
            "resource_id": str(value["resource_id"]),
            "event_type": value["event_type"],
            "occurred_at": value["occurred_at"]
            .astimezone(UTC)
            .isoformat(timespec="microseconds"),
            "payload": value["payload"],
            "prev_hash": value["prev_hash"],
            "chain_version": value["chain_version"],
        }
        if (
            value["sequence"] != sequence + 1
            or value["prev_hash"] != previous
            or sha(event_bytes(data)) != value["event_hash"]
        ):
            raise ValueError("audit chain verification failed")
        sequence, previous = value["sequence"], value["event_hash"]
    return sequence, previous


def audit(conn, actor, kind, resource, request_id, payload):
    head = lock(conn)
    if head is None:
        raise ServiceError(503, "audit_unavailable")
    occurred = datetime.now(UTC)
    data = {
        "chain_id": "application",
        "sequence": head["last_sequence"] + 1,
        "actor_id": str(actor) if actor else None,
        "request_id": str(request_id),
        "resource_id": str(resource),
        "event_type": kind,
        "occurred_at": occurred.isoformat(timespec="microseconds"),
        "payload": payload,
        "prev_hash": head["last_hash"],
        "chain_version": "audit-chain-v1",
    }
    digest = sha(event_bytes(data))
    eid = uuid.uuid4()
    conn.execute(
        s.events.insert().values(
            id=eid,
            chain_id="application",
            sequence=data["sequence"],
            actor_id=actor,
            request_id=request_id,
            resource_id=resource,
            event_type=kind,
            payload=payload,
            occurred_at=occurred,
            prev_hash=head["last_hash"],
            event_hash=digest,
            chain_version="audit-chain-v1",
        )
    )
    conn.execute(
        s.heads.update()
        .where(s.heads.c.chain_id == "application")
        .values(last_sequence=data["sequence"], last_hash=digest)
    )
    return eid


class Store:
    def __init__(self, url, pin_path="artifacts/backend-deployment-pin.json"):
        self.pin_path = Path(pin_path).absolute()
        self.engine = sa.create_engine(
            url,
            pool_pre_ping=True,
            pool_size=4,
            max_overflow=0,
            connect_args={
                "connect_timeout": 2,
                "options": "-c statement_timeout=2000 -c lock_timeout=2000 "
                "-c timezone=UTC",
            },
        )
        if self.engine.dialect.name != "postgresql":
            raise ValueError("PostgreSQL required")

    def migrated(self, conn):
        return (
            conn.execute(sa.text("SELECT version_num FROM alembic_version")).scalar()
            == HEAD
        )

    @contextmanager
    def publication_lock(self):
        # Separate from the short audit lock: held over operator publication only.
        with self.engine.begin() as conn:
            conn.execute(sa.text("SELECT pg_advisory_xact_lock(74913401)"))
            yield

    def authorize(self, conn, identity, required=()):
        subject = row(
            conn,
            sa.select(s.subjects).where(
                s.subjects.c.issuer == identity.issuer, s.subjects.c.sub == identity.sub
            ),
        )
        if not subject or subject["disabled_at"]:
            raise ServiceError(403, "forbidden")
        local = set(
            conn.execute(
                sa.select(s.grants.c.role_code).where(
                    s.grants.c.subject_id == subject["id"]
                )
            ).scalars()
        )
        roles = identity.roles & local
        if not roles or (required and not roles.intersection(required)):
            raise ServiceError(403, "forbidden")
        return subject["id"], roles

    def approved(self, conn, version, digest, require_active=True):
        model = row(
            conn,
            sa.select(s.models).where(
                s.models.c.version == version, s.models.c.release_sha256 == digest
            ),
        )
        if not model:
            raise ServiceError(503, "model_unavailable")
        release = row(
            conn,
            sa.select(s.releases)
            .join(s.events, s.events.c.id == s.releases.c.audit_event_id)
            .where(s.releases.c.model_version_id == model["id"])
            .order_by(s.events.c.sequence.desc())
            .limit(1),
        )
        if not release or release["action"] not in {
            "approved",
            "activated",
            "rolled_back",
        }:
            raise ServiceError(503, "model_unavailable")
        if require_active:
            state = row(conn, sa.select(s.deployment))
            if (
                not state
                or not state["published"]
                or state["active_model_id"] != model["id"]
            ):
                raise ServiceError(503, "activation_required")
            event = row(
                conn,
                sa.select(s.releases).where(
                    s.releases.c.id == state["release_event_id"]
                ),
            )
            try:
                pin = json.loads(
                    safe_file(self.pin_path.parent, self.pin_path.name).read_bytes()
                )
            except (OSError, ValueError) as exc:
                raise ServiceError(503, "deployment_pin_unavailable") from exc
            if pin != self.deployment_pin(conn, state, event):
                raise ServiceError(503, "deployment_pin_disagreement")
        return model

    def deployment_pin(self, conn, state, event):
        model = row(
            conn, sa.select(s.models).where(s.models.c.id == state["active_model_id"])
        )
        return {
            "event_id": str(event["audit_event_id"]),
            "action": event["action"],
            "active": {
                k: model[k]
                for k in (
                    "registry_name",
                    "version",
                    "run_id",
                    "release_sha256",
                    "package_sha256",
                )
            }
            if model
            else None,
        }

    def release_action(self, identity, version, digest, action):
        if action not in {"activated", "revoked", "rolled_back"}:
            raise ValueError("unsupported release action")
        with self.engine.begin() as conn:
            lock(conn)
            actor, _ = self.authorize(conn, identity, {"administrator"})
            model = row(
                conn,
                sa.select(s.models).where(
                    s.models.c.version == version, s.models.c.release_sha256 == digest
                ),
            )
            if not model:
                raise ServiceError(503, "model_unavailable")
            state = row(conn, sa.select(s.deployment).with_for_update())
            last = row(
                conn,
                sa.select(s.releases).where(
                    s.releases.c.id == state["release_event_id"]
                ),
            )
            if (
                last
                and last["model_version_id"] == model["id"]
                and last["action"] == action
            ):
                return last["audit_event_id"]
            if not state["published"] and last:
                raise ServiceError(409, "publication_pending")
            self.approved(conn, version, digest, require_active=False)
            if (
                action == "rolled_back"
                and not conn.execute(
                    sa.select(s.releases.c.id).where(
                        s.releases.c.model_version_id == model["id"],
                        s.releases.c.action.in_(("activated", "rolled_back")),
                    )
                ).first()
            ):
                raise ServiceError(409, "rollback_requires_previous_activation")
            rid = uuid.uuid4()
            eid = audit(
                conn,
                actor,
                "release_" + action,
                rid,
                uuid.uuid4(),
                {"version": version, "release_sha256": digest},
            )
            conn.execute(
                s.releases.insert().values(
                    id=rid,
                    model_version_id=model["id"],
                    actor_id=actor,
                    action=action,
                    previous_version_id=state["active_model_id"],
                    audit_event_id=eid,
                )
            )
            active = model["id"] if action != "revoked" else state["active_model_id"]
            if action == "revoked" and active == model["id"]:
                active = None
            conn.execute(
                s.deployment.update().values(
                    active_model_id=active, release_event_id=rid, published=False
                )
            )
            self.authorize(conn, identity, {"administrator"})
            return eid

    def finish_publication(self, identity, event_id, pin):
        with self.engine.begin() as conn:
            lock(conn)
            self.authorize(conn, identity, {"administrator"})
            state = row(conn, sa.select(s.deployment).with_for_update())
            event = row(
                conn,
                sa.select(s.releases).where(
                    s.releases.c.id == state["release_event_id"]
                ),
            )
            if (
                not event
                or event["audit_event_id"] != event_id
                or self.deployment_pin(conn, state, event) != pin
            ):
                raise ServiceError(409, "publication_conflict")
            conn.execute(s.deployment.update().values(published=True))
            self.authorize(conn, identity, {"administrator"})

    def revoke_role(self, identity, issuer, subject, role):
        if role not in {"engineer", "reviewer", "administrator"}:
            raise ValueError("unsupported role")
        with self.engine.begin() as conn:
            lock(conn)
            actor, _ = self.authorize(conn, identity, {"administrator"})
            target = row(
                conn,
                sa.select(s.subjects).where(
                    s.subjects.c.issuer == issuer, s.subjects.c.sub == subject
                ),
            )
            if not target:
                raise ServiceError(404, "not_found")
            if target["disabled_at"] or (
                target["id"] == actor and role == "administrator"
            ):
                raise ServiceError(409, "unsafe_entitlement_change")
            audit(
                conn, actor, "role_revoked", target["id"], uuid.uuid4(), {"role": role}
            )
            result = conn.execute(
                s.grants.delete().where(
                    s.grants.c.subject_id == target["id"], s.grants.c.role_code == role
                )
            )
            if result.rowcount != 1:
                raise ServiceError(404, "not_found")
            self.authorize(conn, identity, {"administrator"})

    def disable_subject(self, identity, issuer, subject):
        with self.engine.begin() as conn:
            lock(conn)
            actor, _ = self.authorize(conn, identity, {"administrator"})
            target = row(
                conn,
                sa.select(s.subjects)
                .where(s.subjects.c.issuer == issuer, s.subjects.c.sub == subject)
                .with_for_update(),
            )
            if not target:
                raise ServiceError(404, "not_found")
            if target["disabled_at"] or target["id"] == actor:
                raise ServiceError(409, "unsafe_entitlement_change")
            eid = audit(conn, actor, "subject_disabled", target["id"], uuid.uuid4(), {})
            conn.execute(
                s.subjects.update()
                .where(s.subjects.c.id == target["id"])
                .values(disabled_at=sa.func.now())
            )
            self.authorize(conn, identity, {"administrator"})
            return eid

    def bootstrap(self, issuer, subject):
        if not issuer or not subject:
            raise ValueError("explicit configured identity required")
        with self.engine.begin() as conn:
            if not conn.execute(
                sa.text(
                    "SELECT has_table_privilege(current_user,'subject_roles','INSERT')"
                )
            ).scalar():
                raise ServiceError(403, "operator_privilege_required")
            if not self.migrated(conn):
                raise ServiceError(503, "migration_required")
            lock(conn)
            if (
                conn.execute(
                    sa.select(s.events.c.id).where(
                        s.events.c.event_type == "initial_administrator_bootstrap"
                    )
                ).first()
                or conn.execute(sa.select(s.grants)).first()
            ):
                raise ServiceError(409, "bootstrap_refused")
            existing = list(conn.execute(sa.select(s.subjects)).mappings())
            if existing and (
                len(existing) != 1
                or existing[0]["issuer"] != issuer
                or existing[0]["sub"] != subject
                or existing[0]["disabled_at"]
            ):
                raise ServiceError(409, "bootstrap_refused")
            sid = existing[0]["id"] if existing else uuid.uuid4()
            if not existing:
                conn.execute(
                    s.subjects.insert().values(id=sid, issuer=issuer, sub=subject)
                )
            eid = audit(
                conn,
                None,
                "initial_administrator_bootstrap",
                sid,
                uuid.uuid4(),
                {"role": "administrator", "attribution": "system"},
            )
            conn.execute(
                s.grants.insert().values(
                    subject_id=sid,
                    role_code="administrator",
                    granted_by=None,
                    grant_kind="bootstrap",
                    grant_audit_event_id=eid,
                )
            )
            return sid

    def grant(self, actor_identity, issuer, subject, role):
        if role not in {"engineer", "reviewer", "administrator"}:
            raise ValueError("unsupported role")
        with self.engine.begin() as conn:
            lock(conn)
            actor, _ = self.authorize(conn, actor_identity, {"administrator"})
            existing = row(
                conn,
                sa.select(s.subjects).where(
                    s.subjects.c.issuer == issuer, s.subjects.c.sub == subject
                ),
            )
            sid = existing["id"] if existing else uuid.uuid4()
            if existing and existing["disabled_at"]:
                raise ServiceError(409, "disabled_subject")
            if (
                existing
                and conn.execute(
                    sa.select(s.grants.c.role_code).where(
                        s.grants.c.subject_id == sid, s.grants.c.role_code == role
                    )
                ).first()
            ):
                raise ServiceError(409, "role_already_granted")
            if not existing:
                conn.execute(
                    s.subjects.insert().values(id=sid, issuer=issuer, sub=subject)
                )
            eid = audit(conn, actor, "role_granted", sid, uuid.uuid4(), {"role": role})
            conn.execute(
                s.grants.insert().values(
                    subject_id=sid,
                    role_code=role,
                    granted_by=actor,
                    grant_kind="operator",
                    grant_audit_event_id=eid,
                )
            )
            self.authorize(conn, actor_identity, {"administrator"})
            return sid

    def register(self, identity, release, registry):
        with self.engine.begin() as conn:
            lock(conn)
            actor, _ = self.authorize(conn, identity, {"administrator"})
            m = release.manifest
            am = release.protocol
            expected = dict(
                registry_name=registry["name"],
                version=registry["version"],
                run_id=registry["run_id"],
                package_sha256=registry["package_sha256"],
                release_sha256=release.digest,
                model_sha256=am["identity"]["model_sha256"],
                config_sha256=am["config_sha256"],
                selection_sha256=am["identity"]["selection_sha256"],
                split_sha256=am["identity"]["split_lock_sha256"],
                protocol_sha256=am["protocol_sha256"],
                results_sha256=m["files"]["artifacts/healthcare-audit-v1/results.json"],
                signature_version="application-v1",
                runtime=m["runtime"],
            )
            existing = list(
                conn.execute(
                    sa.select(s.models).where(
                        sa.or_(
                            s.models.c.release_sha256 == release.digest,
                            sa.and_(
                                s.models.c.registry_name == registry["name"],
                                s.models.c.version == registry["version"],
                            ),
                            s.models.c.run_id == registry["run_id"],
                        )
                    )
                ).mappings()
            )
            if existing:
                if len(existing) != 1 or any(
                    existing[0][k] != v for k, v in expected.items()
                ):
                    raise ServiceError(409, "registration_identity_conflict")
                self.approved(
                    conn, registry["version"], release.digest, require_active=False
                )
                return existing[0]["id"]
            mid = uuid.uuid4()
            conn.execute(s.models.insert().values(id=mid, **expected))
            for kind, section in (
                ("global", "global"),
                ("synthetic_local", "synthetic_local"),
                ("stability", "stability"),
                ("subgroups", "fairness"),
                ("feasibility", "counterfactual"),
            ):
                conn.execute(
                    s.explanations.insert().values(
                        id=uuid.uuid4(),
                        model_version_id=mid,
                        kind=kind,
                        case_id=CASE if kind == "synthetic_local" else None,
                        result_sha256=release.manifest["files"][
                            "artifacts/healthcare-audit-v1/results.json"
                        ],
                        section=section,
                        schema_version="application-v1",
                    )
                )
            rid = uuid.uuid4()
            eid = audit(
                conn,
                actor,
                "release_approved",
                rid,
                uuid.uuid4(),
                {"version": registry["version"], "release_sha256": release.digest},
            )
            conn.execute(
                s.releases.insert().values(
                    id=rid,
                    model_version_id=mid,
                    actor_id=actor,
                    action="approved",
                    audit_event_id=eid,
                )
            )
            self.authorize(conn, identity, {"administrator"})
            return mid

    def accessible(self, conn, identity, prediction_id):
        actor, roles = self.authorize(conn, identity)
        prediction = row(
            conn, sa.select(s.predictions).where(s.predictions.c.id == prediction_id)
        )
        if not prediction or (
            prediction["actor_id"] != actor
            and not roles & {"reviewer", "administrator"}
        ):
            raise ServiceError(404, "not_found")
        return prediction

    def command(
        self,
        identity,
        payload,
        key,
        request_id,
        version,
        release,
        prediction_id=None,
        deadline=None,
    ):
        route = (
            f"/api/v1/predictions/{prediction_id}/reviews"
            if prediction_id
            else "/api/v1/predictions"
        )
        fingerprint = sha(canonical({"payload": payload, "model_version": version}))
        if deadline is None:
            deadline = time.monotonic() + 10
        self.check_deadline(deadline)
        # First lookup avoids needless inference on retries; final lookup is serialized.
        with self.engine.begin() as conn:
            self.transaction_deadline(conn, deadline)
            actor, _ = self.authorize(
                conn,
                identity,
                {"reviewer"}
                if prediction_id
                else {"engineer", "reviewer", "administrator"},
            )
            previous = self._previous(conn, actor, route, key, fingerprint)
            if previous:
                return previous
        start = time.monotonic()
        score = None if prediction_id else release.score()
        self.check_deadline(deadline)
        if not prediction_id and time.monotonic() - start > 3:
            raise ServiceError(504, "inference_deadline_exceeded")
        with self.engine.begin() as conn:
            self.transaction_deadline(conn, deadline)
            lock(conn)
            actor, _ = self.authorize(
                conn,
                identity,
                {"reviewer"}
                if prediction_id
                else {"engineer", "reviewer", "administrator"},
            )
            model = self.approved(conn, version, release.digest)
            previous = self._previous(conn, actor, route, key, fingerprint)
            if previous:
                return previous
            if deadline is not None and time.monotonic() >= deadline:
                raise ServiceError(504, "deadline_exceeded")
            rid = uuid.uuid4()
            if prediction_id:
                target_prediction = self.accessible(conn, identity, prediction_id)
                if target_prediction["model_version_id"] != model["id"]:
                    raise ServiceError(409, "version_conflict")
                revision = (
                    conn.execute(
                        sa.select(sa.func.max(s.reviews.c.revision)).where(
                            s.reviews.c.prediction_id == prediction_id,
                            s.reviews.c.reviewer_id == actor,
                        )
                    ).scalar()
                    or 0
                )
                if revision != payload["expected_revision"]:
                    raise ServiceError(409, "revision_conflict")
                eid = audit(
                    conn,
                    actor,
                    "review_created",
                    rid,
                    request_id,
                    {
                        "prediction_id": str(prediction_id),
                        "revision": revision + 1,
                        "decision": payload["decision"],
                        "reason_code": payload["reason_code"],
                    },
                )
                conn.execute(
                    s.reviews.insert().values(
                        id=rid,
                        prediction_id=prediction_id,
                        reviewer_id=actor,
                        revision=revision + 1,
                        decision=payload["decision"],
                        reason_code=payload["reason_code"],
                        audit_event_id=eid,
                    )
                )
            else:
                if payload["model_version"] != version:
                    raise ServiceError(409, "version_conflict")
                explanation = row(
                    conn,
                    sa.select(s.explanations).where(
                        s.explanations.c.model_version_id == model["id"],
                        s.explanations.c.kind == "synthetic_local",
                    ),
                )
                if explanation is None:
                    raise ServiceError(503, "evidence_unavailable")
                eid = audit(
                    conn,
                    actor,
                    "prediction_created",
                    rid,
                    request_id,
                    {
                        "case_id": CASE,
                        "probability": format(score, ".17g"),
                        "model_version": version,
                    },
                )
                conn.execute(
                    s.predictions.insert().values(
                        id=rid,
                        actor_id=actor,
                        model_version_id=model["id"],
                        case_id=CASE,
                        input_sha256=sha(canonical(release.case)),
                        probability=score,
                        threshold=0.5,
                        class_at_threshold=int(score >= 0.5),
                        explanation_ref_id=explanation["id"],
                        audit_event_id=eid,
                    )
                )
            conn.execute(
                s.keys.insert().values(
                    actor_id=actor,
                    method="POST",
                    route=route,
                    key=key,
                    payload_sha256=fingerprint,
                    resource_id=rid,
                    response_schema="application-v1",
                    status=201,
                )
            )
            result = row(
                conn,
                sa.select(s.reviews if prediction_id else s.predictions).where(
                    (s.reviews if prediction_id else s.predictions).c.id == rid
                ),
            )
            if deadline is not None and time.monotonic() >= deadline:
                raise ServiceError(504, "deadline_exceeded")
            self.authorize(
                conn,
                identity,
                {"reviewer"}
                if prediction_id
                else {"engineer", "reviewer", "administrator"},
            )
            self.check_deadline(deadline)
        return result  # Context has committed before any successful result is returned.

    @staticmethod
    def check_deadline(deadline):
        if time.monotonic() >= deadline:
            raise ServiceError(504, "deadline_exceeded")

    def transaction_deadline(self, conn, deadline):
        self.check_deadline(deadline)
        milliseconds = str(max(1, min(2000, int((deadline - time.monotonic()) * 1000))))
        for name in ("statement_timeout", "lock_timeout"):
            conn.execute(
                sa.text("SELECT set_config(:name, :value, true)"),
                {"name": name, "value": milliseconds},
            )

    def _previous(self, conn, actor, route, key, fingerprint):
        previous = row(
            conn,
            sa.select(s.keys).where(
                s.keys.c.actor_id == actor,
                s.keys.c.route == route,
                s.keys.c.method == "POST",
                s.keys.c.key == key,
            ),
        )
        if not previous:
            return None
        if previous["payload_sha256"] != fingerprint:
            raise ServiceError(409, "idempotency_conflict")
        table = s.reviews if route.endswith("/reviews") else s.predictions
        return row(conn, sa.select(table).where(table.c.id == previous["resource_id"]))

    def audit_query(self, conn, identity):
        actor, roles = self.authorize(conn, identity)
        condition = sa.false()
        if "administrator" in roles:
            condition = sa.true()
        else:
            if "engineer" in roles:
                condition |= s.events.c.actor_id == actor
            if "reviewer" in roles:
                condition |= sa.or_(
                    sa.and_(
                        s.events.c.event_type == "prediction_created",
                        s.events.c.resource_id.in_(sa.select(s.predictions.c.id)),
                    ),
                    sa.and_(
                        s.events.c.event_type == "review_created",
                        s.events.c.resource_id.in_(sa.select(s.reviews.c.id)),
                    ),
                )
        return sa.select(s.events).where(condition)
