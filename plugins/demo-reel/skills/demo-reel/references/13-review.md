# 13 Review

**Goal.** Catch what the checks cannot and fix it, show the owner the cuts once, then apply the owner's notes.
**Produces.** A checked draft per cut and the owner's notes, applied and re-rendered.
**Gate.** The owner signs off. The sign-off covers publishing too, so [14](14-deliver.md) needs no second ask.

## The checklist

Watch each draft in full, then check:

1. **Every cut follows a sentence.** A picture change with no sentence behind it gets cut or given a cue.
2. **Legibility.** No text under 22 pixels at 1080p. Code shots fit their pane without wrapping.
3. **Badges.** Every speed-up shows its factor, every stubbed dependency shows "stub", every unbuilt part shows
   "design".
4. **Numbers.** Every number on screen can be traced to a line in a take's events.
5. **The timer** stops at its real total and holds there.
6. **Runtime.** Each cut is within 10% of its target.
7. **Honesty of the climax.** What the narration claims happened is what the events show happened.

Fix every failed item, re-render, and check again before the owner sees anything. Look at frames from the middle and
the end of every shot, because a pane that empties at a cut inside one take, or a line edited too early, shows there.

## The final watch

Show the owner each cut with its length against target, then the ledger's Decided by the agent list, then anything
the checklist could not settle. Ask for notes or a sign-off in one message.

## The owner's notes

Apply each note with the least re-work. Re-run what the change requires:

| Change | Re-run |
|---|---|
| A narration line | voice that scene, `timing.py`, `build_props.py`, render |
| A cue moved within a scene | `timing.py`, `build_props.py`, render |
| A shot's layout, slot, `in` or `out` | `build_props.py`, render |
| The scenario or the driver | every take that uses it, then `build_props.py`, render |
| Code shown on screen | the tokens for that file, render |
| The workflow UI | every take with a browser slot |

## Leaving the phase

Record the sign-off in the ledger, then deliver ([14](14-deliver.md)).
