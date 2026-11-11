# ClickHouse Architecture and MergeTree

> **Module:** Stage 2C — Data Engineering_3  
> **Location:** `Stage 2C — Data Engineering_3/07-Real-Time-OLAP-and-Query-Engines/01-clickhouse-architecture-and-mergetree.md`  
> **Prerequisites:** SQL and `EXPLAIN`; columnar storage, compression and partitioning; dimensional modelling; Kafka basics; Docker Compose; analytical warehouses.  
> **Scope:** ClickHouse architecture, MergeTree storage and operations. Druid, Pinot, Trino, StarRocks and Doris are covered by neighboring lessons.  
> **Roadmap dependencies:** SQL/`EXPLAIN`, columnar storage and compression, dimensional modelling, Kafka, Docker Compose; this lesson is Topic 01 and precedes the Druid/Pinot and Trino lessons.

## 1. Learning objectives

By the end, you should be able to:

- Explain where ClickHouse fits, and how columnar storage, vectorized execution and parallelism support analytical workloads.
- Run ClickHouse locally and query it through `clickhouse-client`, HTTP and Python's `clickhouse-connect`.
- Choose practical data types, ingest CSV, JSONEachRow and Parquet, and batch writes.
- Explain parts, merges, sorting keys, sparse primary indexes and granules.
- Design `PARTITION BY`, `ORDER BY`, codecs, skipping indexes and projections from actual query patterns.
- Select a suitable MergeTree-family engine and understand its consistency semantics.
- Build insert-triggered materialized views with mergeable aggregate states.
- Diagnose query performance and operate ingestion, mutations, replication, retention and backups.
- Run controlled experiments, including a benchmark that scales to 100 million rows without fabricating expected performance numbers.

## 2. The mental model

### 2.1 What ClickHouse is

ClickHouse is a column-oriented analytical database designed for high-throughput scans, aggregation and interactive analytics. Typical workloads include event analytics, logs, observability, product analytics, operational dashboards and time-series exploration.

A general-purpose warehouse can be a better choice when a workload relies heavily on complex joins, broad transactional semantics, frequent row-level updates or integrated governance and workload management. ClickHouse can execute joins; the point is not that joins are impossible, but that the schema, join pattern, data volume, memory use and concurrency must be evaluated against the intended workload.

### 2.2 Why columnar storage helps

A row-oriented layout stores values for a record together. A columnar layout stores values from the same column together. An analytics query such as:

```sql
SELECT country, sum(revenue)
FROM events
WHERE event_date >= today() - 7
GROUP BY country;
```

does not need every field from every event. Columnar storage can read only the columns needed by the filter, grouping and aggregate. Similar values in a column often compress well, and codecs can be selected by column.

### 2.3 Vectorized execution and parallelism

Rather than invoking a complete operator separately for every row, vectorized execution processes blocks or batches of values. This reduces per-row overhead and enables efficient CPU execution. ClickHouse can parallelize work across data ranges and threads, subject to available resources, query shape and storage layout.

```text
Client
  │ SQL
  ▼
Parser → Analyzer / Planner → Query pipeline
                              │
                    read selected columns
                              │
             parts → marks/granules → data blocks
                              │
               filters → aggregates → sorting
                              │
                         result blocks
```

The storage layout determines how much data the pipeline must read. The execution engine cannot compensate for every poor table-design decision.

### 2.4 Parts and merges: the central idea

A MergeTree insert normally creates one or more immutable data parts. Each part contains sorted column files and metadata for its partition. Background merge tasks combine compatible parts from the **same partition** into larger parts. Merges are asynchronous; they are not a transaction that rewrites the whole table after every insert. A merge does not consolidate rows across partition boundaries, which matters for engines whose deduplication/aggregation happens during merges.

```text
Insert batch A ──► Part A ─┐
Insert batch B ──► Part B ─┼── background merge ──► Part AB
Insert batch C ──► Part C ─┘                         (later merges)
```

This design makes ingestion and reads efficient, but it means that frequent tiny inserts create many parts, metadata overhead and merge pressure. Batch inserts whenever the workload permits. As a starting operational guideline, prefer batches of thousands of rows or larger rather than one insert per event; the appropriate batch size depends on payload size, freshness target and deployment.

## 3. Run ClickHouse locally

### 3.1 Docker Compose smoke environment

Create a working directory and save this as `docker-compose.yml`:

```yaml
services:
  clickhouse:
    # Pin a release tag for repeatable labs; update deliberately.
    image: clickhouse/clickhouse-server:26.8
    environment:
      CLICKHOUSE_DB: analytics
      CLICKHOUSE_USER: lab_user
      CLICKHOUSE_PASSWORD: ${CLICKHOUSE_PASSWORD:?Set CLICKHOUSE_PASSWORD in .env}
      CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT: "1"
    ports:
      - "127.0.0.1:8123:8123"   # HTTP, local host only
      - "127.0.0.1:9000:9000"   # native protocol, local host only
    volumes:
      - clickhouse_data:/var/lib/clickhouse
    ulimits:
      nofile:
        soft: 262144
        hard: 262144

volumes:
  clickhouse_data:
```

This is a local learning setup, not a production deployment. The example pins the documented `26.8` release line for repeatability; it was not runtime-tested here, and you should deliberately update to a currently supported release after validating the lab. No production credentials are embedded. Do not expose a test instance to an untrusted network.

Create a local `.env` file (do not commit it) containing a lab-only password:

```dotenv
CLICKHOUSE_USER=lab_user
CLICKHOUSE_PASSWORD=replace-with-a-long-local-lab-password
CLICKHOUSE_DATABASE=analytics
CLICKHOUSE_HOST=127.0.0.1
CLICKHOUSE_PORT=8123
```

Start and inspect:

```bash
docker compose up -d
docker compose ps
docker compose logs --tail=100 clickhouse
```

Export the variable in your shell before using the host-side clients (`set -a; . ./.env; set +a` in a POSIX shell). Native client (if installed locally):

```bash
clickhouse-client --host 127.0.0.1 --port 9000 --user lab_user --password "$CLICKHOUSE_PASSWORD" --query "SELECT version()"
```

Or execute through the container (Compose passes the password in the container environment):

```bash
docker compose exec clickhouse clickhouse-client --user lab_user --password "$CLICKHOUSE_PASSWORD" --query "SELECT version()"
```

HTTP interface:

```bash
curl --fail --silent --show-error --user "lab_user:${CLICKHOUSE_PASSWORD}" \
  --data-binary 'SELECT version()' http://127.0.0.1:8123/
```

Stop the environment with `docker compose down`. To also delete persisted learning data, use `docker compose down -v`; this is destructive.

### 3.2 Python client

Create a Python 3.12+ environment using `uv`:

```bash
uv init clickhouse-lab
cd clickhouse-lab
uv add clickhouse-connect
```

Example `smoke.py`:

```python
import os
import clickhouse_connect

client = clickhouse_connect.get_client(
    host=os.getenv("CLICKHOUSE_HOST", "127.0.0.1"),
    port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
    username=os.environ["CLICKHOUSE_USER"],
    password=os.environ["CLICKHOUSE_PASSWORD"],
    database=os.getenv("CLICKHOUSE_DATABASE", "analytics"),
)

result = client.query("SELECT version()")
print(result.result_rows)
client.close()
```

The example reads credentials from environment variables rather than embedding them in source. Run it in the shell where you exported `.env` values. The code is statically reviewed; it has not been executed as part of this document's preparation.

## 4. Create an events table

### 4.1 Practical data types

- `DateTime64(3, 'UTC')`: timestamp with millisecond precision and an explicit timezone convention.
- `LowCardinality(String)`: dictionary-encoded representation that can help when a string column has relatively few distinct values compared with its row count, such as `country` or `event_type`.
- `Nullable(T)`: represents missing values explicitly. Nullability adds semantics and can add storage or execution overhead; do not use it automatically for every field.
- `Array(T)`: multiple values of one type per row.
- `Map(K, V)`: key/value attributes. Repeated keys and access patterns should be understood before choosing this model.
- `Tuple(...)`: a fixed structured value with named or positional elements.
- `JSON`: a flexible semi-structured type whose exact behavior and performance depend on the ClickHouse version and JSON implementation. For stable, frequently filtered attributes, typed columns may be simpler and more efficient.

A minimal example of the `JSON` type is shown below. The native `JSON` type and its subcolumn behavior are version-sensitive; use it only on a release that supports it in your deployment, and prefer ordinary typed columns for stable, frequently queried attributes.

```sql
CREATE TABLE analytics.event_payloads
(
    event_id UUID,
    received_at DateTime64(3, 'UTC'),
    payload JSON
)
ENGINE = MergeTree
ORDER BY (received_at, event_id);

INSERT INTO analytics.event_payloads FORMAT JSONEachRow
{"event_id":"00000000-0000-0000-0000-000000000011","received_at":"2026-01-10 10:00:00.123","payload":{"campaign":"winter","score":0.9}};

SELECT payload.campaign, payload.score
FROM analytics.event_payloads;
```

### 4.2 Schema and sample data

```sql
CREATE DATABASE IF NOT EXISTS analytics;

CREATE TABLE analytics.events
(
    event_time DateTime64(3, 'UTC'),
    event_date Date MATERIALIZED toDate(event_time),
    tenant LowCardinality(String),
    user_id UInt64,
    event_id UUID,
    event_type LowCardinality(String),
    country LowCardinality(String),
    revenue Decimal(12, 2),
    is_conversion UInt8,
    tags Array(String),
    attributes Map(String, String),
    device Tuple(kind String, os String),
    campaign Nullable(String)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_date)
ORDER BY (tenant, event_date, user_id, event_time, event_id);
```

`event_date` is materialized from `event_time`, so inserts should provide `event_time`, not a separate value for `event_date`. `ORDER BY` is a sorting key and is not the same thing as a uniqueness constraint. `event_id` is included as a tie-breaker, not as an enforced unique key.

Insert a few rows:

```sql
INSERT INTO analytics.events
    (event_time, tenant, user_id, event_id, event_type, country,
     revenue, is_conversion, tags, attributes, device, campaign)
VALUES
    ('2026-01-10 10:00:00.123', 'acme', 101,
     '00000000-0000-0000-0000-000000000001', 'page_view', 'IN',
     0.00, 0, ['home', 'mobile'], {'source':'ad'}, ('phone','Android'), 'winter'),
    ('2026-01-10 10:00:01.123', 'acme', 102,
     '00000000-0000-0000-0000-000000000002', 'purchase', 'IN',
     29.99, 1, ['checkout'], {'source':'email'}, ('desktop','Linux'), NULL);
```

Query it:

```sql
SELECT tenant, count() AS events, sum(revenue) AS revenue
FROM analytics.events
GROUP BY tenant;
```

### 4.3 CSV, JSONEachRow and Parquet

For production-like loads, use bulk formats rather than a loop that inserts one row at a time.

CSV (column order must match the target columns or an explicit column list):

```bash
clickhouse-client --query \
  "INSERT INTO analytics.events (event_time, tenant, user_id, event_id, event_type, country, revenue, is_conversion, tags, attributes, device, campaign) FORMAT CSV" \
  < events.csv
```

CSV parsing for complex nested columns needs a correctly encoded representation; for the first CSV exercise, a simplified table with scalar columns is easier to validate.

JSONEachRow sends one JSON object per line:

```bash
clickhouse-client --query \
  "INSERT INTO analytics.simple_events FORMAT JSONEachRow" < events.jsonl
```

Example line:

```json
{"event_time":"2026-01-10 10:00:00.123","tenant":"acme","user_id":101,"event_type":"page_view"}
```

For Parquet files accessible to the server, `INSERT ... SELECT` with the `file` table function is one option for a local file:

```sql
INSERT INTO analytics.simple_events
SELECT *
FROM file('/var/lib/clickhouse/user_files/events.parquet', Parquet);
```

The file must be in a path permitted by the server's user-file configuration and have columns compatible with the target. Another common path is reading an object in object storage with the `s3` table function. Check the server's access configuration before using either function.

A minimal scalar table for the CSV/JSON/Parquet examples:

```sql
CREATE TABLE analytics.simple_events
(
    event_time DateTime64(3, 'UTC'),
    tenant String,
    user_id UInt64,
    event_type String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(toDate(event_time))
ORDER BY (tenant, event_time, user_id);
```

## 5. MergeTree internals in detail

### 5.1 Parts, marks and granules

Each inserted part is sorted according to the table's sorting key. It contains per-column data and metadata that let ClickHouse find candidate ranges efficiently. The sparse primary index stores key values at granule boundaries rather than an entry for every row. The commonly used default index granularity is about 8,192 rows per granule, but adaptive granularity and settings mean that actual granule sizes can vary.

A query with a selective filter can use the primary index to identify relevant granules and skip others. It still reads the needed columns for the selected ranges. The index is most effective when predicates constrain a useful prefix/range of the key; filtering only on a later key column may still require broad reads. Partition pruning is a separate earlier exclusion mechanism. This differs from a traditional row-level B-tree index that directly locates individual rows.

```text
Part sorted by (tenant, event_date, user_id)
┌────────────────────────────────────────────┐
│ granule 0 │ granule 1 │ granule 2 │ ...    │
└─────┬──────────┬──────────┬────────────────┘
      marks identify candidate ranges
      filter on leading key columns
      skips granules whose key ranges cannot match
```

### 5.2 `ORDER BY` versus `PRIMARY KEY`

`ORDER BY` defines the physical sorting key. `PRIMARY KEY` defines the sparse primary-index key and, when specified, must be a prefix of the sorting key. If `PRIMARY KEY` is omitted, the sorting key is normally used for the primary index.

```sql
CREATE TABLE analytics.events_short_index
(
    tenant String,
    event_date Date,
    user_id UInt64,
    event_time DateTime64(3, 'UTC'),
    event_type String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_date)
PRIMARY KEY (tenant, event_date)
ORDER BY (tenant, event_date, user_id, event_time);
```

This stores data sorted by all four columns while indexing only the first two. A shorter primary key can reduce index size, but it may provide less pruning power for filters that depend on later sorting-key columns. Select key order from common predicates: leading columns are particularly important for primary-index pruning. The example `(tenant, event_date, user_id)` is reasonable when queries commonly constrain tenant and date and then filter/group by user; it is not universally optimal.

### 5.3 Part lifecycle and inspection

Inspect active parts:

```sql
SELECT
    partition,
    name,
    rows,
    formatReadableSize(bytes_on_disk) AS disk_size,
    level,
    active
FROM system.parts
WHERE database = 'analytics'
  AND table = 'events'
ORDER BY partition, name;
```

Inspect merge activity:

```sql
SELECT *
FROM system.merges
WHERE database = 'analytics';
```

Inspect recent part events (available fields may vary by version):

```sql
SELECT event_type, event_time, part_name, rows, size_in_bytes
FROM system.part_log
WHERE database = 'analytics'
ORDER BY event_time DESC
LIMIT 50;
```

A part's merge level is useful evidence of merge history, but do not interpret a single snapshot as a complete merge-health diagnosis. Part count must be considered with insert rate, partition count, bytes, merge backlog and server resources. `system.parts` reports active/inactive parts, `system.merges` shows current merges, `system.part_log` records part events when enabled, and `system.mutations` helps track mutation progress. Avoid relying on one instantaneous snapshot.

### 5.4 Partitioning

`PARTITION BY` groups data into independently managed partition ranges. Monthly partitions are a common starting point for event data because they make retention and partition-level operations manageable. Partition pruning can reduce the parts considered when a query filters on the partition expression, but it is distinct from primary-index pruning and is not an automatic speed switch: sorting, column selection and query shape often matter more. Merges occur within a partition, so versions of one logical row should normally share a partition if merge-time deduplication is expected.

Avoid partitioning by high-cardinality values such as user ID or event ID. Each partition and insert can contribute parts and metadata; too many small partitions or parts increase operational overhead. A practical default is to partition by a coarse time unit when data lifecycle requirements justify it, and rely on sorting keys for most query pruning.

### 5.5 Compression and column design

Common codecs:

- `LZ4`: fast compression/decompression, commonly used where CPU cost matters.
- `ZSTD`: often better compression at a higher CPU cost; test levels and workload.
- `Delta`: stores differences between sequential numeric values, useful for monotonic-ish values.
- `DoubleDelta`: encodes differences of differences, useful for steadily changing sequences such as timestamps.
- `Gorilla`: designed for changing numeric/time-series values, particularly floating-point series; validate compatibility with the column type and version.

Example:

```sql
CREATE TABLE analytics.metrics
(
    ts DateTime64(3, 'UTC') CODEC(Delta, ZSTD),
    sensor_id LowCardinality(String),
    value Float64 CODEC(Gorilla, ZSTD)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(toDate(ts))
ORDER BY (sensor_id, ts);
```

Codecs are a measured choice, not a guaranteed improvement. Check read CPU, compression ratio and query latency. Column order in the table definition can affect physical file organization and locality, but the sorting key controls row order; do not confuse those two meanings of “order.” `LowCardinality` is generally useful for repeated categorical values, but may be less useful when almost every value is unique.

### 5.6 Skipping indexes

Skipping indexes summarize blocks of data so ClickHouse can skip blocks that cannot satisfy a predicate. They do not replace a well-chosen sorting key.

```sql
ALTER TABLE analytics.events
    ADD INDEX idx_campaign_bloom campaign TYPE bloom_filter(0.01) GRANULARITY 4;
```

After adding an index, existing parts may require materialization before the index is present for all data:

```sql
ALTER TABLE analytics.events MATERIALIZE INDEX idx_campaign_bloom;
```

Types and trade-offs:

- `minmax`: stores minimum and maximum values; useful when values within blocks have locality. Weak for randomly distributed values with broad ranges.
- `set(max_rows)`: stores distinct values for a block up to a configured limit; useful for low-cardinality values when the set stays small. It can be ineffective when values are too numerous.
- `bloom_filter`: probabilistic membership filter; can reduce reads for selective equality/membership predicates, but may produce false positives and cannot prove absence incorrectly. Tune and benchmark it.

The example is meaningful only if `campaign` exists in the table and the chosen type supports the index. For a `Nullable` or nested column, validate exact index support and predicate semantics for the deployed version.

### 5.7 Projections

A projection stores an additional representation of table data, potentially with a different sort order or aggregation. The optimizer may choose it when it can answer a query more efficiently.

```sql
ALTER TABLE analytics.events
ADD PROJECTION by_event_type
(
    SELECT tenant, event_type, event_date, count()
    GROUP BY tenant, event_type, event_date
);
```

Materialize for existing data where appropriate:

```sql
ALTER TABLE analytics.events MATERIALIZE PROJECTION by_event_type;
```

Projections consume storage and add write/merge work. Optimizer selection depends on the query and version; confirm the selected plan with `EXPLAIN` rather than assuming the projection will always be used.

## 6. MergeTree-family engines and correctness

The base `MergeTree` engine is append-oriented. Specialized variants alter what happens when rows with related keys are merged; they do not make inserts behave like transactional row-by-row updates.

### 6.1 `ReplacingMergeTree`

Use when multiple versions of a logical row can arrive and the latest version should eventually win. Define a sorting key that identifies the logical row and, optionally, a version column:

```sql
CREATE TABLE analytics.user_state
(
    user_id UInt64,
    version UInt64,
    status String,
    updated_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(version)
ORDER BY user_id;

INSERT INTO analytics.user_state VALUES
    (7, 1, 'trial', '2026-01-01 00:00:00.000'),
    (7, 2, 'paid',  '2026-01-02 00:00:00.000');
```

Before a merge, ordinary reads may see both versions. Background merges eventually remove superseded rows only within the same partition/merge scope. If versions of one logical key are assigned to different partitions, background merges cannot deduplicate them across that boundary; design the partition key so versions stay together when this engine is used for current-state semantics. This is not a uniqueness constraint and does not guarantee immediate deduplication. A `FINAL` query can apply merge semantics at read time:

```sql
SELECT * FROM analytics.user_state FINAL WHERE user_id = 7;
```

`FINAL` can add CPU and memory work, especially over many parts or large ranges. Prefer explicit version-aware query patterns or a data model suited to the freshness requirement when possible. Do not use `ReplacingMergeTree` as a substitute for transactional uniqueness enforcement.

### 6.2 `SummingMergeTree`

Rows with the same sorting key can have eligible numeric columns summed during merges (you can explicitly choose which columns are summed in the engine declaration). Reads must still aggregate when matching rows remain in separate parts:

```sql
CREATE TABLE analytics.daily_totals
(
    day Date,
    tenant String,
    events_count UInt64,
    revenue Decimal(18, 2)
)
ENGINE = SummingMergeTree
ORDER BY (day, tenant);
```

Query with `GROUP BY day, tenant` and `sum(...)` for correct results regardless of whether background merges have combined all rows.

### 6.3 `AggregatingMergeTree`

Stores aggregate states rather than only final scalar values. It is useful for mergeable aggregates such as distinct-count sketches or quantile states. State types must match the aggregate function and be combined with the corresponding `...Merge` function.

```sql
CREATE TABLE analytics.daily_user_states
(
    day Date,
    tenant String,
    users AggregateFunction(uniq, UInt64),
    revenue_sum AggregateFunction(sum, Decimal(18, 2))
)
ENGINE = AggregatingMergeTree
ORDER BY (day, tenant);
```

The materialized-view example in the next section populates this table.

### 6.4 `CollapsingMergeTree`

Stores signed rows that represent changes to a logical record. The sign column is conventionally `Int8` and contains `1` for an inserted/current version and `-1` for a row to cancel. Rows with the same sorting key and opposite sign can cancel during merges; queries over unmerged parts must account for both signs. Correctness depends on a disciplined event/sign model, including out-of-order changes and unmatched signs. It is useful for particular change-log patterns, but is more difficult to reason about than append-only facts and should not be selected without a precise correctness model.

```sql
CREATE TABLE analytics.account_changes
(
    account_id UInt64,
    balance Decimal(18, 2),
    sign Int8
)
ENGINE = CollapsingMergeTree(sign)
ORDER BY account_id;
```

This is a schema illustration, not a complete change-capture protocol; the producer must emit paired/correctly ordered state transitions and the query must use sign-aware semantics until rows have collapsed.

### 6.5 Insert-time behavior versus merge-time behavior

Materialized views and Kafka consumers can act when data is inserted. Replacing, summing, aggregating and collapsing behavior may be finalized only as parts merge or at query time. Never assume that background merges run immediately or in a deterministic time bound.

## 7. Incremental materialized views and aggregate states

An incremental materialized view processes inserted blocks and writes transformed rows to a target table. It is not a continuously recomputed query over all historical source rows. Existing data normally requires a separate backfill strategy when the view is created after the source already contains data.

```sql
CREATE TABLE analytics.events_for_rollup
(
    event_time DateTime64(3, 'UTC'),
    tenant String,
    user_id UInt64,
    revenue Decimal(18, 2)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(toDate(event_time))
ORDER BY (tenant, event_time, user_id);

CREATE TABLE analytics.hourly_rollup
(
    hour DateTime('UTC'),
    tenant String,
    event_count AggregateFunction(count),
    unique_users AggregateFunction(uniq, UInt64),
    revenue_sum AggregateFunction(sum, Decimal(18, 2))
)
ENGINE = AggregatingMergeTree
ORDER BY (hour, tenant);

CREATE MATERIALIZED VIEW analytics.events_to_hourly_rollup
TO analytics.hourly_rollup
AS
SELECT
    toStartOfHour(event_time) AS hour,
    tenant,
    countState() AS event_count,
    uniqState(user_id) AS unique_users,
    sumState(revenue) AS revenue_sum
FROM analytics.events_for_rollup
GROUP BY hour, tenant;
```

Query the states correctly:

```sql
SELECT
    hour,
    tenant,
    countMerge(event_count) AS events,
    uniqMerge(unique_users) AS users,
    sumMerge(revenue_sum) AS revenue
FROM analytics.hourly_rollup
GROUP BY hour, tenant
ORDER BY hour, tenant;
```

Why states matter: `uniqState` stores a mergeable representation of the distinct-count computation. Summing final distinct counts from separate blocks would double-count users present in more than one block. `uniqMerge` combines states using the aggregate's semantics. Similarly, `avg(a)` cannot generally be rolled up by averaging averages unless group sizes are equal; preserve sum and count or use a suitable aggregate state.

Incremental materialized views process newly inserted source blocks. They do not automatically repair a target if source rows are later mutated or deleted. Late-arriving events can be included in the relevant historical bucket, but corrections and retractions require an explicit strategy: compensating events, rebuilding affected partitions, or a controlled backfill. Reconcile rollups against raw data.

## 8. Updates, deletes and data lifecycle

### 8.1 Lightweight deletes and mutations

For supported versions and settings, lightweight deletes use `DELETE FROM ... WHERE ...` to mark matching rows as deleted and filter them from reads before physical cleanup. Availability and compatibility depend on the ClickHouse release and table features; verify the deployed version. Mutation-based `ALTER TABLE ... DELETE` and `ALTER TABLE ... UPDATE` rewrite affected data asynchronously and can be expensive for large ranges.

```sql
-- Lightweight delete: supported versions/settings only; verify the target first.
DELETE FROM analytics.events_for_rollup
WHERE event_time < toDateTime64('2025-01-01 00:00:00', 3, 'UTC');

-- Mutation-based delete and update (heavier rewrite operations):
ALTER TABLE analytics.events_for_rollup
DELETE WHERE event_time < toDateTime64('2025-01-01 00:00:00', 3, 'UTC');

ALTER TABLE analytics.events_for_rollup
UPDATE revenue = 0
WHERE tenant = 'test-tenant'
  AND event_time >= toDateTime64('2026-01-01 00:00:00', 3, 'UTC')
  AND event_time <  toDateTime64('2026-01-02 00:00:00', 3, 'UTC');
```

These statements are intentionally scoped examples. Mutations are not equivalent to cheap in-place OLTP updates. For frequently changing entities, consider append-only versioned rows with query semantics designed for the required freshness. Monitor mutation progress and disk/CPU pressure.

### 8.2 TTL, tiered storage and retention

TTL policies can expire rows or move data between storage volumes according to configured rules. Retention should be designed around legal requirements, user expectations, late-arriving data and recovery needs. Tiered storage can keep recent data on faster media and older data on cheaper media, but retrieval latency and operational complexity may change.

A minimal local-disk policy shape (configure paths and mount points for the actual storage devices, then validate server configuration before restart) is:

```xml
<clickhouse>
  <storage_configuration>
    <disks>
      <hot><path>/var/lib/clickhouse/hot/</path></hot>
      <cold><path>/var/lib/clickhouse/cold/</path></cold>
    </disks>
    <policies>
      <tiered>
        <volumes>
          <hot><disk>hot</disk></hot>
          <cold><disk>cold</disk></cold>
        </volumes>
      </tiered>
    </policies>
  </storage_configuration>
</clickhouse>
```

The paths must be writable and should map to the intended storage classes; putting both paths on the same device does not create a meaningful cost tier. After the policy exists, a table can select it and define a TTL move:

```sql
CREATE TABLE analytics.tiered_events
(
    event_time DateTime64(3, 'UTC'),
    tenant String,
    payload String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(toDate(event_time))
ORDER BY (tenant, event_time)
TTL event_time + INTERVAL 30 DAY TO VOLUME 'cold',
    event_time + INTERVAL 180 DAY DELETE
SETTINGS storage_policy = 'tiered';
```

This is an illustrative configuration template, not a ready-to-deploy storage policy. TTL movement and deletion are asynchronous; validate the volume names, disk configuration and behavior on the target version.

Illustrative table TTL syntax should be checked against the deployment's storage policy and version before use:

```sql
-- Example retention policy: keep event rows for 180 days.
ALTER TABLE analytics.events
MODIFY TTL event_time + INTERVAL 180 DAY DELETE;
```

TTL actions are asynchronous and should not be treated as an exact-time deletion guarantee.

## 9. Distributed architecture and ingestion

### 9.1 Shards, replicas, Distributed tables and Keeper

- **Shard:** a subset of the dataset. Sharding can distribute storage and query work, but requires a deliberate sharding key and operational planning.
- **Replica:** another copy of a shard's data for availability and read scaling. Replication behavior depends on configuration and engine.
- **`ReplicatedMergeTree`:** a MergeTree-family engine that coordinates replicated table metadata and data-part replication through ClickHouse Keeper or ZooKeeper-compatible coordination.
- **`Distributed` table:** a logical routing/query layer over remote tables. It does not itself store the underlying rows. It can route inserts and distribute queries according to configuration.
- **ClickHouse Keeper:** coordination service used by replicated tables and related distributed operations.

Sharding can make joins and aggregations more complicated if matching keys are not colocated. A `Distributed` query may fan out to shards and combine partial results; network, remote execution, replica selection, and data skew affect latency. Distributed inserts can be buffered/forwarded depending on settings, so do not assume a client insert is synchronously durable on every shard/replica without checking the write path and consistency settings. Replication improves resilience but does not replace backups; accidental deletion or corruption can replicate too.

A simplified DDL pattern for a configured cluster is below. The cluster named `analytics_cluster`, Keeper/ZooKeeper service, and `{shard}` / `{replica}` macros must already exist in server configuration; this is a template, not a standalone local setup.

```sql
CREATE TABLE analytics.events_local ON CLUSTER analytics_cluster
(
    event_time DateTime64(3, 'UTC'),
    tenant LowCardinality(String),
    user_id UInt64,
    event_type LowCardinality(String)
)
ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/analytics/events_local',
    '{replica}'
)
PARTITION BY toYYYYMM(toDate(event_time))
ORDER BY (tenant, event_time, user_id);

CREATE TABLE analytics.events_all ON CLUSTER analytics_cluster
AS analytics.events_local
ENGINE = Distributed(
    'analytics_cluster', 'analytics', 'events_local', cityHash64(tenant)
);
```

Inspect replica health and queued replication work (fields/settings can vary by release):

```sql
SELECT database, table, is_readonly, queue_size, inserts_in_queue,
       merges_in_queue, absolute_delay
FROM system.replicas
WHERE database = 'analytics';

SELECT database, table, type, create_time, num_tries, last_exception
FROM system.replication_queue
WHERE database = 'analytics'
ORDER BY create_time DESC
LIMIT 20;
```

### 9.2 Kafka ingestion options

1. **Kafka table engine:** ClickHouse reads Kafka topics through a Kafka engine table, commonly paired with a materialized view that writes into a MergeTree target. It is useful for a self-managed integration, but requires careful consumer, retry, duplicate and delivery-semantics design.
2. **ClickPipes:** a managed ingestion option in ClickHouse Cloud. Availability and supported sources vary by service/version.
3. **Kafka Connect:** an ecosystem integration pattern; connector capabilities and delivery guarantees depend on the selected connector and configuration.

A typical flow:

```text
Kafka topic → Kafka-engine table → incremental materialized view
                                      │
                                      ▼
                                MergeTree target
                                      │
                                      ▼
                               dashboard queries
```

The following is a minimal **template** for a broker reachable as `kafka:9092` from the ClickHouse server/container. The topic and schema must exist, and authentication/TLS settings must be added for secured deployments:

```sql
CREATE TABLE analytics.kafka_events
(
    event_id UUID,
    produced_at DateTime64(3, 'UTC'),
    event_time DateTime64(3, 'UTC'),
    tenant String,
    user_id UInt64,
    event_type String
)
ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'events',
    kafka_group_name = 'clickhouse-events-lab',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 1;

CREATE TABLE analytics.kafka_events_target
(
    event_id UUID,
    produced_at DateTime64(3, 'UTC'),
    event_time DateTime64(3, 'UTC'),
    tenant String,
    user_id UInt64,
    event_type String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(toDate(event_time))
ORDER BY (tenant, event_time, event_id);

CREATE MATERIALIZED VIEW analytics.kafka_events_to_target
TO analytics.kafka_events_target
AS SELECT * FROM analytics.kafka_events;
```

This template is statically reviewed, not executed; Kafka engine settings and behavior are version-sensitive. Do not treat Kafka-to-ClickHouse ingestion as universal exactly-once delivery: failures and retries can produce duplicates, and deduplication/consumer semantics depend on the full configuration. For the hands-on experiment, use the official documentation for the exact version, then record the event timestamp at production and query time to measure freshness. Account for duplicates, retries and consumer lag.

### 9.3 Object storage

The `s3` table function can query supported object-storage files or read from an object store using configured credentials. For a publicly readable Parquet object, a read-only example is:

```sql
SELECT *
FROM s3('https://example-bucket.s3.amazonaws.com/events/*.parquet', 'Parquet')
LIMIT 10;
```

For a private bucket, use the supported authentication mechanism for the deployment (for example, IAM role/instance identity, named collection, or a managed secret); do not paste long-lived keys into SQL committed to source control. A load into the scalar lab table can be expressed as:

```sql
INSERT INTO analytics.simple_events (event_time, tenant, user_id, event_type)
SELECT event_time, tenant, user_id, event_type
FROM s3('https://example-bucket.s3.amazonaws.com/events/*.parquet', 'Parquet');
```

`S3Queue` is intended for queue-like ingestion from object storage. Its arguments, queue mode, Keeper coordination, and after-processing settings have evolved, so treat this as a shape to adapt to the deployed release rather than a copy-paste command:

```sql
-- Template only; verify S3Queue syntax and settings for your exact release.
CREATE TABLE analytics.s3_events_queue
(
    event_time DateTime64(3, 'UTC'),
    tenant String,
    user_id UInt64,
    event_type String
)
ENGINE = S3Queue(
    'https://example-bucket.s3.amazonaws.com/landing/*.jsonl',
    'JSONEachRow'
)
SETTINGS mode = 'unordered';
```

For continuous consumption, attach a materialized view to the queue table and write into a MergeTree target, then monitor processed files, failures and duplicates. Validate object paths, permissions, format and schema before large ingestion.

## 10. Query analysis and production operations

### 10.1 `EXPLAIN`

Start with a plan:

```sql
EXPLAIN
SELECT country, count()
FROM analytics.events
WHERE tenant = 'acme'
  AND event_date >= today() - 7
GROUP BY country;
```

Inspect index use:

```sql
EXPLAIN indexes = 1
SELECT count()
FROM analytics.events
WHERE tenant = 'acme'
  AND event_date >= today() - 7;
```

`EXPLAIN indexes = 1` is supported by current ClickHouse versions, but plan output and details are version-sensitive. Check the version running in the lab and compare actual execution, not just the plan.

### 10.2 Query log

Enable logging if required by the environment, run the query, then inspect it after the log flush interval:

```sql
SYSTEM FLUSH LOGS;

SELECT
    event_time,
    query_duration_ms,
    read_rows,
    formatReadableSize(read_bytes) AS read_size,
    memory_usage,
    query
FROM system.query_log
WHERE type = 'QueryFinish'
  AND query ILIKE '%analytics.events%'
ORDER BY event_time DESC
LIMIT 20;
```

Avoid collecting sensitive query text in shared logs. Query logs may not contain the query until it finishes or logs are flushed. Compare repeated runs and record cache effects; do not report a single run as a reliable benchmark.

### 10.3 Memory, joins and concurrency

Use settings and limits appropriate to the workload; inspect memory usage and query failures. For a controlled lab query, for example, `SET max_memory_usage = 2000000000;` applies a per-query memory limit of roughly 2 GB (bytes; server/session policy may impose tighter limits). Do not increase limits blindly to mask an inefficient query. Join performance depends on table sizes, join algorithm, key cardinality, sort/order, distribution and memory. Filter early, project only required columns, maintain appropriate data layout, and test join strategies. For repeated dashboard joins, denormalization or pre-aggregation can reduce per-query work, but increases storage and data-maintenance complexity.

High concurrency changes the problem: a query that is fast in isolation may compete for CPU, memory, I/O or thread slots under load. Measure p50/p95/p99 latency and throughput at representative concurrency rather than relying on a single stopwatch run.

### 10.4 Backups and deployment model

Backups need a tested restore procedure, retention, encryption, access controls and a recovery-point/recovery-time objective. Where the deployment has a configured backup destination/disk and supports the SQL backup feature, the command family is `BACKUP TABLE ... TO Disk(...)` and `RESTORE TABLE ... FROM Disk(...)`; the named disk must be configured first and the exact syntax/features checked against the deployed release. A syntax template is:

```sql
BACKUP TABLE analytics.events
TO Disk('backups', 'events_backup_20261019');

-- Restore under a new name for validation; the backup disk must be configured.
RESTORE TABLE analytics.events
AS analytics.events_restore_check
FROM Disk('backups', 'events_backup_20261019');
```

Run a restore drill in a disposable environment and validate row counts and representative aggregates before relying on a backup. Other deployments use a supported backup tool or managed-service backup feature. Replicas alone are not backups. For self-managed deployments, the team owns upgrades, capacity, coordination, disks, monitoring, backup and restore. ClickHouse Cloud can reduce operational burden and provide managed capabilities, but service limits, pricing, networking, security and supported features must be evaluated. The correct choice depends on operational skills and workload requirements, not only query speed.

## 11. Hands-on experiments

> **Benchmark discipline:** No latency or throughput numbers are supplied here because none were measured while authoring this lesson. Record your own results, ClickHouse version, hardware, settings, data volume and concurrency.

### Experiment 1 — Poor versus justified sorting key

**Objective:** demonstrate how sorting-key design affects granule pruning and read volume.

**Prerequisites:** running ClickHouse; enough free disk for the chosen dataset.

Create two tables with the same rows but different sort orders:

```sql
CREATE TABLE analytics.events_poor
(
    tenant String,
    event_date Date,
    user_id UInt64,
    event_time DateTime64(3, 'UTC'),
    revenue Decimal(12, 2)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_time, user_id);

CREATE TABLE analytics.events_good
(
    tenant String,
    event_date Date,
    user_id UInt64,
    event_time DateTime64(3, 'UTC'),
    revenue Decimal(12, 2)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_date)
ORDER BY (tenant, event_date, user_id, event_time);
```

Generate a smoke dataset of one million rows first:

```sql
INSERT INTO analytics.events_poor
SELECT
    if(number % 10 = 0, 'acme', concat('tenant-', toString(number % 1000))),
    toDate('2026-01-01') + toIntervalDay(number % 28),
    number % 100000,
    toDateTime64('2026-01-01 00:00:00', 3, 'UTC')
        + toIntervalSecond(number % 2419200),
    toDecimal64((number % 10000) / 100.0, 2)
FROM numbers(1000000);

INSERT INTO analytics.events_good
SELECT tenant, event_date, user_id, event_time, revenue
FROM analytics.events_poor;
```

The second insert reads the first table and writes the same logical rows into the better-sorted table. Use a deterministic dataset so results are comparable.

Run:

```sql
EXPLAIN indexes = 1
SELECT sum(revenue)
FROM analytics.events_poor
WHERE tenant = 'acme'
  AND event_date >= '2026-01-20';

EXPLAIN indexes = 1
SELECT sum(revenue)
FROM analytics.events_good
WHERE tenant = 'acme'
  AND event_date >= '2026-01-20';
```

Then run each query several times and capture `read_rows`, `read_bytes`, `query_duration_ms` from `system.query_log`. Use equivalent warm/cold-cache conditions and do not compare one warm run with one cold run.

**Expected observation:** the better key should usually permit more effective pruning for this predicate because `tenant` and `event_date` lead the sorting key. This is a hypothesis to test, not a guaranteed speedup; data distribution, part count and cache affect results.

**Scale-up:** after validating correctness and resource usage, recreate/load at 10M, 50M and then 100M rows if disk and time permit. Do not load 100M rows first on a constrained laptop. Use the same deterministic generator, schema, query set, data distribution, server version, resource limits and settings for all comparisons. Record `SELECT version()`, hardware/CPU limits, memory, storage type, cache state, part count and background merge activity alongside every result. Save DDL, scripts and results under `olap_lab/experiments/01_clickhouse/` so the experiment is repeatable. The following ten-query suite meets the module roadmap's workload mix; run the same logical queries against both table layouts, substituting `events_poor` and `events_good` for `events`.

```sql
-- Optional dimension table for the join query; create once before the suite.
CREATE TABLE analytics.tenant_dim
(
    tenant String,
    tier LowCardinality(String)
)
ENGINE = MergeTree
ORDER BY tenant;

INSERT INTO analytics.tenant_dim
SELECT concat('tenant-', toString(number)),
       if(number % 2 = 0, 'pro', 'free')
FROM numbers(1000);
INSERT INTO analytics.tenant_dim VALUES ('acme', 'pro');

-- Q1: filtered count
SELECT count() FROM analytics.events_good WHERE tenant = 'acme';

-- Q2: date-range scan and aggregate
SELECT sum(revenue) FROM analytics.events_good
WHERE tenant = 'acme' AND event_date >= toDate('2026-01-20');

-- Q3: group-by
SELECT tenant, count(), sum(revenue)
FROM analytics.events_good GROUP BY tenant;

-- Q4: top-N
SELECT tenant, sum(revenue) AS revenue
FROM analytics.events_good GROUP BY tenant
ORDER BY revenue DESC LIMIT 20;

-- Q5: distinct count
SELECT uniqExact(user_id) FROM analytics.events_good
WHERE tenant = 'acme' AND event_date >= toDate('2026-01-15');

-- Q6: time series
SELECT toStartOfHour(event_time) AS hour, count(), sum(revenue)
FROM analytics.events_good
WHERE tenant = 'acme' AND event_date >= toDate('2026-01-20')
GROUP BY hour ORDER BY hour;

-- Q7: grouped user analysis
SELECT user_id, count() AS events
FROM analytics.events_good
WHERE tenant = 'acme' AND event_date >= toDate('2026-01-20')
GROUP BY user_id ORDER BY events DESC LIMIT 100;

-- Q8: ordered top-N detail
SELECT event_time, user_id, revenue
FROM analytics.events_good WHERE tenant = 'acme'
ORDER BY event_time DESC LIMIT 100;

-- Q9: join
SELECT d.tier, sum(e.revenue) AS revenue
FROM analytics.events_good AS e
INNER JOIN analytics.tenant_dim AS d USING (tenant)
WHERE e.event_date >= toDate('2026-01-20')
GROUP BY d.tier;

-- Q10: distinct users by day
SELECT event_date, uniqExact(user_id) AS users
FROM analytics.events_good WHERE tenant = 'acme'
GROUP BY event_date ORDER BY event_date;
```

This suite intentionally mixes filters, group-bys, top-N, exact distinct counts, time series and a join. It is a starter workload, not a universal benchmark. Compare result equivalence first; then measure repeated latency, `read_rows`, `read_bytes`, throughput and p50/p95 latency at concurrency 1/10/100. Report p99 only when the number of samples supports a stable tail estimate. Separate cold-cache and warm-cache runs and account for merges/background work. For each query, write a prediction before running it, inspect `EXPLAIN indexes = 1`, and change only one design choice per comparison.

**Cleanup:**

```sql
DROP TABLE analytics.events_poor;
DROP TABLE analytics.events_good;
```

**Diagnostics:** if the plan shows broad reads, inspect key order, date type, partition pruning, data distribution and whether the filter matches the key prefix. If inserts fail, inspect free disk and server logs.

### Experiment 2 — Tiny inserts versus batches

**Objective:** observe part creation and merge pressure.

Create a disposable table:

```sql
CREATE TABLE analytics.insert_test
(
    event_time DateTime64(3, 'UTC'),
    tenant String,
    value UInt64
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(toDate(event_time))
ORDER BY (tenant, event_time);
```

Use a client script to insert small batches (for example, 100 rows per insert) and compare with fewer larger batches (for example, 10,000 rows per insert). Do not create millions of HTTP requests. Python sketch:

```python
from datetime import datetime, timezone
import clickhouse_connect

client = clickhouse_connect.get_client(host="localhost", port=8123, username="default")
base = datetime.now(timezone.utc)

def insert_batches(total_rows: int, batch_size: int) -> None:
    for start in range(0, total_rows, batch_size):
        stop = min(start + batch_size, total_rows)
        rows = [
            (base, "acme", i)
            for i in range(start, stop)
        ]
        client.insert(
            "analytics.insert_test",
            rows,
            column_names=["event_time", "tenant", "value"],
        )

insert_batches(total_rows=100_000, batch_size=100)     # small-batch run
# Drop/recreate table or record baseline, then compare:
# insert_batches(total_rows=100_000, batch_size=10_000) # batched run
client.close()
```

Run the two cases separately and capture elapsed wall-clock time. Inspect parts after each load:

```sql
SELECT partition, count() AS active_parts, sum(rows) AS rows
FROM system.parts
WHERE database = 'analytics' AND table = 'insert_test' AND active
GROUP BY partition;
```

**Expected observation:** small inserts generally create more parts initially and increase merge overhead. Background merges can make the part count decline after the insert phase. Timing varies; report measurements only from your environment.

**Cleanup:** `DROP TABLE analytics.insert_test`.

**Diagnostics:** if the part count does not fall, check `system.merges`, server load, partition count and background-pool settings. Do not use forced merges as the normal remedy for a poor ingestion pattern.

### Experiment 3 — Pre-aggregation with a materialized view

**Objective:** compare raw aggregation with a maintained aggregate table.

Use the `events_for_rollup`, `hourly_rollup` and `events_to_hourly_rollup` definitions in Section 7. Insert representative rows:

```sql
INSERT INTO analytics.events_for_rollup VALUES
    ('2026-01-01 10:00:00.000', 'acme', 1, 10.00),
    ('2026-01-01 10:01:00.000', 'acme', 2, 15.00),
    ('2026-01-01 10:02:00.000', 'acme', 1, 5.00);
```

Compare:

```sql
SELECT toStartOfHour(event_time) AS hour, tenant,
       count() AS events, uniqExact(user_id) AS users, sum(revenue) AS revenue
FROM analytics.events_for_rollup
GROUP BY hour, tenant;

SELECT hour, tenant, countMerge(event_count) AS events,
       uniqMerge(unique_users) AS users, sumMerge(revenue_sum) AS revenue
FROM analytics.hourly_rollup
GROUP BY hour, tenant;
```

**Expected observation:** results should agree for these metrics, although `uniq` is an approximate distinct-count aggregate and may differ from `uniqExact` on larger data. Measure both query time and the additional write/storage cost.

**Cleanup:** drop the view first, then target and source tables. A materialized view does not retroactively populate the target for data inserted before the view existed.

**Diagnostics:** verify target types match the state expressions, use `...Merge` on states, and check that the view targets the intended database/table.

### Experiment 4 — ReplacingMergeTree and `FINAL`

**Objective:** demonstrate eventual deduplication and the query-time cost/semantics of `FINAL`.

Use the `analytics.user_state` table from Section 6. Insert two versions for one user, then query both normally and with `FINAL`:

```sql
SELECT * FROM analytics.user_state WHERE user_id = 7;
SELECT * FROM analytics.user_state FINAL WHERE user_id = 7;
```

The normal query may return both rows until merges consolidate them. `FINAL` should apply replacement semantics to the selected rows, using the version column to select the winning version. Results depend on sorting-key design and version ties; do not assume it is a uniqueness guarantee across arbitrary sharding or all parts.

Inspect parts:

```sql
SELECT name, rows, level, active
FROM system.parts
WHERE database = 'analytics' AND table = 'user_state'
ORDER BY name;
```

For a disposable test table, you may request an explicit merge to observe the post-merge state, but this is a lab operation and not a routine production fix:

```sql
OPTIMIZE TABLE analytics.user_state FINAL;
```

**Cleanup:** `DROP TABLE analytics.user_state`.

**Diagnostics:** ensure the logical identity is the sorting key, a version column is configured when required, and duplicate semantics are explicit in application queries.

### Experiment 5 — Kafka freshness (optional infrastructure)

**Objective:** measure the end-to-end delay from event production to query visibility.

**Prerequisites:** a local Kafka broker and topic, Kafka support enabled in the chosen ClickHouse build, and a Kafka engine table plus materialized view configured according to the official documentation for the exact version.

1. Generate events with a unique ID and producer timestamp.
2. Configure a Kafka engine table to consume the topic.
3. Attach an incremental materialized view that writes events into a MergeTree target.
4. Query recent rows and calculate `now64(3) - produced_at` in milliseconds, accounting for clock synchronization.
5. Record p50/p95 freshness, consumer lag, errors and duplicate behavior under a steady event rate.
6. Repeat with controlled load and after restarting a consumer or ClickHouse.

**Expected observation:** freshness changes with batch sizes, broker load, consumer progress, insert behavior and resource contention. There is no universal latency guarantee.

**Cleanup:** stop the generator and services, then drop the test tables and topic only if it is safe to do so.

**Diagnostics:** verify broker reachability from the ClickHouse container, topic names, credentials, format/schema compatibility, consumer-group state, materialized-view target and server logs. If Kafka is not available, complete the other experiments and document the infrastructure blocker rather than claiming this test ran.

## 12. Troubleshooting guide

| Symptom | Likely causes | Investigation and response |
|---|---|---|
| Queries read too many rows | Poor key order, broad predicates, many small parts, low-selectivity filter | Use `EXPLAIN indexes = 1`, inspect `read_rows`, redesign from query patterns |
| Part count grows continuously | Tiny inserts, high partition cardinality, insufficient merge capacity | Batch inserts, simplify partitioning, inspect `system.parts` and `system.merges` |
| `ReplacingMergeTree` returns duplicates | Merges have not consolidated rows; key/version semantics are wrong | Use explicit query semantics or `FINAL` selectively; verify logical key and version |
| Rollup differs from raw query | Incorrect state merging, view created after historical inserts, updates/deletes not propagated | Use matching `-State`/`-Merge`, backfill, reconcile raw and aggregate tables |
| Memory limit exceeded | Large joins/sorts/aggregations, too much concurrency, weak filters | Reduce scanned columns/rows, inspect plan, review join strategy and resource limits |
| Kafka rows are delayed or missing | Consumer lag, broker connectivity, schema/format errors, MV target issue | Check logs, consumer group, topic, materialized view and target table |
| TTL data remains visible | TTL is asynchronous or policy/column is incorrect | Verify table TTL, mutation/merge progress and retention configuration |
| Inserts fail or become slow | Disk pressure, malformed data, too many parts, merge backlog | Inspect logs, disk, rejected rows, part counts and insert batching |

## 13. Common engineering mistakes

- **Partitioning by a high-cardinality identifier.** This multiplies partitions and parts. Partition by a coarse lifecycle dimension; use sorting keys for pruning.
- **Choosing `ORDER BY` without examining queries.** The key should reflect common filter/order/group patterns and the distribution of values.
- **Inserting one event per request.** Small parts create merge and metadata overhead. Buffer and batch where the freshness contract allows it.
- **Assuming merges happen immediately.** MergeTree engine variants can have eventual behavior. Queries must be correct before background consolidation.
- **Treating `ReplacingMergeTree` as a unique constraint.** It is not transactional uniqueness.
- **Using `FINAL` indiscriminately.** It can be expensive; understand where it is required and benchmark it.
- **Averaging averages or summing distinct counts.** Preserve sufficient statistics or mergeable aggregate states.
- **Expecting materialized views to repair mutations.** Incremental views process inserted blocks; design corrections and backfills explicitly.
- **Adding skipping indexes without measuring.** Indexes that cannot rule out many blocks add write/storage overhead without enough read benefit.
- **Assuming a single benchmark is proof.** Record version, dataset, cache state, concurrency, settings and repeated measurements.
- **Treating replicas as backups.** Deletions and corruption may replicate; test restoration from backups.
- **Assuming all joins are bad.** Evaluate join types, data size, key distribution, algorithms, memory, concurrency and alternatives using real query plans.

## 14. Knowledge checks

Answer without looking back, then verify your reasoning.

1. Why can a columnar engine read less data than a row-oriented engine for an aggregation over two columns?
2. What does vectorized execution change compared with row-at-a-time operator execution?
3. What is a data part? Why do inserts create parts, and what do background merges do?
4. Explain the difference between a sorting key and the sparse primary index.
5. Why is the primary index sparse, and what does a granule represent?
6. When would a shorter `PRIMARY KEY` be useful even if `ORDER BY` has more columns?
7. Why is monthly partitioning often a reasonable starting point, and why is partitioning not automatically a speed optimization?
8. What workload characteristics favor `LowCardinality`, `ZSTD`, `Delta` or `Gorilla`?
9. How do minmax, set and bloom-filter skipping indexes differ?
10. Why can `ReplacingMergeTree` return duplicate versions? What does `FINAL` do and cost?
11. Why must aggregate states be merged instead of summing their final distinct counts?
12. What does an incremental materialized view do with newly inserted blocks? What happens to its target after source mutations?
13. What is the difference between a shard, a replica, a `Distributed` table and a `ReplicatedMergeTree` table?
14. Which metrics and system tables would you inspect for slow queries and a growing part count?
15. How would you measure Kafka end-to-end freshness without confusing it with consumer lag or clock skew?

## 15. Practical checkpoint

Do not move to the next topic until you can:

- [ ] Explain parts, merges, granules and sparse indexes in your own words.
- [ ] Draw how several inserts create parts and how background merges consolidate them.
- [ ] Justify a sorting key and partitioning scheme from a query workload.
- [ ] Use `EXPLAIN indexes = 1` and query logs to compare scanned rows and latency.
- [ ] Explain why small inserts create operational pressure and demonstrate batching.
- [ ] Build a materialized view with aggregate states and reconcile it with raw data.
- [ ] Explain eventual deduplication, `FINAL`, mutations and append-oriented modeling.
- [ ] Describe the distributed, Kafka and object-storage ingestion options at an architectural level.
- [ ] Complete the smoke tests and scale the benchmark toward 100 million rows only when resources allow.
- [ ] Record real measurements and explain them without inventing or overgeneralizing results.

## 16. Revision summary

- **Columnar storage** reduces unnecessary column reads; **vectorized execution** processes blocks efficiently; **parallelism** uses available resources.
- **MergeTree** stores sorted immutable parts and merges them asynchronously.
- **`ORDER BY`** controls physical sort order; **`PRIMARY KEY`** defines a sparse index prefix.
- **Partitioning** is primarily a lifecycle/management decision; avoid excessive partition cardinality.
- **Skipping indexes and projections** are additional optimizations that must be validated by plans and measurements.
- Specialized MergeTree engines change merge/read semantics, not transactional uniqueness.
- Incremental materialized views process inserted blocks; aggregate states must be combined with correct merge functions.
- Use query plans, logs, parts and merge telemetry to diagnose real behavior.
- Production readiness includes ingestion correctness, resource controls, retention, security, backups and tested restores.

## 17. References

Use the documentation matching the version you run; ClickHouse behavior and syntax evolve.

- ClickHouse documentation: https://clickhouse.com/docs/
- MergeTree table engine: https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree
- ReplacingMergeTree: https://clickhouse.com/docs/engines/table-engines/mergetree-family/replacingmergetree
- SummingMergeTree: https://clickhouse.com/docs/engines/table-engines/mergetree-family/summingmergetree
- AggregatingMergeTree: https://clickhouse.com/docs/engines/table-engines/mergetree-family/aggregatingmergetree
- Incremental materialized views: https://clickhouse.com/docs/materialized-view/incremental-materialized-view
- EXPLAIN: https://clickhouse.com/docs/sql-reference/statements/explain
- System tables: https://clickhouse.com/docs/operations/system-tables
- ClickHouse Connect: https://clickhouse.com/docs/integrations/language-clients/python
- Kafka integration: https://clickhouse.com/docs/integrations/kafka
- S3 table function: https://clickhouse.com/docs/sql-reference/table-functions/s3
- S3Queue: https://clickhouse.com/docs/engines/table-engines/integrations/s3queue

> **Verification note:** The complete document was statically reviewed against the project tree and the module roadmap. SQL, Python, shell, Docker Compose and configuration examples were inspected for internal consistency, but no ClickHouse server, Docker runtime, Kafka broker or S3-compatible service was available for execution during this audit. Therefore, the examples are not represented as runtime-tested. The Compose image tag is an explicit lab pin, not a claim that it is the latest release; verify that the tag remains available and validate version-sensitive syntax, JSON support, Kafka/S3Queue settings, authentication, backups and query-plan output against the exact release used in your environment.
