from src.core.config import settings
from src.database.manager import AsyncSessionManager


manager = AsyncSessionManager(
    url=settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    isolation_level="REPEATABLE READ",
)
