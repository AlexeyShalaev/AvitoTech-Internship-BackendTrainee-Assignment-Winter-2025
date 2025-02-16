import httpx


class ApiGatewayClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.client = httpx.AsyncClient()

    async def send_coins(self, to_user: str, amount: int):
        """Send coins to a user."""
        url = f"{self.base_url}/api/coins/send"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"to_user": to_user, "amount": amount}
        
        response = await self.client.post(url, json=data, headers=headers)
        return response.status_code, response.json()

    async def get_user_info(self):
        """Get current user's info."""
        url = f"{self.base_url}/api/info"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = await self.client.get(url, headers=headers)
        return response.status_code, response.json()

    async def buy_merch(self, name: str):
        """Buy merch for a specific item."""
        url = f"{self.base_url}/api/merch/buy/{name}"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = await self.client.post(url, headers=headers)
        return response.status_code, response.json()
