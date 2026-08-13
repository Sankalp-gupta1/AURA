import logging
from datetime import datetime, timezone
from typing import List, Dict

from sqlalchemy.orm import Session

from app.models.memory_model import Memory

logger = logging.getLogger(__name__)

MAX_MEMORIES_PER_USER = 200  # prevent unbounded growth from ever slowing down context building


def get_relevant_memories(db: Session, user_id: int, limit: int = 15) -> List[Dict]:
    """Highest-importance, most-recently-referenced memories first - these get
    injected into every briefing and chat prompt as long-term context."""
    rows = (
        db.query(Memory)
        .filter(Memory.user_id == user_id)
        .order_by(Memory.importance.desc(), Memory.last_referenced_at.desc())
        .limit(limit)
        .all()
    )
    return [{"id": m.id, "content": m.content, "category": m.category, "importance": m.importance} for m in rows]


def _is_duplicate(db: Session, user_id: int, content: str) -> bool:
    content_lower = content.strip().lower()
    existing = db.query(Memory.content).filter(Memory.user_id == user_id).all()
    return any(content_lower == e[0].strip().lower() for e in existing)


def store_memories(db: Session, user_id: int, memories: List[Dict], source: str = "chat") -> int:
    stored = 0
    for m in memories:
        content = m.get("content", "").strip()
        if not content or _is_duplicate(db, user_id, content):
            continue
        db.add(
            Memory(
                user_id=user_id,
                content=content,
                category=m.get("category", "fact"),
                importance=m.get("importance", 3),
                source=source,
            )
        )
        stored += 1

    if stored:
        db.commit()
        _enforce_cap(db, user_id)
    return stored


def _enforce_cap(db: Session, user_id: int) -> None:
    count = db.query(Memory).filter(Memory.user_id == user_id).count()
    if count <= MAX_MEMORIES_PER_USER:
        return
    # Drop the lowest-importance, least-recently-referenced memories first.
    overflow = count - MAX_MEMORIES_PER_USER
    stale = (
        db.query(Memory)
        .filter(Memory.user_id == user_id)
        .order_by(Memory.importance.asc(), Memory.last_referenced_at.asc())
        .limit(overflow)
        .all()
    )
    for m in stale:
        db.delete(m)
    db.commit()


def delete_memory(db: Session, user_id: int, memory_id: int) -> bool:
    row = db.query(Memory).filter(Memory.id == memory_id, Memory.user_id == user_id).first()
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


def add_manual_memory(db: Session, user_id: int, content: str, category: str = "fact") -> Memory:
    row = Memory(user_id=user_id, content=content.strip(), category=category, importance=4, source="manual")
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
