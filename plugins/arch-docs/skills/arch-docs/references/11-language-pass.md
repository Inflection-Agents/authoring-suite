# 11 Language pass

**Goal.** Put every word a reader sees into the owner's voice, as its own pass.
**Produces.** A before and after table the owner can veto, then the rebuilt pages.
**Gate.** Three rounds, then everything still unresolved goes to the owner as open items with a recommendation.

Run this after the diagrams are right. Prose written while placing boxes comes out competent and anonymous, because the
attention went to geometry.

The prose rules belong to the `writing-voice` skill. Load it and follow it; it owns the plain-sentence rules, the banned
words and the lint script, and it is where a voice sheet comes from. This file covers only what is specific to a diagram
set, which is which lines you rewrite, what each kind of line has to do, and how the set reads when the subtitles are put
end to end.

## What is in scope

Every word a reader sees across the set: titles, subtitles, notes, edge labels and captions. Not the SVG descriptions,
which only screen readers read.

Rewrite them in the owner's voice. When the owner has a voice sheet, follow it and let it win over anything else. Read
the stored edit pairs first; a rewrite the owner made wins over the sheet.

## The plain check, on every line, every round

1. **Real subject.** The subject is a thing on the page or in the system. Not "the gap", "the story", "the picture",
   "the takeaway".
2. **Literal verb.** The verb says what happens: reads, writes, charges, retries, skips. Not "powers", "drives",
   "feeds", "unlocks".
3. **No colon in the middle.** Put the point in the first clause.
4. **Not a slogan.** Read it aloud. If it sounds like a headline, rewrite it in the words the owner would use across a
   table.

A line that fails any of the four gets rewritten, even when the rewrite is longer.

## What each element has to do

- **Title** names what the diagram shows. It makes no claim and sells nothing.
- **Subtitle** is one direct sentence, point first, concrete actor as the subject. A second sentence is allowed only to
  point at another page.
- **Note** adds a fact the diagram cannot show: a limit, a time, a reason, a constraint. A note that repeats the subtitle
  or a label gets cut.
- **Edge label** is a literal verb phrase for what moves along the line. Never "talks to", "handles", "manages".

## Bans

Em dashes, always. And the word list the `writing-voice` skill owns, which covered these on the engagement this came
from:

```
leverage, utilize, facilitate, comprehensive, crucial, essential, pivotal, seamless, powerful, robust, empowers,
ultimately, arguably, it's worth noting, that said, in conclusion, overall
```

Take the current list from that skill rather than from here, and lint against its script.

## The subtitle-only read

Put every subtitle in manifest order into one paragraph and read it as prose. It has to make one argument. Report three
faults: two subtitles that could swap places, a term used before the page that introduces it, and a subtitle with no
link to the one before it. This is the same read [09](09-set-review.md) does, run again now that the words have moved.

## Pin the terms

Pin an ambiguous term in parentheses at first use, in the owner's words: "property (a verifiable characteristic)". A term
that selects data gets its exact condition instead of a gloss. Label an illustrative or estimated value once, where it
first appears, and never label an estimate as correct. When the owner rejects a term, ban it across the set and sweep
every page for it, including the legend.

## How the rounds run

Show the owner a before and after table for every line changed, grouped by page, before applying anything. Then apply,
rebuild, and confirm the pages still pass their checks.

Stop after three rounds. Anything still unresolved goes into a list of open items with your recommendation, so the owner
makes the call instead of you rewriting a fourth time.

## Two rewrites the owner made, and the habit each shows

| Drafted | The owner's rewrite | The habit |
|---|---|---|
| "The people and outside systems stay the same as today." | "We propose replacing the decision service with two new services, and configuration flows down from one orchestrator while the public interfaces stay the same." | Say what we are doing and who does it. A sentence about what did not change is not a claim. |
| "The decision service is gone. Two new services take its place." | "The orchestrator reads the configuration and passes it down to the capabilities and their downstream dependencies." | Name the mechanism, not the absence. "X is gone" is a slogan, and the sentence that follows it is the one worth writing. |

Store every rewrite the owner makes as an edit pair next to the set, with a one-line note naming the habit. Read the
pairs before writing new prose. The owner's rewrite beats the voice sheet.

## Two short prompts to reach for

One line at a time, when the owner wants options rather than a decision:

```
Rewrite this subtitle. Give me four options, each with the actor as the subject and a literal verb, ordered from
most plain to most compressed. No colons, no em dash, no slogan. Then say which one you would ship and why: <LINE>
```

A sanity check that changes nothing:

```
Read the titles and subtitles of this set as a list and tell me, in five sentences, the argument it makes. Then
tell me the three lines that are working hardest and the three that are carrying nothing. Do not rewrite anything.
```
