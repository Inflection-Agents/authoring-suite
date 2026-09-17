# 01 Kickoff

**Goal.** Fix the frame for the set before asking the owner a single question about the system.
**Produces.** The frame, recorded in the ledger at `<set>/_brief/engagement.md` (see [ledger.md](ledger.md)):
audience, deliverable, the problem the set has to make visible, the sources on hand, and the process rules for this
engagement.
**Gate.** The owner has corrected the playback.

Nothing is drawn in this phase and no diagram is proposed. The phase ends when the owner has read back a description
of their own system and fixed what is wrong in it.

## Collect the frame

Six fields. The owner usually gives some of them in their first message. Ask for the rest in one numbered batch, and
record every answer in the ledger.

1. **System.** What is being documented, named as the owner names it: `<SYSTEM OR CLIENT>`.
2. **Deliverable.** A set of C4 diagrams built with the `/diagram-design:diagram-design` skill, read `<in a deck / as
   a standalone page set / in a proposal>`.
3. **Audience.** `<executives, engineering leadership, product managers>`. The audience decides the depth of every
   layer, so get the roles, not a category.
4. **Scope.** One or two sentences. Where there are two architectures, name both, the system as it is today and the
   system the owner proposes to build. Two architectures means two facts files and a stated contrast.
5. **Sources.** `<source code, prior design documents, an existing analysis, nothing but the owner's own head>`, with
   `<paths>`. Any source beyond the interview sends the engagement through [03](03-source-reconciliation.md) before
   the facts file.
6. **The problem the set has to make visible.** The one thing the reader must understand by the end. For example:
   the system is configuration driven and the configuration is split between a central service and each service's
   own files, which is why nothing can be tested in isolation. This sentence is what [05](05-diagram-list.md) checks
   the diagram order against.

## Play the frame back before any question

Play back what you understood before you ask anything else. Write it as two numbered walkthroughs:

1. One unit of work moving through the system end to end.
2. One change moving through the system end to end.

Close with the single assumption you are leaning on and the sentence "correct me if that is wrong". One assumption,
not a list. Naming the assumption you would bet on is what makes the owner correct it.

The owner corrects the playback before the interview starts. A playback they accept without a correction usually
means it was too vague to disagree with, so write it concrete enough to be wrong.

## Process rules for the engagement

These hold for every later phase. Record them in the ledger, because a build agent in [07](07-build-agents.md)
inherits them without seeing this conversation.

1. **Interview the owner first.** Ask in numbered batches so they can answer inline. Keep asking until you can name
   every container, every integration and every piece of vocabulary without guessing. See [02](02-interview.md).
2. **Name the diagrams before generating any.** One paragraph each, and the owner cuts and adds. See
   [05](05-diagram-list.md).
3. **Draft wide.** Start with more detail than the audience needs, then prune. Assume the first pass has roughly
   double the diagrams the final set will have.
4. **Structure the set as layers** that peel from high level to deep detail, so a reader can stop at any depth and
   still hold a complete picture at that depth.
5. **Suspend the box-count limits for this set.** Every other rule of the diagram skill applies, including the
   connector rules and the accent budget.
6. **Brand skin.** Use the `<CLIENT>` brand skin, or pull the skin from `<URL>`, or use the default. Settle this in
   kickoff so no page is redrawn for it later.
7. **Never invent a number, a threshold, a vendor or a name to fill a gap.** An open question is drawn as open,
   dashed and labelled "to decide", or it is left out and listed for the owner.

## Content bans

Ask the owner what must not appear on any page, and write the answer into the ledger as a list. Typical bans:

```
Do not put any of these on any page:
- counts of services
- counts of configuration keys
- test-cycle times
- model or vendor names
```

The bans are inherited by every later phase. [06](06-build-brief.md) copies them into the brief's voice section, and
every build agent reads them there.

## Leaving the phase

The gate is the corrected playback, not a complete frame. Where a field is still open, say which one and ask once,
then start the interview with the open field as its first question.
