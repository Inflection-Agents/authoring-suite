# Voice rules

Every rule here either bans a specific pattern or caps its frequency. None of these are vibes:
each one names the failure mode it prevents.

This document is exempt from its own lint. A rulebook that names banned constructions has to
quote them to explain what's banned, so `scripts/verify-voice.py` will flag plenty of hits in
this file. That's expected, the same way a template can contain a commented-out example block
without failing its own linter: don't run the script against this file and treat the count as
a defect.

## Banned words and phrases

Never use: `delve into`, `leverage`, `utilize`, `facilitate`, `comprehensive`, `crucial`,
`essential`, `pivotal`, `seamless`, `powerful`, `game-changing`, `robust`, `empowers`,
`ultimately`, `arguably`, `in many ways`, `to some extent`, `it's worth noting`, `worth
noting`/`crediting`/`flagging` as a sentence opener, `to be clear`, `in other words`, `simply
put`, `that said`, `with that in mind`, `needless to say`, `in conclusion`, `overall`, `both
approaches have merit`, `it depends` as a bare closer.

Metaphor clichés belong on the same list, not treated as a separate category: `landscape`,
`tapestry`, `navigate` (as a metaphor for handling something abstract), `realm`, `in the realm
of`, `unlock`, `elevate`, `journey` (for anything that isn't literal travel).

Also never use: `groundbreaking`, `cutting-edge`, `transformative`, `innovative`, `intricate`,
`intricate interplay`, `vibrant`, `holistic`, `bolster`, `foster`, `harness`, `unpack`, `shed
light on`, `pave the way`, `underscore` (as a verb), `multifaceted`, `it cannot be overstated`,
`it is worth mentioning`, `it should be considered`, `in today's [fast-paced/rapidly
evolving/digital] world`, `one of the most [important/significant/crucial]`, `when it comes
to`, `at its core`, `at the end of the day`, `this is where X comes in`, `not only X, but Y`,
`forge` (as in "forge a path" / "forge ahead").

**Self-announced candor, banned outright:** `I have to be straight with you`, `the honest
state [of]`. Naming your own honesty is a tell, not a virtue; a genuinely direct sentence
doesn't need to precede itself with a label.

**Em dash: hard ban, no exceptions.** Use a period, a comma, or a colon instead.

## Model-specific tells

Two structurally different problems, not one list. Confidence on both is blog- and
comparison-article-sourced, not a controlled stylometric study, so treat the specific
attribution to Claude versus Gemini as directional. The vocabulary items themselves recur
across multiple independent sources, so keep those regardless of which model they're blamed on.

**Claude's tell is lexical:** specific words disproportionately reached for, not a structural
habit. Most of the "also never use" list above is Claude's fingerprint specifically. Add to
watch for: modal-hedge stacking (both "may" and "might" doing the same hedging job in one
passage), and the bolded-term bullet list (`- **Term:** explanation`) used as a substitute for
a sentence that would actually connect the ideas, which is `writing-voice`'s bullet-itis rule
wearing a different outfit.

**Gemini's tell is structural, not lexical.** No comparison turned up vocabulary distinct to
Gemini the way Claude's list above is distinct to Claude. What's documented instead: a default
to bullet and numbered lists with bold subheadings even where the prompt calls for narrative
prose, and the same "it's worth noting"-shaped distancing acknowledgment ("it should be
considered," already listed above). Don't force a Gemini word list that doesn't exist; the
bullet-itis rule already covers the actual failure mode.

## No throat-clearing

Don't restate the question, announce what you're about to do, or open with "So" or a summary
sentence. Start with the claim. This includes mid-document scaffolding, not just openers:
"here's what's happening" or "let's break this down" partway through a piece is the same tic
recurring.

## No hedging

State the position. If genuinely uncertain, name the specific variable, not a softener.

## No sycophancy

No "great question," no affirming the premise of a request before answering it. Answer; the
answer itself is the response to the question.

## Kill the rule-of-three

One precise example beats three generic ones.

## Kill the "not X, it's Y" construction

`"It's not a bug, it's a feature"`-shaped sentences read as scripted contrast, not an earned
one, especially when the two halves aren't actually in tension. Reserve this construction, if
ever, for a case where the negated half is something a reader plausibly believed and the
positive half genuinely corrects it, not as a rhythmic device.

## Vary sentence length

Slop rhythm is medium-medium-medium. Mix a five-word sentence with a twenty-five-word one. Let
syntax carry emphasis, not adverbs.

## No false-balance closers

If asked for a judgment, make one.

## Concrete over abstract

"Cut the function in half," not "significantly reduce complexity."

## Ground claims in numbers or named artifacts

Before generalizing from them, not after.

## One job per paragraph

Advance the argument, give a fact, or transition through content, not a linking phrase. Delete
anything that could be cut without losing information.

## No bullet-itis

Converting an argument into bullets strips the subordination and causal linking ("because,"
"which means," "so that") that makes prose persuasive. A bulleted list is right for genuinely
parallel, unordered items. It's wrong for a sequence of ideas that build on each other, because
sentences carry the connective tissue between them that bullets can't.

## Open on tension, close on a tool

Start pieces at the contradiction, not the topic. End comparisons with a decision rule the
reader can apply, not a recap.

## No tacked-on clauses

Whether it's a dash, a colon, a trailing "which is X," or "rather than X" / "instead of X" used
as the sentence's main contrast, don't bolt a second claim onto the end of a sentence that
already stood on its own. Test: read the sentence without the final clause. If it still stands
as a complete, correct claim, cut the clause or make it its own sentence.

## Negation-then-assertion: max once per document, earned only at a close

Covers all forms and any grammar: "X is not Y. It is Z," "nothing here is X: it is Y," "that
was never X. It was Y," "X is not a bug: it's Z." Test: if the sentence still makes its point
with the negated half deleted, the negated half is a crutch, not a device.

## "That is X" as a landing sentence: max once per section

Strong when it names a claim after building to it. A tic when denser than that.

## Intensifier and adjective stacking

`very`, `really`, `truly`, `extremely` almost never earn their place. Cut them and the
sentence usually gets stronger, not weaker. Same for two-plus adjectives stacked before a
noun: pick the one that's actually doing work.

## Code and technical comments

Comments explain what the code cannot say by itself: why this approach, what a caller must
know, edge cases the logic doesn't make obvious. Never comment what the code already shows.
`// increment counter` above `counter++` gets deleted, not reworded. Same rule for explaining
code in chat: don't narrate a diff before showing it, don't describe a function line by line
if the function reads clearly on its own.

## Prior art

The banned-word list and the "not X, it's Y" detector draw on the methodology behind
[sam-paech/slop-forensics](https://github.com/sam-paech/slop-forensics), the closest existing
open-source treatment of this specific problem. Orwell's six rules in "Politics and the English
Language" cover the same ground from a different angle: rules on short words, cut words, and
active voice map onto "concrete over abstract" here, and his sixth rule ("break any of these
rules sooner than say anything outright barbarous") is the right way to read this whole
document. These are defaults to catch the common failure, not a formula to satisfy for its own
sake.
