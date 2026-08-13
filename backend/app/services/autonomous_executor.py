"""
Turns a task into a concrete plan (via the task strategist agent) and,
once the user approves a specific proposed action, actually carries it out.

Safety boundary: build_and_store_plan() only ever creates "proposed" rows in
the database - it never touches Gmail, Calendar, or anything external.
execute_action() is the only function that performs a real side effect, and
it only runs when explicitly called after user approval (see
app/api/actions.py). AURA never sends an email on its own; draft_reply
actions only ever produce a draft the user reviews and sends themselves.
"""
import json
import logging
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from app.models.agent_action import AgentAction
from app.models.task_model import Task
from app.models.email_model import Email
from app.models.note_model import Note
from app.agents.task_strategist_agent import build_plan
from app.services import calendar_service

logger = logging.getLogger(__name__)


def _related_context(db: Session, user_id: int, task: Task) -> str:
    """Pull a little surrounding context (recent emails + notes) so the
    strategist agent isn't planning in a vacuum."""
    emails = (
        db.query(Email)
        .filter(Email.user_id == user_id)
        .order_by(Email.created_at.desc())
        .limit(15)
        .all()
    )
    notes = db.query(Note).filter(Note.user_id == user_id).order_by(Note.created_at.desc()).limit(10).all()

    email_text = "\n".join(f"- {e.subject} from {e.sender}: {e.snippet}" for e in emails) or "None"
    note_text = "\n".join(f"- {n.content}" for n in notes) or "None"
    return f"Recent emails:\n{email_text}\n\nNotes:\n{note_text}"


def build_and_store_plan(db: Session, user_id: int, task: Task) -> List[AgentAction]:
    context = _related_context(db, user_id, task)
    now_iso = datetime.now(timezone.utc).isoformat()

    proposed = build_plan(task, context, now_iso)

    rows: List[AgentAction] = []
    for action in proposed:
        row = AgentAction(
            user_id=user_id,
            task_id=task.id,
            action_type=action["action_type"],
            title=action["title"],
            description=action["description"],
            payload_json=json.dumps(action["payload"]),
            status="proposed",
        )
        db.add(row)
        rows.append(row)

    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def execute_action(db: Session, user, action: AgentAction) -> AgentAction:
    if action.status == "executed":
        return action

    payload = json.loads(action.payload_json or "{}")

    try:
        if action.action_type == "create_event":
            created = calendar_service.create_event(
                user,
                title=payload.get("title", action.title),
                start_time=payload["start_time"],
                end_time=payload["end_time"],
                location=payload.get("location", ""),
            )
            action.result_note = f"Created on Google Calendar: {created.get('title')}"

        elif action.action_type == "add_subtask":
            subtask = Task(
                user_id=user.id,
                title=payload.get("title", action.title),
                priority=payload.get("priority", "Medium"),
                source="ai_task_plan",
            )
            db.add(subtask)
            action.result_note = f"Added task: {subtask.title}"

        elif action.action_type == "draft_reply":
            # Intentionally NOT sent - AURA never sends email autonomously.
            # The draft is stored on the action for the user to copy/send themselves.
            action.result_note = "Draft saved. Review and send it yourself from Gmail."

        elif action.action_type == "set_reminder":
            if action.task_id:
                task = db.query(Task).filter(Task.id == action.task_id).first()
                if task and payload.get("remind_at"):
                    task.deadline = payload["remind_at"]
            action.result_note = "Reminder noted on the task."

        else:
            raise ValueError(f"Unknown action_type: {action.action_type}")

        action.status = "executed"
        action.executed_at = datetime.now(timezone.utc).isoformat()

    except Exception as exc:
        logger.exception("Failed to execute action %s", action.id)
        action.status = "failed"
        action.result_note = f"Execution failed: {exc}"

    db.commit()
    db.refresh(action)
    return action
