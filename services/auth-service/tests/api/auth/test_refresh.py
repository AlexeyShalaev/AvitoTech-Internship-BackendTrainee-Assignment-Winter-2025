import pytest
from httpx import AsyncClient
from src.services.auth import TokenBasedAuthentication

REFRESH_ENDPOINT = "/api/auth/refresh"
AUTH_ENDPOINT = "/api/auth"


@pytest.mark.asyncio()
async def test_refresh_without_refresh_token(client: AsyncClient):
    res = await client.post(REFRESH_ENDPOINT)
    assert res.status_code == 404
    assert res.json() == {"detail": TokenBasedAuthentication.ProblemCode.SESSION_NOT_FOUND}
    assert TokenBasedAuthentication.delete_refresh_token_headers[
        "Set-Cookie"
    ] in res.headers.get("set-cookie")


@pytest.mark.asyncio()
async def test_refresh_ok(client: AsyncClient):
    await client.post(
        AUTH_ENDPOINT,
        json={
            "username": "username",
            "password": "password",
        },
    )
    res = await client.post(REFRESH_ENDPOINT)
    assert res.status_code == 200
