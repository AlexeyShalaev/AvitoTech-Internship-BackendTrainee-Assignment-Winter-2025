import grpc
import merch_pb2
import merch_pb2_grpc
from src.database import manager
from src.services.merch import MerchService


class MerchServiceServicer(merch_pb2_grpc.MerchService):
    async def BuyMerch(
        self, request: merch_pb2.BuyMerchRequest, context: grpc.aio.ServicerContext,
    ) -> merch_pb2.BuyMerchResponse:
        return await MerchService(manager.get_pool()).BuyMerch(request)
