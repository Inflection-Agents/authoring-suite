#!/usr/bin/env python3
"""CI entry point for the geometry checker that ships with the skill.

The implementation lives in `skills/diagram-design/scripts/verify_geometry.py` so it
travels to whoever installs the plugin: an author needs to measure the diagram they just
drew, and until v2.4 only this repo could measure anything (ADR 0011). This wrapper adds
the repo-side conveniences — `--all` over the shipped assets and the grandfather
baseline — without a second copy of the predicates.

Usage:
    python3 scripts/verify-geometry.py --all --baseline
    python3 scripts/verify-geometry.py skills/diagram-design/assets/example-x.html
    python3 scripts/verify-geometry.py --all --also corner-landing,loose-start
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "skills/diagram-design/assets"
IMPL = ROOT / "skills/diagram-design/scripts/verify_geometry.py"
BASELINE = ROOT / "scripts/geometry-baseline.txt"


def _load():
    spec = importlib.util.spec_from_file_location("verify_geometry", IMPL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_impl = _load()

# Re-exported so the adversarial tests and any caller keep one implementation to target.
check = _impl.check
check_svg = _impl.check_svg
parse_rects = _impl.parse_rects
path_points = _impl.path_points
DEFAULT_CHECKS = _impl.DEFAULT_CHECKS
OPTIONAL_CHECKS = _impl.OPTIONAL_CHECKS
ALL_CHECKS = _impl.ALL_CHECKS


def load_baseline() -> set[str]:
    if not BASELINE.exists():
        return set()
    names = set()
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            names.add(line)
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="HTML diagrams to check")
    parser.add_argument("--all", action="store_true", help="check every shipped asset")
    parser.add_argument("--baseline", action="store_true",
                        help="under --all, skip files listed in scripts/geometry-baseline.txt")
    parser.add_argument("--only", help="run exactly these checks, comma-separated")
    parser.add_argument("--also", help="add optional checks to the default set")
    args = parser.parse_args()
    enabled = _impl.resolve_checks(args.only, args.also, parser)

    paths = sorted(ASSET_DIR.glob("*.html")) if args.all else [Path(p) for p in args.files]
    if not paths:
        parser.error("pass one or more files, or --all")

    baseline = load_baseline() if (args.all and args.baseline) else set()
    findings: list[str] = []
    skipped = 0
    for path in paths:
        if path.name in baseline:
            skipped += 1
            continue
        if not path.exists():
            findings.append(f"{path}: file not found")
            continue
        findings.extend(check(path, enabled))

    for finding in findings:
        print(finding)
    tail = f", {skipped} baselined" if skipped else ""
    print(f"Summary: {len(paths) - skipped} file(s) checked, {len(findings)} finding(s)"
          f"{tail}, checks: {', '.join(sorted(enabled))}.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
