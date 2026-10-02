#!/usr/bin/env bash
# One take: reset the system, start the browser recorder, wait until it is recording, run the driver.
#   TAKE=run-1 UI_ROUTE='http://localhost:<UI_PORT>/<route>/{id}' STEP=start bash demo/capture/run-take.sh
set -euo pipefail
TAKE=${TAKE:?set TAKE}
TSX=demo/node_modules/.bin/tsx
bash demo/driver/reset.sh
$TSX demo/capture/browser.ts & REC=$!
for _ in $(seq 1 100); do
  grep -q '"recording-start"' "demo/takes/$TAKE/events.jsonl" 2>/dev/null && break
  sleep 0.2
done
$TSX demo/driver/driver.ts
wait $REC
echo "take $TAKE: demo/takes/$TAKE/events.jsonl, demo/remotion/public/takes/$TAKE/browser.webm"
