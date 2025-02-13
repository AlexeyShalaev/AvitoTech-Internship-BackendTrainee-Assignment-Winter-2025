"""
Test can find cases, when you've changed something in migration and forgot
about models for some reason (or vice versa).
"""

from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine

from src.models import Base


def test_migrations_up_to_date(pg_url):
    engine = create_engine(str(pg_url))
    migration_ctx = MigrationContext.configure(engine.connect())
    diff = compare_metadata(migration_ctx, Base.metadata)
    assert not diff
