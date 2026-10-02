#!/usr/bin/env python3
"""Tests for pack. Run: python3 -m unittest test_pack (from this folder)."""
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pack as P  # noqa: E402


class Pack(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.kit = self.tmp / "demo"
        (self.kit / "_brief").mkdir(parents=True)
        (self.kit / "_brief" / "engagement.md").write_text("phase: pack\n")
        (self.kit / "narrative.md").write_text("# n\n")
        (self.kit / ".DS_Store").write_bytes(b"x")
        (self.kit / "node_modules").mkdir()
        (self.kit / "node_modules" / "x.js").write_text("x")
        secret = self.tmp / "secret.txt"
        secret.write_text("SECRET\n")
        os.symlink(secret, self.kit / "link.txt")
        (self.kit / "old-kit.zip").write_bytes(b"zip")

    def names(self, out):
        return zipfile.ZipFile(out).namelist()

    def test_keeps_kit_folder_name_and_drops_junk_links_and_zips(self):
        out = self.kit / "demo-kit.zip"
        report = P.pack(self.kit, out, limit_mb=20)
        self.assertTrue(report["ok"])
        self.assertEqual(sorted(self.names(out)), ["demo/_brief/engagement.md", "demo/narrative.md"])

    def test_prefix_survives_a_relative_dot_path(self):
        out = self.tmp / "kit.zip"
        cwd = os.getcwd()
        os.chdir(self.kit)
        try:
            P.pack(Path("."), out, limit_mb=20)
        finally:
            os.chdir(cwd)
        self.assertIn("demo/narrative.md", self.names(out))

    def test_over_limit_names_largest_files_and_writes_nothing(self):
        (self.kit / "big.wav").write_bytes(b"0" * 3_000_000)
        out = self.tmp / "kit.zip"
        report = P.pack(self.kit, out, limit_mb=1)
        self.assertFalse(report["ok"])
        self.assertEqual(report["largest"][0][0], "demo/big.wav")
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
