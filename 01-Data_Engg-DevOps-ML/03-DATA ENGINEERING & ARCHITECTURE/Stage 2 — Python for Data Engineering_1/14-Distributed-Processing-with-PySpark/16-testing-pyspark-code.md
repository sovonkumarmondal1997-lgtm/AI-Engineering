# Testing PySpark Code

> **Module 2.14 — Distributed Processing with PySpark | Topic 16**
>
> Final technical topic of the module.
>
> **Core principle:** business logic should be implemented as small, testable `DataFrame → DataFrame` transformations, while SparkSession creation, I/O, configuration, and orchestration remain in thin entry points.

---

## 1. Learning Objectives

By the end of this topic, you should be able to:

- Design PySpark code that is easy to unit test.
- Separate transformation logic from I/O and orchestration.
- Separate SparkSession lifecycle from business logic.
- Build reusable pytest Spark fixtures.
- Use tiny deterministic DataFrames with explicit schemas.
- Compare DataFrames and schemas correctly.
- Test NULLs, empty inputs, duplicates, timestamps, and ANSI-mode failures.
- Test Python UDFs and pandas UDFs at appropriate levels.
- Test Spark SQL and temporary views.
- Build local-file and MinIO integration tests.
- Validate outputs with data-quality assertions and Pandera where supported by the installed environment.
- Write targeted plan-regression tests for critical performance contracts.
- Protect broadcast joins and predicate pushdown without brittle full-plan comparisons.
- Keep Spark test suites fast enough for CI/CD.
- Use careful parallel test execution.
- Understand Spark Connect as an advanced testing/client option.
- Apply property-based testing to transformation invariants.
- Debug flaky and failing Spark tests systematically.
- Design a production-grade testing strategy.

### The learning loop

```text
UNDERSTAND
    ↓
DESIGN
    ↓
WRITE SMALL TEST DATA
    ↓
WRITE TRANSFORMATION
    ↓
WRITE ASSERTION
    ↓
RUN TEST
    ↓
READ FAILURE
    ↓
DEBUG
    ↓
FIX
    ↓
RE-RUN
    ↓
REFACTOR
    ↓
INTEGRATE
    ↓
PROTECT PERFORMANCE
    ↓
AUTOMATE
```

---

## 2. Why Testing PySpark Is Different

A normal Python function can often be tested with:

```python
assert add(2, 3) == 5
```

PySpark adds additional dimensions:

- distributed execution,
- lazy evaluation,
- schemas,
- NULL semantics,
- row ordering,
- floating-point behavior,
- JVM/Python boundaries,
- SparkSession lifecycle,
- SQL,
- UDFs,
- file/object-store I/O,
- physical execution plans,
- version-sensitive optimizer behavior.

A test therefore has to distinguish at least three questions:

```text
Is the result correct?
        ↓
Is the schema correct?
        ↓
Is the execution behavior acceptable?
```

These are related but different contracts.

### Example

```python
actual.collect() == expected.collect()
```

can be fragile because:

- row order may not be semantically meaningful,
- schemas can differ while values look similar,
- NULL handling matters,
- floating-point results may need tolerance,
- large collections can overload the driver.

This does **not** mean `collect()` is forbidden.

For tiny test data, bounded `collect()` can be perfectly reasonable. It becomes dangerous when it is unbounded or used against production-scale data.

---

## 3. The Core Testability Principle

A production job commonly looks like:

```text
Input
  ↓
Read
  ↓
Transform
  ↓
Write
```

A testable architecture looks like:

```text
Thin Entry Point
      ↓
Read
      ↓
Pure/Testable Transformations
      ↓
Write
```

Then the unit test becomes:

```text
Small DataFrame
      ↓
Transformation
      ↓
Expected DataFrame
      ↓
Assertion
```

The architectural goal is:

```text
BUSINESS LOGIC
        ↓
DataFrame → DataFrame
        ↓
Easy unit testing

I/O + SparkSession + orchestration
        ↓
Thin integration boundary
```

The more business logic is mixed with:

- file paths,
- database connections,
- environment variables,
- SparkSession construction,
- writes,
- external services,

the harder it becomes to test deterministically.

---

## 4. Unit Tests vs Integration Tests vs Plan Regression Tests

| Test type | Main purpose | Data | I/O | Typical speed |
|---|---|---|---|---|
| Unit | Transformation correctness | Tiny | Minimal | Fast |
| Integration | Components work together | Small realistic | Real/local/object storage | Slower |
| Plan regression | Protect critical execution behavior | Tiny/controlled | Minimal | Fast/moderate |
| Property-based | Validate general invariants | Generated | Usually minimal | Variable |

You need all of them.

### Unit test

Answers:

> "Does this transformation produce the correct result?"

### Integration test

Answers:

> "Do the real components work together?"

### Plan regression test

Answers:

> "Is Spark still executing this critical workload according to an important performance contract?"

### Property-based test

Answers:

> "Does this transformation preserve a property across many valid inputs?"

Do not turn every test into an end-to-end test.

---

## 5. Designing Testable PySpark Code

### Bad design

```python
from pyspark.sql import SparkSession

def run_job():
    spark = SparkSession.builder.getOrCreate()

    df = spark.read.parquet("/data/sales")

    result = (
        df.filter("status = 'COMPLETED'")
          .withColumn("net", df.amount - df.discount)
          .groupBy("customer_id")
          .sum("net")
    )

    result.write.mode("overwrite").parquet("/data/output")
```

Problems:

- session creation is embedded,
- input path is embedded,
- transformation logic is embedded,
- output is embedded,
- I/O cannot easily be isolated,
- unit tests require filesystem setup.

### Refactored design

```python
from pyspark.sql import DataFrame


def transform_sales(df: DataFrame) -> DataFrame:
    return (
        df.filter("status = 'COMPLETED'")
          .withColumn("net", df.amount - df.discount)
          .groupBy("customer_id")
          .sum("net")
    )


def run_job(spark, input_path: str, output_path: str) -> None:
    df = spark.read.parquet(input_path)
    result = transform_sales(df)
    result.write.mode("overwrite").parquet(output_path)
```

Now the transformation can be tested independently.

### Test

```python
def test_transform_sales(spark):
    input_df = ...
    expected_df = ...

    actual_df = transform_sales(input_df)

    assertDataFrameEqual(actual_df, expected_df)
```

The exact assertion options available depend on the installed Spark version.

---

## 6. Pure DataFrame → DataFrame Transformations

In this module, "pure" means the transformation is designed to behave predictably from its explicit inputs.

Prefer:

```python
def clean_customers(df):
    return (
        df.filter("customer_id IS NOT NULL")
          .dropDuplicates(["customer_id"])
    )
```

Avoid hidden behavior such as:

```python
def clean_customers(df):
    spark = SparkSession.builder.getOrCreate()
    other = spark.read.parquet(os.environ["OTHER_DATA"])
    ...
```

The second function has hidden dependencies.

### Characteristics of good transformation functions

- Input is explicit.
- Output is explicit.
- No hidden file reads.
- No hidden writes.
- No SparkSession creation.
- No global mutable state.
- Configuration is explicit where practical.
- Business behavior is observable from the function contract.

### Important nuance

A Spark transformation is still lazy.

Testing a function can therefore build a DataFrame plan without executing it until an assertion/action requires execution.

That is useful: the test controls when execution happens.

---

## 7. Thin Job Entry Points

A production entry point can own:

```text
configuration
    ↓
SparkSession
    ↓
input read
    ↓
transform
    ↓
output write
```

Example:

```python
def main(spark, input_path, output_path):
    source = spark.read.parquet(input_path)
    result = transform_sales(source)
    result.write.mode("overwrite").parquet(output_path)
```

The entry point is intentionally thin.

This produces two testing layers:

```text
Unit tests
    ↓
transform_sales()

Integration tests
    ↓
main()
```

### Dependency injection

Passing `spark`, paths, or configuration explicitly can make tests easier.

Instead of:

```python
def run_job():
    spark = SparkSession.builder.getOrCreate()
```

prefer:

```python
def run_job(spark, input_path, output_path):
    ...
```

The test owns the Spark fixture.

---

## 8. Separating I/O From Transformation Logic

A useful architecture is:

```text
read_sales()
      ↓
transform_sales()
      ↓
validate_sales()
      ↓
write_sales()
```

Only the transformation should require no external system.

### Why this matters

If a test fails, you can quickly determine whether the failure is:

- transformation logic,
- input data,
- configuration,
- I/O,
- output validation.

This is dramatically easier than debugging one giant function.

---

## 9. pytest Fundamentals for PySpark

pytest provides:

- test discovery,
- assertions,
- fixtures,
- parametrization,
- setup/teardown,
- markers,
- failure reporting.

Basic test:

```python
def test_addition():
    assert 1 + 1 == 2
```

PySpark test:

```python
def test_filter_completed_orders(spark):
    df = ...
    actual = filter_completed_orders(df)

    assert actual.count() == 2
```

For production-quality DataFrame comparisons, prefer the Spark testing utilities covered later.

### Naming

Prefer:

```python
def test_transform_sales_excludes_cancelled_orders():
    ...
```

over:

```python
def test_job():
    ...
```

Test names are documentation.

---

## 10. Session-Scoped SparkSession Fixture

A common test fixture is:

```python
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("pytest-pyspark")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )

    yield spark

    spark.stop()
```

### Why session scope?

Starting Spark repeatedly is expensive.

Instead of:

```text
test 1 → Spark startup
test 2 → Spark startup
test 3 → Spark startup
```

use:

```text
pytest session
      ↓
one reusable SparkSession
      ↓
many tests
```

### Why these settings?

`local[2]`:

- provides limited local parallelism,
- keeps tests small,
- avoids pretending the test suite is a production cluster.

Small `spark.sql.shuffle.partitions`:

- reduces unnecessary test task counts,
- is appropriate for tiny test data.

`spark.ui.enabled=false`:

- avoids unnecessary UI overhead in test runs,
- removes a diagnostic surface that is generally unnecessary for normal unit tests.

UTC:

- reduces timezone-dependent surprises.

### Version awareness

Configuration names and behavior must be verified against the installed Spark version. Do not assume every configuration is identical across Spark distributions.

Check:

```python
print(spark.version)
```

---

## 11. One SparkSession Per Test Run

A session-scoped fixture improves test speed, but it does not eliminate test isolation concerns.

Potential shared state includes:

- temporary views,
- SQL configuration,
- cached data,
- filesystem state,
- environment variables.

Therefore:

```text
Reuse SparkSession
+
Isolate test state
```

is better than:

```text
New SparkSession for everything
```

and better than:

```text
One global mutable state with no cleanup
```

### Cleanup examples

```python
spark.catalog.dropTempView("sales")
```

or use unique view names per test.

---

## 12. Building Tiny Test DataFrames

Small test data is a feature, not a limitation.

Example:

```python
from pyspark.sql.types import (
    StructType,
    StructField,
    LongType,
    StringType,
    DoubleType,
)

schema = StructType([
    StructField("customer_id", LongType(), False),
    StructField("status", StringType(), True),
    StructField("amount", DoubleType(), True),
])

data = [
    (1, "COMPLETED", 100.0),
    (2, "CANCELLED", 50.0),
    (3, "COMPLETED", 75.0),
]

df = spark.createDataFrame(data, schema)
```

Small datasets make failures:

- fast,
- readable,
- deterministic,
- easy to reason about.

A five-row dataset can expose a logic bug just as effectively as five million rows.

---

## 13. Explicit Schemas in Tests

Explicit schemas make tests more precise.

Useful types include:

- `StringType`
- `IntegerType`
- `LongType`
- `DoubleType`
- `BooleanType`
- `DateType`
- `TimestampType`
- `DecimalType`
- `StructType`
- `ArrayType`
- `MapType`

Example:

```python
from pyspark.sql.types import (
    DecimalType,
    StructField,
    StructType,
    StringType,
)

schema = StructType([
    StructField("product_id", StringType(), False),
    StructField("price", DecimalType(12, 2), True),
])
```

### Why explicit schemas matter

They let tests detect:

- accidental type inference,
- unexpected nullability,
- decimal changes,
- timestamp changes,
- schema evolution.

---

## 14. DataFrame Equality

Modern Spark provides testing helpers under `pyspark.testing`.

Example:

```python
from pyspark.testing import assertDataFrameEqual

assertDataFrameEqual(actual, expected)
```

Use the installed Spark version's documentation to verify the exact supported signature and options.

### Why not compare `collect()` blindly?

This:

```python
assert actual.collect() == expected.collect()
```

can accidentally encode row ordering into a test.

It also does not provide the same semantic comparison capabilities as the Spark testing helpers.

### When bounded collection is reasonable

For a tiny unit test:

```python
rows = actual.limit(10).collect()
```

can be useful for diagnostics.

The problem is uncontrolled collection:

```python
actual.collect()
```

against a potentially large DataFrame.

---

## 15. Schema Equality

Use:

```python
from pyspark.testing import assertSchemaEqual

assertSchemaEqual(actual.schema, expected.schema)
```

A schema assertion protects against regressions such as:

```text
customer_id: long
```

silently becoming:

```text
customer_id: string
```

or a timestamp becoming a date.

Schema is part of the data contract.

### What to inspect

- names,
- data types,
- nested structure,
- nullability where relevant,
- ordering where semantically relevant.

---

## 16. Order-Insensitive DataFrame Comparisons

Distributed processing does not automatically imply a meaningful row order.

For an aggregation:

```python
actual:
customer 2
customer 1
```

may be logically equivalent to:

```python
expected:
customer 1
customer 2
```

if the contract does not specify ordering.

Use the appropriate order-related option supported by your installed `assertDataFrameEqual`.

### When order matters

Order matters when the transformation explicitly defines it, for example:

- top-N results,
- ranking,
- ordered windows,
- deterministic report output.

A test should reflect the business contract rather than accidentally enforce physical execution order.

---

## 17. Floating-Point Tolerances

Floating-point calculations can produce tiny representation differences.

For example:

```text
expected = 0.3
actual   = 0.30000000000000004
```

Exact equality can therefore be unnecessarily brittle.

Use the supported tolerance options of the installed Spark testing API.

### Principle

```text
Numerical contract
        ↓
acceptable tolerance
        ↓
test
```

Do not use an arbitrarily large tolerance merely to make tests pass.

The tolerance should reflect the business/numerical requirement.

---

## 18. Testing NULLs

NULL is not the same as an ordinary value.

Test:

```text
NULL input
↓
expected NULL behavior
```

Example:

```python
data = [
    (1, None),
    (2, "A"),
]
```

Important cases include:

- `col.isNull()`,
- `col.isNotNull()`,
- `when`,
- `coalesce`,
- aggregation behavior,
- join behavior.

Example:

```python
result = df.withColumn(
    "label",
    F.coalesce("label", F.lit("UNKNOWN"))
)
```

Test both:

- NULL input,
- non-NULL input.

---

## 19. Empty DataFrames

An empty DataFrame is not necessarily invalid.

Test:

```text
0 rows
+
expected schema
```

Important cases:

- filtering everything out,
- empty aggregation,
- empty join,
- empty output,
- schema preservation.

Example:

```python
empty_df = spark.createDataFrame([], schema)
```

A good test checks that the transformation behaves intentionally when no records exist.

---

## 20. Duplicate Records

Duplicates often expose incorrect assumptions.

Test:

```text
duplicate rows
duplicate business keys
```

Example:

```python
data = [
    (1, "A"),
    (1, "A"),
    (2, "B"),
]
```

If the business rule is deduplication:

```python
result = df.dropDuplicates(["id"])
```

The test should verify the business key contract, not just one sample row.

---

## 21. Time-Zone Boundary Testing

Time bugs frequently appear at boundaries.

Test:

- UTC,
- midnight,
- date-to-timestamp conversion,
- timestamp truncation,
- daylight-saving-related boundaries where relevant.

Keep the default shared test session in UTC:

```python
.config("spark.sql.session.timeZone", "UTC")
```

When a test intentionally validates another timezone, make the timezone explicit.

### Determinism

Avoid tests based on uncontrolled current time:

```python
now = datetime.now()
```

Prefer a fixed timestamp:

```python
fixed_timestamp = "2026-01-01 00:00:00"
```

---

## 22. Testing ANSI-Mode Errors

Modern Spark can use ANSI behavior where invalid operations can raise errors rather than silently producing NULL-like results.

Behavior is version/configuration sensitive.

A pytest pattern is:

```python
import pytest


def test_invalid_cast_raises(spark):
    with pytest.raises(Exception):
        spark.sql(
            "SELECT CAST('not-a-number' AS INT)"
        ).collect()
```

For production-quality tests, prefer a stable exception class or characteristic when the installed version provides one rather than asserting a brittle complete error string.

### Verify configuration

Do not assume ANSI settings:

```python
print(spark.conf.get("spark.sql.ansi.enabled"))
```

if the configuration exists in your installed Spark version.

---

## 23. Testing Python UDFs

Use two levels.

### Level 1 — Test the Python function directly

```python
def normalize_email(value):
    if value is None:
        return None
    return value.strip().lower()
```

Test:

```python
def test_normalize_email():
    assert normalize_email(" A@EXAMPLE.COM ") == "a@example.com"
    assert normalize_email(None) is None
```

This is extremely fast.

### Level 2 — Test the UDF inside Spark

```python
from pyspark.sql import functions as F
from pyspark.sql.types import StringType


normalize_email_udf = F.udf(
    normalize_email,
    StringType(),
)
```

Then:

```python
result = df.withColumn(
    "normalized",
    normalize_email_udf("email"),
)
```

The Spark-level test protects:

- UDF registration,
- Spark input/output types,
- NULL integration,
- actual DataFrame behavior.

---

## 24. Testing pandas UDFs

For pandas UDFs, test:

- input/output values,
- data types,
- NULL behavior where applicable,
- grouping behavior,
- batch assumptions,
- edge cases.

Do not duplicate the entire Topic 11 implementation lesson here.

The testing strategy is:

```text
Python-level logic
      +
Spark integration
      +
small deterministic input
```

For complex pandas UDFs, test the core Python logic independently where practical, then use Spark tests to verify integration.

---

## 25. Testing Spark SQL

A simple SQL test:

```python
from pyspark.testing import assertDataFrameEqual


def test_sales_sql(spark):
    schema = ...
    df = spark.createDataFrame(
        [(1, 10.0), (1, 5.0), (2, 7.0)],
        schema,
    )

    df.createOrReplaceTempView("sales")

    actual = spark.sql("""
        SELECT customer_id, SUM(amount) AS total
        FROM sales
        GROUP BY customer_id
    """)

    expected = spark.createDataFrame(
        [(1, 15.0), (2, 7.0)],
        ["customer_id", "total"],
    )

    assertDataFrameEqual(actual, expected)
```

The SQL is now tested without reading production data.

---

## 26. Temporary Views and Test Isolation

Temporary views are scoped to the Spark session/context according to Spark's view semantics.

That means test suites using one session must avoid stale view state.

### Safer pattern

Use unique names:

```python
view_name = "sales_test_case_001"
df.createOrReplaceTempView(view_name)
```

or clean up:

```python
spark.catalog.dropTempView(view_name)
```

### Global temporary views

Global temporary views have different scope semantics and are intentionally accessed through the global temporary namespace.

For normal unit tests, ordinary temporary views are generally easier to reason about.

---

## 27. SQL Edge Cases

Do not test only:

```text
normal rows
```

Also test:

- NULL values,
- duplicates,
- empty input,
- unmatched joins,
- multiple matches,
- aggregation,
- date boundaries.

Example join test:

```text
fact row with no dimension match
```

should explicitly test the expected result.

SQL correctness includes semantics, not just syntax.

---

## 28. Integration Testing

An integration test connects real components:

```text
Sample Input
    ↓
Spark Read
    ↓
Transformations
    ↓
Spark Write
    ↓
Output Read
    ↓
Validation
```

Use integration tests for:

- file formats,
- paths,
- object storage,
- configuration,
- complete job wiring,
- output layout.

Do not use integration tests for every transformation branch.

---

## 29. Local File Integration Tests

A good local integration test:

1. creates temporary input,
2. runs the real job,
3. reads output,
4. validates output,
5. cleans up.

Example pattern:

```python
from pathlib import Path


def test_daily_job_with_local_files(spark, tmp_path):
    input_path = tmp_path / "input"
    output_path = tmp_path / "output"

    source = spark.createDataFrame(
        [(1, "A")],
        ["id", "value"],
    )

    source.write.mode("overwrite").parquet(str(input_path))

    run_job(
        spark,
        str(input_path),
        str(output_path),
    )

    result = spark.read.parquet(str(output_path))

    assert result.count() == 1
```

The exact job contract determines the correct assertions.

---

## 30. MinIO Integration Testing

MinIO is useful for testing S3-compatible object-storage workflows locally.

Conceptual flow:

```text
pytest
 ↓
MinIO sample input
 ↓
Spark job
 ↓
MinIO output
 ↓
Read output
 ↓
DataFrame assertions
 ↓
Data-quality validation
```

This catches problems that local filesystem tests may miss:

- object-store paths,
- S3-compatible configuration,
- credentials,
- connector behavior,
- object-store semantics.

### Important

Do not hard-code credentials in tests.

Use environment/configuration mechanisms appropriate for the test environment.

Do not modify the project's MinIO configuration as part of this learning file.

---

## 31. Output Validation

A test should distinguish:

```text
Did the job produce the expected DataFrame?
```

from:

```text
Does the output satisfy the business data contract?
```

Examples of output contracts:

- required columns exist,
- business key is non-null,
- values fall within valid ranges,
- uniqueness holds,
- row counts are reasonable.

This is where Module 2.11's data-quality concepts connect to Spark testing.

---

## 32. Data Quality Validation with Pandera

Pandera can express data-quality expectations where the installed version/environment supports the relevant PySpark functionality.

Conceptually:

```text
Spark output
    ↓
Schema validation
    ↓
Business constraints
    ↓
Pass / fail
```

Examples:

- required column exists,
- numeric value is non-negative,
- business key is non-null,
- category belongs to an allowed set.

### Equality vs quality

DataFrame equality asks:

> "Did I get this expected dataset?"

Pandera-style validation asks:

> "Does this output satisfy the data contract?"

You need both when the expected dataset alone is insufficient.

---

## 33. Plan Regression Testing

A correctness test can pass while performance silently deteriorates.

Example:

```text
Yesterday:
BroadcastHashJoin

Today:
SortMergeJoin
+
large Exchange
```

The rows can still be correct.

A plan regression test protects a performance contract.

### Useful contracts

- expected broadcast join,
- expected predicate pushdown,
- expected partition filtering,
- absence of unexpected Cartesian product,
- absence of clearly prohibited execution patterns.

Use these selectively.

Do not test every internal operator.

---

## 34. Broadcast Join Regression Tests

A conceptual test:

```python
def test_fact_dimension_join_uses_broadcast(spark):
    fact = spark.range(0, 1000).withColumn("key", F.col("id") % 10)
    dim = spark.createDataFrame(
        [(i, f"v{i}") for i in range(10)],
        ["key", "value"],
    )

    result = fact.join(F.broadcast(dim), "key")

    plan = result._jdf.queryExecution().executedPlan().toString()

    assert "Broadcast" in plan
```

### Important warning

Do not treat the exact plan string as a stable public contract.

The plan can vary due to:

- Spark version,
- statistics,
- AQE,
- configuration,
- data size,
- optimizer changes.

A production plan test should assert the **smallest meaningful characteristic**.

For example, if a broadcast join is a real performance contract, detect the relevant broadcast operator/strategy rather than comparing the entire plan character-for-character.

Internal JVM access is version-sensitive; verify it against the installed Spark release.

---

## 35. Predicate Pushdown Regression Tests

Suppose a Parquet filter is expected to push down.

The result can remain correct if pushdown disappears.

That is a performance regression.

Inspect plan evidence such as:

```text
PushedFilters
PartitionFilters
```

### Test design

Use a tiny Parquet dataset and a selective predicate.

Then inspect the explain/physical plan for the relevant scan characteristics.

Do not assert the complete formatted plan string.

### Why?

Spark's physical representation can change while preserving the same important performance contract.

---

## 36. Plan Test Design

### Good

- Assert a broadcast characteristic when broadcast is contractual.
- Assert partition filtering when it is contractual.
- Assert pushdown where it materially protects performance.
- Assert absence of Cartesian execution when prohibited.

### Bad

```python
assert actual_plan == huge_expected_plan_string
```

Why?

A harmless Spark upgrade could change:

- formatting,
- operator IDs,
- internal details,
- adaptive representation.

A good plan test is:

```text
specific
+
minimal
+
stable
+
version-aware
+
performance-relevant
```

---

## 37. Fast Spark Test Suites

A 45-minute test suite will not be run consistently by developers.

Optimize for fast feedback.

Use:

- tiny datasets,
- one session per test run,
- local execution,
- small shuffle partitions,
- minimal I/O,
- targeted integration tests,
- carefully selected parallelism.

### Test pyramid

```text
             E2E / Integration
                  /\
                 /  \
                /    \
               /------\
              /  Plan  \
             /Regression\
            /------------\
           /    Unit      \
          /     Tests      \
         /------------------\
```

Most tests should be unit tests.

Integration and plan-regression tests should exist where they provide additional confidence.

---

## 38. Parallel Test Processes

Tools such as pytest-xdist can run independent tests in multiple Python processes.

Potential benefit:

```text
Test A ─┐
Test B ─┼─ parallel
Test C ─┤
Test D ─┘
```

But Spark is resource-intensive.

Parallelism can become slower because of:

- CPU contention,
- memory contention,
- multiple JVMs,
- multiple Spark sessions,
- port conflicts,
- disk contention.

Therefore:

> Measure parallel test execution instead of assuming it is faster.

---

## 39. Spark Connect for Testing

Spark Connect introduces a client/server architecture:

```text
Python Client
      ↓
Spark Connect
      ↓
Spark Server
      ↓
Spark Execution
```

Potential testing benefits include lighter clients and separation between client process and Spark execution.

But:

- APIs can be version-sensitive,
- not every local testing pattern maps identically,
- server/client compatibility matters.

Treat Spark Connect as an advanced option, not a requirement for ordinary unit tests.

Verify behavior against the installed Spark version.

---

## 40. Property-Based Testing

Example-based testing:

```text
input A → expected A
input B → expected B
input C → expected C
```

Property-based testing:

```text
many generated inputs
        ↓
invariant
        ↓
must hold
```

### Useful Spark transformation properties

For a deterministic filter:

```text
output row count <= input row count
```

For deduplication:

```text
deduplicate(deduplicate(df))
==
deduplicate(df)
```

For normalization:

```text
normalize(normalize(df))
==
normalize(df)
```

For required columns:

```text
required columns
must always exist
```

For required business keys:

```text
required key
must remain non-null
```

These are examples, not universal truths. The property must match business semantics.

---

## 41. Property-Based Testing of Transformations

A practical design is:

```text
Generate small valid input
        ↓
Apply transformation
        ↓
Check invariant
```

Example property:

```python
def assert_filter_does_not_increase_rows(input_df, output_df):
    assert output_df.count() <= input_df.count()
```

Then generate many input shapes.

For Spark, keep generated datasets intentionally small to avoid turning property tests into distributed performance tests.

Property-based testing is a bridge toward the deeper testing material in Module 2.19.

---

## 42. Determinism

A flaky test may depend on:

- randomness,
- current time,
- row order,
- timezone,
- external state,
- shared files,
- shared temporary views,
- parallel execution.

### Improve determinism

Use:

- fixed seeds where randomness is intentional,
- fixed timestamps,
- UTC defaults,
- explicit schemas,
- explicit ordering when ordering is contractual,
- temporary directories,
- isolated views,
- deterministic inputs.

Do not "fix" a flaky test by adding arbitrary sleeps.

---

## 43. Test Isolation

Each test should be independently runnable.

Avoid shared mutable state such as:

```text
test A creates temp view
test B assumes it exists
```

Instead:

```text
test A → setup → execute → cleanup
test B → setup → execute → cleanup
```

Isolation also applies to:

- MinIO objects,
- temporary files,
- databases,
- environment variables,
- caches.

---

## 44. CI/CD Strategy

A useful pipeline is:

```text
Pull Request
     ↓
Fast Unit Tests
     ↓
Plan Regression Tests
     ↓
Integration Tests
     ↓
Full Validation
```

Fast feedback should happen first.

Expensive tests can run:

- after unit tests,
- on protected branches,
- on scheduled builds,
- before release,
- or according to organizational risk.

Do not assume a particular CI platform.

### CI requirements

- pinned/controlled Spark version,
- reproducible Python environment,
- deterministic test data,
- useful failure diagnostics,
- controlled external services,
- cleanup.

---

## 45. Test Naming and Maintainability

Good:

```python
def test_transform_sales_excludes_cancelled_orders():
    ...
```

Good:

```python
def test_daily_job_writes_expected_schema_to_output():
    ...
```

Avoid:

```python
def test1():
    ...
```

A maintainable suite makes the failure understandable before opening the code.

### Test behavior, not implementation trivia

Prefer:

```text
cancelled orders are excluded
```

over:

```text
filter operation appears as the third expression
```

unless the latter is a deliberate performance contract.

---

## 46. Test Data Design

High-value test data targets behavior.

A useful matrix:

| Case | Purpose |
|---|---|
| Normal | Happy path |
| NULL | Missing values |
| Empty | No records |
| Duplicate | Data quality |
| Boundary | Limits |
| Invalid | Failure behavior |
| Multiple matches | Join/cardinality |
| Time boundary | Temporal correctness |

Do not make every dataset large.

Large datasets belong in performance/integration experiments, not ordinary unit tests.

---

## 47. Testing Expected Failures

Use pytest exception assertions:

```python
import pytest


def test_invalid_input_raises(spark):
    with pytest.raises(Exception):
        ...
```

Prefer stable exception types or stable error characteristics where possible.

Avoid:

```python
assert str(exc.value) == "some enormous exact version-specific string"
```

unless the exact message itself is part of the contract.

---

## 48. Common Testing Anti-Patterns

### 1. New SparkSession for every test

**Problem:** startup overhead.

**Better:** session-scoped fixture with state isolation.

### 2. Only end-to-end tests

**Problem:** slow failures and difficult diagnosis.

**Better:** unit + integration.

### 3. Only happy paths

**Problem:** production edge cases remain untested.

**Better:** NULL, empty, duplicate, invalid, boundary cases.

### 4. Huge unit-test datasets

**Problem:** slow and hard to debug.

**Better:** tiny targeted datasets.

### 5. Careless `collect()`

**Problem:** driver pressure.

**Better:** bounded collection or Spark testing utilities.

### 6. Accidental row-order dependence

**Problem:** nondeterministic failures.

**Better:** order-insensitive assertions unless order is contractual.

### 7. Ignoring schemas

**Problem:** type regressions pass unnoticed.

**Better:** schema assertions.

### 8. Exact floating-point equality

**Problem:** numerical fragility.

**Better:** meaningful tolerance.

### 9. Ignoring timezone

**Problem:** environment-dependent dates/times.

**Better:** UTC default and explicit timezone tests.

### 10. Hard-coded full plan strings

**Problem:** brittle across versions.

**Better:** minimal plan contracts.

### 11. Shared mutable state

**Problem:** test ordering affects results.

**Better:** setup/cleanup and isolation.

### 12. No integration tests

**Problem:** I/O failures reach production.

**Better:** targeted integration suite.

### 13. No plan regression tests

**Problem:** correctness can pass while critical performance behavior changes.

**Better:** protect only important execution contracts.

### 14. Expensive tests on every change

**Problem:** slow developer feedback.

**Better:** layered CI strategy.

### 15. No cleanup

**Problem:** stale data contaminates later tests.

**Better:** temporary resources and teardown.

### 16. Ignoring Spark upgrades

**Problem:** APIs/plans/configuration can change.

**Better:** version-controlled environment and version-aware tests.

### 17. Treating passing tests as proof of performance

**Problem:** correctness is not performance.

**Better:** plan contracts and performance experiments.

### 18. Treating code coverage as the only quality metric

**Problem:** high coverage can still miss meaningful cases.

**Better:** cover business invariants and failure modes.

### 19. Parallelizing blindly

**Problem:** resource contention can make tests slower.

**Better:** measure.

### 20. Treating Spark Connect as a magic speedup

**Problem:** architecture changes do not automatically make tests faster.

**Better:** evaluate it against actual test needs and installed versions.

---

## 49. Hands-On Labs

### Lab 1 — First PySpark pytest

**Objective:** write a minimal DataFrame test.

**Setup:** create a tiny DataFrame.

**Code:**

```python
def test_count(spark):
    df = spark.createDataFrame([(1,), (2,)], ["id"])
    assert df.count() == 2
```

**Expected behavior:** the test passes.

**Common failure:** Spark fixture is unavailable.

**Debug:** inspect `conftest.py`.

**Production lesson:** establish a repeatable test harness first.

---

### Lab 2 — Session-Scoped Fixture

**Objective:** create one reusable SparkSession.

**Setup:** use the fixture pattern from this chapter.

**Measure:** run several tests and record suite runtime.

**Lesson:** Spark startup cost matters.

---

### Lab 3 — Explicit Schema

**Objective:** build a typed test DataFrame.

**Assertion:** verify the expected schema.

**Failure:** inferred type differs from intended type.

**Lesson:** schemas are contracts.

---

### Lab 4 — DataFrame Equality

**Objective:** compare actual and expected DataFrames using `assertDataFrameEqual`.

**Include:** at least one NULL.

**Lesson:** use semantic DataFrame assertions rather than naive list comparisons.

---

### Lab 5 — Schema Equality

**Objective:** deliberately change one expected column type.

**Observe:** schema assertion fails.

**Lesson:** a correct-looking value set can still have the wrong schema.

---

### Lab 6 — Order-Insensitive Comparison

**Objective:** create identical logical results in different row orders.

**Task:** use the supported order-related comparison option.

**Lesson:** do not encode accidental physical order.

---

### Lab 7 — Floating-Point Tolerance

**Objective:** create a small aggregation with floating-point output.

**Task:** compare with an appropriate tolerance supported by the installed API.

**Lesson:** tolerance should reflect numerical requirements.

---

### Lab 8 — NULL Cases

Test:

- NULL input,
- non-NULL input,
- `coalesce`,
- conditional expressions.

**Lesson:** NULL semantics are part of correctness.

---

### Lab 9 — Empty DataFrame

Create an empty DataFrame with an explicit schema.

Test:

- filter,
- aggregation,
- output schema.

**Lesson:** empty input is a valid boundary condition.

---

### Lab 10 — Duplicate Records

Create duplicate business keys.

Test the expected deduplication behavior.

**Lesson:** data-quality assumptions should become executable tests.

---

### Lab 11 — Timezone Boundary

Use a fixed timestamp around midnight UTC.

Test conversion/truncation.

**Lesson:** time should be deterministic.

---

### Lab 12 — ANSI Error

Create an intentionally invalid operation.

Use `pytest.raises`.

**Lesson:** expected failures are testable behavior.

---

### Lab 13 — Python UDF

Test the Python function directly, then test the registered Spark UDF.

**Lesson:** separate fast logic tests from Spark integration tests.

---

### Lab 14 — pandas UDF

Use a tiny deterministic dataset.

Test values and edge cases.

**Lesson:** vectorized execution still needs correctness tests.

---

### Lab 15 — Spark SQL Temporary View

Create a view and run a SQL aggregation.

Compare against an expected DataFrame.

**Lesson:** SQL is another transformation interface that should be tested.

---

### Lab 16 — Local-File Integration

Write tiny Parquet input to a temporary path.

Run the real job.

Read output.

Validate result and schema.

**Lesson:** integration tests protect wiring and I/O.

---

### Lab 17 — MinIO Integration

Run a sample job against the project's MinIO environment.

Validate:

- input availability,
- output existence,
- output contents,
- cleanup.

**Lesson:** object-store integration can differ from local filesystem behavior.

---

### Lab 18 — Pandera Output Validation

Validate a produced DataFrame against a data-quality contract.

**Lesson:** correctness and data quality are related but distinct.

---

### Lab 19 — Broadcast Plan Regression

Build fact and small dimension DataFrames.

Inspect the plan.

Assert only the required broadcast characteristic.

**Lesson:** protect meaningful performance contracts without brittle full-plan assertions.

---

### Lab 20 — Predicate Pushdown Regression

Write a small Parquet dataset.

Apply a selective filter.

Inspect scan information such as `PushedFilters` where supported.

**Lesson:** a correct result can still hide a performance regression.

---

### Lab 21 — Property-Based Transformation

Define an invariant for a deterministic transformation.

Generate multiple small input cases.

Verify the invariant.

**Lesson:** properties generalize beyond hand-written examples.

---

### Lab 22 — Test Suite Optimization

Measure:

- baseline runtime,
- number of tests,
- Spark startup behavior,
- unit runtime,
- integration runtime.

Then change one factor.

Re-measure.

**Lesson:** test performance should itself be engineered.

---

## 50. Required Refactoring Exercise

Take one earlier Spark job.

### Before

```text
Job
 ├── SparkSession
 ├── Read
 ├── Transform
 ├── More Transform
 └── Write
```

### After

```text
main()
 ├── SparkSession
 ├── read()
 ├── transform_stage_1()
 ├── transform_stage_2()
 └── write()

Tests
 ├── test_transform_stage_1()
 ├── test_transform_stage_2()
 └── integration_test_job()
```

### Required outcome

Every meaningful transformation should be testable without external I/O.

### Measure

Record the original testability:

- how many components require I/O?
- how many transformations are directly testable?

Then record the refactored architecture.

---

## 51. Debugging Exercises

### Exercise 1 — Spark Fixture Recreated

**Symptom:** every test appears to start Spark.

**Investigation:** inspect fixture scope.

**Root cause:** function-scoped Spark fixture.

**Fix:** use an appropriate session-scoped fixture.

**Prevention:** keep fixture scope intentional.

---

### Exercise 2 — Equality Fails Due to Order

**Symptom:** values match but assertion fails.

**Investigation:** compare row order.

**Root cause:** unordered result compared as ordered.

**Fix:** use the supported order-insensitive comparison or explicitly sort when order is contractual.

**Prevention:** encode business semantics.

---

### Exercise 3 — Schema Assertion Fails

**Symptom:** values look correct.

**Investigation:** inspect `actual.schema` and `expected.schema`.

**Root cause:** type/nullability difference.

**Fix:** correct transformation or expected contract.

**Prevention:** explicit schemas.

---

### Exercise 4 — Floating-Point Failure

**Symptom:** values differ by tiny amounts.

**Investigation:** inspect numerical scale.

**Root cause:** floating-point representation/aggregation.

**Fix:** appropriate tolerance.

**Prevention:** define numerical contract.

---

### Exercise 5 — NULL Test Fails

**Symptom:** NULL input produces unexpected output.

**Investigation:** inspect `when`, comparisons, and `coalesce`.

**Root cause:** misunderstanding Spark NULL semantics.

**Fix:** encode intended NULL behavior.

**Prevention:** dedicated NULL cases.

---

### Exercise 6 — Empty Data Fails

**Symptom:** job works with normal data but fails on zero rows.

**Investigation:** inspect schema and aggregation behavior.

**Root cause:** empty input path not considered.

**Fix:** explicitly support or reject empty input according to business rules.

**Prevention:** empty-data tests.

---

### Exercise 7 — Duplicate Rows

**Symptom:** output contains duplicate business keys.

**Investigation:** trace joins and deduplication.

**Root cause:** cardinality assumption.

**Fix:** correct join/deduplication logic.

**Prevention:** duplicate test cases.

---

### Exercise 8 — Timezone Failure

**Symptom:** test passes locally but fails in CI.

**Investigation:** compare session timezone.

**Root cause:** environment-dependent timezone.

**Fix:** explicit UTC/default timezone and explicit alternate-timezone tests.

**Prevention:** fixed timestamps.

---

### Exercise 9 — ANSI Exception Missing

**Symptom:** expected exception is not raised.

**Investigation:** inspect ANSI configuration and Spark version.

**Root cause:** environment/configuration difference.

**Fix:** configure the test intentionally and verify behavior.

**Prevention:** version-aware tests.

---

### Exercise 10 — UDF Result Differs

**Symptom:** Python-level test passes but Spark-level test fails.

**Investigation:** compare input/output types and NULL behavior.

**Root cause:** Spark integration contract differs from pure Python function.

**Fix:** correct UDF return type or integration logic.

**Prevention:** two-level UDF tests.

---

### Exercise 11 — Stale Temporary View

**Symptom:** SQL test sees data from another test.

**Investigation:** inspect catalog/view lifecycle.

**Root cause:** shared session state.

**Fix:** unique names or cleanup.

**Prevention:** isolation discipline.

---

### Exercise 12 — MinIO Input Missing

**Symptom:** integration test cannot find input.

**Investigation:** verify endpoint, bucket, object key, credentials, and setup order.

**Root cause:** environment/setup issue.

**Fix:** controlled test setup.

**Prevention:** health/setup checks and unique test prefixes.

---

### Exercise 13 — Pandera Failure

**Symptom:** DataFrame equality passes but quality validation fails.

**Investigation:** inspect business constraints.

**Root cause:** expected values may be structurally correct but violate quality rules.

**Fix:** transformation or data-quality contract.

**Prevention:** validate business invariants.

---

### Exercise 14 — Broadcast Plan Regression

**Symptom:** expected broadcast no longer appears.

**Investigation:**

- Spark version,
- statistics,
- AQE,
- threshold/configuration,
- input size,
- query changes.

**Root cause possibilities:**

- real regression,
- changed data size,
- intentional optimizer change,
- brittle test.

**Fix:** determine which contract is actually required.

---

### Exercise 15 — Predicate Pushdown Disappears

**Symptom:** results remain correct but scan becomes expensive.

**Investigation:** inspect scan plan and `PushedFilters`/`PartitionFilters` where applicable.

**Root cause:** expression or source change.

**Fix:** restore pushdown-compatible logic where required.

**Prevention:** targeted plan regression test.

---

### Exercise 16 — Suite Becomes Slow

**Symptom:** tests grow from fast to slow.

**Investigation:**

- count tests,
- Spark startup,
- integration frequency,
- dataset size,
- parallelism.

**Fix:** move expensive work to integration layer, reuse session, shrink datasets.

**Prevention:** measure suite runtime continuously.

---

### Exercise 17 — Parallel Tests Exhaust Resources

**Symptom:** parallel execution is slower or unstable.

**Investigation:** CPU, memory, JVM count, Spark sessions.

**Root cause:** resource contention.

**Fix:** reduce worker count or isolate expensive tests.

**Prevention:** benchmark parallelism.

---

## 52. Test Performance Engineering

Measure the test suite like an engineering system.

Track:

- total runtime,
- unit-test runtime,
- integration-test runtime,
- plan-test runtime,
- Spark startup overhead,
- number of tests,
- parallel worker count.

Use:

```text
BASELINE
   ↓
ONE CHANGE
   ↓
MEASURE
   ↓
COMPARE
```

Do not invent benchmark numbers.

A target such as "about two minutes" can be a useful example for a project, but it is not a universal requirement.

---

## 53. Test Quality

Test quantity is not test quality.

A strong suite provides:

- meaningful coverage,
- boundary cases,
- business invariants,
- failure-mode coverage,
- maintainability,
- stability,
- useful diagnostics.

100 fragile tests can be worse than 30 high-value tests.

Do not reduce quality to code-coverage percentage.

---

## 54. Production Testing Scenarios

### Scenario 1 — Logic Inside `main()`

**Context:** all transformations live inside a single production function.

**Problem:** unit tests require real I/O.

**Design:** extract DataFrame → DataFrame functions.

**Trade-off:** refactoring effort.

**Validation:** unit tests run without external systems.

---

### Scenario 2 — 30-Minute Test Suite

**Context:** developers stop running tests locally.

**Evidence:** high Spark startup and integration overhead.

**Design:** session-scoped fixture, tiny datasets, test pyramid.

**Validation:** measure before/after.

---

### Scenario 3 — Every Test Creates Spark

**Context:** hundreds of tests.

**Problem:** startup overhead.

**Design:** one session per run with state isolation.

**Risk:** shared session state.

**Mitigation:** cleanup and unique names.

---

### Scenario 4 — Row Order Failure

**Context:** aggregation result is logically correct.

**Problem:** ordered list comparison fails.

**Design:** order-insensitive comparison unless order is contractual.

---

### Scenario 5 — Spark Upgrade Breaks Plan Test

**Context:** query remains correct.

**Problem:** exact plan string changed.

**Design:** replace brittle full-string assertion with minimal performance contract.

---

### Scenario 6 — Flaky MinIO Test

**Context:** object-storage integration fails intermittently.

**Investigation:** setup timing, object naming, credentials, cleanup, environment readiness.

**Design:** isolated prefixes and deterministic setup.

---

### Scenario 7 — Broadcast Silently Disappears

**Context:** fact-dimension query becomes slower.

**Design:** targeted broadcast plan contract.

**Validation:** inspect actual plan and workload changes before forcing behavior.

---

### Scenario 8 — Example Tests Miss Distribution Bug

**Context:** hand-written examples pass.

**Problem:** unexpected data distribution breaks production.

**Design:** property-based tests and targeted skew/cardinality cases.

---

### Scenario 9 — Only E2E Tests

**Context:** failures take 20 minutes to diagnose.

**Design:** extract unit-testable transformations.

**Result:** faster feedback and better failure localization.

---

### Scenario 10 — Property-Based Testing Introduction

**Context:** transformation has many input combinations.

**Design:** identify business invariants and generate small valid datasets.

**Trade-off:** more abstract failures require good shrinking/debugging practices.

---

## 55. Cross-Module Connections

### Module 2.11 — Data Validation, Contracts and Quality

Testing protects:

- schema contracts,
- Pandera checks,
- business constraints,
- NULL rules.

### Module 2.12 — Transformation Patterns and Pipeline Design

Testing directly reinforces:

- pure transformations,
- layered pipelines,
- idempotency,
- separation of concerns.

### Module 2.13 — Orchestration

Tests protect:

- job entry points,
- retries,
- task boundaries,
- integration behavior.

### Topics 01–15

Testing protects understanding from:

- driver/executor architecture,
- jobs/stages/tasks,
- DataFrames,
- lazy evaluation,
- joins,
- shuffle,
- partitioning,
- skew,
- caching,
- UDFs,
- Catalyst,
- AQE,
- data sources,
- bucketing,
- Spark UI,
- performance debugging.

Do not re-teach those topics here. Use tests to protect them.

---

## 56. Performance Contracts

There are two different contracts.

### Correctness contract

> "The output is correct."

### Performance contract

> "A critical execution behavior remains within an acceptable pattern."

Examples:

- expected broadcast join,
- expected partition pruning,
- expected predicate pushdown,
- no unexpected Cartesian product.

Performance contracts should be selective.

Do not make every optimizer decision a test.

---

## 57. Spark Version Awareness

This module targets modern Spark, but APIs and plan behavior are version-sensitive.

Verify:

```python
print(spark.version)
```

and:

```bash
python -c "import pyspark; print(pyspark.__version__)"
```

Verify against the installed version:

- `pyspark.testing` APIs,
- `assertDataFrameEqual`,
- `assertSchemaEqual`,
- order-related options,
- tolerance options,
- Spark Connect behavior,
- configuration names,
- plan representation.

Never invent API parameters.

Never assume an old Spark tutorial describes current Spark exactly.

---

## 58. No Fabricated Test Output

Do not invent:

- pytest output,
- test counts,
- execution times,
- Spark plans,
- MinIO behavior,
- benchmark improvements,
- memory usage.

If output is illustrative, label it:

> **Illustrative example — actual output may vary.**

Actual measurements must come from the learner's environment.

---

## 59. Practice Questions

Exactly **40** scenario-based practice questions.

### Basic — 1–10

1. A PySpark function reads a file, transforms it, and writes output. What architectural change would make its business logic easier to unit test?
2. Why is a `DataFrame → DataFrame` transformation easier to test than a function that creates its own SparkSession?
3. What is the purpose of a session-scoped pytest Spark fixture?
4. Why are tiny test DataFrames preferable to production-sized datasets for unit tests?
5. Why should important test DataFrames often use explicit schemas?
6. A DataFrame equality test fails because rows appear in a different order. What should you investigate?
7. Why should a test suite use UTC by default for many timestamp tests?
8. Why should empty DataFrames be included in a transformation's test cases?
9. What is the difference between a unit test and an integration test for a Spark job?
10. Why is `collect()` sometimes acceptable in a tiny unit test but dangerous on large data?

### Moderate — 11–20

11. A transformation correctly handles normal rows but fails when a required column contains NULL. How would you redesign the tests?
12. A test passes locally but fails in CI because a timestamp changes date. What evidence would you inspect?
13. A schema-equality test fails after a refactor while row values appear unchanged. What could have changed?
14. A Python function used by a UDF has ten edge cases. Which cases would you test without Spark and which would you test inside Spark?
15. A SQL test returns the correct rows but intermittently fails because a temporary view contains unexpected data. How would you isolate it?
16. An integration test against local Parquet passes, but the MinIO version fails. What additional failure classes does the MinIO test expose?
17. A DataFrame equality test passes, but a Pandera validation fails. Explain why both tests can be correct.
18. A broadcast join plan regression fails after a Spark upgrade. What should you investigate before changing the test?
19. A test suite has 500 tiny unit tests and takes 20 minutes. What measurements would you collect before optimizing it?
20. Why can running four Spark test workers be slower than running one?

### Hard — 21–30

21. Design a test architecture for a job with five transformation stages, three file inputs, and one object-storage output.
22. A plan regression test compares an entire physical-plan string. Explain how you would make it more stable.
23. A correct query stops using predicate pushdown. What test could detect this without asserting the entire plan?
24. A session-scoped fixture creates test speed improvements but introduces flaky SQL-view tests. Explain the trade-off and fix.
25. A UDF's pure Python tests pass, but Spark-level tests fail only for NULL values. Design the investigation.
26. An integration test fails because MinIO is unavailable. How should the CI pipeline distinguish environment failure from transformation failure?
27. A property-based test generates a dataset where a business invariant fails. What should the developer do before weakening the property?
28. A Spark upgrade changes a broadcast join into a different join strategy. How would you decide whether this is a regression or an intentional optimizer change?
29. A test suite is fast locally but slow in CI. Design an evidence-driven investigation.
30. A team wants to enforce an expected broadcast join for a critical fact-dimension workload. What should the performance contract contain?

### Advanced — 31–40

31. Design a complete testing pyramid for a production PySpark platform containing dozens of jobs.
32. Refactor a monolithic PySpark job into testable transformations while preserving orchestration behavior. What boundaries would you introduce?
33. Design a plan-regression framework that survives Spark-version upgrades without becoming meaningless.
34. Design a MinIO integration-test strategy that prevents tests from interfering with each other.
35. Design a property-based testing strategy for a deduplication and normalization pipeline.
36. A production query remains correct but becomes 5× slower after a code change. Explain how unit, integration, and plan-regression tests could each contribute to detection.
37. Design a CI pipeline that gives developers fast feedback while still validating object storage and critical Spark execution behavior.
38. A Spark test suite contains flaky timestamp, ordering, and shared-view failures. Build a systematic determinism/isolation remediation plan.
39. Design a testing strategy for PySpark UDFs that minimizes expensive Spark-level execution while retaining integration confidence.
40. Define the minimum evidence required before declaring a PySpark testing architecture production-ready.

---

## 60. Interview Questions

Exactly **40** interview questions.

### Basic — 1–10

1. How do you structure PySpark code for testability?
2. What is a pure `DataFrame → DataFrame` transformation?
3. Why should SparkSession creation normally stay outside business logic?
4. What is a pytest fixture?
5. Why use a session-scoped Spark fixture?
6. Why use explicit schemas in Spark tests?
7. How do you compare DataFrames?
8. How do you compare schemas?
9. Why can row order make a DataFrame test flaky?
10. What is the difference between unit and integration testing?

### Moderate — 11–20

11. How would you test NULL behavior in PySpark?
12. How would you test an empty DataFrame?
13. How would you test duplicate business keys?
14. How would you test timezone-sensitive transformations?
15. How would you test an ANSI-mode error?
16. How would you test a Python UDF?
17. How would you test pandas UDF behavior?
18. How do you test Spark SQL?
19. How do you isolate temporary views in a shared SparkSession?
20. How do local-file integration tests complement unit tests?

### Hard — 21–30

21. How would you test a full Spark job against MinIO?
22. How would you validate a Spark output with Pandera?
23. What is a plan regression test?
24. How would you test that a join remains a broadcast join?
25. How would you detect loss of predicate pushdown?
26. Why is comparing an entire physical plan string brittle?
27. How do you keep Spark tests fast?
28. When can parallel pytest processes make Spark tests slower?
29. What is Spark Connect and why might it be useful for testing?
30. What is property-based testing and how can it apply to DataFrame transformations?

### Advanced — 31–40

31. Design a production-grade PySpark test pyramid.
32. How would you refactor a monolithic Spark job into testable components?
33. How would you design plan tests that survive Spark upgrades?
34. How would you diagnose flaky Spark tests?
35. How would you test a transformation that has many possible input distributions?
36. How would you balance unit-test speed against integration confidence?
37. How would you protect a critical broadcast-join performance contract without over-constraining Catalyst?
38. How would you design PySpark testing in CI/CD?
39. What evidence would convince you that a Spark test suite is maintainable?
40. How would you distinguish correctness testing from performance testing?

---

## 61. Architecture Scenarios

### Scenario 1 — Logic Inside `main()`

**Context:** every job has SparkSession, I/O, transformations, and writes inside `main()`.

**Problem:** unit tests require external systems.

**Constraints:** production behavior must not change.

**Design options:**

- extract pure transformations,
- inject SparkSession,
- isolate I/O.

**Trade-off:** refactoring cost.

**Validation:** transformation tests run without external I/O.

---

### Scenario 2 — 30-Minute Suite

**Context:** developers stop running tests.

**Evidence:** many Spark startups and integration tests.

**Options:**

- session fixture,
- smaller data,
- test pyramid,
- controlled parallelism.

**Validation:** measure suite runtime before and after.

---

### Scenario 3 — New SparkSession Per Test

**Problem:** startup overhead.

**Decision criteria:**

- fixture scope,
- state isolation,
- cleanup.

**Validation:** compare suite runtime and flakiness.

---

### Scenario 4 — Row-Order Failure

**Context:** aggregation result is logically unordered.

**Problem:** list comparison fails.

**Decision:** order-insensitive DataFrame assertion.

**Validation:** explicitly sort only when order is contractual.

---

### Scenario 5 — Plan Regression After Upgrade

**Context:** Spark version changed.

**Problem:** full plan string changed.

**Investigation:**

- compare meaningful operator behavior,
- compare workload,
- inspect configuration,
- verify Spark version.

**Decision:** update the test only if the contract itself changed.

---

### Scenario 6 — Flaky MinIO Test

**Context:** object-store integration intermittently fails.

**Investigation:**

- readiness,
- object naming,
- credentials,
- cleanup,
- environment.

**Design:** isolated prefixes and deterministic setup.

---

### Scenario 7 — Broadcast Disappears

**Context:** critical query slows.

**Investigation:**

- plan,
- dimension size,
- statistics,
- thresholds,
- AQE,
- Spark version.

**Decision:** protect only the real business/performance contract.

---

### Scenario 8 — Unexpected Data Distribution

**Context:** examples pass but production data causes skew.

**Design:**

- property-based tests,
- cardinality tests,
- targeted skew cases,
- integration/performance validation.

---

### Scenario 9 — Only End-to-End Tests

**Problem:** slow feedback and poor failure localization.

**Design:** extract unit-testable transformations and retain selected E2E coverage.

---

### Scenario 10 — Introducing Property-Based Testing

**Context:** normalization function has many input combinations.

**Design:**

- define invariants,
- generate small valid inputs,
- preserve reproducibility,
- shrink failures,
- keep Spark execution bounded.

---

## 62. Common Misconceptions

1. Every PySpark test should execute the whole job.
2. A new SparkSession per test is always better isolation.
3. More test data automatically means better tests.
4. `collect()` is always bad.
5. `collect()` is always safe in tests.
6. DataFrame equality always requires row order.
7. Schema equality is unnecessary if values look correct.
8. NULL behaves like an ordinary value.
9. Empty DataFrames do not need tests.
10. Duplicate data does not need tests.
11. If output is correct, the execution plan never matters.
12. Plan tests should compare the entire physical plan.
13. Broadcast joins should always be forced.
14. Integration tests replace unit tests.
15. Unit tests replace integration tests.
16. Passing tests prove a pipeline is fast.
17. One SparkSession eliminates all isolation problems.
18. Parallel test execution is always faster.
19. Spark Connect automatically makes tests faster.
20. Property-based tests replace example-based tests.
21. MinIO behaves identically to a local filesystem.
22. Pandera and DataFrame equality test the same contract.
23. A passing test guarantees production correctness.
24. Spark-version upgrades cannot affect tests.
25. Timezone does not matter in data tests.
26. High code coverage means high test quality.
27. Exact error strings are always the best assertions.
28. Every transformation detail should be encoded in a plan regression test.

### Corrections

The correct principle is:

```text
Test behavior
+
test contracts
+
test critical performance assumptions
+
keep tests small and deterministic
```

---

## 63. Production Test Strategy Checklist

### Code Design

- [ ] Transformations separated from I/O.
- [ ] Pure DataFrame functions where practical.
- [ ] Thin entry points.
- [ ] Dependencies injected where useful.

### Unit Tests

- [ ] Tiny deterministic datasets.
- [ ] Explicit schemas.
- [ ] NULL cases.
- [ ] Empty cases.
- [ ] Duplicate cases.
- [ ] Boundary cases.
- [ ] Numerical tolerance.

### Integration

- [ ] Local-file tests.
- [ ] MinIO tests where required.
- [ ] Output validation.
- [ ] Cleanup.

### Performance

- [ ] Critical plan regression tests.
- [ ] Broadcast contracts where justified.
- [ ] Pushdown contracts where justified.
- [ ] No brittle full-plan comparisons.

### Test Performance

- [ ] Session-scoped Spark fixture.
- [ ] Small shuffle partitions.
- [ ] Spark UI disabled where appropriate.
- [ ] UTC timezone.
- [ ] Parallelism used carefully.
- [ ] Expensive integration tests separated.

### CI/CD

- [ ] Fast tests on pull requests.
- [ ] Integration tests appropriately scheduled.
- [ ] Reproducible environment.
- [ ] Spark version controlled.
- [ ] Useful diagnostics.

---

## 64. Learning Checkpoints

### Checkpoint 1 — Testable Architecture

You can:

- separate I/O from transformations,
- write DataFrame → DataFrame functions,
- explain thin entry points.

### Checkpoint 2 — Unit Testing

You can:

- build a Spark fixture,
- create explicit-schema DataFrames,
- compare DataFrames,
- compare schemas.

### Checkpoint 3 — Edge Cases

You can test:

- NULLs,
- empty input,
- duplicates,
- timezones,
- ANSI failures.

### Checkpoint 4 — Advanced Testing

You can:

- test UDFs,
- test SQL,
- build integration tests,
- validate outputs with data-quality tools.

### Checkpoint 5 — Performance Testing

You can:

- write plan regression tests,
- protect important broadcast behavior,
- protect pushdown,
- avoid brittle plan assertions.

### Checkpoint 6 — Production Architecture

You can:

- design a fast test suite,
- use CI/CD appropriately,
- apply property-based testing,
- explain unit vs integration vs plan regression.

---

## 65. Final Assessment

### Part A — Code Design

Take a poorly structured PySpark job containing:

- SparkSession creation,
- file reads,
- transformations,
- output writes.

Refactor it into:

- thin entry point,
- pure transformations,
- explicit dependencies.

### Part B — Unit Testing

Write tests for:

- normal input,
- NULL,
- empty input,
- duplicates,
- timezone boundary,
- invalid input.

### Part C — Integration

Write:

- local-file integration test,
- MinIO integration test,
- output validation.

### Part D — Plan Regression

Protect:

- broadcast join contract,
- predicate pushdown contract.

Do not compare entire plan strings.

### Part E — Property-Based Testing

Define at least three valid properties, for example:

- filter does not increase row count,
- deduplication is idempotent,
- normalization is idempotent.

### Part F — CI Strategy

Design:

```text
Pull Request
    ↓
Unit Tests
    ↓
Plan Tests
    ↓
Integration Tests
    ↓
Production Validation
```

### Passing standard

You should be able to explain:

> what is being tested, why it is tested at that layer, what failure it protects against, how to debug a failure, and how to keep the test fast and deterministic.

---

## 66. Glossary

**Unit test** — A focused test of a small unit of behavior, such as a DataFrame transformation.

**Integration test** — A test that exercises multiple real components together.

**Plan regression test** — A test that protects an important execution-plan characteristic.

**Property-based testing** — Testing invariants across many generated inputs rather than only fixed examples.

**pytest** — Python testing framework used to discover and execute tests.

**Fixture** — Reusable test setup supplied to test functions.

**Session-scoped fixture** — Fixture created once for a pytest session and reused by applicable tests.

**SparkSession** — Main entry point for DataFrame and Spark SQL operations.

**DataFrame** — Distributed structured dataset with named columns and schema.

**Schema** — Column names, data types, and structural metadata describing a DataFrame.

**Explicit schema** — A schema supplied directly rather than inferred.

**DataFrame equality** — Comparison of DataFrame contents and structural properties using Spark testing utilities.

**Schema equality** — Comparison of DataFrame schemas.

**NULL** — SQL missing/unknown value with special semantics.

**Empty DataFrame** — DataFrame containing zero rows, potentially with a valid schema.

**Duplicate** — Repeated record or repeated business key according to a defined contract.

**Timezone** — Temporal interpretation context for timestamps.

**ANSI mode** — Spark SQL behavior intended to provide stricter SQL semantics for certain invalid operations.

**UDF** — User-defined function executed as part of Spark computation.

**pandas UDF** — Python UDF mechanism using vectorized/batched data interchange and pandas-oriented processing.

**Temporary view** — Session-scoped SQL view over a DataFrame.

**MinIO** — S3-compatible object-storage system often used for local development/integration testing.

**Pandera** — Data validation framework that can express schema and data-quality expectations for supported data structures/environments.

**Broadcast join** — Join strategy where a suitably small relation is distributed to executors to reduce shuffle of the larger side.

**Predicate pushdown** — Applying filters as close to the data source as possible.

**Partition pruning** — Avoiding unnecessary source partitions based on partition predicates.

**Plan regression** — An undesirable change in execution strategy despite preserved logical correctness.

**Performance contract** — A deliberately selected execution behavior that the system expects to preserve.

**Determinism** — Producing stable results from the same controlled inputs and environment.

**Test isolation** — Ensuring tests do not depend on mutable state created by other tests.

**CI/CD** — Automated software integration, testing, validation, and delivery workflows.

**Spark Connect** — Client/server interface for interacting with Spark remotely.

**Pure transformation** — A transformation designed around explicit inputs and outputs without hidden external side effects.

**Thin entry point** — Small orchestration layer responsible for lifecycle, I/O, and composition rather than business logic.

---

## 67. Final Self-Review

Before considering Topic 16 complete:

- [ ] Testable DataFrame → DataFrame functions understood.
- [ ] Thin entry points understood.
- [ ] I/O/session separation understood.
- [ ] pytest fundamentals understood.
- [ ] Session-scoped Spark fixture understood.
- [ ] Local SparkSession understood.
- [ ] Small shuffle partitions understood.
- [ ] Spark UI disabled for tests understood.
- [ ] UTC timezone understood.
- [ ] Explicit schemas understood.
- [ ] `assertDataFrameEqual` understood.
- [ ] `assertSchemaEqual` understood.
- [ ] Order-insensitive comparison understood.
- [ ] Floating-point tolerance understood.
- [ ] NULL testing understood.
- [ ] Empty DataFrame testing understood.
- [ ] Duplicate testing understood.
- [ ] Timezone boundary testing understood.
- [ ] ANSI-mode error testing understood.
- [ ] Python UDF testing understood.
- [ ] pandas UDF testing understood.
- [ ] Spark SQL testing understood.
- [ ] Temporary-view isolation understood.
- [ ] Integration testing understood.
- [ ] Local-file integration understood.
- [ ] MinIO integration understood.
- [ ] Output validation understood.
- [ ] Pandera/data-quality validation understood.
- [ ] Plan regression testing understood.
- [ ] Broadcast regression testing understood.
- [ ] Predicate-pushdown regression testing understood.
- [ ] Fast test-suite architecture understood.
- [ ] One session per test run understood.
- [ ] Parallel test processes understood.
- [ ] Spark Connect awareness understood.
- [ ] Property-based testing understood.
- [ ] Determinism understood.
- [ ] Test isolation understood.
- [ ] CI/CD strategy understood.
- [ ] Test debugging workflow understood.
- [ ] At least 15 hands-on labs completed.
- [ ] At least 15 debugging exercises completed.
- [ ] At least 8 architecture scenarios analyzed.
- [ ] Exactly 40 practice questions completed.
- [ ] Exactly 40 interview questions completed.
- [ ] At least 25 misconceptions corrected.
- [ ] Production test strategy checklist completed.
- [ ] Final assessment completed.
- [ ] No fabricated benchmark or test output treated as real.
- [ ] Spark-version-sensitive behavior verified against the installed version.

---

## 68. Final Takeaway

Production-grade PySpark testing is not simply:

```text
pytest + SparkSession
```

It is an architecture.

The target design is:

```text
                 PRODUCTION JOB
                       │
             ┌─────────┴─────────┐
             │                   │
        Thin Entry Point    Pure Transformations
             │                   │
        I/O / Spark         DataFrame → DataFrame
             │                   │
       Integration Tests       Unit Tests
             │                   │
             └─────────┬─────────┘
                       │
               Plan Regression
                       │
               Performance Contract
                       │
                    CI/CD
```

The strongest PySpark test suite is:

- fast,
- deterministic,
- isolated,
- explicit about schemas,
- rich in edge cases,
- selective about integration tests,
- selective about plan contracts,
- aware of Spark-version changes,
- capable of diagnosing failures,
- and aligned with production architecture.

The final engineering principle is:

> **Make the transformation easy to test, make the job thin, make the tests deterministic, and protect only the execution behavior that actually matters.**
