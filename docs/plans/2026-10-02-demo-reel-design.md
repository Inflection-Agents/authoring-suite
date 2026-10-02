# demo-reel design

Date: 2026-10-02
Status: approved sections 1-3

## Problem

A demo video of working software has to show a paper's idea, the code that carries it, and the
system running, often with several surfaces on screen at once: API calls, a workflow engine's UI,
logs, and the facts a run produces. Filmed live, that choreography looks complicated and cannot be
re-cut. The owner wants it to look simple, and wants a process that a coding agent can drive to
completion on a machine the author may never see.

## Decision log

- Audience: two cuts from one set of recordings (choice D). A short cut for leadership, a long cut
  for engineers. Every short-cut shot is also a long-cut shot; the long cut only adds depth.
- Climax: one payoff beat, with up to two supporting beats and an optional extra in the long cut.
- Code on screen: only the code that carries the design. The short cut shows only code that is also
  configuration.
- Voice: pluggable narration engine. The first engagement uses the owner's cloned voice through
  `voice-lab`, generated on the target machine (choice B).
- Two machines: the author machine holds the context; the target machine holds the code. The
  author-side kit travels as a zip. Client material never enters this repository.
- Target machine has open internet (choice A): every tool installs normally.
- Build approach: everything composed in code (approach 1), borrowing proven patterns from the
  open-source `claude-code-video-toolkit` without forking it. Live recording from a runbook survives
  only as a per-shot fallback (`capture: manual`).
- Plugin name: `demo-reel`.

## Section 1: Narrative (approved)

The narrative is engagement-specific and lives in the engagement's own kit, not in this plugin. The
plugin encodes its shape:

- **The hook is a promise.** Open on the problem the work solves and promise to fix it on camera.
  Every scene earns the promise; the climax keeps it with real evidence on screen, such as a timer.
- **One scenario, used in every run.** A fixed input whose output flips on a one-value change, so
  the climax is concrete. The target machine verifies the numbers against a real run.
- **Scene tables per cut,** each row with a time range, the scene's spine sentence, what is on
  screen, and what the narration says. Scene titles read top to bottom as the argument
  (`narrative-spine`).
- **Honesty rules,** enforced by the shot list and the review checklist: every speed-up shows its
  factor, every stubbed dependency carries a "stub" tag, anything not built is labelled "design",
  and every number on screen comes from the demo driver's event log.

## Section 2: The plugin (approved)

`demo-reel` has the same shape as `arch-docs`. It has one skill with a reference per phase, a command
per phase, a ledger on disk, and gates that advise rather than block. It delegates: `narrative-spine` for the
scene spine, `writing-voice` for the voiceover script and its lint, `diagram-design` for any new
figure.

| Phase | Machine | Produces | Gate |
|---|---|---|---|
| 01 Kickoff | author | playback of the job: subject, audience, cuts, constraints | owner corrects the playback |
| 02 Interview | author | answers from a question bank: audience and cuts, what is live, climax, code items, scenario, voice, honesty rules | nothing left that would change a scene |
| 03 Narrative | author | `narrative.md`: promise, scenario, scene table per cut | owner approves |
| 04 Script | author | `script.md`: voiceover with `[cue:...]` markers | voice lint clean, owner approves |
| 05 Shot list | author | `shots.yaml`: per shot the cuts, layout, sources, cues, tags. Code shots carry intent, not location | every scene has shots, every cue has a shot |
| 06 Pack | author | `kit.zip`, size-checked | under the transfer limit |
| 07 Reconcile | target | code shots resolved to file and lines, scenario checked against a real run, numbered disagreements | owner rules on each |
| 08 Rig | target | every tool installed and proven by a smoke render | all green |
| 09 Driver | target | demo driver and reset script; each run writes `events.jsonl` | two consecutive runs give the same events, apart from times and IDs |
| 10 Capture | target | one agent per surface: browser, terminal, code scenes, figures, editor | each asset plays and matches its shot |
| 11 Voice | target | narration per scene, word timestamps into `timing.json` | QC passes or failures are listed |
| 12 Compose | target | a Remotion composition per cut, draft render | it renders |
| 13 Review | target | checklist pass (pacing, legibility at 1080p, honesty tags, every cut tied to a sentence), then owner notes | owner signs off |
| 14 Deliver | target | final MP4s, SRT captions, a thumbnail per cut | |

The ledger travels in the kit, so the target machine starts at phase 07.

**Shipped inside the plugin,** so each engagement does not rebuild the machinery:

- A Remotion starter project with five layouts: full-screen figure; code pane (focus and dim,
  magic-move between versions, error callouts); three-pane run (terminal, browser, facts panel,
  optional log strip); editor beside terminal with a timer; title card. Plus badges for speed
  factor, "stub" and "design".
- Templates: a demo-driver skeleton writing `events.jsonl`; a VHS tape generator reading events; a
  Playwright capture script that opens a workflow UI at an ID from the events; a timing script that
  maps narration audio to cue timestamps.
- The agent kernel from `arch-docs`, and a `failure-modes.md` that grows per engagement.

**Kept out:** anything specific to a client or a stack. A workflow engine's UI is one browser
source among others. The narration engine sits behind an interface with three implementations
named: a local cloned voice, a cloud voice, a human recording.

## Section 3: Data flow, failure handling, testing (approved)

**Three files carry the pipeline.**

- `shots.yaml`, written on the author machine and completed on the target. A code shot carries
  `find` (intent) on the author side; reconcile fills `file` and `lines`.
- `events.jsonl`, written by the demo driver on every run: one line per event with time, kind, run,
  invocation ID, step and payload. Every recorder and every on-screen panel reads it.
- `timing.json`, from the voice phase: each `[cue:...]` marker mapped to a second in the audio. The
  composition places each shot at its cue, so editing a narration line re-times the video.

**Failure handling.**

- A surface that cannot be scripted is marked `capture: manual` and gets a runbook entry.
- Kit and code disagree: reconcile lists the disagreements, numbered; the owner rules on each.
- A non-repeatable run fails the driver gate; the reset script restores a clean state before each
  take.
- Voice QC failures are listed with the failing word; a lexicon entry fixes the pronunciation.
- An oversized kit: pack lists the largest files and proposes compression before zipping.

**Testing.**

- `verify-shots.py`: every script cue has a shot, every shot has a scene and a cut, each cut's
  runtime is within 10% of its target, every stub source carries a `stub` tag.
- A fixture demo in the plugin (fake events, short timing, two shots) that the Remotion starter must
  render to a 5-second MP4. It is also the rig phase's smoke test and can run in CI.
- `scripts/verify-skill-frontmatter.py` covers the new skill.
