"""A pronunciation lexicon applied in front of any engine.

`demo/lexicon.json` maps a word to {"respell": "..."} (an "ipa" field may sit beside it for the
record). The respelling replaces whole words only, case-sensitively, so "SLA" changes and "SLAs"
does not unless the lexicon lists it.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


def load(path: Path | None) -> dict[str, str]:
    if not path or not Path(path).exists():
        return {}
    raw = json.loads(Path(path).read_text())
    return {w: v["respell"] for w, v in raw.items() if isinstance(v, dict) and v.get("respell")}


def apply(text: str, lexicon: dict[str, str]) -> str:
    for word in sorted(lexicon, key=len, reverse=True):
        text = re.sub(rf"(?<![\w-]){re.escape(word)}(?![\w-])", lexicon[word], text)
    return text
