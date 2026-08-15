# Composition (Catalog and Assembly)

**Best for:** "the whole is built from reusable parts, and the parts outlive the whole" —
showing a shared catalog of interchangeable pieces alongside one product assembled from a
selection of them.

## Layout conventions
- **Catalog**: a uniform row or grid of parts, all the same size and treatment. Uniformity
  *is* the claim — interchangeability. Don't dim or resize parts to show usage; that belongs
  in the assembly, not the catalog.
- **Number every catalog part** (`01 · auth`, `02 · ingest`, …) as part of its name text, not
  a separate badge.
- **Assembly**: a container holding the product's parts. Used catalog parts appear as small
  reference chips — smaller than a full node, undecorated (no `dd-node` class, so they don't
  register as new nodes to the tag-consistency gate), carrying the *same* numbered label as
  their catalog entry. That matching number is the entire correspondence mechanism.
- **No connectors between catalog and assembly.** Four-plus catalog parts drawing edges to
  one assembly box violates the no-overlap rule almost immediately at any real catalog size.
  Matched numbering does the same job with zero lines and no crossing risk.
- **The bespoke remainder** — the part of the assembly not from the catalog — is a full,
  real node (not a reference chip), carrying the diagram's one accent. Every honest
  composition has one; omitting it makes the assembly look more reusable than it is.

## Anti-patterns
- Catalog parts that vary in size or treatment — destroys the interchangeability reading the
  whole type exists to make.
- Reference chips styled identically to full catalog nodes — a reader can't tell "used here"
  from "a new, independent part."
- Omitting the bespoke remainder.
- Drawing connectors from every used catalog part to the assembly instead of matching numbers
  — this is the spaghetti the type is designed to avoid.
- Confusing this with Hub & spoke: a catalog is inert and drawn *from*; a hub is active and
  routes between spokes.

## Examples
- `assets/example-composition.html` — minimal light
- `assets/example-composition-dark.html` — minimal dark
- `assets/example-composition-full.html` — full editorial
