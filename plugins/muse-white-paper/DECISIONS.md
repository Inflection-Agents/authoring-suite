# DECISIONS.md — muse-white-paper

Append-only running log. Read at the start of every run, appended at each
gate. Entry shape follows `sdlc/templates/decisions.md`: question, decided,
rejected, reversal path. Open breaks land here with the owner's call, never
as a silent extra rewrite round.

## D1: Voice source

**Question:** Where does the owner's voice come from — inferred samples, an
explicit sheet, edit pairs, or a mix?

**Decided:** Explicit `voice-sheet.md` owned by the writer, corrected by
draft-vs-rewrite edit pairs. On any conflict between the sheet and a stored
rewrite, the rewrite wins without a sheet edit.

**Rejected:** Pure sample-inference (returns an average author; mixes
registers), sheet-only with no veto path (goes stale the first time the
owner overrides it in practice).

**Reversal path:** If rewrites contradict each other across registers, split
the sheet by register instead of letting the latest rewrite win silently.
Record the split here as a `SPEC DEVIATION` block.

## D2: One spine, two renders

**Question:** Are the 6-pager and the 2-pager written separately or derived
from one source?

**Decided:** One spine, two renders. The 2-pager is cut from the 6-pager by
`cut.py`, never a separate write. `spine.md` is the source of truth; no
prose generates before spine, diagram briefs, and link pack are signed.

**Rejected:** Two independent drafts (claims drift apart; double the review
cost), 2-pager-first expansion (short argues differently than long cut down;
expansion bloats past caps).

**Reversal path:** If a brief must argue something the paper never states,
add the section to the spine and re-sign rather than writing brief-only
prose. If that happens twice for the same audience, propose a standing
third render here instead of a third one-off cut.

## D3: Hybrid storyboard

**Question:** How does raw material become a spine — rough dump, interview,
or both?

**Decided:** Hybrid. A rough dump when one exists, an interview when
starting blank. Both land in the same `spine.md` shape (kicker, claim, link
to prior claim, body brief per section).

**Rejected:** Dump-only (blank-page starts stall), interview-only (wastes an
existing draft and its momentum).

**Reversal path:** If interviews keep producing spines the dump path would
have rejected at the title-only read, log the failure pattern here and
tighten the interview questions, not the spine schema.

## D4: Plugin proposes briefs, owner approves

**Question:** Who proposes diagrams and links, and when are they approved?

**Decided:** The plugin proposes one diagram brief per section plus a link
pack (fact pack plus outbound citations); the owner approves all three —
spine, briefs, link pack — before any prose. `diagram-design` stays
untouched; the plugin only writes briefs for it.

**Rejected:** Prose-first with figures fitted after (figures duplicate prose
instead of carrying their own claim), auto-accepted briefs (unreviewed
diagrams misstate the argument they illustrate).

**Reversal path:** If the owner rewrites more than half the briefs two runs
in a row, the brief format is wrong. Record an `EXECUTIVE DECISION` here
with the new format and update the storyboard questions to match.

## D5: Area budget numbers

**Question:** What are the word and figure-area caps for each render?

**Decided:** Grounding: A4 with 1-inch margins at 11pt/1.5 spacing, planning
figure 400 words per prose-only page. A half-page figure displaces 230
words. 6-pager: prose cap 2,400 minus 230 per half-page figure used; figure
cap 1.5 pages total, max 4 figures, none larger than half a page. 2-pager:
prose cap 800 minus displacement; figure cap 0.5 page, max 2 carried over,
no new ones. Over words or over area both fail; `cut.py` enforces both
ledgers.

**Rejected:** Word-only caps (a figure-heavy page passes while overflowing
the layout), fixed per-section caps (starves the claim section to feed
filler), "be concise" prompting with no counted budget (does not hold under
uncertainty).

**Reversal path:** If print checks show the 400-words-per-page figure is off
by more than 10% for the owner's actual layout, update the per-half-page
displacement and both prose caps together here — never one without the
other — and re-run every fixture.

## D6: Three-round revision loop cap

**Question:** How many revision rounds before stopping, and where do
leftovers go?

**Decided:** Cap at three rounds. Per round order: reorder on broken
connectives, merge on shared fact packs, drop sections alive only by their
link packs; retitle touched sections and rerun spine and budget checks.
Unresolved breaks land here as open items with the owner's call recorded,
not a silent fourth rewrite.

**Rejected:** Uncapped iteration (converges on the reviewer's taste, not the
owner's claim), single-pass no-retitle (titles promise what bodies no
longer argue after round-one edits).

**Reversal path:** If the same open break recurs three runs running, it is a
missing spine section, not a wording problem. Add the section and re-sign
the spine; record the addition here.

---

## D-007 — Shared PDFs are story inputs, never citations

**Date:** 2026-09-12
**Question:** May the paper cite the two PDFs (Durable Execution Proposal Jan 2024, Ventures x Restate Q4 2025)?
**Decided:** No. Both inform the spine; every fact needs an independent public source.
**Rejected:** Citing them directly (one is confidential-marked, the other's funding numbers contradict themselves).
**Raised by:** owner

## D-008 — Owner-attested claims and their print status

**Date:** 2026-09-12
**Question:** How to handle claims the owner confirms from experience that lack public sources?
**Decided:** Exactly-once vs at-least-once delivery (founder conversation) and Restate's lack of serialization limits print as owner-attested, labeled as such. Admin API registry claim verified at https://docs.restate.dev/admin-api/service/list-services (GET /services returns handlers, deployment_id, revision).
**Rejected:** Holding the paper for public proof of all three; asserting unattested mechanisms (log-segment tiering) as fact.
**Raised by:** owner
