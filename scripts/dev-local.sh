#!/usr/bin/env bash
# Run backend + frontend locally when Docker isn't available (or for debugging).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export DATABASE_PATH="${DATABASE_PATH:-$ROOT/data/app.db}"
export PROFILE_PATH="${PROFILE_PATH:-$ROOT/data/buyer_style_profile.yaml}"
export FAKE_FIXTURE_PATH="${FAKE_FIXTURE_PATH:-$ROOT/backend/app/adapters/sources/fixtures/fake_listings.json}"

if [[ ! -f "$PROFILE_PATH" ]]; then
  echo "Missing profile at $PROFILE_PATH — copy from templates or ensure data/ is populated." >&2
  exit 1
fi

BACK_PY="$ROOT/backend/.venv/bin/python"
BACK_PIP="$ROOT/backend/.venv/bin/pip"
BACK_UVICORN="$ROOT/backend/.venv/bin/uvicorn"

if [[ ! -x "$BACK_UVICORN" ]]; then
  echo "Creating backend venv and installing dependencies…"
  python3 -m venv "$ROOT/backend/.venv"
  (cd "$ROOT/backend" && "$ROOT/backend/.venv/bin/pip" install -q -e ".[dev]")
fi

cleanup() {
  [[ -n "${BACK_PID:-}" ]] && kill "$BACK_PID" 2>/dev/null || true
  [[ -n "${FRONT_PID:-}" ]] && kill "$FRONT_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting API at http://127.0.0.1:8000 (health: /health)"
(
  cd "$ROOT/backend"
  PYTHONPATH=. exec "$BACK_UVICORN" app.main:app --host 127.0.0.1 --port 8000
) &
BACK_PID=$!

echo "Waiting for backend…"
for _ in $(seq 1 40); do
  if curl -sf "http://127.0.0.1:8000/health" >/dev/null; then
    break
  fi
  sleep 0.25
done
if ! curl -sf "http://127.0.0.1:8000/health" >/dev/null; then
  echo "Backend failed to start." >&2
  exit 1
fi

export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"
echo "Starting UI at http://127.0.0.1:3000"
(
  cd "$ROOT/frontend"
  exec npm run dev -- --hostname 127.0.0.1 --port 3000
) &
FRONT_PID=$!

echo ""
echo "Open http://localhost:3000 — click \"Run fake source\" to load fixtures."
echo "Press Ctrl+C to stop both servers."
wait "$FRONT_PID"
