#!/usr/bin/env python3
"""Rewrite hard-coded skin colours in diagram HTML as `--dd-*` token references.

The migration is **value-preserving by construction**: every substitution resolves to the
byte-identical colour it replaced, because the token values come from the same
`style-guide.md` tables the literals were copied from. That is what makes a 102-file diff
reviewable — the proof is a rasterized before/after comparison, not 102 read-throughs.

Three substitution forms are used, in order of preference:

1. A literal that exactly equals a contract role's value becomes ``var(--dd-<role>)``.
2. A translucent literal whose RGB triplet belongs to a role becomes
   ``color-mix(in srgb, var(--dd-<role>) <alpha>%, transparent)``. Mixing with
   ``transparent`` in sRGB reproduces the source ``rgba()`` exactly.
3. Anything else is left alone and reported, so an unrecognised colour is a visible
   decision rather than a silent guess.

The variant (light or dark) matters because the same literal means different roles in each:
``#f5f5f5`` is *paper* in a light diagram and *ink* in a dark one. It is detected from the
paper the file actually paints, **not** from its name — five shipped ``-dark`` examples
render on light paper, and trusting the name would invert them.

Usage:
    python3 scripts/migrate-to-tokens.py [--dry-run] [--quiet] FILE [FILE ...]
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIN_DIR = ROOT / "skills/diagram-design/assets/skins"

HEX_RE = re.compile(
    r"(?<![\w-])#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-fA-F])"
)
RGBA_RE = re.compile(
    r"rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([0-9]*\.?[0-9]+)\s*\)",
    re.IGNORECASE,
)
ROOT_BLOCK_RE = re.compile(r"(:root\s*\{)(?P<body>[^}]*)(\})")
DECL_RE = re.compile(r"(?P<name>--[a-z0-9-]+)\s*:\s*(?P<value>[^;}]*?)\s*(?:;|$)")
COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
VAR_REF_RE = re.compile(r"var\(\s*(--[a-z0-9-]+)\s*\)")
SVG_RE = re.compile(r"<svg\b.*?</svg\s*>", re.DOTALL | re.IGNORECASE)
STYLE_RE = re.compile(r"(<style[^>]*>)(.*?)(</style\s*>)", re.DOTALL | re.IGNORECASE)
RECT_RE = re.compile(r"<rect\b[^>]*>", re.IGNORECASE)
RX_ATTR_RE = re.compile(r'\brx\s*=\s*"(\d+(?:\.\d+)?)"')
CLASS_ATTR_RE = re.compile(r'\bclass\s*=\s*"([^"]*)"')

# Literal `rx` values the skill uses, and the geometry role each one expresses.
RADIUS_CLASSES = {"2": "dd-tag", "6": "dd-node", "8": "dd-container"}

SKIN_PLACEHOLDER = "      /* __dd_generated_skin__ */"

RADIUS_RULES = """\
    /* Radius rides the token; the literal rx attribute stays as a Safari fallback. */
    .dd-node      { rx: var(--dd-radius-node); }
    .dd-tag       { rx: var(--dd-radius-tag); }
    .dd-container { rx: var(--dd-radius-container); }
"""


def load_build_skins():
    spec = importlib.util.spec_from_file_location(
        "diagram_design_build_skins", ROOT / "scripts" / "build-skins.py"
    )
    if spec is None or spec.loader is None:
        raise SystemExit("could not load scripts/build-skins.py")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


BUILD_SKINS = load_build_skins()
CONTRACT = BUILD_SKINS.CONTRACT
COLOUR_ROLES = tuple(role for role in CONTRACT if role not in BUILD_SKINS.LENGTH_ROLES)


def expand_hex(value: str) -> str:
    value = value.lower()
    if len(value) == 4:
        return "#" + "".join(character * 2 for character in value[1:])
    return value


def triplet_of(value: str) -> tuple[int, int, int] | None:
    value = value.strip()
    if value.startswith("#"):
        expanded = expand_hex(value)
        if len(expanded) != 7:
            return None
        return tuple(int(expanded[offset:offset + 2], 16) for offset in (1, 3, 5))
    match = RGBA_RE.fullmatch(value)
    if match:
        return tuple(int(match.group(index)) for index in (1, 2, 3))
    return None


def alpha_of(value: str) -> float:
    match = RGBA_RE.fullmatch(value.strip())
    return float(match.group(4)) if match else 1.0


def format_percentage(alpha: float) -> str:
    text = f"{alpha * 100:.4f}".rstrip("0").rstrip(".")
    return text or "0"


class Skin:
    """The literal→role lookups for one variant of the active skin."""

    def __init__(self, variant: str) -> None:
        self.variant = variant
        roles = BUILD_SKINS.read_roles()
        self.exact: dict[str, str] = {}
        self.opaque: dict[tuple[int, int, int], str] = {}
        for role in COLOUR_ROLES:
            value = roles[role][variant].strip()
            key = self.normalize(value)
            # First role wins, so the contract's own ordering resolves any tie.
            self.exact.setdefault(key, role)
            if value.startswith("#"):
                triplet = triplet_of(value)
                if triplet is not None:
                    self.opaque.setdefault(triplet, role)
        # A translucent role also anchors its own triplet when no opaque role claims it —
        # the dark skin defines `rule` and `accent-tint` as rgba with no hex counterpart.
        for role in COLOUR_ROLES:
            value = roles[role][variant].strip()
            triplet = triplet_of(value)
            if triplet is not None and triplet not in self.opaque:
                base = self.base_role_for(role)
                if base is not None:
                    self.opaque[triplet] = base

    @staticmethod
    def base_role_for(role: str) -> str | None:
        """The opaque role a derived role is a wash of, per style-guide.md."""
        if role in {"rule", "wash-2", "wash-3", "wash-5", "wash-20", "wash-30"}:
            return "ink"
        if role in {"rule-solid", "wash-10"}:
            return "muted"
        if role == "accent-tint":
            return "accent"
        return None

    @staticmethod
    def normalize(value: str) -> str:
        value = value.strip()
        if value.startswith("#"):
            return expand_hex(value)
        match = RGBA_RE.fullmatch(value)
        if match:
            red, green, blue = (int(match.group(index)) for index in (1, 2, 3))
            return f"rgba({red},{green},{blue},{float(match.group(4)):g})"
        return value.casefold()

    def substitute(self, literal: str) -> str | None:
        """Return the token expression for *literal*, or None if it is off-skin."""
        role = self.exact.get(self.normalize(literal))
        if role is not None:
            return f"var(--dd-{role})"
        triplet = triplet_of(literal)
        if triplet is None:
            return None
        base = self.opaque.get(triplet)
        if base is None:
            return None
        alpha = alpha_of(literal)
        if alpha >= 1:
            return f"var(--dd-{base})"
        return (
            f"color-mix(in srgb, var(--dd-{base}) "
            f"{format_percentage(alpha)}%, transparent)"
        )


BODY_BACKGROUND_RE = re.compile(r"\bbackground(?:-color)?\s*:\s*([^;}]+)", re.IGNORECASE)
FULL_BLEED_RE = re.compile(
    r"<rect\b[^>]*\bwidth\s*=\s*\"(?:100%|\d{3,4})\"[^>]*\bfill\s*=\s*\"([^\"]+)\"",
    re.IGNORECASE,
)


def root_aliases(text: str) -> dict[str, str]:
    match = ROOT_BLOCK_RE.search(text)
    if match is None:
        return {}
    body = COMMENT_RE.sub("", match.group("body"))
    return {
        declaration.group("name"): declaration.group("value").strip()
        for declaration in DECL_RE.finditer(body)
    }


def variant_for(path: Path, text: str) -> str:
    """Decide whether a file paints on light or dark paper.

    The filename is *not* authoritative: `example-gantt-dark.html` and
    `example-dp-integration-dark.html` both render on `#f5f5f5`, so trusting the name
    would map their paper onto `ink` — value-identical today and catastrophically wrong the
    moment the skin changes. The paper colour the file actually paints is authoritative,
    with a tally of variant-exclusive literals as the fallback.
    """
    light, dark = Skin("light"), Skin("dark")
    aliases = root_aliases(text)

    def resolve(value: str) -> str:
        value = value.strip()
        reference = VAR_REF_RE.fullmatch(value)
        if reference:
            return aliases.get(reference.group(1), value).strip()
        return value

    candidates: list[str] = []
    body_rule = re.search(r"\bbody\s*\{([^}]*)\}", text, re.IGNORECASE)
    if body_rule:
        background = BODY_BACKGROUND_RE.search(body_rule.group(1))
        if background:
            candidates.append(resolve(background.group(1).split()[0]))
    bleed = FULL_BLEED_RE.search(text)
    if bleed:
        candidates.append(resolve(bleed.group(1)))

    for candidate in candidates:
        key = Skin.normalize(candidate)
        if light.exact.get(key) == "paper":
            return "light"
        if dark.exact.get(key) == "paper":
            return "dark"

    light_only = set(light.exact) - set(dark.exact)
    dark_only = set(dark.exact) - set(light.exact)
    tally = {"light": 0, "dark": 0}
    for match in list(HEX_RE.finditer(text)) + list(RGBA_RE.finditer(text)):
        key = Skin.normalize(match.group())
        if key in light_only:
            tally["light"] += 1
        elif key in dark_only:
            tally["dark"] += 1
    if tally["dark"] != tally["light"]:
        return "dark" if tally["dark"] > tally["light"] else "light"
    return "dark" if "-dark" in path.stem else "light"


def uses_terminal_skin(path: Path) -> bool:
    """The terminal window is a second, fixed skin (style-guide.md § Terminal skin).

    It is deliberately not part of the `--dd-*` contract, and its palette overlaps the
    default one with different meanings — `#f5f5f5` is `terminal-ink`, not `paper`. Files
    that opt into it are skipped whole rather than half-migrated.
    """
    return "terminal" in path.stem


def skin_block(variant: str) -> list[str]:
    """The generated skin's declarations, ready to paste into a :root block."""
    source = (SKIN_DIR / f"active-{variant}.tokens.css").read_text(encoding="utf-8")
    body = ROOT_BLOCK_RE.search(source)
    if body is None:
        raise SystemExit(f"generated skin active-{variant}.tokens.css has no :root block")
    return [
        f"      {line.strip()}"
        for line in body.group("body").splitlines()
        if line.strip()
    ]


class Report:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.variant = "light"
        self.substitutions = 0
        self.aliases: dict[str, str] = {}
        self.unmapped: list[tuple[int, str]] = []
        self.classes = 0

    def note_unmapped(self, text: str, offset: int, literal: str) -> None:
        self.unmapped.append((text.count("\n", 0, offset) + 1, literal))


def rewrite_literals(text: str, skin: Skin, report: Report) -> str:
    """Replace every colour literal that the active skin can express as a token."""

    def replace(match: re.Match[str]) -> str:
        literal = match.group()
        token = skin.substitute(literal)
        if token is None:
            report.note_unmapped(text, match.start(), literal)
            return literal
        report.substitutions += 1
        return token

    text = RGBA_RE.sub(replace, text)
    return HEX_RE.sub(replace, text)


def rewrite_root_block(text: str, skin: Skin, report: Report) -> str:
    """Insert the generated skin and fold colour aliases onto contract roles.

    An alias whose value *is* a role (``--color-ink: #2d3142``) is deleted and every
    ``var(--color-ink)`` retargeted at ``var(--dd-ink)``. An alias whose value is only
    derivable (``--color-border: rgba(45,49,66,0.10)``) keeps its declaration with a
    token-based value, so no reference site has to change.
    """
    match = ROOT_BLOCK_RE.search(text)
    if match is None:
        return text

    body = match.group("body")
    comments = COMMENT_RE.findall(body)
    stripped = COMMENT_RE.sub("", body)

    # Declarations are parsed individually rather than by line: the examples pack several
    # onto one line (`--paper: #f5f5f5; --ink: #2d3142;`), and a line-based pass silently
    # discards every declaration after the first one it rewrites.
    declarations = list(DECL_RE.finditer(stripped))
    residue = DECL_RE.sub("", stripped).strip()
    if residue:
        raise SystemExit(
            f"{report.path.name}: unparsed content in the :root block: {residue!r}"
        )

    kept: list[str] = [f"      {comment.strip()}" for comment in comments]
    for declaration in declarations:
        name = declaration.group("name")
        value = declaration.group("value").strip()
        if name.startswith("--dd-"):
            continue  # already migrated; the regenerated block replaces it
        token = skin.substitute(value)
        if token is None:
            kept.append(f"      {name}: {value};")
            continue
        report.substitutions += 1
        if token.startswith("var(--dd-"):
            report.aliases[name] = token
            continue
        kept.append(f"      {name}: {token};")

    # The generated block is spliced in after literal rewriting, or its own declarations
    # would be rewritten into `--dd-paper: var(--dd-paper)`.
    body = "\n" + "\n".join([SKIN_PLACEHOLDER] + kept) + "\n    "
    return text[: match.start()] + match.group(1) + body + match.group(3) + text[match.end():]


def splice_skin(text: str, variant: str) -> str:
    if SKIN_PLACEHOLDER not in text:
        return text
    return text.replace(SKIN_PLACEHOLDER, "\n".join(skin_block(variant)), 1)


def retarget_aliases(text: str, report: Report) -> str:
    for name, token in report.aliases.items():
        text = re.sub(rf"var\(\s*{re.escape(name)}\s*\)", token, text)
    return text


def add_radius_classes(text: str, report: Report) -> str:
    """Tag rects with the geometry class matching their literal corner radius."""

    def tag(match: re.Match[str]) -> str:
        element = match.group()
        radius = RX_ATTR_RE.search(element)
        if radius is None:
            return element
        name = RADIUS_CLASSES.get(radius.group(1))
        if name is None:
            return element
        existing = CLASS_ATTR_RE.search(element)
        if existing:
            if name in existing.group(1).split():
                return element
            report.classes += 1
            return (
                element[: existing.start(1)]
                + f"{existing.group(1)} {name}".strip()
                + element[existing.end(1):]
            )
        report.classes += 1
        insert = radius.end()
        return element[:insert] + f' class="{name}"' + element[insert:]

    return RECT_RE.sub(tag, text)


def add_radius_rules(text: str) -> str:
    if ".dd-node" in text:
        return text
    match = STYLE_RE.search(text)
    if match is None:
        return text
    body = match.group(2)
    if not body.rstrip().endswith("}"):
        return text
    insertion = body.rstrip("\n ") + "\n\n" + RADIUS_RULES + "  "
    return text[: match.start(2)] + insertion + text[match.end(2):]


def swap_skin(path: Path) -> tuple[str, Report]:
    """Replace an already-migrated file's skin block and change nothing else.

    This is the operation the whole milestone exists to make possible: reskinning a diagram
    is one `:root` block, not one edit per attribute. It is a separate mode from `migrate`
    because re-running the full codemod would re-resolve literals against the *new* palette,
    which is a different and much larger change.
    """
    original = path.read_text(encoding="utf-8")
    report = Report(path)
    report.variant = variant_for_migrated(path, original)
    match = ROOT_BLOCK_RE.search(original)
    if match is None:
        raise SystemExit(f"{path.name}: no :root block to swap")

    body = COMMENT_RE.sub("", match.group("body"))
    contract = {f"--dd-{role}" for role in CONTRACT}
    declared = {
        declaration.group("name")
        for declaration in DECL_RE.finditer(body)
    }
    if not contract.issubset(declared):
        missing = ", ".join(sorted(contract - declared))
        raise SystemExit(f"{path.name}: not migrated to the contract yet, missing {missing}")

    kept = [
        f"      {declaration.group('name')}: {declaration.group('value').strip()};"
        for declaration in DECL_RE.finditer(body)
        if declaration.group("name") not in contract
    ]
    comments = [f"      {comment.strip()}" for comment in COMMENT_RE.findall(match.group("body"))]
    report.substitutions = len(contract)
    new_body = "\n" + "\n".join(skin_block(report.variant) + comments + kept) + "\n    "
    text = (
        original[: match.start()]
        + match.group(1)
        + new_body
        + match.group(3)
        + original[match.end():]
    )
    check_no_dangling_references(text, report)
    return text, report


def variant_for_migrated(path: Path, text: str) -> str:
    """Read the variant a migrated file already committed to, from its own skin block."""
    aliases = root_aliases(text)
    paper = aliases.get("--dd-paper", "")
    for variant in BUILD_SKINS.VARIANTS:
        if Skin.normalize(paper) == Skin.normalize(
            BUILD_SKINS.read_roles()["paper"][variant]
        ):
            return variant
    return variant_for(path, text)


def migrate(path: Path) -> tuple[str, Report]:
    original = path.read_text(encoding="utf-8")
    report = Report(path)
    report.variant = variant_for(path, original)
    skin = Skin(report.variant)

    text = rewrite_root_block(original, skin, report)
    text = rewrite_literals(text, skin, report)
    text = splice_skin(text, skin.variant)
    text = retarget_aliases(text, report)
    text = add_radius_classes(text, report)
    text = add_radius_rules(text)
    check_no_dangling_references(text, report)
    return text, report


def check_no_dangling_references(text: str, report: Report) -> None:
    """Fail loudly if the rewrite left a `var()` pointing at nothing.

    A custom property that resolves to nothing does not fall back to the literal it
    replaced — it renders as if the declaration were absent, which is a large and silent
    visual change. This is the failure mode that folding alias declarations invites, so it
    is checked rather than trusted.
    """
    referenced = {match.group(1) for match in VAR_REF_RE.finditer(text)}
    declared = {match.group("name") for match in DECL_RE.finditer(text)}
    dangling = sorted(referenced - declared)
    if dangling:
        raise SystemExit(
            f"{report.path.name}: {len(dangling)} dangling custom propert(ies) after "
            f"migration: {', '.join(dangling)}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="report without writing")
    parser.add_argument(
        "--skin-only",
        action="store_true",
        help="replace the generated :root block in an already-migrated file, nothing else",
    )
    parser.add_argument("--quiet", action="store_true", help="print only the summary")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    total = 0
    ambiguous: list[Report] = []
    for path in args.files:
        if uses_terminal_skin(path):
            if not args.quiet:
                print(f"{path.name}: skipped — opts into the fixed terminal skin")
            continue
        text, report = swap_skin(path) if args.skin_only else migrate(path)
        total += report.substitutions
        if report.unmapped:
            ambiguous.append(report)
        if not args.dry_run and text != path.read_text(encoding="utf-8"):
            path.write_text(text, encoding="utf-8")
        if not args.quiet:
            flag = ""
            named = "dark" if "-dark" in path.stem else "light"
            if report.variant != named:
                flag = f"  [!] name says {named}, paints {report.variant}"
            print(
                f"{path.name}: {report.variant}, {report.substitutions} substitution(s), "
                f"{report.classes} radius class(es), {len(report.unmapped)} unmapped{flag}"
            )

    print(f"\nTotal: {total} substitution(s) across {len(args.files)} file(s).")
    if ambiguous:
        print("\nLeft unchanged — no contract role expresses these colours:")
        for report in ambiguous:
            seen: dict[str, int] = {}
            for line, literal in report.unmapped:
                seen.setdefault(literal, line)
            for literal, line in sorted(seen.items()):
                count = sum(1 for _line, value in report.unmapped if value == literal)
                print(f"  {report.path.name}:{line}: {literal} ×{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
