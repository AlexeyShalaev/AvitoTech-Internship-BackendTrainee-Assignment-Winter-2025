import pytest
import pytest_asyncio
import grpc
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.coins import CoinsService
from src.models.account import Account
import coins_pb2


class TestChargeUser:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_method(self, session: AsyncSession):
        self.session = session
        self.service = CoinsService(self.session)

        self.user = Account(
            id=uuid.uuid4(), user_id=uuid.uuid4(), username="user1", balance_whole=50, balance_fraction=30
        )
        self.session.add(self.user)
        await self.session.commit()

    @pytest.mark.asyncio
    async def test_successful_charge(self):
        request = coins_pb2.ChargeUserRequest(
            username="user1",
            amount_whole=10,
            amount_fraction=20,
            idempotency_key=str(uuid.uuid4()),
        )
        response = await self.service.ChargeUser(request)
        
        assert response.status == coins_pb2.Status.COMPLETED

        updated_user = await self.session.get(Account, self.user.id)
        assert updated_user.balance_whole == 40
        assert updated_user.balance_fraction == 10
