from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.memory_model import Memory
from app.schemas.schemas import MemoryOut, MemoryCreate
from app.api.deps import get_current_user
from app.services import memory_service

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.get("", response_model=List[MemoryOut])
def list_memories(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(Memory)
        .filter(Memory.user_id == user.id)
        .order_by(Memory.importance.desc(), Memory.created_at.desc())
        .all()
    )


@router.post("", response_model=MemoryOut)
def add_memory(payload: MemoryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return memory_service.add_manual_memory(db, user.id, payload.content, payload.category)


@router.delete("/{memory_id}")
def forget_memory(memory_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ok = memory_service.delete_memory(db, user.id, memory_id)
    if not ok:
        raise HTTPException(404, "Memory not found")
    return {"ok": True}
