# Portable skin system and archetype roadmap

**Date:** 2026-08-14
**Status:** approved, not yet implemented
**Milestone:** M1 — portability + Inflection skin
**Repo:** `Inflection-Agents/diagram-design` (fork of `cathrynlavery/diagram-design`, MIT)

---

## 1. Context

A review of the skill at `v2.3` (upstream commit `a5e3978`) found two classes of problem.

**The skin cannot travel.** `style-guide.md` is a genuine single source of truth and `lint-skin.py`
validates against it, but nothing downstream honours that. A single example diagram carries 62 hex
literals and 22 `rgba()` literals inside its `<svg>`, and zero `var()` references — the `:root`
tokens in `template.html` style the page chrome only. The repo already contains the proof:
`scripts/lint-skin-baseline.txt` exempts 20 examples because they were built under an older skin
and were never migrated, and `style-guide.md` defers that migration to "a v5.1 task".

**The archetype library has gaps the skill itself depends on.** `SKILL.md` instructs the author to
"split into an overview + detail" in §3, §7, and §11, and provides no visual type that draws the
overview-to-detail relationship. Before/after comparison is similarly absent.

This document specifies M1 (portability) in full and records the roadmap for M2–M3 (archetypes).

### Decisions taken during design

| Decision | Choice | Rationale |
|---|---|---|
| Fork posture | Branded derivative; no upstream PRs | Frees us from ADR-0002's type freeze and the byte cap as hard limits |
| Token binding | `var()` everywhere, no flattening pass | Export already injects `<style>` into `<defs>`; see §6.3 |
| Canonical values | `style-guide.md`, skins generated from it | Mirrors the established `build-icons.py` + `git diff --exit-code` pattern |
| M1 scope | Portability + Inflection skin only | Portability touches all 104 examples; archetypes would collide in `SKILL.md` and the gallery |

### Non-goals for M1

- No new visual types or semantic patterns.
- No change to node-kind visual encoding, despite the defect recorded in §9. It is a
  visual-grammar change and therefore a separate concern.
- No per-project runtime skin resolution. The skin-swap procedure is documented and the
  alternate skin is archived; automatic per-directory resolution can follow if it is ever needed.

---

## 2. Fork and identity

The skill keeps the internal name `diagram-design` and the path `skills/diagram-design/`. Those
strings are load-bearing in `verify-plugin-package.py`, `verify-docs-sync.py`, both marketplace
manifests, `commands/`, and `prompts/`. Renaming the skill means touching all 16 gates for no
user-visible benefit. Only identity changes.

| File | Field | New value |
|---|---|---|
| `.claude-plugin/plugin.json` | `author`, `homepage`, `repository` | Inflection-Agents |
| `.codex-plugin/plugin.json` | as above, plus `interface.developerName`, `interface.websiteURL` | Inflection-Agents |
| `.codex-plugin/plugin.json` | `interface.brandColor` | `#967A3A` (was `#b5523a`) |
| `SECURITY.md` | private reporting path | Inflection Agents channel |
| `README.md` | new **Attribution** section | fork provenance, MIT, upstream credit |

**Licensing.** MIT permits the fork. `LICENSE` stays byte-identical with Cathryn Lavery's 2025
copyright line intact; our copyright line is added beneath it, never in place of it.
`THIRD_PARTY_LICENSES.md` is unchanged.

**Versioning.** Continue from `2.3.5`. `verify-plugin-package.py origin/main` compares against
`origin/main`, which after the fork is our own default branch, so the gate keeps working untouched.
M1 lands as `2.4.0` via `python3 scripts/bump-plugin-version.py --minor`.

**Process retained deliberately.** All 16 validation gates, the documentation-first structure, the
ADR practice, Conventional Commits, and branch-per-concern are kept. They are the reason this repo
is worth forking. ADR-0002's 27-type freeze is relaxed only at M2, and by a superseding ADR rather
than a silent edit.

---

## 3. The token contract

Every role becomes a `--dd-` prefixed CSS custom property. The prefix is required, not cosmetic:
these diagrams are embedded into slide decks and documentation pages, where an unprefixed
`--paper` would collide with the host page's own tokens.

### 3.1 Colour roles

Today's role set plus one addition (see below).

```
--dd-paper        --dd-ink        --dd-rule         --dd-accent
--dd-paper-2      --dd-muted      --dd-rule-solid   --dd-accent-tint
--dd-node-white   --dd-soft                         --dd-link
--dd-series-1 … --dd-series-5
```

**`--dd-node-white` is new, and it is a real hole rather than a nicety.** `SKILL.md` §5 specifies a
white fill for backend/API/step nodes, and no role names it — white survives today only because
`lint-skin.py`'s `allowed_colors()` hardcodes `{"#fff", "#ffffff"}` alongside the style-guide
palette. Under a token-only regime that literal has nowhere to live, so every backend node in the
system would have to carry a raw hex. Found during external design review, where all twelve option
files had to declare the token themselves to avoid a bare hex in an SVG attribute.

### 3.2 Wash roles (new)

The node-treatment table in `SKILL.md` §5 expresses fills as ink or muted at fixed opacity, which
appear as `rgba()` literals throughout the examples. These are promoted to named tokens rather than
computed with `color-mix()`, which keeps the linter simple and avoids a browser-support dependency.

| Token | Derived from | Used by |
|---|---|---|
| `--dd-wash-2` | `ink @ 0.02` | Optional / async node fill, zone fill |
| `--dd-wash-3` | `ink @ 0.03` | External / cloud node fill |
| `--dd-wash-5` | `ink @ 0.05` | Store / state node fill |
| `--dd-wash-10` | `muted @ 0.10` | Input / user node fill |
| `--dd-wash-20` | `ink @ 0.20` | Optional node stroke |
| `--dd-wash-30` | `ink @ 0.30` | External node stroke |

### 3.3 Geometry roles (new)

Forced by the Inflection brand, whose radius scale is `0 / 2 / 4 / 8` with square-edged buttons.
The skill's hardcoded `rx="6"` cannot express that register.

| Token | Default skin | Inflection skin |
|---|---|---|
| `--dd-radius-node` | `6` | `2` |
| `--dd-radius-tag` | `2` | `2` |
| `--dd-radius-container` | `8` | `4` |

The Inflection values are a taste call — the brand specifies component radius, not diagram
geometry — and should be reviewed against a rendered example in PR 4.

---

## 4. Architecture

```
style-guide.md ───build-skins.py──▶ assets/skins/active.tokens.css
  canonical:                          generated; CI enforces
  role contract +                     git diff --exit-code
  active skin values                          │
        │                                     │
        │                                     ▼
        └───lint-skin.py reads────▶  inlined into the :root block
            the same tables           of every generated .html
```

`style-guide.md` remains canonical and keeps its current table shape, so `lint-skin.py`'s existing
parser (`table_hexes`, `style_guide_families`) needs no rewrite. The upstream editorial skin is
archived to `references/skins/editorial-default.md` so switching back is a documented operation.
That archive is what makes "works with any design system" real rather than aspirational.

### 4.1 Output shape

Self-containment (`SKILL.md` §12) is preserved. The skin is **inlined**, never linked:

```html
<style>
  :root{
    --dd-paper:#F5F2EC; --dd-ink:#1B2B3C; --dd-accent:#967A3A;
    --dd-radius-node:2; /* … full contract … */
  }
  .dd-node{ rx:var(--dd-radius-node); }
</style>
...
<rect fill="var(--dd-paper)" stroke="var(--dd-ink)" rx="2" class="dd-node"/>
```

Colours ride `var()` in presentation attributes, which is universally supported. Radius rides a
CSS class **with the literal attribute retained as a fallback**: `rx` as a CSS geometry property is
solid in Chromium and Firefox but landed late in Safari, so the attribute guarantees correct
rendering everywhere while the token drives it where supported.

Reskinning an existing diagram becomes: replace the `:root` block. That is the entire win, and it
is precisely what the 20 baselined examples needed and never received.

---

## 5. The Inflection skin

Extracted from `https://inflectionagents.com/tokens.json` — a W3C DTCG file with a reference layer
and a semantic layer, so no inference from screenshots was required.

> The token file is headed *"Butterfly Investments · Inflection Agents brand tokens"*. Confirm this
> is the intended system before PR 4 lands.

### 5.1 Colour map, light

| Role | Brand token | Value | On paper | Note |
|---|---|---|---|---|
| `paper` | `surface.page` | `#F5F2EC` | — | Warm neutral; satisfies the not-pure-white rule |
| `paper-2` | `surface.divider` | `#EDE9E0` | — | |
| `ink` | `text.primary` | `#1B2B3C` | 12.90:1 | |
| `muted` | **substituted** `slate.mid` | `#4A6275` | 5.70:1 | See §5.4 |
| `soft` | `slate.base` | `#6E8799` | 3.36:1 | Sublabels only, never below 11px |
| `rule` | derived from ink | `rgba(27,43,60,0.14)` | — | |
| `rule-solid` | `neutral.stone` | `#C8C4BB` | — | |
| `accent` | `brand.accent` | `#967A3A` | 3.66:1 | Strokes and fills only — never small text |
| `accent-tint` | derived | `rgba(150,122,58,0.10)` | — | |
| `link` | `state.info` | `#3A5F8B` | 5.89:1 | |

### 5.2 Colour map, dark

The brand ships its own dark surfaces, so the inversion rule in `style-guide.md` is **not** applied.
This is settled by ADR-0008 (§8).

| Role | Brand token | Value | On dark paper |
|---|---|---|---|
| `paper` | `surface.deepest`-adjacent, `navy.deep` | `#0F1A26` | — |
| `paper-2` | `surface.dark` | `#1B2B3C` | — |
| `ink` | `neutral.ivory` | `#F5F2EC` | 16.94:1 |
| `muted` | `text.on-dark` / `stone` | `#C8C4BB` | 10.88:1 |
| `soft` | `slate.light` | `#A8BFCC` | 9.90:1 |
| `accent` | `brand.on-dark` / `gold.pale` | `#D4B97A` | 9.93:1 |
| `link` | derived (lightened steel) | `#8FB0DC` | — |

### 5.3 Series palette

The brand defines eight chart series; the contract caps at five, and brand `series-1` is navy,
which collides with `ink`. Mapping drops navy and takes the next five:

| Contract | Brand source | Value |
|---|---|---|
| `series-1` | `chart.series-2` | `#B0934B` |
| `series-2` | `chart.series-3` / `slate.mid` | `#4A6275` |
| `series-3` | `chart.series-4` / `sage.light` | `#7AAE8E` |
| `series-4` | `chart.series-5` / `amber` | `#C47A4A` |
| `series-5` | `chart.series-6` / `dusk` | `#6B5B8B` |

Dropped and recorded in the fidelity receipt: brand `series-1` (collides with `ink`), `series-7`,
`series-8` (beyond the cap).

### 5.4 Required substitution

The brand's `text.secondary` is ash `#8A8880`, which is **3.18:1** on ivory. `style-guide.md`
requires `muted` to reach 4.5:1, and the role is used at 8–9px for arrow labels and sublabels —
well below the 11px the constraint assumes. Slate-mid `#4A6275` reaches 5.70:1 and is inside the
brand's own secondary ramp, so nothing foreign is introduced.

Gold at **3.66:1** clears WCAG's 3:1 floor for graphical objects but not the 4.5:1 text floor. It is
therefore valid as a stroke or box fill and invalid for an 8px label.

**Both facts must appear in the brand fidelity receipt** that `onboarding.md` already specifies.
A substitution that lands silently is the failure mode this rule exists to prevent.

### 5.5 Typography

| Role | Family | Source |
|---|---|---|
| `title`, `callout` | Cormorant Garamond | exact |
| `node-name` | DM Sans | exact |
| `sublabel`, `eyebrow`, `arrow-label` | Geist Mono | **fallback, disclosed** |

The brand ships display, body, and a Chinese serif — no monospace. Per the exact-font gate in
`onboarding.md`, the mono role is labelled `fallback` rather than force-picking a face the brand
does not use. `lint-skin.py` reads allowed families from the style guide's Typography table, so
updating that table is sufficient; both new families are served from `fonts.googleapis.com/css2`
and therefore pass the existing single-file allowlist.

---

## 6. File-by-file changes

### 6.1 New — `scripts/build-skins.py`

Mirrors `scripts/build-icons.py` exactly, including the generated-file discipline. Reads the token
tables from `references/style-guide.md`, emits `skills/diagram-design/assets/skins/active.tokens.css`
and `skills/diagram-design/assets/skins/<name>.tokens.css` for archived skins. CI runs the script
then `git diff --exit-code` on the generated files.

Accompanied by `scripts/test-build-skins.py`, following the `test-build-icons-*.py` pattern.

### 6.2 Changed — `scripts/lint-skin.py`

1. Accept `var(--dd-*)` wherever a colour is currently accepted.
2. Verify each referenced token name exists in the contract; an unknown token is an error.
3. Continue rejecting raw hex and `rgba()` **outside** the `:root` block.
4. New **coverage check**: every role in the contract must be defined in the skin block. This is
   what prevents a half-written skin from shipping, and is the one idea worth borrowing from the
   neighbouring `architecture-diagram` skill.

Extend `scripts/test-lint-a11y.py`'s sibling cases for the new colour forms.

### 6.3 Changed — `references/export.md`

SVG export already injects a `<style>` block into `<defs>` to carry the Google Fonts `@import`
(step 3). The skin block is injected into that same `<style>`, so `var()` resolves in a standalone
`.svg`. PNG export rasterizes **the original HTML** in Chromium, where custom properties resolve
natively — no change required.

The existing renderer caveat (§"Caveat to surface to the user") is extended: consumers that do not
support CSS custom properties — older Illustrator, some Figma import paths, non-browser
rasterizers — will not resolve the palette, and PNG remains the recommendation for pixel-perfect
portability.

### 6.4 Changed — templates and examples

5 templates and 104 examples convert hex/`rgba()` literals to `var(--dd-*)`. Mechanical; see §7.

### 6.5 Changed — `SKILL.md`

§5 gains the wash and geometry roles; §6 primitive snippets switch to `var()`; §12 gains one
sentence on token binding. Measure against the 40,000-byte cap **before** opening the PR — current
headroom is 2,594 bytes.

---

## 7. Migration

Scope is all 104 examples and 5 templates, not only the 20 baselined files. The baselined subset is
simply the set that *also* fails the current palette.

**Success criterion: `scripts/lint-skin-baseline.txt` drops to zero entries.** CONTRIBUTING forbids
adding to that file; emptying it is the exact inverse, and it is the concrete proof that the skin
now travels.

The codemod maps known literals to role names using `style-guide.md` as the lookup. Ambiguities —
a hex serving two roles in different contexts — are reported for manual resolution rather than
guessed.

**PR 3 is visually identical by construction**: it substitutes tokens whose values are unchanged.
That makes it reviewable by diffing rasterized output rather than by reading 104 diffs, and it
isolates every pixel of visual change into PR 4 where it can be judged. Playwright is already the
PNG-export dependency, so the before/after comparison is a one-off script, not a permanent gate.

---

## 8. ADRs to write

| ADR | Settles |
|---|---|
| 0007 | Generated SVG binds colour through `--dd-*` tokens, not literals; skins are generated from `style-guide.md` |
| 0008 | Brand-supplied dark palettes override the inversion rule; inversion is the fallback |
| 0009 | Grid-versus-brand precedence: the 4px grid wins for geometry, the brand owns the type ramp |

ADR 0009 exists because the Inflection ramp is `10 / 12 / 15 / 18 / 24 / 32 / 48 / 64`, of which
10, 15, and 18 are not divisible by four, while `SKILL.md` §7 calls that rule non-negotiable. The
recommendation is that a diagram set which does not share its brand's text sizes reads as foreign
no matter how well the boxes align, so the brand wins for type while coordinates stay on the grid.

---

## 9. Known defects carried forward

Recorded here so they are not mistaken for regressions introduced by M1.

**Node kind is encoded almost entirely by hue.** The seven node treatments separate mainly by fill
opacity at 2–5% of ink. Composited over paper, ten of the fifteen pairs fall below 1.10:1 —
`store` against `external` is 1.04:1, `optional` against bare paper is 1.04:1. In greyscale or on a
projector those fills are identical, so kind is carried by stroke hue alone. `SKILL.md` forbids
exactly this for status ("state is never color-only") and then relies on it for kind.

The mechanical migration preserves this defect. Fixing it is a visual-grammar change, scheduled for
M3 together with a greyscale render gate.

---

## 10. PR sequence

| PR | Concern | Visual change | Gates |
|---|---|---|---|
| 1 | Fork identity, attribution, SECURITY | none | full suite |
| 2 | Token contract, `build-skins.py`, 5 templates, linter support + tests | none | full suite + new build gate |
| 3 | Codemod 104 examples to `var()`, empty the baseline | **none — pure refactor** | full suite + raster diff |
| 4 | Inflection skin values, fonts, ADRs 0007–0009 | **all of it** | full suite |
| 5 | `export.md` skin injection + caveat | none | full suite |

Each PR bumps both plugin manifests via `scripts/bump-plugin-version.py`.

---

## 11. Risks

| Risk | Mitigation |
|---|---|
| Safari's late support for CSS `rx` | Literal `rx` attribute retained as fallback |
| `muted` substitution lands silently | Required entry in the brand fidelity receipt (§5.4) |
| `SKILL.md` exceeds the 40,000-byte cap | Measure before opening PR 2; 2,594 bytes headroom today |
| Codemod mis-maps an ambiguous literal | Ambiguities reported, not guessed; PR 3 raster diff catches drift |
| Brand identity mismatch ("Butterfly Investments") | Confirm before PR 4 |

---

## 12. Roadmap beyond M1

**M2 — archetypes.** Six new visual types after two external design passes: Zoom, Contrast,
Lineage, Matrix, Composition, and Deployment. Each ships with a reference, three example variants,
gallery registration, and a superseding ADR relaxing ADR-0002. Zoom is the priority: the skill
already instructs authors to split into overview and detail in three places without providing the
grammar.

Two proposed archetypes cost nothing. **Matrix** retires `type-dp-security-matrix` to a preset of
itself, so the net type count is unchanged. **Hub & spoke** came back as a grammar rather than a
type — Architecture already draws it; what was missing were conventions — so it becomes a semantic
pattern. Final count: 27 → 32. See `2026-08-14-design-review-pass-2.md`. Appendix A is the original
design brief.

**M3 — visual grammar.** Node-kind encoding is now specified: the type tag becomes mandatory and
load-bearing, paired with a corner notch for distance; fills stop signifying. Applies retrospectively
to all 32 types and all 104 examples, so it must land *after* M1 in its own PR — M1's migration is
verified by raster-identity, which a tag sweep would destroy. Blocked on a notch primitive. Add the
greyscale render gate here too. See `2026-08-14-design-review-pass-3.md`.

**Code level.** Lands as a rename-and-generalize of `type-er.md` into one type with an entity preset
and a class preset, unified by a text token at each relationship endpoint. Costs no new type.

**M4 — semantic patterns.** At pattern cost (one section plus a routing row each): Agent/tool/memory
loop, Control plane vs data plane, Tenancy isolation, Blast radius, Multi-region failover,
Environment promotion, Latency budget, Event backbone guarantees, Scaling.

---

## Appendix A — Claude Design brief: Zoom and Contrast

Use this as the prompt packet when exploring layouts for the M2 archetypes. It is deliberately
specific about constraints, because the value of generated options here is in the *layout grammar*,
not the styling — the styling is already settled by the token contract.

### A.1 Shared constraints (apply to both)

> You are designing a new diagram archetype for an editorial diagramming system. Output is a
> self-contained HTML file with inline SVG. Produce 4–6 genuinely different layout options, not
> variations on one idea.
>
> **Non-negotiable constraints:**
> - Every coordinate, font size, node dimension, and gap is divisible by 4.
> - Connectors between nodes that do not share an x or y axis use rounded right-angle elbows with
>   `r=8`. Diagonal lines are an automatic fail.
> - Arrow labels sit 6–10px clear of their connector, over an opaque mask rect, never on the line,
>   never vertical text.
> - No two connectors overlap or share an attach point; connectors entering the same box edge are
>   fanned ≥12px apart.
> - Maximum 9 nodes, 12 connectors, 2 accent elements per diagram.
> - No shadows, no gradients, no glow. Borders only. Border radius 0–8px.
> - The `<svg>` carries `role="img"` and `aria-labelledby` naming a first-child `<title>` and a
>   `<desc>` that describes content rather than geometry.
> - All colour comes from these tokens; never invent a colour:
>   `--dd-paper #F5F2EC`, `--dd-paper-2 #EDE9E0`, `--dd-ink #1B2B3C`, `--dd-muted #4A6275`,
>   `--dd-soft #6E8799`, `--dd-accent #967A3A`, `--dd-link #3A5F8B`,
>   `--dd-rule rgba(27,43,60,0.14)`.
> - Type: Cormorant Garamond for the title, DM Sans for node names (12px/600), monospace for
>   technical sublabels (9px) and arrow labels (8px, uppercase, tracked).
> - Accent appears on at most 2 elements. It is editorial emphasis, not a signalling system.
>
> **Evaluate each option against:** can a reader reconstruct the relationship without the caption;
> does it hold at 50% scale; does it survive greyscale; does it still work with the maximum node
> count.

### A.2 Zoom — overview and detail

> **What it must prove:** "the box you already saw contains this."
>
> The diagram shows a reduced reproduction of a parent diagram with one element marked, and an
> expansion of that element occupying the majority of the canvas. The visual correspondence between
> the marked element and the expansion is the entire content of the archetype — if a reader cannot
> instantly tell which box was opened, the diagram has failed.
>
> **Properties to explore:**
> - How the parent is reduced: true scale reduction, schematic abstraction, or a simplified
>   silhouette. Reduction must keep the marked box identifiable.
> - How correspondence is drawn: a connector, a wedge or frustum joining the marked box to the
>   expansion's frame, matching stroke treatment, or a shared label.
> - Where the parent sits: corner inset, left rail, top strip. Each implies a different reading
>   order.
> - How the parent is made visibly quiet without becoming illegible — it is orientation, not
>   content.
> - Whether the expansion gets its own frame or bleeds to the canvas edge.
>
> **Failure modes to avoid:** a parent thumbnail so small the marked box cannot be identified; a
> parent redrawn differently from the original, breaking continuity; the parent competing with the
> expansion for attention; correspondence implied by position alone.

### A.3 Contrast — before and after

> **What it must prove:** "the current state is broken and the proposed state is better."
>
> Two panels of identical width and identical internal structure. The mirroring is the argument:
> because the panels are structurally the same, the single difference between them becomes
> unmissable. Panels are labelled with states (`Today` / `Proposed`), never judgements.
>
> **Properties to explore:**
> - The divider: hairline rule, gutter alone, or a labelled transition marker between panels.
> - How the difference is marked — accent on the changed element in the right panel only, while the
>   left panel reads as entirely ordinary.
> - Whether a delta ledger (a short list of what changed) earns its place, and where it sits.
> - How structural parity is made visually obvious — aligned baselines across panels, matched node
>   sizes, shared row positions.
> - Handling the case where the right panel has fewer nodes than the left, which is the most common
>   real shape of this argument.
>
> **Failure modes to avoid:** panels with different internal structure, which makes them
> undiffable; strawmanning the left panel by making it uglier or more crowded than reality;
> highlighting both panels, which destroys the baseline; three panels — a third state is a pipeline
> of states, not a contrast.
