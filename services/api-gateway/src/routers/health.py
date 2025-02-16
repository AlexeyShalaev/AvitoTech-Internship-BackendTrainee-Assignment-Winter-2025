from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/ping", include_in_schema=False)
async def health_ping() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/check", include_in_schema=False)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
