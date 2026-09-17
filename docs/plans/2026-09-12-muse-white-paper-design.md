# muse-white-paper design

Date: 2026-09-12
Status: approved sections 1-6

## Problem

AI drafts do not sound like the owner, and they run long. A paper that
should fill 2 pages arrives at 10. A good white paper states its claim,
links out for proof, mixes prose with figures, and stops before boredom.

## Decision log

- Voice source: explicit `voice-sheet.md` owned by the writer (choice C),
  corrected by draft vs rewrite edit pairs (choice B). Edit pairs overrule
  the sheet on conflict.
- Lengths: one spine, two renders (choice A). The 2-pager is cut from the
  6-pager, never a separate write.
- Storyboard: hybrid. Rough dump when one exists, interview when starting
  blank. Both land in the same `spine.md`.
- Diagrams and links: plugin proposes one diagram brief per section plus a
  link pack; owner approves before prose (choice A).
- Plugin name: `muse-white-paper`.
- Running log: `DECISIONS.md` sidecar, append-only, read at the start of
  every run. Format follows `sdlc/templates/decisions.md`: per-task entries
  plus `EXECUTIVE DECISION` and `SPEC DEVIATION` blocks as they happen.

## Section 1: Architecture (approved)

New plugin `muse-white-paper` orchestrates the two owned skills.
`writing-voice` gains `voice-sheet.md` plus an edit-pair veto file.
`narrative-spine` gains a per-section budget and a cut script that derives
the 2-pager. `diagram-design` stays untouched; the new plugin only writes
diagram briefs for it. Source of truth stays `spine.md`. Both lengths
render from it. No prose generates before spine, diagram briefs, and link
pack are signed.

## Section 2: Components (approved)

- `voice-sheet.md`: one entry per habit, each with a liked line and a
  rejected line showing its edge.
- `pairs/`: draft vs rewrite snippets. Rewrites win.
- `spine.md`: kicker, claim, link to prior claim, body brief per section.
- `budgets.json`: prose caps plus figure-area caps (see area budget below).
- `cut.py`: derives the 2-pager by dropping bodies, keeping every title.
- `verify-voice.py`: existing script, gains the sheet as config.

## Section 3: Data flow and area budget (approved)

Flow: dump or interview into `spine.md` draft, propose briefs and link
pack, approve all three, draft 6-pager bodies against caps, voice check,
`cut.py` derives the 2-pager. `DECISIONS.md` appends at each gate. Every
run reads spine, sheet, and decisions file first.

Budget grounds in A4: 1-inch margins give a 159 by 246 mm block, 392 sqcm.
At 11pt and 1.5 spacing, about 75 chars over 42 lines, near 3,150 chars
per full-prose page. At 5.5 chars per word that is 573 words wall to wall,
about 460 after headings. Planning figure: 400 words per prose-only page.
A half-page figure displaces close to 230 words.

- Prose ledger in words, figure ledger in page fractions (0.25, 0.5).
- 6-pager: prose cap 2,400 minus 230 per half-page figure used. Figure cap
  1.5 pages total, max 4 figures, none larger than half a page.
- 2-pager: prose cap 800 minus displacement. Figure cap 0.5 page, max 2
  figures carried over, no new ones.
- `cut.py` enforces both ledgers. Over-words fails loud; over-area cannot fire because figures are dropped until the area fits, so area holds by construction.

## Section 4: Voice elicitation (approved)

Three passes, all stored. One: three 15-minute talk-throughs across
registers (opinion, explainer, work story); keep habits that survive all
three. Two: 20 to 30 A/B sentence pairs, one habit per pair; log the
reject as the counter-example. Three: deletion check; strip each habit in
turn and confirm the line goes flat without it. Single-topic habits never
reach the sheet. Later edit pairs overrule without a sheet rewrite.

Background: handing a model loose samples returns an average author
(Lari, June 2026); auto-inferred profiles mix registers and can study
their own prior output (ChatGPT Work, Sept 2026); "be concise" in a prompt
does not hold under uncertainty, so length needs a counted budget
(arXiv 2411.07858, verbosity compensation).

## Section 5: Failure modes and testing (approved)

Spine check before prose (titles alone read as one paragraph or drafting
stops). Budget check after (words plus figure area or the overrun is
named). Voice check last (flags only, never auto-fix). Reader check is
human on the 2-pager at 12th-grade level: any paragraph that needs its
citation to make sense gets cut or moved to the 6-pager. Skipped gates
fail closed.

## Section 6: Revision loop (approved)

Two-pass titles: pass one sets the claim before prose; pass two revisits
each title after its body and keeps whichever carries the section alone,
subject to the connective and title-only-read rules. Per round, in order:
reorder on broken connectives, merge on shared fact packs, drop sections
kept alive only by their link packs. Retitle touched sections, rerun spine
and budget checks. Cap at three rounds; leftovers land in `DECISIONS.md`
as open breaks with the owner's call, not a silent fourth rewrite.

## Open items for the plan

- Exact `budgets.json` shape and `cut.py` drop rules (which bodies yield
  first when the 2-pager overflows).
- `voice-sheet.md` schema and the A/B pair generator.
- `DECISIONS.md` seeding: which choices above enter as the first entries.
- 12th-grade check: scripted flag pass vs pure human read.
