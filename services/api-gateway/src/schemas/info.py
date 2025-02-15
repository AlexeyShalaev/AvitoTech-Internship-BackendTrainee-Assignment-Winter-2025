from pydantic import BaseModel


class Item(BaseModel):
    type: str
    quantity: int


class ReceivedCoins(BaseModel):
    fromUser: str
    amount: int
    
    
class SentCoins(BaseModel):
    toUser: str
    amount: int


class CoinsHistory(BaseModel):
    received: list[ReceivedCoins]
    sent: list[SentCoins]


class InfoResponse(BaseModel):
    coins: int
    inventory: list[Item]
    coinHistory: CoinsHistory
    