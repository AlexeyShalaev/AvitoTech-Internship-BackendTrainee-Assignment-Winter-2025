import uuid
import pytest
import grpc
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.coins import CoinsService
from src.models.account import Account
from src.models.transaction import Transaction, TransactionType, TransactionStatus
from src.core.exceptions import GrpcException
import coins_pb2


@pytest.fixture
def coins_service(session: AsyncSession):
    return CoinsService(session)


@pytest.mark.asyncio
async def test_transfer_funds_success(coins_service, session):
    """Тест успешного перевода средств между пользователями"""

    from_user = Account(id=uuid.uuid4(), username="alice", balance_whole=10, balance_fraction=50)
    to_user = Account(id=uuid.uuid4(), username="bob", balance_whole=5, balance_fraction=25)

    session.add_all([from_user, to_user])
    await session.commit()

    request = coins_pb2.TransferFundsRequest(
        idempotency_key=str(uuid.uuid4()),
        from_username="alice",
        to_username="bob",
        amount_whole=2,
        amount_fraction=75,
    )

    response = await coins_service.TransferFunds(request)

    assert response.status == coins_pb2.Status.COMPLETED

    updated_from_user = await session.get(Account, from_user.id)
    updated_to_user = await session.get(Account, to_user.id)

    assert updated_from_user.balance_whole == 7
    assert updated_from_user.balance_fraction == 75
    assert updated_to_user.balance_whole == 8
    assert updated_to_user.balance_fraction == 0


@pytest.mark.asyncio
async def test_transfer_funds_insufficient_funds(coins_service, session):
    """Тест недостатка средств при переводе"""

    from_user = Account(id=uuid.uuid4(), username="alice", balance_whole=1, balance_fraction=50)
    to_user = Account(id=uuid.uuid4(), username="bob", balance_whole=5, balance_fraction=25)

    session.add_all([from_user, to_user])
    await session.commit()

    request = coins_pb2.TransferFundsRequest(
        idempotency_key=str(uuid.uuid4()),
        from_username="alice",
        to_username="bob",
        amount_whole=2,
        amount_fraction=0,
    )

    with pytest.raises(GrpcException) as exc_info:
        await coins_service.TransferFunds(request)

    assert exc_info.value.status_code == grpc.StatusCode.FAILED_PRECONDITION
    assert exc_info.value.details == CoinsService.ProblemCode.INSUFFICIENT_FUNDS


@pytest.mark.asyncio
async def test_transfer_funds_user_not_found(coins_service):
    """Тест перевода средств на несуществующего пользователя"""

    request = coins_pb2.TransferFundsRequest(
        idempotency_key=str(uuid.uuid4()),
        from_username="alice",
        to_username="bob",
        amount_whole=1,
        amount_fraction=50,
    )

    with pytest.raises(GrpcException) as exc_info:
        await coins_service.TransferFunds(request)

    assert exc_info.value.status_code == grpc.StatusCode.NOT_FOUND
    assert exc_info.value.details == CoinsService.ProblemCode.USER_NOT_FOUND


@pytest.mark.asyncio
async def test_charge_user_success(coins_service, session):
    """Тест успешного списания средств"""

    user = Account(id=uuid.uuid4(), username="alice", balance_whole=10, balance_fraction=50)

    session.add(user)
    await session.commit()

    request = coins_pb2.ChargeUserRequest(
        idempotency_key=str(uuid.uuid4()),
        username="alice",
        amount_whole=3,
        amount_fraction=75,
    )

    response = await coins_service.ChargeUser(request)

    assert response.status == coins_pb2.Status.COMPLETED

    updated_user = await session.get(Account, user.id)
    assert updated_user.balance_whole == 6
    assert updated_user.balance_fraction == 75


@pytest.mark.asyncio
async def test_credit_user_success(coins_service, session):
    """Тест успешного пополнения баланса"""

    user = Account(id=uuid.uuid4(), username="alice", balance_whole=10, balance_fraction=50)

    session.add(user)
    await session.commit()

    request = coins_pb2.CreditUserRequest(
        idempotency_key=str(uuid.uuid4()),
        username="alice",
        amount_whole=2,
        amount_fraction=60,
    )

    response = await coins_service.CreditUser(request)

    assert response.status == coins_pb2.Status.COMPLETED

    updated_user = await session.get(Account, user.id)
    assert updated_user.balance_whole == 13
    assert updated_user.balance_fraction == 10


@pytest.mark.asyncio
async def test_get_balance_success(coins_service, session):
    """Тест получения баланса"""

    user = Account(id=uuid.uuid4(), username="alice", balance_whole=15, balance_fraction=30)

    session.add(user)
    await session.commit()

    request = coins_pb2.GetBalanceRequest(username="alice")
    response = await coins_service.GetBalance(request)

    assert response.username == "alice"
    assert response.balance_whole == 15
    assert response.balance_fraction == 30


@pytest.mark.asyncio
async def test_get_balance_user_not_found(coins_service):
    """Тест получения баланса для несуществующего пользователя"""

    request = coins_pb2.GetBalanceRequest(username="unknown")

    with pytest.raises(GrpcException) as exc_info:
        await coins_service.GetBalance(request)

    assert exc_info.value.status_code == grpc.StatusCode.NOT_FOUND
    assert exc_info.value.details == CoinsService.ProblemCode.USER_NOT_FOUND


@pytest.mark.asyncio
async def test_get_transaction_history(coins_service, session):
    """Тест получения истории транзакций"""

    user = Account(id=uuid.uuid4(), username="alice", balance_whole=15, balance_fraction=30)
    transaction = Transaction(
        id=uuid.uuid4(),
        from_account_id=user.id,
        to_account_id=None,
        amount_whole=5,
        amount_fraction=25,
        type=TransactionType.PAYMENT,
        status=TransactionStatus.COMPLETED,
    )

    session.add_all([user, transaction])
    await session.commit()

    request = coins_pb2.GetTransactionHistoryRequest(username="alice")
    response = await coins_service.GetTransactionHistory(request)

    assert len(response.transactions) == 1
    assert response.transactions[0].transaction_id == str(transaction.id)
    assert response.transactions[0].amount_whole == 5
    assert response.transactions[0].amount_fraction == 25
    assert response.transactions[0].status == coins_pb2.Status.COMPLETED
