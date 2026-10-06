# Practice Questions — Serving Data for Analytics, ML, and AI

> **Module 2.22 — Stage 2: Python for Data Engineering**

## Overview

This practice set evaluates the production-oriented serving skills taught across FastAPI data services, aggregates and caching, semantic layers, feature stores/ML handoff, and embedding/vector data pipelines. The specification requires exactly 40 questions: 10 Basic, 10 Moderate, 10 Hard, and 10 Advanced. Every question follows **Problem → How to Solve the Problem → Solution → Why This Solution Works → Production Insight**.

### Difficulty progression

- **Basic:** understand → explain → apply
- **Moderate:** apply → implement → debug → compare
- **Hard:** analyze → diagnose → optimize → integrate
- **Advanced:** architect → evaluate → optimize → secure → operate → defend the decision

# Part I — Basic

## Question 01 — Design a Safe FastAPI Data Endpoint

**Difficulty:** Basic

### Problem

A customer-support API must return customer records from PostgreSQL. Product requirements say clients may filter by region and status, but they must not be able to supply arbitrary SQL fragments. Explain how you would design the endpoint.

### How to Solve the Problem

1. Identify the security requirement: user-controlled values must not become SQL syntax.
2. Separate API validation from database access.
3. Use Pydantic request/query models and an allowlist for filterable fields.
4. Use parameterized SQL for values.
5. Keep routing, service, and repository responsibilities separate.
6. Return a stable response contract and safe error body.

### Solution

A suitable design is:

```python
from typing import Literal
from pydantic import BaseModel

class CustomerFilter(BaseModel):
    region: str | None = None
    status: Literal["active", "inactive"] | None = None
```

The repository builds only SQL fragments that come from an explicit server-side allowlist, while actual values are bound as parameters. The endpoint should never concatenate raw client input into SQL.

Conceptually:

```text
FastAPI router
   ↓
Pydantic validation
   ↓
Service layer
   ↓
Repository
   ↓
Parameterized PostgreSQL query
```

Authentication and authorization are separate concerns: validating a filter does not establish that the caller may see every customer row.

### Why This Solution Works

The allowlist controls which query dimensions are legal; parameterized queries control how values enter SQL. Separating router/service/repository responsibilities also makes security and testing easier.

### Production Insight

In production, log the endpoint, latency, query shape, and authorization outcome without logging sensitive customer data or raw credentials. Test malicious inputs explicitly and keep database errors out of client responses.

## Question 02 — Why Keyset Pagination?

**Difficulty:** Basic

### Problem

An orders endpoint currently uses `OFFSET 1000000 LIMIT 100`. The table is large and customers report increasing latency on later pages. Explain a better pagination strategy.

### How to Solve the Problem

1. Identify that deep OFFSET pagination can require the database to walk past many rows.
2. Define a stable ordering, such as `(created_at, order_id)`.
3. Return a cursor containing the last seen ordering values.
4. Query for rows after that cursor.
5. Add an index matching the ordering/filter pattern.

### Solution

Use keyset/cursor pagination:

```sql
SELECT order_id, customer_id, created_at, total_amount
FROM orders
WHERE (created_at, order_id) < (%s, %s)
ORDER BY created_at DESC, order_id DESC
LIMIT %s;
```

The API returns an opaque cursor representing the last row's ordering values. The next request supplies that cursor instead of a large OFFSET.

### Why This Solution Works

The database can seek into an indexed ordering rather than repeatedly processing and discarding a growing prefix. The ordering also needs a deterministic tie-breaker such as `order_id`.

### Production Insight

For production, define cursor semantics, test behavior under concurrent inserts, index the access path, and avoid exposing database-specific cursor details directly to clients.

## Question 03 — Cache-Aside for a Revenue Rollup

**Difficulty:** Basic

### Problem

A dashboard repeatedly requests daily revenue by country. The underlying gold rollup is expensive to query. Explain how cache-aside should work.

### How to Solve the Problem

1. Check the cache first.
2. On a hit, return the cached value.
3. On a miss, query the authoritative rollup.
4. Store the result with a correctly designed key and TTL/version.
5. Return the result.
6. Define what happens when the underlying data is republished.

### Solution

The flow is:

```text
Request
  ↓
Cache lookup
  ├── hit → return
  └── miss
        ↓
      Gold rollup
        ↓
      Cache set
        ↓
      Return
```

A key might encode the metric, dimensions, filters, caller scope where relevant, and data version. TTL alone is not necessarily sufficient when the source can be republished before TTL expiry.

### Why This Solution Works

Cache-aside keeps the source of truth in the database/rollup while using the cache as an acceleration layer. Explicit invalidation or versioned keys can prevent stale values from surviving a publication boundary.

### Production Insight

Do not cache everything. Precompute expensive reusable aggregates first, then cache high-value read paths. Measure hit rate, latency, and database-load reduction.

## Question 04 — Why a Semantic Layer?

**Difficulty:** Basic

### Problem

Finance, BI, and an internal API each calculate `net_revenue` independently and now report different numbers. What problem is a semantic layer intended to solve?

### How to Solve the Problem

1. Identify duplicated metric logic.
2. Define entities, dimensions, measures, and metrics centrally.
3. Put metric definitions under version control.
4. Add ownership, documentation, and tests.
5. Serve the governed metric definition consistently to consumers.

### Solution

A semantic layer provides a governed definition such as:

```text
net_revenue
= gross_revenue - refunds
```

with explicit grain, joins, dimensions, aggregation behavior, ownership, and tests. BI, APIs, and other consumers should reference the same definition instead of independently rewriting SQL.

### Why This Solution Works

Centralizing metric meaning reduces semantic drift. The important distinction is that a semantic layer governs meaning; it does not remove the need for correct underlying data and join design.

### Production Insight

Treat metrics as code: review them in Git, assign owners, document business meaning, test known answers, and define deprecation procedures.

## Question 05 — Point-in-Time Correctness

**Difficulty:** Basic

### Problem

A churn model predicts whether a customer will churn on June 30. An engineer joins today's customer feature value to the June 30 label. What is wrong?

### How to Solve the Problem

1. Identify the label timestamp.
2. Ask what feature values were actually known at that timestamp.
3. Restrict feature history to values available before the label time.
4. Perform a point-in-time join.
5. Test the resulting training dataset for leakage.

### Solution

The join is vulnerable to future-data leakage. Training data should use the feature value that was available at or before the prediction/label cutoff, not the customer's current value.

Conceptually:

```text
feature_history
      ↓
as-of join at label_time
      ↓
training row
```

A feature recorded after June 30 must not contribute to a June 30 training example.

### Why This Solution Works

Point-in-time correctness makes historical training data resemble what the model could actually have known at prediction time. Without it, offline metrics can be unrealistically strong.

### Production Insight

Version the feature definitions and underlying tables where possible, record the training run metadata, and make point-in-time correctness a testable property rather than a manual assumption.

## Question 06 — What Is an Embedding Pipeline?

**Difficulty:** Basic

### Problem

Your company wants an AI support assistant that retrieves relevant policy documents before generating an answer. Describe the data pipeline required before the AI application can retrieve those documents semantically.

### How to Solve the Problem

1. Ingest source documents.
2. Parse and clean them.
3. Split them into meaningful chunks.
4. Attach source and security metadata.
5. Hash content for change detection.
6. Generate embeddings.
7. Store vectors and metadata.
8. Build/search an appropriate vector index.
9. Evaluate retrieval quality.

### Solution

The core flow is:

```text
documents
 → parse/clean
 → chunk
 → metadata
 → content hash
 → embedding
 → vector storage/index
 → retrieval
```

The pipeline must also support incremental updates, deletion, ACL enforcement, evaluation, and observability in production.

### Why This Solution Works

An embedding is only one transformation. Retrieval quality and operational correctness depend heavily on upstream parsing, chunking, metadata, lifecycle, security, and evaluation.

### Production Insight

Treat the vector index as a derived data product. Every vector should be traceable to a source, chunk, embedding-model version, and authorization context.

## Question 07 — Why Store Metadata with Vectors?

**Difficulty:** Basic

### Problem

A vector table contains only an embedding and an internal row ID. The team now needs to show the source URL, restrict results by department, delete one document, and identify which embedding model produced a result. What metadata is missing?

### How to Solve the Problem

Identify metadata required for:
- provenance;
- filtering;
- lifecycle;
- security;
- reproducibility.

At minimum, consider document/chunk identity, source information, ACL attributes, content hash, timestamps, embedding model/version, and index version.

### Solution

A useful chunk record includes:

```text
chunk_id
document_id
source_id
source_url
section
language
updated_at
content_hash
embedding_model_version
index_version
ACL attributes
```

The exact fields can vary, but provenance, lifecycle, security, and model identity must be represented.

### Why This Solution Works

The vector captures numerical similarity; metadata captures what the vector means operationally and whether it may be returned. Without metadata, filtering, deletion, auditing, and migration become unreliable.

### Production Insight

Do not treat metadata as optional decoration. In production it is part of the retrieval data contract and often part of the security boundary.

## Question 08 — Offline and Online Feature Stores

**Difficulty:** Basic

### Problem

A data-science team needs historical feature values to train a churn model and a low-latency feature lookup during online inference. Explain why the two serving patterns are different.

### How to Solve the Problem

1. Separate historical training retrieval from online inference retrieval.
2. Identify the latency and volume requirements for each.
3. Use an offline store for historical/reproducible training retrieval.
4. Materialize appropriate features to an online store for low-latency access.
5. Keep feature definitions aligned to avoid training-serving skew.

### Solution

The offline path is optimized for historical retrieval and reproducibility. The online path is optimized for low-latency point lookups.

```text
Feature computation
       ↓
  ┌────┴────┐
  ↓         ↓
Offline    Online
training   inference
```

The same feature logic should govern both where practical.

### Why This Solution Works

Different access patterns have different storage and latency requirements. Separating them allows efficient training while preserving fast online inference.

### Production Insight

Monitor freshness and online/offline value parity. A feature store is not automatically necessary for every ML workload; simple feature tables can be enough when online serving and lifecycle complexity do not justify it.

## Question 09 — Freshness and `as_of`

**Difficulty:** Basic

### Problem

A dashboard displays a revenue number that was computed yesterday. Product wants consumers to know exactly how current the number is. What should the serving contract expose?

### How to Solve the Problem

1. Identify freshness as part of the data contract.
2. Record the source/serving version or timestamp.
3. Return `as_of` and/or `data_version`.
4. Document the freshness SLA.
5. Decide explicitly whether stale data is acceptable.

### Solution

A response can expose:

```json
{
  "value": 1250000,
  "as_of": "2026-10-05T23:00:00Z",
  "data_version": "gold-2026-10-05-23"
}
```

The service should document how current the value is expected to be and whether stale serving is permitted.

### Why This Solution Works

A number without freshness metadata can be technically correct yet operationally misleading. `as_of` and `data_version` make freshness observable to consumers and simplify cache/invalidation reasoning.

### Production Insight

Freshness should be monitored as an SLA. A cache hit should not silently become a stale-data exception unless the serving contract explicitly allows it.

## Question 10 — Retrieval-Time Authorization

**Difficulty:** Basic

### Problem

An AI support assistant uses vector search over company documents. A user is allowed to see Engineering documents but not Finance documents. Where should the access restriction be enforced?

### How to Solve the Problem

1. Authenticate the caller.
2. Construct the authorization context.
3. Associate ACL attributes with indexed chunks.
4. Apply authorization-aware filtering during retrieval.
5. Test both direct retrieval and cached retrieval paths.

### Solution

The retrieval path should be conceptually:

```text
user
 ↓
authentication
 ↓
authorization context
 ↓
ACL-aware retrieval
 ↓
authorized results
```

Do not rely solely on filtering after unauthorized candidates have already entered application memory or downstream processing.

### Why This Solution Works

Vector similarity does not understand business permissions. Authorization is a separate concern that must be carried into the retrieval operation.

### Production Insight

Test cross-tenant and cross-department access explicitly. Also ensure cache keys include authorization scope so one user's result cannot become another user's cache hit.

# Part II — Moderate

## Question 11 — Implement Keyset Pagination

**Difficulty:** Moderate

### Problem

Implement the core repository query for an orders endpoint that returns 50 rows ordered by `created_at DESC, order_id DESC`. The next page is represented by the last row's `(created_at, order_id)`. Show the SQL and explain the required index.

### How to Solve the Problem

1. Establish a deterministic composite ordering.
2. Use the cursor values in a row-value comparison.
3. Keep the limit parameterized.
4. Add an index aligned with the ordering.
5. Decide how the cursor is encoded at the API boundary.

### Solution

A representative query is:

```sql
SELECT order_id, customer_id, created_at, total_amount
FROM orders
WHERE (created_at, order_id) < (%s, %s)
ORDER BY created_at DESC, order_id DESC
LIMIT %s;
```

A suitable index is conceptually:

```sql
CREATE INDEX idx_orders_created_id
ON orders (created_at DESC, order_id DESC);
```

The exact index can also include columns needed by a frequent filter pattern.

### Why This Solution Works

The composite comparison preserves ordering across duplicate timestamps. The matching index gives PostgreSQL an efficient access path instead of scanning increasingly large OFFSET ranges.

### Production Insight

Test cursor behavior when many rows share the same timestamp and when new orders arrive between requests. Cursor pagination defines a contract; it is not simply a query rewrite.

## Question 12 — Fix an Authorization-Unsafe Cache Key

**Difficulty:** Moderate

### Problem

A revenue API caches responses using `revenue:{country}:{month}`. Users from different authorization scopes can request the same country/month, and one user occasionally receives data they should not see. Diagnose and fix the design.

### How to Solve the Problem

1. Identify that the cache key lacks caller access scope.
2. Determine which authorization dimensions affect the response.
3. Include a stable representation of the authorized scope in the key.
4. Include data version/freshness dimensions when needed.
5. Clear existing unsafe cache entries during rollout.

### Solution

A safer conceptual key is:

```text
metric
+
country
+
month
+
authorization_scope
+
data_version
```

For example:

```text
revenue:US:2026-09:scope-finance:v42
```

The exact scope identifier should be stable and derived from the server-side authorization context, not trusted from an arbitrary client string.

### Why This Solution Works

Two users can send identical query parameters while being entitled to different result sets. Therefore query parameters alone do not define cache identity.

### Production Insight

Treat authorization scope as part of response identity. During remediation, invalidate or namespace old entries so the previously unsafe values cannot continue serving.

## Question 13 — Correct a Ratio Metric

**Difficulty:** Moderate

### Problem

A dashboard defines `average_order_value` as the average of row-level order values after joining orders to order_items. The metric is too high for customers with multiple items. Diagnose the problem and propose a correct semantic definition.

### How to Solve the Problem

1. Identify the grain of `orders` and `order_items`.
2. Detect the one-to-many join fan-out.
3. Avoid averaging a duplicated order-level measure.
4. Define the metric at the correct grain.
5. Test the result against known answers.

### Solution

A robust definition is:

```text
orders = count of distinct orders
revenue = sum(order-level revenue)
average_order_value = aggregate revenue / aggregate orders
```

For example:

```sql
SELECT
    SUM(o.total_amount) / NULLIF(COUNT(DISTINCT o.order_id), 0)
        AS average_order_value
FROM orders o
JOIN order_items i
  ON i.order_id = o.order_id;
```

If the join is not required for the metric, remove it. A semantic layer should represent the correct join graph and grain rather than relying on every consumer to remember the workaround.

### Why This Solution Works

Ratios should normally be calculated from separately aggregated numerator and denominator values. A one-to-many join can duplicate numerator rows and corrupt the result.

### Production Insight

Add known-answer tests and fan-out checks. Metric correctness should be enforced in CI, not discovered when Finance notices a dashboard discrepancy.

## Question 14 — Diagnose Point-in-Time Leakage

**Difficulty:** Moderate

### Problem

A training query joins `customer_features` to churn labels by `customer_id` only. The feature table contains values from multiple dates. Offline AUC is excellent, but production performance is poor. Explain the likely issue and the correct query strategy.

### How to Solve the Problem

1. Compare the label timestamp with feature timestamps.
2. Determine whether future feature values can join to historical labels.
3. Replace the equality-only join with an as-of/point-in-time condition.
4. Ensure each training row receives only information available before the prediction timestamp.
5. Add leakage tests.

### Solution

Conceptually:

```sql
SELECT ...
FROM labels l
JOIN feature_history f
  ON f.customer_id = l.customer_id
 AND f.feature_time <= l.label_time
```

Then select the latest valid feature record for the label timestamp. The exact SQL pattern depends on the database, but the invariant is that future observations cannot be used.

### Why This Solution Works

The original join ignores time, so it can leak future information into historical examples. That inflates offline performance while creating training-serving skew.

### Production Insight

Persist feature timestamps, define the point-in-time contract explicitly, and pin the relevant table/feature versions for reproducibility.

## Question 15 — Incremental Embedding Updates

**Difficulty:** Moderate

### Problem

A knowledge base has 2 million chunks, but only 0.5% change each day. The current pipeline re-embeds every chunk nightly. Design a changed-only workflow.

### How to Solve the Problem

1. Persist a deterministic content hash for each chunk.
2. Compare the new hash with the stored hash.
3. Skip unchanged chunks.
4. Re-embed changed chunks.
5. Reindex changed vectors.
6. Handle deleted chunks separately.
7. Measure the reduction in embedding work.

### Solution

The pipeline becomes:

```text
source
 ↓
parse/chunk
 ↓
content_hash
 ↓
compare
 ├── same → skip
 └── changed → embed → update index
```

At 0.5% change rate:

```text
2,000,000 × 0.005 = 10,000 chunks/day
```

So the changed set is approximately 10,000 rather than 2 million, subject to chunk-boundary effects.

### Why This Solution Works

Content hashing converts unnecessary full reprocessing into incremental processing. The pipeline must still reprocess neighboring chunks if a structural document change alters chunk boundaries.

### Production Insight

Track processed counts and embedding cost before and after the change. Also add idempotency so retries cannot create duplicate vector records.

## Question 16 — Prevent an Async API from Blocking

**Difficulty:** Moderate

### Problem

A FastAPI endpoint is declared `async def`, but p95 latency rises sharply under load. Investigation shows the endpoint uses a blocking database operation and creates a new database connection on every request. Explain the redesign.

### How to Solve the Problem

1. Identify blocking I/O inside an async request path.
2. Replace per-request connection creation with an application-managed pool.
3. Use an async-compatible database path where appropriate.
4. Move genuinely CPU-heavy work away from the event loop.
5. Load-test p50/p95/p99 after the change.

### Solution

Use application lifespan to create/manage a connection pool, inject the pool into request handlers/services, and use the appropriate async database API. The architecture becomes:

```text
FastAPI
  ↓
dependency injection
  ↓
pooled DB access
  ↓
PostgreSQL
```

Do not assume `async def` makes a blocking library asynchronous.

### Why This Solution Works

An async endpoint can still block the event loop if it performs synchronous I/O. A pool also avoids repeated connection setup and limits database concurrency to a controlled level.

### Production Insight

Measure database pool saturation, request latency, errors, and PostgreSQL load. More connections are not automatically better; uncontrolled concurrency can overload the database.

## Question 17 — Prevent a Cache Stampede

**Difficulty:** Moderate

### Problem

A product dashboard cache entry expires at 10:00. Hundreds of requests arrive immediately afterward and all query the warehouse. Explain two techniques to reduce the stampede and when you would use them.

### How to Solve the Problem

1. Recognize synchronized expiration as the trigger.
2. Decide whether requests can share one refresh.
3. Use request coalescing or a distributed lock so one request refreshes the value.
4. Consider early refresh and TTL jitter to spread refresh work.
5. Monitor hit rate and warehouse load.

### Solution

Two useful approaches are:

**Request coalescing:** the first request performs the refresh while other requests wait for the same result.

**TTL jitter:** vary expiration slightly so a large population of keys does not expire at exactly the same moment.

Early refresh can also refresh hot keys before expiration.

### Why This Solution Works

The goal is to prevent many identical misses from producing duplicate expensive work. Locks/coalescing address concurrent refresh; jitter reduces synchronized expiration patterns.

### Production Insight

Use bounded lock/wait behavior and failure handling. Never allow cache protection logic itself to become a single point of outage.

## Question 18 — Build a Retrieval Evaluation Set

**Difficulty:** Moderate

### Problem

Your vector retrieval team says the new embedding model is "better" because a few manually tested queries look good. Design a small evaluation set that can support a defensible comparison.

### How to Solve the Problem

1. Define representative query categories.
2. Record expected relevant documents/chunks.
3. Include paraphrases, exact identifiers, ambiguous queries, and permission-sensitive cases.
4. Run both models against the same set.
5. Calculate Recall@K and appropriate ranking metrics.
6. Compare latency and cost alongside quality.

### Solution

Create a golden dataset with roughly 20–50 representative queries as a practical starting point. For each query, record expected relevant content and, where appropriate, relevance grades. Evaluate Recall@1/5/10 and ranking metrics such as MRR or NDCG when they match the use case.

### Why This Solution Works

A shared golden set converts anecdotal examples into a repeatable regression baseline. Quality should be compared under the same corpus, filters, and evaluation protocol.

### Production Insight

Keep the golden set in the engineering workflow and run it in CI for meaningful retrieval changes. Never present unexecuted metrics as measured results.

## Question 19 — Choose a Serving Store

**Difficulty:** Moderate

### Problem

A team needs to serve a small-to-moderate set of customer aggregates with relational filters and already operates PostgreSQL. Another engineer proposes introducing a dedicated real-time analytical database immediately. How would you evaluate the decision?

### How to Solve the Problem

1. Define latency, throughput, data freshness, query shape, and scale.
2. Check whether PostgreSQL indexes and precomputed rollups can satisfy the contract.
3. Consider DuckDB or another covered serving pattern where appropriate.
4. Compare operational complexity and cost.
5. Benchmark the candidate architecture before adding infrastructure.

### Solution

Start with the simplest store that meets the serving contract. PostgreSQL can serve indexed point lookups and precomputed aggregates effectively for appropriate workloads. A real-time analytical database becomes more compelling when scale, query concurrency, analytical workload shape, or latency requirements exceed the simpler design.

### Why This Solution Works

Adding infrastructure has an operational and cost burden. Technology selection should follow workload requirements, not the perceived sophistication of the tool.

### Production Insight

Record the decision, measured workload assumptions, capacity limits, and trigger conditions for revisiting the architecture.

## Question 20 — Safe Large Export Workflow

**Difficulty:** Moderate

### Problem

An API client requests millions of orders. Returning the entire result in one in-memory JSON response risks exhausting application memory. Design a safer workflow using concepts from the serving module.

### How to Solve the Problem

1. Recognize that the result is too large for ordinary response buffering.
2. Choose streaming or asynchronous export based on the consumer's needs.
3. For very large exports, create an async job and return HTTP 202.
4. Generate the artifact outside the request memory path.
5. Provide a secure download mechanism such as a presigned URL where appropriate.
6. Apply authorization, timeouts, request limits, and observability.

### Solution

A production design can be:

```text
POST /exports
   ↓
validate + authorize
   ↓
202 Accepted + job_id
   ↓
background export
   ↓
Parquet/CSV object
   ↓
short-lived presigned URL
```

For moderately large immediate responses, NDJSON/CSV streaming may be appropriate instead.

### Why This Solution Works

Asynchronous export separates expensive work from request latency and avoids holding millions of records in application memory. Parquet can also be substantially more efficient than JSON for analytical consumers.

### Production Insight

Define export quotas, job expiration, authorization checks on download, status endpoints, failure handling, and cost limits. Never let exports become an unbounded data-exfiltration path.

# Part III — Hard

## Question 21 — Diagnose a p95 API Regression

**Difficulty:** Hard

### Problem

An orders API historically runs at p95 = 250 ms. After a release, p95 becomes 4.2 seconds while p50 remains 300 ms. Database CPU is high and connection-pool wait time is increasing. Diagnose the incident and propose an investigation order.

### How to Solve the Problem

1. Interpret the tail-latency pattern: p50 stable but p95 degraded suggests a concurrency/contention problem rather than universal slowdown.
2. Inspect pool utilization and wait time.
3. Inspect database query latency and concurrency.
4. Compare query plans and request volume with the previous release.
5. Check for N+1 queries, missing indexes, expensive filters, or excessive parallel requests.
6. Mitigate traffic/query pressure while investigating.
7. Validate the fix using load testing.

### Solution

The strongest initial hypothesis is that the release increased expensive database work or concurrency, causing some requests to queue behind database capacity. Investigate:

```text
request rate
 → pool saturation
 → PostgreSQL active queries
 → slow-query traces
 → query plans/indexes
 → code-path differences
```

Do not assume that increasing the pool is the fix. That can make database overload worse.

### Why This Solution Works

p95 exposes queueing and contention that p50 can hide. The correct response correlates application traces, pool metrics, database load, and query-level evidence rather than optimizing one layer in isolation.

### Production Insight

Set p50/p95/p99 SLOs and alert on pool saturation, database latency, and error rates. Load-test releases with realistic concurrency before production rollout.

## Question 22 — Metric, Cache, and Freshness Consistency

**Difficulty:** Hard

### Problem

A semantic-layer metric `net_revenue` is correct in BI, but an API sometimes returns a value that is one data publication behind. The API uses a Redis cache with a 30-minute TTL. Design a correction without duplicating metric logic.

### How to Solve the Problem

1. Keep the semantic layer as the metric source of meaning.
2. Identify the data publication/version boundary.
3. Include `data_version` in the serving response and cache identity.
4. Invalidate or version cache entries when the gold data is republished.
5. Keep TTL as a safety mechanism rather than the only freshness mechanism.
6. Add a reconciliation test between API and BI.

### Solution

The API should resolve the governed `net_revenue` definition, then serve a result associated with the current gold `data_version`.

Conceptually:

```text
semantic metric
      ↓
gold data_version = V43
      ↓
cache key includes V43
      ↓
API response includes as_of + V43
```

When V44 is published, V43 entries become unusable or are explicitly invalidated.

### Why This Solution Works

A fixed TTL expresses time-based freshness, but a data publication is an explicit correctness boundary. Versioned serving lets consumers distinguish stale data from current data and avoids redefining the metric in the API.

### Production Insight

Monitor metric reconciliation, cache hit rate, version lag, and stale-serving frequency. Document whether stale responses are allowed and under what conditions.

## Question 23 — Semantic Layer Fan-Out Incident

**Difficulty:** Hard

### Problem

Finance reports that `gross_revenue` is 12% too high after a new product dimension was added to the semantic model. The query joins orders to order_items and products. Diagnose the likely grain problem and design a correction.

### How to Solve the Problem

1. State the grain of each table.
2. Identify whether the order-level revenue is duplicated by item rows.
3. Determine whether the product dimension is genuinely required.
4. If product-level analysis is required, aggregate order revenue at the appropriate grain before joining or use item-level revenue.
5. Add known-answer and fan-out regression tests.

### Solution

If `orders.total_amount` is joined directly to multiple `order_items`, each order amount can be repeated. For product analysis, a safer model may use item-level revenue as the measure:

```text
order_items
  → product dimension
  → SUM(item_revenue)
```

For order-level revenue, avoid the item join or aggregate the order table to one row per order before joining.

The semantic model must make the join graph and grain explicit.

### Why This Solution Works

Fan-out is a semantic correctness problem, not just a SQL syntax problem. A query can execute successfully while producing materially wrong numbers.

### Production Insight

Require metric owners to define grain, join paths, and known-answer tests. Reconcile important metrics to finance-controlled totals before certifying changes.

## Question 24 — Feature Store Skew Incident

**Difficulty:** Hard

### Problem

A churn model has strong offline validation but poor production results. Investigation shows that the training pipeline computes `orders_last_30d` in one SQL job, while the online service computes it from a different implementation. Explain the failure and redesign the feature path.

### How to Solve the Problem

1. Identify training-serving skew.
2. Compare definitions, windows, timezone handling, defaults, and freshness.
3. Establish a shared feature definition/computation path.
4. Use an offline store for historical retrieval and an online store for low-latency retrieval.
5. Test offline/online parity on the same entities and timestamps.
6. Monitor feature freshness and missingness.

### Solution

The redesign should make the feature definition authoritative and materialize it to both serving modes:

```text
shared feature definition
        ↓
 ┌──────┴──────┐
 ↓             ↓
offline      online
 ↓             ↓
training     inference
```

For historical data, use point-in-time retrieval. For online inference, materialize current features to the online store.

### Why This Solution Works

Using separate feature logic creates silent semantic drift. A feature store is useful when it centralizes definitions, historical retrieval, and online serving sufficiently to reduce this risk.

### Production Insight

Monitor offline/online value parity, freshness, missingness, and drift. If the workload does not require online serving, a well-governed feature table may be simpler than a full feature-store platform.

## Question 25 — Secure Vector Retrieval with Deletion

**Difficulty:** Hard

### Problem

A support assistant has two incidents: users can occasionally retrieve Finance chunks, and a document deleted from the source system remains retrievable for several hours. Design the investigation and remediation.

### How to Solve the Problem

1. Audit chunk metadata for ACL attributes.
2. Verify authorization context reaches retrieval.
3. Check whether filtering happens during candidate selection.
4. Inspect cache keys for authorization scope.
5. Trace the deletion event through source → chunks → vectors → index/cache.
6. Add post-deletion retrieval verification.
7. Add cross-scope security tests.

### Solution

For authorization:

```text
authenticated user
 → authorization context
 → ACL-aware vector/hybrid query
 → authorized top-k
```

For deletion:

```text
delete event
 → identify document
 → delete chunks/vectors
 → update index state
 → invalidate retrieval caches
 → verify zero unauthorized/stale hits
```

The exact index update mechanism depends on the storage system.

### Why This Solution Works

Similarity search does not enforce business permissions, and source deletion does not automatically delete derived vectors. Both security and lifecycle state must propagate through derived data.

### Production Insight

Track deletion lag and authorization failures as operational metrics. Treat a stale sensitive vector as a security incident, not merely a freshness bug.

## Question 26 — ANN Quality vs Latency

**Difficulty:** Hard

### Problem

An exact vector search achieves Recall@10 = 0.98 with p95 latency of 900 ms. An HNSW configuration achieves Recall@10 = 0.91 with p95 latency of 45 ms. Product requires Recall@10 ≥ 0.95 and p95 < 100 ms. What should you do?

### How to Solve the Problem

1. Treat exact search as the quality reference.
2. Reject the current HNSW configuration because it misses the quality target.
3. Tune HNSW parameters and/or retrieval strategy.
4. Benchmark recall, latency, memory, and index build time.
5. Consider hybrid retrieval or candidate/reranking changes if covered by the architecture.
6. Select the first configuration satisfying both hard requirements.

### Solution

The current HNSW result is not acceptable because:

```text
Recall: 0.91 < 0.95
Latency: 45 ms < 100 ms
```

Latency passes, quality fails. Tune the index and rerun the same evaluation set. If no ANN configuration meets the contract, reconsider the retrieval architecture rather than silently accepting degraded quality.

### Why This Solution Works

Performance is a constrained optimization problem. A faster system that violates retrieval quality is not a successful optimization.

### Production Insight

Store benchmark results with index version and dataset version. Never tune against a tiny hand-picked query set and generalize the result to production.

## Question 27 — Cache Stampede Under Load

**Difficulty:** Hard

### Problem

A hot dashboard endpoint has a 60-second TTL. At expiry, 2,000 requests arrive in a short burst. PostgreSQL CPU reaches saturation and API p99 exceeds the SLO. Design a production mitigation.

### How to Solve the Problem

1. Confirm synchronized expiration and duplicate recomputation.
2. Add request coalescing or a distributed refresh lock.
3. Add TTL jitter for large populations of keys.
4. Consider early refresh for very hot keys.
5. Bound waiting and define fallback behavior.
6. Measure cache hit rate, refresh concurrency, DB load, and p99.

### Solution

A suitable strategy is:

```text
request
 ↓
cache
 ├── hit → return
 └── miss
       ↓
   refresh lock
       ↓
 one request computes
       ↓
 shared result
```

Add jitter to reduce synchronized expiry and early refresh to keep high-value keys warm. Use versioned keys/invalidation if data publication requires stronger freshness semantics.

### Why This Solution Works

The root cause is not simply "the database is slow"; it is a thundering herd created by cache expiration. The mitigation prevents duplicated expensive work while preserving a controlled refresh path.

### Production Insight

Load-test cache expiry events explicitly. Monitor refresh concurrency and lock contention, not just ordinary cache hit rate.

## Question 28 — API Export Under Authorization

**Difficulty:** Hard

### Problem

A company exposes an asynchronous Parquet export endpoint. A user requests all orders for a region. The export worker runs outside the request process. Explain how authorization and PII controls must survive the handoff.

### How to Solve the Problem

1. Authenticate and authorize the export request before job creation.
2. Persist the authorized scope with the job, not just the user's display name.
3. Revalidate access when appropriate at execution/download time.
4. Apply row/column restrictions while generating the file.
5. Protect the resulting object and use a short-lived authorized download URL.
6. Audit access without logging sensitive data.

### Solution

The job should carry a server-derived authorization scope:

```text
request
 → authenticate
 → authorize
 → create job(scope=authorized_scope)
 → export only allowed rows/columns
 → private object
 → short-lived presigned URL
```

PII columns should be masked or omitted according to the caller's permissions.

### Why This Solution Works

Asynchronous processing breaks the original request context unless the authorization contract is deliberately persisted. A job ID alone is not an authorization decision.

### Production Insight

Treat export artifacts as sensitive data products with lifecycle/retention rules. Test a user attempting to download another user's completed export.

## Question 29 — Vector Model Migration

**Difficulty:** Hard

### Problem

Your current embedding model uses 768 dimensions. The replacement model uses 1536 dimensions and is expected to improve retrieval quality. Production traffic cannot tolerate an outage. Design a migration.

### How to Solve the Problem

1. Keep v1 serving.
2. Define a versioned model/index contract including dimension and metric.
3. Backfill v2 vectors into a separate index.
4. Run the same golden evaluation set and performance tests.
5. Validate ACL/deletion behavior on v2.
6. Switch a stable serving alias atomically.
7. Monitor and retain v1 for rollback.

### Solution

Use:

```text
v1 model → v1 index → production
v2 model → v2 index → evaluation
                         ↓
                    validation
                         ↓
                    atomic switch
```

Do not mix 768- and 1536-dimensional vectors in an index contract designed for one dimension. Keep model/index metadata explicit.

### Why This Solution Works

Side-by-side migration separates construction risk from serving risk. The atomic switch limits the production change surface, while retaining v1 provides rollback.

### Production Insight

Migration success is not just retrieval quality. Check latency, index size, memory, cost, ACL behavior, deletion behavior, freshness, and operational rollback.

## Question 30 — Capacity Reasoning for Feature Serving

**Difficulty:** Hard

### Problem

An online feature endpoint currently serves 400 requests/second at 20 ms p95. A planned launch is expected to produce 1,200 requests/second. Explain what you would measure and change before launch.

### How to Solve the Problem

1. Establish current capacity under realistic load.
2. Measure p50/p95/p99, throughput, error rate, feature freshness, and online-store latency.
3. Identify the current bottleneck: API workers, connection pool, online store, network, or feature computation.
4. Load-test at and beyond 1,200 RPS.
5. Scale the actual bottleneck and retest.
6. Add capacity headroom and alerting.

### Solution

Do not multiply the current server count blindly. First establish whether the current system scales approximately linearly and which component saturates.

A useful test matrix is:

```text
400 → 600 → 800 → 1,000 → 1,200+ RPS
```

Record p50/p95/p99, throughput, errors, and store latency at each step.

### Why This Solution Works

Capacity is a measured property of the entire serving path. A fast API can still fail if the online feature store or connection pool saturates.

### Production Insight

Set launch thresholds and rollback triggers before the event. Include realistic feature cardinality and concurrent users in load tests.

# Part IV — Advanced

## Question 31 — Design the Unified Enterprise Serving Platform

**Difficulty:** Advanced

### Problem

Design a serving platform for four consumers: customer-support APIs, company dashboards, a churn model, and an AI support assistant. The organization requires one definition of revenue, low-latency customer features, permission-aware document retrieval, freshness visibility, and production observability.

### How to Solve the Problem

1. Identify each consumer's serving contract.
2. Centralize governed metrics in a semantic layer.
3. Precompute/cache aggregates for dashboard/API workloads.
4. Build offline/online feature paths for the churn model only where online serving is required.
5. Build a vector pipeline for the AI assistant with ACL metadata, incremental updates, deletion, and retrieval evaluation.
6. Expose secure APIs around the serving products.
7. Apply shared testing, observability, lineage, freshness, and cost controls.

### Solution

A reference architecture is:

```text
Trusted warehouse/lakehouse/gold data
        ↓
 ┌──────┼───────────────┬──────────────────┐
 ↓      ↓               ↓                  ↓
Semantic Aggregates   Features           Documents
 ↓      ↓               ↓                  ↓
BI/API Cache       Offline/Online      Chunk/Embed
                         ↓                  ↓
                    ML/Inference       Vector Index
                         ↓                  ↓
                         API / Serving Layer
                                  ↓
                           Consumers/AI
```

The semantic layer owns metric meaning; cache/rollups own serving performance; the feature path owns ML data correctness; the vector path owns retrieval infrastructure. Security and observability span all paths.

### Why This Solution Works

A single architecture does not mean a single storage technology. Each consumer has different latency, freshness, and access patterns, while governance keeps definitions and contracts consistent.

### Production Insight

Document the serving contract for every consumer: shape, latency, freshness, availability, access rules, and cost limits. Review the architecture as a set of data products rather than a collection of endpoints.

## Question 32 — Diagnose a Cross-Layer Customer Data Incident

**Difficulty:** Advanced

### Problem

A customer sees stale revenue in the API, the dashboard shows the current number, and an AI assistant cites an old support document. Both API and vector retrieval have healthy cache hit rates. Design a systematic incident investigation.

### How to Solve the Problem

1. Separate the two symptoms: metric freshness and document freshness.
2. Trace each source through its serving pipeline.
3. For revenue, inspect gold publication version, semantic metric version, cache version, and `as_of`.
4. For documents, inspect source update timestamp, ingestion lag, embedding lag, index version, and cache.
5. Compare serving versions rather than assuming cache health means freshness.
6. Identify whether the issue is publication propagation or stale caching.

### Solution

For revenue:

```text
gold data_version
 → semantic serving
 → cache key/version
 → API response
```

For documents:

```text
source updated_at
 → ingestion
 → chunk hash
 → embedding
 → index
 → retrieval
```

A healthy cache hit rate only says the cache is being used; it does not prove the cached value is current.

### Why This Solution Works

Freshness is an end-to-end property. A system can have excellent latency and cache hit rate while serving obsolete data.

### Production Insight

Instrument each stage with version/timestamp metadata and define source-to-serving freshness SLAs. During incidents, correlate those values rather than relying on application timestamps alone.

## Question 33 — Design a Governed 'Ask a Metric' System

**Difficulty:** Advanced

### Problem

Executives want to ask, "What was APAC net revenue last month?" through an AI assistant. They also want to prevent the assistant from generating unrestricted SQL. Design the data-serving architecture.

### How to Solve the Problem

1. Identify the user intent as a governed metric query.
2. Resolve natural language to a certified metric, dimensions, time grain, and filters.
3. Validate the requested entities/joins against the semantic model.
4. Execute the governed semantic query.
5. Apply access controls.
6. Cache/preaggregate where appropriate.
7. Return the metric with freshness/version context and traceability.

### Solution

A safe flow is:

```text
Natural-language question
        ↓
Metric intent parser
        ↓
Certified metric + dimensions + filters
        ↓
Semantic layer
        ↓
Authorized query
        ↓
Cache/preaggregation if appropriate
        ↓
Metric result + as_of/data_version
```

The assistant should map the request to governed semantic objects rather than freely inventing SQL over arbitrary tables.

### Why This Solution Works

The semantic layer constrains meaning and join paths. Unrestricted AI-generated SQL can bypass metric definitions, expose unauthorized data, create expensive queries, and produce inconsistent answers.

### Production Insight

Log the resolved metric/dimensions/filter intent, not sensitive prompt content unnecessarily. Add known-answer tests for representative executive questions and enforce query-cost limits.

## Question 34 — Feature Store Decision: Do You Need One?

**Difficulty:** Advanced

### Problem

A small ML team trains a weekly churn model. Features are generated in a warehouse, predictions are batch-only, and there is no online inference endpoint. An engineer proposes deploying Feast immediately. Decide whether to adopt it and defend the decision.

### How to Solve the Problem

1. Identify actual requirements rather than assuming every ML workload needs a feature store.
2. Confirm batch-only inference and historical training needs.
3. Determine whether feature reuse, point-in-time retrieval, versioning, and governance can be handled with well-designed feature tables.
4. Estimate the operational cost of adding an online feature store.
5. Adopt Feast when its lifecycle/serving capabilities solve real requirements, not merely because it is a standard tool.

### Solution

For the stated workload, a governed feature-table approach may be sufficient:

```text
warehouse feature tables
 → point-in-time training dataset
 → batch inference
 → predictions
```

Feast becomes more compelling when the team needs reusable feature definitions, standardized historical retrieval, online materialization, and low-latency online feature serving.

### Why This Solution Works

A feature store introduces infrastructure and operational complexity. The correct architecture is the simplest one that satisfies correctness, reuse, reproducibility, and serving requirements.

### Production Insight

Document explicit adoption criteria: online latency requirements, number of consumers, feature reuse, freshness, lineage, and operational ownership. Revisit when requirements change.

## Question 35 — Design a Zero-Downtime Vector Migration with Rollback

**Difficulty:** Advanced

### Problem

A production AI assistant uses pgvector/HNSW. The team wants to change both the embedding model and chunking strategy. The new system must maintain ACL enforcement, support deletion, and provide a rollback path. Design the rollout.

### How to Solve the Problem

1. Treat chunking and embedding changes as a coupled retrieval-data migration.
2. Build a new versioned corpus/index alongside production.
3. Preserve source IDs, content hashes, ACL metadata, and deletion state.
4. Run golden retrieval evaluation and security tests.
5. Benchmark latency, memory, index build time, and cost.
6. Validate deletion on the new index.
7. Atomically switch serving to the new index.
8. Monitor and retain the old index until the rollback window expires.

### Solution

Use:

```text
Source of truth
    ├── v1 chunking → v1 embeddings → v1 index → production
    └── v2 chunking → v2 embeddings → v2 index → evaluation

v2 passes:
quality + security + freshness + performance
                 ↓
          atomic serving switch
                 ↓
              monitor
                 ↓
          rollback to v1 if needed
```

Because chunking changed, content hashes and chunk identity must be handled carefully; unchanged source content does not necessarily imply identical chunk boundaries.

### Why This Solution Works

Changing chunking can alter the retrieval corpus even when the source documents are unchanged. Therefore this is a data migration, not merely a model deployment.

### Production Insight

Keep explicit corpus/index/model versions and record the evaluation dataset version. Rollback must restore a known-good retrieval state, not simply redeploy application code.

## Question 36 — Design a Cost-Controlled Embedding Platform

**Difficulty:** Advanced

### Problem

A company has 20 million document chunks. 99% of content is unchanged each day, but a nightly full re-embedding job is consuming most of the AI infrastructure budget. Design a cost-control plan without reducing retrieval freshness.

### How to Solve the Problem

1. Measure current embedding volume, token volume, throughput, and cost.
2. Add content hashing and changed-only processing.
3. Deduplicate identical content/chunks where semantically and operationally safe.
4. Batch embedding requests.
5. Bound retries and classify transient failures.
6. Use local embedding models where privacy, quality, and economics justify them.
7. Use distributed processing only when a single machine is insufficient.
8. Track cost per changed chunk and source-to-index freshness.

### Solution

The primary optimization is:

```text
20M total
 × 1% changed
 = 200K changed chunks/day
```

The pipeline should process the changed set, while separately handling deletions and chunk-boundary changes. Then benchmark batch size, local/hosted model economics, and Ray Data only if the workload warrants distributed processing.

### Why This Solution Works

The largest saving comes from eliminating unnecessary work, not from making full re-embedding faster. Freshness can remain high because only changed content needs new vectors.

### Production Insight

Create a cost budget and freshness SLA together. A cheap pipeline that delays updates beyond the serving contract is not an optimization.

## Question 37 — Production Security Review for the Serving Stack

**Difficulty:** Advanced

### Problem

Perform a security review of a platform containing a FastAPI data service, Redis cache, semantic metric API, Feast online features, and a vector retrieval API. The platform handles PII and tenant-specific data. Identify the major security boundaries and controls.

### How to Solve the Problem

Review each layer for:
1. authentication;
2. authorization;
3. row/column access;
4. PII masking;
5. SQL injection;
6. cache isolation;
7. feature-store access;
8. vector ACL filtering;
9. deletion/erasure;
10. sensitive error leakage;
11. export/download authorization;
12. observability without excessive sensitive logging.

### Solution

A layered control model is:

```text
Identity
  ↓
Authorization context
  ↓
API validation
  ↓
Data/query authorization
  ↓
Permission-aware cache
  ↓
Serving store
  ↓
Response filtering
```

For vector data, ACL metadata must be enforced during retrieval. For caches, caller scope must influence cache identity. For SQL, values must be parameterized and identifiers allowlisted. For PII, expose only permitted columns and mask where required.

### Why This Solution Works

Security failures often happen at boundaries between otherwise-correct systems. A secure database does not make an unsafe cache key secure, and an authenticated API does not automatically authorize every row.

### Production Insight

Create cross-layer security tests: unauthorized row access, cross-tenant cache hits, restricted feature access, unauthorized vector retrieval, export download by another user, and deletion verification.

## Question 38 — Build a Full Observability and SLO Strategy

**Difficulty:** Advanced

### Problem

You operate the full Module 2.22 serving platform. Define an observability strategy that can distinguish API performance problems, cache problems, semantic-data freshness problems, feature freshness problems, and retrieval-quality regressions.

### How to Solve the Problem

1. Define consumer-facing SLOs.
2. Instrument each serving path with latency percentiles and errors.
3. Add freshness/version metadata to data-serving paths.
4. Track cache hit/miss and refresh behavior.
5. Track feature freshness, missingness, and drift.
6. Track vector retrieval quality and index/model versions.
7. Correlate traces across API, storage, cache, and downstream services.
8. Define alerts and incident runbooks.

### Solution

A practical metric set includes:

```text
API:
  p50/p95/p99, throughput, errors

Cache:
  hit rate, miss rate, refresh concurrency, stale responses

Semantic:
  metric reconciliation failures, data_version lag

Features:
  freshness, missingness, drift, online/offline parity

Vectors:
  Recall@K, empty-result rate, p95/p99, freshness,
  model/index version, ACL failures

Platform:
  DB latency/load, pool saturation, cost
```

OpenTelemetry can provide traces linking request → service → database/cache calls.

### Why This Solution Works

No single metric explains a serving system. Latency tells you how fast; freshness tells you how current; quality tells you whether the result is useful; security metrics tell you whether access is correct.

### Production Insight

Alert on user-impacting conditions and define diagnostic dashboards that expose the causal chain. Avoid logging sensitive payloads merely to make debugging easier.

## Question 39 — Incident: Same Metric, Different Answers

**Difficulty:** Advanced

### Problem

At 09:00, Finance reports that BI says monthly `net_revenue` is ₹100M, the API says ₹96M, and an AI assistant says ₹103M. All three systems are operationally healthy. Design a root-cause investigation and permanent remediation.

### How to Solve the Problem

1. Freeze assumptions and collect the exact query/filter/time context from each consumer.
2. Compare metric definitions and semantic-layer versions.
3. Compare entity grain and join paths.
4. Compare `data_version`/`as_of`.
5. Check cache versions and invalidation.
6. Inspect whether the AI assistant is using a certified metric or free-form SQL.
7. Reconcile each result to a known finance-controlled query.
8. Centralize the metric definition and add regression tests.

### Solution

The investigation should build a comparison table:

```text
Consumer | Metric version | Data version | Grain | Filters | Cache | Result
```

If the API and BI use the same certified metric but different data versions, fix serving freshness/versioning. If the AI assistant generated independent SQL, route it through the governed semantic layer instead.

The permanent solution is one governed metric definition plus explicit serving versions and known-answer tests.

### Why This Solution Works

Operational health does not imply semantic correctness. Three systems can all return HTTP 200 while answering different questions.

### Production Insight

Treat metric definitions as code with ownership, certification, regression tests, reconciliation, and deprecation. Make `as_of` and `data_version` visible to consumers so discrepancies can be explained quickly.

## Question 40 — Design the Production Rollout and Cost Plan

**Difficulty:** Advanced

### Problem

You are launching a unified serving platform supporting customer APIs, dashboard aggregates, churn features, and AI retrieval. Leadership requires: p95 API latency under 300 ms, feature freshness under 5 minutes, retrieval Recall@5 ≥ 0.90, strong tenant isolation, and a measurable cost per 1,000 requests. Design the rollout plan.

### How to Solve the Problem

1. Convert requirements into explicit serving contracts and test gates.
2. Build unit, integration, contract, security, retrieval, and data-correctness tests.
3. Load-test APIs and online feature paths with p50/p95/p99.
4. Benchmark vector retrieval against a golden dataset and exact baseline.
5. Validate cache hit rate, freshness, invalidation, and versioning.
6. Run a staged rollout with observability and rollback triggers.
7. Measure cost by serving path and per 1,000 requests.
8. Document architecture decisions and operational runbooks.

### Solution

A strong rollout is:

```text
Build
 ↓
Unit + integration + contract tests
 ↓
Security tests
 ↓
Data correctness tests
 ↓
Load test
 ↓
Retrieval evaluation
 ↓
Cost benchmark
 ↓
Canary / staged deployment
 ↓
Observe SLOs
 ↓
Expand traffic
```

Example gates:

```text
API p95 < 300 ms
Feature freshness < 5 min
Recall@5 >= 0.90
No cross-tenant authorization failures
Cost/1,000 requests within budget
```

For each failure, define rollback before increasing traffic.

### Why This Solution Works

The platform has multiple independent correctness dimensions: API latency, data freshness, metric consistency, feature correctness, retrieval quality, security, and cost. Passing only a performance test is insufficient.

### Production Insight

Senior engineers make rollout criteria measurable before launch. The final architecture should include dashboards, alerts, cost attribution, data/version lineage, rollback paths, and documented ownership for each serving product.

# Module Coverage Summary

| Area | Coverage emphasis |
|---|---|
| FastAPI Data Services | pagination, safe filtering, pooling, async I/O, exports, security, latency |
| Aggregates & Caching | cache-aside, keys, invalidation, freshness, stampede protection, capacity |
| Semantic Layers | metric governance, grain, fan-out, ratios, testing, governed AI metric access |
| Feature Stores & ML Handoff | offline/online serving, point-in-time correctness, skew, freshness, adoption decisions |
| Embedding & Vector Pipelines | chunking, metadata, pgvector, ANN, hybrid retrieval, ACLs, deletion, migration, evaluation |
| Cross-topic engineering | security, correctness, performance, observability, cost, rollout and incident response |

# Final Assessment

Successful completion should demonstrate that the learner can do more than define Module 2.22 terminology. They should be able to design and defend secure serving paths, diagnose correctness and performance failures, reason about freshness and cache behavior, build reproducible ML data handoffs, operate evaluated vector retrieval, and integrate these components into a production-oriented serving platform.

# Validation

- Basic: exactly 10 questions
- Moderate: exactly 10 questions
- Hard: exactly 10 questions
- Advanced: exactly 10 questions
- Total: exactly 40 questions
- Every question contains Problem, How to Solve the Problem, Solution, Why This Solution Works, and Production Insight
- Questions are numbered sequentially from Question 01 through Question 40
