# demo-reel

`demo-reel` produces a narrated demo video of working software in two cuts from one set of
recordings: a short one for leaders and a long one for engineers. It opens on the problem the work
solves, shows the code that carries the design, and runs the system on camera. Every pane is driven
by the scenario's own event log, so the video can be re-cut after any change, and it never shows a
number that did not happen.

## Two halves

The interview, narrative, voiceover script and shot list (phases 01 to 06) are written where the
context is, usually beside the design document. Capture, narration and composition (phases 07 to 14)
run next to the code. A kit zip carries the first half to the second. When everything runs on one
machine, the pack phase is skipped.

## Install

```
/plugin marketplace add Inflection-Agents/authoring-suite
/plugin install demo-reel@authoring-suite
```

## Prerequisites next to the code

Node 22, Python 3.11 or later, `uv`, and ffmpeg. The rig phase installs Playwright's browser. A
narration engine is optional: `narration/install.sh qwen` installs a local cloned voice (Qwen3-TTS,
Apple silicon), and `narration/install.sh elevenlabs` checks an ElevenLabs key kept in
`~/.config/demo-reel/elevenlabs.env`. Narration recorded by hand needs neither.

## Phases

| Phase | Where | Produces | Gate |
|---|---|---|---|
| 01 Kickoff | author | playback of the job: subject, audience, cuts, machines | owner corrects the playback |
| 02 Interview | author | answers from a question bank | nothing left that would change a scene |
| 03 Narrative | author | `narrative.md`: promise, scenario, scene table per cut | owner approves |
| 04 Script | author | `script.md`: voiceover with `[cue:...]` markers | voice lint clean, scenes inside budget |
| 05 Shot list | author | `shots.yaml`: scenes per cut, shots per cue | `verify_shots.py` reports 0 problems |
| 06 Pack | author | `demo-kit.zip`, size-checked; skipped on one machine | under the transfer limit |
| 07 Reconcile | code | code shots resolved to tokens, scenario checked against a real run, numbered disagreements | each ruled; a story change goes to the owner |
| 08 Rig | code | every tool installed and proven by the fixture render and the toy take | all green |
| 09 Driver | code | demo driver, reset script, one events file per take | two takes normalize identically |
| 10 Capture | code | one take per shot-list `take`, with events and a browser recording | every shot's window fits |
| 11 Voice | code | narration per scene, `timing.json` | QC passes or failures are listed |
| 12 Compose | code | `props-<cut>.json`, a draft render per cut | builds with 0 problems, renders |
| 13 Review | code | checklist pass, owner notes applied | owner signs off once, for review and publishing |
| 14 Deliver | code | final MP4s, captions, thumbnails, a hand-back note | |

## Four owner stops

The owner stops the work at the kickoff, the interview, the narrative and the final watch. After the narrative,
`/demo-reel:produce` runs the script through review without asking, and stops early only when a decision would change
the story: a narrated claim, a scenario value, an honesty rule, or a check that keeps failing. Every other decision
goes into the ledger for the owner to read at the final watch.

## What lives where

The skill holds the process, the scripts, the narration engines, the capture templates, a toy system
and the Remotion starter. The engagement's `demo/` folder, in the owner's own repository, holds
everything specific to one demo: the narrative, script, shot list, takes, voice and renders.
