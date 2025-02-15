import asyncio
from concurrent import futures

import coins_pb2_grpc
import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc
from loguru import logger

from src.core.config import settings
from src.database.base import run_migrations
from src.kafka import KafkaConsumer, KafkaProducerSingleton, ensure_topics
from src.interceptors import ExceptionHandler, RequestLogger
from src.servicer import CoinsServiceServicer
from src.utils.logger import prepare_loggers


async def serve() -> None:
    prepare_loggers(debug=settings.DEBUG)
    run_migrations(settings.ALEMBIC_CFG)

    server = grpc.aio.server(
        migration_thread_pool=futures.ThreadPoolExecutor(),
        compression=grpc.Compression.Gzip,
        interceptors=[
            ExceptionHandler(),
            RequestLogger(),
        ]
    )
    
    coins_pb2_grpc.add_CoinsServiceServicer_to_server(CoinsServiceServicer(), server)
    
    health_servicer = health.aio.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    
    # Устанавливаем статус SERVING для всех сервисов
    await health_servicer.set(
        "", health_pb2.HealthCheckResponse.SERVING
    )  # Статус всего сервера
    
    listen_addr = "[::]:50051"
    
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting server on {listen_addr}")
    
    await KafkaProducerSingleton.create_producer()
    await ensure_topics([settings.KAFKA_TX_TOPIC_NAME])
    
    # Создаём Kafka Consumer
    kafka_consumer = KafkaConsumer(settings.KAFKA_BOOTSTRAP_SERVERS, settings.KAFKA_USER_TOPIC_NAME)
    await kafka_consumer.start()
    
    await server.start()
    await server.wait_for_termination()
    await KafkaProducerSingleton.close()


if __name__ == "__main__":
    asyncio.run(serve())
