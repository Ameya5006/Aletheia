"""Forward-compatible immutable case snapshots and audited save membership."""

from alembic import op

revision = "0004_case_input"
down_revision = "0003_integrity"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE prediction_events ALTER COLUMN explanation_ref_id DROP NOT NULL"
    )
    op.execute(
        "ALTER TABLE prediction_events ADD COLUMN inputs jsonb, "
        "ADD COLUMN result_snapshot jsonb"
    )
    op.execute(
        "ALTER TABLE prediction_events DROP CONSTRAINT prediction_events_case_id_check"
    )
    op.execute("""ALTER TABLE prediction_events ADD CHECK
      (case_id IN ('synthetic-discharge-v1','entered-case-v1')),
      ADD CONSTRAINT case_snapshot CHECK (
        (case_id='synthetic-discharge-v1' AND inputs IS NULL
         AND result_snapshot IS NULL AND explanation_ref_id IS NOT NULL)
        OR (case_id='entered-case-v1' AND inputs IS NOT NULL
            AND result_snapshot IS NOT NULL
            AND explanation_ref_id IS NULL AND jsonb_typeof(inputs)='object'
            AND jsonb_typeof(result_snapshot)='object'
            AND result_snapshot ?& ARRAY['inputs','probability','threshold',
                'class_at_threshold','schema_version']
            AND result_snapshot->'inputs'=inputs
            AND (result_snapshot->>'probability')::float8=probability
            AND (result_snapshot->>'threshold')::float8=threshold
            AND (result_snapshot->>'class_at_threshold')::integer=class_at_threshold
            AND result_snapshot->>'schema_version'='case-result-v1'))""")
    op.execute("""CREATE TABLE saved_analyses (
      id uuid PRIMARY KEY REFERENCES prediction_events(id) ON DELETE RESTRICT,
      actor_id uuid NOT NULL REFERENCES subjects(id) ON DELETE RESTRICT,
      created_at timestamptz NOT NULL DEFAULT now(),
      audit_event_id uuid NOT NULL UNIQUE REFERENCES audit_events(id) ON DELETE RESTRICT
    )""")
    op.execute("GRANT SELECT,INSERT ON saved_analyses TO aletheia_runtime")
    op.execute("""CREATE TRIGGER immutable_history
      BEFORE UPDATE OR DELETE ON saved_analyses
      FOR EACH ROW EXECUTE FUNCTION reject_history_mutation()""")
    op.execute("ALTER TABLE audit_events DROP CONSTRAINT audit_events_event_type_check")
    op.execute("""ALTER TABLE audit_events ADD CHECK (event_type IN (
      'initial_administrator_bootstrap','role_granted','role_revoked','subject_disabled',
      'prediction_created','review_created','release_approved','release_revoked',
      'release_activated','release_rolled_back','prediction_saved'))""")
    op.execute("""CREATE OR REPLACE FUNCTION validate_event_scope()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        IF NEW.event_type NOT IN
          ('prediction_created','review_created','prediction_saved')
          AND NOT has_table_privilege(current_user,'subject_roles','INSERT')
        THEN RAISE EXCEPTION 'operator event privilege required'; END IF;
        IF EXISTS (SELECT 1 FROM jsonb_object_keys(NEW.payload) k WHERE k NOT IN
          ('role','attribution','prediction_id','revision','decision','reason_code',
           'case_id','probability','model_version','version','release_sha256'))
        THEN RAISE EXCEPTION 'unapproved audit payload'; END IF;
        RETURN NEW;
      END $$""")
    # The original reverse validator still governs every original event type.
    op.execute("DROP TRIGGER reverse_business_audit ON audit_events")
    op.execute("""CREATE CONSTRAINT TRIGGER reverse_business_audit
      AFTER INSERT ON audit_events
      DEFERRABLE INITIALLY DEFERRED FOR EACH ROW
      WHEN (NEW.event_type <> 'prediction_saved')
      EXECUTE FUNCTION validate_reverse_event()""")
    op.execute("""CREATE FUNCTION validate_saved_analysis()
      RETURNS trigger LANGUAGE plpgsql AS $$
      DECLARE valid integer; BEGIN
        IF TG_TABLE_NAME='saved_analyses' THEN
          SELECT count(*) INTO valid FROM audit_events e
            JOIN prediction_events p ON p.id=NEW.id
            WHERE e.id=NEW.audit_event_id AND e.event_type='prediction_saved'
              AND e.resource_id=NEW.id AND e.actor_id=NEW.actor_id
              AND p.actor_id=NEW.actor_id AND p.case_id='entered-case-v1'
              AND e.payload->>'prediction_id'=NEW.id::text;
        ELSE
          SELECT count(*) INTO valid FROM saved_analyses a
            JOIN prediction_events p ON p.id=a.id
            WHERE a.audit_event_id=NEW.id AND a.id=NEW.resource_id
              AND a.actor_id=NEW.actor_id AND p.actor_id=a.actor_id
              AND p.case_id='entered-case-v1'
              AND NEW.payload->>'prediction_id'=a.id::text;
        END IF;
        IF valid<>1 THEN RAISE EXCEPTION 'saved analysis audit mismatch'; END IF;
        RETURN NEW;
      END $$""")
    op.execute("""CREATE CONSTRAINT TRIGGER saved_analysis_audit
      AFTER INSERT ON saved_analyses DEFERRABLE INITIALLY DEFERRED FOR EACH ROW
      EXECUTE FUNCTION validate_saved_analysis()""")
    op.execute("""CREATE CONSTRAINT TRIGGER reverse_saved_audit
      AFTER INSERT ON audit_events DEFERRABLE INITIALLY DEFERRED FOR EACH ROW
      WHEN (NEW.event_type='prediction_saved')
      EXECUTE FUNCTION validate_saved_analysis()""")


def downgrade():
    raise RuntimeError("destructive downgrade refused")
