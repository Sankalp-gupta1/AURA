from fastapi import APIRouter
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime

from app.db.database import SessionLocal
from app.models.calendar_model import CalendarEvent

router = APIRouter(
    prefix="/api/calendar",
    tags=["Calendar"]
)


@router.get("/")
def get_calendar_events():
    creds = Credentials.from_authorized_user_file(
        "token.json",
        [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/calendar.readonly"
        ]
    )

    service = build("calendar", "v3", credentials=creds)

    now = datetime.utcnow().isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    db = SessionLocal()
    result = []

    for event in events:
        event_id = event.get("id")
        title = event.get("summary", "No Title")
        start_time = event["start"].get("dateTime", event["start"].get("date"))
        end_time = event["end"].get("dateTime", event["end"].get("date"))
        location = event.get("location", "")
        description = event.get("description", "")

        existing_event = db.query(CalendarEvent).filter(
            CalendarEvent.event_id == event_id
        ).first()

        if not existing_event:
            new_event = CalendarEvent(
                event_id=event_id,
                title=title,
                start_time=start_time,
                end_time=end_time,
                location=location,
                description=description
            )
            db.add(new_event)
            db.commit()

        result.append({
            "event_id": event_id,
            "title": title,
            "start": start_time,
            "end": end_time,
            "location": location,
            "description": description
        })

    db.close()

    return {
        "message": "Calendar events fetched and saved successfully",
        "total_events": len(result),
        "events": result
    }
