#!/usr/bin/env python3
"""Adversarial tests for the geometry verifier (scripts/verify-geometry.py).

Every check carries both polarities: the defect must be reported, and the legal case that
resembles it must not be. Since v2.4 the predicates live in the shipped skill module and
this wrapper re-exports them, so these tests target the same code an installed plugin
runs (ADR 0011).
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFIER = ROOT / "scripts/verify-geometry.py"
ASSET_DIR = ROOT / "skills/diagram-design/assets"
ARCHITECTURE = ASSET_DIR / "example-architecture.html"
SWIMLANE = ASSET_DIR / "example-swimlane.html"
ZONED = ASSET_DIR / "example-dp-integration.html"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_geometry", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SVG_HEAD = (
    '<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg" role="img" '
    'aria-labelledby="t-title t-desc">'
    "<title id=\"t-title\">T</title><desc id=\"t-desc\">T.</desc>"
)


def document(body: str) -> str:
    return f"<!DOCTYPE html><html><body>{SVG_HEAD}{body}</svg></body></html>"


def main() -> int:
    module = load_verifier()
    failures: list[str] = []

    def check(label: str, source: str, expect_findings: int, checks=None) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            candidate = Path(scratch) / "candidate.html"
            candidate.write_text(source, encoding="utf-8")
            findings = module.check(candidate, checks)
        if len(findings) != expect_findings:
            failures.append(
                f"{label}: expected {expect_findings} finding(s), got "
                f"{len(findings)}: {findings}"
            )
        else:
            print(f"OK: {label}")

    def check_file(label: str, path: Path, expect_findings: int, checks=None) -> None:
        findings = module.check(path, checks)
        if len(findings) != expect_findings:
            failures.append(
                f"{label}: expected {expect_findings} finding(s), got "
                f"{len(findings)}: {findings}"
            )
        else:
            print(f"OK: {label}")

    node = '<rect x="100" y="60" width="160" height="64" rx="6" fill="#f5f5f5" stroke="#333"/>'
    badge = '<rect x="108" y="68" width="32" height="12" rx="2" fill="#f5f5f5"/>'
    zone = '<rect x="80" y="40" width="240" height="120" rx="8" fill="#eee"/>'

    # A label mask straddling a node declared later is the defect being caught.
    check(
        "mask clipped by a later node",
        document('<rect x="240" y="80" width="48" height="12" rx="2" fill="#f5f5f5"/>' + node),
        1,
    )
    # Same geometry, but the node is painted first, so the label stays on top.
    check(
        "mask over an earlier node is legal",
        document(node + '<rect x="240" y="80" width="48" height="12" rx="2" fill="#f5f5f5"/>'),
        0,
    )
    # A badge chip fully inside its own node is legal regardless of order.
    check("badge chip inside a node", document(badge + node), 0)
    # A zone eyebrow overlaps the zone container, which is painted first.
    check(
        "zone eyebrow on a zone container",
        document(zone + '<rect x="160" y="34" width="60" height="12" rx="2" fill="#f5f5f5"/>'),
        0,
    )
    # A mask entirely in open canvas is legal.
    check(
        "mask clear of every node",
        document('<rect x="10" y="10" width="48" height="12" rx="2" fill="#f5f5f5"/>' + node),
        0,
    )
    # Touching within the 1px tolerance is not a finding.
    check(
        "mask abutting a node edge",
        document('<rect x="52" y="80" width="48" height="12" rx="2" fill="#f5f5f5"/>' + node),
        0,
    )

    clipped = ["clipped-mask"]
    check_file("shipped architecture example", ARCHITECTURE, 0, clipped)
    check_file("shipped swimlane example", SWIMLANE, 0, clipped)
    check_file("shipped zoned example", ZONED, 0, clipped)

    # ── masked-edge (SKILL.md §6 rule 2, the geometry ADR 0005 deferred) ─────────────
    stroke = ('<path d="M 100,144 H 300" fill="none" stroke="#888" '
              'marker-end="url(#arrow)"/>')
    check(
        "label mask sitting on its own connector",
        document(stroke + '<rect x="180" y="138" width="48" height="12" fill="#fff"/>'),
        1,
        ["masked-edge"],
    )
    check(
        "label mask cleared 8px above the same connector",
        document(stroke + '<rect x="180" y="124" width="48" height="12" fill="#fff"/>'),
        0,
        ["masked-edge"],
    )
    # A curve's endpoints are exact even though its interior is flattened, so an elbow
    # is caught the same way a straight run is.
    elbow = ('<path d="M 100,200 H 180 Q 188,200 188,208 V 260" fill="none" '
             'stroke="#888" marker-end="url(#arrow)"/>')
    check(
        "label mask sitting on an elbow's horizontal run",
        document(elbow + '<rect x="130" y="194" width="40" height="12" fill="#fff"/>'),
        1,
        ["masked-edge"],
    )
    # A path with no marker is a body, not a connector, and never triggers the check.
    check(
        "mask over a shape outline rather than a connector",
        document('<path d="M 100,144 H 300" fill="none" stroke="#888"/>'
                 + '<rect x="180" y="138" width="48" height="12" fill="#fff"/>'),
        0,
        ["masked-edge"],
    )

    # ── broken-out ──────────────────────────────────────────────────────────────────
    check(
        "node breaking out of the container holding its centre",
        document(zone + '<rect x="200" y="120" width="160" height="64" fill="#fff" stroke="#333"/>'),
        1,
        ["broken-out"],
    )
    check(
        "node wholly inside that container",
        document(zone + '<rect x="100" y="60" width="160" height="64" fill="#fff" stroke="#333"/>'),
        0,
        ["broken-out"],
    )

    # ── a background band is not a node ─────────────────────────────────────────────
    # data-flow lays a full-width, 1.8%-opacity lane behind its steps. Counted as a node
    # it turned every connector crossing it into a corner landing.
    band = '<rect x="0" y="196" width="728" height="80" fill="#fafafa"/>'
    crossing = ('<path d="M582 156 H636 Q644 156 644 164 V204" fill="none" stroke="#888" '
                'marker-end="url(#arrow)"/>')
    check("a connector crossing an unstroked, unclassed band", document(band + crossing),
          0, ["corner-landing"])
    check(
        "the same band given a stroke, so it IS a body",
        document(band.replace('fill="#fafafa"', 'fill="#fafafa" stroke="#333"') + crossing),
        1,
        ["corner-landing"],
    )

    # ── optional checks are off unless asked for ────────────────────────────────────
    floating = ('<path d="M 400,300 H 460" fill="none" stroke="#888" '
                'marker-end="url(#arrow)"/>')
    check("connector in open canvas is silent by default", document(floating), 0)
    check(
        "connector in open canvas is reported when requested",
        document(floating),
        1,
        ["loose-start"],
    )

    if failures:
        print("\nFAILURES:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("All label geometry tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
