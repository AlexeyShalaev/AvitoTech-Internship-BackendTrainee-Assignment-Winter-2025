import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator
from src.core.config import WorkingMode, settings
from src.middlewares import (
    AuthenticationMiddleware,
    AuthorizationMiddleware,
    GRPCErrorHandlingMiddleware,
    IdempotencyMiddleware,
    LoggingMiddleware,
    ProcessingTimeMiddelware,
)
from src.routers import api_router
from src.routers.health import router as health_router


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:

    instrumentator.expose(
        application, include_in_schema=False, endpoint=settings.METRICS_PATH
    )

    logger.info("Application started.")

    yield


def get_app() -> FastAPI:
    """Creates application and all dependable objects."""
    description = "API Gateway"

    tags_metadata = [
        {
            "name": "API Gateway",
            "description": "API for API Gateway",
        },
    ]

    application = FastAPI(
        debug=settings.DEBUG,
        title=f"API Gateway {settings.MODE}",
        description=description,
        docs_url=settings.DOCS_PATH,
        openapi_url=settings.OPENAPI_PATH,
        version=settings.VERSION,
        openapi_tags=tags_metadata,
        lifespan=lifespan,
    )

    application.include_router(health_router)
    application.include_router(api_router)

    application.add_middleware(GRPCErrorHandlingMiddleware)

    application.add_middleware(IdempotencyMiddleware)

    allowed_path_prefixes = [
        settings.HEALTH_PATH,
        settings.METRICS_PATH,
        settings.OPENAPI_PATH,
        settings.DOCS_PATH,
    ]

    application.add_middleware(
        AuthorizationMiddleware,
        allowed_paths=[],
        allowed_path_prefixes=allowed_path_prefixes,
    )

    application.add_middleware(
        AuthenticationMiddleware,
        jwt_secret=settings.JWT_SECRET_KEY.get_secret_value(),
        jwt_algorithms=[settings.JWT_ALGORITHM.get_secret_value()],
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)
    application.add_middleware(ProcessingTimeMiddelware)
    application.add_middleware(LoggingMiddleware)

    return application


app = get_app()

instrumentator = Instrumentator(
    should_instrument_requests_inprogress=True,
    excluded_handlers=[
        settings.METRICS_PATH,
        settings.OPENAPI_PATH,
        settings.DOCS_PATH,
        settings.HEALTH_PATH,
    ],
).instrument(app, metric_namespace="auth_service")


def main() -> None:
    import uvicorn

    workers = 1
    cpu_cnt = os.cpu_count()
    if settings.MODE == WorkingMode.PRODUCTION and cpu_cnt is not None:
        workers = cpu_cnt * 2 + 1

    logger.info(f"Running app with {workers} workers.")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        log_level=logging.getLevelName("DEBUG" if settings.DEBUG else "INFO"),
        workers=workers,
        log_config=None,
    )


if __name__ == "__main__":
    main()
