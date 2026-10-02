# demo-reel design

Date: 2026-10-02
Status: approved sections 1-3; revised to v2 the same day after four adversarial reviews (PR #12)

## Problem

A demo video of working software has to show a paper's idea, the code that carries it, and the
system running, often with several surfaces on screen at once: API calls, a workflow engine's UI,
logs, and the facts a run produces. Filmed live, that choreography looks complicated and cannot be
re-cut. The owner wants it to look simple, and wants a process that a coding agent can drive to
completion on a machine the author may never see.

## Decision log

- Audience: two cuts from one set of recordings (choice D). A short cut for leadership, a long cut
  for engineers. Recordings are shared between cuts; narration is not. A scene the short cut needs
  shorter is a separate scene with its own narration that reuses the same takes.
- Climax: one payoff beat, with up to two supporting beats and an optional extra in the long cut.
- Code on screen: only the code that carries the design. The short cut shows only code that is also
  configuration.
- Voice: pluggable narration engine: a local cloned voice, a cloud voice or a human recording.
- Machines: the interview, narrative, script and shot list are written where the context is, and
  capture, narration and composition run next to the code. A kit zip carries one half to the other.
  When the whole engagement runs on one machine, including draft review, the pack step is skipped and
  later author-side edits happen in place.
- Build approach: everything composed in code (approach 1), borrowing proven patterns from the
  open-source `claude-code-video-toolkit` without forking it. Live recording from a runbook survives
  only as a per-shot fallback (`capture: manual`).
- v2, owner ruling: the terminal pane is drawn from the event log, not recorded. The driver also runs
  the live edit, the build and the re-run, so the editor pane is drawn from events too. A browser
  recording of the workflow UI is the only surface captured as video. VHS leaves the toolchain.
- v2, owner ruling: the climax timer runs between two marks the driver logs, `timer-start` just before
  the edit and `timer-stop` when the re-run's outcome arrives. It can never show time that did not pass.
- v2: the shot list stays YAML for readability, so the engagement-time scripts use PyYAML. The
  repository's gates stay standard-library only; the unit tests do not import YAML.
- Plugin name: `demo-reel`.

## Section 1: Narrative

The narrative is engagement-specific and lives in the engagement's own folder, not in this plugin.
The plugin encodes its shape:

- **The hook is a promise.** Open on the problem the work solves and promise to fix it on camera.
  Every scene earns the promise; the climax keeps it with real evidence on screen, such as a timer.
- **One scenario, used in every run.** A fixed input whose output flips on a one-value change, so
  the climax is concrete. The target machine verifies the numbers against a real run.
- **Scene tables per cut,** each row with a time range, the scene's spine sentence, what is on
  screen, and what the narration says. Scene titles read top to bottom as the argument
  (`narrative-spine`).
- **Honesty rules,** enforced in code where possible: every speed-up shows its factor (computed, never
  typed); every stubbed dependency the driver declares shows a "stub" badge; anything not built is
  labelled "design"; every number on screen comes from a take's event log; the timer shows only real
  elapsed time between its marks.

## Section 2: The plugin

`demo-reel` has the same shape as `arch-docs`. It has one skill with a reference per phase, a command
per phase, a ledger at `demo/_brief/engagement.md`, and gates that advise rather than block. Its
runtime files live inside the skill (`skills/demo-reel/scripts`, `remotion`, `templates`,
`examples`), as every other plugin's do. It delegates: `narrative-spine` for the scene spine,
`writing-voice` for the voiceover script and its lint, `diagram-design` for any new figure.

| Phase | Where | Produces | Gate |
|---|---|---|---|
| 01 Kickoff | author | playback of the job: subject, audience, cuts, machines | owner corrects the playback |
| 02 Interview | author | answers from a question bank | nothing left that would change a scene |
| 03 Narrative | author | `narrative.md`: promise, scenario, scene table per cut | owner approves |
| 04 Script | author | `script.md`: voiceover with `[cue:...]` markers | voice lint clean, owner approves |
| 05 Shot list | author | `shots.yaml`: scenes per cut, shots per cue | `verify_shots.py` reports 0 problems |
| 06 Pack | author | `demo-kit.zip`, size-checked; skipped on one machine | under the transfer limit |
| 07 Reconcile | target | code shots resolved to tokens files, scenario checked against a real run, UI route found, numbered disagreements | owner rules on each |
| 08 Rig | target | every tool installed and proven by the fixture render and the toy take | all green |
| 09 Driver | target | demo driver, reset script, one events file per take | two takes normalize identically |
| 10 Capture | target | one take per shot-list `take`, each with its events and browser recording | every take present, every shot's window fits |
| 11 Voice | target | narration per scene, `timing.json` with cue and sentence times | QC passes or failures are listed |
| 12 Compose | target | `props-<cut>.json` from `build_props.py`, a draft render per cut | builds with 0 problems, renders |
| 13 Review | target | checklist pass, then owner notes, applied and re-rendered | owner signs off |
| 14 Deliver | target | final MP4s, SRT captions, a thumbnail per cut, a hand-back note | |

**Shipped inside the skill:**

- A Remotion starter with five layouts: `title`, `figure`, `code` (focus and dim, error callout,
  edits retyped on the take's clock), `three-pane` (terminal drawn from events, browser recording in a
  fixed 820 by 1000 slot, facts panel, optional log strip drawn from events), and `editor-build`
  (code pane with the live edit, build and re-run output drawn from events, the timer). Badges come
  from computed speed, driver stub events and the `design` tag.
- Templates: a capture `package.json` (ES module, pinned `tsx` and `playwright`), the driver with
  helpers for calls, commands, edits, marks, stubs, facts and outcomes, a per-take reset script, the
  browser recorder, and a take runner.
- A toy system (`examples/toy/`) that the rig phase and CI use to prove the whole capture chain.
- The agent kernel from `arch-docs` plus one rule, and a `failure-modes.md` that grows per engagement.

**Kept out:** anything specific to a client or a stack. A workflow engine's UI is one browser source
among others. Example names in the plugin are neutral (`orders`, `orderTotal`, `payment-gateway`).

## Section 3: Data flow, failure handling, testing

**Four files carry the pipeline.**

- `shots.yaml`: scenes (with their cuts and estimated durations) and shots (each on one cue). A shot
  that shows a recording names its `take`, and optionally `in` and `out` marks (default
  `capture-start` and `capture-end`) and a `speed`. A code slot carries `find` on the author side;
  reconcile fills `tokens`.
- `demo/takes/<take>/events.jsonl`: one file per take. The driver writes `t` (seconds since it
  started) and `wall` (Unix seconds) on every event: `capture-start`, `capture-end`, `request`,
  `response`, `command`, `edit`, `invocation`, `fact`, `outcome`, `stub`, `mark`. The browser recorder
  adds `recording-start` with `wall` only.
- `timing.json`: per scene, the audio's duration, each cue's second, and each sentence's start.
- `props-<cut>.json`: built by `build_props.py`, read by Remotion. Nothing else feeds the render.

**The clocks.** A shot shows its take's window between `in` and `out`. Its speed is the window's
length over the shot's length, rounded up to one decimal and never below 1; a speed given in the shot
list that is too low to fit the window is an error. Every event lands at `(t - in) / speed` seconds
into the shot. The browser recording is trimmed by the gap between its `recording-start` and the
window's start, converted to driver time through `capture-start`, so every pane shows the same moment.

**What re-times and what does not.**

| Change | Re-run |
|---|---|
| A narration line | voice that scene, `timing.py`, `build_props.py`, render |
| A cue moved within a scene | `timing.py`, `build_props.py`, render |
| A shot's layout, slot or `in`/`out` | `build_props.py`, render |
| The scenario or the driver | every take that uses it, then `build_props.py`, render |
| Code shown on screen | reconcile's tokens for that file, render |
| The workflow UI | every take with a browser slot |

**Failure handling.** Every check reports all problems at once and writes nothing on failure.

- `verify_shots.py` rejects headings without a scene id, malformed or duplicate cue ids, cues
  without shots, shots on cues the script lacks, scenes without shots or script sections, unknown
  cuts and scenes, non-positive speeds, and estimated runtimes more than 10% off target.
- `build_props.py` rejects missing takes, missing marks, windows that cannot fit at the given speed,
  browser slots without a `recording-start`, timers without both marks, cues missing from the timing,
  and two shots on one frame. It warns when a cut's real runtime is more than 10% off target.
- The driver gate: two takes of the same scenario, run through `normalize_events.py`, must be
  identical. It drops times and take names, and replaces every invocation ID wherever it appears.
- `pack.py` skips symbolic links, junk folders and earlier zips, and writes nothing when over the limit.
- A surface that cannot be scripted is marked `capture: manual` and gets a runbook entry.

**Testing.**

- Unit tests for every script: 49 tests over the shot check, cue timing, the props builder, the
  packer, event normalization and captions.
- A fixture rendered through the real pipeline (`verify_shots`, `build_props`, render) to 10 seconds
  of 1080p video with audio. It is the rig phase's smoke test and a CI job.
- The toy system: two real takes with the browser recorder, the determinism gate, and a three-pane
  render, run in the rig phase and in CI.
- `scripts/verify-skill-frontmatter.py` (via the existing `skills-frontmatter` workflow) covers the skill.
