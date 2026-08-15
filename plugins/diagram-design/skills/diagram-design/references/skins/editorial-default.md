# Editorial Default — archived skin

The upstream Diagram Design skin: white-smoke paper, jet-black ink, atomic-tangerine accent,
blue-slate muted. It shipped as the default through v2.4.1 and was replaced by the Inflection Agents
brand skin in M1 PR 4.

It is kept here because a skin system that cannot get back to where it started is not portable. This
file is the proof: restoring it is a table swap and a script run, and it is exercised as part of
M1's definition of done.

## How to restore it

1. Replace the **Semantic roles**, **Wash roles**, **Geometry roles**, **Series palette**, and
   **Typography** tables in [`../style-guide.md`](../style-guide.md) with the tables below.
2. Regenerate the skin: `python3 scripts/build-skins.py`
3. Re-skin the shipped assets:
   `python3 scripts/migrate-to-tokens.py skills/diagram-design/assets/example-*.html skills/diagram-design/assets/template*.html`
4. Swap the Google Fonts `<link>` in every asset back to the stack at the bottom of this file.
5. Verify: `python3 scripts/lint-skin.py --all` and `python3 scripts/test-build-skins.py`.

Step 3 exists only because the assets carry an inlined copy of the skin — that inlining is what keeps
each file self-contained. The colour *bindings* need no change at all; only the `:root` block does.

---

## Semantic roles

| Role | Purpose | Default (light) | Default (dark) |
|---|---|---|---|
| `paper` | Page background, default node fill | `#f5f5f5` (white-smoke) | `#2d3142` (jet-black) |
| `paper-2` | Diagram container bg, secondary fill | `#ececec` | `#393e53` |
| `node-white` | Backend / API / step node fill | `#ffffff` | `#ffffff` |
| `ink` | Primary text, primary stroke | `#2d3142` (jet-black) | `#f5f5f5` (white-smoke) |
| `muted` | Secondary text, default arrow stroke | `#4f5d75` (blue-slate) | `#bfc0c0` (silver) |
| `soft` | Sublabels, boundary labels | `#7a8399` | `#8e98ac` |
| `rule` | Hairline borders | `rgba(45,49,66,0.12)` | `rgba(245,245,245,0.12)` |
| `rule-solid` | Stronger borders, baselines | `#bfc0c0` (silver) | `rgba(191,192,192,0.25)` |
| `accent` | Focal / 1–2 max per diagram | `#eb6c36` (atomic-tangerine) | `#f08a59` |
| `accent-tint` | Fill for accent-bordered boxes | `rgba(235,108,54,0.08)` | `rgba(240,138,89,0.10)` |
| `link` | HTTP/API calls, external arrows | `#2e5aa8` | `#6a95d8` |

> **Brand palette source:** this skin maps to a five-color brand palette — `jet-black #2d3142`,
> `silver #bfc0c0`, `white-smoke #f5f5f5`, `atomic-tangerine #eb6c36`, `blue-slate #4f5d75`. The
> `soft`, `rule`, and `link` tokens are derived (lighter slate, ink-at-opacity, and a saturated
> variant in the blue-slate hue family) to cover roles the brand palette doesn't name directly.

## Wash roles

| Role | Derived from | Default (light) | Default (dark) |
|---|---|---|---|
| `wash-2` | `ink @ 0.02` | `rgba(45,49,66,0.02)` | `rgba(245,245,245,0.02)` |
| `wash-3` | `ink @ 0.03` | `rgba(45,49,66,0.03)` | `rgba(245,245,245,0.03)` |
| `wash-5` | `ink @ 0.05` | `rgba(45,49,66,0.05)` | `rgba(245,245,245,0.05)` |
| `wash-10` | `muted @ 0.10` | `rgba(79,93,117,0.10)` | `rgba(191,192,192,0.10)` |
| `wash-20` | `ink @ 0.20` | `rgba(45,49,66,0.20)` | `rgba(245,245,245,0.20)` |
| `wash-30` | `ink @ 0.30` | `rgba(45,49,66,0.30)` | `rgba(245,245,245,0.30)` |

## Geometry roles

| Role | Default | Use |
|---|---|---|
| `radius-node` | `6` | Node boxes |
| `radius-tag` | `2` | Type tags, label masks |
| `radius-container` | `8` | Zones, rings, containers |

Matching authoring names in the Stroke, radius, spacing table: `radius-sm` `4`, `radius-md` `6`,
`radius-lg` `8`.

## Series palette

| Role | Default (light) | Default (dark) | Notes |
|---|---|---|---|
| `series-1` | `#7c8f6f` (sage) | `#9caf8f` | Non-focal series |
| `series-2` | `#5e7a9b` (dusty-blue) | `#82a0c0` | Non-focal series |
| `series-3` | `#b8915a` (mustard) | `#d3ad7a` | Non-focal series |
| `series-4` | `#9c6b50` (rust-brown) | `#b88670` | Non-focal series |
| `series-5` | `#6e6479` (slate) | `#8d8298` | Non-focal series |

## Typography

| Role | Family | Size | Weight | Usage |
|---|---|---|---|---|
| `title` | Instrument Serif | 1.75rem | 400 | Page H1 |
| `node-name` | Geist (sans) | 12px | 600 | Human-readable labels |
| `sublabel` | Geist Mono | 9px | 400 | Port, protocol, URL, field type |
| `eyebrow` | Geist Mono | 7–8px | 500, tracked 0.18em, uppercase | Type tags, axis labels |
| `arrow-label` | Geist Mono | 8px | 400, tracked 0.06em | Arrow annotations |
| `callout` | Instrument Serif *italic* | 14px | 400 | Editorial asides only |

### Font stack

```html
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

The `--font-*` declarations that go with it:

```css
--font-sans:  'Geist', system-ui, sans-serif;
--font-serif: 'Instrument Serif', serif;
--font-mono:  'Geist Mono', ui-monospace, monospace;
```

## Inversion rule

Any `rgba(45,49,66, X)` in light becomes `rgba(245,245,245, X)` in dark. Same opacities, RGB
flipped; the accent hue-shifts brighter to read on dark paper. This skin has no brand-supplied dark
palette, so the inversion rule is what generates its dark variant — the fallback path described in
[ADR-0008](../../../../docs/adr/0008-brand-dark-palettes-override-inversion.md).
