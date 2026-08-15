---
name: narrative-spine
description: Build executive presentations, board decks, strategy decks, technical proposals, and whitepapers around a title-driven narrative spine, where reading only the slide titles top to bottom gives the whole argument as a persuasive paragraph. Use when writing, restructuring, reviewing, or condensing any deck, presentation, whitepaper, or long-form proposal; when a deck "jumps" or "loses the room"; when producing an executive walk-around version of a longer deck; or when a speaker script or speaker notes are needed. Pairs with the diagram-design skill for every diagram and the writing-voice skill for the body prose.
license: MIT
---

# Narrative Spine

A deck is a written argument that happens to be paginated. The titles are the argument. The
bodies are evidence. If the titles do not carry the argument on their own, the deck depends
on the presenter being in the room, and it fails the moment it is forwarded to someone who
was not.

**The governing test:** strip everything except the slide titles and read them top to bottom.
They must form a single persuasive paragraph, with no leaps. If they do not, the deck is
not ready, no matter how good the individual slides are.

---

## The unit: kicker + title

Every content slide carries two pieces of text before any body content.

| Element | Form | Job |
|---|---|---|
| **Kicker** | 1 to 4 words, uppercase, tracked | Names the *narrative beat*, so the reader always knows where they are in the argument |
| **Title** | One full declarative sentence | Carries the *argument*, so the spine reads on its own |

```
THE COMPLICATION
This bespoke engineering is exponentially compounded by the strict data
governance required by our global client base.
```

The kicker is a signpost; the title is a claim. Getting this backwards is the most common
structural failure: a topic label as the title (`Cloud Strategy`) and prose in the kicker.

**Titles are sentences, not labels.** `Tenant Isolation` is a label and tells the reader
nothing. `Inside these cells, multi-tenancy is secured at the platform layer via AWS IAM,
preventing application-level data breaches` is a claim, and it survives being read alone.

Rules for titles:

- A subject and a verb. Always.
- One idea. If it needs "and also", it is two slides.
- Opens with a **connective** that binds it to the slide before (except slide 1). The full
  taxonomy of connective moves is in `references/spine-grammar.md`.
- States the **so what**, not only the fact. `We use hexagonal architecture` is a fact.
  `To make these components truly reusable, we use a hexagonal architecture that strictly
  isolates business logic from underlying infrastructure` is a fact plus its purpose.
- Two lines at presentation size. Roughly 20 to 32 words.

---

## Method

### 1. Establish the spine before anything else

`spine.md` is the source of truth. Slides, whitepaper, and speaker script are all rendered
from it. Never start in the deck: starting in slides produces beautiful pages in an
incoherent order, and reordering slides later is far more expensive than reordering lines.

Write, for each slide: kicker, title, the narrative link to the previous slide, and a
one-line brief for the body. Template in `assets/spine.template.md`.

### 2. Choose the arc

Arcs, and when each applies, are in `references/arcs.md`. The default for technical strategy:

```
Situation -> Complication -> Consequence -> Resolution -> [Map] ->
Mechanism -> Proof -> Scale & Safety -> Economics -> Flywheel -> Ask
```

The Map slide is optional and powerful: it declares a taxonomy the rest of the deck navigates.
Once declared, **every downstream slide must signpost which branch it is in** via its kicker
(`DIMENSION ONE - COMPOSABILITY`). A map that is declared and then abandoned is worse than no
map, because the audience keeps waiting for it.

### 3. Read the titles alone

Before writing a single body, read the titles top to bottom as prose. Every "wait, why are we
here now?" is a missing connective, which means a missing slide or a missing clause.

```bash
node scripts/spine-check.mjs spine.md
```

This prints the title-only read-through and flags: label-shaped titles, missing connectives,
unsignposted branches after a map, jargon without translation, over-length titles, house
style violations, and repeated kickers.

### 4. Write bodies as Factor plus So What

Every body element is a fact and its consequence. The fact alone is inert; executives are
being asked to make a decision, and a decision needs the consequence.

```
Trapped Learnings:  Because our codebases are isolated islands, an innovation
                    or a bug fix in one product does not reach the others.
```

Full guidance, including density limits and the one-idea-per-slide rule, in
`references/body-content.md`.

### 5. Brief the diagrams, do not draw them

For each slide needing a picture, write a **diagram brief**: the claim (which is the title),
and what has to be visible for the claim to land. Then invoke the `diagram-design`
skill, which chooses the archetype and renders to the slide canvas.

Two rules keep a deck's pictures coherent:

1. **The diagram's claim is the slide's title, verbatim.** When they diverge, the audience
   believes the picture.
2. **The diagrams are one system, not twelve pictures.** A recurring entity keeps its shape
   and colour on every slide it appears on. Declare a set (`references/diagram-sets.md`) and
   run `python3 scripts/verify-set.py --all` from the diagram-design skill over the whole
   `diagrams/` folder, not just each file as it is made.

### 6. Build, then audit

Render the deck (`references/deck-build.md`), then run the audit in
`references/spine-review.md`. The audit is the Sudden Jump method: for every slide, name the
jump, name the link, propose the fix. It is also how to review someone else's deck.

---

## Non-negotiables

1. **The titles alone tell the whole story.** The governing test. Everything else serves it.
2. **One idea per slide.** The reliable way to confuse a room is to teach infrastructure,
   architecture, and economics on one page.
3. **Every title after the first opens with a connective.** No orphan slides.
4. **Every body point states its so what.**
5. **A declared map is honoured to the end** through kicker signposting.
6. **The title slide sells a business outcome, not a technology.**
   `From Bespoke Services to Exponential SaaS`, not `Serverless Multi-Tenant Platform`.
7. **The ask is specific**: what, why now, and what it unlocks.
8. **No em dashes.** Comma, colon, semicolon, parentheses, or a separate sentence.
9. **The pictures tell the same story as the titles, and the same story as each other.**
   A deck's diagrams are checked as a set, not one at a time.
10. **Jargon earns its place or gets translated.** In a title, only if the audience already
   uses the word.
11. **Every deck has a shorter version.** The spine makes it near-free; generating it is how
    the spine gets stress-tested.

---

## Working style

When proposing titles, structure, or copy, present **two or three labelled options**, the
recommendation first, then a short "What changed" noting the Factor and the So What.

```
Option 1: The Direct Contrast (Recommended)
  Kicker: THE SHIFT
  Title:  Instead of building from scratch, we compose solutions from a shared
          platform catalog, engineering only what is strictly net-new.

Option 2: Action-Oriented
  ...

What changed
  Factor:  names the choice being made (compose vs build), not just the end state
  So what: ties the mechanism to the benefit, so the slide bridges from the problem
```

This makes the reasoning inspectable and the choice fast. It is the working mode for this
skill unless asked otherwise.

---

## Files

| File | Read when |
|---|---|
| `references/spine-grammar.md` | Writing or fixing any title. Kicker forms, the connective taxonomy, title patterns. |
| `references/arcs.md` | Choosing or restructuring the arc. Six arcs with slide-by-slide beats. |
| `references/spine-review.md` | Auditing a deck, yours or someone else's. The Sudden Jump method. |
| `references/body-content.md` | Writing slide bodies. Factor/So What, density, one-idea, jargon translation. |
| `references/formats.md` | Producing exec deck, full deck, whitepaper, or speaker script from one spine. |
| `references/deck-build.md` | Building the `.dc.html` deck against a design system. |
| `references/house-style.md` | Voice and mechanics. Read once, then it is muscle memory. |
| `assets/spine.template.md` | Starting a new deck. |
| `scripts/spine-check.mjs` | After every spine edit, and before delivery. |

---

## Companion skills

`diagram-design` handles every picture. Call it with the slide title as the claim. Do
not hand-draw diagrams in slide markup: rows of boxes separated by text arrows are the
signature of a deck whose diagrams were built by the layout engine rather than designed, and
they undo the credibility the titles earn.

`writing-voice` governs the sentences inside the body content, once the spine itself is
right. Run it on the bodies, not the titles: the titles are the argument, and their rules
live in this document, not in `writing-voice`'s.
