#!/usr/bin/env python3
"""Write timing.json from per-scene narration audio.

Usage:
    python3 timing.py demo/script.md demo/remotion/public/voice demo/timing.json
    python3 timing.py --estimate demo/shots.yaml demo/script.md demo/timing.json

For every scene in the script it reads <voice dir>/<scene>.wav and its word timings from
<voice dir>/<scene>.words.json, which narration/narrate.py writes for both engines. Narration
recorded by hand has no words file, so it is transcribed with Whisper (narration/asr.py, installed by
`narration/install.sh qwen`). Writes {scene: {"duration": s, "cues": {cue: s},
"sentences": [{"text", "start"}]}}.

Before narration exists, --estimate writes the same file from the shot list's estimated scene durations:
the words share each scene's time evenly after its holds, so build_props can check every shot's window
during capture.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from cues import cue_times, parse_script, sentence_times
from holds import apply_holds


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "default=noprint_wrappers=1:nokey=1", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def heard_words(wav: Path) -> list[tuple[str, float, float]]:
    words_file = wav.with_suffix(".words.json")
    if words_file.exists():
        words = json.loads(words_file.read_text())["words"]
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "narration"))
        import asr
        words = asr.words_from_file(wav)
    return [(w["word"], float(w["start"]), float(w["end"])) for w in words]


def estimate(scene, seconds: float) -> dict:
    words = scene.text.split()
    each = max(0.0, seconds - sum(h for h, _ in scene.holds)) / max(1, len(words))
    even = [{"word": w, "start": round(i * each, 3), "end": round((i + 1) * each, 3)} for i, w in enumerate(words)]
    spread, _ = apply_holds(even, scene.holds, len(words) * each)
    heard = [(w["word"], w["start"], w["end"]) for w in spread]
    return {"duration": seconds, "cues": cue_times(scene, heard), "sentences": sentence_times(scene, heard)}


def main_estimate(shots: Path, script: Path, out: Path) -> int:
    import yaml

    durations = {s["id"]: float(s["duration"]) for s in yaml.safe_load(shots.read_text())["scenes"]}
    timing = {sc.id: estimate(sc, durations[sc.id]) for sc in parse_script(script.read_text()) if sc.id in durations}
    out.write_text(json.dumps(timing, indent=1))
    print(f"{out}: {len(timing)} scenes, estimated")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 5 and argv[1] == "--estimate":
        return main_estimate(Path(argv[2]), Path(argv[3]), Path(argv[4]))
    if len(argv) != 4:
        print("usage: timing.py script.md voice-dir timing.json | --estimate shots.yaml script.md timing.json",
              file=sys.stderr)
        return 2
    script, voice_dir, out = Path(argv[1]), Path(argv[2]), Path(argv[3])
    timing = {}
    for scene in parse_script(script.read_text()):
        wav = voice_dir / f"{scene.id}.wav"
        if not wav.exists():
            print(f"missing {wav}", file=sys.stderr)
            return 1
        heard = heard_words(wav)
        timing[scene.id] = {"duration": round(duration(wav), 3), "cues": cue_times(scene, heard),
                            "sentences": sentence_times(scene, heard)}
        print(f"{scene.id}: {timing[scene.id]['duration']}s, {len(timing[scene.id]['cues'])} cues")
    out.write_text(json.dumps(timing, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
