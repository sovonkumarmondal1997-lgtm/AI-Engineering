# Replication, Consistency and Transaction Boundaries

> **Stage:** 2D — Data Architecture  
> **Module:** 05 — Database and Storage Architecture  
> **Topic:** 6 of 7  
> **Scope:** Vendor-neutral architectural reasoning. This lesson derives correctness, replication and transaction decisions from business requirements; it is not a product-specific administration guide.

---

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Define replication, redundancy, replica lag, consistency, transaction, atomicity, isolation, durability, idempotency, reconciliation, Recovery Point Objective (RPO), and Recovery Time Objective (RTO).
2. Distinguish replication from backup, synchronization between separate systems, and an end-to-end consistency guarantee.
3. Compare synchronous and asynchronous replication for latency, availability, acknowledged-write loss exposure, and recovery without claiming that one mode is universally superior.
4. Translate business requirements into explicit rules about read freshness, ordering, atomic updates, acceptable staleness, and data loss.
5. Separate guarantees provided by a store and its configuration from architectural assumptions and application-level mechanisms.
6. Explain replica lag, stale reads, read-after-write behavior, failover, split-brain risk, and reconciliation after recovery.
7. Define a lag budget and explain when lag is—and is not—a useful proxy for potential data loss or RPO.
8. Identify transaction boundaries inside one store and across independently operated systems.
9. Analyze the database-plus-event dual-write problem and design an outbox-style flow or justified alternative.
10. Use idempotent consumers, retries, deduplication, ordering rules, compensating actions, and reconciliation to make cross-system workflows recoverable.
11. Analyze failures before commit, after commit but before publication, duplicate delivery, consumer failure, delayed/reordered events, and replay.
12. Produce an operation-to-consistency table, replication topology/lag budget, and cross-system failure analysis for a fictional banking workload.

**Core rule:** every consistency guarantee must be tied to a business invariant, a specific system guarantee or mechanism, explicit assumptions, and a defined response when the guarantee cannot be met.

---

## 2. Why the topic matters in real-world data architecture

Imagine a customer transfers money between two accounts. The ledger may record the transfer correctly, but the customer's balance screen might read from a replica that has not yet applied the update. A downstream risk service might never receive the event if the application crashes after committing the ledger row but before publishing the message. A failover might promote a replica that is behind the previous primary. These are not merely infrastructure issues: they can affect customer trust, regulatory evidence, duplicate actions, and financial correctness.

Replication and consistency are architectural decisions because they determine:
- which copies exist and why;
- which copy is authoritative;
- what a successful write means;
- what readers may observe after a write;
- what happens when nodes or network paths fail;
- how much acknowledged data might be lost in a failure;
- how quickly service is expected to recover;
- which operations succeed or fail together;
- how separate systems recover from partial completion.

A design that says only “we have three replicas” is incomplete. It does not establish that a committed write reached those replicas, that a failover selects the latest safe copy, that a deleted record can be recovered, or that a database update and a published event are atomic together.

### 2.1 Essential distinctions

| Concept | Meaning | What it does **not** mean |
|---|---|---|
| **Replication** | Maintaining copies of data across nodes, processes, regions, or systems | A backup, or proof that separate systems are synchronized |
| **Backup** | A recoverable copy or recovery point designed to restore data after loss, corruption, or operator error | A continuously current replica |
| **Synchronization/integration** | Moving or reconciling state between distinct systems under defined rules | Automatic atomicity across those systems |
| **Consistency guarantee** | A rule about which states a read may observe relative to writes | A generic synonym for “the data looks correct” |
| **Transaction** | A defined unit of work with specified atomicity/isolation/durability behavior | A guarantee that unrelated services participate in the same commit |
| **Idempotency** | Repeating an operation has the same intended effect as applying it once, within a defined scope | Proof that a message was delivered only once |
| **Reconciliation** | Comparing systems or records against an invariant/source of truth and repairing discrepancies | A substitute for preventing all failures |
| **RPO** | The maximum tolerable data-loss window expressed as a recovery objective | A promise that observed lag never exceeds that window |
| **RTO** | The target maximum time to restore an acceptable service after disruption | A guarantee that failover always completes within that time |

Replication can improve availability, read scale, locality, or durability against particular failures. It can also copy corruption, accidental deletion, or an unwanted update. Backups and tested restore procedures remain separate controls.

### 2.2 Start from business consequences

Do not begin by asking “Should replication be synchronous?” Start with questions such as:
- Can a customer ever see a balance older than their own successful payment?
- Can two transfers spend the same available funds?
- Can a risk alert arrive late, and if so, how late?
- Can a downstream analytics table temporarily lag behind the ledger?
- If a primary fails, how much acknowledged data may be lost?
- How long can the payment service remain unavailable?
- Can an event be delivered more than once?
- What is the required response if a downstream system misses an event?

Different data classes may have different answers. A ledger posting, a search index, a customer activity feed, and a daily analytical aggregate should not automatically receive the same consistency contract.

---

## 3. Prerequisite knowledge

This topic builds on the following roadmap material.

| Prerequisite | Required understanding | Use in this lesson |
|---|---|---|
| Topic 1 — OLTP/OLAP separation | Operational versus analytical workloads, systems of record, read replicas and analytical copies | Determine which reads require strong freshness and which can tolerate lag |
| Topic 2 — Database category selection | Access patterns, transaction support, store limitations, operational trade-offs | Choose only among systems whose guarantees fit the invariant |
| 2D.2 Topic 4 — Latency, throughput, freshness and availability targets | Define measurable service objectives | Set lag budgets, RPO/RTO targets and acceptable unavailability |
| 2D.3 Topic 6 — Event-driven and data-sharing patterns | Event producers/consumers, asynchronous delivery, event ordering and delivery semantics | Analyze publication, retries, duplicate events and recovery/replay |
| 2D.4 Topic 6 — Event modeling and domain-driven design | Aggregate boundaries, invariants and ownership | Decide which business changes must be atomic within one store |
| Topic 5 — Partitioning, indexing, clustering and layout | Physical data layout and hot keys | Recognize write hotspots and understand that layout cannot itself guarantee consistency |

### 3.1 Prerequisite check

Before designing replication, write down:
1. the system of record for each entity;
2. the business invariant that must remain true;
3. the operations that must be atomic together;
4. the reads that may be stale and the reads that may not;
5. the tolerated data-loss and recovery windows;
6. the consumers that need events and how they detect duplicates;
7. how correctness will be checked after recovery.

If these are unknown, the design is not ready to select a replication mode or transaction mechanism.

---

## 4. Beginner-level learning sequence

### 4.1 Replication and redundancy

**Replication** means maintaining copies of data. **Redundancy** means having additional components or copies so a failure does not necessarily destroy all capability or data. A replica may be used for:
- failover when a primary becomes unavailable;
- read scaling;
- geographic locality;
- durability across a defined failure domain;
- serving a derived workload such as search or analytics.

A replica only protects against the failure classes and timing conditions covered by its design. Two copies in the same failure domain may both be lost in a larger incident. A replica can also reproduce a bad write or deletion. A backup with independent retention and restore controls addresses a different recovery problem.

### 4.2 Synchronous and asynchronous replication

These labels describe when replication acknowledgement is required relative to the source write. The exact protocol varies by system and configuration; the table is conceptual.

| Dimension | Synchronous-style acknowledgement | Asynchronous-style acknowledgement |
|---|---|---|
| Write acknowledgement | The write waits for confirmation from the required replica/replication participants according to the configured protocol | The source may acknowledge after its local commit while replica application continues |
| Write latency | Includes the required replication acknowledgement path | Can be lower because the client need not wait for all replica application |
| Failure behavior | If required participants cannot acknowledge, the write may block or fail; availability can decrease | The source may continue while replicas lag, but a source failure can expose missing acknowledged writes |
| Acknowledged-write loss | May be prevented for specified failures if the protocol and failover rules ensure the acknowledged copy survives; not an unconditional universal guarantee | Possible if the only surviving/promoted copy has not received the acknowledged write |
| Read freshness | Depends on the read path and consistency guarantees, not just the replication label | Replica reads may be stale until changes are applied |
| Operations | Needs correct quorum/acknowledgement and failover configuration | Needs lag monitoring, promotion rules, loss assessment and reconciliation |

**Do not oversimplify:** “synchronous means no data loss” is only valid within a stated guarantee and failure model. It depends on which acknowledgements are required, durable persistence, replica placement, promotion rules, and the failure being considered. Similarly, asynchronous replication does not always lose data; it creates an exposure when the source fails before changes reach the surviving copy.

Neither mode is universally superior. Synchronous acknowledgement may be appropriate for critical writes when its latency and availability trade-off is acceptable. Asynchronous replication may be appropriate for read scaling or derived copies where lag is acceptable and recovery procedures cover possible loss.

### 4.3 Transactions and ACID properties

A **transaction** is a bounded unit of work. In relational systems, ACID describes four properties, though the exact isolation and durability guarantees must be checked for the selected system and configuration.

- **Atomicity:** all changes in the transaction take effect, or none do.
- **Consistency:** the transaction preserves defined constraints/invariants; this does not mean every distributed copy is instantly identical.
- **Isolation:** concurrent transactions are prevented from observing/interleaving changes in ways forbidden by the selected isolation level.
- **Durability:** once committed according to the system's contract, the change survives the failures covered by that contract.

Example: a transfer may require two ledger entries and a transfer record to commit together. If only one side commits, the ledger invariant is broken. The required transaction boundary should include all changes that must be atomic and are supported within that store's transaction model.

### 4.4 Consistency in business language

Consistency is not one single property. Write down the read rule that matters.

| Read behavior | Plain-language meaning | Example |
|---|---|---|
| **Strong/linearizable read** | A read behaves as if it occurred at one point in a single order consistent with real-time completed operations, under the system's stated guarantee | A balance read must reflect a completed posting that happened before the read began |
| **Read-your-writes** | A client that completed a write can subsequently read a state that includes that write | A customer sees their own payment after the service reports success |
| **Monotonic reads** | A client does not move backward to an older state across successive reads | A session should not show a newer balance and then an older one |
| **Sequential consistency** | Operations appear in a single order that respects each participant's program order, but not necessarily real-time order across participants | Useful as a concept for reasoning about ordered operations; actual support varies |
| **Eventual consistency** | If updates stop and propagation succeeds, replicas are expected eventually to converge | A reporting dashboard catches up after a delay |
| **Bounded staleness** | A system or application contract limits how old a read may be, within a specified definition and assumptions | An activity feed may tolerate a delay of a few seconds if measured and enforced |

These are conceptual categories, not claims that every database implements all of them. A system may offer different consistency options per operation, transaction, replica, or configuration. Always verify the actual contract.

### 4.5 Replica lag

**Replica lag** is the delay between a change becoming committed at the source and becoming visible/applied at a replica, measured using a clearly defined timestamp or position.

A conceptual time-based definition is:

```text
lag = replica_apply_time − source_commit_time
```

This requires comparable clocks or a reliable system-provided lag measure. Some systems report lag in log positions, sequence numbers, or queue offsets rather than wall-clock time. Do not compare timestamps from unsynchronized clocks and treat the result as precise.

Lag can cause:
- stale reads;
- a user not seeing their own write;
- different consumers observing different states;
- delayed risk alerts or analytical metrics;
- a failover candidate missing recent source commits;
- additional reconciliation after recovery.

Lag is not the same as a data-loss guarantee. Observed lag is a measurement of what happened; a contractual maximum is a guarantee only if the system and operating conditions actually provide one.

### 4.6 RPO and RTO

- **Recovery Point Objective (RPO):** the maximum tolerable amount of data loss, often expressed as time between the latest recoverable point and the disruption.
- **Recovery Time Objective (RTO):** the target maximum time to restore the service to an acceptable operating state.

Example (illustrative): a risk dashboard may have an RPO of 5 minutes and RTO of 60 minutes, while a financial ledger may require a much stricter data-loss objective. These are not universal targets; business owners, compliance requirements, and system feasibility determine them.

RPO and RTO are separate:
- A service may recover quickly but lose recent writes.
- A service may preserve all committed data but take a long time to restore service.

### 4.7 Replication is not synchronization, and neither is end-to-end consistency

A database replica is a copy maintained under a database's replication mechanism. A separate search index, event stream, cache, and analytics table are distinct systems that need integration rules.

Moving data between distinct systems involves:
- a source of truth and ownership;
- a delivery mechanism;
- ordering and duplicate handling;
- schema and semantic compatibility;
- lag/freshness expectations;
- retries, replay, reconciliation, and failure response.

A transaction committed in one system does not automatically commit a corresponding record in another system. A “replicated” architecture therefore needs an explicit cross-system consistency design.

### 4.8 Beginner exercise: three failure cases

For each scenario, explain what may be lost, delayed, stale, unavailable, or duplicated.

1. A primary node fails while a synchronous replication protocol is waiting for a required acknowledgement.
2. A primary node fails after acknowledging a write locally but before an asynchronous replica applies it.
3. A replica is healthy but behind; a customer reads from it immediately after a successful write.

**Answer guidance**
- For case 1, writes may be blocked or fail if required participants are unavailable. The result depends on the protocol and its failure rules.
- For case 2, if failover promotes a copy missing the acknowledged write, that write may be lost from the active history; determine whether another durable log/copy can recover it.
- For case 3, the data may still exist at the source but the replica read can be stale. Route the read to a sufficiently fresh/authoritative path or use a supported read-your-writes mechanism.

---

## 5. Intermediate-level learning sequence

### 5.1 Replication topologies

| Topology | Concept | Potential strengths | Main risks/questions |
|---|---|---|---|
| Single primary with replicas | One write authority; replicas receive changes | Clear write ownership; read scaling and failover options | Replica lag, promotion safety, read staleness |
| Multi-primary | Multiple nodes can accept writes | Local write availability and geographic distribution in some designs | Concurrent conflict resolution, ordering, write-write conflicts, split-brain protection |
| Leaderless/quorum-based | Reads/writes coordinate with a subset of replicas | Can tolerate some node failures while serving operations | Quorum semantics, version/conflict resolution, repair, stale reads under some configurations |
| Source plus derived copies | Source database feeds cache, search, analytics, or another service | Workload-specific serving and decoupling | Cross-system lag, duplicate/missing events, reconciliation and ownership |

A topology name does not establish a consistency guarantee. The implementation's protocol, quorum/acknowledgement rules, conflict handling, and failover behavior matter.

### 5.2 Operation-to-consistency requirements

Use this table as a design artifact. The values below are **illustrative**; actual values must be agreed with the business and verified against the chosen system.

| Business operation | Required guarantee | Acceptable staleness/loss | Candidate mechanism | Assumptions to verify | Failure response |
|---|---|---|---|---|---|
| Post a ledger transfer | Debit and credit entries preserve the transfer invariant atomically | No partial transfer; acknowledged data-loss objective must be explicitly set by the bank | One local transaction in the ledger; replication protocol matched to RPO | Both entries are in one supported transaction boundary; durability/failover contract covers chosen failure model | Reject/roll back incomplete transaction; fail closed if invariant cannot be guaranteed; recover and reconcile |
| Read balance immediately after a successful transfer | Read includes that transfer (read-your-writes or stronger as required) | No stale result for the initiating session | Read from authoritative/strongly consistent path or supported session consistency token | Routing actually honors the guarantee; failover semantics preserve it | Route to authoritative path, wait within a bounded policy, or return a clear temporary-unavailable response |
| Display recent activity feed | Eventual or bounded staleness may be acceptable | Illustrative maximum delay: 10 seconds; no silent permanent omission | Asynchronous event stream, consumer checkpoint, idempotent projection | The 10-second budget is a business assumption and can be monitored; delivery/replay is configured | Alert on lag; replay; reconcile against source |
| Daily finance reconciliation | Complete and internally consistent as-of a declared cutoff | Delay until batch window; missing records not acceptable at sign-off | Consistent source snapshot or controlled extraction plus completeness checks | Cutoff and late-arrival policy are explicit | Mark run incomplete; retry/reconcile; do not publish final totals prematurely |
| Fraud/risk alert | Freshness requirement derived from fraud-loss tolerance | Illustrative maximum 2 seconds; alert may be duplicated but not silently lost | Durable event publication, consumer idempotency, lag monitoring, replay | Event source and detection latency are measured; duplicate handling preserves semantics | Retry/replay; alert on lag; reconcile gaps and apply compensating action if needed |
| Search customer profile | Bounded stale profile may be acceptable | Illustrative maximum 60 seconds; authoritative changes remain in source | Asynchronous projection into search index | Search is not the system of record; lag is visible to clients/operations | Rebuild or replay index; route critical reads to source |
| Customer list/dashboard | Eventual consistency may be acceptable | Illustrative staleness 5 minutes | Asynchronous replica or analytical copy | Users do not use it for payment authorization or other critical decisions | Show freshness timestamp; alert/rebuild if lag exceeds budget |
| Publish payment-confirmed event | Event must not be permanently lost after the ledger commits | Duplicate delivery allowed if consumers are idempotent; ordering rule defined per account/transfer | Transactional outbox or an equivalent atomic publication mechanism | Outbox insert is in the same local transaction as the business update; relay retries durably | Retry relay; deduplicate consumers; reconcile committed payments against emitted events |
| External payment-provider call | Local DB and provider may not share a transaction | Duplicate requests must not create duplicate payments where provider supports idempotency; otherwise uncertainty is handled explicitly | Durable workflow, provider idempotency key where supported, state machine and reconciliation | Provider's idempotency scope/retention and queryability are confirmed | Mark outcome unknown, query provider, retry safely or escalate; compensate if supported |

This table deliberately distinguishes:
- **required guarantee** (business meaning);
- **candidate mechanism** (how it might be implemented);
- **assumptions** (must be verified);
- **failure response** (what the service does when normal progress fails).

### 5.3 Derive a lag budget

A **lag budget** is the maximum tolerated delay between source state and a replica or derived consumer for a specific data class/use case. It should be derived from the business consequence of stale data, not copied from an infrastructure dashboard.

A useful design record includes:
- source commit or event time definition;
- replica apply/consumer processing definition;
- measurement method and clock/offset assumptions;
- normal operating target;
- alert threshold;
- maximum tolerated lag before a consumer is considered unsafe;
- action at threshold: route reads, pause processing, degrade service, or escalate;
- recovery and reconciliation method.

#### Illustrative lag-budget example

Assume (illustrative only):
- A customer activity feed can tolerate up to 10 seconds of lag.
- A metric reports a 2-second current lag.
- The service alerts when lag exceeds 5 seconds and stops claiming “up to date” after 10 seconds.
- A recovery test observes a peak lag of 8 seconds during a load burst.

Interpretation:
- The 2-second observation is one measurement, not a guarantee.
- The 8-second observed peak is below the stated 10-second tolerance in that test, but it does not prove future worst-case lag is bounded at 8 seconds.
- The 5-second alert threshold leaves time for investigation before the consumer exceeds its tolerance; whether it is sufficient depends on detection and response delay.
- If the system has no contractual upper bound, the architecture must treat the budget as an operational objective supported by monitoring and a failure response—not as a hard guarantee.

### 5.4 Lag and RPO: use a careful relationship

For asynchronous replication, the lag at the time of source failure can approximate the time window of changes that may not exist on the surviving promoted replica. It is therefore a useful **RPO exposure proxy** only under explicit assumptions.

Assumptions needed for the simple approximation:
1. the source acknowledges writes before the replica has applied them;
2. the replica is the recovery source being considered;
3. lag is measured from the relevant source commit position to the replica's durable/applied position;
4. failover promotes that replica without another recoverable copy of the missing writes;
5. the measure corresponds to the same data stream and has not hidden gaps or reordering.

Under those assumptions:

```text
time-based RPO exposure at failure ≈ age of newest source change
                                      missing from the promoted replica
```

If a replica is reported 2 seconds behind at the moment of failure, approximately 2 seconds of source changes may be exposed to loss under this simplified model. This does **not** mean exactly 2 seconds of writes are lost, or that all changes in that interval are missing. Workload activity varies; the lag measure may be delayed; and another durable log or replica may permit recovery.

**A single average lag is not a safe worst-case guarantee.** Record distributions and peaks, monitor the age/position of the newest unapplied change, and test failover. RPO is a business recovery objective; lag is a measurement; a replication protocol/configuration provides a guarantee only within its documented failure model.

### 5.5 Quorum reasoning, carefully qualified

In a system that uses read and write quorums over \(N\) replicas, a common first check is whether read quorum \(R\) and write quorum \(W\) overlap:

\[
R + W > N
\]

This overlap can be a useful condition for intersecting replica sets, but **it is not by itself a complete proof of latest-value or linearizable reads**. The actual guarantee also depends on versioning, concurrent writes, quorum rules, repair behavior, leader/epoch changes, and the system's protocol. Never infer a consistency level from the inequality alone.

### 5.6 Transaction boundaries inside one store

A transaction boundary defines which changes must commit or roll back together.

Examples:
- posting both sides of a transfer;
- updating an account status and recording an audit row;
- inserting an order and its order lines;
- changing a business entity and appending an outbox event.

Keep the boundary large enough to preserve the invariant and no larger than necessary. A transaction spanning many unrelated records can increase contention and failure scope. A boundary that is too small may expose invalid intermediate states.

**Isolation matters:** atomicity does not prevent every concurrency anomaly. Two concurrent transactions may each read the same balance and then write conflicting results unless the chosen isolation level, locking, optimistic concurrency control, or invariant enforcement prevents it.

### 5.7 Transaction boundaries across systems

A database transaction usually controls operations within that database's transaction domain. It does not automatically include:
- publishing to a separate message broker;
- updating a search index;
- calling an external payment API;
- writing an object to independent storage;
- updating a second database with no shared transaction protocol.

Cross-system designs commonly use eventual consistency with explicit recovery rather than pretending the whole workflow is one atomic transaction.

### 5.8 The dual-write hazard

Consider this unsafe sequence:

```text
1. Commit payment row in database.
2. Publish PaymentConfirmed event to message broker.
```

Failure timeline:
- If the process crashes after step 1 and before step 2, the payment exists but the event is missing.
- If the event is published and the process crashes before recording publication status, a retry may publish the event again.
- If step 1 fails but the event is published due to an incorrect ordering/error path, consumers may act on a payment that never committed.

Reversing the order does not solve the problem; it merely changes which partial state is possible.

### 5.9 Outbox-style pattern

An **outbox** is a durable table or equivalent local record of events to publish. The business update and outbox record are written in the same local transaction.

Conceptual flow:

```text
Producer request
    |
    v
Local database transaction
    ├── Update business state
    └── Insert outbox event (unique event ID, aggregate/key, sequence if needed)
    |
    v
Commit succeeds or both changes roll back
    |
    v
Outbox relay reads unpublished rows
    |
    v
Publish event; retry on failure
    |
    v
Mark/record publication progress (implementation-specific)
    |
    v
Consumer receives event
    |
    v
Deduplicate + apply local transaction + record processed event ID
```

This pattern prevents the specific gap in which the business update commits but no durable publication intent exists, provided the business update and outbox insert really share one atomic local transaction.

It does **not** automatically guarantee exactly-once delivery. A relay may publish an event and crash before recording that it did so, causing a retry. Consumers should be prepared for duplicate delivery. The exact delivery guarantee depends on the broker, relay, storage, acknowledgement, and consumer implementation.

### 5.10 Idempotency, deduplication and ordering

- **Idempotent operation:** applying the same request/event repeatedly has the same intended effect as applying it once, within a defined scope.
- **Idempotency key:** a stable identifier used to recognize repeated requests, with a documented uniqueness scope and retention period.
- **Deduplication:** detect and suppress repeated event/request IDs or repeated business effects.
- **Ordering:** a defined order in which events for a key or aggregate must be applied. Global ordering is more expensive and may not be needed.
- **Retry:** attempt an operation again after a transient or ambiguous failure. Retry policy must distinguish safe retries from operations that may duplicate side effects.
- **Reconciliation:** compare the source and downstream state against an invariant and repair gaps.

An idempotent consumer often records the processed event ID and applies its business effect in the same local transaction. If the consumer commits the effect but fails before acknowledging the message, the message may be redelivered; the recorded ID lets the consumer avoid applying the effect twice. This works only if deduplication state and effect commit atomically, or an equivalent protocol is used.

For a non-idempotent external side effect, a local deduplication table alone may not prevent duplicates at the external service. Use an external idempotency key if supported, query the outcome after ambiguous failures, or reconcile and compensate under a defined policy.

### 5.11 Compensating actions and sagas

A **compensating action** is a business operation that counteracts the effect of an earlier completed step when the whole workflow cannot proceed. It is not always a literal rollback.

Example: a booking service reserves inventory and then a payment service declines the payment. A compensating action may release the reservation. If the payment succeeded but a later step failed, the appropriate compensation may be a refund, not deletion of the payment record.

A **saga** is a workflow of local transactions coordinated through events/commands, with retry, timeout, and compensation rules. It supports recovery from partial completion; it does not make independent systems one ACID transaction.

---

## 6. Advanced-level learning sequence

### 6.1 Separate guarantees, assumptions and compensating mechanisms

Use three columns in every design review.

| Category | Meaning | Example |
|---|---|---|
| **System guarantee** | Behavior promised by the selected system under specified configuration and failure assumptions | A committed local transaction is atomic; a configured acknowledgement protocol requires a stated replication acknowledgement |
| **Architecture assumption** | A condition the design expects but has not itself guaranteed | Network delay stays below a target; a consumer normally catches up within 10 seconds |
| **Application mechanism** | Logic designed to preserve or repair correctness across system boundaries | Idempotency key, outbox, deduplication, reconciliation, compensation |

Never promote an assumption into a guarantee. If the design depends on an assumption, state how it will be monitored, tested, and handled when violated.

### 6.2 Failover, split-brain and recovery

**Failover** moves service from a failed or unavailable primary to another node/copy. Safe failover requires more than detecting that the old primary is not responding:
- determine whether it is truly unavailable or merely isolated;
- ensure only the authorized primary can accept writes;
- fence or otherwise prevent the old primary from continuing as a competing writer;
- choose a promotion candidate according to the consistency/durability policy;
- determine whether acknowledged changes are missing;
- restore replicas and consumers without creating divergent histories.

**Split-brain** is a condition in which two nodes or groups both act as authoritative writers for the same logical data. This can produce conflicting updates and divergent histories. A safe design needs a defined authority/fencing mechanism, epoch/term or equivalent protection where applicable, and a recovery procedure for any conflict that remains.

**Reconciliation after recovery** should compare more than row counts when the business invariant requires more:
- transaction/event IDs and sequence ranges;
- counts by date/account/status;
- debit-credit totals or balances;
- source commit positions and consumer offsets;
- missing and duplicate event IDs;
- downstream projections against the authoritative source;
- unresolved/ambiguous external operations.

A matching row count does not prove that the correct rows or amounts match.

### 6.3 Failure matrix: source and replica

| Failure | Synchronous-style replication: possible behavior | Asynchronous replication: possible behavior | Required design response |
|---|---|---|---|
| Primary node fails | If acknowledged writes were durably replicated to a surviving participant and promotion follows the protocol, those writes may be preserved; service may pause while a safe primary is selected | Promoted replica may be behind; recent acknowledged writes may be missing | Establish the failure model, select promotion rule, determine loss exposure, reconcile, and communicate service state |
| Required replica unavailable | Writes may block/fail or the system may alter behavior only if configured to do so | Source may continue while lag grows | Define whether writes fail closed, degrade, or continue; monitor the resulting RPO exposure |
| Network partition | Depending on quorum/leadership rules, one side may stop writes to avoid divergent authority | A source may keep accepting writes while replicas are unreachable; lag grows | Avoid dual authority; define availability-versus-consistency policy |
| Replica disk corruption | Corruption may be detected, repaired from another copy, or propagated if undetected | Same risk; the lagging replica may need rebuild | Validate checksums/integrity, rebuild from a trusted source, retain independent backups |
| Operator deletes data | Replication may propagate the deletion | Replication may propagate it after a delay | Restore from independent backup or point-in-time recovery; replication alone is not protection |
| Zone/region loss | Safety depends on replica placement and acknowledgement/failover contract | Safety depends on surviving copy freshness and recovery path | Map replicas to failure domains; test RPO/RTO for the stated outage |

This table describes possible behavior, not universal product guarantees. The selected system's documentation and configuration define the actual behavior.

### 6.4 Cross-system failure analysis: database plus event

Assume a service updates a business row and emits an event for downstream consumers. The outbox pattern is used; event delivery is at least once in the conceptual design. The exact implementation must still be validated.

| Failure point | Durable state after failure | Risk | Recovery/control |
|---|---|---|---|
| Before local transaction starts | No business change and no outbox event | Request may be retried | Retry using request/idempotency policy |
| During local transaction before commit | Neither business update nor outbox event should commit if transaction rolls back correctly | Partial writes if transaction boundary is incorrectly designed | Verify atomicity; rollback/retry |
| Commit succeeds, process crashes before relay sees outbox row | Business update and outbox intent are durable | Publication delayed, not silently absent if outbox is retained and relay resumes | Relay scans/claims pending rows and retries; monitor age of oldest pending row |
| Relay reads outbox row but crashes before publish | Business update and outbox intent remain | Event not yet delivered | Retry publication |
| Broker accepts event, relay crashes before recording publication | Event may already be in broker; outbox may still appear pending | Duplicate publication on retry | Stable event ID; consumer idempotency; relay/broker protocol as supported |
| Event is delivered twice | Broker/consumer may see duplicate event IDs | Duplicate business effect if consumer is not idempotent | Deduplicate atomically with consumer effect |
| Consumer fails before local commit | Consumer's effect should not commit; event may be redelivered | Repeated attempts or poison event | Retry with backoff; quarantine/dead-letter under policy; alert and repair |
| Consumer commits effect but fails before acknowledgement | Effect and processed-event ID are durable if committed together | Redelivery | Check processed ID and skip duplicate effect; acknowledge safely |
| Events are delayed or reordered | Consumer may see an older event after a newer event | State regression or incorrect derived state | Partition/order by key where needed; sequence/version checks; buffer or reject stale events; reconcile |
| Consumer is offline for a long period | Outbox/broker retains events only according to its retention/availability contract | Retention expiry may cause gaps | Alert on consumer lag; replay from source/outbox/archive if available; reconcile gaps |
| Recovery/replay repeats a long range | Events may be reprocessed | Duplicate side effects or stale state if replay is unsafe | Idempotent processing, version guards, replay plan, reconciliation |
| External API outcome is ambiguous | Local service may not know whether external effect occurred | Retry could duplicate an irreversible effect | Query external status, use provider idempotency key if supported, escalate unresolved outcomes |

### 6.5 Sequence example: outbox with idempotent consumer

This is conceptual pseudocode, not product-specific executable code.

```text
handlePayment(command):
    begin local transaction
        look up command.idempotency_key under a concurrency-safe uniqueness rule
        if key already completed:
            read recorded result
            end transaction without changing business state
            return recorded result

        validate business invariant
        update ledger state
        insert payment result
        insert outbox event with stable event_id and aggregate sequence
        record command idempotency key and result
    commit local transaction

relay:
    for each pending outbox event:
        publish event with event_id
        after broker acknowledgement, record publication progress
        # a crash between publish and progress update can cause duplicate publish

consumer(event):
    begin local transaction
        if event.event_id already processed:
            end transaction without changing business state
            mark for acknowledgement after transaction closure
        else:
            validate sequence/version if ordering matters
            apply local projection/business effect
            record event.event_id as processed
    commit local transaction
    acknowledge message only after the local transaction outcome is known
```

Implementation cautions:
- The command idempotency record must share the correct transaction boundary with the business effect. A uniqueness constraint or equivalent concurrency-safe claim is needed so two simultaneous requests with the same key cannot both execute the effect.
- The consumer's processed-event record must commit atomically with its local effect, or an equivalent guarantee must exist.
- The relay may publish more than once; the stable event ID is what allows deduplication.
- Broker acknowledgement and publication progress are implementation-specific.
- Sequence numbers are only useful if the producer assigns them correctly and consumers define what gaps/reordering mean.
- This design does not make an external API part of the local database transaction.
- “Exactly once” should only be claimed for a precise operation boundary if the full system actually guarantees it. Across independent database, broker, consumer and external side effects, prefer explicit at-least-once delivery plus idempotent effects and reconciliation unless a verified end-to-end protocol establishes otherwise.

### 6.6 Lag budget and operational response table

| Signal | What it measures | Example policy (illustrative) | What it does not prove |
|---|---|---|---|
| Current replica lag | Current delay/position difference | Display and alert above 5 seconds for an activity feed | That lag will stay below 5 seconds |
| Maximum observed lag over a window | Peak measured during that period | Review if any sample exceeds 10 seconds | A bound on future worst-case lag |
| Oldest unprocessed outbox event | Time since publication intent was committed | Alert at 5 seconds; escalate at 10 seconds for a 10-second budget | That every event has been published unless the measurement covers all pending states |
| Consumer offset/sequence gap | Progress difference between source and consumer | Pause finalization or trigger replay when a required range is missing | That all missing events are recoverable from the current broker retention |
| Failover data-loss check | Missing source commit positions or business records after promotion | Block normal processing until loss assessment/reconciliation completes | That row counts alone prove correctness |
| Recovery duration | Time until service meets its recovery definition | Compare to RTO | That all downstream projections have caught up |

An alert threshold should be below the business limit only if detection, notification, diagnosis, and response can plausibly happen before the limit is breached. If not, use an automated safety response (for example routing a critical read to the source, stopping a decision workflow, or marking a feed stale) rather than relying only on an alert.

### 6.7 Recovery objectives and tests

For each data class, define:
- **RPO:** what data loss is tolerable, and how the recovery point is established;
- **RTO:** what “service restored” means, including critical reads/writes and downstream dependencies;
- failure domains: process, node, disk, zone, region, operator error, corruption;
- recovery source: replica, transaction log, backup, event log, or reconciled external record;
- correctness checks before reopening writes;
- who authorizes failover and who resolves data divergence.

A failover drill should measure:
1. failure detection time;
2. time to fence the old writer;
3. promotion/restore time;
4. missing acknowledged write range, if any;
5. service recovery time;
6. replica/consumer catch-up time;
7. reconciliation discrepancies;
8. whether the RPO/RTO criteria were met.

Do not claim RPO=0 or a particular RTO from architecture diagrams alone. It requires a defined failure model and evidence from the selected implementation and tests.

### 6.8 Concurrent updates and transaction isolation

Replication does not fix an invalid concurrent-update model. For example, two withdrawals may each read the same available balance, calculate a valid result independently, and then overwrite one another. A transaction boundary with insufficient isolation may allow a lost update or write skew.

Possible controls depend on the store:
- atomic conditional update;
- locking or serializable isolation;
- optimistic concurrency with version checks;
- unique constraints or invariant enforcement;
- single-writer ownership for a key/aggregate;
- conflict-resolution logic in multi-writer systems.

Each control has a cost: lower concurrency, retries, contention, or more application complexity. Validate with concurrent tests, not only single-threaded functional tests.

### 6.9 Network partitions: availability versus consistency

A network partition can prevent nodes from communicating. A design that continues writes on multiple isolated sides risks divergent state unless it has a safe conflict/authority strategy. A design that requires a quorum or single authoritative writer may reject or block some operations to preserve its consistency rules.

This is a business decision:
- For a critical ledger operation, rejecting a write temporarily may be safer than acknowledging conflicting state.
- For a low-risk activity feed or cache, serving stale data may be preferable to unavailability.
- For a downstream analytics copy, lag may be acceptable as long as freshness is visible and completeness is eventually verified.

Do not use “CAP” as a shortcut for a full design. Specify the operation, the failure condition, the consistency guarantee, and what the application does when the required guarantee cannot be satisfied.

### 6.10 Reconciliation design

A reconciliation procedure needs:
1. a declared authoritative source;
2. a key or stable identifier to compare records;
3. a time/window or sequence boundary;
4. business invariants (for example, transfer debits equal credits);
5. detection of missing, duplicate, stale, and conflicting records;
6. repair rules and safeguards against double application;
7. an exception queue and owner;
8. an audit trail of discrepancies and repairs;
9. a way to prove the process completed.

Example: compare ledger payment IDs with payment-confirmed event IDs over a defined time window. Investigate each committed payment with no event, each event with no committed payment, and duplicates. The outbox should reduce the first class of gap, but reconciliation remains useful for software defects, retention mistakes, manual intervention, and downstream consumer failures.

---

## 7. Industry-application exercises

The following is a **fictional illustrative case**. No stated number is a Northbridge Bank requirement or measured result.

### 7.1 Northbridge Bank requirements to elicit

Assume Northbridge has:
- a ledger service that owns posted account movements;
- a customer-facing balance view;
- a transaction-history analytical store;
- a risk service consuming payment and transfer events;
- a notification service sending payment confirmations.

Before choosing mechanisms, ask stakeholders to specify:
- which operations must be atomic;
- which reads must include a just-completed write;
- maximum acceptable staleness for each derived view;
- acceptable acknowledged-write loss by failure class;
- acceptable service recovery time;
- duplicate-event tolerance and ordering scope;
- retention and replay needs for events;
- how unresolved external notification/payment outcomes are handled.

Do not invent these requirements. The exercise below gives illustrative values only to demonstrate the method.

### 7.2 Illustrative operation-to-guarantee table

| Operation | Business invariant / consequence | Required guarantee | Candidate mechanism | Assumption to verify | Failure response |
|---|---|---|---|---|---|
| Post transfer | Debit and credit must balance; no half-transfer | Atomic local ledger transaction; durability matched to agreed RPO | One transaction covering both entries and transfer record; configured replication strategy | All rows share one transaction domain; failover contract protects required committed writes | Reject/roll back incomplete posting; perform recovery and ledger reconciliation |
| Read balance immediately after posting | Customer must not see a balance older than their completed transfer | Read-your-writes or stronger | Route to authoritative/strongly consistent path or use a supported consistency token | Read routing and failover preserve the guarantee | Retry against authoritative path, or return explicit temporary-unavailable state |
| Risk alert | Late alert may allow fraud loss; duplicate alert must not duplicate a financial action | Defined freshness budget; duplicate-safe effect | Outbox, durable event stream, idempotent consumer, lag alerting | Budget reflects risk tolerance; replay retention sufficient | Trigger lag response, replay, reconcile event IDs and risk outcomes |
| Transaction history page | May lag behind ledger if the UI clearly defines freshness | Bounded staleness or eventual consistency | Asynchronous projection | User cannot use this view as the authority for a payment decision | Display freshness; route critical balance decisions to the ledger |
| Payment confirmation notification | Notification may be delayed, but a committed payment must not be silently forgotten | Durable publication intent; duplicate-safe sending where possible | Outbox relay; notification idempotency key or delivery ledger if supported | Provider behavior and idempotency scope are verified | Retry, query delivery state where possible, reconcile pending notifications |
| Daily finance report | Must represent a known cutoff and not silently omit transactions | Consistent as-of cutoff and completeness checks | Controlled snapshot/extract, reconciliation, late-arrival policy | Cutoff and source consistency are defined | Mark report incomplete and rerun/reconcile before final publication |

### 7.3 Illustrative replication topology and lag budget

Candidate conceptual topology:

```text
                ┌────────────────────────────┐
Commands ──────>│ Authoritative ledger store │
                │ local transaction boundary │
                └─────────────┬──────────────┘
                              │
                   configured replication
                              │
                  ┌───────────▼───────────┐
                  │ Recovery/read replica │
                  └───────────────────────┘

Ledger transaction:
  ├── ledger changes
  └── outbox event (same local transaction)

Outbox relay ──> durable event transport ──> idempotent consumers
                                             ├── risk projection
                                             ├── customer history
                                             └── notification workflow
```

This is a logical flow, not a claim about a specific product topology or a guarantee that the replica can be safely promoted. The selected store must document the replication acknowledgement and promotion rules.

**Illustrative lag budget table**

| Data path | Business tolerance (illustrative) | Alert / safety response | RPO interpretation |
|---|---|---|---|
| Ledger to recovery replica | Assume the business requires no loss of acknowledged ledger commits for the specified node-failure scenario | Monitor replication position; failover only to a candidate meeting the documented promotion rule | Cannot be proven by a time-lag graph alone; verify acknowledgement durability, failure model and promotion behavior |
| Outbox to risk consumer | 2 seconds target; 5 seconds alert; 10 seconds maximum acceptable delay (illustrative) | Alert at 5 seconds; at 10 seconds apply defined risk-service degradation/escalation and replay | Consumer lag is not automatically ledger RPO; it is a freshness/delivery budget |
| Outbox to transaction-history projection | 60 seconds maximum staleness (illustrative) | Display stale status and alert when over budget | Missing events require replay/reconciliation, not merely waiting for lag to fall |
| Outbox to notification workflow | 30 seconds target (illustrative) | Retry and monitor oldest pending event | A delayed notification is not necessarily a lost ledger transaction; track the workflow separately |

**Important distinction:** the recovery replica's lag relates to which source changes may be missing after a failover. The risk consumer's lag relates to when downstream processing has caught up. These are different positions in the system and should not be treated as one RPO number.

### 7.4 Failure analysis for a transfer event

Consider this local transaction:
- write the debit/credit ledger entries;
- write the transfer record;
- write an outbox event with stable `event_id`;
- commit all together.

Then analyze the downstream flow:
1. **Before commit:** no ledger change or outbox event should be durable if the transaction rolls back.
2. **After commit, before relay:** ledger and outbox intent exist; event publication is delayed.
3. **During publication:** relay failure may leave publication status uncertain; retry can duplicate the event.
4. **Duplicate delivery:** consumer deduplication prevents a second business effect only if its processed-event record and effect are atomic or otherwise safely coordinated.
5. **Consumer failure before commit:** local effect should not be committed; retry is expected.
6. **Consumer failure after commit, before acknowledgement:** message can be redelivered; processed-event ID suppresses duplicate effect.
7. **Delayed/reordered event:** sequence/version policy prevents an older event from overwriting a newer state if the consumer's logic requires order.
8. **Retention/replay gap:** if events are no longer available, compare source transactions with consumer state and rebuild or repair under an approved procedure.
9. **Primary failure:** evaluate ledger RPO separately from downstream event lag; the outbox is only as durable as the local transaction and recovery path.
10. **Recovery complete:** reconcile transfer IDs, ledger invariants, outbox publication state, and downstream event IDs before declaring the incident resolved.

### 7.5 Exercise: design and defend the strategy

Prepare:
1. a business-invariant list for transfers and balances;
2. an operation-to-consistency table for at least six operations;
3. a replication topology diagram with failure domains;
4. a lag-budget table with measurement definition, normal target, alert threshold, hard business limit, and response;
5. a dual-write/outbox design with event IDs and idempotency rules;
6. a cross-system failure matrix covering every failure point in Section 6.4;
7. a reconciliation plan with source, keys, invariants, time windows, and repair owner;
8. a failover test plan with explicit RPO/RTO criteria;
9. rejected alternatives and the business consequences that make them unsuitable.

**Answer guidance:** a good design does not simply state “use synchronous replication and exactly-once events.” It defines the exact operation guarantee, identifies the system providing it, distinguishes the guarantee from assumptions, allows for duplicate delivery where appropriate, and describes recovery when an assumption fails.

---

## 8. Practical scenarios and case-based reasoning

> **Scenario-data caveat:** all numerical values in this section (including the 2-second lag, 300 ms average, 20-second tail, and event-retention periods) are illustrative assumptions for reasoning, not observed measurements, service-level commitments, or universal targets.

### Scenario 1 — Customer sees an old balance from a replica

A customer successfully transfers funds and immediately refreshes the balance page. The page reads from an asynchronous replica and displays the old balance.

**Questions**
1. Did the ledger write necessarily fail?
2. Which guarantee did the page require?
3. What options are available without making every read synchronous?
4. What should happen if the authoritative read path is temporarily unavailable?

**Answer guidance**
- The ledger write may have succeeded; the replica may simply not have applied it yet.
- The page may need read-your-writes for the initiating customer, not necessarily globally strong reads for every dashboard.
- Options include routing the immediate follow-up read to the authoritative path, using a supported session/consistency token, or waiting within a bounded policy while showing a clear pending/freshness state.
- Do not silently display stale data as current if the user may make a consequential decision from it.

### Scenario 2 — Primary fails while asynchronous replicas lag by 2 seconds

Illustrative case: the primary fails, and a candidate replica is reported to be approximately 2 seconds behind at the failure time.

**Questions**
1. Can you conclude exactly two seconds of data were lost?
2. What decides whether acknowledged writes are lost?
3. What should the service do before resuming critical writes?
4. How do you reconcile?

**Answer guidance**
- No. Two seconds is a lag observation, not a count of lost transactions or a hard bound. The metric definition, missing log position, other copies, and failover protocol matter.
- If the promoted replica lacks acknowledged source commits and no recovery source can restore them, those changes may be lost from the active history.
- Follow the documented promotion policy, assess missing acknowledged writes, and apply the ledger's fail-closed or recovery rule.
- Reconcile transaction IDs, source commit positions, debit/credit invariants, and downstream events; record repairs and unresolved discrepancies.

### Scenario 3 — Service writes a database and publishes an event separately

A service commits a row, then publishes an event. Crashes sometimes leave rows without events; retries sometimes create duplicate events.

**Answer guidance**
- The database commit and broker publication are separate transaction boundaries.
- Use an outbox or another mechanism that atomically persists business state and publication intent. A relay retries publication.
- Design for duplicate delivery: stable event IDs, idempotent consumer effects, deduplication state committed with the effect, and explicit ordering requirements.
- Add reconciliation to detect missing downstream effects. Do not claim end-to-end exactly-once processing from the outbox alone.

### Scenario 4 — Synchronous replication blocks writes during a replica outage

A business owner complains that writes stop when a required replica cannot acknowledge.

**Answer guidance**
- This may be the configured trade-off to preserve a durability/consistency guarantee under the defined failure model.
- Confirm the actual protocol: required acknowledgements, degraded-mode behavior, and failover safety.
- Compare the business cost of write unavailability with the accepted data-loss exposure. Do not silently weaken the protocol without updating RPO and correctness requirements.

### Scenario 5 — A read replica has low average lag but occasional long stalls

Illustrative measurements: average lag is 300 ms, but some samples reach 20 seconds.

**Answer guidance**
- The average hides the tail. Use percentile/maximum observed lag, age of oldest unapplied change, and time spent above the business budget.
- The 20-second observation may violate a freshness contract even though the average is low.
- Determine whether the consumer should switch read paths, expose stale status, pause a decision workflow, or alert/escalate.

### Scenario 6 — Two writers update the same account concurrently

Two requests read the same balance and compute separate updates.

**Answer guidance**
- Replication does not solve the lost-update risk.
- Identify the invariant and transaction isolation guarantee. Consider atomic conditional updates, locking/serializable isolation, optimistic version checks, or a single-writer rule where supported.
- Test concurrent operations and assert the business invariant, not only that both requests returned success.

### Scenario 7 — A consumer is offline longer than event retention

Illustrative retention case: a risk consumer is offline for two days, while the transport retains only one day of events.

**Answer guidance**
- The consumer may have a permanent gap in its available replay range.
- Lag monitoring should alert before retention expiry; recovery needs a durable source/outbox/archive or a rebuild from authoritative records.
- Reconcile by stable event IDs or business keys and prove that the rebuilt projection is complete.

### Scenario 8 — Failover creates two apparent primaries

A network partition causes one team to promote a replica while the old primary later resumes accepting writes.

**Answer guidance**
- This is a split-brain risk. Define one authoritative writer using fencing, leases/epochs, quorum/leadership rules, or the selected system's equivalent mechanism.
- Do not merge divergent ledger histories using “last writer wins” unless the business explicitly accepts the loss and conflict semantics.
- Stop conflicting writes, identify the authoritative history, reconcile the divergent changes, and record the incident.

### Scenario 9 — A team says its pipeline is “exactly once”

The team points to a broker's delivery mode but the pipeline also writes to a database and calls an external API.

**Answer guidance**
- Ask: exactly once at which boundary—producer-to-broker, broker-to-consumer state, database effect, or external side effect?
- A broker guarantee does not automatically make a database commit and API call atomic.
- Document the scope of each guarantee, use idempotency and reconciliation for cross-system effects, and test ambiguous failures.

---

## 9. Expected outputs and deliverables

### 9.1 Operation-to-consistency requirements table

For every important business operation, include:
- business invariant and consequence of violation;
- required read/write consistency;
- acceptable staleness and loss;
- candidate system mechanism;
- system guarantee to verify;
- architecture assumptions;
- failure response and recovery owner.

No row is complete if it says only “strong consistency” or “eventual consistency” without describing the business consequence.

### 9.2 Replication topology and lag budget

Include:
- source of record and replica/derived-copy roles;
- replica placement and failure domains;
- synchronous/asynchronous acknowledgement behavior where relevant;
- promotion/fencing rules;
- RPO and RTO targets by data class;
- lag measurement definition and unit;
- normal target, alert threshold, maximum tolerated lag, and action;
- limitations of the metric and recovery path.

### 9.3 Cross-system consistency design

Document:
- producer transaction boundary;
- event publication mechanism (outbox or justified alternative);
- event ID, aggregate/key, version/sequence, and schema expectations;
- retry and duplicate-handling policy;
- consumer transaction and deduplication boundary;
- ordering requirements;
- external API behavior and idempotency support;
- replay retention and recovery process;
- reconciliation rules, exception ownership, and audit trail.

### 9.4 Failure analysis

For each failure point, state:
- what has committed;
- what may be missing, stale, duplicated, or out of order;
- whether acknowledged data can be lost;
- what a reader or consumer can observe;
- which system guarantee applies;
- recovery/replay/reconciliation action;
- test that proves the recovery behavior.

### 9.5 Test and decision record

A validation plan should specify:
- failure injection or failover scenario;
- expected state and business invariants;
- observed lag and data-loss exposure;
- time to restore service;
- duplicate/missing/reordered event checks;
- reconciliation discrepancies and repairs;
- pass/fail criteria fixed before testing;
- owner and unresolved risks.

---

## 10. Common mistakes and misconceptions

1. **Treating replication as backup.** Replication may copy deletions or corruption; independent backups and restore tests address different risks.
2. **Equating replication with synchronization between systems.** Separate stores need integration, ownership, lag, replay, and reconciliation rules.
3. **Treating “committed” as a universal guarantee.** A commit's meaning depends on transaction scope, isolation, durability configuration, and documented failure model.
4. **Assuming synchronous replication is always safer or better.** It trades latency/availability for particular acknowledgement guarantees; configuration and failure domain matter.
5. **Assuming asynchronous replication always loses data.** Loss is possible if a failure leaves acknowledged changes only on the failed source; other recovery copies may exist.
6. **Using average lag as the maximum lag guarantee.** Averages hide stalls and tail exposure.
7. **Treating observed lag as RPO.** Lag is a measurement; RPO is a business objective. Their relationship requires explicit assumptions.
8. **Assuming a read replica is safe for every read.** Read-your-writes and decision-critical operations may require an authoritative path or a defined freshness rule.
9. **Assuming a transaction covers a database and message broker.** Separate systems do not share atomicity unless a supported coordination protocol establishes it.
10. **Using a naive dual-write sequence.** A crash between commits creates a missing event or a phantom event.
11. **Assuming an outbox guarantees exactly-once delivery.** Publication can be retried and duplicated; the pattern makes publication intent durable.
12. **Deduplicating outside the effect transaction.** A crash between effect and dedup record can still duplicate the effect.
13. **Ignoring ordering.** Duplicate-safe consumers can still regress state if older events overwrite newer state.
14. **Retrying ambiguous external calls blindly.** The external action may already have happened; query outcome or use a supported idempotency mechanism.
15. **Using row counts as complete reconciliation.** Equal counts can hide wrong values, missing/duplicate pairs, or broken business invariants.
16. **Assuming a multi-primary or quorum topology has one universal consistency behavior.** The protocol and configuration determine the guarantee.
17. **Failing to prevent split-brain.** A promoted node must not coexist as an unfenced competing writer.
18. **Ignoring failure-domain placement.** Replicas in one zone may not protect against zone loss.
19. **Assuming eventual consistency means “will always be correct soon.”** Convergence depends on delivery, retry, retention, and repair mechanisms.
20. **Claiming exactly-once end to end without defining scope.** State which boundary is guaranteed and how external side effects are made safe.
21. **Leaving recovery and reconciliation ownerless.** A design without an accountable operator and tested procedure is incomplete.

---

## 11. Mastery criteria

You have mastered this topic when you can provide evidence that you can:

- [ ] Define replication, lag, synchronous/asynchronous replication, consistency, isolation, durability, atomicity, idempotency, reconciliation, RPO and RTO accurately.
- [ ] Explain why replication is not backup and why a separate-system copy is not automatically consistent.
- [ ] Compare synchronous and asynchronous replication under node loss, replica outage, and network partition.
- [ ] Translate each important business operation into a consistency/freshness/loss requirement and a failure response.
- [ ] Separate system guarantees from architecture assumptions and application compensations.
- [ ] Define a lag budget with measurement semantics, thresholds, actions and limitations.
- [ ] Explain why average lag is not a safe worst-case bound and calculate a lag-based loss exposure only with explicit assumptions.
- [ ] Identify transaction boundaries and concurrency anomalies.
- [ ] Explain the dual-write failure window and the role and limitations of an outbox.
- [ ] Design duplicate-safe consumers, retries, deduplication, ordering and reconciliation.
- [ ] Analyze every failure stage in a cross-system flow, including replay and recovery.
- [ ] Define failover tests and pass/fail criteria tied to RPO/RTO and business invariants.
- [ ] Avoid unsupported “exactly-once” claims and specify the scope of each guarantee.

**Mastery standard:** a reviewer can trace every claimed guarantee to a documented system capability or explicit application mechanism, see the assumptions, and understand the business response when the guarantee cannot be met.

---

## 12. Completion gate

Do not mark Topic 6 complete until all of the following are satisfied.

- [ ] **Requirements:** the operation-to-consistency table links each guarantee to a business consequence.
- [ ] **Topology:** the replication diagram names the system of record, replica roles, failure domains, and promotion/fencing assumptions.
- [ ] **Lag budget:** measurement method, units, normal target, alert threshold, maximum tolerance, and response are explicit.
- [ ] **RPO/RTO:** objectives are stated per relevant data class and are not confused with observed lag or recovery time measurements.
- [ ] **Guarantees versus assumptions:** each system guarantee is verified for the chosen category/configuration; assumptions have monitoring or test plans.
- [ ] **Transaction boundaries:** local atomic changes and cross-system steps are distinguished.
- [ ] **Dual-write analysis:** failure before commit, after commit but before publication, duplicate delivery, consumer failure, reordering, retention gaps, and replay are covered.
- [ ] **Recovery:** failover, split-brain prevention, and reconciliation are described with owners and correctness checks.
- [ ] **No unsupported claims:** no generic synchronous/asynchronous guarantee or end-to-end exactly-once claim is made without a precise scope and evidence.
- [ ] **Practice questions:** answer the Topic 6 practice questions, correct wrong answers, and attempt them again.
- [ ] **Validation:** the failover and cross-system test plan has baseline conditions, expected outcomes, and pass/fail criteria defined before execution.

### Final self-test

1. What does synchronous replication guarantee under the configured protocol, and what assumptions remain?
2. Why can an asynchronous replica's measured lag not by itself establish a hard RPO?
3. How is RPO different from RTO?
4. Why is replication not a backup?
5. What is the business difference between read-your-writes and eventual consistency?
6. What failure window exists when a service commits a database row and then publishes an event separately?
7. What does the outbox pattern solve, and what does it not solve?
8. How should a consumer handle an event delivered twice after its effect committed but acknowledgement failed?
9. Why is an idempotent consumer not enough for an external API that lacks idempotency or queryable outcomes?
10. What evidence is needed before declaring recovery complete after failover?

A strong answer identifies the operation, invariant, guarantee, assumption, failure mode, and recovery action.

---

**Topic boundary:** this lesson defines replication, consistency, and transaction-boundary decisions. Detailed cross-system integration patterns are developed in Stage 2D.6; platform-level resilience and disaster recovery are developed in Stage 2D.12. Those topics build on these concepts, but do not remove the need to define correctness and recovery requirements here.
