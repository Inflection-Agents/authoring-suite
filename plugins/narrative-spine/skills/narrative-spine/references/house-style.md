# House Style

Voice and mechanics. Read once; after that it should be automatic.

---

## Mechanics

**No em dashes.** Not in titles, bodies, speaker notes, whitepapers, or diagram labels. Use a
comma, a colon, a semicolon, parentheses, or a separate sentence. This is a hard rule and
`scripts/spine-check.mjs` enforces it.

| Instead of | Write |
|---|---|
| `We build from scratch — every time.` | `We build from scratch, every time.` |
| `The result — higher cost.` | `The result: higher cost.` |
| `Cells (one per region) — solve residency.` | `Cells, one per region, solve residency.` |

For compound kickers, use a middot: `DIMENSION TWO - MULTI-TENANCY`.

**Casing.** Kickers and section labels uppercase. Titles sentence case. Body sentence case.
Never title case a full-sentence title: it turns a claim back into a label.

**No emoji.** Anywhere in a deliverable.

**No exclamation points.**

**Numerals** for anything countable. Spell out only at the start of a sentence.

---

## Voice

Calm, confident, specific. Claim-driven rather than descriptive. Short declarative sentences.

**Commit.** No "could potentially consider". If the recommendation is a recommendation, make
it. If it is genuinely uncertain, state the uncertainty as a fact: "We do not yet know
whether X; the first two components will tell us."

**Own it.** "We build every solution from scratch", not "solutions are built from scratch".
Passive voice with no actor reads as evasion, especially in a problem statement.

**Person.** First person plural for the organisation's own work. Second person only in a
direct call to action. Avoid "I" outside a speaker script.

**No hype.** No "revolutionary", "game-changing", "world-class", "best-in-class",
"seamless", "leverage" as a verb where "use" works, "synergy" at all.

**Concrete over abstract.** "Engineers spend the first three weeks of every deal rebuilding
authentication" beats "significant duplicated effort exists across the portfolio".

---

## Problem statements

The problem statement determines whether the rest of the deck gets a fair hearing. Three
requirements:

1. **Name the choice, not just the outcome.** "Despite clear repeating patterns across our
   solutions, we build or fork every use case from scratch" is stronger than "our costs are
   high", because it names what we are doing, which is the thing we can change.
2. **State the hidden cost.** Trapped learnings, wasted engineering time, compounding
   maintenance. The visible cost is rarely the expensive one.
3. **No blame.** Describe the system, not the people. A problem statement that reads as an
   accusation puts the room in defence and the argument never lands.

Test: can the problem be stated in one sentence that an executive would repeat accurately to
someone else? If not, it is not sharp enough yet.

---

## Naming discipline

Vocabulary drift is a silent killer. When two words are used for one thing, or one word for
two things, an audience stops trusting the whole model.

Fix the vocabulary before writing, and keep it fixed:

| Term | Means | Not |
|---|---|---|
| Component | A single-function, independently deployable artifact | Service, module, block, piece |
| Product | A composed, deployable solution | Solution, app, offering |
| Client | An organisation that buys | Customer, tenant, account |
| Tenant | A client's isolated presence inside a deployed product | Instance, deployment |
| Cell | A regional deployment boundary | Region, environment, stack |

The client / product distinction is the one that most often breaks a platform narrative.
Engineers build **products**; **clients** are hosted in them. A slide that says "every client
benefits from the R&D done for the others" quietly implies engineers build per client, which
contradicts the whole argument. It should read "every **product** benefits from the R&D done
for the others."

Build the glossary during the spine, not after. Every slide that gets it wrong has to be
found and fixed later, and some will be missed.

---

## Definitions

When a term must be defined, define it in one sentence with its consequence attached.

> A **component** is a single, independently deployable artifact that performs one function,
> packaged with its application code and infrastructure as code for fast, self-contained
> deployment.

The factor is "single-function, independently deployable artifact". The so what is that
packaging code and infrastructure together makes it self-contained, removing external
dependencies at deploy time. A definition without its so what is a dictionary entry, and the
audience will not know why it was worth their attention.

---

## Length

| Artifact | Target |
|---|---|
| Slide title | 20 to 32 words, 2 lines at presentation size |
| Kicker | 1 to 4 words |
| Subtitle (cover) | 1 sentence, up to 40 words |
| Body element | 25 words |
| Speaker note | 2 to 5 sentences |
| Executive summary paragraph | 120 words |
| Full deck | 20 to 26 slides |
| Executive deck | 7 to 9 slides |

---

## Checklist

Before delivery:

- [ ] No em dashes anywhere
- [ ] No emoji, no exclamation points
- [ ] Kickers uppercase, titles sentence case
- [ ] Vocabulary consistent against the glossary
- [ ] Client and product used precisely
- [ ] No hedging in the recommendation
- [ ] No hype words
- [ ] Every claim either evidenced or marked as a projection
- [ ] Numbers have comparisons
- [ ] Illustrative figures labelled as illustrative
