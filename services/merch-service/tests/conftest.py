import pytest_asyncio
from src.core.config import settings
from src.database import manager
from src.database.base import run_migrations
from src.services import coins
from mocks import MockCoinsServiceClient

coins.CoinsServiceClient = MockCoinsServiceClient # Monkey patching
run_migrations(settings.ALEMBIC_CFG)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_and_teardown():
    await manager.connect()
    
    yield
    
    await manager.close()


@pytest_asyncio.fixture()
async def pool():
    async with manager.get_pool() as _pool:
        yield _pool
