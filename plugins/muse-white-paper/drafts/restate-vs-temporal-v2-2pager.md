# Restate vs Temporal: what the next size costs (v2)

Audience: teams running Temporal today and comfortable with it. This paper asks what each engine charges when workflows get longer and releases keep shipping.

## 1. Your team runs Temporal comfortably, and the workflows keep getting longer.

Temporal runs your current workload. The bill arrives when workflows double in length and a release ships mid-flight, which means this paper reads as a bill, not a review.

Workers poll task queues (a pull loop each worker owns). The cluster splits duty across four named services (frontend, history, matching, worker). State lands in an external database with a separate visibility store beside it. Short histories never feel the price. Runs that live for months pay it on every append, load, and replicate pass through the persistence backend, which means length is the tax base the rest of this paper measures [CITE temporal-scaling-guide].

## 2. Every release that must not break a running workflow ships version branches inside the workflow code, so the code carries its own release history.

Workflow code outlives the deploy that wrote it, which means March code still governs a March workflow after the June release. Temporal names the obligation determinism (workflow code must replay the same path). The patching API (getVersion and its patch markers) carries the cost first.

Temporal's worker versioning post says patching "adds clutter to your Workflow source files over time" [CITE temporal-worker-versioning]. Markers stay because some old execution may still replay them. Build IDs and version sets (infra-level versioning assigned at deployment) move the next decision onto the fleet. They leave committed markers in place, which means a reviewer reconstructs one generation per marker before judging the next change.

## 3. The shard count that sets your scale cannot change without a database reset, which means growth replays a migration, not a config edit.

History is sharded (partitioned across a fixed shard count set at cluster creation; most teams meet 512 shards first). The count fixes how history ownership spreads. Changing it requires a database reset [CITE temporal-shard-config], which means export, rebuild, and reimport with a runbook and rollback page.

Traffic doubles and the persistence backend becomes the bottleneck [CITE temporal-scaling-guide]. The team wants one edited field. The engine requires a weekend.

[DIAGRAM 2]

A count chosen when histories were short governs a fleet whose histories are now long. The number cannot learn, which means growth arrives as a migration with a freeze window.

## 4. Continue-As-New keeps long workflows alive by making your team hand-partition what the engine cannot hold.

Histories end at 51,200 events or 50 MB per execution, with a warning at 10,240 events or 10 MB [CITE temporal-continue-as-new]. Payloads add walls at 2 MB per payload and 4 MB per gRPC message [CITE temporal-payload-limits]. Long workflows reach these limits by succeeding.

Continue-As-New (the API that closes one execution and starts a successor with fresh history) is the documented answer. Your team picks the cut point, writes the state-carry code, and debugs the chain. Signals must find the live successor. Queries must span links the engine stores as separate executions. Both patterns are solvable. Both are yours, which means longevity ships as application code the team owns.

## 5. Restate pushes work to versioned deployments, so a new release drains the old one instead of branching inside your workflow code.

Restate pushes work to registered deployments over a bidirectional SDK connection (a persistent channel the SDK opens to the runtime) [CITE restate-runtime]. Registration is explicit: a GET /services call on the Admin API returns each service with its handlers, deployment_id, and revision [CITE restate-admin-api].

A new deployment registers under a new deployment_id. In-flight invocations finish on the old revision. New invocations route to the new one, which means the release history lives in the deployment list rather than in branches inside the workflow file. The package matches: a single binary in converged mode (runtime, metadata store, and user-space services colocated for small setups) [CITE restate-converged-mode]. Rollback routes new invocations back to the registered old deployment.

[DIAGRAM 4]

Restate's lack of serialization limits is owner-attested from production use, not publicly sourced. Treat it as a field report the trial can confirm or refute.

## 6. Run one long-lived workflow on both engines past one release, and let the version diff decide.

Port the workflow that already hurts. It runs for months, carries real state, and survives one release mid-flight. Run both copies against the same load for one quarter.

Score four named measures. First, the version diff: branches added per release against deployment entries added. Second, history size: event counts toward the 10,240 warning and the 51,200 cap [CITE temporal-continue-as-new]. Third, release labor: hours on markers, version sets, continuation boundaries, and shard review. Fourth, recovery: time to resume after a mid-run worker kill. Idempotency-key attach (a client-supplied key Restate holds for 24 hours so retries rejoin the original invocation) [CITE restate-idempotency] covers duplicate submits. Exactly-once delivery in Restate is owner-attested from production use, stated here under that label until the trial confirms it. Fund the smaller diff.
