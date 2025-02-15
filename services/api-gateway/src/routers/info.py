import httpx
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from src.core.config import settings
from src.schemas.info import InfoResponse

router = APIRouter(prefix="/info", tags=["info"])


@router.get("", response_model=InfoResponse)
async def current_user_get_info_controller(
    request: Request,
) -> InfoResponse:
    username = request.user["username"]

    headers = {"x-username": username}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.INFO_SERVICE_HOST}/api/info", headers=headers
            )
            response.raise_for_status()  # Вызывает исключение, если статус ответа >= 400
            data = response.json()
            return InfoResponse(**data)
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Info Service returned an error: {e.response.status_code} - {e.response.text}"
            )
            raise HTTPException(
                status_code=e.response.status_code, detail="Failed to fetch info"
            )
        except httpx.RequestError as e:
            logger.error(f"Request to Info Service failed: {e}")
            raise HTTPException(status_code=500, detail="Info Service is unreachable")
