"""
Given one task plus the user's surrounding context (related emails, notes),
this agent proposes a small set of CONCRETE actions AURA could take to move
it forward - not generic advice, but structured actions the rest of the
system knows how to actually execute (create a calendar event, draft a
reply, add a sub-task, set a reminder). Nothing here executes on its own;
autonomous_executor.py only acts once the user approves a specific proposal.
"""
from typing import List, Dict

from app.agents.base import generate_json

ACTION_TYPES = ("create_event", "draft_reply", "add_subtask", "set_reminder")

PLAN_PROMPT = """You are AURA's task strategist. Propose 2-4 CONCRETE next actions to move
this task forward. Every action must be one of these exact types:

- "create_event": schedule something on the calendar. payload: {{"title": str, "start_time":
  ISO 8601 datetime, "end_time": ISO 8601 datetime, "location": str}}
- "draft_reply": draft an email reply (never sent automatically - just drafted for the user
  to review). payload: {{"to": str (best guess, empty string if unknown), "subject": str, "body": str}}
- "add_subtask": break the task into a smaller step. payload: {{"title": str, "priority":
  "High"|"Medium"|"Low"}}
- "set_reminder": a simple reminder note with no calendar entry. payload: {{"remind_at": ISO
  8601 date or empty string, "note": str}}

Today's date/time for reference: {now}

TASK:
Title: {title}
Description: {description}
Priority: {priority}
Deadline: {deadline}

RELEVANT CONTEXT (recent emails/notes that might relate to this task):
{context}

Return ONLY a JSON object: {{"actions": [{{"action_type": str, "title": str, "description":
str, "payload": {{...}}}}]}}. Keep titles short (under 10 words). Only propose actions that
are genuinely useful - fewer good actions beats padding to 4.
"""


def build_plan(task, context_block: str, now_iso: str) -> List[Dict]:
    prompt = PLAN_PROMPT.format(
        now=now_iso,
        title=task.title,
        description=task.description or "(none)",
        priority=task.priority,
        deadline=task.deadline or "(none)",
        context=context_block or "None",
    )
    data = generate_json(prompt, fallback={"actions": []}, temperature=0.3)
    actions = data.get("actions", [])

    cleaned = []
    for a in actions:
        action_type = a.get("action_type")
        if action_type not in ACTION_TYPES:
            continue
        cleaned.append(
            {
                "action_type": action_type,
                "title": str(a.get("title", "Untitled action"))[:120],
                "description": str(a.get("description", ""))[:500],
                "payload": a.get("payload", {}) if isinstance(a.get("payload"), dict) else {},
            }
        )
    return cleaned
