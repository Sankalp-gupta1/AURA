import re
import time

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.auth_session import AuthSession
from app.models.user import User
from app.services.sessions import token_hash


def bearer_token(authorization: str | None) -> str | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    return token if re.fullmatch(r"[A-Za-z0-9_-]{43}", token) else None


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    # Next.js reads its HttpOnly cookie and supplies the private bearer header.
    # Browser cookies and the old JWT/localStorage tokens are not accepted here.
    token = bearer_token(authorization)
    if not token:
        raise HTTPException(401, "Not authenticated")
    session = db.get(AuthSession, token_hash(token))
    if not session or session.expires_at <= int(time.time()):
        raise HTTPException(401, "Invalid or expired session")
    user = db.get(User, session.user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user
