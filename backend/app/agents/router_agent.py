"""
Routes an incoming "Ask Aura" question to the specialist agent best suited
to answer it. This is deliberately rule-based rather than an extra LLM call:
free-tier Gemini quota is precious (as little as ~20 requests/day on some
models), so spending one of those requests just to classify intent before
even answering would be wasteful. A handful of keyword patterns gets us
90% of the routing value for 0% of the extra cost.
"""

TASK_PLANNING_KEYWORDS = (
    "plan", "next steps", "how do i", "how should i", "break down",
    "execute", "help me finish", "what should i do about", "strategy for",
)
EMAIL_KEYWORDS = ("email", "inbox", "sender", "who emailed", "message from", "mail")
BRIEFING_KEYWORDS = ("today", "briefing", "summary", "summarize", "focus", "priorit", "risk")
CALENDAR_KEYWORDS = ("calendar", "meeting", "event", "schedule", "when is")

Intent = str  # "task_planning" | "email_query" | "briefing_query" | "calendar_query" | "general"


def classify_intent(question: str) -> Intent:
    q = question.lower()

    if any(k in q for k in TASK_PLANNING_KEYWORDS):
        return "task_planning"
    if any(k in q for k in CALENDAR_KEYWORDS):
        return "calendar_query"
    if any(k in q for k in EMAIL_KEYWORDS):
        return "email_query"
    if any(k in q for k in BRIEFING_KEYWORDS):
        return "briefing_query"
    return "general"


# Short framing line injected into the chat agent's system prompt per intent,
# so the same underlying model answers differently depending on which
# specialist "persona" the router decided fits best.
INTENT_FRAMING = {
    "task_planning": (
        "The user is asking how to approach or execute something. Give a short, concrete, "
        "numbered plan. If this relates to a specific task on their board, mention that they "
        "can click 'Plan with AURA' on that task for a one-click actionable plan with real "
        "calendar events and drafts, not just advice."
    ),
    "email_query": "The user is asking about their inbox. Reference specific senders, subjects, and dates from the EMAILS context.",
    "briefing_query": "The user wants a summary or prioritization. Be direct about what matters most right now and why.",
    "calendar_query": "The user is asking about their schedule. Reference specific events, times, and locations from the CALENDAR EVENTS context.",
    "general": "Answer naturally using the context provided.",
}
