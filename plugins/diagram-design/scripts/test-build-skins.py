#!/usr/bin/env python3
"""Regression tests for skin generation from the style guide."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "scripts" / "build-skins.py"


def load_build_module():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("diagram_design_build_skins", BUILD)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load build-skins.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    build_skins = load_build_module()

    roles = build_skins.read_roles()
    css = build_skins.render_skin(roles, variant="light")

    if "--dd-paper:" not in css:
        raise AssertionError(f"colour role missing from generated skin:\n{css}")
    if "--dd-wash-5:" not in css:
        raise AssertionError("wash role missing from generated skin")
    if "--dd-radius-node:" not in css:
        raise AssertionError("geometry role missing from generated skin")
    if ":root{" not in css.replace(" ", ""):
        raise AssertionError("generated skin is not wrapped in a :root block")

    # Every role the contract declares must be emitted — a half-written skin must not build.
    for role in build_skins.CONTRACT:
        if f"--dd-{role}:" not in css:
            raise AssertionError(f"contract role {role!r} was not emitted")

    print(f"PASS: skin generation emits all {len(build_skins.CONTRACT)} contract roles")

    # Values must be clean: no stray backticks, annotations, or empty declarations.
    for variant in ("light", "dark"):
        for role in build_skins.CONTRACT:
            value = roles[role][variant]
            if not value:
                raise AssertionError(f"{role} has no {variant} value")
            if "`" in value or "(" in value and not value.startswith("rgba("):
                raise AssertionError(
                    f"{role} {variant} value is not a bare token value: {value!r}"
                )
    print("PASS: every contract value parses to a bare CSS value in both variants")

    # The dark variant must differ from light, or the tables were misread.
    dark = build_skins.render_skin(roles, variant="dark")
    if dark == css:
        raise AssertionError("dark skin is identical to light — table columns misread")
    print("PASS: light and dark variants are distinct")

    # A style guide missing a contract role must fail the build, not emit a partial skin.
    partial = {role: values for role, values in roles.items() if role != "accent"}
    try:
        build_skins.render_skin(partial, variant="light")
    except SystemExit as error:
        if "accent" not in str(error):
            raise AssertionError(f"missing-role failure did not name the role: {error}")
    else:
        raise AssertionError("a style guide missing 'accent' was accepted")
    print("PASS: a half-written skin is rejected")

    # The generated files on disk must match what the builder produces right now.
    for variant in ("light", "dark"):
        target = build_skins.OUT_DIR / f"active-{variant}.tokens.css"
        if not target.exists():
            raise AssertionError(f"generated skin {target.name} is missing; run build-skins.py")
        if target.read_text(encoding="utf-8") != build_skins.render_skin(roles, variant):
            raise AssertionError(
                f"{target.name} is stale; run scripts/build-skins.py and commit the result"
            )
    print("PASS: generated skin files on disk are up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
