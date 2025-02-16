import uuid

import coins_pb2


class MockCoinsServiceClient:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def charge_user(
        self,
        username: str,
        amount_whole: int,
        amount_fraction: int,
        idempotency_key: str,
    ) -> coins_pb2.ChargeUserResponse:
        return coins_pb2.ChargeUserResponse(
            transaction_id=str(uuid.uuid4()),
            status=coins_pb2.Status.COMPLETED,
        )
