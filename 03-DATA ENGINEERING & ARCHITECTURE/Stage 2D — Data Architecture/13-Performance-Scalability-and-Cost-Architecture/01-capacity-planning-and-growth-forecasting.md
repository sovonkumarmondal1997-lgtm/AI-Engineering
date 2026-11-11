# Capacity Planning and Growth Forecasting

**Repository location:** `Stage 2D — Data Architecture/13-Performance-Scalability-and-Cost-Architecture/01-capacity-planning-and-growth-forecasting.md`  
**Topic:** Stage 2D, Module 2D.13, Topic 01  
**Level:** Beginner → Intermediate → Advanced  
**Approach:** Vendor-neutral; calculations and exercises use illustrative assumptions only.

## 1. Purpose and scope

Capacity planning answers four questions:

1. **What work must the platform perform?**
2. **What resources are needed to perform it within agreed service objectives?**
3. **How will those requirements change over time?**
4. **What evidence and triggers will cause us to revise the plan?**

The planning chain is:

```text
Business demand
    → workload profile
    → resource demand
    → peak and failure scenarios
    → growth forecast and uncertainty
    → capacity options and triggers
    → measurement and forecast revision
```

Capacity planning is not simply buying enough storage. A platform can have abundant disk space but still fail because CPU, memory, network throughput, IOPS, connections, a service quota, or a processing window is exhausted.

This lesson establishes the workload and demand model used by later topics. It introduces performance and resilience relationships, but does **not** replace the dedicated lessons on throughput/latency/queueing, query performance, partitioning and hotspots, cost modelling, or performance testing.

### Source-roadmap alignment

The module roadmap identifies Topic 01 as the foundation for the eight-topic sequence. Its stated outcomes are to characterize workload, translate workload into resource requirements, apply linear/compound/scenario growth models, include peak factors and headroom, express uncertainty, and relate capacity decisions to performance, scalability, resilience, and cost. The roadmap also says the lesson files were empty when it was authored; the methods and examples in this lesson are teaching content, not claims that a pre-existing lesson already contained them.

## 2. Learning outcomes

By the end, you should be able to:

- Explain workload, demand, capacity, resource, utilisation, peak, headroom, growth, and forecast.
- Build a workload profile with volume, event rate, mix, read/write ratio, concurrency, seasonality, burstiness, retention, and service objectives.
- Convert records and bytes into daily volume, average events/second, peak rate, and retained storage with consistent units.
- Estimate ingestion, storage, compute, and network demand while stating assumptions and limits.
- Compare linear, compound, and driver-based forecasts using low, expected, and high scenarios.
- Calculate headroom and verify N+1 capacity by checking surviving capacity after a failure.
- Identify the likely limiting resource and account for batch, backfill, and interactive-workload overlap.
- Define measurable re-planning triggers and validate estimates against observed measurements and historical forecast errors.
- Produce a workload profile, assumptions register, capacity worksheet, scenario and sensitivity tables, headroom/N+1 calculations, triggers, and an architecture decision record (ADR) when a material decision warrants one.

## 3. Prerequisites

The module roadmap marks these as essential:

- **Volume, velocity, growth, units, and ranges:** review `../02-Requirements-Constraints-and-Architecture-Decisions/03-data-volume-velocity-variety-and-growth-estimation.md`.
- **Measurable service targets:** review `../02-Requirements-Constraints-and-Architecture-Decisions/04-latency-throughput-freshness-and-availability-targets.md`.
- **Basic arithmetic:** ratios, percentages, powers, and compound growth.

Useful supporting context includes redundancy and recovery throughput in `../12-Reliability-Resilience-and-Disaster-Recovery/03-high-availability-and-redundancy-patterns.md` and `../12-Reliability-Resilience-and-Disaster-Recovery/06-replay-reprocessing-and-backfill-architecture.md`.

You do not need advanced mathematics, a cloud account, or production access. All numbers below are explicitly illustrative.

## 4. Beginner foundations

### 4.1 Core concepts

| Term | Meaning | Practical question |
|---|---|---|
| Workload | The mix and pattern of work presented to a system | What does the platform actually do? |
| Demand | The amount of work requested over a period | How many events, scans, jobs, or queries arrive? |
| Capacity | The amount of work a system can sustain while meeting its service objectives | What can it handle without unacceptable degradation? |
| Resource | A constrained means of processing or storing work | CPU, memory, disk, network, IOPS, connections, or quota? |
| Utilisation | Used capacity divided by usable capacity, for a specified resource and interval | What fraction of the resource is busy? |
| Average load | Total work divided by elapsed time over a stated interval | What is typical over the interval? |
| Peak load | The highest relevant measured or forecast load over a defined interval | What must the system survive? |
| Headroom | Deliberately unconsumed capacity reserved for variability, growth, or recovery | How much margin remains? |
| Growth forecast | An estimate of future workload or resource demand based on a model and assumptions | What might demand look like later? |
| Forecast error | Difference between a forecast and the subsequently observed value | How trustworthy was the prior estimate? |

**Capacity is conditional.** “The system supports 10,000 events/s” is incomplete unless it states the event shape, workload mix, latency/freshness objectives, duration, failure state, and test conditions under which that rate was sustained.

### 4.2 Intuition: planning a restaurant

Imagine a restaurant serving meals:

- Customers arriving are **demand**.
- Menu choices and group sizes describe the **workload mix**.
- Tables, chefs, ovens, and serving staff are **resources**.
- Meals served per hour are **throughput**.
- Waiting time is a **service outcome**.
- Friday evening is a possible **peak**.
- Empty tables and an available backup chef are **headroom** and resilience capacity.
- A forecast of more customers next year informs future staffing and space.

A data platform is similar, but it has multiple resource constraints at once. Extra storage does not compensate for an overloaded CPU, just as more tables do not compensate for too few chefs.

### 4.3 Average is not peak

An average smooths away short intervals of intense demand. Suppose an illustrative ingestion workload receives 2,000,000 events/day.

There are 86,400 seconds in a 24-hour day:

\[
\text{average rate}=\frac{2{,}000{,}000\ \text{events/day}}{86{,}400\ \text{s/day}}
\approx 23.15\ \text{events/s}
\]

If a measured peak factor is 8 for the chosen interval:

\[
\text{peak rate}=23.15\ \text{events/s}\times 8\approx185.19\ \text{events/s}
\]

A platform sized only for 23 events/s would not meet a requirement to accept a sustained 185 events/s peak. The peak factor must come from representative measurements or a documented assumption; it is not a universal constant.

### 4.4 Headroom is intentional, not waste by definition

If peak demand is 12,000 events/s and the chosen maximum target utilisation is 70%, a first-pass required capacity is:

\[
C_{\text{required}}=\frac{D_{\text{peak}}}{u_{\text{target}}}
=\frac{12{,}000\ \text{events/s}}{0.70}
\approx17{,}143\ \text{events/s}
\]

This corresponds to about 5,143 events/s of capacity above the 12,000 events/s peak, under the assumptions of this simplified model.

The target utilisation is a design input to validate with performance testing, not a universal recommendation. Latency can deteriorate before a resource reports 100% utilisation, and different resources have different saturation behaviour.

## 5. Workload characterization and measurement units

### 5.1 Workload profile

Create one row per materially different workload. Do not combine workloads whose resource behaviour or service objectives differ significantly.

| Dimension | What to record | Why it matters |
|---|---|---|
| Data volume | Records/day, bytes/day, TB/month, total retained data | Drives storage, transfer, and often processing |
| Event rate | Average, sustained peak, burst rate; events/s | Drives ingestion and per-event processing |
| Workload mix | Streaming ingest, batch ETL, interactive queries, ML/feature reads, backfills | Different work consumes resources differently |
| Read/write ratio | Operations or bytes read versus written, with denominator specified | Helps estimate I/O and contention |
| Concurrency | Simultaneous jobs, queries, writers, connections | Reveals contention and connection/slot constraints |
| Seasonality | Hour-of-day, weekday, month-end, quarter-end, annual events | Helps identify repeatable peaks |
| Burstiness | How rapidly demand rises and how long it stays elevated | Determines whether elasticity can react in time |
| Retention | Days/months retained; hot/warm/cold policy | Determines retained footprint and lifecycle work |
| Service objectives | Latency percentile, freshness, completion window, availability target | Defines acceptable service, not just maximum raw throughput |
| Growth drivers | Customers, events/customer, products, queries/user, new feeds, policy changes | Supports causal rather than purely extrapolated forecasts |
| Evidence quality | Source, sampling interval, missing periods, confidence | Makes estimates auditable |

**Define the interval.** “Peak = 4× average” is ambiguous until you specify whether it means a one-second peak, a five-minute sustained peak, or the busiest hour. Autoscaling and capacity have different responses to each.

### 5.2 Decimal and binary units

Use decimal units for storage unless the source explicitly uses binary units:

| Unit | Bytes |
|---|---:|
| 1 kB | \(10^3\) |
| 1 MB | \(10^6\) |
| 1 GB | \(10^9\) |
| 1 TB | \(10^{12}\) |
| 1 PB | \(10^{15}\) |

Binary units are different:

| Unit | Bytes |
|---|---:|
| 1 KiB | \(2^{10}=1{,}024\) |
| 1 MiB | \(2^{20}=1{,}048{,}576\) |
| 1 GiB | \(2^{30}\) |
| 1 TiB | \(2^{40}\) |

Do not label a binary quantity as GB or a decimal quantity as GiB. State whether vendor dashboards use decimal or binary units.

### 5.3 Consistent time bases

There are 60 seconds/minute, 3,600 seconds/hour, and 86,400 seconds/day.

For \(N\) events/day:

\[
\lambda_{\text{avg}}=\frac{N\ \text{events/day}}{86{,}400\ \text{s/day}}
\]

For \(N\) events/hour:

\[
\lambda_{\text{avg}}=\frac{N\ \text{events/hour}}{3{,}600\ \text{s/hour}}
\]

The time units cancel, leaving events/s. Always check dimensional consistency before trusting a number.

### 5.4 Record size and volume

If 2,000,000 records/day average 500 bytes/record:

\[
V_{\text{day}}=2{,}000{,}000\ \frac{\text{records}}{\text{day}}
\times500\ \frac{\text{bytes}}{\text{record}}
=1{,}000{,}000{,}000\ \text{bytes/day}=1.0\ \text{GB/day}
\]

This assumes 500 bytes is the average **stored or transferred representation relevant to the estimate**. A logical record size may differ from serialized size, compressed size, index footprint, or physical storage footprint. Measure the representation that matches the resource being planned.

## 6. Core capacity formulas

Each formula below is a first-order estimate. Use it to establish a transparent baseline, then validate it with measurements and tests.

### 6.1 Ingestion volume and rate

Let:

- \(N_d\) = records/day (records/day)
- \(s\) = average encoded record size (bytes/record)
- \(T_d\) = seconds/day = 86,400 seconds/day
- \(p\) = peak factor (dimensionless)

Daily bytes:

\[
V_d=N_d\times s\quad[\text{bytes/day}]
\]

Average event rate:

\[
\lambda_{\text{avg}}=\frac{N_d}{T_d}\quad[\text{events/s}]
\]

Average byte rate:

\[
B_{\text{avg}}=\frac{V_d}{T_d}\quad[\text{bytes/s}]
\]

Estimated peak event rate:

\[
\lambda_{\text{peak}}=\lambda_{\text{avg}}\times p\quad[\text{events/s}]
\]

Estimated peak byte rate, if average record size is representative at peak:

\[
B_{\text{peak}}=B_{\text{avg}}\times p\quad[\text{bytes/s}]
\]

**Limitation:** the average record size and event mix may change during peak periods. Prefer direct peak-byte measurements where available.

### 6.2 Retained storage

A simplified retained-storage estimate is:

\[
S_{\text{physical}}=
V_d\times R\times C\times(1+h)
\]

where:

- \(V_d\) = logical bytes ingested per day (bytes/day)
- \(R\) = retention (days)
- \(C\) = number of full equivalent copies (dimensionless)
- \(h\) = fractional overhead (dimensionless; e.g., 0.20 means 20%)

The result is bytes. This formula assumes the same daily volume throughout retention, full-copy replication, and overhead applied after multiplying logical retained data by copies. If compression is used, define the compression ratio clearly and include it once. For example, with compression ratio \(r=0.4\), compressed data is \(0.4\times\) logical data. Do not simultaneously use a compressed record size and apply the same compression factor again.

**What overhead might include:** indexes, metadata, manifests, small-file effects, logs, temporary work areas, or storage-engine overhead. These components are system-specific and may not scale as a single percentage. Separate them when better evidence is available.

**Deletion lag and retention semantics:** a 90-day retention policy does not always mean physical bytes disappear exactly at day 90. Compaction, snapshots, backups, tombstones, legal holds, and lifecycle delays may extend physical retention. Model these separately if material.

### 6.3 Compute demand from measured work cost

A portable first approximation is based on measured CPU-seconds per unit of work.

Let:
- \(\lambda\) = events/s
- \(c\) = CPU-seconds/event
- \(U\) = target CPU utilisation as a fraction between 0 and 1

CPU demand in core-equivalents:

\[
\text{busy cores}=\lambda\ [\text{events/s}]\times c\ [\text{CPU-s/event}]
\]

Because events/s × CPU-s/event = CPU-s/s, the result is core-equivalents. Required allocated cores at target utilisation:

\[
\text{cores}_{\text{required}}=\frac{\lambda c}{U}
\]

**Illustrative example:** at 1,000 events/s, if measured processing cost is 0.003 CPU-s/event, demand is \(1{,}000\times0.003=3\) busy core-equivalents. At a chosen target utilisation of 60%, the first-pass estimate is \(3/0.60=5\) allocated cores.

This is not a substitute for benchmarking. CPU cost can change with payload size, compression, serialization, skew, cache hit rate, garbage collection, vectorization, query plan, and contention. For batch workloads, estimate CPU-seconds/job and required completion window rather than assuming a uniform per-event cost.

### 6.4 Network demand

For byte rate \(B\) bytes/s:

\[
\text{bits/s}=B\ [\text{bytes/s}]\times8\ [\text{bits/byte}]
\]

Then convert bits/s to Mb/s or Gb/s using decimal network units (1 Mb/s = \(10^6\) bits/s; 1 Gb/s = \(10^9\) bits/s). Include protocol overhead, framing, encryption, retries, acknowledgements, replication traffic, and cross-zone/region transfers as appropriate. Do not assume application payload bytes equal wire bytes.

### 6.5 Storage IOPS and connections

If each operation generates \(q\) storage I/O operations on average and the application issues \(r\) operations/s:

\[
\text{IOPS demand}=r\ [\text{operations/s}]\times q\ [\text{I/O operations/operation}]
\]

This estimate can be misleading if operations have different sizes, cache behaviour, or random/sequential access patterns. Validate with observed IOPS, latency, queue depth, and read/write mix.

Connections are often a **limit**, not a continuously scalable throughput metric. Estimate expected concurrent connections, include connection pools and administrative/system connections, and compare with enforced limits. Do not multiply requests/s by latency and call the result a connection count unless the assumptions behind that relationship are appropriate; the dedicated queueing lesson covers this in depth.

### 6.6 Batch processing window

For a batch with \(W\) units and measured sustained processing rate \(\mu\) units/s:

\[
t_{\text{batch}}=\frac{W\ [\text{units}]}{\mu\ [\text{units/s}]}\quad[\text{s}]
\]

If the batch must finish within a deadline \(D\) seconds, required average processing rate is at least \(W/D\), before accounting for startup, shuffle, retries, skew, dependencies, and contention. Use end-to-end measured duration for service commitments.

## 7. Intermediate forecasting methods

### 7.1 Linear growth

Linear growth assumes a fixed absolute increment each period:

\[
V_n=V_0+n\Delta
\]

where \(V_0\) and \(\Delta\) use the same quantity unit, and \(n\) is the number of periods.

**Illustrative example:** a store starts at 250 TB and grows by 75 TB/year. After three years:

\[
V_3=250\ \text{TB}+3\times75\ \text{TB}=475\ \text{TB}
\]

Use linear growth when an absolute addition is the meaningful driver (for example, a fixed new feed each quarter) and historical evidence supports that assumption. It may understate growth when usage compounds with the installed base.

### 7.2 Compound growth

Compound growth assumes a fixed proportional rate per period:

\[
V_n=V_0(1+g)^n
\]

where \(g\) is the per-period growth fraction and \(n\) counts those periods. Match the rate and period: 30% per year must be applied once per year, not once per month.

**Illustrative example:** 250 TB grows by 30%/year for three years:

\[
V_3=250\ \text{TB}\times1.3^3
=549.25\ \text{TB}
\]

This is larger than the linear example's 475 TB because each year's growth is applied to the larger base.

Compound growth is convenient but not automatically realistic. Growth may slow, saturate, step-change after a launch, or vary by workload. Do not extrapolate a short historical period far into the future without stating the uncertainty.

### 7.3 Driver-based forecast

Model demand from its drivers rather than a single aggregate growth percentage.

For a customer-event workload:

\[
\text{events/day}=
\text{active customers}\times
\frac{\text{events}}{\text{customer-day}}
\]

If there are 400,000 active customers and an illustrative 25 events/customer/day, expected volume is 10,000,000 events/day. If active customers are forecast to grow 15% and events/customer/day 8%, next-period event volume is:

\[
V_1=V_0(1+0.15)(1+0.08)=1.242V_0
\]

That is 24.2% growth, not 23%, because the drivers multiply. Driver-based models help explain *why* demand changes and support scenarios such as customer growth, increased product adoption, or new regulatory events. Avoid double-counting a driver already included in an aggregate growth rate.

### 7.4 Low, expected, and high scenarios

Scenarios are coherent sets of assumptions, not guaranteed probability bounds.

| Scenario | Growth assumption | Peak factor | Interpretation |
|---|---:|---:|---|
| Low | 15%/year | 4× | Lower adoption and less severe peaks |
| Expected | 30%/year | 6× | Planning baseline given current evidence |
| High | 45%/year | 8× | Faster adoption and more severe peaks |

All values in this table are illustrative. Replace them with evidence-based estimates. Forecast each scenario consistently across volume, event rate, storage, and resource demand. Do not combine the low growth assumption with an unrelated high workload mix unless you intentionally define that as a stress scenario.

### 7.5 Forecast uncertainty and error

A forecast is a conditional estimate, not a precise prediction. Record:
- point estimate and range;
- assumptions and evidence source;
- confidence or evidence quality;
- known step changes and dependencies;
- excluded factors;
- forecast horizon and review date.

A simple signed forecast error is:

\[
e=\text{actual}-\text{forecast}
\]

A signed percentage error is:

\[
e_\%=\frac{\text{actual}-\text{forecast}}{\text{forecast}}\times100\%
\]

Percentage error is undefined when the forecast is zero. For operational tracking, store actual, forecast, absolute error, signed error, and whether the forecast was above or below actual. MAPE (mean absolute percentage error) also has problems when actual values are zero or very small; do not use it blindly. Choose an error metric suited to the data and decision.

### 7.6 Sensitivity analysis

Sensitivity analysis asks which uncertain input changes the answer most. Change one variable at a time while holding the others constant, then test interactions separately.

For example, retained storage is proportional to daily volume, retention, copies, and the overhead multiplier. Doubling retention doubles the estimated retained data under the model. Increasing overhead from 10% to 20% changes the multiplier from 1.10 to 1.20, which is a 9.09% increase relative to the former estimate—not a 10% increase in the final total.

Use sensitivity results to prioritize measurement effort. A highly uncertain variable with little impact may matter less than a moderately uncertain variable that dominates capacity.

## 8. Peak load, utilisation, headroom, and failure capacity

### 8.1 Peak factors and sustained demand

A peak factor is:

\[
p=\frac{\text{peak rate over a defined interval}}{\text{average rate over the reference interval}}
\]

It is only meaningful if the interval and averaging window are stated. Use historical time series and include unusual-but-plausible business events. A maximum one-second spike may be less relevant to a batch platform than the highest sustained 15-minute load; conversely, a short burst can overflow a bounded queue even if the daily average is low.

Distinguish:
- **average:** work averaged over the full observation window;
- **sustained peak:** elevated load lasting long enough to matter for resource saturation;
- **burst:** short, sharp increase;
- **design peak:** the selected planning demand, based on evidence and business risk.

### 8.2 Headroom calculation

For demand \(D\) and target utilisation \(U\), where \(0<U\leq1\):

\[
C_{\text{required}}=\frac{D}{U}
\]

Capacity headroom above demand is:

\[
H=C_{\text{required}}-D
\]

Headroom fraction relative to provisioned capacity is:

\[
H_\%=\frac{C_{\text{required}}-D}{C_{\text{required}}}\times100\%
\]

At \(U=0.70\), the headroom fraction is 30% of provisioned capacity; headroom relative to demand is \(1/0.70-1=42.86\%\). These are different denominators. State which one you mean.

### 8.3 N+1 capacity: calculate the failed state

“N+1” usually means enough capacity remains after the loss of one capacity unit to carry the required load. It is not sufficient to say that there are three nodes.

Assume:
- required peak demand \(D=120\) work units/s (illustrative);
- each node can sustain \(K=50\) work units/s at the required service level;
- there are \(n=3\) equal nodes;
- one node may fail.

Normal aggregate capacity is \(3\times50=150\) units/s. After one node fails, surviving capacity is \(2\times50=100\) units/s. Since \(100<120\), this configuration **fails** the N+1 requirement.

With four nodes, normal capacity is \(4\times50=200\) units/s and after one failure \(3\times50=150\) units/s. Since \(150\geq120\), it meets this simplified N+1 capacity requirement.

For equal nodes, a first-pass node count is:

\[
n\geq\left\lceil\frac{D}{K}\right\rceil+f
\]

where \(f\) is the number of nodes assumed unavailable in the failure scenario (for N+1, \(f=1\)). This formula assumes capacity is additive and the remaining nodes can actually reach \(K\) under the target workload. Shared network, storage, coordination, or quota limits can invalidate that assumption. Recalculate per bottleneck resource, not just node count.

### 8.4 Failure, recovery, and backfill overlap

A recovery operation can coincide with normal peak traffic. Model the combined workload rather than treating each workload in isolation.

If normal interactive demand is 800 requests/s and a backfill adds 300 requests/s at the same resource, a conservative first-pass total is 1,100 requests/s. This addition is valid only if both rates use comparable units and consume the same constrained resource in a roughly additive way. If backfill consumes a different mix of CPU, I/O, and network, estimate each resource separately.

Questions to ask:
- Can backfill be throttled, paused, or scheduled off-peak?
- Does recovery compete with foreground ingestion?
- How much backlog accumulates while capacity is unavailable?
- What sustained rate is needed to catch up before the next peak?
- Does the platform need to meet normal service objectives during recovery, or is an explicitly degraded mode acceptable?

Detailed replay and disaster-recovery design belongs in the reliability/resilience module; this lesson makes the capacity overlap explicit.

## 9. Advanced resource constraints and interacting workloads

### 9.1 Capacity is a vector, not one number

Represent resource demand as a vector:

\[
\mathbf{D}=(D_{\text{CPU}},D_{\text{memory}},D_{\text{storage}},
D_{\text{network}},D_{\text{IOPS}},D_{\text{connections}},D_{\text{quota}},\ldots)
\]

A system is feasible only if every relevant resource remains within its effective capacity while meeting service objectives. For each resource, compare demand with usable capacity and a target margin.

| Resource/constraint | Typical symptoms or evidence | Capacity question |
|---|---|---|
| CPU | Sustained busy cores, throttling, rising processing duration | How much CPU work per event/job at the expected mix? |
| Memory | High working set, spills, out-of-memory failures, GC pressure | What is peak concurrent working memory, not just average data size? |
| Storage capacity | Free-space decline, retention breaches | What is retained physical footprint including copies and overhead? |
| Network | Link saturation, retransmits, transfer backlog | What are payload and protocol-adjusted peak bytes/s? |
| IOPS / storage latency | Queue depth and I/O latency rise | What I/O pattern and operation size does the workload create? |
| Connections / slots | Pool exhaustion, rejected work, queueing | What concurrency is allowed and needed? |
| Service quotas | Rejections despite unused local resources | What are hard limits and how long does quota increase take? |
| Metadata/control plane | Slow planning, catalog pressure, coordination delays | Does object/partition/job count grow faster than bytes? |
| Processing window | Jobs miss deadlines despite adequate daily throughput | Can the work finish in the required window under contention? |

Do not infer a bottleneck from one metric alone. Correlate resource metrics with throughput, latency, failures, and workload events.

### 9.2 Mixed workloads and peak overlap

A platform may serve:
- continuous streaming ingestion;
- scheduled batch transformations;
- interactive analytical queries;
- data quality and governance jobs;
- replay/backfill after an incident.

Each workload may be acceptable alone but collectively exceed a shared bottleneck. Create a time-aligned demand table and model overlap explicitly.

| Interval | Streaming (illustrative CPU cores) | Batch | Interactive | Total additive estimate |
|---|---:|---:|---:|---:|
| Normal hour | 4 | 2 | 3 | 9 |
| Month-end peak | 5 | 7 | 5 | 17 |
| Month-end plus backfill | 5 | 7 | 5 + 4 backfill | 21 |

These are fictional values and assume core-equivalent demand is additive. They do not imply that CPU is the only constraint or that 21 cores will necessarily deliver the service objectives. Memory, I/O, network, skew, and scheduling effects may dominate.

### 9.3 Provisioning lead time and elasticity

Capacity response has a delay. Consider:
- **Provisioning lead time:** time from decision/request to usable capacity (procurement, approval, quota, deployment, warm-up, data movement).
- **Elasticity:** ability to add or remove capacity as demand changes.
- **Scale-up/scale-out time:** time for the new capacity to become useful.
- **Workload scheduling:** moving flexible work away from constrained periods.
- **Admission control/throttling:** limiting or delaying work to protect service objectives.

If a forecast says a quota will be reached in six weeks and increasing it takes eight weeks, action is already late. Trigger planning based on projected time-to-exhaustion and lead time, not only on a utilisation threshold.

Elastic capacity is not instantaneous or free of limits. It may be constrained by quotas, startup time, warm-up, data locality, state movement, minimum capacity, or a burst limit. Batch scheduling can be cheaper and simpler than provisioning for a short peak, but only if deadlines and freshness allow it.

### 9.4 Non-linear scaling

Doubling data does not guarantee exactly double compute time or cost. Scaling can be:
- **sublinear** when caching, vectorization, pruning, or fixed overhead helps;
- **approximately linear** when per-unit work is stable;
- **superlinear** when coordination, skew, memory spills, metadata, or data movement grow disproportionately.

A forecast is a workload forecast; converting it to resource capacity requires a measured relationship between workload and resource consumption. That relationship can change after architecture changes or at a different scale.

## 10. Forecast validation and capacity operations

### 10.1 Compare forecasts with actuals

Keep dated forecasts rather than overwriting them. For each forecast horizon, record:
- forecast date and target date;
- forecast value and scenario;
- actual observed value;
- signed and absolute error;
- workload/architecture changes since forecast;
- data quality and measurement gaps;
- corrective action.

Review whether error is biased (consistently under-forecasting or over-forecasting), whether error increases with horizon, and which drivers explain it. A model that repeatedly underestimates month-end peaks needs a changed workload model, not simply another arbitrary safety factor.

### 10.2 Performance-test evidence

An estimate should be treated as a hypothesis until measured. Performance testing should validate:
- representative payload sizes and workload mix;
- average, sustained peak, and burst arrival patterns;
- concurrency and duration;
- service objectives and acceptable degradation;
- resource saturation and bottleneck movement;
- normal and failure-state capacity where required;
- recovery/backfill overlap if it is a real operational scenario.

Record test environment, configuration, data shape, duration, observed rates, resource metrics, failures, and limitations. A short test at a small data volume may not reveal metadata growth, compaction, skew, or long-run memory behaviour. Topic 07 covers performance testing in detail.

### 10.3 Measurable re-planning triggers

Triggers should specify a metric, threshold, duration or forecast horizon, owner, and action. The values below are illustrative, not universal thresholds.

| Trigger (illustrative) | Condition | Action |
|---|---|---|
| CPU headroom | p95 CPU utilisation above 70% for 7 consecutive days | Review trend, workload mix, and benchmarked capacity; update forecast |
| Storage runway | Forecast free storage falls below 60 days of expected net growth | Start expansion/lifecycle review before lead time is consumed |
| Quota runway | Projected quota exhaustion within 8 weeks, while increase lead time is 6 weeks | Request quota or reduce/redistribute demand now |
| Forecast error | Actual peak exceeds expected forecast by 20% for 2 review periods | Investigate driver and peak-factor assumptions; reforecast |
| Service objective | Freshness or latency objective breached during two representative peak tests | Find bottleneck and revise capacity/design or workload schedule |
| Failure margin | N+1 surviving capacity below the agreed peak demand | Escalate resilience/capacity gap; do not claim N+1 readiness |

Adapt thresholds to measured performance curves, risk tolerance, and provisioning delays. A trigger is not operational until someone owns it and knows what action follows.

### 10.4 Re-planning cadence

Choose cadence based on workload volatility and lead time. A reasonable operating pattern may include:
- frequent automated observation of resource and workload metrics;
- weekly or monthly trend and runway review;
- formal forecast refresh after launches, acquisitions, new feeds, retention changes, or architecture changes;
- periodic comparison of forecast with actuals;
- explicit pre-event review before known month-end/seasonal peaks.

The exact cadence is an operational decision. High-volatility workloads or long procurement lead times need earlier signals and more frequent review.

## 11. Worked end-to-end example

This section combines the formulas in one fictional scenario. All numbers are illustrative assumptions, not benchmarks or vendor recommendations.

### 11.1 Inputs

A fictional data platform ingests 2,000,000 records/day, averaging 500 bytes/record. It retains 90 days, stores three full equivalent copies, and applies a 20% overhead allowance. A peak factor of 8 is assumed. The current baseline is used for illustration; future growth is evaluated separately.

### 11.2 Ingestion

Daily volume:

\[
2{,}000{,}000\ \text{records/day}\times500\ \text{bytes/record}
=1{,}000{,}000{,}000\ \text{bytes/day}=1.0\ \text{GB/day}
\]

Average rate:

\[
2{,}000{,}000/86{,}400\approx23.1481\ \text{events/s}
\]

Peak rate:

\[
23.1481\times8\approx185.1852\ \text{events/s}
\]

### 11.3 Retained storage

Logical retained volume:

\[
1.0\ \text{GB/day}\times90\ \text{days}=90\ \text{GB}
\]

After three copies and 20% overhead:

\[
90\ \text{GB}\times3\times1.20=324\ \text{GB}
\]

This is a simplified physical-footprint estimate under the stated assumptions. It excludes any unmodelled snapshots, backups, temporary compaction space, or retention deletion lag.

### 11.4 Capacity at a target utilisation

If the **forecast peak demand** is 250 events/s and the chosen design target is 70% utilisation, the first-pass capacity requirement is:

\[
C_{\text{required}}=250/0.70\approx357.14\ \text{events/s}
\]

A benchmark should then verify that the proposed configuration sustains at least the forecast demand under the same workload mix and service objectives, with the intended margin. Do not treat 250 events/s as a universal platform benchmark or confuse required demand with the system's measured maximum throughput.

### 11.5 Three-year storage scenarios

Start from 324 GB of estimated physical footprint and apply illustrative annual growth rates. This simplified scenario assumes current retention, copies, and overhead remain unchanged and daily volume grows at the same rate as the retained footprint.

| Scenario | Annual compound growth | Year 1 | Year 2 | Year 3 |
|---|---:|---:|---:|---:|
| Low | 15% | 372.6 GB | 428.49 GB | 492.76 GB |
| Expected | 30% | 421.2 GB | 547.56 GB | 711.83 GB |
| High | 45% | 469.8 GB | 681.21 GB | 987.75 GB |

Formula: \(S_n=324\ \text{GB}\times(1+g)^n\). Rounded to two decimal places for display. Actual systems should retain unrounded values in calculations and round only for presentation/provisioning.

### 11.6 Interpretation

The worksheet says the base workload produces 1 GB/day, approximately 23.15 average events/s, and approximately 185.19 events/s at an assumed 8× peak. Under the stated copy and overhead assumptions, 90-day storage is approximately 324 GB. The three-year storage range is wide enough to justify scenario-based planning rather than a single-point purchase.

It does **not** prove that a platform can process the peak, that 70% utilisation is safe, or that three copies deliver the required failure behaviour. Those require measured capacity, resource-specific analysis, service objectives, and failure-state checks.

## 12. Practical Python implementation

The following standard-library-only Python module implements the arithmetic used in this lesson. Save it as `capacity_model.py` or run it in a notebook. It uses decimal GB/TB conventions and validates inputs. It is an estimation worksheet, not a simulator of a specific platform.

```python
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, isfinite
from typing import Iterable

SECONDS_PER_DAY = 86_400
BYTES_PER_GB = 1_000_000_000


def _positive(name: str, value: float, *, allow_zero: bool = False) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{name} must be numeric")
    if isinstance(value, float) and not isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value < 0 or (value == 0 and not allow_zero):
        qualifier = "non-negative" if allow_zero else "positive"
        raise ValueError(f"{name} must be {qualifier}")


def _finite_result(name: str, value: int | float) -> int | float:
    """Reject floating-point overflow rather than returning infinity silently."""
    if isinstance(value, float) and not isfinite(value):
        raise ValueError(f"{name} exceeds the numeric range supported by this model")
    return value


def daily_volume_bytes(records_per_day: float, average_record_bytes: float) -> float:
    """Return bytes/day from records/day × bytes/record."""
    _positive("records_per_day", records_per_day, allow_zero=True)
    _positive("average_record_bytes", average_record_bytes, allow_zero=True)
    return _finite_result("daily volume", records_per_day * average_record_bytes)


def average_events_per_second(events_per_day: float) -> float:
    """Convert events/day to events/second."""
    _positive("events_per_day", events_per_day, allow_zero=True)
    try:
        result = events_per_day / SECONDS_PER_DAY
    except OverflowError as exc:
        raise ValueError("event rate exceeds the numeric range supported by this model") from exc
    return _finite_result("average event rate", result)


def peak_rate(average_rate_per_second: float, peak_factor: float) -> float:
    """Estimate peak events/second from average rate × dimensionless factor."""
    _positive("average_rate_per_second", average_rate_per_second, allow_zero=True)
    _positive("peak_factor", peak_factor)
    return _finite_result("peak rate", average_rate_per_second * peak_factor)


def retained_storage_bytes(
    daily_bytes: float,
    retention_days: float,
    copies: int,
    overhead_fraction: float = 0.0,
    compression_ratio: float = 1.0,
) -> float:
    """
    Estimate physical bytes = daily logical bytes × retention × compression ratio
    × full-equivalent copies × (1 + overhead fraction).

    compression_ratio is compressed/logical size (e.g. 0.4 means 40% of logical
    bytes remain). Do not use already-compressed daily_bytes and apply compression
    again.
    """
    _positive("daily_bytes", daily_bytes, allow_zero=True)
    _positive("retention_days", retention_days, allow_zero=True)
    _positive("copies", copies)
    _positive("overhead_fraction", overhead_fraction, allow_zero=True)
    _positive("compression_ratio", compression_ratio)
    if not isinstance(copies, int) or isinstance(copies, bool):
        raise TypeError("copies must be an integer")
    if compression_ratio > 1:
        raise ValueError("compression_ratio must be <= 1 for this convention")
    result = (
        daily_bytes
        * retention_days
        * compression_ratio
        * copies
        * (1 + overhead_fraction)
    )
    return _finite_result("retained storage estimate", result)


def _growth_rate(name: str, value: float) -> None:
    """Validate a finite numeric growth rate greater than -100%."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{name} must be numeric")
    if isinstance(value, float) and not isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value <= -1:
        raise ValueError(f"{name} must be greater than -1")


def compound_growth(initial: float, annual_growth: float, years: int) -> float:
    """Forecast a quantity after integer periods of compound growth."""
    _positive("initial", initial, allow_zero=True)
    _growth_rate("annual_growth", annual_growth)
    if not isinstance(years, int) or isinstance(years, bool) or years < 0:
        raise ValueError("years must be a non-negative integer")
    try:
        result = initial * (1 + annual_growth) ** years
    except OverflowError as exc:
        raise ValueError("forecast exceeds the numeric range supported by this model") from exc
    return _finite_result("forecast", result)


def linear_growth(initial: float, increment_per_period: float, periods: int) -> float:
    """Forecast a quantity after fixed absolute increments."""
    _positive("initial", initial, allow_zero=True)
    _positive("increment_per_period", increment_per_period, allow_zero=True)
    if not isinstance(periods, int) or isinstance(periods, bool) or periods < 0:
        raise ValueError("periods must be a non-negative integer")
    return _finite_result("linear forecast", initial + increment_per_period * periods)


def required_capacity(demand: float, target_utilisation: float) -> float:
    """Capacity needed to keep utilisation at or below a target fraction."""
    _positive("demand", demand, allow_zero=True)
    if not isinstance(target_utilisation, (int, float)) or isinstance(target_utilisation, bool):
        raise TypeError("target_utilisation must be numeric")
    if isinstance(target_utilisation, float) and not isfinite(target_utilisation):
        raise ValueError("target_utilisation must be finite")
    if not 0 < target_utilisation <= 1:
        raise ValueError("target_utilisation must be in (0, 1]")
    try:
        result = demand / target_utilisation
    except OverflowError as exc:
        raise ValueError("required capacity exceeds the numeric range supported by this model") from exc
    return _finite_result("required capacity", result)


def required_equal_nodes(
    demand_per_second: float,
    capacity_per_node_per_second: float,
    unavailable_nodes: int = 1,
) -> int:
    """
    Return nodes required so surviving nodes can carry demand after the stated
    number of nodes are unavailable. Assumes equal, additive node capacity.
    """
    _positive("demand_per_second", demand_per_second, allow_zero=True)
    _positive("capacity_per_node_per_second", capacity_per_node_per_second)
    if not isinstance(unavailable_nodes, int) or isinstance(unavailable_nodes, bool):
        raise TypeError("unavailable_nodes must be an integer")
    if unavailable_nodes < 0:
        raise ValueError("unavailable_nodes must be non-negative")
    if demand_per_second == 0:
        return unavailable_nodes
    try:
        required_active_nodes = ceil(demand_per_second / capacity_per_node_per_second)
    except OverflowError as exc:
        raise ValueError("node count exceeds the numeric range supported by this model") from exc
    return required_active_nodes + unavailable_nodes


def cpu_cores_required(
    events_per_second: float, cpu_seconds_per_event: float, target_utilisation: float
) -> float:
    """Estimate allocated core-equivalents from measured CPU-seconds/event."""
    _positive("events_per_second", events_per_second, allow_zero=True)
    _positive("cpu_seconds_per_event", cpu_seconds_per_event, allow_zero=True)
    return required_capacity(
        events_per_second * cpu_seconds_per_event, target_utilisation
    )


@dataclass(frozen=True)
class Scenario:
    name: str
    annual_growth: float


def scenario_table(
    initial_daily_bytes: float,
    scenarios: Iterable[Scenario],
    years: int,
) -> dict[str, list[float]]:
    """Return forecast daily bytes by growth scenario for years 0..years.

    Peak factors are intentionally not part of this storage-only helper; model
    peak rates separately from the corresponding workload-rate forecast.
    """
    _positive("initial_daily_bytes", initial_daily_bytes, allow_zero=True)
    if not isinstance(years, int) or isinstance(years, bool) or years < 0:
        raise ValueError("years must be a non-negative integer")
    output: dict[str, list[float]] = {}
    for scenario in scenarios:
        if not isinstance(scenario, Scenario):
            raise TypeError("each scenario must be a Scenario instance")
        if not isinstance(scenario.name, str) or not scenario.name.strip():
            raise ValueError("scenario name must be a non-empty string")
        if scenario.name in output:
            raise ValueError(f"duplicate scenario name: {scenario.name}")
        _growth_rate("annual_growth", scenario.annual_growth)
        output[scenario.name] = [
            compound_growth(initial_daily_bytes, scenario.annual_growth, year)
            for year in range(years + 1)
        ]
    return output


if __name__ == "__main__":
    records_per_day = 2_000_000
    record_bytes = 500
    daily_bytes = daily_volume_bytes(records_per_day, record_bytes)
    avg_rate = average_events_per_second(records_per_day)
    peak = peak_rate(avg_rate, 8)
    storage = retained_storage_bytes(daily_bytes, 90, copies=3, overhead_fraction=0.20)

    print(f"Daily volume: {daily_bytes / BYTES_PER_GB:.2f} GB/day")
    print(f"Average rate: {avg_rate:.2f} events/s")
    print(f"Peak estimate: {peak:.2f} events/s")
    print(f"90-day storage estimate: {storage / BYTES_PER_GB:.2f} GB")
    print(f"3-year 30% growth: {compound_growth(storage / BYTES_PER_GB, 0.30, 3):.2f} GB")
```

### 12.1 Automated assertions

Save the following as `test_capacity_model.py` beside the module and run `python test_capacity_model.py`. These assertions cover core calculations and selected edge cases without requiring third-party packages.

```python
import math

from capacity_model import (
    average_events_per_second,
    compound_growth,
    cpu_cores_required,
    daily_volume_bytes,
    linear_growth,
    peak_rate,
    required_capacity,
    required_equal_nodes,
    retained_storage_bytes,
    scenario_table,
    Scenario,
)

# Worked example: 2,000,000 records/day × 500 bytes/record = 1 GB/day.
daily = daily_volume_bytes(2_000_000, 500)
assert daily == 1_000_000_000
assert math.isclose(average_events_per_second(2_000_000), 23.1481481481, rel_tol=1e-9)
assert math.isclose(peak_rate(average_events_per_second(2_000_000), 8), 185.185185185, rel_tol=1e-9)
assert retained_storage_bytes(daily, 90, 3, 0.20) == 324_000_000_000

# Linear and compound growth: zero periods preserve the initial value.
assert linear_growth(250, 75, 0) == 250
assert compound_growth(250, 0.30, 0) == 250
assert math.isclose(compound_growth(250, 0.30, 3), 549.25)

# Headroom and CPU estimate.
assert math.isclose(required_capacity(12_000, 0.70), 17_142.8571428571)
assert math.isclose(cpu_cores_required(1_000, 0.003, 0.60), 5.0)

# N+1: 120 units/s, each node 50 units/s, one unavailable -> 4 nodes.
assert required_equal_nodes(120, 50, unavailable_nodes=1) == 4
assert (4 - 1) * 50 >= 120
assert (3 - 1) * 50 < 120

# Zero workload, large value, and no compression are handled consistently.
assert average_events_per_second(0) == 0
assert required_equal_nodes(0, 50, unavailable_nodes=1) == 1
assert retained_storage_bytes(0, 90, 3, 0.20) == 0
assert compound_growth(1_000_000_000_000, 0.0, 5) == 1_000_000_000_000

# Scenario outputs include the baseline (year 0) and all requested years.
table = scenario_table(
    1_000_000_000,
    [Scenario("low", 0.15), Scenario("expected", 0.30), Scenario("high", 0.45)],
    years=3,
)
assert len(table["expected"]) == 4
assert table["expected"][0] == 1_000_000_000
assert math.isclose(table["expected"][3], 2_197_000_000)

# Invalid inputs must fail explicitly, including non-finite and wrong-type values.
for fn in (
    lambda: daily_volume_bytes(-1, 500),
    lambda: required_capacity(100, 0),
    lambda: required_capacity(100, 1.1),
    lambda: required_capacity(100, float("nan")),
    lambda: required_capacity(100, True),
    lambda: compound_growth(100, -1, 2),
    lambda: compound_growth(100, float("nan"), 2),
    lambda: compound_growth(100, float("inf"), 2),
    lambda: compound_growth(100, "0.1", 2),
    lambda: retained_storage_bytes(100, 30, 2, compression_ratio=1.2),
    lambda: retained_storage_bytes(100, 30, 2, compression_ratio=0),
    lambda: required_equal_nodes(100, 0),
    lambda: scenario_table(100, [Scenario("duplicate", 0.1), Scenario("duplicate", 0.2)], 2),
    lambda: scenario_table(100, [Scenario("bad-growth", float("nan"))], 2),
    lambda: scenario_table(100, [Scenario("", 0.1)], 2),
):
    try:
        fn()
    except (TypeError, ValueError):
        pass
    else:
        raise AssertionError("Expected invalid input to raise TypeError or ValueError")

# Larger but practical values remain calculable; floating-point overflow fails clearly.
assert daily_volume_bytes(10**12, 10**6) == 10**18
for fn in (
    lambda: daily_volume_bytes(1e308, 10),
    lambda: average_events_per_second(10**10000),
    lambda: peak_rate(1e308, 10),
    lambda: retained_storage_bytes(1e308, 2, 1),
    lambda: linear_growth(1e308, 1e308, 1),
    lambda: required_capacity(1e308, 1e-308),
    lambda: required_equal_nodes(1e308, 1e-308),
    lambda: compound_growth(100, 1e308, 2),
):
    try:
        fn()
    except ValueError:
        pass
    else:
        raise AssertionError("Expected an overflowing calculation to fail explicitly")

print("All capacity-model assertions passed.")
```

### 12.2 Expected output and verification

Running `python capacity_model.py` should print approximately:

```text
Daily volume: 1.00 GB/day
Average rate: 23.15 events/s
Peak estimate: 185.19 events/s
90-day storage estimate: 324.00 GB
3-year 30% growth: 711.83 GB
```

The test script prints:

```text
All capacity-model assertions passed.
```

The expected values are independently derived from the formulas shown above. The assertions check the key arithmetic, growth, zero-workload handling, N+1 survival, large values, and invalid inputs. If you edit a formula, update the tests only after independently confirming the revised expected result.

## 13. Practical exercises

Do not look at the solution hints until you have written down your assumptions and units.

### 13.1 Beginner — transaction feed

**Illustrative inputs:** 2,000,000 transactions/day, 500 bytes/transaction, 90-day retention, three full copies, 20% overhead, peak factor 8.

Tasks:
1. Calculate logical GB/day.
2. Calculate average and estimated peak events/s.
3. Estimate 90-day physical storage.
4. State at least four assumptions that could make the result wrong.

**Validation targets:** 1.0 GB/day; approximately 23.15 average events/s; approximately 185.19 peak events/s; approximately 324 GB under the stated storage model.

### 13.2 Intermediate — three-year risk analytics store

**Illustrative inputs:** current physical footprint 250 TB; annual compound growth scenarios 20%, 30%, and 40%; peak demand 12,000 events/s; chosen target utilisation 70%.

Tasks:
1. Forecast storage for years 1–3 under each scenario.
2. Calculate required capacity for the stated peak and target utilisation.
3. Compare the year-3 range and identify which assumption most affects the result.
4. Describe one reason the storage growth rate might differ from event-rate growth.

**Validation targets:** year 3 is \(250(1.2)^3=432\) TB, \(250(1.3)^3=549.25\) TB, and \(250(1.4)^3=686\) TB. First-pass required capacity is approximately 17,143 events/s. All figures are illustrative.

### 13.3 Advanced — mixed platform with failure and backfill

Build a capacity plan for a fictional platform with streaming, scheduled batch, interactive queries, and backfill. Define:
- a time-aligned workload profile;
- low/expected/high growth assumptions;
- CPU, memory, storage, network, IOPS, connections, and quota constraints;
- a sustained peak and a short burst;
- provisioning lead time and elasticity delay;
- an N+1 scenario for each critical capacity unit;
- a backfill-overlap scenario;
- service objectives and an acceptable degraded mode, if any;
- measurable triggers and an ADR for the most consequential decision.

Tasks:
1. Show demand and capacity with units for each constrained resource.
2. Prove that surviving capacity after the specified failure meets or misses the required demand.
3. Explain how normal work and recovery work compete.
4. Rank the top five sensitivities and explain how you would reduce uncertainty.
5. Define what evidence from a load test would invalidate your assumptions.

**Review standard:** every number has a unit, source or explicit illustrative label, and confidence statement. No claim of resilience is accepted without arithmetic for the surviving state.

## 14. Industry-style scenarios and architecture trade-offs

All organizations and values in this section are fictional.

| Scenario | Options | Trade-offs | Evidence needed |
|---|---|---|---|
| Month-end workload reaches 4× normal for three days | Size permanently for the peak; scale elastically; schedule flexible jobs outside the peak | Permanent peak sizing is simple but may leave idle capacity; elasticity may start too slowly; scheduling may affect freshness/deadlines | Historical peaks, startup/warm-up time, test at peak, business deadlines |
| Customer acquisition increases active customers by 40% | Provision toward high case; provision toward expected case with early triggers; stagger migration | High-case provisioning lowers shortfall risk but may over-provision; expected-case planning depends on trigger quality and lead time | Acquisition plan, per-customer usage, migration overlap, early observed actuals |
| Backfill competes with interactive analytics | Run concurrently; throttle; pause; use isolated resources; schedule off-peak | Concurrent recovery finishes sooner but may breach interactive objectives; throttling protects foreground work but prolongs recovery | Per-resource measurements, acceptable recovery time, service objectives |
| Storage appears ample but jobs miss deadlines | Add compute; inspect I/O/network/metadata; change scheduling or data layout | Adding compute helps only if compute is the limiting resource; other changes may require design work | Correlated metrics, query/job profiles, representative performance tests |

A defensible recommendation names the constraint, the evidence, the expected benefit, the operational risk, and how the outcome will be measured.

## 15. Common mistakes and troubleshooting

| Mistake | Why it fails | Correction |
|---|---|---|
| Planning only from daily averages | Bursts and sustained peaks are hidden | Inspect time-series data at relevant intervals and state peak definition |
| Mixing bytes, bits, GB, GiB, seconds, and days | Produces order-of-magnitude errors | Write units in each formula and convert explicitly |
| Treating a peak factor as universal | Peak patterns vary by workload and interval | Derive it from representative observations or label it as an assumption |
| Treating logical data as physical storage | Ignores copies, compression, indexes, metadata, and retention lag | Model logical and physical footprints separately |
| Applying compression twice | Underestimates storage | Define whether input bytes are pre- or post-compression |
| Treating target utilisation as a magic constant | Performance may degrade before saturation; resources differ | Choose a target based on measured performance and service objectives |
| Counting nodes without checking the failure state | Remaining nodes may not carry required demand | Calculate surviving capacity and compare with required load |
| Adding workload rates that use different units | Totals become meaningless | Convert to a common unit and model each resource independently |
| Forecasting from one growth percentage without drivers | Hides launches, mix shifts, and saturation | Use driver-based forecasts and scenario analysis |
| Using a compound rate with the wrong time period | Overstates or understates growth | Align rate period and forecast step |
| Treating a forecast as a guarantee | Business and system behaviour change | Report ranges, error history, assumptions, and triggers |
| Scaling every resource together | Can waste money and leave the bottleneck untouched | Identify the constrained resource and measure before/after |
| Ignoring lead time | Action begins after capacity is needed | Trigger on projected runway minus provisioning lead time |
| Ignoring backfill/recovery overlap | Normal and recovery demand can exceed shared capacity | Model concurrent workload and the acceptable degraded mode |
| Claiming tests passed without running them | Makes the artifact unauditable | Record the actual command, environment, result, and known gaps |

### Troubleshooting checklist

When an estimate looks implausible:
1. Check the input quantity and time base.
2. Check decimal/binary units and bytes/bits.
3. Recompute the formula manually with units.
4. Verify copies, compression, overhead, and retention are each applied once.
5. Compare peak factor and target utilisation with the same time interval and workload mix.
6. Check whether capacity is measured under the required service objectives.
7. Confirm the failed-state calculation uses surviving—not normal—capacity.
8. Compare the model with observations and update the assumptions register.

## 16. Deliverables and reusable templates

### 16.1 Workload profile template

| Field | Value | Unit / interval | Evidence source | Confidence / notes |
|---|---|---|---|---|
| Workload name and owner |  |  |  |  |
| Work type / mix |  |  |  |  |
| Average volume |  |  |  |  |
| Sustained peak / burst |  |  |  |  |
| Average record or operation size |  |  |  |  |
| Read/write ratio |  |  |  |  |
| Concurrency |  |  |  |  |
| Seasonality / peak interval |  |  |  |  |
| Retention |  |  |  |  |
| Service objectives |  |  |  |  |
| Growth drivers |  |  |  |  |
| Measurement gaps |  |  |  |  |

### 16.2 Assumptions register template

| ID | Assumption | Value/range | Unit | Evidence/source | Confidence | Impact if wrong | Owner / review date |
|---|---|---|---|---|---|---|---|
| A-01 | Average record size |  | bytes/record |  |  |  |  |
| A-02 | Peak factor and interval |  | × / interval |  |  |  |  |
| A-03 | Annual growth |  | %/year |  |  |  |  |
| A-04 | Retention and deletion lag |  | days |  |  |  |  |
| A-05 | Copies and overhead |  | count / % |  |  |  |  |
| A-06 | Target utilisation |  | fraction |  |  |  |  |
| A-07 | Provisioning lead time |  | days/weeks |  |  |  |  |

### 16.3 Capacity-estimation worksheet

For each resource, record:

| Resource | Current demand | Peak/scenario demand | Usable capacity | Target margin | Failure-state capacity | Evidence / gap |
|---|---:|---:|---:|---:|---:|---|
| CPU |  |  |  |  |  |  |
| Memory |  |  |  |  |  |  |
| Storage |  |  |  |  |  |  |
| Network |  |  |  |  |  |  |
| IOPS |  |  |  |  |  |  |
| Connections / slots |  |  |  |  |  |  |
| Quotas / processing window |  |  |  |  |  |  |

Use a separate row or worksheet per unit and scenario. “Target margin” must state the denominator and method; do not mix headroom relative to demand with headroom relative to provisioned capacity.

### 16.4 Scenario and sensitivity table

| Input | Low | Expected | High | Sensitivity method | Result / ranking |
|---|---:|---:|---:|---|---|
| Annual growth |  |  |  | One-at-a-time |  |
| Peak factor |  |  |  | One-at-a-time |  |
| Record size |  |  |  | One-at-a-time |  |
| Retention |  |  |  | One-at-a-time |  |
| Copies / overhead |  |  |  | One-at-a-time |  |
| CPU-seconds/event |  |  |  | One-at-a-time |  |

### 16.5 Capacity trigger register

| Metric | Threshold and duration | Forecast horizon | Lead time | Owner | Action | Escalation |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

### 16.6 Architecture decision record (ADR) outline

Create an ADR when a material capacity choice has meaningful cost, reliability, or operational consequences.

- **Title / status / date**
- **Context:** workload, service objectives, growth horizon, constraints.
- **Decision drivers:** peak demand, failure requirements, lead time, elasticity, scheduling flexibility.
- **Options considered:** permanently provisioned, elastic, scheduled, isolated, or hybrid capacity.
- **Evidence:** measured demand, benchmark results, forecast scenarios, uncertainty, failure arithmetic.
- **Decision:** selected approach and scope.
- **Consequences:** benefits, risks, costs deferred to the dedicated cost lesson, operational ownership.
- **Revisit triggers:** measurable conditions and review date.

Do not create an ADR for every arithmetic exercise; use it when a decision needs a durable rationale and later review.

## 17. Mastery criteria and completion gate

### 17.1 Mastery criteria

You are ready to move on when you can independently:

- Convert a workload description into daily bytes, average rate, peak rate, and retained storage with correct units.
- Explain the assumptions and limitations of each estimate.
- Forecast at least three years using appropriate growth models and low/expected/high scenarios.
- Rank important sensitivities and explain the business or technical drivers behind them.
- Calculate target capacity and headroom with an explicit denominator.
- Prove N+1 capacity by calculating the load and capacity remaining after the failure.
- Explain how backfill, batch, and interactive workloads overlap at each bottleneck.
- Define actionable re-planning triggers that account for provisioning lead time.
- Compare a forecast with actuals and use test evidence to revise assumptions.
- Distinguish measured facts, estimates, assumptions, and unresolved questions.

### 17.2 Completion checklist

- [ ] Workload profile completed with evidence and measurement gaps.
- [ ] Assumptions register completed; illustrative values are clearly distinguished from observed data.
- [ ] Capacity-estimation worksheet covers all relevant resources.
- [ ] Low/expected/high growth scenarios calculated for at least three years.
- [ ] Sensitivity analysis completed and ranked.
- [ ] Headroom and N+1 calculations independently recomputed.
- [ ] Backfill/recovery overlap assessed.
- [ ] Measurable capacity triggers include owner, action, and lead time.
- [ ] Python calculations and assertions run successfully in the learner's environment.
- [ ] Forecast validation plan includes actual-versus-forecast error and performance-test evidence.
- [ ] Remaining uncertainty and exclusions documented.
- [ ] Practice-question gaps logged.

**Completion gate:** the worksheet, scenario table, and sensitivity ranking must be reproducible; every material number must have a unit and a source or explicit assumption; and the plan must state what it cannot establish. If any item fails, revise the model before proceeding.

## 18. Summary and transition to Topic 02

Capacity planning starts with a measurable workload, translates demand into resource requirements, adds peak and failure-state considerations, and forecasts future demand with explicit uncertainty. The central discipline is not to produce one impressive number; it is to make assumptions visible, calculate consistently, identify constraints, and revise the model as evidence changes.

Remember:
- Average load is not peak load.
- Logical data is not necessarily physical storage.
- Capacity is constrained by the scarcest relevant resource.
- Headroom and N+1 must be calculated, not merely asserted.
- Forecasts are uncertain and must be compared with actual measurements.
- Provisioning lead time and workload overlap can matter as much as total demand.

**Readiness transition:** Topic 02, `02-throughput-latency-concurrency-and-queueing.md`, examines how demand and utilisation affect throughput, latency, concurrency, and queueing. Bring forward your workload profile, peak assumptions, and service objectives; do not infer latency behaviour from capacity arithmetic alone.
