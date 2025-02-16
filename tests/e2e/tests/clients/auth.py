import httpx


class AuthClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def authenticate(self, username: str, password: str) -> str:
        response = await self.client.post(
            f"{self.base_url}/api/auth",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()["token"]
