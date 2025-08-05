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
