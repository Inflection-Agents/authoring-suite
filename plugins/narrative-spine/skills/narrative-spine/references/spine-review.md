# Spine Review

The audit. Use it on a draft, on a finished deck that is not landing, and on someone else's
deck. It is also the method for turning a rough deck into a tight one without rewriting the
content.

---

## The Sudden Jump method

The core move. For every slide from 2 onward, answer three questions in order:

1. **The Sudden Jump** - what does the audience have to infer to get here from the previous
   slide? Name the unstated leap.
2. **The Narrative Link** - what is the actual logical relationship between these two slides?
   This is a connective move from `spine-grammar.md`.
3. **The Fix** - the proposed kicker and title that make the link explicit, plus any body
   tweak needed.

Worked example:

```
Slide 8: Component Design

  The Sudden Jump
    We went from "let us use a catalog" to "here is what hexagonal architecture is."
    The audience has to infer that reusability requires a particular internal design.

  The Narrative Link
    To make a component truly reusable, as promised on the previous slide, it cannot
    be hardcoded to its infrastructure. This is the HOW behind that promise.

  The Fix
    Kicker: COMPONENT DESIGN
    Title:  To make these components truly reusable, we use a hexagonal architecture
            that strictly isolates business logic from underlying infrastructure.
    Body:   group application code, adapter, and IaC under the one artifact idea, so
            the slide shows the boundary rather than describing it.
```

Where no honest link exists, the slide is in the wrong place, or a slide is missing between
them. Both are structural fixes, not wording fixes. **Never paper over a missing slide with a
connective phrase**: it produces a title that claims a logical relationship the content does
not support, which is worse than the jump, because now the argument is dishonest as well as
hard to follow.

---

## Pass 1: the title-only read-through

Mechanical, and always first.

```bash
node scripts/spine-check.mjs spine.md
node scripts/spine-check.mjs "deck/My Deck.dc.html"
```

Then read the printed titles aloud as a single paragraph. Aloud matters: the ear catches
missing connectives that the eye skims over.

Mark every place where:

- A sentence could open with "and another thing" without loss. That is a list, not an
  argument.
- A term appears that was never introduced.
- The argument arrives somewhere without having travelled there.
- Two consecutive titles could swap with no damage. If order does not matter, there is no
  argument, only a collection.

---

## Pass 2: per-slide audit

For each slide:

- [ ] Is the title a **sentence with a verb**, not a label?
- [ ] Does it open with a **connective** binding it to the previous slide?
- [ ] Does it carry **one** idea?
- [ ] Does it state the **so what**, not just the fact?
- [ ] Does the **kicker** add position rather than repeat the title?
- [ ] If a map was declared, is the **branch signposted**?
- [ ] Does the **body support the title**, or wander to an adjacent point?
- [ ] If there is a diagram, does its **claim equal the title**?
- [ ] Would the slide survive being **read without the presenter**?

---

## Pass 3: the executive pass

Read as a CEO, CFO, or non-technical board member. Different failure modes surface.

### Jargon

For every technical term in a **title**, ask whether the audience already uses that word. If
not, either translate it or move it to the body where context can carry it.

| Term | To an executive it means | Say instead |
|---|---|---|
| Hexagonal architecture | nothing | "We isolate the logic, so a client demanding private cloud does not force a rewrite of our core IP." |
| Federated micro-frontends | nothing | "Our UI teams ship independently instead of waiting for each other to finish." |
| IAM ABAC/RBAC | nothing | "The credential cannot see another tenant's data, so the mistake is not available to make." |
| Serverless | vaguely, cost | "We pay only for what we use, and nothing while idle." |
| Sovereign cells | nothing | "Data stays in the region the law requires, because of where we deploy, not because of custom code." |

The term can stay in the body once the outcome has been stated. The rule is that the
**outcome comes first**, because that is the part the audience can act on.

### Business framing

- [ ] Does the **title slide** sell an outcome, not a technology?
- [ ] Is there a slide that makes the **money argument** explicitly?
- [ ] Is the **ask** specific: what, why now, what it unlocks?
- [ ] Does any slide require prior technical knowledge to parse the **title**?
- [ ] Is there a moment of **honest downside**? A deck with no cost reads as a sales pitch.

---

## Pass 4: the condensation test

Produce the short version. This is the strongest structural test available, because a spine
with weak joints cannot be condensed without visibly breaking.

1. Pick the beats that must survive: usually Challenge, Pivot, each Dimension, Economics, Ask.
2. **Re-argue** them at lower resolution. Do not delete slides and hope.
3. Re-run the title-only read-through on the short version.
4. Where the short version now jumps, the **long version has a weak joint at the same place**.
   Fix it in both.

Merging beats needs care: three merged beats must be presented as cause and effect, with the
relationships labelled, not as three parallel facts.

---

## Pass 5: after delivery

The most valuable input available, and the one usually discarded. Record it in the spine.

| Signal | Diagnosis |
|---|---|
| A question that a later slide answers | The order is wrong, or the earlier slide over-promised |
| A question the deck never answers | A missing slide, usually an objection beat |
| "Can you go back to slide N?" | Slide N had too much on it |
| Confusion about one specific slide | That slide holds two or three ideas; split it |
| The ask was misunderstood | The ask was not specific, or the payoff was not established first |
| Silence | Either it landed or nobody followed. Ask one person afterwards which. |

A confused audience is data about the deck, not about the audience. The single most common
root cause is one slide carrying several concepts that each deserved their own page.

---

## Reviewing someone else's deck

Same passes, different delivery. Lead with the structural diagnosis, not with line edits:
rewriting their titles first reads as a rewrite of their thinking, and the feedback gets
rejected before it is heard.

Useful order:

1. Show the **title-only read-through**. It is objective and usually self-evident.
2. Name the **two or three biggest jumps**, using the three-part format.
3. Offer **options** for each fix, recommendation first, with what changed and why.
4. Only then, line edits.

Give the diagnosis before the prescription. Most authors fix the rest themselves once they
see the read-through.
