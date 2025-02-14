from sqlalchemy import VARCHAR, BigInteger, CheckConstraint, Column
from sqlalchemy.dialects.postgresql import UUID
from src.models import BaseTable


class Account(BaseTable):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    username = Column(VARCHAR(64), unique=True, nullable=False)
    balance_whole = Column(BigInteger, nullable=False, default=0)  # Целая часть
    balance_fraction = Column(BigInteger, nullable=False, default=0)  # Дробная часть
    
    __table_args__ = (
        CheckConstraint("balance_whole >= 0 AND balance_fraction >= 0 AND balance_fraction < 100", name="check_balance_valid"),
    )
