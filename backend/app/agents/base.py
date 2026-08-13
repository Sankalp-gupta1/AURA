"""
Shared helpers every specialist agent uses to talk to the LLM. Keeping this
separate from ai_service.py's high-level functions means agents don't need
to know about Gemini specifically - if the provider ever changes again,
only this file (and ai_service.py) need to change.
"""
import json
import logging

from app.services.ai_service import get_client
from app.core.config import settings

logger = logging.getLogger(__name__)


def safe_json_loads(text: str, fallback: dict) -> dict:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Agent returned non-JSON payload, using fallback. Raw: %.200s", text)
        return fallback


def generate_text(prompt: str, temperature: float = 0.3) -> str:
    response = get_client().models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config={"temperature": temperature},
    )
    return response.text or ""


def generate_json(prompt: str, fallback: dict, temperature: float = 0.2) -> dict:
    response = get_client().models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config={"temperature": temperature, "response_mime_type": "application/json"},
    )
    return safe_json_loads(response.text or "", fallback)
