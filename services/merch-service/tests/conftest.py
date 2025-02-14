
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, AsyncEngine, create_async_engine
from src.core.config import settings
from src.database.base import run_migrations
from src.services import coins
from tests.mocks import MockCoinsServiceClient

coins.CoinsServiceClient = MockCoinsServiceClient # Monkey patching
run_migrations(settings.ALEMBIC_CFG)


@pytest_asyncio.fixture()
async def connection():
    engine: AsyncEngine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        yield conn
        await conn.rollback()


@pytest_asyncio.fixture()
async def session(connection: AsyncConnection):
    async with AsyncSession(connection, expire_on_commit=False) as _session:
        yield _session


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    import asyncio
    """Reference: https://github.com/pytest-dev/pytest-asyncio/issues/38#issuecomment-264418154"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
