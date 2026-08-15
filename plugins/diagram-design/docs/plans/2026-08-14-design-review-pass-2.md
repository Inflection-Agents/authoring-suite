# Design review — pass 2

**Date:** 2026-08-14
**Reviewed:** Claude Design project `849654d7`, `Pass 2 - Four Archetypes.dc.html`
**Covers:** Lineage, Matrix, Hub & spoke, Composition
**Status:** accepted

---

## 1. Headline: the taxonomy grows by four, not six

Two of the four proposed archetypes came back with answers that *reduce* what we ship. Both are
reasoned rejections of my framing, and both are right.

| Archetype | Verdict | Type count |
|---|---|---|
| **Lineage** | Keep — but redefined. Distinct because of the **DAG**, not the direction. | +1 |
| **Matrix** | Keep, **and retire `type-dp-security-matrix` as a preset of it**. | **net 0** |
| **Hub & spoke** | **Not a type.** Conventions on Architecture — a reference page, not a layout grammar. | **0** |
| **Composition** | Keep. Distinct from Nested because the parts outlive the whole. | +1 |

Running total for the archetype programme: 27 existing + Zoom + Contrast + Lineage + Composition +
Deployment = **32**, with Matrix and Hub & spoke costing nothing. Code structure remains undecided.

The method that produced both reductions is worth noting: each option set contained one option
**designed to fail in a specific way**, and the failures settled the questions. That is a practice
to carry into our own type references.

---

## 2. Lineage — keep, but the definition changes

**Selected: 3a, hop columns.** Holds provenance and impact simultaneously, keeps the multi-parent
case intact, and carries direction with two named bands plus edge weight so it survives greyscale.

**The distinctness answer overturns my framing.** I asked whether Lineage is Tree with directional
encoding added. It is not, and direction is not the differentiator:

> A flipped Tree would draw a single-parent lineage perfectly. What Tree cannot draw is a DAG — and
> option 3c shows exactly what happens when you try: `mart_revenue` has two parents, so the outline
> draws it twice and the reader cannot tell one asset from two.

*Amendment:* define the type as **"DAG with one selected node and cohort aggregation"**, never as
"Tree with direction". The multi-parent case is the reason the type exists, so the reference must
lead with it and `type-tree.md` must say explicitly that a second parent means reaching for Lineage.

**Budget:** three hops each side of the focal, three assets per hop column, cohort nodes exempt
because an aggregation is not an asset. Note the binding constraint here is **arrows, not nodes** —
3c hit the 12-arrow ceiling before the node ceiling.

---

## 3. Matrix — keep, and retire one

**Selected: 4a, framed cells.** The frame is what makes an empty cell read as an empty container
rather than a hole in the layout.

**Two findings settle open questions.**

*What makes it a diagram rather than a grid of text:* only the **marked region** and **deliberate
emptiness**. Take either away and it should be a table. This sharpens the refusal rules — an
unmarked matrix is a table with extra steps.

*The accent collision dissolves rather than needing a counter.* I flagged that marking a column
means accenting three cells and breaking the two-accent budget. The answer:

> A region is ONE accent element however many cells it spans.

That is the right resolution and it generalises — an accent counts occurrences of *emphasis*, not
of shapes. Worth stating in §7 as a general clarification, because the same question will arise for
any type that marks a group.

*Type-count consequence.* `type-dp-security-matrix.md` is the only thing currently serving the
`two-dimensions` relation, and it is the general form hard-coded to one domain. Ship the general
Matrix and **retire the DP security matrix as a documented preset of it**. Net type count unchanged,
and a domain-specific name stops sitting in a general-purpose library.

**Budget:** 4×4 maximum, nine chips total, marked region counts as one accent.

---

## 4. Hub & spoke — a grammar, not a type

**The most valuable answer in the pass, because it is a "no".**

> Loop puts stations around a hub but asserts a cycle. Architecture already draws this freehand —
> what is missing is the conventions (identical spokes, tag-carried direction, cohort past six),
> which is a reference page, not a layout engine.

This is exactly the ADR-0002 test applied correctly: no new *layout grammar* exists, so no new type
is warranted. It saves a full shipping set — reference, three variants, example triple, gallery
registration, ADR.

*Placement:* conventions go into `type-architecture.md`, or a semantic pattern routing to
Architecture if we want it discoverable from the routing table. I lean toward the semantic pattern,
because `one-serves-many` is a relation in the routing table and needs somewhere to point.

**Selected layout: 5b, flanking columns.** Every spoke shares its `y` with its attach point, so the
drawing contains **zero elbows**, and a tenth spoke costs one row. Permit **5a radial at six spokes
or fewer** when the canvas has room — radial is the better picture when it fits.

**Where radial breaks, and why it is not the reason I predicted.** I expected attach-point fanning
to be the binding constraint. It is not:

> A 200px hub edge takes three points 50px apart comfortably. What breaks is that orthogonal routing
> places spokes on a grid rather than a circle, so past six the distances to the hub become unequal —
> 96px for the centre spokes against 168px for the corners — and the spokes stop reading as
> interchangeable, which is the one thing this archetype exists to assert.

The constraint that kills radial is **semantic, not geometric**. That is a better finding than the
one I asked for, and it generalises: when a layout's meaning depends on elements reading as
equivalent, unequal spacing is a correctness bug, not an aesthetic one.

*Also settled:* publish versus subscribe is carried by a **tag inside the box**, never by which side
of the hub a spoke sits on. Position already means "interchangeable"; overloading it with direction
breaks that.

**Budget:** six drawn spokes plus one cohort node with a count. Past six, radial is not permitted.

---

## 5. Composition — keep, and a general rule for correspondence

**Selected: 6a, column alignment.** Each drawn part sits directly beneath its catalog entry, so
correspondence needs three straight rails that cannot cross, and the bespoke remainder identifies
itself as the one box with no column above it.

**Distinctness:** Nested asserts containment *in place*; Composition asserts that the parts exist
independently of the whole and outlive it. Nothing in the library has a slot for the **bespoke
remainder**, which is the element that makes the diagram credible rather than idealised.

**The spaghetti answer generalises into a rule worth promoting beyond this type:**

> Refuse edges and spend position instead.

| Condition | Mechanism |
|---|---|
| Assembly order can match catalog order | **Shared position** — alignment, no strokes |
| Assembly order must differ | **Numerals** (`keyNum`), still zero strokes |
| Only the count matters | **Set membership** with one edge |
| — | Four edges from four parts to one assembly is never the answer |

That last line is the important one: the no-overlap constraint was doing its job, and the correct
response to a constraint that keeps firing is a different mechanism, not an exemption.

**Budget:** the catalog is one element — the same treatment Zoom gives the parent reduction — and
the assembly is budgeted at six parts plus one remainder.

---

## 6. New primitives entering the kit

Four additions and one node kind, all of which need homes in the primitive references:

| Primitive | Purpose | Where it belongs |
|---|---|---|
| `focalLight` node kind | Border-only focal — no fill, 1.6 stroke. For cases where geometry already grants prominence and a filled focal over-eggs it. | `style-guide.md` node treatments |
| `emptyMark` | A hairline in a deliberately empty cell. **Never a blank.** | `type-matrix.md` |
| `chip` | Matrix cell contents | `type-matrix.md` |
| `countBar` | Quantity as bar length, for cells holding a count rather than instances | `type-matrix.md` |
| `keyNum` | Numeral key — correspondence with zero strokes | `type-composition.md`, and the general correspondence rule in §5 |

All five are grid-safe by construction: `emptyMark` spans `cx ± 16`, `keyNum` is `16×16`,
`countBar` is `n × 24` wide, and `chip` takes caller coordinates like `node` does.

`focalLight` is worth adopting generally, not just for hubs. It answers a question the current node
table cannot: how to grant focus to something the layout already emphasises.

---

## 7. Amendments carried forward

Additions to the amendment list from pass 1 (§4 of the pass-1 review):

**4.8 — An accent counts emphasis, not shapes.** A marked region is one accent element however many
cells or nodes it spans. Resolves the Matrix collision and pre-empts the same question for any type
that marks a group.

**4.9 — Correspondence is carried by position before strokes.** Alignment, then numerals, then a
single set-membership edge. N edges from N parts to one target is never correct. Generalises §4.6's
correspondence-stroke class into a precedence order.

**4.10 — Equivalence requires equal spacing.** Where a layout's meaning depends on elements reading
as interchangeable, unequal spacing is a correctness failure, not a style choice. This is what caps
radial hub layouts at six.

**4.11 — Ship a documented failure with each type.** Each pass-2 option set included one option
built to fail in a specific way, and those failures settled the open questions. Type references
should carry the near-miss and say why it fails.

---

## 8. Roadmap changes

| Milestone | Change |
|---|---|
| **M2 — archetypes** | Now six types, not eight: Zoom, Contrast, Lineage, Matrix, Composition, Deployment. Matrix lands with the DP security matrix retired to a preset in the same PR — one concern, one PR. |
| **M2 — hub & spoke** | Reclassified out of M2 into a semantic pattern routing to Architecture. Pattern cost: one section plus a routing row. |
| **M2.2 — routing** | Unchanged; the `one-serves-many` row now points at the pattern rather than a type. |
| **M2.4 — selection guidance** | Gains the pass-2 variant rules: Lineage 3a default; Matrix 4a default; Hub 5b default with 5a permitted at ≤6 spokes; Composition 6a default with 6b when order differs and 6c when only the count matters. |
| **M3 — visual grammar** | Gains `focalLight` as a general node treatment. |

**Still outstanding:** Code structure (archetype 7) — unbuilt, and their C4 table still marks the
level itself an open question. Given Hub & spoke came back as "not a type", it is worth asking the
same question of Code structure before commissioning a pass 3.
