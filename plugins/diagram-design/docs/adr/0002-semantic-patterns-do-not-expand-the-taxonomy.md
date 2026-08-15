# ADR 0002 — Semantic patterns never expand the 27-type taxonomy

**Status:** superseded by ADR-0010 (v2.4, Phase 3 / M2) — the type count moved from 27 to 32 as
six genuinely new layout grammars were found; the freeze mechanism itself (patterns never
expand the taxonomy; a new type requires a layout no pattern-on-an-existing-type can carry)
continues in force at the new number. Kept here as the record of the reasoning at 27.

## Context

Auditing behavior-rich figures (queues, policy traces, trust boundaries) showed the skill could arrange boxes but not model system behavior. The obvious fix — new diagram types — would balloon the taxonomy, dilute the selection guide, and force every new behavior into a new layout grammar.

## Decision

Behavior is a separate axis. The seven semantic patterns in `references/semantic-patterns.md` each route to the **nearest existing visual type** for layout; a pattern owns semantic primitives and a tighter budget, never a second layout grammar. The visual-type count stays at 27 unless a genuinely new *layout* grammar appears.

## Consequences

- "27 visual types" is a stable, verifiable claim (`verify-semantic-motion.py` and `verify-docs-sync.py` both count it).
- A new behavior costs one pattern section plus a routing-table row — not a new type reference, template set, and example triple.
- If a pattern ever needs a layout no existing type provides, that is the signal to add a type, with the full §10 shipping set.
