import os

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dotenv import load_dotenv

from app.db.database import SessionLocal
from app.models.email_model import Email

load_dotenv()

router = APIRouter()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly"
]


def create_flow():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
            }
        },
        scopes=SCOPES,
        autogenerate_code_verifier=False
    )

    flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return flow


@router.get("/google/login")
def google_login():
    flow = create_flow()

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    return RedirectResponse(auth_url)


@router.get("/google/callback")
def google_callback(request: Request):
    flow = create_flow()
    flow.fetch_token(authorization_response=str(request.url))

    creds = flow.credentials

    # Save token for Calendar/Gmail reuse
    with open("token.json", "w") as token_file:
        token_file.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId="me",
        maxResults=10
    ).execute()

    msgs = results.get("messages", [])
    emails = []

    db = SessionLocal()

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

        existing_email = db.query(Email).filter(
            Email.gmail_id == msg["id"]
        ).first()

        if not existing_email:
            new_email = Email(
                gmail_id=msg["id"],
                sender=email_data["from"],
                subject=email_data["subject"],
                snippet=email_data["snippet"],
                email_date=email_data["date"]
            )
            db.add(new_email)
            db.commit()

        emails.append(email_data)

    db.close()

    return {
        "message": "Gmail and Calendar connected successfully",
        "token_saved": True,
        "total_emails_fetched": len(emails),
        "emails": emails
    }
