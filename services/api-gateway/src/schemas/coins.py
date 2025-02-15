from pydantic import BaseModel, Field


class SendCoinsRequest(BaseModel):
    to_user: str = Field(..., min_length=1)  # Минимальная длина 1 символ (не пустая строка)
    amount: int = Field(..., gt=0)           # Должно быть больше 0
