from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp
from uvicorn.protocols.utils import get_path_with_query_string

from .processing_time import processing_time_counter


class LoggingMiddleware(BaseHTTPMiddleware):
    """ASGI logging middleware."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            with processing_time_counter() as processing_time_ms:
                response = await call_next(request)
        except BaseException as exception:
            logger.exception("Uncaught exception")
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            raise exception from None
        else:
            status_code = response.status_code
        finally:
            path = get_path_with_query_string(request.scope)
            client = {"real_ip": "unknown"}
            if request.client is not None:
                client["real_ip"] = client["connection_ip"] = request.client.host
            if forwarded_ip := request.headers.get("X-Forwarded-For-Y"):
                client["real_ip"] = client["forwarded_ip"] = forwarded_ip

            http_method = request.method
            http_version = request.scope["http_version"]
            logger.info(
                {
                    "http": {
                        "method": http_method,
                        "path": path,
                        "version": http_version,
                        "status_code": status_code,
                    },
                    "client": client,
                    "duration_ms": processing_time_ms.get(),
                }
            )
        return response
