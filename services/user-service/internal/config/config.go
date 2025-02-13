package config

import (
	"fmt"
	"os"
)

type Config struct {
	DatabaseURL string
	MigrationsPath string
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
		MigrationsPath: os.Getenv("MIGRATIONS_PATH"),
	}
}
