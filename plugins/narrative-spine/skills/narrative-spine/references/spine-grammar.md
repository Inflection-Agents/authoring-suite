# Spine Grammar

How a title is built, and how it binds to the one before it. This is the mechanical layer
under the governing test.

---

## The kicker

One to four words, uppercase, letter-spaced. It names the **beat**, not the topic. A reader
who has lost the thread should recover it from the kicker alone.

### Forms

| Form | Example | Use |
|---|---|---|
| Beat name | `THE SITUATION`, `THE COMPLICATION`, `THE RESOLUTION` | Argument slides. The arc's own vocabulary. |
| Branch signpost | `DIMENSION ONE - COMPOSABILITY` | Any slide after a map. Mandatory there. |
| Subject label | `COMPONENT DESIGN`, `TENANT ISOLATION` | Mechanism slides inside a branch. |
| Evidence marker | `WORKED EXAMPLE - CERTAINTY` | Proof slides. Name the instance. |
| Objection marker | `THE TWO-WAY DOOR` | Slides that pre-empt a known pushback. |

### Rules

- **Unique within a deck**, with one exception: a branch signpost repeats deliberately, and
  that repetition is what holds the map together.
- **Never a sentence.** The kicker is a label; the title is the sentence.
- **Never redundant with the title.** Kicker `CLOUD STRATEGY` above a title beginning "Our
  cloud strategy is..." wastes the slot. The kicker should add position, not repeat content.
- Use a middot for compound kickers (`DIMENSION TWO - MULTI-TENANCY`), not a dash.

---

## The connective taxonomy

Every title after the first opens with a move that binds it to the previous slide. This is
the connective tissue. Without it, a deck reads as a list of true statements in an arbitrary
order, which is exactly what "it jumps" means when an audience says it.

Each move below is drawn from a working deck. The opener column is a starting point, not a
template to fill mechanically.

| # | Move | Job | Openers |
|---|---|---|---|
| 1 | **Concession** | Grant something true that makes the problem worse | "Despite X, we..." / "Even with X, ..." |
| 2 | **Escalation** | Stack a second problem on the first | "This X is compounded by..." / "Simultaneously, ..." |
| 3 | **Consequence** | Convert the problem into cost | "As a result, ..." / "Because both X and Y are Z, our..." |
| 4 | **Resolution** | Pivot to the answer | "To break this cycle, we must..." / "To fix this, ..." |
| 5 | **Taxonomy** | Declare the map the deck will navigate | "To scale, we must separate X from Y..." |
| 6 | **Mechanism** | Explain how the answer works | "To make X truly Y, we use..." / "We achieve this by..." |
| 7 | **Instantiation** | Give a concrete case | "For example, ..." |
| 8 | **Extension** | Apply the same idea to a new area | "This X extends to..." / "The same holds for..." |
| 9 | **Causation** | Derive a capability from a property | "Because X, we retain..." / "Since X, Y follows." |
| 10 | **Evidence** | Prove it against reality | "We already see this in..." / "X today already does Y." |
| 11 | **Implication** | Project the benefit forward | "By doing X, Y becomes..." |
| 12 | **Objection** | Pre-empt a known pushback | "While X provides Y, Z preserves..." |
| 13 | **Quantification** | Put a number or a limit on it | "Sharing X drives Y toward zero." |
| 14 | **Ask** | Request the decision | "To unlock X, we require..." |
| 15 | **Anaphora** | Point back at what the previous slide established | "This X...", "These Y...", "Each Z...", "Inside these..." |

### Anaphora, the quiet connective

Move 15 deserves special mention because it is the most-used and least-noticed. A title that
opens by pointing back at what the previous slide established is already bound to it:

> *This modularity extends to the UI, where federated micro-frontends allow teams to ship
> capabilities independently into a consistent shell.*

> *Inside these cells, multi-tenancy is secured at the platform layer via AWS IAM,
> preventing application-level data breaches.*

"This modularity" and "these cells" are doing the connective work. There is no conjunction,
and none is needed: the reference itself carries the link.

The weaker cousin is **lexical cohesion**, where a title simply reuses a meaningful noun from
the slide before without pointing at it. It binds, but loosely. A title with neither an
explicit connective, nor anaphora, nor a shared term is a true orphan, and
`scripts/spine-check.mjs` flags exactly that case.

### Choosing the move

The move is determined by the **relationship** between two adjacent slides, not by taste.
When the right move is unclear, the order is probably wrong. Reorder, then the connective
becomes obvious. That is the diagnostic value of the taxonomy: difficulty finding a
connective is a signal about structure, not about wording.

### Worked spine

A complete arc, with the move for each transition. Read the titles alone: it is one paragraph.

| Kicker | Title | Move |
|---|---|---|
| THE SITUATION | Despite clear repeating patterns across our solutions, we build or fork every use case from scratch. | opens |
| THE COMPLICATION | This bespoke engineering is exponentially compounded by the strict data governance required by our global client base. | escalation |
| THE CONSEQUENCE | Because both the application code and the infrastructure are bespoke, our cost to serve scales linearly with every client we win. | consequence |
| THE RESOLUTION | To break this cycle, we must transition to a composable platform, engineering reusable components and hosting them in standardized cells. | resolution |
| THE TWO DIMENSIONS OF REUSE | Every solution we deliver makes the next one cheaper: components compose into products, products serve many clients, and client work feeds the catalog. | taxonomy |
| DIMENSION ONE - COMPOSING PRODUCTS | Products are composed from the shared catalog, and bespoke components that generalize are promoted back into it. | mechanism |
| COMPONENT DESIGN | To make these components truly reusable, we use a hexagonal architecture that strictly isolates business logic from underlying infrastructure. | mechanism |
| THE ADAPTER PATTERN | For example, a connector handles data ingestion agnostically, meaning we can swap providers without rewriting the core application. | instantiation |
| FRONTEND MODULARITY | This modularity extends to the UI, where federated micro-frontends allow teams to ship capabilities independently into a consistent shell. | extension |
| SYSTEM INTEGRATION | Because these components communicate via standard events, we retain the flexibility to choreograph or orchestrate workflows as the problem demands. | causation |
| WORKED EXAMPLE | We already see this in Certainty, which natively decomposes into two distinct workflows powered by the same three underlying capabilities. | evidence |
| PLATFORMIZING CERTAINTY | By platformizing these capabilities, serving the next client becomes a simple matter of adding a datasource block. | implication |
| THE TWO-WAY DOOR | While optimizing for AWS provides speed, our adapter layer preserves the ability to easily deploy to private clouds when deals require it. | objection |
| MULTI-TENANCY ECONOMICS | Sharing capacity across tenants drives our infrastructure cost per client toward zero. | quantification |
| THE INVESTMENT | To unlock this compounding velocity across all our solutions, we require dedicated engineering capacity to build the foundational component layer. | ask |

---

## Title patterns

Reusable shapes. Each guarantees a subject, a verb, and a so what.

### Purpose then mechanism
> To **[achieve outcome]**, we **[do mechanism]**.

*To make these components truly reusable, we use a hexagonal architecture that strictly
isolates business logic from underlying infrastructure.*

The strongest general-purpose pattern, because the purpose clause is the so what and it
comes first.

### Cause then capability
> Because **[property]**, we **[gain capability]**.

*Because these components communicate via standard events, we retain the flexibility to
choreograph or orchestrate workflows as the problem demands.*

### Concession then claim
> While **[true thing that invites doubt]**, **[our answer]**.

*While optimizing for AWS provides speed, our adapter layer preserves the ability to easily
deploy to private clouds when deals require it.*

The objection-handling pattern. Naming the doubt out loud is what defuses it.

### Means then result
> By **[action]**, **[result]** becomes **[new state]**.

*By platformizing these capabilities, serving the next client becomes a simple matter of
adding a datasource block.*

### Colon expansion
> **[Claim]**: **[the three things that make it true]**.

*We deploy these self-contained artifacts into sovereign cells: one AWS account per region,
each running many products.*

Useful when a term needs defining in the same breath as the claim. At most one per section:
the colon is a strong rhythm and repetition flattens it.

### Falsifiable quantity
> **[Action]** drives **[metric]** toward **[limit]**.

*Sharing capacity across tenants drives our infrastructure cost per client toward zero.*

The strongest closing shape for an economics section, because it can be argued with, and a
claim that can be argued with is one the audience takes seriously.

---

## Anti-patterns

| Anti-pattern | Example | Fix |
|---|---|---|
| **Label as title** | `Cloud Strategy` | State the claim: "To maximize engineering velocity, we build on AWS primitives, leaving our teams focused purely on business logic." |
| **Fact with no so what** | `We use CDK for infrastructure.` | Add the purpose: "We package the required infrastructure alongside the application code using CDK, creating a single, portable artifact." |
| **Orphan** | `Multi-tenancy is secured via IAM.` after a slide about cost | Add the connective, or move the slide to where it belongs. |
| **Two ideas** | `We deploy into cells and multi-tenancy drives cost down.` | Two slides. This exact merge is a known source of audience confusion. |
| **Jargon-first** | `Federated micro-frontends enable independent deployability.` | Lead with the outcome: "This modularity extends to the UI, where teams ship capabilities independently into a consistent shell." |
| **Hedged** | `We could potentially consider moving toward composability.` | Commit: "To break this cycle, we must transition to a composable platform." |
| **Passive with no actor** | `It was decided that costs would be reduced.` | Name who: "We reduce cost to serve by..." |
| **Technology as outcome** | Title slide: `Serverless Multi-Tenant Platform` | Business outcome: `From Bespoke Services to Exponential SaaS`. |

---

## The title slide

The only slide with no connective, and the one that sets the frame. It carries three things:

| Element | Job | Example |
|---|---|---|
| Kicker | Name the body of work | `LABRYNTH PLATFORM STRATEGY` |
| Title | The transformation, as an outcome | `From Bespoke Services to Exponential SaaS` |
| Subtitle | The mechanism and the payoff, in one sentence | `Transitioning from building custom software per client to composing global, multi-tenant solutions, breaking the linear cost curve and unlocking compounding velocity.` |

The `From X to Y` shape is reliable for any change proposal: it states the current state, the
target state, and implicitly the whole reason the deck exists.

Executives care about the outcome of a technology, not the technology. `Serverless` and
`sovereign cells` belong in the body, where they are earned; putting them in the title asks
the audience to already believe the thing the deck is meant to prove.
