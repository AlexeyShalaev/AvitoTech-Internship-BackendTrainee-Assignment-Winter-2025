import time
from tests.clients import AuthClient, ApiGatewayClient


class Account:
    def __init__(self, username: str, password: str, auth_service_url: str, api_gateway_url: str):
        self.username = username
        self.password = password
        self.auth_service_url = auth_service_url
        self.api_gateway_url = api_gateway_url
        self.token = None  # Токен будет получен позже
        self.auth_client = AuthClient(auth_service_url)
        self.gateway_client = ApiGatewayClient(api_gateway_url, token=None)

    async def authenticate(self):
        """Получаем токен для аккаунта и инициализируем клиент для API Gateway."""
        self.token = await self.auth_client.authenticate(self.username, self.password)
        self.gateway_client = ApiGatewayClient(self.api_gateway_url, self.token)

    def get_client(self):
        """Возвращаем клиент для API Gateway с токеном для этого аккаунта."""
        if self.token is None:
            raise ValueError(f"Account {self.username} is not authenticated.")
        return self.gateway_client
    
    
class AccountManager:
    def __init__(self, api_gateway_url: str, auth_service_url: str, prefix: str | None = None):
        self.api_gateway_url = api_gateway_url
        self.auth_service_url = auth_service_url
        self.accounts = {}  # Словарь для хранения аккаунтов
        
        if prefix is None:
            self.prefix = str(int(time.time()))
        else:
            self.prefix = prefix

    async def add_account(self, username: str, password: str):
        """Добавление нового аккаунта."""
        account = Account(f"{username}_{self.prefix}", password, self.auth_service_url, self.api_gateway_url)
        await account.authenticate()  # Получаем токен для аккаунта
        self.accounts[username] = account
    
    def get_account(self, username: str) -> Account:
        """Получить аккаунт по имени."""
        if username not in self.accounts:
            raise ValueError(f"Account {username} not found.")
        return self.accounts[username]
