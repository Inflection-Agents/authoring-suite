#!/usr/bin/env python3
"""Holds: silence inserted into a scene's narration where the picture needs time to land.

A `> hold: 3s` line in the script sits between sentences. After a scene is voiced, the silence is
inserted into its WAV at that point and every later word's timing moves by the same number of seconds, so the
cues stay on their words. It runs after either engine, on 16-bit PCM WAV, with the standard library.
"""
from __future__ import annotations

import wave
from pathlib import Path


def apply_holds(words: list[dict], holds: list[tuple[float, int]], duration: float,
                script_words: list[str] | None = None):
    """(words with later timings shifted, [(time in the original audio, seconds)]).

    A hold before script word n sits at the end of script word n - 1; a hold after the last word sits
    at the end of the audio. `words` are the words as heard. A transcript can differ from the script
    (Whisper writes "three hundred and twelve" as 312), so with `script_words` each hold is placed
    through the same alignment that times the cues, not by counting heard words.
    """
    if script_words is None:
        ends = [w["end"] for w in words]
        n_words = len(words)
    else:
        from cues import _word_times

        starts, ends = _word_times(script_words, [(w["word"], w["start"], w["end"]) for w in words])
        ends = [e if e is not None else s for s, e in zip(starts, ends)]
        n_words = len(script_words)
    inserts = []
    for seconds, n in holds:
        if n >= n_words:
            at = duration
        elif n == 0:
            at = 0.0
        else:
            at = ends[n - 1]
        inserts.append((round(at, 3), seconds))
    shifted = []
    for w in words:
        delay = sum(s for at, s in inserts if w["start"] >= at)
        shifted.append({**w, "start": round(w["start"] + delay, 3), "end": round(w["end"] + delay, 3)})
    return shifted, inserts


def insert_silence(src: Path, dst: Path, inserts: list[tuple[float, float]]) -> None:
    with wave.open(str(src), "rb") as r:
        params = r.getparams()
        data = r.readframes(r.getnframes())
    width = params.sampwidth * params.nchannels
    out, pos = [], 0
    for at, seconds in sorted(inserts):
        cut = min(len(data), round(at * params.framerate) * width)
        out += [data[pos:cut], b"\x00" * (round(seconds * params.framerate) * width)]
        pos = cut
    out.append(data[pos:])
    with wave.open(str(dst), "wb") as w:
        w.setparams(params)
        w.writeframes(b"".join(out))
