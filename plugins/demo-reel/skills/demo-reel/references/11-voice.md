# 11 Voice

**Goal.** Voice every scene and turn the narration into the clock the video runs on.
**Produces.** `demo/remotion/public/voice/<id>.wav` and `<id>.words.json` per scene, and `demo/timing.json`.
**Gate.** Every scene passes the pronunciation check, or its failures are listed for the owner.

## The reference recording, for a cloned voice

About 30 seconds of one speaker in a quiet room, ending on a complete sentence, with a transcript that matches it word
for word. A reference that stops mid-sentence makes Qwen speak its last word before every scene. Keep it in
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

`--scenes L5` re-voices one scene. Qwen voices sentence chunks and transcribes each one with Whisper; a chunk whose word
error rate is above 0.12 is re-voiced with the lexicon's respellings, up to two retries, and the accepted chunk's
transcript becomes its word timings. ElevenLabs voices a whole scene per request, with the neighbouring scenes as
context and a fixed seed, and returns its own character timings.

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
