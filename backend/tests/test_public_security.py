"""Checks for public entry points and credential-free access logging."""
import logging
import unittest

from fastapi.testclient import TestClient
from app.main import app
from app.core.logging_config import OAuthQueryFilter


class PublicSecurityTests(unittest.TestCase):
    def test_browser_landing_page_identifies_aura_without_a_password_form(self):
        with TestClient(app) as client:
            response = client.get("/", headers={"Accept": "text/html"})
            self.assertEqual(response.status_code, 200)
            self.assertIn("It is not a Google product", response.text)
            self.assertNotIn("<form", response.text)
            self.assertIn("frame-ancestors 'none'", response.headers["content-security-policy"])

    def test_search_console_file_stays_public_and_exact(self):
        client = TestClient(app)
        response = client.get("/googlee9dc7450537262e6.html", follow_redirects=False)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "google-site-verification: googlee9dc7450537262e6.html")
        self.assertNotIn("set-cookie", response.headers)
        client.close()

    def test_oauth_codes_and_state_are_not_in_application_access_logs(self):
        record = logging.LogRecord("uvicorn.access", logging.INFO, "", 0, '%s - "%s %s HTTP/%s" %d',
                                   ("local", "GET", "/api/auth/google/callback?code=private-code&state=private-state", "1.1", 303), None)
        OAuthQueryFilter().filter(record)
        message = record.getMessage()
        self.assertNotIn("private-code", message)
        self.assertNotIn("private-state", message)
        self.assertIn("/api/auth/google/callback", message)
