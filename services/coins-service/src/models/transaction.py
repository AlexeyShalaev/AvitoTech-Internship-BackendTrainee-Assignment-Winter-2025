from enum import StrEnum

from sqlalchemy import TIMESTAMP, VARCHAR, BigInteger, CheckConstraint, Column, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from src.models import BaseTable


class TransactionStatus(StrEnum):
    COMPLETED = "COMPLETED"
    ROLLBACKED = "ROLLBACKED"
    
    
class TransactionType(StrEnum):
    TRANSFER = "TRANSFER"
    PAYMENT = "PAYMENT"
    REPLENISHMENT = "REPLENISHMENT"


class Transaction(BaseTable):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True)
    from_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    to_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    from_username = Column(VARCHAR, nullable=True)
    to_username = Column(VARCHAR, nullable=True)
    amount_whole = Column(BigInteger, nullable=False)
    amount_fraction = Column(BigInteger, nullable=False)
    type = Column(Enum(TransactionType, name="transaction_type"), nullable=False)
    status = Column(Enum(TransactionStatus, name="transaction_status"), nullable=False, default=TransactionStatus.COMPLETED)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.timezone("UTC", func.now()),
    )
    
    __table_args__ = (
        CheckConstraint("amount_fraction >= 0 AND amount_fraction < 100", name="check_transaction_fraction"),  # 0-99
    )
