import pytest
import pytest_asyncio
import grpc
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.merch import MerchService
from src.models.merch import Merch
import merch_pb2
import coins_pb2


class TestBuyMerch:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_method(self, session: AsyncSession):
        self.session = session
        self.service = MerchService(self.session)

        self.merch = Merch(
            id=uuid.uuid4(), name="test", price=100
        )
        self.session.add(self.merch)
        await self.session.commit()

    @pytest.mark.asyncio
    async def test_successful_buying(self):
        request = merch_pb2.BuyMerchRequest(
            username="user",
            merch_name=self.merch.name,
            idempotency_key=str(uuid.uuid4()),
        )
        response = await self.service.BuyMerch(request)
        
        assert response.status == coins_pb2.Status.COMPLETED
