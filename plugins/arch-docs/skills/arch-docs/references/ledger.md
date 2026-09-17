# The engagement ledger

**Goal.** Let a fresh session pick up an engagement that has run for days across several contexts.
**Produces.** `<set>/_brief/engagement.md`, in the owner's repository.
**Gate.** None. The ledger is a convenience, and a missing one is not a reason to stop.

Most of the state is already on disk. The facts file exists or it does not. The manifest lists 29 diagrams or 41.
The pages are built or they are not. What the files cannot tell you is which artifacts the owner approved, and that
is the whole content of this file.

## Format

```markdown
# Engagement: <client or system> <deliverable>

phase: brief
audience: <who reads this, and where>
skin: <brand>

## Approved
- facts.md          2026-09-15  interview plus six reconciled disagreements
- diagram list      2026-09-15  29 diagrams in 6 layers

## Open
- mid-flight update semantics, deferred, the platform owner decides
- whether the partner API is in scope, still to decide

## Decisions worth carrying
- stage means the orchestrator's grouping; phase belongs to the task lifecycle
- the term "durable promise" is banned set-wide, use "workflow promise"
```

`phase` is one of: kickoff, interview, reconcile, facts, plan, brief, build, refine, voice, deliver.

## Rules

**The artifacts win.** When the ledger says `phase: build` and there is no manifest, the ledger is stale. Correct it
and say so; do not act on it.

**Only the owner's approval goes under Approved.** An artifact you wrote and nobody has read is not approved. This
line is the one that protects the gates, so do not write it on the owner's behalf.

**Open items here match the open items in the facts file.** The facts file is the source of truth for what gets
drawn; this list is the reminder that they are still open. When one closes, close it in both.

**Decisions worth carrying** holds rulings that would otherwise live only in a chat window: a renamed concept, a
banned term, a convention the owner set mid-set. Anything here is binding on every later page.

## Writing one for an engagement already in flight

Read what is on disk, then propose the ledger and ask the owner to confirm the Approved list. Derive `phase` from
the earliest artifact that is missing, not from the most advanced one that exists, because a set with pages and no
brief is at the brief phase and the pages need checking against it.
