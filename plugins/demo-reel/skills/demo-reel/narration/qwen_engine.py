"""Qwen3-TTS 1.7B Base through mlx-audio, extracted from voice-lab.

Apple silicon only. The tuning comes from voice-lab's measurements:
- A reference longer than 30 s costs time without improving the clone (73 s ran at 2.9x real time
  against 0.9x for the same voice trimmed to 30 s), and one shorter than about 10 s can send the model
  into a runaway generation. So a long reference is trimmed to its first 30 s.
- Qwen aligns the reference transcript against the reference audio, so the transcript is trimmed in
  proportion to the audio; a mismatched pair degrades the clone badly.
- The runaway guard budgets 11 tokens a word (honest speech costs about 5), floor 90.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

REPO = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"
REF_WINDOW_S = 30.0
_MODEL = None


def est_tokens(text: str, per_word: int = 11, floor: int = 90) -> int:
    return max(floor, int(len(text.split()) * per_word))


def prepare_ref(path: str, window_s: float = REF_WINDOW_S) -> str:
    import numpy as np
    import soundfile as sf

    info = sf.info(path)
    if info.duration <= window_s + 1.0:
        return path
    a, sr = sf.read(path)
    a = np.asarray(a, np.float32)
    if a.ndim > 1:
        a = a.mean(axis=1)
    out = Path(tempfile.gettempdir()) / f"demo-reel-ref-{abs(hash((path, window_s))) % 10**10}.wav"
    sf.write(out, a[: int(window_s * sr)], sr)
    return str(out)


def trim_ref_text(ref_text: str, path: str, window_s: float = REF_WINDOW_S) -> str:
    import soundfile as sf

    dur = sf.info(path).duration
    if dur <= window_s + 1.0:
        return ref_text
    w = ref_text.split()
    return " ".join(w[: max(6, int(len(w) * window_s / dur))])


def model():
    global _MODEL
    if _MODEL is None:
        from mlx_audio.tts.utils import load_model
        _MODEL = load_model(REPO)
    return _MODEL


def synth(text: str, ref_audio: str, ref_text: str):
    """(audio as float32 numpy array, sample rate) for one chunk of text in the reference voice."""
    import numpy as np

    ref_text = trim_ref_text(ref_text, ref_audio)
    ref_audio = prepare_ref(ref_audio)
    pieces, sr = [], 24000
    for r in model().generate(text=text, ref_audio=ref_audio, ref_text=ref_text, verbose=False,
                              max_tokens=est_tokens(text)):
        pieces.append(np.asarray(r.audio, dtype=np.float32).reshape(-1))
        sr = getattr(r, "sample_rate", sr) or sr
    return (np.concatenate(pieces) if pieces else np.zeros(0, np.float32)), sr


def crossfade(a, b, sr: int, ms: int = 25):
    """Join two pieces with a short equal-power fade; returns (joined, samples of overlap)."""
    import numpy as np

    n = min(int(sr * ms / 1000), len(a), len(b))
    if n < 16:
        return np.concatenate([a, b]), 0
    t = np.linspace(0, np.pi / 2, n, dtype=np.float32)
    return np.concatenate([a[:-n], a[-n:] * np.cos(t) + b[:n] * np.sin(t), b[n:]]), n
