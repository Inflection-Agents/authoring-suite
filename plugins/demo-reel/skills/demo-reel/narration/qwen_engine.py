"""Qwen3-TTS 1.7B Base through mlx-audio, extracted from voice-lab.

Apple silicon only. The tuning comes from voice-lab's measurements:
- A reference longer than 30 s costs time without improving the clone (73 s ran at 2.9x real time
  against 0.9x for the same voice trimmed to 30 s), and one shorter than about 10 s can send the model
  into a runaway generation. So a long reference is trimmed to the last complete sentence inside its
  first 30 s.
- Qwen aligns the reference transcript against the reference audio, so the transcript keeps exactly
  the sentences the trimmed audio keeps; a mismatched pair, or one cut mid-sentence, degrades the clone.
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


_REF_CACHE: dict = {}


def prepare_reference(path: str, ref_text: str, window_s: float = REF_WINDOW_S) -> tuple[str, str]:
    """(reference audio, its transcript), trimmed to end on a complete sentence inside the window.

    A reference cut mid-sentence makes Qwen speak its last word before every line, so a long
    recording is cut at the end of the last sentence it completes inside the first 30 seconds,
    found with Whisper's word timings, and the transcript keeps the same number of sentences.
    """
    import numpy as np
    import soundfile as sf

    import asr
    from textutil import first_sentences, sentence_cut

    if sf.info(path).duration <= window_s + 1.0:
        return path, ref_text
    key = (path, ref_text, window_s)
    if key not in _REF_CACHE:
        cut = sentence_cut(asr.words_from_file(path), window_s)
        if cut is None:
            raise ValueError(f"{path} runs past {window_s:g} s and no sentence ends inside them; "
                             "record a reference of about 30 s that ends on a complete sentence")
        seconds, sentences = cut
        a, sr = sf.read(path)
        a = np.asarray(a, np.float32)
        if a.ndim > 1:
            a = a.mean(axis=1)
        out = Path(tempfile.gettempdir()) / f"demo-reel-ref-{abs(hash(key)) % 10**10}.wav"
        sf.write(out, a[: int(seconds * sr)], sr)
        _REF_CACHE[key] = (str(out), first_sentences(ref_text, sentences))
    return _REF_CACHE[key]


def model():
    global _MODEL
    if _MODEL is None:
        from mlx_audio.tts.utils import load_model
        _MODEL = load_model(REPO)
    return _MODEL


def synth(text: str, ref_audio: str, ref_text: str):
    """(audio as float32 numpy array, sample rate) for one chunk of text in the reference voice."""
    import numpy as np

    ref_audio, ref_text = prepare_reference(ref_audio, ref_text)
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
