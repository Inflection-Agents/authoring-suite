# 02 Interview

**Goal.** Ask the owner everything that blocks drawing, until you can name every container, every integration and
every piece of vocabulary without guessing.
**Produces.** The owner's answers, held in the conversation and in the ledger's open-items list, plus the diagram
plan table that closes the phase. No file of record yet; [04](04-facts-file.md) writes that.
**Gate.** No question is left that would change a page.

Enter this phase after the owner has corrected the playback in [01](01-kickoff.md). Re-enter it whenever a new area
of the system opens up mid-set.

The question bank below is what actually had to be asked to draw a platform architecture set. Work through it rather
than rediscovering the list. Skip anything the owner's earlier answers already cover.

## How to run the interview

- **Number the questions** so the owner can answer `1. …` `2. …` inline.
- **Batch them**, roughly ten to fifteen at a time, grouped by area.
- **Name the diagram consequence in each question**, in one clause, so the owner can say when a question does not
  matter. "Is the configuration multi-tenant, one policy per institution per product? If so the institution goes on
  the context diagram, and that would explain why the configuration grew this large."
- **Follow up immediately** when an answer opens a new area, rather than saving the follow-ups for a later batch.
- **Mark every "I don't know" and every "exclude it" as an open item.** Those are drawn as open or left out, never
  guessed, and they carry through to the open-items section of the facts file.
- **Write nothing else yet.** Do not start the facts file and do not propose diagrams until the owner says the
  interview is done.

## The question bank

**Actors and boundary**
- Who uses the system, in role terms, and which roles matter for the diagrams as distinct from each other?
- Which external organisations and vendors sit outside the boundary?
- Which of those are so numerous that they should collapse into one box?

**Containers**
- What are the deployable services, stores, queues and UIs, with the name each one is called internally?
- Which ones are so central that the reader needs a component-level diagram for them?
- Which are peripheral but must appear because they carry a surprise?

**Configuration**
- Where does configuration live, in what format, and who writes it?
- Does a service look configuration up, or is it passed in?
- Is there more than one configuration mechanism, and does anything hold configuration locally as well?
- Is configuration versioned, validated against a schema, or neither?
- How does a configuration change reach a running service?

**Contracts and payloads**
- Do services exchange typed contracts or generic payloads?
- Where does transformation happen, and who owns the mapping?
- How many grammars, DSLs or rule languages are in play?

**Synchrony and transport**
- Which calls are synchronous, which are asynchronous, and which are events?
- For each asynchronous path: poll, callback, or event, and who retries?
- Are events consumed, and by whom? Name any event that is published and never read.
- What pushes to a browser?

**State**
- Where does the state of a unit of work live, and what outlives the workflow?
- What is keyed by what? Get the key shape.
- Which store is the source for reporting and analytics?

**Behaviour that changes by caller or tenant**
- Does any component behave differently depending on who calls it or which tenant it serves?
- What is shared between tenants and what is duplicated per tenant?

**Failure and operations**
- What happens on timeout, on a vendor no-hit, and on a terminal failure?
- Where is the locking, and what is it protecting?
- Who is paged, and what do they look at first?

**The pain**
- Which change takes longest today, and what makes it slow?
- What has to be aligned before a single feature can be tested end to end? Name each artifact.
- Which of these does the owner want the set to argue, and which is context?

**Output**
- The owner's brand or the client's? Going into a document, or onto 16:9 slides?

**Proposal specific, if the set includes one**
- What is the design goal in one sentence per goal, ranked?
- Which components stay, which are replaced, and which are new?
- What is the rollout, and what is the first thing that delivers value?
- What is explicitly deferred or not yet designed?

## How the interview ends

Close with one message containing three things, then stop.

1. **The diagram plan as a table**: number, C4 level, visual type, what it shows, where the accent goes. This is a
   first cut that [05](05-diagram-list.md) expands into a paragraph per diagram.
2. **What the budget will force out**, named per diagram. "Diagram 2: the limit is 9 boxes, so I plan to leave the
   people out and show them on the context diagram only."
3. **One gate sentence**: ask for corrections on the open disagreements and any diagrams to add or drop, and say
   that once the owner says go, the set gets generated.

Where the engagement has source code, an analysis or older design documents, the next phase is
[03](03-source-reconciliation.md), not the facts file.
