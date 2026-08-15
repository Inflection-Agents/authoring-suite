# ADR 0010 — Phase 3 archetypes supersede the 27-type taxonomy freeze

**Status:** accepted (v2.4, Phase 3 / M2)

**Supersedes:** ADR-0002

## Context

ADR-0002 froze the visual-type count at 27 on the reasoning that behavior belongs to a separate
axis (semantic patterns) and should never itself justify a new layout grammar. That reasoning
held for the seven patterns it introduced — Fan-in queue, Stage framework, Unstructured-input
transformation, Paired policy traces, Secure paved road, Governance catalog, Compensating
security layers — every one of them routes to an existing type.

Two completeness audits (the M2 archetype design brief, `docs/plans/2026-08-14-archetype-design-
brief.md`) found relations no existing type — and no possible semantic pattern on an existing
type — could express: detail-of (Zoom), differs-from (Contrast), derives-from/impact-if-changed
with multi-parent (Lineage), assembled-from (Composition), runs-on with nesting and multiplicity
(Deployment). These are genuinely new *layout grammars*, exactly the case ADR-0002 itself named
as the exception: "if a pattern ever needs a layout no existing type provides, that is the
signal to add a type."

Two more candidates from the same audit turned out **not** to need new types, confirming
ADR-0002's freeze was doing real work and wasn't just inertia:
- **Matrix** retired `type-dp-security-matrix.md` into a preset of itself rather than adding a
  type — the categorical-grid layout and the permissions-grid layout are the same archetype.
- **Hub & spoke** landed as an eighth semantic pattern, not a type — Architecture already drew
  it freehand; the gap was a missing convention, not a missing layout.
- **Code level** cost no new type either — it renamed and generalized `type-er.md` in place.

## Decision

**The visual-type count is 32, and the freeze mechanism ADR-0002 established stays in force at
the new number.** `verify-docs-sync.py` and `verify-semantic-motion.py` continue to enforce an
exact count (now 32) and a routing table entry per type; `semantic-patterns.md` continues to
enforce that every pattern names a nearest existing visual type with no exceptions. The test for
adding a 33rd type is unchanged from ADR-0002's own exception clause: a genuinely new claim that
no existing type's layout grammar can carry, checked against the full type roster before
concluding a pattern won't do.

Two structural decisions from Phase 3 apply retroactively to the whole roster, not just the six
new types:
- **The corner-notch primitive's scope is per-type, not fixed at its original seven.**
  `deployment` extended it (D35) by mapping its three kinds onto the existing vocabulary. Future
  types should ask the same question — does this type's kind-taxonomy match backend/store/
  external — rather than assuming notch is closed to new types.
- **A claim-marking region can be one element spanning several cells/rows/nodes**, not one
  accent per cell in that region (D34's Composition catalog column, D37's Matrix marked column).
  `verify-accent-budget.py`'s per-position dedup already supports this; future types marking a
  multi-cell region should default to a single spanning element, not per-cell accents.

## Consequences

- "32 visual types" is the new stable, verifiable claim, exactly as "27" was — enforced the same
  way, by the same two scripts, just at a new number.
- Every one of the 6 new/generalized types shipped the full set ADR-0002 implied a new type
  would cost: reference doc, 3 example variants, gallery registration, and a decision-log entry
  documenting the judgment calls specific to it (D30–D38).
- Adding a 33rd type still costs the same thing it always did — nothing about this ADR makes the
  bar lower for the next one. Matrix and Hub & spoke crossing this same audit and *not* becoming
  types confirms the bar held.
- Superseding rather than amending ADR-0002 in place preserves its original reasoning as a
  record of what was true at 27 types; a reader tracing why the count changed follows this ADR
  back to it rather than finding an edited document that no longer matches its own git history.
