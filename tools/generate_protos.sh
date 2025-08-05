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
