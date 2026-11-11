# Streaming and Real-Time Data Architecture — Practice Questions

## 1. Title, purpose, and how to use this assessment

This assessment checks conceptual understanding, quantitative reasoning, architecture judgment, and incident troubleshooting across the seven topics in the **Streaming and Real-Time Data Architecture** module of Stage 2D.

**Source and scope note:** The supplied module roadmap is the scope guide. It says the seven topic files and `practice-questions.md` existed as empty files when the roadmap was authored. Accordingly, the questions and answer explanations below are newly authored from the roadmap's stated learning outcomes and recommended learning focus; they are not extracted from pre-existing lesson files. All scenario numbers and targets introduced by this assessment are **illustrative assumptions**, not repository requirements, production benchmarks, or universal defaults.

### Recommended workflow

1. Study Topics 1–7 in numeric filename order.
2. Attempt Sections 3–7 before opening Section 9, the answer key.
3. Show your calculations with units. For architecture questions, state assumptions and explain why your choice fits the stated constraints.
4. Score yourself using Section 8. Use Section 10 to select the lesson to revisit.
5. Complete Section 11 before starting the module's final project.

**Vendor-neutral assessment:** No question depends on a specific vendor, product, command, or version. Where behavior varies by implementation, state the required guarantee and verify it against the selected technology during real design work.

### Learning-objective codes used below

| Code | Objective |
|---|---|
| LO1 | Translate a real-time use case into measurable latency, freshness, throughput, and correctness requirements. |
| LO2 | Explain broker/topic/partition/key/consumer-group/offset/retention choices and their consequences for ordering and parallelism. |
| LO3 | Reason about event time, processing time, ordering, windows, watermarks, and late-event policy. |
| LO4 | Explain state, checkpointing, recovery, delivery semantics, idempotency, and duplicate effects. |
| LO5 | Design CDC/snapshot-plus-stream handoff, replay, retention, and reconciliation. |
| LO6 | Select serving stores and define materialized-view access patterns, freshness, and safe update semantics. |
| LO7 | Diagnose lag, backpressure, failures, retry behavior, and recovery trade-offs. |
| LO8 | Integrate all seven topics into a defensible end-to-end architecture and explain trade-offs. |

## 2. Coverage map: topic filenames to assessment sections

Paths are relative to `Stage 2D — Data Architecture/09-Streaming-and-Real-Time-Data-Architecture/`.

| Topic | Exact lesson filename | Assessment locations | Main evidence expected |
|---|---|---|---|
| 1. Use cases and latency budgets | `01-real-time-use-cases-and-latency-budgets.md` | B1–B2, I1, Q1, A1, Capstone C1 | Measurable use case, latency budget, freshness boundary |
| 2. Brokers, topics, partitions, retention | `02-event-brokers-topics-partitions-and-retention.md` | B3–B4, I2, Q2, Q5, A1–A2, A4, Capstone C2 | Key/partition reasoning, offsets, consumer parallelism, retention |
| 3. Event time, ordering, watermarks | `03-event-time-processing-ordering-and-watermarks.md` | B5–B6, I3, Q4, A2, Capstone C3 | Timestamp semantics, windows, watermark and late-data policy |
| 4. State and delivery semantics | `04-stream-processing-state-and-delivery-semantics.md` | B7–B8, I4, A2–A3, Capstone C3 | Recovery boundaries, duplicates, idempotency, delivery guarantees |
| 5. CDC, event backbones, replay | `05-cdc-event-backbones-and-replay.md` | B9–B10, I5, Q5, A2–A4, Capstone C4 | Snapshot handoff, source positions, replay feasibility, reconciliation |
| 6. Serving stores and materialized views | `06-real-time-serving-stores-and-materialized-views.md` | B11–B12, I6, A3–A4, Capstone C5 | Store selected by access pattern, version-safe updates, freshness |
| 7. Late events, backpressure, failures | `07-late-events-backpressure-and-stream-failure-modes.md` | B13–B14, I7, Q3, A1–A4, Capstone C6 | Lag diagnosis, failure-mode analysis, bounded recovery |
| Cross-topic integration | All seven lesson files | B15–B16, I8, Section 7 capstone | End-to-end reasoning and explicit trade-offs |

**Assessment format and score**

- Section 3 — Beginner questions: 16 questions × 1 point = **16 points**
- Section 4 — Intermediate application: 8 questions × 3 points = **24 points**
- Section 5 — Advanced architecture/troubleshooting: 4 scenarios × 5 points = **20 points**
- Section 6 — Quantitative exercises: 5 exercises × 4 points = **20 points**
- Section 7 — Integrated capstone: **20 points**

**Total: 100 points.** The score model and thresholds are recommended assessment guidance, not repository requirements.

## 3. Beginner questions — grouped by topic

Answer in one to three sentences unless the question asks for a list. Each question is worth **1 point**. Topic and learning-objective mappings are shown with each item.

### Topic 1 — Real-time use cases and latency budgets

**B1. Define end-to-end latency and freshness.** Explain why a fast API response does not, by itself, prove that the data returned is fresh.

- **Mapping:** `01-real-time-use-cases-and-latency-budgets.md`; LO1.

**B2. Explain the difference between a business objective and a latency budget.** Give one example of a measurable objective and name at least two component boundaries that could be measured.

- **Mapping:** `01-real-time-use-cases-and-latency-budgets.md`; LO1.

### Topic 2 — Brokers, topics, partitions, keys, consumer groups, offsets, and retention

**B3. Define a topic, partition, key, offset, and consumer group.** Explain how partitions affect parallelism and ordering.

- **Mapping:** `02-event-brokers-topics-partitions-and-retention.md`; LO2.

**B4. Explain the difference between consumer lag and retention.** Why can retention expiry prevent a lagging consumer from recovering from the broker alone?

- **Mapping:** `02-event-brokers-topics-partitions-and-retention.md`; LO2.

### Topic 3 — Event time, processing time, ordering, windows, and watermarks

**B5. Distinguish event time, processing time, and ingestion time.** Give one reason the values may differ for the same event.

- **Mapping:** `03-event-time-processing-ordering-and-watermarks.md`; LO3.

**B6. What does a watermark represent in event-time processing?** Explain why it should not be described as proof that no older event can ever arrive.

- **Mapping:** `03-event-time-processing-ordering-and-watermarks.md`; LO3.

### Topic 4 — Stateful processing, checkpoints, delivery semantics, idempotency, and duplicates

**B7. What is the purpose of a checkpoint?** Explain one limitation of assuming a checkpoint automatically makes an external sink write atomic with processor progress.

- **Mapping:** `04-stream-processing-state-and-delivery-semantics.md`; LO4.

**B8. Explain at-least-once processing and idempotency.** How can at-least-once delivery be used safely when the destination supports a stable event ID or version guard?

- **Mapping:** `04-stream-processing-state-and-delivery-semantics.md`; LO4.

### Topic 5 — CDC, event backbones, snapshot-plus-stream, retention, replay, and reconciliation

**B9. What is change data capture (CDC), and what is the purpose of a source log position or equivalent version?**

- **Mapping:** `05-cdc-event-backbones-and-replay.md`; LO5.

**B10. Explain the snapshot-plus-stream handoff problem.** What can go wrong if the snapshot boundary and the stream start position are not coordinated?

- **Mapping:** `05-cdc-event-backbones-and-replay.md`; LO5.

### Topic 6 — Serving stores and materialized views

**B11. What is a materialized view in a streaming architecture?** Explain why the choice of serving store should start with the access pattern rather than popularity.

- **Mapping:** `06-real-time-serving-stores-and-materialized-views.md`; LO6.

**B12. What is a version-aware upsert?** Explain how it helps prevent an older, out-of-order update from overwriting newer state.

- **Mapping:** `06-real-time-serving-stores-and-materialized-views.md`; LO6.

### Topic 7 — Late events, backpressure, lag, and failure modes

**B13. Distinguish backlog, consumer lag, backpressure, and saturation.** Your answer should make clear which are accumulated work, flow control, or resource conditions.

- **Mapping:** `07-late-events-backpressure-and-stream-failure-modes.md`; LO7.

**B14. Define a poison message and a dead-letter/quarantine path.** Why does moving a poison message aside not automatically mean the data problem is resolved?

- **Mapping:** `07-late-events-backpressure-and-stream-failure-modes.md`; LO7.

### Cross-topic foundations

**B15. Explain the difference between a transport-level duplicate and a business-level duplicate effect.** Give one example of how the former can create the latter.

- **Mapping:** `04-stream-processing-state-and-delivery-semantics.md`, `07-late-events-backpressure-and-stream-failure-modes.md`; LO4, LO7.

**B16. Name four signals you would inspect when a streaming pipeline becomes stale, and state what at least two of those signals cannot prove on their own.**

- **Mapping:** `01-real-time-use-cases-and-latency-budgets.md`, `06-real-time-serving-stores-and-materialized-views.md`, `07-late-events-backpressure-and-stream-failure-modes.md`; LO1, LO6, LO7.

## 4. Intermediate application questions — grouped by topic

For each question, provide a short decision or analysis and justify it. Each is worth **3 points**: 1 for correct diagnosis/choice, 1 for reasoning grounded in the supplied facts, and 1 for identifying an important limitation or correctness risk.

### Topic 1

**I1. Latency budget.**  
**Illustrative assumptions:** A risk API has a proposed p95 end-to-end response objective of 500 ms. The team allocates 120 ms to event consumption/processing, 80 ms to view update, 150 ms to the serving read, 100 ms to network/application overhead, and 50 ms as unallocated headroom.

1. Sum the component allocations and headroom.
2. Explain whether the arithmetic alone proves that the end-to-end p95 will be at most 500 ms.
3. State what should be measured to validate the budget.

- **Mapping:** `01-real-time-use-cases-and-latency-budgets.md`; LO1.

### Topic 2

**I2. Partition and consumer-group reasoning.**  
**Illustrative assumptions:** A topic has 12 partitions. One consumer group has 4 healthy consumer instances. Assume the chosen broker/consumer model assigns each partition to at most one active consumer in this group at a time, and work is evenly distributed.

1. What is the approximate number of partitions per consumer?
2. How many consumer instances could be active before the 12-partition limit prevents further useful partition-level parallelism?
3. Name two reasons actual throughput may still be uneven.

- **Mapping:** `02-event-brokers-topics-partitions-and-retention.md`; LO2.

### Topic 3

**I3. Window and late-event policy.**  
**Illustrative assumptions:** A processor uses one-minute event-time tumbling windows. Its watermark is defined for this exercise as `maximum event time observed so far − 2 minutes`. The maximum event time observed is 14:08:00, so the watermark is 14:06:00. A new event has event time 14:04:30 and arrives at processing time 14:09:10. The system's declared policy is to accept late events only while the relevant window remains open; no additional allowed-lateness period is configured.

1. Which one-minute event-time window contains the event?
2. Is the event late relative to the current watermark, and has the watermark passed that window's end?
3. Given the stated policy, should the event update the already-closed window as an on-time event? If not, name a safe policy-defined disposition (for example, record the late event and drop it from the closed window, or route it to a correction/recomputation path if the architecture explicitly supports one).

- **Mapping:** `03-event-time-processing-ordering-and-watermarks.md`; LO3.

### Topic 4

**I4. Crash after sink write.**  
**Illustrative assumptions:** A processor reads event `E-77`, successfully writes a current-state upsert to a destination, then crashes before committing its input progress. On restart, it reads `E-77` again.

Explain the likely delivery behavior and propose two destination/processing design controls that reduce duplicate business effects. State one guarantee you must not assume without checking the implementation.

- **Mapping:** `04-stream-processing-state-and-delivery-semantics.md`; LO4.

### Topic 5

**I5. Snapshot-plus-stream and replay.**  
**Illustrative assumptions:** A database snapshot is consistent as of source log position `L100`. The change stream contains `L101`, `L102`, and later positions. The snapshot is loaded to a new target.

1. State the intended stream start boundary.
2. Explain the risk of starting after `L101` or replaying `L101` without duplicate-safe semantics.
3. Name three checks required before replaying a historical interval.

- **Mapping:** `05-cdc-event-backbones-and-replay.md`; LO5.

### Topic 6

**I6. Choose a serving pattern from access patterns.**  
**Illustrative assumptions:** Two consumers need different outputs:
- Consumer A: fetch the current risk state for one customer ID, with a proposed p95 read objective below 50 ms.
- Consumer B: run interactive analytical queries over many customers, filtering by several dimensions and grouping by risk band.

Recommend a serving pattern for each and explain why forcing both consumers onto one store may be a poor fit. You may state reasonable assumptions, but make them explicit.

- **Mapping:** `06-real-time-serving-stores-and-materialized-views.md`; LO6.

### Topic 7

**I7. Diagnose lag.**  
**Illustrative assumptions:** For ten consecutive one-minute intervals, input remains near 10,000 events/s while successful output remains near 8,000 events/s. Oldest-event age rises throughout the interval. Sink write latency also rises; processor CPU remains moderate.

Identify the likely immediate bottleneck, explain why scaling processor instances alone may not solve it, and name three additional signals or checks.

- **Mapping:** `07-late-events-backpressure-and-stream-failure-modes.md`; LO7.

### Cross-topic

**I8. Delivery, freshness, and recovery.**  
A team proposes to commit consumer progress immediately after reading each event so that lag stays low, then retry destination writes asynchronously without tracking their outcomes. Explain the core correctness risk and propose a safer high-level pattern. Your answer must distinguish a progress/lag metric from proof that data is durable and queryable.

- **Mapping:** `04-stream-processing-state-and-delivery-semantics.md`, `06-real-time-serving-stores-and-materialized-views.md`, `07-late-events-backpressure-and-stream-failure-modes.md`; LO4, LO6, LO7.

## 5. Advanced architecture and troubleshooting scenarios

Each scenario is worth **5 points**: 2 for diagnosis/design, 1 for evidence or calculations, 1 for correctness/ordering/retention risk, and 1 for a validation or durable-fix plan. More than one architecture can be acceptable if the assumptions and trade-offs are explicit.

### A1. Month-end sink slowdown and backlog

**Illustrative assumptions:**
- Input rate: 12,000 events/s.
- Effective successful processing rate during the slowdown: 9,000 events/s.
- Duration: 10 minutes (600 seconds).
- Starting backlog: 0 events.
- After repair, input returns to 12,000 events/s and measured sustainable processing capacity is 15,000 events/s.
- For the arithmetic, assume stable average rates and no additional bottleneck.

Tasks:
1. Estimate the backlog at the end of the slowdown.
2. Estimate idealized drain time after capacity recovers.
3. Describe the first checks you would make before scaling.
4. Give a mitigation plan that protects the sink and live traffic while accounting for retention and duplicate risk.

- **Mapping:** `01-real-time-use-cases-and-latency-budgets.md`, `02-event-brokers-topics-partitions-and-retention.md`, `04-stream-processing-state-and-delivery-semantics.md`, `06-real-time-serving-stores-and-materialized-views.md`, `07-late-events-backpressure-and-stream-failure-modes.md`; LO1, LO2, LO4, LO6, LO7.

### A2. Poison message in a keyed stream

**Illustrative assumptions:** A partition contains state-changing events `C1`, `C2`, and `C3` for the same customer, in source order. `C2` is malformed and repeatedly fails validation; `C3` changes the same customer's risk state. The business contract requires state transitions for this customer to be applied in order. The original event can be retained securely for repair.

Compare:
- Pausing the affected partition/key path.
- Quarantining `C2` and continuing with `C3`.
- Repairing the consumer/schema and replaying `C2`.

Recommend an immediate response and a recovery plan. Identify the ordering, availability, and correctness trade-off.

- **Mapping:** `03-event-time-processing-ordering-and-watermarks.md`, `04-stream-processing-state-and-delivery-semantics.md`, `05-cdc-event-backbones-and-replay.md`, `07-late-events-backpressure-and-stream-failure-modes.md`; LO3, LO4, LO5, LO7.

### A3. Consumer crash, ambiguous sink outcome, and replay

**Illustrative assumptions:** A consumer writes event `T-900` to a serving store. The request times out; logs cannot establish whether the store applied it. The consumer then crashes before committing progress. A restart will read `T-900` again. The event represents a transaction whose total must not be incremented twice. Source and broker history are still available.

Tasks:
1. Identify the ambiguity and possible duplicate effect.
2. Specify the information you would inspect before retry/replay.
3. Propose an idempotency or version-aware strategy and a reconciliation check.
4. Explain why a successful restart alone does not prove correctness.

- **Mapping:** `04-stream-processing-state-and-delivery-semantics.md`, `05-cdc-event-backbones-and-replay.md`, `06-real-time-serving-stores-and-materialized-views.md`, `07-late-events-backpressure-and-stream-failure-modes.md`; LO4, LO5, LO6, LO7.

### A4. Replay threatens live freshness

**Illustrative assumptions:** A live consumer receives 5,000 events/s. Shared processing and sink capacity is 7,000 events/s. A replay job is proposed to consume 2,500 events/s of that same total capacity. The live freshness objective is important, and the replay can be paused and resumed. Assume these rates remain stable and capacity is shared as stated.

Tasks:
1. Calculate the capacity left for live events during replay.
2. Decide whether live backlog rises or falls under these assumptions.
3. Recommend replay admission controls and validation gates.
4. Explain how you would report recovery if some source history had already expired.

- **Mapping:** `01-real-time-use-cases-and-latency-budgets.md`, `02-event-brokers-topics-partitions-and-retention.md`, `05-cdc-event-backbones-and-replay.md`, `06-real-time-serving-stores-and-materialized-views.md`, `07-late-events-backpressure-and-stream-failure-modes.md`; LO1, LO2, LO5, LO6, LO7.

## 6. Quantitative exercises — intermediate difficulty

These questions test arithmetic and interpretation using supplied assumptions; they do not require vendor-specific knowledge. Show formulas, substitutions, units, and conclusions. Each exercise is worth **4 points**: 2 for correct arithmetic with units, 1 for interpretation, and 1 for stating a relevant assumption or limitation.

### Q1. Latency-budget arithmetic

**Illustrative assumptions:** A proposed end-to-end latency budget is allocated as follows: source-to-broker 70 ms, broker wait 40 ms, processing 90 ms, serving-store update 110 ms, and API/read/network 140 ms. There is 50 ms of explicit headroom. The proposed objective is 500 ms.

Tasks:
1. Calculate the sum of component allocations.
2. Add headroom and compare with the 500 ms objective.
3. Explain why a component-budget sum is a planning tool, not proof that a measured p95 end-to-end objective is satisfied.

- **Mapping:** `01-real-time-use-cases-and-latency-budgets.md`; LO1.

### Q2. Partition-level parallelism

**Illustrative assumptions:** A topic has 18 partitions. A consumer group has 6 healthy instances. Assume each partition is assigned to at most one active instance in the group and partitions are evenly distributed.

Tasks:
1. Estimate the partitions per instance.
2. What is the maximum number of instances that can be usefully active for partition-level parallelism under this model?
3. Explain why actual throughput can still be uneven.

- **Mapping:** `02-event-brokers-topics-partitions-and-retention.md`; LO2.

### Q3. Backlog growth and drain time

**Illustrative assumptions:** Input is 7,500 events/s. Successful processing is 6,000 events/s for 8 minutes (480 seconds), starting from zero backlog. After repair, processing capacity is 9,000 events/s while input remains 7,500 events/s. Ignore variability and other bottlenecks for the arithmetic.

Tasks:
1. Calculate the backlog created during the incident.
2. Calculate the net drain rate after repair.
3. Estimate idealized drain time.
4. State two real-world factors that could make the actual drain time longer.

- **Mapping:** `07-late-events-backpressure-and-stream-failure-modes.md`; LO7.

### Q4. Event-time window and watermark

**Illustrative assumptions:** A stream uses fixed one-minute windows `[HH:MM:00, next HH:MM:00)`. Its watermark is `maximum event time observed − 90 seconds`. The maximum event time observed is 10:12:00, so the watermark is 10:10:30. There is no allowed-lateness period after a window closes. An event with event time 10:09:40 arrives now.

Tasks:
1. Identify the event-time window containing the event.
2. Compare the event timestamp to the watermark.
3. Under the stated policy, explain whether the event should be treated as on-time or late and what must be checked before deciding its final disposition.

- **Mapping:** `03-event-time-processing-ordering-and-watermarks.md`; LO3.

### Q5. Retention and replay planning

**Illustrative assumptions:** A recovery plan estimates 90 minutes to detect the issue, 150 minutes to diagnose/repair it, 240 minutes to replay the required interval, and 60 minutes of safety margin. Treat these as sequential planning components for this exercise. The broker and source log have separate retention settings.

Tasks:
1. Calculate the planning window suggested by the four components, in minutes and hours.
2. State the minimum comparison you must make against retention.
3. Explain what changes if broker retention covers the window but the source log needed to reconstruct CDC changes has already expired.

- **Mapping:** `02-event-brokers-topics-partitions-and-retention.md`, `05-cdc-event-backbones-and-replay.md`, `07-late-events-backpressure-and-stream-failure-modes.md`; LO2, LO5, LO7.

## 7. Integrated end-to-end architecture challenge

### Capstone — Northbridge real-time risk monitoring

**Difficulty: Advanced (integrated architecture design).** Multiple designs can earn full credit when they satisfy the stated invariants and explain assumptions/trade-offs.

**Scenario:** Northbridge Bank is fictional. All numbers and targets below are **illustrative assumptions for this assessment**, not production recommendations or roadmap requirements.

Northbridge wants a streaming platform that consumes account and transaction changes from operational databases, maintains a current-risk view, records risk alerts, and serves two consumers:
- A customer-risk API that looks up one customer by ID and has a proposed p95 read objective below 50 ms.
- An analyst dashboard that filters and groups across many customers and needs fresh data within 60 seconds of the defined source event boundary.

Additional assumptions:
- The API should expose whether the returned view is stale or current according to a measurable freshness rule.
- Source changes are captured through CDC.
- Events may arrive out of order and may be delivered more than once.
- The processor may crash after a destination write but before input progress is committed.
- The serving store may be unavailable for 15 minutes.
- A snapshot is consistent at source log position `L500`; subsequent change positions are `L501`, `L502`, and onward.
- The design must support replay from retained history, but no numeric retention duration is prescribed; you must calculate and justify a duration from your stated recovery assumptions.
- A single customer’s state transitions must not be applied out of order.
- External alerts should not be emitted twice for the same logical alert.
- No specific broker, processor, cloud, database, or vendor product is mandated.

### Deliverables

Prepare a concise architecture package with the following subsections.

**C1. Requirements and latency/freshness contract (3 points)**

- **Mapping:** `01-real-time-use-cases-and-latency-budgets.md`; LO1.

- State the event-to-queryable-view freshness boundary and how it is measured.
- Separate the API read-latency objective from data freshness.
- Allocate a proposed end-to-end latency/freshness budget with component boundaries and explain how you will validate it.
- State which requirements are hard constraints and which are proposed targets requiring business confirmation.

**C2. Broker, key, partition, and retention design (3 points)**

- **Mapping:** `02-event-brokers-topics-partitions-and-retention.md`; LO2.

- Define event identity and a key suitable for per-customer ordering.
- Explain partition and consumer-group choices and the limit on useful parallelism.
- Propose a retention-planning method that covers detection, repair, restore/replay, and safety margin; include source-log retention.
- Explain how you will detect hot partitions or a stalled partition.

**C3. Event-time and state/delivery design (4 points)**

- **Mapping:** `03-event-time-processing-ordering-and-watermarks.md`, `04-stream-processing-state-and-delivery-semantics.md`; LO3, LO4.

- Distinguish event time from source commit time and processing time.
- Define a watermark/late-event policy and state what happens to late corrections.
- Explain state/checkpoint recovery and the crash-after-sink-write case.
- Specify idempotency/version safeguards for current state and duplicate-alert prevention.

**C4. CDC, replay, and reconciliation plan (3 points)**

- **Mapping:** `05-cdc-event-backbones-and-replay.md`; LO5.

- Describe snapshot-plus-stream handoff from `L500` to later changes without a gap.
- Define the conditions under which replay is safe, how replay rate is controlled, and how live traffic is protected.
- Specify reconciliation checks and what you will do if required history has expired.

**C5. Serving stores and view update semantics (3 points)**

- **Mapping:** `06-real-time-serving-stores-and-materialized-views.md`; LO6.

- Recommend a serving pattern for the per-customer API and a pattern for analytical filtering/grouping. You may recommend separate stores/views.
- Define keys, versions, upsert behavior, delete/correction behavior, and rebuild approach.
- Explain how the API/dashboard detects and communicates staleness.

**C6. Failure-mode analysis and operational readiness (4 points)**

- **Mapping:** `07-late-events-backpressure-and-stream-failure-modes.md`; LO7, with dependencies on Topics 1–6.

- Include at least eight failure modes, including sink outage, poison message/schema incompatibility, consumer/checkpoint failure, retry storm, retention expiry, hot partition, and replay overload.
- For each, identify symptom/detection, immediate mitigation, durable fix/recovery, and correctness risk.
- Include alerting for absence of data, lag/freshness, sink health, retry/quarantine, and reconciliation.
- Define incident recovery acceptance criteria and list the evidence required before declaring recovery.

**Capstone scoring:** 20 points total as listed above. Full-credit responses need not match one specific architecture; they must satisfy the stated constraints, preserve per-customer ordering, avoid duplicate external alerts, make assumptions explicit, and justify trade-offs.

## 8. Scoring rubric and recommended mastery thresholds

The scoring model below is **recommended assessment guidance**, not a requirement from the repository or a claim that the roadmap prescribes these cutoffs.

### 8.1 Point allocation

| Section | Maximum |
|---|---:|
| 3. Beginner questions | 16 |
| 4. Intermediate application | 24 |
| 5. Advanced scenarios | 20 |
| 6. Quantitative exercises | 20 |
| 7. Integrated capstone | 20 |
| **Total** | **100** |

### 8.2 Recommended interpretation

| Score | Suggested interpretation | Recommended next step |
|---|---|---|
| 90–100 | Strong module readiness | Review any remaining errors; proceed to the project with a peer review if available |
| 80–89 | Ready with targeted gaps | Complete the remediation items and revise the weakest artifact |
| 70–79 | Developing; not yet consistently production-oriented | Revisit weak topics, redo quantitative exercises, and resubmit the capstone |
| Below 70 | Foundations need reinforcement | Study Topics 1–7 in sequence and retake the assessment |

**Mastery guardrails:** A high total score should not hide a critical weakness. Before calling yourself ready for the project, aim for:
- At least 70% on each topic's directly mapped items. For this diagnostic, count the beginner questions for that topic (B1–B14), its primary intermediate question (I1–I7), and the quantitative item only where the coverage map explicitly maps it to that topic (Q1–Q5); score cross-topic scenarios against their stated rubrics and use them as additional evidence. Do not add secondary mappings twice to the 100-point total.
- No unresolved capstone defect that permits data loss, unbounded retries, unsafe duplicate alerts, a snapshot/stream gap, or stale writes overwriting newer state.
- Correct units and reproducible calculations in all quantitative exercises.
- Explicitly documented assumptions wherever the architecture depends on business policy or technology-specific guarantees.

These guardrails are recommendations. Adjust them with an instructor or reviewer if the assessment is used in a formal program. Because some questions intentionally test multiple topics, use the coverage map and written reasoning—not a mechanically summed cross-topic subtotal alone—to diagnose topic-level mastery.

### 8.3 Partial-credit rubric

- **Definition/short answer:** correct core meaning earns full credit; a vague synonym without the distinction earns partial credit.
- **Calculation:** award arithmetic credit only when units and interval conversions are correct; award interpretation credit only when the result is tied to the stated assumptions.
- **Architecture judgment:** full credit requires a fit to the stated access pattern/SLO, a clear rationale, and a trade-off or limitation. An alternative is acceptable if its assumptions are explicit and it meets the constraints.
- **Troubleshooting:** full credit requires evidence that discriminates between plausible causes, a bounded mitigation, a correctness-risk statement, and a durable fix or validation step.
- **Capstone:** score each listed deliverable separately. Do not award full credit for a diagram alone without delivery, state, replay, serving, and failure semantics.

## 9. Answer key and explanations

Attempt the questions first. Explanations below are intentionally concise enough to support self-assessment while showing the reasoning expected. Where a design choice is judgment-based, equivalent answers are acceptable when the learner states assumptions and addresses the specified correctness constraints.

### 9.1 Beginner answer key

**B1 — End-to-end latency and freshness**  
End-to-end latency measures elapsed time across the defined pipeline boundary, while freshness describes how recently the returned view reflects the required source/event state. A query can respond quickly from a stale view. A valid answer defines the start and end measurement points.

**B2 — Business objective versus budget**  
The objective describes the measurable outcome (for example, a proposed p95 API response below a stated limit, or source-to-queryable freshness within a stated interval). The budget allocates time or delay across stages. Suitable boundaries include source capture, broker arrival, processing, sink visibility, and API read. The example's target must be measurable and tied to the use case.

**B3 — Broker terms**  
A topic is a named stream/category; a partition is an ordered sequence/parallelism unit within it; a key associates related records and often determines partition placement; an offset identifies a position in a partition; a consumer group is a set of consumers sharing work under a group-assignment model. Partition-level parallelism is limited by the number of partitions, while ordering is generally scoped to a partition or keying design—not automatically global across all partitions.

**B4 — Lag versus retention**  
Lag is unprocessed distance/work or delay. Retention is how long records remain available. If a required record expires before the consumer catches up, the consumer cannot retrieve that record from the broker history alone. Recovery may need an archive, source log, authoritative snapshot, or documented gap process.

**B5 — Time types**  
Event time represents when the business event is said to have occurred; ingestion time is when an ingestion boundary accepted/observed it; processing time is when the processor handles it. Network delay, source buffering, late delivery, clock skew, and differing timestamp semantics can make them differ.

**B6 — Watermark**  
A watermark is a progress estimate/processing policy for event time used to decide when event-time results may advance or windows may close. It is not proof that no older event can ever arrive; late data can still arrive due to delay, skew, retries, or source behavior. The system needs an explicit late-event policy.

**B7 — Checkpoint**  
A checkpoint persists enough processing progress/state to recover from a failure according to the framework's guarantees. It does not automatically make an arbitrary external sink write atomic with input progress. The sink may have committed before a crash while the checkpoint/progress did not, or progress may advance without a durable sink write if the design is wrong.

**B8 — At-least-once and idempotency**  
At-least-once permits reprocessing/duplicate delivery to avoid losing work under the relevant guarantee. An idempotent operation can be applied repeatedly with the same logical result, for example setting customer state to a specific source version or recording an event ID once. This safety depends on the destination's actual semantics and correct identity/version design.

**B9 — CDC and source position**  
CDC captures database changes, often from a transaction/log mechanism or equivalent change stream. A source log position/version locates a change in the source's change history and helps establish ordering, snapshot boundaries, and replay progress. Exact guarantees depend on the source/connector.

**B10 — Snapshot-plus-stream handoff**  
A snapshot represents state at a defined boundary; the stream must begin at the corresponding next change position (or use a documented overlap/deduplication protocol). A gap can miss changes between snapshot and stream start. Uncontrolled overlap can duplicate changes or apply them against an inconsistent baseline.

**B11 — Materialized view and access pattern**  
A materialized view stores a derived result so a consumer can query it without recomputing the full stream. Store selection should follow access pattern, latency, freshness, query flexibility, concurrency, and consistency needs. A store optimized for one-key lookups may be poor for flexible analytical filters/grouping.

**B12 — Version-aware upsert**  
An upsert inserts or updates a record. A version-aware rule applies an update only if its source version/order is newer than the currently stored version (according to the contract). This prevents an older late event from overwriting newer state. Event timestamps alone are insufficient if their semantics or clock quality are unreliable; source versions may be stronger when available.

**B13 — Backlog, lag, backpressure, saturation**  
Backlog is accumulated unprocessed work. Consumer lag describes how far the consumer is behind according to a position or time measure. Backpressure is flow control that slows upstream work when downstream cannot keep up. Saturation is a resource or component operating near its useful capacity. Definitions can overlap operationally but are not synonyms.

**B14 — Poison message and quarantine**  
A poison message repeatedly fails processing under the current code/schema/policy. A DLQ/quarantine path isolates it for inspection and repair. The event may still be required for business correctness, and letting later same-key events pass it can violate ordering or completeness. A quarantine needs an owner, retention/access policy, repair/replay process, and reconciliation.

**B15 — Transport duplicate versus business duplicate**  
A transport duplicate is the same logical event delivered/processed more than once. A business duplicate effect occurs when those deliveries cause the effect to be applied twice, such as incrementing a transaction total twice or emitting the same alert twice. Idempotent writes, event identity, deduplication, or destination-side constraints can prevent the second effect.

**B16 — Signals**  
Valid examples include input/output rates, lag by partition, oldest-event age, end-to-end freshness, sink latency/error rate, processor resource use, checkpoint failures, retry rate, quarantine rate, and reconciliation discrepancy. Lag alone cannot prove freshness or correctness; CPU alone cannot prove CPU is the bottleneck; zero lag cannot prove output is correct; a fast query cannot prove the view is current.

### 9.2 Intermediate answer key

**I1 — Latency budget**

1. Sum: \(120 + 80 + 150 + 100 + 50 = 500\) ms.
2. The arithmetic fits the proposed 500 ms allocation, but does not prove measured p95 end-to-end latency will meet 500 ms. Component percentile values do not necessarily compose into the same end-to-end percentile, and correlated tail delays, queues, and measurement-boundary differences matter.
3. Measure end-to-end latency at the defined boundary and stage-level latency distributions under representative load; validate p95 and relevant tail behavior, not only averages. Check that the freshness objective is separately measured.

**I2 — Partition/consumer group**

1. \(12\) partitions ÷ \(4\) instances = approximately **3 partitions per instance** under the even-distribution assumption.
2. Up to **12 active instances** can be useful for partition-level parallelism under the stated one-active-consumer-per-partition model; beyond that, some instances cannot own a partition in that group.
3. Throughput may still be uneven due to hot keys/partition skew, different event sizes, slow sink writes, unequal work, external-call latency, or resource differences.

**I3 — Window and late event**

1. Event time 14:04:30 belongs to window **[14:04:00, 14:05:00)**.
2. Watermark 14:06:00 is later than both the event timestamp and the window end at 14:05:00; the event is late and the window is closed under the stated exercise policy.
3. The event should not update the closed window as an on-time event. The system must follow a defined disposition, such as recording the late event and excluding it from the closed result, or routing it to a correction/recomputation path if that behavior is explicitly supported. Do not silently lose the event or assume every framework supports corrections identically.

**I4 — Crash after sink write**

The event is likely to be reprocessed because input progress was not committed. That creates at-least-once behavior and a possible duplicate effect. Controls include an idempotent upsert keyed by stable event/entity ID, destination deduplication, a source-version guard, or a transaction pattern that explicitly covers the relevant boundary. Do not assume the checkpoint atomically includes arbitrary external sink effects without verifying framework/connector semantics.

**I5 — Snapshot-plus-stream**

1. The intended stream boundary is changes **strictly after `L100`**, if the snapshot is consistent as of `L100` and the source's position semantics support that interpretation.
2. Starting after `L101` could omit `L101`; replaying `L101` can apply it twice unless the target is idempotent/deduplicating or an overlap protocol is defined.
3. Check required source/broker history is still available; verify source positions and snapshot boundary; verify schema/transform version compatibility; establish sink idempotency/version semantics; estimate replay capacity; suppress duplicate external side effects; and define reconciliation criteria. Any three with reasoning are acceptable.

**I6 — Serving pattern**

Consumer A is a key-based current-state lookup. A key-value or suitably indexed operational serving store is a reasonable choice if it meets the measured p95 objective and supports safe version-aware writes. Consumer B needs flexible multi-dimensional filters/grouping; an analytical serving store or real-time OLAP-style pattern may fit better. Separate views/stores can avoid forcing incompatible read/write workloads onto one system. Alternatives are acceptable if access patterns, latency, freshness, query flexibility, and consistency assumptions are justified. The store must not be chosen solely because it is popular.

**I7 — Diagnose lag**

The rising sink write latency with moderate processor CPU suggests a sink or downstream write-path bottleneck is a leading hypothesis. More processor instances may send more concurrent writes and worsen sink saturation; they may also not help if a hot partition limits parallelism. Check per-partition lag/throughput, sink errors and connection-pool waits, retry rate, external dependency latency, checkpoint duration, event-size/key skew, and broker/network health. A strong answer distinguishes hypothesis from confirmed cause.

**I8 — Progress committed before durable destination write**

The design can report low lag while data has not been durably written or is not queryable; a failure may lose events from the consumer's recovery path. A safer pattern ties progress advancement to a defined durable processing boundary, uses a supported transaction where available, or uses a durable outbox/inbox/idempotent write protocol with tracked outcomes. Measure sink durability/visibility and reconcile progress against destination versions/records. Low lag is not proof of correctness.

### 9.3 Advanced scenario answer key

**A1 — Month-end sink slowdown**

1. Deficit: \(12{,}000 - 9{,}000 = 3{,}000\) events/s. Backlog after 600 s: \(3{,}000 \times 600 = \mathbf{1{,}800{,}000}\) events.
2. After repair, net drain rate: \(15{,}000 - 12{,}000 = 3{,}000\) events/s. Idealized drain time: \(1{,}800{,}000 / 3{,}000 = 600\) s = **10 minutes**.
3. Check the first degraded boundary, sink latency/error rate, input/output rates, per-partition lag/skew, retries, source/broker progress, and checkpoint health before scaling.
4. Mitigation should stabilize/repair the sink, bound retries with backoff/jitter, reduce or pause competing replay/optional work, and resume consumption gradually. Monitor retention headroom and live freshness. Verify ambiguous sink outcomes, event identity/version guards, and duplicate-safe updates. Reconcile source coverage, destination versions/counts/totals, and alert side effects. The 10-minute drain is idealized and may be longer in real operation.

**A2 — Poison message and ordering**

Given the stated per-customer ordering requirement, the safest immediate response is to stop later state transitions for the affected key/partition (or otherwise park dependent events) while retaining and alerting on `C2`. Quarantining `C2` and continuing with `C3` improves throughput but violates the stated order unless `C3` can be proven independent or a documented correction process exists. Repair the schema/consumer, validate `C2`, replay it at the correct position, then process later events and reconcile the customer's state. Pausing the entire partition may affect other keys if the partition is the isolation unit; this is an availability cost to document. A valid alternative must preserve the per-customer ordering invariant.

**A3 — Ambiguous sink outcome**

1. The timeout does not prove the write failed. The destination may have applied `T-900`; reprocessing can increment the total twice.
2. Inspect event ID/source version, destination state or operation ID, input progress/checkpoint, sink logs/acknowledgement if available, and any external side effect.
3. Use an idempotency key or destination-side unique event record so the logical transaction contributes once; alternatively use a versioned current-state upsert if the business operation is a state-setting operation. Reconcile transaction IDs/counts/totals against authoritative source records over the affected position range.
4. Restart success proves the process is running, not that the ambiguous effect occurred exactly once, that no event was lost, or that output is correct.

**A4 — Replay and live freshness**

1. Capacity left for live work: \(7{,}000 - 2{,}500 = \mathbf{4{,}500}\) events/s.
2. Live arrival is 5,000 events/s, so the live backlog grows by \(5{,}000 - 4{,}500 = \mathbf{500}\) events/s under the assumptions.
3. Throttle or pause replay, reserve capacity for live processing, watch live/replay lag separately, set sink latency/freshness pause conditions, verify history/schema/idempotency/side-effect policy, and reconcile before cutover.
4. If source history has expired, do not claim full replay. Determine whether an authoritative snapshot, archive, or alternate reconstruction path can restore the missing interval; reconcile the recovered result and document any irrecoverable gap and business disposition.

### 9.4 Quantitative answer key

**Q1 — Latency budget**

1. Component sum: \(70 + 40 + 90 + 110 + 140 = 450\) ms.
2. Including 50 ms headroom: \(450 + 50 = \mathbf{500}\) ms, equal to the proposed objective.
3. The sum is a planning allocation. Measured end-to-end p95 must be tested at the defined boundaries and load; component percentile distributions, correlated delays, queueing, and measurement differences can invalidate a simple percentile sum.

**Q2 — Partition-level parallelism**

1. \(18\) partitions ÷ \(6\) instances = **3 partitions per instance** on average.
2. Maximum useful active instances under the given model: **18**, because each partition can be assigned to at most one active instance.
3. Skewed keys, event-size/work differences, slow sinks, external dependencies, and resource differences can cause unequal throughput.

**Q3 — Backlog growth and drain**

1. Deficit: \(7{,}500 - 6{,}000 = 1{,}500\) events/s. Duration: 8 minutes = 480 s. Backlog: \(1{,}500 \times 480 = \mathbf{720{,}000}\) events.
2. Net drain rate: \(9{,}000 - 7{,}500 = \mathbf{1{,}500}\) events/s.
3. Idealized drain time: \(720{,}000 / 1{,}500 = 480\) s = **8 minutes**.
4. Real drain can take longer due to hot partitions, variable event sizes, checkpointing/state restore, retry overhead, sink limitations, network problems, or new arrival spikes. Any two are acceptable.

**Q4 — Event-time window and watermark**

1. Event time 10:09:40 belongs to **[10:09:00, 10:10:00)**.
2. The watermark is 10:10:30, later than the event time, so the event is late relative to the watermark.
3. Under the stated no-additional-lateness policy, the event should be treated as late because the watermark has passed the window end. The exact disposition—drop with observability, correct/retract a previous result, or route for controlled recomputation—must follow the declared policy and framework semantics. Do not silently discard it or assume every system handles it identically.

**Q5 — Retention and replay planning**

1. Total: \(90 + 150 + 240 + 60 = \mathbf{540}\) minutes = **9 hours**.
2. Compare the planning window with the retention/availability of both broker history and source CDC log, and verify that the required positions remain available long enough for detection, repair, and replay. Confirm the estimate includes the relevant recovery/catch-up assumptions.
3. Broker history alone may not reconstruct source changes if the required source log has expired and the broker does not contain the complete authoritative change history. Investigate an archive or authoritative snapshot/reload. If completeness cannot be restored, document the interval/gap and obtain a business disposition rather than claiming complete recovery.

### 9.5 Capstone scoring guide / expected evidence

This is a scoring guide, not a single required architecture.

**C1 — Requirements and latency/freshness contract (3 points)**
- 1 point: defines the source boundary and when a version becomes queryable; measures freshness independently from read latency.
- 1 point: includes component budgets and an end-to-end validation plan using measured distributions.
- 1 point: distinguishes stated constraints from assumptions/targets requiring confirmation.

**C2 — Broker, key, partition, and retention (3 points)**
- 1 point: stable event identity and per-customer key/order rationale.
- 1 point: partition/group design explains useful parallelism and hot-partition monitoring.
- 1 point: retention covers detection + repair + replay/catch-up + margin for broker and source log.

**C3 — Event time and state/delivery (4 points)**
- 1 point: distinguishes event, source commit, and processing times; defines late-data policy.
- 1 point: explains checkpoint and recovery boundary.
- 1 point: protects current-state writes with idempotency/source version.
- 1 point: prevents duplicate alerts through stable logical alert identity and durable deduplication/idempotency.

**C4 — CDC, replay, reconciliation (3 points)**
- 1 point: snapshot consistent at `L500`, stream resumes at the documented next change position without a gap.
- 1 point: replay has history, capacity, idempotency, and live-traffic controls.
- 1 point: reconciliation and expired-history disposition are explicit.

**C5 — Serving stores and views (3 points)**
- 1 point: store/pattern selected for point lookup and analytical filtering/grouping, with justification.
- 1 point: key/version/upsert/delete/correction/rebuild behavior is defined.
- 1 point: freshness is observable and staleness is communicated.

**C6 — Failure-mode analysis and operations (4 points)**
- 1 point: at least eight relevant failure modes with specific detection signals.
- 1 point: immediate mitigations are bounded and fit the fault; durable fixes are identified.
- 1 point: duplicate/loss/order/retention/replay correctness risks are addressed.
- 1 point: recovery acceptance requires evidence and reconciliation, not just a running job or low lag.

Full credit requires the entire design to satisfy the per-customer ordering requirement and prevent duplicate logical alerts. If a proposed design breaks either invariant, the relevant capstone subscore should not receive full credit even if the diagram is polished.

## 10. Remediation map: common wrong answers to lesson filenames

| Common error | What to review | Corrective task |
|---|---|---|
| Treating freshness as the same as query latency | `01-real-time-use-cases-and-latency-budgets.md` | Define source boundary, queryable boundary, percentile, and measurement method |
| Adding component p95 values and assuming the result proves end-to-end p95 | `01-real-time-use-cases-and-latency-budgets.md` | Compare allocations with measured end-to-end distributions |
| Assuming more consumers always increase throughput | `02-event-brokers-topics-partitions-and-retention.md` | Recalculate partition-level parallelism and inspect skew |
| Confusing lag with retention or assuming expired events remain replayable | `02-event-brokers-topics-partitions-and-retention.md`, `05-cdc-event-backbones-and-replay.md` | Build a retention/recovery worksheet for broker and source history |
| Treating event time as processing time | `03-event-time-processing-ordering-and-watermarks.md` | Rework the timeline/window/watermark exercises |
| Assuming a watermark proves no older event can arrive | `03-event-time-processing-ordering-and-watermarks.md` | State a late-event policy and consequences |
| Assuming checkpoints guarantee exactly-once effects in any sink | `04-stream-processing-state-and-delivery-semantics.md` | Draw the crash points around sink write and progress commit |
| Treating a timeout as proof a write failed | `04-stream-processing-state-and-delivery-semantics.md`, `06-real-time-serving-stores-and-materialized-views.md` | Add idempotency/event identity or an outcome lookup |
| Starting CDC after an arbitrary snapshot without a position contract | `05-cdc-event-backbones-and-replay.md` | Document the snapshot boundary and stream start/overlap strategy |
| Replaying without checking sink side effects or capacity | `05-cdc-event-backbones-and-replay.md`, `07-late-events-backpressure-and-stream-failure-modes.md` | Create a replay admission and reconciliation plan |
| Choosing one serving store for incompatible access patterns | `06-real-time-serving-stores-and-materialized-views.md` | Complete an access-pattern comparison and justify the chosen view |
| Allowing an older event to overwrite a newer view | `06-real-time-serving-stores-and-materialized-views.md` | Specify key, source version, upsert condition, delete/correction behavior |
| Treating every lag spike as under-provisioning | `07-late-events-backpressure-and-stream-failure-modes.md` | Compare input/output rates, per-partition lag, sink latency, and retry rate |
| Retrying indefinitely or dead-lettering without ownership | `07-late-events-backpressure-and-stream-failure-modes.md` | Write a bounded retry/quarantine policy with ordering and recovery rules |
| Declaring recovery complete when lag reaches zero | `05-cdc-event-backbones-and-replay.md`, `06-real-time-serving-stores-and-materialized-views.md`, `07-late-events-backpressure-and-stream-failure-modes.md` | Reconcile positions, versions, keys, counts/totals, deletes, and side effects |

## 11. Final readiness checklist for the module project

Before beginning `Projects/09-real-time-risk-monitoring-architecture.md`, confirm that you can produce and defend each artifact.

### Requirements and broker design
- [ ] State a real-time use case with measurable latency, freshness, availability, throughput, and correctness expectations.
- [ ] Show where each metric begins and ends; distinguish API latency from source-to-queryable freshness.
- [ ] Define topic/partition/key choices, consumer-group assumptions, ordering scope, and useful parallelism.
- [ ] Justify retention for the expected outage, diagnosis, repair, replay/catch-up, and safety margin.

### Event-time and processing semantics
- [ ] Define event, ingestion, source commit, and processing timestamps used by the design.
- [ ] Document windows, watermark assumptions, allowed lateness, and late-event/correction behavior.
- [ ] Document state/checkpoint recovery and the actual transaction boundary.
- [ ] Explain delivery guarantees, event identity, idempotency, duplicate detection, and stale-update protection.

### CDC, serving, and recovery
- [ ] Define the snapshot-plus-stream boundary and source-position handling.
- [ ] State replay prerequisites, retention feasibility, rate limits, side-effect controls, and cutover steps.
- [ ] Choose serving patterns from explicit access patterns, latency/freshness needs, and query shapes.
- [ ] Specify materialized-view key, version, upsert, delete/correction, cache/invalidation (if relevant), and rebuild semantics.
- [ ] Define reconciliation checks and the response to unavailable/expired history.

### Reliability and operations
- [ ] Show where backlog can accumulate and how it propagates.
- [ ] Distinguish temporary bursts from sustained capacity shortage with rates and backlog slope.
- [ ] Include a failure-mode matrix with detection, immediate mitigation, durable fix, and correctness risk.
- [ ] Define bounded retries, backoff/jitter, retry budgets, quarantine ownership, and poison-message ordering policy.
- [ ] Monitor absence of data, end-to-end freshness, per-partition lag, input/output rates, sink health, checkpoint health, retry/quarantine, and reconciliation.
- [ ] Define recovery acceptance criteria that require both operational health and data correctness.
- [ ] Identify assumptions, trade-offs, and technology-specific guarantees that must be verified during implementation.

**Ready to proceed when:** the architecture package is internally consistent, quantitative assumptions are explicit, replay and recovery are feasible under the retention plan, and no known design path silently loses required data or creates duplicate business effects. Treat this as a recommended readiness gate, not a formal repository requirement.
