"""
AURA AI service using Google Gemini.
This is the low-level LLM access layer - specialist agents in app/agents/
build on top of get_client()/generate_json/generate_text rather than
duplicating the client setup.
"""

import json
import logging
from typing import List, Dict, Iterator

from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings

logger = logging.getLogger(__name__)

_client = None


def get_client():
    global _client

    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to backend/.env before using AI features."
            )

        _client = genai.Client(api_key=settings.GEMINI_API_KEY)

    return _client


_RETRYABLE = (Exception,)


def _retry():
    return retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(_RETRYABLE),
    )


def _safe_json_loads(text: str, fallback: dict) -> dict:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        logger.warning(
            "AI returned non-JSON payload, using fallback. Raw: %.200s",
            text,
        )
        return fallback


SYSTEM_PERSONA = """You are AURA, a sharp and reliable AI Chief of Staff embedded in the
user's personal productivity dashboard. You are precise, practical, and never invent facts
that are not present in the provided context. When information is missing, say so plainly
instead of guessing."""


def _generate(prompt: str, temperature: float = 0.2) -> str:
    response = get_client().models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config={
            "temperature": temperature,
            "response_mime_type": "application/json",
        },
    )

    return response.text or ""


@_retry()
def analyze_and_extract(emails: List[Dict]) -> Dict:
    """Classify each email and pull out actionable tasks in a single pass."""

    if not emails:
        return {"emails": [], "tasks": []}

    email_block = "\n".join(
        f"[{i}] gmail_id={e['gmail_id']}\n"
        f"From: {e['sender']}\n"
        f"Subject: {e['subject']}\n"
        f"Date: {e['email_date']}\n"
        f"Snippet: {e['snippet']}"
        for i, e in enumerate(emails)
    )

    prompt = f"""{SYSTEM_PERSONA}

Analyze these {len(emails)} emails from the user's inbox.

For EACH email, output an object with:
- gmail_id (copy exactly from input)
- category: one of "security", "job_opportunity", "deadline", "personal", "newsletter", "spam", "general"
- priority: "High", "Medium", or "Low"
- is_important: boolean
- summary: one crisp sentence

Separately, extract a flat list of concrete actionable tasks across all emails.
Skip newsletters/spam unless truly actionable.

Each task needs:
- title
- description
- priority (High/Medium/Low)
- deadline (ISO date string or null)
- source_gmail_id

Return ONLY a JSON object with exactly two keys:
"emails" (array) and "tasks" (array).

EMAILS:
{email_block}
"""

    text = _generate(prompt, temperature=0.2)

    return _safe_json_loads(
        text,
        {"emails": [], "tasks": []},
    )


@_retry()
def generate_briefing(tasks: List, emails: List, events: List, memories: List[Dict] = None) -> Dict:

    task_text = "\n".join(
        f"- [{t.priority}] {t.title} "
        f"(due {t.deadline or 'no deadline'}, status {t.status})"
        for t in tasks
    ) or "None"

    email_text = "\n".join(
        f"- {e.subject} from {e.sender} "
        f"({e.category}, {e.priority})"
        for e in emails[:25]
    ) or "None"

    event_text = "\n".join(
        f"- {ev.title} at {ev.start_time} "
        f"({ev.location or 'no location'})"
        for ev in events[:10]
    ) or "None"

    memory_text = "\n".join(f"- {m['content']}" for m in (memories or [])[:10]) or "None"

    prompt = f"""{SYSTEM_PERSONA}

Generate today's executive briefing for the user based on their live data below.

Be specific and reference real items by name.
Never use generic filler.

WHAT YOU KNOW ABOUT THE USER LONG-TERM (their goals, preferences, ongoing situations -
use this to prioritize and frame the briefing, don't just repeat it back):
{memory_text}

PENDING TASKS:
{task_text}

RECENT IMPORTANT EMAILS:
{email_text}

UPCOMING CALENDAR EVENTS:
{event_text}

Return ONLY a JSON object with keys:

- daily_briefing (string, 3-5 sentences)
- top_focus (array of up to 4 short strings)
- risks (array of up to 3 short strings - things that could slip)
- suggested_actions (array of up to 4 short, concrete next actions)
- motivational_note (string, one short encouraging sentence, not cheesy)
"""

    text = _generate(prompt, temperature=0.4)

    fallback = {
        "daily_briefing": "Not enough synced data yet to build a briefing.",
        "top_focus": [],
        "risks": [],
        "suggested_actions": [],
        "motivational_note": "",
    }

    return _safe_json_loads(text, fallback)


def _build_context_block(
    emails: List,
    tasks: List,
    events: List,
    notes: List,
    memories: List[Dict] = None,
) -> str:

    email_text = "\n".join(
        f"- From: {e['sender']} | Subject: {e['subject']} | "
        f"Date: {e['email_date']} | {e['snippet']}"
        for e in emails[:40]
    ) or "None"

    task_text = "\n".join(
        f"- {t['title']} [{t['priority']}, {t['status']}] "
        f"due {t['deadline'] or 'n/a'}"
        for t in tasks
    ) or "None"

    event_text = "\n".join(
        f"- {ev['title']} at {ev['start_time']} "
        f"({ev['location'] or 'no location'})"
        for ev in events
    ) or "None"

    note_text = "\n".join(
        f"- {n['content']}"
        for n in notes[:15]
    ) or "None"

    memory_text = "\n".join(f"- {m['content']}" for m in (memories or [])[:15]) or "None"

    return (
        f"LONG-TERM MEMORY (things AURA has learned about the user over past sessions):\n{memory_text}\n\n"
        f"EMAILS:\n{email_text}\n\n"
        f"TASKS:\n{task_text}\n\n"
        f"CALENDAR EVENTS:\n{event_text}\n\n"
        f"NOTES:\n{note_text}"
    )


def ask_aura_stream(
    question: str,
    emails: List,
    tasks: List,
    events: List,
    notes: List,
    history: List[Dict],
    memories: List[Dict] = None,
    framing: str = "",
) -> Iterator[str]:
    """Generate an answer from Gemini for the AURA chat assistant."""

    context = _build_context_block(
        emails,
        tasks,
        events,
        notes,
        memories,
    )

    history_text = "\n".join(
        f"{h['role']}: {h['content']}"
        for h in history[-8:]
    )

    framing_line = f"\n{framing}\n" if framing else ""

    prompt = f"""{SYSTEM_PERSONA}

Answer using ONLY the CONTEXT below plus the conversation history and long-term memory.
{framing_line}
If the answer isn't in the context, say so clearly instead of guessing.

Be concise and specific.
Cite senders, subjects, and dates when relevant.

CONTEXT:
{context}

CONVERSATION HISTORY:
{history_text}

USER QUESTION:
{question}
"""

    try:
        response = get_client().models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config={
                "temperature": 0.3,
            },
        )

        text = response.text or ""

        if text:
            yield text

    except Exception as exc:
        logger.exception("Gemini chat failed")
        yield f"\n\n[AURA hit an error talking to the AI provider: {exc}]"
