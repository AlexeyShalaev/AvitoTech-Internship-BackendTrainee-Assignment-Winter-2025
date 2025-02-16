package user

import (
	"context"
	"log"
	"time"
	"user-service/internal/infra/kafka/producer"
	"user-service/internal/models"

	"golang.org/x/crypto/bcrypt"
)

type Service struct {
	repo     *Repository
	producer *kafka_producer.KafkaProducer
}

func NewService(repo *Repository, producer *kafka_producer.KafkaProducer) *Service {
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
			newCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
			defer cancel()

			err := s.producer.SendMessage(newCtx, "user_created", user.ID, user.Username)
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

func (s *Service) GetUserInventory(ctx context.Context, username string) ([]models.InventoryItem, error) {
	userID, err := s.repo.GetUserIDByUsername(ctx, username)
	if err != nil {
		return nil, err
	}

	return s.repo.GetUserInventory(ctx, userID)
}

// ======= Новый метод обновления инвентаря =======
func (s *Service) UpdateUserInventory(ctx context.Context, username, merchName string) error {
	userID, err := s.repo.GetUserIDByUsername(ctx, username)
	if err != nil {
		log.Printf("User not found: %s", username)
		return err
	}

	err = s.repo.AddOrUpdateInventory(ctx, userID, merchName)
	if err != nil {
		log.Printf("Failed to update inventory for user %s: %v", username, err)
	}
	return err
}
