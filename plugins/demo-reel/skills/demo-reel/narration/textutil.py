"""Pure text and timing helpers shared by the engines."""
from __future__ import annotations

import re
import unicodedata


def chunk(text: str, max_chars: int = 350) -> list[str]:
    """Split on sentence ends, packing sentences up to max_chars.

    Open models drift on long inputs, so chunking keeps the tenth minute sounding like the first.
    """
    sents = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
    out, cur = [], ""
    for s in sents:
        if not s:
            continue
        if cur and len(cur) + len(s) + 1 > max_chars:
            out.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        out.append(cur)
    return out


def chars_to_words(alignment: dict) -> list[dict]:
    """ElevenLabs' character timings to word timings: a word starts at its first character and ends
    at its last."""
    words, cur, start, end = [], "", None, None
    for ch, s, e in zip(alignment["characters"], alignment["character_start_times_seconds"],
                        alignment["character_end_times_seconds"]):
        if ch.isspace():
            if cur:
                words.append({"word": cur, "start": round(start, 3), "end": round(end, 3)})
            cur, start = "", None
            continue
        if start is None:
            start = s
        cur += ch
        end = e
    if cur:
        words.append({"word": cur, "start": round(start, 3), "end": round(end, 3)})
    return words


def shift(words: list[dict], seconds: float) -> list[dict]:
    return [{**w, "start": round(w["start"] + seconds, 3), "end": round(w["end"] + seconds, 3)} for w in words]


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).lower()
    s = re.sub(r"[^a-z0-9' ]+", " ", s)
    return " ".join(s.split())


def wer(ref: str, hyp: str) -> float:
    """Word error rate of a transcript against the text that was meant to be spoken."""
    r, h = norm(ref).split(), norm(hyp).split()
    if not r:
        return 0.0 if not h else 1.0
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            cur = min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
            prev, d[j] = d[j], cur
    return d[len(h)] / len(r)
