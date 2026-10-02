#!/usr/bin/env python3
"""Build the props file Remotion renders a cut from.

Every number the video shows is computed here from three inputs: the shot list, the narration
timing, and each take's event log. Nothing is typed into the edit.

The clocks. The driver writes `t` (seconds since it started) and `wall` (Unix seconds) on every
event. A recorder running in another process logs only `recording-start` with `wall`, so its start
is converted to driver time through the take's `capture-start`. A shot shows the window of its take
between two events, `in` (default `capture-start`) and `out` (default `capture-end`), played at a
speed that makes the window fit the shot. A recording is trimmed by the gap between its own start and
the window's start, so every pane shows the same moment.

Usage:
    python3 build_props.py demo/shots.yaml demo/timing.json demo/takes <cut> demo/remotion/props-<cut>.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

WIDTH, HEIGHT = 1920, 1080
TOLERANCE = 0.10


class BuildError(Exception):
    def __init__(self, problems: list[str]):
        super().__init__("\n".join(problems))
        self.problems = problems


def load_takes(takes_dir: Path) -> dict[str, list[dict]]:
    takes = {}
    for f in sorted(takes_dir.glob("*/events.jsonl")):
        takes[f.parent.name] = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    return takes


def _find(events: list[dict], kind: str, name: str | None = None) -> dict | None:
    for e in events:
        if e["kind"] == kind and (name is None or e.get("name") == name):
            return e
    return None


def _mark(events, label):
    """`capture-start`/`capture-end`, or a named mark."""
    if label in ("capture-start", "capture-end"):
        return _find(events, label)
    return _find(events, "mark", label)


def _text(v) -> str:
    return v if isinstance(v, str) else json.dumps(v, separators=(", ", ": "))


def _terminal_lines(window, at):
    lines = []
    for e in window:
        if e["kind"] == "request":
            body = f"  {_text(e['body'])}" if e.get("body") is not None else ""
            lines.append({"atFrame": at(e), "kind": "cmd", "text": f"{e['method']} {e['path']}{body}"})
        elif e["kind"] == "response":
            lines.append({"atFrame": at(e), "kind": "out", "text": f"{e['status']}  {_text(e.get('body', ''))}"})
        elif e["kind"] == "command":
            lines.append({"atFrame": at(e), "kind": "cmd", "text": e["cmd"]})
            for out in str(e.get("out", "")).splitlines()[:12]:
                lines.append({"atFrame": at(e), "kind": "err" if e.get("exit") else "out", "text": out})
    return lines


def _shot_window(shot, events, fps, frames, problems):
    take = shot["take"]
    start, end = _mark(events, shot.get("in", "capture-start")), _mark(events, shot.get("out", "capture-end"))
    if start is None or end is None:
        problems.append(f"shot {shot['id']}: take {take} has no event '{shot.get('in', 'capture-start') if start is None else shot.get('out', 'capture-end')}'")
        return None
    span = end["t"] - start["t"]
    seconds = frames / fps
    needed = span / seconds if seconds else math.inf
    speed = shot.get("speed")
    if speed is None:
        speed = max(1.0, math.ceil(needed * 10) / 10)
    elif speed + 1e-9 < needed:
        problems.append(f"shot {shot['id']}: take {take} spans {span:g}s but the shot is {seconds:g}s; "
                        f"speed must be at least {math.ceil(needed * 10) / 10:g}")
        return None
    window = [e for e in events if "t" in e and start["t"] <= e["t"] <= end["t"]]
    return start, end, speed, window


def _fill(shot, takes, fps, frames, problems):
    slots = {k: dict(v) if isinstance(v, dict) else v for k, v in (shot.get("slots") or {}).items()}
    badges, speed = [], 1
    take = shot.get("take")
    if take:
        events = takes.get(take)
        if events is None:
            problems.append(f"shot {shot['id']}: take {take} has no events file")
            return slots, badges, speed
        win = _shot_window(shot, events, fps, frames, problems)
        if win is None:
            return slots, badges, speed
        start, _, speed, window = win
        cap = _find(events, "capture-start")
        if cap is None:
            problems.append(f"shot {shot['id']}: take {take} has no capture-start")
            return slots, badges, speed
        offset = cap["wall"] - cap["t"]  # wall = t + offset

        def at(e):
            return round((e["t"] - start["t"]) / speed * fps)

        for slot in slots.values():
            if not isinstance(slot, dict):
                continue
            kind = slot.get("kind")
            if kind == "terminal":
                slot["lines"] = _terminal_lines(window, at)
            elif kind == "facts-panel":
                slot["facts"] = [{"atFrame": at(e), "name": e["name"], "value": e["value"]}
                                 for e in window if e["kind"] in ("fact", "outcome")]
            elif kind == "browser":
                rec = next((e for e in events if e["kind"] == "recording-start" and e.get("surface") == "browser"), None)
                if rec is None:
                    problems.append(f"shot {shot['id']}: take {take} has no browser recording-start")
                    continue
                slot["src"] = f"takes/{take}/browser.webm"
                slot["trimBefore"] = round((start["t"] - (rec["wall"] - offset)) * fps)
            elif kind == "code" and slot.get("edits"):
                slot["edits"] = [{"atFrame": at(e), "line": e["line"], "before": e["before"], "after": e["after"]}
                                 for e in window if e["kind"] == "edit"]
            elif kind == "timer":
                t0, t1 = _find(window, "mark", "timer-start"), _find(window, "mark", "timer-stop")
                if t0 is None or t1 is None:
                    problems.append(f"shot {shot['id']}: timer needs marks timer-start and timer-stop in take {take}")
                    continue
                slot.update({"startFrame": at(t0), "stopFrame": at(t1), "seconds": round(t1["t"] - t0["t"], 2)})
        for e in events:
            if e["kind"] == "stub":
                label = "stub · " + e["name"].replace("-", " ")
                if label not in badges:
                    badges.append(label)
    elif "speed" in shot:
        speed = shot["speed"]
    if speed != 1:
        badges.insert(0, f"{speed:g}×")
    for tag in shot.get("tags") or []:
        label = "stub · " + tag.split(":", 1)[1].replace("-", " ") if tag.startswith("stub:") else tag
        if tag.startswith("stub:") or tag == "design":
            if label not in badges:
                badges.append(label)
    return slots, badges, speed


def build(shots: dict, timing: dict, takes: dict[str, list[dict]], cut: str) -> tuple[dict, list[str]]:
    """Props for one cut, plus warnings. Raises BuildError listing every problem found."""
    fps = int(shots.get("fps", 30))
    problems: list[str] = []
    scenes = []
    for sc in shots["scenes"]:
        if cut not in sc["cuts"]:
            continue
        t = timing.get(sc["id"])
        if t is None:
            problems.append(f"scene {sc['id']} has no narration timing")
            continue
        total = math.ceil(t["duration"] * fps)
        mine = [s for s in shots["shots"] if s["scene"] == sc["id"]]
        for s in mine:
            if s["cue"] not in t["cues"]:
                problems.append(f"shot {s['id']}: cue {s['cue']} is not in the timing for scene {sc['id']}")
        mine = [s for s in mine if s["cue"] in t["cues"]]
        mine.sort(key=lambda s: t["cues"][s["cue"]])
        starts = [0 if i == 0 else round(t["cues"][s["cue"]] * fps) for i, s in enumerate(mine)]
        for i in range(1, len(starts)):
            if starts[i] <= starts[i - 1]:
                problems.append(f"shots {mine[i - 1]['id']} and {mine[i]['id']} start on the same frame")
        placed = []
        for i, s in enumerate(mine):
            end = starts[i + 1] if i + 1 < len(mine) else total
            frames = max(1, end - starts[i])
            slots, badges, speed = _fill(s, takes, fps, frames, problems)
            placed.append({"id": s["id"], "layout": s["layout"], "from": starts[i], "durationInFrames": frames,
                           "slots": slots, "badges": badges, "speed": speed})
        scenes.append({"id": sc["id"], "title": sc["title"], "audio": f"voice/{sc['id']}.wav",
                       "durationInFrames": total, "shots": placed})
    if problems:
        raise BuildError(problems)
    warnings = []
    target = shots["cuts"][cut]["target_seconds"]
    seconds = sum(s["durationInFrames"] for s in scenes) / fps
    if abs(seconds - target) > TOLERANCE * target:
        warnings.append(f"cut {cut} runs {seconds:.0f}s against a {target}s target")
    return {"fps": fps, "width": WIDTH, "height": HEIGHT, "cut": cut, "scenes": scenes}, warnings


def main(argv: list[str]) -> int:
    import yaml

    if len(argv) != 6:
        print("usage: build_props.py shots.yaml timing.json takes-dir cut out.json", file=sys.stderr)
        return 2
    shots = yaml.safe_load(Path(argv[1]).read_text())
    timing = json.loads(Path(argv[2]).read_text())
    try:
        props, warnings = build(shots, timing, load_takes(Path(argv[3])), argv[4])
    except BuildError as e:
        for p in e.problems:
            print(p)
        print(f"{len(e.problems)} problem(s); nothing written")
        return 1
    Path(argv[5]).write_text(json.dumps(props, indent=1))
    for w in warnings:
        print(f"warning: {w}")
    frames = sum(s["durationInFrames"] for s in props["scenes"])
    print(f"{argv[4]}: {len(props['scenes'])} scenes, {frames / props['fps']:.1f}s -> {argv[5]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
