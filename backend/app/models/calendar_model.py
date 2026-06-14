from sqlalchemy import Column, Integer, String

from app.db.database import Base


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True)
    title = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    location = Column(String)
    description = Column(String)
