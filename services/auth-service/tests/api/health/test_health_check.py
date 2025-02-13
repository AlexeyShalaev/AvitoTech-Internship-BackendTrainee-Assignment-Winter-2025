import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    res = await client.get("/health/check")
    assert res.status_code == 200
