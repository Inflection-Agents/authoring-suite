# Diagram sets — the spine across multiple diagrams

Every generated diagram is a standalone, self-contained file. Nothing links them, which is
correct for a single diagram and a real gap once a project needs *several* diagrams that
describe the same system at different zoom levels and must agree with each other.

**This is opt-in and costs nothing when unused.** A file with no `diagram:` meta tags is simply
not part of a set — the common case, a single standalone diagram, stays zero-ceremony.

## When to declare a set

Declare a set when two or more diagrams describe the *same* system such that a reader should be
able to trust that an element named `Transform` in one diagram is the same `Transform` in
another — a container-level overview and the component-level detail it drills into, for example.
A single diagram, or several unrelated diagrams that happen to share a subject informally, needs
no set metadata.

Zoom (`type-zoom.md`) and the set spine solve different problems and are not substitutes for
each other:

| | Zoom (visual type) | Set spine (this document) |
|---|---|---|
| What it is | A visual type | Metadata plus a verification gate |
| Scope | One image showing one hop | An invariant across a whole set of files |
| Answers | "What is inside this box?" | "Is this the same box, everywhere it appears?" |
| Artifact | An HTML diagram | `<meta>` tags plus `scripts/verify-set.py` |

Zoom renders a parent-child relationship inside one file. The spine guarantees that relationship
is real *across files*, and that every diagram in the set agrees about names and structure.

## The schema

Set metadata lives in `<meta>` tags in the generated file's `<head>` — inert, invisible,
machine-readable, and already permitted by the skin linter (which rejects scripts and remote
resources, not metadata). A sidecar manifest would break the single-self-contained-file promise
and drift from the files it describes; `data-*` attributes on `<svg>` would survive SVG export,
but set membership is authoring-time information a viewer never needs.

```html
<meta name="diagram:id"       content="ingest-platform.transform">
<meta name="diagram:level"    content="component">
<meta name="diagram:parent"   content="ingest-platform">
<meta name="diagram:subject"  content="transform">
<meta name="diagram:elements" content="schema-registry,validate,normalise,enrich,quarantine">
```

| Field | Required | Meaning |
|---|---|---|
| `diagram:id` | yes | Unique identity for this diagram within the set. Dotted path by convention — a convention, not a constraint the gate enforces; see [Risk](#risk-and-open-questions). |
| `diagram:level` | yes | One of the levels below. |
| `diagram:parent` | no | The `diagram:id` this diagram drills into. Absent for the root of a set. |
| `diagram:subject` | when `parent` is set | The element id **in the parent** that this diagram expands. |
| `diagram:elements` | yes | Comma-separated element ids drawn in this diagram. |

## Levels

Borrowed from C4's vocabulary because it's widely understood, and the point is the hierarchy,
not a new notation.

```
landscape → context → container → component → code
                          ↓
                     deployment
                          ↓
                      dynamic
```

`landscape`, `context`, `container`, `component`, and `code` form the strict descent ladder — a
child's level must be exactly one rung below its parent's. `deployment` and `dynamic` attach to a
declared level rather than continuing the descent: a deployment diagram expands a
container-level system into infrastructure, and a dynamic diagram shows one scenario over an
existing structure. Neither needs to sit exactly one rung below its parent.

## Element identity

Elements that participate in the spine — drilled into from another diagram, or shared across
diagrams — carry an explicit id on their group:

```svg
<g data-element-id="transform"> … </g>
```

**Only elements that are drilled into or shared need an id.** A leaf node drawn once needs
nothing — this keeps adoption incremental. An existing diagram gains spine membership by adding
meta tags and ids to the two or three boxes that matter, not by re-authoring the whole file.

Ids are never derived from slugified labels. `verify-set.py` check 4 exists precisely to catch a
rename between diagrams, and deriving identity from the label would make the rename invisible —
the id and the label must be free to diverge so the gate can compare them.

## Verification — `scripts/verify-set.py`

| # | Check | Severity |
|---|---|---|
| 1 | Every `diagram:parent` resolves to another diagram's `diagram:id` | error |
| 2 | `diagram:subject` appears in the parent's `diagram:elements` | error |
| 3 | Level descent is legal — parent is exactly one rung above, for ladder levels | error |
| 4 | An element id appearing in two diagrams has the same human label in both | error |
| 5 | No cycles in the parent graph | error |
| 6 | Exactly one root per declared set (grouped by `diagram:id`'s first dotted segment) | error |
| 7 | An element with no child diagram | **info** — coverage reporting, not a failure |

Check 7 is deliberately not an error. Not drilling into everything is normal; a gate that
demanded full coverage would push authors toward diagrams nobody needs. It reports what's
undocumented so the author can decide, rather than failing the build over it.

Run it with `python3 scripts/verify-set.py --all` (or specific files). It also regenerates
`docs/diagram-map.md` — a generated file, `git diff --exit-code`-checked in CI the same way
`build-icons.py` and `build-skins.py` are, so a stale map fails CI rather than rotting silently.

## Risk and open questions

- **The dotted-path id convention carries real weight for check 6, and only check 6.** Every
  other check is pure referential integrity (does the parent exist, does the subject appear) and
  never touches naming style. Check 6 is the exception: a diagram's single `parent` field makes
  the parent graph a forest, and a connected component of a forest can never itself contain two
  roots — so "exactly one root" can only ever produce a real error when "set" is defined by the
  id's first dotted segment instead. A naming linter enforcing the *shape* of the id would still
  be ceremony; grouping by it for this one check is not, because it is the only grouping under
  which the check can catch anything.
- **`landscape` may deserve to be its own set** rather than the top of every set's ladder — an
  enterprise landscape spanning ten systems is arguably ten roots, not one tree. Undecided until
  a real multi-system example exists.
- **Whether `dynamic` diagrams should declare the elements they traverse**, so a scenario
  referencing a deleted component fails, is open. It would make sequence diagrams carry
  structural metadata that may not be worth the authoring burden.

## Out of scope

- Rendering a navigable HTML hierarchy — `docs/diagram-map.md` is Markdown; a clickable version
  can follow if anyone wants it.
- Automatically generating a child diagram from a parent element.
- Enforcing that a set exists. A single standalone diagram remains the common case.
