# Zoom (Overview + Detail)

**Best for:** splitting a diagram into an overview and a detail view and showing exactly how
they relate — the case `SKILL.md` already instructs authors toward without, until now, a
grammar for the relationship itself.

## Layout conventions
- **Parent strip**, top of canvas: a reduced, quieted reproduction of the overview. Boxes sit
  under the 56px short-box floor with a single small label line — no type tag, no sublabel.
  It is orientation, not content; a reader should recognise it, not re-read it.
- Exactly **one** parent box is marked — accent-tint fill, accent stroke — the element being
  expanded below. Marking is the only thing that breaks the parent's quiet.
- **Correspondence wedge**: a single closed frustum (a `<path>`, not a connector) from the
  marked box's own bottom corners down to the expansion frame's top corners. This is the
  entire correspondence mechanism — a reader does not need the caption to know what opened.
  It is framing, not a relationship between two nodes, so the diagonal sides are intentional
  and out of scope for the no-diagonal-connector rule (see `scripts/verify-no-diagonal.py`,
  which only scans `<line>` elements for exactly this reason).
- **Expansion frame**: a bordered container occupying the majority of the canvas, holding the
  marked element's internals at full node size (tag + name + sublabel, same as any other
  type). A short label in the frame's corner repeats the parent element's name — the wedge and
  the shared label are two independent correspondence signals, deliberately redundant.
- Failure/exception paths inside the expansion are drawn as real branches (dashed, labeled),
  never hidden — a happy-path-only zoom misrepresents what the step does.

## Anti-patterns
- Parent thumbnail small enough that the marked box can't be identified at a glance.
- Parent redrawn differently from the source diagram it's excerpted from.
- Marking more than one parent element — Zoom asserts detail-of for exactly one thing.
- Skipping the wedge and relying on position alone to imply "this is what expanded."
- A caption doing the correspondence's job. If a reader needs the caption to know which box
  opened, the design has failed regardless of how good it looks.

## Examples
- `assets/example-zoom.html` — minimal light
- `assets/example-zoom-dark.html` — minimal dark
- `assets/example-zoom-full.html` — full editorial
