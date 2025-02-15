from fastapi import APIRouter, Depends, Request
import merch_pb2
import merch_pb2_grpc
from loguru import logger
from src.core.dependencies import get_idempotency_key, get_merch_service
from src.utils.protobuf import message_to_dict


router = APIRouter(prefix="/merch", tags=["merch"])


@router.post("/buy/{name}")
async def buy_merch_controller(
    name: str,
    request: Request,
    idempotency_key: str = Depends(get_idempotency_key),
    merch_service: merch_pb2_grpc.MerchServiceStub = Depends(get_merch_service),
) :
    logger.info(f"BuyMerch request: {name} {request.user['username']}")
    response: merch_pb2.BuyMerchResponse = await merch_service.BuyMerch(
        merch_pb2.BuyMerchRequest(
            username=request.user["username"],
            merch_name=name,
            idempotency_key=idempotency_key,
        ))
    logger.info(f"BuyMerch response: {response}")
    return message_to_dict(response)
