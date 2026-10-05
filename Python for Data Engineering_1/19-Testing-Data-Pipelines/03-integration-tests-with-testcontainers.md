---
title: "Integration Tests with Testcontainers"
module: "Stage 2 — Python for Data Engineering"
topic: "2.19.03"
filename: "03-integration-tests-with-testcontainers.md"
level: "Beginner → Intermediate → Advanced → Production"
---

# 03 — Integration Tests with Testcontainers

> **Production principle:** Integration tests should prove that your code works with the real behavior of the systems it depends on, while remaining isolated, deterministic, reproducible, and safe to run automatically.

This module teaches the learner to verify Data Engineering components against **real disposable infrastructure** instead of relying exclusively on mocks. The progression is deliberately simple-to-production:

```text
Basic testing
  ↓
Unit vs integration
  ↓
Why mocks are insufficient
  ↓
Docker + Testcontainers
  ↓
PostgreSQL
  ↓
Isolation + migrations + COPY/MERGE/SCD2
  ↓
MinIO + Parquet
  ↓
Kafka + commits + at-least-once + rebalancing
  ↓
HTTP integration / recorded HTTP
  ↓
Parallel execution + CI
  ↓
Failure injection + diagnostics
  ↓
Production-grade integration testing
```

### Learning outcomes

By the end, the learner can:

- distinguish unit and integration tests;
- explain what a real dependency proves that a mock cannot;
- use Testcontainers with PostgreSQL, MinIO, and Kafka;
- design pytest fixtures and lifecycle management;
- isolate state across tests and parallel workers;
- test Alembic migrations, `COPY`, `MERGE`, and SCD Type 2 against real PostgreSQL;
- test MinIO object storage and Parquet round trips;
- test Kafka producer/consumer behavior, commits, at-least-once semantics, and rebalances;
- use recorded HTTP interactions appropriately;
- run integration tests in CI with a measurable time budget;
- deliberately inject dependency failures and diagnose them;
- design a production-ready integration-testing strategy.

### Required stack

```text
Python 3.12+
uv
pytest
pytest-xdist
testcontainers[postgres,kafka,minio]
PostgreSQL
MinIO
Kafka
Alembic
boto3
pandas / Polars where useful
DuckDB where useful
PySpark only where relevant
pytest-recording
Docker
```

## 1. The Core Question — What Are We Trying to Prove?

A unit test usually proves a local computation:

```text
function → known input → expected output
```

An integration test proves that multiple components interact correctly:

```text
application code
      ↓
real database / object storage / broker / API
      ↓
real protocol + real semantics
      ↓
real response
      ↓
assertion
```

The key question is:

> **What production risk would remain if I replaced this dependency with a mock?**

If the risk involves SQL semantics, driver behavior, transactions, serialization, offsets, commits, object paths, authentication, migrations, or protocol behavior, a real integration test is usually warranted.

An integration test is not “a bigger unit test.” Its subject is the **boundary between components**.

## 2. Unit Tests vs Integration Tests

| Dimension | Unit Test | Integration Test |
|---|---|---|
| Dependencies | Isolated | Real/disposable |
| Database | Usually mocked | Real disposable DB |
| Kafka | Usually mocked | Real broker |
| Object storage | Usually mocked | Real object store |
| Speed | Very fast | Slower |
| Scope | Small | Multiple components |
| Debugging | Simpler | More involved |
| CI frequency | Very frequent | Controlled |
| Typical failures | Logic | Logic + integration + configuration + infrastructure |

Data Engineering needs both. Unit tests provide rapid feedback on transformation logic. Integration tests catch defects that appear only at the boundary with a real database, broker, storage service, or API.

The test pyramid for this module is:

```text
                  E2E Smoke
                      ↑
              Schema / Contract
                      ↑
                  Integration
                      ↑
            Unit / DataFrame Tests
```

Topic 03 sits above unit/DataFrame testing and below broader system-level regression and smoke testing.

## 3. Why Mocks Are Not Enough

Mocks are excellent for fast local logic and controlled error paths. They are not proof that a real dependency behaves as expected.

### PostgreSQL

A mocked database may happily accept:

```sql
INSERT INTO orders ...
```

while real PostgreSQL rejects it because of:

- SQL syntax or dialect differences;
- missing columns;
- type conversion;
- constraints;
- transaction semantics;
- isolation behavior;
- PostgreSQL-specific SQL;
- `COPY`;
- `MERGE`;
- migration ordering.

### Kafka

A fake Kafka client cannot prove:

- broker connectivity;
- serialization;
- partitions;
- offsets;
- commits;
- consumer groups;
- rebalances;
- broker restart behavior.

### Object storage

A mocked S3 client does not prove:

- real object upload/download;
- object-key/path behavior;
- metadata;
- bucket behavior;
- Parquet bytes;
- permissions;
- round-trip compatibility.

### Practical rule

Use mocks when the test's purpose is application branching. Use a real disposable dependency when the test's purpose is the **integration contract itself**.

## 4. Testcontainers Fundamentals

Testcontainers starts real services inside temporary containers for automated tests.

```text
pytest
  |
  +---- PostgreSQL container
  |
  +---- MinIO container
  |
  +---- Kafka container
```

Important concepts:

- **Image** — packaged service filesystem and metadata.
- **Container** — running instance of an image.
- **Port mapping** — exposes the service to the test process.
- **Environment** — configuration passed to the service.
- **Readiness** — service can actually accept the operation the test needs.
- **Lifecycle** — create, start, wait, test, collect diagnostics, stop.
- **Disposable infrastructure** — the test owns the dependency and can destroy it safely.

Testcontainers does not remove the need to understand PostgreSQL, Kafka, or object storage. It automates their lifecycle so the test can use real behavior without depending on shared production infrastructure.

## 5. Installation and Project Setup

Install the test dependencies with the roadmap's Python tooling:

```bash
uv add --dev pytest pytest-xdist "testcontainers[postgres,kafka,minio]"   alembic boto3 pytest-recording
```

Docker must be available locally and in CI:

```bash
docker version
docker info
```

A useful project layout is:

```text
data-pipeline/
├── pyproject.toml
├── src/
│   └── pipeline/
├── alembic/
├── tests/
│   ├── unit/
│   └── integration/
│       ├── conftest.py
│       ├── test_postgres.py
│       ├── test_minio.py
│       ├── test_kafka.py
│       └── test_api.py
└── README.md
```

Keep integration tests visibly separate from unit tests. Developers should immediately know which tests require Docker and disposable services.

## 6. First Testcontainers Example — PostgreSQL

### Scenario

Prove that Python can connect to a real PostgreSQL service, create a table, insert a row, query it, and clean up.

### Infrastructure

```python
from testcontainers.postgres import PostgresContainer
import psycopg

def test_postgres_round_trip() -> None:
    with PostgresContainer("postgres:16") as postgres:
        with psycopg.connect(postgres.get_connection_url()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE orders (
                        order_id INTEGER PRIMARY KEY,
                        amount NUMERIC(12, 2) NOT NULL
                    )
                    """
                )
                cur.execute(
                    "INSERT INTO orders (order_id, amount) VALUES (%s, %s)",
                    (1, 125.50),
                )
                conn.commit()

                cur.execute(
                    "SELECT order_id, amount FROM orders WHERE order_id = %s",
                    (1,),
                )
                row = cur.fetchone()

        assert row == (1, 125.50)
```

### Walk-through

1. Testcontainers creates a PostgreSQL container.
2. The service starts.
3. The test obtains the connection endpoint.
4. PostgreSQL executes real DDL and DML.
5. The query reads real persisted state.
6. The assertion checks the returned row.
7. The context manager cleans up.

The example is intentionally small. The learning objective is to establish the lifecycle before introducing multiple services.

## 7. Container Lifecycle and pytest Fixtures

A context manager is useful for one test:

```python
with PostgresContainer("postgres:16") as postgres:
    ...
```

A suite benefits from pytest fixtures:

```python
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture
def postgres():
    with PostgresContainer("postgres:16") as container:
        yield container
```

Then:

```python
def test_database_is_reachable(postgres) -> None:
    assert postgres.get_connection_url()
```

The fixture owns setup and teardown, even when a test fails.

### Fixture scopes

pytest provides:

```text
function
class
module
session
```

A useful production pattern is:

```text
session-scoped container
+
function-scoped state
```

This shares expensive infrastructure while keeping mutable test state isolated.

### Lifecycle failure

If container startup fails, preserve the startup exception and service logs. Do not allow cleanup code to hide the original cause.

## 8. Readiness — Synchronization, Not sleep()

This distinction is mandatory:

```text
container process started
        ≠
service ready for the required operation
```

Avoid:

```python
import time
time.sleep(10)
```

A fixed sleep can be too short on slow CI and waste time on fast machines.

Prefer:

- port checks as an early signal;
- health checks;
- log-based readiness;
- connection-based readiness;
- bounded retries;
- explicit timeouts.

A robust model is:

```text
start
  ↓
poll readiness
  ↓
ready? ── no ──> retry before deadline
  |
 yes
  ↓
test
```

For a PostgreSQL test, “can establish a database connection and execute the required probe query” is a stronger readiness condition than “TCP port 5432 is open.”

> **Readiness is a synchronization problem, not a fixed-sleep problem.**

## 9. PostgreSQL Integration Testing

A realistic PostgreSQL integration suite covers:

- connections;
- schemas and tables;
- inserts and queries;
- transactions;
- constraints;
- indexes where relevant;
- cleanup;
- migrations.

Example transaction test:

```python
def test_transaction_commit(postgres) -> None:
    with psycopg.connect(postgres.get_connection_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE ledger (id INTEGER PRIMARY KEY, amount INTEGER)"
            )
            cur.execute("INSERT INTO ledger VALUES (1, 100)")
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT amount FROM ledger WHERE id = 1")
            assert cur.fetchone() == (100,)
```

The important property is that the test exercises real PostgreSQL transaction and storage behavior.

## 10. PostgreSQL Test Isolation

Without isolation:

```text
Test A inserts data
    ↓
Test B sees Test A's data
    ↓
order-dependent suite
```

Isolation strategies required by the roadmap are:

### Transaction rollback

```text
BEGIN → test → ROLLBACK
```

Fast and useful when all writes stay inside the transaction. Less suitable when application code opens independent connections, commits internally, or uses background workers.

### Unique schema per test

```text
test A → schema_test_a
test B → schema_test_b
```

Strong isolation and good parallelism. Cleanup must remove schemas.

### Truncation

```sql
TRUNCATE orders, customers RESTART IDENTITY CASCADE;
```

Simple, but foreign-key relationships, cascading behavior, and sequence state must be understood.

### Dedicated container per test

Maximum isolation at substantial startup cost.

### Trade-off table

| Strategy | Speed | Isolation | Complexity | Parallel-friendly |
|---|---:|---:|---:|---:|
| Transaction rollback | High | High when applicable | Medium | Depends |
| Unique schema | High | High | Medium | High |
| Truncation | Medium | High | Low/Medium | Depends |
| New container/test | Low | Very high | Low | Expensive |

There is no universal best strategy.

## 11. Session-Scoped Containers with Isolated Per-Test State

The pattern is:

```text
One PostgreSQL container
   ├── Test A → isolated state
   ├── Test B → isolated state
   └── Test C → isolated state
```

Example:

```python
import uuid
import pytest

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16") as container:
        yield container

@pytest.fixture
def schema_name() -> str:
    return f"test_{uuid.uuid4().hex[:12]}"
```

The container starts once. Each test gets a unique schema or another isolated namespace.

This is often much faster than creating a PostgreSQL container for every test while preserving strong isolation.

> **Share infrastructure; isolate state.**

## 12. Alembic Migration Integration Tests

Migrations must be tested against a real PostgreSQL instance.

A migration can parse successfully yet fail because of real schema state, existing data, constraints, locking, ordering, or database-specific semantics.

### Test flow

```text
Empty PostgreSQL
      ↓
alembic upgrade head
      ↓
Inspect schema
      ↓
Insert realistic rows
      ↓
Apply next migration
      ↓
Verify data preserved
      ↓
Verify new schema
```

Typical commands:

```bash
alembic upgrade head
```

and, where supported by the project's migration policy:

```bash
alembic downgrade <revision>
```

Verify more than process exit status:

- tables;
- columns;
- types;
- constraints;
- indexes;
- data preservation;
- migration ordering.

A migration integration test should fail if the real database rejects the migration.

## 13. Testing PostgreSQL COPY

`COPY` must be tested against real PostgreSQL because a mock cannot prove delimiter handling, quoting, null representation, type conversion, or database behavior.

```text
CSV / stream
    ↓
COPY
    ↓
PostgreSQL
    ↓
SELECT
    ↓
assert
```

Example:

```python
from io import StringIO

def test_copy_loads_csv(postgres):
    csv_data = StringIO(
        "order_id,amount
"
        "1,100.50
"
        "2,25.00
"
    )

    with psycopg.connect(postgres.get_connection_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE orders (
                    order_id INTEGER PRIMARY KEY,
                    amount NUMERIC(12, 2) NOT NULL
                )
                """
            )
            with cur.copy(
                "COPY orders (order_id, amount) "
                "FROM STDIN WITH (FORMAT csv, HEADER true)"
            ) as copy:
                copy.write(csv_data.getvalue())
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM orders")
            assert cur.fetchone()[0] == 2
```

Also test malformed input. The failure assertion should use the specific PostgreSQL driver exception expected by the project.

## 14. Testing MERGE

Use a realistic staging-to-target flow:

```text
staging_orders
      ↓
    MERGE
      ↓
target_orders
```

Cover:

1. new record;
2. existing record;
3. changed record;
4. unchanged record;
5. duplicate source keys;
6. idempotent re-run.

Example SQL shape:

```sql
MERGE INTO target_orders AS t
USING staging_orders AS s
ON t.order_id = s.order_id
WHEN MATCHED AND t.amount <> s.amount THEN
    UPDATE SET amount = s.amount
WHEN NOT MATCHED THEN
    INSERT (order_id, amount)
    VALUES (s.order_id, s.amount);
```

Run the real statement against the real database. Then execute the operation twice and assert that the second execution does not introduce unintended duplicates or history changes.

The exact SQL must match the PostgreSQL version and schema used by the project.

## 15. Testing SCD Type 2

A representative SCD Type 2 table contains:

```text
customer_id
attribute
valid_from
valid_to
is_current
```

Test this sequence:

```text
initial record
    ↓
attribute changes
    ↓
previous record closes
    ↓
new version becomes current
```

Assertions should include:

1. initial version exists;
2. changed attribute creates a new version;
3. previous version has an appropriate `valid_to`;
4. new version is current;
5. validity intervals do not overlap;
6. re-running the operation does not corrupt history.

Use deterministic timestamps. Do not make correctness depend on the wall clock at test execution time.

A real PostgreSQL test proves the SQL, constraints, transactions, persistence, and historical state—not just the Python function that generated the SQL.

## 16. MinIO / Object Storage Integration

MinIO provides an S3-compatible object-storage service that can run locally in a disposable container.

Test:

- bucket creation;
- object upload;
- listing;
- download;
- metadata;
- prefixes;
- cleanup;
- unavailable-service behavior.

Example client shape:

```python
import boto3

def make_s3(endpoint: str, access_key: str, secret_key: str):
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="us-east-1",
    )
```

Then perform a real round trip:

```python
s3.create_bucket(Bucket="integration")
s3.put_object(
    Bucket="integration",
    Key="raw/example.txt",
    Body=b"hello data engineering",
)
response = s3.get_object(
    Bucket="integration",
    Key="raw/example.txt",
)
assert response["Body"].read() == b"hello data engineering"
```

Use unique bucket names or worker-specific namespaces for parallel tests.

## 17. MinIO + Parquet Integration Test

The required round trip is:

```text
DataFrame
   ↓
Parquet
   ↓
MinIO
   ↓
Download
   ↓
Read Parquet
   ↓
Compare
```

Example:

```python
from io import BytesIO
import pandas as pd

def test_parquet_round_trip(s3):
    frame = pd.DataFrame(
        {"order_id": [1, 2], "amount": [10.5, 20.0]}
    )

    buffer = BytesIO()
    frame.to_parquet(buffer, index=False)
    buffer.seek(0)

    s3.put_object(
        Bucket="integration",
        Key="orders/orders.parquet",
        Body=buffer.getvalue(),
    )

    obj = s3.get_object(
        Bucket="integration",
        Key="orders/orders.parquet",
    )

    restored = pd.read_parquet(BytesIO(obj["Body"].read()))
    pd.testing.assert_frame_equal(restored, frame)
```

The equality assertion is a dependency on Topic 02; do not duplicate that module's detailed comparison theory here.

Verify:

- correct object key;
- object exists;
- content is readable;
- schema is preserved;
- values survive the round trip.

## 18. MinIO vs Mocks

| Need | Mock | MinIO container |
|---|---|---|
| Application branching | Excellent | Unnecessary |
| Fast error simulation | Excellent | Useful but slower |
| Real upload/download | No | Yes |
| Object-key behavior | No | Yes |
| Parquet round trip | No | Yes |

A good suite uses both techniques at the appropriate level.

## 19. Kafka Integration Testing

The real Kafka flow is:

```text
Producer
   ↓
Kafka broker
   ↓
Topic / partition
   ↓
Consumer group
   ↓
Consumer
   ↓
Database or sink
```

Teach and test:

- broker;
- topic;
- partition;
- producer;
- consumer;
- consumer group;
- offsets;
- commits.

A Testcontainers Kafka fixture should hide the container lifecycle behind a pytest fixture. Pin the Kafka image used by CI rather than depending on `latest`.

Conceptual fixture:

```python
@pytest.fixture(scope="session")
def kafka():
    with KafkaContainer("confluentinc/cp-kafka:7.6.1") as container:
        yield container
```

Because Testcontainers and Kafka images evolve, validate the exact advertised-listener/bootstrap configuration against the pinned versions used by the repository.

## 20. Kafka Producer Integration Test

The complete test is:

```text
Start broker
  ↓
Create topic
  ↓
Produce event
  ↓
Consume event
  ↓
Assert payload
```

Verify:

- serialization;
- event structure;
- topic;
- key;
- partitioning where relevant.

Do not assert merely that `producer.send()` was called. Produce to the real broker and consume the real record.

Example event:

```python
event = {
    "event_type": "order.created",
    "order_id": "o-123",
    "amount": 42.50,
}
```

The consumer assertion should prove that the serialized event accepted by Kafka can be read and decoded by the consumer used by the pipeline.

## 21. Kafka Consumer, Commits, and At-Least-Once

The critical processing sequence is:

```text
Message
  ↓
Process
  ↓
Commit
```

If the consumer commits first:

```text
Message
  ↓
Commit
  ↓
Process fails
```

the message may be lost.

If processing succeeds but the process fails before committing:

```text
Message
  ↓
Process succeeds
  ↓
Crash before commit
  ↓
Message delivered again
```

This is why at-least-once processing requires safe downstream side effects.

### Required integration scenario

1. Produce an event.
2. Consume it.
3. Perform a database side effect.
4. Fail before commit.
5. Restart/re-run.
6. Observe duplicate delivery.
7. Verify the sink is idempotent or deduplicates by event ID.
8. Verify commit occurs only after successful processing.

The test should explicitly document the intended delivery semantics.

## 22. Kafka Consumer Groups and Rebalancing

Consumer groups distribute partitions across consumers. Membership changes can trigger a rebalance.

A manageable test:

```text
Start broker
  ↓
Create multi-partition topic
  ↓
Start consumer A in group G
  ↓
Start consumer B in group G
  ↓
Observe assignment
  ↓
Stop one consumer
  ↓
Observe reassignment
  ↓
Produce more records
  ↓
Verify processing continues
```

Do not assert exact rebalance timing. Assert stable outcomes: records are eventually processed, offsets remain valid, and downstream side effects follow the intended delivery semantics.

A rebalance test should be controlled rather than an attempt to reproduce every possible distributed-system race.

## 23. Kafka Failure Injection

Test:

- broker restart;
- connection interruption;
- consumer timeout;
- duplicate delivery;
- delayed messages.

Failure pattern:

```text
Working system
    ↓
Break dependency
    ↓
Observe failure
    ↓
Diagnose
    ↓
Recover
    ↓
Assert intended behavior
```

For broker restart, verify recovery according to the application's contract. Do not claim exactly-once behavior unless the architecture actually implements and proves it.

## 24. HTTP API Integration Testing

There are three useful levels:

### Mock API

Fast and deterministic. Use for application branching and most local error paths.

### Recorded HTTP

Use `pytest-recording` or another VCR-style approach to capture and replay controlled interactions.

### Real test API/container

Use when actual service behavior matters and a controlled test endpoint/service exists.

| Technique | Speed | Real dependency | Deterministic | Best use |
|---|---:|---:|---:|---|
| Mock | Very high | No | High | Local logic |
| Recorded HTTP | High | Captured | High | Stable external interactions |
| Test service/container | Medium | Yes | High when controlled | Integration behavior |
| Public production API | Low | Yes | Low | Avoid in CI |

The automated suite should not depend on an uncontrolled public internet service.

## 25. Recorded HTTP / pytest-recording

Recorded HTTP testing turns a controlled real interaction into a deterministic test artifact.

```text
Controlled request
    ↓
real test service
    ↓
sanitized recording

Later test
    ↓
replay recording
```

Teach:

- recording responses;
- replay;
- deterministic fixtures;
- authentication concerns;
- stale recordings;
- sensitive information.

Never commit:

- access tokens;
- API keys;
- cookies;
- customer PII.

Also test:

- HTTP 429;
- token refresh;
- timeout;
- malformed response;
- schema change;
- connection failure.

For `429`, verify bounded retry/backoff behavior rather than sleeping for the real rate-limit interval. For token refresh, use controlled credentials or a recording/test service.

## 26. pytest Fixture Architecture

A production-oriented integration test tree is:

```text
tests/
└── integration/
    ├── conftest.py
    ├── test_postgres.py
    ├── test_minio.py
    ├── test_kafka.py
    └── test_api.py
```

`conftest.py` should centralize:

- container lifecycle;
- service configuration;
- readiness;
- worker-aware resource names;
- cleanup;
- diagnostics.

Service-specific assertions belong in test modules.

Use dependency injection:

```python
@pytest.fixture
def db(postgres):
    return Database(postgres.get_connection_url())
```

Then:

```python
def test_orders_are_loaded(db):
    ...
```

The test focuses on behavior rather than container mechanics.

## 27. Fixture Scopes

Use:

```text
function
class
module
session
```

based on cost and isolation.

A common pattern:

```text
session-scoped infrastructure
+
function-scoped state
```

The session container reduces startup cost. Function-scoped schemas, buckets, and topics prevent contamination.

Do not make everything session-scoped merely for speed. Session scope increases the amount of mutable state that can leak across tests.

## 28. Parallel Execution with pytest-xdist

Run integration tests in parallel:

```bash
pytest -n auto tests/integration
```

Parallelism introduces:

- database-state collisions;
- schema collisions;
- topic collisions;
- bucket collisions;
- race conditions;
- resource contention.

Use worker-specific namespaces:

```text
schema_test_gw0
schema_test_gw1

topic_orders_gw0
topic_orders_gw1

bucket_test_gw0
bucket_test_gw1
```

Example:

```python
import os

def worker_id() -> str:
    return os.getenv("PYTEST_XDIST_WORKER", "gw0")

def resource_name(prefix: str) -> str:
    return f"{prefix}_{worker_id()}"
```

Every mutable resource created by a parallel test must either be isolated or intentionally immutable.

## 29. Container Reuse and Slim Test Images

There is a trade-off:

```text
new container per test
```

provides maximal isolation but costs startup time.

```text
reusable/session container
```

is faster but requires disciplined state cleanup.

Do not enable reuse blindly. Measure first.

Slim images reduce:

- image pull time;
- disk usage;
- startup overhead.

Use:

- minimal base images;
- pinned versions;
- only required dependencies;
- no unnecessary packages.

Correctness and reproducibility take priority over shaving a few seconds from a suite.

## 30. CI Execution

A typical CI flow is:

```text
Developer push
    ↓
lint / type checks
    ↓
unit tests
    ↓
integration tests
    ↓
Docker + Testcontainers
    ↓
disposable services
    ↓
reports + diagnostics
```

CI requirements include:

- Docker availability or supported Testcontainers execution;
- sufficient CPU/memory;
- network access to required container images;
- bounded readiness timeouts;
- safe parallelism;
- cleanup;
- log/artifact retention.

Do not use production credentials or services in the integration suite.

A failed CI integration test should retain enough evidence to determine whether the cause was application logic, dependency behavior, readiness, resource exhaustion, or configuration.

## 31. Integration-Test Time Budgets

Integration tests are slower than unit tests. Define a measurable repository-level budget rather than inventing a universal number.

Conceptually:

```text
Unit tests        → seconds
Integration suite → controlled minutes
```

Measure:

```bash
pytest tests/integration --durations=20
```

Track:

- total wall-clock time;
- container startup time;
- slowest tests;
- fixture setup;
- serial vs parallel performance.

If the suite is slow, investigate before optimizing:

1. reuse expensive infrastructure carefully;
2. isolate state instead of restarting services;
3. use xdist;
4. namespace worker resources;
5. use slim images;
6. remove unnecessary network round trips.

Never sacrifice deterministic isolation just to meet a timing target.

## 32. Failure-Path Testing

A production integration suite must test:

```text
dependency fails
```

not only:

```text
everything works
```

For each failure:

```text
Setup
  ↓
Failure injection
  ↓
Expected behavior
  ↓
Assertion
  ↓
Recovery
```

Required cases:

| Failure | Verify |
|---|---|
| Database connection killed | clear failure/retry/reconnect semantics |
| Database timeout | bounded timeout and correct retry behavior |
| UNIQUE violation | real constraint and safe state |
| FOREIGN KEY violation | referential contract |
| NOT NULL violation | invalid data rejected |
| CHECK violation | business constraint |
| Kafka broker restart | recovery according to delivery contract |
| Kafka connection failure | bounded failure/retry |
| MinIO unavailable | safe storage failure |
| API timeout | timeout policy |
| API 429 | rate-limit/backoff policy |
| Invalid API response | validation/error path |

## 33. Killing Database Connections

Controlled database failure should establish:

```text
Application
   ↓
DB connection
   ↓
connection disappears
```

Then verify whether the application:

- fails clearly;
- retries only transient errors;
- reconnects when designed to do so;
- avoids corrupting state;
- does not falsely report success.

Do not retry deterministic constraint failures simply because they are exceptions.

## 34. Database Timeouts

Cover:

- connection timeout;
- statement timeout;
- client timeout;
- retry policy;
- backoff.

Use a controlled timeout with a short bounded deadline. Avoid long `sleep()` calls.

The test should assert the behavior contract:

```text
operation begins
  ↓
deadline reached
  ↓
expected timeout
  ↓
retry or fail according to policy
```

It should not assert an exact wall-clock duration that becomes flaky on shared CI runners.

## 35. Constraint Failure Tests

Use real PostgreSQL to trigger:

```text
UNIQUE
FOREIGN KEY
NOT NULL
CHECK
```

For each test:

1. create the real schema;
2. submit deliberately invalid data;
3. assert the specific database exception category;
4. verify transaction/state behavior;
5. clean up.

This proves that the database itself enforces the contract.

## 36. Observability and Debugging

When a Testcontainers test fails, inspect evidence before increasing retries.

### Debug checklist

1. Did the container start?
2. Did readiness complete?
3. What do container logs say?
4. Is the endpoint correct?
5. Are credentials/configuration correct?
6. What SQL executed?
7. What Kafka topic/partition/offset was involved?
8. What objects exist in MinIO?
9. What HTTP response/status was received?
10. Did another worker contaminate the resource?

Preserve in CI:

- container logs;
- pytest output;
- relevant SQL/log output;
- Kafka offsets and topic state;
- object keys;
- test duration;
- dependency/version information.

Do not log secrets while adding diagnostics.

## 37. Security Requirements

Integration tests must be safe to run automatically.

Never use:

- production credentials;
- production databases;
- production buckets;
- real customer PII.

Use:

- disposable credentials;
- synthetic data;
- local containers;
- isolated CI resources.

For HTTP recordings, scrub authorization headers, tokens, cookies, API keys, and customer information.

A test environment is still a security boundary.

## 38. Common Integration-Testing Mistakes

| Mistake | Failure mode | Better approach |
|---|---|---|
| Mocking everything | Production integration defects escape | Real disposable dependencies for integration behavior |
| `sleep()` readiness | Flaky/slow tests | Condition-based readiness |
| Container per test unnecessarily | Slow suite | Session/module container + isolated state |
| Shared DB state | Order dependence | Rollback/schema/truncation |
| Hard-coded ports | Port conflicts | Container-mapped endpoints |
| Shared Kafka topics | Old messages leak | Unique topics/namespaces |
| Shared buckets | Stale objects | Unique bucket/prefix |
| Resource leaks | CI instability | Fixture lifecycle |
| Public internet dependency | Nondeterministic CI | Mock/record/controlled service |
| Huge fixtures | Slow, opaque tests | Minimal behavior-focused data |
| Retry assertions | Hidden races | Correct synchronization |
| Ignoring logs | Blind debugging | Preserve diagnostics |
| Production credentials | Security incident | Disposable credentials |
| Production PII | Privacy risk | Synthetic data |
| No failure tests | Recovery bugs reach production | Deliberate failure injection |
| Shared xdist resources | Intermittent collisions | Worker-specific namespaces |

## 39. Hands-On Project — Data Pipeline Integration Test Lab

### Scenario

Build tests for:

```text
PostgreSQL
   ↓
Python transformation
   ↓
MinIO
   ↓
Kafka
   ↓
Consumer
   ↓
PostgreSQL
```

### Required coverage

1. PostgreSQL connectivity;
2. Alembic migrations;
3. `COPY`;
4. `MERGE`;
5. SCD2;
6. MinIO Parquet;
7. Kafka producer;
8. Kafka consumer;
9. Kafka commit behavior;
10. at-least-once semantics;
11. API interaction;
12. failure scenarios;
13. isolated test state;
14. parallel execution;
15. CI execution;
16. integration-test timing.

### Suggested structure

```text
integration-test-lab/
├── pyproject.toml
├── src/
├── alembic/
└── tests/
    ├── unit/
    └── integration/
        ├── conftest.py
        ├── test_migrations.py
        ├── test_copy.py
        ├── test_merge.py
        ├── test_scd2.py
        ├── test_minio_parquet.py
        ├── test_kafka_producer.py
        ├── test_kafka_consumer.py
        └── test_failures.py
```

### Acceptance criteria

- no production credentials;
- no production data;
- condition-based readiness;
- isolated mutable state;
- safe parallel execution;
- explicit Kafka commit semantics;
- failure-path coverage;
- useful diagnostics;
- CI execution;
- measured integration-test duration.

## 40. Failure-Injection Lab

Intentionally break infrastructure.

### Failure 1 — PostgreSQL connection disappears

```text
Start service
→ perform operation
→ inject failure
→ observe behavior
→ verify retry/failure contract
→ clean up
```

### Failure 2 — PostgreSQL timeout

Create a bounded slow operation and verify timeout handling.

### Failure 3 — UNIQUE constraint violation

Submit duplicate data and verify the expected constraint exception and safe transaction state.

### Failure 4 — Kafka broker restart

Produce/consume, restart the broker, and verify recovery according to the application's semantics.

### Failure 5 — Kafka consumer timeout

Create a controlled timeout and verify that unprocessed work is not incorrectly acknowledged.

### Failure 6 — MinIO unavailable

Make object storage unreachable and verify the pipeline does not report a false success.

### Failure 7 — API 429

Return a controlled 429 and verify bounded retry/backoff behavior.

### Failure 8 — API token refresh failure

Simulate expired credentials and failed refresh. Verify clear failure and no infinite retry loop.

For each lab record:

```text
Failure injected
Expected behavior
Observed behavior
Root cause
Recovery mechanism
Assertion
Diagnostic evidence
```

## 41. Checkpoint

The learner must be able to explain and demonstrate:

- what an integration test is;
- why mocks are insufficient;
- what Testcontainers provides;
- container lifecycle;
- readiness and why `sleep()` is unreliable;
- PostgreSQL isolation strategies;
- session-scoped containers;
- Alembic upgrade/downgrade testing;
- `COPY`, `MERGE`, and SCD2;
- MinIO and Parquet integration;
- Kafka producer/consumer behavior;
- commits and at-least-once semantics;
- consumer groups and rebalancing;
- recorded HTTP testing;
- xdist and worker-specific resources;
- failure injection;
- CI execution;
- integration-test time budgets.

### Practical checkpoint

1. Build a PostgreSQL fixture.
2. Add unique schema isolation.
3. Test an Alembic migration.
4. Test `COPY` and malformed input.
5. Test idempotent merge behavior.
6. Test SCD2 history.
7. Test MinIO Parquet.
8. Produce and consume Kafka events.
9. Demonstrate duplicate delivery before commit.
10. Run with `pytest -n auto`.
11. Inject a dependency failure and preserve diagnostics.

## 42. Production Interview Preparation

### Q1. Why do Data Engineering systems need integration tests if unit coverage is high?

Unit tests prove local logic. Integration tests prove that local logic works with real databases, brokers, storage systems, drivers, protocols, and configuration.

### Q2. Why not mock PostgreSQL?

A mock cannot prove SQL semantics, constraints, transactions, migrations, `COPY`, `MERGE`, or real driver behavior.

### Q3. What does Testcontainers provide?

Disposable real infrastructure with automated lifecycle management.

### Q4. Why is `sleep()` poor readiness logic?

Startup time varies. A fixed delay can be too short or unnecessarily long.

### Q5. Session container or container per test?

Use session/module scope when state can be isolated reliably and startup is expensive. Use a new container when maximum isolation is required.

### Q6. How do you isolate PostgreSQL tests?

Use transaction rollback, unique schemas, truncation, or dedicated containers according to the application's connection and state model.

### Q7. How do you make xdist tests safe?

Namespace mutable resources by worker and avoid shared mutable state.

### Q8. What does at-least-once imply?

A message can be delivered again if processing succeeds but the consumer fails before committing. Downstream side effects therefore need idempotency/deduplication where required.

### Q9. How do you test a rebalance?

Change consumer-group membership against a real multi-partition topic and verify eventual processing and valid offsets.

### Q10. How do you test migrations?

Run them against real disposable PostgreSQL, inspect schema/data, and test supported upgrade/downgrade/recovery behavior.

### Q11. How do you test `COPY`?

Load realistic data into real PostgreSQL and verify stored values and malformed-input behavior.

### Q12. How do you test MinIO?

Use real bucket/object operations and a Parquet round trip.

### Q13. When should recorded HTTP be used?

When realistic HTTP behavior matters but a controlled full external dependency is expensive, rate-limited, unavailable, or nondeterministic.

### Q14. How do you debug a failing Testcontainers test?

Inspect container logs, readiness, endpoint configuration, SQL, Kafka offsets, object keys, API responses, and test timing.

### Q15. How do you keep integration tests fast?

Reuse infrastructure carefully, isolate state, choose appropriate fixture scopes, parallelize safely, use slim images, and remove unnecessary setup/network calls.

### Q16. What is an integration-test time budget?

A measurable repository-level target based on the project's size and CI environment.

### Q17. What must never be used?

Production credentials, production databases/buckets, and real customer PII.

### Q18. What makes integration tests flaky?

Uncontrolled timing, shared state, public external services, nondeterministic data, race conditions, weak readiness checks, and unstable assertions.

### Q19. Should every dependency failure be retried?

No. Retry only explicitly transient failures. Do not hide deterministic defects behind blanket retries.

### Q20. What is the core principle?

Use real dependencies when their behavior is the subject of the test, while keeping the environment disposable, isolated, deterministic, diagnosable, and safe.

## 43. Final Assessment

### Scenario

A production data platform has extensive unit tests but almost no integration tests. A deployment succeeds in CI but fails in production because of:

1. a PostgreSQL migration issue;
2. incorrect Kafka commit behavior;
3. an object-storage path bug.

Design and implement an integration-testing strategy.

### Required implementation

```text
PostgreSQL Testcontainer
+
Alembic
+
COPY
+
MERGE
+
SCD2
+
MinIO
+
Kafka
+
API testing
+
Isolation
+
Failure injection
+
Parallel execution
+
CI integration
```

### Required demonstrations

**PostgreSQL**

- migration upgrade;
- supported downgrade/recovery;
- `COPY` success and malformed-input failure;
- `MERGE` new/update/idempotency cases;
- SCD2 history;
- constraint failures;
- connection/timeout failure.

**MinIO**

- isolated bucket;
- Parquet upload/download;
- object-path assertion;
- unavailable-storage failure.

**Kafka**

- producer/consumer;
- commit ordering;
- duplicate delivery / at-least-once;
- consumer group;
- controlled rebalance;
- broker restart.

**API**

- successful interaction;
- recorded interaction;
- 429;
- timeout;
- token-refresh failure;
- malformed response.

**Execution**

- xdist-safe namespaces;
- CI-compatible Docker/Testcontainers setup;
- measurable duration;
- actionable diagnostics.

A written explanation is not enough. The learner must implement and execute the tests and demonstrate that they fail when the corresponding integration defect is deliberately introduced.

## 44. Final Self-Review Checklist

```text
[ ] Unit vs integration testing
[ ] Why integration tests matter
[ ] Why mocks are insufficient
[ ] Testcontainers fundamentals
[ ] Docker prerequisites
[ ] PostgreSQL container
[ ] Container lifecycle
[ ] Readiness strategies
[ ] No fixed sleep anti-pattern
[ ] pytest fixtures
[ ] Fixture scope
[ ] Session-scoped containers
[ ] Per-test isolated state
[ ] Transaction rollback
[ ] Unique schemas
[ ] Unique buckets
[ ] Unique Kafka topics
[ ] Truncation
[ ] Isolation trade-offs
[ ] Alembic
[ ] Upgrade testing
[ ] Downgrade testing
[ ] COPY
[ ] MERGE
[ ] SCD2
[ ] MinIO
[ ] Parquet round-trip
[ ] Kafka producer
[ ] Kafka consumer
[ ] Kafka commits
[ ] At-least-once semantics
[ ] Consumer groups
[ ] Rebalancing
[ ] Broker restart
[ ] HTTP integration testing
[ ] pytest-recording / VCR-style testing
[ ] API 429
[ ] Token refresh
[ ] Parallel pytest workers
[ ] pytest-xdist
[ ] Worker-specific resources
[ ] Container reuse
[ ] Slim images
[ ] CI execution
[ ] Integration test time budgets
[ ] Database connection failure
[ ] Database timeout
[ ] Constraint failures
[ ] Broker failures
[ ] Object-storage failures
[ ] API failures
[ ] Container logs
[ ] Debugging
[ ] Security
[ ] No production credentials
[ ] No production PII
[ ] Common mistakes
[ ] Hands-on project
[ ] Failure-injection lab
[ ] Checkpoint
[ ] Interview questions
[ ] Final assessment
```

## 45. Production Quality Gate

### Technical accuracy

Validate Testcontainers, pytest, PostgreSQL, MinIO, Kafka, Alembic, and HTTP examples against the exact versions pinned by the repository. Pin container image versions; do not build CI around `latest`.

### Roadmap alignment

Every Topic 03 concept in the supplied specification is represented.

### Progressive learning

```text
Beginner → Intermediate → Advanced → Production
```

### Practicality

The learner actually creates and executes integration tests.

### Failure handling

Dependency failures are deliberately tested, not merely discussed.

### Isolation

State contamination and parallel-worker conflicts are explicitly addressed.

### Performance

Integration duration is measured against a repository-defined budget.

### CI readiness

Docker/Testcontainers execution, diagnostics, cleanup, and parallelism are addressed.

### Security

No production credentials, production databases, production buckets, or real customer PII.

### Scope control

This file remains focused on:

```text
Integration Tests with Testcontainers
```

It does not attempt to teach the later Module 2.19 topics in depth.

## 46. Connection to Module 2.19

Topic 03 connects the preceding unit/DataFrame testing layers to broader pipeline verification:

```text
                  E2E Smoke
                      ↑
              Schema / Contract
                      ↑
                  Integration
                      ↑
            Unit / DataFrame Tests
```

Topic 01 focuses on testing transformations with fixture DataFrames. Topic 02 focuses on DataFrame equality and tolerance assertions. Topic 03 adds real dependency behavior.

Later topics should build on this foundation rather than duplicating it. The boundary is clear:

> **Topic 03 proves that components work together against real disposable dependencies. It is not the complete Module 2.19.**

## 47. Final Engineering Principle

Reliable integration testing is a deliberate discipline:

```text
Real dependency
+
Disposable environment
+
Deterministic test data
+
Strong isolation
+
Controlled failure
+
Useful diagnostics
=
Reliable integration testing
```

Before writing an integration test, ask:

1. What production boundary can fail?
2. What behavior can a mock not prove?
3. What is the smallest real disposable dependency required?
4. How will mutable state be isolated?
5. How will readiness be detected?
6. What failure should be injected?
7. What evidence will diagnose failure?
8. What is the repository's acceptable execution time?
9. Can the test run safely in CI and in parallel?
10. Does it use only synthetic data and non-production credentials?

If these questions have explicit answers, the test is moving beyond “a test that uses Docker” toward a production-grade integration test.

## Appendix A — Practical Command Reference

```bash
# Install
uv add --dev pytest pytest-xdist "testcontainers[postgres,kafka,minio]"   alembic boto3 pytest-recording

# Unit suite
pytest tests/unit

# Integration suite
pytest tests/integration

# Parallel integration suite
pytest -n auto tests/integration

# Slowest tests
pytest tests/integration --durations=20

# One test
pytest tests/integration/test_postgres.py::test_postgres_round_trip -q

# Docker diagnostics
docker version
docker info
docker ps
docker ps -a

# Alembic
alembic upgrade head
alembic downgrade <revision>
```

## Appendix B — Troubleshooting Decision Tree

```text
Test failed
   |
   +-- Container did not start?
   |      ├─ Check Docker daemon
   |      ├─ Check image/version
   |      ├─ Check resource limits
   |      └─ Preserve startup logs
   |
   +-- Container started but cannot connect?
   |      ├─ Check readiness
   |      ├─ Check mapped endpoint
   |      ├─ Check credentials
   |      └─ Check network configuration
   |
   +-- PostgreSQL assertion failed?
   |      ├─ Inspect SQL
   |      ├─ Inspect schema
   |      ├─ Check transaction state
   |      └─ Check isolation
   |
   +-- Kafka assertion failed?
   |      ├─ Check topic
   |      ├─ Check partition/offset
   |      ├─ Check consumer group
   |      ├─ Check commit timing
   |      └─ Check duplicate-delivery assumptions
   |
   +-- MinIO assertion failed?
   |      ├─ Check bucket
   |      ├─ Check object key
   |      ├─ Check object bytes
   |      └─ Check Parquet schema
   |
   +-- API assertion failed?
          ├─ Check status code
          ├─ Check recording freshness
          ├─ Check auth handling
          └─ Check timeout/rate-limit contract
```

The goal is to diagnose the dependency boundary rather than randomly increasing sleeps or retries.

## Appendix C — Topic 03 Traceability

The supplied Topic 03 specification requires the module to cover the full path from basic integration concepts to production Testcontainers execution. The main sections above intentionally map the required concepts into teaching, examples, failure scenarios, project work, checkpoint questions, and assessment.

The central scope is preserved:

```text
Integration Tests with Testcontainers
```

No later Module 2.19 topic is taught as a substitute for Topic 03.
