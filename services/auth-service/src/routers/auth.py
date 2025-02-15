from fastapi import APIRouter, Cookie, Depends, Request, Response, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.database import manager
from src.schemas.common import DetailSchema
from src.schemas.auth import (
    AuthRequest,
    AuthResponse,
)
from src.services.auth import TokenBasedAuthentication

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = TokenBasedAuthentication(
    settings.ACCESS_TOKEN_EXPIRES_IN, settings.REFRESH_TOKEN_EXPIRES_IN
)

@router.post("", response_model=AuthResponse)
async def auth_controller(
    request: Request,
    response: Response,
    payload: AuthRequest,
    db_session: AsyncSession = Depends(manager.get_session),
) -> AuthResponse:
    new_token: str = await auth_service.create_session(
        username=payload.username,
        password=payload.password,
        db_session=db_session,
        request=request,
        response=response,
    )

    return AuthResponse(token=new_token)


@router.post("/refresh", response_model=AuthResponse)
async def refresh_session_controller(
    request: Request,
    response: Response,
    avito_staff_refresh_token: str = Cookie(None),
    db_session: AsyncSession = Depends(manager.get_session),
) -> AuthResponse:
    # Create New Session
    new_token: str = await auth_service.refresh_session(
        refresh_token=avito_staff_refresh_token,
        db_session=db_session,
        request=request,
        response=response,
    )

    return AuthResponse(token=new_token)


@router.delete("/logout", response_model=DetailSchema)
async def logout_controller(
    response: Response,
    avito_staff_refresh_token: str = Cookie(None),
    db_session: AsyncSession = Depends(manager.get_session),
) -> DetailSchema:
    await auth_service.delete_session(
        db_session=db_session, refresh_token=avito_staff_refresh_token, response=response
    )

    return {"detail": "User is logged out from current session."}
