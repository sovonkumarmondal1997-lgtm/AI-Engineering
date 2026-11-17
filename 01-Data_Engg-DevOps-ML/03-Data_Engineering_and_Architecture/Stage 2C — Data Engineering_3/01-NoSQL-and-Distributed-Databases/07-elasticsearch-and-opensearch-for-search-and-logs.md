# Elasticsearch and OpenSearch for Search and Logs

**Stage:** Stage 2C — Data Engineering_3  
**Module:** 01 — NoSQL and Distributed Databases  
**Topic:** 07  
**Target path:** `Stage 2C — Data Engineering_3/01-NoSQL-and-Distributed-Databases/07-elasticsearch-and-opensearch-for-search-and-logs.md`

> **Version discipline:** Elasticsearch and OpenSearch share concepts and much of their historical API shape, but they are separate products. This lesson labels product-specific examples. Pin your server, dashboard, and Python-client versions together; validate exact APIs against those versions before production use. Do not assume an Elasticsearch client or lifecycle policy is fully compatible with OpenSearch.

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Explain clusters, nodes, indices, documents, primary shards, replicas, REST APIs, and the inverted index.
- Create a product index with explicit mappings; explain `text`, `keyword`, multi-fields, dynamic mapping, and mapping explosion.
- Inspect analysis with `_analyze`, define custom analyzers, and reason about stemming and synonyms.
- Write `match`, `term`, `multi_match`, `bool`, `range`, and filter queries; interpret `_score` and BM25 at a practical level.
- Build metric, bucket, and pipeline aggregations for faceted product search and log analytics.
- Bulk-index records with a Python client and understand refresh/near-real-time behavior.
- Design log data streams, templates, lifecycle/retention policies, rollover, and sensible shard sizes.
- Plan alias-based reindexing, ingest pipelines, reliable source synchronization, and PIT plus `search_after` exports to Parquet.
- Describe vector/hybrid search and the important product, API, licensing, and deployment differences between Elasticsearch and OpenSearch.

## 2. Prerequisites and where this topic fits

The authoritative module roadmap places this topic after NoSQL fundamentals, consistency, MongoDB, Cassandra, DynamoDB, and Redis, and before graph databases and NoSQL-to-lakehouse ingestion. You should already know Python, JSON, REST/HTTP, SQL and aggregations, OLTP versus OLAP, batch versus streaming, idempotent ingestion, CDC basics, Docker Compose, and basic Kafka concepts.

The purpose is not to replace a transactional database. Elasticsearch/OpenSearch are usually **derived search and analytics stores** built from authoritative systems such as PostgreSQL, MongoDB, or event streams. A data engineer must be able to index into them and extract from them reliably.

### Suggested local toolchain

- Docker Compose and either Elasticsearch plus Kibana **or** OpenSearch plus OpenSearch Dashboards.
- Python 3.12+ and a virtual environment.
- Elasticsearch Python client for Elasticsearch; OpenSearch Python client for OpenSearch.
- `pandas` and `pyarrow` for the Parquet export exercise.

Example Python environment:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install 'elasticsearch>=8,<9' 'opensearch-py>=2,<3' pandas pyarrow python-dotenv
```

These are example major-version ranges, not a promise that every server/client combination is compatible. Install only the client for the product you run in each experiment and check the official compatibility matrix. Keep credentials in environment variables, never in source control.

## 3. Architecture and core vocabulary

- **Cluster:** a coordinated set of nodes that stores and serves data.
- **Node:** one running server process. Roles can include data, ingest, master-eligible, coordinating, or specialized tier roles; the exact role model varies by version and deployment.
- **Index:** a logical collection of documents with mappings and settings. In time-series workflows, a data stream can provide a stable name over backing indices.
- **Document:** JSON-like record with an identifier and fields.
- **Primary shard:** a partition of an index. Each document is routed to one primary shard based on its routing value (normally derived from `_id`).
- **Replica shard:** a copy of a primary shard, generally on another eligible node. Replicas can provide redundancy and serve searches; they consume storage and resources.
- **REST API:** HTTP endpoints for indexing, searching, mappings, settings, lifecycle, cluster health, and administration.
- **Kibana / OpenSearch Dashboards:** browser interfaces for discovering data, querying, visualizing, and operating the corresponding stack.

A single-node local lab is suitable for learning APIs, but it does not demonstrate high availability. A production cluster needs failure-domain-aware placement, security, backups, capacity planning, monitoring, and tested recovery.

### REST API quick start

For a local Elasticsearch container with security enabled, the official image typically prints an initial password and enrollment information. Follow the exact instructions for the pinned image; do not assume anonymous HTTP access. A local OpenSearch configuration may be different and may use a demo security configuration. Never expose an unsecured lab endpoint to a public network.

Useful calls (replace the URL, credentials, and certificate options for your installation):

```bash
curl --cacert ./http_ca.crt -u "elastic:${ELASTIC_PASSWORD}" https://localhost:9200/
curl --cacert ./http_ca.crt -u "elastic:${ELASTIC_PASSWORD}" 'https://localhost:9200/_cluster/health?pretty'
curl --cacert ./http_ca.crt -u "elastic:${ELASTIC_PASSWORD}" 'https://localhost:9200/_cat/nodes?v'
curl --cacert ./http_ca.crt -u "elastic:${ELASTIC_PASSWORD}" 'https://localhost:9200/_cat/indices?v'
```

For OpenSearch, use the endpoint and authentication/certificate settings appropriate to your chosen OpenSearch distribution or managed service. `_cat` APIs are diagnostic conveniences; automate against stable structured APIs when possible.

## 4. How search works: documents, analysis, and the inverted index

Consider these product documents:

```json
{"product_id":"p-101","name":"Wireless noise-cancelling headphones","brand":"Acme Audio","description":"Comfortable Bluetooth headphones with active noise cancellation.","price":129.99,"in_stock":true}
{"product_id":"p-102","name":"Wired studio headphones","brand":"StudioCo","description":"Closed-back monitoring headphones for recording.","price":89.50,"in_stock":true}
```

When a `text` field is indexed, an analyzer usually runs a character-filter stage, a tokenizer, and token filters. For example, `Wireless noise-cancelling headphones` may yield tokens like `wireless`, `noise`, `cancelling`, `headphones`, depending on the analyzer. The engine records terms and their document/position information in an **inverted index** (term → postings), which avoids scanning every full source document for many text searches.

Analysis has trade-offs. Stemming can make `connect`, `connected`, and `connecting` match, but can over-normalize language. Synonyms can increase recall, but a poorly designed synonym set can create irrelevant matches or increase index/query complexity. Exact values such as a SKU, status, brand facet, or a timestamp generally need non-analyzed fields.

For this introductory request/response demonstration, use a separate `products-demo` index. The explicit `products-v1` mapping is created in the next section; keeping the demo index separate avoids auto-creating `products-v1` before its mapping is installed.

Index a first document:

```http
PUT products-demo/_doc/p-101
{
  "product_id": "p-101",
  "name": "Wireless noise-cancelling headphones",
  "brand": "Acme Audio",
  "description": "Comfortable Bluetooth headphones with active noise cancellation.",
  "price": 129.99,
  "in_stock": true
}
```

Search it:

```http
GET products-demo/_search
{
  "query": { "match": { "name": "wireless headphones" } }
}
```

Read the response:

- `hits.total` gives the total-match information; depending on request and defaults, it may be an exact count or a lower-bound relation such as `gte`.
- `hits.hits` contains returned documents, often with `_index`, `_id`, `_source`, and `_score`.
- `_score` is a relevance score for scored queries, not a probability and not necessarily comparable across unrelated queries.
- Filter-only matches may have no meaningful relevance ranking; do not interpret a missing/constant score as a defect.

## 5. Mappings and field design

A **mapping** defines how fields are interpreted and indexed. Prefer explicit mappings for important production fields. Dynamic mapping is convenient during exploration but can create unwanted field types or unbounded field names when every arbitrary JSON key becomes a mapped field (**mapping explosion**).

### `text` versus `keyword`

| Field type | Typical use | Behavior |
|---|---|---|
| `text` | Product names/descriptions, log messages | Analyzed for full-text search; usually not used for exact terms aggregation or sorting unless a separate keyword field exists |
| `keyword` | SKU, brand facet, status, tenant ID, tags | Exact value; suitable for terms filters, aggregations, and sorting |
| `integer`, `long`, `float`, `double`, `scaled_float` | Counts and prices | Numeric comparisons and range filters; choose precision and range deliberately |
| `date` | Event time, order time | Date parsing, sorting, ranges, date histograms |
| `boolean` | Availability, flags | True/false filtering |
| `ip` | Client IP | IP parsing and CIDR queries |
| `object` / `nested` | Structured objects / arrays of objects | `nested` is needed when array-object field relationships must be preserved across matching clauses |
| `dense_vector` / `knn_vector` | Embeddings | Product/version-specific vector search capabilities and constraints |

Multi-fields index one source value in multiple ways. A `name` can be `text` for relevance and `name.keyword` for exact sorting/aggregation.

### Explicit product mapping (common Elasticsearch/OpenSearch subset)

```http
PUT products-v1
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "refresh_interval": "1s"
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "product_id": { "type": "keyword" },
      "name": {
        "type": "text",
        "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } }
      },
      "brand": { "type": "keyword" },
      "category": { "type": "keyword" },
      "description": { "type": "text" },
      "price": { "type": "scaled_float", "scaling_factor": 100 },
      "in_stock": { "type": "boolean" },
      "updated_at": { "type": "date" },
      "tags": { "type": "keyword" }
    }
  }
}
```

The single primary shard and zero replicas are **lab-only** settings. For production, select shard count based on expected primary-shard size, throughput, retention, and node capacity; set replicas to meet availability requirements. `dynamic: strict` rejects unmapped fields, which protects the schema but requires an explicit migration when a new field is introduced.

`scaled_float` stores a scaled representation appropriate for many currency values; choose a scaling factor that matches the precision requirement. If exact decimal financial arithmetic is critical, keep the authoritative monetary value in a database designed for it and define the search projection deliberately.

### Dynamic mapping and mapping explosion

Default dynamic mapping infers fields from observed values. Risks include:

- A field first seen as a number later arrives as a string and causes mapping conflicts.
- Arbitrary user-defined keys produce thousands of distinct mapped fields.
- High-cardinality values are mistakenly mapped as analyzed text, or analyzed messages are mistakenly mapped as keyword.

Use explicit mappings, `dynamic: false` or `strict` where appropriate, flattened/object strategies for arbitrary metadata (depending on product/version), and ingest-time normalization. Do not map every raw event property without a schema plan.

### Compare `text` and `keyword`

```http
POST products-v1/_doc/p-103?refresh=true
{
  "product_id": "p-103",
  "name": "Wireless Headphones",
  "brand": "Acme Audio",
  "category": "audio",
  "description": "Bluetooth audio device",
  "price": 99.00,
  "in_stock": true,
  "updated_at": "2026-01-15T10:00:00Z",
  "tags": ["wireless", "audio"]
}

GET products-v1/_search
{
  "query": { "match": { "name": "wireless headphones" } }
}

GET products-v1/_search
{
  "query": { "term": { "brand": "Acme Audio" } }
}
```

A `term` query does not analyze its query text. Use `term` on `keyword` or numeric/boolean/date fields when exact matching is intended. A `term` query against analyzed `text` often surprises beginners because the indexed field contains tokens rather than the original whole phrase. Use `match` for full-text search. If the mapping uses a multi-field, exact name matching is `name.keyword`, not `name`.

## 6. Analyzers, tokenizers, filters, stemming, and synonyms

An analyzer commonly combines:

1. **Character filters** — optional character-level normalization before tokenization.
2. **Tokenizer** — splits the input into tokens.
3. **Token filters** — lowercase, stop-word removal, stemming, synonym expansion, and other token transformations.

Inspect the default analyzer:

```http
POST products-v1/_analyze
{
  "analyzer": "standard",
  "text": "Wireless noise-cancelling headphones"
}
```

Inspect the analyzer configured on a field (if the field has a known analyzer):

```http
POST products-v1/_analyze
{
  "field": "name",
  "text": "Wireless noise-cancelling headphones"
}
```

The response's token list helps explain why a query matches or fails. Analysis at index time and search time should be designed together. Existing indexed terms are not retroactively changed when you update an analyzer setting; changing index-time analysis generally requires a new index and reindexing.

### Custom analyzer with synonyms

Synonym syntax and reload behavior vary by product/version. This illustrative common pattern uses a synonym set/file configured for the pinned server. Ensure the synonym resource is installed and readable by the server before creating the index.

```http
PUT products-synonyms-v1
{
  "settings": {
    "analysis": {
      "filter": {
        "product_synonyms": {
          "type": "synonym_graph",
          "synonyms": [
            "tv, television",
            "cell phone, mobile phone, smartphone"
          ]
        }
      },
      "analyzer": {
        "product_index": {
          "tokenizer": "standard",
          "filter": ["lowercase"]
        },
        "product_search": {
          "tokenizer": "standard",
          "filter": ["lowercase", "product_synonyms"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "name": { "type": "text", "analyzer": "product_index", "search_analyzer": "product_search" }
    }
  }
}
```

Test the actual behavior:

```http
POST products-synonyms-v1/_analyze
{
  "analyzer": "product_search",
  "text": "smartphone"
}
```

Index a document whose `name` is `Cell phone with long battery life`, then search for `smartphone`. Compare with an otherwise identical index without the synonym filter. Expected observation: the synonym-aware query can retrieve the document through the configured synonym expansion. This is an experiment to run, not a claimed measured result. For larger synonym lists, use the product's supported synonym-set management/reload mechanism and validate search-time versus index-time expansion trade-offs.

## 7. Query DSL: relevance and structured filtering

Search usually combines **relevance clauses** with **structured filters**. Scoring clauses answer “how well does the document match this text?” Filters answer “does the document satisfy this exact condition?” Filters are generally cacheable and avoid relevance scoring for those clauses.

### `match` and `multi_match`

```http
GET products-v1/_search
{
  "query": {
    "match": {
      "description": {
        "query": "bluetooth noise cancellation",
        "operator": "or"
      }
    }
  }
}
```

```http
GET products-v1/_search
{
  "query": {
    "multi_match": {
      "query": "wireless headphones",
      "fields": ["name^3", "description", "brand^2"],
      "type": "best_fields"
    }
  }
}
```

The `^3` boost makes a match in `name` contribute more strongly under this query. Boosts influence ranking; they do not guarantee a fixed ordering independent of term statistics and other query clauses.

### `bool`: `must`, `should`, `filter`, `must_not`

```http
GET products-v1/_search
{
  "query": {
    "bool": {
      "must": [
        { "multi_match": {
          "query": "wireless headphones",
          "fields": ["name^3", "description"]
        }}
      ],
      "filter": [
        { "term": { "in_stock": true }},
        { "range": { "price": { "gte": 50, "lte": 200 }}}
      ],
      "should": [
        { "term": { "brand": { "value": "Acme Audio", "boost": 1.5 }}}
      ],
      "minimum_should_match": 0
    }
  }
}
```

- `must`: must match and contributes to score.
- `should`: optional scoring preference unless the `bool` context makes it required (for example, when no `must` or `filter` clauses are present) or `minimum_should_match` says otherwise.
- `filter`: must match, but does not contribute to relevance score.
- `must_not`: must not match; does not contribute to score.
- `range`: numeric/date bounds and related range conditions.

For a search box, text belongs in `must`/`should`; availability, tenant, brand, and price constraints generally belong in `filter`. Always include tenant/authorization filters where required; never rely on a user-provided query to enforce access control.

### `term` and `range`

```http
GET products-v1/_search
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "category": "audio" }},
        { "terms": { "brand": ["Acme Audio", "StudioCo"] }},
        { "range": { "price": { "gte": 75, "lt": 150 }}}
      ]
    }
  }
}
```

Use the field's actual mapped type and exact stored value. Keyword matching is normally case-sensitive at the stored-value level unless normalizers or application normalization change that behavior.

## 8. BM25, relevance tuning, and explainability

BM25 is a commonly used text relevance model. In broad terms, it weighs term frequency, inverse document frequency, and document-length normalization with saturation. A rare query term can contribute more than a very common one; repeated terms help but with diminishing returns. Field length and corpus statistics affect the score. The score is not a probability or universal quality metric.

Improve relevance methodically:

1. Check mappings and `_analyze` output before changing boosts.
2. Decide which fields are searchable and which are filters.
3. Boost high-intent fields such as product title or SKU carefully.
4. Use synonyms only for true equivalences or business-approved alternatives.
5. Inspect representative good and bad results; define a small query set with expected relevant documents.
6. Use `_explain` for a document/query pair when you need to understand scoring.

```http
GET products-v1/_explain/p-103
{
  "query": {
    "multi_match": {
      "query": "wireless headphones",
      "fields": ["name^3", "description"]
    }
  }
}
```

Do not claim that a boost improves quality until you evaluate it on representative queries. Avoid over-tuning to a few examples.

## 9. Aggregations: metrics, buckets, and pipelines

Aggregations summarize matching documents. They are central to faceted product search and log analytics. Aggregations on high-cardinality fields can be memory-intensive; use appropriate keyword/numeric/date fields and realistic limits.

### Product facets: brand terms and price histogram

```http
GET products-v1/_search
{
  "size": 0,
  "query": {
    "bool": {
      "must": [{ "match": { "description": "wireless headphones" }}],
      "filter": [{ "term": { "in_stock": true }}]
    }
  },
  "aggs": {
    "brands": { "terms": { "field": "brand", "size": 20 }},
    "prices": { "histogram": { "field": "price", "interval": 25 }},
    "price_stats": { "stats": { "field": "price" }}
  }
}
```

- **Metric aggregations:** `min`, `max`, `avg`, `sum`, `value_count`, `stats`, percentiles (subject to implementation and settings).
- **Bucket aggregations:** `terms`, `range`, `histogram`, `date_histogram`, `filters`.
- **Pipeline aggregations:** operate on aggregation outputs, for example `derivative` over a date histogram or `moving_fn` over a series. Exact names/availability should be checked for your product/version.

### Log analytics with date histogram and error counts

```http
GET logs-app/_search
{
  "size": 0,
  "query": {
    "range": {
      "@timestamp": {
        "gte": "now-24h",
        "lt": "now"
      }
    }
  },
  "aggs": {
    "per_5m": {
      "date_histogram": {
        "field": "@timestamp",
        "fixed_interval": "5m"
      },
      "aggs": {
        "errors": { "filter": { "term": { "log.level": "ERROR" }}},
        "latency_p95": { "percentiles": { "field": "http.duration_ms", "percents": [95] }}
      }
    },
    "by_service": { "terms": { "field": "service.name", "size": 20 }}
  }
}
```

This assumes mappings for `log.level`, `service.name`, `http.duration_ms`, and `@timestamp`. If the event uses ECS-like field names, use consistent mappings across the ingest pipeline. Aggregation buckets do not return every distinct value when cardinality is high; the `terms` aggregation is top-N by default and may report approximation/other-bucket information. Use composite aggregation for paginating many buckets when suitable, not an unbounded `terms` size.

## 10. Python clients and bulk indexing

Use the client corresponding to the server. Do not point an Elasticsearch Python client at an arbitrary OpenSearch major version and assume full compatibility. Keep authentication and TLS verification enabled in production.

### Elasticsearch Python client

```python
import os
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch(
    os.environ["ELASTICSEARCH_URL"],
    api_key=os.environ["ELASTICSEARCH_API_KEY"],
    request_timeout=30,
    # Keep TLS certificate verification enabled.
)

products = [
    {
        "_op_type": "index",
        "_index": "products-v1",
        "_id": "p-101",
        "_source": {
            "product_id": "p-101",
            "name": "Wireless noise-cancelling headphones",
            "brand": "Acme Audio",
            "category": "audio",
            "description": "Comfortable Bluetooth headphones with active noise cancellation.",
            "price": 129.99,
            "in_stock": True,
            "updated_at": "2026-01-15T10:00:00Z",
            "tags": ["wireless", "audio"],
        },
    }
]

ok = 0
failed = 0
for success, item in helpers.streaming_bulk(
    es,
    products,
    chunk_size=500,
    max_chunk_bytes=5 * 1024 * 1024,
    raise_on_error=False,
    raise_on_exception=False,
    request_timeout=60,
):
    if success:
        ok += 1
    else:
        failed += 1
print({"indexed": ok, "failed": failed})
```

Use the API-key form only when your deployment supports it; for local username/password or managed-service authentication, configure the appropriate credential mechanism. Never disable certificate verification to “fix” TLS errors. Investigate the certificate trust chain instead.

The bulk API reduces per-document HTTP overhead, but large batches increase memory use and can amplify retries. Tune chunk size by measurement, handle per-item failures, and retry only retryable errors with bounded backoff. Do not blindly replay non-idempotent operations. Stable `_id` values make repeated `index` operations easier to make idempotent, but do not make all application workflows exactly-once.

### OpenSearch Python client

```python
import os
from opensearchpy import OpenSearch, helpers

client = OpenSearch(
    hosts=[os.environ["OPENSEARCH_URL"]],
    http_auth=(os.environ["OPENSEARCH_USERNAME"], os.environ["OPENSEARCH_PASSWORD"]),
    use_ssl=True,
    verify_certs=True,
    ssl_assert_hostname=True,
    timeout=30,
)

actions = [
    {
        "_op_type": "index",
        "_index": "products-v1",
        "_id": "p-101",
        "_source": {"product_id": "p-101", "name": "Wireless headphones", "brand": "Acme Audio", "price": 129.99},
    }
]
for success, item in helpers.streaming_bulk(
    client, actions, chunk_size=500, max_chunk_bytes=5 * 1024 * 1024,
    raise_on_error=False, raise_on_exception=False,
):
    if not success:
        print("Bulk item failed", item)
```

This authentication example is illustrative for username/password deployments. Managed services may require SigV4 or another authentication scheme. Use the official OpenSearch client documentation for the deployment and version you run.

## 11. Refresh and near-real-time search

An acknowledged indexing request does not necessarily mean the document is already searchable. Search visibility follows refresh behavior: newly indexed changes become searchable after a refresh. Refreshing too frequently creates small segments and overhead; refreshing too slowly increases visibility latency.

For interactive examples, `?refresh=true` can force immediate visibility, but do not use it for every document in a high-throughput production ingestion path. Bulk-index a batch and then refresh once if a lab requires immediate verification. In production, use the default or a deliberately configured refresh interval based on freshness and throughput requirements. A refresh is not the same as a durable disk flush or a backup.

## 12. Log data streams, templates, lifecycle, rollover, and shard sizing

Logs are time-series events. A good schema has a timestamp, service/environment identifiers, severity, message, trace/request IDs, and typed numeric fields for metrics such as duration. Normalize at ingestion; avoid mapping every arbitrary field from untrusted input.

### Ingest architecture

```text
Applications / hosts / containers
  ├─ OpenTelemetry Collector / Fluent Bit / Beats / Elastic Agent
  └─ Logstash (parsing, enrichment, routing when needed)
          ↓ TLS + authentication
    Elasticsearch or OpenSearch ingest pipeline
          ↓
    data stream / backing indices
          ↓
    Kibana or OpenSearch Dashboards + alerts
          ↓
    PIT/search_after export or stream/CDC pipeline → object storage/lakehouse
```

Choose one or a small number of collection paths with clear ownership. Fluent Bit, Beats/Elastic Agent, Logstash, and OpenTelemetry Collector overlap but are not interchangeable in every deployment. Define parsing, timestamps, redaction, retries, buffering, and dead-letter handling at the right layer. Do not ingest secrets or unnecessary personal data into logs.

### Index template for a data stream — Elasticsearch example

The following uses Elasticsearch ILM. Verify data-stream template and ILM syntax against the pinned Elasticsearch version. The template defines a data stream, and the lifecycle policy handles rollover and retention.

```http
PUT _ilm/policy/logs-retain-14d
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_primary_shard_size": "30gb",
            "max_age": "1d"
          }
        }
      },
      "delete": {
        "min_age": "14d",
        "actions": { "delete": {} }
      }
    }
  }
}

PUT _index_template/logs-app-template
{
  "index_patterns": ["logs-app-*"],
  "data_stream": {},
  "priority": 300,
  "template": {
    "settings": {
      "index.lifecycle.name": "logs-retain-14d",
      "number_of_shards": 1,
      "number_of_replicas": 1
    },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "message": { "type": "match_only_text" },
        "log.level": { "type": "keyword" },
        "service.name": { "type": "keyword" },
        "service.environment": { "type": "keyword" },
        "trace.id": { "type": "keyword" },
        "http.duration_ms": { "type": "long" }
      }
    }
  }
}
```

`match_only_text` is an Elasticsearch field type; do not assume it exists or behaves identically in OpenSearch. Replace it with `text` for a more portable example. In a production deployment, the number of shards and replicas must reflect cluster topology and expected ingestion. A single primary shard per backing index is only a starting point for a modest workload. The `30gb` and `1d` thresholds above are **example policy thresholds**, not universal recommendations. Use the first of the configured rollover conditions that is supported and reached according to the product's lifecycle semantics. In Elasticsearch ILM, a delete-phase `min_age` for an index that has rolled over is measured from rollover time, not necessarily from each event's timestamp; retention is therefore not an exact per-document age guarantee. Validate the resulting retention window against compliance requirements.

Create/write to the data stream (after template and policy are installed):

```http
POST logs-app-prod/_doc
{
  "@timestamp": "2026-01-15T10:01:00Z",
  "message": "request completed",
  "log": { "level": "INFO" },
  "service": { "name": "checkout", "environment": "prod" },
  "trace": { "id": "trace-001" },
  "http": { "duration_ms": 42 }
}
```

The `@timestamp` field is required for a data stream. Data streams are append-oriented; use the documented backing-index or update/delete-by-query behavior if updates/deletes are truly needed. They are best suited to events that accumulate rather than frequently mutate.

### OpenSearch lifecycle is ISM, not ILM

OpenSearch uses Index State Management (ISM), with policies and actions whose syntax and supported data-stream behavior depend on the OpenSearch version. Do not send the Elasticsearch `_ilm/policy` request to OpenSearch. A representative ISM policy for ordinary time-based indices can look like this:

```http
PUT _plugins/_ism/policies/logs-retain-14d
{
  "policy": {
    "description": "Roll over and delete application log indices",
    "default_state": "hot",
    "states": [
      {
        "name": "hot",
        "actions": [
          { "rollover": { "min_size": "30gb", "min_index_age": "1d" } }
        ],
        "transitions": [
          { "state_name": "delete", "conditions": { "min_index_age": "14d" } }
        ]
      },
      { "name": "delete", "actions": [{ "delete": {} }], "transitions": [] }
    ],
    "ism_template": [{ "index_patterns": ["logs-app-*"], "priority": 100 }]
  }
}
```

Treat this as a version-scoped illustration of ISM, not a universal data-stream recipe. Confirm that your OpenSearch version supports the required data-stream lifecycle attachment and rollover behavior. If it does not, use the documented supported pattern for that version—often a rollover alias plus ordinary indices—or select a compatible release. Test policy attachment, rollover, and deletion in a disposable cluster before relying on retention in production. Deletion policies are irreversible unless you have another copy.

### Hot/warm/cold/delete and retention

- **Hot:** active indexing and frequent searches; fast storage and adequate CPU/heap.
- **Warm:** less frequently updated, often still searched; can use lower-cost resources and optimized segments.
- **Cold/frozen:** infrequent queries and storage-cost optimization; query latency can be higher and architecture differs by product/version.
- **Delete:** enforce retention after legal, privacy, and operational requirements are satisfied.

Elasticsearch ILM supports phases and data tiers depending on version/deployment; OpenSearch ISM uses states/actions and can implement transitions. The vocabulary and APIs are not identical. Do not copy an ILM policy into ISM or assume a tier action exists in both.

### Shard sizing and hot nodes

There is no universally correct shard size. Estimate daily primary data volume, compression/overhead, retention, replica count, query concurrency, and failure-recovery requirements. Many small shards create per-shard metadata and heap overhead; very large shards can slow recovery, relocation, and queries. Use observed primary shard sizes and query/ingest metrics to tune. For a log stream, rollover by size and age can prevent unbounded backing indices, but a daily rollover alone may create tiny shards at low volume.

Watch:

- primary/replica shard sizes and count;
- JVM heap pressure and garbage collection (for self-managed Java deployments);
- indexing and search rejections, queue depth, CPU, disk watermarks, and merge pressure;
- uneven shard allocation, skewed routing, and hot ingest nodes;
- refresh/merge cost, query latency percentiles, and recovery time.

Avoid using shard count as a substitute for capacity planning. Replica count improves redundancy and search parallelism at the cost of storage and write work. A single-node lab cannot allocate a replica; yellow health in that specific setup may be expected, but yellow/red in production needs investigation.

## 13. Reindexing and zero-downtime schema changes with aliases

Mappings are not freely mutable. You can add some fields, but you cannot safely change an existing field's type or rewrite its indexed tokens in place. The normal migration pattern is:

1. Create a new index with the desired mapping/analyzer.
2. Reindex documents from the old index to the new index.
3. Capture and replay writes that happened during the copy, or dual-write from a reliable change stream/outbox.
4. Validate counts, representative queries, and aggregations.
5. Atomically switch the read/write alias using the aliases API.
6. Keep the old index temporarily for rollback, then delete it only after the retention window.

### Example alias setup

Assume application code reads and writes through `products` alias, not a concrete versioned index. Initial creation:

```http
PUT products-v1
{
  "mappings": {
    "properties": {
      "product_id": { "type": "keyword" },
      "name": { "type": "text", "fields": { "keyword": { "type": "keyword" } } },
      "brand": { "type": "keyword" },
      "price": { "type": "float" }
    }
  }
}

POST _aliases
{
  "actions": [
    { "add": { "index": "products-v1", "alias": "products", "is_write_index": true } }
  ]
}
```

Create the target `products-v2` with the new mapping, then run:

```http
POST _reindex?wait_for_completion=false
{
  "source": { "index": "products-v1" },
  "dest": { "index": "products-v2", "op_type": "create" }
}
```

Poll the returned task ID and inspect failures. `op_type: create` helps avoid overwriting an already-present destination ID; conflicts must be interpreted and resolved intentionally. **A reindex alone does not capture concurrent source writes.** For strict correctness, use a write freeze/cutover window or an application/CDC strategy that captures changes and applies them to the target. Then switch aliases atomically:

```http
POST _aliases
{
  "actions": [
    { "remove": { "index": "products-v1", "alias": "products" } },
    { "add": { "index": "products-v2", "alias": "products", "is_write_index": true } }
  ]
}
```

The alias operation is atomic at the cluster-state level, but the overall migration is only zero-downtime and correct if writes during the reindex are accounted for and validation succeeds. Aliases are not a distributed transaction with the source database. Plan rollback and index cleanup.

## 14. Ingest pipelines and collection tools

Use ingest processors or upstream collectors to parse and normalize records before indexing. Typical operations include date parsing, renaming, dropping sensitive fields, converting numeric strings, adding environment metadata, and routing malformed records to a quarantine path.

Example common-subset ingest pipeline:

```http
PUT _ingest/pipeline/normalize-app-log
{
  "description": "Normalize common application log fields",
  "processors": [
    { "set": { "field": "event.dataset", "value": "application" } },
    { "lowercase": { "field": "log.level", "ignore_missing": true } },
    { "remove": { "field": "debug_payload", "ignore_missing": true } }
  ]
}

POST logs-app-prod/_doc?pipeline=normalize-app-log
{
  "@timestamp": "2026-01-15T10:01:00Z",
  "log": { "level": "ERROR" },
  "service": { "name": "checkout" },
  "message": "payment provider timeout"
}
```

Processor names and options should be checked for the pinned product/version. Elasticsearch and OpenSearch both provide ingest processing, but processor availability and plugin support can differ.

Common tools in the ingest path:

- **Beats / Elastic Agent:** Elastic ecosystem collection and integration, depending on product/version and deployment.
- **Logstash:** pipeline-based parsing, enrichment, buffering, and routing.
- **Fluent Bit:** lightweight log processor/forwarder commonly used with containers and Kubernetes.
- **OpenTelemetry Collector:** vendor-neutral telemetry receiver/processor/exporter pipeline for logs, metrics, and traces.

Design for retries, backpressure, persistent buffers where needed, poison messages, duplicate events, timestamp normalization, redaction, and schema evolution. “The client returned 200” does not necessarily mean every item in a bulk response succeeded; inspect per-item results.

## 15. Elasticsearch versus OpenSearch: APIs, clients, vectors, and licensing

OpenSearch originated as a fork of Elasticsearch 7.10.2 and Kibana 7.10.2. Since the fork, the products have diverged in releases, features, APIs, plugins, and client compatibility. Shared syntax is useful for learning, but compatibility is not guaranteed.

| Area | Elasticsearch | OpenSearch |
|---|---|---|
| Dashboard | Kibana | OpenSearch Dashboards |
| Lifecycle | ILM (and deployment-specific data lifecycle capabilities) | ISM; lifecycle behavior/API differs |
| Python client | `elasticsearch` | `opensearch-py` |
| Vector fields/search | Elasticsearch vector types and query APIs depend on version/tier | `knn_vector` and k-NN plugin/query APIs depend on version/configuration |
| Hybrid search | Available approaches and retrievers depend on Elasticsearch version/features | Hybrid query/search pipeline features depend on OpenSearch version/plugins |
| Licensing | Elasticsearch licensing has changed over time; current source/distribution options include AGPLv3, ELv2 and/or SSPL depending on code/distribution; feature entitlements can differ | Core OpenSearch project is Apache 2.0; managed services may add proprietary service features and terms |
| Client/API compatibility | Match the official client to the Elasticsearch server version | Use the OpenSearch client and its compatibility matrix for OpenSearch |

For any commercial or managed deployment, read the current license and service terms rather than relying on a historical summary. Feature availability may depend on version, distribution, subscription, plugin, or managed-service offering.

### Vector and hybrid search awareness

A vector field stores an embedding generated by a model. k-NN search finds vectors close to a query vector according to a configured similarity/distance function. Hybrid search combines lexical relevance with semantic similarity, often with a product-specific score normalization or rank fusion mechanism.

Illustrative OpenSearch-style query (requires a compatible `knn_vector` mapping and k-NN plugin/configuration):

```http
GET products-vector/_search
{
  "size": 10,
  "query": {
    "knn": {
      "embedding": {
        "vector": [0.12, -0.04, 0.31, 0.08],
        "k": 10
      }
    }
  }
}
```

The vector values and dimension are examples only; real vectors must come from the same embedding model and match the mapping dimension. Hybrid query APIs are not identical across product versions. Do not copy an OpenSearch hybrid search pipeline into Elasticsearch or vice versa without checking the relevant documentation. For production RAG, evaluate retrieval quality, filtering, recall/latency, embedding versioning, deletion propagation, and access control—not only vector distance.

## 16. Search as a derived store: consistency and source-of-truth synchronization

The authoritative product/order/customer data usually lives in a transactional system. The search index is a **projection** optimized for retrieval and analytics. Treat it as rebuildable and potentially stale.

Recommended patterns:

- **Transactional outbox / CDC:** publish committed changes from the source database into a durable event stream; consumers project them into the search index.
- **Idempotent upserts:** use stable document IDs, version/timestamp checks, or source sequence numbers to prevent stale events overwriting newer state.
- **Delete propagation:** represent deletes as explicit events/tombstones and ensure they remove the derived document. A missing event can leave ghost search results.
- **Replay and rebuild:** preserve a replayable source/event log and make index rebuilds deterministic.
- **Reconciliation:** compare source counts, sampled IDs, versions, and key aggregates; monitor lag, failures, and dead-letter volume.
- **Backpressure:** retry bounded transient failures, pause or scale consumers when the cluster is unhealthy, and do not drop events silently.

Do not treat a successful search write as a transaction with the source database. There is no automatic cross-system atomic commit. Search results may lag behind a committed source update. Define freshness objectives and expose or tolerate that lag in the application.

## 17. Analytics extraction: PIT plus `search_after` to Parquet

Avoid deep pagination with large `from` offsets: the cluster must collect and discard many earlier hits. `search_after` uses the previous page's sort values. For a consistent export while writes continue, combine it with a **point in time (PIT)** snapshot where supported. PIT contexts retain resources, so close them promptly and use a reasonable keep-alive. If the pinned product/version does not support PIT, choose its documented alternative and understand the consistency trade-off. Scroll remains useful for some bulk extraction workflows but has different resource and snapshot semantics.

The following is an Elasticsearch Python-client example for versions whose client supports `open_point_in_time` and `close_point_in_time`. Check the equivalent method signatures in your pinned client. It streams batches into Parquet row groups rather than accumulating the full index in RAM.

```python
import os
from pathlib import Path
from elasticsearch import Elasticsearch
import pyarrow as pa
import pyarrow.parquet as pq

es = Elasticsearch(
    os.environ["ELASTICSEARCH_URL"],
    api_key=os.environ["ELASTICSEARCH_API_KEY"],
    request_timeout=60,
)

index_name = "products-v1"
out_path = Path("experiments/07_search/products-export.parquet")
out_path.parent.mkdir(parents=True, exist_ok=True)
tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")

# Explicit schema avoids page-to-page inference drift and defines the export contract.
arrow_schema = pa.schema([
    ("product_id", pa.string()),
    ("name", pa.string()),
    ("brand", pa.string()),
    ("category", pa.string()),
    ("description", pa.string()),
    ("price", pa.float64()),
    ("in_stock", pa.bool_()),
    ("updated_at", pa.string()),
    ("tags", pa.list_(pa.string())),
])

pit_id = None
writer = None
rows_written = 0
expected_total = None
search_after = None
completed = False
try:
    pit = es.open_point_in_time(index=index_name, keep_alive="2m")
    pit_id = pit["id"]
    while True:
        body = {
            "size": 1000,
            "pit": {"id": pit_id, "keep_alive": "2m"},
            "query": {"match_all": {}},
            "sort": [
                {"product_id": {"order": "asc"}},
                {"_shard_doc": "asc"}
            ],
            # Exact count is useful for this validation lab, but adds work on large indices.
            "track_total_hits": True,
        }
        if search_after is not None:
            body["search_after"] = search_after
        response = es.search(body=body)
        pit_id = response.get("pit_id", pit_id)
        if expected_total is None:
            total = response["hits"].get("total", 0)
            expected_total = total["value"] if isinstance(total, dict) else total
        hits = response["hits"]["hits"]
        if not hits:
            break

        rows = []
        for hit in hits:
            source = hit.get("_source", {})
            rows.append({
                "product_id": source.get("product_id"),
                "name": source.get("name"),
                "brand": source.get("brand"),
                "category": source.get("category"),
                "description": source.get("description"),
                "price": source.get("price"),
                "in_stock": source.get("in_stock"),
                "updated_at": source.get("updated_at"),
                "tags": source.get("tags"),
            })
        table = pa.Table.from_pylist(rows, schema=arrow_schema)
        if writer is None:
            writer = pq.ParquetWriter(tmp_path, arrow_schema, compression="zstd")
        writer.write_table(table, row_group_size=1000)
        rows_written += len(rows)
        search_after = hits[-1]["sort"]

    if writer is not None:
        writer.close()
        writer = None
    expected_total = expected_total if expected_total is not None else 0
    if rows_written != expected_total:
        raise RuntimeError(f"Export count mismatch: wrote {rows_written}, PIT reported {expected_total}")
    if rows_written:
        check = pq.ParquetFile(tmp_path)
        if check.metadata.num_rows != rows_written or check.schema_arrow != arrow_schema:
            raise RuntimeError("Parquet validation failed: row count or schema mismatch")
    else:
        pq.write_table(pa.Table.from_pylist([], schema=arrow_schema), tmp_path, compression="zstd")
    os.replace(tmp_path, out_path)  # Publish only after count/schema validation succeeds.
    completed = True
finally:
    try:
        if writer is not None:
            writer.close()
    finally:
        try:
            if pit_id is not None:
                es.close_point_in_time(id=pit_id)
        finally:
            es.close()
            if not completed and tmp_path.exists():
                tmp_path.unlink()

print({"rows_written": rows_written, "expected_total": expected_total, "output": str(out_path)})
```

**Important engineering notes:**

- `_shard_doc` is suitable as a PIT-local tie-breaker for this export style, but the sort fields and response shape must match your server/client version. Do not use a non-unique sort with live `search_after` pagination.
- Mapping to Parquet requires a stable schema. Real datasets may have missing fields, nested objects, mixed types, or arrays; define a target Arrow schema and normalize values rather than relying blindly on `Table.from_pylist` inference.
- For a long export, renew `keep_alive` in every request and monitor PIT resource use. This sample restarts from the beginning after a failure and removes the temporary file; it does not implement durable resume checkpoints. A resumable export needs a durable cursor plus a valid PIT lifecycle strategy, and must still validate duplicates/gaps before publishing. The sample publishes to a temporary file and replaces the final path only after row-count and schema validation.
- Exporting a search projection does not make it the authoritative analytics source if the source index is stale or fields were transformed/lost during indexing. Prefer the canonical source/lakehouse ingestion path when it meets the requirement.
- For OpenSearch, use `opensearch-py` and the matching PIT/close API signatures documented for the pinned version. The REST concepts are similar, but do not assume Python method signatures are identical.

### Export verification

1. Record the query, source index, mapping, PIT start time, and expected document-count strategy.
2. Check export row count against a reliable count for the same snapshot or reconcile IDs/counts with the source.
3. Read the Parquet file back with PyArrow and inspect schema, null counts, duplicate IDs, and timestamp bounds.
4. Validate representative rows and aggregates against the source projection.
5. Keep the export temporary until validation passes; then atomically publish or move it to the downstream landing location.

## 18. Hands-on lab workspace: `experiments/07_search/`

Create one workspace for all labs:

```text
experiments/07_search/
├── README.md
├── docker-compose.yml
├── .env.example
├── scripts/
│   ├── generate_products.py
│   ├── bulk_index_products.py
│   ├── export_products.py
│   └── generate_logs.py
├── queries/
│   ├── product-mapping.json
│   ├── analyzer-synonyms.json
│   ├── product-search.json
│   └── log-aggregations.json
├── data/
│   └── (generated local files; do not commit secrets or huge artifacts)
└── output/
    └── (metrics, Parquet export, and validation summaries)
```

Pin a server image version in Compose rather than using `latest`. Choose either Elasticsearch plus Kibana or OpenSearch plus Dashboards. Do not run a mixed stack accidentally. For a local lab, set a bounded heap and a named volume; follow the chosen image's current security/bootstrap instructions. A minimal OpenSearch single-node lab may use the official image's documented demo security configuration; keep it bound to localhost and never reuse demo credentials in production. Elasticsearch images commonly enable security by default. Because bootstrap details change, copy the Compose block from the official documentation for the exact version you pin and record that version in `README.md`.

### Lab 1 — Index a product catalogue and progressively develop queries

1. Create `products-v1` using the explicit mapping in Section 5.
2. Index at least 10 hand-written products with distinct brands, categories, prices, stock states, and names.
3. Run `match_all`, then `match`, then `multi_match`, then `bool` with filters.
4. Add a `brand` terms aggregation and a price histogram.
5. Save each request/response or a short observation in the lab README.

**Test cases:** search for a common word, a rare word, a phrase with a hyphen, an exact brand, a price range, and an out-of-stock item.  
**Expected observations:** full-text and exact filters behave differently; filters narrow matches without adding relevance score; aggregation buckets summarize the filtered result set. Actual hit counts depend on your generated records and must be recorded from your run.

### Lab 2 — Inspect `_analyze`

Run the `_analyze` requests from Section 6 with `standard`, the field analyzer, and your custom analyzer. Compare token text and positions. Test punctuation, capitalization, plurals, and synonym terms.  
**Expected observation:** tokenization and filters explain why some terms match and others do not. Do not claim a particular token list without checking the analyzer in your actual version.

### Lab 3 — Explicit mappings and bulk-index 200,000 products

Generate reproducible synthetic products. Use a fixed random seed and stable IDs; the following script creates JSON Lines without a third-party faker dependency:

```python
# experiments/07_search/scripts/generate_products.py
import json
import random
from pathlib import Path

rng = random.Random(20261019)
brands = ["Acme Audio", "StudioCo", "Northstar", "Contoso", "Fabrikam"]
categories = ["audio", "home", "computing", "outdoor"]
adjectives = ["Wireless", "Portable", "Compact", "Professional", "Smart", "Durable"]
products = ["Headphones", "Speaker", "Keyboard", "Camera", "Lamp", "Router"]

out = Path("experiments/07_search/data/products.jsonl")
out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", encoding="utf-8") as f:
    for i in range(200_000):
        doc = {
            "product_id": f"p-{i:06d}",
            "name": f"{rng.choice(adjectives)} {rng.choice(products)} {i}",
            "brand": rng.choice(brands),
            "category": rng.choice(categories),
            "description": f"{rng.choice(adjectives)} product for everyday use; model {i}",
            "price": round(rng.uniform(5, 2000), 2),
            "in_stock": rng.random() < 0.82,
            # Fixed UTC timestamp keeps the complete generated dataset reproducible.
            "updated_at": "2026-01-01T00:00:00+00:00",
            "tags": [rng.choice(categories)],
        }
        f.write(json.dumps(doc) + "\n")
print(f"Wrote {out}")
```

For reproducible timestamps, you may set one fixed timestamp instead of `datetime.now`; the random seed controls choices but not wall-clock time. To make the entire dataset byte-for-byte reproducible, use a fixed timestamp and stable JSON serialization.

Bulk-index using streaming actions:

```python
# experiments/07_search/scripts/bulk_index_products.py
import json
import os
import time
from pathlib import Path
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch(os.environ["ELASTICSEARCH_URL"], api_key=os.environ["ELASTICSEARCH_API_KEY"], request_timeout=120)
source = Path("experiments/07_search/data/products.jsonl")

def actions():
    with source.open(encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            yield {"_op_type": "index", "_index": "products-v1", "_id": doc["product_id"], "_source": doc}

start = time.perf_counter()
ok = 0
failed = 0
for success, item in helpers.streaming_bulk(
    es, actions(), chunk_size=1000, max_chunk_bytes=10 * 1024 * 1024,
    raise_on_error=False, raise_on_exception=False, request_timeout=120,
):
    if success:
        ok += 1
    else:
        failed += 1
es.indices.refresh(index="products-v1")
elapsed = time.perf_counter() - start
result = {"success": ok, "failed": failed, "elapsed_seconds": elapsed, "docs_per_second": ok / elapsed if elapsed else None}
print(result)
if failed:
    raise SystemExit(f"Bulk indexing had {failed} failed item(s); inspect item-level errors before proceeding")
if ok != 200_000:
    raise SystemExit(f"Expected 200000 successful items, observed {ok}")
count = es.count(index="products-v1")["count"]
if count != 200_000:
    raise SystemExit(f"Expected 200000 documents after refresh, observed {count}")
```

If you are using OpenSearch, replace the imports/client with `opensearchpy` and use the OpenSearch authentication for your environment. Confirm the destination mapping matches the generated document fields. The bulk script prints **your measured results**; do not copy those values into a report as if they were known in advance.

**Measurement methodology:** record server/client versions, CPU/memory, shard and replica settings, refresh interval, bulk chunk size, document count, failures, elapsed wall time, and throughput. Run at least three trials after a warm-up if comparing configurations; report median and range, and do not compare runs with different hardware or load without noting it. Never disable replicas or refreshes in production merely to improve a benchmark.

**Verification:** refresh once after the bulk load, query `products-v1/_count`, confirm expected count, inspect `_cat/indices`, and check per-item failures. Count mismatch is a failure to investigate, not a result to explain away.

### Lab 4 — Compare `text` and `keyword`

Create fields such as `brand_text` (`text`) and `brand` (`keyword`) or use the `name`/`name.keyword` multi-field. Run `match` and `term` against both. Test case differences and punctuation.  
**Expected observation:** analyzed fields are token-oriented; keyword fields preserve a whole value for exact matching/aggregation. Exact behavior depends on the mapping and any normalizer.

### Lab 5 — Custom analyzer and synonyms

Create the synonym-aware index in Section 6. Index documents containing `television` and `cell phone`; compare results for `tv` and `smartphone` with the synonym filter enabled and disabled. Keep the same documents and query set between runs.  
**Measurement:** count relevant documents returned in top-k for a manually defined query set; record false positives as well as recall. This is a small qualitative lab, not a statistically conclusive search-quality benchmark.

### Lab 6 — Boolean filters and faceted aggregations

Implement the `bool` query from Section 7 and brand/price aggregations from Section 9. Verify that changing a price filter changes both hits and the aggregation buckets. Compare `size: 0` for aggregation-only requests.  
**Expected observation:** filtering occurs before the aggregation over the matching document set unless a filter aggregation intentionally defines a separate scope.

### Lab 7 — Synthetic application logs into a data stream with rollover and lifecycle

1. Create a template and lifecycle policy for the product you selected (Elasticsearch ILM **or** OpenSearch ISM); do not mix APIs.
2. Define `@timestamp`, `message`, `log.level`, `service.name`, and `http.duration_ms` mappings.
3. Generate synthetic events with multiple services, levels, and timestamps.
4. Bulk-index events through the data stream name, not a concrete backing index.
5. For a lab only, use a low rollover threshold supported by your product version so rollover can be observed quickly; restore realistic thresholds before any production deployment.
6. Inspect the data stream/backing indices, lifecycle status, document counts, and date-histogram aggregations.

**Expected observation:** writes target the current write backing index, while searches across the stream cover its backing indices. Rollover timing depends on policy execution and the chosen threshold; do not assume it occurs immediately when a threshold is crossed. Verify actual state with the product's lifecycle explain/status APIs.

### Lab 8 — Reindex to a new mapping behind an alias

1. Put application traffic through `products` alias.
2. Create `products-v2` with the changed mapping or analyzer.
3. Run `_reindex` and poll the task; capture and inspect failures/conflicts.
4. Replay concurrent changes from an outbox/CDC log or run a controlled write pause.
5. Compare counts, sample IDs, queries, and aggregations.
6. Switch the alias with one `_aliases` request; test read/write behavior; retain `products-v1` for rollback.

**Acceptance criteria:** no unexplained missing IDs; all updates after the copy are represented; query behavior is tested; alias switch succeeds atomically; rollback steps are documented. Merely getting a successful `_reindex` task is not proof that concurrent writes were captured.

### Lab 9 — Export to Parquet with PIT and `search_after`

1. Install `pyarrow` and use the extraction script in Section 17.
2. Export a defined index and query with PIT and deterministic sorting.
3. Read the output with `pyarrow.parquet.read_table` and check schema, row count, nulls, and a sample of IDs.
4. Compare counts against a consistent snapshot or use source reconciliation. Do not compare a PIT snapshot to a live count if writes are occurring and assume they must match.
5. Close the PIT in a `finally` block, and remove the temporary output if validation fails.

**Acceptance criteria:** export can run in bounded memory, paging uses the last hit's `sort` array, the same PIT is maintained/updated according to the client API, Parquet schema is stable, and the output is only published after validation.

## 19. Common mistakes and production failure modes

- Using `term` on a `text` field and expecting analyzed full-text behavior.
- Aggregating on analyzed text rather than a `keyword` field or suitable multi-field.
- Letting dynamic mapping ingest arbitrary keys without a schema/field-count budget.
- Changing index-time analyzers and expecting existing documents to be re-tokenized automatically.
- Assuming a successful bulk HTTP response means every item succeeded.
- Calling refresh after every document and creating excessive small segments.
- Creating too many small shards or choosing shard count without measuring primary data size and query load.
- Treating one-node lab health warnings as proof of production health, or ignoring production yellow/red health.
- Copying ILM syntax into OpenSearch ISM, or mixing client libraries and APIs without checking compatibility.
- Assuming `_reindex` captures concurrent writes, or that alias switching is a transaction with the source database.
- Deep-paging with large `from` offsets; using PIT without closing it; using `search_after` without a deterministic sort.
- Assuming vector similarity alone yields good hybrid retrieval, or assuming vector APIs are identical across products.
- Storing the only copy of business data in the search index or assuming search indexing is exactly-once and strongly consistent with the source.

## 20. Practice questions

1. Explain the path from source JSON to tokens, postings, and a scored search result.
2. When would you map a field as `text`, `keyword`, `date`, `nested`, or numeric?
3. Why can a `term` query against a `text` field return unexpected results?
4. What does `_score` mean, and why is it not a probability?
5. How do `must`, `should`, `filter`, and `must_not` differ?
6. What are metric, bucket, and pipeline aggregations? Give one example of each.
7. What is near-real-time about search visibility? Why is refresh not a durability operation?
8. What operational symptoms suggest over-sharding or a hot node?
9. How do data streams and lifecycle policies reduce operational toil for logs?
10. What differs between Elasticsearch ILM and OpenSearch ISM?
11. Why does reindexing require a concurrent-write strategy?
12. When is PIT plus `search_after` safer than `from`/`size`? What resources does PIT hold?
13. How should a data engineer propagate source updates and deletes into a derived search index?
14. What must be evaluated before adding vector or hybrid search to product discovery?
15. What evidence would you collect before claiming one analyzer or mapping improves relevance or throughput?

## 21. Checkpoints and final self-assessment

Mark each item only after you can demonstrate it in the running lab, not merely explain it from memory.

- [ ] I can explain clusters, nodes, indices, documents, shards, and replicas.
- [ ] I can index and search a product document and interpret `hits` and `_score`.
- [ ] I can design explicit mappings, use `text`/`keyword`/multi-fields, and prevent mapping explosion.
- [ ] I can inspect analyzer tokens and demonstrate a custom synonym analyzer.
- [ ] I can write a `bool` query with relevance clauses, exact filters, ranges, and boosts.
- [ ] I can build metric, bucket, and pipeline aggregations for product facets and log trends.
- [ ] I can bulk-index 200,000 synthetic documents, inspect item failures, and record reproducible measurements.
- [ ] I can explain refresh intervals and near-real-time visibility.
- [ ] I can create a log data stream and a product-appropriate ILM or ISM lifecycle policy.
- [ ] I can estimate shard needs, identify over-sharding/hot-node symptoms, and define monitoring.
- [ ] I can migrate mappings with a versioned index and alias while accounting for concurrent writes.
- [ ] I can explain ingest pipelines, Logstash, Beats/Elastic Agent, Fluent Bit, and OpenTelemetry Collector roles.
- [ ] I can describe the version, client, API, lifecycle, vector, and licensing differences between Elasticsearch and OpenSearch.
- [ ] I can export to Parquet with PIT and `search_after`, validate the file, and close PIT resources.
- [ ] I can explain why the search index is a derived store and design replay, delete propagation, and reconciliation.

**Ready to move on when:** all required labs run successfully, failures are explained, actual measurements are recorded with environment details, and you can defend mapping, lifecycle, shard, and synchronization decisions. The goal is not to memorize every API; it is to make deliberate design choices and verify behavior on the exact product/version deployed.

## 22. Further reading and version checks

Use current official documentation for the exact server/client version you pin:

- Elasticsearch reference: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
- Elasticsearch ILM concepts: https://www.elastic.co/guide/en/elasticsearch/reference/current/ilm-concepts.html
- Elasticsearch Python client: https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html
- OpenSearch documentation: https://docs.opensearch.org/latest/
- OpenSearch data streams: https://docs.opensearch.org/latest/opensearch/data-streams/
- OpenSearch PIT: https://docs.opensearch.org/latest/search-plugins/searching-data/point-in-time/
- OpenSearch Python client: https://docs.opensearch.org/latest/clients/python-low-level/
- OpenSearch k-NN: https://docs.opensearch.org/latest/query-dsl/specialized/k-nn/index/
- OpenSearch project FAQ/licensing: https://opensearch.org/faq/

Always record the server version, dashboard version, client version, plugins, and lifecycle mechanism in the experiment README. Documentation for `current` changes over time; for a production runbook, use versioned documentation matching the deployed release.
