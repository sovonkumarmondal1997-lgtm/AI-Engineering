# Reliability Objectives, Service Level Indicators (SLIs), Service Level Objectives (SLOs) and Service Level Agreements (SLAs)

> **Document status:** Learning material and design guide.  
> **Audience:** Beginner through advanced data engineers, data architects, platform engineers and SRE practitioners.  
> **Scope:** Defining, measuring, validating and operating reliability objectives for data services and pipelines.  
> **Scenario:** Northbridge Bank is a fictional organisation used only for teaching. Every Northbridge target, policy, volume, cost, dependency value and business rule in this document is an **illustrative assumption**, not a benchmark, production measurement, legal requirement or universal recommendation.

## How to use this document

Work from foundations through the intermediate design method, then the production architecture material. Complete the exercises and retain the deliverables. Do not copy example targets into a real service without confirming business impact, measurement quality, historical performance, dependencies, operational capability and cost.

The module roadmap states that the topic files and project files were empty when it was written. Therefore, the roadmap's Topic 01 outline is the documented learning specification used here; its exercises, scenarios and targets are recommendations. The project tree confirms this file belongs in `Stage 2D — Data Architecture/12-Reliability-Resilience-and-Disaster-Recovery/` as lesson 01. This document adds general engineering explanations and clearly labeled illustrative examples; it does not imply that empty source files contained those details.

## Contents

- [1. Learning outcomes](#1-learning-outcomes)
- [2. Prerequisites and knowledge dependencies](#2-prerequisites-and-knowledge-dependencies)
- [3. Beginner foundations](#3-beginner-foundations)
  - [3.1 Reliability in a data service](#31-reliability-in-a-data-service)
  - [3.2 SLI, SLO, SLA, internal target and error budget](#32-sli-slo-sla-internal-target-and-error-budget)
  - [3.3 Identify users and business outcomes](#33-identify-users-and-business-outcomes)
  - [3.4 Data-platform indicators](#34-data-platform-indicators)
- [4. Intermediate: define measurable objectives](#4-intermediate-define-measurable-objectives)
  - [4.1 The SLI specification](#41-the-sli-specification)
  - [4.2 Windows, granularity and event populations](#42-windows-granularity-and-event-populations)
  - [4.3 Worked availability and error-budget calculations](#43-worked-availability-and-error-budget-calculations)
  - [4.4 Correctness-aware pipeline objectives](#44-correctness-aware-pipeline-objectives)
  - [4.5 Representative objectives table](#45-representative-objectives-table)
- [5. Dependency feasibility and architecture](#5-dependency-feasibility-and-architecture)
- [6. Advanced production operation](#6-advanced-production-operation)
  - [6.1 Error-budget consumption and burn-rate alerts](#61-error-budget-consumption-and-burn-rate-alerts)
  - [6.2 Interacting objectives and trade-offs](#62-interacting-objectives-and-trade-offs)
  - [6.3 SLA design and contract boundaries](#63-sla-design-and-contract-boundaries)
  - [6.4 Example error-budget policy](#64-example-error-budget-policy)
  - [6.5 Architecture Decision Record](#65-architecture-decision-record)
- [7. Worked Northbridge Bank scenario](#7-worked-northbridge-bank-scenario)
- [8. Exercises and expected deliverables](#8-exercises-and-expected-deliverables)
- [9. Architectural trade-offs and industry scenarios](#9-architectural-trade-offs-and-industry-scenarios)
- [10. Common mistakes and troubleshooting](#10-common-mistakes-and-troubleshooting)
- [11. Glossary](#11-glossary)
- [12. Mastery criteria and completion gate](#12-mastery-criteria-and-completion-gate)
- [13. Cross-topic references](#13-cross-topic-references)
- [14. Source and further reading](#14-source-and-further-reading)

---

## 1. Learning outcomes

After studying and practising this lesson, you should be able to:

1. Explain reliability from the perspective of a data consumer and business outcome.
2. Distinguish an SLI, SLO, SLA, internal service target and error budget.
3. Select indicators for availability, freshness, latency, completeness, correctness and successful delivery.
4. Specify an SLI's population, numerator, denominator, boundary, window, exclusions, timestamp semantics, data source and limitations.
5. Calculate availability, allowed downtime, error-budget quantities and burn rates with correct units.
6. Explain why event-based and time-based SLIs answer different questions and why coarse-grained windows can mislead.
7. Evaluate serial dependency availability and redundancy assumptions without treating independence as a fact.
8. Set objectives from business need, observed history, dependency constraints and cost rather than copying arbitrary “nines.”
9. Define an error-budget policy, alerting approach, change-management response and exception process.
10. Design a contractually precise SLA that is distinct from internal SLOs.
11. Produce a reliability-objectives table, feasibility calculation and ADR suitable for architecture review.
12. Connect reliability objectives to failure domains, high availability, backup/restore, RPO/RTO, replay, incident response and resilience testing.

## 2. Prerequisites and knowledge dependencies

Review these concepts before setting targets. The paths are relative to the Stage 2D directory; use the actual repository names and confirm each referenced file exists before relying on it.

| Prerequisite | Why it matters | Related module material |
|---|---|---|
| Percentages, ratios, percentiles, timestamps and time windows | An objective is only meaningful if its arithmetic and time semantics are clear | `../02-Requirements-Constraints-and-Architecture-Decisions/04-latency-throughput-freshness-and-availability-targets.md` |
| Constraints, assumptions, risks and ADRs | Reliability is a decision under constraints, not a wish for maximum uptime | `../02-Requirements-Constraints-and-Architecture-Decisions/05-constraints-assumptions-dependencies-and-risks.md`; `06-architecture-trade-offs-and-decision-criteria.md`; `07-architecture-decision-records-adrs.md` |
| Replication, consistency and transaction boundaries | A replica can be reachable while its data is stale or inconsistent | `../05-Database-and-Storage-Architecture/06-replication-consistency-and-transaction-boundaries.md` |
| Idempotency, deduplication and reconciliation | Retry and replay can create duplicates or conceal missing records | `../06-Data-Integration-and-Interoperability/07-idempotency-deduplication-and-reconciliation.md` |
| Platform planes, tenancy and service levels | Shared control planes and shared resources affect end-to-end reliability | `../07-Enterprise-Data-Platform-and-Lakehouse-Architecture/04-compute-storage-and-control-plane-separation.md`; `07-multi-team-isolation-and-tenant-boundaries.md`; `08-platform-service-levels-and-product-thinking.md` |
| Regions, zones, connectivity and infrastructure as code | Redundancy is only effective if failure domains and dependencies are understood | `../08-Cloud-Hybrid-and-Multi-Cloud-Data-Architecture/01-cloud-data-architecture-principles.md` |
| Streaming lag, late events and replay | Event-time, processing-time and arrival-time differences affect freshness | `../09-Streaming-and-Real-Time-Data-Architecture/05-cdc-event-backbones-and-replay.md`; `07-late-events-backpressure-and-stream-failure-modes.md` |
| Lineage, observability and data quality | Consumer impact, recovery order and correctness checks depend on these capabilities | `../11-Metadata-Lineage-Quality-and-Master-Data/03-end-to-end-lineage-and-impact-analysis.md`; `05-data-observability-and-quality-service-levels.md` |

**Quick prerequisite check:** You should be able to calculate 0.5% of 30 days, distinguish a timestamp from a duration, explain what a denominator represents, and describe how a failed upstream source can make a downstream report unavailable even if the report server is healthy.

## 3. Beginner foundations

### 3.1 Reliability in a data service

**Reliability** is the degree to which a service consistently delivers the behaviour its users need over a defined period and under stated conditions. A data service is not reliable merely because its processes are running. It must deliver data that is usable, timely enough, sufficiently complete and correct for the intended purpose.

Examples of data services include a batch customer mart, a streaming fraud feature, a warehouse query endpoint, a published regulatory report, a feature store, a data API or a metadata/catalog service.

Reliability is a user-facing outcome. Internal metrics such as CPU, memory, queue depth and task retries help diagnose causes, but they do not by themselves prove that the consumer received the right data on time.

| Quality dimension | Consumer question | Example failure |
|---|---|---|
| Availability | Can I access the required service or dataset when I need it? | The published table cannot be queried at report time |
| Freshness | Is the data recent enough for this use? | The fraud feature is 20 minutes behind its agreed event-time watermark |
| Latency | How long does a request or event take end to end? | A query exceeds the consumer's response-time budget |
| Completeness | Are all expected records, partitions or business entities present? | One source partition is missing from the daily load |
| Correctness | Do values satisfy business definitions and reconciliation rules? | Amounts are duplicated or a join maps customers incorrectly |
| Delivery success | Did the expected output arrive at the intended destination and become consumable? | The job reports success but the table publication transaction failed |

These dimensions overlap but are not interchangeable. For example, a table can be available and fresh but wrong. A job can finish successfully while publishing zero rows because an upstream extraction returned an empty result. A report can be correct but arrive too late to support a business decision.

**Why objectives matter:** “Make it reliable” cannot be tested consistently. A measurable objective identifies what must work, for whom, how well, over what window, and how evidence will be collected. It also makes trade-offs explicit: a tighter freshness target may require more compute, stronger isolation, more operational coverage or a different design.

### 3.2 SLI, SLO, SLA, internal target and error budget

| Term | Meaning | Main question | Example (illustrative) |
|---|---|---|---|
| **SLI — Service Level Indicator** | A measured quantity or ratio describing service behaviour | What did users experience? | 98.8% of eligible business-day reports were correct and published by 07:00 |
| **SLO — Service Level Objective** | A target value for an SLI over a defined window | What level are we aiming to achieve? | At least 99.0% of eligible reports meet the agreed end-to-end success condition over a rolling 90-day window |
| **SLA — Service Level Agreement** | A formal agreement, often contractual, defining service commitments and consequences | What have the parties agreed happens if a commitment is missed? | A contract defines a monthly service measure and a service-credit remedy under specified conditions |
| **Internal service target** | A team-level design or operating target, possibly stricter than the SLO | What engineering performance do we need to support the SLO? | Publish 99.5% of scheduled loads by 06:45 to leave a 15-minute buffer before 07:00 |
| **Error budget** | The allowed unsuccessful portion implied by an SLO and its measurement model | How much unreliability can occur before the objective is breached? | A 99% event-based success SLO allows 1% unsuccessful eligible events |

An **SLI is a measurement**, not a target. An **SLO is a target**, not automatically a contract. An **SLA is an agreement**, which may include remedies, exclusions, measurement authority and dispute processes. An **internal target** can provide operational headroom before the SLO is at risk. An **error budget** is derived from the SLO; it is not permission to knowingly deliver bad data.

SLAs are often set with more tolerance than internal SLOs, but that is a design convention rather than a law. The relationship must be deliberately negotiated and documented. Never assume an SLO is legally binding or an SLA is automatically less stringent without reading the actual agreement.

A simple analogy: for a train, punctuality recorded from arrivals is the indicator; the target percentage of on-time arrivals is the objective; a published passenger compensation policy is analogous to a service agreement. For a data platform, define the consumer-visible outcome rather than relying on a vague “job uptime” number.

**Reliability, resilience, high availability and disaster recovery are related but different:** reliability describes delivered behaviour; resilience describes the ability to withstand and recover from disruption; high availability (HA) seeks to continue service through certain failures; disaster recovery (DR) restores service/data after a major disruption; business continuity keeps critical business functions operating, possibly in degraded mode. An SLO helps define the outcome against which these designs are evaluated.

### 3.3 Identify users and business outcomes

Before selecting an indicator, identify the real consumer and the consequence of failure.

For a daily customer mart, possible consumers include:

- A finance analyst building a morning report.
- A fraud service reading customer risk features.
- A regulatory reporting process with a fixed submission deadline.
- A downstream data product that expects a complete, schema-compatible table.
- A data steward responsible for correcting disputed values.

Each has different needs. A 30-minute freshness objective may be appropriate for fraud operations but meaningless for a monthly finance extract. A regulatory report may require strong completeness and reconciliation even if its refresh frequency is low.

Use this sequence:

1. **Name the consumer and decision.** Who uses the output and what do they do with it?
2. **Define the required outcome.** For example, “the risk report is queryable, reconciled and ready before 07:00 local business time.”
3. **Define failure from the consumer's perspective.** Decide whether late, missing, stale, duplicate, incorrect or inaccessible data counts as failure.
4. **Choose a measurable population.** Which scheduled runs, requests, records, partitions or minutes are eligible?
5. **Set a candidate objective.** Use business impact and historical evidence; mark it provisional until feasibility is assessed.
6. **Define ownership and response.** Who owns the indicator, who responds to breaches and who accepts risk?

A useful objective statement has this shape:

> For **[consumer/service]**, **[defined population]** must satisfy **[observable success condition]** at least **[target]** over **[window]**, measured at **[boundary]** using **[evidence source]**, with **[explicit exclusions and limitations]**.

### 3.4 Data-platform indicators

A useful SLI should represent a material user outcome, be measurable with trustworthy evidence, and support an action when it deteriorates. Do not create a large collection of unowned indicators that nobody uses.

| Indicator | Typical definition | Common measurement boundary | Important caveat |
|---|---|---|---|
| Availability | Eligible time intervals or requests in which the service is usable | Consumer-facing API, query endpoint or publication layer | A successful health probe may not prove the requested dataset is usable |
| Freshness | Age of the newest eligible data, or share of outputs meeting a freshness deadline | Consumer-visible dataset or feature | Specify event time vs ingestion time vs publication time; late source events can change the result |
| Latency | Request-to-response duration or event-to-consumable-output duration | End-to-end consumer boundary | Use percentiles for distributions; define timeouts and whether retries count |
| Completeness | Expected records/partitions/entities present under a defined contract | Reconciled output compared with an authoritative expectation | The denominator must be independently defined; “all rows returned” is not proof of completeness |
| Correctness | Share of eligible outputs/records passing defined correctness checks | Validated published data | Checks can only detect the failure modes they cover; reference truth may itself be delayed or wrong |
| Successful delivery | Eligible deliveries that arrive, are committed, discoverable and consumable | Destination/consumer boundary | A task's exit code is not enough if publication or access fails |
| Schema compatibility | Eligible publications accepted by declared consumer contracts | Contract validation boundary | Compatibility is not equivalent to semantic correctness |
| Reconciliation | Output totals or keys agree with an independent source/control total within policy | Reconciliation stage or final output | Tolerance and timing rules must be explicit |

**Recommended practice:** choose a small set of high-value SLOs for a service, then retain diagnostic metrics for troubleshooting. There is no universal rule that a service must have exactly one to three SLOs; the right number depends on distinct user outcomes and whether each objective can be measured and acted upon.

## 4. Intermediate: define measurable objectives

### 4.1 The SLI specification

An SLI definition must be precise enough that two independent engineers would calculate the same result from the same evidence.

Document at least these fields:

| Field | Questions to answer |
|---|---|
| Name and owner | What is measured, and who is accountable for its quality and response? |
| User outcome | What user need does the indicator represent? |
| Service and scope | Which pipeline, dataset, tenant, region, interface or consumer is included? |
| Unit and type | Percent, count, duration, age, ratio, Boolean event, or distribution percentile? |
| Eligible population | Which requests, scheduled runs, records, partitions or time intervals enter the denominator? |
| Success condition | What exact conditions make an observation good? Include correctness where required. |
| Numerator and denominator | What is counted and what is the total eligible population? |
| Boundary | Where is success measured: source, orchestration, publication, or consumer? Prefer the boundary that reflects user experience. |
| Window | Calendar month, rolling 30 days, rolling 90 days, or a defined event cohort? |
| Time semantics | UTC or local business time? Event time, processing time, ingestion time or publication time? |
| Exclusions | What is excluded, under what authority, and how is it evidenced? Avoid vague post-hoc exclusions. |
| Evidence source | Durable logs, audit events, probes, reconciliation output, consumer telemetry or independent measurement? |
| Missing/invalid evidence | Does missing telemetry count as failure, unknown, or trigger a separate monitoring-data incident? State the rule. |
| Reporting delay | When is the result final, and how are late-arriving evidence and corrections handled? |
| Limitations | What failures can the indicator miss? How can the measurement be manipulated or become unavailable? |
| Alert and action | What threshold triggers paging, ticketing, review or a budget policy? |

**Ratio SLI:**

`SLI = good eligible events / total eligible events`

`SLI percentage = (good eligible events / total eligible events) × 100%`

If there are no eligible events, the ratio is undefined, not automatically 100%. Define whether the window is reported as “no data,” evaluated by a separate availability probe, or handled by an agreed policy. A quiet system should not receive a perfect score merely because no requests were observed.

**Time-based SLI:**

`availability = eligible time classified as available / total eligible time`

The time interval, sampling frequency, outage aggregation and treatment of partial intervals must be specified. A one-minute probe can miss a 10-second outage; a coarse sample is not proof that every instant was available.

**Percentile SLI:**

For latency, define the population and percentile method, e.g. “the 95th percentile of successful consumer requests during each rolling 5-minute interval is below 300 ms.” A percentile is not an average. Specify whether failed/time-out requests are separately counted, because calculating latency only over successful requests can hide severe failures.

### 4.2 Windows, granularity and event populations

SLI measurement choices determine what failures are visible.

| Measurement approach | Example | Strength | Limitation |
|---|---|---|---|
| Time-based | Fraction of eligible minutes with a usable endpoint | Maps naturally to uptime/downtime | Can understate impact if an outage affects a high-value moment or a small subset of users |
| Request/event-based | Fraction of eligible requests or deliveries that succeed | Weights observed user events; works for APIs and deliveries | A low-traffic period contributes fewer events; the event population can be gamed if eligibility is unclear |
| Scheduled-run-based | Fraction of expected daily loads meeting the complete success condition | Fits batch pipelines and deadlines | Coarse granularity means one failure can be a large fraction of a short window |
| Record-based | Fraction of eligible records passing validation | Useful for data quality | A large volume of good records can hide one critical missing entity; record-level and business-level correctness differ |
| Deadline-based | Fraction of scheduled outputs ready by a deadline | Directly reflects business timing | Must specify business days, holidays, time zones, and what “ready” means |
| Composite | Fraction of scheduled outputs both timely and correct | Aligns with end-to-end outcome | Requires reliable correctness evidence and can make diagnosis less direct; retain component SLIs too |

A **rolling window** recalculates over a moving interval, such as the last 30 days. A **calendar window** resets at a boundary, such as the calendar month. Rolling windows avoid abrupt resets but can be harder to reconcile to invoices; calendar windows may create a “new budget” effect on the first day of a month. A **cohort/event window** evaluates a defined group of expected events, such as all business-day reports scheduled during a period.

Granularity matters. If one report is expected per business day, a 30-calendar-day window may contain about 20–23 eligible reports depending on holidays and weekends. A 99% run-based SLO over 20 runs permits only 0.2 failed runs mathematically; since a run is indivisible, zero failures are allowed if the objective must be met in that exact window. This does **not** mean 99% is impossible forever; it means the sample is too small/coarse to express the intended tolerance in that window. Consider a longer window, a different aggregation, or a separate time-based measure, while preserving the business outcome.

**Measurement safeguards:**

- Use a stable, explicit eligibility rule. Do not remove difficult requests after they fail.
- Do not exclude incidents after the fact unless the written policy explicitly allows that exclusion and the evidence supports it.
- Use independent or consumer-side evidence where practical. A producer reporting “success” may not know the consumer could read the output.
- Distinguish telemetry loss from service failure, but do not silently treat missing telemetry as success.
- Handle duplicate events, retries, delayed logs and corrected records consistently.
- Specify daylight-saving changes and business calendars when deadlines use local time.
- Keep both end-to-end and component metrics: component health explains causes; end-to-end indicators establish user impact.

### 4.3 Worked availability and error-budget calculations

#### Example A: allowed downtime

For a time-based availability SLO:

`allowed_unavailable_time = (1 − target_availability) × eligible_time_window`

Use a 30-day window, where each day is 24 hours:

- Total eligible time = `30 × 24 = 720 hours`.
- At 99.9% availability, allowed unavailable fraction = `1 − 0.999 = 0.001` (0.1%).
- Allowed unavailable time = `720 hours × 0.001 = 0.72 hours`.
- Convert to minutes: `0.72 × 60 = 43.2 minutes`.

At 99.5% availability:

- Allowed fraction = `1 − 0.995 = 0.005` (0.5%).
- `720 hours × 0.005 = 3.6 hours = 216 minutes`.

These are arithmetic illustrations for a 30 × 24-hour window with no excluded time. A real SLA may define a different measurement window, eligible time, maintenance treatment, or outage aggregation. The result is not a contractual promise.

| Availability target | Unavailable fraction | Allowance over 30 × 24-hour days |
|---:|---:|---:|
| 99% | 1% | 7.2 hours (432 minutes) |
| 99.5% | 0.5% | 3.6 hours (216 minutes) |
| 99.9% | 0.1% | 43.2 minutes |
| 99.95% | 0.05% | 21.6 minutes |
| 99.99% | 0.01% | 4.32 minutes |

Do not convert availability allowance into a count of failures without knowing outage durations. One 40-minute outage and forty 1-minute outages use the same 40 minutes of a time-based budget, but can have different operational and business impacts.

#### Example B: event-based error budget

Assume (illustrative) a delivery SLO of 99.5% successful eligible deliveries over a window, with 20,000 eligible deliveries.

- Error fraction = `1 − 0.995 = 0.005`.
- Allowed unsuccessful deliveries = `20,000 × 0.005 = 100`.
- If 35 deliveries are bad, budget consumed = `35 / 100 = 35%`.
- Remaining allowance = `100 − 35 = 65` deliveries, or 65% of the original budget.

The word “bad” must have an operational definition. For a report delivery, a delivery is good only if the report arrives at the intended destination, is queryable by the consumer, meets the deadline, passes required completeness checks and passes required correctness checks. A timely but incorrect delivery is unsuccessful for this composite SLI.

#### Example C: fractional allowance and discrete events

For a 99% SLO and 30 eligible daily runs, the arithmetic allowance is `30 × 0.01 = 0.3` failed runs. A run cannot normally be 0.3 failed; therefore, if compliance is computed as an exact fraction of those 30 runs, one failure yields `29/30 = 96.67%`, below 99%, while zero failures yields 100%. Avoid saying “round 0.3 down” as a universal calculation rule; instead state the discrete event model and evaluate the measured ratio. A longer cohort of 100 runs would allow one failed run exactly at 99%.

#### Example D: time window conversions

- 7 days = `7 × 24 × 60 = 10,080 minutes`.
- 30 days = `30 × 24 × 60 = 43,200 minutes`.
- 90 days = `90 × 24 = 2,160 hours`.

Use the actual eligible period if the window is not a fixed 24-hour-day interval (e.g. business hours or a calendar month). “Month” can mean 28, 29, 30 or 31 days; do not assume it always means 30 days in a contract.

### 4.4 Correctness-aware pipeline objectives

A data pipeline should not be counted as successful merely because a task returned exit code 0. A useful success predicate can be expressed as:

`good_delivery = delivered AND consumable AND timely AND complete AND correct`

This is a conceptual Boolean rule. In a real service, each term must be defined and evidenced. Some objectives may deliberately focus on only one dimension, but they must not imply broader success than they measure.

For example, a pipeline may publish at 06:55 (before a 07:00 deadline), but reconciliation discovers 4% of expected account records are missing. The delivery is **not** good for a consumer whose report requires complete account coverage. Conversely, an output may be complete and correct but arrive at 07:20; it is a correctness success but a deadline failure. Track component indicators as well as an end-to-end composite.

Correctness is rarely proven absolutely. It is operationalized through checks such as:

- Reconciliation of independent counts, balances or control totals.
- Primary-key uniqueness and referential integrity constraints.
- Schema and semantic contract checks.
- Freshness and source-watermark checks.
- Domain invariants (e.g. non-negative quantities where the domain requires them).
- Sampling or independent comparison to a trusted source.
- Consumer acceptance tests and known-answer tests.

State the coverage and blind spots of each check. If the “source of truth” is itself corrupted, a reconciliation can agree while both datasets are wrong. For high-impact outputs, use multiple independent signals and explicit data-quality incident handling.

### 4.5 Representative objectives table

The following table is a **complete illustrative proposal** for a fictional daily risk-report pipeline. It is not a recommended universal target. The target values are provisional until validated against business requirements, historical observations, dependency capabilities, data-quality controls and cost.

**Scenario assumptions:** Northbridge Bank's risk operations team needs a reconciled risk report on business days. The consumer deadline is 07:00 `Asia/Kolkata`; the source and publication systems have UTC timestamps that are converted with an explicitly configured time-zone database. The team treats an incorrect or incomplete report as a failed delivery even if it is on time.

| SLI / outcome | Measurement definition | Illustrative target and window | Evidence and boundary | Exclusions / limitations | Owner / action |
|---|---|---|---|---|---|
| End-to-end report success | Good eligible business-day reports / all expected eligible business-day reports. Good means published, queryable, by 07:00 local time, complete against the approved control totals and passing mandatory correctness checks | ≥ 99% over rolling 100 eligible report runs | Consumer-side query probe, publication audit event, schedule calendar, reconciliation result and quality-test evidence | A formally cancelled run is excluded only if cancellation is approved and recorded before the deadline; missing evidence is not silently good | Data product owner; incident if a report is late, inaccessible, incomplete or incorrect |
| Freshness | Share of required source partitions whose accepted data watermark is no older than the agreed threshold at publication | ≥ 99% of eligible runs with source watermark age ≤ 60 minutes at publication | Source event-time watermark and consumer-visible publication timestamp | Event-time lateness can be caused by source arrival; define whether source delay is included in end-to-end service responsibility | Ingestion owner; investigate lag and late-source pattern |
| Publication availability | Eligible 1-minute intervals in which the published dataset can be queried and returns the expected schema / all eligible intervals | ≥ 99.9% over rolling 30 days | Independent consumer probe against published dataset | Probe sampling can miss sub-minute failures; schema check alone does not prove correctness | Serving owner; alert on sustained probe failure |
| Delivery latency | p95 time from scheduled extraction start to consumer-usable publication for eligible runs | p95 ≤ 45 minutes over rolling 30 days, with minimum sample rules defined | Correlated run IDs and consumer publication timestamp | Report separately when there are too few samples; failed runs are also counted in end-to-end success, not discarded from reporting | Pipeline owner; review queueing, compute and source delays |
| Completeness | Eligible runs where reconciled expected keys/partitions and required control totals meet defined tolerance / all eligible runs | ≥ 99.5% over rolling 100 eligible runs | Independent source manifest, expected partition list, control totals and reconciliation output | Define tolerance per field and source; an unknown expected count cannot prove completeness | Data quality owner; block or quarantine publication if mandatory controls fail |
| Correctness | Eligible runs passing mandatory business invariants, uniqueness, referential-integrity and semantic validation / all eligible runs | ≥ 99.5% over rolling 100 eligible runs; critical invariant failures block publication regardless of aggregate score | Versioned test results, rule definitions and audit trail | Tests do not prove all possible correctness; rule changes are reviewed and versioned | Data owner/steward; block, quarantine or publish an explicitly labeled degraded dataset only under approved policy |
| Monitoring evidence coverage | Eligible runs with complete correlated evidence for outcome, timing, completeness and correctness / all eligible runs | ≥ 99.9% over rolling 100 runs | Immutable run metadata and monitoring pipeline | Evidence absence is “unknown” for reporting and triggers a monitoring incident; it is not counted as good | Platform observability owner; repair instrumentation before trusting SLO reports |

**How to review the table:** every row has a defined population, success condition, window, boundary, evidence, limitation and owner. The exact targets are intentionally illustrative. Before approval, confirm the target denominator can be reconstructed from schedule records, all required evidence is retained, the monitoring path does not share an unexamined failure mode with the pipeline, and the dependencies can plausibly support the target.

## 5. Dependency feasibility and architecture

### 5.1 Serial dependencies

For a service that requires every component in a serial chain to work, and under a simplified model where component availabilities refer to the same period and are appropriately defined, end-to-end availability is:

`A_end_to_end = A1 × A2 × ... × An`

This product assumes the component failures behave independently for the probability model and that the service is unavailable whenever any required component is unavailable. It can be a useful first-order estimate, but it is not a substitute for measuring the end-to-end SLI. Correlated failures, shared control planes, maintenance overlap, retry masking, cached responses, degraded modes and mismatched availability definitions can invalidate the assumptions.

**Illustrative calculation:** ingestion availability = 99.9% (`0.999`), transformation availability = 99.95% (`0.9995`), and publication availability = 99.9% (`0.999`). If all three are required and independence assumptions hold:

1. `0.999 × 0.9995 = 0.9985005`.
2. `0.9985005 × 0.999 = 0.9975019995`.
3. Convert to percent: `0.9975019995 × 100 = 99.75019995%`, approximately **99.7502%**.

So a naive serial composition of those components does not support a 99.9% end-to-end availability objective over the same measurement model. This calculation does not prove the real service has exactly 99.7502% availability; it demonstrates the constraint under stated assumptions.

### 5.2 Redundancy and independence

For two truly independent parallel components where either one can fully serve the same request, system availability is:

`A_parallel = 1 − (1 − A1) × (1 − A2)`

If both components each have 99% availability and fail independently, the theoretical parallel availability is `1 − (0.01 × 0.01) = 0.9999 = 99.99%`. This result only holds if either path can serve the workload, failover works, health detection and routing are available, capacity is sufficient, data is consistent enough, and there is no common failure that disables both.

Do not multiply or combine percentages without writing down the topology and failure assumptions. Two zones using the same broken deployment, identity provider, DNS path, encryption key, control plane, source, network route or operator change may share a failure domain. A standby that has never been tested may not provide the availability implied by the formula.

### 5.3 Feasibility method

1. Define the end-to-end SLI and the period precisely.
2. Draw the required dependency chain, including data sources, orchestration, storage, identity, network, metadata/catalog, quality checks and serving path.
3. Identify hard dependencies (failure blocks the outcome) and soft dependencies (service degrades but remains usable).
4. Gather measured availability and incident history for the same boundary and period where possible. Mark estimates separately from measured data.
5. Calculate a first-order serial estimate only when assumptions are defensible.
6. Identify shared failure domains and correlated failure scenarios; do not claim independence without evidence.
7. Include recovery time, backlog catch-up, data correctness validation and publication time, not just component restart time.
8. Compare the requirement to feasible performance. If infeasible, negotiate the target, reduce dependencies, add tested redundancy, isolate failure domains, introduce a safe degraded mode, or change the business workflow.
9. Validate with end-to-end measurements and resilience tests; revise the estimate after incidents and game days.

**Key distinction:** the roadmap's suggested formula `A_service ≤ A1 × A2 × ... × An` is a useful conservative feasibility framing for a required serial chain, while the product equality is the standard simplified calculation under the specific model above. In a real architecture, define exactly what availability means and measure the end-to-end result; the inequality is not a universal law for every topology or degraded service.

## 6. Advanced production operation

### 6.1 Error-budget consumption and burn-rate alerts

An error budget is the allowed bad portion of a defined SLO. The budget model must match the SLI. For a ratio SLO with target `S`, the allowed bad fraction is `1 − S`. For a time-based availability SLO, convert that fraction into eligible unavailable time. For event-based SLOs, convert it to an allowed count only after defining the eligible event population.

**Budget consumed fraction** (simple count model):

`consumed_fraction = observed_bad_events / allowed_bad_events`

This formula is appropriate only when the allowed budget is a positive, well-defined count for the same window and event population. If the allowed count is fractional or zero, report the raw good/bad ratio and define a discrete-event policy rather than divide by zero or round silently.

**Burn rate** expresses the rate of budget consumption relative to the rate implied by consuming the full budget evenly over the SLO window. For a stable event population and a target with allowed bad fraction `e = 1 − S`:

`burn_rate = observed_bad_fraction / e`

Example: with a 99.9% SLO, `e = 0.001`. If 0.5% of eligible events are bad in a recent window, burn rate is `0.005 / 0.001 = 5`. This means the budget is being consumed at five times the rate that would exhaust it evenly over the objective window, assuming comparable event rates and populations. It does not by itself predict an exact breach time if traffic is highly variable or windows/populations differ.

A common alerting pattern uses multiple windows: a short window detects acute incidents; a longer window reduces noise and confirms sustained consumption. Thresholds must be calibrated to the service's objective window, event volume, impact and response capability. Avoid treating any particular burn-rate threshold as a universal standard.

**Illustrative alert policy:**

- Page the on-call engineer if a high burn rate persists across both a short and longer window and the affected SLI is business-critical.
- Open a ticket for moderate, sustained consumption that is not immediately paging-worthy.
- Alert separately on missing/late monitoring evidence, because an unmeasurable SLO is not evidence of reliability.
- Route correctness failures that could cause material harm to a data-quality incident path even if the aggregate error budget is healthy.
- Tune alerts using incident review; do not page on every isolated transient if no action is required.

### 6.2 Interacting objectives and trade-offs

Objectives can conflict. Optimising one dimension in isolation can degrade another.

| Decision | Potential benefit | Potential cost / risk | Evidence needed |
|---|---|---|---|
| Tighter freshness deadline | More current data for decisions | More frequent compute, less batching, higher cost and more sensitivity to source delay | Arrival distributions, late-event rates, business value of freshness, cost curve |
| More redundancy | Reduced interruption for some component failures | Additional cost, operational complexity, consistency/failover risks and shared failure modes | Failure-domain map, failover tests, capacity and data-consistency checks |
| Strict correctness gate | Prevents known-bad data from reaching consumers | May delay or block publication when checks fail or evidence is unavailable | Impact of bad data vs delayed data, validation coverage, approved degraded-mode rules |
| Automatic retries | Recovers transient errors | Retry storms, duplicate writes, longer tail latency and delayed downstream work | Idempotency, backoff, retry budget, queue/backlog behaviour |
| Longer SLO window | Smooths random variation and makes rare events measurable | Can hide a recent sharp deterioration and delay policy action | Short-window burn alerts plus rolling objective reports |
| More exclusions in an SLA | Clarifies non-attributable cases | Can make the commitment less meaningful and harder to trust | Contract review, evidence requirements and clear boundaries |
| Higher availability target | Less interruption tolerance | Often higher cost and complexity; returns diminish as targets tighten | Business loss per interruption, marginal cost, architecture feasibility |

A composite objective can represent the real user outcome (for example, correct **and** complete **and** on time). But a single composite number can hide the cause of failure. Retain component SLIs and define whether any critical condition is a hard gate. For example, if any critical correctness invariant fails, the report is a failed delivery regardless of the average quality score.

### 6.3 SLA design and contract boundaries

An SLA should be reviewed with legal, procurement, security, operations and the service owner as appropriate. This lesson is not legal advice and does not prescribe contract language.

A precise SLA should define:

- Contracting parties, covered service, tenant/region and service boundary.
- The exact metric, numerator, denominator, eligible population, window and calculation method.
- Measurement source and authority, including how disagreements are resolved.
- Time zone, calendar, reporting lag and the method for handling missing or corrected evidence.
- Planned maintenance treatment and any permitted exclusions, with notice and evidence requirements.
- Incident notification, escalation and reporting obligations.
- Remedies (such as service credits where agreed), eligibility, caps, claim windows and procedures.
- Dependencies and responsibilities of each party; avoid vague blanket exclusions.
- Security, privacy, retention and audit requirements for the measurement evidence.
- Change control, versioning, termination and review mechanisms.

Do not write “99.9% uptime” without defining uptime, the service boundary and the window. Do not assume an internal SLO and an SLA are interchangeable. An SLA may measure a different boundary from the engineering SLO, so show the mapping explicitly. Never promise a target that is inconsistent with dependencies, historical evidence, recovery design or operational capability merely because the number sounds competitive.

### 6.4 Example error-budget policy

The following is a **fictional, illustrative policy** for Northbridge's risk-report pipeline. It requires approval from actual service stakeholders before use.

| Budget state | Illustrative trigger | Required response | Decision authority / evidence |
|---|---|---|---|
| Healthy | Less than 50% of the rolling-window budget consumed and no unresolved critical correctness incident | Normal change process; continue reliability work and review leading indicators | Service owner; dashboard and release records |
| Watch | 50–80% consumed, or burn rate is materially above expected pace | Review recent changes, backlog, source delay, and error classification; prioritize corrective work | Service owner and on-call; incident/ticket links |
| At risk | More than 80% consumed, repeated SLO misses, or sustained high burn | Require explicit reliability review for high-risk changes; prioritize remediation and capacity/failure-domain work | Engineering lead; documented risk assessment |
| Exhausted | 100% of the defined budget consumed for the current window, or critical bad-data condition regardless of aggregate budget | Pause non-essential high-risk changes; permit emergency fixes and changes needed to restore reliability; define exit criteria and exception path | Service owner plus incident commander/engineering lead; recorded decision and review date |
| Monitoring untrustworthy | Evidence coverage falls below its objective or the calculation cannot be reproduced | Treat SLO status as unknown; repair measurement, investigate the observability failure and avoid claiming success | Observability owner and service owner; evidence gap log |

Policy details to make explicit in a real organisation:

- Which changes are “high risk” and which are necessary remediation.
- Whether the budget is rolling, calendar-based or event-cohort-based.
- How discrete event counts and windows with no eligible events are handled.
- Who can approve exceptions, for how long, and how the rationale is recorded.
- Whether critical correctness or security incidents bypass the aggregate budget threshold.
- What evidence permits the service to return to normal change policy.
- How customer communications, contractual reporting and incident response relate to the internal policy.

An error budget is a decision aid, not a quota to spend and not permission to deliver known-wrong data. Reliability work and feature delivery remain balanced through explicit risk decisions.

### 6.5 Architecture Decision Record

#### ADR-012-01: Define an end-to-end success SLO for the daily risk report

- **Status:** Proposed (illustrative; not an approved production decision).
- **Context:** Northbridge Bank's risk operations team needs a report available by 07:00 local business time. A job-level success metric can pass even when publication is inaccessible, expected partitions are missing or reconciliation detects incorrect values.
- **Decision:** Define an end-to-end, scheduled-run SLI. A run is good only when the report is published, consumer-queryable, available by 07:00, complete against approved manifests/control totals and passes mandatory correctness checks. Proposed objective: at least 99% of eligible business-day runs over a rolling 100 eligible-run window. Track freshness, availability, latency, completeness, correctness and evidence coverage separately as supporting indicators.
- **Measurement boundary:** Consumer query and publication boundary, correlated with scheduler run ID, source watermark, reconciliation results and versioned quality checks.
- **Assumptions:** The business-day schedule is authoritative; a pre-deadline cancellation is excluded only with recorded approval; mandatory validation evidence is retained; targets remain provisional until historical data and dependency analysis are reviewed.
- **Alternatives considered:** (A) use orchestration job-success only; rejected because it does not prove consumer delivery or correctness. (B) use availability only; rejected because an accessible but wrong report is a business failure. (C) use only a composite score; rejected because it can hide the failure dimension, so component indicators are retained.
- **Consequences:** More instrumentation and a stricter publication gate are required. Some reports may be delayed or blocked by validation failures; stakeholders must agree on safe degraded-mode behaviour. The objective must be checked against source, orchestration, storage, identity, metadata, validation and serving dependencies.
- **Error-budget policy:** Use the illustrative policy in Section 6.4 only after approval; critical correctness failures trigger incident handling even when the aggregate budget is not exhausted.
- **Validation plan:** Reconstruct the SLI from retained events; test missing telemetry, duplicate events, late source arrivals, failed publication, incorrect control totals and a consumer query outage; compare the computed result with a hand-calculated sample; run a dependency-feasibility review and a resilience exercise.
- **Risks:** Source truth may be delayed or wrong; quality rules can miss unknown defects; business calendar/time-zone errors can misclassify deadlines; shared dependencies may invalidate independence assumptions.
- **Review triggers:** Material source or consumer changes, new contractual terms, repeated SLO misses, incident/postmortem actions, change in business deadline, or a resilience test exposing a gap.
- **Owners:** Data product owner, pipeline owner, data quality owner and platform observability owner (roles, not real people).

An ADR should record the decision and rationale, not just the selected target. Revisit it when evidence changes rather than treating it as permanent truth.

## 7. Worked Northbridge Bank scenario

This section integrates the method. All values are illustrative assumptions.

### Step 1 — Business outcome

Risk operations needs a correct and complete daily report queryable by 07:00 local business time. A report that is late or wrong can trigger rework and delay decisions. Therefore, the end-to-end success definition includes timeliness, accessibility, completeness and mandatory correctness checks.

### Step 2 — Choose the SLI

Let `N` be the number of eligible scheduled business-day reports in the window. Let `G` be the number that are published, queryable by 07:00, complete and correct under the approved rules.

`SLI = G / N`

A run with missing evidence is not counted as good. The reporting policy distinguishes “failed” from “unknown due to monitoring gap,” but both prevent the service owner from asserting successful compliance until resolved. The service may report the observed SLI and an evidence-coverage SLI separately.

### Step 3 — Propose an SLO

Illustrative proposal: `G / N ≥ 0.99` over 100 eligible runs. The maximum bad-event allowance implied by the ratio is one unsuccessful run in 100. If 100 runs contain one bad run, the SLI is `99/100 = 99%`; two bad runs yield `98%` and miss the target.

This proposal is not yet approved. The business must validate whether one missed/incorrect report per 100 eligible runs is tolerable, and the team must assess historical performance and dependencies. A target with too little historical evidence should be marked provisional.

### Step 4 — Validate the measurement

Reconstruct the eligible run set from the approved schedule calendar, including holidays and cancellations. Join records using a stable run ID. For each run, obtain:

- Source watermark and relevant arrival timestamps.
- Pipeline completion and publication audit events.
- Consumer-side queryability result.
- Expected partition/key manifest and reconciliation totals.
- Versioned correctness test results.
- Any approved exclusion and its timestamped authorization.

Test that a task marked successful but with failed reconciliation is classified as a bad delivery. Test that an absent consumer probe cannot silently count as good. Ensure timestamps use the agreed business timezone and deadline rule.

### Step 5 — Check feasibility

The earlier illustrative component calculation yielded approximately 99.7502% under a simplified independent serial model for components at 99.9%, 99.95% and 99.9%. This is below 99.9%, but above the proposed 99% event-based target numerically. **Do not conclude feasibility from this comparison alone:** component availability and a run-based composite SLO are different metrics. Convert them to a common measurement model where possible, examine historical end-to-end run outcomes, and account for correctness, late arrivals, recovery/catch-up and shared dependencies.

### Step 6 — Define operational response

Use burn-rate and component alerts to detect deterioration, while routing critical correctness failures through a data-quality incident process. If the budget is exhausted, pause non-essential risky changes according to the approved policy; continue emergency repairs and reliability changes. Record exceptions and review after incidents.

### Step 7 — Review and learn

After a missed objective, ask: Was the indicator representative? Was the population correct? Did the failure originate in a shared dependency? Did monitoring fail? Did retries or replay preserve idempotency? Could the system recover and republish correct data within the business deadline? Update the ADR, failure-domain map, runbook, dependency model and resilience test plan where evidence requires it.

## 8. Exercises and expected deliverables

All scenarios and targets below are illustrative. Work independently first; then compare your output with the expected result. A numerical answer without assumptions, units and a measurement definition is incomplete.

### Exercise 1 — Beginner: classify statements

Classify each as SLI, SLO, SLA, internal target or error-budget policy. Some statements may describe a policy rather than a metric.

1. “The proportion of eligible reports queryable by the consumer before 07:00.”
2. “At least 99% of eligible reports are correct and on time over 100 eligible runs.”
3. “The signed agreement defines service credits if the monthly contractual availability measure falls below its threshold.”
4. “Publish by 06:45 to provide a 15-minute buffer.”
5. “If the rolling error budget is exhausted, non-essential risky releases require an explicit reliability review.”

**Expected output:** a classification table with one-sentence rationale for each item.

**Answer key:** (1) SLI definition; (2) SLO; (3) SLA term/remedy; (4) internal target; (5) error-budget policy. The actual SLI value is the measured proportion, not merely its written definition.

### Exercise 2 — Beginner: select indicators

For a daily customer mart, propose three indicators for (a) an analyst, (b) a fraud feature consumer and (c) a data steward. For each, name the user outcome and a failure that the indicator would detect.

**Expected output:** at least nine role-to-indicator mappings, with a clear note on overlapping needs.

**Review criteria:** indicators are user-visible, measurable and distinguish freshness, completeness and correctness rather than relying only on job status.

### Exercise 3 — Intermediate: availability arithmetic

A service proposes 99.95% time-based availability over 30 days. Assume 30 × 24 eligible hours and no exclusions.

**Tasks:** calculate unavailable fraction, allowed hours and allowed minutes; state two reasons a contract might calculate a different allowance.

**Expected result:** unavailable fraction `1 − 0.9995 = 0.0005` (0.05%); allowed time `720 × 0.0005 = 0.36 hours`; minutes `0.36 × 60 = 21.6 minutes`. A contract may use a calendar month with 28–31 days, exclude defined periods, or use a different measurement boundary/window. Exclusions must be explicit, not assumed.

### Exercise 4 — Intermediate: define a reproducible SLI

A pipeline emits a success log, but consumers report missing partitions. Write an SLI specification with population, numerator, denominator, boundary, window, evidence, missing-evidence rule and limitations.

**Expected deliverable:** one fully completed SLI specification. The numerator must count only outputs that satisfy the defined consumer outcome; the denominator must come from an independent expected schedule/manifest rather than only the set of outputs that happened to arrive.

### Exercise 5 — Intermediate: discrete runs

An SLO requires 99% of eligible runs to succeed over 30 eligible runs. Determine whether one failed run meets the SLO.

**Expected result:** with one failure, 29/30 = 0.966666… = 96.67%, so it does not meet 99%. Zero failures gives 100%. The arithmetic allowance is 0.3 failed runs, but discrete events cannot be rounded into a fractional failure. Explain whether a longer window or different SLI would better represent the intended tolerance.

### Exercise 6 — Intermediate: serial dependencies

Three required components have assumed availabilities 99.9%, 99.95% and 99.9%. Compute the simplified serial product and explain at least three assumptions or limitations.

**Expected result:** `0.999 × 0.9995 × 0.999 = 0.9975019995`, approximately 99.7502%. Limitations include independence assumptions, shared failure domains, differing metric boundaries/windows, failover/degraded modes, and the fact that component availability does not measure correctness or freshness.

### Exercise 7 — Advanced: three-stage objective composition

Design an end-to-end objective for ingestion → transformation → publication. Use the illustrative component values in Exercise 6 or justify alternatives. Identify hard dependencies, propose stage targets, and explain what you would change if the composed estimate does not meet the business requirement.

**Expected deliverables:** dependency diagram; stage SLI/SLO table; calculation with units; assumptions register; end-to-end SLI; and a decision proposal (change target, isolate/replace dependency, add tested redundancy, or change service behaviour). Do not compare a run-based correctness SLO to a time-based availability product as though they were identical metrics.

### Exercise 8 — Advanced: error budget and burn rate

A 99.9% event-based SLO has an allowed bad fraction of 0.1%. A recent window has 0.5% bad eligible events.

**Expected result:** burn rate = `0.5% / 0.1% = 5`. Explain that this is five times the even-consumption rate under comparable populations; it is not automatically an exact time-to-breach prediction. Propose short- and long-window alert handling and name the on-call action.

### Exercise 9 — Advanced: ADR and policy

Draft an ADR for an SLO that matters to a real or fictional data product. Include context, alternatives, decision, measurement, assumptions, consequences, validation plan, risks, error-budget policy and review triggers.

**Expected deliverable:** a reviewable ADR with an owner and evidence plan. Targets must be labelled provisional/illustrative unless supported by actual requirements and measurements.

### Exercise 10 — Production review: measurement attack and edge cases

Review your SLI for these cases: no eligible events; missing telemetry; duplicate run events; delayed quality results; daylight-saving transition; an approved cancellation; a task that succeeds but publishes nothing; correct output published late; timely output that fails a critical correctness invariant; and a common-cause dependency failure.

**Expected deliverable:** a decision table showing how each case is classified, the evidence needed and the owner/action. No case may be silently counted as a good outcome without justification.

## 9. Architectural trade-offs and industry scenarios

| Scenario | Risk / symptom | Candidate response | Trade-off and validation evidence |
|---|---|---|---|
| Executive asks for 100% uptime | Absolute guarantee is usually not a defensible engineering objective and can imply unbounded cost | Quantify business impact, propose measurable tiered objectives and discuss residual risk | Compare marginal cost, complexity and remaining failure modes; do not promise perfection |
| SLO is met but users are unhappy | Indicator measures a proxy such as job status, not consumer outcome | Redesign the SLI around queryability, correctness, freshness or deadline success | Compare incident reports and user outcomes against indicator results |
| Tight freshness objective increases spend | Smaller batches or continuous processing increase compute and operational complexity | Segment by use case, use tiered service levels, optimize incremental processing | Measure business value of freshness and total cost, including on-call burden |
| Replicas exist but failover fails | Redundancy was not tested or shares a failure domain | Map failure domains, test failover/failback, verify capacity and data consistency | Evidence from repeatable game days, not a diagram alone |
| Pipeline is on time but data is wrong | Availability/freshness metric hides correctness failure | Add hard correctness gates and an end-to-end good-delivery SLI | Measure detection coverage and false positives/negatives; define safe quarantine behaviour |
| SLO is breached during source outage | Responsibility boundary is ambiguous | Keep an end-to-end user SLI; track source dependency SLI and define contract responsibility separately | Explicitly state attribution and any contract exclusion; do not hide user impact from internal reporting |
| Monitoring data is missing | Team cannot reliably assert objective status | Treat status as unknown, alert on evidence coverage, repair monitoring | Verify monitoring path independence and retained audit evidence |
| Monthly SLA report conflicts with rolling SLO dashboard | Windows and definitions differ | Publish metric definitions and a mapping; compute each using its own written semantics | Reconcile source events and report both windows without silently substituting one for another |

## 10. Common mistakes and troubleshooting

| Mistake | Why it fails | Correction / diagnostic question |
|---|---|---|
| Treating SLI, SLO and SLA as synonyms | Measurement, target and agreement have different roles | Can you identify the metric, target, contractual consequence and owner separately? |
| Measuring only task success | Task completion may not imply publication, accessibility or correctness | Can a consumer query the expected output and pass its quality contract? |
| Counting timely but incorrect data as good | The SLI rewards a harmful outcome | Does the success predicate include mandatory completeness and correctness checks? |
| Using a denominator based on observed outputs only | Missing outputs disappear from the population | Is the expected population independently known from schedules/manifests/contracts? |
| No measurement boundary | Different teams report different values | Where exactly is the consumer-visible outcome observed? |
| No window or vague “monthly” definition | Results cannot be reproduced | Is the period rolling or calendar-based, and what are its exact start/end rules? |
| Ignoring discrete sample sizes | Fractional event allowances cannot be realized | How many eligible events exist, and what does one failure do to the ratio? |
| Treating missing telemetry as success | Measurement failure creates false confidence | Is missing evidence “unknown,” failed, or a separate SLI? Who fixes it? |
| Blindly multiplying component availability | Independence and topology assumptions are hidden | Are all components required, measured over the same period, and free from common-cause failures? |
| Assuming redundancy guarantees reliability | Shared dependencies and untested failover can defeat redundancy | Have failure domains, capacity, consistency and failover been tested? |
| Choosing targets from another team | Business impact, traffic and dependencies differ | What historical and business evidence supports this target? |
| Alerting on every error | Noise obscures material incidents | Does the alert represent actionable user impact or meaningful budget burn? |
| Using only a composite SLO | It hides whether freshness, correctness or availability is failing | Are component SLIs retained and critical correctness failures treated as hard gates? |
| Excluding maintenance informally | Results become disputable and potentially misleading | Are exclusions agreed in advance, bounded and evidenced? |
| Assuming an SLO is a legal commitment | Internal goals and contract obligations differ | What does the actual signed agreement state? |
| Ignoring recovery and catch-up | A system may restart quickly but take hours to restore current correct data | Include restore, replay, reconciliation and consumer availability in recovery tests |

### Troubleshooting questions

1. **The dashboard says 100%, but a consumer reports failure.** Is the SLI boundary too far upstream? Is the denominator incomplete? Is the probe representative? Is correctness measured?
2. **The objective appears impossible.** Are component targets incompatible with the end-to-end target? Are windows comparable? Are dependencies measured or merely estimated? Can the architecture reduce serial dependencies or support a safe degraded mode?
3. **The budget jumps unexpectedly.** Did the event population change? Were late events backfilled? Did a rule version change? Are duplicates or retries counted consistently?
4. **The same incident is counted twice.** Is there a stable incident/run ID? Are outage intervals unioned rather than summed twice? Are event retries deduplicated according to the SLI contract?
5. **The service appears healthy during a data-quality incident.** Does availability only check reachability? Add correctness/completeness indicators and a composite good-delivery definition.
6. **SLO status is unknown.** Repair evidence capture; do not convert unknown to good. Record the monitoring incident and assess whether the underlying service can be independently validated.
7. **The SLA and SLO disagree.** Compare scope, boundary, denominator, window, exclusions, timestamp semantics and remedies. Do not silently report one as the other.

## 11. Glossary

| Term | Definition |
|---|---|
| Availability | Fraction of eligible time or requests in which a defined service outcome is available; the measurement model must be specified |
| Blast radius | Extent of systems, data products, tenants or business processes affected by a failure |
| Business continuity (BC) | Arrangements that keep critical business functions operating during disruption, potentially in a degraded mode |
| Burn rate | Observed error-budget consumption rate relative to the rate that would exhaust the budget evenly over the SLO window |
| Completeness | Degree to which expected records, partitions, entities or fields are present according to a defined expectation |
| Correctness | Conformance of data to defined business meaning, invariants and validation rules |
| Error budget | Allowed unreliability implied by a defined SLO and measurement model |
| Failure domain | Components or resources that can fail together due to a shared cause |
| Freshness | Age or recency of data at a defined measurement boundary, with time semantics specified |
| High availability (HA) | Design approach intended to keep service available through specified component failures |
| Latency | Duration between two explicitly defined events or boundaries |
| RPO (Recovery Point Objective) | Maximum tolerable data-loss interval, expressed as time between the recovery point and the disruption point under a stated definition |
| RTO (Recovery Time Objective) | Target maximum time to restore a defined service or business function after disruption |
| Resilience | Ability to withstand, adapt to, continue through or recover from disruption |
| SLI | Service Level Indicator: a measurement of service behaviour |
| SLA | Service Level Agreement: a formal service commitment with defined terms and potential consequences |
| SLO | Service Level Objective: a target for an SLI over a defined window |
| Service boundary | Point at which the service's measured outcome is evaluated |
| Serial dependency | Required component whose failure can prevent the end-to-end outcome |
| Shared/common-cause failure | Failure that affects multiple components thought to be redundant or independent |
| Window | Period or event cohort over which an SLI/SLO is evaluated |
| MTTD | Mean time to detect a failure or incident; exact start/end definitions matter |
| MTTR | Mean time to restore, repair or resolve; organisations must define which meaning and timestamps they use |
| Runbook | Operational procedure for diagnosing or responding to a known condition |
| Postmortem | Structured review of an incident, its causes, impact and follow-up actions |

## 12. Mastery criteria and completion gate

You have mastered this topic when you can demonstrate all of the following without relying on memorized definitions alone:

- [ ] Explain reliability in terms of the data consumer's outcome.
- [ ] Distinguish SLI, SLO, SLA, internal target and error budget with examples.
- [ ] Identify the actual users and business decisions served by a pipeline.
- [ ] Define availability, freshness, latency, completeness, correctness and successful delivery in measurable terms.
- [ ] Specify numerator, denominator, eligible population, boundary, window, exclusions, evidence source, missing-evidence rule and limitations.
- [ ] Calculate allowed downtime for at least 99%, 99.5%, 99.9% and 99.99% over a stated period with units.
- [ ] Explain why event-based, time-based and scheduled-run-based SLIs are not interchangeable.
- [ ] Handle discrete events and fractional error-budget allowances without silently rounding them into possible events.
- [ ] Calculate a serial dependency estimate and state independence/common-cause limitations.
- [ ] Distinguish component availability from an end-to-end correctness-aware success objective.
- [ ] Propose targets based on business requirements and evidence, marking assumptions and provisional targets.
- [ ] Explain burn rate and create an actionable alert/policy proposal.
- [ ] Describe SLA terms and contractual measurement boundaries without confusing them with internal SLOs.
- [ ] Produce a reliability-objectives table, feasibility analysis, error-budget policy and ADR.
- [ ] Connect findings to failure-domain analysis, HA, backup/restore, RPO/RTO, replay/backfill, incident response and resilience testing.
- [ ] Complete the exercises and record unresolved assumptions or knowledge gaps.

**Completion gate (aligned to the module roadmap):**

- [ ] SLI vs SLO vs SLA is explained in your own words using a data-platform example.
- [ ] Intermediate calculation and window/granularity exercise is complete with reproducible arithmetic.
- [ ] Reliability-objectives table includes the measurement method and feasibility statement for every objective.
- [ ] Dependency-feasibility calculation includes assumptions and a clear conclusion.
- [ ] Error-budget policy and ADR are drafted and reviewed by another person where possible.
- [ ] Relevant questions in the module's `practice-questions.md` have been attempted once that file is available; gaps are logged rather than hidden.
- [ ] You can use objectives to decide which failures matter before moving to Topic 02, **Failure Domains and Blast Radius**.

## 13. Cross-topic references

The next topics use the objectives defined here to choose and validate architectural mechanisms. Review these connections during exercises and architecture reviews.

| Module topic | Relationship to reliability objectives | Questions to carry forward |
|---|---|---|
| `02-failure-domains-and-blast-radius.md` | Maps shared causes and affected services; tests whether redundancy assumptions are credible | What can fail together? Which objectives are affected and how far does impact spread? |
| `03-high-availability-and-redundancy-patterns.md` | Selects active/standby, active/active, isolation and failover patterns against required service levels | Does the pattern meet the target under tested failure scenarios and capacity constraints? |
| `04-backup-restore-and-recovery-validation.md` | Distinguishes redundancy from recoverability; validates restoration of correct, consistent data | Can the service restore from corruption/deletion, not just continue through a node failure? |
| `05-rpo-rto-and-disaster-recovery-strategies.md` | Converts business tolerance into recovery-point/time objectives and DR choices | Does the recovery plan restore service and data within the business limit? |
| `06-replay-reprocessing-and-backfill-architecture.md` | Restores data currency after an outage or point-in-time recovery | Are replay and backfill idempotent, reconciled and safe for downstream consumers? |
| `07-incident-response-runbooks-and-postmortems.md` | Turns SLO breaches into operational response and learning | Who acts, how is impact communicated, and what evidence updates the SLO/ADR? |
| `08-business-continuity-and-resilience-testing.md` | Tests the architecture and business process against defined success criteria | Can the business operate during a disruption, and do tests prove the assumptions? |
| `../05-Database-and-Storage-Architecture/` | Replication, consistency, retention and storage durability affect recovery and data correctness | Are the required data and transaction boundaries preserved? |
| `../06-Data-Integration-and-Interoperability/` | Idempotency, reconciliation and failure handling protect correctness under retries | Can a retry duplicate or omit data? |
| `../08-Cloud-Hybrid-and-Multi-Cloud-Data-Architecture/` | Zones, regions, network paths and infrastructure-as-code determine failure isolation | Are redundant paths actually independent and recoverable? |
| `../09-Streaming-and-Real-Time-Data-Architecture/` | Event-time, lag, backpressure and replay shape freshness objectives | Does the freshness SLI account for late-arriving data and backlog catch-up? |
| `../10-Data-Governance-Security-Privacy-and-Compliance/` | Retention, deletion, key recovery and auditability constrain DR and evidence retention | Can evidence be retained lawfully and can required keys/access be recovered? |
| `../11-Metadata-Lineage-Quality-and-Master-Data/` | Lineage informs impact analysis; observability and quality controls make objectives measurable | Can you trace the affected downstream outputs and validate correctness? |
| `../13-Performance-Scalability-and-Cost-Architecture/` | Capacity, latency and cost constrain achievable objectives | What is the marginal cost of a tighter target, and is capacity sufficient during failover/backfill? |
| `../15-Architecture-Documentation-Reviews-and-Operating-Model/` | Ensures decisions, diagrams, ownership and review processes remain auditable | Can another engineer reproduce the rationale and measurement method? |
| `../16-Enterprise-Data-Architecture-Case-Studies-and-Capstone/` | Integrates objectives into case studies and the final architecture package | Can the complete design defend its reliability choices with evidence? |

## 14. Source and further reading

### Repository sources used

1. `Roadmap_ptree(20261020-183631).md` — establishes the Stage 2D module path, lesson filename and neighboring lesson structure. The project tree lists `12-Reliability-Resilience-and-Disaster-Recovery/` with eight numbered lesson files, a practice-question file, README and project folder.
2. `roadmap-Reliability-Resilience-and-Disaster-Recovery(1).md` — module-specific learning roadmap, especially Topic 01 in Section E.1, the prerequisite map in Section C, recommended sequence in Section D, cross-topic integration in Section F and module completion guidance. The roadmap explicitly says the lesson and project files were empty when it was written and that exercises, templates, scenarios and targets are recommendations rather than previously documented requirements.

### General engineering references

These references provide broader conceptual context; they do not replace local business requirements or contract review. URLs are provided as starting points and were not independently validated as live links during preparation of this learning file.

- Google SRE, *Service Level Objectives*: https://sre.google/sre-book/service-level-objectives/
- Google SRE, *Implementing SLOs*: https://sre.google/workbook/implementing-slos/
- Google SRE, *Alerting on SLOs*: https://sre.google/workbook/alerting-on-slos/
- Google SRE, *Eliminating Toil* and operational reliability practices: https://sre.google/sre-book/eliminating-toil/
- NIST, *Contingency Planning Guide for Federal Information Systems* (SP 800-34 Rev. 1): https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final

**Source limitation:** The repository roadmap is a learning specification, not evidence of a live production platform's performance. All Northbridge examples and targets are illustrative. No real production measurements, contractual guarantees, vendor-specific capabilities or independently verified link-status claims are made in this document.
