package user

import (
	"context"
	"log"
	"user-service/internal/infra/kafka"
	"user-service/internal/models"

	"golang.org/x/crypto/bcrypt"
)

type Service struct {
	repo     *Repository
	producer *kafka.KafkaProducer
}

func NewService(repo *Repository, producer *kafka.KafkaProducer) *Service {
	return &Service{repo: repo, producer: producer}
}

func (s *Service) GetUserById(ctx context.Context, id string) (*models.User, error) {
	return s.repo.GetUserById(ctx, id)
}

func (s *Service) CreateUserIfNotExists(ctx context.Context, username, password string) (*models.User, bool, error) {
	hashedPassword, err := HashPassword(password)
	if err != nil {
		return nil, false, err
	}

	user, created, err := s.repo.CreateIfNotExists(ctx, username, hashedPassword)
	if err != nil {
		return nil, false, err
	}

	if created {
		go func() {
			err := s.producer.SendMessage(ctx, "user_created", user.ID, user.Username)
			if err != nil {
				log.Printf("Failed to send Kafka message: %v", err)
			}
		}()
	}

	return user, created, nil
}

func HashPassword(password string) (string, error) {
	hashed, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}
	return string(hashed), nil
}
