import asyncio
from concurrent import futures

import merch_pb2_grpc
import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc
from loguru import logger

from src.core.config import settings
from src.database import manager, YDBManager
from src.database.fill import fill_db
from src.database.migrations import run_migrations
from src.kafka import KafkaProducerSingleton, ensure_topics
from src.interceptors import ExceptionHandler
from src.servicer import MerchServiceServicer
from src.utils.logger import prepare_loggers


async def serve() -> None:
    global manager
    prepare_loggers(debug=settings.DEBUG)
    
    await run_migrations(settings.DATABASE_HOST, settings.DATABASE_NAME)
    
    server = grpc.aio.server(
        migration_thread_pool=futures.ThreadPoolExecutor(),
        compression=grpc.Compression.Gzip,
        interceptors=[
            ExceptionHandler()
        ]
    )
    
    merch_pb2_grpc.add_MerchServiceServicer_to_server(MerchServiceServicer(), server)
    
    health_servicer = health.aio.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    
    # Устанавливаем статус SERVING для всех сервисов
    await health_servicer.set(
        "", health_pb2.HealthCheckResponse.SERVING
    )  # Статус всего сервера
    
    listen_addr = "[::]:50051"
    
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting server on {listen_addr}")
    
    manager = YDBManager(
        endpoint=settings.DATABASE_HOST,
        database=settings.DATABASE_NAME,
    )
    await manager.connect()
    await fill_db(manager.get_pool())

    await KafkaProducerSingleton.create_producer()
    await ensure_topics([settings.KAFKA_MERCH_TOPIC_NAME])
    
    await server.start()
    
    await server.wait_for_termination()
    
    await manager.close()
    await KafkaProducerSingleton.close()


if __name__ == "__main__":
    asyncio.run(serve())
