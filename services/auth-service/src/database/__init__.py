from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.core.config import settings
from src.database.manager import AsyncSessionManager


manager = AsyncSessionManager(
    url=settings.DATABASE_URL.get_secret_value(),
    echo=settings.DATABASE_ECHO,
)


async def check_database_connection() -> bool:
    """
    Checks the connection to the database by executing a simple query.

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    try:
        # Execute a simple query to check the connection
        async with manager.session_maker() as session:
            await session.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        # Handle any exceptions that occur
        return False
