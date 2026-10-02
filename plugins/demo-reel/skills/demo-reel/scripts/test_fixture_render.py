#!/usr/bin/env python3
"""Render the Remotion fixture through the real pipeline and check the result.

The fixture is a shot list, a script, a timing file and one take's events. The test generates a
stand-in browser recording and a silent narration track with ffmpeg (so the repository carries no
media), runs verify_shots and build_props exactly as an engagement would, renders the cut, and checks
it is 10 seconds of 1920x1080 video with an audio stream.

Slow, because it starts a headless browser. Needs Node 22, ffmpeg, and `npm ci` run in the Remotion
folder. Run it directly:
    python3 skills/demo-reel/scripts/test_fixture_render.py
    REMOTION_DIR=demo/remotion python3 <plugin>/skills/demo-reel/scripts/test_fixture_render.py
"""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REMOTION = Path(os.environ.get("REMOTION_DIR", SCRIPTS.parent / "remotion")).resolve()


def run(*cmd, cwd=REMOTION):
    subprocess.run([str(c) for c in cmd], cwd=cwd, check=True)


class FixtureRender(unittest.TestCase):
    def test_fixture_renders_ten_seconds_at_1080p_with_audio(self):
        fx = REMOTION / "fixtures"
        (REMOTION / "public" / "takes" / "fixture").mkdir(parents=True, exist_ok=True)
        (REMOTION / "public" / "voice").mkdir(parents=True, exist_ok=True)
        (REMOTION / "out").mkdir(exist_ok=True)
        run("ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=820x1000:rate=30:duration=6",
            "-c:v", "libvpx", "-b:v", "500k", "public/takes/fixture/browser.webm")
        run("ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "10",
            "public/voice/F1.wav")
        run(sys.executable, SCRIPTS / "verify_shots.py", fx / "shots.yaml", fx / "script.md")
        run(sys.executable, SCRIPTS / "build_props.py", fx / "shots.yaml", fx / "timing.json", fx / "takes",
            "fixture", fx / "props.json")
        out = REMOTION / "out" / "fixture.mp4"
        out.unlink(missing_ok=True)
        run("npx", "remotion", "render", "src/index.ts", "Cut", out, f"--props={fx / 'props.json'}")
        probe = json.loads(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
             "-of", "json", str(out)], capture_output=True, text=True, check=True).stdout)
        video = next(s for s in probe["streams"] if s["codec_type"] == "video")
        self.assertEqual((video["width"], video["height"]), (1920, 1080))
        self.assertTrue(any(s["codec_type"] == "audio" for s in probe["streams"]))
        self.assertAlmostEqual(float(probe["format"]["duration"]), 10.0, delta=0.2)


if __name__ == "__main__":
    unittest.main()
