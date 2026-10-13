import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.email_model import Email
from app.models.calendar_model import Event
from app.models.task_model import Task
from app.models.user import User
from app.services import gmail_service, calendar_service, ai_service

logger = logging.getLogger(__name__)


def sync_user_data(db: Session, user: User) -> dict:
    """Full sync: pull Gmail + Calendar, run AI analysis, persist everything.
    Returns a small summary dict for the API response / logs.
    """
    new_emails_count = 0
    new_events_count = 0
    new_tasks_count = 0
    warnings = []
    gmail_ok = True
    calendar_ok = True

    # ---- Gmail ----
    try:
        raw_emails = gmail_service.fetch_recent_emails(user)
    except Exception:
        logger.exception("Gmail sync failed for user %s", user.id)
        raw_emails = []
        gmail_ok = False
        warnings.append("Gmail could not sync. Reconnect Google and check that Gmail access is allowed.")

    existing_ids = {row[0] for row in db.query(Email.gmail_id).filter(Email.user_id == user.id).all()}
    fresh_emails = [e for e in raw_emails if e["gmail_id"] not in existing_ids]

    analysis = {"emails": [], "tasks": []}
    if fresh_emails:
        try:
            analysis = ai_service.analyze_and_extract(fresh_emails)
            if not isinstance(analysis, dict) or not isinstance(analysis.get("emails", []), list) or not isinstance(analysis.get("tasks", []), list):
                raise ValueError("Unexpected AI analysis format")
        except Exception:
            logger.exception("AI analysis failed during sync for user %s", user.id)
            analysis = {"emails": [], "tasks": []}
            warnings.append("Your emails were saved, but AI summaries are unavailable right now.")

    analysis_by_id = {a.get("gmail_id"): a for a in analysis.get("emails", []) if isinstance(a, dict)}

    for e in fresh_emails:
        meta = analysis_by_id.get(e["gmail_id"], {})
        row = Email(
            user_id=user.id,
            gmail_id=e["gmail_id"],
            thread_id=e.get("thread_id", ""),
            sender=e["sender"],
            subject=e["subject"],
            snippet=e["snippet"],
            body=e.get("body", ""),
            email_date=e["email_date"],
            category=meta.get("category", "general"),
            priority=meta.get("priority", "Low"),
            is_important=bool(meta.get("is_important", False)),
            ai_summary=meta.get("summary", ""),
        )
        db.add(row)
        new_emails_count += 1

    db.flush()  # get IDs assigned before mapping tasks to emails

    gmail_id_to_row_id = {
        row.gmail_id: row.id
        for row in db.query(Email).filter(Email.user_id == user.id, Email.gmail_id.in_([e["gmail_id"] for e in fresh_emails])).all()
    } if fresh_emails else {}

    for t in analysis.get("tasks", []):
        if not isinstance(t, dict):
            continue
        db.add(
            Task(
                user_id=user.id,
                title=t.get("title", "Untitled task"),
                description=t.get("description", ""),
                priority=t.get("priority", "Medium"),
                deadline=t.get("deadline") or "",
                source="ai_email",
                source_email_id=gmail_id_to_row_id.get(t.get("source_gmail_id")),
            )
        )
        new_tasks_count += 1

    # ---- Calendar ----
    try:
        raw_events = calendar_service.fetch_upcoming_events(user)
    except Exception:
        logger.exception("Calendar sync failed for user %s", user.id)
        raw_events = []
        calendar_ok = False
        warnings.append("Calendar could not sync. Reconnect Google and check that Calendar access is allowed.")

    existing_events = {row.google_event_id: row for row in db.query(Event).filter(Event.user_id == user.id).all()}
    for ev in raw_events:
        if ev["google_event_id"] in existing_events:
            row = existing_events[ev["google_event_id"]]
            for field in ("title", "description", "location", "start_time", "end_time", "meet_link"):
                setattr(row, field, ev.get(field, ""))
            continue
        db.add(
            Event(
                user_id=user.id,
                google_event_id=ev["google_event_id"],
                title=ev["title"],
                description=ev.get("description", ""),
                location=ev.get("location", ""),
                start_time=ev["start_time"],
                end_time=ev["end_time"],
                meet_link=ev.get("meet_link", ""),
            )
        )
        new_events_count += 1

    # A failed connection must not appear as a successful sync in the UI.
    if gmail_ok and calendar_ok:
        user.last_synced_at = datetime.now(timezone.utc).isoformat()
    db.add(user)
    db.commit()

    return {
        "new_emails": new_emails_count,
        "new_events": new_events_count,
        "new_tasks": new_tasks_count,
        "synced_at": user.last_synced_at,
        "status": "ok" if not warnings else ("partial" if gmail_ok or calendar_ok else "failed"),
        "warnings": warnings,
    }
