import coins_pb2
import coins_pb2_grpc
from fastapi import APIRouter, Depends, Request
from loguru import logger
from src.core.dependencies import get_coins_service, get_idempotency_key
from src.schemas.coins import SendCoinsRequest
from src.utils.protobuf import message_to_dict

router = APIRouter(prefix="/coins", tags=["coins"])


@router.post("/send")
async def send_coins_controller(
    payload: SendCoinsRequest,
    request: Request,
    idempotency_key: str = Depends(get_idempotency_key),
    coins_service: coins_pb2_grpc.CoinsServiceStub = Depends(get_coins_service),
):
    logger.info(f"Send Coins request: {payload} {request.user['username']}")
    response: coins_pb2.TransferFundsResponse = await coins_service.TransferFunds(
        coins_pb2.TransferFundsRequest(
            from_username=request.user["username"],
            to_username=payload.to_user,
            amount_whole=payload.amount,
            amount_fraction=0,
            idempotency_key=idempotency_key,
        )
    )
    logger.info(f"Send Coins response: {response}")
    return message_to_dict(response)
