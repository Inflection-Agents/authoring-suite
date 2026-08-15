# ADR 0006 — The SKILL.md cap holds; the selection tables move to routing

**Status:** accepted (fork, v2.4 planning)

## Context

`SKILL.md` is capped at 40,000 bytes by `verify-semantic-motion.py` so the installed skill stays
cheap to load. It currently sits at 37,406 bytes, leaving 2,594 bytes of headroom.

The planned work does not fit in that headroom. Phases 3 and 4 add six type rows to the §3 selection
table, six type names to the frontmatter description, a semantic-pattern row for hub & spoke, and
amendments to §5 (mandatory tags, the notch), §6 (correspondence strokes, the containment-frame
clarification to connector rule 5) and §7 (per-unit budgets for Zoom, Contrast, Deployment and the
code level). Estimated at 2,400–3,000 bytes.

Because this repository is a branded derivative rather than an upstream contributor, raising the cap
was available. ADR-0004 established the cap upstream, and a fork is not bound by it.

Measurement showed raising it is unnecessary:

| Section | Bytes |
|---|---|
| §3 visual-type guide table (32 lines) | 3,217 |
| §3 semantic-pattern routing table | 885 |
| **Total relocatable** | **4,102** |

M2.2 introduces `references/routing.md`, whose entire purpose is to select a type from a relation.
Both tables are already that document's subject matter; they sit in `SKILL.md` only because no such
document existed when they were written.

## Decision

**The 40,000-byte cap holds unchanged.** The new content is paid for by relocating both §3 tables
into `references/routing.md` as part of M2.2, leaving §3 as a short routing pointer.

Relocation lands **before or with** the Phase 3 type additions, so the headroom exists before it is
spent.

Projected result: headroom rises from 2,594 to roughly 6,696 bytes, then falls to roughly
3,700–4,300 after the planned additions — a wider margin than the skill has today.

## Consequences

- The cap remains a real constraint rather than a number adjusted whenever it binds. That was the
  point of ADR-0004 and it survives the fork.
- Selection logic gains a single home. Today a reader chooses a type from a table in `SKILL.md` and
  then reads a procedure in `routing.md` that explains how to choose; splitting those is the
  accident, and merging them is an improvement independent of bytes.
- §3 becomes a pointer, which reinforces the progressive-disclosure design: `SKILL.md` routes,
  references carry detail.
- **Ordering constraint.** M2.2's relocation must not land after the Phase 3 additions, or the cap
  binds mid-phase. The execution plan already sequences routing after the archetypes for a different
  reason — that ordering must now be revisited so the *relocation* half of M2.2 comes early even if
  the routing *procedure* lands later.
- If a future change genuinely cannot fit, this ADR is superseded rather than quietly amended.
