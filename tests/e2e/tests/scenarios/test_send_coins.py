import random
import pytest
from tests.utils.accounts import Account, AccountManager, ApiGatewayClient


@pytest.mark.asyncio
async def test_sending_coins(account_manager: AccountManager):
    one: ApiGatewayClient = account_manager.get_account("one").get_client()
    second_acc: Account = account_manager.get_account("two")
    two: ApiGatewayClient = second_acc.get_client()

    # Получаем информацию о пользователях и балансах
    _, one_info = await one.get_user_info()
    one_initial_balance = one_info["coins"]
    
    _, two_info = await two.get_user_info()
    two_initial_balance = two_info["coins"]
   
    # Отправим монеты от пользователя one пользователю two
    amount = random.randint(1, one_initial_balance)
    _, response = await one.send_coins(second_acc.username, amount)
    assert response["status"] == "COMPLETED"
        
    # Проверим, что балансы изменились
    _, one_info_after = await one.get_user_info()
    assert one_info_after["coins"] == one_initial_balance - amount
    
    _, two_info_after = await two.get_user_info()
    assert two_info_after["coins"] == two_initial_balance + amount
        