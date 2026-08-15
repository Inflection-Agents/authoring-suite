#!/usr/bin/env python3
"""Adversarial tests for the tag-consistency verifier (verify-tag-consistency.py)."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFIER = ROOT / "scripts/verify-tag-consistency.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_tag_consistency", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def node(x: int, y: int, w: int = 160, h: int = 64) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" class="dd-node" '
        f'fill="var(--dd-paper)"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" class="dd-node" '
        f'fill="var(--dd-node-white)" stroke="var(--dd-ink)"/>'
        f'<text x="{x + w / 2:g}" y="{y + h / 2:g}" font-size="12">Name</text>'
    )


def tag(x: int, y: int, text: str = "API") -> str:
    return (
        f'<rect x="{x + 8}" y="{y + 6}" width="28" height="12" rx="2" class="dd-tag" '
        f'fill="transparent" stroke="var(--dd-ink)"/>'
        f'<text x="{x + 22}" y="{y + 15}" font-size="7">{text}</text>'
    )


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

    with tempfile.TemporaryDirectory(prefix="verify-tag-consistency-") as tmp:
        directory = Path(tmp)

        # A file with no tags anywhere establishes no convention - not this check's concern.
        no_tags = wrap(node(40, 40) + node(240, 40))
        path = write(directory, "example-no-tags.html", no_tags)
        if verifier.check(path):
            raise AssertionError("a file with zero tags anywhere was flagged")
        print("OK: a file establishing no tag convention is not flagged")

        # A file where every node is tagged passes.
        all_tagged = wrap(node(40, 40) + tag(40, 40) + node(240, 40) + tag(240, 40))
        path = write(directory, "example-all-tagged.html", all_tagged)
        if verifier.check(path):
            raise AssertionError("a fully consistent file was flagged")
        print("OK: a fully tagged file is not flagged")

        # A file where one node is tagged and a comparable one is not: the real defect.
        inconsistent = wrap(node(40, 40) + tag(40, 40) + node(240, 40))
        path = write(directory, "example-inconsistent.html", inconsistent)
        findings = verifier.check(path)
        if not findings:
            raise AssertionError("an inconsistently tagged file was not flagged")
        print("OK: a partially tagged file is flagged")

        # A short (h<56) box that already carries a name + sublabel is exempt.
        short_two_line = (
            '<rect x="40" y="40" width="160" height="48" rx="6" class="dd-node" '
            'fill="var(--dd-paper)"/>'
            '<rect x="40" y="40" width="160" height="48" rx="6" class="dd-node" '
            'fill="var(--dd-node-white)" stroke="var(--dd-ink)"/>'
            '<text x="120" y="60" font-size="12">Name</text>'
            '<text x="120" y="76" font-size="9">sublabel detail</text>'
        )
        short_box_file = wrap(short_two_line + node(240, 40) + tag(240, 40))
        path = write(directory, "example-short-box.html", short_box_file)
        if verifier.check(path):
            raise AssertionError("a short two-line box was not exempted")
        print("OK: a short box with a name and sublabel is exempt")

        # An icon-based kind signal (a nested 24x24 <svg>) counts as tagged.
        icon_node = (
            '<rect x="40" y="40" width="160" height="64" rx="6" class="dd-node" '
            'fill="var(--dd-paper)"/>'
            '<rect x="40" y="40" width="160" height="64" rx="6" class="dd-node" '
            'fill="var(--dd-node-white)" stroke="var(--dd-ink)"/>'
            '<svg x="52" y="56" width="24" height="24" viewBox="0 0 24 24"><path d="M0 0"/></svg>'
            '<text x="120" y="90" font-size="12">Name</text>'
        )
        icon_file = wrap(icon_node + node(240, 40) + tag(240, 40))
        path = write(directory, "example-icon.html", icon_file)
        if verifier.check(path):
            raise AssertionError("an icon-tagged node was flagged despite an equivalent signal")
        print("OK: a nested-icon kind signal counts as tagged")

    print("All tag-consistency verifier tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
