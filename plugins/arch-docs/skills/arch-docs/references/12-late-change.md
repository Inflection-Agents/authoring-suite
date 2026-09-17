# 12 Late change

**Goal.** Realign a finished set to a rename, a reversed decision, or the code that shipped.
**Produces.** The updated set, and a list of everywhere the new source contradicted the earlier facts.
**Gate.** Every contradiction is reported to the owner, not absorbed into the pages.

A finished set is not finished. This phase is what keeps it alive instead of letting it drift into a historical artifact.

**Read first:** `_brief/facts.md`, `_brief/brief.md`, the library (do not edit it), and the new source, which is the
shipped code, a decision record, or a message from the owner.

## The rename

Take the old term, the new term, and the reason in one line. Ask for the reason if the owner did not give one. You will
meet edge cases and the reason is what tells you which side of the line they fall on.

Rename it everywhere: titles, slugs, subtitles, notes, labels, element names, the facts file and the brief. Where a slug
changes, rename the spec file, delete the stale page and image, and rebuild so the file names match the manifest. Where
the old term legitimately survives with a different meaning, say so in the facts file so the two never collide.

Verify with a grep for the old term across the specs and the brief. The only hits left should be ones you can justify in
your report.

## Aligning to the implementation

Read the new source and correct the diagrams to match it. Record what it says in the facts file first, in a dated
section, marked as coming from the implementation, and name which earlier line each fact corrects. Do not silently edit
the original line.

Ask the owner for the behaviours to check, in the code's own vocabulary, and be concrete: the names of the states, the
shape of the keys, what runs in parallel, what short-circuits, what is ordered, what is idempotent, what happens on
terminal failure. For each behaviour, check the diagram that claims to show it.

Name which diagrams change and what changes on each. Keep every other page's layout.

## Numbering

The owner's diagram numbers may be stale, because [10](10-prune-and-split.md) renumbers the set. Map by slug against the
current manifest and tell the owner the mapping you used.

## The build loop

For each changed page: build, screenshot, look at the image with the Read tool, and iterate until it meets the
definition of done in the brief. Then run the full set build, confirm the set checks pass and the index regenerates, and
delete stale pages and images for renamed slugs.

## The report

Files renamed, what changed on each diagram, **every place the new source contradicted the earlier facts**, remaining
warnings, and anything you could not resolve. The contradictions list is the part the owner cares about most, because it
is where their understanding was wrong.
