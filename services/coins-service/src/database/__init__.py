import redis.asyncio as aioredis

from src.core.config import settings
from src.database.manager import AsyncSessionManager


manager = AsyncSessionManager(
    url=settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    isolation_level="REPEATABLE READ",
)

redis_client: aioredis.Redis = aioredis.from_url(settings.REDIS_URL)
