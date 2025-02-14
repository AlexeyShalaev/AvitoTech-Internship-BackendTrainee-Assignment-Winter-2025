import ydb
import ydb.aio


class YDBManager:
    def __init__(
        self,
        endpoint: str,
        database: str,
    ) -> None:
        self._driver = ydb.aio.Driver(endpoint=endpoint, database=database)
        self._connected: bool = False

    async def connect(self, timeout: int = 30) -> None:
        if not self._connected:
            await self._driver.wait(timeout=timeout)
            self._connected = True

    async def get_pool(self):
        async with ydb.aio.QuerySessionPool(self._driver) as pool:
            yield pool
    
    async def close(self) -> None:
        if self._connected:
            await self._driver.stop()
            self._connected = False
