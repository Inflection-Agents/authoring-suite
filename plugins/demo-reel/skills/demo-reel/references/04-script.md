# 04 Script

**Goal.** Write the voiceover, cue by cue, for the ear.
**Produces.** `demo/script.md`.
**Gate.** `writing-voice`'s linter is clean and every scene fits its time budget. The owner does not approve the script
separately: they hear it at the final watch.

## The format

```markdown
## L1 The promise
> direction lines start with ">" and are never voiced
A trip needs three bookings, and any one of them can fail. [cue:headline]
By the end of this video, we'll watch one fail and the others undo themselves. [cue:promise]
```

- **One `## <id> <title>` heading per scene**, ids exactly as in the narrative. A heading without a scene id is
  rejected by the shot-list check rather than merged into the scene before it.
- **`[cue:<id>]` immediately before the word the picture should change on.** The cue's time is the start of the first
  word after it; a cue at the end of a scene is the end of the last word. Cue ids are lowercase words joined by
  hyphens, unique within a scene.
- **Direction lines start with `>`.** They are never voiced, and cues inside them are ignored.
- **`> hold: 3s` on its own line, between sentences, inserts silence there** so the picture has time to land with no
  words over it. It also works at the end of a scene. The voice phase inserts the silence and moves every later word's
  timing, so the cues stay on their words.

## Writing for the ear

- **Sentences under 20 words.** The listener cannot re-read.
- **Numbers as they are spoken.** "Four thousand dollars", "zero point eight five".
- **One cue per change of picture.** More cues than pictures means the narration is describing the screen.
- **Budget at the voice's measured rate.** Rates differ by voice: a premade ElevenLabs voice spoke at about 210 words
  a minute, and a Qwen clone of a calm speaker at about 160. Voice one scene early, divide its words by its seconds,
  and read each scene's word count against its time budget in the narrative, plus its holds. A scene over budget
  is cut, not sped up; a cut well under its target is retargeted, not padded.
- **Every sentence ends with a full stop, question mark or exclamation mark.** Captions are built one per sentence.

## Checks

```bash
python3 <writing-voice skill>/scripts/verify-voice.py demo/script.md
python3 <skill>/scripts/cues.py demo/script.md /tmp/voice-check   # words per scene
```

## Leaving the phase

Record the script in the ledger under Decided by the agent, with each cut's word count, then write the shot list
([05](05-shot-list.md)) without stopping.
