# 07 Reconcile

**Goal.** Resolve every piece of author-side intent against the real code and the running system.
**Produces.** Code tokens for every code shot, the scenario checked against a real run, the workflow UI's URL, and
`demo/_brief/reconcile.md`, a numbered list of disagreements.
**Gate.** Every disagreement has a ruling. The agent rules on each one, and sends to the owner only those that change
the story (see the four tests in the skill's "The owner stops the work four times").

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

Find the URL that shows one invocation (or run, or job) by its ID, and write it as `UI_ROUTE` with `{id}` in place of
the ID. The browser recorder in [10](10-capture.md) navigates there.

## The disagreements file

```markdown
# Reconcile

1. **The scenario's stay.** Kit says three nights; the hotel stub accepts at most two. Proposed: use two nights, which
   still shows the hold and its release.
```

Kit says, code says, the ruling, and who made it. Never pick a winner quietly: every ruling is written down.

## Ruling

Rule in this order, and take the first that works:

1. **Change the demo's setup, not the story.** A server setting, a seed, a driver step or a workflow key that makes the
   system do what the narrative says.
2. **Change the wording, not the claim.** "The same booking" becomes "another booking" when a workflow runs once per
   key; the claim that it fails the same way stands.
3. **Escalate.** When neither works, the story itself must change: a narrated claim, a scenario value or an honesty
   rule. Stop and put the disagreement to the owner with a proposed ruling.

Mark each ruling `agent` or `owner`, apply it to `narrative.md`, `script.md` and `shots.yaml`, and copy the agent's
rulings into the ledger under Decided by the agent.

## Leaving the phase

Re-run `verify_shots.py`, then rig the machine ([08](08-rig.md)) without stopping.
