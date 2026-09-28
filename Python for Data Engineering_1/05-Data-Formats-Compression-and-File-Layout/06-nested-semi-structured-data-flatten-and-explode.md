# Nested, Semi-Structured Data — Flatten and Explode

> **Module:** Stage 2 → Python for Data Engineering → Module 2.5 — Data Formats, Compression, and File Layout  
> **Phase:** C — Other Formats and Data Shapes  
> **Topic:** 06 — Nested, Semi-Structured Data: Flatten and Explode
>
> **Central engineering question:**  
> **What is the grain of my data before the transformation, what is the grain after the transformation, and what business meaning changes when nested data is flattened or exploded?**

---

## Learning Objectives

By the end of this topic, you should be able to:

- explain structured and semi-structured data
- identify nested objects/structs, arrays/lists, and maps
- draw a nested JSON tree
- identify parent-child relationships
- define and track table grain
- flatten nested structs without unintentionally changing row count
- explode arrays into rows while explicitly accounting for the grain change
- use pandas `pd.json_normalize`, `record_path`, `meta`, `sep`, and `explode`
- use Polars `unnest`, `explode`, and the `struct` and `list` namespaces
- use DuckDB `UNNEST`, struct access, and list functions
- use PyArrow `Table.flatten()` and relevant `pyarrow.compute` list/struct functions
- split nested documents into related tables with stable parent/child keys
- distinguish null collections from empty collections
- prevent parent-level double counting after child explosion
- detect accidental cross-products when multiple arrays are flattened
- decide when to keep data nested and when to produce flat/normalized Parquet
- handle heterogeneous JSON, changing field types, optional fields, and sparse keys
- preserve raw JSON when the source is too dynamic for a complete typed model
- understand JSON/semi-structured columns and Variant-style types at an awareness level
- reason about deeply nested and recursive structures
- build tests that prove grain and relationship correctness
- explain nested-data modeling decisions in production architecture reviews

---

## Prerequisites

This topic assumes you have already completed:

- Topic 01 — Row-Oriented vs Columnar Storage
- Topic 02 — Parquet Internals
- Topic 03 — Reading/Writing Parquet with PyArrow
- Topic 04 — Avro
- Topic 05 — ORC and Format Selection

You should also know the basics of:

- JSON
- DataFrames
- columns
- schemas
- Parquet
- Arrow
- pandas
- Polars
- DuckDB

Earlier topics established how row/column layout affects physical I/O, how Parquet stores nested data, how PyArrow represents schemas, and how analytical engines read columnar files. This topic does **not** re-teach those subjects. Instead, it answers a different question:

> **How do I transform nested source data into analytical shapes without changing its business meaning?**

A useful connection to previous topics is:

```text
Row-oriented
    ↓
Record-at-a-time processing
    ↓
Nested application/event payload
    ↓
Typed transformation
    ↓
Nested or normalized analytical representation
```

---

# 1. Why Nested Data Exists

Nested data is not an exotic problem. It is often the most natural representation of a real-world event.

Consider an order returned by an API:

```json
{
  "order_id": 1001,
  "customer": {
    "id": "C001",
    "name": "Alice",
    "address": {
      "city": "Kolkata",
      "country": "IN"
    }
  },
  "items": [
    {
      "sku": "A100",
      "qty": 2
    },
    {
      "sku": "B200",
      "qty": 1
    }
  ]
}
```

This shape is natural for:

- APIs
- webhooks
- application events
- event streams
- document databases
- application-to-application communication

The application thinks in terms of one **order object** containing other related objects.

An analytical system may instead want:

```text
orders
order_lines
```

because analysts frequently need queries such as:

```sql
SELECT sku, SUM(qty)
FROM order_lines
GROUP BY sku;
```

The challenge is not merely "how to flatten JSON."

The challenge is:

> **How do we reshape the data while preserving its business meaning?**

---

# 2. Structured vs Semi-Structured Data

## 2.1 Structured Data

Structured data has a predefined tabular shape:

```text
order_id | customer_id | amount
---------+-------------+-------
1001     | C001        | 180.00
1002     | C002        | 95.00
```

The schema is explicit:

```text
order_id     → integer/string
customer_id  → string
amount       → decimal/numeric
```

Structured data is convenient for:

- SQL
- relational modeling
- BI tools
- predictable transformations
- strict contracts

## 2.2 Semi-Structured Data

Semi-structured data has structure, but that structure may be nested, optional, or evolving.

For example:

```json
{
  "customer": {
    "id": "C001"
  },
  "items": [
    {"sku": "A", "qty": 2},
    {"sku": "B", "qty": 1}
  ],
  "metadata": {
    "campaign": "summer"
  }
}
```

It is **not correct** to say semi-structured means "no schema."

A semi-structured source can have:

- an implicit schema
- an evolving schema
- optional fields
- nested types
- dynamic keys
- producer-specific conventions

The schema may simply be less rigid than a classic relational table.

### Trade-off

| Property | Structured | Semi-structured |
| --- | --- | --- |
| Shape | predictable | flexible/nested |
| Schema | usually explicit | may be implicit/evolving |
| Relationships | usually explicit keys/rows | often represented by nesting |
| Querying | straightforward | may require unnesting/reshaping |
| Ingestion | stricter | often easier at the boundary |
| Evolution | controlled | can drift |

---

# 3. Understanding JSON Trees

Before you call `explode`, `unnest`, or `json_normalize`, draw the source as a tree.

For a realistic order:

```text
Order
├── order_id
├── customer
│   ├── id
│   ├── name
│   └── address
│       ├── city
│       └── country
├── items[]
│   ├── sku
   ├── qty
│   └── discounts[]
│       ├── code
│       └── amount
├── payment
└── metadata{}
```

This immediately tells you the data contains several different shapes.

### Scalar

A single value:

```text
order_id = 1001
```

### Struct / object

Named fields grouped together:

```text
customer
├── id
└── name
```

### List / array

Zero or more ordered elements:

```text
items[]
├── item 1
├── item 2
└── ...
```

### Map

Dynamic key/value entries:

```text
metadata{}
├── campaign
├── browser
└── feature_flag
```

---

## Stop and Think

Look at this JSON:

```json
{
  "order_id": 42,
  "customer": {
    "name": "Maya",
    "address": {
      "city": "Kolkata"
    }
  },
  "items": [
    {"sku": "A", "qty": 2}
  ]
}
```

Classify each field:

- `order_id`
- `customer`
- `customer.name`
- `customer.address`
- `items`
- `items[0].sku`

### Answer

```text
order_id              → scalar
customer              → struct/object
customer.name         → scalar inside a struct
customer.address      → nested struct
items                 → list/array
items[0].sku          → scalar inside a list element
```

The important part is not memorizing these names. It is being able to look at a payload and identify the shape before you transform it.

---

# 4. Structs, Arrays, and Maps

## 4.1 Structs

A struct/object groups related named fields.

```json
"customer": {
  "id": "C001",
  "name": "Alice",
  "address": {
    "city": "Kolkata",
    "country": "IN"
  }
}
```

Conceptually:

```text
customer
├── id
├── name
└── address
    ├── city
    └── country
```

Flattening a struct can become:

```text
customer_id
customer_name
customer_address_city
customer_address_country
```

A struct-to-column transformation does not inherently change row count.

If:

```text
Before:
1 row = 1 order
```

then after flattening:

```text
After:
1 row = 1 order
```

The shape changes. The grain usually does not.

---

## 4.2 Arrays / Lists

A list holds zero, one, or many elements.

```json
"items": [
  {"sku": "A", "qty": 2},
  {"sku": "B", "qty": 1}
]
```

The key phrase is **many elements**.

That "many" is why exploding a list changes row cardinality.

Before:

```text
1 row = 1 order
```

After exploding `items`:

```text
1 row = 1 order line/item
```

This is a modeling change, not just a DataFrame operation.

---

## 4.3 Maps

A map represents key/value data where the keys are not necessarily fixed schema columns.

```json
"metadata": {
  "campaign": "summer",
  "browser": "chrome",
  "feature_flag": "v2"
}
```

Maps are useful when:

- keys are dynamic
- the source evolves frequently
- only some records have a given key
- the set of keys is too large or unstable to justify columns

However, flattening every map key can create a very wide sparse table.

---

# 5. The Most Important Concept: Table Grain

## 5.1 Definition

> **Grain = what one row represents.**

This is the single most important mental model in this topic.

Examples:

```text
orders
→ one row = one order

order_lines
→ one row = one order line

payments
→ one row = one payment

discounts
→ one row = one discount
```

A nested source can encode several grains inside a single document.

For example:

```text
1 order
  ├── 2 order lines
  │    ├── 2 discounts
  │    └── 1 discount
```

The source document contains:

```text
order grain
line grain
discount grain
```

Your job is to decide which grain belongs in which analytical table.

---

## 5.2 The Grain Rule

Memorize this:

> **Before every flatten or explode operation, write down the grain. After every operation, write down the new grain.**

Use this template:

```text
Before transformation:
1 row = ______________________

Operation:
_______________________________

After transformation:
1 row = ______________________
```

For a list explosion:

```text
Before:
1 row = one order

Operation:
explode(items)

After:
1 row = one order line
```

---

## 5.3 Why Grain Matters

Suppose one order has:

```text
order_total = 100
```

and two line items.

After exploding items, you may have:

```text
order_id | sku | order_total
---------+-----+------------
O1       | A   | 100
O1       | B   | 100
```

The value `100` is still an **order-level measure**, but the rows now have **line-level grain**.

That mismatch is a major source of analytical bugs.

---

# 6. Parent-Child Relationships

A nested structure often represents relationships that would be explicit in normalized relational tables.

```text
orders
    │
    └── order_lines
            │
            └── discounts
```

A production design usually needs stable keys.

Example:

```text
orders:
order_id

order_lines:
order_line_id
order_id

discounts:
discount_id
order_line_id
order_id
```

The relationships are:

```text
orders.order_id
      │
      └── order_lines.order_id

order_lines.order_line_id
      │
      └── discounts.order_line_id
```

This is a one-to-many-to-many shape:

```text
one order
    ↓
many lines
    ↓
many discounts per line
```

### Why preserve keys?

Because once the nested document is split into multiple tables, the original hierarchy is no longer visible from row position alone.

Keys preserve identity.

---

# 7. Flattening Structs

## 7.1 What Is Flattening?

> **Flattening converts nested struct/object fields into columns without necessarily changing row count.**

Example:

```text
customer.address.city
            ↓
customer_address_city
```

Before:

```text
1 row = one order
```

After flattening:

```text
1 row = one order
```

The row shape changed, but the business entity represented by the row did not.

---

## 7.2 Example

Input:

```json
{
  "order_id": 1001,
  "customer": {
    "name": "Alice",
    "address": {
      "city": "Kolkata",
      "country": "IN"
    }
  }
}
```

Conceptual flat result:

| order_id | customer_name | customer_address_city | customer_address_country |
| ---: | --- | --- | --- |
| 1001 | Alice | Kolkata | IN |

No new order was created.

---

## 7.3 When Flattening Is Useful

Flattening can help when:

- downstream SQL is simpler with scalar columns
- BI tools have limited nested-type support
- a nested field is queried frequently
- the nested structure is stable
- the resulting schema remains manageable

Flattening can be harmful when:

- the source contains thousands of sparse fields
- nested structure is highly dynamic
- you destroy useful hierarchy
- field names become ambiguous
- schema evolution becomes difficult

---

# 8. Exploding Arrays

## 8.1 What Is Exploding?

> **Exploding turns each element of a list/array into a separate row.**

Suppose:

```text
order O1
items = [A, B, C]
```

Before:

```text
1 row = 1 order
```

After:

```text
O1 | A
O1 | B
O1 | C
```

Now:

```text
1 row = 1 item/order line
```

---

## 8.2 Explode Is a Grain Change

Do not think:

```text
explode(items)
```

means "make the JSON easier to read."

Think:

```text
explode(items)
=
change row cardinality
=
change table grain
```

That mindset prevents a large class of production errors.

---

## Stop and Think

If:

```text
orders = 10,000 rows
```

and every order contains exactly 3 line items, what is the expected number of line-level rows after a correct explode?

### Answer

Conceptually:

```text
10,000 orders × 3 lines/order = 30,000 order-line rows
```

The real number depends on the actual list lengths. The point is that row count is now driven by the child collection.

---

# 9. Flatten vs Explode

This comparison should be part of your permanent mental model.

| Operation | Input | Output | Grain changes? |
| --- | --- | --- | --- |
| Flatten struct | object/struct | columns | Usually no |
| Explode list | array/list | rows | Yes |
| Normalize child array | nested records | child table | Yes |
| Extract scalar nested field | struct field | scalar column | No |

A useful shorthand:

```text
STRUCT → columns
LIST   → rows
MAP    → key/value structure
```

That is not a substitute for understanding the data model, but it is a useful first mental check.

---

# 10. pandas `json_normalize`

`pandas.json_normalize` transforms semi-structured JSON-like records into a DataFrame. Its `record_path`, `meta`, and `sep` parameters are particularly useful when nested data contains repeated child records. The current pandas documentation describes `record_path` as the path to the list of records and `meta` as fields carried into the resulting records. citeturn296478search0

## 10.1 Simple Struct Flattening

```python
import pandas as pd

data = [
    {
        "order_id": 1,
        "customer": {
            "name": "Alice",
            "city": "Kolkata",
        },
    },
    {
        "order_id": 2,
        "customer": {
            "name": "Bob",
            "city": "London",
        },
    },
]

df = pd.json_normalize(data, sep="_")

print(df)
```

Conceptual result:

```text
   order_id customer_name customer_city
0         1         Alice       Kolkata
1         2           Bob        London
```

The important modeling point is:

```text
Before:
1 row = one order

After:
1 row = one order
```

The customer struct was flattened. The order grain did not change.

---

## 10.2 Why `sep` Matters

Without deliberate naming, nested paths may produce names such as:

```text
customer.address.city
```

You may prefer:

```python
df = pd.json_normalize(data, sep="_")
```

which creates:

```text
customer_address_city
```

The separator is not just cosmetic.

A production naming convention should avoid:

- ambiguous names
- collisions
- names that conflict with SQL conventions
- names that are difficult to document

---

# 11. `record_path`

Now consider a list of order items.

```python
data = [
    {
        "order_id": "O1001",
        "customer": {"name": "Alice"},
        "items": [
            {"line_id": "L1", "sku": "A100", "qty": 2},
            {"line_id": "L2", "sku": "B200", "qty": 1},
        ],
    },
    {
        "order_id": "O1002",
        "customer": {"name": "Bob"},
        "items": [
            {"line_id": "L3", "sku": "C300", "qty": 4},
        ],
    },
]
```

Use:

```python
lines = pd.json_normalize(
    data,
    record_path="items",
    meta=["order_id"],
)

print(lines)
```

The important semantics are:

```text
record_path="items"
→ identify repeated child records

meta=["order_id"]
→ carry parent identity into each child row
```

The grain changes:

```text
Before:
1 row = one order

After:
1 row = one order line
```

---

## 11.1 Why `meta` Matters

Suppose the result contains:

```text
line_id | sku | qty
```

Without `order_id`, you may know the line itself but not which order it belongs to.

With:

```python
meta=["order_id"]
```

the child table can contain:

```text
order_id | line_id | sku | qty
```

That gives you:

```text
orders.order_id
    ↓
order_lines.order_id
```

The key is more important than blindly copying every parent attribute.

---

## 11.2 Nested Metadata Paths

For deeper structures, metadata paths can be represented as path lists. For example:

```python
lines = pd.json_normalize(
    data,
    record_path=["items"],
    meta=[
        "order_id",
        ["customer", "name"],
    ],
    sep="_",
)
```

Keep the parent key first and add other parent fields only when they serve the target table's business purpose.

---

# 12. pandas `explode`

Suppose a DataFrame contains a list column:

```python
import pandas as pd

df = pd.DataFrame(
    {
        "order_id": ["O1", "O2"],
        "items": [
            [{"sku": "A", "qty": 2}, {"sku": "B", "qty": 1}],
            [{"sku": "C", "qty": 4}],
        ],
    }
)

exploded = df.explode("items", ignore_index=True)

print(exploded)
```

Conceptually:

```text
O1 | {"sku": "A", "qty": 2}
O1 | {"sku": "B", "qty": 1}
O2 | {"sku": "C", "qty": 4}
```

The parent columns repeat.

The new grain is:

```text
1 row = one item
```

Often you then normalize the item structs:

```python
items = pd.json_normalize(exploded["items"])

lines = pd.concat(
    [
        exploded[["order_id"]].reset_index(drop=True),
        items.reset_index(drop=True),
    ],
    axis=1,
)
```

The operation is deliberately two-stage:

```text
list
 ↓
explode
 ↓
one item per row
 ↓
normalize item fields
 ↓
scalar child columns
```

---

# 13. Empty Arrays and Null Arrays

This is a production-critical distinction.

## 13.1 Empty Array

```json
"items": []
```

Usually means:

> The collection exists, but there are currently zero items.

## 13.2 Null

```json
"items": null
```

Usually means:

> The collection itself is absent, unknown, or null according to the source semantics.

Do not assume every source system assigns exactly the same business meaning.

The difference may affect:

- counts
- joins
- completeness metrics
- downstream business rules
- child-table row counts

### Required design question

Ask:

> "Do I need an output row for a parent with zero children?"

Often the answer is:

```text
orders table → yes
order_lines table → no child row
```

That is different from forcing a fabricated placeholder line.

---

## 13.3 Tool Semantics Are Not Identical

Pandas, Polars, DuckDB, and PyArrow do not have identical nested-data APIs or identical null/empty-list behavior.

Therefore, for production transformations:

```text
Do not assume
   ↓
Test the actual library/version
   ↓
Document the chosen semantics
```

Current DuckDB documentation states that `unnest(NULL)` and `unnest([])` produce zero rows, while Polars exposes explicit `empty_as_null` and `keep_nulls` controls on list explosion expressions. citeturn722838search0turn774852search5

Pandas also needs to be tested against the actual transformation path, especially when empty lists, nulls, and nested records are mixed.

---

# 14. Polars `unnest`

Polars provides struct-oriented operations for turning a struct into its individual fields. Its current expression API includes `Expr.struct.unnest()`, which expands a struct into its member fields. citeturn296478search3

Example:

```python
import polars as pl

df = pl.DataFrame(
    {
        "order_id": ["O1", "O2"],
        "customer": [
            {"name": "Alice", "city": "Kolkata"},
            {"name": "Bob", "city": "London"},
        ],
    }
)

result = df.unnest("customer")

print(result)
```

Conceptual shape:

```text
order_id | name  | city
---------+-------+--------
O1       | Alice | Kolkata
O2       | Bob   | London
```

Grain:

```text
Before:
1 row = one order

After:
1 row = one order
```

---

## 14.1 Expression Form

You can also work at the expression level:

```python
result = df.select(
    pl.col("order_id"),
    pl.col("customer").struct.unnest(),
)
```

Use expression syntax when you want explicit control over what enters the output projection.

---

# 15. Polars `explode`

Polars supports exploding list columns into separate rows. The current DataFrame API supports `DataFrame.explode`, and the expression API also provides `Expr.explode`. citeturn774852search10turn774852search19

Example:

```python
import polars as pl

df = pl.DataFrame(
    {
        "order_id": ["O1", "O2"],
        "items": [
            [{"sku": "A", "qty": 2}, {"sku": "B", "qty": 1}],
            [{"sku": "C", "qty": 4}],
        ],
    }
)

result = df.explode("items")

print(result)
```

The conceptual result is:

```text
O1 | {A, 2}
O1 | {B, 1}
O2 | {C, 4}
```

Then:

```python
lines = result.unnest("items")
```

or use struct expressions where you need more targeted extraction.

Again:

```text
explode → list becomes rows
unnest  → struct becomes columns
```

---

# 16. Polars Struct Namespace

The `struct` namespace is useful when a column contains structured values.

A common pattern is:

```python
result = df.select(
    pl.col("customer").struct.field("name").alias("customer_name"),
    pl.col("customer").struct.field("city").alias("customer_city"),
)
```

This lets you extract only the fields you need instead of expanding every field.

When the complete struct is wanted:

```python
result = df.select(
    pl.col("customer").struct.unnest()
)
```

The current Polars documentation describes `struct.unnest()` as an alias for expanding all struct fields. citeturn296478search3

### Engineering reason

Use targeted extraction when:

- only a few nested fields are important
- the source struct is wide
- you want a stable output schema

Use full unnesting when:

- the struct is well-defined
- downstream consumers need most fields
- schema growth is controlled

---

# 17. Polars List Namespace

Polars also provides a `list` namespace for list-aware transformations.

Useful operations include:

- list length
- list element access
- list transformation
- list filtering
- list explosion

Examples:

```python
df.select(
    pl.col("items").list.len().alias("item_count")
)
```

Extract an element:

```python
df.select(
    pl.col("items").list.get(0)
)
```

Transform list elements when appropriate:

```python
df.select(
    pl.col("numbers").list.eval(pl.element() * 2)
)
```

Explode:

```python
df.select(
    pl.col("items").list.explode()
)
```

The exact API surface evolves across Polars versions, so pin your project version and test production pipelines against the installed version.

---

# 18. DuckDB Nested Data

DuckDB has native `LIST`, `STRUCT`, `MAP`, `ARRAY`, and `UNION`-style nested types and provides `unnest` for `LIST` and `STRUCT` values. Its current documentation states that unnesting a list creates one row per element, while unnesting a struct emits its fields as columns. citeturn722838search0turn722838search6

This is particularly useful when the downstream audience prefers SQL.

---

# 19. DuckDB Struct Access

Suppose a table contains:

```text
customer STRUCT(...)
```

You can access nested fields with dot notation:

```sql
SELECT
    order_id,
    customer.name AS customer_name,
    customer.address.city AS customer_city
FROM orders;
```

DuckDB also supports `struct_extract` and bracket notation for struct entries. citeturn722838search2turn722838search3

The engineering meaning is the same:

```text
struct field
    ↓
scalar expression
    ↓
same row grain
```

---

# 20. DuckDB `UNNEST`

Suppose:

```text
items = [
  {sku: 'A', qty: 2},
  {sku: 'B', qty: 1}
]
```

A conceptual query is:

```sql
SELECT
    order_id,
    item
FROM orders,
UNNEST(items) AS t(item);
```

For a list of structs, you can then access:

```sql
SELECT
    order_id,
    item.sku,
    item.qty
FROM orders,
UNNEST(items) AS t(item);
```

DuckDB documents `unnest()` as a special function that changes result cardinality for lists and can also expand structs into columns. citeturn722838search0turn722838search2

Important:

```text
orders
1 row/order
   ↓
UNNEST(items)
   ↓
1 row/item
```

---

# 21. DuckDB List Functions

Useful DuckDB list operations include:

```sql
SELECT list_count(items)
FROM orders;
```

and list transformation functions such as `list_transform`, as supported by the current DuckDB release. citeturn722838search1

For example:

```sql
SELECT
    order_id,
    list_transform(items, lambda x: x.qty * 2) AS doubled_qty
FROM orders;
```

Use nested functions where the business task can be solved without exploding the list.

That can be important because:

```text
keep list
→ preserve row grain

explode list
→ increase row cardinality
```

---

# 22. Apache Arrow Nested Data

Arrow can represent nested values such as:

- structs
- lists
- maps

When the transformation only needs to flatten a struct, `Table.flatten()` is the direct Arrow concept. The current Arrow documentation states that `Table.flatten()` creates one column per struct field while leaving other columns unchanged. citeturn296478search1

Example:

```python
import pyarrow as pa

customer = pa.array(
    [
        {"name": "Alice", "city": "Kolkata"},
        {"name": "Bob", "city": "London"},
    ]
)

table = pa.Table.from_arrays(
    [pa.array(["O1", "O2"]), customer],
    names=["order_id", "customer"],
)

flat = table.flatten()

print(flat.schema)
```

Conceptually:

```text
customer: struct<name: string, city: string>
```

becomes:

```text
customer.name: string
customer.city: string
```

No list explosion has occurred.

---

## 22.1 `pyarrow.compute`

Arrow's compute layer includes nested-data functions such as:

- `list_value_length`
- `list_element`
- `list_flatten`
- `list_parent_indices`
- `struct_field`

The current Arrow documentation exposes these as structural transform functions. citeturn774852search3

Example:

```python
import pyarrow as pa
import pyarrow.compute as pc

items = pa.array(
    [
        [1, 2, 3],
        [4],
        None,
    ]
)

lengths = pc.list_value_length(items)
first_values = pc.list_element(items, 0)

print(lengths)
print(first_values)
```

The important distinction:

```text
list_value_length
→ derives a scalar from each parent row
→ row count stays the same

list_flatten
→ removes a list nesting level
→ output cardinality can increase
```

The current Arrow documentation states that `list_flatten` emits elements from the top list level and does not emit values for null list entries. citeturn774852search17

---

# 23. Flatten vs Explode: Production Rule

Use this decision:

```text
Is the nested value a STRUCT?
        │
        └── Usually think "columns"

Is the nested value a LIST?
        │
        └── Usually think "rows"
```

But do not confuse the shorthand with a complete modeling rule.

The real question is:

> **What business entity does the nested value represent?**

A list may be:

- a repeated business entity → child table is often sensible
- a small collection used only for a calculation → keeping it nested may be better
- a technical payload component → raw preservation may be sufficient

---

# 24. Normalizing One Document Into Related Tables

A nested order document can naturally become:

```text
orders
order_lines
discounts
payments
```

This is not "flattening everything."

It is **modeling each repeated entity at its own grain**.

---

# 25. Required Normalized Table Design

Consider:

```json
{
  "order_id": "O1001",
  "customer": {
    "id": "C001",
    "name": "Alice"
  },
  "items": [
    {
      "line_id": "L1",
      "sku": "A100",
      "qty": 2,
      "discounts": [
        {
          "discount_id": "D1",
          "amount": 5
        }
      ]
    }
  ],
  "payment": {
    "payment_id": "P1",
    "method": "card"
  }
}
```

A reasonable relational decomposition is:

### `orders`

```text
order_id
customer_id
customer_name
```

Grain:

```text
1 row = 1 order
```

### `order_lines`

```text
line_id
order_id
sku
qty
```

Grain:

```text
1 row = 1 order line
```

### `discounts`

```text
discount_id
line_id
order_id
amount
```

Grain:

```text
1 row = 1 discount
```

### `payments`

```text
payment_id
order_id
method
```

Grain:

```text
1 row = 1 payment
```

Keys preserve the hierarchy:

```text
orders.order_id
       ↓
order_lines.order_id
       ↓
discounts.order_id / order_lines.line_id
```

---

# 26. The Normalization Rule

A useful production heuristic is:

> **When repeated nested entities have their own meaningful grain, consider extracting them into their own related table.**

Do not interpret this as a mandatory normalization law.

There are trade-offs.

### More tables can mean

- clearer grain
- fewer repeated parent measures
- simpler correctness reasoning
- additional joins

### Keeping nested data can mean

- fewer joins
- closer source fidelity
- easier single-document retrieval
- more complex nested query syntax

Choose based on downstream workload.

---

# 27. Nulls vs Empty Collections

Use explicit semantics.

| Source value | Typical interpretation | Child rows naturally produced? |
| --- | --- | ---: |
| `items=[]` | collection exists, zero children | 0 |
| `items=null` | collection absent/unknown/null | 0 in many explode/unnest operations, but test |
| `items=[...]` | children exist | number of elements |

The critical point is that **zero child rows does not necessarily mean the parent should disappear**.

For example:

```text
orders table
→ keep all valid orders

order_lines table
→ only actual line items
```

This is often the cleanest modeling boundary.

---

# 28. Preserving Parents With Empty Child Arrays

Suppose:

```json
{
  "order_id": "O3",
  "items": []
}
```

You probably still want:

```text
orders
O3
```

even though there are no rows in:

```text
order_lines
```

A safe architecture is:

```text
Parent table
→ built from parent records

Child table
→ built only from actual child elements
```

Do not derive the survival of the parent table from the result of an inner-style child explosion.

### Practical rule

> **Build the parent entity at parent grain first. Build child entities separately.**

This makes empty-child behavior much easier to reason about.

---

# 29. pandas Empty-Array Handling: Test, Don't Guess

Different transformation paths can produce different representations of empty lists and nulls.

Use a small test:

```python
import pandas as pd

df = pd.DataFrame(
    {
        "order_id": ["O1", "O2", "O3"],
        "items": [
            [{"sku": "A"}],
            [],
            None,
        ],
    }
)

result = df.explode("items", ignore_index=True)

print(result)
```

Your job is not to memorize one output from one library release.

Instead document:

```text
Library version:
________

Operation:
________

Empty-list behavior:
________

Null-list behavior:
________

Business policy:
________
```

That is production thinking.

---

# 30. Polars Empty/Null List Handling

Current Polars list-explosion APIs expose controls such as:

```python
empty_as_null=False
keep_nulls=True
```

These controls make the semantics more explicit than relying purely on default behavior. citeturn774852search5turn774852search10

Example:

```python
import polars as pl

df = pl.DataFrame(
    {
        "order_id": ["O1", "O2", "O3"],
        "items": [
            ["A", "B"],
            [],
            None,
        ],
    }
)

result = df.explode(
    "items",
    empty_as_null=False,
    keep_nulls=True,
)

print(result)
```

The correct production behavior still depends on your business requirement.

A library option cannot decide your business semantics for you.

---

# 31. DuckDB Empty/Null List Handling

DuckDB's current documentation explicitly states:

```sql
SELECT unnest([]);
```

and:

```sql
SELECT unnest(NULL);
```

produce no output rows. citeturn722838search0

That means a direct child `UNNEST` result does not preserve a parent row with zero children.

If you need parent preservation, design the query accordingly.

For example, conceptually:

```text
orders
    │
    ├── parent result → all orders
    │
    └── child result  → actual items only
```

Do not force a fake child record merely to preserve the parent.

---

# 32. Double Counting After Explode

This is one of the most important production failure modes.

Suppose:

```text
Order O1
order_total = 100
```

with lines:

```text
A = 60
B = 40
```

Before explode:

```text
order_id | order_total | items
---------+-------------+----------------
O1       | 100         | [A, B]
```

After explode:

```text
order_id | sku | line_amount | order_total
---------+-----+-------------+------------
O1       | A   | 60          | 100
O1       | B   | 40          | 100
```

Now:

```sql
SELECT SUM(order_total)
FROM order_lines;
```

produces:

```text
200
```

But the actual order total is:

```text
100
```

Why?

Because the measure:

```text
order_total
```

has **order grain**, while the table now has **line grain**.

The value was duplicated by the transformation.

---

# 33. The Grain Mismatch Rule

Memorize:

> **Never aggregate a measure at a different grain unless you have deliberately accounted for the grain change.**

This applies far beyond JSON.

It appears in:

- joins
- exploded arrays
- event modeling
- dimensional models
- nested arrays
- clickstream analysis

---

# 34. Correct Ways to Avoid Double Counting

There is no single fix for every query.

## Strategy 1 — Aggregate at Parent Grain

If the desired answer is order-level:

```sql
SELECT
    order_id,
    MAX(order_total) AS order_total
FROM order_lines
GROUP BY order_id;
```

This can be appropriate **only when `order_total` is truly constant per order and the business contract guarantees that**.

## Strategy 2 — Aggregate Children Separately

For example:

```sql
SELECT
    order_id,
    SUM(line_amount) AS lines_total
FROM order_lines
GROUP BY order_id;
```

Then join the aggregate to the parent table.

## Strategy 3 — Maintain Separate Facts by Grain

Keep:

```text
orders
order_lines
discounts
```

instead of forcing all measures into one wide table.

## Strategy 4 — Use Parent Keys Carefully

A `DISTINCT` on parent keys can help identify unique parents, but it does not magically fix duplicated measures.

### Dangerous shortcut

Do **not** blindly use:

```sql
SUM(DISTINCT order_total)
```

If two different orders both have:

```text
order_total = 100
```

the distinct sum treats them as one value and undercounts.

---

# 35. Two Independent Arrays: Cross Products

Consider:

```text
Order
├── items: [A, B]
└── promotions: [D1, D2]
```

If you independently explode both arrays as if they were connected, you can produce:

```text
A D1
A D2
B D1
B D2
```

That is:

```text
2 items × 2 promotions = 4 combinations
```

But the source may not say that every promotion applies to every item.

You have accidentally created a cross-product.

This can corrupt:

- counts
- sums
- revenue
- discounts
- event metrics

---

# 36. Safe Strategy for Multiple Arrays

If discounts belong to an individual line item, preserve the hierarchy:

```text
Order
   ↓
Extract items
   ↓
order_lines
   ↓
For each line, extract discounts
   ↓
discounts
```

Use:

```text
orders
    │
    └── order_lines
            │
            └── discounts
```

Do not flatten unrelated collections into the same row unless the source or business rules explicitly define the relationship.

---

# 37. Nested Parquet vs Flat Parquet

After modeling the data, you have another decision:

```text
Nested Parquet
```

or:

```text
Flat/normalized Parquet
```

---

## 37.1 Nested Parquet

Keep fields such as:

- structs
- lists
- maps

Example:

```text
orders
├── order_id
├── customer: STRUCT
├── items: LIST<STRUCT>
├── payment: STRUCT
└── metadata: ...
```

Potential advantages:

- source fidelity
- fewer normalization steps
- efficient retrieval of a whole nested document in compatible engines
- fewer joins for document-style access

Potential costs:

- more complex SQL
- consumer limitations
- more difficult BI access
- more complex schema evolution
- different nested semantics across tools

---

## 37.2 Flat Parquet

Produce:

```text
orders.parquet
order_lines.parquet
discounts.parquet
payments.parquet
```

Potential advantages:

- clear grains
- simpler SQL
- predictable relationships
- broad analytical compatibility

Potential costs:

- joins
- multiple datasets
- transformation overhead
- possible repeated parent attributes if modeling is poor

Neither design is universally better.

---

# 38. When to Keep Nested Types

Keeping nested data can be useful when:

- document fidelity matters
- the source is naturally nested
- downstream engines support the nested types well
- consumers retrieve whole objects
- exploding would cause huge row multiplication
- the nested collection is not independently queried often

Example:

```text
raw event
→ typed nested Parquet
```

can be a reasonable representation when consumers understand the structure.

---

# 39. When to Flatten

Flattening can be useful when:

- BI tools expect scalar columns
- analysts need frequent direct access
- the nested structure is stable
- only a few child levels exist
- traditional SQL is the dominant interface
- interoperability matters

Example:

```text
customer.address.city
```

might become:

```text
customer_address_city
```

because it is a frequently queried business attribute.

---

# 40. Schema Evolution Trade-offs

Nested and flat designs move complexity rather than eliminating it.

Possible nested changes:

```text
customer
├── id
├── name
└── loyalty_tier  ← new optional field
```

can be relatively localized.

But changing an array's element shape may affect:

- child processing
- downstream schemas
- existing queries
- validation rules

Flattening a dynamic object can create another kind of churn:

```text
metadata.key_1
metadata.key_2
metadata.key_3
...
metadata.key_2000
```

with only a small fraction populated per record.

The engineering question is:

> **Which kind of change is easier for our consumers and operating model to absorb?**

---

# 41. Heterogeneous JSON

JSON is flexible enough to contain different types in the same field.

Example:

```json
{"value": 10}
```

then:

```json
{"value": "ten"}
```

then:

```json
{}
```

Possible consequences:

- type inference conflicts
- coercion decisions
- nullability complications
- downstream schema instability

Do not silently assume:

```text
value = number
```

just because the first record says so.

---

# 42. Changing Field Types

Consider:

```text
record 1 → price = 10.5
record 2 → price = "10.5"
record 3 → price = null
```

A production ingestion pipeline must define a policy.

Possible policies include:

### Strict

Reject incompatible records.

```text
wrong type
   ↓
quarantine
```

### Controlled coercion

Convert only according to documented rules.

```text
"10.5"
   ↓
Decimal/float
```

### Raw preservation

Retain the original value when semantics are uncertain.

Do not silently coerce just because a library makes it possible.

---

# 43. Optional Fields

These are different states:

```json
{"name": "Alice"}
```

```json
{"name": "Alice", "phone": null}
```

```json
{"name": "Alice", "phone": ""}
```

They may mean:

```text
missing
null
present but empty
```

The correct downstream interpretation is a **data-contract decision**, not merely a parser default.

Document how your pipeline maps these states.

---

# 44. Sparse Keys

Suppose one record contains:

```json
{
  "metadata": {
    "browser": "Chrome",
    "campaign": "summer"
  }
}
```

and another:

```json
{
  "metadata": {
    "device": "mobile",
    "experiment": "A"
  }
}
```

Flattening the map can create:

```text
browser
campaign
device
experiment
```

with many nulls.

Over time, you may end up with:

```text
hundreds or thousands of columns
```

That can create:

- sparse tables
- schema churn
- hard-to-read SQL
- expensive transformations
- difficult contracts

---

# 45. Raw JSON Preservation

A very useful production pattern is:

```text
Typed columns
+
Raw JSON
```

For example:

```text
event_id
event_type
created_at
customer_id
metadata_raw_json
```

This does **not** mean raw JSON should replace typed modeling.

Instead, raw preservation gives you a fallback when:

- the source schema is not fully understood
- keys are dynamic
- future parsing requirements are unknown
- debugging requires the exact source payload
- a parser bug must be repaired and historical data replayed

Think:

```text
Source JSON
     ↓
bronze/raw preservation
     ↓
typed fields
     +
metadata_raw_json
```

---

# 46. When Raw JSON Is Especially Valuable

Use raw preservation when:

- metadata keys evolve quickly
- records are heterogeneous
- the parser is still stabilizing
- you need replayability
- source payloads are required for audits/debugging

Avoid the opposite extreme:

```text
"Everything is raw JSON forever."
```

That moves complexity into every downstream consumer.

The goal is:

```text
Typed where stable and valuable
+
Raw where dynamic and uncertain
```

---

# 47. Semi-Structured Columns and Variant Awareness

Modern analytical systems increasingly expose native ways to represent flexible nested values.

You may encounter:

- JSON columns
- semi-structured columns
- Variant-like types

The goal of a Variant-style type is broadly:

> Represent semi-structured values while preserving the ability to query inside them.

This can be useful when:

- schemas vary
- document shape matters
- not every attribute deserves a dedicated column
- consumers need flexible access

Treat this as awareness for this topic. Exact support and syntax vary by engine and version.

---

# 48. Variant Awareness Across Modern Ecosystems

You may encounter Variant-oriented representations in:

- Parquet ecosystems
- Spark
- Iceberg

Do not assume support is identical across versions.

When evaluating a Variant-style feature, ask:

```text
Can our writer create it?
Can our main engines read it?
Can BI tools access it?
Can our validation system understand it?
Can we evolve it safely?
```

The feature is only useful if the entire platform can operate around it.

---

# 49. Deeply Nested Data

Nested structures can become difficult very quickly.

Example:

```text
order
  ↓
items[]
  ↓
discounts[]
  ↓
rules[]
  ↓
conditions[]
```

Every additional level introduces more:

- transformation logic
- key management
- null behavior
- testing burden
- query complexity
- schema maintenance

A deeply nested source does not imply that a deeply nested analytical model is optimal.

---

# 50. Recursive Structures

Some data is recursive:

```text
folder
├── child folder
│   ├── child folder
│   └── ...
```

or:

```text
employee
└── manager
    └── manager
        └── ...
```

Naively flattening recursion can cause:

- output explosion
- recursion-depth problems
- cycles
- unpredictable schemas
- difficult SQL

For recursive data, prefer a model that makes hierarchy explicit, such as:

```text
node_id
parent_node_id
```

when the business problem supports it.

---

# 51. Limits of Flattening

Flattening everything is usually a mistake.

Potential symptoms:

```text
nested source
    ↓
flatten all levels
    ↓
1,000+ columns
    ↓
mostly NULL
    ↓
unstable schema
```

A better principle:

> **Flatten only what downstream workloads actually need.**

Keep some nested fields nested when they are:

- rarely accessed
- highly dynamic
- document-like
- costly to flatten
- not useful as independent analytical dimensions

---

# 52. Required Real-API / JSON Tree Exercise

Choose a public API such as:

- GitHub
- a weather API
- another API with nested JSON

The source must produce realistic nested content.

### Exercise

1. Retrieve one representative JSON response.
2. Save the response locally for the exercise.
3. Draw its tree.
4. Mark every scalar.
5. Mark every struct/object.
6. Mark every list/array.
7. Mark every map/dynamic object.
8. Identify parent-child relationships.
9. Decide which fields remain nested.
10. Design target tables.
11. Write the grain of each table.
12. Identify the keys needed to preserve relationships.

Use this worksheet:

```text
Source:
________________________

Parent entity:
________________________

Child entity:
________________________

Repeated collection:
________________________

Target tables:
________________________

Nested fields to keep:
________________________

Fields to flatten:
________________________

Raw fields to preserve:
________________________
```

### Worked Example

For the order JSON from the opening:

```text
Order
├── order_id
├── customer
│   ├── id
│   ├── name
│   └── address
│       ├── city
│       └── country
├── items[]
│   ├── sku
│   ├── qty
│   └── discounts[]
│       ├── code
│       └── amount
├── payment
└── metadata{}
```

A reasonable first model is:

```text
orders
→ one row/order

order_lines
→ one row/order line

discounts
→ one row/discount

payments
→ one row/payment
```

And:

```text
customer.id
customer.name
customer.address.city
customer.address.country
```

can be flattened into `orders` if those attributes are stable and commonly queried.

Dynamic `metadata` can remain a raw JSON string or a structured map depending on consumer support and schema stability.

---

# 53. Required Hands-On Lab — `nested_orders.py`

> **Important file-safety rule:** This module documents the complete implementation of `nested_orders.py`, but this learning workspace task must not create that file. Save the code below as a learner-created file when performing the exercise yourself.

The lab uses JSON Lines containing:

- customer struct
- array of line items
- discounts inside each line item
- optional payment struct
- free-form metadata object

The lab must cover:

- orders
- order_lines
- discounts
- payments awareness
- double counting
- empty arrays
- raw metadata preservation
- validation

---

# 54. Lab Part 1 — Input Data

Use this small but rich JSON Lines dataset.

```jsonl
{"order_id":"O1001","customer":{"id":"C001","name":"Alice","address":{"city":"Kolkata","country":"IN"}},"items":[{"line_id":"L1001-1","sku":"A100","qty":2,"unit_price":50.0,"discounts":[{"discount_id":"D1","code":"SUMMER","amount":5.0},{"discount_id":"D2","code":"LOYALTY","amount":2.0}]},{"line_id":"L1001-2","sku":"B200","qty":1,"unit_price":90.0,"discounts":[{"discount_id":"D3","code":"PROMO","amount":10.0}]}],"payment":{"payment_id":"P1001","method":"card"},"metadata":{"campaign":"summer","browser":"Chrome"},"order_total":183.0}
{"order_id":"O1002","customer":{"id":"C002","name":"Bob","address":{"city":"London","country":"GB"}},"items":[{"line_id":"L1002-1","sku":"C300","qty":4,"unit_price":20.0,"discounts":[]}],"payment":null,"metadata":{"device":"mobile"},"order_total":80.0}
{"order_id":"O1003","customer":{"id":"C003","name":"Carol","address":{"city":"Delhi","country":"IN"}},"items":[],"payment":{"payment_id":"P1003","method":"upi"},"metadata":{"experiment":"A"},"order_total":0.0}
{"order_id":"O1004","customer":{"id":"C004","name":"David","address":{"city":"Mumbai","country":"IN"}},"items":[{"line_id":"L1004-1","sku":"D400","qty":1,"unit_price":120.0,"discounts":[{"discount_id":"D4","code":"WELCOME","amount":20.0}]}],"payment":{"payment_id":"P1004","method":"card"},"metadata":{"campaign":"new_user","feature_flag":"v2"},"order_total":100.0}
```

This sample intentionally contains:

- multiple lines
- one line
- an empty line array
- null payment
- multiple discounts
- an empty discount array
- dynamic metadata keys

---

# 55. Lab Part 2 — Parent Table With pandas

Start by loading the JSON objects:

```python
import json
from pathlib import Path

import pandas as pd

records = [
    json.loads(line)
    for line in Path("orders.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
```

Create the parent table separately:

```python
orders = pd.json_normalize(
    records,
    sep="_",
)

orders = orders[
    [
        "order_id",
        "customer_id",
        "customer_name",
        "customer_address_city",
        "customer_address_country",
        "payment_payment_id",
        "payment_method",
        "order_total",
        "metadata",
    ]
].copy()

orders["metadata_raw_json"] = orders["metadata"].map(
    lambda value: json.dumps(value, sort_keys=True)
)

orders = orders.drop(columns=["metadata"])
```

Conceptual grain:

```text
orders
→ one row per order
```

### Important observation

Do not create `orders` by first exploding `items`.

The parent table should be independent of child cardinality.

---

# 56. Lab Part 3 — `order_lines` With pandas

Use `record_path`:

```python
order_lines = pd.json_normalize(
    records,
    record_path=["items"],
    meta=["order_id"],
    sep="_",
)

order_lines = order_lines[
    [
        "order_id",
        "line_id",
        "sku",
        "qty",
        "unit_price",
        "discounts",
    ]
].copy()
```

Then add a check:

```python
assert order_lines["line_id"].notna().all()
assert order_lines["order_id"].notna().all()
```

Grain:

```text
order_lines
→ one row per order line
```

Note that order `O1003` does not create an order-line row because its list is empty.

That is correct for the child table.

The parent order remains present in `orders`.

---

# 57. Lab Part 4 — `discounts` With pandas

Because discounts belong to individual line items, extract them from the line-level records rather than independently from the order.

A clear approach is:

```python
line_records = []

for order in records:
    for item in order.get("items") or []:
        line = dict(item)
        line["order_id"] = order["order_id"]
        line_records.append(line)

discounts = pd.json_normalize(
    line_records,
    record_path=["discounts"],
    meta=["order_id", "line_id"],
    sep="_",
)

discounts = discounts[
    [
        "order_id",
        "line_id",
        "discount_id",
        "code",
        "amount",
    ]
].copy()
```

Grain:

```text
discounts
→ one row per discount
```

Relationship:

```text
discounts.line_id
    ↓
order_lines.line_id
```

This avoids independently exploding:

```text
items[]
discounts[]
```

from the parent order.

---

# 58. Lab Part 5 — The Double-Counting Bug

Demonstrate the bug intentionally.

Take:

```python
line_level = order_lines.merge(
    orders[["order_id", "order_total"]],
    on="order_id",
    how="left",
)

print(line_level[["order_id", "line_id", "order_total"]])
```

For `O1001`, the output contains:

```text
O1001 | L1001-1 | 183.0
O1001 | L1001-2 | 183.0
```

Now this is wrong:

```python
bad_total = line_level["order_total"].sum()
print(bad_total)
```

The problem is not the addition operation.

The problem is the grain mismatch.

```text
order_total
→ order grain

line_level
→ line grain
```

### Correct pattern

Use the parent table for parent-level revenue:

```python
correct_order_total = orders["order_total"].sum()
print(correct_order_total)
```

Or aggregate line-level amounts only:

```python
order_lines["line_total"] = (
    order_lines["qty"] * order_lines["unit_price"]
)
```

Then aggregate that child-grain measure:

```python
line_totals = (
    order_lines.groupby("order_id", as_index=False)
    .agg(lines_total=("line_total", "sum"))
)
```

If discounts affect the final business amount, account for them at the appropriate grain before reconciling totals.

---

# 59. Lab Part 6 — Empty Line Arrays

Order `O1003` contains:

```json
"items": []
```

Verify:

```python
assert "O1003" in set(orders["order_id"])
assert "O1003" not in set(order_lines["order_id"])
```

This is often the correct relationship:

```text
Parent table:
O1003 exists

Child table:
no line exists
```

Do not create a fake line such as:

```text
sku = "__NO_LINE__"
```

unless the business model explicitly requires a placeholder record.

---

# 60. Lab Part 7 — Optional Payment

Payment is a separate optional nested entity.

Build a payment table:

```python
payments = []

for order in records:
    payment = order.get("payment")
    if payment is None:
        continue

    payments.append(
        {
            "payment_id": payment["payment_id"],
            "order_id": order["order_id"],
            "method": payment["method"],
        }
    )

payments = pd.DataFrame(payments)
```

Grain:

```text
payments
→ one row per payment
```

Order `O1002` has:

```text
payment = null
```

and therefore produces no payment row.

That does not imply the order itself should disappear.

---

# 61. Lab Part 8 — Polars Implementation

```python
import json
import polars as pl

pl_orders = pl.DataFrame(records)
```

Inspect the inferred shape:

```python
print(pl_orders.schema)
```

You should expect nested types such as:

```text
customer → Struct
items    → List
payment  → Struct or nullable Struct
metadata → Struct-like/dynamic representation depending on inference
```

For the parent table:

```python
orders_pl = (
    pl_orders
    .select(
        "order_id",
        pl.col("customer").struct.field("id").alias("customer_id"),
        pl.col("customer").struct.field("name").alias("customer_name"),
        pl.col("customer").struct.field("address").struct.field("city")
            .alias("customer_address_city"),
        pl.col("customer").struct.field("address").struct.field("country")
            .alias("customer_address_country"),
        "payment",
        "order_total",
        "metadata",
    )
)
```

Then extract payment fields without exploding orders:

```python
payments_pl = (
    orders_pl
    .select(
        "order_id",
        pl.col("payment").struct.field("payment_id").alias("payment_id"),
        pl.col("payment").struct.field("method").alias("method"),
    )
    .filter(pl.col("payment").is_not_null())
)
```

For the line table:

```python
order_lines_pl = (
    pl_orders
    .select(
        "order_id",
        pl.col("items").alias("items"),
    )
    .explode("items")
    .filter(pl.col("items").is_not_null())
    .select(
        "order_id",
        pl.col("items").struct.field("line_id").alias("line_id"),
        pl.col("items").struct.field("sku").alias("sku"),
        pl.col("items").struct.field("qty").alias("qty"),
        pl.col("items").struct.field("unit_price").alias("unit_price"),
        pl.col("items").struct.field("discounts").alias("discounts"),
    )
)
```

For discounts, preserve the parent line relationship:

```python
discounts_pl = (
    order_lines_pl
    .select(
        "order_id",
        "line_id",
        "discounts",
    )
    .explode("discounts")
    .filter(pl.col("discounts").is_not_null())
    .select(
        "order_id",
        "line_id",
        pl.col("discounts").struct.field("discount_id").alias("discount_id"),
        pl.col("discounts").struct.field("code").alias("code"),
        pl.col("discounts").struct.field("amount").alias("amount"),
    )
)
```

This uses the data hierarchy:

```text
orders
   ↓
items
   ↓
discounts
```

rather than creating unrelated combinations.

---

# 62. Lab Part 9 — DuckDB Implementation

A convenient approach for the learning lab is to register the already-parsed Python records or a pandas DataFrame, then use DuckDB SQL for nested operations.

```python
import duckdb
import pandas as pd

raw_df = pd.DataFrame(records)

con = duckdb.connect()
con.register("orders_raw", raw_df)
```

Parent projection:

```sql
SELECT
    order_id,
    customer.id AS customer_id,
    customer.name AS customer_name,
    customer.address.city AS customer_city,
    customer.address.country AS customer_country,
    order_total
FROM orders_raw;
```

The grain remains:

```text
1 row = 1 order
```

---

# 63. Lab Part 10 — DuckDB `UNNEST` for Lines

Use:

```sql
SELECT
    order_id,
    item.line_id,
    item.sku,
    item.qty,
    item.unit_price,
    item.discounts
FROM orders_raw,
UNNEST(items) AS t(item);
```

The list becomes rows.

The grain becomes:

```text
1 row = 1 order line
```

DuckDB documents that a list unnest duplicates the input row's scalar values for each list element. citeturn722838search0

---

# 64. Lab Part 11 — DuckDB `UNNEST` for Discounts

A safe hierarchy-preserving pattern is:

```sql
WITH lines AS (
    SELECT
        order_id,
        item.line_id AS line_id,
        item.discounts AS discounts
    FROM orders_raw,
    UNNEST(items) AS t(item)
)
SELECT
    order_id,
    line_id,
    discount.discount_id,
    discount.code,
    discount.amount
FROM lines,
UNNEST(discounts) AS t(discount);
```

Grain:

```text
1 row = 1 discount
```

Parent relationship:

```text
discount.line_id
    ↓
order_lines.line_id
```

---

# 65. Lab Part 12 — Empty Arrays in DuckDB

Because DuckDB returns zero rows when unnesting a `NULL` or empty list, the child query naturally contains only real child elements. citeturn722838search0

Therefore:

```text
orders_raw
→ preserves O1003

UNNEST(items)
→ no line for O1003
```

That is often exactly what a normalized child table should do.

---

# 66. Lab Part 13 — Nested Parquet

A nested Parquet representation can preserve the source hierarchy.

A simple PyArrow example:

```python
import json
import pyarrow as pa
import pyarrow.parquet as pq

nested_rows = []

for record in records:
    nested_rows.append(
        {
            "order_id": record["order_id"],
            "customer": record["customer"],
            "items": record["items"],
            "payment": record["payment"],
            "metadata_raw_json": json.dumps(
                record["metadata"],
                sort_keys=True,
            ),
            "order_total": record["order_total"],
        }
    )

nested_table = pa.Table.from_pylist(nested_rows)

pq.write_table(
    nested_table,
    "nested_orders.parquet",
)
```

This keeps:

```text
customer → struct
items    → list of structs
payment  → nullable struct-like field
```

and preserves dynamic metadata as raw JSON text.

Do not assume every source-side Python object maps to exactly the same nested Arrow type in every library/version. Inspect the resulting schema.

---

# 67. Lab Part 14 — Flat / Normalized Parquet

Convert the normalized DataFrames/tables separately:

```python
import pyarrow as pa
import pyarrow.parquet as pq

orders_table = pa.Table.from_pandas(
    orders,
    preserve_index=False,
)

lines_table = pa.Table.from_pandas(
    order_lines,
    preserve_index=False,
)

discounts_table = pa.Table.from_pandas(
    discounts,
    preserve_index=False,
)

pq.write_table(orders_table, "orders.parquet")
pq.write_table(lines_table, "order_lines.parquet")
pq.write_table(discounts_table, "discounts.parquet")
```

Now compare:

```text
Nested representation
→ one dataset with nested fields

Normalized representation
→ related datasets with explicit grains
```

---

# 68. Lab Part 15 — Compare Nested vs Flat Parquet

Populate this table with measurements from your environment.

| Representation | Rows | Columns | File Size | Query | Runtime | Memory | Notes |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| Nested Parquet | | | | | | | |
| Flat orders Parquet | | | | | | | |
| Flat lines Parquet | | | | | | | |

Do not fill this table with invented values.

Useful questions:

- Which representation is easier to query?
- Which requires fewer joins?
- Which has a simpler schema?
- How much row multiplication occurs?
- Which consumer tools support the nested representation?
- Which representation best matches the dominant workload?

---

# 69. Lab Part 16 — Raw Metadata JSON

For dynamic metadata, preserve the raw representation:

```python
orders["metadata_raw_json"] = orders["metadata"].map(
    lambda value: json.dumps(value, sort_keys=True)
)
```

Now count recurring keys:

```python
from collections import Counter

key_counts = Counter()

for record in records:
    metadata = record.get("metadata") or {}
    key_counts.update(metadata.keys())

print(key_counts)
```

Expected behavior:

```text
The output is determined by the input records.
```

Do not hard-code an expected count.

The goal is to discover:

```text
Which dynamic keys recur often enough to justify typed modeling?
```

---

# 70. Lab Part 17 — Validation

The lab must validate:

## Parent count

```python
assert orders["order_id"].nunique() == len(records)
```

## Child identity

```python
assert order_lines["line_id"].is_unique
```

If the business source allows duplicate line IDs, use a composite key instead.

## Parent-child integrity

```python
valid_order_ids = set(orders["order_id"])

assert set(order_lines["order_id"]).issubset(valid_order_ids)
```

## Discount-parent integrity

```python
valid_line_ids = set(order_lines["line_id"])

assert set(discounts["line_id"]).issubset(valid_line_ids)
```

## Empty array preservation

```python
assert "O1003" in set(orders["order_id"])
```

## No unintended cross-product

Compare expected source child counts with resulting child counts.

## Value preservation

Reconcile important identifiers and measures against the source representation.

---

# 71. Grain Tracking Template

Use this in every nested transformation project:

| Dataset | Before grain | Operation | After grain | Key |
| --- | --- | --- | --- | --- |
| `orders` | one row/order | flatten customer | one row/order | `order_id` |
| `orders` | one row/order | explode `items` | one row/order_line | `order_id + line_id` |
| `order_lines` | one row/line | explode `discounts` | one row/discount | `line_id + discount_id` |

This small table is one of the most useful production artifacts you can create during nested-data work.

---

# 72. Data Quality Rules for Nested Transformations

## Parent Count

Compare the number of source parent records with the output parent table.

## Child Count

For every parent:

```text
source item count
=
output order-line count
```

subject to the explicit null/empty policy.

## Relationship Integrity

Every child must reference a valid parent.

## Discount Count

The source discount count must reconcile with `discounts`.

## Empty-Array Preservation

If the business requirement says parents must remain, assert that they do.

## No Cross-Product

For each order and line, validate expected child counts.

## Measure Integrity

Parent-level totals must reconcile without being multiplied by child cardinality.

---

# 73. Performance Considerations

Nested transformations can be expensive.

### Explode Can Multiply Rows

If:

```text
1 million orders
average 20 items/order
```

the line table can approach:

```text
20 million rows
```

before considering discounts or other child arrays.

The multiplication is a data-model consequence, not merely a library-performance problem.

### Wide Flattening Can Create Large Schemas

A dynamic metadata object can turn:

```text
few keys per record
```

into:

```text
thousands of possible columns
```

with sparse values.

### Repeated Traversal Costs CPU and Memory

Deep nested transformations can require:

- repeated decoding
- object construction
- list materialization
- joins
- serialization

The important rule is:

> **Row multiplication is both a data-modeling issue and a performance issue.**

---

# 74. Nested Data and Columnar Storage

Nested data can be stored in two broad ways.

## Option A — Keep Nested

```text
Nested JSON
    ↓
Typed nested representation
    ↓
Nested Parquet
```

## Option B — Normalize

```text
Nested JSON
    ↓
Model by grain
    ↓
orders / order_lines / discounts
    ↓
Flat Parquet
```

The correct choice depends on:

- access patterns
- consumers
- schema stability
- query complexity
- joins
- file design
- engine support

Do not assume flattening is automatically more analytical.

---

# 75. Engine Comparison

| Tool | Struct flattening | List explode | Nested access | Main strength | Main consideration |
| --- | --- | --- | --- | --- | --- |
| pandas | `json_normalize` | `explode` | DataFrame/Python oriented | familiar, flexible workflow | memory |
| Polars | `unnest` / struct expressions | `explode` | struct/list namespaces | expression-oriented transformations | API learning/versioning |
| DuckDB | struct access / `UNNEST` | `UNNEST` | SQL nested access | SQL analytics | SQL/engine semantics |
| PyArrow | `Table.flatten` | compute/list operations | Arrow-native nested types | Arrow interoperability | lower-level API |

Treat this as a capability map, not a performance ranking.

---

# 76. Common Nested-Data Debugging Problems

Use this production debugging loop:

```text
Symptom
  ↓
Likely causes
  ↓
Inspect
  ↓
Measure
  ↓
Fix
  ↓
Lesson
```

---

## Problem 1 — Rows Increased 20× Unexpectedly

### Symptom

```text
input rows    = 1,000,000
output rows   = 20,000,000
```

### Likely causes

- explode
- repeated child arrays
- accidental cross-product

### Inspect

Track:

```text
source child count
operation
output child count
```

### Fix

Write grain before and after each operation.

### Lesson

Row multiplication must be intentional.

---

## Problem 2 — Some Orders Disappeared

### Likely causes

- empty arrays
- null arrays
- inner-style joins
- filtering null child structs after a parent-preserving operation

### Inspect

Find parents where:

```text
items = []
items = null
```

### Fix

Build the parent table separately when parent preservation is required.

### Lesson

Parent survival is a modeling requirement.

---

## Problem 3 — Revenue Doubled

### Likely cause

An order-level measure was aggregated at line grain.

### Inspect

Check:

```text
measure grain
table grain
```

### Fix

Aggregate using the correct source table or aggregate at the measure's true grain.

### Lesson

Grain errors often look like simple arithmetic bugs.

---

## Problem 4 — Hundreds of Unexpected Columns

### Likely cause

Flattening a dynamic metadata map.

### Inspect

Count distinct metadata keys.

### Fix

Keep the dynamic object as raw JSON or map-like data unless a stable analytical model exists.

### Lesson

Do not turn every dynamic key into a permanent column.

---

## Problem 5 — Different Records Infer Different Types

### Likely cause

Heterogeneous JSON.

### Inspect

Sample field values and types.

### Fix

Choose:

- strict rejection
- documented coercion
- quarantine
- raw preservation

### Lesson

Inference is not a schema policy.

---

## Problem 6 — Nested Field Is Missing

### Likely causes

- optional field
- null
- schema drift
- incorrect path
- inconsistent producer behavior

### Inspect

Inspect source records where the path exists and where it does not.

### Fix

Make the missing/null policy explicit.

### Lesson

Missing is a data state, not automatically a parser error.

---

## Problem 7 — Two Arrays Cause a Huge Row Explosion

### Likely cause

Independent array cross-product.

### Inspect

Compare:

```text
len(items)
len(promotions)
```

and expected relationships.

### Fix

Transform nested relationships at their actual parent/child levels.

### Lesson

Structure in the source should determine how arrays are normalized.

---

## Problem 8 — Flattening Creates an Unmanageable Schema

### Likely cause

Flattening all levels of a dynamic document.

### Inspect

Count output columns and null density.

### Fix

Flatten only business-critical fields; retain nested/raw fields for flexible attributes.

### Lesson

"Fully flat" is not a universal definition of good analytical data.

---

# 77. Common Mistakes

## 1. Exploding Without Recording the Grain

Why it matters:

You can no longer tell what one row means.

---

## 2. Treating Flatten and Explode as the Same Operation

They are different:

```text
struct → columns
list   → rows
```

---

## 3. Losing Parents With Empty Arrays

A child explosion can legitimately produce no child rows while the parent still matters.

---

## 4. Treating Null and Empty Arrays as Identical

They can have different source semantics.

---

## 5. Exploding Two Independent Arrays Sequentially

This can create false combinations.

---

## 6. Double Counting Parent Measures

Repeated parent values are not automatically additive at child grain.

---

## 7. Using `SUM(DISTINCT ...)` as a Lazy Fix

Distinct values can legitimately repeat across different parents.

---

## 8. Flattening Every Possible Field

This creates:

- wide schemas
- sparse columns
- schema churn

---

## 9. Converting Every Map Key Into a Column

Dynamic keys should be modeled according to stability and workload.

---

## 10. Ignoring Schema Heterogeneity

One malformed or variant record can break inference assumptions.

---

## 11. Silently Coercing Incompatible Types

Conversion without an explicit rule can corrupt semantics.

---

## 12. Discarding Raw Source Data Too Early

Raw preservation can be critical for replay and debugging.

---

## 13. Assuming Tools Have Identical Semantics

pandas, Polars, DuckDB, and Arrow differ.

Test the actual library/version.

---

## 14. Assuming Nested Parquet Is Always Better

Nested can be excellent for some workloads and inconvenient for others.

---

## 15. Assuming Flat Parquet Is Always Better

Flat models can introduce joins and lose natural hierarchy.

---

## 16. Ignoring Downstream Consumers

BI tools, analysts, ML systems, and operational debugging users may have different needs.

---

## 17. Forgetting Parent/Child Keys

Without stable keys, relationships can become ambiguous after normalization.

---

## 18. Failing to Validate Row Counts

A transformation that "looks right" can still be wrong.

---

# 78. Production Design Pattern

A robust nested-data pipeline often looks like:

```text
Raw JSON / Event
      ↓
    Bronze
      ↓
Schema Inspection
      ↓
   Validation
      ↓
 Identify Grain
      ↓
Typed Transformation
      ↓
┌────────────┬─────────────┬────────────┐
│   orders   │ order_lines │ discounts  │
└────────────┴─────────────┴────────────┘
      ↓
    Parquet
      ↓
  Analytics
```

The responsibilities are:

### Bronze

Preserve source information.

### Schema inspection

Understand actual producer shape.

### Validation

Reject or quarantine invalid records.

### Grain identification

Define the meaning of every output row.

### Typed transformation

Flatten stable structs and normalize meaningful repeated entities.

### Output

Write controlled analytical data.

### Analytics

Serve consumers at the correct grain.

---

# 79. Hybrid Modeling Pattern

Not everything needs to become a separate table.

A practical hybrid can look like:

```text
orders
├── typed scalar columns
├── important customer fields
├── normalized line items
└── metadata_raw_json
```

This can balance:

- query convenience
- schema stability
- flexibility
- source fidelity

It is a design pattern, not a universal standard.

---

# 80. Decision Framework — Keep Nested or Flatten?

Use this as a starting decision tree:

```text
Is the field nested?
       │
       ├── STRUCT?
       │      │
       │      └── Is direct scalar access useful?
       │             ├── Yes → Flatten/unnest selectively
       │             └── No  → Consider keeping nested
       │
       └── LIST/ARRAY?
              │
              └── Does it represent repeated entities?
                     ├── Yes → Consider child table / explode
                     └── No  → Consider keeping nested
```

Then ask:

```text
Before deciding:
→ What is the grain?
→ Who consumes it?
→ How often is it queried?
→ How dynamic is the schema?
→ How much would flattening increase columns?
→ Would exploding multiply rows dramatically?
```

---

# 81. Production Case Study — E-Commerce Orders

A retail company receives an event payload containing:

- customer struct
- order lines
- line-level discounts
- payment struct
- dynamic metadata

Consumers include:

- BI users
- analysts
- ML users
- operational debugging users

### Questions

1. What should become scalar columns?
2. What should become child tables?
3. What should remain nested?
4. What should remain raw JSON?
5. What are the grains?
6. Which keys are required?
7. How do we prevent double counting?

---

## Worked Reasoning

### `orders`

Good candidates:

```text
order_id
customer_id
customer_name
customer_address_city
customer_address_country
order_total
```

These fields are:

- stable
- directly useful
- order-grain attributes

### `order_lines`

Use:

```text
line_id
order_id
sku
qty
unit_price
```

because a line is a meaningful repeated business entity.

### `discounts`

Use:

```text
discount_id
line_id
order_id
code
amount
```

because discounts belong to lines.

### `payments`

Use a child table when payment can repeat or when payment analysis is important.

### Dynamic metadata

Keep:

```text
metadata_raw_json
```

until recurring metadata fields prove sufficiently stable to become typed columns.

### Why?

Because the model preserves:

```text
order grain
line grain
discount grain
```

rather than forcing everything into one row shape.

---

# 82. How a Senior Data Engineer Handles Nested Data

Senior engineers do not start with:

> "Which library function should I call?"

They start with:

> **"What does one row mean after this transformation?"**

Use this reasoning framework:

```text
Understand Source Shape
        ↓
Draw JSON Tree
        ↓
Define Business Grain
        ↓
Identify Parent/Child Relationships
        ↓
Decide Flatten vs Explode
        ↓
Design Keys
        ↓
Handle Null/Empty Collections
        ↓
Handle Schema Drift
        ↓
Preserve Raw Data Where Needed
        ↓
Validate Counts and Relationships
        ↓
Write Typed Outputs
        ↓
Measure Query Convenience
```

This is the actual production workflow.

---

# 83. Architecture Review Questions

When reviewing a nested-data design, ask:

```text
What is the source grain?
What is the target grain?
Which fields changed row count?
Which parent keys were retained?
Can an empty child collection remove a parent?
Can two arrays create a cross-product?
Which measures changed grain?
Which fields are dynamic?
Which fields are typed?
What happens when a field changes type?
Can the source be replayed?
Which consumers support the final representation?
```

A good design should answer each question explicitly.

---

# 84. Format / Storage Decision for Nested Data

Nested modeling is also a storage decision.

Ask:

| Question | Why it matters |
| --- | --- |
| Does the consumer support nested types? | Determines query usability |
| Is the nested structure stable? | Determines schema maintenance cost |
| Does a list represent a business entity? | May imply a child table |
| Will explode multiply rows heavily? | Determines compute/storage impact |
| Are dynamic keys frequent? | May favor raw/map/Variant representation |
| Are BI tools involved? | Flat columns may be easier |
| Is source fidelity important? | Nested/raw preservation may matter |
| Do we need many independent child queries? | Related tables may be clearer |

No single representation is correct for every workload.

---

# 85. Interview Questions

## Basic

### 1. What is semi-structured data?

**Model answer:**  
Data with meaningful structure that may be nested, optional, or evolving rather than conforming to one rigid rectangular schema. JSON event payloads are a common example.

### 2. What is a struct?

**Model answer:**  
A nested object containing named fields. Flattening a struct usually converts those fields into columns without changing the parent row grain.

### 3. What is a list?

**Model answer:**  
A collection of zero or more elements. When a list represents repeated entities, exploding it usually changes row grain.

### 4. What is a map?

**Model answer:**  
Key/value data where the set of keys can be dynamic. It is useful for flexible metadata but can create sparse schemas if every key is flattened.

### 5. What is table grain?

**Model answer:**  
The business meaning of one row. For example, one row per order, one row per order line, or one row per discount.

### 6. What is flattening?

**Model answer:**  
Turning nested struct/object fields into scalar columns without necessarily changing row count.

### 7. What is exploding?

**Model answer:**  
Turning each element of a list into a separate row, which changes cardinality and usually changes grain.

---

## Intermediate

### 8. What is `json_normalize`?

**Model answer:**  
A pandas function for turning JSON-like nested records into a tabular DataFrame, with options such as `record_path`, `meta`, and `sep`.

### 9. What is `record_path`?

**Model answer:**  
The path to the repeated child records that should become rows.

### 10. What is `meta`?

**Model answer:**  
Parent fields that should be carried into the resulting child records, commonly keys such as `order_id`.

### 11. Why does explode change grain?

**Model answer:**  
Because one input row can produce multiple rows, one for each list element.

### 12. Why preserve parent keys?

**Model answer:**  
Because after normalization the hierarchy is no longer contained in a single document. Keys preserve parent-child relationships.

### 13. What happens to empty arrays?

**Model answer:**  
The child collection contains zero elements. The exact DataFrame/explode output semantics vary by tool, so production code should test the library/version and preserve the parent separately when required.

### 14. Why can flattening be useful?

**Model answer:**  
It can make frequently queried nested fields easier to use in SQL/BI and can provide a stable analytical interface for important attributes.

---

## Advanced

### 15. How can exploding nested data cause double counting?

**Model answer:**  
A parent-level measure can be repeated across child rows. Summing it after explosion counts the same parent measure multiple times.

### 16. What is a cross-product from two arrays?

**Model answer:**  
When two independent collections are combined as though their elements were related, producing combinations that did not exist in the source.

### 17. When should nested data remain nested in Parquet?

**Model answer:**  
When source fidelity or document-style retrieval is valuable, downstream engines support the nested types, and flattening would add little analytical value or cause significant schema/row multiplication.

### 18. How should heterogeneous JSON be handled?

**Model answer:**  
First detect it. Then use an explicit policy: reject/quarantine, controlled coercion, or preserve the raw value when semantics are uncertain.

### 19. Why preserve raw JSON?

**Model answer:**  
For replay, debugging, future parsing, schema discovery, and recovery from transformations that later prove incorrect.

### 20. How can schema evolution differ between nested and flat designs?

**Model answer:**  
Nested changes may remain localized inside a structure, while flattening can expose each nested field as a top-level contract. Dynamic nested structures can also make flat schemas unstable.

---

## Senior / Architecture

### 21. How would you design tables from a deeply nested event payload?

**Model answer:**  
First map the JSON tree, identify business entities and grains, define parent/child keys, decide which structs become scalar columns, decide which arrays represent independent child entities, preserve raw dynamic data where needed, then validate row counts and relationships.

### 22. How would you prove your transformation did not change business meaning?

**Model answer:**  
Define source and target grains first, reconcile parent and child counts, validate key relationships, compare important source values, test null/empty behavior, and reconcile business measures at their correct grains.

### 23. How would you handle an event where a field changes type?

**Model answer:**  
Detect the type drift, determine whether the change is semantically compatible, apply a documented coercion or quarantine policy, and preserve the original payload so the transformation can be replayed.

### 24. How would you design bronze-to-silver nested processing?

**Model answer:**  
Preserve the original event in bronze, inspect/validate its schema, model stable fields explicitly, split repeated business entities into tables where appropriate, retain dynamic attributes in a controlled form, and publish typed silver outputs with tests.

### 25. How would you prevent future developers from introducing double counting?

**Model answer:**  
Make grain explicit in dataset/table documentation, encode relationship keys, add aggregate reconciliation tests, include grain comments in transformation code, and reject changes that mix measures from different grains without an intentional aggregation step.

---

# 86. Practical Scenarios

## Scenario 1 — Empty Items

An order has:

```json
{
  "order_id": "O2001",
  "items": []
}
```

### Question

Should the order disappear?

### Reasoning

Not necessarily.

If the `orders` table represents orders, the order should normally remain if it is a valid source order.

There simply are no child rows in `order_lines`.

---

## Scenario 2 — Parent Amount

An order has:

```text
order_total = 500
```

and five lines.

### Question

Can you sum `order_total` after exploding to lines?

### Reasoning

Not directly.

The value has order grain while the rows have line grain.

You need to aggregate at order grain or use a measure that truly belongs to the line grain.

---

## Scenario 3 — Two Arrays

An order has:

```text
items = 3
promotions = 4
```

### Question

What happens if you independently combine both collections per order?

### Reasoning

You can create up to:

```text
3 × 4 = 12
```

combinations.

Those 12 pairings may not exist in the source.

---

## Scenario 4 — Dynamic Metadata

An event contains a few metadata keys per record, but over a year the key set reaches 2,000 distinct keys.

### Question

Should every key become a column?

### Reasoning

Not automatically.

Inspect:

- key frequency
- business value
- query frequency
- schema stability
- null density

Stable/high-value keys can become typed columns. Dynamic remainder can remain map/JSON-like.

---

## Scenario 5 — Nested Parquet Consumers

Consumers include:

- DuckDB
- Polars
- BI tooling with limited nested support

### Question

Should the dataset remain fully nested?

### Reasoning

Not automatically.

The consumer with the strictest practical limitations may justify a flat analytical projection while retaining nested/raw data elsewhere.

The decision should be validated against actual query patterns and tool behavior.

---

# 87. Stop-and-Think Exercises

## Exercise A

If:

```text
1 row = 1 order
```

and you explode `items`, what is the likely new grain?

### Answer

```text
1 row = 1 order line/item
```

provided each list element represents an item/line entity.

---

## Exercise B

Does flattening:

```text
customer.name
```

necessarily change row count?

### Answer

No.

Flattening a scalar field from a struct can preserve the parent row grain.

---

## Exercise C

An order contains:

```text
3 items
4 promotions
```

What can happen if both arrays are independently combined?

### Answer

Potentially:

```text
12 combinations
```

which may be an unintended cross-product.

---

## Exercise D

An order has:

```text
order_total = 500
```

and five lines.

What happens if `order_total` is copied to each line and then summed?

### Answer

Potential overcounting:

```text
500 × 5 = 2,500
```

The problem is grain mismatch.

---

## Exercise E

Metadata has 2,000 possible keys over time, but each record uses only a few.

Should you flatten every key?

### Answer

Not automatically.

Evaluate:

- query usefulness
- frequency
- stability
- schema growth
- null density

A raw JSON/map/Variant-style representation may be better for the dynamic portion.

---

# 88. Testing Nested Transformations

Production tests should validate both **data values** and **data meaning**.

## 88.1 Grain Tests

Verify:

```text
orders.order_id is unique
order_lines.line_id is unique (if contract says so)
discounts.discount_id is unique (if contract says so)
```

## 88.2 Parent-Child Integrity

```python
assert set(order_lines["order_id"]).issubset(
    set(orders["order_id"])
)
```

## 88.3 Empty Arrays

Test explicit parent-preservation requirements.

```python
assert "O1003" in set(orders["order_id"])
```

## 88.4 Null Semantics

Test:

- null child collection
- empty child collection
- null nested field
- missing nested field

## 88.5 No Cross-Product

Construct a test with:

```text
2 items
3 promotions
```

and assert that your intended output does **not** contain six false relationships.

## 88.6 Value Preservation

Compare:

```text
order_id
line_id
discount_id
customer_id
important measures
```

between source and output.

## 88.7 Aggregate Reconciliation

Reconcile source totals at their correct grain.

---

# 89. Example Validation Function

```python
def validate_nested_outputs(
    source_records: list[dict],
    orders: pd.DataFrame,
    order_lines: pd.DataFrame,
    discounts: pd.DataFrame,
) -> None:
    source_order_ids = {
        record["order_id"]
        for record in source_records
    }

    assert set(orders["order_id"]) == source_order_ids

    source_line_count = sum(
        len(record.get("items") or [])
        for record in source_records
    )

    assert len(order_lines) == source_line_count

    source_discount_count = sum(
        len(item.get("discounts") or [])
        for record in source_records
        for item in record.get("items") or []
    )

    assert len(discounts) == source_discount_count

    assert set(order_lines["order_id"]).issubset(
        source_order_ids
    )

    assert set(discounts["line_id"]).issubset(
        set(order_lines["line_id"])
    )
```

This validates structural correctness without assuming a specific business total.

---

# 90. Grain as a Data Contract

Document grain as part of every output dataset.

For example:

```text
Dataset: orders
Grain: one row per order
Primary key: order_id

Dataset: order_lines
Grain: one row per order line
Primary key: line_id
Foreign key: order_id

Dataset: discounts
Grain: one row per discount
Primary key: discount_id
Foreign key: line_id
```

This makes the model understandable to:

- engineers
- analysts
- reviewers
- future maintainers

A grain statement is often more valuable than a long transformation comment.

---

# 91. Production Reliability Pattern

A robust nested transformation should be designed around:

```text
Raw Source
    ↓
Preserve
    ↓
Inspect
    ↓
Validate
    ↓
Define Grain
    ↓
Transform
    ↓
Validate Again
    ↓
Publish
```

Never let:

```text
parse success
```

be mistaken for:

```text
business correctness
```

A parser can succeed while still creating:

- duplicated rows
- missing parents
- wrong types
- false relationships
- incorrect aggregates

---

# 92. Measuring a Nested Transformation

When benchmarking nested transformations, measure more than runtime.

Use:

| Measurement | Why it matters |
| --- | --- |
| Source rows | parent cardinality |
| Output rows | row multiplication |
| Child rows | repeated-entity volume |
| Output columns | schema width |
| Memory | transformation pressure |
| Runtime | user/system latency |
| Output size | storage |
| Query time | downstream usability |
| Join count | analytical complexity |
| Validation failures | source/data quality |

A transformation that is slightly faster but produces incorrect grain is not an optimization.

---

# 93. Fair Benchmarking

Nested representations should be compared with:

```text
Same source data
       ↓
Same semantic result
       ↓
Same query intent
       ↓
Same environment
       ↓
Measure
       ↓
Compare
```

Do not compare:

```text
nested dataset
```

against:

```text
flat dataset
```

when they answer different business questions.

The result must be semantically equivalent before performance comparison is meaningful.

---

# 94. Required Lab Comparison Table

Use this measurement template:

| Representation | Rows | Columns | File Size | Query | Runtime | Memory | Notes |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| Nested Parquet | | | | | | | |
| Flat orders Parquet | | | | | | | |
| Flat lines Parquet | | | | | | | |

Populate it only from actual measurements.

---

# 95. Final Data-Modeling Checklist

Before publishing a nested-data transformation, verify:

- [ ] I drew the source JSON tree.
- [ ] I identified structs.
- [ ] I identified lists.
- [ ] I identified maps.
- [ ] I wrote the source grain.
- [ ] I wrote the target grain.
- [ ] I identified parent/child relationships.
- [ ] I defined keys.
- [ ] I decided flatten vs explode.
- [ ] I tested null behavior.
- [ ] I tested empty arrays.
- [ ] I checked for cross-products.
- [ ] I checked for double counting.
- [ ] I handled heterogeneous types.
- [ ] I handled sparse keys.
- [ ] I preserved raw data where justified.
- [ ] I tested the transformation.
- [ ] I validated row counts and relationships.

---

# 96. Learning Checkpoint

Do not move on until you can honestly check every item.

### Roadmap checkpoint

- [ ] Explain flatten vs explode and state the grain after each.
- [ ] Split a nested document into related tables with keys.
- [ ] Avoid double counting after an explode.
- [ ] Decide when to keep nested types instead of flattening.

### Tool skills

- [ ] Use `pd.json_normalize`.
- [ ] Use `record_path`, `meta`, and `sep`.
- [ ] Use pandas `explode`.
- [ ] Use Polars `unnest`.
- [ ] Use Polars `explode`.
- [ ] Explain Polars struct/list operations.
- [ ] Use DuckDB `UNNEST`.
- [ ] Explain DuckDB nested access.
- [ ] Explain Arrow `Table.flatten()`.
- [ ] Use relevant Arrow compute functions for list/struct operations.

### Data modeling

- [ ] Preserve parents with empty child arrays when required.
- [ ] Distinguish null and empty collections.
- [ ] Preserve parent/child keys.
- [ ] Detect cross-products.
- [ ] Validate parent-child relationships.
- [ ] Avoid parent-level double counting.

### Advanced

- [ ] Handle heterogeneous JSON.
- [ ] Handle fields whose types change.
- [ ] Preserve raw JSON where appropriate.
- [ ] Compare nested and flat Parquet.
- [ ] Explain schema-evolution implications.
- [ ] Explain the limits of deep and recursive flattening.
- [ ] Explain Variant-style awareness.

### Production

- [ ] Explain how to validate nested transformations.
- [ ] Explain how to debug missing parents.
- [ ] Explain how to debug row multiplication.
- [ ] Explain how to design grain-aware output tables.
- [ ] Defend a nested/flat decision in an architecture review.

---

# 97. Final Master Mental Model

```text
             NESTED DATA
                  │
                  ↓
             Draw JSON Tree
                  │
                  ↓
             Identify Shapes
           ┌──────┼─────────┐
           ↓      ↓         ↓
        Scalar  Struct    List/Array
                   │          │
                   ↓          ↓
               Flatten      Explode
                   │          │
                   │          ↓
                   │     Grain Changes
                   │          │
                   └──────┬───┘
                          ↓
                   Define Target Grain
                          ↓
                     Define Keys
                          ↓
                  Parent / Child Tables
                          ↓
                   Handle Null / Empty
                          ↓
                  Prevent Cross-Products
                          ↓
                  Prevent Double Counting
                          ↓
                 Validate Relationships
                          ↓
                  Typed Analytical Storage
                          ↓
                    Nested / Flat Parquet
                          ↓
                       Consumers
```

The strongest habit in this topic is:

```text
Before every transformation:
"What does one row mean?"

After every transformation:
"What does one row mean now?"
```

---

# 98. Final "Remember This"

1. **Nested data is normal in APIs, events, and document systems.**
2. **A struct/object can often be flattened without changing row grain.**
3. **Exploding a list changes row grain.**
4. **Always write the grain before and after an explode.**
5. **Parent keys must survive when creating child tables.**
6. **Null and empty arrays are different concepts and must be handled deliberately.**
7. **Exploding two independent arrays can create a false cross-product.**
8. **Parent-level measures are not automatically safe to aggregate at child grain.**
9. **`SUM(DISTINCT ...)` is not a generic double-counting fix.**
10. **Dynamic maps do not automatically deserve hundreds of columns.**
11. **Heterogeneous JSON needs an explicit type-handling policy.**
12. **Raw JSON can complement typed data when the source is dynamic or uncertain.**
13. **Nested Parquet and flat Parquet are both valid designs for different workloads.**
14. **Consumer capability is part of the data-model decision.**
15. **Library semantics differ; test the actual versions you run.**
16. **A transformation that parses successfully can still be semantically wrong.**
17. **Row multiplication is both a modeling issue and a performance issue.**
18. **The goal is not to flatten everything. The goal is to produce a correct, useful analytical model.**

---

# 99. Concept Map

```text
Nested / Semi-Structured Data
│
├── Shapes
│   ├── Scalar
│   ├── Struct
│   ├── List / Array
│   └── Map
│
├── Modeling
│   ├── Grain
│   ├── Parent
│   ├── Child
│   ├── Keys
│   └── Relationships
│
├── Transformations
│   ├── Flatten
│   ├── Unnest
│   ├── Explode
│   └── Normalize
│
├── Edge Cases
│   ├── Null
│   ├── Empty
│   ├── Missing
│   ├── Cross-product
│   └── Double counting
│
├── Schema
│   ├── Heterogeneous types
│   ├── Optional fields
│   ├── Sparse keys
│   ├── Schema evolution
│   └── Raw preservation
│
├── Storage
│   ├── Nested Parquet
│   └── Flat Parquet
│
└── Tools
    ├── pandas
    ├── Polars
    ├── DuckDB
    └── PyArrow
```

---

# 100. Connection to the Rest of Module 2.5

This topic sits after the format-selection work and before physical optimization.

The learning path is:

```text
01 Row vs Column
       ↓
02 Parquet Internals
       ↓
03 PyArrow Parquet
       ↓
04 Avro
       ↓
05 ORC / Format Selection
       ↓
06 Nested Data
       ↓
07 Compression
       ↓
08 Partitioning
       ↓
09 Small Files
       ↓
10 Legacy Formats
```

The important connection is:

```text
Nested source shape
      ↓
Correct data model
      ↓
Correct physical representation
      ↓
Correct analytical queries
```

Later topics will deepen:

- compression choices
- partitioning
- small files
- legacy ingestion

Do not treat those later topics as prerequisites for this module.

---

# 101. Production Architecture Summary

A mature pipeline often separates concerns:

```text
Source API / Event
        ↓
    Raw Bronze
        ↓
Schema / Shape Inspection
        ↓
Validation
        ↓
Grain Definition
        ↓
Typed Nested / Normalized Model
        ↓
Silver Parquet
        ↓
Gold / BI / ML
```

The modeling choice at the middle is driven by:

```text
Business grain
+
Consumer needs
+
Schema stability
+
Query patterns
+
Engine support
+
Performance
+
Operational requirements
```

---

# 102. Final Professional Principle

A junior engineer often asks:

> "How do I explode this JSON?"

A production-minded engineer asks:

> "What entity does this array represent, what is the target grain, what keys preserve the relationship, what happens to parent-level measures, and how will downstream consumers query the result?"

That is the transition from **data manipulation** to **data engineering**.

---

## Official Documentation References

Use the installed project versions as the final authority for exact behavior. Helpful primary references include:

- [pandas `json_normalize`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.json_normalize.html)
- [Polars `DataFrame.explode`](https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.explode.html)
- [Polars struct expressions](https://docs.pola.rs/api/python/stable/reference/expressions/struct.html)
- [DuckDB `UNNEST`](https://duckdb.org/docs/current/sql/query_syntax/unnest)
- [DuckDB STRUCT type](https://duckdb.org/docs/current/sql/data_types/struct)
- [DuckDB list functions](https://duckdb.org/docs/current/sql/functions/list)
- [Apache Arrow `Table.flatten`](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html)
- [Apache Arrow compute functions](https://arrow.apache.org/docs/python/api/compute.html)
