package user_test

import (
	"context"
	"testing"

	"user-service/internal/services/user"

	"github.com/stretchr/testify/require"

	"golang.org/x/crypto/bcrypt"
)

func TestHashAndVerifyPassword(t *testing.T) {
	password := "my_secure_password"

	hashedPassword, err := user.HashPassword(password)
	require.NoError(t, err)
	require.NotEmpty(t, hashedPassword)

	// Проверяем правильность хеша
	isValid := VerifyPassword(password, hashedPassword)
	require.True(t, isValid, "Password verification should pass")

	// Проверяем неверный пароль
	isValid = VerifyPassword("wrong_password", hashedPassword)
	require.False(t, isValid, "Wrong password should not pass")
}

func TestCreateUserIfNotExists(t *testing.T) {
	ctx := context.Background()
	username := "test_service_user_456"
	password := "service_password"

	// Используем testRepo из `repository_test.go`
	userService := user.NewService(testRepo, testProducer)

	user, isNew, err := userService.CreateUserIfNotExists(ctx, username, password)
	require.NoError(t, err)
	require.True(t, isNew)
	require.NotEmpty(t, user.ID)

	// Проверяем повторное создание
	user2, isNew, err := userService.CreateUserIfNotExists(ctx, username, password)
	require.NoError(t, err)
	require.False(t, isNew)
	require.Equal(t, user.ID, user2.ID)
}

func VerifyPassword(password, hash string) bool {
	return bcrypt.CompareHashAndPassword([]byte(hash), []byte(password)) == nil
}
