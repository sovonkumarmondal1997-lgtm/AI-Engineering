# Event Brokers, Topics, Partitions, and Retention

> **Purpose:** Learn how a partitioned event log carries events from producers to consumers, how topic and key design determine ordering and parallelism, and how retention and replication affect replay, availability, storage, and operational cost.

> **Scope and source note:** This lesson follows `roadmap-Streaming-and-Real-Time-Data-Architecture.md`, the module-specific source of truth. That roadmap states that the topic files were empty when it was written and that its scenarios, numbers, exercises, and targets are illustrative recommendations—not requirements already documented in those files. All numerical values and the fictional examples in this lesson are explicitly illustrative. Concepts are vendor-neutral; broker products differ, so verify exact semantics and configuration against the selected product.

---

## 1. Title and purpose

An event broker is a transport and storage layer for events. It lets producers publish records without requiring every consumer to be online at the same moment, and it lets multiple independent applications consume the same event stream for different purposes.

But “put events on a broker” is not a complete design. Architects must decide:

- Which events belong in which topics?
- What key, if any, should group related events?
- How many partitions are needed for throughput and parallel processing?
- What ordering guarantee does the business actually require?
- Which consumers need independent progress?
- How long must events remain available for normal consumption, recovery, audit, or replay?
- What replication and failure behavior is needed?
- How do these decisions support the latency objective from Topic 1 without creating excessive cost or operational complexity?

By completing this lesson, you should be able to produce a conceptual topic-and-partition design, justify key and partition choices, estimate retained storage transparently, and document the important assumptions.

## 2. Position in Stage 2D and prerequisites

This is Topic 2 of `Stage 2D — Data Architecture/09-Streaming-and-Real-Time-Data-Architecture/`. The module’s recommended numeric order is:

1. `01-real-time-use-cases-and-latency-budgets.md` — define the business outcome and latency requirement.
2. `02-event-brokers-topics-partitions-and-retention.md` — design the event carrying layer (**this lesson**).
3. `03-event-time-processing-ordering-and-watermarks.md` — distinguish event time from processing time and reason about ordering and watermarks.
4. `04-stream-processing-state-and-delivery-semantics.md` — understand state, checkpoints, and processing/delivery semantics.
5. `05-cdc-event-backbones-and-replay.md` — integrate database changes and design replay.
6. `06-real-time-serving-stores-and-materialized-views.md` — make computed results usable.
7. `07-late-events-backpressure-and-stream-failure-modes.md` — reason about lag, overload, and failures.

### Prerequisites

The module roadmap identifies these as essential or particularly relevant:

- **P1 — Measurable latency, freshness, throughput, and availability targets.** Topic and partition decisions must support the end-to-end objective, not a generic “fast” label.
- **P2 — Volume, rate, and growth estimation.** Partition sizing and retention depend on event rate, average encoded size, peaks, and growth.
- **P4 — Batch/stream and event-driven patterns.** Understand why a broker is being introduced.
- **P5 — Events, state, and domain-event basics.** Know what an event represents and what entity or process it belongs to.
- **P6 — Event contracts and schema evolution.** Producers and consumers need an agreed record structure.
- **P8 — Idempotency, deduplication, and reconciliation at a conceptual level.** A broker alone does not guarantee that downstream business effects occur exactly once.

Review these repository-relative references if needed:

- `../02-Requirements-Constraints-and-Architecture-Decisions/03-data-volume-velocity-variety-and-growth-estimation.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/04-latency-throughput-freshness-and-availability-targets.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/06-architecture-trade-offs-and-decision-criteria.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/07-architecture-decision-records-adrs.md`
- `../03-Data-Architecture-Patterns-and-Reference-Architectures/06-event-driven-and-data-sharing-patterns.md`
- `../04-Conceptual-Logical-and-Physical-Data-Modeling/06-event-modeling-and-domain-driven-design.md`
- `../04-Conceptual-Logical-and-Physical-Data-Modeling/07-schema-evolution-and-backward-compatibility.md`
- `../06-Data-Integration-and-Interoperability/04-streaming-events-and-message-contracts.md`
- `../06-Data-Integration-and-Interoperability/05-data-contracts-schema-registry-and-compatibility.md`
- `../06-Data-Integration-and-Interoperability/07-idempotency-deduplication-and-reconciliation.md`

## 3. Learning objectives

By the end of this lesson, you will be able to:

1. Define producer, broker, topic, partition, key, consumer, consumer group, offset, retention, and replication.
2. Trace an event from producer to broker to consumer.
3. Explain an append-only partition log and why ordering is generally guaranteed within a partition, not globally across all partitions.
4. Choose keys based on the entity whose order matters, while evaluating load distribution and hot-partition risk.
5. Explain consumer groups, independent groups, partition assignment, rebalancing, and the common partition-count limit on useful parallel consumers.
6. Estimate partition count using workload throughput, processing capacity, ordering requirements, key distribution, and operational overhead—with explicit assumptions.
7. Estimate retained storage from event rate, encoded event size, retention duration, and replication factor.
8. Explain conceptually how retention, replication, and broker failures affect replay and availability.
9. Connect broker choices to Topic 1’s latency budget and preview dependencies in Topics 3–7.
10. Record a product-neutral design decision and identify which product-specific guarantees must be verified.

## 4. Readiness check

Answer before reading further:

1. What is the difference between an event and a topic?
2. Why might two applications need separate consumer groups for the same topic?
3. If all events use the same key, what could happen to load distribution?
4. Does increasing partition count automatically preserve global event order?
5. If an event is deleted from the broker after retention expires, can a new consumer necessarily replay it from that broker?
6. What extra information is needed to estimate storage from “10,000 events per second”?

**Answers**

1. An event is a record of something that happened; a topic is a named stream/category in which events are stored and read.
2. Each application may need to read the full stream independently and keep its own progress.
3. If the key maps all records to one partition, that partition can become a bottleneck while others are underused.
4. No. Ordering is commonly scoped to an individual partition; multiple partitions progress independently.
5. No. Once records are removed by the broker’s retention policy, replay from that broker may no longer be possible. Another archive may exist, but that is a separate design.
6. Average encoded event size, retention duration, replication factor, and overhead assumptions; for capacity planning, peak rates and growth also matter.

## 5. Beginner foundations and event-flow diagram

### 5.1 Core concepts

| Term | Definition | Why it matters |
|---|---|---|
| **Event** | A record describing something that happened, usually with an identifier, payload, and one or more timestamps | The unit of communication and processing |
| **Producer** | An application or service that publishes events | Its throughput, retry behavior, and contract affect the stream |
| **Broker** | A system that accepts, stores, and makes events available to consumers | Decouples publishers and readers; provides buffering and retention |
| **Topic** | A named logical stream of related events | Establishes a boundary for event type, access, retention, and ownership |
| **Partition** | An ordered sequence of records within a topic in a partitioned-log design | Provides a unit of ordering, storage, and parallelism |
| **Key** | A record field or value used by the broker/client’s partitioning strategy to choose a partition | Related records can be routed together to preserve per-key ordering |
| **Consumer** | An application that reads records and acts on them | Defines the work done with the stream |
| **Consumer group** | A set of cooperating consumers that share reading work for a topic or subscription under a group identity | Enables horizontal processing while maintaining a shared progress model |
| **Offset** | A position or sequence identifier for a record within a partition log | Allows a consumer to track its position and resume reading |
| **Retention** | The policy that determines how long records remain available in the broker | Sets the broker’s replay and recovery window and storage demand |
| **Replication** | Keeping copies of partition data or logs across multiple broker nodes or failure domains | Can improve resilience and availability, depending on product and configuration |

These are conceptual definitions. Exact terms, offset semantics, deletion policies, replication acknowledgements, and group assignment behavior differ across products.

### 5.2 Event flow

```text
+------------------+
| Producer service |
+------------------+
         |
         | publish event (key + payload + metadata)
         v
+-------------------------------------+
| Broker / Topic                      |
|                                     |
|  Partition 0: [r0][r1][r2][r3] ...  |
|  Partition 1: [r0][r1][r2]    ...   |
|  Partition 2: [r0][r1][r2][r3] ...  |
+-------------------------------------+
         |
         | consumers read records by partition position
         v
+--------------------+       +----------------------+
| Consumer group A   |       | Consumer group B     |
| Risk decisions     |       | Operational metrics  |
+--------------------+       +----------------------+
```

A producer publishes a record to a topic. The record is assigned to a partition according to the chosen routing/partitioning behavior. The broker stores it and makes it available for consumers to read. Consumers process records and track their progress. A second consumer group can independently read the same topic for a different purpose.

A broker does not itself know the business meaning of every record or guarantee that a consumer’s external side effect is correct. The event contract, producer behavior, consumer logic, and processing semantics still matter.

### 5.3 Topics: logical streams and ownership boundaries

A topic groups records that belong to a coherent stream. Good topic boundaries often reflect event type, domain, access needs, retention needs, or a clear contract. Avoid treating a topic as an arbitrary dumping ground for unrelated payloads.

A topic design should answer:

- What business event types belong here?
- Who owns the event contract?
- Which producers may publish?
- Which consumer applications need access?
- What retention and replay needs apply?
- Are records compatible with the topic’s schema and evolution policy?
- What volume, sensitivity, and latency requirements apply?

**When to use:** create a distinct topic when events need a separate contract, access boundary, retention policy, scaling profile, or ownership model.

**Trade-offs:** too few topics can mix unrelated contracts and policies; too many topics increase governance, monitoring, permissions, and operational overhead.

**Industry example:** a retail platform may publish `order-events` for order lifecycle changes and `payment-events` for payment outcomes. The separation reflects different ownership, sensitivity, consumers, and retention needs—not merely naming preference.

### 5.4 Append-only partition logs and offsets

In a common partitioned-log design, a partition is an ordered sequence of records appended over time. Records are assigned positions, commonly called offsets. Consumers read records in partition order and use their progress to resume after interruption.

A simplified partition:

```text
Partition 0 (older ------------------------------------------> newer)

Offset:       0       1       2       3       4       5
Record:      [A]     [B]     [C]     [D]     [E]     [F]
```

An offset is usually meaningful within its partition, not as a global position across the whole topic. Offset 12 in Partition 0 is not inherently earlier or later than offset 12 in Partition 1.

**Ordering scope:** systems of this design commonly preserve append/read order within a partition. They do not automatically establish one total order across all partitions. A business requirement for global order may constrain the design to one partition or require an explicit sequencing/coordination mechanism, which can limit scalability and increase complexity.

**Failure modes and caveats:**

- A consumer may process a record but fail before recording progress, or record progress at an unsafe point; the resulting replay/duplicate behavior depends on the system and processing design.
- Retention can remove older records, so an old offset may no longer be readable.
- Partition reassignment or consumer restarts can affect who reads a partition, without creating global ordering.
- Broker products differ in whether offsets are numeric, how they advance, and how progress is stored.

Consumer progress and delivery semantics are developed in Topic 4; this lesson introduces offsets only at the level needed for broker design.

### 5.5 Retention: the broker’s replay window

Retention defines how long the broker keeps records available. Common policy families include time-based retention and size-based retention; some systems also support log compaction or other policies. Exact behavior is product-specific.

Retention affects:

- **Normal consumer delay:** a temporarily slow consumer needs old records to remain available until it catches up.
- **Recovery:** after an outage, consumers may need to resume from earlier positions.
- **Replay:** a consumer or pipeline may need to re-read records to rebuild results or investigate an incident.
- **Audit and investigation:** teams may need a record history for a defined period.
- **Storage and cost:** longer retention generally requires more storage.
- **Data governance:** retention must align with legal, privacy, contractual, and business requirements.

Retention is not the same as a permanent archive. If events must be preserved for years but the broker only needs to support several days of replay, use a separate governed archival design where appropriate.

### 5.6 Replication: copies and failure tolerance

Replication means that partition data is copied to multiple broker nodes or failure domains. It can reduce the risk that a single node failure makes data unavailable, but the guarantee depends on product architecture and configuration.

Important questions include:

- How many replicas exist?
- Are replicas placed in independent failure domains?
- Which replica is allowed to serve reads or become authoritative?
- When is a producer acknowledgement returned?
- What happens if a replica is unavailable or lagging?
- Can a write be acknowledged and later lost under a particular failure scenario?
- What are the storage and network costs?

Do not assume “replication factor 3” means the same durability or availability in every product. Replica count alone does not specify acknowledgement policy, quorum behavior, leader election, consistency, or failure-domain placement.

**When to use:** replication is typically considered when the stream’s durability and availability requirements justify the additional resource cost.

**Trade-off:** more copies can improve resilience but consume additional disk and network bandwidth and can affect write latency. The correct configuration depends on the required failure tolerance and product semantics.

## 6. Intermediate topic, key, partition, and consumer-group design

### 6.1 Keys: choose based on the ordering requirement

A key commonly influences partition assignment. If the same key is consistently routed to the same partition, events for that key can be read in that partition’s order. This is useful when the order of updates for an entity matters.

Possible key choices include:

- `account_id` when account-level event order matters;
- `order_id` when order lifecycle events should be colocated;
- `device_id` when per-device sequence matters;
- a composite key such as `(tenant_id, account_id)` when tenant context is needed and the chosen distribution method supports it.

A key should be selected by answering:

1. Which entity or aggregate needs ordered events?
2. Does every event for that entity use the same stable key?
3. Is the key distribution reasonably balanced?
4. Can one entity generate a disproportionate share of traffic?
5. What happens if the key is null or missing?
6. Will changing the key or partition count alter routing and therefore ordering assumptions?

A key is not automatically a unique event ID. A key often groups many events for an entity; a separate event identifier may be needed for deduplication or tracing.

### 6.2 Bad key and better alternatives: skew

**Illustrative workload:** a consumer receives 50,000 events/s from 100,000 active customer accounts. One key is the constant string `"all-events"`.

If the partitioning strategy hashes the key, every record with the same constant key maps to the same partition. Even with many partitions, that partition receives nearly all traffic. Other partitions may be mostly idle. The result is a hot partition, growing lag, and a long latency tail.

Better choices depend on the requirement:

- If per-account ordering is needed, use `account_id`; traffic should distribute across accounts, subject to skew from unusually active accounts.
- If per-order ordering is needed, use `order_id`, not one global constant.
- If no per-entity ordering is required, consider a null/no-key or round-robin-like strategy if the chosen product and producer support it; distribution behavior and ordering semantics must be verified.
- If a single entity genuinely dominates traffic and its events must remain ordered, splitting that entity across partitions may violate the requirement. Consider whether the business can relax ordering, split the logical workload into independent subkeys, or accept a dedicated hot path. Do not change keys blindly.

A composite key does not magically solve skew. It is only valid if it preserves the ordering semantics required by the consumer. Salting a hot key can distribute its traffic across partitions, but events for the original entity are then split across salts and no longer share one partition-order sequence. Use salting only when the business can relax or reconstruct that ordering safely.

**Illustrative skew diagnostic:** define `skew_ratio = maximum partition rate ÷ mean partition rate`. If a 12-partition topic carries 24,000 events/s, its mean partition rate is `24,000 ÷ 12 = 2,000 events/s`. If the busiest partition carries 4,500 events/s, its skew ratio is `4,500 ÷ 2,000 = 2.25`. The busiest partition is running at 2.25 times the mean. This is a diagnostic, not a universal pass/fail threshold; interpret it alongside per-key rates, processing cost, peak windows, and the workload’s ordering requirements.

### 6.3 Worked example: key and partition design

**All numbers are illustrative assumptions.** A fictional Northbridge Bank receives 24,000 account activity events/s at peak. The risk workflow needs per-account order for some state updates, but does not need a single global order across every account.

Assumptions for a first sizing pass:

- Peak arrival rate: 24,000 events/s.
- Average encoded event size: 1.5 KiB (1,536 bytes).
- Tested sustainable processing capacity per consumer instance: 4,000 events/s for the representative event mix.
- Desired planning utilization for the consumer fleet: 70% (an illustrative test assumption, not a universal rule).
- Candidate partition count: 12.
- Keys are account IDs; no account should dominate traffic, but this must be measured.

**Step 1 — Choose the key from the ordering requirement.**  
Use `account_id` because order is required per account, not globally. A constant key would concentrate traffic and defeat parallelism. `transaction_id` would likely distribute well but would not group all events for one account, so it would not meet the stated per-account ordering need.

**Step 2 — Estimate the consumer capacity needed.**  
At the assumed 4,000 events/s per consumer and 70% planning utilization:

`planning capacity per consumer = 4,000 × 0.70 = 2,800 events/s`

Consumers required by this simplified rate estimate:

`24,000 events/s ÷ 2,800 events/s per consumer = 8.57`

Round up to **9 consumer instances** as an initial estimate.

**Step 3 — Check partition parallelism.**  
With 12 partitions, a common consumer-group model can assign up to 12 partitions concurrently within that group, so 9 consumers could each receive work if assignment and workload distribution permit. This does not guarantee balanced throughput: partition skew, processing-cost variation, and assignment behavior must be tested.

If only 6 partitions existed, adding 9 consumers would not usually yield 9-way partition-level parallelism in one group; some consumers would be idle for that topic. Conversely, adding many partitions increases metadata, file/log management, replication, and operational overhead.

**Step 4 — Validate distribution and assumptions.**  
Measure events per account and per partition under peak and burst traffic. If one account accounts for 30% of traffic, an `account_id` key can still create a hot partition. The architecture must decide whether that account’s ordering requirement is strict and whether the workload can be decomposed safely.

**Conclusion:** 12 partitions is a candidate for testing, not a universal formula or final answer. Validate throughput, end-to-end latency, per-partition skew, failover behavior, and consumer assignment with representative load.

### 6.4 Consumer groups and independent consumption

A consumer group is a named set of consumers that cooperate to read a topic or subscription. In common partitioned-log systems, partitions are assigned among group members so they share the work. A group typically maintains its own progress, independent of other groups.

Example:

- Group `risk-engine` reads `account-events` to compute risk signals.
- Group `operations-dashboard` reads the same topic to update operational metrics.
- Group `warehouse-loader` reads it to load analytical storage.

These are independent groups because each application needs its own progress and processing pace. A slow warehouse loader should not inherently prevent the risk group from reading, though all groups still share broker resources and can affect one another through resource contention.

Within a single group, a partition is commonly assigned to one active consumer at a time for ordered consumption. Thus, useful parallelism for one topic/group is commonly bounded by the number of partitions. Exact assignment, cooperative rebalancing, static membership, and concurrency features vary by product.

### 6.5 Rebalancing at a conceptual level

**Rebalancing** is the reassignment of partitions among consumers in a group when group membership or assignment conditions change—for example, a consumer joins, leaves, crashes, or the topic’s partition layout changes.

Rebalancing matters because it can temporarily interrupt or delay processing. During reassignment, consumers may pause work, reload state, or resume from stored progress depending on the system and application. Frequent restarts, unstable membership, or poorly sized workloads can increase lag and latency.

Do not attempt to solve all rebalancing and recovery problems in this topic. Topic 4 covers state and checkpoints; Topic 7 covers lag and failure modes. For now, include rebalancing behavior in performance and failure tests.

## 7. Partition sizing and ordering trade-offs

### 7.1 What partition count controls

Partition count affects several dimensions at once:

- **Parallelism:** how much independent partition-level work a consumer group can perform.
- **Throughput:** whether records can be spread across consumers and broker resources.
- **Ordering:** which records are placed in the same ordered sequence.
- **Key distribution:** whether a routing strategy can spread keys across partitions.
- **Storage and operations:** more partitions create more logs, metadata, assignments, and monitoring objects.
- **Recovery behavior:** more partitions may mean more assignment and state-management work during restart/rebalance.
- **Latency:** too few partitions can bottleneck; too many can increase overhead and make operational behavior harder to manage.

More partitions are not always better. Partition count should be chosen for the expected workload and tested under the target service objective.

### 7.2 A practical sizing method

Use a transparent method rather than a universal formula:

1. **Establish workload:** average and peak events/s, burst shape, event-size distribution, and processing-cost variation.
2. **Define ordering scope:** global, per entity, per key, or no strict ordering requirement.
3. **Measure processing capacity:** benchmark one consumer instance using representative events and the actual processing logic.
4. **Estimate consumer concurrency:** use measured capacity and a documented planning margin.
5. **Check partition distribution:** estimate or simulate how keys map to partitions and identify hot keys.
6. **Account for broker capacity:** network, disk throughput, replication traffic, and per-partition overhead.
7. **Test end-to-end:** verify the latency objective, not just producer throughput.
8. **Test change and failure:** consumer joins/leaves, broker loss, slow consumers, and backlog recovery.
9. **Document limits:** state what assumptions would force a redesign.

A simplified rate estimate can be useful:

`consumer instances required ≈ peak arrival rate ÷ tested sustainable rate per consumer at chosen planning utilization`

This is only a first approximation. It assumes that event costs are reasonably representative, consumers scale near-linearly, partition assignment is balanced, broker I/O is not the bottleneck, and there is enough partition parallelism. Those assumptions often fail under skew or heterogeneous workloads.

**Worked partition-throughput cross-check (illustrative assumptions):** suppose a topic receives 30,000 events/s with an average encoded record size of 500 bytes (0.5 decimal KB). The incoming record-byte rate is:

`30,000 events/s × 500 bytes/event = 15,000,000 bytes/s = 15 MB/s` (decimal units).

Assume a representative benchmark shows that one partition can sustain 5 MB/s at the required acknowledgement, replication, payload-size, and latency settings. This is an assumed measured capacity for the example, not a generic broker limit.

- At the mean rate with no extra margin, `15 MB/s ÷ 5 MB/s per partition = 3 partitions`.
- For a 2× capacity margin, plan against `15 MB/s × 2 = 30 MB/s`; `30 MB/s ÷ 5 MB/s per partition = 6 partitions`.
- If the consumer group also needs 12-way partition-level parallelism, 12 partitions are the larger constraint in this simplified design. At an even distribution, the average is `15 MB/s ÷ 12 = 1.25 MB/s per partition`, or 2.5 MB/s per partition at the 2× planning rate.

A candidate is therefore `max(6 throughput-based partitions, 12 parallelism-based partitions) = 12 partitions`. This conclusion assumes even key distribution and comparable per-partition capacity. Validate producer ingress, replication traffic, per-partition skew, consumer throughput, end-to-end latency, and failure behavior under representative load. If the benchmark’s 5 MB/s figure already includes a particular replication or acknowledgement configuration, do not count that capacity assumption twice or apply it to a different configuration without testing.

### 7.3 Ordering versus scalability

Ordering is a business constraint with a cost. If every event must be globally ordered, a single ordered sequence or coordination mechanism may be required, which can limit throughput and availability. If order is needed only per account or order, keying by that entity can allow different entities to be processed in parallel while preserving per-key partition order.

Before choosing a key or partition count, ask the domain owner to specify what “in order” means:

- order of source commits?
- order of publication?
- order by event timestamp?
- order within one account/order/device?
- order of consumer side effects?
- does the system tolerate late events or corrections?

Broker partition order is not automatically the same as event-time order or business-causal order. Topic 3 explains event time and watermarks; Topic 4 explains state and processing semantics.

### 7.4 Scaling caveats

Changing partition count can alter key-to-partition mapping in some partitioning schemes. That can affect where future events for a key are stored relative to earlier events, depending on product behavior and the migration strategy. Do not assume that increasing partitions is always a transparent change for an application that relies on per-key ordering.

Plan changes with product-specific documentation, compatibility tests, and a migration approach. Consider whether the application requires a stable key-routing strategy, whether historical records remain in their old partitions, and how consumers combine old and new data.

## 8. Retention, replay window, replication, and storage estimation

### 8.1 Choose retention from recovery and replay needs

Retention should be derived from a documented requirement, not chosen solely because “more is safer.” Ask:

- How long can a consumer be unavailable before it must recover?
- How long could it take to detect and fix a bad deployment?
- How much time is needed to replay and rebuild a derived result?
- Are events needed for audit or investigation?
- Is there a separate durable archive?
- What legal, privacy, or contractual retention rules apply?
- How much storage and replication traffic can the platform afford?

Retention should exceed the maximum expected consumer outage plus the time needed to catch up, with a defensible margin. If replaying a week of events itself takes several days, a one-week retention period may be insufficient to recover from an outage that begins near the retention boundary.

A broker’s retention period is not necessarily the time a consumer has to be offline safely. Consumer lag and catch-up throughput must be considered alongside record age.

### 8.2 Worked retention capacity example

**All figures are illustrative assumptions.** Estimate the baseline retained bytes for one logical copy of a topic. The stated encoded record size is the counted byte size for this exercise; it should not be mistaken for business payload bytes alone if the real record also includes keys, headers, or protocol metadata.

Assumptions:

- Average arrival rate: **5,000 events/s**.
- Average encoded record size counted for this estimate: **2 KiB/event = 2,048 bytes/event**.
- Retention: **72 hours**.
- Replication factor: **3 copies**.
- Ignore compression, indexes, protocol overhead, filesystem reserve, compaction, and other broker metadata in the first calculation. These exclusions mean the result is a baseline estimate, not a final provisioned disk size.
- Use decimal seconds and bytes for the arithmetic; label the conversion to GiB separately.

**Step 1 — Events per second to events per day**

`5,000 events/s × 86,400 s/day = 432,000,000 events/day`

**Step 2 — Events over 72 hours**

`432,000,000 events/day × 3 days = 1,296,000,000 events`

**Step 3 — Logical payload bytes retained (one copy)**

`1,296,000,000 events × 2,048 bytes/event = 2,654,208,000,000 bytes`

That is approximately **2.654 TB decimal** (divide by \(10^{12}\)) or approximately **2.414 TiB** (divide by \(2^{40}\)) for one logical copy.

**Step 4 — Account for three replicas**

`2,654,208,000,000 bytes × 3 = 7,962,624,000,000 bytes`

That is approximately **7.963 TB decimal** or **7.242 TiB** across three copies before compression, overhead, and reserve.

**Interpretation:** the rough retained payload footprint is about 2.654 TB for one copy and about 7.963 TB for three copies under these assumptions. Do not provision exactly this number and call the cluster sized. Add measured overhead, account for compression and segment/index behavior, leave operational disk headroom, and validate with actual record-size distributions and peak arrival rates.

### 8.3 Capacity is not only a retention multiplication

The basic estimate is:

`logical retained bytes ≈ average events/s × average bytes/event × retention seconds`

For replicated storage, a first-order estimate is:

`replicated payload bytes ≈ logical retained bytes × replication factor`

These equations are approximations. Real storage depends on whether the record size includes headers and keys, compression ratio, metadata, indexes, segment management, replication protocol, compaction, and product-specific implementation. Retention may be based on time, size, or both; whichever limit is reached can govern actual deletion behavior.

Use realistic measurements for:

- average and high-percentile event sizes;
- average and peak arrival rates;
- compression under the actual event mix;
- replica placement and replication factor;
- retention policy and deletion timing;
- storage reserved for recovery and rebalancing;
- broker disk utilization alerts and safe operating limits.

### 8.4 Replay window and recovery time

A replay window is the span of history still available for a consumer or recovery process to reread. The effective recovery window is bounded by retention and by how much work can be caught up before the oldest required records expire.

Illustrative example:

- A consumer falls 6 hours behind.
- Live arrivals continue at 5,000 events/s.
- Its recovery processing capacity is 7,000 events/s.
- Its net catch-up capacity is approximately 2,000 events/s while the live arrival rate remains steady.

If the backlog contains 6 hours of events, the backlog count is `5,000 × 6 × 3,600 = 108,000,000 events`. At 2,000 events/s net catch-up capacity, the simplified drain estimate is `108,000,000 ÷ 2,000 = 54,000 seconds`, or **15 hours**. This estimate assumes constant rates, uniform event cost, and no additional bottlenecks. It shows why “retention is 24 hours” does not automatically mean a consumer can recover safely after a 6-hour outage: the oldest records continue aging while the consumer catches up.

For durable long-term history, consider a separate archive or source-of-truth store, with access controls and lifecycle policies appropriate to the data. A broker is not automatically an archive.

### 8.5 Replication, acknowledgement, and availability caveats

Replication affects the chance that data remains accessible when a node or failure domain is lost, but it is not a complete durability specification by itself.

The following concepts must be verified for the chosen product:

- replica placement across independent failure domains;
- leader/primary selection and failover behavior;
- acknowledgement policy for producers;
- minimum in-sync or eligible replicas, if applicable;
- behavior during network partitions;
- whether reads can be served from replicas and what consistency they provide;
- whether acknowledged records can be lost under the documented failure model;
- how replication lag affects visibility and failover.

A system configured for stronger write acknowledgement may trade latency or write availability during failures for stronger durability properties. The exact trade-off depends on product semantics. Do not transfer a configuration recipe from one broker product to another without verifying its meaning.

For cross-region replication, assess replication lag, bandwidth and storage cost, regional failure assumptions, data-residency constraints, and which region is authoritative during failover. Asynchronous replication can leave a recent interval unavailable in the secondary region after a source-region failure; synchronous or quorum-based designs may have different latency and availability trade-offs. Verify the actual product’s guarantees rather than inferring them from the phrase “multi-region.” Producer retry and idempotence features also have product-specific boundaries; they do not by themselves guarantee that every downstream business side effect occurs exactly once. Topic 4 develops delivery semantics in more detail.

## 9. Advanced architecture decisions and product-neutral caveats

### 9.1 Topic boundaries and retention are coupled

Different topics may need different retention periods because consumers, recovery requirements, sensitivity, and volume differ. Combining all event types into one topic may force a compromise retention policy or access boundary. Splitting topics can improve isolation but creates more governance and operational objects.

Document topic ownership, schema/contract, access policy, expected rate, key strategy, ordering requirement, retention reason, and consumer groups.

### 9.2 The latency objective constrains broker choices

Topic 1 defines the end-to-end objective and measurement boundaries. Broker design contributes to that budget through producer publication, broker acknowledgement, queueing, consumer wait, replication, and rebalancing. A topic can have high aggregate throughput yet miss a latency objective because one partition is hot or a consumer group is behind.

Monitor the broker stages that matter to the chosen SLO, such as publish acknowledgement latency, per-partition traffic, consumer lag, replication health, and under-replicated or unavailable partitions where the product exposes those signals. The names and meanings of metrics are product-specific.

### 9.3 Partition count is not the only parallelism limit

Useful parallelism can be constrained by:

- partition count;
- consumer instance count and per-instance concurrency;
- CPU, memory, disk, and network;
- partition/key skew;
- expensive downstream calls;
- state ownership or transaction boundaries;
- broker throughput and replication overhead;
- rebalancing and restart costs.

Adding consumers beyond the available partition-level work may not increase throughput. Adding partitions may not help if the bottleneck is a downstream database or a single hot key.

### 9.4 Key and partition changes require migration thinking

Changing the key may change the ordering group. Changing partition count can change partition mapping under some routing schemes. Either change can complicate the interpretation of historical and new events if consumers assume all events for an entity live in one continuous partition sequence.

Before changing a key or partition count:

1. State the invariant that must be preserved.
2. Check product-specific partitioning behavior.
3. Define how old and new records are handled during migration.
4. Test per-key ordering and duplicate handling.
5. Monitor lag and latency during rollout.
6. Record rollback and reconciliation steps.

### 9.5 Retention, replay, and recovery are connected but distinct

- **Retention** controls how long records remain available in the broker.
- **Replay** is the act of reading available historical records again.
- **Recovery** is the process of returning a consumer or derived system to a correct operating state after a disruption.

Longer retention helps only if the consumer can read and process the required history before it expires and if replay is safe for the downstream application. Replay can create duplicate side effects unless the processing design accounts for them. Topic 4 covers state and delivery semantics; Topic 5 covers CDC and replay planning; Topic 7 covers late events, lag, and failure modes.

### 9.6 Vendor-neutral design checklist

Before finalizing a product-specific configuration, verify from current official product documentation and tests:

- ordering scope and guarantees;
- partition assignment and key hashing/routing;
- maximum practical partition count and per-partition overhead;
- consumer-group assignment and rebalancing behavior;
- offset and progress storage semantics;
- retention and deletion rules;
- replication, acknowledgements, and failover;
- compression and storage accounting;
- quotas, message-size limits, and throughput constraints;
- security, authorization, encryption, and audit controls;
- operational metrics, alert thresholds, and upgrade behavior.

This lesson does not prescribe a particular broker product or imply that all products behave identically.

## 10. Industry examples and failure scenarios

### 10.1 Banking risk events

**Fictional example:** Northbridge Bank publishes account activity events for a risk service and operational analytics consumers.

- Topic: `account-activity-events`.
- Candidate key: `account_id` if per-account ordering is required.
- Separate groups: `risk-engine`, `operations-analytics`, and `warehouse-loader`.
- Retention: selected from the maximum outage, catch-up time, replay needs, and policy requirements—not an arbitrary default.
- Replication: selected after defining durability and availability objectives and checking product semantics.

Failure scenario: one high-volume account produces a disproportionate number of events and its partition falls behind. The team should detect skew and lag, then determine whether the key distribution matches the business ordering need. Splitting that account across keys may improve throughput but can break per-account ordering unless the business logic is redesigned.

### 10.2 E-commerce order lifecycle

An e-commerce platform publishes order lifecycle events. A key such as `order_id` may be appropriate when events for one order must be processed in partition order. A separate `payment-events` topic may be justified by a distinct contract, security boundary, retention need, or ownership.

Failure scenario: a consumer group is sized for normal traffic but an event sale creates a large burst. Lag increases even though the broker accepts records. The team should compare arrival rate with processing rate, inspect partition distribution, and test whether the consumer fleet and downstream services can catch up.

### 10.3 Internet of Things (IoT) telemetry

A fleet of devices publishes telemetry. `device_id` may be a sensible key if per-device sequence matters. However, a single malfunctioning device can emit an extreme volume and create a hot partition. If strict per-device ordering is not needed, a different distribution strategy may be appropriate, but it must be chosen against the actual consumer semantics.

Failure scenario: retention is set to 24 hours, but a consumer is offline for 20 hours and then can process only slightly faster than the live arrival rate. It may not catch up before older data expires. Retention, outage tolerance, and catch-up capacity must be designed together.

### 10.4 Common failure scenarios

| Failure or design defect | Likely symptom | Architectural response |
|---|---|---|
| Constant or poorly distributed key | One hot partition, uneven lag, long tail latency | Revisit key against ordering needs; measure per-key and per-partition rates |
| Too few partitions | Limited consumer parallelism, throughput bottleneck | Benchmark capacity and add partitions only after checking routing and ordering impact |
| Excessive partition count | Metadata and operational overhead; complex rebalancing | Use measured workload needs; avoid partition inflation without evidence |
| Retention too short | Consumer’s required offset has expired; incomplete recovery/replay | Recalculate outage + catch-up + replay window and consider archive |
| Retention too long without capacity plan | Storage pressure, cost growth, disk alerts | Estimate logical and replicated bytes, measure compression, set reserve and alerts |
| Replica/failure-domain assumptions wrong | Data or availability risk during a correlated failure | Verify placement, acknowledgement, failover, and product-specific failure model |
| Frequent consumer restarts | Rebalancing churn and growing lag | Stabilize deployments and resource limits; test assignment behavior |
| Consumer group shares one identity unintentionally | Applications interfere with each other’s progress or work assignment | Give independent applications independent group identities when each must read the full stream |
| Assumed global ordering across partitions | Inconsistent cross-partition sequence | Define the actual ordering invariant and use explicit coordination if global order is truly required |
| Topic mixes incompatible event contracts | Consumers break as payloads diverge | Separate streams or enforce a versioned compatible contract |

## 11. Hands-on exercises with deliverables and validation criteria

All values below are illustrative exercise inputs, not universal benchmarks or repository requirements.

### Exercise A — Design a topic and key strategy

**Inputs**

A fictional order platform emits:

- `OrderCreated`
- `OrderAddressChanged`
- `OrderCancelled`
- `PaymentAuthorized`
- `PaymentFailed`

The order service requires per-order lifecycle ordering. The payment service is owned by a different team and has stricter access requirements. No global order across all orders is required.

**Tasks**

1. Propose topic boundaries and explain why.
2. Select a key for each topic.
3. State the required ordering scope for each topic.
4. Identify one risk in the key choice and how you would test it.
5. List the topic metadata you would document (owner, contract, expected rate, retention rationale, access).

**Deliverable**

A topic design table with columns: topic, event types, owner, key, ordering scope, consumer groups, retention rationale, and risks.

**Validation criteria**

- Topic boundaries are tied to contract, ownership, access, or retention—not only convenience.
- The order key preserves the stated per-order ordering requirement.
- The design does not claim global order without a mechanism to provide it.
- The payment access requirement is addressed.
- At least one skew or hot-key test is included.

### Exercise B — Partition and consumer capacity estimate

**Inputs**

- Peak rate: 18,000 events/s.
- One consumer instance has a measured sustainable rate of 3,000 events/s on the representative workload.
- Planning utilization: 75%.
- Candidate topic partition count: 8.
- Ordering is required per customer; no global ordering is required.
- Assume for the first pass that load is balanced across keys and downstream dependencies do not bottleneck.

**Tasks**

1. Calculate the planning capacity per consumer.
2. Estimate the number of consumer instances needed by rate.
3. Compare that number with the candidate partition count.
4. Explain what the estimate does not prove.
5. Propose a validation test for customer-key skew.

**Deliverable**

A calculation sheet and a short partition-count recommendation.

**Validation criteria**

- Planning capacity is calculated as `3,000 × 0.75 = 2,250 events/s`.
- Estimated consumers are `18,000 ÷ 2,250 = 8` instances.
- Eight partitions could support eight partition assignments in a common group model, but do not guarantee balanced work or sufficient broker capacity. Eight consumers at the calculated planning rate exactly match the stated peak rate; this baseline has no spare consumer capacity for a worker failure or additional burst. If N+1 resilience or further headroom is required, increase tested capacity and/or partition count accordingly.
- The recommendation explicitly says the estimate depends on representative benchmarking and balanced keys.
- A test includes a highly active customer and reports per-partition traffic and lag.

### Exercise C — Retention storage estimate

**Inputs**

- Average event rate: 2,000 events/s.
- Average encoded record size: 3 KiB = 3,072 bytes.
- Retention: 48 hours.
- Replication factor: 2.
- Ignore compression and overhead for the baseline.

**Tasks**

1. Calculate events per day and events over 48 hours.
2. Calculate logical payload bytes for one copy.
3. Convert the result to decimal TB and approximate TiB.
4. Calculate the replicated payload estimate.
5. List at least five reasons actual provisioned storage will differ.

**Deliverable**

A transparent calculation with units and a capacity caveat.

**Validation criteria**

- Events/day = `2,000 × 86,400 = 172,800,000`.
- Events over 48 hours = `172,800,000 × 2 = 345,600,000`.
- Logical bytes = `345,600,000 × 3,072 = 1,061,683,200,000 bytes`.
- Logical size is about **1.062 TB decimal** or **0.966 TiB**.
- Two-copy payload estimate is `2,123,366,400,000 bytes`, about **2.123 TB decimal** or **1.932 TiB**, before overhead.
- Caveats include compression, headers/keys, indexes/metadata, peak rate, replica placement, retention/deletion behavior, filesystem reserve, and other product-specific storage costs.

### Exercise D — Retention and catch-up feasibility

**Inputs**

- A consumer is offline for 4 hours.
- Live arrival rate is 4,000 events/s.
- After restart, the consumer can process 5,000 events/s.
- Retention is 12 hours.
- Assume constant rates and event costs for the simplified calculation.

**Tasks**

1. Calculate the event backlog at restart.
2. Calculate net catch-up rate while new events continue to arrive.
3. Estimate time to drain the backlog.
4. Explain why the answer is only an approximation.
5. Decide whether 12-hour retention appears sufficient under the simplified assumptions, and identify a safety margin or test you would require.

**Deliverable**

A recovery feasibility note with calculations and assumptions.

**Validation criteria**

- Backlog = `4,000 × 4 × 3,600 = 57,600,000 events`.
- Net catch-up rate = `5,000 − 4,000 = 1,000 events/s`.
- Drain time = `57,600,000 ÷ 1,000 = 57,600 seconds = 16 hours`.
- The simplified drain time exceeds the remaining retention window, so the design is not safe under these assumptions without changing capacity, retention, or recovery strategy.
- The explanation notes constant rates, uniform event cost, and no other bottlenecks are assumed.

### Exercise E — Write a product-neutral architecture decision

**Inputs**

A risk stream has a p95 end-to-end target defined in Topic 1. The design needs per-account order, two independent consumer applications, and enough retention to recover from a long weekend outage. The broker product has not yet been selected.

**Tasks**

Write an ADR with:

- Context and measurable requirements.
- Topic and key strategy.
- Candidate partition-sizing method and assumptions.
- Independent consumer-group design.
- Retention and replay rationale.
- Replication/failure requirements that need product verification.
- Alternatives, trade-offs, validation plan, and revisit conditions.

**Deliverable**

A 400–700 word ADR.

**Validation criteria**

- It separates requirements from assumptions.
- It avoids product-specific guarantees before selection.
- It explains the ordering scope and why the key supports it.
- It calculates or estimates retention from outage plus catch-up needs.
- It includes load, skew, failure, and end-to-end latency validation.

## 12. Common mistakes and misconceptions

1. **“A topic is a partition.”** A topic is a logical stream; it may contain multiple partitions.
2. **“The broker guarantees global order.”** In common partitioned-log systems, order is scoped to each partition unless an additional mechanism provides a wider order.
3. **“More partitions always mean more throughput.”** More partitions can increase parallelism, but can also increase overhead and cannot fix a hot key or downstream bottleneck.
4. **“Any key is fine.”** Key choice affects ordering groups and load distribution. A constant key can create a hot partition.
5. **“Use a unique event ID as the key for best distribution.”** That may distribute records but can destroy the per-entity ordering required by the consumer.
6. **“All consumers should share one group.”** Independent applications that each need the full stream generally need independent group identities.
7. **“Adding consumers always increases parallelism.”** In common partition-assignment models, useful parallelism for one group is bounded by partition count.
8. **“Retention equals backup.”** Retention makes records available for a defined window; it is not necessarily a long-term archive or backup strategy.
9. **“Three replicas guarantee no data loss.”** Replica count alone does not define acknowledgement, consistency, failure domains, or failover semantics.
10. **“A 24-hour retention period means any 24-hour outage is recoverable.”** The consumer must also catch up before required records expire; backlog drain time matters.
11. **“The average event size is enough for final capacity.”** Real payload distributions, headers, compression, metadata, peak traffic, and operational reserve matter.
12. **“Partition count can be changed without consequences.”** Key-to-partition mapping and ordering assumptions may change; check product behavior and plan migration.
13. **“Broker throughput proves the end-to-end SLO.”** Producer, broker, consumer, and downstream stages all contribute to the latency budget.
14. **“Vendor-neutral concepts imply identical product behavior.”** The concepts are general; exact limits, offsets, retention, replication, and rebalancing semantics must be verified for the selected product.

## 13. Knowledge-check questions with answers or explanations

1. **What is the difference between a producer and a consumer?**  
   A producer publishes events; a consumer reads and acts on them.

2. **Why does a topic have partitions?**  
   Partitions divide the log into independent ordered sequences, enabling storage distribution and parallel consumption.

3. **What is the usual scope of ordering in a partitioned-log system?**  
   Within a partition. There is no automatic total order across all partitions.

4. **Why might `account_id` be a better key than a constant string?**  
   It can preserve per-account routing/order while spreading different accounts across partitions. A constant key can map all records to one hot partition.

5. **When could `account_id` still be a poor key?**  
   If one account generates disproportionate traffic, or if the consumer does not need account-level grouping/order and another strategy distributes the load better.

6. **What is a consumer group?**  
   A cooperating set of consumers sharing topic-reading work and a group progress model in common systems.

7. **Why use two independent consumer groups for the same topic?**  
   Each application can read the full stream at its own pace and track its own progress.

8. **What usually limits partition-level parallelism within one consumer group?**  
   The number of partitions, along with available consumer instances and other resource bottlenecks.

9. **What happens during rebalancing?**  
   Partition assignments are redistributed as group membership or assignment conditions change; processing may pause or lag may increase depending on the system.

10. **What information is needed for a first-order retention storage estimate?**  
    Average event rate, average encoded record size, retention duration, and replication factor for replicated storage; overhead and compression assumptions are also needed for capacity planning.

11. **Using the worked example, what is the unreplicated payload size for 5,000 events/s, 2 KiB each, retained for 72 hours?**  
    5,000 × 86,400 × 3 × 2,048 = 2,654,208,000,000 bytes, approximately 2.654 TB decimal.

12. **Why is the actual disk requirement different from the baseline calculation?**  
    Compression, headers, metadata, indexes, segment management, replication implementation, peak rates, reserve, and product-specific behavior affect storage.

13. **Does a replication factor of 3 specify a complete durability guarantee?**  
    No. Acknowledgement policy, replica placement, failover, consistency, and failure scenarios must also be defined.

14. **Why might a long retention period still be insufficient?**  
    A consumer may not have enough net processing capacity to catch up before the oldest required records expire.

15. **How does this topic connect to Topic 1?**  
    Producer acknowledgement, broker queueing, consumer wait, replication, and rebalancing can consume part of the end-to-end latency budget. Broker design must be tested against that objective.

16. **Which later topics deepen the concepts introduced here?**  
    Topic 3 covers event time and watermarks; Topic 4 covers state and delivery semantics; Topic 5 covers CDC and replay; Topic 7 covers lag, late events, and failures.

## 14. Summary, mastery criteria, and completion checklist

### Key takeaways

- A broker decouples producers and consumers and can retain events for a configured window.
- A topic is a logical stream; partitions are ordered log sequences within it.
- Ordering is generally within a partition, not global across all partitions.
- Keys should reflect the entity or ordering group required by the business while considering distribution and hot-key risk.
- Independent consumer applications generally use independent consumer groups when each needs the full stream.
- In common partitioned-log systems, partition count bounds useful partition-level parallelism for a consumer group.
- Partition sizing requires measured workload rates, processing capacity, key distribution, ordering constraints, and operational overhead.
- Retention must support outage, catch-up, replay, and policy requirements; a simple byte estimate is only a baseline.
- Replication can improve resilience, but its guarantees depend on product semantics, acknowledgement policy, and failure-domain placement.
- Topic and partition choices affect the latency budget, replay window, stateful processing, and failure behavior.
- Product-neutral design is not a substitute for verifying current product documentation and testing the actual workload.

### Mastery criteria

You are ready to move to Topic 3 when you can:

- [ ] Explain each core term without relying on a memorized vendor-specific definition.
- [ ] Draw the event flow from producer through topic/partitions to consumer groups.
- [ ] State the ordering scope and explain why partition order is not global order.
- [ ] Choose a key from a stated ordering requirement and identify hot-key risks.
- [ ] Explain consumer groups, independent progress, partition assignment, and rebalancing.
- [ ] Estimate consumer capacity and compare it with partition count, including assumptions and limits.
- [ ] Calculate a retention storage baseline with units and replication factor.
- [ ] Explain why retention and catch-up capacity must be considered together.
- [ ] List the product-specific replication and offset semantics that need verification.
- [ ] Connect broker design to the Topic 1 end-to-end latency objective.
- [ ] Complete at least three exercises with calculations, assumptions, and validation criteria.
- [ ] Record a concise architecture decision with alternatives, risks, and a test plan.

**Completion gate:** Save the topic design table, key/partition rationale, sizing calculation, retention estimate, and ADR together as your Topic 2 deliverables. A peer should be able to identify the ordering invariant, reproduce the arithmetic, and see which assumptions still require measurement.

## 15. Exact repository-relative cross-references

These paths follow the supplied overall project tree and module roadmap. They identify learning dependencies; they do not imply that every referenced file was read or that an empty topic file already contains lesson content.

### Within `Stage 2D — Data Architecture/09-Streaming-and-Real-Time-Data-Architecture/`

- `01-real-time-use-cases-and-latency-budgets.md` — previous lesson; defines latency and correctness requirements.
- `03-event-time-processing-ordering-and-watermarks.md` — next lesson; event time, ordering, windows, and watermarks.
- `04-stream-processing-state-and-delivery-semantics.md` — state, checkpoints, and delivery semantics.
- `05-cdc-event-backbones-and-replay.md` — CDC, event backbones, and replay.
- `06-real-time-serving-stores-and-materialized-views.md` — serving results and materialized views.
- `07-late-events-backpressure-and-stream-failure-modes.md` — late events, lag, backpressure, and failure modes.
- `practice-questions.md` — module review questions.
- `README.md` — module entry point.
- `roadmap-Streaming-and-Real-Time-Data-Architecture.md` — module source of truth and learning sequence.
- `Projects/09-real-time-risk-monitoring-architecture.md` — integrated module project.

### Earlier Stage 2D modules

- `../02-Requirements-Constraints-and-Architecture-Decisions/03-data-volume-velocity-variety-and-growth-estimation.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/04-latency-throughput-freshness-and-availability-targets.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/06-architecture-trade-offs-and-decision-criteria.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/07-architecture-decision-records-adrs.md`
- `../03-Data-Architecture-Patterns-and-Reference-Architectures/06-event-driven-and-data-sharing-patterns.md`
- `../04-Conceptual-Logical-and-Physical-Data-Modeling/06-event-modeling-and-domain-driven-design.md`
- `../04-Conceptual-Logical-and-Physical-Data-Modeling/07-schema-evolution-and-backward-compatibility.md`
- `../06-Data-Integration-and-Interoperability/04-streaming-events-and-message-contracts.md`
- `../06-Data-Integration-and-Interoperability/05-data-contracts-schema-registry-and-compatibility.md`
- `../06-Data-Integration-and-Interoperability/07-idempotency-deduplication-and-reconciliation.md`
- `../06-Data-Integration-and-Interoperability/08-integration-pattern-selection-and-failure-handling.md`
- `../07-Enterprise-Data-Platform-and-Lakehouse-Architecture/08-platform-service-levels-and-product-thinking.md`

The next topic should build on the partition-ordering concepts here to study event time, ordering, and watermarks. Keep the boundary between lessons clear: this file introduces the broker and its design constraints; later files develop stateful computation, CDC/replay, serving, and failure recovery.
