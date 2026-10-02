#!/usr/bin/env bash
# Prove the capture chain on a toy system: two takes with the browser recorder, the determinism gate,
# and a three-pane render built from the first take.
#   bash <skill>/examples/toy/prove.sh [work-dir]
# Needs Node 22, Python 3 with PyYAML, ffmpeg, and network access for npm. Uses port 8080.
set -euo pipefail
SKILL=$(cd "$(dirname "$0")/../.." && pwd)
WORK=${1:-$(mktemp -d)}
mkdir -p "$WORK/demo/driver" "$WORK/demo/capture"
cd "$WORK"

cp "$SKILL/templates/package.json" demo/
cp "$SKILL/templates/driver/reset.sh" demo/driver/
cp "$SKILL/templates/capture/browser.ts" "$SKILL/templates/capture/run-take.sh" demo/capture/
python3 - "$SKILL" <<'PY'
import sys
skill = sys.argv[1]
src = open(f"{skill}/templates/driver/driver.ts").read()
steps = open(f"{skill}/examples/toy/steps.ts").read().split("\n", 1)[1]
marker = "const SCENARIOS: Record<string, Step[]> = {};\n"
assert marker in src, "driver template changed; update prove.sh"
open("demo/driver/driver.ts", "w").write(src.replace(marker, "const state: {id?: string} = {};\n" + steps))
PY
rsync -a --exclude node_modules --exclude out "$SKILL/remotion/" demo/remotion/
npm install --prefix demo --no-audit --no-fund >/dev/null
demo/node_modules/.bin/playwright install chromium >/dev/null
(cd demo/remotion && npm ci --no-audit --no-fund >/dev/null)

export STOP_CMD="pkill -f 'node $SKILL/examples/toy/server.mjs'"
export START_CMD="nohup node $SKILL/examples/toy/server.mjs >/dev/null 2>&1 &"
export HEALTH_URL=http://localhost:8080/health UI_ROUTE='http://localhost:8080/ui/{id}' SCENARIO=toy
trap 'eval "$STOP_CMD" || true' EXIT
TAKE=run-1 bash demo/capture/run-take.sh
TAKE=run-2 bash demo/capture/run-take.sh

python3 "$SKILL/scripts/normalize_events.py" demo/takes/run-1/events.jsonl > demo/run-1.norm
python3 "$SKILL/scripts/normalize_events.py" demo/takes/run-2/events.jsonl > demo/run-2.norm
diff demo/run-1.norm demo/run-2.norm && echo "determinism: the two takes are identical"

cp "$SKILL/examples/toy/script.md" "$SKILL/examples/toy/shots.yaml" "$SKILL/examples/toy/timing.json" demo/
python3 "$SKILL/scripts/verify_shots.py" demo/shots.yaml demo/script.md
python3 "$SKILL/scripts/build_props.py" demo/shots.yaml demo/timing.json demo/takes toy demo/remotion/props-toy.json
mkdir -p demo/remotion/public/voice
ffmpeg -loglevel error -y -f lavfi -i anullsrc=r=24000:cl=mono -t 4 demo/remotion/public/voice/T1.wav
(cd demo/remotion && npx remotion render src/index.ts Cut out/toy.mp4 --props=props-toy.json >/dev/null)
echo "toy proven: $WORK/demo/remotion/out/toy.mp4"
