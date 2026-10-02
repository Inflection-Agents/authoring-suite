# 12 Compose

**Goal.** Build each cut from the shot list, the clock and the takes, and render a draft.
**Produces.** `demo/remotion/props-<cut>.json` and `demo/remotion/out/<cut>.mp4`.
**Gate.** `build_props.py` reports 0 problems for every cut, and every cut renders.

## Build and render

```bash
demo/.venv/bin/python <skill>/scripts/build_props.py demo/shots.yaml demo/timing.json demo/takes <cut> \
  demo/remotion/props-<cut>.json
cd demo/remotion
npm run studio                                                         # preview
npx remotion render src/index.ts Cut out/<cut>.mp4 --props=props-<cut>.json
```

`build_props.py` writes nothing when it finds a problem, and lists every problem at once. It warns, without failing,
when a cut's real runtime is more than 10% off its target.

## What the props builder decides

- Each shot runs from its cue to the next shot's cue. Two shots on one frame is an error.
- A recorded window plays at the speed that fits it into the shot, never below 1, and the badge shows that speed.
- The browser recording is trimmed so it shows the window's first moment on the shot's first frame.
- Terminal lines, facts, edits and the timer are placed on the take's clock at that speed.
- A shot shows everything its take logged before its `out` event: facts, terminal lines and edits from earlier shots
  are on screen from its first frame, so cutting inside one take never empties a pane.

## A layout the starter lacks

Add it to `demo/remotion/src/layouts/` and to the `LAYOUTS` map in `Cut.tsx`, keep its slots filled from the props
file only, and propose it back to the plugin in the hand-back note.

## Leaving the phase

Review ([13](13-review.md)).
