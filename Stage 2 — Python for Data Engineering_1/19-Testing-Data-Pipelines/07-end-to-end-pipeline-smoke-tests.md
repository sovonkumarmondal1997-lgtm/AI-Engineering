# 07 — End-to-End Pipeline Smoke Tests

> **Module 2.19 — Testing Data Pipelines**
>
> Topic 07 is the final system-level protection layer: validate that the complete data pipeline works on small, deterministic data before and after deployment.

---

## 1. Learning Objectives

By the end of this module, you should be able to:

- Explain what an end-to-end (E2E) smoke test is and why it exists.
- Distinguish a smoke test from a full E2E test.
- Map a pipeline's critical path before writing a smoke test.
- Design the smallest dataset that exercises every critical stage.
- Build batch E2E smoke tests with `pytest`.
- Run orchestrated workflows from tests using Airflow, Dagster, or Prefect patterns.
- Build streaming smoke tests around known Kafka events.
- Use bounded polling and timeouts instead of fixed sleeps.
- Validate outputs, row counts, invariants, data-quality checks, and business assertions.
- Use Docker Compose, Testcontainers, and ephemeral/per-PR environments.
- Design post-deployment smoke tests for staging and production.
- Use safe synthetic canary records and read-only production checks.
- Place smoke tests correctly in CI/CD.
- Diagnose and eliminate E2E flakiness.
- Retry transient infrastructure failures without retrying incorrect assertions.
- Define realistic time budgets.
- Parallelize E2E tests safely.
- Test component failure and recovery.
- Produce actionable failure reports and CI artifacts.
- Understand where smoke testing ends and continuous production monitoring begins.

The central principle is:

> **Unit tests prove components behave correctly. E2E smoke tests prove the components work together as a system.**

---

## 2. Why End-to-End Smoke Tests Matter

A pipeline can have excellent component tests and still fail as a system.

For example:

```text
PostgreSQL integration test passes
Kafka integration test passes
Spark transformation test passes
dbt test passes
API contract test passes

                    BUT

Airflow points to the wrong table
        OR
Kafka topic name is wrong
        OR
IAM permission is missing
        OR
Bronze path changed
        OR
Gold reads yesterday's table
```

The system can fail because the **wiring** is wrong.

That is the gap E2E smoke tests fill.

### The critical distinction

A component test asks:

```text
Does this component work?
```

An E2E smoke test asks:

```text
Can the complete critical path work?
```

A successful pipeline run is not enough either.

The test should verify meaningful outcomes:

```text
Input
  ↓
Ingestion
  ↓
Bronze
  ↓
Silver
  ↓
Gold
  ↓
Output
  ↓
Data/business assertions
```

---

## 3. Testing Pyramid Position

Topic 07 comes last because it is the broadest and most environment-dependent layer.

```text
                    ▲
                    │ fewer, slower, broader
                    │
            07 E2E Smoke Tests
            06 Regression Tests
            03 Integration Tests
         01–02 Unit/DataFrame Tests
                    │
                    ▼ more, faster, narrower
```

E2E smoke tests are:

- broader;
- slower;
- more expensive;
- more environment-dependent;
- especially valuable for system wiring.

They should **not** replace lower-level tests.

A healthy strategy looks like:

```text
Unit tests
    ↓
Integration tests
    ↓
Property tests
    ↓
Test-data validation
    ↓
Regression tests
    ↓
E2E smoke tests
```

Each layer answers a different question.

---

## 4. Smoke Test vs Full E2E Test

A **smoke test** is a small, fast, critical-path test asking:

> **Does the pipeline work at all?**

A full E2E suite asks:

> **Does the pipeline correctly handle many realistic scenarios?**

| Dimension | Smoke Test | Full E2E |
|---|---|---|
| Purpose | Basic system health | Comprehensive behavior |
| Dataset | Tiny | Larger |
| Runtime | Short | Longer |
| Scenarios | Critical path | Many scenarios |
| Frequency | Often | Less frequently |
| CI | Merge/promotion | Selected CI/nightly |
| Diagnosis | Narrower | More complex |

### Why smoke tests stay small

The smoke test is a deployment and integration signal, not the entire functional test suite.

A good smoke test should tell you quickly:

```text
Is the environment usable?
Can data move through the critical path?
Does the output exist?
Is the output plausibly correct?
```

If a smoke test takes an hour, teams will avoid running it frequently.

---

## 5. Define the E2E Critical Path

Before writing code, map the pipeline.

### Batch

```text
Source
  ↓
Extractor
  ↓
Raw/Bronze
  ↓
Transformation/Silver
  ↓
Aggregation/Gold
  ↓
Validation
```

### Streaming

```text
Producer
   ↓
Kafka
   ↓
Consumer
   ↓
Stream processing
   ↓
Lakehouse/storage
   ↓
Aggregation
   ↓
Validation
```

Identify:

- inputs;
- outputs;
- dependencies;
- state;
- orchestration;
- external services;
- assertions;
- cleanup.

### Critical-path worksheet

| Question | Example |
|---|---|
| Input | `orders.csv` |
| Ingestion | Python ingestion job |
| Bronze | object-storage path |
| Silver | Spark transformation |
| Gold | `gold_daily_revenue` |
| Orchestrator | Airflow |
| External dependency | PostgreSQL |
| Event dependency | Kafka |
| Assertion | revenue + row count |
| Cleanup | test namespace |

The test should cover the smallest complete path, not every optional branch.

---

## 6. Choose the Smallest Dataset That Touches Every Stage

The best E2E dataset is usually not the largest dataset.

> **Choose the smallest dataset that exercises the complete critical path.**

For example:

```text
5 customers
10 orders
3 products
2 payments
1 late record
1 duplicate
1 null
```

This is enough to exercise:

- ingestion;
- joins;
- transformations;
- aggregation;
- output;
- validation.

### Dataset size trade-off

```text
Larger dataset
    → more coverage
    → longer runtime
    → harder diagnosis
    → more variability

Smaller dataset
    → faster
    → easier diagnosis
    → more deterministic
    → must still cover the critical path
```

The goal is not "realistic volume."

The goal is **representative system behavior with minimal cost**.

---

## 7. Batch E2E Smoke Test

Consider:

```text
orders.csv
    ↓
ingestion
    ↓
bronze_orders
    ↓
silver_orders
    ↓
gold_daily_revenue
```

A smoke test should:

1. Start or prepare the environment.
2. Load tiny test data.
3. Run the complete pipeline.
4. Wait for completion.
5. Verify outputs.
6. Verify row counts.
7. Verify important invariants.
8. Verify data-quality results.
9. Save useful artifacts.
10. Clean up.

### Basic example

### What are we testing?

The complete daily path from source data to gold output.

### Why does this matter?

A successful individual stage does not prove that the stages are correctly wired together.

### Code

```python
def test_daily_pipeline_smoke():
    load_test_data()

    run_pipeline(run_date="2026-01-15")

    assert output_exists()
    assert row_count() > 0
    assert revenue_is_correct()
    assert_quality_checks_pass()
```

### Expected behavior

The pipeline finishes and produces the expected output.

### Failure example

The pipeline exits successfully, but the gold table is empty.

A weak test might pass if it checks only the process exit code.

A strong smoke test fails on:

```python
assert row_count() > 0
```

### Production lesson

An E2E smoke test should validate **system behavior**, not merely process completion.

---

## 8. Production-Grade Batch Smoke Test

A more useful structure separates execution from assertions.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class SmokeResult:
    row_count: int
    total_revenue: float
    duplicate_count: int


def assert_smoke_result(result: SmokeResult) -> None:
    assert result.row_count > 0, "Gold output is empty"
    assert result.total_revenue >= 0, (
        f"Revenue invariant violated: {result.total_revenue}"
    )
    assert result.duplicate_count == 0, (
        f"Duplicate business keys: {result.duplicate_count}"
    )
```

The test can then be:

```python
def test_daily_pipeline_smoke():
    run_id = "smoke-2026-01-15"

    load_test_data(run_id=run_id)
    run_pipeline(run_date="2026-01-15", run_id=run_id)

    result = collect_gold_metrics(run_id=run_id)

    assert_smoke_result(result)
```

The `run_id` makes the test's input and output traceable.

---

## 9. Ephemeral Environments

E2E smoke tests need an environment in which their dependencies can be controlled.

Useful approaches include:

```text
Docker Compose
Testcontainers
Per-PR environments
Ephemeral environments
```

These connect directly to the container and infrastructure work from Module 2.18.

### Why ephemeral environments help

They provide:

- isolation;
- reproducibility;
- cleanup;
- reduced shared state;
- deterministic testing.

### The trade-off

```text
Fresh environment
    → better isolation
    → more startup time
```

versus:

```text
Shared environment
    → faster startup
    → more contamination risk
    → more flakiness
```

The right choice depends on test frequency, environment cost, and required fidelity.

---

## 10. Docker Compose for Smoke Environments

A local or CI smoke stack might contain:

```text
PostgreSQL
MinIO/object storage
Kafka
Schema Registry
pipeline runner
orchestrator
```

A conceptual Compose setup:

```yaml
services:
  postgres:
    image: postgres:16

  kafka:
    image: apache/kafka:latest

  pipeline:
    build: .
    depends_on:
      - postgres
      - kafka
```

Do not interpret `depends_on` alone as proof that a service is ready.

```text
container started
      ≠
application ready
```

Use health checks or explicit readiness checks.

---

## 11. Testcontainers for E2E Dependencies

Testcontainers is useful when the test should create disposable real services.

Conceptually:

```python
from testcontainers.postgres import PostgresContainer


def test_pipeline_with_postgres():
    with PostgresContainer("postgres:16") as postgres:
        connection_url = postgres.get_connection_url()

        run_pipeline(database_url=connection_url)

        assert_output_is_correct()
```

For a complete pipeline, additional containers may represent:

- PostgreSQL;
- Kafka;
- object storage;
- supporting services.

Use isolated namespaces, unique paths, and unique topics where parallel execution is possible.

---

## 12. Per-PR and Ephemeral Environments

For larger platforms, a pull request can receive a temporary environment:

```text
PR
 ↓
Build artifact
 ↓
Create ephemeral environment
 ↓
Deploy
 ↓
Run E2E smoke
 ↓
Collect artifacts
 ↓
Destroy environment
```

Benefits:

- real deployment wiring is exercised;
- environment-specific configuration is tested;
- permissions can be validated;
- state is isolated.

Trade-offs:

- startup cost;
- cloud cost;
- cleanup complexity;
- credential management.

The environment should be disposable by design.

---

## 13. What an E2E Smoke Test Should Assert

At minimum, validate more than job success.

### Pipeline completion

```text
Did the pipeline finish successfully?
```

### Output existence

```text
Does the expected table/file/topic/output exist?
```

### Row counts

```text
Are row counts within expected ranges?
```

### Key invariants

Examples:

```text
No duplicate order IDs
No negative revenue
Every order has a valid customer
```

### Data-quality checks

Examples:

```text
null rate
duplicate rate
schema validity
referential integrity
```

### Business assertions

Examples:

```text
expected revenue
expected order count
expected customer count
```

### Why `assert pipeline_succeeded()` is insufficient

This:

```python
assert pipeline_succeeded()
```

proves only that the process completed according to its orchestration/runtime status.

It does not prove:

```text
output exists
output is non-empty
schema is correct
keys are unique
business metrics are correct
```

A pipeline can succeed and still produce incorrect data.

---

## 14. Orchestrated Pipeline Testing

E2E tests often need to invoke an orchestrated workflow.

The roadmap includes:

- Airflow;
- Dagster;
- Prefect.

The objective is not to relearn these orchestrators.

The objective is:

> **How does the E2E smoke test invoke the complete orchestrated pipeline?**

### Airflow

For a targeted DAG run, Airflow provides commands such as:

```bash
airflow dags test <dag_id> <logical_date>
```

Use this in an appropriate test environment and validate the actual outputs produced by the workflow.

Do not stop at:

```text
DAG state = success
```

Also validate downstream outputs.

### Dagster

A useful pattern is in-process or isolated materialization:

```text
test inputs
    ↓
Dagster resources
    ↓
materialize assets
    ↓
validate outputs
```

The important concerns are:

- isolated resources;
- deterministic inputs;
- complete critical path.

### Prefect

A flow can be invoked from a test with controlled inputs:

```python
def test_flow_smoke():
    result = my_flow(test_run_id="smoke-001")
    assert result.output_rows > 0
```

Again, validate system output, not merely flow completion.

---

## 15. Streaming Smoke Tests

Streaming E2E testing differs from batch testing because the system may not have a natural completion point.

Batch:

```text
Start
 ↓
Run
 ↓
Finish
 ↓
Assert
```

Streaming:

```text
Produce event
 ↓
Wait for asynchronous processing
 ↓
Poll sink
 ↓
Observe expected result
 ↓
Assert
```

A streaming smoke test should use:

- known test events;
- deterministic event IDs;
- expected sink records;
- bounded polling;
- timeout;
- eventual-consistency awareness.

---

## 16. Streaming Smoke Test Project

Use a small known event set:

```text
100 known events
      ↓
Kafka
      ↓
stream processor
      ↓
lakehouse sink
      ↓
expected aggregates
```

The test should:

1. Prepare the environment.
2. Produce known events.
3. Record event IDs.
4. Poll the sink.
5. Wait until expected results appear.
6. Compare against expected aggregates.
7. Fail clearly on timeout.
8. Save debugging information.

### Why known IDs matter

If an event has:

```text
event_id = smoke-2026-001
```

the test can locate exactly what it produced.

This is much easier to debug than searching for arbitrary values.

---

## 17. Never Use Fixed Sleeps for Streaming Validation

Do **not** use:

```python
import time

time.sleep(30)
assert result_exists()
```

as the primary synchronization mechanism.

Fixed sleeps create:

- slow tests;
- flaky tests;
- unnecessary waiting;
- failures on slower environments.

Instead, poll until either:

```text
condition becomes true
```

or:

```text
deadline is reached
```

### Bounded polling

```python
import time


def wait_until(predicate, *, timeout=30.0, poll_interval=0.5):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if predicate():
            return

        time.sleep(poll_interval)

    raise AssertionError(
        f"Condition was not satisfied within {timeout}s"
    )
```

### Production-quality use

```python
wait_until(
    lambda: sink_contains_event_ids(expected_ids),
    timeout=60,
    poll_interval=1,
)
```

The test now waits only as long as necessary.

### What the helper must make explicit

- timeout;
- polling interval;
- eventual consistency;
- useful failure message.

---

## 18. Post-Deployment Smoke Tests

There are two distinct phases:

```text
Pre-deployment smoke
```

and:

```text
Post-deployment smoke
```

### Pre-deployment

Usually validates:

- candidate artifact;
- staging environment;
- complete wiring;
- deployment readiness.

### Post-deployment

Validates the deployed system:

```text
Staging
Production
```

Typical checks include:

- read-only canary queries;
- freshness;
- output existence;
- expected table availability;
- synthetic canary record;
- end-to-end trace.

The post-deployment test should be deliberately small.

---

## 19. Synthetic Canary Records

A synthetic canary is a deterministic, identifiable test record intentionally used to trace the system.

```text
Synthetic test order
       ↓
Production ingestion
       ↓
Bronze
       ↓
Silver
       ↓
Gold
       ↓
Canary validation
```

A canary can detect:

- ingestion failure;
- routing failure;
- transformation failure;
- permission failure;
- orchestration failure;
- downstream availability failure.

### Canary properties

A production-safe canary should be:

- clearly identifiable;
- deterministic;
- safe;
- non-sensitive;
- traceable.

For example:

```text
canary_id = "e2e-smoke-2026-01-15-001"
```

Do not use real customer information.

---

## 20. Read-Only Production Checks

Production smoke tests must not accidentally corrupt production state.

Prefer read-only checks such as:

```sql
SELECT COUNT(*)
FROM published_output;
```

or:

```sql
SELECT MAX(updated_at)
FROM published_output;
```

or:

```sql
SELECT *
FROM published_output
WHERE canary_id = 'e2e-smoke-2026-01-15-001';
```

### Safety principle

> **Production smoke testing should verify system health without becoming another source of production data corruption.**

If a platform deliberately supports synthetic production canaries, the write path must be explicitly designed and permission-scoped.

Do not casually write arbitrary test records into production tables.

---

## 21. CI/CD Placement

A practical promotion flow is:

```text
Developer
   ↓
Unit tests
   ↓
PR
   ↓
Integration / Regression
   ↓
Merge
   ↓
Build artifact
   ↓
Deploy staging
   ↓
E2E smoke
   ↓
Promotion gate
   ↓
Deploy production
   ↓
Post-deploy smoke
```

Smoke tests can also run on a schedule:

```text
Nightly smoke suite
```

### Why multiple triggers?

#### On merge

Catch integration problems early.

#### Before staging promotion

Verify the deployment candidate.

#### Before production promotion

Prevent known deployment wiring failures from reaching production.

#### After production deployment

Verify the actual deployed environment.

#### Scheduled

Detect environmental or dependency drift even when application code has not changed.

---

## 22. CI Job Design

A CI pipeline might contain:

```yaml
jobs:
  unit:
    ...

  integration:
    ...

  regression:
    ...

  e2e:
    ...

  promotion-gate:
    ...
```

Dependencies should make the intended order clear.

```text
unit
  ↓
integration
  ↓
regression
  ↓
e2e
  ↓
promotion
```

A real CI job should also manage:

- environment setup;
- credentials/secrets;
- dependencies;
- parallelism;
- artifacts;
- cleanup;
- timeouts.

GitHub Actions is one possible implementation, but the architectural pattern applies to other CI systems.

---

## 23. E2E Flakiness

A flaky test passes and fails without a meaningful code or data change.

Flakiness is a production engineering problem because repeated false failures cause teams to lose trust in CI.

### Timing

Common causes:

```text
race conditions
asynchronous processing
eventual consistency
```

### Shared state

Examples:

```text
shared database
shared Kafka topic
shared files
```

### Random data

```text
unseeded random generators
```

### External services

```text
network
API availability
cloud services
```

### Time zones

```text
UTC/local-time differences
DST
```

A good smoke suite makes these dependencies explicit.

---

## 24. Flakiness Fixes

### Deterministic data

Use seeded or deterministic generators.

```python
import random

random.seed(42)
```

For production test suites, deterministic factories are usually preferable to global random state.

### Readiness checks

Do not assume:

```text
container started == service ready
```

Wait for the actual readiness condition.

### Isolation

Use unique:

- schemas;
- buckets;
- topics;
- paths;
- run IDs.

### Frozen time

When wall-clock time affects a test, use a tool such as `time-machine` where appropriate.

### Polling

Use bounded polling for asynchronous processing rather than fixed sleeps.

### Cleanup

Always remove test state or destroy the ephemeral environment.

---

## 25. Retries — Very Important

A crucial distinction:

> **Retry transient infrastructure failures when appropriate; do not retry failed assertions until they pass.**

Bad:

```python
retry(assert_revenue_is_correct)
```

This can hide a real defect.

Better:

```text
Retry:
    temporary service startup
    connection establishment
    transient readiness

Do not blindly retry:
    incorrect row count
    wrong revenue
    missing records
    broken invariants
```

### Two failure classes

#### Transient infrastructure failure

```text
Service is still starting.
Connection temporarily unavailable.
```

A bounded retry may be reasonable.

#### Deterministic application/data failure

```text
Revenue is wrong.
Duplicate records exist.
Expected event never produces the correct result.
```

Retrying this does not fix the defect.

---

## 26. Time Budgets

E2E tests need explicit time budgets.

A conceptual hierarchy is:

```text
Unit tests       → seconds
Integration      → minutes
E2E smoke        → bounded minutes
Nightly E2E      → larger budget
```

Do not treat these as universal numerical requirements.

The appropriate budget depends on:

- infrastructure;
- pipeline complexity;
- CI environment;
- business criticality.

### Detecting an oversized smoke test

If the smoke test contains:

```text
millions of records
many unrelated scenarios
long historical backfill
large cluster startup
multiple unrelated external APIs
```

it may no longer be a smoke test.

Split broad scenarios into deeper integration or nightly suites.

---

## 27. Parallelism

`pytest-xdist` can reduce test duration, but parallel E2E tests can collide.

Potential shared resources:

- databases;
- Kafka topics;
- object-storage paths;
- temporary directories;
- ports.

### Namespace resources

Use:

```text
run_id
worker_id
test_id
```

For example:

```python
def smoke_topic(worker_id: str, run_id: str) -> str:
    return f"smoke-test-{worker_id}-{run_id}"
```

The same principle applies to:

```text
s3://bucket/smoke/<run_id>/
schema_<run_id>
```

### When parallelism helps

Parallelism helps when tests are independent and infrastructure has enough capacity.

### When it hurts

If tests contend for a shared database, Kafka partition, port, or environment, parallelism may create more nondeterminism than it removes.

Isolation comes before speed.

---

## 28. Chaos and Recovery Variants

An advanced smoke test can validate recovery.

Conceptual scenario:

```text
Pipeline running
     ↓
Kill worker
     ↓
Worker restarts
     ↓
Pipeline resumes
     ↓
Expected result eventually appears
```

Possible targets:

```text
Kafka
stream processor
database
worker
container
```

The purpose is not to become a full chaos-engineering program.

The smoke test should validate a specific recovery contract involving:

- fault tolerance;
- retries;
- checkpointing;
- idempotency;
- recovery.

### Example assertion

The test should not merely verify:

```text
worker restarted
```

It should verify:

```text
worker restarted
      ↓
pipeline recovered
      ↓
no unacceptable duplicate/corrupt output
      ↓
expected final result exists
```

---

## 29. Failure Reporting

A failed E2E test should answer:

> Which stage failed?

> What input was used?

> What run ID was used?

> What output was expected?

> What output was observed?

> Where are the logs?

> Where are the artifacts?

Example:

```text
E2E SMOKE TEST FAILED

Run ID: smoke-2026-01-15-001

Failed stage:
silver → gold

Expected:
1,000 rows

Actual:
1,247 rows

Likely issue:
duplicate join expansion

Artifacts:
logs/
outputs/
sample-diff/
```

This is much more actionable than:

```text
AssertionError
```

### Structured result

A smoke test can emit structured metadata:

```python
failure_context = {
    "run_id": run_id,
    "failed_stage": "silver_to_gold",
    "expected_rows": 1000,
    "actual_rows": 1247,
    "artifact_path": "artifacts/smoke-001/",
}
```

The CI system can then expose it in logs or reports.

---

## 30. CI Artifacts

When an E2E test fails, preserve useful evidence.

Examples:

```text
Pipeline logs
DAG logs
Application logs
Input dataset
Output sample
Schema
Row counts
Metrics
Execution metadata
Run ID
Container logs
Kafka offsets
```

### Why artifacts matter

Without artifacts:

```text
CI failed
    ↓
environment disappears
    ↓
engineer tries to reproduce
    ↓
failure may disappear
```

With artifacts:

```text
CI failed
    ↓
logs + run ID + input + output sample
    ↓
diagnose failure
```

Artifacts reduce mean time to diagnosis.

---

## 31. End-to-End Failure Simulation

Deliberately break the system.

### Failure 1 — Wrong table name

```text
Silver job reads the wrong table.
```

Expected:

```text
E2E output assertion fails.
```

### Failure 2 — Missing permission

```text
Gold output cannot be written.
```

Expected:

```text
Pipeline failure or missing output
+
permission evidence
```

### Failure 3 — Wrong configuration

```text
Environment variable points to incorrect storage.
```

Expected:

```text
output missing
+
configuration diagnostic
```

### Failure 4 — Missing Kafka topic

```text
Streaming smoke test cannot consume expected topic.
```

Expected:

```text
bounded timeout
+
topic diagnostic
```

### Failure 5 — Duplicate records

```text
Expected:
100 events

Observed:
200 events
```

Expected:

```text
duplicate/invariant assertion fails
```

### Failure 6 — Delayed streaming result

Slow the sink intentionally.

The polling helper should tolerate delay up to its defined timeout.

It should not wait indefinitely.

### Failure 7 — Component crash

Kill a worker/container.

Expected:

```text
worker recovery
→ continued processing
→ expected final output
```

### Failure workflow

```text
Failure
   ↓
Detection
   ↓
Assertion message
   ↓
Logs/artifacts
   ↓
Diagnosis
   ↓
Fix
   ↓
Passing smoke test
```

---

## 32. Production E2E Project

Build a realistic system:

```text
                  ┌──────────────┐
                  │ Source/API   │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │ Ingestion    │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │ Bronze       │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │ Silver       │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │ Gold         │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │ Consumer     │
                  └──────────────┘
```

Build both:

```text
Batch smoke test
```

and:

```text
Streaming smoke test
```

### Project requirements

Demonstrate:

- tiny deterministic data;
- complete pipeline execution;
- meaningful assertions;
- polling;
- timeouts;
- orchestration;
- isolation;
- failure reporting;
- CI integration;
- artifact collection;
- post-deployment canary.

---

## 33. Required Hands-On Exercises

### Exercise 1 — Batch Smoke Test

**Goal:** Validate a complete batch critical path.

**Scenario:** A daily orders pipeline.

**Input:** Tiny deterministic orders dataset.

**Task:**

1. Start the stack.
2. Load the tiny test-data tier.
3. Run the full daily pipeline for one date.
4. Check outputs.
5. Check row counts.
6. Check invariants.
7. Check quality results.

**Expected behavior:** The complete path succeeds and meaningful output assertions pass.

**Failure cases:** Empty output, wrong count, duplicate key, incorrect revenue.

**Hint:** Keep the dataset small enough to diagnose manually.

---

### Exercise 2 — Streaming Smoke Test

**Goal:** Validate asynchronous processing.

**Scenario:**

```text
100 known events
    ↓
Kafka
    ↓
stream processor
    ↓
lakehouse sink
```

**Task:** Produce known events, poll the sink, and compare expected aggregates.

**Expected behavior:** The test completes when the expected output appears.

**Failure cases:** Missing topic, consumer failure, delayed result, wrong aggregate.

**Hint:** Use event IDs and a bounded timeout.

Do not use fixed sleeps as the primary synchronization mechanism.

---

### Exercise 3 — Post-Deployment Smoke Test

**Goal:** Validate a deployed environment safely.

**Scenario:** Staging environment after deployment.

**Task:** Add:

- read-only checks;
- freshness checks;
- output existence;
- synthetic canary record;
- trace from source to gold.

**Expected behavior:** The deployment is accepted only when the critical path is healthy.

**Failure cases:** Wrong path, stale output, canary missing.

**Hint:** Keep production checks read-only where possible.

---

### Exercise 4 — CI Promotion Gate

**Goal:** Prevent broken deployments from promotion.

**Task:** Add E2E smoke tests as:

```text
CI promotion gate
```

and:

```text
nightly job
```

**Expected behavior:** Promotion stops when the critical path fails.

**Failure cases:** Missing dependency, incorrect environment configuration, failed output assertion.

**Hint:** Separate fast PR checks from broader scheduled suites.

---

### Exercise 5 — Flakiness Elimination

**Goal:** Make the smoke suite deterministic.

Run the smoke test:

```text
20 consecutive times
```

Identify and fix:

- timing races;
- shared state;
- random data;
- external-service variability;
- timezone problems;
- missing readiness checks.

**Expected behavior:** The same known input produces stable test behavior.

**Hint:** Never solve flakiness by simply adding longer sleeps.

---

### Exercise 6 — Failure Artifacts

**Goal:** Make failures diagnosable.

**Task:** Force a smoke-test failure and save:

- logs;
- output samples;
- execution metadata;
- failed stage;
- expected/actual metrics.

**Expected behavior:** CI artifacts contain enough evidence to begin diagnosis without reproducing the run immediately.

**Hint:** Always include a unique run ID.

---

## 34. Practical Debugging Guide

### Pipeline never starts

**Symptom**

No meaningful pipeline execution begins.

**Likely causes**

- environment setup;
- missing dependency;
- incorrect command;
- orchestration issue.

**Diagnostic steps**

Check:

```bash
python --version
docker compose ps
docker compose logs
```

Then inspect the orchestrator's task/run state.

**Fix**

Correct environment or orchestration configuration before changing assertions.

---

### Pipeline starts but hangs

**Symptom**

The smoke test reaches a stage but never completes.

**Likely causes**

- deadlock;
- waiting dependency;
- Kafka consumer;
- missing input;
- external service.

**Diagnostic steps**

Inspect:

```text
task state
container state
consumer state
logs
input availability
```

**Fix**

Identify the actual blocking dependency. Do not increase the timeout blindly.

---

### Output missing

**Symptom**

The pipeline reports success but the expected output does not exist.

**Likely causes**

- wrong path;
- wrong table;
- permissions;
- failed upstream stage.

**Diagnostic steps**

Check the resolved output location and execution logs.

**Fix**

Correct the pipeline wiring or deployment configuration.

---

### Row count wrong

**Symptom**

Expected 100 rows, observed 143.

**Likely causes**

- duplicate joins;
- missing records;
- incorrect filters;
- incremental boundary error.

**Diagnostic SQL**

```sql
SELECT order_id, COUNT(*)
FROM gold_orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

**Fix**

Trace the first stage where the count diverges.

---

### Streaming timeout

**Symptom**

Expected records never appear before the deadline.

**Likely causes**

- consumer not running;
- wrong topic;
- wrong partition;
- processing delay;
- checkpoint issue.

**Diagnostic steps**

Check:

```text
topic exists
consumer is active
event IDs were published
consumer offsets advance
sink is receiving records
```

**Fix**

Resolve the actual stream-processing problem rather than increasing the timeout indefinitely.

---

### Local pass, CI failure

**Symptom**

The same test passes locally and fails in CI.

**Likely causes**

- environment variables;
- timing;
- resource constraints;
- shared state;
- time zones;
- dependency versions.

**Diagnostic steps**

Compare:

```text
Python version
dependency lock
environment variables
timezone
resource limits
container versions
```

**Fix**

Make dependencies explicit and eliminate environment-sensitive assumptions.

---

## 35. Common Mistakes

### Mistake 1 — Huge smoke datasets

Running E2E tests on millions of rows can make them too slow for frequent validation.

### Mistake 2 — Fixed sleeps

Avoid:

```python
time.sleep(30)
```

as the primary synchronization mechanism for asynchronous systems.

### Mistake 3 — Retrying failed assertions

Do not retry:

```text
wrong revenue
wrong row count
missing records
broken invariants
```

until they pass.

### Mistake 4 — Unsafe production writes

Do not casually insert smoke-test records into production tables.

### Mistake 5 — No failure artifacts

A failed test without logs or context is difficult to diagnose.

### Additional mistakes

- non-deterministic test data;
- shared state;
- missing cleanup;
- no timeout;
- too many scenarios in smoke tests;
- too few critical assertions;
- ignoring production configuration;
- no run ID;
- unclear ownership;
- treating smoke tests as monitoring;
- using smoke tests instead of lower-level tests.

---

## 36. Smoke Tests vs Production Monitoring

This boundary is critical.

### Smoke Test

Validates:

> **Can the system successfully execute this known path?**

Characteristics:

- controlled input;
- known expected behavior;
- CI/staging/post-deploy;
- deployment validation;
- small deterministic dataset.

### Production Monitoring

Validates:

> **Is the real production system healthy over time?**

Characteristics:

- real production data;
- expected operational ranges;
- continuous execution;
- runtime health;
- ongoing anomaly detection.

| Smoke Testing | Production Monitoring |
|---|---|
| Controlled input | Real production data |
| Known expected behavior | Expected operational ranges |
| CI/staging/post-deploy | Continuous production |
| Deployment validation | Runtime health |
| Small deterministic dataset | Real workload |

Smoke tests do not replace production monitoring.

They establish that a known critical path works at a specific point in time.

---

## 37. Production E2E Architecture

A mature project might structure E2E tests as:

```text
tests/
├── e2e/
│   ├── batch/
│   ├── streaming/
│   ├── post_deploy/
│   └── recovery/
│
├── data/
│   └── smoke/
│
└── conftest.py
```

Shared infrastructure can provide:

- fixtures;
- environment configuration;
- test data;
- run IDs;
- cleanup;
- artifact handling;
- CI markers.

The exact repository layout can differ, but the separation of concerns is valuable.

---

## 38. Test Tagging

Use markers to selectively execute E2E suites.

```python
import pytest


@pytest.mark.e2e
@pytest.mark.batch
def test_daily_pipeline_smoke():
    ...


@pytest.mark.e2e
@pytest.mark.streaming
def test_streaming_pipeline_smoke():
    ...
```

CI can then select:

```text
e2e
batch
streaming
post_deploy
recovery
```

For example:

```bash
pytest -m "e2e and batch"
```

This allows the same test suite to support multiple execution schedules.

---

## 39. Security and Safety

Production-oriented smoke tests must be safe.

### Credentials

Never expose production credentials in test code.

Use:

- CI secret management;
- workload identity where supported;
- short-lived credentials;
- least privilege.

### Data

Avoid production PII in fixtures.

Prefer:

- synthetic data;
- non-sensitive canary records;
- isolated staging data.

### Production permissions

Use read-only checks where possible.

If a production canary requires a write:

- make the path explicit;
- restrict the permission;
- use identifiable synthetic records;
- guarantee cleanup or controlled retention.

### Environment isolation

Ensure staging and ephemeral tests cannot accidentally point at unrelated production resources.

---

## 40. Code Explanation Format

For significant code examples, use this structure:

### What are we testing?

State the exact system behavior.

### Why does this matter?

Explain the production failure it prevents.

### Code

```python
# Example implementation
```

### Expected behavior

State what a passing test proves.

### Failure example

Show a realistic failure.

### Production lesson

Explain how the pattern scales beyond the toy example.

This avoids presenting code without engineering context.

---

## 41. Exercise Format

Every major exercise should contain:

```text
Goal
Scenario
Input
Task
Expected behavior
Failure cases
Hint
```

The exercises should require reasoning and implementation.

Do not immediately reveal the complete solution when the exercise is intended for learner practice.

---

## 42. Checkpoint

Before leaving this module, you should be able to:

```text
[ ] Explain smoke tests.
[ ] Distinguish smoke tests from full E2E tests.
[ ] Design a minimal E2E dataset.
[ ] Build a batch smoke test.
[ ] Run an orchestrated pipeline inside a test.
[ ] Build a streaming smoke test.
[ ] Use polling instead of fixed sleeps.
[ ] Use timeouts correctly.
[ ] Design post-deployment smoke tests.
[ ] Build synthetic canary records.
[ ] Place smoke tests correctly in CI/CD.
[ ] Diagnose flaky E2E tests.
[ ] Apply isolation and readiness checks.
[ ] Define E2E time budgets.
[ ] Parallelize safely.
[ ] Test recovery from component failures.
[ ] Save useful CI artifacts.
[ ] Debug failed pipeline stages.
[ ] Distinguish smoke testing from production monitoring.
```

### Checkpoint questions

1. Why is a smoke test intentionally smaller than a full E2E suite?
2. What is the smallest dataset that can still validate your critical path?
3. Why is `assert pipeline_succeeded()` insufficient?
4. Why are fixed sleeps a poor synchronization strategy for streaming?
5. What should be retried, and what should not?
6. How would you isolate parallel E2E runs?
7. What should a post-deployment canary prove?
8. What evidence should a failed smoke test retain?
9. How would you test recovery after a worker crash?
10. Where does smoke testing end and production monitoring begin?

---

## 43. Senior Data Engineer Interview Preparation

### Beginner

**1. What is an E2E smoke test?**

A small system-level test that validates the critical path of a deployed or deployable pipeline.

**2. Why do we need E2E tests if unit tests exist?**

Unit tests validate individual components. E2E tests validate the wiring and behavior of the complete system.

**3. What is the difference between smoke testing and full E2E testing?**

Smoke testing is narrow, fast, and critical-path focused; full E2E testing is broader and covers more scenarios.

### Intermediate

**4. How would you design a batch pipeline smoke test?**

Discuss tiny deterministic data, isolated environment, full execution, output assertions, row counts, invariants, artifacts, and cleanup.

**5. How would you test an Airflow DAG end to end?**

Invoke the DAG/run in an appropriate test environment and validate the outputs of the complete workflow, not merely DAG state.

**6. How would you test a Kafka-based streaming pipeline?**

Publish known events, identify them deterministically, poll the sink with a timeout, validate expected results, and retain offsets/logs on failure.

**7. Why should you avoid fixed sleeps?**

They are slow and flaky because they guess how long asynchronous processing will take.

**8. How do you make E2E tests deterministic?**

Use deterministic inputs, isolated resources, readiness checks, bounded polling, controlled time, stable IDs, cleanup, and explicit configuration.

### Advanced

**9. How would you design E2E tests for a multi-stage lakehouse?**

Map source → Bronze → Silver → Gold, use tiny deterministic data, validate each important boundary, and assert final business behavior.

**10. How would you design a post-deployment canary?**

Use a safe synthetic record or read-only validation, trace it through the critical path, validate freshness and final output, and keep the operation tightly scoped.

**11. How would you prevent E2E tests from becoming flaky?**

Discuss isolation, readiness, polling, deterministic data, frozen time, unique resources, bounded retries, and artifact collection.

**12. How would you parallelize E2E tests safely?**

Namespace every shared resource by run/worker/test ID or use isolated environments.

**13. When should infrastructure failure be retried?**

When it is plausibly transient, such as startup or connection readiness. Deterministic data assertions should not be blindly retried.

**14. How would you test recovery after a worker crashes?**

Inject the failure, verify restart/recovery, then verify the final expected result and important invariants.

**15. What artifacts would you collect after an E2E failure?**

Logs, run ID, inputs, output samples, metrics, schema, container logs, Kafka offsets, failed stage, and execution metadata.

**16. How would you determine whether an E2E test belongs in PR CI or nightly CI?**

Evaluate runtime, stability, environment cost, criticality, and whether the test validates a deployment-critical path.

### System Design

> **Design an E2E smoke-testing strategy for a production platform consisting of REST ingestion, Kafka, PostgreSQL, object storage, Spark, dbt, and Airflow.**

A strong answer should cover:

```text
Test environment
      ↓
Test data
      ↓
Batch tests
      ↓
Streaming tests
      ↓
Assertions
      ↓
Canary
      ↓
CI/CD
      ↓
Failure handling
      ↓
Artifacts
      ↓
Monitoring boundary
```

---

## 44. Final Assessment

### Scenario

You operate an e-commerce data platform.

**Sources:**

- REST APIs;
- PostgreSQL CDC;
- Kafka.

**Processing:**

- Bronze;
- Silver;
- Gold;
- Spark;
- dbt.

**Orchestration:**

- Airflow.

**Storage:**

- Object storage.

**Deployment:**

- CI/CD.

### Design and implementation task

Build a production-oriented E2E strategy containing:

1. Tiny deterministic batch dataset.
2. Batch E2E smoke test.
3. Streaming smoke test.
4. Orchestrated DAG test.
5. Output assertions.
6. Row-count assertions.
7. Invariant checks.
8. Data-quality checks.
9. Polling with timeout.
10. Post-deployment staging smoke test.
11. Synthetic canary.
12. CI promotion gate.
13. Nightly smoke job.
14. Flakiness controls.
15. Time budget.
16. Parallelization strategy.
17. Failure artifact collection.
18. Recovery test.
19. Production safety controls.
20. Monitoring boundary.

### Architectural reasoning

Your design must explain:

```text
What is isolated?
What is shared?
What is deterministic?
What is retried?
What is asserted?
Where are artifacts stored?
What blocks deployment?
What happens after deployment?
How is a streaming timeout diagnosed?
How is a worker crash validated?
Which checks are read-only in production?
```

Memorizing tools is not enough.

The goal is to demonstrate that you can design a reliable system-level test strategy.

---

## 45. Failure-Injection Final Lab

Intentionally break the system with at least:

```text
Wrong table
Wrong storage path
Missing permission
Missing Kafka topic
Duplicate records
Delayed streaming result
Component crash
Incorrect transformation
```

For each failure, demonstrate:

```text
Bug
 ↓
Smoke test failure
 ↓
Failure report
 ↓
Artifact
 ↓
Diagnosis
 ↓
Fix
 ↓
Green run
```

### Required outcome

The learner should be able to explain:

- why the failure occurred;
- why the smoke test detected it;
- what evidence was retained;
- how the fix was validated;
- how the test prevents recurrence.

---

## 46. Production E2E Smoke-Test Checklist

### Test Design

```text
[ ] Smoke tests are small.
[ ] Critical path is covered.
[ ] Inputs are deterministic.
[ ] Outputs are meaningful.
[ ] Assertions check more than job success.
```

### Batch

```text
[ ] Full batch path executes.
[ ] Outputs exist.
[ ] Row counts are validated.
[ ] Invariants are validated.
[ ] Quality checks are validated.
```

### Streaming

```text
[ ] Known events are produced.
[ ] Sink is polled.
[ ] Timeout exists.
[ ] Fixed sleeps are avoided.
[ ] Expected aggregates are validated.
```

### Orchestration

```text
[ ] DAG/flow is executed.
[ ] Dependencies are exercised.
[ ] Run state is validated.
```

### Post-Deployment

```text
[ ] Staging smoke tests exist.
[ ] Production checks are safe.
[ ] Canary record exists.
[ ] Freshness is checked.
```

### Reliability

```text
[ ] Test isolation exists.
[ ] Readiness checks exist.
[ ] Flakiness is controlled.
[ ] Infrastructure retries are bounded.
[ ] Assertions are not blindly retried.
```

### CI/CD

```text
[ ] Smoke tests run on merge.
[ ] Smoke tests gate promotion.
[ ] Nightly execution exists.
[ ] Parallelism is safe.
[ ] Time budgets exist.
[ ] Failure artifacts are retained.
```

### Recovery

```text
[ ] Component failure is tested.
[ ] Recovery behavior is validated.
```

### Production Safety

```text
[ ] No unsafe production writes.
[ ] No production PII in fixtures.
[ ] Credentials are secured.
[ ] Canary data is safe.
```

### Observability

```text
[ ] Failed stage is reported.
[ ] Logs are retained.
[ ] Output samples are retained.
[ ] Run ID is reported.
[ ] CI artifacts are available.
```

### Monitoring Boundary

```text
[ ] Smoke tests are not treated as production monitoring.
```

---

## 47. Final Quality Gate

The module explicitly covers:

```text
✓ Smoke tests vs full E2E tests
✓ Batch smoke tests
✓ Tiny datasets
✓ Ephemeral environments
✓ Docker Compose
✓ Testcontainers
✓ Per-PR environments
✓ Pipeline completion assertions
✓ Output existence
✓ Row-count assertions
✓ Key invariants
✓ Data-quality assertions
✓ Airflow DAG testing
✓ Dagster in-process testing
✓ Prefect flow testing
✓ Streaming smoke tests
✓ Known events
✓ Polling
✓ Timeouts
✓ No fixed sleeps
✓ Post-deployment smoke tests
✓ Staging
✓ Production
✓ Read-only canary queries
✓ Freshness checks
✓ Synthetic canary records
✓ CI/CD placement
✓ Merge execution
✓ Promotion gates
✓ Scheduled execution
✓ Flakiness causes
✓ Deterministic data
✓ Readiness checks
✓ Isolation
✓ Frozen time
✓ Infrastructure-only retries
✓ Time budgets
✓ Parallelism
✓ Chaos/recovery variants
✓ Failure-stage reporting
✓ Logs
✓ CI artifacts
✓ Smoke testing vs production monitoring
✓ Hands-on batch exercise
✓ Hands-on streaming exercise
✓ Post-deployment exercise
✓ CI integration exercise
✓ 20 consecutive green runs
✓ Failure injection
✓ Debugging guide
✓ Common mistakes
✓ Checkpoint
✓ Senior-level interview questions
✓ Final assessment
✓ Production checklist
```

---

## 48. Final Engineering Principles

Keep these principles throughout production Data Engineering:

> **A successful pipeline run does not prove that the complete data path is correct.**

> **Smoke tests should validate the critical path, not become a second full functional test suite.**

> **Use the smallest deterministic dataset that exercises the complete system.**

> **Never use fixed sleeps as the primary synchronization mechanism for asynchronous pipelines.**

> **Retry transient infrastructure conditions, not incorrect data assertions.**

> **A failed E2E test is only useful when it provides enough evidence to diagnose the failure.**

> **Production canaries must be safe, deterministic, non-sensitive, and traceable.**

> **Smoke testing validates a known path at a point in time; production monitoring validates real system health over time.**

The final reliability workflow is:

```text
Deploy candidate
      ↓
Run critical-path smoke test
      ↓
Observe meaningful output
      ↓
Validate business/data invariants
      ↓
Promote only if healthy
      ↓
Run post-deployment smoke
      ↓
Continue with production monitoring
```

Topic 07 therefore completes the testing progression:

```text
Unit correctness
      ↓
DataFrame equality
      ↓
Integration correctness
      ↓
Property-based invariants
      ↓
Realistic test data
      ↓
Schema/contract regression
      ↓
End-to-end system correctness
```

The objective is not to prove that every possible scenario works.

The objective is to ensure that the **critical production path is continuously proven to work as a system**.


---

## 49. Final Mastery Questions

Answer these without looking at the module:

1. Why can every component test pass while the complete pipeline fails?
2. What makes a smoke test different from a full E2E suite?
3. How do you choose the smallest dataset that still exercises the critical path?
4. What should a batch smoke test assert besides process success?
5. How does a streaming smoke test synchronize with asynchronous processing?
6. Why are fixed sleeps inferior to bounded polling?
7. Which failures are appropriate for retries?
8. How do you isolate parallel E2E tests?
9. What makes a production canary safe?
10. What artifacts should be retained after a failed smoke test?
11. How would you test recovery after killing a worker?
12. What belongs in PR CI versus nightly E2E?
13. How do smoke tests interact with Airflow, Dagster, and Prefect?
14. Why should smoke tests not replace production monitoring?
15. What would cause you to reject a smoke-test design in a production code review?

If you can answer these questions and complete the final assessment and failure-injection lab, you have the intended system-level competency for Topic 07.
