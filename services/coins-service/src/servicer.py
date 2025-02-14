import grpc
import coins_pb2
import coins_pb2_grpc
from src.database import manager
from src.services.coins import CoinsService


class CoinsServiceServicer(coins_pb2_grpc.CoinsService):
    async def TransferFunds(
        self, request: coins_pb2.TransferFundsRequest, context: grpc.aio.ServicerContext,
    ) -> coins_pb2.TransferFundsResponse:
        async with manager.session_maker() as session:
            return await CoinsService(session).TransferFunds(request)

    async def ChargeUser(
        self,
        request: coins_pb2.ChargeUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> coins_pb2.ChargeUserResponse:
        async with manager.session_maker() as session:
            return await CoinsService(session).ChargeUser(request)

    async def CreditUser(
        self,
        request: coins_pb2.CreditUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> coins_pb2.CreditUserResponse:
        async with manager.session_maker() as session:
            return await CoinsService(session).CreditUser(request)

    async def GetBalance(
        self,
        request: coins_pb2.GetBalanceRequest,
        context: grpc.aio.ServicerContext,
    ) -> coins_pb2.GetBalanceResponse:
        async with manager.session_maker() as session:
            return await CoinsService(session).GetBalance(request)

    async def GetTransactionHistory(
        self, request: coins_pb2.GetTransactionHistoryRequest, context: grpc.aio.ServicerContext
    ) -> coins_pb2.GetTransactionHistoryResponse:
        async with manager.session_maker() as session:
            return await CoinsService(session).GetTransactionHistory(request)
