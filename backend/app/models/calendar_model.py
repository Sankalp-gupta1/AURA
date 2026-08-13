from datetime import datetime, timezone

from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    google_event_id: Mapped[str] = mapped_column(String, unique=True, index=True)

    title: Mapped[str] = mapped_column(String, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    location: Mapped[str] = mapped_column(String, default="")
    start_time: Mapped[str] = mapped_column(String, default="")
    end_time: Mapped[str] = mapped_column(String, default="")
    meet_link: Mapped[str] = mapped_column(String, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
