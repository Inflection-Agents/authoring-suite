"""Word timestamps from audio, with Whisper on Apple silicon (mlx-whisper) or elsewhere (openai-whisper).

Used for Qwen's pronunciation check, where the transcript of each accepted chunk doubles as its word
timings, and as the fallback for narration recorded by hand.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

MLX_MODEL = "mlx-community/whisper-large-v3-turbo"


def words_from_file(path: str | Path) -> list[dict]:
    try:
        import mlx_whisper
        result = mlx_whisper.transcribe(str(path), path_or_hf_repo=MLX_MODEL, word_timestamps=True)
    except ImportError:
        import whisper
        result = whisper.load_model("turbo").transcribe(str(path), word_timestamps=True)
    return [{"word": w["word"].strip(), "start": round(float(w["start"]), 3), "end": round(float(w["end"]), 3)}
            for seg in result["segments"] for w in seg.get("words", [])]


def words_from_audio(audio, sr: int) -> list[dict]:
    import soundfile as sf

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name
    try:
        sf.write(path, audio, sr)
        return words_from_file(path)
    finally:
        Path(path).unlink(missing_ok=True)
