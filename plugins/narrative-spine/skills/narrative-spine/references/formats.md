# Formats

One spine, several deliverables. The spine is the source of truth; every format is a
rendering of it. When a format needs a different argument, the spine was wrong.

---

## The pipeline

```
spine.md                          <- source of truth: kickers, titles, links, briefs
   |
   +-- full deck        (.dc.html, 20-26 slides)
   +-- executive deck   (.dc.html, 7-9 slides)
   +-- whitepaper       (.md / .docx / .pdf)
   +-- speaker script   (.md)
   +-- diagrams         (.svg, via the architecture-diagram skill)
```

Change the argument in `spine.md`, then re-render. Editing a title directly in a deck and not
in the spine is how the executive version silently drifts out of sync with the full one.

---

## Full deck

The complete argument, presented live. 20 to 26 slides for a technical strategy arc.

- Every beat gets its own slide
- Mechanism sections get 3 to 5 slides each
- Every slide carries kicker, title, and 3 to 4 body elements
- Speaker notes on every slide

Build mechanics in `references/deck-build.md`.

---

## Executive walk-around

7 to 9 slides, read **without a presenter**. The hardest format, because every slide has to
survive alone.

Produced by **re-arguing** at lower resolution, never by deleting slides. Deleting slides
deletes connectives, which is precisely what produces a version with unnatural leaps.

Procedure:

1. Choose the beats that must survive: Challenge, Pivot, each Dimension, Economics, Flywheel,
   Ask.
2. For each, write a **new** title carrying the merged content, with its own connective.
3. Where a merged slide holds two or three concepts, split it, even at the cost of slide
   count. A nine-slide deck that lands beats a seven-slide deck that confuses.
4. Run the title-only read-through on the result.
5. Any jump found here reveals a weak joint in the **full** deck at the same point. Fix both.

Since nobody is narrating, add a short executive summary paragraph on the title slide, so a
reader who opens it cold has the frame before slide 2.

---

## Whitepaper

The same spine as prose. Section headings are the titles, and they still have to pass the
governing test.

```markdown
# From Bespoke Services to Exponential SaaS

## Executive summary
[120 words: the entire spine as one paragraph. Written last, from the finished spine.]

## Despite clear repeating patterns, we build every solution from scratch
[The situation beat, expanded with evidence a slide could not hold.]

## This is compounded by the data governance our global client base requires
...
```

What a whitepaper adds, and a deck cannot carry:

- Derivations behind the numbers
- Caveats and the conditions under which the argument fails
- Prior art, and why the alternatives were rejected
- Implementation detail for a reader who will build it
- References

What it must not add: a different argument, a different order, or a different vocabulary.

Diagrams render at the `standalone` profile (`0 0 1440 810`) or as full-page figures, with a
caption stating the claim. Use the `light` preset when the document will be printed.

---

## Speaker script

For a rehearsed delivery: keynote, board presentation, or any high-stakes room.

Write for the ear, not the eye. Then read it aloud, because the mouth finds what the eye
skips.

Per section:

```
[0:00] OPENING

I am not going to start with the architecture. [PAUSE]

Last quarter we won four clients. We also built authentication four times.

[PAUSE, let it land]

That is the whole problem, and everything I am about to show you follows from it.
```

Conventions:

- `[PAUSE]` where silence does the work. Silence is emphasis, and it has to be scripted or it
  will not happen.
- `[EMPHASIS]` on the words that carry the point
- `[0:00]` timing markers at section breaks
- Short paragraphs: one breath each
- Contractions, since people speak in them

Also produce:

- **Structure overview**: a table of section, topic, time, purpose
- **Opening options**: story-led, question-led, statement-led
- **Closing options**: call to action, callback to the opening, vision
- **Contingencies**: what to cut if running long, what to expand if short
- **Anticipated questions**: the three hardest, with real answers

The script's spine is the deck's spine. Sections map to beats, and the connectives become
spoken transitions: "Despite that", "Which brings us to", "So here is what we are asking for".

---

## Speaker notes versus script

| | Speaker notes | Script |
|---|---|---|
| Lives in | The deck, per slide | A separate document |
| Length | 2 to 5 sentences | Full prose |
| Use | Presenter knows the material | High-stakes, rehearsed, or timed |
| Contains | The line that matters, the translation, the likely question | Everything, verbatim |

Both come from the spine. Notes are the compressed form.

---

## Keeping formats in sync

The executive deck, whitepaper, and script all derive from one spine, so drift is a real
risk once edits start arriving.

- Edit `spine.md` first, always
- After any spine edit, re-run `scripts/spine-check.mjs` and re-check each rendered format
- If a format needs a title the spine does not have, the spine is missing a beat: add it
  there, then re-render
- Keep the glossary in the spine, so vocabulary stays consistent across every format
