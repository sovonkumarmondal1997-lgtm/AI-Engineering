# Event-Time Processing, Ordering, and Watermarks

> **Purpose:** Learn how to interpret timestamps in event streams, reason about events that arrive out of order, define time windows, and use watermarks and lateness policies to balance result completeness against latency.

> **Roadmap alignment:** This is Topic 3 in `Stage 2D — Data Architecture/09-Streaming-and-Real-Time-Data-Architecture/`. The module roadmap is the source of truth for intended scope and learning order. It notes that topic files were empty when the roadmap was authored; the scenarios, timestamps, thresholds, and exercises in this lesson are illustrative teaching examples, not pre-existing repository requirements. Watermark behavior and APIs differ across processing engines; verify exact semantics for the technology selected.

---

## 1. Title and purpose

A stream’s arrival order is not necessarily the order in which business events happened. A mobile device can record an event while offline and upload it later. A network retry can delay one record while later records arrive first. Multiple partitions can progress independently. Producer clocks can also disagree.

If an analytics system groups events by the time they are processed rather than by the time the events actually happened, it may assign events to the wrong reporting interval. If it waits indefinitely for every possible late event, it may never publish a timely result.

This topic teaches the vocabulary and design decisions needed to answer:

- Which timestamp represents the business event?
- What ordering does the system actually provide?
- Which time interval should receive each event?
- How does the processor estimate that it has seen most events for a period?
- What happens when an event arrives after a result has been emitted?
- How much waiting is acceptable under the latency objective from Topic 1?

The goal is not to guarantee that no late event will ever arrive. The goal is to make the time semantics, assumptions, and late-event policy explicit and testable.

## 2. Position in the module and prerequisites

This is Topic 3 in the recommended sequence:

1. `01-real-time-use-cases-and-latency-budgets.md` — define a measurable end-to-end outcome and latency budget.
2. `02-event-brokers-topics-partitions-and-retention.md` — understand topics, keys, partitions, offsets, and retention.
3. `03-event-time-processing-ordering-and-watermarks.md` — **this lesson**: define time, windows, ordering, watermarks, and late-event policy.
4. `04-stream-processing-state-and-delivery-semantics.md` — deeper treatment of keyed state, checkpoints, and delivery/processing semantics.
5. `05-cdc-event-backbones-and-replay.md` — database changes, event backbones, and replay.
6. `06-real-time-serving-stores-and-materialized-views.md` — make results available to consumers.
7. `07-late-events-backpressure-and-stream-failure-modes.md` — diagnose lag, backpressure, and operational failure modes.

### Prerequisites

- Topic 1: latency, freshness, percentiles, end-to-end objectives, and trade-offs.
- Topic 2: partition-local ordering, keys, consumer groups, retention, and replay window.
- Event-model basics: what happened, which entity it concerns, and what timestamp the source records.

Useful repository-relative prerequisites:

- `../02-Requirements-Constraints-and-Architecture-Decisions/04-latency-throughput-freshness-and-availability-targets.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/06-architecture-trade-offs-and-decision-criteria.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/07-architecture-decision-records-adrs.md`
- `../03-Data-Architecture-Patterns-and-Reference-Architectures/06-event-driven-and-data-sharing-patterns.md`
- `../04-Conceptual-Logical-and-Physical-Data-Modeling/06-event-modeling-and-domain-driven-design.md`
- `../06-Data-Integration-and-Interoperability/04-streaming-events-and-message-contracts.md`

## 3. Learning objectives

After this lesson, you should be able to:

1. Distinguish event time, ingestion time, and processing time.
2. Explain why arrival order can differ from event-time order.
3. State the limits of partition-local ordering and why multiple partitions do not create a global order.
4. Define tumbling, sliding, and session windows and select a window that matches a business question.
5. Explain a watermark as an estimate of event-time progress, not proof that no earlier event can arrive.
6. Apply an explicitly stated watermark and allowed-lateness policy to a timeline.
7. Distinguish an initial/provisional result from a final-looking result that can later be corrected or retracted.
8. Explain timestamp quality, missing timestamps, time zones, and clock skew.
9. Balance latency, completeness, cost, and operational complexity using Topic 1’s objective.
10. Identify which state and delivery questions belong to Topic 4 rather than solving them implicitly here.

## 4. Readiness check

Try these questions before reading the lesson.

1. A payment occurs at 10:02, reaches the broker at 10:03, and is processed at 10:04. Which time is event time?
2. Can a later event be processed before an earlier event? Give one reason.
3. If two records are in different partitions, does their partition order tell you which business event happened first?
4. What is the difference between a five-minute tumbling window and a five-minute sliding window that advances every minute?
5. Does a watermark prove that an event with an earlier timestamp can never arrive?
6. Why can waiting longer for late events conflict with a low-latency requirement?

**Answers**

1. 10:02, assuming it is the trusted timestamp for when the payment event occurred.
2. Yes. Network delays, retries, partition scheduling, or different producer paths can change arrival/processing order.
3. No. Each partition has its own order; there is no automatic global ordering across partitions.
4. A tumbling window creates adjacent, non-overlapping five-minute intervals. The sliding configuration creates overlapping five-minute intervals starting every minute.
5. No. It is a progress estimate or engine-defined signal used to make progress decisions. Events earlier than it may still arrive.
6. Waiting increases result latency; publishing sooner improves timeliness but may require later corrections or acceptance of incompleteness.

## 5. Beginner foundations: timestamps and ordering

### 5.1 Three important timestamps

| Timestamp | Meaning | Common source | Main use | Common risk |
|---|---|---|---|---|
| **Event time** | When the business event happened, as represented by the event’s timestamp | Producer/source system, device, database change metadata | Business-time analytics, event-time windows, temporal comparisons | Source clock may be wrong; timestamp may be missing or semantically ambiguous |
| **Ingestion time** | When the event is received by an ingestion boundary, such as the broker or collector | Broker/collector clock | Measuring transport delay, arrival rates, and ingestion behavior | Does not tell you when the business event happened |
| **Processing time** | When a processing operator handles the event | Processor/worker clock | Measuring processing delay and runtime behavior | Changes with queueing, load, retries, and scheduling |

These definitions are conceptual. A product may expose several related timestamps (for example, source timestamp, broker append timestamp, operator processing timestamp), and the exact meaning depends on configuration. Document the meaning and clock source for every timestamp used in a requirement or calculation.

### 5.2 Intuitive example: a letter and its postmark

Imagine a letter written on Monday, posted on Tuesday, and read on Thursday.

- The day it was written is analogous to **event time**.
- The day the postal system accepted it is analogous to **ingestion time**.
- The day the recipient reads it is analogous to **processing time**.

If a report asks “How many letters were written on Monday?”, grouping by read time answers the wrong question. Streaming systems face the same problem: arrival time is convenient, but may not represent the business time being measured.

### 5.3 Why events arrive late or out of order

Events can arrive later than expected, or in a different order from the order implied by their event timestamps, because of:

- **Network delays:** one record takes longer to reach the broker than another.
- **Retries:** a failed publish or transmission is retried after later records have already arrived.
- **Multiple partitions:** partitions progress independently; records in one partition may lag behind records in another.
- **Producer behavior:** an application buffers, batches, queues, or sends records asynchronously.
- **Offline sources:** a phone, vehicle, or sensor records data without connectivity and uploads it later.
- **Clock skew:** two source clocks disagree, so timestamps do not accurately represent a common timeline.
- **Source semantics:** a timestamp may describe when a record was created, committed, received, or exported—not necessarily when the business action occurred.
- **Backpressure or overloaded consumers:** the processor may receive data faster than it can process it.

Late and out-of-order are related but not identical:

- **Out of order** describes a mismatch between arrival/processing sequence and the intended temporal order.
- **Late** is defined relative to a policy or deadline—for example, an event arriving after the processor has advanced beyond a window’s end or after that window’s allowed-lateness period.

An event is not inherently “late” without a reference point and a policy.

### 5.4 Ordering guarantees and their limits

Topic 2 introduced the common partitioned-log model: records have an order within a partition. That guarantee does not imply one total order across all partitions.

Example:

```text
Topic: account-events

Partition 0:  A1 (event time 10:01) -> A2 (event time 10:03)
Partition 1:  B1 (event time 10:02) -> B2 (event time 10:04)

There is no broker-provided global sequence that automatically proves
whether A2 or B1 should be considered first by business event time.
```

A stream processor may merge records from multiple partitions as they become available. Its observed sequence can therefore differ from the global order one might infer by sorting event timestamps.

Also distinguish:

- **Transport/partition order:** the sequence exposed within one partition.
- **Event-time order:** a sequence inferred from timestamps.
- **Causal order:** the order required by a business dependency (for example, an account must be opened before a transaction is applied).
- **Processing order:** the order in which operators handle records.

These orders can differ. Sorting by timestamp alone does not prove causality, especially when clocks are skewed or timestamps have coarse resolution.

### 5.5 Timestamp quality: what to check

Before using a timestamp for event-time computation, establish:

1. **Meaning:** What business moment does it represent?
2. **Authority:** Which system creates it, and can it be trusted?
3. **Clock source:** Is the clock synchronized, and what is the expected maximum skew?
4. **Time zone:** Is the timestamp stored with an offset or normalized consistently (often UTC)?
5. **Precision:** Is it seconds, milliseconds, microseconds, or another unit?
6. **Validity:** Can it be null, malformed, defaulted, or far in the future?
7. **Monotonicity:** Does the source guarantee any order for a given entity? Do not assume it does.
8. **Corrections:** Can the source later revise the timestamp or publish a correction?
9. **Contract:** Is the meaning and unit documented in the event schema?

A timestamp unit error can create extreme apparent lateness: interpreting milliseconds as seconds or vice versa shifts an event by orders of magnitude. A future-dated record can also push a naïve progress calculation forward unexpectedly. Validation and quarantine policies should be explicit.

## 6. Intermediate foundations: windows and watermark mechanics

### 6.1 What is a time window?

A window assigns events to a time interval or activity period so that a processor can compute results such as a count, sum, average, maximum, or risk exposure for that period.

Without windows, a question like “How many failed payments occurred in each five-minute period?” has no clear grouping boundary.

The following are common window types. Exact APIs and boundary conventions vary by engine; use the definitions and interval notation specified in your chosen technology.

### 6.2 Tumbling windows

A **tumbling window** has a fixed duration and does not overlap adjacent windows.

For five-minute tumbling windows, a common convention is:

- `[10:00, 10:05)`
- `[10:05, 10:10)`
- `[10:10, 10:15)`

The half-open interval `[start, end)` includes the start but excludes the end. Under this convention, an event exactly at 10:05 belongs to the second window, not the first.

**Useful when:** producing fixed-interval totals, such as payment failures per five minutes.

**Trade-off:** the interval boundary can split events that are close in time but conceptually related.

**What can go wrong:** the team assumes different boundary conventions, or uses processing time when the business requirement is event time.

### 6.3 Sliding windows

A **sliding window** has a duration and a slide/advance interval. Windows overlap when the slide is shorter than the duration.

Example: duration 5 minutes, slide 1 minute:

- `[10:00, 10:05)`
- `[10:01, 10:06)`
- `[10:02, 10:07)`

An event may contribute to multiple windows. This can answer questions such as “What was the total in the trailing five minutes, updated each minute?” but it increases computation and result volume.

**Useful when:** monitoring rolling activity or rolling risk measures.

**Trade-off:** more overlapping computations and more updates; the exact number of windows affected by an event depends on the window definition.

### 6.4 Session windows

A **session window** groups activity separated by no more than a configured inactivity gap. A new event can extend a session; a sufficiently long gap separates one session from the next.

Illustrative example with a 10-minute inactivity gap:

- Events at 10:00, 10:04, and 10:11 can belong to one session because each successive gap is at most 10 minutes.
- If the next event is at 10:25, the 14-minute gap from 10:11 may end the earlier session and start a new one.

Session boundaries can be revised if late events bridge two previously separate sessions. That makes late-event behavior particularly important.

**Useful when:** grouping user activity, device bursts, or related interactions separated by periods of inactivity.

**Trade-off:** session boundaries are data-dependent and can change as new events arrive. Session implementation details vary across engines.

### 6.5 Watermarks: an estimate of event-time progress

A **watermark** is a processing system’s signal or estimate that event time has progressed to a certain point. It helps a processor decide when it can emit a result for an event-time window or when to stop waiting under a chosen policy.

A watermark is **not proof** that no earlier event can ever arrive. It is a practical progress estimate under assumptions about event delays, source behavior, partition progress, and the engine’s watermark strategy.

An intuitive example: a train dispatcher may say, “We expect all trains scheduled before 10:05 to have reported by now.” That expectation helps operations move forward, but it cannot prove that a delayed train will never report later.

Watermarks matter because they make a trade-off explicit:

- Advance quickly → lower result latency, but more events may arrive after a result has been emitted.
- Advance cautiously → more time for late events to be included, but results may be delayed and retained state may grow.

### 6.6 Watermark strategy and multiple inputs

Some engines derive watermark progress from observed event timestamps and a configured delay; others use source-specific signals or more complex strategies. With multiple partitions or inputs, the effective progress can depend on how the engine combines progress across them. A lagging or idle input may hold back progress in some configurations; ignoring an idle input can improve timeliness but creates assumptions about future arrivals.

Do not assume that a formula such as `maximum observed event time − allowed delay` exactly describes every engine. It is a useful teaching model, not a universal implementation contract. Check:

- whether the watermark is per source, partition, operator, or merged input;
- how idle partitions/inputs are treated;
- whether watermarks can move backward (many systems constrain them to progress monotonically, but verify the model);
- what event-time timestamp is used;
- how window closure and late-event handling are triggered;
- whether results can be emitted or updated multiple times.

### 6.7 Window end, watermark, and allowed lateness are distinct

For a window `[10:00, 10:05)`:

- **Window end:** 10:05, the end boundary of the event-time interval.
- **Watermark:** the system’s current estimate of event-time progress.
- **Allowed lateness:** an application/engine policy that permits events to affect a window after its nominal end or after an initial result, for a defined period or condition.

A simplified policy might say:

- emit an initial result when the watermark reaches or exceeds 10:05;
- with a three-minute allowed-lateness allowance, continue accepting ordinary updates while the watermark is at or before 10:08;
- close ordinary updates once the watermark is greater than 10:08, then drop, side-output, or separately handle later events.

This explicit boundary convention is for the teaching example, not a universal engine rule. Some APIs define allowed lateness relative to the window end; others express late-data behavior differently. Always check the chosen engine’s exact semantics.

## 7. Worked timeline with late and out-of-order events

This example uses a simplified watermark model so that the arithmetic is visible. All timestamps, processing arrivals, and thresholds are **illustrative assumptions**.

### 7.1 Assumptions

- We calculate a count for the tumbling event-time window **`[10:00, 10:05)`**.
- The window includes event times from 10:00 up to but not including 10:05.
- Events arrive at the processing system in the sequence shown below.
- For teaching only, assume watermark = maximum event time observed so far minus **2 minutes**.
- The watermark is treated as monotonic in this example.
- Initial output is eligible when watermark is at or beyond the window end (10:05).
- **Allowed lateness is 3 minutes after the window end**. Under this example’s boundary convention, ordinary updates remain eligible while the watermark is at or before 10:08; the window closes to ordinary updates once the watermark is greater than 10:08. This is a simplified policy, not a promise about a specific engine.
- We count all events in the window; no deduplication is assumed in this example.

### 7.2 Input events

| Arrival order | Event ID | Event time | Arrival/processing time | Meaning |
|---:|---|---|---|---|
| 1 | E1 | 10:01 | 10:01:05 | First event for the window |
| 2 | E2 | 10:04 | 10:04:05 | Later event time arrives second |
| 3 | E3 | 10:06 | 10:06:05 | Advances maximum event time |
| 4 | E4 | 10:08 | 10:08:05 | Advances watermark past window end |
| 5 | E5 | 10:02 | 10:09:00 | Late event for the earlier window |
| 6 | E6 | 10:11 | 10:11:05 | Advances watermark past allowed-lateness boundary |

The arrival sequence is not sorted by event time: E5 has event time 10:02 but arrives after E4, whose event time is 10:08.

### 7.3 Timeline and watermark calculation

| Step | Newly received event | Maximum event time seen | Simplified watermark (`max event time − 2 min`) | Effect on `[10:00, 10:05)` |
|---:|---|---|---|---|
| 1 | E1 at event time 10:01 | 10:01 | 09:59 | E1 is included; window not closed |
| 2 | E2 at event time 10:04 | 10:04 | 10:02 | E2 is included; window not closed |
| 3 | E3 at event time 10:06 | 10:06 | 10:04 | E3 is outside the target window; watermark still before 10:05 |
| 4 | E4 at event time 10:08 | 10:08 | 10:06 | Watermark is at or beyond 10:05; emit initial count = 2 (E1, E2) |
| 5 | E5 at event time 10:02 | 10:08 | 10:06 | E5 belongs to the target window and arrives within the allowed-lateness period; updated count = 3 |
| 6 | E6 at event time 10:11 | 10:11 | 10:09 | Watermark passes 10:08; the illustrative allowed-lateness period ends |

### 7.4 What the example teaches

1. **Window membership uses event time.** E5 belongs to `[10:00, 10:05)` because its event time is 10:02, even though it arrives after the processor has observed events with later timestamps.
2. **Watermark progress is an estimate.** At step 4, the watermark reaches 10:06, so the simplified policy emits an initial result for a window ending at 10:05. This does not prove no earlier event can arrive.
3. **Late arrival can revise a result.** E5 arrives after the initial result but before the allowed-lateness boundary. Under the example policy, the result changes from 2 to 3.
4. **A policy boundary has consequences.** At step 6, the watermark advances to 10:09, beyond 10:08. Under the example policy, the window is no longer eligible for ordinary updates. An even later event for `[10:00, 10:05)` would need to be dropped, sent to a late-data path, or handled by a separate correction process.
5. **Engine details matter.** The exact timing of output, closure, and updates depends on the selected engine’s watermark and window semantics. The example’s formula is intentionally simplified.

### 7.5 Timeline diagram

```text
Event time axis (business occurrence)
10:00        10:05        10:08
  |------------|------------|
  [ target window )  [allowed-lateness boundary for the example]

Arrival sequence:
E1(event 10:01) -> E2(event 10:04) -> E3(event 10:06)
    -> E4(event 10:08) -> E5(event 10:02, late)
    -> E6(event 10:11)

At E4: watermark = 10:06 -> initial window count 2
At E5: still within illustrative allowed lateness -> corrected count 3
At E6: watermark = 10:09 -> allowed-lateness boundary passed
```

The diagram separates the **event-time interval** from the **arrival sequence**. That distinction is the core skill in this topic.

## 8. Advanced policies: allowed lateness, corrections, clock skew, and latency/correctness trade-offs

### 8.1 What to do with late events

A late event is not automatically invalid. Decide what should happen based on the business meaning and the result’s consumers.

| Policy | What happens | Advantages | Costs and risks | Appropriate when |
|---|---|---|---|---|
| **Wait longer before emitting** | Delay output until a later progress threshold | More late events can be included in the first emitted result | Higher result latency; more waiting/state | Completeness matters more than immediate output |
| **Emit provisional result, then update** | Publish an early result and revise it when late events arrive within policy | Timely initial result and improved completeness | Consumers must understand updates and avoid treating provisional values as immutable |
| **Drop beyond the lateness limit** | Ignore events arriving after the policy boundary | Predictable state/cost and simple output lifecycle | Results remain incomplete; business impact must be acceptable |
| **Side-output or quarantine late records** | Route late events to a separate path for inspection/reconciliation | Preserves visibility and supports diagnosis | Extra pipeline and operational ownership |
| **Issue corrections/retractions** | Publish a compensating update or retract an earlier result | Can maintain downstream correctness after a published result changes | Consumers must support updates/retractions and reconcile state |
| **Recompute a historical interval** | Rebuild a result from retained raw events or an archive | Useful for material errors or audit | More compute and operational work; depends on retained source data and safe replay |

The policy should be documented per use case. A fraud alert, a regulatory report, and a dashboard may have different acceptable trade-offs even if they use the same input events.

### 8.2 Allowed lateness is a policy, not a property of nature

Allowed lateness specifies how long or under what progress condition the processor will continue to accept events for a window after its initial closure point. It does not make events arrive on time. It only defines what the processor does when they do not.

To choose a threshold, examine:

- observed arrival-delay distribution (for example p95/p99 lateness);
- expected source disconnection and retry patterns;
- acceptable result latency;
- business impact of missing or correcting events;
- storage/state and compute cost;
- whether consumers can handle revisions;
- whether a durable archive or replay process exists.

A threshold based only on average lateness can be misleading because tail delays may be much longer. Use measurements from representative conditions and state the target percentile or coverage goal where appropriate.

### 8.3 Timestamp quality and clock skew

Clock skew is the difference between clocks that are intended to represent the same time. Producer clocks can be fast or slow because of synchronization problems, device sleep, manual changes, faulty hardware, or incorrect time-zone handling.

Consequences include:

- events appearing to occur in the future or distant past;
- misleading lateness calculations;
- windows receiving events in the wrong interval;
- event-time order disagreeing with causal order;
- a single future-dated event advancing a naïve watermark strategy unexpectedly;
- confusing monitoring when ingestion time and event time differ sharply.

Mitigations include:

1. Define timestamp semantics and units in the event contract.
2. Prefer a trusted source timestamp where it truly represents the business event; do not blindly replace it with broker time.
3. Record ingestion time separately so transport delay can be measured.
4. Validate plausible timestamp ranges and quarantine clearly invalid values.
5. Measure source clock skew where possible and define an acceptable tolerance.
6. Handle missing timestamps explicitly rather than silently substituting processing time.
7. Document what happens to future-dated or malformed events.
8. Use a monotonic clock for measuring local elapsed duration where appropriate; wall-clock timestamps and monotonic elapsed-time clocks serve different purposes.

No design should assume all producer clocks are perfectly synchronized. Even synchronized clocks have finite uncertainty.

### 8.4 Connecting Topic 1’s latency budget to watermark policy

Topic 1 requires a measurable end-to-end latency objective—for example, a percentile target with clear start/end measurement points. Watermark and lateness choices consume part of that latency budget.

If the business requires an alert within a few seconds, waiting several minutes for event-time completeness may violate the requirement. Possible design options include:

- emit an early provisional signal and update it when late data arrives;
- use a separate rapid alert path and a slower, more complete reporting path;
- set a measured lateness allowance that fits the business tolerance;
- use a source with better event-time quality or lower delivery delay;
- explicitly accept a bounded incompleteness rate and monitor it.

Do not promise both immediate finality and unlimited late-event inclusion without a mechanism and cost to support it.

### 8.5 Partitioning from Topic 2 constrains event-time behavior

Topic 2 established that partition-local order is not global order. If events for one entity are keyed consistently to one partition, the processor may receive that entity’s records in partition order, subject to the product and producer semantics. Across partitions, the processor must not assume that observed arrival order is a total event-time sequence.

A lagging partition can affect event-time progress, depending on the engine’s watermark strategy. If a processor combines multiple inputs, it may need a policy for idle inputs and partitions. Such policies can improve latency but may increase the chance that later-arriving records are considered late.

Partition count, key choice, and event-time policy therefore interact:

- too few partitions can cause lag that delays watermarks;
- skew can make one partition much slower than others;
- treating an idle partition as inactive can let watermarks advance sooner but risks late events from that partition;
- repartitioning may change routing and ordering assumptions;
- more partitions do not automatically create a global event-time order.

### 8.6 State and delivery semantics: preview only

Windowed processing often needs to remember partial aggregates, window membership, and progress. If a result is updated after a late event, the processor and downstream consumers must agree on whether the output is an update, replacement, retraction, or new event.

Those concerns depend on state and delivery semantics and are treated in depth in Topic 4, `04-stream-processing-state-and-delivery-semantics.md`. This lesson does not claim that a watermark alone guarantees exactly-once output, prevents duplicates, or makes external side effects consistent.

## 9. Industry use cases

### 9.1 Fraud and risk monitoring

A bank wants transaction activity grouped into five-minute event-time windows. Events may arrive out of order due to separate ingestion paths. A watermark allows the system to emit a timely initial risk summary while an allowed-lateness policy determines whether delayed transactions revise it.

Key design questions:

- Is the initial alert actionable before the window is complete?
- Can the risk service accept updates or reversals?
- What fraction of events arrive later than the chosen threshold?
- Is the event timestamp authoritative and validated?
- Does the latency target allow waiting, or is a provisional alert needed?

### 9.2 IoT telemetry

A vehicle or industrial sensor may buffer events while offline and upload them later. Event time represents the measurement time; ingestion time reflects when connectivity returned. A session window may group bursts of device activity, while a late-data path preserves measurements outside the normal lateness threshold.

Risk: a future-dated device clock can advance event-time progress incorrectly. Validate timestamps and do not assume all devices have synchronized clocks.

### 9.3 E-commerce activity

A business wants a rolling five-minute view of checkout failures, refreshed every minute. A sliding window can support the rolling metric. If a payment event is retried or delayed, a correction policy must define whether the dashboard updates historical totals.

Risk: treating a provisional count as final can cause teams to react to a number that later changes. The serving layer must communicate freshness and revision semantics.

### 9.4 Operational monitoring

An operations team wants to count service errors by minute. Processing-time windows can be useful for “what is arriving now?” while event-time windows answer “when did the errors occur?” These are different questions. Both can be useful, but the dashboard label should identify which timeline it represents.

### 9.5 Choosing the time basis

| Business question | Likely time basis | Important caveat |
|---|---|---|
| How many transactions occurred in each business-time interval? | Event time | Source timestamp quality and late events matter |
| How many records reached our broker this minute? | Ingestion time | Measures arrival volume, not occurrence volume |
| How much work did the processor handle in the last minute? | Processing time | May reflect queueing and runtime behavior rather than source activity |
| What is the current operational backlog? | Processing/ingestion metrics plus event-time lag | Define the metric precisely; one timestamp alone may be insufficient |

## 10. Hands-on exercises with inputs, tasks, deliverables, and validation criteria

All dates, times, thresholds, and rates in these exercises are illustrative. State any additional assumptions you make.

### Exercise A — Classify timestamps

**Inputs**

| Event | Business description | Source timestamp | Broker receive time | Processor handles it |
|---|---|---|---|---|
| A | Device measures temperature | 09:00:00 UTC | 09:03:00 UTC | 09:03:02 UTC |
| B | Payment service records authorization | 09:04:30 UTC | 09:04:31 UTC | 09:04:32 UTC |
| C | Mobile app records a click offline | 08:50:00 UTC | 09:10:00 UTC | 09:10:03 UTC |

Assume for this exercise that each source timestamp represents when the business event occurred. Assume all times are UTC and clocks are accurate enough for this exercise.

**Tasks**

1. Label event time, ingestion time, and processing time for each row.
2. Calculate source-to-broker delay and broker-to-processing delay.
3. Explain why event C arrives last but occurred earliest.
4. State what you would verify before using these timestamps in production.

**Deliverable**

A completed table with delay calculations and a short timestamp-quality checklist.

**Validation criteria**

- Event A: source-to-broker delay = 3 minutes; broker-to-processing delay = 2 seconds.
- Event B: source-to-broker delay = 1 second; broker-to-processing delay = 1 second.
- Event C: source-to-broker delay = 20 minutes; broker-to-processing delay = 3 seconds.
- The learner distinguishes event time from arrival and processing time and notes that source semantics and clock quality require verification.

### Exercise B — Reconstruct an out-of-order timeline

**Inputs**

All timestamps are illustrative and assumed to use the same time zone.

| Arrival order | ID | Event time | Arrival time |
|---:|---|---|---|
| 1 | X1 | 12:01 | 12:01:02 |
| 2 | X2 | 12:04 | 12:04:03 |
| 3 | X3 | 12:02 | 12:05:00 |
| 4 | X4 | 12:07 | 12:07:02 |
| 5 | X5 | 12:03 | 12:08:00 |

**Tasks**

1. List the events in arrival order.
2. List them in event-time order.
3. Identify which event first demonstrates an out-of-order arrival.
4. Explain why sorting the records by timestamp after the fact is not the same as the broker guaranteeing that order.
5. State one risk if these events come from different partitions.

**Deliverable**

Two timelines and a brief explanation.

**Validation criteria**

- Arrival order is X1, X2, X3, X4, X5.
- Event-time order is X1 (12:01), X3 (12:02), X5 (12:03), X2 (12:04), X4 (12:07).
- X3 arriving after X2 is the first out-of-order case relative to event time.
- The explanation distinguishes a retrospective sort from a live processing guarantee and notes that partition-local ordering does not imply global ordering.

### Exercise C — Apply a window and watermark policy

**Inputs**

- Target tumbling window: `[14:00, 14:05)`.
- All event times and arrivals below are illustrative.
- Simplified teaching watermark: maximum event time seen minus 2 minutes.
- Initial result is emitted when watermark reaches or passes 14:05.
- For this exercise, accept ordinary late updates while the watermark is at or before 14:08; close ordinary updates once it is greater than 14:08.
- Assume a monotonic watermark and count each event once.

| Arrival order | ID | Event time |
|---:|---|---|
| 1 | A | 14:01 |
| 2 | B | 14:04 |
| 3 | C | 14:06 |
| 4 | D | 14:08 |
| 5 | E | 14:02 |
| 6 | F | 14:11 |

**Tasks**

1. Compute the simplified watermark after each event.
2. Determine when the initial window result is emitted.
3. Determine the count in the initial result.
4. Decide whether E can update the result under the stated policy.
5. Decide when the allowed-lateness period ends.

**Deliverable**

A step-by-step table of max event time, watermark, window action, and result count.

**Validation criteria**

- Watermarks by arrival: 13:59, 14:02, 14:04, 14:06, 14:06, 14:09.
- The initial result becomes eligible after D, when the watermark reaches 14:06 (at or beyond the 14:05 window end).
- Initial count is 2 (A and B); C and D fall outside the target window.
- E has event time 14:02 and arrives before the policy boundary is crossed, so the result updates to 3 under these assumptions.
- After F, the watermark reaches 14:09, which is greater than 14:08, so ordinary updates are closed under the example policy.
- The learner notes that actual engine behavior may differ and must be checked.

### Exercise D — Decide late-event handling

**Inputs**

A fraud dashboard must show a result within 5 seconds at p95. Historical measurements show that most events arrive within 2 seconds of event time, but a small fraction arrive 30–90 seconds late. These figures are illustrative. The business says a missed event can matter, but an alert that arrives two minutes late is not useful for immediate intervention.

**Tasks**

1. Compare a policy that waits 90 seconds before emitting with a policy that emits quickly and allows corrections.
2. Recommend a policy or split-path design and state the assumptions.
3. Explain how late events should be observed and reconciled.
4. State what the dashboard or downstream consumer must know about provisional results.

**Deliverable**

A one-page policy decision with alternatives, trade-offs, and validation metrics.

**Validation criteria**

- The answer explicitly recognizes that waiting 90 seconds conflicts with the 5-second p95 target.
- A plausible answer uses a rapid provisional result with a late correction path, or a separate fast alert and slower complete reporting path.
- The answer does not claim a watermark eliminates late events.
- The design defines metrics such as lateness distribution, correction rate, dropped/side-output count, and end-to-end latency.
- The answer identifies the consumer contract for updates or corrections.

### Exercise E — Explain latency versus completeness

**Inputs**

Two designs are under consideration for a five-minute event-time window:

- **Design A:** emits after a short watermark delay and drops events after a brief lateness allowance.
- **Design B:** waits longer and accepts more late events; it emits results later and keeps more window state.
- The business requires an initial alert quickly but also needs accurate end-of-day totals.

**Tasks**

1. Compare latency, completeness, state/cost, and operational complexity.
2. Recommend a design or two-path strategy.
3. Define the business metrics that would validate the decision.
4. State what changes if late events can revise published results.

**Deliverable**

A decision table and a short architecture recommendation.

**Validation criteria**

- The answer does not assume one policy is best for all uses.
- It separates immediate alerting from end-of-day completeness if appropriate.
- It proposes measurable criteria, such as p95 alert latency, late-event percentage, correction volume, final reconciliation variance, and compute/storage cost.
- It documents the consequences for downstream consumers if results are revised.

## 11. Common mistakes and misconceptions

1. **“Event time and processing time are the same.”** They represent different moments and answer different questions.
2. **“The broker’s order is the global event-time order.”** Partition order is local; timestamps and causal order may differ.
3. **“Sorting by timestamp guarantees correct causal order.”** Clock skew, duplicate timestamps, and business dependencies can make timestamp sorting insufficient.
4. **“A watermark proves all earlier events have arrived.”** It is a progress estimate or engine-defined signal, not proof about the future.
5. **“An event is late by definition.”** Lateness is relative to a window, watermark, deadline, and policy.
6. **“A five-minute window always means five-minute tumbling windows.”** Window type, slide, boundaries, and time basis must be stated.
7. **“A window result is final when first emitted.”** It may be provisional and can change if the system supports late updates.
8. **“Allowed lateness makes every late event safe.”** It only defines a policy boundary; events later than that may still need a separate path or may be discarded.
9. **“Wait longer and the system becomes perfectly complete.”** There may be arbitrarily delayed, lost, malformed, or future-corrected events; waiting also adds latency.
10. **“All producer clocks are synchronized.”** Clock skew is a real design condition; measure and validate timestamps.
11. **“A future-dated event is harmless.”** It may distort progress estimates and window behavior depending on the engine.
12. **“A watermark formula is identical in every engine.”** Watermark generation, merging, idleness, and window closure vary by product and API.
13. **“Watermarks provide exactly-once processing.”** Watermarks address event-time progress, not all state, side-effect, or delivery guarantees.
14. **“If a late event is ignored, the business result is still correct.”** The policy may create bounded incompleteness; the business must accept and monitor that outcome.
15. **“More partitions automatically solve event-time lag.”** A hot key, slow consumer, idle partition policy, or downstream bottleneck may remain.

## 12. Knowledge-check questions with answers or explanations

1. **Define event time, ingestion time, and processing time.**  
   Event time represents when the event occurred; ingestion time is when an ingestion boundary received it; processing time is when the processor handled it.

2. **Why can arrival order differ from event-time order?**  
   Network delay, retries, source buffering, offline devices, partition scheduling, and clock skew can all reorder observed arrivals.

3. **What does partition-local ordering guarantee, and what does it not guarantee?**  
   In common partitioned-log systems, records are ordered within a partition. That does not create a total order across partitions or prove event-time/causal order.

4. **When is a tumbling window appropriate?**  
   For fixed, adjacent, non-overlapping intervals such as counts per five-minute period.

5. **What distinguishes a sliding window from a tumbling window?**  
   A sliding window advances by a configured interval and may overlap; an event can contribute to multiple windows.

6. **How does a session window differ from fixed-duration windows?**  
   It groups activity based on an inactivity gap; new events can extend or merge sessions depending on the rules.

7. **What is a watermark?**  
   A processor’s estimate or signal of event-time progress used to make decisions about window results and late events.

8. **Does watermark 10:06 prove no event with event time 10:02 can arrive?**  
   No. It only indicates progress under the engine’s strategy and assumptions. Earlier events may still arrive.

9. **In the worked example, why does E5 update the window result?**  
   Its event time (10:02) falls in `[10:00, 10:05)`, and it arrives while the illustrative allowed-lateness policy still permits updates.

10. **Why can a late event change a published aggregate?**  
    It may belong to a window whose initial result was already emitted. If updates/corrections are supported, the aggregate must be revised; otherwise the event may be routed or discarded according to policy.

11. **What is clock skew?**  
    A difference between clocks expected to represent the same time; it can distort event timestamps and apparent ordering.

12. **Why keep ingestion time if event time is the main business timestamp?**  
    It helps measure source-to-broker delay, detect late arrivals, and diagnose transport behavior.

13. **How should an architect choose allowed lateness?**  
    Use observed lateness distributions, business impact, latency targets, correction capability, state/cost, and recovery requirements. State assumptions and validate with production-like data.

14. **Why might a fast provisional result plus correction path be better than waiting for every event?**  
    It can meet a strict initial latency target while improving completeness later, provided consumers understand revisions and the correction path is reliable.

15. **Which topic covers deeper state and delivery semantics?**  
    Topic 4, `04-stream-processing-state-and-delivery-semantics.md`.

## 13. Summary and mastery checklist

### Summary

- Event time, ingestion time, and processing time are different timelines.
- Out-of-order arrivals are normal in distributed systems; the reasons include network delays, retries, partitions, source buffering, offline devices, and clock skew.
- Ordering within a partition is not global ordering and is not automatically causal or event-time order.
- Tumbling windows are non-overlapping fixed intervals; sliding windows overlap according to duration and slide; session windows group activity separated by an inactivity gap.
- Watermarks help a processor reason about event-time progress but do not prove that earlier events can never arrive.
- Allowed lateness defines how long a window remains eligible for late updates under a policy; exact semantics are engine-specific.
- Late-event strategies include waiting, provisional results with updates, dropping, side outputs, corrections, and historical recomputation.
- Timestamp meaning, units, source clock quality, time zones, and skew must be documented.
- Topic 1’s latency objective and Topic 2’s partition/key design constrain the window and watermark policy.
- Topic 4 owns the deeper treatment of state, checkpoints, and delivery semantics.

### Mastery checklist

You are ready to progress to Topic 4 when you can:

- [ ] Label event, ingestion, and processing timestamps in a sample event.
- [ ] Reconstruct arrival order and event-time order for a timeline.
- [ ] Explain partition-local versus global ordering.
- [ ] Select and describe a tumbling, sliding, or session window for a business question.
- [ ] Calculate a simplified watermark under explicitly stated assumptions.
- [ ] Apply a window-end and allowed-lateness policy without mixing the two boundaries.
- [ ] Explain whether a late event is included, updates a result, is side-output, or is dropped under a stated policy.
- [ ] Identify timestamp-quality and clock-skew risks.
- [ ] Explain the trade-off between initial latency and result completeness.
- [ ] Identify which engine-specific watermark details must be verified.
- [ ] Complete the timeline and policy exercises with consistent calculations.
- [ ] Document the result contract for provisional outputs, updates, or corrections.

**Completion gate:** Produce a timestamp classification table, an event-time/arrival timeline, a window-and-watermark simulation, and a short late-event policy decision. A reviewer should be able to reproduce your calculations and identify the assumptions.

## 14. Cross-references to relevant module files

Paths below follow the supplied overall project tree and module roadmap. The roadmap describes the intended sequence; it does not imply that each topic file was already populated.

### Within `Stage 2D — Data Architecture/09-Streaming-and-Real-Time-Data-Architecture/`

- `01-real-time-use-cases-and-latency-budgets.md` — prior topic; measurable latency objective and budget.
- `02-event-brokers-topics-partitions-and-retention.md` — prior topic; partition ordering, keys, retention, and replay window.
- `04-stream-processing-state-and-delivery-semantics.md` — next topic; state, checkpoints, and delivery semantics.
- `05-cdc-event-backbones-and-replay.md` — CDC and replay.
- `06-real-time-serving-stores-and-materialized-views.md` — serving results and update semantics.
- `07-late-events-backpressure-and-stream-failure-modes.md` — late events, lag, backpressure, and failure handling.
- `practice-questions.md` — module practice and knowledge validation.
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

The next topic builds on this lesson by examining what the processor remembers, what survives a restart, and what delivery guarantees mean. Keep the boundary clear: this lesson defines time and window-progress decisions; Topic 4 develops state and delivery semantics.
