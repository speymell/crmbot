from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a bcrypt hash."""
    password_bytes = password.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


def create_access_token(*, user_id: int, business_id: int, role: str) -> str:
    now = datetime.now(tz=timezone.utc)
    exp = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {
        "sub": str(user_id),
        "business_id": business_id,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
