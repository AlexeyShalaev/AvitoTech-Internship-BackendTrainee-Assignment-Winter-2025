from jose import JWTError, jwt
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app: ASGIApp, 
        jwt_secret: str, 
        jwt_algorithms: list[str], 
        jwt_issuer: str | None = None
    ) -> None:
        super().__init__(app)
        self._jwt_secret = jwt_secret
        self._jwt_algorithms = jwt_algorithms
        self._jwt_issuer = jwt_issuer

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        scope["user"] = await self.authenticate(scope=scope)
        await self.app(scope, receive, send)

    async def authenticate(self, scope: Scope):
        try:
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode()

            if not auth_header.startswith("Bearer "):
                logger.debug("No valid Authorization header found")
                return None

            token = auth_header.split("Bearer ")[1]

            decoded = jwt.decode(
                token,
                self._jwt_secret,
                algorithms=self._jwt_algorithms,
                options={"verify_aud": False},
                issuer=self._jwt_issuer
            )
            return decoded
        except (ValueError, UnicodeDecodeError, JWTError) as e:
            logger.debug(f"Failed to decode token: {e}")
            return None
