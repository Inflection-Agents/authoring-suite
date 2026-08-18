# ADR 0012 — A whole-system request routes to a descent, not to one diagram

**Status:** accepted (v2.4)

## Context

Every part of a C4-style descent already shipped. `references/diagram-sets.md` borrows the
ladder verbatim (`landscape → context → container → component → code`, with `deployment`
and `dynamic` attaching rather than continuing it) on the stated grounds that C4's
vocabulary is widely understood. `type-zoom.md` is the mechanism for one hop, parent strip
and correspondence wedge included. `scripts/verify-set.py` enforces the spine with six
checks.

What was missing was the routing. `routing.md` offered **Architecture** and **Zoom** as two
unrelated single-diagram picks:

    | Topology  | Components + connections in a system  | Architecture |
    | Detail-of | An overview with one element expanded | Zoom         |

So "document our infrastructure" resolved to one Architecture diagram. Nothing said that a
whole-system request is a descent.

The failure this produces is not a bad diagram; it is a diagram forced into a choice it
cannot win. One Architecture view of an entire estate either shows the parts and stops
being legible, or stays legible by omitting them. The complexity budget (§7) already says
"above 9 nodes, it's probably two diagrams", but it says it as a limit to respect rather
than as a structure to reach for, so the honest response to a large subject looked like
deletion.

Observed: an agent asked to document a platform's infrastructure against v2.3 produced a
single Architecture diagram. Re-run with the descent named explicitly, it produced eleven
diagrams in one declared set, and `verify-set.py` caught a real modelling error on the way
(a `dynamic` diagram naming its own parent as its `subject`, which is not a relationship
the ladder has). Every part was already in the box. Only the default was wrong.

## Decision

1. `routing.md` opens with a scope question before any type selection: one flow, topology,
   comparison or subsystem is a single diagram; a whole system, product, platform or estate
   is a set.
2. `SKILL.md` §3 states the same question in two sentences, because §3 is the decision
   point and an agent may never load `routing.md` if it believes it already knows the type.
3. `type-architecture.md` carries a scope check, because an agent that routed straight to
   the type reference needs the choice to surface at the moment of drawing.
4. `type-zoom.md` states that across a set the parent strip is byte-identical apart from
   the marked box, and should be emitted from one declaration of the container list.

## Consequences

- The descent is a default, not a capability. A reader asking for "our architecture" gets a
  navigable set rather than one crowded canvas.
- Two guard rails keep the set from inflating. Containers are grouped by what fails
  together rather than by source-tree shape, and `verify-set.py` reports an element with no
  child diagram as coverage rather than as a failure, so not every container needs an
  expansion.
- The byte-identical parent strip is stated as discipline, not enforced. `verify-set.py`
  check 4 compares element ids across diagrams and does not read the strip's geometry.
  Emitting the strip from a single declaration is what actually holds it; a checker for it
  would need to know which rects form the strip, which is the same semantic question ADR
  0011 declined to guess at for `loose-start`.
- This is documentation only. No type is added, no template changes, and the 32-type
  taxonomy of ADR 0010 is untouched — the descent composes existing types rather than
  introducing a new one.
