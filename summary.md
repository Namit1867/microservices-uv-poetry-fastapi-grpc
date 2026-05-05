# Summary: Microservices Architecture with FastAPI + gRPC + Poetry + Docker

## Overview

A minimal **microservices architecture** demonstration using FastAPI as an API Gateway, gRPC for internal service communication, Poetry for dependency management, uv for local development, and Docker Compose for orchestration.

---

## Services

| Service | Protocol | Port | Responsibility |
|---|---|---|---|
| **User Service** | gRPC | 50051 | Provides user information from in-memory store |
| **Order Service** | gRPC | 50052 | Provides order information from in-memory store |
| **API Gateway** | REST (FastAPI) | 8080 | Exposes REST endpoints; proxies to gRPC services |

---

## Architecture

- **External**: Clients communicate with the API Gateway over REST
- **Internal**: API Gateway communicates with User/Order services over gRPC
- **Data**: In-memory stores (demonstration only)

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/users/{user_id}` | Fetch user details |
| `GET` | `/users/{user_id}/orders` | Fetch user + their orders (parallel gRPC calls) |

---

## Key Technologies

| Tool | Purpose |
|---|---|
| **FastAPI** | REST API Gateway |
| **gRPC / Protobuf** | Typed internal service communication |
| **Poetry** | Per-service Python dependency management |
| **uv** | Fast local Python runtime |
| **Docker / Compose** | Containerization and multi-service orchestration |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Namit1867/microservices-uv-poetry-fastapi-grpc.git
cd microservices

# 2. Generate gRPC stubs
bash tools/generate_protos.sh

# 3. Build and run
docker compose up --build

# 4. Test
curl -s http://localhost:8080/users/u1 | jq
curl -s http://localhost:8080/users/u1/orders | jq
```

---

## Project Structure

```
microservices/
├── proto/               # Shared .proto definitions
├── tools/               # Proto generation scripts
├── usersvc/             # User gRPC service
├── ordersvc/            # Order gRPC service
├── gateway/             # FastAPI REST gateway
└── docker-compose.yml
```

---

## Key Concepts

- **API Gateway Pattern** — single entry point aggregating multiple backend services
- **Protocol Buffers** — strongly typed, binary-serialized service contracts
- **Parallel gRPC Calls** — `asyncio.gather` for concurrent upstream requests
- **Error Propagation** — gRPC status codes mapped to HTTP responses
- **Src Layout** — proper Python packaging with `src/` directory structure
