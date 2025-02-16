import pytest
from tests.utils.accounts import AccountManager, Account


@pytest.mark.asyncio
async def test_buying_merch(account_manager: AccountManager):
    # Получаем аккаунт buyer
    account: Account = account_manager.get_account("buyer")
    client = account.get_client()

    # Установим начальную цену товара и получим текущий баланс
    item_name = "hoody"
    item_price = 300

    # Получаем информацию о пользователе и баланс
    _, user_info = await client.get_user_info()
    initial_balance = user_info["coins"]
    
    # Вычислим максимальное количество товаров, которые можно купить
    max_items_can_buy = initial_balance // item_price

    # Купим товар столько раз, сколько позволяет баланс
    for _ in range(max_items_can_buy):
        _, response = await client.buy_merch(item_name)
        assert response["status"] == "COMPLETED"  # Проверка успешности покупки
    
    # Проверим, что после покупок баланс уменьшился на соответствующую сумму
    _ ,user_info_after_purchase = await client.get_user_info()
    assert user_info_after_purchase["coins"] == initial_balance - max_items_can_buy * item_price

    # Попробуем купить товар еще раз, ожидаем исключение из-за недостаточного баланса
    _, response = await client.buy_merch(item_name)
    assert "INSUFFICIENT_FUNDS" in response
        