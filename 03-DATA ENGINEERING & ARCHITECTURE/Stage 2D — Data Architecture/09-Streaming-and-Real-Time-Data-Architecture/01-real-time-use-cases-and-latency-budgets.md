# Real-Time Use Cases and Latency Budgets

> **Purpose:** Learn to turn a business need for timely data into a measurable end-to-end latency objective, allocate a defensible budget across a data path, and choose the simplest processing model that satisfies the objective without sacrificing required correctness or operational reliability.

> **Scope and source note:** This lesson follows the learning objectives and sequence in `roadmap-Streaming-and-Real-Time-Data-Architecture.md`. The supplied roadmap says the topic files were empty when it was written and that its scenarios, numbers, exercises, and targets are illustrative recommendations—not existing repository requirements. The Northbridge Bank scenario and all numeric values below are therefore explicitly fictional assumptions for learning, not benchmarks or mandatory targets. The architecture discussion is vendor-neutral; verify semantics against any product selected later.

---

## 1. Title and purpose

A business stakeholder may say, “We need real-time data.” That statement is not yet an architecture requirement. “Real-time” could mean a response in 50 milliseconds, an alert within 5 seconds, a dashboard refreshed every minute, or a report ready before the next business day.

The architect’s job is to establish:

1. **Which decision or action depends on the data?**
2. **How late can the answer be before business value is lost?**
3. **Where does measurement begin and end?**
4. **Which percentile must meet the objective, and over what population and time window?**
5. **What correctness, availability, throughput, freshness, and cost constraints apply?**
6. **What is the simplest design that meets those requirements?**
7. **How will the team measure and prove that it meets them in production?**

The output of this lesson is a small architecture decision package:

- a use-case classification;
- a measurable end-to-end latency objective;
- a stage-by-stage latency budget with explicit boundaries and headroom;
- a validation and monitoring plan;
- a decision between batch, micro-batch, continuous streaming, polling, or another adequate option;
- a short Architecture Decision Record (ADR) explaining the choice and its trade-offs.

This lesson establishes the requirement and decision logic. Later lessons cover broker partitioning, event-time processing, state and delivery semantics, CDC and replay, serving stores, and failure handling in depth.

## 2. Where this topic sits in Stage 2D and its prerequisites

This is Topic 1 in `Stage 2D — Data Architecture/09-Streaming-and-Real-Time-Data-Architecture/`. It comes first because all later choices—broker, partitions, processing engine, state, CDC, serving store, and recovery—must be judged against the business latency and correctness requirement.

The module’s learning sequence is:

1. `01-real-time-use-cases-and-latency-budgets.md` — requirements and latency budget (**this lesson**)
2. `02-event-brokers-topics-partitions-and-retention.md` — event carrying, parallelism, ordering boundaries, and replay window
3. `03-event-time-processing-ordering-and-watermarks.md` — event time, ordering, windows, and watermarks
4. `04-stream-processing-state-and-delivery-semantics.md` — state, checkpoints, and delivery guarantees
5. `05-cdc-event-backbones-and-replay.md` — database changes, event backbones, and replay
6. `06-real-time-serving-stores-and-materialized-views.md` — making computed results queryable
7. `07-late-events-backpressure-and-stream-failure-modes.md` — behavior under delay, overload, and failure

### Prerequisites

The module roadmap identifies P1–P4 as the key prerequisites for this topic:

- **Measurable service targets:** latency, throughput, freshness, availability, and percentiles.
- **Volume and rate estimation:** events per second, payload sizes, peak rates, and growth.
- **Trade-offs and ADRs:** comparing options and recording why a decision was made.
- **Processing patterns:** batch, micro-batch, continuous streaming, event-driven patterns, and Lambda/Kappa at a conceptual level.

Useful repository references:

- `../02-Requirements-Constraints-and-Architecture-Decisions/04-latency-throughput-freshness-and-availability-targets.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/03-data-volume-velocity-variety-and-growth-estimation.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/06-architecture-trade-offs-and-decision-criteria.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/07-architecture-decision-records-adrs.md`
- `../03-Data-Architecture-Patterns-and-Reference-Architectures/03-lambda-and-kappa-architectures.md`
- `../03-Data-Architecture-Patterns-and-Reference-Architectures/06-event-driven-and-data-sharing-patterns.md`

If percentiles or freshness are unfamiliar, review the first reference before continuing. If the difference between batch and stream processing is unclear, review the processing-pattern references. Product-specific configuration is not a prerequisite.

## 3. Learning objectives

By the end of this lesson, you should be able to:

1. Classify a use case using the decision it supports and the cost of delay—not a vague “real-time” label.
2. Define end-to-end latency with a start point, end point, population, percentile, and measurement window.
3. Distinguish business response time from component processing latency.
4. Define latency, throughput, freshness, p50, p95, p99, tail latency, latency budget, SLI, SLO, and headroom precisely.
5. Build a stage-level budget that includes handoffs, queueing, batching, serving, and the final consumer action.
6. Explain why component p95 values do not add exactly to the end-to-end p95.
7. Relate latency to throughput, freshness, availability, correctness, and cost.
8. Compare batch, frequent incremental batch, polling, micro-batch, and continuous stream processing.
9. Account for variability, tail latency, clock skew, operational headroom, and failure recovery.
10. Design a validation plan and document the processing-model decision in an ADR.

## 4. Prerequisite concepts and readiness check

### 4.1 Readiness check

Try these without looking at the answers.

1. A pipeline processes 20,000 records per minute. Is that latency or throughput?
2. A dashboard updates every 30 seconds. Does that prove every displayed event is less than 30 seconds old?
3. A service has p95 latency of 200 ms. Does that mean every request completes within 200 ms?
4. What is missing from the requirement “the risk alert must be fast”?
5. If an event waits 4 seconds in a buffer and takes 100 ms to process, what is its approximate event-to-result latency before serving overhead?

**Answers**

1. Throughput, if the number means records completed per minute. State whether it is offered, accepted, or successfully processed throughput.
2. No. Refresh cadence is not the same as data freshness. An upstream delay can make the displayed data older.
3. No. Approximately 95% of the measured requests are at or below 200 ms under the stated measurement method; the remaining tail is slower.
4. The decision supported, scope, start and end measurement points, percentile, time window, target, correctness expectations, and failure behavior.
5. About 4.1 seconds, before any additional serving or consumer delay.

If these ideas are unclear, review the prerequisite files above before proceeding.

## 5. Beginner foundations

### 5.1 Latency and end-to-end latency

**Latency** is the elapsed time between two defined events. A latency number is meaningful only when both boundaries are named.

**End-to-end latency** is the elapsed time from a defined business-relevant start event to a defined business-relevant outcome at the end of the full path.

Examples:

- **Transaction-to-decision latency:** from a transaction being committed or accepted at its authoritative source to a risk decision being available to the authorization service.
- **Event-to-alert latency:** from the business event occurring (or being committed, if that is the chosen start) to the alert being delivered to the intended alerting system.
- **Source-to-dashboard latency:** from the source change becoming eligible for capture to the updated value being visible in a dashboard query.
- **Request response time:** from the user or caller sending a request to receiving a response. This can include network and application time outside the data pipeline.

Always define whether the start point is **event occurrence**, **source commit**, **event publication**, or some other point. These are not interchangeable. For example, a pipeline that starts measuring only when an event reaches the broker excludes source capture and publication delay.

### 5.2 Component latency versus business response time

**Component latency** measures one component or stage, such as broker acknowledgement time, processor execution time, database write time, or query time.

**Business response time** measures how long the business must wait for the result or action it needs. It often includes multiple component latencies plus queueing, scheduling, network handoffs, buffering, retries, and the consumer’s own work.

A processor may handle an individual record in 40 ms while the event-to-alert path takes 3 seconds because the record waited in a queue, a batch flush, a store write, and an alert-delivery step.

Optimizing a fast component is not useful if another stage dominates the business outcome. Start with the end-to-end objective, then use component measurements to locate the causes of delay.

### 5.3 Throughput

**Throughput** is the amount of work successfully completed per unit of time, such as records per second, transactions per second, or bytes per second.

Be precise about the point being measured:

- **Offered rate:** work arriving at the system.
- **Accepted rate:** work admitted by the system.
- **Processed rate:** work successfully handled.
- **Served rate:** results successfully made available to consumers.

If the offered rate is higher than the sustained processing rate, backlog grows. A system can have low latency at quiet times but fail its latency objective during a traffic spike.

### 5.4 Freshness

**Freshness** describes how current the data visible to a consumer is relative to a defined source or event-time reference.

One common measure is the age of the newest relevant source update visible to the consumer:

`freshness age = measurement time − source update time`

The definition must specify which timestamp is used. Freshness is not identical to event-to-result latency:

- Event-to-result latency follows a particular event through a path.
- Freshness age asks how old the latest relevant data is at the point of use.

A dashboard can refresh every 5 seconds but still display data that is 2 minutes old if ingestion is delayed. Conversely, a dashboard may show very recent data while a particular older event is still missing.

### 5.5 Percentiles: p50, p95, and p99

A **latency percentile** summarizes a distribution of observed latency values over a specified population and measurement window.

- **p50 (median):** about half the observations are at or below this value.
- **p95:** about 95% of observations are at or below this value; roughly 5% are slower.
- **p99:** about 99% are at or below this value; roughly 1% are slower.

For a sample of 10,000 requests, a p95 of 2 seconds means approximately 9,500 requests completed in 2 seconds or less and approximately 500 took longer, subject to the percentile calculation method and ties.

Percentiles do **not** mean that latency is guaranteed to stay below the value. Nor does a p99 target alone describe the absolute worst case. Define what happens when the objective is missed.

Percentiles depend on the measured population and window. Do not compare two p95 values without checking whether they cover the same path, workload, geography, event types, and time period.

### 5.6 Tail latency and variability

**Tail latency** is the slower end of the latency distribution, often discussed using p95, p99, or more extreme percentiles. **Variability** is the extent to which latency changes across observations or conditions.

Common causes of a slow tail include:

- queueing when demand approaches capacity;
- bursty input or skewed workloads;
- batch windows and periodic flushes;
- retries and timeouts;
- garbage collection, cold caches, or resource contention;
- database lock or storage delays;
- consumer lag, restarts, or rebalances;
- downstream throttling or unavailable dependencies.

Averages can hide the tail. If most alerts arrive in 300 ms but a small proportion arrive 20 seconds late, the average may look acceptable while those delayed alerts miss their business purpose.

**When it matters:** tail latency is especially important for customer-facing decisions, fraud detection, operational alerts, and any workflow where a small fraction of late results causes disproportionate harm.

### 5.7 Latency budget

A **latency budget** allocates an end-to-end latency objective across the stages and handoffs that make up the path. It is a planning and accountability tool, not a guarantee that component measurements will add to the exact end-to-end percentile.

A useful budget identifies:

- the end-to-end objective and percentile;
- start and end measurement boundaries;
- each stage’s allocated time;
- batching and queueing delays;
- network and handoff delays;
- operational headroom;
- assumptions and exclusions;
- the instrumentation and test plan.

### 5.8 SLI, SLO, and SLA

- **Service Level Indicator (SLI):** a measured signal about service behavior. Example: the percentage of eligible risk events whose event-to-decision latency is at most 5 seconds.
- **Service Level Objective (SLO):** a target for an SLI over a defined window. Example: at least 99% of eligible events should become decision-ready within 5 seconds over a rolling 30-day window.
- **Service Level Agreement (SLA):** an external or contractual commitment that may define consequences if service targets are missed.

An SLO must state the population, time window, measurement method, threshold, and treatment of excluded events. Do not call a design aspiration an SLO unless it can be measured.

### 5.9 Headroom

**Headroom** is capacity or time deliberately left unused in the plan so normal variation, bursts, and small delays can be absorbed without immediately violating the objective.

For a simple time budget:

`time headroom = end-to-end target − sum of planned stage allocations`

If the target is 5 seconds and the planned allocations total 3 seconds, the arithmetic headroom is 2 seconds. That is not a promise that every event will finish within 3 seconds or that the remaining 2 seconds can absorb every possible failure. It is a planning margin that must be validated under representative and stressed conditions.

Capacity headroom is related but different: spare processing, network, storage, or concurrency capacity above expected demand. A pipeline may have time headroom in its design but insufficient capacity headroom during a spike.

### 5.10 The basic path

A typical event-to-consumer path may look like this:

```text
Business event
   │
   ▼
Source commit / capture
   │
   ▼
Publish and network handoff
   │
   ▼
Broker acceptance / retention
   │
   ▼
Consumer wait / queue
   │
   ▼
Processing and any state lookup
   │
   ▼
Write result to serving store
   │
   ▼
Query / alert delivery / consumer action
```

Not every architecture uses every stage. A direct synchronous API may have no broker; a batch report may have a scheduler and file landing stage instead. The budget should represent the actual chosen path, not a generic diagram.

## 6. Intermediate architecture and worked latency-budget example

### 6.1 Convert a vague request into a measurable objective

A good objective answers five questions:

1. **What is being timed?** For example, each eligible card authorization event.
2. **Where does timing start?** For example, when the authoritative source commits the transaction.
3. **Where does timing stop?** For example, when the risk decision is available to the authorization service—not merely when a processor finishes.
4. **What percentile and target apply?** For example, p95 ≤ 5 seconds.
5. **What is the measurement population and window?** For example, eligible production events over a rolling 30-day window, segmented by channel and event type.

**Weak:** “Risk monitoring must be real-time.”

**Stronger, illustrative objective:** “For eligible card-authorization events, p95 source-commit-to-risk-decision latency will be no more than 5 seconds over a rolling 30-day window, measured using correlated event identifiers and timestamps at source commit and decision availability. The service will separately report p99 latency, missing decisions, late decisions, and data-quality failures.”

This is still incomplete until the business defines eligibility, the handling of events that never produce a decision, clock/timestamp rules, and the required availability and correctness behavior. Latency should not look healthy merely because failed or missing events were excluded from the denominator.

### 6.2 Fictional scenario: Northbridge Bank

**Northbridge Bank is fictional.** All requirements, volumes, timings, and design choices in this example are illustrative assumptions.

The bank wants to detect a potentially risky card-authorization pattern quickly enough for an authorization service or analyst workflow to act before the opportunity to intervene passes. The business team initially says, “We need real-time risk monitoring.”

The architecture team asks:

- Which event begins the timer: transaction creation, source commit, or broker publication?
- Which decision ends the timer: a computed score, a persisted decision, an alert, or a customer-facing action?
- Does every transaction require a decision, and how are missing results counted?
- What traffic rate and burst size are expected?
- Can the result be provisional and corrected later, or must the decision be authoritative?
- How late can the result arrive before it loses value?
- What should happen during dependency failure?

For the worked example, assume the chosen scope is source commit to decision visibility, and the illustrative target is p95 ≤ 5 seconds. The numbers are planning allocations, not vendor benchmarks.

### 6.3 Worked latency-budget table

The table below shows one possible allocation. Each row’s boundary must be instrumented. “p95 allocation” is a planning allowance for the stage, not a claim that the stage’s actual p95 will always remain below it.

| Stage | Measurement boundary (start → end) | Planned allocation | Illustrative assumption / risk |
|---|---|---:|---|
| 1. Source capture and publish preparation | Source commit → publish request sent to the broker/client boundary | 0.30 s | Capture mechanism and publisher are healthy; includes source-to-publisher handoff but stops before broker acknowledgement |
| 2. Broker ingress and consumer availability | Publish request sent → record available to the consumer under the chosen broker contract | 0.20 s | Includes the broker/network path and required acknowledgement/visibility behavior; exact semantics depend on the selected product |
| 3. Consume, queue, and process | Broker availability/consumer position → processed decision payload | 1.50 s | Includes consumer wait, processing, required lookups, and any intentional batching |
| 4. Persist decision | Processed payload → decision committed to serving store | 0.50 s | Store write and required acknowledgement complete |
| 5. Serve and deliver | Decision committed → decision queryable/delivered to intended consumer | 0.50 s | Includes read/notification handoff; does not include unrelated human reaction time |
| **Planned stage-allocation sum** | — | **3.00 s** | Arithmetic sum of allocations |
| **End-to-end objective** | Source commit → decision visible to the intended consumer | **p95 ≤ 5.00 s** | Illustrative business objective; must be agreed and validated |
| **Time headroom** | Target minus planned allocation sum | **2.00 s** | 5.00 s − 3.00 s = 2.00 s; absorbs ordinary variability only if testing proves it does |
| **Headroom as a share of target** | 2.00 s ÷ 5.00 s | **40%** | Arithmetic description, not a universal recommended margin |

**Calculation**

- Planned allocation sum = 0.30 + 0.20 + 1.50 + 0.50 + 0.50 = **3.00 seconds**.
- Time headroom = 5.00 − 3.00 = **2.00 seconds**.
- Headroom share of target = 2.00 ÷ 5.00 = **40%**.

The 3-second planned sum is a budgeting aid. It is not a measured end-to-end p95 and should not be represented as one.

### 6.4 Why component p95 values do not add exactly

Percentiles describe distributions, not fixed durations. The p95 observation for one stage may belong to a different event from the p95 observation for another stage. Stage delays may also be correlated: a traffic spike can increase broker wait, processor queueing, and store latency together. Their joint distribution determines end-to-end latency.

Therefore:

- Summing component p95 values is a **planning approximation**, useful for allocating attention and identifying obvious budget overruns.
- It is not a mathematical identity for end-to-end p95.
- If the component measurements cover different populations or boundaries, the sum is even less informative.
- A conservative-looking component sum can still underestimate the end-to-end tail if correlated delays, omitted handoffs, or missing stages exist.
- The only reliable way to know the end-to-end percentile is to measure the end-to-end path directly with correlated events and well-defined timestamps.

A budget should be paired with direct end-to-end measurement and stage-level telemetry. If the end-to-end SLO fails, stage telemetry helps explain why; it does not replace the SLO measurement.

### 6.5 Measurement boundaries and timestamp design

Use a correlation identifier that follows an event through the path. Record timestamps at named boundaries, such as:

- `t0`: authoritative source commit;
- `t1`: publish request sent to the broker/client boundary;
- `t2`: record becomes available to the consumer under the chosen broker contract (record producer acknowledgement separately if it is a distinct boundary);
- `t3`: processing begins;
- `t4`: processing finishes;
- `t5`: decision write commits;
- `t6`: decision becomes queryable or is delivered to the consumer.

Then calculate:

- source-to-publish-preparation delay: `t1 − t0`;
- broker-to-consumer-availability delay: `t2 − t1`;
- consumer wait and processing: `t4 − t2` (or split into wait and execution if separate timestamps exist);
- persistence delay: `t5 − t4`;
- serving/delivery delay: `t6 − t5`;
- end-to-end latency: `t6 − t0`.

Be precise about whether a boundary means “request sent,” “request acknowledged,” “record available to a consumer,” “write committed,” or “result visible.” A producer acknowledgement and consumer visibility may be different boundaries; measure or infer the one used by the budget, and record the other separately if it matters. For a user-visible objective, a database write finishing is not sufficient if the consumer still cannot read the result.

Use a monotonic clock for elapsed durations measured within one process whenever possible. Wall-clock timestamps are needed to correlate events across systems, but wall clocks can drift. See Section 7.4.

### 6.6 Build a validation plan

The budget is a hypothesis until it is measured. Validate it in layers:

1. **Boundary validation:** prove every timestamp corresponds to the named event and uses the same event identifier.
2. **Functional validation:** confirm that the measured path produces a decision for the correct eligible events.
3. **Baseline load test:** measure end-to-end p50, p95, and p99 at expected steady traffic.
4. **Peak and burst test:** increase offered load to expected peaks and representative bursts; monitor backlog and end-to-end latency.
5. **Dependency-delay test:** introduce controlled delays in publishing, processing, storage, and serving to verify attribution.
6. **Recovery test:** test restart, retry, and dependency recovery; determine whether recovery time counts against the SLO.
7. **Clock-quality check:** compare clock synchronization health and investigate impossible negative or implausible durations.
8. **Production verification:** compare actual production measurements with the SLO and budget allocations over the agreed window.

A test report should include workload shape, event mix, payload sizes, concurrency, environment, warm-up, duration, sample count, errors, and the percentile calculation method. A low-volume test cannot establish reliable p99 behavior for a high-volume production workload.

### 6.7 Relating latency to throughput and freshness

Suppose a pipeline receives 8,000 events/s and can sustainably process 10,000 events/s under the tested event mix. That leaves 2,000 events/s of nominal processing-rate margin, but it does not prove adequate headroom under skew, larger payloads, slow dependencies, or bursts.

If arrival rate stays above service rate, backlog grows. Approximate backlog growth during a sustained overload is:

`backlog growth rate = arrival rate − completion rate`

For example, if 12,000 events/s arrive and only 10,000 events/s complete, backlog grows by about 2,000 events/s while those rates persist. A larger backlog usually increases the wait before processing and therefore harms latency and freshness.

Latency, throughput, and freshness are related but not interchangeable:

- High throughput does not guarantee low latency.
- Low latency at low load does not prove sufficient peak throughput.
- A dashboard refresh schedule does not guarantee fresh source data.
- A pipeline can process quickly but produce an incorrect result if events are missing, duplicated, late, or ordered incorrectly.

### 6.8 Intentional batching can consume the budget

A micro-batch system that waits up to 2 seconds to form a batch adds a delay before processing begins. Depending on the batch policy and arrival pattern, the delay may range from near zero to nearly the configured interval; the average is not necessarily half the interval under every workload.

If a 5-second end-to-end target has only 3 seconds of planned allocation, a 2-second flush interval can consume most of the remaining margin. Always include scheduling intervals, polling intervals, debounce windows, and retry delays explicitly.

## 7. Advanced design decisions and trade-offs

### 7.1 Choose the simplest processing model that meets the objective

The architecture decision should start from business tolerance for delay, required correctness, input shape, and operational constraints—not from a preference for streaming technology.

| Model | How it works | Strengths | Costs and limitations | Often suitable when |
|---|---|---|---|---|
| Scheduled batch | Process a bounded set on a schedule | Simple operations, efficient bulk processing, straightforward reconciliation | Data is stale between runs; schedule and job duration add delay | Daily finance reports, overnight reconciliation, historical training datasets |
| Frequent incremental batch | Periodically process only new or changed records | Simpler than a continuously running processor; can meet minute-level needs | Delay includes interval plus execution and scheduling; overlapping runs need care | A dashboard can tolerate several minutes of lag |
| Polling | Query a source periodically for changes | Easy to understand; useful when change notifications are unavailable | Poll interval creates delay; repeated reads add load; can miss changes if cursor logic is wrong | Small systems with low change rates and moderate freshness needs |
| Micro-batch | Process small bounded groups at short intervals | High throughput; can reuse batch transformations; simpler state model in some designs | Batch interval creates a latency floor; processing time can vary by batch size | Seconds-level objective where small periodic delay is acceptable |
| Continuous stream processing | Process events continuously or in very small units | Low potential latency; event-triggered decisions; continuous state updates | More operational complexity; ordering, state, duplicates, late events, and recovery require design | Actions lose value quickly, such as transaction-risk checks or immediate outage detection |
| Synchronous request/response | Caller requests a decision and waits for the response | Direct response path; no asynchronous result wait for the caller | Couples availability and latency to dependencies; not suitable for every fan-out or long-running task | A caller needs an immediate answer before continuing |

“Continuous” does not automatically mean faster in production. Network hops, queueing, external lookups, and overloaded dependencies can dominate. Likewise, a well-designed incremental batch pipeline may meet a seconds-to-minutes requirement at lower operational cost.

### 7.2 Tail latency and capacity headroom

Queueing delay often increases nonlinearly as utilization approaches the maximum sustainable capacity. At low utilization, bursts may be absorbed quickly; near saturation, a small increase in offered load can produce long queues and a large tail.

Do not adopt a universal utilization threshold without evidence. An illustrative starting hypothesis might be to test at 60–70% average utilization under expected traffic, then validate burst tolerance, skew, and recovery. This is not a mandatory target; some workloads need more headroom and others can safely run at higher utilization.

Capacity planning should cover:

- sustained arrival rate and peak rate;
- burst duration and burst size;
- event-size distribution;
- processing cost distribution, not just average cost;
- hot keys or uneven partitioning (covered in Topic 2);
- slow or unavailable dependencies;
- retry amplification;
- recovery and backlog-drain time.

For backlog recovery, estimate whether the system has capacity above the live arrival rate. If arrivals continue at 8,000 events/s and recovery capacity is 10,000 events/s, only about 2,000 events/s of capacity is available to drain backlog, assuming those rates hold. A backlog of 600,000 events would take roughly 300 seconds (5 minutes) to drain under those simplified assumptions: 600,000 ÷ 2,000 = 300 seconds. Actual recovery can differ because processing costs and arrivals vary.

### 7.3 Latency versus correctness

Some streaming calculations need to wait for late or out-of-order events before a result is complete. Waiting improves completeness but delays the result. Emitting early improves timeliness but may require corrections when late events arrive.

The business must choose explicitly among options such as:

- **Early provisional result:** return quickly, mark it provisional, and support later correction.
- **Wait for a defined completeness threshold:** delay the result until an event-time or business rule says enough data has arrived.
- **Strict synchronous validation:** block the business action until required checks finish; define timeout and fail-open/fail-closed behavior.
- **Approximate result:** use a documented approximation only if the decision can tolerate it.

Do not trade correctness away silently to meet a latency target. For financial, risk, safety, or compliance decisions, the consequences of a wrong or missing result may exceed the cost of delay. Event time, watermarks, state, delivery semantics, and late-event handling are developed in Topics 3, 4, and 7.

### 7.4 Clock skew and timestamp correctness

**Clock skew** is the difference between clocks on different systems. If a source clock is 800 ms ahead of the processor clock, subtracting their wall-clock timestamps may yield a negative or misleading duration. Clock drift can also change over time.

Good practice:

- Define the authoritative timestamp for the business event.
- Use synchronized wall clocks across hosts and monitor synchronization health.
- Use monotonic clocks for local elapsed-time measurement, since wall clocks can jump due to adjustment.
- Do not assume clocks are perfectly synchronized; document expected error bounds.
- Avoid calculating a precise cross-host duration when clock uncertainty is comparable to the duration being measured.
- Use tracing or event correlation to connect stage measurements, but verify how timestamps are generated.
- Record both event time and processing/observation time when the distinction matters.

For a source-to-consumer metric, cross-system timestamps are often necessary. If source-to-consumer wall-clock subtraction is used, document the clock-synchronization assumptions and treat small differences within the clock-error bound cautiously. In high-precision systems, use a measurement design that avoids relying on unsynchronized wall clocks for short durations.

### 7.5 Availability and recovery consume the latency objective

A fast healthy path does not guarantee timely results during failure. Decide whether the objective covers all eligible events, including events processed during restarts and dependency recovery, or only successful events under a narrower condition. Excluding failures can make the SLI misleading.

Clarify:

- whether the timer continues during retry and recovery;
- what counts as a missing or failed decision;
- whether late decisions are failures even if eventually delivered;
- whether a fallback path exists and what correctness it provides;
- how duplicate, replayed, or corrected outputs affect the business action.

Availability and latency should be measured separately but interpreted together. A system can be “available” in the sense that an endpoint responds while producing stale or incomplete decisions.

### 7.6 Cost and operational complexity

Lower latency may require more continuously running capacity, more frequent writes, smaller batches, low-latency serving, redundant dependencies, and more monitoring. These choices increase operating cost and operational burden.

Compare options using total cost and risk, not just infrastructure price:

- compute and storage;
- network and cross-zone traffic;
- broker retention and replication;
- on-call burden and incident complexity;
- reconciliation and replay capability;
- consequences of missed or incorrect decisions;
- cost of delayed business action.

A system that runs 24×7 needs ownership, alerting, deployment discipline, recovery procedures, and capacity planning. If the business only needs a daily answer, streaming may add cost and failure modes without meaningful benefit.

### 7.7 SLI/SLO design for a data path

A useful latency SLI is not simply “processor execution time.” It should reflect the consumer-visible outcome.

Illustrative SLI:

`eligible events delivered within 5 seconds ÷ all eligible events observed in the source population`

This formula is only meaningful if the team can identify the full eligible population. If the numerator counts only events that reached the broker, source capture failures disappear from the denominator and the metric overstates performance.

Define:

- **Population:** which events or requests qualify?
- **Start:** where is the timer started?
- **Stop:** what observable event proves the outcome is usable?
- **Threshold:** what is “within target”?
- **Window:** over what rolling or fixed period is the SLO evaluated?
- **Missing events:** how are events that never produce an output counted?
- **Duplicates and corrections:** do they count as extra outputs, and how is correctness assessed?
- **Segments:** are p95/p99 tracked by event type, channel, region, tenant, or priority?
- **Clock uncertainty:** what timestamp quality is required?
- **Error budget:** what fraction of eligible events may miss the SLO before corrective action is required?

A complementary freshness SLI may track the age of the newest source update visible to the consumer. Do not substitute it for event-to-result latency; use both when both matter.

### 7.8 Architecture decision record (ADR)

An ADR records the decision, context, alternatives, consequences, and evidence. A compact example:

**Title:** Processing model for Northbridge risk-monitoring decisions  
**Status:** Proposed (illustrative)  
**Context:** The risk workflow needs a decision before a time-sensitive authorization action. The assumed objective is p95 source-commit-to-decision visibility ≤ 5 seconds. Correctness and missing-decision behavior require explicit business approval.  
**Options considered:** (A) continuous stream processing; (B) 5-second micro-batch; (C) frequent incremental batch; (D) polling; (E) scheduled batch.  
**Decision:** Investigate continuous processing as the leading candidate, while benchmarking a short micro-batch design against the same end-to-end SLO. Do not finalize the decision until load, correctness, recovery, and cost tests are complete.  
**Reasons:** A time-sensitive decision may lose value during a multi-minute delay, but a streaming design carries greater operational complexity.  
**Consequences and risks:** More continuous operations and state/recovery concerns; late events and duplicates must not silently corrupt risk decisions.  
**Validation:** Measure end-to-end p50/p95/p99, missing decisions, freshness, peak throughput, recovery behavior, and cost under a representative event mix.  
**Revisit if:** Business tolerance changes, event rate changes materially, correctness requirements change, or the simpler model meets the same SLO at lower cost.

The decision above is a worked example, not a prescribed architecture for every risk system.

## 8. Industry use cases and decision table

The right model depends on the cost of delay, not on the industry label. These examples are illustrative.

| Use case | Decision supported | Cost of delay | Candidate model | Why / caveat |
|---|---|---|---|---|
| Card authorization risk signal | Approve, decline, or challenge a transaction | Potentially high if the next authorization occurs first | Synchronous decision path, continuous stream, or hybrid | Define the exact stop point and fallback behavior; correctness is as important as speed |
| Operational outage detection | Page the on-call engineer when a service degrades | Seconds to a few minutes, depending on incident | Continuous stream or short-window aggregation | A windowing delay may be acceptable; alert noise and late data matter |
| Operations dashboard read by staff every minute | Decide whether to investigate current operational metrics | Usually moderate | 30–60 second refresh, micro-batch, or incremental query | Continuous streaming may be unnecessary if the user only acts once a minute |
| Daily finance reconciliation | Identify mismatches before daily close or next morning | Hours may be acceptable | Scheduled batch | Batch offers simpler completeness and reconciliation; live processing is not justified by the stated decision |
| Monthly executive revenue pack | Review completed period performance | Hours or a day, according to reporting calendar | Scheduled batch or warehouse refresh | Freshness need is low; correctness and reproducibility dominate |
| Inventory availability at checkout | Decide whether an item can be promised now | Potentially high | Synchronous read/update with event-driven projections as needed | Must handle concurrent updates and consistency; “streaming” alone does not solve correctness |
| Model feature used for an interactive prediction | Provide current context to an online model | Application-specific, often tightly bounded | Online serving with event-driven feature updates or cached reads | End-to-end prediction latency includes model inference and network calls, not only feature ingestion |
| Weekly customer segmentation | Select audiences for a campaign | Hours to days | Batch | A continuously updated stream is usually needless unless the campaign decision changes materially during the week |

### Decision rule

Choose the **simplest** model that satisfies all of the following:

1. Business decision timing.
2. Required end-to-end latency percentile.
3. Required freshness.
4. Throughput and burst capacity.
5. Correctness and completeness.
6. Availability and recovery expectations.
7. Cost and operational ownership.

If two options meet the same measurable requirements, prefer the one with lower total complexity and cost unless another documented constraint changes the decision.

## 9. Hands-on exercises

All scenarios and values in these exercises are illustrative learning inputs, not repository mandates or industry benchmarks. Complete the tasks in Markdown or a spreadsheet. Do not begin by selecting a technology.

### Exercise A — Turn “real-time dashboard” into an objective

**Inputs**

- A support operations team says: “Our dashboard must be real-time.”
- Agents usually check it once every minute.
- The data represents ticket status changes.
- A stale status can inconvenience an agent but does not trigger an automatic safety-critical action.
- No agreed latency target exists yet.

**Tasks**

1. Write three clarification questions for the business owner.
2. Propose a measurable objective with a percentile, start and stop boundary, scope, and measurement window.
3. State a freshness objective separately from event-to-dashboard latency.
4. Recommend a candidate processing model and list one assumption that could change the decision.

**Deliverable**

A short requirement statement, a separate freshness statement, and a one-paragraph model recommendation.

**Validation criteria**

- “Real-time” is replaced by measurable terms.
- Start and stop boundaries are explicit.
- Percentile, population, and window are stated.
- Freshness is not confused with refresh interval.
- The recommendation follows the cost of delay and includes a condition that would change it.

**Example answer (one reasonable option)**

“For ticket status changes, p95 source-commit-to-dashboard-visibility latency should be no more than 60 seconds over a rolling 7-day window, measured for all eligible status changes. Separately, the newest relevant source update should normally be no more than 60 seconds old at dashboard query time.” A 30–60 second refresh or incremental micro-batch may be adequate because agents inspect the dashboard roughly once a minute. If the dashboard begins driving automated dispatch or escalation decisions within seconds, reassess the target and model.

### Exercise B — Build and validate a latency budget

**Inputs**

A fictional transaction-risk pipeline has an illustrative end-to-end target of p95 ≤ 4.0 seconds.

Planning allocations:

- Source capture and publish: 0.25 s
- Broker acceptance: 0.15 s
- Consumer wait and processing: 1.20 s
- Persist decision: 0.45 s
- Serve decision to consumer: 0.35 s

**Tasks**

1. Calculate the planned stage-allocation sum.
2. Calculate time headroom and headroom as a percentage of the target.
3. Add a measurement boundary to each stage.
4. Name three reasons why the arithmetic sum does not prove the end-to-end p95.
5. Propose a load-test validation plan.

**Deliverable**

A budget table and a validation checklist.

**Validation criteria**

- Sum is calculated in seconds with correct arithmetic.
- Headroom is target minus planned sum.
- All stages have start and end boundaries.
- Percentiles are described as distributions, not fixed durations.
- Validation measures the end-to-end path directly and includes peak load.

**Answer key**

Planned sum = 0.25 + 0.15 + 1.20 + 0.45 + 0.35 = **2.40 s**.  
Time headroom = 4.00 − 2.40 = **1.60 s**.  
Headroom share = 1.60 ÷ 4.00 = **40%**.

The sum does not prove end-to-end p95 because stage p95s may occur on different events, delays can be correlated, and unmeasured handoffs or failures may add latency. Test with correlated event IDs and measure source-to-consumer latency directly.

### Exercise C — Choose the simplest adequate model

For each use case below, recommend scheduled batch, incremental batch, polling, micro-batch, continuous streaming, synchronous request/response, or a hybrid. State the cost of delay and one risk.

| Use case | Inputs |
|---|---|
| 1. End-of-day ledger reconciliation | Complete prior-day transactions needed before the next business morning |
| 2. Detect repeated suspicious card attempts | The result may affect the next attempt, potentially within seconds |
| 3. Warehouse dashboard refreshed for a meeting every 10 minutes | Users do not act on individual records |
| 4. Service health alert | A team wants a warning within about 30 seconds of a sustained failure signal |
| 5. Online recommendation request | The caller needs a recommendation before rendering a page |

**Tasks**

- Choose a model for each use case.
- Explain the business reason, not just the technical preference.
- Identify one assumption that would change each recommendation.
- State where end-to-end timing begins and ends.

**Validation criteria**

- At least one case explicitly recommends batch or scheduled refresh.
- The time-sensitive fraud case addresses correctness and late results.
- The recommendation request includes the serving/inference path, not only data ingestion.
- Each choice identifies an assumption that can be tested.

**Illustrative answer guide**

1. Scheduled batch, unless the business introduces an earlier intraday decision.
2. A synchronous or continuous/hybrid design may be needed; confirm whether the result must block the next attempt and how failures are handled.
3. Scheduled or incremental refresh; streaming is not justified by the meeting cadence alone.
4. Continuous or short-window micro-batch processing, depending on the measured 30-second requirement and acceptable detection semantics.
5. Synchronous request/response for the caller-visible deadline, with upstream data freshness handled separately.

More than one answer may be valid if the objective, correctness, and operational assumptions are explicit.

### Exercise D — Design the SLI/SLO and measurement contract

**Inputs**

A service reports “99% of events are processed within 2 seconds,” but its dashboard counts only events that reached the processor. The source occasionally fails to publish events. The service also retries some writes.

**Tasks**

1. Explain how the current metric can overstate service performance.
2. Define an SLI denominator that includes the full eligible source population.
3. Define the start and stop points.
4. Specify how missing outputs and late outputs are counted.
5. Add a freshness metric and explain why it is separate.
6. List timestamp and correlation fields needed for investigation.

**Deliverable**

A short measurement contract with an SLI, SLO proposal, and missing-event policy.

**Validation criteria**

- Source capture and publish failures cannot silently disappear from the denominator.
- The stop point reflects a usable result, not merely processor completion.
- Missing results are treated explicitly.
- Freshness and event-to-result latency remain separate metrics.
- Clock-skew limitations are documented.

### Exercise E — Write a short ADR

**Inputs**

The fictional business wants an alert within 5 seconds at p95. Options are continuous streaming, 5-second micro-batch, polling every 5 seconds, and 1-minute incremental batch. All values are illustrative assumptions.

**Tasks**

Write an ADR containing:

- Context and measurable objective.
- Options considered.
- Decision or decision to defer.
- Reasons and trade-offs.
- Correctness and recovery risks.
- Validation plan.
- Conditions that would trigger a revisit.

**Deliverable**

A concise ADR of roughly 300–600 words.

**Validation criteria**

- It compares at least three options.
- It explains the cost of delay.
- It does not treat a polling or batch interval as the whole end-to-end latency.
- It distinguishes a provisional recommendation from a validated production decision.
- It includes direct end-to-end measurement and representative load testing.

## 10. Common mistakes and misconceptions

| Mistake | Why it is harmful | Better practice |
|---|---|---|
| Saying “real-time” without a number | Different stakeholders infer different service levels | Specify target, percentile, scope, boundaries, and window |
| Timing only processor execution | Omits capture, queues, batching, storage, serving, and delivery | Measure the complete business-relevant path |
| Treating refresh cadence as freshness | Upstream lag may make the newest visible data old | Measure source-update age separately |
| Treating p95 as a maximum | A tail of slower requests remains | Monitor p50/p95/p99 and define miss handling |
| Adding p95s and calling the result end-to-end p95 | Percentiles do not add exactly | Use the sum as a planning approximation; measure end to end |
| Ignoring batching and polling delays | Hidden intervals consume the budget | Include timers, schedules, flushes, retries, and queueing |
| Optimizing average latency only | Slow outliers may cause business harm | Inspect tail latency and segment by workload |
| Assuming high throughput implies low latency | Queues can grow even when aggregate throughput is high | Compare offered and completed rates; measure backlog and latency |
| Ignoring missing events | A latency metric can look healthy while events disappear | Define the full eligible population and missing-output policy |
| Assuming wall clocks are exact | Clock skew can create false negative or misleading durations | Use monotonic local timing and document cross-host clock assumptions |
| Selecting streaming because it sounds modern | Adds continuous operations and failure modes without business value | Compare simpler models against the same requirements |
| Treating headroom as a guarantee | Ordinary arithmetic does not prove tail behavior under load | Validate with realistic load, bursts, dependencies, and recovery |
| Meeting latency by weakening correctness without approval | Fast incorrect decisions can be worse than late ones | Make provisional results, corrections, and fail-open/fail-closed behavior explicit |
| Measuring only a healthy baseline | Misses saturation and recovery behavior | Test peaks, bursts, slow dependencies, and restart/recovery scenarios |

## 11. Knowledge-check questions with answers or explanations

1. **Why is “real-time” not a complete requirement?**  
   It does not specify what is timed, the target, percentile, population, measurement boundaries, or the business consequence of delay.

2. **What is the difference between component latency and end-to-end latency?**  
   Component latency covers one stage. End-to-end latency covers the complete defined path from the business-relevant start to the usable outcome.

3. **If p95 is 1.2 seconds, what can you conclude?**  
   Approximately 95% of observations in the measured population and window were at or below 1.2 seconds under the specified calculation method. The remaining tail can be slower.

4. **Why can p99 be more important than average latency for alerting?**  
   A small fraction of very late alerts can miss the opportunity to act, even when most alerts are fast.

5. **A system has a 5-second target and planned stage allocations totaling 3 seconds. What is arithmetic time headroom?**  
   2 seconds. It is a planning margin, not a guarantee.

6. **Why is the sum of component p95 values not necessarily end-to-end p95?**  
   Each percentile may correspond to different observations, stage delays may be correlated, and boundaries or handoffs may be omitted. Measure the full path directly.

7. **What is the difference between throughput and latency?**  
   Throughput is completed work per unit time; latency is elapsed time for a defined operation or event path.

8. **What is the difference between freshness and event-to-result latency?**  
   Freshness measures the age of the newest relevant data visible to a consumer. Event-to-result latency follows an individual event from a start boundary to an outcome.

9. **When might micro-batch be preferable to continuous streaming?**  
   When a short periodic delay meets the business objective and the simpler operational model is worth more than the potential latency reduction.

10. **Give one case where batch is sufficient.**  
    End-of-day reconciliation or a monthly reporting pack when results are needed on a schedule and intermediate updates do not change decisions.

11. **How can an SLI be misleading if it counts only events that reached the processor?**  
    Source or publication failures are excluded, so missing events vanish from the denominator and reported latency looks better than the true end-to-end service.

12. **How can clock skew affect latency measurement?**  
    Cross-system wall-clock subtraction may be inaccurate or negative when clocks differ. Use monotonic clocks for local elapsed time and document clock synchronization assumptions for cross-host timing.

13. **Why does high utilization increase tail latency?**  
    There is less spare capacity to absorb bursts, so queueing and backlog can grow sharply as demand approaches sustainable capacity.

14. **What should happen if a result arrives after the business deadline?**  
    The service should count and expose the miss according to the agreed SLI/SLO, then follow the business-defined late-result policy—such as discard, record, alert, or correct—rather than silently treating it as on time.

15. **What belongs in an ADR for a processing-model choice?**  
    Context, measurable objective, options, decision, rationale, consequences and risks, validation plan, and conditions for revisiting the decision.

## 12. Summary / key takeaways

- Latency is elapsed time between defined boundaries; end-to-end latency must represent the business-relevant outcome.
- Component processing time is only one part of business response time.
- A meaningful latency objective states the percentile, target, population, measurement start and stop, and time window.
- p50, p95, and p99 describe a distribution; none is a universal maximum.
- Tail latency and variability often determine whether time-sensitive decisions arrive in time.
- A latency budget assigns stage allocations and makes handoffs, queues, batching, serving, and headroom visible.
- Summed component p95s are a planning approximation—not the measured end-to-end p95.
- Measure event-to-result latency and freshness separately when both matter.
- Throughput, latency, freshness, availability, correctness, and cost interact; optimizing one in isolation can damage another.
- Clock skew can corrupt cross-system timing; use a deliberate timestamp and clock strategy.
- Batch, polling, incremental batch, micro-batch, continuous streaming, and synchronous request/response are options—not maturity levels.
- Select the simplest model that meets the business objective, and document why.
- Validate under representative load, bursts, slow dependencies, and recovery conditions; do not rely only on a healthy baseline.
- Make missing events, late results, and correctness trade-offs explicit.

## 13. Mastery criteria and completion checklist

You are ready to move to Topic 2 when you can do the following without relying on a template:

- [ ] Replace a vague “real-time” request with a measurable latency objective.
- [ ] State the business decision, cost of delay, eligible population, measurement boundaries, percentile, threshold, and window.
- [ ] Explain latency, end-to-end latency, component latency, throughput, freshness, p50/p95/p99, tail latency, SLI, SLO, and headroom accurately.
- [ ] Build a stage-level budget with units, boundaries, assumptions, arithmetic sum, headroom, and validation plan.
- [ ] Explain why component p95s do not add exactly to end-to-end p95.
- [ ] Distinguish a refresh interval from actual data freshness.
- [ ] Compare at least four processing models and justify one using business needs and operational trade-offs.
- [ ] Identify how clock skew, queueing, batching, and missing events can distort results.
- [ ] Define a direct end-to-end SLI and explain how missing outputs are counted.
- [ ] Write an ADR with options, rationale, risks, validation, and revisit conditions.
- [ ] Provide at least one justified batch case and one justified streaming case.

**Completion gate:** Keep the objective statement, latency-budget table, model decision table, validation plan, and ADR together as the Topic 1 deliverable. Have a peer review the measurement boundaries and the claim that the chosen model meets the business requirement. Revise the deliverable if it relies on vague labels or component metrics instead of end-to-end evidence.

## 14. References to adjacent module files

The following paths are taken from the supplied module roadmap and project tree. The lesson file names below are repository-relative to `Stage 2D — Data Architecture/09-Streaming-and-Real-Time-Data-Architecture/`, unless a parent path (`../`) is shown.

### Within this module

- `roadmap-Streaming-and-Real-Time-Data-Architecture.md` — module source of truth and learning order.
- `02-event-brokers-topics-partitions-and-retention.md` — next lesson; broker boundaries, partitioning, retention, and parallelism.
- `03-event-time-processing-ordering-and-watermarks.md` — event time, ordering, windows, and watermarks.
- `04-stream-processing-state-and-delivery-semantics.md` — state, checkpoints, and delivery semantics.
- `05-cdc-event-backbones-and-replay.md` — database change capture and replay.
- `06-real-time-serving-stores-and-materialized-views.md` — result availability and serving boundaries.
- `07-late-events-backpressure-and-stream-failure-modes.md` — late data, backlog, failure, and recovery.
- `practice-questions.md` — module-level review after studying the topic files.
- `Projects/09-real-time-risk-monitoring-architecture.md` — final module project integrating the seven topics.

### Earlier Stage 2D modules

- `../02-Requirements-Constraints-and-Architecture-Decisions/03-data-volume-velocity-variety-and-growth-estimation.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/04-latency-throughput-freshness-and-availability-targets.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/06-architecture-trade-offs-and-decision-criteria.md`
- `../02-Requirements-Constraints-and-Architecture-Decisions/07-architecture-decision-records-adrs.md`
- `../03-Data-Architecture-Patterns-and-Reference-Architectures/03-lambda-and-kappa-architectures.md`
- `../03-Data-Architecture-Patterns-and-Reference-Architectures/06-event-driven-and-data-sharing-patterns.md`
- `../04-Conceptual-Logical-and-Physical-Data-Modeling/06-event-modeling-and-domain-driven-design.md`
- `../04-Conceptual-Logical-and-Physical-Data-Modeling/07-schema-evolution-and-backward-compatibility.md`
- `../05-Database-and-Storage-Architecture/02-relational-nosql-and-specialized-database-selection.md`
- `../05-Database-and-Storage-Architecture/05-partitioning-indexing-clustering-and-data-layout.md`
- `../05-Database-and-Storage-Architecture/06-replication-consistency-and-transaction-boundaries.md`
- `../05-Database-and-Storage-Architecture/07-retention-archival-and-data-lifecycle-storage-tiers.md`
- `../06-Data-Integration-and-Interoperability/02-change-data-capture-and-database-replication.md`
- `../06-Data-Integration-and-Interoperability/04-streaming-events-and-message-contracts.md`
- `../06-Data-Integration-and-Interoperability/05-data-contracts-schema-registry-and-compatibility.md`
- `../06-Data-Integration-and-Interoperability/07-idempotency-deduplication-and-reconciliation.md`
- `../06-Data-Integration-and-Interoperability/08-integration-pattern-selection-and-failure-handling.md`
- `../07-Enterprise-Data-Platform-and-Lakehouse-Architecture/02-ingestion-storage-processing-and-consumption-zones.md`
- `../07-Enterprise-Data-Platform-and-Lakehouse-Architecture/04-compute-storage-and-control-plane-separation.md`
- `../07-Enterprise-Data-Platform-and-Lakehouse-Architecture/08-platform-service-levels-and-product-thinking.md`
- `../08-Cloud-Hybrid-and-Multi-Cloud-Data-Architecture/05-networking-identity-and-private-connectivity.md`
- `../08-Cloud-Hybrid-and-Multi-Cloud-Data-Architecture/06-hybrid-connectivity-and-on-premises-integration.md`

These references identify the intended learning dependencies. They do not imply that this lesson has inspected or reproduced the contents of every referenced file. Product-specific semantics and actual service targets must be verified against the implementation and the business-approved requirements.
