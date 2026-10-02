# 09 Driver

**Goal.** Make the scenario run the same way every time, and log everything the video will show.
**Produces.** `demo/driver/driver.ts`, `demo/driver/reset.sh`, `demo/capture/browser.ts`, `demo/capture/run-take.sh`.
**Gate.** Two takes of the scenario normalize to identical event logs.

## Set up

```bash
mkdir -p demo/driver demo/capture
cp <skill>/templates/driver/driver.ts <skill>/templates/driver/reset.sh demo/driver/
cp <skill>/templates/capture/browser.ts <skill>/templates/capture/run-take.sh demo/capture/
```

`reset.sh` needs `STOP_CMD`, `START_CMD` and `HEALTH_URL` for the system under demo. It clears only the take it is
about to record, so takes never overwrite each other.

## Write the steps

Fill `STEPS` in `driver.ts` with the scenario, using its helpers. Each helper logs an event the video reads:

| Helper | Logs | Shown as |
|---|---|---|
| `call(step, method, path, body)` | `request`, `response` | terminal lines |
| `command(step, cmd)` | `command` with its exit code and output | terminal lines, red on failure |
| `edit(step, file, line, after)` | `edit` with the line before and after | the line retyped in the code pane |
| `invocation(step, id)` | `invocation` | the browser opens this ID |
| `fact(name, value)`, `outcome(name, value)` | `fact`, `outcome` | the facts panel |
| `stub(name)` | `stub` | a "stub" badge on every shot of the take |
| `mark(name)` | `mark` | a shot's `in` or `out`, or the timer |

Rules:

- **Call `stub()` for every dependency the demo replaces.** The badge is computed from it.
- **For a live change,** log `mark('timer-start')` immediately before the first `edit`, then run the build with
  `command`, re-run the scenario with `call`, and log `mark('timer-stop')` when the re-run's outcome arrives. The timer
  shows only the real time between those marks.
- **A deliberate mistake is part of the scenario.** An `edit` that breaks the build, the failing `command`, then the
  `edit` that fixes it: the video shows exactly what happened.
- **Pause between steps** (`pauseMs`) so a viewer can read; the props builder speeds a long window up and says so.

## Prove determinism

```bash
TAKE=a bash demo/capture/run-take.sh
TAKE=b bash demo/capture/run-take.sh
diff <(demo/.venv/bin/python <skill>/scripts/normalize_events.py demo/takes/a/events.jsonl) \
     <(demo/.venv/bin/python <skill>/scripts/normalize_events.py demo/takes/b/events.jsonl)
```

The diff must print nothing. The normalizer drops times and take names and replaces each invocation ID wherever it
appears. A remaining difference is a real one: a timestamp in a response body, a random value, an order that changes.
Fix the system's seed or the driver, not the normalizer.

## Leaving the phase

Delete the two proof takes, then capture ([10](10-capture.md)).
