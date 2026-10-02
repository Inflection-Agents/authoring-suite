#!/usr/bin/env python3
"""Write an SRT caption file for one cut, one caption per spoken sentence.

Sentence start times come from timing.json (written by timing.py); scene order and lengths come
from the cut's props file, so the captions follow the same clock as the video.

Usage:
    python3 captions.py demo/timing.json demo/remotion/props-<cut>.json demo/out/<cut>.srt
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _ts(seconds: float) -> str:
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def srt(timing: dict, props: dict) -> str:
    fps = props["fps"]
    blocks, offset, n = [], 0.0, 1
    for scene in props["scenes"]:
        length = scene["durationInFrames"] / fps
        sentences = timing[scene["id"]].get("sentences", [])
        for i, s in enumerate(sentences):
            end = sentences[i + 1]["start"] if i + 1 < len(sentences) else length
            blocks.append(f"{n}\n{_ts(offset + s['start'])} --> {_ts(offset + end)}\n{s['text']}\n")
            n += 1
        offset += length
    return "\n".join(blocks)


def main(argv: list[str]) -> int:
    timing = json.loads(Path(argv[1]).read_text())
    props = json.loads(Path(argv[2]).read_text())
    Path(argv[3]).write_text(srt(timing, props))
    print(f"captions -> {argv[3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
