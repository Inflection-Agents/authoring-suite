#!/usr/bin/env python3
"""Tests for build_props. Run: python3 -m unittest test_build_props (from this folder)."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_props as B  # noqa: E402

SHOTS = {
    "fps": 30,
    "cuts": {"short": {"target_seconds": 10}, "long": {"target_seconds": 20}},
    "scenes": [
        {"id": "L1", "title": "Promise", "cuts": ["short", "long"], "duration": 10},
        {"id": "E1", "title": "Extra", "cuts": ["long"], "duration": 10},
    ],
    "shots": [
        {"id": "L1.2", "scene": "L1", "cue": "b", "layout": "three-pane", "take": "run-1",
         "slots": {"left": {"kind": "terminal"}, "center": {"kind": "browser"},
                   "right": {"kind": "facts-panel"}}, "tags": []},
        {"id": "L1.1", "scene": "L1", "cue": "a", "layout": "title", "slots": {"text": {"text": "hi"}}, "tags": []},
        {"id": "E1.1", "scene": "E1", "cue": "c", "layout": "figure", "slots": {}, "tags": ["design"]},
    ],
}
TIMING = {"L1": {"duration": 10.0, "cues": {"a": 0.0, "b": 2.0}},
          "E1": {"duration": 10.0, "cues": {"c": 0.5}}}
# Driver started at wall 1000.0, so wall = t + 1000. The browser recorder started 3 s before capture-start.
RUN1 = [
    {"t": 0.0, "wall": 1000.0, "kind": "capture-start"},
    {"wall": 997.0, "kind": "recording-start", "surface": "browser"},
    {"t": 1.0, "wall": 1001.0, "kind": "stub", "name": "payment-gateway"},
    {"t": 2.0, "wall": 1002.0, "kind": "request", "step": "start", "method": "POST", "path": "/bookings/start",
     "body": {"nights": 3}},
    {"t": 2.5, "wall": 1002.5, "kind": "response", "step": "start", "status": 200, "body": {"id": "id_1"}},
    {"t": 8.0, "wall": 1008.0, "kind": "fact", "name": "nights", "value": 3},
    {"t": 16.0, "wall": 1016.0, "kind": "capture-end"},
]
TAKES = {"run-1": RUN1}


def shots():
    return copy.deepcopy(SHOTS)


class Placement(unittest.TestCase):
    def test_short_cut_keeps_only_its_scenes(self):
        p, _ = B.build(shots(), TIMING, TAKES, "short")
        self.assertEqual([s["id"] for s in p["scenes"]], ["L1"])

    def test_scene_length_comes_from_audio(self):
        p, _ = B.build(shots(), TIMING, TAKES, "long")
        self.assertEqual([s["durationInFrames"] for s in p["scenes"]], [300, 300])

    def test_shots_sorted_by_cue_and_run_to_next_cue(self):
        p, _ = B.build(shots(), TIMING, TAKES, "short")
        self.assertEqual([(s["id"], s["from"], s["durationInFrames"]) for s in p["scenes"][0]["shots"]],
                         [("L1.1", 0, 60), ("L1.2", 60, 240)])

    def test_first_shot_starts_at_scene_start(self):
        p, _ = B.build(shots(), TIMING, TAKES, "long")
        self.assertEqual(p["scenes"][1]["shots"][0]["from"], 0)

    def test_two_shots_on_one_frame_is_an_error(self):
        t = copy.deepcopy(TIMING)
        t["L1"]["cues"]["b"] = 0.01
        with self.assertRaises(B.BuildError) as e:
            B.build(shots(), t, TAKES, "short")
        self.assertIn("shots L1.1 and L1.2 start on the same frame", e.exception.problems)

    def test_cue_missing_from_timing_is_an_error(self):
        t = copy.deepcopy(TIMING)
        del t["L1"]["cues"]["b"]
        with self.assertRaises(B.BuildError) as e:
            B.build(shots(), t, TAKES, "short")
        self.assertIn("shot L1.2: cue b is not in the timing for scene L1", e.exception.problems)

    def test_audio_path_per_scene(self):
        p, _ = B.build(shots(), TIMING, TAKES, "short")
        self.assertEqual(p["scenes"][0]["audio"], "voice/L1.wav")


class Takes(unittest.TestCase):
    def shot(self, p):
        return p["scenes"][0]["shots"][1]

    def test_speed_is_derived_so_the_take_fits_the_shot(self):
        # the take spans 16 s; the shot is 240 frames = 8 s; so 2x
        p, _ = B.build(shots(), TIMING, TAKES, "short")
        self.assertEqual(self.shot(p)["speed"], 2.0)

    def test_given_speed_too_low_is_an_error(self):
        s = shots()
        s["shots"][0]["speed"] = 1.5
        with self.assertRaises(B.BuildError) as e:
            B.build(s, TIMING, TAKES, "short")
        self.assertIn("shot L1.2: take run-1 spans 16s but the shot is 8s; speed must be at least 2",
                      e.exception.problems)

    def test_badges_from_speed_driver_stubs_and_tags(self):
        p, _ = B.build(shots(), TIMING, TAKES, "long")
        self.assertEqual(self.shot(p)["badges"], ["2×", "stub · payment gateway"])
        self.assertEqual(p["scenes"][1]["shots"][0]["badges"], ["design"])

    def test_facts_on_the_take_clock_at_speed(self):
        # fact at t=8 s, window starts at t=0, speed 2: 4 s into the shot = frame 120
        p, _ = B.build(shots(), TIMING, TAKES, "short")
        self.assertEqual(self.shot(p)["slots"]["right"]["facts"],
                         [{"atFrame": 120, "name": "nights", "value": 3}])

    def test_terminal_lines_from_requests_and_responses(self):
        p, _ = B.build(shots(), TIMING, TAKES, "short")
        self.assertEqual(self.shot(p)["slots"]["left"]["lines"], [
            {"atFrame": 30, "kind": "cmd", "text": 'POST /bookings/start  {"nights": 3}'},
            {"atFrame": 38, "kind": "out", "text": '200  {"id": "id_1"}'},
        ])

    def test_browser_recording_trimmed_to_the_window(self):
        # recording started 3 s before capture-start, the window starts at capture-start: trim 90 frames
        p, _ = B.build(shots(), TIMING, TAKES, "short")
        center = self.shot(p)["slots"]["center"]
        self.assertEqual((center["src"], center["trimBefore"]), ("takes/run-1/browser.webm", 90))

    def test_window_from_named_marks(self):
        events = RUN1[:5] + [{"t": 4.0, "wall": 1004.0, "kind": "mark", "name": "go"}] + RUN1[5:]
        s = shots()
        s["shots"][0]["in"] = "go"
        p, _ = B.build(s, TIMING, {"run-1": events}, "short")
        shot = self.shot(p)
        self.assertEqual(shot["speed"], 1.5)
        self.assertEqual(shot["slots"]["center"]["trimBefore"], 210)
        self.assertEqual(shot["slots"]["right"]["facts"][0]["atFrame"], 80)

    def test_missing_take_is_an_error(self):
        with self.assertRaises(B.BuildError) as e:
            B.build(shots(), TIMING, {}, "short")
        self.assertIn("shot L1.2: take run-1 has no events file", e.exception.problems)

    def test_browser_without_recording_start_is_an_error(self):
        events = [e for e in RUN1 if e["kind"] != "recording-start"]
        with self.assertRaises(B.BuildError) as e:
            B.build(shots(), TIMING, {"run-1": events}, "short")
        self.assertIn("shot L1.2: take run-1 has no browser recording-start", e.exception.problems)


    def test_take_without_capture_start_is_an_error(self):
        events = [e for e in RUN1 if e["kind"] != "capture-start"] + [{"t": 0.0, "wall": 1000.0, "kind": "mark", "name": "go"}]
        s = shots()
        s["shots"][0]["in"] = "go"
        with self.assertRaises(B.BuildError) as e:
            B.build(s, TIMING, {"run-1": events}, "short")
        self.assertIn("shot L1.2: take run-1 has no capture-start", e.exception.problems)


class EditsAndTimer(unittest.TestCase):
    def test_edits_and_timer_from_events(self):
        events = [
            {"t": 0.0, "wall": 500.0, "kind": "capture-start"},
            {"t": 1.0, "wall": 501.0, "kind": "mark", "name": "timer-start"},
            {"t": 2.0, "wall": 502.0, "kind": "edit", "file": "booking.ts", "line": 4,
             "before": "holdMinutes = 15", "after": "holdMinutes = 20"},
            {"t": 3.0, "wall": 503.0, "kind": "command", "cmd": "npm run build", "exit": 0, "out": "ok"},
            {"t": 7.0, "wall": 507.0, "kind": "mark", "name": "timer-stop"},
            {"t": 8.0, "wall": 508.0, "kind": "capture-end"},
        ]
        s = shots()
        s["shots"][0].update({"layout": "editor-build", "take": "climax",
                              "slots": {"code": {"kind": "code", "edits": True, "tokens": "code/booking.json"},
                                        "terminal": {"kind": "terminal"}, "timer": {"kind": "timer"}}})
        p, _ = B.build(s, TIMING, {"climax": events}, "short")
        shot = p["scenes"][0]["shots"][1]
        self.assertEqual(shot["speed"], 1.0)
        self.assertEqual(shot["slots"]["code"]["edits"],
                         [{"atFrame": 60, "line": 4, "before": "holdMinutes = 15", "after": "holdMinutes = 20"}])
        self.assertEqual(shot["slots"]["timer"], {"kind": "timer", "startFrame": 30, "stopFrame": 210, "seconds": 6.0})
        self.assertEqual(shot["slots"]["terminal"]["lines"][0], {"atFrame": 90, "kind": "cmd", "text": "npm run build"})


class TimerAcrossShots(unittest.TestCase):
    def test_timer_marks_outside_the_window_keep_the_count_going(self):
        events = [
            {"t": 0.0, "wall": 500.0, "kind": "capture-start"},
            {"t": 1.0, "wall": 501.0, "kind": "mark", "name": "timer-start"},
            {"t": 5.0, "wall": 505.0, "kind": "mark", "name": "rerun"},
            {"t": 7.0, "wall": 507.0, "kind": "mark", "name": "timer-stop"},
            {"t": 9.0, "wall": 509.0, "kind": "capture-end"},
        ]
        s = shots()
        s["shots"][0].update({"layout": "three-pane", "take": "climax", "in": "rerun",
                              "slots": {"right": {"kind": "facts-panel"}, "timer": {"kind": "timer"}}})
        p, _ = B.build(s, TIMING, {"climax": events}, "short")
        shot = p["scenes"][0]["shots"][1]
        self.assertEqual(shot["speed"], 1.0)
        self.assertEqual(shot["slots"]["timer"], {"kind": "timer", "startFrame": -120, "stopFrame": 60, "seconds": 6.0})


class EditsAcrossShots(unittest.TestCase):
    def test_an_edit_before_the_window_is_already_applied(self):
        events = [
            {"t": 0.0, "wall": 500.0, "kind": "capture-start"},
            {"t": 1.0, "wall": 501.0, "kind": "edit", "line": 11, "before": "  a: 15,", "after": "  a: 20,"},
            {"t": 2.0, "wall": 502.0, "kind": "mark", "name": "typo"},
            {"t": 3.0, "wall": 503.0, "kind": "edit", "line": 11, "before": "  a: 20,", "after": "  b: 20,"},
            {"t": 6.0, "wall": 506.0, "kind": "capture-end"},
        ]
        s = shots()
        s["shots"][0].update({"layout": "editor-build", "take": "climax", "in": "typo", "speed": 1,
                              "slots": {"code": {"kind": "code", "edits": True}, "terminal": {"kind": "terminal"}}})
        p, _ = B.build(s, TIMING, {"climax": events}, "short")
        edits = p["scenes"][0]["shots"][1]["slots"]["code"]["edits"]
        self.assertEqual([(e["atFrame"], e["after"]) for e in edits], [(-30, "  a: 20,"), (30, "  b: 20,")])


class TimerTotal(unittest.TestCase):
    def test_closing_card_reads_the_real_total_without_badges(self):
        events = [
            {"t": 0.0, "wall": 500.0, "kind": "capture-start"},
            {"t": 0.5, "wall": 500.5, "kind": "stub", "name": "payment-gateway"},
            {"t": 1.0, "wall": 501.0, "kind": "mark", "name": "timer-start"},
            {"t": 95.5, "wall": 595.5, "kind": "mark", "name": "timer-stop"},
            {"t": 96.0, "wall": 596.0, "kind": "capture-end"},
        ]
        s = shots()
        s["shots"][0].update({"layout": "title", "take": "climax",
                              "slots": {"text": {"text": "~~an hour~~"}, "total": {"kind": "timer-total"}}})
        p, _ = B.build(s, TIMING, {"climax": events}, "short")
        shot = p["scenes"][0]["shots"][1]
        self.assertEqual(shot["slots"]["total"], {"kind": "timer-total", "seconds": 94.5})
        self.assertEqual((shot["badges"], shot["speed"]), ([], 1))


class HistoryBeforeTheWindow(unittest.TestCase):
    events = [
        {"t": 0.0, "wall": 1000.0, "kind": "capture-start"},
        {"t": 1.0, "wall": 1001.0, "kind": "fact", "name": "nights", "value": 3},
        {"t": 1.0, "wall": 1001.0, "kind": "request", "step": "a", "method": "POST", "path": "/a"},
        {"t": 2.0, "wall": 1002.0, "kind": "mark", "name": "go"},
        {"t": 3.0, "wall": 1003.0, "kind": "edit", "line": 11, "before": "x", "after": "y"},
        {"t": 4.0, "wall": 1004.0, "kind": "mark", "name": "stop"},
        {"t": 4.0, "wall": 1004.0, "kind": "edit", "line": 11, "before": "y", "after": "z"},
        {"t": 4.0, "wall": 1004.0, "kind": "fact", "name": "late", "value": 1},
        {"t": 9.0, "wall": 1009.0, "kind": "capture-end"},
    ]

    def slots(self, kinds):
        s = shots()
        s["shots"][0].update({"layout": "editor-build", "in": "go", "out": "stop", "speed": 1, "slots": kinds})
        p, _ = B.build(s, TIMING, {"run-1": self.events}, "short")
        return p["scenes"][0]["shots"][1]["slots"]

    def test_facts_and_terminal_lines_from_before_the_window_are_already_shown(self):
        sl = self.slots({"right": {"kind": "facts-panel"}, "terminal": {"kind": "terminal"}})
        self.assertEqual([(f["name"], f["atFrame"]) for f in sl["right"]["facts"]], [("nights", -30)])
        self.assertEqual([(l["text"], l["atFrame"]) for l in sl["terminal"]["lines"]], [("POST /a", -30)])

    def test_an_edit_logged_after_out_in_the_same_millisecond_is_outside(self):
        sl = self.slots({"code": {"kind": "code", "edits": True}})
        self.assertEqual([e["after"] for e in sl["code"]["edits"]], ["y"])


class SilentCommand(unittest.TestCase):
    def test_a_command_with_no_output_shows_its_exit_code(self):
        lines = B._terminal_lines([{"t": 1.0, "kind": "command", "cmd": "npm run build", "exit": 0, "out": ""}], lambda e: 0)
        self.assertEqual([(l["kind"], l["text"]) for l in lines], [("cmd", "npm run build"), ("out", "exit 0")])


class QuietTail(unittest.TestCase):
    def test_a_short_quiet_tail_past_the_shot_needs_no_speed_up(self):
        events = [
            {"t": 0.0, "wall": 1000.0, "kind": "capture-start"},
            {"t": 6.0, "wall": 1006.0, "kind": "fact", "name": "last", "value": 1},
            {"t": 8.05, "wall": 1008.05, "kind": "capture-end"},
        ]
        s = shots()
        s["shots"][0]["slots"] = {"right": {"kind": "facts-panel"}}
        p, _ = B.build(s, TIMING, {"run-1": events}, "short")
        self.assertEqual(p["scenes"][0]["shots"][1]["speed"], 1.0)


class WindowOrder(unittest.TestCase):
    def test_an_event_logged_after_out_in_the_same_millisecond_is_outside(self):
        events = [
            {"t": 0.0, "wall": 1000.0, "kind": "capture-start"},
            {"t": 1.0, "wall": 1001.0, "kind": "fact", "name": "first", "value": 1},
            {"t": 6.0, "wall": 1006.0, "kind": "mark", "name": "second-booking"},
            {"t": 6.0, "wall": 1006.0, "kind": "fact", "name": "second", "value": 2},
            {"t": 9.0, "wall": 1009.0, "kind": "capture-end"},
        ]
        s = shots()
        s["shots"][0].update({"out": "second-booking", "slots": {"right": {"kind": "facts-panel"}}})
        p, _ = B.build(s, TIMING, {"run-1": events}, "short")
        self.assertEqual([f["name"] for f in p["scenes"][0]["shots"][1]["slots"]["right"]["facts"]], ["first"])


class ShortWindow(unittest.TestCase):
    def build(self):
        events = [
            {"t": 0.0, "wall": 1000.0, "kind": "capture-start"},
            {"wall": 1000.0, "kind": "recording-start", "surface": "browser"},
            {"t": 3.0, "wall": 1003.0, "kind": "mark", "name": "stop"},
            {"t": 16.0, "wall": 1016.0, "kind": "capture-end"},
        ]
        s = shots()
        s["shots"][0].update({"out": "stop", "slots": {"center": {"kind": "browser"}}})
        return B.build(s, TIMING, {"run-1": events}, "short")

    def test_the_recording_freezes_at_the_out_mark(self):
        p, _ = self.build()
        shot = p["scenes"][0]["shots"][1]
        self.assertEqual((shot["speed"], shot["slots"]["center"]["freezeAt"]), (1.0, 90))

    def test_a_long_hold_is_a_warning(self):
        _, warnings = self.build()
        self.assertEqual(warnings, ["shot L1.2 shows 3.0s of take run-1 over 8.0s, so its picture holds still for 5.0s; "
                                    "lengthen the driver's pauses there and re-record"])


class Warnings(unittest.TestCase):
    def test_runtime_against_target_is_a_warning(self):
        s = shots()
        s["cuts"]["short"]["target_seconds"] = 30
        _, warnings = B.build(s, TIMING, TAKES, "short")
        self.assertEqual(warnings, ["cut short runs 10s against a 30s target"])


if __name__ == "__main__":
    unittest.main()
