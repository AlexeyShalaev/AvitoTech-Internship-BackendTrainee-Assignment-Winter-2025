package grpc_server

import (
	"context"

	pb "user-service/internal/proto"
	"user-service/internal/services/user"
)

type Server struct {
	pb.UnimplementedUserServiceServer
	userService *user.Service
}

func NewServer(userService *user.Service) *Server {
	return &Server{userService: userService}
}

func (s *Server) GetUserById(ctx context.Context, req *pb.GetUserByIdRequest) (*pb.GetUserByIdResponse, error) {
	user, err := s.userService.GetUserById(ctx, req.Id)
	if err != nil {
		return nil, err
	}

	return &pb.GetUserByIdResponse{
		Id:             user.ID,
		Username:       user.Username,
		HashedPassword: user.HashedPassword,
	}, nil
}

func (s *Server) CreateIfNotExists(ctx context.Context, req *pb.CreateIfNotExistsRequest) (*pb.CreateIfNotExistsResponse, error) {
	user, isNew, err := s.userService.CreateUserIfNotExists(ctx, req.Username, req.Password)
	if err != nil {
		return nil, err
	}

	return &pb.CreateIfNotExistsResponse{
		Id:             user.ID,
		Username:       user.Username,
		HashedPassword: user.HashedPassword,
		IsNew:          isNew,
	}, nil
}

func (s *Server) GetUserInventory(ctx context.Context, req *pb.GetUserInventoryRequest) (*pb.GetUserInventoryResponse, error) {
	items, err := s.userService.GetUserInventory(ctx, req.Username)
	if err != nil {
		return nil, err
	}

	var response pb.GetUserInventoryResponse
	for _, item := range items {
		response.Items = append(response.Items, &pb.InventoryItem{
			Merch:    item.Merch,
			Quantity: int32(item.Quantity),
		})
	}

	return &response, nil
}
