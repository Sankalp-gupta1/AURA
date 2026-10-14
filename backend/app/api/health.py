import os

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "ai_configured": bool(settings.GEMINI_API_KEY),
        # Public deployment metadata, never keys or provider response bodies.
        "ai_model": settings.GEMINI_MODEL,
        "release": os.environ.get("RENDER_GIT_COMMIT", "local")[:12],
        "google_oauth_configured": bool(
            settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET
        ),
    }
