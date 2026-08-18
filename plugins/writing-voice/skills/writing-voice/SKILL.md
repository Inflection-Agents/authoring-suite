---
name: writing-voice
description: "Enforce a specific, audience-tailored prose voice and catch LLM writing slop in chat responses, docs, commit messages, PR descriptions, and deck body content. Use whenever prose is being drafted, reviewed, or edited, not just decks. Run the lint script on a draft before treating it as final: the rules alone catch what a human reviewer would flag, the script catches what's easy to miss by eye."
license: MIT
---

# Writing Voice

Most drafts read like a draft because they hedge, pad, and average out. This skill names the
specific tics that cause that and gives a script that finds them mechanically, instead of
relying on a re-read to notice.

## Core rules

Full list with examples in `references/voice-rules.md`. The shape of it:

- **A banned-word list** (`delve into`, `leverage`, `utilize`, `comprehensive`, `crucial`,
  `seamless`, `robust`, `ultimately`, `arguably`, and about twenty more) plus a hard ban on the
  em dash. No exceptions clause for either.
- **No throat-clearing.** Start with the claim, not a restated question or an announcement of
  what comes next.
- **No hedging.** State the position. If genuinely uncertain, name the variable that's
  uncertain, not a softening phrase.
- **Kill the rule-of-three and the `not X, it's Y` construction.** One precise example beats
  three generic ones. A real contrast beats a scripted one.
- **Vary sentence length.** Flat medium-medium-medium rhythm is a tell on its own, independent
  of word choice.
- **Concrete over abstract**, grounded in a number or a named artifact before generalizing.
- **One job per paragraph.** No tacked-on clauses bolting a second claim onto a sentence that
  already made its point.
- **No bullet-itis.** A list of bullets can't carry a causal argument the way a paragraph can.
  Don't reach for bullets to avoid writing the sentence that connects two ideas.
- **No sycophancy.** No "great question," no validating the premise before answering it.

## Audience modes

Full detail in `references/audience-modes.md`. Three presets, matched to who's reading:

| Mode | Structure | Jargon |
|---|---|---|
| Executive | Answer first, then up to three supporting points | Cut unless load-bearing |
| Engineering | Evidence can precede the conclusion; precision over brevity | Permitted if precise |
| Product | Answer first, trade-offs explicit | Explain anything engineering-specific |

Pick the mode from who's actually reading, not from the topic. A technical decision written
for an executive audience still opens with the answer.

## Verification: `scripts/verify-voice.py`

Checks the mechanical half of the rule list: banned words and phrases, em dashes, the
`not X, it's Y` pattern, sentence-length variance, intensifier density, paragraph length,
"that is X" frequency, and bullet-to-prose ratio. Run it on a draft with:

```
python3 scripts/verify-voice.py path/to/draft.md
```

It flags candidates, not verdicts. A flagged em dash is always wrong, but a flagged short
paragraph might be a deliberate beat. Read every flag; don't auto-apply fixes.

What it can't check stays a judgment call: whether a claim is genuinely concrete, whether the
piece actually opens on tension and closes on a tool, whether the jargon matches the audience.
No formula substitutes for reading the sentence.

## Companion skills

`narrative-spine` structures a deck's argument. This skill governs the sentences inside it, so
run it after a deck's spine is right, on the body content, not the titles. `diagram-design`
handles the pictures. None of this applies to diagram labels, which follow their own, much
shorter, style rules.
