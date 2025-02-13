import bcrypt
from jose import jwt
from src.core.config import settings


def hash_password(password: str) -> str:
    """Хеширует пароль, используя bcrypt."""
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()  # Преобразуем байты в строку для хранения


def verify_password(hashed_password: str, password: str) -> bool:
    """Проверяет пароль, сравнивая его с хешем."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def create_access_token(data: dict) -> str:
    return jwt.encode(
        data,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM.get_secret_value(),
    )
