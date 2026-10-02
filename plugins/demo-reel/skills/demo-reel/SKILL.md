---
name: demo-reel
description: Produce a narrated demo video of working software, end to end. Use when someone wants a demo, walkthrough or screencast that shows a design document, the code that carries it and the system running; when a demo is built on a machine the author cannot see; when a demo needs a short and a long cut; or when a finished demo must be re-cut after the code or the narration changed. Owns the process and the artifacts; calls narrative-spine for the scene spine, writing-voice for the voiceover and diagram-design for any new figure.
license: MIT
---

# Demo reel

A demo filmed live fails in three ways before anyone watches it. It cannot be re-cut, so one changed
sentence means filming again. The choreography shows, because a person is clicking through four
windows at once. And numbers drift into the edit by hand, so the viewer sees a value the system never
produced.

This skill builds the video the other way round. A driver runs the scenario and logs every event. Each
pane on screen (the API calls, the workflow UI, the facts, the code and the build) is drawn from that
log or trimmed to it, and the cut is composed in code against the voiceover's word timings. A changed
sentence re-times the video, and no number appears that did not happen.

## The sequence

| Phase | Where | Reference | Produces | Gate |
|---|---|---|---|---|
| Kickoff | author | [01](references/01-kickoff.md) | a playback of the job | the owner has corrected it |
| Interview | author | [02](references/02-interview.md) | answers that shape every scene | no question left that would change a scene |
| Narrative | author | [03](references/03-narrative.md) | `demo/narrative.md` | the owner has approved it |
| Script | author | [04](references/04-script.md) | `demo/script.md` | voice lint clean, owner approved |
| Shot list | author | [05](references/05-shot-list.md) | `demo/shots.yaml` | `verify_shots.py` reports 0 problems |
| Pack | author | [06](references/06-pack.md) | `demo-kit.zip` | under the transfer limit; skipped on one machine |
| Reconcile | code | [07](references/07-reconcile.md) | code shots resolved, scenario checked, disagreements listed | the owner has ruled on each |
| Rig | code | [08](references/08-rig.md) | every tool installed | fixture render and toy proof pass |
| Driver | code | [09](references/09-driver.md) | the demo driver and reset script | two takes normalize identically |
| Capture | code | [10](references/10-capture.md) | one take per shot-list `take` | every shot's window fits |
| Voice | code | [11](references/11-voice.md) | narration per scene, `demo/timing.json` | the pronunciation check passes or failures are listed |
| Compose | code | [12](references/12-compose.md) | a draft render per cut | `build_props.py` reports 0 problems |
| Review | code | [13](references/13-review.md) | the checklist pass and the owner's notes applied | the owner signs off |
| Deliver | code | [14](references/14-deliver.md) | final MP4s, captions, thumbnails, a hand-back note | |

Load one reference when you enter its phase. Do not load them all. When the whole engagement runs on
one machine, skip Pack and keep going.

## Where you are

State lives on disk in the engagement's `demo/` folder, not in this skill. Read it before doing
anything:

1. The **ledger** at `demo/_brief/engagement.md` records the phase and what the owner approved.
   Format and rules in [ledger.md](references/ledger.md).
2. The **artifacts** say the rest. `narrative.md` exists or it does not. A take's events file exists
   or it does not. A cut's props file builds or it reports problems.

When the two disagree, the artifacts win and the ledger gets corrected. When there is no ledger,
offer to write one from what is on disk, then start at the earliest phase whose artifact is missing.

## The gates advise, they do not block

State the gate, say what is missing, and ask once. Then do what the owner says. A demo made on one
machine skips Pack, and a demo narrated by hand skips the narration engine. What is never skipped is
`build_props.py`, because it is the step that refuses a video the event log does not support.

Refusing to proceed is wrong. Proceeding silently past a missing gate is also wrong.

## Five rules that carry the work

1. **The voiceover is the clock.** Shots land on cues in the script, and cues land on words in the
   narration audio. Nothing is timed by hand.
2. **Every number on screen comes from a take's events.** Facts, outcomes, IDs, the terminal's lines
   and the timer are all read from `demo/takes/<take>/events.jsonl`.
3. **Honesty badges are computed, never typed.** Speed comes from the take's window and the shot's
   length, "stub" from the driver's stub events, "design" from the shot list's tag.
4. **The author side writes intent; the code side resolves it.** A code shot says what to find, and
   reconcile finds it. Disagreements between the kit and the code are listed and ruled on, never
   absorbed.
5. **The words are a separate pass.** The voiceover is written for the ear and linted with
   `writing-voice` before any narration is generated.

## Where the tools are

Inside this skill, referred to as `<skill>` in every reference:

| Folder | What it holds |
|---|---|
| `scripts/` | `verify_shots.py`, `cues.py`, `timing.py`, `build_props.py`, `normalize_events.py`, `captions.py`, `pack.py`, and their tests |
| `narration/` | `install.sh qwen` or `elevenlabs`, and `narrate.py`, which voices every scene with word timings |
| `templates/` | the capture `package.json`, the demo driver, the reset script, the browser recorder and the take runner |
| `remotion/` | the Remotion starter with five layouts, the tokenizer, and a fixture rendered through the pipeline |
| `examples/toy/` | a toy system and `prove.sh`, which proves the capture chain end to end |

## Delegating to agents

Every agent prompt this skill writes carries the kernel in [agent-kernel.md](references/agent-kernel.md).
Check a prompt against it before sending it.

## What never leaves the engagement

The narrative, script, shot list, takes, voice and renders belong to the owner's own repository, in
`demo/`. This skill ships generic, and its examples use neutral names. Client names, product names,
internal component names and private paths never enter a shared or public repository. Every agent
prompt that touches engagement material carries a confidentiality grep against the engagement's term
list, and its report must include a zero-matches line.
