# Caching, Materialization and Serving Trade-offs

## 1. Purpose, scope, and learning outcomes

### Purpose

This lesson explains how to reduce repeated computation and backend work without losing control of freshness, correctness, availability, or cost. It progresses from basic cache behaviour to quantitative serving decisions, materialisation economics, consistency contracts, and failure planning.

The central principle is:

> Avoid repeated work only when the saved work is worth the cost and the resulting data remains correct enough for the consumer's decision.

### Scope

This is a vendor-neutral architecture lesson, not an implementation manual for every cache, query engine, serving database, or materialised-view product. It focuses on workload reasoning, decision criteria, reproducible arithmetic, failure modes, and the evidence required to justify an architecture.

All numeric values and prices in examples are **illustrative assumptions**, not production benchmarks, market prices, or recommended service-level targets. Replace them with measured workload and cost data before making a production decision.

### Learning outcomes

By the end, you should be able to:

1. Distinguish caching, materialisation, and compute-on-demand.
2. Explain cache keys, hits, misses, eviction, TTL, invalidation, and cache capacity.
3. Calculate hit ratio, effective mean latency under stated assumptions, and backend request load.
4. Explain why hit ratio alone cannot prove latency, correctness, or availability.
5. Set freshness contracts and compare TTL, scheduled refresh, and event-driven invalidation.
6. Recognise cache stampedes, cache penetration, hot keys, cold starts, and cache-outage risks.
7. Compare full and incremental materialisation, refresh cadence, storage, and compute costs.
8. Choose serving patterns for point lookups, repeated aggregates, ad hoc analysis, and freshness-sensitive decisions.
9. Quantify alternatives using explicit workload, reuse, freshness, and cost assumptions.
10. Produce a requirements profile, decision matrix, freshness/invalidation policy, quantitative analysis, and evidence-based recommendation.

### The architectural question

A cache or materialised dataset is not automatically an optimisation. It moves work and risk around:

- **Potential gains:** lower read latency, fewer repeated queries, less load on a source system, more predictable serving.
- **Potential costs:** memory or storage, refresh compute, invalidation logic, operational complexity, and stale or inconsistent answers.
- **Potential failure modes:** cache outage, miss-path overload, failed refresh, partial publication, stale replicas, and data-deletion gaps.

The decision is justified only if the total design meets the consumer's correctness and freshness contract and improves a measured outcome.

---

## 2. Prerequisites and links to Topics 02–04

The module roadmap specifies Topic 05 prerequisites as **Sequence 3–4 and P9**. Sequence 3 is query performance and data locality; Sequence 4 is scaling, partitioning, sharding, and hotspots. P9 is the serving-stores and materialised-views prerequisite, referenced by the roadmap as `../09-Streaming-and-Real-Time-Data-Architecture/06-real-time-serving-stores-and-materialized-views.md`.

If that P9 source is not available in your working repository, treat the following as the minimum recap rather than assuming it has been completed.

### Topic 02 — Throughput, latency, concurrency, and queueing

Connect caching to:

- arrival rate and request rate;
- average versus percentile latency;
- queue growth when service capacity is exceeded;
- concurrency and the cost of a miss path;
- why reducing average work may still leave tail latency poor.

A cache can lower backend request rate, but a stampede or a cache outage can abruptly send the full request rate to the backend. Use the miss-path capacity, not only normal hit-path performance, when designing resilience.

### Topic 03 — Query performance and data locality

Connect materialisation to:

- expensive scans, joins, aggregations, and repeated transformations;
- partition pruning and data movement;
- the difference between optimising a query and avoiding its repeated execution;
- the cost and correctness of maintaining a derived result.

Before materialising a slow query, first determine whether its plan, filters, joins, layout, or data movement can be improved. Precomputing a needlessly expensive query can preserve avoidable cost in the refresh pipeline.

### Topic 04 — Scaling, partitioning, sharding, and hotspots

Connect serving design to:

- hot keys and skewed access patterns;
- partitioning and routing of cache entries or derived data;
- the cost of spreading requests across many shards;
- cache capacity and rebalancing;
- the possibility that a single popular key dominates load even when average traffic looks safe.

Adding shards does not necessarily solve a hot key. Caching, request coalescing, replication, or workload redesign may be required, and each option has consistency and cost consequences.

### Prerequisite checkpoint

You should be able to answer:

- What is the baseline request rate, peak rate, and latency distribution?
- Which operation dominates query cost?
- Is load uniformly distributed, or are there hot keys/partitions?
- What is the source system's safe miss-path capacity?
- Which freshness and correctness constraints come from the business requirement rather than technical convenience?

If these are unknown, record them as assumptions and define how to measure them.

---

## 3. Beginner explanations and examples

### 3.1 A cache is a reuse layer

Imagine a support application repeatedly asks for the same product description. Without a cache, every request reads the primary store and may repeat expensive joins or transformations. With a cache, the application stores a copy of a recently retrieved value under a key. Later requests may reuse that value rather than recomputing or rereading it.

A cache is usually optimised for **reuse and quick lookup**. Its contents may be temporary, incomplete, or safe to reconstruct from an authoritative source. A cache should not silently become the only durable copy of data unless the architecture explicitly defines it as a system of record—which is a different design.

### 3.2 Materialisation is precomputation

Imagine a dashboard repeatedly computes daily sales by region from billions of transaction rows. A materialised aggregate stores the already-computed regional totals. Reads become cheaper because the expensive aggregation was performed earlier, but the aggregate must be refreshed when source data changes.

Materialisation is usually about **storing the result of a computation**. It can be durable and governed, but it still has lineage, refresh, schema-evolution, and correctness requirements.

### 3.3 The desk-and-filing analogy

- **Cache:** keep frequently used documents on your desk for quick access. The copy can be outdated and may be discarded.
- **Materialised result:** prepare and file a summary report in advance. The report is quick to consult, but preparing and updating it takes work.
- **Compute on demand:** create the report whenever someone asks. It reflects the selected source state, subject to source consistency, but may take longer and cost more per request.

### 3.4 Three approaches compared

| Approach | Best fit when | Main benefit | Main cost or risk |
|---|---|---|---|
| Cache | Values/results are reused and tolerate a defined freshness window | Cheap repeated reads; lower backend load | Eviction, staleness, invalidation and miss-path risk |
| Materialised view or derived dataset | A costly computation is reused across consumers or requests | Avoids repeating scans, joins, or aggregates | Refresh compute, storage, lag, dependency management |
| Compute on demand | Query shapes vary, reuse is low, or the required source snapshot can be queried within budget | Flexible and avoids maintaining a derived copy | Repeated compute, variable latency, source load; freshness is limited by source/replica semantics |

These are not mutually exclusive. A serving architecture may use a materialised aggregate as the cache's backing source, with a cache in front of it and authoritative source data behind both. **On-demand does not automatically mean perfectly current:** the result reflects the snapshot and consistency semantics actually provided by the queried source, replica, and query engine. If the source is delayed or the read is served by a lagging replica, on-demand computation can still return lagging data.

### 3.5 Where caching can occur

- **Client or browser:** reduces repeat network requests, but may have device-specific state and security implications.
- **Application/process:** fast local reuse, but separate instances can disagree and each consumes memory.
- **Shared serving cache:** reused across application instances, but introduces a network hop and a dependency.
- **Query engine:** reuses result or intermediate data according to engine-specific rules.
- **Storage or filesystem layer:** reuses blocks or pages; it may be transparent to the application.
- **CDN/edge:** serves geographically distributed content near consumers; invalidation and regional consistency need consideration.

The layer determines what the key means, which consumers share the entry, how invalidation is propagated, and what happens when the layer fails.

---

## 4. Core terminology and fundamentals

### 4.1 Cache lookup lifecycle

A typical cache-aside lookup follows this flow:

1. Construct a key from the request's relevant dimensions.
2. Look up the key.
3. On a **hit**, return the cached entry if it is valid for the request.
4. On a **miss**, fetch or compute from the backing system.
5. Validate and store the result under the key, with metadata such as expiry or version.
6. Return the result and record telemetry.

A production implementation must also handle errors, timeouts, negative results, concurrent misses, authorization, and invalidation races.

### 4.2 Core terms

| Term | Definition | Operational question |
|---|---|---|
| Cache key | Identifier used to retrieve an entry | Does it include every dimension that changes the answer? |
| Cache entry | Stored value plus optional expiry, version, size, and metadata | How large is it and how is it validated? |
| Hit | A lookup returns a usable cached entry | Was the entry correct and fresh enough? |
| Miss | No usable entry is returned | Can the backing system absorb the load? |
| Hit ratio | Hits divided by eligible lookups over a defined window | Which lookups and failures are included? |
| Miss ratio | Misses divided by eligible lookups over the same window | Is this measured at the same cache layer? |
| Eviction | Removal to reclaim capacity or enforce policy | Which policy causes entries to leave? |
| TTL | Time-to-live: a policy expiry interval | From which event does the timer start? |
| Invalidation | Making an entry unusable after a change or policy event | How are all relevant copies invalidated? |
| Refresh | Recomputing or reloading an entry or derived result | Is publication atomic and is lag measured? |
| Staleness | Difference between served data state/time and the required current state/time | What stale window is acceptable? |
| Materialised view | Persisted result of a query or transformation | How is it refreshed and reconciled? |
| Freshness lag | Delay between source change/availability and the served result reflecting it | What is the measured lag distribution? |

### 4.3 Define hit ratio precisely

For a single cache layer and a measurement window:

\[
\text{hit ratio} = \frac{\text{usable cache hits}}{\text{eligible cache lookups}}
\]

\[
\text{miss ratio} = \frac{\text{eligible lookups that miss}}{\text{eligible cache lookups}}
\]

If every eligible lookup is classified as either hit or miss, the ratios sum to 1. State how timeouts, bypasses, errors, negative-cache hits, and requests excluded from caching are treated. A multi-tier cache needs separate ratios per tier and a clearly defined end-to-end metric.

**Denominator example:** over a five-minute window, a cache receives 120,000 eligible lookups; 96,000 return usable entries. Hit ratio = 96,000 / 120,000 = 80%; miss ratio = 24,000 / 120,000 = 20%. Do not divide hits by all application requests if only a subset actually reaches this cache.

A high hit ratio does **not** by itself prove:

- that the result is fresh or correct;
- that cache-hit latency meets a percentile target;
- that misses are fast enough;
- that a small number of misses are not extremely expensive;
- that the cache can survive an outage;
- that the ratio remains high under a different workload or after restart.

### 4.4 Cache keys and correctness

A key must distinguish requests that can legitimately return different answers. Depending on the application, key dimensions may include:

- tenant or customer;
- entity identifier;
- requested date range or time bucket;
- locale, currency, or unit;
- query filters and sort/order semantics;
- model, transformation, or schema version;
- authorization scope or policy version.

A missing dimension can cause cross-tenant leakage, incorrect aggregation, or an authorization bypass. A key with too many unique dimensions can reduce reuse and increase memory use. Canonicalise inputs and version keys when the interpretation of a result changes.

Never use a cache hit as a substitute for current authorization checks unless the design explicitly proves that the cached value and its access policy remain valid for that caller.

### 4.5 Cache capacity and eviction

A cache has finite memory or storage. A first-order capacity estimate is:

\[
\text{raw value bytes} \approx \text{entry count} \times \text{average value size}
\]

Actual capacity must also account for keys, metadata, allocator overhead, replication, fragmentation, and operational headroom. If 2 million entries average 1.5 KiB of value data, raw values alone require about 3,000,000 KiB (roughly 2.86 GiB using 1 GiB = 1,048,576 KiB). This is not a safe memory sizing figure; overhead and peak working-set behaviour remain unaccounted for.

Common eviction policies include least-recently-used (LRU), least-frequently-used (LFU), time-based expiry, and policy-specific admission/eviction. No policy is universally best. LRU can be poor for scan-heavy traffic; LFU can retain once-popular entries; a short TTL can churn an otherwise useful working set.

### 4.6 Cache patterns

| Pattern | How it works | Advantages | Risks / considerations |
|---|---|---|---|
| Cache-aside (lazy loading) | Application reads cache; on miss it reads source and populates cache | Simple; only requested keys are loaded | Miss storms, stale entries after writes, application owns logic |
| Read-through | Cache layer loads from source on miss | Centralises lookup/load path | Coupling to loader; failure semantics must be clear |
| Write-through | Write path updates source and cache synchronously or as part of a coordinated operation | Can reduce immediate stale reads | More write latency; partial failure/atomicity complexity |
| Write-behind / write-back | Cache accepts write and persists asynchronously | Low apparent write latency, can batch | Data-loss and ordering risks; needs durable queueing and recovery |
| Refresh-ahead | Popular entries refreshed before expected expiry | Reduces expiry misses for hot entries | Can refresh unused entries and increase load |
| Time-based TTL | Entry expires after configured interval | Simple bound on cache residence time | Expiry does not itself guarantee source freshness or coordinated invalidation |
| Event-driven invalidation | Source change emits an event that invalidates or updates cache | Can reduce staleness | Event loss, ordering, duplicate delivery, consumer lag |
| Versioned keys | New data version gets a new key; readers switch to current version | Safer cutover and reduced delete races | Old entries consume space until reclaimed; version pointer must be correct |
| Negative caching | Cache a confirmed “not found” or safe negative result | Reduces repeated lookups for absent keys | Newly created records can remain hidden until expiry/invalidation |

Pattern choice depends on write frequency, read reuse, acceptable staleness, failure behaviour, and how writes are coordinated. A read-heavy, slowly changing reference dataset may suit long-lived caching; a balance or risk decision may require stronger consistency and a bypass or authoritative read.

### 4.7 TTL, invalidation, and refresh are different

- **TTL** makes an entry expire after a duration measured from a defined event, often cache insertion or refresh.
- **Invalidation** reacts to a state change or policy event and marks an entry unusable.
- **Refresh** obtains or computes a new value and publishes it.

TTL is a safety net, not proof of freshness. If a source changes immediately after a cache entry is populated, a TTL of 60 seconds can permit nearly 60 seconds of stale residence, plus propagation and read-path delays. If refresh itself is delayed or fails, a nominal schedule is not a guarantee.

For scheduled materialisation every \(T\) minutes, with successful refreshes and source updates occurring uniformly between refreshes, the average schedule-induced lag is approximately \(T/2\); the worst schedule-induced lag approaches \(T\). Add source ingestion delay, refresh runtime, queueing, and publication delay for an end-to-end freshness bound. If updates are bursty or correlated with the refresh schedule, the \(T/2\) expectation may not hold.

---

## 5. Worked quantitative examples

Every example states its assumptions. The arithmetic is a model to be validated against measured data, not a benchmark prediction.

### 5.1 Hit ratio, mean latency, and backend load

Assume one cache tier receives 1,000 eligible requests/second. Over the measurement window:

- hit ratio \(h = 0.90\);
- cache-hit service time \(t_c = 2\) ms;
- backend service time for a miss \(t_b = 100\) ms;
- each miss produces exactly one backend request;
- the rates and times are stable, and the model ignores queueing, retries, parallel fan-out, and network variance.

Expected miss rate:

\[
R_{miss} = R(1-h) = 1000 \times 0.10 = 100\ \text{requests/s}
\]

Expected hit rate:

\[
R_{hit} = Rh = 1000 \times 0.90 = 900\ \text{requests/s}
\]

A simple weighted mean service-time estimate is:

\[
\bar{t} = h t_c + (1-h)t_b
= 0.90(2) + 0.10(100) = 11.8\ \text{ms}
\]

This is a **weighted mean approximation**, not a percentile-latency prediction. It assumes the hit and miss times represent comparable end-to-end service-time components and ignores queueing. If miss requests wait behind other misses, actual mean and tail latency can be much worse.

Sensitivity to hit ratio under the same assumptions:

| Hit ratio | Hit rate at 1,000 req/s | Miss/backend rate | Weighted mean estimate |
|---:|---:|---:|---:|
| 90% | 900 req/s | 100 req/s | 11.8 ms |
| 75% | 750 req/s | 250 req/s | 26.5 ms |
| 50% | 500 req/s | 500 req/s | 51.0 ms |
| 0% | 0 req/s | 1,000 req/s | 100.0 ms |

The backend-load reduction relative to a design where every request reaches the backend is \(1-h\) only under the one-miss/one-backend-request assumption. If a miss fans out to five queries, backend query count is not simply application request count times miss ratio.

### 5.2 A high hit ratio can hide expensive misses

Assume 99% of 10,000 requests in a window hit a cache, and the 1% misses each trigger a 20-query fan-out.

- Eligible cache lookups: 10,000
- Hits: 9,900
- Misses: 100
- Hit ratio: 99%
- Backend query count caused by misses: \(100 \times 20 = 2,000\)

A 99% hit ratio may still leave 2,000 backend queries per window. Track miss cost and fan-out as well as hit ratio.

### 5.3 Materialisation economics

Compare one day of on-demand computation with a materialised result.

Illustrative assumptions:

- 5,000 reads/day;
- each live query costs \$0.04 in attributable compute;
- one daily refresh costs \$30;
- storage and serving of the materialised result cost \$2/day;
- correctness, engineering, monitoring, and failure-recovery costs are not included in the initial simplified comparison.

On-demand compute:

\[
C_{live} = 5{,}000 \times \$0.04 = \$200/\text{day}
\]

Materialised approach:

\[
C_{mat} = \$30 + \$2 = \$32/\text{day}
\]

Simplified difference:

\[
\Delta C = C_{live} - C_{mat} = \$168/\text{day}
\]

This does **not** establish net production savings until all material refreshes, retries, storage, serving, data transfer, and operational costs are included. Also check whether the live-query cost is truly avoidable and whether the materialised output meets the freshness contract.

A general decision inequality is:

\[
N C_{live} > C_{refresh} + C_{storage} + C_{serve} + C_{maintenance}
\]

where all costs cover the same time period and use the same currency/accounting basis. Include expected failure and operational costs when they are material.

### 5.4 Refresh frequency and cost

Assume a full refresh costs \$12 per run and runs every \(T\) minutes, continuously across a 24-hour day. Ignore retries and orchestration overhead.

Runs/day = \(1440/T\).

| Refresh interval | Runs/day | Refresh cost/day | Idealised average schedule-induced lag |
|---:|---:|---:|---:|
| 5 min | 288 | \$3,456 | 2.5 min |
| 15 min | 96 | \$1,152 | 7.5 min |
| 60 min | 24 | \$288 | 30 min |
| 240 min | 6 | \$72 | 120 min |

These costs are intentionally illustrative and demonstrate the shape of the trade-off, not a recommended interval. The table's average-lag estimate assumes refreshes complete successfully, updates arrive uniformly relative to the schedule, and other sources of lag are zero. Real end-to-end lag is larger if ingestion, processing, or publication is delayed.

If a full refresh costs \$12 each time, changing from 60-minute to 15-minute refresh multiplies scheduled refresh count and cost by four. It also reduces idealised schedule-induced average lag from 30 to 7.5 minutes. Whether that is worthwhile depends on the business value of fresher results.

### 5.5 Incremental versus full refresh

Assume the full refresh processes the entire dataset and costs \$12. An incremental refresh processes changed data and costs \$2 per run, but requires a full reconciliation costing \$12 once per day. With 15-minute refresh:

- Incremental runs/day = 96
- Incremental refresh cost/day = \(96 \times \$2 = \$192\)
- Daily reconciliation = \$12
- Total modelled incremental cost = \$204/day
- Full refresh cost/day = \(96 \times \$12 = \$1,152\)

Under these illustrative assumptions, incremental refresh is \$948/day lower in direct refresh cost. This comparison is incomplete if incremental processing has significant state-management, late-arrival, deletion, deduplication, or operational costs. A cheaper incremental path that silently omits corrections is not an acceptable optimisation.

### 5.6 Freshness as an explicit contract

Suppose a dashboard may show data at most 20 minutes behind the authoritative source. A 15-minute schedule alone does not guarantee compliance. If ingestion takes up to 4 minutes, refresh processing takes up to 3 minutes, and publication takes up to 1 minute, the conservative sum can reach:

\[
15 + 4 + 3 + 1 = 23\ \text{minutes}
\]

This simple upper-bound composition exceeds the 20-minute contract. Options include reducing the interval, using event-driven/incremental updates, reducing processing duration, or revising the business requirement if stakeholders accept it. Do not call the 15-minute schedule “fresh within 15 minutes” without defining the lag origin and the other delays.

### 5.7 Storage estimate for a materialised result

Suppose a derived dataset contains 40 million rows with an average encoded row size of 240 bytes.

Raw payload estimate:

\[
40{,}000{,}000 \times 240 = 9.6 \times 10^9\ \text{bytes}
\]

That is about 9.6 GB in decimal units, before indexes, metadata, compression effects, replicas, retained versions, and backup copies. Use measured stored size for a mature design. A materialised table may be smaller than source data due to aggregation or compression, or larger due to indexes and multiple derived dimensions.

---

## 6. Intermediate decision-making and pattern selection

### 6.1 Start with the access pattern

Record, at minimum:

- request rate and peak-to-average ratio;
- read/write ratio;
- distinct keys and key popularity distribution;
- reuse distance or repeated-query frequency;
- result size and cardinality;
- query compute cost and backend fan-out;
- freshness and correctness requirements;
- required read-after-write behaviour;
- security and tenant boundaries;
- expected source and cache failure behaviour.

A high request rate alone does not justify caching. If every request asks for a unique key, reuse may be low. A lower-rate query may be an excellent materialisation candidate if it repeatedly scans a large dataset and the result can be shared by many consumers.

### 6.2 Selection guide

| Workload shape | Candidate approach | Why it may fit | Questions before choosing |
|---|---|---|---|
| Repeated reads of stable entity by ID | Cache-aside or read-through | Reuses values with low lookup cost | What is the maximum acceptable stale interval? |
| Repeated expensive aggregate over stable source | Materialised aggregate/view | Avoids repeating scan/join/aggregation | Can the refresh complete inside the freshness window? |
| Interactive ad hoc analysis with many query shapes | Optimised analytical query on demand | Avoids maintaining every possible result | Can the query engine meet latency and concurrency targets? |
| Current account balance or decision-critical risk state | Authoritative read or strongly controlled serving path | Incorrect stale answers may have direct consequences | Is a cached result allowed, and what consistency guarantee is required? |
| Text retrieval across documents | Search index, possibly with cache for repeated queries | Index serves retrieval semantics; cache reuses repeated results | How are document updates, ACL changes, and deletes propagated? |
| Feature/embedding lookup for online inference | Online serving store with selective cache | Low-latency point lookups can be critical | Is feature freshness, point-in-time correctness, or model-version alignment required? |
| Repeated dashboard query with a known freshness tolerance | Materialised view plus optional cache | Precomputation reduces repeated aggregation; cache absorbs bursts | Are refresh lag and cache staleness separately monitored? |
| Rare, unique, expensive query | On-demand, potentially with query-plan optimisation | Low reuse may not repay cache or refresh costs | Can work be bounded or results shared safely? |

### 6.3 Cache, materialise, or compute on demand: decision matrix

Score each option against requirements rather than using a universal ranking. Example scoring scale: 1 = poor fit, 3 = conditional, 5 = strong fit. The values below are **illustrative for a hypothetical read-heavy dashboard**, not general facts.

| Criterion | Cache-aside | Materialised view | On-demand query |
|---|---:|---:|---:|
| Repeated same-key lookups | 5 | 3 | 2 |
| Repeated expensive aggregate | 2 | 5 | 2 |
| Highly variable query shapes | 2 | 2 | 5 |
| Tight freshness with low write rate | 4, if invalidation is reliable | 3, if refresh meets the contract | 4, if source query is fast |
| Low operational complexity | 2 | 2 | 4 |
| Low read latency under predictable reuse | 5 | 4 | 2 |
| Low storage footprint | 3 | 2 | 5 |
| Tolerance of cache outage | Depends on backend headroom | Not applicable to cache alone | 5 if source capacity is sufficient |

Do not add scores mechanically unless you have defined criterion weights and evidence. Some requirements are hard gates, not tradeable points: privacy, authorization, correctness, and maximum staleness may disqualify an option regardless of its total score.

### 6.4 A practical decision sequence

1. **Establish the baseline.** Measure request rate, latency percentiles, query cost, backend load, reuse, and freshness.
2. **Optimise the underlying operation.** Fix avoidable scans, joins, skew, or poor key access first.
3. **Classify the result.** Is it a reusable entity value, a repeated query result, a costly aggregate, or an ad hoc query?
4. **Define a correctness contract.** Specify allowable staleness, read-after-write expectations, and access-control behaviour.
5. **Estimate benefit.** Model hit ratio, miss-path rate, avoided compute, refresh, storage, and serving cost.
6. **Design the miss and failure paths.** Include cache outage, cold start, stampede, refresh failure, and backend overload.
7. **Validate with realistic workload.** Use the observed key/query distribution, not uniform synthetic traffic unless that matches reality.
8. **Compare before and after.** Check latency percentiles, correctness, source load, and total cost.
9. **Record the decision.** Document assumptions, risks, owners, rollback, and evidence in an architecture decision record (ADR).

---

## 7. Advanced consistency, invalidation, failure, and cost trade-offs

### 7.1 Freshness, consistency, and staleness

These concepts are related but not interchangeable:

- **Freshness** asks how recently the result reflects source changes.
- **Consistency** asks which states different readers can observe and what ordering/visibility guarantees apply.
- **Staleness** describes how far the returned result lags the required source state or time.
- **Correctness** asks whether the result is valid for the requested business operation and caller.

A result can be recently refreshed but incorrect due to a bug or incomplete source input. A result can be old but still acceptable for a historical dashboard. A result can be individually correct but inconsistent with another materialised view built from a different source snapshot.

Define freshness in business terms: “the dashboard includes all source events committed up to watermark W, with observed lag below 10 minutes for 99% of intervals” is more testable than “near real-time.” Use a time-based lag, event-time watermark, source version, or combination suited to the data.

### 7.2 Invalidation strategies and race conditions

**TTL only:** simple, but may allow stale values until expiry. If source writes are frequent and correctness requires prompt visibility, TTL may be insufficient.

**Invalidate after source write:** reduces stale residence, but a write can commit while invalidation fails. A retryable outbox/event pattern can improve delivery, but the system still needs idempotency, monitoring, and a recovery procedure.

**Update cache after source write:** can improve read-your-writes behaviour, but concurrent updates, partial failure, and write ordering need explicit treatment.

**Versioned keys:** store values under a source or materialisation version and make readers resolve the active version. This reduces some delete/update races, but the active-version pointer must be published safely and old versions must eventually be reclaimed.

**Short TTL plus event invalidation:** can combine fast normal invalidation with a bound on residence time under some failure assumptions. It is not a formal staleness guarantee unless propagation, timer behaviour, and read-path rules are specified.

An important race:

1. Reader A misses and begins reading old source value V1.
2. Writer B commits V2 and invalidates the cache.
3. Reader A finishes late and writes V1 into the cache after the invalidation.
4. Later readers receive V1 until another invalidation or expiry.

Possible mitigations include version checks before publication, fencing tokens, compare-and-set, versioned keys, write-through coordination, or a design that tolerates the stale window. Choose based on the consistency requirement and complexity budget.

### 7.3 Cache stampede and thundering herd

A **cache stampede** occurs when many requests simultaneously miss for the same expensive key, often after expiry. A **thundering herd** is a broader burst of many requests waking or retrying together and competing for a shared resource. These can overlap.

Mitigations include:

- request coalescing/single-flight so one loader serves concurrent requests for a key;
- jittered expiry to avoid synchronized expiration across many entries;
- stale-while-revalidate when stale responses are permitted;
- refresh-ahead for predictable hot entries;
- bounded retries with exponential backoff and jitter;
- per-key or global concurrency limits;
- circuit breakers and controlled degradation;
- capacity reserved for the full miss path;
- warming a known working set after deploy or restart.

No mitigation is free. Stale-while-revalidate explicitly permits a stale result; request coalescing can create a queue behind one loader; warming can compete with foreground traffic; and retries can amplify an outage if not bounded.

### 7.4 Cache penetration and negative caching

**Cache penetration** commonly refers to repeated requests for absent or invalid keys that never produce a normal cache hit and repeatedly reach the backend. Causes can include random identifiers, invalid inputs, or malicious probing.

Controls may include input validation, rate limits, short-lived negative caching for confirmed absence, admission policies, and safe request filtering. Negative cache entries must expire or be invalidated when a record is created; otherwise a newly created record can remain invisible.

Do not confuse a cache miss with a source “not found” result. A miss says the cache had no usable entry; the backing source may return a valid object, a confirmed absence, or an error.

### 7.5 Hot keys and uneven distributions

A popular key can saturate a single cache partition or loader even when total cache capacity and average request rate look adequate. Options include local replicas, request coalescing, selective replication, key redesign, and precomputation. Replication can increase memory and invalidation work; key salting may distribute load but complicates reads and updates.

Measure per-key or per-shard skew where feasible, subject to privacy and telemetry-cardinality constraints. A system-wide hit ratio can conceal one hot key that accounts for a large fraction of misses or latency.

### 7.6 Cache outage and miss-path capacity

Under normal operation, if request rate is \(R\) and hit ratio is \(h\), the simplified backend miss rate is \(R(1-h)\). During a total cache outage, the miss path can approach \(R\), potentially multiplied by fan-out or retries.

Illustrative case: \(R = 2{,}000\) application requests/s, \(h = 0.95\), one backend call per miss.

- Normal miss rate: \(2{,}000 \times 0.05 = 100\) backend calls/s.
- Cache unavailable, if requests bypass/fall through: up to 2,000 backend calls/s.
- Load increase: 20× the normal miss rate.

This is not a universal cache-outage multiplier; it follows from these stated assumptions. If the backend cannot safely serve the full rate, define a deliberate policy: bounded queues, load shedding, stale fallback if allowed, degraded response, rate limits, or temporary rejection. Blindly falling back to the source can turn a cache outage into a wider outage.

### 7.7 Materialisation refresh and publication

A refresh pipeline should specify:

- source snapshot or watermark used;
- full or incremental processing logic;
- late-arriving and corrected data behaviour;
- deletion propagation;
- idempotency and duplicate handling;
- dependency order for upstream/downstream derived datasets;
- validation and reconciliation checks;
- atomic or versioned publication;
- handling of partial refresh and retry;
- last-successful-refresh timestamp and freshness-lag alert;
- rollback and rebuild procedure.

A safer publication pattern is often to build a new version, validate it, then atomically switch consumers to that version. This avoids exposing a partially rebuilt table, but it temporarily increases storage and requires a safe version-pointer switch. The exact pattern depends on the platform's transaction and visibility semantics.

Incremental refresh can be cheaper than full refresh, but only when change capture, updates, deletes, late events, deduplication, and state reconciliation are correctly handled. A daily or periodic full reconciliation can detect drift; its cost belongs in the model.

### 7.8 Cross-view consistency and dependency management

If a dashboard reads a customer aggregate and a risk score from separate materialisations, they may reflect different source watermarks. Each result can be internally valid yet jointly inconsistent.

Record dependencies and source versions. If the business operation requires a consistent snapshot, refresh related outputs from a common watermark or publish them as a coordinated version. If independent freshness is acceptable, document it explicitly rather than implying atomic consistency.

### 7.9 Security, privacy, and governance

Caches and materialised datasets are additional copies of data. They need appropriate:

- tenant and authorization isolation;
- encryption and network controls;
- retention and deletion propagation;
- masking/tokenisation rules;
- auditability and access logging;
- regional/residency controls where applicable;
- schema and lineage metadata;
- expiry of sensitive values and old materialised versions.

A cache can accidentally bypass source-system authorization if the key or lookup path omits tenant/user scope. A deleted source record may persist in a cache or materialised output unless deletion handling is designed and tested. Data minimisation applies to derived copies too.

### 7.10 Total cost model

Compare alternatives over the same time period and workload:

\[
C_{total} =
C_{source\ compute} + C_{cache\ infrastructure} + C_{refresh}
+ C_{storage} + C_{serving} + C_{transfer} + C_{operations}
\]

Possible additional terms include replicas, backups, retained versions, orchestration, monitoring, failed refreshes, recovery, and engineering/maintenance. Avoid double-counting costs already included in a managed-service rate.

Use consistent units, currency, time window, and attribution. “Cost per request” should specify whether the denominator is all successful application requests, all requests including errors, or only eligible cache lookups. Report both direct infrastructure cost and material exclusions when full operational cost cannot be estimated.

### 7.11 Repeated computation versus precomputation

Precomputation tends to become more attractive when:

- the same expensive result is requested frequently;
- the result is reusable across many consumers;
- the freshness requirement permits refresh delay;
- the result can be maintained correctly;
- storage and refresh costs are lower than the repeated computation avoided.

On-demand work tends to remain attractive when:

- requests are rare or unique;
- query shapes vary substantially;
- the source can answer within the latency and cost budgets;
- results must reflect a current state that cannot tolerate refresh lag;
- materialisation maintenance and invalidation would be more complex than the saved work.

Use a break-even model, then validate with observed distributions. Average request count alone may hide skew, seasonal demand, and query-cost differences.

---

## 8. Python examples with tests and assertions

The examples use only the Python standard library. They are deterministic teaching models, not production cache implementations or performance benchmarks. Each code block is self-contained.

### 8.1 Calculate hit ratio and expected backend load

Assumptions: every eligible lookup is classified as a hit or miss; each miss triggers exactly one backend call; no retries or fan-out. Counts are integers, and request rate is a finite non-negative number. A zero-lookup sample has an undefined hit ratio and is rejected.

```python
import math


def _finite_nonnegative_number(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and non-negative")


def cache_metrics(hits: int, misses: int, requests_per_second: float) -> dict:
    for name, value in (("hits", hits), ("misses", misses)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")
    _finite_nonnegative_number("requests_per_second", requests_per_second)

    total = hits + misses
    if total == 0:
        raise ValueError("hit ratio is undefined when there are no eligible lookups")

    hit_ratio = hits / total
    miss_ratio = misses / total
    return {
        "eligible_lookups": total,
        "hit_ratio": hit_ratio,
        "miss_ratio": miss_ratio,
        "expected_backend_requests_per_second": requests_per_second * miss_ratio,
    }


metrics = cache_metrics(hits=900, misses=100, requests_per_second=1000)
assert metrics["eligible_lookups"] == 1000
assert abs(metrics["hit_ratio"] - 0.90) < 1e-12
assert abs(metrics["miss_ratio"] - 0.10) < 1e-12
assert abs(metrics["expected_backend_requests_per_second"] - 100.0) < 1e-12

for invalid in (
    (0, 0, 10), (-1, 2, 10), (1.5, 2, 10), (True, 2, 10),
    (1, 2, float("nan")), (1, 2, float("inf")), (1, 2, -1),
):
    try:
        cache_metrics(*invalid)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid metrics input was accepted: {invalid!r}")

print(metrics)
```

Expected key results: 90% hit ratio, 10% miss ratio, and 100 expected backend calls/second under the one-miss/one-backend-call assumption. The helper validates input shape; it does not prove that the observed hit/miss sample and supplied request rate describe the same workload window. Ensure they do before using the result operationally.

### 8.2 A tiny cache-aside simulation

This toy simulation demonstrates hits, misses, TTL expiry, loader failures, and source-load attempts. It uses a logical clock and does not model concurrency, memory limits, eviction, distributed failure, or clock skew. Callers must supply finite, non-negative, nondecreasing logical timestamps.

```python
import math


class TinyTTLCache:
    def __init__(self, ttl_seconds: float):
        if (isinstance(ttl_seconds, bool)
                or not isinstance(ttl_seconds, (int, float))
                or not math.isfinite(ttl_seconds)
                or ttl_seconds <= 0):
            raise ValueError("TTL must be a finite positive number")
        self.ttl = ttl_seconds
        self.entries = {}
        self.hits = 0
        self.misses = 0
        self.backend_read_attempts = 0
        self.last_now = None

    def get(self, key, now, loader):
        if (isinstance(now, bool) or not isinstance(now, (int, float))
                or not math.isfinite(now) or now < 0):
            raise ValueError("now must be a finite non-negative number")
        if self.last_now is not None and now < self.last_now:
            raise ValueError("logical clock must be nondecreasing")
        try:
            hash(key)
        except TypeError as exc:
            raise ValueError("cache key must be hashable") from exc
        self.last_now = now

        entry = self.entries.get(key)
        if entry is not None:
            value, expires_at = entry
            if now < expires_at:
                self.hits += 1
                return value

        self.misses += 1
        self.backend_read_attempts += 1
        # A failed loader is not cached; a later request can retry.
        value = loader(key)
        self.entries[key] = (value, now + self.ttl)
        return value


source = {"customer:7": {"tier": "silver"}}
cache = TinyTTLCache(ttl_seconds=10)

def load_from_source(key):
    return source[key]

assert cache.get("customer:7", now=0, loader=load_from_source)["tier"] == "silver"
assert cache.get("customer:7", now=5, loader=load_from_source)["tier"] == "silver"
assert cache.hits == 1 and cache.misses == 1
assert cache.backend_read_attempts == 1

# The entry expires at t=10; t=10 is expired because now < expires_at is false.
source["customer:7"] = {"tier": "gold"}
assert cache.get("customer:7", now=10, loader=load_from_source)["tier"] == "gold"
assert cache.hits == 1 and cache.misses == 2
assert cache.backend_read_attempts == 2

# Failed loads are counted as miss/read attempts, but are not cached.
failing_cache = TinyTTLCache(ttl_seconds=5)
def failed_loader(_key):
    raise RuntimeError("temporary source failure")
try:
    failing_cache.get("missing", now=0, loader=failed_loader)
except RuntimeError:
    pass
else:
    raise AssertionError("loader failure should propagate")
assert failing_cache.misses == 1
assert failing_cache.backend_read_attempts == 1
assert "missing" not in failing_cache.entries
assert failing_cache.get("missing", now=1, loader=lambda _key: "recovered") == "recovered"
assert failing_cache.backend_read_attempts == 2

for invalid_ttl in (0, -1, float("nan"), float("inf"), True):
    try:
        TinyTTLCache(invalid_ttl)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid TTL was accepted: {invalid_ttl!r}")

try:
    cache.get("customer:7", now=9, loader=load_from_source)
except ValueError:
    pass
else:
    raise AssertionError("a backward logical clock must be rejected")

try:
    cache.get(["unhashable"], now=11, loader=load_from_source)
except ValueError:
    pass
else:
    raise AssertionError("an unhashable cache key must be rejected")

print({"hits": cache.hits, "misses": cache.misses,
       "hit_ratio": cache.hits / (cache.hits + cache.misses),
       "backend_read_attempts": cache.backend_read_attempts})
```

Expected results for the primary cache: 1 hit, 2 misses, hit ratio \(1/3\), and 2 backend-read attempts. A failed loader increments the miss and attempt counters but does not create an entry. The source change at time 5 is not visible at time 5 because the cached entry remains valid until expiry; this illustrates the staleness consequence of TTL-only invalidation.

### 8.3 Estimate idealised freshness lag and refresh cost

Assumptions: continuous 24-hour operation; a refresh succeeds every interval; source changes occur uniformly between refreshes; source ingestion and refresh processing delays are zero in this simplified model. `runs_per_day` is a steady-state rate calculation; the exact integer number of runs in a particular calendar day depends on schedule alignment, interval divisibility, and whether a run occurs at the day boundary.

```python
import math


def scheduled_refresh_model(interval_minutes: float, cost_per_refresh: float) -> dict:
    for name, value in (("interval_minutes", interval_minutes),
                        ("cost_per_refresh", cost_per_refresh)):
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value)):
            raise ValueError(f"{name} must be finite numeric input")
    if interval_minutes <= 0:
        raise ValueError("interval must be positive")
    if cost_per_refresh < 0:
        raise ValueError("refresh cost must be non-negative")

    minutes_per_day = 24 * 60
    runs_per_day = minutes_per_day / interval_minutes
    return {
        "interval_minutes": interval_minutes,
        "runs_per_day": runs_per_day,
        "refresh_cost_per_day": runs_per_day * cost_per_refresh,
        "ideal_average_schedule_lag_minutes": interval_minutes / 2,
        "ideal_worst_schedule_lag_approaches_minutes": interval_minutes,
    }


fifteen_min = scheduled_refresh_model(15, 12)
sixty_min = scheduled_refresh_model(60, 12)
assert abs(fifteen_min["runs_per_day"] - 96) < 1e-12
assert abs(fifteen_min["refresh_cost_per_day"] - 1152) < 1e-12
assert abs(fifteen_min["ideal_average_schedule_lag_minutes"] - 7.5) < 1e-12
assert abs(sixty_min["runs_per_day"] - 24) < 1e-12
assert abs(sixty_min["refresh_cost_per_day"] - 288) < 1e-12
assert abs(sixty_min["ideal_average_schedule_lag_minutes"] - 30) < 1e-12

for invalid in ((0, 12), (-1, 12), (float("nan"), 12), (15, float("inf")), (True, 12), (15, -1)):
    try:
        scheduled_refresh_model(*invalid)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid refresh input was accepted: {invalid!r}")

print({"15_min": fifteen_min, "60_min": sixty_min})
```

Expected results: 96 runs/day and $1,152/day for 15-minute refresh; 24 runs/day and $288/day for 60-minute refresh. These are model outputs from the stated illustrative cost, not market pricing.

### 8.4 Compare simplified on-demand and materialised cost

Assumptions: all requests would otherwise execute the same live query; each live query has an attributable marginal cost; materialisation costs are measured over the same day; all materialisation read-serving cost is included in the daily total. Read count must be a non-negative integer; costs must be finite and non-negative.

```python
import math


def compare_daily_cost(
    reads_per_day: int,
    live_cost_per_read: float,
    refresh_cost_per_day: float,
    storage_cost_per_day: float,
    serving_cost_per_day: float = 0.0,
    maintenance_cost_per_day: float = 0.0,
) -> dict:
    if (isinstance(reads_per_day, bool) or not isinstance(reads_per_day, int)
            or reads_per_day < 0):
        raise ValueError("reads_per_day must be a non-negative integer")
    costs = {
        "live_cost_per_read": live_cost_per_read,
        "refresh_cost_per_day": refresh_cost_per_day,
        "storage_cost_per_day": storage_cost_per_day,
        "serving_cost_per_day": serving_cost_per_day,
        "maintenance_cost_per_day": maintenance_cost_per_day,
    }
    for name, cost in costs.items():
        if (isinstance(cost, bool) or not isinstance(cost, (int, float))
                or not math.isfinite(cost) or cost < 0):
            raise ValueError(f"{name} must be finite and non-negative")

    live = reads_per_day * live_cost_per_read
    materialised = (refresh_cost_per_day + storage_cost_per_day
                    + serving_cost_per_day + maintenance_cost_per_day)
    return {
        "on_demand_cost_per_day": live,
        "materialised_cost_per_day": materialised,
        "modelled_savings_per_day": live - materialised,
        "materialisation_is_cheaper_in_model": materialised < live,
    }


comparison = compare_daily_cost(
    reads_per_day=5000,
    live_cost_per_read=0.04,
    refresh_cost_per_day=30,
    storage_cost_per_day=2,
)
assert abs(comparison["on_demand_cost_per_day"] - 200.0) < 1e-12
assert abs(comparison["materialised_cost_per_day"] - 32.0) < 1e-12
assert abs(comparison["modelled_savings_per_day"] - 168.0) < 1e-12
assert comparison["materialisation_is_cheaper_in_model"] is True

# Fixed serving and maintenance costs can reverse the decision.
reversed_case = compare_daily_cost(
    reads_per_day=500,
    live_cost_per_read=0.04,
    refresh_cost_per_day=15,
    storage_cost_per_day=2,
    serving_cost_per_day=2,
    maintenance_cost_per_day=5,
)
assert abs(reversed_case["on_demand_cost_per_day"] - 20.0) < 1e-12
assert abs(reversed_case["materialised_cost_per_day"] - 24.0) < 1e-12
assert reversed_case["materialisation_is_cheaper_in_model"] is False

for invalid in (
    (-1, 0.04, 1, 1), (True, 0.04, 1, 1), (1, float("nan"), 1, 1),
    (1, 0.04, float("inf"), 1), (1, 0.04, 1, -1),
):
    try:
        compare_daily_cost(*invalid)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid cost input was accepted: {invalid!r}")

print({"high_reuse": comparison, "low_reuse": reversed_case})
```

Expected results: in the high-reuse case, the simplified materialised option costs $32/day versus $200/day on demand; in the low-reuse case with the stated fixed costs, materialisation costs $24/day versus $20/day on demand. This illustrates why reuse and fixed refresh/maintenance costs matter.

### 8.5 Test a freshness budget

This helper adds upper-bound components. It assumes the components form a serial path and that the stated maxima are valid; correlated delays, retries, and parallel paths may require a more detailed model. The sum is a conservative bound only when each component is defined consistently and the assumed sequence covers the actual data path.

```python
import math


def freshness_upper_bound(
    schedule_interval_minutes: float,
    ingestion_delay_minutes: float,
    refresh_runtime_minutes: float,
    publication_delay_minutes: float,
) -> float:
    values = {
        "schedule_interval_minutes": schedule_interval_minutes,
        "ingestion_delay_minutes": ingestion_delay_minutes,
        "refresh_runtime_minutes": refresh_runtime_minutes,
        "publication_delay_minutes": publication_delay_minutes,
    }
    for name, value in values.items():
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value < 0):
            raise ValueError(f"{name} must be finite and non-negative")
    return sum(values.values())


bound = freshness_upper_bound(15, 4, 3, 1)
assert bound == 23
assert bound > 20  # This bound does not prove a 20-minute contract.
assert freshness_upper_bound(10, 0, 0, 0) == 10

for invalid in ((-1, 0, 0, 0), (1, float("nan"), 0, 0),
                (1, 0, float("inf"), 0), (1, 0, 0, True)):
    try:
        freshness_upper_bound(*invalid)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid freshness input was accepted: {invalid!r}")

print({"freshness_upper_bound_minutes": bound, "meets_20_minute_contract": bound <= 20})
```

Expected result: 23 minutes, so the illustrative 20-minute freshness contract is not met by this conservative bound.

---

## 9. Industry-style scenarios and architecture comparisons

### 9.1 Scenario A — customer profile API

**Workload:** frequent point lookups by customer ID; many repeated reads; profile changes are uncommon but authorization and tenant boundaries are important.

**Candidate:** cache-aside or read-through cache in front of an authoritative customer store.

**Conditions:** key must include tenant and any response-varying scope; authorization must be evaluated correctly; update/delete events should invalidate or version entries; TTL must be consistent with the business freshness contract.

**Risks:** stale profile after update, cross-tenant key collision, cache outage driving source overload, and deletion not propagating.

**Validation:** measure hit ratio by request class, p50/p95/p99 latency, source request rate, invalidation delay, cache error rate, and correctness after update/delete. Test cold start and cache-disabled load.

### 9.2 Scenario B — executive sales dashboard

**Workload:** many users repeatedly request similar daily/weekly aggregates; underlying transaction data is large; a 15-minute or hourly delay may be acceptable only if business owners explicitly approve it.

**Candidate:** materialised aggregate, potentially with a short-lived cache for repeated dashboard responses.

**Conditions:** publish a consistent snapshot/watermark; define late-arriving correction handling; show last successful refresh and data-through timestamp; monitor refresh lag.

**Risks:** expensive full refresh, partial publication, stale aggregates after corrections, inconsistent totals across tiles, and refresh contention with ingestion.

**Validation:** compare materialised totals with a trusted recomputation for sampled periods; load test refresh and foreground queries together; calculate refresh cost and storage; alert on freshness and reconciliation failure.

### 9.3 Scenario C — risk dashboard with point lookups and aggregate views

**Workload:** per-customer risk lookups are latency-sensitive; portfolio aggregates are expensive and reused. Some decisions may require the latest risk state, while management reporting may tolerate a defined lag.

**Candidate:** separate serving paths: an online store for customer-level current features/state, plus materialised portfolio aggregates for reporting. Cache only the fields whose staleness and authorization behaviour are explicitly acceptable.

**Design principle:** do not force point lookups and aggregate analytics into one store if their latency, query shape, and freshness needs differ. Define the consistency relationship between customer state and portfolio aggregate.

**Failure plan:** if cache fails, protect the online store with rate limits and load shedding; if aggregate refresh fails, serve the last validated version only when the dashboard can visibly communicate its age and policy permits it; otherwise mark the aggregate unavailable.

### 9.4 Scenario D — search and retrieval over documents

**Workload:** varied text queries; index-based retrieval; document permissions and deletes can change; some queries repeat and some are unique.

**Candidate:** search index as the serving structure; selective query-result cache only for high-reuse queries with safe keys and invalidation. The search index itself is a derived representation and must receive document updates and ACL changes.

**Risks:** cached result contains deleted or newly restricted documents; query cache key omits user/ACL scope; index refresh lag and result-cache lag compound; low reuse makes result caching expensive.

**Validation:** test ACL changes, deletion propagation, duplicate/reordered query parameters, query version changes, and low/high-cardinality traffic. Measure cache hit ratio and index freshness separately.

### 9.5 Architecture comparison table

| Option | Typical access shape | Freshness/consistency concern | Cost drivers | Failure/recovery concern |
|---|---|---|---|---|
| On-demand analytical query | Variable filters, joins, aggregates | Usually reads source/query snapshot; source may itself lag | Query compute, scans, concurrency | Queueing or source overload |
| Cache-aside over source | Repeated keys or results | TTL/invalidation; write/read races | Memory, network, misses, backend | Cache outage can expose full miss path |
| Materialised view/table | Repeated known computation | Refresh lag, snapshot consistency, late data | Refresh compute, storage, serving | Partial/failed refresh; rollback/rebuild |
| Online key-value serving store | High-rate point lookups | Update propagation and feature freshness | Provisioned capacity, replication, writes | Hot keys, shard failure, stale replicas |
| Search index | Text retrieval and filtering | Index/ACL/delete propagation | Indexing compute, index storage, queries | Lagging or corrupt index; rebuild |
| Layered design | Multiple distinct access patterns | Layer-to-layer consistency and compounded lag | Costs of all layers plus orchestration | More dependencies, harder diagnosis |

### 9.6 Decision matrix deliverable — worked example

For a dashboard with five query types, a learner could start with this illustrative matrix and replace the choices after measuring actual workload.

| Query type | Reuse/cost profile | Freshness need | Candidate | Evidence required |
|---|---|---|---|---|
| Customer profile by ID | High reuse; moderate lookup cost | Minutes acceptable if approved | Cache-aside | Key distribution, invalidation lag, miss-path capacity |
| Daily sales by region | High reuse; expensive aggregation | 15-minute lag if business-approved | Materialised aggregate | Refresh cost, reconciliation, end-to-end lag |
| Arbitrary ad hoc drill-down | Low predictable reuse; varied query shape | Current query snapshot | On-demand analytical query | Query plan, scan volume, p95/p99, concurrency |
| Current risk decision | Potentially high reuse but stale value may be harmful | Strong freshness/consistency | Authoritative or tightly controlled online serving path | Read-after-write, source watermark, correctness test |
| Top products widget | High repeated aggregate; bounded dimensions | Short delay may be acceptable | Materialised aggregate plus optional cache | Reuse, refresh cost, cache benefit, stale-display policy |

The matrix is not a final architecture. It is a structured hypothesis set to validate against actual requirements and measurements.

---

## 10. Practical exercises at three difficulty levels

Attempt each exercise before reading the answer key.

### Level 1 — Beginner: classify five requests

For each request, select cache, materialisation, on-demand, or a layered option, and state one risk:

1. Product details are requested thousands of times per hour and change rarely.
2. A finance report performs a costly join and aggregation once every day.
3. Analysts issue unique ad hoc queries with changing filters.
4. A payment authorization needs the current account state.
5. A dashboard repeatedly requests the same daily total, and a 10-minute delay is acceptable.

Write the freshness assumption explicitly. Do not label “cache” as correct without explaining what happens after a write.

### Level 2 — Intermediate: calculate cache impact

A cache receives 4,000 eligible lookups/second. During a 10-minute window, 2,160,000 lookups hit and 240,000 miss. Each miss triggers one backend query. Cache-hit service time is 3 ms and backend miss service time is 75 ms.

Calculate:

1. Hit and miss ratios.
2. Expected hit and miss rates.
3. The simplified weighted mean service-time estimate.
4. Backend query rate reduction relative to all requests going to the backend.
5. Two reasons the estimate may not match p95 latency.

### Level 3 — Advanced: choose a serving architecture

A risk dashboard has:
- 1,200 per-customer lookups/second at peak;
- 200 aggregate queries/minute;
- per-customer state must reflect updates within 30 seconds;
- aggregate reporting may be at most 10 minutes behind source;
- a full aggregate refresh costs an illustrative \$18/run;
- a 10-minute scheduled refresh takes 4 minutes to process after source data is available;
- ingestion delay can be up to 2 minutes;
- the cache hit ratio for customer lookups is measured at 92% in the representative test;
- the backing online store can safely handle 250 lookups/second in normal operation;
- no tested cache-outage capacity has yet been established.

Tasks:

1. Calculate normal miss rate under the one-miss/one-backend-call assumption.
2. Compare that miss rate with the online store's stated 250 lookups/second capacity.
3. Calculate the conservative freshness upper bound for the aggregate with a 10-minute schedule, 2-minute ingestion delay, and 4-minute refresh duration; state whether it proves the 10-minute contract.
4. Calculate full refresh cost/day if refresh runs every 10 minutes for 24 hours.
5. Recommend separate serving paths or explain why one path might suffice.
6. Identify the missing evidence required before production approval.
7. Define a cache-outage policy that does not assume the online store can absorb 1,200 requests/second.

---

## 11. Answer key and reasoning

### Level 1 — example answers

1. **Product details:** cache-aside/read-through may fit if tenant/locale/version dimensions are keyed correctly; risk is stale details after an update.
2. **Daily finance report:** materialise if reuse or query cost justifies refresh and the business accepts its freshness; risk is reconciliation or correction lag.
3. **Ad hoc queries:** on-demand query execution is a reasonable starting point; optimise plans and bound concurrency. Caching every unique result may have poor reuse.
4. **Payment authorization:** use an authoritative or explicitly consistency-controlled path. Do not assume a stale cache is safe; the business correctness requirement is a hard gate.
5. **Repeated daily total:** materialised aggregate and possibly a short-lived response cache; verify end-to-end freshness and the economics of maintaining both layers.

Other answers can be valid if they state assumptions, risks, and validation criteria.

### Level 2 — calculations

Total lookups = 2,160,000 + 240,000 = 2,400,000.

- Hit ratio = 2,160,000 / 2,400,000 = **90%**.
- Miss ratio = 240,000 / 2,400,000 = **10%**.
- The window is 600 seconds, so observed request rate = 2,400,000 / 600 = **4,000 lookups/s**.
- Hit rate = 4,000 × 0.90 = **3,600/s**.
- Miss/backend query rate = 4,000 × 0.10 = **400/s**.
- Weighted mean service-time estimate = 0.90 × 3 ms + 0.10 × 75 ms = 2.7 + 7.5 = **10.2 ms**.
- Under the stated one-miss/one-backend-query assumption, backend query rate falls from 4,000/s to 400/s, a **90% reduction** in backend queries.

The estimate may differ from p95 because (a) misses may queue or fan out, making their latency much larger; (b) cache/backend times have distributions and the weighted average does not determine percentiles; (c) network, retries, contention, or cache eviction can alter observed latency.

### Level 3 — reasoning

1. Normal miss rate = 1,200 × (1 − 0.92) = **96 lookups/s**.
2. 96/s is below the stated normal capacity of 250/s, leaving 154/s of nominal capacity in this simplified model. This is not proof of safe operation: measure burstiness, write load, other consumers, latency at that load, and what happens on cache failure.
3. Conservative upper-bound sum = 10 + 2 + 4 = **16 minutes**, before publication delay or retries. It does **not** prove the 10-minute contract. Shorten the interval/runtime/ingestion delay or adopt a suitable incremental/event-driven design; then measure end-to-end lag.
4. Runs/day = 1,440 / 10 = 144. Refresh cost/day = 144 × \$18 = **\$2,592/day**, excluding storage, serving, retries, and operations.
5. Separate paths are a strong starting hypothesis: current per-customer lookups have a 30-second freshness requirement, while aggregate views have a different, stricter-than-the-scheduled-plan 10-minute lag requirement. Use an online serving path for customer state and a validated aggregate materialisation with a refresh strategy that can actually meet the lag contract. Add a cache only where its freshness and outage behaviour are acceptable.
6. Missing evidence includes p95/p99 under peak and burst traffic, cache outage and cold-start tests, actual miss fan-out, write/read-after-write semantics, end-to-end aggregate lag distribution, late-event/correction behaviour, storage and serving costs, data reconciliation, security scope, and recovery time.
7. Do not blindly fall through to the online store at 1,200/s. Options include rate limiting, bounded concurrency, queueing only where latency permits, load shedding, stale fallback only for fields whose policy permits it, degraded responses, and prioritisation of critical traffic. Test each mode and alert operators. The store's 250/s normal capacity is not a demonstrated outage capacity.

---

## 12. Common mistakes, troubleshooting, and limitations

### 12.1 Common mistakes

| Mistake | Why it fails | Better practice |
|---|---|---|
| Optimising only for hit ratio | A high ratio can coexist with slow hits, expensive misses, stale results, or poor tail latency | Track latency percentiles, backend fan-out, correctness, and freshness |
| Treating TTL as a freshness guarantee | Source changes, ingestion delay, refresh runtime, and invalidation delay may exceed the assumed window | Define the lag origin and calculate end-to-end bounds; measure actual lag |
| Using incomplete cache keys | Different tenants, filters, versions, or permissions can collide | Define key schema and test all result-varying dimensions |
| Assuming cache outage is harmless | Backend load can jump from miss rate to full request rate | Capacity-test cache-disabled operation and define degradation controls |
| Caching every query | Unique results consume capacity with little reuse | Measure reuse and admit only beneficial result classes |
| Materialising without correcting the query | Expensive or faulty computation is repeated during every refresh | Inspect and optimise the plan before precomputing |
| Comparing costs over different periods | Daily refresh cost cannot be compared directly with monthly query cost | Normalise currency, units, and time window |
| Ignoring refresh failures | A scheduled job may fail or publish partial output | Track last successful refresh, watermark, validation, and publication status |
| Treating incremental refresh as inherently correct | Deletes, corrections, late data, and duplicate events can be missed | Define change semantics and reconcile against a trusted recomputation |
| Forgetting security on derived copies | Cached/precomputed data can outlive permissions or deletion | Propagate ACL and deletion changes; scope keys; audit derived data |
| Using average latency to claim p95/p99 | A weighted mean does not determine the tail | Measure percentiles under representative concurrency and failure cases |
| Ignoring cold start and stampede | A restart/expiry can send a burst to the backend | Coalesce requests, jitter expiry, warm carefully, and bound concurrency |

### 12.2 Troubleshooting guide

| Symptom | Possible causes | Evidence to inspect | Candidate action |
|---|---|---|---|
| Hit ratio falls after deployment | Key format changed, cache flush, new query dimensions | Hit/miss by key class, deployment timestamp, cardinality | Review key version and warm only valuable working sets |
| High hit ratio but p99 is poor | Slow cache network, hot key, queueing, expensive misses | Separate hit/miss latency, per-shard load, fan-out | Remove hot bottleneck, coalesce misses, reduce backend fan-out |
| Backend overload after expiry | Synchronized TTL, stampede, insufficient miss capacity | Miss rate over time, concurrent loaders, expiry distribution | TTL jitter, single-flight, bounded loader concurrency |
| Stale value survives a write | Invalidation failed or raced with a late loader | Source version, invalidation events, cache entry version | Version/fence writes, retryable invalidation, test race |
| Materialised output is old | Refresh queue, source lag, failed run, long processing | Source watermark, start/end times, last successful publication | Alert on end-to-end lag; optimise or change refresh strategy |
| Totals differ between dashboard tiles | Different snapshots/watermarks, late data, duplicated increments | Lineage, source version, reconciliation output | Coordinate publication or document independent freshness |
| Refresh cost grows unexpectedly | Full rebuilds, retries, increased source volume, more frequent schedule | Cost per run, bytes processed, retries, schedule history | Profile work, incrementalise safely, revisit cadence |
| Cache memory churn/evictions rise | Working set exceeds capacity, entry sizes grow, TTL too short | Resident set, eviction reason, value size, reuse distribution | Resize only after measuring; tune admission/TTL; reduce entry size |
| New record remains “not found” | Negative cache has not expired or been invalidated | Negative-hit metrics, creation event, key TTL | Invalidate negative entries or shorten their policy TTL |
| Cache outage cascades to source | No load shedding, retries amplify demand, no bypass limits | Backend rate, retry count, queue depth, circuit state | Apply limits, jittered retries, graceful degradation and runbooks |

### 12.3 Limitations of the calculations

- Weighted mean latency assumes hit and miss outcomes have known representative times and ignores queueing; it cannot predict p95/p99.
- Backend request rate assumes one backend call per miss. Fan-out, retries, refresh traffic, and background jobs must be added separately.
- Idealised schedule lag assumes successful periodic refresh and a particular distribution of source changes. It is not a substitute for measured freshness.
- Simple cost comparisons omit any explicitly excluded cost. Record exclusions rather than interpreting a simplified difference as net savings.
- A cache simulation with a logical clock does not model distributed concurrency, network failure, eviction, replication, or consistency races.
- A decision matrix is a reasoning aid, not a replacement for hard constraints, operational tests, or measured evidence.

---

## 13. Practical deliverables

Produce the following artefacts as part of a design review. The examples below are templates; fill them with measured values and label every assumption.

### 13.1 Caching and materialisation requirements profile

| Field | Required entry |
|---|---|
| Consumer and business purpose | Which application, dashboard, API, model, or decision consumes the data? |
| Source of truth | Authoritative system/table/topic and owner |
| Access pattern | Point lookup, repeated query, aggregate, search, ad hoc, feature lookup |
| Request profile | Average/peak rate, burstiness, concurrency, read/write mix |
| Reuse evidence | Hit ratio/reuse distance, repeated query frequency, key popularity |
| Data shape | Cardinality, average/max entry size, aggregate size |
| Latency objective | End-to-end p50/p95/p99 target and measurement point |
| Freshness contract | Maximum lag, lag origin, watermark, acceptable stale behaviour |
| Consistency contract | Read-your-writes, cross-view consistency, ordering/version needs |
| Security | Tenant, user/role, masking, ACL, retention and deletion requirements |
| Failure requirements | Cache outage, source outage, stale fallback, load shedding, recovery |
| Cost envelope | Source compute, cache, refresh, storage, serving, transfer, operations |
| Validation plan | Load test, correctness comparison, failure tests, success thresholds |
| Owner and review date | Accountable team and when assumptions must be revisited |

### 13.2 Decision matrix

| Candidate | Hard constraints passed? | Expected latency | Freshness fit | Estimated total cost/period | Operational complexity | Failure behaviour | Evidence confidence |
|---|---|---|---|---:|---|---|---|
| Cache-aside | TBD | TBD | TBD | TBD | TBD | TBD | Low/medium/high with reason |
| Materialised view | TBD | TBD | TBD | TBD | TBD | TBD | Low/medium/high with reason |
| On-demand query | TBD | TBD | TBD | TBD | TBD | TBD | Low/medium/high with reason |
| Layered option | TBD | TBD | TBD | TBD | TBD | TBD | Low/medium/high with reason |

Hard constraints should include security, correctness, and freshness. A candidate that fails a hard constraint should not win because it scores well on cost or latency.

### 13.3 Freshness and invalidation policy

Document:

- allowed staleness and the business owner who approved it;
- the source event or watermark from which lag is measured;
- TTL/refresh interval and why it is sufficient;
- invalidation trigger and delivery semantics;
- handling of duplicate, late, out-of-order, or missing events;
- what happens if invalidation or refresh fails;
- maximum stale fallback duration, if any;
- deletion and permission-change propagation;
- metrics and alert thresholds;
- reconciliation procedure;
- rollback and cache/materialisation rebuild procedure.

### 13.4 Quantitative analysis worksheet

Use a consistent period (for example, per day):

```text
Eligible cache lookups:
Hits:
Misses:
Measurement window:
Hit ratio = hits / (hits + misses):
Miss ratio = misses / (hits + misses):
Application request rate:
Backend calls per miss (fan-out):
Estimated normal backend rate:
Estimated cache-outage backend rate:
Cache-hit latency distribution:
Miss-path latency distribution:

On-demand query count / period:
Measured cost per live query:
On-demand compute cost / period:

Refresh interval:
Refresh runs / period:
Cost per refresh:
Refresh compute cost / period:
Materialised storage cost / period:
Serving cost / period:
Transfer and operations cost / period:
Total modelled materialised cost / period:

Allowed freshness lag:
Observed ingestion delay:
Observed refresh duration:
Publication delay:
Observed freshness lag p50/p95/max:
Correctness/reconciliation result:
Excluded costs and uncertainties:
```

### 13.5 Recommendation and validation criteria

An architecture recommendation should state:

1. **Decision:** selected serving pattern and which workloads it serves.
2. **Rejected alternatives:** why they fail a requirement or are less favourable under stated assumptions.
3. **Assumptions:** workload, key distribution, hit ratio, query cost, freshness, and pricing inputs.
4. **Quantified trade-off:** latency/load/cost/freshness differences with units and time windows.
5. **Operational risks:** stampede, invalidation failure, refresh lag, outage, data deletion, and recovery.
6. **Controls:** coalescing, TTL/invalidation, versioning, load shedding, validation, and alerts.
7. **Validation:** representative load test, cache-disabled test, correctness reconciliation, and total-cost comparison.
8. **Rollback:** how to disable cache or return to a last-known-good materialisation safely.
9. **Ownership:** team responsible for freshness, cache correctness, refresh health, and cost.
10. **Review trigger:** what workload, cost, freshness, or incident change forces reconsideration.

### 13.6 Architecture decision record (ADR) outline

```text
Title:
Status and date:
Context:
Consumer and business requirements:
Baseline evidence:
Options considered:
Hard constraints:
Decision and rationale:
Quantitative comparison and assumptions:
Freshness/consistency contract:
Failure and recovery behaviour:
Security and governance:
Validation and rollout plan:
Rollback plan:
Owners:
Open questions:
Review triggers:
```

---

## 14. Mastery criteria and completion gate

You are ready to move on when you can do all of the following without relying on an assumed “best” pattern:

- [ ] Explain the difference between caching, materialisation, and on-demand computation.
- [ ] Define the hit-ratio denominator, measurement window, and treatment of errors/bypasses.
- [ ] Calculate hit ratio, miss rate, and backend load with explicit fan-out assumptions.
- [ ] Explain why hit ratio does not prove p95/p99 latency, freshness, correctness, or outage safety.
- [ ] Design cache keys that include result-varying dimensions and security scope.
- [ ] Compare TTL, invalidation, refresh, versioned keys, and negative caching.
- [ ] Explain and mitigate stampedes, penetration, hot keys, cold starts, and cache outages.
- [ ] Estimate full/incremental refresh cost, storage, and schedule-induced freshness lag.
- [ ] State source watermark, ingestion delay, refresh duration, publication delay, and measured freshness.
- [ ] Compare cache, materialised view, on-demand query, and layered serving options for different access patterns.
- [ ] Model total cost over a consistent time period and disclose excluded costs.
- [ ] Define correctness checks, failure tests, alerts, rollback, and ownership.
- [ ] Produce the requirements profile, decision matrix, freshness/invalidation policy, quantitative worksheet, and recommendation.

### Completion gate

Submit a short architecture review for one realistic workload. It must contain:

1. A measured or explicitly assumed workload profile.
2. At least two viable serving alternatives and one rejected alternative.
3. A reproducible hit-ratio, refresh-cost, or break-even calculation.
4. A freshness contract and invalidation/refresh policy.
5. A cache-outage or refresh-failure plan.
6. Validation criteria that can pass or fail.
7. A list of assumptions and evidence gaps.

**Pass condition:** the recommendation's numbers are reproducible; all hard correctness/freshness/security constraints are addressed; failure behaviour is explicit; and no assumed benchmark or price is presented as a measured fact. If any critical input is unknown, the output must identify it and propose how to measure it rather than conceal the uncertainty.

---

## 15. Transition to Topic 06 — Cost Modeling, Unit Economics, and FinOps

Topic 05 shows how serving design changes the shape of resource consumption: caches trade memory and invalidation complexity for reuse; materialised results trade refresh and storage for fewer repeated computations; on-demand queries trade repeated compute for flexibility and potentially fresher results.

Topic 06 will turn these resource patterns into a transparent financial model. Carry forward:

- request volume and peak/average profile from Topic 01;
- latency and queueing behaviour from Topic 02;
- query cost and data movement evidence from Topic 03;
- skew, partition, and hot-key risks from Topic 04;
- measured hit ratio, miss fan-out, freshness lag, refresh runs, storage, and failure-path capacity from this topic.

In Topic 06, compare cost per request, cost per successful query, cost per refreshed dataset, and cost per business outcome where those units are meaningful. Keep assumptions, attribution, currency, time window, and excluded costs explicit. A cheaper serving path is not an optimisation if it violates freshness, correctness, reliability, or governance requirements.

**Next file:** `06-cost-modeling-unit-economics-and-finops.md`.
