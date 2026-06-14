from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    gmail_id = Column(String, unique=True, index=True)
    sender = Column(String)
    subject = Column(String)
    snippet = Column(Text)
    email_date = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
