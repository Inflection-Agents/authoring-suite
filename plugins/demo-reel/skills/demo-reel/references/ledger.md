# The engagement ledger

**Goal.** Let a fresh session, on either machine, pick up a demo that has run for days.
**Produces.** `demo/_brief/engagement.md`, in the owner's repository.
**Gate.** None. The ledger is a convenience, and a missing one is not a reason to stop.

Most of the state is already on disk: a narrative exists or it does not, a take's events file exists or it does not.
What the files cannot tell you is which artifacts the owner approved, and that is the whole content of this file.

## Format

```markdown
# Engagement: <subject> demo

phase: script
machine: author
kit: v1
cuts: short (about 4 minutes), long (about 10 minutes)

## Approved
- kickoff and interview   2026-10-02  two cuts; climax: the change made live
- narrative.md            2026-10-02  scenario, beats, scene tables

## Open
- the workflow UI's URL per invocation (reconcile)

## Decisions worth carrying
- the agent's approval is shown as an API call tagged "stub"
```

`phase` is one of: kickoff, interview, narrative, script, shots, pack, reconcile, rig, driver, capture, voice,
compose, review, deliver. `machine` is `author` or `code`. `kit` counts the kits sent, so a second kit is never
mistaken for the first.

## Rules

**The artifacts win.** When the ledger says `phase: compose` and there is no `timing.json`, the ledger is stale.
Correct it and say so; do not act on it.

**Only the owner's approval goes under Approved.** An artifact you wrote and nobody has read is not approved. Do not
write this line on the owner's behalf.

**Decisions worth carrying** holds rulings that would otherwise live only in a chat window: a renamed scene, a banned
word, a reconcile ruling. Anything here binds every later phase.

## Writing one for a demo already in flight

Read what is on disk, propose the ledger, and ask the owner to confirm the Approved list. Derive `phase` from the
earliest artifact that is missing, not from the most advanced one that exists.
