#!/usr/bin/env python3
"""Adversarial tests for the compartment-transcription verifier
(verify-no-transcription.py)."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFIER = ROOT / "scripts/verify-no-transcription.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_no_transcription", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def line(text: str) -> str:
    return f'<text class="dd-compartment-line" x="0" y="0" font-size="10">{text}</text>'


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

    with tempfile.TemporaryDirectory(prefix="verify-no-transcription-") as tmp:
        directory = Path(tmp)

        # A shape-only compartment line (a bare key, no colon or bracket) is legal.
        clean = wrap(line("# id"))
        path = write(directory, "example-clean.html", clean)
        if verifier.check(path):
            raise AssertionError("a bare key compartment line was flagged")
        print("OK: a shape-only compartment line (no colon, no bracket) passes")

        # A field-type transcription with both a colon and a bracket is rejected.
        transcribed = wrap(line("items: List[str]"))
        path = write(directory, "example-transcribed.html", transcribed)
        findings = verifier.check(path)
        if not findings or "transcribes a field type" not in findings[0]:
            raise AssertionError(f"a colon+bracket transcription was not flagged: {findings}")
        print("OK: a colon-and-bracket compartment line is rejected")

        # A colon alone is still rejected.
        colon_only = wrap(line("status: active"))
        path = write(directory, "example-colon.html", colon_only)
        findings = verifier.check(path)
        if not findings or "contains a colon" not in findings[0]:
            raise AssertionError(f"a colon-only line was not flagged: {findings}")
        print("OK: a colon-only compartment line is rejected")

        # A bracket pair alone is still rejected.
        bracket_only = wrap(line("tags(admin)"))
        path = write(directory, "example-bracket.html", bracket_only)
        findings = verifier.check(path)
        if not findings or "contains a bracket pair" not in findings[0]:
            raise AssertionError(f"a bracket-only line was not flagged: {findings}")
        print("OK: a bracket-only compartment line is rejected")

        # Four consecutive compartment lines exceed the three-line cap.
        four_lines = wrap("".join(line(f"field_{i}") for i in range(4)))
        path = write(directory, "example-four-lines.html", four_lines)
        findings = verifier.check(path)
        if not any("exceeds 3 lines" in f for f in findings):
            raise AssertionError(f"a four-line compartment was not capped: {findings}")
        print("OK: a compartment over three lines is rejected")

        # Three lines exactly is fine.
        three_lines = wrap("".join(line(f"field_{i}") for i in range(3)))
        path = write(directory, "example-three-lines.html", three_lines)
        findings = verifier.check(path)
        if any("exceeds" in f for f in findings):
            raise AssertionError(f"exactly three compartment lines was flagged: {findings}")
        print("OK: exactly three compartment lines is not flagged")

        # A file with no compartment-line class at all (every shipped example today) passes.
        no_class = wrap('<text x="0" y="0">id: uuid</text>')
        path = write(directory, "example-no-class.html", no_class)
        if verifier.check(path):
            raise AssertionError("plain text without the compartment-line class was flagged")
        print("OK: text without the dd-compartment-line class is untouched")

    print("All compartment-transcription verifier tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
