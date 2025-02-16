from typing import Any, Callable

import grpc
from grpc_interceptor import AsyncServerInterceptor
from src.core.exceptions import GrpcException


class ExceptionHandler(AsyncServerInterceptor):
    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ):
        try:
            return await method(request_or_iterator, context)
        except GrpcException as e:
            return await context.abort(e.status_code, e.details)
