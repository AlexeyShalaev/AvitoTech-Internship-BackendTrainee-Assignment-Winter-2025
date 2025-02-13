from sqlalchemy import TIMESTAMP, Column, Integer
from sqlalchemy.dialects.postgresql import UUID, VARCHAR
from src.models import BaseTable


class Session(BaseTable):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    refresh_token = Column(UUID(as_uuid=True), unique=True, nullable=False)
    user_agent = Column(VARCHAR(200), nullable=False)
    ip = Column(VARCHAR(39), nullable=False)  # IPv6 max length is 39
    expires_in = Column(TIMESTAMP(timezone=True), nullable=False)
