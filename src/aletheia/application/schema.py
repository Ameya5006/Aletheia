"""PostgreSQL-only storage contract. Migrations own schema and privileges."""

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

metadata = sa.MetaData()


def pk():
    return sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def stamp(name="created_at"):
    return sa.Column(
        name,
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )


def fk(name, table, nullable=False, **kwargs):
    return sa.Column(
        name,
        UUID(as_uuid=True),
        sa.ForeignKey(f"{table}.id", ondelete="RESTRICT"),
        nullable=nullable,
        **kwargs,
    )


def text(name, **kwargs):
    return sa.Column(name, sa.Text, nullable=False, **kwargs)


subjects = sa.Table(
    "subjects",
    metadata,
    pk(),
    text("issuer"),
    text("sub"),
    stamp(),
    sa.Column("disabled_at", sa.DateTime(timezone=True)),
    sa.UniqueConstraint("issuer", "sub"),
)
roles = sa.Table(
    "roles",
    metadata,
    text("code", primary_key=True),
    sa.CheckConstraint("code IN ('engineer','reviewer','administrator')"),
)
heads = sa.Table(
    "audit_chain_heads",
    metadata,
    text("chain_id", primary_key=True),
    sa.Column("last_sequence", sa.BigInteger, nullable=False),
    text("last_hash"),
    sa.CheckConstraint("last_sequence >= 0"),
    sa.CheckConstraint("last_hash ~ '^[0-9a-f]{64}$'"),
)
EVENT_TYPES = (
    "'initial_administrator_bootstrap','role_granted','role_revoked',"
    "'subject_disabled','prediction_created','review_created',"
    "'release_approved','release_revoked','release_activated','release_rolled_back'"
)
events = sa.Table(
    "audit_events",
    metadata,
    pk(),
    sa.Column(
        "chain_id",
        sa.Text,
        sa.ForeignKey("audit_chain_heads.chain_id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("sequence", sa.BigInteger, nullable=False),
    fk("actor_id", "subjects", True),
    sa.Column("request_id", UUID(as_uuid=True), nullable=False),
    text("event_type"),
    sa.Column("resource_id", UUID(as_uuid=True), nullable=False),
    sa.Column("payload", JSONB, nullable=False),
    stamp("occurred_at"),
    text("prev_hash"),
    text("event_hash"),
    text("chain_version"),
    sa.UniqueConstraint("chain_id", "sequence"),
    sa.CheckConstraint(f"event_type IN ({EVENT_TYPES})"),
    sa.CheckConstraint("sequence > 0 AND chain_version = 'audit-chain-v1'"),
    sa.CheckConstraint(
        "prev_hash ~ '^[0-9a-f]{64}$' AND event_hash ~ '^[0-9a-f]{64}$'"
    ),
    sa.CheckConstraint("jsonb_typeof(payload) = 'object'"),
    sa.CheckConstraint(
        "(actor_id IS NULL) = (event_type = 'initial_administrator_bootstrap')"
    ),
)
sa.Index(
    "only_one_bootstrap",
    events.c.event_type,
    unique=True,
    postgresql_where=events.c.event_type == "initial_administrator_bootstrap",
)
grants = sa.Table(
    "subject_roles",
    metadata,
    fk("subject_id", "subjects", primary_key=True),
    sa.Column(
        "role_code",
        sa.Text,
        sa.ForeignKey("roles.code", ondelete="RESTRICT"),
        primary_key=True,
    ),
    stamp("granted_at"),
    fk("granted_by", "subjects", True),
    text("grant_kind"),
    fk("grant_audit_event_id", "audit_events", unique=True),
    sa.CheckConstraint("grant_kind IN ('bootstrap','operator')"),
    sa.CheckConstraint("(granted_by IS NULL) = (grant_kind = 'bootstrap')"),
    sa.CheckConstraint("grant_kind <> 'bootstrap' OR role_code = 'administrator'"),
)
models = sa.Table(
    "model_versions",
    metadata,
    pk(),
    text("registry_name"),
    text("version"),
    text("run_id"),
    *[
        text(n)
        for n in (
            "model_sha256",
            "package_sha256",
            "release_sha256",
            "config_sha256",
            "selection_sha256",
            "split_sha256",
            "protocol_sha256",
            "results_sha256",
        )
    ],
    text("signature_version"),
    sa.Column("runtime", JSONB, nullable=False),
    stamp(),
    sa.UniqueConstraint("registry_name", "version"),
    sa.UniqueConstraint("release_sha256"),
    sa.CheckConstraint("version ~ '^[1-9][0-9]*$'"),
    *[
        sa.CheckConstraint(f"{n} ~ '^[0-9a-f]{{64}}$'")
        for n in (
            "model_sha256",
            "package_sha256",
            "release_sha256",
            "config_sha256",
            "selection_sha256",
            "split_sha256",
            "protocol_sha256",
            "results_sha256",
        )
    ],
)
releases = sa.Table(
    "model_release_events",
    metadata,
    pk(),
    fk("model_version_id", "model_versions"),
    fk("actor_id", "subjects"),
    text("action"),
    fk("previous_version_id", "model_versions", True),
    stamp(),
    fk("audit_event_id", "audit_events", unique=True),
    sa.CheckConstraint("action IN ('approved','revoked','activated','rolled_back')"),
)
explanations = sa.Table(
    "explanation_references",
    metadata,
    pk(),
    fk("model_version_id", "model_versions"),
    text("kind"),
    sa.Column("case_id", sa.Text),
    text("result_sha256"),
    text("section"),
    text("schema_version"),
    sa.UniqueConstraint("model_version_id", "kind"),
    sa.UniqueConstraint("id", "model_version_id", "case_id"),
    sa.CheckConstraint(
        "kind IN ('global','synthetic_local','stability','subgroups','feasibility')"
    ),
    sa.CheckConstraint(
        "(kind = 'synthetic_local' AND case_id = 'synthetic-discharge-v1') "
        "OR (kind <> 'synthetic_local' AND case_id IS NULL)"
    ),
)
predictions = sa.Table(
    "prediction_events",
    metadata,
    pk(),
    fk("actor_id", "subjects"),
    fk("model_version_id", "model_versions"),
    text("case_id"),
    text("input_sha256"),
    sa.Column("probability", sa.Double, nullable=False),
    sa.Column("threshold", sa.Double, nullable=False),
    sa.Column("class_at_threshold", sa.Integer, nullable=False),
    fk("explanation_ref_id", "explanation_references"),
    stamp(),
    fk("audit_event_id", "audit_events", unique=True),
    sa.ForeignKeyConstraint(
        ["explanation_ref_id", "model_version_id", "case_id"],
        [
            "explanation_references.id",
            "explanation_references.model_version_id",
            "explanation_references.case_id",
        ],
        ondelete="RESTRICT",
    ),
    sa.CheckConstraint(
        "probability >= 0 AND probability <= 1 AND probability <> 'NaN'::float8"
    ),
    sa.CheckConstraint("threshold = 0.5 AND class_at_threshold IN (0,1)"),
    sa.CheckConstraint("case_id = 'synthetic-discharge-v1'"),
    sa.CheckConstraint("input_sha256 ~ '^[0-9a-f]{64}$'"),
)
reviews = sa.Table(
    "reviewer_decisions",
    metadata,
    pk(),
    fk("prediction_id", "prediction_events"),
    fk("reviewer_id", "subjects"),
    sa.Column("revision", sa.Integer, nullable=False),
    text("decision"),
    text("reason_code"),
    stamp(),
    fk("audit_event_id", "audit_events", unique=True),
    sa.UniqueConstraint("prediction_id", "reviewer_id", "revision"),
    sa.CheckConstraint("revision > 0"),
    sa.CheckConstraint(
        "decision IN ('acknowledged','needs_investigation','dismissed_demo')"
    ),
    sa.CheckConstraint(
        "reason_code IN ('evidence_reviewed','limitations_noted','identity_issue')"
    ),
)
keys = sa.Table(
    "idempotency_records",
    metadata,
    pk(),
    fk("actor_id", "subjects"),
    text("method"),
    text("route"),
    sa.Column("key", UUID(as_uuid=True), nullable=False),
    text("payload_sha256"),
    sa.Column("resource_id", UUID(as_uuid=True), nullable=False),
    text("response_schema"),
    sa.Column("status", sa.Integer, nullable=False),
    stamp(),
    sa.UniqueConstraint("actor_id", "method", "route", "key"),
    sa.CheckConstraint("payload_sha256 ~ '^[0-9a-f]{64}$' AND status = 201"),
)

# Operator-owned projection; append-only release events remain the authority.
deployment = sa.Table(
    "deployment_state",
    metadata,
    sa.Column("singleton", sa.Integer, primary_key=True),
    fk("active_model_id", "model_versions", True),
    fk("release_event_id", "model_release_events", True),
    sa.Column("published", sa.Boolean, nullable=False, server_default=sa.false()),
    sa.CheckConstraint("singleton = 1"),
)


IMMUTABLE = (models, releases, explanations, predictions, reviews, events, keys)
