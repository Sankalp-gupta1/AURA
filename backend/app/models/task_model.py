from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    priority = Column(String)
    deadline = Column(String)
    source = Column(String, default="gmail")
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
