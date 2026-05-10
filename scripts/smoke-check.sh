#!/usr/bin/env bash
# Quick verification that the API matches Phase 1 acceptance (no UI).
set -euo pipefail
BASE="${API_BASE:-http://127.0.0.1:8000}"
echo "Checking $BASE/health …"
curl -sf "$BASE/health" | grep -q ok
echo "Running fake source …"
curl -sf -X POST "$BASE/api/sources/fake/run" | grep -q '"status":"success"'
echo "Fetching default feed …"
FEED="$(curl -sf "$BASE/api/feed")"
echo "$FEED" | grep -q '"verdict":"click_now"\|"verdict":"maybe"'
echo "Fetching profile …"
curl -sf "$BASE/api/profile" | grep -q 'yaml'
echo "OK — API smoke checks passed."
