"""Deferred reverse audit bindings and pending lifecycle publication projection."""

from alembic import op
from sqlalchemy import text

revision = "0003_integrity"
down_revision = "0002_deadlines"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    op.execute("""
CREATE TABLE deployment_state (
      singleton SERIAL NOT NULL,
      active_model_id UUID,
      release_event_id UUID,
      published BOOLEAN DEFAULT false NOT NULL,
      PRIMARY KEY (singleton),
      CHECK (singleton = 1),
      FOREIGN KEY(active_model_id) REFERENCES model_versions (id) ON DELETE RESTRICT,
      FOREIGN KEY(release_event_id) REFERENCES model_release_events (id)
        ON DELETE RESTRICT
)
    """)
    op.execute("INSERT INTO deployment_state (singleton,published) VALUES (1,false)")
    conn.execute(text("GRANT SELECT ON deployment_state TO aletheia_runtime"))
    conn.execute(
        text("""
    CREATE FUNCTION validate_reverse_event() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE matches integer; BEGIN
      IF NEW.event_type = 'prediction_created' THEN
        SELECT count(*) INTO matches FROM prediction_events p JOIN model_versions m
          ON m.id=p.model_version_id WHERE p.audit_event_id=NEW.id
          AND p.id=NEW.resource_id AND p.actor_id=NEW.actor_id
          AND NEW.payload->>'case_id'=p.case_id
          AND (NEW.payload->>'probability')::float8=p.probability
          AND NEW.payload->>'model_version'=m.version;
      ELSIF NEW.event_type = 'review_created' THEN
        SELECT count(*) INTO matches FROM reviewer_decisions r
          WHERE r.audit_event_id=NEW.id AND r.id=NEW.resource_id
          AND r.reviewer_id=NEW.actor_id
          AND NEW.payload->>'prediction_id'=r.prediction_id::text
          AND (NEW.payload->>'revision')::integer=r.revision
          AND NEW.payload->>'decision'=r.decision
          AND NEW.payload->>'reason_code'=r.reason_code;
      ELSIF NEW.event_type LIKE 'release_%' THEN
        SELECT count(*) INTO matches FROM model_release_events r JOIN model_versions m
          ON m.id=r.model_version_id WHERE r.audit_event_id=NEW.id
          AND r.id=NEW.resource_id AND r.actor_id=NEW.actor_id
          AND NEW.event_type='release_' || r.action
          AND NEW.payload->>'version'=m.version
          AND NEW.payload->>'release_sha256'=m.release_sha256;
      ELSIF NEW.event_type IN ('role_granted','initial_administrator_bootstrap') THEN
        SELECT count(*) INTO matches FROM subject_roles g
          WHERE g.grant_audit_event_id=NEW.id AND g.subject_id=NEW.resource_id
          AND g.role_code=NEW.payload->>'role'
          AND g.granted_by IS NOT DISTINCT FROM NEW.actor_id
          AND (g.grant_kind='bootstrap')=
            (NEW.event_type='initial_administrator_bootstrap');
      ELSIF NEW.event_type = 'role_revoked' THEN
        SELECT count(*) INTO matches FROM subjects u WHERE u.id=NEW.resource_id
          AND NEW.payload->>'role' IN ('engineer','reviewer','administrator')
          AND NOT EXISTS (SELECT 1 FROM subject_roles g WHERE g.subject_id=u.id
            AND g.role_code=NEW.payload->>'role');
      ELSIF NEW.event_type = 'subject_disabled' THEN
        SELECT count(*) INTO matches FROM subjects u WHERE u.id=NEW.resource_id
          AND u.disabled_at IS NOT NULL;
      ELSE RAISE EXCEPTION 'unbound audit event'; END IF;
      IF matches <> 1 THEN RAISE EXCEPTION 'reverse business audit mismatch'; END IF;
      RETURN NEW;
    END $$
    """)
    )
    conn.execute(
        text("""
    CREATE CONSTRAINT TRIGGER reverse_business_audit AFTER INSERT ON audit_events
    DEFERRABLE INITIALLY DEFERRED FOR EACH ROW
    EXECUTE FUNCTION validate_reverse_event()
    """)
    )


def downgrade():
    raise RuntimeError("destructive downgrade refused")
