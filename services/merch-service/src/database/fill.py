from loguru import logger
import ydb
import uuid


async def fill_db(pool: ydb.aio.QuerySessionPool) -> None:
    """Заполняет таблицу merchandises товарами, если их нет."""
    items = [
        ("t-shirt", 80),
        ("cup", 20),
        ("book", 50),
        ("pen", 10),
        ("powerbank", 200),
        ("hoody", 300),
        ("umbrella", 200),
        ("socks", 10),
        ("wallet", 50),
        ("pink-hoody", 500),
    ]

    query_check = """
    DECLARE $name AS Utf8;

    SELECT id FROM merchandises WHERE name = $name;
    """

    query_insert = """
    DECLARE $id AS Utf8;
    DECLARE $name AS Utf8;
    DECLARE $price AS Uint64;

    INSERT INTO merchandises (id, name, price) VALUES ($id, $name, $price);
    """

    for name, price in items:
        result = await pool.execute_with_retries(query_check, {"$name": name})

        if result[0].rows:
            logger.info(f"✅ {name} уже есть в базе")
            continue
        
        item_id = str(uuid.uuid4())  # Генерируем UUID
        await pool.execute_with_retries(query_insert, {"$id": item_id, "$name": name, "$price": (price, ydb.PrimitiveType.Uint64)})
        logger.info(f"✅ Добавлен {name} за {price} у.е.")
