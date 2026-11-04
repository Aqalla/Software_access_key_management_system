import secrets
import string
from datetime import datetime, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def generate_api_key(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return "ak_" + "".join(secrets.choice(alphabet) for _ in range(length))


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def calculate_expiration_date(days: int) -> datetime:
    return datetime.utcnow() + timedelta(days=days)


def is_key_expired(expires_at: datetime) -> bool:
    if expires_at is None:
        return False
    return datetime.utcnow() > expires_at
