#!/usr/bin/env python3
"""End-to-end fixture for muse-white-paper (plan Task 7).

A six-section sample spine with word counts and 3 figures runs through
budget-check.py (6-pager OK) then cut.py (2-pager within 800 words and
0.5 pages, all titles kept). Reuses both scripts via subprocess; asserts
only on their outputs, no budget or cut logic duplicated here.

Run: python3 plugins/muse-white-paper/skills/muse-white-paper/scripts/test-end-to-end.py
Exits 0 when every case prints ok, nonzero otherwise.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUDGET_CHECK = HERE / "budget-check.py"
CUT = HERE / "cut.py"
BUDGETS_PATH = HERE.parent / "assets" / "budgets.sample.json"

TWO_PAGER_WORD_CAP = 800
TWO_PAGER_AREA_CAP = 0.5


def sample_spine():
    """Six sections (1500 words) plus 3 figures inside the 6-pager caps."""
    return {
        "sections": [
            {"title": "Problem", "words": 300, "priority": 6, "min_words": 50},
            {"title": "Insight", "words": 280, "priority": 5, "min_words": 50},
            {"title": "Approach", "words": 260, "priority": 4, "min_words": 50},
            {"title": "Evidence", "words": 240, "priority": 3, "min_words": 50},
            {"title": "Plan", "words": 220, "priority": 2, "min_words": 50},
            {"title": "Ask", "words": 200, "priority": 1, "min_words": 50},
        ],
        "figures": [0.5, 0.5, 0.25],
    }


def _write_temp(manifest):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(manifest, fh)
    fh.close()
    return Path(fh.name)


def _run(*argv):
    return subprocess.run(
        [sys.executable] + [str(a) for a in argv],
        capture_output=True,
        text=True,
    )


def test_six_pager_passes_budget_check():
    path = _write_temp(sample_spine())
    try:
        proc = _run(BUDGET_CHECK, path, "six_pager", "--budgets", BUDGETS_PATH)
    finally:
        path.unlink(missing_ok=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout.startswith("OK"), proc.stdout


def _cut_spine():
    src = _write_temp(sample_spine())
    out = Path(tempfile.mkdtemp()) / "cut.json"
    try:
        proc = _run(CUT, src, "--budgets", BUDGETS_PATH, "--out", out)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        check = _run(BUDGET_CHECK, out, "two_pager", "--budgets", BUDGETS_PATH)
        result = json.loads(out.read_text(encoding="utf-8"))
    finally:
        src.unlink(missing_ok=True)
    return check, result, out


def test_cut_passes_two_pager_budget_check():
    check, result, out = _cut_spine()
    try:
        assert check.returncode == 0, check.stdout + check.stderr
        assert check.stdout.startswith("OK"), check.stdout
    finally:
        out.unlink(missing_ok=True)


def test_cut_keeps_every_title():
    _, result, out = _cut_spine()
    try:
        expected = [s["title"] for s in sample_spine()["sections"]]
        assert [s["title"] for s in result["sections"]] == expected
    finally:
        out.unlink(missing_ok=True)


def test_cut_holds_word_and_area_caps():
    _, result, out = _cut_spine()
    try:
        words = sum(s["words"] for s in result["sections"])
        area = sum(float(f) for f in result["figures"])
        assert words <= TWO_PAGER_WORD_CAP, words
        assert area <= TWO_PAGER_AREA_CAP + 1e-9, area
    finally:
        out.unlink(missing_ok=True)


TESTS = [
    test_six_pager_passes_budget_check,
    test_cut_passes_two_pager_budget_check,
    test_cut_keeps_every_title,
    test_cut_holds_word_and_area_caps,
]


def main():
    failed = 0
    for test in TESTS:
        try:
            test()
        except Exception as exc:
            failed += 1
            print("FAIL %s: %s: %s" % (test.__name__, type(exc).__name__, exc))
        else:
            print("ok %s" % test.__name__)
    print("%d passed, %d failed" % (len(TESTS) - failed, failed))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
