# ADR 0008 — A brand's own dark palette overrides the inversion rule

**Status:** accepted (v2.4)

## Context

`style-guide.md` has always derived the dark skin mechanically: flip ink and paper, keep the opacities, hue-shift the accent brighter. That works when a brand ships only a light palette, which is the case the rule was written for.

The Inflection Agents tokens ship their own dark surfaces — `navy.deep` paper, `neutral.ivory` ink, `gold.pale` accent, `slate.light` soft. Inverting the light palette instead would have produced a near-black paper the brand does not use and a gold that the brand had already tuned for dark ground.

## Decision

When a brand supplies dark values, take them. The inversion rule is the **fallback** for brands that do not, and `style-guide.md` now says so at the point of use. The dark column of each token table is authoritative regardless of how it was arrived at, so `build-skins.py` needs no notion of derivation — it reads two columns and emits two variants.

## Consequences

- The dark skin is as much a brand artifact as the light one, and the fidelity receipt records which dark values were taken exactly and which were derived. For this skin, `rule`, `rule-solid`, `accent-tint`, and the five dark series values are derived; the seven surface and text roles are the brand's own.
- A skin with no dark palette still works: fill the dark column by inversion and the generator is none the wiser.
- Contrast must be measured against the brand's dark paper, not assumed from the light measurements. All five dark text roles clear 9.9:1 on `navy.deep` — better than their light counterparts.
- The archived editorial skin keeps the inversion rule in its own file, which is the reference implementation of the fallback path.
