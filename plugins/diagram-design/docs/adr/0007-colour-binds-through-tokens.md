# ADR 0007 — Generated SVG binds colour through `--dd-*` tokens

**Status:** accepted (v2.4)

## Context

Every colour in a generated diagram was a literal — around 6,500 hex and `rgba()` values across 97 examples and 5 templates. `style-guide.md` claimed to be the single source of truth for the skin, but changing it repainted nothing: reskinning a shipped diagram meant editing every attribute in it. That is why 20 legacy examples sat in `lint-skin-baseline.txt` for two minor versions — they were built against an older palette and re-skinning them was never worth the edit cost.

## Decision

Colour and radius bind through CSS custom properties, prefixed `--dd-` because these files are embedded into slide decks and documentation pages where an unprefixed `--paper` would collide with the host page's tokens. The 25-role contract has exactly one definition, `CONTRACT` in `scripts/build-skins.py`; `build-skins.py` generates `assets/skins/active-{light,dark}.tokens.css` from the tables in `style-guide.md`, and CI runs the script then `git diff --exit-code`, exactly as it already does for icons.

Each diagram inlines the generated `:root` block — never links it, so self-containment (`SKILL.md` §12) holds. `lint-skin.py` rejects a `var(--dd-…)` that names no contract role, and requires any file using the contract to declare all 25 roles, so a half-written skin cannot ship. A shade with no named role is written `color-mix(in srgb, var(--dd-ink) 55%, transparent)`, which resolves to exactly the `rgba()` it replaces.

## Consequences

- Reskinning a diagram is one `:root` block, not one edit per attribute. `references/skins/editorial-default.md` archives the previous skin so the round trip is a documented operation rather than an aspiration.
- `lint-skin-baseline.txt` is empty for the first time. The 20 legacy files conform because conforming finally cost one block each.
- Radius rides a class (`dd-node`, `dd-tag`, `dd-container`) with the literal `rx` attribute kept as a fallback — `rx` as a CSS geometry property landed late in Safari.
- Consumers that do not resolve custom properties — older Illustrator, some Figma import paths, non-browser rasterizers — will not pick up the palette from a standalone `.svg`. `references/export.md` says so, and PNG remains the recommendation for pixel-perfect portability.
