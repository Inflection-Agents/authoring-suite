#!/usr/bin/env python3
"""Adversarial tests for the accent-budget verifier (verify-accent-budget.py)."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFIER = ROOT / "scripts/verify-accent-budget.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_accent_budget", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def focal_node(x: int, y: int) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="160" height="64" rx="6" class="dd-node" '
        f'fill="var(--dd-paper)"/>'
        f'<rect x="{x}" y="{y}" width="160" height="64" rx="6" class="dd-node" '
        f'fill="var(--dd-accent-tint)" stroke="var(--dd-accent)" stroke-width="1.6"/>'
        f'<rect x="{x+8}" y="{y+6}" width="28" height="12" rx="2" class="dd-tag" '
        f'fill="transparent" stroke="color-mix(in srgb, var(--dd-accent) 50%, transparent)"/>'
    )


def accent_connector(x1: int, y1: int, x2: int, y2: int) -> str:
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="var(--dd-accent)"/>'


def wrap(body: str) -> str:
    return (
        '<svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-labelledby="t-title t-desc">'
        '<title id="t-title">T</title><desc id="t-desc">T.</desc>'
        f"{body}</svg>"
    )


def write(directory: Path, name: str, svg: str) -> Path:
    path = directory / name
    path.write_text(svg, encoding="utf-8")
    return path


def main() -> int:
    verifier = load_verifier()

    with tempfile.TemporaryDirectory(prefix="verify-accent-budget-") as tmp:
        directory = Path(tmp)

        # One focal node's mask+box+tag-chip trio must count as ONE element, not three.
        single = wrap(focal_node(40, 40))
        path = write(directory, "example-single.html", single)
        count = verifier.count_accent_elements(path.read_text(encoding="utf-8"))
        if count != 1:
            raise AssertionError(f"a single node's mask/box/tag trio counted as {count}, not 1")
        print("OK: one focal node's mask+box+tag-chip trio counts once")

        # One node plus one connector: exactly at budget, must pass.
        at_budget = wrap(focal_node(40, 40) + accent_connector(200, 72, 240, 72))
        path = write(directory, "example-at-budget.html", at_budget)
        if verifier.check(path):
            raise AssertionError("exactly 2 accent elements was flagged")
        print("OK: exactly 2 accent elements passes")

        # Two nodes plus one connector: over budget, must fail.
        over_budget = wrap(
            focal_node(40, 40) + focal_node(40, 200) + accent_connector(200, 72, 240, 72)
        )
        path = write(directory, "example-over-budget.html", over_budget)
        findings = verifier.check(path)
        if not findings:
            raise AssertionError("3 accent elements was not flagged")
        print("OK: exceeding the 2-element budget is flagged")

        # A legend swatch referencing accent (for the key, not the diagram) doesn't count.
        with_legend = wrap(
            focal_node(40, 40)
            + accent_connector(200, 72, 240, 72)
            + '<text>LEGEND</text>'
            + '<rect x="40" y="500" width="16" height="12" fill="var(--dd-accent-tint)" '
            'stroke="var(--dd-accent)"/>'
        )
        path = write(directory, "example-with-legend.html", with_legend)
        if verifier.check(path):
            raise AssertionError("a legend swatch after the LEGEND marker was counted")
        print("OK: legend swatches after the LEGEND marker are excluded")

    print("All accent-budget verifier tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
