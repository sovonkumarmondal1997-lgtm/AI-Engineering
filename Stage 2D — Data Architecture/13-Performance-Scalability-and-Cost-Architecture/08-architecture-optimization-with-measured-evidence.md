# Architecture Optimization with Measured Evidence

## 1. Purpose, scope, and learning outcomes

### Purpose

This lesson teaches a disciplined way to decide which data-architecture changes are worth making and to verify what they actually achieve. It integrates capacity planning, queueing and latency, query performance, scaling and data distribution, caching and materialisation, cost modelling, and performance testing.

The core workflow is:

**baseline → diagnose → prioritise → hypothesise → change → measure → decide → document**

Optimisation without evidence is guessing. The goal is not to produce the most sophisticated design or the largest benchmark number. It is to meet explicit workload and business objectives with an acceptable combination of performance, capacity, cost, freshness, reliability, and operational complexity.

### Scope

This is an evidence and decision-making lesson, not a replacement for the dedicated lessons on capacity formulas, query plans, partitioning, cache semantics, cost modelling, or load testing. Reuse those topic-specific methods and artefacts rather than duplicating their full implementation detail here.

All numerical datasets and prices in this lesson are **illustrative**. They are not production measurements, vendor benchmarks, or evidence of actual savings. A worked example demonstrates how to reason; it does not establish what a real system will do.

### Learning outcomes

After completing this lesson, you should be able to:

1. Establish a reproducible baseline with explicit workload, environment, units, and measurement windows.
2. Separate measured facts, assumptions, estimates, hypotheses, recommendations, and verified outcomes.
3. Diagnose bottlenecks by impact rather than by whichever metric looks worst.
4. Form falsifiable optimisation hypotheses and define success criteria before changing a system.
5. Design controlled, repeatable before-and-after experiments and recognise confounding variables.
6. Quantify latency, throughput, cost-per-unit, capacity headroom, and trade-offs.
7. Apply Amdahl-style reasoning while recognising its assumptions and limits.
8. Detect regression, bottleneck migration, diminishing returns, and workload-specific effects.
9. Update capacity and cost models using measured outcomes without overgeneralising.
10. Produce an optimisation review, evidence register, decision record, rollback plan, and follow-up measurements.

### Central rule

A claim must not be stronger than its evidence. “The change is expected to reduce scan volume” is a hypothesis or estimate. “Scan volume fell in three controlled runs” is a measured result. “The change improved production performance” requires relevant production evidence or must remain qualified.

---

## 2. Prerequisites and dependencies on Topics 01–07

The module roadmap lists Topic 08 prerequisites as **Sequence 5–7 (and earlier topics)**. The complete sequence is an integrated dependency: each earlier topic supplies a method or input that this lesson uses.

| Topic | Evidence or artefact to reuse | How Topic 08 uses it |
|---|---|---|
| 01 — Capacity planning and growth forecasting | Workload profile, peak and growth scenarios, capacity estimate, assumptions register | Establishes the demand envelope and identifies assumptions that optimisation might invalidate |
| 02 — Throughput, latency, concurrency and queueing | Latency percentiles, arrival rate, concurrency, queue/backlog analysis | Separates response-time symptoms from saturation and queueing causes |
| 03 — Query performance and data locality | Query ranking, scan volume, pruning, joins, shuffle/data movement, query-plan evidence | Identifies expensive operations and estimates the maximum impact of query-level changes |
| 04 — Scaling, partitioning, sharding and hotspots | Skew measurements, distribution comparison, partitioning strategy, resharding risks | Evaluates whether a proposed distribution change addresses the measured bottleneck |
| 05 — Caching, materialisation and serving trade-offs | Serving decision matrix, hit/miss metrics, freshness policy, refresh economics | Tests whether reuse or precomputation is justified and whether it creates staleness or failure risk |
| 06 — Cost modelling, unit economics and FinOps | Cost-driver inventory, unit cost, scenario model, allocation assumptions | Compares expected and measured cost on a consistent basis |
| 07 — Performance testing and capacity validation | Test plan, baseline, workload model, acceptance criteria, capacity validation | Provides the repeatable method for verifying changes |

### Before starting

Have these items available, or explicitly mark them as missing:

- the workload and business objective being optimised;
- the current baseline and its provenance;
- a measurable acceptance criterion;
- the main constraints (freshness, correctness, reliability, security, budget);
- candidate measurements that can confirm or refute the bottleneck hypothesis;
- the cost and operational implications of each candidate;
- a safe test and rollback approach.

If the baseline does not exist, the first deliverable is a measurement plan—not an architecture rewrite.

---

## 3. Beginner foundations: what evidence-based optimisation means

### 3.1 Symptoms are not causes

Suppose a dashboard has a p95 latency of 4 seconds. That is a **symptom**: it describes what users experienced under a defined workload and measurement window. It does not by itself establish why the dashboard is slow.

Possible causes include:

- an expensive scan or join;
- queueing at a saturated compute pool;
- a hot partition or key;
- a low cache hit ratio;
- a remote data read or network bottleneck;
- a downstream dependency;
- an overloaded test client;
- an instrumentation or sampling artefact.

A credible diagnosis gathers evidence that discriminates between explanations. Adding compute might help a compute-bound stage but do little for serial work, poor data locality, a lock, or a throttled dependency.

### 3.2 Six evidence labels

Use these labels throughout notebooks, reports, discussions, and architecture decision records (ADRs).

| Label | Meaning | Example |
|---|---|---|
| **Fact (measured)** | Directly observed and recorded with source, units, and conditions | “In run 7, p95 was 3.2 s at 800 requests/s.” |
| **Assumption** | Accepted provisionally but not verified | “Peak traffic next quarter will be 30% higher.” |
| **Estimate** | Calculated from facts and/or assumptions | “At the forecast peak, 12 worker units may be required.” |
| **Hypothesis** | A testable explanation or prediction not yet established | “Partition skew causes the long-tail task duration.” |
| **Recommendation** | A proposed action based on current evidence and trade-offs | “Test a different partition key in a controlled replay.” |
| **Verified outcome** | A result measured after a defined intervention and evaluated against the baseline | “Across five paired runs, p95 fell by 18% while error rate and cost stayed within limits.” |

A recommendation can be well justified without being a verified outcome. An estimate can be useful without being a fact. Keep the labels visible when evidence is reused in a later decision.

### 3.3 Why establish a baseline first?

A baseline answers: **what happens now, for which workload, under which conditions?** Without it, there is no reliable comparison.

A useful baseline includes:

- workload shape: arrival rate, concurrency, read/write mix, key/query distribution, data size;
- outputs: throughput, latency percentiles, error rate, backlog, freshness;
- resource signals: CPU, memory, storage I/O, network, queue depth, spill, throttling;
- cost: compute, storage, data transfer, refresh, and cost per relevant unit;
- environment: software version, configuration, instance shape, cache state, region or network path, background work;
- measurement details: start/end times, warm-up, steady-state interval, sample count, exclusions, and instrumentation;
- known limitations and confidence.

A number without a unit, time window, workload, or source is not a reproducible baseline.

### 3.4 The optimisation loop

1. Define the business objective and hard constraints.
2. Measure the baseline under a representative workload.
3. Identify symptoms and rank plausible bottlenecks by impact.
4. Form a falsifiable hypothesis.
5. Select one meaningful intervention where feasible.
6. Predefine the test, metrics, guardrails, and rollback conditions.
7. Run a controlled comparison and record raw evidence.
8. Evaluate effect size, variability, side effects, and cost.
9. Keep, revise, or revert the change.
10. Update capacity/cost forecasts and document remaining uncertainty.

This loop is iterative. Fixing one bottleneck often exposes another. A successful experiment can justify a staged rollout; it does not automatically justify a broad architectural migration.

---

## 4. Baseline-to-optimisation workflow

### Step 1 — Define the objective and constraints

Translate a vague request such as “make the pipeline faster” into measurable objectives. Examples:

- dashboard p95 latency at or below a specified threshold at a specified peak workload;
- batch completion before a deadline for a stated fraction of days;
- error rate below a specified threshold;
- freshness lag within a defined limit;
- cost per successful workload below a budget;
- required recovery and availability maintained.

Separate **hard constraints** from preferences. Data correctness, access control, retention, and contractual service-level objectives may be hard gates. A candidate that violates one should not win because it is faster or cheaper.

### Step 2 — Build the baseline record

Record a stable workload identifier and test version. Capture raw results, not only a summary table. Note whether the baseline is a production observation, staging test, synthetic simulation, or estimate.

Where possible, collect multiple comparable runs. If production data cannot be used, construct representative synthetic data and state which production characteristics it does not represent.

### Step 3 — Diagnose and rank bottlenecks

Use a causal chain rather than a list of metrics:

- **Symptom:** what violated an objective?
- **Evidence:** what measurements were observed?
- **Candidate cause:** what mechanism could produce those observations?
- **Discriminating test:** what result would support or refute that cause?
- **Impact estimate:** if confirmed, how much of the total outcome can it affect?
- **Risk:** what other outcomes could change?

Rank by expected impact, evidence confidence, implementation cost, reversibility, and risk. Amdahl-style reasoning can bound the upside of improving a component, but does not replace measurement.

### Step 4 — Form a falsifiable hypothesis

A strong hypothesis states a proposed mechanism, a predicted effect, and conditions.

**Weak:** “More workers should improve performance.”

**Stronger:** “At the current 900 requests/s workload, the transform stage consumes 55% of end-to-end processing time and its worker pool is CPU-saturated. Increasing workers from 8 to 12 should reduce stage duration, provided input throughput and downstream capacity remain unchanged. We will accept the change only if p95 end-to-end latency improves by at least 10%, error rate does not rise, and cost per successful request rises by no more than 5%.”

The thresholds above are illustrative. Set them from the actual service objective and business constraints before the experiment.

A hypothesis is useful when an outcome could prove it wrong. “The change will help somehow” is not falsifiable.

### Step 5 — Select the experiment

Where feasible, change one meaningful variable at a time. This improves attribution, but it is not an absolute rule: some changes require a coordinated bundle or have interaction effects. If several changes must be combined, state that the experiment estimates the bundle's effect rather than each component's separate effect.

Choose an appropriate comparison:

- **Paired runs:** run baseline and candidate under similar conditions, alternating order when practical.
- **A/B or control group:** compare comparable traffic or data partitions, with clear assignment and spillover checks.
- **Replay:** replay a recorded or synthetic workload against isolated environments.
- **Canary:** expose a small, controlled portion of real traffic to the candidate.
- **Factorial/interaction experiment:** deliberately vary multiple factors when interactions are central to the question.

Never allow an experiment to create uncontrolled risk for a production workload. Define safety limits, abort conditions, and rollback before execution.

### Step 6 — Execute consistently

Keep these conditions stable or record their differences:

- input data snapshot, row counts, data skew, and data freshness;
- request rate, concurrency, query mix, key popularity, and burst shape;
- environment and resource configuration;
- software version, plan, feature flags, and dependencies;
- cache warm/cold state and materialised-view freshness;
- background jobs, compaction, checkpointing, and other shared activity;
- measurement tools and sampling configuration.

Use a warm-up period where the system has startup, JIT, cache, autoscaling, or connection-pool effects. Measure steady state separately. Include cold-start tests if cold start is a real user or recovery condition; do not mix cold and warm results without labelling them.

### Step 7 — Compare results and guardrails

Compare like with like. Report:

- absolute change and relative change;
- run-to-run variability and sample size;
- latency percentiles, not only averages;
- throughput and errors;
- resource utilisation, queue depth, backlog, and saturation;
- freshness/correctness outcomes;
- cost per unit and total cost over a consistent period;
- regressions in other workloads or components.

A change that improves p95 but doubles cost or violates freshness is not automatically a win. A change with a small performance gain may still be valuable if it materially improves reliability or lowers unit cost—but the value and trade-off must be explicit.

### Step 8 — Decide and document

Choose one of the following:

- **Keep / staged rollout:** evidence meets the predefined criteria and guardrails.
- **Revert:** criteria fail or risk is unacceptable.
- **Iterate:** result is promising but incomplete, noisy, or exposes a new bottleneck.
- **Stop:** the objective is met, or the expected next gain is not worth the cost/risk.
- **Investigate:** the experiment is invalid or cannot discriminate among hypotheses.

Update the capacity and cost models using measured outcomes and stated limitations. Preserve the baseline so future changes can be compared against a known reference.

---

## 5. Measurement concepts and decision criteria

### 5.1 Metric definitions

Every metric needs a definition, unit, window, source, and aggregation method.

| Metric | Definition | Common unit | What to record |
|---|---|---|---|
| Throughput | Completed work per unit time | requests/s, rows/s, TB/h | Successful versus attempted work; time window |
| Latency | Time from a defined start event to a defined completion event | ms or s | p50, p90, p95, p99; sample count; exclusions |
| Error rate | Failed eligible operations divided by eligible operations | % | Which statuses/timeouts count; retry treatment |
| Utilisation | Busy or consumed resource relative to available capacity | % or resource units | Averaging window and throttling/queue context |
| Queue depth/backlog | Work waiting or accumulated but not completed | items, bytes, seconds of work | Sampling interval, arrival and completion rates |
| Freshness lag | Delay between source state/time and served state/time | seconds/minutes | Lag origin, watermark, percentile, max |
| Cost per unit | Attributed cost divided by a defined unit of successful work | currency/query, currency/million events | Cost period, denominator, failed/retried work |
| Capacity headroom | Difference between validated sustainable capacity and expected demand | requests/s or % | Workload shape, SLO boundary, safety margin |
| Data movement | Bytes scanned, shuffled, transferred, or fetched remotely | MB/GB/TB | Definition of bytes and query/workload scope |

Do not compare metrics whose definitions changed between runs. For example, a throughput increase caused by counting failed requests as completions is not a valid performance gain.

### 5.2 Relative changes

For a metric where lower is better (e.g. latency or cost per successful request):

\[
\text{relative reduction} = \frac{\text{baseline} - \text{candidate}}{\text{baseline}}\times100\%
\]

For a metric where higher is better (e.g. throughput):

\[
\text{relative increase} = \frac{\text{candidate} - \text{baseline}}{\text{baseline}}\times100\%
\]

The formulas require a meaningful nonzero baseline and comparable measurement units/windows. If the baseline is zero, report the absolute change or use a metric-specific alternative; do not divide by zero.

### 5.3 Percentiles and tail latency

The p95 latency is the value at or below which approximately 95% of observations fall under the chosen percentile convention. It is not the average latency of the slowest 5%, and it is not a guarantee that every request completes within that time.

Always report sample count and the calculation method. Percentiles from small samples can be unstable. Do not average p95 values from separate runs to obtain a defensible combined p95; combine raw observations where possible, or use a method appropriate to the available histograms.

A change can improve the mean while worsening p99 if it improves common requests but creates rare stalls, retries, or queueing. Examine the distribution and user-relevant thresholds.

### 5.4 Statistical and practical significance

Two concepts matter:

- **Statistical evidence:** how compatible the observed difference is with random variation under a stated analysis and assumptions.
- **Practical significance:** whether the size of the difference matters to the objective, user experience, cost, or risk.

A tiny difference can appear statistically detectable with a huge sample yet be irrelevant. A material improvement can be uncertain when sample sizes are small or variability is high. Do not infer significance merely because one run is better than another.

A pragmatic process:

1. Collect repeated runs or request-level observations under a stable design.
2. Examine distributions, outliers, autocorrelation, and run-level effects.
3. Report effect size and uncertainty (for example, a confidence interval or a range across paired runs).
4. Compare the plausible effect with a predeclared practical threshold.
5. Avoid multiple unplanned comparisons and selective reporting.
6. If the evidence is inconclusive, collect more data or redesign the experiment rather than declaring success.

For production systems, observations may be correlated in time, and individual requests are not always independent. A simple independent-sample test can understate uncertainty when traffic, hosts, or time periods are clustered. Use a design and statistical method suited to the actual data.

### 5.5 Baseline record template

```text
Workload / service ID:
Business objective:
Hard constraints:
Baseline version / date:
Evidence source: production observation / test / simulation / estimate
Environment and configuration:
Data snapshot, volume, skew, freshness:
Arrival rate, concurrency, read/write mix:
Key/query distribution and burst profile:
Warm-up period:
Steady-state measurement window:
Run count and sample count:
Throughput definition and observed value:
Latency p50 / p95 / p99:
Error rate and definition:
CPU / memory / I/O / network / queue / backlog:
Freshness and correctness results:
Cost period and unit economics:
Known confounders:
Evidence limitations:
Owner / reviewer:
```

---

## 6. Amdahl-style reasoning and impact prioritisation

### 6.1 Formula and worked example

Amdahl-style reasoning estimates the maximum overall speedup when only part of a workload improves.

Let:

- \(p\) = fraction of total elapsed time spent in the component being improved;
- \(s\) = speedup factor for that component;
- the remaining fraction \(1-p\) be unchanged.

Then:

\[
\text{overall speedup}=\frac{1}{(1-p)+p/s}
\]

**Illustrative example A:** a component accounts for 40% of elapsed time (\(p=0.40\)) and is made 10 times faster (\(s=10\)).

\[
\frac{1}{0.60+0.40/10}=\frac{1}{0.64}=1.5625\times
\]

The overall elapsed time becomes 64% of baseline, a 36% reduction. The component's large speedup does not translate to a 10× end-to-end speedup.

**Illustrative example B:** a component accounts for 10% of elapsed time and becomes 100 times faster.

\[
\frac{1}{0.90+0.10/100}=\frac{1}{0.901}\approx1.1099\times
\]

The overall speedup is only about 1.11×. This is why optimising a small part of the total often has limited impact.

### 6.2 Assumptions and limitations

The simple formula assumes the workload and the other components remain unchanged, component times can be represented as fractions of the same total, and the intervention changes only the target component. Real distributed data systems can violate these assumptions because of parallelism, contention, queueing, shared-resource interference, changed data movement, cache effects, or a bottleneck that migrates.

Use Amdahl-style reasoning as a **prioritisation bound**, not as proof of the expected result. Verify the actual end-to-end outcome.

### 6.3 Prioritisation matrix

| Candidate | Baseline evidence | Amdahl/impact estimate | Expected benefit range | Implementation cost | Runtime cost change | Risk/reversibility | Confidence |
|---|---|---|---|---|---|---|---|
| Query pruning/index/layout | Query plan, bytes scanned, stage timing | Share of workload affected | Estimate with assumptions | Low/medium/high | Estimate | Reversible? | Evidence-based |
| Change partition key | Per-partition load/skew, shuffle, tail task time | Share of slow workload caused by skew | Estimate with assumptions | Usually non-trivial | Compute/storage/migration | Migration risk | Evidence-based |
| Cache/materialise repeated result | Reuse, miss cost, freshness requirement | Avoidable repeated work | Estimate with assumptions | Build/operate/refresh | Memory/storage/refresh | Staleness risk | Evidence-based |
| Add compute capacity | Saturation, queueing, scaling curve | Portion constrained by resource | Measure or estimate | Provisioning/engineering | Usually changes spend | May mask inefficiency | Evidence-based |
| Re-platform | End-to-end profile and requirements | Must cover a real limiting factor | High uncertainty until tested | High | Uncertain | High migration risk | Usually low without prototype |

Rank options by expected impact, evidence strength, cost, risk, time to validate, and reversibility. A dramatic redesign is not inherently better than a small, well-supported change.

---

## 7. Worked examples with illustrative performance and cost data

All values in this section are synthetic teaching data.

### 7.1 Before-and-after latency and cost

Suppose a batch service has the following baseline and candidate measurements under the same synthetic workload and environment.

| Metric | Baseline | Candidate | Definition |
|---|---:|---:|---|
| Eligible operations attempted | 1,002 | 1,002 | Includes successful and failed attempts |
| Completed successful jobs | 1,000 | 1,000 | Same logical batch; 2 failed attempts per run |
| p50 latency | 1.8 s | 1.6 s | End-to-end request latency; same percentile convention |
| p95 latency | 4.0 s | 3.2 s | Same percentile convention |
| p99 latency | 7.0 s | 6.8 s | Same percentile convention |
| Error rate | 0.20% | 0.20% | 2 failed / 1,002 eligible operations = 0.1996%, rounded to 0.20% |
| Compute cost per run | \$50 | \$56 | Same accounting window |
| Cost per successful job | \$0.050 | \$0.056 | Run cost / successful jobs |

Calculations:

- p95 reduction = \((4.0-3.2)/4.0 = 20\%\).
- p99 reduction = \((7.0-6.8)/7.0 \approx 2.86\%\).
- cost per successful job increase = \((0.056-0.050)/0.050 = 12\%\).

Interpretation: the candidate shows a 20% p95 reduction in this illustrative table, but the p99 change is much smaller and the unit cost is 12% higher. Whether it is acceptable depends on the predeclared SLO and cost guardrail. This table alone does not establish statistical confidence because run counts, sample counts, and variability are not provided. It also does not prove a production improvement.

### 7.2 Capacity headroom

Suppose a repeatable test finds that the service meets its SLO up to 1,200 successful requests/s under the tested workload. The expected peak is 900 requests/s.

A simple headroom fraction relative to validated capacity is:

\[
H = \frac{C-D}{C} = \frac{1200-900}{1200}=0.25=25\%
\]

Demand uses 75% of this tested SLO-compliant capacity. Another convention expresses spare capacity relative to demand:

\[
H_D = \frac{C-D}{D}=\frac{300}{900}=33.3\%
\]

Both are valid if named clearly; they have different denominators. Do not report “25% headroom” without saying which definition is used. The result applies only to the tested workload shape, environment, data size, and acceptance criteria. It is not universal capacity.

### 7.3 Bottleneck migration

Illustrative end-to-end processing time is 100 seconds:

| Stage | Baseline time | Share |
|---|---:|---:|
| Read/input | 20 s | 20% |
| Transform | 50 s | 50% |
| Shuffle/join | 20 s | 20% |
| Publish/output | 10 s | 10% |
| **Total** | **100 s** | **100%** |

A 4× speedup of the transform stage gives an Amdahl estimate:

\[
T' = 20 + 50/4 + 20 + 10 = 62.5\text{ s}
\]

Overall speedup = \(100/62.5 = 1.6\times\), or 37.5% less elapsed time. After this change, the transform stage is 12.5 seconds, while input is 20 seconds and shuffle/join is 20 seconds. The original bottleneck is no longer uniquely dominant. The next investigation should use new measurements, not continue optimising transform by habit.

### 7.4 Payback and net benefit

Suppose a proposed change has an illustrative one-time engineering and migration cost of \$18,000. If measured and attributable steady-state savings were later established at \$3,000/month, simple payback would be:

\[
\text{payback}=\frac{\$18{,}000}{\$3{,}000/\text{month}}=6\text{ months}
\]

This is only a model. It assumes the saving is net, sustained, attributable, and measured on a consistent cost basis. If the \$3,000 is an estimate rather than measured savings, payback remains an estimate. Include ongoing maintenance, migration risk, opportunity cost, and any increased serving or storage cost before calling it net benefit.

### 7.5 Freshness and reliability guardrails

Suppose a materialisation optimisation reduces dashboard p95 from 3.5 seconds to 1.8 seconds, but refresh lag increases from 4 minutes to 14 minutes. If the accepted freshness limit is 10 minutes, the candidate fails the hard constraint even though latency improves.

This example illustrates multi-objective evaluation: performance is not the only success criterion. A faster stale answer can be the wrong answer.

---

## 8. Intermediate experiment design and trade-off analysis

### 8.1 Experiment plan

Before running an experiment, write down:

| Field | Example |
|---|---|
| Objective | Meet p95 ≤ 2.5 s at 800 requests/s |
| Baseline | Version A, five runs, 10-minute steady-state window each |
| Hypothesis | Reducing unnecessary scan bytes lowers query latency |
| Intervention | Enable partition pruning only; no other changes |
| Control | Version A under the same input snapshot and workload |
| Workload | Fixed query mix, key distribution, data volume, and burst pattern |
| Primary metric | p95 end-to-end latency |
| Guardrails | Error rate, p99, freshness, correctness, cost per successful query |
| Practical threshold | At least 10% p95 reduction, if preapproved by the service owner |
| Measurement | Same instrumentation, same percentile convention, raw samples retained |
| Safety / abort | Stop if errors exceed the predeclared threshold or source saturation risks shared workloads |
| Decision rule | Keep only if the primary threshold and every hard guardrail pass |
| Rollback | Disable feature / revert plan; verify baseline behaviour |
| Limitations | Test environment differs from production in listed ways |

The values are illustrative. The objective and thresholds must be set from the real service contract and risk appetite.

### 8.2 Control the confounders

A **confounder** changes alongside the intervention and can explain some or all of the observed difference. Common examples:

- different data volume or skew;
- different query mix or request arrival pattern;
- a warm cache in one run and a cold cache in another;
- different software version, statistics, query plan, or configuration;
- a background compaction, checkpoint, or batch job;
- autoscaling or throttling differences;
- a test client that saturates before the service;
- time-of-day effects or shared noisy neighbours.

Control a confounder where practical. Otherwise record it, assess likely direction and magnitude, and reduce the strength of the conclusion. If baseline and candidate differ in several uncontrolled ways, say the comparison is inconclusive.

### 8.3 One variable at a time—and when not to

Changing one meaningful variable at a time makes attribution easier. It can be inefficient when effects interact—for example, partitioning and worker count may only work well together. In such cases:

1. State the interaction hypothesis.
2. Design a factorial, staged, or bundle experiment.
3. Include a baseline and enough combinations to distinguish the effect.
4. Do not attribute the whole bundle's benefit to one component unless the design supports that claim.

A test that changes three settings simultaneously can show that the combined configuration worked under the test conditions; it cannot reveal which setting caused the change.

### 8.4 Performance, cost, freshness, reliability, complexity

Use a trade-off table that makes losses visible.

| Candidate | Performance | Cost | Freshness/correctness | Reliability | Complexity / reversibility |
|---|---|---|---|---|---|
| Add compute | May improve resource-bound stages | Usually higher while provisioned | Often neutral, but not guaranteed | May add headroom; shared dependency remains | Usually reversible, but can mask inefficient work |
| Improve query/data locality | May reduce scan/shuffle | May lower compute or transfer | Must preserve query semantics | Usually neutral; plan changes can introduce regressions | Often reversible; requires plan evidence |
| Cache repeated result | Can reduce repeated read/compute | Adds memory/network and invalidation cost | Staleness and key correctness are critical | Cache outage can overload backing store | Moderate complexity |
| Materialise aggregate | Reduces repeated expensive work | Adds refresh/storage cost | Refresh lag and snapshot alignment matter | Refresh failure can leave stale output | Moderate to high complexity |
| Repartition/re-shard | Can reduce skew or improve locality | Migration and ongoing resource cost | Must preserve ordering/joins/semantics | Migration can create operational risk | Higher complexity, potentially difficult rollback |
| Re-platform | Potentially broad benefits, uncertain until tested | Migration plus new run cost | Semantics and migration parity must be proven | New failure modes and cutover risks | High cost and low reversibility |

No row is universally superior. Select against the workload and hard constraints, not a generic best-practice slogan.

### 8.5 Regression guards

A change can improve one workload and harm another. Maintain a representative regression suite containing:

- critical query patterns and representative parameter values;
- small, median, and large data volumes;
- normal and skewed distributions;
- cache warm and cold cases where relevant;
- peak concurrency and realistic burst patterns;
- freshness, correctness, and access-control checks;
- cost and resource-consumption checks.

Define thresholds before interpreting the results. Keep raw test data and versioned configuration so a later release can reproduce the comparison.

---

## 9. Advanced cases: multi-workload systems, interactions, and diminishing returns

### 9.1 Shared-resource contention

In a data platform, optimising one pipeline may increase pressure on a shared resource used by other workloads. Examples:

- a faster refresh job competes with interactive queries for compute;
- a cache warming job saturates network bandwidth before peak traffic;
- a larger shuffle spills into a shared storage layer;
- an index improves one query but increases write amplification and ingestion latency;
- a new materialisation reduces read compute but adds refresh load during the same window as batch processing.

Measure per-workload and shared-resource effects. A single aggregate CPU number may hide one queue or tenant being starved. Record workload identity, concurrency, scheduling priority, and fairness where relevant.

### 9.2 Interacting bottlenecks

Suppose the original pipeline is limited by CPU. After adding workers, CPU utilisation falls, but network saturation and remote reads increase. The next limiting factor is not necessarily a failure of the first change; it may be a bottleneck that was hidden by the previous limit.

After each significant intervention:

1. Re-profile end-to-end stage timings.
2. Recheck queues, resource saturation, and data movement.
3. Recompute the component shares used in Amdahl-style reasoning.
4. Verify that the bottleneck is not in the test harness or a downstream dependency.
5. Decide whether the new limit matters to the business objective before optimising it.

### 9.3 Diminishing returns and stopping rules

Optimisation has diminishing returns when additional effort produces progressively smaller benefits or when another component dominates. Define a stopping rule before an endless tuning cycle begins.

Possible rules:

- all hard SLO and correctness requirements pass with agreed headroom;
- the expected benefit of the next candidate is below a minimum practical threshold;
- the expected payback exceeds the approved period;
- residual risk is acceptable and further improvement would create disproportionate complexity;
- evidence is too weak to justify a structural change, so the next step is measurement rather than implementation.

A system need not be maximally optimised. It needs to meet its requirements with a defensible margin and an operationally supportable design.

### 9.4 Updating growth and capacity forecasts

Use measured throughput and saturation results to update Topic 01 forecasts, but avoid extrapolating beyond the validated workload envelope.

Record:

- the tested SLO-compliant capacity and workload shape;
- the demand level where latency, errors, or backlog breached criteria;
- observed resource scaling and any non-linear knee;
- headroom definition and growth scenarios;
- what changes when data volume, skew, query mix, or concurrency changes;
- the next revalidation trigger.

A measured capacity at today's data volume is not proof of the same capacity at twice the data volume. Use a growth model and retest critical points.

### 9.5 Updating cost models

For each intervention, compare costs over the same period and workload:

\[
\text{cost per successful unit} =
\frac{\text{attributed total cost in period}}{\text{successful units in period}}
\]

Define the unit carefully: successful query, completed batch, million deduplicated events, or another business-relevant outcome. State how failed, retried, and duplicate work is treated.

Update:
- compute and memory allocation;
- storage, replication, and retention;
- network/data transfer;
- refresh, orchestration, and observability;
- engineering and operational costs where relevant;
- denominator volume and successful completion count.

Do not report a cost reduction just because one resource's bill decreased. A change may move cost to another service, increase retries, or reduce throughput. Reconcile the total and disclose excluded costs.

### 9.6 Canary, rollout, and rollback

A controlled test environment may not represent production. For changes that can be rolled out safely, use staged exposure:

1. validate in an isolated test;
2. deploy to a limited canary or workload slice;
3. compare candidate and control under comparable traffic;
4. monitor primary metrics and hard guardrails;
5. expand only if criteria pass;
6. stop or roll back if a threshold is breached;
7. continue observation long enough to detect delayed effects such as cache churn, storage growth, or periodic batch overlap.

Define rollback criteria before release. A rollback itself may change cache state, query plans, data layout, or in-flight work, so validate recovery as well as the forward path.

### 9.7 Confidence and communication

Use calibrated wording:

- **High confidence:** repeated comparable measurements, strong instrumentation, low material confounding, effect exceeds variability and practical threshold.
- **Moderate confidence:** direction is consistent but sample size, environment match, or one confounder limits inference.
- **Low confidence:** few runs, synthetic workload mismatch, unstable environment, or multiple changes prevent attribution.

These are qualitative categories; define a local rubric if teams need consistent scoring. Do not convert a qualitative confidence label into a probability unless the method supports it.

A decision summary should include what was measured, under which conditions, what changed, what did not change, the effect size and uncertainty, the guardrails, the limitations, and the next action.

---

## 10. Python examples with reproducible assertions

These examples use the Python standard library and deterministic synthetic data. They demonstrate arithmetic and experiment reasoning; they are not performance benchmarks and do not simulate a distributed data platform.

### 10.1 Compare baseline and candidate metrics

```python
import math


def _finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def relative_reduction(baseline: float, candidate: float) -> float:
    if not _finite_number(baseline) or baseline <= 0:
        raise ValueError("baseline must be a finite positive number")
    if not _finite_number(candidate) or candidate < 0:
        raise ValueError("candidate must be a finite non-negative number")
    return (baseline - candidate) / baseline


def relative_increase(baseline: float, candidate: float) -> float:
    if not _finite_number(baseline) or baseline <= 0:
        raise ValueError("baseline must be a finite positive number")
    if not _finite_number(candidate) or candidate < 0:
        raise ValueError("candidate must be a finite non-negative number")
    return (candidate - baseline) / baseline


p95_reduction = relative_reduction(4.0, 3.2)
p99_reduction = relative_reduction(7.0, 6.8)
unit_cost_increase = relative_increase(0.050, 0.056)

assert abs(p95_reduction - 0.20) < 1e-12
assert abs(p99_reduction - (0.2 / 7.0)) < 1e-12
assert abs(unit_cost_increase - 0.12) < 1e-12
for invalid in (float("nan"), float("inf"), -1, True, "4.0"):
    try:
        relative_reduction(4.0, invalid)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid candidate accepted: {invalid!r}")

print({
    "p95_reduction_pct": p95_reduction * 100,
    "p99_reduction_pct": p99_reduction * 100,
    "unit_cost_increase_pct": unit_cost_increase * 100,
})
```

Expected values: p95 reduction = 20%; p99 reduction ≈ 2.857%; unit-cost increase = 12%. These reproduce the illustrative table in Section 7.1.

### 10.2 Amdahl-style overall speedup

```python
import math


def _finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def amdahl_speedup(component_fraction: float, component_speedup: float) -> float:
    if not _finite_number(component_fraction) or not 0 <= component_fraction <= 1:
        raise ValueError("component fraction must be finite and between 0 and 1")
    if not _finite_number(component_speedup) or component_speedup <= 0:
        raise ValueError("component speedup must be finite and positive")
    return 1.0 / ((1.0 - component_fraction) + component_fraction / component_speedup)


case_a = amdahl_speedup(0.40, 10)
case_b = amdahl_speedup(0.10, 100)

assert abs(case_a - 1.5625) < 1e-12
assert abs(case_b - (1 / 0.901)) < 1e-12
assert case_a < 10  # A component's speedup is not the end-to-end speedup.
for fraction, speedup in ((float("nan"), 2), (0.5, float("inf")), (True, 2), (0.5, 0)):
    try:
        amdahl_speedup(fraction, speedup)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid Amdahl input accepted")

print({"case_a_speedup": case_a, "case_b_speedup": case_b})
```

Expected values: 1.5625× and approximately 1.10988×. The assertion reinforces the limit of optimising only part of a system.

### 10.3 Summarise repeated runs and inspect variability

This example uses synthetic run-level p95 measurements. It reports the mean and range of runs; with only five runs per condition, this is descriptive evidence, not a formal significance test.

```python
import math
from statistics import mean, stdev

baseline_runs = [4.1, 3.9, 4.0, 4.2, 3.8]
candidate_runs = [3.4, 3.3, 3.2, 3.5, 3.1]


def describe(values):
    if not isinstance(values, (list, tuple)) or len(values) < 2:
        raise ValueError("at least two run measurements are required")
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
        for value in values
    ):
        raise ValueError("run measurements must be finite non-negative numbers")
    return {
        "n": len(values),
        "mean": mean(values),
        "min": min(values),
        "max": max(values),
        "sample_sd": stdev(values),
    }


b = describe(baseline_runs)
c = describe(candidate_runs)
reduction = (b["mean"] - c["mean"]) / b["mean"]

assert b["n"] == 5 and c["n"] == 5
assert abs(b["mean"] - 4.0) < 1e-12
assert abs(c["mean"] - 3.3) < 1e-12
assert abs(reduction - 0.175) < 1e-12
for invalid_runs in ([], [4.0], [4.0, float("nan")], [4.0, -1.0], [True, 4.0]):
    try:
        describe(invalid_runs)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid run sample accepted: {invalid_runs!r}")

print({"baseline": b, "candidate": c, "mean_run_p95_reduction_pct": reduction * 100})
```

Expected mean run-level p95 values: baseline 4.0 seconds; candidate 3.3 seconds; descriptive reduction 17.5%. The result suggests a consistent improvement in these synthetic runs, but a formal conclusion still depends on test validity, paired/independent design, relevant sample sizes, and guardrails. Note that these are means of per-run p95 values, not a pooled p95 across all request observations.

### 10.4 Capacity headroom with an explicit denominator

```python
import math


def _finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def capacity_headroom(validated_capacity: float, expected_demand: float) -> dict:
    if not _finite_number(validated_capacity) or validated_capacity <= 0:
        raise ValueError("validated capacity must be finite and positive")
    if not _finite_number(expected_demand) or expected_demand < 0:
        raise ValueError("expected demand must be finite and non-negative")
    if expected_demand > validated_capacity:
        raise ValueError("demand exceeds validated capacity")

    spare = validated_capacity - expected_demand
    return {
        "spare_requests_per_second": spare,
        "headroom_as_fraction_of_capacity": spare / validated_capacity,
        "spare_as_fraction_of_demand": None if expected_demand == 0 else spare / expected_demand,
        "demand_utilisation_of_validated_capacity": expected_demand / validated_capacity,
    }


h = capacity_headroom(1200, 900)
assert h["spare_requests_per_second"] == 300
assert abs(h["headroom_as_fraction_of_capacity"] - 0.25) < 1e-12
assert abs(h["spare_as_fraction_of_demand"] - (1 / 3)) < 1e-12
assert abs(h["demand_utilisation_of_validated_capacity"] - 0.75) < 1e-12
assert capacity_headroom(1200, 0)["spare_as_fraction_of_demand"] is None
for capacity, demand in ((0, 0), (1200, -1), (1200, float("nan")), (float("inf"), 10), (True, 1)):
    try:
        capacity_headroom(capacity, demand)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid capacity input accepted")

print(h)
```

Expected: 300 requests/s spare; 25% headroom relative to validated capacity; 33.33% spare relative to demand; 75% demand utilisation. Always label the denominator.

### 10.5 Payback calculation with input validation

```python
import math


def _finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def simple_payback_months(one_time_cost: float, monthly_net_saving: float) -> float:
    if not _finite_number(one_time_cost) or one_time_cost < 0:
        raise ValueError("one-time cost must be finite and non-negative")
    if not _finite_number(monthly_net_saving) or monthly_net_saving <= 0:
        raise ValueError("monthly net saving must be finite and positive")
    return one_time_cost / monthly_net_saving


payback = simple_payback_months(18000, 3000)
assert abs(payback - 6.0) < 1e-12
assert simple_payback_months(0, 3000) == 0
for cost, saving in ((-1, 3000), (18000, 0), (18000, float("nan")), (float("inf"), 3000), (True, 3000)):
    try:
        simple_payback_months(cost, saving)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid payback input accepted")

print({"simple_payback_months": payback})
```

Expected: six months under the illustrative assumption of \$3,000/month in net savings. If savings are estimated, the payback is estimated; it is not proof of realized return.

---

## 11. Practical exercises at three levels

Attempt the tasks before consulting the answer key.

### Level 1 — Beginner: label the evidence

Classify each statement as **fact (measured), assumption, estimate, hypothesis, recommendation, or verified outcome**. If a statement is ambiguous, rewrite it so its evidence type is clear.

1. “p95 was 3.4 seconds in run 12 at 700 requests/s.”
2. “Traffic will rise by 25% next quarter.”
3. “At that growth rate, the system will need 10 additional worker units.”
4. “Partition skew is causing the long-running tasks.”
5. “Run a controlled replay with a different partition key.”
6. “After the change, p95 fell from 3.4 seconds to 2.9 seconds across four comparable runs, and the error-rate guardrail passed.”
7. “The cache probably explains the latency spike.”
8. “The change will save \$2,000/month.”
9. “The source query scanned 1.8 TB in the recorded execution.”
10. “Keep the candidate behind a 10% canary while collecting another day of evidence.”

For each, state what additional evidence would strengthen the claim.

### Level 2 — Intermediate: evaluate a candidate

A synthetic test compares a baseline and candidate under a declared 600 requests/s workload.

| Metric | Baseline | Candidate |
|---|---:|---:|
| p95 latency | 2.8 s | 2.3 s |
| p99 latency | 5.0 s | 5.4 s |
| Error rate | 0.10% | 0.15% |
| Cost per successful query | \$0.020 | \$0.022 |
| Freshness lag p95 | 4 min | 4 min |

Tasks:

1. Calculate the p95 reduction.
2. Calculate the p99 relative change and state its direction.
3. Calculate the relative cost-per-successful-query increase.
4. Explain why the candidate cannot be called an unconditional success from this table alone.
5. Propose two additional measurements or controls.
6. Write a conditional recommendation with evidence labels.

### Level 3 — Advanced: three-iteration bottleneck migration

A fictional data pipeline has an end-to-end baseline of 100 seconds, composed of:

- input/read: 20 s;
- transform: 50 s;
- shuffle/join: 20 s;
- publish: 10 s.

Assume these stage times are serial and additive for the first-pass model.

Iteration A makes transform 4× faster. Iteration B, after re-profiling, makes the shuffle/join stage 2× faster from its post-A duration. Iteration C proposes doubling input throughput, but the expected benefit and cost are not yet measured.

Tasks:

1. Calculate end-to-end time and speedup after A.
2. Calculate the new end-to-end time and speedup after B.
3. Identify which stage(s) now dominate the remaining time.
4. Explain what evidence is needed before accepting C.
5. List at least three guardrails that could block an otherwise faster design.
6. Create a short ADR recommendation, including whether to proceed, test, or stop.

---

## 12. Answer key and reasoning

### Level 1 — example classifications

1. **Fact (measured)** — requires test ID, units, workload and measurement definition to be reproducible.
2. **Assumption** — verify against traffic forecasts or label a low/expected/high range.
3. **Estimate** — show the capacity formula and assumptions behind the worker count.
4. **Hypothesis** — compare per-partition load, task duration, spill, and skew evidence.
5. **Recommendation** — specify the test design, acceptance criteria, and rollback.
6. **Verified outcome candidate** — the stated repeated measurements and guardrail are evidence; confirm the workload/environment comparability and other hard constraints before calling the architecture change verified overall.
7. **Hypothesis** — inspect hit/miss ratio, cache latency, backend queueing, and time correlation; correlation alone is not proof.
8. **Estimate or hypothesis**, depending on whether a model supports it. It is not a verified saving until costs are measured and attributable.
9. **Fact (measured)** — retain query ID, plan/execution record, data definition, and measurement source.
10. **Recommendation** — define the canary allocation, comparison group, monitoring window, and rollback threshold.

### Level 2 — calculations

1. p95 reduction = \((2.8-2.3)/2.8 \approx 17.86\%\).
2. p99 relative change = \((5.4-5.0)/5.0 = 8\%\) increase, which is worse.
3. Cost increase = \((0.022-0.020)/0.020 = 10\%\).
4. The p95 improves, but p99 worsens, error rate rises by 0.05 percentage points, and cost per successful query rises by 10%. The candidate may violate a tail-latency or error/cost guardrail. Run counts and variability are missing, so the table alone cannot establish confidence or causality.
5. Useful additions: repeated comparable runs and raw latency distributions; workload and cache-state verification; backend queue and resource saturation; correctness/freshness checks; cost attribution and successful-work denominator; another workload mix.
6. Example: **Fact (measured in the supplied synthetic table):** p95 falls 17.86% while p99 rises 8%, error rate rises, and unit cost increases 10%. **Hypothesis:** the change helps common requests but worsens a tail path or resource contention. **Recommendation:** do not broadly roll out until repeated tests determine whether p99/error regressions violate guardrails; keep or revert based on predeclared criteria.

### Level 3 — calculations and decision

1. After A: transform falls from 50 s to 12.5 s. Total = \(20 + 12.5 + 20 + 10 = 62.5\) s. Speedup = \(100/62.5 = 1.6\times\).
2. After B: shuffle/join falls from 20 s to 10 s. Total = \(20 + 12.5 + 10 + 10 = 52.5\) s. Speedup from baseline = \(100/52.5 \approx 1.9048\times\).
3. Input is 20 s, transform 12.5 s, shuffle/join 10 s, publish 10 s. Input is now the largest single stage; there is no longer a single dominant stage of 50% as before.
4. Measure whether input is genuinely limiting: input queue/throughput, storage and network saturation, read latency, source capacity, data locality, and whether increasing input throughput moves load to transform or downstream stages. Estimate resource and cost impact, then test under a representative workload.
5. Possible guardrails: end-to-end p95/p99, error rate, correctness/reconciliation, freshness lag, source-system load, cost per successful batch, reliability/recovery, and data-transfer or egress limits.
6. Example ADR: “Do not implement C directly based only on stage timing. **Fact (synthetic model):** after A+B, input is the longest single stage at 20 seconds. **Hypothesis:** input throughput limits further improvement. **Recommendation:** profile input and downstream saturation, then run a bounded experiment that increases input throughput while preserving source safety. Keep only if end-to-end latency improves by the predeclared threshold and cost, error, freshness, and correctness guardrails pass. Roll back on any hard-constraint breach.”

---

## 13. Common mistakes, misleading conclusions, and troubleshooting

### 13.1 Common mistakes

| Mistake | Why it misleads | Correction |
|---|---|---|
| Optimising before recording a baseline | No defensible measure of change | Capture workload, metrics, conditions, and raw results first |
| Treating a symptom as a cause | Multiple mechanisms can produce the same symptom | Form a falsifiable hypothesis and use discriminating measurements |
| Changing many things at once without a design | Attribution becomes impossible | Change one variable where feasible, or explicitly test a bundle/interaction |
| Comparing unlike workloads | Difference may be caused by traffic or data changes | Match or model workload, data, and environment |
| Reporting only averages | Tail regressions disappear | Report p50/p95/p99, sample counts, and distributions |
| Declaring success from one run | Run-to-run noise and environmental effects remain unknown | Repeat and quantify variability; use a suitable design |
| Using Amdahl as a prediction guarantee | Real systems have parallelism, contention, and shifting bottlenecks | Use it to bound prioritisation; measure end-to-end |
| Optimising a small component | Overall gain is limited | Estimate component share and likely system-level impact |
| Ignoring the new bottleneck | Further work targets the wrong stage | Re-profile after each meaningful change |
| Calling an estimate a saving | The result may not be realised or attributable | Label estimate and verify actual cost over a consistent period |
| Ignoring operational complexity | Performance gains may create refresh, invalidation, or recovery burden | Include operational cost, failure modes, and ownership |
| Failing to predefine success | Teams can rationalise almost any outcome after seeing it | Define primary metric, practical threshold, and guardrails first |
| Ignoring regression risk | One workload improves while another degrades | Run representative regression and failure suites |
| Treating synthetic tests as production proof | Synthetic data may miss real skew, contention, or dependency behaviour | State the representativeness gap and validate in a safe canary if appropriate |

### 13.2 Troubleshooting guide

| Observation | Possible explanations | Evidence to inspect | Next action |
|---|---|---|---|
| Candidate is faster in one run but slower in another | Noise, cache state, shared load, autoscaling | Run-level distributions and conditions | Repeat paired/alternating runs; stabilise or record environment |
| p50 improves but p99 worsens | Tail path, queueing, retries, skew, downstream saturation | Per-stage percentiles, errors, queue depth, key skew | Isolate tail requests and test the suspected mechanism |
| CPU falls but latency does not improve | Bottleneck is elsewhere or concurrency changed | Network, I/O, locks, queueing, dependency latency | Re-profile end-to-end; avoid CPU-only conclusions |
| Throughput increases but errors rise | Overload, retries, timeout budget, weak denominator | Successful throughput, error types, retry count | Enforce guardrails and evaluate successful work only |
| Query gets faster but total batch does not | Query is a small part, overlap hides savings, next stage dominates | Stage timing and critical path | Apply Amdahl reasoning and profile the new critical path |
| Cost per unit falls but total bill rises | Volume growth or fixed baseline changed | Total cost, unit denominator, workload volume | Report unit and total cost together; normalise periods |
| Test result cannot be reproduced | Configuration drift, data drift, missing raw evidence | Version, input hash/snapshot, run logs | Freeze environment and automate the test procedure |
| Production does not match staging | Different data, scale, network, contention, policy, cache | Environment differences and production telemetry | Canary safely; update the validity limits of staging evidence |
| Change improves one tenant but harms another | Shared-resource contention or workload mix | Per-tenant latency, queueing, fairness, resource use | Evaluate multi-workload outcomes and scheduling policies |
| Expected savings are absent from billing | Attribution mismatch, shifted spend, commitments, lag | Service-level cost records and allocation rules | Reconcile cost categories and billing periods; do not assume savings |

### 13.3 Limits of the method

- A controlled experiment can still be unrepresentative of production.
- A before/after comparison can be confounded by unobserved environmental changes.
- A small sample can fail to reveal rare but severe tail events.
- Amdahl-style estimates simplify complex parallel and distributed execution.
- Cost attribution can be imperfect for shared infrastructure.
- Some changes affect multiple variables and require a designed bundle experiment.
- A verified outcome applies to the tested conditions and time window; it does not guarantee all future workloads.

State these limitations in the conclusion rather than hiding them in footnotes.

---

## 14. Expected deliverables and practical templates

The module roadmap expects a **baseline record**, **bottleneck ranking with impact calculation**, **option comparison with evidence levels and risks**, **before/after evaluation report**, and a **decision record with labelled evidence**. These artefacts are meant to make the recommendation reviewable by someone who did not run the experiment.

### 14.1 Optimisation hypothesis card

```text
Hypothesis ID / title:
Owner and date:
Workload / service:
Business objective:
Observed symptom:
Evidence supporting the hypothesis:
Evidence against / alternative explanations:
Evidence label for each statement:
Proposed mechanism:
Intervention:
Expected effect (range, unit, rationale):
Primary metric:
Practical improvement threshold:
Hard guardrails:
Workload and environment:
Control/comparison design:
Sample/run plan:
Known confounders:
Safety and abort conditions:
Rollback plan:
Decision date:
Result and evidence links:
```

### 14.2 Before-and-after evaluation report

| Field | Baseline | Candidate | Difference | Interpretation / evidence label |
|---|---:|---:|---:|---|
| Workload ID and version | | | | |
| Data volume and skew | | | | |
| Throughput | | | | |
| p50 / p95 / p99 | | | | |
| Error rate | | | | |
| Queue/backlog | | | | |
| Resource saturation | | | | |
| Freshness/correctness | | | | |
| Cost per successful unit | | | | |
| Total cost per period | | | | |
| Run count / sample count | | | | |
| Variability / uncertainty | | | | |
| Hard guardrails passed? | | | | |
| Confounders and limits | | | | |

### 14.3 Evidence register

| ID | Claim | Evidence label | Source / run ID | Unit and time window | Confidence | Limitation | Follow-up |
|---|---|---|---|---|---|---|---|
| E-001 | | Fact / assumption / estimate / hypothesis / recommendation / verified outcome | | | | | |

Every important number and conclusion in the final review should map to an evidence-register entry. Keep links or paths to raw logs, query plans, test outputs, and cost records where available.

### 14.4 Bottleneck ranking

| Rank | Symptom | Candidate cause | Evidence | Estimated share/impact | Confidence | Validation test | Cost/risk |
|---:|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |

Use estimates only where their assumptions are explicit. If the evidence does not distinguish causes, rank the next measurements rather than pretending the cause is known.

### 14.5 Option comparison and decision record

```text
ADR ID / title:
Status: proposed / accepted / rejected / superseded
Date / owner / reviewers:
Context and business objective:
Baseline and evidence links:
Hard constraints:
Options considered:
Decision:
Evidence labels and confidence:
Expected benefit range:
Measured outcome (if available):
Performance / capacity impact:
Cost and unit-economics impact:
Freshness / correctness impact:
Reliability and recovery impact:
Operational complexity / maintainability:
Risks and confounders:
Validation plan and acceptance criteria:
Rollback / stop condition:
Residual issues:
Follow-up measurements and due date:
Revisit triggers:
```

### 14.6 Follow-up and regression checklist

- [ ] Baseline and candidate use comparable workload, data, environment, and metric definitions.
- [ ] Primary metric and hard guardrails were defined before the test.
- [ ] Repeated runs and uncertainty are reported.
- [ ] Correctness, freshness, and access-control checks pass.
- [ ] Other workloads and shared-resource effects were checked.
- [ ] Cost per successful unit and total cost use consistent periods and attribution.
- [ ] Capacity forecasts and growth assumptions were updated where evidence warrants it.
- [ ] Rollback was tested or its limits documented.
- [ ] Raw evidence and configuration are retained.
- [ ] An independent reviewer can reproduce key calculations.
- [ ] Remaining risks and the next measurement are assigned to an owner.

---

## 15. Mastery criteria and completion gate

### Mastery criteria

You are ready to integrate this topic into the final review when you can:

- [ ] Correctly label facts, assumptions, estimates, hypotheses, recommendations, and verified outcomes.
- [ ] Establish a baseline with workload, units, time window, environment, and limitations.
- [ ] Turn a performance symptom into one or more falsifiable hypotheses.
- [ ] Prioritise candidate fixes using measured impact and Amdahl-style bounds.
- [ ] Design a controlled experiment with a baseline/control, primary metric, guardrails, and rollback criteria.
- [ ] Compare before/after results while accounting for variability and confounders.
- [ ] Explain why a single successful run or a faster average is not enough.
- [ ] Identify bottleneck migration and check for regressions across workloads.
- [ ] Quantify performance, capacity, freshness, and cost trade-offs with reproducible calculations.
- [ ] Update capacity and cost models without presenting estimates as verified savings.
- [ ] Communicate confidence, evidence gaps, and follow-up measurements.
- [ ] Produce an optimisation review and ADR that another reviewer can audit.

### Completion gate

The module roadmap defines the gate as an optimisation review and decision record reviewed by another person; every claim is evidence-labelled and none overstates; relevant practice questions are attempted and gaps logged; and the learner is ready to integrate all eight topics into the final project.

Use this practical gate:

1. Submit a baseline record and evidence register.
2. Submit a bottleneck ranking with an impact calculation.
3. Submit an experiment plan with predeclared acceptance criteria.
4. Submit a before-and-after report with run variability and guardrails.
5. Submit an option comparison and ADR, including costs and risks.
6. Have another person reproduce at least three calculations and challenge one major recommendation.
7. Record unresolved gaps and the follow-up measurement that would reduce uncertainty.

**Pass condition:** the reviewer can trace any material claim to its evidence label, source, unit, and time window; calculations are reproducible; conclusions respect the limits of the experiment; and each recommendation includes a validation and rollback or stop condition. A simulation can demonstrate the method, but must be labelled as simulated and cannot be described as a production-verified benefit.

---

## 16. Integration with the final Capacity, Cost and Performance Review project

Topic 08 is the final synthesis topic for the module. It does not stand alone: it turns earlier artefacts into a coherent, evidence-backed architecture review.

### 16.1 Integrate all eight topics

| Topic | Input to the final review | How Topic 08 closes the loop |
|---|---|---|
| 01 — Capacity and growth | Workload and demand scenarios | Update forecasts with validated capacity and explicitly stated uncertainty |
| 02 — Throughput, latency and queueing | Latency distributions, saturation and backlog | Verify whether the intervention changes the actual limiting mechanism |
| 03 — Query performance and locality | Query plans, scan/shuffle evidence | Prioritise fixes by workload share and verify end-to-end effect |
| 04 — Scaling and hotspots | Skew, distribution, partitioning evidence | Test whether a proposed distribution change reduces the measured bottleneck |
| 05 — Caching/materialisation | Reuse, hit/miss, freshness and refresh costs | Verify net performance and cost while preserving freshness/correctness |
| 06 — Cost modelling and FinOps | Cost drivers, unit economics, forecasts | Compare estimated and measured cost on consistent terms |
| 07 — Performance testing | Repeatable test design and acceptance criteria | Produce evidence for or against the proposed change |
| 08 — Evidence-based optimisation | Baseline, hypothesis, experiment, decision record | Prioritise, evaluate, communicate, and follow up |

### 16.2 Recommended final review package

The module roadmap's final project guide notes that the project files were empty when the roadmap was authored and proposes a review package consistent with the project name. Treat the following as recommended unless the actual project specification supplies different requirements:

1. Requirements and assumptions summary.
2. Workload profile and baseline.
3. Capacity and growth forecast.
4. Performance and bottleneck analysis.
5. Query performance review.
6. Scaling and data-distribution decision matrix.
7. Caching/materialisation/serving comparison.
8. Cost model and unit-economics table.
9. Performance test and capacity-validation plan.
10. Optimisation recommendation register.
11. Consolidated architecture review and evidence register.
12. Validation checklist and limitations list.

### 16.3 Final review consistency checks

Before presenting the review:

- Ensure capacity assumptions match the workload used in performance tests.
- Ensure query and skew findings support the chosen optimisation.
- Ensure serving choices meet freshness and correctness requirements.
- Ensure cost inputs use consistent units, periods, and denominators.
- Ensure no recommendation is called verified unless measurement supports it.
- Ensure the before-and-after test uses comparable conditions and states its limits.
- Ensure every recommendation includes an expected effect, validation method, risks, and rollback or stop condition.
- Ensure a reviewer can reproduce three calculations and trace each major claim to its evidence source.

### 16.4 Final communication pattern

For each recommendation, communicate:

1. **Decision:** what should be done now.
2. **Evidence:** what was measured and under which conditions.
3. **Interpretation:** what the evidence supports—and what it does not.
4. **Expected impact:** range, units, and assumptions.
5. **Trade-offs:** cost, freshness, reliability, complexity, and maintainability.
6. **Validation:** acceptance criteria and comparison design.
7. **Risk control:** rollback, stop condition, and monitoring.
8. **Next evidence:** what remains unknown, who will measure it, and when.

The final review is complete when it is possible to challenge a recommendation without relying on the author's confidence or intuition: the evidence, assumptions, calculations, limitations, and next test are all visible.

**Module outcome:** you can now evaluate and improve data architectures using measured evidence, connect performance to capacity and cost, and make recommendations that are testable, reversible where possible, and honest about uncertainty.
