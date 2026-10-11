"""Initial delivery schema, insert-only history and attributed grants."""

from alembic import op
from sqlalchemy import text

revision = "0001_backend"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    op.execute("""
CREATE TABLE audit_chain_heads (
      chain_id TEXT NOT NULL,
      last_sequence BIGINT NOT NULL,
      last_hash TEXT NOT NULL,
      PRIMARY KEY (chain_id),
      CHECK (last_sequence >= 0),
      CHECK (last_hash ~ '^[0-9a-f]{64}$')
)
    """)
    op.execute("""
CREATE TABLE model_versions (
      id UUID NOT NULL,
      registry_name TEXT NOT NULL,
      version TEXT NOT NULL,
      run_id TEXT NOT NULL,
      model_sha256 TEXT NOT NULL,
      package_sha256 TEXT NOT NULL,
      release_sha256 TEXT NOT NULL,
      config_sha256 TEXT NOT NULL,
      selection_sha256 TEXT NOT NULL,
      split_sha256 TEXT NOT NULL,
      protocol_sha256 TEXT NOT NULL,
      results_sha256 TEXT NOT NULL,
      signature_version TEXT NOT NULL,
      runtime JSONB NOT NULL,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
      PRIMARY KEY (id),
      UNIQUE (registry_name, version),
      UNIQUE (release_sha256),
      CHECK (version ~ '^[1-9][0-9]*$'),
      CHECK (model_sha256 ~ '^[0-9a-f]{64}$'),
      CHECK (package_sha256 ~ '^[0-9a-f]{64}$'),
      CHECK (release_sha256 ~ '^[0-9a-f]{64}$'),
      CHECK (config_sha256 ~ '^[0-9a-f]{64}$'),
      CHECK (selection_sha256 ~ '^[0-9a-f]{64}$'),
      CHECK (split_sha256 ~ '^[0-9a-f]{64}$'),
      CHECK (protocol_sha256 ~ '^[0-9a-f]{64}$'),
      CHECK (results_sha256 ~ '^[0-9a-f]{64}$')
)
    """)
    op.execute("""
CREATE TABLE roles (
      code TEXT NOT NULL,
      PRIMARY KEY (code),
      CHECK (code IN ('engineer','reviewer','administrator'))
)
    """)
    op.execute("""
CREATE TABLE subjects (
      id UUID NOT NULL,
      issuer TEXT NOT NULL,
      sub TEXT NOT NULL,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
      disabled_at TIMESTAMP WITH TIME ZONE,
      PRIMARY KEY (id),
      UNIQUE (issuer, sub)
)
    """)
    op.execute("""
CREATE TABLE audit_events (
      id UUID NOT NULL,
      chain_id TEXT NOT NULL,
      sequence BIGINT NOT NULL,
      actor_id UUID,
      request_id UUID NOT NULL,
      event_type TEXT NOT NULL,
      resource_id UUID NOT NULL,
      payload JSONB NOT NULL,
      occurred_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
      prev_hash TEXT NOT NULL,
      event_hash TEXT NOT NULL,
      chain_version TEXT NOT NULL,
      PRIMARY KEY (id),
      UNIQUE (chain_id, sequence),
      CHECK (event_type IN (
        'initial_administrator_bootstrap','role_granted','role_revoked',
        'subject_disabled','prediction_created','review_created',
        'release_approved','release_revoked','release_activated','release_rolled_back')),
      CHECK (sequence > 0 AND chain_version = 'audit-chain-v1'),
      CHECK (prev_hash ~ '^[0-9a-f]{64}$' AND event_hash ~ '^[0-9a-f]{64}$'),
      CHECK (jsonb_typeof(payload) = 'object'),
      CHECK ((actor_id IS NULL) = (event_type = 'initial_administrator_bootstrap')),
      FOREIGN KEY(chain_id) REFERENCES audit_chain_heads (chain_id) ON DELETE RESTRICT,
      FOREIGN KEY(actor_id) REFERENCES subjects (id) ON DELETE RESTRICT
)
    """)
    op.execute("""
CREATE TABLE explanation_references (
      id UUID NOT NULL,
      model_version_id UUID NOT NULL,
      kind TEXT NOT NULL,
      case_id TEXT,
      result_sha256 TEXT NOT NULL,
      section TEXT NOT NULL,
      schema_version TEXT NOT NULL,
      PRIMARY KEY (id),
      UNIQUE (model_version_id, kind),
      UNIQUE (id, model_version_id, case_id),
      CHECK (kind IN (
        'global','synthetic_local','stability','subgroups','feasibility')),
      CHECK ((kind = 'synthetic_local' AND case_id = 'synthetic-discharge-v1')
        OR (kind <> 'synthetic_local' AND case_id IS NULL)),
      FOREIGN KEY(model_version_id) REFERENCES model_versions (id) ON DELETE RESTRICT
)
    """)
    op.execute("""
CREATE TABLE idempotency_records (
      id UUID NOT NULL,
      actor_id UUID NOT NULL,
      method TEXT NOT NULL,
      route TEXT NOT NULL,
      key UUID NOT NULL,
      payload_sha256 TEXT NOT NULL,
      resource_id UUID NOT NULL,
      response_schema TEXT NOT NULL,
      status INTEGER NOT NULL,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
      PRIMARY KEY (id),
      UNIQUE (actor_id, method, route, key),
      CHECK (payload_sha256 ~ '^[0-9a-f]{64}$' AND status = 201),
      FOREIGN KEY(actor_id) REFERENCES subjects (id) ON DELETE RESTRICT
)
    """)
    op.execute("""
CREATE TABLE model_release_events (
      id UUID NOT NULL,
      model_version_id UUID NOT NULL,
      actor_id UUID NOT NULL,
      action TEXT NOT NULL,
      previous_version_id UUID,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
      audit_event_id UUID NOT NULL,
      PRIMARY KEY (id),
      CHECK (action IN ('approved','revoked','activated','rolled_back')),
      FOREIGN KEY(model_version_id) REFERENCES model_versions (id) ON DELETE RESTRICT,
      FOREIGN KEY(actor_id) REFERENCES subjects (id) ON DELETE RESTRICT,
      FOREIGN KEY(previous_version_id) REFERENCES model_versions (id)
        ON DELETE RESTRICT,
      UNIQUE (audit_event_id),
      FOREIGN KEY(audit_event_id) REFERENCES audit_events (id) ON DELETE RESTRICT
)
    """)
    op.execute("""
CREATE TABLE prediction_events (
      id UUID NOT NULL,
      actor_id UUID NOT NULL,
      model_version_id UUID NOT NULL,
      case_id TEXT NOT NULL,
      input_sha256 TEXT NOT NULL,
      probability DOUBLE PRECISION NOT NULL,
      threshold DOUBLE PRECISION NOT NULL,
      class_at_threshold INTEGER NOT NULL,
      explanation_ref_id UUID NOT NULL,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
      audit_event_id UUID NOT NULL,
      PRIMARY KEY (id),
      FOREIGN KEY(explanation_ref_id, model_version_id, case_id)
        REFERENCES explanation_references (id, model_version_id, case_id)
        ON DELETE RESTRICT,
      CHECK (probability >= 0 AND probability <= 1 AND probability <> 'NaN'::float8),
      CHECK (threshold = 0.5 AND class_at_threshold IN (0,1)),
      CHECK (case_id = 'synthetic-discharge-v1'),
      CHECK (input_sha256 ~ '^[0-9a-f]{64}$'),
      FOREIGN KEY(actor_id) REFERENCES subjects (id) ON DELETE RESTRICT,
      FOREIGN KEY(model_version_id) REFERENCES model_versions (id) ON DELETE RESTRICT,
      FOREIGN KEY(explanation_ref_id) REFERENCES explanation_references (id)
        ON DELETE RESTRICT,
      UNIQUE (audit_event_id),
      FOREIGN KEY(audit_event_id) REFERENCES audit_events (id) ON DELETE RESTRICT
)
    """)
    op.execute("""
CREATE TABLE subject_roles (
      subject_id UUID NOT NULL,
      role_code TEXT NOT NULL,
      granted_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
      granted_by UUID,
      grant_kind TEXT NOT NULL,
      grant_audit_event_id UUID NOT NULL,
      PRIMARY KEY (subject_id, role_code),
      CHECK (grant_kind IN ('bootstrap','operator')),
      CHECK ((granted_by IS NULL) = (grant_kind = 'bootstrap')),
      CHECK (grant_kind <> 'bootstrap' OR role_code = 'administrator'),
      FOREIGN KEY(subject_id) REFERENCES subjects (id) ON DELETE RESTRICT,
      FOREIGN KEY(role_code) REFERENCES roles (code) ON DELETE RESTRICT,
      FOREIGN KEY(granted_by) REFERENCES subjects (id) ON DELETE RESTRICT,
      UNIQUE (grant_audit_event_id),
      FOREIGN KEY(grant_audit_event_id) REFERENCES audit_events (id) ON DELETE RESTRICT
)
    """)
    op.execute("""
CREATE TABLE reviewer_decisions (
      id UUID NOT NULL,
      prediction_id UUID NOT NULL,
      reviewer_id UUID NOT NULL,
      revision INTEGER NOT NULL,
      decision TEXT NOT NULL,
      reason_code TEXT NOT NULL,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
      audit_event_id UUID NOT NULL,
      PRIMARY KEY (id),
      UNIQUE (prediction_id, reviewer_id, revision),
      CHECK (revision > 0),
      CHECK (decision IN ('acknowledged','needs_investigation','dismissed_demo')),
      CHECK (reason_code IN ('evidence_reviewed','limitations_noted','identity_issue')),
      FOREIGN KEY(prediction_id) REFERENCES prediction_events (id) ON DELETE RESTRICT,
      FOREIGN KEY(reviewer_id) REFERENCES subjects (id) ON DELETE RESTRICT,
      UNIQUE (audit_event_id),
      FOREIGN KEY(audit_event_id) REFERENCES audit_events (id) ON DELETE RESTRICT
)
    """)
    op.execute("""
CREATE UNIQUE INDEX only_one_bootstrap ON audit_events (event_type)
  WHERE event_type = 'initial_administrator_bootstrap'
    """)
    op.execute(
        "INSERT INTO roles (code) VALUES ('engineer'), ('reviewer'), ('administrator')"
    )
    op.execute(
        "INSERT INTO audit_chain_heads (chain_id,last_sequence,last_hash) "
        "VALUES ('application',0,"
        "'0000000000000000000000000000000000000000000000000000000000000000')"
    )
    conn.execute(
        text("""DO $$ BEGIN
      IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='aletheia_runtime')
      THEN CREATE ROLE aletheia_runtime NOLOGIN; END IF; END $$""")
    )
    conn.execute(text("REVOKE ALL ON SCHEMA public FROM PUBLIC"))
    conn.execute(text("GRANT USAGE ON SCHEMA public TO aletheia_runtime"))
    for name in (
        "audit_chain_heads",
        "model_versions",
        "roles",
        "subjects",
        "audit_events",
        "explanation_references",
        "idempotency_records",
        "model_release_events",
        "prediction_events",
        "subject_roles",
        "reviewer_decisions",
    ):
        conn.execute(text(f'GRANT SELECT ON "{name}" TO aletheia_runtime'))
    conn.execute(text("GRANT SELECT ON alembic_version TO aletheia_runtime"))
    for table in (
        "prediction_events",
        "reviewer_decisions",
        "audit_events",
        "idempotency_records",
    ):
        conn.execute(text(f'GRANT INSERT ON "{table}" TO aletheia_runtime'))
    conn.execute(
        text(
            "GRANT UPDATE (last_sequence,last_hash) ON audit_chain_heads "
            "TO aletheia_runtime"
        )
    )
    conn.execute(
        text("""
    CREATE FUNCTION reject_history_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN RAISE EXCEPTION 'append-only history'; END $$
    """)
    )
    for table in (
        "model_versions",
        "model_release_events",
        "explanation_references",
        "prediction_events",
        "reviewer_decisions",
        "audit_events",
        "idempotency_records",
    ):
        conn.execute(
            text(
                "CREATE TRIGGER immutable_history BEFORE UPDATE OR DELETE "
                f"OR TRUNCATE ON {table} FOR EACH STATEMENT "
                "EXECUTE FUNCTION reject_history_mutation()"
            )
        )
    conn.execute(
        text("""
    CREATE FUNCTION validate_event_scope() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.event_type NOT IN ('prediction_created','review_created')
        AND NOT has_table_privilege(current_user,'subject_roles','INSERT')
      THEN RAISE EXCEPTION 'operator event privilege required'; END IF;
      IF EXISTS (SELECT 1 FROM jsonb_object_keys(NEW.payload) k WHERE k NOT IN
        ('role','attribution','prediction_id','revision','decision','reason_code',
         'case_id','probability','model_version','version','release_sha256'))
      THEN RAISE EXCEPTION 'unapproved audit payload'; END IF;
      RETURN NEW;
    END $$
    """)
    )
    conn.execute(
        text(
            "CREATE TRIGGER event_scope BEFORE INSERT ON audit_events "
            "FOR EACH ROW EXECUTE FUNCTION validate_event_scope()"
        )
    )
    conn.execute(
        text("""
    CREATE FUNCTION validate_grant() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE e audit_events; BEGIN
      SELECT * INTO STRICT e FROM audit_events WHERE id = NEW.grant_audit_event_id;
      IF e.payload->>'role' IS DISTINCT FROM NEW.role_code
      THEN RAISE EXCEPTION 'grant role mismatch'; END IF;
      IF e.resource_id <> NEW.subject_id THEN
        RAISE EXCEPTION 'grant resource mismatch'; END IF;
      IF NEW.grant_kind = 'bootstrap' THEN
        IF e.event_type <> 'initial_administrator_bootstrap' OR e.actor_id IS NOT NULL
        THEN RAISE EXCEPTION 'invalid bootstrap attribution'; END IF;
      ELSE
        IF e.event_type <> 'role_granted' OR e.actor_id IS DISTINCT FROM NEW.granted_by
          OR NOT EXISTS (SELECT 1 FROM subject_roles g
             JOIN subjects s ON s.id=g.subject_id
             WHERE g.subject_id=NEW.granted_by AND g.role_code='administrator'
             AND s.disabled_at IS NULL)
        THEN RAISE EXCEPTION 'administrator attribution required'; END IF;
      END IF;
      RETURN NEW;
    END $$
    """)
    )
    conn.execute(
        text(
            "CREATE CONSTRAINT TRIGGER attributed_grant AFTER INSERT OR UPDATE "
            "ON subject_roles DEFERRABLE INITIALLY DEFERRED FOR EACH ROW "
            "EXECUTE FUNCTION validate_grant()"
        )
    )
    conn.execute(
        text("""
    CREATE FUNCTION validate_business_event() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE e audit_events; expected_actor uuid; expected_type text; BEGIN
      SELECT * INTO STRICT e FROM audit_events WHERE id = NEW.audit_event_id;
      IF TG_TABLE_NAME = 'prediction_events' THEN
        expected_actor=NEW.actor_id; expected_type='prediction_created';
      ELSIF TG_TABLE_NAME = 'reviewer_decisions' THEN
        expected_actor=NEW.reviewer_id; expected_type='review_created';
      ELSE expected_actor=NEW.actor_id; expected_type='release_' || NEW.action; END IF;
      IF e.resource_id <> NEW.id OR e.actor_id IS DISTINCT FROM expected_actor
        OR e.event_type <> expected_type
      THEN RAISE EXCEPTION 'business audit mismatch'; END IF;
      RETURN NEW;
    END $$
    """)
    )
    for table in ("prediction_events", "reviewer_decisions", "model_release_events"):
        conn.execute(
            text(
                f"CREATE CONSTRAINT TRIGGER business_audit AFTER INSERT ON {table} "
                "DEFERRABLE INITIALLY DEFERRED FOR EACH ROW "
                "EXECUTE FUNCTION validate_business_event()"
            )
        )


def downgrade():
    raise RuntimeError(
        "destructive downgrade refused; use verified backup and forward repair"
    )
