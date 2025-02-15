import coins_pb2
import coins_pb2_grpc
import grpc
from src.core.config import settings


class CoinsServiceClient:
    def __init__(self, timeout: float = settings.COINS_SERVICE_TIMEOUT) -> None:
        self._timeout: float = timeout
        self._channel = None
        self._stub = None

    async def __aenter__(self):
        self._channel = grpc.aio.insecure_channel(settings.COINS_SERVICE_HOST)
        self._stub = coins_pb2_grpc.CoinsServiceStub(self._channel)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._channel.close()

    async def charge_user(
        self,
        username: str,
        amount_whole: int,
        amount_fraction: int,
        idempotency_key: str,
    ) -> coins_pb2.ChargeUserResponse:
        return await self._stub.ChargeUser(
            coins_pb2.ChargeUserRequest(
                username=username,
                amount_whole=amount_whole,
                amount_fraction=amount_fraction,
                idempotency_key=idempotency_key,
            ),
            timeout=self._timeout,
        )
