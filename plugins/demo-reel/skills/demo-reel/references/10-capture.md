# 10 Capture

**Goal.** Record one take for every `take` the shot list names, and prove every shot's window fits.
**Produces.** `demo/takes/<take>/events.jsonl` and `demo/remotion/public/takes/<take>/browser.webm` per take.
**Gate.** `build_props.py` reports no problem about a take for either cut.

## Record

```bash
TAKE=run-1 UI_ROUTE='http://localhost:<port>/<route>/{id}' STEP=start bash demo/capture/run-take.sh
```

`STEP` names the driver step whose `invocation` event the browser should open. The browser records at 820 by 1000,
the three-pane centre slot's exact size, so the recording is never scaled. With a log strip the slot is 820 by 780:
set `WIDTH` and `HEIGHT` to match.

Give each agent one take when takes run in parallel, and never two agents on one take: the system under demo is shared
state. Run takes one after another unless the system has one instance per take.

## Prove the windows fit

```bash
demo/.venv/bin/python <skill>/scripts/build_props.py demo/shots.yaml demo/timing.json demo/takes <cut> /tmp/check.json
```

Before narration exists, write a `demo/timing.json` from the shot list's estimated durations with cues spread evenly,
so this check can run now. Every problem it names about a take (no events file, a missing mark, a window that cannot
fit at the given speed, a browser slot with no recording) is fixed by re-recording or by editing the shot's `in`, `out`
or `speed`.

## Figures

Copy the source document's figures to `demo/remotion/public/figures/`, under the names the shot list uses.

## Leaving the phase

Narrate ([11](11-voice.md)).
