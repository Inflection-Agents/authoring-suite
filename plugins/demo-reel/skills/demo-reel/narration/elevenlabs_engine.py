"""ElevenLabs: speech with character timings, voice listing, and instant voice clones.

Standard library only (urllib), plus ffmpeg to turn the returned MP3 into WAV. The with-timestamps
endpoint returns the audio and a start and end time for every character, so word timings come
straight from the engine and no speech model is needed.
"""
from __future__ import annotations

import base64
import json
import subprocess
import tempfile
import uuid
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.elevenlabs.io"


class ElevenLabsError(RuntimeError):
    pass


def tts_request(text: str, voice_id: str, model_id: str, seed: int | None = None,
                previous_text: str | None = None, next_text: str | None = None) -> tuple[str, dict]:
    """The URL and JSON body for one with-timestamps request."""
    body: dict = {"text": text, "model_id": model_id}
    if seed is not None:
        body["seed"] = seed
    if previous_text:
        body["previous_text"] = previous_text
    if next_text:
        body["next_text"] = next_text
    return f"{API}/v1/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128", body


def multipart(fields: dict[str, str], files: list[Path], field: str = "files") -> tuple[bytes, str]:
    boundary = f"demo-reel-{uuid.uuid4().hex}"
    parts = []
    for name, value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    for f in files:
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{field}"; filename="{f.name}"\r\n'
                     f"Content-Type: application/octet-stream\r\n\r\n".encode() + f.read_bytes() + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def _call(url: str, api_key: str, data: bytes | None = None, content_type: str = "application/json",
          method: str | None = None, opener=urllib.request.urlopen) -> dict:
    if not api_key:
        raise ElevenLabsError("no ELEVENLABS_API_KEY: put it in ~/.config/demo-reel/elevenlabs.env")
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"),
                                 headers={"xi-api-key": api_key, "content-type": content_type,
                                          "accept": "application/json"})
    try:
        with opener(req, timeout=300) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        raise ElevenLabsError(f"ElevenLabs answered {e.code}: {detail}") from None


def mp3_to_wav(mp3: bytes, out_wav: Path) -> None:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(mp3)
        src = f.name
    try:
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ac", "1", "-ar", "24000",
                        "-c:a", "pcm_s16le", str(out_wav)],
                       check=True)
    finally:
        Path(src).unlink(missing_ok=True)


def synth(text: str, out_wav: Path, cfg: dict, seed: int | None = 1234, previous_text: str | None = None,
          next_text: str | None = None, opener=urllib.request.urlopen, decode=mp3_to_wav) -> list[dict]:
    """Voice one scene to out_wav and return its word timings."""
    from textutil import chars_to_words

    if not cfg.get("voice_id"):
        raise ElevenLabsError("no voice: set ELEVENLABS_VOICE_ID, or create one with `narrate.py clone`")
    url, body = tts_request(text, cfg["voice_id"], cfg["model_id"], seed, previous_text, next_text)
    res = _call(url, cfg["api_key"], json.dumps(body).encode(), opener=opener)
    decode(base64.b64decode(res["audio_base64"]), out_wav)
    alignment = res.get("alignment") or res.get("normalized_alignment")
    return chars_to_words(alignment) if alignment else []


def voices(cfg: dict, opener=urllib.request.urlopen) -> list[dict]:
    res = _call(f"{API}/v1/voices", cfg["api_key"], opener=opener)
    return [{"voice_id": v["voice_id"], "name": v.get("name", ""), "category": v.get("category", "")}
            for v in res.get("voices", [])]


def clone(name: str, files: list[Path], cfg: dict, opener=urllib.request.urlopen) -> str:
    """Create an Instant Voice Clone from reference recordings; returns its voice ID."""
    data, ctype = multipart({"name": name, "remove_background_noise": "true"}, files)
    res = _call(f"{API}/v1/voices/add", cfg["api_key"], data, content_type=ctype, opener=opener)
    return res["voice_id"]
