"""
The orchestrator is the single entry point the API layer talks to for
"Ask Aura". It is what turns AURA from one big prompt into a small team of
collaborating specialists:

  router_agent      -> decides which specialist framing fits the question
  chat agent         -> (in ai_service.py) answers, grounded in synced data
                         + long-term memory, using the router's framing
  memory_agent       -> after answering, decides what's worth remembering
  task_strategist    -> (used separately, via /api/tasks/{id}/plan) turns a
                         single task into an executable action plan

Keeping this thin on purpose: the orchestrator's job is routing and
composition, not doing the actual generation work itself.
"""
import logging
from typing import Iterator, List, Dict

from app.agents.router_agent import classify_intent, INTENT_FRAMING
from app.agents.memory_agent import extract_memories
from app.services import ai_service

logger = logging.getLogger(__name__)


def ask_aura_stream(
    question: str,
    emails: List[Dict],
    tasks: List[Dict],
    events: List[Dict],
    notes: List[Dict],
    history: List[Dict],
    memories: List[Dict],
) -> Iterator[str]:
    intent = classify_intent(question)
    framing = INTENT_FRAMING.get(intent, INTENT_FRAMING["general"])

    yield from ai_service.ask_aura_stream(
        question, emails, tasks, events, notes, history, memories=memories, framing=framing
    )


def remember_from_exchange(question: str, answer: str) -> List[Dict]:
    """Runs the memory agent after a chat exchange. Safe to call even if the
    AI call fails - returns an empty list rather than raising, since a failed
    memory extraction should never break the chat response the user already got.
    """
    try:
        return extract_memories(question, answer)
    except Exception:
        logger.exception("Memory extraction failed")
        return []
