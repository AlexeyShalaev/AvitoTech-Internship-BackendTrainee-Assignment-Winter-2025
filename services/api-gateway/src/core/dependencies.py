from fastapi import Request
import grpc

import merch_pb2_grpc
import coins_pb2_grpc

from src.core.config import settings


async def get_idempotency_key(request: Request) -> str:
    return request.headers.get("x-idempotency-key")


async def get_merch_service():
    async with grpc.aio.insecure_channel(settings.MERCH_SERVICE_HOST) as channel:
        yield merch_pb2_grpc.MerchServiceStub(channel)
        
    
async def get_coins_service():
    async with grpc.aio.insecure_channel(settings.COINS_SERVICE_HOST) as channel:
        yield coins_pb2_grpc.CoinsServiceStub(channel)
        