# 07 Build agents

**Goal.** Draw the approved diagrams in parallel without two agents touching the same file or drifting apart on conventions.
**Produces.** The specs and the built pages, plus one report per agent naming what went wrong.
**Gate.** Every page meets the definition of done in the brief, and the set check and the consistency check pass across the wave.

In this phase you are the lead. You do not draw. You split the work, write one prompt per build agent, run the set-level
checks between waves, and collect the reports. Read `_brief/brief.md` before splitting, because the brief fixes the
conventions every agent has to share and the per-diagram paragraphs decide which pages belong together.

## How to split the work

- **Give each agent disjoint file ownership and name it in the prompt.** One agent owns one set of spec files and the
  pages they produce, and touches nothing else. An agent that finds a problem in a file it does not own reports it to
  the owner instead of fixing it.
- **Group diagrams by visual type, not by number**, so one agent carries the idioms of one type across several pages.
- **Run at most four agents at once.** The library and the manifest are shared state.
- **Nobody edits the generator library.** A missing capability comes back as a report line, and the owner adds it once,
  centrally.
- **Nobody runs the whole-set build.** Each agent builds only its own pages. The lead runs the set build after the wave.
- **Run the set check and the consistency check after each wave**, before starting the next one.

## The agent prompt

Send this as written, with the placeholders filled. It carries all ten points of the agent kernel in
[../SKILL.md](../SKILL.md), so check a change to it against that list.

```
You are drawing diagrams <NN to NN> of the <NAME> set. Work directory: <PATH>

**Read first, in this order:** `_brief/facts.md` (the source of truth), `_brief/brief.md` (conventions and the
definition of done, including your per-diagram paragraphs), `_build/<library>.py` (the library, do not edit it), and
the type reference for each visual type you will use.

**You own exactly these files:** `<spec paths>` and the pages they produce. Do not create, edit, rebuild or delete
anything else. **Other agents are editing specs <LIST THE NUMBERS> right now**, so do not touch those, and do not
run the whole-set build command; the lead runs it after everyone reports. If another page is wrong, say so in your
report. You may write scratch files under `<SCRATCH DIR>`.

**For each diagram:**

1. Read the type reference and the two reference specs the brief names, and look at their rendered images.
2. **Plan the coordinates on paper first.** List every box as x, y, width, height and every connector as its
   waypoints before you write a line of the spec. Orthogonal routing without crossings is the hard part of this
   job, and it cannot be recovered by nudging afterwards. Use the hop primitive for crossings you cannot avoid.
3. Write the spec. Use the library's primitives; put anything the library cannot do in a local helper in your own
   spec file.
4. Build it, screenshot it, and **look at the image with the Read tool**. Never report a diagram you have not
   looked at. Checking the markup is not looking at the page.
5. Iterate until it meets the definition of done. Expect two or three rounds; one round is usually a page you have
   not really looked at.
6. Run the self-check and fix what it reports. Warnings the brief names as known false are disposed of by verifying
   them in the image and saying so, not by changing the page.

**Rules that override your judgment:**

- Every claim traces to the facts file. When the facts do not cover something you need, draw it as an open item or
  leave it out and report it. Do not fill the gap.
- Illustrative names are labelled illustrative on the page.
- Connector styles mean what the brief says they mean, on every page.
- The accent goes on at most two elements, counting connectors.
- Voice: plain sentences, real subject, literal verb, no em dashes, no banned words.
- When two references contradict each other, report the contradiction. Do not pick a side quietly.

**Report back, short:** one line per diagram saying what it shows and anything you had to decide; every place the
facts file was thin; every rule you had to bend and why; every warning you judged false, with the reason; **every
library gap you worked around**; and anything you could not resolve. Do not pad the report with what went fine.
```

## The line that compounds

The library-gap line turns every builder into a reporter on the tool. Ask for it from the first wave, because a helper
written three times in three specs is a missing primitive, and the handback audit in
[13](13-handback-audit.md) can only find it if the builders wrote it down.

## When the wave comes back

Read every report before starting the next wave. A thin spot in the facts file goes back to the owner as a question, not
to the next agent as an assumption. A page an agent flagged but does not own goes to [08](08-page-critique.md). Findings
that span pages wait for [09](09-set-review.md).
