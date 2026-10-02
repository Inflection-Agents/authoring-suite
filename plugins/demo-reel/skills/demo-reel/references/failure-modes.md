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
| The script reference said to put a cue after the words a picture lands on, while the code times a cue from the word after it | pictures changing one phrase late | the reference says to put the cue immediately before the word the picture changes on |
| Script budgets assumed 150 words a minute, while the speech engines spoke near 210 | cuts a third shorter than their targets | budgets assume about 200 words a minute for an engine; holds give the picture time without padding the words |
| The engine trimmed a 38-second reference to exactly 30 seconds, mid-sentence | the same stray word before every scene as a badly recorded reference | the trim cuts at the last sentence that ends inside the window |
| The closing card's total had to be typed, because a title could not read a take | a number on screen that did not come from the events | a `timer-total` slot on a title shot reads the take's timer marks |
| A timer read its marks only inside the shot's own window, and only the editor layout drew one | the climax timer vanishing when the shot cut from the build to the re-run | the timer reads marks from the whole take, and three-pane takes an optional timer slot |
| The browser recorder opened only the first invocation of a take | a take with two requests showing the first one's page throughout | the recorder follows each new invocation the driver logs |
| An edit made before a shot's window was dropped from the shot | a shot starting after an edit showing the old line | edits before the window are applied from the shot's first frame |
| A Restate service restarted while a run waited on a promise, inside the one-minute inactivity window | an orange network-error banner and a second attempt in the journal | a waiting invocation suspends after a short inactivity timeout, so a restart finds no open connection |
| A shot longer than its take's window kept playing the recording past the `out` event | the next request's page on screen while the narration still described the first | the recording holds its last frame at `out`, and a hold over 2 seconds is a warning |
| The driver template held one list of steps | a demo with three scenarios needing three drivers | `SCENARIOS` holds one list per scenario, picked by `SCENARIO` |
| The capture check needed a timing file nothing wrote | a hand-written `timing.json` per engagement | `timing.py --estimate` writes it from the shot list |
| The pronunciation check compared "three hundred and twelve" with Whisper's "312" | correct narration failing the check and burning retries | both sides spell numbers as words, without "and", before comparing |
| A window 0.03 s longer than its shot was rounded up to 1.1x | a speed badge on footage that was not sped up | an overrun under 0.5 s with no logged event in it is cut instead |
| Takes were recorded before the narration existed | the picture running ahead of the words, or holding still under them | after narration, each driver pause is set from its sentence's start, and the takes are re-recorded |
| Each shot drew only the facts, terminal lines and edits inside its own window | the facts panel emptying at every cut inside one take, and a corrected line shown while the narration described the mistake | a shot shows everything its take logged before its `out` event, in log order |
| Holds were placed by counting the transcript's words, and Whisper writes "three hundred and twelve" as 312 | the narration stopping mid-sentence for two or three seconds, then resuming | holds are placed through the cue alignment; the raw scene is kept, so holds can be placed again without re-voicing |
