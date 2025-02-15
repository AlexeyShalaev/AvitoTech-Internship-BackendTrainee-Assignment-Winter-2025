import uuid

import coins_pb2
import grpc
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.account import Account
from src.services.coins import CoinsService


class TestGetTransactionHistory:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_method(self, session: AsyncSession):
        self.session = session
        self.service = CoinsService(self.session)

        self.user = Account(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            username="user1",
            balance_whole=100,
            balance_fraction=0,
        )
        self.session.add(self.user)
        await self.session.commit()

    @pytest.mark.asyncio
    async def test_get_transaction_history(self):
        request = coins_pb2.GetTransactionHistoryRequest(username="user1")
        response = await self.service.GetTransactionHistory(request)

        assert len(response.transactions) == 0
