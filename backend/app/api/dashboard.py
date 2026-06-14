from fastapi import APIRouter
from app.db.database import SessionLocal
from app.models.email_model import Email
from app.models.task_model import Task
from app.models.calendar_model import CalendarEvent
from app.services.ai_service import generate_dashboard_ai_summary

router = APIRouter()


def task_to_dict(t):
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "priority": t.priority,
        "deadline": t.deadline,
        "status": t.status,
    }


def email_to_dict(e):
    return {
        "id": e.id,
        "from": e.sender,
        "subject": e.subject,
        "snippet": e.snippet,
        "date": e.email_date,
    }


def event_to_dict(ev):
    return {
        "id": ev.id,
        "title": ev.title,
        "start": ev.start_time,
        "end": ev.end_time,
        "location": ev.location,
        "description": ev.description,
    }


@router.get("/")
def get_dashboard():
    db = SessionLocal()

    total_emails = db.query(Email).count()
    total_tasks = db.query(Task).count()
    total_events = db.query(CalendarEvent).count()

    pending_tasks = db.query(Task).filter(
        Task.status == "pending"
    ).all()

    high_priority_tasks = db.query(Task).filter(
        Task.priority == "High",
        Task.status == "pending"
    ).all()

    latest_emails = db.query(Email).order_by(
        Email.id.desc()
    ).limit(5).all()

    upcoming_events = db.query(CalendarEvent).filter(
        CalendarEvent.title != "Happy birthday!"
    ).order_by(
        CalendarEvent.start_time.asc()
    ).limit(5).all()

    pending_result = [task_to_dict(t) for t in pending_tasks]
    high_result = [task_to_dict(t) for t in high_priority_tasks]
    email_result = [email_to_dict(e) for e in latest_emails]
    event_result = [event_to_dict(ev) for ev in upcoming_events]

    today_focus = []

    if high_result:
        today_focus.append({
            "type": "task",
            "title": high_result[0]["title"],
            "reason": "High priority pending task"
        })

    elif pending_result:
        today_focus.append({
            "type": "task",
            "title": pending_result[0]["title"],
            "reason": "Pending task needing attention"
        })

    if event_result:
        today_focus.append({
            "type": "calendar",
            "title": event_result[0]["title"],
            "reason": "Upcoming calendar event"
        })

    db.close()

    return {
        "message": "Life OS dashboard generated",
        "stats": {
            "total_emails": total_emails,
            "total_tasks": total_tasks,
            "total_events": total_events,
            "pending_tasks": len(pending_result),
            "high_priority_tasks": len(high_result),
        },
        "today_focus": today_focus,
        "high_priority_tasks": high_result,
        "pending_tasks": pending_result,
        "latest_emails": email_result,
        "upcoming_events": event_result,
        "suggested_actions": [
            "Review high priority tasks first",
            "Check important job or assessment emails",
            "Update task status after completion"
        ]
    }


@router.get("/ai")
def get_ai_dashboard_summary():
    db = SessionLocal()

    tasks = db.query(Task).filter(
        Task.status == "pending"
    ).limit(10).all()

    emails = db.query(Email).order_by(
        Email.id.desc()
    ).limit(30).all()

    events = db.query(CalendarEvent).filter(
        CalendarEvent.title != "Happy birthday!"
    ).order_by(
        CalendarEvent.start_time.asc()
    ).limit(10).all()

    ai_summary = generate_dashboard_ai_summary(
        tasks=tasks,
        emails=emails,
        events=events
    )

    db.close()

    return {
        "message": "AI Chief of Staff briefing generated",
        "briefing": ai_summary
    }
