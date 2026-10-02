#!/usr/bin/env python3
"""Zip an engagement's demo/ folder into a kit, refusing an oversized one.

The kit often travels by email, so the limit is checked against the uncompressed size: some mail
gateways unpack attachments to scan them. Symbolic links are skipped, because a link can point
outside the kit and carry a file nobody meant to send.

Usage:
    python3 pack.py demo demo-kit.zip [--limit-mb 20]
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

JUNK = {".DS_Store", "Thumbs.db"}
JUNK_DIRS = {"node_modules", "__pycache__", ".git", ".venv"}


def _files(kit: Path, out: Path):
    out = out.resolve()
    for p in sorted(kit.rglob("*")):
        rel = p.relative_to(kit)
        if (p.is_symlink() or not p.is_file() or p.name in JUNK or set(rel.parts) & JUNK_DIRS
                or p.resolve() == out or p.suffix == ".zip"):
            continue
        yield p


def pack(kit: Path, out: Path, limit_mb: float = 20) -> dict:
    kit = kit.resolve()
    files = list(_files(kit, out))
    sizes = [(f"{kit.name}/{p.relative_to(kit).as_posix()}", p.stat().st_size) for p in files]
    total = sum(s for _, s in sizes)
    largest = sorted(sizes, key=lambda x: -x[1])[:5]
    ok = total <= limit_mb * 1_000_000
    if ok:
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for p, (arc, _) in zip(files, sizes):
                z.write(p, arc)
    return {"ok": ok, "total_mb": round(total / 1_000_000, 2),
            "zip_mb": round(out.stat().st_size / 1_000_000, 2) if ok else None,
            "files": len(files), "largest": largest}


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: pack.py demo demo-kit.zip [--limit-mb 20]", file=sys.stderr)
        return 2
    limit = float(argv[argv.index("--limit-mb") + 1]) if "--limit-mb" in argv else 20
    r = pack(Path(argv[1]), Path(argv[2]), limit)
    if not r["ok"]:
        print(f"{r['files']} files, {r['total_mb']} MB unpacked: over the {limit:g} MB limit, nothing written.")
        print("largest files:")
        for name, size in r["largest"]:
            print(f"  {size / 1_000_000:6.2f} MB  {name}")
        return 1
    print(f"{r['files']} files, {r['total_mb']} MB unpacked, {r['zip_mb']} MB zipped -> {argv[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
