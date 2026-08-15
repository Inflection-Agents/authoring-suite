# Diagram-set spine

**Date:** 2026-08-14
**Status:** proposed
**Milestone:** M2.5 — after the archetypes land, before the semantic patterns

---

## 1. The problem

The library can draw every rung of the abstraction ladder. Nothing guarantees it is the same ladder.

Using C4 as a coverage yardstick, the per-level drawing capability is good: system context and
container level are served by Architecture, component level by Architecture and Nested, dynamic
behaviour by Sequence, and enterprise scope by DP integration and IT current-state. Code level and
deployment are gaps, addressed by the M2 archetypes.

But C4's actual value is not its four diagram types. It is that they form a **zoom hierarchy with
identity continuity**: an element named `X` at level N becomes the subject at level N+1, and carries
the same name and type everywhere it appears. That property is what lets a reader descend from a
one-box system diagram to a class diagram and trust that they are still looking at the same system.

Today every generated diagram is an independent HTML file. There is no notion of a set, a level, a
parent, or an element identity. `verify-docs-sync.py` checks that the gallery can reach every
example — reachability, not semantic coherence. So the following all pass silently:

- A container diagram drills into `Transform`, but the component diagram is titled `Transformer`.
- A component diagram declares a parent that does not exist.
- A container is renamed at level 2 and the level 3 diagram still uses the old name.
- A level 3 diagram is drilled from a level 1 diagram, skipping a rung.

Each of these is the failure that makes a documentation set stop being trusted, and none of them is
catchable by eye once a set exceeds a handful of diagrams.

**Precedent:** the neighbouring `architecture-diagram` skill ships `validate-set.mjs` for exactly
this concern — "one design system, one grammar, one story across every diagram" — so the idea is
proven adjacent rather than speculative.

---

## 2. Relationship to the Zoom archetype

These are complementary and it is worth being precise about the difference, because they sound
alike.

| | Zoom (M2 archetype) | Set spine (this document) |
|---|---|---|
| What it is | A visual type | Metadata plus a verification gate |
| Scope | One image showing one hop | An invariant across a whole set |
| Answers | "What is inside this box?" | "Is this the same box?" |
| Artifact | An HTML diagram | `<meta>` tags and `verify-set.py` |

Zoom renders a parent-child relationship. The spine guarantees that the relationship it renders is
real, and that every other diagram in the set agrees about it. Neither replaces the other.

---

## 3. Design

### 3.1 Where the metadata lives

Set metadata goes in `<meta>` tags in the generated file's `<head>`.

Considered and rejected:

- **A sidecar manifest** (`diagram-set.json`) — breaks the single-self-contained-file promise in
  `SKILL.md` §12, and immediately drifts from the files it describes.
- **`data-*` attributes on `<svg>`** — survives SVG export, but export is explicitly diagram-only
  and set membership is authoring-time information a viewer does not need.
- **A comment block** — not machine-readable without a bespoke parser.

`<meta>` tags are inert, invisible, machine-readable, cost nothing at render time, and are already
permitted by the skin linter, which rejects scripts and remote resources but not metadata.

### 3.2 Schema

```html
<meta name="diagram:id"      content="ingest-platform.transform">
<meta name="diagram:level"   content="component">
<meta name="diagram:parent"  content="ingest-platform">
<meta name="diagram:subject" content="transform">
<meta name="diagram:elements" content="schema-registry,validate,normalise,enrich,quarantine">
```

| Field | Required | Meaning |
|---|---|---|
| `diagram:id` | yes | Unique identity for this diagram within the set. Dotted path by convention. |
| `diagram:level` | yes | One of the levels in §3.3. |
| `diagram:parent` | no | The `diagram:id` this diagram drills into. Absent for the root. |
| `diagram:subject` | when `parent` is set | The element id **in the parent** that this diagram expands. |
| `diagram:elements` | yes | Comma-separated element ids drawn in this diagram. |

### 3.3 Levels

C4's vocabulary, because it is widely understood and the point is to borrow the hierarchy.

```
landscape → context → container → component → code
                          ↓
                     deployment
                          ↓
                      dynamic
```

`landscape`, `context`, `container`, `component`, and `code` form the strict descent ladder.
`deployment` and `dynamic` attach to a declared level rather than continuing the descent — a
deployment diagram expands a container-level system into infrastructure, and a dynamic diagram
shows one scenario over an existing structure.

### 3.4 Element identity

Elements that participate in the spine carry an explicit id on their group:

```svg
<g data-element-id="transform"> … </g>
```

**Only elements that are drilled into or shared across diagrams need an id.** A leaf node drawn once
needs nothing. This keeps adoption incremental — an existing diagram gains spine membership by
adding meta tags and ids to the two or three boxes that matter, not by re-authoring.

Deriving ids from slugified text labels was considered and rejected: rule 4 below exists precisely
to catch renames, and deriving identity from the label makes a rename invisible.

### 3.5 The verification gate — `scripts/verify-set.py`

| # | Check | Severity |
|---|---|---|
| 1 | Every `diagram:parent` resolves to another diagram's `diagram:id` | error |
| 2 | `diagram:subject` appears in the parent's `diagram:elements` | error |
| 3 | Level descent is legal — parent is exactly one rung above, per §3.3 | error |
| 4 | An element id appearing in two diagrams has the same human label in both | error |
| 5 | No cycles in the parent graph | error |
| 6 | Exactly one root per set | error |
| 7 | An element with no child diagram | **info** — coverage reporting, not a failure |

Check 7 is deliberately not an error. You do not drill into everything, and a gate that demanded it
would push authors toward drawing diagrams nobody needs. It reports coverage so the author can see
what is unexplained and decide.

### 3.6 Generated output — `docs/diagram-map.md`

The gate emits the ladder as a tree, following the repo's generated-file convention
(`build-icons.py`, `build-skins.py`) with `git diff --exit-code` in CI:

```
ingest-platform                        [context]
└── ingest-platform.containers         [container]
    ├── …transform                     [component]
    │   └── …transform.validator       [code]
    ├── …warehouse                      [component]
    └── …production                     [deployment]

3 of 7 container elements have a child diagram.
```

This doubles as the answer to "what do we have and what is missing", which is currently
unanswerable without opening every file.

---

## 4. Scope

**In scope**
- The `<meta>` schema and `data-element-id` convention.
- `scripts/verify-set.py` with checks 1–7 and unit tests, following `test-lint-a11y.py`'s style.
- Generated `docs/diagram-map.md` plus its CI diff gate.
- A short `references/diagram-sets.md` routed from `SKILL.md`, describing when to declare a set.
- Templates carry commented-out meta tags so the shape is discoverable.

**Out of scope**
- Rendering a navigable HTML hierarchy. The map is Markdown; a clickable version can follow if
  anyone wants it.
- Automatically generating a child diagram from a parent element. Tempting and premature.
- Enforcing that a set exists. A single standalone diagram remains the common case and must stay
  zero-ceremony — the spine is opt-in, and a file with no `diagram:` meta tags is simply not part of
  a set.

---

## 5. Consequences

**Good.** The library stops producing drawings and starts producing an architecture description. A
rename becomes a CI failure instead of a slow rot. "What is undocumented" becomes a generated
report. C4's hierarchy is available without C4's notation, which was the goal.

**Cost.** Authors of multi-diagram sets take on a small annotation burden. Mitigated by making ids
required only for elements that are drilled into, and by keeping the whole feature opt-in.

**Risk.** The dotted-path id convention is a convention, not a constraint, and could drift. The
gate checks referential integrity rather than naming style, which is the right trade — a naming
linter here would be ceremony.

---

## 6. Open questions

1. **Should `landscape` be a level or a separate set?** An enterprise landscape spanning ten systems
   is arguably ten roots, not one tree. Leaning toward: landscape is its own set whose elements are
   the roots of other sets, but this needs a real example before deciding.
2. **Should `dynamic` diagrams declare the elements they traverse**, so a scenario referencing a
   deleted component fails? Attractive, but it makes sequence diagrams carry structural metadata
   that may not be worth the burden.
3. **Does the deployment archetype's budget problem** (see the M2 design brief) change the level
   model? If deployment needs a larger node budget than every other type, that may indicate it
   belongs outside the descent ladder entirely rather than hanging off `container`.
