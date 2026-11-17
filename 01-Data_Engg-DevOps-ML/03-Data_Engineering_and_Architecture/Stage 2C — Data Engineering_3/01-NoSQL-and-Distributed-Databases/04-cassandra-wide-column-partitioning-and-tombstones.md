# Cassandra: Wide-Column Partitioning and Tombstones

> **Roadmap position:** Stage 2C — Data Engineering_3 → `01-NoSQL-and-Distributed-Databases/` → Topic 04.  
> **Primary reference:** `roadmap-NoSQL-and-Distributed-Databases.md`, Topic 04.  
> **Version baseline:** Apache Cassandra **5.0** for examples unless explicitly marked otherwise. Verify commands and defaults against the exact distribution and patch version you run.

## Learning objectives

By the end of this lesson, you should be able to:

- Explain Cassandra's ring, nodes, token ownership, replication, keyspaces, tables, and CQL.
- Read and design primary keys, distinguishing partition keys from clustering columns.
- Design tables from query patterns, including bounded partitions and time buckets.
- Explain how replication factor and `ONE`, `QUORUM`, `LOCAL_QUORUM`, and `ALL` affect acknowledgement and read/write overlap.
- Trace the write path (commit log → memtable → SSTable) and read path (coordinator, replicas, Bloom filters, caches, SSTables, reconciliation).
- Use collections, UDTs, static columns, TTL, counters, lightweight transactions, indexes, SAI, and materialized views with appropriate caveats.
- Explain tombstone creation, grace periods, compaction, repair, zombie data, and safe deletion practices.
- Select and inspect compaction strategies; use `nodetool` for basic operational diagnosis.
- Plan a safe node-outage/repair exercise and extract data through token ranges, Spark, or CDC.
- Complete the five query-first designs and all five roadmap lab exercises without fabricating measurements.

## 1. Where this lesson fits

The NoSQL module assumes you have already learned Python and JSON handling, SQL and transaction concepts, OLTP versus OLAP, normalization/denormalization, CDC and idempotent ingestion, Kafka/Debezium basics, and Docker Compose. Topic 01 introduces NoSQL families; Topic 02 introduces consistency theory; Topic 03 introduces document modelling. Cassandra follows those topics because it makes data placement and query shape explicit. Topic 05 (DynamoDB) builds on the same query-first partitioning mindset.

Cassandra is not a replacement for every relational workload. It is a distributed wide-column database designed for high write throughput, horizontal scale, and availability across nodes and racks/datacentres. Its strengths depend on choosing partition keys and query patterns before writing CQL.

## 2. Terminology

| Term | Meaning |
|---|---|
| Cluster | A set of Cassandra nodes that cooperate to store data. |
| Node | One Cassandra process/instance that owns token ranges. |
| Token / token range | A value/range in the partitioner's token space; partition-key bytes are hashed to a token. |
| Ring | Conceptual ordering of token ranges and their owners; modern deployments use token metadata and vnodes rather than a literal physical ring. |
| Coordinator | The node a client contacts; it routes the request to replicas and coordinates responses. It need not own the partition. |
| Keyspace | Namespace and replication configuration for tables. |
| Table | A query-shaped set of rows; a table's primary key controls partitioning and ordering. |
| Partition | Rows sharing the same complete partition-key value(s). It is placed on a replica set and is the primary unit of locality. |
| Partition key | The first component of the primary key, possibly a tuple of multiple columns; determines token and replica placement. |
| Clustering column | A remaining primary-key component that orders rows within a partition and contributes to row identity. |
| Replica | A node storing a copy of a partition according to the keyspace replication strategy. |
| SSTable | Immutable on-disk sorted-string table produced when a memtable flushes. |
| Tombstone | A timestamped deletion marker that participates in reconciliation and later may be purged safely. |
| Repair | Anti-entropy process that compares replica data and streams missing/corrected data. |
| Compaction | Rewrites SSTables to merge data and discard obsolete versions/tombstones when safe. |

## 3. Architecture: from key to replicas

Cassandra hashes the serialized partition key into a token. The token metadata maps that token to a primary token range owner. The keyspace's replication strategy determines the replicas that store the partition. With `NetworkTopologyStrategy`, Cassandra places replicas with datacentre/rack awareness when the topology is configured correctly.

```text
Client
  │ CQL request
  ▼
Coordinator node (any node can coordinate)
  │ hashes partition key → token → replica endpoints
  ├──────────────► Replica A
  ├──────────────► Replica B      (replication factor 3 example)
  └──────────────► Replica C

Each replica's local write path:
  commit log (durability) → memtable (memory) → flush → immutable SSTable
```

Important distinctions:

- The partition key determines which rows are colocated and which replica set owns them; it is not merely an index.
- All rows for one partition key go to the same replica set. A very active partition can therefore become a hot partition even if the cluster has many nodes.
- A composite partition key such as `((device_id, day), observed_at)` means the **tuple** `(device_id, day)` is hashed; `observed_at` is a clustering column.
- Replication is not the same as sharding terminology in every database, though both distribute data. Cassandra automatically distributes token ranges; the schema still determines the distribution key.
- Vnodes let a node own multiple token ranges, smoothing some rebalancing effects. They do not fix a skewed partition key or a single hot partition.

### 3.1 Keyspaces and replication

Use `NetworkTopologyStrategy` in real multi-node/multi-datacentre deployments. `SimpleStrategy` is useful for a disposable local learning cluster, but is not appropriate for production datacentre-aware placement.

```sql
-- Local disposable lab only; use a replication factor compatible with node count.
CREATE KEYSPACE IF NOT EXISTS cassandra_lab
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3};

-- Production-shaped example: datacentre names must match nodetool status.
CREATE KEYSPACE IF NOT EXISTS telemetry
WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'dc1': 3
};

USE telemetry;
```

If your local cluster has one node, use RF 1 for a functional smoke test; do not pretend that it demonstrates replica failure tolerance. For the three-node lab, RF 3 is a useful teaching setting. Replication factor is per keyspace and datacentre, not per table. Validate node/DC topology before using the second example.

## 4. CQL fundamentals: SQL-like, not relational SQL

CQL supports schema definitions and familiar `SELECT`, `INSERT`, `UPDATE`, and `DELETE` syntax. But it is not an unrestricted relational query engine:

- Reads are designed around a known partition key and supported clustering restrictions.
- Joins are not a general-purpose query operation. Model a query so it can be served by a table, or perform a deliberate application/analytics-side join.
- `WHERE` clauses cannot arbitrarily filter any column efficiently. A non-key predicate usually requires an appropriate index or an explicit filtering scan, and `ALLOW FILTERING` can be expensive/unpredictable.
- `ORDER BY` is constrained to clustering columns and their declared order within a single partition; it is not a global sort across arbitrary partitions.
- `GROUP BY` and aggregation capabilities are limited compared with an analytical SQL engine. Export/stream to an analytics system for broad scans and complex aggregation.
- A CQL upsert is not the same as a relational `INSERT` that errors on duplicates: inserting the same primary key writes the supplied cells under Cassandra's timestamp reconciliation rules. Columns omitted from the mutation are not automatically cleared; they can retain earlier values.

### 4.1 A minimal table

```sql
CREATE TABLE telemetry.quick_example (
  device_id text,
  observed_at timestamp,
  temperature_c double,
  PRIMARY KEY (device_id, observed_at)
) WITH CLUSTERING ORDER BY (observed_at DESC);
```

Here `device_id` is the partition key and `observed_at` is the clustering column. For a given device, rows are ordered newest-first. This is only a teaching schema: if one device emits data forever, the partition grows without bound. The bounded design appears later.

```sql
INSERT INTO telemetry.quick_example (device_id, observed_at, temperature_c)
VALUES ('sensor-17', '2026-10-19T09:00:00Z', 22.4);

SELECT observed_at, temperature_c
FROM telemetry.quick_example
WHERE device_id = 'sensor-17'
LIMIT 20;
```

The timestamp literal is shown in ISO-8601 form; use a driver or the exact CQL timestamp literal accepted by your shell/version. The query specifies the partition key, so Cassandra can route it to the replica set for that partition.

### 4.2 Primary-key notation

```sql
PRIMARY KEY (user_id)                         -- one-column partition key; no clustering columns
PRIMARY KEY (user_id, message_time)           -- partition=user_id; clustering=message_time
PRIMARY KEY ((device_id, day), observed_at)   -- composite partition key=(device_id, day)
PRIMARY KEY ((tenant_id, bucket), event_time, event_id)
```

In the last example, `(tenant_id, bucket)` defines the partition and `(event_time, event_id)` defines clustering order and uniqueness within it. Choose the clustering order based on required range scans and ordering, not on the order in which columns appear in application JSON.

### 4.3 Supported query shapes

| Query shape | Typical status | Reason |
|---|---|---|
| Exact partition key, optionally clustering range | Preferred | Routes to a known replica set and reads a bounded slice. |
| Exact partition key + `ORDER BY` matching clustering order | Preferred | Uses the partition's clustering order. |
| Partial partition key of a composite key | Not enough for a normal single-partition lookup | The complete partition key is required. |
| Filter only on a non-key column without an index | Usually rejected or requires filtering | No efficient route to the rows is known. |
| Global sort across all partitions | Not supported as a normal table query | Ordering is local to a partition. |
| Arbitrary join across tables | Not a normal CQL operation | Cassandra tables are designed around known reads. |

`ALLOW FILTERING` is a diagnostic/exception tool, not a data-model strategy. It may scan large amounts of data and have latency proportional to data size. Avoid making it part of an SLO-critical production path without explicit boundedness and load testing.

## 5. Query-first modelling

Start with questions, not entities. Write the required query, decide what data must be returned, estimate how many rows the query can touch, and then design a table whose primary key can answer it directly. Duplication is intentional when it gives each access pattern an efficient representation.

### 5.1 Modelling workflow

1. List reads and writes, including frequency, freshness, sort order, and pagination.
2. Identify the partition key that groups the data needed together.
3. Add clustering columns to establish row identity, order, and range slicing.
4. Bound the number of rows and bytes per partition with a bucket if necessary.
5. Estimate skew: do some users/devices/tenants generate far more traffic than others?
6. Decide replication and consistency based on availability, latency, and durability requirements.
7. Test with realistic cardinality, row widths, skew, TTLs, and deletes—not just a tiny happy-path sample.
8. Add a separate table for a genuinely different query pattern. Plan dual writes or a CDC-based projection and make retries idempotent.

### 5.2 Partition sizing: estimate, then measure

There is no universal safe row count. Partition size depends on row width, clustering metadata, cells per row, tombstones, compaction behavior, read patterns, and version/runtime characteristics. As a first approximation:

`estimated partition bytes ≈ rows per partition × average encoded bytes per row`

Add headroom for metadata, indexes, tombstones, and write/read amplification. A useful starting engineering target is to keep partitions comfortably bounded—often tens of MB rather than hundreds of MB or GB—and set a maximum expected row count. Treat any numeric target as a hypothesis to validate against your workload and Cassandra version, not a product guarantee.

For a device emitting `r` readings/second and a bucket duration of `t` seconds:

`rows per partition ≈ r × t`

For example, 2 readings/second × 3,600 seconds = 7,200 rows/device/hour. At an assumed encoded average of 120 bytes/row, raw row payload is roughly 0.82 MiB per device-hour before storage overhead. This is a planning estimate, not a benchmark. Measure actual SSTable sizes and read latency after loading realistic data.

### 5.3 Time buckets

Common buckets include day, hour, month, or a fixed sequence number. Pick the narrowest bucket that meets expected partition size and query patterns without producing excessive tiny partitions. Queries across multiple buckets must issue multiple partition reads, usually in parallel with bounded concurrency and merged results in the application.

- Daily bucket: fewer partitions, larger partitions, convenient daily scans.
- Hourly bucket: smaller partitions, more partition fan-out for multi-hour reads.
- Fixed-size bucket (for example, a bounded number of events per partition): can bound volume even when event rate varies, but requires deterministic bucket assignment and often an extra sequence or epoch.

Never use `day` alone for all devices if it causes every device's readings to share one partition; use `(device_id, day)`. Conversely, never assume `(device_id, day)` is enough if a single device can emit an extreme volume; consider an additional shard/bucket component.

## 6. Five required query patterns: worked designs

The following are example designs for the roadmap exercise. They are not one universal schema. Production schemas must be refined with actual access patterns, retention, row widths, hot-key distribution, and consistency needs.

### 6.1 Messages by user

**Required query:** fetch a user's latest messages, newest first, with optional time-range pagination.

```sql
CREATE TABLE app.messages_by_user (
  user_id uuid,
  message_time timeuuid,
  message_id uuid,
  sender_id uuid,
  body text,
  conversation_id uuid,
  PRIMARY KEY (user_id, message_time, message_id)
) WITH CLUSTERING ORDER BY (message_time DESC, message_id ASC);
```

- **Partition key:** `user_id`, because the query starts with one user.
- **Clustering:** `message_time` orders messages; `message_id` breaks ties and guarantees a unique primary key when multiple messages share the same timeuuid precision/domain assumptions. Ensure the actual key values are unique.
- **Expected size/distribution:** highly active users can create large partitions; choose a time bucket such as `(user_id, message_month)` or `(user_id, message_day)` if message volume is unbounded. Add the bucket to the partition key and update the query to select the appropriate buckets.
- **Read path:** exact user partition; newest rows are at the clustering-order end, so `LIMIT` can return a small recent slice.
- **Write path:** message writes distribute by user; very popular accounts can become hot partitions. If one user can produce huge write volume, use a bounded bucket or split strategy.
- **Replication/consistency:** RF 3 with `LOCAL_QUORUM` is a common starting point for local-datacentre user-visible messaging, but the choice depends on cross-DC needs and latency SLOs. Use `QUORUM`/`ALL` only when their wider acknowledgement cost is acceptable.
- **Trade-off:** this table does not efficiently answer “all messages in a conversation” unless user-centric access is the only required query. Create a separate `messages_by_conversation` table for that query and maintain both views deliberately.

Example query:

```sql
SELECT message_time, message_id, sender_id, body
FROM app.messages_by_user
WHERE user_id = 11111111-1111-4111-8111-111111111111
LIMIT 50;
```

### 6.2 Events by device per day

**Required query:** fetch one device's events for a known UTC day, optionally in a time range.

```sql
CREATE TABLE telemetry.events_by_device_day (
  device_id text,
  day date,
  event_time timestamp,
  event_id uuid,
  event_type text,
  payload text,
  PRIMARY KEY ((device_id, day), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time ASC, event_id ASC);
```

- **Partition key:** `(device_id, day)` distributes devices across the ring while bounding each device-day.
- **Clustering:** event time gives ordered range scans; event ID resolves timestamp ties.
- **Expected size:** estimate device event rate × 86,400 seconds. If the largest device can create too many rows or bytes per day, use an hourly bucket or a shard suffix.
- **Read path:** a day query targets one partition; a multi-day query fans out over a known number of day partitions.
- **Hotness:** a single high-rate device can still saturate its partition. Partition keys with many devices do not help if one device is a dominant producer.
- **Consistency:** telemetry often tolerates `LOCAL_QUORUM` or `ONE` for writes depending on loss tolerance; choose and test deliberately. A critical audit event may need stronger acknowledgement and idempotent producer semantics.
- **Trade-off:** clients must compute the correct UTC day and query each day partition for ranges spanning midnight.

```sql
SELECT event_time, event_id, event_type, payload
FROM telemetry.events_by_device_day
WHERE device_id = 'device-17' AND day = '2026-10-19'
  AND event_time >= '2026-10-19T08:00:00Z'
  AND event_time <  '2026-10-19T09:00:00Z';
```

### 6.3 Orders by customer

**Required query:** list a customer's recent orders and retrieve one order by ID.

```sql
CREATE TABLE commerce.orders_by_customer (
  customer_id uuid,
  order_month date,
  created_at timeuuid,
  order_id uuid,
  status text,
  total_minor_units bigint,
  currency text,
  item_count int,
  PRIMARY KEY ((customer_id, order_month), created_at, order_id)
) WITH CLUSTERING ORDER BY (created_at DESC, order_id ASC);

CREATE TABLE commerce.order_by_id (
  order_id uuid PRIMARY KEY,
  customer_id uuid,
  created_at timestamp,
  status text,
  total_minor_units bigint,
  currency text,
  shipping_address text
);
```

- **Required queries:** recent orders by customer/month; order detail by order ID. These are two different access patterns, hence two tables.
- **Partition/clustering:** customer + month bounds the list partition; creation time orders recent orders. The point lookup table uses `order_id` as its partition key.
- **Expected size:** estimate orders/customer/month. Large business accounts may still be hot; use a finer bucket if needed.
- **Read/write path:** an order creation writes both projections. Use an idempotent application workflow/outbox or CDC-based projection; Cassandra does not provide a general cross-table transaction for these two writes.
- **Consistency:** use a consistency level appropriate for the business contract. A customer order listing may use `LOCAL_QUORUM`; order-by-ID reads must account for projection propagation if writes are asynchronous.
- **Trade-off:** duplicated status/total fields need an update policy. Keep an authoritative event or write path and reconcile projections; don't silently assume cross-table atomicity.

### 6.4 Sensor readings by hour

**Required query:** read one device's measurements in a given hour or time range.

```sql
CREATE TABLE telemetry.sensor_readings (
  device_id text,
  day date,
  hour tinyint,
  observed_at timestamp,
  reading_id uuid,
  temperature_c double,
  humidity_pct double,
  PRIMARY KEY ((device_id, day, hour), observed_at, reading_id)
) WITH CLUSTERING ORDER BY (observed_at ASC, reading_id ASC);
```

- **Partition key:** `(device_id, day, hour)` explicitly bounds the data to one device-hour.
- **Clustering:** event time supports range reads; `reading_id` breaks ties.
- **Expected size:** `rate × 3,600`; if one device emits 100 readings/sec, one hour has 360,000 rows and may need a smaller bucket or a shard suffix. Estimate bytes as well as rows.
- **Read path:** query one partition for one device-hour; a range spanning multiple hours requires a bounded fan-out of partition queries.
- **Write path:** evenly distributed devices spread traffic; one high-rate device-hour can be hot. A shard suffix can spread load, but then a query must read each shard and merge results.
- **Consistency:** telemetry can use `LOCAL_QUORUM` or `ONE` when the loss/latency contract supports it. Use RF 3 for a three-node lab and understand the difference between one replica acknowledgement and quorum acknowledgement.
- **Trade-off:** more buckets reduce partition size but increase client orchestration and partition count.

For the specific roadmap lab, the required partition key is `(device_id, day)`. You can use the table above as the production design discussion, but create the exact `(device_id, day)` version in the lab first, then measure whether hourly bucketing is necessary.

### 6.5 Top posts

**Required query:** return the top posts for a time window and ranking category, for example a daily trending feed.

```sql
CREATE TABLE social.top_posts_by_day (
  feed_day date,
  region text,
  rank_bucket text,
  score_bucket int,
  score double,
  post_time timestamp,
  post_id uuid,
  author_id uuid,
  title text,
  PRIMARY KEY ((feed_day, region, rank_bucket), score_bucket, score, post_time, post_id)
) WITH CLUSTERING ORDER BY (score_bucket DESC, score DESC, post_time DESC, post_id ASC);
```

This is a **materialized feed projection**, not an instruction to run a global `ORDER BY score` on the base posts table. The application or stream processor computes ranking updates and writes the ordered feed table.

- **Partition key:** day + region + feed/rank shard. `rank_bucket` can be a fixed shard such as `00`–`07` if one day-region partition would be too hot. A bucket/shard scheme increases read fan-out.
- **Clustering:** the ranking bucket and score ordering provide a limited ranked list inside one partition. The exact `score_bucket` strategy must be consistent with the app's score-update behavior; mutable scores can cause row rewrites and movement between buckets.
- **Expected size:** cap retained entries per shard/window; use a feed-generation process to expire or replace old ranking rows. Avoid a single unbounded “all-time top posts” partition.
- **Read/write path:** serving the top feed is a bounded partition read, but maintaining ranks can be write-heavy and require duplicate updates.
- **Consistency:** a feed can often tolerate eventual refresh and `LOCAL_QUORUM`/`ONE`; a strict global ranking is not guaranteed by Cassandra's local clustering order.
- **Trade-off:** if a global, frequently changing top-N is the primary workload, consider computing it in a stream processor/search/analytics system and publishing a bounded serving view.

### 6.6 Layout diagram and on-disk implications

For `sensor_readings` with `PRIMARY KEY ((device_id, day, hour), observed_at, reading_id)`:

```text
Partition key = (device-17, 2026-10-19, 09)
┌─────────────────────────────────────────────────────────┐
│ one logical partition replicated to RF-selected nodes   │
│                                                         │
│ clustering order: observed_at ASC, reading_id ASC       │
│ 09:00:00.010  id-a  temperature=22.1                    │
│ 09:00:00.500  id-b  temperature=22.2                    │
│ 09:00:01.000  id-c  temperature=22.2                    │
│ ...                                                     │
└─────────────────────────────────────────────────────────┘

Each replica's memtable flushes to immutable SSTables. The same logical
partition can have fragments/versions in multiple SSTables until compaction
merges them. Clustering order is a logical/on-disk ordering guarantee for
rows in the partition, not a promise that the entire partition lives in one
single SSTable forever.
```

The partition key localizes rows to one replica set. The clustering key lets Cassandra read a contiguous slice rather than scanning unrelated rows in that partition. Repeated updates and deletes can leave older cell versions and tombstones across SSTables; compaction reconciles them and only purges tombstones when safe.

## 7. Write path and read path

### 7.1 Write path

1. Client sends a CQL mutation to a coordinator.
2. Coordinator determines replicas for the partition and forwards the mutation.
3. Each replica appends the mutation to its commit log (durability/recovery) and applies it to an in-memory memtable.
4. The replica acknowledges according to the requested consistency level once enough replicas respond.
5. When memtables reach flush thresholds or are flushed, they become immutable SSTables on disk.
6. Compaction later merges SSTables, resolves old versions, and may discard obsolete data/tombstones when safe.

```text
CQL mutation → coordinator → replicas
                              ├─ commit log (append)
                              └─ memtable (mutable, memory)
                                       │ flush
                                       ▼
                                immutable SSTable(s)
                                       │ compaction
                                       ▼
                                fewer/new SSTables
```

An acknowledged write does not necessarily mean every replica has applied it. Consistency level determines how many replica responses the coordinator requires. Cassandra uses timestamps to reconcile competing mutations; clock discipline and explicit client timestamps matter. Do not send arbitrary old timestamps casually, because an older write can lose to a newer cell timestamp.

### 7.2 Read path

1. Coordinator routes the query to replicas for the partition.
2. Replica checks partition/key caches where enabled and relevant, Bloom filters to rule out SSTables that definitely do not contain the partition, and index/summary structures to locate data in candidate SSTables.
3. Candidate data from memtables and multiple SSTables is merged/reconciled by timestamps and deletion markers.
4. Coordinator combines responses according to consistency level and, depending on configuration/version/read type, may perform read repair or digest comparison.
5. Returned rows follow the table's clustering order and the query's allowed slice.

Bloom filters are probabilistic: they can have false positives but not false negatives in their intended role. A false positive means Cassandra may inspect an SSTable that does not contain the partition. Caches can reduce work but should not be treated as the primary access path. A query that touches a huge partition or many tombstones can be slow even when its partition key is correct.

### 7.3 On-disk layout and storage amplification

Cassandra SSTables are immutable. Updates generally create newer cell versions rather than editing an old SSTable in place. For a hot partition, fragments of the partition may exist in multiple SSTables and the read path must reconcile them. Compaction reduces the number of SSTables and reclaims eligible obsolete data, at the cost of disk I/O, CPU, temporary disk space, and write amplification.

Capacity planning must include more than live payload: replication factor, commit logs, memtables, SSTable compaction overlap, snapshots, hints, repair streaming, CDC data if enabled, and free-space safety margin. Do not fill disks to 100%; compaction and streaming can require substantial temporary space.

## 8. Replication and consistency levels

With RF 3, three replicas store each partition. For a single datacentre, the following quorum intuition applies:

| Level | Acknowledgement requirement | Typical trade-off |
|---|---|---|
| `ONE` | One replica response | Lower latency/high availability; read may observe a stale value if replicas diverge. |
| `QUORUM` | Majority of replicas for the applicable replication scope | More responses and stronger overlap than `ONE`; cross-DC scope/latency must be understood. |
| `LOCAL_QUORUM` | Majority of replicas in the coordinator's local datacentre | Common for local DC applications; avoids waiting for remote DC acknowledgements. |
| `ALL` | All replicas in the applicable replication scope | Strong acknowledgement requirement but one unavailable replica can fail the operation. |

For RF 3 in one DC, quorum is 2. The classic overlap condition is `R + W > RF`: if read and write replica counts overlap, a read at an appropriate consistency level can observe the latest acknowledged mutation under the relevant assumptions. This is not a universal promise of linearizability for every operation; concurrent writes, timestamps, multiple DCs, repair, and consistency choices matter. `LOCAL_QUORUM` is defined per local DC and must be reasoned about alongside the write CL and replication topology.

Use the same consistency contract intentionally for writes and reads. Examples:

- User-visible local writes: `LOCAL_QUORUM` write/read is a common starting point for RF 3 in one DC.
- Loss-tolerant metrics: `ONE` may be acceptable when latency matters and eventual convergence is expected.
- `ALL` may be useful for specific administrative or validation cases but can reduce availability; it is rarely a default for a highly available service.

### 8.1 Hinted handoff, read repair, and anti-entropy repair

- **Hinted handoff:** a coordinator may retain a hint for a temporarily unavailable replica and replay it later, subject to configuration and hint-window limits. Hints are not a substitute for repair and may not cover long outages.
- **Read repair:** on some reads/configurations, replica disagreement may be detected and corrected as part of the read path. Behavior and options vary by Cassandra version; do not assume every read repairs all replica data.
- **Anti-entropy repair:** compares replica data (using Merkle-tree-based mechanisms in common implementations) and streams missing/different data. Run repair on a planned schedule and ensure the selected range/replicas are covered. Repair is operational work with CPU, disk, and network cost.
- **Consistency over time:** CL controls request acknowledgement/response; repair, hints, and reads help replicas converge. No single low CL eliminates the need to monitor repair and replica health.

## 9. CQL types and special features

### 9.1 Collections

CQL supports `list`, `set`, and `map`. Collections are useful for small, bounded attributes; they are not a substitute for a child table when values grow indefinitely or are updated independently.

```sql
CREATE TABLE app.user_preferences (
  user_id uuid PRIMARY KEY,
  tags set<text>,
  notification_flags map<text, boolean>,
  recent_labels list<text>
);

UPDATE app.user_preferences
SET tags = tags + {'data-engineering'}
WHERE user_id = 11111111-1111-4111-8111-111111111111;
```

Keep collections bounded. Large collections increase read/write and tombstone costs and may be rewritten or represented as many cells. For a user's unbounded event history, create a separate query-shaped table instead.

### 9.2 User-defined types (UDTs)

```sql
CREATE TYPE app.address (
  line1 text,
  city text,
  postal_code text,
  country text
);

CREATE TABLE app.customer_profile (
  customer_id uuid PRIMARY KEY,
  display_name text,
  address frozen<address>
);
```

`frozen` values are stored as one value at the enclosing column level, so updating part of a frozen UDT requires replacing the value. UDT schema evolution and driver mapping should be tested carefully. Do not use a UDT to hide a frequently changing/unbounded child collection.

### 9.3 Static columns

A static column stores one value for a partition and is shared by its clustered rows. It is useful when a partition has many rows with a shared attribute.

```sql
CREATE TABLE app.messages_by_conversation (
  conversation_id uuid,
  message_time timeuuid,
  message_id uuid,
  conversation_title text STATIC,
  sender_id uuid,
  body text,
  PRIMARY KEY (conversation_id, message_time, message_id)
);
```

`conversation_title` is one value per conversation partition, not one independent value per message. Static columns require a clustering column in the table and should not be confused with a relational join.

### 9.4 TTL and expiry

```sql
INSERT INTO app.ephemeral_sessions (session_id, user_id, payload)
VALUES (11111111-1111-4111-8111-111111111111,
        22222222-2222-4222-8222-222222222222,
        '...') USING TTL 3600;

SELECT TTL(payload)
FROM app.ephemeral_sessions
WHERE session_id = 11111111-1111-4111-8111-111111111111;
```

TTL expiration is logical first: it creates tombstone/deletion metadata; physical removal occurs later when compaction can safely purge it. Different TTLs and non-TTL data mixed in the same partition/SSTables can delay safe cleanup. Do not use TTL as a promise of immediate disk erasure at the expiration second.

### 9.5 Counters

Counter columns support distributed increments/decrements but have special semantics and limitations: counter updates are not ordinary idempotent writes, counters cannot be mixed freely with regular columns in the same mutation, and retrying an increment may double-count. Use a counter table only when approximate/distributed counter semantics and retry handling fit the requirement. For billing/financial facts, prefer immutable events plus a derived aggregate.

```sql
CREATE TABLE metrics.page_views_by_day (
  page_id text,
  day date,
  view_count counter,
  PRIMARY KEY ((page_id, day))
);

UPDATE metrics.page_views_by_day
SET view_count = view_count + 1
WHERE page_id = '/home' AND day = '2026-10-19';
```

### 9.6 Lightweight transactions (LWT)

`IF NOT EXISTS` uses a Paxos-based conditional operation for compare-and-set semantics and costs more latency/coordination than a normal write. Use it for a narrow correctness requirement such as creating a unique claim, not for every write on a high-throughput path.

```sql
CREATE TABLE app.idempotency_keys (
  key text PRIMARY KEY,
  created_at timestamp,
  request_hash text
);

INSERT INTO app.idempotency_keys (key, created_at, request_hash)
VALUES ('request-2026-10-19-0001', toTimestamp(now()), 'sha256:example')
IF NOT EXISTS;
```

Check the `[applied]` result returned by CQL. `now()` returns a timeuuid and `toTimestamp(now())` converts it to a timestamp on the server. For reproducible application writes, binding the timestamp from the driver is often easier to test. LWT does not create a general multi-table transaction, and the Paxos coordination adds latency and load compared with an ordinary mutation.

## 10. Secondary indexes, SAI, and materialized views

### 10.1 Secondary indexes

Secondary indexes can make some non-partition-key queries possible, but they do not erase the need to model access patterns. Traditional local secondary-index behavior can be problematic when indexed values are high-cardinality, sparsely populated, or queried across many nodes. Index design must match Cassandra version, index implementation, cardinality, and query selectivity.

### 10.2 Storage-Attached Indexing (SAI)

Cassandra 5.0 supports Storage-Attached Indexing (SAI). It attaches index structures to SSTables and can support filtering on non-primary-key columns in supported query shapes. It is not a free relational index: index build/storage/maintenance consume resources, and broad low-selectivity queries can still touch many partitions.

```sql
CREATE TABLE app.events_by_tenant (
  tenant_id text,
  day date,
  event_time timestamp,
  event_id uuid,
  event_type text,
  severity int,
  PRIMARY KEY ((tenant_id, day), event_time, event_id)
);

CREATE CUSTOM INDEX IF NOT EXISTS events_by_tenant_type_sai
ON app.events_by_tenant (event_type)
USING 'StorageAttachedIndex';
```

Treat the index as a deliberate exception to the primary query design. Validate whether your intended query is supported by Cassandra 5.0 SAI and whether it can meet latency under realistic load. SAI syntax and capabilities can differ by version/distribution; test on the exact release.

### 10.3 Materialized views

Materialized views maintain an alternate representation of base-table data with server-side view maintenance, subject to primary-key restrictions and version-specific caveats. They can reduce application-side duplication in some workloads but add write amplification and operational complexity. Historically, materialized views have had significant operational limitations and should not be adopted casually.

Before using a view:

- Confirm support and known limitations for your exact Cassandra version and distribution.
- Verify primary-key requirements and whether the base table can safely represent the view's key.
- Test node failure, repair, view build, and write behavior under load.
- Compare with application-managed dual writes, an outbox/CDC projection, or a separate query table.

Do not present a materialized view as a general join or arbitrary secondary access path.

## 11. Tombstones: lifecycle, costs, and zombie data

### 11.1 Why delete markers exist

Cassandra replicates immutable SSTables and reconciles mutations by timestamps. Immediately erasing a value from one replica would be unsafe: another replica could still have an older copy and later reintroduce it during repair or reconciliation. Therefore, deletion is represented as a timestamped tombstone that tells replicas and readers that older data is deleted.

Tombstones can be created by:

- `DELETE` of a row, cell, or collection element;
- TTL expiry of a cell/row;
- range or partition deletions;
- replacing collection elements or updates that remove existing cells, depending on operation semantics.

### 11.2 Lifecycle

```text
DELETE / TTL expires
        │
        ▼
Tombstone mutation with timestamp
        │ normal write path: commit log → memtable → SSTable
        ▼
Readers reconcile tombstone against older cell versions
        │ tombstone remains through gc_grace_seconds
        ▼
Compaction may purge it only when old data it shadows cannot survive elsewhere
        │
        ▼
Physical deletion metadata can disappear from SSTables
```

**Creation is not physical removal.** The row may disappear from normal query results as soon as the tombstone is visible, but tombstone bytes and shadowed old values can remain on disk. `gc_grace_seconds` is a minimum grace period for safe tombstone retention, not a timer that automatically erases a tombstone at exactly that moment. Compaction must occur, and it must be safe to remove the tombstone without exposing older data.

### 11.3 `gc_grace_seconds`

The common default is 864000 seconds (10 days), but verify the actual schema and deployment. The grace period allows unavailable replicas time to recover and receive deletion information before tombstones can be purged. It is not a guarantee that every missed mutation will be replayed automatically. Do **not** lower it simply to reclaim disk space.

A dangerous sequence:

1. A replica containing a value is down or isolated.
2. The cluster accepts a delete on the available replicas and writes tombstones.
3. The unavailable replica misses the delete for longer than the configured grace period.
4. Available replicas purge the tombstone during safe compaction.
5. The old replica rejoins with the old value, and a later repair/reconciliation may make the deleted value visible again.

This reappearing deleted value is called a **zombie**. Hinted handoff is not a complete defense against long outages; hints can expire or be unavailable. Repair cadence, node outage duration, tombstone retention, and compaction safety must be considered together.

### 11.4 Why tombstone-heavy reads are expensive

A read may need to scan tombstones and reconcile them with live cells across multiple SSTables before returning few or no rows. Symptoms can include elevated read latency, logs/warnings about many tombstones scanned, high CPU, and high SSTable read amplification. A small returned result set does not imply a small amount of work.

Common causes:

- Large deletes or frequent TTL expiry in the same partitions queried for live data;
- Huge/unbounded partitions;
- Many SSTables with overlapping historical versions;
- Collections that grow and shrink heavily;
- TTLs of widely varying duration mixed in the same partitions;
- Query patterns that scan long clustering ranges with many deleted rows.

### 11.5 Safe deletion strategies

Prefer these, in order of fit:

1. **Model retention into partitions.** If data expires by day/hour, use time buckets and retire old buckets/partitions in a planned manner rather than deleting millions of individual rows.
2. **Use TTL for naturally expiring data**, with a realistic retention and tombstone/compaction plan. TTL still creates tombstones; it does not eliminate tombstone cost.
3. **Avoid unbounded collections and frequent element deletion.** Use rows in a dedicated table when elements need independent lifecycle.
4. **Bound delete scope and rate.** Batch or schedule deletes only within documented operational limits; huge logged batches are not a bulk-load optimization.
5. **Maintain repair coverage before tombstones are eligible for purge.** Never rely on the grace period alone as a correctness guarantee.
6. **Monitor and inspect before forcing compaction or changing grace settings.** A manual major compaction can create heavy I/O and temporary disk pressure and may not purge tombstones if safety conditions are unmet.

Do not set `gc_grace_seconds = 0` as a generic performance fix. It can make zombie data possible if a replica misses a delete. Any non-default grace period requires a documented repair/outage policy and validation of version-specific tombstone-purge safeguards.

### 11.6 Observe tombstones

For a lab, capture baseline and post-delete query behavior. Do not rely on a particular warning line or count; warning thresholds, log wording, and available metrics vary by version and configuration. Look for:

- server logs mentioning tombstones scanned or tombstone warnings;
- read latency and CPU changes;
- SSTable count, pending compactions, and compaction throughput;
- query traces and driver timings;
- schema options and TTL remaining values;
- `nodetool tablestats` / `nodetool cfstats` output (exact command availability/output differs by release).

A correct report records the actual version, configuration, query, dataset size, command, and output. If no warning occurs, say that the warning was not observed under that test setup; do not invent one.

## 12. Compaction strategies

Compaction merges immutable SSTables and reconciles cells/tombstones. It can improve read efficiency and reclaim space, but requires I/O, CPU, and temporary disk capacity. The correct strategy depends on write patterns, read patterns, retention, and SSTable size distribution.

Cassandra 5.0 includes Unified Compaction Strategy (UCS), in addition to size-tiered, leveled, and time-window strategies. Apache Cassandra 5.0 documentation recommends UCS for most new workloads, while legacy STCS may still be the fallback default when no strategy is specified. Do not infer the active strategy from a generic default: inspect `DESCRIBE TABLE`, verify the patch release, and account for managed-service defaults. Since the roadmap specifically asks to compare STCS and TWCS, study those directly while recognizing that neither is the universal production choice.

### 12.1 Size-Tiered Compaction Strategy (STCS)

STCS groups similarly sized SSTables and compacts them together. It is a reasonable general write-heavy strategy and can be efficient for append/update workloads, but can create temporary space amplification and may leave overlapping SSTables that increase read amplification. Expired data can be harder to reclaim if old and new data are mixed across SSTables.

### 12.2 Leveled Compaction Strategy (LCS)

LCS organizes SSTables into levels with size/overlap constraints to reduce read amplification, often at the cost of higher write amplification and more compaction I/O. It is often considered for read-heavy workloads with predictable point/range queries, but validate workload and disk budget.

### 12.3 Time-Window Compaction Strategy (TWCS)

TWCS groups SSTables into time windows and is intended for time-series/TTL workloads where data is written with roughly monotonic timestamps and expires by age. It can make entire old SSTables eligible for dropping when all their data has expired and no other SSTable can contain older shadowed values. It is less effective when old timestamps arrive late, TTLs vary widely, or old and new data mix.

### 12.4 Example table options

Use these only in an isolated experiment; do not change a production table's compaction strategy without testing and a rollback plan.

```sql
-- Legacy STCS comparison example.
CREATE TABLE telemetry.sensor_readings_stcs (
  device_id text,
  day date,
  hour tinyint,
  observed_at timestamp,
  reading_id uuid,
  value double,
  PRIMARY KEY ((device_id, day, hour), observed_at, reading_id)
) WITH compaction = {
  'class': 'SizeTieredCompactionStrategy'
};

-- TWCS time-series comparison example; verify options for your exact release.
CREATE TABLE telemetry.sensor_readings_twcs (
  device_id text,
  day date,
  hour tinyint,
  observed_at timestamp,
  reading_id uuid,
  value double,
  PRIMARY KEY ((device_id, day, hour), observed_at, reading_id)
) WITH compaction = {
  'class': 'TimeWindowCompactionStrategy',
  'compaction_window_unit': 'HOURS',
  'compaction_window_size': '1'
};
```

For Cassandra CQL option types, table option values in the compaction map are strings. The legacy `TimeWindowCompactionStrategy` class and option names are version-specific; verify the syntax against the exact release. In Cassandra 5.0, also evaluate UCS and its time-window-oriented configuration. TWCS settings are workload-dependent; one-hour windows are an experiment, not a universal recommendation.

### 12.5 Compare fairly

Keep schema, RF, dataset, row width, node count, hardware, write rate, retention, and query mix constant. Use fresh equivalent tables or reset the test data between runs. Measure:

- write throughput and p50/p95/p99 latency;
- read latency for recent range and older range queries;
- SSTable count and pending compactions;
- live disk size and temporary free-space headroom;
- tombstones scanned/warnings and expired SSTable reclamation;
- CPU, disk I/O, and compaction throughput.

Do not report “TWCS is faster” unless your measured workload supports it. Report the conditions and the trade-offs.

## 13. Repair and safe cluster operations

### 13.1 Before a repair

- Verify all nodes, datacentres, and racks with `nodetool status` and `nodetool describecluster`.
- Check free disk, pending compactions, streaming, and recent errors.
- Know the RF and which replica ranges the repair will cover.
- Confirm the repair schedule and whether your cluster uses full or incremental repair; avoid overlapping repairs that overload nodes.
- Use version-matched repair documentation. Repair is not a harmless “cleanup” command.

### 13.2 Useful `nodetool` commands

```bash
nodetool status
nodetool describecluster
nodetool info
nodetool version
nodetool tpstats
nodetool compactionstats
nodetool tablestats telemetry
nodetool netstats
nodetool gossipinfo
```

Exact availability and output vary by Cassandra version and packaging. Some commands accept keyspace/table arguments differently across releases. Capture outputs to a lab log rather than copying values from this lesson.

For a controlled local cluster, a documented repair invocation often looks like:

```bash
# Repair ranges replicated by the node on which this command runs.
# Review your Cassandra 5.0 distribution's nodetool repair options first.
nodetool repair -full telemetry sensor_readings

# For a planned full-cluster coverage, run primary-range repairs on each node
# in each datacentre, sequentially and with health/load checks between nodes.
nodetool repair -full -pr telemetry sensor_readings
```

Cassandra 5.0 documents `nodetool repair -full <keyspace> <table>` and `nodetool repair -full -pr <keyspace> <table>`; confirm the exact options with `nodetool help repair` on the installed binary. A full repair can stream substantial data and consume resources. The first command repairs ranges replicated by the node on which it runs; it is not a cluster-wide repair by itself. For full-cluster primary-range coverage, run the appropriate primary-range repair on each node in each datacentre, with health/load checks between nodes. In production, use your established repair orchestration, scope, and maintenance window rather than copying a lab command blindly.

### 13.3 Safe node-outage exercise

The roadmap exercise is not permission to stop a production node. Use a disposable three-node cluster and a non-critical keyspace.

1. Confirm RF 3 and `nodetool status` shows all three nodes `UN` (Up/Normal).
2. Choose a test partition and write a baseline value at `QUORUM`.
3. Stop exactly one node using the container/orchestrator's normal stop command. Confirm the other two are healthy and the node is actually down.
4. Issue a small number of test writes at `QUORUM`; with RF 3, two available replicas can satisfy quorum. Verify application behavior and capture timestamps/CL.
5. Restart the node and wait for it to rejoin and become `UN`. Do not assume it is fully caught up merely because the process started.
6. Check `nodetool netstats`, logs, hints, and cluster status. Allow hinted handoff to operate; then run the documented repair for the test keyspace/table using the version-matched command and a healthy cluster.
7. Read the test keys at a deliberate consistency level and verify expected values on the client. Capture the actual evidence.
8. Repeat only after the cluster returns to a healthy state.

Do not stop multiple nodes at once in a three-node RF3 lab. Do not lower `gc_grace_seconds`, delete system tables, manually remove SSTables, or force unsafe tombstone compaction to make the exercise “work.”

### 13.4 Adding/removing nodes and vnodes

Adding a node generally involves configuring compatible cluster name, snitch, seed settings, networking, authentication, and data directories; starting the node; validating status; and monitoring bootstrap streaming. Exact procedures differ by deployment tooling. Removing a node is a controlled decommission when the node is healthy and should transfer its data; `removenode` is a different recovery path for a dead node and must be used with care. Never simply delete a node's data directory or change its identity in a live cluster without a documented procedure.

Vnodes split token ownership into multiple ranges. They can smooth load distribution and simplify some expansion tasks, but increase range count and can complicate repair/operations. Validate `num_tokens` and topology with your distribution's current guidance. Avoid assuming vnodes cure hot partitions: a single partition remains assigned to one replica set.

### 13.5 Monitoring and capacity planning

Monitor at minimum:

- node status, dropped messages, pending tasks, GC pauses, heap/off-heap pressure;
- read/write latency and throughput by workload;
- compaction pending tasks, SSTable counts, disk utilization, and free disk headroom;
- hints, repair completion/coverage, streaming progress, and node-down duration;
- tombstone warnings, partition-size estimates, and skew/hot keys;
- commit-log and CDC disk usage where CDC is enabled;
- p95/p99 latency under realistic concurrency and node failure.

Capacity planning starts with logical data volume × RF, then adds compression/metadata, SSTable overlap during compaction, snapshots, hints, streaming/repair, CDC, and safety headroom. Measure the actual ratio for your dataset; do not assume replication is the only storage multiplier. Load testing must include the largest tenant/device and the skewed distribution, not only average keys.

## 14. Analytics extraction: token ranges, Spark, CDC

Cassandra is an operational store, not a replacement for a lakehouse. Large analytics scans should be planned so they do not saturate serving traffic.

### 14.1 Token-range scans

The partitioner's token ranges can be enumerated and read in bounded segments. A token-aware driver or controlled extraction job can distribute work and checkpoint progress. Exact token-range predicates and APIs depend on the driver and Cassandra version; avoid hand-coding token math without accounting for partitioner, topology, and range boundaries.

Operational rules:

- Prefer a Spark connector or a tested driver-based extractor over an uncontrolled full-table client loop.
- Use bounded concurrency, paging, and rate limits.
- Checkpoint completed token ranges so a failed job resumes idempotently.
- Use a consistent snapshot/export strategy if cross-partition temporal consistency matters; a token-range scan alone is not a point-in-time snapshot of a changing table.
- Isolate analytics workload when needed and monitor production p99 latency.

### 14.2 Spark Cassandra Connector

The Spark Cassandra Connector integrates Cassandra reads/writes with Spark DataFrames/RDDs. Version compatibility between Spark, Scala binary version, connector, and Cassandra must be checked. Partitioning/predicate pushdown and connector options affect load on Cassandra. Test on the exact versions; do not assume every Spark/Cassandra combination is compatible.

Use it when you need parallel extraction or transformations at scale, while controlling concurrency and preserving incremental/restart semantics. Do not point a large unconstrained Spark scan at a production cluster during peak traffic.

### 14.3 CDC logs

Cassandra's CDC feature can record mutations into commit-log segments for downstream processing when configured. CDC is not automatically a complete durable event bus: capacity, segment retention, consumer progress, duplicate handling, schema changes, and gaps need explicit management. Monitor CDC disk usage and ensure segments are not discarded before consumption. Check the Cassandra 5.0 CDC configuration and supported interfaces for the exact distribution.

A lakehouse pipeline should generally land raw change records, preserve source metadata/ordering where available, deduplicate idempotently, and apply changes using a deterministic key/version policy. Coordinate with Topic 09 on incremental NoSQL-to-lakehouse ingestion.

## 15. Cassandra 5.0: awareness notes

- Cassandra 5.0 includes Unified Compaction Strategy (UCS) and Storage-Attached Indexing (SAI); SAI also enables vector-search use cases in supported 5.0 deployments. Verify the precise feature, API, maturity, and configuration in the exact release/distribution rather than assuming every managed Cassandra service exposes the same capability.
- Do not assume older 3.x/4.x defaults, operational advice, index behavior, or command output maps exactly to 5.0.
- STCS, LCS, and TWCS remain useful to understand because existing systems and workloads use them; compare them with the UCS options available in the deployment you actually operate.
- Validate CQL syntax, index support, materialized-view behavior, repair options, CDC settings, and compaction defaults against the official docs for the exact patch version.
- This lesson is a practical foundation, not a substitute for the release notes and runbooks for your managed Cassandra service or distribution.

## 16. Hands-on lab: `experiments/04_cassandra/`

### 16.1 Lab goals and setup

Create this directory in your project repository. The lesson describes the experiment; it does not claim the cluster was run or that measurements were observed.

```text
experiments/04_cassandra/
├── README.md
├── docker-compose.yml          # 3-node Cassandra 5.0 lab, pinned image tag
├── cql/
│   ├── 01-schema.cql
│   ├── 02-load-test.cql
│   ├── 03-tombstone-test.cql
│   └── 04-compaction-tables.cql
├── scripts/
│   ├── generate_sensor_data.py
│   ├── load_sensor_data.py
│   └── run_queries.py
├── results/
│   ├── environment.md
│   ├── ingest-metrics.csv
│   ├── query-metrics.csv
│   ├── nodetool-before.txt
│   ├── nodetool-after.txt
│   └── observations.md
└── diagrams/
    └── partition-layout.md
```

**Setup requirements**

- Docker Engine + Docker Compose plugin, enough RAM/disk for three Cassandra nodes, Python 3.12+ and a Cassandra Python driver compatible with your cluster.
- Pin the Cassandra image to a specific 5.0 patch tag; do not use `latest` for a reproducible lab. Check the official image's configuration variables and container command for the tag you choose.
- Use an isolated local network and non-production data. Expose CQL only to your local machine. Keep persistent volumes for the duration of the lab and clean them only after saving results.
- Verify each node's cluster name, datacentre/rack, RF, and status before running failure/repair tests.
- Five million rows can require substantial RAM, disk, and time depending on payload size and container limits. Ensure free disk for compaction; if the host cannot support it, reduce rows for a smoke test and explicitly record that it did not meet the 5M requirement.

**Data-generation assumptions**

- Generate deterministic synthetic device IDs, timestamps, UUID row IDs, and bounded numeric sensor values.
- Use a fixed seed so runs are reproducible. Avoid generating all rows for one device before moving to the next if it creates unrealistic skew; also run a separate skewed test intentionally.
- Choose and document a row width (for example, temperature, humidity, status, and a small payload) and timestamp distribution.
- For five million rows over 100 devices and 30 days, the mean is about 1,667 rows/device/day; this average does not prove the largest partition is safe. Measure the maximum partition size and skew.
- Use prepared statements and bounded asynchronous concurrency in the loader; do not send five million individual unprepared statements serially or in an unbounded burst.


#### Reproducible 5-million-row generator

The following standard-library script streams a CSV to disk (it does not hold five million rows in memory). It assigns rows across 100 devices and 30 UTC days, spreads each device/day's readings across that day, uses a fixed random seed, and generates deterministic unique UUIDs. Change the arguments deliberately and record them with every run. The distribution is intentionally close to uniform; create a separate skewed workload to test hot-key risk.

```python
#!/usr/bin/env python3
"""Generate deterministic Cassandra sensor rows as a streaming CSV."""
import argparse
import csv
import random
import uuid
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path


def generate(path: Path, rows: int, devices: int, days: int, seed: int) -> None:
    if rows <= 0 or devices <= 0 or days <= 0:
        raise ValueError("rows, devices, and days must all be positive")
    rng = random.Random(seed)
    base_day = date(2026, 10, 1)
    rows_per_device_day = (rows + devices * days - 1) // (devices * days)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["device_id", "day", "observed_at", "reading_id",
                         "temperature_c", "humidity_pct"])
        for i in range(rows):
            device_index = i % devices
            day_index = (i // devices) % days
            slot = i // (devices * days)
            event_day = base_day + timedelta(days=day_index)
            seconds = slot * 86400 // rows_per_device_day
            observed = datetime.combine(event_day, time.min, tzinfo=timezone.utc)
            observed += timedelta(seconds=seconds)
            # Keep a valid UUID version/variant while preserving uniqueness for this range.
            reading_uuid = uuid.UUID(int=(4 << 76) | (0b10 << 62) | (i + 1))
            writer.writerow([
                f"device-{device_index:05d}", event_day.isoformat(),
                observed.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                str(reading_uuid), round(rng.uniform(-10.0, 45.0), 2),
                round(rng.uniform(0.0, 100.0), 2),
            ])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/sensor_readings.csv"))
    parser.add_argument("--rows", type=int, default=5_000_000)
    parser.add_argument("--devices", type=int, default=100)
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--seed", type=int, default=20261019)
    args = parser.parse_args()
    generate(args.output, args.rows, args.devices, args.days, args.seed)
    print(f"Generated {args.rows:,} rows at {args.output}; seed={args.seed}")
```

For a smoke test, use `--rows 10000 --output /tmp/sensor-smoke.csv`; inspect row count, date alignment, and uniqueness before generating the full file. The printed count reports rows written by the generator, not rows acknowledged by Cassandra.

#### Bounded prepared-statement loader pattern

This example shows the essential driver mechanics. Install a Python-driver version compatible with the selected Cassandra release, configure the correct contact points/local DC/authentication for your lab, and test with a small CSV first. It submits bounded chunks and counts successful responses; it does not claim exactly-once behavior across process crashes. After a failure, resume using an explicit checkpoint strategy and idempotent primary keys.

```python
#!/usr/bin/env python3
import csv
import uuid
from datetime import date, datetime
from cassandra.cluster import Cluster
from cassandra.concurrent import execute_concurrent_with_args
from cassandra.policies import DCAwareRoundRobinPolicy

CONTACT_POINTS = ["127.0.0.1"]
LOCAL_DC = "datacenter1"  # Replace with nodetool status output.
CSV_PATH = "results/sensor_readings.csv"
CHUNK_SIZE = 500
CONCURRENCY = 64

cluster = Cluster(
    CONTACT_POINTS,
    load_balancing_policy=DCAwareRoundRobinPolicy(local_dc=LOCAL_DC),
)
session = cluster.connect("cassandra_lab")
session.default_timeout = 30
statement = session.prepare("""
    INSERT INTO sensor_readings
      (device_id, day, observed_at, reading_id, temperature_c, humidity_pct)
    VALUES (?, ?, ?, ?, ?, ?)
""")

successes = 0
failures = 0
try:
    with open(CSV_PATH, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        while True:
            chunk = []
            for _ in range(CHUNK_SIZE):
                row = next(reader, None)
                if row is None:
                    break
                observed = datetime.fromisoformat(row["observed_at"].replace("Z", "+00:00"))
                chunk.append((
                    row["device_id"], date.fromisoformat(row["day"]), observed,
                    uuid.UUID(row["reading_id"]), float(row["temperature_c"]),
                    float(row["humidity_pct"]),
                ))
            if not chunk:
                break
            results = execute_concurrent_with_args(
                session, statement, chunk, concurrency=CONCURRENCY,
                raise_on_first_error=False,
            )
            for ok, result in results:
                if ok:
                    successes += 1
                else:
                    failures += 1
                    print(f"Write failed: {result!r}")
    print(f"successful acknowledgements={successes}, failures={failures}")
finally:
    cluster.shutdown()
```

The shown code is a minimal mechanics example, not a complete production loader: add retry classification, rate limits, checkpointing, authentication/TLS as required, and run metrics. A successful response count is a client-observed acknowledgement count, not an independent proof that all replicas contain each row.

### Exercise 1 — Five query patterns

Design and document the five tables in Section 6: messages by user, events by device per day, orders by customer, sensor readings by hour, and top posts. For each table include required query, key rationale, partition-size estimate, hot-key risk, read/write path, consistency choice, and operational trade-off. Draw the partition/clustering layout.

**Evaluation criteria:** each query has a complete partition key; clustering order matches requested range/sort; unbounded growth is addressed; no unsupported join/global-sort assumption; duplicated projections have a maintenance plan.

### Exercise 2 — Build and load `sensor_readings` (5 million rows)

Create `cql/01-schema.cql`:

```sql
CREATE KEYSPACE IF NOT EXISTS cassandra_lab
WITH replication = {'class': 'NetworkTopologyStrategy', 'dc1': 3};

CREATE TABLE IF NOT EXISTS cassandra_lab.sensor_readings (
  device_id text,
  day date,
  observed_at timestamp,
  reading_id uuid,
  temperature_c double,
  humidity_pct double,
  PRIMARY KEY ((device_id, day), observed_at, reading_id)
) WITH CLUSTERING ORDER BY (observed_at ASC, reading_id ASC);
```

This is the roadmap-required partition key `(device_id, day)`. Verify the actual datacentre name with `nodetool status`; change `dc1` to the cluster's real DC label. If a one-node smoke test is used, use RF 1 for that smoke test only and mark the RF3 requirement as not met.

1. Start the cluster and confirm all three nodes are `UN`.
2. Create the schema with `cqlsh` or a CQL driver.
3. Generate 5,000,000 unique `(device_id, day, observed_at, reading_id)` combinations.
4. Load using prepared statements and bounded concurrency; record elapsed time, client settings, node specs, and errors/retries.
5. Verify counts through the loader's acknowledged-row counter or controlled sampling. Avoid a full `COUNT(*)` as a casual Cassandra benchmark; it can be expensive and does not behave like an OLAP count.
6. Query one device and one day:

```sql
SELECT observed_at, reading_id, temperature_c, humidity_pct
FROM cassandra_lab.sensor_readings
WHERE device_id = 'device-00017'
  AND day = '2026-10-19'
  AND observed_at >= '2026-10-19T08:00:00Z'
  AND observed_at <  '2026-10-19T09:00:00Z'
LIMIT 500;
```

7. Demonstrate that the query supplies the complete partition key and a clustering range. Explain why it targets one logical partition/replica set, even though the coordinator may be any node and replicas may reside on multiple nodes.
8. Record observed latency, returned row count, and any trace/driver evidence. Do not invent expected milliseconds or claim a particular node was used unless you observed it.

**Evaluation criteria:** 5M rows actually loaded; key uniqueness checked; query uses `(device_id, day)` and a clustering range; environment/measurements are recorded; the lesson report distinguishes logical one-partition routing from “one physical node only” because RF>1 means multiple replicas.

### Exercise 3 — Create an unbounded partition, observe, redesign

In a separate disposable table, deliberately use only `device_id` as the partition key:

```sql
CREATE TABLE IF NOT EXISTS cassandra_lab.sensor_readings_unbounded (
  device_id text,
  observed_at timestamp,
  reading_id uuid,
  temperature_c double,
  PRIMARY KEY (device_id, observed_at, reading_id)
) WITH CLUSTERING ORDER BY (observed_at ASC, reading_id ASC);
```

Write increasing volumes for one device while observing partition growth, read latency, SSTable/compaction behavior, and server logs. Stop before exhausting disk or destabilizing the cluster. A large partition may not produce an immediate failure; record the risk and actual observations rather than manufacturing a warning.

Redesign as `PRIMARY KEY ((device_id, day), observed_at, reading_id)` or hourly `(device_id, day, hour)` when the measured/estimated daily volume is too large. Compare number of partitions, query fan-out for a multi-day read, maximum rows/bytes per partition, and tail latency.

**Evaluation criteria:** explain why one device forever is unbounded; show the new bounded key; estimate worst-case partition size from peak device rate; discuss extra fan-out and bucket-boundary logic.

### Exercise 4 — Delete many rows and investigate tombstones

1. Insert a known test population into a dedicated test partition/table. Record the exact row range and row count.
2. Capture baseline query latency, logs, `nodetool tablestats` (or version-equivalent), SSTable count, and compaction status.
3. Delete a large but safe subset using bounded deletes. Avoid a single massive logged batch.
4. Repeat the same read and capture any tombstone warnings/read-cost changes. If no warning appears, record that honestly.
5. Inspect TTL/deletion behavior, then allow compaction to run under normal conditions. Do not force unsafe tombstone purge or lower `gc_grace_seconds` to force a visible change.
6. Propose a safer design: time-bucketed partitions with retention, a suitable TTL, bounded deletes, or a separate lifecycle table. Explain that TTL creates tombstones too.

Example bounded deletion of a known row (replace bound values with your test data):

```sql
DELETE FROM cassandra_lab.sensor_readings
WHERE device_id = 'device-00017'
  AND day = '2026-10-19'
  AND observed_at = '2026-10-19T08:00:00Z'
  AND reading_id = 33333333-3333-4333-8333-333333333333;
```

**Evaluation criteria:** baseline vs post-delete evidence, exact data scope, no unsafe grace-period change, explanation of logical deletion vs physical purge, and a safer lifecycle proposal.

### Exercise 5 — Stop a node, write at QUORUM, restart, repair

Perform the safe procedure in Section 13.3 on the disposable three-node cluster. Save node status before/after, the CQL consistency level, mutation keys, relevant logs/hints/netstats, repair command/help output, and post-repair reads. Use the command syntax supported by your installed `nodetool`.

**Evaluation criteria:** only one node stopped; quorum writes succeeded or their failure was accurately recorded; restarted node returned to `UN`; repair was run after health checks; no data-resurrection claims unsupported by observations; no repair/compaction safety shortcuts.

### Exercise 6 — Compare STCS and TWCS

Create the two equivalent tables in Section 12.4. Use the same generator, row count, write order, TTL/retention, node count, RF, and query mix. Prefer a fresh cluster or fresh tables for each run and document any carry-over state. Capture write and read percentiles, compaction metrics, SSTable counts, disk use, and tombstone observations.

**Evaluation criteria:** apples-to-apples setup; raw results saved; STCS and TWCS trade-offs explained; no fabricated numbers; production recommendation explicitly conditioned on measured workload and late-arriving data/TTL behavior.

### Lab report template

```markdown
# Cassandra Lab Results
- Cassandra distribution/version and container image tag:
- Host resources / container limits:
- Node count, DC/rack labels, RF:
- Schema and compaction options:
- Dataset generator seed, row width, row count, skew:
- Loader concurrency / prepared statement settings:
- Query definitions and consistency levels:
- Metrics captured and how they were measured:
- Observed results (attach raw output/CSV; do not estimate as measured):
- Deviations from the 5M-row requirement:
- Partition-size and hot-key analysis:
- Tombstone/compaction/repair observations:
- Design changes and rationale:
- Limitations and follow-up tests:
```

## 17. Common mistakes and production anti-patterns

- Designing a normalized entity model first and hoping Cassandra will join it later.
- Partitioning only by a popular user/device/tenant when its history grows without bound.
- Choosing a key that looks evenly distributed on average but has a severe hot-key tail.
- Assuming clustering columns distribute data across nodes; only the partition key determines partition placement.
- Using `ALLOW FILTERING` to avoid fixing a schema for a production query.
- Treating a secondary index or SAI as a replacement for query-first modelling.
- Assuming `ORDER BY` sorts across partitions or that all rows are globally ordered.
- Treating `ONE`, `QUORUM`, and `ALL` as labels for “weak/strong” without considering RF, DC topology, read/write CL, and failure state.
- Treating a successful write acknowledgement as proof every replica has the latest mutation.
- Using giant logged batches for bulk ingestion or mass deletes.
- Treating TTL as immediate physical deletion.
- Lowering `gc_grace_seconds` without a repair and outage policy.
- Skipping repair because hinted handoff or read repair “should handle it.”
- Forcing major compaction without checking disk headroom and workload impact.
- Comparing compaction strategies with different schemas, data volumes, hardware, or load order.
- Running a full scan/Spark job at peak production load without concurrency limits.
- Assuming Cassandra 5 defaults and index features are identical to 3.x/4.x or managed-service distributions.
- Reporting benchmark numbers that were not measured.

## 18. Checkpoints

Before moving on, you should be able to check all of these:

- [ ] Explain partition key versus clustering columns, including composite partition keys.
- [ ] Design one query-first table for each of the five required access patterns.
- [ ] Draw partition/clustering layout and explain SSTable implications.
- [ ] Explain why arbitrary joins, filters, and global sorts are not Cassandra's model.
- [ ] Estimate rows/bytes per partition and identify hot-key risk.
- [ ] Choose and defend RF and a consistency level for a workload.
- [ ] Trace commit log, memtable, flush, SSTable, Bloom filter, cache, read reconciliation, and compaction.
- [ ] Explain collections, UDTs, static columns, TTL, counters, and LWT caveats.
- [ ] Explain secondary index, SAI, and materialized-view trade-offs.
- [ ] Explain tombstone creation, `gc_grace_seconds`, physical purge conditions, and zombie data.
- [ ] Compare STCS, LCS, and TWCS and recognize Cassandra 5.0 UCS awareness.
- [ ] Describe hinted handoff, read repair, and anti-entropy repair without treating them as interchangeable.
- [ ] Use `nodetool` to inspect health, compaction, streaming, and table statistics.
- [ ] Describe a safe one-node outage/quorum/repair lab.
- [ ] Explain bounded token-range extraction, Spark connector compatibility, and CDC operational requirements.

## 19. Practice questions

### Beginner

1. What determines which replicas store a Cassandra partition?
2. In `PRIMARY KEY ((tenant_id, day), event_time, event_id)`, identify the partition key and clustering columns.
3. Why can Cassandra return the latest 50 rows for one user efficiently but not sort every user's rows globally by timestamp?
4. What is the difference between a keyspace and a table?
5. Why does CQL resemble SQL but not support arbitrary joins?

### Intermediate

6. Design a schema for retrieving a device's readings from a known hour. Estimate maximum rows/bytes per partition at peak rate.
7. Why is a partition key with high cardinality not automatically a good key if one tenant dominates traffic?
8. With RF 3 in one DC, how many replicas must respond for `QUORUM`? What changes if one node is down?
9. Trace one write from the coordinator to commit log, memtable, and SSTable.
10. Why can a read query return only 10 live rows while still scanning many tombstones?
11. When is a static column useful? Why is a growing list collection risky?
12. What additional cost does `IF NOT EXISTS` impose, and when is it justified?
13. Why does SAI not eliminate the need to model important access patterns?

### Advanced

14. Explain a zombie-data scenario involving a node down longer than `gc_grace_seconds`.
15. Why does tombstone age alone not guarantee that compaction can purge it?
16. Compare STCS, LCS, and TWCS for an append-only sensor table with a 30-day TTL and late-arriving events.
17. Why is hinted handoff not a substitute for anti-entropy repair?
18. Design a safe procedure for taking one node down, writing at `QUORUM`, restarting it, and validating convergence.
19. How would you extract a very large table to a lakehouse without saturating online traffic or losing restartability?
20. Which observations would you capture to recommend TWCS over STCS? What would invalidate the recommendation?

## 20. Self-assessment rubric

Score each area from 0 to 3: **0** = cannot explain; **1** = can define terms; **2** = can design and test a working solution; **3** = can explain failure modes, quantify trade-offs, and defend operational choices.

| Skill | Score (0–3) | Evidence |
|---|---:|---|
| CQL and primary-key interpretation |  |  |
| Query-first table design |  |  |
| Partition size and hot-key reasoning |  |  |
| Replication and consistency choice |  |  |
| Read/write internals |  |  |
| Tombstones and safe retention |  |  |
| Compaction comparison |  |  |
| Repair and node operations |  |  |
| Analytics extraction/CDC |  |  |
| Lab measurement quality |  |  |

A score of 2 or 3 in every area, backed by lab evidence rather than memorized definitions, is a reasonable readiness threshold for moving to Topic 05. Revisit any area scored 0 or 1.

## 21. Further reading and version verification

Use official documentation for the exact version you install. The references below support the version-sensitive material in this lesson; managed Cassandra services may diverge in supported features and operational commands.

- [Apache Cassandra 5.0 — Data Definition / CQL primary keys](https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/ddl.html)
- [Apache Cassandra — CQL reference](https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/cql_singlefile.html)
- [Apache Cassandra — Compaction overview and tombstones](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/overview.html)
- [Apache Cassandra — Compaction strategies](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/index.html)
- [Apache Cassandra — `CREATE TABLE` reference](https://cassandra.apache.org/doc/5.0/cassandra/reference/cql-commands/create-table.html)
- [Apache Cassandra 5.0 — Repair and `nodetool repair`](https://cassandra.apache.org/doc/5.0/cassandra/managing/tools/nodetool/repair.html)
- [Apache Cassandra 5.0 — Unified Compaction Strategy](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/ucs.html)
- [Apache Cassandra 5.0 — Storage-Attached Indexing](https://cassandra.apache.org/doc/5.0/cassandra/developing/cql/indexing/sai/sai-overview.html)

---

**Completion standard:** You can model all five access patterns, demonstrate a bounded partition query on the five-million-row dataset, explain measured tombstone/compaction behavior without inventing results, and run the node-outage/repair exercise safely in a disposable cluster.
