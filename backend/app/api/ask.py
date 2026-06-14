from fastapi import APIRouter
from pydantic import BaseModel
from app.db.database import SessionLocal
from app.models.email_model import Email
from app.models.task_model import Task
from app.models.calendar_model import CalendarEvent
from app.services.ai_service import ask_aura

router = APIRouter()


class AskRequest(BaseModel):
    question: str


@router.post("/")
def ask_life_os(req: AskRequest):
    db = SessionLocal()

    emails = db.query(Email).order_by(Email.id.desc()).limit(50).all()
    tasks = db.query(Task).order_by(Task.id.desc()).limit(20).all()
    events = db.query(CalendarEvent).order_by(CalendarEvent.start_time.asc()).limit(20).all()

    answer = ask_aura(
        question=req.question,
        emails=emails,
        tasks=tasks,
        events=events
    )

    db.close()

    return {
        "assistant": "Aura",
        "question": req.question,
        "answer": answer
    }
