from enum import StrEnum

import coins_pb2
import merch_pb2
import grpc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from src.kafka import KafkaProducerSingleton
from src.core.config import settings
from src.core.exceptions import GrpcException
from src.services.coins import CoinsServiceClient
from src.models.merch import Merch


class MerchService:
    class ProblemCode(StrEnum):
        MERCH_NOT_FOUND = "Merch not found"

    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def _publish_selling(self, transaction_id: str, status: str, username: str, merch_name: str, price: int) -> None:
        message = {
            "transaction_id": transaction_id,
            "status": status,
            "username": username,
            "merch_name": merch_name,
            "price": price
        }
        try:
            await KafkaProducerSingleton.get_producer().send_and_wait(settings.KAFKA_MERCH_TOPIC_NAME, value=message)
        except Exception as e:
            logger.error(f"Failed to publish selling to Kafka: {e}")

    async def BuyMerch(self, request: merch_pb2.BuyMerchRequest) -> merch_pb2.BuyMerchResponse:
        logger.info(f"BuyMerch request: {request.username}, {request.merch_name}, {request.idempotency_key}")
        result = await self._db_session.execute(select(Merch).where(Merch.name == request.merch_name))
        merch: Merch | None = result.scalar()
        if not merch:
            raise GrpcException(
                grpc.StatusCode.NOT_FOUND, 
                self.ProblemCode.MERCH_NOT_FOUND
            )
            
        try:
            async with CoinsServiceClient() as coins_service:
                response: coins_pb2.ChargeUserResponse = await coins_service.charge_user(username=request.username, 
                                                amount_whole=merch.price, 
                                                amount_fraction=0,
                                                idempotency_key=request.idempotency_key)
        except grpc.RpcError as e:
            logger.error(f"Error calling charge_user: {e.details()}")
            raise GrpcException(
                status_code=e.code(),
                details=e.details(),
            )
            
        status: str = coins_pb2.Status.Name(response.status)
            
        logger.info(f"BuyMerch response: {response.transaction_id}, {status}")

        await self._publish_selling(response.transaction_id, status, request.username, merch.name, merch.price)

        return merch_pb2.BuyMerchResponse(transaction_id=response.transaction_id,
                                          status=status
                                          )
