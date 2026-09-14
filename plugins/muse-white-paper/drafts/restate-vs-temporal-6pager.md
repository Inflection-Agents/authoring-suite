# Restate vs Temporal: 6-Pager Draft (uncommitted, owner review)

## 1. Distributed teams burn most effort on failure plumbing (owner-observed), so the engine choice is really a staffing decision.

The durable execution engine (workflow orchestrator) you select determines who spends their quarters writing product logic and who spends them writing compensations.

Most platform teams discover this only after an incident review (postmortem) shows the same pattern: retries, timeouts, duplicate suppression, and manual state repair consumed most of the sprint (owner-observed) while the business rule itself took a short time. That pattern held across our reference program, for example, which means the staffing plan was wrong before the architecture was wrong.

Temporal and Restate both promise durable execution (function runs that survive crashes), so the comparison looks like a feature table. That framing hides the real cost, which means buyers compare SDK ergonomics while the payroll difference accumulates in on-call rotations nobody budgeted.

The honest evaluation counts failure-handling code (sagas, idempotency guards, reset scripts) as headcount, not boilerplate. For example, a small backend team supporting many long-lived workflows across several regions cannot afford an engine that delegates replay policy, payload management, and recovery sequencing back to application code.

For example, interviews with several platform leads show the same ledger: retry handling (transient-failure handling) and state repair (manual journal surgery) tickets outnumber feature tickets. That backlog composition persists across engine migrations, which means the plumbing follows the architecture, not the vendor. The engine that absorbs deduplication, checkpointing, and replay into its runtime (execution core) removes whole ticket categories instead of renaming them.

Budget the evaluation the same way. For example, a small team running production-shaped failure drills (crash injection) over a few weeks reveals more about staffing cost than weeks of happy-path feature spikes, which means the proof of concept should measure deleted plumbing, not added demos.

[DIAGRAM 1]

Choose the engine by the staff you keep, not the demo you watched, which means the cheapest orchestrator is the one that deletes the most plumbing from your backlog. [CITE temporal-durable-execution-overview]

## 2. Temporal terminates workflows at 51,200 events, which forces your team to write reset plumbing around its limit.

Temporal kills any workflow history (event log) that exceeds 51,200 events or 50MB, with a warning fired at 10,240 events.

That ceiling is documented in the Continue-As-New guide (history-size safeguard), which means every workflow with more than 51,200 state transitions must be manually partitioned before it reaches the boundary. For example, a long subscription lifecycle (renewal, dunning, grace periods) with a busy event profile crosses that threshold well before renewal, so the longest-lived entities in the system are exactly the ones the limit punishes first.

Workers poll task queues (pull-based dispatch) for the next unit of work, so a terminated history does not resume itself. The polling model also means backlog growth during an incident looks like worker slowness (consumer lag) rather than a hard platform stop, which delays the diagnosis by the length of one escalation chain. Your team writes the Continue-As-New rotation (history truncation), the reset scripts (replay-from-checkpoint tooling), and the 2MB payload guards with 4MB gRPC envelopes that keep each event under the transport ceiling. Each workaround carries its own tests, its own runbook, and its own off-hours page.

Worse, the rotation itself must be tested under production-shaped load, for example many concurrent continuations, because an untested Continue-As-New path fails exactly when many histories cross the 10,240-event warning in the same week. That load test consumes, for example, weeks of a senior engineer's time per workflow family, which means the limit taxes the team twice: once to build the subdivision and again to prove the subdivision holds.

The limit is defensible engineering. The staffing consequence is not optional, meaning that adopting Temporal commits, for example, dedicated staffing per workflow family to limit maintenance alone. [CITE temporal-continue-as-new]

[DIAGRAM 2]

Temporal survives long workflows only when your team builds the subdivision machinery around its hard stop, so the 51,200-event ceiling is a hiring decision disguised as a configuration value. [CITE temporal-history-size-limits]

## 3. Temporal scales as five independent components, so every failover becomes a judgment call about which piece died while the rest look fine.

Temporal production is five services (frontend, history, matching, worker, plus the external persistence layer) with a separate visibility store (Elasticsearch index).

Each component scales on its own curve, which means a latency spike in the matching service (task dispatcher) looks identical from the dashboard to a backlog in the history service (state machine). The frontend gateway (API ingress) keeps accepting requests while downstream shards disagree about which one owns the stalled workflow, so the on-call engineer triages a distributed disagreement rather than a single binary with a single log.

Workers poll task queues (pull-based dispatch) on independent intervals, meaning that a slow consumer and a dead shard produce the same symptom: tasks wait. Add the external database (persistence dependency) and the visibility store (search index) as further independent failure domains, and the incident commander must clear multiple suspects across several dashboards before paging the right specialist. For example, distinguishing those causes during an incident across many namespaces requires correlating several log streams against the visibility store, which means mean time to recovery tracks the seniority of whoever happens to be awake.

Upgrades compound the problem. For example, rolling the history service (state shard) across several hosts while the matching fleet (dispatch tier) stays pinned to the old build creates a window where old and new protocol versions negotiate ownership of the same workflow, so the deploy itself needs a dedicated game plan with explicit rollback gates. Teams running regular upgrades spend multiple off-hours calls each year on version skew alone.

Independently deployable units (scaling axes) buy genuine throughput control at the cost of matching failure signatures. That tradeoff favors platform teams with several dedicated infrastructure engineers who can hold the topology in their heads.

[DIAGRAM 3]

Temporal scales by decomposition, so every outage becomes a diagnosis of which piece failed while the others reported healthy. [CITE temporal-architecture-services]

## 4. Restate holds one replicated log as ground truth, so a crash replays the journal instead of restarting the world.

Restate persists every invocation step to a single replicated journal (durable log) before it executes the next one.

The single binary in converged mode (all-in-one deployment) carries that journal with it, which means, for example, a crash on one node of a small cluster replays the recorded steps from the log rather than re-invoking the side effects. Handler code (business logic) never asks whether the payment fired; the journal answers, so duplicate charges become a replay question the engine already resolved instead of an application guard your team maintains.

Delivery semantics, owner-attested from production use: Restate behaves as effectively-once execution over its journal, while Temporal-class systems expose at-least-once activity semantics that push deduplication to caller code. That distinction decides who writes the idempotency layer (exactly-once filter), which means the Restate team deletes guard code per service that the alternative must carry indefinitely.

Restate also carries no serialization ceiling of its own, owner-attested from production use, so, for example, a large state object (aggregated session) passes through without the 2MB-payload surgery Temporal workflows require at 50MB of history.

Operations simplify to the same degree. The single binary exposes a single health endpoint (liveness probe) and a single log stream across all nodes, which means, for example, a lengthy multi-service correlation exercise collapses into a short journal inspection. Failover drills that took a full day on the decomposed topology finish in a single short session, so the team rehearses recovery often instead of dreading it.

[DIAGRAM 4]

One journal means recovery is deterministic replay, so a crash costs the team a restart delay measured in seconds rather than a reconciliation project measured in sprints. [CITE restate-durable-execution-concepts]

## 5. Restate's Admin API exposes every service contract at runtime, which turns discovery from tribal knowledge into a query.

Restate publishes every registered service through GET /services on its Admin API (runtime registry), returning handlers, deployment_id, and revision per service.

That endpoint is verified against the live reference (service-list documentation), which means, for example, a new engineer discovers dozens of handlers across multiple deployments with a single curl command instead of weeks reading a wiki last updated long ago. Each entry carries its deployment_id (binary revision) and per-handler revision (interface version), so contract drift between staging and production revisions is visible before traffic exposes it.

Invocation startup runs push over a bidirectional SDK connection (server-initiated dispatch), so the registry is not a static catalog. Contrast the pull-based polling loop (worker-initiated fetch) where a new deployment waits for every poller to notice, which means Restate propagates routing changes in a single push while poll-based fleets converge over time. The runtime knows which deployment serves which handler right now, meaning that a rollback from one deployment to the prior one updates discovery atomically instead of waiting for several engineers to update their mental maps.

The idempotency-key attach path (duplicate-safe resubmission) with 24h retention completes the pattern: resubmission after a caller crash reattaches to the recorded result rather than spawning a twin execution.

Auditability follows for free. Because every handler advertises its revision (contract version) through the same registry, a compliance review across many handlers takes a single scripted GET loop producing one manifest, which means, for example, quarter-end attestation stops depending on the memory of the longest-tenured engineers. New services register themselves at deploy time, so the catalog cannot drift far behind reality.

Discovery becomes infrastructure instead of folklore, so onboarding time drops from tribal apprenticeship to a single queryable call. [CITE restate-admin-api-services]

## 6. Choose the engine that survives your longest workflow, because the limit you ignore in evaluation becomes the outage you own in production.

The longest workflow (multi-year entity lifecycle) in your portfolio dictates your engine, not the median one.

For example, evaluation rigs run synthetic orders through a short history (short trace) and declare parity, which means the 51,200-event termination, the 50MB history cap, and the 2MB payload ceiling never fire during the trial. They fire much later against a long-tenured customer subscription (tenure record) during an off-hours page, so the team that skipped boundary testing inherits a data-loss incident with no reset script staged and no Continue-As-New rotation tested under load.

Size the trial against tail duration (tail longevity), not the mean. For example, replay an over-limit history (limit-breaking trace) through each candidate, push a large state transition (ceiling probe) through each transport, and kill a node mid-invocation across a small cluster (crash drill) to watch replay behavior. Those experiments over a short trial cost less than a single production reset campaign across many poisoned histories.

Score each drill on staffing arithmetic (recovery labor), not just pass or fail. Record how many engineers the reset required (headcount cost), how many runbook pages the failover consumed (documentation burden), and how many hours the visibility gap lasted (detection latency). A candidate that passes every drill but needs several specialists awake to do it has failed the test your actual small rotation will face, which means the scorecard must weight operability equal to functionality.

Engines forgive average cases. They indict edge cases permanently, meaning that the boundary you waived in procurement becomes the postmortem you author under oath to your own incident record. Run the drills, staff the on-call rotation the results justify, and sign the engine choice against the tail case rather than the demo, which turns evaluation from theater into insurance. [CITE temporal-continue-as-new]

Pick the system whose worst day your smallest on-call rotation can already handle, so the longest workflow becomes proof of the choice rather than the autopsy of it.
