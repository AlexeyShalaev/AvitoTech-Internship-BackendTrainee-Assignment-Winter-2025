import uuid

import user_pb2

from src.utils.security import hash_password


class MockUserServiceClient:
    def __init__(self, id: str | None = None) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.username: str = 'username'
        self.password: str = 'password'

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def create_if_not_exists(self, username: str, password: str) -> user_pb2.CreateIfNotExistsResponse:
        return user_pb2.CreateIfNotExistsResponse(
            id=self.id,
            username=self.username,
            hashed_password=hash_password(self.password),
            is_new=False,
        )
        
    async def get_by_id(self, user_id: str) -> user_pb2.GetUserByIdResponse:
        return user_pb2.GetUserByIdResponse(
            id=self.id,
            username=self.username,
            hashed_password=hash_password(self.password),
        )
