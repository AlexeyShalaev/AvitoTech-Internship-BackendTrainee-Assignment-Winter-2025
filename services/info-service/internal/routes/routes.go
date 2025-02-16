package routes

import (
	"github.com/gin-gonic/gin"
	"info-service/internal/handlers"
	"info-service/internal/services"
)

// RegisterRoutes регистрирует все маршруты API
func RegisterRoutes(router *gin.Engine, userService services.UserService, coinsService services.CoinsService) {
	// Обработчик информации о пользователе
	infoHandler := handlers.NewInfoHandler(userService, coinsService)
	router.GET("/api/info", infoHandler.GetInfo)

	// Health Check
	router.GET("/api/health", handlers.HealthCheck)
}
