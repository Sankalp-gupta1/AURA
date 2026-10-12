import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.database import init_db
from app.tasks.scheduler import start_scheduler, stop_scheduler

from app.api import auth, emails, tasks, calendar, dashboard, ask, notes, health, memory, actions

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("%s backend starting up (env=%s)", settings.APP_NAME, settings.ENVIRONMENT)
    start_scheduler()
    yield
    stop_scheduler()
    logger.info("%s backend shutting down", settings.APP_NAME)


app = FastAPI(title=settings.APP_NAME, version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error. Check server logs."})


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(emails.router)
app.include_router(tasks.router)
app.include_router(calendar.router)
app.include_router(dashboard.router)
app.include_router(ask.router)
app.include_router(notes.router)
app.include_router(memory.router)
app.include_router(actions.router)


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} backend is running. See /docs for the API."}
