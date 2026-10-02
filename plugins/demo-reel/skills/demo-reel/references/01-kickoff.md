# 01 Kickoff

**Goal.** Fix the frame for the demo before asking the owner a single question about the system.
**Produces.** The frame, recorded in the ledger at `demo/_brief/engagement.md` (see [ledger.md](ledger.md)):
what the demo shows, who watches it, which cuts, where each half runs, and how files move between them.
**Gate.** The owner has corrected the playback.

Nothing is written for the video in this phase. The phase ends when the owner has read back a description of their
own demo and fixed what is wrong in it.

## Collect the frame

Seven fields. The owner usually gives some in their first message. Ask for the rest in one numbered batch, and record
every answer in the ledger.

1. **Subject.** The working software the video shows, named as the owner names it.
2. **Source document.** The paper, design or proposal the demo proves, with its path. The video opens on its problem
   statement, so read it before the playback.
3. **Audience and cuts.** Who watches and what they should do afterwards. Default: two cuts from one set of recordings,
   a short one for leaders and a long one for engineers.
4. **Where each half runs.** The author half (phases 01 to 06) runs where the context is. The code half (07 to 14) runs
   next to the code. Name both machines, or say it is one machine.
5. **How files move.** Git, an emailed zip, a shared drive. This sets the kit's size limit in [06](06-pack.md).
6. **What the code machine can reach.** Open internet, internal mirrors only, or nothing. Every install in
   [08](08-rig.md) assumes package registries are reachable; say so early if they are not.
7. **Narration.** A local cloned voice (Qwen, Apple silicon), a cloud voice (ElevenLabs), or a human recording.

## Play the frame back before any question

Write the playback as one walkthrough of the finished video: what the viewer sees in the first twenty seconds, the
moment the system runs, and the closing shot. Close with the one assumption you are leaning on and "correct me if that
is wrong". A playback the owner accepts without a correction was usually too vague to disagree with, so write it
concrete enough to be wrong.

## Process rules for the engagement

Record these in the ledger. Agents in later phases inherit them without seeing this conversation.

1. **Interview before writing.** See [02](02-interview.md).
2. **The voiceover is the clock.** Nothing on screen is timed by hand.
3. **Every number on screen comes from a take's events.**
4. **Never invent a value, an endpoint or a name to fill a gap.** Mark it open and ask.
5. **Content bans.** Ask what must not appear on screen or in narration (names, figures, vendors) and record the list.

## Leaving the phase

The gate is the corrected playback, not a complete frame. Where a field is still open, say which one and ask once,
then start the interview with it.
