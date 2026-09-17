#!/usr/bin/env python3
"""Derive the 2-pager manifest from the 6-pager manifest.

Drops section bodies lowest-priority first (ties broken by longest body),
keeps every title, and carries over at most 2 figures within 0.5 pages.
Exits nonzero naming the overrun when even titles plus minimum bodies
exceed the caps. Pure stdlib.

Manifest shape: {"sections": [{"title": str, "words": int,
                 "priority": int, "min_words": int (optional, default 0)}],
                 "figures": [0.5, ...]} (a figure may also be a dict
with a size/pages/fraction/area key).

Usage: cut.py MANIFEST [--budgets BUDGETS_JSON] [--out OUT_JSON]
Exit 0 on success (cut manifest on stdout or in OUT_JSON),
1 when caps cannot be met, 2 on usage error.
"""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUDGET_CHECK = HERE / "budget-check.py"
DEFAULT_BUDGETS = HERE.parent / "assets" / "budgets.sample.json"

_EPS = 1e-9


def _budget_impl():
    spec = importlib.util.spec_from_file_location("budget_check_impl", BUDGET_CHECK)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(BUDGET_CHECK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class CutOverrun(ValueError):
    """Raised when caps cannot be met; `kind` names the overrun."""

    def __init__(self, kind, message):
        super().__init__(message)
        self.kind = kind


def all_titles(manifest):
    """Every section title in the manifest, in order."""
    return [s["title"] for s in manifest.get("sections", [])]


def _figure_pages(entry):
    if isinstance(entry, (int, float)):
        return float(entry)
    if isinstance(entry, dict):
        for key in ("size", "pages", "fraction", "area"):
            if key in entry:
                return float(entry[key])
        raise ValueError("figure entry has no size: %r" % (entry,))
    return float(entry)


def _section_min_words(section):
    for key in ("min_words", "min", "minimum"):
        if key in section:
            return int(section[key])
    return 0


def _section_priority(section):
    return int(section.get("priority", 0))


def _carry_figures(figures, max_figs, area_cap):
    """Greedily carry figures in manifest order within count and area caps."""
    kept = []
    area = 0.0
    for entry in figures:
        size = _figure_pages(entry)
        if len(kept) >= max_figs or area + size - area_cap > _EPS:
            continue
        kept.append(entry)
        area += size
    return kept


def cut_manifest(manifest, budgets):
    """Cut the 6-pager manifest down to the two-pager budgets.

    Raises CutOverrun (naming over-words) when even titles plus minimum
    bodies exceed the effective prose cap.
    """
    impl = _budget_impl()
    cap = budgets["two_pager"]
    prose_cap = int(cap["prose_cap"])
    area_cap = float(cap["figure_cap_pages"])
    max_figs = int(cap["max_figures"])
    per_half = int(budgets.get("displacement_per_half_page_words", 230))

    kept_figures = _carry_figures(manifest.get("figures", []), max_figs, area_cap)
    displaced = sum(
        impl.displacement(_figure_pages(f), per_half) for f in kept_figures
    )
    effective_cap = prose_cap - displaced

    sections = [dict(s) for s in manifest.get("sections", [])]
    for section in sections:
        section["words"] = int(section.get("words", 0))
    total = sum(s["words"] for s in sections)

    while total - effective_cap > _EPS:
        droppable = [s for s in sections if s["words"] > _section_min_words(s)]
        if not droppable:
            raise CutOverrun(
                "over-words",
                "over-words: titles plus minimum bodies need %d words, "
                "cap is %d (prose %d, displaced %d)"
                % (total, effective_cap, prose_cap, displaced),
            )
        victim = min(
            droppable, key=lambda s: (_section_priority(s), -s["words"])
        )
        total -= victim["words"] - _section_min_words(victim)
        victim["words"] = _section_min_words(victim)

    return {"sections": sections, "figures": kept_figures}


def kept_titles(manifest, budgets=None):
    """Titles surviving the cut; every input title must survive."""
    if budgets is None:
        budgets = _budget_impl().load_budgets(str(DEFAULT_BUDGETS))
    return all_titles(cut_manifest(manifest, budgets))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Derive the 2-pager manifest.")
    parser.add_argument("manifest", help="path to 6-pager manifest JSON")
    parser.add_argument("--budgets", default=str(DEFAULT_BUDGETS))
    parser.add_argument("--out", default=None, help="output path (default stdout)")
    args = parser.parse_args(argv)
    try:
        impl = _budget_impl()
        budgets = impl.load_budgets(args.budgets)
        with open(args.manifest, encoding="utf-8") as fh:
            manifest = json.load(fh)
        result = cut_manifest(manifest, budgets)
    except CutOverrun as exc:
        print("%s: %s" % (exc.kind, exc), file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    text = json.dumps(result, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
