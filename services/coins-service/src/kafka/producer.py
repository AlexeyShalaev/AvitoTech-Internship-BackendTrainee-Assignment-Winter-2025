from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from src.core.config import settings


class KafkaProducerSingleton:
    _instance: AIOKafkaProducer | None = None

    @classmethod
    async def create_producer(cls) -> None:
        if cls._instance is None:
            cls._instance = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id=settings.KAFKA_CLIENT_ID,
                acks="all",  # Гарантирует запись во все реплики
                enable_idempotence=True,  # Идемпотентность (предотвращает дубли)
                compression_type="gzip",  # Сжатие сообщений
                request_timeout_ms=100,
            )
            await cls._instance.start()

    @classmethod
    def get_producer(cls) -> AIOKafkaProducer:
        return cls._instance

    @classmethod
    async def close(cls) -> None:
        if cls._instance is not None:
            await cls._instance.stop()
            cls._instance = None


async def ensure_topics(topics: list[str]):
    admin_client = AIOKafkaAdminClient(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )
    await admin_client.start()
    try:
        existing_topics = await admin_client.list_topics()
        new_topics = [
            NewTopic(name=topic_name, num_partitions=3, replication_factor=1)
            for topic_name in topics
            if topic_name not in existing_topics
        ]
        await admin_client.create_topics(new_topics)
    finally:
        await admin_client.close()
