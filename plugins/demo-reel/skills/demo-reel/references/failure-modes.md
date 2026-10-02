# Failure modes

What went wrong in earlier engagements and reviews, what it would have cost, and the rule that now prevents it.
Engagements append to this file through the hand-back note.

| What happened | What it would have cost | The rule now |
|---|---|---|
| A recording's length, its playback speed and the shot it filled were never compared | panes that froze or cut mid-action, and a timer showing time that never passed | a shot shows a window between two events; speed is derived or checked; the props builder refuses a window that does not fit |
| Each take reset the shared event log and wrote to fixed file names | every earlier take lost its facts without a warning | one events file and one recording per take, named by the take |
| The terminal recorder, the browser recorder and the event log each ran on their own clock | facts appeared seconds before the terminal printed them | one clock per take; recorders log their own start; recordings are trimmed to it; the terminal is drawn from events |
| A 1280-pixel terminal recording was squeezed into a 560-pixel pane | text at about 10 pixels, unreadable | terminals are drawn, not recorded; the browser records at its slot's exact size |
| The determinism check compared logs that still held each run's IDs | a check that could never pass | the normalizer replaces every invocation ID wherever it appears |
| Templates used top-level await in a repository without `"type": "module"` | the driver and recorder failed to start | the capture `package.json` is an ES module with pinned `tsx` and `playwright` |
| `npx` asked to install a package inside a recorded terminal | the take stalled at a prompt | tools run from `demo/node_modules/.bin`, never through `npx` |
| A Qwen reference recording ended mid-sentence | the model spoke the reference's last word before every scene | the reference ends on a complete sentence, with an exact transcript |
