# ADR 0011 — Geometry is measured author-side, and §9 asks for the output

**Status:** accepted (v2.4)

## Context

ADR 0005 established that a geometric contract in this project is expressed as a checker
with fixtures, on the grounds that *"a rule that only lives in prose is a rule that ships
broken examples."* That reasoning was applied to one rule and one direction.

Two gaps followed from it.

**The checkers point at this repo, not at the agent.** `scripts/` carries fourteen
`verify-*.py`. `skills/diagram-design/scripts/`, the directory that travels to whoever
installs the plugin, carried three: two import extractors and `self_check.py`, none of
which reads a coordinate. So the gates verify the examples shipped *from* here, and
nothing verifies the diagram an agent produces *with* the skill.

**§9 asks the author to certify what it cannot see.** "Every arrow label has a visible
6–10px gap above its connector?" is answered from intent, not from measuring label rects
against path segments. A pre-output checklist also fires before the only moment the
property exists: these defects are properties of rendered output.

The evidence for both is a set of eleven diagrams authored against v2.3 by an agent that
had read §9 first. It shipped roughly forty geometry defects in five classes, and every
one was found afterwards by building ad-hoc checkers. §9 already named two of the classes
correctly. Coverage was not the problem; the absence of an instrument was.

ADR 0005 also recorded, as a known limit, that the connector-clearance half of §6 rule 2
*"needs stroke geometry rather than rectangles"* and would remain a checklist item. It
did, and 46 violations of it are shipped in this repo's own examples.

## Decision

1. The predicates move into `skills/diagram-design/scripts/verify_geometry.py`, which
   ships with the plugin. `scripts/verify-geometry.py` becomes a thin CI entry point that
   re-exports them and adds `--all` plus the baseline, so there is one implementation and
   the adversarial tests target the code an installed plugin actually runs.
2. Three checks run by default: `clipped-mask` (ADR 0005's, unchanged), `masked-edge`
   (the stroke geometry ADR 0005 deferred), and `broken-out`.
3. Two checks ship opt-in behind `--also`: `corner-landing` and `loose-start`. Both must
   decide what counts as a node, and that judgement is not reliable from shape alone
   across 32 types. Several types legitimately anchor a connector beside an icon or a
   text label rather than on a shape edge, and a rect-shaped heuristic reads those as
   errors. Measured against the shipped assets they produce 65 and 32 findings
   respectively, nearly all correct-by-design. They are exact for diagrams whose bodies
   are all real shapes, which is the common case for a generated set.
4. §9 changes contract from confirmation to evidence. The gate asks for the checker's
   output, not a tick. `verify_geometry.py: 0 findings` is checkable; "☑ every label has
   a gap" is not.
5. What the checker cannot do is named rather than implied. Text advance needs font
   metrics, so a name overrunning its box is not caught here; §9 carries a console
   snippet that lets the browser measure it.

## Consequences

- The 46 findings the new checks surface are recorded in `scripts/geometry-baseline.txt`
  under the same grandfather rule as `grid-baseline.txt`: the list only shrinks, and
  fixing those hand-placed labels is tracked separately from adding the checker.
- A shape heuristic now reads circles, ellipses, polygons and closed paths, not only
  rects. Without it the checker called every polygon-bodied type "open canvas". A future
  type with markedly different proportions widens the constants at the top of the module
  and adds the case to the adversarial tests, as ADR 0005 set out.
- Two checks being opt-in is a real limit, stated rather than hidden. Making them
  default-safe means the checker knowing which shapes are bodies, which is a semantic
  question this project's hand-authored SVG does not answer. The alternative considered
  and rejected was baselining their findings: a checker that fires on correct work trains
  authors to ignore it, which is the failure ADR 0005 exists to prevent.
