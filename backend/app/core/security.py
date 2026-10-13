import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from jose import jwt, JWTError

from app.core.config import settings


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        return int(user_id) if user_id is not None else None
    except (JWTError, ValueError, TypeError):
        return None


def _fernet() -> Fernet:
    """Derive a stable Fernet key from SECRET_KEY for OAuth-token encryption."""
    digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(value: str) -> str:
    if not value:
        return ""
    if value.startswith("enc:"):
        return value
    encrypted = _fernet().encrypt(value.encode("utf-8")).decode("utf-8")
    return f"enc:{encrypted}"


def decrypt_secret(value: str) -> str:
    if not value:
        return ""
    # Backwards compatible with existing local DB rows that stored plaintext.
    if not value.startswith("enc:"):
        return value
    try:
        return _fernet().decrypt(value[4:].encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return ""
