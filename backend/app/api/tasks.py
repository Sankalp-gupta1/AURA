import json
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.task_model import Task
from app.models.user import User
from app.schemas.schemas import TaskOut, TaskCreate, TaskUpdate, ActionOut
from app.api.deps import get_current_user
from app.services.autonomous_executor import build_and_store_plan

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tasks", tags=["tasks"])

_PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


@router.get("", response_model=List[TaskOut])
def list_tasks(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Task).filter(Task.user_id == user.id)
    if status:
        q = q.filter(Task.status == status)
    tasks = q.all()
    tasks.sort(key=lambda t: (_PRIORITY_ORDER.get(t.priority, 3), t.deadline or "9999"))
    return tasks


@router.post("", response_model=TaskOut)
def create_task(payload: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = Task(user_id=user.id, source="manual", **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    db.delete(task)
    db.commit()
    return {"ok": True}


@router.post("/{task_id}/plan", response_model=List[ActionOut])
def plan_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Ask the task strategist agent for a concrete action plan on this task.
    Returns proposed actions - nothing executes until each is approved via
    POST /api/actions/{id}/approve."""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(404, "Task not found")

    try:
        rows = build_and_store_plan(db, user.id, task)
    except Exception:
        logger.exception("Task planning failed for task %s", task_id)
        raise HTTPException(502, "AURA couldn't generate a plan right now. Try again shortly.")

    return [
        ActionOut(
            id=r.id,
            task_id=r.task_id,
            action_type=r.action_type,
            title=r.title,
            description=r.description,
            payload=json.loads(r.payload_json or "{}"),
            status=r.status,
            result_note=r.result_note,
        )
        for r in rows
    ]
