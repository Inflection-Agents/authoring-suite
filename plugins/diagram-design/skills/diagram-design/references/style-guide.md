# Style Guide

**The single source of truth for colors, typography, and tokens.** Every diagram draws from this — not from hex values inlined in other reference files. If you want to change the visual skin of Diagram Design, change this file.

Default skin is the Inflection Agents brand — ivory paper, navy ink, gold accent, slate-mid muted. Swap these values (or run [`onboarding.md`](onboarding.md)) and every new diagram inherits the new skin without touching any type-specific logic: colour binds through `--dd-*` custom properties, so a reskin is one `:root` block, not one edit per attribute.

To generate your own from a website URL, see [`onboarding.md`](onboarding.md).

---

## Tokens

### Semantic roles

Every token is referred to by **semantic role**, not by its hex value. Type references (`type-*.md`) and SKILL.md say `accent`, not `#f7591f`.

| Role | Purpose | Default (light) | Default (dark) |
|---|---|---|---|
| `paper` | Page background, default node fill | `#F5F2EC` (ivory) | `#0F1A26` (navy-deep) |
| `paper-2` | Diagram container bg, secondary fill | `#EDE9E0` (divider) | `#1B2B3C` (navy) |
| `node-white` | Backend / API / step node fill | `#ffffff` | `#ffffff` |
| `ink` | Primary text, primary stroke | `#1B2B3C` (navy) | `#F5F2EC` (ivory) |
| `muted` | Secondary text, default arrow stroke | `#4A6275` (slate-mid) | `#C8C4BB` (stone) |
| `soft` | Sublabels, boundary labels | `#6E8799` (slate-base) | `#A8BFCC` (slate-light) |
| `rule` | Hairline borders | `rgba(27,43,60,0.14)` | `rgba(245,242,236,0.14)` |
| `rule-solid` | Stronger borders, baselines | `#C8C4BB` (stone) | `rgba(200,196,187,0.25)` |
| `accent` | Focal / 1–2 max per diagram | `#967A3A` (gold) | `#D4B97A` (gold-pale) |
| `accent-tint` | Fill for accent-bordered boxes | `rgba(150,122,58,0.10)` | `rgba(212,185,122,0.10)` |
| `link` | HTTP/API calls, external arrows | `#3A5F8B` (steel) | `#8FB0DC` (steel-light) |

> **Brand palette source:** the Inflection Agents design tokens, a W3C DTCG file with a reference
> layer and a semantic layer. `muted` is a documented substitution and `accent` is not usable for
> small text — both are recorded in the [brand fidelity receipt](#brand-fidelity-receipt) below,
> which you should read before changing any value here.

> **The previous skin is archived,** not deleted: [`skins/editorial-default.md`](skins/editorial-default.md)
> holds the upstream editorial palette and the procedure for restoring it.

### Wash roles

Fixed-opacity derivations used by the node-treatment table. Named rather than computed, so the
seven treatments in [Node type → treatment](#node-type--treatment) are one token each. Shades
*outside* that table — a 55% ink rule, a 22% accent band — are written
`color-mix(in srgb, var(--dd-ink) 55%, transparent)`, which resolves to exactly the `rgba()` it
replaces. Do not add wash roles for one-off opacities.

| Role | Derived from | Default (light) | Default (dark) |
|---|---|---|---|
| `wash-2` | `ink @ 0.02` | `rgba(27,43,60,0.02)` | `rgba(245,242,236,0.02)` |
| `wash-3` | `ink @ 0.03` | `rgba(27,43,60,0.03)` | `rgba(245,242,236,0.03)` |
| `wash-5` | `ink @ 0.05` | `rgba(27,43,60,0.05)` | `rgba(245,242,236,0.05)` |
| `wash-10` | `muted @ 0.10` | `rgba(74,98,117,0.10)` | `rgba(200,196,187,0.10)` |
| `wash-20` | `ink @ 0.20` | `rgba(27,43,60,0.20)` | `rgba(245,242,236,0.20)` |
| `wash-30` | `ink @ 0.30` | `rgba(27,43,60,0.30)` | `rgba(245,242,236,0.30)` |

### Geometry roles

Radius is tokenized so a brand with a sharper corner register can be expressed — this skin's is
`0 / 2 / 4 / 8` with square-edged buttons, which the old hardcoded `rx="6"` could not say.
`radius-node`, `radius-tag`, and `radius-container` restate `radius-md`, `radius-sm`, and
`radius-lg` from [Stroke, radius, spacing](#stroke-radius-spacing) under their contract names and
must be kept in step with them.

Diagrams carry the token on a class (`dd-node`, `dd-tag`, `dd-container`) and keep the literal `rx`
attribute as a fallback, because `rx` as a CSS geometry property landed late in Safari.

| Role | Default | Use |
|---|---|---|
| `radius-node` | `2` | Node boxes |
| `radius-tag` | `2` | Type tags, label masks |
| `radius-container` | `4` | Zones, rings, containers |

### Inversion rule (light → dark)

**Only a fallback.** This skin ships its own dark surfaces — navy-deep paper, ivory ink, gold-pale
accent — so the dark column above is taken from the brand, not derived. See
[ADR-0008](../../../docs/adr/0008-brand-dark-palettes-override-inversion.md).

For a skin with no dark palette of its own, invert: any `rgba(<ink>, X)` in light becomes
`rgba(<dark ink>, X)` in dark, same opacities, and the accent hue-shifts brighter to read on dark
paper.

### Series palette (multi-series chart types only)

A small set of desaturated, editorial-tone colors for chart types that genuinely need to distinguish multiple overlapping entities (currently: **radar**). The "1-focal" rule still holds — `accent` is reserved for the focal series; the palette below covers the rest.

| Role | Default (light) | Default (dark) | Notes |
|---|---|---|---|
| `series-1` | `#B0934B` (gold-deep) | `#C8B483` | Non-focal series |
| `series-2` | `#4A6275` (slate-mid) | `#86949F` | Non-focal series |
| `series-3` | `#7AAE8E` (sage-light) | `#A5C6AF` | Non-focal series |
| `series-4` | `#C47A4A` (amber) | `#D5A483` | Non-focal series |
| `series-5` | `#6B5B8B` (dusk) | `#9B90AD` | Non-focal series |

Fills sit at `0.18` opacity light, `0.22` dark; strokes use the full color. **Don't backfill these tokens to non-chart types** — architecture, swimlane, etc. continue to use muted-ink variants. The series palette is opt-in for diagrams where overlapping shapes demand distinguishable color, not a license to add color elsewhere.

### Terminal skin (opt-in alternate)

A self-contained palette for the terminal-window primitive (see [primitive-terminal.md](primitive-terminal.md)) — a CLI-chrome register for dev-tool posts and technical social cards. It does not replace the default skin above and isn't affected by onboarding; it's a second, fixed skin you opt into per-diagram.

| Token | Hex | Purpose |
|---|---|---|
| `terminal-page` | `#0a0a0a` | Page background behind the window |
| `terminal-paper` | `#141414` | Window body, node fill |
| `terminal-bar` | `#1b1b1b` | Titlebar strip |
| `terminal-border` | `#2b2b2b` | Window border, hairlines |
| `terminal-ink` | `#f5f5f5` | Primary text, primary stroke (white-smoke; the terminal skin keeps its own value) |
| `terminal-muted` | `#9a9a9a` | Secondary text, sublabels, ring stroke |
| `terminal-soft` | `#5c5c5c` | Tertiary — inactive dots, spokes |
| `terminal-accent` | `#ff5a36` | The one accent — focal station, prompt sign, active dot |
| `terminal-accent-tint` | `rgba(255,90,54,0.12)` | Fill for accent-bordered boxes |

**1-accent rule still holds.** Everything that isn't `terminal-ink` or `terminal-muted`/`terminal-soft` should be `terminal-accent` — never introduce a second hue.

---

## Typography

| Role | Family | Size | Weight | Usage |
|---|---|---|---|---|
| `title` | Cormorant Garamond | 1.75rem | 400 | Page H1 |
| `node-name` | DM Sans | 12px | 600 | Human-readable labels |
| `sublabel` | Geist Mono | 9px | 400 | Port, protocol, URL, field type |
| `eyebrow` | Geist Mono | 7–8px | 500, tracked 0.18em, uppercase | Type tags, axis labels |
| `arrow-label` | Geist Mono | 8px | 400, tracked 0.06em | Arrow annotations |
| `callout` | Cormorant Garamond *italic* | 14px | 400 | Editorial asides only |

### Font stack

```html
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

**Load-bearing rule:** Mono is for *technical* content (ports, commands, URLs, field types). Names go in DM Sans. Page title is Cormorant Garamond. Italic Cormorant Garamond is reserved for annotation callouts (see [primitive-annotation.md](primitive-annotation.md)). **Never JetBrains Mono** as a blanket "dev" font.

Geist Mono is a **disclosed fallback**: the brand ships display, body, and a Chinese serif, but no
monospace. Per the exact-font gate in [`onboarding.md`](onboarding.md) the role is labelled rather
than filled with a face the brand does not use.

---

## Stroke, radius, spacing

| Token | Value | Use |
|---|---|---|
| `stroke-thin` | `0.8` | Tag-box outlines, leaf nodes |
| `stroke-default` | `1` | Most strokes |
| `stroke-strong` | `1.2` | Emphasis strokes |
| `radius-sm` | `2` | Small tags |
| `radius-md` | `2` | Node boxes |
| `radius-lg` | `4` | Containers, rings |
| `grid` | `4` | Every coord, size, and gap is divisible by 4 (hard rule) |

---

## Node type → treatment

Semantic role combinations — reference these by name in type specs. `Notch` is the second kind
channel for the diagram families where a kind taxonomy applies at all — see
[`primitive-notch.md`](primitive-notch.md) for scope, the primitive, and why `optional`/`security`/
`focal` inherit rather than carry their own count.

| Type | Fill | Stroke | Notch |
|---|---|---|---|
| `focal` (1–2 max) | `accent-tint` | `accent` @ **1.6** stroke-width | inherits base kind, else 0 |
| `backend` | `#ffffff` (white) | `ink` | 0 |
| `store` | `ink @ 0.05` | `muted` | 1 (top-right) |
| `external` | `ink @ 0.03` | `ink @ 0.30` | 2 (top-right, bottom-right) |
| `input` | `muted @ 0.10` | `soft` | 2 (top-right, bottom-right) |
| `optional` | `ink @ 0.02` | `ink @ 0.20` dashed `4,3` | inherits base kind |
| `security` | `accent @ 0.05` | `accent @ 0.50` dashed `4,4` | inherits base kind, else 2 |

---

## Brand fidelity receipt

Every skin onboarded from a brand records what was taken exactly, what was substituted, and what was
dropped. A substitution that lands silently is the failure this receipt exists to prevent. This is
the receipt for the active skin.

**Source.** The Inflection Agents design tokens (`inflectionagents.com/tokens.json`), a W3C DTCG
file with a reference layer and a semantic layer, so no value was inferred from a screenshot.

**Provenance caveat.** The token file is headed *"Butterfly Investments · Inflection Agents brand
tokens"*. The values below are used as published; if that heading means the palette belongs to a
different system, the fix is to replace the tables above and rerun `scripts/build-skins.py` — which
is a single-block edit by construction.

### Taken exactly

`surface.page`, `surface.divider`, `text.primary`, `slate.base`, `neutral.stone`, `brand.accent`,
`state.info`, `navy.deep`, `surface.dark`, `neutral.ivory`, `text.on-dark`, `slate.light`,
`brand.on-dark`, and chart series 2 through 6. Cormorant Garamond and DM Sans are the brand's own
display and body faces.

### Substituted — `muted`

The brand's `text.secondary` is ash `#8A8880`, which measures **3.18:1** on ivory. This guide
requires `muted` to reach 4.5:1, and the role is used at 8–9px for arrow labels and sublabels —
well below the 11px the constraint assumes. Slate-mid `#4A6275` reaches **5.70:1** and sits inside
the brand's own secondary ramp, so nothing foreign is introduced.

### Limited — `accent` is not a text colour

Gold `#967A3A` measures **3.66:1** on ivory. That clears WCAG's 3:1 floor for graphical objects, so
it is valid as a stroke or a box fill, and it fails the 4.5:1 text floor, so it is **invalid for an
8px label**. Accent text must be `ink`; the accent carries focus through stroke and fill instead.

### Disclosed fallback — the mono role

The brand ships display, body, and a Chinese serif, and no monospace. Geist Mono is retained for
`sublabel`, `eyebrow`, and `arrow-label` and labelled a fallback rather than force-picking a face
the brand does not use.

### Dropped

- Brand `chart.series-1` — navy, collides with `ink`.
- Brand `chart.series-7` and `chart.series-8` — beyond the contract's cap of five series.

### Derived

- `rule` and the `wash-*` roles: `ink` and `muted` at fixed opacity, as before.
- `accent-tint`: `accent` at 0.10.
- Dark `rule`, `rule-solid`, and `accent-tint`: the same derivations against the dark values.
- Dark series: each light series mixed 35% toward `neutral.ivory`, because the brand publishes one
  chart ramp and it is too dark to read on navy paper.

### Measured contrast

| Pair | Ratio | Verdict |
|---|---|---|
| `ink` on `paper` | 12.90:1 | AA and AAA |
| `muted` on `paper` | 5.70:1 | AA at any size |
| `soft` on `paper` | 3.36:1 | Sublabels at 11px+ only |
| `accent` on `paper` | 3.66:1 | Graphical objects only, never text |
| `link` on `paper` | 5.89:1 | AA at any size |
| `ink` on dark `paper` | 16.94:1 | AA and AAA |
| `muted` on dark `paper` | 10.88:1 | AA at any size |
| `soft` on dark `paper` | 9.90:1 | AA at any size |
| `accent` on dark `paper` | 9.93:1 | AA at any size |

---

## Customizing the skin

Three options:

1. **Run onboarding** — see [`onboarding.md`](onboarding.md). Drop a URL; the skill extracts the palette + fonts and rewrites this file.
2. **Edit by hand** — change the hex values in the tables above. Run the pre-output taste gate afterward to verify the accent still reads as "focal" against the new paper color.
3. **Brand handoff** — paste your existing design-token JSON into a new section here and map its tokens to the semantic roles above.

### Constraints (don't break these)

- **Contrast**: `ink` must hit WCAG AA on `paper`. `muted` must hit AA on `paper` for 11px+ text.
- **One accent**: pick one color for `accent`. Two accents erases the focal signal.
- **No rainbow palette**: if your brand ships 8 colors, pick 3 (paper, ink, accent). The rest become `muted` variants.
- **Serif + sans + mono**: three families, not more. If brand typography is all sans, keep a serif for `title` and `callout` anyway — the contrast is load-bearing.
- **Paper is warm-neutral, not pure white**: pure white turns the design sterile. Pick a cream, bone, or light grey with a hint of warmth.
- **Dot pattern is optional, not default**: the 22×22 dot pattern is an opt-in "dotted paper" variant (good for long-form editorial hero diagrams). The default background is a clean `paper` fill, no pattern. When the pattern is enabled, it should sit at ~10% opacity of `ink` on `paper` — visible but quiet.
- **Container is clean by default**: the diagram sits directly on the page paper, no secondary container background or border. A framed variant (`paper-2` bg + `rule` border + 8px radius + padding) is available as an opt-in for card-heavy layouts, but don't reach for it by default — the extra chrome fights the figure.
