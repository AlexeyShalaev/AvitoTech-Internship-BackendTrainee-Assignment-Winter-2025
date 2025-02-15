import grpc
import user_pb2
import user_pb2_grpc
from src.core.config import settings


class UserServiceClient:
    def __init__(self, timeout: float = settings.USER_SERVICE_TIMEOUT) -> None:
        self._timeout: float = timeout
        self._channel = None
        self._stub = None

    async def __aenter__(self):
        self._channel = grpc.aio.insecure_channel(settings.USER_SERVICE_HOST)
        self._stub = user_pb2_grpc.UserServiceStub(self._channel)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._channel.close()

    async def create_if_not_exists(
        self, username: str, password: str
    ) -> user_pb2.CreateIfNotExistsResponse:
        return await self._stub.CreateIfNotExists(
            user_pb2.CreateIfNotExistsRequest(username=username, password=password),
            timeout=self._timeout,
        )

    async def get_by_id(self, user_id: str) -> user_pb2.GetUserByIdResponse:
        return await self._stub.GetUserById(
            user_pb2.GetUserByIdRequest(id=user_id), timeout=self._timeout
        )
