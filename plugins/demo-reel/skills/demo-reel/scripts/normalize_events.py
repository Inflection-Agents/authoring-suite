#!/usr/bin/env python3
"""Reduce a take's event log to what must be identical between two runs of the same scenario.

Times and wall clocks always differ, and so do the IDs the system under demo issues. Each ID the
driver logged in an `invocation` event is replaced, wherever it appears (response bodies, URL paths),
by a placeholder numbered in order of first appearance. What is left must match run for run, or the
demo is not deterministic.

Usage:
    python3 normalize_events.py demo/takes/run-1/events.jsonl > /tmp/run-1a.txt
    diff /tmp/run-1a.txt /tmp/run-1b.txt   # empty means deterministic
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DROP = {"t", "wall", "take"}


def _replace(v, ids: dict[str, str]):
    if isinstance(v, str):
        for real, ph in ids.items():
            v = v.replace(real, ph)
        return v
    if isinstance(v, list):
        return [_replace(x, ids) for x in v]
    if isinstance(v, dict):
        return {k: _replace(x, ids) for k, x in v.items()}
    return v


def normalize(events: list[dict]) -> list[str]:
    ids: dict[str, str] = {}
    for e in events:
        if e.get("kind") == "invocation" and str(e.get("id")) not in ids:
            ids[str(e["id"])] = f"<id-{len(ids) + 1}>"
    out = []
    for e in events:
        if e.get("kind") == "recording-start":
            continue  # written by a recorder, not by the scenario
        kept = {k: v for k, v in e.items() if k not in DROP}
        out.append(json.dumps(_replace(kept, ids), sort_keys=True))
    return out


def main(argv: list[str]) -> int:
    events = [json.loads(l) for l in Path(argv[1]).read_text().splitlines() if l.strip()]
    print("\n".join(normalize(events)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
