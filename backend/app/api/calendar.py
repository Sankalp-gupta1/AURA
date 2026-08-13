from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.calendar_model import Event
from app.models.user import User
from app.schemas.schemas import EventOut, EventCreate
from app.api.deps import get_current_user
from app.services import calendar_service

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("", response_model=List[EventOut])
def list_events(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Event).filter(Event.user_id == user.id).order_by(Event.start_time.asc()).all()


@router.post("", response_model=EventOut)
def create_event(payload: EventCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        created = calendar_service.create_event(
            user, payload.title, payload.start_time, payload.end_time, payload.description, payload.location
        )
    except Exception as exc:
        raise HTTPException(502, f"Could not create event on Google Calendar: {exc}")

    row = Event(user_id=user.id, **created)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
