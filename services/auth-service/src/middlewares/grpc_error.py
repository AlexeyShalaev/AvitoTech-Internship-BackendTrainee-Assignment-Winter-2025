import grpc
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response


class GRPCErrorHandlingMiddleware(BaseHTTPMiddleware):
    _map_grpc_to_http_status = {
        grpc.StatusCode.OK: 200,
        grpc.StatusCode.CANCELLED: 499,
        grpc.StatusCode.UNKNOWN: 500,
        grpc.StatusCode.INVALID_ARGUMENT: 400,
        grpc.StatusCode.DEADLINE_EXCEEDED: 504,
        grpc.StatusCode.NOT_FOUND: 404,
        grpc.StatusCode.ALREADY_EXISTS: 409,
        grpc.StatusCode.PERMISSION_DENIED: 403,
        grpc.StatusCode.RESOURCE_EXHAUSTED: 429,
        grpc.StatusCode.FAILED_PRECONDITION: 412,
        grpc.StatusCode.ABORTED: 409,
        grpc.StatusCode.OUT_OF_RANGE: 400,
        grpc.StatusCode.UNIMPLEMENTED: 501,
        grpc.StatusCode.INTERNAL: 500,
        grpc.StatusCode.UNAVAILABLE: 503,
        grpc.StatusCode.DATA_LOSS: 500,
        grpc.StatusCode.UNAUTHENTICATED: 401,
    }

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            return await call_next(request)
        except grpc.RpcError as e:
            http_status = self._map_grpc_to_http_status[e.code()]
            details = e.details()

            if (
                (details.startswith('"') and details.endswith('"'))
                or (details.startswith("{") and details.endswith("}"))
                or (details.startswith("[") and details.endswith("]"))
                or details in {"null", "true", "false"}
                or details.isdigit()
            ):
                return Response(
                    content=details,
                    media_type="application/json",
                    status_code=http_status,
                )

            return PlainTextResponse(status_code=http_status, content=details)
