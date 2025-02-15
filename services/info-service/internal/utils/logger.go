package utils

import (
	"go.uber.org/zap"
)

var logger, _ = zap.NewProduction()

func GetLogger() *zap.Logger {
	return logger
}
