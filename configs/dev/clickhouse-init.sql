-- 1. Таблица для чтения из Kafka
CREATE TABLE IF NOT EXISTS kafka_transactions
(
    transaction_id UUID,
    from_account_id Nullable(UUID),
    to_account_id Nullable(UUID),
    from_username Nullable(String),
    to_username Nullable(String),
    amount_whole UInt64,
    amount_fraction UInt8,
    type Enum8('TRANSFER' = 1, 'PAYMENT' = 2, 'REPLENISHMENT' = 3),
    status Enum8('COMPLETED' = 1, 'ROLLBACKED' = 2),
    _timestamp_ms Nullable(DateTime64(3))
) ENGINE = Kafka
SETTINGS kafka_broker_list = 'kafka:9092',
         kafka_topic_list = 'transactions',
         kafka_group_name = 'clickhouse-consumer',
         kafka_format = 'JSONEachRow',
         kafka_num_consumers = 4,
         kafka_commit_on_select = false;

-- 2. Основная таблица хранения транзакций
CREATE TABLE IF NOT EXISTS transactions
(
    transaction_id UUID,
    from_account_id Nullable(UUID),
    to_account_id Nullable(UUID),
    from_username Nullable(String),
    to_username Nullable(String),
    amount_whole UInt64,
    amount_fraction UInt8,
    type Enum8('TRANSFER' = 1, 'PAYMENT' = 2, 'REPLENISHMENT' = 3),
    status Enum8('COMPLETED' = 1, 'ROLLBACKED' = 2),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (created_at, transaction_id);

-- 3. Materialized View (переносит из Kafka в ClickHouse)
CREATE MATERIALIZED VIEW IF NOT EXISTS transactions_mv TO transactions AS
SELECT
    transaction_id,
    from_account_id,
    to_account_id,
    from_username,
    to_username,
    amount_whole,
    amount_fraction,
    type,
    status,
    now() AS created_at
FROM kafka_transactions
WHERE status = 'COMPLETED';
