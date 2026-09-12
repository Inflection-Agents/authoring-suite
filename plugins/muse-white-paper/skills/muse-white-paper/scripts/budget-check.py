#!/usr/bin/env python3
"""Check a manuscript manifest against word and figure-area budgets.

Reads a manuscript manifest (section word counts plus figure sizes in page
fractions) and reports over-words, over-area, or OK for the named render.
Pure stdlib; callers pass word counts in, no NLP word counter.

Manifest shape: {"sections": [{"title": str, "words": int}, ...],
                 "figures": [0.5, ...]} (a figure may also be a dict
with a size/pages/fraction/area key).

Usage: budget-check.py MANIFEST RENDER [--budgets BUDGETS_JSON]
Exit 0 on OK, 1 over budget, 2 usage error.
"""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_BUDGETS = Path(__file__).resolve().parent.parent / "assets" / "budgets.sample.json"

_RENDER_ALIASES = {
    "six_pager": "six_pager",
    "six-pager": "six_pager",
    "6-pager": "six_pager",
    "6pager": "six_pager",
    "two_pager": "two_pager",
    "two-pager": "two_pager",
    "2-pager": "two_pager",
    "2pager": "two_pager",
}

_EPS = 1e-9


def load_budgets(path=DEFAULT_BUDGETS):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def displacement(size, per_half_page_words=230):
    """Words displaced by one figure; scales linearly from the half-page unit."""
    if isinstance(size, str):
        key = size.strip().lower().replace("-", " ").replace("_", " ")
        if key in ("half", "half page", "0.5"):
            frac = 0.5
        elif key in ("quarter", "quarter page", "0.25"):
            frac = 0.25
        else:
            try:
                frac = float(key)
            except ValueError:
                raise ValueError("unknown figure size: %r" % (size,))
    else:
        frac = float(size)
    if frac < 0:
        raise ValueError("figure size cannot be negative: %r" % (size,))
    return int(round(frac * 2 * per_half_page_words))


def _figure_pages(entry):
    if isinstance(entry, (int, float)):
        return float(entry)
    if isinstance(entry, dict):
        for key in ("size", "pages", "fraction", "area"):
            if key in entry:
                return float(entry[key])
        raise ValueError("figure entry has no size: %r" % (entry,))
    if isinstance(entry, str):
        return float(entry)
    raise ValueError("bad figure entry: %r" % (entry,))


def _section_words(entry):
    if isinstance(entry, (int, float)):
        return int(entry)
    if isinstance(entry, dict):
        for key in ("words", "word_count", "count"):
            if key in entry:
                return int(entry[key])
        raise ValueError("section entry has no word count: %r" % (entry,))
    raise ValueError("bad section entry: %r" % (entry,))


def check_manifest(manifest, render, budgets):
    """Return a result dict whose status is OK, over-words, or over-area."""
    render = _RENDER_ALIASES.get(render, render)
    try:
        cap = budgets[render]
    except KeyError:
        raise ValueError("unknown render: %r" % (render,))
    prose_cap = int(cap["prose_cap"])
    area_cap = float(cap["figure_cap_pages"])
    max_figs = int(cap["max_figures"])
    per_half = int(budgets.get("displacement_per_half_page_words", 230))

    sections = manifest.get("sections", [])
    figures = manifest.get("figures", [])
    total_words = sum(_section_words(s) for s in sections)
    sizes = [_figure_pages(f) for f in figures]
    total_area = sum(sizes)
    # Effective prose cap shrinks per figure used: 2400 minus 230 per half page.
    displaced = sum(displacement(s, per_half) for s in sizes)
    effective_cap = prose_cap - displaced

    if total_words > effective_cap:
        status = "over-words"
    elif (
        total_area - area_cap > _EPS
        or len(sizes) > max_figs
        or any(s - 0.5 > _EPS for s in sizes)
    ):
        status = "over-area"
    else:
        status = "OK"
    return {
        "render": render,
        "status": status,
        "words": total_words,
        "prose_cap": prose_cap,
        "displaced_words": displaced,
        "effective_prose_cap": effective_cap,
        "figure_area": total_area,
        "figure_cap_pages": area_cap,
        "figures": len(sizes),
        "max_figures": max_figs,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check manuscript budgets.")
    parser.add_argument("manifest", help="path to manuscript manifest JSON")
    parser.add_argument("render", help="six_pager or two_pager")
    parser.add_argument("--budgets", default=str(DEFAULT_BUDGETS))
    args = parser.parse_args(argv)
    try:
        budgets = load_budgets(args.budgets)
        with open(args.manifest, encoding="utf-8") as fh:
            manifest = json.load(fh)
        result = check_manifest(manifest, args.render, budgets)
    except (OSError, ValueError, KeyError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    print(
        "%(status)s: %(render)s words %(words)d/%(effective_prose_cap)d "
        "(cap %(prose_cap)d, displaced %(displaced_words)d) "
        "area %(figure_area)g/%(figure_cap_pages)g "
        "figures %(figures)d/%(max_figures)d" % result
    )
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
