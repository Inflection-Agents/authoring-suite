# 10 Capture

**Goal.** Record one take for every `take` the shot list names, and prove every shot's window fits.
**Produces.** `demo/takes/<take>/events.jsonl` and `demo/remotion/public/takes/<take>/browser.webm` per take.
**Gate.** `build_props.py` reports no problem about a take for either cut.

## Record

```bash
TAKE=run-1 UI_ROUTE='http://localhost:<port>/<route>/{id}' bash demo/capture/run-take.sh
```

The browser opens the page of each new invocation the driver logs, so a take with two requests shows each in turn.
Set `STEP` to follow only one driver step's invocations. The browser records at 820 by 1000,
the three-pane centre slot's exact size, so the recording is never scaled. With a log strip the slot is 820 by 780:
set `WIDTH` and `HEIGHT` to match.

Give each agent one take when takes run in parallel, and never two agents on one take: the system under demo is shared
state. Run takes one after another unless the system has one instance per take.

## Prove the windows fit

```bash
demo/.venv/bin/python <skill>/scripts/build_props.py demo/shots.yaml demo/timing.json demo/takes <cut> /tmp/check.json
```

Before narration exists, estimate `demo/timing.json` from the shot list's durations, so this check can run now:

```bash
demo/.venv/bin/python <skill>/scripts/timing.py --estimate demo/shots.yaml demo/script.md demo/timing.json
```
 Every problem it names about a take (no events file, a missing mark, a window that cannot
fit at the given speed, a browser slot with no recording) is fixed by re-recording or by editing the shot's `in`, `out`
or `speed`.

A window shorter than its shot is not a problem: the recording holds its last frame at the `out` event, so it never
shows what came after. A hold longer than 2 seconds is a warning, because it reads as a frozen screen. With estimated
timing, note the warnings and move on. After narration, rebuild the props, lengthen the driver's pauses where a warning
remains, and re-record those takes.

## Figures

Copy the source document's figures to `demo/remotion/public/figures/`, under the names the shot list uses.

## Leaving the phase

Narrate ([11](11-voice.md)).
