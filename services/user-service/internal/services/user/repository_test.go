package user_test

import (
	"context"
	"log"
	"os"
	"testing"

	"user-service/internal/config"
	"user-service/internal/db"
	"user-service/internal/infra/kafka"
	"user-service/internal/services/user"

	"github.com/stretchr/testify/require"
)

var testRepo *user.Repository
var testProducer *kafka.KafkaProducer

func TestMain(m *testing.M) {
	// Загружаем конфиг
	cfg := config.Load()

	// Подключаемся к реальной БД
	dbPool, err := db.InitDB(cfg)
	if err != nil {
		log.Fatalf("Failed to connect to test database: %v", err)
	}
	defer dbPool.Close()

	db.ApplyMigrations(cfg.MigrationsPath, cfg.DatabaseURL)
	
	// Инициализируем Kafka-продюсер
	testProducer = kafka.NewKafkaProducer(cfg.KafkaBrokers, cfg.KafkaTopic)
	defer testProducer.Close()

	// Инициализируем репозиторий
	testRepo = user.NewRepository(dbPool)

	// Запускаем тесты
	code := m.Run()

	// Завершаем тесты
	os.Exit(code)
}

func TestCreateAndGetUser(t *testing.T) {
	ctx := context.Background()

	username := "test_user_123"
	password := "secure_password"

	// Создаём пользователя
	user, isNew, err := testRepo.CreateIfNotExists(ctx, username, password)
	require.NoError(t, err)
	require.True(t, isNew, "User should be new")
	require.NotEmpty(t, user.ID)
	require.Equal(t, username, user.Username)

	// Получаем пользователя по ID
	fetchedUser, err := testRepo.GetUserById(ctx, user.ID)
	require.NoError(t, err)
	require.NotNil(t, fetchedUser)
	require.Equal(t, user.ID, fetchedUser.ID)
	require.Equal(t, username, fetchedUser.Username)

	// Повторное создание должно вернуть `isNew = false`
	user2, isNew, err := testRepo.CreateIfNotExists(ctx, username, password)
	require.NoError(t, err)
	require.False(t, isNew, "User should already exist")
	require.Equal(t, user.ID, user2.ID)
}
