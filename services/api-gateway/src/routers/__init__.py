from fastapi import APIRouter

from src.routers.merch import router as merch_router
from src.routers.coins import router as coins_router


api_router = APIRouter(prefix="/api")

api_router.include_router(coins_router)
api_router.include_router(merch_router)
