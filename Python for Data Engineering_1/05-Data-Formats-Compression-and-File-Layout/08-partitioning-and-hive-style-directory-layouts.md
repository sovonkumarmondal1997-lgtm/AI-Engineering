# Partitioning and Hive-Style Directory Layouts

> **Stage 2 → Python for Data Engineering → Module 2.5 — Data Formats, Compression, and File Layout → Phase D → Topic 08**

## Learning Objectives

By the end of this module, you should be able to:

- explain partitioning and partition pruning;
- distinguish datasets, partitions, files, row groups, and pages;
- explain Hive-style `key=value` paths;
- choose partition columns using workload, selectivity, cardinality, stability, volume, and operational constraints;
- compare yearly, monthly, daily, and hourly granularity;
- reason about null and special-character partition values;
- write/read partitioned datasets with PyArrow, pandas, Polars, and DuckDB;
- design idempotent partition overwrites and backfills;
- identify over-partitioning, skew, and multi-level partition explosion;
- distinguish partitioning from sorting, clustering, and bucketing;
- reason about object-storage listing/request overhead;
- understand path-based partition migration and later awareness of hidden partitioning/partition evolution;
- benchmark partition strategies with DuckDB and MinIO;
- estimate partitions/files/bytes before testing;
- write an evidence-based production partitioning guideline.

### Core principle

> **Partitioning should be driven by workload, data volume, query filters, file sizing, operational constraints, and measurable pruning benefits.**

Never start with:

> "We always partition by date."

Start with:

> **"What physical layout reduces the real workload's cost without creating more operational cost than it saves?"**

---

## Prerequisites

This topic assumes completion of:

- Topic 01 — Row-Oriented vs Columnar Storage
- Topic 02 — Parquet Internals
- Topic 03 — Reading and Writing Parquet with PyArrow
- Topic 04 — Avro
- Topic 05 — ORC and Format Selection
- Topic 06 — Nested/Semi-Structured Data
- Topic 07 — Compression

You should already understand Parquet row groups, column chunks, pages, statistics, filtering, compression, and basic object storage. Earlier topics are connected here but not re-taught.

---

# 1. Why Partitioning Exists

Consider:

```text
orders
-----------------------------------------
order_id
created_at
country
customer_id
amount
product_category
```

Suppose the table has 1 billion rows across two years. A common query is:

```sql
SELECT SUM(amount)
FROM orders
WHERE created_at >= DATE '2026-01-01'
  AND created_at <  DATE '2026-02-01';
```

An unpartitioned layout might look like:

```text
orders/
├── part-000.parquet
├── part-001.parquet
├── part-002.parquet
└── ...
```

A partitioned layout might look like:

```text
orders/
├── year=2025/
│   ├── month=01/
│   ├── month=02/
│   └── ...
└── year=2026/
    ├── month=01/
    ├── month=02/
    └── ...
```

For a filter aligned with the partition values, a capable engine can avoid considering directories that cannot match.

That is **partition pruning**.

Partitioning is therefore a physical optimization, not merely a naming convention.

---

# 2. Partitioning vs File Layout vs Row Groups

These are separate levels:

```text
Dataset
  ↓
Partition
  ↓
File
  ↓
Row Group
  ↓
Page
```

| Concept | Physical meaning | Example |
| --- | --- | --- |
| Dataset | logical collection of files | `orders/` |
| Partition | subset identified by partition values | `year=2026/month=09` |
| File | physical object | `part-0001.parquet` |
| Row group | internal Parquet storage unit | row group 3 |
| Page | smaller internal storage unit | data page |

A partition is **not** a row group.

---

# 3. Partition Pruning

The core query path is:

```text
Query
  ↓
Partition Filter
  ↓
Partition Pruning
  ↓
Relevant Partitions
  ↓
Relevant Files
  ↓
Parquet Row Groups
  ↓
Columns / Pages
  ↓
Execution
```

A useful conceptual hierarchy is:

```text
Partition pruning
      ↓
File pruning
      ↓
Row-group pruning
      ↓
Page-level pruning
      ↓
Column pruning
```

This is a mental model, not a promise that every engine implements or exposes all levels in exactly this order.

### Partition pruning

Uses path/partition metadata to eliminate directories or files.

### Predicate pushdown

Moves a filter closer to the data source. With columnar formats, this can cooperate with file and row-group statistics.

### Row-group skipping

Uses Parquet metadata such as min/max statistics to avoid irrelevant internal regions.

### Column pruning

Reads only columns required by the query where the reader can do so.

---

# 4. What Is a Partition?

A partition is a physically separated subset of a dataset identified by one or more partition values.

Example:

```text
year=2026/month=09
```

means the partition key is conceptually:

```text
(year=2026, month=9)
```

The path turns a logical predicate into physical organization:

```text
Logical data
    ↓
Partition key
    ↓
Path
    ↓
Files
```

---

# 5. Hive-Style Directory Layouts

A classic Hive-style path is:

```text
dataset/year=2025/month=03/day=14/part-0000.parquet
```

Breakdown:

```text
dataset/
  year=2025/
    month=03/
      day=14/
        part-0000.parquet
```

The defining convention is `key=value`.

Current PyArrow documentation describes `HivePartitioning` as a multi-level `$key=$value` directory scheme. The partition parser also supports URI decoding of path segments and a configurable null fallback. citeturn916880search2

---

# 6. A Partitioned Dataset on Disk

```text
orders/
├── year=2025/
│   ├── month=01/
│   │   ├── part-0.parquet
│   │   └── part-1.parquet
│   └── month=02/
│       └── part-0.parquet
└── year=2026/
    ├── month=01/
    │   └── part-0.parquet
    └── month=02/
        └── part-0.parquet
```

For:

```sql
WHERE year = 2026 AND month = 2
```

a Hive-aware reader can potentially focus on:

```text
orders/year=2026/month=02/
```

The files still contain ordinary Parquet internals such as row groups and pages.

---

# 7. Partition Columns

A logical table can contain:

```text
order_id
created_at
country
amount
```

You can derive:

```text
year
month
```

from `created_at` and use them for directory partitioning.

Important distinction:

> **Partition information in the path is separate from whether the same fields are physically stored as ordinary columns in each Parquet file.**

Some tools can reconstruct partition columns from the path during dataset discovery. DuckDB's current documentation explicitly describes partition columns as being read from directory structure when Hive partitioning is enabled. citeturn807253search3

---

# 8. Cardinality and Selectivity

## Cardinality

Cardinality is the number of distinct values.

Examples:

```text
year        → few values
month       → 12 values
country     → relatively low/moderate cardinality
customer_id → potentially millions
session_id  → potentially millions/billions
```

High cardinality is a warning sign for partitioning.

## Selectivity

Selectivity asks how much of the dataset a filter selects.

A query selecting 2 of 10,000 partitions has much more pruning potential than a query selecting 8,000 of 10,000.

Crucial distinction:

```text
high cardinality
≠
good partition key
```

and:

```text
highly selective predicate
≠
partition it directly
```

---

# 9. Choosing Partition Columns

Evaluate a candidate against:

| Factor | Question |
| --- | --- |
| Filter frequency | Do important queries filter on it? |
| Selectivity | Can the filter eliminate a large fraction of data? |
| Cardinality | How many distinct values exist? |
| Stability | Will the value change later? |
| Volume | How much data lands in each value? |
| Skew | Are some values much larger? |
| File health | Will files remain operationally healthy? |
| Backfills | How much data must be rewritten? |
| Object storage | How many objects/prefixes will exist? |
| Consumers | Can the required engines discover/prune it? |

The final decision is based on the combined evidence.

---

# 10. Filter Frequency

Suppose:

```text
70% → date filters
20% → date + country
5%  → category
5%  → customer equality
```

A date-related partition candidate may serve the dominant workload.

But do not stop there. Measure:

- partition count;
- bytes per partition;
- file count;
- skew;
- query latency;
- bytes read.

The important lesson is:

> **Optimize the workload distribution, not the most interesting individual query.**

---

# 11. Partition Stability

A partition field should generally be stable enough to avoid constant movement of records.

Example:

```text
customer_segment
```

may change frequently:

```text
bronze → silver → gold
```

If this is a physical partition key, a logical update can become a physical relocation.

Ask:

> **Can this value change after the record is written?**

Also consider:

- late-arriving data;
- updates;
- corrections;
- backfills;
- replay.

---

# 12. Partition Selectivity

Suppose:

```text
10,000 partitions
```

Query A selects:

```text
8 partitions
```

Query B selects:

```text
9,000 partitions
```

The dataset is partitioned in both cases, but Query A has much greater pruning potential.

Therefore:

> **A partition column is valuable only when the workload's filters eliminate meaningful physical scope.**

---

# 13. Partition Granularity

For time-based partitioning, common choices are:

```text
year
month
 day
 hour
```

Coarser:

```text
year
↓
fewer, larger partitions
```

Finer:

```text
hour
↓
more, smaller partitions
```

The trade-off is:

```text
pruning precision
        vs
partition/file/request overhead
```

---

# 14. Monthly vs Daily vs Hourly

Suppose a pipeline receives:

```text
10 TB/day
```

Ignoring skew for a moment:

### Daily

```text
~10 TB/partition/day
```

### Hourly

```text
~10 TB / 24 ≈ 417 GB/hour
```

### Monthly

A 30-day month is roughly:

```text
300 TB/month
```

The actual data distribution can be much less uniform.

The correct choice depends on common query windows and resulting file health.

---

# 15. Partition Volume and File Size

Partitioning interacts with writer behavior.

Example:

```text
Partition = 500 GB
```

If it creates:

```text
5 files
```

average size is about:

```text
100 GB/file
```

If it creates:

```text
500 files
```

average size is about:

```text
1 GB/file
```

The partition key stayed the same, but the operational shape changed dramatically.

File sizing is detailed in Topic 09.

---

# 16. Partition Values and Path Types

A path such as:

```text
month=09
```

contains text.

Conceptually:

```text
path text
   ↓
partition parser
   ↓
logical type
```

PyArrow supports explicit partition schemas. citeturn916880search2

Example:

```python
import pyarrow as pa
import pyarrow.dataset as ds

partitioning = ds.partitioning(
    pa.schema([
        ("year", pa.int16()),
        ("month", pa.int8()),
    ]),
    flavor="hive",
)
```

This makes the intended interpretation explicit.

---

# 17. Null Partition Values

A null partition value needs a path representation.

A common Hive-style representation is:

```text
__HIVE_DEFAULT_PARTITION__
```

Example:

```text
orders/country=__HIVE_DEFAULT_PARTITION__/
```

PyArrow currently documents `__HIVE_DEFAULT_PARTITION__` as the default `null_fallback` for `HivePartitioning`. citeturn916880search2

Do not assume every tool uses exactly the same sentinel.

Document your dataset contract.

---

# 18. Special Characters and URI Encoding

Partition values may contain:

- spaces;
- `/`;
- `=`;
- `%`;
- Unicode characters.

A slash is especially important because it is a path separator.

Therefore use a deliberate policy:

```text
logical value
   ↓
validate
   ↓
encode
   ↓
path segment
   ↓
read/decode
```

Current PyArrow `HivePartitioning` documents `segment_encoding="uri"` by default, with `"none"` available for leaving segments unchanged. citeturn916880search2

Do not invent a custom escape scheme casually.

---

# 19. Time-Based Partition Derivation

A production timestamp should be mapped to a partition deterministically.

```text
event timestamp
      ↓
timezone policy
      ↓
year/month/day derivation
      ↓
partition path
```

Possible bugs include:

- UTC/local date mismatch;
- midnight boundary errors;
- inconsistent timezone handling between normal ingestion and backfill;
- daylight-saving transitions.

The key rule is:

> **Use one documented partition-derivation policy and test it.**

---

# 20. PyArrow Partitioned Writes

Current PyArrow `dataset.write_dataset` supports partitioning via field names plus `partitioning_flavor="hive"`. It also supports controls including `max_rows_per_file`, `min_rows_per_group`, `max_rows_per_group`, and `existing_data_behavior`. citeturn916880search0

### Basic write

```python
from __future__ import annotations

import pyarrow as pa
import pyarrow.dataset as ds

table = pa.table({
    "order_id": [1, 2, 3, 4],
    "year": [2026, 2026, 2026, 2026],
    "month": [9, 9, 10, 10],
    "amount": [100.0, 200.0, 150.0, 250.0],
})

ds.write_dataset(
    table,
    base_dir="orders",
    format="parquet",
    partitioning=["year", "month"],
    partitioning_flavor="hive",
)
```

Possible structure:

```text
orders/
  year=2026/
    month=09/
    month=10/
```

Exact filenames and file counts depend on writer behavior.

---

# 21. Reading with PyArrow Dataset

```python
import pyarrow.dataset as ds

dataset = ds.dataset(
    "orders",
    format="parquet",
    partitioning="hive",
)

result = dataset.to_table(
    filter=(
        (ds.field("year") == 2026)
        & (ds.field("month") == 9)
    ),
    columns=["order_id", "amount"],
)
```

This combines:

```text
partition-aware filtering
+
column projection
```

Do not promise a fixed reduction in bytes or runtime.

---

# 22. Batch Reading a Partitioned Dataset

For large output:

```python
scanner = dataset.scanner(
    filter=(
        (ds.field("year") == 2026)
        & (ds.field("month") == 9)
    ),
    columns=["order_id", "amount"],
)

for batch in scanner.to_batches():
    process(batch)
```

Filtering and batch consumption solve different problems:

```text
filtering
→ reduce logical scan scope

batching
→ control materialization/memory
```

---

# 23. pandas `partition_cols=`

Current pandas documents:

```python
df.to_parquet(
    "orders",
    partition_cols=["year", "month"],
)
```

for writing a partitioned dataset. pandas also delegates Parquet writing to a selected backend such as PyArrow. citeturn807253search0

Example:

```python
import pandas as pd

frame = pd.DataFrame({
    "order_id": [1, 2, 3, 4],
    "year": [2026, 2026, 2026, 2026],
    "month": [9, 9, 10, 10],
    "amount": [100.0, 200.0, 150.0, 250.0],
})

frame.to_parquet(
    "orders",
    partition_cols=["year", "month"],
)
```

The convenience API does not eliminate the need to reason about partition design.

---

# 24. Polars Partitioned Writes

Current Polars documentation provides Hive-partitioned Parquet writes with `partition_by`:

```python
import polars as pl

df = pl.DataFrame({
    "order_id": [1, 2, 3, 4],
    "year": [2026, 2026, 2026, 2026],
    "month": [9, 9, 10, 10],
    "amount": [100.0, 200.0, 150.0, 250.0],
})

df.write_parquet(
    "orders",
    partition_by=["year", "month"],
)
```

Current Polars documentation labels this Hive partition-writing functionality as **unstable**, so pin and test the library version used by production. citeturn807253search6

Do not assume Polars' API is identical to pandas or PyArrow.

---

# 25. DuckDB `PARTITION_BY`

DuckDB currently supports Hive-partitioned Parquet writes using:

```sql
COPY orders
TO 'orders'
(
    FORMAT parquet,
    PARTITION_BY (year, month)
);
```

DuckDB documents `PARTITION_BY` as producing a Hive partitioned folder hierarchy. citeturn916880search4

If fields must be derived:

```sql
COPY (
    SELECT
        *,
        year(created_at) AS year,
        month(created_at) AS month
    FROM source_orders
)
TO 'orders'
(
    FORMAT parquet,
    PARTITION_BY (year, month)
);
```

Current DuckDB documentation shows this general pattern. citeturn807253search3

---

# 26. DuckDB Reading of Hive Partitions

```sql
SELECT *
FROM read_parquet(
    'orders/*/*/*.parquet',
    hive_partitioning = true
);
```

You can then filter:

```sql
SELECT
    year,
    month,
    SUM(amount) AS total_amount
FROM read_parquet(
    'orders/*/*/*.parquet',
    hive_partitioning = true
)
WHERE year = 2026
  AND month = 9
GROUP BY year, month;
```

DuckDB's current documentation states that partition columns can be read from the directory structure when Hive partitioning is enabled. citeturn807253search3

---

# 27. `EXPLAIN ANALYZE`

Use:

```sql
EXPLAIN ANALYZE
SELECT
    SUM(amount)
FROM read_parquet(
    'orders/*/*/*.parquet',
    hive_partitioning = true
)
WHERE year = 2026
  AND month = 9;
```

Inspect what your DuckDB version exposes:

- scan operators;
- filters;
- rows;
- timing;
- bytes/statistics where available.

Do not fabricate plan output.

DuckDB's `COPY` documentation also exposes file-writing statistics options such as `RETURN_STATS`; available metrics should be interpreted according to the version and operation. citeturn807253search2

---

# 28. Partitioning vs Sorting

Partitioning separates directories/files:

```text
partition by year/month
```

Sorting orders rows inside files:

```text
sort by country, customer_id
```

A candidate design can be:

```text
orders/year=2026/month=09/
    ↓
rows sorted by customer_id, created_at
```

Potential effect:

```text
partition pruning
+
intra-file locality
+
more useful row-group statistics
```

Sorting does not create additional directory paths.

---

# 29. Required `pickup_zone` Comparison

Compare:

### Strategy A

```text
partition by pickup_zone
```

with:

### Strategy B

```text
partition by year/month
sort by pickup_zone inside files
```

Measure:

- directories;
- files;
- average file size;
- query runtime;
- bytes read where available.

Do not assume either is better before testing.

---

# 30. High-Cardinality Partition Keys

Suppose:

```text
customer_id
→ 50 million distinct values
```

A path structure such as:

```text
customer_id=C000001/
customer_id=C000002/
...
```

is operationally suspicious.

Potential problems:

- huge directory count;
- many files;
- small files;
- high metadata/listing overhead;
- difficult backfills;
- difficult migration.

The important principle:

> **High-cardinality filtering does not automatically justify high-cardinality partitioning.**

---

# 31. Partition Skew

Skew means the partitions are not similarly sized.

Example:

```text
country=IN → 2 TB
country=US → 500 GB
country=UK → 100 GB
country=OTHER → 10 GB
```

A simple partition-count metric can hide the fact that one partition dominates.

Measure:

```text
rows per partition
bytes per partition
files per partition
```

A useful diagnostic is:

```text
max partition size / median partition size
```

Treat this as an investigative metric, not a universal pass/fail threshold.

---

# 32. Multi-Level Partition Explosion

Suppose:

```text
10 years
12 months
31 days
100 regions
```

Potential combinations:

```text
10 × 12 × 31 × 100
= 372,000
```

This does not mean all 372,000 paths will exist.

It demonstrates how quickly partition dimensions multiply.

Add another dimension such as 50 categories:

```text
372,000 × 50
= 18,600,000
```

More dimensions therefore require a strong workload justification.

---

# 33. Multi-Level Partitioning

A path such as:

```text
year/
  month/
    day/
      country/
```

may look precise but can create:

- deep paths;
- many empty combinations;
- many files;
- difficult backfills;
- metadata complexity.

Rule:

> **Do not add a partition level unless its pruning benefit justifies the additional physical complexity.**

---

# 34. Bucketing — Awareness

Bucketing groups high-cardinality values into a bounded number of buckets.

Conceptually:

```text
customer_id
    ↓
hash
    ↓
bucket 0..N-1
```

This differs from:

```text
partition by customer_id
```

because the number of buckets can be bounded.

Potential uses include certain:

- equality filters;
- join patterns.

Detailed Spark bucketing belongs later in the roadmap.

---

# 35. Z-Ordering / Clustering — Awareness

Clustering tries to improve data locality across multiple query dimensions.

Conceptually:

```text
date + country + customer_id
           ↓
   improved locality
```

This can reduce the pressure to encode every dimension as a directory partition.

Z-ordering is not the same thing as ordinary sorting. Detailed implementation belongs to later lakehouse topics.

---

# 36. Object Storage

Object storage commonly provides a hierarchical-looking namespace over object keys.

Conceptually:

```text
bucket/orders/year=2026/month=09/part-0.parquet
```

is an object key/prefix organization rather than necessarily a POSIX directory tree.

Partition design can therefore affect:

- object count;
- prefix count;
- LIST requests;
- metadata requests;
- planning time;
- storage/network cost.

Do not assume all object stores have identical behavior or limits.

---

# 37. Directory Listing and Request Costs

A very large partition tree can require substantial metadata discovery.

Example:

```text
2 million objects
```

Even if a query ultimately reads few bytes, discovering all candidate objects can create overhead.

Therefore evaluate:

```text
data scan cost
vs
metadata/request cost
```

This is especially important in remote object storage.

---

# 38. Prefix and Request-Rate Considerations

Object stores have request-rate characteristics, but exact limits vary by implementation, region, account, and configuration.

Do not memorize a universal numeric limit.

Instead ask:

```text
How many objects will exist?
How many prefixes?
How many LIST operations?
How many GET/HEAD operations?
What planning behavior does the engine show?
```

---

# 39. Changing a Partition Scheme

Suppose the current layout is:

```text
orders/customer_id=...
```

and the target is:

```text
orders/year=.../month=...
```

The directory path itself encodes the physical layout.

Therefore, a plain-directory migration generally needs:

```text
Profile
 ↓
Design new layout
 ↓
Benchmark
 ↓
Rewrite
 ↓
Validate
 ↓
Cut over
```

Changing a partition scheme has costs in:

- compute;
- I/O;
- temporary storage;
- validation;
- reader migration;
- rollback.

---

# 40. Hidden Partitioning — Awareness

Modern table formats can separate:

```text
logical table semantics
```

from:

```text
physical partition path layout
```

This is commonly called hidden partitioning.

The benefit is reduced coupling between query logic and directory names.

Detailed implementation is deferred to later lakehouse topics.

---

# 41. Partition Evolution — Awareness

Some modern table formats can evolve partition transforms over time.

Conceptually:

```text
historical data → old physical transform
new data        → new physical transform
logical table   → one queryable table abstraction
```

This reduces the need to treat a directory scheme as a permanent public contract.

Detailed partition evolution belongs to later lakehouse material.

---

# 42. Idempotent Partition Overwrite

Define:

> **An idempotent overwrite produces the same logical dataset state when the same input is successfully applied repeatedly.**

Bad:

```text
Run 1 → append
Run 2 → append same batch
Result → duplicates
```

Desired:

```text
Run 1 → replace partition
Run 2 → replace same partition
Result → same logical state
```

---

# 43. `existing_data_behavior` in PyArrow

Current PyArrow `write_dataset` documents:

```text
error
overwrite_or_ignore
delete_matching
```

The `delete_matching` behavior is specifically useful for partitioned writes because the first time an output partition is encountered, its destination directory can be deleted before replacement files are written. citeturn916880search0

This is a writer behavior setting, not a full transaction system.

---

# 44. Safe Temporary Output

A safer conceptual publication flow is:

```text
Incoming batch
      ↓
Identify affected partitions
      ↓
Write temporary output
      ↓
Validate
      ↓
Replace affected partitions
      ↓
Verify
```

Why?

Because a crash during direct publication can leave:

- partial output;
- mixed old/new files;
- incomplete partitions.

---

# 45. Plain Directories Are Not Transactional Tables

A directory tree does not inherently provide:

- snapshot isolation;
- atomic multi-file transactions;
- concurrent-writer coordination;
- versioned table snapshots.

Therefore:

> **A safe filesystem workflow is not equivalent to a transactional lakehouse table.**

Later table-format modules address this problem at greater depth.

---

# 46. Reference Implementation — `overwrite_partitions(...)`

The roadmap asks for a function conceptually named:

```python
overwrite_partitions(df, root, partition_cols)
```

The following is an **educational local-filesystem implementation**. It is intentionally not presented as an object-store transaction protocol.

```python
from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

import pyarrow as pa
import pyarrow.dataset as ds


def _distinct_partition_keys(
    table: pa.Table,
    partition_cols: list[str],
) -> list[tuple[object, ...]]:
    rows = table.select(partition_cols).to_pylist()
    return sorted(
        {
            tuple(row[column] for column in partition_cols)
            for row in rows
        },
        key=lambda key: tuple(
            "" if value is None else str(value)
            for value in key
        ),
    )


def _partition_dir(
    root: Path,
    partition_cols: list[str],
    values: tuple[object, ...],
) -> Path:
    path = root

    for column, value in zip(partition_cols, values):
        if value is None:
            rendered = "__HIVE_DEFAULT_PARTITION__"
        else:
            rendered = str(value)

        # Production code should apply a documented path-encoding policy.
        if "/" in rendered or "\x00" in rendered:
            raise ValueError(
                f"Unsafe partition value for {column!r}: {rendered!r}"
            )

        path = path / f"{column}={rendered}"

    return path


def overwrite_partitions(
    df: pa.Table,
    root: str | Path,
    partition_cols: list[str],
) -> None:
    """Replace exactly the partitions represented in df.

    Teaching implementation for a local filesystem.
    It is not a substitute for transactional table-format commits.
    """
    root_path = Path(root)
    root_path.mkdir(parents=True, exist_ok=True)

    missing = set(partition_cols) - set(df.column_names)
    if missing:
        raise ValueError(
            f"Missing partition columns: {sorted(missing)}"
        )

    keys = _distinct_partition_keys(df, partition_cols)
    if not keys:
        return

    run_id = uuid4().hex
    temp_root = root_path.parent / (
        f".{root_path.name}.tmp-{run_id}"
    )

    try:
        # 1. Write the complete replacement outside the published root.
        ds.write_dataset(
            df,
            base_dir=temp_root,
            format="parquet",
            partitioning=partition_cols,
            partitioning_flavor="hive",
            existing_data_behavior="error",
        )

        # 2. Validate the temporary dataset before publication.
        temp_dataset = ds.dataset(
            temp_root,
            format="parquet",
            partitioning="hive",
        )

        if temp_dataset.count_rows() != df.num_rows:
            raise RuntimeError(
                "Temporary row count does not match input."
            )

        # 3. Replace only affected partitions.
        for key in keys:
            source = _partition_dir(
                temp_root,
                partition_cols,
                key,
            )
            target = _partition_dir(
                root_path,
                partition_cols,
                key,
            )

            if not source.exists():
                raise RuntimeError(
                    f"Missing expected temporary partition: {source}"
                )

            target.parent.mkdir(parents=True, exist_ok=True)
            backup = target.parent / (
                f".{target.name}.backup-{run_id}"
            )

            if target.exists():
                target.rename(backup)

            try:
                source.rename(target)
            except Exception:
                if backup.exists() and not target.exists():
                    backup.rename(target)
                raise

            if backup.exists():
                shutil.rmtree(backup)

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
```

### What it does

```text
incoming batch
   ↓
distinct partition keys
   ↓
temporary write
   ↓
validate
   ↓
replace only affected partitions
```

### What it does not guarantee

It does not provide full distributed transactions or concurrent-reader isolation, especially on object storage.

---

# 47. Backfills and Reruns

Suppose three monthly partitions need correction:

```text
2026-01
2026-02
2026-03
```

A good backfill should:

1. identify exactly those partition keys;
2. regenerate their data deterministically;
3. write replacement data safely;
4. validate row counts and key relationships;
5. replace only affected partitions;
6. leave unrelated partitions untouched;
7. support safe retry.

Partitioning is therefore also a **maintenance-scope decision**.

---

# 48. Empty and Large Partitions

A healthy partition scheme should avoid both extremes.

Too coarse:

```text
huge partition
→ broad scans
→ large rewrite scope
```

Too fine:

```text
many tiny partitions
→ many files
→ more metadata/listing
→ small-file risk
```

The target is not "maximum partition precision."

The target is:

> **meaningful pruning with manageable physical organization.**

---

# 49. Five Required Query Patterns

Use these in design reviews and benchmarks.

## Query 1 — Date Range

```sql
SELECT SUM(amount)
FROM orders
WHERE created_at >= DATE '2026-01-01'
  AND created_at <  DATE '2026-02-01';
```

Reason about candidate time partitions.

## Query 2 — Date + Region

```sql
SELECT COUNT(*)
FROM orders
WHERE created_at >= DATE '2026-01-01'
  AND created_at <  DATE '2026-02-01'
  AND region = 'east';
```

Ask whether region deserves a partition level or whether intra-file ordering is enough.

## Query 3 — Customer Equality

```sql
SELECT *
FROM orders
WHERE customer_id = 'C123456';
```

Ask whether customer-level partitioning is operationally sensible.

## Query 4 — Full History

```sql
SELECT product_category, SUM(amount)
FROM orders
GROUP BY product_category;
```

This can still require most or all partitions.

## Query 5 — Mixed Filter

```sql
SELECT country, product_category, SUM(amount)
FROM orders
WHERE created_at >= DATE '2026-08-01'
  AND created_at <  DATE '2026-09-01'
GROUP BY country, product_category;
```

Use it to compare time pruning with intra-file locality.

---

# 50. Partition Estimate Worksheet

Before running queries, record:

| Query | Filter | Estimated Partitions | Estimated Files | Estimated Bytes |
| --- | --- | ---: | ---: | ---: |
| Q1 | date range | | | |
| Q2 | date + region | | | |
| Q3 | customer | | | |
| Q4 | full history | | | |
| Q5 | date + aggregation | | | |

Then run the benchmark and add:

| Query | Actual | Gap Explanation |
| --- | --- | --- |
| Q1 | | |
| Q2 | | |
| Q3 | | |
| Q4 | | |
| Q5 | | |

The gap is often the most educational part.

---

# 51. Required Partition Design Lab — `partition_design.py`

The roadmap requires an exercise named:

```text
partition_design.py
```

Because this module must not create helper files, the implementation is shown here as a code block only.

Compare:

1. no partitioning;
2. `year/month`;
3. `year/month/day`;
4. `pickup_zone`.

---

# 52. Lab Dataset

Use NYC taxi data or an orders dataset with at least:

```text
trip_id/order_id
pickup_datetime/created_at
year
month
day
pickup_zone/country
numeric measure
high-cardinality candidate
```

If generating synthetic data, use a fixed seed.

Example:

```python
from __future__ import annotations

import random
from datetime import datetime, timedelta

import pyarrow as pa
import pyarrow.compute as pc


def make_dataset(
    rows: int = 2_000_000,
    seed: int = 42,
) -> pa.Table:
    rng = random.Random(seed)

    zones = [f"zone_{i:03d}" for i in range(1, 11)]
    weights = [50, 15, 10, 8, 5, 4, 3, 2, 2, 1]
    start = datetime(2026, 1, 1)

    trip_ids = list(range(1, rows + 1))
    timestamps = [
        start + timedelta(
            minutes=rng.randrange(90 * 24 * 60)
        )
        for _ in range(rows)
    ]
    pickup_zones = [
        rng.choices(zones, weights=weights, k=1)[0]
        for _ in range(rows)
    ]
    passenger_count = [
        rng.randint(1, 5)
        for _ in range(rows)
    ]
    fare_amount = [
        round(rng.uniform(5, 150), 2)
        for _ in range(rows)
    ]

    table = pa.table({
        "trip_id": pa.array(trip_ids, type=pa.int64()),
        "pickup_datetime": pa.array(timestamps),
        "pickup_zone": pa.array(pickup_zones),
        "passenger_count": pa.array(
            passenger_count,
            type=pa.int16(),
        ),
        "fare_amount": pa.array(
            fare_amount,
            type=pa.float64(),
        ),
    })

    return table.append_column(
        "year",
        pc.year(table["pickup_datetime"]),
    ).append_column(
        "month",
        pc.month(table["pickup_datetime"]),
    ).append_column(
        "day",
        pc.day(table["pickup_datetime"]),
    )
```

The deliberately skewed zone distribution makes partition-skew analysis useful.

---

# 53. Lab Writer

```python
from pathlib import Path
import shutil

import pyarrow.dataset as ds


def write_strategy(
    table,
    root: Path,
    partition_cols: list[str] | None,
) -> None:
    if root.exists():
        shutil.rmtree(root)

    kwargs = {
        "data": table,
        "base_dir": root,
        "format": "parquet",
        "max_rows_per_file": 250_000,
        "min_rows_per_group": 50_000,
        "max_rows_per_group": 250_000,
    }

    if partition_cols:
        kwargs["partitioning"] = partition_cols
        kwargs["partitioning_flavor"] = "hive"

    ds.write_dataset(**kwargs)
```

The row/file settings are experimental controls, not organization-wide recommendations.

---

# 54. Lab Strategies

```python
strategies = {
    "none": [],
    "year_month": ["year", "month"],
    "year_month_day": ["year", "month", "day"],
    "pickup_zone": ["pickup_zone"],
}
```

Run them with the exact same dataset and writer settings.

```python
from pathlib import Path

for name, partition_cols in strategies.items():
    write_strategy(
        table,
        Path("partition_lab") / name,
        partition_cols,
    )
```

---

# 55. Lab Layout Statistics

```python
from pathlib import Path
from statistics import mean


def layout_stats(root: str | Path) -> dict[str, int | float]:
    root = Path(root)
    files = list(root.rglob("*.parquet"))
    sizes = [path.stat().st_size for path in files]
    directories = {path.parent for path in files}

    return {
        "directories": len(directories),
        "files": len(files),
        "total_bytes": sum(sizes),
        "avg_file_bytes": mean(sizes) if sizes else 0,
        "min_file_bytes": min(sizes) if sizes else 0,
        "max_file_bytes": max(sizes) if sizes else 0,
    }
```

Record:

| Strategy | Directories | Files | Total Bytes | Avg File Size | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| None | | | | | | |
| Year/Month | | | | | | |
| Year/Month/Day | | | | | | |
| Pickup Zone | | | | | | |

---

# 56. Benchmark Queries

For each strategy, run the same logical queries.

### Q1 — Date

```sql
SELECT
    COUNT(*) AS rows,
    SUM(fare_amount) AS total_fare
FROM read_parquet(
    'PATH_PATTERN',
    hive_partitioning = true
)
WHERE year = 2026
  AND month = 1;
```

### Q2 — Date + zone

```sql
SELECT
    pickup_zone,
    COUNT(*)
FROM read_parquet(
    'PATH_PATTERN',
    hive_partitioning = true
)
WHERE year = 2026
  AND month = 1
  AND pickup_zone = 'zone_001'
GROUP BY pickup_zone;
```

### Q3 — Full history

```sql
SELECT
    pickup_zone,
    SUM(fare_amount)
FROM read_parquet(
    'PATH_PATTERN',
    hive_partitioning = true
)
GROUP BY pickup_zone;
```

### Q4 — Point lookup

```sql
SELECT *
FROM read_parquet(
    'PATH_PATTERN',
    hive_partitioning = true
)
WHERE trip_id = 123456;
```

### Q5 — Two-month filter

```sql
SELECT
    pickup_zone,
    SUM(fare_amount)
FROM read_parquet(
    'PATH_PATTERN',
    hive_partitioning = true
)
WHERE year = 2026
  AND month BETWEEN 1 AND 2
GROUP BY pickup_zone;
```

Do not use one universal glob blindly. The correct path pattern differs by layout depth.

---

# 57. DuckDB `EXPLAIN ANALYZE` Lab

Run:

```sql
EXPLAIN ANALYZE
SELECT
    SUM(fare_amount)
FROM read_parquet(
    'partition_lab/year_month/**/*.parquet',
    hive_partitioning = true
)
WHERE year = 2026
  AND month = 1;
```

Repeat for:

```text
none
year_month
year_month_day
pickup_zone
```

Inspect the real output.

Record observations, not invented metrics.

---

# 58. MinIO Experiment

Use:

```text
PyArrow / DuckDB
       ↓
partitioned Parquet
       ↓
MinIO
       ↓
DuckDB
       ↓
EXPLAIN ANALYZE
```

The purpose is to expose object-store behavior that a local SSD benchmark may hide.

MinIO is S3-compatible, but it is not identical to every production cloud object store.

Keep credentials in environment variables.

Do not hard-code credentials in scripts.

---

# 59. Required Benchmark Table

| Strategy | Directories | Files | Avg File Size | Query Runtime | Bytes Read | Planning Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| None | | | | | | |
| Year/Month | | | | | | |
| Year/Month/Day | | | | | | |
| Pickup Zone | | | | | | |

Populate only from actual runs.

---

# 60. Pickup Zone vs Year/Month + Sorting Experiment

### Design A

```text
partition by pickup_zone
```

### Design B

```text
partition by year/month
sort by pickup_zone, pickup_datetime
```

Keep constant:

- dataset;
- schema;
- compression;
- row-group settings;
- engine;
- query;
- storage;
- machine.

Measure:

```text
directories
files
average file size
query runtime
bytes read
```

The experiment answers whether another partition level provides enough incremental pruning to justify its physical cost.

---

# 61. Partitioning and Full Scans

A query such as:

```sql
SELECT COUNT(*) FROM orders;
```

requires the full logical dataset.

Partition pruning may eliminate nothing.

This is not a failure of partitioning.

It demonstrates the correct scope:

> **Partitioning is most valuable for selective workloads.**

A full-history aggregation may instead benefit primarily from column pruning, compression, parallel scanning, row-group layout, and other physical optimizations.

---

# 62. Partitioning and Point Lookups

A partitioned analytical dataset is not automatically a key-value database.

A query such as:

```sql
WHERE customer_id = 'C123'
```

can still be expensive if the physical layout does not align with that predicate.

Do not turn a path-partitioned lake into an accidental operational lookup system.

---

# 63. Debugging — Partition Pruning Does Not Happen

### Symptom

A filter on a partition column does not improve the scan.

### Possible causes

- partition discovery is incorrect;
- filter type differs from partition type;
- query expression is not recognized;
- filter still selects many partitions;
- file count is large;
- engine behavior differs by version.

### Inspect

```text
physical paths
partition schema
dataset schema
query plan
filter expression
```

### Measure

Compare the same query against:

```text
unpartitioned
vs
partitioned
```

### Lesson

A partition only helps when the reader can exploit it for the real predicate.

---

# 64. Debugging — Millions of Files

### Symptom

The partitioned dataset has far more files than expected.

### Likely causes

- high-cardinality key;
- excessive partition levels;
- small input batches;
- writer parallelism;
- overly small rows/file setting.

### Inspect

```text
partitions
files/partition
rows/file
bytes/file
writer parallelism
```

### Fix candidates

- coarser partitioning;
- larger batches;
- sorting instead of another partition level;
- controlled file sizing;
- compaction.

Topic 09 covers the compaction side in depth.

---

# 65. Debugging — Queries Still Slow

Possible causes:

- filter selects many partitions;
- too many files remain;
- files are huge;
- poor row-group layout;
- no useful sorting/locality;
- object-store planning overhead;
- engine overhead.

Inspect:

```text
partitions touched
files touched
bytes read
row-group behavior
query plan
```

---

# 66. Debugging — Huge Partition

### Symptom

One partition is much larger than others.

### Possible causes

- skew;
- changing business distribution;
- hot key;
- inappropriate partition dimension.

Measure:

```text
rows/partition
bytes/partition
files/partition
```

Then decide whether:

- granularity should change;
- sorting would help;
- a different partition key is needed;
- skew should be accepted as part of the workload.

---

# 67. Debugging — Strange Partition Paths

Investigate:

- null fallback;
- URI encoding;
- special characters;
- inconsistent formatting;
- type inference.

Inspect:

```text
raw path
partition schema
encoding policy
null policy
```

Never normalize paths by ad hoc string replacement without understanding the reader's parser.

---

# 68. Debugging — Rerun Doubled the Data

### Symptom

A retry creates duplicate files/data.

### Likely cause

The operation was append-oriented rather than replacement-oriented.

### Inspect

- filename pattern;
- overwrite behavior;
- incoming partition keys;
- rerun semantics.

### Lesson

Write semantics must explicitly distinguish:

```text
append
```
from:

```text
replace partition
```

---

# 69. Debugging — Backfill Touched the Wrong Day

Likely causes:

- timezone mismatch;
- incorrect date boundary;
- wrong timestamp derivation;
- inconsistent partition function.

Use one deterministic partition-derivation function for both normal and backfill pipelines.

---

# 70. Common Mistakes

## 1. Partitioning by high-cardinality IDs

Creates path/file explosion.

## 2. Partitioning by columns nobody filters on

Creates complexity without pruning value.

## 3. Partitioning too finely

Creates too many paths/files.

## 4. Partitioning too coarsely

Can make pruning too weak.

## 5. Adding every filtered column as a partition

Ignores cardinality, skew, and file growth.

## 6. Adding many levels without estimating combinations

Creates multiplicative complexity.

## 7. Ignoring skew

A few giant partitions can dominate processing.

## 8. Assuming more partitions always means faster queries

False.

## 9. Assuming pruning always happens automatically

The engine must recognize and exploit the partitioning.

## 10. Ignoring path typing

String path values can have different logical interpretations.

## 11. Ignoring null partition values

Nulls need a documented path representation.

## 12. Ignoring path encoding

Special characters can change path semantics.

## 13. Making overwrite non-idempotent

Retries can duplicate data.

## 14. Writing directly to published partitions

A crash can expose partial state.

## 15. Ignoring object-store listing/request cost

More data pruning can coexist with worse planning overhead.

## 16. Treating partitioning as sorting

They operate at different physical levels.

## 17. Treating sorting as a complete substitute for partitioning

Some date workloads still benefit from coarse path pruning.

## 18. Benchmarking one query

You can overfit to a single workload.

## 19. Measuring only runtime

Also inspect files, bytes, and layout health.

## 20. Ignoring target file sizes

Partitioning and file creation interact.

## 21. Ignoring migration cost

A path layout can become a consumer contract.

## 22. Comparing different datasets

Invalidates most conclusions.

---

# 71. Partitioning vs Sorting / Clustering

| Requirement | Partitioning | Sorting / Clustering |
| --- | --- | --- |
| Eliminate whole directories/files | Strong fit | Not directly |
| Improve row-group locality | Indirect | Strong fit |
| Avoid high-cardinality path explosion | Helpful | Often useful |
| Coarse time pruning | Strong fit | Can help inside files |
| Several query dimensions | Can create path explosion | Often attractive |
| Frequently changing key | Can be operationally awkward | Potentially easier |
| Stable low-cardinality key | Candidate | Also possible |

No row in this table is a universal recommendation.

---

# 72. Partitioning vs Compression

These optimize different physical layers:

```text
Partitioning
→ fewer physical locations considered

Compression
→ fewer bytes stored/transferred within the chosen data
```

A good lake layout may combine:

```text
partition pruning
+
row-group/page pruning
+
column pruning
+
encoding
+
compression
```

---

# 73. Partitioning vs Row-Group Statistics

```text
Partition pruning
→ skip directories/files

Row-group statistics
→ skip regions inside files
```

A time partition plus sorted timestamps can potentially provide both.

Do not assume every engine uses every possible optimization.

---

# 74. Partitioning and Data Contracts

Document at least:

```text
partition columns
partition granularity
partition derivation rules
null representation
path encoding
overwrite semantics
backfill scope
```

If consumers hard-code object paths, the physical layout is effectively an API.

That makes future migration more expensive.

---

# 75. Partition Migration Pattern

```text
Old Layout
   ↓
Inventory Consumers
   ↓
Profile Workload
   ↓
Design Candidate
   ↓
Benchmark
   ↓
Rewrite
   ↓
Validate
   ↓
Parallel Compare
   ↓
Cutover
```

Do not delete the old layout until the consumer transition and validation plan are complete.

---

# 76. Production Observability

Monitor:

- partition count;
- files per partition;
- partition-size distribution;
- file-size distribution;
- query bytes read;
- query latency;
- pruning effectiveness where exposed;
- failed partition replacements;
- retry frequency;
- backfill duration.

Useful signals include:

```text
partition count suddenly rises
average file size suddenly falls
one partition becomes huge
bytes read for a common filter increases
```

---

# 77. Partition Health Report

Use a simple report:

| Metric | Value |
| --- | ---: |
| Partitions | |
| Files | |
| Total GB | |
| Avg file MB | |
| Min file MB | |
| Max file MB | |
| Median partition GB | |
| Max partition GB | |
| Skew indicator | |

Do not use the average alone.

A small number of tiny files can be hidden by a large average.

---

# 78. Production Architecture Pattern

```text
Source Systems
      ↓
Landing
      ↓
Bronze
      ↓
Validation
      ↓
Partition Derivation
      ↓
Typed Analytical Dataset
      ↓
Partitioned Parquet
      ↓
Object Storage
      ↓
Query Engine
      ↓
Analytics
```

Backfill:

```text
Backfill Input
      ↓
Affected Partitions
      ↓
Temporary Output
      ↓
Validation
      ↓
Replacement
      ↓
Verification
```

---

# 79. Production Case Study

A retail lake contains:

```text
3 years of orders
5 billion rows
```

Workload:

```text
mostly date-range queries
some country filters
rare customer lookups
```

Current layout:

```text
orders/customer_id=...
```

Symptoms:

- too many directories;
- too many files;
- small files;
- object-storage listing overhead;
- slow queries.

### Candidate designs

```text
A. no partitioning
B. year/month
C. year/month/day
D. country
E. year/month + sort by country/customer_id
```

Benchmark:

```text
partition count
file count
file-size distribution
query runtime
bytes read
backfill cost
object-store behavior
```

The correct design is whichever satisfies the workload and operational constraints with measured evidence.

---

# 80. Architecture Review Example

A proposal says:

```text
Partition by:
customer_id
country
category
hour
```

Reason:

> "These are the fields people filter on."

A senior review should ask:

```text
What is cardinality?
What is selectivity?
How many combinations exist?
What is the skew?
How many files result?
How much metadata exists?
How often are these filters used?
Can sorting provide locality instead?
What is the backfill scope?
What does the benchmark show?
```

This is stronger than approving a path pattern by intuition.

---

# 81. Production Partitioning Guideline

Example guideline — **not a universal organization-wide standard**:

```text
1. Partition only for measurable pruning benefits.
2. Prefer stable, commonly filtered dimensions.
3. Avoid high-cardinality partition keys.
4. Validate granularity against data volume.
5. Estimate partition and file counts before implementation.
6. Monitor partition skew.
7. Make partition replacement idempotent.
8. Use temporary output plus validation for production rewrites.
9. Consider sorting/clustering before adding another partition level.
10. Account for object-storage listing/request behavior.
11. Benchmark representative queries.
12. Record runtime, bytes read, file count, and file-size distribution.
13. Document exceptions and evidence.
14. Re-evaluate when workload or infrastructure changes.
```

---

# 82. Partition Policy Template

Use this as a reusable artifact inside an engineering repository:

```text
Dataset:
Primary workload:
Secondary workloads:

Common filters:
Partition columns:
Partition transforms:
Granularity:

Cardinality:
Estimated partition count:
Estimated files:
Expected file size:

Skew risk:
Sorting/clustering:
Null policy:
Path encoding:

Overwrite policy:
Backfill policy:
Retry/idempotency policy:

Object-storage considerations:

Benchmark:
Query 1:
Query 2:
Query 3:
Query 4:
Query 5:

Decision:
Reason:
Exceptions:
Review trigger:
Owner:
```

Do not populate fields with invented values.

---

# 83. Required One-Page Evidence Report

```text
PARTITIONING EVIDENCE REPORT

Dataset:
Workload:
Candidate layouts:

Partition counts:
File counts:
Partition size distribution:
File size distribution:

Query results:
Q1:
Q2:
Q3:
Q4:
Q5:

Bytes read:
Planning observations:
Skew observations:

Backfill impact:
Object-storage observations:

Decision:
Evidence:
Exceptions:
```

---

# 84. Testing Partitioned Datasets

Production-oriented tests should verify:

### Partition path correctness

`created_at` maps to the expected year/month/day.

### Row count conservation

```text
input rows = sum(output rows)
```

for the intended write semantics.

### Query equivalence

A partitioned dataset and a reference unpartitioned dataset return the same logical result.

### Idempotency

Running the same replacement twice does not duplicate logical data.

### Unaffected partitions

Partitions outside the update scope remain unchanged.

### Null handling

Null partition values are represented and interpreted according to the documented policy.

### Path encoding

Special-character values round-trip correctly.

---

# 85. Example Correctness Test

```python
import pyarrow.dataset as ds


def count_rows(path: str) -> int:
    return ds.dataset(
        path,
        format="parquet",
        partitioning="hive",
    ).count_rows()


before = count_rows("orders")

# Run the replacement workflow here.

after = count_rows("orders")

assert after >= 0
```

In a real test, assert the exact expected count derived from the business operation. The example intentionally does not fabricate a value.

---

# 86. Partition Assignment Validation

For a timestamp partition:

```python
def derive_partition(ts):
    return {
        "year": ts.year,
        "month": ts.month,
        "day": ts.day,
    }
```

Test that the values used to construct the path agree with the source timestamp under the project's explicit timezone policy.

The exact vectorized implementation depends on whether timestamps are timezone-aware and which library is used.

---

# 87. Data Quality Rules

For every partitioned pipeline, validate:

```text
partition values
row counts
primary keys
partition boundaries
null semantics
aggregate reconciliation
```

For a backfill:

```text
affected partitions only
```

should change.

---

# 88. Workload Weighting

A workload could be:

```text
Query A → 50%
Query B → 20%
Query C → 15%
Query D → 10%
Query E → 5%
```

A conceptual scoring model is:

```text
workload value
=
Σ(
    query_frequency
    ×
    query_cost
    ×
    potential_savings
)
```

This is a reasoning framework, not an exact billing formula.

---

# 89. Partitioning and Maintenance

Partitioning affects:

- ingestion;
- backfills;
- retention;
- corrections;
- compaction;
- deletes;
- migration.

That means a partition design should answer two questions:

```text
How does this improve reads?

How does this affect maintenance?
```

A read-optimized layout with impossible backfills is not a production-ready design.

---

# 90. Partitioning and Retention

Time partitions can make retention operations easy to scope:

```text
remove old year/month partitions
```

But lifecycle operations must consider:

- late-arriving data;
- legal retention requirements;
- dependencies;
- recovery requirements.

Partitioning can simplify lifecycle work, but it does not replace governance.

---

# 91. Partitioning and Incremental Pipelines

A typical incremental flow is:

```text
watermark
   ↓
extract changes
   ↓
derive partition
   ↓
write
   ↓
validate
   ↓
commit
```

If partition boundaries match incremental maintenance boundaries, reruns and backfills can become easier to reason about.

---

# 92. Partitioning and Late Arrivals

An event created on:

```text
2026-01-15
```

may arrive on:

```text
2026-09-28
```

If partitioned by event date, the pipeline may need to update the historical January partition.

That is why the design must include:

```text
late data
backfill
replacement
retry
```

from the beginning.

---

# 93. Partition Migration Cost

A physical path is often referenced by:

- ETL jobs;
- SQL views;
- notebooks;
- cleanup scripts;
- monitoring;
- permissions;
- downstream teams.

Changing:

```text
year/month/day
```

to:

```text
year/month
```

may therefore be both a rewrite and a consumer-migration project.

---

# 94. Partition Scheme as an API

If downstream teams directly use:

```text
s3://bucket/orders/year=2026/month=09/
```

the path structure has become part of the interface.

This creates coupling.

Table abstractions and hidden partitioning can reduce this coupling.

---

# 95. Object Storage and File Count

A partition design can produce:

```text
few partitions
many files
```

or:

```text
many partitions
many files
```

Object-store cost and planning behavior are therefore linked to file count, not just partition count.

Do not use:

```text
number of partitions
```

as a substitute for:

```text
number of physical objects
```

---

# 96. `WRITE_PARTITION_COLUMNS` Awareness

DuckDB's current `COPY` documentation exposes:

```text
WRITE_PARTITION_COLUMNS
```

for partitioned writes. It controls whether partition columns are written into the output files as well as represented in the directory path. citeturn807253search2

This reinforces:

```text
path-derived partition information
≠
ordinary file-column storage
```

The right choice depends on consumer needs.

---

# 97. `FILENAME_PATTERN` Awareness

DuckDB supports `FILENAME_PATTERN` for partitioned writes, with tokens including `{i}` and UUID variants in current documentation. citeturn916880search4

Example:

```sql
COPY orders
TO 'orders'
(
    FORMAT parquet,
    PARTITION_BY (year, month),
    FILENAME_PATTERN 'orders_{i}'
);
```

Filename control is useful operationally, but it does not fix a poor partition strategy.

---

# 98. Remote-Write Semantics

DuckDB's current partitioned-write documentation distinguishes local and remote filesystem behavior for overwrites. Do not assume local-directory replacement semantics carry over unchanged to object storage. citeturn916880search4

General lesson:

> **Storage semantics are part of the physical-layout design.**

---

# 99. Partitioning vs Query Shape

A dataset can have several workloads:

```text
date range
country filter
customer lookup
full scan
aggregate
```

A single partition scheme may help some and do little for others.

Therefore benchmark multiple query classes.

---

# 100. Why More Partitions Can Be Worse

Suppose Strategy A:

```text
100 directories
1,000 files
```

Strategy B:

```text
10,000 directories
10,000 files
```

and query latency is:

```text
A → 2.0 sec
B → 1.9 sec
```

Do not conclude B is automatically better.

You must also ask:

- how much more metadata exists?
- how many requests occur?
- how much maintenance is added?
- how much better is the workload overall?

---

# 101. New Partitioning Scheme Evaluation

Use:

```text
Existing workload
   ↓
Profile
   ↓
New partition hypothesis
   ↓
Representative data
   ↓
Benchmark
   ↓
File/partition health
   ↓
Object-store evaluation
   ↓
Backfill/migration assessment
   ↓
Decision
```

Do not migrate first and benchmark after.

---

# 102. Production Decision Logic

```text
Requirements
    +
Workload
    +
Cardinality
    +
Selectivity
    +
Granularity
    +
Skew
    +
File health
    +
Object storage
    +
Backfills
    +
Idempotency
    +
Measurements
    ↓
Defensible partition decision
```

---

# 103. Senior Engineer Mental Model

A senior engineer asks:

```text
What problem are we solving?
        ↓
Which queries create the cost?
        ↓
Which filters dominate?
        ↓
How selective are they?
        ↓
How many distinct values exist?
        ↓
How stable are they?
        ↓
How much data lands per value?
        ↓
How many files will result?
        ↓
What skew exists?
        ↓
Could sorting help instead?
        ↓
What does object storage add?
        ↓
How will retries/backfills work?
        ↓
What does the benchmark show?
```

Only then choose the physical layout.

---

# 104. Production Code Review Exercise

Review this proposal:

```text
partition by:
customer_id
country
category
hour
```

Questions:

1. What are the cardinalities?
2. What fraction of queries use each filter?
3. What is the theoretical partition-combination space?
4. How skewed are the values?
5. What file count is expected?
6. What average and tail file sizes result?
7. What object-store listing overhead is expected?
8. Can sorting provide sufficient locality?
9. What will backfills touch?
10. What benchmark evidence supports the design?

A production review must answer those questions before standardizing the path.

---

# 105. Practical Scenario 1 — Daily Analytics

Dataset:

```text
2 billion rows
```

Workload:

```text
most queries filter by event date
```

Evaluate:

- month vs day;
- partition volume;
- file count;
- backfill scope;
- query windows.

The answer comes from workload and evidence.

---

# 106. Practical Scenario 2 — Customer Equality Lookup

Dataset:

```text
100 million customers
```

Query:

```sql
WHERE customer_id = 'C123'
```

Do not automatically partition by customer ID.

Evaluate:

- cardinality;
- query frequency;
- partition/file count;
- sorting;
- clustering/bucketing;
- object-store overhead.

---

# 107. Practical Scenario 3 — Severe Skew

```text
region=A → 80%
region=B → 10%
region=C → 5%
region=D → 5%
```

Ask:

> Does region partitioning create meaningful selectivity?

For the dominant region, the filter may still read most of the dataset.

Inspect distribution before standardizing.

---

# 108. Practical Scenario 4 — Hourly Ingestion

Input:

```text
50 GB/hour
```

Compare:

```text
daily
vs
hourly
```

Evaluate:

- query time windows;
- partition volume;
- file count;
- listing overhead;
- late data;
- backfill scope.

---

# 109. Practical Scenario 5 — Multiple Dimensions

Users filter by:

```text
date
country
category
customer_id
```

Do not create four partition levels automatically.

Evaluate:

```text
cardinality
selectivity
query frequency
skew
combination count
sorting alternatives
```

---

# 110. Practical Scenario 6 — Three-Month Backfill

A correction affects:

```text
January
February
March
```

Ask:

- how many partitions are touched?
- can the operation replace only those partitions?
- can the rerun be idempotent?
- are unaffected partitions protected?
- what happens if the writer crashes?

---

# 111. Stop and Think — Combination Count

Given:

```text
10 years
12 months
31 days
100 regions
```

Calculate the maximum theoretical combination count.

### Answer

```text
10 × 12 × 31 × 100
= 372,000
```

The important lesson is multiplicative growth.

---

# 112. Stop and Think — High Cardinality

A column has:

```text
100 million distinct customer IDs
```

Is customer ID automatically a good partition key?

### Answer

No.

High cardinality can create physical and operational problems that outweigh query pruning benefits.

---

# 113. Stop and Think — Filter Frequency

Workload:

```text
90% → date filter
10% → customer lookup
```

Should both columns automatically be partitions?

### Answer

No.

Start with the dominant workload and evaluate high-cardinality customer filtering through alternatives such as sorting/clustering/bucketing.

---

# 114. Stop and Think — Skew

One partition is:

```text
1 TB
```

while the others are:

```text
10 GB
```

What does this indicate?

### Answer

Partition skew.

The large partition may dominate query and backfill work.

---

# 115. Stop and Think — Derived Filter

Physical path:

```text
year=2026/month=09/day=28
```

Query:

```sql
WHERE date_trunc('month', created_at) = DATE '2026-09-01'
```

What should you do?

### Answer

Inspect the actual query plan.

Do not assume the engine will rewrite the expression into partition predicates.

Compare it with direct partition predicates if useful:

```sql
WHERE year = 2026 AND month = 9
```

---

# 116. Stop and Think — Idempotency

A partition overwrite job is run twice with identical input.

What should be true after both successful runs?

### Answer

The logical dataset should be the same as after one successful run, with no duplicate logical data.

---

# 117. Partitioning and Security Awareness

Partition paths may expose business categories:

```text
segment=high_value/
region=restricted/
```

Paths can appear in:

- logs;
- object-store tooling;
- monitoring;
- operational scripts.

Therefore partition design can have governance implications.

Do not accidentally make the directory scheme an undocumented security boundary.

---

# 118. Partitioning and Retention

Time partitions may simplify retention:

```text
older_than_retention_window
        ↓
identify partitions
        ↓
apply retention policy
```

Still verify:

- late-arriving data;
- legal holds;
- recovery requirements;
- dependencies.

---

# 119. Partitioning and Object-Storage Cost

A useful conceptual model is:

```text
Partitioning benefit
=
less data scanned

Partitioning cost
=
more paths + objects + metadata/request activity
```

The net result depends on workload and storage behavior.

---

# 120. Required Five-Query Benchmark Record

Use:

| Strategy | Q1 | Q2 | Q3 | Q4 | Q5 | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| None | | | | | | |
| Year/Month | | | | | | |
| Year/Month/Day | | | | | | |
| Pickup Zone | | | | | | |

Add a separate table for bytes read where the engine exposes a comparable metric.

---

# 121. Fair Benchmarking

Keep constant:

- dataset;
- schema;
- row count;
- values;
- compression;
- row-group settings;
- sorting unless sorting is the variable;
- engine;
- machine;
- storage;
- query.

Change only:

```text
partitioning strategy
```

for the primary experiment.

Then run a separate experiment for:

```text
partitioning + sorting
```

---

# 122. Benchmark Environment Record

Record:

```text
OS:
CPU:
RAM:
Python:
PyArrow:
DuckDB:
Polars:
Dataset version:
Rows:
Schema:
Storage:
Compression:
Partition strategy:
Sort order:
Query:
Run number:
Cache state:
```

This turns a timing into a reproducible experiment.

---

# 123. Benchmark Interpretation

Ask:

### How many partitions exist?

### How many files?

### What is the file-size distribution?

### How many partitions does the query touch?

### How many files?

### How many bytes?

### What is the runtime?

### What does the plan show?

### What is the maintenance cost?

### Is the improvement large enough to justify the complexity?

---

# 124. Estimate vs Actual

The core learning loop is:

```text
Estimate
   ↓
Run
   ↓
Measure
   ↓
Compare
   ↓
Explain gap
```

Do not skip the estimate.

The gap often reveals hidden factors such as:

- writer behavior;
- data skew;
- cache;
- file counts;
- query optimization;
- object-store planning.

---

# 125. Partitioning and Query Runtime

A query can improve from:

```text
10 sec → 8 sec
```

while producing:

```text
10× more files
```

That trade-off needs to be discussed.

Do not evaluate a layout from one metric.

---

# 126. Partitioning and Bytes Read

Bytes read can be useful for understanding physical work.

But label the metric correctly:

```text
compressed bytes
uncompressed bytes
logical bytes
network bytes
```

They are not interchangeable.

---

# 127. Partitioning and File-Size Distribution

Average file size can hide a tail.

Example:

```text
1 GB
1 GB
1 GB
1 KB
1 KB
1 KB
```

The tiny files are operationally important even if the average looks reasonable.

Use min/max and percentiles where useful.

---

# 128. Production Partitioning Standard

A mature standard may define:

```text
what qualifies as a partition candidate
what requires an exception
what evidence is required
how backfills work
how overwrite is implemented
how skew is monitored
when policies are revisited
```

Do not use a rigid fixed number unless your organization has evidence for it.

---

# 129. Exception Example

Suppose:

```text
region
→ 5 values
→ 85% of queries filter on region
```

An organization might justify region partitioning.

The evidence should still include:

```text
cardinality
partition sizes
skew
file counts
query impact
maintenance impact
```

An exception is stronger when it is measurable and documented.

---

# 130. Final Partition Decision Framework

```text
                         START
                           │
                           ↓
                    Define Workload
                           │
                           ↓
                 Identify Common Filters
                           │
                           ↓
                  Estimate Selectivity
                           │
                           ↓
                    Measure Cardinality
                           │
                           ↓
                    Check Stability
                           │
                           ↓
                Estimate Partition Count
                           │
                           ↓
                Estimate Partition Volume
                           │
                           ↓
                    Estimate File Count
                           │
                           ↓
                       Check Skew
                           │
                           ↓
                Consider Sorting/Clustering
                           │
                           ↓
             Consider Object-Store Behavior
                           │
                           ↓
                       Benchmark
                           │
                           ↓
             Compare Runtime + Bytes + Files
                           │
                           ↓
                 Design Backfill Strategy
                           │
                           ↓
                Implement Idempotently
                           │
                           ↓
                    Document Decision
                           │
                           ↓
                     Monitor in Prod
                           │
                           ↓
                     Re-evaluate Later
```

The final decision is based on:

```text
Workload
+
Requirements
+
Measurements
+
Operational constraints
+
Future scale
```

---

# 131. Final Architecture Example

```text
                 SOURCE SYSTEMS
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
       CSV            Avro          JSONL
        │              │              │
        └──────────────┼──────────────┘
                       ↓
                    LANDING
                       ↓
                    BRONZE
                       ↓
                  VALIDATION
                       ↓
                 TYPED DATA
                       ↓
                    SILVER
                 Parquet / table
                       ↓
                     GOLD
                       ↓
              BI / Analytics / ML
```

The silver layer may use a workload-aligned partition scheme while bronze preserves replay/source requirements.

The format and partition choice can legitimately differ by pipeline stage.

---

# 132. Learning Checkpoint

Confirm that you can:

- [ ] Explain partitioning and partition pruning.
- [ ] Explain Hive-style paths.
- [ ] Distinguish dataset, partition, file, row group, and page.
- [ ] Choose partition columns using workload and cardinality.
- [ ] Explain selectivity and filter frequency.
- [ ] Explain partition stability.
- [ ] Compare yearly, monthly, daily, and hourly granularity.
- [ ] Explain `__HIVE_DEFAULT_PARTITION__`.
- [ ] Explain path type interpretation and URI encoding awareness.
- [ ] Write partitioned data with PyArrow.
- [ ] Write partitioned data with pandas.
- [ ] Write partitioned data with Polars.
- [ ] Write partitioned data with DuckDB.
- [ ] Read Hive-partitioned datasets.
- [ ] Use DuckDB `EXPLAIN ANALYZE`.
- [ ] Design idempotent partition overwrite.
- [ ] Explain why temp output is safer than direct replacement.
- [ ] Design backfills.
- [ ] Diagnose over-partitioning.
- [ ] Diagnose skew.
- [ ] Explain partition-vs-sorting trade-offs.
- [ ] Explain bucketing awareness.
- [ ] Explain Z-ordering/clustering awareness.
- [ ] Explain object-storage listing/request considerations.
- [ ] Explain partition migration cost.
- [ ] Explain hidden partitioning and partition evolution at a high level.
- [ ] Estimate partitions/files/bytes before benchmarking.
- [ ] Compare estimates with measured results.
- [ ] Write a production partitioning guideline.

---

# 133. Interview Questions — Basic

### What is a partition?

**Model answer:** A physically separated subset of a dataset identified by one or more partition values.

### What is partition pruning?

**Model answer:** Eliminating partitions that cannot satisfy a query predicate so fewer physical files need to be considered.

### What is Hive-style partitioning?

**Model answer:** A directory convention using paths such as `year=2026/month=09`, where directory keys and values identify partitions.

### Why partition data?

**Model answer:** To create physical locality that can reduce the files considered for selective filters.

---

# 134. Interview Questions — Intermediate

### How do you choose a partition column?

**Model answer:** Evaluate filter frequency, selectivity, cardinality, stability, partition volume, skew, file count, storage behavior, and measured query benefit.

### Why does granularity matter?

**Model answer:** Granularity controls partition size and count. Finer granularity can improve pruning for narrow windows but creates more physical objects and operational complexity.

### Why is high cardinality a warning sign?

**Model answer:** Many distinct values can produce many partitions and files, causing metadata, listing, small-file, and maintenance overhead.

### Why can sorting help?

**Model answer:** Sorting can improve locality inside files and make row-group statistics more selective without creating another directory level.

---

# 135. Interview Questions — Advanced

### Why does partitioning not guarantee pruning?

**Model answer:** The engine must recognize the partition scheme and predicate, and the predicate must actually eliminate meaningful partitions.

### Why is filtering on a high-cardinality ID not enough to justify partitioning?

**Model answer:** The query may be highly selective while the physical partition strategy creates unacceptable path and file complexity. Other locality techniques may be better.

### What is partition skew?

**Model answer:** Uneven partition size distribution in rows or bytes, often causing unbalanced scan, storage, and backfill cost.

### Why can multiple partition levels explode?

**Model answer:** Distinct-value combinations multiply across dimensions, producing a potentially huge partition space.

### Why does object storage matter?

**Model answer:** Object count, prefix listing, metadata requests, and network behavior become part of the partitioning cost.

---

# 136. Interview Questions — Senior / Architecture

### How would you design partitioning for a 10 TB/day dataset?

**Model answer:** Start from workload filter windows, profile cardinality/skew, compare granularities, estimate partition/file counts, benchmark representative queries, test the storage environment, and design idempotent backfills/replacements.

### How would you evaluate `customer_id` partitioning?

**Model answer:** Measure distinct values, data volume per customer, query frequency, resulting paths/files, object-store overhead, and alternatives such as time partitioning plus sorting or bucketing.

### How would you migrate a bad partition scheme?

**Model answer:** Inventory consumers, profile workload, design candidates, benchmark, rewrite and validate, run parallel comparisons, migrate readers, cut over, then retire the old layout.

### When would sorting be preferable to another partition level?

**Model answer:** When the field is high-cardinality or adds another query dimension but path explosion would outweigh its pruning benefit.

### Why might hidden partitioning help?

**Model answer:** It reduces coupling between logical query semantics and the physical directory structure and can make partition evolution easier.

---

# 137. Practical Scenario — Date-Heavy Retail Lake

Given:

```text
3 years
5 billion rows
70% date filters
20% date + country
10% other
```

Candidate layouts:

```text
year/month
year/month/day
country
year/month + sorting
```

Reasoning process:

1. estimate partition counts;
2. estimate partition volume;
3. estimate file count;
4. measure skew;
5. benchmark five query classes;
6. compare bytes read and runtime;
7. evaluate backfill scope;
8. evaluate object-store metadata overhead.

Do not choose the final design before the evidence.

---

# 138. Practical Scenario — Customer Partitioning Proposal

Proposal:

```text
customer_id
```

Question:

> What evidence is required before approval?

Answer:

```text
cardinality
query frequency
partition volume
file count
skew
object-store impact
backfill behavior
sorting/clustering alternatives
benchmark
```

---

# 139. Practical Scenario — Hourly vs Daily

Dataset:

```text
50 GB/hour
```

Workload:

```text
common queries cover 2–6 hours
```

Evaluate:

- hourly pruning benefit;
- daily file volume;
- file count;
- listing overhead;
- late-arrival handling.

Do not decide from the time window alone.

---

# 140. Practical Scenario — Backfill

Three months need correction.

Desired behavior:

```text
January replaced
February replaced
March replaced
Other months unchanged
```

A good implementation must:

- derive affected partitions deterministically;
- write temporary output;
- validate;
- replace only affected partitions;
- support retry.

---

# 141. Final Partition Decision Matrix

| Factor | Questions |
| --- | --- |
| Query filters | Which columns are filtered most often? |
| Selectivity | How much data can be eliminated? |
| Cardinality | How many distinct values exist? |
| Stability | Will values change later? |
| Granularity | Year/month/day/hour? |
| Volume | How much data lands per partition? |
| Files | How many files will be created? |
| Skew | Are partitions balanced? |
| Sorting | Could locality be obtained inside files? |
| Object storage | What metadata/request cost exists? |
| Backfills | How often are historical partitions rewritten? |
| Idempotency | Can retries safely replace partitions? |
| Migration | How difficult is the scheme to change later? |
| Consumers | Which engines must read it? |
| Evidence | What does the benchmark show? |

---

# 142. Final Data-Model-to-Layout Connection

Remember:

```text
Logical Table
      ↓
Business Workload
      ↓
Common Filters
      ↓
Partition Candidate
      ↓
Physical Paths
      ↓
Files
      ↓
Row Groups
      ↓
Pages
      ↓
Columns
      ↓
Query
```

Partitioning is one layer of a larger physical optimization system.

---

# 143. Final Master Mental Model

```text
                 QUERY
                   │
                   ↓
              Query Filters
                   │
                   ↓
          Partition Predicate
                   │
                   ↓
          Partition Pruning
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
 Irrelevant Paths        Relevant Paths
        │                     │
       SKIP                    ↓
                         Relevant Files
                               │
                               ↓
                      Row-Group Statistics
                               │
                               ↓
                        Relevant Row Groups
                               │
                               ↓
                         Column Pruning
                               │
                               ↓
                             Pages
                               │
                               ↓
                           CPU / I/O
                               │
                               ↓
                            RESULT
```

And:

```text
GOOD PARTITION DESIGN
=
Workload
+
Filter Patterns
+
Selectivity
+
Cardinality
+
Granularity
+
Data Volume
+
File Count
+
Skew
+
Sorting / Clustering
+
Object Storage
+
Backfills
+
Idempotency
+
Measured Evidence
```

---

# 144. Final "Remember This"

1. **Partitioning decides which directories/files a query should consider.**
2. **Partition pruning matters only when the query can eliminate meaningful physical scope.**
3. **Hive-style layouts represent partition values in `key=value` paths.**
4. **Dataset, partition, file, row group, and page are different physical concepts.**
5. **Good partition columns are workload-driven.**
6. **High cardinality is a warning sign.**
7. **A selective query does not automatically imply a good partition key.**
8. **Partition granularity balances pruning against physical complexity.**
9. **More partition levels multiply the partition space.**
10. **Partition skew can dominate workload cost.**
11. **Sorting can improve locality without adding directory levels.**
12. **Partitioning and sorting solve different physical problems.**
13. **Null partition values require a documented representation.**
14. **Partition path values require deliberate type and encoding rules.**
15. **Partition overwrite should be idempotent.**
16. **Temporary output and validation are safer than exposing partial replacement output.**
17. **Plain directories do not provide full transactional table guarantees.**
18. **Object-storage listing and request behavior are part of partitioning economics.**
19. **Changing a path-based partition scheme has migration cost.**
20. **Partitioning should be benchmarked against realistic queries.**
21. **Estimate first, measure second, explain the gap.**
22. **The correct partition strategy is workload-specific.**
23. **The correct question is not "What should I partition by?"**
24. **The correct question is "What physical layout best serves this workload?"**

---

# 145. Final Assignment

Choose one real dataset from your project.

Document:

```text
Dataset:
Rows:
Growth:

Top query patterns:
Q1:
Q2:
Q3:
Q4:
Q5:

Candidate partition columns:
Cardinality:
Selectivity:
Stability:

Candidate granularity:
Year:
Month:
Day:
Hour:

Estimated partitions:
Estimated files:
Estimated bytes:

Sorting/clustering alternative:
Skew risk:
Object-storage considerations:

Backfill requirements:
Overwrite semantics:
Idempotency strategy:
```

Then benchmark the candidate strategies and record:

```text
directory count
file count
file-size distribution
query runtime
bytes read
planning observations
```

Finally produce:

```text
Decision
Reasoning
Trade-offs
Exceptions
Migration plan
Monitoring plan
Review trigger
```

The conclusion must be evidence-based.

---

# 146. References and Version Discipline

Primary documentation used to verify implementation details:

- Apache Arrow `write_dataset`: https://arrow.apache.org/docs/python/generated/pyarrow.dataset.write_dataset.html
- Apache Arrow `HivePartitioning`: https://arrow.apache.org/docs/python/generated/pyarrow.dataset.HivePartitioning.html
- pandas `DataFrame.to_parquet`: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_parquet.html
- Polars Hive-partitioned writes: https://docs.pola.rs/user-guide/io/hive/
- DuckDB partitioned writes: https://duckdb.org/docs/stable/data/partitioning/partitioned_writes
- DuckDB Hive partitioning: https://duckdb.org/docs/current/data/partitioning/hive_partitioning
- DuckDB `COPY`: https://duckdb.org/docs/current/sql/statements/copy

### Version discipline

When an API or behavior is version-sensitive:

```text
Check installed version
      ↓
Read official documentation
      ↓
Run small compatibility test
      ↓
Inspect actual output
      ↓
Run workload benchmark
```

Do not assume two libraries expose identical partitioning behavior.

---

# 147. Depth Boundary

This topic owns:

- partitioning;
- partition pruning;
- Hive-style directory layout;
- cardinality/selectivity;
- partition-column selection;
- granularity;
- path value typing;
- null values;
- path encoding awareness;
- idempotent partition replacement;
- safe publication concepts;
- backfills;
- over-partitioning;
- skew;
- multi-level partitioning;
- partition vs sorting/clustering;
- bucketing awareness;
- Z-ordering awareness;
- object-storage implications;
- partition migration;
- hidden partitioning awareness;
- partition evolution awareness;
- partition benchmarks.

Later topics own the deep treatment of:

- Parquet internals;
- compression;
- small files/compaction;
- Spark partitioning/bucketing;
- lakehouse table formats;
- cloud-storage economics;
- advanced performance/scaling.

---

# 148. Final Self-Review

## Fundamentals

- [x] Partition
- [x] Partition pruning
- [x] Hive-style layout
- [x] Dataset/file/partition/row-group distinction

## Selection

- [x] Cardinality
- [x] Selectivity
- [x] Filter frequency
- [x] Stability
- [x] Granularity
- [x] Year/month/day/hour

## Path Semantics

- [x] Path-derived partition values
- [x] Logical partition types
- [x] Null values
- [x] `__HIVE_DEFAULT_PARTITION__`
- [x] Special characters
- [x] URI/URL encoding awareness

## PyData Tools

- [x] PyArrow dataset writes
- [x] PyArrow dataset reads
- [x] pandas `partition_cols=`
- [x] Polars `partition_by`
- [x] DuckDB `PARTITION_BY`
- [x] DuckDB Hive reading
- [x] DuckDB `EXPLAIN ANALYZE`

## Reliability

- [x] Idempotent overwrite
- [x] Temporary output
- [x] Validation before publication
- [x] Backfills
- [x] Crash/failure considerations
- [x] Plain-directory transaction limitations

## Advanced

- [x] Over-partitioning
- [x] High-cardinality risks
- [x] Partition skew
- [x] Multi-level explosion
- [x] Partition vs sorting
- [x] Bucketing awareness
- [x] Z-ordering/clustering awareness
- [x] Object-storage listing
- [x] Request-rate considerations
- [x] Partition-scheme migration
- [x] Hidden partitioning awareness
- [x] Partition evolution awareness

## Required experiments

- [x] Five query patterns
- [x] Estimate partitions/files/bytes
- [x] `EXPLAIN ANALYZE`
- [x] MinIO experiment
- [x] No partitioning
- [x] Year/month
- [x] Year/month/day
- [x] Pickup zone
- [x] File/directory metrics
- [x] Runtime/bytes metrics
- [x] Idempotency test
- [x] Unaffected partition test
- [x] Pickup-zone vs sorting comparison
- [x] One-page team guideline

## Production

- [x] Debugging
- [x] Common mistakes
- [x] Production case study
- [x] Architecture review
- [x] Decision tree
- [x] Benchmark methodology
- [x] Observability
- [x] Interview questions
- [x] Practical scenarios
- [x] Checkpoint
- [x] Final mental model

---

# 149. Closing Principle

Partitioning is not:

```text
date column
+
folder names
```

It is:

```text
Workload
   ↓
Physical locality
   ↓
Path organization
   ↓
Partition pruning
   ↓
File selection
   ↓
I/O reduction
   ↓
Query behavior
   ↓
Operational cost
```

> **Partition when the workload, physical layout, and measurements show that partitioning is worth the cost.**
'''
