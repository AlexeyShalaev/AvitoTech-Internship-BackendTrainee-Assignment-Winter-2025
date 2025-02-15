package config

import (
	"fmt"
	"os"
	"strings"
)

type Config struct {
	DatabaseURL     string
	MigrationsPath  string
	KafkaBrokers    []string
	KafkaTopic      string
	KafkaMerchTopic string
}

func Load() *Config {
	return &Config{
		DatabaseURL: fmt.Sprintf("postgres://%s:%s@%s:%s/%s?sslmode=disable",
			os.Getenv("POSTGRES_USER"),
			os.Getenv("POSTGRES_PASSWORD"),
			os.Getenv("POSTGRES_HOST"),
			os.Getenv("POSTGRES_PORT"),
			os.Getenv("POSTGRES_DB"),
		),
		MigrationsPath:  os.Getenv("MIGRATIONS_PATH"),
		KafkaBrokers:    strings.Split(os.Getenv("KAFKA_BROKERS"), ","), // Разделяем по запятым
		KafkaTopic:      os.Getenv("KAFKA_TOPIC"),
		KafkaMerchTopic: os.Getenv("KAFKA_MERCH_TOPIC"),
	}
}
