import uuid
from datetime import datetime, timedelta
from enum import StrEnum
from zoneinfo import ZoneInfo

import user_pb2
from fastapi import HTTPException, Request, Response, status
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.session import Session
from src.services.user import UserServiceClient
from src.utils.security import create_access_token, verify_password


class TokenBasedAuthentication:
    refresh_token_key = "avito_staff_refresh_token"
    delete_refresh_token_headers = {
        "Set-Cookie": f"{refresh_token_key}=; HttpOnly; expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/; SameSite=lax"
    }

    class ProblemCode(StrEnum):
        INCORRECT_PROVIDED_DATA = "Incorrect provided data"
        SESSION_NOT_FOUND = "Session not found"
        TOKEN_EXPIRED = "Token expired"
        REFRESH_TOKEN_NOT_PROVIDED = "Refresh token not provided"

    def __init__(
        self, access_token_expires_in: int, refresh_token_expires_in: int, issuer: str = "http://auth-service"
    ) -> None:
        self._access_token_expires_in: int = access_token_expires_in
        self._refresh_token_expires_in: int = refresh_token_expires_in
        self._issuer: str = issuer

    async def create_session(
        self,
        username: str,
        password: str,
        db_session: AsyncSession,
        request: Request,
        response: Response,
    ) -> str:
        # Check if the user exist
        async with UserServiceClient() as user_client:
            user: user_pb2.CreateIfNotExistsResponse = await user_client.create_if_not_exists(username, password)

            if not user.is_new and not verify_password(
                user.hashed_password, password
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=self.ProblemCode.INCORRECT_PROVIDED_DATA.value,
                )

        # Create Session
        refresh_token = uuid.uuid4()
        current_datetime = datetime.now(tz=ZoneInfo("UTC"))
        session_expires_in = current_datetime + timedelta(
            seconds=self._refresh_token_expires_in
        )
        
        await db_session.execute(
            insert(Session).values(
                user_id=user.id,
                refresh_token=refresh_token,
                user_agent=self._get_user_agent(request),
                ip=self._get_ip(request),
                expires_in=session_expires_in,
            )
        )
        await db_session.commit()

        # Create Access Token
        session_data: dict = self._create_session_data(user.id, user.username, current_datetime)

        # Store refresh token in cookie
        response.set_cookie(
            self.refresh_token_key,
            refresh_token,
            max_age=self._refresh_token_expires_in,
            httponly=True,
        )

        # Send token
        return create_access_token(session_data)

    async def refresh_session(
        self,
        refresh_token: str,
        db_session: AsyncSession,
        request: Request,
        response: Response,
    ) -> str:
        result = await db_session.execute(
            select(Session).filter(Session.refresh_token == refresh_token)
        )
        session: Session | None = result.scalar()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self.ProblemCode.SESSION_NOT_FOUND,
                headers=TokenBasedAuthentication.delete_refresh_token_headers,
            )

        if session.ip != self._get_ip(
            request
        ) or session.user_agent != self._get_user_agent(request):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=self.ProblemCode.INCORRECT_PROVIDED_DATA,
                headers=TokenBasedAuthentication.delete_refresh_token_headers,
            )

        current_datetime = datetime.now(tz=ZoneInfo("UTC"))

        if current_datetime > session.expires_in:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=self.ProblemCode.TOKEN_EXPIRED,
                headers=TokenBasedAuthentication.delete_refresh_token_headers,
            )
            
        async with UserServiceClient() as user_client:
            user: user_pb2.GetUserByIdResponse = await user_client.get_by_id(str(session.user_id))
            
        # Create Access Token
        session_data: dict = self._create_session_data(user.id, user.username, current_datetime)

        # Store refresh token in cookie
        response.set_cookie(
            self.refresh_token_key,
            session.refresh_token,
            max_age=int((session.expires_in - current_datetime).total_seconds()),
            httponly=True,
        )

        # Send token
        return create_access_token(session_data)

    async def delete_session(
        self,
        db_session: AsyncSession,
        refresh_token: str,
        response: Response,
    ) -> None:
        await db_session.execute(
            delete(Session).filter(Session.refresh_token == refresh_token)
        )
        await db_session.commit()
        # Delete cookie
        response.delete_cookie(self.refresh_token_key)

    def _create_session_data(self, user_id: str, username: str, current_datetime: datetime) -> dict:
        return {
            "user_id": str(user_id),
            "username": username,
            "exp": current_datetime + timedelta(seconds=self._access_token_expires_in),
            "iss": self._issuer,
        }

    def _get_user_agent(self, request: Request) -> str:
        return request.headers.get("user-agent", "")

    def _get_ip(self, request: Request) -> str:
        return request.headers.get("x-real-ip", request.client.host)
