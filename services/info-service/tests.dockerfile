FROM golang:1.24

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
COPY --from=proto . /proto

COPY go.mod go.sum ./
RUN go mod download

COPY . .

# Генерируем gRPC-код
RUN protoc --go_out=. --go-grpc_out=. -I/proto /proto/user.proto /proto/coins.proto

CMD ["go", "test", "./..."]
