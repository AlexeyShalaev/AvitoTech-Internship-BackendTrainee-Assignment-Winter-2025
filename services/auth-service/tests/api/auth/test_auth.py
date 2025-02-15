import pytest
from httpx import AsyncClient
from src.services.auth import TokenBasedAuthentication

AUTH_ENDPOINT = "/api/auth"


@pytest.mark.asyncio()
async def test_login_wrong_password(client: AsyncClient):
    res = await client.post(
        AUTH_ENDPOINT,
        json={
            "username": "username",
            "password": "wrong_password",
        },
    )
    assert res.status_code == 400
    assert res.json() == {
        "detail": TokenBasedAuthentication.ProblemCode.INCORRECT_PROVIDED_DATA
    }


@pytest.mark.asyncio()
async def test_login_ok(client: AsyncClient):
    res = await client.post(
        AUTH_ENDPOINT,
        json={
            "username": "username",
            "password": "password",
        },
    )
    assert res.status_code == 200
