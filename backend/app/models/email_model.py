from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Email(Base):
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    gmail_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    thread_id: Mapped[str] = mapped_column(String, default="")

    sender: Mapped[str] = mapped_column(String, default="")
    subject: Mapped[str] = mapped_column(String, default="")
    snippet: Mapped[str] = mapped_column(Text, default="")
    body: Mapped[str] = mapped_column(Text, default="")
    email_date: Mapped[str] = mapped_column(String, default="")

    category: Mapped[str] = mapped_column(String, default="general")  # security, job, deadline, personal, spam...
    priority: Mapped[str] = mapped_column(String, default="Low")
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_summary: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
