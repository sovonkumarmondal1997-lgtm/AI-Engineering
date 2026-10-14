# Testing and Validating DAGs

> **Stage 2 — Python for Data Engineering**  
> **Module 2.13 — Orchestration and Workflow Management**  
> **Topic 11 — Testing and Validating DAGs**
>
> **Learning path:** Beginner → Foundation → Intermediate → Advanced → Production-grade

---

## 1. Learning Objectives

By the end of this topic, you should be able to:

- Explain what it means to test an orchestration workflow.
- Explain why "the DAG parses" is not the same as "the DAG is correct."
- Build a layered testing strategy for Airflow DAGs.
- Write import tests for every DAG.
- Debug an Airflow DAG locally with `dag.test()`.
- Use `airflow dags test` appropriately.
- Unit-test task and business logic as ordinary Python.
- Write DAG structure tests.
- Validate expected tasks and dependencies.
- Reason about cycle detection.
- Write policy and contract tests.
- Validate owners, tags, retries, timeouts, start dates, and catch-up behavior.
- Detect forbidden operators.
- Use Ruff and static analysis.
- Understand and protect DAG parse-time budgets.
- Mock hooks and connections safely.
- Use isolated environment-variable-based test configuration.
- Test templates and data intervals.
- Test quality gates and prove that publishing is blocked when quality checks fail.
- Test retry, timeout, failure, idempotency, and safe-rerun behavior.
- Use Docker-backed integration tests with isolated services.
- Test Dagster assets at the appropriate testing layer.
- Test Prefect flows without turning every test into an infrastructure test.
- Design CI validation for orchestration code.
- Validate deployments after release.
- Detect missing or disappeared DAGs.
- Build a complete testing workflow for a production Data Engineering platform.

The central principle is:

> **Testing an orchestration system means proving correctness at multiple layers, not merely proving that a workflow can run.**

---

# 2. What Does "Testing a DAG" Mean?

A DAG can be:

- syntactically valid;
- importable;
- structurally valid;
- logically wrong;
- operationally unsafe;
- production-invalid.

Therefore:

> **"THE DAG PARSES" DOES NOT MEAN "THE DAG IS CORRECT."**

Consider:

```text
Python syntax
     ↓
DAG imports
     ↓
DAG object exists
     ↓
Task graph is correct
     ↓
Policies are correct
     ↓
Business logic is correct
     ↓
External integrations work
     ↓
Failure behavior is correct
     ↓
Deployment is correct
```

Every layer answers a different question.

---

## 2.1 Example: A DAG That Parses but Is Wrong

Suppose the intended workflow is:

```text
extract
   ↓
transform
   ↓
quality_check
   ↓
publish
```

But the actual DAG is:

```text
extract
   ↓
transform ─────────→ publish
      \
       → quality_check
```

The Python may import successfully.

The scheduler may see the DAG.

The tasks may execute.

Yet the system can publish data before the quality gate finishes.

This is an orchestration correctness failure.

---

# 3. Testing Pyramid for Orchestration

A useful testing model is:

```text
                 Production / Deployment Validation
                              ▲
                              │
                       Integration Tests
                              ▲
                              │
                       Template / Interval
                              ▲
                              │
                       Policy / Contract
                              ▲
                              │
                       DAG Structure
                              ▲
                              │
                         DAG / Flow
                              ▲
                              │
                         Unit Tests
                              ▲
                              │
                       Static Analysis
```

A practical eight-layer model is:

1. Static checks
2. Import/parse tests
3. Unit tests
4. DAG structure tests
5. Policy/contract tests
6. Template/data-interval tests
7. Integration tests
8. End-to-end/deployment validation

---

## 3.1 Why the Pyramid Matters

Lower layers are generally:

- faster;
- cheaper;
- more deterministic;
- easier to debug.

Higher layers are generally:

- slower;
- more environment-dependent;
- more realistic;
- more expensive.

Do not turn every test into a full Airflow integration test.

---

## 3.2 What Each Layer Catches

| Layer | Main question |
|---|---|
| Static analysis | Is the code structurally and stylistically sane? |
| Import test | Can the DAG be loaded? |
| Unit test | Does business logic work? |
| Structure test | Is the workflow graph correct? |
| Policy test | Does the DAG follow engineering rules? |
| Template/interval test | Does runtime context produce the correct values? |
| Integration test | Do real external services behave as expected? |
| Deployment validation | Did the production system actually load the intended workflow? |

---

# 4. Testing Business Logic Separately from Orchestration

A strong architecture keeps business logic outside the DAG definition whenever possible.

## 4.1 Bad Pattern

```python
from airflow.decorators import dag
from datetime import datetime

@dag(
    dag_id="orders_daily",
    start_date=datetime(2026, 1, 1),
)
def pipeline():
    # hundreds of lines of business logic
    # API calls
    # transformations
    # SQL generation
    # validation
    # writes
    ...

dag = pipeline()
```

Problems:

- difficult unit testing;
- slow parsing if work happens at module scope;
- hidden dependencies;
- large orchestration boundary;
- difficult failure isolation.

---

## 4.2 Better Pattern

```python
def transform_orders(rows: list[dict]) -> list[dict]:
    return [
        {
            "order_id": row["order_id"],
            "amount": float(row["amount"]),
        }
        for row in rows
    ]
```

Then:

```python
from airflow.decorators import task

@task
def transform_orders_task(rows: list[dict]) -> list[dict]:
    return transform_orders(rows)
```

Now:

```text
business logic
     ↓
ordinary Python unit test

task wrapper
     ↓
orchestration/structure test
```

This separation is one of the most important design decisions for testability.

---

# 5. Static Analysis

Static analysis should happen before runtime.

Typical checks include:

- Python syntax;
- unused imports;
- formatting;
- obvious code-quality problems;
- naming;
- complexity where appropriate;
- Airflow-specific linting where available/applicable.

A common tool is Ruff.

Conceptually:

```text
Source code
    ↓
Ruff / formatter / linter
    ↓
pass / fail
```

---

## 5.1 Why Static Analysis Matters

It catches problems before:

```text
CI
 ↓
DAG parsing
 ↓
scheduler
```

For example:

```python
from airflow import DAG

def unused_helper():
    ...
```

Static analysis may identify issues before the DAG reaches an Airflow environment.

---

## 5.2 Example CI Commands

A project may use commands such as:

```bash
ruff check .
ruff format --check .
```

The exact command set belongs to the repository's engineering standard.

The important principle is:

> Fast deterministic checks should fail early.

---

# 6. Import Tests for Every DAG

Import testing is mandatory for a production DAG repository.

The question is:

> **Can every expected DAG file be imported and produce a valid DAG object without raising an exception?**

---

## 6.1 Why Importability Matters

A DAG import can fail because of:

- syntax errors;
- missing packages;
- invalid Airflow imports;
- provider mismatches;
- missing environment configuration;
- top-level network calls;
- top-level database calls;
- expensive initialization;
- side effects during module import.

A scheduler cannot schedule a DAG it cannot load.

---

## 6.2 Import Lifecycle

Conceptually:

```text
DAG file
   ↓
Python import
   ↓
DAG object created
   ↓
No import exception
   ↓
DAG becomes discoverable
```

Failure:

```text
DAG file
   ↓
Python import
   ↓
Exception
   ↓
DAG unavailable
```

---

## 6.3 Simple Import Test

A simple test can import a known DAG module:

```python
def test_orders_dag_imports():
    import dags.orders_daily  # noqa: F401
```

If the import raises, the test fails.

---

## 6.4 Testing Every DAG

A repository can discover DAG modules and import each one.

A conceptual pattern:

```python
import importlib
from pathlib import Path

DAGS_DIR = Path("dags")


def test_all_dags_import():
    modules = [
        path.stem
        for path in DAGS_DIR.glob("*.py")
        if path.name != "__init__.py"
    ]

    for module_name in modules:
        importlib.import_module(f"dags.{module_name}")
```

For a real repository, module discovery should account for nested packages and the repository's actual Python package layout.

---

## 6.5 Import Tests Should Be Fast

Do not allow an import test to:

```text
call API
connect to production database
download file
run transformation
```

Import-time code should construct definitions, not perform runtime work.

---

# 7. Airflow 3.x Testing Awareness

This module is Airflow 3.x-focused.

Current Airflow 3.x APIs and Task SDK expectations should be the primary reference.

Two practical testing approaches required here are:

- `dag.test()`;
- `airflow dags test`.

Airflow 2-era examples may still appear in existing repositories, but they should be treated as legacy/compatibility awareness rather than the primary implementation model.

Always verify exact CLI/API behavior against the installed Airflow version.

---

# 8. Local Debugging with `dag.test()`

## 8.1 What `dag.test()` Is For

`dag.test()` is useful for local development and debugging of a DAG.

It allows an engineer to execute a DAG in a local/testing context and inspect task behavior without treating the local run as a full production deployment.

Conceptually:

```text
DAG definition
     ↓
dag.test()
     ↓
local execution
     ↓
inspect task behavior
```

---

## 8.2 Why Use It?

Use it to investigate:

- task failures;
- dependency behavior;
- template rendering;
- connection problems;
- unexpected task output;
- local execution context.

---

## 8.3 What `dag.test()` Does Not Replace

It does not replace:

- unit tests;
- structure tests;
- policy tests;
- integration tests;
- CI validation;
- deployment validation.

Think:

```text
dag.test()
=
local debugging tool
```

not:

```text
dag.test()
=
entire test strategy
```

---

## 8.4 Conceptual Example

A DAG can expose:

```python
from airflow.decorators import dag, task
from pendulum import datetime


@dag(
    dag_id="orders_daily",
    start_date=datetime(2026, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
)
def orders_daily():

    @task
    def extract():
        return ["order-1", "order-2"]

    @task
    def transform(rows):
        return [row.upper() for row in rows]

    transform(extract())


dag = orders_daily()

if __name__ == "__main__":
    dag.test()
```

The exact schedule/decorator parameters should be verified against the installed Airflow 3.x version.

---

## 8.5 Debugging Failures

### Missing Connection

```text
dag.test()
    ↓
task executes
    ↓
connection lookup fails
```

Ask:

- Is the connection configured?
- Is the test environment isolated?
- Should the dependency be mocked?
- Should this be an integration test instead?

### Invalid Template

```text
task starts
 ↓
template rendering fails
```

Ask:

- Which variable is invalid?
- Is the data interval what you expected?
- Is timezone handling correct?

### Unexpected Data

```text
task executes
 ↓
output incorrect
```

Separate:

```text
business logic defect
```

from:

```text
orchestration defect
```

---

# 9. `airflow dags test`

`airflow dags test` is a CLI-oriented way to test a DAG run from the command line.

Use it when you need a repeatable command-line workflow for inspecting DAG behavior.

Conceptually:

```text
airflow dags test
       ↓
DAG execution context
       ↓
task execution
       ↓
logs / result
```

The exact Airflow 3.x command syntax and behavior should be verified against the installed Airflow release.

---

## 9.1 `dag.test()` vs `airflow dags test`

| Concern | `dag.test()` | `airflow dags test` |
|---|---|---|
| Interface | Python | CLI |
| Local debugging | Strong | Strong |
| Automation | Easy from Python | Easy from shell/CI |
| DAG-specific execution | Yes | Yes |
| Unit testing replacement | No | No |
| Structure-test replacement | No | No |
| Integration-test replacement | No | No |

The important lesson is that both are execution/debugging tools inside a broader testing strategy.

---

# 10. Pytest Foundation

Only the pytest concepts needed for orchestration testing are required here.

---

## 10.1 Test Function

```python
def test_add_numbers():
    assert 2 + 2 == 4
```

---

## 10.2 Fixtures

Fixtures provide reusable test setup.

```python
import pytest


@pytest.fixture
def sample_order():
    return {
        "order_id": "o-1",
        "amount": "25.50",
    }
```

---

## 10.3 Parametrization

```python
import pytest


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("10", 10.0),
        ("25.5", 25.5),
        ("0", 0.0),
    ],
)
def test_amount_conversion(raw, expected):
    assert float(raw) == expected
```

---

## 10.4 Expected Exceptions

```python
import pytest


def validate_amount(value: float):
    if value < 0:
        raise ValueError("amount cannot be negative")


def test_negative_amount_rejected():
    with pytest.raises(ValueError):
        validate_amount(-1)
```

---

## 10.5 Mocking

Mock external systems when testing local logic.

```text
Unit test
   ↓
mock external dependency
   ↓
test local behavior
```

Do not mock everything indiscriminately. A mock can hide integration defects.

---

# 11. Unit Testing Task Logic as Plain Python

The key principle is:

> **BUSINESS LOGIC SHOULD BE TESTABLE WITHOUT AIRFLOW.**

---

## 11.1 Pure Function

```python
def normalize_order(order: dict) -> dict:
    return {
        "order_id": str(order["order_id"]),
        "amount": float(order["amount"]),
    }
```

Test:

```python
def test_normalize_order():
    raw = {
        "order_id": 123,
        "amount": "12.50",
    }

    result = normalize_order(raw)

    assert result == {
        "order_id": "123",
        "amount": 12.50,
    }
```

---

## 11.2 Edge Cases

Test:

```text
missing order_id
invalid amount
negative amount
empty payload
unexpected type
duplicate record
```

---

## 11.3 Dependency Injection

Instead of:

```python
def load_orders():
    connection = create_production_connection()
    ...
```

prefer:

```python
def load_orders(rows, connection):
    ...
```

Now tests can provide a controlled dependency.

---

## 11.4 Idempotency Tests

A useful test is:

```text
run once
 ↓
capture result

run twice
 ↓
capture result
```

Then verify that the second execution does not produce incorrect duplication.

For a partitioned write:

```text
write(partition)
write(partition)
```

should preserve the intended business result.

---

# 12. DAG Structure Tests

Structure tests validate the orchestration graph itself.

Test:

- DAG exists;
- expected task IDs;
- expected task count where appropriate;
- dependencies;
- upstream/downstream relationships;
- no unexpected tasks;
- task groups where relevant;
- quality-gate placement;
- publish dependency.

---

## 12.1 Example Structure

Expected:

```text
extract
   ↓
transform
   ↓
quality_check
   ↓
publish
```

A test can inspect task relationships.

Conceptually:

```python
def test_publish_depends_on_quality_check():
    dag = build_orders_dag()

    publish = dag.get_task("publish")
    quality = dag.get_task("quality_check")

    assert quality.task_id in publish.upstream_task_ids
```

Exact DAG construction depends on the project's Airflow version and architecture.

---

## 12.2 Why Structure Tests Matter

A DAG can:

- import;
- schedule;
- execute;

while still having an incorrect dependency graph.

Structure tests protect orchestration semantics.

---

# 13. Testing Expected Tasks

If the contract says:

```text
extract
transform
quality_check
publish
```

a structure test can verify the expected set.

```python
def test_expected_tasks():
    dag = build_orders_dag()

    assert set(dag.task_ids) == {
        "extract",
        "transform",
        "quality_check",
        "publish",
    }
```

Use exact task-count or task-set assertions when the graph is intentionally stable.

Avoid brittle assertions for workflows where task expansion is intentionally dynamic.

---

# 14. Dependency Tests

Dependency assertions are usually more valuable than merely counting tasks.

Example:

```python
def test_quality_gate_blocks_publish():
    dag = build_orders_dag()

    quality = dag.get_task("quality_check")
    publish = dag.get_task("publish")

    assert quality.task_id in publish.upstream_task_ids
```

Also verify important upstream relationships:

```text
extract → transform
transform → quality_check
quality_check → publish
```

---

# 15. Cycle Detection

A DAG must be acyclic.

Valid:

```text
A → B → C
```

Invalid:

```text
A → B → C
↑         ↓
└─────────┘
```

Airflow validates DAG structure and rejects invalid cycles.

Tests should still protect intended relationships.

The principle is:

> A structure test should make important workflow contracts explicit rather than relying only on framework validation.

---

# 16. Policy Tests

Functional tests ask:

> Does the task work?

Policy tests ask:

> Does the workflow follow organizational engineering rules?

---

## 16.1 Example Production Policy

Every production DAG must:

```text
- have an owner
- have tags
- define retry behavior
- define timeout behavior where required
- deliberately define catch-up
- use approved operators
- avoid unsafe dynamic configuration
```

These are not business-function tests.

They are governance/engineering-contract tests.

---

# 17. Owner and Tag Validation

Example policy:

```python
def test_dag_has_owner_and_tags():
    dag = build_orders_dag()

    assert dag.owner
    assert dag.tags
```

A stronger policy may require approved values:

```python
ALLOWED_OWNERS = {"data-platform", "analytics"}

def test_owner_is_approved():
    dag = build_orders_dag()

    assert dag.owner in ALLOWED_OWNERS
```

Do not make policies stricter than the actual organizational requirement.

---

# 18. Retries and Timeouts Policy Tests

Example:

```python
def test_extract_has_retry_policy():
    dag = build_orders_dag()

    extract = dag.get_task("extract")

    assert extract.retries >= 1
```

A more specific policy may assert an expected upper bound.

The purpose is to catch accidental removal of resilience configuration.

---

## 18.1 Configuration vs Behavior

A configuration test proves:

```text
retries = 3
```

It does **not** prove:

```text
retry actually behaves correctly
```

Behavioral tests must inject a failure and observe the resulting execution.

---

# 19. Timeout Policy Tests

Example:

```python
def test_external_task_has_timeout():
    dag = build_orders_dag()

    extract = dag.get_task("extract")

    assert extract.execution_timeout is not None
```

The exact timeout property/API can vary by operator/task implementation, so use the installed Airflow version's current interface.

---

# 20. Naive Start Dates

Avoid dynamic scheduling anchors such as:

```python
start_date=datetime.now()
```

Why?

Because the DAG's behavior can change depending on when the file is imported.

This can create:

- confusing scheduling;
- inconsistent historical behavior;
- testing difficulties;
- timezone problems.

---

## 20.1 Better Pattern

Use an explicit timezone-aware date:

```python
from pendulum import datetime

START_DATE = datetime(
    2026,
    1,
    1,
    tz="UTC",
)
```

Then:

```python
@dag(
    dag_id="orders_daily",
    start_date=START_DATE,
    schedule="@daily",
    catchup=False,
)
def orders_daily():
    ...
```

The exact scheduling API should be verified against the installed Airflow 3.x release.

---

# 21. Start-Date Policy Test

A policy test can inspect the DAG's start date and reject obviously dynamic patterns at code-review/static-analysis level.

A more useful runtime policy is:

```python
def test_start_date_is_explicit():
    dag = build_orders_dag()

    assert dag.start_date is not None
```

The strongest protection is architectural:

> Define explicit, deterministic scheduling configuration in source code.

---

# 22. Catch-Up Validation

Catch-up controls whether historical intervals are automatically scheduled when a DAG becomes active.

The key principle is:

> **Catch-up must be intentional.**

Do not assume:

```text
catchup=False
```

is universally correct.

---

## 22.1 Why Accidental Catch-Up Is Dangerous

Suppose:

```text
DAG start date
= 2025-01-01
```

but the DAG is deployed in:

```text
2026-10
```

If historical scheduling is enabled, the system may need to process a large historical range.

That may cause:

- API load;
- warehouse load;
- unexpected costs;
- downstream pressure;
- operational incidents.

---

## 22.2 Why Disabling Catch-Up Blindly Is Also Wrong

Some workflows intentionally require:

```text
historical partition processing
```

Therefore the policy should be:

```text
catch-up decision = deliberate
```

---

## 22.3 Catch-Up Policy Test

```python
def test_catchup_is_explicit():
    dag = build_orders_dag()

    assert dag.catchup in {True, False}
```

The test alone does not establish whether the chosen value is correct. The policy must encode the intended behavior.

---

# 23. Forbidden Operators

Organizations may prohibit:

- deprecated operators;
- unsafe operators;
- operators that bypass quality gates;
- operators that violate platform architecture;
- operators that embed secrets or unsafe execution.

A policy test can inspect task classes.

Conceptually:

```python
FORBIDDEN_TASK_TYPES = {
    "SomeForbiddenOperator",
}


def test_no_forbidden_tasks():
    dag = build_orders_dag()

    for task in dag.tasks:
        assert task.__class__.__name__ not in FORBIDDEN_TASK_TYPES
```

This is useful in CI because a developer receives fast feedback before deployment.

---

# 24. Parse-Time Budgets

## 24.1 What Is Parse Time?

DAG parsing is the process by which Airflow loads DAG definitions and builds the workflow objects used by the platform.

Top-level Python code runs during import/parsing.

---

## 24.2 Bad Pattern

```python
import requests

data = requests.get(
    "https://example.com/metadata"
).json()
```

This happens at import time.

The scheduler/DAG processor may now depend on:

- network availability;
- remote latency;
- remote authentication;
- external service health.

---

## 24.3 Better Pattern

Put runtime work inside a task:

```python
from airflow.decorators import task


@task
def fetch_metadata():
    import requests

    return requests.get(
        "https://example.com/metadata",
        timeout=30,
    ).json()
```

Now the network call belongs to task execution rather than DAG parsing.

---

## 24.4 Why Parse-Time Performance Matters

With many DAGs:

```text
100 DAGs
×
slow imports
```

can create scheduler/DAG-processing pressure.

Therefore:

```text
DAG definition
=
cheap to import
```

is an important production principle.

---

## 24.5 Parse-Time Testing

Possible safeguards include:

- import tests;
- timing imports in CI;
- static analysis;
- code review rules;
- preventing network/database calls at module scope.

A parse-time budget can be treated as an engineering contract.

---

# 25. Mocking Hooks and Connections

## 25.1 Why Mock External Systems?

Unit tests should be:

- fast;
- deterministic;
- isolated.

A unit test should not require:

```text
production PostgreSQL
production SFTP
production object storage
```

---

## 25.2 Hook Concept

A hook provides an abstraction for interacting with an external system.

Examples include:

- PostgreSQL;
- SFTP;
- cloud services;
- APIs.

The testing principle is:

```text
Unit test
    ↓
mock hook/connection
    ↓
test local behavior
```

---

## 25.3 Example

Suppose business logic uses a database hook:

```python
def count_orders(hook) -> int:
    result = hook.get_first(
        "SELECT COUNT(*) FROM orders"
    )
    return int(result[0])
```

Unit test:

```python
class FakeHook:
    def get_first(self, sql):
        assert "COUNT(*)" in sql
        return (42,)


def test_count_orders():
    assert count_orders(FakeHook()) == 42
```

This tests local behavior without connecting to a real database.

---

# 26. When Mocks Are Not Enough

A mock can prove:

```text
my code called get_first()
```

It cannot prove:

```text
PostgreSQL accepts this SQL
```

That requires an integration test.

This leads to:

```text
Unit test
    ↓
fast local behavior

Integration test
    ↓
real service semantics
```

Use both where justified.

---

# 27. Environment-Variable Test Connections

Test environments should use isolated configuration.

Conceptually:

```text
TEST_DATABASE_HOST
TEST_DATABASE_PORT
TEST_DATABASE_USER
TEST_DATABASE_PASSWORD
```

These should point to:

```text
local container
test service
ephemeral CI environment
```

not production.

---

## 27.1 Why This Matters

Never let:

```text
pytest
```

accidentally execute against:

```text
production database
```

Use:

- test-specific credentials;
- environment variables;
- secret management;
- isolated databases;
- local services.

---

# 28. Template Testing

Airflow templates often depend on runtime context.

Examples:

- `ds`;
- `data_interval_start`;
- `data_interval_end`;
- run IDs;
- partition/date parameters.

A DAG can import successfully while a template fails only during execution.

Therefore template behavior must be tested.

---

## 28.1 Common Template Failures

- wrong variable;
- wrong date format;
- timezone assumption;
- quoting error;
- invalid SQL;
- wrong partition;
- incorrect interval boundary.

---

## 28.2 Example Template

Conceptually:

```jinja2
SELECT *
FROM orders
WHERE order_date >= '{{ data_interval_start }}'
  AND order_date < '{{ data_interval_end }}'
```

Test the rendered output for a known interval.

Expected:

```text
start = 2026-10-01 00:00
end   = 2026-10-02 00:00
```

---

# 29. Data Interval Testing

Data intervals are part of correctness.

For a daily run:

```text
data_interval_start = 2026-10-01 00:00 UTC
data_interval_end   = 2026-10-02 00:00 UTC
```

The pipeline should process:

```text
[2026-10-01, 2026-10-02)
```

not:

```text
"whatever data exists right now"
```

---

## 29.1 Why This Matters

Without explicit interval semantics:

```text
daily run
```

can accidentally become:

```text
query current time
```

which breaks:

- backfills;
- reruns;
- historical reproducibility;
- partition correctness.

---

## 29.2 Data Interval Test

Test that:

```text
given interval
    ↓
expected partition
    ↓
expected SQL
    ↓
expected output
```

is deterministic.

---

# 30. Quality Gate Before Publish

A critical DAG contract is:

```text
extract
   ↓
transform
   ↓
quality_gate
   ↓
publish
```

Not:

```text
extract
   ↓
transform ─────────→ publish
      \
       → quality_gate
```

In the second graph, the quality gate does not actually protect publication.

---

## 30.1 Structure Test

```python
def test_quality_gate_blocks_publish():
    dag = build_orders_dag()

    quality = dag.get_task("quality_gate")
    publish = dag.get_task("publish")

    assert quality.task_id in publish.upstream_task_ids
```

---

## 30.2 Behavioral Test

Also test:

```text
quality passes
    ↓
publish executes
```

and:

```text
quality fails
    ↓
publish does not execute
```

The structure test proves dependency.

The behavioral test proves failure semantics.

Both are valuable.

---

# 31. Failure Behavior Testing

Do not only test happy paths.

Test:

- task failure;
- retry;
- timeout;
- upstream failure;
- skipped task;
- quality failure;
- external dependency failure;
- mapped partial failure;
- invalid parameters.

The key principle is:

> **Failure behavior is part of the DAG's contract.**

---

## 31.1 Example Failure Contract

```text
API returns 503
    ↓
task fails
    ↓
retry
    ↓
success
```

But:

```text
API returns 401
    ↓
do not blindly retry forever
    ↓
fail and alert
```

The tests should reflect this distinction.

---

# 32. Testing Idempotency and Safe Reruns

A production workflow must be safe to rerun.

Test:

```text
run once
```

and:

```text
run twice
```

Then compare the resulting business state.

---

## 32.1 Historical Interval Rerun

Example:

```text
orders/date=2026-10-01
```

Run it once.

Then run the same interval again.

Expected result:

```text
same correct partition
```

not:

```text
duplicate partition data
```

---

## 32.2 Retry After Partial Write

Critical scenario:

```text
database write
    ↓
commit succeeds
    ↓
task crashes
    ↓
retry
```

The test must prove that the second attempt does not corrupt data.

Useful mechanisms include:

- unique keys;
- merge/upsert;
- staging;
- transactional writes;
- deterministic batch IDs;
- atomic publish.

---

# 33. Integration Tests with Docker Services

Integration tests should use isolated services.

The roadmap calls for environments such as:

- Docker;
- PostgreSQL;
- MinIO;
- SFTP where applicable.

---

## 33.1 Unit Test vs Integration Test

Unit:

```text
task
 ↓
fake/mocked database
```

Integration:

```text
task
 ↓
real PostgreSQL container
```

---

## 33.2 Why Docker Helps

A local container can provide:

- reproducible environment;
- isolated state;
- deterministic setup;
- CI compatibility;
- realistic database semantics.

---

## 33.3 Integration Test Lifecycle

```text
Start service
    ↓
Create schema/data
    ↓
Run test
    ↓
Assert result
    ↓
Cleanup
```

---

## 33.4 PostgreSQL Integration Example

Conceptually:

```python
def test_load_orders_integration(postgres_service):
    connection = postgres_service.connection()

    connection.execute(
        """
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            amount NUMERIC NOT NULL
        )
        """
    )

    load_orders(
        connection,
        [
            {"order_id": "o-1", "amount": 10.0},
        ],
    )

    row = connection.execute(
        "SELECT order_id, amount FROM orders"
    ).fetchone()

    assert row == ("o-1", 10.0)
```

The fixture/service lifecycle belongs to the test infrastructure.

Do not point the test at production.

---

# 34. MinIO / Object Storage Integration

For object-store pipelines, test real object-storage semantics where useful:

```text
task
 ↓
MinIO container
 ↓
put object
 ↓
read object
 ↓
assert content
```

This can catch issues that a mock cannot:

- path semantics;
- serialization;
- credentials;
- object existence;
- content types;
- SDK behavior.

---

# 35. SFTP Integration

If the workflow depends on SFTP, an isolated test service can verify:

- connection;
- authentication;
- file listing;
- download;
- upload;
- permissions;
- failure behavior.

Do not assume that a mocked SFTP client proves actual protocol behavior.

---

# 36. Integration Test Strategy

Do not integrate everything.

Use integration tests for:

- SQL compatibility;
- database behavior;
- object storage behavior;
- serialization;
- connection configuration;
- external-system semantics.

Keep pure business logic in unit tests.

---

## 36.1 Trade-Off

```text
More mocks
   ↓
faster
but less realistic

More real services
   ↓
more realistic
but slower/more expensive
```

A balanced suite uses both.

---

# 37. Testing Historical Data Intervals

Suppose:

```text
orders_daily
```

processes:

```text
orders/date=2026-10-01
```

Test:

1. correct interval;
2. correct partition;
3. correct SQL;
4. correct output;
5. correct dependency chain.

Then test an older date:

```text
orders/date=2026-01-15
```

The workflow should still process the intended historical interval.

This is essential for backfills.

---

# 38. Testing Retries

There are two different questions.

### Configuration

```text
Are retries configured?
```

### Behavior

```text
Does the workflow actually recover correctly?
```

Test both.

---

## 38.1 Retry Behavior Test

Conceptually:

```text
Attempt 1 → injected transient failure
Attempt 2 → success
```

Assert:

- task eventually succeeds;
- attempt count is correct;
- no duplicate side effect;
- logs identify the failure/retry.

---

# 39. Testing Timeouts

Inject a slow operation:

```text
task
 ↓
sleep / slow external service
 ↓
timeout
```

Assert:

- task does not run indefinitely;
- timeout is recognized;
- retry behavior is correct if configured;
- external side effects remain safe.

---

# 40. Testing Mapped or Dynamic Work

For a workflow processing:

```text
source_1
source_2
source_3
...
source_N
```

test:

- all expected inputs are represented;
- one failed input does not hide other results;
- retries are applied appropriately;
- successful items remain successful;
- recovery does not duplicate successful work.

The exact mechanics differ by orchestrator, but the testing principle is the same.

---

# 41. Dagster Asset Testing

The roadmap requires awareness of testing Dagster assets.

Keep this scoped to testing rather than turning it into a complete Dagster tutorial.

---

## 41.1 Asset Logic

Asset business logic should be independently testable.

Conceptually:

```text
asset logic
   ↓
ordinary Python test
```

---

## 41.2 In-Process Asset Testing

An asset can be executed in a controlled in-process test context.

Test:

- expected output;
- dependencies;
- metadata;
- partition behavior where relevant;
- asset checks.

---

## 41.3 Asset Dependency Validation

For:

```text
raw_orders
    ↓
clean_orders
    ↓
daily_orders
```

tests should protect the intended dependency relationship.

---

## 41.4 Asset Checks

If a critical asset check must pass before downstream consumption, test:

```text
valid asset
   ↓
check passes
```

and:

```text
invalid asset
   ↓
check fails
```

The exact APIs should follow the installed/current Dagster version.

---

# 42. Prefect Flow Testing

Topic 10 covers Prefect in depth; here the focus is only testing.

The same principle applies:

> Keep business logic testable as ordinary Python.

---

## 42.1 Test Task Logic

```python
def normalize_order(order):
    ...
```

Test it directly.

---

## 42.2 Test Flow Parameters

Test:

```text
valid source
valid date
```

and:

```text
invalid source
invalid date
```

---

## 42.3 Test Failure Behavior

Inject:

```text
temporary API failure
```

and verify the flow/task's configured retry behavior.

---

## 42.4 Test Orchestration Boundaries

Verify:

- expected tasks;
- expected dependencies;
- parameter behavior;
- failure semantics;
- concurrency behavior where relevant.

Do not duplicate the complete Prefect API material from Topic 10.

---

# 43. CI Testing Pipeline

A production CI sequence can look like:

```text
Pull Request
      ↓
Ruff / Static Analysis
      ↓
Python Unit Tests
      ↓
DAG Import Tests
      ↓
DAG Structure Tests
      ↓
Policy Tests
      ↓
Template / Data Interval Tests
      ↓
Integration Tests
      ↓
Build / Deployment Validation
```

---

## 43.1 On Every Pull Request

Fast checks:

- Ruff;
- unit tests;
- import tests;
- structure tests;
- policy tests;
- template tests.

---

## 43.2 On Merge

Potentially add:

- integration tests;
- build validation;
- environment validation.

---

## 43.3 Before Deployment

Run:

- full validation;
- integration tests;
- package/build checks;
- expected DAG inventory checks.

---

## 43.4 After Deployment

Validate:

- expected DAGs are loaded;
- no required DAG disappeared;
- scheduler/DAG processor sees the new version;
- deployment configuration is correct.

---

# 44. CI Failure Examples

## Example 1 — Import Failure

```text
PR #42
   ↓
Ruff passes
   ↓
Unit tests pass
   ↓
Import test fails
   ↓
Deployment blocked
```

This is valuable because the DAG would not be safely deployable.

---

## Example 2 — Dependency Regression

```text
Structure test
   ↓
publish no longer depends on quality_gate
   ↓
CI fails
   ↓
deployment blocked
```

The test caught a correctness regression before production.

---

## Example 3 — Policy Regression

```text
DAG owner removed
   ↓
policy test fails
   ↓
developer fixes metadata
```

---

# 45. Deployment Validation

CI proves that the code package is acceptable.

It does not prove that production actually loaded the intended workflows.

The deployment path is:

```text
Git commit
   ↓
CI
   ↓
Build/deploy
   ↓
DAG processor
   ↓
Scheduler
   ↓
DAG appears
```

---

## 45.1 What Can Go Wrong?

- file not deployed;
- import failure;
- missing dependency;
- invalid configuration;
- provider mismatch;
- renamed DAG;
- accidentally removed DAG;
- incorrect deployment package.

---

# 46. Detecting Disappeared DAGs

A missing DAG can be more dangerous than an obvious deployment failure.

Suppose expected:

```text
orders_daily
customers_daily
inventory_daily
payments_daily
```

After deployment, loaded:

```text
orders_daily
customers_daily
inventory_daily
```

Then:

```text
payments_daily
```

has disappeared.

If nobody checks the inventory, the deployment may look healthy.

---

## 46.1 Inventory Comparison

Before deployment:

```text
EXPECTED_DAG_IDS
```

After deployment:

```text
LOADED_DAG_IDS
```

Compare:

```python
missing = expected_ids - loaded_ids

assert not missing, (
    f"Missing DAGs after deployment: {missing}"
)
```

The exact retrieval mechanism depends on the production Airflow environment.

---

# 47. DAG Inventory / Regression Testing

A production platform can maintain an expected inventory containing:

- DAG ID;
- owner;
- tags;
- schedule;
- criticality;
- key dependencies.

Test:

```text
required DAG exists
owner correct
tags present
schedule correct
```

Do not make the inventory unnecessarily rigid.

If every implementation detail becomes a snapshot, ordinary refactoring can produce noisy failures.

---

# 48. Testing the Orchestration Contract

An orchestration contract describes what the workflow promises.

Example:

```text
DAG: orders_daily

Must:
- run daily
- process one data interval
- retry transient failures
- timeout hung work
- execute quality checks
- block publishing on critical quality failure
- produce expected output
```

Each statement should map to one or more tests.

---

## 48.1 Contract-to-Test Mapping

| Contract | Test |
|---|---|
| Runs daily | Schedule/policy test |
| One interval | Data-interval test |
| Retries transient failures | Behavioral retry test |
| Timeout | Timeout test |
| Quality checks execute | Structure test |
| Quality blocks publishing | Dependency + failure test |
| Correct output | Unit/integration/data test |

This is much stronger than measuring coverage alone.

---

# 49. Quality Gates as Contracts

Suppose:

```text
quality_gate
```

checks:

```text
row_count > 0
null_rate < 1%
duplicate_rate = 0
```

A production test should prove:

```text
quality passes
    ↓
publish allowed
```

and:

```text
quality fails
    ↓
publish blocked
```

The second test is especially important.

A quality check that runs but cannot prevent publication is not a reliable quality gate.

---

# 50. Testing Failure Injection Lab

Deliberately introduce the following defects:

1. Broken import
2. Missing dependency
3. Incorrect task dependency
4. Missing quality gate
5. Forbidden operator
6. Missing retry
7. Missing timeout
8. Invalid template
9. Wrong data interval
10. Database failure
11. Object-storage failure
12. Task logic failure
13. Disappeared DAG
14. Deployment mismatch

For every defect:

```text
Introduce defect
      ↓
Run appropriate test
      ↓
Observe expected failure
      ↓
Explain why that test layer caught it
      ↓
Fix defect
      ↓
Rerun test
      ↓
Confirm validation
```

---

# 51. Failure Injection Matrix

| Defect | Primary test layer |
|---|---|
| Syntax error | Static/import |
| Missing package | Import/integration environment |
| Wrong dependency | Structure |
| Missing quality gate | Structure/behavior |
| Forbidden operator | Policy |
| Missing retry | Policy |
| Retry doesn't recover | Behavioral |
| Missing timeout | Policy/behavior |
| Invalid template | Template |
| Wrong interval | Data-interval |
| SQL incompatibility | Integration |
| Business transformation bug | Unit |
| Missing DAG | Deployment |
| Environment mismatch | Deployment/integration |

---

# 52. Complete Testing Lab — `orders_daily`

Build the conceptual pipeline:

```text
ingest
   ↓
bronze
   ↓
silver
   ↓
quality_gate
   ↓
gold
   ↓
publish
```

The testing strategy should contain eight layers.

---

## Layer 1 — Lint / Static Analysis

Validate:

```text
Ruff
formatting
syntax
```

---

## Layer 2 — Import Test

Prove:

```text
orders_daily imports successfully
```

---

## Layer 3 — Unit Tests

Test:

```text
parsing
normalization
business rules
validation
```

---

## Layer 4 — Structure Tests

Prove:

```text
bronze → silver
silver → quality_gate
quality_gate → gold
gold → publish
```

---

## Layer 5 — Policy Tests

Prove:

```text
owner
tags
retry
timeout
catch-up
approved operators
```

---

## Layer 6 — Template / Interval Tests

Prove:

```text
2026-10-01
```

produces the intended:

```text
[2026-10-01, 2026-10-02)
```

and correct partition/SQL.

---

## Layer 7 — Integration Tests

Use isolated:

```text
PostgreSQL
MinIO
SFTP if required
```

---

## Layer 8 — Deployment Validation

Prove:

```text
DAG exists
DAG loads
expected inventory remains intact
```

---

# 53. Test Directory Design

A production-oriented repository might conceptually use:

```text
tests/
├── unit/
├── dags/
├── policies/
├── integration/
├── templates/
└── deployment/
```

This is a conceptual design only.

It is **not** a request to create these directories as part of this topic file.

---

## 53.1 `unit/`

Pure business logic.

---

## 53.2 `dags/`

Import and structure tests.

---

## 53.3 `policies/`

Owners, tags, retries, timeouts, operators, catch-up.

---

## 53.4 `integration/`

Real isolated services.

---

## 53.5 `templates/`

Template and data-interval validation.

---

## 53.6 `deployment/`

Loaded-DAG and deployment validation.

---

# 54. Common Testing Anti-Patterns

## 54.1 Only Testing That the DAG Imports

**BAD APPROACH**

```text
import succeeds
→ therefore production is safe
```

**WHY IT FAILS**

It does not prove dependencies, policies, business logic, templates, integrations, or deployment correctness.

**BETTER APPROACH**

Use layered testing.

---

## 54.2 Only Testing Happy Paths

**BAD**

```text
task succeeds
```

**WHY IT FAILS**

Production failures are often the important part of orchestration behavior.

**BETTER**

Test:

```text
success
failure
retry
timeout
partial failure
```

---

## 54.3 Testing Everything Through Airflow

**BAD**

```text
every unit test
→ full Airflow environment
```

**WHY IT FAILS**

Slow, expensive, difficult to debug.

**BETTER**

Keep business logic as ordinary Python.

---

## 54.4 Mocking Everything

**BAD**

```text
mock database
mock storage
mock SQL
mock SDK
mock everything
```

**WHY IT FAILS**

You can accidentally prove that your mocks behave correctly rather than proving that the real systems work.

**BETTER**

Combine unit tests with targeted integration tests.

---

## 54.5 No Integration Tests

**BAD**

```text
all tests pass
```

but:

```text
real PostgreSQL rejects SQL
```

**BETTER**

Use integration tests for important external-system semantics.

---

## 54.6 Integration Testing Everything

**BAD**

Every tiny function requires:

```text
Docker
database
network
Airflow
```

**WHY IT FAILS**

Very slow feedback and high maintenance.

**BETTER**

Use the lowest-cost test layer that can prove the contract.

---

## 54.7 Testing Implementation Instead of Contracts

**BAD**

Asserting dozens of internal implementation details.

**WHY IT FAILS**

Small refactoring breaks tests even when behavior remains correct.

**BETTER**

Test important external behavior and orchestration contracts.

---

## 54.8 Excessive Snapshot Testing

Snapshots can become:

```text
large
brittle
difficult to review
```

Use semantic assertions for critical workflow properties.

---

## 54.9 Brittle Task-Count Assertions

A test such as:

```python
assert len(dag.tasks) == 27
```

may be weak if dynamic task expansion or legitimate refactoring is expected.

Prefer:

```python
assert required_task_id in dag.task_ids
```

and dependency assertions for important contracts.

---

## 54.10 Ignoring Templates

A DAG can import while a template fails at runtime.

Always test important templates.

---

## 54.11 Ignoring Data Intervals

A workflow that works for "today" may fail for historical partitions.

Test explicit intervals.

---

## 54.12 No Policy Validation

Without policy tests, developers can accidentally remove:

- retries;
- owners;
- tags;
- timeouts;
- required quality gates.

---

## 54.13 No Deployment Validation

CI can pass while the deployed environment is missing a DAG.

Validate after deployment.

---

## 54.14 No Idempotency Tests

A workflow may succeed once and corrupt data on retry.

Test repeated execution.

---

## 54.15 Testing Production Services from CI

Never use production systems as an ordinary CI test environment.

Use isolated services.

---

## 54.16 Using Production Credentials

Never put production credentials in test configuration.

Use:

```text
test secrets
test accounts
local services
ephemeral environments
```

---

## 54.17 Relying Entirely on Manual UI Testing

The UI is useful for operational investigation.

It is not a substitute for automated validation.

---

# 55. Test Selection Decision Tree

Use this mental model:

```text
What are you testing?
        │
        ├── Pure business logic?
        │       → Unit test
        │
        ├── DAG dependency?
        │       → Structure test
        │
        ├── DAG configuration?
        │       → Policy test
        │
        ├── Template/data interval?
        │       → Rendering/context test
        │
        ├── Database/object storage behavior?
        │       → Integration test
        │
        ├── Failure/retry/idempotency?
        │       → Behavioral test
        │
        └── Deployment correctness?
                → Deployment validation
```

---

# 56. Testing Trade-Offs

There is no universal test strategy.

---

## 56.1 Speed vs Realism

```text
Mock
  ↓
fast

Real service
  ↓
realistic
```

Use both where justified.

---

## 56.2 Unit vs Integration

Unit tests answer:

> "Is this logic correct?"

Integration tests answer:

> "Does this logic work correctly with the real dependency?"

---

## 56.3 Coverage vs Maintenance

More tests are not automatically better.

Prefer tests that protect important contracts.

---

## 56.4 Strict Policy vs Flexibility

A policy should be:

```text
strict enough to prevent real operational risk
```

but not:

```text
so rigid that harmless refactoring becomes impossible
```

---

## 56.5 Snapshot vs Semantic Assertions

Prefer:

```python
assert publish.task_id in dag.task_ids
```

and:

```python
assert quality.task_id in publish.upstream_task_ids
```

over giant serialized snapshots when the semantic relationship is what matters.

---

## 56.6 Local vs CI vs Deployment Testing

```text
Local
→ fast debugging

CI
→ repeatable validation

Deployment
→ production reality check
```

All three have different purposes.

---

# 57. Code Review Exercises

## Exercise 1 — Only Checks DAG Existence

### Bad Code

```python
def test_dag_exists():
    dag = build_orders_dag()
    assert dag is not None
```

### Problem

It proves almost nothing about workflow correctness.

### Better

```python
def test_expected_tasks_exist():
    dag = build_orders_dag()

    assert {
        "extract",
        "transform",
        "quality_gate",
        "publish",
    } <= set(dag.task_ids)
```

Then test important dependencies.

---

## Exercise 2 — Task Count Only

### Bad

```python
assert len(dag.tasks) == 4
```

### Problem

The four tasks could be completely misconnected.

### Better

```python
assert (
    "quality_gate"
    in dag.get_task("publish").upstream_task_ids
)
```

---

## Exercise 3 — Production Database

### Bad

```python
def test_load():
    connection = connect_to_production()
    ...
```

### Problem

A test can modify production data.

### Better

Use an isolated test database.

---

## Exercise 4 — Over-Mocking

### Bad

```python
mock_database.execute.return_value = True
```

for every database test.

### Problem

The test may never detect invalid SQL.

### Better

Use a real PostgreSQL integration test for important SQL semantics.

---

## Exercise 5 — Current Datetime

### Bad

```python
def test_partition():
    expected = datetime.now()
```

### Problem

The test is nondeterministic.

### Better

Use a fixed interval:

```text
2026-10-01 → 2026-10-02
```

---

## Exercise 6 — Missing Quality Gate

### Bad Graph

```text
transform → publish
    \
     → quality_gate
```

### Problem

Quality does not block publication.

### Better

```text
transform
   ↓
quality_gate
   ↓
publish
```

---

## Exercise 7 — Missing Retry Policy

### Bad

```python
def test_extract():
    ...
```

with no policy validation.

### Better

Explicitly validate required retry configuration and separately test retry behavior.

---

# 58. Architecture Questions

## 1. How would you test 100 Airflow DAGs?

Use a layered CI strategy:

```text
Ruff
 ↓
import every DAG
 ↓
structure tests
 ↓
policy tests
 ↓
template/interval tests
 ↓
targeted integration tests
```

Do not execute every DAG end-to-end on every pull request.

---

## 2. How would you prevent a bad DAG from reaching production?

Use CI gates:

```text
static
+
import
+
unit
+
structure
+
policy
+
template
+
integration
```

and block deployment on failure.

---

## 3. How would you detect a DAG disappearing after deployment?

Maintain an expected DAG inventory and compare it with the deployed environment's loaded DAG IDs.

---

## 4. How would you test quality gates?

Test both:

```text
quality passes → publish allowed
```

and:

```text
quality fails → publish blocked
```

---

## 5. How would you test backfill correctness?

Use fixed historical data intervals and assert:

- correct partition;
- correct SQL;
- correct output;
- deterministic rerun;
- no duplicate side effects.

---

## 6. How would you test idempotency?

Run the same logical operation multiple times and compare the resulting business state.

Also inject failure after a partial external side effect.

---

## 7. How would you test external database failures?

Use:

- unit tests with mocks for local failure handling;
- integration tests with an isolated database;
- controlled connection failures where practical.

---

## 8. How would you balance mocks and integration tests?

Use mocks for fast deterministic unit tests and real services for a targeted set of integration contracts.

---

## 9. How would you design CI for Airflow?

Use:

```text
static
→ unit
→ import
→ structure
→ policy
→ template/interval
→ integration
→ deployment validation
```

with expensive tests placed later in the pipeline.

---

## 10. How would you test Dagster assets?

Test asset logic independently, execute assets in a controlled in-process context where appropriate, validate dependencies, partitions, and asset checks.

---

## 11. How would you test Prefect flows?

Test business logic as ordinary Python, then test flow parameters, task boundaries, failure behavior, and orchestration semantics at appropriate integration levels.

---

## 12. How would you validate production deployment?

Verify:

- expected DAGs exist;
- imports succeed;
- scheduler/DAG processor sees the intended version;
- configuration is correct;
- no required DAG disappeared.

---

## 13. How would you detect slow DAG parsing?

Measure import/parse duration in CI and investigate:

- network calls;
- database calls;
- large computations;
- expensive module initialization.

---

## 14. How would you test hundreds of mapped tasks?

Test the mapping contract with representative small datasets, include partial failure scenarios, and use integration/end-to-end tests only where they prove behavior that lower layers cannot.

---

## 15. How would you prevent policy violations?

Encode organizational rules as automated policy tests and run them in CI.

---

# 59. Practical Exercises

## Beginner

### Exercise 1 — Basic Import Test

Write a test that imports one DAG module.

---

### Exercise 2 — Plain Python Task Test

Write:

```python
def normalize_order(...):
    ...
```

and test it independently from Airflow.

---

### Exercise 3 — Expected Task IDs

Verify that the required tasks exist.

---

## Intermediate

### Exercise 4 — Dependencies

Test:

```text
extract → transform → quality → publish
```

---

### Exercise 5 — Retry Policy

Verify that an external task has the required retry configuration.

---

### Exercise 6 — Timeout Policy

Verify that the external task has a timeout.

---

### Exercise 7 — Owner and Tags

Write policy tests.

---

### Exercise 8 — Catch-Up

Verify that catch-up behavior is explicitly configured.

---

### Exercise 9 — Templates

Test a daily data interval template.

---

### Exercise 10 — Historical Interval

Test:

```text
2026-01-15 → 2026-01-16
```

and verify the correct partition.

---

## Advanced

### Exercise 11 — Mock a Database Hook

Test database-related task logic without a real database.

---

### Exercise 12 — PostgreSQL Integration

Run the same logic against an isolated PostgreSQL service.

---

### Exercise 13 — MinIO Integration

Test object creation and retrieval.

---

### Exercise 14 — Failure Behavior

Inject a transient failure and verify retry behavior.

---

### Exercise 15 — Idempotency

Execute the same write twice and verify that business data remains correct.

---

### Exercise 16 — Quality Gate

Prove that:

```text
quality failure
```

prevents:

```text
publish
```

---

## Production Exercise

Build a complete CI validation suite for:

```text
orders_daily
```

with:

- static analysis;
- import tests;
- unit tests;
- structure tests;
- policy tests;
- template tests;
- interval tests;
- integration tests;
- failure tests;
- idempotency tests;
- deployment validation.

For every test, document:

```text
What does it prove?
What failure does it catch?
Why is this test at this layer?
```

---

# 60. Final Capstone — Production Orchestration Validation Platform

## 60.1 Scenario

A Data Engineering platform contains:

- multiple ingestion DAGs;
- transformation DAGs;
- quality gates;
- database loads;
- object storage;
- Airflow;
- Dagster assets;
- Prefect flows.

You are responsible for designing the validation system.

---

## 60.2 Required Validation

The platform must detect:

```text
broken imports
dependency mistakes
policy violations
business-logic bugs
template errors
data-interval errors
external integration failures
failure/retry problems
idempotency defects
deployment errors
missing DAGs
```

---

## 60.3 Target Architecture

```text
                 Git Pull Request
                        │
                        ▼
                 Static Analysis
                        │
                        ▼
                  Unit Tests
                        │
                        ▼
                 Import Tests
                        │
                        ▼
              Structure / DAG Tests
                        │
                        ▼
                Policy / Contract
                        │
                        ▼
             Template / Interval Tests
                        │
                        ▼
              Integration Test Layer
                        │
                        ▼
                 Build / Package
                        │
                        ▼
                  Deployment
                        │
                        ▼
             Loaded DAG Inventory
                        │
                        ▼
             Production Validation
```

---

## 60.4 Required Capstone Demonstration

Demonstrate all of the following:

1. Break a DAG import.
2. Show CI failure.
3. Fix the import.
4. Break a dependency.
5. Show structure-test failure.
6. Remove a retry policy.
7. Show policy-test failure.
8. Break a template.
9. Show template-test failure.
10. Change a data interval.
11. Show interval-test failure.
12. Break a database integration.
13. Show integration-test failure.
14. Create an idempotency defect.
15. Show duplicate-write test failure.
16. Remove a deployed DAG.
17. Show deployment-inventory failure.
18. Restore the DAG.
19. Run the complete suite.
20. Explain why each layer exists.

The goal is not merely to make all tests green.

The goal is to understand **which class of failure each test is designed to detect**.

---

# 61. Connection to Previous Modules

## Module 2.9 — Data Ingestion and Extraction Patterns

Ingestion tasks interact with:

- APIs;
- files;
- databases;
- object storage.

Testing must therefore validate:

```text
ingestion logic
+
external integration
+
failure behavior
+
idempotency
```

---

## Module 2.10 — Concurrency and Parallelism in Practice

Concurrency creates additional test requirements:

- partial failures;
- race conditions;
- resource limits;
- mapped work;
- bounded concurrency.

A workflow that works sequentially may fail under concurrent execution.

---

## Module 2.11 — Data Validation, Contracts and Quality

Quality gates must be tested as workflow contracts.

```text
transform
   ↓
quality
   ↓
publish
```

Testing must prove that quality failure prevents unsafe publication.

---

## Module 2.12 — Transformation Patterns and Pipeline Design

Transformation design introduces:

- idempotency;
- reruns;
- backfills;
- late data;
- deterministic partitions.

Testing validates that orchestration preserves those guarantees.

---

## Module 2.13 — Orchestration and Workflow Management

Testing is the quality layer over all orchestration mechanisms:

```text
Ingestion
   ↓
Transformation
   ↓
Quality
   ↓
Orchestration
   ↓
Testing / Validation
   ↓
CI / Deployment
```

---

# 62. Connection to the Rest of Module 2.13

## Topic 01 — DAGs, Dependencies, and Scheduling Concepts

Topic 11 validates the dependency and scheduling concepts introduced earlier.

---

## Topic 02 — Limits of Cron

Testing helps determine whether an orchestration workflow has acquired enough complexity to require stronger operational guarantees.

---

## Topic 03 — Apache Airflow Architecture

Import, structure, policy, and deployment tests validate code against the Airflow runtime architecture.

---

## Topic 04 — Airflow DAGs, Operators, and TaskFlow API

Structure tests validate the actual task graph created by these constructs.

---

## Topic 05 — Connections, Variables, Hooks, and XComs

Mocking and integration tests validate external integrations and configuration behavior.

---

## Topic 06 — Sensors, Deferrable Operators, and Data-Aware Scheduling

Testing must validate timing, readiness, and scheduling behavior where those features are used.

---

## Topic 07 — Task Retries, Deadlines/SLAs, and Failure Callbacks

Topic 11 turns retry and failure concepts into testable contracts.

---

## Topic 08 — Backfills, Catch-Up, and Partitioned Runs

Data-interval and idempotency tests protect historical processing.

---

## Topic 09 — Dagster Software-Defined Assets

Asset testing validates logic, dependencies, partitions, and asset checks.

---

## Topic 10 — Prefect Flows and Tasks

Flow testing follows the same layered principle:

```text
business logic
 ↓
flow/task behavior
 ↓
integration
 ↓
deployment
```

---

## Topic 11 — Testing and Validating DAGs

This topic is the quality gate for the orchestration code developed throughout Topics 01–10.

---

# 63. Learning Checkpoints

After each major section, ask yourself:

### Checkpoint 1

**Can you explain why import tests are necessary?**

You should be able to explain that a scheduler cannot operate a DAG it cannot load.

---

### Checkpoint 2

**Can you distinguish unit testing from DAG structure testing?**

Unit testing validates logic.

Structure testing validates orchestration relationships.

---

### Checkpoint 3

**Can you explain why `dag.test()` does not replace unit tests?**

Because local DAG execution is not the same as testing pure business logic independently.

---

### Checkpoint 4

**Can you explain why integration tests should use isolated services?**

Because real service semantics matter, but production systems must not be used as ordinary test environments.

---

### Checkpoint 5

**Can you explain how a quality gate can accidentally be bypassed?**

If `publish` does not depend on `quality_gate`, the quality check cannot reliably block publication.

---

### Checkpoint 6

**Can you explain how deployment validation detects a missing DAG?**

Compare the expected DAG inventory with the loaded DAG inventory after deployment.

---

# 64. Interview Preparation — Exactly 40 Questions

## Basic — 10 Questions

### 1. QUESTION
What is the difference between testing that a DAG parses and testing that a DAG is correct?

**ANSWER:** Parsing proves that Airflow can load the DAG definition; correctness requires additional tests for structure, policy, logic, integrations, failure behavior, and deployment.

**EXPLANATION:** A DAG can import successfully while having a wrong dependency graph, invalid template, unsafe retry policy, incorrect data interval, or broken external integration.

---

### 2. QUESTION
Why are import tests important?

**ANSWER:** They verify that DAG modules can be loaded without import errors.

**EXPLANATION:** A broken import can prevent the scheduler from discovering or operating the DAG.

---

### 3. QUESTION
What is `dag.test()` used for?

**ANSWER:** It is a local DAG execution/debugging mechanism.

**EXPLANATION:** It helps developers inspect task execution and failures without treating it as a replacement for unit, structure, integration, or deployment tests.

---

### 4. QUESTION
What is `airflow dags test`?

**ANSWER:** It is a CLI-oriented mechanism for testing a DAG run.

**EXPLANATION:** It provides a repeatable command-line workflow for DAG execution/testing and should be used alongside other validation layers.

---

### 5. QUESTION
Why should business logic be tested as plain Python?

**ANSWER:** It makes tests faster, simpler, and independent of orchestration infrastructure.

**EXPLANATION:** Pure functions can be tested directly without starting Airflow or connecting to external systems.

---

### 6. QUESTION
What is a DAG structure test?

**ANSWER:** A test that verifies tasks and their dependencies match the intended workflow contract.

**EXPLANATION:** It can prove that critical tasks exist and that required upstream/downstream relationships are correct.

---

### 7. QUESTION
What is a policy test?

**ANSWER:** A test that verifies an orchestration workflow follows engineering or organizational rules.

**EXPLANATION:** Examples include owner, tags, retries, timeouts, catch-up configuration, and forbidden operators.

---

### 8. QUESTION
Why should external services be mocked in unit tests?

**ANSWER:** To keep unit tests fast, deterministic, and isolated.

**EXPLANATION:** Real services belong in targeted integration tests.

---

### 9. QUESTION
What is an integration test?

**ANSWER:** A test that validates behavior against a real isolated external dependency.

**EXPLANATION:** PostgreSQL or object storage running in a test environment can expose defects that mocks cannot.

---

### 10. QUESTION
Why must data intervals be tested?

**ANSWER:** Because the interval determines which logical data a scheduled or historical run should process.

**EXPLANATION:** Incorrect interval handling can break daily processing, backfills, and deterministic reruns.

---

## Moderate — 10 Questions

### 11. QUESTION
Why is testing task count alone insufficient?

**ANSWER:** Task count does not prove that dependencies are correct.

**EXPLANATION:** Four tasks can exist while `publish` bypasses the quality gate.

---

### 12. QUESTION
Why should dynamic start dates such as `datetime.now()` be avoided in DAG scheduling configuration?

**ANSWER:** They make scheduling behavior nondeterministic.

**EXPLANATION:** The DAG's temporal behavior can change depending on when it is parsed or deployed.

---

### 13. QUESTION
Why should catch-up configuration be deliberate?

**ANSWER:** Because automatic historical scheduling can create unexpected workload, but disabling it blindly can prevent required historical processing.

**EXPLANATION:** The correct value depends on the workflow's business and operational requirements.

---

### 14. QUESTION
What is the difference between testing retry configuration and testing retry behavior?

**ANSWER:** Configuration testing verifies the policy exists; behavioral testing proves the workflow actually recovers correctly after failure.

**EXPLANATION:** A task can have `retries=3` while still producing duplicate side effects if its write is not idempotent.

---

### 15. QUESTION
Why are network calls at DAG import time dangerous?

**ANSWER:** They make DAG parsing dependent on external service availability and latency.

**EXPLANATION:** Slow or failed external services can interfere with DAG processing and scheduler operations.

---

### 16. QUESTION
When is a mock insufficient?

**ANSWER:** When correctness depends on real external-system semantics.

**EXPLANATION:** A mocked database cannot prove that SQL is valid for the actual database engine.

---

### 17. QUESTION
What should a quality-gate structure test prove?

**ANSWER:** That publishing depends on the quality gate.

**EXPLANATION:** The dependency must make the quality check a true prerequisite for publication.

---

### 18. QUESTION
Why test both current and historical data intervals?

**ANSWER:** To prove that the workflow is deterministic across normal runs and backfills.

**EXPLANATION:** A pipeline can work for today's data while failing for historical partitions.

---

### 19. QUESTION
Why are deployment tests necessary if CI already passed?

**ANSWER:** CI validates the source/build; deployment validation verifies what the production orchestration environment actually loaded.

**EXPLANATION:** Packaging, configuration, dependencies, or deployment errors can cause DAGs to disappear after successful CI.

---

### 20. QUESTION
Why should integration tests use isolated databases?

**ANSWER:** To obtain realistic database behavior without risking production data.

**EXPLANATION:** Containers or ephemeral test services provide controlled integration environments.

---

## Hard — 10 Questions

### 21. QUESTION
A DAG imports successfully but publishing can bypass the quality gate. Which test should catch this?

**ANSWER:** A DAG structure/dependency test.

**EXPLANATION:** The test should assert that `quality_gate` is an upstream dependency of `publish`.

---

### 22. QUESTION
A task has three retries, but the first attempt commits data and crashes before completion. What should testing verify?

**ANSWER:** That retrying the task does not create duplicate or otherwise incorrect business data.

**EXPLANATION:** Retry configuration alone does not provide idempotency. A failure after a side effect is a critical test case.

---

### 23. QUESTION
How would you test a DAG repository containing 100 DAGs?

**ANSWER:** Combine static analysis, import tests for all DAGs, targeted structure/policy tests, unit tests, integration tests, and deployment validation.

**EXPLANATION:** Testing every DAG end-to-end on every change would be expensive and slow. Layered validation provides faster feedback.

---

### 24. QUESTION
How would you detect a DAG that disappeared after deployment?

**ANSWER:** Compare an expected DAG inventory with the DAG IDs loaded in the deployed environment.

**EXPLANATION:** A missing DAG may otherwise go unnoticed because deployment infrastructure can remain healthy while one workflow silently disappears.

---

### 25. QUESTION
How would you test a Jinja template using `data_interval_start` and `data_interval_end`?

**ANSWER:** Render the template for a fixed known interval and assert that the resulting SQL/path/partition is correct.

**EXPLANATION:** This catches variable, formatting, timezone, and boundary errors.

---

### 26. QUESTION
How would you test idempotency of a partitioned load?

**ANSWER:** Execute the same logical partition multiple times, including a simulated retry after a partial write, and verify that the final business state is correct without duplicates.

**EXPLANATION:** This tests the actual failure mode rather than merely checking a configuration value.

---

### 27. QUESTION
Why is a test using `datetime.now()` often a poor data-interval test?

**ANSWER:** It is nondeterministic.

**EXPLANATION:** The expected result changes over time, making failures difficult to reproduce and potentially hiding historical-processing defects.

---

### 28. QUESTION
How would you test a database hook without requiring PostgreSQL?

**ANSWER:** Mock or replace the hook with a controlled fake in a unit test.

**EXPLANATION:** This validates local task behavior. A separate integration test should validate real PostgreSQL behavior.

---

### 29. QUESTION
How would you test that a quality failure blocks publication?

**ANSWER:** Combine a dependency test with a behavioral failure-path test.

**EXPLANATION:** The structure test proves the graph, while the behavioral test proves that the failure prevents downstream publication.

---

### 30. QUESTION
How would you detect slow DAG parsing?

**ANSWER:** Measure import/parse time and inspect module-level code for network calls, database calls, expensive computation, and large initialization work.

**EXPLANATION:** Parse-time performance affects scheduler/DAG-processing capacity at scale.

---

## Advanced — 10 Questions

### 31. QUESTION
Design a production CI pipeline for an Airflow repository.

**ANSWER:** Use staged validation: static analysis → unit tests → DAG import tests → structure tests → policy tests → template/data-interval tests → targeted integration tests → build/deployment validation.

**EXPLANATION:** Cheap deterministic checks should run early, while expensive environment-dependent checks should run later or on appropriate branches/merges.

---

### 32. QUESTION
How would you design a testing strategy for 100 production DAGs without executing every DAG end-to-end on every pull request?

**ANSWER:** Test all DAGs for importability, apply common policy checks globally, test stable structures selectively, unit-test business logic independently, and run targeted integration/end-to-end tests for affected or critical workflows.

**EXPLANATION:** The strategy maximizes coverage of common failure classes while controlling CI cost.

---

### 33. QUESTION
How would you prove that a backfill is safe?

**ANSWER:** Test fixed historical data intervals, deterministic partition selection, correct templates, idempotent writes, expected downstream dependencies, and repeated execution.

**EXPLANATION:** Backfill correctness is a combination of temporal correctness, data correctness, and safe rerun behavior.

---

### 34. QUESTION
How would you test an external API task?

**ANSWER:** Unit-test business logic with a mock client, then integration-test representative API semantics against an isolated or controlled test endpoint where appropriate, including failure cases.

**EXPLANATION:** Mocks provide fast feedback while integration tests validate real serialization, authentication, status handling, and client behavior.

---

### 35. QUESTION
How would you validate orchestration policies across an entire DAG repository?

**ANSWER:** Build reusable policy tests that discover every DAG and inspect common properties such as owner, tags, retry policy, timeout requirements, catch-up, and forbidden operators.

**EXPLANATION:** Centralized policy validation prevents individual DAG authors from accidentally violating platform standards.

---

### 36. QUESTION
How would you test a DAG that uses dynamically generated tasks?

**ANSWER:** Test the generation contract and representative expanded structure rather than relying on a brittle fixed task count.

**EXPLANATION:** Dynamic workflows need tests that validate required inputs, dependencies, and failure semantics without assuming a permanently fixed number of runtime tasks.

---

### 37. QUESTION
How would you test Airflow, Dagster, and Prefect workflows using one general philosophy?

**ANSWER:** Separate business-logic tests from orchestration tests, validate structure/dependencies, test policies and failure behavior, validate external integrations, and verify deployment.

**EXPLANATION:** The APIs differ, but the engineering contracts—correct logic, correct orchestration, safe failures, and operational correctness—are shared.

---

### 38. QUESTION
What is the difference between pre-deployment and post-deployment validation?

**ANSWER:** Pre-deployment validation proves the artifact should be deployable; post-deployment validation proves the production orchestration environment actually loaded and operates the intended workflows.

**EXPLANATION:** A deployment can succeed technically while a DAG is missing, renamed, unable to import, or configured incorrectly.

---

### 39. QUESTION
How would you test a retry-safe database write?

**ANSWER:** Inject a failure after the database side effect but before task completion, allow a retry, and assert that the final database state contains the correct records exactly once.

**EXPLANATION:** This reproduces the uncertain-outcome failure that creates duplicate-write bugs.

---

### 40. QUESTION
What does production-grade orchestration testing ultimately prove?

**ANSWER:** It proves that the workflow can be loaded, has the intended structure and policies, performs correct business logic, handles failures safely, integrates correctly with external systems, and remains present and correctly configured after deployment.

**EXPLANATION:** Production quality is a layered property. No single test can establish it.

---

# 65. Final Self-Assessment

Answer **YES** only if you can demonstrate the skill, not merely recognize the terminology.

- [ ] Can I explain what DAG testing means?
- [ ] Can I explain the orchestration testing pyramid?
- [ ] Can I write import tests?
- [ ] Can I use `dag.test()`?
- [ ] Can I use `airflow dags test`?
- [ ] Can I unit-test task/business logic independently?
- [ ] Can I write pytest tests?
- [ ] Can I test DAG structure?
- [ ] Can I validate dependencies?
- [ ] Can I reason about DAG cycles?
- [ ] Can I write policy tests?
- [ ] Can I validate owners and tags?
- [ ] Can I validate retries?
- [ ] Can I validate timeouts?
- [ ] Can I validate catch-up configuration?
- [ ] Can I detect forbidden operators?
- [ ] Can I use Ruff/static analysis?
- [ ] Can I reason about parse-time performance?
- [ ] Can I mock hooks?
- [ ] Can I mock connections?
- [ ] Can I use environment-based test connections?
- [ ] Can I test Jinja templates?
- [ ] Can I test data intervals?
- [ ] Can I verify quality gates block publishing?
- [ ] Can I test task failures?
- [ ] Can I test retry behavior?
- [ ] Can I test idempotency?
- [ ] Can I write integration tests?
- [ ] Can I use Docker services for integration testing?
- [ ] Can I test Dagster assets?
- [ ] Can I test Prefect flows?
- [ ] Can I design a CI testing pipeline?
- [ ] Can I validate deployments?
- [ ] Can I detect disappeared DAGs?
- [ ] Can I design a production orchestration test strategy?

---

# 66. Final Production Checklist

## Static Quality

- [ ] Ruff/static analysis passes.
- [ ] Formatting passes.
- [ ] No obvious unused/dead imports.
- [ ] No unexplained module-level side effects.

## Importability

- [ ] Every expected DAG imports.
- [ ] Required dependencies are available.
- [ ] No production network calls happen at import time.
- [ ] Parse time is within the team's budget.

## Structure

- [ ] Expected tasks exist.
- [ ] Critical dependencies are correct.
- [ ] No unintended cycles.
- [ ] Quality gates precede publication.
- [ ] Dynamic-work contracts are tested.

## Policy

- [ ] Owner is present.
- [ ] Tags are present.
- [ ] Retry policy is deliberate.
- [ ] Timeout policy is deliberate.
- [ ] Start date is deterministic.
- [ ] Catch-up is deliberate.
- [ ] Forbidden operators are absent.

## Logic

- [ ] Business logic is unit-tested.
- [ ] Edge cases are covered.
- [ ] Expected exceptions are covered.
- [ ] Idempotency is tested.

## Templates and Intervals

- [ ] Important templates are rendered in tests.
- [ ] Data interval boundaries are tested.
- [ ] Historical intervals are tested.
- [ ] Timezone assumptions are explicit.

## Integrations

- [ ] External services are mocked for unit tests where appropriate.
- [ ] Critical SQL is integration-tested.
- [ ] Object storage behavior is integration-tested where required.
- [ ] SFTP behavior is integration-tested where required.
- [ ] Test credentials are isolated.

## Failure Behavior

- [ ] Transient failure behavior is tested.
- [ ] Retry behavior is tested.
- [ ] Timeout behavior is tested.
- [ ] Permanent failure behavior is tested.
- [ ] Partial failures are tested.
- [ ] Quality failures block unsafe publication.

## CI

- [ ] Fast tests run on pull requests.
- [ ] Expensive tests are placed appropriately.
- [ ] CI blocks deployment on critical validation failures.
- [ ] Test reports are actionable.

## Deployment

- [ ] Expected DAG inventory is known.
- [ ] Deployed DAG inventory is checked.
- [ ] No required DAG disappeared.
- [ ] Production configuration is validated.
- [ ] Scheduler/DAG processor sees the intended version.

---

# 67. Final Mental Model

Do not think:

```text
"DAG parses, therefore DAG is good."
```

Think:

```text
                    PRODUCTION WORKFLOW
                           │
                           ▼
                    Static Analysis
                           │
                           ▼
                     Importability
                           │
                           ▼
                    Unit Correctness
                           │
                           ▼
                   DAG Structure
                           │
                           ▼
                 Policy / Contracts
                           │
                           ▼
              Templates / Data Intervals
                           │
                           ▼
                  Failure Behavior
                           │
                           ▼
                External Integrations
                           │
                           ▼
                       CI
                           │
                           ▼
                     Deployment
                           │
                           ▼
                 Production Validation
```

The goal is to prove:

```text
CAN IT LOAD?
     +
IS THE GRAPH CORRECT?
     +
DO POLICIES HOLD?
     +
IS THE BUSINESS LOGIC CORRECT?
     +
DO TEMPLATES AND INTERVALS WORK?
     +
DO EXTERNAL SYSTEMS WORK?
     +
ARE FAILURES SAFE?
     +
ARE RERUNS IDEMPOTENT?
     +
DID DEPLOYMENT PRESERVE THE WORKFLOW?
```

That is production-grade orchestration quality engineering.

---

# 68. Key Takeaways

1. **Importability is necessary but not sufficient.**
2. **A DAG can parse and still be logically wrong.**
3. **Business logic should be unit-testable without Airflow.**
4. **Structure tests protect dependencies and orchestration semantics.**
5. **Policy tests enforce engineering standards.**
6. **Dynamic start dates can create nondeterministic scheduling behavior.**
7. **Catch-up must be deliberate.**
8. **Retry configuration must be distinguished from retry behavior.**
9. **Parse-time code should be cheap and side-effect-free.**
10. **Mocks provide speed; integration tests provide realism.**
11. **Templates and data intervals are correctness concerns.**
12. **Quality gates must actually block unsafe publication.**
13. **Failure behavior is part of the workflow contract.**
14. **Idempotency must be tested under retries and reruns.**
15. **Docker-backed integration tests provide realistic isolated services.**
16. **Dagster and Prefect require testing strategies appropriate to their models, but the underlying quality principles are shared.**
17. **CI should layer fast deterministic tests before expensive integration tests.**
18. **Deployment validation is necessary because successful CI does not guarantee successful production loading.**
19. **Expected DAG inventories help detect silently disappeared workflows.**
20. **Production testing proves not just that code works, but that orchestration remains correct, recoverable, observable, and deployable.**
