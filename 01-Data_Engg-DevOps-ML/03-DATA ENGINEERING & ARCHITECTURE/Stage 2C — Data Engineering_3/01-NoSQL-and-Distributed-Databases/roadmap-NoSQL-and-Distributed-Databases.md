# Roadmap — Module 2C.1: NoSQL and Distributed Databases

This is the learning roadmap for the first module of Stage 2C, **Data
Engineering_3**. It tells you **what** to learn about NoSQL and distributed
databases, **in what order**, **how** to learn each topic, and **how to
prove to yourself** that you have learned it before you move on.

Stage 2 taught you relational databases, SQL, and columnar analytics. But
the systems that *produce* your data are often not relational: a product
catalogue in MongoDB, a session store in Redis, a high-write device log in
Cassandra, a serverless app on DynamoDB, a search index in Elasticsearch, a
fraud graph in Neo4j. A data engineer must understand how each of these
stores data, what it is good and bad at, what consistency it really gives,
and — most importantly — **how to get its data out reliably and
incrementally into the lakehouse**.

NoSQL is not "SQL, but worse" or "SQL, but faster". Each family makes a
deliberate trade-off (consistency vs availability, flexibility vs
integrity, write speed vs query flexibility). This module teaches those
trade-offs, then the main systems one by one, then the ingestion patterns
that connect them to everything you built in Stage 2.

---

## 1. Module outcome

By the end of this module you will be able to:

- Name the NoSQL families (key-value, document, wide-column, search,
  graph) and choose the right store — or choose to stay relational.
- Explain the **CAP theorem** and **PACELC**, and reason about consistency
  models (strong, eventual, causal, read-your-writes) in real systems.
- Model data and write **aggregation pipelines** in MongoDB.
- Design **query-first** partition and clustering keys in Cassandra and
  explain tombstones, compaction, and repair.
- Design a **single-table** DynamoDB schema, choose keys and indexes, and
  consume DynamoDB Streams.
- Use Redis data structures correctly for caching, counters, rate limiting,
  and queues, and explain persistence and eviction.
- Index, query, and operate Elasticsearch/OpenSearch for search and log
  analytics.
- Model connected data as a graph and write Cypher queries in Neo4j.
- Ingest NoSQL data into the lakehouse **incrementally** using change
  streams, DynamoDB Streams, and CDC connectors.

---

## 2. Prerequisites

This module builds on Stage 2 and Stage 2B. It does **not** re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Python, JSON handling, type hints, packaging | Stage 1 | Every client driver and ingestion script |
| OLTP vs OLAP, batch vs streaming | Stage 2 — Module 2.1 | Why operational NoSQL stores feed analytics platforms |
| Nested/semi-structured data, flatten and explode | Stage 2 — Module 2.5 | Document stores produce nested JSON |
| SQL, transactions, isolation levels | Stage 2 — Module 2.6 | The baseline you compare NoSQL consistency against |
| Normalisation and denormalisation | Stage 2 — Module 2.8 | NoSQL modelling is deliberate denormalisation |
| CDC concepts, watermarks, incremental extraction | Stage 2 — Module 2.9 | Foundations of Topic 09 |
| Idempotent merge loads, dedup | Stage 2 — Module 2.12 | Landing change events into tables |
| Kafka basics, Debezium | Stage 2 — Module 2.16 | Streaming NoSQL changes through Kafka |
| Docker Compose | Stage 2B — Module 2B.1 | Running every database locally |
| AWS basics (IAM, S3) | Stage 2B — Module 2B.3 | DynamoDB and OpenSearch Service |

**Tools needed:**

- Docker Compose with: **MongoDB** (as a replica set), a **3-node
  Cassandra** cluster, **Redis**, **Elasticsearch or OpenSearch** with
  Kibana/Dashboards, **Neo4j**, and **DynamoDB Local** (or LocalStack).
- Python 3.12+ in a `uv` project: `uv add pymongo cassandra-driver redis
  elasticsearch boto3 neo4j pytest`.
- A free tier of MongoDB Atlas, DynamoDB, or Neo4j Aura is optional.

**A note on versions:** Cassandra 5.x, MongoDB 7/8, and OpenSearch vs
Elasticsearch licences and APIs have diverged. Check behaviour against the
versions you run.

---

## 3. How the module is organised

The nine topics are grouped into four phases. Work through them **in order**.

```text
Phase A — Concepts and Trade-offs                   (Basics)
  01 NoSQL families and when to use them
  02 CAP theorem and consistency models

Phase B — Document and Wide-Column Stores           (Intermediate → Advanced)
  03 MongoDB: document modelling and aggregation
  04 Cassandra: wide-column partitioning and tombstones
  05 DynamoDB: single-table design and streams

Phase C — Specialised Stores                        (Intermediate → Advanced)
  06 Redis: caching and data structures
  07 Elasticsearch and OpenSearch for search and logs
  08 Graph databases: Neo4j and Cypher

Phase D — Into the Lakehouse                        (Advanced)
  09 Change streams and NoSQL-to-lakehouse ingestion

Consolidate
  Module mini-project: a polyglot operational platform feeding a lakehouse
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09
map  rules doc  wide key- fast search graph  get it
     of    store column value cache  / logs       out
     the                                          to the
     game                                         lakehouse
```

Why this order:

- Families (01) and consistency theory (02) give the vocabulary for every
  later store.
- MongoDB (03) is the gentlest NoSQL model for SQL people; Cassandra (04)
  and DynamoDB (05) force query-first thinking and partition design.
- Redis, search, and graph (06–08) are specialised stores usually used
  *alongside* a primary database.
- Ingestion (09) needs the internals of the earlier stores to be done well.

---

## 4. Suggested schedule

About **6 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — families · Topic 02 — CAP and consistency |
| 2 | Topic 03 — MongoDB modelling and aggregation |
| 3 | Topic 04 — Cassandra |
| 4 | Topic 05 — DynamoDB · Topic 06 — Redis |
| 5 | Topic 07 — Elasticsearch/OpenSearch · Topic 08 — Neo4j |
| 6 | Topic 09 — ingestion into the lakehouse · mini-project |

---

## 5. How to study every topic (the database loop)

```text
Read → Model the access patterns first → Predict behaviour → Load data
→ Query it → Break it (kill a node, add skew, create conflicts)
→ Inspect internals → Measure → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **List access patterns first** — the queries and writes the application
   needs. In NoSQL, the schema follows the queries, not the other way round.
3. **Predict** how data will be distributed, indexed, and read.
4. **Load a realistic dataset** (use one dataset — an e-commerce domain —
   across all stores so you can compare them).
5. **Query it** with the native query language and the Python driver.
6. **Break it**: stop a node, create a hot key, write conflicting updates,
   delete rows, send a huge document.
7. **Inspect internals** with each system's tools (`explain`, `nodetool`,
   `INFO`, `_cat` APIs, `PROFILE`).
8. **Measure** latency and throughput for at least two designs.
9. **Write it down** in `module-2c1-notes.md`.
10. **Explain aloud** why the chosen store and model fit the workload.

Keep one `nosql_lab/` project:

```text
nosql_lab/
├── docker-compose.yml    # MongoDB RS, Cassandra x3, Redis, OpenSearch, Neo4j, DynamoDB Local
├── data/                 # one shared e-commerce dataset generator
├── src/nosql_lab/        # drivers, loaders, queries per store
├── ingestion/            # change-stream and CDC extractors (Topic 09)
├── notebooks/            # comparison experiments
└── tests/
```

---

## 6. Phase A — Concepts and Trade-offs (Basics)

### Topic 01 — [NoSQL families and when to use them](01-nosql-families-and-when-to-use-them.md)

**Why it comes first:** "NoSQL" is a label for very different systems.
Choosing the wrong family — or choosing NoSQL when PostgreSQL would do —
is one of the costliest early architecture mistakes.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What "NoSQL" means (not only SQL); why these systems appeared (scale-out, flexible schema, low latency, specialised access patterns) |
| Basics | The five families: **key-value** (Redis, DynamoDB), **document** (MongoDB), **wide-column** (Cassandra, HBase), **search** (Elasticsearch), **graph** (Neo4j) |
| Basics | Schema-on-write vs schema-on-read; "schemaless" really means "schema in the application" |
| Intermediate | Matching families to access patterns: lookup by key, nested-object retrieval, high-volume time-series writes, full-text relevance, relationship traversal |
| Intermediate | Scaling models: vertical vs horizontal, **sharding/partitioning**, replication, and what each family does natively |
| Intermediate | **Polyglot persistence**: using several stores, each for what it does best, and the cost of keeping them in sync |
| Intermediate | When *not* to use NoSQL: joins, ad-hoc queries, multi-row transactions, and reporting — and how modern PostgreSQL with JSONB closes much of the gap |
| Advanced | NewSQL and distributed SQL (Spanner, CockroachDB, TiDB, YugabyteDB) as the other answer to scale — awareness |
| Advanced | Multi-model databases and the convergence of families (Cosmos DB, MongoDB with search and vectors, Postgres extensions) |
| Advanced | Vector databases and vector search as a new family (links to Module 2.22) — awareness |
| Advanced | The data engineer's view: every operational store is a **source system** with its own extraction constraints (Topic 09) |

**How to learn it**

1. Read the topic file.
2. For twelve scenarios (shopping cart, product catalogue, IoT telemetry,
   chat history, social graph, site search, leaderboard, audit log,
   session store, recommendations, ledger, user profiles), pick a family
   and justify, then say whether PostgreSQL alone would be enough.
3. Build a one-page comparison matrix: family × data model × scaling ×
   consistency × query power × typical failure.

**Hands-on exercise — `experiments/01_families/`**

1. Store the same 10,000 products in PostgreSQL (with JSONB), MongoDB, and
   Redis; implement "get product by id", "products by category and price
   range", and "search by text" in each; compare effort and speed.
2. Show one query that is easy in one store and painful in another.
3. Write a one-page decision guide for your team.

**Checkpoint — you are ready to move on when you can:**

- [ ] Name the five NoSQL families and one example of each.
- [ ] Choose a family from an access-pattern list.
- [ ] Explain polyglot persistence and its synchronisation cost.
- [ ] Say when relational is the better answer.

**Common mistakes:** choosing NoSQL for "scale" you do not have; treating
"schemaless" as "no design"; using one store for every access pattern;
ignoring how data will be extracted for analytics.

---

### Topic 02 — [CAP theorem and consistency models](02-cap-theorem-and-consistency-models.md)

**Why here:** every distributed database promises something different
about what a read returns after a write. Without this vocabulary, vendor
documentation is unreadable and data-loss incidents are unexplainable.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why distribution forces trade-offs: replication, network partitions, node failures |
| Basics | **CAP**: during a network **partition** you can keep **consistency** or **availability**, not both; why "pick two of three" is a misleading summary |
| Basics | **ACID** (single-node transactions) vs **BASE** (basically available, soft state, eventual consistency) |
| Intermediate | Consistency models in order of strength: **linearizable**, sequential, **causal**, **read-your-writes**, monotonic reads, **eventual** |
| Intermediate | **PACELC**: even without partitions there is a trade-off between latency and consistency |
| Intermediate | **Quorums**: N replicas, write quorum W, read quorum R, and the rule R + W > N |
| Intermediate | Tunable consistency in practice (Cassandra levels, DynamoDB strongly consistent reads, MongoDB read/write concerns) |
| Advanced | Replication mechanics: leader/follower, multi-leader, leaderless; replication lag and its visible symptoms |
| Advanced | Conflict resolution: last-write-wins, vector clocks, version vectors, **CRDTs**, application-level merge |
| Advanced | Consensus (Raft, Paxos) in one level of detail; why leader election matters; split brain |
| Advanced | Distributed transactions: two-phase commit, sagas, and why many NoSQL stores avoid multi-key transactions |
| Advanced | Testing consistency claims: the idea behind Jepsen-style analysis — awareness |

**How to learn it**

1. Read the topic file.
2. Draw a three-replica cluster; trace a write and a read for each
   consistency level and say whether a stale read is possible.
3. Compute for N = 3, 5 which (R, W) pairs give strong consistency.

**Hands-on exercise — `experiments/02_consistency/`**

1. Write a small Python simulation of three replicas with random message
   delays; show stale reads with R=1/W=1 and none with R=2/W=2.
2. On the Cassandra cluster, write at `ONE` and read at `ONE` while a node
   is down, then repeat at `QUORUM`; record the differences.
3. Demonstrate last-write-wins losing an update, then fix it with a
   version check or a simple CRDT counter.

**Checkpoint:**

- [ ] State CAP correctly, including what "partition tolerance" means.
- [ ] Explain PACELC.
- [ ] Choose R and W for a workload.
- [ ] Explain read-your-writes and why users notice its absence.
- [ ] Name two ways to resolve write conflicts.

**Common mistakes:** saying a database is "CP" or "AP" as a fixed label;
assuming eventual consistency means "eventually wrong"; ignoring replica
lag in read-after-write flows; confusing ACID's "C" with CAP's "C".

---

## 7. Phase B — Document and Wide-Column Stores (Intermediate → Advanced)

### Topic 03 — [MongoDB: document modelling and aggregation](03-mongodb-document-modelling-and-aggregation.md)

**Why here:** MongoDB is the most common document store and the most common
NoSQL *source system* a data engineer extracts from. Its documents are
nested JSON — exactly the shape that causes trouble downstream.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Databases, collections, **documents** (BSON), `_id`, data types, and how documents differ from rows |
| Basics | CRUD: `insertOne/Many`, `find`, projection, `updateOne/Many` with operators (`$set`, `$inc`, `$push`), `deleteOne/Many` |
| Basics | Query operators: comparison, logical, array, and element operators; sorting, limit, and skip |
| Intermediate | **Embedding vs referencing**: one-to-few, one-to-many, many-to-many; when to embed, when to reference, and the 16 MB document limit |
| Intermediate | Modelling patterns: bucket, subset, computed, extended reference, polymorphic, schema versioning |
| Intermediate | **Indexes**: single-field, compound (and the ESR rule), multikey, text, TTL, partial; reading `explain()` |
| Intermediate | The **aggregation pipeline**: `$match`, `$project`, `$group`, `$sort`, `$unwind`, `$lookup`, `$facet`, `$bucket`, `$merge`/`$out` |
| Intermediate | Schema validation with JSON Schema; the Python driver (PyMongo) and typed access |
| Advanced | Replica sets, elections, **read preference**, **read concern**, and **write concern**; transactions and their costs |
| Advanced | **Sharding**: shard keys (hashed vs ranged), chunk balancing, jumbo chunks, hot shards |
| Advanced | Aggregation performance: pipeline ordering, index use, memory limits, `allowDiskUse` |
| Advanced | Atlas features worth knowing: Search, Vector Search, time-series collections — awareness |

**How to learn it**

1. Read the topic file.
2. Model the e-commerce domain twice — fully embedded and fully referenced
   — and write the five main queries for each.
3. Rewrite three SQL aggregations (group by, join, top-N) as pipelines.

**Hands-on exercise — `experiments/03_mongodb/`**

1. Load 500,000 orders with line items; build a compound index following
   the ESR rule and show `explain()` before and after.
2. Build a pipeline that produces daily revenue per category using
   `$unwind`, `$group`, and `$merge`.
3. Create a schema validator and show a rejected document.
4. Add a TTL index and a partial index; prove they work.
5. On a replica set, stop the primary and observe the election.

**Checkpoint:**

- [ ] Decide embed vs reference for a relationship and defend it.
- [ ] Design a compound index with the ESR rule.
- [ ] Write a multi-stage aggregation pipeline.
- [ ] Explain read and write concerns.
- [ ] Explain how to choose a shard key.

**Common mistakes:** unbounded arrays that grow forever; no index on the
query shape; `$lookup` used as a general join; a monotonically increasing
shard key; ignoring document size.

---

### Topic 04 — [Cassandra: wide-column partitioning and tombstones](04-cassandra-wide-column-partitioning-and-tombstones.md)

**Why here:** Cassandra is built for massive write throughput and
always-on availability. It rewards correct partition design and punishes
SQL habits — making it the best teacher of query-first modelling.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The ring architecture, nodes, keyspaces, tables, and **CQL** (SQL-like but not SQL) |
| Basics | **Primary key** = **partition key** + **clustering columns**; data inside a partition is stored sorted by clustering columns |
| Basics | Why there are no joins, no arbitrary `WHERE`, and no `ORDER BY` outside clustering order |
| Intermediate | **Query-first modelling**: one table per query, deliberate duplication, and partition sizing (bounded partitions, time bucketing) |
| Intermediate | Replication strategies, replication factor, and **consistency levels** (`ONE`, `QUORUM`, `LOCAL_QUORUM`, `ALL`) |
| Intermediate | The **write path**: commit log → memtable → SSTable; the read path with Bloom filters, caches, and merging SSTables |
| Intermediate | Collections, UDTs, static columns, TTL, counters, and lightweight transactions (`IF NOT EXISTS`) |
| Intermediate | Secondary indexes, SAI (storage-attached indexes), and materialised views — why they are used sparingly |
| Advanced | **Tombstones**: how deletes are written as markers, `gc_grace_seconds`, tombstone-heavy reads, and "zombie" data |
| Advanced | **Compaction** strategies (size-tiered, leveled, time-window) and matching them to workloads |
| Advanced | **Repair** (anti-entropy), hinted handoff, read repair, and consistency over time |
| Advanced | Operations: `nodetool`, adding and removing nodes, vnodes, monitoring, and capacity planning; Cassandra 5 features — awareness |
| Advanced | Extraction for analytics: full-table scans by token range, Spark connector, CDC logs |

**How to learn it**

1. Read the topic file.
2. For five queries (messages by user, events by device per day, orders by
   customer, sensor readings by hour, top posts), design one table each.
3. Draw the partition and clustering layout and the on-disk effect.

**Hands-on exercise — `experiments/04_cassandra/`**

1. Create a `sensor_readings` table partitioned by `(device_id, day)` and
   ingest 5 million rows; show one query served from one partition.
2. Create an unbounded partition on purpose, watch it grow, then fix it
   with time bucketing.
3. Delete many rows, then read; observe tombstone warnings and fix with a
   better delete pattern or TTL.
4. Stop a node, write at `QUORUM`, restart it, and run a repair.
5. Compare size-tiered and time-window compaction for time-series data.

**Checkpoint:**

- [ ] Explain partition key vs clustering columns.
- [ ] Design tables from queries, not from entities.
- [ ] Trace the write and read paths.
- [ ] Explain tombstones and why heavy deletes hurt.
- [ ] Choose a consistency level and a compaction strategy.

**Common mistakes:** unbounded partitions; using Cassandra as a queue
(delete-heavy workloads); `ALLOW FILTERING` in production; secondary
indexes on high-cardinality columns; skipping repairs.

---

### Topic 05 — [DynamoDB: single-table design and streams](05-dynamodb-single-table-design-and-streams.md)

**Why here:** DynamoDB is the default database of serverless AWS
applications. Its access-pattern-first design and its Streams feature
matter directly to data engineers (Stage 2B Module 3 covers the AWS side).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Tables, items, attributes; **partition key** and optional **sort key**; data types |
| Basics | Core operations: `PutItem`, `GetItem`, `UpdateItem`, `DeleteItem`, `Query` vs `Scan` and why `Scan` is a smell |
| Basics | Capacity modes: **on-demand** vs **provisioned**; read/write capacity units |
| Intermediate | **Access-pattern-first modelling**: list every query, then design keys; overloaded generic key names (`PK`, `SK`) |
| Intermediate | **Single-table design**: storing several entity types in one table, item collections, and when separate tables are fine |
| Intermediate | **Secondary indexes**: LSI vs **GSI**, projections, GSI overloading and sparse indexes |
| Intermediate | Conditional writes, optimistic locking with version attributes, atomic counters, TTL |
| Intermediate | `boto3` resource and client APIs, pagination, batch operations, and handling throttling with retries |
| Advanced | Hot partitions, adaptive capacity, write sharding, and key distribution |
| Advanced | **Transactions** (`TransactWriteItems`), their limits and costs; consistency (eventual vs strong reads) and global tables |
| Advanced | **DynamoDB Streams** and Kinesis Data Streams for DynamoDB: item-level change records, ordering per key, 24-hour retention, and Lambda consumers |
| Advanced | Export to S3 (point-in-time exports) and incremental exports for analytics; zero-ETL integrations (links to Stage 2B Module 3) |
| Advanced | Cost modelling and avoiding scans; backup and point-in-time recovery |

**How to learn it**

1. Read the topic file.
2. For a "customers, orders, items, addresses" domain, list 8 access
   patterns, then design one table with keys and two GSIs on paper.
3. Walk each access pattern through the design and mark the exact
   operation used.

**Hands-on exercise — `experiments/05_dynamodb/`**

1. Implement the design in DynamoDB Local; load sample data; run all 8
   patterns using only `Query`/`GetItem`.
2. Add a sparse GSI and use it to find "open orders".
3. Implement optimistic locking with a condition expression and show a
   rejected stale update.
4. Enable a stream; write a consumer that turns change records into
   Parquet files in object storage.
5. Create a hot key, observe throttling, and fix it with write sharding.

**Checkpoint:**

- [ ] Derive keys and indexes from access patterns.
- [ ] Explain single-table design and its trade-offs.
- [ ] Use conditions and transactions correctly.
- [ ] Explain what Streams records contain and how long they last.
- [ ] Choose between on-demand and provisioned capacity.

**Common mistakes:** designing like a relational schema; relying on
`Scan`; low-cardinality partition keys; large items; treating Streams as a
permanent log.

---

## 8. Phase C — Specialised Stores (Intermediate → Advanced)

### Topic 06 — [Redis: caching and data structures](06-redis-caching-and-data-structures.md)

**Why here:** Redis appears next to almost every production system: as a
cache, a rate limiter, a session store, a lightweight queue, and a
real-time leaderboard. Data engineers meet it as a serving layer and as a
source of operational state.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | In-memory key-value store, single-threaded command execution, and why it is fast |
| Basics | Core data types: **strings**, **hashes**, **lists**, **sets**, **sorted sets**; commands and big-O cost of each |
| Basics | Expiry and TTL (`EXPIRE`, `SET ... EX`); namespacing keys |
| Intermediate | Caching patterns: **cache-aside**, read-through, write-through, write-behind; **stampede** protection and TTL jitter |
| Intermediate | Atomic operations: `INCR`, `SETNX`, Lua scripts, transactions (`MULTI`/`EXEC`), and pipelining |
| Intermediate | Patterns: rate limiting, distributed locks (and their caveats), leaderboards, session stores, deduplication with sets |
| Intermediate | **Streams** (consumer groups) and pub/sub; lists as simple queues; comparing with Kafka |
| Intermediate | Python client usage, connection pools, and serialisation choices |
| Advanced | **Persistence**: RDB snapshots vs AOF; durability trade-offs |
| Advanced | **Eviction policies** (`allkeys-lru`, `volatile-ttl`, etc.), memory analysis, big keys, and fragmentation |
| Advanced | **Replication, Sentinel, and Cluster**: hash slots, resharding, failover, and multi-key limits |
| Advanced | Probabilistic structures: HyperLogLog, Bloom filters, bitmaps (links to Module 2C.9 sketches) |
| Advanced | Redis as a feature store/serving cache for ML and as a vector store — awareness |

**How to learn it**

1. Read the topic file.
2. Practise every data type in `redis-cli`, recording the time complexity.
3. Sketch cache-aside for a slow aggregate query and list invalidation
   strategies.

**Hands-on exercise — `experiments/06_redis/`**

1. Put a cache in front of a slow DuckDB or Postgres aggregate; measure
   hit ratio and latency.
2. Implement a sliding-window rate limiter with a sorted set.
3. Build a leaderboard and a unique-visitor counter (set vs HyperLogLog)
   and compare memory.
4. Reproduce a cache stampede and fix it with a lock or jittered TTL.
5. Fill memory under `allkeys-lru` and watch evictions.

**Checkpoint:**

- [ ] Choose the right Redis type for a use case.
- [ ] Implement cache-aside with sane invalidation.
- [ ] Explain RDB vs AOF and the durability you actually get.
- [ ] Explain eviction policies and Cluster hash slots.
- [ ] Explain why Redis is a cache, not your system of record.

**Common mistakes:** no TTLs; huge keys; `KEYS *` in production; treating
distributed locks as bulletproof; assuming persistence equals durability.

---

### Topic 07 — [Elasticsearch and OpenSearch for search and logs](07-elasticsearch-and-opensearch-for-search-and-logs.md)

**Why here:** search and log analytics are everywhere — product search,
application logs, security events. Elasticsearch and OpenSearch are the
standard engines, and data engineers feed and extract from them.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Clusters, nodes, **indices**, documents, **shards** and **replicas**; the REST API and Kibana/Dashboards |
| Basics | The **inverted index**: analysis → tokens → postings; why full-text search is fast |
| Basics | Indexing documents, searching, and reading a response (`hits`, `_score`) |
| Intermediate | **Mappings**: field types, `text` vs `keyword`, multi-fields, dynamic vs explicit mapping, and mapping explosion |
| Intermediate | **Analyzers**: tokenizers, filters, stemming, synonyms, and custom analyzers |
| Intermediate | The query DSL: `match`, `term`, `bool` (must/should/filter), `range`, `multi_match`; relevance scoring (BM25) and boosting |
| Intermediate | **Aggregations**: metrics, buckets, and pipeline aggregations for analytics |
| Intermediate | Bulk indexing with the Python client and helpers; refresh interval and near-real-time behaviour |
| Advanced | **Logs at scale**: data streams, index templates, **ILM / ISM** (hot-warm-cold-delete), rollover, and shard sizing |
| Advanced | Shard strategy and cluster sizing: over-sharding, heap pressure, and hot nodes |
| Advanced | Reindexing, aliases, and zero-downtime schema changes |
| Advanced | Ingest pipelines, Logstash/Beats/Fluent Bit/OpenTelemetry collectors in the ingest path |
| Advanced | Vector and hybrid search (k-NN with keyword) — awareness; Elasticsearch vs OpenSearch differences and licensing |
| Advanced | Search as a **derived store**: keeping it in sync from the source of truth, and extracting data for analytics (scroll / PIT + search_after) |

**How to learn it**

1. Read the topic file.
2. Index a product catalogue; run queries from simple to relevance-tuned.
3. Use the `_analyze` API to see how text becomes tokens.

**Hands-on exercise — `experiments/07_search/`**

1. Create an explicit mapping for products, bulk-index 200,000 documents,
   and compare `text` vs `keyword` queries.
2. Build a custom analyzer with synonyms and show better recall.
3. Write a `bool` query with filters and a faceted aggregation (brand,
   price histogram).
4. Ingest synthetic application logs into a data stream with a rollover
   and ILM policy.
5. Reindex to a new mapping behind an alias with no downtime.
6. Export the index to Parquet using point-in-time + `search_after`.

**Checkpoint:**

- [ ] Explain the inverted index and analysis.
- [ ] Choose `text` vs `keyword` and design a mapping.
- [ ] Write bool queries and aggregations.
- [ ] Design index lifecycle and shard counts for logs.
- [ ] Extract a full index reliably.

**Common mistakes:** dynamic mapping explosions; too many small shards;
treating the search index as the system of record; deep paging with
`from/size`; no lifecycle policy for logs.

---

### Topic 08 — [Graph databases: Neo4j and Cypher](08-graph-databases-neo4j-and-cypher.md)

**Why here:** some questions — fraud rings, recommendations, dependency
and lineage graphs, identity resolution — are about relationships. Graph
databases make those queries natural where SQL needs many self-joins.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The **property graph** model: nodes, relationships, labels, relationship types, properties |
| Basics | Why traversal beats recursive joins for connected data; index-free adjacency |
| Basics | **Cypher** basics: `MATCH`, `WHERE`, `RETURN`, `CREATE`, `MERGE`, `SET`, `DELETE`, `LIMIT` |
| Intermediate | Patterns: variable-length paths, shortest path, optional matches, `WITH`, aggregation, `UNWIND` |
| Intermediate | **Graph modelling**: nodes vs properties vs relationships, avoiding "super nodes", modelling time and events |
| Intermediate | Constraints and indexes; `PROFILE` and `EXPLAIN` for tuning |
| Intermediate | Loading data: `LOAD CSV`, batched `UNWIND` with the Python driver, idempotent `MERGE` |
| Advanced | **Graph algorithms** (Graph Data Science): PageRank, community detection, similarity, path finding |
| Advanced | Use cases: fraud rings, recommendations, knowledge graphs, lineage and dependency graphs, identity resolution |
| Advanced | Clustering and scaling in Neo4j; limits of single-writer scaling; alternatives (property graphs on other engines, RDF/SPARQL) — awareness |
| Advanced | Graph + LLM patterns (GraphRAG) — awareness; exporting graph data to the lakehouse for analytics |

**How to learn it**

1. Read the topic file.
2. Whiteboard a customers–accounts–devices–transactions model and
   identify the questions only a graph answers easily.
3. Rewrite a 4-hop SQL self-join in Cypher.

**Hands-on exercise — `experiments/08_neo4j/`**

1. Load a synthetic fraud dataset (people, accounts, shared devices,
   transfers) with batched, idempotent `MERGE`.
2. Find accounts sharing devices with a known fraudster within 3 hops.
3. Use `PROFILE` to compare runtimes with and without an index.
4. Run PageRank and community detection and export results to Parquet.
5. Create a super node and show the performance impact.

**Checkpoint:**

- [ ] Model a domain as a property graph.
- [ ] Write Cypher with variable-length paths and aggregation.
- [ ] Load data idempotently in batches.
- [ ] Choose a graph over SQL for the right reasons.

**Common mistakes:** modelling everything as nodes with no properties
discipline; super nodes; `CREATE` instead of `MERGE` causing duplicates;
using a graph database for plain tabular analytics.

---

## 9. Phase D — Into the Lakehouse (Advanced)

### Topic 09 — [Change streams and NoSQL-to-lakehouse ingestion](09-change-streams-and-nosql-to-lakehouse-ingestion.md)

**Why it comes last:** this is the topic that turns everything above into
a data engineering skill. Operational NoSQL stores must be copied into the
lakehouse **incrementally, correctly, and cheaply** — without hammering
the source.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why you do not run analytics on the operational store; extraction constraints of each family |
| Basics | **Full snapshot** extraction per store and its cost; scanning by key range or token range |
| Basics | **Watermark-based incremental** extraction (updated-at fields) and its blind spots: deletes and missing timestamps (from Module 2.9) |
| Intermediate | **MongoDB change streams**: resume tokens, full-document lookup, pre/post-images, oplog window limits |
| Intermediate | **DynamoDB Streams / Kinesis** and incremental S3 exports; **Cassandra CDC** logs; Elasticsearch and Neo4j sync patterns |
| Intermediate | Kafka-based pipelines: MongoDB source connectors, Debezium for MongoDB/Cassandra, sinks into object storage (Module 2.16) |
| Intermediate | Landing and flattening: raw JSON in Bronze, schema inference, flattening nested documents, arrays → child tables (Module 2.5) |
| Intermediate | **Applying changes**: ordering per key, idempotent `MERGE` into Delta/Iceberg tables, handling deletes as tombstone events (Module 2.15) |
| Advanced | Schema drift in schemaless sources: detection, evolution policy, and quarantining bad documents (Module 2.11) |
| Advanced | Initial snapshot + stream handoff without gaps or duplicates (snapshot isolation, resume tokens, watermarks) |
| Advanced | Replaying and backfilling safely; oplog/stream retention windows and what to do when they are exceeded |
| Advanced | Managed options: Atlas Data Federation, DynamoDB zero-ETL, Glue/Databricks connectors (Stage 2B), Airbyte/Fivetran/dlt — build vs buy |
| Advanced | Reconciliation: row counts, checksums, and sampled comparisons between source and lakehouse |
| Advanced | Observability: lag per source, missed-resume alarms, and cost of reads against the source |

**How to learn it**

1. Read the topic file.
2. For each of the five stores, write down how you would get a full copy,
   how you would get changes, and how you would see deletes.
3. Draw the handoff from initial snapshot to change stream and mark where
   duplicates or gaps could appear.

**Hands-on exercise — `experiments/09_nosql_to_lakehouse/`**

1. Open a MongoDB change stream; persist resume tokens; kill and restart
   the consumer without losing events.
2. Do an initial snapshot of a collection, then switch to the stream with
   no gap; verify with reconciliation.
3. Consume a DynamoDB (Local) stream and write changes as Parquet/Delta,
   applying them with an idempotent `MERGE` including deletes.
4. Flatten a nested orders collection (arrays → child tables) into
   Bronze → Silver.
5. Introduce a new field and a type change in the source; detect and
   handle the drift.
6. Write a runbook for "the resume token expired".

**Checkpoint:**

- [ ] Choose full, incremental, or CDC extraction per store.
- [ ] Apply change events idempotently, including deletes.
- [ ] Hand off from snapshot to stream without gaps.
- [ ] Handle schema drift in a schemaless source.
- [ ] Reconcile a lakehouse table against its source.

**Common mistakes:** polling with `updated_at` and missing deletes;
running heavy scans against production primaries; losing resume tokens;
no plan for retention-window expiry; flattening documents without a stable
key.

---

## 10. Module mini-project — a polyglot operational platform feeding a lakehouse

**Goal:** build a small e-commerce backend using the right store for each
job, then replicate everything into one lakehouse.

**Requirements**

1. **MongoDB** holds the product catalogue and orders; **Cassandra** holds
   high-volume clickstream/sensor events; **DynamoDB (Local)** holds
   carts; **Redis** caches hot product pages and enforces rate limits;
   **OpenSearch** serves product search and logs; **Neo4j** powers
   "customers also bought" and a simple fraud check.
2. A data generator drives all stores with realistic traffic.
3. Ingestion jobs copy every store into Bronze (Delta or Iceberg) using
   the best incremental method for each; deletes are respected.
4. Silver tables flatten nested documents; Gold has a daily revenue and
   funnel model queried with DuckDB or Spark.
5. A reconciliation report compares source and lakehouse counts daily.
6. A design document explains every store choice, key design,
   consistency level, and failure behaviour, plus a runbook.

**Done when** killing any single database node does not stop the platform,
the lakehouse reconciles with every source, and your design document can
defend every choice.

---

## 11. Module self-assessment — exit criteria

You have completed this module when you can do all of the following
**without notes**:

- [ ] Choose a data store family from an access-pattern list, or choose
      relational.
- [ ] State CAP and PACELC accurately and pick quorum settings.
- [ ] Model and aggregate documents in MongoDB.
- [ ] Design Cassandra and DynamoDB tables from queries and explain
      tombstones, compaction, and hot partitions.
- [ ] Use Redis safely as a cache and explain its durability limits.
- [ ] Build and size a search and log index.
- [ ] Model a relationship problem as a graph.
- [ ] Ingest any of these stores into the lakehouse incrementally with
      deletes, drift handling, and reconciliation.

---

## 12. Recommended reading and references

- *Designing Data-Intensive Applications* — Martin Kleppmann (replication,
  partitioning, consistency, and consensus chapters).
- Official documentation: MongoDB Manual, Apache Cassandra docs, Amazon
  DynamoDB Developer Guide, Redis docs, Elasticsearch/OpenSearch
  references, Neo4j Cypher manual.
- *The DynamoDB Book* — Alex DeBrie (single-table design).
- *Cassandra: The Definitive Guide* — Jeff Carpenter and Eben Hewitt.
- Jepsen analyses (jepsen.io) for real-world consistency behaviour.

---

## 13. Where this module leads

- **Module 2C.2** looks back at the Hadoop-era stores (HBase, Hive) that
  influenced these designs.
- **Modules 2C.3–2C.5** apply similar thinking to cloud warehouses.
- **Module 2C.7** covers real-time OLAP engines that serve analytics at
  low latency.
- **Module 2C.8** places polyglot stores inside a wider data-platform
  architecture.
