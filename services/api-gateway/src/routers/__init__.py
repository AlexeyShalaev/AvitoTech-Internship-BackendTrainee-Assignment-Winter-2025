from fastapi import APIRouter
from src.routers.coins import router as coins_router
from src.routers.info import router as info_router
from src.routers.merch import router as merch_router

api_router = APIRouter(prefix="/api")

api_router.include_router(coins_router)
api_router.include_router(info_router)
api_router.include_router(merch_router)
