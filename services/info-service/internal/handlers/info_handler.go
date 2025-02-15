package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"info-service/internal/services"
)

type InfoHandler struct {
	userService  services.UserService
	coinsService services.CoinsService
}

func NewInfoHandler(userService services.UserService, coinsService services.CoinsService) *InfoHandler {
	return &InfoHandler{userService: userService, coinsService: coinsService}
}

func (h *InfoHandler) GetInfo(c *gin.Context) {
	username := c.GetHeader("x-username")
	if username == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	// Получаем инвентарь пользователя
	inventory, err := h.userService.GetUserInventory(username)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка получения инвентаря"})
		return
	}

	// Получаем баланс пользователя
	BalanceWhole, _, err := h.coinsService.GetBalance(username)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка получения баланса"})
		return
	}

	// Получаем историю транзакций
	coinHistory, err := h.coinsService.GetTransactionHistory(username)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка получения истории транзакций"})
		return
	}

	// Формируем ответ
	response := gin.H{
		"coins":     BalanceWhole,
		"inventory": inventory,
		"coinHistory": gin.H{
			"received": coinHistory.Received,
			"sent":     coinHistory.Sent,
		},
	}

	c.JSON(http.StatusOK, response)
}
