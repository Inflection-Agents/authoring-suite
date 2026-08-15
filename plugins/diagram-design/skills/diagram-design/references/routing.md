# Routing — semantic pattern and visual-type selection

Moved out of `SKILL.md` §3 verbatim (per the M1 execution plan's "start of Phase 3" step) to
keep `SKILL.md` under its byte cap as new types land. `SKILL.md` §3 still states the two-step
rule (pattern first, then type) and links here; this file holds the tables themselves. New
type rows land here as each type ships — `SKILL.md` §3 is touched only once more, for the
M2.2 routing rewrite.

## Semantic pattern, then visual type

When behavior, state, enforcement, or risk carries the meaning, first load
[`semantic-patterns.md`](semantic-patterns.md) and choose one primary pattern. Then choose the
nearest visual type for layout. If no pattern matches, choose the type directly.

| Behavioral trigger | Semantic pattern → nearest type |
|---|---|
| Fan-in, queue depth, finite capacity, bottleneck | **Fan-in queue / bottleneck** → Data flow |
| Repeated Question / Input / Governance / Output slots across stages | **Stage framework with semantic slots** → Process |
| Conversation or loose input becomes a structured durable artifact | **Unstructured input → structured artifact** → Data flow |
| Two rule traces need pass/fail/skipped/not-reached and first divergence | **Paired policy-evaluation traces** → Flowchart |
| Trust boundaries plus permitted/forbidden ingress or deploy paths | **Secure paved road** → Architecture |
| Controls grouped by where they are enforced | **Governance / control catalog** → Layer stack |
| Defenses compensate for prior gaps and residual risk propagates | **Compensating security layers** → Layer stack |
| One hub serving many interchangeable spokes, or spokes feeding one hub | **Hub & spoke** → Architecture |

The pattern owns semantic primitives and its tighter budget; the type owns layout grammar. Use
[`animation.md`](animation.md) only when motion is requested or materially clarifies ordered
change; static remains the default.

### Visual-type guide (32)

**Relation** is the vocabulary the gallery (`assets/index.html`) groups by (M2.4) — the same
word names the section a type's card sits in. It answers "what claim am I making," one level
above "which type." Several types share a relation (e.g. every temporal-ordering type sits under
**Sequences**) because the relation is genuinely the same; a shared relation is not a sign the
types are redundant, only that the layout choice within it depends on what else is load-bearing
(actors and messages vs. bare event dates vs. task duration).

| Relation | If you're showing… | Use | Reference |
|---|---|---|---|
| Topology | Components + connections in a system | **Architecture** | [type-architecture.md](type-architecture.md) |
| Detail-of | An overview with one element expanded into full detail below | **Zoom** | [type-zoom.md](type-zoom.md) |
| Differs-from | A current state and a proposed state, one difference between them | **Contrast** | [type-contrast.md](type-contrast.md) |
| Derives-from | One asset's provenance (derives-from) and impact (breaks-if-changed), multi-parent | **Lineage** | [type-lineage.md](type-lineage.md) |
| Assembled-from | A shared catalog of reusable parts plus one product assembled from a selection of them | **Composition** | [type-composition.md](type-composition.md) |
| Runs-on | Nested infrastructure (region/zone/cluster) holding running container instances, with replicas | **Deployment** | [type-deployment.md](type-deployment.md) |
| Topology | Legacy IT landscape grouped by phase/department; documents the *before* state in modernization proposals | **IT current-state** | [type-it-state.md](type-it-state.md) |
| Branches | Decision logic with branches | **Flowchart** | [type-flowchart.md](type-flowchart.md) |
| Sequences | Time-ordered messages between actors | **Sequence** | [type-sequence.md](type-sequence.md) |
| Transitions | States + transitions + guards | **State machine** | [type-state.md](type-state.md) |
| Structures | Entities + fields + relationships, or class/type structure in code | **Code level** | [type-code-level.md](type-code-level.md) |
| Sequences | Events positioned in time | **Timeline** | [type-timeline.md](type-timeline.md) |
| Sequences | Cross-functional process with handoffs | **Swimlane** | [type-swimlane.md](type-swimlane.md) |
| Positions | Two-axis positioning / prioritization | **Quadrant** | [type-quadrant.md](type-quadrant.md) |
| Positions | Multiple entities scored across 3–5 quantitative criteria | **Radar / Spider** | [type-radar.md](type-radar.md) |
| Recurs | Reinforcing cycle / flywheel where the last step feeds the first and a shared hub accumulates state | **Loop** | [type-loop.md](type-loop.md) |
| Contains | Hierarchy through containment / scope | **Nested** | [type-nested.md](type-nested.md) |
| Contains | Parent → children relationships | **Tree** | [type-tree.md](type-tree.md) |
| Contains | Human/agent/team ownership, reporting, routing, escalation | **Org chart** | [type-org-chart.md](type-org-chart.md) |
| Contains | Stacked abstraction levels | **Layer stack** | [type-layers.md](type-layers.md) |
| Overlaps | Overlap between sets | **Venn** | [type-venn.md](type-venn.md) |
| Narrows | Ranked hierarchy or conversion drop-off | **Pyramid / funnel** | [type-pyramid.md](type-pyramid.md) |
| Compares | Quantitative comparison across categories | **Bar chart** | [type-bar.md](type-bar.md) |
| Compares | Continuous trends over time | **Line chart** | [type-line.md](type-line.md) |
| Sequences | Tasks and phases on a timeline | **Gantt** | [type-gantt.md](type-gantt.md) |
| Compares | Distribution and correlation between two variables | **Scatter plot** | [type-scatter.md](type-scatter.md) |
| Topology | End-to-end data stack on a container cluster | **High-Level** | [type-high-level.md](type-high-level.md) |
| Sequences | Multi-actor sequential process with data handoffs | **Process** | [type-process.md](type-process.md) |
| Contains | Multi-tier data storage with quality levels and access policies | **Medallion** | [type-medallion.md](type-medallion.md) |
| Flows-to | Role-scoped data flow: who does what at each pipeline step | **Data flow** | [type-data-flow.md](type-data-flow.md) |
| Topology | Integration topology of a data platform — sources → core → consumers | **DP integration** | [type-dp-integration.md](type-dp-integration.md) |
| Combines | Two independent dimensions, combination is the insight — includes the per-role/per-component permissions preset | **Matrix** | [type-matrix.md](type-matrix.md) |

Rules of thumb:

- If a 3-column table communicates the same thing, pick the table.
- If two types seem useful, pick the dominant axis; a semantic pattern may add behavior-specific primitives, not a second layout grammar.
- If you're past the complexity budget (§7 in `SKILL.md`), split into an overview + detail.

**Always load the chosen `references/type-*.md` before drawing.** When routed above, also load `semantic-patterns.md`; when animation is chosen, load `animation.md`.
