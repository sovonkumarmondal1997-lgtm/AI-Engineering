# Roadmap — Module 2.22: Serving Data for Analytics, ML, and AI

This is the learning roadmap for the twenty-second and final module of
Stage 2, **Python for Data Engineering**. It tells you **what** to learn
about serving data to its consumers, **in what order**, **how** to learn
each topic, and **how to prove to yourself** that you have learned it
before you finish the stage.

Everything in Stage 2 so far moved data **into** the platform and made it
correct, fast, governed, and affordable. But data only creates value when
it reaches someone who uses it: a product feature calling an API, a
dashboard showing a metric the whole company agrees on, a machine-learning
model trained on the right features and fed the same features in
production, or an AI assistant retrieving the right document at the right
moment.

This module covers the **last mile**: data services and APIs, fast
aggregates and caches, semantic layers that make metrics consistent,
feature stores that hand data to ML safely, and embedding and vector
pipelines that feed AI applications. It is also the bridge to the next
stages of this curriculum — Applied AI and Agentic AI engineering — where
these serving layers become the foundation for models and agents.

---

## 1. Module outcome

By the end of this module you will be able to:

- Build secure, fast, well-tested **data APIs with FastAPI**: pagination,
  filtering, streaming large results, authentication, and observability.
- Serve **pre-computed aggregates** with the right storage and **caching**
  strategy, with explicit freshness guarantees and safe invalidation.
- Define **metrics once** in a **semantic layer** and serve them
  consistently to BI tools, APIs, and AI assistants.
- Build **feature pipelines** and use a **feature store** for
  point-in-time-correct training data and low-latency online features,
  avoiding leakage and training–serving skew.
- Build **embedding and vector pipelines** — ingestion, chunking,
  embedding, indexing, incremental updates, deletion, access control, and
  retrieval evaluation — ready for retrieval-augmented generation.
- Choose the right serving pattern for each consumer and connect it to the
  platform's quality, governance, and cost controls.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.21. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Local networking and ports | Stage 0 | Running services locally |
| Type hints, dataclasses, pure functions, layered design | Stage 1 — Modules 1.6 and 1.8 | Service structure and models |
| Reverse ETL, consumers, SLAs, data products | Stage 2 — Module 2.1 | Why and how data is served |
| DuckDB, Arrow, zero-copy interop | Stage 2 — Module 2.4 | Embedded serving and Arrow responses |
| Nested and semi-structured data, legacy formats | Stage 2 — Module 2.5 | Document ingestion for embeddings |
| SQL, indexes, keyset pagination, materialised views | Stage 2 — Module 2.6 | Query design behind APIs |
| Connection pools, SQL injection prevention | Stage 2 — Module 2.7 | Safe, efficient database access from services |
| Dimensional models, OBT, ML feature tables and leakage | Stage 2 — Module 2.8 | What semantic layers and feature stores sit on |
| HTTP semantics, auth, pagination, rate limits, webhooks (client side) | Stage 2 — Module 2.9 | The same rules, now on the server side |
| asyncio, bounded concurrency, locks | Stage 2 — Module 2.10 | Async endpoints and cache stampede protection |
| Pydantic, contracts, drift monitors | Stage 2 — Module 2.11 | API models, ML data contracts, feature drift |
| Incremental processing, hashing, dbt | Stage 2 — Module 2.12 | Incremental re-embedding and metric models |
| Asset-based scheduling | Stage 2 — Module 2.13 | Cache invalidation and materialisation triggers |
| Time travel and versioned tables | Stage 2 — Module 2.15 | Reproducible training datasets |
| Kafka, CDC, stateful streaming | Stage 2 — Module 2.16 | Streaming features and incremental vector updates |
| Containers, CI/CD, secrets | Stage 2 — Module 2.18 | Deploying services |
| Testing strategy | Stage 2 — Module 2.19 | Testing APIs, metrics, and retrieval |
| Observability, catalogs, PII, access control, erasure | Stage 2 — Module 2.20 | Governed serving |
| Estimation, Ray Data, benchmarking, cost | Stage 2 — Module 2.21 | Batch embedding, load testing, and serving cost |

**Tools needed:**

- Python 3.12+ in a `uv` project: `uv add fastapi uvicorn pydantic httpx
  "psycopg[binary,pool]" duckdb pyarrow redis feast sentence-transformers
  opentelemetry-sdk` (plus `dbt-metricflow` or a Cube deployment for the
  semantic layer).
- Docker services: PostgreSQL **with the `pgvector` extension**, a
  Redis-compatible cache (Redis or Valkey), a semantic-layer server (e.g.
  Cube) if you choose that option, and optionally a dedicated vector
  database (e.g. Qdrant) for comparison.
- A load-testing tool (e.g. Locust or k6).
- Your gold tables, dbt project, lakehouse, streaming stack, and
  observability from earlier modules.
- An embedding model: a small open-source model running locally is enough;
  hosted embedding APIs are optional (mind cost, rate limits, and data
  privacy).

**A note on change:** semantic-layer, feature-store, and vector-database
tooling is evolving quickly (new open standards, licence changes, and new
products each year). Learn the patterns here; check each tool's current
documentation and licence before adopting it.

---

## 3. How the module is organised

The five topics are grouped into three phases. Work through them **in
order**.

```text
Phase A — Serving Data to Applications               (Basics → Intermediate)
  01 FastAPI data services
  02 Serving aggregates and caching layers

Phase B — Serving Consistent Meaning                 (Intermediate → Advanced)
  03 Semantic layers and metric definitions

Phase C — Serving ML and AI                          (Advanced)
  04 Feature stores and ML handoff
  05 Embedding and vector data pipelines

Consolidate
  practice-questions.md
  Module mini-project: the platform's serving layer
```

The dependency chain:

```text
01 ──────► 02 ──────► 03 ──────► 04 ──────► 05
expose     make it    make it    serve      serve
data       fast       mean the   features   knowledge
safely     & fresh    same thing to models  to AI
                      everywhere
```

Why this order:

- A data API (01) is the basic serving mechanism; caching and
  pre-aggregation (02) make it fast enough for real traffic.
- A semantic layer (03) sits between gold tables and every consumer,
  ensuring APIs, dashboards, and AI assistants compute metrics the same
  way.
- Feature stores (04) are serving layers specialised for ML, with strict
  time correctness.
- Vector pipelines (05) are the newest and most complex serving layer and
  combine ingestion, incremental processing, APIs, access control, and
  evaluation from everything before.

---

## 4. Suggested schedule

About **4 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — FastAPI data services · Topic 02 — aggregates and caching |
| 2 | Topic 03 — semantic layers and metrics |
| 3 | Topic 04 — feature stores · Topic 05 — embeddings and vectors (part 1: pipeline) |
| 4 | Topic 05 — (part 2: indexing, retrieval, evaluation) · practice questions · mini-project · Stage 2 review |

---

## 5. How to study every topic (the serving loop)

```text
Read → Name the consumer and its contract → Design the serving path
→ Build it → Secure it → Test it → Load it → Observe it
→ Change the data underneath → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Name the consumer** (an app, a dashboard, an analyst, a model, an AI
   assistant) and write its **serving contract**: shape, latency, freshness,
   availability, access rules, and cost limits.
3. **Design the serving path** from gold data to the consumer: storage,
   pre-computation, caching, and interface.
4. **Build it** with the topic's tools.
5. **Secure it**: authentication, authorisation, row/column rules, no PII
   leaks (Module 2.20).
6. **Test it**: unit, integration, contract, and correctness tests (Module
   2.19).
7. **Load it**: measure latency percentiles and throughput under realistic
   traffic (Module 2.21).
8. **Observe it**: metrics, traces, freshness, and error rates (Module
   2.20).
9. **Change the data underneath** (a pipeline publishes new data, a schema
   evolves, a record is deleted) and confirm consumers see correct,
   consistent results.
10. **Write down** what you learned in `module-2.22-notes.md`.
11. **Explain aloud** the full path from source to consumer.

Keep one `serving/` project:

```text
serving/
├── api/            # FastAPI application(s)
├── cache/          # caching and invalidation logic
├── semantic/       # semantic-layer definitions (metrics as code)
├── features/       # feature definitions and feature-store repository
├── vectors/        # ingestion, chunking, embedding, indexing, retrieval
├── loadtests/      # load-testing scripts
└── tests/
```

---

## 6. Phase A — Serving Data to Applications (Basics → Intermediate)

### Topic 01 — [FastAPI data services](01-fastapi-data-services.md)

**Why it comes first:** Applications, partners, and internal tools should
not connect directly to your warehouse or lakehouse. A data API provides a
stable contract, security, performance control, and observability.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | FastAPI essentials: path and query parameters, request and response models with Pydantic (Module 2.11), status codes, and automatic OpenAPI documentation |
| Basics | Running with an ASGI server (uvicorn); project structure (routers, services, repositories) |
| Basics | Why a data API instead of direct database access: stable contracts, security, caching, and protecting the underlying systems |
| Intermediate | **Dependency injection** for settings, database pools, and the current user; **lifespan** events for creating and closing pools (Module 2.7) |
| Intermediate | **Sync vs async endpoints**: when async helps (I/O-bound, async drivers) and when blocking calls must run in threads (Module 2.10) |
| Intermediate | **Server-side pagination** (keyset/cursor — the server side of Module 2.9), filtering, and sorting with **allowlists** and parameterised queries (Module 2.7) |
| Intermediate | **Authentication and authorisation**: API keys and OAuth2 bearer tokens (JWT validation); applying row- and column-level rules per caller (Module 2.20) |
| Intermediate | Errors: consistent error bodies, validation errors, and never leaking internal details or SQL |
| Advanced | **Large results**: streaming responses (NDJSON, CSV), Arrow or Parquet downloads, and asynchronous export jobs (the `202` pattern from Module 2.9, now as the provider) |
| Advanced | Protecting the service and its data stores: timeouts, rate limiting, request size limits, and query cost limits |
| Advanced | HTTP caching on the server side: `ETag` and `Cache-Control` headers based on data versions |
| Advanced | API versioning and deprecation; publishing the OpenAPI schema as a contract (Module 2.11) |
| Advanced | Observability (OpenTelemetry instrumentation, Module 2.20), testing with a test client and async HTTP client (Module 2.19), and deployment in containers with several workers (Module 2.18) |
| Advanced | Alternatives and complements: GraphQL, gRPC, Arrow Flight for high-throughput columnar transfer, and reverse ETL (Module 2.1) — awareness |

**How to learn it**

1. Read the topic file.
2. Write a serving contract for an "orders API" consumed by a customer
   support tool: endpoints, fields, filters, latency, freshness, and access
   rules.
3. Build it, then read the generated OpenAPI documentation as if you were
   the consumer.

**Hands-on exercise — `api/`**

1. Build an orders and customers API over PostgreSQL gold tables with a
   pooled async driver: list endpoints with keyset pagination, allowlisted
   filters and sorting, and detail endpoints.
2. Add OAuth2 bearer authentication (with a local token issuer) and apply
   row-level rules (regional users see their region) and column masking for
   PII.
3. Add a streaming NDJSON export and an asynchronous Parquet export job
   that writes to object storage and returns a presigned URL (Module 2.17).
4. Add `ETag` support based on the gold table's version and return `304`
   when unchanged.
5. Add rate limiting, timeouts, structured errors, and OpenTelemetry
   tracing.
6. Test with unit tests (dependencies overridden), integration tests
   against Testcontainers, and a contract test of the OpenAPI schema; run a
   load test and record p50/p95/p99 latency.

**Checkpoint — you are ready to move on when you can:**

- [ ] Build FastAPI services with Pydantic models and dependency
      injection.
- [ ] Paginate, filter, and sort safely on the server side.
- [ ] Authenticate callers and enforce row and column rules.
- [ ] Stream or export large results without exhausting memory.
- [ ] Test, observe, and load-test a data API.

**Common mistakes:** exposing raw SQL or table names; `OFFSET` pagination
on large tables; blocking database calls inside async endpoints; a new
database connection per request; returning PII by default.

---

### Topic 02 — [Serving aggregates and caching layers](02-serving-aggregates-and-caching-layers.md)

**Why here:** A dashboard or product page cannot wait for a warehouse to
scan billions of rows on every request. Pre-computed aggregates and caches
deliver fast answers — as long as they stay correct and fresh.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Latency needs by consumer: product features (milliseconds), dashboards (sub-second to seconds), analysts (seconds to minutes) |
| Basics | **Pre-aggregation**: rollup tables, summary tables, and materialised views in gold, built by pipelines (Module 2.12) |
| Basics | Caching basics: cache hits and misses, time-to-live (TTL), and a Redis-compatible key-value store |
| Intermediate | **Choosing serving storage**: PostgreSQL with indexes for point lookups, embedded DuckDB files for read-only analytical serving, key-value stores for precomputed results, and real-time analytical databases (e.g. ClickHouse, Druid, Pinot) — awareness and trade-offs |
| Intermediate | **Caching patterns**: cache-aside, read-through, write-through, and refresh-ahead |
| Intermediate | **Cache keys**: including parameters, the caller's access scope (never serve one user's cached data to another), and the **data version** |
| Intermediate | **Invalidation**: TTLs vs event-driven invalidation when a pipeline publishes new data (asset events from Module 2.13) |
| Intermediate | **Freshness contracts**: returning `as_of` timestamps and data versions with every response; serving stale data knowingly |
| Advanced | **Cache stampedes**: request coalescing, locks, early refresh, and jittered expiry (Module 2.10) |
| Advanced | Multi-level caching: in-process, shared cache, HTTP/CDN, and warehouse result caches (Module 2.17) |
| Advanced | Consistency: avoiding mixed versions across related responses (e.g. totals and breakdowns from different refreshes) |
| Advanced | Capacity and cost: cache memory sizing, hit-rate targets, and comparing cache cost with warehouse query cost (Module 2.21) |
| Advanced | Awareness of the Redis ecosystem's licensing changes and compatible open-source alternatives |

**How to learn it**

1. Read the topic file.
2. For five endpoints or dashboards, decide pre-aggregation, cache, direct
   query, or a combination, and write the freshness contract for each.
3. Load-test one endpoint with no cache, a TTL cache, and an event-invalidated
   cache; compare latency, load on the database, and staleness.

**Hands-on exercise — `cache/` and gold rollups**

1. Build rollup tables (daily and monthly revenue by country, category, and
   channel) as part of your gold pipeline, and a read-only DuckDB file
   published for serving.
2. Add a cache-aside layer to your metrics endpoints with keys that include
   parameters, caller scope, and data version.
3. Invalidate or version the cache when the gold asset is republished
   (orchestrator event or version bump) and prove no stale mixing occurs.
4. Implement stampede protection and demonstrate it under a burst of
   identical requests after expiry.
5. Return `as_of` and `data_version` in every response.
6. Measure hit rate, latency percentiles, and database load before and
   after.

**Checkpoint:**

- [ ] Choose serving storage and pre-aggregation for a latency target.
- [ ] Implement cache-aside with correct, scoped, versioned keys.
- [ ] Invalidate caches on data publication.
- [ ] Prevent cache stampedes.
- [ ] Communicate freshness to consumers.

**Common mistakes:** cache keys that ignore user permissions; TTLs so long
that dashboards contradict each other; no invalidation after backfills;
caching errors; caching everything instead of pre-aggregating once.

---

## 7. Phase B — Serving Consistent Meaning (Intermediate → Advanced)

### Topic 03 — [Semantic layers and metric definitions](03-semantic-layers-and-metric-definitions.md)

**Why here:** When "revenue" is computed differently in five dashboards, an
API, and a notebook, trust collapses. A semantic layer defines each metric
**once**, in code, and serves it consistently to every consumer —
including AI assistants that answer questions in natural language.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The problem: duplicated, inconsistent metric logic across BI tools, SQL, and code |
| Basics | What a semantic layer is: a governed layer between modelled data (Module 2.8) and consumers that defines entities, dimensions, measures, and metrics |
| Basics | Building blocks: **entities** (join keys), **dimensions** (group-by attributes, including time with grains), **measures** (aggregations), and **metrics** built from measures |
| Intermediate | Metric types: simple, ratio (numerator and denominator aggregated separately — Module 2.6's ratio lesson), cumulative/running, derived, and period-over-period |
| Intermediate | The join graph: how the layer generates correct joins and avoids fan-out (Modules 2.6 and 2.8) |
| Intermediate | Tools and approaches: the dbt Semantic Layer with MetricFlow, Cube, and BI-tool modelling languages — awareness of each; emerging open standards for exchanging semantic definitions |
| Intermediate | **Metrics as code**: definitions in Git, reviewed like any code, with owners and descriptions linked to the business glossary (Module 2.20) |
| Advanced | **Testing metrics**: known answers on fixed data, metric regression bounds (Module 2.19), and reconciliation with finance-approved figures (Module 2.11) |
| Advanced | Serving interfaces: SQL, REST/GraphQL APIs, and BI integrations; caching and pre-aggregations inside the semantic layer (Topic 02) |
| Advanced | Governance: certified metrics in the catalog, access control on metrics and dimensions (Module 2.20), and deprecation of old definitions |
| Advanced | **Semantic layers for AI**: grounding natural-language and "text-to-metrics" assistants on governed definitions instead of letting a model guess SQL over raw tables |
| Advanced | Limits: ad-hoc exploration, very custom logic, and performance on huge models |

**How to learn it**

1. Read the topic file.
2. Find three places in your platform where revenue or active users are
   computed, and document every difference.
3. Define those metrics once in a semantic layer and make each consumer use
   the definition.

**Hands-on exercise — `semantic/`**

1. Define semantic models on your dbt marts (or in Cube): entities for
   customer, order, and product; time dimensions; measures; and metrics —
   `gross_revenue`, `net_revenue`, `orders`, `average_order_value` (ratio),
   `active_customers`, `revenue_mom_growth`.
2. Query the metrics by time grain and dimensions through the layer's
   interface and compare with your hand-written gold SQL.
3. Write metric tests with known answers on a fixed dataset and add them to
   CI (Module 2.18).
4. Expose certified metrics through your FastAPI service (Topic 01) with
   caching (Topic 02) and publish them to the catalog with owners.
5. Build a small "ask a metric" prototype: a natural-language question is
   mapped to a metric, dimensions, and filters from the semantic layer's
   catalogue (rule-based or with a model), never to free-form SQL.

**Checkpoint:**

- [ ] Explain entities, dimensions, measures, and metrics.
- [ ] Define simple, ratio, cumulative, and derived metrics correctly.
- [ ] Manage and test metrics as code.
- [ ] Serve one metric definition to APIs, BI, and AI consumers.
- [ ] Govern and certify metrics.

**Common mistakes:** averaging ratios; metrics defined in BI tools outside
version control; semantic models that allow fan-out joins; letting AI
assistants write unrestricted SQL instead of using governed metrics.

---

## 8. Phase C — Serving ML and AI (Advanced)

### Topic 04 — [Feature stores and ML handoff](04-feature-stores-and-ml-handoff.md)

**Why here:** Machine-learning models are data consumers with very strict
requirements: training data must reflect only what was known at the time,
and the features used in production must be computed exactly as in
training. Getting this wrong produces models that look excellent offline
and fail in production.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The ML lifecycle and the data engineer's role: features, labels, training datasets, batch and online inference, monitoring |
| Basics | Features, **entities** (customer, product), feature views, and **feature freshness** |
| Basics | **Offline store** (historical features in the lakehouse or warehouse, for training) vs **online store** (latest features in a low-latency store, for inference) |
| Intermediate | **Point-in-time correct joins**: for each training example, use only feature values known before the label's timestamp — preventing **data leakage** (introduced in Module 2.8, implemented here) |
| Intermediate | **Training–serving skew**: different logic, freshness, or defaults between training and serving — and eliminating it by computing features once |
| Intermediate | A feature store in practice with **Feast** (open source): repository configuration, entities, data sources, feature views, historical retrieval for training, **materialisation** from offline to online, and online retrieval |
| Intermediate | Batch feature pipelines (Module 2.12) and **streaming features** (Module 2.16) such as "orders in the last 10 minutes" |
| Advanced | **Reproducible training datasets**: pinning table versions and feature definitions (time travel from Module 2.15), recording them in run metadata |
| Advanced | **The ML handoff contract**: datasets delivered with schema, statistics, lineage, versions, and known limitations; data contracts with the ML team (Module 2.11) |
| Advanced | **Monitoring**: feature freshness, missing values, and **drift** between training and production distributions (drift checks from Module 2.11) |
| Advanced | **Batch inference** pipelines writing predictions back to the lakehouse or warehouse for use by applications (Ray Data from Module 2.21) |
| Advanced | Managed feature stores on data and ML platforms — awareness; when a full feature store is overkill and well-designed feature tables suffice |

**How to learn it**

1. Read the topic file.
2. Build a leaky training dataset on purpose (joining current customer
   attributes to historical labels) and measure how much it inflates model
   accuracy; then build it point-in-time correctly.
3. Draw the offline and online paths of one feature and find every place
   skew could creep in.

**Hands-on exercise — `features/`**

1. Define a churn-prediction use case with labels (customer churned within
   30 days after a date).
2. Create a Feast repository: `customer` entity; batch feature views
   (lifetime orders, days since last order, average order value) from
   lakehouse Parquet; and one streaming-derived feature (orders in the last
   hour) from your Kafka pipeline.
3. Generate a point-in-time-correct training dataset with historical
   retrieval, pinned to table versions, and record it in run metadata.
4. Materialise features to an online store (Redis-compatible) on a
   schedule from your orchestrator.
5. Serve online features through a FastAPI endpoint used by a toy model's
   inference; prove offline and online values match for the same entity and
   time.
6. Add feature freshness and drift monitors and a handoff document for the
   ML team.

**Checkpoint:**

- [ ] Explain offline vs online stores and feature freshness.
- [ ] Build point-in-time-correct training datasets.
- [ ] Explain and prevent training–serving skew.
- [ ] Use Feast for definition, materialisation, and retrieval.
- [ ] Deliver reproducible, documented datasets to ML teams.

**Common mistakes:** joining current feature values to past labels
(leakage); separate feature code for training and serving; unmonitored
online stores serving stale features; training datasets that cannot be
recreated.

---

### Topic 05 — [Embedding and vector data pipelines](05-embedding-and-vector-data-pipelines.md)

**Why last:** AI applications that answer questions over company knowledge
(retrieval-augmented generation, semantic search, agents with memory)
depend on a data pipeline that turns documents into embeddings and serves
the right pieces quickly and safely. Most failures of such applications are
**data** failures: stale documents, bad chunking, missing access rules,
undeleted data, and unmeasured retrieval quality.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What embeddings are: vectors that place similar meanings close together; similarity measures (cosine, dot product, Euclidean distance) |
| Basics | The pipeline: **ingest** documents → **parse** and clean → **chunk** → **embed** → **store and index** with metadata → **retrieve** → serve to an application |
| Basics | Storing vectors in PostgreSQL with **pgvector** and querying nearest neighbours |
| Intermediate | **Ingestion and parsing**: HTML, PDF, office documents, tickets, and database records (Modules 2.5 and 2.9); keeping source ids, URLs, sections, and timestamps |
| Intermediate | **Chunking strategies**: fixed size with overlap, recursive/structure-aware splitting (headings, paragraphs), and semantic chunking — trade-offs in retrieval quality |
| Intermediate | **Metadata** on every chunk: source, section, language, timestamps, content hash, embedding model version, and **access-control attributes** |
| Intermediate | **Generating embeddings at scale**: batching, rate limits and retries for hosted models (Module 2.9), local models, distributed batch embedding (Ray Data, Module 2.21), and cost estimation |
| Intermediate | **Vector indexes**: exact search vs approximate nearest neighbour (e.g. HNSW, IVF); recall vs latency vs memory trade-offs; index build and tuning parameters |
| Intermediate | **Hybrid retrieval**: combining keyword search (BM25/full-text) with vector search, plus metadata filters |
| Advanced | **Incremental updates**: detecting changed documents with CDC or content hashes (Modules 2.9, 2.12, 2.16), re-embedding only changed chunks, and removing chunks of deleted documents |
| Advanced | **Deletion and privacy**: erasure requests must remove vectors and chunks too (Module 2.20); scanning chunks for PII before embedding (Module 2.20) |
| Advanced | **Access control at retrieval time**: filtering by the caller's permissions so the AI never sees documents the user may not read |
| Advanced | **Model versioning and re-embedding migrations**: new models change vector dimensions and meaning; running old and new indexes side by side and switching atomically |
| Advanced | **Retrieval evaluation**: golden question sets, recall@k and ranking metrics, regression tests in CI (Module 2.19), and monitoring retrieval quality and freshness in production |
| Advanced | Choosing storage: pgvector, dedicated vector databases, search engines with vector support, and lakehouse-friendly vector formats — trade-offs in scale, filtering, operations, and cost |
| Advanced | Serving retrieval through an API (Topic 01) with caching (Topic 02), observability, and cost limits — ready for the Applied AI stage |

**How to learn it**

1. Read the topic file.
2. Pick a document corpus (your platform's documentation and runbooks,
   public product documentation, or synthetic support tickets) and write 50
   real questions with the documents that answer them — your golden set.
3. Try three chunking strategies and two index settings; measure recall@5
   on the golden set for each.

**Hands-on exercise — `vectors/`**

1. Build an ingestion pipeline that parses Markdown/HTML/PDF documents,
   removes boilerplate, scans for PII, chunks by structure with overlap,
   and stores chunks with full metadata (including ACL groups and content
   hashes) in PostgreSQL.
2. Embed chunks in batches with a local open-source model (optionally a
   hosted API with rate limiting); store vectors in `pgvector` with an HNSW
   index.
3. Make the pipeline incremental: re-embed only changed chunks (content
   hash), remove chunks of deleted documents, and run it from your
   orchestrator; for database-sourced records, drive updates from CDC
   events.
4. Build a retrieval API: hybrid search (full-text + vector), metadata
   filters, and permission filtering by the caller's groups; return chunks
   with sources.
5. Evaluate recall@5 and a ranking metric on your golden set; add a CI
   regression test on retrieval quality.
6. Process an erasure request that removes a person's documents and chunks,
   and prove they can no longer be retrieved.
7. Migrate to a different embedding model with a side-by-side index and an
   atomic switch, comparing retrieval quality before switching.

**Checkpoint:**

- [ ] Build an end-to-end embedding pipeline with rich metadata.
- [ ] Choose chunking and indexing strategies from measured retrieval
      quality.
- [ ] Update vector stores incrementally, including deletions.
- [ ] Enforce access control and privacy at retrieval time.
- [ ] Evaluate and regression-test retrieval quality.
- [ ] Migrate embedding models safely.

**Common mistakes:** embedding everything once and never updating it;
chunks without source or permission metadata; deleted documents still
retrievable; no evaluation set, so "it seems to work" is the only test;
mixing vectors from different models in one index.

---

## 9. Consolidate — practice questions

When all five topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Identify the consumer and write its serving contract (shape, latency,
   freshness, availability, access, cost).
2. Design the serving path from gold data (or documents) to the consumer.
3. Decide what is pre-computed, cached, stored in a feature or vector
   store, or queried live.
4. Define correctness: metric definitions, point-in-time rules, retrieval
   quality, or API contracts.
5. Implement, secure, test, and load-test it.
6. Explain what happens when the underlying data changes, is backfilled,
   or is deleted.

---

## 10. Module mini-project — the platform's serving layer

This is the proof that you have finished the module.

**Scenario:** Your platform (Modules 2.9–2.21) now produces trustworthy,
governed data. Four consumers are waiting: a customer-support application,
the company's dashboards, a data-science team building a churn model, and
an AI team building a support assistant.

Build `serving/` with:

1. **Data API** — a FastAPI service with orders and customer endpoints
   (keyset pagination, allowlisted filters, OAuth2, row- and column-level
   rules, streaming and asynchronous exports, ETags, rate limits, tracing).
2. **Aggregates and caching** — gold rollups, a versioned and
   permission-aware cache with event-driven invalidation, stampede
   protection, and `as_of` freshness in every response.
3. **Semantic layer** — certified metric definitions as code, tested in CI,
   served to the API and a BI tool, published in the catalog, and used by a
   governed "ask a metric" prototype.
4. **Feature store** — Feast with batch and streaming features,
   point-in-time-correct training datasets pinned to table versions, online
   materialisation, an online feature endpoint, skew checks, and drift
   monitoring, plus a handoff document.
5. **Vector pipeline** — incremental ingestion of documentation and support
   tickets, PII scanning, structure-aware chunking, embeddings in pgvector,
   hybrid retrieval with permission filtering, erasure support, a golden
   evaluation set with a CI quality gate, and a model-migration procedure.
6. **Operations** — load tests with p95 latency targets, dashboards and
   alerts for API errors, cache hit rates, feature freshness, and retrieval
   quality, containerised deployment through your CI/CD, and serving cost
   per 1,000 requests.

**Grading yourself:** every consumer has a written serving contract that
is met under load; the same metric returns the same number in every
interface; training datasets are reproducible and leak-free, and online
features match offline ones; retrieval respects permissions and deletions
and meets its quality threshold; and all of it is observable, tested, and
deployed like the rest of the platform.

---

## 11. Module self-assessment — exit criteria

Tick every box without looking at your notes:

- [ ] I can build secure, tested, observable data APIs with FastAPI.
- [ ] I can serve aggregates quickly with correct caching and freshness
      contracts.
- [ ] I can define, test, govern, and serve metrics through a semantic
      layer.
- [ ] I can build point-in-time-correct feature pipelines and use a feature
      store without training–serving skew.
- [ ] I can build, update, secure, and evaluate embedding and vector
      pipelines.
- [ ] I have finished all practice questions and the mini-project.

---

## 12. Stage 2 wrap-up

This is the last module of **Python for Data Engineering**. Before moving
on:

1. Complete the stage capstone in
   [`../00-Stage-2-Overview/Projects/`](../00-Stage-2-Overview/Projects/) —
   especially the end-to-end data platform capstone, which combines the
   mini-projects of all 22 modules.
2. Review your notes files (`module-2.1-notes.md` to `module-2.22-notes.md`)
   and write a one-page summary of your personal "data engineering
   principles" — the rules you would defend in any design review.
3. Revisit the exit criteria of every module and mark any you can no longer
   tick; repeat those exercises.

The serving layers you built here — governed APIs, consistent metrics,
point-in-time-correct features, and permission-aware vector retrieval — are
exactly the foundations that the **Applied AI** and **Agentic AI** stages
build on. Models and agents are only as good as the data they are given,
and you now know how to give them the right data, at the right time, to
the right people, safely.

---

## 13. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| FastAPI documentation — tutorial, dependencies, security, async, testing, deployment | 01 |
| *Building Data Science Applications with FastAPI*, 2nd edition — François Voron (Packt) | 01, 04 |
| Redis/Valkey documentation — caching patterns and data structures | 02 |
| *Designing Data-Intensive Applications* — Martin Kleppmann, chapters on derived data and caching | 02, 04 |
| dbt Semantic Layer / MetricFlow documentation and Cube documentation | 03 |
| Feast documentation — concepts, point-in-time joins, materialisation, online serving | 04 |
| *Designing Machine Learning Systems* — Chip Huyen (O'Reilly) — features, leakage, training–serving skew, and data distribution shift | 04 |
| pgvector documentation and your chosen vector database's documentation (indexing, filtering, tuning) | 05 |
| *AI Engineering* — Chip Huyen (O'Reilly) — retrieval-augmented generation, evaluation, and data for AI applications | 05 |
| Sentence-transformers documentation and embedding-model benchmark leaderboards (to compare models on your own data, not only public scores) | 05 |

---

## 14. Where this module leads

| This module's idea | Where it goes next |
| --- | --- |
| Retrieval pipelines, vector stores, and evaluation | Applied AI Engineering — retrieval-augmented generation and LLM applications |
| Governed metrics and data APIs as tools | Agentic AI Engineering — agents that call tools and query data safely |
| Feature pipelines and ML handoff | Machine-learning engineering — training, deployment, and monitoring of models |

Serving is where data engineering meets the people and systems it exists
for. The habits you build here — write a contract for every consumer,
define meaning once, keep time correct, respect permissions and deletions
all the way to the last mile, and measure quality where it is used — are
what turn a well-built platform into data that people, models, and agents
can rely on.
