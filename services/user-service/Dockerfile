FROM golang:1.24 AS builder

WORKDIR /app

# Устанавливаем protoc
RUN apt-get update && apt-get install -y \
    unzip \
    curl

# Скачиваем и устанавливаем protoc (ПРАВИЛЬНЫЙ URL)
RUN curl -LO https://github.com/protocolbuffers/protobuf/releases/download/v24.4/protoc-24.4-linux-x86_64.zip \
    && ls -lah protoc-24.4-linux-x86_64.zip \
    && unzip protoc-24.4-linux-x86_64.zip -d /usr/local \
    && rm protoc-24.4-linux-x86_64.zip

# Устанавливаем protoc и плагины
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
RUN go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Copy the proto files
COPY --from=proto user.proto /proto/user.proto

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN mkdir internal/proto

# Генерируем gRPC-код
RUN protoc --go_out=. --go-grpc_out=. -I/proto /proto/user.proto

# Сборка бинарника
RUN go build -o user-service ./cmd/

# Финальный контейнер
FROM golang:1.24

WORKDIR /app

COPY --from=builder /app/user-service /app/user-service
COPY --from=builder /app/migrations /app/migrations

# Установка grpc_health_probe
COPY --from=slyncio/grpc-health-probe /bin/grpc_health_probe /bin/grpc_health_probe

CMD ["/app/user-service"]
