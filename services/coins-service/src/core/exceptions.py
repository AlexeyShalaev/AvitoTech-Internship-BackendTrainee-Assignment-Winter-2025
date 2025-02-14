"""Exceptions for ExceptionToStatusInterceptor.

See https://grpc.github.io/grpc/core/md_doc_statuscodes.html for the source of truth
on status code meanings.
"""

from dataclasses import asdict, dataclass
from enum import Enum

from grpc import StatusCode

try:
    import orjson as json

    def json_dumps(data):
        return json.dumps(data).decode()

except ImportError:
    import json

    def json_dumps(data):
        return json.dumps(data)


@dataclass
class Details:
    code: str
    default: str | None = None
    kwargs: dict | None = None

    @staticmethod
    def from_enum(enum: Enum, **kwargs):
        return Details(code=enum.name, default=enum.value, kwargs=kwargs)

    def __str__(self):
        return self.default.format(**self.kwargs) if self.kwargs else self.default


class GrpcException(Exception):
    """Base class for gRPC exceptions."""

    status_code: StatusCode = StatusCode.UNKNOWN
    details: str = "Unknown exception occurred"

    def __init__(
        self,
        status_code: StatusCode | None = None,
        details: str | dict | Details | None = None,
    ):
        if status_code is not None:
            if status_code == StatusCode.OK:
                raise ValueError("The status code for an exception cannot be OK")
            self.status_code = status_code

        if details is not None:
            if isinstance(details, Details):
                self.details = json_dumps(asdict(details))
            elif isinstance(details, str):
                self.details = json_dumps(details)

    def __repr__(self) -> str:
        """Show the status code and details.

        Returns:
            A string displaying the class name, status code, and details.
        """
        clsname = self.__class__.__name__
        sc = self.status_code.name
        return f"{clsname}(status_code={sc}, details={self.details!r})"

    @property
    def status_string(self):
        """Return status_code as a string.

        Returns:
            The status code as a string.

        Example:
            >>> GrpcException(status_code=StatusCode.NOT_FOUND).status_string
            'NOT_FOUND'
        """
        return self.status_code.name
