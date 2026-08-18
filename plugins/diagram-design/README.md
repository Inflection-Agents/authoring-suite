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

## What you get

**32 visual types**, each in three variants (minimal light, minimal dark, full editorial).
Architecture, Zoom, Deployment, Sequence, State, Flowchart, ER/class, Lineage, Contrast,
Composition, Swimlane, Timeline, Gantt, Quadrant, Radar, Venn, Pyramid, Tree, Org chart, Layer
stack, Nested, Loop, Matrix, Medallion, Data flow, DP integration, IT current-state, High-level,
Process, and bar/line/scatter charts.

**Semantic patterns** describe behaviour separately from layout, so a queue, a policy trace or a
trust boundary routes to the nearest existing type instead of inflating the type count.

**A token contract.** Every colour and radius binds through `--dd-*`, so a diagram carries its
skin and reskinning is one `:root` block, not one edit per attribute.

**Brand onboarding.** Point it at a URL and it extracts palette and fonts into
`references/style-guide.md`, with contrast checked automatically and a receipt naming what it
took. See [`onboarding.md`](skills/diagram-design/references/onboarding.md).

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
