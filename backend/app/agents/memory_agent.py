"""
After each chat exchange, this agent decides whether anything durable was
revealed about the user - a goal, a preference, an ongoing situation - that
AURA should carry forward into future conversations and briefings. Most
exchanges reveal nothing worth remembering long-term, and that's fine: the
agent is instructed to return an empty list rather than force something.
"""
from typing import List, Dict

from app.agents.base import generate_json

MEMORY_EXTRACTION_PROMPT = """You are AURA's memory module. Read this single exchange between
the user and AURA. Decide if it reveals any DURABLE fact worth remembering across future
sessions - a goal, a stated preference, an ongoing situation (e.g. "job hunting for backend
roles", "prefers short answers", "has a thesis deadline in October"). Do NOT record one-off,
transient details (e.g. "asked about today's weather") or anything already obvious from a
single email.

If nothing durable was revealed, return an empty list. Do not force it.

USER: {question}
AURA: {answer}

Return ONLY a JSON object: {{"memories": [{{"content": str, "category":
"fact"|"preference"|"goal"|"ongoing_situation", "importance": 1-5}}]}}
"""


def extract_memories(question: str, answer: str) -> List[Dict]:
    if not answer.strip():
        return []

    prompt = MEMORY_EXTRACTION_PROMPT.format(question=question, answer=answer[:2000])
    data = generate_json(prompt, fallback={"memories": []}, temperature=0.1)
    memories = data.get("memories", [])

    # Basic shape validation - never let a malformed AI response corrupt storage.
    cleaned = []
    for m in memories:
        content = str(m.get("content", "")).strip()
        if not content:
            continue
        cleaned.append(
            {
                "content": content[:500],
                "category": m.get("category") if m.get("category") in {"fact", "preference", "goal", "ongoing_situation"} else "fact",
                "importance": max(1, min(5, int(m.get("importance", 3) or 3))),
            }
        )
    return cleaned
