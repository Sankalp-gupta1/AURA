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

    # ---- Gmail ----
    try:
        raw_emails = gmail_service.fetch_recent_emails(user)
    except Exception:
        logger.exception("Gmail sync failed for user %s", user.id)
        raw_emails = []

    existing_ids = {row[0] for row in db.query(Email.gmail_id).filter(Email.user_id == user.id).all()}
    fresh_emails = [e for e in raw_emails if e["gmail_id"] not in existing_ids]

    analysis = {"emails": [], "tasks": []}
    if fresh_emails:
        try:
            analysis = ai_service.analyze_and_extract(fresh_emails)
        except Exception:
            logger.exception("AI analysis failed during sync for user %s", user.id)

    analysis_by_id = {a.get("gmail_id"): a for a in analysis.get("emails", [])}

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

    existing_event_ids = {row[0] for row in db.query(Event.google_event_id).filter(Event.user_id == user.id).all()}
    for ev in raw_events:
        if ev["google_event_id"] in existing_event_ids:
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

    user.last_synced_at = datetime.now(timezone.utc).isoformat()
    db.add(user)
    db.commit()

    return {
        "new_emails": new_emails_count,
        "new_events": new_events_count,
        "new_tasks": new_tasks_count,
        "synced_at": user.last_synced_at,
    }
