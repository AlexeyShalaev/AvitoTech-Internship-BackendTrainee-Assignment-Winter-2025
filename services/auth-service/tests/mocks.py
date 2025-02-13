import uuid

import user_pb2

from src.utils.security import hash_password


class MockUserServiceClient:
    def __init__(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def create_if_not_exists(self, username: str, password: str) -> user_pb2.CreateIfNotExistsResponse:
        return user_pb2.CreateIfNotExistsResponse(
            id=str(uuid.uuid4()),
            username='username',
            hashed_password=hash_password('password'),
            is_new=False,
        )
