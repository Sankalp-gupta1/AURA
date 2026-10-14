import logging
import re
import secrets

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Response
from fastapi.responses import RedirectResponse
from googleapiclient.discovery import build
from pydantic import BaseModel, Field
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.api.deps import bearer_token, get_current_user
from app.core.config import settings
from app.core.security import encrypt_secret
from app.db.database import get_db
from app.models.auth_session import AuthSession
from app.models.user import User
from app.schemas.schemas import UserOut
from app.services import google_oauth
from app.services.sessions import consume_handoff, create_handoff, create_session, token_hash

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])
OAUTH_STATE_COOKIE = "aura_oauth_state"


def _is_production() -> bool:
    return settings.ENVIRONMENT != "development"


def _redirect(path: str) -> RedirectResponse:
    response = RedirectResponse(f"{settings.frontend_origin}{path}", status_code=303)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.delete_cookie(OAUTH_STATE_COOKIE, samesite="lax", secure=_is_production())
    # Remove the cookie from older releases. New sessions live on the frontend.
    response.delete_cookie("aura_session", samesite="none" if _is_production() else "lax", secure=_is_production())
    return response


@router.get("/google/login")
def google_login(challenge: str = ""):
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", challenge):
        raise HTTPException(400, "Start sign-in from the AURA website.")
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(503, "Google sign-in is not configured yet.")
    state = secrets.token_urlsafe(32)
    google_verifier = secrets.token_urlsafe(64)
    response = RedirectResponse(google_oauth.build_auth_url(state, google_verifier))
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.set_cookie(OAUTH_STATE_COOKIE, f"{state}.{challenge}.{google_verifier}", httponly=True,
                        samesite="lax", secure=_is_production(), max_age=600)
    return response


@router.get("/google/callback")
def google_callback(
    code: str = "", state: str = "", error: str = "",
    aura_oauth_state: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    parts = (aura_oauth_state or "").split(".")
    cookie_state, challenge, google_verifier = parts if len(parts) == 3 else ("", "", "")
    if (not state or not secrets.compare_digest(state, cookie_state)
            or not re.fullmatch(r"[A-Za-z0-9_-]{43}", challenge)
            or not re.fullmatch(r"[A-Za-z0-9_-]{86}", google_verifier)):
        return _redirect("/?error=oauth_state")
    if error or not code:
        return _redirect("/?error=oauth_cancelled")
    try:
        creds = google_oauth.exchange_code(code, google_verifier)
        userinfo = build("oauth2", "v2", credentials=creds, cache_discovery=False).userinfo().get().execute()
        google_id = userinfo["id"]
        if not userinfo.get("verified_email"):
            raise ValueError("Google account email is not verified")
    except Exception:
        # Provider exceptions can contain a code or token URL. Do not log them.
        logger.warning("Google sign-in could not be completed")
        return _redirect("/?error=oauth_failed")
    user = db.query(User).filter(User.google_id == google_id).first()
    if not user:
        user = User(google_id=google_id, email=userinfo.get("email", ""))
    user.name = userinfo.get("name", "")
    user.picture = userinfo.get("picture", "")
    user.access_token = encrypt_secret(creds.token or "")
    if creds.refresh_token:
        user.refresh_token = encrypt_secret(creds.refresh_token)
    user.token_expiry = google_oauth.expiry_to_str(creds)
    user.granted_scopes = " ".join(creds.granted_scopes or creds.scopes or [])
    db.add(user)
    db.flush()
    handoff = create_handoff(db, user.id, challenge)
    db.commit()
    # A two-minute, single-use code, bound to the frontend's HttpOnly verifier.
    # No session or Google token is placed in the redirect URL.
    return _redirect(f"/auth/callback?code={handoff}")


class SessionExchange(BaseModel):
    code: str = Field(pattern=r"^[A-Za-z0-9_-]{43}$", max_length=43)
    verifier: str = Field(pattern=r"^[A-Za-z0-9_-]{43}$", max_length=43)


@router.post("/session/exchange")
def exchange_session(payload: SessionExchange, response: Response, db: Session = Depends(get_db)):
    user_id = consume_handoff(db, payload.code, payload.verifier)
    if user_id is None:
        raise HTTPException(401, "Sign-in expired. Start again from AURA.")
    session, expires_at = create_session(db, user_id)
    db.commit()
    response.headers["Cache-Control"] = "no-store"
    return {"session": session, "expires_at": expires_at}


@router.post("/logout")
def logout(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    token = bearer_token(authorization)
    if token:
        db.execute(delete(AuthSession).where(AuthSession.token_hash == token_hash(token)))
        db.commit()
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
