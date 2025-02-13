from jose import jwt
from src.core.config import settings
from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(hashed_password: str, password: str) -> bool:
    return check_password_hash(hashed_password, password)


def create_access_token(data: dict) -> str:
    return jwt.encode(
        data,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM.get_secret_value(),
    )
