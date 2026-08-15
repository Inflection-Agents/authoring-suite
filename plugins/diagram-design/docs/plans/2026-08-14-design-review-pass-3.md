# Design review — pass 3

**Date:** 2026-08-14
**Reviewed:** Claude Design project `849654d7`, `Pass 3 - Code Level, Node Kinds, Dynamic View.dc.html`
**Covers:** node-kind encoding, the code level (class + entity), the dynamic-view primitive
**Status:** accepted, with one implementation gap flagged

---

## 1. Headline

Three results, and the first one pays for the other two.

| Item | Result | Type cost |
|---|---|---|
| **B · Node kinds** | Promote the type tag to the load-bearing kind channel, mandatory on every node; pair with a corner notch for distance. | — |
| **A · Code level** | **One type, two presets.** The existing ER type becomes the entity preset. | **0** |
| **C · Dynamic view** | Key strip below the host diagram. A primitive, not a type. | — |

**Final type count for the whole archetype programme: 32.** Every one of the eight proposed
archetypes has now landed, and three of them cost nothing — Matrix absorbed the DP security matrix,
Hub & spoke became a semantic pattern, and the code level absorbed ER.

---

## 2. Item B — node kinds

This closes the defect measured at the very start of the review: seven node kinds separating almost
entirely by fill opacity at 2–5% of ink, with **ten of fifteen pairs below 1.10:1** composited
contrast. `store` against `external` was 1.04:1.

**Selected: B1 (semantic tag) and B4 (corner notch), in that priority order.**

> The lightest second channel is the one that already exists and is made of words: promote the type
> tag from decoration to the load-bearing kind channel, mandatory on every node. A tag reading
> `STORE` needs no legend **because it is the legend, inline** — which is why it beats a shape
> grammar that has to be learned before it can be read.

That argument is the right one for this system. A shape grammar buys silhouette-level distinction at
the cost of turning every diagram into a notation the reader must learn first; the tag was already
in the node anatomy and was simply optional.

**The tag fails exactly one test**, and the second channel exists to cover it: at 50% a 7px tag is
unreadable. The **corner notch** — zero, one, or two clipped corners — carries three
silhouette-level states for the distinction that survives distance: *a thing that runs*, *a thing
that stores*, *a thing outside our control*. Two channels, no hue, nothing to memorise.

**Rejections worth keeping.** B3, a stroke weight-and-dash system, is rejected because it needs a
legend. B5, a coloured left rule, is rejected **despite performing best mechanically**, because a
coloured left border is the house style of every product-UI callout on the web and therefore reads
as "notice" rather than "kind". That is a taste rejection with a real argument behind it, and it is
the kind of judgement a linter could never make.

**Fills stay, but stop being load-bearing** — decoration reinforcing a channel already carried by
text and silhouette. This is the right disposition: it means the existing 104 examples do not look
wrong, they are simply under-specified.

### Implementation gap — flagged

**The notch is not in the kit.** `build/kit.js` emits tags (and always could), but `node()` still
draws a plain `rect` with `rx`; the corner notch exists only as bespoke markup inside
`options/kinds/kinds-b4.html`. Half the recommendation is therefore specified in prose only.

A notch primitive is a prerequisite before the encoding can be applied across 32 types — a clipped
corner needs a `path`, not a `rect`, which also interacts with `--dd-radius-node`. Worth resolving
before M3 starts rather than discovering it mid-sweep.

---

## 3. Item A — the code level

**Selected: A1 for the class preset, A4 for the entity preset. One type, two presets.**

The unification argument is specific rather than a family resemblance, which is what makes it
convincing:

> Both traditions need exactly two classes of line — **structural** ("this is that", "this owns
> that") and **referential** ("this uses that", "this points at that") — and both need a second
> vocabulary layered on top. UML spends arrowheads on that second vocabulary; ER spends crow's feet.
> Replace both with a **text token at the line's endpoint** and the two notations become the same
> grammar with different token sets.

So `is-a` and `owns` in one preset, `1` / `N` / `0..1` in the other — same slot, same 8px mono, no
legend needed in either case. **Crow's foot survives only as text.** The `endToken` primitive added
to the kit is what carries it.

This also answers, in one move, the three questions the brief posed separately: stereotypes,
relationship kinds, and crow's-foot cardinality.

### What each preset overrides

| Aspect | Entity preset | Class preset |
|---|---|---|
| Box | name + `ENTITY` or `JOIN` tag | name + `INTERFACE` / `ABSTRACT` / `CLASS` / `ENUM` tag |
| Structural line | identifying relationship | inheritance, realization, composition |
| Referential line | nullable or non-identifying FK | depends-on, uses |
| Endpoint token | `1` · `N` · `0..1` | `is-a` · `owns` |
| Compartment | keys only; no field types | nothing, or ≤3 responsibilities in prose |
| Layout convention | join entity sits between its parents | declarations on the row above their implementations |
| Many-to-many | always reified; no `N—M` line exists | not applicable |
| Self-reference | orthogonal loop above the box, or an inline token | rare; same loop if needed |

Everything not in that table is shared.

### Member detail

My prior held, with one correction worth adopting as a general rule:

> **Keys are shape; field types are transcription.** A foreign key determines the relationship
> structure, so it earns its line; a `varchar(255)` does not.

A3 is the documented failure and it measures the cost rather than asserting it: full compartments
triple each box's height, the nine-type scenario drops to four, and both hierarchies leave the
canvas.

### Type-count consequence

The routing check produced the finding:

> The relation is `is-a / has-a / depends-on` among declared types, and it is distinct from every
> relation in the table — but it is **not** distinct between the two scenarios, which is the
> finding. The existing ER type does serve half of it, so **ER becomes the entity preset rather than
> a casualty**.

Same outcome as Matrix. The code level ships for free.

### Budget

Count **edges, not types**: nine boxes and ten edges, with the unit being **one cluster** — a focal
type plus its direct neighbours and whatever it realizes. Real schemas exceed that immediately, so
the code level **pairs with Zoom exactly as Deployment does**: the package is the parent diagram,
the cluster is the detail.

That is now three types resolving scale the same way. It should be stated once as a general
principle rather than three times as a local rule.

### Staleness — three enforceable rules

The best part of the answer, because two of the three are machine-checkable:

1. **Cap the compartment at three lines.**
2. **Reject any compartment line containing a colon or a bracket pair** — that is what a linter can
   see, and what transcription always contains.
3. **Require the title to state a claim.** A diagram that only transcribes has nothing to put there,
   so the rule fails loudly rather than rotting quietly.

Rule 3 is the elegant one: it makes the failure mode surface at authoring time instead of six months
later.

---

## 4. Item C — the dynamic view

**Selected: C1, key strip below.** All three options overlay the same untouched host diagram, which
is the test a primitive has to pass.

**The four answers requested:**

- **Seven steps is the ceiling.** Past that the reader is counting rather than reading, and a
  sequence longer than seven belongs to the Sequence type.
- **The strip sits below a hairline and costs 104px of height.** A margin rail costs 240px of width
  and would force the host to be redrawn — which disqualifies it as a primitive outright. That is
  the correct disqualifying test: a primitive that reshapes its host is not a primitive.
- **When one step touches three elements**, place one numeral on the connector where the step
  begins and name the other elements in the key line. **Never repeat a numeral** — the count is the
  reading, and a repeated numeral destroys it.
- **Markers count against neither budget.** They are labels and obey §6 — 8px clear of the stroke,
  opaque mask, never on the line — but they get their own cap of seven, and the key strip is
  **mandatory above four steps**.

**A step with no connector to attach to is not a step.** Fold it into the wording of the step that
has one. (Their example: Trino shutting down.)

C3 is the documented failure: with no key strip, every step must fit fourteen characters, at which
point *"Trino starts, runs five models, stops"* becomes `4 MODEL` — and an ordinary arrow label
would have done the job.

---

## 5. Amendments carried forward

Continuing the numbering from passes 1 and 2:

**4.12 — Kind is carried by text and silhouette, never by fill.** The type tag is mandatory on every
node and is the primary kind channel. The corner notch is the secondary channel for distance. Fills
reinforce; they no longer signify.

**4.13 — Relationship vocabulary is text at the endpoint, never arrowhead shape.** Replaces both
UML's arrowhead set and ER's crow's feet with a token in the same slot. Applies wherever a
relationship needs a second vocabulary beyond direction.

**4.14 — Transcription has a machine-visible signature.** A compartment line containing a colon or a
bracket pair is transcription, not shape, and is rejected. Compartments cap at three lines.

**4.15 — Step markers are labels, not nodes.** They count against neither the node nor the arrow
budget, carry their own cap of seven, and require a key strip above four.

**4.16 — Scale is resolved by pairing with Zoom, not by raising budgets.** Deployment, the code
level, and any future type whose real-world instances exceed the budget state their unit and pair
with Zoom. Stated once as a principle.

---

## 6. Roadmap changes

| Milestone | Change |
|---|---|
| **M2 — archetypes** | Now **six types**: Zoom, Contrast, Lineage, Matrix, Composition, Deployment. Plus the code level, which lands as a rename-and-generalize of `type-er.md` rather than a new file. |
| **M2.4 — selection guidance** | Gains the code-level preset rule (entity vs class), and the dynamic-view "reach for this when" (overlay when the host architecture must survive; Sequence when it need not). |
| **M3 — visual grammar** | **Now fully specified.** Mandatory tags plus corner notch across all 32 types. Blocked on a notch primitive (§2). |
| **M3 — new prerequisite** | A `notch` primitive in whatever builder we ship, since a clipped corner needs a `path` and interacts with `--dd-radius-node`. |
| **M1.5 — grammar enforcement** | Gains two checks: the compartment transcription test (colon or bracket), and tag-presence on every node. |

### Sequencing consequence — important

Item B is **retrospective**. Mandatory tags and the notch apply to all 32 types *and* all 104
existing examples, which is a second full sweep of the asset base after M1's token migration.

These two sweeps must not be combined, and the order matters:

- **M1 PR 3 asserts raster-identity** — the token migration changes nothing visually, verified by
  byte-identical PNGs.
- **The M3 tag sweep is a visual change** — it adds tags where they were absent and clips corners.

So M3 must land after M1, in its own PR, reviewed by looking at the output rather than by asserting
it did not change. Running them together would destroy the one verification property that makes the
M1 migration reviewable at all.
