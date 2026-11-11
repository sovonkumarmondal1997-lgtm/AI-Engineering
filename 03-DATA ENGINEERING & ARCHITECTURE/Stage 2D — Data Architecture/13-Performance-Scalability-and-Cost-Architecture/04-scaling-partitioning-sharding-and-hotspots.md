# Scaling, Partitioning, Sharding and Hotspots

**Repository location:** `Stage 2D — Data Architecture/13-Performance-Scalability-and-Cost-Architecture/04-scaling-partitioning-sharding-and-hotspots.md`  
**Module:** Stage 2D, Module 2D.13 — Performance, Scalability and Cost Architecture  
**Level:** Beginner → Intermediate → Advanced  
**Approach:** Vendor-neutral. Organisations, sizes, rates, and performance figures are illustrative assumptions, not benchmarks.

---

## 1. Purpose, scope, and learning outcomes

When one machine, worker, storage unit, or partition cannot meet capacity or service objectives, architects consider scaling. They can make a resource larger (**scale up**) or distribute work across more resources (**scale out**). Scale-out usually requires deliberate data and workload distribution. That distribution can improve aggregate capacity, but it can also introduce coordination, network transfer, cross-partition work, uneven utilisation, and operational complexity.

The central risk is a **hotspot**: a node, shard, partition, key, or resource that receives a disproportionate share of work. Adding nodes does not necessarily solve a hotspot because the work may still be routed to the same key or partition.

### 1.1 Learning outcomes

By the end of this lesson, you should be able to:

1. Compare vertical and horizontal scaling and explain their limits.
2. Distinguish logical partitioning, physical partitioning, and sharding while recognising that systems use these terms differently.
3. Evaluate range, hash, composite, and directory/lookup distribution strategies.
4. Select partition-key candidates using access patterns, cardinality, key frequency, growth, write patterns, and cross-partition operations.
5. Distinguish balanced data volume from balanced request load and resource use.
6. Calculate skew ratios and explain what they can and cannot prove.
7. Estimate effective capacity under explicit simplifying assumptions.
8. Explain data skew, request skew, resource skew, hot keys, and hot partitions.
9. Compare repartitioning, rebalancing, and resharding, including movement, consistency, availability, and rollback risks.
10. Design hotspot mitigations such as composite keys, salting, adaptive splitting, rate limiting, and read replicas where appropriate.
11. Build a controlled validation plan with realistic key distributions and measurable acceptance criteria.
12. Produce a scaling requirements profile, partition-key evaluation, distribution/skew analysis, strategy comparison, hotspot proposal, and validation plan.

### 1.2 Scope and boundaries

This lesson covers how data and workload are distributed to meet capacity, performance, availability, and operational needs. It is not a full course on query tuning, caching, detailed streaming administration, or formal cost modelling.

- **Topic 01 — Capacity planning and growth forecasting:** estimates demand, peak load, growth, and headroom.
- **Topic 02 — Throughput, latency, concurrency and queueing:** explains how load and waiting affect response time.
- **Topic 03 — Query performance and data locality:** examines scan work, joins, shuffle, and movement within query execution.
- **Topic 04 — This lesson:** decides how to distribute data and work, and how to handle imbalance.
- **Topic 05 — Caching, materialisation and serving trade-offs:** evaluates avoiding repeated work, freshness, and serving patterns.
- **Topic 06 — Cost modelling, unit economics and FinOps:** prices capacity and operational trade-offs.
- **Topic 07 — Performance testing and capacity validation:** formalises repeatable tests and acceptance criteria.
- **Topic 08 — Architecture optimisation with measured evidence:** integrates evidence and recommendations.

The module roadmap identifies Topic 04 prerequisites as **Seq 2–3; P4, P7**: throughput/latency/concurrency and query performance/data locality, plus partitioning and streaming-partition/backlog concepts. Examples here are self-contained and require no production account.

### 1.3 Governing principle

> Distribute work according to the workload you actually have, not according to a diagram that assumes every key is equally popular.

A distribution design must be evaluated against reads, writes, scans, joins, ingestion, query fan-out, consistency, failure handling, and future growth. No single partition key is best for every workload.

---

## 2. Prerequisites and connections to Topics 01–03

### 2.1 Topic 01: capacity and growth

Bring forward the workload profile: event/transaction rates, peak-to-average ratio, growth, retention, storage volume, and headroom. A design that meets today's average load may fail at month-end or during a promotion. Capacity estimates should include ranges and uncertainty rather than a single falsely precise number.

A capacity requirement should name the unit of work. “Ten thousand requests per second” is not sufficient if some requests are tiny lookups and others are large scans or multi-shard transactions.

### 2.2 Topic 02: throughput, latency, concurrency, and queueing

A saturated partition can create queues even when the cluster as a whole appears underused. Record throughput and latency by partition/shard or workload class where possible, not only cluster-wide averages.

Useful measures include completed operations per second, p50/p95/p99 latency, timeout/error rate, queued and in-flight work, resource utilisation, wait time, and per-partition input/output rates or lag. Averages can hide the busiest partition and tail latency. The slowest shard may bound a scatter-gather request's completion time, especially when the response requires all shards.

### 2.3 Topic 03: query performance and locality

A query can become expensive when data needed together is distributed across many workers. A partition key that spreads writes evenly may scatter range queries or joins. A locality-friendly design can reduce movement for common queries, but may concentrate writes on a hot partition.

Use Topic 03 concepts to understand which bytes move and where a query spends time. Use this topic to decide whether the data distribution itself should change.

### 2.4 Stateless and stateful scaling

- **Stateless services** can often add replicas behind a load balancer with limited state movement, assuming sessions and dependencies are handled appropriately.
- **Stateful services** own or coordinate durable data, partition ownership, stream state, or local state. Scaling may require transferring state, moving data, changing routing, coordinating ownership, or preserving consistency during the transition.

Stateless scale-out is not cost-free: shared databases, connection pools, queues, or downstream services may become bottlenecks. Stateful scale-out is usually more involved because data and ownership must remain correct while the system changes.

---

## 3. Beginner level: scaling and distribution fundamentals

### 3.1 Scale up versus scale out

Imagine a checkout area:

- **Scale up:** replace one cashier with a faster cashier and a larger checkout station.
- **Scale out:** open more checkout lanes.
- **Hotspot:** every shopper insists on using one particular lane, leaving other lanes idle.

A larger cashier may help until the station reaches physical, software, or cost limits. More lanes increase aggregate capacity only if shoppers and tasks can be distributed among them.

| Dimension | Scale up (vertical) | Scale out (horizontal) |
|---|---|---|
| Basic change | Larger machine/resource | More machines/workers/shards |
| Potential benefit | More CPU, memory, I/O, or bandwidth per unit | More aggregate capacity and parallelism |
| Limit | Hardware/resource ceiling; diminishing returns; expensive larger instances | Coordination, communication, routing, skew, partition count, quotas |
| Data movement | Often lower, though upgrades can still require migration/restart | May require redistribution and cross-node communication |
| Application complexity | May remain simpler | Often requires distribution-aware access and failure handling |
| Failure domain | One larger node can remain a larger single failure domain | Can improve fault isolation if designed for it; coordination adds failure modes |
| Good fit | Workload benefits from larger shared memory/CPU or has limited parallelism | Work can be divided and distributed with acceptable coordination |
| Common failure | Buy a larger resource without fixing serial work or skew | Add nodes while a hot key or shared dependency remains the bottleneck |

Neither is universally better. A hybrid design may scale up within each node and scale out across nodes.

### 3.2 Why adding nodes is not linear

If one worker processes 1,000 operations/s, it is tempting to assume eight workers process 8,000 operations/s. That assumes independent, evenly distributed work with no coordination, network, storage, scheduling, or serial bottleneck. Real systems rarely satisfy all of those assumptions.

A useful conceptual model is:

\[
C_{effective} \leq \min(C_{compute}, C_{storage}, C_{network}, C_{coordination}, C_{hottest\ partition})
\]

This is not a universal capacity equation. It reminds us that the system is constrained by its limiting component. Adding compute does little if a shared storage path, one partition, or a serial coordinator remains saturated.

### 3.3 Key terms

| Term | Meaning |
|---|---|
| Partition | A subset of data or work managed as a unit; it may be logical, physical, or execution-oriented. |
| Partition key | Attribute(s) used to decide which partition receives a record or request. |
| Shard | A partition assigned to a node, storage group, or independently managed data unit in a distributed system. |
| Sharding | Distributing shards across nodes or groups. In some systems, “partitioning” and “sharding” overlap or are used synonymously. |
| Range partitioning | Assigns ordered key ranges to partitions. |
| Hash partitioning | Applies a hash function to a key and maps the result to a partition. |
| Composite key | Combines attributes, such as a hash prefix and a time value. |
| Directory/lookup routing | Uses a mapping from key or tenant to partition/shard. |
| Skew | Uneven distribution of data, requests, work, or resource consumption. |
| Hot key | One key receives a disproportionately large share of requests or records. |
| Hot partition / hotspot | A partition, shard, node, or resource is disproportionately loaded. |
| Rebalancing | Redistributing ownership or workload among existing/new partitions or nodes. |
| Resharding | Changing shard allocation or shard count/strategy, often involving data movement and routing updates. |
| Fan-out / scatter-gather | Send a request to multiple partitions, then combine their responses. |
| Replication | Keeping copies of data on multiple nodes for availability, read capacity, or resilience. |

### 3.4 Partitioning versus sharding

The words are context-dependent; do not treat one definition as a law for every product.

- **Logical partitioning** divides a dataset into named or predicate-defined subsets, such as daily partitions in a warehouse table.
- **Physical partitioning** lays data out in separate files, blocks, segments, or storage units.
- **Sharding** typically means assigning data partitions to different nodes or independently managed groups so storage and work can scale horizontally.

A table can be partitioned by date inside each shard, and each shard can be distributed to a node. A distributed database may call its node-owned units “partitions” even when they are functionally shards. State what the design means operationally: what unit is split, who owns it, how routing works, and how it moves.

### 3.5 Why partition at all?

Partitioning may serve several purposes:

1. **Storage management:** isolate data by date, tenant, or lifecycle.
2. **Query pruning:** avoid reading irrelevant units when predicates align with the partition scheme.
3. **Parallel processing:** allow independent tasks to work on separate subsets.
4. **Write distribution:** spread ingestion or mutations across owners.
5. **Workload isolation:** keep some tenants or workload classes from overwhelming others.
6. **Failure and recovery boundaries:** restore, replicate, or move subsets independently.

A scheme that helps one purpose can harm another. Date partitions can prune time-range queries but create a hot “current day” write target. Tenant partitions can improve isolation but create one oversized partition for a large tenant.

---

## 4. Capacity distribution and workload balance

### 4.1 Define the unit of load

Before measuring balance, state what is distributed: bytes stored, rows/events ingested, read requests, write requests, CPU seconds, network bytes, query tasks, queued work, resource utilisation, or service-level violations.

Equal data volume does not guarantee equal request load. Equal request count does not guarantee equal work if request costs differ.

### 4.2 Skew ratio

The module roadmap defines the simple measure:

\[
\text{skew ratio} = \frac{\text{maximum partition load}}{\text{mean partition load}}
\]

For loads `[10, 10, 10, 70]`:

- Total load = 100.
- Number of partitions = 4.
- Mean load = 100 / 4 = 25.
- Maximum load = 70.
- Skew ratio = 70 / 25 = 2.8.

A ratio of 1 means equal measured load when the mean is nonzero. A ratio of 2.8 means the busiest partition has 2.8 times the mean load for the metric being measured.

**Limitations:** the ratio hides the shape of the distribution, does not identify the cause, and depends on the chosen metric and measurement window. Show per-partition values alongside the ratio.

### 4.3 Effective capacity approximation

The roadmap gives the intuition:

\[
\text{effective capacity} \approx \frac{\text{total capacity}}{\text{skew ratio}}
\]

This is a **rough approximation** when partitions have similar independent capacity, the maximum-load partition limits throughput, and the skew metric is proportional to resource demand. It is not a universal capacity law.

If four equal-capacity partitions have a skew ratio of 2.8, the rough estimate is \(4 / 2.8 \approx 1.43\) balanced-partition equivalents. This is not a literal count of machines and does not account for spare headroom, non-linear queues, workload differences, or other bottlenecks.

### 4.4 Data skew, request skew, and resource skew

| Type | What is uneven | Example | Why it matters |
|---|---|---|---|
| Data skew | Stored rows/bytes/key counts | One customer has 30% of all transactions | One partition can be much larger and slower to scan, join, compact, or restore |
| Request skew | Requests per key/partition | One product is requested 40% of the time | One shard receives disproportionate reads/writes even if data size is balanced |
| Resource skew | CPU, I/O, memory, network, or task time | Each partition has similar rows, but one performs expensive joins | Equal row counts can still produce unequal latency and utilisation |

These types can occur independently. A small key can be a request hotspot; a large partition can be cold; equal requests can produce resource skew because request complexity differs.

---

## 5. Worked examples

All data sizes, request rates, and capacity values below are illustrative assumptions, not production measurements or performance promises.

### 5.1 Example A — scale-up or scale-out?

Assume a batch job must process 12 million records within 20 minutes. One worker is measured in a controlled test at 8,000 records/s on this workload. Ignore startup and coordination for the first estimate.

Required average rate:

\[
12{,}000{,}000 / (20 \times 60) = 10{,}000 \text{ records/s}
\]

One worker at 8,000 records/s does not meet the target. Under an ideal linear model, two equivalent workers would provide 16,000 records/s, but that is only a planning upper bound.

Before adding workers, determine whether the workload divides into independent units, records have similar processing cost, shared storage/network has enough throughput, a serial stage exists, state must move, output ordering or cross-record coordination is required, and the measured rate includes realistic I/O and contention.

Scale-up could be sufficient if a larger worker improves the bottleneck and the job cannot be parallelized efficiently. Scale-out could be better if partitions are independent and movement/coordination overhead is acceptable. Validate with a representative test.

### 5.2 Example B — twelve keys, three shards

For a reproducible classroom example, keys are integers 0 through 11. We use the explicit assignment `key % 3`; this is a simple hash-like demonstration, not a production hash function.

**Modulo assignment:**

| Key | Shard (`key % 3`) |
|---:|---:|
| 0 | 0 |
| 1 | 1 |
| 2 | 2 |
| 3 | 0 |
| 4 | 1 |
| 5 | 2 |
| 6 | 0 |
| 7 | 1 |
| 8 | 2 |
| 9 | 0 |
| 10 | 1 |
| 11 | 2 |

Each shard receives four keys. With equal request probability and equal work per key, the distribution is balanced.

**Range assignment:** split the ordered keys into three equal ranges:

- Shard 0: keys 0–3
- Shard 1: keys 4–7
- Shard 2: keys 8–11

This is also balanced for this tiny set. But range assignment preserves key locality: a query for keys 4–7 targets one shard. A hash-style mapping scatters nearby keys across shards, so a range query may need to contact all three.

A balanced key count does not guarantee balanced traffic. If key `7` receives 60% of requests, the range shard containing it becomes hot even though each shard stores four keys.

### 5.3 Example C — poor partition key: current timestamp

Suppose a write-heavy event stream is partitioned by the exact current timestamp or by a very narrow time bucket. Most new writes target the current bucket. Older partitions are mostly idle.

Possible consequences: one partition/shard receives most ingestion; the system cannot use all nodes' write capacity; the hot partition queues or throttles; adding nodes does not help unless the hot bucket can be split or routing changes.

A composite design such as `(hash(tenant_id), time_bucket)` or a controlled hash prefix plus time can spread writes while retaining some time locality. The exact design depends on queries and engine support. If every query must scan every hash prefix for a time range, the write benefit creates read fan-out.

### 5.4 Example D — balanced data, unbalanced requests

Four shards each store 1 TiB. Each shard has comparable CPU and storage capacity. However, one popular tenant receives 50% of all requests and is assigned to shard 2. Request shares may be 15%, 17%, 50%, and 18%.

Shard 2 can hit CPU or connection limits while the other shards remain underutilised. Collect per-shard request rate, request cost, latency percentiles, queue depth, and resource use—not just bytes stored.

### 5.5 Example E — calculate skew and rough effective capacity

Assume four equal-capacity partitions show CPU demand units `[10, 10, 10, 70]` over the same interval.

- Mean = 25 units.
- Max = 70 units.
- Skew ratio = 2.8.
- Rough effective balanced-partition equivalents = 4 / 2.8 ≈ 1.43.

Interpretation: if the busiest partition is the limiting resource and the workload/capacity assumptions hold, the four-partition system may deliver throughput closer to 1.43 balanced partitions than four. This is a diagnostic approximation, not a measured throughput figure. Confirm using throughput, queueing, and per-partition utilisation.

### 5.6 Example F — modulo resharding versus consistent hashing

Suppose a simple modulo scheme assigns a key to `hash(key) % N`. Increasing shard count from \(N\) to \(N+1\) changes the divisor, so many keys map to different shards.

Under a uniform hash distribution and a naive reassignment to the new modulo scheme, the approximate fraction of keys that remain on the same shard is \(1/(N+1)\), so the fraction expected to move is:

\[
1 - \frac{1}{N+1} = \frac{N}{N+1}
\]

For \(N=10\), this is \(10/11 \approx 90.9\%\) of keys expected to move. This is a simplified expectation for modulo mapping, not a universal data-movement guarantee: actual bytes moved depend on key sizes, data placement, replication, and implementation.

A consistent-hashing ring can be designed so that adding one of \(N+1\) equally sized owners moves roughly \(1/(N+1)\) of key space in an idealized balanced case. Real systems use virtual nodes, tokens, range maps, or other schemes; balance and movement depend on implementation and current ownership.

Even when only a fraction of keys moves, rebalancing can be disruptive because of network limits, replica synchronization, disk I/O, foreground contention, and cutover coordination.

---

## 6. Partition-key evaluation and distribution strategies

### 6.1 A partition key is a workload decision

Evaluate candidate keys against actual access patterns, not just uniqueness or convenience.

Questions to ask:

1. Which operations are most frequent and most latency-sensitive?
2. Which attributes appear in routing predicates?
3. Are writes append-only, update-heavy, or time-ordered?
4. Is the key distribution uniform, Zipf-like, tenant-skewed, or bursty?
5. Can one tenant/customer/key grow much larger than others?
6. Which queries need ranges, joins, global aggregates, or multiple tenants?
7. What consistency or transaction boundaries must be preserved?
8. How many partitions will exist now and at expected growth?
9. What happens when the partition count changes?
10. Can a hot key be split without breaking ordering, uniqueness, or transaction semantics?

High cardinality is often helpful for hash distribution, but it does not guarantee balance. A key can have millions of distinct values and still have one value that dominates requests.

### 6.2 Range partitioning

**Mechanism:** assign contiguous ranges of an ordered key to partitions. Examples include time intervals, numeric ID ranges, or lexical ranges.

**Strengths:** efficient range routing/pruning when predicates align; ordered locality for scans; understandable boundaries in some systems.

**Risks:** monotonically increasing keys can concentrate new writes in the latest range; historical ranges may differ in size/activity; skewed distributions produce uneven partitions; boundary changes may require splitting and moving data; queries spanning many ranges may fan out.

Range partitioning is attractive when range access is central and data distribution is manageable. It needs special care for append-heavy time series.

### 6.3 Hash partitioning

**Mechanism:** apply a stable hash function to the partition key, then map the result to an owner/partition. A simple teaching form is `hash(key) mod N`.

**Strengths:** spreads diverse keys when the hash and key distribution behave well; supports targeted point lookups when the key is known; avoids monotonic-key hotspots in many designs.

**Risks:** range locality is lost; queries without the key may scatter across shards; a single hot key still maps to one partition; changing `N` in modulo hashing can remap many keys; poor or unstable routing can create imbalance or correctness issues.

Hashing distributes keys, not requests within one key. A popular tenant remains a hot key unless the design can split or replicate that tenant's work.

### 6.4 Composite distribution: prefix plus range

A composite scheme combines attributes or routing stages, for example a hash prefix and time bucket.

**Potential benefit:** spread writes across sub-partitions while retaining time locality within each prefix.

**Costs:** time-range queries may have to read every prefix; ordering may only be preserved within each prefix; partition management and query logic become more complex. Validate both write distribution and the fan-out cost of common reads.

### 6.5 Directory / lookup-based routing

A directory maps a logical key or tenant to a physical shard. This can support uneven shard sizes, tenant movement, and controlled placement.

**Benefits:** placement can change without changing the logical key; large tenants can be moved or isolated; routing can reflect observed workload.

**Costs:** directory availability and latency become dependencies; cached mappings can become stale; updates must be coordinated with data movement; the directory itself can become a hotspot if not designed to scale.

The directory must define cutover behavior: when a mapping changes, how do reads and writes avoid being lost, duplicated, or routed to stale owners?

### 6.6 Strategy comparison

| Strategy | Strong fit | Common weakness | Important validation |
|---|---|---|---|
| Range | Time/range scans and ordered access | Hot current range; uneven ranges | Per-range volume/rate, range-query fan-out |
| Hash | Point access and spreading diverse keys | Poor range locality; one hot key remains hot | Key and request distributions, remap cost |
| Composite hash + time | Append-heavy workload needing write spread and time queries | Read fan-out and more complex boundaries | Per-prefix load and query fan-out |
| Directory/lookup | Tenant placement and flexible movement | Lookup dependency and routing consistency | Directory latency/availability, stale-map behavior |
| Tenant-per-shard | Isolation and tenant-level operations | Large/small tenant imbalance and noisy neighbours | Per-tenant workload and largest-tenant growth |
| Replicas | Read scaling and availability | Does not inherently scale primary writes; replication lag | Read/write mix, freshness, failover and lag |
| Separate analytical layout/copy | Different scan and ingestion access patterns | Duplicate storage and data movement/consistency | Freshness, load isolation, refresh cost |

### 6.7 Partition boundaries and partition count

Too few partitions can limit parallelism and create large failure/recovery units. Too many can increase metadata, file counts, scheduling overhead, routing complexity, and small-partition costs.

There is no universal ideal partition size or count. Choose a target range based on workload parallelism and task duration; per-partition bytes and request rate; metadata and file-listing time; compaction/recovery time; storage/compute limits; and expected growth/rebalancing behavior.

Do not create one partition for every distinct customer or timestamp by default. High cardinality may create an enormous number of tiny partitions and an expensive control plane.

---

## 7. Intermediate level: rebalancing, movement, and workload isolation

### 7.1 Repartitioning, rebalancing, and resharding

These terms overlap in practice; state the exact operation in a design document.

- **Repartitioning:** change how records are divided, such as changing partition boundaries or the key.
- **Rebalancing:** redistribute current data or ownership to make resource usage more even.
- **Resharding:** change shard count, assignments, or routing strategy, usually across nodes.

Potential reasons include growth, a hot partition, node replacement, changing access patterns, tenant isolation, or capacity limits.

### 7.2 A migration is a correctness problem, not just a copy job

A safe migration plan addresses:

1. **Inventory:** data volume, key distribution, current ownership, replicas, and active workload.
2. **Target layout:** new key/partition map and why it addresses measured imbalance.
3. **Copy strategy:** snapshot, streaming changes, dual writes, log-based replication, or another controlled method.
4. **Consistency:** how updates arriving during copy are captured and reconciled.
5. **Routing:** how clients find the authoritative owner before, during, and after transition.
6. **Cutover:** the condition for switching traffic and how in-flight operations are handled.
7. **Validation:** row/key counts, checksums, sampled values, invariants, and application-level results.
8. **Rollback:** how to return to previous routing and data state without losing acknowledged writes.
9. **Capacity:** extra source/target CPU, network, disk, and replica traffic during migration.
10. **Cleanup:** when old copies can be removed safely and how to prove they are no longer needed.

A naive copy followed by a routing switch can lose writes made after the snapshot. Dual-write approaches can create duplicates or partial success unless idempotency, ordering, retries, and reconciliation are designed explicitly.

### 7.3 Online and offline approaches

| Approach | Advantage | Risk / limitation |
|---|---|---|
| Offline migration with maintenance window | Simpler consistency and cutover reasoning | Downtime; window may be too short for large data |
| Snapshot plus change capture | Can reduce downtime while catching up | Capture ordering, lag, replay, and reconciliation complexity |
| Dual writes | Can maintain both destinations during transition | Partial failures and divergent copies; idempotency needed |
| Proxy/directory-based routing | Can abstract physical movement from clients | Proxy/directory becomes critical infrastructure |
| Gradual key-range/tenant migration | Limits blast radius and supports staged validation | Mixed old/new state and routing complexity |
| Add read replicas | Can improve read capacity without moving primary ownership | Does not solve write hotspots; stale reads/failover considerations |

Choose based on correctness guarantees, data volume, downtime tolerance, recovery requirements, and operational maturity—not on a generic claim that online migration is always safer.

### 7.4 Cross-partition queries and scatter-gather

If a request does not include the shard key, it may need to query many or all shards. The response often waits for the slowest required shard plus coordination and merge work.

If shard response times are independent and a request waits for all \(n\) shards, the probability that every shard finishes within time \(t\) is:

\[
P(\max(T_1,\ldots,T_n) \le t) = \prod_{i=1}^{n} P(T_i \le t)
\]

If all shards have the same independent probability \(p\) of finishing within \(t\), this becomes \(p^n\). For example, if each of 8 shards has a 99% chance of finishing within a threshold, the chance that all 8 finish within that threshold is \(0.99^8 \approx 92.3\%\). This is an illustrative independence model; real shard times can be correlated, and request deadlines/retries alter the behavior.

Reduce unnecessary fan-out by including the routing key, maintaining a suitable aggregate/index/copy, or changing the serving model. Such alternatives add freshness, storage, or maintenance trade-offs (expanded in Topic 05).

### 7.5 Replication and availability

Replication can improve read capacity, availability, and recovery, but introduces data movement and consistency concerns. Consider synchronous versus asynchronous replication; replica lag and freshness requirements; failover behavior and split-brain prevention; read-after-write and transaction guarantees; write amplification and network/storage overhead; failure-domain placement; and whether the primary remains the write hotspot.

Adding read replicas does not automatically distribute primary writes. If a single key or primary partition is overloaded by writes, the design needs write distribution, key splitting, buffering/rate limits, or another targeted response.

### 7.6 Multi-tenancy and noisy neighbours

A shared shard can be dominated by one tenant's batch job or request burst. Tenant-aware quotas, admission control, workload pools, or dedicated placement can reduce interference. Dedicated shards improve isolation but can strand capacity for small tenants and increase operational overhead.

Track per-tenant request rates, work per request, storage, latency, queue depth, and errors. Do not assume equal tenant count means equal workload.

---

## 8. Advanced level: hotspots and mitigation

### 8.1 Detect the hotspot before choosing the remedy

Useful evidence includes per-partition read/write rate and bytes; CPU, memory, disk/network utilisation; queue depth, throttling, errors, and tail latency; key-frequency distributions and tenant-level workload; task duration, input size, and spill where applicable; and time-aligned events such as promotions, batch jobs, month-end, or backfills.

A cluster-wide average can conceal one saturated partition. A single high metric is not enough: high CPU may be expected if throughput is high and latency remains within target; low CPU with high latency may indicate I/O, queueing, or downstream waits.

### 8.2 Mitigation patterns

#### A. Split a hot partition

Create smaller units and redistribute them. This can reduce per-unit load if routing can spread work across owners. It may increase metadata, fan-out, and coordination, and may not help if all requests still target the same indivisible key.

#### B. Salt a hot key

Salting adds a bounded suffix/prefix to distribute one logical key across multiple physical keys, such as `(customer_id=42, salt=0..3)`. A write path can choose a salt using a stable hash of a secondary attribute or a controlled distribution. Reads by logical customer may then need to query all salt buckets and merge results. Aggregates may need a two-stage combine. Uniqueness, ordering, transactions, and updates must be preserved.

Salting trades write spread for read fan-out and complexity. Random salting can make deterministic updates or idempotency harder unless the mapping is designed carefully.

#### C. Composite hash prefix plus time

This can spread writes across several prefixes while retaining some time locality. A time-range query may need to scan all prefixes, and global ordering may require a merge. Measure per-prefix load and actual query fan-out.

#### D. Handle a large tenant separately

Move a known large tenant to dedicated capacity or a dedicated shard while smaller tenants remain pooled. This can improve isolation but requires routing, operational automation, and a plan for tenants that grow or shrink.

#### E. Rate limit or apply admission control

Cap the rate or concurrency sent to a hot partition, or reject/defer low-priority work. This protects the system but can increase client latency, queueing, retries, or rejected work. Retry policy must include backoff/jitter and respect idempotency; immediate retries can intensify the hotspot.

#### F. Buffer and smooth writes

A queue or batch buffer can smooth bursts and coalesce updates. It does not increase the sustained capacity of the destination. If average arrival rate exceeds sustained processing rate, backlog grows until the producer is throttled or capacity changes.

#### G. Add read replicas or cache hot reads

This can help read-heavy hotspots when consistency/freshness allow it. It does not solve primary write contention and introduces replica lag or cache staleness. Detailed cache selection belongs to Topic 05.

#### H. Change the distribution key

A new key may spread work more effectively, but can make important queries scatter, complicate transactions, or require large data movement. Change the key only after workload and skew evidence show the current key is a problem.

### 8.3 Choosing among mitigations

| Observed problem | Candidate response | Main risk | Validation evidence |
|---|---|---|---|
| Hot key dominates writes | Salt, composite key, isolate tenant, rate limit | Read fan-out, consistency complexity, delayed writes | Per-key write rate, queueing, read fan-out, correctness |
| Latest time partition is hot | Hash prefix + time, split current range, buffer | More range-query fan-out or latency | Per-prefix writes, time-range query cost |
| Data sizes uneven | Rebalance, split large partition, move tenant | Migration I/O and cutover risk | Bytes/rows per partition, movement duration, service impact |
| Requests uneven but data balanced | Route/replicate reads, isolate hot tenant, quotas | Staleness or wasted capacity | Request rate and latency per shard |
| One shard has long query tasks | Revisit query plan/locality, partition key, skew handling | More shuffle or duplicate work | Task-duration spread, bytes moved, output correctness |
| Cluster underutilized but p95 high | Check single hot resource, serial dependency, queueing | Scaling the wrong layer | Per-shard utilisation, critical path, wait events |
| All shards are busy similarly | Scale up/out or reduce work per request | Cost and coordination overhead | Load-versus-capacity curve, latency and throughput |

### 8.4 Dynamic hotspots and autoscaling

Hotspots can be time-dependent: a trending product, one large customer, a daily time boundary, month-end, or a backfill. Static partitioning may not be enough.

Autoscaling adds resources after a trigger, but detection and provisioning have delay; state may need to move before new capacity helps; the hot key may remain assigned to one owner; quotas or partition count may cap useful parallelism; scaling down too early can cause oscillation; and adding nodes may increase coordination or network traffic.

Autoscaling is effective when the workload can use new capacity and the system can redistribute work. It cannot fix an indivisible serial operation or a key that remains pinned to one partition.

---

## 9. Capacity, performance, and cost trade-offs

This lesson identifies cost drivers but does not price them; formal modelling belongs in Topic 06.

| Design | Capacity upside | Limiting factor | Operational/cost consideration |
|---|---|---|---|
| One larger node | Larger per-node CPU/memory/I/O | Resource ceiling and serial work | Larger unit may be expensive; maintenance/failure domain |
| More homogeneous nodes | Aggregate parallelism | Skew, coordination, network, partition count | More fixed overhead and distributed operations |
| More partitions on same nodes | More task granularity and potentially better balance | Scheduler/metadata overhead; physical resources unchanged | More small units and management complexity |
| Read replicas | More read-serving capacity | Primary writes and replication lag | Extra storage/network and replica operations |
| Dedicated hot-tenant shard | Isolation for large/noisy tenant | Hot key inside tenant may remain | Lower sharing efficiency; more operational units |
| Salted/composite key | Splits selected hot-key workload | Read fan-out and multi-key coordination | More complex query and correctness logic |
| Buffering/throttling | Smooths bursts and protects service | Sustained capacity unchanged | Backlog/latency or rejected work |
| Separate analytical copy/layout | Isolates scans from operational access | Refresh/consistency and duplicated storage | Data movement, freshness, maintenance |

### 9.1 Capacity and headroom

Do not size only for average throughput. Define expected average and peak arrival rates; key and tenant distribution under peak conditions; target latency and error rate; per-partition safe throughput at that objective; failover and maintenance headroom; and expected growth/resharding thresholds.

A system can have enough aggregate capacity on paper but still violate service objectives because one shard saturates first. Use per-shard capacity under realistic distributions rather than multiplying one-node benchmark throughput by node count.

### 9.2 Avoid false precision in cost estimates

Relevant cost drivers include compute/node count, storage, network transfer, replication, migration/rebalancing, extra copies, metadata, operations, and capacity stranded for isolation. Cost per request or per processed record is useful only when the denominator and included workload are clear.

Do not call a design cheaper because it uses fewer nodes without accounting for slower queries, more retries, extra transfer, operational burden, or required replicas. Conversely, the fastest design may not be justified for an infrequent noncritical workload.

---

## 10. Python demonstrations and reproducible tests

These standard-library examples are deterministic teaching models, not simulations of a specific database or distributed runtime. They use explicit integer/modulo assignment for reproducibility rather than Python's process-randomized built-in `hash()`. The examples require Python 3.9 or later because they use built-in generic type annotations such as `dict[int, list[int]]`.

### 10.1 Assign keys to shards and count distribution

```python
from typing import Callable, Iterable


def _require_positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def assign_modulo(key: int, shard_count: int) -> int:
    _require_positive_int(shard_count, "shard_count")
    if isinstance(key, bool) or not isinstance(key, int):
        raise ValueError("key must be an integer (booleans are not valid keys)")
    return key % shard_count


def distribute_keys(
    keys: Iterable[int],
    shard_count: int,
    assign: Callable[[int, int], int] = assign_modulo,
) -> dict[int, list[int]]:
    _require_positive_int(shard_count, "shard_count")
    if not callable(assign):
        raise ValueError("assign must be callable")
    result = {shard: [] for shard in range(shard_count)}
    for key in keys:
        if isinstance(key, bool) or not isinstance(key, int):
            raise ValueError(f"key must be an integer (booleans are not valid keys): {key!r}")
        shard = assign(key, shard_count)
        if isinstance(shard, bool) or not isinstance(shard, int) or shard not in result:
            raise ValueError(f"assignment returned invalid shard: {shard!r}")
        result[shard].append(key)
    return result


def distribution_counts(distribution: dict[int, list[int]]) -> dict[int, int]:
    return {shard: len(keys) for shard, keys in distribution.items()}


def test_distribution() -> None:
    keys = list(range(12))
    result = distribute_keys(keys, 3)
    assert distribution_counts(result) == {0: 4, 1: 4, 2: 4}
    assert sorted(key for group in result.values() for key in group) == keys
    assert distribution_counts(distribute_keys([], 3)) == {0: 0, 1: 0, 2: 0}
    assert distribution_counts(distribute_keys([-2, -1, 0, 1], 3)) == {0: 1, 1: 2, 2: 1}
    for invalid_count in (0, -1, 1.5, True):
        try:
            distribute_keys(keys, invalid_count)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid shard count should fail")
    for invalid_key in ("7", 1.5, True, None):
        try:
            distribute_keys([invalid_key], 3)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid key should fail")
    for invalid_assignment in (lambda key, count: -1, lambda key, count: 1.0, lambda key, count: True):
        try:
            distribute_keys([1], 3, invalid_assignment)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid shard assignment should fail")


if __name__ == "__main__":
    test_distribution()
    print("Modulo counts:", distribution_counts(distribute_keys(range(12), 3)))
    print("All distribution assertions passed.")
```

Expected output:

```text
Modulo counts: {0: 4, 1: 4, 2: 4}
All distribution assertions passed.
```

### 10.2 Measure skew and approximate balanced capacity

```python
import math
from numbers import Real
from typing import Iterable


def _finite_nonnegative_number(value: Real) -> bool:
    return not isinstance(value, bool) and isinstance(value, Real) and math.isfinite(value) and value >= 0


def skew_ratio(loads: Iterable[float]) -> float:
    values = list(loads)
    if not values:
        raise ValueError("loads must not be empty")
    if any(not _finite_nonnegative_number(value) for value in values):
        raise ValueError("loads must be finite, numeric, and non-negative")
    scale = max(values)
    if scale == 0:
        return 1.0  # explicit convention for an all-zero measurement window
    # Normalise before summing to avoid overflow for very large finite values.
    mean_scaled = sum(value / scale for value in values) / len(values)
    return 1.0 / mean_scaled


def effective_partition_equivalents(partition_count: int, ratio: float) -> float:
    if isinstance(partition_count, bool) or not isinstance(partition_count, int) or partition_count <= 0:
        raise ValueError("partition_count must be a positive integer")
    if not _finite_nonnegative_number(ratio) or ratio < 1:
        raise ValueError("skew ratio must be finite and at least 1")
    return partition_count / ratio


def test_skew() -> None:
    assert abs(skew_ratio([10, 10, 10, 70]) - 2.8) < 1e-12
    assert skew_ratio([5, 5, 5, 5]) == 1.0
    assert skew_ratio([0, 0, 0]) == 1.0
    assert abs(skew_ratio([1e308, 1e308]) - 1.0) < 1e-12
    assert abs(skew_ratio([1e308, 1e307]) - (1e308 / ((1e308 + 1e307) / 2))) < 1e-12
    assert abs(effective_partition_equivalents(4, 2.8) - (4 / 2.8)) < 1e-12
    for bad_loads in ([], [-1, 2], [float("nan"), 1], [float("inf"), 1], [True, 1], ["3", 1]):
        try:
            skew_ratio(bad_loads)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid loads should fail")
    for bad_count in (0, -1, 1.5, True):
        try:
            effective_partition_equivalents(bad_count, 2.0)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid partition count should fail")
    for bad_ratio in (0.9, 0, float("nan"), float("inf"), True):
        try:
            effective_partition_equivalents(4, bad_ratio)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid skew ratio should fail")


if __name__ == "__main__":
    test_skew()
    print("Skew ratio:", skew_ratio([10, 10, 10, 70]))
    print("Effective partition equivalents:", effective_partition_equivalents(4, 2.8))
    print("All skew assertions passed.")
```

Expected output:

```text
Skew ratio: 2.8
Effective partition equivalents: 1.4285714285714286
All skew assertions passed.
```

The zero-load convention is explicit: if all measured loads are zero, the function returns 1.0 rather than dividing by zero. In an operational report, also state that there was no observed load during the measurement window.

### 10.3 Detect a hot key from request counts

```python
import math
from numbers import Real
from typing import Hashable


def hot_keys(
    request_counts: dict[Hashable, int],
    threshold_fraction: float,
) -> dict[Hashable, float]:
    if isinstance(threshold_fraction, bool) or not isinstance(threshold_fraction, Real) or not math.isfinite(threshold_fraction) or not 0 < threshold_fraction <= 1:
        raise ValueError("threshold_fraction must be finite and in (0, 1]")
    if any(isinstance(count, bool) or not isinstance(count, int) or count < 0 for count in request_counts.values()):
        raise ValueError("request counts must be non-negative integers")
    total = sum(request_counts.values())
    if total == 0:
        return {}
    return {
        key: count / total
        for key, count in request_counts.items()
        if count / total >= threshold_fraction
    }


def test_hot_key_detection() -> None:
    counts = {"A": 500, "B": 200, "C": 200, "D": 100}
    assert hot_keys(counts, threshold_fraction=0.30) == {"A": 0.5}
    assert hot_keys({"A": 0, "B": 0}, 0.1) == {}
    assert hot_keys({}, 0.1) == {}
    for bad_threshold in (0, 1.1, float("nan"), float("inf"), True):
        try:
            hot_keys(counts, bad_threshold)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid threshold should fail")
    for bad_counts in ({"A": -1}, {"A": 1.5}, {"A": True}, {"A": float("inf")}):
        try:
            hot_keys(bad_counts, 0.1)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid request counts should fail")


if __name__ == "__main__":
    test_hot_key_detection()
    print("Hot keys:", hot_keys({"A": 500, "B": 200, "C": 200, "D": 100}, 0.30))
    print("All hot-key assertions passed.")
```

Expected output:

```text
Hot keys: {'A': 0.5}
All hot-key assertions passed.
```

This detects keys exceeding a chosen share of total requests. The threshold is a diagnostic setting, not a universal definition of a hotspot. A key with a lower share can still be hot if its requests are much more expensive.

### 10.4 Simulate a salted hot key

```python
def salt_loads(total_requests: int, salt_buckets: int) -> list[int]:
    if isinstance(total_requests, bool) or not isinstance(total_requests, int) or total_requests < 0:
        raise ValueError("total_requests must be a non-negative integer")
    if isinstance(salt_buckets, bool) or not isinstance(salt_buckets, int) or salt_buckets <= 0:
        raise ValueError("salt_buckets must be a positive integer")
    base, remainder = divmod(total_requests, salt_buckets)
    return [base + (1 if i < remainder else 0) for i in range(salt_buckets)]


def test_salt_loads() -> None:
    loads = salt_loads(101, 4)
    assert loads == [26, 25, 25, 25]
    assert sum(loads) == 101
    assert max(loads) - min(loads) <= 1
    assert salt_loads(0, 3) == [0, 0, 0]
    assert salt_loads(7, 1) == [7]
    for args in ((-1, 3), (10, 0), (1.5, 2), (2, 1.5), (True, 3)):
        try:
            salt_loads(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid input should fail")


if __name__ == "__main__":
    test_salt_loads()
    print("Salted request counts:", salt_loads(101, 4))
    print("All salting assertions passed.")
```

Expected output:

```text
Salted request counts: [26, 25, 25, 25]
All salting assertions passed.
```

This demonstrates idealized even assignment, not a real salt-selection algorithm. A production design must decide how requests map to salts and how reads, updates, uniqueness, ordering, and aggregation work across salt buckets.

---

## 11. Practical exercises

All numerical values are illustrative. Attempt the tasks before consulting the answer key.

### 11.1 Beginner

**B1 — scaling requirement.** A job must process 9 million records in 15 minutes. A single worker sustains 7,500 records/s on a representative test. Calculate the required average rate and idealized number of workers. List three assumptions that make the worker estimate optimistic.

**B2 — twelve keys.** Assign keys 0–11 to three shards using `key % 3`. Then assign them to three contiguous ranges. Compare key counts and explain which design makes a query for keys 4–7 easier to route.

**B3 — skew.** Partition loads are `[20, 20, 20, 100]`. Calculate mean, maximum, skew ratio, and rough effective partition equivalents for four equal-capacity partitions. State the limitations.

**B4 — partition terminology.** Explain logical partitioning, physical partitioning, and sharding. Give one example where these ideas coexist.

### 11.2 Intermediate

**I1 — choose a key.** An append-heavy event table is queried mostly by time range, but writes target the current minute. Compare range-by-time, hash-by-tenant, and hash-prefix-plus-time. Include write distribution, query fan-out, skew, and maintenance.

**I2 — identify the skew type.** Four shards each store 500 GiB, but one receives 55% of requests. Identify the likely skew type and the metrics needed to establish whether resource skew is present too.

**I3 — resharding estimate.** A simple modulo scheme has 12 shards. Estimate the fraction of keys expected to move when growing to 13 shards under the uniform-hash assumption. Compare with the idealized movement fraction for consistent hashing adding one of 13 equally sized owners. Explain why these are not guarantees for bytes moved.

**I4 — migration plan.** A tenant must move to a dedicated shard with minimal downtime. List the copy, change-capture, routing, validation, cutover, and rollback decisions that must be resolved.

**I5 — skew diagnosis.** Task times are `[8, 9, 8, 10, 42]` seconds. Calculate the max/mean ratio. List at least three explanations besides “bad partition key.”

### 11.3 Advanced

**A1 — ledger hotspot.** A customer-keyed ledger has 5,000 customers. Three customers produce 45% of writes, and month-end doubles the overall write rate. Propose two candidate designs, calculate the evidence you need, and discuss read/transaction costs. Do not assume salting is automatically correct for a ledger.

**A2 — query fan-out.** A request must wait for all 10 shards. Each shard independently has a 98% chance of completing within 200 ms. Calculate the probability that all ten finish within 200 ms. State why independence may be unrealistic.

**A3 — hot current partition.** One time partition is at 95% CPU while the rest are below 40%. Compare hash-prefix-plus-time, adaptive splitting, and buffering. Define success criteria and failure signals.

**A4 — design decision.** Compare scale-up, scale-out with hash sharding, and scale-out with tenant-aware directory routing for a mixed read/write platform. Include consistency, cross-shard operations, availability, operational complexity, and growth.

**A5 — validation design.** A benchmark with uniform keys shows a 2× throughput increase after adding nodes. Design a representative test that could reveal hotspots and non-linear scaling. Specify data distribution, workload mix, concurrency, metrics, and acceptance criteria.

---

## 12. Exercise answer key and reasoning

### 12.1 Beginner answers

- **B1:** 15 minutes = 900 seconds. Required rate = 9,000,000 / 900 = 10,000 records/s. Idealized workers = 10,000 / 7,500 = 1.33, so at least 2 equivalent workers under linear scaling. This ignores uneven record cost, shared I/O/network limits, serial stages, startup/coordination overhead, skew, and safety headroom.
- **B2:** Modulo: shard 0 gets `[0,3,6,9]`, shard 1 gets `[1,4,7,10]`, shard 2 gets `[2,5,8,11]`. Range: `[0–3]`, `[4–7]`, `[8–11]`. Both have four keys. Range makes keys 4–7 local to one shard; modulo scatters them.
- **B3:** Total = 160; mean = 40; max = 100; skew = 100/40 = 2.5; rough effective equivalents = 4/2.5 = 1.6. This assumes equal partition capacity and that the busiest partition is the bottleneck. It is not a measured throughput prediction.
- **B4:** Logical partitioning defines subsets; physical partitioning places data in separate storage units; sharding assigns subsets to distributed owners/nodes. Example: a transaction table is logically partitioned by date, stored in separate files, and each date partition is distributed among shards by customer hash.

### 12.2 Intermediate answers

- **I1:** Range-by-time supports time scans but risks concentrating current writes. Hash-by-tenant may spread writes only if tenant load is reasonably balanced, but a large/hot tenant can dominate and time queries may fan out. Hash-prefix-plus-time can spread writes across prefixes and preserve time buckets, but range queries may read all prefixes and ordering may need a merge. Compare actual tenant/key distributions, write rate per partition, range-query frequency, fan-out, and maintenance costs.
- **I2:** Request skew is evident from the 55% share. Equal stored bytes do not imply equal request load. Measure per-shard CPU, I/O, network, queue depth, request cost, latency percentiles, errors, and concurrency to establish resource skew and the limiting resource.
- **I3:** Modulo: \(12/13 \approx 92.3\%\) expected keys remap under the simplified model. Idealized consistent hashing: \(1/13 \approx 7.7\%\) of key space moves to the added owner. Actual byte movement depends on key sizes, replication, ownership implementation, virtual nodes, existing imbalance, and data-copy policy.
- **I4:** Define a snapshot boundary; capture changes after that boundary; copy and verify existing records; replay changes in order or reconcile conflicts; establish an authoritative routing map; prevent stale clients from writing to the old shard; choose a cutover condition based on lag and invariants; test reads/writes after cutover; preserve a rollback path that accounts for writes accepted by the new shard; delete old data only after reconciliation and a safe retention window.
- **I5:** Mean = (8+9+8+10+42)/5 = 15.4 seconds; skew ratio = 42/15.4 ≈ 2.73. Other explanations include remote I/O, one task receiving more expensive records, GC/memory pressure, a straggler node, network contention, scheduling noise, or a stage dependency. Compare per-task input bytes/rows, CPU, I/O wait, spill, node health, and key distribution.

### 12.3 Advanced answers

- **A1:** Candidate 1: keep customer-key routing and isolate the three large customers onto dedicated shards, preserving per-customer ordering/transactions but requiring directory routing and movement. Candidate 2: use a composite or salted design for the hot customers, but validate how ledger ordering, idempotency, account-level atomicity, and reads across salts are maintained. Measure per-customer write rates during month-end, per-shard queueing/latency, transaction scope, read patterns, and migration cost. Do not salt a ledger key if it breaks required serialization or atomic balance updates.
- **A2:** \(0.98^{10} \approx 0.8171\), or about 81.7%. Real shard latencies can be correlated because they share network, storage, or load; retries and timeouts also alter the distribution.
- **A3:** Hash-prefix-plus-time can spread writes but may increase read fan-out. Adaptive splitting can target the hot range but requires routing and movement coordination. Buffering smooths bursts but does not fix sustained overload if arrival rate exceeds processing capacity. Success should include per-partition CPU/write rate, p95/p99, queue depth, error rate, query fan-out, and correctness. Failure signals include a hotspot persisting on one salt/prefix, read latency worsening, unbounded backlog, or migration-induced errors.
- **A4:** Scale-up is operationally simpler but bounded by resource ceilings and may retain a large failure domain. Hash sharding distributes diverse keys and point access but scatters range queries, leaves hot keys intact, and makes cross-shard operations harder. Tenant-aware directory routing can isolate large tenants and support movement but adds a routing dependency, stale-map risks, and operational complexity. Evaluate workload distribution, consistency/transaction boundaries, failure domains, growth, migration, and service objectives.
- **A5:** Generate realistic key frequencies including top tenants/hot keys, bursts and month-end multipliers; mix reads/writes and query patterns; use open-loop arrival rates or a documented closed-loop client model; ramp concurrency; include enough duration to observe queues and rebalancing; compare multiple node counts; record per-shard requests/bytes/CPU, p50/p95/p99, throughput, queueing, errors, network, data movement, and correctness. Predefine acceptance criteria such as target p95 and error rate at peak load, bounded skew/lag, and no material regression in other workload classes. Report variance, not just the best run.

---

## 13. Industry-style scenarios and architectural comparisons

All systems and symptoms in this section are fictional teaching scenarios.

### 13.1 Scenario A — the latest partition is always hot

**Situation:** writes arrive in timestamp order. One current partition is at 95% CPU while historical partitions are mostly idle.

**Options:** hash partition on a stable key; composite hash prefix plus time; buffer writes; or split the active partition adaptively. Each option has a different balance between write distribution, time locality, fan-out, and maintenance.

**Evidence needed:** per-partition write rates, key frequency, queueing, latency, range-query fan-out, and maintenance/compaction cost.

**Decision rule:** choose the least complex option that meets write and query objectives under representative peak load. Do not infer that the design worked just because CPU became more even; check end-to-end latency, query fan-out, correctness, and backlog.

### 13.2 Scenario B — one customer accounts for 30% of a fact table

**Situation:** a customer-keyed join produces one task that runs much longer than the rest.

**Options:** validate join cardinality; pre-aggregate where semantics allow; isolate the large customer; salt a hot key if reads/aggregates can tolerate fan-out; or change distribution strategy.

**Evidence needed:** customer key frequency, per-task rows/bytes/duration, shuffle volume, spill, actual join output, and downstream query requirements.

**Decision rule:** distinguish a large data partition from a high request rate and from expensive per-row work. A single “skew ratio” is not enough to select a remedy.

### 13.3 Scenario C — resharding during peak load

**Situation:** a platform needs more capacity soon, but a naive modulo scheme is expected to remap most keys when shard count changes.

**Options:** reshard immediately; add read replicas for a read-only bottleneck; defer until a lower-load window; introduce a stable routing/directory layer; or migrate gradually by tenant/range.

**Evidence needed:** bytes to move, copy bandwidth, replication lag, peak load, cutover guarantees, rollback requirements, and whether the actual bottleneck is reads or writes.

**Decision rule:** read replicas can help read capacity but will not fix a primary write hotspot. A planned migration may reduce risk if the current system has enough headroom; an urgent change requires an explicit failure/rollback plan.

### 13.4 Architecture comparison: three distribution choices

| Dimension | Range by time | Hash by tenant/customer | Directory + tenant-aware placement |
|---|---|---|---|
| Time-range reads | Strong locality | Often fan out | Depends on placement and query |
| Point lookup by tenant | May require range/key lookup | Often routes directly | Routes through directory |
| Append/write distribution | Current range may be hot | Depends on tenant distribution | Can isolate/move hot tenants |
| Large tenant isolation | Can be difficult if mixed | One tenant can dominate a shard | Flexible, but operationally complex |
| Cross-tenant aggregate | May span ranges | Often fans out across shards | Usually fans out unless a separate aggregate exists |
| Routing complexity | Simple boundaries | Hash and shard map | Directory consistency and availability |
| Resharding | Split/move ranges | Modulo remapping can be expensive | Can move selected tenants gradually |
| Operational cost | Boundary management | Rebalance and hot-key monitoring | Directory, automation, migration, and auditing |

### 13.5 Architecture decision record (ADR) outline

Record the decision in a short ADR:

- **Context:** workload, growth, SLOs, key distribution, current bottleneck.
- **Decision drivers:** read/write mix, latency, throughput, consistency, availability, operations, cost.
- **Options considered:** scale-up, scale-out, candidate keys/strategies, replicas, isolation, mitigation.
- **Evidence:** per-partition metrics, skew calculations, workload distribution, test results.
- **Decision:** selected approach and reasons.
- **Consequences:** query fan-out, data movement, maintenance, consistency, failure modes.
- **Validation:** workload and acceptance criteria, owner, test window, rollback.
- **Revisit triggers:** skew threshold, growth, p95/error regression, partition count, backlog, or cost deviation.

---

## 14. Common mistakes and troubleshooting

| Mistake | Why it fails | Better approach |
|---|---|---|
| Assuming scale-out is linear | Skew, coordination, shared dependencies, and fan-out limit gains | Measure effective capacity across node counts |
| Choosing a key only for uniqueness | A unique key can still have request or resource skew | Evaluate key frequencies and access patterns |
| Partitioning by current timestamp alone | New writes converge on the active partition | Consider composite distribution or controlled splitting |
| Believing even row counts mean even load | Request rates and work per row differ | Measure request and resource distribution |
| Testing only uniform keys | Hides realistic hot tenants and hot keys | Include skewed and bursty distributions |
| Adding nodes to fix a hot key | Key may remain pinned to one owner | Split/route the key or mitigate the workload itself |
| Using hash for every workload | Range scans and locality can suffer | Compare query fan-out and movement costs |
| Using range for every workload | Sequential writes can create a hot latest range | Validate time-based write distribution |
| Creating too many tiny partitions | Metadata, scheduling, and management overhead rise | Choose partition count from measured workload and unit size |
| Ignoring cross-shard operations | Scatter-gather and transactions increase latency/complexity | Route by shard key where possible; document exceptions |
| Ignoring resharding movement | Migration may overwhelm network/disk and disrupt foreground work | Estimate movement and test cutover/rollback |
| Treating read replicas as a write-scaling solution | Primary writes still target the primary/partition | Diagnose read versus write bottleneck |
| Salting without a read plan | Logical-key queries need scatter-gather or two-stage aggregation | Define salt routing and merge semantics first |
| Ignoring replication lag | Reads can be stale after failover or writes | Define consistency and freshness contract |
| Relying only on cluster averages | A single saturated shard disappears in the average | Monitor per-partition and per-tenant metrics |
| Calling a model output a benchmark | A simplified formula is not observed system behavior | Label assumptions and run a controlled test |
| Treating migration as a copy only | Concurrent writes and routing changes can lose or duplicate data | Design change capture, cutover, validation, and rollback |

### 14.1 Troubleshooting checklist

- [ ] Is the workload and its unit of work defined?
- [ ] Are peak and growth conditions represented?
- [ ] Is the chosen partition key aligned with dominant access patterns?
- [ ] Are per-partition bytes, requests, CPU, I/O, and queue depth measured?
- [ ] Are data skew, request skew, and resource skew distinguished?
- [ ] Is the hottest key/partition identified?
- [ ] Does the operation include the shard key, or does it scatter-gather?
- [ ] Are cross-shard joins/transactions material to latency or correctness?
- [ ] Does the system need more capacity, or is one key/partition indivisible?
- [ ] Are replication lag and failure domains part of the design?
- [ ] Is data movement during rebalancing estimated and rate-limited?
- [ ] Are routing, cutover, validation, and rollback explicit?
- [ ] Are realistic skewed and bursty distributions included in tests?
- [ ] Are acceptance criteria predeclared and measurable?
- [ ] Are findings separated from hypotheses and illustrative calculations?

---

## 15. Expected deliverables

Complete the following package for one representative workload.

### 15.1 Deliverable A — scaling requirements profile

| Field | Required content |
|---|---|
| Workload / owner | Name and responsible role |
| Business purpose | Why the workload exists and what happens if it slows |
| Work units | Requests, records, bytes, queries, or another explicit unit |
| Read/write mix | Frequencies and patterns |
| Arrival profile | Average, peak, burst, month-end, backfill |
| Service objectives | p50/p95/p99, throughput, errors, freshness, availability |
| Data profile | Size, growth, retention, key cardinality and distribution |
| Access patterns | Point lookups, ranges, joins, global aggregates, tenant queries |
| Constraints | Consistency, transaction scope, locality, quotas, maintenance window |
| Baseline evidence | Per-partition load, latency, queueing, resource use |
| Unknowns | Missing measurements and how to obtain them |

### 15.2 Deliverable B — partition-key evaluation

For each candidate key, document expected cardinality and frequency distribution; read/write patterns supported; likely data and request skew; point lookup and range-query locality; fan-out for queries without the key; transaction/consistency implications; growth and boundary behavior; number/size of partitions; movement cost and operational complexity; and evidence supporting or weakening the choice.

### 15.3 Deliverable C — partition-distribution and skew analysis

Include partition count and ownership map; data volume per partition; request/write/read rate per partition; CPU, memory, I/O, network, queue depth and latency where available; skew ratio for each meaningful metric; hottest keys/tenants and their workload shares; limitations of the measurement window and metric definitions; and any effective-capacity approximation with assumptions stated.

### 15.4 Deliverable D — scaling strategy comparison

Compare at least three options, such as scale-up, hash sharding, range partitioning, composite distribution, directory routing, replicas, or tenant isolation. For each, include capacity and latency expectations; consistency/availability implications; locality and cross-partition work; migration/rebalancing effort; maintenance and operational complexity; resource/network cost drivers; and evidence required to validate the expected benefit.

### 15.5 Deliverable E — hotspot mitigation proposal

State the observed hotspot and metric definition; evidence and time window; root-cause hypothesis and counter-evidence; proposed mitigation and why it matches the workload; expected effects on writes, reads, query fan-out, consistency, and operations; risks and rollback path; measurable acceptance criteria; follow-up metrics and owner.

### 15.6 Deliverable F — validation plan

Define realistic key and tenant distribution, including hot keys; arrival pattern, concurrency, and read/write mix; dataset size and growth assumptions; baseline and candidate architecture; run duration and repeat strategy; throughput, latency percentiles, errors, backlog, per-partition load, movement, and resource metrics; correctness/consistency checks; acceptance and regression thresholds; failure injection or rebalance testing where appropriate; and rollout/rollback conditions.

Do not write “performance improved” unless the specified measurements demonstrate it. Separate a predicted benefit from a measured result.

---

## 16. Mastery criteria and completion gate

### 16.1 Mastery criteria

You have mastered this topic when you can:

1. Explain scale-up and scale-out and identify their bottlenecks.
2. Distinguish partitioning from sharding in the context of a specific design.
3. Compare range, hash, composite, and directory routing.
4. Select partition-key candidates from workload evidence rather than intuition.
5. Calculate skew and explain the limits of the effective-capacity approximation.
6. Distinguish data, request, and resource skew.
7. Explain why balanced data can still produce a hot partition.
8. Estimate modulo and consistent-hashing movement under stated assumptions.
9. Design a migration plan that addresses concurrent writes, routing, validation, cutover, and rollback.
10. Compare hotspot mitigations and quantify their read/write/fan-out trade-offs.
11. Explain replication and why read replicas do not automatically scale writes.
12. Define a repeatable validation plan using realistic distributions and measurable acceptance criteria.

### 16.2 Completion gate

- [ ] Scaling requirements profile completed with units and peak conditions.
- [ ] At least three partition-key/distribution options evaluated.
- [ ] Twelve-key range/hash exercise completed and totals checked.
- [ ] Skew calculations reproduced with metric and measurement window stated.
- [ ] Resharding movement estimate completed with assumptions.
- [ ] Data skew, request skew, and resource skew distinguished.
- [ ] Hotspot proposal includes risks, read/write consequences, and rollback.
- [ ] Validation plan includes realistic skew, workload mix, success criteria, and regression checks.
- [ ] Beginner, intermediate, and advanced exercises attempted; gaps logged.
- [ ] Architecture decision record documents evidence, trade-offs, and revisit triggers.

**Readiness statement:** You are ready for Topic 05 when you can explain whether a performance problem is best addressed by distributing work or by avoiding repeated work—and can justify the choice using workload frequency, freshness, skew, and measured evidence.

---

## 17. Transition to Topic 05 — Caching, materialisation and serving trade-offs

Topic 04 focuses on spreading data and workload while keeping partitions useful and balanced. Topic 05 explores the alternative of **avoiding repeated work** by reusing results or maintaining precomputed representations.

Bring forward the scaling requirements profile; key and tenant frequency distributions; partition-key evaluation; per-partition skew and hotspot analysis; query fan-out and data-movement estimates; distribution comparison and ADR; and unresolved questions about freshness, repeated reads, and workload isolation.

The key next question is:

> Is the best next step to distribute the workload more effectively, or to reduce repeated computation with an explicit freshness and maintenance contract?

Neither is automatically superior. The choice depends on request repetition, read/write ratio, freshness requirements, skew, operational maturity, and the measured bottleneck.
