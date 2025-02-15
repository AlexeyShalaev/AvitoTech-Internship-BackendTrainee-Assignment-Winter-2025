import typing as tp

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.types import ASGIApp


class AuthorizationMiddleware(BaseHTTPMiddleware):
    """ASGI middleware with basic authorization (deny any unauthenticated request)."""

    def __init__(
        self,
        app: ASGIApp,
        allowed_paths: tp.Iterable[str] = (),
        allowed_path_prefixes: tp.Iterable[str] = (),
    ) -> None:
        super().__init__(app)
        self.allowed_paths = frozenset(allowed_paths)
        self.allowed_path_prefixes = frozenset(allowed_path_prefixes)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if not self.is_allowed_path(request) and (
            "user" not in request.scope or not request.user
        ):
            return Response(status_code=HTTP_401_UNAUTHORIZED, content="Unauthorized")
        return await call_next(request)

    def is_allowed_path(self, request: Request) -> bool:
        if request["path"] in self.allowed_paths:
            return True
        for prefix in self.allowed_path_prefixes:
            if request["path"].startswith(prefix):
                return True
        return False
