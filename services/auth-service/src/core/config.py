from enum import StrEnum

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class WorkingMode(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    MODE: WorkingMode = WorkingMode.DEVELOPMENT
    DEBUG: bool = MODE != WorkingMode.PRODUCTION
    VERSION: str = "0.0.1"

    DOCS_PATH: str = "/docs"
    OPENAPI_PATH: str = "/openapi.json"

    API_PATH: str = "/api"
    HEALTH_PATH: str = "/health"
    METRICS_PATH: str = "/metrics"

    PORT: int = 8080

    ALEMBIC_CFG: str = "alembic.ini"
    DATABASE_URL: SecretStr = SecretStr("postgresql+asyncpg://postgres:postgres@localhost:15432/postgres")
    DATABASE_ECHO: bool = False

    CORS_ALLOW_ORIGINS: list[str] = ["*"]
    
    JWT_SECRET_KEY: SecretStr = "secret"
    JWT_ALGORITHM: SecretStr = "HS256"

    ACCESS_TOKEN_EXPIRES_IN: int = 1200000
    REFRESH_TOKEN_EXPIRES_IN: int = 2592000
    
    USER_SERVICE_HOST: str = "user-service:50051"
    USER_SERVICE_TIMEOUT: float = 0.1


settings = Settings()
