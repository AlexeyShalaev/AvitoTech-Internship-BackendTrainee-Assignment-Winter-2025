package handlers

import (
	"net/http"
	"log"

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
		log.Println("[WARN] Unauthorized access attempt - missing x-username header")
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	log.Printf("[INFO] Fetching info for user: %s", username)

	// Получаем инвентарь пользователя
	inventory, err := h.userService.GetUserInventory(username)
	if err != nil {
		log.Printf("[ERROR] Failed to fetch inventory for user %s: %v", username, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка получения инвентаря"})
		return
	}

	// Получаем баланс пользователя
	BalanceWhole, _, err := h.coinsService.GetBalance(username)
	if err != nil {
		log.Printf("[ERROR] Failed to fetch balance for user %s: %v", username, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка получения баланса"})
		return
	}

	// Получаем историю транзакций
	coinHistory, err := h.coinsService.GetTransactionHistory(username)
	if err != nil {
		log.Printf("[ERROR] Failed to fetch transaction history for user %s: %v", username, err)
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

	log.Printf("[INFO] Successfully fetched info for user %s", username)
	c.JSON(http.StatusOK, response)
}
