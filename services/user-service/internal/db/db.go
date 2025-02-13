package db

import (
	"context"
	"log"

	"user-service/internal/config"

	"github.com/jackc/pgx/v4/pgxpool"
)

func InitDB(cfg *config.Config) (*pgxpool.Pool, error) {
	dbPool, err := pgxpool.Connect(context.Background(), cfg.DatabaseURL)
	if err != nil {
		return nil, err
	}

	log.Println("Connected to PostgreSQL")
	return dbPool, nil
}
