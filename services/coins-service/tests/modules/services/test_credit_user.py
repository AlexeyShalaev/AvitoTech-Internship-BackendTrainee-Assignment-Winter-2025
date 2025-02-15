import uuid

import coins_pb2
import grpc
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.account import Account
from src.services.coins import CoinsService


class TestCreditUser:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_method(self, session: AsyncSession):
        self.session = session
        self.service = CoinsService(self.session)

        self.user = Account(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            username="user1",
            balance_whole=30,
            balance_fraction=70,
        )
        self.session.add(self.user)
        await self.session.commit()

    @pytest.mark.asyncio
    async def test_successful_credit(self):
        request = coins_pb2.CreditUserRequest(
            username="user1",
            amount_whole=20,
            amount_fraction=40,
            idempotency_key=str(uuid.uuid4()),
        )
        response = await self.service.CreditUser(request)

        assert response.status == coins_pb2.Status.COMPLETED

        updated_user = await self.session.get(Account, self.user.id)
        assert updated_user.balance_whole == 51
        assert updated_user.balance_fraction == 10  # 70 + 40 → 110 → 1 whole + 10
