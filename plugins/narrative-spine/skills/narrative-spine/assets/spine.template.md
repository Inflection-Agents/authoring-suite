# Spine: <DECK NAME>

> Source of truth. Every format renders from this file. Edit here first, always.

## Frame

| | |
|---|---|
| **Audience** | Who is in the room, and what they decide |
| **Decision sought** | The one thing they should do afterwards |
| **Arc** | technical-strategy \| executive \| decision \| pitch \| whitepaper \| talk |
| **Formats** | full deck, executive deck, whitepaper, script |
| **Design system** | `_ds/<name>` |
| **Diagram preset** | neutral-dark \| labrynth \| light |

## The one-paragraph argument

Written before any slide, and rewritten after the spine settles. If this paragraph is not
persuasive, no arrangement of slides will be.

> ...

## Glossary

Fix the vocabulary before writing. Drift is expensive to fix later.

| Term | Means | Never call it |
|---|---|---|
| Component | | |
| Product | | |
| Client | | |
| Tenant | | |

---

## Spine

<!--
  One block per slide.
  Link  = the connective move binding this slide to the previous one
          (concession, escalation, consequence, resolution, taxonomy, mechanism,
           instantiation, extension, causation, evidence, implication, objection,
           quantification, ask)
  Brief = one line on what the body must establish
  Diagram = the claim the picture must prove. Equals the title, verbatim.
-->

### 01 - Cover
- **Kicker:** <PROGRAMME NAME>
- **Title:** From <current state> to <target state>
- **Subtitle:** <mechanism and payoff, one sentence>
- **Link:** opens
- **Brief:** the section names, so the arc is visible before it starts

### 02 - Situation
- **Kicker:** THE SITUATION
- **Title:** Despite <true thing>, we <the choice we are making>.
- **Link:** opens the argument
- **Brief:** three factors, each with its so what
- **Notes:** the line that matters / the translation / the likely question

### 03 - Complication
- **Kicker:** THE COMPLICATION
- **Title:** This <problem> is compounded by <external reality>.
- **Link:** escalation
- **Brief:**
- **Notes:**

### 04 - Consequence
- **Kicker:** THE CONSEQUENCE
- **Title:** Because <cause>, <business cost>.
- **Link:** consequence
- **Brief:** convert the technical problem into money or time
- **Notes:**

### 05 - Resolution
- **Kicker:** THE RESOLUTION
- **Title:** To break this cycle, we must <the pivot>.
- **Link:** resolution
- **Brief:**
- **Notes:**

### 06 - Map
- **Kicker:** THE TWO DIMENSIONS
- **Title:** <the taxonomy the rest of the deck navigates>
- **Link:** taxonomy
- **Brief:** two dimensions, each with its action and its value
- **Diagram:** <claim>
- **Notes:** every slide from here signposts its branch in the kicker

### 07 - <Mechanism>
- **Kicker:** DIMENSION ONE - <NAME>
- **Title:** To <achieve outcome>, we <mechanism>.
- **Link:** mechanism
- **Brief:**
- **Diagram:** <claim, equal to the title>
- **Notes:**

### NN - Proof
- **Kicker:** WORKED EXAMPLE - <REAL THING>
- **Title:** We already see this in <thing>, which <decomposes as ...>.
- **Link:** evidence
- **Brief:** one real named thing, decomposed
- **Diagram:** <claim>
- **Notes:**

### NN - Economics
- **Kicker:** <...> ECONOMICS
- **Title:** <action> drives <metric> toward <limit>.
- **Link:** quantification
- **Brief:** three numbers maximum, each with a comparison
- **Notes:**

### NN - Flywheel
- **Kicker:** THE FLYWHEEL
- **Title:** Every <unit of work> makes the next one cheaper: <the loop>.
- **Link:** implication
- **Brief:** the loop, and the gain per turn
- **Diagram:** <claim>
- **Notes:**

### NN - The Ask
- **Kicker:** THE INVESTMENT
- **Title:** To unlock <payoff>, we require <specific ask>.
- **Link:** ask
- **Brief:** workstreams, each with the work and its value; close on what it unlocks
- **Notes:**

---

## Title-only read-through

Paste the titles here, in order, as one paragraph. This is the governing test.

> Despite clear repeating patterns across our solutions, we build or fork every use case
> from scratch. This bespoke engineering is exponentially compounded by the strict data
> governance required by our global client base. Because both the application code and the
> infrastructure are bespoke, our cost to serve scales linearly with every client we win.
> To break this cycle, we must transition to a composable platform, ...

## Executive cut

The beats that survive in the 7 to 9 slide version, and how they merge. Re-argue, do not
delete.

| Exec slide | Merges | New title |
|---|---|---|
| 02 The Challenge | 02, 03, 04 | |
| 03 The Strategic Pivot | 05, 06 | |

## Anticipated questions

The three hardest, with real answers.

1. **Q:**
   **A:**
2. **Q:**
   **A:**
3. **Q:**
   **A:**

## Post-delivery notes

What confused people, what they asked, what to fix. A confused audience is data about the
deck.
