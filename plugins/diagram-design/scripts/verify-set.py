#!/usr/bin/env python3
"""Verify the diagram-set spine — cross-file identity continuity for multi-diagram sets.

See `references/diagram-sets.md` for the schema and the reasoning. Briefly: a diagram opts into
a set by carrying `<meta name="diagram:id/level/parent/subject/elements">` tags. A file with none
of these tags is not part of any set and is silently skipped — this feature is opt-in, checked
zero times against the vast majority of the corpus by design.

Seven checks, six errors and one info:

1. Every `diagram:parent` resolves to another diagram's `diagram:id`.
2. `diagram:subject` appears in the parent's `diagram:elements`.
3. Level descent is legal: for the strict ladder (landscape/context/container/component/code) a
   child sits exactly one rung below its parent. `deployment` and `dynamic` attach to any
   declared level without a rung constraint — see `references/diagram-sets.md` § Levels.
4. An element id appearing in more than one diagram carries the same human label everywhere —
   the label is read from the first `<text>` inside that element's `<g data-element-id="...">`.
5. No cycles in the parent graph.
6. Exactly one root per declared set — diagrams grouped by the first dotted segment of
   `diagram:id` (`ingest-platform.transform` claims the `ingest-platform` set) must have exactly
   one member with no parent. This is the one check that leans on the id convention rather than
   pure referential integrity: the parent graph is a forest by construction (one `parent` field
   per diagram), so a connected component of it can never itself hold two roots — the grouping
   that can actually produce a real, catchable error is "these diagrams claim the same set."
7. (info, not an error) An element with no child diagram drilling into it — coverage reporting.

Regenerates `docs/diagram-map.md` as a side effect, the same generated-file-plus-`git diff
--exit-code` pattern `build-icons.py`/`build-skins.py` use.

Element-group parsing is non-greedy up to the first `</g>` — correct for the common case (a
`data-element-id` group is a single node's box, not a container of further nested groups); it is
not a general nested-tag parser.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "skills/diagram-design/assets"
DIAGRAM_MAP = ROOT / "docs/diagram-map.md"

META_RE = re.compile(
    r'<meta\s+name="diagram:([a-z]+)"\s+content="([^"]*)"',
    re.IGNORECASE,
)
ELEMENT_RE = re.compile(
    r'<g\b[^>]*\bdata-element-id="([^"]+)"[^>]*>(.*?)</g>',
    re.IGNORECASE | re.DOTALL,
)
TEXT_RE = re.compile(r"<text\b[^>]*>([^<]*)</text>", re.IGNORECASE)

HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

LADDER = ("landscape", "context", "container", "component", "code")
ATTACHED_LEVELS = ("deployment", "dynamic")
ALL_LEVELS = LADDER + ATTACHED_LEVELS


class Diagram:
    def __init__(self, path: Path, fields: dict[str, str]):
        self.path = path
        self.id = fields.get("id", "")
        self.level = fields.get("level", "")
        self.parent = fields.get("parent") or None
        self.subject = fields.get("subject") or None
        elements = fields.get("elements", "")
        self.elements = [e.strip() for e in elements.split(",") if e.strip()]

    def __repr__(self) -> str:
        return f"Diagram({self.id!r} @ {self.path.name})"


def strip_comments(text: str) -> str:
    """Blank out HTML comments so a template's commented-out example meta block (or a
    commented-out element group) is never mistaken for a live one."""
    return HTML_COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), text)


def parse_diagram(path: Path) -> Diagram | None:
    text = strip_comments(path.read_text(encoding="utf-8"))
    fields = dict(META_RE.findall(text))
    if "id" not in fields:
        return None
    return Diagram(path, fields)


def parse_element_labels(path: Path) -> dict[str, str]:
    text = strip_comments(path.read_text(encoding="utf-8"))
    labels: dict[str, str] = {}
    for element_id, body in ELEMENT_RE.findall(text):
        match = TEXT_RE.search(body)
        if match:
            labels[element_id] = match.group(1).strip()
    return labels


def find_cycles(diagrams: dict[str, Diagram]) -> list[str]:
    findings = []
    for did in diagrams:
        seen = {did}
        current = diagrams[did].parent
        chain = [did]
        while current is not None:
            chain.append(current)
            if current in seen:
                findings.append(
                    f"cycle in parent graph: {' -> '.join(chain)}"
                )
                break
            seen.add(current)
            current = diagrams.get(current).parent if current in diagrams else None
        # unresolved parents are reported separately by check 1
    # dedupe (a cycle is found once per member without this)
    return sorted(set(findings))


def check(paths: list[Path]) -> tuple[list[str], list[str]]:
    diagrams: dict[str, Diagram] = {}
    duplicate_ids: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        diagram = parse_diagram(path)
        if diagram is None:
            continue
        if diagram.id in diagrams:
            duplicate_ids.append(
                f"duplicate diagram:id {diagram.id!r} in {path.name} and "
                f"{diagrams[diagram.id].path.name}"
            )
            continue
        diagrams[diagram.id] = diagram

    errors: list[str] = list(duplicate_ids)
    infos: list[str] = []

    if not diagrams:
        return errors, infos

    # Check 1: parent resolves
    for diagram in diagrams.values():
        if diagram.parent is not None and diagram.parent not in diagrams:
            errors.append(
                f"{diagram.path.name}: diagram:parent {diagram.parent!r} does not resolve "
                f"to any diagram:id"
            )

    # Check 2: subject appears in parent's elements
    for diagram in diagrams.values():
        if diagram.parent is None or diagram.parent not in diagrams:
            continue
        parent = diagrams[diagram.parent]
        if diagram.subject is None:
            errors.append(
                f"{diagram.path.name}: has diagram:parent but no diagram:subject"
            )
        elif diagram.subject not in parent.elements:
            errors.append(
                f"{diagram.path.name}: diagram:subject {diagram.subject!r} does not appear "
                f"in parent {parent.id!r}'s diagram:elements"
            )

    # Check 3: legal level descent
    for diagram in diagrams.values():
        if diagram.level not in ALL_LEVELS:
            errors.append(
                f"{diagram.path.name}: diagram:level {diagram.level!r} is not one of "
                f"{', '.join(ALL_LEVELS)}"
            )
        if diagram.parent is None or diagram.parent not in diagrams:
            continue
        parent = diagrams[diagram.parent]
        if diagram.level in LADDER and parent.level in LADDER:
            if LADDER.index(diagram.level) != LADDER.index(parent.level) + 1:
                errors.append(
                    f"{diagram.path.name}: level {diagram.level!r} is not exactly one rung "
                    f"below parent {parent.id!r}'s level {parent.level!r}"
                )
        # deployment/dynamic children attach to any declared parent level — no rung check.

    # Check 4: cross-diagram label consistency
    element_labels: dict[str, dict[str, str]] = {}  # element_id -> {diagram_id: label}
    for diagram in diagrams.values():
        labels = parse_element_labels(diagram.path)
        for element_id in diagram.elements:
            if element_id in labels:
                element_labels.setdefault(element_id, {})[diagram.id] = labels[element_id]
    for element_id, by_diagram in element_labels.items():
        distinct = set(by_diagram.values())
        if len(distinct) > 1:
            detail = ", ".join(f"{did}={label!r}" for did, label in sorted(by_diagram.items()))
            errors.append(
                f"element {element_id!r} has inconsistent labels across diagrams: {detail}"
            )

    # Check 5: no cycles
    errors.extend(find_cycles(diagrams))

    # Check 6: exactly one root per set. A diagram's single `parent` field makes the
    # parent graph a forest by construction — a connected component of parent/child edges
    # can never itself contain two roots, so that grouping can never catch anything. The
    # grouping that can actually fail is "diagrams that claim to belong to the same set,"
    # which the id convention expresses via the dotted path's first segment
    # (`ingest-platform.transform` claims the `ingest-platform` set). Two diagrams with no
    # parent sharing that prefix are two roots of one declared set; zero is an orphaned
    # set where every member's parent chain fails to terminate inside the group.
    by_set_prefix: dict[str, list[str]] = {}
    for did in diagrams:
        prefix = did.split(".", 1)[0]
        by_set_prefix.setdefault(prefix, []).append(did)
    for prefix, members in by_set_prefix.items():
        if len(members) <= 1:
            continue  # a lone diagram is trivially its own 1-root set
        roots = [m for m in members if diagrams[m].parent is None]
        if len(roots) != 1:
            errors.append(
                f"set {prefix!r} has {len(roots)} root(s) (expected exactly 1) among "
                f"{sorted(members)}"
            )

    # Check 7 (info): elements never drilled into
    subjects_used = {d.subject for d in diagrams.values() if d.subject is not None}
    for diagram in diagrams.values():
        undrilled = [e for e in diagram.elements if e not in subjects_used]
        if undrilled:
            infos.append(
                f"{diagram.id}: {len(undrilled)} of {len(diagram.elements)} element(s) have "
                f"no child diagram ({', '.join(undrilled)})"
            )

    return errors, infos


def build_map(paths: list[Path]) -> str:
    diagrams: dict[str, Diagram] = {}
    for path in paths:
        if not path.exists():
            continue
        diagram = parse_diagram(path)
        if diagram is not None and diagram.id not in diagrams:
            diagrams[diagram.id] = diagram

    if not diagrams:
        return (
            "# Diagram map\n\n"
            "Generated by `scripts/verify-set.py` — do not edit by hand.\n\n"
            "No diagram sets declared yet. This feature is opt-in; see "
            "`skills/diagram-design/references/diagram-sets.md`.\n"
        )

    children_of: dict[str, list[str]] = {did: [] for did in diagrams}
    roots: list[str] = []
    for did, diagram in diagrams.items():
        if diagram.parent in diagrams:
            children_of[diagram.parent].append(did)
        else:
            roots.append(did)

    lines = ["# Diagram map", "", "Generated by `scripts/verify-set.py` — do not edit by hand.", ""]

    def render(did: str, prefix: str, is_last: bool, is_root: bool) -> None:
        diagram = diagrams[did]
        connector = "" if is_root else ("└── " if is_last else "├── ")
        lines.append(f"{prefix}{connector}{did:<38} [{diagram.level}]")
        child_prefix = prefix if is_root else prefix + ("    " if is_last else "│   ")
        kids = sorted(children_of[did])
        for i, kid in enumerate(kids):
            render(kid, child_prefix, i == len(kids) - 1, False)

    for i, root in enumerate(sorted(roots)):
        render(root, "", i == len(roots) - 1, True)

    subjects_used = {d.subject for d in diagrams.values() if d.subject is not None}
    total_elements = sum(len(d.elements) for d in diagrams.values())
    drilled = sum(1 for d in diagrams.values() for e in d.elements if e in subjects_used)
    lines.append("")
    lines.append(f"{drilled} of {total_elements} element(s) across the set have a child diagram.")
    lines.append("")

    return "\n".join(lines)


def targets(args: argparse.Namespace) -> list[Path]:
    if args.all:
        return sorted(ASSET_DIR.glob("example-*.html")) + sorted(
            ASSET_DIR.glob("template*.html")
        )
    return [Path(p) for p in args.files]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="HTML diagrams to check")
    parser.add_argument("--all", action="store_true", help="check every shipped asset")
    args = parser.parse_args()

    paths = targets(args)
    if not paths:
        parser.error("pass one or more files, or --all")

    errors, infos = check(paths)

    for info in infos:
        print(f"info: {info}")
    for error in errors:
        print(f"error: {error}")

    if args.all:
        DIAGRAM_MAP.parent.mkdir(parents=True, exist_ok=True)
        DIAGRAM_MAP.write_text(build_map(paths), encoding="utf-8")

    print(
        f"Summary: {len(paths)} file(s) checked, {len(errors)} error(s), {len(infos)} info "
        f"finding(s)."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
