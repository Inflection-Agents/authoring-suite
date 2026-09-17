# 08 Page critique

**Goal.** Find what is wrong with one page and name the fix, before anything on the page moves.
**Produces.** A numbered fix list, worst first, then the rebuilt page.
**Gate.** The owner has taken the findings, and the rebuilt page has been looked at again.

Use this when a page is built and has to be made right, and when the owner says something is off about a page but cannot
name it. Look at the rendered image with the Read tool first, then read its spec. Critique it against the brief and
against this skill's rules. Give the owner a numbered list before changing anything, worst first, each item naming what
is wrong, why it matters to a reader, and the fix.

## The checklist, in order

Work in this order, because an early item makes later ones moot. A page whose claim is wrong does not need its label
spacing fixed.

1. **The claim.** Does the page show what its title and subtitle say it shows? Is there a claim on the page that the
   facts file does not support?
2. **The focal.** Can a reader tell in two seconds what the page is about? Is the accent on at most two elements, and
   are they the right two?
3. **Geometry.** Any line through a label, label touching a box, two connectors sharing a path, connector passing behind
   a box that is not its endpoint, crossing without a hop, two connectors entering one point on an edge.
4. **Text.** Any text overflowing its box, any label over the character limit, any label that says nothing ("talks to",
   "handles"), any sublabel a reader cannot act on.
5. **Density.** Is anything on the page carrying no information? Would the reader lose anything if it were deleted? Name
   the deletions.
6. **Consistency.** Does every connector style mean what the brief says? Is every element drawn under its canonical
   name? Does the page match its neighbours in scale and in level of detail?
7. **The legend.** Does it explain only what is on this page?

Then apply the fixes the owner takes, rebuild, look at the image again, and say what changed. When a fix requires the
page to hold less, say what was cut and why, rather than shrinking the type.

## Two shorter ways for the owner to ask

The owner does not have to write a critique request. Two cheaper forms do most of the work once the definition of done
has fixed the vocabulary.

**An annotated screenshot with no text.** This was the main refinement channel across sixty-five diagrams. The owner
marks up the image, pastes it, and says nothing. Read the marks as the fix list and work the checklist above around them.

**The diagram number and the missing argument, not the missing pixel.** "Diagram 35 covers testing one capability
against its contract, which is right, but I also need it to say the end to end got simpler." The owner decides what the
page has to prove. You decide what moves on the page.

## Surface the judgment calls

After a wave, list the judgment calls made, each naming the diagram, the choice, and what would change it. "Diagram 11:
the facts confirm only three calls from the back-office UI, so the rest sit in one box labelled other services. Tell me
which ones the browser really calls and I will name them." A judgment call surfaced is cheap to correct. A judgment call
buried is what the owner finds in the meeting.

Findings that touch more than one page belong in [09](09-set-review.md). Findings that say the set has too many pages
belong in [10](10-prune-and-split.md).
