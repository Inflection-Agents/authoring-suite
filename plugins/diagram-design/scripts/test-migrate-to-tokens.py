#!/usr/bin/env python3
"""Adversarial tests for the hex-to-token codemod.

Each case is a defect the codemod actually hit during the M1 migration. They matter
because the codemod's whole claim is that it preserves pixels, and every failure mode
below is silent: the output still lints, still parses, and still renders — just wrong.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MIGRATE = ROOT / "scripts/migrate-to-tokens.py"


def load_module():
    spec = importlib.util.spec_from_file_location("diagram_design_migrate", MIGRATE)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load migrate-to-tokens.py")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


migrate = load_module()

# Fixtures are built from the *active* skin, so the tests keep working across a reskin —
# the codemod's behaviour is what is under test, not any particular palette.
ROLES = migrate.BUILD_SKINS.read_roles()
LIGHT = {role: values["light"] for role, values in ROLES.items()}
DARK = {role: values["dark"] for role, values in ROLES.items()}


def rgba_of(role: str, alpha: str, variant: dict[str, str] = LIGHT) -> str:
    """`role` at `alpha`, written the way an author would have written it by hand."""
    red, green, blue = migrate.triplet_of(variant[role])
    return f"rgba({red},{green},{blue},{alpha})"


def document(root_block: str, svg_body: str = "", background: str = "") -> str:
    return (
        "<html><head><style>\n"
        f"    :root {{{root_block}}}\n"
        f"    body {{ background: {background}; }}\n"
        "  </style></head><body>\n"
        '<svg role="img" aria-labelledby="t-title t-desc">\n'
        f"{svg_body}\n</svg></body></html>\n"
    )


def run(text: str, name: str = "example-fixture.html") -> tuple[str, object]:
    with tempfile.TemporaryDirectory(prefix="migrate-tokens-") as directory:
        path = Path(directory) / name
        path.write_text(text, encoding="utf-8")
        return migrate.migrate(path)


def main() -> int:
    # 1. Several declarations on one line must all survive. The first version of the
    #    codemod matched line-by-line, folded `--paper`, and silently deleted `--ink`,
    #    `--muted`, and `--soft` along with the rest of the line — 47 of 102 files went
    #    visually wrong, and every one of them still passed the linter.
    packed = (
        f"--paper: {LIGHT['paper']}; --ink: {LIGHT['ink']}; "
        f"--muted: {LIGHT['muted']}; --soft: {LIGHT['soft']};"
    )
    result, _report = run(
        document(packed, '<rect fill="var(--ink)"/>', background=LIGHT["paper"])
    )
    for role in ("paper", "ink", "muted", "soft"):
        if f"var(--dd-{role})" not in result and f"--dd-{role}:" not in result:
            raise AssertionError(f"packed declaration --{role} was lost")
    if "var(--ink)" in result:
        raise AssertionError("alias reference was not retargeted onto the contract")
    print("OK: every declaration on a packed line is preserved and retargeted")

    # 2. A reference left pointing at a deleted alias must be a hard failure, not a
    #    silently unstyled element — an unresolved var() does not fall back to anything.
    try:
        run(
            document(
                f"--paper: {LIGHT['paper']};",
                '<rect fill="var(--nonesuch)"/>',
                background=LIGHT["paper"],
            )
        )
    except SystemExit as error:
        if "dangling" not in str(error):
            raise AssertionError(f"unexpected failure: {error}")
    else:
        raise AssertionError("a dangling custom-property reference was accepted")
    print("OK: a dangling custom-property reference is rejected")

    # 3. The variant is decided by the paper the file paints, not by its name. Five
    #    shipped `-dark` examples render on `#f5f5f5`; reading the name would map their
    #    paper onto `ink` and invert them the moment the skin changed.
    light_named_dark = document(
        f"--paper: {LIGHT['paper']};",
        f'<rect fill="{LIGHT["paper"]}"/>',
        background=LIGHT["paper"],
    )
    _result, report = run(light_named_dark, name="example-fixture-dark.html")
    if report.variant != "light":
        raise AssertionError(
            f"a -dark file painting #f5f5f5 was read as {report.variant}, not light"
        )
    dark = document(
        f"--paper: {DARK['paper']};",
        f'<rect fill="{DARK["paper"]}"/>',
        background=DARK["paper"],
    )
    _result, report = run(dark, name="example-fixture-dark.html")
    if report.variant != "dark":
        raise AssertionError("a file painting the dark paper was not read as dark")
    print("OK: variant is detected from the painted paper, not the filename")

    # 4. color-mix must reproduce the rgba it replaces exactly, including short alphas
    #    written without a leading zero and alphas finer than a percent.
    skin = migrate.Skin("light")
    cases = {
        rgba_of("ink", "0.55"): "color-mix(in srgb, var(--dd-ink) 55%, transparent)",
        rgba_of("ink", "0.018"): "color-mix(in srgb, var(--dd-ink) 1.8%, transparent)",
        LIGHT["rule"].replace("0.", "."): "var(--dd-rule)",
        LIGHT["accent-tint"]: "var(--dd-accent-tint)",
        LIGHT["wash-10"]: "var(--dd-wash-10)",
        LIGHT["accent"].upper(): "var(--dd-accent)",
        "#fff": "var(--dd-node-white)",
    }
    for literal, expected in cases.items():
        actual = skin.substitute(literal)
        if actual != expected:
            raise AssertionError(f"{literal} -> {actual!r}, expected {expected!r}")
    print("OK: exact roles win over color-mix, and alpha formatting round-trips")

    # 5. An off-skin colour is reported and left alone rather than snapped to a
    #    near neighbour.
    result, report = run(
        document(
            f"--paper: {LIGHT['paper']};",
            '<rect fill="#b85450"/>',
            background=LIGHT["paper"],
        )
    )
    if "#b85450" not in result:
        raise AssertionError("an off-skin colour was rewritten instead of reported")
    if not any(literal == "#b85450" for _line, literal in report.unmapped):
        raise AssertionError("an off-skin colour was not reported")
    print("OK: an off-skin colour is left unchanged and reported")

    # 6. The terminal window is a second fixed skin whose literals collide with the
    #    default one's — `#f5f5f5` is terminal-ink there, not paper.
    if not migrate.uses_terminal_skin(Path("example-loop-terminal.html")):
        raise AssertionError("a terminal-skin example was not excluded")
    if migrate.uses_terminal_skin(Path("example-loop.html")):
        raise AssertionError("a default-skin example was excluded")
    print("OK: terminal-skin files are excluded from the contract")

    # 7. Radius classes match the literal corner, and an existing class is merged
    #    rather than clobbered.
    result, _report = run(
        document(
            f"--paper: {LIGHT['paper']};",
            '<rect class="station" rx="6"/><rect rx="2"/><rect rx="8"/><rect rx="3"/>',
            background=LIGHT["paper"],
        )
    )
    for expected in ('class="station dd-node"', 'class="dd-tag"', 'class="dd-container"'):
        if expected not in result:
            raise AssertionError(f"missing radius class: {expected}")
    if 'rx="3"' not in result or result.count("dd-node") < 2:
        raise AssertionError("an unrecognised radius was given a class")
    print("OK: radius classes match the literal rx and merge with existing classes")

    print("All codemod tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
