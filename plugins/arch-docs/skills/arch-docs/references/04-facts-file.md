# 04 Facts

**Goal.** Write the one file every later phase and every build agent reads first.
**Produces.** `_brief/facts.md`.
**Gate.** The owner has corrected it.

One file carries the whole engagement. A build agent reads it and nothing else about the domain, so anything not in
this file does not exist. It has to be complete enough to draw from and short enough to read in full.

Enter this phase when the interview in [02](02-interview.md) is answered and, where there was source,
[03](03-source-reconciliation.md) is closed.

## The section list

Lift this skeleton into `_brief/facts.md` and fill it. The order matters, because an agent that hits a
contradiction reads upward to find which side wins.

```markdown
# Facts: <SET NAME>

## Header
Source: the owner's interview on <DATE>, unless a line is marked otherwise.
Companion set: <PATH TO THE OTHER FACTS FILE>, where a second architecture exists.
Digested elsewhere: <OLDER DOCUMENT>. A detail from it is used only where it agrees with this file, and is marked.
Dead vocabulary: <TERMS that appear in old documents and are not real>.

## 1. Decisions that override everything below
The owner's rulings from reconciliation, numbered, one bold claim plus the reason each.
This section outranks the body, so an agent that finds a contradiction knows which side wins.

## 2. Design goals
Numbered and ranked, one bold phrase plus one sentence each. Only for a proposal set.

## 3. Actors and boundary

## 4. Containers
One bullet each: what it is, what it holds, what it talks to. Components nest under the container that owns them.

## 5. Contracts
Field-level shape wherever a diagram will show fields.

## 6. Flows
One short paragraph per flow the set will draw.

## 7. State and keys
Key shapes as literal strings.

## 8. Configuration
Who writes, who reads, and what is not validated.

## 9. Failure behaviour

## 10. Open items
Everything the owner said was undecided, deferred or unknown, each naming who decides.
These get drawn as open, dashed and labelled, never as designed.

## 11. Vocabulary
The exact name for each thing, and the wrong names it must never be called.
Include the terms banned set-wide, so a phrase rejected on one page cannot reappear on another.

## 12. Implementation notes, <DATE>
Added only when shipped code contradicts a line above. Records what the code says and which earlier line it
corrects. The earlier line stays where it is.
```

## Rules for what goes in

- **Every statement is something the owner said, or something agreed after reconciliation.** Mark anything else with
  its source in bold brackets.
- **Write facts, not prose.** A bullet a build agent can act on beats a paragraph that reads well.
- **Numbers, thresholds and vendor names appear only where the owner gave them.**
- **Never silently edit a line the code has overtaken.** When the implementation contradicts this file, add the
  dated implementation section and name the line it corrects. [12](12-late-change.md) runs on that section.

## Before anything is drawn

Show the file to the owner. Their corrections are binding on every later diagram, and they go into the file rather
than into the conversation. Once the owner has corrected it, [05](05-diagram-list.md) proposes the set.
