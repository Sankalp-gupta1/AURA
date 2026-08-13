"""
Gmail integration. Fetches recent messages and normalizes them into
plain dicts the rest of the app can work with (AI service, DB, API).
"""
import base64
import logging
from typing import List, Dict

from googleapiclient.discovery import build

from app.core.config import settings
from app.services.google_oauth import credentials_from_user

logger = logging.getLogger(__name__)


def _decode_body(payload: dict) -> str:
    """Walk the MIME parts and pull out the best-effort plain text body."""
    if not payload:
        return ""

    def _extract(part) -> str:
        body_data = part.get("body", {}).get("data")
        if body_data:
            try:
                return base64.urlsafe_b64decode(body_data.encode("utf-8")).decode("utf-8", errors="ignore")
            except Exception:
                return ""
        return ""

    mime_type = payload.get("mimeType", "")
    if mime_type == "text/plain":
        return _extract(payload)

    for part in payload.get("parts", []) or []:
        if part.get("mimeType") == "text/plain":
            text = _extract(part)
            if text:
                return text
    # fallback: first part with any data
    for part in payload.get("parts", []) or []:
        text = _extract(part)
        if text:
            return text
    return _extract(payload)


def _header(headers: List[dict], name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def fetch_recent_emails(user, max_results: int = None) -> List[Dict]:
    """Fetch the most recent inbox messages for the given user."""
    max_results = max_results or settings.MAX_EMAILS_PER_SYNC
    creds = credentials_from_user(user)
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    results = (
        service.users()
        .messages()
        .list(userId="me", maxResults=max_results, labelIds=["INBOX"])
        .execute()
    )
    message_refs = results.get("messages", [])

    emails: List[Dict] = []
    for ref in message_refs:
        try:
            msg = service.users().messages().get(userId="me", id=ref["id"], format="full").execute()
        except Exception:
            logger.exception("Failed to fetch gmail message %s", ref.get("id"))
            continue

        headers = msg.get("payload", {}).get("headers", [])
        body_text = _decode_body(msg.get("payload", {}))

        emails.append(
            {
                "gmail_id": msg.get("id", ""),
                "thread_id": msg.get("threadId", ""),
                "sender": _header(headers, "From"),
                "subject": _header(headers, "Subject") or "(no subject)",
                "snippet": msg.get("snippet", ""),
                "body": body_text[:6000],  # cap body size before it hits the LLM
                "email_date": _header(headers, "Date"),
            }
        )
    return emails
