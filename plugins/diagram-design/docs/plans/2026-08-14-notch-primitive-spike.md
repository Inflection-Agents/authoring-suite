# Spike — the corner-notch primitive

**Date:** 2026-08-14
**Phase:** 0
**Question:** can a clipped corner be drawn conformantly, does it survive distance and greyscale,
and which corner convention reads best?
**Answer:** yes, yes, and Convention A — but the spike found two things that re-scope M3.

---

## 1. The primitive

A clipped corner needs a `path`, not a `rect`, because `rx` rounds every corner uniformly. The
generator below produces a rounded rectangle in which any subset of corners is chamfered instead.

```python
def notched_rect(x, y, w, h, r=2, n=8, corners=()):
    """corners ⊆ {'tl','tr','br','bl'} are chamfered at depth n; the rest are rounded at r."""
    p = [f"M {x + (n if 'tl' in corners else r)},{y}"]
    p += ([f"H {x+w-n}", f"L {x+w},{y+n}"]
          if 'tr' in corners else [f"H {x+w-r}", f"A {r},{r} 0 0 1 {x+w},{y+r}"])
    p += ([f"V {y+h-n}", f"L {x+w-n},{y+h}"]
          if 'br' in corners else [f"V {y+h-r}", f"A {r},{r} 0 0 1 {x+w-r},{y+h}"])
    p += ([f"H {x+n}", f"L {x},{y+h-n}"]
          if 'bl' in corners else [f"H {x+r}", f"A {r},{r} 0 0 1 {x},{y+h-r}"])
    p += ([f"V {y+n}", f"L {x+n},{y}"]
          if 'tl' in corners else [f"V {y+r}", f"A {r},{r} 0 0 1 {x+r},{y}"])
    return " ".join(p + ["Z"])
```

**Interaction with `--dd-radius-node` is clean.** Chamfered corners ignore `r`; rounded corners keep
it. A skin can set radius 0, 2, or 8 without touching notch geometry. This was the interaction the
plan flagged as the risk, and it is a non-issue.

**No conflict with the no-diagonal rule.** That rule targets connectors and is checked on `<line>`
elements. A chamfer is a diagonal *edge of a shape*, inside a `<path>`. Worth stating explicitly in
the reference so nobody "fixes" it later.

**Grid safety:** with `x, y, w, h, n` on the 4px grid, every emitted coordinate is on the grid. Only
`r` sits off it, exactly as the current `rx` does.

**Conformance:** the specimen passes `lint-skin.py` and the packaged `self_check.py` today, on the
current editorial palette, with zero findings.

---

## 2. Convention: adopt A

| | 1 notch | 2 notches |
|---|---|---|
| **A — adopt** | top-right | top-right **+ bottom-right** |
| B — reject | top-right | top-right + bottom-left |

Rendered side by side, A wins because its two clips sit on the same edge and **combine into a single
silhouette feature** — the box reads as one chevron-ish shape. B's diagonally opposite clips read as
two separate corner events rather than one shape, which is weaker at distance and easy to mistake
for a drawing error.

**Semantics** (from pass 3): 0 notches = *acts*, 1 = *holds*, 2 = *outside our control*.
Optional and boundary keep their dashes; dash is already a third channel and the notch does not
need to carry them.

**Depth:** `n = 8` at full size. The specimen renders legibly at 50% with `n = 4`, so the notch
survives the projector test that kills the 7px tag.

---

## 3. The greyscale render found a gap in pass 3

The specimen was rendered at 2× and again through `grayscale(1)`. Two results:

**The notch works exactly as claimed.** At full size and at 50%, in colour and in greyscale, the
one-notch and two-notch boxes stay instantly distinguishable. This is the channel the system needed.

**Focal does not survive greyscale at all — and pass 3 did not give it a replacement.** In the
greyscale render the focal node is indistinguishable from `input` and `store`: the accent fill and
accent stroke both collapse to the same grey, and stroke-width 1.2 against 1.0 is not a perceptible
difference.

Pass 3 concluded that "fills stay, but stop being load-bearing", and spent all three notch states on
*kind*. But **focal is orthogonal to kind** — a focal node is still a step, or still a store — so it
cannot use the notch, and it no longer has a fill to rely on.

**Recommendation:** focal is carried by **stroke weight ≥ 1.6**, not by fill. The kit's `focalLight`
already uses 1.6 for exactly this reason; the ordinary `focal` kind uses 1.2 and should be raised to
match. That gives three independent channels — tag text for kind, notch for silhouette-level kind,
stroke weight for emphasis — none of which depends on hue.

---

## 4. Mandatory tags are not a mechanical sweep

Pass 3 described M3 as "a mechanical sweep, not a redesign, and the kit already emits tags — they
were simply optional." Measured against the shipped assets, that is **too optimistic**.

| Measure | Value |
|---|---|
| Files with no type tags at all | **55 of 97** |
| Node boxes shorter than 56px | **124** |
| Files containing at least one such box | **21 of 97** |
| The dominant short height | `h=48` (75 boxes) |

The problem is not vertical space alone; it is that a **left-aligned tag chip and a centre-aligned
name compete for the same horizontal band** unless the box is tall enough to separate them
vertically. At `h≥56` they clear comfortably. At `h=48` they clear by about a pixel. Below 48 they
collide, which the specimen demonstrates.

Corroboration: every option file built across the three design passes used `h=64` for tagged nodes
and dropped to `h=40` only where the node carried **no** tag. The design agent landed on the same
constraint independently without stating it.

**Consequence for M3:** making tags mandatory implies a **minimum node height of 56–64px**, so for
those 21 files the sweep is a reflow, not an annotation. That is a redesign of about a fifth of the
library.

**Options, for decision at M3:**

1. **Reflow the 21 files** — honest, and the most work.
2. **Allow a left-aligned name when the box is short** — the tag keeps the top-left, the name sits
   below it left-aligned. Cheap, and it introduces a second name alignment into the system.
3. **Exempt nodes below a height threshold from the tag rule** — cheapest, and it puts a hole in a
   rule whose whole value is being universal.

I lean to (2): it preserves the universal rule, costs no layout reflow, and a left-aligned name is
already used in the kit via its `align: 'start'` option.

---

## 5. What this changes in the plan

| Item | Change |
|---|---|
| Phase 0 notch spike | **Done.** Primitive proven, convention chosen, no blocking interaction. |
| M3 scope | **Grew.** Add the focal-stroke-weight change and a decision on short-box tags. Re-estimate: 21 files need layout attention, not just annotation. |
| M3 risk | **Raised.** It was already the sweep judged by eye; it is now also the sweep that reflows boxes. |
| `focal` node kind | Stroke weight 1.2 → 1.6, matching `focalLight`. |

The execution plan's judgement that Phase 2 is where review attention belongs is reinforced rather
than changed.

---

## 6. Artifacts

The specimen and its two renders live in the session scratchpad rather than the repo — this is a
spike, and the primitive graduates into the codebase during M3 with its own tests. The generator
above is the deliverable worth keeping.
