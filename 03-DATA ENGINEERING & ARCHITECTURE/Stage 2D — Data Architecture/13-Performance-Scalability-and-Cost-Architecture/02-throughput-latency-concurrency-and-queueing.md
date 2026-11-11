# Throughput, Latency, Concurrency and Queueing

**Repository location:** `Stage 2D — Data Architecture/13-Performance-Scalability-and-Cost-Architecture/02-throughput-latency-concurrency-and-queueing.md`  
**Module:** Stage 2D, Module 2D.13 — Performance, Scalability and Cost Architecture  
**Level:** Beginner → Intermediate → Advanced  
**Examples:** Vendor-neutral; all organizations, measurements, thresholds, and datasets are illustrative.

## 1. Purpose and scope

This lesson explains how work moves through a system, how to measure its speed and delay, why queues form, and why performance can deteriorate rapidly when demand approaches a resource's sustainable capacity.

The core questions are:

- How much work is offered, admitted, and completed per unit time?
- How long does each request or unit of work take?
- How many units are in progress or waiting?
- Is the system stable, accumulating backlog, or overloaded?
- What evidence distinguishes a capacity limit from another cause of high latency?

This topic builds on Topic 01, `01-capacity-planning-and-growth-forecasting.md`, which characterizes demand, average and peak load, resource capacity, headroom, and forecast uncertainty. It prepares you for Topic 03, `03-query-performance-and-data-locality.md`, where measurements help identify why particular queries or data-access paths are slow.

**Scope boundary:** this lesson develops queueing intuition and diagnostic practice. Detailed query tuning and data locality belong to Topic 03; partitioning, sharding, and hotspots to Topic 04; caching and materialization to Topic 05; cost modelling to Topic 06; and formal performance-test planning to Topic 07.

## 2. Learning outcomes

By the end, you should be able to:

1. Distinguish throughput, latency, service time, queue wait, concurrency, utilisation, capacity, and saturation.
2. Interpret averages and latency percentiles without treating one statistic as a complete description.
3. Separate offered load, admitted load, completed throughput, service rate, and backlog.
4. Apply Little's Law with explicit system boundaries, units, and stability assumptions.
5. Calculate backlog growth and idealized drain time.
6. Explain why response time can rise sharply near saturation and why extra concurrency can worsen overload.
7. Distinguish open and closed workload-generation models.
8. Form hypotheses about CPU-, memory-, I/O-, network-, lock-, and connection-limited workloads.
9. Explain backpressure, admission control, timeouts, retries, and load shedding.
10. Produce a workload/metric definition sheet, a measurement analysis, a queue calculation, a diagnosis note, and measurable warning signals.

## 3. Prerequisites and Topic 01 review

### 3.1 Concepts carried forward

Topic 01 established that capacity planning starts with workload characterization, not a single machine-size guess.

| Topic 01 concept | How it is used here |
|---|---|
| Workload profile | Defines request types, sizes, rates, concurrency, and time windows |
| Average vs peak | Separates normal demand from sustained peaks and bursts |
| Capacity and target utilisation | Establishes a measured operating region with margin |
| Headroom | Provides room for variability, growth, and failure scenarios |
| Growth scenarios | Helps predict when demand may approach a bottleneck |
| Service objectives | Define which latency, freshness, and completion outcomes are acceptable |
| Measurement and forecast error | Tests whether capacity assumptions match observed behaviour |

A capacity estimate alone cannot tell you the latency at a given load. You need measured response behaviour under a representative workload. Likewise, an average event rate does not reveal whether arrivals are steady or bursty.

### 3.2 Questions to carry forward

Before analysing performance, record:

- What is the workload unit: request, row, event, job, query, or byte?
- What interval defines the rate: one second, one minute, or one hour?
- Is the rate offered, admitted, or completed?
- What are the workload mix and payload sizes?
- What service objective must hold (for example, p95 latency below a stated target)?
- What resource or limit may constrain the workload?
- Are measurements complete and time-aligned?

## 4. Beginner foundations

### 4.1 Intuitive example: a service desk

Imagine a service desk with people arriving, waiting, being served, and leaving.

- **Arrival rate:** people arriving each minute.
- **Service rate:** people one worker can serve each minute under a stated mix.
- **Queue wait:** time spent waiting before service starts.
- **Service time:** time the worker spends handling a person.
- **Response time:** waiting time plus service time.
- **Concurrency / work in progress:** people currently waiting or being served, depending on the stated boundary.
- **Throughput:** people actually completed per minute.
- **Saturation:** the workers and other necessary resources cannot keep up with demand.

If arrivals exceed service capacity for long enough, the line grows. Hiring another worker may help only if worker capacity is the bottleneck; if the payment system is down, the extra worker may not improve throughput.

### 4.2 Precise terminology

| Term | Definition | Important distinction |
|---|---|---|
| Throughput | Completed work per unit time | It is an observed rate, not automatically the maximum sustainable rate |
| Latency | Elapsed time for a unit of work across a defined boundary | State where timing begins and ends |
| Service time | Time actively receiving service from the constrained component | Does not include all waiting outside that service boundary |
| Queue-wait time | Time waiting before or between service stages | Can rise even when service time is unchanged |
| End-to-end latency | Elapsed time from the user-visible start to completion | May include network, queue, service, retries, and downstream waits |
| Concurrency | Number of work units in progress at a given time or averaged over time | State whether queued units are included |
| Work in progress (WIP) | Work that has started but has not yet completed, within a defined boundary | May include queued and actively served work |
| Arrival rate \(\lambda\) | Work units arriving per unit time | Offered arrivals can exceed admitted work |
| Completion rate \(X\) | Work units completed per unit time | Successful completions may be a subset of all responses |
| Service rate \(\mu\) | Rate a server or resource can complete work when busy, under stated assumptions | Not necessarily equal to system throughput under idle time, failures, or contention |
| Utilisation \(\rho\) | Fraction of a specified resource's available service capacity in use | Resource-specific; 80% CPU does not mean 80% memory |
| Capacity | Sustainable workload level while meeting specified service objectives | Depends on workload mix and operating conditions |
| Saturation | A resource or control limit prevents additional useful work from being processed without degradation | Can occur before a dashboard reaches 100% |

**Always define the boundary.** “Concurrency is 200” is incomplete without knowing whether that means client requests, requests waiting in a queue, active database operations, open connections, or all in-flight operations.

### 4.3 Throughput is not latency

A system can complete 5,000 requests/s while each request takes 400 ms if enough requests are in flight. A different system may complete 500 requests/s with 20 ms latency. Neither is universally better: the right comparison depends on the workload, service objectives, and resource cost.

High throughput does not guarantee low latency. Low latency at low offered load does not prove that the system can maintain that latency at peak load.

### 4.4 Latency components

For a simple single-stage path:

\[
T_{\text{response}}=T_{\text{queue wait}}+T_{\text{service}}
\]

For a real end-to-end request, elapsed time may include client/network transit, admission wait, multiple queues, service stages, serialization, retries, and downstream calls. Be careful not to double-count overlapping intervals when summing instrumented spans.

A useful diagnostic split is:
- **Queue wait rises; service time stable:** possible contention, concurrency cap, or saturation upstream.
- **Service time rises; queue wait stable:** possible slower dependency, larger payload, CPU/I/O slowdown, or changed workload.
- **Both rise:** could be one bottleneck causing cascading delays, or multiple changes.
- **Latency rises while throughput falls:** strong overload or failure signal, but investigate evidence before assigning cause.

## 5. Units and measurement discipline

### 5.1 Common units

| Metric | Common units |
|---|---|
| Throughput | requests/s, events/s, rows/s, jobs/min, MB/s |
| Latency / wait / service time | ms, seconds |
| Concurrency / WIP / backlog | requests, events, jobs, connections |
| Arrival or completion rate | work units/s or work units/min |
| Service capacity | work units/s under a defined workload |
| Utilisation | ratio or percentage |
| Backlog drain time | seconds, minutes, hours |

Keep the work unit consistent. “Rows/s” and “requests/s” cannot be added unless you have a justified conversion between rows and requests.

### 5.2 Time conversion

- 1 second = 1,000 milliseconds.
- 1 minute = 60 seconds.
- 1 hour = 3,600 seconds.

If a system completes 18,000 events in 5 minutes:

\[
X=\frac{18{,}000\ \text{events}}{300\ \text{s}}=60\ \text{events/s}
\]

Use the actual measurement interval. A one-second peak and a five-minute average answer different questions.

### 5.3 Offered, admitted, and completed work

Keep these rates separate:

- **Offered load:** work clients attempt to send.
- **Admitted load:** work accepted by the system for processing.
- **Completed throughput:** work that finishes within the measured boundary.
- **Successful throughput:** completed work that meets the defined success criterion.
- **Service rate:** potential processing rate when a specific server/resource is busy, under a model or measured condition.

When a system rejects requests, admitted load can be below offered load. When work times out at clients but continues on the server, client-observed failures may not reduce server-side resource consumption. When a queue is draining, completion rate can exceed current arrival rate because old work is being completed.

## 6. Latency distributions: mean, p50, p95, p99

### 6.1 Why the mean is incomplete

Suppose 99 requests take 20 ms and one takes 2,000 ms. The mean is:

\[
\bar{T}=\frac{99(20\text{ ms})+1(2000\text{ ms})}{100}=39.8\text{ ms}
\]

The mean is almost twice the common 20 ms case, but it does not communicate that one request took 2 seconds. Tail latency matters when users, downstream services, or deadlines are sensitive to the slowest fraction.

A **percentile** \(p_k\) is a value at or below which approximately \(k\)% of observations fall, under the chosen percentile estimator. In plain terms:
- p50 is the median;
- p95 is the 95th percentile;
- p99 is the 99th percentile.

Percentile algorithms differ in their interpolation conventions, especially for small samples. Use the same method when comparing runs.

### 6.2 Interpreting percentiles

If p95 latency is 250 ms, approximately 95% of the measured requests completed in 250 ms or less, and approximately 5% took longer, subject to sampling and percentile-estimator details.

Percentiles do not identify the cause of slow requests. Break observations down by route, request type, payload, tenant, region, and time window when those dimensions are relevant and privacy-safe.

### 6.3 Percentiles cannot generally be added

If a request calls service A and then service B, the end-to-end p95 is not generally equal to p95(A) + p95(B). The slow requests may not be the same requests in both components; dependencies and correlations matter. Summing component percentiles can be a rough conservative or planning approximation only when its assumptions are stated, not a general identity.

For sequential stages, actual per-request elapsed durations can be added when they are non-overlapping spans for the same request. To compute the end-to-end percentile, calculate the percentile from the end-to-end observations (or use a justified statistical model).

### 6.4 Sampling and aggregation pitfalls

- Averaging p95 values from different hosts or intervals does not generally yield the combined p95.
- Averages can hide a small but important slow tail.
- Low sample counts make extreme percentiles noisy.
- Sampling may omit slow or failed requests.
- Averages over a day can hide a short peak interval.
- Compare like-for-like workloads, time windows, status codes, and percentile methods.

## 7. Little's Law: WIP, throughput, and time

### 7.1 Formula

Little's Law states:

\[
L=\lambda W
\]

where:
- \(L\) = long-run average number of work units in the defined system (units);
- \(\lambda\) = long-run average throughput through that system (units/s);
- \(W\) = long-run average time a unit spends in that system (s).

The units are consistent: units/s × s = units.

For a system in which the relevant arrivals and departures balance over the long run, average WIP equals average throughput times average time in the system.

### 7.2 Worked example

A service completes an average of 200 requests/s. Average end-to-end time in the measured system is 50 ms = 0.050 s.

\[
L=200\ \frac{\text{requests}}{\text{s}}\times0.050\ \text{s}
=10\ \text{requests}
\]

The system contains about 10 requests on average within that boundary, including whatever queued and active work the boundary definition includes.

If average latency rises to 100 ms while throughput remains 200 requests/s, Little's Law implies average WIP of 20 requests. This is a relationship among averages, not proof that latency caused concurrency to double.

### 7.3 Assumptions and limitations

Little's Law is very general, but its use still requires careful measurement:
- Define the system boundary and count the same work units at entry, WIP, and exit.
- Use long-run averages over a period where the system is sufficiently stable and the relevant rates are finite.
- For a stable queue, long-run admitted arrival rate and departure rate balance (ignoring defined loss/abandonment differences).
- Include waiting and service time consistently if WIP includes queued and in-service units.
- Handle rejected, abandoned, cancelled, duplicated, or retried work explicitly.
- Do not apply a steady-state interpretation to a queue whose backlog is growing without bound.
- Do not mix an average rate over one window with latency from a different workload regime.

Little's Law does not predict latency from capacity alone and does not tell you the queue's latency distribution. It relates observed average WIP, throughput, and time.

### 7.4 Use Little's Law diagnostically

If measured average throughput is 500 events/s and average time in the pipeline is 2 seconds, average WIP is approximately 1,000 events. If instrumentation reports only 100 in-flight events, investigate whether the boundaries, event definitions, time windows, or sampling differ. The discrepancy is a clue to measurement inconsistency, not automatically proof of a bug.

## 8. Queue growth, backlog, and catch-up

### 8.1 Basic backlog arithmetic

Let:
- \(B_0\) = starting backlog (work units);
- \(\lambda\) = incoming arrival rate (units/s);
- \(\mu\) = processing/completion rate available to that queue (units/s);
- \(\Delta t\) = interval (s).

When rates are approximately constant and \(\lambda>\mu\):

\[
B_1=B_0+(\lambda-\mu)\Delta t
\]

This is a fluid approximation: it ignores discrete events, variable processing time, retries, failures, and changing rates.

**Illustrative example:** a queue starts at 10,000 events. Arrivals are 800 events/s and processing is 650 events/s for 120 seconds.

\[
\Delta B=(800-650)\ \text{events/s}\times120\ \text{s}=18{,}000\ \text{events}
\]

Final backlog is \(10{,}000+18{,}000=28{,}000\) events.

### 8.2 Queue drain time

If new arrivals stop and the system processes at a constant rate \(\mu>0\), ideal drain time is:

\[
T_{\text{drain}}=\frac{B}{\mu}
\]

If new work continues at rate \(\lambda\) and processing capacity is \(\mu>\lambda\), net drain rate is \(\mu-\lambda\):

\[
T_{\text{drain}}=\frac{B}{\mu-\lambda}
\]

**Illustrative example:** backlog is 28,000 events; new arrivals continue at 500 events/s; processing capacity is 700 events/s.

\[
T_{\text{drain}}=\frac{28{,}000\ \text{events}}{(700-500)\ \text{events/s}}
=140\ \text{s}
\]

If \(\mu=\lambda\), the backlog does not drain under this constant-rate model. If \(\mu<\lambda\), backlog grows. These equations assume rates stay constant and that the queue can use the stated processing capacity for the whole interval.

### 8.3 Catch-up after an outage

Suppose a feed is unavailable for 30 minutes while 400 events/s would normally arrive. Ignoring any already-processed or dropped events, backlog accumulated is:

\[
B=400\ \text{events/s}\times1{,}800\ \text{s}=720{,}000\ \text{events}
\]

After recovery, if processing can run at 700 events/s while new arrivals continue at 400 events/s, net catch-up capacity is 300 events/s. Ideal catch-up time is:

\[
720{,}000/300=2{,}400\ \text{s}=40\ \text{minutes}
\]

That 40-minute estimate assumes the system can sustain 700 events/s without violating foreground service objectives. If it can only process 500 events/s while preserving those objectives, net catch-up capacity is 100 events/s and the backlog takes 120 minutes to clear.

### 8.4 Why backlog is not the same as latency

A backlog count alone does not reveal each item's wait. If arrivals are FIFO and processing is steady, backlog divided by processing rate can approximate the time needed to clear the work already ahead of a new item. But actual waiting depends on queue discipline, priorities, variable service times, concurrency, retries, and new arrivals.

A growing queue is evidence that, over that interval, incoming admitted work exceeds completed work for the queue boundary. It is not by itself proof of which resource is limiting processing.

## 9. Utilisation and response time near saturation

### 9.1 Utilisation intuition

For a simple single server with arrival rate \(\lambda\) and mean service rate \(\mu\), define:

\[
\rho=\frac{\lambda}{\mu}
\]

Under the basic single-server model, \(\rho<1\) is required for a stable queue. As \(\rho\) approaches 1, there is less spare capacity to absorb random variation, and waiting can rise rapidly.

Real data platforms contain multiple servers, stages, finite queues, variable workloads, dependencies, retries, and resource limits. Therefore, the formula is an intuition aid, not a universal latency predictor.

### 9.2 M/M/1 model (intuition only)

The M/M/1 model assumes:
- arrivals form a Poisson process (memoryless interarrival times);
- service times are exponentially distributed;
- one work-conserving server;
- an effectively unlimited queue;
- independent arrivals and service times;
- steady state with \(\lambda<\mu\).

For this model, mean time in the system is:

\[
W=\frac{1}{\mu-\lambda}
\]

where rates are in requests/s and \(W\) is seconds. Let \(\mu=100\) requests/s:

| Arrival rate \(\lambda\) | Utilisation \(\rho\) | Mean time in system \(W\) |
|---:|---:|---:|
| 50 requests/s | 0.50 | \(1/(100-50)=0.020\) s = 20 ms |
| 90 requests/s | 0.90 | \(1/(100-90)=0.100\) s = 100 ms |
| 95 requests/s | 0.95 | \(1/(100-95)=0.200\) s = 200 ms |
| 99 requests/s | 0.99 | \(1/(100-99)=1.000\) s = 1,000 ms |

This illustrates the nonlinear increase in waiting as utilisation approaches 100%. It is not a prediction for a distributed service without validating the assumptions.

### 9.3 Why actual systems differ

- Multiple parallel workers may change the queueing behaviour.
- Bursty arrivals violate the Poisson-arrival assumption.
- Service time may vary widely by query or payload.
- Shared locks, I/O, memory pressure, and downstream dependencies couple stages.
- Finite queues may reject work rather than grow indefinitely.
- Autoscaling introduces delays and changing service capacity.
- Retries can increase offered load precisely when the system is unhealthy.
- Priorities and fairness policies change which requests wait.

Use queueing models to generate hypotheses and reason about direction. Use measurements and controlled tests to establish system-specific behaviour.

## 10. Open and closed workload models

### 10.1 Open workload model

An open workload generator schedules arrivals independently of response completion. For example, it attempts 1,000 requests/s whether the service is fast or slow.

Useful for:
- modelling externally driven event streams or incoming requests;
- testing a specified arrival-rate profile;
- exposing overload and queue growth when demand exceeds capacity.

Risk: if the generator itself cannot keep up, the test may deliver less load than configured. Record scheduled arrivals, actually sent arrivals, admitted requests, and completed requests separately.

### 10.2 Closed workload model

A closed workload model has a fixed population of clients or workers. Each client sends work, waits for completion, then sends the next request (possibly after a think time).

Useful for:
- modelling a fixed worker pool or interactive users with bounded outstanding requests;
- understanding throughput under a fixed population.

Risk: when the service slows, clients issue fewer requests per second. This can conceal the overload response that an open workload would expose. A related measurement risk is **coordinated omission**: a closed-loop generator may omit or delay samples for arrivals that would have occurred during a stall, making the reported latency distribution look better than the experience under the intended arrival schedule. Closed-loop testing is not inherently invalid; choose the model to match the real workload and use an open-loop or corrected measurement approach when externally scheduled arrivals are the target.

### 10.3 Choosing and reporting a model

Choose the model that resembles the real source of demand. For a queue-based ingestion service, an open arrival-rate model may be appropriate. For a fixed pool of batch workers, a closed model may be more representative. Some systems need both tests.

Always report:
- workload model and configured arrival pattern;
- actual generated and admitted rates;
- concurrency and client limits;
- latency measurement start/end points;
- generator CPU/network limits;
- rejected, timed-out, and unfinished requests.

## 11. Resource-bound workloads and evidence

A slowdown can be caused by different limiting resources. These are hypotheses to test, not diagnoses from a single chart.

| Possible limit | Evidence to inspect | Common confounders |
|---|---|---|
| CPU-bound | CPU busy/throttled time rises; per-unit CPU cost; throughput plateaus | A lock or I/O wait can coexist with moderate CPU |
| Memory-bound | Working set pressure, paging, spills, allocation/GC pauses, OOM | Cache changes or larger payloads can alter memory and CPU together |
| I/O-bound | I/O latency, queue depth, IOPS/throughput limits, read/write mix | Storage latency may itself be caused by contention elsewhere |
| Network-bound | Link utilization, retransmits, packet loss, send/receive queues | Remote service latency or DNS/TLS setup may appear as network time |
| Lock-bound | Lock wait, blocked threads, contention profiles | Hot keys or long transactions may cause both locks and skew |
| Connection-limited | Pool exhaustion, connection wait, rejected acquisition, server connection cap | Increasing the pool can move overload to the database |
| Quota/admission-limited | Rejections, throttling, quota counters, unused local resources | Quotas may be per tenant, region, or time window |
| Downstream-limited | Dependency latency and saturation correlate with caller delay | Caller-side queueing may amplify a smaller downstream slowdown |

A useful diagnosis links time-aligned evidence: demand increased, a particular resource reached a limit, queue wait rose, and completion rate plateaued or fell. If the evidence is not sufficient to establish causation, label the explanation as a hypothesis and specify the next measurement.

## 12. Advanced overload behaviour and control mechanisms

### 12.1 Why excessive concurrency can hurt

More in-flight work can hide latency temporarily by keeping a resource busy, but excessive concurrency may increase:
- context switching and scheduler overhead;
- memory per request and garbage-collection pressure;
- lock contention and cache misses;
- downstream connection usage;
- queue depth and tail latency;
- wasted work when requests time out or clients disconnect.

The correct concurrency limit depends on the constrained resource and workload. Determine it through measurements rather than assuming “more concurrency means more throughput.”

### 12.2 Unbounded queues

An unbounded queue accepts work until some external limit (often memory or disk) is reached. When arrival rate persistently exceeds service rate, queue length grows without a finite steady-state value. Consequences include:
- increasing wait time;
- stale work that is no longer useful;
- memory/storage exhaustion;
- cascading timeouts and retries;
- long recovery time after a burst ends.

A bounded queue makes overload visible earlier, but it requires a defined policy for rejection, retry, prioritization, or backpressure. A full queue is a signal to protect the system, not automatically a reason to increase its size.

### 12.3 Backpressure

Backpressure communicates that a downstream stage cannot currently accept more work, so upstream producers should slow, pause, or buffer within explicit limits.

Good backpressure needs:
- a clear signal and propagation path;
- bounded buffers;
- timeout or cancellation semantics;
- fairness rules where tenants/workloads share resources;
- observability for paused producers and queue depth;
- a plan for sustained overload that cannot be solved by waiting.

Backpressure moves the pressure to an upstream component; it does not create capacity. If upstream cannot slow down, use admission control, durable buffering, prioritization, or explicit load shedding as appropriate.

### 12.4 Admission control and load shedding

**Admission control** decides whether new work may enter, based on current load, resource budgets, priority, or service objectives. **Load shedding** intentionally rejects or discards some work when the system cannot safely process all offered demand.

Trade-offs:
- reject early to preserve latency for accepted work;
- queue briefly when work can wait and the queue is bounded;
- shed low-priority or expired work before critical work;
- degrade optional features if the degraded mode is safe and explicit;
- protect dependencies with concurrency limits and bulkheads.

A rejected request is not successful throughput. Report offered, admitted, rejected, and completed rates to make the policy visible.

### 12.5 Timeouts and retries

Timeouts bound how long callers wait, but a client timeout does not guarantee the server stops processing. If a timed-out request is retried while the original still consumes resources, one logical action may create multiple attempts.

Retry storms happen when many clients retry together, increasing load during an incident. Safer patterns often include:
- bounded retries;
- exponential backoff with jitter;
- retry budgets;
- idempotency or deduplication for repeatable operations;
- clear distinction between retryable and permanent errors;
- deadlines propagated through dependencies;
- cancellation where it is safe and supported.

Retries can improve recovery from transient faults but worsen sustained overload. Test retry behaviour under failure, not only in the healthy case.

### 12.6 Fairness and priority

A single shared queue can allow a noisy tenant or expensive workload to dominate resources. Fair scheduling, per-tenant quotas, weighted priorities, or separate pools can protect critical work, but may reduce overall utilization or delay low-priority jobs.

Document:
- which work is prioritized and why;
- whether starvation is possible;
- per-tenant or per-class limits;
- what happens when every class is overloaded;
- how fairness is measured.

## 13. Measurement and diagnosis workflow

Use this sequence to avoid confusing correlation with causation.

1. **Define the question.** Which service objective is breached, for which workload and interval?
2. **Validate instrumentation.** Confirm units, clock alignment, sample coverage, success/failure definitions, and percentile method.
3. **Quantify demand.** Plot offered, admitted, completed, rejected, and timed-out rates.
4. **Inspect latency distribution.** Compare p50, p95, p99, and counts; split by request type and time.
5. **Inspect WIP and queues.** Measure active work, queue depth, oldest-item age, and backlog trend.
6. **Correlate resource evidence.** CPU, memory, I/O, network, locks, connection pools, quotas, and downstream latency.
7. **Form competing hypotheses.** Example: CPU saturation versus connection-pool limit versus a slow downstream dependency.
8. **Choose a discriminating test.** Change one variable or run a controlled load profile where safe.
9. **Re-measure.** Compare equivalent workloads and time windows; note any bottleneck movement.
10. **Update the capacity plan.** Feed measured sustainable rates and peak behaviour back into Topic 01 assumptions.

### 13.1 Warning signals

The values below are example signal types; thresholds must be derived from service objectives and measured behaviour.

- p95/p99 latency rises while throughput plateaus.
- Queue depth or oldest-item age increases across consecutive intervals.
- Completion rate stays below admitted arrival rate for a sustained period.
- Offered load rises but admitted rate remains flat and rejections increase.
- Timeout and retry rates rise together.
- A connection pool or worker queue is saturated while downstream capacity is unused.
- CPU throttling, memory pressure, I/O wait, network drops, or lock wait rises in the same interval as latency.
- Backlog drain time exceeds the recovery objective.
- Performance changes materially under one workload class or tenant.
- A load generator reports fewer actual sends than its configured arrival rate.

## 14. Python implementation: reproducible metrics and queue calculations

The following code uses only the Python standard library. It deliberately implements simple arithmetic and summaries rather than a full queueing simulator. It validates inputs and states assumptions. Save it as `queueing_metrics.py`.

```python
from __future__ import annotations

from math import ceil
from statistics import mean
from typing import Iterable


def _finite_nonnegative(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric")
    if value < 0 or value != value or value == float("inf") or value == float("-inf"):
        raise ValueError(f"{name} must be finite and non-negative")


def throughput(completed_units: float, interval_seconds: float) -> float:
    """Completed units per second over a positive interval."""
    _finite_nonnegative("completed_units", completed_units)
    if isinstance(interval_seconds, bool) or not isinstance(interval_seconds, (int, float)):
        raise TypeError("interval_seconds must be numeric")
    if interval_seconds <= 0 or not math_is_finite(interval_seconds):
        raise ValueError("interval_seconds must be finite and positive")
    return completed_units / interval_seconds


def math_is_finite(value: float) -> bool:
    return value == value and value not in (float("inf"), float("-inf"))


def latency_summary(latencies_ms: Iterable[float]) -> dict[str, int | float]:
    """
    Summarize observed latencies in milliseconds.
    Percentiles use the nearest-rank estimator: sorted[ceil(p*n)-1].
    Requires at least one finite, non-negative numeric observation.
    This estimator is intentionally simple; small-sample percentiles are coarse.
    """
    values = list(latencies_ms)
    if not values:
        raise ValueError("latencies_ms must contain at least one observation")
    for value in values:
        _finite_nonnegative("latency", value)
    ordered = sorted(values)

    def nearest_rank(p: float) -> float:
        return ordered[ceil(p * len(ordered)) - 1]

    return {
        "count": len(ordered),
        "mean_ms": mean(ordered),
        "p50_ms": nearest_rank(0.50),
        "p95_ms": nearest_rank(0.95),
        "p99_ms": nearest_rank(0.99),
        "max_ms": ordered[-1],
    }


def littles_law(throughput_per_second: float, average_time_seconds: float) -> float:
    """Average WIP = throughput (units/s) × average time in system (s)."""
    _finite_nonnegative("throughput_per_second", throughput_per_second)
    _finite_nonnegative("average_time_seconds", average_time_seconds)
    return throughput_per_second * average_time_seconds


def backlog_after_interval(
    starting_backlog: float,
    arrival_rate_per_second: float,
    processing_rate_per_second: float,
    interval_seconds: float,
) -> float:
    """
    Fluid approximation: backlog changes by (arrival - processing) × time.
    Processing cannot reduce the queue below zero; this function assumes the
    supplied processing rate is work actually available to this queue.
    """
    _finite_nonnegative("starting_backlog", starting_backlog)
    _finite_nonnegative("arrival_rate_per_second", arrival_rate_per_second)
    _finite_nonnegative("processing_rate_per_second", processing_rate_per_second)
    _finite_nonnegative("interval_seconds", interval_seconds)
    net = (arrival_rate_per_second - processing_rate_per_second) * interval_seconds
    return max(0.0, starting_backlog + net)


def drain_time_seconds(
    backlog_units: float,
    processing_rate_per_second: float,
    continuing_arrival_rate_per_second: float = 0.0,
) -> float:
    """
    Ideal drain time with constant rates.
    Returns 0 for no backlog, infinity if net drain capacity is <= 0.
    """
    _finite_nonnegative("backlog_units", backlog_units)
    _finite_nonnegative("processing_rate_per_second", processing_rate_per_second)
    _finite_nonnegative("continuing_arrival_rate_per_second", continuing_arrival_rate_per_second)
    if backlog_units == 0:
        return 0.0
    net = processing_rate_per_second - continuing_arrival_rate_per_second
    if net <= 0:
        return float("inf")
    return backlog_units / net


def mm1_mean_time_seconds(arrival_rate: float, service_rate: float) -> float:
    """
    M/M/1 mean time in system = 1 / (service_rate - arrival_rate).
    Assumes Poisson arrivals, exponential service, one server, infinite queue,
    independent arrivals/service, and arrival_rate < service_rate.
    """
    _finite_nonnegative("arrival_rate", arrival_rate)
    _finite_nonnegative("service_rate", service_rate)
    if service_rate <= 0:
        raise ValueError("service_rate must be positive")
    if arrival_rate >= service_rate:
        raise ValueError("M/M/1 steady state requires arrival_rate < service_rate")
    return 1.0 / (service_rate - arrival_rate)


if __name__ == "__main__":
    summary = latency_summary([20, 20, 20, 20, 2000])
    print(f"Throughput: {throughput(18_000, 300):.2f} events/s")
    print(f"Little's Law WIP: {littles_law(200, 0.050):.2f} requests")
    print(f"Backlog after 120 s: {backlog_after_interval(10_000, 800, 650, 120):.0f} events")
    print(f"Drain time: {drain_time_seconds(28_000, 700, 500):.0f} s")
    print(f"M/M/1 mean time at 90% utilisation: {mm1_mean_time_seconds(90, 100) * 1000:.0f} ms")
    print(f"Latency summary: {summary}")
```

### 14.1 Automated assertions

Save as `test_queueing_metrics.py` beside the module and run `python test_queueing_metrics.py`.

```python
import math

from queueing_metrics import (
    backlog_after_interval,
    drain_time_seconds,
    latency_summary,
    littles_law,
    mm1_mean_time_seconds,
    throughput,
)

assert throughput(18_000, 300) == 60
assert math.isclose(littles_law(200, 0.050), 10.0)

assert backlog_after_interval(10_000, 800, 650, 120) == 28_000
assert drain_time_seconds(28_000, 700, 500) == 140
assert drain_time_seconds(0, 700, 500) == 0
assert math.isinf(drain_time_seconds(100, 100, 100))
assert math.isinf(drain_time_seconds(100, 90, 100))

summary = latency_summary([20, 20, 20, 20, 2000])
assert summary["count"] == 5
assert math.isclose(summary["mean_ms"], 416.0)
assert summary["p50_ms"] == 20
assert summary["p95_ms"] == 2000
assert summary["p99_ms"] == 2000
assert summary["max_ms"] == 2000

assert math.isclose(mm1_mean_time_seconds(50, 100), 0.02)
assert math.isclose(mm1_mean_time_seconds(90, 100), 0.10)
assert math.isclose(mm1_mean_time_seconds(95, 100), 0.20)

# A queue cannot have a negative backlog in the fluid helper.
assert backlog_after_interval(10, 0, 100, 10) == 0

# Boundary and invalid-input tests.
assert throughput(0, 1) == 0
assert math.isclose(littles_law(0, 10), 0.0)
assert latency_summary([0]) == {
    "count": 1, "mean_ms": 0, "p50_ms": 0, "p95_ms": 0, "p99_ms": 0, "max_ms": 0
}
assert backlog_after_interval(0, 5, 5, 10) == 0
assert backlog_after_interval(10, 0, 100, 10) == 0
assert math.isclose(drain_time_seconds(100, 10, 0), 10.0)

invalid_calls = [
    lambda: throughput(10, 0),
    lambda: throughput(10, float("inf")),
    lambda: throughput(-1, 1),
    lambda: throughput(True, 1),
    lambda: littles_law(-1, 1),
    lambda: littles_law(1, float("nan")),
    lambda: littles_law(True, 1),
    lambda: latency_summary([]),
    lambda: latency_summary([10, float("nan")]),
    lambda: latency_summary([10, float("inf")]),
    lambda: latency_summary([10, -1]),
    lambda: latency_summary([10, True]),
    lambda: backlog_after_interval(0, 1, 1, -1),
    lambda: drain_time_seconds(-1, 10),
    lambda: mm1_mean_time_seconds(100, 100),
    lambda: mm1_mean_time_seconds(-1, 100),
    lambda: mm1_mean_time_seconds(1, float("inf")),
]
for call in invalid_calls:
    try:
        call()
    except (TypeError, ValueError):
        pass
    else:
        raise AssertionError("Expected invalid input to raise TypeError or ValueError")

print("All queueing-metrics assertions passed.")
```

### 14.2 Expected outputs

Running `python queueing_metrics.py` should print:

```text
Throughput: 60.00 events/s
Little's Law WIP: 10.00 requests
Backlog after 120 s: 28000 events
Drain time: 140 s
M/M/1 mean time at 90% utilisation: 100 ms
Latency summary: {'count': 5, 'mean_ms': 416, 'p50_ms': 20, 'p95_ms': 2000, 'p99_ms': 2000, 'max_ms': 2000}
```

The tests use a nearest-rank percentile estimator. Different libraries may produce different percentile values for small samples because their interpolation rules differ; document the method used. The Python model is an arithmetic aid, not a replacement for telemetry or load testing.

## 15. Practical exercises

Try each exercise before checking its validation targets. All values are illustrative.

### 15.1 Beginner — API service

A fictional API completes 18,000 requests over five minutes. Its average end-to-end latency is 40 ms.

Tasks:
1. Calculate throughput in requests/s.
2. Use Little's Law to estimate average in-flight requests for a stable interval.
3. Explain why the estimate does not tell you p95 latency.
4. List the boundaries and assumptions you would verify.

**Validation targets:** throughput is 60 requests/s. Estimated average WIP is \(60 \times 0.040 = 2.4\) requests, provided the throughput and latency refer to the same system boundary and stable interval.

### 15.2 Intermediate — ingestion backlog

A fictional event pipeline starts with a backlog of 50,000 events. During a 10-minute period, arrivals average 900 events/s and processing averages 1,000 events/s.

Tasks:
1. Calculate the net backlog change.
2. Calculate the ideal backlog after ten minutes.
3. If arrivals continue at 900 events/s and processing capacity remains 1,000 events/s, estimate drain time from that final backlog.
4. Explain which real-world factors could make the estimate wrong.

**Validation targets:** net change is \((900-1000)\times600=-60,000\) events. Since this exceeds the initial backlog, the queue reaches zero before the interval ends; it cannot become negative. Ideal drain time from the starting backlog is \(50,000/100=500\) seconds. After clearing, the system may be idle unless new arrivals are available.

### 15.3 Advanced — diagnose a latency regression

A fictional analytics platform has p50 latency steady at 80 ms, p99 latency increasing from 400 ms to 2,500 ms, completion throughput flat, queue age increasing, and retry rate rising. CPU is moderate, but connection-pool wait increases.

Tasks:
1. Separate observations from hypotheses.
2. Identify at least three competing hypotheses.
3. Propose measurements or controlled tests that distinguish them.
4. Explain how retries could worsen the incident.
5. Recommend immediate overload controls and longer-term capacity/architecture follow-up.
6. State what evidence would cause you to reject your leading hypothesis.

**Expected output:** a diagnosis note that does not declare the connection pool to be the root cause solely because its wait time rose. Establish timing, saturation, dependency behaviour, and causal evidence.

## 16. Industry-style diagnosis scenarios and trade-offs

All organizations and thresholds are fictional and illustrative.

| Scenario | Observations | Candidate explanations | Useful next evidence |
|---|---|---|---|
| Throughput flat; p99 and queue age rise | Completion rate stops increasing as offered load grows | Resource saturation, connection cap, downstream slowdown | Offered/admitted/completed rates, queue waits, resource and dependency metrics |
| Low average latency; occasional severe tails | p50 stable but p99 high | Variable service times, retries, noisy neighbour, lock contention | Per-request traces, request-class breakdown, retry counts, lock/pool waits |
| Backlog grows during recovery | Arrival rate exceeds processing rate | Reduced capacity, competing batch work, throttling, dependency limit | Time-aligned rates, resource demand, foreground-vs-backfill measurements |
| More workers reduce throughput | Higher concurrency correlates with lower completions | Lock contention, memory pressure, connection exhaustion, context switching | Controlled concurrency sweep, per-resource metrics, error and wait time |
| Load test misses configured arrival rate | Generator sends fewer requests than intended | Client CPU/network bottleneck, closed-loop feedback, generator limits | Scheduled vs actual sends, generator utilization, client-side latency accounting |
| Retries rise during a slowdown | More attempts per logical request | Transient errors or retry amplification | Attempt-level vs logical-request rates, backoff distribution, server work after client timeout |

### 16.1 Example trade-off matrix

| Control | Benefit | Cost / risk | Use when |
|---|---|---|---|
| Increase concurrency | Can use idle parallel capacity | Can increase contention, memory use, and tail latency | Measurements show parallel capacity is available and bottleneck permits it |
| Increase queue size | Absorbs a finite burst | Adds wait time and memory/storage pressure; delays overload visibility | Burst is bounded and delayed processing remains useful |
| Bound queue and reject | Protects service and memory; explicit overload | Some offered work is rejected | Service objectives require protecting accepted work |
| Apply backpressure | Slows upstream production to match downstream capacity | Pressure moves upstream; producers may need buffering or pause support | Upstream can react safely |
| Limit retries | Reduces amplification during incidents | Some transient failures may be exposed sooner | Retry traffic materially contributes to load |
| Shed low-priority work | Preserves critical requests | Lower-priority work is delayed or lost | Priorities are explicit and business-approved |
| Add capacity | May increase sustainable throughput | Lead time, cost, and possible bottleneck movement | A measured resource limit is the constraint and added capacity improves it |

## 17. Common mistakes and diagnostic guidance

| Mistake | Why it is wrong | Better practice |
|---|---|---|
| Treating throughput as latency | Rate and elapsed time have different units and meanings | Track both under a defined workload |
| Using service time as end-to-end latency | Omits queueing and other stages | Instrument queue wait and full request boundary |
| Applying Little's Law to mismatched windows | Inputs do not describe the same system regime | Align boundary, work unit, and observation interval |
| Using offered rate as completed throughput | Rejections, failures, and backlog change the relationship | Track offered, admitted, completed, successful, and rejected rates |
| Inferring p99 from mean latency | The distribution and tail are unknown | Measure a latency histogram or raw sample with adequate coverage |
| Averaging percentile values across hosts | Percentiles are not generally additive or linearly aggregatable | Merge compatible histograms or compute from combined observations |
| Adding component p95 values as exact end-to-end p95 | Component tails may occur on different requests and be correlated | Measure end-to-end requests or use a justified model |
| Increasing concurrency blindly | Can increase contention and memory/connection pressure | Run a controlled concurrency sweep and observe throughput plus tail latency |
| Making queues unbounded | Backlog and wait can grow without bound under sustained overload | Bound queues and define backpressure/rejection policy |
| Treating timeouts as cancellation | Server work may continue after client gives up | Verify cancellation and measure attempts separately |
| Retrying immediately without limits | Can create retry storms | Use bounded retries, backoff, jitter, budgets, and idempotency where needed |
| Treating correlation as root cause | Multiple metrics can move because of a third factor | State hypotheses and run discriminating tests |
| Trusting configured load in a load test | Generator may deliver less than requested | Record scheduled and actual send rates and generator health |
| Assuming an M/M/1 prediction applies directly | Real workloads often violate its assumptions | Use it for intuition, then validate with representative tests |

## 18. Reusable deliverables

### 18.1 Workload and metric definition sheet

| Field | Definition / value | Unit / interval | Source | Notes / confidence |
|---|---|---|---|---|
| Workload and owner |  |  |  |  |
| Work unit |  |  |  |  |
| Offered arrival pattern |  |  |  |  |
| Admitted rate |  |  |  |  |
| Completed / successful rate |  |  |  |  |
| Latency boundary |  |  |  |  |
| p50 / p95 / p99 method |  |  |  |  |
| Queue / WIP boundary |  |  |  |  |
| Concurrency limit |  |  |  |  |
| Service objectives |  |  |  |  |
| Resource signals |  |  |  |  |
| Measurement gaps |  |  |  |  |

### 18.2 Throughput, latency, and concurrency analysis

Document:
1. Measurement window and workload mix.
2. Offered, admitted, completed, successful, rejected, and timed-out rates.
3. p50, p95, p99, maximum, sample count, and percentile method.
4. Average WIP and the Little's Law cross-check.
5. Queue depth, oldest-item age, and backlog trend.
6. Resource and dependency measurements aligned to the same time window.
7. Conclusions supported by observations, plus unresolved hypotheses.

### 18.3 Queue/backlog calculation

| Interval | Start backlog | Arrivals/s | Processed/s | Duration | End backlog | Net drain rate | Estimated drain time |
|---|---:|---:|---:|---:|---:|---:|---:|
|  |  |  |  |  |  |  |  |

Record whether arrivals continue during drain and whether rates are measured, averaged, or assumed.

### 18.4 Diagnosis note template

- **Symptom and impact:**
- **Service objective affected:**
- **Time window and workload:**
- **Direct observations:**
- **Supported inferences:**
- **Competing hypotheses:**
- **Evidence for/against each hypothesis:**
- **Next discriminating test:**
- **Immediate safeguards:**
- **Longer-term capacity or architecture actions:**
- **Unknowns and confidence:**
- **Revisit trigger / owner:**

### 18.5 Capacity and overload warning register

| Signal | Definition | Threshold / duration | Owner | Action |
|---|---|---|---|---|
| Tail latency | p95/p99 relative to objective |  |  |  |
| Queue growth | Backlog or oldest-item age trend |  |  |  |
| Throughput plateau | Completed rate stops rising as offered load rises |  |  |  |
| Rejection rate | Rejected/admission-denied work over a stated interval |  |  |  |
| Retry amplification | Attempts per logical request or retry rate |  |  |  |
| Resource saturation | CPU, memory, I/O, network, locks, connections, quota |  |  |  |
| Catch-up runway | Estimated backlog drain time vs recovery objective |  |  |  |

## 19. Mastery criteria and completion gate

### 19.1 Mastery criteria

You are ready to proceed when you can:
- Explain and measure throughput, latency, service time, queue wait, concurrency, WIP, utilisation, and saturation with explicit boundaries.
- Interpret p50/p95/p99 and explain why mean latency is insufficient.
- Apply Little's Law to compatible long-run averages and state its limitations.
- Calculate queue growth, ideal drain time, and catch-up capacity with consistent units.
- Explain why queueing delay can grow rapidly near saturation.
- Distinguish open and closed load models and identify when a test generator under-delivers.
- Diagnose resource-bound hypotheses using time-aligned evidence without claiming causation from correlation alone.
- Explain how backpressure, bounded queues, admission control, timeouts, retries, and load shedding change overload behaviour.
- Produce reproducible calculations, tests, and a diagnosis note separating observations from hypotheses.

### 19.2 Completion checklist

- [ ] Workload and metric definition sheet completed.
- [ ] Throughput, latency, and concurrency analysis includes offered/admitted/completed rates.
- [ ] Percentiles, sample count, and percentile method documented.
- [ ] Little's Law calculation uses a consistent boundary and time window.
- [ ] Queue/backlog calculation includes arrival rate, processing rate, interval, and drain assumptions.
- [ ] Open/closed workload implications documented.
- [ ] At least three competing diagnosis hypotheses evaluated.
- [ ] Warning signals have measurable definitions and follow-up actions.
- [ ] Python example and automated assertions executed successfully in the learner's environment.
- [ ] Remaining measurement gaps and uncertainty documented.

**Completion gate:** every reported metric has a definition, unit, and time window. Calculations can be reproduced. The diagnosis note distinguishes observed facts from hypotheses. You can explain what the evidence does not establish.

## 20. Summary and transition to Topic 03

Throughput tells you how much work completes per unit time; latency tells you how long work takes; concurrency and WIP describe how much work is in progress; queues reveal mismatches between admitted arrivals and processing capacity. Little's Law connects average WIP, throughput, and time when the boundaries and conditions are consistent. Queueing models explain why delays can rise sharply near saturation, but their assumptions must be checked before using their predictions.

The operational discipline is to define metrics precisely, align measurements, observe rates and latency distributions together, inspect queues and resource limits, test competing explanations, and feed measured sustainable capacity back into Topic 01.

**Readiness transition:** Topic 03, `03-query-performance-and-data-locality.md`, uses these measurement habits to investigate query scans, joins, data movement, pruning, and locality. Bring forward your latency distribution, throughput/queue evidence, workload definition, and unresolved bottleneck hypotheses.
