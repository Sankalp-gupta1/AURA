"""Exercise the built Next.js app and FastAPI together with synthetic accounts.

Build frontend first, then run: python tests/check_session_roundtrip.py
No Google login, real account, secrets, or third-party data writes are used.
"""
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, urlparse

import httpx


def unused_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class SessionRoundTrip(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory(prefix="aura-auth-test-")
        cls.processes = []
        cls.logs = []
        # Loopback-only test servers; do not route localhost through a shell proxy.
        cls.client = httpx.Client(timeout=15, follow_redirects=False, trust_env=False)
        root = Path(__file__).resolve().parents[2]
        backend_port, frontend_port = unused_port(), unused_port()
        cls.backend = f"http://127.0.0.1:{backend_port}"
        cls.frontend = f"http://127.0.0.1:{frontend_port}"
        env = {**os.environ, "DATABASE_URL": f"sqlite:///{cls.folder.name}/test.db",
               "ENVIRONMENT": "development", "SECRET_KEY": "synthetic-test-only-key",
               "GOOGLE_CLIENT_ID": "fixture-client", "GOOGLE_CLIENT_SECRET": "fixture-secret",
               "GEMINI_API_KEY": "", "AURA_LOCAL_AUTH_TEST": "1",
               "FRONTEND_URL": cls.frontend, "BACKEND_URL": cls.backend,
               "GOOGLE_REDIRECT_URI": f"{cls.backend}/api/auth/google/callback",
               "PYTHONPATH": str(root / "backend"), "NODE_ENV": "production"}
        commands = [
            ([sys.executable, "-m", "uvicorn", "oauth_fixture:app", "--app-dir", "tests", "--host", "127.0.0.1", "--port", str(backend_port)], root / "backend", cls.backend + "/api/health"),
            (["node", "node_modules/next/dist/bin/next", "start", "-H", "127.0.0.1", "-p", str(frontend_port)], root / "frontend", cls.frontend + "/"),
        ]
        try:
            for command, cwd, url in commands:
                log = open(Path(cls.folder.name) / f"server-{len(cls.logs)}.log", "w+")
                cls.logs.append(log)
                process = subprocess.Popen(command, cwd=cwd, env=env, stdout=log, stderr=log)
                cls.processes.append(process)
                deadline = time.monotonic() + 45
                while time.monotonic() < deadline:
                    if process.poll() is not None:
                        log.seek(0)
                        raise RuntimeError("Test server failed to start: " + log.read())
                    try:
                        if cls.client.get(url).status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.15)
                else:
                    raise RuntimeError("Test server startup timed out")
        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        for process in reversed(cls.processes):
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        cls.client.close()
        for log in cls.logs:
            log.close()
        cls.folder.cleanup()

    def sign_in(self, account):
        start = self.client.get(self.frontend + "/api/auth/google/login")
        self.assertEqual(start.status_code, 303)
        cookie = SimpleCookie(start.headers["set-cookie"])["__Host-aura_login_verifier"]
        self.assertTrue(cookie["httponly"])
        self.assertTrue(cookie["secure"])
        self.assertEqual(cookie["samesite"], "lax")
        self.assertEqual(start.headers["cache-control"], "no-store")
        self.assertTrue(start.headers["location"].startswith(self.backend + "/api/auth/google/login?challenge="))
        google = self.client.get(start.headers["location"])
        self.assertEqual(urlparse(google.headers["location"]).hostname, "accounts.google.com")
        parameters = parse_qs(urlparse(google.headers["location"]).query)
        self.assertEqual(parameters["redirect_uri"], [self.backend + "/api/auth/google/callback"])
        # Stop at Google's URL; only the provider calls are mocked by the fixture.
        returned = self.client.get(self.backend + "/api/auth/google/callback", params={"code": f"fixture-{account}", "state": parameters["state"][0]})
        self.assertEqual(returned.status_code, 303)
        callback = returned.headers["location"]
        self.assertEqual(urlparse(callback).fragment, "")
        self.assertNotIn("token=", callback)
        # Secure cookies are sent explicitly because this isolated test uses HTTP.
        verifier_cookie = f"__Host-aura_login_verifier={cookie.value}"
        completed = self.client.get(callback, headers={"Cookie": verifier_cookie})
        self.assertEqual(completed.status_code, 303)
        self.assertEqual(urlparse(completed.headers["location"]).path, "/dashboard")
        response_cookies = SimpleCookie()
        for value in completed.headers.get_list("set-cookie"):
            response_cookies.load(value)
        session = response_cookies["__Host-aura_session"]
        self.assertTrue(session["httponly"])
        self.assertTrue(session["secure"])
        self.assertEqual(session["path"], "/")
        self.assertEqual(session["domain"], "")
        self.assertNotIn(session.value, completed.text + completed.headers["location"])
        replay = self.client.get(callback, headers={"Cookie": verifier_cookie})
        self.assertIn("oauth_failed", replay.headers["location"])
        self.assertNotIn("__Host-aura_session=", replay.headers.get("set-cookie", ""))
        return {"Cookie": f"__Host-aura_session={session.value}", "Origin": self.frontend}

    def test_full_sign_in_private_api_csrf_stream_and_revocable_logout(self):
        self.assertEqual(self.client.get(self.frontend + "/api/auth/me").status_code, 401)
        alice = self.sign_in("alice")
        bob = self.sign_in("bob")
        me = self.client.get(self.frontend + "/api/auth/me", headers=alice)
        self.assertEqual(me.json()["email"], "fixture-alice@example.test")
        self.assertEqual(me.headers["cache-control"], "no-store")
        self.assertNotIn("access_token", me.text)
        task = self.client.post(self.frontend + "/api/tasks", headers=alice, json={"title": "Alice private task"})
        self.assertEqual(task.status_code, 200)
        self.assertEqual(self.client.get(self.frontend + "/api/tasks", headers=bob).json(), [])
        self.assertEqual(self.client.delete(self.frontend + f"/api/tasks/{task.json()['id']}", headers=bob).status_code, 404)
        for origin in ("https://unrelated.example", "null", ""):
            denied = self.client.post(self.frontend + "/api/tasks", headers={**alice, "Origin": origin}, json={"title": "Blocked"})
            self.assertEqual(denied.status_code, 403)
        self.assertEqual(len(self.client.get(self.frontend + "/api/tasks", headers=alice).json()), 1)
        self.assertEqual(self.client.post(self.frontend + "/api/auth/session/exchange", headers=alice, json={}).status_code, 404)
        self.assertEqual(self.client.get(self.frontend + "/api/auth/google%2Fcallback", headers=alice).status_code, 404)
        self.assertEqual(self.client.post(self.frontend + "/api/notes", headers=alice, json={"content": "x" * (1024 * 1024)}).status_code, 413)
        answer = self.client.post(self.frontend + "/api/ask", headers=alice, json={"question": "Test stream"})
        self.assertEqual(answer.status_code, 200)
        self.assertIn("text/event-stream", answer.headers["content-type"])
        self.assertIn("Synthetic test answer.", answer.text)
        self.assertIn('"done": true', answer.text)
        out = self.client.post(self.frontend + "/api/auth/logout", headers=alice)
        self.assertEqual(out.status_code, 200)
        self.assertIn("Max-Age=0", out.headers["set-cookie"])
        self.assertEqual(self.client.get(self.frontend + "/api/auth/me", headers=alice).status_code, 401)
        self.assertEqual(self.client.get(self.frontend + "/api/auth/me", headers=bob).status_code, 200)
        print("Verified: Google handoff, HttpOnly cookies, account isolation, CSRF, streaming and logout revocation (synthetic accounts only).")


if __name__ == "__main__":
    unittest.main(verbosity=2)
