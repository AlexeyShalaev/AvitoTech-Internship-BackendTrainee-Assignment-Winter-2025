import time
import typing as tp
from contextlib import contextmanager
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

PROCESSING_TIME_HEADER = "X-Processing-Time"

_processing_time: ContextVar[int | None] = ContextVar("processing_time", default=None)


class ProcessingTimeMiddelware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        with processing_time_counter() as total_time_ms:
            response = await call_next(request)
        response.headers[PROCESSING_TIME_HEADER] = str(total_time_ms.get())
        return response


@contextmanager
def processing_time_counter() -> tp.Iterator[ContextVar]:
    start_time = time.perf_counter_ns()
    try:
        yield _processing_time
    finally:
        if _processing_time.get() is None:
            _processing_time.set((time.perf_counter_ns() - start_time) // 1_000_000)
