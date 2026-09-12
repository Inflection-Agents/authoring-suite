# muse-white-paper Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the `muse-white-paper` plugin that renders a 6-page paper and a cut-down 2-page brief from one approved spine, in the owner's voice, within word and figure-area budgets.

**Architecture:** New plugin at `plugins/muse-white-paper` orchestrates the existing `narrative-spine` and `writing-voice` skills. It adds `voice-sheet.md` plus edit-pair vetoes, `budgets.json` plus a budget script, and `cut.py` for the 2-pager derivation. `diagram-design` stays untouched.

**Tech Stack:** Python 3 stdlib only for scripts, Markdown skill files, existing `verify-voice.py` and `spine-check.mjs`, repo frontmatter gate `scripts/verify-skill-frontmatter.py`.

---

### Task 1: Scaffold the plugin skeleton

**Files:**
- Create: `plugins/muse-white-paper/skills/muse-white-paper/SKILL.md`
- Create: `plugins/muse-white-paper/skills/muse-white-paper/references/budgets.md`
- Create: `plugins/muse-white-paper/skills/muse-white-paper/references/elicitation.md`
- Create: `plugins/muse-white-paper/skills/muse-white-paper/references/revision-loop.md`
- Create: `plugins/muse-white-paper/skills/muse-white-paper/assets/spine.template.md`
- Modify: `.claude-plugin/marketplace.json`

**Step 1: Create the skeleton files**

SKILL.md frontmatter must parse under the repo gate: `name`, one-line quoted `description`, `license`. Keep the body short, pointer to references.

```markdown
---
name: muse-white-paper
description: "Render a 6-page white paper and a cut-down 2-page brief from one approved spine, in the owner's voice, within word and figure-area budgets."
license: MIT
---

# Muse White Paper

One spine, two renders. See `references/budgets.md` for the area math,
`references/elicitation.md` for voice capture, `references/revision-loop.md`
for the capped revision loop. Copy `assets/spine.template.md` to start.
```

Marketplace entry to append inside `"plugins"`:

```json
{
  "name": "muse-white-paper",
  "source": "./plugins/muse-white-paper"
}
```

**Step 2: Run the frontmatter gate**

Run: `python3 scripts/verify-skill-frontmatter.py`
Expected: PASS, no findings for the new SKILL.md.

**Step 3: Commit**

```bash
git add plugins/muse-white-paper .claude-plugin/marketplace.json
git commit -m "feat(muse-white-paper): scaffold plugin skeleton"
```

### Task 2: Voice sheet schema and sample

**Files:**
- Create: `plugins/muse-white-paper/skills/muse-white-paper/references/voice-sheet-schema.md`
- Create: `plugins/muse-white-paper/skills/muse-white-paper/assets/voice-sheet.sample.md`

**Step 1: Write the schema doc**

One entry per habit with fields: habit name, liked line, rejected line showing the edge, scope note (cross-register or single-topic, single-topic excluded).

**Step 2: Write the sample with two entries**

Use neutral placeholder lines, each rejected line differing by exactly one habit so the edge is visible.

**Step 3: Commit**

```bash
git add plugins/muse-white-paper/skills/muse-white-paper/references/voice-sheet-schema.md plugins/muse-white-paper/skills/muse-white-paper/assets/voice-sheet.sample.md
git commit -m "feat(muse-white-paper): voice sheet schema and sample"
```

### Task 3: Edit-pair veto convention

**Files:**
- Create: `plugins/muse-white-paper/skills/muse-white-paper/references/edit-pairs.md`
- Create: `plugins/muse-white-paper/skills/muse-white-paper/assets/pairs-sample/README.md`

**Step 1: Write the convention**

Rule in one line: on any conflict between `voice-sheet.md` and a stored rewrite, the rewrite wins without a sheet edit. Pairs stored as `pairs/YYYY-MM-DD-<slug>-draft.md` and `-rewrite.md` with a one-line note naming the overridden habit.

**Step 2: Write the sample pair**

One three-line draft plus its rewrite plus the override note.

**Step 3: Commit**

```bash
git add plugins/muse-white-paper/skills/muse-white-paper/references/edit-pairs.md plugins/muse-white-paper/skills/muse-white-paper/assets/pairs-sample/
git commit -m "feat(muse-white-paper): edit-pair veto convention"
```

### Task 4: Budget script (words plus figure area)

**Files:**
- Create: `plugins/muse-white-paper/skills/muse-white-paper/scripts/budget-check.py`
- Create: `plugins/muse-white-paper/skills/muse-white-paper/scripts/test-budget-check.py`
- Create: `plugins/muse-white-paper/skills/muse-white-paper/assets/budgets.sample.json`

**Step 1: Write the failing test**

```python
def test_half_page_figure_displaces_230_words():
    assert displacement("half") == 230
```

Sample budgets file:

```json
{
  "six_pager": {"prose_cap": 2400, "figure_cap_pages": 1.5, "max_figures": 4},
  "two_pager": {"prose_cap": 800, "figure_cap_pages": 0.5, "max_figures": 2},
  "displacement_per_half_page_words": 230
}
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/muse-white-paper/skills/muse-white-paper/scripts/test-budget-check.py`
Expected: FAIL with `displacement not defined`.

**Step 3: Write minimal implementation**

`budget-check.py` reads a manuscript manifest (section word counts plus figure sizes in page fractions) and reports over-words, over-area, or OK for the named render. Pure stdlib, no NLP word counter: callers pass counts in.

**Step 4: Run test to verify it passes**

Run: `python3 plugins/muse-white-paper/skills/muse-white-paper/scripts/test-budget-check.py`
Expected: exit 0, all cases print OK, both polarities covered (over-words flagged, exact-cap passes).

**Step 5: Commit**

```bash
git add plugins/muse-white-paper/skills/muse-white-paper/scripts/ plugins/muse-white-paper/skills/muse-white-paper/assets/budgets.sample.json
git commit -m "feat(muse-white-paper): budget script for words plus figure area"
```

### Task 5: cut.py derives the 2-pager

**Files:**
- Create: `plugins/muse-white-paper/skills/muse-white-paper/scripts/cut.py`
- Create: `plugins/muse-white-paper/skills/muse-white-paper/scripts/test-cut.py`

**Step 1: Write the failing test**

```python
def test_cut_keeps_every_title():
    assert kept_titles(long_spine) == all_titles(long_spine)
```

**Step 2: Run test to verify it fails**

Run: `python3 plugins/muse-white-paper/skills/muse-white-paper/scripts/test-cut.py`
Expected: FAIL with `kept_titles not defined`.

**Step 3: Write minimal implementation**

`cut.py` takes the 6-pager manifest plus `budgets.json`, drops bodies lowest-priority first (priority field per section, ties broken by longest body), keeps every title and at most 2 carried-over figures within 0.5 pages, and exits nonzero naming the overrun when even titles plus minimum bodies exceed caps.

**Step 4: Run test to verify it passes**

Run: `python3 plugins/muse-white-paper/skills/muse-white-paper/scripts/test-cut.py`
Expected: exit 0; titles intact, figure cap held, overrun case exits nonzero.

**Step 5: Commit**

```bash
git add plugins/muse-white-paper/skills/muse-white-paper/scripts/cut.py plugins/muse-white-paper/skills/muse-white-paper/scripts/test-cut.py
git commit -m "feat(muse-white-paper): cut script derives 2-pager from 6-pager"
```

### Task 6: Two-pass titling and revision loop

**Files:**
- Create: `plugins/muse-white-paper/skills/muse-white-paper/references/revision-loop.md`

**Step 1: Write the loop doc**

Pass one titles before prose. Pass two retitles touched sections after bodies, keeping whichever carries the section alone subject to connective and title-only-read rules. Per round order: reorder on broken connectives, merge on shared fact packs, drop sections alive only by their link packs. Cap three rounds; leftovers go to `DECISIONS.md` as open breaks.

**Step 2: Commit**

```bash
git add plugins/muse-white-paper/skills/muse-white-paper/references/revision-loop.md
git commit -m "feat(muse-white-paper): two-pass titling and revision loop"
```

### Task 7: DECISIONS.md seed and end-to-end fixture

**Files:**
- Create: `plugins/muse-white-paper/DECISIONS.md`
- Create: `plugins/muse-white-paper/skills/muse-white-paper/scripts/test-end-to-end.py`

**Step 1: Seed the decision log**

First entries: voice source (explicit sheet plus edit-pair veto), one spine two renders, hybrid storyboard, plugin-proposes briefs, area budget numbers, three-round loop cap. Format follows `sdlc/templates/decisions.md` shape (question, decided, rejected, reversal path).

**Step 2: Write the end-to-end fixture test**

A six-section sample spine with word counts and 3 figures runs through `budget-check.py` (6-pager OK) then `cut.py` (2-pager within 800 words and 0.5 pages, all titles kept).

**Step 3: Run the full gate suite**

Run: `python3 scripts/verify-skill-frontmatter.py`
Expected: PASS.
Run: `python3 plugins/muse-white-paper/skills/muse-white-paper/scripts/test-end-to-end.py`
Expected: exit 0.

**Step 4: Commit**

```bash
git add plugins/muse-white-paper/DECISIONS.md plugins/muse-white-paper/skills/muse-white-paper/scripts/test-end-to-end.py
git commit -m "feat(muse-white-paper): seed decisions log and end-to-end fixture"
```

