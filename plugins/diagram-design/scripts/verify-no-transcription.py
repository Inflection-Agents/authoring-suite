#!/usr/bin/env python3
"""Verify compartment lines never transcribe field types, and never exceed three.

Design review pass 3 (§4.14): "A compartment line containing a colon or a bracket
pair is transcription, not shape, and is rejected." The rule targets the class/entity
member-list convention the code-level type (M2 / Phase 3) will introduce — "Keys are
shape; field types are transcription. A foreign key determines the relationship
structure, so it earns its line; a `varchar(255)` does not." — and caps a compartment
at three lines, since a full field list "triples each box's height" and the diagram
stops being a diagram.

**Written ahead of the convention it protects, and still zero findings today.**
`example-er.html` lists full field-name/type pairs, but as two separate `<text>`
elements per row (name left, type right) rather than one colon-joined string, so it
is not what pass 3 means by "compartment." The code-level type's class preset
(Phase 3) is the first to use `class="dd-compartment-line"`, and it ships with a
single short responsibility phrase per box (`parse source → IR`) — shape, never a
field/type pair — so it stays compliant by construction rather than by retrofit. See
`docs/plans/2026-08-14-design-review-pass-3.md` §3 and the M2 archetype plan.

A compartment is the run of consecutive `dd-compartment-line` elements sharing a
parent `<g>` (or, absent a wrapping group, adjacent in document order) — each such
run is capped at three lines.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "skills/diagram-design/assets"

COMPARTMENT_LINE_RE = re.compile(
    r'<text\b[^>]*\bclass\s*=\s*"[^"]*\bdd-compartment-line\b[^"]*"[^>]*>(.*?)</text>',
    re.IGNORECASE | re.DOTALL,
)
BRACKET_RE = re.compile(r"[\[\](){}]")
MAX_COMPARTMENT_LINES = 3


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def check(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    findings = []
    run_length = 0
    last_end = None

    for match in COMPARTMENT_LINE_RE.finditer(text):
        content = strip_tags(match.group(1)).strip()
        line_no = text.count("\n", 0, match.start()) + 1

        if ":" in content and BRACKET_RE.search(content):
            findings.append(
                f"{path.name}:{line_no}: compartment line transcribes a field type "
                f"(colon and bracket pair) — {content!r}"
            )
        elif ":" in content:
            findings.append(
                f"{path.name}:{line_no}: compartment line contains a colon — {content!r}"
            )
        elif BRACKET_RE.search(content):
            findings.append(
                f"{path.name}:{line_no}: compartment line contains a bracket pair — "
                f"{content!r}"
            )

        # Consecutive lines (no more than a few characters of whitespace between them)
        # belong to the same compartment; a gap of real content starts a new one.
        if last_end is not None and match.start() - last_end < 40:
            run_length += 1
        else:
            run_length = 1
        if run_length > MAX_COMPARTMENT_LINES:
            findings.append(
                f"{path.name}:{line_no}: compartment exceeds {MAX_COMPARTMENT_LINES} "
                f"lines"
            )
        last_end = match.end()

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
