#!/usr/bin/env python3
"""Verify every node in a diagram carries its file's own kind-signal consistently.

This is **not** a universal "every box needs a tag chip" mandate — most of the 32
visual types have no kind-taxonomy concept at all (a pyramid tier, a venn region, a
timeline event), and two — `it-state` and `dp-integration`'s source/consumer sides —
signal kind through an icon and a CSS modifier class instead of a text chip, which is
at least as legible and predates this check. Forcing a chip onto either would be
clutter, not a fix. See `references/primitive-notch.md` and the M1 decision log
(D24, D27, D28) for the full reasoning and the file-by-file record of what was
checked and why.

What this catches instead: a file that has **already** established a tag convention —
at least one node-sized box carries a `dd-tag` chip — but applies it to only some of
its comparably-treated boxes. That is an unambiguous defect regardless of type,
independent of the philosophical question of which types "should" use tags at all.
`example-org-chart.html`'s specialist tier (fixed in the same PR that added this
check) is the case that motivated it: root and pod-owner tiers were tagged, the
specialist tier was not, with no documented reason for the gap.

A node under the 56px short-box floor that already carries a name and a technical
sublabel is exempt — there is no room for a third line, and the fix there is a
reflow, not a chip (see `primitive-notch.md`, "Short boxes").
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "skills/diagram-design/assets"

RECT_RE = re.compile(r'<rect\b([^>]*?)/?>', re.IGNORECASE)
ATTR_RE = re.compile(r'([\w-]+)\s*=\s*"([^"]*)"')
ICON_USE_RE = re.compile(
    r'<use\b[^>]*\bhref\s*=\s*"#ico-[^"]*"[^>]*\btransform\s*=\s*"translate\(\s*'
    r'(-?[\d.]+)[ ,]+(-?[\d.]+)\s*\)"',
    re.IGNORECASE,
)
ICON_SVG_RE = re.compile(
    r'<svg\b[^>]*\bx\s*=\s*"(-?[\d.]+)"[^>]*\by\s*=\s*"(-?[\d.]+)"[^>]*viewBox="0 0 24 24"',
    re.IGNORECASE,
)
SHORT_BOX_FLOOR = 56


def attrs(raw: str) -> dict[str, str]:
    return dict(ATTR_RE.findall(raw))


def num(mapping: dict[str, str], key: str) -> float | None:
    value = mapping.get(key)
    if value is None:
        return None
    try:
        return float(value.rstrip("px"))
    except ValueError:
        return None


def find_boxes(text: str) -> tuple[list[tuple[float, float, float, float]], list[tuple[float, float]]]:
    """Return (deduplicated node boxes, tag-chip anchor points)."""
    nodes: list[tuple[float, float, float, float]] = []
    chips: list[tuple[float, float]] = []
    seen: set[tuple[float, float]] = set()

    for match in RECT_RE.finditer(text):
        a = attrs(match.group(1))
        x, y, w, h = num(a, "x"), num(a, "y"), num(a, "width"), num(a, "height")
        if None in (x, y, w, h):
            continue
        class_attr = a.get("class", "")
        if w <= 90 and 8 <= h <= 16:
            chips.append((x, y))
            continue
        if w > 300 or w < 40 or h < 28 or h > 120:
            continue  # upper bound excludes zone/container rects, which also carry dd-node
        if "dd-node" not in class_attr:
            continue
        if a.get("fill", "").strip().lower() == "transparent":
            continue  # a boundary/annotation outline, not a filled node
        key = (x, y)
        if key in seen:
            continue
        seen.add(key)
        nodes.append((x, y, w, h))

    return nodes, chips


def has_sublabel(text: str, y: float, h: float) -> bool:
    """A node with two text lines already (name + sublabel) has no room for a tag."""
    # Count <text> elements whose y falls inside the box - two or more means name+sublabel.
    count = 0
    for tm in re.finditer(r'<text\b[^>]*\by\s*=\s*"(-?[\d.]+)"', text):
        ty = float(tm.group(1))
        if y <= ty <= y + h:
            count += 1
    return count >= 2


def find_icon_anchors(text: str) -> list[tuple[float, float]]:
    """Icon-based kind signals: a <use> glyph or a nested 24x24 <svg>, near a node's
    top-left. At least as legible as a text chip (SKILL.md's icon primitive) and
    predates this check in it-state and dp-integration's source/consumer sides."""
    anchors = []
    for m in ICON_USE_RE.finditer(text):
        anchors.append((float(m.group(1)), float(m.group(2))))
    for m in ICON_SVG_RE.finditer(text):
        anchors.append((float(m.group(1)), float(m.group(2))))
    return anchors


def check(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    nodes, chips = find_boxes(text)
    if not nodes:
        return []
    icons = find_icon_anchors(text)

    def tagged(x: float, y: float, w: float, h: float) -> bool:
        if any(abs(cx - (x + 8)) <= 10 and abs(cy - (y + 8)) <= 10 for cx, cy in chips):
            return True
        return any(x <= ix <= x + w and y <= iy <= y + h for ix, iy in icons)

    tagged_nodes = [(x, y, w, h) for (x, y, w, h) in nodes if tagged(x, y, w, h)]
    if not tagged_nodes:
        return []  # file establishes no tag convention at all - not this check's concern

    findings = []
    for (x, y, w, h) in nodes:
        if tagged(x, y, w, h):
            continue
        if h < SHORT_BOX_FLOOR and has_sublabel(text, y, h):
            continue  # documented short-box exemption
        findings.append(
            f"{path.name}: node at ({x:g},{y:g}) has no tag chip, but "
            f"{len(tagged_nodes)} other node(s) in this file do"
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
