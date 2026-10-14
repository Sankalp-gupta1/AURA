import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.email_model import Email
from app.models.task_model import Task
from app.models.calendar_model import Event
from app.models.user import User
from app.schemas.schemas import DashboardStats, BriefingOut
from app.api.deps import get_current_user
from app.services import ai_service, memory_service
from app.services.sync_service import sync_user_data

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Simple in-memory briefing cache per user so we don't burn tokens on every dashboard refresh.
_briefing_cache: dict[int, BriefingOut] = {}


@router.post("/sync")
def trigger_sync(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    summary = sync_user_data(db, user)
    _briefing_cache.pop(user.id, None)  # invalidate cached briefing after new data
    return summary


@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    emails = db.query(Email).filter(Email.user_id == user.id).count()
    important = db.query(Email).filter(Email.user_id == user.id, Email.is_important.is_(True)).count()
    pending_tasks = db.query(Task).filter(Task.user_id == user.id, Task.status != "done").count()
    upcoming_events = db.query(Event).filter(Event.user_id == user.id).count()
    return DashboardStats(
        emails=emails, tasks_pending=pending_tasks, events_upcoming=upcoming_events, important_emails=important
    )


@router.get("/briefing", response_model=BriefingOut)
def briefing(force: bool = False, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not force and user.id in _briefing_cache:
        return _briefing_cache[user.id]

    tasks = db.query(Task).filter(Task.user_id == user.id, Task.status != "done").all()
    emails = db.query(Email).filter(Email.user_id == user.id).order_by(Email.created_at.desc()).limit(30).all()
    events = db.query(Event).filter(Event.user_id == user.id).order_by(Event.start_time.asc()).limit(10).all()
    memories = memory_service.get_relevant_memories(db, user.id)

    generated = False
    try:
        data = ai_service.generate_briefing(tasks, emails, events, memories=memories)
        generated = True
    except Exception:
        logger.warning("Briefing generation could not be completed for user %s", user.id)
        data = {
            "daily_briefing": "Could not reach the AI provider right now. Please try again shortly.",
            "top_focus": [],
            "risks": [],
            "suggested_actions": [],
            "motivational_note": "",
        }

    result = BriefingOut(
        daily_briefing=data.get("daily_briefing", ""),
        top_focus=data.get("top_focus", []),
        risks=data.get("risks", []),
        suggested_actions=data.get("suggested_actions", []),
        motivational_note=data.get("motivational_note", ""),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    if generated:
        _briefing_cache[user.id] = result
    return result
