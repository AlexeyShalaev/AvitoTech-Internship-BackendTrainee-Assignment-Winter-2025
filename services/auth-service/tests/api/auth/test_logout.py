import pytest
from httpx import AsyncClient
from src.services.auth import TokenBasedAuthentication

LOGOUT_ENDPOINT = "/api/auth/logout"
AUTH_ENDPOINT = "/api/auth"


@pytest.mark.asyncio()
async def test_logout_without_refresh_token(client: AsyncClient):
    res = await client.delete(LOGOUT_ENDPOINT)
    assert res.status_code == 400
    assert res.json() == {"detail": TokenBasedAuthentication.ProblemCode.REFRESH_TOKEN_NOT_PROVIDED}


@pytest.mark.asyncio()
async def test_logout_ok(client: AsyncClient):
    await client.post(
        AUTH_ENDPOINT,
        json={
            "username": "username",
            "password": "password",
        },
    )
    res = await client.delete(LOGOUT_ENDPOINT)
    assert res.status_code == 200
