# 14 Deliver

**Goal.** Hand over finished cuts the owner can publish as they are.
**Produces.** Per cut: the final MP4, an SRT caption file and a thumbnail. One hand-back note.
**Gate.** None. The owner signed off in [13](13-review.md).

## Per cut

```bash
cd demo/remotion
npx remotion render src/index.ts Cut out/<cut>.mp4 --props=props-<cut>.json
npx remotion still src/index.ts Cut out/<cut>.png --frame=<a frame from the climax> --props=props-<cut>.json
cd ../..
demo/.venv/bin/python <skill>/scripts/captions.py demo/timing.json demo/remotion/props-<cut>.json demo/out/<cut>.srt
```

Captions are one per spoken sentence, on the same clock as the video.

## The hand-back note

`demo/HANDBACK.md`, listing:

1. Each cut's file, length and target.
2. Every `capture: manual` shot and who recorded it.
3. Every disagreement ruled in [07](07-reconcile.md) and the ruling.
4. Every layout or helper added to `demo/` that the plugin should take back.
5. What went wrong, for [failure-modes.md](failure-modes.md).

## Leaving the phase

Set the ledger's phase to `deliver` and record the files delivered.
