from datetime import datetime, timezone

from sqlalchemy import String, Text, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AgentAction(Base):
    """
    A concrete action an AURA agent has proposed for a task (e.g. draft a
    reply, create a calendar reminder, add a sub-task). Nothing in here
    ever executes automatically - a human always has to approve it first.
    That approval boundary is what makes this "autonomous but safe" rather
    than an agent quietly sending emails or booking meetings on its own.
    """

    __tablename__ = "agent_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=True, index=True)

    action_type: Mapped[str] = mapped_column(String)  # create_event, draft_reply, add_subtask, set_reminder
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text, default="")
    payload_json: Mapped[str] = mapped_column(Text, default="{}")  # action-specific structured data

    status: Mapped[str] = mapped_column(String, default="proposed")  # proposed, approved, rejected, executed, failed
    result_note: Mapped[str] = mapped_column(Text, default="")  # what happened when executed (or why it failed)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    executed_at: Mapped[str] = mapped_column(String, default="")
