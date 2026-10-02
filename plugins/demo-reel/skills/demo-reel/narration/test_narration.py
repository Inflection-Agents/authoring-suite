#!/usr/bin/env python3
"""Tests for the narration helpers that need no model and no network.
Run: python3 -m unittest test_narration (from this folder)."""
import base64
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
import elevenlabs_engine as E  # noqa: E402
import lexicon as LX  # noqa: E402
from textutil import chars_to_words, chunk, shift, wer  # noqa: E402


class Config(unittest.TestCase):
    def setUp(self):
        self.path = Path(tempfile.mkdtemp()) / "elevenlabs.env"
        self.path.write_text('# demo-reel\nexport ELEVENLABS_API_KEY="file-key"\nELEVENLABS_VOICE_ID=v1\n')

    def test_file_values(self):
        cfg = config.elevenlabs(env={}, path=self.path)
        self.assertEqual(cfg, {"api_key": "file-key", "voice_id": "v1", "model_id": "eleven_multilingual_v2"})

    def test_environment_overrides_file(self):
        cfg = config.elevenlabs(env={"ELEVENLABS_API_KEY": "env-key"}, path=self.path)
        self.assertEqual((cfg["api_key"], cfg["voice_id"]), ("env-key", "v1"))

    def test_missing_file_gives_empty_key(self):
        self.assertEqual(config.elevenlabs(env={}, path=self.path.with_name("none"))["api_key"], "")

    def test_private_file(self):
        os.chmod(self.path, 0o600)
        self.assertTrue(config.file_is_private(self.path))
        os.chmod(self.path, 0o644)
        self.assertFalse(config.file_is_private(self.path))


class Lexicon(unittest.TestCase):
    def test_whole_words_only_longest_first(self):
        lex = {"DTI": "dee tee eye", "DTI ratio": "debt ratio"}
        self.assertEqual(LX.apply("The DTI ratio and DTIs and pre-DTI.", lex), "The debt ratio and DTIs and pre-DTI.")

    def test_load_reads_respell_only(self):
        p = Path(tempfile.mkdtemp()) / "lexicon.json"
        p.write_text(json.dumps({"zod": {"ipa": "zɒd", "respell": "zod"}, "x": {"ipa": "ks"}}))
        self.assertEqual(LX.load(p), {"zod": "zod"})


class Text(unittest.TestCase):
    def test_chunk_packs_sentences(self):
        self.assertEqual(chunk("One two. Three four. Five.", max_chars=12), ["One two.", "Three four.", "Five."])
        self.assertEqual(chunk("One two. Three four.", max_chars=100), ["One two. Three four."])

    def test_chars_to_words(self):
        text = "Hi there"
        alignment = {"characters": list(text),
                     "character_start_times_seconds": [i * 0.1 for i in range(len(text))],
                     "character_end_times_seconds": [i * 0.1 + 0.1 for i in range(len(text))]}
        self.assertEqual(chars_to_words(alignment), [{"word": "Hi", "start": 0.0, "end": 0.2},
                                                     {"word": "there", "start": 0.3, "end": 0.8}])

    def test_shift(self):
        self.assertEqual(shift([{"word": "a", "start": 0.1, "end": 0.2}], 1.0), [{"word": "a", "start": 1.1, "end": 1.2}])

    def test_wer(self):
        self.assertEqual(wer("The DTI is low.", "the dti is low"), 0.0)
        self.assertAlmostEqual(wer("one two three four", "one too three four"), 0.25)


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class ElevenLabs(unittest.TestCase):
    cfg = {"api_key": "k", "voice_id": "v1", "model_id": "eleven_multilingual_v2"}

    def test_request_url_and_body(self):
        url, body = E.tts_request("Hello.", "v1", "m", seed=7, previous_text="Before.", next_text=None)
        self.assertEqual(url, "https://api.elevenlabs.io/v1/text-to-speech/v1/with-timestamps?output_format=mp3_44100_128")
        self.assertEqual(body, {"text": "Hello.", "model_id": "m", "seed": 7, "previous_text": "Before."})

    def test_synth_writes_audio_and_returns_words(self):
        seen = {}

        def opener(req, timeout):
            seen["key"] = req.get_header("Xi-api-key")
            seen["body"] = json.loads(req.data)
            text = "Hi you"
            return FakeResponse(json.dumps({"audio_base64": base64.b64encode(b"mp3").decode(), "alignment": {
                "characters": list(text), "character_start_times_seconds": [0, .1, .2, .3, .4, .5],
                "character_end_times_seconds": [.1, .2, .3, .4, .5, .6]}}).encode())

        decoded = {}
        out = Path(tempfile.mkdtemp()) / "S1.wav"
        words = E.synth("Hi you", out, self.cfg, seed=1, opener=opener,
                        decode=lambda mp3, path: decoded.update(mp3=mp3, path=path))
        self.assertEqual(seen["key"], "k")
        self.assertEqual(seen["body"]["seed"], 1)
        self.assertEqual(decoded, {"mp3": b"mp3", "path": out})
        self.assertEqual([w["word"] for w in words], ["Hi", "you"])

    def test_http_error_names_status_without_key(self):
        def opener(req, timeout):
            raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, io.BytesIO(b'{"detail":"invalid key"}'))

        with self.assertRaises(E.ElevenLabsError) as e:
            E.voices(self.cfg, opener=opener)
        self.assertIn("401", str(e.exception))
        self.assertNotIn("'k'", str(e.exception))

    def test_voices_lists_id_name_and_category(self):
        def opener(req, timeout):
            return FakeResponse(b'{"voices": [{"voice_id": "a", "name": "Owner", "category": "cloned"}, {"voice_id": "b"}]}')

        self.assertEqual(E.voices(self.cfg, opener=opener), [{"voice_id": "a", "name": "Owner", "category": "cloned"},
                                                             {"voice_id": "b", "name": "", "category": ""}])

    def test_missing_key_and_voice(self):
        with self.assertRaises(E.ElevenLabsError):
            E.voices({"api_key": "", "voice_id": "", "model_id": "m"})
        with self.assertRaises(E.ElevenLabsError):
            E.synth("x", Path("x.wav"), {"api_key": "k", "voice_id": "", "model_id": "m"})

    def test_clone_sends_multipart_and_returns_voice_id(self):
        ref = Path(tempfile.mkdtemp()) / "ref.wav"
        ref.write_bytes(b"RIFFdata")
        seen = {}

        def opener(req, timeout):
            seen["ctype"] = req.get_header("Content-type")
            seen["data"] = req.data
            return FakeResponse(b'{"voice_id": "new1", "requires_verification": false}')

        self.assertEqual(E.clone("Owner", [ref], self.cfg, opener=opener), "new1")
        self.assertTrue(seen["ctype"].startswith("multipart/form-data; boundary="))
        self.assertIn(b'name="name"\r\n\r\nOwner', seen["data"])
        self.assertIn(b'filename="ref.wav"', seen["data"])
        self.assertIn(b"RIFFdata", seen["data"])


if __name__ == "__main__":
    unittest.main()
