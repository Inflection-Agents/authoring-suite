#!/usr/bin/env python3
"""Verify a diagram spends its accent on at most 2 elements — nodes and connectors
counted as distinct semantic things, not as raw colour occurrences.

**The naive metric is wrong, and the execution plan says so directly** (§1): counting
occurrences of the accent hex "triple-counts a single accent node" — a focal box's mask
rect, styled rect, tag-chip stroke, and name text can all reference `var(--dd-accent)`
for one visual element. This script counts instead:

* **Nodes** — `<rect>` elements at least 28x28 (excludes tag chips and legend
  swatches), deduplicated by position, so a node's mask-and-styled-box pair or a
  notched mask-and-path pair counts once.
* **Connectors** — `<line>`/`<path>` elements whose *own* stroke is the accent
  (`var(--dd-accent)`, not a tint), deduplicated by shape.

Legend swatches are excluded by cutting the scan off at the `>LEGEND<` marker every
shipped example uses for its key strip.

**Grandfathered, like the grid check, for a reason specific to connectors.** Measured
against the shipped assets: 18 of 97 exceed 2, and most exceed by exactly one distinct
`<path>` — because a single accent-highlighted flow that bends around another connector
or changes direction through a Q-bezier corner is drawn as two consecutive path
elements, which a reader perceives as one continuous highlighted route, not two
independent accent decisions. Distinguishing "two segments of one flow" from "two
unrelated accent connectors" requires tracing endpoint adjacency across elements, which
this script does not attempt. `scripts/accent-baseline.txt` is seeded with every file
that exceeds the budget today; new files are held to it without exemption. See the M1
decision log for the full re-measurement this script replaces the plan's original
metric with.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "skills/diagram-design/assets"
BASELINE = ROOT / "scripts/accent-baseline.txt"

RECT_RE = re.compile(r"<rect\b([^>]*?)/?>", re.IGNORECASE)
LINE_RE = re.compile(r"<line\b([^>]*?)/?>", re.IGNORECASE)
PATH_RE = re.compile(r"<path\b([^>]*?)/?>", re.IGNORECASE)
ATTR_RE = re.compile(r'([\w-]+)\s*=\s*"([^"]*)"')
MAX_ACCENT_ELEMENTS = 2


def attrs(raw: str) -> dict[str, str]:
    return dict(ATTR_RE.findall(raw))


def is_accent_fill_or_stroke(a: dict[str, str]) -> bool:
    fill, stroke = a.get("fill", ""), a.get("stroke", "")
    return (
        "var(--dd-accent)" in fill
        or "var(--dd-accent-tint)" in fill
        or "var(--dd-accent)" in stroke
    )


def diagram_body(text: str) -> str:
    legend = text.find(">LEGEND<")
    return text[:legend] if legend > 0 else text


def count_accent_elements(text: str) -> int:
    body = diagram_body(text)

    node_positions: set[tuple[str | None, str | None]] = set()
    for match in RECT_RE.finditer(body):
        a = attrs(match.group(1))
        try:
            w, h = float(a.get("width", "0") or 0), float(a.get("height", "0") or 0)
        except ValueError:
            continue
        if w < 28 or h < 28:
            continue  # a tag chip or legend swatch, not an independent node
        if is_accent_fill_or_stroke(a):
            node_positions.add((a.get("x"), a.get("y")))

    connector_shapes: set[object] = set()
    for match in list(LINE_RE.finditer(body)) + list(PATH_RE.finditer(body)):
        a = attrs(match.group(1))
        if "var(--dd-accent)" in a.get("stroke", ""):
            key = a.get("d") or (a.get("x1"), a.get("y1"), a.get("x2"), a.get("y2"))
            connector_shapes.add(key)

    return len(node_positions) + len(connector_shapes)


def check(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    count = count_accent_elements(text)
    if count > MAX_ACCENT_ELEMENTS:
        return [
            f"{path.name}: {count} distinct accent element(s) (nodes + connectors), "
            f"budget is {MAX_ACCENT_ELEMENTS}"
        ]
    return []


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
        help="under --all, skip files listed in scripts/accent-baseline.txt",
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
