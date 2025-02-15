package services

import (
	"context"

	"info-service/internal/proto/coins"
	"google.golang.org/grpc"
)

type CoinsService interface {
	GetTransactionHistory(username string) (*CoinHistoryResponse, error)
	GetBalance(username string) (int64, int64, error)
}

type CoinHistoryResponse struct {
	Received       []map[string]interface{}
	Sent           []map[string]interface{}
}

type coinsService struct {
	client coinspb.CoinsServiceClient
}

func NewCoinsService(conn *grpc.ClientConn) CoinsService {
	return &coinsService{client: coinspb.NewCoinsServiceClient(conn)}
}

// Получение истории транзакций + баланс из gRPC
func (s *coinsService) GetTransactionHistory(username string) (*CoinHistoryResponse, error) {
	// Запрашиваем историю транзакций
	req := &coinspb.GetTransactionHistoryRequest{Username: username}
	resp, err := s.client.GetTransactionHistory(context.Background(), req)
	if err != nil {
		return nil, err
	}

	// Обрабатываем транзакции
	received := []map[string]interface{}{}
	sent := []map[string]interface{}{}

	for _, tx := range resp.Transactions {
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

	return &CoinHistoryResponse{
		Received:       received,
		Sent:           sent,
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
