#!/usr/bin/env python3
"""Check that each cut's scene titles read as one argument, with narrative-spine's checker.

narrative-spine's `spine-check.mjs` reads a spine file (`### n label` blocks with a `- **Title:**` line).
This writes one such file per cut from narrative.md's scene tables, following "(as in ...)" rows back
to the scene's title, so the checker can read each cut top to bottom.

Usage:
    python3 spine_titles.py demo/narrative.md /tmp/spine
    node <narrative-spine skill>/scripts/spine-check.mjs /tmp/spine/<cut>.md

For a video, ignore the checker's "no kicker" and "no Ask beat" warnings: scenes have no kickers and a
demo makes no ask. Fix every orphan warning; it means a title has no connective to the one before it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CUT_RE = re.compile(r"^##\s+(?P<name>\w+)\s+cut\b", re.I)
ROW_RE = re.compile(r"^\|\s*(?P<id>[A-Za-z]+\d+)\s*\|[^|]*\|\s*(?P<title>[^|]+?)\s*\|")


def cut_titles(text: str) -> dict[str, list[tuple[str, str]]]:
    cuts: dict[str, list[tuple[str, str]]] = {}
    known: dict[str, str] = {}
    cut = None
    for line in text.splitlines():
        m = CUT_RE.match(line)
        if m:
            cut = m.group("name").lower()
            cuts[cut] = []
            continue
        r = ROW_RE.match(line)
        if cut and r:
            sid, title = r.group("id"), r.group("title")
            if title.startswith("(as in"):
                title = known.get(sid, title)
            else:
                known[sid] = title
            cuts[cut].append((sid, title))
    return cuts


def spine(cut: str, rows: list[tuple[str, str]]) -> str:
    blocks = [f"### {i} {sid}\n- **Title:** {title}\n" for i, (sid, title) in enumerate(rows, 1)]
    return f"# Spine: {cut} cut\n\n" + "\n".join(blocks)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: spine_titles.py demo/narrative.md out-dir", file=sys.stderr)
        return 2
    out = Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for cut, rows in cut_titles(Path(argv[1]).read_text()).items():
        (out / f"{cut}.md").write_text(spine(cut, rows))
        print(f"{out / f'{cut}.md'}: {len(rows)} scenes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
