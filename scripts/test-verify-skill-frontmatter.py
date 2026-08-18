#!/usr/bin/env python3
"""Adversarial tests for scripts/verify-skill-frontmatter.py.

Both polarities for every rule: the defect must be reported, and the legal case that
resembles it must not be. The first case is the exact block that shipped in
writing-voice, kept verbatim so a regression is caught by the thing it broke.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFIER = ROOT / "scripts/verify-skill-frontmatter.py"

SHIPPED_BROKEN = (
    "description: Enforce a specific, audience-tailored prose voice and catch LLM writing "
    "slop in chat responses, docs, commit messages, PR descriptions, and deck body content. "
    "Use whenever prose is being drafted, reviewed, or edited, not just decks. Run the lint "
    "script on a draft before treating it as final: the rules alone catch what a human "
    "reviewer would flag, the script catches what's easy to miss by eye."
)


def load():
    spec = importlib.util.spec_from_file_location("verify_skill_frontmatter", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load()
    failures: list[str] = []

    def case(label: str, body: str, expected: int, skill: str = "demo-skill") -> None:
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / "plugins" / skill / "skills" / skill / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(body, encoding="utf-8")
            findings = module.check(path)
        if len(findings) != expected:
            failures.append(f"{label}: expected {expected}, got {len(findings)}: {findings}")
        else:
            print(f"OK: {label}")

    ok = "---\nname: demo-skill\ndescription: Does a thing worth describing.\nlicense: MIT\n---\n\n# Demo\n"

    case("a well-formed block", ok, 0)

    # ── the regression that prompted this checker ───────────────────────────────────
    case(
        "the exact frontmatter that shipped broken in writing-voice",
        f"---\nname: demo-skill\n{SHIPPED_BROKEN}\nlicense: MIT\n---\n",
        1,
    )
    case(
        "the same description, quoted",
        f"---\nname: demo-skill\ndescription: \"{SHIPPED_BROKEN[len('description: '):]}\"\n---\n",
        0,
    )
    # A colon with no following space is ordinary prose, not a mapping.
    case(
        "a colon inside a word, unquoted",
        "---\nname: demo-skill\ndescription: Handles http://example.com and 12:30 fine.\n---\n",
        0,
    )
    case(
        "a trailing colon, unquoted",
        "---\nname: demo-skill\ndescription: Consider this:\n---\n",
        1,
    )
    case(
        "a value opening with a YAML indicator",
        "---\nname: demo-skill\ndescription: [not a list, just a bracket]\n---\n",
        1,
    )

    # ── structure ──────────────────────────────────────────────────────────────────
    case("no opening delimiter", "name: demo-skill\ndescription: x\n", 1)
    case("never closed", "---\nname: demo-skill\ndescription: x\n", 1)
    case("missing description", "---\nname: demo-skill\n---\n", 1)
    case("empty description", "---\nname: demo-skill\ndescription:   \n---\n", 1)
    case("duplicate key", "---\nname: demo-skill\ndescription: a\ndescription: b\n---\n", 1)
    case(
        "unknown key",
        "---\nname: demo-skill\ndescription: x\nnmae: typo\n---\n",
        1,
    )
    # A nested block is legal: the key carries no inline value and its lines are indented.
    case(
        "a nested metadata block",
        "---\nname: demo-skill\ndescription: x\nmetadata:\n  version: 2\n---\n",
        0,
    )

    # ── identity ───────────────────────────────────────────────────────────────────
    case(
        "name disagreeing with its directory",
        "---\nname: other-name\ndescription: x\n---\n",
        1,
    )
    case(
        "name that is not kebab-case",
        "---\nname: Demo_Skill\ndescription: x\n---\n",
        2,  # not kebab-case, and disagrees with the directory
    )

    if failures:
        print("\nFAILURES:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("\nAll skill frontmatter tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
