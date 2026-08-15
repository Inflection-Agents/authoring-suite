#!/usr/bin/env python3
"""Adversarial tests for the diagram-set spine verifier (verify-set.py)."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFIER = ROOT / "scripts/verify-set.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_set", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def diagram_html(
    id_: str,
    level: str,
    parent: str | None = None,
    subject: str | None = None,
    elements: str = "",
    element_labels: dict[str, str] | None = None,
) -> str:
    meta = [
        f'<meta name="diagram:id" content="{id_}">',
        f'<meta name="diagram:level" content="{level}">',
    ]
    if parent is not None:
        meta.append(f'<meta name="diagram:parent" content="{parent}">')
    if subject is not None:
        meta.append(f'<meta name="diagram:subject" content="{subject}">')
    meta.append(f'<meta name="diagram:elements" content="{elements}">')
    groups = ""
    for element_id, label in (element_labels or {}).items():
        groups += f'<g data-element-id="{element_id}"><text>{label}</text></g>'
    return (
        "<!DOCTYPE html><html><head>"
        + "\n".join(meta)
        + "</head><body><svg>"
        + groups
        + "</svg></body></html>"
    )


def write(directory: Path, name: str, html: str) -> Path:
    path = directory / name
    path.write_text(html, encoding="utf-8")
    return path


def main() -> int:
    verifier = load_verifier()

    with tempfile.TemporaryDirectory(prefix="verify-set-") as tmp:
        directory = Path(tmp)

        # A file with no diagram: meta tags is not part of any set — no findings at all.
        standalone = write(
            directory,
            "standalone.html",
            "<html><head></head><body><svg><text>hi</text></svg></body></html>",
        )
        errors, infos = verifier.check([standalone])
        if errors or infos:
            raise AssertionError(f"a file with no diagram: meta was flagged: {errors + infos}")
        print("OK: a file with no diagram: meta tags is silently skipped")

        # Check 1: parent must resolve.
        orphan = write(
            directory,
            "orphan.html",
            diagram_html("set.child", "component", parent="set.missing-parent"),
        )
        errors, _ = verifier.check([orphan])
        if not any("does not resolve" in e for e in errors):
            raise AssertionError(f"unresolved parent was accepted: {errors}")
        print("OK: an unresolved diagram:parent is rejected")

        # Check 2: subject must appear in the parent's elements.
        parent = write(
            directory,
            "parent2.html",
            diagram_html("set.parent2", "container", elements="a,b,c"),
        )
        bad_child = write(
            directory,
            "child2.html",
            diagram_html("set.child2", "component", parent="set.parent2", subject="not-there"),
        )
        errors, _ = verifier.check([parent, bad_child])
        if not any("does not appear in parent" in e for e in errors):
            raise AssertionError(f"subject not in parent elements was accepted: {errors}")
        print("OK: a diagram:subject absent from the parent's diagram:elements is rejected")

        good_child = write(
            directory,
            "child2ok.html",
            diagram_html("set.child2ok", "component", parent="set.parent2", subject="a"),
        )
        errors, _ = verifier.check([parent, good_child])
        if errors:
            raise AssertionError(f"a valid subject was rejected: {errors}")
        print("OK: a diagram:subject present in the parent's diagram:elements passes")

        # Check 3: legal level descent — ladder skip is rejected, correct rung passes.
        parent3 = write(
            directory, "parent3.html", diagram_html("set.parent3", "context", elements="x")
        )
        skip_child = write(
            directory,
            "skip3.html",
            diagram_html("set.skip3", "component", parent="set.parent3", subject="x"),
        )
        errors, _ = verifier.check([parent3, skip_child])
        if not any("is not exactly one rung below" in e for e in errors):
            raise AssertionError(f"a skipped rung was accepted: {errors}")
        print("OK: a child level more than one rung below its parent is rejected")

        ok_child = write(
            directory,
            "ok3.html",
            diagram_html("set.ok3", "container", parent="set.parent3", subject="x"),
        )
        errors, _ = verifier.check([parent3, ok_child])
        if errors:
            raise AssertionError(f"a correct one-rung descent was rejected: {errors}")
        print("OK: a child exactly one rung below its parent passes")

        # deployment/dynamic attach without a rung constraint.
        deploy_child = write(
            directory,
            "deploy3.html",
            diagram_html("set.deploy3", "deployment", parent="set.parent3", subject="x"),
        )
        errors, _ = verifier.check([parent3, deploy_child])
        if errors:
            raise AssertionError(f"a deployment child was wrongly rung-checked: {errors}")
        print("OK: deployment/dynamic children attach to any declared level with no rung check")

        # Check 4: cross-diagram label consistency. Distinct diagram:id prefixes per pair so
        # this test's roots never coincidentally collide with check 6's set-grouping.
        d1 = write(
            directory,
            "labels1.html",
            diagram_html(
                "lbla.labels1", "container", elements="transform",
                element_labels={"transform": "Transform"},
            ),
        )
        d2 = write(
            directory,
            "labels2.html",
            diagram_html(
                "lblb.labels2", "container", elements="transform",
                element_labels={"transform": "Transformer"},
            ),
        )
        errors, _ = verifier.check([d1, d2])
        if not any("inconsistent labels" in e for e in errors):
            raise AssertionError(f"a renamed shared element was accepted: {errors}")
        print("OK: an element id with different labels across diagrams is rejected")

        d3 = write(
            directory,
            "labels3.html",
            diagram_html(
                "lblc.labels3", "container", elements="transform",
                element_labels={"transform": "Transform"},
            ),
        )
        errors, _ = verifier.check([d1, d3])
        if errors:
            raise AssertionError(f"a consistent shared label was rejected: {errors}")
        print("OK: an element id with the same label across diagrams passes")

        # Check 5: no cycles.
        a = write(directory, "cyc-a.html", diagram_html("cyctest.a", "context", parent="cyctest.b"))
        b = write(directory, "cyc-b.html", diagram_html("cyctest.b", "context", parent="cyctest.a"))
        errors, _ = verifier.check([a, b])
        if not any("cycle in parent graph" in e for e in errors):
            raise AssertionError(f"a parent-graph cycle was accepted: {errors}")
        print("OK: a cycle in the parent graph is rejected")

        # Check 6: exactly one root per declared set (grouped by the id's first dotted
        # segment). Two diagrams claiming the same set, both with no parent, is the real
        # failure; one root with any number of children is valid regardless of set size.
        one_root_a = write(
            directory, "oneroot-a.html", diagram_html("acme.a", "context", elements="p")
        )
        one_root_b = write(
            directory,
            "oneroot-b.html",
            diagram_html("acme.b", "container", parent="acme.a", subject="p"),
        )
        one_root_c = write(
            directory,
            "oneroot-c.html",
            diagram_html("acme.c", "container", parent="acme.a", subject="p"),
        )
        errors, _ = verifier.check([one_root_a, one_root_b, one_root_c])
        if errors:
            raise AssertionError(f"a valid one-root set with two children was flagged: {errors}")
        print("OK: one root with multiple children in the same declared set passes")

        two_roots_a = write(
            directory, "tworoots-a.html", diagram_html("acme2.a", "context", elements="p")
        )
        two_roots_b = write(
            directory, "tworoots-b.html", diagram_html("acme2.b", "context", elements="p")
        )
        errors, _ = verifier.check([two_roots_a, two_roots_b])
        if not any("has 2 root(s)" in e for e in errors):
            raise AssertionError(f"two roots claiming the same set were accepted: {errors}")
        print("OK: two diagrams with no parent claiming the same set are rejected")

        no_root_a = write(
            directory,
            "noroot-a.html",
            diagram_html("acme3.a", "container", parent="acme3.b", subject="p"),
        )
        no_root_b = write(
            directory,
            "noroot-b.html",
            diagram_html("acme3.b", "container", parent="acme3.a", subject="p"),
        )
        errors, _ = verifier.check([no_root_a, no_root_b])
        if not any("has 0 root(s)" in e for e in errors):
            raise AssertionError(f"a set with no root (a same-set cycle) was accepted: {errors}")
        print("OK: a declared set where every member has a parent (zero roots) is rejected")

        lone_a = write(directory, "lone-a.html", diagram_html("lone1.x", "context", elements=""))
        lone_b = write(directory, "lone-b.html", diagram_html("lone2.x", "context", elements=""))
        errors, _ = verifier.check([lone_a, lone_b])
        if errors:
            raise AssertionError(f"two unrelated single-diagram sets were flagged: {errors}")
        print("OK: multiple unrelated single-diagram sets are each accepted as their own root")

        # Check 7 (info): an element never drilled into is reported, not an error.
        info_parent = write(
            directory,
            "info-parent.html",
            diagram_html("set.info-parent", "container", elements="drilled,undrilled"),
        )
        info_child = write(
            directory,
            "info-child.html",
            diagram_html(
                "set.info-child", "component", parent="set.info-parent", subject="drilled"
            ),
        )
        errors, infos = verifier.check([info_parent, info_child])
        if errors:
            raise AssertionError(f"undrilled-element case raised an error, not info: {errors}")
        if not any("undrilled" in i for i in infos):
            raise AssertionError(f"an undrilled element was not reported: {infos}")
        print("OK: an element with no child diagram is reported as info, not an error")

        # Duplicate diagram:id across files.
        dup_a = write(directory, "dup-a.html", diagram_html("set.dup", "context", elements=""))
        dup_b = write(directory, "dup-b.html", diagram_html("set.dup", "context", elements=""))
        errors, _ = verifier.check([dup_a, dup_b])
        if not any("duplicate diagram:id" in e for e in errors):
            raise AssertionError(f"a duplicate diagram:id was accepted: {errors}")
        print("OK: a duplicate diagram:id across files is rejected")

        # HTML comments must not leak a commented-out meta block or element group as live.
        commented = write(
            directory,
            "commented.html",
            "<html><head><!-- "
            + diagram_html("set.commented", "context", elements="x")
            + " --></head><body></body></html>",
        )
        diagram = verifier.parse_diagram(commented)
        if diagram is not None:
            raise AssertionError("a commented-out diagram: meta block was parsed as live")
        print("OK: a commented-out diagram: meta block is not mistaken for a live one")

    print("All diagram-set verifier tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
