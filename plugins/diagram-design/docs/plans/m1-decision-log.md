# M1 decision log

Decisions taken while executing `2026-08-14-m1-portable-skin.md` where the plan was silent,
ambiguous, or wrong. Each entry records the choice, why, the rejected alternative, and how to
reverse it. Entries are committed with the PR that contains the decision.

---

## D1 — The version line continues from 2.3.8, not 2.3.5

**PR:** 1

**Choice.** PR 1 bumps to `2.3.9`. The plan (Task 3, Step 1) and design doc §2 both say the fork
continues from `2.3.5` and that PR 1 produces `2.3.6`; the repository is actually at `2.3.8` because
three Phase-0 PRs landed after the design was written.

**Why.** `verify-plugin-package.py origin/main` requires the version to be strictly greater than the
base branch's. Following the plan's literal number would fail that gate. The plan's intent — one
patch bump per PR, one minor bump for a feature PR — is preserved.

**Rejected.** Setting the manifests to 2.3.6 as written. That fails the monotonic-version gate and
misrepresents the release history.

**Reverse.** Edit the `version` key in both manifests; nothing else references it.

---

## D2 — Attribution is appended below `## About`, and `## About` is left intact

**PR:** 1

**Choice.** The new `## Attribution` section goes at the end of `README.md`, after the existing
`## About` section, which still credits Cathryn Lavery.

**Why.** `verify-docs-sync.py` validates the README's Architecture tree; appending below it is the
safe insertion point the plan anticipated (Task 2, Step 4). Rewriting `## About` was not asked for
and would remove upstream credit that the MIT attribution obligation is better served by keeping.

**Rejected.** Replacing `## About` with an Inflection Agents bio. That is an identity decision beyond
PR 1's stated scope of "attribution and contact", and it deletes the clearest statement of who wrote
the original work.

**Reverse.** Edit `README.md`; no gate depends on either section's contents.

---

## D3 — Coverage is enforced only on files that bind through the contract

**PR:** 2

**Choice.** `lint-skin.py` requires the full 25-role skin block only in files that reference at least
one `var(--dd-*)`. A file with no token references is unaffected.

**Why.** Design doc §6.2 item 4 specifies a coverage check — "every role in the contract must be
defined in the skin block" — as the thing that stops a half-written skin shipping. The M1 plan's
Task 7 implements only token-name validation and does not mention coverage. Enforcing coverage
unconditionally would demand a full `--dd-*` block in `template-terminal.html`, which the plan
(Task 8, Step 1) explicitly puts out of scope because the terminal skin is a separate fixed palette.
Gating on "does this file use the contract at all" keeps the design's guarantee and the plan's
exclusion at the same time.

**Rejected.** Unconditional coverage on every linted file. That forces a 25-role block into the
terminal template, where 23 of the roles would be unused and misleading.

**Reverse.** Delete the `if referenced_tokens:` guard in `lint_text` to make the check
unconditional, or delete the block entirely to drop coverage.

---

## D4 — `build-skins.py` is a runtime dependency of `lint-skin.py`

**PR:** 2

**Choice.** `lint-skin.py` imports `CONTRACT` from `scripts/build-skins.py` at module load, as the
plan directs. `test-lint-a11y.py`'s sandboxed-project fixture now copies `build-skins.py` alongside
the linter.

**Why.** The plan says "import the contract from the builder rather than duplicating it — a second
copy will drift". The consequence it does not mention is that the existing test builds a throwaway
project containing only `lint-skin.py` and `style-guide.md`; without the builder the linter cannot
import and three test cases fail with a `FileNotFoundError` that reads as a linter bug. Copying the
file states the dependency honestly.

**Rejected.** A silent fallback to a hardcoded contract when `build-skins.py` is absent. That is the
exact drift the single-definition rule exists to prevent, and it would fail open.

**Reverse.** Inline `CONTRACT` into `lint-skin.py` and drop the `shutil.copy2` in the test — at the
cost of two definitions.

---

## D5 — The Series palette table header is renamed to `| Role | Default (light) | Default (dark) |`

**PR:** 2

**Choice.** `style-guide.md`'s series table header changes from `| Token | Light | Dark | Notes |`
to `| Role | Default (light) | Default (dark) | Notes |`.

**Why.** The plan's `read_roles()` latches column headers from lines beginning `| Role |` and
carries them forward. The series table's own header does not match, so its five rows would have been
parsed against whichever role table appeared last — the geometry table, whose single value column
would have mapped `series-1` light to the string `#7c8f6f` (sage)` and produced no dark value at all.
Making the header uniform is a one-line fix at the source of truth rather than a special case in the
parser.

**Rejected.** Teaching `read_roles()` about `| Token |` headers. That preserves an inconsistency in
the canonical document and makes the parser carry it forever. `lint-skin.py` reads the series table
by scanning for hex literals, so it is indifferent to the header text.

**Reverse.** Restore the old header row and add a `| Token |` branch to `HEADER_RE`.

---

## D6 — Translucent shades with no named role use `color-mix()`

**PR:** 2

**Choice.** A colour literal that exactly equals a contract role becomes `var(--dd-<role>)`. A
translucent literal whose RGB triplet belongs to a role but whose opacity has no named wash becomes
`color-mix(in srgb, var(--dd-<role>) <alpha>%, transparent)`.

**Why.** The plan and design doc name six wash roles, which cover the node-treatment table in
`SKILL.md` §5. The assets actually contain **about ninety** distinct opacity/colour combinations —
`rgba(45,49,66,0.55)`, `rgba(235,108,54,0.80)`, and so on. Leaving those literal would have broken
the milestone's whole point twice over: a `:root` swap would not reach them, and once PR 4 removes
`#2d3142` from the palette the linter would reject every one of them. `color-mix` with `transparent`
in sRGB reproduces the source `rgba()` exactly — the raster comparison in Task 13 confirms this
across all 102 files — so the substitution is value-preserving.

The design doc §3.2 does say the wash roles are "named rather than computed … [to avoid] a
browser-support dependency". That reasoning applies to the six *documented node treatments*, which
remain named tokens. It was not a ruling on the long tail, which the design doc does not mention.

**Rejected.** (a) Expanding the contract with ~90 more roles — unreadable, and the contract is fixed
at 25 by design. (b) `fill-opacity` / `stroke-opacity` attributes — equally exact and better
supported, but it needs attribute surgery on every element and composes wrongly wherever an element
already carries `opacity`, and it does not work in the CSS rules outside the `<svg>`.

**Reverse.** `color-mix` expressions are mechanically recognisable; a script can convert them back to
`rgba()` by resolving the role against `active-*.tokens.css`.

---

## D7 — Geometry tokens are emitted with a `px` unit

**PR:** 2

**Choice.** `build-skins.py` appends `px` to the three geometry roles when generating the CSS, so
`radius-node: 6` in the style guide becomes `--dd-radius-node: 6px`.

**Why.** The plan's Task 8 Step 3 adds `.dd-node { rx: var(--dd-radius-node); }`. The CSS `rx`
geometry property requires a `<length-percentage>`; a unitless `6` is invalid, so the declaration
would have been dropped by every browser and the rule would have silently done nothing — masked by
the literal `rx="6"` fallback the same step keeps. In SVG user space `1px` is one user unit, so
`rx: 6px` and `rx="6"` are the same corner. The style guide keeps the bare number, matching the SVG
attribute it documents.

**Rejected.** `rx: calc(var(--dd-radius-node) * 1px)` — keeps the token unitless and CSS-usable, but
puts a `calc` in every generated file to work around a formatting choice in the generator.

**Reverse.** Delete `LENGTH_ROLES` from `build-skins.py` and rerun it.

---

## D8 — A third radius class, `dd-container`, is added

**PR:** 2

**Choice.** The generated radius rules are `.dd-node`, `.dd-tag`, **and** `.dd-container`, mapping
literal `rx="6"`, `rx="2"`, and `rx="8"` respectively.

**Why.** The plan's Task 8 Step 3 lists only `.dd-node` and `.dd-tag`, but the contract has three
geometry roles and `radius-container` is the one the Inflection skin changes most (8 → 4). Without a
class, every zone, ring, and container would have kept a hardcoded 8px corner through PR 4 and the
brand's sharper register would have reached only half the geometry.

**Rejected.** Leaving containers on the literal attribute. That silently exempts them from the skin.

**Reverse.** Drop the rule from `RADIUS_RULES` in `scripts/migrate-to-tokens.py` and re-run it.

---

## D9 — The terminal skin is skipped by file, not by hand

**PR:** 2

**Choice.** `migrate-to-tokens.py` refuses to touch any file whose name contains `terminal`, and
prints that it skipped it. That is `template-terminal.html` and `example-loop-terminal.html`.

**Why.** The plan (Task 8, Step 1) says not to convert the terminal template's palette. It does not
mention that one *example* also opts into that skin. The terminal palette overlaps the default one
with different meanings — `#f5f5f5` is `terminal-ink` there, not `paper` — so a blind pass would
have inverted that file's colours while reporting a clean run. Encoding the exclusion in the tool
makes it reproducible instead of a step someone has to remember.

**Rejected.** Passing a file list that happens to exclude them. The next person to run the codemod
across the asset directory would silently corrupt both files.

**Reverse.** Delete `uses_terminal_skin` and its call site.

---

## D10 — `SKILL.md` is updated in PR 2, not left to PR 4

**PR:** 2

**Choice.** `SKILL.md` §5, §6, §9, and §12 are converted to `var(--dd-*)` and gain the
bind-don't-inline rule in this PR.

**Why.** The M1 plan never mentions `SKILL.md`; design doc §6.5 does, and requires it. `SKILL.md` is
what the skill actually follows when it draws, so leaving its snippets full of `#4f5d75` would mean
every *newly generated* diagram was born un-tokenized while the shipped 102 were migrated — the
defect would reappear as fast as it was fixed. The contract PR is where the contract's instructions
belong.

Byte cap after the change: **38,314 of 40,000, 1,686 bytes of headroom** (was 2,594). ADR-0006's
relocation of the §3 tables, scheduled for the start of Phase 3, restores roughly 4,100.

**Rejected.** Deferring to PR 4. That would ship a milestone whose stated goal — colour binds
through tokens — was false for every diagram made after it.

**Reverse.** Revert the `SKILL.md` hunk; nothing else depends on it.

---

## D11 — Emptying the baseline moves from PR 3 to PR 4

**PR:** 3

**Choice.** PR 3 leaves `scripts/lint-skin-baseline.txt` intact. The 46 remaining lint findings are
remediated in PR 4, which empties the file. M1's definition of done — "`lint-skin.py --all` passes
without `--baseline`" — is met at the end of the milestone, not at the end of PR 3.

**Why.** The plan asks PR 3 to do two things that cannot both be true. Task 12 Step 4 says empty the
baseline and pass without it; Task 13 says the rasterized before and after must be byte-identical.
Measured on the real assets, the baseline holds because of **46 findings across 8 files** using six
colours that are not in the palette at all — `#3d4460`, `#b85450`, `#4a5270`, `#d97a78`, `#221f1c`,
and four `rgba()` derivations of them. No contract role has those values, so putting those files on
the contract necessarily changes their pixels. Emptying the baseline in PR 3 would have meant
accepting a differing raster, which the plan and the milestone brief both forbid outright.

Given the choice between the two, raster identity is the one that carries the load: it is what makes
102 changed files reviewable without reading 102 diffs, and it is the property later phases assume.
The baseline is a bookkeeping file whose emptying is checked at the milestone boundary.

**Rejected.** (a) Remediating the 8 legacy files inside PR 3 and exempting them from the raster
assertion — that guts the only gate protecting the sweep. (b) A sixth PR between 3 and 4 — the
remediation is visual change, and PR 4 is defined as the PR where all visual change lands.

**Reverse.** Move the legacy-colour commit from PR 4 to PR 3 and re-run the raster comparison,
expecting 8 files to differ.

---

## D12 — The light/dark variant is detected from the painted paper, not the filename

**PR:** 3

**Choice.** `migrate-to-tokens.py` decides a file's variant by resolving the paper it actually
paints — the `body` background, else the full-bleed background rect — falling back to a tally of
variant-exclusive literals, and only then to the filename.

**Why.** The plan assumes the two variants are distinguishable, and the obvious reading is by name.
They are not: **five shipped examples are named `-dark` and render on `#f5f5f5` white-smoke** —
`example-dp-integration-dark`, `example-gantt-dark`, `example-line-dark`, `example-process-dark`, and
`example-scatter-dark`. Confirmed by sampling the corner pixel of each rasterized PNG: all five read
`(245,245,245)`, while genuine dark examples read `(45,49,66)`.

Trusting the name would have mapped their `#f5f5f5` paper onto `--dd-ink`, since `#f5f5f5` *is* ink
in the dark skin. That is value-identical today, so **the raster gate would not have caught it** — and
it would have turned the page background ivory the moment PR 4 landed. This is the one class of
error raster identity cannot detect, which is why it is decided from content and asserted in
`test-migrate-to-tokens.py`.

**Rejected.** Renaming the five files to match their appearance. That is a real defect worth fixing,
but renaming shipped examples breaks gallery links and the a11y slug contract, and it is not M1's
concern. Recorded below as a carried-forward finding instead.

**Reverse.** Replace `variant_for` with the one-line filename check.

---

## D13 — `migrate-to-tokens.py` ships with a test and a CI gate

**PR:** 3

**Choice.** Added `scripts/test-migrate-to-tokens.py`, wired into CI and the CONTRIBUTING gate table.

**Why.** The plan treats the codemod as a throwaway. It is not: PR 4 re-runs it after the skin
changes, and every failure mode it has is silent — the output still lints, still parses, and still
renders. The line-based declaration parser it started with dropped `--ink`, `--muted`, and `--soft`
from packed one-line `:root` blocks and corrupted 47 of 102 files while passing every existing gate.
Only the raster comparison caught it. Each of the seven cases in the test is a defect that actually
occurred.

**Rejected.** Leaving it untested as a one-off script. The repo's own convention is that every script
in `scripts/` has a companion test, and this one earned it.

**Reverse.** Delete the test and its two gate entries.

---

## D14 — Legacy colours are mapped by the role they play, not by nearest neighbour

**PR:** 4

**Choice.** The 46 lint findings deferred from PR 3, plus the old-palette residue exposed once the
skin changed, were remediated by resolving each literal to the role it expressed and re-binding it.
The full mapping:

| Literal | Where | Bound to | Reasoning |
|---|---|---|---|
| `#f08a59`, `rgba(240,138,89,α)` | 5 mis-named `-dark` files | `accent` | Editorial dark accent, sitting in a light-paper file |
| `#82a0c0`, `#9caf8f`, `#b88670`, `rgba(184,134,112,α)`, `rgba(130,160,192,α)` | dark files | `series-2`, `series-1`, `series-4` | Editorial dark series values |
| `#7c8f6f`, `#5e7a9b`, `#b8915a`, `#9c6b50` | `data-flow-dark` | `series-1`…`series-4` | Editorial *light* series in a dark file |
| `#3d4460` (light) | high-level chevron banner | `color-mix(… ink 90%, paper)` | The banner alternates against `ink`; this is the lifted band |
| `#3d4460`, `#4a5270` (dark) | high-level chevron banner | `paper-2`, `color-mix(… ink 10%, paper-2)` | Two lifted surface tones on dark paper |
| `#221f1c` | `layers-dark` | `color-mix(… ink 6%, paper)` | A third surface tone in the layer stack, between `paper` and `paper-2` |
| `#b85450`, `#d97a78`, `rgba(184,84,80,α)`, `rgba(217,122,120,α)` | high-level-vertical security bar | `accent` | See below |
| `rgba(142,140,131,α)`, `rgba(150,146,138,α)` | tag strokes, timeline baseline | `muted` | Warm greys serving as a secondary rule |

**Why the reds collapse into `accent`.** `example-high-level-vertical*` used a red hue for its
Security/Identity cross-cutting bar *alongside* the coral accent — a second accent, which
`style-guide.md` forbids outright ("Two accents erases the focal signal") and which the node-treatment
table already answers: the `security` treatment is `accent @ 0.05` fill with an `accent @ 0.50`
dashed stroke. Binding the bar to `accent` puts the file back inside the design system rather than
inventing a role to preserve a violation.

**Rejected.** Nearest-neighbour colour matching. It gets `#3d4460` wrong in exactly the case that
matters: the chevron banner alternates two bands, and both bands map to the same nearest role, so
the alternation would have vanished. Role-by-context keeps the design intent that the colour was
expressing.

**Reverse.** Every mapping is a single `var()` or `color-mix()` expression; `git show` on this PR
names the file and line for each.

---

## D15 — Radius stays at node 2 / tag 2 / container 4

**PR:** 4

**Choice.** The design doc's radius values are kept unchanged after rendering the gallery.

**What the gallery showed.** The execution plan §6 flags these as a taste call to settle against a
rendered example, so all 102 files were rasterized under the brand skin and reviewed. A 2px corner
does not read as mean: node boxes are large relative to the corner — 160×64 is typical — so 2px
reads as deliberate precision rather than a clipped rectangle, and it matches the square-edged
register the brand uses for its own buttons. The 4px container corner stays legible as a container
without softening the figure.

**Gold as focal.** Also confirmed against the render: `#967A3A` on `#F5F2EC` clearly pulls the eye in
`example-architecture` and `example-high-level`, and `#D4B97A` on `#0F1A26` reads at least as
strongly in the dark variant. The focal signal survives the palette change.

**Rejected.** Node 4 / container 8, a softer register closer to the upstream editorial skin. It
looks fine, but it is the previous brand's register, not this one's, and the whole point of
tokenizing radius was to be able to say something other than 6.

**Reverse.** Edit the Geometry roles table in `style-guide.md`, run `scripts/build-skins.py`, then
`scripts/migrate-to-tokens.py --skin-only` over the assets.

---

## D16 — The reference files are re-skinned too

**PR:** 4

**Choice.** The ~110 palette literals and font names in `references/type-*.md`,
`primitive-annotation.md`, `onboarding.md`, and `output-spec.md` are bound to tokens alongside the
assets. `import-drawio.md` and `primitive-terminal.md` are excluded.

**Why.** Neither the plan nor design doc §6 lists the type references among the changed files. But
those files are prescriptive — the skill copies their snippets when it draws — so leaving `#eb6c36`
in them would mean every *newly generated* diagram was born off-palette and failed `lint-skin.py` on
its first run. The milestone would have shipped a skin that applied to the 102 files nobody edits and
to none of the ones the skill produces.

`import-drawio.md` is excluded because its hex table describes colours found in *incoming* draw.io
files, not this skin's palette. `primitive-terminal.md` is excluded because the terminal window is a
separate fixed skin.

Three light/dark variant tables (`type-dp-integration`, `type-process`, `type-high-level`) collapsed
to one column each in the process: a token name is the same in both variants, which is the point.

**Rejected.** Leaving the references for a follow-up. They are the skill's actual instructions;
a skin that the instructions contradict is not applied.

**Reverse.** The conversion is mechanical and recorded in this PR's diff.

---

## D17 — Carried forward, not fixed in M1

**PR:** 4

Findings surfaced by this milestone that are real but out of its scope. Recorded so they are not
mistaken for regressions.

1. **Five examples are named `-dark` and render on light paper** — `example-dp-integration-dark`,
   `example-gantt-dark`, `example-line-dark`, `example-process-dark`, `example-scatter-dark`. The
   codemod handles them correctly (D12), but the names still lie. Renaming shipped examples breaks
   gallery links and the a11y slug contract, so it belongs with the M2.4 gallery restructure.
2. **`series-1` is close to `accent`.** Both are gold: `#B0934B` against `#967A3A`. The brand's own
   chart ramp puts gold first, and design doc §5.3 maps it deliberately, so it was not reordered.
   Only `example-radar*` is affected, and the two are distinguishable — but the focal signal is
   weaker there than elsewhere. Worth revisiting when M2.4 sets per-variant selection rules.
3. **Node kind is still encoded almost entirely by hue** — design doc §9. The migration preserved it
   deliberately; M3 fixes it with a greyscale gate.

---

## D18 — Defect found and fixed after PR 4: the mono font URL was corrupted

**PR:** 5 (fix/mono-font-url)

**What happened.** The PR 4 font sweep replaced the Google Fonts `<link>` with the brand stack and
*then* ran a family-name replacement of `Geist` → `DM Sans` over the whole file. That second pass hit
`family=Geist+Mono` inside the URL it had just written, producing `family=Geist+Mono` →
`family=DM Sans+Mono`. Every one of the 104 assets requested a font that does not exist, so
`Geist Mono` never loaded and every sublabel, eyebrow, and arrow label fell back to `ui-monospace`.

**Why no gate caught it.** `lint-skin.py` parses the `family=` parameter by splitting on `:`, so
`DM Sans+Mono` reads as the family `DM Sans`, which is allowed. The `font-family` declarations still
said `'Geist Mono'`, which is in the linter's hardcoded allowlist. Both halves were individually
valid; only their *relationship* was broken, and nothing checks that.

**How it was caught.** By re-rasterizing after the change and comparing: 100 of 102 renders differ
between the broken and fixed states. The raster comparison built for PR 3 found a defect in PR 4 —
which is the argument for keeping it.

**Fix.** `family=DM Sans+Mono` → `family=Geist+Mono` across every asset and reference, plus the
stale `Instrument+Serif` URL in `export.md` that the sweep had half-updated. Shipped as its own PR
rather than folded into the export change, since it is a different concern.

**Worth doing later.** A gate asserting that every family named in a `font-family` declaration is
actually requested by the file's Google Fonts link would have caught this in CI. It is a small check
and it closes a real hole; recorded here rather than added now because it is enforcement work, which
Phase 2c owns.

---

## D19 — The export skin block is mandatory and complete, and was verified by rendering

**PR:** 5

**Choice.** `export.md` step 3 now injects the source's `:root` declarations into the same `<defs>
<style>` that already carries the font `@import`, rewritten from `:root` to `svg`, together with the
three `.dd-*` radius rules. All 25 roles are carried, never a subset.

**Why it is mandatory, not a nicety.** Verified by exporting `example-architecture.html` by hand both
ways and rendering each in Chromium. **With** the block: the standalone `.svg` parses as XML and
renders with the full palette, correct typography, and correct corners — indistinguishable from the
HTML. **Without** it: a solid black rectangle. An unresolved `var()` does not fall back to the
literal it replaced; `fill` falls back to its initial value, which is black. Tokenizing the assets
turned a merely-degraded export into a broken one, and this PR is what closes that.

**Why all 25 roles.** Trimming to the subset a diagram currently uses is smaller and works today, but
the block is generated — the next edit that reaches for a role the trim dropped produces a black
shape with no error anywhere. Copying the block whole is also the same operation as everywhere else
in the system, which is worth more than the bytes.

**Rejected.** Resolving the tokens to literals at export time. It produces a smaller, more
compatible file — but it is exactly the un-skinning this milestone exists to undo, and an exported
SVG would then be unreskinnable.

**Reverse.** Remove the added bullet from `export.md` step 3; exports revert to unstyled.

---

## D20 — The terminal files keep their own font link

**PR:** 6 (fix/terminal-font-link)

**What happened.** The PR 4 font sweep replaced *every* asset's Google Fonts link with the brand
stack, including `template-terminal.html` and `example-loop-terminal.html`. Those two originally
requested `family=Geist+Mono:wght@400;500;600;700` and nothing else — the terminal window is
all-monospace by design (`primitive-terminal.md`: "Everything is monospace — this is the one variant
where that's correct"). The sweep dropped the **700 weight** they actually use, so bold mono was
synthesised rather than loaded, and added two families they never reference.

**Why it was missed.** The exclusion in `migrate-to-tokens.py` covers colour (D9); the font sweep was
a separate pass and did not inherit it. Both files still linted clean, because a link that requests
too much and too little is valid either way.

**How it was caught.** The definition-of-done round trip: restoring the editorial skin returned 84 of
102 renders byte-identical to their pre-M1 state, and of the 18 that differed, 17 were the
deliberate legacy remediations from D14. The eighteenth was `example-loop-terminal`, which had no
business differing — and pulling that thread found the dropped weight.

**Choice.** Both terminal files get their original link back. The terminal skin is self-contained by
design, and that now includes its typography.

**Reverse.** Point the two links at the brand stack.

---

## D21 — The icon gallery is generated *from* the active skin

**PR:** 7 (fix/icon-generator-fonts)

**What happened.** CI failed on `main` after PR 4 with the icon gate red on all six OS/Python
combinations. Two separate causes, both from treating generated files as editable:

1. The PR 4 font sweep rewrote `assets/icons.html`, which `build-icons.py` generates. Regenerating
   restored the editorial fonts, so `git diff --exit-code` failed.
2. The reference sweep rewrote `#ffffff` → `var(--dd-node-white)` inside **two vendored icon paths**
   in `references/primitive-icons.md`, also generated. The token does not resolve inside a
   `currentColor` icon and the value came from upstream vendor SVGs, not from this skin.

**Why the local suite missed it.** The icon gate is `build-icons.py` followed by `git diff
--exit-code`, and it was in `CONTRIBUTING.md`'s table but **not** in my local runner — I built that
from the "run them all at once" chain, which omits it. The chain and the table disagree, and the
chain is what people copy.

**Choice.** Rather than hand-repair the two generated files, `build-icons.py` now reads the skin from
`assets/skins/active-light.tokens.css` and the typography from `style-guide.md`, and the gallery
binds through `var(--dd-*)` like every other asset. The gallery can no longer drift from the active
skin, because it is no longer a copy of it.

**Rejected.** Regenerating and moving on. That fixes today's red and leaves the next reskin to
rediscover the same failure — the gallery was hardcoded to the editorial palette, which is exactly
the defect M1 exists to remove.

**Reverse.** Restore the literal `:root` block in `GALLERY_TEMPLATE` and rerun `build-icons.py`.

**Also fixed:** the local suite runner now includes the icon gate. `CONTRIBUTING.md`'s copy-paste
chain gains it too, so the chain and the gate table finally agree.

---

## D22 — The plan's "45 diagonal `<line>` across 15 files" overcounts by 39

**Phase:** 2a

**Choice.** Only 6 diagonal `<line>` elements — 2 per variant across `example-swimlane`'s 3 files —
are genuine violations of the "no diagonal connector between off-axis nodes" rule. The other 39 are
left exactly as they render today.

**Why.** Inspecting all 45 by coordinates and context:

| Source | Count | What it actually is |
|---|---|---|
| `example-high-level*` (6 files × 4) | 24 | A vendored Kubernetes gear-icon glyph (`viewBox` coords 0–24), not a diagram connector at all |
| `example-radar*` (3 files × 4) | 12 | Axis spokes radiating from the chart's center — `type-radar.md` §"Axis spokes" names this explicitly and a 5-gon's spokes cannot be orthogonal by construction |
| `example-scatter*` (3 files × 1) | 3 | The optional trend line — `type-scatter.md` §"Trend line" specifies it as a diagonal `<line>` by name |
| `example-swimlane*` (3 files × 2) | 6 | Genuine lane-crossing connectors between off-axis node boxes — the rule's actual target |

The execution plan's own count (§1) asserts these are "real defects" without showing how it was
measured. A plain regex over `<line x1 y1 x2 y2>` — which is what produces 45 — cannot distinguish a
node-to-node connector from a chart primitive or an icon glyph. Two of the three excluded categories
are documented in their type references as intentionally non-orthogonal; forcing them onto elbows
would mean rewriting a radar chart's axes into right angles, which no reader would recognize as a
radar chart, and removing a scatter trend line's diagonal, which is the one thing that makes it a
trend line.

**What was fixed.** In `example-swimlane` (light/dark/full): the Open-PR→Review handoff became a
single-bend elbow (`type-architecture.md`'s "port selection" pattern — exit the source's bottom
edge, enter the destination's top edge); the Approve→Build handoff became a plain vertical `<line>`
by re-aligning both endpoints to `x=720`, which is legal under the rule's own exception for
same-axis endpoints and needed no bend at all.

**Rejected.** Redrawing the radar spokes as elbows, or the scatter trend line as a stair-step. Both
would produce a diagram unrecognizable as its own type, in service of a rule aimed at flowchart-style
connectors.

**Reverse.** Not applicable — no exclusion was hand-waved; each excluded file is checked against its
own type reference, and the check is re-run in full above.

**Consequence for 2c.** The diagonal-connector enforcement gate (Phase 2c) must exclude decorative
`<line>` elements — radar spokes, scatter trend lines, and any vendored icon glyph — or it will flag
39 files that are not defects. The gate's implementation needs a way to distinguish "connector
between node boxes" from "chart/icon primitive," most simply by scoping the check to lines whose
coordinates fall within the diagram's node-layout region and excluding `<g id="ico-*">` subtrees and
any file whose type reference documents an intentional diagonal primitive.

---

## D23 — "coral" renamed to "gold" everywhere it describes the accent

**Phase:** post-M1 cleanup, found while verifying 2a

**Choice.** Every reader-visible and maintainer-visible reference to the accent as "coral" —
20 sentences of editorial card prose across 12 `-full`/`-dark` examples, ~40 HTML comments, and the
`.card-dot.coral` CSS class (30 usage sites, renamed to `.card-dot.accent` to match the canonical
pattern `SKILL.md` already uses) — now says "gold," matching what the brand skin actually renders.

**Why.** PR 4 (the Inflection skin) retargeted every colour token but never touched prose that named
a colour by English word rather than by role. `example-state-full.html` literally said "hence coral"
next to a gold-bordered box. This is exactly the kind of defect a linter can't catch — `lint-skin.py`
validates hex values and token names, not whether a caption's colour claim matches its render.

Also removed: four orphaned comment lines (`/* white-smoke */`, `/* jet-black */`, `/* blue-slate */`,
`/* atomic-tangerine */`) in `example-import-drawio.html`, stranded mid-`:root`-block by the PR 3
migration — they annotated four values that used to sit on one line and now describe nothing.

**Rejected.** Leaving comments as-is on the theory that they're invisible to readers. They're visible
to whoever edits these files next, and a fork whose own source comments contradict its own rendered
output is the failure mode ADRs and decision logs exist to prevent elsewhere.

**Reverse.** `git grep -i gold` in `skills/diagram-design/assets/` finds every site; re-run the
inverse substitution.

---

## D24 — Phase 2b: the notch and mandatory-tag scope, corrected from the spike's assumption

**Phase:** 2b

**Choice.** The corner-notch encoding (0/1/2 = runs/holds/outside-our-control) is applied only where
the 7-kind vocabulary from `style-guide.md`'s "Node type → treatment" table is genuinely in use —
confirmed per-file by checking actual fill/stroke pairs and tag text, not assumed from the type name.
This lands on `architecture`, `high-level`, `high-level-vertical`, and `sequence`/`sequence-oauth`
(their actors), across all variants, plus `import-drawio` as a worked example of the pattern applied
to a redrawn diagram.

**Why the scope is narrower than "every diagram with boxes."** Fill/stroke signature matching across
all 97 files found the same token values reused for unrelated purposes: `tree`'s leaf-skill boxes and
`org-chart`'s IC-tier boxes use the exact `wash-5`/`muted` pair the style guide calls `store`, purely
as a de-emphasis treatment for hierarchy depth — not a claim that a skill category is a database.
Notching them would misrepresent the diagram. `flowchart`, `state`, `tree`, `er`, and `org-chart` each
have their own kind vocabulary (decision/process/terminal; state names; category/leaf/root;
entity/join; role/pod) and gain nothing from a taxonomy built for infrastructure kind. Chart types
(`bar`, `line`, `gantt`, `scatter`, `radar`) and the three animated semantic-pattern examples
(paved-road, policy-trace, queue) have no node-kind concept at all — verified by inspection, not
assumed — and keep their own established vocabulary (`primitive-notch.md` documents this scope).

**A real defect found along the way.** `example-high-level`, `-high-level-vertical`, and
`-datalake` (6 files, 8+ nodes each) used the literal CSS keyword `fill="white"` instead of
`var(--dd-node-white)` — a token-contract violation the M1 linter never caught, because
`lint-skin.py`'s hex/rgba checks don't recognise bare CSS colour keywords. Fixed by replacing the
literal with the token, and `lint-skin.py` now rejects any bare `fill`/`stroke` colour keyword
outside `none`/`transparent`/`currentColor`, with a regression test, so this class of drift can't
recur silently.

**Also found:** four EXT-tagged source boxes each in `high-level` and `high-level-vertical` carried
a softened stroke opacity (`ink @ 22%`) that doesn't byte-match the canonical `external` signature
(`wash-3`/`wash-30`) — a legitimate per-file stylistic choice (external sources sit outside a
Kubernetes-boundary zone that's already dashed, so the individual node stroke is softer by design).
These 8 boxes were hand-notched at 2 (matching their tag text and context), since the mechanical
codemod correctly declined to touch a fill/stroke pair it didn't recognise rather than guess.

**Rejected.** Generalising the codemod's signature table to catch every stroke-opacity variant found
across 97 hand-authored files. Several of those variants are deliberate per-diagram choices (softer
external stroke on a boundary source, `ink@25%` vs `ink@22%` in the same file distinguishing backend
from external at a glance); absorbing all of them into one signature table would either misclassify
some or require a signature per file, at which point the codemod is not saving anything over reading
the file.

**Reverse.** `primitive-notch.md`'s scope section names every excluded type and why; adding a type
means adding its row there and its fill/stroke pair to `KIND_NOTCH` (or hand-notching, if its signature
diverges as high-level's did).

## D25 — Focal stroke-weight bump applied universally, notch scope narrower

**Phase:** 2b

**Choice.** The 1.2→1.6 focal stroke-weight bump (per the spike's recommendation) was applied to
every `accent-tint`/`accent` node across all 97 files, including the three semantic-pattern animated
examples and types outside the notch's scope (state, tree, venn's intersection tint, etc.) — unlike
the notch, this change carries no kind-taxonomy assumption, just emphasis, so it is safe everywhere
the focal treatment already appears.

**Reverse.** Revert `stroke-width="1.6"` to whatever value preceded it per file (1, 1.2, or 1.5 —
recorded as found, not previously uniform).

---

## D26 — The coral-to-gold sweep missed the reference docs and SKILL.md itself

**Phase:** post-M1 cleanup, found while landing 2b

**Choice.** 18 files under `skills/diagram-design/references/` plus `SKILL.md` still said "coral"
to mean the accent colour — including three places in `SKILL.md`'s own philosophy section and
pre-output checklist. Fixed with the same case-preserving substitution used in D23.

**Why this is more serious than the earlier miss.** D23 fixed prose in the shipped *examples* —
cosmetic, in already-rendered output. This one is in the skill's own *authoring instructions*: every
`type-*.md` file tells the agent what to do when it draws a **new** diagram. `type-sequence.md` said
"Max coral elements: 2" and `type-org-chart.md` said "Max coral nodes: 1" — correct rules, wrong
colour name, and the skill would carry that name into every diagram it generates from here on
regardless of how many examples were already fixed.

**Why it was missed the first time.** D23's sweep scope was `skills/diagram-design/assets/` — the
rendered examples — because that is where the visible defect was first noticed (a caption
contradicting its own render). Reference docs don't render, so nothing prompted a look at them until
this unrelated pass (verifying the notch work) surfaced `SKILL.md`'s own occurrences by chance.

**Reverse.** Same as D23: `git grep -i coral` in `skills/diagram-design/` finds any recurrence.

---

## D27 — Phase 2b closes with three documented exemptions, not silently dropped

**Phase:** 2b

**Choice.** Of the seven "systems-family" types PR #17 named as in-scope, three needed no
tag/notch work at all, for reasons specific to each — recorded in `primitive-notch.md` rather than
left as an unexplained gap between what the PR said and what it shipped.

- **`data-flow`** — already fully tagged (verified by a precise geometric pairing check, not the
  substring match that first suggested otherwise).
- **`it-state` and `dp-integration`'s source/consumer sides** — already carry a complete kind-signal
  via icon + CSS modifier class (`.node.external`, `.side-node`, `.core-node`), predating this
  milestone. Grafting a text chip beside an icon that already reads at a glance would be redundant
  clutter, not an improvement.
- **`swimlane`** — every step is the same kind (`backend`), so a tag would repeat "STEP" on all
  seven boxes with no differentiating information, and its 48px height (below the 56px floor) has
  no room for a third line alongside the name and technical sublabel it already carries. Reflowing
  to 64px is real layout work that belongs with the other 20 short-box files this same 56px
  threshold flagged, not a one-off fix.

**Why this matters enough to log.** A prior PR's decision log (D24) named these seven types as
in-scope without qualification. Someone reading only that entry would expect all seven to show
tags and notches, and finding three unchanged would look like an abandoned task rather than a
reasoned exemption. This entry is the record that closes that gap.

**Reverse.** Each exemption is reversible independently: add tag chips to swimlane after reflowing
it to 64px, or add chips alongside the icons in it-state/dp-integration if a future review decides
the icon alone isn't sufficient.

---

## D28 — org-chart's specialist tier gets an `IC` tag; tree's leaf tier is exempt for the same reason as swimlane

**Phase:** 2c prep

**Choice.** Measuring genuine tag-consistency (not just tag presence) across all 97 files —
comparing each file's own established tag vocabulary against every box that should carry one —
found two real gaps and one false positive:

- **`org-chart`'s 6 specialist boxes had no tag at all**, while the root (`FRONT`) and pod-owner
  tier (`POD`) above them do. At `h=56`, name-only, no sublabel — clear of the 56px floor with room
  to spare. Fixed with an `IC` tag (individual contributor, completing the FRONT → POD → IC
  hierarchy already implied by the fill treatment) across all 3 variants, plus a 4th legend swatch
  that was also missing.
- **`tree`'s leaf-skill tier has the same gap**, but is exempt for the reason `swimlane` already is
  (D27, generalised here): `h=48`, already spends its height on a name and a sublabel
  (`align · space · rhythm`), no third line available. `primitive-notch.md`'s exemption language is
  now general — any short box with name+sublabel, not swimlane-specific — since the underlying
  constraint is geometric, not particular to one type.
- **`high-level`/`high-level-vertical`'s apparent "4/5 tagged" reading was a measurement artifact**:
  the geometric checker only scanned `<rect>` elements, and PR #17 had already converted several of
  their nodes to `<path>` for the notch. Re-measured including path-based nodes: both files are
  fully, consistently tagged. No fix needed; recorded so the false alarm doesn't get re-investigated.

**Reverse.** Remove the 6 `IC` tag insertions and the 4th legend swatch from the 3 `org-chart`
variants to fully undo; `tree` and `swimlane` are untouched by this entry.

---

## D29 — Phase 2c's five enforcement gates: three ship clean, two grandfathered

**Phase:** 2c

**Choice.** Built the five gates the execution plan's §4.1 lists for 2c, each with a paired
adversarial test script following the `verify-geometry.py`/`test-verify-geometry.py` pattern. Two
of the five needed grandfather baselines; three landed clean because the corrections already made
in D22 (diagonal scope), D24/D27/D28 (notch/tag scope) held up under a full-corpus re-measurement.

- **`verify-no-diagonal.py`** — 0 findings across all 102 shipped files. Masks nested
  `<svg>`/`<symbol>`/`<marker>` subtrees (icon glyphs, which legitimately draw diagonals) before
  scanning the outer canvas, and exempts `example-radar*`/`example-scatter*` by filename since
  those chart types are diagonal-native. D22's corrected scope — diagonals between off-axis
  *nodes*, not diagonals anywhere in the SVG — is what makes a clean pass possible; the plan's
  original "45 diagonal lines" estimate was counting raw `<line>` tags including icon interiors.
- **`verify-tag-consistency.py`** — 0 findings. Not a universal per-node mandate: a file that tags
  one node-sized box must tag all its comparable siblings, with the short-box (h<56) and
  icon-as-signal exemptions D27/D28 already established. Required extending node detection to
  path-based nodes (not just `<rect>`) to avoid re-triggering the same high-level false alarm D28
  documented, and excluding `fill="transparent"` outline boxes and `h>120` zone containers so
  annotation/grouping shapes don't get misread as untagged nodes.
- **`verify-no-transcription.py`** — 0 findings, forward-looking. Establishes the
  `class="dd-compartment-line"` convention now, ahead of Phase 3's code-level type, per
  design-review-pass-3 §4.14: no compartment line may transcribe a field's type (colon or bracket
  syntax), and no more than 3 consecutive compartment lines. Nothing today uses the class, so this
  gate is pure guardrail — it protects a convention that doesn't have a violator yet, deliberately,
  so Phase 3 can't introduce one during code-level's first draft.
- **`verify-grid.py --baseline`** — 101 of 102 files fail outright (5,741 raw violations, close to
  the plan's own 5,405 estimate). Grandfathered per the plan's explicit instruction: moving every
  coordinate onto the 4px grid is a redraw, not a lint fix, and would change every shipped layout
  with no way to review that the change was visually intended. `scripts/grid-baseline.txt` seeded
  with all 101 today; `r`/`rx`/`ry` and path `d` curve coordinates stay out of scope, matching
  `style-guide.md`'s Geometry roles table.
- **`verify-accent-budget.py --baseline`** — rebuilt the metric from "count hex occurrences" (the
  plan's original approach, which triple-counts one focal node's mask/box/tag-chip trio) to "count
  distinct nodes and connector shapes." 18 of 97 exceed the 2-element budget, almost always by
  exactly one `<path>` — a single accent flow drawn as two consecutive path segments around a bend,
  which a reader perceives as one continuous route, not two accent decisions. Distinguishing that
  from a genuine second accent connector needs endpoint-adjacency tracing this linter doesn't
  attempt, so `scripts/accent-baseline.txt` seeds the 18 today rather than under- or
  over-counting them.

**Why this matters enough to log.** Every naive per-gate estimate in the plan (diagonal count,
grid violations, accent occurrences) was derived by raw substring/regex counting rather than by
what a reader actually perceives as one visual decision. The pattern held across all five gates:
re-derive the true scope from what the rule protects against, then measure that. D22/D24/D27/D28
each caught one instance of this; this entry is where all five gates' final shapes are recorded
together, since they were designed and landed as one PR.

**Reverse.** Delete the five `verify-*`/`test-verify-*` script pairs and their two baseline files,
and remove the corresponding rows from `CONTRIBUTING.md`'s gate table, run-chain, and
`.github/workflows/ci.yml` to fully undo. Baselines shrink independently of this entry: a file
leaves `grid-baseline.txt` or `accent-baseline.txt` by becoming clean, never by re-addition.

---

## D30 — Code level lands as type-er.md renamed and generalized, not a new type

**Phase:** 3 (M2 archetypes)

**Choice.** Per the execution plan's Phase 3 ordering, code level shipped first — lowest risk,
since it proves the type-shipping pipeline against an existing type before new ones. `type-er.md`
is renamed to `type-code-level.md` with a new `## Which variant` section splitting it into an
**Entity preset** (the original ER content, untouched) and a new **Class preset** (class/interface
structure). Costs no new type — the SKILL.md row that was "ER / data model" is now "Code level",
same row, same count.

The class preset answers the design brief's open question #3 ("is a code-level diagram worth
drawing at all?") with yes, conditionally: it earns its place by showing *shape*, not by
reproducing source (each box carries one short responsibility phrase, never a member listing),
which is also why the type never needed the notch primitive — its kind vocabulary is
`INTERFACE`/`ABSTRACT`/`CLASS`, unrelated to the 7-kind infra taxonomy notch encodes.

Three relation kinds (`is-a`, `has-a`, `depends-on`) get three marker treatments so the diagram
reads without a legend for the kind, only for the specific verb: `is-a` shares one hollow-triangle
marker family (dashed = realizes, solid = extends), `depends-on` is a thin dashed line with a
filled arrowhead, `has-a` terminates in a filled square at the whole's end. A text token at each
line (`REALIZES`, `EXTENDS`, `PRODUCES`, `DEPENDS ON`, `HAS`) carries the specific verb, unifying
with the entity preset's existing cardinality-token convention exactly as the plan specified.

The scenario shipped is the design brief's own 9-type stress case (`Extractor` realized by two
extractors, both producing `DiagramIR`; `Validator` extended by two validators, both depending on
`DiagramIR`; `DiagramIR` composed of `Node`/`Edge`) — 10 connectors converging on one focal box,
deliberately at the budget ceiling. Getting the 4 connectors converging on `DiagramIR`'s top edge
to route without overlap needed staggered jog heights (the closer source jogs early, the farther
source jogs late) rather than a single shared elbow height — a real instance of the "fanned
attach ≥12px apart, no two connectors overlap" rule biting on a converging cluster, not just a
straight run.

**Two real bugs in `verify-grid.py` (Phase 2c) surfaced building this file, both fixed here, both
shrinking the grandfather baseline:**
- `\b(width|...)` matched inside `stroke-width="1.2"` — a hyphen is a non-word character, so `\b`
  sits happily right before "width". Any stroke-width value that wasn't itself a multiple of 4
  (1.2, 1.6, 0.8 — every stroke-weight token in the style guide) was flagged as a bogus geometry
  violation. Fixed with a negative lookbehind excluding a preceding word character or hyphen.
  Re-measuring the full corpus with the fix dropped 2 files off `grid-baseline.txt` entirely
  (`example-import-mermaid.html`, `example-quadrant-consultant.html` — their only "violations"
  were stroke-width false positives).
- `<defs>` content (the decorative dot-pattern tile and marker glyphs) was scanned as though it
  were layout geometry. Every shipped file's dot pattern uses the same off-grid `cx="1" cy="1"`
  chosen for a seamless tile repeat, not placement on the canvas grid — confirmed by the pattern
  being identical across every file regardless of how clean that file's actual layout is. Excluded
  `<defs>` from the scan, which dropped 11 more files off the baseline
  (`nested`/`timeline`/`venn` ×3 variants each, plus `template.html`, `template-dark.html`,
  `template-terminal.html`).

Both fixes were necessary before any *new* file could pass the grid gate at all — new files get no
baseline exemption, and every style-guide stroke-weight token plus the universal dot-pattern
background would otherwise make a clean pass impossible regardless of how correct the actual
layout is. `scripts/grid-baseline.txt` shrank from 101 files to 88 as a result.

**Reverse.** `git mv type-code-level.md type-er.md`, delete the `## Which variant` section and
Class preset content, remove the 3 `example-class*.html` files and their gallery tab, and revert
the SKILL.md row and frontmatter description to their prior "ER / data model" wording. The two
`verify-grid.py` bug fixes are independent of the rename and are not part of this reverse — they
correct measurement, not design, and un-fixing them would reintroduce false positives.

---

## D31 — Zoom: parent boxes drop below the node-detection floor by design, not accident

**Phase:** 3 (M2 archetypes)

**Choice.** Zoom's parent strip (the quieted, reduced reproduction the design brief requires)
uses 24px-tall boxes — below both `verify-tag-consistency.py`'s 56px short-box floor *and*
`verify-accent-budget.py`'s 28px node-detection floor. This is deliberate: the brief's own
language for the parent is "orientation, not content," and a box that size genuinely isn't a
full node by either gate's own reasoning — a tag chip has nowhere to sit, and marking one of
these boxes gold doesn't spend from the same 2-accent budget a real focal node would. The one
marked parent box (`Transform`) and the expansion's real focal box (`Quarantine`, at full 64px
node size) together are exactly the "one thing marked" the archetype calls for twice — once in
the overview, once in the detail — and only `Quarantine` counts against the accent budget. This
is a consequence of the parent being legitimately smaller, not a size chosen to dodge a gate.

**Correspondence mechanism chosen: a wedge (frustum) plus a shared label, not a connector.**
Of the five options the design brief lists (connector, wedge/frustum, matched stroke, shared
label, cut-away), a plain connector would read as a *relationship between two nodes* rather than
"this box's contents are drawn below," and matched-stroke-only relies on a reader noticing a
colour echo. The wedge is unambiguous on its own (it is the universal "zoom in" cone from
Mission Control to Keynote's morph transition) and needed no accent colour to read, so it's
drawn in a neutral wash — keeping the entire 2-element accent budget free for the two marked
boxes. A repeated label (`TRANSFORM · DETAIL` in the frame's corner) is layered on top as a
second, independent confirmation signal, per the brief's "explicit visual correspondence"
requirement being worth over-satisfying once, cheaply, rather than relying on geometry alone.

**The wedge's diagonal sides are not a `verify-no-diagonal.py` violation.** That gate scans
`<line>` elements specifically because the house rule it encodes ("no diagonal connector
between off-axis nodes") is about connectors asserting a relationship between two boxes. The
wedge is drawn as a single closed `<path>` — a framing/correspondence shape, structurally like a
container boundary, not a connector — so it was already out of scope by the gate's own
construction rather than needing a new exemption. Documented here so a future reviewer doesn't
mistake the omission for a gap.

**Node/connector budget applies per sub-diagram, not to the file's total.** The parent (6 boxes)
plus the expansion (5 boxes) sum to 11 visible boxes, over the stated 9-node ceiling — but Zoom
is definitionally two diagrams in one file (an overview and a detail), and the brief requires
showing both in full. Read the ≤9 nodes / ≤12 connectors budget as applying to the parent and the
expansion independently (6 and 5 nodes; 5 and 4 connectors, respectively), the same way a
multi-panel Contrast diagram will need to when it lands next.

**Reverse.** Delete `type-zoom.md`, the three `example-zoom*.html` files, the SKILL.md row and
frontmatter hook, the gallery tab, and revert the `verify-docs-sync.py` count back to 27.

---

## D32 — Contrast: parity through matched columns and matched vertical extent, not a literal grid

**Phase:** 3 (M2 archetypes)

**Choice.** Shipped the design brief's own scenario — three product teams each owning an
Auth/Billing/Audit stack (9 boxes, 3 columns) versus one shared Platform Core the same three
teams consume instead — because it's explicitly the archetype's hardest case: "the lopsided
case is the most common real shape," where the proposed panel has far fewer nodes than today's.

The brief lists several ways to make parity visible — aligned baselines, matched node sizes,
shared row positions, a shared background grid. Rather than drawing a literal grid overlay
(which would compete visually with the actual content), parity comes from three structural
matches that don't need to be drawn to be felt: identical column x-positions in both panels,
identical team-header size/position, and — the one specific to the lopsided case — the
consolidated `Platform Core` box's height exactly spans the vertical extent the three stacked
services used to occupy (128 to 304 in both panels). A reader's eye can trace "this column, this
vertical space" across the divider without needing gridlines drawn over the content.

**Team-header boxes (6 total, 3 per panel) use the same sub-28px-height treatment Zoom's parent
strip established in D31** — quieted, no tag, below both the tag-consistency and accent-budget
node floors. They're doing the same job here that Zoom's parent thumbnail does: orientation
(which team, which column) rather than content, and the precedent held on a second, independent
type without needing to be re-derived.

**Only the Today panel's ownership is undrawn; the Proposed panel's consumption is an explicit
connector.** This is itself part of the argument, not an inconsistency: owning your own stack
needs no connector (the column layout already says "these three are Team A's"), but depending on
something *external and shared* is new information once it's true, so it gets drawn. The
contrast isn't just "fewer boxes" — it's "implicit ownership became an explicit dependency,"
and the connectors are how that second, quieter claim gets made visible too.

**Delta ledger deferred to the full-editorial variant's supporting prose**, per the brief's own
"whether it earns its place" framing — the minimal/dark variants read the whole claim from the
diagram alone; a bulleted list of what changed would be redundant weight there, but is a
reasonable inclusion once the full variant already carries explanatory cards.

**Reverse.** Delete `type-contrast.md`, the three `example-contrast*.html` files, the SKILL.md
row and frontmatter hook, and the gallery tab; revert the visual-type count from 29 to 28 across
the same files D31 lists.

---

## D33 — Lineage: distinct from Tree by design, layered by longest path

**Phase:** 3 (M2 archetypes)

**Choice.** Shipped the design brief's own scenario verbatim (`dim_customer`'s upstream
staging/raw assets and downstream fact/mart/dashboard consumers) and answered the brief's open
question #1 directly in `type-lineage.md`: **yes, Lineage is genuinely distinct from Tree.**
Tree has no notion of direction-of-consequence and no multi-parent case; Lineage's entire
reason to exist is a DAG where one node can have several parents and two opposite claims
(derived-from, impact-if-changed) read off the same graph. Stretching Tree's grammar to carry
either would be the tree type doing a different type's job.

**Nodes are layered by longest incoming path, not nearest.** `mart_revenue` has a direct edge
from `dim_customer` (distance 1) and an indirect one through `fct_orders` (distance 2) — it's
placed in the 2-hops-downstream column, matching the layered-DAG convention real graph-layout
tools use, and the direct edge from `dim_customer` is drawn as a genuine skip connector that
routes around `fct_orders`' column rather than being compressed into an adjacent-column edge.
This was also the hardest routing problem in the set so far: getting the two upstream boxes in
the 2-hop column to feed a two-box 1-hop column without any edge crossing another required
routing every cross-row connection through the *inter-row gap* (the vertical band between the
stacked pairs, safely clear of every column's node y-ranges at that height) rather than through
node edges directly — documented here since the pattern (route through the shared safe band,
never through a box's own column at a height another box occupies) generalizes to any future
type with stacked multi-node columns.

**Direction is colour-coded, not just arrow-coded.** Upstream connectors and node tags stay
ink/muted; downstream connectors and node tags use `--dd-link`. This is the brief's own
requirement ("without relying on arrowheads alone") satisfied through the same "text token +
colour" combination Lineage's siblings have each used slightly differently — Zoom used
shape (the wedge), Contrast used position (matched columns); Lineage uses colour, because
here the axis being encoded (upstream/downstream) is a stable structural property of every
node, not a one-off marked difference.

**The fan-out cohort (`Dashboards ×12`) uses undecorated stacked rects, not `dd-node`.** Giving
the two card-stack rects behind the main box a `dd-node` class would register them as three
separate untagged nodes to `verify-tag-consistency.py`, when they're decoration for one
cohort, not three additional assets. Keeping them classless keeps the count semantically
honest without fighting the gate.

**A font-size caught late by measurement, not estimation.** `raw_billing_accounts` (21
characters) at the same 10.5px mono used for shorter names overflowed its 140px box by ~2px —
invisible without checking, since Playwright's default screenshot doesn't flag clipped text.
Measured the actual rendered `getBBox()` width rather than estimating from character count,
found the overflow, and dropped every name to 9.5px, which is now the ceiling for identifier-
style names in a 140px node at this type's density.

**Reverse.** Delete `type-lineage.md`, the three `example-lineage*.html` files, the SKILL.md row
and frontmatter hook, and the gallery tab; revert the visual-type count from 30 to 29 across the
same files D31/D32 list.

---

## D34 — Composition: correspondence by matched numbering, zero connectors

**Phase:** 3 (M2 archetypes)

**Choice.** Shipped the design brief's own scenario (a 6-part catalog — auth, ingest, engine,
ui, audit, notify — with `Certainty` assembled from three of them plus a bespoke `Award rules`
component) and directly solved the brief's flagged hard problem: "edges from 4 catalog parts
to 1 assembly will violate the no-overlap rule fast — solve this."

**The solution is to draw zero connectors between catalog and assembly.** Every catalog part
carries its number in its own name text (`02 · ingest`), and every used part appears again
inside the assembly container as a small reference chip carrying the *identical* label. The
matching number is the entire correspondence mechanism — a reader matches "02 · ingest" in the
assembly to "02 · ingest" in the catalog above it, with no line, no crossing risk, and no
budget spent on connectors at all. This generalizes the "if the relationship is obvious from
layout, remove the line" philosophy one step further: here the relationship isn't obvious from
layout alone, but it doesn't need a *connector* either — a repeated label is enough, and it's
what the brief's own "matched treatment... numbering" correspondence option was pointing at.

**Reference chips are deliberately not `dd-node`.** They're smaller (32px tall vs. the
catalog's 64px) and undecorated on purpose — a full-size, fully-treated duplicate would read as
a *second independent part*, not a citation of the first. Keeping them off the tag-consistency
gate's scan (no `dd-node` class, same technique D33's cohort stack used) keeps the geometry
honest: there are 6 real catalog parts and 1 real bespoke part, and 3 references, not 10 nodes.

**Catalog uniformity chosen over "show which parts are most used."** The brief lists both as
properties to explore; dimming or resizing unused catalog parts would break the exact signal
the catalog exists to send (interchangeability), so which parts got used is information that
belongs in the assembly zone, not a mutation of the catalog's own presentation.

**No promotion edge.** The brief asks whether bespoke work returning to the catalog earns its
place; this scenario has no such event, so the minimal/dark variants don't manufacture one —
adding a edge for a relationship that doesn't exist in the scenario would be exactly the kind
of undrawn-but-implied claim the type is designed to avoid making.

**Reverse.** Delete `type-composition.md`, the three `example-composition*.html` files, the
SKILL.md row and frontmatter hook, and the gallery tab; revert the visual-type count from 31 to
30 across the same files D31–D33 list.

---

## D35 — Deployment: the budget question answered, notch scope extended to a new type

**Phase:** 3 (M2 archetypes)

**Choice.** Shipped the design brief's own scenario verbatim — `Production` in AWS
`eu-west-1`, two availability zones each running an ECS cluster (`API` ×3, `Worker` ×2), a
Postgres primary in zone A replicating to a read replica in zone B, an ALB fronting both zones,
and Route 53 outside the region — and answered the brief's explicitly-flagged central question
("does Deployment survive realistic scale?") directly in `type-deployment.md` rather than
leaving it implicit: **yes**, once nesting containers are free (not counted against the node
budget, since they're transparent `dd-container` boundaries structurally identical to zone
boundaries other types already use), replica counts are stated badges rather than drawn copies,
and asymmetric siblings (this scenario's two zones, which differ because the primary/replica
split makes them genuinely not interchangeable) stay uncollapsed while symmetric ones wouldn't.
Applying all three lands this exact realistic topology at 8 real content nodes — inside budget.

**Notch scope extended to `deployment`, documented as an extension not an exception.**
`primitive-notch.md`'s scope list was an enumerated set of existing types; `deployment` is a new
type whose three kinds (container instance / database instance / infrastructure) map directly
onto the existing vocabulary (`backend`/`store`/`external`), so this is the first type to *lean
on* the notch for its primary kind-distinction — the brief's own "fill opacity alone is weak"
concern is real here specifically because dashed-transparent deployment-node containers already
spend fill/opacity as a *fourth* signal (deployment node vs. instance vs. infra vs. focal), so a
shape-based channel earns its place rather than being decorative.

**Three visual treatments, not two.** Deployment node (dashed, transparent, unnotched — it's a
boundary, not a kind-bearing box) / container instance (solid, 0 notch) / infrastructure (solid,
2 notch) — plus focal accent as an orthogonal fourth signal on the Postgres pair, and 1 notch
(`store`) as a *fifth* distinguishing detail specific to the database instances. This is the
densest kind-signaling stack shipped in any type so far, and it holds because each signal answers
a different question (what kind of thing / is it focal / does it hold state) rather than
stacking redundant cues for the same fact.

**Cross-zone replication crosses containment boundaries directly.** The brief asked whether this
breaks the containment reading; it doesn't — a connector between a primary and its replica exits
zone A's dashed boundary and enters zone B's directly, at the same y-level as both instances, no
special routing needed. Containment boxes are visual scope, not a physical wall a real
cross-cutting relationship can't cross.

**Reverse.** Delete `type-deployment.md`, the three `example-deployment*.html` files, the
SKILL.md row and frontmatter hook, the gallery tab, and the `deployment` scope-extension
paragraph in `primitive-notch.md`; revert the visual-type count from 32 to 31 across the same
files D31–D34 list.

---

## D36 — Caught mid-Phase-3: the §3 table relocation to routing.md, missed at Phase 3's start

**Phase:** 3 (M2 archetypes), triggered while landing Deployment

**Choice.** The execution plan explicitly scheduled a step I skipped: "moving the §3 tables into
`references/routing.md` frees 4,102 bytes... Relocation | **Start of Phase 3** | Frees the bytes
before they are spent." I proceeded straight into Code Level without doing it. By the time
Deployment's row landed, `SKILL.md` was at 40,077 bytes — 77 over the 40,000 cap
`verify-semantic-motion.py` enforces — and the suite went red.

Fixed by doing the relocation now, exactly as originally planned: created `skills/diagram-design/
references/routing.md` holding both tables verbatim (the semantic-pattern trigger table and the
32-row visual-type guide) plus the "rules of thumb" and "always load" closing notes. `SKILL.md`
§3 now states the two-step rule in three sentences and points to `routing.md` for both tables.
This dropped `SKILL.md` from 40,077 to 34,980 bytes — 5,020 bytes of headroom restored, close to
the plan's own 4,102-byte estimate for this exact move.

**Three gate scripts needed updating to read the relocated table, not just SKILL.md and
routing.md themselves:**
- `verify-docs-sync.py`'s `check_description()` now reads `selection_table_types()` from
  `routing.md` instead of `SKILL.md` (the frontmatter description hook-check still reads
  `SKILL.md`, since that file didn't move).
- `verify-semantic-motion.py`'s `verify_markdown()` now checks `SKILL.md` links to
  `references/routing.md` (replacing the old "guide heading exists in SKILL.md" check), reads
  the 32-row table and its `Rules of thumb:` boundary from `routing.md`, and checks each of the
  7 semantic-pattern names against `skill or routing` instead of `skill` alone.
- `test-verify-motion.py`'s "missing visual-guide anchor" adversarial case now patches
  `semantic_module.ROUTING` instead of `semantic_module.SKILL`.

Also added `routing.md` to the architecture tree in `README.md`, which had never listed it
(harmless to the gate, since `check_readme_tree` only validates named files exist, not that all
real files are named — but a new reference file with no discovery path in the README is exactly
the kind of gap this system otherwise tries not to leave).

**Why this matters enough to log as its own entry** rather than folding into D35: this wasn't a
design decision about Deployment, it was a missed step from the plan's own dependency ordering
that happened to surface *while* landing Deployment. Recording it separately keeps D35's
Deployment-specific reasoning (the budget answer, the notch extension) from being diluted by an
unrelated infrastructure fix, and makes the gap and its correction independently greppable.

**Reverse.** Move both tables back into `SKILL.md` §3 verbatim, delete `routing.md`, revert the
three gate scripts' `SKILL`/`ROUTING` split back to reading `SKILL.md` alone, and remove the
`routing.md` line from `README.md`'s architecture tree.

---

## D37 — Matrix: retires DP security matrix to a preset, net type count unchanged at 32

**Phase:** 3 (M2 archetypes) — the sixth and final new-type PR, per the execution plan's own
ordering ("Matrix — last, because it lands with `type-dp-security-matrix` retired to a preset in
the same PR").

**Choice.** Shipped the design brief's own scenario (3 regions × 3 products, tenant counts per
cell, the `Fission` column marked as the only product deployed everywhere) as a new **General
preset**, and folded the existing, detailed parametric `type-dp-security-matrix.md` spec into
the same file as a **Security-matrix preset** — same file rename pattern D30 (Code level)
established for ER/Class. `type-dp-security-matrix.md` → `type-matrix.md`, its entire
parametric input-schema/formula/reproducibility-checklist content preserved verbatim under its
own heading, `routing.md`'s row retargeted from "DP security matrix" to "Matrix," and the
existing 3 `example-dp-security-matrix*.html` files and their gallery tab left untouched — they
still demonstrate the preset correctly and needed no changes. This is why the visual-type count
stays at **32** rather than climbing to 33: one row was retargeted, not added.

**The claim-marking problem the general preset needed to solve, and didn't need a new gate for**:
marking an entire column (not one cell) as "the claim" using a *single* rect spanning all its
rows, rather than one accent per cell — three separately-accented Fission cells would have
consumed the entire 2-accent budget on the marked column alone, `verify-accent-budget.py`'s
per-position node dedup treating each as independent. One tall rect behind the whole column
is both the honest visual claim (this is a *column-level* fact, not three cell-level facts) and
the only way to stay in budget on anything larger than a trivial grid.

**The grid holds with zero drawn lines**, per the brief's own "test whether the grid can hold
with no lines at all" challenge — answered yes, using alternating row background tints plus
column gaps (negative space, not stroked rules) for all cell-boundary structure. This is the
second type (after Contrast) to use fills-only structure instead of ruled lines, and the pattern
generalizes: a grid-shaped claim rarely needs a drawn grid to read as one.

**Reverse.** `git mv type-matrix.md type-dp-security-matrix.md`, delete the General preset
section and its `## Which variant` header (restoring the original single-preset doc), delete
the three `example-matrix*.html` files and the `matrix` gallery tab, revert `routing.md`'s row
back to "DP security matrix," and revert the SKILL.md frontmatter hook and `type-it-state.md`'s
cross-reference.

---

## D38 — Hub & spoke lands as a semantic pattern, not a type — no new example files needed

**Phase:** 3 (M2 archetypes) — the seventh and final Phase 3 item.

**Choice.** Per the execution plan's own framing, Hub & spoke is "drawable freehand in our
architecture type, but with no grammar, so every attempt looks different" — the gap was a
missing *convention*, not a missing layout grammar Architecture couldn't express. Landed as
`## 8. Hub & spoke` in `semantic-patterns.md`, following the exact six-field shape (Selection
triggers / Required primitives / Complexity budget / Anti-patterns / Static fallback / Nearest
visual type) every other pattern already uses, plus a `routing.md` row. This is the one Phase 3
item that shipped with **no new `example-*.html` files and no new `type-*.md`** — a semantic
pattern describes composition rules layered onto an existing type's own examples, not a
separate set of worked diagrams, consistent with how the other 7 patterns work (each routes to
an existing type — Data flow, Process, Flowchart, Architecture, Layer stack — none of them ship
dedicated pattern-specific example files either).

**Direction (serves vs. feeds) stated via arrowhead/line style, not spoke appearance** — spokes
must stay visually uniform regardless of direction, since their interchangeability is the entire
point; varying a spoke's look by whether it serves or feeds the hub would reintroduce exactly
the false hierarchy the pattern exists to prevent.

**Caught while landing this: `PATTERN_NAMES` in `verify-semantic-motion.py` is a literal
8-tuple gate scripts must extend by hand each time a pattern is added** — same shape as the
visual-type count problem D31–D37 kept re-encountering, just for patterns instead of types. Added
`"Hub & spoke"` to the tuple, fixed the hardcoded `"7 semantic patterns"` print statement to `8`,
and updated `README.md`'s "seven routed patterns" prose to "eight." No test in
`test-verify-motion.py` hardcoded the pattern count, so nothing else needed updating there.

**Reverse.** Delete the `## 8. Hub & spoke` section and its `Composition rules` boundary shift
in `semantic-patterns.md`, remove its `routing.md` row, drop `"Hub & spoke"` from
`verify-semantic-motion.py`'s `PATTERN_NAMES` tuple (reverting the print statement to "7"), and
revert `README.md`'s prose back to "seven."

---

## D39 — M2.2: relation vocabulary added to routing.md, not a further SKILL.md rewrite

**Phase:** 4 (M2.2 routing, M2.4 selection/gallery)

**Choice.** The execution plan's M2.2 line item reads "`references/routing.md` plus the
`SKILL.md` §3 rewrite." The `routing.md` creation and the §3 shortening both already happened
during Phase 3 (D36), out of necessity when `SKILL.md` hit its byte cap mid-Deployment-PR — so
the mechanical half of M2.2 was already done. What remained was the actual content M2.2 exists
to deliver: a **relation vocabulary** the gallery (M2.4) can group by, since "the relation
vocabulary exists" is M2.4's stated dependency on M2.2.

Added a **Relation** column to `routing.md`'s 32-row visual-type guide — one word per type
(`Topology`, `Detail-of`, `Differs-from`, `Derives-from`, `Assembled-from`, `Runs-on`,
`Branches`, `Sequences`, `Transitions`, `Structures`, `Positions`, `Recurs`, `Contains`,
`Overlaps`, `Narrows`, `Compares`, `Flows-to`, `Combines` — 18 distinct relations across 32
types). Several relations are shared by design, not by accident: every temporally-ordered type
(Sequence, Timeline, Swimlane, Gantt, Process) sits under **Sequences** because the relation
really is the same one; what differs between them is which secondary thing is load-bearing
(actors and messages, bare event dates, task duration). A shared relation label is the
system correctly saying "you have the right relation, now pick by what else matters" — not a
sign two types are redundant.

**No further `SKILL.md` §3 rewrite was needed.** The plan's own reasoning for the rewrite was to
avoid touching §3 "seven more times as types land" during Phase 3 — that reasoning is now moot
since Phase 3 is closed and §3 already reads as a short pointer to `routing.md`. Re-expanding §3
to restate the relation vocabulary inline would just re-spend the bytes D36 freed for no reader
benefit, since `routing.md` is one link away and already the canonical home for both tables.

**A real regex bug surfaced immediately**: `verify-docs-sync.py`'s `selection_table_types()`
assumed the type name sat in the table's *second* column (`^\|[^|]*\|\s*\*\*name\*\*`) — true
before this change, false the moment a Relation column became the first column. Fixed to skip
any number of leading columns via a non-greedy repeating group
(`^\|(?:[^|]*\|)+?\s*\*\*name\*\*\s*\|\s*\[`), anchored on the **Reference** column's opening
`[` immediately after the name so it can't accidentally match into a later column. This is the
same class of "measured naively, re-derive from what the check actually protects" bug this log
has caught repeatedly (D22, the two `verify-grid.py` fixes in D30) — column position was never
the real invariant; "the type name is followed by its reference link" was.

**Reverse.** Remove the Relation column and its explanatory paragraph from `routing.md`, revert
`verify-docs-sync.py`'s `selection_table_types()` regex to the fixed-second-column version.

---

## D40 — M2.4: gallery reindexed by relation, presets and demos kept as labeled non-relation groups

**Phase:** 4 (M2.2 routing, M2.4 selection/gallery)

**Choice.** Restructured `assets/index.html`'s flat, numbered 39-tab strip into relation-labeled
groups matching D39's vocabulary exactly — each group is a `<div class="tab-group">` with a
`group-label` heading, and each canonical type's button carries a `data-reach` attribute holding
its routing.md trigger text verbatim, displayed in a new subtitle line (`#reach-line`) that
updates on click. Per the M2.4 design doc's explicit scope (`docs/plans/2026-08-14-selection-
guidance-and-gallery-design.md` §6), this does **not** invent new layout-variant examples
(a fish-eye Zoom, a second Contrast layout, a 4-way Deployment abbreviation menu) that don't
exist yet — only Code level and Matrix currently have genuine multiple presets, and both already
carry their own `## Which variant` section in their type doc, built during Phase 3.

**Presets sit inside their parent type's relation group, not as separate relation entries.**
`class` (Code level's class preset), `dp-security-matrix` (Matrix's permissions preset),
`quadrant-consultant`, `loop-terminal`, `sequence-oauth`, and `high-level-vertical` all render
next to their parent type's tab within the same group — a preset doesn't introduce a new
relation, it's a different scenario for the same one.

**`datalake` turned out to be an undocumented Architecture scenario, confirmed by reading its own
`<title>`/`<desc>`** ("Open data lake · Architecture") rather than guessed from its gallery tab
position — it had no reference-doc mention anywhere before this. Placed in Topology next to
Architecture, labeled `data-reach="Open data lake — a worked Architecture scenario"` so it no
longer sits undocumented; not otherwise touched, since giving it a full preset write-up is out of
this PR's scope.

**Imports and motion demos get their own trailing group, explicitly labeled "capability, not a
relation.**" `import-drawio`, `import-mermaid`, and the three `-animated` examples answer "can
this redraw a source" or "does this support motion" — a different kind of question than "what
relation do I have" — so folding them into a relation group would misrepresent what they
demonstrate.

**The tab strip gained an internal scroll (`max-height: 34vh`) rather than growing the header
unbounded** — 18 relation groups plus a demos group is taller than the original 39-tab flat wrap,
and letting the header consume unbounded viewport height would starve the iframe preview on
shorter screens. Verified via Playwright that scrolling within `#type-tabs` reaches every group
including the trailing ones, and that tab-click behavior (active state, reach-line update,
single-variant disabling) all work identically to the pre-restructure version.

**Reverse.** Revert `assets/index.html` to the flat numbered tab list (drop the `tab-group`/
`group-label` wrapper markup, the `data-reach` attributes, the `#reach-line` element and its CSS,
and the `update()` JS's `reachLine.textContent` line).

---

## D41 — M2.5 set spine: schema and docs land first, gate follows in its own PR

**Phase:** 5 (M2.5 set spine, Pages enablement)

**Choice.** Split M2.5 into two PRs rather than one: this one ships the `<meta name="diagram:*">`
schema, the C4-derived level ladder, the `data-element-id` convention, and
`references/diagram-sets.md` documenting all of it plus commented-out meta blocks in all 5
templates so the shape is discoverable at the point an author would reach for it. The
verification gate (`scripts/verify-set.py`, its tests, and the generated `docs/diagram-map.md`)
follows as its own PR — the schema is stable and reviewable on its own, and splitting keeps each
PR focused the same way every Phase 3 archetype PR did.

**Zero real files adopt the schema in this PR, by design.** The feature is explicitly opt-in
(per the design doc's own scope: "Enforcing that a set exists" is out of scope) — a file with no
`diagram:` meta tags is simply not part of a set, so there is nothing to retrofit onto the
existing 32-type, 100+-file corpus to make this land. The gate PR's tests will use synthetic
fixtures, matching every other `verify-*.py`/`test-verify-*.py` pair built in Phase 2c, rather
than requiring real-corpus adoption to prove the checks work.

**`README.md`'s architecture-tree gate caught a real ordering mistake immediately**: naming
`verify-set.py` in the tree's annotation comment before the file existed failed
`verify-docs-sync.py`'s check that every filename mentioned in the tree actually exists — a
useful confirmation that the check works on prose within annotations, not just the tree's own
file-listing lines. Fixed by describing the not-yet-built gate generically ("verification gate")
rather than naming it ahead of its own PR.

**Reverse.** Delete `references/diagram-sets.md`, revert the `SKILL.md` §12 addition and the
`README.md` architecture-tree line, and remove the commented meta block from all 5 templates.

---

## D42 — verify-set.py: check 6 redefined around the id convention, the one check that must

**Phase:** 5 (M2.5 set spine, Pages enablement)

**Choice.** Built `scripts/verify-set.py` (checks 1–7) and `scripts/test-verify-set.py`, and
found a real design flaw in the spec's own framing of check 6 while writing the adversarial
tests for it, not while writing the checker itself — a useful reminder that tests are where an
underspecified check gets caught, not code review of the implementation alone.

**"Exactly one root per connected set," read as "connected component of the parent graph,"
can never fire.** A diagram declares at most one `diagram:parent`, which makes the parent graph
a *forest* by construction — every node has 0 or 1 parents, so a connected component (built by
walking parent and child edges) is always a valid tree with exactly one root. There is no input
that produces two roots in one such component; the check as originally read is vacuously true
always, which I only discovered by trying and failing to construct a failing test case for it.

**Redefined "set" for this one check as "diagrams sharing the first dotted segment of
`diagram:id`"** (`ingest-platform.transform` and `ingest-platform.warehouse` both claim the
`ingest-platform` set) instead of graph-connectivity. This is the only grouping under which the
check can produce a real, catchable error — two diagrams both claiming to be `ingest-platform`'s
root with no parent, or every member of a claimed set having a parent (an internally cyclic or
mis-rooted set). `docs/diagram-sets.md`'s own claim that "the dotted-path id convention is a
convention, not a constraint the gate enforces" no longer holds without qualification — amended
to note check 6 is the one exception, and why it has to be.

**Regenerating `docs/diagram-map.md` against the full corpus produced the trivial empty-state
message**, since the feature is genuinely opt-in and zero shipped files declare `diagram:id` —
exactly the expected initial state per D41, not a bug.

**A second real bug, caught before it shipped**: the initial implementation didn't strip HTML
comments before scanning for `<meta name="diagram:...">` tags, so the commented-out placeholder
blocks the previous PR added to all 5 templates were parsed as five *live*, mutually duplicate
diagrams — the very first `--all` run against the real corpus failed with 6 errors. Fixed with
the same "blank out the matched span, preserve offsets" technique `verify-no-diagonal.py` uses
for masking nested icon `<svg>` subtrees.

**Reverse.** Delete `scripts/verify-set.py`, `scripts/test-verify-set.py`, and `docs/diagram-
map.md`; remove the three CONTRIBUTING.md rows and run-chain lines, the three CI steps and their
summary rows, and the three `suite.sh` lines; revert `diagram-sets.md`'s check-6 row and the
"convention, not a constraint" amendment.
