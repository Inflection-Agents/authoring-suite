# 11 Voice

**Goal.** Voice every scene and turn the narration into the clock the video runs on.
**Produces.** `demo/remotion/public/voice/<id>.wav` and `<id>.words.json` per scene, and `demo/timing.json`.
**Gate.** Every scene passes the pronunciation check, or its failures are listed for the owner.

## The reference recording, for a cloned voice

About 30 seconds of one speaker in a quiet room, ending on a complete sentence, with a transcript that matches it word
for word. A reference that stops mid-sentence makes Qwen speak its last word before every scene. A longer recording
is fine: the engine cuts it at the last sentence that ends inside its first 30 seconds, and keeps the same sentences
of the transcript. It refuses a recording with no sentence end inside those 30 seconds. Keep it in
`demo/voice-ref/ref.wav` and `ref.txt`, never in a shared repository.

## Voice the scenes

```bash
# local cloned voice (Apple silicon)
demo/.venv/bin/python <skill>/narration/narrate.py voice --engine qwen --script demo/script.md \
  --out demo/remotion/public/voice --lexicon demo/lexicon.json \
  --ref demo/voice-ref/ref.wav --ref-text demo/voice-ref/ref.txt

# cloud voice
demo/.venv/bin/python <skill>/narration/narrate.py voice --engine elevenlabs --script demo/script.md \
  --out demo/remotion/public/voice --lexicon demo/lexicon.json
```

`--scenes L5` re-voices one scene. After either engine voices a scene, its `> hold:` lines become silence in the audio
and every later word's timing moves with them. Each hold is placed through the same word alignment that times the
cues, so it lands at the end of its sentence even when Whisper writes a spoken number as digits. The scene as voiced
is kept as `<id>.raw.wav` and `<id>.raw.json`, so a changed hold line needs no re-voicing:

```bash
demo/.venv/bin/python <skill>/narration/narrate.py holds --script demo/script.md --out demo/remotion/public/voice
```

After any voice change, list the silences in each render, and check that each one is a hold:

```bash
ffmpeg -hide_banner -i demo/remotion/out/<cut>.mp4 -af silencedetect=noise=-45dB:d=0.5 -f null - 2>&1 | grep silence_end
``` Qwen voices sentence chunks and transcribes each one with Whisper; a chunk whose word
error rate is above 0.12 is re-voiced with the lexicon's respellings, up to two retries, and the accepted chunk's
transcript becomes its word timings. ElevenLabs voices a whole scene per request, with the neighbouring scenes as
context and a fixed seed, and returns its own character timings.

## Then pace the takes

Write the timing, then rebuild the props for each cut:

```bash
demo/.venv/bin/python <skill>/scripts/timing.py demo/script.md demo/remotion/public/voice demo/timing.json
demo/.venv/bin/python <skill>/scripts/build_props.py demo/shots.yaml demo/timing.json demo/takes <cut> demo/remotion/props-<cut>.json
```

The takes were recorded against estimated timing, so a shot may now hold a still frame or show a speed badge. Set
each driver step's pause from the sentence it belongs to (`timing.json` lists every sentence's start), so each event
lands on the words that describe it, then re-record the takes. A pause added for narration also runs on the climax
timer: the total it shows is then longer than the bare change, never shorter.

## ElevenLabs set-up

The key lives in `~/.config/demo-reel/elevenlabs.env` with `chmod 600`, never in a repository or a kit:

```
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...
```

`narrate.py check-key` proves the key and the voice. `narrate.py voices` lists the account's voices, cloned ones first.
`narrate.py clone --name <name> --ref demo/voice-ref/ref.wav` creates an instant voice clone, and only with the owner's
word, because it creates a voice on their account.

## Pronunciation

A word the check flags, or one the owner hears wrong, goes into `demo/lexicon.json`:

```json
{"DSL": {"respell": "dee ess ell"}}
```

Re-voice the scene. Whole words only, case-sensitive.

## Narration recorded by hand

Put `<id>.wav` files in the voice folder. With no words file, `timing.py` transcribes them with Whisper.

## The clock

```bash
demo/.venv/bin/python <skill>/scripts/timing.py demo/script.md demo/remotion/public/voice demo/timing.json
```

## Leaving the phase

Compose ([12](12-compose.md)).
