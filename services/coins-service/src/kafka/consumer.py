import asyncio
import orjson
import uuid
from aiokafka import AIOKafkaConsumer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import manager
from src.models.account import Account


class KafkaConsumer:
    def __init__(self, brokers: list[str], topic: str) -> None:
        self._brokers = brokers
        self._topic = topic
        self._consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=brokers,
            group_id="coins-service-group",
            auto_offset_reset="earliest",  # Читаем с первого непрочитанного
            enable_auto_commit=True,
        )

    async def start(self):
        """Запускает Kafka-консьюмер в фоновом режиме."""
        await self._consumer.start()
        asyncio.create_task(self.consume())

    async def consume(self):
        """Слушает Kafka и обрабатывает сообщения."""
        async for msg in self._consumer:
            try:
                event = orjson.loads(msg.value.decode("utf-8"))
                if event.get("event") == "user_created":
                    await self.handle_user_created(event)
            except Exception as e:
                logger.exception(f"Error processing Kafka message: {e}")

    async def handle_user_created(self, event: dict):
        """Добавляет нового пользователя в таблицу `accounts`."""
        user_id = event.get("user_id")
        username = event.get("username")

        if not user_id or not username:
            logger.error("Invalid user_created event: missing fields")
            return

        async with manager.session_maker() as session:
            await self._create_account(session, user_id, username)

    async def _create_account(self, session: AsyncSession, user_id: str, username: str):
        """Создаёт `Account`, если он ещё не существует."""
        stmt = select(Account).where(Account.user_id == uuid.UUID(user_id))
        result = await session.execute(stmt)
        existing_account = result.scalar_one_or_none()

        if existing_account:
            logger.warning(f"Account for user {username} already exists.")
            return

        new_account = Account(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            username=username,
            balance_whole=1000,
            balance_fraction=0,
        )

        session.add(new_account)
        await session.commit()
        logger.info(f"Created account for user {username}")

    async def close(self):
        """Закрывает Kafka-консьюмер."""
        await self._consumer.stop()
