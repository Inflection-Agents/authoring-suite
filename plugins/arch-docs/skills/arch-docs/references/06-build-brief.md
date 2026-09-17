# 06 Brief

**Goal.** Fix every convention that twenty agents would otherwise decide twenty different ways.
**Produces.** `_brief/brief.md`, one paragraph per diagram, read by every build agent after `facts.md`.
**Gate.** Conventions are fixed.

A build agent reads `_brief/facts.md`, then this file, then draws one diagram without talking to the owner. Write
the brief for that reader. It settles what a dashed line means, which element ids exist, how deep a zoom goes, and
what done is.

Enter this phase once the owner has approved the list in [05](05-diagram-list.md).

## Sections, in this order

**1. Frame.** Client, audience, which deliverable this is, and the standing instructions from
[01](01-kickoff.md): first draft with more detail than needed, box-count limits suspended, every other rule of the
diagram skill applies.

**2. Files.** Exact paths for: the facts file; any companion set to match or contrast against; the generator
library, with "do not edit it, write local helpers in your spec instead"; two or three reference specs worth copying
idioms from, named with what each one demonstrates; where the agent's own spec goes; the screenshot command; the
self-check command; the skill reference files for each visual type.

**3. Definition of done, per diagram.** Use these four, adjusted to the tooling. [07](07-build-agents.md) references
them by name rather than restating them, and [08](08-page-critique.md) checks against them.

```
1. The spec prints no warnings, or only warnings you verified are false by looking at the image.
2. The image shows no line through a label, no label touching a box, no two connectors sharing a path, no connector
   behind a box that is not its endpoint, no overflowing text, and a readable legend.
3. The self-check prints OK.
4. Every claim traces to the facts file. Open items are drawn as open, never as designed.
```

**4. Library cheat sheet.** Every call a spec needs, with its signature and the allowed values, and anything added
since the last set marked as new. This is what stops agents from reading the library source.

**5. Conventions.** The consistency rules:

- Fixed meaning for every connector style, one line each. A reader who learns a style on page 3 must not meet a
  second meaning on page 20.
- The accent budget, and that it counts connectors as well as boxes.
- The element registry: canonical id and name for every recurring thing, so the same service is never drawn under
  two names. Anything not in the registry is drawn as an unnamed component.
- Set metadata per group: level, parent, subject. This is what lets the set be checked as a set in
  [09](09-set-review.md).
- Anything that stays deliberately small because the story does not depend on it.

**6. Voice.** Four or five lines only: plain sentences, the subject is the real thing, the verb is literal, the
subtitle states what the diagram shows and the one thing to notice, no em dashes, the banned word list, and the
content bans from [01](01-kickoff.md), such as no counts of X and no vendor names.

**7. Per-diagram specs.** One paragraph per diagram, in manifest order, each headed by number, title and type. Say
what goes on it, the illustrative values to use, what to mirror from another diagram, what to leave off, and the
focal element. Name the type reference to read first. Where a value is illustrative, say that it must be labelled
illustrative on the page.

Write the paragraphs so that two agents drawing adjacent diagrams produce pages that look like they were drawn by
one person.
