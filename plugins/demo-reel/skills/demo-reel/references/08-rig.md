# 08 Rig

**Goal.** Install every tool next to the code and prove the whole chain works before writing the driver.
**Produces.** A working `demo/.venv`, `demo/node_modules`, `demo/remotion`, and a narration engine if one is used.
**Gate.** The fixture render and the toy proof both pass.

Run everything from the code repository's root. `<skill>` is the folder holding this skill's `SKILL.md`.

## Install

```bash
# Python, the way voice-lab does it
uv venv --python 3.12 demo/.venv
uv pip install --python demo/.venv/bin/python -r <skill>/scripts/requirements.txt

# capture tools: an ES-module package with pinned tsx and playwright
cp <skill>/templates/package.json demo/
npm install --prefix demo
demo/node_modules/.bin/playwright install chromium      # on Linux, also: install-deps chromium

# the Remotion starter
rsync -a --exclude node_modules <skill>/remotion/ demo/remotion/
(cd demo/remotion && npm ci)

# narration, optional
bash <skill>/narration/install.sh qwen         # local cloned voice, Apple silicon
bash <skill>/narration/install.sh elevenlabs   # cloud voice, key in ~/.config/demo-reel/elevenlabs.env
```

ffmpeg and `uv` come from the system package manager (`brew install ffmpeg uv` on macOS). `install.sh` installs `uv`
itself if it is missing.

## Prove it

```bash
REMOTION_DIR=demo/remotion demo/.venv/bin/python <skill>/scripts/test_fixture_render.py
bash <skill>/examples/toy/prove.sh /tmp/demo-reel-prove
```

The first renders a fixture through the real pipeline. The second starts a toy server on port 8080, records two takes
with the browser recorder, checks they normalize identically, and renders a three-pane shot. Both must pass. When port
8080 is in use, stop what holds it for the length of the proof.

From here on, run every Python script with `demo/.venv/bin/python`.

## Leaving the phase

Record the tool versions in the ledger, then write the driver ([09](09-driver.md)).
