#!/usr/bin/env python3
"""Check a demo-reel shot list against its voiceover script before anything is captured.

A shot list is wrong long before a frame renders: a cue the narration lands on with nothing to show,
a shot filed under a scene that was renamed, a cue id with a typo that would be read aloud, a cut
that runs twice its target. Each of those is cheap to fix here and expensive after capture.

Usage:
    python3 verify_shots.py demo/shots.yaml demo/script.md
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CUE_RE = re.compile(r"\[cue:([^\]]*)\]")
CUE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEADING_RE = re.compile(r"^##\s+(?P<rest>.*)$")
SCENE_ID_RE = re.compile(r"^(?P<id>[A-Za-z]+\d+)(?:\s+(?P<title>.*))?$")
TOLERANCE = 0.10


def parse_headings(text: str) -> tuple[dict[str, list[str]], list[str]]:
    """Cue ids per scene in order, plus problems with the script's own markup.

    Direction lines (starting with '>') are never voiced, so cues in them are ignored.
    """
    cues: dict[str, list[str]] = {}
    problems: list[str] = []
    scene = None
    for n, line in enumerate(text.splitlines(), 1):
        h = HEADING_RE.match(line)
        if h:
            m = SCENE_ID_RE.match(h.group("rest").strip())
            if not m:
                problems.append(f"line {n}: heading '{line.strip()}' does not start with a scene id like L1 or E12")
                scene = None
                continue
            scene = m.group("id")
            if scene in cues:
                problems.append(f"line {n}: scene {scene} appears twice")
            cues.setdefault(scene, [])
            continue
        if line.lstrip().startswith(">"):
            continue
        for cue in CUE_RE.findall(line):
            if scene is None:
                problems.append(f"line {n}: cue {cue} sits outside any scene")
            elif not CUE_ID_RE.match(cue):
                problems.append(f"line {n}: cue id '{cue}' must be lowercase words joined by hyphens")
            elif cue in cues[scene]:
                problems.append(f"line {n}: cue {cue} appears twice in scene {scene}")
            else:
                cues[scene].append(cue)
    return cues, problems


def script_cues(text: str) -> dict[str, list[str]]:
    return parse_headings(text)[0]


def _stubs(slots) -> list[str]:
    found = []
    if isinstance(slots, dict):
        if "stub" in slots:
            found.append(str(slots["stub"]))
        for v in slots.values():
            found.extend(_stubs(v))
    return found


def check(shots: dict, script_text: str) -> list[str]:
    script, problems = parse_headings(script_text)
    cuts = shots.get("cuts", {})
    scenes = {s["id"]: s for s in shots.get("scenes", [])}
    shot_list = shots.get("shots", [])

    for sid, scene in scenes.items():
        for cut in scene.get("cuts", []):
            if cut not in cuts:
                problems.append(f"scene {sid} names unknown cut {cut}")
        if sid not in script:
            problems.append(f"scene {sid} has no section in the script")
        if not any(s.get("scene") == sid for s in shot_list):
            problems.append(f"scene {sid} has no shots")
    for sid in script:
        if sid not in scenes:
            problems.append(f"script scene {sid} is missing from the shot list")

    covered = {(s.get("scene"), s.get("cue")) for s in shot_list}
    for sid, cue_ids in script.items():
        for cue in cue_ids:
            if (sid, cue) not in covered:
                problems.append(f"cue {sid}:{cue} has no shot")

    seen_ids = set()
    for s in shot_list:
        sid, cue = s.get("scene"), s.get("cue")
        if s.get("id") in seen_ids:
            problems.append(f"shot id {s.get('id')} is used twice")
        seen_ids.add(s.get("id"))
        if sid not in scenes:
            problems.append(f"shot {s.get('id')} names unknown scene {sid}")
        elif cue not in script.get(sid, []):
            problems.append(f"shot {s.get('id')} names cue {cue}, which is not in scene {sid} of the script")
        if "speed" in s and not (isinstance(s["speed"], (int, float)) and not isinstance(s["speed"], bool)
                                 and s["speed"] > 0):
            problems.append(f"shot {s.get('id')} has speed {s['speed']!r}; it must be a number above 0")
        tags = set(s.get("tags") or [])
        for stub in _stubs(s.get("slots") or {}):
            if f"stub:{stub}" not in tags:
                problems.append(f"shot {s.get('id')} shows stub {stub} without tag stub:{stub}")

    for cut, spec in cuts.items():
        target = float(spec["target_seconds"])
        total = sum(float(sc.get("duration", 0)) for sc in scenes.values() if cut in sc.get("cuts", []))
        if abs(total - target) > TOLERANCE * target:
            problems.append(f"cut {cut} runs {total:g}s against a {target:g}s target")
    return problems


def main(argv: list[str]) -> int:
    import yaml

    if len(argv) != 3:
        print("usage: verify_shots.py demo/shots.yaml demo/script.md", file=sys.stderr)
        return 2
    shots = yaml.safe_load(Path(argv[1]).read_text())
    problems = check(shots, Path(argv[2]).read_text())
    for p in problems:
        print(p)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
