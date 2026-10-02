#!/usr/bin/env python3
"""Voice every scene of a demo script, in the owner's cloned voice, with word timings.

    narrate.py voice --engine qwen --script demo/script.md --out demo/remotion/public/voice \
        --ref demo/voice-ref/ref.wav --ref-text demo/voice-ref/ref.txt [--lexicon demo/lexicon.json]
    narrate.py voice --engine elevenlabs --script demo/script.md --out demo/remotion/public/voice
    narrate.py holds --script demo/script.md --out demo/remotion/public/voice   # re-place holds, no re-voicing
    narrate.py check-key            # ElevenLabs: is the key there, private, and accepted?
    narrate.py voices               # ElevenLabs: the account's voices, to pick ELEVENLABS_VOICE_ID
    narrate.py clone --name "Owner" --ref demo/voice-ref/ref.wav   # ElevenLabs instant voice clone

Each scene becomes <out>/<id>.wav and <out>/<id>.words.json ({"engine", "words": [{word, start, end}],
"qc": [...]}), which timing.py reads instead of transcribing again. --scenes L1,L5 voices only those.

Qwen voices sentence chunks, transcribes each with Whisper, and re-voices a chunk with the lexicon's
respellings when its word error rate is above the threshold; the accepted chunk's transcript is its
word timings. ElevenLabs voices a whole scene per request, with the neighbouring scenes sent as context
and a fixed seed, and returns its own character timings.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))

import config  # noqa: E402
import lexicon as LX  # noqa: E402
from textutil import chunk, shift, wer  # noqa: E402


def finish(scene, out: Path, engine: str, words: list[dict], qc: list) -> float:
    """Keep the scene as voiced (<id>.raw.wav, <id>.raw.json), then place its holds."""
    import shutil

    shutil.copyfile(out / f"{scene.id}.wav", out / f"{scene.id}.raw.wav")
    (out / f"{scene.id}.raw.json").write_text(json.dumps({"engine": engine, "words": words, "qc": qc}, indent=1))
    return place_holds(scene, out)


def place_holds(scene, out: Path) -> float:
    """Write <id>.wav and <id>.words.json from the raw scene with its holds as silence. Runs again after a hold
    line changes, with no re-voicing, because it always starts from the raw audio."""
    import wave

    import holds as HD

    raw = json.loads((out / f"{scene.id}.raw.json").read_text())
    with wave.open(str(out / f"{scene.id}.raw.wav"), "rb") as w:
        duration = w.getnframes() / w.getframerate()
    words, inserts = HD.apply_holds(raw["words"], scene.holds, duration, script_words=scene.text.split())
    HD.insert_silence(out / f"{scene.id}.raw.wav", out / f"{scene.id}.wav", inserts)
    (out / f"{scene.id}.words.json").write_text(json.dumps({**raw, "words": words}, indent=1))
    return duration + sum(s for _, s in inserts)


def _scenes(script: Path, only: str | None):
    from cues import parse_script

    scenes = parse_script(script.read_text())
    keep = set(only.split(",")) if only else None
    return scenes, keep


def voice_qwen(scenes, keep, out: Path, ref: str, ref_text: str, lex: dict, qc: bool, threshold: float,
               retries: int, gap_ms: int = 120) -> int:
    import numpy as np
    import soundfile as sf

    import asr
    import qwen_engine as Q

    flagged = 0
    for scene in scenes:
        if keep and scene.id not in keep:
            continue
        pieces, report = [], []
        for i, text in enumerate(chunk(scene.text), 1):
            best = None
            attempts = []
            for attempt in range(retries + 1 if qc else 1):
                send = text if attempt == 0 else LX.apply(text, lex)
                audio, sr = Q.synth(send, ref, ref_text)
                if not qc:
                    best = (audio, sr, [], 0.0)
                    break
                heard = asr.words_from_audio(audio, sr)
                w = wer(text, " ".join(h["word"] for h in heard))
                attempts.append({"attempt": attempt, "wer": round(w, 3)})
                if best is None or w < best[3]:
                    best = (audio, sr, heard, w)
                if w <= threshold:
                    break
            audio, sr, heard, w = best
            report.append({"chunk": i, "text": text, "wer": round(w, 3), "passed": w <= threshold,
                           "attempts": attempts})
            flagged += w > threshold
            pieces.append((audio, sr, heard))
        sr = pieces[0][1]
        full, words = pieces[0][0], list(pieces[0][2])
        gap = np.zeros(int(sr * gap_ms / 1000), np.float32)
        for audio, _, heard in pieces[1:]:
            base = np.concatenate([full, gap])
            full, overlap = Q.crossfade(base, audio, sr)
            words += shift(heard, (len(base) - overlap) / sr)
        peak = float(np.max(np.abs(full))) or 1.0
        sf.write(out / f"{scene.id}.wav", (full / peak * 0.89).astype(np.float32), sr, subtype="PCM_16")
        seconds = finish(scene, out, "qwen", words, report)
        bad = [r["chunk"] for r in report if not r["passed"]]
        print(f"{scene.id}: {seconds:.1f}s, {len(report)} chunks" + (f", review chunks {bad}" if bad else ""))
    return 1 if flagged else 0


def voice_elevenlabs(scenes, keep, out: Path, lex: dict, seed: int) -> int:
    import elevenlabs_engine as E

    cfg = config.elevenlabs()
    texts = [LX.apply(s.text, lex) for s in scenes]
    for i, scene in enumerate(scenes):
        if keep and scene.id not in keep:
            continue
        words = E.synth(texts[i], out / f"{scene.id}.wav", cfg, seed=seed,
                        previous_text=texts[i - 1] if i else None,
                        next_text=texts[i + 1] if i + 1 < len(texts) else None)
        seconds = finish(scene, out, "elevenlabs", words, [])
        print(f"{scene.id}: {seconds:.1f}s, {len(words)} words")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("voice")
    v.add_argument("--engine", choices=["qwen", "elevenlabs"], required=True)
    v.add_argument("--script", type=Path, required=True)
    v.add_argument("--out", type=Path, required=True)
    v.add_argument("--scenes")
    v.add_argument("--lexicon", type=Path)
    v.add_argument("--ref")
    v.add_argument("--ref-text")
    v.add_argument("--no-qc", action="store_true")
    v.add_argument("--wer-threshold", type=float, default=0.12)
    v.add_argument("--retries", type=int, default=2)
    v.add_argument("--seed", type=int, default=1234)
    h = sub.add_parser("holds")
    h.add_argument("--script", type=Path, required=True)
    h.add_argument("--out", type=Path, required=True)
    h.add_argument("--scenes")
    c = sub.add_parser("clone")
    c.add_argument("--name", required=True)
    c.add_argument("--ref", type=Path, nargs="+", required=True)
    sub.add_parser("check-key")
    sub.add_parser("voices")
    a = ap.parse_args(argv[1:])

    if a.cmd == "voices":
        import elevenlabs_engine as E

        for v in sorted(E.voices(config.elevenlabs()), key=lambda v: (v["category"] != "cloned", v["name"])):
            print(f"{v['voice_id']}  {v['category']:<12} {v['name']}")
        return 0

    if a.cmd == "check-key":
        import elevenlabs_engine as E

        cfg = config.elevenlabs()
        if not cfg["api_key"]:
            print(f"no key: add ELEVENLABS_API_KEY to {config.ELEVENLABS_FILE}")
            return 1
        if config.ELEVENLABS_FILE.exists() and not config.file_is_private():
            print(f"warning: {config.ELEVENLABS_FILE} is readable by others; run chmod 600 on it")
        found = E.voices(cfg)
        print(f"key accepted: {len(found)} voices on the account")
        if cfg["voice_id"]:
            match = [x["name"] for x in found if x["voice_id"] == cfg["voice_id"]]
            print(f"ELEVENLABS_VOICE_ID is {'the voice ' + repr(match[0]) if match else 'not on this account'}")
            return 0 if match else 1
        print("no ELEVENLABS_VOICE_ID yet: pick one from `narrate.py voices`, or create one with `narrate.py clone`")
        return 0

    if a.cmd == "clone":
        import elevenlabs_engine as E

        voice_id = E.clone(a.name, a.ref, config.elevenlabs())
        print(f"created voice {voice_id}; add ELEVENLABS_VOICE_ID={voice_id} to {config.ELEVENLABS_FILE}")
        return 0

    if a.cmd == "holds":
        scenes, keep = _scenes(a.script, a.scenes)
        for scene in scenes:
            if (keep is None or scene.id in keep) and (a.out / f"{scene.id}.raw.json").exists():
                print(f"{scene.id}: {place_holds(scene, a.out):.1f}s, {len(scene.holds)} holds")
        return 0

    a.out.mkdir(parents=True, exist_ok=True)
    scenes, keep = _scenes(a.script, a.scenes)
    lex = LX.load(a.lexicon)
    if a.engine == "elevenlabs":
        return voice_elevenlabs(scenes, keep, a.out, lex, a.seed)
    if not a.ref or not a.ref_text:
        print("qwen needs --ref (reference recording) and --ref-text (its exact transcript)", file=sys.stderr)
        return 2
    return voice_qwen(scenes, keep, a.out, a.ref, Path(a.ref_text).read_text().strip(), lex,
                      not a.no_qc, a.wer_threshold, a.retries)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
