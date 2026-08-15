# Deck Build

Rendering a spine into a `.dc.html` deck against a design system. The format is
component-based: slides are `<section>` elements composed from design-system components
loaded from a global namespace.

---

## Project shape

```
deck/
  MyDeck.dc.html                  the deck: one <section> per slide
  MyDeck - Executive.dc.html      the walk-around version, same _ds
  spine.md                        source of truth
  diagrams/*.svg                  from the architecture-diagram skill
  support.js                      dc runtime (do not edit)
  deck-stage.js                   stage component (do not edit)
  _ds/<design-system>/            the design system
    styles.css                    entry point, @imports the tokens
    tokens/{colors,typography,spacing,effects,fonts}.css
    components/core/*.jsx
    _ds_manifest.json             namespace + component list
  CLAUDE.md                       project rules (house style)
```

Never edit `support.js` or `deck-stage.js`. They are generated runtime.

---

## Reading the design system first

Before writing any slide, read `_ds/<name>/_ds_manifest.json` for:

- `namespace`, e.g. `LabrynthDesignSystem_088180`. Every component reference is prefixed
  with it.
- `components`, the available primitives.

Then read `_ds/<name>/readme.md` for the voice, density, and visual rules. Design systems
carry content rules, not only visual ones (density limits, casing, whether emoji are
permitted), and those rules bind.

---

## Document skeleton

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="_ds/<DS>/tokens/fonts.css">
  <link rel="stylesheet" href="_ds/<DS>/tokens/colors.css">
  <link rel="stylesheet" href="_ds/<DS>/tokens/typography.css">
  <link rel="stylesheet" href="_ds/<DS>/tokens/spacing.css">
  <link rel="stylesheet" href="_ds/<DS>/tokens/effects.css">
  <link rel="stylesheet" href="_ds/<DS>/styles.css">
  <script src="_ds/<DS>/_ds_bundle.js"></script>
  <style>
    body { margin: 0; background: #080605; }
  </style>
</helmet>

<x-import component-from-global-scope="deck-stage" from="./deck-stage.js"
          width="1280" height="720" hint-size="100%,100%">

  <!-- one <section> per slide -->

</x-import>
</x-dc>
</body>
</html>
```

---

## The slide element

```html
<section data-label="Complication"
         data-screen-label="03"
         data-speaker-notes="The global multiplier. Governance dictates where data may live
                             and who may reach it, and today we resolve it by hand, per deal."
         style="display:flex; font-family:'Space Grotesk',sans-serif;">

  <x-import component-from-global-scope="<NS>.SlideFrame"
            page="3" total="26" style="width:100%;height:100%" hint-size="100%,100%">

    <x-import component-from-global-scope="<NS>.Eyebrow" hint-size="200px,20px">
      The Complication
    </x-import>

    <div style="height:14px;"></div>

    <x-import component-from-global-scope="<NS>.SlideTitle" hint-size="860px,100px">
      This bespoke engineering is exponentially compounded by the strict data governance
      required by our global client base.
    </x-import>

    <!-- body region -->

  </x-import>
</section>
```

| Attribute | Purpose |
|---|---|
| `data-label` | Short name for the slide, used in the navigator |
| `data-screen-label` | Zero-padded slide number |
| `data-speaker-notes` | The notes. Always present on a content slide. |
| `hint-size` | Layout hint for the editor. Approximate is fine. |

`Eyebrow` takes the kicker. `SlideTitle` takes the title. This mapping is the whole point:
the deck format has first-class slots for both halves of the spine unit.

---

## Common components

Names vary by design system; check the manifest. A typical core set:

| Component | Use |
|---|---|
| `SlideFrame` | 16:9 shell, background, page marker. Wraps every slide. |
| `Eyebrow` | The kicker |
| `SlideTitle` | The title. `size="hero"` on the cover. |
| `Subtitle` | Cover subtitle only |
| `Card`, `Card.Title`, `Card.Copy` | Body blocks |
| `ListRow` | List items with an accent marker |
| `AccentBlock` | Small square markers |
| `Divider` | Section rules |
| `PageMarker` | Page number |

Prefer design-system components over raw `div`s. Raw elements with inline styles are how a
deck drifts out of its own system: they do not pick up token changes, and by slide fifteen
the values have diverged. Use raw layout elements only for flex and grid scaffolding.

---

## Placing a diagram

Diagrams come from the `architecture-diagram` skill, rendered to the `slide` profile
(`0 0 1136 400`), which is exactly the content region beneath a kicker and a title.

```html
<div style="flex:1; display:flex; align-items:center; justify-content:center;">
  <img src="diagrams/cell-architecture.svg" alt="Products are deployed into sovereign cells:
       one AWS account per region, each running many products."
       style="width:100%; height:auto;">
</div>
```

Rules:

- The diagram's claim is the slide title, **verbatim**. The `alt` text is that claim.
- One diagram per slide.
- The diagram paints no background: the `SlideFrame` owns it.
- Map the deck's design tokens onto the diagram token contract, per
  `architecture-diagram/references/design-system.md`. Do not introduce a second palette.

Inlining the SVG rather than using `<img>` lets it inherit the deck's CSS variables directly,
which is preferable when the deck may be re-themed.

**Do not hand-build diagrams from flex rows of styled `div`s with text arrows.** It is the
fastest way to make a well-argued deck look unconsidered, and it is what the diagram skill
exists to prevent.

---

## Cover slide

```html
<section data-label="Cover" data-screen-label="01"
         data-speaker-notes="Frame the whole deck as a business transformation."
         style="display:flex; font-family:'Space Grotesk',sans-serif;">
  <x-import component-from-global-scope="<NS>.SlideFrame" page="1" total="26"
            style="width:100%;height:100%" hint-size="100%,100%">
    <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
      <x-import component-from-global-scope="<NS>.Eyebrow" hint-size="320px,20px">
        Labrynth Platform Strategy
      </x-import>
      <div style="height:20px;"></div>
      <x-import component-from-global-scope="<NS>.SlideTitle" size="hero" hint-size="760px,130px">
        From Bespoke Services to Exponential SaaS
      </x-import>
      <div style="height:24px;"></div>
      <x-import component-from-global-scope="<NS>.Subtitle" hint-size="620px,54px">
        Transitioning from building custom software per client to composing global,
        multi-tenant solutions, breaking the linear cost curve and unlocking
        compounding velocity.
      </x-import>
    </div>
    <div style="display:flex; gap:28px; font-size:14px; font-weight:600; color:var(--text-secondary);">
      <span>Problem</span><span>Pivot</span><span>Architecture</span>
      <span>Proof</span><span>Cloud &amp; scale</span>
      <span style="color:var(--accent-secondary);">Payoff</span>
    </div>
  </x-import>
</section>
```

The section-name row at the bottom is a useful device: it shows the arc on the cover, so the
audience knows the shape of the argument before it starts.

---

## Build order

1. Write and check `spine.md`
2. Scaffold every slide with kicker and title only, no bodies
3. **Read the deck through at this stage.** Structural problems are cheap to fix now and
   expensive after the bodies exist
4. Add bodies, following `references/body-content.md`
5. Brief and generate diagrams via the `architecture-diagram` skill
6. Add speaker notes
7. Audit against `references/spine-review.md`
8. Generate the executive version from the same spine

---

## Checks before delivery

```bash
# the narrative spine
node scripts/spine-check.mjs "deck/MyDeck.dc.html"

# the diagrams: source, render, and cross-slide coherence
AD=~/.claude/skills/architecture-diagram/scripts
node $AD/validate.mjs     deck/diagrams/*.svg
node $AD/verify.mjs       deck/diagrams/*.svg --out deck/.verify
node $AD/validate-set.mjs deck/diagrams/
```

**`validate-set` is the one that matters most for a deck.** Individually good diagrams that
disagree with each other are worse than mediocre ones that agree: if a cell is a hatched zone
on slide 17 and a plain box on slide 20, the viewer concludes they are different things and
quietly loses the thread. Just as the titles must read as one paragraph, the diagrams must
read as one system.

It checks that every diagram resolves the same tokens, that a role colour means the same
thing on every slide, that a recurring entity keeps its shape, that the shape key is taught
once rather than repeated, and that no two diagrams make the same claim.

Then **look at the screenshots** in `deck/.verify`. Measurement is not verification.

- [ ] `page` and `total` correct on every slide
- [ ] `data-screen-label` sequential
- [ ] Speaker notes on every content slide
- [ ] Every diagram's alt text equals its slide title
- [ ] No raw hex colours in slide markup where a token exists
- [ ] No em dashes
- [ ] Opens correctly in a browser at 1280x720
- [ ] Executive version regenerated from the same spine
