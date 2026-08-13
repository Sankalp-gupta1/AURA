#!/usr/bin/env bash
# Starts backend (FastAPI) and frontend (Next.js) together for local development.
set -e
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Setting up backend..."
cd "$ROOT_DIR/backend"
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "!! backend/.env created from template — add your OPENAI_API_KEY and Google OAuth keys before continuing."
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd "$ROOT_DIR"

echo "==> Setting up frontend..."
cd "$ROOT_DIR/frontend"
if [ ! -f ".env.local" ]; then
  cp .env.example .env.local
fi
if [ ! -d "node_modules" ]; then
  npm install
fi
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
echo ""
echo "AURA is starting:"
echo "  Backend  -> http://localhost:8000/docs"
echo "  Frontend -> http://localhost:3000"
wait
