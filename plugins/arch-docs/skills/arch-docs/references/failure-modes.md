# Failure modes

These nine traps were measured on one engagement: 65 diagrams, 38 agents, 177 builds and 197 image reviews. Every number
below is a count from that engagement, not an estimate, and each entry names the fix that worked. They are the reason the
phases are shaped the way they are, so read an entry when you are about to skip the phase it belongs to.

**Agents overlapping on files.** One agent rebuilt pages it did not own. Fix: name the owned files, the forbidden files,
and the numbers other agents hold right now, and ban the whole-set build command from agent prompts. See
[07](07-build-agents.md).

**A model filling a gap it should report.** Fix: open items are drawn as open, never as designed, and the agent reports
the thin spot instead of inventing a number, a threshold or a vendor.

**Checkers that lie, and agents that chase them.** The consistency checker compared the type-tag chip instead of the
element name, which made all 12 of its label findings false, and it demanded a field flow diagrams do not carry, which
made 15 more. Fix: the definition of done names the known-false warnings and how to dispose of them. Every dismissal is
recorded for [13](13-handback-audit.md).

**Budgets exceeded invisibly.** 47 of 65 diagrams went over the box or arrow limit, the largest at 27 boxes, and about
10 pages carried more accent than the budget allows once connectors are counted. The relaxation was deliberate and the
invisibility was not. Fix: declare the profile up front and have the builder propose exceptions in its handback, which
the owner then declares.

**Caps discovered per diagram instead of set once.** The label cap moved from 14 to 16 characters and 96 labels then
landed on 15 or 16, which means the cap was doing the design. Fix: set it in the brief.

**Prose tooling corrupting source.** A regex-based prose editor broke five spec files on a single apostrophe. Fix: edit
through an AST tool that refuses rather than guesses. This is why [11](11-language-pass.md) shows a before and after
table and rebuilds, instead of running a sweep.

**Stale numbers after renumbering.** The set was renumbered three times, from 23 to 41 diagrams. Fix: one
machine-readable manifest owns numbers and slugs, briefs never restate them, and a rename deletes the old page and
image. See [12](12-late-change.md), which maps by slug rather than by number.

**Client material reaching a public repo.** Fix: a named confidentiality grep list in any prompt that touches a shared
repo, and a required zero-matches line in the report.

**Hand-rolled primitives, 21 of them across 9 specs.** Fix: ask every builder for the library gaps it worked around,
from the first wave, and add the primitive once centrally.
