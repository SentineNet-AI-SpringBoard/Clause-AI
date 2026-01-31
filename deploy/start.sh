#!/usr/bin/env bash
set -euo pipefail

# Run FastAPI backend + Streamlit UI in one container.
# Streamlit talks to backend via BACKEND_URL (default points to localhost inside the container).

APP_ROOT="/app"
BACKEND_PORT="${BACKEND_PORT:-8000}"
UI_PORT="${PORT:-8501}"

# Some code paths may write sqlite/db or outputs; ensure directories exist.
mkdir -p "${APP_ROOT}/milestone3/outputs" || true

export BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:${BACKEND_PORT}}"

echo "Starting FastAPI backend on :${BACKEND_PORT} ..."
python -m uvicorn app:app \
  --app-dir "${APP_ROOT}/milestone3/backend" \
  --host 0.0.0.0 \
  --port "${BACKEND_PORT}" \
  --log-level info \
  &

# Small delay to reduce race conditions on cold start.
sleep 0.5

echo "Starting Streamlit UI on :${UI_PORT} ..."
cd "${APP_ROOT}/milestone4/UI/UI"

exec streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port "${UI_PORT}" \
  --server.headless true \
  --browser.gatherUsageStats false
