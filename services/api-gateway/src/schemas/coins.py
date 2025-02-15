from pydantic import BaseModel


class SendCoinsRequest(BaseModel):
    to_user: str
    amount: int
