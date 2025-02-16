import uuid

import coins_pb2
import merch_pb2
import pytest
import pytest_asyncio
from src.services.merch import MerchService


class TestBuyMerch:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_method(self, pool):
        self.pool = pool
        self.service = MerchService(self.pool)

    @pytest.mark.asyncio
    async def test_successful_buying(self):
        request = merch_pb2.BuyMerchRequest(
            username="user",
            merch_name="book",
            idempotency_key=str(uuid.uuid4()),
        )
        response = await self.service.BuyMerch(request)

        assert response.status == coins_pb2.Status.Name(coins_pb2.Status.COMPLETED)
