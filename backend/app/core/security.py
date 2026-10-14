import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


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
