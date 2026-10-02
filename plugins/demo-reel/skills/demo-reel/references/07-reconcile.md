# 07 Reconcile

**Goal.** Resolve every piece of author-side intent against the real code and the running system.
**Produces.** Code tokens for every code shot, the scenario checked against a real run, the workflow UI's URL, and
`demo/_brief/reconcile.md`, a numbered list of disagreements.
**Gate.** The owner has ruled on every disagreement.

## Code shots

For every slot with `find`, find the file and the line range that carries the intent, then:

```bash
node <skill>/remotion/scripts/tokenize.mjs <file> <lang> <first> <last> demo/remotion/public/code/<shot>.json
```

and set the slot's `tokens: code/<shot>.json`. Keep the range short enough to read at 1080p: about 25 lines. When the
intent spans more, split the shot or choose the part that proves the point.

## The scenario

Run the scenario once by hand against the real system and compare every value in the narrative's scenario table: the
inputs, the outputs, and the one value the climax changes. A value that differs is a disagreement, not a correction.

## The workflow UI

Find the URL that shows one invocation (or run, or order) by its ID, and write it as `UI_ROUTE` with `{id}` in place of
the ID. The browser recorder in [10](10-capture.md) navigates there.

## The disagreements file

```markdown
# Reconcile

1. **The scenario's floor.** Kit says 0.75; the rule's default is 0.8. Proposed: use 0.8 and change the climax to 0.9,
   which still flips the outcome.
```

Kit says, code says, proposed ruling. Never pick a winner quietly; stop for the owner.

## Leaving the phase

Record the rulings in the ledger, apply them to `narrative.md`, `script.md` and `shots.yaml`, and re-run
`verify_shots.py`. Then rig the machine ([08](08-rig.md)).
