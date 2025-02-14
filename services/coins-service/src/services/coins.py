import uuid
from enum import StrEnum

import coins_pb2
import grpc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from src.database import redis_client
from src.database.kafka import KafkaProducerSingleton
from src.core.config import settings
from src.core.exceptions import GrpcException
from src.models.account import Account
from src.models.transaction import Transaction, TransactionType, TransactionStatus


class CoinsService:
    class ProblemCode(StrEnum):
        USER_NOT_FOUND = "User not found"
        INSUFFICIENT_FUNDS = "Insufficient funds"
        DUPLICATE_REQUEST = "Duplicate request"

    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def _check_idempotency(self, idempotency_key: str) -> bool:
        """ Проверка идемпотентности операции """
        exists = await redis_client.exists(idempotency_key)
        if exists:
            logger.info(f"Idempotency key {idempotency_key} already processed")
            return True
        await redis_client.set(idempotency_key, "processed", ex=3600)
        return False

    async def _publish_transaction(self, transaction: Transaction):
        message = {
            "transaction_id": str(transaction.id),
            "from_account_id": str(transaction.from_account_id) if transaction.from_account_id else None,
            "to_account_id": str(transaction.to_account_id) if transaction.to_account_id else None,
            "amount_whole": transaction.amount_whole,
            "amount_fraction": transaction.amount_fraction,
            "type": transaction.type.value,
            "status": transaction.status.value,
        }
        try:
            await KafkaProducerSingleton.get_producer().send_and_wait(settings.KAFKA_TX_TOPIC_NAME, value=message)
        except Exception as e:
            logger.error(f"Failed to publish transaction {transaction.id} to Kafka: {e}")

    async def TransferFunds(self, request: coins_pb2.TransferFundsRequest) -> coins_pb2.TransferFundsResponse:
        if await self._check_idempotency(request.idempotency_key):
            raise GrpcException(
                status_code=grpc.StatusCode.ALREADY_EXISTS,
                details=self.ProblemCode.DUPLICATE_REQUEST,
            )

        async with self._db_session.begin():
            usernames = sorted([request.from_username, request.to_username])  # Ensure consistent locking order
            stmt = select(Account).where(Account.username.in_(usernames)).with_for_update()
            result = await self._db_session.execute(stmt)
            accounts = {acc.username: acc for acc in result.scalars()}

            if request.from_username not in accounts or request.to_username not in accounts:
                raise GrpcException(
                    status_code=grpc.StatusCode.NOT_FOUND,
                    details=self.ProblemCode.USER_NOT_FOUND,
                )

            from_acc, to_acc = accounts[request.from_username], accounts[request.to_username]
            
            total_fraction = from_acc.balance_fraction - request.amount_fraction
            total_whole = from_acc.balance_whole - request.amount_whole
            
            if total_fraction < 0:
                total_whole -= 1
                total_fraction += 100

            if total_whole < 0:
                raise GrpcException(
                    status_code=grpc.StatusCode.FAILED_PRECONDITION,
                    details=self.ProblemCode.INSUFFICIENT_FUNDS,
                )

            from_acc.balance_whole = total_whole
            from_acc.balance_fraction = total_fraction
            
            to_acc.balance_fraction += request.amount_fraction
            if to_acc.balance_fraction >= 100:
                to_acc.balance_whole += 1
                to_acc.balance_fraction -= 100
            to_acc.balance_whole += request.amount_whole
            
            transaction = Transaction(
                id=uuid.uuid4(),
                from_account_id=from_acc.id,
                to_account_id=to_acc.id,
                amount_whole=request.amount_whole,
                amount_fraction=request.amount_fraction,
                type=TransactionType.TRANSFER,
                status=TransactionStatus.COMPLETED,
            )
            self._db_session.add(transaction)
        await self._db_session.commit()
        await self._publish_transaction(transaction)
        return coins_pb2.TransferFundsResponse(transaction_id=str(transaction.id), status=coins_pb2.Status.COMPLETED)

    async def ChargeUser(self, request: coins_pb2.ChargeUserRequest) -> coins_pb2.ChargeUserResponse:
        if await self._check_idempotency(request.idempotency_key):
            raise GrpcException(
                status_code=grpc.StatusCode.ALREADY_EXISTS,
                details=self.ProblemCode.DUPLICATE_REQUEST,
            )

        async with self._db_session.begin():
            stmt = select(Account).where(Account.username == request.username).with_for_update()
            result = await self._db_session.execute(stmt)
            account = result.scalar_one_or_none()
            if not account:
                raise GrpcException(
                    status_code=grpc.StatusCode.NOT_FOUND,
                    details=self.ProblemCode.USER_NOT_FOUND,
                )

            total_fraction = account.balance_fraction - request.amount_fraction
            total_whole = account.balance_whole - request.amount_whole
            
            if total_fraction < 0:
                total_whole -= 1
                total_fraction += 100

            if total_whole < 0:
                raise GrpcException(
                    status_code=grpc.StatusCode.FAILED_PRECONDITION,
                    details=self.ProblemCode.INSUFFICIENT_FUNDS,
                )

            account.balance_whole = total_whole
            account.balance_fraction = total_fraction
            
            transaction = Transaction(
                id=uuid.uuid4(),
                from_account_id=account.id,
                to_account_id=None,
                amount_whole=request.amount_whole,
                amount_fraction=request.amount_fraction,
                type=TransactionType.PAYMENT,
                status=TransactionStatus.COMPLETED,
            )
            self._db_session.add(transaction)
        await self._db_session.commit()
        await self._publish_transaction(transaction)
        return coins_pb2.ChargeUserResponse(transaction_id=str(transaction.id), status=coins_pb2.Status.COMPLETED)

    async def CreditUser(self, request: coins_pb2.CreditUserRequest) -> coins_pb2.CreditUserResponse:
        if await self._check_idempotency(request.idempotency_key):
            raise GrpcException(
                status_code=grpc.StatusCode.ALREADY_EXISTS,
                details=self.ProblemCode.DUPLICATE_REQUEST,
            )

        async with self._db_session.begin():
            stmt = select(Account).where(Account.username == request.username).with_for_update()
            result = await self._db_session.execute(stmt)
            account = result.scalar_one_or_none()
            if not account:
                raise GrpcException(
                    status_code=grpc.StatusCode.NOT_FOUND,
                    details=self.ProblemCode.USER_NOT_FOUND,
                )

            account.balance_fraction += request.amount_fraction
            if account.balance_fraction >= 100:
                account.balance_whole += 1
                account.balance_fraction -= 100
            account.balance_whole += request.amount_whole
   
            transaction = Transaction(
                id=uuid.uuid4(),
                from_account_id=None,
                to_account_id=account.id,
                amount_whole=request.amount_whole,
                amount_fraction=request.amount_fraction,
                type=TransactionType.REPLENISHMENT,
                status=TransactionStatus.COMPLETED,
            )
            self._db_session.add(transaction)
            
        await self._db_session.commit()
        await self._publish_transaction(transaction)
        
        return coins_pb2.CreditUserResponse(transaction_id=str(transaction.id), status=coins_pb2.Status.COMPLETED)

    async def GetBalance(self, request: coins_pb2.GetBalanceRequest) -> coins_pb2.GetBalanceResponse:
        stmt = select(Account).where(Account.username == request.username)
        result = await self._db_session.execute(stmt)
        account = result.scalar_one_or_none()
        if not account:
            raise GrpcException(
                status_code=grpc.StatusCode.NOT_FOUND,
                details=self.ProblemCode.USER_NOT_FOUND,
            )
        return coins_pb2.GetBalanceResponse(
            username=account.username,
            balance_whole=account.balance_whole,
            balance_fraction=account.balance_fraction,
        )

    async def GetTransactionHistory(self, request: coins_pb2.GetTransactionHistoryRequest) -> coins_pb2.GetTransactionHistoryResponse:
        stmt = select(Account).where(Account.username == request.username)
        result = await self._db_session.execute(stmt)
        account = result.scalar_one_or_none()
        if not account:
                raise GrpcException(
                    status_code=grpc.StatusCode.NOT_FOUND,
                    details=self.ProblemCode.USER_NOT_FOUND,
                )
                
        stmt = select(Transaction).where((Transaction.from_account_id == account.id) | (Transaction.to_account_id == account.id))
        result = await self._db_session.execute(stmt)
        transactions = result.scalars().all()
        return coins_pb2.GetTransactionHistoryResponse(
            transactions=[
                coins_pb2.Transaction(
                    transaction_id=str(tx.id),
                    from_username=tx.from_account_id,
                    to_username=tx.to_account_id,
                    amount_whole=tx.amount_whole,
                    amount_fraction=tx.amount_fraction,
                    type=coins_pb2.Type.Value(tx.type.name),
                    status=coins_pb2.Status.Value(tx.status.name),
                    timestamp=str(tx.timestamp),
                ) for tx in transactions
            ]
        )
