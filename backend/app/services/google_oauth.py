"""Google OAuth2 helpers for Gmail + Calendar access."""
import logging
from datetime import datetime, timedelta, timezone

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest

from app.core.config import settings, normalize_origin
from app.core.security import decrypt_secret

logger = logging.getLogger(__name__)

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
]


def _redirect_uri() -> str:
    configured = settings.GOOGLE_REDIRECT_URI.strip()

    if settings.ENVIRONMENT == "development":
        return configured or "http://localhost:8000/api/auth/google/callback"

    if configured and "localhost" not in configured:
        return normalize_origin(configured)

    if settings.backend_origin:
        return f"{settings.backend_origin}/api/auth/google/callback"

    return "http://localhost:8000/api/auth/google/callback"


def _client_config() -> dict:
    redirect_uri = _redirect_uri()
    return {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }


def build_auth_url(state: str | None = None) -> str:
    redirect_uri = _redirect_uri()
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES, redirect_uri=redirect_uri)
    auth_url, _state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,
    )
    return auth_url


def exchange_code(code: str) -> Credentials:
    redirect_uri = _redirect_uri()
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES, redirect_uri=redirect_uri)
    flow.fetch_token(code=code)
    return flow.credentials


def credentials_from_user(user) -> Credentials:
    """Rebuild Google credentials from encrypted DB values and refresh if needed."""
    creds = Credentials(
        token=decrypt_secret(user.access_token),
        refresh_token=decrypt_secret(user.refresh_token),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(GoogleRequest())
            except Exception:
                logger.exception("Failed to refresh Google token for user %s", user.id)
                raise
    return creds


def expiry_to_str(creds: Credentials) -> str:
    if creds.expiry:
        return creds.expiry.replace(tzinfo=timezone.utc).isoformat()
    return (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
