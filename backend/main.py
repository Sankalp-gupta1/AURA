from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.emails import router as emails_router

from app.db.database import engine, Base
from app.models.email_model import Email
from app.models.task_model import Task
from app.models.calendar_model import CalendarEvent

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Life OS AI",
    description="Autonomous Personal Life Operating System using Agentic AI",
    version="1.0.0"
)

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(emails_router, prefix="/api/emails")
