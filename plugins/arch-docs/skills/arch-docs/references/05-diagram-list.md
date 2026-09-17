# 05 Plan

**Goal.** Propose the whole set as a numbered list of diagrams, one paragraph each, so the owner can cut and add
before anything is drawn.
**Produces.** The diagram list, grouped into layers, with the argument the set makes read back from the titles.
**Gate.** The owner has approved the list.

This phase is where the set is cheapest to change. A paragraph per diagram costs almost nothing to read and nothing
to cut. Drawing the wrong set costs a day.

Enter this phase once the owner has corrected `_brief/facts.md` in [04](04-facts-file.md). Draw nothing here.

## Group the diagrams into layers

Layers peel from high level to deep detail, so a reader can stop after any layer and still hold a complete picture
at that depth. Something like: context, containers, components per container, the contracts, the flows, the
cross-cutting concerns, the comparisons. Adjust the layers to this system rather than forcing this order onto it.

## One paragraph per diagram

Give exactly these five fields, in one short paragraph each:

- **Number and title.** The title names what the diagram shows and makes no claim.
- **Visual type** from the diagram skill, and the C4 level.
- **What is on it**, concretely: the boxes, the grouping, and what is deliberately left off.
- **The one thing the reader should notice**, which becomes the focal accent.
- **Why it exists.** Where the answer is "completeness", mark the diagram as a candidate to cut.

## Read the argument back

Separately from the list, give the owner three things.

- **The argument.** Read your own titles in order and say, in five sentences, the argument the set makes. Where the
  order does not build an argument, reorder the list and show the new order. The argument is checked against the
  problem the set has to make visible, recorded in [01](01-kickoff.md).
- **What the owner asked for that you are not drawing**, and why.
- **Where you drafted wider than needed**, so the owner knows which diagrams you expect to lose in pruning.

## Draft wide

Aim high on count. Cutting is cheap and discovering a gap after the set is consistent is not. A diagram that exists
to carry one fact is fine at this stage, and [10](10-prune-and-split.md) is where it gets tested.

Wait for the owner's approval of the list before writing the build brief in [06](06-build-brief.md).
