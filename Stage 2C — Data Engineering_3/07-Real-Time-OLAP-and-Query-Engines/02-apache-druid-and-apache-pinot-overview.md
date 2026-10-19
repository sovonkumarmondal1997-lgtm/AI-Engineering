# Apache Druid and Apache Pinot: Architecture, Ingestion, Indexing, and Operations

> **Roadmap location:** `Stage 2C — Data Engineering_3/07-Real-Time-OLAP-and-Query-Engines/02-apache-druid-and-apache-pinot-overview.md`  
> **Prerequisites:** SQL and `EXPLAIN`; columnar storage and partitioning; dimensional modeling; Kafka basics; Docker Compose; familiarity with analytical warehouses.  
> **Scope boundary:** This lesson covers Druid and Pinot, with only the required comparison to ClickHouse. Trino/Presto, StarRocks/Doris, and general engine selection have separate lessons.

## 1. Learning objectives

After completing this lesson, you should be able to:

- Explain why user-facing analytics needs fresh data, low query latency, and predictable performance at high concurrency.
- Model time-series event data using timestamps, dimensions, and metrics.
- Explain time-partitioned segments and how they support storage, distribution, and query execution.
- Trace a Druid request through Brokers and data-serving nodes, and explain the Coordinator, Overlord, Historical, MiddleManager/Indexer, Router, deep storage, and metadata store.
- Trace a Pinot request through Brokers and Servers, and explain Controllers, Minions, real-time/offline/hybrid tables, Helix, and ZooKeeper.
- Select Pinot indexes from query predicates and data characteristics rather than adding every index.
- Explain Druid roll-up, Pinot star-tree pre-aggregation, Pinot upserts, and the effects of late or corrected events.
- Run a small reproducible streaming experiment, measure freshness, and scale the workload carefully.
- Compare Druid and Pinot operationally and contrast both with ClickHouse without assuming benchmark results in advance.

## 2. The real-time OLAP problem

### 2.1 Why a separate serving engine exists

A product dashboard might need to answer “How many active users did this tenant have in the last five minutes?” while new events continue to arrive. Advertising systems need counts, spend and conversion metrics. Observability systems need rapid filtering and aggregation over recent logs or measurements.

The workload often combines:

- **Freshness:** newly produced events should become queryable quickly.
- **Low latency:** interactive queries should complete in milliseconds to sub-seconds for the intended workload.
- **Concurrency:** many users, dashboards or services may query at once.
- **Time-bounded scans:** most queries constrain a time interval.
- **High ingestion throughput:** data keeps arriving while historical data is queried.

These are targets to measure, not guarantees that every deployment will meet them. Results depend on data volume, query shape, indexes, segment layout, hardware, replication, concurrency and ingestion configuration.

### 2.2 Shared mental model: segments

Both Druid and Pinot organize analytical data into **segments**. A segment is a storage and processing unit that can be assigned to nodes, loaded, queried, replicated, replaced or retired. Segment boundaries often align with time intervals, though exact partitioning and segment-building policies differ between engines.

```text
Event producers
      │
      ▼
 Kafka / Kinesis / batch files
      │
      ▼
 ingestion workers and task/consumer state
      │
      ▼
 immutable or mostly immutable time-partitioned segments
      │
      ├── recent/real-time segments
      └── sealed historical/offline segments
                    │
                    ▼
       query routing → selected segments → partial results
                    │
                    ▼
               final result
```

Segments reduce the amount of data a query needs to examine when time and other filters exclude segments. They also make replication, balancing, retention, compaction and failure recovery manageable. Too many tiny segments, however, increase metadata, scheduling and query-planning overhead.

### 2.3 Timestamp, dimensions and metrics

A common event model is:

| Field | Example | Typical role |
|---|---|---|
| `event_time` | `2026-01-10T10:01:02Z` | Time filtering and time partitioning |
| `tenant` | `acme` | Dimension used to filter/group |
| `event_type` | `purchase` | Dimension |
| `country` | `IN` | Dimension |
| `user_id` | `1234` | Dimension or key, depending on engine/schema |
| `revenue` | `29.99` | Numeric metric |
| `event_id` | UUID/string | Deduplication or traceability field if configured |

A **dimension** is commonly used for filtering, grouping or slicing. A **metric** is a value to aggregate, such as sum, count or a statistical measure. This is a modeling convention rather than an absolute type rule: numeric fields can be dimensions, and a dimension can sometimes be aggregated.

The key design question is which details must remain available at query time. If ingestion aggregates away `event_id` or `user_id`, event-level troubleshooting or distinct-user calculations may become impossible or approximate.

## 3. Apache Druid architecture

### 3.1 Components and responsibilities

Druid is a distributed analytics datastore built around time-partitioned segments, ingestion tasks and query-serving nodes. Roles can be deployed together in small environments or separated across services in production.

| Component | Responsibility | Engineering note |
|---|---|---|
| **Broker** | Receives queries, determines which segments/nodes are relevant, fans out work and merges results | Query-serving scale and latency depend on query fan-out, result merging and available segments |
| **Historical** | Loads and serves immutable historical segments from local cache/storage after segment assignment | Historical nodes are data-serving nodes; deep storage is the durable segment store |
| **Coordinator** | Manages segment availability and balancing across Historical nodes; coordinates rules and placement | It controls distribution, not the SQL query itself |
| **Overlord** | Schedules and manages ingestion tasks | Supervisors for streaming ingestion coordinate task lifecycle |
| **MiddleManager / Indexer** | Executes ingestion tasks; Indexer is the newer task-execution service in deployments using that architecture | Exact process topology depends on the Druid release and deployment mode |
| **Router** | Optional entry point that routes requests to Brokers, Overlords or Coordinators | Useful for a single endpoint and routing policies; not mandatory in every deployment |
| **Deep storage** | Durable storage for published segments, such as S3-compatible object storage or HDFS | Published segments can be reloaded after node loss; deep storage is not the query-serving cache |
| **Metadata store** | Stores Druid metadata such as segment and task-related records, depending on the version/configuration | Commonly an external relational database in production; it is distinct from deep storage |
| **ZooKeeper (deployment-dependent)** | Coordination/discovery for deployments that use it | Check the selected Druid version and deployment architecture rather than assuming every modern setup has identical coordination dependencies |

### 3.2 Druid query path

```text
SQL client / application
          │
          ▼
    Router (optional)
          │
          ▼
        Broker
          │ reads metadata / segment locations
          ├──────────────┐
          ▼              ▼
    Historical A    Historical B
    segments X,Y    segments Z
          │              │
          └──── partial results ────┐
                                    ▼
                            Broker merges results
                                    │
                                    ▼
                               query result
```

Recent streaming data may be served by ingestion tasks holding real-time data, depending on the ingestion and publication state. As data is published into segments, the Coordinator and serving nodes manage its historical availability. The exact query path for a particular interval depends on segment state, ingestion mode and Druid version.

**Why it matters:** a query can be slow even when the underlying scan is efficient if it fans out to many small segments or many nodes, has to merge large intermediate results, or competes with ingestion tasks for resources.

### 3.3 Query interfaces: Druid SQL and native JSON

Druid exposes **Druid SQL** over its SQL HTTP API and a lower-level **native query API** using JSON. SQL is convenient for common analytical work; native query types (such as `timeseries`, `topN`, `groupBy` and `scan`) expose Druid-specific query shapes. Native queries are not SQL embedded in JSON: they have their own query-type-specific schema.

After ingestion maps the source timestamp to Druid's `__time`, a bounded SQL example is:

```sql
SELECT
  TIME_FLOOR("__time", 'PT1H') AS hour,
  country,
  SUM(impressions) AS impressions,
  SUM(clicks) AS clicks
FROM ad_impressions
WHERE "__time" >= TIMESTAMP '2026-01-10 00:00:00'
  AND "__time" <  TIMESTAMP '2026-01-11 00:00:00'
GROUP BY 1, country
ORDER BY impressions DESC
LIMIT 20;
```

The SQL timestamp literals above are interpreted using the query context's timezone (UTC is recommended for this lab). This query assumes `country`, `impressions`, and `clicks` exist in the ingested datasource. It is an example to validate against the selected Druid release, not a claim that the lab cluster was started.

A minimal native timeseries query for the same datasource is:

```json
{
  "queryType": "timeseries",
  "dataSource": "ad_impressions",
  "intervals": ["2026-01-10T00:00:00.000Z/2026-01-11T00:00:00.000Z"],
  "granularity": "hour",
  "aggregations": [
    {"type": "longSum", "name": "impressions", "fieldName": "impressions"},
    {"type": "longSum", "name": "clicks", "fieldName": "clicks"}
  ],
  "descending": false
}
```

Submit native JSON to the queryable Broker/Router endpoint, commonly `POST /druid/v2/`, with `Content-Type: application/json`. Confirm the endpoint and accepted query fields for the selected release.

### 3.4 Druid ingestion: streaming and batch

Druid supports batch ingestion from files/object storage and streaming ingestion from systems such as Kafka and Kinesis. Streaming ingestion commonly uses a **supervisor** to coordinate tasks, track offsets and manage task replacement. Tasks consume events, build segments, and publish segments according to ingestion configuration.

```text
Kafka topic
    │
    ▼
Supervisor → ingestion tasks → intermediate segments
                                  │ publish
                                  ▼
                           deep storage
                                  │
                         segment metadata/assignment
                                  ▼
                              Historicals
```

Batch ingestion is appropriate for historical backfills, file-based imports and reprocessing. Streaming ingestion is appropriate for continuously arriving events with a freshness requirement. A hybrid operational model is common: streaming for current data and batch/reindexing for historical correction.

### 3.5 Druid schema and roll-up

A simplified Druid ingestion specification for a Kafka source typically defines the input topic and consumer settings, timestamp extraction, dimensions, metrics, segment granularity, query granularity, and roll-up behavior. The exact JSON schema is version-sensitive, so use the documentation matching the Druid image rather than copying an old spec into a newer release. The following Kafka supervisor spec is a concrete **starting example** for the event fields used in this lesson; it assumes the Kafka indexing extension is installed on the relevant Druid services, the topic `ad-impressions` exists, and `kafka:9092` is reachable from Druid. Match these values to the Docker network and validate the spec with the target Druid release before posting it to the Overlord supervisor API.

```json
{
  "type": "kafka",
  "spec": {
    "dataSchema": {
      "dataSource": "ad_impressions",
      "timestampSpec": {"column": "event_time", "format": "iso"},
      "dimensionsSpec": {
        "dimensions": ["event_id", "tenant", "campaign", "country", "device"]
      },
      "metricsSpec": [
        {"type": "longSum", "name": "impressions", "fieldName": "impressions"},
        {"type": "longSum", "name": "clicks", "fieldName": "clicks"},
        {"type": "doubleSum", "name": "spend", "fieldName": "spend"}
      ],
      "granularitySpec": {
        "type": "uniform",
        "segmentGranularity": "HOUR",
        "queryGranularity": "NONE",
        "rollup": false
      }
    },
    "ioConfig": {
      "topic": "ad-impressions",
      "inputFormat": {"type": "json"},
      "consumerProperties": {"bootstrap.servers": "kafka:9092"},
      "taskCount": 1,
      "replicas": 1,
      "taskDuration": "PT1H"
    },
    "tuningConfig": {
      "type": "kafka",
      "maxRowsPerSegment": 500000
    }
  }
}
```

This example disables roll-up to preserve event-level rows for baseline correctness checks. Change the topic, bootstrap address, task count, segment policy and roll-up settings deliberately; do not assume these sample resource values are production recommendations. Druid maps the source timestamp to `__time` for query purposes.

Conceptual schema:

```text
Datasource: ad_impressions
  timestamp: event_time
  dimensions: tenant, campaign, country, device
  metrics: impressions, clicks, spend
  segmentGranularity: HOUR or DAY
  queryGranularity: MINUTE (example)
  rollup: enabled or disabled by design
```

- **Segment granularity** controls the time interval used to group data into segments.
- **Query granularity** controls the timestamp grain represented in stored/queryable rows when roll-up is used.
- **Roll-up** combines events with matching dimension values and the timestamp after `queryGranularity` truncation into aggregate rows. In Druid, roll-up is enabled by default unless explicitly disabled in the `granularitySpec`.

Suppose raw events contain `event_id`, `user_id`, campaign, country and a millisecond timestamp. If ingestion rolls up by minute, campaign and country, it can reduce row count significantly. But if `user_id` and `event_id` are not retained in the grouping dimensions, the result no longer supports exact event-level inspection or arbitrary exact user-level distinct counts. Roll-up is a business decision about which questions must remain answerable, not just a performance toggle. Preserve additive metrics (for example `SUM(spend)` and a suitable event-count metric); an average generally needs a mergeable sum/count representation rather than an average of averages.

**Important streaming nuance:** Druid Kafka/Kinesis ingestion uses best-effort roll-up because streaming segments can be published incrementally. Rows with the same dimensions and query-granularity timestamp can therefore remain in separate segments; do not assume global perfect aggregation across the datasource. Batch ingestion methods and compaction configurations have different guarantees. Measure the roll-up ratio and verify aggregates against the raw source. A later compaction can consolidate/rewrite data only according to its configured input and aggregation semantics; it is not a general CDC update mechanism.

Druid metrics need suitable aggregators. For example, sum of spend and count of impressions are additive. Average latency should usually preserve sum and count (or an appropriate mergeable representation), not average already-averaged values without weights.

### 3.6 Druid updates, late events and compaction

Druid's segment-oriented model is not a conventional mutable-row store. Correcting historical source records usually requires reingesting/reindexing the affected interval and publishing replacement segments. Compaction is primarily a segment rewrite/maintenance workflow: by default it does not change the underlying data, though configured compaction can change granularity, dimensions, metrics or roll-up. Compaction alone does not discover a changed source record and is not equivalent to a CDC update. Verify overshadowing/replacement and query correctness after the workflow.

Late events may be accepted by streaming ingestion depending on task configuration and offsets, but their eventual representation and roll-up effects depend on ingestion semantics. If a late event lands in an already aggregated time bucket, it can contribute to that bucket only if the ingestion and segment replacement path correctly processes it. Do not assume that changing source data automatically rewrites previously published aggregate segments.

**Use when:** time-partitioned analytics, high-throughput ingestion, and predictable time-based queries fit the data model.

**Be cautious when:** frequent row-by-row corrections, complex transaction semantics or arbitrary join-heavy exploration dominate the workload.

## 4. Apache Pinot architecture

### 4.1 Components and responsibilities

Pinot is a distributed real-time OLAP datastore designed for low-latency, high-concurrency queries. Its storage and query units are segments; tables can combine real-time and offline segments.

| Component | Responsibility | Engineering note |
|---|---|---|
| **Controller** | Manages table/schema metadata, segment lifecycle, assignments and cluster administration | It is the control plane, not the query fan-out layer |
| **Broker** | Accepts queries, selects relevant servers/segments, distributes work and combines results | Broker count, query fan-out and response merging affect latency |
| **Server** | Hosts and serves table segments; may host real-time consuming segments and offline segments | Server CPU, memory, segment count and replication affect throughput |
| **Minion** | Runs background tasks such as segment conversion, merge/roll-up or other configured maintenance tasks | Not the ordinary SQL query execution path |
| **Helix** | Cluster management and state/assignment coordination used in Pinot's architecture | Manages distributed cluster state and resource assignment |
| **ZooKeeper** | Coordination metadata used by the Helix-based architecture in standard deployments | Operational dependency and failure domain to understand |
| **Deep/object storage (deployment-dependent)** | Stores segment artifacts for download/recovery where configured | Server-local segment copies are not a replacement for durable storage |

### 4.2 Pinot query path

```text
Application / SQL client
          │
          ▼
        Broker
          │ consult table/segment routing
          ├──────────────┐
          ▼              ▼
       Server A       Server B
    segments 1,2     segments 3,4
          │              │
          └── partial aggregates/rows ──┐
                                        ▼
                                Broker combines results
                                        │
                                        ▼
                                   query response
```

The Controller maintains metadata and coordinates segment lifecycle, but the Broker and Servers are the main query path. A Broker uses routing metadata to identify servers holding the relevant segments. If a server is down, routing and replication determine whether the query can still be served and whether latency or completeness changes.

### 4.3 Real-time, offline and hybrid tables

- **Real-time table:** consumes streaming data, often from Kafka, into segments that are available for queries as ingestion progresses.
- **Offline table:** serves segments built from batch ingestion or completed historical data.
- **Hybrid table:** exposes real-time and offline portions as one logical table, typically partitioned by time so the same logical interval is not incorrectly served twice.

A hybrid table is useful when recent data is streamed while older history is batch-loaded. The cutoff and segment assignment must be managed carefully. Overlapping time ranges, missing handoffs, duplicate records or incorrect table configuration can cause double-counting or gaps.

### 4.4 Pinot SQL: single-stage and multi-stage engines

Pinot SQL supports common filtering, grouping, aggregation and top-N analytics. The **single-stage engine (SSE)** is the usual lower-overhead path for scatter-gather queries over segments. The **multi-stage engine (MSE)** supports broader distributed relational plans, including joins, subqueries/CTEs and window operations, but introduces exchange, intermediate-state and memory costs. Enable MSE using the supported query option for the version in use (commonly `useMultistageEngine=true`) or the corresponding client/API setting; do not assume a join automatically runs on SSE.

A simple Pinot query using the example schema is:

```sql
SELECT
  country,
  campaign,
  SUM(impressions) AS impressions,
  SUM(clicks) AS clicks
FROM ad_impressions
GROUP BY country, campaign
ORDER BY impressions DESC
LIMIT 20
```

A join example must use MSE and should keep the right/build-side relation small enough for the selected plan and memory budget:

```sql
-- Run with the Pinot multi-stage query engine enabled.
SELECT e.country, d.campaign_name, SUM(e.impressions) AS impressions
FROM ad_impressions AS e
JOIN campaign_dimension AS d
  ON e.campaign = d.campaign_id
GROUP BY e.country, d.campaign_name
ORDER BY impressions DESC
LIMIT 20
```

The join example is illustrative and requires a separately ingested `campaign_dimension` table with the shown columns. MSE is not a substitute for an unrestricted ETL engine: large unbounded joins/intermediate results can exhaust memory, and join order/data distribution should be inspected with `EXPLAIN` and runtime statistics. SQL support, null behavior, supported join forms and query options vary by Pinot release. Validate every production query against the exact release.

### 4.5 Pinot schema and table configuration

Pinot separates a **schema** (column definitions, primary key and field roles) from **table configuration** (table type, ingestion stream settings, replication, indexing configuration, routing and retention). Configuration formats and property names are version-sensitive.

Example logical schema for ad impressions:

```json
{
  "schemaName": "ad_impressions",
  "dimensionFieldSpecs": [
    {"name": "tenant", "dataType": "STRING"},
    {"name": "campaign", "dataType": "STRING"},
    {"name": "country", "dataType": "STRING"},
    {"name": "device", "dataType": "STRING"}
  ],
  "metricFieldSpecs": [
    {"name": "impressions", "dataType": "LONG"},
    {"name": "clicks", "dataType": "LONG"},
    {"name": "spend", "dataType": "DOUBLE"}
  ],
  "dateTimeFieldSpecs": [
    {
      "name": "event_time",
      "dataType": "TIMESTAMP",
      "format": "1:MILLISECONDS:EPOCH",
      "granularity": "1:MILLISECONDS"
    }
  ]
}
```

This is a schema illustration, not a complete deployable schema for every Pinot release. For a working lab, use the schema/table examples from the selected official quickstart and add fields while preserving that release's expected field specification syntax. For upserts, define the primary-key fields in the supported schema form and configure the table's upsert mode and comparison/ordering behavior as required by that release.

## 5. Segments, indexing and data modeling

### 5.1 Segment lifecycle

A simplified lifecycle:

1. Data is consumed from a stream or loaded in a batch.
2. An ingestion task/consumer builds a segment for a partition and time range.
3. The segment is sealed/published or otherwise made queryable according to engine semantics.
4. Metadata and routing state make it available to query-serving nodes.
5. Segments are replicated, balanced, compacted/replaced or retired according to policies.
6. Retention removes data when it is no longer needed.

Segment size is a balance. Tiny segments make planning, scheduling, metadata and file-open overhead worse; extremely large segments can slow recovery, compaction and rebalancing and may be awkward for parallelism. Use representative data and monitor actual segment sizes, not a universal magic number.

### 5.2 Pinot indexes: choose from the query pattern

Indexes consume disk and may increase ingestion/segment-build time. Their value depends on predicates, cardinality, data distribution and query mix. Add indexes to answer a measured query problem.

| Index | What it does | Useful when | Limitations |
|---|---|---|---|
| **Sorted** | Stores rows sorted by a chosen column in a segment; can support efficient filtering/processing on that column | A dominant filter/sort dimension has useful ordering locality | Sorting choices compete; not every predicate benefits, and sorted-column configuration is not equivalent to a general secondary index |
| **Inverted** | Maps values to matching document/row IDs; Pinot's bitmap inverted index is the common unsorted-column form | Selective equality/`IN` predicates and categorical filters | High-cardinality or broad matches can cost space; dictionary encoding and index configuration matter |
| **Range** | Maps value ranges to matching document IDs | Predicates such as `price BETWEEN ...` or numeric thresholds, especially high-cardinality metrics | Additional storage/build cost; effectiveness depends on range and data distribution |
| **Bitmap** | In Pinot, usually means the bitmap inverted-index representation, not a wholly independent index family in every version | Filtering and combining predicates on values | Treat as a subtype/implementation of inverted indexing; consult the version's index taxonomy rather than counting it as an unrelated index |
| **Text** | Builds searchable structures for text predicates such as token/term search | Search over message, description or log text | Tokenization, supported operators, index size and ingestion overhead matter; not a full replacement for a dedicated search system in every use case |
| **JSON** | Indexes or accelerates access to selected paths/keys in JSON columns, depending on Pinot version and configuration | Semi-structured event attributes where a subset of paths is queried often | Path cardinality, schema variability and index configuration can increase cost; frequently used fields may be better modeled as typed columns |
| **Star-tree** | Pre-aggregates selected dimension combinations and metrics in a segment to answer supported aggregation queries with less raw scanning | Repeated dashboard group-bys over selected dimensions and metrics | Adds storage and segment-build cost; only helps query shapes compatible with the configured dimensions/aggregations; combinatorial growth must be controlled |

**Index design workflow**

1. List the top dashboard queries and their predicates, group-by columns, time ranges and sort/top-N behavior.
2. Measure baseline latency and query plans/metrics.
3. Inspect cardinality, selectivity, segment distribution and ingest throughput.
4. Add one relevant index or star-tree configuration at a time.
5. Apply the configuration and rebuild/reload the affected segments when required by that index and Pinot version. Some indexes are generated during segment creation; others may be added on reload, and not every index can be retrofitted to every existing segment.
6. Compare latency percentiles, bytes/rows processed where exposed, segment size, ingestion time and CPU.
7. Keep the index only if end-to-end value exceeds storage and write cost.

### 5.3 Star-tree pre-aggregation

Suppose the common query is:

```sql
SELECT country, device, SUM(impressions), SUM(clicks)
FROM ad_impressions
WHERE event_time >= <recent_time_boundary>
GROUP BY country, device;
```

A star-tree can store aggregates for selected dimension combinations, letting compatible queries use precomputed values rather than scan all raw rows. The exact syntax and configuration live in Pinot's table index configuration and vary across releases.

Choose dimensions with frequent query use and controlled cardinality. Including high-cardinality identifiers such as `event_id` can destroy the benefit by creating a huge number of combinations. Star-tree is not a general materialized view that can answer every arbitrary aggregation.

## 6. Ingestion correctness and freshness

### 6.1 Measure freshness separately from ingestion lag

**End-to-end freshness** is the difference between the event's production timestamp and the time it becomes queryable. **Ingestion lag** describes progress behind the source stream (for example, consumer offsets or time lag). They are related but not identical: a consumer can be caught up while segment publication/query visibility adds delay.

For meaningful measurement:

- Include a producer timestamp and unique event ID.
- Keep producer and query host clocks synchronized, or measure with a single clock/source where possible.
- Record event creation time, stream offset/partition where available, and first query-visible time.
- Report p50/p95/p99 freshness and ingestion lag over a sustained interval.
- Track duplicates, missing IDs, rejected rows and late arrivals.

### 6.2 Druid roll-up and correction handling

Druid ingestion-time roll-up reduces storage and query work by combining events with the same time bucket and dimension set. It loses details not represented by those dimensions or retained metrics. Decide which questions must be supported before enabling it.

Late data and corrections require an explicit path. Depending on the pipeline, options include reingestion/reindexing, replacing affected segments or compaction/rebuild workflows. Verify the resulting aggregates against raw event history. A source-system correction does not magically update an already published Druid segment.

### 6.3 Pinot upserts and partial upserts

Pinot supports upsert configurations that use a primary key to represent the latest state of a logical record under configured ordering/version semantics. Partial upserts can update only selected fields rather than requiring every incoming record to contain a complete replacement row, but they require a well-defined comparison column, field-level update strategy and supported table configuration.

Important limits:

- Primary-key semantics are configured behavior, not a blanket promise of OLTP transactions across arbitrary operations.
- Ordering/version choice determines which record wins; equal or missing versions require explicit handling.
- Partial updates can interact with null/missing values differently depending on strategy and version.
- Upsert metadata consumes resources; deduplication and delete semantics must be tested.
- Replaying events, out-of-order updates and stream retries need idempotency and reconciliation tests.

Use upserts when the query model is “latest state per key” and the table/configuration supports the required semantics. For immutable event analytics, append-only event rows are often simpler.

### 6.4 Duplicate handling

At-least-once delivery can create duplicates. Define whether duplicates are rejected, tolerated, deduplicated by key, or corrected in aggregates. A UUID field alone does not deduplicate anything. Test retries and replay explicitly. Do not compare totals across engines unless both receive equivalent data and apply the same duplicate policy.

## 7. Joins, subqueries and query-shape limits

Do not summarize either engine as “cannot join.” Both can support joins, but their execution models and intended sweet spots differ from a general-purpose warehouse.

- **Druid:** Druid SQL supports joins in supported forms, including broadcast-style joins with lookup/dimension data; join planning, join algorithm and right-side size matter. Large fact-to-fact joins and unrestricted relational subqueries are not the default low-latency sweet spot. Native query types are more specialized and are not a general SQL relational algebra. For large distributed ETL joins, use a warehouse/lakehouse engine or pre-join/denormalize upstream when appropriate.
- **Pinot SSE:** optimized for scatter-gather filters, aggregations and top-N, with more limited relational planning.
- **Pinot MSE:** broadens join, subquery/CTE and window-function support, but has additional distributed-stage overhead and memory constraints; large intermediate results may fail rather than spill like a batch engine.

For every join/subquery workload, validate supported syntax and null semantics on the exact version, inspect the explain plan, measure p95/p99 under concurrency, and size the build side/intermediate results. If query requirements are mostly ad hoc multi-table exploration, compare a warehouse or Trino rather than assuming a serving OLAP engine is the right fit.

## 8. Operations, scaling and resilience

### 8.1 Segment sizing, compaction, retention and tiering

- **Segment sizing:** avoid many tiny segments; set ingestion/batch parameters and monitor resulting segment size/count.
- **Compaction:** rewrites or merges segments to improve layout, reduce segment count or apply new ingestion/roll-up choices. It consumes CPU, I/O and temporary disk.
- **Retention:** define a policy by business, privacy and cost requirements. Verify which component enforces it and whether removal is asynchronous.
- **Tiering:** keep recent/hot data on faster resources and older data on cheaper storage/nodes where supported by deployment.
- **Replication:** retain multiple copies of segments to tolerate node failures and distribute read load, trading storage and network cost for resilience. A configured replica count is not proof of availability: verify placement across failure domains, segment assignment, routing behavior, and whether all query-relevant segments have a serving replica.

Retention and tiering mechanisms differ by engine and release. Treat sample configuration as version-specific and verify it against the chosen deployment's docs.

### 8.2 Failure behavior

**Druid:** a Historical node failure may temporarily make assigned segments unavailable until they are reloaded or reassigned; replication and segment placement determine whether another node can serve them. Deep storage is important for recovering published segments. Broker availability and ingestion-task health are separate concerns.

**Pinot:** a Server failure removes some segment replicas from service. Brokers route using cluster metadata; adequate replication and healthy routing can preserve query availability. Controller/Helix/ZooKeeper control-plane issues can affect assignment and state changes even when existing segments remain on Servers. Streaming consumption and query serving should be monitored independently.

Never test failure behavior against a shared or production cluster without an approved plan. In a local lab, stop one node only after confirming there is another replica or that the expected temporary unavailability is acceptable.

### 8.3 Scaling dimensions

**Druid**
- Scale Brokers when query fan-out, merge work or query concurrency is the bottleneck.
- Scale Historicals when historical scan CPU, memory, disk throughput or segment capacity is the bottleneck.
- Scale ingestion task capacity/Indexer or MiddleManager resources when stream processing, segment creation or backfills lag.
- Ensure deep storage, metadata store and coordination services are sized and monitored.

**Pinot**
- Scale Brokers for query routing and result merge pressure.
- Scale Servers for segment hosting, scan/aggregation CPU, memory and replica capacity.
- Scale ingestion/Controller/Minion capacity for segment creation, administration and background tasks as the workload requires.
- Watch Helix/ZooKeeper/control-plane health as well as query-path health.

Adding nodes is not a substitute for finding the bottleneck. Measure query latency percentiles, request rate, errors, CPU, memory, disk, segment counts/sizes, ingestion lag, rejected events and background task queues.

### 8.4 Cost and managed services

Always-on low-latency systems need capacity even during quiet periods. Costs include compute, memory, local SSD, durable storage, replicas, network transfer, Kafka, monitoring, backups, engineering time and upgrade work.

Managed offerings can reduce day-to-day cluster operations:
- **Imply** provides managed/commercial offerings around Apache Druid.
- **StarTree** provides managed/commercial offerings around Apache Pinot.

Product names, capabilities, regions, pricing and service availability change; verify current vendor documentation and contracts before making a procurement decision. Druid and Pinot component topologies also differ by release and deployment mode; do not infer a fixed production topology from a single-node quickstart. A managed service is attractive when faster delivery and reduced on-call burden outweigh service fees and constraints. Self-hosting can be appropriate when operational expertise, control, deployment requirements and cost justify the ownership burden.

## 9. Druid versus Pinot

| Dimension | Apache Druid | Apache Pinot |
|---|---|---|
| Core model | Time-partitioned segments with ingestion tasks and Historical serving | Time/partition-oriented segments with real-time and offline tables |
| Control plane | Coordinator and Overlord among the principal roles | Controller with Helix/ZooKeeper-based cluster coordination |
| Query path | Broker fans out to segment-serving nodes and merges results | Broker routes to Servers and combines partial results |
| Streaming ingestion | Kafka/Kinesis ingestion with supervisors and tasks | Real-time tables commonly consume Kafka through Pinot's stream ingestion |
| Historical ingestion | Batch ingestion and segment publication | Offline table ingestion and segment assignment |
| Pre-aggregation | Ingestion-time roll-up using time/dimension/metric configuration | Star-tree indexes can pre-aggregate selected dimension combinations |
| Corrections | Often reingestion/reindexing/compaction and segment replacement | Upsert/partial-upsert options for supported latest-state models; segment rebuilds remain relevant |
| Indexing emphasis | Time/segment pruning and Druid's segment/column/index structures | Rich selectable indexes including inverted, range, text, JSON and star-tree |
| SQL | Druid SQL and native JSON query APIs | Pinot SQL with single-stage and multi-stage engine options |
| Operational focus | Ingestion task lifecycle, deep storage, metadata, segment assignment and Historical capacity | Server/segment assignment, Broker routing, stream consumption, Controller and Helix/ZooKeeper health |
| Main caution | Roll-up and segment-oriented correction semantics require care | Index and upsert configuration can add storage and operational complexity |

Neither engine wins every workload. The correct choice depends on query mix, data shape, ingestion semantics, freshness objective, required corrections, operational maturity and cost.

## 10. Focused comparison with ClickHouse

The roadmap asks for a practical comparison, not a claim that one engine is universally faster.

| Workload concern | Druid | Pinot | ClickHouse |
|---|---|---|---|
| Primary storage/query model | Time-partitioned segments and distributed Brokers/Historicals | Segments, Brokers and Servers; real-time/offline/hybrid tables | Sorted columnar MergeTree parts and a vectorized SQL execution engine |
| Speed lever emphasized here | Segment pruning and optional ingestion-time roll-up | Index-based pruning and optional star-tree pre-aggregation | Sorting-key pruning, columnar scans, compression, parallel execution and optional pre-aggregation |
| Streaming integration | Kafka/Kinesis ingestion tasks | Real-time table ingestion, commonly Kafka | Kafka engine, managed ingestion options and other integrations |
| Corrections | Reingestion/compaction/segment replacement patterns | Upserts for configured latest-state use cases; segment maintenance | Append-oriented MergeTree patterns, specialized engines, mutations and materialized views |
| Join-heavy exploration | Evaluate limits and query shape | Single-stage limitations; multi-stage engine broadens supported plans but must be tested | Joins are supported; performance depends on layout, algorithms, data volume and memory |
| Operational complexity | Multiple task, query, storage and metadata components | Broker/Server/Controller/Minion plus coordination and ingestion components | Self-managed cluster complexity or managed service responsibilities |

The roadmap's contrast can be summarized as **Druid ingest-time roll-up**, **Pinot index-based pruning/star-tree**, and **ClickHouse raw analytical scans plus sorting-key pruning and columnar execution**. This is an emphasis, not an exclusive feature list: each engine has more than one optimization strategy.

To compare fairly, use the same event set, equivalent duplicate policy, equivalent freshness requirements, and the same query mix. Record data size, ingest throughput, p50/p95/p99 latency, throughput at concurrency, resource use and operational cost. Do not compare a pre-aggregated Druid table with raw ClickHouse data and call the result a database benchmark.

## 11. Hands-on lab: `experiments/02_druid_pinot/`

### 11.1 Lab plan and safe scale

The roadmap allows choosing **Pinot or Druid** for the core lab. Start with one engine, then add the other only when the first experiment is reproducible.

Suggested directory:

```text
experiments/02_druid_pinot/
├── README.md
├── docker-compose.yml              # use official version-matched quickstart
├── generator/
│   └── events.py
├── data/
│   └── sample-events.jsonl
├── config/
│   ├── pinot-schema.json            # if choosing Pinot
│   ├── pinot-table-config.json
│   └── druid-kafka-spec.json        # if choosing Druid
├── queries/
│   └── dashboard-queries.sql
├── bench/
│   └── load_test.py
└── results/
    ├── baseline.csv
    └── indexed-or-rollup.csv
```

Start with 10,000–100,000 generated events to validate schema, stream ingestion and query correctness. Scale to one million, then ten million, then larger volumes only when disk, CPU and memory allow. A 100-client concurrency run is a target experiment, not a requirement to overload a laptop. If the machine cannot support it, record the limitation and run lower concurrency.

### 11.2 Generate events

A simple generator can write newline-delimited JSON for inspection or batch loading. For streaming, publish the same logical fields to the Kafka topic using your chosen Kafka client. Keep event IDs deterministic for duplicate tests and include an event creation timestamp.

Example event:

```json
{"event_id":"evt-000001","event_time":"2026-01-10T10:01:02.000Z","tenant":"acme","campaign":"winter","country":"IN","device":"mobile","impressions":1,"clicks":0,"spend":0.02}
```

A minimal Python generator for local JSONL:

```python
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

out = Path("data/sample-events.jsonl")
out.parent.mkdir(parents=True, exist_ok=True)
start = datetime(2026, 1, 10, tzinfo=timezone.utc)

with out.open("w", encoding="utf-8") as f:
    for i in range(100_000):
        event_time = start + timedelta(milliseconds=i * 100)
        row = {
            "event_id": f"evt-{i:08d}",
            "event_time": event_time.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "tenant": f"tenant-{i % 10}",
            "campaign": f"campaign-{i % 100}",
            "country": ["IN", "US", "GB", "DE"][i % 4],
            "device": ["mobile", "desktop", "tablet"][i % 3],
            "impressions": 1,
            "clicks": 1 if i % 20 == 0 else 0,
            "spend": 0.02 if i % 20 == 0 else 0.0,
        }
        f.write(json.dumps(row) + "\n")
print(f"Wrote {out}")
```

This creates deterministic sample data but does not publish to Kafka. Use a Kafka producer for the streaming step; configure broker and topic from environment variables rather than embedding credentials. The sample data timestamp is intentionally fixed for reproducibility, so for freshness measurements generate current timestamps and synchronize clocks.

### 11.3 Choose one engine and start it

**Important reproducibility rule:** Druid and Pinot quickstart Docker Compose files and ingestion schemas change across releases. Use the official quickstart for the exact version you intend to study, pin image tags, and preserve the compose file and configuration in your lab repository. Do not mix a current server image with an old sample ingestion spec.

Official starting points:
- Druid: https://druid.apache.org/docs/latest/tutorials/
- Pinot: https://docs.pinot.apache.org/getting-started/quick-start

Follow the chosen quickstart to start the full local service set and Kafka integration. Verify health before ingestion. For a Druid path, configure a Kafka supervisor/spec for a datasource named `ad_impressions`; for a Pinot path, create a schema and a real-time table configuration whose stream points to the Kafka topic. The exact POST endpoints, config fields and table creation workflow must match the selected release's official example.

**Smoke-test acceptance criteria:**
1. The UI/API reports the expected services healthy.
2. The schema/table or datasource exists.
3. The stream consumer is assigned to the expected topic/partition.
4. A known test event is eventually visible through a query.
5. The event ID or a controlled count proves that the event was not silently dropped.

Do not claim the quickstart passed unless you run it in your own environment.

### 11.4 Query while the generator runs

Use a simple dashboard query: counts and clicks grouped by campaign/country over a bounded time window. Query syntax differs slightly between Druid SQL and Pinot SQL, so adapt the timestamp functions and time filters to the engine/version.

Conceptual SQL:

```sql
SELECT
    country,
    campaign,
    SUM(impressions) AS impressions,
    SUM(clicks) AS clicks,
    SUM(spend) AS spend
FROM ad_impressions
WHERE event_time >= <start_time>
GROUP BY country, campaign
ORDER BY impressions DESC
LIMIT 20;
```

The `<start_time>` token is a placeholder, not literal SQL. Replace it with a valid timestamp literal or parameter for the selected engine. First run a count query and confirm the time range includes the generated events. For Druid, check the datasource and SQL API; for Pinot, check the table name and SQL endpoint supported by the selected quickstart.

### 11.5 Measure freshness and lag

For each test event, record:
- producer timestamp (`produced_at`);
- event ID and Kafka partition/offset if available;
- first observed query time (`first_visible_at`);
- consumer lag/offset progress where exposed by the engine and Kafka;
- whether the event was missing or duplicated.

Calculate:

\[
\text{freshness\_ms} = \text{first\_visible\_at} - \text{produced\_at}
\]

Report p50, p95 and p99 over a sustained period. This formula assumes clock agreement; if clocks differ, measured freshness includes clock skew. In a local experiment, document the limitation.

Compare at least two settings/conditions, such as small versus larger producer batches or baseline versus indexed/rolled-up ingestion. Change one variable at a time.

### 11.6 Add an index or roll-up and compare

**Pinot branch:** choose one high-value predicate (for example `country = 'IN'`) and one range predicate on a numeric field. Add a suitable inverted index and range index using the version-matched table index configuration. For a repeated grouped aggregate, consider a star-tree configured for the exact dimensions and metrics in that query. Rebuild/reload segments if the selected index change requires it.

**Druid branch:** configure ingestion-time roll-up with a time bucket and dimensions that match the dashboard query. Keep a raw/unrolled baseline if the use case needs event-level detail. Reingest the same deterministic input into a separate datasource or test environment to avoid comparing unlike data.

Run the same query set before and after:
- exact same filters, time window, result columns and concurrency;
- several warm-up runs followed by repeated measurements;
- p50/p95/p99 latency and throughput;
- segment size/count, ingestion lag/freshness and storage;
- correctness checks comparing output totals.

**Expected observation:** a relevant Pinot index may reduce work for selective predicates; a compatible star-tree may reduce work for supported aggregations; Druid roll-up may reduce row count and query work for queries at the selected grain. None is guaranteed to help every query. Record actual results; do not fill the results CSV with expected or invented measurements.

### 11.7 Concurrency test up to 100 clients

A minimal HTTP benchmark should send a representative read query repeatedly, record successful request latency, errors and timeouts, and compute percentiles. Use a proper load-testing tool or a controlled Python async client with a connection pool. Begin at 1 client, then 10, then 25, 50 and 100 only if the system remains healthy.

Record:
- engine and exact version;
- hardware and container limits;
- dataset and segment counts;
- query text and time range;
- warm/cold cache approach;
- concurrency and test duration;
- p50/p95/p99, QPS, errors, ingestion lag and resource utilization.

Stop the test if the machine becomes unstable. Do not use a client-side load generator on the same saturated CPU without noting that it may distort results.

### 11.8 Node-failure experiment

Use a disposable local cluster only. Confirm replication and the expected impact before stopping a node.

- **Druid:** stop one Historical node only after identifying its assigned segments and verifying that another replica is available if you expect uninterrupted reads. Query a known interval before, during and after the stop; observe query errors, latency, segment availability and reassignment/recovery.
- **Pinot:** stop one Server only after verifying segment replicas and assignment. Query the same interval and observe whether the Broker can route to other replicas, plus changes in latency/errors.

If the quickstart is single-replica, the expected result may be missing data or failed queries. That is a useful observation, not proof of fault tolerance. Restart the node and wait for health and segment recovery before cleanup.

### 11.9 Compare with ClickHouse

Use the same logical event dataset and dashboard query. Load raw events into ClickHouse and use a documented sorting key; optionally create a separate pre-aggregated design only if comparing it with equivalent roll-up behavior. Compare:
- ingestion freshness and duplicate policy;
- query p50/p95/p99 at 1/10/100 clients where feasible;
- scanned data/rows if exposed, storage size, ingest throughput;
- correctness against a raw-data reconciliation query;
- operational components and failure recovery effort.

A fair report should state the hypothesis before the run and the evidence after it. Do not claim Druid, Pinot or ClickHouse is fastest without measurements on equivalent workloads.

### 11.10 Cleanup and diagnostics

Stop the generator, stop the local services using the quickstart's documented command, and remove only the disposable lab volumes/data. Before deleting volumes, ensure no important local data is stored there.

Troubleshooting checklist:

| Symptom | Possible cause | What to check |
|---|---|---|
| No records visible | Wrong topic/table/datasource, consumer not started, timestamp outside query range | Service logs, topic offsets, ingestion task/consumer state, schema and query time filter |
| Events arrive late | Consumer lag, segment publication/handoff, slow segment creation, CPU/disk contention | Kafka lag, task/consumer logs, segment count/size, resource metrics |
| Counts differ | Duplicate/replayed events, roll-up dimensions, time-zone or time-window mismatch | Unique event IDs, duplicate policy, raw input totals, time-zone and granularity settings |
| Pinot index shows no benefit | Query not compatible/selective, wrong index, segments not rebuilt, low selectivity | Table index config, segment reload/rebuild, query plan/metrics, data distribution |
| Druid roll-up changes results | Lost event-level dimensions, wrong query granularity or aggregators | Compare raw data, dimensions, time bucket, sum/count semantics |
| Query fails after node stop | No replica, segment unavailable, routing/control-plane issue | Replication configuration, segment assignment, Broker/Historical or Broker/Server logs |
| Many small segments | Small ingestion batches or over-frequent segment creation | Segment count/size, ingestion configuration, compaction and batch policy |
| High memory/CPU | High concurrency, broad scans, many segments, complex aggregation | Query profile/metrics, query fan-out, indexes, segment layout, concurrency |

## 12. Knowledge checks

1. Why can user-facing analytics require a different serving pattern from a warehouse used mainly for analyst-driven BI?
2. What is a segment, and how does it help query pruning, replication and lifecycle management?
3. Explain the Druid Broker, Coordinator, Overlord, Historical and deep-storage roles.
4. Trace a Druid query from client to result and distinguish query-serving from ingestion components.
5. Explain Pinot Controller, Broker, Server and Minion responsibilities.
6. What problem do real-time, offline and hybrid Pinot tables solve? What can go wrong at the time boundary?
7. How does Druid roll-up change the questions that can be answered from stored data?
8. When might an inverted index help? Why might a range or text index not help a different query?
9. How does a star-tree differ conceptually from scanning raw segment data?
10. What do Pinot upsert primary-key and ordering semantics control? Why must partial upserts be tested for missing/null values?
11. Why are ingestion lag and end-to-end freshness different measurements?
12. Why do too many tiny segments hurt operations and query performance?
13. How would you safely test server failure in a single-replica versus replicated lab?
14. What makes a Druid/Pinot/ClickHouse benchmark fair?
15. Which data should remain raw, and which can safely be rolled up for an ad-impressions dashboard?

## 13. Practical checkpoint

- [ ] Explain segments and the real-time/historical split.
- [ ] Draw either the Druid or Pinot query path from Broker to segment-serving nodes.
- [ ] Explain Druid roll-up and Pinot star-tree, including information loss/storage costs.
- [ ] Ingest a Kafka topic into either engine and query while the generator runs.
- [ ] Measure end-to-end freshness and monitor ingestion lag.
- [ ] Add inverted/range/star-tree indexes in Pinot or configure roll-up in Druid, then compare query results and latency.
- [ ] Run a concurrency test at 1, 10 and higher client counts; reach 100 only when resources permit.
- [ ] Observe the behavior of a server/Historical node failure in a safe local environment.
- [ ] Compare Druid and Pinot with ClickHouse on the same dataset and query mix.
- [ ] Record actual results and operational observations without inventing benchmark outcomes.

## 14. Common mistakes

- **Rolling up away detail needed later:** keep raw data or retain sufficient dimensions/aggregates for future questions.
- **Too many tiny segments:** tune ingestion/segment sizing and use supported compaction workflows.
- **Assuming Druid and Pinot have the same architecture:** keep Druid's Coordinator/Overlord/Historical terminology separate from Pinot's Controller/Broker/Server/Minion.
- **Confusing deep storage with query-serving storage:** durable segment storage and node-local serving copies have different roles.
- **Adding every Pinot index:** measure selectivity, cardinality, storage growth and ingestion overhead.
- **Treating star-tree as a universal cache:** it only helps supported query shapes and selected dimension combinations.
- **Assuming late events automatically correct historical rollups:** define and test reingestion, replacement or rebuild behavior.
- **Assuming a UUID field deduplicates data:** configure and verify an actual duplicate policy.
- **Treating Pinot upserts as full OLTP transactions:** understand primary-key, ordering, partial-update and delete semantics.
- **Benchmarking unlike data:** compare equivalent filters, freshness, roll-up, duplicate policy and query result semantics.
- **Assuming a single-replica lab proves resilience:** it does not; document the actual replication and failure outcome.
- **Underestimating always-on operations:** include ingestion, metadata/coordination, storage, monitoring, backups, upgrades and on-call costs.
- **Using these engines for ad hoc join-heavy analytics without validation:** measure join/subquery support and performance for the actual version and query shape.

## 15. Revision summary

- Druid and Pinot both use segments, but their control planes, ingestion components and query-serving paths differ.
- Druid's core roles include Broker, Historical, Coordinator and Overlord; ingestion supervisors/tasks create and publish segments.
- Pinot's core roles include Broker, Server, Controller and Minion, with Helix/ZooKeeper-based cluster coordination in standard architectures.
- Pinot's indexes solve different predicate/aggregation problems and carry storage/build costs.
- Druid roll-up reduces data by aggregating at ingestion, but it can permanently remove event-level detail from that datasource.
- Pinot upserts require explicit primary-key and ordering semantics; partial upserts need correctness tests.
- Freshness, ingestion lag, query latency and throughput are separate operational measures.
- Segment sizing, replication, compaction, retention, tiering and recovery are first-class engineering concerns.
- Compare with ClickHouse using equivalent data, queries, correctness rules and measured results.

## 16. References

Use the documentation matching the exact version you run. Configuration formats, engine capabilities and component topology evolve.

### Apache Druid

- Documentation: https://druid.apache.org/docs/latest/
- Tutorials and quickstarts: https://druid.apache.org/docs/latest/tutorials/
- Ingestion overview: https://druid.apache.org/docs/latest/ingestion/
- Kafka ingestion: https://druid.apache.org/docs/latest/ingestion/kafka-ingestion/
- Data roll-up: https://druid.apache.org/docs/latest/ingestion/rollup/
- Compaction: https://druid.apache.org/docs/latest/data-management/compaction/
- Native queries: https://druid.apache.org/docs/latest/querying/
- Storage and segment lifecycle: https://druid.apache.org/docs/latest/design/storage/
- Joins: https://druid.apache.org/docs/latest/querying/datasource/

### Apache Pinot

- Documentation: https://docs.pinot.apache.org/
- Quick start: https://docs.pinot.apache.org/getting-started/quick-start
- Architecture: https://docs.pinot.apache.org/basics/architecture
- Indexing: https://docs.pinot.apache.org/basics/indexing
- Real-time ingestion: https://docs.pinot.apache.org/basics/data-import/stream-ingestion
- Upsert and partial upsert: https://docs.pinot.apache.org/build-with-pinot/ingestion/upsert-dedup/upsert
- Indexing and index compatibility: https://docs.pinot.apache.org/build-with-pinot/indexing
- Multi-stage query engine: https://docs.pinot.apache.org/build-with-pinot/querying-and-sql/multi-stage-query
- Joins: https://docs.pinot.apache.org/build-with-pinot/querying-and-sql/sql-syntax/joins

### ClickHouse comparison

- Documentation: https://clickhouse.com/docs/
- MergeTree engine: https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree

> **Verification note:** The lesson was statically reviewed for syllabus coverage, architecture semantics, example consistency, and links to current official documentation. A Druid/Pinot/Kafka cluster was not started during authoring, so no runtime tests or benchmark results are claimed. The JSON schema, Druid SQL/native query, Pinot SQL, and Python generator examples are educational examples and were not executed against live engine versions. Use the version-matched official quickstart to validate image tags, JSON/YAML properties, API endpoints, query syntax, index configuration, MSE options and upsert/roll-up behavior before treating the lab as executed.
