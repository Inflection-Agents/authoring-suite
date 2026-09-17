# Composition

**Goal.** Keep this skill out of the business of drawing and of prose rules.
**Produces.** Nothing. This file says who owns what.
**Gate.** None.

This skill owns the process and the artifacts. It owns the interview, the reconciliation, the facts file, the
diagram list, the brief, the pruning decision, the handback audit and the ledger. Everything else it calls.

## What each skill owns

| Skill | Owns | This skill calls it for |
|---|---|---|
| `diagram-design` | the visual types, the design system, the connector rules, the complexity budgets, the generator library, the checkers, the page prose reference | drawing every page, and every mechanical check on a page |
| `writing-voice` | the voice rules and the prose linter | the language pass, and the voice line in every agent prompt |
| `narrative-spine` | a deck's title-driven argument | a set that will be presented as a deck rather than read as a document |

When a rule lives in one of those skills, reference it by name instead of restating it. A restated rule goes stale
the first time the owning skill changes, and then two sources disagree with nothing to break the tie.

## Where the boundary sits

**Drawing.** This skill decides which diagrams exist, in what order, and what each one must prove. `diagram-design`
decides how a diagram of that type is drawn. A phase reference here never specifies a corner radius or a marker.

**Prose.** This skill decides when the language pass runs and what it covers. `writing-voice` decides what good
prose is. The one thing this skill adds is the page as a unit: a title, a subtitle, notes and edge labels, each
with its own rule, which `diagram-design` carries in its page prose reference.

**Voice sheets.** The owner's voice sheet, wherever it lives, outranks both. A rewrite the owner made outranks the
sheet. Store those rewrites as edit pairs next to the set.

## When a skill is missing

The sequence still works. Without `diagram-design` you are choosing types and enforcing consistency by hand, which
is slower and produces a set that drifts. Without `writing-voice` the language pass falls back to the rules in
phase 11. Say which skill is missing and what the owner loses, once, and carry on.

## What this skill must never absorb

A generator library, a checker, a design system, or a voice sheet. Each of those belongs to a skill that already
owns it, and a copy here would be a second source of truth for something this skill does not decide.
