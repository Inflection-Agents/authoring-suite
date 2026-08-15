# Deployment

**Best for:** where things run — nested infrastructure (region, zone, cluster) holding running
instances of containers defined elsewhere, plus the infrastructure (load balancers, DNS) that
fronts them. One named environment per diagram.

**Does this survive realistic scale?** Yes, once the budget question is answered honestly —
see below. This was the design brief's own central question, so the answer is documented here
rather than left implicit in the example.

## The budget answer

A realistic topology blows a flat 9-node ceiling immediately if every container and every
instance counts the same. It doesn't have to:

- **Nesting depth is free.** Region, zone, and cluster are deployment nodes — dashed,
  transparent `dd-container` boundaries, structurally identical to the boundary rects other
  types already use for zones and regions. They were never counted as nodes by any gate in this
  system, and they shouldn't be counted by eye either. The 9-node guideline applies to *content*
  — instances and infrastructure — not to how many containment levels wrap it.
- **Replica count is a stated badge, never drawn copies.** One `API` box with a `×3` badge is
  the instance group, not three boxes. This is the same convention Lineage's fan-out cohort uses
  for the same reason: honesty about scale without literal enumeration.
- **Sibling zones collapse only when they're genuinely interchangeable.** If two availability
  zones ran identical content, draw one zone template with a `×2 ZONES` badge instead of two
  full copies. Don't collapse them if they differ — a primary/replica pair split across zones
  (the common real case) means the zones are *not* interchangeable, and collapsing them would
  erase the exact relationship the diagram exists to show.
- **Ceiling: three nesting levels** (region → zone → cluster) before the type becomes illegible.
  A fourth level (e.g., a task definition inside the cluster) is one container too many for a
  single static diagram — split it into a Zoom expansion instead.

Applying all four to a real topology (2 zones × (1 cluster × 2 instance groups) + 1 db pair + 2
infra nodes) lands at exactly 8 content nodes — inside budget, at realistic scale, honestly.

## Layout conventions
- **Three kinds, three treatments** — fill/opacity alone was judged too weak once dashed
  transparent containers were already using transparency as a signal:
  - **Deployment node** (region, zone, cluster, VM, runtime): dashed, transparent boundary.
  - **Container instance** (a running copy of something defined at the container level): solid
    node, plain corners — 0 notch, same as `backend`.
  - **Infrastructure** (load balancer, DNS, firewall): solid node, **notched corners** — a
    database-holding instance gets 1 notch (`store`), infrastructure gets 2 (`external`). See
    `primitive-notch.md`'s `deployment` scope entry.
- **The environment is named explicitly**, once, at the top of the canvas, not per-box.
- Infrastructure sitting genuinely outside a boundary (a global DNS service) is drawn outside
  it, not inside with a special fill.
- **Cross-boundary connectors are normal.** A replication line between a primary in one zone and
  a replica in another crosses both zone boundaries directly — containment boxes are visual
  scope, not a wall a real relationship can't cross.

## Anti-patterns
- Drawing every replica literally — blows the budget and adds no information a badge doesn't.
- Nesting four or more levels deep in one static diagram.
- Treating a load balancer as though it were a container (it fronts things; it doesn't hold
  them) — give it the infrastructure treatment, not a `dd-container` boundary.
- Leaving the environment implicit — a reader must not have to guess production vs. staging.
- Collapsing asymmetric zones into one template to save space when they differ in content.

## Examples
- `assets/example-deployment.html` — minimal light
- `assets/example-deployment-dark.html` — minimal dark
- `assets/example-deployment-full.html` — full editorial
