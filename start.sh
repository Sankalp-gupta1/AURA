#!/bin/bash

gnome-terminal -- bash -c "cd ~/Downloads/life-os-ai/backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000; exec bash"

gnome-terminal -- bash -c "cd ~/Downloads/life-os-ai/frontend && npm run dev; exec bash"

sleep 5

xdg-open http://localhost:3000
