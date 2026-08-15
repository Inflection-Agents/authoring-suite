#!/usr/bin/env python3
"""Adversarial tests for the structural grid verifier (verify-grid.py)."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFIER = ROOT / "scripts/verify-grid.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_grid", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def wrap(body: str) -> str:
    return (
        '<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg" role="img" '
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

    with tempfile.TemporaryDirectory(prefix="verify-grid-") as tmp:
        directory = Path(tmp)

        on_grid = wrap('<rect x="40" y="40" width="160" height="64"/>')
        path = write(directory, "example-on-grid.html", on_grid)
        if verifier.check(path):
            raise AssertionError("grid-aligned coordinates were flagged")
        print("OK: coordinates divisible by 4 pass")

        off_grid = wrap('<rect x="41" y="40" width="160" height="64"/>')
        path = write(directory, "example-off-grid.html", off_grid)
        findings = verifier.check(path)
        if not findings or "x=41" not in findings[0]:
            raise AssertionError(f"an off-grid x was not flagged: {findings}")
        print("OK: an off-grid coordinate is flagged")

        # rx/ry/r are exempt - only x/y/width/height/x1/y1/x2/y2/cx/cy are checked.
        radius_only = wrap('<rect x="40" y="40" width="160" height="64" rx="2" ry="3"/>')
        path = write(directory, "example-radius.html", radius_only)
        if verifier.check(path):
            raise AssertionError("an off-grid rx/ry was flagged, but radius is exempt")
        print("OK: rx/ry/r are exempt from the grid check")

        # stroke-width (and any hyphenated compound ending in a grid attr name) must not
        # be mistaken for a bare `width` — a hyphen is a non-word char, so \b alone would
        # sit right before "width" inside "stroke-width".
        compound_attr = wrap(
            '<rect x="40" y="40" width="160" height="64" stroke-width="1.2"/>'
        )
        path = write(directory, "example-compound-attr.html", compound_attr)
        if verifier.check(path):
            raise AssertionError("stroke-width was mistaken for a bare width attribute")
        print("OK: stroke-width is not mistaken for width")

        # <defs> holds the decorative dot pattern and marker glyphs, not structural
        # geometry — its off-grid cx/cy/width/height must not be flagged.
        defs_only = wrap(
            '<defs><pattern id="dots" width="22" height="22">'
            '<circle cx="1" cy="1" r="0.9"/></pattern></defs>'
            '<rect x="40" y="40" width="160" height="64"/>'
        )
        path = write(directory, "example-defs.html", defs_only)
        if verifier.check(path):
            raise AssertionError("off-grid coordinates inside <defs> were flagged")
        print("OK: <defs> content (patterns, markers) is exempt from the grid check")

        # off_grid() itself: boundary values.
        if verifier.off_grid(4.0) or verifier.off_grid(0.0) or verifier.off_grid(-8.0):
            raise AssertionError("a value exactly on the grid was flagged")
        if not verifier.off_grid(4.5) or not verifier.off_grid(-3.0):
            raise AssertionError("a value off the grid was not flagged")
        print("OK: off_grid() boundary values are correct")

    print("All grid verifier tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
