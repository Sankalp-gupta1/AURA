from datetime import datetime, timezone

from sqlalchemy import String, Text, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Memory(Base):
    """
    A durable fact AURA has learned about the user - separate from raw chat
    history. Chat history is a transcript; Memory is the distilled, long-term
    knowledge AURA carries forward into every future conversation and
    briefing (goals, preferences, ongoing situations), the same way a real
    chief of staff would remember things about you across weeks, not just
    within one conversation.
    """

    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    content: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String, default="fact")  # fact, preference, goal, ongoing_situation
    importance: Mapped[int] = mapped_column(Integer, default=3)  # 1 (minor) - 5 (critical, always include)
    source: Mapped[str] = mapped_column(String, default="chat")  # chat, email, manual

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_referenced_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
