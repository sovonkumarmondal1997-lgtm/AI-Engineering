# Module 2.19 — Testing Data Pipelines
# Practice Questions

## Table of Contents

### Basic
1. Question 01 — Minimal fixture for deduplication
2. Question 02 — Parametrized edge-case catalogue
3. Question 03 — Strict DataFrame equality
4. Question 04 — Tolerance versus exact money
5. Question 05 — Real PostgreSQL Testcontainer
6. Question 06 — Hypothesis idempotency property
7. Question 07 — Deterministic synthetic orders
8. Question 08 — Schema snapshot regression
9. Question 09 — Tiny batch smoke test
10. Question 10 — Choose the correct testing level

### Moderate
11. Question 11 — Table-driven deduplication with ties
12. Question 12 — Order-insensitive DataFrame comparison
13. Question 13 — Null, NaN, and SQL NULL
14. Question 14 — Tolerance from published precision
15. Question 15 — PostgreSQL COPY and MERGE isolation
16. Question 16 — Kafka redelivery and idempotent sink
17. Question 17 — Hypothesis shuffle invariance
18. Question 18 — Relationally consistent synthetic data
19. Question 19 — Key-consistent sampling
20. Question 20 — Golden data plus metric regression

### Hard
21. Question 21 — Cross-engine canonical comparison
22. Question 22 — Diagnose duplicate join expansion
23. Question 23 — Session container with per-test isolation
24. Question 24 — Kafka rebalance after killed consumer
25. Question 25 — Shrink a Hypothesis failure into regression
26. Question 26 — Incremental equals full rebuild
27. Question 27 — Privacy-safe production-derived sample
28. Question 28 — Protobuf compatibility gate
29. Question 29 — Streaming smoke test without fixed sleep
30. Question 30 — CI architecture for the testing pyramid

### Advanced
31. Question 31 — Silent revenue regression across layers
32. Question 32 — Kafka contract to deployment canary
33. Question 33 — Stateful SCD2 property testing
34. Question 34 — Three-tier test-data architecture
35. Question 35 — Exact financial comparison across engines
36. Question 36 — Systematic flakiness elimination
37. Question 37 — Worker-crash recovery contract
38. Question 38 — Production-safe post-deployment canary
39. Question 39 — Complete Module 2.19 testing pyramid
40. Question 40 — Integrated capstone: silent revenue failure

## Practice Philosophy

These are application and reasoning problems rather than definition flashcards. Use the testing loop:

```text
Read → Name the bug/risk → Choose test level → Choose smallest useful input
→ Choose assertion → Implement → Inject bug → Confirm failure
→ Check speed/flakiness → Explain production trade-offs
```

The set deliberately spans fixture tests, DataFrame equality, real-service integration, property-based testing, test-data engineering, schema/contracts, and E2E smoke testing. The goal is to decide **what can go wrong, which level should catch it, what data is needed, how correctness is proven, and where the test belongs in CI/CD**.


## Coverage Matrix

| Question | Difficulty | Primary Topic | Main Skill |
|---|---|---|---|
| 01 | Basic | Topic 01 | A transformation keeps the latest version of  |
| 02 | Basic | Topic 01 | A name normalizer must handle whitespace, Uni |
| 03 | Basic | Topic 02 | A deterministic transformation must preserve  |
| 04 | Basic | Topic 02 | A scientific metric permits tiny floating-poi |
| 05 | Basic | Topic 03 | A mock database test passes but production fa |
| 06 | Basic | Topic 04 | A normalization function must satisfy normali |
| 07 | Basic | Topic 05 | Generate repeatable CI order data without cop |
| 08 | Basic | Topic 06 | A published field is removed and another chan |
| 09 | Basic | Topic 07 | Orders flow through ingestion → Bronze → Silv |
| 10 | Basic | Topics 01–07 | A deterministic tax transformation has a bug. |
| 11 | Moderate | Topic 01 | A deduplication rule must handle empty input, |
| 12 | Moderate | Topic 02 | A SQL result has no guaranteed row order, but |
| 13 | Moderate | Topic 02 | A PostgreSQL-to-pandas test fails because mis |
| 14 | Moderate | Topic 02 | A metric is published to three decimal places |
| 15 | Moderate | Topic 03 | A test bulk-loads with COPY and upserts with  |
| 16 | Moderate | Topic 03 | A consumer can fail before offset commit. Pro |
| 17 | Moderate | Topic 04 | An aggregation should not depend on input row |
| 18 | Moderate | Topic 05 | Generate customers, products, orders, and pay |
| 19 | Moderate | Topic 05 | A 1% production-derived sample must preserve  |
| 20 | Moderate | Topic 06 | A revenue model keeps its schema but changes  |
| 21 | Hard | Topics 01–02 | The same transformation runs in pandas, Polar |
| 22 | Hard | Topic 02 | A Gold output grows from 10,000 to 12,500 row |
| 23 | Hard | Topic 03 | Starting a PostgreSQL container per test is t |
| 24 | Hard | Topic 03 | A consumer crashes during processing. Prove t |
| 25 | Hard | Topic 04 | Hypothesis finds a complex failing input. Exp |
| 26 | Hard | Topic 04 | Sequential incremental processing must equal  |
| 27 | Hard | Topic 05 | Realistic non-production data is needed but s |
| 28 | Hard | Topic 06 | A producer removes a field and reuses its fie |
| 29 | Hard | Topic 07 | A Kafka-to-lakehouse smoke test sleeps 30 sec |
| 30 | Hard | Topics 03/06/07 | A serial CI pipeline takes 25 minutes because |
| 31 | Advanced | Topics 01/02/06/07 | A deployment changes revenue by 8% while sche |
| 32 | Advanced | Topics 03/06/07 | A producer adds an event field while several  |
| 33 | Advanced | Topics 03/04 | An SCD2 table must never overlap intervals an |
| 34 | Advanced | Topics 05/01/07 | A team runs five million rows for every test. |
| 35 | Advanced | Topics 01/02 | Revenue runs in pandas for tests and Spark in |
| 36 | Advanced | Topics 03/04/05/07 | An E2E suite fails 1 in 20 CI runs with missi |
| 37 | Advanced | Topics 03/04/07 | A streaming worker may crash during processin |
| 38 | Advanced | Topics 06/07 | A production deployment must be validated wit |
| 39 | Advanced | Topics 01–07 | Design testing for PostgreSQL CDC → Kafka → o |
| 40 | Advanced | Topics 01–07 | An e-commerce platform has REST, PostgreSQL CDC, Kafka, object storage, Spark, dbt, Airflow, and CI/CD. A deployment caused silent revenue inflation |

# Part I — Basic

## Question 01 — Minimal fixture for deduplication

**Difficulty:** Basic

**Primary Topic:** Topic 01

**Concepts Tested:**
- fixtures\n-  transformations\n-  edge cases\n-  builders

### Problem

A transformation keeps the latest version of each order. Build the smallest pandas fixture with one duplicate key and assert that the newest row survives.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use two versions of one order with different timestamps and compare the exact expected one-row DataFrame.

**How to Solve It**

Fixture → transformation → exact equality. Keep the test focused on one rule.

### Code

```python
actual = deduplicate(input_df)
assert_frame_equal(actual, expected_df)
```

### Why This Solution Works

Use two versions of one order with different timestamps and compare the exact expected one-row DataFrame. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches wrong sort direction, wrong duplicate selection, and accidental dependence on input order.

### Production Lesson

Small fixtures make failures obvious and fast.

---

## Question 02 — Parametrized edge-case catalogue

**Difficulty:** Basic

**Primary Topic:** Topic 01 + Topic 02

**Concepts Tested:**
- fixtures\n-  transformations\n-  edge cases\n-  builders

### Problem

A name normalizer must handle whitespace, Unicode, null, and empty input. Design a parametrized pytest table.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use parameterized input/output pairs and assert each behavior.

**How to Solve It**

Build a table of cases, include explicit null/Unicode cases, then assert the expected result.

### Code

```python
@pytest.mark.parametrize("raw,expected",[("  José ","José"),(None,None)])
def test_normalize(raw, expected):
    assert normalize_name(raw) == expected
```

### Why This Solution Works

Use parameterized input/output pairs and assert each behavior. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches null corruption, Unicode defects, and missing boundary behavior.

### Production Lesson

Table-driven tests turn an edge-case catalogue into executable documentation.

---

## Question 03 — Strict DataFrame equality

**Difficulty:** Basic

**Primary Topic:** Topic 02

**Concepts Tested:**
- DataFrame equality\n-  tolerances\n-  diffs

### Problem

A deterministic transformation must preserve values, dtypes, column order, and row order. Choose the comparison.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use pandas.testing.assert_frame_equal with strict settings.

**How to Solve It**

Identify contractual dimensions and compare the complete normalized output.

### Code

```python
assert_frame_equal(actual, expected, check_dtype=True, check_exact=True)
```

### Why This Solution Works

Use pandas.testing.assert_frame_equal with strict settings. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches structural and value regressions that row-count checks miss.

### Production Lesson

Relax equality only when the contract says a dimension is irrelevant.

---

## Question 04 — Tolerance versus exact money

**Difficulty:** Basic

**Primary Topic:** Topic 02 + Topic 05

**Concepts Tested:**
- DataFrame equality\n-  tolerances\n-  diffs

### Problem

A scientific metric permits tiny floating-point noise but revenue must be exact to the cent. Choose assertions.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use allclose/approx for the scientific value and integer cents or Decimal for money.

**How to Solve It**

Separate fields by semantic type, define justified tolerance, and test a one-cent failure.

### Code

```python
np.testing.assert_allclose(actual_metric, expected_metric, rtol=1e-6, atol=1e-9)
assert actual_revenue_cents == expected_revenue_cents
```

### Why This Solution Works

Use allclose/approx for the scientific value and integer cents or Decimal for money. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches both numerical representation noise and financial rounding defects without conflating them.

### Production Lesson

Tolerance is a domain contract, not a way to make failures disappear.

---

## Question 05 — Real PostgreSQL Testcontainer

**Difficulty:** Basic

**Primary Topic:** Topic 03 + Topic 07

**Concepts Tested:**
- Testcontainers\n-  real services\n-  isolation

### Problem

A mock database test passes but production fails on a PostgreSQL constraint. What should the integration test do?

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use a disposable real PostgreSQL container, readiness check, real schema, operation, and state assertion.

**How to Solve It**

Classify as integration; start container; wait for readiness; migrate; execute; assert.

### Code

```python
with PostgresContainer("postgres:16") as postgres:
    run_pipeline(postgres.get_connection_url())
    assert query_count() == 1
```

### Why This Solution Works

Use a disposable real PostgreSQL container, readiness check, real schema, operation, and state assertion. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches database-specific constraints and SQL behavior that mocks cannot reproduce.

### Production Lesson

Use real disposable services when their semantics are part of the contract.

---

## Question 06 — Hypothesis idempotency property

**Difficulty:** Basic

**Primary Topic:** Topic 04 + Topic 01

**Concepts Tested:**
- Hypothesis\n-  properties\n-  shrinking

### Problem

A normalization function must satisfy normalize(normalize(x)) == normalize(x). Write the property strategy.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use @given with a text strategy and compare one versus two applications.

**How to Solve It**

Generate input, apply once and twice, compare, and let shrinking minimize failures.

### Code

```python
@given(st.text())
def test_idempotent(value):
    assert normalize(normalize(value)) == normalize(value)
```

### Why This Solution Works

Use @given with a text strategy and compare one versus two applications. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches unusual Unicode/whitespace cases missed by examples.

### Production Lesson

Properties should express stable invariants rather than random examples.

---

## Question 07 — Deterministic synthetic orders

**Difficulty:** Basic

**Primary Topic:** Topic 05 + Topic 01

**Concepts Tested:**
- synthetic data\n-  sampling\n-  masking

### Problem

Generate repeatable CI order data without copying production.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use NumPy default_rng with a fixed seed and explicit generation metadata.

**How to Solve It**

Seed a local generator, create IDs and amounts, and verify repeated generation is identical.

### Code

```python
rng = np.random.default_rng(42)
amounts = rng.uniform(10, 500, size=1000)
```

### Why This Solution Works

Use NumPy default_rng with a fixed seed and explicit generation metadata. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches nondeterministic fixture behavior and makes CI failures reproducible.

### Production Lesson

Version generator logic, seed, schema, and purpose.

---

## Question 08 — Schema snapshot regression

**Difficulty:** Basic

**Primary Topic:** Topic 06 + Topic 02

**Concepts Tested:**
- schema regression\n-  contracts\n-  golden data

### Problem

A published field is removed and another changes from integer to string. Design the regression test.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Diff the current schema against an approved snapshot and fail CI on incompatible changes.

**How to Solve It**

Compare names, types, and nullability; classify breaking changes; block promotion.

### Code

```python
assert schema_diff(actual_schema, expected_schema).is_compatible
```

### Why This Solution Works

Diff the current schema against an approved snapshot and fail CI on incompatible changes. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches producer changes that can break downstream consumers before runtime.

### Production Lesson

Schema correctness is necessary but does not prove semantic correctness.

---

## Question 09 — Tiny batch smoke test

**Difficulty:** Basic

**Primary Topic:** Topic 07 + Topic 05

**Concepts Tested:**
- E2E smoke\n-  polling\n-  CI/CD

### Problem

Orders flow through ingestion → Bronze → Silver → Gold. Design a minimal smoke test.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use tiny deterministic input and assert completion, output existence, row count, and one invariant.

**How to Solve It**

Load data, run the complete path, assert Gold exists/nonempty and keys are unique.

### Code

```python
run_pipeline(run_id="smoke-001")
assert output_exists("smoke-001")
assert row_count("smoke-001") > 0
```

### Why This Solution Works

Use tiny deterministic input and assert completion, output existence, row count, and one invariant. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches broken wiring, wrong paths, and successful-but-empty outputs.

### Production Lesson

Smoke tests should be small enough for frequent execution.

---

## Question 10 — Choose the correct testing level

**Difficulty:** Basic

**Primary Topic:** Topics 01–07

**Concepts Tested:**
- testing pyramid\n-  cross-topic reasoning

### Problem

A deterministic tax transformation has a bug. Where should its primary test live?

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use a fixture-based unit/DataFrame test; add broader tests only for cross-component risks.

**How to Solve It**

Choose the narrowest reliable layer, then justify any integration/regression/E2E coverage.

### Code

```python
assert_frame_equal(actual, expected)
```

### Why This Solution Works

Use a fixture-based unit/DataFrame test; add broader tests only for cross-component risks. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches the defect cheaply and keeps E2E focused on system risks.

### Production Lesson

Test at the lowest level that can reliably catch the risk.

---

# Part II — Moderate

## Question 11 — Table-driven deduplication with ties

**Difficulty:** Moderate

**Primary Topic:** Topic 01 + Topic 02

**Concepts Tested:**
- fixtures\n-  transformations\n-  edge cases\n-  builders

### Problem

A deduplication rule must handle empty input, one row, duplicates, equal timestamps, and multiple keys.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use a reusable builder plus parametrized cases and an explicit tie-break rule.

**How to Solve It**

Define the tie rule, build fixtures, parameterize cases, and compare expected outputs.

### Code

```python
@pytest.mark.parametrize("rows", cases)
def test_dedup(rows):
    assert deduplicate(make_df(rows)) is not None
```

### Why This Solution Works

Use a reusable builder plus parametrized cases and an explicit tie-break rule. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches unstable tie handling, empty-input bugs, and duplicate-selection defects.

### Production Lesson

Fixture builders reduce setup duplication without hiding behavior.

---

## Question 12 — Order-insensitive DataFrame comparison

**Difficulty:** Moderate

**Primary Topic:** Topic 02

**Concepts Tested:**
- DataFrame equality\n-  tolerances\n-  diffs

### Problem

A SQL result has no guaranteed row order, but all values and schema must match.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Sort both frames by stable business keys, reset irrelevant index, then assert strict equality.

**How to Solve It**

Normalize only row ordering; keep values, schema, and dtypes strict.

### Code

```python
assert_frame_equal(canonical(actual), canonical(expected), check_dtype=True)
```

### Why This Solution Works

Sort both frames by stable business keys, reset irrelevant index, then assert strict equality. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches structural changes while ignoring an explicitly irrelevant ordering difference.

### Production Lesson

Relax exactly the dimension the contract permits.

---

## Question 13 — Null, NaN, and SQL NULL

**Difficulty:** Moderate

**Primary Topic:** Topic 02 + Topic 03

**Concepts Tested:**
- DataFrame equality\n-  tolerances\n-  diffs

### Problem

A PostgreSQL-to-pandas test fails because missing values have different representations.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Normalize only semantically equivalent missing values and preserve meaningful NaN semantics.

**How to Solve It**

Inspect source types, choose nullable dtypes, normalize deliberately, then compare.

### Code

```python
actual = actual.astype({"id":"Int64","name":"string"})
assert_frame_equal(actual, expected)
```

### Why This Solution Works

Normalize only semantically equivalent missing values and preserve meaningful NaN semantics. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches accidental conversion of missing values into real business values.

### Production Lesson

Cross-engine comparison needs an explicit missing-value contract.

---

## Question 14 — Tolerance from published precision

**Difficulty:** Moderate

**Primary Topic:** Topic 02

**Concepts Tested:**
- DataFrame equality\n-  tolerances\n-  diffs

### Problem

A metric is published to three decimal places. Define a defensible tolerance.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Derive the tolerance from the actual precision; do not choose a large arbitrary value.

**How to Solve It**

Determine precision, set bounded atol/rtol, and test just-inside and just-outside boundaries.

### Code

```python
assert actual == pytest.approx(expected, abs=1e-6)
```

### Why This Solution Works

Derive the tolerance from the actual precision; do not choose a large arbitrary value. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches meaningful drift while allowing representation noise.

### Production Lesson

Numerical tolerance should be justified by computation or domain precision.

---

## Question 15 — PostgreSQL COPY and MERGE isolation

**Difficulty:** Moderate

**Primary Topic:** Topic 03

**Concepts Tested:**
- Testcontainers\n-  real services\n-  isolation

### Problem

A test bulk-loads with COPY and upserts with MERGE. It must run in parallel safely.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use a real PostgreSQL container and unique schema per test/run.

**How to Solve It**

Start ready container, create namespace, migrate, COPY, MERGE, assert, clean up.

### Code

```python
schema = f"test_{run_id}"
copy_rows(schema, rows)
merge_rows(schema, updates)
assert query_count(schema) == expected_count
```

### Why This Solution Works

Use a real PostgreSQL container and unique schema per test/run. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches SQL/state behavior while preventing cross-test contamination.

### Production Lesson

Parallel integration reliability depends on resource isolation.

---

## Question 16 — Kafka redelivery and idempotent sink

**Difficulty:** Moderate

**Primary Topic:** Topic 03 + Topic 07

**Concepts Tested:**
- Testcontainers\n-  real services\n-  isolation

### Problem

A consumer can fail before offset commit. Prove a replay does not create a duplicate logical record.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Publish a deterministic event, force consumer restart, allow redelivery, and assert one sink record.

**How to Solve It**

Exercise processing/commit boundary, restart, poll recovery, and assert by event/business key.

### Code

```python
produce("event-001")
restart_consumer()
wait_until(lambda: sink_count("event-001") >= 1)
assert sink_count("event-001") == 1
```

### Why This Solution Works

Publish a deterministic event, force consumer restart, allow redelivery, and assert one sink record. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches at-least-once duplicate effects.

### Production Lesson

Test delivery semantics together with sink correctness.

---

## Question 17 — Hypothesis shuffle invariance

**Difficulty:** Moderate

**Primary Topic:** Topic 04 + Topic 01

**Concepts Tested:**
- Hypothesis\n-  properties\n-  shrinking

### Problem

An aggregation should not depend on input row order.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Generate rows, aggregate, shuffle, aggregate again, and compare normalized results.

**How to Solve It**

Generate, transform, shuffle, transform, normalize, assert equality.

### Code

```python
@given(st.lists(st.tuples(st.integers(1,10), st.integers(0,100)), min_size=1))
def test_shuffle_invariance(rows):
    assert normalize(aggregate(rows)) == normalize(aggregate(shuffle(rows)))
```

### Why This Solution Works

Generate rows, aggregate, shuffle, aggregate again, and compare normalized results. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches order-dependent implementations.

### Production Lesson

Properties are valuable when they describe invariants under valid transformations.

---

## Question 18 — Relationally consistent synthetic data

**Difficulty:** Moderate

**Primary Topic:** Topic 05 + Topic 01

**Concepts Tested:**
- synthetic data\n-  sampling\n-  masking

### Problem

Generate customers, products, orders, and payments, plus an intentional orphan case.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Generate parent keys first, reference valid keys, then deliberately inject one orphan.

**How to Solve It**

Build valid data, validate relationships, create negative fixture, assert the validator catches it.

### Code

```python
assert referential_integrity(customers, orders, payments)
assert not referential_integrity(customers, [orphan], payments)
```

### Why This Solution Works

Generate parent keys first, reference valid keys, then deliberately inject one orphan. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches referential-integrity defects without producing meaningless random failures.

### Production Lesson

Good synthetic data encodes relationships and failure modes.

---

## Question 19 — Key-consistent sampling

**Difficulty:** Moderate

**Primary Topic:** Topic 05

**Concepts Tested:**
- synthetic data\n-  sampling\n-  masking

### Problem

A 1% production-derived sample must preserve customer/order/payment relationships.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Select root keys deterministically by hash, then include related child rows.

**How to Solve It**

Hash-select roots, filter children through keys, validate relationships, version the rule.

### Code

```python
selected = [k for k in customer_ids if hash_select(k)]
assert all(o.customer_id in selected for o in sampled_orders)
```

### Why This Solution Works

Select root keys deterministically by hash, then include related child rows. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches orphaned sample records and unstable samples.

### Production Lesson

Sample relational data around stable keys, not independently per table.

---

## Question 20 — Golden data plus metric regression

**Difficulty:** Moderate

**Primary Topic:** Topic 06 + Topic 07

**Concepts Tested:**
- schema regression\n-  contracts\n-  golden data

### Problem

A revenue model keeps its schema but changes total revenue unexpectedly.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Compare versioned golden output and/or approved business metrics; require intentional baseline changes to be explicit.

**How to Solve It**

Compute output, compare key rows and revenue, classify expected changes, fail unexplained drift.

### Code

```python
assert actual_total_revenue == expected_total_revenue
```

### Why This Solution Works

Compare versioned golden output and/or approved business metrics; require intentional baseline changes to be explicit. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches semantic regressions invisible to schema tests.

### Production Lesson

Regression protection must detect unexpected change while permitting governed evolution.

---

# Part III — Hard

## Question 21 — Cross-engine canonical comparison

**Difficulty:** Hard

**Primary Topic:** Topic 01 + Topic 02

**Concepts Tested:**
- production testing\n-  debugging\n-  assertions

### Problem

The same transformation runs in pandas, Polars, DuckDB, and Spark with timestamp and ordering differences.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Normalize to a canonical representation, then compare strictly.

**How to Solve It**

Canonicalize schema, timestamps, missing values, and stable order; use exact comparison afterward.

### Code

```python
assert_frame_equal(canonical(pandas_out), canonical(spark_out))
```

### Why This Solution Works

Normalize to a canonical representation, then compare strictly. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches semantic cross-engine divergence without hiding it behind loose comparison.

### Production Lesson

Cross-engine testing needs an explicit canonicalization contract.

---

## Question 22 — Diagnose duplicate join expansion

**Difficulty:** Hard

**Primary Topic:** Topic 02 + Topic 06

**Concepts Tested:**
- DataFrame equality\n-  tolerances\n-  diffs

### Problem

A Gold output grows from 10,000 to 12,500 rows after a join. Diagnose the likely cause.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Compare counts, inspect join-key multiplicity, use anti-joins, and create compact mismatch summaries.

**How to Solve It**

Find first count divergence, group by join key, inspect duplicates, compare unexpected keys, sample evidence.

### Code

```python
duplicates = joined.groupby("order_id").size().query("size > 1")
assert duplicates.empty
```

### Why This Solution Works

Compare counts, inspect join-key multiplicity, use anti-joins, and create compact mismatch summaries. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches duplicate join expansion and makes large-output failures diagnosable.

### Production Lesson

Comparison tooling should help locate the cause, not dump millions of rows.

---

## Question 23 — Session container with per-test isolation

**Difficulty:** Hard

**Primary Topic:** Topic 03

**Concepts Tested:**
- Testcontainers\n-  real services\n-  isolation

### Problem

Starting a PostgreSQL container per test is too slow, but shared state contaminates tests.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use a session-scoped container with unique schemas/state per test or worker.

**How to Solve It**

Start once, wait once, namespace mutable state, migrate as needed, clean up.

### Code

```python
@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16") as c:
        yield c
```

### Why This Solution Works

Use a session-scoped container with unique schemas/state per test or worker. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches both lifecycle inefficiency and cross-test contamination.

### Production Lesson

Fixture scope should optimize lifecycle without sacrificing isolation.

---

## Question 24 — Kafka rebalance after killed consumer

**Difficulty:** Hard

**Primary Topic:** Topic 03

**Concepts Tested:**
- Testcontainers\n-  real services\n-  isolation

### Problem

A consumer crashes during processing. Prove the group recovers and final data is correct.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use real Kafka, deterministic events, injected consumer failure, rebalance, polling, and final data assertions.

**How to Solve It**

Publish, start group, kill consumer, observe rebalance, wait, assert completeness and duplicate invariants.

### Code

```python
kill_consumer("consumer-1")
wait_until(lambda: sink_has_all(expected_ids), timeout=60)
assert no_duplicate_business_keys()
```

### Why This Solution Works

Use real Kafka, deterministic events, injected consumer failure, rebalance, polling, and final data assertions. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches recovery defects that unit tests cannot reproduce.

### Production Lesson

Distributed recovery tests must end in data-level correctness.

---

## Question 25 — Shrink a Hypothesis failure into regression

**Difficulty:** Hard

**Primary Topic:** Topic 04

**Concepts Tested:**
- Hypothesis\n-  properties\n-  shrinking

### Problem

Hypothesis finds a complex failing input. Explain how shrinking should become durable test coverage.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Preserve the minimal counterexample as a focused regression while retaining the property test.

**How to Solve It**

Inspect shrunk case, understand invariant, add named regression, keep property, verify buggy version fails.

### Code

```python
def test_discovered_counterexample():
    assert validate(minimal_failing_case) is True
```

### Why This Solution Works

Preserve the minimal counterexample as a focused regression while retaining the property test. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches the known incident quickly and retains broad generated coverage.

### Production Lesson

Property discovery and regression documentation reinforce each other.

---

## Question 26 — Incremental equals full rebuild

**Difficulty:** Hard

**Primary Topic:** Topic 04

**Concepts Tested:**
- Hypothesis\n-  properties\n-  shrinking

### Problem

Sequential incremental processing must equal a full rebuild over the same logical data.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use a metamorphic property comparing incremental and rebuild paths after normalization.

**How to Solve It**

Generate data, chunk it, apply incremental updates, rebuild all, normalize, compare.

### Code

```python
incremental = apply_chunks(chunks)
full = full_rebuild(concat(chunks))
assert normalize(incremental) == normalize(full)
```

### Why This Solution Works

Use a metamorphic property comparing incremental and rebuild paths after normalization. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches state, boundary, late-data, and deduplication defects.

### Production Lesson

Incremental correctness is stronger when compared with an authoritative rebuild.

---

## Question 27 — Privacy-safe production-derived sample

**Difficulty:** Hard

**Primary Topic:** Topic 05

**Concepts Tested:**
- synthetic data\n-  sampling\n-  masking

### Problem

Realistic non-production data is needed but source data contains PII.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use key-consistent sampling, masking/removal, keyed hashing where joinability is required, and versioned rules.

**How to Solve It**

Select deterministic roots, include related rows, remove unnecessary PII, mask identifiers, validate relationships, version dataset.

### Code

```python
masked_id = hmac_hash(customer_id, secret)
assert referential_integrity(masked_customers, masked_orders)
```

### Why This Solution Works

Use key-consistent sampling, masking/removal, keyed hashing where joinability is required, and versioned rules. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches privacy leakage and broken relational structure in derived test data.

### Production Lesson

Synthetic data is preferred; derived data must be minimized, masked, isolated, and documented.

---

## Question 28 — Protobuf compatibility gate

**Difficulty:** Hard

**Primary Topic:** Topic 06

**Concepts Tested:**
- schema regression\n-  contracts\n-  golden data

### Problem

A producer removes a field and reuses its field number for another type.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Run schema compatibility and consumer contract checks and block incompatible changes.

**How to Solve It**

Diff schemas, classify compatibility, check reserved/reused fields, run consumer tests, fail CI if incompatible.

### Code

```python
assert schema_compatible(old_schema, new_schema)
```

### Why This Solution Works

Run schema compatibility and consumer contract checks and block incompatible changes. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches producer changes that can break older consumers.

### Production Lesson

Schema evolution is a producer/consumer contract, not merely serialization.

---

## Question 29 — Streaming smoke test without fixed sleep

**Difficulty:** Hard

**Primary Topic:** Topic 07

**Concepts Tested:**
- E2E smoke\n-  polling\n-  CI/CD

### Problem

A Kafka-to-lakehouse smoke test sleeps 30 seconds and is flaky.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Publish deterministic events and poll the sink until expected IDs appear or a deadline expires.

**How to Solve It**

Create run/event IDs, verify readiness, publish, poll, fail with context, clean up.

### Code

```python
wait_until(lambda: sink_contains(expected_ids), timeout=60)
```

### Why This Solution Works

Publish deterministic events and poll the sink until expected IDs appear or a deadline expires. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches asynchronous processing failures without timing-based flakiness.

### Production Lesson

Use observable conditions and bounded timeouts, never guessed sleeps.

---

## Question 30 — CI architecture for the testing pyramid

**Difficulty:** Hard

**Primary Topic:** Topics 03/06/07

**Concepts Tested:**
- CI architecture\n-  integration\n-  regression

### Problem

A serial CI pipeline takes 25 minutes because every test blocks every other test.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Parallelize independent fast layers, build once, run a small E2E promotion gate, and schedule broader E2E.

**How to Solve It**

Classify by scope/cost, parallelize independent jobs, deploy artifact, smoke-gate promotion, retain artifacts, schedule broad suites.

### Code

```python
jobs = [unit, integration, regression]
e2e = promotion_gate(needs=jobs)
```

### Why This Solution Works

Parallelize independent fast layers, build once, run a small E2E promotion gate, and schedule broader E2E. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches deployment-critical failures without making every scenario a PR blocker.

### Production Lesson

CI should mirror the testing pyramid and business criticality.

---

# Part IV — Advanced

## Question 31 — Silent revenue regression across layers

**Difficulty:** Advanced

**Primary Topic:** Topics 01/02/06/07

**Concepts Tested:**
- incident regression\n-  metric regression\n-  E2E

### Problem

A deployment changes revenue by 8% while schema tests pass. Design the layered regression strategy.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Reduce to minimal fixture, add exact transformation regression, golden/metric protection, and E2E business assertion.

**How to Solve It**

Find first divergent stage, minimize input, test transformation, protect golden/metric output, run batch smoke, inject bug.

### Code

```python
assert_frame_equal(transform(minimal_fixture), expected)
assert run_smoke().revenue == expected_revenue
```

### Why This Solution Works

Reduce to minimal fixture, add exact transformation regression, golden/metric protection, and E2E business assertion. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches semantic revenue errors at the mechanism, output, and system levels.

### Production Lesson

A production incident should create the smallest durable regression plus broader protection where justified.

---

## Question 32 — Kafka contract to deployment canary

**Difficulty:** Advanced

**Primary Topic:** Topics 03/06/07

**Concepts Tested:**
- CI architecture\n-  integration\n-  regression

### Problem

A producer adds an event field while several consumers are independently owned.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Run schema compatibility, consumer contracts, real Kafka integration, staging canary, and post-deploy validation.

**How to Solve It**

Check compatibility, test consumers, exercise Kafka, deploy staging, publish canary, poll sink, gate promotion.

### Code

```python
assert schema_compatible(old, new)
publish_canary("e2e-canary-001")
wait_until(lambda: sink_contains("e2e-canary-001"))
```

### Why This Solution Works

Run schema compatibility, consumer contracts, real Kafka integration, staging canary, and post-deploy validation. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches both contract incompatibility and deployment wiring failures.

### Production Lesson

Contract correctness and system correctness require connected but distinct gates.

---

## Question 33 — Stateful SCD2 property testing

**Difficulty:** Advanced

**Primary Topic:** Topics 03/04

**Concepts Tested:**
- stateful testing\n-  SCD2

### Problem

An SCD2 table must never overlap intervals and replaying the same changes must not add history.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Generate sequences against a real/controlled state store and assert interval and replay invariants.

**How to Solve It**

Generate changes, apply, inspect history, assert no overlaps/current-row rule, replay, compare state.

### Code

```python
assert no_overlapping_intervals(history)
replay(changes)
assert normalize(read_history()) == before
```

### Why This Solution Works

Generate sequences against a real/controlled state store and assert interval and replay invariants. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches sequence-dependent defects that isolated examples miss.

### Production Lesson

Use stateful properties when correctness depends on operation history.

---

## Question 34 — Three-tier test-data architecture

**Difficulty:** Advanced

**Primary Topic:** Topics 05/01/07

**Concepts Tested:**
- test-data tiers\n-  fixtures\n-  E2E

### Problem

A team runs five million rows for every test. Design tiny, small, and large tiers.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use tiny deterministic data for PR/E2E smoke, small representative data for regression/integration, and large data for scheduled scale testing.

**How to Solve It**

Define tier purpose, version generators/manifests, validate privacy, measure runtime, and place each tier deliberately.

### Code

```python
tiers = {"tiny":"PR smoke","small":"regression","large":"nightly scale"}
```

### Why This Solution Works

Use tiny deterministic data for PR/E2E smoke, small representative data for regression/integration, and large data for scheduled scale testing. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches both CI cost problems and insufficient system coverage.

### Production Lesson

Test-data architecture is part of test architecture.

---

## Question 35 — Exact financial comparison across engines

**Difficulty:** Advanced

**Primary Topic:** Topics 01/02

**Concepts Tested:**
- cross-engine comparison\n-  financial precision

### Problem

Revenue runs in pandas for tests and Spark in production. Timestamp representation may differ, money may not.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Canonicalize timestamp instants/order but compare revenue exactly using cents or Decimal.

**How to Solve It**

Normalize time and order, represent money exactly, test a one-cent failure, compare.

### Code

```python
assert actual_revenue_cents == expected_revenue_cents
```

### Why This Solution Works

Canonicalize timestamp instants/order but compare revenue exactly using cents or Decimal. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches financial defects without false failures from timestamp representation.

### Production Lesson

Comparison strictness must follow business semantics.

---

## Question 36 — Systematic flakiness elimination

**Difficulty:** Advanced

**Primary Topic:** Topics 03/04/05/07

**Concepts Tested:**
- production testing\n-  debugging\n-  assertions

### Problem

An E2E suite fails 1 in 20 CI runs with missing Kafka events, timestamp drift, and duplicates.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Instrument runs, fix readiness, deterministic data/time, isolation, polling, and bounded infrastructure retries; verify 20 consecutive runs.

**How to Solve It**

Capture run/worker IDs, inspect readiness, seed data, control time, namespace resources, poll, retry only transient infrastructure, repeat 20 times.

### Code

```python
wait_until(kafka_ready, timeout=30)
wait_until(lambda: sink_has_run(run_id), timeout=60)
```

### Why This Solution Works

Instrument runs, fix readiness, deterministic data/time, isolation, polling, and bounded infrastructure retries; verify 20 consecutive runs. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches the actual sources of nondeterminism rather than masking them.

### Production Lesson

Flakiness is a reliability defect to measure and eliminate.

---

## Question 37 — Worker-crash recovery contract

**Difficulty:** Advanced

**Primary Topic:** Topics 03/04/07

**Concepts Tested:**
- recovery\n-  properties\n-  E2E

### Problem

A streaming worker may crash during processing. Prove recovery and final correctness.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Inject the crash, allow recovery, poll the sink, and assert complete logical output plus idempotency.

**How to Solve It**

Prepare isolated stream, produce events, kill worker, observe recovery, poll, assert counts/aggregates/duplicates, retain artifacts.

### Code

```python
kill_worker()
wait_until(lambda: sink_has_all(ids), timeout=120)
assert no_duplicate_business_keys()
```

### Why This Solution Works

Inject the crash, allow recovery, poll the sink, and assert complete logical output plus idempotency. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches recovery paths that restart successfully but corrupt data.

### Production Lesson

Chaos variants should validate a specific recovery contract.

---

## Question 38 — Production-safe post-deployment canary

**Difficulty:** Advanced

**Primary Topic:** Topics 06/07

**Concepts Tested:**
- contracts\n-  canaries

### Problem

A production deployment must be validated without PII or arbitrary business-table writes.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Use a safe synthetic canary path if deliberately supported, plus read-only availability/freshness checks.

**How to Solve It**

Define safe canary, validate contract, trace to Gold, poll, run read-only checks, gate deployment, retain evidence.

### Code

```python
publish_safe_canary("e2e-smoke-001")
wait_until(lambda: canary_visible("e2e-smoke-001"))
assert output_is_fresh()
```

### Why This Solution Works

Use a safe synthetic canary path if deliberately supported, plus read-only availability/freshness checks. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches deployment/routing/permission failures without unsafe production mutation.

### Production Lesson

Post-deployment validation is itself a production-safety mechanism.

---

## Question 39 — Complete Module 2.19 testing pyramid

**Difficulty:** Advanced

**Primary Topic:** Topics 01–07

**Concepts Tested:**
- testing pyramid\n-  cross-topic reasoning

### Problem

Design testing for PostgreSQL CDC → Kafka → object storage → Spark/dbt → Gold.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Map every risk to the narrowest useful test and add regression/E2E coverage for cross-component behavior.

**How to Solve It**

Define unit fixtures, equality policy, properties, real-service integration, test-data tiers, contracts/golden/metrics, E2E, canaries, and CI placement.

### Code

```python
strategy = {'unit':'transformations','property':'invariants','integration':'real services','regression':'contracts','e2e':'critical path'}
```

### Why This Solution Works

Map every risk to the narrowest useful test and add regression/E2E coverage for cross-component behavior. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches the widest set of failures with the best diagnostic cost.

### Production Lesson

Senior testing strategy is risk-to-test-level mapping.

---

## Question 40 — Integrated capstone: silent revenue failure

**Difficulty:** Advanced

**Primary Topic:** Topics 01–07

**Concepts Tested:**
- testing pyramid\n-  cross-topic reasoning

### Problem

An e-commerce platform has REST, PostgreSQL CDC, Kafka, object storage, Spark, dbt, Airflow, and CI/CD. A deployment caused silent revenue inflation; Kafka can redeliver and CI is flaky.

> **Try it yourself first.** Identify the bug, choose the appropriate test level, select the smallest useful input, and decide how you would prove the expected behavior before reading the solution.

### Solution

**Short Answer**

Design the complete production-grade testing strategy using every Module 2.19 layer.

**How to Solve It**

Start from the incident; minimize the reproducer; add unit/equality, integration, property, data, schema/contract, golden/metric, batch/streaming E2E, canary, flakiness, CI, artifacts, and recovery protection.

### Code

```python
run_unit_regression()
run_integration_tests()
run_property_suite()
run_contract_regression()
run_batch_smoke()
run_streaming_smoke()
run_post_deploy_canary()
```

### Why This Solution Works

Design the complete production-grade testing strategy using every Module 2.19 layer. The test is aligned to the failure risk instead of merely increasing test count.

### What Failure Does This Catch?

Catches semantic, delivery, contract, deployment, reliability, and recovery risks across the full testing pyramid.

### Production Lesson

The goal is a coherent testing system, not maximum test count.

---

# Module 2.19 Self-Assessment

```text
[ ] DataFrame transformations and minimal fixtures
[ ] Builders, parametrization, and edge cases
[ ] Exact/tolerant DataFrame comparisons
[ ] Exact financial comparison
[ ] PostgreSQL, Kafka, and object-storage integration
[ ] Testcontainers and state isolation
[ ] Hypothesis, shrinking, and invariants
[ ] Idempotency and incremental/full rebuild testing
[ ] Synthetic, sampled, and masked test data
[ ] Schema regression and data contracts
[ ] Golden-data and metric regression
[ ] Batch and streaming E2E smoke tests
[ ] Polling, timeouts, canaries, and flakiness control
[ ] CI/CD placement and promotion gates
[ ] Recovery/failure injection
[ ] Production-safe testing strategy
```

# Can I Move On?

### A — Revenue is wrong but the pipeline succeeds.
**Solution:** Start with the smallest transformation regression, then inspect golden-data/metric regression and E2E business assertions.

### B — Kafka occasionally loses or duplicates events.
**Solution:** Use real Kafka integration tests for commits/restarts, property/invariant tests for conservation/idempotency, and streaming E2E for the complete path.

### C — A producer changes `int` to `string`.
**Solution:** Treat it as a contract/schema-evolution change; run compatibility and consumer regression checks in CI.

### D — A streaming smoke test is flaky.
**Solution:** Replace fixed sleeps with readiness checks, deterministic IDs, bounded polling, and explicit timeouts.

### E — Someone proposes copying hundreds of GB of production data into CI.
**Solution:** Reject it as a default because of privacy, cost, runtime, and reproducibility. Prefer deterministic synthetic data and targeted masked samples.

### F — An E2E test takes an hour.
**Solution:** Shrink the smoke path, move broad scenarios to integration/regression/nightly suites, parallelize only after isolation, and define a time budget.
