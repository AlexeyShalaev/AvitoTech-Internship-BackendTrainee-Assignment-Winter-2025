from src.core.config import settings
from src.database.manager import YDBManager


manager = YDBManager(
    endpoint=settings.DATABASE_HOST,
    database=settings.DATABASE_NAME,
)
