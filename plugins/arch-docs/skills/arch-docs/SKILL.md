---
name: arch-docs
description: Run an architecture documentation engagement end to end, from the first interview to a delivered diagram set. Use when documenting an existing system or a proposed one, when producing a C4 diagram set for a client or a stakeholder review, when an architecture deliverable spans several sessions and needs to stay consistent, or when a finished set must be realigned to shipped code or a renamed concept. Owns the process and the artifacts; calls diagram-design to draw and writing-voice for the prose.
license: MIT
---

# Architecture documentation

A diagram set fails as a set long before any single page is wrong. The same service appears under two names, two
pages make the same point, a term is used eight pages before it is defined, and every page passes its own checks.

This skill runs the engagement as a sequence of phases, each producing one artifact the next phase reads. That
chain is what holds a set together across many diagrams, many agents and many sessions.

## The sequence

| Phase | Reference | Produces | Gate before moving on |
|---|---|---|---|
| Kickoff | [01](references/01-kickoff.md) | the frame: audience, deliverable, process rules | the owner has corrected the playback |
| Interview | [02](references/02-interview.md) | answers to what blocks drawing | no question left that would change a page |
| Reconcile | [03](references/03-source-reconciliation.md) | a closed list of disagreements | the owner has ruled on every one |
| Facts | [04](references/04-facts-file.md) | `_brief/facts.md`, the source of truth | the owner has corrected it |
| Plan | [05](references/05-diagram-list.md) | the diagram list, as layers | the owner has approved the list |
| Brief | [06](references/06-build-brief.md) | `_brief/brief.md`, one paragraph per diagram | conventions are fixed |
| Build | [07](references/07-build-agents.md) | the diagrams | every page meets the definition of done |
| Refine | [08](references/08-page-critique.md), [09](references/09-set-review.md), [10](references/10-prune-and-split.md) | a set that argues one thing | the owner has taken the findings |
| Voice | [11](references/11-language-pass.md) | every word on the page in the owner's voice | three rounds, then open items |
| Change | [12](references/12-late-change.md) | the set realigned to new source | contradictions reported, not absorbed |
| Audit | [13](references/13-handback-audit.md) | what to fix in the tooling | ranked, with effort |

Load one reference when you enter its phase. Do not load them all.

Also available: [failure modes](references/failure-modes.md), measured on the engagement this came from, and
[composition](references/composition.md), which says what this skill owns and what it delegates.

## Where you are

State lives on disk, not in this skill. Read it before doing anything:

1. The **ledger** at `<set>/_brief/engagement.md` records the phase and what the owner approved. Format and rules in
   [ledger.md](references/ledger.md).
2. The **artifacts** say the rest. `facts.md` exists or it does not. The manifest exists or it does not. Pages exist
   or they do not.

When the two disagree, the artifacts win and the ledger gets corrected. When there is no ledger, offer to write one
from what is on disk, then start at the earliest phase whose artifact is missing.

## The gates advise, they do not block

State the gate, say what is missing, and ask once. Then do what the owner says. A small engagement legitimately
skips the reconciliation phase and sometimes the brief. What is never skipped is the facts file, because every
build agent reads it and nothing else about the domain.

Refusing to proceed is wrong. Proceeding silently past a missing gate is also wrong.

## Five rules that carry the work

1. **Nothing gets drawn before the list is approved.** A paragraph per diagram costs nothing to read and nothing to
   cut. Drawing the wrong set costs a day.
2. **One facts file is the source of truth, and it records provenance.** Every claim on a page traces to it. A
   detail from an older document survives only where it agrees, and is marked.
3. **Draft wider than needed, then prune.** Pruning is fast, and it is the only reliable way to learn which
   diagrams were carrying the argument.
4. **Disagreements are surfaced as a numbered list and closed by the owner.** When the interview and the code
   conflict, never pick a winner quietly.
5. **The words are a separate pass.** Prose written while placing boxes comes out correct and anonymous.

## Delegating to agents

Every agent prompt this skill writes, drawing or not, carries these ten. Check a prompt against the list before
sending it.

1. Mode line first: build, read-only, or adversarial.
2. Absolute working directory, and the repo and branch when it is code.
3. A numbered read-first list, each item annotated with why it matters.
4. One named source of truth, with the override order stated.
5. Ownership: files owned, files forbidden, and the names of the agents working concurrently.
6. A loop with the actual commands in it.
7. A definition of done, referenced by name rather than restated.
8. An invention guard: never invent what the facts file does not support.
9. A voice line, even for code agents.
10. A reporting format, capped, that asks for what went wrong, including every library gap worked around.

## What never leaves the engagement

The ledger, the facts file, the brief and the pages belong to the owner's own repository. This skill ships generic.
Client names, internal component names and private paths never enter a shared or public repository, and a prompt
that touches one carries a confidentiality grep with a required zero-matches line in the report.
