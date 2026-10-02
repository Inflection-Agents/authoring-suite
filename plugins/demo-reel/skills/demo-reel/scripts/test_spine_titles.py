#!/usr/bin/env python3
"""Tests for spine_titles. Run: python3 -m unittest test_spine_titles."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import spine_titles as S  # noqa: E402

NARRATIVE = """# Narrative

## Leadership cut, about 2 minutes

| Id | Time | Title | On screen | Narration |
|---|---|---|---|---|
| L1 | 0:00 to 0:15 | A trip needs three bookings. | card | x |
| L2 | 0:15 to 0:45 | Each booking can be undone. | card | x |

## Engineering cut, about 4 minutes

| Id | Time | Title | On screen | Narration |
|---|---|---|---|---|
| L1 | 0:00 to 0:15 | (as in the leadership cut) | | |
| E1 | 0:15 to 0:45 | The workflow records each step. | code | x |
| L2 | 0:45 to 1:15 | (as in the leadership cut) | | |
"""


class Titles(unittest.TestCase):
    def test_cuts_in_order_with_shared_titles_resolved(self):
        self.assertEqual(S.cut_titles(NARRATIVE), {
            "leadership": [("L1", "A trip needs three bookings."), ("L2", "Each booking can be undone.")],
            "engineering": [("L1", "A trip needs three bookings."), ("E1", "The workflow records each step."),
                            ("L2", "Each booking can be undone.")],
        })

    def test_spine_markdown(self):
        md = S.spine("leadership", [("L1", "A trip needs three bookings.")])
        self.assertIn("### 1 L1\n- **Title:** A trip needs three bookings.", md)


if __name__ == "__main__":
    unittest.main()
