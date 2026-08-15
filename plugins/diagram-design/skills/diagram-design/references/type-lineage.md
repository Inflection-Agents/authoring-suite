# Lineage (Provenance and Impact)

**Best for:** answering "what does this depend on, and what breaks if it changes" for one
selected asset in a data or dependency graph.

**Distinct from Tree, deliberately.** Tree draws parent → children with no notion of
direction-of-consequence and no multi-parent case. Lineage's whole point is a node with
*several* parents (a DAG, not a tree) and two opposite claims read off the same graph —
derived-from one way, impact-if-changed the other. A tree can't carry either without
stretching its own grammar past its type. Use Tree for pure hierarchy; reach for Lineage the
moment an asset has more than one parent or you need to show what's downstream.

## Layout conventions
- **Columns per hop**, not a loose graph layout — each column is one step of transitive
  distance from the selected asset, labeled (`2 HOPS UPSTREAM`, `1 HOP DOWNSTREAM`, …).
  `SELECTED` marks the asset's own column.
- **Layer by longest path, not nearest.** An asset with a direct edge from the selected node
  *and* an indirect one through an intermediate asset sits in the column its longest incoming
  path reaches — the same convention layered-DAG tools use. A node can still have a
  same-direction edge that skips a column; draw it as a real elbow around the intervening
  column, not a compressed same-column edge.
- **Direction without relying on arrowheads alone**: upstream and downstream get different
  stroke colours (ink/muted for derives-from, `--dd-link` for impact-if-changed) in addition
  to a `UPSTREAM` / `DOWNSTREAM` text tag on every node. A reader should be able to tell which
  side is cause and which is consequence before reading a single arrowhead.
- **The fan-out problem**: when one asset feeds many, draw one cohort box with a stated count
  (`×12`), not twelve boxes and not a silently truncated one. A light stacked-card effect
  (two faint offset rects behind the main box, undecorated — not `dd-node`, so they don't
  enter node-consistency scanning) signals "more than one" without inventing new nodes.
- Assets outside the selected asset's lineage are excluded from the diagram entirely, not
  dimmed — Lineage draws one asset's graph, not the whole catalog.

## Anti-patterns
- Drawing it as a tree and losing the multi-parent case — the entire reason this type exists.
- Upstream and downstream in the same colour, leaving direction to arrowheads alone.
- Every asset in the graph shown, defeating the point of selecting one.
- A same-column edge to fake a skip connection — route it around the intervening column
  instead, even if the elbow is longer.

## Examples
- `assets/example-lineage.html` — minimal light
- `assets/example-lineage-dark.html` — minimal dark
- `assets/example-lineage-full.html` — full editorial
