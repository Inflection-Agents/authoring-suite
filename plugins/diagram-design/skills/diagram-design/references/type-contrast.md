# Contrast (Before / After)

**Best for:** the workhorse of a "why change" argument — showing a current state and a
proposed state so the single difference between them becomes the claim.

## Layout conventions
- Two panels, identical width, identical internal structure — same columns, same row
  positions, same node sizes in both. The mirroring *is* the argument: because the panels
  are otherwise the same, the one difference is unmissable.
- **State labels, never judgements**: `Today` / `Proposed`, not `Bad` / `Good`. Both panels
  get identical label treatment — no colour or weight bias toward either side.
- Divider: a plain hairline rule between panels is enough; it doesn't need a label of its
  own since the panel headers already carry the state names.
- Mark the single difference with accent in the right panel only, within the house 2-accent
  budget. The left panel stays entirely ordinary — it is the baseline, not a strawman.
- **The lopsided case is the common one**: the proposed panel usually has *fewer* nodes than
  today's, not the same count recoloured. Hold parity through matched column x-positions and
  matched vertical extent (the consolidated element spans the same vertical space the thing
  it replaced used to occupy) rather than through a literal node-for-node swap.
- A short **delta ledger** (what changed, as a plain list) earns its place in the full
  editorial variant's supporting prose, not inside the SVG itself — the diagram should
  already read without it.

## Anti-patterns
- Panels with different internal structure — the reader can't diff them, and it becomes two
  unrelated diagrams side by side.
- Strawmanning the left panel by drawing it more cluttered than it really is. Sophisticated
  readers notice, and the whole argument loses credibility.
- Highlighting both panels — that destroys the baseline the contrast depends on.
- A third panel. A third state is a sequence, which is a different type, not a wider contrast.

## Examples
- `assets/example-contrast.html` — minimal light
- `assets/example-contrast-dark.html` — minimal dark
- `assets/example-contrast-full.html` — full editorial
