package user

import (
	"context"

	"user-service/internal/models"

	"github.com/jackc/pgx/v4/pgxpool"
)

type Repository struct {
	db *pgxpool.Pool
}

func NewRepository(db *pgxpool.Pool) *Repository {
	return &Repository{db: db}
}

func (r *Repository) GetUserById(ctx context.Context, id string) (*models.User, error) {
	var user models.User
	err := r.db.QueryRow(ctx, "SELECT id, username, hashed_password FROM users WHERE id=$1", id).
		Scan(&user.ID, &user.Username, &user.HashedPassword)

	if err != nil {
		return nil, err
	}
	return &user, nil
}

func (r *Repository) CreateIfNotExists(ctx context.Context, username, hashedPassword string) (*models.User, bool, error) {
	var user models.User
	err := r.db.QueryRow(ctx, "SELECT id, username, hashed_password FROM users WHERE username=$1", username).
		Scan(&user.ID, &user.Username, &user.HashedPassword)

	if err == nil {
		return &user, false, nil
	}

	err = r.db.QueryRow(ctx, "INSERT INTO users (username, hashed_password) VALUES ($1, $2) RETURNING id", username, hashedPassword).
		Scan(&user.ID)
	if err != nil {
		return nil, false, err
	}

	user.Username = username
	user.HashedPassword = hashedPassword
	return &user, true, nil
}

func (r *Repository) GetUserIDByUsername(ctx context.Context, username string) (string, error) {
	var userID string
	err := r.db.QueryRow(ctx, "SELECT id FROM users WHERE username=$1", username).Scan(&userID)
	if err != nil {
		return "", err
	}
	return userID, nil
}

func (r *Repository) GetUserInventory(ctx context.Context, userID string) ([]models.InventoryItem, error) {
	rows, err := r.db.Query(ctx, "SELECT merch, quantity FROM inventory WHERE user_id=$1", userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var items []models.InventoryItem
	for rows.Next() {
		var item models.InventoryItem
		if err := rows.Scan(&item.Merch, &item.Quantity); err != nil {
			return nil, err
		}
		items = append(items, item)
	}

	return items, nil
}

// ======= Новые методы для работы с инвентарем =======
func (r *Repository) AddOrUpdateInventory(ctx context.Context, userID, merchName string) error {
	tx, err := r.db.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx) // Откат при ошибке

	// Блокируем строку для обновления
	var quantity int
	err = tx.QueryRow(ctx, "SELECT quantity FROM inventory WHERE user_id=$1 AND merch=$2 FOR UPDATE", userID, merchName).
		Scan(&quantity)

	if err != nil {
		// Если запись не найдена, вставляем новую
		_, err = tx.Exec(ctx, "INSERT INTO inventory (user_id, merch, quantity) VALUES ($1, $2, 1)", userID, merchName)
		if err != nil {
			return err
		}
	} else {
		// Если запись есть, увеличиваем quantity
		_, err = tx.Exec(ctx, "UPDATE inventory SET quantity = quantity + 1 WHERE user_id=$1 AND merch=$2", userID, merchName)
		if err != nil {
			return err
		}
	}

	return tx.Commit(ctx) // Фиксируем транзакцию
}
