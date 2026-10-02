"""Where the narration engines find their settings and credentials.

The ElevenLabs key lives in ~/.config/demo-reel/elevenlabs.env (chmod 600), outside every repository
and kit. An environment variable of the same name overrides the file. Nothing here ever prints a key.
"""
from __future__ import annotations

import os
from pathlib import Path

ELEVENLABS_FILE = Path.home() / ".config" / "demo-reel" / "elevenlabs.env"


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip().removeprefix("export ").strip()] = value.strip().strip('"').strip("'")
    return values


def elevenlabs(env: dict[str, str] | None = None, path: Path = ELEVENLABS_FILE) -> dict[str, str]:
    """{'api_key', 'voice_id', 'model_id'}; the environment wins over the file."""
    env = dict(os.environ) if env is None else env
    file = read_env_file(path)
    get = lambda k, default="": env.get(k) or file.get(k) or default  # noqa: E731
    return {"api_key": get("ELEVENLABS_API_KEY"), "voice_id": get("ELEVENLABS_VOICE_ID"),
            "model_id": get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")}


def file_is_private(path: Path = ELEVENLABS_FILE) -> bool:
    return path.exists() and (path.stat().st_mode & 0o077) == 0
