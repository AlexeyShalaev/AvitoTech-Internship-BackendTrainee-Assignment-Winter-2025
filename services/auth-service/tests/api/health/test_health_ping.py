import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_ping(client: AsyncClient):
    res = await client.get("/health/ping")
    assert res.status_code == 200
