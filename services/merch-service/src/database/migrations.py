import os
import ydb
from loguru import logger


class YDBMigrationManager:
    def __init__(self, endpoint: str, database: str, migrations_dir: str = "migrations"):
        self._migrations_dir: str = migrations_dir
        self._driver = ydb.aio.Driver(endpoint=endpoint, database=database)
        self._pool: ydb.aio.QuerySessionPool | None = None
        self._table_prefix = database  # Используем путь базы как префикс таблиц

    async def connect(self, timeout: int = 10):
        """Подключается к YDB"""
        await self._driver.wait(timeout=timeout)
        self._pool = ydb.aio.QuerySessionPool(self._driver)

    async def close(self):
        """Закрывает соединение с YDB"""
        if self._pool:
            await self._pool.stop()
            await self._driver.stop()

    async def execute(self, query: str, params: dict = None):
        """Выполняет SQL-запрос"""
        return await self._pool.execute_with_retries(
            f"PRAGMA TablePathPrefix('{self._table_prefix}');\n{query}", 
            params or {}
        )

    async def ensure_migrations_table(self):
        """Создает таблицу migrations, если её нет"""
        try:
            await self.execute(f"""
                CREATE TABLE IF NOT EXISTS migrations (
                    id Utf8,
                    applied_at Timestamp,
                    PRIMARY KEY (id)
                );
            """)
            logger.info("✅ Таблица `migrations` проверена (создана, если не существовала).")
        except Exception as e:
            logger.error(f"❌ Ошибка при создании таблицы `migrations`: {e}")

    async def applied_migrations(self):
        """Получает список уже примененных миграций"""
        try:
            result_sets = await self.execute("SELECT id FROM migrations ORDER BY applied_at DESC")
            return [row["id"] for row in result_sets[0].rows]
        except Exception as ex:
            logger.error(f"❌ Ошибка при получении списка примененных миграций: {ex}")
            return []

    async def apply_migration(self, migration_id: str, sql: str):
        """Применяет одну миграцию"""
        await self.execute(sql)
        await self.execute(
            "INSERT INTO migrations (id, applied_at) VALUES ($id, CurrentUtcTimestamp());",
            {"$id": migration_id},
        )

    async def rollback_migration(self):
        """Откатывает последнюю миграцию"""
        await self.connect()
        await self.ensure_migrations_table()
        applied = await self.applied_migrations()
        if not applied:
            logger.info("⚠️ Нет миграций для отката.")
            return

        last_migration = applied[0]
        down_file = os.path.join(self._migrations_dir, f"{last_migration}.down.sql")

        if not os.path.exists(down_file):
            logger.info(f"⚠️ Файл {down_file} отсутствует, откат невозможен.")
            return

        logger.info(f"🔄 Откат миграции: {last_migration}")
        with open(down_file, "r") as f:
            sql = f.read()
        
        await self.execute(sql)
        await self.execute("DELETE FROM migrations WHERE id = $id;", {"$id": last_migration})

        logger.info(f"✅ Миграция {last_migration} откатена.")
        await self.close()

    async def migrate(self):
        """Применяет новые миграции"""
        await self.connect()
        await self.ensure_migrations_table()
        applied = set(await self.applied_migrations())
        migration_files = sorted(f for f in os.listdir(self._migrations_dir) if f.endswith(".sql") and not f.endswith(".down.sql"))

        for filename in migration_files:
            if filename not in applied:
                logger.info(f"📥 Применение миграции: {filename}")
                with open(os.path.join(self._migrations_dir, filename), "r") as f:
                    sql = f.read()
                await self.apply_migration(filename, sql)
                logger.info(f"✅ Миграция {filename} применена.")

        await self.close()


async def run_migrations(endpoint: str, database: str, migrations_dir: str = "migrations"):
    """Запускает миграции при старте приложения"""
    manager = YDBMigrationManager(endpoint=endpoint, database=database, migrations_dir=migrations_dir)
    await manager.migrate()


async def rollback_last_migration(endpoint: str, database: str, migrations_dir: str = "migrations"):
    """Запускает откат последней миграции"""
    manager = YDBMigrationManager(endpoint=endpoint, database=database, migrations_dir=migrations_dir)
    await manager.rollback_migration()
