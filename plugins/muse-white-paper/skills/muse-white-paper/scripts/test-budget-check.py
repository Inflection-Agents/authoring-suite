#!/usr/bin/env python3
"""Failing-first tests for budget-check.py (plan Task 4, step 1).

Run: python3 plugins/muse-white-paper/skills/muse-white-paper/scripts/test-budget-check.py
Exits 0 when every case prints ok, nonzero otherwise.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUDGET_CHECK = HERE / "budget-check.py"
BUDGETS_PATH = HERE.parent / "assets" / "budgets.sample.json"

try:
    _spec = importlib.util.spec_from_file_location("budget_check_impl", BUDGET_CHECK)
    if _spec is None or _spec.loader is None:
        raise FileNotFoundError(BUDGET_CHECK)
    _impl = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_impl)
except FileNotFoundError:
    pass  # implementation not written yet: tests fail with `displacement not defined`
else:
    displacement = _impl.displacement
    check_manifest = _impl.check_manifest
    load_budgets = _impl.load_budgets


def _budgets():
    return json.loads(BUDGETS_PATH.read_text())


def _manifest(total_words, figures, sections=2):
    base, rem = divmod(total_words, sections)
    counts = [base + (1 if i < rem else 0) for i in range(sections)]
    return {
        "sections": [
            {"title": "Section %d" % (i + 1), "words": n}
            for i, n in enumerate(counts)
        ],
        "figures": list(figures),
    }


def test_half_page_figure_displaces_230_words():
    assert displacement("half") == 230


def test_exact_word_cap_passes():
    budgets = _budgets()
    cap = budgets["six_pager"]["prose_cap"] - displacement(0.5)
    result = check_manifest(_manifest(cap, [0.5]), "six_pager", budgets)
    assert result["status"] == "OK", result


def test_over_words_flagged():
    budgets = _budgets()
    cap = budgets["six_pager"]["prose_cap"] - displacement(0.5)
    result = check_manifest(_manifest(cap + 1, [0.5]), "six_pager", budgets)
    assert result["status"] == "over-words", result


def test_exact_area_cap_passes():
    budgets = _budgets()
    figures = [0.5, 0.5, 0.5]  # exactly the 1.5-page six_pager cap
    cap = budgets["six_pager"]["prose_cap"] - sum(
        displacement(f) for f in figures
    )
    result = check_manifest(_manifest(cap, figures), "six_pager", budgets)
    assert result["status"] == "OK", result


def test_over_area_flagged():
    budgets = _budgets()
    result = check_manifest(
        _manifest(100, [0.5, 0.5, 0.5, 0.5]), "six_pager", budgets
    )
    assert result["status"] == "over-area", result


def test_too_many_figures_flagged_as_over_area():
    budgets = _budgets()
    figures = [0.25] * 5  # 1.25 pages but six_pager allows max 4 figures
    result = check_manifest(_manifest(100, figures), "six_pager", budgets)
    assert result["status"] == "over-area", result


def _run_cli(manifest, render):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(manifest, fh)
        path = fh.name
    try:
        return subprocess.run(
            [
                sys.executable,
                str(BUDGET_CHECK),
                path,
                render,
                "--budgets",
                str(BUDGETS_PATH),
            ],
            capture_output=True,
            text=True,
        )
    finally:
        Path(path).unlink(missing_ok=True)


def test_cli_reports_ok_for_named_render():
    budgets = _budgets()
    cap = budgets["two_pager"]["prose_cap"] - displacement(0.5)
    proc = _run_cli(_manifest(cap, [0.5]), "two_pager")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout.startswith("OK"), proc.stdout


def test_cli_flags_over_words_nonzero():
    proc = _run_cli(_manifest(2401, []), "six_pager")
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "over-words" in proc.stdout, proc.stdout


TESTS = [
    test_half_page_figure_displaces_230_words,
    test_exact_word_cap_passes,
    test_over_words_flagged,
    test_exact_area_cap_passes,
    test_over_area_flagged,
    test_too_many_figures_flagged_as_over_area,
    test_cli_reports_ok_for_named_render,
    test_cli_flags_over_words_nonzero,
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
