import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from loguru import logger


class IdempotencyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        headers = dict(scope.get("headers", []))
        idempotency_key = headers.get(b"x-idempotency-key")

        if not idempotency_key:
            new_key = str(uuid.uuid4())
            headers[b"x-idempotency-key"] = new_key.encode()
            logger.debug(f"Generated new X-Idempotency-Key: {new_key}")

        # Обновляем scope с измененными заголовками
        scope["headers"] = list(headers.items())

        await self.app(scope, receive, send)
