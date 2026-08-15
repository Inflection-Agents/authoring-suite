#!/usr/bin/env python3
"""Adversarial tests for the diagonal-connector verifier (verify-no-diagonal.py)."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFIER = ROOT / "scripts/verify-no-diagonal.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_no_diagonal", VERIFIER)
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


def main() -> int:
    verifier = load_verifier()

    # A genuine diagonal connector between off-axis nodes must be caught.
    diagonal = wrap('<line x1="10" y1="10" x2="50" y2="60"/>')
    findings = verifier.diagonal_connectors(diagonal)
    if not findings:
        raise AssertionError("a genuine diagonal connector was not flagged")
    print("OK: diagonal connector between off-axis nodes is flagged")

    # Same-x or same-y lines are legal and must not be flagged.
    vertical = wrap('<line x1="10" y1="10" x2="10" y2="60"/>')
    horizontal = wrap('<line x1="10" y1="10" x2="80" y2="10"/>')
    for name, svg in (("vertical", vertical), ("horizontal", horizontal)):
        findings = verifier.diagonal_connectors(svg)
        if findings:
            raise AssertionError(f"a same-axis {name} line was flagged: {findings}")
    print("OK: same-axis lines are not flagged")

    # A diagonal inside a nested icon <svg> (e.g. the Kubernetes wheel) must not be flagged.
    icon_svg = wrap(
        '<svg x="10" y="10" width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">'
        '<line x1="20.2" y1="7.5" x2="14.9" y2="10.5"/>'
        "</svg>"
    )
    findings = verifier.diagonal_connectors(icon_svg)
    if findings:
        raise AssertionError(f"a diagonal line inside a nested icon <svg> was flagged: {findings}")
    print("OK: diagonal lines inside a nested icon <svg> are not flagged")

    # A diagonal inside a <symbol> definition must not be flagged.
    symbol_svg = wrap(
        '<defs><symbol id="ico-x" viewBox="0 0 24 24">'
        '<line x1="2" y1="2" x2="20" y2="20"/>'
        "</symbol></defs>"
    )
    findings = verifier.diagonal_connectors(symbol_svg)
    if findings:
        raise AssertionError(f"a diagonal line inside a <symbol> was flagged: {findings}")
    print("OK: diagonal lines inside a <symbol> definition are not flagged")

    # radar/scatter are exempt by filename, at the check() level (not diagonal_connectors()).
    with tempfile.TemporaryDirectory(prefix="verify-no-diagonal-") as tmp:
        directory = Path(tmp)
        radar_path = directory / "example-radar.html"
        radar_path.write_text(diagonal, encoding="utf-8")
        findings = verifier.check(radar_path)
        if findings:
            raise AssertionError(f"example-radar.html was not exempted: {findings}")
        print("OK: example-radar.html is exempt by name")

        scatter_path = directory / "example-scatter-dark.html"
        scatter_path.write_text(diagonal, encoding="utf-8")
        findings = verifier.check(scatter_path)
        if findings:
            raise AssertionError(f"example-scatter-dark.html was not exempted: {findings}")
        print("OK: example-scatter-dark.html is exempt by name")

        # A non-exempt type with a real diagonal must still fail via check().
        other_path = directory / "example-architecture.html"
        other_path.write_text(diagonal, encoding="utf-8")
        findings = verifier.check(other_path)
        if not findings:
            raise AssertionError("a non-exempt file with a real diagonal was not flagged")
        print("OK: non-exempt types are still checked")

    print("All diagonal-connector verifier tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
