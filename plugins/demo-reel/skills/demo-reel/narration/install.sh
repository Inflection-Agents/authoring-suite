#!/usr/bin/env bash
# Optional narration engines for demo-reel. Run from the code repository's root.
#   bash <skill>/narration/install.sh qwen        # local cloned voice, Apple silicon
#   bash <skill>/narration/install.sh elevenlabs  # cloud voice, any machine
# Both use the engagement's environment at demo/.venv, created with uv the way voice-lab does.
set -euo pipefail
ENGINE=${1:?usage: install.sh qwen|elevenlabs}
HERE=$(cd "$(dirname "$0")" && pwd)
VENV=${VENV:-demo/.venv}

need() { command -v "$1" >/dev/null || { echo "install.sh: $1 is required: $2" >&2; exit 1; }; }
need ffmpeg "brew install ffmpeg (macOS) or apt-get install ffmpeg"
if ! command -v uv >/dev/null; then
  echo "installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
[ -x "$VENV/bin/python" ] || uv venv --python 3.12 "$VENV"
uv pip install --python "$VENV/bin/python" -r "$HERE/../scripts/requirements.txt"

case "$ENGINE" in
  qwen)
    [ "$(uname -s)-$(uname -m)" = "Darwin-arm64" ] || { echo "qwen runs through MLX, which needs Apple silicon; use elevenlabs here" >&2; exit 1; }
    uv pip install --python "$VENV/bin/python" -r "$HERE/requirements-qwen.txt"
    echo "downloading the Qwen3-TTS and Whisper models (about 3.5 GB the first time)"
    "$VENV/bin/python" - <<'PY'
from huggingface_hub import snapshot_download
for repo in ("mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit", "mlx-community/whisper-large-v3-turbo"):
    snapshot_download(repo)
    print(f"  {repo}")
PY
    if [ -n "${REF:-}" ] && [ -n "${REF_TEXT:-}" ]; then
      SMOKE=$(mktemp -d)
      printf '## S1 Smoke\nThis is a test of the narration engine.\n' > "$SMOKE/script.md"
      "$VENV/bin/python" "$HERE/narrate.py" voice --engine qwen --script "$SMOKE/script.md" --out "$SMOKE" --ref "$REF" --ref-text "$REF_TEXT"
      echo "qwen ready: listen to $SMOKE/S1.wav"
    else
      echo "qwen installed. To voice a test sentence: REF=<ref.wav> REF_TEXT=<ref.txt> bash $0 qwen"
    fi
    ;;
  elevenlabs)
    "$VENV/bin/python" "$HERE/narrate.py" check-key
    ;;
  *) echo "usage: install.sh qwen|elevenlabs" >&2; exit 2 ;;
esac
