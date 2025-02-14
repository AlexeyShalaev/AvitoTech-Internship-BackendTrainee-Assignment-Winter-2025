from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


class AsyncSessionManager:
    def __init__(
        self,
        url: str,
        echo: bool = False,
        future: bool = True,
        poolclass: Any = NullPool,
        session_class: Any = AsyncSession,
        expire_on_commit: bool = False,
        connect_args: dict | None = None,
        isolation_level: str | None = None,
    ) -> None:
        kwargs = {
            "echo": echo,
            "future": future,
            "poolclass": poolclass,
            "isolation_level": isolation_level,
        }
        if connect_args:
            kwargs["connect_args"] = connect_args
        if isolation_level:
            kwargs["isolation_level"] = isolation_level

        engine: AsyncEngine = create_async_engine(url, **kwargs)
        self._session_maker: sessionmaker = sessionmaker(
            engine, class_=session_class, expire_on_commit=expire_on_commit
        )

    @property
    def session_maker(self):
        return self._session_maker

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_maker() as session:
            yield session
