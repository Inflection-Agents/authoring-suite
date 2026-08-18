#!/usr/bin/env python3
"""Verify every plugin's SKILL.md frontmatter, across the whole marketplace.

The frontmatter is the only text an agent sees *before* deciding whether to load a skill.
If it does not parse, the skill's name and description are not what the agent reads, and
nothing downstream reports that: `claude plugin validate --strict` checks the marketplace
and plugin manifests, not the skill file the manifests point at.

That is how `writing-voice` shipped with a broken block. Its description ended with

    ... before treating it as final: the rules alone catch what a human reviewer would flag

and a bare `: ` inside an unquoted YAML scalar makes the parser read a nested mapping,
so the whole document failed with "mapping values are not allowed here". The plugin had
no CI at all -- the two workflows in this repo are both path-filtered to
`plugins/diagram-design/**` -- so nothing looked.

This is a contract checker rather than a YAML validator, deliberately. Skill frontmatter
is a flat map of scalars with a known shape, so the checks that matter are narrower AND
wider than "is it valid YAML": a name that disagrees with its directory parses perfectly
and is still wrong. It uses only the standard library, matching every other gate here.

Usage:
    python3 scripts/verify-skill-frontmatter.py
    python3 scripts/verify-skill-frontmatter.py plugins/writing-voice/skills/writing-voice/SKILL.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED = ("name", "description")
KNOWN = REQUIRED + ("license", "metadata", "allowed-tools", "version")
KEY_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9_-]*):(?P<rest>.*)$")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# A plain scalar starting with one of these changes meaning in YAML; quote it instead.
INDICATORS = "[]{}&*!|>%@`,"


def check(path: Path) -> list[str]:
    # Display a repo-relative path when the file is inside the repo, and the path as
    # given otherwise: this accepts arbitrary file arguments, so it must not assume one.
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    text = path.read_text(encoding="utf-8")
    out: list[str] = []

    if not text.startswith("---\n"):
        return [f"{rel}: frontmatter must open with '---' on line 1"]
    body = text[4:]
    end = body.find("\n---")
    if end == -1:
        return [f"{rel}: frontmatter is never closed with '---'"]
    block = body[:end]

    seen: dict[str, str] = {}
    key = None
    for offset, line in enumerate(block.split("\n"), start=2):
        if not line.strip():
            continue
        if line[0] in " \t":
            if key is None:
                out.append(f"{rel}:{offset}: indented line with no key above it")
            continue  # a continuation or a nested block under the previous key
        match = KEY_RE.match(line)
        if not match:
            out.append(f"{rel}:{offset}: not a 'key: value' line: {line.strip()!r}")
            key = None
            continue
        key = match.group("key")
        value = match.group("rest").strip()
        if key in seen:
            out.append(f"{rel}:{offset}: duplicate key {key!r}")
        seen[key] = value
        if key not in KNOWN:
            out.append(f"{rel}:{offset}: unknown key {key!r} (known: {', '.join(KNOWN)})")
        if not value:
            continue  # a nested block, validated by its indented lines
        quoted = len(value) > 1 and value[0] == value[-1] and value[0] in "\"'"
        if quoted:
            continue
        if ": " in value or value.endswith(":"):
            out.append(
                f"{rel}:{offset}: {key!r} is an unquoted value containing ': ', which YAML "
                f"reads as a nested mapping and rejects. Wrap the value in double quotes.")
        elif value[0] in INDICATORS:
            out.append(
                f"{rel}:{offset}: {key!r} starts with {value[0]!r}, which is a YAML "
                f"indicator. Wrap the value in double quotes.")

    for required in REQUIRED:
        if required not in seen:
            out.append(f"{rel}: frontmatter is missing required key {required!r}")

    name = seen.get("name", "").strip("\"'")
    if name:
        if not NAME_RE.match(name):
            out.append(f"{rel}: name {name!r} must be lowercase kebab-case")
        if name != path.parent.name:
            out.append(
                f"{rel}: name {name!r} does not match its directory {path.parent.name!r}; "
                f"the loader resolves a skill by directory, so these must agree")
    if "description" in seen and not seen["description"].strip("\"'").strip():
        out.append(f"{rel}: description is empty; it is the only text an agent sees "
                   f"before deciding to load the skill")
    return out


def main() -> int:
    args = sys.argv[1:]
    paths = [Path(a).resolve() for a in args] if args else sorted(
        (ROOT / "plugins").glob("*/skills/*/SKILL.md"))
    if not paths:
        print("no SKILL.md found under plugins/*/skills/*/", file=sys.stderr)
        return 1

    findings: list[str] = []
    for path in paths:
        if not path.exists():
            findings.append(f"{path}: file not found")
            continue
        findings.extend(check(path))

    for finding in findings:
        print(finding)
    print(f"Summary: {len(paths)} skill(s) checked, {len(findings)} finding(s).")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
