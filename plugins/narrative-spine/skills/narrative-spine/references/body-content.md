# Body Content

The title carries the argument. The body carries the evidence. Its only job is to make the
title believable, and anything that does not do that belongs in the speaker notes, the
appendix, or nowhere.

---

## Factor plus So What

Every body element is a fact and its consequence. The fact alone is inert. An executive is
being asked to decide, and a decision needs the consequence.

```
Trapped Learnings
  Because our codebases are isolated islands, an innovation or a bug fix in one
  product does not easily translate to another.
```

The label names the factor; the sentence delivers the so what.

| Weak (factor only) | Strong (factor plus so what) |
|---|---|
| "Each client has its own codebase." | "Every client adds an isolated codebase and infrastructure stack that we then support forever." |
| "We use AWS IAM for isolation." | "The credential cannot see another tenant's data, so the mistake is not available to make." |
| "Workloads are bursty." | "Because our workloads are bursty and batch-heavy, a shared model is the most efficient shape for our infrastructure." |
| "We package infra with CDK." | "Infrastructure travels with the code as one artifact, so deploying to a new region is not a new project." |

Applying this to every point is what turns a description into an argument.

---

## Density

Sparse by default. Slides are read in seconds, from a distance, by people also listening.

| Element | Limit |
|---|---|
| Body elements per slide | 3, occasionally 4. Never 5. |
| Words per body element | 25 |
| Paragraph, where one is used | 55 words |
| Items in a list | 3 to 5 |
| Text inside a card | 1 short title plus 1 to 2 lines. Never a paragraph. |
| Numbers on one slide | 3 |

If content does not fit, the slide has too many ideas. Split it. Shrinking the type is how a
slide that read on a laptop fails in the room it was made for.

---

## One idea per slide

The rule that prevents the most damaging kind of failure, where an audience is confused but
cannot say why, so the feedback arrives as "it was a lot".

A single slide covering regional cells, multi-tenancy, and unit economics forces the audience
to absorb infrastructure, application architecture, and finance simultaneously. Each is clear
alone. Together they are a wall.

The fix is always the same: split along the natural hierarchy, and let each slide answer one
question.

```
Slide A - the WHERE     Regional cells: standardised AWS accounts, one per geography.
Slide B - the HOW       Multi-tenancy: one deployment inside a cell serves many clients.
Slide C - the WHY       Economics: sharing capacity drives cost per client toward zero.
```

Three clear slides beat one dense one, even when slide count is constrained. The constraint
is attention, not pagination.

### Detecting a merged slide

- The title needs "and"
- The body has two headings
- Explaining it aloud takes more than about ninety seconds
- Someone asks to go back to it
- It needs two diagrams, or one diagram doing two jobs

---

## Body structures

Pick by the job of the slide.

### Three factors
The default for problem and mechanism slides.

```
Undifferentiated Heavy Lifting   Core capabilities like authentication, logging, and
                                 ingestion share the same shape across solutions, yet
                                 we rebuild them every time.
Trapped Learnings                Isolated codebases mean a fix in one product does not
                                 reach the others.
Wasted Talent                    Engineers write foundational plumbing instead of the
                                 business logic clients actually pay for.
```

### Two dimensions
For map slides, and anywhere a taxonomy is introduced.

```
Dimension One - Composability     Action: engineers assemble shared components into products.
                                  Value:  solves the engineering bottleneck.
Dimension Two - Multi-tenancy     Action: one deployed product serves many clients.
                                  Value:  solves the hosting and margin bottleneck.
```

### Before and after
For contrast slides. Structure both sides identically, or the reader cannot diff them.

### Worked example
For proof slides. One real named thing, decomposed. Naming it is what makes it evidence
rather than illustration.

### The ask
Workstreams, each with the work and its value, then a closing line on what it unlocks.

```
Component interfaces      Work:  define the contracts and implement the headless logic.
                          Value: creates the boundaries engineers assemble against.
Composable infrastructure Work:  build the reusable IaC blocks that wrap each component.
                          Value: infrastructure composes without custom deployment code.
Iterative hardening       Work:  deploy the first components across multiple configurations.
                          Value: real reusability comes from repetition, not from design alone.

Every block delivered permanently removes work from every deal that follows.
```

Naming hardening as real work is what makes an ask credible to an engineering audience and
honest to a financial one.

---

## Numbers

- Put the number where the claim is, not two slides later.
- One number per point. Three numbers on a slide is the ceiling.
- Always give the comparison: "45 to 58 days" beats "58 days".
- Mark illustrative figures as illustrative, on the slide. Being caught implying precision
  costs more than the point was worth.
- Round for speech. "About sixty percent" is more usable aloud than "58.4%".

---

## Speaker notes

Notes carry what the slide cannot: the aside, the translation, the anticipated question.

For each slide, note:

1. **The line that matters.** The one sentence to actually say.
2. **The translation.** How to say it to a non-technical room.
3. **The likely question**, and the answer.

```
Discipline at the edges. Clean interfaces mean an engineer wires components without
reverse-engineering them.

For a non-technical room, skip the word hexagonal and lead with the business value: we
isolate the logic so that if a client demands private cloud, or an infrastructure choice
changes, we do not rewrite the core IP.

Likely question: does this slow us down at the start? Yes, modestly, on the first two
components. It stops mattering from the third onward.
```

---

## Anticipated questions

Prepare the three hardest questions with real answers. This preparation is frequently worth
more than the slides, because it is where a deck is actually won or lost.

Hardest is not most common. It is the question that, if answered badly, ends the meeting:

- "What does this cost, and what are we not doing instead?"
- "What if we do nothing?"
- "Who has done this and failed?"
- "Why now rather than next year?"
- "What happens if the two engineers who understand it leave?"
