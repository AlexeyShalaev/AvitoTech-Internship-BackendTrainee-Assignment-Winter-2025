from fastapi import APIRouter

from src.routers.merch import router as merch_router


api_router = APIRouter(prefix="/api")

api_router.include_router(merch_router)
