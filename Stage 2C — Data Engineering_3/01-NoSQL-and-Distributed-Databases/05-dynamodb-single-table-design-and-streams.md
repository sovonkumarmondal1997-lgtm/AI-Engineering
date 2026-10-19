# DynamoDB: Single-Table Design and Streams

> **Stage:** Stage 2C — Data Engineering_3  
> **Module:** 01-NoSQL-and-Distributed-Databases  
> **Topic:** 05  
> **Level:** Beginner → Intermediate → Advanced  
> **Lab directory:** `experiments/05_dynamodb/`  
> **Primary implementation:** AWS DynamoDB with Python `boto3`; DynamoDB Local for local development

## 1. Why this topic matters

DynamoDB is a managed, distributed key-value and document database designed for predictable, low-latency access at scale. It is common in event-driven and serverless AWS applications. For data engineers, its most important lesson is that **the data model follows the application's access patterns**. DynamoDB Streams and export facilities also make the operational database a source for downstream processing, but a change feed is not automatically a complete lakehouse ingestion architecture.

This topic follows the module's NoSQL-family and consistency foundations, MongoDB document modelling, and Cassandra query-first partition design. It prepares you for the later module on change streams and NoSQL-to-lakehouse ingestion. The same e-commerce domain is used throughout: customers, orders, order items, and addresses.

## 2. Learning objectives

By the end, you should be able to:

- Explain DynamoDB tables, items, attributes, scalar/document/set types, partition keys, and optional sort keys.
- Choose `GetItem` or `Query` for known-key access and explain why an unnecessary `Scan` is expensive.
- Derive a table and index design from explicit access patterns rather than from entity diagrams alone.
- Model customers, orders, items, and addresses in one table with generic `PK` and `SK` attributes, two GSIs, and a sparse index for open orders.
- Compare on-demand and provisioned capacity and estimate read/write capacity units (RCUs/WCUs) without inventing benchmark results.
- Use `boto3` resource and low-level client APIs, paginate results, handle batch-operation unprocessed items, and rely on bounded retries for transient throttling.
- Implement conditional writes, optimistic locking, atomic updates, TTL, and transactional writes safely.
- Explain hot partitions, adaptive capacity, write sharding, consistency modes, and global-table trade-offs.
- Build a stream consumer that processes change records idempotently and writes Parquet to object storage.
- Distinguish DynamoDB Streams, Kinesis Data Streams for DynamoDB, S3 exports, incremental exports, and zero-ETL integrations.
- Plan backup, point-in-time recovery, cost controls, and production verification.

## 3. Prerequisites and dependency order

This lesson assumes the module prerequisites from Stage 2 and Stage 2B:

- Python, JSON, type hints, packaging, and basic exception handling.
- SQL, transactions, isolation, normalisation and denormalisation.
- OLTP versus OLAP, batch versus streaming, incremental extraction, idempotent loads, and deduplication.
- AWS fundamentals (IAM and S3), Docker Compose, and basic event-driven processing.
- Topic 01 NoSQL families and trade-offs; Topic 02 consistency models; Topic 03 document modelling; Topic 04 Cassandra partition design.

Recommended learning sequence: fundamentals → list access patterns → design keys/indexes on paper → implement and test locally → introduce conditional writes and capacity → study streams and analytics extraction → test operational failure cases.

## 4. Terminology and mental model

| Term | Meaning |
|---|---|
| Table | Collection of items; items in a table do not need identical non-key attributes. |
| Item | A group of attributes, identified by the table's primary key. |
| Attribute | A named value, such as `customerName`, `status`, or `total`. |
| Partition key | Required primary-key component. DynamoDB hashes it to distribute items across physical partitions. |
| Sort key | Optional second primary-key component. Items sharing a partition key are ordered by sort-key value. |
| Primary key | Partition key alone (simple key) or partition key plus sort key (composite key). |
| Item collection | Items sharing one partition-key value in a table; with a composite key they can represent related entities. |
| GSI | Global secondary index; has its own partition and optional sort key and can use a different key schema from the base table. |
| LSI | Local secondary index; uses the base table's partition key but a different sort key. Must be defined at table creation. |
| Projection | Attributes copied into an index: `KEYS_ONLY`, `INCLUDE`, or `ALL`. |
| Sparse index | An index containing only items that possess the index key attributes. |
| RCU/WCU | Read/write capacity units used by provisioned-capacity billing and throttling calculations. |
| Conditional write | Write succeeds only if a condition expression evaluates true. |
| Stream record | Change record emitted for an item mutation, depending on stream view type. |
| Idempotency | Reprocessing the same event does not produce an additional incorrect side effect. |

DynamoDB supports scalar types such as string, number, and binary; document types such as map and list; and sets of strings, numbers, or binary values. An item is limited to 400 KB including attribute names and values; large nested documents can hit this limit sooner than expected. Empty values and key attributes have service-specific constraints: partition and sort key attributes must be scalar string, number, or binary types, and key attributes cannot be empty. Do not treat DynamoDB as schemaless: key definitions, validation in application code, and operational invariants form the schema.

## 5. DynamoDB fundamentals

### 5.1 Tables, keys, and data distribution

A table's partition key determines how items are distributed. A composite primary key allows multiple items to share a partition-key value, with the sort key identifying and ordering those items. The same partition key groups related records into an item collection, which is useful for access patterns such as “customer and all their orders.”

```text
Application key
    │
    ▼
Partition-key hashing ──► physical partition placement
                              │
                              ├── item PK=CUSTOMER#c-17, SK=PROFILE
                              ├── item PK=CUSTOMER#c-17, SK=ADDRESS#HOME
                              └── item PK=CUSTOMER#c-17, SK=ORDER#2026-10-18#o-82
```

This is a logical picture, not a promise that all items remain on one immutable physical partition. DynamoDB manages physical placement and partition splits. Good key design spreads activity while keeping the items required for a query addressable by known keys.

### 5.2 Core operations

| Operation | Purpose | Engineering guidance |
|---|---|---|
| `PutItem` | Create or replace an item at its key | Without a condition, it can overwrite an existing item. Use conditions for create-only semantics. |
| `GetItem` | Retrieve one item by its complete primary key | Usually the most direct access path; request `ConsistentRead=True` when a strong read is required and supported. |
| `UpdateItem` | Update selected attributes or create an item if absent | Use update expressions and conditions; consider whether upsert behavior is intended. |
| `DeleteItem` | Delete an item by primary key | Use a condition when deletion must depend on state/version. |
| `Query` | Retrieve items for one partition-key value, optionally narrowing the sort key | Design the primary key or index for the access pattern. It can return multiple pages. |
| `Scan` | Examine items across a table or index | Reads items that match the scan traversal; a filter does not make the underlying read selective. Use for controlled maintenance/analytics, not routine request paths. |

DynamoDB is not a relational database with unrestricted joins and predicates. A `Query` must specify equality on the partition key; sort-key conditions can narrow the range. A `FilterExpression` is applied after items are read and does not reduce the read capacity consumed for the evaluated items. `Scan` can be parallelized, but parallel scans still read the table/index and can compete with production traffic.

### 5.3 Strong and eventual consistency

- Reads from a table or LSI can request strong consistency; eventual consistency is the default and costs less read capacity for the same item size.
- GSI reads are eventually consistent; they do not support `ConsistentRead=True`.
- DynamoDB Streams is a change feed, not a substitute for a strongly consistent application read.
- Global tables replicate across Regions. Replication is asynchronous; multi-Region consistency options and conflict behavior depend on the configured global-table mode and service evolution. Do not assume cross-Region reads instantly reflect every write. Verify the chosen mode and current AWS documentation before relying on conflict-resolution semantics.

### 5.4 Query versus scan: a practical rule

If the application can state the partition-key value for a request, prefer `GetItem` or `Query`. A scan is reasonable for a bounded administrative job, migration, or analytics extraction when its capacity and impact are planned. A scan plus filter is not equivalent to an indexed lookup.

## 6. Access-pattern-first modelling

### 6.1 Start with queries, not entities

An entity diagram tells you what exists. An access-pattern list tells you what the application must retrieve efficiently. Write down for every pattern:

1. Who calls it, how often, and with what latency requirement?
2. Which key values are known at request time?
3. How many items can be returned, and in what order?
4. Does the query need one item, a bounded collection, or a large export?
5. What consistency is required?
6. Which writes must be atomic together?
7. How will the data expire, change, and feed analytics?

### 6.2 Eight required access patterns

The following design uses one table named `Commerce` with `PK` (string) and `SK` (string). Two GSIs are defined: `GSI1` with `GSI1PK`/`GSI1SK`, and `GSI2` with `GSI2PK`/`GSI2SK`. The design is intentionally explicit; the exact index keys can be overloaded for multiple item types.

| # | Access pattern | Operation | Key condition / key values | Index |
|---:|---|---|---|---|
| 1 | Get a customer's profile | `GetItem` | `PK=CUSTOMER#<customerId>`, `SK=PROFILE` | Base table |
| 2 | List a customer's addresses | `Query` | `PK=CUSTOMER#<customerId>`, `begins_with(SK, 'ADDRESS#')` | Base table |
| 3 | List a customer's orders newest-first | `Query` | `PK=CUSTOMER#<customerId>`, `begins_with(SK, 'ORDER#')`, descending sort order | Base table |
| 4 | Get one order by order ID | `GetItem` | `PK=ORDER#<orderId>`, `SK=DETAILS` | Base table |
| 5 | List items for one order | `Query` | `PK=ORDER#<orderId>`, `begins_with(SK, 'ITEM#')` | Base table |
| 6 | List orders by status (for example, all open orders) | `Query` | `GSI1PK=STATUS#OPEN`, sort by `GSI1SK` | GSI1 sparse index |
| 7 | Find a customer by email | `Query` | `GSI2PK=EMAIL#<normalizedEmail>`, `GSI2SK=PROFILE` | GSI2 |
| 8 | List orders for a customer within a time range | `Query` | `PK=CUSTOMER#<customerId>`, `SK BETWEEN 'ORDER#<start>#' AND 'ORDER#<end>#~'` | Base table |

Pattern 3 and 8 use the same customer-order item collection. If a production requirement needs a different sort order or filtering dimension, define the exact key encoding and index needed rather than relying on a post-read filter. For date-range keys, use one canonical sortable UTC timestamp representation (for example ISO-8601 fixed-width UTC) and test lexical ordering at boundaries.

## 7. Worked single-table design

### 7.1 Key conventions

Use readable, namespaced keys. Prefixes make item types and relationships visible during debugging:

- `PK=CUSTOMER#<customerId>` for a customer's profile, addresses, and customer-centric order summaries.
- `PK=ORDER#<orderId>` for order details and order items.
- `SK=PROFILE`, `SK=ADDRESS#<addressType>`, `SK=ORDER#<createdAt>#<orderId>`, `SK=DETAILS`, and `SK=ITEM#<itemId>`.
- Duplicate a limited order summary under the customer partition so customer order history can be queried without a join.

The duplicated customer order summary is deliberate denormalization. Updating both copies consistently requires an explicit write strategy; if the two items must always change atomically, use a transaction where feasible or design the application to tolerate and reconcile eventual projection updates.

### 7.2 Example item shapes

| Entity | PK | SK | Other attributes |
|---|---|---|---|
| Customer profile | `CUSTOMER#c-17` | `PROFILE` | `entityType=CUSTOMER`, `name`, `email`, `createdAt`, `version` |
| Address | `CUSTOMER#c-17` | `ADDRESS#HOME` | `entityType=ADDRESS`, `line1`, `city`, `postalCode`, `isDefault` |
| Customer order summary | `CUSTOMER#c-17` | `ORDER#2026-10-18T10:30:00Z#o-82` | `entityType=ORDER_SUMMARY`, `orderId`, `status`, `total`, `createdAt` |
| Order details | `ORDER#o-82` | `DETAILS` | `entityType=ORDER`, `customerId`, `status`, `total`, `createdAt`, `version` |
| Order item | `ORDER#o-82` | `ITEM#sku-501` | `entityType=ORDER_ITEM`, `sku`, `quantity`, `unitPrice`, `lineTotal` |

For customer profile items, `GSI2PK=EMAIL#<normalizedEmail>` and `GSI2SK=PROFILE`. Normalise email consistently in the application (trim and case-fold according to your identity policy) and treat uniqueness as a business invariant. A GSI alone does not enforce uniqueness: if concurrent registrations must guarantee one account per email, use a dedicated uniqueness item and a conditional/transactional write design.

For open orders, only open order records receive `GSI1PK=STATUS#OPEN` and a `GSI1SK` such as `<createdAt>#<orderId>`. Closed or cancelled order items omit both GSI1 key attributes. This makes GSI1 sparse: the index stores only items with the index key attributes. The item must be updated to remove those attributes when its status is no longer open. Because GSI propagation is asynchronous, status queries through the GSI are eventually consistent.

### 7.3 Two GSIs and the sparse-index design

**GSI1 — Open orders by creation time**

- Partition key: `GSI1PK` (string), value `STATUS#OPEN`.
- Sort key: `GSI1SK` (string), value `<createdAt>#<orderId>`.
- Projection: `INCLUDE` only the attributes needed by the open-orders work queue, for example `orderId`, `customerId`, `status`, `total`, and `createdAt` (plus index keys automatically available).
- Sparse behavior: only active/open order items have GSI1 keys.
- Trade-off: the constant `STATUS#OPEN` can become a hot GSI partition if traffic or item volume is concentrated. If the operational queue becomes very high-volume, shard the status partition, for example `STATUS#OPEN#00` through `STATUS#OPEN#0F`, and query all shards. This makes reads more complex and requires a deterministic, well-distributed shard function.

**GSI2 — Customer lookup by email**

- Partition key: `GSI2PK`, value `EMAIL#<normalizedEmail>`.
- Sort key: `GSI2SK`, value `PROFILE` (or a stable account key if multiple profiles are intentionally allowed).
- Projection: `KEYS_ONLY` if the caller can retrieve the profile from the base table; otherwise `INCLUDE` the small attributes required by the lookup.
- Trade-off: GSI2 is eventually consistent and adds write/storage cost. Email changes must update the index attributes correctly.

**LSI versus GSI:** An LSI keeps the base table's partition key and adds an alternate sort key; it must be declared when the table is created, can support strongly consistent reads, and the item collection for a partition key with LSIs is subject to a 10 GB limit. A GSI can use a different partition key, can be added after table creation, and is always eventually consistent. This design uses two GSIs because the status and email lookups need access paths different from the base-table partition key; it does not need an LSI. The base table and indexes are not free joins. Index keys are maintained as items change, projected attributes occupy index storage, and index backfill/propagation can affect deployment and operational planning.

**GSI overloading:** A GSI key namespace can represent more than one entity/query family when the access patterns share compatible key semantics. For example, `GSI1PK=STATUS#OPEN` with a time-ordered `GSI1SK` can index open orders, while `GSI1PK=SHIPMENT#PENDING` with a compatible time-ordered sort key could index pending shipments in the same GSI. Each item type must populate the index attributes intentionally, and the query contract must specify the namespace and sort-key encoding. Do not overload an index merely to reduce index count if it creates ambiguous keys or hot partitions.

### 7.4 Access-pattern walkthroughs

1. **Customer profile:** complete primary key known, so use `GetItem`; no query fan-out.
2. **Addresses:** one partition key and sort-key prefix, so `Query` returns only address items. The address collection is naturally bounded by business rules.
3. **Order history:** customer partition with `ORDER#` sort keys; use descending order to get recent orders first. Paginate if a customer has many orders.
4. **Order detail:** order partition plus `DETAILS` sort key; direct `GetItem`.
5. **Order items:** order partition plus `ITEM#` prefix. Keep order item count within expected operational limits; for unusually large orders, model separately.
6. **Open orders:** `Query` GSI1 by `STATUS#OPEN`, with optional time-range condition on `GSI1SK`. Since this is a GSI, results are eventually consistent.
7. **Email lookup:** `Query` GSI2 by exact normalized email. If the GSI returns a key but the base item has since changed, handle the race and use conditional uniqueness writes for registration.
8. **Customer order time range:** `Query` base table using `PK=CUSTOMER#...` and a bounded `SK BETWEEN` condition. Avoid time encodings that do not sort lexically.

### 7.5 Readable access-pattern matrix for implementation

```text
Base table Commerce (PK, SK)
  CUSTOMER#c-17 / PROFILE
  CUSTOMER#c-17 / ADDRESS#HOME
  CUSTOMER#c-17 / ADDRESS#WORK
  CUSTOMER#c-17 / ORDER#2026-10-18T10:30:00Z#o-82   (summary)
  ORDER#o-82     / DETAILS
  ORDER#o-82     / ITEM#sku-501

GSI1 (GSI1PK, GSI1SK): STATUS#OPEN / 2026-10-18T10:30:00Z#o-82
GSI2 (GSI2PK, GSI2SK): EMAIL#buyer@example.com / PROFILE
```

Do not put an entire order with all items into a single DynamoDB item by default. Separate item records support bounded access and avoid item-size limits, but the application must explicitly model atomicity and consistency across related records.

### 7.6 When not to use one table

Separate tables are reasonable when workloads have different security boundaries, retention/backup policies, throughput patterns, ownership teams, access patterns, lifecycle requirements, or operational blast radii. Single-table design is not a contest to minimise table count. It is a strategy for grouping access patterns that benefit from shared partition-key item collections and predictable query paths.

## 8. Query and index implementation

### 8.1 Create the table and GSIs

The following AWS CLI example creates a table with a composite primary key and two GSIs. It is intended for a current AWS CLI v2 environment. Billing mode is on-demand for a low-friction lab; a production workload should choose capacity mode based on traffic predictability and cost measurements.

```bash
aws dynamodb create-table \
  --table-name Commerce \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
    AttributeName=GSI1PK,AttributeType=S \
    AttributeName=GSI1SK,AttributeType=S \
    AttributeName=GSI2PK,AttributeType=S \
    AttributeName=GSI2SK,AttributeType=S \
  --key-schema AttributeName=PK,KeyType=HASH AttributeName=SK,KeyType=RANGE \
  --global-secondary-indexes '[
    {"IndexName":"GSI1","KeySchema":[{"AttributeName":"GSI1PK","KeyType":"HASH"},{"AttributeName":"GSI1SK","KeyType":"RANGE"}],"Projection":{"ProjectionType":"INCLUDE","NonKeyAttributes":["entityType","orderId","customerId","status","total","createdAt"]}},
    {"IndexName":"GSI2","KeySchema":[{"AttributeName":"GSI2PK","KeyType":"HASH"},{"AttributeName":"GSI2SK","KeyType":"RANGE"}],"Projection":{"ProjectionType":"KEYS_ONLY"}}
  ]' \
  --billing-mode PAY_PER_REQUEST
```

The `AttributeDefinitions` list contains key attributes only, not every application attribute. If you need a different index projection, adjust the GSI definition before creating the table. The table's base key schema cannot be changed in place; redesigning the primary key generally means creating a new table and migrating data.

### 8.2 Query with the boto3 resource API

```python
from __future__ import annotations

from typing import Any
import boto3
from boto3.dynamodb.conditions import Key

# For AWS, use a role/profile and region. For DynamoDB Local, supply endpoint_url.
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("Commerce")


def get_customer(customer_id: str) -> dict[str, Any] | None:
    response = table.get_item(
        Key={"PK": f"CUSTOMER#{customer_id}", "SK": "PROFILE"},
        ConsistentRead=True,
    )
    return response.get("Item")


def list_addresses(customer_id: str) -> list[dict[str, Any]]:
    response = table.query(
        KeyConditionExpression=(
            Key("PK").eq(f"CUSTOMER#{customer_id}")
            & Key("SK").begins_with("ADDRESS#")
        ),
        ConsistentRead=True,
    )
    return response.get("Items", [])


def list_customer_orders(customer_id: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    request: dict[str, Any] = {
        "KeyConditionExpression": (
            Key("PK").eq(f"CUSTOMER#{customer_id}")
            & Key("SK").begins_with("ORDER#")
        ),
        "ScanIndexForward": False,
    }
    while True:
        response = table.query(**request)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
        request["ExclusiveStartKey"] = last_key
    return items
```

A single `Query` response is limited (up to 1 MB of evaluated data before pagination, and possibly fewer items if a `Limit` is specified). Always follow `LastEvaluatedKey` when the application needs the full result set. Prefer page-by-page processing for large results rather than accumulating everything in memory.

### 8.3 Low-level client API

The resource API uses Python-native values. The low-level client API uses DynamoDB's typed AttributeValue representation. Do not mix the two forms.

```python
import boto3

client = boto3.client("dynamodb", region_name="us-east-1")

response = client.get_item(
    TableName="Commerce",
    Key={
        "PK": {"S": "CUSTOMER#c-17"},
        "SK": {"S": "PROFILE"},
    },
    ConsistentRead=True,
)
item = response.get("Item")  # AttributeValue map, e.g. {"name": {"S": "Asha"}}
```

### 8.4 GSI queries

```python
from boto3.dynamodb.conditions import Key

response = table.query(
    IndexName="GSI1",
    KeyConditionExpression=(
        Key("GSI1PK").eq("STATUS#OPEN")
        & Key("GSI1SK").between(
            "2026-10-01T00:00:00Z#", "2026-10-31T23:59:59Z#~"
        )
    ),
    ScanIndexForward=True,
)
```

Use only sort-key ranges that match the actual canonical key format. A string range is lexical, not a datetime-aware operation. For production, use a fixed-width UTC timestamp and a stable suffix. Since a GSI is eventually consistent, a work queue must tolerate a recently closed order still appearing briefly; re-check status with a conditional update before processing it.

## 9. Capacity modes, RCUs/WCUs, and cost

### 9.1 On-demand versus provisioned

- **On-demand (`PAY_PER_REQUEST`)**: AWS bills for requests. It is convenient for unpredictable or new workloads, avoids capacity planning at the outset, and still requires attention to traffic ramps, hot keys, item size, and service quotas.
- **Provisioned (`PROVISIONED`)**: configure read and write capacity, optionally with auto scaling. It can be cost-effective for steady predictable traffic, but under-provisioning causes throttling and over-provisioning wastes capacity.
- Capacity mode can be changed subject to service rules and quotas; check current AWS limits before planning frequent switches.

### 9.2 Approximate capacity rules

- One write capacity unit represents one write per second for an item up to 1 KB in provisioned mode. Larger writes consume capacity in 1 KB increments.
- One read capacity unit represents one strongly consistent read per second for an item up to 4 KB; eventually consistent reads use half the capacity for the same size. Transactional reads/writes have higher capacity cost than non-transactional operations.
- Batch operations do not make consumed capacity disappear. Capacity is based on item size and operation semantics; index writes also consume write capacity/storage on GSIs.
- Strongly consistent reads are not available on GSIs. Index projection choice affects index storage and read cost.

**Worked capacity estimate (illustrative arithmetic, not a benchmark):** Assume 100 strongly consistent `GetItem` reads per second, each returning an item no larger than 4 KB. The estimate is about 100 RCUs. If the same reads can be eventually consistent, the estimate is about 50 RCUs. Assume 100 non-transactional writes per second, each writing an item of 2.2 KB; round each write up to 3 × 1 KB units, giving about 300 WCUs before considering index writes. Transactional reads and writes consume more capacity (commonly twice the corresponding non-transactional units); calculate them separately. Real item sizes include attribute names and values, and GSIs add their own write/storage costs. On-demand mode bills request units rather than requiring a provisioned RCU/WCU target, but the rounded request-size arithmetic remains useful for workload planning.

These are planning rules, not a cost quote or measured result. Actual billing depends on Region, item sizes, indexes, storage, backups, streams, data transfer, request patterns, and pricing changes. Estimate using measured representative traffic and the AWS pricing calculator, then validate CloudWatch consumed/throttled metrics.

### 9.3 Practical cost model

Track at least:

- Read/write request volume and item-size distribution.
- Base-table and per-index storage, including projected attributes.
- GSI write amplification from index maintenance.
- Scan volume, exports, streams, Lambda, S3 requests/storage, and data transfer.
- Backup and point-in-time recovery retention.
- Retry amplification during throttling and downstream backpressure.

A table with few writes but several broad GSIs can cost more than the table name alone suggests. Do not create an index “just in case”; map each index to a real query and measure its usage.

## 10. Pagination, batch operations, and retry behavior

### 10.1 Pagination

`Query`, `Scan`, and some other APIs can return a continuation key. Use `LastEvaluatedKey` as `ExclusiveStartKey` until no key remains. Do not assume one response contains every match. Apply a page-size limit to keep latency and memory bounded, and stream results into downstream processing when possible.

### 10.2 Batch reads and writes

`BatchGetItem` and `BatchWriteItem` have request-size/operation-count limits and may return `UnprocessedKeys` or `UnprocessedItems`. A successful HTTP response does not mean every requested item was processed. Retry only the unprocessed subset with exponential backoff and jitter, and impose a retry/time budget.

```python
import random
import time
from typing import Any


def batch_write_with_retry(client, request_items: dict[str, list[dict[str, Any]]], max_attempts: int = 8):
    pending = request_items
    for attempt in range(max_attempts):
        if not pending:
            return
        response = client.batch_write_item(RequestItems=pending)
        pending = response.get("UnprocessedItems", {})
        if pending:
            delay = min(2.0, 0.05 * (2 ** attempt))
            time.sleep(random.uniform(0, delay))
    if pending:
        raise RuntimeError(f"Batch write incomplete; unprocessed requests remain: {pending.keys()}")
```

In production, avoid logging sensitive item contents. The example demonstrates the retry loop; add metrics, cancellation, and safe logging. `BatchWriteItem` does not support per-item condition expressions and is not atomic. Use individual conditional writes or `TransactWriteItems` when those guarantees are required.


For `BatchGetItem`, retry only `UnprocessedKeys` and accumulate items returned by every attempt. A successful HTTP response may be partial, and result order is not guaranteed:

```python
import random
import time
from typing import Any


def batch_get_with_retry(client, request_items: dict[str, dict[str, Any]], max_attempts: int = 8):
    pending = request_items
    collected: dict[str, list[dict[str, Any]]] = {}
    for attempt in range(max_attempts):
        if not pending:
            return collected
        response = client.batch_get_item(RequestItems=pending)
        for table_name, items in response.get("Responses", {}).items():
            collected.setdefault(table_name, []).extend(items)
        pending = response.get("UnprocessedKeys", {})
        if pending:
            time.sleep(random.uniform(0, min(2.0, 0.05 * (2 ** attempt))))
    if pending:
        raise RuntimeError(f"Batch get incomplete; unprocessed tables remain: {list(pending)}")
    return collected
```

`BatchGetItem` does not preserve request order; correlate returned items by primary key. The helper accumulates successful responses and retries only unprocessed keys.

### 10.3 Throttling and SDK retries

AWS SDKs retry many transient errors by default, with behavior determined by retry mode and configuration. Configure a bounded retry policy; do not add an unbounded application retry loop on top of SDK retries. Inspect throttling reason fields and CloudWatch metrics to distinguish table-level capacity, index capacity, hot-key pressure, quotas, and client-side bursts. Retries cannot fix a permanently skewed key design.

## 11. Conditional writes, optimistic locking, counters, and TTL

### 11.1 Create-only writes

```python
from botocore.exceptions import ClientError

try:
    table.put_item(
        Item={
            "PK": "CUSTOMER#c-17",
            "SK": "PROFILE",
            "entityType": "CUSTOMER",
            "name": "Asha Rao",
            "email": "asha@example.com",
            "version": 1,
        },
        ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
    )
except ClientError as exc:
    if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
        print("Profile already exists; do not overwrite it")
    else:
        raise
```

### 11.2 Optimistic locking with a version attribute

A client reads `version=7`, edits the object, then writes only if the stored version remains 7. If another client has updated it first, the condition fails rather than silently overwriting the newer value.

```python
from botocore.exceptions import ClientError


def rename_customer(customer_id: str, expected_version: int, new_name: str) -> int:
    response = table.update_item(
        Key={"PK": f"CUSTOMER#{customer_id}", "SK": "PROFILE"},
        UpdateExpression="SET #nm = :name, #ver = :next",
        ConditionExpression="#ver = :expected",
        ExpressionAttributeNames={"#nm": "name", "#ver": "version"},
        ExpressionAttributeValues={
            ":name": new_name,
            ":expected": expected_version,
            ":next": expected_version + 1,
        },
        ReturnValues="ALL_NEW",
    )
    return int(response["Attributes"]["version"])

try:
    rename_customer("c-17", expected_version=7, new_name="Asha R.")
except ClientError as exc:
    if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
        # Reload the item, compare changes, and retry only if business logic permits.
        print("Stale update rejected")
    else:
        raise
```

The `version` attribute must be initialised and incremented by every writer that participates in the concurrency protocol. A client that bypasses the condition defeats the guarantee. For an item that might not exist, use a condition that explicitly handles `attribute_not_exists(version)` or create it with a separate conditional operation.

### 11.3 Atomic counters

```python
table.update_item(
    Key={"PK": "CUSTOMER#c-17", "SK": "PROFILE"},
    UpdateExpression="ADD loginCount :one",
    ExpressionAttributeValues={":one": 1},
)
```

An atomic update avoids a read-modify-write race for the increment itself. It does not make the counter idempotent: if a client retries after an ambiguous timeout, the increment might be applied twice. For billing or event counts that must deduplicate requests, include an idempotency record/transaction or derive the count from a durable event log.

### 11.4 TTL

TTL is an asynchronous cleanup mechanism, not an exact-time scheduler. Configure a numeric Unix epoch-seconds attribute (for example `expiresAt`) in the table's TTL setting. Expired items can remain visible for a while before background deletion; do not rely on TTL to enforce authorization or exact retention cutoffs. A read path should check expiry when correctness requires it. TTL deletions can also appear in Streams, depending on the stream configuration and service behavior.

Example: store `expiresAt=1792368000` as a DynamoDB Number (an illustrative Unix epoch timestamp), then enable TTL for the table:

```bash
aws dynamodb update-time-to-live \
  --table-name Commerce \
  --time-to-live-specification 'Enabled=true,AttributeName=expiresAt'
```

Check the table's TTL status before relying on expiry cleanup; enabling TTL is asynchronous and existing items are not deleted immediately.

### 11.5 Lightweight atomicity versus transactions

Use a conditional write for a single-item invariant. Use `TransactWriteItems` when a small set of writes/checks must succeed or fail together, for example creating a uniqueness claim and customer profile in one logical operation. Transactions have operation-count, item-size, and aggregate request-size limits and cost more than ordinary writes. The commonly documented `TransactWriteItems` limit is 100 actions and 4 MB of aggregate item data per transaction, and each item is still subject to the 400 KB item limit; verify current service limits and exceptions in AWS documentation before implementation. A transaction cannot contain multiple actions targeting the same item. Transactions do not turn DynamoDB into a general relational transaction engine.

## 12. Transactions

```python
client = boto3.client("dynamodb", region_name="us-east-1")

client.transact_write_items(
    TransactItems=[
        {
            "Put": {
                "TableName": "Commerce",
                "Item": {
                    "PK": {"S": "EMAIL#asha@example.com"},
                    "SK": {"S": "CLAIM"},
                    "customerId": {"S": "c-17"},
                },
                "ConditionExpression": "attribute_not_exists(PK)",
            }
        },
        {
            "Put": {
                "TableName": "Commerce",
                "Item": {
                    "PK": {"S": "CUSTOMER#c-17"},
                    "SK": {"S": "PROFILE"},
                    "entityType": {"S": "CUSTOMER"},
                    "email": {"S": "asha@example.com"},
                    "version": {"N": "1"},
                },
                "ConditionExpression": "attribute_not_exists(PK) AND attribute_not_exists(SK)",
            }
        },
    ],
    ClientRequestToken="create-customer-c17-v1",
)
```

The example uses a separate uniqueness-claim item. It illustrates the low-level client's typed values and transactional conditions; production code must choose a request token that is stable for retries of the same logical transaction and unique for different transaction intents. Transaction idempotency tokens have a bounded validity period; do not reuse them indefinitely. Avoid trying to perform two transaction actions on the same item in one transaction. Review the current AWS API constraints and transaction conflict metrics before adopting this pattern.

## 13. Local development with DynamoDB Local

DynamoDB Local is useful for fast schema, key, and application tests. It does **not** reproduce every managed-service behavior, capacity throttle, global-table replication, production IAM, or all stream/integration behavior. Use a real AWS test account for managed-service semantics and cost/throughput tests, with strict budgets and cleanup.

### 13.1 Docker setup

Create `experiments/05_dynamodb/docker-compose.yml`:

```yaml
services:
  dynamodb-local:
    image: amazon/dynamodb-local:latest
    command: "-jar DynamoDBLocal.jar -sharedDb -dbPath ./data"
    working_dir: /home/dynamodblocal
    ports:
      - "8000:8000"
    volumes:
      - ./data:/home/dynamodblocal/data
```

For reproducible team use, pin a tested image tag/digest rather than relying on `latest`. Run:

```bash
cd experiments/05_dynamodb
docker compose up -d
uv init --python 3.12
uv add boto3 pyarrow pytest
```

Create a local resource client:

```python
import boto3

local = boto3.resource(
    "dynamodb",
    region_name="us-east-1",
    endpoint_url="http://localhost:8000",
    aws_access_key_id="local",
    aws_secret_access_key="local",
)
```

The dummy credentials are for local use only. Do not place them in deployed environments. Create the table with the same key/index design as the CLI example, using `endpoint_url` and local credentials, or run the AWS CLI with `--endpoint-url http://localhost:8000`.

## 14. Hot partitions, adaptive capacity, and write sharding

### 14.1 Why hot keys happen

DynamoDB distributes data by partition-key hash, but an extremely popular partition-key value can concentrate requests. A common example is every event written to `PK=STATUS#OPEN`, or every sensor update written to one constant tenant key. Adaptive capacity can help accommodate uneven workloads, but it cannot make a single key infinitely scalable or compensate for a poor distribution strategy.

### 14.2 Write-sharded key design

Instead of a single key `PK=DEVICE#sensor-1`, distribute writes across a deterministic number of buckets:

```text
PK=DEVICE#sensor-1#SHARD#00
PK=DEVICE#sensor-1#SHARD#01
...
PK=DEVICE#sensor-1#SHARD#0F
```

Choose the shard with a stable hash of an event ID or use a documented round-robin strategy if events are uniquely assigned. Readers must query all shard keys and merge results. If ordering is required across shards, each shard can be ordered locally by timestamp, but a globally ordered result requires a merge step. Choose shard count from measured write rate and item sizes, not guesswork; excessive sharding increases read fan-out and operational complexity.

For the open-orders GSI, a sharded sparse index can use `GSI1PK=STATUS#OPEN#<shard>`. A consumer must query each shard and merge/paginate the results. Do not assume a GSI's single partition can sustain arbitrary throughput because it is “only an index.”

## 15. DynamoDB Streams and Kinesis Data Streams for DynamoDB

These are related but distinct products.

| Capability | DynamoDB Streams | Kinesis Data Streams for DynamoDB |
|---|---|---|
| Purpose | Change-data capture feed for item modifications | Publish table changes into a Kinesis data stream for broader streaming integrations |
| Retention | 24 hours | Configurable Kinesis retention, subject to current service limits/configuration; not the same as DynamoDB Streams' fixed 24-hour window |
| Record shape | DynamoDB stream record with keys, event name, sequence metadata, and configured old/new images | Kinesis records containing DynamoDB change data in the Kinesis stream's event envelope; consumers use Kinesis APIs/KCL or supported integrations |
| Consumers | Commonly Lambda event source mapping; also Streams APIs | Kinesis consumers, KCL, Lambda event source mapping, analytics systems, and other Kinesis integrations |
| Ordering | Changes to an item are ordered in the stream shard; do not infer global table-wide order | Ordering is per Kinesis shard/partition key; no global order across shards |
| Replay | Limited by 24-hour retention; consumers must keep up or recover from another source | Replay within configured retention; capacity/consumer model differs |
| Configuration/cost | Enable stream view type on table; stream read requests and consumer architecture matter | Additional Kinesis stream configuration and billing; separate retention/throughput/consumer design |

Verify the exact stream view types and current service integration behavior in the AWS documentation for the target account/Region. Do not assume enabling DynamoDB Streams also creates or configures Kinesis Data Streams.

### 15.1 Stream view types

DynamoDB Streams can be configured to capture:

- `KEYS_ONLY`: key attributes only.
- `NEW_IMAGE`: item after the change.
- `OLD_IMAGE`: item before the change.
- `NEW_AND_OLD_IMAGES`: both images.

Choose the smallest view that supports the consumer. Full images increase record size and may expose sensitive fields to downstream systems. The stream configuration is part of the data contract; consumers must handle absent old/new images according to the chosen view and event type.

### 15.2 Event structure and semantics

A stream record commonly includes fields such as `eventName` (`INSERT`, `MODIFY`, or `REMOVE`), `eventID`, `eventVersion`, `eventSource`, `awsRegion`, `dynamodb.Keys`, optional `NewImage`/`OldImage`, sequence metadata, and approximate creation time. Exact payload fields vary with view type and consumer envelope. For Lambda event source mappings, the handler receives an outer event with a `Records` list and DynamoDB stream record details under each record.

A consumer should assume retries and duplicate processing are possible. Lambda stream processing is at-least-once in common configurations; a record may be retried after partial batch failure or timeout. Per-item/per-shard order is not equivalent to global order. Configure batch size, batching window, retry policy, bisect-on-error, partial batch response, and failure destinations according to the workload and current Lambda integration capabilities. Monitor iterator age, errors, throttles, and failed records.

### 15.3 Idempotent consumer design

A robust consumer should:

1. Identify each source change with a stable event identity (for example stream ARN/shard/sequence number or `eventID` where appropriate).
2. Write the raw change or a deduplication marker durably before declaring success, or use a deterministic output key that makes replay safe.
3. Make transformations deterministic and define how `REMOVE` events are represented downstream.
4. Handle partial batches without silently dropping failed records.
5. Commit/checkpoint only after the downstream side effect is durable.
6. Track lag and recover before the 24-hour DynamoDB Streams retention window is exceeded.

Writing one Parquet file per record is usually inefficient. Buffer records into bounded batches by time/size, write Parquet to S3 using a stable object-key strategy, and keep a manifest/checkpoint or transactional metadata scheme so retries do not create uncontrolled duplicates. Parquet files in S3 are not an atomic append log; downstream readers should consume committed manifests/partitions or use a table format/catalog strategy that handles file commits.

## 16. Example stream consumer to Parquet in S3

This teaching example shows the transformation path, not a complete production deployment. It uses Lambda's DynamoDB Streams event envelope, `boto3`, and `pyarrow`. In a production Lambda layer/container, package compatible versions of `pyarrow` and dependencies. The example writes a deterministic object key per Lambda batch only if the caller supplies a stable batch identifier; in a real implementation derive it from a stable record range and implement a durable idempotency ledger. For simplicity, this example's key is deterministic for the event IDs in the batch, so identical batches target the same S3 object key. Use conditional writes or a manifest/commit protocol if concurrent retries can race.

```python
from __future__ import annotations

import base64
import hashlib
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import boto3
import pyarrow as pa
import pyarrow.parquet as pq

s3 = boto3.client("s3")
BUCKET = os.environ["LAKE_BUCKET"]
PREFIX = os.environ.get("LAKE_PREFIX", "dynamodb/commerce_changes")


def av_to_python(value: dict[str, Any]) -> Any:
    """Convert a DynamoDB AttributeValue to a JSON/Arrow-friendly value."""
    if "S" in value:
        return value["S"]
    if "N" in value:
        number = Decimal(value["N"])
        return int(number) if number == number.to_integral_value() else number
    if "BOOL" in value:
        return value["BOOL"]
    if "NULL" in value:
        return None
    if "M" in value:
        return {k: av_to_python(v) for k, v in value["M"].items()}
    if "L" in value:
        return [av_to_python(v) for v in value["L"]]
    if "SS" in value:
        return sorted(value["SS"])
    if "NS" in value:
        return sorted(Decimal(x) for x in value["NS"])
    if "BS" in value:
        # DynamoDB Streams JSON encodes binary values as Base64 strings.
        return sorted(base64.b64decode(x) for x in value["BS"])
    if "B" in value:
        # Decode the stream's Base64 representation; the JSON serializer below
        # re-encodes bytes as Base64 so the landing format remains portable.
        return base64.b64decode(value["B"])
    raise ValueError(f"Unsupported AttributeValue shape: {list(value)}")


def json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        # Preserve exact decimal value in this JSON landing representation.
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(bytes(value)).decode("ascii")
    raise TypeError(f"Not JSON serializable: {type(value).__name__}")


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    records = event.get("Records", [])
    if not records:
        return {"batchItemFailures": []}

    rows = []
    ids = []
    for record in records:
        ddb = record.get("dynamodb", {})
        keys = {k: av_to_python(v) for k, v in ddb.get("Keys", {}).items()}
        new_image = {k: av_to_python(v) for k, v in ddb.get("NewImage", {}).items()}
        old_image = {k: av_to_python(v) for k, v in ddb.get("OldImage", {}).items()}
        event_id = record.get("eventID") or (
            f"{record.get('eventSourceARN','')}:{ddb.get('SequenceNumber','')}"
        )
        ids.append(event_id)
        rows.append({
            "event_id": event_id,
            "event_name": record.get("eventName"),
            "event_source_arn": record.get("eventSourceARN"),
            "aws_region": record.get("awsRegion"),
            "sequence_number": ddb.get("SequenceNumber"),
            "approx_creation_time": ddb.get("ApproximateCreationDateTime"),
            "keys_json": json.dumps(keys, default=json_default, sort_keys=True),
            "new_image_json": json.dumps(new_image, default=json_default, sort_keys=True),
            "old_image_json": json.dumps(old_image, default=json_default, sort_keys=True),
        })

    # Stable key for the exact set/order of event IDs in this batch.
    digest = hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()
    # Partition by the first source record time, not wall-clock processing time,
    # so a retry that crosses midnight still targets the same date prefix.
    first_epoch = records[0].get("dynamodb", {}).get("ApproximateCreationDateTime")
    source_time = (datetime.fromtimestamp(float(first_epoch), timezone.utc)
                   if first_epoch is not None else datetime.fromtimestamp(0, timezone.utc))
    table = pa.Table.from_pylist(rows)
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink, compression="snappy")
    key = f"{PREFIX}/dt={source_time:%Y-%m-%d}/batch={digest}.parquet"

    # Same batch writes to the same key on retry. Production systems must still
    # handle concurrent duplicate invocations and verify object/manifest commits.
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=sink.getvalue().to_pybytes(),
        ContentType="application/vnd.apache.parquet",
        Metadata={"batch-sha256": digest},
    )
    return {"batchItemFailures": []}
```

**Production hardening required:** The example returns an empty failure list only after the S3 write succeeds; if the write raises, the invocation fails and can be retried. For Lambda partial batch response, return failed sequence numbers using the documented event-source mapping contract, and ensure the mapping is configured to enable it. Add an idempotency ledger or manifest protocol to prevent concurrent retries from overwriting or double-registering output. The converter preserves non-integral numbers as decimal strings in the JSON payload (rather than lossy binary floats) and re-encodes binary values as Base64 strings. JSON serialization above is a simple raw landing representation, not a fully typed warehouse schema; document that representation in the downstream schema contract. Restrict the Lambda role to required stream read and S3 prefix access, encrypt outputs, and avoid copying secrets/PII without policy review.

## 17. DynamoDB Streams versus S3 export and incremental export

Streams are for near-real-time change processing within their retention window. Exports to S3 are for analytical extraction and recovery workflows that should not consume the live request path.

- **Full point-in-time export to S3:** creates an export from a selected point in time without consuming read capacity on the table in the same way as a client-side scan. Output format and downstream conversion options depend on the export configuration and current service support.
- **Incremental export:** requires PITR and exports changes over a selected period of **15 minutes to 24 hours**. It is useful for batch incremental ingestion, but is not the same delivery contract as a live stream. The export output compacts changes to final item state within the selected period, and exports are not transactionally consistent across all items in a multi-item transaction. Check current format, pricing, and table prerequisites before scheduling. See [Requesting a table export](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/S3DataExport_Requesting.html).
- **Zero-ETL integrations:** AWS provides managed integration options for selected sources and destinations. Availability and behavior vary by service/Region and evolve; evaluate supported target, freshness, schema handling, cost, and operational ownership rather than assuming every DynamoDB table has a universal zero-ETL path.
- **Spark connector:** for large-scale processing, use an appropriate connector or controlled export pipeline. Plan throughput, parallelism, retries, consistency expectations, and checkpointing; do not issue an uncontrolled full scan against a latency-sensitive production table.

For downstream lakehouse ingestion, retain a raw immutable change log where appropriate, define delete semantics, deduplicate replays, track watermarks/checkpoints, and make upserts idempotent. This connects directly to Topic 09.

## 18. Global tables, backup, and recovery

### 18.1 Global tables

Global tables replicate DynamoDB data across Regions for multi-Region applications. They improve regional availability and locality but add cost and consistency considerations. Replication is not a distributed SQL transaction across Regions. Define write ownership, conflict behavior, failure recovery, and how applications react to temporarily divergent replicas. Strong consistency options and their limitations have changed over time; check current documentation for the exact global-table mode and supported Region combinations before making correctness claims.

### 18.2 Backup and point-in-time recovery

- Enable point-in-time recovery (PITR) for tables whose recovery objectives justify it.
- Use on-demand backups for milestones, migrations, or additional retention requirements.
- Define retention and restore testing, not just backup enablement.
- A restore creates a new table; plan how applications, IAM, indexes, streams, and integrations will be switched and validated.
- Backups and exports can incur storage/export costs. Confirm that recovered data meets RPO/RTO requirements and test the procedure periodically.

Example CLI commands (check the current CLI/API version and table status):

```bash
aws dynamodb update-continuous-backups \
  --table-name Commerce \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

aws dynamodb describe-continuous-backups --table-name Commerce
aws dynamodb create-backup --table-name Commerce --backup-name Commerce-pre-migration
```

Do not treat a successful API response as proof of a tested recovery plan. Run a restore drill in a non-production account and verify item counts, keys, indexes, permissions, and downstream consumers.

## 19. Hands-on lab — `experiments/05_dynamodb/`

### 19.1 Suggested project layout

```text
experiments/05_dynamodb/
├── docker-compose.yml
├── README.md
├── pyproject.toml
├── src/
│   ├── create_table.py
│   ├── seed_data.py
│   ├── access_patterns.py
│   ├── optimistic_locking.py
│   ├── stream_consumer.py
│   └── hot_key_experiment.py
├── tests/
│   ├── test_access_patterns.py
│   └── test_version_conflict.py
├── data/
│   └── sample_commerce.jsonl
└── outputs/                 # local test outputs only; do not commit credentials/data with PII
```

### 19.2 Setup assumptions

- Python 3.12+, `uv`, Docker Compose, AWS CLI v2, and `boto3`.
- DynamoDB Local for key/query/conditional-write tests.
- For stream-to-S3 and real throttling behavior, use a disposable AWS account with a budget alert, least-privilege IAM, and cleanup commands. DynamoDB Local does not emulate all managed stream, IAM, capacity, global-table, or throttling behavior.
- Use synthetic customers/orders/items/addresses only. Do not load production PII into the lab.

### Exercise 1 — List eight access patterns

Write the eight patterns from Section 6.2 in `README.md`. For each, record caller, frequency, key values known, response size, sort order, consistency, and whether the result must be complete or paginated.

**Evaluation:** every pattern is concrete and testable; none depends on an unbounded table scan or post-read filtering to find its target items.

### Exercise 2 — Design one table and two GSIs on paper

Draw the `Commerce` base table and item collections, plus GSI1 and GSI2. Include item examples for profile, address, customer order summary, order details, and order item. Mark which records populate each GSI and which omit index keys.

**Evaluation:** key conditions support all eight patterns; the open-orders GSI is sparse; email uniqueness is not incorrectly assumed from a GSI; duplicated order summaries have a consistency strategy.

### Exercise 3 — Implement in DynamoDB Local and seed sample data

1. Start DynamoDB Local using the Compose file.
2. Create `Commerce` with composite `PK`/`SK` and both GSIs.
3. Seed synthetic customers, multiple addresses per customer, orders, and line items. Add GSI keys only to applicable records.
4. Make the seed script repeatable: use deterministic IDs and conditional writes or a clean local database reset.

**Expected observation:** items with the same partition key can be retrieved as an item collection; GSI membership depends on the presence of GSI key attributes. No performance claims are expected.

### Exercise 4 — Run all eight patterns using only Query/GetItem

Implement one function per pattern. Add tests that fail if an access pattern calls `scan()`. Use `GetItem` for patterns 1 and 4; use `Query` for the other six, with `IndexName` for patterns 6 and 7. Test pagination for customer orders and order items. Verify returned item types and sort ordering.

**Expected outcome:** all eight tests pass for the seeded fixture. This is a functional acceptance criterion, not a performance benchmark.

### Exercise 5 — Add sparse GSI for open orders

Add `GSI1PK=STATUS#OPEN` and `GSI1SK=<createdAt>#<orderId>` only when an order is open. Update the status transition code so closing/cancelling an order removes both GSI attributes. Query GSI1 for open orders and confirm closed orders are absent after index propagation settles.

**Verification:** test open → closed and open → cancelled transitions; demonstrate that a GSI is eventually consistent and that the worker rechecks status before acting. If the index is already defined as in Section 8, this exercise is about implementing and testing its sparse membership.

### Exercise 6 — Optimistic locking and stale update rejection

1. Create a customer with `version=1`.
2. Simulate two clients reading version 1.
3. Client A updates with `ConditionExpression version = 1` and writes version 2.
4. Client B attempts an update still conditioned on version 1.
5. Verify that B receives `ConditionalCheckFailedException`, reloads the item, and handles the conflict deliberately.

**Expected outcome:** the stale write is rejected; no claim is made about benchmark performance.

### Exercise 7 — Enable a stream and write change records to Parquet in S3

1. In a disposable AWS account, enable DynamoDB Streams on `Commerce` with `NEW_AND_OLD_IMAGES` (or the minimal view that meets your requirements).
2. Configure a Lambda event-source mapping with a least-privilege execution role and S3 write access to a dedicated prefix.
3. Package a compatible `pyarrow` dependency or container image.
4. Use the consumer in Section 16 as a starting point; add durable idempotency/manifest handling, partial batch failure behavior, structured logs, and metrics before calling it production-ready.
5. Insert, modify, and delete synthetic items. Inspect event names, keys, images, and Parquet output. Test a controlled retry and verify downstream deduplication.
6. Monitor iterator age and ensure the consumer catches up before the 24-hour retention limit.

**Expected observations:** the record contains keys and fields according to the configured view type; a delete is represented as a `REMOVE` change; retry behavior can repeat work. Do not invent throughput or latency results. Document actual observations from your account, including any failed tests.

### Exercise 8 — Create a hot key and redesign with write sharding

On a test table, generate a controlled burst of writes to a single partition-key value. Use CloudWatch metrics and request errors to determine whether throttling occurs; whether it occurs depends on account, capacity mode, traffic, item size, and service behavior, so do not assume a specific threshold or outcome. Compare with a deterministic sharded-key design and document the read fan-out needed to retrieve the same logical dataset.

**Expected analysis:** explain why adaptive capacity may help but is not a substitute for distribution, how shard count affects write distribution and query fan-out, and what metrics would support the redesign. Do not run an uncontrolled load test against a production table.

### 19.3 Optional managed-service cleanup

```bash
aws dynamodb list-tables
aws dynamodb delete-table --table-name Commerce
```

Only run the delete command for the disposable lab table after preserving any outputs you need. Confirm account and Region before every destructive AWS command.

## 20. Common mistakes and their remedies

| Mistake | Why it fails | Better practice |
|---|---|---|
| Designing tables from entities alone | Required queries need scans or extra round trips | Enumerate and rank access patterns first. |
| Treating `FilterExpression` as an index | Filtered items still consume read capacity when evaluated | Put selective predicates into key/index design when they are core queries. |
| Assuming GSI is strongly consistent | GSI reads are eventually consistent | Re-check critical state on the base item and use conditional writes. |
| Assuming one table is always best | Coupled lifecycle, security, throughput, and complex key conventions can outweigh benefits | Use one table only when access patterns benefit from shared item collections. |
| Creating a GSI without a query contract | Index adds write/storage cost and operational burden | Map every index to a measured access pattern. |
| Using a constant hot partition key | Writes or reads concentrate on one key | Distribute keys; use sharding when justified and accept fan-out costs. |
| Assuming adaptive capacity removes all hot-key limits | Capacity is still bounded by partition and service limits | Measure distribution and redesign skew. |
| Ignoring `LastEvaluatedKey` | Results silently omit later pages | Implement pagination and test multi-page fixtures. |
| Assuming batch operations are atomic | Unprocessed items and partial completion are possible | Retry unprocessed items with bounded backoff; use transactions where needed. |
| Retrying every error forever | Increases load and hides permanent failures | Classify errors, use bounded retries with jitter, and alert on exhausted retries. |
| Treating TTL as immediate deletion | Expired items can remain visible | Enforce logical expiry in reads when required. |
| Using counters for exactly-once accounting | Retry after ambiguous timeout may double-increment | Add idempotency or derive aggregates from durable events. |
| Assuming Streams is an exactly-once queue | Consumers can retry and duplicate effects | Idempotent writes, dedupe, checkpoints, and failure handling. |
| Confusing DynamoDB Streams with Kinesis | Retention, configuration, and consumer model differ | Select product based on replay window and consumer requirements. |
| Writing one Parquet file per change | Creates tiny files and costly metadata overhead | Buffer records and commit batches safely. |
| Treating a local test as proof of AWS behavior | Local does not emulate every managed feature | Validate stream, throttling, IAM, global table, and cost behavior in a controlled AWS environment. |
| Assuming GSI enforces email uniqueness | Indexes do not provide a unique constraint | Use a conditional uniqueness-claim item or another suitable design. |

## 21. Practice questions

1. Why does DynamoDB require the partition key in a `Query` key condition?
2. What is the difference between a simple primary key and a composite primary key?
3. Why is a scan with a filter often more expensive than a query with a key condition?
4. Describe all eight access patterns and identify the exact operation and key condition for each.
5. Why can a sparse GSI reduce index storage, and what happens when an order changes from open to closed?
6. What are the trade-offs between `KEYS_ONLY`, `INCLUDE`, and `ALL` index projections?
7. When is single-table design beneficial, and when are separate tables more appropriate?
8. Explain eventual consistency for GSIs and how an order-processing worker should handle stale index entries.
9. How does optimistic locking prevent a stale update? What happens if one writer ignores the version condition?
10. Why are atomic counters not automatically idempotent?
11. How do on-demand and provisioned capacity differ operationally and economically?
12. What does a batch write response's `UnprocessedItems` mean?
13. How can a hot partition arise even when the table has a large total capacity?
14. What are the read fan-out costs of write sharding?
15. When should `TransactWriteItems` be used instead of individual conditional writes?
16. What is the difference between DynamoDB Streams and Kinesis Data Streams for DynamoDB?
17. Why must a stream consumer be idempotent even if the source records have sequence metadata?
18. What happens if a DynamoDB Streams consumer remains behind longer than the retention window?
19. When is an S3 point-in-time export a better extraction method than a stream consumer or table scan?
20. What does a restore drill verify beyond the existence of a backup?

## 22. Checkpoints

- [ ] I can explain items, attributes, partition keys, sort keys, and DynamoDB data types.
- [ ] I can explain `GetItem`, `Query`, `Scan`, and why filters do not replace indexes.
- [ ] I can map eight explicit customer/order/item/address access patterns to operations and key conditions.
- [ ] I can draw the base table plus GSI1 and GSI2 and explain sparse index membership.
- [ ] I can justify single-table versus separate-table design using access patterns and operational boundaries.
- [ ] I can estimate RCUs/WCUs from item size and consistency, then validate actual usage using metrics.
- [ ] I can implement `boto3` resource/client calls, pagination, bounded retries, and batch unprocessed-item handling.
- [ ] I can implement conditional create, optimistic locking, atomic update, TTL, and a small transaction.
- [ ] I can explain hot keys, adaptive capacity, write sharding, and the read fan-out trade-off.
- [ ] I can explain Streams retention, event view types, per-key ordering, retry behavior, and idempotent consumers.
- [ ] I can distinguish Streams, Kinesis Data Streams for DynamoDB, S3 exports, incremental exports, and zero-ETL options.
- [ ] I can describe backup/PITR and demonstrate a recovery drill.

## 23. Self-assessment rubric

| Level | Evidence |
|---|---|
| Beginner | Correctly explains primary keys and CRUD/query operations; knows why scans are not the default request path. |
| Intermediate | Designs the eight access patterns, implements table/index keys, and passes tests with `Query`/`GetItem`; uses conditions and pagination correctly. |
| Advanced | Diagnoses hot-key distribution, chooses capacity and transaction patterns, handles stream replay safely, and documents cost/recovery assumptions with real measurements. |
| Production-ready for this topic | Provides tested code, least-privilege IAM, bounded retries, observable failure handling, idempotent downstream output, cost/retention controls, and a documented recovery plan. |

## 24. Final engineering checklist

Before approving a DynamoDB design, verify:

1. Every interactive query has a known key path and bounded result shape.
2. Partition-key distribution matches expected read/write traffic, not merely row counts.
3. All denormalized copies have a consistency and repair strategy.
4. Every GSI supports a named query and has a justified projection.
5. Conditional writes protect invariants that must not be violated.
6. Retries are bounded, jittered, observable, and idempotent where side effects are involved.
7. Stream retention and consumer recovery objectives are compatible.
8. Parquet output is committed and deduplicated safely before the source checkpoint advances.
9. Backups and point-in-time recovery are enabled where required and restore-tested.
10. Costs are estimated from measured workload shapes and validated with AWS metrics rather than guessed.

## 25. Official references and version-sensitive notes

Use the current AWS documentation for the target Region and service mode; quotas, integrations, SDK behavior, and pricing can change.

- [DynamoDB core components and data model](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html)
- [Secondary indexes: GSI and LSI](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/SecondaryIndexes.html)
- [Read/write capacity modes and unit calculations](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/read-write-operations.html)
- [Transactions](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html)
- [DynamoDB Streams](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html)
- [Change data capture: DynamoDB Streams vs Kinesis Data Streams for DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/streamsmain.html)
- [Using Lambda with DynamoDB Streams, including partial batch responses](https://docs.aws.amazon.com/lambda/latest/dg/with-ddb.html)
- [Exporting DynamoDB data to S3, including incremental export](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/S3DataExport_Requesting.html)
- [Point-in-time recovery](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/PointInTimeRecovery.html)

**Version-sensitive notes:** The lesson uses AWS CLI v2 and current `boto3`-style APIs. DynamoDB Local is a development substitute, not proof of managed-service behavior. Verify transaction quotas, global-table consistency mode, Kinesis retention, zero-ETL support, export windows, and Lambda event-source mapping settings at implementation time.

**Core principle:** DynamoDB performance and cost depend on the keys and access patterns you design, not on SQL-style query flexibility. Model the queries first, test the actual distribution, and treat streams as an at-least-once integration boundary that needs explicit idempotency and recovery.
