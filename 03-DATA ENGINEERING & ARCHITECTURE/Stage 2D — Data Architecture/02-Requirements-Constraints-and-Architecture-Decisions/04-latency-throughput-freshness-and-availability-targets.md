# 04 — Latency, Throughput, Freshness and Availability Targets

> **Scope and source note.** This lesson follows Module 4 of `roadmap-Requirements-Constraints-and-Architecture-Decisions.md` and its position in the Stage 2D tree. The roadmap specifies the concepts, learning sequence, exercises, outputs and completion gate below. It also states that the topic lesson files, `practice-questions.md`, module/project READMEs and `Projects/02-requirements-and-architecture-decision-pack.md` are empty. This document therefore teaches from the authoritative roadmap; it does not claim to reproduce content from those empty files. All Northbridge details and all numerical targets introduced for teaching are **illustrative assumptions**, not real-world requirements or industry standards.

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Define latency, throughput, freshness and availability precisely and choose the correct metric for a business need.
2. Convert vague requests such as “real-time”, “fast” and “always available” into measurable, scoped and testable targets.
3. Define the observation boundary, timestamp semantics, workload, measurement window, percentile and verification method for each target.
4. Decompose end-to-end data-pipeline timing into stages, identify what is and is not under the platform’s control, and build a defensible timing budget.
5. Distinguish batch, micro-batch and streaming behaviour, including the meaning of “within X” for each.
6. Interpret median, p95 and p99 latency; explain why averages can conceal tail behaviour.
7. Estimate throughput from peak load and a stated safety factor, connecting the target to the capacity estimates from Topic 3.
8. Define a service-level indicator (SLI) and service-level objective (SLO), and understand the introductory use of an error budget.
9. Calculate allowed downtime for time-based availability targets and reason about serial dependencies and redundant components.
10. Identify conflicts among latency, freshness, throughput, reliability, completeness, cost and operational complexity; validate whether targets are achievable.
11. Produce a workload-specific service-target specification for the Northbridge Bank scenario and defend its assumptions.

**Learning progression:** understand the metrics → measure them consistently → define targets by workload → test feasibility and dependencies → document trade-offs and acceptance criteria.

## 2. Why the topic matters in real-world Data Architecture

Operational targets are among the strongest drivers of data architecture and cost. A design that stores the correct data but exposes it too late may fail a fraud workflow. A pipeline that handles the average event rate but collapses during month-end bursts may miss a reporting deadline. A dashboard can be reachable while displaying stale data, and a pipeline can be fast while silently dropping records. These are different failure modes and require different measurements.

The architecture question is not “Should we use a real-time technology?” It is “What outcome must a named consumer observe, at what rate, within what delay, during which operating conditions, and with what acceptable failure rate?” The answer may lead to batch, micro-batch, streaming, caching, replication, a different source contract, or a revised business target. The target must be established before selecting a technology.

Targets affect:

- **Integration and ingestion:** polling intervals, source change feeds, batch schedules, event transport, buffering and back-pressure.
- **Processing:** parallelism, queueing, state management, ordering, validation and recovery behaviour.
- **Storage and serving:** indexes, partitioning, materialized views, cache policy, query concurrency and data layout.
- **Reliability:** redundancy, failure detection, retries, replay, recovery and dependency design.
- **Operations:** monitoring, alert thresholds, on-call response, incident handling and capacity headroom.
- **Cost:** tighter freshness and availability targets may require more infrastructure, redundancy, testing and operational coverage.
- **Governance:** the measurement must have a defined owner, source of truth, business scope and audit trail.

A target is useful only when it is both **measurable** and **meaningful to the consumer**. A number with no boundary or verification method is not an operational requirement. A number that upstream systems cannot meet is not a credible target until the dependency or business expectation changes.

## 3. Prerequisite concepts

The roadmap requires Modules 2–3 in this module and Stage 2D.1 Topic 4, *Architecture Principles and Quality Attributes*.

| Prerequisite | How it is used here |
|---|---|
| Functional and non-functional requirements (Topic 2) | Separate the capability being delivered from its measurable performance or reliability. |
| Volume, velocity, retention and growth estimates (Topic 3) | Establish expected and peak workload, payload size and the scale that targets must support. |
| Quality attributes | Explain performance, availability, reliability, scalability, cost and operational trade-offs. |
| Basic arithmetic, percentages and time conversions | Calculate latency, rates, availability and allowed downtime. |
| Data-pipeline lifecycle | Identify source commit, extraction, transport, processing, loading and publication boundaries. |
| Northbridge Bank scenario | Provide a common fictional setting for customer-data consolidation and delayed fraud signals. |

### Northbridge context used throughout

**Illustrative scenario from the roadmap:** Northbridge Bank is a fictional mid-sized retail and business bank. It has a core banking system, a separate cards platform, a CRM and a loan-origination system. Nightly extracts feed an enterprise warehouse; a data lake contains copies of some sources. Risk, finance, marketing and compliance report different customer counts. Fraud analysts see card transactions hours after the fact, and a regulator has requested clearer lineage and accountability within a stated period.

The roadmap’s illustrative starting assumptions include approximately 3 million retail customers, approximately 2 million card transactions per day on average, card-platform batch files every 15 minutes today, and seven-year transaction retention. These are teaching assumptions only. Do not infer unprovided latency, availability, cost or throughput facts from them. Any additional target or measurement introduced below is explicitly illustrative and must be validated with stakeholders and measurements before it could be used in a real design.

## 4. Beginner-level learning sequence

### 4.1 Define the four core metrics

| Metric | Definition | Typical unit or expression | Example question it answers | What it does **not** prove |
|---|---|---|---|---|
| **Latency** | Elapsed time between a defined start event and a defined observable result. | milliseconds, seconds, minutes | How long from a request or event until the consumer can use the result? | It does not, by itself, show that the data is current, complete or correct. |
| **Throughput** | Amount of work successfully processed per unit of time. | records/s, bytes/s, MB/s, jobs/hour | How many events or records can the pipeline sustain over a stated interval? | It does not show how long an individual record waited, nor whether the system can absorb a short burst. |
| **Freshness** | Age of data at the point a consumer observes it, measured relative to a meaningful source or business-event timestamp. | seconds, minutes, hours; often a percentile or proportion within a threshold | How old is the newest or relevant data when the consumer uses it? | It is not the same as processing latency: data may be processed quickly after arriving late. |
| **Availability** | Proportion of the defined observation period during which a service meets its availability condition. | percentage over a stated window | How often could the consumer use the service as defined? | It does not guarantee correctness, completeness, freshness or useful performance unless the SLI explicitly includes those conditions. |

#### Latency and freshness are different

Suppose a source creates a transaction at 10:00:00, but a batch file is not made available until 10:15:00. The pipeline ingests and publishes it in 2 seconds after the file arrives. Its **post-arrival processing latency** may be 2 seconds, while its **end-to-end freshness** at publication is about 15 minutes and 2 seconds. A dashboard can also return a query in 100 milliseconds while showing data that is 40 minutes old. These numbers are illustrative examples; they demonstrate why the start and end timestamps must be named.

#### Throughput and capacity are different

Throughput is observed work completed per time unit. Capacity is the maximum sustainable work rate under defined conditions, often established through load testing and constrained by latency, error rate, data correctness and resource limits. A system might briefly process 10,000 records/s but sustain only 4,000 records/s without queue growth. A burst result is not proof of sustainable capacity.

#### Availability and correctness are different

A service may return HTTP 200 and still serve stale or incomplete data. If users consider the service “available” only when a usable result is delivered, define the SLI accordingly—for example, successful responses that meet a latency threshold and return a valid result. Do not quietly redefine availability after incidents; document the contract and exclusions in advance.

### 4.2 Availability arithmetic

Availability must have a defined service boundary, eligible observation period and rule for counting a failure. For a simple time-based model:

```text
availability = uptime / (uptime + downtime)
allowed_downtime = (1 - target_availability) × eligible_period
```

Where:

- `uptime` is eligible time in which the service met the stated availability condition.
- `downtime` is eligible time in which it did not.
- `target_availability` is a fraction between 0 and 1, not a percentage number such as 99.9.
- `eligible_period` is the total time included in the SLO window after applying the documented calendar and exclusions.
- `allowed_downtime` uses the same time unit as `eligible_period`.

This is a time-based model. If the SLI is request-based, calculate the proportion of eligible requests that succeed instead; do not convert request success rates directly into downtime minutes. A request-based SLI must define eligible requests, success conditions (including any latency and validity thresholds), treatment of retries/duplicates, and the denominator. Do not assume request-based and time-based availability are identical.

#### Worked example: monthly downtime allowance

**Inputs and evidence status:** target availability 99.9% (illustrative); one 30-day month (illustrative calendar convention); continuous 24-hour service; no exclusions; use minutes.

**Formula:** `allowed_downtime = (1 - target) × period`.

**Substitution and arithmetic:**

- `target = 99.9 / 100 = 0.999`.
- `period = 30 days × 24 hours/day × 60 minutes/hour = 43,200 minutes`.
- `allowed_downtime = (1 - 0.999) × 43,200 minutes = 0.001 × 43,200 = 43.2 minutes`.

**Result:** 43.2 minutes of eligible downtime in the illustrative 30-day month.

**Architecture interpretation:** this is the total budget for all qualifying outages within the defined service boundary, not a per-incident allowance. Dependency failures, deployment errors and recovery time may all consume it if included by the SLI. The calculation does not establish that the target is feasible or affordable.

**Sensitivity:** the result changes with the observation period, target and exclusion policy. If only business hours count, calculate the actual eligible hours rather than using 30 × 24. A real SLO must define this explicitly.

#### Exercise: monthly and annual downtime

For a 30-day month, the eligible period is 43,200 minutes. For a 365-day year, it is `365 × 24 × 60 = 525,600 minutes`.

| Target | Monthly allowance, 30-day month | Annual allowance, 365-day year |
|---:|---:|---:|
| 99% | `0.01 × 43,200 = 432 min = 7.2 h` | `0.01 × 525,600 = 5,256 min = 87.6 h = 3.65 days` |
| 99.5% | `0.005 × 43,200 = 216 min = 3.6 h` | `0.005 × 525,600 = 2,628 min = 43.8 h` |
| 99.9% | `0.001 × 43,200 = 43.2 min` | `0.001 × 525,600 = 525.6 min = 8.76 h` |
| 99.99% | `0.0001 × 43,200 = 4.32 min` | `0.0001 × 525,600 = 52.56 min` |

The values are arithmetic examples, not recommended targets. A 30-day month is not the same duration as every calendar month. For a production SLO, calculate the actual window or use a clearly defined rolling window.

### 4.3 Why 100% availability is not a sensible default

A 100% target leaves no allowance for any qualifying failure in the measurement period. Real systems have dependencies, maintenance, software defects, infrastructure faults and imperfect recovery. A literal 100% promise may be impossible to verify or economically unjustifiable. The right target depends on the business impact of failure, feasible controls, recovery requirements and cost. Some safety or regulatory constraints may require very strong controls, but the architect must still define the measurement contract and feasibility evidence rather than relying on “always available.”

### 4.4 Beginner questions and practice

1. **Dashboard question:** Explain how a dashboard can have low query latency but poor freshness. Name the timestamps needed to measure each.
2. **Availability question:** Why does a service’s successful response not necessarily prove that its data is correct or complete?
3. **Availability exercise:** Recompute the monthly and annual downtime table independently. Show the target as a fraction, the eligible period, formula, unit conversion and result.
4. **Vague statement exercise:** For each phrase—“fast reports”, “real-time transactions”, “always available”—list the missing scope, metric, threshold, observation window and verification method.

**Ability to demonstrate:** define all four metrics without conflating them and calculate allowed downtime with correct units and explicit assumptions.

## 5. Intermediate-level learning sequence

### 5.1 Decompose end-to-end timing

A data pipeline has stages. The roadmap gives this conceptual equation:

```text
end_to_end_freshness = t_source_commit + t_extract + t_transport
                     + t_process + t_load + t_publish
```

Define each term as an elapsed duration (a difference between two timestamps, not a raw timestamp) in the same unit. Use a consistent event-time/source-time convention and synchronized clocks where timestamps cross systems:

- `t_source_commit`: relevant wait from the business event to durable source commit or source availability, depending on the chosen boundary.
- `t_extract`: delay to read or expose the source data.
- `t_transport`: time to move the data to the next stage.
- `t_process`: validation, transformation, enrichment and computation time.
- `t_load`: time to write or commit data into the target store.
- `t_publish`: time until the consumer-facing interface or view exposes the result.

The formula is a **stage-budget model**. In a simple sequential path with non-overlapping stages, adding durations gives total elapsed time. If stages overlap, execute in parallel, retry, queue, or include waiting intervals not represented in a term, the model must be adjusted. Use timestamps and traces to measure actual end-to-end elapsed time; do not rely only on stage estimates.

#### Worked timing-budget example

**Inputs and evidence status:** all numbers below are illustrative planning budgets for a fraud-case path, not measured Northbridge performance or a prescribed target.

| Stage | Illustrative budget |
|---|---:|
| Source event becomes available | 5 s |
| Transport | 3 s |
| Queue wait | 4 s |
| Processing and validation | 8 s |
| Target-store commit | 4 s |
| Publish to case tool | 3 s |
| **Total stage budget** | **27 s** |

**Formula:** for a sequential path, `end_to_end_budget = Σ stage_budget_i`.

**Substitution:** `5 + 3 + 4 + 8 + 4 + 3 = 27 seconds`.

**Result:** the planned stage budget totals 27 seconds. If stakeholders choose an illustrative end-to-end threshold of 30 seconds, the arithmetic leaves 3 seconds of budget margin: `30 s - 27 s = 3 s`.

**Interpretation:** the budget helps identify where delays can be spent and which stages need instrumentation. It does not prove the end-to-end p95 is 27 seconds. Percentiles of component distributions do not generally add to the same percentile of their sum; the end-to-end distribution must be measured under realistic load. Also clarify whether the 5-second source stage begins at authorisation, event creation or source commit. The boundary determines whether the source wait is included.

### 5.2 Batch, micro-batch and streaming

| Workload | What “within X” must specify | Useful measures | Typical limitation |
|---|---|---|---|
| **Batch** | Window start, window end, source cutoff, job start, completion deadline and when the output is usable. | Completion time, deadline success proportion, records processed/window, end-to-end freshness. | A job can finish quickly after waiting a long time for the next scheduled run. |
| **Micro-batch** | Batch interval, maximum processing delay, backlog behaviour and publication time. | Batch duration, queue age, p95/p99 end-to-end delay, batches meeting deadline. | Small intervals do not guarantee low end-to-end delay if processing falls behind. |
| **Streaming** | Event-time or source timestamp, ingestion timestamp, consumer-visible timestamp, event ordering and handling of late or replayed events. | Events/s, bytes/s, end-to-end latency/freshness, lag, error/drop rate. | High throughput can coexist with queue growth, late events or incomplete output. |

For a batch source that emits every 15 minutes, a target measured from source-file arrival excludes the wait for the next file. A target measured from the original business event includes that wait. Both can be valid metrics, but they answer different questions and must not be presented as equivalent.

### 5.3 Percentiles: median, p95 and p99

A percentile describes a position in the observed distribution. The p95 latency is the value at or below which approximately 95% of measured eligible observations fall; approximately 5% are slower. The p99 has approximately 1% of observations slower. Median is p50.

Consider an **illustrative** sample of 100 request latencies sorted from fastest to slowest. If the 95th observation is 1.8 seconds, the empirical p95 is about 1.8 seconds under the selected percentile method. The exact percentile algorithm, interpolation convention and minimum sample size should be documented where precision matters.

An average hides tail behaviour. For example, 99 requests at 100 ms and one request at 10 seconds produce an average of:

`(99 × 0.1 s + 1 × 10 s) / 100 = (9.9 + 10) / 100 = 0.199 s = 199 ms`.

The average is 199 ms, but one percent of requests take 10 seconds. A user whose request is in the tail experiences a very different service. This example is illustrative. Use percentiles and, where relevant, maximums, timeout rates and distributions rather than reporting only the mean.

Every percentile target needs a measurement window and scope, such as “p95 end-to-end freshness for eligible card transactions during 08:00–20:00 local time, measured per transaction over a rolling 30-day window.” The window must contain enough observations to make the percentile meaningful. Do not compare p95 values calculated with different scopes or time windows as if they were equivalent.

### 5.4 Peak versus average throughput

The roadmap gives the capacity-planning rule:

```text
required_throughput ≥ peak_rate × safety_factor
```

Where:

- `peak_rate` is the peak expected arrival or processing rate in units such as records/s or MB/s.
- `safety_factor` is a dimensionless multiplier above 1, justified by measured variability, forecast uncertainty, backlog recovery needs and capacity-test results.
- `required_throughput` is the planned processing capacity in the same unit per second.

#### Worked throughput example

**Inputs and evidence status:** illustrative source rate of 2,000 events/s during a measured-or-assumed peak; illustrative safety factor 1.5. These values are for teaching only; a real safety factor must be justified by data and operational objectives.

**Formula:** `required_throughput ≥ peak_rate × safety_factor`.

**Substitution:** `2,000 events/s × 1.5 = 3,000 events/s`.

**Result:** plan to demonstrate at least 3,000 events/s under the defined workload and service conditions.

**Interpretation:** this is a capacity target to validate through load testing, not a guarantee of latency or correctness. The load test should include payload-size distribution, concurrency, downstream writes, validation, retries and realistic dependency limits.

**Sensitivity:** if the true peak is 3,000 events/s rather than 2,000, the same factor implies `3,000 × 1.5 = 4,500 events/s`. A wrong peak estimate changes the required capacity directly. If the system receives bursts, measure peak over multiple intervals (for example one-second and one-minute windows) because a daily average cannot characterize short spikes.

### 5.5 Convert vague requests into measurable SLOs

A service-level indicator (SLI) is the measured signal; a service-level objective (SLO) is the target for that signal over a defined window. A service-level agreement (SLA), where one exists, is a formal agreement with consequences and is not synonymous with an internal SLO.

An SLO should identify:

1. **Indicator:** what is counted or timed, and what qualifies as success.
2. **Target:** threshold and required proportion or percentile.
3. **Window:** rolling or calendar period, with time zone and business calendar if relevant.
4. **Scope:** dataset, source, consumer, request type, region or workload.
5. **Boundary and method:** start/end timestamps, instrumentation, sampling and aggregation method.
6. **Operating conditions:** expected load, peak periods, business hours and dependency assumptions.
7. **Exclusions:** for example, documented planned maintenance—only if the exclusion is agreed, measurable and applied consistently.
8. **Failure behaviour:** what happens if the target is missed, including alerting, escalation and acceptance.

#### Vague-to-measurable examples

| Vague request | Questions to resolve | Illustrative measurable rewrite |
|---|---|---|
| “Fraud data must be real-time.” | Which event? Which consumer decision? Start timestamp? What delay changes the outcome? Which hours and percentile? | “For eligible card authorisations, p95 freshness from authorisation timestamp to visibility in the fraud case tool shall be ≤30 seconds during 08:00–20:00 local time, measured per transaction over a rolling 30-day window.” |
| “Reports must be fast.” | Which report, row count, concurrency, start/end boundary, business deadline? | “The risk exposure report shall complete within 60 seconds at p95 for the agreed test dataset and concurrency profile, measured from query submission to complete result availability.” |
| “The platform must always be available.” | What is the service boundary? Which hours count? Is a slow or stale response a failure? What downtime can the business tolerate? | “At least 99.9% of eligible report requests shall return a complete, valid result within 2 seconds over each rolling 30-day window.” The 2-second threshold is illustrative and must be validated; the request-level SLI counts only requests meeting both validity and response-time conditions as successes. |
| “The nightly feed must be reliable.” | What is the deadline? What counts as complete? Which source cutoff? What happens to late records? | “At least 99% of scheduled daily loads shall publish all eligible records through the agreed source cutoff by 06:30 local time on business days, verified by record-count reconciliation and publication timestamps.” |

All thresholds above are illustrative and must not be treated as industry standards or Northbridge-approved requirements.

### 5.6 Northbridge consumers: write workload-specific targets

The roadmap asks for one measurable target for each of five consumers. The following is a **worked illustrative answer**, not a statement of actual business needs. Stakeholder validation is required before adopting any target.

| Consumer | Example indicator and illustrative target | Measurement boundary and method | Why this target may fit; what must be confirmed |
|---|---|---|---|
| Fraud analyst | p95 freshness ≤30 s for eligible card events during 08:00–20:00 local time. | Authorisation timestamp to visible event in the case tool; correlate event IDs and timestamps. | A delayed signal may change a fraud decision. Confirm the source can emit events at the needed cadence; the current 15-minute batch source cannot guarantee this from event time without a source change or a different feed. |
| Risk reporting | 99% of daily exposure reports complete by 07:00 local time on business days. | Source cutoff and report-completion timestamp; report completeness reconciled to source totals. | A deadline may matter more than sub-second query latency. Confirm source batch completion and dependency chain. |
| Regulatory submission | Provisional target: 100% of scheduled submissions meet the applicable, compliance-confirmed deadline in the explicitly approved measurement period, with a separate completeness and validation gate. This is not fully testable until the deadline, eligible submission set, and period are recorded. | Submission accepted timestamp plus evidence of reconciliation and validation; compare against the versioned deadline calendar confirmed by Compliance. | The deadline and correctness requirement must come from Compliance; a latency-only SLO is insufficient. Keep the target provisional until the authority, calendar, eligible set and measurement period are recorded. |
| Marketing segmentation | p95 completion ≤4 hours after the agreed daily source cutoff. | Cutoff timestamp to availability of a validated segment dataset. | A daily batch may be sufficient; confirm campaign cadence and the cost of fresher data. |
| Executive dashboard | p95 query latency ≤2 seconds for an agreed dashboard workload and p95 data freshness ≤60 minutes during defined business hours. | Query submission to complete render; separate source event to dashboard data timestamp. | Two SLIs are required because a fast dashboard can show stale data. Confirm dataset and concurrency profile. |

Do not make all workloads share the strictest target. Classify business criticality, quantify the harm caused by delay, and use different targets when consumers have materially different needs.

**Ability to demonstrate:** a table of workload-specific targets with indicator, threshold, percentile or proportion, window, scope, measurement boundary and method.

## 6. Advanced-level learning sequence

### 6.1 Interdependence: latency, throughput, reliability and cost

These attributes interact. Tight freshness targets can require shorter source intervals, more continuous processing, more frequent commits, additional monitoring and greater on-call coverage. Higher availability may require redundancy, failure detection, failover, replication, tested recovery and additional capacity. Higher throughput can increase resource contention and tail latency if the system runs near saturation. Strict validation can protect correctness but add processing time. Lower cost may require a wider freshness window or a less stringent availability objective.

Do not treat these as isolated requirements. Record conflicts and the business priority rule. If the target cannot be met within a fixed source schedule or budget, the architect should expose the conflict and ask the accountable stakeholder to change the target, dependency or constraint—not quietly redefine the metric.

### 6.2 Compose availability across dependencies

For components required in series, all must work for the end-to-end path to work. Under the simplifying assumption that component availabilities are applicable to the same period and their failures are independent for multiplication purposes:

```text
serial:   A = A1 × A2 × … × An
```

For two components that can serve as redundant alternatives, where either one being available is sufficient and failures are independent:

```text
parallel: A = 1 − (1 − A1) × (1 − A2)
```

Where `A` and each `Ai` are availability fractions, not percentage values. These formulas are simplified models; shared infrastructure, common software defects, shared regions, correlated failures, imperfect failover and different SLI definitions can invalidate the independence assumption.

#### Worked example: three serial components

**Inputs and evidence status:** three required components each have 99.9% availability (illustrative, and assumed applicable to the same eligible window). Failures are treated as independent for this simplified calculation.

**Formula:** `A = A1 × A2 × A3`.

**Substitution:** `A = 0.999 × 0.999 × 0.999 = 0.997002999`.

**Convert to percent:** `0.997002999 × 100 = 99.7002999%`, approximately **99.70%**.

**Result:** the serial path’s modeled availability is about 99.70%, not 99.9%.

**Architecture interpretation:** a service-level target cannot be assessed by looking at the primary component alone. The source, transport, processing, storage and consumer-facing path may all constrain end-to-end availability. If the business requires 99.9% end-to-end, the architecture must improve the dependency chain, alter the service boundary or negotiate a different target.

**Limitations:** multiplying component availability assumes compatible measurement definitions and suitable independence assumptions. In real systems, validate end-to-end measurements and model common-cause failures.

#### Worked example: two redundant alternatives

**Inputs and evidence status:** two independent components each have 99.9% availability (illustrative); either one can serve requests, and failover is assumed to work perfectly.

**Formula:** `A = 1 − (1 − A1) × (1 − A2)`.

**Substitution:** `A = 1 − (1 − 0.999) × (1 − 0.999) = 1 − (0.001 × 0.001) = 0.999999`.

**Convert to percent:** `0.999999 × 100 = 99.9999%`.

**Result:** the idealized redundant pair has modeled availability of 99.9999%.

**Architecture interpretation and limitations:** this is not a production guarantee. If both components share a power supply, network, region, deployment pipeline or data corruption mode, failures are not independent. Failover delay may still violate a request-based SLI. Redundancy improves availability only if it addresses the actual failure modes and is tested.

### 6.3 Tail latency and queueing

When utilization approaches the practical capacity of a stage, arrivals can temporarily exceed service rate. Queues grow; waiting time rises; retries may add load; the p95 and p99 can deteriorate sharply even when average throughput looks acceptable. This is why a capacity plan must include headroom and why latency must be tested at realistic peak load, not only at a quiet baseline.

For a simple queue, if the long-run arrival rate exceeds the service rate, backlog grows rather than stabilizing. If the average arrival rate is close to service capacity, ordinary variation can still create large waiting times. A single-writer constraint, rate-limited API, slow partition, lock contention or expensive validation step can become the bottleneck. Do not infer a universal safe utilization percentage from this lesson; measure the actual system and workload.

Validation should include:

- p50, p95 and p99 end-to-end latency/freshness under normal and peak conditions;
- queue depth and oldest-message age;
- arrival rate and completed processing rate over consistent intervals;
- retry, timeout, rejection and dropped-event rates;
- resource saturation and downstream write limits;
- backlog recovery after a burst or outage;
- whether latency targets remain achievable during recovery, not just during steady state.

### 6.4 Bottlenecks and operational constraints

Identify the slowest or most constrained stage, but do not assume that the stage with the longest average duration is always the only problem. Queueing and tail behaviour can make a short average stage the source of p99 delays. Common constraints include:

- a source system that exposes only scheduled extracts;
- source API quotas or rate limits;
- a single writer or serial dependency;
- a downstream database that cannot sustain the required write rate;
- a batch dependency chain where each stage waits for the previous one;
- validation, enrichment or ordering requirements that increase work per event;
- network bandwidth, payload size or cross-region transfer delay;
- recovery and replay competing with new traffic.

Map each target to the dependencies and the owner who can change them. If the source emits a file every 15 minutes, a p95 freshness target of 30 seconds from the original business event is inconsistent with that source mechanism unless the target excludes the wait or the source path changes. A fast processing stage cannot remove delay that occurred before the data became available.

### 6.5 Different targets for different data products

Classify datasets by consumer need and business impact. Fraud signals, daily regulatory outputs, marketing segments and executive dashboards do not automatically need identical freshness, latency or availability. A tiered approach avoids paying for the strictest objective everywhere. For each tier, document the consumer, criticality, data correctness/completeness requirement, target, support model and consequences of missing the target.

### 6.6 Validate feasibility before committing

For every proposed target, ask:

1. Can the indicator be measured today, and are timestamps trustworthy and synchronized?
2. Is the measurement boundary aligned with the business outcome?
3. Does the source produce data frequently enough to satisfy freshness?
4. Can the pipeline meet the target at expected peak load and during backlog recovery?
5. Are the target and its percentile supported by enough observations?
6. Are downstream dependencies and failure modes included in availability?
7. Does the target conflict with completeness, validation, privacy, cost or retention requirements?
8. What does a missed target mean operationally: alert, escalation, degraded mode, re-run or business decision?
9. What evidence would change the decision, and who owns gathering it?

A target may be accepted as a provisional hypothesis if the evidence is incomplete, but it must be marked as provisional with a validation plan, owner and date. Do not represent a guess as a measured SLO.

### 6.7 Introductory error budget

An error budget expresses the allowed failure implied by an SLO over its measurement window. For a simple time-based availability objective, it is the allowed downtime calculated in Section 4.2. For a request-based SLO, the budget can be expressed as the allowed number or proportion of eligible requests that may fail the SLI.

For example, with an **illustrative** 99.9% request-success SLO over 100,000 eligible requests, the allowed failure proportion is `1 - 0.999 = 0.001`; the request budget is `100,000 × 0.001 = 100 failed requests`. This calculation applies only if all 100,000 requests are eligible and the SLI counts failures as defined. It is not equivalent to 43.2 minutes of downtime unless the service’s measurement model makes them equivalent.

The error budget is a decision aid, not a permission to fail. Teams can use remaining budget to reason about the risk of releases or operational changes. When the budget is being consumed quickly, they may prioritize reliability work, reduce risky changes or investigate incidents. The exact policy belongs to the service owner and should be proportional to the business impact.

### 6.8 Advanced exercise: inconsistent targets

Take a set of proposed targets and identify at least two that are mutually inconsistent or unachievable given a dependency chain. For each:

- state the conflicting targets and the shared dependency;
- show the evidence or arithmetic that demonstrates the conflict;
- identify which stakeholder owns the business trade-off;
- propose defensible alternatives (change boundary, source cadence, target, workload tier or dependency design);
- state the cost, risk and business consequence of each alternative;
- define the measurement or test that would validate the chosen option.

**Ability to demonstrate:** a measurable, internally consistent and feasibility-tested target set with explicit trade-offs and conditions.

## 7. Industry-application exercises

Complete the exercises in sequence. All numeric values you introduce for Northbridge must be labelled illustrative unless a measured source is available.

### 7.1 Build the Northbridge service-target specification

Create one row per consumer: fraud analyst, risk reporting, regulatory submission, marketing segmentation and executive dashboard. Include the target fields in Section 9’s template. Each row must state the indicator, threshold, percentile or success proportion, window, scope, boundary, measurement method, operating conditions, exclusions, owner, evidence status and acceptance criteria.

For each target, write a short justification based on the consumer’s decision and the harm caused by delay or outage. Do not select a technology in place of a target.

### 7.2 Build the fraud-case timing budget

Choose a clearly stated end-to-end boundary—for example, card authorisation timestamp to event visible in the fraud case tool. Break the path into source availability, transport, queue wait, processing/validation, target-store commit and publication. Assign each stage a budget whose sum is no greater than the proposed end-to-end budget. Label every value illustrative until measured.

**Validation:**

- Show the sum and remaining margin.
- State which stages are controlled by Northbridge and which depend on the card platform or another team.
- Instrument stage timestamps and a correlated event ID.
- Test end-to-end p50/p95/p99 under realistic peak load.
- Verify that stage percentile budgets are planning aids; they do not mathematically guarantee the same end-to-end percentile.

### 7.3 Explain why “real-time” became a percentile target

Write one paragraph for a business stakeholder. Explain which decision is supported, why a vague word is ambiguous, how the start and end boundaries are defined, why a percentile captures most observations without hiding the tail, and how the target will be verified. Mention the operational consequence if the target is missed. Avoid jargon that does not help the decision-maker.

### 7.4 Availability composition calculation

Draw the service dependency chain and classify each component as serial-required or redundant. Calculate the simplified availability for the serial path. If using redundancy, state the independence and failover assumptions. Compare the result with the proposed end-to-end SLO and list any shared failure domains that make the simple calculation optimistic.

### 7.5 Northbridge target register — blank template

| ID | Consumer/workload | SLI | Target/threshold | Percentile or success proportion | Window/calendar | Start and end boundary | Scope/operating conditions | Measurement method | Exclusions | Dependencies/owner | Evidence/confidence | Acceptance test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TGT-01 |  |  |  |  |  |  |  |  |  |  |  |  |
| TGT-02 |  |  |  |  |  |  |  |  |  |  |  |  |
| TGT-03 |  |  |  |  |  |  |  |  |  |  |  |  |
| TGT-04 |  |  |  |  |  |  |  |  |  |  |  |  |
| TGT-05 |  |  |  |  |  |  |  |  |  |  |  |  |

### 7.6 Timing budget — blank template

| Stage | Start event/timestamp | End event/timestamp | Budget (unit) | Evidence status | Owner/dependency | Instrumentation | Test result/p95/p99 |
|---|---|---|---:|---|---|---|---|
| Source availability |  |  |  |  |  |  |  |
| Transport |  |  |  |  |  |  |  |
| Queue/wait |  |  |  |  |  |  |  |
| Processing/validation |  |  |  |  |  |  |  |
| Target-store commit |  |  |  |  |  |  |  |
| Publish/consumer visibility |  |  |  |  |  |  |  |
| **Total** |  |  |  |  |  |  |  |

### 7.7 Answer guidance

A strong submission does not simply list numbers. It states why each metric is the correct one, shows the boundary and units, separates measured data from assumptions, identifies the source and downstream constraints, and describes a repeatable acceptance test. The target should be relaxed only with an explicit business rationale, not because a preferred technology cannot meet it.

## 8. Practical scenarios and case-based reasoning

### Scenario 1 — “99.99% availability” for a reporting service used on business days only

The business asks for 99.99% availability. Before accepting the target, ask:

1. Is the service required 24×7 or only during defined business hours? Which calendar and time zone apply?
2. Is availability time-based or request-based? Does a response count as success if it is slow, stale, incomplete or invalid?
3. Which users, reports and dependencies are inside the service boundary?
4. What are the business consequences of an outage during business hours versus overnight or weekends?
5. Are planned maintenance exclusions allowed, and how will they be recorded?
6. What recovery capability, redundancy, testing and on-call coverage would be needed, and what is their cost?
7. Would a less stringent target during low-impact periods meet the business need without harm?

**Answer guidance:** do not automatically lower the target. First establish the actual service hours and business impact. If the service is only eligible during business hours, calculate the downtime allowance using those eligible hours. If it is expected to be available 24×7, a business-day usage pattern does not automatically remove nights and weekends from the SLO. Make the calendar explicit and get the service owner’s approval.

### Scenario 2 — Core banking extract available only after a nightly batch at 02:30

If a required upstream extract is not available until 02:30, a freshness target measured from the original event cannot be met before the source data is produced and exposed. Processing it in a few seconds does not remove the upstream waiting period.

**Reasoning steps:**

1. Define whether freshness starts at the original business event, source commit, extract completion or file availability.
2. Measure the source’s actual completion-time distribution and late-run frequency.
3. Trace the dependency chain from source cutoff to downstream publication.
4. If the business needs data earlier, ask whether a change feed or different source interface exists; do not assume it does.
5. If source behaviour cannot change, negotiate a realistic freshness boundary or target and document the business impact.

**Answer guidance:** a target such as “visible within 30 seconds of source-file availability” may be feasible while “visible within 30 seconds of every transaction event” is inconsistent with a nightly-only source. The two targets are not equivalent. Any numerical deadline introduced is illustrative until validated.

### Scenario 3 — Dashboard meets average latency, but users complain

Measure the distribution, not only the average. Inspect p50, p95 and p99 query latency; slow-query segments; concurrency; payload/result size; cache hit rate; timeouts and errors; time-of-day patterns; source-data freshness; and whether the dashboard renders a complete result. Determine whether users are reporting slow queries, stale data, partial results or availability failures. These symptoms map to different SLIs.

**Answer guidance:** establish a user-visible boundary and correlate client-side timing with backend traces. A low average can coexist with a poor tail. A fast response can also be stale. Do not claim a latency fix until the measurements show the actual bottleneck and the acceptance test passes.

### Scenario 4 — Two targets conflict

Suppose the draft target set says both “fraud data visible within 30 seconds of the authorisation event at p95” and “the only available source emits batch files every 15 minutes,” with no alternate feed. These are inconsistent if the batch mechanism is the sole path and the freshness clock begins at authorisation.

**Defensible alternatives:**

- change the source dependency or obtain a lower-latency feed, if available and approved;
- redefine the boundary to measure from file availability, while clearly acknowledging that this no longer promises event-time freshness;
- change the business target to fit the source cadence and explicitly accept the fraud risk;
- use different service tiers for consumers with different needs.

Do not silently mark both requirements as satisfied. Identify the accountable business owner and document the accepted trade-off.

### Scenario 5 — Error budget and change risk

An SLO’s error budget is being consumed rapidly. Decide whether the team should continue a high-risk release, pause changes, or invest in reliability. Inspect the SLI evidence, recent incidents, remaining budget, risk of the release and business deadlines. State the policy and decision owner; do not treat the budget as a target to exhaust.

### Scenario 6 — Batch deadline versus per-record latency

A report can finish in 20 seconds after a batch starts, but the batch starts only after a 45-minute source wait. The report’s execution latency is 20 seconds; its end-to-end freshness includes the wait. Decide which metric corresponds to the business requirement and instrument both if both are operationally useful.

## 9. Expected outputs and deliverables

The roadmap requires these outputs:

1. **Metric definitions and vague-to-measurable conversion table.** Define each metric and show why the rewritten requirement is testable.
2. **Service-target specification with SLOs.** Targets must be workload-specific and include indicator, target, measurement window, scope, measurement method and exclusions.
3. **End-to-end timing budget.** Stage budgets must sum to the proposed end-to-end budget, with boundaries, units, dependencies and validation evidence.
4. **Availability composition calculation.** Show allowed downtime and model serial dependencies; state assumptions for redundancy and compare the model with end-to-end evidence.
5. **Answers to Topic 4 practice questions.** Answer the roadmap’s conceptual and scenario questions, correct mistakes and retain the reasoning.

### Minimum service-target specification fields

Use the fields that serve a purpose; do not force irrelevant fields into every workload. Mark unknowns as unknown and label evidence.

| Field | What to record |
|---|---|
| Target ID and owner | Stable identifier and accountable owner. |
| Consumer and workload | Named consumer, dataset, request or pipeline path. |
| Business outcome | Why the target matters and what delay/outage harms. |
| SLI definition | Numerator/denominator or timestamp pair; definition of success/failure. |
| Threshold and target | Value, unit, percentile or required proportion. |
| Measurement window | Rolling/calendar period, business calendar and time zone. |
| Boundary | Exact start and end events; whether source wait is included. |
| Conditions and scope | Expected and peak load, data class, hours, region and concurrency. |
| Method and instrumentation | Metrics, traces, logs, event IDs, sampling and aggregation. |
| Exclusions | Explicitly agreed exclusions and how they are measured. |
| Dependencies and assumptions | Upstream cadence, downstream limits, common failure modes. |
| Acceptance criteria | Pass/fail test, dataset, workload, test period and reviewer. |
| Evidence status/confidence | Measured, sampled, stakeholder-stated, estimated or guessed; confidence and validation plan. |
| Failure response | Alerting, escalation, degraded mode, recovery or re-evaluation. |

### Blank vague-to-measurable conversion table

| Original request | Consumer/decision | Missing information | Proposed SLI | Target and window | Boundary/method | Acceptance test | Owner/status |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |

### Worked SLO example (illustrative)

**Statement:** “For eligible card authorisations, p95 end-to-end freshness shall be no more than 30 seconds during 08:00–20:00 local time over a rolling 30-day window.”

- **Indicator:** elapsed time between the authorisation timestamp and the first time the corresponding event is visible in the fraud case tool.
- **Target:** p95 ≤30 seconds. The p95 is calculated from eligible event-level observations; event IDs link source and consumer timestamps.
- **Scope:** eligible card authorisations during the stated hours; specify treatment of duplicates, test events and replayed events before measuring.
- **Method:** timestamped event instrumentation, synchronized clocks, end-to-end trace/correlation ID and a recorded percentile calculation.
- **Acceptance test:** run a representative workload including peak conditions; compute the percentile over a sufficient sample; verify source coverage and event completeness separately.
- **Evidence status:** illustrative proposal only; target, source capability and measurement quality require stakeholder and engineering validation.

A complete SLO cannot hide a source-cadence contradiction. If the only source is a 15-minute batch, the team must resolve that dependency or revise the boundary/target before claiming feasibility.

## 10. Common mistakes and misconceptions

1. **Equating “real-time” with a technology.** A technology choice does not define the business delay that is acceptable.
2. **Reporting averages alone.** Averages can hide p95/p99 tail latency, timeouts and slow segments.
3. **Confusing latency and freshness.** Query execution can be fast while data is stale; processing can be fast after a late source arrival.
4. **Defining no measurement boundary.** If start/end timestamps are unclear, teams can report incompatible numbers.
5. **Setting availability without dependencies.** The primary service may be healthy while an upstream or downstream dependency makes the user path unavailable.
6. **Treating availability as correctness.** A successful response can contain stale, incomplete or invalid data unless the SLI includes the relevant quality condition.
7. **Using average throughput to size peaks.** Bursts and backlog recovery may exceed average load; use measured peaks and a justified safety factor.
8. **Calling throughput “capacity.”** Observed throughput is not proof of sustainable capacity under the required latency and error conditions.
9. **Adding percentile budgets as if they were guaranteed end-to-end percentiles.** Stage budgets are planning aids; measure the end-to-end distribution.
10. **Ignoring source cadence and operating windows.** A downstream pipeline cannot publish data before the source makes it available.
11. **Using arbitrary targets as standards.** Targets must be justified by business harm, observed behaviour, cost and feasibility.
12. **Leaving exclusions implicit.** Planned maintenance, weekends and test traffic must be defined before measuring, not introduced to excuse a miss.
13. **Using an SLO without an SLI.** “99.9% reliable” is not testable without a success condition and observation method.
14. **Ignoring common failure domains in redundancy.** Two nominally redundant services may fail together because of shared infrastructure or software.
15. **Applying one target to every dataset.** Different consumers and business criticality may justify different service tiers.
16. **Treating an error budget as permission to fail.** It is a decision aid for managing risk, not a substitute for reliability work.
17. **Failing to verify clock and timestamp semantics.** Time-zone mismatch, unsynchronized clocks or ambiguous event-time semantics can invalidate latency/freshness results.
18. **Writing targets without acceptance criteria.** A target must specify a reproducible test and what constitutes pass or fail.

## 11. Mastery criteria

You have mastered this topic when you can demonstrate all of the following:

- Define latency, throughput, freshness and availability accurately, and explain what each does not prove.
- Convert vague statements into workload-specific targets with indicator, threshold, percentile or proportion, window, scope, measurement boundary and method.
- Compute allowed downtime for 99%, 99.5%, 99.9% and 99.99% targets over monthly and annual windows, with correct unit conversions.
- Decompose end-to-end timing, identify controlled and external stages, and build a timing budget with consistent units.
- Explain batch versus streaming timing and why source cadence constrains event-time freshness.
- Use p50/p95/p99 appropriately and explain why average latency may misrepresent user experience.
- Estimate required throughput from peak rate and a stated safety factor; distinguish this from sustainable capacity and validate through testing.
- Define an SLI/SLO and describe introductory error-budget use without confusing it with an SLA or a guarantee of correctness.
- Compose simplified availability for serial dependencies and redundant alternatives, state assumptions and identify common-cause failure risks.
- Identify bottlenecks, queueing, source windows and target conflicts; state trade-offs and the owner who must resolve them.
- Produce the service-target specification and fraud-case timing budget for Northbridge, marking every invented value illustrative.

## 12. Completion gate

Do not mark this topic complete until every item below is satisfied.

- [ ] Every target is measurable and names its measurement method.
- [ ] Each target has a defined SLI, threshold, percentile or success proportion where appropriate, observation window, workload scope and measurement boundary.
- [ ] The timing budget stages sum correctly to the stated end-to-end budget, with units and dependencies documented.
- [ ] End-to-end behaviour is validated separately; stage percentile budgets are not presented as mathematical proof of the same end-to-end percentile.
- [ ] Allowed downtime calculations for 99%, 99.5%, 99.9% and 99.99% are independently recomputed for monthly and annual windows.
- [ ] Availability composition is checked against the dependency chain; serial/parallel assumptions and common failure domains are recorded.
- [ ] The Northbridge service-target specification includes all five consumers and labels all illustrative values.
- [ ] At least two inconsistent or unachievable targets are identified in an advanced exercise, with defensible alternatives and explicit trade-offs.
- [ ] The service-target specification, vague-to-measurable table, timing budget and availability calculation are reviewed for consistency.
- [ ] Topic 4 practice questions are answered, checked, corrected and retained with the reasoning.

**Completion evidence:** a reviewer can reproduce the arithmetic, understand exactly how each metric is measured, trace every target to a consumer need, identify the dependency assumptions, and determine whether the targets are feasible without guessing what “real-time”, “fast” or “available” means.
