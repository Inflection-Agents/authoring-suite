#!/usr/bin/env bash
# Return the system under demo to a clean state before a take, and clear only that take's events.
# Copy to demo/driver/reset.sh and set the three commands in phase 09.
set -euo pipefail
TAKE=${TAKE:?set TAKE}
STOP_CMD=${STOP_CMD:?set STOP_CMD}
START_CMD=${START_CMD:?set START_CMD}
HEALTH_URL=${HEALTH_URL:?set HEALTH_URL}
eval "$STOP_CMD" || true
eval "$START_CMD"
for _ in $(seq 1 60); do
  curl -fsS "$HEALTH_URL" >/dev/null 2>&1 && break
  sleep 1
done
curl -fsS "$HEALTH_URL" >/dev/null || { echo "reset: system did not come up" >&2; exit 1; }
mkdir -p "demo/takes/$TAKE"
: > "demo/takes/$TAKE/events.jsonl"
echo "reset: $TAKE clean"
