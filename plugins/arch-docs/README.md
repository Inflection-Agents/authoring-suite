# arch-docs

Run an architecture documentation engagement end to end, from the first interview to a delivered diagram set.

A diagram set fails as a set long before any single page is wrong. The same service appears under two names, two
pages make the same point, a term is used eight pages before it is defined, and every page passes its own checks.
This plugin runs the engagement as phases, each producing one artifact the next phase reads.

## Install

```
/plugin marketplace add Inflection-Agents/authoring-suite
/plugin install arch-docs@authoring-suite
```

Install `diagram-design` alongside it, which does the drawing, and `writing-voice`, which owns the prose rules.

## The sequence

| Phase | Produces |
|---|---|
| Kickoff | the frame: audience, deliverable, process rules |
| Interview | answers to what blocks drawing |
| Reconcile | a closed list of disagreements between the owner and the source |
| Facts | `_brief/facts.md`, the source of truth |
| Plan | the diagram list, as layers |
| Brief | `_brief/brief.md`, one paragraph per diagram |
| Build | the diagrams |
| Refine | a set that argues one thing |
| Voice | every word on the page in the owner's voice |
| Change | the set realigned to shipped code or a renamed concept |
| Audit | what to fix in the tooling |

## Commands

`/arch-docs:status` says where the engagement stands and what the next gate needs. The rest map to the phases:
`kickoff`, `interview`, `reconcile`, `facts`, `plan`, `brief`, `build`, `review`, `voice`, `change`, `audit`.

`review` takes an optional page number. With one it critiques that page; without one it reviews the set.

## Where the state lives

On disk, in the owner's own repository. `_brief/engagement.md` records the phase and what the owner approved;
everything else is derivable from the artifacts. When the ledger and the files disagree, the files win.

Nothing client-specific belongs in this plugin. The ledger, the facts, the brief and the pages stay in the
engagement's own repository.

## Why the gates advise instead of blocking

A small engagement legitimately skips the reconciliation phase, and sometimes the brief. What is never skipped is
the facts file, because every build agent reads it and nothing else about the domain. So each phase states its
gate, says what is missing, asks once, and then does what the owner says.
