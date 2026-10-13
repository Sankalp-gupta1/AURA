"""Local integration tests; Google/Gemini calls are mocked and no real account is used."""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["ENVIRONMENT"] = "development"
os.environ["SECRET_KEY"] = "isolated-test-key-never-for-production"

import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.models.user import User
from app.models.email_model import Email
from app.models.calendar_model import Event
from app.core.security import create_access_token, decrypt_secret, encrypt_secret
from app.services.sync_service import sync_user_data
from app.services.google_oauth import credentials_from_user


class AccountFlowTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.sessions = sessionmaker(bind=self.engine, expire_on_commit=False)
        with self.sessions() as db:
            users = [User(google_id="alice", email="alice@example.test"), User(google_id="bob", email="bob@example.test")]
            db.add_all(users)
            db.commit()
            self.alice, self.bob = [u.id for u in users]
        def test_db():
            with self.sessions() as db:
                yield db
        app.dependency_overrides[get_db] = test_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def headers(self, user_id):
        return {"Authorization": f"Bearer {create_access_token(user_id)}"}

    def test_signed_out_users_cannot_read_private_data(self):
        for path in ("/api/auth/me", "/api/emails", "/api/calendar", "/api/tasks", "/api/notes", "/api/memory"):
            self.assertEqual(self.client.get(path).status_code, 401, path)

    def test_accounts_cannot_read_or_change_each_others_data(self):
        a, b = self.headers(self.alice), self.headers(self.bob)
        task = self.client.post("/api/tasks", headers=a, json={"title": "Alice only"}).json()
        self.assertEqual(self.client.get("/api/tasks", headers=b).json(), [])
        self.assertEqual(self.client.patch(f"/api/tasks/{task['id']}", headers=b, json={"status": "done"}).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/tasks/{task['id']}", headers=b).status_code, 404)
        with self.sessions() as db:
            mail = Email(user_id=self.alice, gmail_id="private", sender="sender@example.test", subject="Private", snippet="Alice only", email_date="")
            event = Event(user_id=self.alice, google_event_id="private", title="Private", start_time="2026-10-14T10:00:00Z", end_time="2026-10-14T11:00:00Z")
            db.add_all([mail, event]); db.commit()
            mail_id = mail.id
        self.assertEqual(self.client.get("/api/emails", headers=b).json(), [])
        self.assertEqual(self.client.get("/api/calendar", headers=b).json(), [])
        self.assertEqual(self.client.get(f"/api/emails/{mail_id}", headers=b).status_code, 404)
        self.assertEqual(self.client.get("/api/auth/me", headers=a).json()["email"], "alice@example.test")

    def test_callback_rejects_forged_state_before_contacting_google(self):
        with patch("app.api.auth.google_oauth.exchange_code") as exchange:
            r = self.client.get("/api/auth/google/callback?code=unused&state=wrong", follow_redirects=False)
        self.assertIn("oauth_state", r.headers["location"])
        exchange.assert_not_called()

    def test_cancelled_consent_returns_a_friendly_redirect(self):
        self.client.cookies.set("aura_oauth_state", "test-state")
        r = self.client.get("/api/auth/google/callback?error=access_denied&state=test-state", follow_redirects=False)
        self.assertIn("oauth_cancelled", r.headers["location"])

    def test_login_returns_before_syncing_and_encrypts_google_tokens(self):
        self.client.cookies.set("aura_oauth_state", "test-state")
        creds = SimpleNamespace(token="test-access", refresh_token="test-refresh", expiry=datetime.now(timezone.utc)+timedelta(hours=1), granted_scopes=["openid"], scopes=["openid"])
        with patch("app.api.auth.google_oauth.exchange_code", return_value=creds), patch("app.api.auth.build") as google, patch("app.services.gmail_service.fetch_recent_emails") as sync:
            google.return_value.userinfo.return_value.get.return_value.execute.return_value = {"id": "alice", "email": "alice@example.test", "verified_email": True}
            r = self.client.get("/api/auth/google/callback?code=unused&state=test-state", follow_redirects=False)
        self.assertEqual(r.status_code, 307)
        self.assertTrue(r.headers["location"].endswith("/dashboard"))
        sync.assert_not_called()
        with self.sessions() as db:
            user = db.get(User, self.alice)
            self.assertTrue(user.access_token.startswith("enc:"))
            self.assertEqual(decrypt_secret(user.refresh_token), "test-refresh")

    def test_failed_sync_does_not_claim_success(self):
        with self.sessions() as db, patch("app.services.gmail_service.fetch_recent_emails", side_effect=RuntimeError("unavailable")), patch("app.services.calendar_service.fetch_upcoming_events", side_effect=RuntimeError("unavailable")):
            result = sync_user_data(db, db.get(User, self.alice))
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["synced_at"], "")
        self.assertEqual(len(result["warnings"]), 2)

    def test_sync_updates_changed_calendar_event_without_duplicate(self):
        event = {"google_event_id": "event", "title": "Before", "start_time": "2026-10-14T10:00:00Z", "end_time": "2026-10-14T11:00:00Z"}
        with self.sessions() as db, patch("app.services.gmail_service.fetch_recent_emails", return_value=[]), patch("app.services.calendar_service.fetch_upcoming_events", side_effect=[[event], [{**event, "title": "After"}]]):
            user = db.get(User, self.alice)
            sync_user_data(db, user)
            result = sync_user_data(db, user)
            self.assertEqual(db.query(Event).count(), 1)
            self.assertEqual(db.query(Event).one().title, "After")
            self.assertEqual(result["new_events"], 0)

    def test_expired_google_credentials_are_refreshed_and_stored_encrypted(self):
        user = SimpleNamespace(access_token=encrypt_secret("old"), refresh_token=encrypt_secret("refresh"), granted_scopes="openid", token_expiry=(datetime.now(timezone.utc)-timedelta(hours=1)).isoformat(), id=1)
        def refreshed(creds, request):
            creds.token = "new"
            creds.expiry = datetime.now(timezone.utc).replace(tzinfo=None)+timedelta(hours=1)
        with patch("google.oauth2.credentials.Credentials.refresh", autospec=True, side_effect=refreshed) as refresh:
            credentials_from_user(user)
        refresh.assert_called_once()
        self.assertTrue(user.access_token.startswith("enc:"))
        self.assertEqual(decrypt_secret(user.access_token), "new")

    def test_calendar_rejects_missing_timezone_and_reversed_times(self):
        for start, end in [("2026-10-14T10:00", "2026-10-14T11:00"), ("2026-10-14T11:00:00Z", "2026-10-14T10:00:00Z")]:
            r = self.client.post("/api/calendar", headers=self.headers(self.alice), json={"title": "Meeting", "start_time": start, "end_time": end})
            self.assertEqual(r.status_code, 422)


if __name__ == "__main__":
    unittest.main()
