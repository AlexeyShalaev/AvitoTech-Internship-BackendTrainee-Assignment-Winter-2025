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
