import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_emails(emails):
    email_text = ""

    for e in emails:
        email_text += f"""
From: {e.sender}
Subject: {e.subject}
Snippet: {e.snippet}
Date: {e.email_date}
---
"""

    prompt = f"""
You are Life OS AI, a personal AI Chief of Staff.

Analyze these emails and return:

1. Short inbox summary
2. Important tasks
3. Deadlines
4. Priority emails
5. Suggested next actions

Emails:
{email_text}

Return clean JSON only with these keys:
summary, tasks, deadlines, priority_emails, suggested_actions
"""

    response = model.generate_content(prompt)
    return response.text


def extract_tasks_from_emails(emails):
    email_text = ""

    for e in emails:
        email_text += f"""
Email ID: {e.id}
From: {e.sender}
Subject: {e.subject}
Snippet: {e.snippet}
Date: {e.email_date}
---
"""

    prompt = f"""
You are Life OS AI.

Extract actionable tasks from the emails below.

Rules:
- Only extract real tasks that require user action.
- Ignore spam, ads, and generic job alerts unless user action is useful.
- If deadline is not present, use null.
- Priority must be High, Medium, or Low.
- Return only valid JSON array.
- No markdown.
- No explanation.

Each task must have:
title, description, priority, deadline, source_email_id

Emails:
{email_text}

Example:
[
  {{
    "title": "Review Google security alert",
    "description": "Check whether the recent Linux sign-in was authorized.",
    "priority": "High",
    "deadline": null,
    "source_email_id": 3
  }}
]
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()

    if text.startswith("```"):
        text = text.replace("```", "").strip()

    return json.loads(text)

def generate_dashboard_ai_summary(tasks, emails, events):
    task_text = ""

    for t in tasks:
        task_text += f"""
Task: {t.title}
Description: {t.description}
Priority: {t.priority}
Deadline: {t.deadline}
Status: {t.status}
---
"""

    email_text = ""

    for e in emails:
        email_text += f"""
From: {e.sender}
Subject: {e.subject}
Snippet: {e.snippet}
Date: {e.email_date}
---
"""

    event_text = ""

    for ev in events:
        event_text += f"""
Event: {ev.title}
Start: {ev.start_time}
End: {ev.end_time}
Location: {ev.location}
---
"""

    prompt = f"""
You are Life OS AI, a personal AI Chief of Staff.

Use the user's tasks, emails, and calendar events to generate a practical daily briefing.

Return only valid JSON. No markdown.

JSON keys:
daily_briefing, top_focus, risks, suggested_actions, motivational_note

Tasks:
{task_text}

Emails:
{email_text}

Calendar Events:
{event_text}
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()

    if text.startswith("```"):
        text = text.replace("```", "").strip()

    return text


def ask_aura(question, emails, tasks, events):
    email_text = "\n".join([
        f"From: {e.sender}\nSubject: {e.subject}\nDate: {e.email_date}\nSnippet: {e.snippet}"
        for e in emails
    ])

    task_text = "\n".join([
        f"Task: {t.title}\nPriority: {t.priority}\nStatus: {t.status}\nDescription: {t.description}"
        for t in tasks
    ])

    event_text = "\n".join([
        f"Event: {ev.title}\nStart: {ev.start_time}\nEnd: {ev.end_time}\nLocation: {ev.location}"
        for ev in events
    ])

    prompt = f"""
You are Aura, an intelligent personal Chief of Staff inside Life OS AI.

Answer the user's question using ONLY the context below.
If the answer is not available in the context, clearly say:
"I could not find this in your saved Life OS data."

Be practical, specific, and concise.
If the question is about an email, mention sender, subject, date, and action needed.
If the question is about jobs, assessments, interviews, deadlines, or applications, prioritize them.
Ignore newsletters unless the user specifically asks about news.

USER QUESTION:
{question}

EMAIL CONTEXT:
{email_text}

TASK CONTEXT:
{task_text}

CALENDAR CONTEXT:
{event_text}
"""

    response = model.generate_content(prompt)
    return response.text
