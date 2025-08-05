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
