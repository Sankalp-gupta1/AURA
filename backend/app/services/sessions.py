"""Only hashes of AURA session credentials are stored in the database."""
import base64
import hashlib
import secrets
import time

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth_session import AuthSession, LoginHandoff


def token_hash(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def verifier_challenge(verifier: str) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).rstrip(b"=").decode("ascii")


def create_session(db: Session, user_id: int) -> tuple[str, int]:
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + settings.SESSION_EXPIRE_MINUTES * 60
    db.execute(delete(AuthSession).where(AuthSession.expires_at <= int(time.time())))
    db.add(AuthSession(token_hash=token_hash(token), user_id=user_id, expires_at=expires_at))
    return token, expires_at


def create_handoff(db: Session, user_id: int, challenge: str) -> str:
    code = secrets.token_urlsafe(32)
    now = int(time.time())
    db.execute(delete(LoginHandoff).where(LoginHandoff.expires_at <= now))
    db.add(LoginHandoff(code_hash=token_hash(code), user_id=user_id, challenge=challenge, expires_at=now + 120))
    return code


def consume_handoff(db: Session, code: str, verifier: str) -> int | None:
    # An atomic DELETE prevents two requests redeeming the same code.
    return db.execute(
        delete(LoginHandoff).where(
            LoginHandoff.code_hash == token_hash(code),
            LoginHandoff.challenge == verifier_challenge(verifier),
            LoginHandoff.expires_at > int(time.time()),
        ).returning(LoginHandoff.user_id)
    ).scalar_one_or_none()
