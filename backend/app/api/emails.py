from fastapi import APIRouter
from app.db.database import SessionLocal
from app.models.email_model import Email
from app.services.ai_service import analyze_emails

router = APIRouter()


@router.get("/")
def get_emails():
    db = SessionLocal()

    emails = db.query(Email).order_by(Email.id.desc()).limit(20).all()

    result = []

    for e in emails:
        result.append({
            "id": e.id,
            "gmail_id": e.gmail_id,
            "from": e.sender,
            "subject": e.subject,
            "snippet": e.snippet,
            "date": e.email_date
        })

    db.close()

    return {
        "total": len(result),
        "emails": result
    }


@router.get("/analyze")
def analyze_stored_emails():
    db = SessionLocal()

    emails = db.query(Email).order_by(Email.id.desc()).limit(20).all()

    ai_result = analyze_emails(emails)

    db.close()

    return {
        "message": "Email analysis completed",
        "analysis": ai_result
    }

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly"
]


@router.get("/sync")
def sync_latest_emails():
    db = SessionLocal()

    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId="me",
        maxResults=20
    ).execute()

    msgs = results.get("messages", [])
    saved = 0
    emails = []

    for msg in msgs:
        data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()

        headers = data.get("payload", {}).get("headers", [])

        email_data = {
            "id": msg["id"],
            "snippet": data.get("snippet", ""),
            "from": "",
            "subject": "",
            "date": ""
        }

        for h in headers:
            if h["name"] == "From":
                email_data["from"] = h["value"]
            elif h["name"] == "Subject":
                email_data["subject"] = h["value"]
            elif h["name"] == "Date":
                email_data["date"] = h["value"]

        exists = db.query(Email).filter(
            Email.gmail_id == msg["id"]
        ).first()

        if not exists:
            new_email = Email(
                gmail_id=msg["id"],
                sender=email_data["from"],
                subject=email_data["subject"],
                snippet=email_data["snippet"],
                email_date=email_data["date"]
            )
            db.add(new_email)
            saved += 1

        emails.append(email_data)

    db.commit()
    db.close()

    return {
        "message": "Latest Gmail emails synced successfully",
        "fetched": len(emails),
        "new_saved": saved,
        "emails": emails
    }
