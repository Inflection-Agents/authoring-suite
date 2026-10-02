#!/usr/bin/env python3
"""Tests for normalize_events and captions. Run: python3 -m unittest test_events_and_captions."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions as CA  # noqa: E402
import normalize_events as N  # noqa: E402


def run(id_, t0):
    return [
        {"t": t0, "wall": 100 + t0, "kind": "capture-start"},
        {"wall": 99.0, "kind": "recording-start", "surface": "browser"},
        {"t": t0 + 1, "wall": 101 + t0, "kind": "response", "status": 200, "body": {"invocationId": id_}},
        {"t": t0 + 1.1, "wall": 101.1 + t0, "kind": "invocation", "id": id_},
        {"t": t0 + 2, "wall": 102 + t0, "kind": "request", "method": "POST", "path": f"/confirm/{id_}"},
    ]


class Normalize(unittest.TestCase):
    def test_two_runs_with_different_ids_and_times_match(self):
        self.assertEqual(N.normalize(run("inv_a1", 0.0)), N.normalize(run("inv_zz9", 5.5)))

    def test_ids_replaced_in_bodies_and_paths(self):
        lines = N.normalize(run("inv_a1", 0.0))
        self.assertIn('"/confirm/<id-1>"', lines[-1])
        self.assertIn('"invocationId": "<id-1>"', lines[1])

    def test_real_difference_still_shows(self):
        b = run("inv_b", 0.0)
        b[2]["status"] = 500
        self.assertNotEqual(N.normalize(run("inv_a", 0.0)), N.normalize(b))


class Captions(unittest.TestCase):
    def test_sentences_across_scenes(self):
        timing = {"L1": {"sentences": [{"text": "One.", "start": 0.0}, {"text": "Two.", "start": 1.5}]},
                  "L2": {"sentences": [{"text": "Three.", "start": 0.2}]}}
        props = {"fps": 30, "scenes": [{"id": "L1", "durationInFrames": 90}, {"id": "L2", "durationInFrames": 60}]}
        self.assertEqual(CA.srt(timing, props),
                         "1\n00:00:00,000 --> 00:00:01,500\nOne.\n\n"
                         "2\n00:00:01,500 --> 00:00:03,000\nTwo.\n\n"
                         "3\n00:00:03,200 --> 00:00:05,000\nThree.\n")


if __name__ == "__main__":
    unittest.main()
