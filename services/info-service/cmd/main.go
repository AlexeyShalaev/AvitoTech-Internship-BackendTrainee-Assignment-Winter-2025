package main

import (
	"log"

	"github.com/gin-gonic/gin"
	"google.golang.org/grpc"

	"info-service/internal/config"
	"info-service/internal/routes"
	"info-service/internal/services"
	"info-service/pkg"
)

func main() {
	// Загружаем переменные окружения
	cfg := config.Load()

	// gRPC подключения
	userConn, err := grpc.Dial(cfg.UserServiceAddr, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("Не удалось подключиться к UserService: %v", err)
	}
	defer userConn.Close()

	coinsConn, err := grpc.Dial(cfg.CoinsServiceAddr, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("Не удалось подключиться к CoinsService: %v", err)
	}
	defer coinsConn.Close()

	// Создаем сервисы
	userService := services.NewUserService(userConn)
	coinsService := services.NewCoinsService(coinsConn)

	// Инициализируем роутер
	r := gin.Default()
	routes.RegisterRoutes(r, userService, coinsService)

	// Запуск сервера
	server := pkg.NewServer(r)
	log.Printf("Запуск сервера на порту %s", cfg.ServerPort)
	if err := server.Run(":" + cfg.ServerPort); err != nil {
		log.Fatalf("Ошибка запуска сервера: %v", err)
	}
}
