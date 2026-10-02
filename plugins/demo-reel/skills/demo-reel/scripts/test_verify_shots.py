#!/usr/bin/env python3
"""Tests for verify_shots. Run: python3 -m unittest test_verify_shots (from this folder)."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_shots as V  # noqa: E402

SCRIPT = """## L1 The promise
> a direction note [cue:ignored]
A change takes a week. [cue:headline] We fix it on camera. [cue:promise]

## L2 Why
Five causes. [cue:causes]
"""

BASE = {
    "fps": 30,
    "cuts": {"short": {"target_seconds": 30}},
    "scenes": [
        {"id": "L1", "title": "The promise", "cuts": ["short"], "duration": 20},
        {"id": "L2", "title": "Why", "cuts": ["short"], "duration": 10},
    ],
    "shots": [
        {"id": "L1.1", "scene": "L1", "cue": "headline", "layout": "title", "slots": {}, "tags": []},
        {"id": "L1.2", "scene": "L1", "cue": "promise", "layout": "title", "slots": {}, "tags": []},
        {"id": "L2.1", "scene": "L2", "cue": "causes", "layout": "figure", "slots": {}, "tags": []},
    ],
}


def shots():
    return copy.deepcopy(BASE)


class ScriptMarkup(unittest.TestCase):
    def test_cues_by_scene_skip_direction_notes(self):
        self.assertEqual(V.script_cues(SCRIPT), {"L1": ["headline", "promise"], "L2": ["causes"]})

    def test_heading_without_scene_id_is_flagged(self):
        _, problems = V.parse_headings("## E1a Extra\nWords. [cue:b]\n")
        self.assertIn("line 1: heading '## E1a Extra' does not start with a scene id like L1 or E12", problems)

    def test_bad_cue_id_is_flagged(self):
        _, problems = V.parse_headings("## L1 T\nHello. [cue:Headline]\n")
        self.assertIn("line 2: cue id 'Headline' must be lowercase words joined by hyphens", problems)

    def test_duplicate_cue_in_scene_is_flagged(self):
        _, problems = V.parse_headings("## L1 T\nA. [cue:a] B. [cue:a]\n")
        self.assertIn("line 2: cue a appears twice in scene L1", problems)


class Check(unittest.TestCase):
    def test_clean_shot_list_has_no_problems(self):
        self.assertEqual(V.check(shots(), SCRIPT), [])

    def test_cue_without_a_shot(self):
        s = shots()
        s["shots"] = s["shots"][:2]
        self.assertIn("cue L2:causes has no shot", V.check(s, SCRIPT))

    def test_scene_without_shots(self):
        s = shots()
        s["shots"] = s["shots"][:2]
        self.assertIn("scene L2 has no shots", V.check(s, SCRIPT))

    def test_shot_cue_missing_from_script(self):
        s = shots()
        s["shots"][2]["cue"] = "effects"
        self.assertIn("shot L2.1 names cue effects, which is not in scene L2 of the script", V.check(s, SCRIPT))

    def test_scene_missing_from_script(self):
        s = shots()
        s["scenes"].append({"id": "L3", "title": "Extra", "cuts": ["short"], "duration": 0})
        s["shots"].append({"id": "L3.1", "scene": "L3", "cue": "x", "layout": "title", "slots": {}, "tags": []})
        self.assertIn("scene L3 has no section in the script", V.check(s, SCRIPT))

    def test_shot_in_unknown_scene(self):
        s = shots()
        s["shots"].append({"id": "X.1", "scene": "X9", "cue": "causes", "layout": "title", "slots": {}, "tags": []})
        self.assertIn("shot X.1 names unknown scene X9", V.check(s, SCRIPT))

    def test_scene_in_unknown_cut(self):
        s = shots()
        s["scenes"][1]["cuts"] = ["short", "director"]
        self.assertIn("scene L2 names unknown cut director", V.check(s, SCRIPT))

    def test_runtime_outside_ten_percent(self):
        s = shots()
        s["cuts"] = {"short": {"target_seconds": 60}}
        self.assertIn("cut short runs 30s against a 60s target", V.check(s, SCRIPT))

    def test_speed_must_be_positive_number(self):
        for bad in (0, -1, "4", None, True):
            s = shots()
            s["shots"][2]["speed"] = bad
            self.assertIn(f"shot L2.1 has speed {bad!r}; it must be a number above 0", V.check(s, SCRIPT))

    def test_stub_slot_needs_stub_tag(self):
        s = shots()
        s["shots"][2]["slots"] = {"left": {"kind": "terminal", "stub": "payments"}}
        self.assertIn("shot L2.1 shows stub payments without tag stub:payments", V.check(s, SCRIPT))

    def test_stub_slot_with_tag_is_clean(self):
        s = shots()
        s["shots"][2]["slots"] = {"left": {"kind": "terminal", "stub": "payments"}}
        s["shots"][2]["tags"] = ["stub:payments"]
        self.assertEqual(V.check(s, SCRIPT), [])


if __name__ == "__main__":
    unittest.main()
