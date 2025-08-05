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
