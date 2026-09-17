#!/usr/bin/env python3
"""Failing-first tests for cut.py (plan Task 5, step 1).

Run: python3 plugins/muse-white-paper/skills/muse-white-paper/scripts/test-cut.py
Exits 0 when every case prints ok, nonzero otherwise.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUT = HERE / "cut.py"
BUDGET_CHECK = HERE / "budget-check.py"
BUDGETS_PATH = HERE.parent / "assets" / "budgets.sample.json"

try:
    _spec = importlib.util.spec_from_file_location("cut_impl", CUT)
    if _spec is None or _spec.loader is None:
        raise FileNotFoundError(CUT)
    _impl = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_impl)
except FileNotFoundError:
    pass  # implementation not written yet: tests fail with `kept_titles not defined`
else:
    cut_manifest = _impl.cut_manifest
    kept_titles = _impl.kept_titles
    all_titles = _impl.all_titles

try:
    _bspec = importlib.util.spec_from_file_location(
        "budget_check_impl", BUDGET_CHECK
    )
    _bimpl = importlib.util.module_from_spec(_bspec)
    _bspec.loader.exec_module(_bimpl)
except FileNotFoundError:
    _bimpl = None


def _budgets():
    return json.loads(BUDGETS_PATH.read_text())


def long_spine():
    return {
        "sections": [
            {"title": "Problem", "words": 300, "priority": 6},
            {"title": "Insight", "words": 250, "priority": 5},
            {"title": "Approach", "words": 200, "priority": 4},
            {"title": "Evidence", "words": 150, "priority": 3},
            {"title": "Plan", "words": 100, "priority": 2},
            {"title": "Ask", "words": 50, "priority": 1},
        ],
        "figures": [0.25, 0.25, 0.5, 0.5],
    }


def test_cut_keeps_every_title():
    assert kept_titles(long_spine()) == all_titles(long_spine())


def test_figure_cap_held():
    result = cut_manifest(long_spine(), _budgets())
    figures = result["figures"]
    cap = _budgets()["two_pager"]
    assert len(figures) <= cap["max_figures"], figures
    assert sum(float(f) for f in figures) <= cap["figure_cap_pages"] + 1e-9, figures


def test_drops_lowest_priority_first():
    manifest = {
        "sections": [
            {"title": "Low", "words": 450, "priority": 1},
            {"title": "High", "words": 400, "priority": 2},
        ],
        "figures": [],
    }
    result = cut_manifest(manifest, _budgets())
    by_title = {s["title"]: s["words"] for s in result["sections"]}
    assert by_title["Low"] == 0, by_title
    assert by_title["High"] == 400, by_title


def test_ties_broken_by_longest_body():
    manifest = {
        "sections": [
            {"title": "Long", "words": 500, "priority": 1},
            {"title": "Short", "words": 300, "priority": 1},
            {"title": "Keep", "words": 100, "priority": 9},
        ],
        "figures": [],
    }
    result = cut_manifest(manifest, _budgets())
    by_title = {s["title"]: s["words"] for s in result["sections"]}
    assert by_title["Long"] == 0, by_title
    assert by_title["Short"] == 300, by_title


def test_cut_result_passes_budget_check():
    assert _bimpl is not None, "budget-check.py missing"
    result = cut_manifest(long_spine(), _budgets())
    check = _bimpl.check_manifest(result, "two_pager", _budgets())
    assert check["status"] == "OK", check


def _run_cli(manifest):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(manifest, fh)
        path = fh.name
    try:
        return subprocess.run(
            [sys.executable, str(CUT), path, "--budgets", str(BUDGETS_PATH)],
            capture_output=True,
            text=True,
        )
    finally:
        Path(path).unlink(missing_ok=True)


def test_cli_success_keeps_titles():
    proc = _run_cli(long_spine())
    assert proc.returncode == 0, proc.stdout + proc.stderr
    result = json.loads(proc.stdout)
    assert [s["title"] for s in result["sections"]] == all_titles(long_spine())


def test_cli_overrun_exits_nonzero_naming_overrun():
    manifest = {
        "sections": [
            {"title": "S%d" % i, "words": 300, "priority": i, "min_words": 250}
            for i in range(4)
        ],
        "figures": [],
    }
    proc = _run_cli(manifest)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "over-words" in proc.stdout + proc.stderr, proc.stdout + proc.stderr


TESTS = [
    test_cut_keeps_every_title,
    test_figure_cap_held,
    test_drops_lowest_priority_first,
    test_ties_broken_by_longest_body,
    test_cut_result_passes_budget_check,
    test_cli_success_keeps_titles,
    test_cli_overrun_exits_nonzero_naming_overrun,
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
