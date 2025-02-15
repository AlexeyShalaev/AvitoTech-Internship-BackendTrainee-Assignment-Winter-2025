import ydb
from loguru import logger


class YDBManager:
    def __init__(
        self,
        endpoint: str,
        database: str,
    ) -> None:
        self._driver = ydb.aio.Driver(endpoint=endpoint, database=database)
        self._pool: ydb.aio.QuerySessionPool  | None = None

    async def connect(self, timeout: int = 10) -> None:
        if not self._pool:
            logger.info("Connecting to YDB")
            await self._driver.wait(timeout=timeout)
            self._pool = ydb.aio.QuerySessionPool(self._driver)
            logger.info("Connected to YDB")

    def get_pool(self):
        return self._pool
    
    async def close(self) -> None:
        if self._pool:
            logger.info("Closing connection to YDB")
            await self._pool.stop()
            await self._driver.stop()
            self._pool = None
            logger.info("Connection to YDB closed")

class YDBSingleton:
    _instance: YDBManager | None = None

    @classmethod
    def set_instance(cls, instance: YDBManager) -> None:
        """
        Устанавливает глобальный инстанс YDBManager.
        """
        cls._instance = instance
        logger.info("YDBManager instance set")

    @classmethod
    def get_instance(cls) -> YDBManager:
        """
        Возвращает глобальный инстанс YDBManager.
        """
        if cls._instance is None:
            raise RuntimeError("YDBManager instance is not set. Call `set_instance` first.")
        return cls._instance
    