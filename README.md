test

test

test

# 🧩 Microservices Architecture with FastAPI + gRPC + Poetry + Dockers

This project demonstrates a minimal **microservices architecture** using:

- 🔗 **gRPC** for efficient internal service communication
- 🚀 **FastAPI** for RESTful API Gateway
- 📦 **Poetry** for per-service Python dependency management
- ⚡ **uv** for fast local development
- 🐳 **Docker Compose** for multi-service orchestration

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Code Structure](#-code-structure)
- [Service Communication](#-service-communication)
- [API Endpoints](#-api-endpoints)
- [Technologies Used](#-technologies-used)
- [Setup and Running](#-setup-and-running)
- [Development Workflow](#-development-workflow)
- [Troubleshooting](#-troubleshooting)

## 🔍 Project Overview

This project demonstrates a microservices architecture with three main components:

1. **User Service** - A gRPC service that provides user information
2. **Order Service** - A gRPC service that provides order information
3. **API Gateway** - A FastAPI service that exposes REST endpoints and communicates with the gRPC services

The services are containerized using Docker and orchestrated using Docker Compose. Each service is a separate Python package managed by Poetry.

## 🏗️ Architecture

```
┌─────────────┐      REST      ┌─────────────┐
│             │◄──────────────►│             │
│   Client    │                │  API Gateway│
│             │                │  (FastAPI)  │
└─────────────┘                └──────┬──────┘
                                      │
                                      │ gRPC
                                      ▼
                 ┌───────────────────────────────────┐
                 │                                   │
                 ▼                                   ▼
        ┌─────────────┐                     ┌─────────────┐
        │  User Service│                     │ Order Service│
        │    (gRPC)    │                     │    (gRPC)    │
        └──────┬──────┘                     └──────┬──────┘
               │                                   │
               ▼                                   ▼
        ┌─────────────┐                     ┌─────────────┐
        │  User Data   │                     │  Order Data  │
        │  (In-Memory) │                     │  (In-Memory) │
        └─────────────┘                     └─────────────┘
```

- **External Communication**: REST API via FastAPI
- **Internal Communication**: gRPC for efficient service-to-service communication
- **Data Storage**: In-memory data stores (for demonstration purposes)

## 📁 Code Structure

```
microservices/
├── proto/                      # Shared gRPC definitions (.proto)
│   └── user_order.proto        # Protocol Buffer definitions
├── tools/
│   └── generate_protos.sh      # Script to generate gRPC stubs
├── usersvc/                    # User gRPC microservice
│   ├── Dockerfile              # Container definition
│   ├── pyproject.toml          # Poetry dependencies
│   └── src/usersvc/            # Service implementation
│       ├── __init__.py
│       ├── server.py           # gRPC server implementation
│       ├── user_db.py          # In-memory user database
│       ├── user_order_pb2.py   # Generated Protocol Buffers
│       └── user_order_pb2_grpc.py # Generated gRPC stubs
├── ordersvc/                   # Order gRPC microservice
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── src/ordersvc/
│       ├── __init__.py
│       ├── server.py           # gRPC server implementation
│       ├── order_db.py         # In-memory order database
│       ├── user_order_pb2.py   # Generated Protocol Buffers
│       └── user_order_pb2_grpc.py # Generated gRPC stubs
├── gateway/                    # API Gateway (REST → gRPC)
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── src/gateway/
│       ├── main.py             # FastAPI implementation
│       ├── user_order_pb2.py   # Generated Protocol Buffers
│       └── user_order_pb2_grpc.py # Generated gRPC stubs
└── docker-compose.yml          # Service orchestration
```

## 💻 Detailed Code Explanation

### Protocol Buffers Definition (`proto/user_order.proto`)

The `.proto` file defines the service interfaces and message types:

```protobuf
syntax = "proto3";
package app;

service UserService {
  rpc GetUser (GetUserRequest) returns (GetUserResponse) {}
}

service OrderService {
  rpc ListOrders (ListOrdersRequest) returns (ListOrdersResponse) {}
}

message GetUserRequest { string user_id = 1; }
message GetUserResponse { User user = 1; }

message ListOrdersRequest { string user_id = 1; }
message ListOrdersResponse { repeated Order orders = 1; }

message User {
  string id = 1;
  string email = 2;
  string name = 3;
}

message Order {
  string id = 1;
  string user_id = 2;
  string item = 3;
  double total = 4;
}
```

This defines:
- Two services: `UserService` and `OrderService`
- Request/response message types for each service method
- Data structures for `User` and `Order` entities

### User Service Implementation

#### In-Memory Database (`usersvc/src/usersvc/user_db.py`)

```python
from dataclasses import dataclass

@dataclass
class User:
    id: str
    email: str
    name: str

_DB = {
    "u1": User(id="u1", email="alice@example.com", name="Alice"),
    "u2": User(id="u2", email="bob@example.com",   name="Bob"),
}

def get_user(user_id: str) -> User | None:
    return _DB.get(user_id)
```

This module:
- Defines a `User` dataclass with `id`, `email`, and `name` fields
- Creates an in-memory dictionary `_DB` with sample user data
- Provides a `get_user` function to retrieve a user by ID

#### gRPC Server (`usersvc/src/usersvc/server.py`)

```python
import asyncio, grpc
from usersvc import user_order_pb2 as pb
from usersvc import user_order_pb2_grpc as rpc
from usersvc.user_db import get_user

class UserService(rpc.UserServiceServicer):
    async def GetUser(self, request: pb.GetUserRequest, context):
        u = get_user(request.user_id)
        if not u:
            await context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        return pb.GetUserResponse(user=pb.User(id=u.id, email=u.email, name=u.name))

async def serve() -> None:
    server = grpc.aio.server()
    rpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    print("UserService listening on :50051")
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
```

This module:
- Implements the `UserService` gRPC service defined in the proto file
- Uses the async gRPC server from `grpc.aio`
- Handles the `GetUser` method by querying the in-memory database
- Returns a proper gRPC error if the user is not found
- Starts the server on port 50051

### Order Service Implementation

#### In-Memory Database (`ordersvc/src/ordersvc/order_db.py`)

```python
from dataclasses import dataclass
from typing import List

@dataclass
class Order:
    id: str
    user_id: str
    item: str
    total: float

_DB: List[Order] = [
    Order(id="o1", user_id="u1", item="Headphones", total=199.0),
    Order(id="o2", user_id="u1", item="Mic",        total=129.5),
    Order(id="o3", user_id="u2", item="Keyboard",   total=89.0),
]

def list_orders(user_id: str) -> list[Order]:
    return [o for o in _DB if o.user_id == user_id]
```

This module:
- Defines an `Order` dataclass with `id`, `user_id`, `item`, and `total` fields
- Creates an in-memory list `_DB` with sample order data
- Provides a `list_orders` function to retrieve orders by user ID

#### gRPC Server (`ordersvc/src/ordersvc/server.py`)

```python
import asyncio, grpc
from ordersvc import user_order_pb2 as pb
from ordersvc import user_order_pb2_grpc as rpc
from ordersvc.order_db import list_orders

class OrderService(rpc.OrderServiceServicer):
    async def ListOrders(self, request: pb.ListOrdersRequest, context):
        orders = list_orders(request.user_id)
        return pb.ListOrdersResponse(
            orders=[pb.Order(id=o.id, user_id=o.user_id, item=o.item, total=o.total) for o in orders]
        )

async def serve() -> None:
    server = grpc.aio.server()
    rpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port("[::]:50052")
    await server.start()
    print("OrderService listening on :50052")
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
```

This module:
- Implements the `OrderService` gRPC service defined in the proto file
- Uses the async gRPC server from `grpc.aio`
- Handles the `ListOrders` method by querying the in-memory database
- Starts the server on port 50052

### API Gateway Implementation (`gateway/src/gateway/main.py`)

```python
import asyncio, grpc
from fastapi import FastAPI, HTTPException
from gateway import user_order_pb2 as pb
from gateway import user_order_pb2_grpc as rpc

app = FastAPI(title="API Gateway")

async def user_stub():
    ch = grpc.aio.insecure_channel("usersvc:50051")
    return rpc.UserServiceStub(ch)

async def order_stub():
    ch = grpc.aio.insecure_channel("ordersvc:50052")
    return rpc.OrderServiceStub(ch)

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    stub = await user_stub()
    try:
        res = await stub.GetUser(pb.GetUserRequest(user_id=user_id), timeout=2.0)
        return {"id": res.user.id, "email": res.user.email, "name": res.user.name}
    except grpc.aio.AioRpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(404, "User not found")
        raise HTTPException(502, f"upstream error: {e.code().name}")

@app.get("/users/{user_id}/orders")
async def get_user_with_orders(user_id: str):
    u_stub, o_stub = await user_stub(), await order_stub()
    try:
        # parallel calls with timeout
        user_task = u_stub.GetUser(pb.GetUserRequest(user_id=user_id), timeout=2.0)
        orders_task = o_stub.ListOrders(pb.ListOrdersRequest(user_id=user_id), timeout=2.0)
        user_res, orders_res = await asyncio.gather(user_task, orders_task)
        return {
            "user": {"id": user_res.user.id, "email": user_res.user.email, "name": user_res.user.name},
            "orders": [{"id": o.id, "item": o.item, "total": o.total} for o in orders_res.orders],
        }
    except grpc.aio.AioRpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(404, "User not found")
        raise HTTPException(502, f"upstream error: {e.code().name}")
```

This module:
- Creates a FastAPI application that serves as the API gateway
- Defines helper functions to create gRPC client stubs for the User and Order services
- Implements two REST endpoints:
  - `/users/{user_id}` - Gets user information
  - `/users/{user_id}/orders` - Gets user information and their orders
- Handles gRPC errors and maps them to appropriate HTTP status codes
- Uses `asyncio.gather` to make parallel gRPC calls for better performance

## 🔄 Service Communication

### Internal Communication (gRPC)

Services communicate internally using gRPC, which offers several advantages:

1. **Strongly Typed**: Protocol Buffers provide type safety across services
2. **Efficient**: Binary serialization is more compact than JSON
3. **Bidirectional Streaming**: Though not used in this example, gRPC supports streaming
4. **Code Generation**: Automatic client/server code generation from `.proto` files

The `generate_protos.sh` script generates the necessary Python code from the `.proto` file:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROTO_DIR="$ROOT_DIR/proto"

# Output paths inside each service package
USER_OUT="$ROOT_DIR/usersvc/src/usersvc"
ORDER_OUT="$ROOT_DIR/ordersvc/src/ordersvc"
GW_OUT="$ROOT_DIR/gateway/src/gateway"

# Ensure grpc tools available in your shell (dev) environment:
# uv tool run pipx install grpcio-tools (or use Poetry dev-deps per service)
python3 -m grpc_tools.protoc \
  -I="$PROTO_DIR" \
  --python_out="$USER_OUT" \
  --grpc_python_out="$USER_OUT" \
  "$PROTO_DIR/user_order.proto"

python3 -m grpc_tools.protoc \
  -I="$PROTO_DIR" \
  --python_out="$ORDER_OUT" \
  --grpc_python_out="$ORDER_OUT" \
  "$PROTO_DIR/user_order.proto"

python3 -m grpc_tools.protoc \
  -I="$PROTO_DIR" \
  --python_out="$GW_OUT" \
  --grpc_python_out="$GW_OUT" \
  "$PROTO_DIR/user_order.proto"

# Fix relative imports if needed (Python <=3.11 sometimes needs package paths).
echo "Protos generated."
```

This script:
- Locates the proto file and output directories
- Runs the Protocol Buffer compiler (`protoc`) with the gRPC Python plugin
- Generates Python code for each service
- Places the generated files in the appropriate service directories

### External Communication (REST)

The API Gateway exposes REST endpoints for external clients, which offers:

1. **Familiar Interface**: REST is widely understood and used
2. **Easy Testing**: Can be tested with simple tools like `curl` or browsers
3. **Aggregation**: The gateway can combine data from multiple services
4. **Error Handling**: Translates gRPC errors to HTTP status codes

## 🌐 API Endpoints

The API Gateway exposes the following REST endpoints:

### Get User Information

```
GET /users/{user_id}
```

**Example Response:**
```json
{
  "id": "u1",
  "email": "alice@example.com",
  "name": "Alice"
}
```

**Status Codes:**
- `200 OK`: User found
- `404 Not Found`: User not found
- `502 Bad Gateway`: Upstream service error

### Get User with Orders

```
GET /users/{user_id}/orders
```

**Example Response:**
```json
{
  "user": {
    "id": "u1",
    "email": "alice@example.com",
    "name": "Alice"
  },
  "orders": [
    {
      "id": "o1",
      "item": "Headphones",
      "total": 199.0
    },
    {
      "id": "o2",
      "item": "Mic",
      "total": 129.5
    }
  ]
}
```

**Status Codes:**
- `200 OK`: User and orders found
- `404 Not Found`: User not found
- `502 Bad Gateway`: Upstream service error

## 📦 Technologies Used

| Tool        | Purpose                                   | Implementation                                |
|-------------|-------------------------------------------|----------------------------------------------|
| **FastAPI** | REST API for external consumers           | Gateway service exposes REST endpoints        |
| **gRPC**    | Internal service communication            | User and Order services communicate via gRPC  |
| **Protobuf**| Define typed messages & services          | `user_order.proto` defines the service interfaces |
| **Poetry**  | Manage Python deps & packaging            | Each service has its own `pyproject.toml`     |
| **uv**      | Fast, isolated Python runtime             | Used for local development                    |
| **Docker**  | Containerize each service                 | Each service has its own `Dockerfile`         |
| **Compose** | Run multiple services together            | `docker-compose.yml` orchestrates all services |

### Dependencies

#### User Service (`usersvc/pyproject.toml`)

```toml
[tool.poetry]
name = "usersvc"
version = "0.1.0"
description = "User gRPC microservice"
authors = ["Namit Jain <namit.cs.rdjps@gmail.com>"]
packages = [{ include = "usersvc", from = "src" }]

[tool.poetry.dependencies]
python = "^3.11"
grpcio = "^1.66"
grpcio-tools = "^1.66"

[tool.poetry.group.dev.dependencies]
mypy = "^1.10"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

#### Order Service (`ordersvc/pyproject.toml`)

```toml
[tool.poetry]
name = "ordersvc"
version = "0.1.0"
description = "Order gRPC microservice"
authors = ["You <you@example.com>"]
packages = [{ include = "ordersvc", from = "src" }]

[tool.poetry.dependencies]
python = "^3.11"
grpcio = "^1.66"
grpcio-tools = "^1.66"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

#### API Gateway (`gateway/pyproject.toml`)

```toml
[tool.poetry]
name = "gateway"
version = "0.1.0"
description = "REST API gateway aggregating User and Order services"
authors = ["You <you@example.com>"]
packages = [{ include = "gateway", from = "src" }]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.112"
uvicorn = {extras = ["standard"], version = "^0.30"}
grpcio = "^1.66"
grpcio-tools = "^1.66"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## 🚀 Setup and Running

### Docker Setup

The project uses Docker Compose to orchestrate the services:

```yaml
version: "3.9"
services:
  usersvc:
    build: ./usersvc
    image: demo/usersvc
    container_name: usersvc
    ports: ["50051:50051"]

  ordersvc:
    build: ./ordersvc
    image: demo/ordersvc
    container_name: ordersvc
    ports: ["50052:50052"]

  gateway:
    build: ./gateway
    image: demo/gateway
    container_name: gateway
    depends_on:
      - usersvc
      - ordersvc
    ports: ["8080:8080"]
```

Each service has its own Dockerfile:

#### User Service (`usersvc/Dockerfile`)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.3

# Copy source code BEFORE poetry install
COPY pyproject.toml poetry.lock* ./
COPY src ./src

# Now run install (it will find the package in src/usersvc)
RUN poetry install --no-interaction --no-ansi

EXPOSE 50052
CMD ["poetry", "run", "python", "src/usersvc/server.py"]
```

#### Order Service (`ordersvc/Dockerfile`)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.3

# Copy source code BEFORE poetry install
COPY pyproject.toml poetry.lock* ./
COPY src ./src

# Now run install (it will find the package in src/ordersvc)
RUN poetry install --no-interaction --no-ansi

EXPOSE 50052
CMD ["poetry", "run", "python", "src/ordersvc/server.py"]
```

#### API Gateway (`gateway/Dockerfile`)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.3

# Copy source code BEFORE poetry install
COPY pyproject.toml poetry.lock* ./
COPY src ./src

# Now run install (it will find the package in src/ordersvc)
RUN poetry install --no-interaction --no-ansi

EXPOSE 8080
CMD ["poetry", "run", "uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Quick Start (Docker)

1. **Clone the repo**

```bash
git clone https://github.com/Namit1867/microservices-uv-poetry-fastapi-grpc.git
cd microservices
```

2. **Generate gRPC Stubs**

```bash
bash tools/generate_protos.sh
```

This generates `user_order_pb2.py` and `user_order_pb2_grpc.py` into:
- `usersvc/src/usersvc/`
- `ordersvc/src/ordersvc/`
- `gateway/src/gateway/`

3. **Build and run services**

```bash
docker compose up --build
```

4. **Test the API**

```bash
# Get User Info
curl -s http://localhost:8080/users/u1 | jq

# Get User + Orders
curl -s http://localhost:8080/users/u1/orders | jq
```

## 🧪 Local Development Workflow

For local development without Docker:

1. **Install uv (if not installed)**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Install Poetry (per container)**

```bash
uv pip install poetry
```

3. **Install Python deps per service**

```bash
cd usersvc && poetry install
cd ordersvc && poetry install
cd gateway && poetry install
```

4. **Run services locally (in separate terminals)**

```bash
# Generate protos first
bash tools/generate_protos.sh

# Run usersvc
cd usersvc && poetry run python src/usersvc/server.py

# Run ordersvc
cd ordersvc && poetry run python src/ordersvc/server.py

# Run gateway
cd gateway && poetry run uvicorn gateway.main:app --host 0.0.0.0 --port 8080
```

## 🛠️ Troubleshooting

### Common Issues

**Problem**: `ImportError: cannot import name 'user_order_pb2'`

**Solution**: Ensure you're importing from the correct path:

```python
from usersvc import user_order_pb2
```

Verify the stub files are generated into `src/<service>/`.

**Problem**: `does not contain any element` (during poetry install)

**Solution**: Ensure your `src/ordersvc/` or `src/usersvc/` has an `__init__.py` and actual `.py` files.

Make sure `COPY src ./src` happens before `poetry install` in Dockerfile.

## 🧠 Key Concepts Demonstrated

| Concept | Implementation |
|---------|----------------|
| **API Gateway Pattern** | FastAPI service aggregates responses from multiple gRPC services |
| **Service Boundaries** | Clear separation between User and Order services |
| **Protocol Buffers** | Strongly typed message definitions in `.proto` file |
| **Error Handling** | Proper error propagation from gRPC to HTTP |
| **Parallel Processing** | Using `asyncio.gather` for concurrent gRPC calls |
| **Timeouts** | Setting timeouts on gRPC calls for resilience |
| **Containerization** | Each service has its own Docker container |
| **Dependency Management** | Poetry for managing Python dependencies |
| **Package Structure** | Proper Python package structure with `src` layout |
