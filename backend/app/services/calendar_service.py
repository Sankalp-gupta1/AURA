import logging
from datetime import datetime, timezone
from typing import List, Dict

from googleapiclient.discovery import build

from app.services.google_oauth import credentials_from_user

logger = logging.getLogger(__name__)


def fetch_upcoming_events(user, max_results: int = 20) -> List[Dict]:
    creds = credentials_from_user(user)
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)

    now = datetime.now(timezone.utc).isoformat()
    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events: List[Dict] = []
    for ev in result.get("items", []):
        start = ev.get("start", {}).get("dateTime") or ev.get("start", {}).get("date", "")
        end = ev.get("end", {}).get("dateTime") or ev.get("end", {}).get("date", "")
        events.append(
            {
                "google_event_id": ev.get("id", ""),
                "title": ev.get("summary", "(untitled event)"),
                "description": ev.get("description", ""),
                "location": ev.get("location", ""),
                "start_time": start,
                "end_time": end,
                "meet_link": ev.get("hangoutLink", ""),
            }
        )
    return events


def create_event(user, title: str, start_time: str, end_time: str, description: str = "", location: str = "") -> Dict:
    creds = credentials_from_user(user)
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)

    body = {
        "summary": title,
        "description": description,
        "location": location,
        "start": {"dateTime": start_time},
        "end": {"dateTime": end_time},
    }
    created = service.events().insert(calendarId="primary", body=body).execute()
    return {
        "google_event_id": created.get("id", ""),
        "title": created.get("summary", title),
        "description": description,
        "location": location,
        "start_time": start_time,
        "end_time": end_time,
        "meet_link": created.get("hangoutLink", ""),
    }
