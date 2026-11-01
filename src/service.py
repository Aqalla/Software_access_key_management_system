from datetime import datetime
from sqlalchemy.orm import Session
from src.database import User, ApiKey
from src.schemas import UserCreate, ApiKeyCreate
from src.utils import generate_api_key, hash_password, verify_password, calculate_expiration_date, is_key_expired


class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        hashed_password = hash_password(user.password)
        db_user = User(username=user.username, password_hash=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user


class ApiKeyService:
    @staticmethod
    def create_api_key(db: Session, user_id: int, api_key: ApiKeyCreate) -> ApiKey:
        key_value = generate_api_key()
        expires_at = None
        if api_key.expires_in_days:
            expires_at = calculate_expiration_date(api_key.expires_in_days)

        db_key = ApiKey(
            key_value=key_value,
            name=api_key.name,
            description=api_key.description,
            owner_id=user_id,
            expires_at=expires_at,
        )
        db.add(db_key)
        db.commit()
        db.refresh(db_key)
        return db_key

    @staticmethod
    def get_api_key_by_value(db: Session, key_value: str) -> ApiKey:
        return db.query(ApiKey).filter(ApiKey.key_value == key_value).first()

    @staticmethod
    def get_user_api_keys(db: Session, user_id: int) -> list[ApiKey]:
        return db.query(ApiKey).filter(ApiKey.owner_id == user_id).all()

    @staticmethod
    def revoke_api_key(db: Session, key_id: int, user_id: int) -> ApiKey:
        api_key = (
            db.query(ApiKey)
            .filter(ApiKey.id == key_id, ApiKey.owner_id == user_id)
            .first()
        )
        if not api_key:
            return None
        api_key.is_revoked = True
        api_key.is_active = False
        db.commit()
        db.refresh(api_key)
        return api_key

    @staticmethod
    def validate_api_key(db: Session, key_value: str) -> dict:
        api_key = ApiKeyService.get_api_key_by_value(db, key_value)
        if not api_key:
            return {
                "is_valid": False,
                "is_active": False,
                "is_expired": False,
                "is_revoked": False,
                "key_id": None,
                "key_name": None,
                "owner_id": None,
                "expires_at": None,
            }

        expired = is_key_expired(api_key.expires_at)
        is_valid = api_key.is_active and not api_key.is_revoked and not expired

        return {
            "is_valid": is_valid,
            "is_active": api_key.is_active,
            "is_expired": expired,
            "is_revoked": api_key.is_revoked,
            "key_id": api_key.id,
            "key_name": api_key.name,
            "owner_id": api_key.owner_id,
            "expires_at": api_key.expires_at,
        }
