#!/usr/bin/env python3
"""Tests for cues. Run: python3 -m unittest test_cues (from this folder)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cues as C  # noqa: E402

SCRIPT = """## L1 The promise
> direction, never voiced
A change takes a week. [cue:headline] We fix it on camera. [cue:promise]
"""


def heard(words):
    return [(w, i * 0.5, i * 0.5 + 0.4) for i, w in enumerate(words)]


class Parse(unittest.TestCase):
    def test_scene_text_and_cue_positions(self):
        [scene] = C.parse_script(SCRIPT)
        self.assertEqual((scene.id, scene.title), ("L1", "The promise"))
        self.assertEqual(scene.text, "A change takes a week. We fix it on camera.")
        self.assertEqual(scene.cues, [("headline", 5), ("promise", 10)])

    def test_sentences_and_their_first_words(self):
        [scene] = C.parse_script(SCRIPT)
        self.assertEqual(scene.sentences, [("A change takes a week.", 0), ("We fix it on camera.", 5)])

    def test_malformed_cue_is_never_voiced(self):
        [scene] = C.parse_script("## L1 T\nHello there. [cue:Bad Id] Bye.\n")
        self.assertEqual(scene.text, "Hello there. Bye.")

    def test_bad_heading_does_not_merge_into_previous_scene(self):
        scenes = C.parse_script("## L1 T\nOne.\n## E1a Extra\nTwo.\n")
        self.assertEqual([(s.id, s.text) for s in scenes], [("L1", "One.")])


class Align(unittest.TestCase):
    def test_exact_match(self):
        [scene] = C.parse_script(SCRIPT)
        h = heard("a change takes a week we fix it on camera".split())
        self.assertEqual(C.cue_times(scene, h), {"headline": 2.5, "promise": 4.9})

    def test_misheard_word_keeps_later_cues(self):
        [scene] = C.parse_script(SCRIPT)
        h = heard("a change takes a weak we fix it on camera".split())
        self.assertEqual(C.cue_times(scene, h)["headline"], 2.5)

    def test_dropped_word_is_interpolated(self):
        [scene] = C.parse_script(SCRIPT)
        h = [("a", 0.0, 0.4), ("change", 0.5, 0.9), ("takes", 1.0, 1.4), ("a", 1.5, 1.9),
             ("week", 2.0, 2.4), ("fix", 3.0, 3.4), ("it", 3.5, 3.9), ("on", 4.0, 4.4), ("camera", 4.5, 4.9)]
        self.assertAlmostEqual(C.cue_times(scene, h)["headline"], 2.7, places=3)

    def test_sentence_times(self):
        [scene] = C.parse_script(SCRIPT)
        h = heard("a change takes a week we fix it on camera".split())
        self.assertEqual(C.sentence_times(scene, h),
                         [{"text": "A change takes a week.", "start": 0.0},
                          {"text": "We fix it on camera.", "start": 2.5}])


if __name__ == "__main__":
    unittest.main()
