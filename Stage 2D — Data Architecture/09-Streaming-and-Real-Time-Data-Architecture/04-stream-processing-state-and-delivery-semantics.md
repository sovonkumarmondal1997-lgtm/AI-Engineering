# Stream Processing, State, and Delivery Semantics

> **Purpose:** Understand how stream processors transform events, when they must remember information between events, how state and processing progress are recovered after failures, and what at-most-once, at-least-once, and exactly-once guarantees do—and do not—mean.

> **Roadmap and source caveat:** This is Topic 4 in `Stage 2D — Data Architecture/09-Streaming-and-Real-Time-Data-Architecture/`. The module-specific roadmap is the source of truth for scope and sequence. It explicitly notes that topic files were empty when the roadmap was authored and that detailed scenarios, targets, and exercises are recommended learning guidance or illustrative assumptions, not requirements already documented in those files. Product-specific behavior must be verified for the selected processor, broker, and sink.

---

## 1. Title and purpose

A stream processor reads events and transforms them into useful results: filters, enriched records, counts, risk signals, account totals, or updates to a serving store. Some transformations can handle each event independently. Others need to remember what happened before.

That remembered information is **state**. State introduces architectural questions:

- What is remembered, and for how long?
- How is state partitioned across keys?
- What happens if a worker crashes after updating state but before publishing output?
- How are state and input progress restored consistently?
- Can an event be processed more than once?
- Can an event be lost?
- Does a processor-level guarantee extend to the database, alert, or payment effect downstream?

The goal of this topic is to make those boundaries explicit. “Exactly once” is not a universal promise that every business effect across every system will happen once. Its meaning depends on the source, processor, state/checkpoint mechanism, sink, transaction boundary, and failure model.

## 2. Module position and prerequisites

The recommended sequence is:

1. `01-real-time-use-cases-and-latency-budgets.md` — measurable latency, freshness, and correctness objectives.
2. `02-event-brokers-topics-partitions-and-retention.md` — topics, keys, partitions, offsets, retention, and replay window.
3. `03-event-time-processing-ordering-and-watermarks.md` — event time, windows, watermarks, and late-event policies.
4. `04-stream-processing-state-and-delivery-semantics.md` — **this lesson**: state, checkpoints, recovery, and guarantee boundaries.
5. `05-cdc-event-backbones-and-replay.md` — CDC, event backbones, and replay design.
6. `06-real-time-serving-stores-and-materialized-views.md` — serving stores and materialized views.
7. `07-late-events-backpressure-and-stream-failure-modes.md` — lag, retries, backpressure, and failure analysis.

### Prerequisites

- Topic 2: partitioning, keys, consumer groups, offsets, retention, and replay.
- Topic 3: event time, windows, watermarks, late events, and provisional/corrected results.
- Conceptual understanding of event contracts, unique event IDs, retries, idempotency, and reconciliation.

Relevant repository-relative prerequisite:

- `../06-Data-Integration-and-Interoperability/07-idempotency-deduplication-and-reconciliation.md`

Other useful references:

- `../02-Requirements-Constraints-and-Architecture-Decisions/04-latency-throughput-freshness-and-availability-targets.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/06-architecture-trade-offs-and-decision-criteria.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/07-architecture-decision-records-adrs.md`
- `../06-Data-Integration-and-Interoperability/04-streaming-events-and-message-contracts.md`
- `../06-Data-Integration-and-Interoperability/05-data-contracts-schema-registry-and-compatibility.md`

## 3. Learning objectives

By the end of this lesson, you should be able to:

1. Distinguish stateless from stateful processing and identify what each requires operationally.
2. Explain keyed state and why key choice affects correctness, distribution, and scaling.
3. Describe state lifecycle decisions for unbounded streams, including expiration and cleanup.
4. Explain conceptually how checkpoints relate processor state to input progress.
5. Describe recovery after a crash and identify where duplicates or lost effects can occur.
6. Distinguish at-most-once, at-least-once, and exactly-once terminology.
7. Separate delivery guarantees, processing guarantees, and end-to-end business-effect guarantees.
8. Explain how retries, duplicate events, idempotency, and deduplication affect correctness.
9. Compare recovery choices across correctness, latency, throughput, and operational complexity.
10. Define the guarantees required at each boundary and identify what must be verified in product documentation and tests.

## 4. Readiness check

Try these questions before reading the lesson.

1. Is a filter that evaluates each event independently stateless or stateful?
2. Why does a running total per account need state?
3. What can go wrong if a worker saves its new state but loses its input progress—or advances input progress without saving the corresponding state?
4. What does at-least-once processing imply about duplicates?
5. Does exactly-once processing inside a stream engine automatically mean a downstream email, HTTP call, or database mutation happens once?
6. How can an output operation be made safer to retry?

**Answers**

1. Stateless, assuming the filter does not depend on earlier events or mutable external data.
2. It must remember the prior total for each account and update it when new events arrive.
3. A mismatch can cause replay without a matching state update, or skipped input after progress has advanced too far; the exact failure depends on the implementation.
4. An event may be processed more than once, so duplicate effects are possible unless handled.
5. No. The end-to-end effect depends on the sink, transaction boundary, retries, and idempotency.
6. Use a stable operation/event ID and an atomic deduplication or idempotency mechanism at the effect boundary, or a transaction that truly covers the relevant state and output.

## 5. Beginner foundations: stateless and stateful processing

### 5.1 What is stream processing?

A stream processor continuously consumes events and applies logic as they arrive. It may validate, filter, transform, enrich, aggregate, join, detect patterns, or publish results.

A simplified flow:

```text
Event source
    |
    v
Broker / topic
    |
    v
Stream processor  <---->  State store (when logic needs memory)
    |
    v
Output / sink
```

The broker transports and retains events according to its own semantics (Topic 2). The processor applies business logic. A sink may be a database, serving store, another topic, an API, or another system. The guarantees of one component do not automatically transfer to the others.

### 5.2 Stateless processing

A transformation is **stateless** when the result for an event depends only on that event and fixed configuration—not on remembered earlier events.

Examples:

- validate a required field;
- discard records that fail a schema check;
- rename a field;
- convert a temperature unit;
- route a record based on its event type.

Conceptual example:

```text
For each event:
    if event.amount < 0:
        route to invalid-events
    else:
        emit normalized(event)
```

This is framework-neutral pseudocode, not a runnable API. It assumes the decision depends only on the current event.

**Why it matters:** stateless operators are often easier to scale and recover because they do not need to restore a per-key aggregate or window history. They still need correct input progress and output behavior; stateless does not mean failure-proof or automatically exactly-once.

**What can go wrong:**

- retries can publish the same normalized record twice;
- a supposedly fixed lookup table may actually change over time;
- a transformation may depend on a mutable external service, making it stateful in practice or non-deterministic;
- invalid records may be dropped without a traceable policy.

**Useful when:** validating, filtering, or transforming each record independently.

### 5.3 Stateful processing

A transformation is **stateful** when it needs information from previous events or a maintained context to compute the next result.

Examples:

- running total per account;
- count of failed logins in the last ten minutes;
- last known device status;
- deduplication of recent event IDs;
- joining events that arrive at different times;
- a windowed risk score.

State can be a counter, map, aggregate, session, timer, buffered event, or other maintained data structure. It may live in memory, a local state store, a remote database, or an engine-managed state backend.

**Why it matters:** stateful processing supports richer business logic, but requires lifecycle, consistency, recovery, and capacity decisions.

### 5.4 Keyed state

**Keyed state** is state associated with a key or entity. For example, an account risk processor might maintain a separate running exposure total for each `account_id`.

```text
Input event: {account_id: "A17", amount: 50}

State before:
  A17 -> exposure 120
  B42 -> exposure 300

Update:
  A17 -> exposure 170

State after:
  A17 -> exposure 170
  B42 -> exposure 300
```

The key should represent the entity or grouping whose state must be updated together. Topic 2 explains how keys and partitions influence routing. A poor key can cause hot partitions; a key that changes between events can split what the business thinks is one entity into multiple state entries.

**Keyed state trade-offs:**

- more distinct keys mean more state and metadata;
- hot keys can bottleneck one partition or worker;
- state may need to move when partition assignments change;
- missing, malformed, or inconsistent keys can corrupt aggregation semantics;
- a key change is a data migration and correctness concern, not just a tuning change.

### 5.5 Unbounded streams need state lifecycle decisions

A stream can continue indefinitely. If a processor stores every key, event ID, session, or partial aggregate forever, state can grow without bound.

For each state type, decide:

- **Purpose:** what future decision depends on this state?
- **Key cardinality:** how many keys may exist?
- **Lifetime:** how long is the state useful?
- **Expiration:** what event-time or processing-time condition makes it safe to remove?
- **Late events:** can a late event legitimately need expired state?
- **Recovery:** must state be persisted or rebuilt from retained input?
- **Privacy/compliance:** does state contain data that must expire or be deleted?
- **Capacity:** what are expected size, growth, and peak state requirements?
- **Observability:** how will state size, expiration, and cleanup failures be monitored?

Examples:

| State | Possible lifecycle policy | Important caveat |
|---|---|---|
| Count of failed logins in a 10-minute window | Expire data when the window is no longer eligible for updates | Must account for late events and watermark policy from Topic 3 |
| Deduplication IDs | Retain IDs for a defined retry/replay horizon | If duplicates can arrive after expiry, they may be counted again |
| Last known device status | Retain until superseded or until a domain-defined expiry | Some devices may be silent without actually being offline |
| Daily account aggregate | Keep the current day plus a defined correction/reconciliation period | Late corrections may require reopening or recomputing old periods |
| Join buffer for matching events | Expire after a domain-defined waiting interval | Too-short expiry loses valid matches; too-long expiry increases state |

Expiration is a correctness decision. Deleting state too early can change results; retaining it too long can cause storage growth, cost, and slower recovery.

## 6. Intermediate state, keys, windows, checkpoints, and recovery

### 6.1 State for event-time windows

Topic 3 introduced event-time windows and watermarks. A stateful windowed operator may maintain partial aggregates until the window can be emitted and, depending on the policy, updated for late events.

For a five-minute event-time window, the processor may need to remember:

- the current aggregate;
- window identity and boundaries;
- any metadata needed to process late events;
- whether an initial result has already been emitted;
- whether the window remains eligible for updates.

This is a conceptual list; a specific engine may store additional metadata or represent it differently. The state-retention policy must align with Topic 3’s watermark and allowed-lateness policy. If state is cleaned up before the promised correction period ends, late events cannot update the result through that state.

### 6.2 State store

A **state store** is the mechanism used to keep and access the processor’s maintained data. It may be local, remote, embedded, replicated, or managed by a stream-processing framework.

The design questions include:

- Is state in memory, on local disk, or in a remote system?
- How is it partitioned and associated with input keys?
- How is it backed up or checkpointed?
- What happens when a worker or machine fails?
- What is the cost of restoring state?
- Does state need to be rebuilt from input, and is the necessary input still retained?
- How does state size affect latency and throughput?

Do not infer a durability or consistency guarantee from the phrase “state store.” The implementation and configuration determine the behavior.

### 6.3 Checkpoints: state and progress must agree

A **checkpoint** is a recovery point that records enough information to restore a processor to a consistent point in its computation. Depending on the system, it can include operator state, source positions/offsets, timers, window state, and other recovery metadata.

The key concept is consistency between **processing state** and **input progress**.

Suppose the processor has consumed events through position 100 and its running total is 5,000. A valid recovery point needs a consistent relationship between that total and the input history represented by the saved position. If the saved total corresponds to event 100 but recovery resumes from event 95, events 96–100 might be applied twice. If progress is saved at 100 but the total only reflects through event 95, events 96–100 might be skipped from the aggregate.

This simplified example illustrates the mismatch risk; actual checkpoint protocols coordinate components differently.

```text
Consistent checkpoint:
  Input position: through event 100
  Processor state: includes exactly the effects of events through 100
  Recovery: resume from the matching position and state

Inconsistent recovery point:
  Input position: through event 100
  Processor state: only includes events through 95
  Risk: events 96–100 may be skipped from the aggregate
```

A checkpoint may be coordinated with source offsets and, in some systems, with sink transactions. But do not assume every processor, source, and sink participates in one atomic transaction. Verify the documented checkpoint protocol and sink integration.

### 6.4 Recovery after a failure

A conceptual recovery sequence is:

1. Detect that a worker or processor failed.
2. Determine the last valid recovery point.
3. Restore state associated with that point.
4. Restore source positions or offsets consistently with that state.
5. Resume processing from the recovery position.
6. Handle any outputs that may have been emitted but not safely committed.
7. Verify lag, state consistency, duplicate behavior, and output correctness.

This is a conceptual flow, not a universal protocol. Systems differ in when they checkpoint, how they restore state, how they coordinate source progress, and how they commit outputs.

Recovery time depends on state size, checkpoint frequency, checkpoint duration, source retention, replay throughput, and sink performance. Frequent checkpoints can reduce the amount of work repeated after a crash, but checkpointing itself consumes resources and can add latency. Less frequent checkpoints may improve normal throughput but increase recovery work.

### 6.5 Retries and the duplicate-effect window

A common failure pattern is:

1. Read an event.
2. Update local state.
3. Publish an output or call an external sink.
4. Fail before the system records progress or confirms the output.
5. Retry the event after restart.

Depending on which steps were durable and coordinated, the retry may repeat the output effect. If the output is not idempotent, the business effect can happen twice.

The reverse ordering can also fail: if input progress advances before the output effect is durable, a crash may cause the effect to be lost. The solution is not simply “choose the right order” in every system; it is to define and implement the transaction boundary, recovery protocol, and sink behavior.

### 6.6 Recovery and replay: preview

A processor may recover from its checkpoint and resume from retained broker records. If state must be rebuilt, it may replay a larger input history. Replay feasibility depends on Topic 2 retention, source availability, event volume, processing capacity, and whether the sink can safely handle repeated output attempts.

Topic 5 (`05-cdc-event-backbones-and-replay.md`) develops CDC and replay planning in detail. Topic 7 (`07-late-events-backpressure-and-stream-failure-modes.md`) develops lag, backpressure, and failure diagnosis. This lesson introduces the dependency without replacing those topics.

## 7. Delivery semantics and guarantee boundaries

### 7.1 Three common terms

The following table uses common conceptual definitions. Products and frameworks may define the scope of their guarantee differently; read the selected product’s documentation carefully.

| Term | Common meaning | What it helps with | What it does not automatically guarantee |
|---|---|---|---|
| **At-most-once** | An input event is processed zero or one times; a failure may cause it to be skipped or lost | Avoiding duplicate processing at the cost of possible loss | No data loss; correct state; successful downstream effect |
| **At-least-once** | The system retries or replays so an event is processed one or more times under its stated recovery assumptions | Reducing loss when retries/recovery work as designed | No duplicates; idempotent effects; unlimited recovery after retention expires |
| **Exactly-once processing/effect within a defined boundary** | The system coordinates state and progress so repeated attempts do not produce repeated committed effects within the specified boundary | Consistent state and outputs under supported failure conditions | A universal exactly-once business effect across arbitrary external systems |

These terms describe different possible contracts, not a ranking where “exactly once” is always the best. A system may choose at-most-once when loss is acceptable and latency is critical, or at-least-once with idempotent sinks when duplicates can be handled reliably.

### 7.2 Delivery, processing, and end-to-end effect are different

Use these boundaries explicitly:

1. **Transport/delivery:** Was the event delivered to the next component? What can the broker or source guarantee?
2. **Processing:** Was the event’s logic applied once, at least once, or at most once within the processor’s boundary?
3. **State consistency:** Does the recovered state match the input progress it represents?
4. **Sink write:** Was an output write committed? Can it be repeated safely?
5. **Business effect:** Did the real-world action occur once—for example, one payment, one email, one account debit, or one alert?
6. **End-to-end workflow:** Do all of the source, processor, sink, and external effects compose into the intended outcome under retries and failures?

A guarantee at one boundary does not automatically propagate to the next. A processor can calculate an output exactly once inside its own transactional state while an external HTTP endpoint receives the request twice. Conversely, an at-least-once input can still produce a single durable database row if the sink uses a stable idempotency key and enforces it atomically.

### 7.3 What “exactly once” must specify

Whenever someone says “exactly once,” ask:

- Exactly once **what**—input processing, state transition, output record, database mutation, payment, notification?
- Within **which components** and transaction boundary?
- For which failures—worker crash, broker loss, network partition, sink timeout, process restart?
- What source and sink integrations are supported?
- Are external side effects inside the transaction?
- What is the behavior when a request times out after the sink committed but before the caller received the response?
- How are retries, duplicates, and replay handled?
- What happens after state or deduplication records expire?
- What are the throughput, latency, and operational costs?

A product-specific exactly-once feature may coordinate input offsets, processor state, and output records to a supported sink under stated conditions. It cannot magically make an arbitrary email server, HTTP endpoint, or unrelated database participate in the same atomic transaction.

### 7.4 Duplicate events and idempotency

A **duplicate event** is the same logical event delivered or observed more than once. Duplicates can arise from producer retries, consumer retries, replay, at-least-once delivery, or upstream systems emitting the same business event again.

An operation is **idempotent** if applying the same operation repeatedly has the same final effect as applying it once, within its stated scope.

Examples:

- Setting `account_status = "FROZEN"` to the same value can be idempotent.
- Incrementing `account_total` by 50 is not idempotent if repeated.
- Replacing a record by a stable key and version may be idempotent if version rules are enforced atomically.
- Sending an email is generally not idempotent unless the receiving system supports deduplication or an equivalent mechanism.

Idempotency needs a precise identity and scope. A stable `event_id` can identify a logical event; a stable `operation_id` can identify a business action. The sink must enforce the idempotency rule atomically with the effect, or duplicates can still race.

### 7.5 Deduplication: useful but bounded

Deduplication tracks identifiers already seen and suppresses repeated events. It is useful when the same logical event can arrive more than once, but it has costs and limits:

- deduplication state consumes storage;
- state must have a retention period;
- duplicates arriving after the deduplication record expires may be applied again;
- a missing or unstable ID makes reliable deduplication difficult;
- two different events sharing an ID can cause legitimate data to be dropped;
- a separate “check then write” operation can race unless enforced atomically.

Deduplication is not a universal substitute for idempotent business operations. Design the event identity, deduplication retention, and sink transaction boundary together.

## 8. Worked duplicate/retry/idempotency example

All values below are illustrative. This is a framework-neutral scenario, not a product-specific API example.

### 8.1 Scenario: account exposure total

A processor consumes a transaction event:

```text
event_id = "TX-8841"
account_id = "A17"
amount = 50
```

The current exposure total for account A17 is 1,000. The processor adds 50 and writes a new total of 1,050 to a database.

### 8.2 Failure without idempotency or a coordinated transaction

| Step | Action | Durable result |
|---:|---|---|
| 1 | Processor reads `TX-8841` | Input position has not yet been safely advanced |
| 2 | Processor calculates total 1,050 | In-memory calculation only |
| 3 | Database commits total 1,050 | Database now shows 1,050 |
| 4 | Processor crashes before confirming progress/output coordination | Database commit happened, but the processor may retry the input |
| 5 | Processor restarts and reads `TX-8841` again | Same logical event is processed again |
| 6 | Processor adds 50 again and commits 1,100 | Incorrect double-counted total |

The processor’s retry may be correct from an at-least-once recovery perspective, but the non-idempotent increment created a duplicate business effect.

### 8.3 Mitigation A: sink-enforced idempotency key

Use `event_id` as an idempotency key and enforce the “apply this event once” rule atomically at the database boundary. Conceptually:

```text
PSEUDOCODE — illustrates the required atomic invariant; not runnable SQL/API

BEGIN TRANSACTION

  if event_id has already been applied:
      do not change the exposure total
  else:
      record event_id as applied
      add amount to account exposure

COMMIT
```

Required invariant: **recording the event ID and changing the exposure total must commit atomically**. If they are separate non-atomic operations, a crash between them can still cause a lost or duplicate effect.

With the invariant enforced:

- first attempt applies `TX-8841`: total becomes 1,050 and the event ID is recorded;
- retry sees that `TX-8841` was already applied and does not increment again;
- total remains 1,050.

This mitigation depends on a stable unique event ID, a durable deduplication record, and an atomic sink transaction. It does not automatically deduplicate a logically repeated business action that arrives under a different ID.

### 8.4 Mitigation B: transactional coordination within a supported boundary

Some processing systems can coordinate checkpointed input progress, processor state, and writes to a supported sink using transactions or a two-phase/commit protocol. Under the product’s documented assumptions, a failed attempt can be aborted and retried without exposing duplicate committed output within that boundary.

This is not a generic guarantee for arbitrary external effects. It only applies to the components and failure modes covered by the implementation. Verify the supported source, sink, configuration, and transaction semantics.

### 8.5 Mitigation C: deterministic upsert instead of increment

If the event contains a complete authoritative value or a monotonic version, the sink may use an upsert keyed by account plus version/event identity rather than an unguarded increment. This can make retries safer, but only if version ordering and conflict rules are correct. Replacing an aggregate with an event’s amount is not equivalent to accumulating amounts.

### 8.6 What the example proves—and what it does not

It proves that a retry can repeat a non-idempotent side effect when the output commit and input progress are not coordinated. It does **not** prove that every processor has this failure sequence or that the pseudocode alone provides exactly-once processing. Actual correctness depends on the sink’s atomicity, uniqueness enforcement, checkpoint protocol, retry behavior, and business identity rules.

## 9. Advanced trade-offs and design decisions

### 9.1 State size versus recovery time

Larger state may support longer windows, more keys, richer joins, or longer deduplication horizons. But it can increase checkpoint duration, restore time, storage, network transfer, and memory pressure.

Document:

- expected key cardinality and growth;
- per-key state size or aggregate estimate;
- expiration rules;
- checkpoint size and frequency;
- recovery-time objective;
- whether state can be rebuilt from retained input;
- how state size and checkpoint health are monitored.

### 9.2 Checkpoint frequency and operational overhead

Frequent checkpoints can reduce repeated work after a crash but consume CPU, storage I/O, network bandwidth, and coordination time. Infrequent checkpoints may improve normal throughput but can increase replay and recovery duration.

Choose based on measured requirements, not a universal interval. Benchmark normal throughput and latency with checkpointing enabled, then test restart and recovery under realistic state size and failure conditions.

### 9.3 Guarantee strength versus latency and throughput

Stronger coordination may require durable writes, barriers, transactions, acknowledgements, or sink participation. Those mechanisms can increase latency and reduce throughput in some architectures. At-most-once may be faster but tolerate loss; at-least-once may be simpler but require idempotency; a supported exactly-once boundary may reduce duplicate committed effects but impose compatibility and operational constraints.

The appropriate choice follows business impact:

- If a missed telemetry sample is acceptable, at-most-once may be reasonable for a specific path.
- If every transaction event must be accounted for, loss may be unacceptable; at-least-once with atomic idempotent application or a supported transactional design may be suitable.
- If external actions cannot be made transactional, define compensating actions, idempotency, reconciliation, and audit controls rather than relying on the label “exactly once.”

### 9.4 Event-time state and late corrections

Topic 3 explains that late events may revise window results. If the processor emits an initial aggregate and then accepts a late event, state must remain available long enough to calculate the correction. The output contract must say whether a correction replaces a previous value, retracts an earlier result, or is a separate compensating event.

If the state is deleted when the first result is emitted, the processor may be unable to correct it. If state remains forever, storage grows without bound. Choose a cleanup boundary that aligns with the watermark/allowed-lateness policy and the business correction horizon.

### 9.5 State restoration and source retention

A checkpoint is useful only if the system can restore the required state and input position. If a recovery process needs to replay events that have expired from the broker, recovery may fail unless a durable archive or source-of-truth system can supply them.

Topic 2’s retention window must therefore be compared with:
- the maximum expected outage;
- detection and repair time;
- state restoration time;
- replay/catch-up throughput;
- the correction/reconciliation horizon.

Topic 5 develops replay and CDC design. This topic’s responsibility is to make the state/recovery dependency visible.

### 9.6 Decision record: what to write down

For a production stream processor, record:

1. Which operators are stateless and which are stateful.
2. State key, schema, expected cardinality, lifecycle, and expiration.
3. Window/watermark dependency and late-event policy.
4. Checkpoint/recovery approach and recovery-time objective.
5. Source position and state consistency semantics.
6. Chosen delivery/processing guarantee and its exact boundary.
7. Sink transaction or idempotency mechanism.
8. Event identity and deduplication retention.
9. Duplicate, loss, replay, and reconciliation behavior.
10. Latency/throughput/storage costs and test evidence.
11. Product-specific assumptions still requiring verification.
12. Conditions that trigger a redesign.

## 10. Industry scenarios and failure cases

### 10.1 Banking: transaction exposure

A bank maintains per-account exposure totals. The processor needs keyed state and a reliable update path. A duplicate transaction can inflate exposure and trigger an incorrect risk action.

Design focus:

- stable transaction/event ID;
- state partitioned by account;
- atomic idempotent sink update or a supported transactional boundary;
- reconciliation against the authoritative transaction ledger;
- state recovery and retention aligned with replay needs.

Failure case: a sink commits the increment but the processor times out before acknowledging success. The retry is expected; the sink must prevent the same logical transaction from incrementing twice.

### 10.2 Fraud detection: rolling failed-login count

A fraud processor maintains counts per user or account over an event-time window. It depends on Topic 3’s timestamp and watermark policy. State must be retained while late events can still change the count.

Failure case: state expires before the configured late-event correction period ends. A late failed-login event arrives but cannot update the prior window. The team must align cleanup with the lateness policy or route late events through a separate correction path.

### 10.3 E-commerce: order status projection

A processor consumes order events and updates a current order-status row. Reprocessing the same `OrderShipped` event should not create multiple shipments or send duplicate notifications.

Design focus:

- event identity and order key;
- deterministic state transitions;
- sink-side idempotency;
- version/sequence checks if events may arrive out of order;
- separate treatment for irreversible side effects such as sending an email.

Failure case: the database upsert is idempotent, but an email API call is retried independently. The row may be correct while the customer receives two emails. Guarantees must be considered per effect boundary.

### 10.4 IoT: last-known device state

A processor maintains the last reported state per device. A device may reconnect and replay buffered events. If events are duplicated or arrive out of order, a naïve “last message wins” rule may overwrite a newer state with an older one.

Design focus:

- device key and timestamp/sequence quality;
- ordering and late-event policy;
- deterministic version comparison;
- state expiration for inactive devices;
- recovery and replay behavior.

Failure case: an old buffered “online” event arrives after a newer “offline” event. Event time alone may not be trustworthy if the device clock is skewed; source sequence or authoritative metadata may be needed.

### 10.5 Failure matrix

| Failure | Potential impact | Detection | Design response |
|---|---|---|---|
| Worker crashes after sink commit but before progress is safely committed | Duplicate side effect on retry | Retry counts, duplicate IDs, output reconciliation | Atomic idempotency or supported transactional coordination |
| Progress advances without corresponding state/output durability | Lost aggregate effect | Input/output reconciliation, checkpoint consistency metrics | Consistent checkpoint protocol; validate source/sink integration |
| State expires too early | Late events cannot update prior result | Late-event rejection/correction rate | Align cleanup with watermark and business correction policy |
| State grows without bound | Resource pressure, latency, expensive recovery | State-size growth, checkpoint duration | Explicit TTL/expiry, bounded windows, capacity planning |
| Duplicate event has no stable ID | Cannot reliably identify same logical event | Duplicate pattern analysis, source quality metrics | Add stable identity to contract or define alternate business key |
| Deduplication record expires too soon | Old replay/retry can repeat effect | Duplicate rate after expiry, reconciliation | Match deduplication horizon to retry/replay horizon |
| Sink is not idempotent and cannot join transaction | Duplicate external effect | Sink timeout/retry logs, business reconciliation | Idempotency key, outbox/inbox pattern where appropriate, compensation or reconciliation |
| Recovery requires records beyond broker retention | State cannot be reconstructed from broker alone | Recovery test and retention audit | Longer retention or governed archive/source-of-truth replay path |
| Rebalance changes state ownership | Temporary lag or state restore work | Rebalance events, lag, restore duration | Product-specific state migration/recovery tests |
| Event-time correction arrives after state cleanup | Incorrect final aggregate | Late-event metrics, final-vs-reconciled variance | Explicit correction horizon and historical recomputation path |

## 11. Hands-on exercises with deliverables and validation criteria

All numbers and scenarios are illustrative learning inputs, not universal performance targets or repository requirements.

### Exercise A — Classify stateless and stateful operators

**Inputs**

A stream workflow performs these steps:

1. Reject records with a missing `event_id`.
2. Convert `amount` from cents to a decimal currency amount.
3. Maintain running exposure per `account_id`.
4. Count failed logins in a rolling 10-minute event-time window.
5. Enrich each event using a static, versioned mapping loaded at job startup.
6. Suppress events whose `event_id` was already seen in the last 24 hours.

**Tasks**

- Classify each step as stateless or stateful under the stated assumptions.
- Identify which state requires a lifecycle/expiry policy.
- Explain how changing the static mapping during runtime would affect step 5.
- Identify where Topic 3’s watermark/lateness policy affects step 4.

**Deliverable**

A table with operator, classification, state required, lifecycle policy, and failure risk.

**Validation criteria**

- Steps 1 and 2 are stateless if they depend only on the current record.
- Step 3 is stateful and requires a per-account state lifecycle.
- Step 4 is stateful and depends on event-time window semantics and late-event handling.
- Step 5 can be treated as stateless with fixed startup configuration; mutable runtime lookup introduces a changing external dependency.
- Step 6 is stateful; the deduplication horizon is 24 hours by assumption and must be compared with the retry/replay horizon.

### Exercise B — Trace checkpoint consistency

**Inputs**

A running count is 40 before event E101. Event E101 increments it to 41. The system fails at one of these points:

- Case 1: before state update;
- Case 2: after state update but before a consistent checkpoint;
- Case 3: after state and source progress are safely included in the same recovery point;
- Case 4: source progress is committed but the corresponding state update is not durable.

**Tasks**

- For each case, explain what a correct recovery protocol must do.
- Identify where reprocessing can be safe or unsafe.
- State which details require product-specific documentation.

**Deliverable**

A failure timeline table showing state, source position, expected recovery, and risk.

**Validation criteria**

- Case 1 should resume from a consistent earlier point and apply E101 once.
- Case 2 must restore a consistent earlier checkpoint or another valid coordinated recovery point; otherwise duplicate/lost effects are possible.
- Case 3 should restore the matching state/progress pair and not reapply the committed effect within that boundary.
- Case 4 can skip E101’s effect if progress cannot be rolled back or reconstructed; it demonstrates why progress and state must be coordinated.
- The learner does not claim that all products implement checkpoints identically.

### Exercise C — Retry and idempotency design

**Inputs**

- Account A17’s current exposure is 1,000.
- Event `TX-8841` adds 50.
- The sink commits the total update, but the processor times out before it can confirm the result.
- The processor retries the event.
- No deduplication is present in the initial design.

**Tasks**

1. Calculate the result without idempotency.
2. Propose an idempotency key.
3. State the atomic invariant required at the sink.
4. Explain what happens if the deduplication record and aggregate update are stored in separate, non-atomic operations.
5. Explain why this is not proof of generic exactly-once processing.

**Deliverable**

A failure sequence diagram and a sink contract.

**Validation criteria**

- Without idempotency, the total can become 1,100 rather than the correct 1,050.
- `TX-8841` is a candidate stable idempotency key if it uniquely identifies the logical transaction.
- Recording the ID and updating the aggregate must be atomic for the proposed mitigation.
- Separate non-atomic operations leave a crash window that can produce duplicates or missing effects.
- The guarantee is limited to the sink operation and its documented atomicity/idempotency behavior.

### Exercise D — Choose a guarantee boundary

**Inputs**

A processor reads transaction events and performs three outputs:

- updates a processor-managed aggregate;
- writes an aggregate row to a supported transactional database sink;
- sends an email through an external email API.

The selected processor documents coordinated checkpointing for its own state and a supported sink connector. The email API does not participate in that transaction and has no idempotency-key support.

**Tasks**

- Describe what may be guaranteed within the processor/supported sink boundary, subject to the product documentation.
- Explain why the email effect has a different guarantee boundary.
- Propose an operational design for duplicate emails or uncertain send outcomes.
- List the tests required before claiming a guarantee.

**Deliverable**

A boundary diagram and a short guarantee statement for each output.

**Validation criteria**

- The answer qualifies the guarantee by the processor, connector, configuration, and documented failure model.
- It does not extend the transaction claim to the email API.
- It proposes a realistic alternative such as an outbox plus delivery tracking, a compensating/reconciliation process, or an email provider with idempotency support; it does not claim the outbox alone makes an arbitrary external email effect exactly once.
- It includes crash/timeout tests around each boundary.

### Exercise E — State lifecycle and recovery trade-off

**Inputs**

A fraud processor keeps deduplication IDs for 24 hours. Broker retention is also 24 hours, while a governed archive retains events for 7 days. After a prolonged outage, the team determines it may need to replay 36 hours of events from that archive. These values are illustrative.

**Tasks**

- Identify the mismatch between the 24-hour deduplication horizon and the 36-hour replay horizon.
- Explain why the broker alone cannot supply the full replay range after its retention window, and what could happen if replayed events are older than the retained deduplication records.
- Propose a consistent archive/replay/state-retention policy.
- State which source of truth is used to validate recovered totals.

**Deliverable**

A lifecycle table and recovery decision note.

**Validation criteria**

- The learner notices that a 36-hour replay exceeds the broker’s 24-hour retention, so the full replay must use the archive or another authoritative source.
- The learner notices that the 24-hour deduplication horizon is shorter than the 36-hour replay horizon; replayed events older than retained deduplication records may repeat effects unless the design provides another idempotency or reconciliation control.
- The design aligns archive retention, replay scope, deduplication horizon, recovery-time assumptions, and reconciliation.
- The recovery source and correctness checks are explicit.

## 12. Common mistakes and misconceptions

1. **“Stateless means no failure handling is needed.”** Stateless transformations can still lose or duplicate outputs when progress and side effects are not coordinated.
2. **“A state store automatically makes state durable.”** Durability and recovery depend on the state backend, checkpoints, and configuration.
3. **“Checkpointing is just saving a counter.”** Recovery needs a consistent relationship among state, source progress, and any coordinated output.
4. **“At-least-once means the output is correct.”** It reduces loss under its assumptions but can repeat non-idempotent effects.
5. **“At-most-once means no duplicates and no loss.”** It may avoid repeated processing by accepting that events can be lost.
6. **“Exactly once means every business action happens once across all systems.”** The guarantee has a defined boundary and depends on supported components and failure assumptions.
7. **“A unique event ID alone makes a sink idempotent.”** The sink must enforce deduplication atomically with the effect.
8. **“Check then write is always safe.”** Concurrent retries can race unless the operation is transactional or protected by a unique constraint/atomic primitive.
9. **“Deduplication can be retained forever for free.”** State consumes storage and has a lifecycle; expiry can re-open a duplicate window.
10. **“State can be deleted when a window first emits.”** Topic 3’s allowed-lateness policy may permit later corrections.
11. **“Replaying the broker is always sufficient to rebuild state.”** Required events may have expired; a separate archive or source of truth may be necessary.
12. **“A transactional database write makes the email or HTTP call transactional too.”** External effects outside the transaction have separate failure and retry semantics.
13. **“Exactly-once is always worth the cost.”** The right choice depends on business loss/duplication tolerance, latency, throughput, and operational constraints.
14. **“All frameworks implement checkpoints and transactions the same way.”** Verify the selected product and sink connector’s documented semantics.
15. **“A successful test proves all failure modes are covered.”** Tests should target crashes and timeouts at specific boundaries and be complemented by reconciliation and operational monitoring.

## 13. Knowledge-check questions with answers or explanations

1. **What distinguishes stateless from stateful processing?**  
   Stateless processing depends on the current event and fixed configuration; stateful processing depends on maintained information from earlier events or context.

2. **Why is a running account total keyed state?**  
   The processor must remember a separate total per account and update it when new account events arrive.

3. **Why does unbounded streaming need state cleanup?**  
   Keys, deduplication IDs, windows, and buffers can accumulate indefinitely; cleanup controls cost and resource growth but must not discard state still needed for correct results.

4. **What is a checkpoint?**  
   A recovery point containing enough coordinated state/progress information to restore processing to a consistent point, according to the selected system’s protocol.

5. **What is the danger of advancing source progress without corresponding state durability?**  
   Recovery may skip events whose effects are absent from the restored state.

6. **What is at-most-once processing?**  
   Each event is processed zero or one times under the stated model; an event may be lost or skipped.

7. **What is at-least-once processing?**  
   The system retries/replays so an event is processed one or more times under its recovery assumptions; duplicates are possible.

8. **What does exactly-once processing mean?**  
   Effects are committed once within a specific supported boundary. The boundary and failure assumptions must be stated.

9. **Why is exactly-once not automatically end-to-end?**  
   Arbitrary sinks and external effects may not participate in the processor’s transaction or idempotency mechanism.

10. **What is idempotency?**  
    Repeating the same logical operation has the same final effect as applying it once, within the defined scope.

11. **Why must deduplication and the business update be atomic?**  
    If one commits without the other, a crash can create a duplicate effect or cause an event to be marked processed without applying its effect.

12. **In the worked example, what total results from applying the 50-unit increment twice to a starting total of 1,000?**  
    1,100, instead of the intended 1,050.

13. **Why is a stable event ID not enough by itself?**  
    The sink must durably and atomically enforce that the ID cannot apply the effect twice.

14. **How does Topic 3 affect state lifecycle?**  
    Window state may need to remain available until the watermark/allowed-lateness policy no longer permits late events to change results.

15. **How does Topic 2 affect recovery?**  
    Partition offsets and retention determine where a consumer can resume and how much input history is available for recovery or replay.

16. **What must be verified before claiming a framework’s exactly-once guarantee?**  
    Source and sink support, configuration, checkpoint/transaction protocol, included components, failure model, output semantics, and behavior under crash/timeout/retry.

## 14. Summary, mastery criteria, and completion checklist

### Summary

- Stateless operators transform records independently; stateful operators remember information across events.
- Keyed state supports per-entity aggregates, but key choice and partition distribution affect correctness and scalability.
- State lifecycle must be bounded and aligned with windows, late-event policy, replay horizon, and business retention requirements.
- Checkpoints are useful only when restored state and input progress represent a consistent point.
- At-most-once may lose events; at-least-once may repeat effects; exactly-once is meaningful only within a clearly defined, supported boundary.
- Delivery, processing, state consistency, sink writes, and end-to-end business effects are different guarantees.
- Retries are normal. Stable identities, atomic idempotency, supported transaction coordination, and reconciliation help control duplicate effects.
- State and recovery decisions trade correctness, latency, throughput, storage, and operational complexity.
- CDC and replay are introduced here as dependencies and are developed in Topic 5; lag and failure diagnosis are developed in Topic 7.

### Mastery criteria

You are ready to proceed when you can:

- [ ] Classify operators as stateless or stateful and explain your assumptions.
- [ ] Define a key and lifecycle policy for each stateful operator.
- [ ] Explain why state cannot grow forever without a lifecycle decision.
- [ ] Draw the relationship among input position, state, checkpoint, and output.
- [ ] Explain how a crash can create duplicate or lost effects when progress and output are not coordinated.
- [ ] Define at-most-once, at-least-once, and exactly-once with explicit boundaries.
- [ ] Distinguish processor-level guarantees from end-to-end business effects.
- [ ] Design an idempotent sink operation with a stable identity and atomic enforcement.
- [ ] Explain deduplication’s storage, expiry, and race conditions.
- [ ] Connect Topic 3’s late-event policy to state retention and output corrections.
- [ ] Connect Topic 2’s retention/replay window to recovery feasibility.
- [ ] Complete the retry, checkpoint, and guarantee-boundary exercises.
- [ ] List product-specific semantics that must be verified rather than assumed.

**Completion gate:** Produce a state inventory/lifecycle table, a checkpoint recovery timeline, a delivery-guarantee decision record, and a duplicate/idempotency design. A reviewer should be able to see the exact guarantee boundary and identify any external effect that remains outside it.

## 15. Exact repository-relative cross-references supported by the roadmap

The paths below follow the supplied overall project tree and the module-specific roadmap. The roadmap describes intended learning sequence and dependencies; it does not imply that the topic files were already populated.

### Within `Stage 2D — Data Architecture/09-Streaming-and-Real-Time-Data-Architecture/`

- `01-real-time-use-cases-and-latency-budgets.md` — measurable latency, freshness, and correctness objectives.
- `02-event-brokers-topics-partitions-and-retention.md` — keys, partitions, offsets, retention, and replay window.
- `03-event-time-processing-ordering-and-watermarks.md` — event-time windows, watermarks, late events, and correction policy.
- `05-cdc-event-backbones-and-replay.md` — next-stage CDC and replay design.
- `06-real-time-serving-stores-and-materialized-views.md` — serving-store update and materialized-view behavior.
- `07-late-events-backpressure-and-stream-failure-modes.md` — operational failure modes, lag, backpressure, and retries.
- `practice-questions.md` — module knowledge validation.
- `README.md` — module entry point.
- `roadmap-Streaming-and-Real-Time-Data-Architecture.md` — module-specific source of truth.
- `Projects/09-real-time-risk-monitoring-architecture.md` — integrated module project.

### Earlier Stage 2D dependencies

- `../02-Requirements-Constraints-and-Architecture-Decisions/04-latency-throughput-freshness-and-availability-targets.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/06-architecture-trade-offs-and-decision-criteria.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/07-architecture-decision-records-adrs.md`
- `../03-Data-Architecture-Patterns-and-Reference-Architectures/06-event-driven-and-data-sharing-patterns.md`
- `../04-Conceptual-Logical-and-Physical-Data-Modeling/06-event-modeling-and-domain-driven-design.md`
- `../06-Data-Integration-and-Interoperability/04-streaming-events-and-message-contracts.md`
- `../06-Data-Integration-and-Interoperability/05-data-contracts-schema-registry-and-compatibility.md`
- `../06-Data-Integration-and-Interoperability/07-idempotency-deduplication-and-reconciliation.md`

The next topic uses these state and guarantee foundations to examine how database changes enter the stream, how event backbones are designed, and when replay can reconstruct or reload data. Keep the boundary clear: this lesson explains state, checkpoint/recovery concepts, and guarantee scopes; Topic 5 develops CDC and replay plans.
