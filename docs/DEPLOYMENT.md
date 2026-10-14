# Deploy AURA with real Google accounts

AURA has two separate experiences. `web/` is a sample-data demo. The Next.js app in
`frontend/` talks to the FastAPI app in `backend/` and uses each signed-in user's
own Gmail and Google Calendar account. Deploy those two folders for real accounts.

## Existing Render services

| Setting | Value |
| --- | --- |
| Backend service | `aura-backend` |
| Backend URL | `https://aura-backend-015h.onrender.com` |
| Backend health check | `/api/health` |
| Frontend service | `aura-frontend` |
| Frontend URL | `https://aura-frontend-gmuw.onrender.com` |
| Database | Existing `aura-db` PostgreSQL service |

These are service addresses, not a claim that Google has approved the app for
unrestricted public use. Google access is currently configured for external test
users. Check the Audience page before inviting anyone to connect a real account.

The backend hostname contains the digits **015**, not `0l5` (a letter l).

## Security update and sign-in flow

The October 14 update replaces the previous URL-fragment/localStorage JWT with a
revocable session held in a frontend HttpOnly cookie. Existing users need to sign
in again. No user data or stored Google connection is deleted by this migration.
On backend startup, SQLAlchemy creates two additional tables: `auth_sessions` and
`login_handoffs`. Keep the database and `SECRET_KEY` from the existing deployment.

1. The frontend starts sign-in and keeps a temporary verifier in an HttpOnly cookie.
2. The backend sends the user to Google's official authorization endpoint with
   OAuth state and PKCE. It preserves the same Google PKCE verifier for the callback.
3. Google returns to the **existing backend callback**. No Cloud Console redirect
   change is needed for this update.
4. The backend returns a two-minute, single-use handoff code to the frontend.
   The code cannot be exchanged without the original frontend verifier.
5. The frontend server exchanges that code and sets a Secure, HttpOnly, SameSite=Lax
   session cookie. Session values are hashed in the database and never sent to
   browser JavaScript or placed in a redirect URL.
6. Browser data requests go to the frontend's `/api/...` routes. Its server adds
   the upstream bearer credential. Cross-site mutations are rejected.
7. Logout revokes the current server session and clears the cookie.

Google Search Console ownership is verified, but a “Deceptive pages” warning was
reported with no example URL. Code checks cannot clear that classification. See
[the security review notes](SECURITY_REVIEW.md) for the investigation scope and a
review draft. A real Google-account sign-in and live Gmail/Calendar sync still
need an acceptance check after the browser warning is resolved.

## Environment variables

Set these public URLs on the relevant service. Keep all secrets on the backend.

```text
# Backend on Render
ENVIRONMENT=production
BACKEND_URL=https://aura-backend-015h.onrender.com
FRONTEND_URL=https://aura-frontend-gmuw.onrender.com
GOOGLE_REDIRECT_URI=https://aura-backend-015h.onrender.com/api/auth/google/callback

# Frontend server
BACKEND_URL=https://aura-backend-015h.onrender.com
FRONTEND_URL=https://aura-frontend-gmuw.onrender.com
```

The existing Render frontend already has `NEXT_PUBLIC_API_URL`; the server accepts
it as a fallback, so this update needs no new secret or mandatory environment
change there. Render's `RENDER_EXTERNAL_HOSTNAME` supplies the frontend origin.
For other hosts or custom domains, set `FRONTEND_URL` explicitly to the public
HTTPS origin. Do not use the backend URL as the frontend origin.

The backend also requires `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`,
`GEMINI_API_KEY`, `SECRET_KEY` and `DATABASE_URL`. Enter them in Render's environment
settings. Never put them in `NEXT_PUBLIC_*`, this README, source files or chat.
Keep `SECRET_KEY` stable: it also encrypts stored Google refresh tokens.

For Vercel, import this repository with **Root Directory `frontend`**, the Next.js
preset, install command `npm ci`, and build command `npm run build`. Set the same
`BACKEND_URL` and public frontend `FRONTEND_URL` for that deployment. Once the production domain is assigned,
change backend `FRONTEND_URL` to that exact HTTPS origin and redeploy the backend.
Do not point the real application at the sample-data `web/` folder.

## Google Cloud configuration

Use the existing AURA project with Gmail API and Google Calendar API enabled.
Use an OAuth client of type **Web application**.

Authorized JavaScript origins (no path or trailing slash):

```text
http://localhost:3000
https://aura-frontend-gmuw.onrender.com
```

If using Vercel, add its final production origin too. The server-side flow uses
the **redirect URI** for its callback; a JavaScript origin cannot replace it.

Authorized redirect URIs (exact matches):

```text
http://localhost:8000/api/auth/google/callback
https://aura-backend-015h.onrender.com/api/auth/google/callback
```

Required scopes:

```text
openid
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/calendar
```

While the app is **External / Testing**, add each intended user's Google email
under **Audience → Test users**. Test access is not a public launch. Test-mode
refresh tokens for these scopes expire after seven days, so users may need to
reconnect. Public Gmail access requires Google's restricted-scope verification
unless an exception applies; server-side handling can also require a security
assessment. Publishing alone does not mean verification is complete. Prepare an
accurate public homepage, privacy policy, verified domains, scope justifications
and a demonstration of the actual OAuth/data flow before requesting review.

Official setup and review guidance:

- https://developers.google.com/identity/protocols/oauth2/web-server
- https://support.google.com/cloud/answer/15549945
- https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification

## What a user does

1. Open the frontend and select **Get started with Google**.
2. Choose their own Google account and review the permissions.
3. After sign-in, choose **Sync my account**. Login itself does not wait for AI or a full inbox import.
4. Review recent emails, upcoming events and suggested tasks. Check AI output before acting on it.
5. Use **Sync now** to refresh data. Partial connection failures are shown instead of silently reported as success.
6. Sign out using the button in the top bar. Google access can also be revoked from their Google Account settings.

## Checks before sharing

```bash
cd backend
python -m unittest discover -s tests -v

cd ../frontend
npm ci
npm run build
npm run lint

cd ../backend
python tests/check_session_roundtrip.py
```

Backend tests use an isolated in-memory database and mocked Google calls. They
cover account separation, unauthenticated requests, OAuth state/cancellation,
encrypted token storage, refresh behavior, failed sync reporting and event times.
The separate round-trip check runs the built Next.js app and FastAPI together,
with synthetic Google profiles and a temporary SQLite database. It checks cookies,
replay rejection, private data, CSRF, streaming and logout. Neither check proves
that live Google credentials or consent settings are correct.

For a deployed smoke test, check the homepage, `/api/health`, the Google redirect,
and sign in with an authorized test user. Verify that a second user sees their own
workspace. Test a calendar write only with the user's explicit approval.

## Hosting limits

Render free web services can sleep after inactivity, so the first request may take
about a minute. A sleeping service cannot guarantee a background sync every 15
minutes. Check the existing free database's expiry in Render before relying on it
for long-term storage. No billing or paid upgrade is required by this setup guide.
