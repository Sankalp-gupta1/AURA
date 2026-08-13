import json
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.email_model import Email
from app.models.task_model import Task
from app.models.calendar_model import Event
from app.models.note_model import Note
from app.models.chat_model import ChatMessage
from app.models.user import User
from app.schemas.schemas import AskRequest
from app.api.deps import get_current_user
from app.agents import orchestrator
from app.services import memory_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/ask",
    tags=["ask"]
)


@router.post("")
def ask_aura(
    payload: AskRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # --------------------------------------------------
    # IMPORTANT:
    # Save user ID before streaming starts.
    # We should NOT use user.id inside event_stream().
    # --------------------------------------------------

    user_id = user.id

    # --------------------------------------------------
    # GET DATA FROM DATABASE
    # --------------------------------------------------

    email_rows = (
        db.query(Email)
        .filter(Email.user_id == user_id)
        .order_by(Email.created_at.desc())
        .limit(50)
        .all()
    )

    task_rows = (
        db.query(Task)
        .filter(Task.user_id == user_id)
        .all()
    )

    event_rows = (
        db.query(Event)
        .filter(Event.user_id == user_id)
        .all()
    )

    note_rows = (
        db.query(Note)
        .filter(Note.user_id == user_id)
        .all()
    )

    # --------------------------------------------------
    # LONG-TERM MEMORY - durable facts learned across past sessions
    # --------------------------------------------------

    memories = memory_service.get_relevant_memories(db, user_id)

    # --------------------------------------------------
    # CONVERT SQLAlchemy OBJECTS
    # TO NORMAL PYTHON DICTS
    # --------------------------------------------------

    emails = [
        {
            "sender": e.sender,
            "subject": e.subject,
            "email_date": e.email_date,
            "snippet": e.snippet,
        }
        for e in email_rows
    ]

    tasks = [
        {
            "title": t.title,
            "priority": t.priority,
            "status": t.status,
            "deadline": t.deadline,
        }
        for t in task_rows
    ]

    events = [
        {
            "title": ev.title,
            "start_time": ev.start_time,
            "location": ev.location,
        }
        for ev in event_rows
    ]

    notes = [
        {
            "content": n.content,
        }
        for n in note_rows
    ]

    # --------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------

    history_rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(8)
        .all()
    )

    history = [
        {
            "role": h.role,
            "content": h.content,
        }
        for h in reversed(history_rows)
    ]

    # --------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------

    db.add(
        ChatMessage(
            user_id=user_id,
            role="user",
            content=payload.question,
        )
    )

    db.commit()

    # --------------------------------------------------
    # STREAM AI RESPONSE (via the multi-agent orchestrator)
    # --------------------------------------------------

    def event_stream():

        full_answer = []

        try:

            for chunk in orchestrator.ask_aura_stream(
                payload.question,
                emails,
                tasks,
                events,
                notes,
                history,
                memories,
            ):
                full_answer.append(chunk)

                yield (
                    f"data: "
                    f"{json.dumps({'delta': chunk})}"
                    f"\n\n"
                )

            # --------------------------------------------------
            # COMPLETE AI RESPONSE
            # --------------------------------------------------

            answer_text = "".join(full_answer)

            # IMPORTANT:
            # Use user_id, NOT user.id
            #
            # user.id can cause DetachedInstanceError
            # because streaming happens after the request
            # session lifecycle has changed.
            # --------------------------------------------------

            db.add(
                ChatMessage(
                    user_id=user_id,
                    role="assistant",
                    content=answer_text,
                )
            )

            db.commit()

            # --------------------------------------------------
            # LONG-TERM MEMORY - decide if anything from this
            # exchange is worth remembering for future sessions.
            # Runs after the answer is already sent so it never
            # delays the response the user is waiting on.
            # --------------------------------------------------

            try:
                new_memories = orchestrator.remember_from_exchange(payload.question, answer_text)
                if new_memories:
                    memory_service.store_memories(db, user_id, new_memories, source="chat")
            except Exception:
                logger.exception("Memory storage failed after chat exchange")

            yield (
                f"data: "
                f"{json.dumps({'done': True})}"
                f"\n\n"
            )

        except Exception as exc:

            # If something goes wrong while streaming,
            # rollback any unfinished DB transaction.

            db.rollback()

            # Send error to frontend instead of crashing
            # the whole streaming response.

            yield (
                f"data: "
                f"{json.dumps({'error': str(exc)})}"
                f"\n\n"
            )

    # --------------------------------------------------
    # RETURN STREAMING RESPONSE
    # --------------------------------------------------

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )
