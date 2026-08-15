# Execution plan

**Date:** 2026-08-14
**Status:** proposed
**Supersedes:** the per-milestone roadmap tables scattered across the design docs

Consolidates M1 through M3 into a dependency-ordered build, and records the measurements that
decide the ordering.

---

## 1. The measurement that shapes everything

Before sequencing, I measured how the 97 shipped examples would fare against the enforcement gates
proposed in the pass-1 review. The results rule out one plan and force another.

| Proposed gate | Files failing | Violations | Can it land retroactively? |
|---|---|---|---|
| No diagonal `<line>` | 15 of 97 | 45 | **Yes** — small enough to fix |
| Structural 4px grid | **97 of 97** | **5,405** | **No** — would require redrawing every diagram |
| Accent ≤ 2 elements | 54 of 97 (approx) | — | **No, and the measure is wrong** |
| Tag on every node | most | — | No — that is what the M3 sweep is for |

Three conclusions:

**The grid gate cannot be retroactive.** 5,405 coordinate changes across every shipped file is a
redraw, not a lint fix, and it would change layouts visually with no way to verify the change was
intended. The grid ships as a **grandfathered** check: the 97 current files are seeded into a
new-check baseline at introduction, and every new or changed file must comply.

This is a different use of a baseline from the one `CONTRIBUTING.md` forbids. That rule bans adding
a file to the baseline *to get your example through*. Seeding a grandfather list when introducing a
rule to a legacy codebase is standard and honest — the distinction is that the list only ever
shrinks.

**The accent measure needs fixing before it can gate.** My count was occurrences of the accent hex,
which triple-counts a single accent node (fill, stroke, marker) and flags chart types that
legitimately colour a series. Build the check to count accent *elements*, then re-measure. Do not
gate on a metric that is wrong.

**The diagonal gate can land clean**, and should — 45 diagonals across 15 files are real defects
against a rule `SKILL.md` calls an automatic fail.

---

## 2. Three sweeps, three different verification strategies

The single most important sequencing fact: three separate pieces of work touch the whole asset base,
and each needs a *different* way of being reviewed. Running any two together destroys the ability to
review either.

| Sweep | Scope | Visual change | How it is verified |
|---|---|---|---|
| **M1 PR 3** — hex to token | 97 examples, 5 templates | **None, by construction** | Rasterize before and after; assert byte-identical PNGs |
| **Diagonal remediation** | 15 examples | Yes, localised | Review the 15 rendered diffs by eye |
| **M3** — tags and notches | 97 examples | Yes, everywhere | Review the gallery; greyscale gate proves the point |

M1 PR 3's raster-identity property is the only thing that makes 97 changed files reviewable without
reading 97 diffs. It must not share a PR — or a milestone — with anything that changes a pixel.

---

## 3. Dependency graph

```
  PR #1 (merged)
        │
        ├── ADR: SKILL.md byte cap ──────────┐
        ├── Spike: notch primitive ──────┐   │
        └── Decision: detach fork        │   │
              │                          │   │
              ▼                          │   │
  ┌───────────────────────┐              │   │
  │ PHASE 1 · M1          │              │   │
  │ portability (5 PRs)   │              │   │
  └───────────┬───────────┘              │   │
              │                          │   │
      ┌───────┴────────┬─────────────────┼───┼──────────┐
      ▼                ▼                 ▼   │          ▼
  ┌────────┐    ┌─────────────┐   ┌──────────┴──┐  ┌─────────┐
  │PHASE 2a│    │  PHASE 2b   │   │  PHASE 2c   │  │ M2.5    │
  │diagonal│───▶│ M3 tags     │──▶│ enforcement │  │ set     │
  │fix     │    │ + notches   │   │ gates       │  │ spine   │
  └────────┘    └──────┬──────┘   └──────┬──────┘  └─────────┘
                       │                 │          (parallel,
                       └────────┬────────┘         touches no
                                ▼                   examples)
                     ┌─────────────────────┐
                     │ PHASE 3 · M2        │
                     │ 6 types + code level│
                     └──────────┬──────────┘
                                ▼
                     ┌─────────────────────┐
                     │ PHASE 4             │
                     │ M2.2 routing        │
                     │ M2.4 variants+gallery│
                     └──────────┬──────────┘
                                ▼
                          Pages enablement
```

**Critical path:** M1 → M3 → M2 → M2.2 → M2.4. Everything else hangs off it.

---

## 4. Phases

### Phase 0 — Foundations

Three small items that block later work if left undecided. None depends on the others.

| Item | Why now |
|---|---|
| **ADR: the `SKILL.md` byte cap** | 2,594 bytes of headroom. The §3 routing rewrite plus six type rows will exceed it. Decide whether to raise it — available to a fork — before it blocks a PR mid-phase. It must be a recorded ADR, not a silent edit; the cap exists to keep the installed skill cheap to load. |
| **Spike: the notch primitive** | M3 is blocked on it. A clipped corner needs a `path` rather than a `rect`, and it interacts with `--dd-radius-node`. Small, but discovering the interaction mid-sweep is expensive. |
| **Decision: detach from the fork network** | Cheap now, awkward later. Also gates Pages. |

**Status: two of three resolved.**

- **Byte cap — resolved, and the answer was not to raise it.** ADR-0006. Moving the two §3
  selection tables into `references/routing.md` frees 4,102 bytes, against 2,400–3,000 of planned
  additions. Headroom goes from 2,594 to roughly 6,696, then settles near 4,000 — wider than today.
  The cap stays a real constraint. **This adds an ordering constraint: see §4.1 below.**
- **Notch primitive — resolved.** `2026-08-14-notch-primitive-spike.md`. The path generator works,
  it is grid-safe, it does not conflict with `--dd-radius-node`, and the specimen passes
  `lint-skin.py` and `self_check.py` today. Convention A adopted. The spike also **grew M3's scope**
  — see §4.2.
- **Fork detachment — still open.** Blocks Pages only.

### 4.1 Ordering constraint from ADR-0006

The table relocation is the *funding* for Phase 3, so it must land **before** the type additions
that spend it. But the execution plan sequences M2.2 routing after Phase 3, so §3 is touched once.

Both can hold if M2.2 is split:

| Half | When | Why |
|---|---|---|
| **Relocation** — move the §3 tables into `references/routing.md` verbatim | **Start of Phase 3** | Frees the bytes before they are spent; a pure move, no rewrite |
| **Procedure** — the routing methodology, refusal rules, worked trace | Phase 4, as planned | Needs the final type list to be written against |

New type rows then land in `routing.md` as each type ships, and `SKILL.md` §3 is touched exactly
twice: once to become a pointer, once never again.

### 4.2 M3 grew

The greyscale render found a gap pass 3 did not account for, and the measurement found the sweep is
larger than described:

- **Focal does not survive greyscale.** Accent fill and stroke both collapse to the same grey, and
  stroke-width 1.2 against 1.0 is imperceptible. Focal is orthogonal to kind, so it cannot use the
  notch. Fix: focal carries **stroke weight ≥1.6**, matching the kit's existing `focalLight`.
- **Mandatory tags are not a mechanical sweep.** 55 of 97 files carry no tags at all, and 124 node
  boxes are shorter than 56px across 21 files — too short for a tag chip and a centred name to
  coexist. Pass 3 called this "a mechanical sweep, not a redesign"; for those 21 files it is a
  reflow.

  **Decided: short boxes carry the tag and the name on one line, left-aligned.** Boxes at 56px and
  above keep the centred two-line treatment. This is the spike's recommendation, and it is the only
  option that neither redraws 21 files nor puts a permanent hole in the rule M3 exists to enforce —
  the tag-presence gate in 2c can land clean. The cost, accepted knowingly, is that two name
  alignments coexist in the system; `type-*.md` must say which applies when.

### Phase 1 — M1, portability

Already planned in full: `2026-08-14-m1-portable-skin.md`, 18 tasks across 5 PRs.

**Why first:** everything downstream edits example files. Doing any of it before tokenization means
migrating the same files twice.

**Exit criteria** (from the M1 plan's definition of done):
- `lint-skin.py --all` passes **without** `--baseline`
- `lint-skin-baseline.txt` is empty
- The raster comparison reports **0** differing files
- Reskinning is a single `:root` block swap, proven by restoring the archived editorial skin

### Phase 2 — Remediation and enforcement

Three sub-phases, strictly ordered, because 2c gates what 2a and 2b fix.

**2a · Diagonal remediation.** Convert 45 diagonal `<line>` elements across 15 files to orthogonal
elbows. Visual change, localised; review the 15 rendered diffs. The `example-high-level*` family is
6 of the 15 and accounts for 24 of the 45 — do that family first as one PR, the remaining 9 files as
another.

**2b · M3, the tag and notch sweep.** Mandatory type tags plus corner notches across 97 examples.
Blocked on the Phase 0 notch spike. Visual change everywhere; review by gallery, and land the
greyscale render gate in the same phase since this is the work it exists to prove.

**2c · Enforcement gates.** Land the checks *after* the things they would flag are fixed:
- Diagonal check — clean, no grandfathering
- Tag-presence check — clean after 2b
- Compartment transcription check (colon or bracket) — clean, nothing violates it yet
- Structural grid check — **grandfathered**, seeded with whatever still fails after 2a and 2b
- Accent check — rebuild the metric to count elements, re-measure, then decide

**Exit:** the grammar rules `SKILL.md` calls non-negotiable are mechanically enforced for the first
time.

### 4.3 How Phase 2 is reviewed

Phase 1 could be verified mechanically — byte-identical rasters, a linter, an empty baseline. Phase 2
cannot: 2a and 2b are judged by looking. The agreed method is a **published before/after gallery per
PR**, reviewed asynchronously, rather than halting on each one.

That puts real weight on the render harness, so it is a deliverable and not a convenience:

- `scripts/build-screenshots.py` already renders any example deterministically.
- Each visual PR publishes a before/after page covering every file it touched.
- The greyscale gate lands with 2b, but it proves node *kind* survives greyscale — it says nothing
  about whether the tag sweep reads well. It is not a substitute for the gallery review.

### Phase 3 — M2, the archetypes

Six new types plus the code level. Order within the phase is chosen to de-risk, not by value:

1. **Code level** — first, because it is a rename-and-generalize of `type-er.md` rather than a new
   file. Lowest risk, and it proves the type-shipping pipeline against an existing type before the
   pipeline is used on new ones.
2. **Zoom** — highest value. `SKILL.md` instructs authors to split into overview and detail in three
   places and provides no grammar; this closes that. Also unblocks Deployment and the code level,
   both of which resolve scale by pairing with Zoom.
3. **Contrast**, then **Lineage**, then **Composition**, then **Deployment**.
4. **Matrix** — last, because it lands with `type-dp-security-matrix` retired to a preset in the same
   PR. One concern, one PR, but it is the only one that removes something.
5. **Hub & spoke** — a semantic pattern, not a type. One section in `semantic-patterns.md` plus a
   routing row.

Each type ships the full set: reference with a `## Which variant` section, three example variants,
gallery registration, and the documented failure the pass reviews identified. One ADR supersedes
ADR-0002 for the whole phase rather than one per type.

**Exit:** 32 types, gallery reachable, gates green.

### Phase 4 — Routing and selection

**M2.2 · Routing.** `references/routing.md` plus the `SKILL.md` §3 rewrite. Deliberately after
Phase 3 so §3 is touched **once**: rewriting it during Phase 3 would mean editing it seven more
times as types land.

**M2.4 · Selection guidance and the gallery.** Per-variant rules with named defaults, then the
gallery re-indexed by relation with a "reach for this when" line per card. Depends on both Phase 3
(the variants exist) and M2.2 (the relation vocabulary exists).

### Phase 5 — Set spine and publish

**M2.5 · Set spine** can start any time after Phase 1 — it adds `<meta>` tags and a gate, and
touches no example geometry. Run it in parallel with Phases 2–4 if there is capacity; it is the
only genuinely parallelizable milestone.

**Pages.** Enable Actions workflows and Pages on the fork. Sequenced last so the Attribution section
and the restructured gallery are both live before the site is.

---

## 5. What can run in parallel

Very little, and that is worth stating plainly rather than discovering.

| Work | Parallel with | Why |
|---|---|---|
| **M2.5 set spine** | Phases 2–4 | Metadata and a gate; touches no example geometry |
| **Routing prose drafting** | Phase 3 | The document can be written while types land; only the `SKILL.md` §3 edit must wait |
| Everything else | — | Serialised by the shared asset base |

The asset base is the bottleneck. Almost every milestone edits the same 97 files, and the only
reason the plan is not one long queue is that M2.5 stays clear of them.

---

## 6. Open decisions blocking the plan

**All resolved as of the close of Phase 1.**

| Decision | Blocked | Resolution |
|---|---|---|
| ~~Raise the `SKILL.md` byte cap?~~ | — | **No.** ADR-0006: relocating the §3 tables funds the additions with room to spare. |
| ~~Detach from the fork network?~~ | Pages | **Already done.** The repository reports `isFork: false` with no parent, so nothing gates Pages but enablement itself. |
| ~~Confirm the brand token source~~ | M1 PR 4 | **Used as published.** The "Butterfly Investments · Inflection Agents" heading is recorded as a provenance caveat in the brand fidelity receipt rather than blocking the skin. M1 decision log D2. |
| ~~Inflection radius values~~ | M1 PR 4 | **Kept at `node: 2`, `tag: 2`, `container: 4`,** settled against the rendered gallery. 2px reads as precision rather than meanness on 160×64 boxes. M1 decision log D15. |
| ~~Short boxes under M3's mandatory tags~~ | Phase 2b | **Left-aligned name in short boxes.** See §4.2. |
| ~~How Phase 2 gets reviewed~~ | Phase 2 | **A published before/after gallery per PR,** reviewed asynchronously rather than blocking each PR. See §4.3. |

---

## 7. Rough shape of the work

Not estimates — relative weight, to inform sequencing.

| Phase | PRs | Files touched | Risk |
|---|---|---|---|
| 0 · Foundations | 2 | few | low |
| 1 · M1 portability | 5 | 104 | **medium** — largest mechanical change; mitigated by raster-identity |
| 2 · Remediation and enforcement | 5–6 | 97 | **high** — two visual sweeps reviewed by eye, plus a reflow of 21 files (see §4.2) |
| 3 · M2 archetypes | 7 | ~25 new | medium — new content, but born into an enforced grammar |
| 4 · Routing and selection | 2–3 | few + gallery | low-medium — byte cap is the risk |
| 5 · Set spine and Pages | 2 | few | low |

**Phase 2 is the one to watch.** It is the only phase where correctness is judged by looking rather
than by a gate, and it is sandwiched between two phases that are mechanically verifiable. Budget
review time there, not in Phase 1.
