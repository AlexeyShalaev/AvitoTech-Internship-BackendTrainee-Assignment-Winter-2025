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

    CORS_ALLOW_ORIGINS: list[str] = ["*"]

    JWT_SECRET_KEY: SecretStr = "secret"
    JWT_ALGORITHM: SecretStr = "HS256"

    USER_SERVICE_HOST: str = "user-service:50051"
    USER_SERVICE_TIMEOUT: float = 0.1

    COINS_SERVICE_HOST: str = "coins-service:50051"
    COINS_SERVICE_TIMEOUT: float = 0.1

    MERCH_SERVICE_HOST: str = "merch-service:50051"
    MERCH_SERVICE_TIMEOUT: float = 0.1

    INFO_SERVICE_HOST: str = "http://info-service:8080"
    INFO_SERVICE_TIMEOUT: float = 0.1


settings = Settings()
