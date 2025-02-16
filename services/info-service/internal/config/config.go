package config

import (
	"os"
)

type Config struct {
	ServerPort       string
	UserServiceAddr  string
	CoinsServiceAddr string
}

func Load() *Config {
	return &Config{
		ServerPort:       getEnv("SERVER_PORT", "8080"),
		UserServiceAddr:  getEnv("USER_SERVICE", "user-service:50051"),
		CoinsServiceAddr: getEnv("COINS_SERVICE", "coins-service:50051"),
	}
}

// getEnv возвращает значение переменной окружения или значение по умолчанию, если переменная не установлена.
func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}
