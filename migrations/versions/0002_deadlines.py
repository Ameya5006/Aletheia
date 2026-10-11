"""Bound database work for runtime sessions (also tests previous-to-head)."""

from alembic import op

revision = "0002_deadlines"
down_revision = "0001_backend"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER ROLE aletheia_runtime SET statement_timeout = '2s'")
    op.execute("ALTER ROLE aletheia_runtime SET lock_timeout = '2s'")


def downgrade():
    raise RuntimeError("destructive downgrade refused")
