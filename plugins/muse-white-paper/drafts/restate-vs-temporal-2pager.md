> SUPERSEDED by the v2 drafts on the audience-first spine. Kept for history only.

# Restate vs Temporal: 2-Pager Draft (derived, uncommitted)

## 1. Distributed teams burn most effort on failure plumbing (owner-observed), so the engine choice is really a staffing decision.

The engine choice sets staffing before architecture. Postmortems (incident reviews) show retries, timeouts, duplicate suppression, and manual state repair (owner-observed) consumed most of the sprint while the business rule took a short time, which means staffing failed before architecture did.

Count failure-handling code (sagas, idempotency guards, reset scripts) as headcount, which means a small team running many long-lived workflows across several regions cannot fund an engine that returns recovery sequencing to application code.

Run failure drills (crash injection) over a few weeks and score deleted plumbing, which means the cheapest orchestrator deletes the most backlog. [CITE temporal-durable-execution-overview]

## 2. Temporal terminates workflows at 51,200 events, which forces your team to write reset plumbing around its limit.

Temporal ends any workflow history (event log) past 51,200 events or 50MB, with a warning at 10,240 events. A long subscription lifecycle (renewal, dunning, grace periods) crosses the threshold before renewal, so the longest-lived entities take the hit first.

Your team writes the Continue-As-New rotation (history truncation), the reset scripts (replay-from-checkpoint tooling), and the 2MB payload guards with 4MB gRPC envelopes, which means each workaround carries its own tests and runbook.

[DIAGRAM 2]

Temporal survives long workflows only when your team builds subdivision machinery around its hard stop, so the 51,200-event ceiling is a hiring decision disguised as a configuration value. [CITE temporal-continue-as-new] [CITE temporal-history-size-limits]

## 3. Temporal scales as five independent components, so every failover becomes a judgment call about which piece died while the rest look fine.

Each component scales on its own curve, which means a latency spike in the matching service (task dispatcher) looks identical to a backlog in the history service (state machine).

Workers poll on independent intervals (pull-based dispatch), which means a slow consumer and a dead shard produce the same symptom: tasks wait.

Rolling the history service (state shard) while the matching fleet (dispatch tier) stays pinned creates version-skew windows, so each deploy needs explicit rollback gates, which means the tradeoff favors teams with several dedicated infrastructure engineers. [CITE temporal-architecture-services]

## 4. Restate holds one replicated log as ground truth, so a crash replays the journal instead of restarting the world.

Restate persists every invocation step to a single replicated journal (durable log) before executing the next one. The single binary in converged mode (all-in-one deployment) carries that journal, which means a crash on one node of a small cluster replays recorded steps rather than re-invoking side effects.

Delivery semantics, owner-attested from production use: Restate behaves as effectively-once execution over its journal, while Temporal-class systems expose at-least-once activity semantics that push deduplication to caller code. Restate carries no serialization ceiling of its own, owner-attested from production use, so a large state object (aggregated session) passes through without the 2MB-payload surgery Temporal requires at 50MB of history.

[DIAGRAM 4]

One journal means recovery is deterministic replay, so a crash costs seconds of restart delay rather than sprints of reconciliation. [CITE restate-durable-execution-concepts]

## 5. Restate's Admin API exposes every service contract at runtime, which turns discovery from tribal knowledge into a query.

Restate publishes every registered service through GET /services on its Admin API (runtime registry), returning handlers, deployment_id, and revision per service. That endpoint is verified against the live reference (service-list documentation), which means a new engineer discovers dozens of handlers with a single curl command instead of weeks reading a stale wiki.

Startup pushes over a bidirectional SDK connection (server-initiated dispatch), so routing changes propagate in one push while pull-based polling loops (worker-initiated fetch) converge over time. The idempotency-key attach path (duplicate-safe resubmission) with 24h retention reattaches a caller crash to its recorded result, which means no twin workflow spawns.

Discovery becomes infrastructure instead of folklore, so onboarding drops to a single queryable call. [CITE restate-admin-api-services]

## 6. Choose the engine that survives your longest workflow, because the limit you ignore in evaluation becomes the outage you own in production.

The longest workflow (multi-year entity lifecycle) in your portfolio dictates the engine, which means the median workflow tells you nothing. The boundary fires later against a long-tenured subscription (tenure record) during an off-hours page, which means the team that skipped boundary testing inherits the incident with no reset script staged.

Size the trial against tail duration (tail longevity). Replay an over-limit history (limit-breaking trace), push a large state transition (ceiling probe), and kill a node mid-invocation across a small cluster (crash drill) to watch replay behavior, which means a short trial costs less than one reset campaign across many poisoned histories.

Pick the system whose worst day your smallest on-call rotation can already handle, so the longest workflow proves the choice rather than becoming its autopsy. [CITE temporal-continue-as-new]
