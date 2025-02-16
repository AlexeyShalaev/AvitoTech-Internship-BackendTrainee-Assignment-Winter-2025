import uuid

import coins_pb2
import grpc
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.account import Account
from src.services.coins import CoinsService


class TestGetBalance:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_method(self, session: AsyncSession):
        self.session = session
        self.service = CoinsService(self.session)

        self.user = Account(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            username="user1",
            balance_whole=100,
            balance_fraction=50,
        )
        self.session.add(self.user)
        await self.session.commit()

    @pytest.mark.asyncio
    async def test_get_balance_success(self):
        request = coins_pb2.GetBalanceRequest(username="user1")
        response = await self.service.GetBalance(request)

        assert response.username == "user1"
        assert response.balance_whole == 100
        assert response.balance_fraction == 50
