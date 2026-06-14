from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.emails import router as emails_router
from app.api.tasks import router as tasks_router
from app.api.dashboard import router as dashboard_router
from app.api.calendar import router as calendar_router
from app.api.ask import router as ask_router

from app.db.database import engine, Base
from app.models.email_model import Email
from app.models.task_model import Task
from app.models.calendar_model import CalendarEvent

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Life OS AI",
    description="Autonomous Personal Life Operating System using Agentic AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(emails_router, prefix="/api/emails")
app.include_router(tasks_router, prefix="/api/tasks")
app.include_router(dashboard_router, prefix="/api/dashboard")
app.include_router(calendar_router, prefix="/api/calendar")
app.include_router(ask_router, prefix="/api/ask")
