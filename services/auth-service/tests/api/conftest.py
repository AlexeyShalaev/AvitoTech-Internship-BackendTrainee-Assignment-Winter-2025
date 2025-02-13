import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import manager
from src.main import app, lifespan

from tests.mocks import MockUserServiceClient


@pytest.fixture(autouse=True)
def override_dependency(session: AsyncSession):
    app.dependency_overrides[manager.get_session] = lambda: session


@pytest_asyncio.fixture()
async def client():
    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client


@pytest.fixture(autouse=True)
def user_service_mock(mocker):
    mocker.patch("src.services.user.UserServiceClient", new=MockUserServiceClient)
