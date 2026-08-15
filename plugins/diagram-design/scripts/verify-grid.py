#!/usr/bin/env python3
"""Verify every coordinate, size, and gap is divisible by 4 (SKILL.md's structural grid).

**Grandfathered, not retroactive.** Measured against the shipped assets before this gate
existed: 97 of 97 files fail, several thousand violations total — moving every one onto
the grid is a redraw, not a lint fix, and it would change layouts visually with no way to
verify the change was intended (see `docs/plans/2026-08-14-execution-plan.md` §1). The
baseline in `scripts/grid-baseline.txt` is seeded with every file that failed at
introduction. This is a different use of a baseline from the one `CONTRIBUTING.md`
forbids — that rule bans adding a file *to get it through* the linter; seeding a
grandfather list when introducing a rule to a legacy codebase is standard, and the
distinction that makes it honest is that **the list only ever shrinks**: a file leaves it
by becoming grid-clean, never by being re-added.

A new or substantively redrawn file is not on the list and must pass outright.

Radius (`r`, `rx`, `ry`) is exempt by design — `references/primitive-notch.md` and
`style-guide.md`'s Geometry roles table both note that only the radius token sits off
the 4px grid, same as the `rx` attribute it replaces. Path `d` curve/arc coordinates are
out of scope for the same reason a curve's control points aren't meaningfully "on" a
linear grid; this check covers straight-edged primitives (`rect`, `line`, `circle`).

`<defs>` is out of scope too. Every shipped file's `<defs>` holds only the decorative dot
pattern (`cx="1" cy="1" r="0.9"` inside a 22x22 tile — the tile size and dot position are
chosen for a seamless repeat, not for placement on the layout grid) and marker glyphs
(`markerWidth`/`markerHeight` in the marker's own tiny local coordinate space, unrelated to
the canvas). Neither is structural geometry, so scanning them was measuring texture, not
layout — confirmed by every example in the corpus sharing the identical off-grid dot
pattern regardless of how clean its actual node/connector layout is.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "skills/diagram-design/assets"
BASELINE = ROOT / "scripts/grid-baseline.txt"

GRID_ATTRS = ("x", "y", "x1", "y1", "x2", "y2", "width", "height", "cx", "cy")
# A lookbehind, not \b: `stroke-width="1.2"` must not match as a bare `width`, since a
# hyphen is a non-word character and \b alone would happily sit right before "width".
NUM_ATTR_RE = re.compile(
    r'(?<![\w-])(' + "|".join(GRID_ATTRS) + r')\s*=\s*"(-?[\d.]+)"'
)
GRID = 4


DEFS_RE = re.compile(r"<defs\b.*?</defs>", re.IGNORECASE | re.DOTALL)


def off_grid(value: float) -> bool:
    return abs(value - round(value / GRID) * GRID) > 0.01


def blank(match: re.Match) -> str:
    return re.sub(r"[^\n]", " ", match.group())


def check(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    svg_start = text.find("<svg")
    body = text[svg_start:] if svg_start >= 0 else text
    body = DEFS_RE.sub(blank, body)

    findings = []
    for match in NUM_ATTR_RE.finditer(body):
        value = float(match.group(2))
        if off_grid(value):
            line_no = body.count("\n", 0, match.start()) + 1
            findings.append(
                f"{path.name}:{line_no}: {match.group(1)}={match.group(2)} is not "
                f"divisible by {GRID}"
            )
    return findings


def load_baseline() -> set[str]:
    if not BASELINE.exists():
        return set()
    return {
        line.strip()
        for line in BASELINE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def targets(args: argparse.Namespace) -> list[Path]:
    if args.all:
        return sorted(ASSET_DIR.glob("example-*.html")) + sorted(
            ASSET_DIR.glob("template*.html")
        )
    return [Path(p) for p in args.files]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="HTML diagrams to check")
    parser.add_argument("--all", action="store_true", help="check every shipped asset")
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="under --all, skip files listed in scripts/grid-baseline.txt",
    )
    args = parser.parse_args()

    paths = targets(args)
    if not paths:
        parser.error("pass one or more files, or --all")

    baseline = load_baseline() if (args.all and args.baseline) else set()
    skipped = 0
    findings: list[str] = []
    for path in paths:
        if not path.exists():
            findings.append(f"{path}: file not found")
            continue
        if path.name in baseline:
            skipped += 1
            continue
        findings.extend(check(path))

    for finding in findings:
        print(finding)
    print(
        f"Summary: {len(paths)} file(s) checked, {skipped} skipped, "
        f"{len(findings)} finding(s)."
    )
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
