# Practice Questions — Performance, Scalability and Cost Architecture

## 1. Purpose and instructions

This question bank assesses the eight-topic module **Performance, Scalability and Cost Architecture**. It is designed to test understanding, calculation, diagnosis, experiment design, and architecture judgement—not recall alone.

The module roadmap is the authority for scope and sequence. Its learning outcomes are to estimate capacity and forecast growth; interpret throughput, latency, concurrency and queueing; analyse query performance and data locality; evaluate scaling and hotspots; compare caching/materialisation/serving; build cost models and unit economics; plan performance tests and validate capacity; recommend evidence-backed optimisation; explain trade-offs; and present an integrated review.

### Difficulty labels

- **Beginner:** definitions, fundamental distinctions, direct calculations.
- **Intermediate:** multi-step calculations, interpreting evidence, selecting and applying methods.
- **Advanced:** interacting workloads, uncertainty, failure behaviour, trade-offs, and defensible decisions.

### Instructions

1. Attempt the questions before reading the answer key.
2. Show formulas, units, time periods, and assumptions for calculations.
3. Treat all prices, workloads, and measurement tables in this question bank as **illustrative synthetic data**, not actual vendor prices or production benchmarks.
4. Distinguish a measured fact from an assumption, estimate, hypothesis, recommendation, and validated outcome.
5. For architecture questions, there may be more than one defensible design. State the conditions under which your recommendation is valid and identify what evidence would change it.
6. Unless a question says otherwise, assume arithmetic is exact to the displayed precision and ignore tax, discounts, and overhead not explicitly included.
7. The answer key provides a defensible answer, not a claim that one design is universally best.

---

## 2. Assessment scope and learning-outcome mapping

| Section | Topic | Main skills assessed | Module outcome |
|---|---|---|---|
| 3 | 01 — Capacity planning and growth forecasting | Workload rates, storage, growth, headroom, N+1, sensitivity | Estimate capacity and forecast growth |
| 4 | 02 — Throughput, latency, concurrency and queueing | Little’s Law, backlog, percentiles, saturation, backpressure | Interpret performance behaviour |
| 5 | 03 — Query performance and data locality | Scan volume, selectivity, query plans, joins, movement | Analyse query performance |
| 6 | 04 — Scaling, partitioning, sharding and hotspots | Scaling options, keys, skew, rebalancing | Evaluate distribution and scaling |
| 7 | 05 — Caching, materialisation and serving | Hit ratio, freshness, invalidation, refresh economics | Compare serving approaches |
| 8 | 06 — Cost modelling, unit economics and FinOps | Cost drivers, unit cost, allocation, scenarios, variance | Build and evaluate cost models |
| 9 | 07 — Performance testing and capacity validation | Test design, criteria, repeatability, capacity evidence | Validate capacity assumptions |
| 10 | 08 — Architecture optimisation with measured evidence | Hypotheses, controlled comparisons, Amdahl, trade-offs | Recommend evidence-backed optimisation |
| 11–12 | Cross-topic integration and final project | End-to-end coherent review and evidence traceability | Present an evidence-backed review |

### Prerequisite reminders from the roadmap

- **P1:** estimating volume, rate, growth, retention, units and ranges.
- **P2:** measurable latency, throughput, freshness and availability targets.
- **P3:** trade-offs, criteria, sensitivity analysis and architecture decision records.
- **P4/P5:** partitioning, indexing, clustering, skew, data layout, table formats and compute/storage separation.
- **P6:** cloud cost drivers including compute, storage, requests and transfer.
- **P7/P8/P9:** streaming backlog and lag, redundancy/recovery capacity, and serving stores/materialised views.
- **P10:** basic arithmetic, ratios, percentages, compound growth and simple probability.

The roadmap recommends the numeric order 01→08 because each topic supplies inputs to later decisions. Its feedback loops matter: performance measurements can revise capacity assumptions; measured costs can revise the cost model; and an optimisation can reveal a new bottleneck.

---

## 3. Topic 01 — Capacity Planning and Growth Forecasting

### Q01.1 — Beginner: workload-rate calculation

A pipeline ingests **7.2 million events in one hour**. Assume the arrivals are uniform during that hour.

1. Calculate average events per second.
2. If the observed peak is 2.5 times the average, calculate peak events per second.
3. Explain why the peak rate, not only the hourly average, matters for capacity design.

### Q01.2 — Beginner: storage estimate

A dataset has 18 million rows, with an average stored row size of 800 bytes. The design retains 30 days of data and receives the same volume each day. Ignore compression, indexes, replication, metadata and backups for this first-order estimate.

1. Calculate daily raw payload in decimal GB.
2. Calculate 30-day raw payload in decimal GB.
3. Name at least four omitted factors that a production storage estimate should consider.

### Q01.3 — Intermediate: compound growth and scenarios

Current daily ingest is 4 TB/day. Forecast annual growth is 25% compounded, and volume is assumed to grow uniformly by year for this planning exercise.

1. Estimate daily ingest after two years at the expected 25% annual growth rate.
2. Estimate the annualized ingest run-rate at the end of year two using 365 days/year.
3. Calculate a two-year low/high range if annual compound growth is 20%/30%, respectively.
4. Give two reasons why these estimates should be represented as scenarios rather than a guaranteed forecast.

### Q01.4 — Advanced: headroom and N+1

A workload is forecast to peak at 900 requests/s. A tested node can sustain 300 requests/s while meeting the service objective. The architecture must continue meeting the objective after any one node fails.

1. How many nodes are required to carry 900 requests/s with no failure?
2. How many nodes are required for N+1 capacity under the stated assumptions?
3. If four nodes are deployed, what is the remaining capacity after one node fails, and what is the headroom relative to 900 requests/s?
4. State two caveats before accepting this arithmetic as a production capacity claim.

---

## 4. Topic 02 — Throughput, Latency, Concurrency and Queueing

### Q02.1 — Beginner: metric interpretation

Define **throughput**, **latency**, **concurrency**, and **backlog** in your own words. Give one example of a misleading conclusion that could result from reporting only average latency.

### Q02.2 — Intermediate: Little’s Law

A service completes 240 requests/s. The mean time a request spends in the system is 0.15 seconds.

1. Estimate the average number of requests in the system using Little’s Law.
2. State the assumptions or measurement alignment needed for the calculation to be meaningful.

### Q02.3 — Intermediate: backlog and drain time

A stream processor receives 8,000 events/s and processes 10,500 events/s. The backlog is 1.5 million events.

1. At the current stable rates, calculate net backlog drain rate.
2. Estimate the time required to drain the backlog, assuming arrivals and processing remain constant.
3. If a backfill adds 2,000 events/s to the incoming work rate and the processor’s total capacity stays 10,500 events/s, calculate the new net drain rate.

### Q02.4 — Advanced: saturation diagnosis

A test records the following illustrative observations:

| Offered load | Successful throughput | p95 latency | Error rate | CPU utilisation |
|---:|---:|---:|---:|---:|
| 400 req/s | 398 req/s | 120 ms | 0.1% | 45% |
| 600 req/s | 595 req/s | 180 ms | 0.2% | 62% |
| 800 req/s | 760 req/s | 620 ms | 2.0% | 88% |
| 1,000 req/s | 770 req/s | 1,800 ms | 8.0% | 92% |

1. Identify the likely knee/saturation region.
2. Explain why increasing offered load from 800 to 1,000 req/s is not a successful throughput improvement.
3. Name three additional metrics or tests that would help distinguish CPU saturation from downstream queueing, I/O, or test-harness limits.

---

## 5. Topic 03 — Query Performance and Data Locality

### Q03.1 — Beginner: selectivity and pruning

A table contains 2 TB. A filter returns 2% of rows.

1. If the query scans the entire table, how many TB are scanned?
2. If effective partition pruning reduces bytes scanned to 8% of the table, how many TB are scanned?
3. Explain why 2% result selectivity does not automatically mean 2% of bytes are read.

### Q03.2 — Intermediate: join data movement

A distributed join shuffles 600 GB from one side and 400 GB from the other. A proposed strategy filters the first side before the join, reducing it to 120 GB; the other side remains 400 GB.

1. Calculate total shuffle before and after.
2. Calculate the absolute and percentage reduction in shuffled data.
3. Identify two checks required before recommending the change.

### Q03.3 — Intermediate: query-plan diagnosis

A query has these **non-overlapping sequential critical-path stage durations** in one representative run:

| Stage | Duration |
|---|---:|
| Scan | 12 s |
| Join/shuffle | 38 s |
| Aggregate | 9 s |
| Output | 6 s |

1. Which stage is the largest measured contributor?
2. Calculate its fraction of the 65-second total.
3. Name three measurements that could help determine whether the join stage is slow because of skew, excessive data movement, or insufficient resources.

If a real engine reports overlapping stage wall times, do not sum them as if they were serial; use the query’s critical path or engine-defined elapsed-time metric.

### Q03.4 — Advanced: optimisation trade-off

A proposed index reduces a point lookup from an illustrative 90 ms to 25 ms, but adds 30% to storage and increases write processing time by 12%. Explain how you would decide whether to adopt it. Include workload frequency, read/write mix, correctness, storage, write amplification, and the evidence needed. Do not assume the faster lookup alone settles the decision.

---

## 6. Topic 04 — Scaling, Partitioning, Sharding and Hotspots

### Q04.1 — Beginner: scale up versus scale out

Explain the difference between vertical scaling and horizontal scaling. Give one situation where each may be a reasonable first option and one limitation for each.

### Q04.2 — Intermediate: skew calculation

Four partitions process the following event counts during the same window: **10,000; 12,000; 11,000; 47,000**.

1. Calculate average events per partition.
2. Calculate the skew ratio defined as maximum partition load divided by average partition load.
3. Explain why total capacity may appear sufficient while completion latency remains poor.
4. If the key is time-ordered, compare range partitioning with hash partitioning: name one workload each favours and one risk each introduces.

### Q04.3 — Intermediate: partition-key choice

A customer event stream has one customer producing 22% of all events. The current partition key is `customer_id`. Compare at least two alternative or complementary approaches—such as composite keys, salting/subkeys, or dedicated hot-key handling—and discuss ordering, per-customer aggregation, hot-key mitigation, and read complexity. Explain why a lookup/directory mapping key to shard can add flexibility but also creates a dependency.

### Q04.4 — Advanced: rebalancing decision

A team proposes moving from 8 to 16 shards because one shard is hot. The workload’s skew report shows that 70% of traffic belongs to one key, and every request for that key must be processed in order.

1. Explain why simply doubling shard count may not solve the hotspot.
2. For a separate hypothetical change from 8 to 9 shards using `hash(key) mod N`, estimate the fraction of uniformly distributed keys that would move if shard IDs are retained, and explain why the exact result depends on the mapping scheme.
3. Propose a diagnostic and mitigation sequence.
4. State the correctness and operational risks that must be validated during any key redesign or migration.

---

## 7. Topic 05 — Caching, Materialisation and Serving Trade-offs

### Q05.1 — Beginner: hit ratio

During a five-minute window, a cache records 72,000 usable hits and 18,000 misses. Treat these as all eligible lookups.

1. Calculate hit ratio and miss ratio.
2. If each miss triggers exactly one backend request, calculate the fraction of backend requests avoided relative to sending every lookup to the backend.
3. State why a high hit ratio alone does not prove that latency or correctness objectives are met.
4. Name two cache-key dimensions that may be needed to prevent collisions or cross-tenant data leakage, and explain one trade-off in choosing an eviction policy.

### Q05.2 — Intermediate: cache outage load

A service receives 2,400 application requests/s and has a 95% cache hit ratio. Assume one backend request per miss and no retries/fan-out.

1. Calculate the normal backend miss rate.
2. If the cache is completely unavailable and all requests fall through to the backend, calculate the potential backend request rate.
3. Calculate the multiple of normal miss load represented by the outage load.
4. Propose two safe failure controls if the backend cannot absorb the full request rate.
5. A popular key expires and many requests miss simultaneously. Name this failure mode and two mitigations; explain why increasing TTL alone is not a complete solution.

### Q05.3 — Intermediate: refresh cost and freshness

A materialised view refresh costs an illustrative \$9 per run and runs every 30 minutes continuously. Ignore retries and other costs.

1. Calculate refresh runs/day and refresh cost/day.
2. Under the assumption that source changes occur uniformly between successful refreshes, and refresh completes immediately, estimate average schedule-induced lag and the worst schedule-induced lag approached.
3. Explain how ingestion and refresh duration affect the real end-to-end freshness bound.
4. In a **separate illustrative scenario**, a repeated query costs $0.12 per execution and runs 5,000 times/day. A materialised alternative costs $300/day including refresh and serving. Calculate the daily request-volume break-even point and the modelled daily saving at 5,000 executions, assuming equal correctness and acceptable freshness.

### Q05.4 — Advanced: serving architecture choice

A risk service has two workloads:
- current customer risk lookup: updates must be visible within 20 seconds;
- portfolio dashboard aggregate: up to 8 minutes of lag is acceptable and the query repeatedly scans a large dataset.

Recommend a serving pattern for each. Explain whether a cache and materialised aggregate should share one freshness policy, and identify failure and validation requirements.

---

## 8. Topic 06 — Cost Modeling, Unit Economics and FinOps

All rates below are illustrative placeholders.

### Q06.1 — Beginner: compute cost

A job uses 12 compute units for 5 hours. The assumed price is \$0.40 per compute-unit-hour.

1. Calculate job compute cost.
2. If it runs 22 times in a month, calculate monthly compute cost.
3. Name three cost components that may be omitted from this compute-only estimate.

### Q06.2 — Intermediate: unit economics and failed work

A pipeline incurs \$4,800 in attributed monthly cost. It completes 2.4 million successful events and separately attempts 2.5 million events; the difference is failed or retried work.

1. Calculate cost per million successful events.
2. Calculate cost per million attempted events.
3. Explain which denominator is more appropriate for business unit economics and why, while stating when attempted-work cost is still useful.
4. Explain why either calculated value is an average unit cost, not necessarily the marginal cost of one additional event; identify what incremental costs would be needed to estimate marginal cost.

### Q06.3 — Intermediate: budget variance

A platform budget is \$48,000/month. Actual spend is \$54,000/month.

1. Calculate absolute variance and percentage variance relative to budget.
2. If data volume increased 20% while spend increased 12.5%, calculate the relative change in spend per unit of data using a normalized index where prior volume and spend are both 1.0.
3. Explain why the normalized unit cost does not by itself identify the cause of the change.
4. A $6,000 shared monthly platform cost is allocated by successful-query share: Team A accounts for 70% and Team B for 30%. Calculate each allocation and distinguish showback from chargeback.

### Q06.4 — Advanced: compare alternatives

Two illustrative designs support the same workload for one month:

| Cost component | Option A: on-demand query | Option B: materialised serving |
|---|---:|---:|
| Query/refresh compute | \$21,000 | \$7,500 |
| Storage | \$1,000 | \$3,000 |
| Serving compute | \$0 | \$4,000 |
| Transfer | \$1,200 | \$900 |
| Operations allowance | \$800 | \$1,400 |

1. Calculate total monthly cost for each option.
2. Calculate the absolute and percentage difference relative to Option A. If each option serves 12 million successful queries in the month, also calculate monthly cost per million successful queries for each option.
3. State at least four non-cost criteria that must be checked before choosing Option B.
4. Explain why the table is not evidence of realised savings.

### Q06.5 — Advanced: review and harden a unit-economics helper

A teammate writes:

```python
def cost_per_million(cost, event_count):
    return cost / event_count * 1_000_000

print(cost_per_million(4800, 2_400_000))
```

1. What value does the function return, and what unit should that value have if `cost` is dollars and `event_count` is successful events?
2. Identify at least two missing safeguards or reporting requirements before using this helper in a FinOps report.
3. Modify the function to reject negative cost and non-positive event counts. For a production-quality helper, also consider non-finite values and booleans. Keep the denominator explicit in the call.

---

## 9. Topic 07 — Performance Testing and Capacity Validation

### Q07.1 — Beginner: test types

Distinguish load testing, stress testing, spike testing, endurance testing, and capacity validation. For each, state one question it is intended to answer.

### Q07.2 — Intermediate: define acceptance criteria

A service requirement states: “At a peak of 750 requests/s, p95 latency must be at most 300 ms, error rate must be below 0.5%, and no backlog may continue growing after the initial burst.”

Write a concise test acceptance criterion including workload duration, warm-up, steady-state window, relevant metrics, and a condition for invalidating the run. You may choose reasonable test durations but must label them as test-design assumptions.

### Q07.3 — Intermediate: capacity evidence

A repeated load test finds the service meets all predeclared SLOs at 900 successful requests/s, but fails the p95 latency threshold at 1,050 requests/s. The workload shape, data volume and environment are fixed.

1. What capacity claim is supported by this test?
2. What capacity claim is not supported?
3. What additional test would help validate peak headroom or failure tolerance?

### Q07.4 — Advanced: misleading comparison

Baseline and candidate tests report:

| Condition | Baseline | Candidate |
|---|---|---|
| Data volume | 5 TB | 3 TB |
| Cache state | Cold | Warm |
| Offered load | 700 req/s | 600 req/s |
| p95 latency | 2.8 s | 1.9 s |
| Error rate | 0.4% | 0.2% |

Can the team conclude that the candidate architecture caused the improvement? Explain confounders and design a better comparison.

---

## 10. Topic 08 — Architecture Optimization with Measured Evidence

### Q08.1 — Beginner: label the evidence

Classify each statement as **measured fact, assumption, estimate, hypothesis, recommendation, or verified outcome**:

1. “The query scanned 1.2 TB in run 14.”
2. “Next quarter’s traffic will rise 30%.”
3. “The capacity model predicts four additional workers.”
4. “The long tail is caused by a hot partition.”
5. “Run a replay with a different partition key.”
6. “Across five comparable paired runs, p95 improved 14%, error rate stayed within the predeclared guardrail, and cost per successful query fell 3%.”

### Q08.2 — Intermediate: Amdahl-style reasoning

A component accounts for 60% of total elapsed time. A proposed optimisation makes that component 3 times faster. Assume all other components and workload conditions remain unchanged.

1. Calculate the estimated overall speedup.
2. Calculate the new elapsed time as a fraction of the baseline.
3. Explain two reasons why the observed distributed-system result may differ from the estimate.

### Q08.3 — Intermediate: before-and-after interpretation

An illustrative experiment reports:

| Metric | Baseline | Candidate |
|---|---:|---:|
| p95 latency | 4.0 s | 3.4 s |
| p99 latency | 7.0 s | 7.8 s |
| Cost per successful query | \$0.050 | \$0.047 |
| Error rate | 0.2% | 0.2% |

1. Calculate p95 reduction.
2. Calculate p99 relative change.
3. Calculate unit-cost reduction.
4. Recommend keep, revert, or investigate, and identify the missing evidence needed before a final decision.

### Q08.4 — Advanced: hypothesis and controlled experiment

A team believes a 4× increase in worker count will reduce batch duration. The only evidence is that CPU utilisation reaches 95% during the slow stage. Design a falsifiable experiment: state the hypothesis, baseline/control, intervention, primary metric, guardrails, workload controls, repeatability approach, rollback condition, and one result that would refute the hypothesis.

---

## 11. Cross-topic integrated scenarios

### Q11.1 — Intermediate: cache and capacity sensitivity

An API receives 1,500 requests/s. A cache hit ratio of 92% is assumed, and each miss triggers one backend query.

1. Calculate expected backend query rate.
2. Recalculate it if the measured hit ratio is only 80%.
3. Calculate the percentage increase in backend query rate between the two cases.
4. Explain which topics should be revisited if the backend is overloaded after the lower hit ratio is observed.

### Q11.2 — Advanced: forecast, capacity, and cost

A data platform currently processes 5 TB/day. Expected annual growth is 30% compounded for two years. For a rough capacity model, assume one compute unit can process 0.25 TB/day at the required service objective, and reserve 20% capacity headroom by targeting 80% utilisation. Each compute unit costs an illustrative \$0.55/hour and runs 24 hours/day for 30 days/month. Ignore storage, transfer, discounts, and operational overhead for this exercise.

1. Calculate projected daily volume after two years.
2. Calculate compute units required before headroom, then the integer units required with the 80% target utilisation.
3. Calculate monthly compute cost for the resulting integer capacity.
4. Identify at least four reasons this is a rough estimate rather than a validated capacity/cost model.

### Q11.3 — Advanced: skew, query performance, and cost

A distributed aggregation processes 800 GB of input. One partition receives 35% of all input; the remaining 65% is evenly distributed across 9 partitions.

1. Calculate the average input per partition across all 10 partitions.
2. Calculate the skew ratio of the hot partition relative to the average.
3. Explain why adding more workers without changing the data distribution may not proportionally reduce completion time.
4. Propose a measured validation plan for a partition-key change and name cost and correctness guardrails.

### Q11.4 — Advanced: integrated architecture decision

A fictional risk analytics platform has:
- 250 TB stored data;
- 20–40% annual data-growth scenarios;
- 200 concurrent dashboard users and 1,000 queries/minute at the 10:00 peak;
- a 2 TB nightly batch that must finish by 06:00;
- dashboard p95 objective of 3 seconds;
- batch completion objective by 06:00 on 99% of days;
- illustrative monthly spend of \$60,000 with a spend-growth ceiling of 15%;
- slow dashboards at 10:00 and a rising bill;
- synthetic evidence available: load/latency table, query-plan summaries for ten patterns, per-partition row counts, monthly cost breakdown by service, and two benchmark runs before/after one change.

Prepare an outline of a coherent architecture review. Include:
1. Facts versus assumptions and missing evidence.
2. Capacity/growth scenarios.
3. Performance and query diagnosis.
4. Distribution/skew and serving choices.
5. Two-option cost model and at least one unit-economics metric.
6. A performance-test plan and acceptance criteria.
7. Three ranked optimisation hypotheses with evidence labels.
8. A validation plan, rollback conditions, and evidence register.

Do not claim any optimisation is validated solely because the scenario says two benchmark runs exist; inspect their comparability and limitations.

---

## 12. Final capacity, cost and performance review challenge

### Q12.1 — Capstone deliverable

Using the fictional risk analytics platform in Q11.4—or a clearly labelled synthetic scenario of your own—produce a review package containing:

1. Requirements and assumptions summary.
2. Workload profile and baseline measurement record.
3. Capacity estimate and low/expected/high growth scenarios.
4. Throughput, latency, concurrency, queueing and saturation analysis.
5. Review of the three highest-cost or highest-impact query patterns.
6. Skew analysis and a partitioning/scaling recommendation.
7. Cache/materialisation/serving decision matrix with hit-ratio or freshness sensitivity.
8. Cost model for at least two alternatives, including cost per successful workload and break-even assumptions.
9. Performance test plan with explicit pass/fail criteria defined before the test.
10. Optimisation backlog ranked by impact, confidence, effort, risk and reversibility.
11. Evidence register and one architecture decision record (ADR).
12. Residual risks, limitations, rollback conditions and follow-up measurements.

**Acceptance criteria:** every number has units and a source/evidence label; all assumptions are explicit; the capacity model reconciles with cost-model inputs; the serving choice respects freshness/correctness; the test can fail; recommendations are consistent with query/skew findings; and no recommendation is described as validated unless supplied or simulated measurements support that claim and are labelled accordingly.

### Q12.2 — Reviewer challenge

Ask a reviewer to select any three claims from your report. For each claim, show:
- evidence label;
- source and measurement window;
- formula or reasoning;
- uncertainty/limitations;
- test that could confirm or refute it;
- decision consequence if it is false.

Record at least one recommendation that you changed or qualified after review.

---

# Answer Key and Explanations

## 13. Topic 01 answers

### A01.1

1. One hour = 3,600 seconds. Average rate = \(7{,}200{,}000 / 3{,}600 = 2{,}000\) events/s.
2. Peak rate = \(2{,}000 \times 2.5 = 5{,}000\) events/s.
3. Capacity must absorb peaks and bursts while meeting latency/freshness targets. An hourly average can hide short intervals of overload and growing backlog.

### A01.2

1. Daily payload = \(18{,}000{,}000 \times 800 = 14{,}400{,}000{,}000\) bytes = **14.4 GB/day** in decimal units.
2. 30-day payload = \(14.4 \times 30 = 432\) GB decimal.
3. Examples: compression, indexes/metadata, replication, backups, retained versions, file-format overhead, growth, temporary staging, and recovery copies. The estimate deliberately excludes them.

### A01.3

1. Daily ingest after two years = \(4 \times 1.25^2 = 6.25\) TB/day.
2. Annualized ingest run-rate at that rate = \(6.25 \times 365 = 2{,}281.25\) TB/year (about 2.28 PB/year in decimal units). This is the year-two end-rate annualized, not the total accumulated during the changing-growth year.
3. At 20% growth: \(4 \times 1.20^2 = 5.76\) TB/day. At 30% growth: \(4 \times 1.30^2 = 6.76\) TB/day. The low/high range is 5.76–6.76 TB/day under those assumptions.
4. Growth rate, workload mix, seasonality, retention, compression, and actual growth shape may change. These scenarios are not confidence bounds unless a forecasting method supports that interpretation.


### A01.4

1. Without failure: \(900/300 = 3\) nodes.
2. N+1 requires enough nodes after one failure: \(N-1 \ge 3\), so **4 nodes**.
3. After one failure, capacity = \(3 \times 300 = 900\) requests/s. Headroom relative to demand is \((900-900)/900 = 0\%\). It meets the stated demand but has no remaining headroom.
4. Caveats: per-node capacity may not scale linearly; failure may cause rebalancing or uneven load; dependencies may bottleneck; the 300 req/s result must come from a representative test; peak demand may exceed 900 req/s.

---

## 14. Topic 02 answers

### A02.1

- Throughput: completed work per unit time.
- Latency: elapsed time from a defined start event to a defined completion event.
- Concurrency: work in progress at the same time.
- Backlog: work waiting or accumulated but not yet completed.
- Average-only pitfall: average can look acceptable while p95/p99 requests violate the user-facing objective.

### A02.2

Little’s Law: \(L = \lambda W\). Here \(\lambda = 240\) requests/s and \(W = 0.15\) s, so \(L = 240 \times 0.15 = 36\) requests on average in the system. The arrival/completion rate and residence-time window must describe the same stable system and workload; use consistent boundaries and units.

### A02.3

1. Net drain = processing − arrivals = \(10{,}500-8{,}000=2{,}500\) events/s.
2. Drain time = \(1{,}500{,}000/2{,}500=600\) s = **10 minutes**.
3. If the backfill adds 2,000 events/s of work, total incoming work is 10,000/s; net drain = \(10{,}500-10{,}000=500\) events/s. Drain time at that rate would be 3,000 s = 50 minutes if rates remain constant.

### A02.4

1. The knee is around **600–800 req/s**; at 800, latency and errors rise materially, while throughput is already below offered load.
2. Offered load rises 25% from 800 to 1,000, but successful throughput rises only from 760 to 770 req/s (about 1.32%), while p95 grows from 620 ms to 1,800 ms and errors rise to 8%. Extra offered work mostly creates queueing/failure rather than useful completed work.
3. Examples: queue depth/wait time, CPU run queue and per-core saturation, disk/network I/O, downstream latency, retry/timeout rate, test-client CPU/network, connection pool occupancy, and per-stage timing.

---

## 15. Topic 03 answers

### A03.1

1. Full scan = **2 TB**.
2. 8% of 2 TB = \(2 \times 0.08 = 0.16\) TB = **160 GB** decimal.
3. Row selectivity and byte selectivity differ. Rows may be spread across all files/partitions; columns may be wide; pruning depends on layout, statistics, predicates, and execution plan.

### A03.2

1. Before = \(600+400=1{,}000\) GB. After = \(120+400=520\) GB.
2. Absolute reduction = 480 GB. Percentage reduction = \(480/1{,}000=48\%\).
3. Check semantic equivalence (filter is safe before the join), row counts/cardinality, join type/null behaviour, plan confirms reduced shuffle, and the measured workload includes realistic data/skew. Any two with reasoning are acceptable.

### A03.3

1. Join/shuffle at 38 s.
2. Total = \(12+38+9+6=65\) s. Fraction = \(38/65 \approx 58.46\%\).
3. Per-partition input/output and task duration; shuffle bytes and spill; skew ratio; remote read/network; join cardinality; CPU and queueing. Measurements should discriminate among causes. The 65-second sum is valid because the question defines these as non-overlapping sequential critical-path durations; do not assume this for overlapping engine-stage metrics.


### A03.4

There is no universal answer. Compare the frequency and business value of lookups against the 30% storage increase and 12% slower writes. Measure read latency distribution, total read/write mix, index maintenance overhead, storage cost, write throughput, update/delete semantics, and correctness. Adopt only if the overall workload meets hard objectives and total cost/operational effects are acceptable. Another design may be better if reads are rare or write throughput is critical.

---

## 16. Topic 04 answers

### A04.1

Vertical scaling increases resources on one node/system; it can be a simple option while a workload is limited by a resource that scales up, but has hardware/service ceilings and may not address serial bottlenecks. Horizontal scaling adds nodes/partitions/replicas; it can increase aggregate capacity, but adds coordination, distribution, skew, and operational complexity.

### A04.2

1. Total = \(10{,}000+12{,}000+11{,}000+47{,}000=80{,}000\). Average = \(80{,}000/4=20{,}000\).
2. Skew ratio = \(47{,}000/20{,}000=2.35\).
3. Overall throughput can be limited by the slowest partition/task. The average load hides the 47,000-event partition, which may determine completion time.
4. Range partitioning can support range scans and preserve key locality, but time-ordered writes may concentrate on the newest range. Hash partitioning can spread point access more evenly, but range scans may touch many partitions and scatter-gather can increase latency.


### A04.3

Possible approaches include a composite key, subpartitioning/salting, splitting the hot customer’s workload into independently processable subkeys, or dedicated handling for the hot customer. Each has trade-offs: salting distributes writes but complicates reads/aggregation; per-customer ordering may require a serial merge or dedicated partition; a composite key only helps if it preserves required query/ordering semantics. Measure per-key rates, skew, and query patterns before changing the key.

### A04.4

1. If 70% of traffic is one indivisible ordered key, adding shards does not split that key's serial work. It may distribute other keys but leave the dominant bottleneck unchanged.
2. Under uniform hashes and retained shard IDs, moving from `hash(key) mod 8` to `hash(key) mod 9` changes the shard for approximately \(8/9 \approx 88.9\%\) of keys; about 11.1% remain on the same shard ID. This is a model for that mapping, not a universal migration estimate.
3. Diagnose per-key/partition load and task duration; confirm whether ordering is required for every operation; profile the hot-key critical path; test batching, per-key serial processing with parallel downstream stages, safe subkeying if semantics allow, or dedicated resources; then replay representative data.
4. Risks: ordering violations, duplicate/missing records, state migration, hot-key read aggregation, replay/cutover consistency, increased fan-out, uneven old/new keys, rollback, and monitoring gaps.


### A05.1

1. Total lookups = \(72{,}000+18{,}000=90{,}000\). Hit ratio = \(72{,}000/90{,}000=80\%\). Miss ratio = 20%.
2. If each miss produces one backend request, 80% of requests are avoided relative to all requests reaching the backend.
3. Hit ratio does not establish hit latency, freshness/correctness, miss cost, p95/p99, outage safety, or whether a small number of misses trigger expensive fan-out.
4. Cache-key dimensions may include tenant/security scope, entity ID, query/filter parameters, schema/version, or locale—include only dimensions that change the result or access policy. Eviction policy trades recency/frequency fit and memory efficiency against scan pollution, churn, and implementation/observability complexity; validate against the real access distribution.


### A05.2

1. Normal miss rate = \(2{,}400 \times 0.05=120\) backend requests/s.
2. Full fall-through = up to 2,400 backend requests/s.
3. Multiple = \(2{,}400/120=20\times\).
4. Examples: bounded concurrency, rate limiting, load shedding, circuit breaker, stale fallback only when policy permits, request coalescing, prioritised traffic, or graceful degradation. The backend’s safe capacity must be measured; do not assume it can absorb the outage rate.
5. This is a cache stampede (thundering herd): many concurrent misses for the same expired key. Mitigations include per-key request coalescing/single-flight, jittered TTLs, refresh-ahead, stale-while-revalidate where allowed, and bounded backend concurrency. A longer TTL alone does not prevent synchronized expiry or establish acceptable freshness.


### A05.3

1. Runs/day = \(1{,}440/30=48\). Cost/day = \(48\times\$9=\$432\).
2. Average idealised schedule lag = \(30/2=15\) minutes; worst schedule-induced lag approaches 30 minutes.
3. Ingestion delay, refresh processing, retries, publication delay, and source watermark delay add to the end-to-end lag. A 30-minute schedule does not imply a 30-minute end-to-end guarantee.
4. Break-even volume = \(\$300 / \$0.12 = 2{,}500\) executions/day. At 5,000 executions/day, on-demand cost is \(5{,}000 \times \$0.12 = \$600/day\); the materialised option is $300/day, so modelled savings are $300/day under the stated equal-correctness/freshness assumptions. This is a separate illustrative model, not measured savings.


### A05.4

For current risk lookup, use an authoritative or explicitly consistency-controlled online serving path; cache only if the 20-second freshness contract, invalidation, and read-after-write semantics are proven. For portfolio aggregate, a materialised aggregate may fit because the query is repeated and 8-minute lag is permitted; validate refresh lag and consistency. The policies should not be assumed identical: each data product needs its own freshness contract. Test cache outage, stale fallback, refresh failure, corrections/deletes, cross-view consistency, and reconciliation.

---

## 18. Topic 06 answers

### A06.1

1. Compute units × hours × price = \(12 \times 5 \times \$0.40 = \$24\).
2. Monthly cost = \(22 \times \$24 = \$528\).
3. Possible omissions: storage, data transfer/egress, requests, orchestration, logging/monitoring, retries, replicas, idle capacity, and support/operations. Do not double-count if already included in a bundled price.

### A06.2

1. Cost per million successful events = \(\$4{,}800 / 2.4 = \$2{,}000\) per million successful events.
2. Cost per million attempted events = \(\$4{,}800 / 2.5 = \$1{,}920\) per million attempts.
3. Successful events usually better represent delivered business output; attempted-work unit cost can expose waste/retries and diagnose efficiency. State the denominator explicitly and report both where useful.
4. These are average attributed costs over the stated period. Marginal cost requires the incremental cost caused by additional work—for example, extra compute steps, request/transfer charges, or a capacity tier crossed—while holding other drivers explicit. Average cost does not reveal those increments by itself.


### A06.3

1. Absolute variance = \(\$54{,}000-\$48{,}000=\$6{,}000\) over budget. Percentage variance = \(6{,}000/48{,}000=12.5\%\) over budget.
2. Normalized prior unit cost = 1.0/1.0 = 1.0. New spend index = 1.125; new volume index = 1.20; new unit-cost index = \(1.125/1.20=0.9375\). Unit cost decreased by \(1-0.9375=6.25\%\) relative to the prior index.
3. It does not identify cause because total spend can change across services, workload mix, retention, transfer, commitments, and resource prices. Attribution and cost-driver analysis are required.
4. Team A allocation = \(\$6{,}000 \times 0.70 = \$4{,}200\); Team B = \(\$6{,}000 \times 0.30 = \$1{,}800\). Showback reports attributed costs to teams; chargeback uses the allocation to bill or financially transfer costs to them. The allocation driver should be documented and fit the resource consumed.


### A06.4

1. Option A = \(21{,}000+1{,}000+0+1{,}200+800=\$24{,}000\). Option B = \(7{,}500+3{,}000+4{,}000+900+1{,}400=\$16{,}800\).
2. Difference = $24,000 − $16,800 = **$7,200/month** lower for B. Relative reduction versus A = \(7{,}200/24{,}000=30\%\). At 12 million successful queries/month, A costs \(\$24{,}000/12 = \$2{,}000\) per million successful queries; B costs \(\$16{,}800/12 = \$1{,}400\) per million.
3. Check freshness/lag, correctness/reconciliation, refresh failure, p95/p99 latency, concurrency, reliability/recovery, security, data deletion, operational complexity, and storage growth.
4. The table is illustrative model input, not observed billing or measured savings. Validate usage, rates, all cost categories, period consistency, and performance/correctness before claiming actual savings.


### A06.5

1. The printed output is `2000.0`, numerically equivalent to \(2{,}000\) dollars per million successful events, provided `event_count` actually represents successful events.
2. It does not reject negative costs or zero/negative counts; it does not identify whether the denominator is successful, attempted, or deduplicated events; and it does not label the cost period/currency or state whether costs are attributed and comparable.
3. One corrected version:

```python
import math


def cost_per_million(cost_dollars, successful_events):
    if isinstance(cost_dollars, bool) or not isinstance(cost_dollars, (int, float)):
        raise TypeError("cost_dollars must be a number")
    if isinstance(successful_events, bool) or not isinstance(successful_events, int):
        raise TypeError("successful_events must be an integer")
    if not math.isfinite(cost_dollars) or cost_dollars < 0:
        raise ValueError("cost_dollars must be finite and non-negative")
    if successful_events <= 0:
        raise ValueError("successful_events must be positive")
    return cost_dollars / successful_events * 1_000_000


assert cost_per_million(4800, 2_400_000) == 2000
for bad_cost, bad_count in [(4800, 0), (-1, 10), (float("nan"), 10), (True, 10), (4800, True)]:
    try:
        cost_per_million(bad_cost, bad_count)
    except (TypeError, ValueError):
        pass
    else:
        raise AssertionError(f"invalid inputs were accepted: {bad_cost!r}, {bad_count!r}")
```

The corrected function makes the denominator explicit. It still depends on the caller supplying correctly attributed costs for a stated period.

---

## 19. Topic 07 answers

### A07.1

- Load test: expected or target workload; asks whether SLOs hold under normal/peak load.
- Stress test: beyond expected capacity; asks how and where the system fails.
- Spike test: abrupt demand change; asks how the system handles bursts and recovery.
- Endurance test: sustained load; asks whether leaks, drift, compaction, or backlog growth appear over time.
- Capacity validation: progressively finds the highest workload that meets predefined criteria for a stated workload and environment.

### A07.2

One acceptable test-design assumption:

- warm up for 5 minutes;
- then sustain 750 offered req/s for 15 minutes;
- measure p95 latency, successful throughput, error rate, queue/backlog slope, CPU/memory/I/O/network and downstream saturation during the steady-state window;
- pass if p95 ≤ 300 ms, error rate < 0.5%, and backlog does not have a positive sustained slope after the initial burst;
- invalidate if the load generator saturates, test traffic deviates materially from 750 req/s, environment/configuration changes, or telemetry is incomplete.
- Run multiple repetitions and document cache state, dataset, query mix, and configuration. Durations are assumptions, not roadmap-mandated values.

### A07.3

1. Supported claim: under the tested workload, data volume, environment, and criteria, the service met its SLO at 900 successful req/s.
2. Not supported: universal capacity of 900 req/s for all workload shapes or data volumes; nor that 1,050 is an exact universal hard limit.
3. Test around the knee with repeated load steps, realistic bursts and data skew; test failure headroom/N−1 if required. Define SLO and error criteria before testing.

### A07.4

No. Data volume, cache state, and offered load differ, so the comparison is confounded. A better design uses the same data snapshot/volume, same offered-load profile, same warm/cold cache condition, same environment/instrumentation, and repeated paired or alternating runs. Predefine primary metric and guardrails; retain raw distributions and invalidate runs if the load generator saturates.

---

## 20. Topic 08 answers

### A08.1

1. Measured fact, if the execution record and query definition are available.
2. Assumption or forecast assumption.
3. Estimate from a capacity model.
4. Hypothesis requiring per-partition evidence.
5. Recommendation for a validation experiment.
6. Verified outcome candidate: repeated comparable runs and guardrails support the claim under those conditions; still state workload/environment limitations.

### A08.2

Amdahl’s formula: \(S=1/((1-p)+p/s)\). Here \(p=0.60\), \(s=3\):

\[
S=1/(0.40+0.60/3)=1/(0.40+0.20)=1/0.60\approx1.6667\times
\]

The new elapsed time is \(1/S=0.60\), or 60% of baseline (a 40% reduction). Real systems can differ due to queueing, parallelism, shared-resource contention, changing bottlenecks, and changed data movement.

### A08.3

1. p95 reduction = \((4.0-3.4)/4.0=15\%\).
2. p99 change = \((7.8-7.0)/7.0\approx11.43\%\) increase (worse).
3. Unit-cost reduction = \((0.050-0.047)/0.050=6\%\).
4. **Investigate** unless the predeclared guardrails already dictate a keep/revert decision. p95 and unit cost improve, but p99 worsens. Missing evidence includes run/sample count, variability, comparable workload and environment, error/freshness/correctness, source load, and whether the tail regression violates an SLO.

### A08.4

A defensible experiment:

- **Hypothesis:** the slow stage is CPU-bound and worker count is the limiting resource; raising workers from baseline to a defined candidate level will reduce stage and end-to-end duration.
- **Control:** current worker count and fixed input snapshot/workload.
- **Intervention:** change worker count only, unless a designed experiment explicitly tests interactions.
- **Primary metric:** end-to-end batch duration or p95 latency, whichever maps to the business objective.
- **Guardrails:** correctness, error rate, freshness, cost per successful batch, downstream queueing and source load.
- **Controls:** same data volume/skew, software/configuration, warm-up, background load, cache state, test client and measurement windows.
- **Repeatability:** multiple comparable runs; retain raw stage timings and resource metrics.
- **Rollback:** revert if hard SLO/correctness guardrail fails or cost rises beyond the predeclared limit.
- **Refutation:** CPU utilisation falls but end-to-end duration does not improve, or the slow stage remains blocked on I/O/network/downstream capacity.

---

## 21. Cross-topic integrated answers

### A11.1

1. At 92% hit ratio, miss ratio = 8%; backend rate = \(1{,}500\times0.08=120\) queries/s.
2. At 80% hit ratio, miss ratio = 20%; backend rate = \(1{,}500\times0.20=300\) queries/s.
3. Increase = \((300-120)/120=150\%\). The backend load becomes 2.5× the original modelled rate.
4. Revisit Topic 05 (actual hit ratio, keys, invalidation, admission), Topic 02 (queueing/saturation), Topic 01 (peak capacity), Topic 06 (cost), and Topic 07 (cache-disabled or low-hit-ratio testing). Do not assume the original hit-ratio estimate is reliable without representative access data.

### A11.2

1. Projected volume = \(5\times1.30^2=8.45\) TB/day.
2. Units before headroom = \(8.45/0.25=33.8\). Target utilisation is 80%, so required provisioned capacity = \(33.8/0.80=42.25\); round up to **43 units**.
3. Monthly cost = \(43\times\$0.55\times24\times30=\$17{,}028\).
4. Omissions include non-linear scaling, peak/seasonality, workload mix, data skew, resource overhead, storage/replication, transfer, retries, service quotas, price/discount changes, actual utilisation shape, and the need to validate 0.25 TB/unit/day under the target SLO. The model is not a measured capacity guarantee.

### A11.3

1. Average = \(800/10=80\) GB per partition.
2. Hot partition = \(800\times0.35=280\) GB. Skew ratio = \(280/80=3.5\).
3. If the hot partition is serial or has limited parallelism, adding workers elsewhere may not reduce its critical-path duration. Data redistribution, task granularity, and downstream coordination may dominate.
4. Capture a baseline with per-partition bytes/rows, task duration, spill, CPU, shuffle, completion time, and cost. Test the new key with the same input and workload; validate semantic equivalence, ordering, aggregation correctness, replay/idempotency, p95/end-to-end time, total compute/storage/transfer, and rollback.

### A11.4 — answer outline

A strong response should contain the following:

1. **Evidence labels:** Treat all supplied scenario figures as illustrative facts/assumptions as stated, not actual measurements. Ask for exact workload distributions, retention/compression, current test environment, query definitions, freshness constraints, prices/discounts, and reliability targets.
2. **Capacity:** Build low/expected/high 20–40% growth scenarios. At 250 TB current data, two-year volume range under compound growth is \(250\times1.20^2=360\) TB to \(250\times1.40^2=490\) TB. Clearly distinguish stored data volume from daily ingest/processing throughput.
3. **Performance/query:** Use the load/latency table to identify the SLO knee; rank query patterns by total cost and latency contribution; inspect scan bytes, pruning, joins/shuffle, skew and data locality.
4. **Distribution/serving:** Calculate skew from per-partition row counts; recommend partition changes only if measured skew supports them. Evaluate cache/materialisation by reuse, freshness, failure path and cost.
5. **Cost:** Build two options with consistent billing periods, units, price assumptions and cost components; calculate cost per successful query or batch; perform sensitivity to growth, hit ratio, refresh interval and compute price.
6. **Test plan:** Set p95 ≤ 3 s and batch completion by 06:00 on 99% of days as stated objectives; define workload, duration, warm-up, errors, correctness, freshness, source safety and repeatability. Define pass/fail before running.
7. **Ranked hypotheses:** Examples: query scan/shuffle is dominant; partition skew creates long-tail tasks; repeated dashboard aggregates are candidates for materialisation/cache. Each must be labelled hypothesis until tested.
8. **Validation/ADR:** Compare the two benchmark runs for same workload, data, environment, cache state and configuration; two runs alone may be insufficient to quantify variability. Preserve raw evidence, define guardrails and rollback, and update capacity/cost models after measurement.

A complete answer should include an evidence register and explicitly state what is unknown. The roadmap’s scenario is an integrated exercise, not evidence that any specific optimisation is already proven.

---

## 22. Scoring guidance and mastery criteria

### Suggested scoring

The bank contains **39 numbered questions** (including the two capstone tasks). Suggested weighting:

- Topic questions Q01.1–Q08.4 plus Q06.5: 4 points each = 132 points. Subparts are scored holistically within each question’s four-point rubric; do not assume each subpart earns a separate point.
- Cross-topic Q11.1–Q11.4: 8 points each = 32 points.
- Capstone Q12.1: 24 points.
- Reviewer challenge Q12.2: 8 points.
- **Total: 196 points.**

For 4-point topic questions:
- 1 point: correct concept/approach;
- 1 point: correct formula or relevant evidence;
- 1 point: correct calculation/interpretation with units;
- 1 point: assumptions, limitations, or trade-off.

For integrated/capstone tasks, award points for coherent cross-topic reasoning, traceable evidence, reproducible arithmetic, explicit constraints, validation and rollback—not for choosing a particular technology.

### Suggested mastery bands

| Score | Interpretation | Next step |
|---:|---|---|
| 90%–100% | Strong integrated understanding | Complete capstone and ask for an independent architecture review |
| 80%–89% | Good working proficiency | Review incorrect answers and retest weak topics |
| 65%–79% | Partial proficiency | Revisit the weakest two topics, then retry integrated scenarios |
| Below 65% | Foundations need reinforcement | Rework beginner questions and prerequisites before the capstone |

These are suggested learning thresholds, not official certification cut-offs. A high score does not override a serious misunderstanding of correctness, safety, or evidence quality.

### Completion gate aligned to the roadmap

You are ready for the final project when you can:

- [ ] Complete a workload profile and capacity/growth estimate with three scenarios.
- [ ] Interpret throughput, latency percentiles, concurrency and queueing from a load table.
- [ ] Review and rank expensive query patterns.
- [ ] Calculate distribution skew and justify a partitioning recommendation.
- [ ] Compare caching/materialisation options with hit-ratio and freshness sensitivity.
- [ ] Build a cost model for two options with unit economics and break-even assumptions.
- [ ] Design a performance test with predeclared acceptance criteria.
- [ ] Rank optimisations using impact, payback, risk and evidence level.
- [ ] Maintain an evidence register separating facts, assumptions, estimates, hypotheses, recommendations and validated outcomes.
- [ ] Produce a coherent capacity, cost and performance review plus one ADR.
- [ ] Have a reviewer trace a claim to its source and identify a test that could confirm or refute it.

---

## 23. Remediation map

| If you missed… | Revisit | Remediation task |
|---|---|---|
| Rates, storage units, growth, headroom, N+1 | Topic 01 | Redo Q01.1–Q01.4; label decimal/binary units and scenario assumptions |
| Little’s Law, backlog drain, saturation, percentiles | Topic 02 | Redo Q02.2–Q02.4 and explain successful versus offered throughput |
| Selectivity, scan bytes, joins, query stages | Topic 03 | Redo Q03.1–Q03.3 using units and a query-plan hypothesis |
| Skew, partition keys, rebalancing | Topic 04 | Redo Q04.2–Q04.4; compare range/hash trade-offs, estimate mapping movement, compute skew, and state ordering/aggregation constraints |
| Hit ratio, cache outage, freshness, refresh cost | Topic 05 | Redo Q05.1–Q05.4; define cache-key/failure controls, calculate break-even, and state the hit-ratio denominator and stale-data policy |
| Cost attribution, unit economics, variance, scenario costs | Topic 06 | Redo Q06.1–Q06.5 with a consistent billing period, successful-work denominator, shared-cost allocation, and validated helper inputs |
| Test design, comparability, capacity claims | Topic 07 | Redo Q07.2–Q07.4; define criteria before comparing results |
| Evidence labels, Amdahl, regression, experiment design | Topic 08 | Redo Q08.1–Q08.4 and write a hypothesis that could be falsified |
| Individual topics seem correct but the architecture story conflicts | Cross-topic | Complete Q11.4 and reconcile capacity inputs, cost model, serving choice, and test workload |
| Calculations are right but recommendation is weak | Topic 08 + capstone | Add hard constraints, uncertainty, risks, rollback, and follow-up measurement |

### Recommended study loop

1. Attempt one topic without the answer key.
2. Mark each missed step as concept, formula, unit, arithmetic, evidence interpretation, or trade-off.
3. Re-read only the relevant lesson section and redo the question without looking.
4. Log unresolved gaps rather than hiding them.
5. After all eight topics, complete Q12.1 as one coherent review.
6. Ask a reviewer to challenge the evidence labels and reproduce selected calculations.

---

## 24. Final reminder

The objective is not to produce a confident-sounding architecture recommendation. It is to produce a review where every material number has units and provenance, every assumption is visible, every trade-off is explained, and every proposed improvement has a test that could prove it wrong.

A recommendation is **not validated** merely because it is plausible, because a model predicts a benefit, or because one benchmark run improved. It becomes a measured outcome only within the workload, environment, measurement method, and limits supported by the evidence.
