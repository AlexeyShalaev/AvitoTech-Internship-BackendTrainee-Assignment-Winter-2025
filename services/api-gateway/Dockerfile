# Stage 1: Generate grpc stubs
FROM python:3.11-alpine AS build

# Set the working directory
WORKDIR /app

# Install grpcio-tools
RUN pip install --no-cache-dir grpcio-tools==1.67.*

# Copy the proto files
COPY --from=proto . ./proto

RUN mkdir stubs

# Compile the proto files into Python gRPC files
RUN find ./proto -name "*.proto" -exec python -m grpc_tools.protoc \
    --python_out=stubs \
    --grpc_python_out=stubs \
    --proto_path=./proto {} +

# Stage 2: Run Application
FROM python:3.11-slim

# Stage 2.1: Prepare env

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/* \
    && pip install -U pip

# Stage 2.2: Copy, prepare and start app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PYTHONPATH=/app:/app/stubs

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy compiled proto files from the build stage
COPY --from=build /app/stubs/ ./stubs/

COPY ./src /app/src

CMD ["python", "src/main.py"]
