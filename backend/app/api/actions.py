import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.agent_action import AgentAction
from app.schemas.schemas import ActionOut
from app.api.deps import get_current_user
from app.services.autonomous_executor import execute_action

router = APIRouter(prefix="/api/actions", tags=["actions"])


def _to_out(row: AgentAction) -> ActionOut:
    return ActionOut(
        id=row.id,
        task_id=row.task_id,
        action_type=row.action_type,
        title=row.title,
        description=row.description,
        payload=json.loads(row.payload_json or "{}"),
        status=row.status,
        result_note=row.result_note,
    )


@router.get("", response_model=List[ActionOut])
def list_actions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(AgentAction).filter(AgentAction.user_id == user.id).order_by(AgentAction.created_at.desc()).all()
    return [_to_out(r) for r in rows]


@router.post("/{action_id}/approve", response_model=ActionOut)
def approve_action(action_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(AgentAction).filter(AgentAction.id == action_id, AgentAction.user_id == user.id).first()
    if not row:
        raise HTTPException(404, "Action not found")
    row.status = "approved"
    db.commit()
    row = execute_action(db, user, row)
    return _to_out(row)


@router.post("/{action_id}/reject", response_model=ActionOut)
def reject_action(action_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.query(AgentAction).filter(AgentAction.id == action_id, AgentAction.user_id == user.id).first()
    if not row:
        raise HTTPException(404, "Action not found")
    row.status = "rejected"
    db.commit()
    db.refresh(row)
    return _to_out(row)
