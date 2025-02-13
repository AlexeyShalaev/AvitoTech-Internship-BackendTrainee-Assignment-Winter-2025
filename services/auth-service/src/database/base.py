from alembic import command
from alembic.config import Config
from loguru import logger


def run_migrations(alembic_cfg_path: str, revision: str = "head") -> None:
    try:
        alembic_cfg = Config(alembic_cfg_path)
        command.upgrade(alembic_cfg, revision)
        logger.info("Database migrated.")
    except Exception as e:
        logger.error(f"An error occurred while migrating the database: {e}")
