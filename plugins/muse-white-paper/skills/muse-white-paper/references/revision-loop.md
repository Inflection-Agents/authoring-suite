# Revision Loop

Two-pass titles, three revision rounds, then stop. Grounded in design Section 6
(`docs/plans/2026-09-12-muse-white-paper-design.md`). The connective taxonomy
and the title-only read-through it cites live in `narrative-spine` under
`references/spine-grammar.md` and `references/spine-review.md`.

Terms: a section's **fact pack** is the evidence and numbers its body argues
from; its **link pack** is the outbound citations proving it. The plugin
proposes one diagram brief plus a link pack per section before prose starts.

## Two-pass titling

**Pass one: titles before prose.** Set every section title first. Each title
states the section's claim as a sentence with a verb. No body drafts until the
spine, diagram briefs, and link packs are signed.

**Pass two: retitle after bodies.** Once bodies exist, revisit each touched
section and keep whichever title carries the section alone for a reader
skimming headings, the old one or a new one. Two rules constrain the choice:

- **Connective rule.** Every title after the first opens with a move binding
  it to the previous section: an explicit connective from the taxonomy
  (concession, escalation, consequence, resolution, and the rest), anaphora
  pointing back ("this X," "these Y"), or at minimum a shared term. A title
  with none of the three is an orphan.
- **Title-only-read rule.** Read the titles aloud as one paragraph; they must
  form a single argument. Mark every place where a sentence could open with
  "and another thing" without loss, a term appears never introduced, the
  argument arrives somewhere without travelling there, or two consecutive
  titles could swap with no damage.

## Per-round order

Run each round in this order. Each step fires only on its condition.

1. **Reorder on broken connectives.** When no honest connective fits between
   two adjacent sections, the order is wrong or a section is missing between
   them. Move the section first; the connective then turns obvious. Never
   paper over a missing section with a connective phrase: a title claiming a
   link the body does not support reads worse than the jump.
2. **Merge on shared fact packs.** Sections arguing from the same evidence
   merge into one. Retitle the result as cause and effect with the
   relationship labelled, not as parallel facts. Split back out any merged
   section holding two or three concepts.
3. **Drop sections alive only by link packs.** A section whose body adds
   nothing beyond its outbound citations gets cut, with any worth-keeping
   links folded into a surviving section's pack.

After any touch, retitle the touched sections and rerun both gates: the spine
check (titles alone read as one paragraph or drafting stops) and the budget
check (words plus figure area). Voice check runs last and flags only.

## Cap

Three rounds. Unresolved breaks land in `DECISIONS.md` as open items with the
owner's call recorded, not a silent fourth rewrite.
