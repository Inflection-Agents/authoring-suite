# Contributing to Diagram Design

Thanks for wanting to contribute — this project only gets better with more eyes on it.

Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) first. All contributions are expected to keep the community welcoming.

---

## What this project is

Diagram Design is an agent skill (Claude Code, Codex, Pi) that produces editorial-quality diagrams as self-contained HTML files. The repo is documentation-first: `skills/diagram-design/SKILL.md` is the index, each of the 32 visual types has its own reference file, and the extractor scripts in `skills/diagram-design/scripts/` turn draw.io and Mermaid sources into a structured IR.

See [README.md](README.md) for the full picture, including the design system and the import/export flows.

---

## Before you start

- **Create an issue first** for anything non-trivial (new type, behavior change, import grammar work). Small fixes and docs can go straight to a PR.
- **Work on a branch** — never commit directly to `main`.
- **Keep the scope tight.** One PR = one concern. Mixing a new diagram type with a docs rewrite makes review slow.
- **Python 3.10+ is required** for the development scripts (CI runs 3.11 and 3.12 across Linux, Windows, and macOS).

---

## Validation gates

Every validation gate below must pass before a PR is ready. They also run automatically as GitHub Actions CI (`.github/workflows/ci.yml`).

Every PR changes the distributed plugin package, including documentation- and CI-only PRs. Increment both native manifests together before opening or updating a PR:

```bash
python3 scripts/bump-plugin-version.py          # patch (default)
python3 scripts/bump-plugin-version.py --minor  # minor release
python3 scripts/bump-plugin-version.py --major  # major release
```

The helper refuses to run if the Claude and Codex versions already differ. If another release lands on `main` first, rebase and bump again so your version remains greater than the new base.

| What it checks | Command |
|---|---|
| Plugin bump helper and adversarial package cases | `python3 scripts/test-plugin-package.py` |
| Synchronized, increasing versions; valid marketplace paths; packaged skill | `python3 scripts/verify-plugin-package.py origin/main` |
| Claude marketplace and plugin schema, with warnings treated as errors | `claude plugin validate . --strict` |
| Accessible SVG contract (unit tests for the a11y linter) | `python3 scripts/test-lint-a11y.py` |
| Semantic-pattern routing | `python3 scripts/verify-semantic-motion.py --markdown-only` |
| Animated-example structure and accessibility | `python3 scripts/verify-semantic-motion.py --example-only` |
| Skin conformance of every example and template (colors, fonts, a11y, assets, scripts) | `python3 scripts/lint-skin.py --all --baseline` |
| A single file, e.g. a new example | `python3 scripts/lint-skin.py skills/diagram-design/assets/example-my-type.html` |
| Sequence-doc consistency (ATL fragments, budgets) | `python3 scripts/verify-sequence-oauth.py` |
| draw.io import path (real extractor vs fixtures + docs sync) | `python3 scripts/verify-drawio-import.py` |
| Mermaid import path (grammars, adversarial input, caps, docs sync) | `python3 scripts/verify-mermaid-import.py` |
| Optional motion contract (fallbacks, controls, budgets, determinism) | `python3 scripts/test-verify-motion.py` |
| Every shipped motion template/example | `python3 scripts/verify-motion.py --shipped` |
| Docs/routing sync (description hooks, gallery reachability, README tree) | `python3 scripts/verify-docs-sync.py` |
| Packaged output self-check behaves (pass + adversarial cases) | `python3 scripts/test-self-check.py` |
| Diagram geometry: clipped masks, labels sitting on their connector, nodes breaking out of a container | `python3 scripts/verify-geometry.py --all --baseline` |
| Geometry checker behaves (both polarities, every check) | `python3 scripts/test-verify-geometry.py` |
| Skin generation from the style guide (contract coverage, both variants) | `python3 scripts/test-build-skins.py` |
| Hex-to-token codemod (packed declarations, variant detection, `color-mix` exactness) | `python3 scripts/test-migrate-to-tokens.py` |
| Generated skin files are up to date (`assets/skins/active-*.tokens.css`) | `python3 scripts/build-skins.py` then `git diff --exit-code` on `skills/diagram-design/assets/skins/` |
| Generated icon assets are up to date (`icons.html`, `primitive-icons.md`) | `python3 scripts/build-icons.py` then `git diff --exit-code` on the two generated files |
| No diagonal `<line>` between off-axis nodes | `python3 scripts/verify-no-diagonal.py --all` |
| Diagonal-connector checker behaves (pass + adversarial cases) | `python3 scripts/test-verify-no-diagonal.py` |
| Tag consistency — a file that tags one node tags all comparable ones | `python3 scripts/verify-tag-consistency.py --all` |
| Tag-consistency checker behaves (pass + adversarial cases) | `python3 scripts/test-verify-tag-consistency.py` |
| Compartment lines never transcribe a field type (colon or bracket), capped at 3 lines | `python3 scripts/verify-no-transcription.py --all` |
| Transcription checker behaves (pass + adversarial cases) | `python3 scripts/test-verify-no-transcription.py` |
| Structural 4px grid, grandfathered | `python3 scripts/verify-grid.py --all --baseline` |
| Grid checker behaves (pass + adversarial cases) | `python3 scripts/test-verify-grid.py` |
| Accent budget (≤2 distinct elements per diagram), grandfathered | `python3 scripts/verify-accent-budget.py --all --baseline` |
| Accent-budget checker behaves (pass + adversarial cases) | `python3 scripts/test-verify-accent-budget.py` |
| Diagram-set spine is referentially sound (opt-in; regenerates `docs/diagram-map.md`) | `python3 scripts/verify-set.py --all` |
| `docs/diagram-map.md` is up to date | `git diff --exit-code -- docs/diagram-map.md` |
| Diagram-set verifier behaves (pass + adversarial cases) | `python3 scripts/test-verify-set.py` |

The semantic-pattern gate also caps `skills/diagram-design/SKILL.md` at 40,000 bytes so the installed skill remains practical to load. If that gate fails, reduce duplication or move detail into a routed reference; do not remove routing vocabulary from frontmatter.

Run them all at once before pushing:

```bash
python3 scripts/test-plugin-package.py \
  && python3 scripts/verify-plugin-package.py origin/main \
  && claude plugin validate . --strict \
  && python3 scripts/test-lint-a11y.py \
  && python3 scripts/verify-semantic-motion.py --markdown-only \
  && python3 scripts/verify-semantic-motion.py --example-only \
  && python3 scripts/verify-motion.py --shipped \
  && python3 scripts/lint-skin.py --all --baseline \
  && python3 scripts/verify-sequence-oauth.py \
  && python3 scripts/verify-drawio-import.py \
  && python3 scripts/verify-mermaid-import.py \
  && python3 scripts/test-verify-motion.py \
  && python3 scripts/verify-docs-sync.py \
  && python3 scripts/test-self-check.py \
  && python3 scripts/verify-geometry.py --all --baseline \
  && python3 scripts/test-verify-geometry.py \
  && python3 scripts/test-build-skins.py \
  && python3 scripts/test-migrate-to-tokens.py \
  && python3 scripts/build-skins.py \
  && git diff --exit-code -- skills/diagram-design/assets/skins/ \
  && python3 scripts/build-icons.py \
  && git diff --exit-code -- skills/diagram-design/assets/icons.html skills/diagram-design/references/primitive-icons.md \
  && python3 scripts/verify-no-diagonal.py --all \
  && python3 scripts/test-verify-no-diagonal.py \
  && python3 scripts/verify-tag-consistency.py --all \
  && python3 scripts/test-verify-tag-consistency.py \
  && python3 scripts/verify-no-transcription.py --all \
  && python3 scripts/test-verify-no-transcription.py \
  && python3 scripts/verify-grid.py --all --baseline \
  && python3 scripts/test-verify-grid.py \
  && python3 scripts/verify-accent-budget.py --all --baseline \
  && python3 scripts/test-verify-accent-budget.py \
  && python3 scripts/verify-set.py --all \
  && git diff --exit-code -- docs/diagram-map.md \
  && python3 scripts/test-verify-set.py
```

### If a gate fails

- **`verify-plugin-package.py`:** run the bump helper if the versions did not increase. If packaging validation fails, keep both marketplaces pointed at the repository root and keep the shared skill at `skills/diagram-design/SKILL.md`.
- **`lint-skin.py`:** the failure message names the file, line, and category (`color`, `font-family`, `a11y`, `external-asset`, `pure-black`, `script`). Colors must come from the palette in `skills/diagram-design/references/style-guide.md` and should be bound through the `--dd-*` token contract (see below); fonts from the allowed list; diagrams must satisfy the accessible SVG contract (see below). The linter also requires the SHA-pinned controller from `template-motion.html` verbatim and rejects remote resources, CSS `@import`, non-fragment CSS `url()`, event handlers, `srcdoc`, executable URLs, and extra scripts.
- **`verify-*.py`:** the extractor's real behavior no longer matches its fixture or the documentation, or the reference/command/prompt wiring drifted. Fix the source of truth — do not widen a test to avoid a failure.
- **`verify-geometry.py`:** one of three defects. `clipped-mask` — a label mask overlaps a node declared later in the document, so the node fill clips the label at render time. `masked-edge` — a label mask sits on the connector it names instead of the 6–10px clear SKILL.md §6 rule 2 requires, so the label hides its own arrow. `broken-out` — a node's body leaves the container holding its centre. Move the label to a free segment of its connector, or resize the box; do not shrink the mask to sneak under the check. The predicates ship with the skill in `skills/diagram-design/scripts/verify_geometry.py` so authors can measure their own output (ADR 0011); this script is the CI entry point over the shipped assets.
- **`geometry-baseline.txt`:** the grandfather list for the checks added in v2.4, under the same rule as `grid-baseline.txt` — it only ever shrinks. Never add a file to dodge a fresh violation.
- **Icon assets:** you changed `scripts/vendor/icons/` or `scripts/build-icons.py` and the generated files went stale. Rerun `python3 scripts/build-icons.py` and commit the regenerated files.
- **Skin assets:** you changed a token table in `references/style-guide.md` and the generated skins went stale. Rerun `python3 scripts/build-skins.py` and commit the regenerated files. Never hand-edit `assets/skins/*.tokens.css` — `style-guide.md` is the source of truth.

Do **not** add a file to `scripts/lint-skin-baseline.txt` to get your example through. The baseline exists only for legacy pre-2.0 examples that legitimately predate the current skin, and it still receives a11y checks.

---

## The accessible SVG contract (a11y)

Every diagram `<svg>` must satisfy the contract enforced by the linter:

1. `role="img"` and `aria-labelledby` naming the `<title>` **and** `<desc>`.
2. `<title>` is the **first child** of `<svg>` (before `<defs>`).
3. IDs are prefixed per diagram and variant: `<slug>-title` / `<slug>-desc` — for `example-loop-dark.html` the slug is `loop-dark`, so the IDs are `loop-dark-title` / `loop-dark-desc`. Bare `title`/`desc` IDs and duplicate IDs are rejected.
4. `<title>` is the short subject name (≈ the `<h1>`, ≤ 60 chars); `<desc>` is one sentence describing the *content*, not the geometry.
5. Purely decorative SVGs (`aria-hidden="true"`) are exempt.

The contract lives in `scripts/lint-skin.py` (`lint_accessible_svgs`) and is unit-tested by `scripts/test-lint-a11y.py`. When in doubt, pattern-match an existing example.

---

## The `--dd-*` token contract

Colour and radius are bound through CSS custom properties so a diagram can be reskinned by
replacing one `:root` block instead of editing every attribute. The contract is defined once, in
`CONTRACT` in `scripts/build-skins.py`, and generated from `references/style-guide.md` into
`skills/diagram-design/assets/skins/active-{light,dark}.tokens.css`.

Rules the linter enforces:

1. Every `var(--dd-…)` must name a contract role. Unknown token names are rejected.
2. A file that references any `--dd-*` must declare **all** of them — paste the generated block
   whole. A partial skin is rejected, because a half-defined skin fails silently at render time.
3. Values still have to come from the style-guide palette; the token layer does not exempt a raw
   hex from the colour check.

Authoring notes:

- Prefer `fill="var(--dd-ink)"`. For a translucent shade with no named role, use
  `color-mix(in srgb, var(--dd-ink) 25%, transparent)` — it resolves to exactly the `rgba()` it
  replaces. The six named `--dd-wash-*` roles cover the node-treatment fills in `SKILL.md` §5.
- Radius rides a class (`dd-node`, `dd-tag`, `dd-container`) with the literal `rx` attribute kept as
  a Safari fallback, since `rx` as a CSS geometry property landed late there.
- The terminal window is a **second, fixed skin** and is deliberately outside the contract. Do not
  convert `template-terminal.html` or `example-loop-terminal.html`.

`scripts/migrate-to-tokens.py` performs the conversion mechanically and reports any colour no
contract role can express, rather than guessing.

## Working on examples (diagrams)

Every diagram type ships three variants: minimal light (`example-<type>.html`), minimal dark (`example-<type>-dark.html`), and full editorial (`example-<type>-full.html`).

1. Copy the closest template (`skills/diagram-design/assets/template.html`, `template-dark.html`, or `template-full.html`).
2. Load the matching `references/type-<name>.md` and follow its layout conventions.
3. Replace the eyebrow, h1, and SVG body; replace the `[diagram-slug]` placeholders with your file's slug and keep the `<title>`/`<desc>` slots filled.
4. Run the taste gate in `SKILL.md` §9, then the linter:

```bash
python3 scripts/lint-skin.py skills/diagram-design/assets/example-my-type.html
```

New examples should be added to the gallery (`assets/index.html`) so they stay browsable.

Motion is opt-in. Start from `skills/diagram-design/assets/template-motion.html`, follow `references/animation.md`, and run `python3 scripts/verify-motion.py <file>` plus `python3 scripts/test-verify-motion.py`. A motion file must preserve complete no-JavaScript, reduced-motion, print, screenshot, and export states. Keep the controller byte-for-byte identical to the template; changes require updating the canonical template, example, documentation, and adversarial tests together.

## Design decisions (ADRs)

Settled policies live as short records in `docs/adr/` — one pinned motion controller, semantic patterns never expanding the 27-type taxonomy, the reveal-only autoplay rule, the SKILL.md byte cap with its trigger-rich description requirement, geometric label placement being verified rather than reviewed, colour binding through the `--dd-*` token contract, brand dark palettes overriding the inversion rule, and the grid-versus-brand split. Read the relevant ADR before proposing a change that touches one; when a PR settles a new policy, add an ADR in the same PR.

## Adding a new diagram type

1. Write `skills/diagram-design/references/type-<name>.md` — layout conventions, anti-patterns, and a worked pattern for that type. Mirror an existing reference's structure.
2. Add the row to the selection table in `skills/diagram-design/SKILL.md` §3 **and** the type's name to the frontmatter `description` — `verify-docs-sync.py` fails if the description loses or lacks a type's lexical hook.
3. Add the three example variants (see above) and register them in the gallery (`assets/index.html`) — `verify-docs-sync.py` fails on any shipped example the gallery can't reach.
4. Run the full gate suite — new examples are linted automatically by `--all`.

## Regenerating the README screenshots

`docs/screenshots/` is generated from the shipped examples. It is **not** a CI gate — it needs
Playwright and a real browser, and rendering is not deterministic enough across platforms to diff.
Rerun it by hand after any change to the skin or to a screenshotted example, or the README quietly
advertises a palette the project no longer ships:

```bash
pip install playwright && playwright install chromium
python3 scripts/build-screenshots.py
```

## Changing the icon set

Icons are generated, never hand-edited:

1. Add or replace the source SVG in `scripts/vendor/icons/<source>/` (`tabler/`, `simple/`, …). Keep license provenance in `THIRD_PARTY_LICENSES.md` accurate.
2. Regenerate and verify:

```bash
python3 scripts/build-icons.py
git diff --exit-code -- skills/diagram-design/assets/icons.html skills/diagram-design/references/primitive-icons.md
```

## Touching the import paths

- draw.io: `skills/diagram-design/scripts/drawio_extract.py` — must pass `scripts/verify-drawio-import.py`, which drives the extractor against `scripts/fixtures/sample-architecture.drawio` in all four container formats (raw XML, deflate+base64, PNG-embedded, SVG-embedded).
- Mermaid: `skills/diagram-design/scripts/mermaid_extract.py` — must pass `scripts/verify-mermaid-import.py`, which covers every supported grammar, multi-block Markdown, adversarial labels, trust-boundary behavior, resource caps, and named failures.

Both scripts treat their input as **untrusted data** — they never render, fetch, or execute source content. Keep it that way. If you add a grammar or a new security boundary, extend the corresponding verifier with a fixture before merging.

Documentation and wiring must stay in sync: the import references, `SKILL.md` §11, the slash commands in `commands/`, and the Pi prompt templates in `prompts/` each describe the same flows. The verifiers check this — keep both sides updated in one PR.

## Documentation

Most of this repo *is* documentation. When behavior changes, update the affected reference files and the README in the same PR. Loose ends here are what the verifiers and reviewers will catch.

---

## Commit and PR conventions

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): summary`, e.g. `fix(import): support current Mermaid syntax`, `ci: verify Mermaid imports`, `docs(onboarding): clarify the URL flow`. Keep summaries short and imperative.

A good PR:

- has a clear title and a description that says *what* changed and *why*;
- mentions how you tested it (which gates you ran);
- keeps generated and source files consistent (extractor + verifier + reference + command in one change);
- is rebased on `main` and green on CI.

## Questions?

Open a discussion or comment on the relevant issue. If it's about security, use the private reporting path in [SECURITY.md](SECURITY.md).
