import time

from fastapi import APIRouter, HTTPException, status

from src.database import check_database_connection


router = APIRouter(prefix="/health", tags=["health"])


@router.get("/ping", include_in_schema=False)
async def health_ping() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/check", include_in_schema=False)
async def health_check() -> dict[str, str]:
    start_time: float = time.time()
    result: bool = await check_database_connection()
    total_time: float = round(time.time() - start_time, 2) * 1000
    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not available.",
        )
    return {"status": "ok", "ping": f"{total_time}ms"}
