# Performance Testing and Capacity Validation

## 1. Purpose, scope, and learning outcomes

### Purpose

Capacity plans, queueing models, query reviews, scaling designs, cache assumptions, and cost estimates are hypotheses until they are tested against a defined workload. Performance testing produces controlled evidence about how a system behaves; capacity validation compares that evidence with expected demand, service objectives, and the resources intended to support the workload.

The goal is not to produce a single impressive throughput number. The goal is to determine whether a specified architecture can safely meet specified service requirements under a stated workload, with known headroom, cost, and limitations.

### Scope

This is a vendor-neutral learning guide. It covers test design, safe synthetic workload execution, measurement, capacity interpretation, failure scenarios, and evidence quality. It is not a product-specific load-testing manual and does not require production access, a cloud account, or live customer data. The Python examples require Python 3.9 or later and use only the standard library.

All sample measurements and thresholds in this lesson are **illustrative** unless explicitly described as calculated outputs from a synthetic example. They are not benchmark claims or universal service targets. Replace them with requirements and measurements from the system under review.

### Learning outcomes

By the end, you should be able to:

1. Distinguish performance testing, benchmarking, and capacity validation.
2. Translate SLOs and capacity forecasts into measurable, falsifiable acceptance criteria.
3. Build a workload model that includes request mix, data shape, arrival pattern, concurrency, bursts, and duration.
4. Select appropriate baseline, load, stress, spike, endurance, scalability, and capacity-limit tests.
5. Interpret throughput, latency percentiles, errors, saturation, queues, resource use, and cost together.
6. Control warm-up, cache state, environment, background load, test data, and run-to-run variability.
7. Recognise test-harness limits, coordinated omission, noisy results, and invalid comparisons.
8. Validate peak demand, growth forecasts, headroom, failure-mode capacity, and recovery/backfill overlap.
9. Distinguish observed results from extrapolations and state the limits of every conclusion.
10. Produce a repeatable test plan, baseline report, acceptance criteria, capacity-validation result, risk analysis, and evidence log.

### Core rule

**Write the hypothesis and pass/fail criteria before running the test.** A test that cannot fail is a demonstration, not a validation exercise.

---

## 2. Prerequisites and connections to Topics 01, 02, and 06

The module roadmap identifies Topic 07 prerequisites as **Sequence 1–2 and 6**:

- **Topic 01 — Capacity planning and growth forecasting:** demand profiles, peak factors, growth scenarios, headroom, and resource estimates.
- **Topic 02 — Throughput, latency, concurrency, and queueing:** arrival rates, service times, percentiles, queue growth, utilisation, and Little's Law.
- **Topic 06 — Cost modeling, unit economics, and FinOps:** cost drivers, cost per unit, and the financial consequences of test duration, scaling, and resource choices.

Topic 03 query performance, Topic 04 scaling and hotspots, and Topic 05 caching/materialisation are useful when a test exposes a query bottleneck, skew, a cache effect, or a refresh-related workload. They are not substitutes for the stated prerequisites.

### Carry-forward inputs

Before designing a test, gather or explicitly assume:

- average and peak request/event rates, peak duration, bursts, and growth horizon;
- operation mix, key/query distribution, data size, read/write mix, and expected fan-out;
- service objectives: latency percentiles, error budget, freshness, and availability where applicable;
- resource plan, intended topology, configured quotas, and required headroom;
- expected cache state and refresh/background workloads;
- budget envelope and cost units;
- acceptable degradation and recovery behaviour.

If an input is unknown, record the uncertainty and how it will be measured. Do not silently substitute a convenient number.

---

## 3. Beginner fundamentals

### 3.1 Performance testing, benchmarking, and capacity validation

| Activity | Main question | Typical output | What it does not prove by itself |
|---|---|---|---|
| Performance testing | How does the system behave under a defined workload? | Results against latency, throughput, errors, and resource criteria | Behaviour under every possible workload or environment |
| Benchmarking | How does one implementation/configuration compare with another under a controlled workload? | Comparable measurements and methodology | That the winner meets production requirements or has the lowest total cost |
| Capacity validation | Can the planned resources handle forecast demand and failure conditions with required headroom? | Supported capacity envelope and assumptions | Universal capacity independent of data, query mix, topology, and failure state |

A benchmark can be part of performance testing; performance testing can contribute evidence to capacity validation. Keep the objective explicit so the result is interpreted correctly.

### 3.2 Analogy

Testing a bridge with known truck weights is not just measuring its maximum load once. The engineer specifies truck weights and spacing, instruments the bridge, observes normal and stressed behaviour, checks safety margins, and documents the conditions. A data platform needs the same discipline: known workload, controlled environment, observable signals, pre-agreed limits, and clear limitations.

### 3.3 Test objective, hypothesis, and acceptance criterion

- **Test objective:** the decision the test is intended to support. Example: determine whether the query service supports the forecast peak on the proposed topology.
- **Test hypothesis:** a falsifiable statement about expected behaviour. Example: at 500 requests/second with the representative query mix, p95 latency will remain below 800 ms and errors below 0.1% after warm-up.
- **Acceptance criterion:** the explicit pass/fail rule, including metric, threshold, window, exclusions, and minimum evidence. Example: across three valid 20-minute steady-state runs, each run has p95 ≤ 800 ms, p99 ≤ 1.5 s, errors < 0.1%, no sustained queue growth, and CPU below the pre-agreed saturation threshold.

The thresholds above are illustrative. In a real plan, derive them from SLOs, business needs, and capacity requirements—not from what the test happens to achieve.

### 3.4 Why a test must be able to fail

If criteria are selected after viewing the results, the test is vulnerable to confirmation bias. If the only goal is “run a load test and see what happens,” there is no defined basis for deciding whether capacity is adequate. A falsifiable test has:

1. an explicit question;
2. controlled workload and environment;
3. measurable metrics;
4. thresholds fixed before execution;
5. a rule for invalid runs;
6. evidence sufficient to reproduce the decision.

---

## 4. Test objectives, metrics, and measurement definitions

Every metric needs a name, unit, scope, sampling/aggregation method, and measurement window. Do not compare values collected at different scopes or with different definitions.

### 4.1 Core metrics

| Metric | Definition / unit | Measurement guidance | Common interpretation error |
|---|---|---|---|
| Offered load | Requests/events scheduled by the generator per second | Record intended arrival rate and burst shape | Confusing intended load with achieved load |
| Throughput | Completed operations per second, often split into successful and failed | Report successes, failures, and total completions | Counting accepted requests as completed work |
| Latency | Elapsed time from a defined start event to a defined completion event | Specify client-observed or server-side timing and timeout policy | Comparing server processing time with end-to-end latency |
| p50 / median | Value at or above 50% of observations, per quantile convention | Report sample count and quantile method if comparisons are sensitive | Treating median as representative of the tail |
| p95 / p99 | Latency threshold below which 95% / 99% of observed requests fall | Report per operation class when mixes differ | Claiming tail guarantees from too few observations |
| Error rate | Failed requests divided by the defined request denominator | State whether timeouts, rejected requests, and retries count | Excluding failures without saying so |
| Saturation | Evidence a resource or queue is near its effective limit | Combine utilisation, queueing, latency, and throughput | Assuming one CPU percentage describes all bottlenecks |
| Utilisation | Busy/used resource divided by available resource over a window | Record CPU, memory, I/O, network, connections, quotas | Treating configured capacity as actual consumption |
| Queue/backlog | Work waiting to be processed, measured in items/bytes/time | Record queue depth and its slope over time | Looking at a single depth instead of whether it grows |
| Resource consumption | CPU-seconds, bytes read/written, memory, I/O, network, etc. | Use counters with clear units and reset semantics | Summing overlapping metrics or counting a resource twice |
| Cost per test | Attributable resource spend over the test period | Include test environment, data generation, storage, transfer, and cleanup where relevant | Comparing runs with different durations or retained resources |

### 4.2 Percentiles need sample context

A percentile is an estimate from a sample, not a guarantee for every request. As a rough planning rule, if you want on the order of 100 observations in the upper 1% tail, you need about 10,000 observations because:

\[
N \approx \frac{100}{1 - 0.99} = 10{,}000
\]

This is a rule of thumb, not a statistical guarantee. Dependence between requests, changing workload, heavy tails, measurement errors, and the quantile estimator affect confidence. For p99.9, the same rough rule would imply about 100,000 observations for 100 points in the upper 0.1%. Always report sample counts and repeat-run variability.

### 4.3 Measurement windows and phases

A well-documented run distinguishes:

1. **Setup:** verify version, topology, data, and instrumentation.
2. **Warm-up:** allow caches, JIT compilation, connection pools, and adaptive plans to reach the intended state. Do not include warm-up in steady-state results unless cold-start behaviour is the objective.
3. **Ramp-up:** raise offered load according to a fixed schedule.
4. **Steady-state measurement:** collect the primary acceptance metrics over a declared window.
5. **Cooldown/drain:** stop new arrivals and observe queued work, background recovery, and cleanup.
6. **Post-run validation:** verify data correctness, resource cleanup, and completeness of logs.

Cold-cache and warm-cache tests answer different questions. Do not silently warm the cache in one configuration and compare it with a cold cache in another.

### 4.4 Error rate denominator

A simple definition is:

\[
\text{error rate} = \frac{\text{failed operations}}{\text{all attempted operations}} \times 100\%
\]

But specify whether “attempted” includes generator-side drops, timeouts, retries, duplicate attempts, and operations rejected before reaching the service. Report both logical-operation success and attempt-level failures when retries exist. A retry may turn one logical operation into several attempts; excluding those attempts can conceal resource amplification.

### 4.5 Capacity and headroom

Capacity is not simply the largest observed throughput. Define it as a workload-specific operating envelope that satisfies required latency, error, correctness, and resource criteria. Headroom can be expressed relative to a measured or estimated safe capacity, but the denominator must be stated.

For example, if a validated safe throughput is 800 successful operations/s and forecast peak is 600/s, headroom relative to safe capacity is:

\[
(800 - 600)/800 = 25\%
\]

Alternatively, capacity-to-demand ratio is 800/600 = 1.33×. These are different descriptions; do not call both “25% headroom.” Also test whether the capacity remains valid for the forecast data volume, query mix, cache state, and failure mode.

---

## 5. Step-by-step test-design methodology

### Step 1 — State the decision

Write one sentence describing the decision the evidence will support. Examples: “Validate the planned peak workload on the proposed topology,” “Compare two query layouts under identical data and request mix,” or “Determine whether the service can survive loss of one node while meeting the degraded-mode SLO.”

### Step 2 — Convert requirements into criteria

Create a criteria table before the run.

| Requirement | Metric | Threshold | Window / sample | Pass/fail rule | Source / owner |
|---|---|---|---|---|---|
| Interactive latency | Client-observed p95 | From SLO | Steady-state per run | Every valid run meets threshold | Product/SLO owner |
| Tail latency | Client-observed p99 | From SLO or risk budget | Enough observations; report count | Meets threshold; insufficient samples = inconclusive | Service owner |
| Reliability under load | Error rate | From SLO | All attempted operations during window | Below threshold, with timeouts counted | Service owner |
| Capacity | Successful throughput | Forecast peak plus required headroom | Stable window | Target met without sustained backlog growth | Capacity owner |
| Resource safety | CPU, memory, I/O, connections, quotas | Defined operating limits | Time series and peaks | No sustained saturation or resource exhaustion | Platform owner |
| Cost | Attributable spend per run / per successful unit | Budget or comparison criterion | Same workload and duration | Within budget; exclusions disclosed | FinOps owner |

Do not invent the thresholds in the table. The table is a template; fill it with approved values.

### Step 3 — Build a workload model

Represent the workload as more than “N concurrent users.” Include:

- operation/query mix and relative weights;
- arrival rate over time, including peaks and bursts;
- open- or closed-loop generation;
- concurrency, think time, and request deadlines;
- payload/result sizes and data volume;
- key cardinality, skew, hot keys, and tenant distribution;
- read/write/refresh/backfill mix;
- dependency fan-out, retries, and timeouts;
- freshness/cache state and data age;
- duration, ramp-up, steady-state window, and cooldown.

Use production-derived aggregate distributions when permitted and available. If unavailable, use synthetic data but preserve the characteristics that affect performance, such as skew, cardinality, row size, compression, query selectivity, and temporal patterns. Do not copy sensitive customer records into a test environment merely to make the workload appear realistic.

### Step 4 — Select the load model

**Closed-loop model:** a fixed number of virtual users submit a request, wait for its response, then submit another (possibly after think time). As the service slows, the generator naturally offers fewer requests. This can be appropriate for user-interaction flows but can understate queueing under independent arrival processes.

**Open-loop model:** requests are scheduled independently of completion, usually at a target arrival rate. It can better represent event arrivals or external request traffic, but the generator must record when it failed to schedule or issue work. An overloaded generator can silently create a lower load than intended.

Closed-loop tests can exhibit **coordinated omission**: when the system stalls, the generator sends fewer requests during the stall, so the latency sample misses some delays that would have affected independently arriving requests. Use an appropriate open-loop model or a correction method where the workload requires it; document which method was used.

### Step 5 — Define environment and controls

Record:

- software/build version, runtime, configuration, topology, node/resource sizes, quotas;
- storage layout, indexes, partitions, cache state, materialised-view version;
- dataset size, data distribution, retention, and generation procedure;
- generator host size, network path, tool version, and generator CPU/network use;
- background jobs, ingestion, compaction, refresh, backups, and monitoring overhead;
- dependency versions, rate limits, connection pools, retry policies;
- isolation boundaries, time synchronisation, and run identifiers.

A test environment need not be identical to production, but every difference must be recorded and its effect assessed. A small environment does not automatically scale linearly to a large one.

### Step 6 — Prepare safe test data and execution boundaries

- Use synthetic or anonymised data approved for the environment.
- Define deterministic seeds or data-generation manifests when repeatability matters.
- Create isolated namespaces, schemas, queues, or test tenants.
- Set hard request, duration, concurrency, storage, and spend limits.
- Ensure the generator targets only the intended test endpoint and cannot accidentally issue destructive operations to production.
- Define cleanup, retention, and post-run correctness checks before starting.
- Establish abort conditions for unexpected errors, saturation, cost, or impact to other users.

Never run uncontrolled stress or spike tests against shared production services. Production validation requires explicit approval, safety limits, monitoring, rollback, and an agreed blast radius.

### Step 7 — Choose test types

| Test type | Main question | Typical workload shape | Important outputs |
|---|---|---|---|
| Baseline | What does the current configuration do at a known load? | Moderate, repeatable workload | Baseline latency, throughput, errors, resources, cost |
| Load | Does the system meet criteria at expected or peak load? | Forecast workload with realistic mix | SLO pass/fail and headroom evidence |
| Stress | Where does performance or correctness break? | Gradually increase load beyond expected peak | Saturation point, failure mode, recovery behaviour |
| Spike | What happens after a sudden load increase? | Abrupt burst followed by sustained or reduced load | Queue buildup, scaling delay, error burst, recovery time |
| Endurance/soak | Does the system degrade over time? | Sustained representative load for hours or longer | Leaks, compaction debt, cache churn, drift, resource growth |
| Scalability | How does performance change as resources or data scale? | Controlled change in one dimension at a time | Scaling efficiency and non-linear effects |
| Capacity-limit search | What is the highest workload that meets all criteria? | Stepwise load increases with stable measurement windows | Workload-specific safe operating envelope |
| Regression | Did a code/config/data-layout change degrade a known workload? | Fixed, versioned workload and data | Before/after difference and acceptance result |
| Failure/N−1 | Can the service operate after a component loss? | Load maintained while a node/dependency is removed safely | Degraded capacity, error window, recovery and backlog |
| Backfill overlap | Can historical work coexist with live workload? | Live workload plus controlled replay/backfill | Priority effects, queue growth, freshness, cost |

Do not assume every test must be run at every development stage. Choose a test programme that covers the system's risks and acceptance requirements.

### Step 8 — Run baseline and pilot first

Start with a low-risk pilot to verify that the generator, metrics, dataset, and service agree on request counts and timing. Check that the generator can sustain the target rate. Then establish the baseline under a known configuration. Do not scale the test until instrumentation and safety limits are proven.

### Step 9 — Run, repeat, and preserve evidence

Use the same versioned workload, data manifest, configuration, and measurement definitions for comparisons. Repeat runs where feasible. Capture raw output, aggregate summaries, time series, logs, exceptions, and operator notes. If a run is invalid—for example, the generator saturated or an unrelated job interfered—mark it invalid with a reason; do not quietly discard an inconvenient result.

### Step 10 — Interpret and decide

Compare results with pre-set criteria. Look for the load level at which latency bends upward, queues begin to grow, errors rise, or a resource saturates. Correlate signals across time and use controlled experiments to test the suspected cause. A correlation between CPU and latency is evidence for a hypothesis, not proof that CPU is the root cause.

### Step 11 — Update capacity and cost models

Record measured capacity, the workload it supports, resource configuration, observed headroom, and limitations. Compare with the original estimate and investigate material differences. Update the cost model using measured resource consumption and test duration; separate observed spend from projected production spend.

### Step 12 — Define retest triggers

Retest after material changes to code, query plans, schema, indexes, partitioning, cache policy, resource sizes, quotas, topology, data volume/distribution, dependencies, or workload forecast. A performance result is conditional on the configuration and workload under which it was obtained.

---

## 6. Worked examples

All values below are synthetic and illustrative. They demonstrate calculations; they are not measured benchmarks.

### 6.1 Throughput and error rate

A 10-minute test window contains 300,000 attempted requests. The service completes 297,600 successfully and 2,400 fail or time out. Assume these counts include all client attempts and there are no hidden generator drops.

- Window = 600 seconds.
- Successful throughput = 297,600 / 600 = **496 successful requests/s**.
- Attempt rate = 300,000 / 600 = **500 attempts/s**.
- Error rate = 2,400 / 300,000 = **0.8%**.
- Success fraction = 99.2%.

If the acceptance criterion were “at least 490 successful requests/s and error rate below 0.5%,” throughput would pass and error rate would fail. The overall test fails because every required criterion must pass. Thresholds are illustrative; use the actual service objective.

### 6.2 Percentiles and why average is insufficient

Suppose a test has the following synthetic latency distribution for 10,000 requests:

- 9,400 requests complete in 100 ms;
- 500 requests complete in 400 ms;
- 100 requests complete in 2,000 ms.

Using a nearest-rank percentile convention, p50 is 100 ms, p95 is 400 ms (the 9,500th ordered observation is in the second group), and p99 is 400 ms (the 9,900th observation is at the end of the second group). The slowest 1% includes the 100 requests at 2,000 ms; p99.9 is 2,000 ms under nearest rank. Exact results at group boundaries can depend on the quantile algorithm, so state the method and preferably use raw samples for tool-generated percentiles.

The average is:

\[
\bar{t} = \frac{9{,}400(100) + 500(400) + 100(2{,}000)}{10{,}000}
= 134\text{ ms}
\]

A 134 ms mean conceals requests taking 2 seconds. Always report a distribution, sample count, and percentiles relevant to the SLO.

### 6.3 Capacity-limit search

Assume the following illustrative steady-state runs use the same workload mix and resource configuration. Each run is 15 minutes after warm-up, with 50,000 or more observations.

| Offered rate | Successful throughput | p95 latency | Error rate | Queue trend | Decision under example criteria |
|---:|---:|---:|---:|---|---|
| 400 req/s | 399 req/s | 180 ms | 0.02% | Stable | Pass |
| 500 req/s | 498 req/s | 240 ms | 0.04% | Stable | Pass |
| 600 req/s | 590 req/s | 700 ms | 0.30% | Growing | Fail |

Assume the illustrative criteria are p95 ≤ 500 ms, errors < 0.1%, and no sustained queue growth. The highest tested rate that passes is 500 offered requests/s. This supports a **tested operating point**, not proof that every rate between 500 and 600 behaves identically or that 500 is the exact physical limit. Further stepwise tests around the boundary and repeated runs can refine the estimate.

### 6.4 Capacity estimate error

The roadmap defines:

\[
\text{estimate error} = \frac{\text{measured capacity} - \text{estimated capacity}}{\text{estimated capacity}}
\]

If estimated capacity was 550 successful requests/s and the measured safe capacity is 500/s:

\[
(500 - 550)/550 = -0.0909 \approx -9.1\%
\]

The tested safe capacity is about 9.1% below the estimate. Investigate workload mismatch, skew, concurrency, data size, background jobs, and resource constraints; do not simply increase resources without a bottleneck hypothesis.

This formula requires a positive non-zero estimate and comparable capacity definitions. If the estimated capacity is zero or undefined, percentage error is not meaningful. Report the absolute difference and revise the method instead.

### 6.5 Headroom at forecast peak

Assume the validated safe operating point is 500 requests/s and the forecast peak is 400 requests/s under the same workload mix.

- Capacity-to-demand ratio = 500 / 400 = **1.25×**.
- Spare capacity relative to safe capacity = (500 − 400) / 500 = **20%**.
- Demand as a fraction of safe capacity = 400 / 500 = **80%**.

The phrase “20% headroom” here means 20% of the tested safe capacity remains unused. It does not mean the service can grow 20% from current demand; growth from 400 to 500 is 25%. State the denominator.

### 6.6 Test cost

Assume a synthetic test environment consumes 8 units of compute at an illustrative rate of 0.20 currency units per compute-unit-hour for 3 hours; storage and transfer are separately estimated at 1.50 and 0.75 currency units. These rates are placeholders, not market prices.

- Compute = 8 × 0.20 × 3 = 4.80 currency units.
- Other stated costs = 1.50 + 0.75 = 2.25 units.
- Modelled total = 7.05 units.

This excludes generator compute, logging, retained test data, snapshots, orchestration, and cleanup time unless separately added. For comparisons, include the same cost categories and period for each candidate. If a test runs longer because a queue fails to drain, the extra duration can change cost as well as correctness.

---

## 7. Intermediate test planning and execution

### 7.1 Workload model template

| Dimension | Record | Example of a useful description |
|---|---|---|
| Business operation | Operation and success definition | Read account summary; successful response plus correct version |
| Mix | Percentage or arrival rate per operation class | 70% point reads, 20% aggregates, 10% writes |
| Arrival process | Open/closed, rate schedule, bursts | Open-loop 400/s for 20 min, then 600/s for 5 min |
| Concurrency | Target and observed in-flight requests | Target arrival rate plus measured in-flight distribution |
| Think time | User delay, if modelled | Fixed or distribution with rationale |
| Data volume | Rows, bytes, keys, partitions, retention | 50 million synthetic records, 1 million distinct keys |
| Distribution | Cardinality, skew, temporal patterns | Zipf-like key popularity; documented generator parameters |
| Payload/result size | Median and tail sizes | p50 1 KiB, p95 8 KiB, if supported by evidence |
| Read/write mix | Reads, writes, deletes, updates | Include write amplification and conflict behaviour |
| Cache state | Cold, warm, mixed, expiry pattern | Explicitly reset or warm before each comparable run |
| Background work | Ingestion, refresh, compaction, backup, backfill | Run concurrently if it is a production requirement |
| Dependencies | Fan-out, retry, timeout, quotas | Two downstream calls on 10% of operations |
| Duration | Ramp, warm-up, measurement, cooldown | 5 min ramp, 10 min warm-up, 20 min measurement, drain |
| Safety bounds | Max rate, time, spend, data, abort condition | Stop if error rate exceeds limit for 60 seconds |

Do not treat these example values as a recommended workload. Populate the model from requirements and observed distributions or label it as a synthetic hypothesis.

### 7.2 Test matrix

A test matrix prevents the team from overfitting to one load point. Example structure:

| Test ID | Objective | Workload / configuration | Duration | Required metrics | Acceptance / stop condition |
|---|---|---|---|---|---|
| T-01 | Baseline | Known moderate rate, standard topology | Defined steady window | Latency, throughput, errors, resources | Baseline recorded; no data corruption |
| T-02 | Peak load | Forecast peak plus approved headroom | Defined steady window | All SLO and saturation metrics | All pre-set criteria pass |
| T-03 | Spike | Abrupt rate increase and recovery | Burst + drain | Queue, errors, recovery time | Queue drains within requirement |
| T-04 | Stress | Stepwise increase beyond peak | Until stop threshold | Throughput, p95/p99, errors, resource use | Safe abort and failure mode documented |
| T-05 | Soak | Representative sustained load | Risk-based duration | Resource drift, lag, memory, cost | No unacceptable drift or leak |
| T-06 | N−1 | Load with one component unavailable | Defined failure and recovery window | Degraded SLO, queue, failover | Required degraded service maintained |
| T-07 | Backfill overlap | Live workload plus bounded replay | Representative overlap window | Live latency, backlog, freshness, cost | Live criteria pass; backlog bounded/drains |
| T-08 | Regression | Fixed workload before/after change | Repeatable | Relative and absolute metrics | No unacceptable regression |

### 7.3 Repeatability and controlled variables

For a comparison, change one major factor at a time where feasible. Keep the data manifest, query mix, generator configuration, environment, measurement window, cache state, and background activity consistent. When a change necessarily affects several factors (for example, a new topology), document them and use a test matrix that can isolate the important effects.

Repeat-run variation may arise from noisy neighbours, scheduling, garbage collection, cache state, compaction, network variance, autoscaling, or test data. Report individual runs and a summary (median/range or a justified interval) rather than only the best run. Do not remove outliers unless a pre-defined invalidation rule is met and the cause is recorded.

### 7.4 Baseline report

A useful baseline records:

- test ID, objective, date/time, owner, and approval;
- source revision, build, configuration, topology, quotas, and dependency versions;
- dataset generator version, seed, size, distribution, and checksum/manifest;
- workload schedule, operation mix, arrival model, concurrency, and timeouts;
- warm-up and measurement boundaries;
- raw metrics and per-operation distributions;
- resource and queue time series;
- errors, retries, dropped arrivals, and anomalies;
- cost categories, units, duration, and exclusions;
- validity decision, limitations, and reproduction instructions.

### 7.5 Interpreting an invalid run

Mark a run invalid or inconclusive if, for example:

- the generator could not issue the intended workload;
- a dependency or environment changed unexpectedly;
- monitoring failed or timestamps cannot be aligned;
- unrelated work materially contaminated the run;
- the data was not representative or setup did not complete;
- the run did not collect enough observations for the required metric;
- safety aborts stopped the run before the required window.

Invalid does not mean “bad result.” It means the run cannot support the planned inference. Preserve the evidence and reason, fix the issue, and rerun.

---

## 8. Advanced capacity validation, variability, and failure scenarios

### 8.1 Open-loop versus closed-loop: choose based on the real arrival process

A closed-loop generator with a fixed number of clients constrains concurrency and naturally reduces arrival rate when responses slow. This may match interactive users who wait for a response before acting. It may not match an external event stream or independent requests arriving at a rate set elsewhere.

An open-loop generator schedules arrivals independently. It can reveal queue growth and latency during overload, but it must be capable of sustaining the schedule. Record scheduled, issued, completed, timed-out, and dropped operations separately. If the generator falls behind, do not claim that the target offered load was achieved.

For both models, check whether the generator itself is saturated on CPU, memory, file descriptors, network, connection pools, or its own queue. A test harness can be the bottleneck and falsely cap measured system throughput.

### 8.2 Saturation and the latency knee

A system often shows a region where throughput rises with load, followed by a “knee” where queueing and tail latency rise sharply while throughput improves little. The knee can result from CPU saturation, storage latency, network limits, lock contention, connection pools, rate limits, partition skew, or downstream dependencies.

Use aligned time series for:

- offered and completed rate;
- p50/p95/p99 latency and errors;
- CPU, memory pressure, I/O wait, disk throughput/latency, network, connections, and quotas;
- queue depth and backlog slope;
- per-node/partition/shard metrics;
- cache hit/miss and refresh activity;
- background workload and cost.

The first resource to reach a high utilisation is not necessarily the root cause. For example, CPU can rise because retries increase; the underlying cause may be a slow downstream dependency. Use controlled experiments: change one suspected factor, predict the signal, rerun, and compare.

### 8.3 Validate growth forecasts

Use Topic 01's low/expected/high scenarios to design tests or justified extrapolations. For each scenario, state:

- projected volume and rate at the target date;
- expected peak-to-average ratio and peak duration;
- assumed data growth and retention;
- operation mix and key/query distribution;
- resource configuration and scaling policy;
- required headroom and SLO;
- whether the scenario is directly tested, partially tested, or model-extrapolated.

A capacity test at today's data volume does not validate future data volume if index size, partition count, compaction, scan selectivity, or cache working set changes non-linearly. Use representative future-sized data where feasible, or make extrapolation explicit and validate the scaling relationship with multiple points.

### 8.4 N−1 and failure-mode capacity

N−1 validation asks whether the system can maintain required service when one relevant component is unavailable. The component might be a node, shard, availability zone, worker, broker, or dependency. Define what “one component” means for the architecture and whether failover itself causes a transient error window.

Measure:

- request success and latency during failure detection and failover;
- capacity remaining after the loss;
- rebalance/recovery traffic and data movement;
- queue/backlog growth and drain time;
- correctness, duplication, loss, and ordering where relevant;
- return-to-normal behaviour and cost.

A topology that meets peak load with all nodes may fail after one node is lost. Test degraded capacity directly when the service objective requires it; do not assume the remaining nodes scale linearly.

### 8.5 Backfill and recovery overlap

Historical replay, backfill, reprocessing, index rebuild, or materialisation refresh can compete with live traffic for compute, storage bandwidth, network, and downstream quotas. Test representative overlap when it is a realistic operating mode.

Define priorities and bounds: live traffic may receive reserved capacity, backfill may be throttled, or the backlog may be allowed to grow only within a specified freshness/recovery objective. Measure live SLOs and the rate at which the backlog drains. If a backlog grows during overlap, the system may never catch up after the backfill finishes unless capacity or scheduling changes.

### 8.6 Graceful degradation and stop conditions

Define stop conditions before stress tests. Examples include sustained error rate above an approved limit, queue growth beyond a bound, resource exhaustion, unexpected data corruption, spend ceiling reached, or impact beyond the isolated environment. A stop condition is not necessarily an acceptance criterion; it is a safety boundary.

Also test intended degradation behaviour: rate limiting, load shedding, bounded queues, stale-but-allowed fallback, reduced refresh rate, or rejection of low-priority work. Verify that the system fails predictably and recovers without a retry storm. Do not use stale fallback for a decision path whose correctness contract prohibits it.

### 8.7 Autoscaling and elasticity

Autoscaling tests must include detection delay, provisioning/startup time, warm-up, scale-in behaviour, quota limits, and cost. A system may eventually scale to the required capacity but still violate latency during the scale-out delay. Conversely, rapid scale-in may cause churn or remove warm capacity just before a burst.

Record the full time series: trigger, requested capacity, provisioned capacity, ready capacity, achieved throughput, latency, and cost. Compare steady-state and transient behaviour. Do not claim elasticity from a final resource count alone.

### 8.8 Cost and performance together

Measure the cost of a valid test over a common window and report cost per successful business operation where meaningful. A faster design that doubles compute may be justified by an SLO; a low-cost design that violates correctness or latency is not. Include test-generator cost and any extra refresh, replication, logging, transfer, and retained storage that differ between candidates.

If cost is derived from resource consumption and an illustrative unit rate, label it a modelled estimate. If actual billing exports are not available, do not call it a measured bill. Compare the same workload, duration, data state, and success definition across candidates.

### 8.9 Statistical limitations and claims

- A single run is vulnerable to transient effects; repeat and report variability.
- Averages hide tail latency and workload-class differences.
- Small samples produce unstable high percentiles.
- Requests are often correlated, so naive independence assumptions can overstate confidence.
- Extrapolating from a small environment assumes scaling behaviour that may not hold.
- A before/after improvement can be caused by cache state, data drift, environment changes, or other concurrent changes—not necessarily the intended code change.
- A test proves behaviour only for its workload, configuration, duration, and environment.

Use language that matches evidence: “observed in three runs under workload X” is stronger and more precise than “the system supports X universally.”

---

## 9. Python examples using safe synthetic workloads

The following examples use only the Python standard library and in-memory synthetic data. They do not send network traffic, access production systems, or benchmark real infrastructure. All assertions validate calculations on deterministic inputs.

### 9.1 Bounded synthetic workload schedule

This function generates a finite list of planned arrival timestamps for an open-loop workload. It is a workload description, not a network load generator. The maximum request count prevents accidental unbounded generation.

```python
from math import isclose, isfinite


def planned_arrivals(rate_per_second: float, duration_seconds: float,
                     max_requests: int = 100_000) -> list[float]:
    numeric_inputs = (rate_per_second, duration_seconds)
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x)
           for x in numeric_inputs):
        raise ValueError("rate and duration must be finite numbers")
    if rate_per_second <= 0 or duration_seconds <= 0:
        raise ValueError("rate and duration must be positive")
    if isinstance(max_requests, bool) or not isinstance(max_requests, int) or max_requests <= 0:
        raise ValueError("max_requests must be a positive integer")
    expected_count = rate_per_second * duration_seconds
    if not isfinite(expected_count):
        raise ValueError("planned request count is not finite")
    count = int(expected_count)  # floor: only arrivals inside the requested interval
    if count > max_requests:
        raise ValueError("planned workload exceeds max_requests safety bound")
    # Deterministic evenly spaced schedule; real arrival processes may be bursty.
    return [i / rate_per_second for i in range(count)]


def must_raise_value_error(callable_, *args, **kwargs):
    try:
        callable_(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


arrivals = planned_arrivals(rate_per_second=20, duration_seconds=5)
assert len(arrivals) == 100
assert isclose(arrivals[0], 0.0)
assert isclose(arrivals[-1], 99 / 20)
assert all(a < b for a, b in zip(arrivals, arrivals[1:]))
assert planned_arrivals(0.5, 1) == []  # floor(0.5 expected arrivals) = zero
must_raise_value_error(planned_arrivals, 0, 5)
must_raise_value_error(planned_arrivals, float("nan"), 5)
must_raise_value_error(planned_arrivals, 1, float("inf"))
must_raise_value_error(planned_arrivals, 1, 1, True)
must_raise_value_error(planned_arrivals, 1000, 1000, max_requests=1000)

print({"planned_requests": len(arrivals), "duration_seconds": 5,
       "target_rate_per_second": 20})
```

Expected output: 100 planned requests over the specified five-second schedule, with a 20/s target. The last timestamp is 4.95 seconds because the first request is scheduled at time zero; the schedule contains 100 arrivals, not an arrival at the end boundary.

### 9.2 Summarise latency samples and nearest-rank percentiles

This helper uses the nearest-rank convention: sort samples and choose rank `ceil(p*n)` using one-based rank. Other tools may use interpolation; comparisons must use a consistent method.

```python
from math import ceil, isclose, isfinite


def nearest_rank(values: list[float], percentile: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    if isinstance(percentile, bool) or not isinstance(percentile, (int, float)) or not isfinite(percentile):
        raise ValueError("percentile must be a finite number in (0, 1]")
    if not 0 < percentile <= 1:
        raise ValueError("percentile must be in (0, 1]")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x)
           for x in values):
        raise ValueError("latency samples must be finite numbers")
    ordered = sorted(values)
    rank = ceil(percentile * len(ordered))  # one-based
    return ordered[rank - 1]


latencies_ms = [100.0] * 9400 + [400.0] * 500 + [2000.0] * 100
assert len(latencies_ms) == 10_000
assert nearest_rank(latencies_ms, 0.50) == 100.0
assert nearest_rank(latencies_ms, 0.95) == 400.0
assert nearest_rank(latencies_ms, 0.99) == 400.0
assert nearest_rank(latencies_ms, 0.999) == 2000.0
mean_ms = sum(latencies_ms) / len(latencies_ms)
assert isclose(mean_ms, 134.0)
for bad_values, bad_percentile in [([], 0.95), ([1.0], 0), ([float("nan")], 0.5), ([1.0], float("inf"))]:
    try:
        nearest_rank(bad_values, bad_percentile)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid percentile input should be rejected")

print({"samples": len(latencies_ms), "mean_ms": mean_ms,
       "p50_ms": nearest_rank(latencies_ms, 0.50),
       "p95_ms": nearest_rank(latencies_ms, 0.95),
       "p99_ms": nearest_rank(latencies_ms, 0.99),
       "p99_9_ms": nearest_rank(latencies_ms, 0.999)})
```

Expected results: mean 134 ms, p50 100 ms, p95 400 ms, p99 400 ms, and p99.9 2,000 ms under the stated nearest-rank definition. This sample is synthetic and is not a performance benchmark.

### 9.3 Throughput, errors, and acceptance checks

```python
from math import isclose, isfinite


def summarise_run(attempted: int, successful: int, duration_seconds: float) -> dict:
    if any(isinstance(x, bool) or not isinstance(x, int) for x in (attempted, successful)):
        raise ValueError("request counts must be integers")
    if attempted <= 0 or successful < 0 or successful > attempted:
        raise ValueError("require attempted > 0 and 0 <= successful <= attempted")
    if (isinstance(duration_seconds, bool) or not isinstance(duration_seconds, (int, float))
            or not isfinite(duration_seconds) or duration_seconds <= 0):
        raise ValueError("duration must be a finite positive number")
    failed = attempted - successful
    return {
        "attempt_rate_per_second": attempted / duration_seconds,
        "successful_throughput_per_second": successful / duration_seconds,
        "failed": failed,
        "error_rate": failed / attempted,
    }


run = summarise_run(attempted=300_000, successful=297_600, duration_seconds=600)
assert isclose(run["attempt_rate_per_second"], 500.0)
assert isclose(run["successful_throughput_per_second"], 496.0)
assert isclose(run["error_rate"], 0.008)
for args in [(0, 0, 10), (10, 11, 10), (10.0, 9, 10), (10, 9, float("inf"))]:
    try:
        summarise_run(*args)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid run input should be rejected")

# Illustrative criteria: >=490 successful/s and error rate < 0.5%.
criteria_pass = (run["successful_throughput_per_second"] >= 490
                 and run["error_rate"] < 0.005)
assert criteria_pass is False  # throughput passes; error-rate criterion fails
print({**run, "criteria_pass": criteria_pass})
```

### 9.4 Estimate capacity error and headroom

```python
from math import isclose, isfinite


def capacity_comparison(estimated_safe_rate: float, measured_safe_rate: float,
                        forecast_peak_rate: float) -> dict:
    rates = (estimated_safe_rate, measured_safe_rate, forecast_peak_rate)
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x)
           for x in rates):
        raise ValueError("rates must be finite numbers")
    if estimated_safe_rate <= 0:
        raise ValueError("estimated capacity must be positive")
    if measured_safe_rate < 0 or forecast_peak_rate < 0:
        raise ValueError("measured and forecast rates must be non-negative")
    return {
        "estimate_error_fraction": (measured_safe_rate - estimated_safe_rate) / estimated_safe_rate,
        "capacity_to_demand_ratio": (measured_safe_rate / forecast_peak_rate
                                      if forecast_peak_rate > 0 else None),
        "spare_capacity_fraction": ((measured_safe_rate - forecast_peak_rate) / measured_safe_rate
                                     if measured_safe_rate > 0 else None),
    }


comparison = capacity_comparison(estimated_safe_rate=550,
                                 measured_safe_rate=500,
                                 forecast_peak_rate=400)
assert isclose(comparison["estimate_error_fraction"], -50 / 550)
assert isclose(comparison["capacity_to_demand_ratio"], 1.25)
assert isclose(comparison["spare_capacity_fraction"], 0.20)
assert capacity_comparison(550, 500, 0)["capacity_to_demand_ratio"] is None
assert capacity_comparison(550, 0, 400)["spare_capacity_fraction"] is None
for rates in [(0, 500, 400), (550, -1, 400), (550, 500, float("nan"))]:
    try:
        capacity_comparison(*rates)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid capacity input should be rejected")
print(comparison)
```

The comparison is meaningful only if estimated and measured rates refer to the same operation definition, success criteria, workload mix, and operating conditions.

### 9.5 Compare repeat runs without hiding variability

This example reports each run and a simple median. It does not compute a formal confidence interval or treat the runs as independent samples from every possible production condition.

```python
from math import isclose, isfinite


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("values must not be empty")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x)
           for x in values):
        raise ValueError("run measurements must be finite numbers")
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


p95_runs_ms = [245.0, 252.0, 248.0, 310.0, 251.0]
summary = {
    "runs_ms": p95_runs_ms,
    "median_p95_ms": median(p95_runs_ms),
    "min_p95_ms": min(p95_runs_ms),
    "max_p95_ms": max(p95_runs_ms),
}
assert isclose(summary["median_p95_ms"], 251.0)
assert summary["min_p95_ms"] == 245.0
assert summary["max_p95_ms"] == 310.0
for bad_runs in [[], [1.0, float("inf")]]:
    try:
        median(bad_runs)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid run samples should be rejected")
print(summary)
```

The 310 ms run should be investigated, not silently deleted. If a pre-defined validity rule shows that run was contaminated by a documented external event, label it invalid and preserve the evidence; otherwise include it in the variability discussion.

### 9.6 Simple test-cost estimate

```python
from math import isclose, isfinite


def test_cost(compute_units: float, rate_per_unit_hour: float,
              duration_hours: float, storage_cost: float = 0.0,
              transfer_cost: float = 0.0, generator_cost: float = 0.0) -> dict:
    values = (compute_units, rate_per_unit_hour, duration_hours,
              storage_cost, transfer_cost, generator_cost)
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x)
           for x in values):
        raise ValueError("cost inputs and quantities must be finite numbers")
    if any(value < 0 for value in values):
        raise ValueError("cost inputs and resource quantities must be non-negative")
    compute = compute_units * rate_per_unit_hour * duration_hours
    total = compute + storage_cost + transfer_cost + generator_cost
    return {"compute_cost": compute, "total_modelled_cost": total}


cost = test_cost(8, 0.20, 3, storage_cost=1.50,
                 transfer_cost=0.75, generator_cost=0.0)
assert isclose(cost["compute_cost"], 4.80)
assert isclose(cost["total_modelled_cost"], 7.05)
assert isclose(test_cost(0, 0.20, 3)["total_modelled_cost"], 0.0)
for inputs in [(8, 0.20, 3, -1, 0, 0), (8, float("nan"), 3, 0, 0, 0)]:
    try:
        test_cost(*inputs)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid cost input should be rejected")
# Round only for display; retain full precision in the model result.
print({key: round(value, 2) for key, value in cost.items()})
```

The rate is an illustrative placeholder. The printed values are rounded to two decimal places for readability; the function retains floating-point results. This calculation excludes any cost not passed into the function; list exclusions in a real report.

---

## 10. Practical exercises

Attempt the exercises before reading the answer key. All data are synthetic.

### Level 1 — Beginner: define a test that can fail

A dashboard team says, “It should be fast for 100 users.” Write a one-page test brief containing:

1. A test objective and a falsifiable hypothesis.
2. At least three acceptance criteria with metric, threshold, and measurement window.
3. A workload definition: request mix, arrival/concurrency model, data size, and duration.
4. A warm-up and measurement plan.
5. One safety abort condition and one run invalidation condition.
6. The evidence another engineer needs to reproduce the run.

Do not invent business thresholds without marking them as assumptions requiring approval.

### Level 2 — Intermediate: interpret a test run

A synthetic 5-minute run records 90,000 attempted requests, 89,550 successful requests, and 450 failed requests. The generator reports that it scheduled 100,000 requests but could issue only 90,000 because its own CPU reached 100%. The service p95 is 180 ms and p99 is 900 ms.

Tasks:

1. Calculate attempted rate, successful throughput, and error rate using issued attempts as the denominator.
2. Decide whether the run validates a target offered rate of 333 requests/s.
3. Explain whether the p95/p99 results can be used to declare the target workload passed.
4. Specify the next steps to make the test valid.

### Level 3 — Advanced: capacity and recovery programme

A data service has an expected peak of 700 operations/s and a high-growth scenario of 900 operations/s in the next planning horizon. A pre-test model estimates safe capacity at 850 operations/s. A representative load test finds 780 operations/s is the highest tested point that passes the agreed latency/error criteria. The system has 6 workers, and a node-loss test has not been performed. A historical backfill can run during business hours and is expected to compete for storage bandwidth.

Tasks:

1. Calculate estimate error using measured safe capacity and the stated formula.
2. Calculate spare capacity relative to the current expected peak and capacity-to-demand ratio.
3. State whether the current test validates the 900/s high-growth scenario.
4. Design a minimal additional test matrix for N−1, backfill overlap, spike, and capacity boundary.
5. Identify at least five metrics or controls needed to distinguish a storage bottleneck from a worker CPU bottleneck.
6. Define the evidence required before claiming production readiness and how cost should be recorded.

---

## 11. Answer key and reasoning

### Level 1 — example structure

A good brief names the decision, workload, metric, threshold, window, and evidence. For example, an **illustrative** hypothesis could be: “At a defined 100-user workload with a specified operation mix and data distribution, p95 client latency is below an approved target, errors remain below an approved threshold, and queue depth does not grow throughout a 20-minute steady-state window.” The actual thresholds must come from the SLO owner.

A suitable safety abort might be sustained error rate above an approved bound or test spend reaching a pre-set ceiling. An invalidation condition might be the generator missing its offered rate by more than a pre-defined tolerance or an unrelated workload changing the environment. Reproducibility requires version, configuration, data manifest, workload schedule, timing boundaries, raw metrics, and cleanup steps.

### Level 2 — calculations and decision

- Attempted rate = 90,000 / 300 = **300 attempts/s**.
- Successful throughput = 89,550 / 300 = **298.5 successful operations/s**.
- Error rate = 450 / 90,000 = **0.5%**.
- The run does **not** validate the target offered rate of 333/s because the generator only issued 300/s and saturated itself. The intended schedule is not the achieved workload.
- The latency results describe the issued workload only; they cannot establish behaviour at the target 333/s. Fix or distribute the generator, verify scheduled/issued/completed counts, rerun with a pilot, and preserve the invalid run with its reason.

### Level 3 — calculations and design

1. Estimate error = (780 − 850) / 850 = −70 / 850 ≈ **−8.24%**. The observed safe rate is below the model estimate.
2. Spare capacity versus expected peak = (780 − 700) / 780 ≈ **10.26%** of measured safe capacity. Capacity-to-demand ratio = 780 / 700 ≈ **1.114×**. The peak uses 700 / 780 ≈ 89.74% of the measured safe rate.
3. No. The measured safe rate of 780/s is below the 900/s high-growth forecast. The system needs an architectural/configuration change, a justified forecast change, or a plan to validate a new capacity envelope. Do not extrapolate success from the 700/s current peak.
4. Minimal additional matrix: (a) stepwise boundary tests around the current pass/fail knee with repeat runs; (b) N−1 at expected peak and, if required, at a defined degraded target; (c) live workload plus bounded backfill with queue/freshness metrics; (d) spike from baseline to peak/high-growth rate and recovery; (e) soak at a representative rate long enough to expose drift. Set criteria and aborts before execution.
5. Collect worker CPU and run queue, storage throughput and latency, I/O wait, queue depth and slope, per-worker skew, bytes read/written, network, connection/queue wait, retry rate, and background backfill throughput. A controlled test that throttles backfill or changes storage throughput can help distinguish cause; correlation alone is insufficient.
6. Require representative data/mix, repeated valid runs, SLO criteria met, capacity headroom, N−1/failure and backfill behaviour, correctness checks, generator validation, safe degradation, and runbook/rollback readiness. Record test environment cost over the same time window with compute, storage, transfer, generator, logs, retained data, and exclusions. Modelled costs must be labelled as estimates if actual billing data is unavailable.

---

## 12. Common mistakes and troubleshooting

### 12.1 Common mistakes

| Mistake | Why it undermines evidence | Correction |
|---|---|---|
| Criteria written after seeing results | Encourages rationalising the outcome | Pre-register criteria and invalidation rules |
| Reporting only average latency | Hides slow tail and operation classes | Report p50/p95/p99, sample counts, and per-class distributions |
| Treating scheduled load as achieved load | Generator may be saturated or dropping arrivals | Record scheduled, issued, completed, failed, and dropped counts |
| Closed-loop only for independent arrivals | Slower responses reduce offered load and can hide queueing | Use an appropriate open-loop model or explain why closed-loop is representative |
| Uniform synthetic data | Hides skew, hot keys, cache behaviour, and partition imbalance | Preserve distributions that materially affect performance |
| Mixing warm-up with steady state | Makes runs incomparable and can bias results | Declare phases and measure the intended cache/compilation state |
| One run or best run only | Conceals variability and transient effects | Repeat, report all valid runs, and explain invalidation decisions |
| Test environment differs silently | Comparisons may be invalid | Record differences and justify extrapolation |
| Inferring capacity from one passing point | Does not reveal the limit or headroom | Step through relevant load levels and test failure/recovery modes |
| Ignoring background work | Overstates capacity if refresh/backfill is normally concurrent | Include it or state that it was excluded and why |
| Confusing utilisation with saturation | High usage can be healthy; low average can hide a hot shard | Correlate utilisation, latency, queueing, throughput, and per-partition metrics |
| Claiming a cause from correlation | Several variables may change together | Form a hypothesis and run a controlled test changing one factor |
| Ignoring retries | Retries amplify load and distort error counts | Track logical operations and attempts separately |
| Ignoring test cost | Long or failed runs can incur significant spend | Record duration and all attributable cost categories |
| Treating a test as universal proof | Results are conditional on tested conditions | State scope, assumptions, and untested cases |

### 12.2 Troubleshooting guide

| Symptom | Possible explanations | Evidence to inspect | Next experiment/action |
|---|---|---|---|
| Offered rate exceeds completed throughput and queue grows | Saturation, slow dependency, insufficient workers | Queue slope, dependency latency, resource timelines | Reduce load safely; isolate suspected bottleneck; rerun a controlled step |
| Latency spikes but CPU is low | I/O wait, network, locks, quotas, dependency queue, test harness | I/O latency, network, lock waits, connection pool, downstream metrics | Instrument and vary one dependency or resource at a time |
| CPU is high and throughput stops increasing | CPU-bound processing, retries, skew, inefficient query | Per-thread/worker CPU, retry rate, query profiles, partition distribution | Profile hot path; reduce fan-out/retries; test targeted change |
| Average looks good but p99 fails | Long-tail queries, queueing, skew, GC, downstream stalls | Per-operation percentiles, trace samples, GC and queue metrics | Split workload classes; inspect slow-tail samples and repeat |
| Results vary widely between runs | Noisy environment, cache state, compaction, autoscaling, data drift | Config diffs, resource timeline, cache and background job state | Stabilise controls, repeat, report spread; avoid cherry-picking |
| Target rate not reached | Generator bottleneck, rate limit, connection cap, endpoint issue | Scheduled vs issued counts, generator CPU/network, rejected connections | Scale/fix generator, validate network and limits, repeat pilot |
| Capacity drops with larger data | Index/working-set growth, partition skew, scan amplification, storage pressure | Dataset size, bytes scanned, cache hit, shard metrics, I/O | Test multiple data scales and identify non-linear driver |
| N−1 test violates SLO | Remaining capacity insufficient or failover slow | Failover timing, remaining resource load, rebalance traffic | Add degraded-mode capacity or reduce work; retest failover and recovery |
| Backfill causes live latency regression | Shared I/O/compute, priority conflict, quota contention | I/O bandwidth, backlog, live p99, backfill rate | Throttle/schedule backfill; reserve resources; validate drain time |
| Test cost unexpectedly high | Longer duration, retries, logs, transfer, retained data | Resource-hour timeline, bytes, retry count, billing estimates | Set spend guardrails, reduce invalid runs, automate cleanup |

### 12.3 Limitations to state in every report

- What workload classes were omitted or simplified?
- Was data volume and distribution representative of the planning horizon?
- Was the test environment production-equivalent, smaller, or otherwise different?
- Were cache state, background jobs, quotas, and autoscaling representative?
- Did the generator sustain the intended arrival process?
- How many observations support each percentile, and how variable were runs?
- Which failure scenarios were not tested?
- Which cost categories were measured, modelled, or excluded?
- Which conclusions are observations, which are extrapolations, and which remain hypotheses?

---

## 13. Practical deliverables

### 13.1 Performance-test plan

```text
Test ID and title:
Decision supported:
Objective:
Falsifiable hypothesis:
SLO / business requirement source:
Acceptance criteria (metric, threshold, window, denominator):
Safety abort criteria:
Run invalidation criteria:
Workload model and assumptions:
Open/closed-loop rationale:
Dataset manifest and generation method:
Environment, topology, versions, quotas:
Cache state and background workloads:
Test phases and duration:
Metrics, sampling, and observability:
Repeat count and variability approach:
Cost tracking and exclusions:
Cleanup and correctness checks:
Owner, approver, and run date:
Known limitations:
```

### 13.2 Workload and assumptions register

| Assumption / input | Value | Unit | Source / confidence | Sensitivity | Validation method | Owner |
|---|---|---|---|---|---|---|
| Peak arrival rate | TBD | requests/s | Measured / forecast / assumed | High/medium/low | Compare traffic profiles | TBD |
| Peak duration | TBD | minutes | TBD | TBD | Inspect time series | TBD |
| Operation mix | TBD | % or requests/s | TBD | TBD | Validate against workload logs | TBD |
| Data volume | TBD | rows/bytes/keys | TBD | TBD | Dataset manifest | TBD |
| Key/query skew | TBD | distribution / ratio | TBD | TBD | Distribution summary | TBD |
| Cache state | TBD | cold/warm/mixed | TBD | TBD | Controlled setup | TBD |
| Background work | TBD | jobs/rate | TBD | TBD | Schedule or run concurrently | TBD |
| Generator limit | TBD | requests/s/resources | TBD | TBD | Pilot and generator telemetry | TBD |

### 13.3 Baseline measurement report

```text
Run ID / timestamp:
Objective and criteria version:
Build / source revision:
Environment and topology:
Data manifest / size / distribution:
Workload and arrival model:
Scheduled / issued / completed / failed / dropped:
Warm-up and measurement window:
Throughput: attempted / successful / failed:
Latency: p50 / p95 / p99 / sample count / quantile method:
Error rate and denominator:
CPU / memory / I/O / network / quotas:
Queue depth and slope:
Per-node / partition / shard findings:
Cache and background-work state:
Cost by category / units / period / exclusions:
Run validity and anomalies:
Conclusion against each acceptance criterion:
Limitations and reproduction instructions:
```

### 13.4 Capacity-validation result

| Item | Result | Evidence / limitation |
|---|---|---|
| Estimated safe capacity | TBD | Model version and assumptions |
| Highest tested passing point | TBD | Exact workload, config, criteria, run IDs |
| First observed failing point / knee | TBD | Step size and failure symptoms |
| Estimate error | TBD | Formula and comparable capacity units |
| Forecast peak and growth scenario | TBD | Forecast source and date |
| Headroom definition and value | TBD | State denominator clearly |
| N−1 / failure-mode result | TBD | Tested component and load |
| Backfill/recovery overlap result | TBD | Workload overlap and drain time |
| Cost at validated operating point | TBD | Measured/modelled and exclusions |
| Untested cases | TBD | Risks and follow-up plan |
| Decision | Pass / conditional / fail / inconclusive | Criteria-based rationale |

### 13.5 Bottleneck and risk analysis

For each hypothesis, record symptom, supporting evidence, competing explanations, experiment, predicted outcome, result, and next action. Example format:

| Hypothesis | Evidence supporting it | Alternative explanation | Discriminating test | Result | Risk / action |
|---|---|---|---|---|---|
| Storage bandwidth limits throughput | I/O latency and queue rise at the latency knee | Retries increase I/O as a secondary effect | Bound backfill and rerun same arrival schedule | TBD | TBD |

### 13.6 Repeatable procedure and evidence log

Preserve the exact workload/configuration and data manifest, environment versions, test tool version, commands or run configuration, time boundaries, raw results, derived calculations, screenshots/graphs where useful, anomalies, cleanup evidence, and decision record. Store evidence with access controls and retention appropriate to the data; do not include secrets or sensitive production records.

### 13.7 Regression suite outline

For each critical operation, version the workload and data fixture, establish a stable baseline, define absolute SLO thresholds and relative regression tolerances, and document environmental noise. Run after relevant code/config changes. Use tolerances based on measurement variability and business impact; do not select a tolerance merely to make flaky tests pass.

---

## 14. Mastery criteria and completion gate

### Mastery criteria

You are ready to proceed when you can:

- [ ] Distinguish testing, benchmarking, and capacity validation.
- [ ] Turn SLOs and forecasts into pre-defined, measurable acceptance criteria.
- [ ] Specify operation mix, data distribution, arrival pattern, concurrency, duration, and generator limits.
- [ ] Select appropriate test types and justify open-loop versus closed-loop modelling.
- [ ] Define throughput, percentile, error, saturation, queue, resource, and cost metrics with units and windows.
- [ ] Explain warm-up, steady-state measurement, cooldown, cache state, and repeat-run variability.
- [ ] Identify invalid runs and preserve the reason rather than cherry-picking results.
- [ ] Calculate throughput, error rate, capacity estimate error, and headroom with consistent denominators.
- [ ] Investigate bottlenecks using correlated time series and discriminating experiments.
- [ ] Validate growth, N−1, spike, soak, and backfill overlap where the architecture requires them.
- [ ] State the scope and limitations of capacity claims and distinguish observations from extrapolations.
- [ ] Produce a test plan, assumptions register, baseline report, capacity result, risk analysis, and evidence log.

### Completion gate

Submit a review package for one realistic data-platform workload containing:

1. A test objective and falsifiable hypothesis.
2. Workload model and assumptions register.
3. Pre-approved acceptance criteria and safety/invalidation rules.
4. Baseline and repeatable run procedure.
5. Results with raw counts, latency percentiles, errors, resource and queue evidence.
6. A capacity comparison against the estimate and forecast, with headroom denominator stated.
7. At least one failure or overlap scenario relevant to the architecture.
8. Cost evidence or a clearly labelled cost estimate with exclusions.
9. Bottleneck hypotheses, follow-up experiments, and a rollback/safety plan.
10. A limitations statement identifying what the test does not establish.

**Pass condition:** another engineer can reproduce the test; criteria were fixed before execution; the generator actually delivered the documented workload; calculations are reproducible; the conclusion follows from the evidence; and unknowns are disclosed. If the run is inconclusive, state that clearly and specify the next experiment.

---

## 15. Transition to Topic 08 — Architecture Optimization with Measured Evidence

Topic 07 establishes whether a workload and architecture meet a defined performance and capacity envelope. Topic 08 uses this evidence to decide what to change, prioritise alternatives, and demonstrate whether the change improved the system without violating reliability, correctness, or cost constraints.

Carry forward into Topic 08:

- baseline workload, configuration, and raw metrics;
- SLO-derived acceptance criteria and observed pass/fail results;
- measured capacity envelope, saturation evidence, and headroom definition;
- bottleneck hypotheses and discriminating experiments;
- data distribution, cache state, background work, and known limitations;
- failure-mode and backfill-overlap results;
- test cost and modelled/observed unit economics;
- retest requirements and reproducibility artefacts.

Topic 08 should compare before/after evidence under controlled conditions, use Amdahl-style reasoning where relevant, distinguish correlation from causation, and avoid claiming improvements beyond the tested workload. An optimisation is successful only when its measured benefit justifies its cost and complexity while continuing to satisfy the system's hard requirements.

**Next file:** `08-architecture-optimization-with-measured-evidence.md`.
