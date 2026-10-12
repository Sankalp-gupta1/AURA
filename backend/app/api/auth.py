import logging
import secrets
from urllib.parse import quote

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from googleapiclient.discovery import build

from app.core.config import settings
from app.core.security import create_access_token, encrypt_secret
from app.db.database import get_db
from app.models.user import User
from app.services import google_oauth
from app.services.sync_service import sync_user_data
from app.schemas.schemas import UserOut
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

COOKIE_NAME = "aura_session"
OAUTH_STATE_COOKIE = "aura_oauth_state"


def _is_production() -> bool:
    return settings.ENVIRONMENT != "development"


def _clear_oauth_state(response: Response) -> None:
    response.delete_cookie(
        OAUTH_STATE_COOKIE,
        samesite="lax",
        secure=_is_production(),
    )


@router.get("/google/login")
def google_login():
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(500, "Google OAuth is not configured on the server.")

    state = secrets.token_urlsafe(32)
    response = RedirectResponse(google_oauth.build_auth_url(state))
    response.set_cookie(
        key=OAUTH_STATE_COOKIE,
        value=state,
        httponly=True,
        samesite="lax",
        secure=_is_production(),
        max_age=10 * 60,
    )
    return response


@router.get("/google/callback")
def google_callback(
    code: str,
    state: str = "",
    aura_oauth_state: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    frontend = settings.FRONTEND_URL.rstrip("/")

    if not state or not aura_oauth_state or not secrets.compare_digest(state, aura_oauth_state):
        response = RedirectResponse(f"{frontend}/?error=oauth_state")
        _clear_oauth_state(response)
        return response

    try:
        creds = google_oauth.exchange_code(code)
    except Exception:
        logger.exception("OAuth code exchange failed")
        response = RedirectResponse(f"{frontend}/?error=oauth_failed")
        _clear_oauth_state(response)
        return response

    userinfo = build("oauth2", "v2", credentials=creds, cache_discovery=False).userinfo().get().execute()
    google_id = userinfo["id"]

    user = db.query(User).filter(User.google_id == google_id).first()
    if not user:
        user = User(google_id=google_id, email=userinfo.get("email", ""))

    user.name = userinfo.get("name", "")
    user.picture = userinfo.get("picture", "")
    user.access_token = encrypt_secret(creds.token or "")
    if creds.refresh_token:
        user.refresh_token = encrypt_secret(creds.refresh_token)
    user.token_expiry = google_oauth.expiry_to_str(creds)
    user.granted_scopes = " ".join(creds.scopes or [])

    db.add(user)
    db.commit()
    db.refresh(user)

    try:
        sync_user_data(db, user)
    except Exception:
        logger.exception("Initial sync after login failed for user %s", user.id)

    token = create_access_token(user.id)

    if settings.ENVIRONMENT == "development":
        response = RedirectResponse(f"{frontend}/dashboard")
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=60 * 60 * 24 * 7,
        )
        _clear_oauth_state(response)
        return response

    response = RedirectResponse(f"{frontend}/auth/callback#token={quote(token)}")
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="none",
        secure=True,
        max_age=60 * 60 * 24 * 7,
    )
    _clear_oauth_state(response)
    return response


@router.post("/logout")
def logout(response: Response):
    production = settings.ENVIRONMENT != "development"
    response.delete_cookie(
        COOKIE_NAME,
        samesite="none" if production else "lax",
        secure=production,
    )
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
