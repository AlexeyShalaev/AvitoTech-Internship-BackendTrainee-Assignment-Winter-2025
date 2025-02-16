from enum import StrEnum

from pydantic_settings import BaseSettings


class WorkingMode(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    MODE: WorkingMode = WorkingMode.DEVELOPMENT
    DEBUG: bool = MODE != WorkingMode.PRODUCTION

    DATABASE_HOST: str = "grpc://localhost:2136"
    DATABASE_NAME: str = "/local"

    COINS_SERVICE_HOST: str = "coins-service:50051"
    COINS_SERVICE_TIMEOUT: float = 0.1

    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_CLIENT_ID: str = "merch-service"
    KAFKA_MERCH_TOPIC_NAME: str = "merch"


settings = Settings()
