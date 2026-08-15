#!/usr/bin/env python3
"""Regenerate the README screenshots from the shipped examples.

Generated, never hand-edited — a screenshot is a rendering of an example, and when the skin
changes every one of them goes stale silently. M1 proved that: the brand skin landed and the
README kept advertising the old palette, because nothing checks an image.

This is **not** a CI gate. It needs Playwright and a real browser, which CI does not have, and
rendering is not deterministic enough across platforms to diff. Run it by hand after any change
to the skin or to a screenshotted example:

    pip install playwright && playwright install chromium
    python3 scripts/build-screenshots.py

Framing is the `.frame` wrapper (the eyebrow, the h1, the diagram, the legend) at 2x, so every
image is the same width and crops to content instead of to an arbitrary viewport. The previous
set had four different widths between 1136 and 2800 because each was captured ad hoc.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "skills/diagram-design/assets"
OUT = REPO / "docs/screenshots"

VIEWPORT_WIDTH = 1400
SCALE = 2
MARGIN = 40  # CSS px of paper around the wrapper, so the eyebrow is not flush to the edge
# The examples wrap their content in one of these, in order of preference.
WRAPPERS = (".frame", ".container")


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Playwright is required: pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        return 1

    targets = sorted(OUT.glob("*.png"))
    if not targets:
        print(f"no screenshots to regenerate in {OUT}", file=sys.stderr)
        return 1

    written = 0
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(
            viewport={"width": VIEWPORT_WIDTH, "height": 900},
            device_scale_factor=SCALE,
        )
        for target in targets:
            source = ASSETS / f"example-{target.stem}.html"
            if not source.exists():
                print(f"  SKIP {target.name}: no example-{target.stem}.html", file=sys.stderr)
                continue
            page.goto(f"file://{source.resolve()}")
            page.wait_for_load_state("networkidle")
            # Fonts load from Google Fonts; without this the capture can race the swap.
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(250)

            box = None
            for wrapper in WRAPPERS:
                candidate = page.locator(wrapper).first
                if candidate.count():
                    box = candidate.bounding_box()
                    break
            if box is None:
                page.screenshot(path=str(target))
            else:
                # Crop to the wrapper plus a margin, rather than screenshotting the element
                # itself: the element box is flush to the eyebrow and the crop looks clipped.
                # Padding the element instead would reflow the diagram inside it.
                extent = page.evaluate(
                    "() => [document.documentElement.scrollWidth,"
                    " document.documentElement.scrollHeight]"
                )
                left = max(0, box["x"] - MARGIN)
                top = max(0, box["y"] - MARGIN)
                page.screenshot(
                    path=str(target),
                    clip={
                        "x": left,
                        "y": top,
                        "width": min(box["width"] + 2 * MARGIN, extent[0] - left),
                        "height": min(box["height"] + 2 * MARGIN, extent[1] - top),
                    },
                )
            written += 1
            print(f"  {target.relative_to(REPO)}", file=sys.stderr)
        browser.close()

    print(f"Done. {written} screenshot(s) at {VIEWPORT_WIDTH}px x{SCALE}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
