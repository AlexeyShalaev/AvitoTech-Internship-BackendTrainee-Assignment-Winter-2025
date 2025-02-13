package user

import (
	"context"

	"user-service/internal/db"
	"user-service/internal/models"
)

func GetUserById(ctx context.Context, id string) (*models.User, error) {
	var user models.User
	err := db.Conn.QueryRow(ctx, "SELECT id, username, hashed_password FROM users WHERE id=$1", id).
		Scan(&user.ID, &user.Username, &user.HashedPassword)

	if err != nil {
		return nil, err
	}
	return &user, nil
}

func CreateIfNotExists(ctx context.Context, username, hashedPassword string) (*models.User, bool, error) {
	var user models.User
	err := db.Conn.QueryRow(ctx, "SELECT id, username, hashed_password FROM users WHERE username=$1", username).
		Scan(&user.ID, &user.Username, &user.HashedPassword)

	if err == nil {
		// Пользователь уже существует
		return &user, false, nil
	}

	// Создаем нового пользователя
	err = db.Conn.QueryRow(ctx, "INSERT INTO users (username, hashed_password) VALUES ($1, $2) RETURNING id", username, hashedPassword).
		Scan(&user.ID)
	if err != nil {
		return nil, false, err
	}

	user.Username = username
	user.HashedPassword = hashedPassword
	return &user, true, nil
}
