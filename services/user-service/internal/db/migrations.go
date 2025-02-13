package db

import (
	"fmt"
	"log"

	"github.com/golang-migrate/migrate/v4"
	_ "github.com/golang-migrate/migrate/v4/database/postgres"
	_ "github.com/golang-migrate/migrate/v4/source/file"
)

// ApplyMigrations накатывает миграции на БД из указанного пути
func ApplyMigrations(migrationsPath, dbURL string) {
	migrationsSource := fmt.Sprintf("file://%s", migrationsPath)

	m, err := migrate.New(migrationsSource, dbURL)
	if err != nil {
		log.Fatalf("Migration initialization error: %v", err)
	}

	if err := m.Up(); err != nil && err != migrate.ErrNoChange {
		log.Fatalf("Migration error: %v", err)
	}

	log.Println("Migrations applied successfully")
}
