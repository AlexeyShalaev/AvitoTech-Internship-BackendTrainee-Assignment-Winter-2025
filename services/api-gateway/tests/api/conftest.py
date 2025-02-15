import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from src.main import app, lifespan


@pytest_asyncio.fixture()
async def client():
    async with lifespan(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client
