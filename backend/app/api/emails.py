from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.email_model import Email
from app.models.user import User
from app.schemas.schemas import EmailOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/emails", tags=["emails"])


@router.get("", response_model=List[EmailOut])
def list_emails(
    category: Optional[str] = None,
    important_only: bool = False,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Email).filter(Email.user_id == user.id)
    if category:
        q = q.filter(Email.category == category)
    if important_only:
        q = q.filter(Email.is_important.is_(True))
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Email.subject.ilike(like), Email.sender.ilike(like), Email.snippet.ilike(like)))
    return q.order_by(Email.created_at.desc()).limit(limit).all()


@router.get("/{email_id}", response_model=EmailOut)
def get_email(email_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Email).filter(Email.id == email_id, Email.user_id == user.id).first()
