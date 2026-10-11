"""Owner-only explicit migrations; database URI comes from operator environment."""

import os

from alembic import context
from sqlalchemy import create_engine

from aletheia.application.schema import metadata

engine = create_engine(os.environ["ALETHEIA_MIGRATION_URL"])
with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=metadata)
    with context.begin_transaction():
        context.run_migrations()
