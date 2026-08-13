from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.note_model import Note
from app.models.user import User
from app.schemas.schemas import NoteOut, NoteCreate
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.get("", response_model=List[NoteOut])
def list_notes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Note).filter(Note.user_id == user.id).order_by(Note.created_at.desc()).all()


@router.post("", response_model=NoteOut)
def create_note(payload: NoteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = Note(user_id=user.id, content=payload.content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note:
        raise HTTPException(404, "Note not found")
    db.delete(note)
    db.commit()
    return {"ok": True}
