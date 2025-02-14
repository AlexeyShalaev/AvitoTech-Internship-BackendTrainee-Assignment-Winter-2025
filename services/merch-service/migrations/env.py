# Dynamically import all modules in the src.models package
import importlib
import pkgutil
from logging.config import fileConfig

import src.models
import sqlalchemy as sa
from alembic import context
from alembic.ddl.impl import DefaultImpl
from sqlalchemy import engine_from_config, pool
from src.models import Base


package = src.models
for _, module_name, _ in pkgutil.iter_modules(package.__path__):
    importlib.import_module(f"{package.__name__}.{module_name}")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
try:
    # running in docker with os env
    from src.core.config import settings

    DATABASE_HOST = settings.DATABASE_HOST
    DATABASE_NAME = settings.DATABASE_NAME
except:
    # running locally with file env
    import os
    from pathlib import Path

    from dotenv import load_dotenv

    load_dotenv(dotenv_path=Path("../../config/alembic.env"))
    DATABASE_HOST = os.environ["DATABASE_HOST"]
    DATABASE_NAME = os.environ["DATABASE_NAME"]
finally:
    DATABASE_URL = f"yql+ydb://{DATABASE_HOST}/{DATABASE_NAME}"
    config.set_main_option("sqlalchemy.url", DATABASE_URL)


class YDBImpl(DefaultImpl):
    __dialect__ = "yql"
    

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        ctx = context.get_context()
        ctx._version = sa.Table(  # noqa: SLF001
            ctx.version_table,
            sa.MetaData(),
            sa.Column("version_num", sa.String(32), nullable=False),
            sa.Column("id", sa.Integer(), nullable=True, primary_key=True),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
