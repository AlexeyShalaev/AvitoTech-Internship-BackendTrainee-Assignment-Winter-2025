from enum import StrEnum

from pydantic_settings import BaseSettings


class WorkingMode(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    MODE: WorkingMode = WorkingMode.DEVELOPMENT
    DEBUG: bool = MODE != WorkingMode.PRODUCTION
    ALEMBIC_CFG: str = "alembic.ini"
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:15432/postgres"
    )
    DATABASE_ECHO: bool = False

    REDIS_URL: str = "redis://localhost:6379/0"

    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_CLIENT_ID: str = "coins-service"
    KAFKA_TX_TOPIC_NAME: str = "transactions"
    KAFKA_USER_TOPIC_NAME: str = "user-events"


settings = Settings()
