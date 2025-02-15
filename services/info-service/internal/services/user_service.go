package services

import (
	"context"

	"info-service/internal/proto/user"
	"google.golang.org/grpc"
)

type UserService interface {
	GetUserInventory(username string) ([]map[string]interface{}, error)
}

type userService struct {
	client userpb.UserServiceClient
}

func NewUserService(conn *grpc.ClientConn) UserService {
	return &userService{client: userpb.NewUserServiceClient(conn)}
}

func (s *userService) GetUserInventory(username string) ([]map[string]interface{}, error) {
	req := &userpb.GetUserInventoryRequest{Username: username}
	resp, err := s.client.GetUserInventory(context.Background(), req)
	if err != nil {
		return nil, err
	}

	inventory := []map[string]interface{}{}
	for _, item := range resp.Items {
		inventory = append(inventory, map[string]interface{}{
			"type":     item.Merch,
			"quantity": item.Quantity,
		})
	}

	return inventory, nil
}
