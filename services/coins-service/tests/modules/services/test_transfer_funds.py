import pytest
import pytest_asyncio
import grpc
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.coins import CoinsService
from src.models.account import Account
import coins_pb2


class TestTransferFunds:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_method(self, session: AsyncSession):
        self.session = session
        self.service = CoinsService(self.session)

        # Создаем два аккаунта с user_id
        self.from_user = Account(
            id=uuid.uuid4(), user_id=uuid.uuid4(), username="user1", balance_whole=100, balance_fraction=50
        )
        self.to_user = Account(
            id=uuid.uuid4(), user_id=uuid.uuid4(), username="user2", balance_whole=50, balance_fraction=25
        )

        self.session.add_all([self.from_user, self.to_user])
        await self.session.commit()

    @pytest.mark.asyncio
    async def test_successful_transfer(self):
        request = coins_pb2.TransferFundsRequest(
            from_username="user1",
            to_username="user2",
            amount_whole=20,
            amount_fraction=30,
            idempotency_key=str(uuid.uuid4()),
        )
        response = await self.service.TransferFunds(request)
        
        assert response.status == coins_pb2.Status.COMPLETED

        updated_from = await self.session.get(Account, self.from_user.id)
        updated_to = await self.session.get(Account, self.to_user.id)

        assert updated_from.balance_whole == 80
        assert updated_from.balance_fraction == 20
        assert updated_to.balance_whole == 70
        assert updated_to.balance_fraction == 55
