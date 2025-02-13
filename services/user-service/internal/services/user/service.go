package user

import (
	"context"

	"user-service/internal/models"

	"golang.org/x/crypto/bcrypt"
)

func HashPassword(password string) (string, error) {
	hashed, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}
	return string(hashed), nil
}

func VerifyPassword(password, hash string) bool {
	return bcrypt.CompareHashAndPassword([]byte(hash), []byte(password)) == nil
}

func CreateUserIfNotExists(ctx context.Context, username, password string) (*models.User, bool, error) {
	hashedPassword, err := HashPassword(password)
	if err != nil {
		return nil, false, err
	}

	return CreateIfNotExists(ctx, username, hashedPassword)
}
