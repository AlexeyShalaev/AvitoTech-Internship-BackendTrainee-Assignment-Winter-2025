package main

import (
	"context"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"

	"user-service/internal/config"
	"user-service/internal/db"
	"user-service/internal/infra/kafka/consumer"
	"user-service/internal/infra/kafka/producer"
	"user-service/internal/servers/grpc_server"
	"user-service/internal/services/user"

	pb "user-service/internal/proto/user"

	"google.golang.org/grpc"
	"google.golang.org/grpc/health"
	"google.golang.org/grpc/health/grpc_health_v1"
)

func runGRPCServer(ctx context.Context, userService pb.UserServiceServer) {
	listener, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	server := grpc.NewServer()
	pb.RegisterUserServiceServer(server, userService)

	healthServer := health.NewServer()
	grpc_health_v1.RegisterHealthServer(server, healthServer)
	healthServer.SetServingStatus("", grpc_health_v1.HealthCheckResponse_SERVING)

	log.Println("User Service running on port 50051")

	go func() {
		if err := server.Serve(listener); err != nil {
			log.Fatalf("Failed to serve: %v", err)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	<-stop

	log.Println("Shutting down gRPC server...")
	server.GracefulStop()
}

func main() {
	cfg := config.Load()

	// Инициализация базы данных
	dbPool, err := db.InitDB(cfg)
	if err != nil {
		log.Fatalf("Database initialization error: %v", err)
	}
	defer dbPool.Close()

	// Применение миграций
	db.ApplyMigrations(cfg.MigrationsPath, cfg.DatabaseURL)

	// Создание топика, если его нет
	err = kafka_producer.EnsureTopicExists(cfg.KafkaBrokers, cfg.KafkaTopic)
	if err != nil {
		log.Fatalf("Failed to create Kafka topic: %v", err)
	}

	// Инициализация Kafka-продюсера
	producer := kafka_producer.NewKafkaProducer(cfg.KafkaBrokers, cfg.KafkaTopic)
	defer producer.Close()

	// Создание сервиса пользователя с Kafka-продюсером
	userRepo := user.NewRepository(dbPool)
	userService := user.NewService(userRepo, producer)

	// Запускаем Kafka Consumer
	consumer := kafka_consumer.NewKafkaConsumer(cfg.KafkaBrokers, cfg.KafkaMerchTopic, userService)
	ctx := context.Background()
	go consumer.StartConsuming(ctx)
	defer consumer.Close()

	// Создание gRPC-сервера
	grpcServer := grpc_server.NewServer(userService)

	runGRPCServer(ctx, grpcServer)
}
