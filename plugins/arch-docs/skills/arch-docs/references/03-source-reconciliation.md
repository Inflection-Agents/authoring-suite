# 03 Reconcile

**Goal.** Surface every place the source disagrees with the owner's interview answers, as a numbered list the owner
can close one line at a time.
**Produces.** A closed list of disagreements, plus two supporting lists and a dead-vocabulary list. The rulings
become the top section of `_brief/facts.md` in [04](04-facts-file.md).
**Gate.** The owner has ruled on every one.

Enter this phase when the engagement has source code, an existing analysis, or older design documents alongside the
interview from [02](02-interview.md). A small engagement with only the interview skips straight to
[04](04-facts-file.md).

The expensive failure is not a wrong diagram. It is a diagram that quietly splits the difference between what the
owner said and what the code does, and then gets shown to a room that knows the code.

## Open with the epistemics

State the epistemics in one sentence before the list, so the owner knows which way to lean. For example: the
analysis came from reading the source in July, nothing was run, so the owner's knowledge of the running system
overrules it. Then say whether "take your recommendations" closes the whole list, so the owner knows whether one
reply is enough.

## The conflict template

Read the source, compare it against the interview answers, and produce a numbered list of every place they disagree.
Use these four fields every time, so the owner can answer with one word per number.

```
**N. <the disputed thing>**
- **You said:** <the owner's version, one sentence>
- **The source says:** <the evidence, with file, counts and identifiers>
- **Diagram impact:** <which diagram changes and how it changes>
- **Recommendation:** <a default the owner can accept by saying "take recommendation">
```

The impact field is the one that earns its keep. "In the configuration publish flow, the event arrows are either
solid, meaning consumed, or dashed and labelled published but not consumed" tells the owner what their answer buys.
Where an answer changes nothing a reader would see, drop the item.

Where a conflict exposes something the owner may not want in a client deck, say so explicitly and hand them the
call.

Then stop. Do not write the facts file and do not draw anything until the owner has answered every item. They
respond with one line per number, and their answer wins even when the source disagrees, because they may be
describing where the system is going or something the code cannot show.

## Two more lists, and the dead terms

Separately from the numbered conflicts:

- **Containers the owner never mentioned** that the source shows and a reader would expect to see, with what each one
  does.
- **Risks the source raises that the owner's description does not cover**, each with a line saying whether it could
  become a note or its own diagram.
- **Anything in the older documents that is now out of date.** Name it so it never leaks back in. The owner confirms
  which terms are dead, and the dead terms go into the header of the facts file.

## Already settled is closed

A conflict the owner's earlier answers already settled is closed, not re-argued. Say "your last answer confirmed
this, so it is closed" and move to the detail that remains.

## Close-out into the facts file

The owner's rulings go into `_brief/facts.md` as a top section headed "Decisions that override everything below",
one numbered bullet each, with the reason the source got it wrong where that is known. The file header states the
precedence: the owner's interview, marked as theirs; the source, marked with its section codes; and where they
disagreed, the owner's ruling wins.

Where an older document has useful supporting detail, it can be used later, but only where it agrees with the
owner's answers, and every such claim gets marked as coming from that document.

## Handing the source read to an agent

Where the source is large enough that reading it would fill this session, send a read-only agent. The prompt below
carries the ten points the skill root requires of every agent prompt. Fill the angle brackets and send it as is.

```
Mode: read-only. You change no file in the source repository and no file in the diagram set.

Working directory: <ABSOLUTE PATH TO THE SOURCE REPO>
Repo and branch: <REPO> on <BRANCH>, at <COMMIT OR TAG>.

Read these first, in order:
1. <ABSOLUTE PATH TO THE OWNER'S ANSWERS>        what the source is being compared to; when the answers live only
                                                 in a conversation, paste them into this prompt instead
2. <ABSOLUTE PATH TO THE PRIOR ANALYSIS>         a prior read of the same source, itself unverified
3. <ABSOLUTE PATH TO THE OLDER DESIGN DOCS>      may contain terms that are now dead

Source of truth: the owner's interview answers. Where the source disagrees with them, the disagreement is reported,
never resolved. Override order: the owner's ruling, then the interview answers, then the running source, then the
prior analysis, then the older design documents.

You own: <ABSOLUTE PATH>/_brief/reconciliation-draft.md, and nothing else. You edit no file in the source repo. The
agents working concurrently with you are <NAMES>, and they own <THEIR FILES>.

Loop, per area of the system:
  rg -n "<TERM>" <PATHS>
  <TEST OR BUILD COMMAND THAT SHOWS WHAT ACTUALLY RUNS>
  write one numbered item into reconciliation-draft.md using the four-field template above

Done when: every area in the interview answers has been checked against the source, and every item in the draft has
all four fields filled, including a diagram impact that names a diagram.

Never invent a number, a threshold, a vendor or a name that the source does not show. Where the source is silent,
write "the source is silent on this" rather than inferring.

Voice: plain sentences, the subject is the real thing, the verb is literal, no em dashes.

Report back, capped at 40 lines: the count of conflicts found, the three with the largest diagram impact, every
place you could not read the source or could not tell what runs, and anything in the source that contradicts the
prior analysis.
```

A prompt that names a client or a private path stays in the owner's own repository. Before any of this reaches a
shared repository, grep for the client name and the internal component names and report a zero-matches line.
