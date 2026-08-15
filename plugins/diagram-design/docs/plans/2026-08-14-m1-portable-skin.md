# M1 Portable Skin Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the diagram skin swappable by binding every generated colour to a `--dd-*` CSS custom property, and ship the Inflection Agents brand as the default skin.

**Architecture:** `references/style-guide.md` stays the canonical source of token values. A new `scripts/build-skins.py` generates `assets/skins/*.tokens.css` from it, guarded by `git diff --exit-code` exactly like `build-icons.py`. Generated diagrams inline that skin block into `:root` and reference it with `var(--dd-*)` in the SVG body, so a reskin is a 14-line swap instead of 84 hand edits per file. `lint-skin.py` gains token-name and coverage validation.

**Tech Stack:** Python 3.10+ (stdlib only — no new dependencies), HTML/CSS/SVG, Playwright (already required by PNG export, used once for the PR 3 raster check).

---

## Before you start

**Read these first:**
- `docs/plans/2026-08-14-portable-skin-and-archetypes-design.md` — the approved design. Sections 3, 4, and 5 define the token contract and the Inflection values; do not re-derive them.
- `CONTRIBUTING.md` — the 16 validation gates and the version-bump rule.
- `docs/adr/0002-semantic-patterns-do-not-expand-the-taxonomy.md` — explains why M1 adds no types.

**Key facts about this repo you will not guess:**
- Tests are plain Python scripts, **not pytest**. They `raise AssertionError` on failure, `print("PASS: …")` on success, and end with `raise SystemExit(main())`. Run them directly: `python3 scripts/test-foo.py`.
- Scripts with hyphens in the name are loaded in tests via `importlib.util.spec_from_file_location`. Copy the loader from `scripts/test-build-icons-devicon.py`.
- **Every PR must bump both plugin manifests** with `python3 scripts/bump-plugin-version.py`. CI fails otherwise. Do this as the last commit of each PR.
- **Check your interpreter before running anything.** These gates need Python 3.10+ (`zip(strict=)`,
  PEP 604 `str | None`). On macOS, `python3` is often the system 3.9, which fails with confusing
  `TypeError`s that look like code bugs rather than version errors — `lint-skin.py` crashes on a
  dataclass annotation and takes three verifiers down with it. Run `python3 --version` first, and if
  it is below 3.10 use an explicit interpreter (e.g. `/opt/homebrew/bin/python3.12`) for every command
  in this plan.
- `bump-plugin-version.py` takes `--minor` or `--major`; **patch is the default and there is no
  `--patch` flag.**
- `lint-skin.py` scans the **entire file** for hex literals and allows any hex present in the `style-guide.md` tables. So a `:root` block full of palette hexes passes today, and `var(--dd-x)` passes trivially because it contains no hex. The new checks in Task 7 are therefore **additive** — the migration cannot break the existing linter.

**Baseline the gates before touching anything:**

```bash
python3 scripts/lint-skin.py --all --baseline && python3 scripts/verify-docs-sync.py
```

Expected: both exit 0. If they do not, stop and fix that first — you need a green baseline to attribute later failures.

**The full suite** (referenced below as *run the full suite*) is the 16-command chain in `CONTRIBUTING.md` § "Run them all at once before pushing".

---

## PR 1 — Fork identity

Branch: `chore/fork-identity`. No behaviour change.

### Task 1: Repoint the plugin manifests

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `.codex-plugin/plugin.json`

**Step 1: Edit `.claude-plugin/plugin.json`**

Change only these keys. Leave `name`, `version`, `description`, and `keywords` alone.

```json
  "author": {
    "name": "Inflection Agents",
    "url": "https://github.com/Inflection-Agents"
  },
  "homepage": "https://github.com/Inflection-Agents/diagram-design",
  "repository": "https://github.com/Inflection-Agents/diagram-design",
```

**Step 2: Edit `.codex-plugin/plugin.json`**

Same three keys, plus inside `interface`:

```json
    "developerName": "Inflection Agents",
    "websiteURL": "https://github.com/Inflection-Agents/diagram-design",
    "brandColor": "#967A3A"
```

**Step 3: Verify the manifests still validate**

Run: `claude plugin validate . --strict`
Expected: exits 0, no warnings.

**Step 4: Verify versions are still synchronized**

Run: `python3 scripts/test-plugin-package.py`
Expected: `PASS` lines, exit 0.

**Step 5: Commit**

```bash
git add .claude-plugin/plugin.json .codex-plugin/plugin.json
git commit -m "chore(identity): repoint plugin manifests to Inflection-Agents"
```

### Task 2: Attribution and security contact

**Files:**
- Modify: `README.md`
- Modify: `SECURITY.md`
- Verify unchanged: `LICENSE`

**Step 1: Confirm `LICENSE` still carries the upstream copyright**

Run: `grep -c "Copyright (c) 2025 Cathryn Lavery" LICENSE`
Expected: `1`. MIT requires that notice to survive verbatim. This checks the obligation directly
rather than diffing against a remote — the `upstream` remote was deliberately removed so no local
path can push to or open a PR against the original repository.

**Step 2: Add an Attribution section to `README.md`**

Append at the end of the file:

```markdown
## Attribution

This project is a fork of [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design),
released under the MIT License, copyright (c) 2025 Cathryn Lavery. The original
copyright notice is retained in [LICENSE](LICENSE).

This fork is maintained by Inflection Agents and diverges from upstream: it ships
the Inflection Agents brand skin by default and adds a portable token system.
Changes are not submitted upstream.
```

**Step 3: Update `SECURITY.md`**

Replace the private reporting path with the Inflection Agents channel. Keep the document's structure; change only the contact.

**Step 4: Verify docs sync still passes**

Run: `python3 scripts/verify-docs-sync.py`
Expected: exits 0. This gate checks README structure — if it fails, the appended section broke a tree it validates; move the Attribution section above that tree.

**Step 5: Commit**

```bash
git add README.md SECURITY.md
git commit -m "docs(identity): add fork attribution and security contact"
```

### Task 3: Bump and close PR 1

**Step 1: Bump both manifests**

Run: `python3 scripts/bump-plugin-version.py`
Expected: prints the new version (`2.3.6`) for both manifests.

**Step 2: Run the full suite**

Expected: all 16 gates exit 0.

**Step 3: Commit and open the PR**

```bash
git add .claude-plugin/plugin.json .codex-plugin/plugin.json
git commit -m "chore(release): bump plugin version to 2.3.6"
git push -u origin chore/fork-identity
gh pr create --title "chore: fork identity and attribution" --body "Repoints manifests to Inflection-Agents, adds MIT attribution, updates the security contact. No behaviour change. Gates: full suite green."
```

---

## PR 2 — Token contract and skin generation

Branch: `feat/token-contract`. No visual change.

### Task 4: Add the wash and geometry roles to the style guide

**Files:**
- Modify: `skills/diagram-design/references/style-guide.md`

**Step 1a: Add `node-white` to the Semantic roles table**

Insert a row into the existing "Semantic roles" table:

```markdown
| `node-white` | Backend / API / step node fill | `#ffffff` | `#ffffff` |
```

`SKILL.md` §5 already specifies a white fill for these nodes; the role simply had no name. Keep the
value identical in light and dark — a backend node is white in both skins today, and changing that
is a visual decision, not a portability one.

**Step 1: Add a Wash roles table**

Insert after the "Semantic roles" table, before "Inversion rule". Values are the current defaults expressed literally so nothing changes visually.

```markdown
### Wash roles

Fixed-opacity derivations used by the node-treatment table. Named rather than computed so the
linter stays simple and no `color-mix()` support is assumed.

| Role | Derived from | Default (light) | Default (dark) |
|---|---|---|---|
| `wash-2` | `ink @ 0.02` | `rgba(45,49,66,0.02)` | `rgba(245,245,245,0.02)` |
| `wash-3` | `ink @ 0.03` | `rgba(45,49,66,0.03)` | `rgba(245,245,245,0.03)` |
| `wash-5` | `ink @ 0.05` | `rgba(45,49,66,0.05)` | `rgba(245,245,245,0.05)` |
| `wash-10` | `muted @ 0.10` | `rgba(79,93,117,0.10)` | `rgba(191,192,192,0.10)` |
| `wash-20` | `ink @ 0.20` | `rgba(45,49,66,0.20)` | `rgba(245,245,245,0.20)` |
| `wash-30` | `ink @ 0.30` | `rgba(45,49,66,0.30)` | `rgba(245,245,245,0.30)` |
```

**Step 2: Add a Geometry roles table**

Insert directly after the Wash roles table:

```markdown
### Geometry roles

Radius is tokenized so a brand with a sharper corner register can be expressed.

| Role | Default | Use |
|---|---|---|
| `radius-node` | `6` | Node boxes |
| `radius-tag` | `2` | Type tags, label masks |
| `radius-container` | `8` | Zones, rings, containers |
```

**Step 3: Verify the linter still reads the palette**

Run: `python3 scripts/lint-skin.py --all --baseline`
Expected: exits 0. The wash values are `rgba()` of colours already in the palette, so `allowed_colors()` is unaffected.

**Step 4: Commit**

```bash
git add skills/diagram-design/references/style-guide.md
git commit -m "docs(style-guide): add wash and geometry token roles"
```

### Task 5: Write the failing test for the skin builder

**Files:**
- Create: `scripts/test-build-skins.py`

**Step 1: Write the test**

```python
#!/usr/bin/env python3
"""Regression tests for skin generation from the style guide."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "scripts" / "build-skins.py"


def load_build_module():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("diagram_design_build_skins", BUILD)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load build-skins.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    build_skins = load_build_module()

    css = build_skins.render_skin(build_skins.read_roles(), variant="light")

    if "--dd-paper:" not in css:
        raise AssertionError(f"colour role missing from generated skin:\n{css}")
    if "--dd-wash-5:" not in css:
        raise AssertionError("wash role missing from generated skin")
    if "--dd-radius-node:" not in css:
        raise AssertionError("geometry role missing from generated skin")
    if ":root{" not in css.replace(" ", ""):
        raise AssertionError("generated skin is not wrapped in a :root block")

    # Every role the contract declares must be emitted — a half-written skin must not build.
    for role in build_skins.CONTRACT:
        if f"--dd-{role}:" not in css:
            raise AssertionError(f"contract role {role!r} was not emitted")

    print(f"PASS: skin generation emits all {len(build_skins.CONTRACT)} contract roles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Step 2: Run it to verify it fails**

Run: `python3 scripts/test-build-skins.py`
Expected: FAIL — `AssertionError: could not load build-skins.py` (the file does not exist yet).

**Step 3: Commit the failing test**

```bash
git add scripts/test-build-skins.py
git commit -m "test(skins): add failing test for skin generation"
```

### Task 6: Implement the skin builder

**Files:**
- Create: `scripts/build-skins.py`
- Create (generated): `skills/diagram-design/assets/skins/active.tokens.css`

**Step 1: Write `scripts/build-skins.py`**

Parse the three role tables from `style-guide.md`. Table shape: column 1 is the role in backticks, the light value is the column whose header contains `light` (or the sole value column for geometry).

```python
#!/usr/bin/env python3
"""Generate skin token CSS from the canonical style guide.

Generated, never hand-edited. CI runs this script then `git diff --exit-code`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STYLE_GUIDE = REPO / "skills/diagram-design/references/style-guide.md"
OUT_DIR = REPO / "skills/diagram-design/assets/skins"

# The token contract. Every role here must be emitted or the build fails.
CONTRACT = (
    "paper", "paper-2", "node-white", "ink", "muted", "soft", "rule", "rule-solid",
    "accent", "accent-tint", "link",
    "series-1", "series-2", "series-3", "series-4", "series-5",
    "wash-2", "wash-3", "wash-5", "wash-10", "wash-20", "wash-30",
    "radius-node", "radius-tag", "radius-container",
)

ROLE_RE = re.compile(r"^\|\s*`([a-z0-9-]+)`\s*\|(.+)$")


def read_roles() -> dict[str, dict[str, str]]:
    """Return {role: {"light": value, "dark": value}} for every contract role."""
    markdown = STYLE_GUIDE.read_text(encoding="utf-8")
    roles: dict[str, dict[str, str]] = {}
    headers: list[str] = []

    for line in markdown.splitlines():
        if line.startswith("| Role |"):
            headers = [cell.strip().casefold() for cell in line.strip("|").split("|")]
            continue
        match = ROLE_RE.match(line)
        if not match:
            continue
        role = match.group(1)
        if role not in CONTRACT:
            continue
        cells = [cell.strip().strip("`") for cell in match.group(2).split("|")]
        light = dark = ""
        for index, header in enumerate(headers[1:], start=0):
            if index >= len(cells):
                break
            if "light" in header or header == "default":
                light = cells[index]
            elif "dark" in header:
                dark = cells[index]
        roles[role] = {"light": light, "dark": dark or light}
    return roles


def render_skin(roles: dict[str, dict[str, str]], variant: str = "light") -> str:
    missing = [role for role in CONTRACT if role not in roles]
    if missing:
        raise SystemExit(f"style guide is missing contract roles: {', '.join(missing)}")
    lines = [
        "/* GENERATED by scripts/build-skins.py — do not edit by hand. */",
        f"/* variant: {variant} */",
        ":root {",
    ]
    for role in CONTRACT:
        lines.append(f"  --dd-{role}: {roles[role][variant]};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> int:
    roles = read_roles()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for variant in ("light", "dark"):
        target = OUT_DIR / f"active-{variant}.tokens.css"
        target.write_text(render_skin(roles, variant), encoding="utf-8")
        print(f"  {target.relative_to(REPO)}", file=sys.stderr)
    print(f"Done. {len(CONTRACT)} roles per variant.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Step 2: Run the test**

Run: `python3 scripts/test-build-skins.py`
Expected: `PASS: skin generation emits all 25 contract roles`

If it fails with "style guide is missing contract roles", the Task 4 tables are malformed — check that role names sit in backticks in column 1.

**Step 3: Generate the skin files**

Run: `python3 scripts/build-skins.py`
Expected: prints two paths under `assets/skins/`, exits 0.

**Step 4: Commit**

```bash
git add scripts/build-skins.py skills/diagram-design/assets/skins/
git commit -m "feat(skins): generate token CSS from the style guide"
```

### Task 7: Add token validation to the linter

**Files:**
- Modify: `scripts/lint-skin.py`
- Modify: `scripts/test-lint-a11y.py`

**Step 1: Write the failing test**

Append a new check inside `main()` of `scripts/test-lint-a11y.py`, following the existing case style:

```python
    # Unknown token names must be rejected.
    bad = '<svg><rect fill="var(--dd-nonesuch)"/></svg>'
    findings = lint_skin.lint_text(bad, colors, triplets, "x")
    if not any(category == "color" for _line, _off, category, _msg in findings):
        raise AssertionError("unknown --dd-* token was not rejected")
```

**Step 2: Run it to verify it fails**

Run: `python3 scripts/test-lint-a11y.py`
Expected: FAIL — `AssertionError: unknown --dd-* token was not rejected`.

**Step 3: Implement the check in `lint-skin.py`**

Add near the other regexes:

```python
VAR_RE = re.compile(r"var\(\s*(--dd-[a-z0-9-]+)\s*\)")
```

Add inside `lint_text`, next to the existing `HEX_RE` loop:

```python
    for match in VAR_RE.finditer(text):
        token = match.group(1).removeprefix("--dd-")
        if token not in CONTRACT_ROLES:
            add(match.start(), "color", f"{match.group(1)} is not a contract role")
```

Import the contract from the builder rather than duplicating it — a second copy will drift:

```python
def contract_roles():
    """Load the token contract from build-skins.py so there is one definition."""
    spec = importlib.util.spec_from_file_location(
        "diagram_design_build_skins", ROOT / "scripts" / "build-skins.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return set(module.CONTRACT)


CONTRACT_ROLES = contract_roles()
```

**Step 4: Run the test**

Run: `python3 scripts/test-lint-a11y.py`
Expected: PASS.

**Step 5: Run the full linter over existing assets**

Run: `python3 scripts/lint-skin.py --all --baseline`
Expected: exits 0. No example uses `var()` yet, so this check is inert until PR 3.

**Step 6: Commit**

```bash
git add scripts/lint-skin.py scripts/test-lint-a11y.py
git commit -m "feat(lint): validate --dd-* token names against the contract"
```

### Task 8: Convert the five templates

**Files:**
- Modify: `skills/diagram-design/assets/template.html`
- Modify: `skills/diagram-design/assets/template-dark.html`
- Modify: `skills/diagram-design/assets/template-full.html`
- Modify: `skills/diagram-design/assets/template-motion.html`
- Modify: `skills/diagram-design/assets/template-terminal.html`

**Step 1: Replace each `:root` block with the generated skin**

Paste the contents of `assets/skins/active-light.tokens.css` (or `active-dark` for the dark template) into the `<style>` block, replacing the existing `--color-*` declarations. Keep the `--font-*` declarations.

**Do not convert `template-terminal.html`'s palette** — the terminal skin is a separate fixed skin per `style-guide.md`, and is out of scope. Only add the `.dd-node` rule there if the template uses `rx`.

**Step 2: Convert SVG literals to `var()`**

In each template's `<svg>` body and `<defs>`, replace:
- `fill="#f5f5f5"` → `fill="var(--dd-paper)"`
- `fill="#2d3142"` → `fill="var(--dd-ink)"`
- `fill="#4f5d75"` / `stroke="#4f5d75"` → `var(--dd-muted)`
- `fill="#eb6c36"` → `var(--dd-accent)`
- `fill="#2e5aa8"` → `var(--dd-link)`

Include the three `<marker>` polygons — they are the most commonly missed.

**Step 3: Add the radius rule to each `<style>` block**

```css
    .dd-node { rx: var(--dd-radius-node); }
    .dd-tag  { rx: var(--dd-radius-tag); }
```

Node rects keep their literal `rx="6"` attribute as a Safari fallback and gain `class="dd-node"`.

**Step 4: Lint each template**

Run: `python3 scripts/lint-skin.py --all --baseline`
Expected: exits 0.

**Step 5: Open `template.html` in a browser and confirm it renders identically**

The templates are near-empty scaffolds, so this is a fast visual check that the `:root` block is wired.

**Step 6: Commit**

```bash
git add skills/diagram-design/assets/template*.html
git commit -m "refactor(templates): bind colours through --dd-* tokens"
```

### Task 9: Wire the build gate and close PR 2

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `CONTRIBUTING.md`

**Step 1: Add the generated-file gate to CI**

Mirror the existing icon gate:

```yaml
      - name: Skins are up to date
        run: |
          python3 scripts/build-skins.py
          git diff --exit-code -- skills/diagram-design/assets/skins/
```

**Step 2: Add both commands to the CONTRIBUTING gate table**

Add rows for `python3 scripts/test-build-skins.py` and the `build-skins.py` + `git diff` pair, and add them to the "run them all at once" chain.

**Step 3: Run the full suite**

Expected: all gates exit 0, including the two new ones.

**Step 4: Bump, commit, open the PR**

```bash
python3 scripts/bump-plugin-version.py --minor
git add .github/workflows/ci.yml CONTRIBUTING.md .claude-plugin/plugin.json .codex-plugin/plugin.json
git commit -m "ci(skins): gate generated skin files"
git push -u origin feat/token-contract
gh pr create --title "feat: token contract and skin generation" --body "Adds --dd-* token contract, build-skins.py, linter validation, and converts the 5 templates. No visual change. Gates: full suite green plus 2 new."
```

---

## PR 3 — Migrate the examples

Branch: `refactor/examples-to-tokens`. **Visually identical by construction.**

### Task 10: Capture the before state

**Step 1: Rasterize every example at the current skin**

```bash
mkdir -p /tmp/skin-before
python3 - <<'PY'
import pathlib
from playwright.sync_api import sync_playwright
assets = pathlib.Path("skills/diagram-design/assets")
out = pathlib.Path("/tmp/skin-before")
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(device_scale_factor=1)
    for src in sorted(assets.glob("example-*.html")):
        page.goto(f"file://{src.resolve()}")
        page.wait_for_load_state("networkidle")
        page.locator("svg").first.screenshot(path=str(out / f"{src.stem}.png"))
    browser.close()
PY
```

Expected: 104 PNGs written. If Playwright is missing, install it per `references/export.md` — do not skip this step, it is the only thing that makes PR 3 reviewable.

### Task 11: Write the codemod

**Files:**
- Create: `scripts/migrate-to-tokens.py`

**Step 1: Implement it**

Build the literal→role map by inverting `read_roles()` from `build-skins.py`, then rewrite only inside the `<svg>` subtree. Report ambiguities instead of guessing.

Requirements:
- Only rewrite within `<svg>…</svg>`; leave page chrome CSS alone.
- Match hex case-insensitively; match `rgba()` on the RGB triplet plus opacity.
- If one literal maps to two roles, print the file, line, and both candidates, and **leave it unchanged**.
- Insert the generated `:root` block into the file's `<style>` if absent.
- Add `class="dd-node"` to rects carrying `rx="6"`.

**Step 2: Dry-run on one file**

Run: `python3 scripts/migrate-to-tokens.py --dry-run skills/diagram-design/assets/example-architecture.html`
Expected: reports ~84 substitutions and 0 ambiguities.

**Step 3: Commit**

```bash
git add scripts/migrate-to-tokens.py
git commit -m "chore(migrate): add hex-to-token codemod"
```

### Task 12: Run the migration

**Step 1: Migrate every example**

Run: `python3 scripts/migrate-to-tokens.py skills/diagram-design/assets/example-*.html`
Expected: a per-file substitution count and a final ambiguity list.

**Step 2: Resolve ambiguities by hand**

For each reported line, choose the role from context (fill on a node box vs. a label mask) and edit directly. Do not widen the codemod to guess.

**Step 3: Lint everything**

Run: `python3 scripts/lint-skin.py --all --baseline`
Expected: exits 0.

**Step 4: Empty the baseline**

The 20 baselined files now use tokens, so they conform. Truncate `scripts/lint-skin-baseline.txt` to empty and re-run without it:

Run: `python3 scripts/lint-skin.py --all`
Expected: exits 0 **with no baseline**. This is the success criterion for M1. If any file still fails, fix that file — do **not** re-add it to the baseline; `CONTRIBUTING.md` forbids it.

**Step 5: Commit**

```bash
git add skills/diagram-design/assets/ scripts/lint-skin-baseline.txt
git commit -m "refactor(examples): bind colours through --dd-* tokens"
```

### Task 13: Prove the refactor changed nothing

**Step 1: Rasterize the after state**

Repeat Task 10's script with `out = /tmp/skin-after`.

**Step 2: Compare**

```bash
python3 - <<'PY'
import pathlib, hashlib
before, after = pathlib.Path("/tmp/skin-before"), pathlib.Path("/tmp/skin-after")
diff = [b.name for b in sorted(before.glob("*.png"))
        if hashlib.sha256(b.read_bytes()).hexdigest()
        != hashlib.sha256((after / b.name).read_bytes()).hexdigest()]
print(f"{len(diff)} of {len(list(before.glob('*.png')))} differ")
for name in diff: print(" ", name)
PY
```

Expected: **0 differ.** Any file that differs has a mis-mapped token — fix it before proceeding. Anti-aliasing should not vary between runs at the same scale factor; if you see noise across the board, compare with a small per-pixel tolerance instead of a hash.

**Step 3: Bump, commit, open the PR**

```bash
python3 scripts/bump-plugin-version.py
git add .claude-plugin/plugin.json .codex-plugin/plugin.json
git commit -m "chore(release): bump plugin version"
git push -u origin refactor/examples-to-tokens
gh pr create --title "refactor: migrate examples to --dd-* tokens" --body "Mechanical hex-to-token conversion of 104 examples. Rasterized before/after are byte-identical. lint-skin-baseline.txt is now empty — the 20 legacy files conform for the first time."
```

---

## PR 4 — The Inflection skin

Branch: `feat/inflection-skin`. **All visual change lands here.**

### Task 14: Archive the current skin

**Files:**
- Create: `skills/diagram-design/references/skins/editorial-default.md`

**Step 1: Copy the current token tables** out of `style-guide.md` into the new file, with a header explaining it is the upstream editorial skin and how to restore it (paste the tables back into `style-guide.md`, run `build-skins.py`, re-lint).

**Step 2: Commit**

```bash
git add skills/diagram-design/references/skins/editorial-default.md
git commit -m "docs(skins): archive the upstream editorial skin"
```

### Task 15: Apply the Inflection values

**Files:**
- Modify: `skills/diagram-design/references/style-guide.md`

**Step 1: Replace the token tables** with the values from design doc §5.1, §5.2, §5.3. Do not re-derive them.

Critical: `muted` is **slate-mid `#4A6275`**, not the brand's `text.secondary` ash `#8A8880`. Ash is 3.18:1 on ivory and fails the 4.5:1 floor this role requires at 8–9px.

**Step 2: Replace the Typography table** per §5.5 — Cormorant Garamond, DM Sans, Geist Mono (fallback).

**Step 3: Update the geometry roles** to `radius-node: 2`, `radius-tag: 2`, `radius-container: 4`.

**Step 4: Add the brand fidelity receipt** as a new section, recording: sampled source (`inflectionagents.com/tokens.json`), the ash→slate-mid substitution and why, gold's 3.66:1 (valid for strokes, invalid for small text), the mono role as `fallback`, and the three dropped chart series.

**Step 5: Regenerate the skins**

Run: `python3 scripts/build-skins.py`
Expected: both files rewritten with brand values.

**Step 6: Commit**

```bash
git add skills/diagram-design/references/style-guide.md skills/diagram-design/assets/skins/
git commit -m "feat(skin): apply the Inflection Agents brand tokens"
```

### Task 16: Update fonts and re-skin every file

**Step 1: Replace the Google Fonts link** in all templates and examples:

```html
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

**Step 2: Replace every `:root` block** with the regenerated skin. This is the operation the whole milestone exists to enable — a scripted find-and-replace of one block per file.

**Step 3: Update `--font-*` declarations** to Cormorant Garamond / DM Sans / Geist Mono.

**Step 4: Lint**

Run: `python3 scripts/lint-skin.py --all`
Expected: exits 0. The linter reads allowed families from the style guide's Typography table, so both new families are accepted once Task 15 landed; both are served from `fonts.googleapis.com/css2` and pass the single-file allowlist.

**Step 5: Look at the rendered output**

Open `assets/index.html` and review the gallery. Judge specifically: does gold still read as focal against ivory, and does `radius-node: 2` suit the diagrams or look mean? The radius values are a taste call flagged in the design doc — this is where you settle them.

**Step 6: Commit**

```bash
git add skills/diagram-design/assets/
git commit -m "feat(skin): re-skin templates and examples to Inflection"
```

### Task 17: Write the ADRs and close PR 4

**Files:**
- Create: `docs/adr/0007-colour-binds-through-tokens.md`
- Create: `docs/adr/0008-brand-dark-palettes-override-inversion.md`
- Create: `docs/adr/0009-grid-versus-brand-precedence.md`

**Step 1: Write each ADR** in the existing four-section shape (title, Status, Context, Decision, Consequences). Content is in design doc §8. Keep them short — the existing ADRs are 15–20 lines.

**Step 2: Check the SKILL.md byte cap**

Run: `python3 -c "import os; n=os.path.getsize('skills/diagram-design/SKILL.md'); print(n, 40000-n)"`
Expected: under 40,000. Headroom was 2,594 bytes at the start of M1.

**Step 3: Run the full suite**

Expected: all gates green.

**Step 4: Bump, commit, open the PR**

```bash
python3 scripts/bump-plugin-version.py --minor
git add docs/adr/ .claude-plugin/plugin.json .codex-plugin/plugin.json
git commit -m "docs(adr): record token binding, dark-palette, and grid precedence decisions"
git push -u origin feat/inflection-skin
gh pr create --title "feat: Inflection Agents brand skin" --body "Applies the brand tokens with the documented ash-to-slate-mid substitution, swaps typography, adds ADRs 0007-0009. All visual change in this PR."
```

---

## PR 5 — Export carries the skin

Branch: `fix/export-skin-block`.

### Task 18: Inject the skin into exported SVG

**Files:**
- Modify: `skills/diagram-design/references/export.md`

**Step 1: Extend SVG export step 3**

The procedure already injects a `<style>` into `<defs>` for the font `@import`. Document that the source file's `:root` block is injected into that same `<style>`, rewritten from `:root` to `svg` so it applies in a standalone document:

```svg
<defs>
  <style>
    @import url('https://fonts.googleapis.com/css2?…');
    svg { --dd-paper:#F5F2EC; --dd-ink:#1B2B3C; /* … */ }
  </style>
</defs>
```

**Step 2: Extend the caveat section**

Add: consumers that do not resolve CSS custom properties — older Illustrator, some Figma import paths, non-browser rasterizers — will not pick up the palette. PNG remains the recommendation for pixel-perfect portability. PNG export is unaffected because it rasterizes the original HTML in Chromium.

**Step 3: Verify by exporting one diagram**

Follow the updated procedure by hand on `example-architecture.html`, then open the resulting `.svg` directly in a browser.
Expected: renders with the Inflection palette, not unstyled.

**Step 4: Run docs sync**

Run: `python3 scripts/verify-docs-sync.py`
Expected: exits 0.

**Step 5: Bump, commit, open the PR**

```bash
python3 scripts/bump-plugin-version.py
git add skills/diagram-design/references/export.md .claude-plugin/plugin.json .codex-plugin/plugin.json
git commit -m "fix(export): carry the skin block into standalone SVG"
git push -u origin fix/export-skin-block
gh pr create --title "fix: export carries the skin block" --body "Standalone SVG export injects the token block into the existing defs style. Extends the renderer caveat. PNG export unaffected."
```

---

## Definition of done for M1

- [ ] `python3 scripts/lint-skin.py --all` passes **without** `--baseline`
- [ ] `scripts/lint-skin-baseline.txt` is empty
- [ ] Task 13's raster comparison reported 0 differing files
- [ ] The full 16-gate suite is green, plus the 2 new skin gates
- [ ] `SKILL.md` is under 40,000 bytes
- [ ] The brand fidelity receipt records the ash substitution, gold's text limitation, the mono fallback, and the 3 dropped series
- [ ] `LICENSE` is byte-identical to upstream
- [ ] Reskinning a diagram is a single `:root` block swap — verified by restoring `editorial-default.md` and rebuilding

## Out of scope — do not do these

- New visual types or semantic patterns (M2)
- Changing node-kind visual encoding (M3) — the migration deliberately preserves the low-contrast fills recorded in design doc §9
- Per-project runtime skin resolution
- Touching the terminal skin, which is a separate fixed palette by design
