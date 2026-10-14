import logging
from contextlib import asynccontextmanager
from pathlib import Path
from html import escape

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

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

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


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


@app.get("/googlee9dc7450537262e6.html", include_in_schema=False)
def google_site_verification():
    # Keep this file available after verification so Search Console ownership
    # remains valid. Only this exact public file is exposed.
    return FileResponse(
        Path(__file__).parent / "static" / "googlee9dc7450537262e6.html",
        media_type="text/html",
    )


@app.get("/")
def root(request: Request):
    if "text/html" in request.headers.get("accept", ""):
        frontend = escape(settings.frontend_origin, quote=True)
        return HTMLResponse(f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AURA — Application API</title>
<style>body{{font:18px/1.7 system-ui,sans-serif;background:#101820;color:#ecf0f3;margin:0;padding:40px 24px}}main{{max-width:700px;margin:8vh auto}}a{{color:#f7c46d}}h1{{line-height:1.2}}small{{color:#b5c1cb}}</style>
</head><body><main><small>AURA · PERSONAL PRODUCTIVITY</small>
<h1>This is AURA's application API.</h1>
<p>AURA is an independent app that brings your Gmail, calendar and tasks into one workspace. It is not a Google product.</p>
<p>Use the AURA website to get started. Google sign-in takes place on Google's own website; AURA does not collect your Google password.</p>
<p>Gmail access is read-only. Calendar changes require your action or approval. Google account access is currently limited to approved test users.</p>
<p><a href="{frontend}/">Open the AURA website</a> · <a href="{frontend}/privacy">Privacy policy</a></p>
</main></body></html>""", headers={"Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"})
    return {"message": f"{settings.APP_NAME} backend is running. See /docs for the API."}
