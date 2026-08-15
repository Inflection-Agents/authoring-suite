# ADR 0009 — The 4px grid wins for geometry; the brand owns the type ramp

**Status:** accepted (v2.4)

## Context

`SKILL.md` §7 calls the 4px grid non-negotiable: every coordinate, size, and gap divisible by four. It is the rule that keeps diagrams from looking machine-arranged, and it is the one visual rule the skill states in absolute terms.

The Inflection type ramp is `10 / 12 / 15 / 18 / 24 / 32 / 48 / 64`. Three of those — 10, 15, 18 — are not divisible by four. Onboarding a brand therefore forces a choice the grid rule does not anticipate: round the brand's sizes onto the grid, or let the brand override a rule called non-negotiable.

## Decision

They govern different things, and the split is by axis rather than by precedence.

**Coordinates stay on the grid.** Positions, widths, heights, and gaps are divisible by four, always. This is what alignment is made of, and a brand has no opinion about where a box sits.

**The brand owns the type ramp.** Font sizes come from the brand's scale even where they fall off the grid. A diagram set that does not share its brand's text sizes reads as foreign no matter how well its boxes align — and text is set on a baseline, not on the layout grid, so an off-grid font size does not disturb a single coordinate.

Radius follows type, not geometry: it is part of a brand's corner register, which is why `radius-node`, `radius-tag`, and `radius-container` are tokens (ADR-0007) rather than the hardcoded `rx="6"` they replaced.

## Consequences

- The grid check that Phase 2c will introduce measures coordinates only. It must not read `font-size`, or every branded skin fails it.
- `style-guide.md`'s Typography table is authoritative for sizes and may hold off-grid values; the Stroke, radius, spacing table stays on the grid for everything except radius.
- Onboarding a brand cannot silently break alignment, because the one thing it is allowed to change — the type ramp — does not move any box.
- If a brand's radius scale ever produced a corner larger than half a node's smallest dimension, that is a taste failure to catch at the pre-output gate, not a grid violation.
