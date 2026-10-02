# Topic 01 — Structuring Extract–Transform–Load Code

> **Stage 2 — Python for Data Engineering**  
> **Module 2.12 — Transformation Patterns and Pipeline Design**

## Learning Objective

Production Data Engineering is not about putting `read()`, `clean()`, and `write()` into one Python function. The objective is to create a pipeline whose responsibilities, inputs, outputs, execution interval, contracts, and side effects are explicit.

The core architecture is:

```text
CLI / Orchestrator
        ↓
    RunContext
        ↓
      Pipeline
        ↓
      Reader
        ↓
Pure Transformations
        ↓
Validation Boundaries
        ↓
      Writer
        ↓
Partitioned Output
```

The central rule is:

> **I/O belongs at the edges; business logic belongs in the middle.**

This chapter teaches the foundation required by the rest of Module 2.12. Later topics build on it with idempotent loads, incremental processing, late-arriving data, hashing, enrichment, metadata-driven execution, checkpoints, and dbt.

---

# 1. What Is a Transformation Pipeline?

A transformation pipeline reads data, changes it according to explicit rules, and publishes the resulting dataset.

```text
Source
  ↓
Extract
  ↓
Transform
  ↓
Load
  ↓
Target
```

For an orders pipeline:

```text
bronze.orders
     ↓
read partition
     ↓
standardise
     ↓
cast types
     ↓
deduplicate within batch
     ↓
flag invalid records
     ↓
validate
     ↓
silver.orders
```

The important architectural distinction is responsibility:

| Layer | Responsibility |
|---|---|
| Extract | Obtain required source data |
| Transform | Apply business/data logic |
| Validate | Check explicit contracts and invariants |
| Load | Persist the output |
| CLI/orchestrator boundary | Select and invoke a pipeline |

A production pipeline should make those boundaries visible.

## Why structure matters

Good structure makes it easier to:

- test transformations without infrastructure,
- rerun a historical interval,
- debug incorrect results,
- replace storage technology,
- benchmark individual steps,
- reuse logic,
- compare implementations,
- and eventually invoke the pipeline from an orchestrator.

A senior engineer should be able to answer:

> Which input interval, transformation logic, configuration, and output produced this dataset?

---

# 2. ETL vs ELT

## ETL

```text
Extract → Transform → Load
```

Transformation happens before the final target receives the transformed data.

Example:

```text
PostgreSQL
    ↓
Python reader
    ↓
Polars
    ↓
Parquet
```

## ELT

```text
Extract → Load → Transform
```

Raw or lightly processed data is loaded into an analytical platform first.

```text
Source
  ↓
Raw warehouse table
  ↓
SQL / DuckDB / warehouse engine
  ↓
Silver / Gold model
```

Modern platforms often favor ELT because analytical engines are optimized for large relational transformations close to the stored data.

Python still matters for:

- file-oriented transformations,
- source-specific preparation,
- DataFrame logic,
- custom validation,
- external APIs,
- local lake processing,
- procedural logic.

The architectural separation remains useful in either approach:

```text
I/O boundary
    ↓
explicit transformation
    ↓
I/O boundary
```

SQL, DuckDB, Polars, and pandas can all implement the transformation layer.

---

# 3. Extract Layer

The extract layer reads the data required by the pipeline.

Sources may include:

- Parquet,
- CSV,
- databases,
- object storage,
- APIs.

A reader might be:

```python
from pathlib import Path
import polars as pl


def read_bronze(path: Path) -> pl.DataFrame:
    return pl.read_parquet(path)
```

The reader owns I/O. It should not secretly implement business rules.

Bad:

```python
def read_bronze(path: Path) -> pl.DataFrame:
    df = pl.read_parquet(path)

    df = df.filter(pl.col("status") != "cancelled")
    df = df.with_columns(
        pl.col("amount").cast(pl.Float64)
    )

    return df
```

Better:

```python
def read_bronze(path: Path) -> pl.DataFrame:
    return pl.read_parquet(path)


def clean_orders(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.col("amount").cast(pl.Float64)
    )
```

The reader answers:

> How do I obtain the data?

The transformation answers:

> What should the data become?

## Read only what the pipeline owns

A partition-aware reader might be:

```python
def read_bronze(
    root: Path,
    logical_date: str,
) -> pl.DataFrame:
    path = (
        root
        / "orders"
        / f"date={logical_date}"
        / "orders.parquet"
    )
    return pl.read_parquet(path)
```

This keeps the transformation independent of storage-path details.

---

# 4. Transform Layer

The transform layer contains business and data logic.

The desired model is:

```text
input data
+
explicit parameters
        ↓
transformed data
```

A simple example:

```python
def add_tax(amount: float, rate: float) -> float:
    return amount * (1 + rate)
```

A DataFrame example:

```python
def standardise_orders(
    df: pl.DataFrame,
) -> pl.DataFrame:
    return df.rename(
        {
            "OrderID": "order_id",
            "CustomerID": "customer_id",
        }
    )
```

The transformation should not secretly:

- write files,
- write databases,
- call APIs,
- inspect global mutable state,
- read the system clock,
- generate random values.

Those are hidden inputs or side effects.

---

# 5. Load Layer

The load layer persists transformed data.

```python
def write_silver(
    df: pl.DataFrame,
    output_path: Path,
) -> None:
    df.write_parquet(output_path)
```

The writer should not decide how the order data is standardized.

This separation allows the same transformation to be used with different outputs:

```text
Parquet writer
Database writer
Warehouse writer
```

without changing the transformation itself.

---

# 6. Pure Functions

A pure function is driven by explicit inputs and does not secretly modify external state.

```python
def add_tax(amount: float, rate: float) -> float:
    return amount * (1 + rate)
```

For the same:

```text
amount = 100
rate = 0.20
```

the result is always:

```text
120
```

A pure DataFrame transformation follows the same idea:

```python
def standardise_orders(
    df: pl.DataFrame,
) -> pl.DataFrame:
    return df.rename(
        {
            "OrderID": "order_id",
            "CustomerID": "customer_id",
        }
    )
```

Pure transformations are easier to:

| Property | Benefit |
|---|---|
| Test | Small in-memory inputs are sufficient |
| Reason about | Dependencies are visible |
| Debug | Behavior is localized |
| Rerun | Same inputs can reproduce results |
| Reuse | Less infrastructure coupling |
| Benchmark | Work can be isolated |
| Compose | Steps can be chained |

Purity is a design preference for the transformation core, not a claim that the entire pipeline has no side effects.

---

# 7. Side Effects

Common side effects include:

- writing files,
- database writes,
- API calls,
- changing external state,
- mutating global state,
- reading the current clock,
- generating uncontrolled random values.

Bad:

```python
def transform(df: pl.DataFrame) -> pl.DataFrame:
    result = clean(df)
    result.write_parquet("output.parquet")
    return result
```

The function name suggests transformation, but it also writes a file.

Better:

```python
def transform(df: pl.DataFrame) -> pl.DataFrame:
    return clean(df)


result = transform(df)
write_silver(result, output_path)
```

Now the side effect is explicit.

---

# 8. I/O at the Edges

A strong structure is:

```text
┌───────────────┐
│    Reader     │
│  Side Effect  │
└───────┬───────┘
        ↓
┌───────────────┐
│ Pure Step 1   │
└───────┬───────┘
        ↓
┌───────────────┐
│ Pure Step 2   │
└───────┬───────┘
        ↓
┌───────────────┐
│ Pure Step 3   │
└───────┬───────┘
        ↓
┌───────────────┐
│    Writer     │
│  Side Effect  │
└───────────────┘
```

This is one of the most useful mental models in production Data Engineering:

> **I/O belongs at the edges; business logic belongs in the middle.**

A real pipeline necessarily performs I/O. The goal is to isolate it rather than hide it.

---

# 9. Repository Structure

A realistic Module 2.12 project is:

```text
transform_lab/
├── src/
│   └── transform_lab/
│       ├── core/
│       ├── pipelines/
│       └── config/
├── tests/
├── dbt_project/
└── lake/
```

## `core/`

Shared infrastructure such as:

- RunContext,
- I/O adapters,
- common validation boundaries,
- genuinely shared utilities.

## `pipelines/`

Dataset-specific pipeline composition:

```text
pipelines/
└── orders_silver/
```

## `config/`

Explicit configuration for datasets and environments.

## `tests/`

Unit and integration tests.

## `dbt_project/`

Later Module 2.12 work for SQL-centric transformations.

## `lake/`

Local bronze/silver/gold Parquet data used by the exercise environment.

Avoid turning `core/` into a miscellaneous dumping ground. Shared code should represent a real shared concept.

---

# 10. Bronze, Silver, Gold

A useful transformation-layer model is:

```text
bronze
  ↓
silver
  ↓
gold
```

## Bronze

Raw or landed data.

```text
bronze.orders
```

## Silver

Cleaned, standardized, validated, and appropriately deduplicated data.

```text
silver.orders
```

## Gold

Business-facing analytical data.

```text
gold.daily_revenue
```

Example:

```text
bronze.orders
      ↓
silver.orders
      ↓
gold.daily_revenue
```

The names are less important than the responsibilities. Each layer should have a clear purpose.

---

# 11. RunContext

A production transformation should not depend on hidden execution state.

Use an explicit context:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RunContext:
    run_id: str
    data_interval_start: datetime
    data_interval_end: datetime
    env: str
    config: dict[str, Any]
```

## Field meanings

| Field | Purpose |
|---|---|
| `run_id` | Identifies this execution |
| `data_interval_start` | Start of the owned data interval |
| `data_interval_end` | End of the owned data interval |
| `env` | Execution environment |
| `config` | Explicit configuration for the run |

The important design property is explicit dependency.

Instead of:

```python
ENV = os.getenv("ENV")
CURRENT_DATE = datetime.now()
```

use:

```python
def transform_orders(
    df: pl.DataFrame,
    ctx: RunContext,
) -> pl.DataFrame:
    ...
```

The function's important context is now visible.

---

# 12. Data Interval vs Execution Time

Do not confuse:

```text
When the program happens to run
```

with:

```text
Which data the program is responsible for
```

Example:

```text
Execution:
2026-10-02 08:15

Owned interval:
2026-10-01 00:00
→
2026-10-02 00:00
```

The pipeline may execute at 08:15 while processing the previous day's data.

Historical intervals can be processed:

- today,
- tomorrow,
- during a backfill,
- after a failure,
- during testing.

The transformation should therefore use the explicit data interval rather than silently using machine time.

---

# 13. Why `datetime.now()` Is a Problem

Bad:

```python
from datetime import datetime


def transform(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.lit(datetime.now()).alias("processed_at")
    )
```

The function has a hidden input:

```text
current system time
```

Therefore:

```text
same data
+
different execution time
=
different result
```

This harms:

- determinism,
- reproducibility,
- testing,
- historical reruns,
- debugging,
- backfills,
- idempotency reasoning.

Better:

```python
def transform(
    df: pl.DataFrame,
    ctx: RunContext,
) -> pl.DataFrame:
    return df.with_columns(
        pl.lit(ctx.data_interval_end).alias("processed_at")
    )
```

Principle:

> **Time-dependent behavior should be explicit input, not hidden state.**

---

# 14. Determinism

A deterministic transformation follows:

> **Same inputs + same run context → same output.**

Potential hidden sources of nondeterminism:

- `datetime.now()`,
- `random.random()`,
- inappropriate random UUIDs,
- mutable globals,
- “latest” queries,
- environment-dependent behavior,
- unstable ordering where ordering matters.

Bad:

```python
import random


def transform(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.lit(random.random()).alias("score")
    )
```

Better design requires any intentional randomness to be explicit and controlled.

Bad global state:

```python
CURRENT_REGION = "IN"


def transform(df: pl.DataFrame) -> pl.DataFrame:
    ...
```

Better:

```python
def transform(
    df: pl.DataFrame,
    region: str,
) -> pl.DataFrame:
    ...
```

Or put the value in `RunContext`.

Avoid vague data selection such as “latest” unless the logical boundary and ordering rules are explicit.

## What determinism enables

```text
Reproducibility
      ↓
Debugging
      ↓
Testing
      ↓
Historical reruns
      ↓
Backfills
      ↓
Auditing
      ↓
Reference-output comparison
```

---

# 15. Deterministic Orders-Silver Flow

A Topic 01 pipeline can be:

```text
read_bronze(ctx)
      ↓
standardise(df)
      ↓
cast_types(df)
      ↓
deduplicate_within_batch(df)
      ↓
flag_invalid(df)
      ↓
validate(df)
      ↓
write_silver(ctx, df)
```

A coherent implementation:

```python
def standardise(df: pl.DataFrame) -> pl.DataFrame:
    return df.rename(
        {
            "OrderID": "order_id",
            "CustomerID": "customer_id",
            "OrderTimestamp": "order_ts",
            "Amount": "amount",
        }
    )


def cast_types(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.col("order_id").cast(pl.Int64),
        pl.col("customer_id").cast(pl.Int64),
        pl.col("order_ts").cast(pl.Datetime),
        pl.col("amount").cast(pl.Float64),
    )


def deduplicate_within_batch(
    df: pl.DataFrame,
) -> pl.DataFrame:
    return df.unique(
        subset=["order_id"],
        keep="last",
    )


def flag_invalid(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        (
            (pl.col("order_id") <= 0)
            | (pl.col("customer_id") <= 0)
            | (pl.col("amount") < 0)
        ).alias("is_invalid")
    )


def transform_orders(
    df: pl.DataFrame,
    ctx: RunContext,
) -> pl.DataFrame:
    result = standardise(df)
    result = cast_types(result)
    result = deduplicate_within_batch(result)
    result = flag_invalid(result)

    return result.with_columns(
        pl.lit(ctx.data_interval_end).alias("processed_at")
    )
```

This chapter deliberately limits deduplication to the current batch. Target-level merge and idempotent loading belong to Topic 02.

---

# 16. Step Contracts

Each important transformation step should have a contract describing:

- input schema,
- output schema,
- assumptions,
- invariants,
- expected grain.

Example:

```text
Step: cast_types

Input:
    order_id may be string
    amount may be string

Output:
    order_id → Int64
    amount   → Float64

Invariant:
    one row represents one order
```

Contracts create explicit boundaries:

```text
Input
  ↓
contract
  ↓
transform
  ↓
contract
  ↓
next step
```

## Pandera boundary example

Module 2.11 covers validation in depth. Here we only integrate it into the pipeline architecture.

```python
import pandera.pandas as pa


orders_schema = pa.DataFrameSchema(
    {
        "order_id": pa.Column(int, nullable=False),
        "customer_id": pa.Column(int, nullable=False),
        "amount": pa.Column(float, nullable=False),
    },
    strict=True,
)


def validate_orders(df):
    return orders_schema.validate(df)
```

Validation failures should be surfaced as explicit pipeline failures rather than silently ignored.

## Grain

Always ask:

> What does one row represent?

For example:

```text
silver.orders
= one row per order
```

A transformation that changes the grain should make that change intentional and understandable.

---

# 17. Choosing SQL, DuckDB, Polars, or pandas

## SQL / DuckDB / warehouse

Useful when:

- the operation is relational,
- the data already lives in a SQL engine,
- SQL is the clearest expression,
- the engine can execute the operation efficiently.

```sql
SELECT
    customer_id,
    SUM(amount) AS revenue
FROM silver.orders
GROUP BY customer_id;
```

## Polars

Useful for:

- columnar DataFrame transformations,
- local/lake workloads,
- expressive Python transformations.

```python
result = df.with_columns(
    (pl.col("amount") * 1.18).alias("amount_with_tax")
)
```

## pandas

Reasonable for:

- smaller workloads,
- existing pandas systems,
- teams with mature pandas code,
- operations naturally expressed in pandas.

The architectural principle is:

> **Keep the transformation interface conceptually consistent even when the execution engine changes.**

Do not build unnecessary abstractions simply to hide a three-line engine difference.

---

# 18. Naming Conventions

Common transformation naming conventions:

```text
stg_
int_
fct_
dim_
```

| Prefix | Meaning |
|---|---|
| `stg_` | Staging |
| `int_` | Intermediate |
| `fct_` | Fact |
| `dim_` | Dimension |

Examples:

```text
stg_orders
int_order_items
fct_daily_revenue
dim_customer
```

Consistent naming improves:

- readability,
- lineage,
- discoverability,
- debugging,
- collaboration,
- platform-scale maintenance.

A useful logical convention is:

> **One clearly defined output table per transformation step.**

That does not mean every step must be physically materialized.

---

# 19. Functional Data Engineering

Functional Data Engineering extends pure transformation thinking to pipeline tasks.

The conceptual model is:

```text
output_partition
=
f(
    input_partitions,
    data_interval,
    configuration
)
```

For example:

```text
bronze/orders/date=2026-09-29
          +
data interval
          +
configuration
          ↓
silver/orders/date=2026-09-29
```

The task should not depend on whatever data happens to be available elsewhere.

## Important properties

### Immutability

Treat input data as input rather than hidden mutable state.

### Partition scope

Define which interval the task owns.

### Explicit dependencies

Make inputs and configuration visible.

### Reproducibility

Same inputs and context should reproduce the same logical output.

### Reruns

A partition can be regenerated from its inputs.

### Backfills

A historical interval can be processed using the same transformation structure.

These principles become essential for later Module 2.12 topics.

---

# 20. Partition-Scoped Processing

Prefer:

```text
orders_silver
└── date=2026-09-29
```

over:

```text
read every order currently available
```

Partition-scoped processing provides:

- bounded processing,
- predictable outputs,
- easier retries,
- easier backfills,
- reduced compute,
- easier debugging.

Example:

```python
def process_partition(
    ctx: RunContext,
    bronze_root: Path,
    silver_root: Path,
) -> None:
    logical_date = ctx.data_interval_start.date().isoformat()

    input_path = (
        bronze_root
        / "orders"
        / f"date={logical_date}"
        / "orders.parquet"
    )

    df = read_bronze(input_path)
    result = transform_orders(df, ctx)

    write_silver(
        result,
        silver_root / "orders" / f"date={logical_date}",
    )
```

The exact storage system can change. The ownership boundary should remain explicit.

---

# 21. Thin CLI Entry Points

Example:

```text
orders-silver --date 2026-09-30
```

The CLI should:

1. parse arguments,
2. create `RunContext`,
3. invoke the pipeline,
4. report success/failure.

It should not contain business transformation rules.

Bad:

```python
def main():
    args = parse_args()
    df = pl.read_parquet(...)
    df = df.filter(...)
    df = df.with_columns(...)
    df.write_parquet(...)
```

Better:

```python
def main() -> None:
    args = parse_args()

    ctx = RunContext(
        run_id=args.run_id,
        data_interval_start=args.start,
        data_interval_end=args.end,
        env=args.env,
        config={},
    )

    run_orders_silver(ctx)
```

Architecture:

```text
CLI
 ↓
RunContext
 ↓
Pipeline
 ↓
Pure transformations
 ↓
Writer
```

A future orchestrator can call the same pipeline boundary.

---

# 22. Anti-Patterns

## 22.1 God script

```python
def run():
    read()
    clean()
    transform()
    write()
    send_email()
    update_database()
```

Problems:

- mixed responsibilities,
- difficult tests,
- hidden dependencies,
- difficult maintenance.

Refactor around explicit boundaries.

## 22.2 Notebook as production pipeline

Notebooks are valuable for:

- exploration,
- prototyping,
- inspecting data,
- testing hypotheses.

They become risky as the sole production implementation because of:

- hidden state,
- execution-order dependency,
- unclear inputs/outputs,
- manual execution,
- difficult automated testing.

Move reusable production logic into executable modules.

## 22.3 Hidden global state

Bad:

```python
ENV = "prod"
COUNTER = 0
```

A transformation depending on these values is harder to reason about and test.

## 22.4 Transformations writing files midway

Bad:

```python
def transform(df):
    result = clean(df)
    result.write_parquet("temporary.parquet")
    return result
```

Keep the write operation in a writer.

## 22.5 Environment logic inside business logic

Bad:

```python
def transform(df):
    if os.getenv("ENV") == "prod":
        ...
```

Prefer:

```text
environment/configuration
        ↓
RunContext
        ↓
business logic
```

---

# 23. Testability

Pure transformations can be tested using small in-memory datasets.

```python
def test_standardise_orders() -> None:
    input_df = pl.DataFrame(
        {
            "OrderID": [1],
            "CustomerID": [42],
        }
    )

    result = standardise_orders(input_df)

    expected = pl.DataFrame(
        {
            "order_id": [1],
            "customer_id": [42],
        }
    )

    assert result.equals(expected)
```

No database or object store is required.

## Unit vs integration tests

### Unit test

```text
input
 ↓
one transformation
 ↓
expected output
```

### Integration test

```text
reader
 ↓
transformations
 ↓
validation
 ↓
writer
```

The architecture supports both.

A later testing module will cover broader production testing patterns; this chapter establishes the structural reason testing is possible.

---

# 24. Complete `orders_silver` Hands-On Exercise

## Objective

Build:

```text
pipelines/orders_silver/
```

with the following logical flow:

```text
read_bronze(ctx)
    ↓
standardise
    ↓
cast_types
    ↓
deduplicate_within_batch
    ↓
flag_invalid
    ↓
validate
    ↓
write_silver(ctx, df)
```

The writer should overwrite exactly the partition owned by the current run in this exercise.

## Complete example

```python
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import polars as pl


@dataclass(frozen=True)
class RunContext:
    run_id: str
    data_interval_start: datetime
    data_interval_end: datetime
    env: str
    config: dict[str, Any]


def read_bronze(
    bronze_root: Path,
    ctx: RunContext,
) -> pl.DataFrame:
    logical_date = ctx.data_interval_start.date().isoformat()

    path = (
        bronze_root
        / "orders"
        / f"date={logical_date}"
        / "orders.parquet"
    )

    return pl.read_parquet(path)


def standardise(df: pl.DataFrame) -> pl.DataFrame:
    return df.rename(
        {
            "OrderID": "order_id",
            "CustomerID": "customer_id",
            "OrderTimestamp": "order_ts",
            "Amount": "amount",
        }
    )


def cast_types(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.col("order_id").cast(pl.Int64),
        pl.col("customer_id").cast(pl.Int64),
        pl.col("order_ts").cast(pl.Datetime),
        pl.col("amount").cast(pl.Float64),
    )


def deduplicate_within_batch(
    df: pl.DataFrame,
) -> pl.DataFrame:
    return df.unique(
        subset=["order_id"],
        keep="last",
    )


def flag_invalid(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        (
            (pl.col("order_id") <= 0)
            | (pl.col("customer_id") <= 0)
            | (pl.col("amount") < 0)
        ).alias("is_invalid")
    )


def transform_orders(
    df: pl.DataFrame,
    ctx: RunContext,
) -> pl.DataFrame:
    result = standardise(df)
    result = cast_types(result)
    result = deduplicate_within_batch(result)
    result = flag_invalid(result)

    return result.with_columns(
        pl.lit(ctx.data_interval_end).alias("processed_at")
    )


def write_silver(
    df: pl.DataFrame,
    silver_root: Path,
    ctx: RunContext,
) -> Path:
    logical_date = ctx.data_interval_start.date().isoformat()

    partition_dir = (
        silver_root
        / "orders"
        / f"date={logical_date}"
    )
    partition_dir.mkdir(parents=True, exist_ok=True)

    output_path = partition_dir / "orders.parquet"
    df.write_parquet(output_path)

    return output_path


def run_orders_silver(
    ctx: RunContext,
    bronze_root: Path,
    silver_root: Path,
) -> Path:
    raw = read_bronze(bronze_root, ctx)
    transformed = transform_orders(raw, ctx)

    # Apply the output contract here.
    # A production implementation can use the
    # appropriate Pandera integration for the DataFrame engine.
    return write_silver(
        transformed,
        silver_root,
        ctx,
    )
```

The important architecture is more important than the small framework:

```text
reader
  ↓
pure steps
  ↓
contract boundary
  ↓
writer
```

The writer knows the target partition. The transformation does not know where its result will be stored.

---

# 25. Pandera Step Validation

A Pandera contract can express expected fields and types.

```python
import pandera.pandas as pa


silver_schema = pa.DataFrameSchema(
    {
        "order_id": pa.Column(int, nullable=False),
        "customer_id": pa.Column(int, nullable=False),
        "amount": pa.Column(float, nullable=False),
        "is_invalid": pa.Column(bool, nullable=False),
    },
    strict=True,
)


def validate_silver(df):
    return silver_schema.validate(df)
```

A pipeline boundary can therefore be:

```python
transformed = transform_orders(raw, ctx)
validated = validate_silver(transformed)
write_silver(validated, ...)
```

The exact DataFrame/Pandera integration depends on the engine and installed versions. The architectural rule is stable:

```text
assumption
   ↓
validate
   ↓
next step
```

Validation failures should be visible and actionable.

---

# 26. CLI Example

A realistic command is:

```text
orders-silver --date 2026-09-30
```

The CLI should convert that argument into an explicit interval.

Conceptually:

```python
def build_context(
    logical_date: datetime,
    env: str,
) -> RunContext:
    return RunContext(
        run_id="generated-run-id",
        data_interval_start=logical_date,
        data_interval_end=logical_date.replace(
            day=logical_date.day + 1,
        ),
        env=env,
        config={},
    )
```

For production code, use proper calendar arithmetic rather than manual day replacement.

The important point is that the pipeline receives a context; it does not discover the interval from the system clock.

---

# 27. Determinism Experiment

Perform this experiment:

1. Select a historical date.
2. Run the pipeline.
3. Save the output.
4. Run the same interval again.
5. Compare outputs.
6. Run it again later.
7. Confirm equivalence.

Conceptually:

```text
Input X + Context C → Output Y
Input X + Context C → Output Y
Input X + Context C → Output Y
```

## Byte comparison

If output serialization is stable, a file hash can be compared:

```python
import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()
```

Then:

```python
assert sha256_file(first) == sha256_file(second)
```

## Semantic comparison

Byte equality is not always necessary. File metadata or row ordering can differ while the dataset remains semantically equivalent.

A semantic test may compare:

- columns,
- data types,
- row count,
- key set,
- values,
- required ordering.

Use the comparison appropriate to the output contract.

---

# 28. Faked-Clock / Time Testing

The goal is to prove that the transformation uses the explicit interval rather than machine time.

Use:

```text
RunContext:
2026-09-30 → 2026-10-01

Machine clock:
2026-10-02
```

The output should still reflect the RunContext.

Example:

```python
def test_processed_at_uses_context() -> None:
    ctx = RunContext(
        run_id="test",
        data_interval_start=datetime(2026, 9, 30),
        data_interval_end=datetime(2026, 10, 1),
        env="test",
        config={},
    )

    df = pl.DataFrame(
        {
            "order_id": [1],
            "customer_id": [10],
            "amount": [25.0],
        }
    )

    result = transform_orders(df, ctx)

    assert result["processed_at"][0] == datetime(2026, 10, 1)
```

No system clock is required.

---

# 29. Bad Design → Refactored Design

## Before

```python
import os
from datetime import datetime

import pandas as pd


def run_orders():
    env = os.getenv("ENV", "dev")

    df = pd.read_parquet("lake/bronze/orders.parquet")

    df["amount"] = df["amount"].astype(float)

    if env == "prod":
        df = df[df["amount"] >= 0]

    df["processed_at"] = datetime.now()

    df.to_parquet("lake/silver/orders.parquet")

    return df
```

## Problems

- extraction, transformation, and loading are mixed,
- environment is discovered inside the pipeline,
- current time is hidden,
- paths are hard-coded,
- no explicit interval exists,
- the function is difficult to unit test,
- inputs and outputs are unclear.

## After

```text
CLI / Orchestrator
        ↓
RunContext
        ↓
Reader
        ↓
Pure Transformations
        ↓
Validation
        ↓
Writer
```

Example:

```python
def read_orders(path: Path) -> pl.DataFrame:
    return pl.read_parquet(path)


def standardise_orders(df: pl.DataFrame) -> pl.DataFrame:
    return df.rename({"OrderID": "order_id"})


def flag_invalid_orders(
    df: pl.DataFrame,
) -> pl.DataFrame:
    return df.with_columns(
        (pl.col("amount") < 0).alias("is_invalid")
    )


def transform_orders(
    df: pl.DataFrame,
    ctx: RunContext,
) -> pl.DataFrame:
    result = standardise_orders(df)
    result = flag_invalid_orders(result)

    return result.with_columns(
        pl.lit(ctx.data_interval_end).alias("processed_at")
    )


def write_orders(
    df: pl.DataFrame,
    path: Path,
) -> None:
    df.write_parquet(path)
```

The improvement is not “more files.” It is explicit responsibility.

---

# 30. Pure-Step Exercises

## Exercise 1 — Separate read/transform/write

Bad:

```python
def process(path):
    df = pl.read_parquet(path)
    df = df.filter(pl.col("amount") > 0)
    df.write_parquet("output.parquet")
    return df
```

Refactor it.

### Solution

```python
def read_orders(path: Path) -> pl.DataFrame:
    return pl.read_parquet(path)


def filter_valid_amounts(
    df: pl.DataFrame,
) -> pl.DataFrame:
    return df.filter(pl.col("amount") > 0)


def write_orders(
    df: pl.DataFrame,
    path: Path,
) -> None:
    df.write_parquet(path)
```

Composition:

```python
df = read_orders(input_path)
result = filter_valid_amounts(df)
write_orders(result, output_path)
```

## Exercise 2 — Replace `datetime.now()`

Bad:

```python
def add_processed_time(df):
    return df.with_columns(
        pl.lit(datetime.now()).alias("processed_at")
    )
```

### Solution

```python
def add_processed_time(
    df: pl.DataFrame,
    ctx: RunContext,
) -> pl.DataFrame:
    return df.with_columns(
        pl.lit(ctx.data_interval_end).alias("processed_at")
    )
```

## Exercise 3 — Remove global configuration

Bad:

```python
ENV = "prod"


def transform(df):
    if ENV == "prod":
        return df.filter(pl.col("amount") >= 0)
    return df
```

### Solution

```python
def transform(
    df: pl.DataFrame,
    ctx: RunContext,
) -> pl.DataFrame:
    if ctx.env == "prod":
        return df.filter(pl.col("amount") >= 0)

    return df
```

## Exercise 4 — Separate validation

Bad:

```python
def transform(df):
    if df["amount"].null_count() > 0:
        raise ValueError("Invalid amount")

    return df.with_columns(...)
```

### Solution

```python
def transform(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.col("amount").cast(pl.Float64)
    )


def validate(df: pl.DataFrame) -> None:
    if df["amount"].null_count() > 0:
        raise ValueError("Invalid amount")
```

## Exercise 5 — Convert notebook logic

Given:

```python
df = pl.read_parquet(...)
df = df.rename(...)
df = df.filter(...)
df.write_parquet(...)
```

Create:

```text
read_bronze()
standardise()
filter_valid()
write_silver()
```

The notebook may remain an exploration tool; the reusable production logic should live in executable functions.

---

# 31. Debugging Guide

## Wrong date processed

**Symptom:** the wrong partition was read or written.

**Likely cause:** `datetime.now()` or implicit “today” logic.

**Debug:** trace CLI argument → RunContext → reader path → writer path.

**Correction:** make the data interval explicit.

## Hidden global configuration

**Symptom:** behavior differs between test and production.

**Likely cause:** module-level variables or `os.getenv()` inside transformation logic.

**Debug:** inspect transformation dependencies.

**Correction:** pass configuration explicitly or through RunContext.

## Different result on second execution

**Symptom:** same historical run produces different results.

**Likely causes:**

- current time,
- random values,
- mutable globals,
- changing source selection,
- unstable ordering.

**Debug:** fix input, context, configuration, and logic version, then compare outputs.

**Correction:** remove hidden inputs and define selection/order rules.

## Unexpected file writes

**Symptom:** unit tests create files.

**Likely cause:** transformation performs I/O.

**Debug:** trace calls to `write_parquet`, `open`, database writes, or API calls.

**Correction:** move persistence into the writer.

## Transformation unexpectedly calls a database

**Symptom:** a pure transformation test requires a database.

**Likely cause:** database access is hidden inside the transform.

**Debug:** inspect the dependency chain.

**Correction:** isolate source I/O and pass required data explicitly.

## CLI contains business logic

**Symptom:** transformation cannot be reused outside the CLI.

**Likely cause:** `main()` contains data-processing rules.

**Correction:** make the CLI create RunContext and call pipeline code.

---

# 32. Production Architecture

The pieces fit together as:

```text
┌───────────────────────────────┐
│ CLI / Future Orchestrator     │
└───────────────┬───────────────┘
                ↓
┌───────────────────────────────┐
│ RunContext                    │
│ run_id / interval / env / cfg │
└───────────────┬───────────────┘
                ↓
┌───────────────────────────────┐
│ Pipeline                      │
└───────────────┬───────────────┘
                ↓
┌───────────────────────────────┐
│ Reader — side effect          │
└───────────────┬───────────────┘
                ↓
┌───────────────────────────────┐
│ Pure transformations          │
└───────────────┬───────────────┘
                ↓
┌───────────────────────────────┐
│ Validation boundaries         │
└───────────────┬───────────────┘
                ↓
┌───────────────────────────────┐
│ Writer — side effect          │
└───────────────┬───────────────┘
                ↓
┌───────────────────────────────┐
│ Partitioned output            │
└───────────────────────────────┘
```

Configuration enters near the boundary:

```text
configuration
      ↓
RunContext
      ↓
pipeline
```

Environment-specific execution belongs at the boundary rather than hidden inside business logic.

Operational state is a separate concern. Topic 08 covers checkpoints and resumability in depth; Topic 01 only establishes that state should not become hidden transformation state.

---

# 33. Trade-offs

Architecture should not become dogma.

## Pure functions vs practical side effects

Keep transformation logic pure where possible, while allowing necessary I/O at explicit edges.

## One large transformation vs several small transformations

A tiny transformation may not need five functions. Split when a step has a meaningful responsibility, contract, or testing boundary.

## pandas vs Polars vs SQL

Choose based on workload, data location, team capability, and operational requirements.

## One output table vs intermediate outputs

Not every logical step needs physical materialization. Materialize when it provides a real operational benefit.

## Abstraction vs simplicity

Abstraction is valuable when it removes repeated complexity. Too much abstraction hides the actual data flow.

## Configuration vs explicit code

Configuration helps when many datasets share a stable pattern. It can become a programming language if overused.

## Partitioned vs full-table processing

Partitioned processing is valuable when the data naturally has a bounded interval. Full-table processing can be reasonable for small data or transformations that genuinely require the full history.

## Strict contracts vs development velocity

Contracts catch problems early, but excessive rigidity can slow exploration. Strengthen contracts at important production boundaries.

---

# 34. Common Beginner Mistakes

1. **Everything in one script** — separate responsibilities.
2. **Files written inside transforms** — move persistence to the writer.
3. **`datetime.now()` everywhere** — use explicit run context.
4. **Global variables** — pass dependencies explicitly.
5. **Environment logic in business logic** — inject environment/configuration.
6. **Database queries inside pure transforms** — isolate I/O.
7. **Notebook as the production system** — move reusable logic into modules.
8. **Unclear function contracts** — define inputs, outputs, schemas, and grain.
9. **Processing all data for one interval** — use partition scope where appropriate.
10. **No validation boundaries** — validate important assumptions.
11. **Premature abstraction** — understand the concrete pipeline first.

---

# 35. Production Checklist

```text
[ ] Extract, transform, and load responsibilities are separated.
[ ] Transformations are pure where possible.
[ ] I/O is kept at explicit edges.
[ ] RunContext is explicit.
[ ] run_id is available.
[ ] Data interval is explicit.
[ ] Environment is explicit.
[ ] Configuration is explicit.
[ ] No hidden now()/random()/latest behavior.
[ ] Inputs and outputs are clear.
[ ] Important steps have contracts.
[ ] Expected grain is understood.
[ ] Validation exists at important boundaries.
[ ] Bronze/silver/gold responsibilities are clear.
[ ] Naming conventions are consistent.
[ ] Processing is partition-scoped where appropriate.
[ ] CLI is thin.
[ ] Pipeline code is callable independently of the CLI.
[ ] Pure transformations have unit tests.
[ ] Pipeline flow has an integration test.
[ ] Determinism has been tested.
[ ] Repeated execution has been compared.
[ ] Notebook exploration is separated from production execution.
[ ] Environment-specific behavior is outside core transformation logic.
[ ] The design is simple enough to understand.
```

---

# 36. Interview Questions

## Basic

### What is ETL?

ETL means Extract, Transform, Load. Data is obtained from a source, transformed, and persisted to a target. The architectural value comes from separating those responsibilities.

### Why separate extract, transform, and load?

Separation makes dependencies explicit and improves testing, debugging, reuse, and infrastructure independence.

### What is a pure transformation?

A transformation whose result is determined by explicit inputs and that does not secretly modify external state.

## Intermediate

### Why should `datetime.now()` normally not be used inside a transformation?

It introduces hidden execution time as an input, making historical reruns potentially produce different results.

### What is RunContext?

An explicit object carrying run-specific information such as run ID, data interval, environment, and configuration.

### Why keep I/O at the edges?

I/O is side-effecting and infrastructure-dependent. Isolating it keeps the transformation core easier to test and reason about.

## Advanced

### How would you redesign a 2,000-line ETL script?

Identify responsibilities, extract readers/writers, isolate pure transformation steps, introduce explicit run context and contracts, define partition scope, and add tests before adding further abstraction.

### How would you make a transformation deterministic?

Remove hidden inputs such as current time, uncontrolled randomness, global state, vague “latest” queries, and unstable ordering. Make required context explicit.

### How would you design partition-scoped processing?

Define an explicit data interval, map it to input/output partitions, ensure every step uses that interval, and make the output ownership explicit.

## Senior / Architecture

### How would you structure a transformation platform used by hundreds of datasets?

Start with stable boundaries and explicit contracts. Introduce shared execution infrastructure and configuration only where repeated patterns justify it. Keep dataset-specific business logic separate and provide controlled escape hatches.

### What belongs in the transformation layer versus the orchestrator?

Transformation code defines how data changes. The orchestrator coordinates scheduling, dependencies, retries, and operational execution.

### How would you prove determinism?

Hold input, run context, configuration, and logic version constant; execute repeatedly; compare outputs using byte equality where appropriate or semantic equality when serialization can vary.

---

# 37. Architecture Exercise

## Design a bronze → silver framework for an orders platform

Design a framework that:

- reads one orders partition,
- standardizes it,
- casts types,
- removes within-batch duplicates,
- flags invalid rows,
- validates the result,
- writes one silver partition,
- can be called from a CLI,
- can later be called by an orchestrator,
- can be unit and integration tested.

### Model architecture

```text
CLI / Orchestrator
        ↓
RunContext
        ↓
orders_silver pipeline
        ↓
Reader
        ↓
standardise
        ↓
cast_types
        ↓
deduplicate_within_batch
        ↓
flag_invalid
        ↓
contract validation
        ↓
Writer
        ↓
silver/orders/date=X
```

### Senior reasoning

- The reader owns source I/O.
- The transformation steps own data logic.
- RunContext owns explicit execution context.
- Validation checks known assumptions.
- The writer owns persistence.
- The CLI only selects and invokes the pipeline.
- The interval defines what the run owns.
- Repeated runs with identical inputs/context should be equivalent.
- The design can later be invoked by an orchestrator without moving business logic into orchestration code.

---

# 38. Progressive Learning Exercises

## Level 1 — Foundation

Implement:

```text
rename_columns()
cast_amount()
normalise_status()
flag_invalid_amount()
calculate_tax()
```

For each, identify inputs, outputs, hidden dependencies, and side effects.

## Level 2 — Pipeline Structure

Build:

```text
reader → transform → writer
```

Use a small Parquet dataset.

Requirement:

```text
No transformation function writes a file.
```

## Level 3 — RunContext

Add:

```python
RunContext(
    run_id=...,
    data_interval_start=...,
    data_interval_end=...,
    env=...,
    config=...,
)
```

Use it to determine the partition.

## Level 4 — Determinism

Run one historical partition twice and compare the outputs.

Then deliberately add `datetime.now()` and observe why the deterministic test fails.

## Level 5 — Production Refactoring

Take a messy ETL script and classify every operation as:

```text
I/O
business logic
configuration
validation
time dependency
entry-point logic
```

Move each operation to the correct boundary.

## Level 6 — Architecture

Design a reusable transformation structure for:

```text
orders
customers
products
payments
```

Explain every shared abstraction.

---

# 39. Relationship to the Rest of Module 2.12

Topic 01 establishes the foundation:

```text
01 Structuring ETL code
        ↓
02 Deduplication and merge-based loads
        ↓
03 Incremental processing and backfills
        ↓
04 Late-arriving data and reprocessing windows
        ↓
05 Hashing
        ↓
06 Lookups and enrichment
        ↓
07 Metadata/config-driven pipelines
        ↓
08 Checkpoints and resumability
        ↓
09 dbt
```

This chapter deliberately does **not** teach those later topics in depth.

Instead, it establishes why they need:

- explicit inputs,
- explicit intervals,
- deterministic transformations,
- clear contracts,
- isolated side effects,
- composable steps,
- and partition ownership.

---

# 40. Final Mental Model

A production transformation pipeline should be:

```text
Explicit
Deterministic
Partition-scoped
Testable
Composable
Observable
Easy to rerun
Easy to backfill
Independent of infrastructure where possible
```

**Explicit** means dependencies and execution context are visible.

**Deterministic** means the same inputs and context produce the same logical output.

**Partition-scoped** means the pipeline knows which data interval it owns.

**Testable** means pure transformation behavior can be tested without external infrastructure.

**Composable** means meaningful steps can be combined into a pipeline.

**Observable** means the run, interval, boundaries, and outputs are understandable.

**Easy to rerun** means a historical interval can be executed deliberately.

**Easy to backfill** means historical intervals can use the same transformation structure.

**Infrastructure-independent where possible** means business logic does not need to know whether data came from Parquet, a database, or another storage system.

---

# 41. Exit Criteria

Do not mark these automatically. They are learner self-assessment criteria.

```text
[ ] I can separate extract, transform, and load responsibilities.
[ ] I can write pure transformation functions.
[ ] I can keep side effects at the edges.
[ ] I can design a RunContext.
[ ] I understand data intervals and logical dates.
[ ] I can make transformations deterministic.
[ ] I can avoid hidden now()/random()/global state.
[ ] I can structure bronze → silver → gold transformations.
[ ] I can define step input/output contracts.
[ ] I can identify expected grain.
[ ] I can choose an appropriate transformation engine.
[ ] I can design partition-scoped transformations.
[ ] I can create a thin CLI entry point.
[ ] I can identify ETL pipeline anti-patterns.
[ ] I can unit-test pure transformations.
[ ] I can integration-test a complete pipeline.
[ ] I can prove repeated runs produce equivalent results.
[ ] I can explain functional data engineering.
[ ] I can explain the architecture to another Data Engineer.
```

---

# 42. Final Review Questions

Before moving to Topic 02, explain these without looking at the chapter:

1. Why should a reader not contain business transformation logic?
2. What makes a transformation pure?
3. Why are side effects kept at the edges?
4. What problem does RunContext solve?
5. What is the difference between execution time and data interval?
6. Why can `datetime.now()` break reproducibility?
7. What sources of nondeterminism should you look for?
8. What belongs in a step contract?
9. Why does expected grain matter?
10. When might SQL, Polars, or pandas be appropriate?
11. Why is partition scope useful?
12. Why should a CLI be thin?
13. Why are notebooks useful for exploration but risky as the sole production pipeline?
14. How do you unit-test a pure transformation?
15. How do you prove two executions are equivalent?
16. How does this architecture prepare for idempotency and incremental processing?

---

# 43. One-Sentence Principle

> **Build transformation pipelines so that explicit inputs and run context flow through deterministic business logic, while source and target side effects remain at deliberate boundaries.**
