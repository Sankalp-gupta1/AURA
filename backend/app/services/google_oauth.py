"""
Handles the Google OAuth2 dance for Gmail + Calendar access.
No client secret JSON file needed - everything comes from env vars,
which makes deployment (and giving Claude your key) much simpler than
the original repo's token.json file dependency.
"""
import logging
from datetime import datetime, timedelta, timezone

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest

from app.core.config import settings

logger = logging.getLogger(__name__)

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
]


def _client_config() -> dict:
    return {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        }
    }


def build_auth_url() -> str:
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES, redirect_uri=settings.GOOGLE_REDIRECT_URI)
    auth_url, _state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",  # ensures a refresh_token is issued every time
    )
    return auth_url


def exchange_code(code: str) -> Credentials:
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES, redirect_uri=settings.GOOGLE_REDIRECT_URI)
    flow.fetch_token(code=code)
    return flow.credentials


def credentials_from_user(user) -> Credentials:
    """Rebuild a Credentials object from what we stored on the user row, refreshing if needed."""
    creds = Credentials(
        token=user.access_token,
        refresh_token=user.refresh_token,
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
