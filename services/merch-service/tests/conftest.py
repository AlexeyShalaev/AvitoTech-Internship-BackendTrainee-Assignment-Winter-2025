import asyncio

import pytest
import pytest_asyncio
from mocks import MockCoinsServiceClient
from src.core.config import settings
from src.database import YDBManager, YDBSingleton
from src.database.fill import fill_db
from src.database.migrations import run_migrations
from src.services import coins

coins.CoinsServiceClient = MockCoinsServiceClient  # Monkey patching


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """Reference: https://github.com/pytest-dev/pytest-asyncio/issues/38#issuecomment-264418154"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_and_teardown():
    await run_migrations(settings.DATABASE_HOST, settings.DATABASE_NAME)

    manager = YDBManager(
        endpoint=settings.DATABASE_HOST,
        database=settings.DATABASE_NAME,
    )
    YDBSingleton.set_instance(manager)
    await manager.connect()
    await fill_db(manager.get_pool())

    yield

    await manager.close()


@pytest.fixture()
def pool():
    return YDBSingleton.get_instance().get_pool()
