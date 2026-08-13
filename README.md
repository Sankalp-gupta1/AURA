# AURA – AI Personal Operating System (v2)

> Transforming fragmented digital information into actionable intelligence through AI-powered reasoning, prioritization, and decision support.

This is a rebuilt, production-grade version of the original AURA prototype: real Google OAuth (no more local `token.json` files), GPT-powered analysis with structured JSON outputs, a streaming AI chat assistant, background auto-sync, and a redesigned dashboard.

---

## What changed vs the original prototype

| Area | Before | Now |
|---|---|---|
| Auth | Manual `token.json` file, single hardcoded user | Real Google OAuth2 login, JWT session cookies, multi-user |
| AI provider | Gemini, raw text parsing with `.replace("```json", ...)` | OpenAI GPT with native JSON mode + retries |
| Chat assistant | Blocking, full-response only | Streaming (SSE), renders token-by-token |
| Empty/stub files | `orchestrator.py`, `config.py`, `gmail_service.py` were empty | Fully implemented services, no stubs |
| Sync | Manual only | Manual **and** background auto-sync every 15 min (APScheduler) |
| Data model | Emails/Tasks/Calendar only | + Notes (quick capture), + Calendar event creation, + persisted chat history |
| Error handling | Crashes on missing files/tokens | Global exception handler, per-service try/except with logging |
| Frontend | Single 275-line page, default Next.js styling | Component-based dashboard, custom dark "control room" design system |

---

## Architecture

```
                         ┌────────────────────┐
                         │        USER         │
                         └──────────┬──────────┘
                                    │
                     Google OAuth2 (Gmail + Calendar)
                                    │
                         ┌──────────▼──────────┐
                         │   Next.js Frontend    │
                         │  Dashboard · Ask Aura │
                         └──────────┬──────────┘
                                    │ REST + SSE
                         ┌──────────▼──────────┐
                         │   FastAPI Backend     │
                         │  Auth · Sync · Ask    │
                         └───┬─────────┬────────┘
                             │         │
                  ┌──────────▼───┐ ┌───▼───────────┐
                  │ Gmail / Cal.  │ │   OpenAI GPT   │
                  │  Google APIs  │ │ JSON + Stream  │
                  └──────────┬───┘ └───┬────────────┘
                             │         │
                         ┌───▼─────────▼───┐
                         │  SQLite (SQLAlchemy) │
                         │ Users·Emails·Tasks·   │
                         │ Events·Notes·Chat     │
                         └───────────────────────┘
```

Background scheduler (`APScheduler`) re-syncs every connected user on an interval so the
dashboard stays fresh without the user manually clicking "Sync".

---

## Features

- **Gmail Intelligence** — every synced email gets an AI category (security / job / deadline / personal / newsletter / spam), priority, and one-line summary.
- **Automated Task Extraction** — GPT reads new emails and creates structured tasks (title, priority, deadline) automatically, linked back to the source email.
- **AI Chief-of-Staff Briefing** — a daily summary generated from your live tasks, emails, and calendar (cached until you sync again or force-regenerate).
- **Ask Aura** — a streaming chat assistant that answers questions using only your synced data, with conversation memory.
- **Calendar Awareness + Creation** — see upcoming events and create new ones directly on your Google Calendar from the dashboard.
- **Quick Notes** — jot things down for Aura to include as context in chat answers.
- **Multi-user, real OAuth** — anyone can sign in with their own Google account; tokens are refreshed automatically.

---

## Tech Stack

**Frontend:** Next.js 15, React 19, TypeScript, Tailwind CSS v4, lucide-react
**Backend:** FastAPI, SQLAlchemy, APScheduler, Pydantic Settings
**AI:** OpenAI GPT (`gpt-4o-mini` by default, configurable)
**Auth:** Google OAuth 2.0 + JWT session cookies
**Integrations:** Gmail API, Google Calendar API
**Database:** SQLite (swap `DATABASE_URL` for Postgres/MySQL in production — SQLAlchemy handles both)

---

## Setup

### 1. Get your API keys

**OpenAI key** — [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

**Google OAuth credentials** — [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
1. Create a project → Enable **Gmail API** and **Google Calendar API**.
2. Configure the OAuth consent screen (External is fine for personal use; add your own email as a test user).
3. Create credentials → OAuth client ID → Application type **Web application**.
4. Authorized redirect URI: `http://localhost:8000/api/auth/google/callback`

### 2. Configure environment variables

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

Open `backend/.env` and paste in:
- `OPENAI_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- Generate `SECRET_KEY` with `openssl rand -hex 32`

### 3. Run it

```bash
./start.sh
```

This sets up a Python venv, installs backend deps, installs frontend deps, and starts both:
- Backend → http://localhost:8000/docs (interactive API docs)
- Frontend → http://localhost:3000

Or run each manually:

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
AURA/
├── backend/
│   └── app/
│       ├── api/        # Route handlers (auth, emails, tasks, calendar, dashboard, ask, notes)
│       ├── core/        # Config, security (JWT), logging
│       ├── db/          # SQLAlchemy engine/session
│       ├── models/      # ORM models
│       ├── schemas/     # Pydantic request/response schemas
│       ├── services/    # Gmail, Calendar, Google OAuth, OpenAI, sync orchestration
│       └── tasks/       # Background auto-sync scheduler
└── frontend/
    ├── app/              # Next.js App Router pages
    ├── components/       # Dashboard widgets (TopBar, BriefingPanel, TaskBoard, AskAura, ...)
    └── lib/              # Typed API client
```

---

## Roadmap — Future Research Directions

Future versions of AURA will focus on expanding the platform into a fully autonomous Personal AI Operating System. Planned enhancements include:

- Long-Term Memory Architecture
- Multi-Agent Collaboration Framework
- WhatsApp Integration
- LinkedIn Integration
- Voice-Based Interaction
- Personalized Recommendation Engine
- Autonomous Task Execution
- Meeting Scheduling Automation
- Cross-Platform Knowledge Graph
- Behavioral Learning Models

The long-term vision is to evolve AURA from an intelligent assistant into a proactive digital partner capable of understanding, planning, and executing tasks on behalf of users.

---

## Security Notes

- OAuth tokens are stored in the local SQLite database for simplicity. For any real deployment, encrypt them at rest (e.g. `cryptography.Fernet`) before storing.
- `SECRET_KEY` must be a real random secret in production — never reuse the example value.
- Session cookies are `httponly` and marked `secure` automatically outside `ENVIRONMENT=development`.
- Add rate limiting (e.g. `slowapi`) in front of `/api/ask` before exposing this publicly — OpenAI calls cost money per request.
