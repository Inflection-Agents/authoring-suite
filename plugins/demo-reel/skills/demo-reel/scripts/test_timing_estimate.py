#!/usr/bin/env python3
"""Tests for timing.py's estimate mode. Run: python3 -m unittest test_timing_estimate."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cues as C  # noqa: E402
import timing as T  # noqa: E402

SCRIPT = """## L1 T
One two.
> hold: 2s
[cue:b] Three four.
"""


class Estimate(unittest.TestCase):
    def test_words_share_the_time_left_after_holds(self):
        [scene] = C.parse_script(SCRIPT)
        est = T.estimate(scene, 6.0)
        self.assertEqual(est["duration"], 6.0)
        self.assertEqual(est["cues"], {"b": 4.0})
        self.assertEqual([s["start"] for s in est["sentences"]], [0.0, 4.0])


if __name__ == "__main__":
    unittest.main()
