# Selection guidance and the gallery as a decision surface

**Date:** 2026-08-14
**Status:** proposed
**Milestone:** M2.4 — after routing, alongside the archetypes

---

## 1. The problem: choice is growing faster than guidance

The skill is about to get considerably harder to use. Today a user picks from 27 types. After M2
they pick from 35, and — new with this design pass — from **variants within a type**: Zoom has a
frustum and a fish-eye, Contrast has a balanced grammar and a lopsided one, Deployment has four
abbreviations that apply under different conditions.

Every option added without a rule for reaching for it is a tax on the person using the skill.

### The decision stack

Six choice points sit between "I need a diagram" and a finished file. Five are covered; one is not.

| # | Decision | Covered by | Status |
|---|---|---|---|
| 1 | Should I draw at all? | Refusal rules in the routing methodology | M2.2 |
| 2 | Which *set* of diagrams? | Routing: extract claims, collapse, budget-test, drop-test | M2.2 |
| 3 | Which type? | Routing table — relation selects the type | M2.2 |
| 4 | **Which variant within the type?** | — | **gap** |
| 5 | Which size, detail level, audience? | `output-spec.md` dials | shipped |
| 6 | Which skin? | Style guide, generated skins | M1 |

Layer 4 is new because until this design pass, types had no variants worth choosing between.

---

## 2. Principle: default the decision, do not present it

The failure mode to avoid is a reference that lists three variants with balanced descriptions and
leaves the reader to weigh them. That converts one decision into three paragraphs of reading.

Every type therefore names **one default variant**, and the alternates are reached only when a
stated condition holds. The reader who does not want to decide gets a good answer by not deciding;
the reader who has the edge case finds it by matching a condition, not by evaluating trade-offs.

The rule must be **mechanical** — a test with a deterministic answer, phrased as a condition rather
than a consideration. "Reach for the fish-eye when the detail fits one box width" is a rule.
"Consider whether the fish-eye might read faster" is not.

---

## 3. Variant selection lives in the type reference

A new standard section, `## Which variant`, in every `type-*.md` that has more than one.

This placement matters for a reason beyond tidiness: by the time you are reading a type reference,
routing has already chosen the type, so the guidance costs **nothing** at skill-load time. It sits
behind progressive disclosure and never touches the `SKILL.md` byte cap.

### Worked rules from this design pass

**Zoom**

> Default: **frustum**. Reach for the **fish-eye** when exactly one stage opens *and* its detail
> fits within the parent box's own width. Two stages opening, or detail wider than the box, is
> always the frustum — the fish-eye cannot express either.

**Contrast**

> Default: **shared row grid**. Reach for **lopsided panels** when the proposed panel has fewer
> rows than the current one. Give the vacated rows to a delta ledger, never to padding nodes.
> Never reach for retirement-in-place: one field cannot hold a baseline, and it is documented in
> this reference as a worked failure.

**Deployment abbreviations** — a four-way rule, all conditions mechanical:

| Condition | Abbreviation |
|---|---|
| Sibling frames whose contents are identical | Sibling collapse with a multiplier |
| The same component appears N times in one frame | Replica badge `×N` |
| A second region duplicating the first | Peer region — one drawn in full, peers as a named stack |
| Leaves exceed the instance budget | Cohort node with a count |

Each of those is checkable by looking at the data, which is the standard to hold every variant rule
to.

---

## 4. The gallery becomes the decision surface

Today `assets/index.html` is a specimen sheet: type tabs numbered 01–27, variant tabs for
light/dark/full, and an iframe. It answers *what does this look like* and says nothing about *when
would I want it*. With 35 types and per-type variants, a flat numbered tab strip stops working as
navigation.

**Three changes, in value order.**

### 4.1 Index by relation, not by type number

Group the gallery under the same relation vocabulary the routing table uses — *detail-of*,
*differs-from*, *runs-on*, *derived-from*, *contains*, *precedes*, and so on. A user arrives
already knowing their relation, because that is what step 2 of routing produced. The gallery then
becomes the visual front end of the routing table rather than a parallel index with its own
ordering.

This is the single highest-value change: it makes browsing and routing agree, so the gallery stops
being a separate thing to learn.

### 4.2 Every card carries its "reach for this when" line

One sentence per specimen, taken verbatim from the type reference's `## Which variant` section.
The gallery and the reference cannot drift, because the line has one source.

### 4.3 Show variants as peers, not as a hidden tab

Zoom's frustum and fish-eye are different answers, not different skins of one answer. They belong
side by side with their conditions visible. The existing light/dark/full tabs stay what they are —
renderings of the same diagram — and should be visually distinguished from variant choices, which
are different diagrams.

### Existing machinery that helps

Gallery reachability is **already a CI gate**: `verify-docs-sync.py` fails on any shipped example
the gallery cannot reach. So adding archetypes forces gallery registration whether or not we plan
for it. The work here is restructuring what a gallery entry *contains*, not building a new pipeline.

---

## 5. Spinning up the fork's gallery

`.github/workflows/pages.yml` already exists and deploys `skills/diagram-design/assets` to Pages on
every push to `main`. It needs three things on the fork, none of which are code changes:

1. **Enable Actions workflows.** Forked repositories disable inherited workflows until explicitly
   enabled. Actions permissions are already `enabled: true, allowed_actions: all`, but no workflows
   are registered yet.
2. **Enable Pages with source `github-actions`.** Currently returns 404 — no Pages site configured.
3. **Push to `main`.** The workflow triggers on push and on `workflow_dispatch`.

Resulting URL: `https://inflection-agents.github.io/diagram-design/`

**This publishes a public website.** It is a fork of a public MIT project and contains no private
material, but it should be a deliberate call rather than a side effect of a push — and the
Attribution section from M1 PR 1 should be in place before it goes live, so provenance is visible
from the site rather than only from the repo.

---

## 6. Scope

**In scope**
- `## Which variant` sections in every multi-variant type reference, with mechanical rules and a
  named default.
- Gallery restructured to index by relation, with a "reach for this when" line per card and
  variants shown as peers.
- Fork Pages enablement.

**Out of scope**
- Rewriting guidance for the 27 existing single-variant types. They have no variant decision, so
  they get no section. Adding one everywhere for symmetry would be ceremony.
- A search or filter UI. The relation grouping is the navigation; a search box is what you add when
  the grouping has failed.

---

## 7. Consequences

The gallery stops being a showcase and becomes the fastest path from "I have a system to explain"
to "this is the diagram I want" — which is where the cognitive load actually is. The routing
methodology answers that question in prose; the gallery answers it visually, from the same
vocabulary.

The cost is that every new variant now owes a rule before it ships. That is the right tax: a
variant nobody can state a reaching-for condition for is a variant that should not exist.
