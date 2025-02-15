package kafka_consumer

import (
	"context"
	"encoding/json"
	"log"
	"user-service/internal/services/user"

	"github.com/segmentio/kafka-go"
)

// ======= Консумер =======
type KafkaConsumer struct {
	reader  *kafka.Reader
	service *user.Service
}

func NewKafkaConsumer(brokers []string, topic string, service *user.Service) *KafkaConsumer {
	return &KafkaConsumer{
		reader: kafka.NewReader(kafka.ReaderConfig{
			Brokers: brokers,
			Topic:   topic,
			GroupID: "merch-consumer-group",
		}),
		service: service,
	}
}

func (kc *KafkaConsumer) StartConsuming(ctx context.Context) {
	log.Println("Starting Kafka Consumer for topic 'merch'...")

	for {
		msg, err := kc.reader.ReadMessage(ctx)
		if err != nil {
			log.Printf("Kafka Consumer error: %v", err)
			continue
		}

		var message struct {
			TransactionID string  `json:"transaction_id"`
			Status        string  `json:"status"`
			Username      string  `json:"username"`
			MerchName     string  `json:"merch_name"`
			Price         float64 `json:"price"`
		}

		if err := json.Unmarshal(msg.Value, &message); err != nil {
			log.Printf("Failed to unmarshal Kafka message: %v", err)
			continue
		}

		// Обновляем инвентарь, если статус успешный
		if message.Status == "COMPLETED" {
			err := kc.service.UpdateUserInventory(ctx, message.Username, message.MerchName)
			if err != nil {
				log.Printf("Failed to update inventory: %v", err)
			}
		}
	}
}

func (kc *KafkaConsumer) Close() {
	kc.reader.Close()
}
