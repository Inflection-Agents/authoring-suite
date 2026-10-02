# 04 Script

**Goal.** Write the voiceover, cue by cue, for the ear.
**Produces.** `demo/script.md`.
**Gate.** `writing-voice`'s linter is clean and the owner has approved the script.

## The format

```markdown
## L1 The promise
> direction lines start with ">" and are never voiced
A change that takes five minutes to make takes a week to ship. [cue:headline]
By the end of this video, we'll make that change on camera. [cue:promise]
```

- **One `## <id> <title>` heading per scene**, ids exactly as in the narrative. A heading without a scene id is
  rejected by the shot-list check rather than merged into the scene before it.
- **`[cue:<id>]` after the words a picture change lands on.** Cue ids are lowercase words joined by hyphens, unique
  within a scene. The cue's time is the start of the first word after it; a cue at the end of a scene is the end of
  the last word.
- **Direction lines start with `>`.** They are never voiced, and cues inside them are ignored.

## Writing for the ear

- **Sentences under 20 words.** The listener cannot re-read.
- **Numbers as they are spoken.** "Four thousand dollars", "zero point eight five".
- **One cue per change of picture.** More cues than pictures means the narration is describing the screen.
- **150 words a minute.** Read each scene's word count against its time budget in the narrative. A scene over budget
  is cut, not sped up.
- **Every sentence ends with a full stop, question mark or exclamation mark.** Captions are built one per sentence.

## Checks

```bash
python3 <writing-voice skill>/scripts/verify-voice.py demo/script.md
python3 <skill>/scripts/cues.py demo/script.md /tmp/voice-check   # words per scene
```

## Leaving the phase

Record the approval, then write the shot list ([05](05-shot-list.md)).
