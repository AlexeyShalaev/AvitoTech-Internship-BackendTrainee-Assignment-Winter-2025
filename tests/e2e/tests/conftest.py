import os
import pytest
from tests.utils.accounts import AccountManager  # Импортируем класс AccountManager


@pytest.fixture(scope="session")
async def account_manager():
    """Создание AccountManager один раз на все тесты."""
    
    api_gateway_url = os.getenv("API_GATEWAY_URL", "http://localhost:8080")
    auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:8081")
    
    manager = AccountManager(
        api_gateway_url=api_gateway_url, 
        auth_service_url=auth_service_url,
    )
    # Добавление аккаунтов
    await manager.add_account("one", "password1")
    await manager.add_account("two", "password12")
    
    return manager
