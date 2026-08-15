# Code Level

**Best for:** database schemas, API resource relationships, domain models, and class/type
structure in a codebase. One type, two presets — see [Which variant](#which-variant).

## Which variant

| If you're modeling… | Use the | Relationship kinds |
|---|---|---|
| Entities, fields, and cardinality | **Entity preset** | `1` / `N` / `0..1` / `1..*` at each line end |
| Classes, interfaces, and dependencies | **Class preset** | `is-a` / `has-a` / `depends-on` |

Both presets are the same type because they share a spine: boxes with a type-tag header and a
short body, and relationship lines carrying a small text token at the endpoint rather than a
notation-heavy arrowhead vocabulary. What differs is the vocabulary the tokens are drawn from —
cardinality numbers for data models, relationship verbs for code structure.

---

## Entity preset

### Layout conventions
- Each entity is a two-section box:
  - **Header**: type tag (`ENTITY`) + entity name in DM Sans.
  - **Body**: field list in Geist Mono, one per line. PK prefixed with `#`, FK prefixed with `→`.
- Relationships: lines between entities with cardinality at each end:
  - `1`, `N`, `0..1`, `1..*` in Geist Mono, 8px, placed 10–12px from the entity edge.
  - Optional relationship label ("has", "belongs to") centered on the line.
- Group related entities close; lay out so most relationships are straight lines, not tangles.
- Gold on the aggregate root or central entity of the model.

### Anti-patterns
- Drawing an arrow for every FK on a model with dozens — lay out by cluster instead.
- Inconsistent cardinality notation between ends of the same relationship.
- Fields padded to equal-height boxes — natural height by content is fine.

### Examples
- `assets/example-er.html` — minimal light
- `assets/example-er-dark.html` — minimal dark
- `assets/example-er-full.html` — full editorial

---

## Class preset

C4's own guidance treats the code level as optional, on the grounds that it goes stale the
moment the code changes and an IDE draws it better. This preset earns its place anyway by
showing *shape* — how types relate — not by reproducing the source. If a diagram needs
twenty classes to make its point, the claim is about a package, not a class; split it or
step up a level.

### Layout conventions
- Each type is a box with a type tag (`INTERFACE`, `ABSTRACT`, or `CLASS`) + name in DM Sans,
  plus at most one short responsibility line in Geist Mono — a phrase (`parse source → IR`),
  never a member listing. Member signatures belong in the source, not the diagram.
- Three relationship kinds, three treatments, no UML arrowhead zoo:
  - **is-a** (inheritance/realization) — heavier stroke, a shared hollow-triangle marker.
    Dashed = realizes an interface, solid = extends a class. Both read as "is-a" by marker;
    the specific verb (`REALIZES` / `EXTENDS`) is a text token at the line, same convention
    as the entity preset's cardinality numbers.
  - **depends-on** (association/uses) — thin dashed stroke, a small filled arrowhead,
    verb token (`DEPENDS ON`, `PRODUCES`) pointing at the thing depended on.
  - **has-a** (composition) — a filled square terminator at the whole's end, no arrowhead,
    token `HAS`. Reserve this for genuine ownership, not every reference.
- Layer interfaces/abstracts above their implementations when the model has both; free
  placement otherwise.
- Gold on the type every other type in the diagram touches, if there is one.

### Anti-patterns
- UML's full arrowhead vocabulary (hollow/filled diamonds, open/closed arrows) — needs a
  legend to read, which this house style treats as a failure signal.
- Full method signatures or attribute lists — turns the diagram into badly formatted source.
- A relationship line that could be read as either inheritance or use — the marker family
  must make the kind unmistakable without relying on the text token alone.
- More than about nine types — that's a package diagram wearing a class diagram's clothes.

### Examples
- `assets/example-class.html` — minimal light
- `assets/example-class-dark.html` — minimal dark
- `assets/example-class-full.html` — full editorial
