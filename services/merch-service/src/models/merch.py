from sqlalchemy import VARCHAR, BigInteger, Column
from sqlalchemy.dialects.postgresql import UUID
from src.models import BaseTable


class Merch(BaseTable):
    __tablename__ = "merchandises"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(VARCHAR(128), nullable=False)
    price = Column(BigInteger, nullable=False)
