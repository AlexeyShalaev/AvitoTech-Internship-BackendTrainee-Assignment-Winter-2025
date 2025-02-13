package grpc_server

import (
	"context"

	pb "user-service/internal/proto"
	"user-service/internal/services/user"
)

// Конструктор сервера
func NewServer() *Server {
	return &Server{}
}

type Server struct {
	pb.UnimplementedUserServiceServer
}

func (s *Server) GetUserById(ctx context.Context, req *pb.GetUserByIdRequest) (*pb.GetUserByIdResponse, error) {
	user, err := user.GetUserById(ctx, req.Id)
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
	user, isNew, err := user.CreateUserIfNotExists(ctx, req.Username, req.Password)
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
