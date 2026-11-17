# MongoDB: Document Modelling and Aggregation

**Stage:** Stage 2C — Data Engineering_3  
**Module:** 01 — NoSQL and Distributed Databases  
**Topic:** 03 — MongoDB document modelling and aggregation  
**Exact filename:** `03-mongodb-document-modelling-and-aggregation.md`

------------------------------------------------------------------------

## 1. Learning objectives

By the end of this lesson, you should be able to:

1.  Explain MongoDB databases, collections, BSON documents, `_id`, BSON data types, and how document storage differs from relational rows.
2.  Perform CRUD operations using `mongosh` and PyMongo.
3.  Query nested fields and arrays with comparison, logical, array, and element operators.
4.  Choose embedding or referencing for one-to-few, one-to-many, and many-to-many relationships.
5.  Apply bucket, subset, computed, extended-reference, polymorphic, and schema-versioning patterns.
6.  Design single-field, compound, multikey, text, TTL, and partial indexes.
7.  Apply the ESR rule carefully and interpret `explain("executionStats")` without inventing performance results.
8.  Translate relational group-by, join, and top-N queries into aggregation pipelines.
9.  Build pipelines using `$match`, `$project`, `$group`, `$sort`, `$unwind`, `$lookup`, `$facet`, `$bucket`, `$merge`, and `$out`.
10. Validate documents with JSON Schema and access MongoDB safely using typed Python/PyMongo code.
11. Explain replica-set elections, read preference, read concern, write concern, transaction costs, and sharding trade-offs.
12. Design experiments that measure query performance, index effects, failover, and data quality rather than relying on assumptions.

## 2. Roadmap position and prerequisites

This is Topic 03 in the authoritative module sequence:

``` text
Stage 2C — Data Engineering_3/
└── 01-NoSQL-and-Distributed-Databases/
    ├── 01-nosql-families-and-when-to-use-them.md
    ├── 02-cap-theorem-and-consistency-models.md
    ├── 03-mongodb-document-modelling-and-aggregation.md  ← this lesson
    ├── 04-cassandra-wide-column-partitioning-and-tombstones.md
    ├── 05-dynamodb-single-table-design-and-streams.md
    ├── 06-redis-caching-and-data-structures.md
    ├── 07-elasticsearch-and-opensearch-for-search-and-logs.md
    ├── 08-graph-databases-neo4j-and-cypher.md
    └── 09-change-streams-and-nosql-to-lakehouse-ingestion.md
```

The module roadmap places MongoDB after NoSQL families and CAP/consistency because you should first understand access-pattern-first modelling and consistency guarantees. MongoDB then introduces nested documents and aggregation before Cassandra and DynamoDB demand more rigid query-first partition design. Topic 09 later uses MongoDB as a source for incremental lakehouse ingestion.

### Prerequisites

The module roadmap expects these earlier skills rather than reteaching them:

- Python, JSON, type hints, and packaging (Stage 1).
- OLTP versus OLAP, batch versus streaming, and nested/semi-structured data (Stage 2).
- SQL, transactions, isolation levels, normalization, and denormalization.
- CDC, watermarks, idempotent merge loads, and deduplication.
- Docker Compose and basic local database operation.
- Topics 01 and 02: NoSQL families, access patterns, replication, and consistency vocabulary.

### Version note

Examples use modern MongoDB shell (`mongosh`) syntax and PyMongo 4.x-style APIs. The roadmap names MongoDB 7/8. Check the exact server/driver version before relying on a feature, explain-plan field, Atlas capability, or deployment-specific behavior. Atlas Search and Vector Search are managed Atlas capabilities, not identical to ordinary self-managed MongoDB indexes.

## 3. The running e-commerce domain

Use one domain throughout: a store selling products, receiving orders, and producing daily revenue by product category.

Core entities:

- **Customer:** identity and contact details.
- **Product:** SKU, name, category, current price, and active status.
- **Order:** customer, order timestamp, status, line items, shipping snapshot, and totals.
- **Order line:** product ID, quantity, unit price at purchase, and product/category snapshots.
- **Session:** expiring state such as a checkout session.
- **Daily revenue:** derived aggregate for analytics.

An illustrative order document:

``` javascript
const sampleOrder = {
  _id: ObjectId("65a000000000000000000001"),
  orderNumber: "ORD-10001",
  customerId: ObjectId("65a000000000000000000101"),
  createdAt: ISODate("2026-10-01T10:15:00Z"),
  status: "paid",
  currency: "USD",
  items: [
    {
      productId: ObjectId("65a000000000000000000201"),
      sku: "MUG-BLUE",
      productName: "Blue Mug",
      category: "kitchen",
      quantity: 2,
      unitPrice: Decimal128("12.50")
    },
    {
      productId: ObjectId("65a000000000000000000202"),
      sku: "NOTE-A5",
      productName: "A5 Notebook",
      category: "stationery",
      quantity: 1,
      unitPrice: Decimal128("6.00")
    }
  ],
  shippingAddress: {
    recipient: "Taylor Reed",
    city: "Pune",
    postalCode: "411001",
    country: "IN"
  },
  totals: {
    subtotal: Decimal128("31.00"),
    shipping: Decimal128("3.00"),
    tax: Decimal128("2.00"),
    grandTotal: Decimal128("36.00")
  },
  schemaVersion: 1
};
```

This example is illustrative. In a lab, generate your own IDs and use synthetic data. Avoid storing real customer data in experiments.

## 4. MongoDB fundamentals

### 4.1 Database, collection, document, BSON

- **Database:** a logical namespace containing collections and other database objects.
- **Collection:** a group of documents, broadly analogous to a relational table but without requiring every document to have the same fields.
- **Document:** a nested field/value structure made of key-value pairs, arrays, and embedded documents.
- **BSON:** MongoDB’s binary serialization format. It supports types that JSON does not directly represent, such as `ObjectId`, `Date`, and `Decimal128`.
- **`_id`:** the required unique identifier for each document in a collection. MongoDB creates an `ObjectId` if `_id` is omitted on insertion. `_id` is uniquely indexed by default, and applications can use other supported unique values.
- **Field:** a named value within a document.

Documents can represent nested objects and arrays naturally. This makes related data convenient to retrieve together, but it also makes document growth, duplication, validation, and downstream flattening important design concerns.

### 4.2 BSON types to recognize

| Type            | Example                            | Practical use / caution                                     |
|-----------------|------------------------------------|-------------------------------------------------------------|
| String          | `"paid"`                           | Names, labels, IDs where string identity is intended        |
| ObjectId        | `ObjectId("...")`                  | Common generated identifier; not a security token           |
| Boolean         | `true`                             | Explicit flags                                              |
| Int32 / Int64   | `quantity: 2`                      | Counts; choose appropriate range                            |
| Double          | `score: 0.92`                      | Approximate floating-point values                           |
| Decimal128      | `Decimal128("12.50")`              | Monetary values where decimal arithmetic is required        |
| Date            | `ISODate("2026-10-01T10:15:00Z")`  | UTC timestamp; BSON Date stores milliseconds from the epoch |
| Array           | `items: [...]`                     | Ordered embedded values                                     |
| Object/document | `shippingAddress: {...}`           | Nested structured fields                                    |
| Null            | `cancelledAt: null`                | Explicit null; distinct from missing field                  |
| Binary          | binary payload                     | Raw binary content                                          |
| Timestamp       | internal/replication-oriented type | Do not confuse with application event time                  |

**Money:** use `Decimal128` or integer minor units (for example, cents) with an explicit currency. Do not use binary floating point for exact monetary calculations without understanding rounding.

### 4.3 Documents versus relational rows

| Relational model                                          | MongoDB document model                                                                          |
|-----------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| Rows in tables                                            | Documents in collections                                                                        |
| Columns normally follow table schema                      | Documents can have varying fields; validation is optional/configurable                          |
| Relationships often represented by foreign keys and joins | Relationships can be embedded or referenced                                                     |
| Normalization reduces duplication                         | Denormalization may optimize common reads                                                       |
| SQL joins are central                                     | `$lookup` exists, but the best model often serves common access patterns without frequent joins |
| Types are database column types                           | BSON types are stored per field/value                                                           |
| Constraints often defined centrally                       | JSON Schema validation and application validation can be combined                               |

MongoDB is not “schema-free.” A document has a shape; without validation, that shape is enforced by application code and operational discipline. A field stored sometimes as a string and sometimes as a number creates query and analytics problems.

### 4.4 Connect with `mongosh`

Example URI for a local replica set:

``` bash
mongosh "mongodb://localhost:27017/?replicaSet=rs0"
```

Select a database and inspect collections:

``` javascript
use ecommerce
show collections
db.orders.countDocuments({})
db.orders.getIndexes()
```

`use ecommerce` selects a database; the database/collection may be created lazily when data is written.

## 5. CRUD: create, read, update, delete

### 5.1 Insert one and many

``` javascript
db.products.insertOne({
  sku: "MUG-BLUE",
  name: "Blue Mug",
  category: "kitchen",
  price: Decimal128("12.50"),
  active: true,
  tags: ["ceramic", "drinkware"],
  createdAt: new Date()
})

db.products.insertMany([
  {
    sku: "NOTE-A5",
    name: "A5 Notebook",
    category: "stationery",
    price: Decimal128("6.00"),
    active: true,
    tags: ["paper", "office"],
    createdAt: new Date()
  },
  {
    sku: "LAMP-DESK",
    name: "Desk Lamp",
    category: "home",
    price: Decimal128("29.95"),
    active: true,
    tags: ["lighting", "office"],
    createdAt: new Date()
  }
])
```

- `insertOne()` inserts one document.
- `insertMany()` inserts multiple documents; the default ordered behavior stops at the first error, while unordered mode may continue processing other documents. Duplicate `_id` or unique-index values can cause errors.
- Do not assume that an application-level `sku` is unique unless a unique index enforces it.

Create a unique SKU index:

``` javascript
db.products.createIndex({ sku: 1 }, { unique: true })
```

If duplicates already exist, index creation will fail until the data is repaired.

### 5.2 Find, projection, sort, limit, skip

``` javascript
// All active kitchen products priced below 20.
db.products.find(
  { category: "kitchen", active: true, price: { $lt: Decimal128("20.00") } },
  { sku: 1, name: 1, price: 1, _id: 0 }
).sort({ price: 1, sku: 1 }).limit(20)
```

- First argument: filter.
- Second argument: projection. Inclusion and exclusion cannot normally be mixed in the same projection except for `_id`.
- `.sort()` orders results; include a tie-breaker for deterministic pagination.
- `.limit(20)` caps returned documents.
- `.skip(100)` skips the first 100 matching results. Large skip offsets can be expensive because the server must traverse the skipped results. For deep pagination, prefer a range/keyset filter using the last seen sort key.

Pagination example:

``` javascript
const pageSize = 20;
const lastSku = "MUG-BLUE";

db.products.find({ sku: { $gt: lastSku } })
  .sort({ sku: 1 })
  .limit(pageSize)
```

This assumes `sku` is a stable, unique sort key and that the corresponding index exists. For compound sort keys, build the continuation predicate carefully.

### 5.3 Comparison operators

| Operator      | Meaning                 | Example                                                   |
|---------------|-------------------------|-----------------------------------------------------------|
| `$eq`         | Equal                   | `{ status: { $eq: "paid" } }`                             |
| `$ne`         | Not equal               | `{ status: { $ne: "cancelled" } }`                        |
| `$gt`, `$gte` | Greater than / at least | `{ total: { $gte: 100 } }`                                |
| `$lt`, `$lte` | Less than / at most     | `{ createdAt: { $lt: ISODate("2026-10-02T00:00:00Z") } }` |
| `$in`         | Any value in list       | `{ status: { $in: ["paid", "shipped"] } }`                |
| `$nin`        | Not in list             | `{ category: { $nin: ["archived"] } }`                    |

`$ne` and `$nin` can match documents where a field is missing, depending on the expression. Use `$exists` when field presence matters.

### 5.4 Logical operators

``` javascript
db.products.find({
  $and: [
    { active: true },
    {
      $or: [
        { category: "kitchen" },
        { tags: "office" }
      ]
    }
  ]
})
```

- `$and`: all clauses must match.
- `$or`: at least one clause must match.
- `$nor`: none of the clauses may match.
- `$not`: negates a field operator expression; be precise with arrays and missing fields.

MongoDB implicitly ANDs ordinary sibling predicates, so this is equivalent for simple cases:

``` javascript
db.products.find({
  active: true,
  price: { $gte: Decimal128("5.00"), $lt: Decimal128("50.00") }
})
```

### 5.5 Array operators

Given a product:

``` javascript
const sampleProduct = {
  sku: "MUG-BLUE",
  tags: ["ceramic", "drinkware"],
  reviews: [
    { customerId: "c1", rating: 5 },
    { customerId: "c2", rating: 2 }
  ]
};
```

Examples:

``` javascript
// Array contains an exact value.
db.products.find({ tags: "ceramic" })

// Array contains any requested value.
db.products.find({ tags: { $in: ["ceramic", "glass"] } })

// Array has at least one element matching all predicates in $elemMatch.
db.products.find({
  reviews: { $elemMatch: { rating: { $gte: 4 }, customerId: "c1" } }
})

// Array size exactly 2 (not a range query).
db.products.find({ tags: { $size: 2 } })
```

For arrays of embedded documents, separate dotted predicates can match different array elements. Use `$elemMatch` when the conditions must be true of the **same** element.

### 5.6 Element operators

``` javascript
// Field exists, even if its value is null.
db.products.find({ discontinuedAt: { $exists: true } })

// Field's BSON type is a date.
db.products.find({ createdAt: { $type: "date" } })
```

`$exists: false` matches missing fields, not fields explicitly set to `null`. `$type` can be useful when investigating schema drift, but should not replace a stable schema contract.

### 5.7 Update one/many: `$set`, `$inc`, `$push`

``` javascript
// Set a field and create it if it does not exist.
db.products.updateOne(
  { sku: "MUG-BLUE" },
  { $set: { active: false, updatedAt: new Date() } }
)

// Increment inventory atomically within the matched document.
db.products.updateOne(
  { sku: "MUG-BLUE" },
  { $inc: { stock: -1 } }
)

// Add one review to an array.
db.products.updateOne(
  { sku: "MUG-BLUE" },
  { $push: { reviews: { customerId: "c3", rating: 5 } } }
)

// Update every matching document.
db.products.updateMany(
  { category: "stationery" },
  { $set: { promotionEligible: true } }
)
```

- `updateOne()` modifies at most one matching document. If the filter is not unique, which matching document is updated may not be what the application intended; use a unique key.
- `updateMany()` applies an update to all matching documents. It is not one atomic transaction across all matched documents.
- `$set` replaces the value at a path; it does not replace the entire document.
- `$inc` is atomic for the field within a single document. It is often safer than read-modify-write for a counter.
- `$push` appends to an array. Unbounded arrays can grow documents toward the 16 MB document limit and increase update costs. `$addToSet` avoids adding an equal value twice, but equality semantics for embedded documents require care.

Avoid overwriting an entire order just to change its status. Use a targeted update and, where concurrency matters, a version or expected-state condition.

### 5.8 Delete one/many

``` javascript
db.products.deleteOne({ sku: "OLD-SKU" })

db.orders.deleteMany({
  status: "test",
  createdAt: { $lt: ISODate("2026-01-01T00:00:00Z") }
})
```

Deletion is permanent unless backups, point-in-time recovery, or an application-level retention strategy provide recovery. Always run the filter as a `find()` first and verify the count before a bulk deletion.

``` javascript
const filter = { status: "test" };
db.orders.countDocuments(filter);
db.orders.find(filter).limit(5);
// Only after verifying:
db.orders.deleteMany(filter);
```

## 6. Data modelling: let access patterns drive the shape

MongoDB modelling starts by listing the queries and updates the application performs. A normalized relational schema is not automatically the best document schema, and neither is embedding everything.

### 6.1 Embed versus reference

**Embedding** stores related data inside the parent document. It can provide a single-document read and atomic single-document updates, but duplicates data and grows the document.

**Referencing** stores IDs that point to documents in another collection. It reduces duplication and supports independently managed entities, but can require extra round trips or `$lookup`, and does not automatically provide a foreign-key constraint.

| Relationship | Usually consider embedding when…                                             | Usually consider referencing when…                                                                           |
|--------------|------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| One-to-few   | Child data is small, bounded, read with parent, and usually updated together | Child has independent lifecycle or is reused by many parents                                                 |
| One-to-many  | “Many” is bounded and children are normally read with parent                 | Children can grow without bound, need independent pagination, or are queried independently                   |
| Many-to-many | Relationship set is small and bounded, and duplication is acceptable         | Either side has many relationships, relationship data changes independently, or bidirectional queries matter |

Embedding can make a single-document update atomic. A write that updates several separate documents is not automatically atomic across those documents; use a transaction when the invariant requires it and the deployment supports it.

### 6.2 The 16 MB limit and unbounded arrays

MongoDB’s BSON document size limit is 16 MiB. An order with a handful of line items is a good embedding candidate; a user’s lifetime clickstream or millions of comments are not.

Unbounded arrays cause:

- document growth and eventual size-limit failures;
- increasingly expensive reads and updates;
- contention when many writers update the same parent document;
- poor pagination and indexing behavior; and
- excessive data transfer when most queries need only a small subset.

Bound arrays deliberately or move the growing records to a separate collection.

### 6.3 Model A: extensive embedding

For repeatable query examples, define these IDs once in the same `mongosh` session and use the same fixture IDs in both designs:

```javascript
const demoCustomerId = ObjectId("65a000000000000000000101");
const demoProductId = ObjectId("65a000000000000000000201");
const demoOrderId = ObjectId("65a000000000000000000301");
const demoOrderLineId = ObjectId("65a000000000000000000401");
```

For the exercise, put customer snapshot, order lines, and shipping details directly into each order. Product metadata needed for the historical receipt is also embedded in the line item. The fixture snippets below are inserted into their named collections so the following five queries can be run against the sample data.

``` javascript
// orders_embedded
const embeddedOrderExample = {
  _id: demoOrderId,
  orderNumber: "ORD-10001",
  createdAt: ISODate("2026-10-01T10:15:00Z"),
  status: "paid",
  customer: {
    customerId: demoCustomerId,
    name: "Taylor Reed",
    email: "taylor@example.test"
  },
  shippingAddress: {
    city: "Pune",
    country: "IN"
  },
  items: [
    {
      productId: demoProductId,
      sku: "MUG-BLUE",
      name: "Blue Mug",
      category: "kitchen",
      quantity: 2,
      unitPrice: Decimal128("12.50")
    }
  ],
  totals: { grandTotal: Decimal128("28.00") },
  schemaVersion: 1
};

// Repeatable fixture load; rerunning replaces this one lab order by its stable _id.
db.orders_embedded.replaceOne(
  { _id: demoOrderId }, embeddedOrderExample, { upsert: true }
);
```

**Access patterns served well:** fetch a complete order receipt, list a customer’s recent orders (with a suitable index), and calculate order totals from embedded lines.

**Trade-offs:** customer and product snapshots are duplicated across orders. This is intentional for historical receipts: if the product name or customer email changes later, the past order remains as purchased. Current product price/inventory still belongs in the products collection, not in an order snapshot.

#### Five representative queries for the embedded model

``` javascript
// 1. Fetch an order receipt.
db.orders_embedded.findOne({ orderNumber: "ORD-10001" })

// 2. Recent orders for a customer.
db.orders_embedded.find({ "customer.customerId": demoCustomerId })
  .sort({ createdAt: -1, _id: -1 }).limit(20)

// 3. Paid orders in a date range.
db.orders_embedded.find({
  status: "paid",
  createdAt: {
    $gte: ISODate("2026-10-01T00:00:00Z"),
    $lt: ISODate("2026-11-01T00:00:00Z")
  }
})

// 4. Orders containing a line for a given SKU.
db.orders_embedded.find({ "items.sku": "MUG-BLUE" })

// 5. Aggregate sold units by category.
db.orders_embedded.aggregate([
  { $unwind: "$items" },
  { $group: { _id: "$items.category", units: { $sum: "$items.quantity" } } },
  { $sort: { units: -1 } }
])
```

Indexes aligned with these query shapes can be created after loading the fixture:

```javascript
db.orders_embedded.createIndex({ orderNumber: 1 }, { unique: true });
db.orders_embedded.createIndex({ "customer.customerId": 1, createdAt: -1, _id: -1 });
db.orders_embedded.createIndex({ "items.sku": 1 });
```

The embedded model makes the receipt query simple. The category aggregation must unwind line items; for a large dataset it can scan many orders unless a valid early filter narrows the input. The multikey index on `items.sku` helps SKU lookup, not an unfiltered all-orders category aggregation.

### 6.4 Model B: extensive referencing

Separate customers, products, orders, and order lines. The order contains references to customer and product records. For historical reporting, it is often still prudent to store purchased unit price and category/name snapshots on the order line; “fully referenced” in this exercise means the entities are separate, not that all historical facts must be looked up from mutable current records.

``` javascript
// customers
const customerExample = {
  _id: demoCustomerId,
  name: "Taylor Reed",
  email: "taylor@example.test"
};

// products
const productExample = {
  _id: demoProductId,
  sku: "MUG-BLUE",
  name: "Blue Mug",
  category: "kitchen",
  currentPrice: Decimal128("13.00")
};

// orders
const orderExample = {
  _id: demoOrderId,
  orderNumber: "ORD-10001",
  customerId: ObjectId("65a000000000000000000101"),
  createdAt: ISODate("2026-10-01T10:15:00Z"),
  status: "paid",
  shippingAddress: { city: "Pune", country: "IN" },
  shipping: Decimal128("3.00"),
  total: Decimal128("28.00")
};

// order_lines
const orderLineExample = {
  _id: demoOrderLineId,
  orderId: demoOrderId,
  productId: demoProductId,
  skuAtPurchase: "MUG-BLUE",
  productNameAtPurchase: "Blue Mug",
  categoryAtPurchase: "kitchen",
  quantity: 2,
  unitPriceAtPurchase: Decimal128("12.50")
};

// Repeatable fixture load into the referenced collections.
db.customers.replaceOne({ _id: customerExample._id }, customerExample, { upsert: true });
db.products.replaceOne({ _id: productExample._id }, productExample, { upsert: true });
db.orders.replaceOne({ _id: orderExample._id }, orderExample, { upsert: true });
db.order_lines.replaceOne({ _id: orderLineExample._id }, orderLineExample, { upsert: true });
```

**Access patterns served well:** independently manage product/customer records, query orders and order lines separately, and avoid duplicating mutable current fields. The cost is more queries or `$lookup` for a complete receipt and extra care to keep relationships and historical snapshots correct.

#### Five representative queries for the referenced model

``` javascript
// 1. Fetch an order.
db.orders.findOne({ orderNumber: "ORD-10001" })

// 2. Find order lines for an order.
db.order_lines.find({ orderId: demoOrderId })

// 3. Find recent orders for one customer.
db.orders.find({ customerId: demoCustomerId })
  .sort({ createdAt: -1, _id: -1 }).limit(20)

// 4. Fetch an order and its line items with a join-like lookup.
db.orders.aggregate([
  { $match: { orderNumber: "ORD-10001" } },
  {
    $lookup: {
      from: "order_lines",
      localField: "_id",
      foreignField: "orderId",
      as: "lines"
    }
  }
])

// 5. Aggregate purchased units by historical category.
db.order_lines.aggregate([
  { $group: { _id: "$categoryAtPurchase", units: { $sum: "$quantity" } } },
  { $sort: { units: -1 } }
])
```

The five queries intentionally cover order retrieval, child retrieval, customer history, join-like retrieval, and aggregation. Candidate indexes aligned with the shown queries are:

```javascript
db.orders.createIndex({ orderNumber: 1 }, { unique: true });
db.orders.createIndex({ customerId: 1, createdAt: -1, _id: -1 });
db.order_lines.createIndex({ orderId: 1 });
```

The referencing design may be preferable when line items are independently queried or when orders can be very large, but it is not automatically faster. Retain each index only if the measured workload justifies its storage and write-maintenance cost.

### 6.5 Compare the two models

| Concern                         | Extensive embedding                                    | Extensive referencing                                                           |
|---------------------------------|--------------------------------------------------------|---------------------------------------------------------------------------------|
| Receipt read                    | Usually one document read                              | Often multiple reads or `$lookup`                                               |
| Customer/product current fields | Duplication; update many snapshots only if desired     | Current entity is stored once                                                   |
| Historical price/category       | Natural to snapshot in line                            | Still should usually snapshot on line                                           |
| Write complexity                | Simple for bounded related data; parent may become hot | More writes and coordination across collections                                 |
| Atomicity                       | One document update is atomic                          | Multi-document invariants may require a transaction                             |
| Document size                   | Can grow; 16 MiB limit applies                         | More bounded parent documents                                                   |
| Analytics                       | Nested arrays require `$unwind`                        | Separate line collection may simplify line-level aggregation                    |
| Data integrity                  | Application/schema validation and update discipline    | References still do not create relational foreign-key constraints automatically |

A production model is often **hybrid**: embed bounded data commonly read together; reference independently managed or unbounded entities; snapshot historical values where business semantics require them.

### 6.6 Additional modelling patterns

#### Bucket pattern

Group a bounded batch of events into a bucket document, such as hourly sensor readings or a day of metrics. Include a bucket boundary and a bounded array/count. Benefits include fewer documents and efficient range reads; risks include hot buckets and document growth. Do not create a bucket that can grow forever.

#### Subset pattern

Store a small, frequently requested subset on a parent document and keep the full set separately. Example: embed the most recent 3 reviews on a product page, while all reviews live in `reviews`. This reduces common page-read cost without an unbounded array.

#### Computed pattern

Precompute values that are expensive to calculate repeatedly, such as product review count or daily category revenue. The derived value can make reads fast, but updates and backfills must be correct and idempotent. Define whether the value is exact, delayed, or eventually reconciled.

#### Extended-reference pattern

Duplicate a few frequently needed fields from a referenced entity, such as product name and SKU in an order line, while keeping the canonical product in `products`. This reduces joins. Decide whether duplicated fields are historical snapshots or denormalized current values; they have different update rules.

#### Polymorphic pattern

Store documents of related but non-identical shapes in one collection, using a discriminator such as `kind: "physical"` or `kind: "digital"`. Shared queries are convenient, but validate each variant and index the fields that are actually queried. Do not let “polymorphic” become uncontrolled schema drift.

#### Schema versioning

Include a field such as `schemaVersion: 1`. When a document shape changes, define how readers handle old versions, how writes migrate data, and whether a background migration is required.

``` javascript
db.orders.updateMany(
  { schemaVersion: { $exists: false } },
  { $set: { schemaVersion: 1 } }
)
```

This example only sets a version marker; it is not a full migration if old documents need field transformations. Test migration code on a backup or staging copy and make it restartable.

## 7. Indexes: build them for real query shapes

An index is an auxiliary data structure that can reduce the amount of collection data examined. Indexes consume storage and memory and add work to inserts, updates, and deletes. An index is a trade-off, not a free speed button.

### 7.1 Single-field index

``` javascript
db.orders.createIndex({ customerId: 1 })
```

Useful for queries filtering by `customerId`. `1` means ascending index order; `-1` means descending. For a single field, MongoDB can often traverse an index in either direction, but sort direction interactions matter more for compound indexes.

### 7.2 Compound index and ESR

A compound index stores keys in a specified order. A common design heuristic is **ESR: Equality, Sort, Range**.

Suppose the query is:

``` javascript
db.orders.find({
  status: "paid",
  createdAt: { $gte: ISODate("2026-10-01T00:00:00Z"),
               $lt: ISODate("2026-11-01T00:00:00Z") }
}).sort({ customerId: 1 }).limit(100)
```

A possible candidate index based on equality, sort, then range is:

``` javascript
db.orders.createIndex({ status: 1, customerId: 1, createdAt: 1 })
```

This is only a candidate. The best order depends on the exact query, whether the requested sort is supported by the index order, range predicates, selectivity, index prefixes, data distribution, and the cost of scanning additional keys. Some workloads benefit from ERS (Equality, Range, Sort), especially when a selective range greatly narrows results and an in-memory sort is acceptable. Measure both if appropriate.

**ESR does not mean every compound index must mechanically follow the same order.** Explain the query first, identify equality predicates, sort requirements, and range conditions, then inspect the actual plan.

### 7.3 Multikey index

An index on an array field becomes a multikey index:

``` javascript
db.products.createIndex({ tags: 1 })
db.products.find({ tags: "office" })
```

MongoDB indexes array elements. Multikey indexes have restrictions, especially around compound indexes that include multiple array fields and sort behavior. Check the specific index definition and query plan rather than assuming any combination is valid.

### 7.4 Text index

For basic built-in text search:

``` javascript
db.products.createIndex({ name: "text", description: "text" })
db.products.find({ $text: { $search: "blue ceramic mug" } })
  .project({ score: { $meta: "textScore" }, name: 1 })
  .sort({ score: { $meta: "textScore" } })
```

MongoDB’s built-in text index is not equivalent to Atlas Search or a dedicated search engine. It has specific language, tokenization, and query limitations. A collection has restrictions on the number/configuration of built-in text indexes; verify your version’s documentation before designing around them.

### 7.5 TTL index

TTL indexes automatically expire documents based on a date field or a configured age. They are useful for sessions or temporary records, not for exact real-time scheduling; expiration is performed asynchronously by a background process.

``` javascript
db.sessions.createIndex(
  { expiresAt: 1 },
  { expireAfterSeconds: 0 }
)

db.sessions.insertOne({
  sessionId: "sess-demo",
  customerId: ObjectId(),
  expiresAt: new Date(Date.now() + 60_000)
})
```

With `expireAfterSeconds: 0`, the stored date is the expiry time. The document may remain after the timestamp briefly; do not assert it disappears at the exact millisecond. TTL deletion is not a substitute for authorization checks or application-level expiry validation.

### 7.6 Partial index

A partial index includes only documents matching a filter:

``` javascript
db.orders.createIndex(
  { createdAt: -1, customerId: 1 },
  { partialFilterExpression: { status: "paid" } }
)
```

This can reduce index size if queries commonly target paid orders. A query must have a predicate that ensures using the partial index cannot omit valid results; the optimizer cannot use it for every query on those fields. Confirm with `explain()`.

### 7.7 Unique and compound indexes

``` javascript
db.products.createIndex({ sku: 1 }, { unique: true })
db.orders.createIndex({ customerId: 1, createdAt: -1, _id: -1 })
db.order_lines.createIndex({ orderId: 1, productId: 1 })
```

The second index supports a common “recent orders by customer” pattern with a deterministic tie-breaker. The third supports fetching order lines by order ID; add uniqueness only if the data model guarantees the key is unique.

### 7.8 `explain()` and query-plan analysis

Before indexing:

``` javascript
db.orders.find({
  status: "paid",
  createdAt: {
    $gte: ISODate("2026-10-01T00:00:00Z"),
    $lt: ISODate("2026-11-01T00:00:00Z")
  }
}).sort({ customerId: 1 }).limit(100)
 .explain("executionStats")
```

After creating the candidate compound index, rerun the **same query** with `explain("executionStats")`.

Inspect: - `queryPlanner.winningPlan`: the selected plan shape. - `IXSCAN`: an index scan; useful but not proof that the index is optimal. - `COLLSCAN`: a collection scan. - `totalKeysExamined`: index keys examined. - `totalDocsExamined`: documents examined. - `nReturned`: number of results. - execution time fields: observed for this run and environment; they can vary due to cache, load, and data distribution.

An index is useful when it reduces work for the target query without unacceptable write/storage costs. Do not compare one cold-cache run to one warm-cache run and claim a universal speedup. The lesson does not prescribe fabricated `explain()` output; your lab must save the real plan from your environment.

## 8. Aggregation pipelines

An aggregation pipeline passes documents through ordered stages. Each stage receives the previous stage’s output and transforms, filters, groups, or writes it.

``` text
collection
   │
   ▼
$match  → filter documents
   │
   ▼
$unwind → one output per array element
   │
   ▼
$group  → aggregate by key
   │
   ▼
$sort   → order aggregate rows
   │
   ▼
$merge  → write results to a target collection
```

### 8.1 `$match`

``` javascript
db.orders.aggregate([
  { $match: { status: "paid" } }
])
```

Filters documents. Put selective filters early when semantics permit; an initial `$match` can often use collection indexes. Do not move filters across stages if doing so changes the result.

### 8.2 `$project`

``` javascript
db.orders.aggregate([
  { $project: {
      orderNumber: 1,
      customerId: 1,
      createdAt: 1,
      grandTotal: "$totals.grandTotal",
      _id: 0
  } }
])
```

Shapes output fields, renames fields, and can compute expressions. Use it to make pipeline output explicit and avoid carrying unnecessary fields when that benefits readability or processing.

### 8.3 `$unwind`

``` javascript
db.orders.aggregate([
  { $unwind: "$items" },
  { $project: {
      orderNumber: 1,
      sku: "$items.sku",
      category: "$items.category",
      quantity: "$items.quantity"
  } }
])
```

A document with three items produces three pipeline documents. By default, missing, null, and empty arrays are dropped. Use `preserveNullAndEmptyArrays: true` when the business question requires retaining parents without items. `$unwind` can multiply row counts dramatically, so filter orders first if valid and useful.

### 8.4 `$group`

``` javascript
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $unwind: "$items" },
  { $group: {
      _id: "$items.category",
      unitsSold: { $sum: "$items.quantity" },
      lineRevenue: {
        $sum: { $multiply: ["$items.quantity", "$items.unitPrice"] }
      }
  } },
  { $sort: { lineRevenue: -1 } }
])
```

`_id` is the group key. Accumulators include `$sum`, `$avg`, `$min`, `$max`, `$first`, `$last`, `$push`, and `$addToSet`. The order of documents reaching `$first`/`$last` is not guaranteed unless the pipeline defines an appropriate sort first.

### 8.5 `$sort`

``` javascript
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $sort: { createdAt: -1, _id: -1 } },
  { $limit: 10 }
])
```

Sorting before a grouping stage and sorting after grouping answer different questions. If sorting input for `$first`/`$last`, place it before `$group`; if sorting grouped results, place it after `$group`.

### 8.6 `$lookup`

`$lookup` performs a left outer join from documents in one collection to matching documents in another, producing an array field.

``` javascript
db.orders.aggregate([
  { $match: { orderNumber: "ORD-10001" } },
  {
    $lookup: {
      from: "order_lines",
      localField: "_id",
      foreignField: "orderId",
      as: "lines"
    }
  }
])
```

Index the foreign field used for matching when appropriate (here, `order_lines.orderId`). `$lookup` can be useful, but frequent joins across very large collections may signal that a read-heavy access pattern should be modelled differently. Pipeline-form `$lookup` and sharded-collection support have version-specific details; verify the target server version.

### 8.7 `$facet`

`$facet` runs multiple sub-pipelines over the same input and returns each result under its own field.

``` javascript
db.products.aggregate([
  { $match: { active: true } },
  {
    $facet: {
      byCategory: [
        { $group: { _id: "$category", count: { $sum: 1 } } },
        { $sort: { count: -1 } }
      ],
      priceBands: [
        {
          $bucket: {
            groupBy: "$price",
            boundaries: [
              Decimal128("0.00"),
              Decimal128("10.00"),
              Decimal128("25.00"),
              Decimal128("50.00"),
              Decimal128("1000.00")
            ],
            default: "other",
            output: { count: { $sum: 1 } }
          }
        }
      ]
    }
  }
])
```

`$facet` is useful for page results plus category counts or price bands. It has a 100 MB limit for its resulting document and cannot spill that `$facet` memory to disk; the final aggregation result document is also subject to the 16 MiB BSON document limit. `allowDiskUse: true` does not remove the `$facet` limit. Test with realistic cardinalities.

### 8.8 `$bucket`

`$bucket` groups documents into specified ranges of a field or expression.

``` javascript
db.products.aggregate([
  {
    $bucket: {
      groupBy: "$price",
      boundaries: [
        Decimal128("0.00"),
        Decimal128("10.00"),
        Decimal128("25.00"),
        Decimal128("50.00"),
        Decimal128("1000.00")
      ],
      default: "other",
      output: {
        count: { $sum: 1 },
        averagePrice: { $avg: "$price" }
      }
    }
  }
])
```

Boundary intervals are lower-inclusive and upper-exclusive. The `default` bucket captures values outside the defined boundaries; choose boundaries that make sense for the dataset and BSON type.

### 8.9 `$merge` and `$out`

`$merge` writes pipeline output into a target collection and can merge by a key; it is useful for incremental or repeatable materialization patterns when the pipeline and merge key are designed carefully.

``` javascript
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $unwind: "$items" },
  {
    $group: {
      _id: {
        day: {
          $dateTrunc: {
            date: "$createdAt",
            unit: "day",
            timezone: "UTC"
          }
        },
        category: "$items.category"
      },
      revenue: {
        $sum: { $multiply: ["$items.quantity", "$items.unitPrice"] }
      },
      units: { $sum: "$items.quantity" }
    }
  },
  {
    $project: {
      _id: 0,
      day: "$_id.day",
      category: "$_id.category",
      revenue: 1,
      units: 1
    }
  },
  {
    $merge: {
      into: "daily_category_revenue",
      on: ["day", "category"],
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
])
```

This uses `$dateTrunc`, available in modern MongoDB versions; verify the server version. The target collection needs a compatible unique index whose keys correspond exactly to the custom `on` fields (for this example, `{day:1, category:1}` with `unique: true`) and whose collation matches the aggregation if a collation is specified. MongoDB permits sparse unique indexes for `$merge`, but this example uses a regular non-sparse index because both key fields should always be present. The target fields should exist and have consistent types; null/missing key values are not suitable for this custom key. Check the target index and deployment/version requirements before running. `$merge` does not automatically delete target rows whose source group disappears; define a reconciliation strategy if source data can be corrected or deleted.

`$out` writes the pipeline result to a collection, replacing the target collection as part of the operation’s semantics. It is useful for full rebuilds, but has different constraints and operational implications from `$merge`. Check version-specific support, especially for sharded targets and transactions. Do not use `$out` when you intend to merge into existing target records.

Example of a full rebuild (use a dedicated target and confirm the replacement semantics before running):

```javascript
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $unwind: "$items" },
  {
    $group: {
      _id: "$items.category",
      units: { $sum: "$items.quantity" },
      revenue: {
        $sum: { $multiply: ["$items.quantity", "$items.unitPrice"] }
      }
    }
  },
  { $project: { _id: 0, category: "$_id", units: 1, revenue: 1 } },
  { $out: "paid_category_summary_rebuild" }
])
```

This rebuild replaces the contents of `paid_category_summary_rebuild`; it does not merge individual results into existing rows. It is not a substitute for `$merge` when preserving unrelated target records is required.

## 9. Convert three SQL aggregation patterns

Use these as a learning exercise: identify the relational operation, map it to pipeline stages, and state what each stage emits.

### 9.1 SQL `GROUP BY`

SQL:

``` sql
SELECT category,
       SUM(quantity) AS units_sold,
       SUM(quantity * unit_price) AS revenue
FROM order_lines
GROUP BY category
ORDER BY revenue DESC;
```

MongoDB (`order_lines` has one document per line):

``` javascript
db.order_lines.aggregate([
  {
    $group: {
      _id: "$categoryAtPurchase",
      unitsSold: { $sum: "$quantity" },
      revenue: {
        $sum: { $multiply: ["$quantity", "$unitPriceAtPurchase"] }
      }
    }
  },
  { $project: { _id: 0, category: "$_id", unitsSold: 1, revenue: 1 } },
  { $sort: { revenue: -1 } }
])
```

Reasoning: `$group` maps to `GROUP BY`; `$sum` maps to aggregate expressions; `$project` renames `_id`; `$sort` maps to `ORDER BY`.

### 9.2 SQL `JOIN`

SQL:

``` sql
SELECT o.order_number, c.name, o.status
FROM orders o
JOIN customers c ON c._id = o.customer_id
WHERE o.status = 'paid';
```

MongoDB:

``` javascript
db.orders.aggregate([
  { $match: { status: "paid" } },
  {
    $lookup: {
      from: "customers",
      localField: "customerId",
      foreignField: "_id",
      as: "customer"
    }
  },
  { $unwind: "$customer" },
  {
    $project: {
      _id: 0,
      orderNumber: 1,
      status: 1,
      customerName: "$customer.name"
    }
  }
])
```

Reasoning: `$match` reduces orders before the join; `$lookup` adds an array of matching customers; `$unwind` turns the matching array into a joined row; `$project` chooses output fields. This uses inner-join-like behavior because `$unwind` drops unmatched orders by default. To retain unmatched orders (left-join behavior), use `$unwind` with `preserveNullAndEmptyArrays: true`.

### 9.3 SQL top-N

SQL:

``` sql
SELECT category, SUM(quantity * unit_price) AS revenue
FROM order_lines
GROUP BY category
ORDER BY revenue DESC
LIMIT 5;
```

MongoDB:

``` javascript
db.order_lines.aggregate([
  {
    $group: {
      _id: "$categoryAtPurchase",
      revenue: {
        $sum: { $multiply: ["$quantity", "$unitPriceAtPurchase"] }
      }
    }
  },
  { $sort: { revenue: -1, _id: 1 } },
  { $limit: 5 },
  { $project: { _id: 0, category: "$_id", revenue: 1 } }
])
```

Reasoning: aggregate first, sort the aggregate results, then limit to five. `_id: 1` is a deterministic tie-breaker for equal revenue. A `$limit` before `$group` would answer a different question.

## 10. Daily revenue per category with `$unwind`, `$group`, and `$merge`

This is a required roadmap deliverable. Assume `orders` has `createdAt`, `status`, and an `items` array with `category`, `quantity`, and `unitPrice`.

First create a unique target index:

``` javascript
db.daily_category_revenue.createIndex(
  { day: 1, category: 1 },
  { unique: true }
)
```

Then run:

``` javascript
db.orders.aggregate([
  {
    $match: {
      status: "paid",
      createdAt: {
        $gte: ISODate("2026-10-01T00:00:00Z"),
        $lt: ISODate("2026-11-01T00:00:00Z")
      }
    }
  },
  { $unwind: "$items" },
  {
    $group: {
      _id: {
        day: {
          $dateTrunc: {
            date: "$createdAt",
            unit: "day",
            timezone: "UTC"
          }
        },
        category: "$items.category"
      },
      revenue: {
        $sum: { $multiply: ["$items.quantity", "$items.unitPrice"] }
      },
      units: { $sum: "$items.quantity" },
      orderCountByLine: { $sum: 1 }
    }
  },
  {
    $project: {
      _id: 0,
      day: "$_id.day",
      category: "$_id.category",
      revenue: 1,
      units: 1,
      orderCountByLine: 1
    }
  },
  {
    $merge: {
      into: "daily_category_revenue",
      on: ["day", "category"],
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
])
```

`orderCountByLine` is intentionally named to avoid implying distinct order count: one order with two items in the same category contributes two line documents after `$unwind`. If you need distinct orders per category, use an appropriate intermediate grouping by day/category/order ID before the final aggregation.

**Operational caution:** this pipeline recomputes the selected date range and replaces matching target keys, but it does not remove target rows for categories/days that no longer appear after a correction. For a reliable materialization, define how to clear/rebuild the affected date range or reconcile the target. For full correctness with corrections/deletes, a bounded rebuild into a staging collection followed by controlled replacement may be safer than blindly merging partial aggregates.

## 11. Schema validation with JSON Schema

MongoDB allows collection validators to enforce a document shape on writes. Validation is valuable because flexible schema should not mean uncontrolled schema.

Create a validator for orders:

``` javascript
db.createCollection("validated_orders", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["orderNumber", "customerId", "createdAt", "status", "items", "schemaVersion"],
      properties: {
        orderNumber: { bsonType: "string" },
        customerId: { bsonType: "objectId" },
        createdAt: { bsonType: "date" },
        status: {
          enum: ["pending", "paid", "shipped", "cancelled", "refunded"]
        },
        schemaVersion: { bsonType: "int" },
        items: {
          bsonType: "array",
          minItems: 1,
          items: {
            bsonType: "object",
            required: ["sku", "quantity", "unitPrice"],
            properties: {
              sku: { bsonType: "string" },
              quantity: { bsonType: ["int", "long"], minimum: 1 },
              unitPrice: { bsonType: "decimal", minimum: 0 }
            }
          }
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
})
```

The server’s JSON Schema dialect is MongoDB’s supported subset; it is not identical to every draft of JSON Schema. Numeric keyword/type support should be tested against the exact server version. In particular, use BSON-aware types such as `objectId`, `date`, and `decimal` rather than assuming plain JSON types cover them.

Valid insert:

``` javascript
db.validated_orders.insertOne({
  orderNumber: "ORD-VALID-1",
  customerId: ObjectId(),
  createdAt: new Date(),
  status: "pending",
  schemaVersion: NumberInt(1),
  items: [
    { sku: "MUG-BLUE", quantity: NumberInt(2), unitPrice: Decimal128("12.50") }
  ]
})
```

Expected rejection: this document is missing required `items` and other required fields, so the validator should reject it under `validationAction: "error"`:

``` javascript
db.validated_orders.insertOne({
  orderNumber: "ORD-INVALID-1",
  status: "unknown"
})
```

Record the actual validation error in your lab; the exact error text can vary by server version. Validators can be bypassed by authorized operations configured to bypass document validation, so they are a strong guardrail, not a substitute for access control and application validation.

## 12. PyMongo and typed access

Install in the project’s Python environment:

``` bash
uv add pymongo
```

For local development, use a local connection URI. Store production credentials in a secret manager/environment variables, not source code.

``` python
from __future__ import annotations

import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from bson.decimal128 import Decimal128
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError


MONGODB_URI = os.environ.get(
    "MONGODB_URI",
    "mongodb://localhost:27017/",
)

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5_000)
client.admin.command("ping")

db = client["ecommerce"]
products: Collection[dict[str, Any]] = db["products"]

product = {
    "sku": "MUG-GREEN",
    "name": "Green Mug",
    "category": "kitchen",
    "price": Decimal128("14.25"),
    "active": True,
    "createdAt": datetime.now(timezone.utc),
}

try:
    result = products.insert_one(product)
except DuplicateKeyError:
    raise RuntimeError("SKU must be unique; handle the duplicate explicitly")

saved = products.find_one(
    {"_id": result.inserted_id},
    {"sku": 1, "name": 1, "price": 1, "_id": 1},
)
if saved is None:
    raise RuntimeError("Inserted product could not be read back")

price_bson = saved["price"]
if not isinstance(price_bson, Decimal128):
    raise TypeError("Unexpected BSON type for price")

price_decimal: Decimal = price_bson.to_decimal()
print(saved["sku"], saved["name"], price_decimal)
client.close()
```

Purpose and edge cases: - `MongoClient` manages a connection pool; it is normally reused rather than created for every request. - `ping` checks connectivity at startup; it does not prove every later operation will succeed. - `Collection[dict[str, Any]]` adds useful static type hints but does not validate BSON data at runtime. - `Decimal128.to_decimal()` converts the BSON decimal value to Python `Decimal`. - ObjectIds are identifiers, not authorization controls. - Handle duplicate keys, timeouts, network errors, and retry behavior explicitly in production.

### 12.1 Typed document model

A lightweight typed representation helps prevent inconsistent application writes:

``` python
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field


class OrderLineInput(BaseModel):
    sku: str
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=Decimal("0"))


class OrderInput(BaseModel):
    order_number: str
    customer_id: str
    created_at: datetime
    status: Literal["pending", "paid", "shipped", "cancelled", "refunded"]
    items: list[OrderLineInput] = Field(min_length=1)
```

This example uses Pydantic 2-style field constraints. It is application validation, not MongoDB server validation. Convert `customer_id` to `ObjectId` and `unit_price` to `Decimal128` at the persistence boundary, and keep the Python model and server validator aligned. Do not assume a Python type annotation alone changes the stored BSON type.

## 13. Replica sets, read/write concerns, and transactions

### 13.1 Replica sets

A replica set is a group of `mongod` processes maintaining the same data set. One member is primary; eligible secondary members replicate the primary’s oplog. If the primary becomes unavailable, eligible members can hold an election to select a new primary.

``` text
             application writes
                    │
                    ▼
                 Primary
                /        \
               ▼          ▼
          Secondary B  Secondary C
```

The topology and settings determine which members are eligible and how quickly a new primary is elected. Election is not instantaneous; writes may fail or pause during the transition. A successful election does not mean every secondary is fully caught up at every instant.

### 13.2 Read preference

Read preference selects which replica-set members may serve reads:

- `primary`: read from primary.
- `primaryPreferred`: prefer primary, fall back to eligible secondary when needed.
- `secondary`: read from secondary members.
- `secondaryPreferred`: prefer secondary, fall back to primary.
- `nearest`: select among members meeting latency and staleness constraints.

Secondary reads may be stale. Read preference is a routing policy; it does not by itself define the visibility guarantee of returned data. The exact options and restrictions should be checked against the driver/server version.

### 13.3 Read concern

Read concern controls the consistency/isolation properties of data returned by reads in supported contexts. Common modes include:

- `"local"`: data returned need not be majority committed.
- `"majority"`: reads data acknowledged by a majority of replica-set members.
- `"linearizable"`: provides real-time order guarantees for supported primary reads, subject to documented constraints.
- `"snapshot"`: reads from a consistent snapshot in supported transaction/operation contexts.

These modes have different availability and latency costs. `linearizable` is for supported reads from the primary and has documented restrictions; it is not a general setting for secondary reads. Read concern does not make a multi-operation workflow transactional by itself.

### 13.4 Write concern

Write concern defines what acknowledgement a write must receive before the client is told it succeeded. Common examples include `w: 1` and `w: "majority"`; journaling options can add durability requirements depending on configuration.

``` javascript
db.orders.insertOne(
  { orderNumber: "ORD-WC-1", status: "pending", createdAt: new Date() },
  { writeConcern: { w: "majority", wtimeout: 5000 } }
)
```

A write-concern timeout does not necessarily mean the write did not happen; it means the requested acknowledgement was not received within the timeout. Handle ambiguous outcomes using idempotency keys or a follow-up read.

Read concern, read preference, and write concern are separate controls. For example, reading from a secondary does not become linearizable simply because the preceding write used majority write concern.

### 13.5 Transactions and costs

MongoDB supports multi-document transactions on supported replica-set and sharded-cluster deployments. They provide atomicity across participating operations, but add coordination, resource, and latency costs. Transactions also have limits and operational considerations that vary by version/deployment.

Prefer a single-document atomic update when the invariant naturally fits one document. Use a transaction when a business invariant truly spans documents and cannot be safely implemented with a different model. Keep transactions short, avoid external network calls inside them, and design retry logic for transient transaction errors. A transaction is not a substitute for appropriate data modelling.

## 14. Sharding and shard-key design

Sharding distributes a collection across multiple shards to scale storage and throughput. MongoDB divides data into chunks/ranges or hash-distributed values according to the shard key; the balancer manages chunk distribution subject to constraints.

### 14.1 Choose the shard key from access patterns

Evaluate: - **Cardinality:** does the key have many distinct values? - **Distribution:** will writes and storage spread across shards? - **Query targeting:** do common queries include the shard key so the router can target shards? - **Write pattern:** does the key concentrate writes on one range/shard? - **Growth and operational needs:** can the key support future data volume and movement?

A shard key is difficult to change after deployment. Test distribution with representative data and traffic, not just a small sample.

### 14.2 Ranged versus hashed keys

- **Ranged shard key:** preserves ordering locality. It can efficiently target ranges, but monotonically increasing keys (such as timestamps or sequential IDs) can concentrate new writes on the current range.
- **Hashed shard key:** hashes the key to distribute values more evenly, which can reduce monotonic write hotspots. It often makes range queries on the original key less efficient and may scatter queries that do not include the shard key.

Neither choice is universally superior. Compound shard keys can combine a distribution component with query-oriented fields, but their order and cardinality must be reasoned through.

### 14.3 Chunk balancing, jumbo chunks, hot shards

- **Chunk balancing:** MongoDB moves chunks to keep data distribution within configured balancing goals. Movement consumes network and I/O and can affect workload performance.
- **Jumbo chunk:** a chunk too large to split under the shard-key distribution and configured limits, commonly because many documents share the same shard-key value. It can block balancing for that chunk and may require shard-key/data-distribution remediation.
- **Hot shard:** one shard receives disproportionate traffic or storage, often due to a poor key, skewed values, or workload locality. Adding shards does not fix a hot key automatically.

Monitor shard distribution, query targeting, write latency, chunk migration activity, and per-shard load. Do not select a shard key solely because it is unique.

## 15. Aggregation performance and operational guardrails

### 15.1 Pipeline ordering

- Place selective `$match` stages early when semantics permit.
- Use a suitable index for an initial filter or sort where possible.
- `$unwind` can multiply documents; filter before it if correct.
- Project only needed fields where it helps readability and resource use, while understanding that MongoDB can optimize some field pruning automatically.
- `$group`, `$sort`, `$facet`, and high-cardinality joins can be expensive.
- Put `$limit` before expensive work only when it preserves the required semantics; limiting before aggregation changes the population being aggregated.

### 15.2 Memory limits and `allowDiskUse`

Some aggregation stages have memory limits. Depending on server version/configuration and stage, an operation may fail when it exceeds a memory threshold or may spill to disk when disk use is permitted. Disk spilling can increase latency and I/O; it is not a substitute for sensible pipeline design.

Example:

``` javascript
db.orders.aggregate(
  [
    { $match: { status: "paid" } },
    { $unwind: "$items" },
    {
      $group: {
        _id: "$items.category",
        revenue: {
          $sum: { $multiply: ["$items.quantity", "$items.unitPrice"] }
        }
      }
    },
    { $sort: { revenue: -1 } }
  ],
  { allowDiskUse: true }
)
```

Check the server’s version-specific defaults for `allowDiskUseByDefault` and stage restrictions. Record the option used in your experiment. If an aggregation spills to disk, investigate cardinality, filter selectivity, index support, and whether a computed/materialized pattern is more appropriate.

### 15.3 Atlas Search, Vector Search, and time-series collections — awareness

- **Atlas Search:** managed search functionality built on Lucene, useful for relevance-ranked full-text search, analyzers, autocomplete, and richer search queries than a basic text index.
- **Atlas Vector Search:** supports similarity search over vector embeddings and can be combined with metadata filtering in supported configurations. It is relevant to AI retrieval systems but does not replace embedding generation, evaluation, or access control.
- **Time-series collections:** specialized storage for time-stamped measurements with metadata and bucketing behavior. They can improve workloads with high-volume measurements, but design around time/meta fields and the query patterns documented for the server version.

These are awareness topics in this lesson. Verify current Atlas/server availability, limits, and syntax for your environment; do not assume all managed Atlas features exist in a self-managed deployment.

## 16. Hands-on lab: `experiments/03_mongodb/`

**Verification discipline:** code examples in this lesson are instructional, not evidence that a MongoDB server was available during authoring. The lab requires a running compatible server to verify server-side query plans, validator errors, TTL cleanup, `$merge` behavior, and elections. Save actual outputs in `results/`; do not substitute estimated timings or fabricated plans.

### 16.1 Suggested project layout

``` text
experiments/
└── 03_mongodb/
    ├── README.md
    ├── docker-compose.yml
    ├── requirements.txt
    ├── generate_orders.py
    ├── queries.js
    ├── validators.js
    ├── aggregation.js
    ├── failover_notes.md
    └── results/
        ├── explain_before.json
        ├── explain_after.json
        └── observations.md
```

### 16.2 Setup

Requirements:

- MongoDB 7.x or 8.x; a standalone server is enough for CRUD, data loading, indexing, and aggregation.
- A replica set with at least three eligible voting members for the primary-election exercise and replica-set transaction demonstrations.
- `mongosh`, Python 3.12+, `uv` (or a virtual environment), and PyMongo 4.x.
- Enough local disk space for 500,000 synthetic orders, line items, and indexes.

Run all destructive experiments only against the dedicated `ecommerce_lab` database. The generator deliberately drops `ecommerce_lab.orders` before loading data. General Python examples default to `mongodb://localhost:27017/`; set `MONGODB_URI` explicitly when using a replica set. For example, `mongodb://localhost:27017/?replicaSet=rs0` works only when the replica-set member address advertised by the server is reachable from the client. Container hostnames may not resolve from the host, so run the client on the same Docker network or configure reachable member addresses. Adding `replicaSet=rs0` does not initialize a replica set.

For a replica-set container, use the known-good Docker Compose configuration from your module lab and initialize the replica set according to its instructions. A standalone server cannot demonstrate an election or replica-set transaction behavior.

Install:

``` bash
uv init
uv add pymongo pydantic
```

Before running the `mongosh` lab snippets in Sections 16.4–16.8, select the same database that the generator uses:

```javascript
use ecommerce_lab
```

This avoids running the shell-side index, aggregation, TTL, and validator examples in the default `test` database while the Python script writes to `ecommerce_lab`. The TTL polling Python snippet also reads `ecommerce_lab.sessions`.

### 16.3 Generate 500,000 orders with line items

Save as `generate_orders.py`. It generates deterministic synthetic data and inserts in batches. This sample emphasizes reproducibility and manageable memory usage; tune batch size based on your environment.

``` python
from __future__ import annotations

import os
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from bson.decimal128 import Decimal128
from pymongo import MongoClient
from pymongo.collection import Collection


URI = os.environ.get(
    "MONGODB_URI",
    "mongodb://localhost:27017/",
)
DB_NAME = "ecommerce_lab"
ORDER_COUNT = 500_000
BATCH_SIZE = 1_000
SEED = 20261019

CATEGORIES = ["kitchen", "stationery", "home", "electronics", "outdoors"]
STATUSES = ["pending", "paid", "shipped", "cancelled", "refunded"]


def build_order(i: int, rng: random.Random) -> dict:
    created_at = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(
        seconds=rng.randrange(0, 280 * 24 * 60 * 60)
    )
    item_count = rng.randint(1, 6)
    items = []
    for line_no in range(item_count):
        category = rng.choice(CATEGORIES)
        cents = rng.randint(300, 50_000)
        items.append({
            "sku": f"SKU-{rng.randrange(1, 20_001):05d}",
            "category": category,
            "quantity": rng.randint(1, 5),
            "unitPrice": Decimal128(Decimal(cents) / Decimal(100)),
            "lineNumber": line_no,
        })

    return {
        "orderNumber": f"ORD-{i:07d}",
        "customerId": f"CUST-{rng.randrange(1, 100_001):06d}",
        "createdAt": created_at,
        "status": rng.choice(STATUSES),
        "items": items,
        "schemaVersion": 1,
    }


def main() -> None:
    rng = random.Random(SEED)
    client = MongoClient(URI, serverSelectionTimeoutMS=5_000)
    client.admin.command("ping")
    db = client[DB_NAME]
    orders: Collection = db["orders"]

    # Use a fresh lab collection so repeated runs do not silently duplicate data.
    orders.drop()
    batch = []
    for i in range(1, ORDER_COUNT + 1):
        batch.append(build_order(i, rng))
        if len(batch) >= BATCH_SIZE:
            orders.insert_many(batch, ordered=True)
            batch.clear()
            if i % 50_000 == 0:
                print(f"Inserted {i:,} orders")
    if batch:
        orders.insert_many(batch, ordered=True)

    print("Final order count:", orders.count_documents({}))
    line_count_result = next(
        orders.aggregate([
            {"$project": {"lineCount": {"$size": "$items"}}},
            {"$group": {"_id": None, "lineItems": {"$sum": "$lineCount"}}},
        ]),
        {"lineItems": 0},
    )
    print("Final line-item count:", line_count_result["lineItems"])
    client.close()


if __name__ == "__main__":
    main()
```

Run:

``` bash
uv run python generate_orders.py
```

The script’s expected final order count is 500,000 if it completes without errors and targets the intended lab collection. Each order has 1–6 line items; the script also computes and prints the actual total line-item count from the loaded collection. It prints progress from the actual run; record what you observe. Because line-item counts are random but seeded, repeated successful runs with the same code and seed should generate the same data sequence. It intentionally drops `ecommerce_lab.orders`, so do not point it at production or a collection with data you need.

### 16.4 ESR experiment: compare `explain()` before and after

Use this query shape to find paid orders for a customer, in a time range, sorted newest-first:

``` javascript
const customer = "CUST-000123";

db.orders.find({
  customerId: customer,
  status: "paid",
  createdAt: {
    $gte: ISODate("2026-04-01T00:00:00Z"),
    $lt: ISODate("2026-05-01T00:00:00Z")
  }
}).sort({ createdAt: -1, _id: -1 }).limit(50)
 .explain("executionStats")
```

**Before:** save the real output:

``` javascript
const before = db.orders.find({
  customerId: customer,
  status: "paid",
  createdAt: {
    $gte: ISODate("2026-04-01T00:00:00Z"),
    $lt: ISODate("2026-05-01T00:00:00Z")
  }
}).sort({ createdAt: -1, _id: -1 }).limit(50)
 .explain("executionStats");

printjson(before);
```

Create a candidate ESR index: equality fields first, then sort, then range if the actual query shape supports this order. Here both `customerId` and `status` are equality predicates; `createdAt` is both a sort field and a range field. A candidate is:

``` javascript
db.orders.createIndex({
  customerId: 1,
  status: 1,
  createdAt: -1,
  _id: -1
})
```

This index can support the equality prefix and sort/range on `createdAt` for this query shape, but the actual usefulness must be checked. Re-run the exact same query and save the real output as `explain_after.json`.

Compare: - winning plan (`COLLSCAN` vs `IXSCAN` or other stages); - `totalKeysExamined`; - `totalDocsExamined`; - `nReturned`; - execution time, while noting cache state and run-to-run variation.

Do not claim a measured improvement until you have the outputs. If the plan does not use the index, check the exact query, existing indexes, index build completion, data distribution, and server plan selection. Use `hint()` only as a controlled diagnostic comparison, not as proof that the hinted index is always optimal.

### 16.5 Daily revenue aggregation

Adapt the pipeline in Section 10 to your generated `orders` collection. The generator includes status, timestamp, and item category/quantity/unit price. For this lab, create `daily_category_revenue` and a unique index on `{day:1, category:1}` before running `$merge`.

Important adaptation: generated `customerId` and SKU are strings, which is acceptable for this synthetic dataset. `unitPrice` is Decimal128. Make sure all records use the same numeric type so aggregation does not mix incompatible types.

Verify the target with:

``` javascript
db.daily_category_revenue.find().sort({ day: 1, category: 1 }).limit(20)
db.daily_category_revenue.countDocuments({})
```

Record the actual output and reconcile a few groups against a Python/SQL calculation on a small sample. Do not invent revenue totals.

### 16.6 Validator rejection experiment

Create the validator from Section 11 on a dedicated lab collection. Run one valid insert and one invalid insert. Record: - the accepted valid document; - the actual rejected insert response/error; - the exact missing or mistyped fields; - how you would roll out a validator against an existing collection.

For existing collections, `collMod` can apply validation settings, but existing invalid documents are not necessarily retroactively rewritten. A rollout plan should audit/repair existing data and decide whether validation is strict or moderate during migration.

### 16.7 TTL and partial index experiment

TTL:

``` javascript
db.sessions.drop();

db.sessions.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });
db.sessions.insertOne({
  sessionId: "ttl-demo",
  expiresAt: new Date(Date.now() + 30_000)
});

db.sessions.find({ sessionId: "ttl-demo" });
```

Poll from Python to capture the actual deletion time (run this after the insert above; use the same `MONGODB_URI` and database):

```python
import os
from time import monotonic, sleep
from pymongo import MongoClient

client = MongoClient(os.environ.get("MONGODB_URI", "mongodb://localhost:27017/"))
sessions = client["ecommerce_lab"]["sessions"]
started = monotonic()
deadline = started + 180
while monotonic() < deadline:
    if sessions.find_one({"sessionId": "ttl-demo"}) is None:
        print(f"TTL deletion observed after {monotonic() - started:.1f} seconds")
        break
    sleep(1)
else:
    print("Document still present after 180 seconds; inspect TTL index and server health")
client.close()
```

TTL cleanup is asynchronous, and the reported duration is an observation from this run, not a guarantee. Do not expect exact 30-second deletion.

Partial index (use a separate, small collection so the earlier ESR index cannot confound the demonstration):

```javascript
db.orders_partial_lab.drop();
db.orders_partial_lab.insertMany([
  { customerId: "CUST-000123", status: "paid", createdAt: ISODate("2026-10-01T10:00:00Z") },
  { customerId: "CUST-000123", status: "pending", createdAt: ISODate("2026-10-02T10:00:00Z") },
  { customerId: "CUST-000456", status: "paid", createdAt: ISODate("2026-10-03T10:00:00Z") }
]);

db.orders_partial_lab.createIndex(
  { customerId: 1, createdAt: -1 },
  {
    name: "paid_customer_recent",
    partialFilterExpression: { status: "paid" }
  }
);

// Controlled eligibility check: the predicate implies the partial filter.
db.orders_partial_lab.find({
  status: "paid",
  customerId: "CUST-000123"
}).sort({ createdAt: -1 }).hint("paid_customer_recent")
  .explain("executionStats");

// Do not force the partial index here: this query must include pending orders too.
db.orders_partial_lab.find({
  customerId: "CUST-000123"
}).sort({ createdAt: -1 }).explain("executionStats");
```

The first query explicitly forces the partial index as a controlled eligibility test for a predicate that includes `status: "paid"`; this does not prove the optimizer would choose it without `hint()`. The second query must return paid and pending orders, so the partial index alone is not a correct source for its complete result. A tiny collection may lead the optimizer to choose a collection scan when no hint is used; that is not proof the index is invalid. For a realistic planner comparison, repeat on the 500,000-order dataset and record the actual plans.

### 16.8 Replica-set primary failover experiment

Use a local replica set with at least three eligible voting members. A standalone server cannot demonstrate election behavior. Confirm the primary before starting:

``` javascript
rs.status()
db.hello()
```

Record the primary’s `me`/host information and current term/state where available. In a separate terminal, stop the primary using the safe procedure for your local Docker Compose setup. For example, after mapping the current primary to its Compose service, run `docker compose stop <primary-service-name>`; do not kill a production primary. Observe:

1.  whether the application’s writes pause or fail during election;
2.  how long until a new primary is elected;
3.  what `db.hello()` reports after failover;
4.  whether clients reconnect/retry;
5.  whether any operation returns an ambiguous timeout;
6.  what the secondaries report before and after election.

Restart the stopped node with `docker compose start <primary-service-name>` and watch it rejoin as a secondary if appropriate. Exact election duration depends on configuration, network, and version; do not hard-code an expected duration or assume failover is instantaneous. Document actual observations in `failover_notes.md`.

### 16.9 Troubleshooting

| Symptom                                  | Likely checks                                                                                                                |
|------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| Connection refused                       | Container health, port mapping, URI, authentication, TLS settings                                                            |
| “not primary” or election-related error  | Check `db.hello()`, wait for election, verify driver retry settings                                                          |
| Unique index build fails                 | Find and repair duplicates before creating the index                                                                         |
| Validator rejects valid-looking document | Check BSON types (`int` vs `long`, `Date`, `ObjectId`, `Decimal128`), required fields, enum values                           |
| TTL document remains after expiry        | TTL cleanup is asynchronous; verify indexed field is a BSON date and index options are correct                               |
| Index not used                           | Recheck filter/sort shape, index prefix, selectivity, collation, data size, and `explain()`                                  |
| `$merge` fails                           | Check target index on `on` fields, field types, permissions, and target schema                                               |
| Revenue differs from expected            | Check timezone boundaries, cancelled/refunded status policy, Decimal128 types, `$unwind` row multiplication, duplicate lines |
| Large aggregation fails or spills        | Inspect cardinality, `$unwind`, `$group`, sort, disk use, and whether early filters are possible                             |
| Replica-set URI fails                    | Confirm replica set is initialized and hostnames in the replica config are resolvable from the client                        |

## 17. Common mistakes

1.  Embedding an unbounded array and discovering the 16 MiB limit only after production growth.
2.  Choosing embedding or referencing based only on entity relationships instead of actual access patterns.
3.  Duplicating current fields without defining how they are updated—or whether they are historical snapshots.
4.  Assuming references enforce foreign keys automatically.
5.  Creating indexes for every field without considering write cost, storage, and memory.
6.  Applying ESR mechanically without checking selectivity, query shape, sort, and execution plan.
7.  Claiming `IXSCAN` always means the query is fast or optimal.
8.  Using `$lookup` as a universal replacement for data modelling.
9.  Forgetting `$unwind` multiplies documents and can change counts.
10. Sorting or limiting before grouping when the requirement is top-N groups.
11. Treating `$merge` as if it deletes stale target keys that disappear from source results.
12. Using TTL as an exact scheduler or authorization check.
13. Confusing read preference with read concern or write concern.
14. Assuming a write-concern timeout proves that a write did not commit.
15. Assuming a successful primary election means all secondaries are immediately caught up.
16. Choosing a monotonically increasing shard key without evaluating write hotspots.
17. Treating application type hints as runtime validation.
18. Reporting benchmark numbers or explain plans that were not actually observed.

## 18. Practice questions

1.  What are BSON documents, and why does MongoDB use BSON rather than plain JSON internally?
2.  What is `_id` used for, and when should you create a unique business-key index?
3.  When would you embed order lines, and when would you reference them?
4.  Why should an order preserve unit price at purchase instead of always looking up the product’s current price?
5.  What is the difference between a missing field and a field set to `null`?
6.  When does `$elemMatch` matter for arrays of embedded documents?
7.  Why can large `skip()` offsets be expensive?
8.  Explain the six modelling patterns in this lesson and give one use case for each.
9.  What does the ESR rule suggest, and when might ERS be worth testing?
10. What does `totalDocsExamined` tell you? Why is it not a complete latency metric?
11. How does a multikey index differ from an ordinary single-value index?
12. Why is TTL cleanup not exact to the second?
13. Explain the difference between `$lookup` and embedding.
14. What does `$unwind` do to document counts?
15. Why does a top-N aggregation group before sorting and limiting?
16. What conditions must be met for `$merge` with a custom `on` key?
17. Distinguish MongoDB read preference, read concern, and write concern.
18. Why can transactions cost more than a single-document update?
19. What makes a shard key prone to hotspots?
20. Why should a data engineer understand MongoDB schema drift before building a CDC pipeline?

## 19. Roadmap checkpoint

You are ready to proceed when you can:

- [ ] Decide whether to embed or reference a relationship and defend the choice.
- [ ] Design a compound index using the ESR rule and explain its limitations.
- [ ] Write a multi-stage aggregation pipeline.
- [ ] Explain read and write concerns.
- [ ] Explain how to choose a shard key.

Additional evidence for this lesson: - \[ \] Perform CRUD operations and query nested arrays safely. - \[ \] Explain the 16 MiB document limit and prevent unbounded arrays. - \[ \] Use `$match`, `$project`, `$group`, `$sort`, `$unwind`, `$lookup`, `$facet`, `$bucket`, `$merge`, and `$out`. - \[ \] Compare the embedded and referenced e-commerce models using five queries each. - \[ \] Convert SQL group-by, join, and top-N patterns into pipelines. - \[ \] Load 500,000 synthetic orders, capture actual explain plans before and after indexing, and report only observed results. - \[ \] Demonstrate validator rejection, TTL expiry, and partial-index eligibility. - \[ \] Observe primary election in a replica set and record actual behavior. - \[ \] Explain aggregation performance, memory constraints, and the Atlas Search/Vector Search/time-series awareness topics.

## 20. Final self-assessment

Score each skill from 0 to 2: **0** = cannot explain; **1** = can do with notes; **2** = can explain and defend trade-offs.

| Skill                                                                             | Score (0–2) |
|-----------------------------------------------------------------------------------|------------:|
| BSON, documents, `_id`, and CRUD                                                  |             |
| Query operators, arrays, projection, sort, pagination                             |             |
| Embedding versus referencing and 16 MiB limit                                     |             |
| Bucket, subset, computed, extended-reference, polymorphic, schema versioning      |             |
| Single-field, compound, multikey, text, TTL, partial indexes                      |             |
| ESR design and real `explain()` interpretation                                    |             |
| Aggregation stages and SQL-to-pipeline conversions                                |             |
| Daily revenue materialization and `$merge` caveats                                |             |
| JSON Schema validation and typed PyMongo access                                   |             |
| Replica sets, elections, read preference/concern, write concern                   |             |
| Transactions, sharding, shard-key choice, hot shards                              |             |
| Aggregation performance, memory, Atlas Search/Vector Search/time-series awareness |             |
| Completed labs with honest, reproducible evidence                                 |             |
| **Total (maximum 26)**                                                            |             |

Suggested interpretation: - **0–13:** revisit BSON, CRUD, and embed/reference examples. - **14–20:** core skills are developing; repeat the index and aggregation labs. - **21–26:** ready for Topic 04 if you can explain the assumptions and operational trade-offs, not merely reproduce syntax.

## 21. Official documentation references

Use the manual for the exact server version deployed in the lab; some behavior and managed Atlas capabilities change between releases.

- [BSON types and documents](https://www.mongodb.com/docs/manual/reference/bson-types/)
- [Embedded data and references](https://www.mongodb.com/docs/manual/data-modeling/)
- [Indexes and compound-index field order](https://www.mongodb.com/docs/manual/indexes/)
- [Query optimization and `explain()`](https://www.mongodb.com/docs/manual/tutorial/analyze-query-plan/)
- [Aggregation pipeline](https://www.mongodb.com/docs/manual/core/aggregation-pipeline/)
- [`$facet` memory and result limits](https://www.mongodb.com/docs/manual/reference/operator/aggregation/facet/)
- [`$merge` semantics and unique-index requirements](https://www.mongodb.com/docs/manual/reference/operator/aggregation/merge/)
- [`$out` semantics](https://www.mongodb.com/docs/manual/reference/operator/aggregation/out/)
- [Partial indexes and query coverage](https://www.mongodb.com/docs/manual/core/index-partial/)
- [TTL indexes](https://www.mongodb.com/docs/manual/core/index-ttl/)
- [JSON Schema validation](https://www.mongodb.com/docs/manual/core/schema-validation/specify-json-schema/)
- [Replica-set elections](https://www.mongodb.com/docs/manual/core/replica-set-elections/)
- [Read concern](https://www.mongodb.com/docs/manual/reference/read-concern/), [write concern](https://www.mongodb.com/docs/manual/reference/write-concern/), and [read preference](https://www.mongodb.com/docs/manual/core/read-preference/)
- [Transactions](https://www.mongodb.com/docs/manual/core/transactions/)
- [Sharding](https://www.mongodb.com/docs/manual/sharding/)
- [PyMongo documentation](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/)
- [Atlas Search](https://www.mongodb.com/docs/atlas/atlas-search/), [Atlas Vector Search](https://www.mongodb.com/docs/atlas/atlas-vector-search/), and [time-series collections](https://www.mongodb.com/docs/manual/core/timeseries-collections/)

## Summary

MongoDB’s document model is most effective when the schema reflects the application’s access patterns. Embedding makes bounded, related data easy to retrieve and update atomically in one document; referencing helps with independently managed or unbounded data but adds join/read complexity. Indexes reduce work for particular query shapes while adding storage and write costs. The ESR rule is a starting heuristic, not a replacement for `explain()` and measured evidence.

Aggregation pipelines turn nested operational data into analytical results, but `$unwind`, `$group`, joins, sorts, and materialization have cardinality, memory, and correctness implications. Validators and typed PyMongo access reduce schema drift; replica-set concerns, elections, transactions, and shard-key design determine how the application behaves under scale and failure. For a data engineer, these details also determine whether incremental extraction and downstream lakehouse reconciliation can be trusted.

**Next lesson:** `04-cassandra-wide-column-partitioning-and-tombstones.md`.
