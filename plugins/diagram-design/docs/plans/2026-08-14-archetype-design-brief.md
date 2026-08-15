# Design brief — eight diagram archetypes

## What this is

We maintain an editorial diagramming system with 27 visual types. Two completeness audits found
eight relations that no existing type can express. We need **layout grammars** for them.

The first audit asked *what relation does a diagram assert* — containment, sequence, comparison,
and so on — and found six missing. The second used the C4 model as a yardstick for *levels of
abstraction*, and found that we can draw a system at context, container, and component level but
not at code level, and that we have no way to draw deployment topology at all. Those are
archetypes 7 and 8.

We are borrowing C4's abstraction hierarchy and its discipline of giving every element a name, a
type, and a technology. We are **not** borrowing its notation, which crams four lines of text into
every box and needs a legend to read. Our register is the answer to that.

We are not asking for styling — the visual language is already settled and given to you in
`01-CONSTRAINTS.md` and `02-TOKENS.css`. We are asking for **structure**: where things sit, how the
relationship is drawn, and what makes the claim legible without a caption.

## What we need from you

For **each** archetype below, produce **4–6 genuinely different layout options** — different
structural ideas, not recolourings or nudges of one idea. For each option:

1. A **built HTML file** following `examples/template.html`, using the real scenario content given.
2. A **two-sentence rationale**: what structural idea it commits to, and what it trades away.

Then, for each archetype, a short **recommendation** naming your strongest option and why.

We will lint every submission against the constraints and reject anything that violates them, so
please treat `01-CONSTRAINTS.md` as a specification rather than guidance. The connector rules
(§2) and the 4px grid (§1) are where designs most often fail.

## The test each design must pass

> Can a reader reconstruct the relationship **without reading the caption**?

Secondary tests, all of which matter:

- Does it hold at 50% scale (a slide seen from the back of a room)?
- Does it survive greyscale? Assume colour is decoration, not information.
- Does it still work at the maximum node count in the budget, not just the example count?
- Does it degrade gracefully when the data is lopsided — one side much larger than the other?

## House register

Read `examples/example-architecture.html`, `example-nested.html`, and `example-quadrant.html`
before starting. The register is **editorial, not technical-decorative**: warm paper, hairline
rules, sharp corners, one accent used sparingly, generous negative space, no shadows or gradients
anywhere. Think a well-set printed diagram in a design annual, not a cloud-vendor reference
architecture.

---

# Archetype 1 — Zoom (overview + detail)

**Priority: highest.** Our own documentation instructs authors to "split into an overview + detail"
in three separate places and then provides no way to draw the relationship, so today the two halves
ship as two unrelated files.

**Relation encoded:** *detail-of*. "The box you already saw contains this."

**Required elements**
- A reduced reproduction of a parent diagram, with exactly one element marked.
- An expansion of that element occupying the majority of the canvas.
- An explicit visual correspondence between the marked element and the expansion.

The correspondence is the entire content of this archetype. If a reader cannot instantly tell
*which* box was opened, the design has failed regardless of how good it looks.

**Properties to explore**
- **Reduction strategy:** true-scale miniature, schematic abstraction, or simplified silhouette.
  Whatever you choose must keep the marked box identifiable at that size.
- **Correspondence mechanism:** a connector, a wedge/frustum joining the marked box to the
  expansion frame, matched stroke treatment, a shared label, or a cut-away.
- **Parent placement:** corner inset, left rail, top strip. Each implies a different reading order —
  say which you intend.
- **Quieting the parent** without making it illegible. It is orientation, not content.
- Whether the expansion sits in its own frame or bleeds to the canvas edge.

**Failure modes**
- Parent thumbnail so small the marked box cannot be identified.
- Parent redrawn differently from the original, breaking the reader's continuity.
- Parent competing with the expansion for attention.
- Correspondence implied by position alone.

**Scenario to build**
Parent: an ingestion platform — `Sources` → `Ingest Gateway` → `Transform` → `Warehouse` →
`Serving API`, with `Observability` beneath. Mark **Transform**. Expansion shows Transform's
internals: `Schema Registry` → `Validate` → `Normalise` → `Enrich` → `Quarantine` (branching off
Validate on failure). Focal element: `Quarantine`.

---

# Archetype 2 — Contrast (before / after)

**Priority: highest.** The workhorse of any "why change" argument, and completely absent.

**Relation encoded:** *differs-from*. "The current state is broken; the proposed state is better."

**Required elements**
- Two panels of identical width with identical internal structure.
- State labels, never judgements: `Today` / `Proposed`, not `Bad` / `Good`.
- The single difference marked in the right panel only.

The mirroring *is* the argument: because the panels are structurally the same, the one difference
between them becomes unmissable. Left panel is the baseline and must read as entirely ordinary.

**Properties to explore**
- **The divider:** hairline rule, gutter alone, or a labelled transition marker between panels.
- **How parity is made visible:** aligned baselines across panels, matched node sizes, shared row
  positions, a shared background grid.
- **Marking the difference** using accent in the right panel only, within the 2-accent budget.
- Whether a **delta ledger** (a short list of what changed) earns its place, and where it sits.
- **The lopsided case**, which is the most common real shape: the right panel has fewer nodes than
  the left. Show how the layout holds when one side is half-empty — this is where most before/after
  diagrams collapse.

**Failure modes**
- Panels with different internal structure — the reader cannot diff them, so it becomes two
  unrelated diagrams side by side.
- Strawmanning the left panel by drawing it more crowded than reality. Sophisticated audiences
  notice and the whole argument loses credibility.
- Highlighting both panels, which destroys the baseline.
- Three panels. A third state is a sequence of states, not a contrast.

**Scenario to build**
Today: three product teams each running their own `Auth`, `Billing`, and `Audit` service —
nine boxes, three columns. Proposed: one shared `Platform Core` providing all three, with the same
three product teams consuming it. Focal: the shared core.

---

# Archetype 3 — Lineage (provenance and impact)

**Priority: high.** Distinct from our existing Tree type, which has no notion of impact direction,
and from Data flow, which has no notion of transitive depth.

**Relation encoded:** *derived-from*, transitively, plus *impact-if-changed* in the reverse
direction.

**Required elements**
- A directed acyclic graph of assets, not a strict tree — an asset may have several parents.
- One selected asset.
- Its **upstream** (what it derives from) and **downstream** (what breaks if it changes) visually
  distinguished from each other.
- Transitive depth legible: direct dependency versus two hops away.
- Assets outside the selected asset's lineage visibly de-emphasised or excluded.

**Properties to explore**
- **Axis choice:** upstream-left/downstream-right, or upstream-above/downstream-below. Say why.
- **Encoding direction** without relying on arrowheads alone — a reader scanning quickly must see
  which side is cause and which is effect.
- **Showing depth**: columns per hop, indentation, edge weight, or explicit hop labels.
- **The fan-out problem**: a real lineage graph has one asset feeding 30 others. Show how you
  aggregate — a cohort node with a count is acceptable, silent truncation is not.
- Whether **freshness or ownership** metadata earns space, or belongs in a sublabel.

**Failure modes**
- Drawing it as a tree and losing the multi-parent case.
- Upstream and downstream rendered identically, so the reader cannot tell cause from consequence.
- Every asset in the graph shown, defeating the purpose of selecting one.
- Crossing edges everywhere — this archetype lives or dies on node ordering.

**Scenario to build**
Selected asset: `dim_customer`. Upstream: `raw_crm_contacts` and `raw_billing_accounts` feed
`stg_customer`, which with `stg_region` feeds `dim_customer`. Downstream: `dim_customer` feeds
`fct_orders` and `mart_revenue`, and `fct_orders` also feeds `mart_revenue` plus a cohort of
**12 dashboards**. Focal: `dim_customer`.

---

# Archetype 4 — Matrix (categorical grid)

**Priority: medium.** We have a role-by-component permissions grid hard-coded to one domain; we
need the general form.

**Relation encoded:** two independent dimensions varying at once, where the *combination* is the
insight.

**Required elements**
- Both axes explicitly labelled at their heads.
- Cells holding instances, not prose.
- The claim's region — one cell, one row, one column, or the diagonal — marked.
- Empty cells that read as deliberately empty rather than forgotten.

**Properties to explore**
- **Marking a region** — cell, row, column, diagonal — within the 2-accent budget.
- **Cell content density**: how many chips fit before a cell needs a count instead.
- **The empty cell**: an em-dash, a hairline, or genuine blank. It must not read as an oversight.
- **Axis label placement** for long labels without rotating text (vertical text is banned).
- Whether the grid gets rules, alternating surfaces, or nothing but alignment. Our register favours
  restraint — test whether the grid can hold with no lines at all.

**Failure modes**
- Becoming a data table, at which point the audience starts studying cells instead of listening.
- Axes that are not actually independent, which makes half the grid meaningless.
- More than roughly 4×4.
- Unlabelled axes.

**Scenario to build**
Rows: `EU cell`, `US cell`, `APAC cell`. Columns: `Certainty`, `Fission`, `Beacon`. Cells hold
tenant chips — EU/Certainty has 2 tenants, EU/Fission has 1, US/Certainty has 1, US/Fission has 2,
US/Beacon has 1, APAC/Fission has 1, APAC/Beacon has 1, and EU/Beacon and APAC/Certainty are
deliberately empty. Claim: the `Fission` column is the only product deployed in every cell.

---

# Archetype 5 — Hub & spoke (one serves many)

**Priority: medium.** Drawable freehand in our architecture type, but with no grammar, so every
attempt looks different.

**Relation encoded:** *one-serves-many*, where the spokes are interchangeable.

**Required elements**
- A hub, central.
- Spokes visually identical to each other — their interchangeability is usually the whole point.
- Where spokes exceed the budget, a grouped cohort labelled with a count.

**Properties to explore**
- **Radial versus two flanking columns.** Radial is the obvious reading but collides with labels
  fast; test both and tell us where the crossover is.
- **Granting focus to the hub lightly** — the geometry already makes it central, so a heavy fill
  over-eggs it. Try border-only.
- **Direction**: does the hub serve, or do the spokes feed it? Show how you distinguish serving from
  feeding when both exist.
- **Label collision at 6–8 spokes**, which is where radial layouts break.
- Keeping every spoke connector traceable under the no-overlap and fanned-attach-point rules — this
  is the hardest constraint interaction in the set.

**Failure modes**
- Spokes of differing size or colour, implying a hierarchy the claim never made.
- A "hub" that actually has an in-side and an out-side — that is a pipeline, not a hub.
- Radial layouts crossing their own labels.

**Scenario to build**
Hub: `Event Bus`. Spokes: `Orders`, `Inventory`, `Shipping`, `Billing`, `Notifications`, `Analytics`.
`Orders` and `Inventory` publish; the rest subscribe. Focal: the hub.

---

# Archetype 6 — Composition (catalog and assembly)

**Priority: lower.** Include if capacity allows.

**Relation encoded:** *assembled-from*. "The whole is built from reusable parts, and the parts
outlive the whole."

**Required elements**
- A **catalog** of parts drawn as a uniform grid, signalling interchangeability.
- An **assembly** showing one product built from a selection of them.
- A drawn correspondence between the selected parts and their use in the assembly.
- The **bespoke remainder** — the part of the product that is not from the catalog.

**Properties to explore**
- **Correspondence without spaghetti**: matched treatment, ghosting, numbering, or edges. Edges from
  four catalog parts to one assembly will violate the no-overlap rule fast — solve this.
- Whether a **promotion edge** (bespoke work returning to the catalog) earns its place.
- **Catalog uniformity** versus showing which parts are most used.
- Relative weight of catalog and assembly zones.

**Failure modes**
- Catalog parts varying in size, destroying the interchangeability reading.
- Omitting the bespoke remainder — every honest composition has one, and including it is what makes
  the diagram credible rather than idealised.
- Confusing this with hub & spoke: a catalog is inert and drawn *from*; a hub is active and routes.

**Scenario to build**
Catalog: `auth`, `ingest`, `engine`, `ui`, `audit`, `notify`. Assembly: a product called `Certainty`
built from `ingest`, `engine`, and `ui`, plus bespoke `award rules`. Focal: the bespoke remainder.

---

---

# Archetype 7 — Code structure

**Priority: high.** We can draw a system at context, container, and component level, but not at code
level. Our ER type is the nearest thing and it is not the same: it models data entities with
cardinality, not code structure.

**Relation encoded:** *is-a*, *has-a*, and *depends-on* among types in a codebase.

**Required elements**
- Types with a name and a stereotype: class, interface, abstract, enum.
- **Inheritance/realization visually distinct from association.** These are different claims and a
  reader must not confuse them.
- Composition distinguished from plain association where it matters.
- Dependency direction.

**Properties to explore**
- **How much member detail earns its place.** UML crams attributes and method signatures into
  compartments. Test the range: full compartments, responsibilities in prose, or name and
  stereotype only. Our house view is that a code diagram earns its place by showing *shape*, not by
  reproducing the source — but prove or disprove that.
- **Distinguishing relationship kinds without UML's arrowhead vocabulary.** UML uses hollow
  triangles, open arrows, filled and hollow diamonds — a notation that needs a legend to read.
  We have a small marker set and a rule that a colour legend is a failure signal. Find a way to
  make "inherits from" unmistakably different from "uses" with minimal vocabulary.
- **Showing an interface boundary** — the seam where an abstraction is declared versus implemented.
- Whether **layering** (interface row above implementations) beats free placement.

**Failure modes**
- Reproducing UML's full arrowhead zoo, which is unreadable without a key.
- Every method signature listed, turning the diagram into badly formatted source code.
- Twenty classes. If the code diagram needs twenty types, the claim is about a package, not a class.
- Relationship lines that could be either inheritance or use.

**Scenario to build**
Interface `Extractor`, realized by `DrawioExtractor` and `MermaidExtractor`. Both produce
`DiagramIR`, which is composed of `Node` and `Edge`. Abstract class `Validator` is extended by
`GeometryValidator` and `SkinValidator`, both of which depend on `DiagramIR`. Focal: `DiagramIR`.

That is exactly 9 types — the budget ceiling. Treat it as a stress test rather than a comfortable
case.

---

# Archetype 8 — Deployment

**Priority: high.** Nested infrastructure holding running instances of things defined elsewhere is
its own grammar, and nothing in the library expresses it.

**Relation encoded:** *runs-on*, nested, with multiplicity.

**Required elements**
- **Deployment nodes**, nestable: region, availability zone, cluster, virtual machine, runtime.
- **Container instances** — running copies of applications defined in a container-level diagram.
- **Replica count**, stated, without drawing every copy.
- **Infrastructure nodes** — load balancers, DNS, firewalls — visually distinct from both deployment
  nodes and container instances.
- **The environment**, named explicitly. One environment per diagram.

**Properties to explore**
- **The budget problem, which is the central design challenge here.** A realistic production
  topology blows a 9-node budget immediately. Show us how you handle it: does nesting depth count
  against the budget the same way? Do sibling availability zones collapse into one drawn zone with
  a multiplier? Is there an honest abbreviation that does not lie about the topology? **This is the
  question we most want answered** — a deployment archetype that only works at toy scale is not
  useful.
- **Three element kinds needing three treatments.** Deployment node, container instance, and
  infrastructure node must be tellable apart. Our node-kind palette separates mainly by fill
  opacity and is weak at this; you may need shape or structure, not just fill.
- **Replica notation**: a count badge, stacked cards, or a multiplier on the node.
- **Nesting depth** before it becomes illegible. Find the ceiling and say what it is.
- Whether **cross-zone replication** (a primary/replica pair spanning zones) can be drawn without
  breaking the containment reading.

**Failure modes**
- Drawing N replicas literally, which blows the budget and adds no information.
- Nesting five levels deep.
- Treating a load balancer as though it were a container.
- The environment left implicit, so the reader cannot tell production from staging.
- Vendor icons doing the work that labels should do.

**Scenario to build**
Environment: **Production**. `AWS eu-west-1` containing two availability zones. Each zone runs an
`ECS cluster` hosting `API` ×3 and `Worker` ×2. A `Postgres` primary sits in zone A with a read
replica in zone B, replicating across zones. An `ALB` infrastructure node fronts both zones, with
`Route 53` outside the region boundary. Focal: the primary/replica pair.

---

## Deliverable summary

| Archetype | Options wanted | Priority |
|---|---|---|
| Zoom | 4–6 | highest |
| Contrast | 4–6 | highest |
| Lineage | 4–6 | high |
| Code structure | 4–6 | high |
| Deployment | 4–6 | high |
| Matrix | 4–6 | medium |
| Hub & spoke | 4–6 | medium |
| Composition | 4–6 | lower |

If capacity is limited, work down the priority order rather than delivering all eight thinly.
Zoom and Contrast in full are worth more to us than eight partial sets.

## Three open questions we would like your view on

**1. Is Lineage genuinely distinct?** Or is it our existing Tree type with directional encoding
added? We are not certain. Design it as if distinct, then tell us what you concluded — a reasoned
"this should not be a separate type" is a useful answer and will save us shipping a type we do not
need.

**2. Does Deployment survive realistic scale?** See archetype 8. A deployment diagram that only
works at toy scale is not useful, and the honest answer might be that it needs a larger budget than
our other types. If so, say what budget it needs and why.

**3. Is a code-level diagram worth drawing at all?** C4's own guidance treats the code level as
optional and rarely recommended, on the grounds that it goes stale immediately and the IDE draws it
better. We are inclined to include it because "detailed design through to code" is an explicit
requirement, but if your designs convince you the level cannot earn its place, tell us that.
