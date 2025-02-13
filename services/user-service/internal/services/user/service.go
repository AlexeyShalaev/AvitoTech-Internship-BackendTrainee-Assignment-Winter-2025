package user

import (
	"context"

	"user-service/internal/models"

	"golang.org/x/crypto/bcrypt"
)

type Service struct {
	repo *Repository
}

func NewService(repo *Repository) *Service {
	return &Service{repo: repo}
}

func (s *Service) GetUserById(ctx context.Context, id string) (*models.User, error) {
	return s.repo.GetUserById(ctx, id)
}

func (s *Service) CreateUserIfNotExists(ctx context.Context, username, password string) (*models.User, bool, error) {
	hashedPassword, err := HashPassword(password)
	if err != nil {
		return nil, false, err
	}

	return s.repo.CreateIfNotExists(ctx, username, hashedPassword)
}

func HashPassword(password string) (string, error) {
	hashed, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}
	return string(hashed), nil
}
