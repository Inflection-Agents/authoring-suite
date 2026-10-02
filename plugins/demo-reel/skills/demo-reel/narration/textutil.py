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


_ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
         "seventeen eighteen nineteen").split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
_NUMBER_WORDS = set(_ONES) | set(_TENS) | {"hundred", "thousand"}


def spell(n: int) -> str:
    """0 to 999,999 in words, without "and": 312 is "three hundred twelve"."""
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else " " + _ONES[n % 10])
    if n < 1000:
        return _ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + spell(n % 100))
    return spell(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + spell(n % 1000))


def _spoken(tokens: list[str]) -> list[str]:
    """Whisper writes "three hundred and twelve" as 312, so both sides spell numbers out and drop the "and"
    inside a number before they are compared."""
    out: list[str] = []
    for t in tokens:
        out.extend(spell(int(t)).split() if t.isdigit() and int(t) < 10**6 else [t])
    return [t for i, t in enumerate(out)
            if not (t == "and" and 0 < i < len(out) - 1 and out[i - 1] in _NUMBER_WORDS and out[i + 1] in _NUMBER_WORDS)]


def wer(ref: str, hyp: str) -> float:
    """Word error rate of a transcript against the text that was meant to be spoken."""
    r, h = _spoken(norm(ref).split()), _spoken(norm(hyp).split())
    if not r:
        return 0.0 if not h else 1.0
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            cur = min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
            prev, d[j] = d[j], cur
    return d[len(h)] / len(r)


def sentence_cut(words: list[dict], window: float, pad: float = 0.2) -> tuple[float, int] | None:
    """Where to cut a long reference recording so it ends on a complete sentence.

    Returns (seconds to keep, sentences kept): the end of the last sentence-ending word inside the
    window, plus a short pad. None when no sentence ends inside the window.
    """
    cut, sentences, count = None, 0, 0
    for w in words:
        if w["word"].rstrip("\"'").endswith((".", "!", "?")):
            count += 1
            if w["end"] <= window:
                cut, sentences = w["end"], count
    return (round(cut + pad, 3), sentences) if cut is not None else None


def first_sentences(text: str, n: int) -> str:
    return " ".join(re.split(r"(?<=[.!?])\s+", " ".join(text.split()))[:n])
