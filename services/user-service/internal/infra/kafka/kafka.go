package kafka

import (
	"context"
	"encoding/json"
	"log"

	"github.com/segmentio/kafka-go"
)

type KafkaProducer struct {
	writer *kafka.Writer
}

func NewKafkaProducer(brokers []string, topic string) *KafkaProducer {
	return &KafkaProducer{
		writer: &kafka.Writer{
			Addr:     kafka.TCP(brokers...),
			Topic:    topic,
			Balancer: &kafka.LeastBytes{},
		},
	}
}

func (kp *KafkaProducer) SendMessage(ctx context.Context, eventType, userID, username string) error {
	message := map[string]string{
		"event":    eventType,
		"user_id":  userID,
		"username": username,
	}

	data, err := json.Marshal(message)
	if err != nil {
		return err
	}

	err = kp.writer.WriteMessages(ctx, kafka.Message{
		Value: data,
	})
	if err != nil {
		log.Printf("Kafka error: %v", err)
	}
	return err
}

func (kp *KafkaProducer) Close() {
	kp.writer.Close()
}

// EnsureTopicExists проверяет существование топика и создаёт его при необходимости.
func EnsureTopicExists(brokers []string, topic string) error {
	conn, err := kafka.Dial("tcp", brokers[0])
	if err != nil {
		return err
	}
	defer conn.Close()

	// Получаем список существующих топиков
	partitions, err := conn.ReadPartitions()
	if err != nil {
		return err
	}

	exists := false
	for _, p := range partitions {
		if p.Topic == topic {
			exists = true
			break
		}
	}

	if exists {
		log.Printf("Kafka topic '%s' already exists", topic)
		return nil
	}

	// Создаём топик, если его нет
	err = conn.CreateTopics(kafka.TopicConfig{
		Topic:             topic,
		NumPartitions:     3,  // Количество партиций (можно изменить)
		ReplicationFactor: 1,  // Фактор репликации (должен быть >= 1)
	})
	if err != nil {
		return err
	}

	log.Printf("Kafka topic '%s' created successfully", topic)
	return nil
}
