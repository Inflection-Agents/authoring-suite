# Primitive — the corner notch

Second channel for node kind, for the distance and greyscale cases where the mandatory type tag
(§5 in `SKILL.md`) becomes illegible: a 7px tag is unreadable at 50% zoom or on a projector, but a
clipped corner still reads at silhouette level. Two channels, no hue, nothing to memorise. Settled
in `docs/plans/2026-08-14-notch-primitive-spike.md`; this file is where the primitive graduates from
spike to shipped reference.

## Scope — which diagrams use it

The notch is not universal. It encodes **system-component kind** — a thing that runs, a thing that
stores, a thing outside the system boundary — and that concept only exists in diagrams whose nodes
represent infrastructure or process components: `architecture`, `data-flow`, `dp-integration`,
`high-level`, `it-state`, `swimlane`, `sequence` (its actors), `deployment` (container instance /
store / infrastructure), and the draw.io/Mermaid import and animated examples that redraw these.

**`deployment` (Phase 3) extends this scope, not an exception to it.** Its three kinds map onto
the existing vocabulary directly: a container instance (API, Worker) *runs* — 0 notch, same as
`backend`; a database instance *holds* — 1 notch, same as `store`; a load balancer or DNS service
is infrastructure the application doesn't control — 2 notches, same as `external`. This is also
where the "may need shape, not just fill" question from the M2 archetype design brief gets
answered directly: fill/opacity alone was judged too weak to separate three kinds sharing a
canvas with dashed *deployment-node* containers already using transparency as a fourth signal, so
`deployment` is the first type to lean on the notch for its primary kind-distinction rather than
as a secondary channel behind the tag chip.

It does **not** apply to types with their own, different kind vocabulary — `flowchart` (decision /
process / terminal), `state` (the state's own name is its identity), `tree` (category / leaf / root),
`er` (entity / join — a code-level concept), `org-chart` (role / pod). Several of these coincidentally
reuse the same `--dd-wash-5`/`--dd-muted` fill pair that `store` uses elsewhere, for depth or tier
emphasis — that is a token-reuse coincidence, not a claim that a tree's leaf skill is a database, and
notching it would misrepresent the diagram. Nor does it apply to types with no discrete "nodes" at
all: the chart types (`bar`, `line`, `gantt`, `scatter`, `radar`), or types whose boxes represent
something else entirely (`pyramid`'s ranked tiers, `venn`'s set regions, `quadrant`'s plotted items,
`timeline`'s events, `nested`'s containment depth, `layers`'s abstraction tiers, `loop`'s flywheel
stations) — these already carry an identifying label in their own idiom and gain nothing from a
kind taxonomy that does not describe them.

When a type already has its own complete, working kind-signal, prefer extending that system's own
vocabulary over grafting an unrelated chip onto it. The goal is legible kind, not a uniform chip on
every box regardless of fit. Two documented cases:

- **`it-state` and `dp-integration`'s source/consumer sides** mark kind with an icon (database,
  file, stream, chart, notebook, API glyph) plus a CSS modifier class (`.node.external`,
  `.node.focal`, `.node.survivor`, `.side-node`, `.core-node`) rather than a text tag chip. An icon
  is at least as legible as three mono letters and needs no translation; retrofitting a chip beside
  it would clutter a box that already reads its kind at a glance.
- **Any node at `h=48` that already carries a name *and* a technical sublabel** has no third line to
  spend on a tag — the left-align fallback in the next section assumes a two-line box (tag + name),
  not three. `swimlane`'s step boxes (`gh pr create`, `astro build`) and `tree`'s leaf-skill tier
  (`align · space · rhythm`) both hit this. Where the boxes are also all one kind — `swimlane`'s are
  uniformly `backend` — a tag would repeat the same word on every box with no differentiating value
  regardless of space. Reflowing to `h=64` to make room properly is real layout work, deferred to the
  same pass that reflows the other 20 short-box files identified in the M1 decision log rather than
  done once, ad hoc, here. Where a box has a name only, no sublabel, and is short only because it
  wasn't designed with a tag in mind — `org-chart`'s specialist tier was this case at `h=56`, already
  clear of the floor — add the tag properly instead of exempting it.

## The primitive

A clipped corner needs a `path`, not a `rect` — `rx` rounds every corner uniformly and cannot leave
one chamfered while the rest stay round.

```python
def notched_rect(x, y, w, h, r=2, n=8, corners=()):
    """corners subset of {'tl','tr','br','bl'} are chamfered at depth n; the rest are rounded at r."""
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

`r` reads `var(--dd-radius-node)` exactly as a plain `rect`'s `rx` would; chamfered corners ignore
it, so a brand's radius token can be 0, 2, or 8 without touching notch geometry. Depth `n=8` at full
size; the specimen stays legible at 50% with `n=4`. With `x, y, w, h, n` on the 4px grid, every
emitted coordinate stays on the grid — only `r` sits off it, exactly as `rx` does today.

**No conflict with the no-diagonal-connector rule** (`SKILL.md` §6). That rule targets `<line>`
connectors between nodes; a chamfer is a diagonal *edge of a shape*, inside a `<path>`. Do not "fix"
it later.

## Convention — Convention A

One notch: top-right. Two notches: top-right **and** bottom-right — both clips on the same edge,
so they read as one silhouette feature (a chevron-ish cut) rather than two unrelated corner events.
The rejected alternative (top-right + bottom-left, diagonally opposite) reads as two separate
mistakes rather than one shape, and is weaker at distance.

## Kind → notch mapping

| Kind | Fill / stroke | Notches | Corners |
|---|---|---|---|
| `backend` (runs) | white / `ink` | 0 | — |
| `store` (holds) | `ink @ 0.05` / `muted` | 1 | top-right |
| `external` (outside our control) | `ink @ 0.03` / `ink @ 0.30` | 2 | top-right, bottom-right |
| `input` (outside our control) | `muted @ 0.10` / `soft` | 2 | top-right, bottom-right |
| `optional` | `ink @ 0.02` / `ink @ 0.20` dashed | inherits its base kind | — |
| `security` | `accent @ 0.05` / `accent @ 0.50` dashed | inherits its base kind, default 2 | top-right, bottom-right |
| `focal` | `accent-tint` / `accent` | inherits its base kind if known, else 0 | — |

**`input` groups with `external` at two notches.** Both sit at the system boundary — a user is as
far outside programmatic control as a third-party service — and grouping them keeps the "outside our
control" reading coherent for both.

**`optional` and `security` are modifiers, not base kinds** — like `focal`, they can apply to any of
the three base kinds above (an optional *store*, a security-gated *backend* service) and their dash
pattern already carries that distinction. Where the underlying base kind is legible from the node's
own tag or name, notch it accordingly; `security` defaults to 2 (a boundary concept fits "outside
normal flow"), and an untaggable `focal` node defaults to 0 rather than guess.

## Focal is orthogonal to kind

A focal node's fill and stroke already override its kind's colour, so the notch reflects whatever
kind the node would carry without the focal treatment — focal changes stroke weight, not silhouette.
**Stroke weight rises from `1.2` to `1.6`** on focal nodes (matching the emphasis weight
`SKILL.md`'s summary-card pattern already uses) — the accent fill and accent stroke both collapse to
the same grey in a greyscale render, and `1.2` against the default `1.0` is not a perceptible
difference at that point. `1.6` is.

## Short boxes: left-align instead of reflow

A left-aligned tag chip and a centred node name compete for the same horizontal band below 56px of
box height. Per the M1 decision log (execution plan §4.2): boxes at 56px and above keep the
centred, two-line treatment (tag chip top-left, name centred, sublabel centred below). Boxes below
56px put the tag and the name on **one line, left-aligned**:

```svg
<rect x="X+8" y="Y+H/2-6" width="24" height="12" rx="2" fill="transparent" stroke="STROKE@0.40" stroke-width="0.8"/>
<text x="X+22" y="Y+H/2+3" fill="STROKE@0.8" font-size="7" font-family="'Geist Mono', monospace"
      text-anchor="middle" letter-spacing="0.08em">API</text>
<text x="X+40" y="Y+H/2+4" fill="var(--dd-ink)" font-size="11" font-weight="600"
      font-family="'DM Sans', sans-serif" text-anchor="start">Node Name</text>
```

No sublabel in a left-aligned short box — there is no vertical room for a third line. If the
technical detail matters, it belongs in the sublabel of a taller sibling node, not crammed in here.
