# Arcs

The order of the beats. Pick one, commit to it, and let it decide what goes where. Most
"this deck jumps" problems are an arc problem, not a wording problem: no amount of title
polish rescues a sequence that grouped code-level architecture, cloud choices, and business
problems in alternating order.

---

## 1. Technical strategy (default)

The workhorse for platform proposals, architecture strategy, and re-platforming cases. Also
the right shape for most internal "we should change how we build" arguments.

| # | Beat | Kicker | The slide answers |
|---|---|---|---|
| 1 | Cover | brand | What is this, and what changes? |
| 2 | **Situation** | THE SITUATION | What is true today, stated without blame? |
| 3 | **Complication** | THE COMPLICATION | What external reality makes it worse? |
| 4 | **Consequence** | THE CONSEQUENCE | What does it cost the business? |
| 5 | **Resolution** | THE RESOLUTION | What is the pivot, in one sentence? |
| 6 | **Map** | THE TWO DIMENSIONS | What are the axes the rest of the deck navigates? |
| 7-11 | **Mechanism A** | DIMENSION ONE - ... | How does the first axis actually work? |
| 12-13 | **Proof** | WORKED EXAMPLE - ... | Where does this already hold in reality? |
| 14-18 | **Mechanism B** | DIMENSION TWO - ... | How does the second axis actually work? |
| 19-21 | **Economics** | ...ECONOMICS | Why does this make money, not just sense? |
| 22 | **Flywheel** | THE FLYWHEEL | Why does the advantage compound? |
| 23 | **Ask** | THE INVESTMENT | What is needed, and what does it unlock? |

### Why this order

Three sequencing rules do the work, and violating any of them is what produces jumps:

1. **Problem before solution, cost before pivot.** An audience will not accept a solution to
   a problem they have not agreed is expensive. Consequence must land before Resolution.
2. **Code before cloud.** How a component is built must precede where it runs. Reversing this
   forces the audience to hold an unexplained abstraction while hearing infrastructure.
3. **Proof before scale.** Show it working on something real before arguing it works
   globally. A scaling argument about an unproven mechanism is a hypothesis.

### The Map slide

Optional, and the highest-leverage slide in the arc when the solution has two independent
dimensions that will otherwise be conflated. It prevents the most expensive kind of
confusion: the audience silently merging two ideas and then finding everything downstream
contradictory.

Two obligations come with it:

- **Signpost every downstream slide** with its branch, in the kicker.
- **Announce the switch** when moving from branch one to branch two, in the kicker of the
  first slide of the new branch. Without it, the audience is still in branch one and reads
  everything wrongly.

---

## 2. Executive walk-around (7 to 9 slides)

Derived from a longer deck, and read without a presenter. Not a summary: a **re-argued**
version at lower resolution. Summarising by deletion is what produces the "very weak story
narrative with unnatural leaps" failure, because deleting slides deletes the connectives.

| # | Beat | The slide answers |
|---|---|---|
| 1 | Vision | What is the transformation, in business terms? |
| 2 | The Challenge | What is broken, and what does it cost? (merges Situation + Complication + Consequence) |
| 3 | The Strategic Pivot | What is the answer, and what are its two dimensions? (merges Resolution + Map) |
| 4 | Dimension One | How do we build differently? |
| 5 | Dimension Two, part 1 | Where does it run? |
| 6 | Dimension Two, part 2 | How is it shared safely? |
| 7 | Economics | Why does this improve margin? |
| 8 | The Flywheel | Why does it compound? |
| 9 | The Ask | What is needed? |

**Merging beats is where this goes wrong.** When three beats merge into one slide, the
sub-points must be explicitly labelled as cause and effect, not listed as three facts. A
merged slide with an unlabelled list reads as three unrelated problems.

**Splitting is often required too.** If one condensed slide has to carry geography plus
tenancy plus economics, split it into three, even in a short deck. Fewer slides is not the
goal; fewer *ideas per slide* is. A nine-slide deck that lands beats a seven-slide deck that
confuses.

---

## 3. Decision / ADR

For a specific choice needing a specific approval.

| # | Beat | The slide answers |
|---|---|---|
| 1 | The Decision | What are we deciding, in one sentence? |
| 2 | Context | What forces this now? |
| 3 | Criteria | What are we optimising for, in priority order? |
| 4 | Options | What are the real candidates? (never a strawman) |
| 5 | Assessment | How does each score against the criteria? |
| 6 | Recommendation | Which one, and why? |
| 7 | Consequences | What becomes harder, and what door stays open? |
| 8 | The Ask | What approval, by when? |

Slide 7 is what earns trust. A recommendation with no stated downside reads as advocacy, and
a technical audience discounts it immediately.

---

## 4. Sales / pitch

| # | Beat | The slide answers |
|---|---|---|
| 1 | Hook | What is their pain, in their words? |
| 2 | Stakes | What does the status quo cost them? |
| 3 | Approach | How do we solve it, in one sentence? |
| 4-5 | Mechanism | How does it actually work? |
| 6 | Proof | Who else, and what happened? |
| 7 | Process | What does working together look like? |
| 8 | The Ask | What is the specific next step? |

Focus on their outcomes, not our features. The connectives still apply: a pitch that jumps
is a pitch that loses.

---

## 5. Whitepaper

The same spine, in prose. Titles become section headings, and they still have to pass the
governing test: reading only the headings gives the argument.

| Section | From the spine |
|---|---|
| Executive summary | The whole spine compressed to one paragraph, written last |
| The situation | Beats 2 to 4 |
| The proposal | Beat 5, plus the map |
| How it works | The mechanism beats, one subsection each |
| In practice | The proof beat, expanded with real detail |
| Economics | The economics beats, with the numbers a slide could not hold |
| What we need | The ask |

A whitepaper carries what a deck cannot: derivations, numbers, caveats, and prior art. It
must not carry a different argument. Same spine, more evidence.

---

## 6. Conference talk

| # | Beat | The section answers |
|---|---|---|
| 1 | Hook | Why should anyone lean in? (a story or a surprising number) |
| 2 | Problem | Why does this matter beyond one company? |
| 3-5 | Insights | Three ideas, each with one concrete example |
| 6 | Takeaways | What should they do differently on Monday? |
| 7 | Close | Callback to the hook |

Minimise bullets, maximise story. Slides support the speaker rather than carrying the
argument, which makes this the one format where the governing test relaxes. The **script**
still has a spine; see `references/formats.md`.

---

## Diagnosing a broken arc

| Symptom | Likely cause | Fix |
|---|---|---|
| "It jumps" | Missing connectives, or wrong order | Run the Sudden Jump audit in `spine-review.md` |
| "Too deep too fast" | Mechanism before Resolution | Move the pivot earlier |
| "Why are we talking about this?" | Beat is in the wrong section | Regroup: problem, pivot, architecture, proof, scale, payoff |
| "I lost the thread halfway" | A map was declared and abandoned | Signpost every downstream slide |
| "What are you actually asking for?" | No Ask beat, or a vague one | Add a specific ask: what, why now, what it unlocks |
| "Confused about slide N" | Slide N holds two or three ideas | Split it, even if the deck gets longer |
| "Great deck, so what?" | Economics or Flywheel missing | Add the payoff beat; mechanism alone does not motivate |
