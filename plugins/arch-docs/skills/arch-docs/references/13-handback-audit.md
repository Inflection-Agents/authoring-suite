# 13 Handback audit

**Goal.** Get out of the session what the tooling does not know yet, so the next set costs less.
**Produces.** Six audit sections ending in a ranked list of changes, each with its effort.
**Gate.** Every item is specific enough for the owner to act on, and the list is ranked by how often the problem recurs.

Run this when the set is delivered and before the session is closed. Audit the session and everything the agents did.
The question is what had to be worked around, so the tooling stops costing that next time.

## 1. Rules relaxed

Every rule of the skill or the brief that was suspended, bent or ignored. For each: the rule, how many pages broke it,
whether the relaxation was right, and what the rule should say instead. Count, do not estimate. When you cannot count
it, say so.

## 2. Work the library did not do

Every place an agent wrote a local helper or dropped to raw output because the library had no primitive. Group them. A
pattern that appears in three specs is a missing primitive. The build reports from [07](07-build-agents.md) carry these
if the agents were asked for them.

## 3. Checks that lied

Every checker finding dismissed as false, and why it fired. A checker that produces false failures trains people to
ignore it, which is worse than not having it.

## 4. Coordination failures

Every case of agents overlapping, rebuilding each other's work, or producing inconsistent output, with what in the
prompt allowed it.

## 5. What the prompts were missing

The things the owner had to say mid-session that should have been in the kickoff, the brief or the agent template. Quote
the correction and say which phase it belongs in.

## 6. What to change

Turn the five sections above into a ranked list of changes to the skill, the library and the phase files. Each with the
problem it solves, the effort, and whether it would have changed the outcome of this set. Rank by how often the problem
will recur, not by how annoying it was.

Be specific and be unflattering. A finding the owner cannot act on is not a finding.

## Two rules that came out of this audit

Both earned their place the hard way, and they belong in whatever gets built next.

**Checkers measure what they relax.** A checker that skips a rule reports what it did not measure. A silent exemption
trains people to trust a green result that means nothing.

**Exceptions are proposed by the builder and declared by the owner.** The builder that drew the over-budget page names
it in the handback with its reason, and the owner accepts it in the spec. An exception nobody declared is
indistinguishable from a mistake.

## Sending the fixes to a review agent

Make the reviewer adversarial and give it recipes rather than a theme:

- build fixtures that should fail and pass, and that should pass and fail
- check whether any baseline entry was added to hide a regression introduced on the same branch
- verify each claim the change makes by running it, not by reading it
- grep the whole diff for client identifiers, and treat any hit inside the distributed package as a blocker

Ask for numbered findings with severity, file and line, a minimal reproduction, and a split between what the reviewer
reproduced and what it suspects.

The measured cost of the problems this audit looks for is in [failure modes](failure-modes.md).
