#!/usr/bin/env python3
"""Turn [cue:...] markers in a voiceover script into seconds in the narration audio.

The voiceover is the clock of the whole video. A recognizer returns word timestamps for the audio;
this module lines those words up with the script's words and reads off where each cue landed, and
where each sentence starts (for captions). A word the recognizer missed gets a start time halfway
between the end of the word before it and the start of the word after it.

Usage, to write one narration text file per scene for the narration engine:
    python3 cues.py demo/script.md demo/voice
"""
from __future__ import annotations

import difflib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from verify_shots import CUE_RE, HEADING_RE, HOLD_RE, SCENE_ID_RE

WORD_RE = re.compile(r"[a-z0-9']+")
SPLIT_RE = re.compile(r"(\[cue:[^\]]*\])")


@dataclass
class Scene:
    id: str
    title: str
    text: str = ""
    cues: list[tuple[str, int]] = field(default_factory=list)
    sentences: list[tuple[str, int]] = field(default_factory=list)
    holds: list[tuple[float, int]] = field(default_factory=list)


def _norm(w: str) -> str:
    return "".join(WORD_RE.findall(w.lower()))


def parse_script(text: str) -> list[Scene]:
    scenes: list[Scene] = []
    words: list[str] = []
    active = False  # False after a heading without a scene id, so its words go nowhere

    def close():
        if scenes and active:
            scenes[-1].text = " ".join(words)
            scenes[-1].sentences = _sentences(words)

    for line in text.splitlines():
        h = HEADING_RE.match(line)
        if h:
            m = SCENE_ID_RE.match(h.group("rest").strip())
            close()
            words = []
            active = bool(m)
            if m:
                scenes.append(Scene(m.group("id"), (m.group("title") or "").strip()))
            continue
        if active and HOLD_RE.match(line):
            scenes[-1].holds.append((float(HOLD_RE.match(line).group("seconds")), len(words)))
            continue
        if not active or line.lstrip().startswith(">") or not line.strip():
            continue
        for part in SPLIT_RE.split(line):
            c = CUE_RE.fullmatch(part)
            if c:
                scenes[-1].cues.append((c.group(1), len(words)))
            else:
                words.extend(part.split())
    close()
    return scenes


def _sentences(words: list[str]) -> list[tuple[str, int]]:
    out, start = [], 0
    for i, w in enumerate(words):
        if w.endswith((".", "?", "!")):
            out.append((" ".join(words[start:i + 1]), start))
            start = i + 1
    if start < len(words):
        out.append((" ".join(words[start:]), start))
    return out


def _word_times(script_words, heard):
    ref = [_norm(w) for w in script_words]
    hyp = [_norm(w) for w, _, _ in heard]
    starts: list = [None] * len(ref)
    ends: list = [None] * len(ref)
    sm = difflib.SequenceMatcher(a=ref, b=hyp, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("equal", "replace") and (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                starts[i1 + k] = heard[j1 + k][1]
                ends[i1 + k] = heard[j1 + k][2]
    for i, s in enumerate(starts):
        if s is None:
            prev_end = next((ends[j] for j in range(i - 1, -1, -1) if ends[j] is not None), 0.0)
            next_start = next((starts[j] for j in range(i + 1, len(starts)) if starts[j] is not None), prev_end)
            starts[i] = (prev_end + next_start) / 2
    return starts, ends


def times_at(scene: Scene, heard: list[tuple[str, float, float]], positions: list[int]) -> list[float]:
    """Seconds at which each word position starts; a position past the last word is the last word's end."""
    words = scene.text.split()
    starts, ends = _word_times(words, heard)
    last_end = next((e for e in reversed(ends) if e is not None), heard[-1][2] if heard else 0.0)
    return [round(starts[n], 3) if n < len(words) else round(last_end, 3) for n in positions]


def cue_times(scene: Scene, heard: list[tuple[str, float, float]]) -> dict[str, float]:
    return dict(zip([c for c, _ in scene.cues], times_at(scene, heard, [n for _, n in scene.cues])))


def sentence_times(scene: Scene, heard: list[tuple[str, float, float]]) -> list[dict]:
    starts = times_at(scene, heard, [n for _, n in scene.sentences])
    return [{"text": t, "start": s} for (t, _), s in zip(scene.sentences, starts)]


def main(argv: list[str]) -> int:
    src, out_dir = Path(argv[1]), Path(argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    for s in parse_script(src.read_text()):
        (out_dir / f"{s.id}.txt").write_text(s.text + "\n")
        print(f"{s.id}: {len(s.text.split())} words")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
