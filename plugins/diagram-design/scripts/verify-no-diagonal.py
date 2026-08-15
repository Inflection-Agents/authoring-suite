#!/usr/bin/env python3
"""Verify no diagonal <line> connector between off-axis nodes.

SKILL.md §6 calls this an automatic fail: "Never use diagonal `<line>` or straight
slanted paths between nodes that don't share an x or y axis." A plain `<line>` whose
endpoints differ on both axes is exactly that.

Two classes of legitimate diagonal `<line>` exist and must not be flagged:

* Icon glyphs — every vendored icon is a self-contained nested `<svg viewBox="0 0 24
  24">...</svg>`, and several (the Kubernetes wheel, among others) draw diagonal
  spokes as part of the pictogram. These sit inside a nested `<svg>`, `<symbol>`, or
  `<marker>`, never as direct children of the diagram's own outer `<svg>`, so masking
  those subtrees before scanning excludes them structurally rather than by name.
* Chart-native diagonals — a radar chart's axis spokes and a scatter plot's optional
  trend line are diagonal by mathematical necessity and are documented as such in
  `references/type-radar.md` and `references/type-scatter.md`. These two types are
  exempted by name; forcing their geometry onto right angles would produce a shape
  unrecognisable as its own type.

See `docs/plans/m1-decision-log.md` D22 for the measurement that found this split —
a naive count over every `<line>` element overstates real defects roughly 7-to-1.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "skills/diagram-design/assets"

# Chart types whose diagonal <line> elements are the documented subject of the type,
# not a connector between nodes.
EXEMPT_STEMS = ("example-radar", "example-scatter")

NESTED_SVG_RE = re.compile(r"<svg\b[^>]*>.*?</svg\s*>", re.IGNORECASE | re.DOTALL)
SYMBOL_RE = re.compile(r"<symbol\b[^>]*>.*?</symbol\s*>", re.IGNORECASE | re.DOTALL)
MARKER_RE = re.compile(r"<marker\b[^>]*>.*?</marker\s*>", re.IGNORECASE | re.DOTALL)
LINE_RE = re.compile(
    r'<line\b[^>]*\bx1\s*=\s*"(?P<x1>-?[\d.]+)"[^>]*\by1\s*=\s*"(?P<y1>-?[\d.]+)"'
    r'[^>]*\bx2\s*=\s*"(?P<x2>-?[\d.]+)"[^>]*\by2\s*=\s*"(?P<y2>-?[\d.]+)"',
    re.IGNORECASE,
)


def blank(match: re.Match[str]) -> str:
    """Replace a matched span with whitespace of the same length, preserving offsets."""
    return re.sub(r"[^\n]", " ", match.group())


def outer_svg_span(text: str) -> tuple[int, int] | None:
    match = re.search(r"<svg\b", text, re.IGNORECASE)
    if match is None:
        return None
    close = re.search(r"</svg\s*>", text[match.start() :], re.IGNORECASE)
    if close is None:
        return None
    return match.start(), match.start() + close.end()


def diagonal_connectors(text: str) -> list[tuple[int, str]]:
    span = outer_svg_span(text)
    if span is None:
        return []
    start, end = span
    outer = text[start:end]
    # The outer <svg ...> tag itself is not a nested icon; blank only what follows its
    # opening tag so a first-line diagonal <line> (there are none, but be exact) is
    # still visible to the scan.
    open_tag_end = re.search(r"<svg\b[^>]*>", outer, re.IGNORECASE).end()
    head, body = outer[:open_tag_end], outer[open_tag_end:]
    body = NESTED_SVG_RE.sub(blank, body)
    body = SYMBOL_RE.sub(blank, body)
    body = MARKER_RE.sub(blank, body)
    masked = head + body

    findings = []
    for match in LINE_RE.finditer(masked):
        x1, y1, x2, y2 = (float(match.group(k)) for k in ("x1", "y1", "x2", "y2"))
        if abs(x1 - x2) > 0.5 and abs(y1 - y2) > 0.5:
            line_no = masked.count("\n", 0, match.start()) + 1
            findings.append((line_no, match.group()))
    return findings


def check(path: Path) -> list[str]:
    if path.stem.startswith(EXEMPT_STEMS):
        return []
    text = path.read_text(encoding="utf-8")
    findings = []
    for line_no, snippet in diagonal_connectors(text):
        findings.append(
            f"{path.name}:{line_no}: diagonal <line> between off-axis nodes — "
            f"{snippet.strip()[:80]}"
        )
    return findings


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
    args = parser.parse_args()

    paths = targets(args)
    if not paths:
        parser.error("pass one or more files, or --all")

    findings: list[str] = []
    for path in paths:
        if not path.exists():
            findings.append(f"{path}: file not found")
            continue
        findings.extend(check(path))

    for finding in findings:
        print(finding)
    print(f"Summary: {len(paths)} file(s) checked, {len(findings)} finding(s).")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
