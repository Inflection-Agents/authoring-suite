# Diagram Design

> A fork of [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design),
> MIT, copyright (c) 2025 Cathryn Lavery. The original notice is retained in [LICENSE](LICENSE).
> Maintained by Inflection Agents; diverges upstream by shipping a portable token system and a
> brand skin by default. Changes are not submitted upstream.

**Architecture diagrams an agent can draw and a checker can prove.**

![Content site architecture](docs/screenshots/architecture.png)

An agent skill for Claude Code, Codex and Pi. You describe a system; it emits **one
self-contained HTML file** with inline SVG. No build step, no JavaScript, no runtime
dependency, no image assets. Double-click it, commit it, paste it into a PR.

The point is not that an LLM can draw boxes. It is that the output is **measurable**: geometry,
palette, accessibility and cross-diagram identity are all gates that fail a build, not opinions
in a review thread.

---

## C4, as a default rather than a capability

Ask for "our architecture" and most tools give you one diagram. One Architecture view of an
entire platform has to choose between showing the parts and staying legible, and it loses either
way. This skill routes a whole-system request to a **descent**:

```
context          the system in its world, and who talks to it
└── container    grouped by what fails together, not by what the repo calls a module
    └── component    one container opened, at full node detail

deployment       where it runs          ┐ attach to a declared level
dynamic          one scenario over it   ┘ rather than continuing the ladder
```

The ladder is C4's, borrowed because the vocabulary is widely understood. What makes it hold
together is that the relationship is **declared and verified**, not implied by filenames:

```html
<meta name="diagram:id"       content="platform.ingest">
<meta name="diagram:level"    content="component">
<meta name="diagram:parent"   content="platform">
<meta name="diagram:subject"  content="ingest">
<meta name="diagram:elements" content="poller,queue,loader,ledger">
```

```bash
python3 scripts/verify-set.py --all      # also regenerates docs/diagram-map.md
```

Six error checks and one advisory: a parent that resolves to nothing, a subject absent from its
parent's elements, an illegal rung, a renamed element, a cycle, or a second root all fail. An
element with **no** child diagram is reported as coverage, not as failure. Not every container
earns an expansion, and a gate demanding full coverage would push you toward diagrams nobody
needs.

The descent itself is drawn with the **Zoom** type: each component diagram repeats the container
view along its top with exactly one box marked, and a wedge down into the expansion. That is the
whole correspondence mechanism; a reader never has to consult a caption to know which box opened.

Set membership is opt-in. A file with no `diagram:` meta is not part of a set and is skipped.

---

## What it makes

All 32 types ship in three static variants: minimal light, minimal dark, full editorial. Grouped
below by the question you are answering, because that is how you pick one.

### The descent

<table>
<tr>
  <td align="center" width="33%"><img src="docs/screenshots/architecture.png" alt="Architecture"><br><b>Architecture</b><br><sub>Components + connections</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/zoom.png" alt="Zoom"><br><b>Zoom</b><br><sub>One box opened, with the wedge</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/deployment.png" alt="Deployment"><br><b>Deployment</b><br><sub>Where it runs · nested infra</sub></td>
</tr>
</table>

### Structure and relationships

<table>
<tr>
  <td align="center" width="33%"><img src="docs/screenshots/er.png" alt="ER / class"><br><b>ER / class</b><br><sub>Entities, fields, cardinality</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/lineage.png" alt="Lineage"><br><b>Lineage</b><br><sub>Provenance + breaks-if-changed</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/composition.png" alt="Composition"><br><b>Composition</b><br><sub>Catalog → one assembly</sub></td>
</tr>
<tr>
  <td align="center" width="33%"><img src="docs/screenshots/nested.png" alt="Nested"><br><b>Nested</b><br><sub>Hierarchy by containment</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/tree.png" alt="Tree"><br><b>Tree</b><br><sub>Parent → children</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/org-chart.png" alt="Org chart"><br><b>Org chart</b><br><sub>Ownership + routing</sub></td>
</tr>
<tr>
  <td align="center" width="33%"><img src="docs/screenshots/layers.png" alt="Layer stack"><br><b>Layer stack</b><br><sub>Stacked abstractions</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/dp-security-matrix.png" alt="Matrix"><br><b>Matrix</b><br><sub>Categorical grid · permissions</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/dp-integration.png" alt="DP integration"><br><b>DP integration</b><br><sub>Sources → core → consumers</sub></td>
</tr>
</table>

### Behaviour over time

<table>
<tr>
  <td align="center" width="33%"><img src="docs/screenshots/sequence.png" alt="Sequence"><br><b>Sequence</b><br><sub>Messages between lifelines</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/state.png" alt="State machine"><br><b>State machine</b><br><sub>States + transitions</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/flowchart.png" alt="Flowchart"><br><b>Flowchart</b><br><sub>Decision logic</sub></td>
</tr>
<tr>
  <td align="center" width="33%"><img src="docs/screenshots/swimlane.png" alt="Swimlane"><br><b>Swimlane</b><br><sub>Cross-functional flow</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/process.png" alt="Process"><br><b>Process</b><br><sub>Multi-actor workflow</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/data-flow.png" alt="Data flow"><br><b>Data flow</b><br><sub>Role-scoped pipeline steps</sub></td>
</tr>
<tr>
  <td align="center" width="33%"><img src="docs/screenshots/timeline.png" alt="Timeline"><br><b>Timeline</b><br><sub>Events on an axis</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/gantt.png" alt="Gantt"><br><b>Gantt</b><br><sub>Tasks and phases</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/loop.png" alt="Loop"><br><b>Loop</b><br><sub>Flywheel · stations round a hub</sub></td>
</tr>
</table>

### Whole pictures and comparisons

<table>
<tr>
  <td align="center" width="33%"><img src="docs/screenshots/high-level.png" alt="High-level"><br><b>High-level</b><br><sub>End-to-end stack on a cluster</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/it-state.png" alt="IT current-state"><br><b>IT current-state</b><br><sub>Legacy estate, modernization</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/medallion.png" alt="Medallion"><br><b>Medallion</b><br><sub>Multi-tier data storage</sub></td>
</tr>
<tr>
  <td align="center" width="33%"><img src="docs/screenshots/contrast.png" alt="Contrast"><br><b>Contrast</b><br><sub>Current vs proposed, one delta</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/quadrant.png" alt="Quadrant"><br><b>Quadrant</b><br><sub>Two-axis positioning</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/radar.png" alt="Radar"><br><b>Radar</b><br><sub>Multi-axis comparison</sub></td>
</tr>
<tr>
  <td align="center" width="33%"><img src="docs/screenshots/venn.png" alt="Venn"><br><b>Venn</b><br><sub>Set overlap</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/pyramid.png" alt="Pyramid / funnel"><br><b>Pyramid / funnel</b><br><sub>Ranked tiers or drop-off</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/quadrant-consultant.png" alt="Consultant 2×2"><br><b>Consultant 2×2</b><br><sub>Quadrant preset, named cells</sub></td>
</tr>
</table>

### Quantities

<table>
<tr>
  <td align="center" width="33%"><img src="docs/screenshots/bar.png" alt="Bar"><br><b>Bar</b><br><sub>Categorical comparison</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/line.png" alt="Line"><br><b>Line</b><br><sub>Trends over time</sub></td>
  <td align="center" width="33%"><img src="docs/screenshots/scatter.png" alt="Scatter"><br><b>Scatter</b><br><sub>Distribution and correlation</sub></td>
</tr>
</table>

**Browse them all:** open [`skills/diagram-design/assets/index.html`](skills/diagram-design/assets/index.html)
to flip through every type with light / dark / full-editorial tabs.

---

## Beyond the types

**Semantic patterns** describe behaviour separately from layout, so a queue, a policy trace or a
trust boundary routes to the nearest existing type instead of inflating the type count.

**A token contract.** Every colour and radius binds through `--dd-*`, so a diagram carries its
skin and reskinning is one `:root` block, not one edit per attribute.

**Brand onboarding.** Point it at a URL and it extracts palette and fonts into
`references/style-guide.md`, contrast-checked, with a receipt naming what it took.

**Import, not conversion.** `.drawio` and Mermaid sources are extracted to a structured IR and
**redrawn** at a chosen format, size and detail level. Source coordinates, colours and shape
quirks are discarded; components, relationships and grouping are kept, and you get a fidelity
ledger of what was merged or dropped.

---

## Install

```bash
/plugin marketplace add Inflection-Agents/authoring-suite
/plugin install diagram-design@authoring-suite
```

Editable install, if you intend to customise the references:

```bash
git clone git@github.com:Inflection-Agents/authoring-suite.git
ln -s "$PWD/authoring-suite/plugins/diagram-design/skills/diagram-design" \
      ~/.claude/skills/diagram-design
```

Then just ask. `"Draw our platform architecture"` gets a descent; `"a sequence for a bearer call
with refresh on 401"` gets one diagram.

---

## Verification is the feature

A rule that lives only in prose ships broken examples, so the rules are checkers with fixtures.

| Gate | Catches |
|---|---|
| `verify_geometry.py` *(ships with the skill)* | Labels clipped by a node, labels sitting on the connector they name, boxes escaping their container |
| `self_check.py` *(ships with the skill)* | Accessible-SVG contract, single-file safety, motion contract |
| `lint-skin.py` | Colours, fonts, token contract, external assets |
| `verify-set.py` | Cross-diagram identity and the level ladder |
| `verify-grid.py`, `verify-accent-budget.py`, `verify-no-diagonal.py` | 4px grid, accent budget, orthogonal connectors |

The first two ship **inside the skill**, so an agent measures the diagram it just drew rather
than certifying it from intent. `SKILL.md` §9 asks for the checker's output, not a tick.

CI runs the full suite on Linux, Windows and macOS across Python 3.11 and 3.12. Settled decisions
live as short ADRs in [`docs/adr/`](docs/adr/); read the relevant one before relitigating it.

---

## Context cost

Progressive disclosure is the reason this scales to 32 types. At rest the agent sees only the
skill's name and description.

| Request | Loads |
|---|---|
| "Make me a flowchart" | `SKILL.md` + one type reference |
| "Why did these two policy requests differ?" | ...plus `semantic-patterns.md` |
| "Animate that trace" | ...plus `animation.md` |

Adding a type tomorrow changes nothing about what a flowchart costs.

```
diagram-design/
├── skills/diagram-design/
│   ├── SKILL.md                 — philosophy, selection, the §9 gate
│   ├── references/
│   │   ├── routing.md           — scope question, then pattern, then type
│   │   ├── diagram-sets.md      — the C4 spine: meta schema + verification
│   │   ├── type-zoom.md         — one hop of the descent
│   │   ├── style-guide.md       — single source for colours and fonts
│   │   └── type-*.md            — one per visual type
│   ├── scripts/                 — verify_geometry.py, self_check.py, the import extractors
│   └── assets/                  — index.html gallery, templates, 3 variants × 32 types
├── scripts/                     — repo-side gates and generators
└── docs/adr/                    — settled decisions
```

---

## When not to use it

A quick unicode sketch in a terminal. A list of things that is really a table. A
one-shape "diagram" that is a sentence. Anything where a well-written paragraph teaches more
than a picture would. The skill's own §2 says to check that before drawing.

## Contributing

New types, import grammars, examples and tooling are all welcome. See
[CONTRIBUTING.md](CONTRIBUTING.md) for the gate suite and the workflow, and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards.
