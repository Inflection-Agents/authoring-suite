# Design review and spec amendments

**Date:** 2026-08-14
**Reviewed:** Claude Design project `849654d7` — "Design packet: Eight diagram archetypes"
**Status:** accepted with amendments; passes 2–3 outstanding

---

## 1. What came back

Twelve built option files (six Zoom, six Contrast), six deployment worked examples, a six-diagram
applied set for High Gear, a shared builder (`build/kit.js`), and three specification documents.

The brief asked for layout grammars. It also returned two things it was not asked for, both of
which are more valuable than another archetype:

- **A routing methodology** — a reproducible procedure for turning a system description into a
  diagram *set*. See §5.
- **A builder that makes the constraints structurally unrepresentable** rather than merely
  documented. See §6.

---

## 2. What was verified, and how

Honest accounting, because "the self-check says it passes" is not verification.

**Verified by hand, end to end:** `options/zoom/zoom-1a.html`, the recommended Zoom layout.

| Check | Result |
|---|---|
| Structural coordinates on the 4px grid | **0 violations** across every `rect`, `line`, and `path` |
| Diagonal connectors | none — every `<line>` shares an axis; every `<path>` is `H`/`V` with `Q` corners |
| Label masks overlapping later-painted nodes | none; both arrow labels sit in open canvas |
| Accessible SVG contract | passes — `role`, `aria-labelledby`, first-child `<title>`, prefixed IDs, content-describing `<desc>` |
| Single-file safety | passes — no scripts, Google Fonts link only |
| Colour | every SVG attribute is `var(--dd-*)`; no raw hex |

**Audited at the builder level:** the remaining eleven option files are emitted by `build/kit.js`,
whose `hArrow`/`vArrow` constructors take a shared axis as an argument and therefore *cannot*
express a diagonal, and whose `up4`/`Math.round(n/4)*4` helpers cannot emit an off-grid structural
coordinate. Auditing the kit covers those violation classes for every file it generated; the
hand-check of 1a confirms the kit's output matches its contract.

**Accepted on their documented self-checks:** node, arrow, and accent counts per file.

### An inversion worth recording

The repo's own examples are *less* grid-compliant than the new work:

| File | Structural coords off-grid |
|---|---|
| `example-architecture.html` | 62 of 223 |
| `example-nested.html` | 16 of 74 |
| `example-quadrant.html` | 10 of 61 |
| `zoom-1a.html` (new) | **0** |

No gate checks the grid today — `SKILL.md` §7 calls it non-negotiable and nothing enforces it. See
§6 for the fix.

---

## 3. Layout decisions

| Archetype | Selected | Also adopt | Keep as documented reject |
|---|---|---|---|
| **Zoom** | **1a — frustum.** The marked box's side walls run down and flare into the walls of the detail frame, so correspondence is drawn by the geometry rather than asserted beside it. Wins the caption test before the reader reaches a label; survives squint and greyscale because the claim is carried by shape. | **1d — fish-eye**, as the second convention for the single-stage case. Reads faster but cannot open two stages, or a stage whose detail is wider than one box. | — |
| **Contrast** | **2a — shared row grid.** Parity is structural rather than stylistic: the same three row baselines and column heads run through both panels, so the collapse from three boxes to one is the only thing left to notice. Holds in greyscale with the accent removed entirely. | **2e — lopsided panels**, as the same grammar's rule for the unbalanced case: give vacated rows to a short delta ledger, never to padding nodes. | **2d — retirement in place.** One field cannot hold a baseline, and it breaks the node budget that two panels each satisfy. Ship it in the reference as a worked failure. |

Shipping a documented reject alongside the recommendation is a good practice we should adopt
generally — a type reference that shows only successes teaches less than one that shows the near
miss and says why it fails.

---

## 4. Amendments to the specification

Seven changes. Four are corrections to errors in our own material.

### 4.1 `--dd-node-white` joins the token contract — **correction**

`SKILL.md` §5 specifies a white fill for backend/API/step nodes and no role names it. White
survives today only because `lint-skin.py`'s `allowed_colors()` hardcodes `{"#fff", "#ffffff"}`.
Under a token-only regime that literal has nowhere to live, so every backend node would carry a raw
hex. All twelve option files had to declare the token themselves.

*Applied:* added to the M1 design doc §3.1 and to `CONTRACT` in the M1 plan (now 25 roles).

### 4.2 Paint order — **correction to our packet, not to `SKILL.md`**

The constraints sheet stated the order as `background → zones → arrows → nodes → labels`. That
contradicts `SKILL.md` §6 rule 6, which reasons that "nodes are painted after labels". `SKILL.md`
is right and the packet was wrong.

*Canonical order:* `background → zones → arrows → arrow labels → nodes`. Rule 6 then means what it
says. Every option file resolved the ambiguity conservatively — no label mask overlaps any node in
*either* order — which is the correct defensive reading and should become the documented rule.

### 4.3 The 4px grid exempts text baselines — **correction**

The rule as written covers "every x/y coordinate", which `SKILL.md`'s own primitives already
violate: the node pattern places tag text at `Y+15` and names at `CY+2`. Text baselines are optical
and must stay free.

*Amendment:* the grid binds structural geometry — `rect`, `line`, `path` coordinates, widths,
heights, gaps. Text baselines and font sizes below 12px are exempt. This documents existing
practice rather than changing it.

### 4.4 Budgets get a unit smaller than the diagram — **new**

A single 9-node counter cannot govern a diagram that contains two structures.

| Type | Budget |
|---|---|
| **Zoom** | Parent reduction counts as **one element**; its marks are not nodes. The expansion alone is held to 9. |
| **Contrast** | The **panel** is the unit: 9 per panel. |
| **Deployment** | Three counters: **9 container instances**, **5 deployment frames** at depth ≤3, **3 infrastructure nodes** — 17 drawn boxes. Justified because two thirds of it is containment, which is parsed pre-attentively. |

Deployment's answer to "does it survive realistic scale" is worth quoting: the real answer is *not*
a bigger budget but pairing with Zoom. An ETL's medallion stages are a container-level claim, and
forcing them into the deployment view is what turns these into wall posters.

### 4.5 Connector rule 5 applies to leaf boxes, not containment frames — **correction**

"A connector must not pass behind a box that is not its source or destination" makes every
deployment diagram unroutable, because a network edge crossing a zone boundary is the *normal*
case. Frames are painted before arrows, so nothing is actually hidden.

*Amendment:* rule 5 binds leaf nodes and container instances only. Containment frames are
crossable. Additionally, deployment draws **infrastructure edges** — routing and replication — not
application dependencies; who calls whom belongs at container level. The exception is a dependency
that leaves the zone, which is itself a deployment fact.

### 4.6 Correspondence walls are a new primitive class — **new**

The frustum's flared walls are not connectors. They carry no direction, have no marker, and join a
box to a *frame* rather than to another node. Left unclassified they trip rules 3 and 4 the moment
another connector crosses them.

*Amendment:* define **correspondence strokes** as a primitive class exempt from the connector
rules, with their own constraint: they may only join a marked element to the frame that expands it,
and there may be at most one pair per diagram.

### 4.7 Four honest abbreviations for deployment — **new**

- **Sibling collapse** — identical sibling frames become one frame with a multiplier, *only* while
  their contents are identical.
- **Replica badge** — `×N` on the instance. Stacked cards read as three different things at 50%.
- **Peer region** — one region in full, peers as a single named stack with their shape in the
  sublabel.
- **Managed service placement** — regional services sit at region level, never inside a zone; their
  zone topology is not ours.

Two ideas from vendor reference architectures were explicitly refused: vendor icons doing the work
labels should do, and subnet tiers as a fourth nesting level. Depth four is where the containment
reading collapses; a public/private split is better drawn as two zones at depth three.

---

## 5. New pillar: the routing methodology

The strongest thing in the return, and it was not asked for.

`SKILL.md` §3 is a selection *table* — it maps a thing you already know you want onto a type. There
is no procedure for going from a system description to a diagram *set*, which is the actual task
most of the time. The result today is that set composition is taste, and two runs over the same
description produce different sets.

The proposed method makes it mechanical:

> **The unit of a diagram is a claim, not a system.** Counting diagrams means counting claims.

1. **Ask first** — four mandatory questions, four conditional, never more than eight. Never ask
   about layout, colour, or type; those are consequences.
2. **Extract claims by verb.** Verb-bearing assertions only. "We use Trino" is not a claim; "dbt
   runs against Trino instead of Postgres" is two. Extracting by verb is what makes two people
   produce the same list.
3. **Classify the relation** — the relation selects the type; subject matter has no bearing.
4. **Collapse duplicates** — same relation *and* same subject means one diagram.
5. **Test against the budget** — over nine nodes, the claim spans two abstraction levels and
   becomes two diagrams joined by Zoom. Mechanical, and it forces the level split C4 wants anyway.
6. **Drop test** — write the one question each candidate answers in the audience's words; if nobody
   asks it, drop it. Applied last so it can remove diagrams but never reshape them.
7. **Order by abstraction, not chronology.** Readers descend levels; they do not follow the
   pipeline.

Plus refusal rules (a list is bullets; one box is a sentence; a trend is a chart; "these things
exist" is not a relation) and a persistence rule: record the claim inventory, the relation assigned
to each, and the audience question per diagram, and a second run reproduces the set. A reviewer who
disagrees can then point at the step that went wrong instead of relitigating drawings.

**Placement:** `references/routing.md`, loaded *before* any type reference — it is the step that
decides which type reference to load, so it sits above them in the progressive-disclosure chain.
This needs a `SKILL.md` §3 rewrite, which has byte-cap consequences (§8).

**This supersedes nothing in the set spine.** Routing decides *which* diagrams exist; the spine
guarantees they agree with each other afterwards. They compose.

---

## 6. Turn the builder into enforcement

`build/kit.js` is the missing layer between rules-in-prose and hand-placed coordinates. Its value is
not that it is a library — the model writes SVG directly — but that it demonstrates **which
constraints are mechanically checkable**, and today none of them are checked.

The repo has no gate for the grid, for diagonal connectors, for label gaps, or for accent counts.
That is why `example-architecture.html` carries 62 off-grid coordinates.

*Proposed:* extend `lint-skin.py` (or add `verify-grammar.py`) with checks the kit proves are
decidable:

| Check | Rule |
|---|---|
| Every `<line>` has `x1==x2` or `y1==y2` | §6 rule 1, no diagonals |
| Structural coords divisible by 4 | §7 grid, text baselines exempt per §4.3 |
| Accent-stroked elements ≤ 2 | §7 budget |
| Every arrow label mask has a paper fill | §6 arrow labels |

The no-diagonal check alone would be the first mechanical enforcement of the connector rules the
skill calls non-negotiable. Note the existing examples will fail these — introduce them with a
baseline, or fix the examples first.

**Do not port `kit.js` to the repo as JavaScript.** Every gate here is Python and CI installs no
Node. If a builder is wanted, it belongs as `skills/diagram-design/scripts/diagram_kit.py`
alongside `self_check.py`, which already ships with the skill.

---

## 7. Coverage: what is answered, what is open

| Open question | Answer |
|---|---|
| Deployment at realistic scale | **Answered.** Three counters, four abbreviations, and pairing with Zoom rather than a bigger budget. |
| Code-level diagram worth drawing | **Still open.** Marked "open question" in their own C4 table; no option set built. |
| Lineage distinct from Tree | **Not reached.** Pass 1 covered Zoom and Contrast only. |
| Dynamic view | **New finding.** Reclassified from "mostly covered" to a **real gap**: Sequence answers it by changing the layout, which discards the architecture the reader just learned. Solved **without a new type** — a numbered step marker plus a key strip over the existing topology. This becomes a *primitive*, not an archetype. |
| Level traversal | Confirmed as **the load-bearing addition**. Without Zoom, C4 levels ship as unrelated files — the problem the audit opened with. |

**Outstanding:** option sets for Lineage, Matrix, Hub & spoke, Composition, and Code structure
(passes 2 and 3). Deployment has worked examples and a budget proposal but not a six-option set.

---

## 8. Roadmap changes

| Milestone | Change |
|---|---|
| **M1 — portability** | `--dd-node-white` added to the contract (25 roles). Otherwise unchanged and still first. |
| **M1.5 — grammar enforcement** | **New.** The §6 linter checks. Small, and it should land before archetypes so new types are born enforced rather than retrofitted. |
| **M2 — archetypes** | Zoom (1a + 1d) and Contrast (2a + 2e, 2d as documented reject) are ready to write up. Amendments §4.4–4.6 land with them. |
| **M2.2 — routing** | **New.** `references/routing.md` plus the `SKILL.md` §3 rewrite. Arguably belongs *before* M2: it is the layer that decides a type is needed at all. |
| **M2.4 — selection guidance and gallery** | **New.** Per-variant "which variant" rules with a named default, and the gallery re-indexed by relation so it becomes the visual front end of the routing table. See `2026-08-14-selection-guidance-and-gallery-design.md`. |
| **M2.5 — set spine** | Unchanged. Composes with routing. |
| **M3 — visual grammar** | Unchanged; add the dynamic-view step-marker primitive here. |

**Byte-cap warning.** `SKILL.md` had 2,594 bytes of headroom before any of this. The §3 routing
rewrite plus two new type rows plus the amended §6 and §7 will exceed it. Since this fork is a
branded derivative, raising the cap is available — but it should be a recorded ADR with a new
number, not a silent edit, because the cap exists to keep the installed skill cheap to load.
