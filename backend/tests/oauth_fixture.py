"""Local-only provider fixture. Production never imports this module.

Run only through check_session_roundtrip.py: no real Google or AI requests occur.
"""
import os
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

if os.environ.get("AURA_LOCAL_AUTH_TEST") != "1":
    raise RuntimeError("This fixture is only for isolated local authentication tests.")

import app.main as main
from app.api import auth, ask


def exchange_code(code, code_verifier):
    if code not in ("fixture-alice", "fixture-bob"):
        raise ValueError("Unknown fixture account")
    return SimpleNamespace(token=code, refresh_token="fixture-refresh", scopes=["openid"],
                           granted_scopes=["openid"], expiry=datetime.now(timezone.utc) + timedelta(hours=1))


class Profile:
    def __init__(self, account):
        self.account = account

    def userinfo(self):
        return self

    def get(self):
        return self

    def execute(self):
        return {"id": self.account, "email": f"{self.account}@example.test", "verified_email": True}


auth.google_oauth.exchange_code = exchange_code
auth.build = lambda *args, credentials, **kwargs: Profile(credentials.token)
ask.orchestrator.ask_aura_stream = lambda *args: iter(["Synthetic test answer."])
ask.orchestrator.remember_from_exchange = lambda *args: []
main.start_scheduler = lambda: None
main.stop_scheduler = lambda: None
app = main.app
