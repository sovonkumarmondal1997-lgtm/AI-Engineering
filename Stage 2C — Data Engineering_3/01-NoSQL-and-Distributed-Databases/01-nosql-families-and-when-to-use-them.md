# NoSQL Families and When to Use Them

**Stage:** Stage 2C — Data Engineering_3  
**Module:** 01 — NoSQL and Distributed Databases  
**Lesson:** Topic 01 — NoSQL families and when to use them  
**Output:** `01-nosql-families-and-when-to-use-them.md`

------------------------------------------------------------------------

## Learning objectives

By the end of this lesson, you should be able to:

1.  Explain what *NoSQL* means and why specialized, distributed data stores emerged.
2.  Identify the five families—key-value, document, wide-column, search, and graph—and representative systems.
3.  Distinguish schema-on-write from schema-on-read and explain why “schemaless” still requires application-level data contracts.
4.  Match a database family to an access pattern rather than choosing by trend or product popularity.
5.  Explain vertical and horizontal scaling, sharding/partitioning, and replication at a conceptual level.
6.  Describe polyglot persistence and account for the synchronization, operations, and data-governance costs it introduces.
7.  Recognize when PostgreSQL or another relational database is the simpler, safer choice, including cases where PostgreSQL `JSONB` is sufficient.
8.  Recognize distributed SQL/NewSQL, multi-model systems, and vector search without treating them as deep-dive topics in this lesson.
9.  Think like a data engineer: understand that operational databases are source systems with different extraction, change-capture, retention, and consistency constraints.
10. Complete the twelve scenario decisions and the `experiments/01_families/` comparison exercise without inventing performance claims.

## How this lesson fits the roadmap

The project tree places this lesson at:

``` text
Stage 2C — Data Engineering_3/
└── 01-NoSQL-and-Distributed-Databases/
    ├── 01-nosql-families-and-when-to-use-them.md  ← this lesson
    ├── 02-cap-theorem-and-consistency-models.md
    ├── 03-mongodb-document-modelling-and-aggregation.md
    ├── 04-cassandra-wide-column-partitioning-and-tombstones.md
    ├── 05-dynamodb-single-table-design-and-streams.md
    ├── 06-redis-caching-and-data-structures.md
    ├── 07-elasticsearch-and-opensearch-for-search-and-logs.md
    ├── 08-graph-databases-neo4j-and-cypher.md
    └── 09-change-streams-and-nosql-to-lakehouse-ingestion.md
```

The authoritative module syllabus puts Topic 01 first because it supplies the vocabulary for the remaining eight lessons. Topic 02 formalizes distributed consistency and CAP; Topics 03–08 examine individual stores; Topic 09 focuses on extracting operational changes into a lakehouse. This lesson introduces the families and trade-offs, but does **not** replace those later deep dives.

### Prerequisites

The module assumes you have already encountered:

- Python, JSON, type hints, packages, and database client libraries (Stage 1).
- OLTP versus OLAP, batch versus streaming, and nested/semi-structured data (Stage 2).
- SQL, relational modelling, transactions, isolation, normalization, and denormalization (Stage 2).
- CDC, watermarks, incremental extraction, idempotent merge loads, deduplication, Kafka/Debezium basics (Stage 2).
- Docker Compose and basic AWS/IAM/S3 concepts (Stage 2B).

You do not need to know every vendor API before starting. Learn the model and workload fit first; the later lessons teach the system-specific operations.

## 1. Fundamentals: what does NoSQL mean?

**NoSQL** is commonly expanded as “not only SQL.” It is an umbrella term for database systems whose data models, query interfaces, scaling strategies, or consistency trade-offs differ from the traditional relational model. It does **not** mean that SQL is bad, that these databases never use SQL-like languages, or that every NoSQL system is distributed.

Relational databases represent data in relations (usually tables with rows and columns), describe relationships with keys, and provide declarative queries through SQL. They are excellent general-purpose systems. NoSQL systems emerged and matured as applications needed combinations of:

- **Scale-out:** distribute storage and work across multiple machines instead of relying only on a larger server.
- **Flexible data shape:** represent nested or evolving records without requiring every attribute to fit a fixed table layout.
- **Low latency for a known operation:** optimize common requests such as “get this key,” “retrieve this document,” or “find documents matching these words.”
- **Specialized access patterns:** efficiently traverse relationships, rank text results, or accept high-volume writes partitioned by a device or time window.
- **Operational availability across nodes or regions:** continue serving selected operations despite certain failures, according to the system’s consistency and availability design.

These are motivations, not guarantees. A NoSQL database may still need careful schema design, indexes, capacity planning, backups, access control, and operational expertise. It may not scale well for a poorly chosen key, and a flexible document store can still have expensive queries.

### A database is a workload decision

Start with the application’s **access patterns**—the reads, writes, filters, ordering, aggregations, and relationships it must support. For example:

- “Given `product_id`, return one product” is a key lookup.
- “Return a product with its variants and attributes” is a nested-object retrieval.
- “Find sensor readings for device D during a time interval” is a time-series/event access pattern.
- “Search product descriptions for ‘waterproof hiking jacket’ and rank relevant results” is full-text search.
- “Find friends-of-friends or paths between accounts” is relationship traversal.

The same business entity may appear in more than one store because each store supports a different operation. That is an architectural choice with costs, not a free optimization.

## 2. The five NoSQL families

### 2.1 Key-value stores

**Model:** a unique key maps to a value. The value may be a string, bytes, serialized object, or a richer native structure depending on the product.

``` text
"session:8f2..." ──► {"user_id": 42, "expires_at": "..."}
"cart:42"        ──► serialized cart or structured value
"score:player7"  ──► 1840
```

**Representative systems:** Redis and Amazon DynamoDB. They are both commonly used for key-oriented access, but they are not interchangeable: Redis is an in-memory data-structure server often used for caching and real-time state, while DynamoDB is a managed durable key-value/document database with partition and optional sort keys.

**How it works:** the application supplies a key; the system locates the corresponding item/value. Hashing or partition-key routing can distribute keys across nodes. Some systems expose rich operations over values, conditional writes, expiration, or range queries within a key partition.

**Use it when:** the dominant operation is lookup/update by a known key; examples include sessions, carts, idempotency records, feature-serving caches, counters, and leaderboards (Redis sorted sets).

**Trade-offs and risks:** - Arbitrary filtering across all values may require scans or secondary indexes. - A hot key can receive disproportionate traffic. - Cache eviction or expiration may remove data; cache data must be rebuildable if it is not the system of record. - Key design becomes part of the application API. - Durability, replication, transactions, and query features differ by product; do not infer them from the family name.

**Industry example:** an online service uses Redis to cache a frequently requested profile summary. PostgreSQL remains authoritative. Cache misses read PostgreSQL; updates invalidate or refresh the cache. The cache improves latency but adds invalidation and stale-data risks.

### 2.2 Document databases

**Model:** records are documents, typically nested JSON-like structures. MongoDB stores BSON, a binary representation with additional types. Documents in a collection may have different fields, although production systems should usually validate important fields.

``` json
{
  "_id": "p-1007",
  "name": "Trail Jacket",
  "category": "outerwear",
  "price": 89.5,
  "attributes": {
    "waterproof": true,
    "insulation": "light"
  },
  "variants": [
    {"sku": "TJ-BLK-M", "size": "M", "color": "black"}
  ]
}
```

**Representative system:** MongoDB.

**How it works:** a document groups attributes that are often read or updated together. Indexes can support queries on selected fields, including nested fields and arrays. Applications can embed related data or store references to other documents.

**Use it when:** records are naturally nested, their attributes evolve, and common operations retrieve a whole aggregate (for example, a product with variants, content records, user preferences, or application configuration).

**Trade-offs and risks:** - Duplicated embedded data may become inconsistent when copied facts change. - Large or unbounded arrays can make documents expensive to update and approach product limits. - Cross-document relationships and broad ad-hoc analytics may be less natural than relational joins and SQL. - Flexible shape can lead to inconsistent field names/types unless validation and migrations are deliberate.

**Industry example:** a product catalogue stores product-specific attributes in documents because shoes, appliances, and clothing have different attribute sets. Price and category fields still need consistent types and indexes.

### 2.3 Wide-column stores

**Model:** data is organized around partition keys and ordered clustering columns, with a storage model designed for distributed, high-throughput access. “Wide-column” covers related but distinct systems. Cassandra uses a partitioned row model with CQL tables and SSTables; HBase offers sparse, versioned cells addressed by row key, column family, and qualifier. Do not assume their APIs or internals are identical.

**Representative systems:** Apache Cassandra and Apache HBase.

**How it works:** data is distributed by a row/partition key. A table is typically designed around known queries. In Cassandra, the primary key includes a partition key and optional clustering columns that determine ordering within a partition. HBase uses row keys and column families to locate cells. Both can handle large datasets across nodes, but modelling and operations differ.

**Use it when:** high write volume, large distributed datasets, and predictable query patterns dominate—such as device telemetry, event histories, messaging timelines, or time-bucketed observations.

**Trade-offs and risks:** - Query-first design may require multiple tables/materialized representations for different access patterns. - Joins and arbitrary ad-hoc filters are not the main strength. - Poor partition keys can create hot partitions or unbounded partitions. - Deletes and compaction/maintenance behavior matter; Cassandra tombstones are covered in Topic 04, while HBase has its own storage and compaction behavior.

**Industry example:** telemetry is partitioned by device and day so a query for one device’s readings during a day targets a bounded region rather than scanning every device’s history.

### 2.4 Search engines / search stores

**Model:** indexed documents optimized for text matching, filtering, facets/aggregations, and relevance ranking. Elasticsearch and OpenSearch are search and analytics engines, not simply general-purpose document databases.

**Representative systems:** Elasticsearch and OpenSearch.

**How it works:** a text field is analyzed into tokens. An **inverted index** maps each token to documents containing it. Query logic combines term matching, filters, and relevance scoring. Numeric, date, and keyword fields can support structured filters and aggregations.

``` text
Document text: "waterproof lightweight hiking jacket"
             │ analyzer/tokenizer
             ▼
Tokens: waterproof | lightweight | hiking | jacket
             │
             ▼
Inverted index: token ──► matching document IDs
```

**Use it when:** users need full-text search, ranking, typo/synonym handling, faceted navigation, or log/event search. Search engines are often **derived stores** populated from an authoritative database or event stream.

**Trade-offs and risks:** - Search results may lag source writes because indexing and refresh are asynchronous. - Relevance quality depends on mappings, analyzers, synonyms, and query design. - Indexes consume storage and need shard sizing, lifecycle management, and reindexing plans. - Keeping a search index in sync with the source of truth is a data pipeline problem. - A search engine is usually not the best sole authority for financial balances or transactional workflows.

**Industry example:** PostgreSQL stores products and orders; a pipeline projects searchable product fields into Elasticsearch/OpenSearch for relevance-ranked catalogue search.

### 2.5 Graph databases

**Model:** nodes represent entities, edges represent relationships, and both can carry properties. A graph database makes relationships first-class rather than treating every traversal as a sequence of joins.

``` text
(:Person {id: "A"})-[:FOLLOWS]->(:Person {id: "B"})
       │
       └──[:WORKS_WITH]──►(:Person {id: "C"})
```

**Representative system:** Neo4j, queried with Cypher.

**How it works:** queries begin with entities or patterns and traverse connected edges. Graph storage and query engines are designed to explore multi-hop relationships.

**Use it when:** the question is fundamentally about connections—fraud rings, identity resolution, recommendation paths, dependency graphs, knowledge graphs, or network topology.

**Trade-offs and risks:** - Simple key lookups or large tabular aggregations may be more straightforward in other systems. - Graph modelling still requires domain choices about node and relationship types. - Very broad traversals can be expensive; query shape and limits matter. - Operational and analytical graph workloads may have different requirements.

**Industry example:** a fraud analysis system explores whether an account shares devices, payment instruments, addresses, or transaction paths with known suspicious accounts.

## 3. Schema-on-write, schema-on-read, and application contracts

A **schema** describes expected fields, types, constraints, and relationships.

- **Schema-on-write:** validate or enforce the structure when data is written. Relational tables typically enforce column types and constraints; MongoDB can use collection validators; application code can validate requests before persistence.
- **Schema-on-read:** interpret or validate structure when data is read or transformed. This is common when raw semi-structured records are landed before all fields are standardized.
- **Flexible schema:** records may differ in shape, but this does not eliminate the need to define what each field means.

“Schemaless” is misleading shorthand. A document store may allow a document without `price`, another with `price` as a string, and a third with `price` as a number. The database may accept these, but application code, sorting, filtering, and downstream analytics can behave inconsistently.

A robust application-level contract should specify: - required and optional fields; - data types and units (for example, `price` in one currency); - allowed values and null semantics; - identifier formats; - compatibility rules for adding, renaming, or retiring fields; - validation and migration strategy.

**Example:** adding `shipping_address.postal_code` may be backward-compatible if readers tolerate its absence. Changing `price` from a number to a formatted string is likely a breaking change. Versioning or migration logic may be required.

The important distinction is not “SQL has schema, NoSQL has none.” It is where and when schema rules are enforced, how flexible the model is, and who owns data quality.

## 4. Match the model to the access pattern

| Access pattern                                                  | Natural fit | Why                                           | Important caveat                                             |
|-----------------------------------------------------------------|-------------|-----------------------------------------------|--------------------------------------------------------------|
| Exact lookup by key                                             | Key-value   | Direct key routing                            | Broad filtering may need another index/store                 |
| Nested aggregate/document retrieval                             | Document    | Related fields travel together                | Avoid unbounded documents and uncontrolled duplication       |
| High-volume partitioned event/time-series writes                | Wide-column | Partitioned write path and query-first tables | Partition key, bucketing, and retention are critical         |
| Full-text relevance and facets                                  | Search      | Inverted index, analyzers, scoring            | Usually an asynchronously maintained projection              |
| Multi-hop relationship traversal                                | Graph       | Relationships are first-class                 | Broad traversal and analytics still need careful design      |
| Joins, constraints, flexible ad-hoc SQL, multi-row transactions | Relational  | Mature SQL and transactional semantics        | Distributed scale may require architecture and capacity work |

The best fit is determined by the **dominant query shapes**, latency objectives, consistency requirements, write rate, data volume, operational capability, and cost. No family is universally superior.

## 5. Scaling and distribution

### 5.1 Vertical versus horizontal scaling

- **Vertical scaling (scale up):** add CPU, memory, storage throughput, or a larger machine to one database node. It is often operationally simple until cost, hardware, or a single-node ceiling becomes limiting.
- **Horizontal scaling (scale out):** distribute data and/or request processing across multiple machines. It can increase aggregate capacity and resilience, but adds network hops, coordination, data placement, failure modes, and operational complexity.

Many relational systems scale vertically very effectively and can also scale reads through replicas, partition data, or use distributed extensions/services. Many NoSQL systems are designed around horizontal distribution, but “NoSQL” does not automatically mean effortless scale-out.

### 5.2 Partitioning and sharding

**Partitioning** means splitting a dataset into smaller logical or physical pieces. The term is used differently by products: a relational table can be partitioned within one database, while a distributed system may partition data across nodes.

**Sharding** commonly means distributing partitions across multiple database servers or shards. A **shard key** or partition key determines where a record lives.

``` text
Application
    │ key / partition key
    ▼
Routing layer
    ├── partition A ──► node 1
    ├── partition B ──► node 2
    └── partition C ──► node 3
```

Good partition keys distribute traffic and storage while keeping common queries targeted. Poor choices cause:

- **Hot partition/shard:** one partition receives disproportionate traffic.
- **Scatter-gather query:** a query must contact many or all partitions.
- **Skew:** uneven data or traffic distribution.
- **Expensive repartitioning:** changing a key can require data movement and operational work.

Examples: - DynamoDB uses a partition key and optional sort key; skewed partition-key values can throttle a hot key. - Cassandra distributes partitions by partition key; very large partitions and hot keys are dangerous. - MongoDB sharding requires selecting a shard key that balances distribution and query targeting. - Elasticsearch distributes index shards across nodes; shard sizing and count affect memory, search fan-out, and recovery. - Redis Cluster maps keys to hash slots and distributes slots across cluster nodes; multi-key operations have slot-related constraints. - Neo4j deployment and scaling options depend on edition and architecture; do not assume graph traversals shard like key-value lookups.

### 5.3 Replication

**Replication** maintains copies of data on multiple nodes or locations. It can improve read capacity, availability, and recovery from node failure, but requires a policy for ordering, acknowledgements, lag, and conflicting writes.

- **Leader/follower:** writes typically go to a leader and are copied to followers.
- **Multi-leader:** multiple nodes can accept writes; conflict handling becomes important.
- **Leaderless/quorum-oriented:** reads and writes may contact multiple replicas according to configured consistency rules.

Replication is not the same as backup. Accidental deletes or corrupted writes can replicate; backups and restore testing remain necessary. Replication also does not guarantee that every read immediately sees the latest write.

Topic 02 develops CAP, PACELC, consistency models, quorums, and conflict resolution. For this lesson, remember that consistency and availability are product- and configuration-dependent—not labels to guess from a family name.

## 6. Family comparison matrix

Use this as the required one-page reference. “Typical failure/design risk” is a common risk, not a claim that every product has the same failure mode.

| Family              | Data model                                                                          | Scaling pattern                                                             | Consistency considerations                                                                     | Query capabilities                                                                            | Good workloads                                                  | Typical failure/design risk                                                               |
|---------------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| Key-value           | Key → value/item; some products expose rich structures                              | Hash/partition-based distribution; replication varies                       | Product-specific durability, conditional writes, replica behavior                              | Strong for key access; secondary queries vary widely                                          | Sessions, carts, counters, caches, direct lookups               | Hot keys, cache staleness/eviction, key design that blocks needed queries                 |
| Document            | Nested documents                                                                    | Replica sets and optional sharding in MongoDB; details are product-specific | Per-document atomicity is common in MongoDB; multi-document transactions exist with trade-offs | Field predicates, indexes, arrays, aggregations; joins are possible but not the default model | Product catalogues, content, profiles, nested aggregates        | Schema drift, unbounded arrays, duplicated facts, missing indexes                         |
| Wide-column         | Partitioned rows / column families, clustering or sparse cells depending on product | Designed for distributed partitions and horizontal capacity                 | Tunable/product-specific; replica lag and repair/maintenance matter                            | Query-first access, partition/range queries; limited arbitrary joins                          | Telemetry, event histories, high-write workloads                | Hot or unbounded partitions, tombstone/compaction issues, access-pattern mismatch         |
| Search              | Indexed documents and inverted indexes                                              | Index shards and replicas across nodes                                      | Often near-real-time rather than immediate visibility; source and index can diverge            | Full-text relevance, filters, facets, aggregations                                            | Site search, logs, security events                              | Mapping/analyzer mistakes, excessive shards, stale index, expensive reindexing            |
| Graph               | Nodes, edges, properties                                                            | Deployment-specific; scaling and traversal behavior vary                    | Product-specific transaction and cluster guarantees                                            | Pattern matching and multi-hop traversal                                                      | Fraud networks, recommendations, dependencies, knowledge graphs | Unbounded traversals, poor graph model, using it for workloads that are simpler elsewhere |
| Relational baseline | Tables, constraints, relationships                                                  | Scale-up, replicas, partitioning; distributed options exist                 | Mature ACID transactions; exact guarantees depend on configuration                             | SQL joins, ad-hoc queries, constraints, reporting                                             | Orders, ledgers, operational CRUD, reporting                    | Under-indexing, contention, poor query plans, scaling beyond chosen architecture          |

## 7. Polyglot persistence: more than one store

**Polyglot persistence** means using multiple database technologies in one system because different workloads benefit from different models.

Example:

``` text
                       ┌────────────────────┐
Customer / API writes ─► PostgreSQL         │  system of record
                       └─────────┬──────────┘
                                 │ CDC / events / projection job
                    ┌────────────┼──────────────┐
                    ▼            ▼              ▼
                 Redis       Search index    Analytics lakehouse
              cache/session  relevance       history and reporting
```

The source of truth remains explicit. Other stores may be caches, search projections, graph projections, or serving indexes.

**Benefits** - Each store can be optimized for its dominant workload. - Search, caching, or graph traversal need not burden the transactional database. - Different read paths can scale independently.

**Costs** - **Synchronization:** updates must propagate; consumers can fail or lag. - **Consistency:** the source and projections may temporarily disagree. - **Operations:** more services, deployments, monitoring, backups, security policies, and on-call knowledge. - **Data governance:** access control, deletion, retention, lineage, and schema changes must apply across stores. - **Rebuildability:** teams need a reliable way to recreate derived stores from the source or event history. - **Failure handling:** retries, deduplication, idempotency, dead-letter handling, and reconciliation are required.

Do not add a database because it is fashionable. Add one when a measured or clearly justified workload need outweighs the synchronization and operational cost.

## 8. When relational is the better answer

A relational database—often PostgreSQL—is usually the starting point when the application needs several of the following:

- joins across related entities;
- ad-hoc queries that are not fully known in advance;
- constraints and referential integrity;
- multi-row transactions;
- financial or inventory invariants;
- reporting and aggregations across many dimensions;
- one source of truth with understandable operational ownership.

Relational databases can scale substantially. A single well-designed PostgreSQL deployment with indexes, connection pooling, read replicas where appropriate, partitioning when justified, and query tuning can handle many workloads without adding distributed-system complexity. If one node eventually becomes a limit, measure and evaluate options rather than assuming NoSQL was required from day one.

### 8.1 PostgreSQL with JSONB

`JSONB` stores JSON data in a decomposed binary format that PostgreSQL can query and index. It is useful when some attributes are nested or vary by record while the system still benefits from SQL, transactions, joins, and constraints.

Illustrative table:

``` sql
CREATE TABLE products (
    product_id  text PRIMARY KEY,
    category    text NOT NULL,
    price       numeric(12, 2) NOT NULL CHECK (price >= 0),
    attributes  jsonb NOT NULL DEFAULT '{}'::jsonb,
    description text NOT NULL
);

CREATE INDEX products_category_price_idx
    ON products (category, price);

CREATE INDEX products_attributes_gin_idx
    ON products USING gin (attributes);
```

Example query:

``` sql
SELECT product_id, category, price, attributes
FROM products
WHERE category = 'outerwear'
  AND price BETWEEN 50 AND 150
  AND attributes @> '{"waterproof": true}'::jsonb
ORDER BY price;
```

This demonstrates structured columns plus flexible attributes. PostgreSQL also supports JSONB operators and GIN indexes; choose indexes based on the actual query shapes and validate plans with `EXPLAIN (ANALYZE, BUFFERS)` against representative data.

**Limits to understand:** - JSONB does not make every nested query free; indexing and query plans still matter. - A GIN index can speed supported predicates but adds storage and write cost. - Full-text search exists in PostgreSQL, but its relevance tooling, language analysis, fuzzy matching, and search operations may not match a dedicated search engine’s requirements. - JSONB is not a substitute for a relational model when fields require strong constraints, joins, or transaction semantics. - Use ordinary typed columns for important, frequently filtered fields when that is clearer and more efficient.

### 8.2 PostgreSQL sufficiency test

Ask:

1.  Can the required queries be expressed clearly in SQL?
2.  Can the workload meet latency and throughput targets on a reasonable PostgreSQL design?
3.  Are joins, constraints, and multi-row transactions important?
4.  Is full-text search, graph traversal, or massive partitioned write throughput a core requirement—or merely a future possibility?
5.  Can the team operate the simpler architecture reliably?

If PostgreSQL meets requirements, it is often the lower-complexity choice. If one workload does not fit, consider adding a specialized **derived** store for that workload while keeping authoritative data in a system of record.

## 9. Advanced awareness: other approaches to scale

These concepts are intentionally awareness-level here. The aim is to recognize the architecture category and know when to investigate further.

### 9.1 NewSQL / distributed SQL

**Distributed SQL** systems aim to provide SQL and relational semantics while distributing data and transaction processing across nodes. “NewSQL” is a historical umbrella term often used for this goal; definitions vary.

Examples: - **Google Spanner:** globally distributed relational database with strong consistency and externally consistent transactions, using Google’s infrastructure and time/consensus design. - **CockroachDB:** distributed SQL database designed for resilient, horizontally scaled relational workloads. - **TiDB:** distributed SQL system with MySQL compatibility, separating SQL processing from distributed storage architecture. - **YugabyteDB:** distributed SQL database with PostgreSQL-compatible YSQL and a distributed storage layer.

These systems are an alternative to some NoSQL choices when the application needs relational queries and transactions across distributed infrastructure. They are not automatically cheaper or simpler: distributed transactions, network latency, operational constraints, compatibility, and workload-specific tuning still matter. Evaluate actual guarantees and deployment topology rather than assuming all products behave identically.

### 9.2 Multi-model databases and convergence

The boundaries between database families are increasingly blurred:

- **Azure Cosmos DB** offers multiple APIs and data-model approaches within a managed globally distributed database service. API compatibility does not mean all APIs share identical semantics or performance.
- **MongoDB** has added search and vector-search capabilities in its ecosystem, reducing the need for a separate system for some applications. Feature availability depends on product/deployment.
- **PostgreSQL extensions** can add capabilities such as full-text search, geospatial processing (PostGIS), and vector operations (for example, pgvector). Extensions expand the toolkit but do not erase the operational and performance trade-offs of a specialized engine.

A product may support several models without being equally good at every workload. Compare the required operations, consistency, operational constraints, costs, and portability.

### 9.3 Vector databases and vector search — awareness only

A **vector embedding** is a numerical representation of an item, such as text or an image, where geometric similarity can approximate semantic similarity. **Vector search** retrieves vectors close to a query vector, often using approximate nearest-neighbor indexes, sometimes combined with keyword filters or hybrid ranking.

Common use cases include semantic retrieval, recommendations, and retrieval-augmented generation (RAG). Dedicated vector databases and vector features in existing systems are options. The right choice depends on scale, filtering, freshness, recall/latency targets, metadata needs, and operational integration.

This is an awareness bridge to **Module 2.22**; do not turn Topic 01 into a vector-index algorithms course. First learn the database-family decision framework in this lesson.

## 10. The data engineer’s perspective: operational stores are source systems

An operational database is often the system where an application creates or updates its current state. A data engineer may need to move that data into a warehouse or lakehouse for historical analysis, feature engineering, governance, or reporting.

The extraction design depends on the source:

- **Snapshot/full extract:** read a point-in-time or bounded dataset. Simple but potentially expensive and may miss changes unless coordinated with a watermark or snapshot boundary.
- **Incremental query:** extract records based on a trustworthy update timestamp or sequence. Requires handling late updates, deletes, timestamp precision, and overlapping windows.
- **Change data capture (CDC):** capture inserts, updates, and deletes from a database change log or supported change stream. Semantics and availability differ by product.
- **Native change streams:** MongoDB change streams and DynamoDB Streams expose changes through product-specific mechanisms and retention/ordering guarantees.
- **Search index export:** search stores may be derived and refreshed asynchronously; pagination strategy and index mutation can complicate a consistent export.
- **Cache extraction:** a cache may be incomplete, evicted, or stale and should not automatically be treated as a source of truth.
- **Wide-column scans:** token/range scans or connectors may be needed; query-first schemas can make arbitrary analytical extraction costly.
- **Graph extraction:** relationship and node data may need to be exported separately while preserving identifiers and relationship semantics.

Before designing an extractor, document:

1.  What is authoritative, and what is derived?
2.  Which changes must be captured—insert, update, delete, schema change?
3.  What ordering and consistency guarantees are available?
4.  How long are change events retained, and what happens if the consumer is offline longer?
5.  Can the extractor resume from a durable checkpoint?
6.  Is processing idempotent? Can duplicate events be safely merged?
7.  How are deletes represented downstream?
8.  How will backfills and reconciliation repair gaps?
9.  What limits exist on throughput, pagination, API rate, or query fan-out?
10. How will credentials, network access, and least privilege be managed?

Topic 09 develops reliable incremental ingestion into the lakehouse. The key lesson now is architectural: **source selection and extraction strategy are connected decisions**. A specialized serving store may improve the application while creating a separate pipeline responsibility.

## 11. Decision framework

Use this sequence when selecting a store.

``` text
Start with requirements and access patterns
                 │
                 ▼
Are joins, constraints, ad-hoc SQL, or multi-row
transactions central to correctness?
          ┌──────┴──────┐
         Yes            No / not dominant
          │                  │
          ▼                  ▼
Start with relational   Identify dominant operation
(PostgreSQL is a        │
strong default)        ├─ direct key lookup/state ─► key-value
                       ├─ nested aggregate records ─► document
                       ├─ high-write partitioned events ─► wide-column
                       ├─ full-text relevance/facets ─► search
                       └─ multi-hop relationships ─► graph
                                  │
                                  ▼
Can the existing relational system meet measured SLOs?
             ┌──────────────────┴──────────────────┐
            Yes                                    No
             │                                      │
             ▼                                      ▼
Prefer simpler architecture              Prototype specialized/derived store
                                                     │
                                                     ▼
                          Design synchronization, recovery, security,
                          retention, observability, and lakehouse extraction
```

### Decision checklist

- **Workload:** What are the top reads/writes, filters, sorts, joins, and aggregations?
- **Scale:** What are present and forecast volume, throughput, data growth, and skew?
- **Latency:** What are p50/p95/p99 targets and expected concurrency?
- **Correctness:** What consistency and transaction guarantees are required?
- **Data shape:** Are records nested, relational, graph-like, or text-heavy?
- **Operations:** Can the team deploy, monitor, back up, restore, secure, and upgrade the system?
- **Cost:** Include compute, storage, indexes, replicas, data transfer, licenses, and staff time.
- **Integration:** How will the source be extracted into analytics? Are deletes and schema changes visible?
- **Failure recovery:** How is data restored or a derived index rebuilt?
- **Exit strategy:** Can the system and data be migrated if requirements change?

Do not select a database on a single benchmark or a vendor’s “fastest” claim. Build a representative workload, measure the required operations, and record the assumptions.

## 12. Twelve scenario decisions

These are reasoned starting points, not universal answers. “Would PostgreSQL alone be sufficient?” assumes a competently designed PostgreSQL system and ordinary application scale unless the scenario explicitly requires specialized behavior. A specialized store may still be justified by measured requirements.

| Scenario              | Initial recommendation                                                                                                                      | Why                                                                                                                  | Would PostgreSQL alone be sufficient?                                                                                                                                                                                  |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1\. Shopping cart     | PostgreSQL for transactional carts; Redis may cache ephemeral cart state; DynamoDB is an option for key-oriented serverless access          | Cart updates, item quantities, ownership, and checkout invariants can require transactions; fast key lookup may help | **Often yes.** Start with PostgreSQL if transaction consistency and simplicity dominate. Add cache only after measuring; do not let a disposable cache become the only durable cart record without an explicit design. |
| 2\. Product catalogue | PostgreSQL with typed columns and JSONB, or MongoDB for document-centric product aggregates                                                 | Products have shared fields plus category-specific nested attributes; search may be a separate projection            | **Often yes.** PostgreSQL JSONB can handle varying attributes. Add MongoDB if document access/modeling and scale justify it; add search for advanced relevance rather than assuming JSONB is inadequate.               |
| 3\. IoT telemetry     | Cassandra or HBase for very high-volume distributed writes; PostgreSQL partitioning or a time-series extension may work at moderate scale   | Device/time queries and sustained ingest favor time-bucketed partitions                                              | **Sometimes.** PostgreSQL can be sufficient for modest throughput, retention, and query scope. Validate ingestion rate, storage growth, retention, and p99 latency before moving to wide-column.                       |
| 4\. Chat history      | PostgreSQL for ordinary conversations; document or wide-column store for high-scale message timelines with predictable access               | Need ordering, conversation membership, pagination, and often transactional metadata                                 | **Often yes.** Relational constraints and query flexibility are useful. Specialized stores become attractive at large message volume or when the access pattern and availability goals demand them.                    |
| 5\. Social graph      | Neo4j for multi-hop relationship traversal; PostgreSQL adjacency tables for simpler graph queries                                           | Friends-of-friends, path finding, and relationship-centric questions can involve repeated joins/traversals           | **Sometimes.** PostgreSQL is enough for direct relationships and bounded joins. Graph database value grows when multi-hop traversal is frequent and central.                                                           |
| 6\. Site search       | Elasticsearch/OpenSearch as a derived search index; PostgreSQL full-text search for simpler needs                                           | Relevance, analyzers, facets, synonyms, and search operations are the core workload                                  | **Sometimes.** PostgreSQL can serve modest search with simpler ranking. A dedicated search engine is appropriate when relevance features, scale, and operational needs warrant it.                                     |
| 7\. Leaderboard       | Redis sorted sets for frequent ranking updates and top-N reads; PostgreSQL for durable history/reporting                                    | Sorted sets support score updates and ordered range reads efficiently                                                | **Often yes at modest scale**, but high-frequency real-time rankings may justify Redis. If Redis is used, decide how scores are persisted/rebuilt and what happens on eviction or failover.                            |
| 8\. Audit log         | Append-only relational table or durable event/log platform; wide-column/object storage at high volume                                       | Audit data requires retention, traceability, controlled mutation, and efficient time/entity retrieval                | **Often yes at moderate volume**, with append-only permissions, retention, and indexing. Regulatory immutability, very high ingest, or long-term analytics may require additional controls/stores.                     |
| 9\. Session store     | Redis for low-latency ephemeral sessions; durable database if sessions must survive cache loss                                              | TTL and key lookup fit the key-value model                                                                           | **Yes technically**, but it may be operationally unnecessary or slower for ephemeral high-volume sessions. PostgreSQL can work when scale is modest and avoiding another service matters.                              |
| 10\. Recommendations  | Relational/analytical platform for offline feature generation; graph or vector search for specific online similarity/relationship retrieval | “Recommendations” may mean offline ranking, collaborative filtering, graph traversal, or semantic similarity         | **Often sufficient for the baseline and offline data.** PostgreSQL alone may not meet low-latency, high-scale graph/vector serving needs. Specify the recommendation algorithm and serving SLO before choosing.        |
| 11\. Ledger           | PostgreSQL or another relational database with ACID transactions, constraints, and carefully designed immutable entries                     | Balances and transfers require strong invariants, transactional updates, reconciliation, and auditability            | **Usually the preferred starting point.** A generic key-value store is not a substitute for transactional ledger correctness. Distributed SQL may be evaluated for multi-region relational requirements.               |
| 12\. User profiles    | PostgreSQL with JSONB or MongoDB                                                                                                            | Profile fields can be partly structured and evolve; relationships and uniqueness may still matter                    | **Often yes.** PostgreSQL with typed identity fields and JSONB attributes is a strong default. Choose document storage if the document access pattern and operational needs provide a clear advantage.                 |

### Scenario exercise instructions

For each scenario, write a short decision record with:

1.  Primary access patterns and write patterns.
2.  Data volume and latency assumptions.
3.  Consistency and transaction requirements.
4.  Initial store and why it fits.
5.  Whether PostgreSQL alone is sufficient under your assumptions.
6.  What evidence would cause you to change the decision.
7.  Extraction method and whether the chosen store is authoritative or derived.

**Evaluation criteria:** recommendations must follow the workload; PostgreSQL sufficiency must be justified rather than answered reflexively; trade-offs and assumptions must be explicit; no database should be selected solely because it is “NoSQL” or “scalable.”

## 13. Hands-on lab: `experiments/01_families/`

### Objective

Store the same **10,000 products** in PostgreSQL using JSONB, MongoDB, and Redis. Implement the same three logical operations in all three stores:

1.  Get one product by ID.
2.  Find products by category and price range.
3.  Search product text.

Compare implementation effort and measured speed using a repeatable protocol. **Do not invent or assume benchmark results.** Your report should contain measurements you actually collect, or explicitly say a measurement has not been run.

### 13.1 Suggested directory layout

``` text
experiments/
└── 01_families/
    ├── README.md
    ├── pyproject.toml
    ├── docker-compose.yml
    ├── data/
    │   └── generate_products.py
    ├── src/
    │   ├── load_postgres.py
    │   ├── load_mongodb.py
    │   ├── load_redis.py
    │   ├── queries_postgres.py
    │   ├── queries_mongodb.py
    │   ├── queries_redis.py
    │   └── benchmark.py
    ├── results/
    │   ├── raw-results.csv
    │   └── report.md
    └── tests/
        └── test_query_equivalence.py
```

You may adapt the structure, but keep the dataset, load process, query definitions, and results reproducible.

### 13.2 Dataset contract

Generate exactly 10,000 products with stable IDs and fields such as:

``` json
{
  "product_id": "p-000001",
  "name": "Waterproof Hiking Jacket",
  "category": "outerwear",
  "price": 89.50,
  "price_cents": 8950,
  "description": "Lightweight waterproof jacket for hiking",
  "attributes": {"waterproof": true, "weight_grams": 620},
  "updated_at": "2026-01-01T00:00:00Z"
}
```

Use a fixed random seed so repeated runs produce the same records. Use a documented distribution for category and price. Validate that every backend receives the same logical dataset. Use UTC timestamps and numeric prices; do not store some prices as strings. Keep `price_cents` as the canonical integer used to build Redis sorted-set scores; derive the decimal `price` for SQL/document queries.

Reference deterministic generator (`data/generate_products.py`):

``` python
import json
import random
from pathlib import Path

SEED = 20261019
COUNT = 10_000
CATEGORIES = ["outerwear", "footwear", "equipment", "accessories", "electronics"]
NAMES = [
    "Waterproof Hiking Jacket", "Trail Running Shoes", "Insulated Bottle",
    "Compact Camping Lantern", "Lightweight Backpack", "Wireless Headlamp",
    "Waterproof Trail Pants", "Hiking Socks", "Portable Power Bank",
    "Weatherproof Tent",
]
PHRASES = [
    "lightweight waterproof gear for hiking",
    "durable equipment for outdoor travel",
    "compact design for camping and trail use",
    "breathable material for everyday adventures",
    "reliable accessory for hiking and travel",
]


def main() -> None:
    rng = random.Random(SEED)
    output = Path("data/products.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        for i in range(1, COUNT + 1):
            price_cents = rng.randint(500, 50_000)
            row = {
                "product_id": f"p-{i:06d}",
                "name": rng.choice(NAMES),
                "category": rng.choice(CATEGORIES),
                "price": price_cents / 100,
                "price_cents": price_cents,
                "description": rng.choice(PHRASES),
                "attributes": {
                    "waterproof": bool(rng.getrandbits(1)),
                    "weight_grams": rng.randint(100, 5000),
                },
                "updated_at": "2026-01-01T00:00:00Z",
            }
            stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"Wrote {COUNT:,} products to {output}; seed={SEED}")


if __name__ == "__main__":
    main()
```

Run it from the `experiments/01_families/` directory with `python data/generate_products.py`. The fixed seed and ID sequence make records repeatable. The category and price distributions are intentionally simple for a learning lab, not representative of a real catalogue. Loaders should map `price_cents` to integer cents for Redis scores and map `price` to PostgreSQL `numeric(12,2)` / MongoDB numeric values. Record the generator version/seed with benchmark results.

### 13.3 PostgreSQL schema and queries

Example schema:

``` sql
CREATE TABLE products (
    product_id text PRIMARY KEY,
    name text NOT NULL,
    category text NOT NULL,
    price numeric(12, 2) NOT NULL CHECK (price >= 0),
    description text NOT NULL,
    attributes jsonb NOT NULL,
    updated_at timestamptz NOT NULL
);

CREATE INDEX products_category_price_id_idx
    ON products (category, price, product_id);

CREATE INDEX products_text_idx
    ON products USING gin (
        to_tsvector('english', name || ' ' || description)
    );
```

**Operation A — lookup by ID**

``` sql
SELECT product_id, name, category, price, description, attributes
FROM products
WHERE product_id = 'p-000001';
```

**Operation B — category and price range**

``` sql
SELECT product_id, name, category, price
FROM products
WHERE category = 'outerwear'
  AND price BETWEEN 50 AND 150
ORDER BY price, product_id;
```

**Operation C — text search**

``` sql
SELECT product_id, name, ts_rank(
    to_tsvector('english', name || ' ' || description),
    plainto_tsquery('english', 'waterproof hiking')
) AS rank
FROM products
WHERE to_tsvector('english', name || ' ' || description)
      @@ plainto_tsquery('english', 'waterproof hiking')
ORDER BY rank DESC, product_id
LIMIT 20;
```

These queries use PostgreSQL full-text search. The expression index must match the indexed expression closely enough for the planner to use it. Verify with `EXPLAIN`; do not assume an index is used just because it exists.

### 13.4 MongoDB collection and queries

Use a `products` collection where each product is a document. Recommended indexes:

``` javascript
db.products.createIndex({ product_id: 1 }, { unique: true });
db.products.createIndex({ category: 1, price: 1, product_id: 1 });
db.products.createIndex({ name: "text", description: "text" });
```

**Operation A — lookup by ID**

``` javascript
db.products.findOne({ product_id: "p-000001" });
```

**Operation B — category and price range**

``` javascript
db.products.find(
  { category: "outerwear", price: { $gte: 50, $lte: 150 } },
  { _id: 0, product_id: 1, name: 1, category: 1, price: 1 }
).sort({ price: 1, product_id: 1 });
```

**Operation C — text search**

``` javascript
db.products.find(
  { $text: { $search: "waterproof hiking" } },
  { score: { $meta: "textScore" }, product_id: 1, name: 1 }
).sort({ score: { $meta: "textScore" } }).limit(20);
```

MongoDB text indexes and PostgreSQL full-text search do not use identical analyzers or ranking algorithms, and the example queries are not semantically identical: MongoDB `$text` treats unquoted terms as an OR by default, while PostgreSQL `plainto_tsquery` joins surviving terms with AND. Therefore, compare result overlap and relevance explicitly; do not label latency as an apples-to-apples comparison unless you normalize the query semantics. MongoDB self-managed text indexes also allow only one text index per collection, and the text index does not accelerate sorting. Atlas Search is a separate capability with deployment-specific availability; do not confuse its `$search` aggregation stage with the `$text` operator. For advanced relevance requirements, Topic 07’s dedicated search-engine lesson is the next step.

### 13.5 Redis representation and queries

Redis is primarily a key-value/data-structure store, not a general document query engine. To make the comparison fair, state the representation and any secondary-index structures explicitly.

A simple baseline representation is: - `product:<product_id>` → JSON-serialized product; - `products:category:<category>` → a sorted set where members are product IDs and scores are integer price cents; - a text-search implementation must be specified. Redis core alone does **not** provide a general full-text search query over arbitrary JSON values. For full-text search, either use the Redis Search capability available in your chosen Redis distribution/deployment (verify module/edition/version and index syntax first) or implement a deliberately limited application-side inverted index for the experiment.

**Operation A — lookup by ID (Python, redis-py)**

``` python
import json
import redis

client = redis.Redis.from_url(
    "redis://localhost:6379/0",
    decode_responses=True,
)

raw = client.get("product:p-000001")
product = json.loads(raw) if raw is not None else None
```

This assumes the loader wrote each product JSON to the corresponding key.

**Operation B — category and price range with a sorted set**

``` python
product_ids = client.zrange(
    "products:category:outerwear",
    5000,
    15000,
    byscore=True,
)
```

The loader must add each product ID to the category sorted set with its price expressed as integer cents, for example `ZADD products:category:outerwear 8950 p-000001` for a price of 89.50. Convert with a documented decimal-safe rule (for example, parse the canonical two-decimal price and multiply by 100) rather than storing a binary floating-point price directly as the score. Fetch each returned product by key to obtain fields. `ZRANGE ... BYSCORE` is the modern form available since Redis 6.2; `ZRANGEBYSCORE` remains a compatibility option but is deprecated in current Redis documentation. Redis orders equal-score members lexicographically, which matches the `product_id` tie-break only if IDs use the same canonical representation. Normalize results before comparing backends.

**Operation C — text search**

Choose and document one of these paths:

- **Redis Search enabled:** define an index over product documents and run a full-text query with filters as appropriate. Exact commands depend on the Redis Search version and deployment; record the version and index schema.
- **Core Redis only:** create an application-managed inverted index, such as token → set of product IDs, then intersect candidate sets for a simple AND-token query. This is an educational approximation, not equivalent to a production search engine: stemming, phrase search, scoring, synonyms, typo tolerance, tokenization rules, and index lifecycle are absent unless you implement them. Ensure every insert/update/delete updates both the product key and inverted index; otherwise results become stale. The custom AND-token behavior also differs from MongoDB `$text`'s default OR behavior, so define a common query contract before judging result equivalence.

Do not compare Redis key lookup to a search-engine query and claim the result proves Redis is universally faster. The data structures and query capabilities differ.

### 13.6 Correctness before speed

Before benchmarking, verify each of the following:

- Each backend contains exactly 10,000 products.
- IDs are unique and identical across stores.
- ID lookup returns the same logical product.
- Category/range queries return the same product IDs and ordering after normalization.
- Text search uses the same query terms and a documented interpretation. PostgreSQL `plainto_tsquery` defaults to AND semantics while MongoDB `$text` defaults to OR semantics, so record result-set differences or normalize the comparison contract rather than asserting exact equality.
- Missing IDs and empty search results are handled.
- Loaders can be rerun safely or clean up previous data.
- Index creation and warm-up are documented.

Search result sets may differ because analyzers and ranking algorithms differ. In that case, report the difference and define a fair comparison (for example, exact set overlap, top-20 overlap, or relevance judgments on a small labelled query set) rather than pretending semantics are identical.

### 13.7 Implementation-effort comparison

Before measuring latency, compare the amount of modelling and application work required. This is a qualitative hypothesis to test—not a benchmark result.

| Operation                          | PostgreSQL JSONB                                                              | MongoDB                                                                         | Redis core                                                                                                                                                                         |
|------------------------------------|-------------------------------------------------------------------------------|---------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Get product by ID                  | Primary key and one SQL query; low implementation effort                      | Unique index and `findOne`; low effort                                          | Direct `GET`; very low effort once the key convention is defined                                                                                                                   |
| Category + price range             | Composite B-tree and SQL predicate; low-to-moderate effort                    | Compound index and filter/sort; low-to-moderate effort                          | Maintain category sorted sets and fetch product keys; moderate effort because secondary structures must be kept consistent                                                         |
| Text search                        | Full-text configuration, expression/index, and ranking query; moderate effort | Text index and `$text`; moderate effort, with product-specific search semantics | Redis Search requires index setup; core Redis requires application-managed tokenization, inverted indexes, updates, and ranking, so effort is high for a meaningful implementation |
| Cross-entity ad-hoc query          | SQL joins and aggregation are natural                                         | Possible, but modelling and aggregation choices matter                          | Usually requires application-side joins or denormalized structures; high effort                                                                                                    |
| Data consistency across structures | One transaction can update product and relational indexes                     | Document update and indexes are maintained by the database                      | Loader/application must update the product key and all secondary structures coherently; partial failures need handling                                                             |

Record the actual implementation time, number of database-specific structures, lines of query/application code, and complexity of keeping indexes correct. Keep the comparison honest: Redis Search is a different capability from Redis core, and a custom inverted index is a teaching exercise rather than a feature-equivalent substitute for a mature search engine.

### 13.8 Measurement protocol

Record the following rather than inventing numbers:

- software and version (PostgreSQL, MongoDB, Redis and Redis Search if used);
- machine/container CPU and memory limits;
- storage and persistence configuration;
- index definitions;
- data loading time and whether index creation is included;
- client library versions and network topology;
- number of warm-up iterations and measured repetitions;
- concurrency and request mix;
- p50, p95, and p99 latency where sample size supports them;
- throughput, errors, and result correctness;
- memory and storage footprint where measurable.

Use the same client location, query inputs, concurrency, and timing method where practical. Separate cold-start and warmed runs. Do not compare one store on a local socket and another over a remote network without noting it. A tiny dataset of 10,000 products is a learning experiment, not proof of behavior at billions of records.

Suggested results table (fill with actual measurements):

| Backend          | Operation      | Index/structure                       | p50 ms | p95 ms | p99 ms | Throughput req/s | Correctness notes    |
|------------------|----------------|---------------------------------------|-------:|-------:|-------:|-----------------:|----------------------|
| PostgreSQL JSONB | ID lookup      | Primary key                           |      — |      — |      — |                — | Not measured yet     |
| MongoDB          | ID lookup      | Unique product ID index               |      — |      — |      — |                — | Not measured yet     |
| Redis            | ID lookup      | Direct key                            |      — |      — |      — |                — | Not measured yet     |
| PostgreSQL JSONB | Category/price | Composite B-tree                      |      — |      — |      — |                — | Not measured yet     |
| MongoDB          | Category/price | Compound index                        |      — |      — |      — |                — | Not measured yet     |
| Redis            | Category/price | Category sorted set                   |      — |      — |      — |                — | Not measured yet     |
| PostgreSQL JSONB | Text search    | GIN full-text expression index        |      — |      — |      — |                — | Not measured yet     |
| MongoDB          | Text search    | Text index                            |      — |      — |      — |                — | Not measured yet     |
| Redis            | Text search    | Redis Search or custom inverted index |      — |      — |      — |                — | State implementation |

### 13.9 Show one easy query and one painful query

Document both examples with the exact query and the structures needed.

- **Easy in a relational store:** an ad-hoc join, such as products joined to suppliers and inventory, with filters not anticipated when designing the schema. PostgreSQL expresses this naturally in SQL. Redis core would require the application to fetch and combine multiple keys or maintain denormalized indexes.
- **Easy in a key-value store:** direct retrieval of one known product key. Redis `GET` is straightforward. A relational database can also do this efficiently with a primary-key index, so the experiment should measure rather than claim it is impossible in SQL.
- **Potentially painful in Redis core:** full-text search over arbitrary descriptions without Redis Search or an application-managed inverted index. Adding the index makes the query possible but shifts indexing, tokenization, consistency, and ranking work to the application.

A good report explains *why* a query fits one model and what extra indexes, denormalization, or application code the other model needs.

### 13.10 Deliverables and evaluation rubric

Submit: 1. Runnable loaders and query functions for all three backends. 2. A shared deterministic data generator. 3. Tests proving dataset and query-result equivalence where semantics allow. 4. Benchmark script and raw results; if not run, mark results as unmeasured. 5. A one-page comparison matrix. 6. A one-page team decision guide. 7. A short conclusion with trade-offs and limitations.

| Criterion               | Weight | Evidence of success                                                                             |
|-------------------------|-------:|-------------------------------------------------------------------------------------------------|
| Dataset reproducibility |    15% | Exactly 10,000 stable product IDs; fixed seed; equivalent records                               |
| Query correctness       |    25% | Three operations implemented or precisely specified; tests cover boundaries and missing records |
| Fair comparison         |    20% | Versions/configuration recorded; same inputs; no invented results; limitations stated           |
| Data-model explanation  |    15% | Explains indexes, Redis secondary structures, and search semantic differences                   |
| Decision guide          |    15% | Recommendations follow access patterns, not popularity                                          |
| Engineering quality     |    10% | Clear setup instructions, repeatable loading, safe configuration, readable results              |

### 13.11 One-page decision guide template

Fill this in after the experiment:

- **Default store:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
- **Primary access patterns:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
- **Required consistency/transaction guarantees:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
- **Measured bottleneck (if any):** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
- **Why PostgreSQL alone is / is not sufficient:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
- **Specialized store and exact responsibility (if any):** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
- **Source of truth:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
- **How derived data is synchronized and rebuilt:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
- **Extraction path into the lakehouse:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
- **Operational and cost risks:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
- **Evidence that would trigger redesign:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

## 14. Common mistakes and trade-offs

1.  **Choosing NoSQL just because the system might scale.** Start with measured workload requirements and a baseline.
2.  **Treating “schemaless” as “designless.”** Define field types, contracts, validation, versioning, and migration.
3.  **Using one store for every access pattern.** One store may be enough, but specialized workloads sometimes merit a derived store.
4.  **Ignoring joins and transactions.** These are often central to correctness, not merely convenience.
5.  **Assuming all NoSQL systems scale the same way.** Redis, MongoDB, Cassandra, Elasticsearch, and Neo4j have different data placement and query semantics.
6.  **Confusing replication with backup.** Replicated mistakes are still mistakes.
7.  **Assuming horizontal scaling is automatic.** Bad partition keys, skew, hot keys, and scatter-gather queries can defeat it.
8.  **Adding polyglot persistence without a synchronization plan.** Define source of truth, retries, idempotency, reconciliation, deletion, and rebuild.
9.  **Treating a search index as the system of record.** Search indexes are often derived and near-real-time, not transactionally identical to source data.
10. **Ignoring extraction constraints.** A store optimized for online access may not support cheap, consistent full scans or indefinite change replay.
11. **Comparing benchmarks without matching semantics.** A key lookup, SQL full-text query, MongoDB text search, and Redis token lookup may not perform equivalent work.
12. **Assuming a product feature means every deployment supports it.** Check edition, service, version, configuration, and API semantics.

## 15. Practice questions

Answer in your own words before checking the checkpoints.

1.  Why is “NoSQL means no SQL” an incomplete description?
2.  Name the five families and one representative system for each.
3.  What is the difference between schema-on-write and schema-on-read?
4.  Why is a schemaless document still governed by a schema in practice?
5.  Which family is a natural starting point for full-text relevance, and why is it often a derived store?
6.  Explain vertical scaling versus horizontal scaling.
7.  What is a shard/partition key, and how can a poor key create a hot partition?
8.  Why is replication not a backup strategy?
9.  Define polyglot persistence and name three costs beyond database licensing.
10. When would PostgreSQL plus JSONB be preferable to MongoDB?
11. Why might PostgreSQL full-text search be enough for one application but insufficient for another?
12. What is distributed SQL trying to combine?
13. What is vector search used for, and why is it only an awareness topic here?
14. Why does a data engineer need to know whether a database is authoritative or derived?
15. What can go wrong if a CDC consumer is offline longer than the source’s change-retention window?

### Scenario-based reasoning

For each prompt, state the access pattern, candidate family, PostgreSQL sufficiency, and the main risk.

- A dashboard needs a top-100 live leaderboard updated thousands of times per second.
- An accounting workflow transfers value between two accounts and must never create money through a partial update.
- A support team searches logs by phrase, time, service, and severity.
- A sensor fleet writes billions of readings with queries constrained by device and time bucket.
- A product manager adds new product attributes every month but still needs joins to suppliers and inventory.
- A fraud analyst follows relationships across accounts, devices, addresses, and payments for several hops.
- A data pipeline must ingest updates and deletes from an operational store into a lakehouse.

There can be more than one defensible answer. Credit depends on the assumptions and trade-offs, not matching a memorized vendor name.

## 16. Roadmap-aligned checkpoints

Do not move to Topic 02 until you can complete all four syllabus checkpoints:

- [ ] **Name the five NoSQL families and one example of each.** Key-value—Redis or DynamoDB; document—MongoDB; wide-column—Cassandra or HBase; search—Elasticsearch/OpenSearch; graph—Neo4j.
- [ ] **Choose a family from an access-pattern list.** Explain which query operations dominate and what the proposed store makes easy.
- [ ] **Explain polyglot persistence and its synchronization cost.** Identify the system of record, derived stores, propagation path, lag, retries, reconciliation, and rebuild strategy.
- [ ] **Say when relational is the better answer.** Explain the role of joins, ad-hoc queries, multi-row transactions, constraints, reporting, and PostgreSQL JSONB.

Also verify that you have completed: - \[ \] All twelve scenario decisions with a justified PostgreSQL-alone assessment. - \[ \] The one-page family comparison matrix. - \[ \] The `experiments/01_families/` plan or implementation for PostgreSQL JSONB, MongoDB, and Redis. - \[ \] All three operations: ID lookup, category/price range, and text search. - \[ \] A fair comparison of implementation effort and measured speed—or explicit “not measured” status. - \[ \] One example of a query easy in one model and difficult in another. - \[ \] A one-page team decision guide. - \[ \] A source-system extraction note preparing for Topic 09.

## 17. Final self-assessment

Rate each item from 0 to 2: **0** = cannot explain; **1** = can explain with notes; **2** = can explain and defend a design choice.

| Skill                                                                                 | Score (0–2) |
|---------------------------------------------------------------------------------------|------------:|
| Explain why NoSQL families emerged without claiming relational databases are obsolete |             |
| Distinguish all five families and representative systems                              |             |
| Explain schema-on-write, schema-on-read, and application contracts                    |             |
| Match data models to access patterns                                                  |             |
| Explain scale-up, scale-out, partitioning/sharding, and replication                   |             |
| Explain polyglot persistence and synchronization/recovery costs                       |             |
| Decide when PostgreSQL/JSONB is sufficient                                            |             |
| Recognize distributed SQL, multi-model, and vector-search options at awareness level  |             |
| Explain how operational-store properties affect lakehouse extraction                  |             |
| Complete the twelve scenarios and experiment plan without fabricated claims           |             |
| **Total (maximum 20)**                                                                |             |

Suggested interpretation: - **0–10:** Revisit fundamentals and redo the scenario exercise. - **11–15:** Good conceptual base; strengthen weak areas and finish the lab. - **16–20:** Ready for Topic 02 if you can defend your choices aloud and identify the assumptions that would change them.

## Documentation and version notes

The examples are teaching patterns, not a promise that every server version or managed deployment exposes identical features. Check the exact product/version before using them in production. Useful primary references include the [PostgreSQL JSON types and JSONB indexing documentation](https://www.postgresql.org/docs/current/datatype-json.html), [PostgreSQL full-text search controls](https://www.postgresql.org/docs/current/textsearch-controls.html), [MongoDB `$text` behavior](https://www.mongodb.com/docs/manual/reference/operator/query/text/), [MongoDB text-index restrictions](https://www.mongodb.com/docs/manual/core/indexes/index-types/index-text/text-index-restrictions/), and [Redis `ZRANGE` documentation](https://redis.io/docs/latest/commands/zrange/). These references support the specific examples; they do not replace workload testing or deployment-specific review.

## Summary

NoSQL is a family of different models, not a single technology or a universal replacement for SQL. Key-value stores optimize key-oriented operations; document stores group nested records; wide-column systems target partitioned high-throughput workloads; search engines index text and rank results; graph databases make relationships first-class. Their strengths depend on access patterns, data placement, consistency requirements, and operations.

Start with the simplest database that satisfies correctness and performance requirements. PostgreSQL—with ordinary relational modelling and JSONB where useful—covers many applications. Add a specialized store only when its workload advantage justifies synchronization, operational, governance, and extraction costs. As a data engineer, always ask not only “How does the application query this?” but also “How will we capture, validate, recover, and deliver its changes to the lakehouse?”

**Next lesson:** `02-cap-theorem-and-consistency-models.md` — formalize distributed consistency and the failure trade-offs introduced here.
