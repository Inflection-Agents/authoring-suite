# 05 Shot list

**Goal.** Say what is on screen at every cue, in a form the code side can resolve and the props builder can check.
**Produces.** `demo/shots.yaml`.
**Gate.** `python3 <skill>/scripts/verify_shots.py demo/shots.yaml demo/script.md` prints `0 problem(s)`.

## The schema

```yaml
fps: 30
cuts:
  short: {target_seconds: 240}
  long: {target_seconds: 600}
scenes:
  - {id: L1, title: The promise, cuts: [short, long], duration: 20}
shots:
  - id: L1.1
    scene: L1
    cue: headline
    layout: title
    slots: {text: {text: "A trip needs three bookings, and any one of them can fail"}}
    tags: []
```

- **`scenes`** carry their cuts and an estimated `duration` in seconds. The real length comes from the narration audio
  later; the estimate is what the runtime check uses now.
- **`shots`** sit on one cue each. A shot runs from its cue to the next shot's cue, or to the end of the scene. The first
  shot of a scene starts at the scene's start, whatever its cue.
- **Show the running system in `three-pane`**: the calls on the left, the workflow UI in the middle, the facts on the
  right. One screen then carries the request, the system's own record of it and the result, which a viewer can follow
  without being told where to look.
- **A shot that shows a recorded window** names its `take`, and optionally `in` and `out` (events in that take; default
  `capture-start` and `capture-end`) and a `speed`. Leave `speed` out and the props builder derives it from the
  window's length and the shot's length.

## Layouts and their slots

| Layout | Slots |
|---|---|
| `title` | `text: {text}`, where a phrase written `~~like this~~` is struck through; optional `total: {kind: timer-total}` with the shot's `take`, showing that take's real timer total |
| `figure` | `figure: {src: figures/<file>.svg}` |
| `code` | `code: {kind: code, find, tokens, focus: [lines], error: {line, message}}` |
| `three-pane` | `left: {kind: terminal}`, `center: {kind: browser, label}`, `right: {kind: facts-panel}`, optional `log: {kind: terminal}`, optional `timer: {kind: timer}` |
| `editor-build` | `code: {kind: code, tokens, edits: true}`, `terminal: {kind: terminal}`, `timer: {kind: timer}` |

The terminal, facts, edits, timer and timer total are filled from the take's events by the props builder. A title shot
with a `take` but no recorded slot gets no speed or stub badge. A timer reads its marks from the whole take, so a shot
that starts after `timer-start` shows the time already elapsed. The browser slot is
filled with the take's recording. Nothing in a slot is typed by hand except titles, figure paths and focus lines.

## Author side versus code side

On the author machine a code slot has `find` (what to show, in words) and no `tokens`. [07](07-reconcile.md) finds the
file and lines and sets `tokens`. Takes do not exist yet either; name them (`run-1`, `run-fail`) so the driver can be
written to produce them.

## Tags

- `design` on any shot that shows something not built. It becomes a "design" badge.
- `stub:<name>` only for a stub the driver does not declare itself. Stubs the driver declares become badges on their
  own.
- `capture: manual` on a shot a person must record by hand. List each one in the hand-back note.

## Leaving the phase

The gate is the zero-problem check. Then pack the kit ([06](06-pack.md)), or on one machine go straight to
[07](07-reconcile.md).
