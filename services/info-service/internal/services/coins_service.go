package services

import (
	"context"
	"log"

	"google.golang.org/grpc"
	"info-service/internal/proto/coins"
)

type CoinsService interface {
	GetTransactionHistory(username string) (*CoinHistoryResponse, error)
	GetBalance(username string) (int64, int64, error)
}

type CoinHistoryResponse struct {
	Received []map[string]interface{}
	Sent     []map[string]interface{}
}

type coinsService struct {
	client coinspb.CoinsServiceClient
}

func NewCoinsService(conn *grpc.ClientConn) CoinsService {
	return &coinsService{client: coinspb.NewCoinsServiceClient(conn)}
}

// Получение истории транзакций + баланс из gRPC
func (s *coinsService) GetTransactionHistory(username string) (*CoinHistoryResponse, error) {
	log.Printf("Fetching transaction history for user: %s", username)

	// Запрашиваем историю транзакций через gRPC
	req := &coinspb.GetTransactionHistoryRequest{Username: username}
	resp, err := s.client.GetTransactionHistory(context.Background(), req)
	if err != nil {
		log.Printf("Error fetching transaction history for user %s: %v", username, err)
		return nil, err
	}

	log.Printf("Total transactions received for user %s: %d", username, len(resp.Transactions))

	// Обрабатываем только транзакции со статусом COMPLETED и типом TRANSFER
	received := []map[string]interface{}{}
	sent := []map[string]interface{}{}
	filteredCount := 0

	for _, tx := range resp.Transactions {
		// Фильтруем по статусу и типу
		if tx.Status != coinspb.Status_COMPLETED || tx.Type != coinspb.Type_TRANSFER {
			filteredCount++
			continue
		}

		log.Printf("Processing transaction %s: From=%v To=%v Amount=%d",
			tx.TransactionId, tx.FromUsername, tx.ToUsername, tx.AmountWhole)

		amount := tx.AmountWhole
		if tx.FromUsername != nil && *tx.FromUsername == username {
			sent = append(sent, map[string]interface{}{
				"toUser": tx.ToUsername,
				"amount": amount,
			})
		} else {
			received = append(received, map[string]interface{}{
				"fromUser": tx.FromUsername,
				"amount":   amount,
			})
		}
	}

	log.Printf("User %s - Filtered out %d transactions", username, filteredCount)
	log.Printf("User %s - Total sent transactions: %d, received transactions: %d", username, len(sent), len(received))

	return &CoinHistoryResponse{
		Received: received,
		Sent:     sent,
	}, nil
}

// Получение баланса через gRPC
func (s *coinsService) GetBalance(username string) (int64, int64, error) {
	req := &coinspb.GetBalanceRequest{Username: username}
	resp, err := s.client.GetBalance(context.Background(), req)
	if err != nil {
		return 0, 0, err
	}
	return resp.BalanceWhole, resp.BalanceFraction, nil
}
