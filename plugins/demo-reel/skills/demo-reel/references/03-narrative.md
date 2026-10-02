# 03 Narrative

**Goal.** Write the story both cuts tell, scene by scene, before a word of voiceover exists.
**Produces.** `demo/narrative.md`.
**Gate.** The owner has approved it.

## The format

`narrative.md` has these sections, in this order:

1. **The job.** A table: subject, cuts with target lengths, the code machine, the narration engine, how files travel.
2. **What is live.** The parts of the source document that run, and the parts shown only as figures labelled "design".
3. **The promise.** The video opens on the problem the work solves and promises to fix it on camera. Every scene earns
   the promise, and the climax keeps it with real evidence on screen.
4. **The beats.** The climax and its supporting beats, each with its role and what happens on screen.
5. **The scenario.** A table of the fixed input and the value the climax changes, with a line saying what must be
   verified next to the code in [07](07-reconcile.md).
6. **Code on screen.** A table of the code items, what each proves, and which cut shows it.
7. **One scene table per cut.** Columns: id, time range, scene title, on screen, what the narration says.
8. **Honesty rules.** Speed factors shown, stubs tagged, unbuilt parts labelled "design", every number from a take's
   events, the timer bounded by its marks.

## Rules

- **Scene titles read top to bottom as the argument.** Run `narrative-spine`'s title check over each cut's titles.
- **Every short-cut scene also appears in the long cut**, or has a long-cut scene that reuses the same takes.
- **One scenario for every run.** The numbers that appear on screen are the scenario's numbers.
- **Scene ids are letters then digits** (`L1`, `E12`), because the script and the shot list key on them.

## Leaving the phase

Record the approval in the ledger with its date, then write the script ([04](04-script.md)).
