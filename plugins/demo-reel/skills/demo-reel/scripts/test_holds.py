#!/usr/bin/env python3
"""Tests for hold lines in the script and silence inserted into narration. Run: python3 -m unittest test_holds."""
import struct
import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cues as C  # noqa: E402
import holds as H  # noqa: E402
import verify_shots as V  # noqa: E402

SCRIPT = """## L1 T
First sentence here.
> hold: 2s
Second one. [cue:b] Third.
> hold: 1.5s
"""


class Parse(unittest.TestCase):
    def test_holds_by_word_position(self):
        [scene] = C.parse_script(SCRIPT)
        self.assertEqual(scene.holds, [(2.0, 3), (1.5, 6)])
        self.assertEqual(scene.text, "First sentence here. Second one. Third.")

    def test_malformed_hold_is_flagged(self):
        _, problems = V.parse_headings("## L1 T\nWords.\n> hold 3s\n")
        self.assertIn("line 3: hold line '> hold 3s' must read like '> hold: 3s'", problems)


class Apply(unittest.TestCase):
    words = [{"word": w, "start": s, "end": s + 0.4} for w, s in
             [("First", 0.0), ("sentence", 0.5), ("here.", 1.0), ("Second", 2.0), ("one.", 2.5), ("Third.", 3.0)]]

    def test_words_after_a_hold_shift_by_its_length(self):
        shifted, inserts = H.apply_holds(self.words, [(2.0, 3)], duration=3.6)
        self.assertEqual(inserts, [(1.4, 2.0)])
        self.assertEqual([w["start"] for w in shifted], [0.0, 0.5, 1.0, 4.0, 4.5, 5.0])

    def test_a_hold_lands_after_its_sentence_when_the_transcript_writes_numbers_as_digits(self):
        heard = [{"word": w, "start": s, "end": s + 0.4} for w, s in
                 [("A", 0.0), ("queue", 0.5), ("of", 1.0), ("312", 1.5), ("drains.", 2.0), ("Then", 3.0), ("the", 3.5),
                  ("worker", 4.0), ("stops.", 4.5)]]
        script = "A queue of three hundred and twelve drains. Then the worker stops.".split()
        shifted, inserts = H.apply_holds(heard, [(2.0, 8)], duration=5.0, script_words=script)
        self.assertEqual(inserts, [(2.4, 2.0)])
        self.assertEqual(shifted[5]["start"], 5.0)

    def test_hold_at_the_end_inserts_trailing_silence(self):
        shifted, inserts = H.apply_holds(self.words, [(1.5, 6)], duration=3.6)
        self.assertEqual(inserts, [(3.6, 1.5)])
        self.assertEqual(shifted, self.words)

    def test_silence_inserted_into_a_wav(self):
        d = Path(tempfile.mkdtemp())
        src = d / "in.wav"
        with wave.open(str(src), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(1000)
            w.writeframes(struct.pack("<1000h", *([1000] * 1000)))
        H.insert_silence(src, src, [(0.5, 0.25)])
        with wave.open(str(src), "rb") as w:
            self.assertEqual(w.getnframes(), 1250)
            frames = struct.unpack(f"<{w.getnframes()}h", w.readframes(w.getnframes()))
        self.assertEqual(frames[499:502], (1000, 0, 0))
        self.assertEqual(frames[749:751], (0, 1000))


if __name__ == "__main__":
    unittest.main()
