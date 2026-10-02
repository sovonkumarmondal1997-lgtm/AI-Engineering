# Airflow DAGs, Operators, and TaskFlow API

> **Stage:** 2 — Python for Data Engineering  
> **Module:** `13-Orchestration-and-Workflow-Management/`  
> **Topic:** 04 — Airflow DAGs, Operators, and TaskFlow API  
> **Primary implementation target:** Apache Airflow 3.x  
> **Prerequisites:** Topics 01–03 of this module

---

# 1. Learning Objective

The previous topics established:

```text
DAG concepts
→ dependencies
→ scheduling
→ why orchestration exists
→ Airflow architecture
```

This topic moves from architecture to authoring.

By the end, you should be able to look at a Data Engineering workflow and determine:

```text
What is the DAG?

What are the tasks?

Which operator or TaskFlow abstraction represents each task?

What are the dependencies?

What data interval should each task process?

Where should Jinja templating be used?

Should the work be dynamically mapped?

How should mapping be bounded?

Where should branching occur?

Which trigger rule is correct?

What requires setup and teardown?

How should existing CLI/package/dbt workloads be orchestrated?

Where should the business logic live?

How should concurrency be controlled?

Is the DAG thin, deterministic, idempotent, observable, and maintainable?
```

The progression is:

```text
Basic
→ Intermediate
→ Advanced
→ Production patterns
→ Coding
→ Debugging
→ Failure injection
→ Architecture
→ Interview preparation
```

The central principle is:

> **A production Airflow DAG should describe and coordinate the workflow, not become the workflow's entire implementation.**

---

# 2. Airflow 3.x Version Rule

This topic primarily teaches **Airflow 3.x**.

When a version-sensitive concept appears, distinguish:

```text
Airflow 3.x — current focus
```

from:

```text
Airflow 2.x — legacy/reference
```

Do not silently copy older examples.

Before using version-sensitive code, verify:

```text
Airflow version
Python version
provider version
```

and consult the documentation for the installed release when exact syntax matters.

This is particularly important for:

- DAG imports;
- TaskFlow;
- branching;
- setup/teardown;
- dynamic mapping;
- provider operators;
- executor-related routing.

---

# 3. The Simplest DAG

Start with the smallest useful Airflow 3.x DAG:

```python
from airflow.sdk import dag, task


@dag
def hello_pipeline():

    @task
    def hello():
        print("Hello Airflow")

    hello()


hello_pipeline()
```

This contains two conceptual layers:

```text
DAG
 └── task
```

The DAG describes the workflow.

The task represents executable work.

The Python function body is **not** executed merely because the DAG file is parsed.

---

# 4. DAG Definition Time vs Task Execution Time

This distinction is fundamental.

## DAG definition time

Airflow processes the Python source:

```text
DAG file
   ↓
Python imports
   ↓
DAG definition
   ↓
Task definitions
```

## Task execution time

Later:

```text
Scheduler
   ↓
task becomes runnable
   ↓
execution environment
   ↓
Python function executes
```

Therefore this is dangerous:

```python
result = expensive_function()
```

at module/DAG-definition time.

The expensive function executes while the DAG source is being processed.

Prefer:

```python
@task
def expensive_function():
    ...
```

The architecture becomes:

```text
DAG file
    ↓
describes work

Task runtime
    ↓
performs work
```

This follows the architecture principle from Topic 03:

> **DAG files define orchestration; tasks perform work.**

---

# 5. DAG Definition

A DAG is the workflow definition.

A practical DAG contains metadata such as:

```text
dag_id
schedule
start_date
catchup
tags
task configuration
```

A conceptual example:

```python
from datetime import datetime, timezone

from airflow.sdk import dag


@dag(
    dag_id="orders_daily",
    schedule="0 2 * * *",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["orders", "daily"],
)
def orders_daily():
    ...
```

The exact API surface should be verified against the installed Airflow 3.x release.

---

# 6. `dag_id`

`dag_id` uniquely identifies a DAG within an Airflow environment.

Example:

```python
dag_id="orders_daily"
```

Good names communicate purpose:

```text
orders_daily
customer_snapshot_daily
payments_ingestion
```

Poor names:

```text
dag1
test
pipeline
new_dag
```

Production naming should optimize:

```text
discoverability
ownership
operations
incident response
historical interpretation
```

A DAG name is operational metadata, not decoration.

---

# 7. Schedule

A schedule determines when Airflow should create/schedule workflow runs according to the DAG's scheduling configuration.

Example:

```python
schedule="0 2 * * *"
```

Conceptually:

```text
schedule
   ↓
workflow run
   ↓
data interval
   ↓
tasks process that interval
```

Do not confuse:

```text
run creation
```

with:

```text
task execution
```

A scheduled run still has to pass through task dependency and concurrency rules.

Topic 01 covered scheduling theory in detail. Here the focus is how scheduling becomes DAG configuration.

---

# 8. Timezone-Aware `start_date`

A production DAG should deliberately define its timezone policy.

Prefer an explicit timezone-aware datetime:

```python
from datetime import datetime, timezone

start_date=datetime(
    2026,
    1,
    1,
    tzinfo=timezone.utc,
)
```

Avoid casually using:

```python
datetime(2026, 1, 1)
```

without a deliberate timezone policy.

Why?

```text
timezone
   ↓
schedule interpretation
   ↓
data interval
   ↓
historical reproducibility
```

Timezone ambiguity becomes especially dangerous around:

- daylight-saving transitions;
- regional schedules;
- historical execution;
- cross-region pipelines.

UTC is often operationally convenient, but the correct policy depends on the business schedule and platform.

---

# 9. `catchup`

A common configuration is:

```python
catchup=False
```

Catch-up controls whether historical scheduled intervals should be considered when a DAG begins operating after its start point.

For example:

```text
start_date = January 1
today      = January 10
```

With an appropriate schedule, historical intervals may be eligible.

With:

```python
catchup=False
```

the DAG does not automatically create the full backlog simply because the start date is historical.

Important distinction:

```text
catchup=False
```

does **not** mean:

> “This DAG can never process historical data.”

A historical run can still be deliberately created through supported operational mechanisms.

Detailed backfill/catch-up curriculum belongs to Topic 08.

---

# 10. Tags

Tags improve operational organization.

Example:

```python
tags=[
    "orders",
    "production",
    "daily",
]
```

Useful tag dimensions include:

```text
domain
owner
environment
criticality
schedule
```

For example:

```python
tags=[
    "domain:orders",
    "owner:data-platform",
    "tier:critical",
]
```

Tags help with:

- discovery;
- filtering;
- operational ownership;
- incident response.

Tags are metadata. They are **not** authorization controls.

---

# 11. Default Arguments and Configuration

DAG/task defaults can reduce repetitive configuration.

Conceptually:

```text
shared defaults
      ↓
tasks
```

Potential settings include:

- ownership metadata;
- retry-related defaults;
- execution configuration;
- task behavior.

Keep version awareness in mind because Airflow's APIs evolve.

Do not copy an old `default_args` example merely because it appears in a tutorial.

A useful engineering rule is:

> Use defaults for genuinely shared behavior; keep task-specific behavior explicit.

---

# 12. A Complete Basic DAG

A compact example:

```python
from datetime import datetime, timezone

from airflow.sdk import dag, task


@dag(
    dag_id="orders_daily",
    schedule="0 2 * * *",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["orders", "daily"],
)
def orders_daily():

    @task
    def extract():
        print("extract orders")

    @task
    def transform():
        print("transform orders")

    @task
    def publish():
        print("publish orders")

    extract() >> transform() >> publish()


orders_daily()
```

The important structure is:

```text
DAG metadata
     ↓
tasks
     ↓
dependencies
```

---

# 13. What Is a Task?

A task is a unit of orchestrated work.

Examples:

```text
extract data
run SQL
call CLI
run dbt
validate data
publish data
send notification
```

A task should have a meaningful operational boundary.

Bad granularity:

```text
task_1 = add one column
task_2 = rename one column
task_3 = filter one row
```

Better:

```text
transform_orders
```

when those operations form one meaningful transformation unit.

Task boundaries affect:

```text
observability
retry behavior
parallelism
debugging
resource usage
maintainability
```

---

# 14. What Is an Operator?

An operator is a reusable task abstraction that describes a kind of work Airflow can execute.

Conceptually:

```text
Operator
    ↓
Task instance
    ↓
Execution
```

Common categories include:

```text
Bash
Python
SQL
Provider-specific
```

The distinction is:

```text
DAG
    = workflow definition

Task
    = unit of orchestrated work

Operator
    = reusable task abstraction

TaskFlow
    = Python-native task authoring model
```

---

# 15. Bash Operator

A simple Bash example:

```python
from airflow.providers.standard.operators.bash import BashOperator

show_date = BashOperator(
    task_id="show_date",
    bash_command="date",
)
```

The exact provider import should be verified for the installed Airflow/provider release.

The execution flow is:

```text
Airflow task
   ↓
shell process
   ↓
command
   ↓
exit code
   ↓
task success/failure
```

If the command returns a non-zero exit code, the task is normally considered failed unless the operator's behavior says otherwise.

---

# 16. Bash for Existing CLI Tools

Bash is useful when the organization already has a command-line application.

For example:

```python
run_transform = BashOperator(
    task_id="run_transform",
    bash_command=(
        "python -m platform.transform "
        "--start '{{ data_interval_start }}' "
        "--end '{{ data_interval_end }}'"
    ),
)
```

The DAG coordinates the CLI.

The CLI performs the business/data processing.

This is an important thin-DAG pattern:

```text
Airflow
   ↓
CLI
   ↓
data processing
```

Do not turn a Bash task into hundreds of lines of inline business logic.

---

# 17. Bash Trade-offs

Bash is useful for:

- existing CLI tools;
- simple shell commands;
- external programs;
- lightweight system operations.

Bash becomes problematic when it contains:

- complex business rules;
- complex error handling;
- large embedded programs;
- difficult-to-test logic;
- portability-sensitive shell behavior.

Use:

```text
Bash → orchestration of an existing CLI
```

rather than:

```text
Bash → entire data application
```

Also consider shell quoting, environment variables, working directories, and secrets.

Never hard-code credentials in a command.

---

# 18. Python Operator

A traditional Python operator pattern is:

```python
def validate_orders():
    print("validating orders")


validate_task = PythonOperator(
    task_id="validate_orders",
    python_callable=validate_orders,
)
```

The callable is executed at task runtime.

The important distinction is:

```text
python_callable=validate_orders
```

versus accidentally invoking it during DAG construction:

```python
python_callable=validate_orders()
```

The latter executes the function immediately and is not the intended task-authoring pattern.

---

# 19. Python Operator Trade-offs

Python operators are useful when:

- an existing Python callable should be executed;
- explicit operator semantics improve clarity;
- a provider/operator style fits the task.

But for Python-native pipelines, TaskFlow often provides a more readable model.

Compare:

```text
PythonOperator
    explicit operator object

TaskFlow
    Python function becomes task
```

Neither is universally superior.

Choose the abstraction that clearly expresses the work.

---

# 20. SQL Operators

SQL operators represent database/warehouse work.

Conceptually:

```text
Airflow task
     ↓
SQL operator
     ↓
database / warehouse
```

A simplified PostgreSQL-oriented example may look like:

```python
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

refresh_orders = SQLExecuteQueryOperator(
    task_id="refresh_orders",
    conn_id="warehouse",
    sql="""
        INSERT INTO analytics.orders_daily
        SELECT *
        FROM staging.orders;
    """,
)
```

Exact provider/operator names and parameters are version/provider dependent.

Verify them against the installed provider documentation.

Do not teach Connections, Variables, or Hooks in depth here; those belong to Topic 05.

---

# 21. SQL Operator Production Considerations

Ask:

```text
Is the SQL idempotent?
What interval does it process?
Can reruns duplicate rows?
Is the transaction appropriate?
Is the query bounded?
Is the target table protected?
```

A SQL task should not merely “run SQL.”

It should represent a correct, deterministic unit of data work.

---

# 22. Provider Operators

Providers extend Airflow with integrations.

Examples include:

```text
PostgreSQL
AWS
Kubernetes
HTTP
SFTP
cloud services
```

Conceptually:

```text
Airflow core
      +
provider package
      ↓
external-system integration
```

Use a provider operator when it clearly expresses the external action.

Do not turn this topic into a provider-by-provider tutorial.

---

# 23. Dependencies

The dependency operator:

```python
task_a >> task_b
```

means:

```text
task_a
   ↓
task_b
```

It means a relationship exists.

It does **not** mean:

> Execute task A right now.

Likewise:

```python
task_b << task_a
```

represents the same dependency relationship.

---

# 24. Dependency Chaining

A simple chain:

```python
extract >> transform >> validate >> publish
```

means:

```text
extract
   ↓
transform
   ↓
validate
   ↓
publish
```

Fan-out:

```python
extract >> [validate_orders, validate_customers]
```

produces:

```text
             ┌── validate_orders
extract ─────┤
             └── validate_customers
```

Fan-in:

```python
[validate_orders, validate_customers] >> publish
```

produces:

```text
validate_orders ──┐
                  ├── publish
validate_customers┘
```

These relationships define orchestration order.

---

# 25. TaskFlow API

TaskFlow is Airflow's Python-native task authoring model.

Traditional operator style:

```python
extract = PythonOperator(...)
transform = PythonOperator(...)
```

TaskFlow style:

```python
@task
def extract():
    return ...


@task
def transform(data):
    return ...
```

The TaskFlow model makes Python function boundaries visible.

Its strengths include:

- readable DAGs;
- natural Python syntax;
- function arguments representing dependencies;
- return values representing inter-task communication;
- good fit for Python-native workflows.

---

# 26. `@dag`

The `@dag` decorator lets a Python function define a DAG.

Example:

```python
from airflow.sdk import dag


@dag(
    dag_id="orders_daily",
    schedule="0 2 * * *",
    catchup=False,
)
def orders_daily():
    ...
```

The function acts as a DAG factory/definition boundary.

The important mental model is:

```text
@dag function
    ↓
workflow definition
```

not:

```text
@dag function
    ↓
execute entire pipeline immediately
```

---

# 27. `@task`

A TaskFlow task:

```python
from airflow.sdk import task


@task
def extract_orders():
    return "orders"
```

declares a task.

When used inside a DAG:

```python
orders = extract_orders()
```

the call constructs/represents a task relationship in the DAG definition.

It does not mean the function body executes immediately during DAG parsing.

This is one of the most important TaskFlow concepts.

---

# 28. TaskFlow Dependencies Through Arguments

Example:

```python
@task
def extract():
    return "orders"


@task
def transform(data):
    return f"transformed-{data}"


raw = extract()
transformed = transform(raw)
```

The argument:

```python
transform(raw)
```

expresses a dependency.

Conceptually:

```text
extract
   ↓
transform
```

The return value becomes part of the task-to-task communication boundary.

---

# 29. TaskFlow Return Values and XCom

TaskFlow return values commonly use Airflow's XCom mechanism to move **small metadata** between tasks.

Good values:

```text
file path
object-storage URI
table name
partition ID
row count
status
small identifiers
```

Bad values:

```text
large DataFrame
entire dataset
large binary file
hundreds of MB of JSON
```

Prefer:

```text
Task A
   ↓
"s3://bucket/orders/2026-10-01/"
   ↓
Task B
   ↓
reads actual data
```

rather than:

```text
Task A
   ↓
huge DataFrame through XCom
   ↓
Task B
```

The full Connections/Variables/Hooks/XCom curriculum belongs to Topic 05.

---

# 30. TaskFlow vs Operators

| Concern | Operators | TaskFlow |
|---|---|---|
| Style | Operator objects | Python functions |
| Best fit | External/predefined operations | Python-native logic |
| Readability | Can be explicit/verbose | Often concise |
| Data passing | Configuration/XCom | Function arguments/return values |
| External systems | Strong provider ecosystem | Can call clients/packages |
| Reuse | Operator classes | Python functions |
| Main strength | Express an operation | Express Python workflow logic |

There is no universal winner.

Use:

> **the abstraction that most clearly expresses the work being orchestrated.**

---

# 31. When to Use TaskFlow

TaskFlow is particularly useful for:

```text
Python-native pipelines
clean function boundaries
small metadata passed between tasks
readable dependencies
testable business logic
```

Example:

```python
@task
def validate_orders(path):
    ...
```

The function can be designed as normal Python logic while Airflow supplies the orchestration boundary.

Keep substantial business logic in importable Python packages when it should be reused outside Airflow.

---

# 32. Thin DAG Principle

A bad DAG:

```python
@dag
def pipeline():

    # hundreds of lines
    # business rules
    # API client implementation
    # transformations
    # validation engine
    # SQL generation
    # complex data processing
```

A better architecture:

```text
Airflow DAG
     ↓
thin orchestration
     ↓
Python package / CLI / SQL / dbt
     ↓
actual data processing
```

Example:

```python
@task
def run_transform():
    subprocess.run(
        [
            "python",
            "-m",
            "platform.transform",
        ],
        check=True,
    )
```

Or call an importable package function where that is appropriate.

Thin DAGs improve:

- testing;
- maintainability;
- reuse;
- readability;
- deployment;
- debugging;
- versioning.

---

# 33. Importable Package Logic

A preferred architecture:

```text
Airflow DAG
      ↓
orchestration
      ↓
Python package
      ↓
business/data logic
```

For example:

```text
src/
└── platform/
    ├── extraction.py
    ├── transformation.py
    └── quality.py
```

The DAG should coordinate:

```text
extract
→ transform
→ quality
→ publish
```

while the package implements:

```text
how extraction works
how transformation works
how validation works
```

This separation enables unit testing outside Airflow.

---

# 34. Module 2.12 CLI Integration

The roadmap requires integrating existing transformation tooling from Module 2.12.

A conceptual command:

```bash
python -m platform.transform \
    --start 2026-10-01T00:00:00Z \
    --end 2026-10-02T00:00:00Z
```

Airflow should supply the interval.

The architecture becomes:

```text
Airflow
   ↓
data interval
   ↓
Module 2.12 CLI
   ↓
transformation
```

Do not duplicate the transformation implementation inside the DAG.

---

# 35. Data-Interval-Aware Tasks

A production batch task should know what interval it is responsible for.

Conceptually:

```text
DAG run
   ↓
data interval
   ↓
task
   ↓
processing for that interval
```

This is safer than:

```python
datetime.now()
```

because “now” changes depending on when the task actually executes.

For example:

```text
scheduled interval:
2026-10-01 → 2026-10-02
```

The task should process that interval even if it actually runs on:

```text
2026-10-03
```

after a delay or rerun.

---

# 36. Jinja Templating

Jinja allows runtime context to be injected into supported templated fields.

Examples:

```jinja
{{ ds }}
```

```jinja
{{ data_interval_start }}
```

```jinja
{{ data_interval_end }}
```

```jinja
{{ run_id }}
```

The important model is:

```text
DAG definition
      ↓
template expression
      ↓
runtime context
      ↓
rendered value
      ↓
task execution
```

---

# 37. `{{ ds }}`

`ds` represents a date-oriented runtime value.

Example:

```jinja
{{ ds }}
```

It can be useful for:

```text
partition naming
date-based paths
simple date logging
```

But do not assume a single date string fully represents the data interval.

For interval-aware pipelines, exact boundaries are often more useful:

```jinja
{{ data_interval_start }}
{{ data_interval_end }}
```

---

# 38. `{{ data_interval_start }}`

Example:

```python
bash_command="""
python -m platform.transform \
  --start "{{ data_interval_start }}" \
  --end "{{ data_interval_end }}"
"""
```

This lets the task process the interval associated with the DAG run.

The important benefit is deterministic historical behavior:

```text
same interval
     ↓
same intended input boundaries
```

---

# 39. `{{ data_interval_end }}`

The end boundary defines the other side of the processing interval.

For example:

```text
[2026-10-01T00:00:00Z,
 2026-10-02T00:00:00Z)
```

A half-open interval is a useful mental model:

```text
start <= timestamp < end
```

The exact semantics of downstream systems must be respected.

Do not blindly assume every database, API, or partitioning system uses the same boundary convention.

---

# 40. `{{ run_id }}`

A run ID can help with:

```text
logging
tracing
output correlation
audit metadata
debugging
```

Example:

```python
bash_command="""
python -m platform.audit \
  --run-id "{{ run_id }}"
"""
```

Do not use run IDs as a substitute for a correct business/data partition key.

---

# 41. Jinja Correctness and Security

Templating is powerful but should not become uncontrolled code generation.

Be careful with:

```text
shell quoting
SQL construction
user-controlled values
secrets
paths
```

Bad conceptual pattern:

```text
untrusted input
    ↓
raw shell command string
    ↓
execution
```

Prefer strongly bounded arguments and safe interfaces.

Do not hard-code credentials in templates.

Do not use templating to solve a problem that should be solved through structured parameters.

---

# 42. Task Groups

Task Groups organize related tasks without changing the underlying workflow meaning.

Example:

```text
orders_daily
├── extract
│   ├── orders
│   ├── customers
│   └── products
├── transform
│   ├── bronze_to_silver
│   └── silver_to_gold
├── quality
│   ├── schema
│   ├── freshness
│   └── reconciliation
└── publish
```

Task groups improve:

- readability;
- UI organization;
- logical boundaries;
- conceptual communication.

---

# 43. Task Group Design

Group tasks by meaningful responsibilities.

Good:

```text
extract
transform
quality
publish
```

Bad:

```text
group_1
group_2
group_3
```

unless those groups have a real architectural meaning.

A Task Group should answer:

> “Why do these tasks belong together?”

not:

> “How can I hide more tasks?”

---

# 44. Dynamic Task Mapping

Suppose the source list is only known at runtime:

```python
sources = [
    "orders",
    "customers",
    "products",
    "payments",
]
```

Without mapping, you might manually create:

```text
extract_orders
extract_customers
extract_products
extract_payments
```

Dynamic mapping lets Airflow create task instances based on runtime input.

Conceptually:

```text
source list
    ↓
mapped task
    ↓
task instance per source
```

This is useful when workload cardinality changes.

---

# 45. `.expand()`

A simplified TaskFlow mapping pattern:

```python
from airflow.sdk import task


@task
def extract_source(source):
    print(f"extracting {source}")


sources = ["orders", "customers", "products"]

extract_source.expand(source=sources)
```

Conceptually:

```text
extract_source[orders]
extract_source[customers]
extract_source[products]
```

The exact runtime representation is managed by Airflow.

The key idea is:

> **The number of task instances can be generated from runtime data.**

---

# 46. `.partial()`

`.partial()` separates fixed arguments from mapped arguments.

Example:

```python
@task
def extract_source(source, environment):
    print(environment, source)


extract_source.partial(
    environment="prod",
).expand(
    source=["orders", "customers", "products"],
)
```

Here:

```text
environment = fixed
source      = mapped
```

Conceptually:

```text
prod + orders
prod + customers
prod + products
```

This is useful when one configuration applies to every mapped task.

---

# 47. Dynamic Mapping Trade-offs

Advantages:

```text
less repetitive DAG code
dynamic workload size
parallel execution
runtime discovery
```

Risks:

```text
too many task instances
scheduler pressure
metadata growth
external-system overload
harder debugging
downstream complexity
```

Therefore:

> **Dynamic mapping creates execution flexibility, not unlimited capacity.**

---

# 48. Mapping and Source Rate Limits

Suppose:

```text
100 mapped extraction tasks
        ↓
external API
        ↓
API permits only 10 concurrent requests
```

This architecture is unsafe if all 100 tasks can hit the source simultaneously.

Use resource controls such as pools and appropriate concurrency limits.

Conceptually:

```text
100 mapped tasks
       ↓
source pool = 10
       ↓
10 concurrent requests
```

The exact pool configuration is deployment-specific.

The principle is universal:

> **Bound concurrency at the resource that can be damaged by concurrency.**

---

# 49. Branching

Branching chooses a workflow path based on runtime conditions.

Example:

```text
quality_check
      |
      +---- pass ----> publish
      |
      +---- fail ----> quarantine
```

Branching is appropriate when the workflow itself has conditional paths.

Examples:

```text
quality passed?
data available?
source changed?
business condition satisfied?
```

Branching should remain simple.

Do not put the complete business decision engine inside the DAG.

---

# 50. Branching and Skipped Tasks

When a branch selects one path:

```text
branch
 ├── publish
 └── quarantine
```

and selects:

```text
publish
```

the other path can become:

```text
quarantine = skipped
```

This matters because downstream tasks may consider:

```text
success
failed
skipped
upstream_failed
```

differently.

Therefore branching must be designed together with trigger rules.

---

# 51. Short-Circuiting

Short-circuiting is useful when a condition determines whether a downstream section should continue.

Conceptually:

```text
data_available?
      |
      +── true  → continue
      |
      +── false → stop downstream path
```

Difference:

```text
Branching
    chooses among paths

Short-circuiting
    decides whether downstream work should continue
```

Use the current Airflow 3.x-compatible API/operator for the installed provider version rather than copying an older tutorial unchanged.

---

# 52. Trigger Rules

The default success-oriented dependency behavior is not sufficient for every workflow.

Important trigger rules include:

```text
all_success
all_done
one_failed
none_failed
```

Other trigger rules may be appropriate depending on the workflow.

The critical skill is to reason from upstream states to downstream eligibility.

---

# 53. `all_success`

Consider:

```text
A ──┐
B ──┼── C
D ──┘
```

With:

```text
all_success
```

C becomes eligible only when the required upstream tasks have succeeded.

This is appropriate for:

```text
A → B → C
```

style success-dependent pipelines.

---

# 54. `all_done`

`all_done` means downstream execution can proceed after upstream tasks reach terminal states, rather than requiring all upstream tasks to succeed.

Useful for:

```text
cleanup
resource release
diagnostic collection
```

Conceptually:

```text
A ──┐
B ──┼── cleanup
C ──┘

A/B/C:
success OR failure
       ↓
cleanup
```

Cleanup behavior should be designed deliberately.

---

# 55. `one_failed`

A failure-handling path may use:

```text
one_failed
```

Conceptually:

```text
A ──┐
B ──┼── notify_failure
C ──┘
```

The notification path should not accidentally require all upstream tasks to succeed.

The exact behavior depends on upstream states and the trigger-rule semantics of the installed Airflow release.

---

# 56. `none_failed`

`none_failed` is particularly useful when branching can produce skipped states.

For example:

```text
branch
 ├── path_a
 └── path_b
```

One path may be:

```text
success
```

while the other is:

```text
skipped
```

A downstream task requiring:

```text
none_failed
```

can be appropriate when skipped upstreams are acceptable but failed upstreams are not.

This is why:

```text
all_success
```

and:

```text
none_failed
```

are not interchangeable.

---

# 57. Skipped States and Trigger Rules

A common mistake is:

```text
branch
  ↓
path_a
path_b
  ↓
join
```

with a join using the wrong trigger rule.

If:

```text
path_a = success
path_b = skipped
```

then a downstream task that requires all upstreams to be successful may not run.

Always ask:

```text
What states can each upstream produce?
What should the downstream task do with skipped?
What should it do with failed?
```

Trigger rules are workflow semantics, not merely configuration syntax.

---

# 58. Setup and Teardown

Some workflows require temporary resources:

```text
staging schema
temporary directory
ephemeral environment
temporary table
```

Conceptually:

```text
setup_staging
      ↓
transform
      ↓
quality
      ↓
teardown_staging
```

Setup/teardown tasks express resource lifecycle.

The important requirement is:

```text
resource created
   ↓
resource used
   ↓
resource cleaned up
```

Cleanup behavior must be designed with failure paths in mind.

Use the current Airflow 3.x setup/teardown APIs and verify exact syntax against the installed release.

---

# 59. Concurrency Controls

Concurrency controls protect:

```text
source systems
databases
workers
APIs
downstream platforms
```

The roadmap requires understanding:

```text
max_active_runs
max_active_tasks
pools
priority_weight
queues/execution routing where applicable
```

These controls answer different questions.

---

# 60. `max_active_runs`

Conceptually:

```python
max_active_runs=1
```

limits how many runs of a DAG can be active at the same time.

Useful when:

```text
run N+1
```

must not overlap:

```text
run N
```

because both would modify the same resource.

But do not use it blindly.

Sometimes overlapping intervals are safe and desirable.

---

# 61. `max_active_tasks`

Conceptually:

```text
max active tasks for this DAG
```

bounds concurrent task execution associated with that DAG.

Useful for protecting:

```text
database capacity
worker capacity
source systems
external APIs
```

It is a DAG-level bound, not a substitute for every resource-specific control.

---

# 62. Pools

A pool models a shared constrained resource.

Example:

```text
SFTP_POOL = 3 slots
```

Suppose:

```text
20 extraction tasks
```

compete for the same SFTP source.

With three available slots:

```text
3 execute
17 wait
```

This is valuable because the limit follows the resource:

```text
SFTP capacity
```

rather than merely the number of DAG tasks.

---

# 63. Priority

Priority can influence which eligible work receives capacity when tasks compete.

Example:

```text
critical_orders_pipeline
```

versus:

```text
low_priority_reporting
```

The exact scheduling behavior depends on the configured environment and Airflow scheduling semantics.

Use priority deliberately.

Do not assume:

```text
high priority = immediate execution
```

Priority still operates within:

```text
dependencies
capacity
concurrency
resource availability
```

---

# 64. Queues and Execution Routing

Some Airflow execution architectures support routing work toward particular execution capacity.

Conceptually:

```text
light tasks
    ↓
general capacity

heavy tasks
    ↓
specialized capacity
```

The exact mechanism is executor-dependent.

Therefore distinguish:

```text
conceptual execution routing
```

from:

```text
a specific executor's configuration
```

Do not copy queue configuration from an unrelated Airflow version/executor.

---

# 65. One DAG per Logical Pipeline

Prefer:

```text
orders_daily
customers_daily
payments_daily
```

over:

```text
everything_company_data
```

A logical pipeline boundary improves:

- ownership;
- failure isolation;
- scheduling;
- observability;
- deployment;
- historical execution.

This does not mean every DAG must be tiny.

It means the DAG should have a coherent operational purpose.

---

# 66. Ownership Metadata

Use tags or other supported metadata to make ownership visible.

Example:

```python
tags=[
    "domain:orders",
    "owner:data-platform",
    "tier:critical",
]
```

This helps answer:

```text
Who owns this pipeline?
Which domain does it serve?
How critical is it?
```

Ownership metadata supports:

- incident response;
- discovery;
- operational accountability.

It does not replace authorization or access control.

---

# 67. The `orders_daily` Mini-Project

The roadmap requires a complete daily pipeline conceptually containing:

```text
dynamic-mapped extraction
→ bronze-to-silver
→ dbt gold
→ quality gate
→ publish
```

with:

```text
task groups
branching
failure handling
source-rate pools
setup/teardown
past-date execution
idempotency verification
```

The final architecture is:

```text
                         orders_daily
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
             SETUP                    EXTRACTION
                                      /    |    \
                                     /     |     \
                               orders customers products
                                     \     |     /
                                      \    |    /
                                       ▼   ▼   ▼
                                   BRONZE → SILVER
                                          │
                                          ▼
                                      DBT GOLD
                                          │
                                          ▼
                                    QUALITY GATE
                                      /       \
                                   PASS       FAIL
                                    |           |
                                    ▼           ▼
                                 PUBLISH      ALERT
```

---

# 68. `orders_daily` — Dynamic Extraction

Start with source definitions:

```python
sources = [
    "orders",
    "customers",
    "products",
]
```

Then map:

```python
extract_source.expand(source=sources)
```

Conceptually:

```text
extract[orders]
extract[customers]
extract[products]
```

The source list can be runtime-generated.

The important question is:

> Can the source system safely handle the resulting concurrency?

---

# 69. `orders_daily` — Source Rate Limit

Suppose:

```text
10 mapped extraction tasks
```

but the source permits only:

```text
3 concurrent requests
```

The DAG should not simply launch all 10.

Use a resource pool/concurrency boundary:

```text
10 mapped tasks
       ↓
source pool = 3
       ↓
3 active
7 waiting
```

This is a production reliability pattern.

---

# 70. `orders_daily` — Bronze to Silver

Call existing Module 2.12 transformation logic.

Conceptual command:

```bash
python -m platform.transform \
    --layer silver \
    --start "{{ data_interval_start }}" \
    --end "{{ data_interval_end }}"
```

The DAG supplies orchestration context.

The transformation package owns:

```text
business logic
data transformations
schema handling
processing implementation
```

---

# 71. `orders_daily` — dbt Gold

Airflow can coordinate a dbt workflow.

Conceptually:

```text
bronze → silver
       ↓
dbt build
       ↓
gold
```

The DAG should answer:

```text
When should dbt run?
What must succeed first?
Which interval/run does it belong to?
What happens if it fails?
```

dbt should own the transformation logic.

Airflow should own orchestration.

Do not turn this into a dbt tutorial.

---

# 72. `orders_daily` — Quality Gate

The quality stage checks:

```text
schema
freshness
reconciliation
row counts
business invariants
```

Conceptually:

```text
dbt gold
    ↓
quality gate
```

The quality gate should determine whether publication is safe.

A failure should normally prevent unsafe publication.

---

# 73. `orders_daily` — Branching

The quality result drives:

```text
PASS
   ↓
publish

FAIL
   ↓
failure handling
```

Conceptually:

```text
quality_gate
      |
      +── PASS ──> publish
      |
      +── FAIL ──> alert/quarantine
```

Branching should be small and explicit.

---

# 74. `orders_daily` — Failure Alert

The failure path should use an appropriate trigger rule such as:

```text
one_failed
```

The alert should contain useful context:

```text
DAG ID
run ID
data interval
failed task
failure reason
source/domain
operational link
```

Detailed callback and notification architecture belongs to Topic 07.

---

# 75. `orders_daily` — Setup and Teardown

Conceptually:

```text
setup_staging
      ↓
extract
      ↓
transform
      ↓
quality
      ↓
publish
      ↓
teardown_staging
```

Temporary resources might include:

```text
staging schema
temporary tables
temporary filesystem
ephemeral compute
```

The cleanup path must be considered even when upstream work fails.

---

# 76. `orders_daily` — Historical Execution

The same DAG definition should be able to process historical intervals.

For example:

```text
2026-09-28
2026-09-29
2026-09-30
```

The exact dates are illustrative.

The important principle is:

```text
DAG run
   ↓
data interval
   ↓
same deterministic logic
   ↓
different interval
```

Do not use:

```python
datetime.now()
```

as the primary business-date selector for interval-driven processing.

---

# 77. `orders_daily` — Idempotency Verification

Run the same interval twice:

```text
2026-09-29
```

First:

```text
execution 1
```

Then:

```text
execution 2
```

Verify:

```text
no duplicate outputs
no corrupted state
deterministic result
expected task behavior
```

Airflow does not automatically make a task idempotent.

Idempotency belongs to the task/data-processing design.

---

# 78. Complete Educational `orders_daily` DAG

The following is intentionally an architecture-focused example. Provider-specific connection IDs, environment setup, and exact operator parameters must be adapted to the installed Airflow/provider versions.

```python
from datetime import datetime, timezone

from airflow.sdk import dag, task
from airflow.providers.standard.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.task_group import TaskGroup


@dag(
    dag_id="orders_daily",
    schedule="0 2 * * *",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=[
        "domain:orders",
        "owner:data-platform",
        "tier:critical",
    ],
    max_active_runs=1,
    max_active_tasks=10,
)
def orders_daily():

    @task
    def discover_sources():
        return [
            "orders",
            "customers",
            "products",
        ]

    @task
    def extract_source(source):
        print(f"Extracting {source}")
        return {
            "source": source,
            "path": f"/bronze/{source}/",
        }

    with TaskGroup(group_id="extract") as extract_group:
        sources = discover_sources()

        extracted = extract_source.expand(
            source=sources,
        )

    transform_silver = BashOperator(
        task_id="transform_silver",
        bash_command=(
            "python -m platform.transform "
            "--layer silver "
            "--start '{{ data_interval_start }}' "
            "--end '{{ data_interval_end }}'"
        ),
    )

    dbt_gold = BashOperator(
        task_id="dbt_gold",
        bash_command=(
            "dbt build "
            "--select tag:orders "
        ),
    )

    @task
    def quality_gate():
        print("Running quality checks")
        return True

    @task.branch
    def choose_publish_path(quality_passed):
        if quality_passed:
            return "publish"
        return "quality_failed"

    publish = BashOperator(
        task_id="publish",
        bash_command=(
            "python -m platform.publish "
            "--start '{{ data_interval_start }}' "
            "--end '{{ data_interval_end }}'"
        ),
    )

    quality_failed = BashOperator(
        task_id="quality_failed",
        bash_command="python -m platform.alert --reason quality_failure",
    )

    teardown = BashOperator(
        task_id="teardown_staging",
        bash_command="python -m platform.cleanup --staging orders",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    (
        extract_group
        >> transform_silver
        >> dbt_gold
        >> quality_gate()
    )

    branch = choose_publish_path(quality_gate())

    branch >> [publish, quality_failed]

    [publish, quality_failed] >> teardown


orders_daily()
```

## Important implementation notes

This example intentionally illustrates:

```text
DAG metadata
TaskFlow
Task Groups
dynamic mapping
BashOperator
Jinja
branching
trigger rules
CLI integration
dbt integration
setup/teardown concept
concurrency controls
```

It also contains a simplification worth noticing:

```text
quality_gate()
```

is referenced more than once in the illustrative structure.

In production code, retain the TaskFlow task output in a variable and pass that value consistently:

```python
quality_result = quality_gate()
branch = choose_publish_path(quality_result)
```

That is clearer and avoids accidental duplicate task-definition patterns.

A cleaner production-oriented version of that section is:

```python
quality_result = quality_gate()

branch = choose_publish_path(
    quality_result
)

branch >> [publish, quality_failed]
[publish, quality_failed] >> teardown
```

Also verify current imports for:

```text
TaskGroup
TriggerRule
branch decorators
provider operators
```

against the installed Airflow 3.x/provider versions before executing the example.

---

# 79. `orders_daily` Code Walkthrough

## 79.1 DAG metadata

```python
@dag(
    dag_id="orders_daily",
    schedule="0 2 * * *",
    ...
)
```

defines:

```text
identity
schedule
historical behavior
ownership metadata
concurrency
```

## 79.2 Source discovery

```python
@task
def discover_sources():
```

produces the runtime list.

## 79.3 Dynamic extraction

```python
extract_source.expand(source=sources)
```

creates runtime-mapped task instances.

## 79.4 Task Group

```python
with TaskGroup(group_id="extract"):
```

organizes extraction work.

## 79.5 Transformation

```text
platform.transform
```

owns the transformation logic.

Airflow coordinates it.

## 79.6 dbt

```text
dbt build
```

owns the dbt transformation logic.

Airflow coordinates its execution.

## 79.7 Quality gate

The quality task determines whether publication is allowed.

## 79.8 Branching

The branch selects:

```text
publish
```

or:

```text
quality_failed
```

## 79.9 Teardown

The cleanup task uses an appropriate terminal-state trigger rule so resource cleanup is not accidentally dependent on every upstream task succeeding.

---

# 80. Architecture of `orders_daily`

The complete conceptual pipeline is:

```text
                         orders_daily
                              │
                              ▼
                         SETUP
                              │
                              ▼
                       SOURCE DISCOVERY
                              │
                              ▼
                    DYNAMIC EXTRACTION
                     /       |       \
                orders   customers   products
                     \       |       /
                              ▼
                        BRONZE → SILVER
                              │
                              ▼
                           DBT GOLD
                              │
                              ▼
                         QUALITY GATE
                          /         \
                       PASS         FAIL
                        |             |
                        ▼             ▼
                     PUBLISH        ALERT
                        \             /
                         \           /
                          ▼         ▼
                           TEARDOWN
```

Each stage has a clear responsibility.

---

# 81. Practical Exercise 1 — Simple DAG

## Problem

Create a DAG containing:

```text
extract
transform
publish
```

## Requirements

- Airflow 3.x style;
- clear DAG ID;
- schedule;
- timezone-aware start date;
- tags;
- dependencies.

## Expected behavior

```text
extract
   ↓
transform
   ↓
publish
```

## Solution

```python
from datetime import datetime, timezone

from airflow.sdk import dag, task


@dag(
    dag_id="simple_orders",
    schedule="0 2 * * *",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["orders"],
)
def simple_orders():

    @task
    def extract():
        return "orders"

    @task
    def transform(data):
        return f"transformed-{data}"

    @task
    def publish(data):
        print(data)

    raw = extract()
    transformed = transform(raw)
    publish(transformed)


simple_orders()
```

---

# 82. Practical Exercise 2 — Operators to TaskFlow

## Problem

Convert a Python operator workflow into TaskFlow.

## Requirements

```text
extract
→ transform
→ validate
```

## Expected behavior

Use:

```text
@task
```

and function arguments to express dependencies.

## Solution pattern

```python
@task
def extract():
    return "orders"


@task
def transform(data):
    return f"silver-{data}"


@task
def validate(data):
    print(f"validating {data}")
```

Then:

```python
raw = extract()
silver = transform(raw)
validate(silver)
```

---

# 83. Practical Exercise 3 — Jinja

## Problem

Run an interval-aware CLI.

## Requirements

Pass:

```text
data_interval_start
data_interval_end
```

## Solution

```python
BashOperator(
    task_id="transform",
    bash_command=(
        "python -m platform.transform "
        "--start '{{ data_interval_start }}' "
        "--end '{{ data_interval_end }}'"
    ),
)
```

---

# 84. Practical Exercise 4 — Task Group

## Problem

Organize:

```text
orders extraction
customer extraction
product extraction
```

into a logical group.

## Expected structure

```text
extract
├── orders
├── customers
└── products
```

The goal is readability, not hiding complexity.

---

# 85. Practical Exercise 5 — Branching

## Problem

Implement:

```text
quality passed?
   ├── yes → publish
   └── no  → alert
```

## Expected behavior

Only one business path should execute.

The non-selected path may become skipped.

Then determine the appropriate downstream trigger rules.

---

# 86. Practical Exercise 6 — Trigger Rules

## Problem

Create cleanup that should run whether the processing succeeds or fails.

## Solution concept

```text
cleanup
trigger_rule = all_done
```

The purpose is resource lifecycle management.

---

# 87. Practical Exercise 7 — Dynamic Mapping

## Problem

Extract:

```text
orders
customers
products
payments
```

without manually defining four tasks.

## Solution

```python
@task
def extract_source(source):
    print(source)


extract_source.expand(
    source=[
        "orders",
        "customers",
        "products",
        "payments",
    ]
)
```

Then ask:

```text
What happens if there are 10,000 sources?
```

The answer is:

> Mapping must be bounded and designed around scheduler, metadata, worker, and source-system capacity.

---

# 88. Practical Exercise 8 — Pool Protection

## Problem

A source API permits only three concurrent calls.

## Design

```text
mapped extraction
        ↓
source API pool = 3
```

Explain:

```text
mapping ≠ unlimited concurrency
```

---

# 89. Practical Exercise 9 — CLI Integration

## Problem

The transformation logic already exists as:

```bash
python -m platform.transform
```

Create a task that passes:

```text
data interval
```

instead of duplicating the transformation implementation.

---

# 90. Practical Exercise 10 — dbt

## Problem

Run:

```text
dbt build
```

after the silver layer succeeds.

## Expected structure

```text
silver
  ↓
dbt build
```

Airflow coordinates.

dbt transforms.

---

# 91. Practical Exercise 11 — Quality Gate

## Problem

Prevent publication when validation fails.

## Expected structure

```text
dbt
 ↓
quality
 ↓
branch
 ├── publish
 └── alert
```

---

# 92. Practical Exercise 12 — Historical Interval

## Problem

Run the same DAG definition for multiple historical intervals.

Verify that:

```text
2026-09-28
2026-09-29
2026-09-30
```

produce interval-specific processing.

The transformation should not accidentally use the wall-clock execution date.

---

# 93. Practical Exercise 13 — Idempotency

## Problem

Run the same interval twice.

Verify:

```text
no duplicates
same intended output
no corrupt state
```

Then identify which task is responsible for enforcing idempotency.

The answer should be:

> The task/data-processing implementation, not Airflow itself.

---

# 94. Practical Exercise 14 — Failure Injection

## Problem

Make one mapped extraction fail.

Observe:

```text
mapped task state
downstream behavior
quality stage
publish behavior
alert behavior
```

Document the state transitions.

---

# 95. Practical Exercise 15 — Complete `orders_daily`

Build the entire pipeline:

```text
setup
→ dynamic extraction
→ bronze/silver
→ dbt gold
→ quality
→ branch
→ publish/alert
→ teardown
```

Then test:

```text
normal run
historical run
repeated run
source failure
quality failure
```

---

# 96. Debugging Scenario 1 — DAG Does Not Appear

## Problem

The DAG source exists but the DAG does not appear operationally.

## Symptoms

```text
file exists
but DAG unavailable
```

## Investigation

```text
source location
→ DAG Processor
→ parse/import errors
→ Airflow version/API compatibility
```

## Root cause examples

```text
syntax error
bad import
version mismatch
invalid DAG construction
```

## Fix

Correct the source and verify parsing.

## Production lesson

A DAG source file existing on disk does not guarantee that Airflow successfully processed it.

---

# 97. Debugging Scenario 2 — DAG Parses Slowly

## Problem

DAG processing is slow.

## Symptoms

```text
slow DAG availability
high parser CPU
delayed scheduling visibility
```

## Investigation

Search for:

```text
network calls
database calls
heavy imports
large computations
filesystem scans
```

## Root cause

Expensive work at DAG-definition time.

## Fix

Move runtime work into tasks or imported application logic.

## Production lesson

DAG source is part of the control plane.

---

# 98. Debugging Scenario 3 — Downstream Never Starts

## Problem

A task succeeds but downstream work does not start.

## Investigation

Check:

```text
dependency
task state
trigger rule
skipped state
concurrency
pool
scheduler
```

## Root cause example

A downstream task uses:

```text
all_success
```

while an upstream branch is:

```text
skipped
```

## Fix

Choose the trigger rule that matches the intended workflow semantics.

---

# 99. Debugging Scenario 4 — Mapping Overloads the Source

## Problem

Mapped tasks overload an API.

## Symptoms

```text
HTTP 429
timeouts
source degradation
worker overload
```

## Root cause

Unlimited or insufficiently bounded concurrency.

## Fix

Use:

```text
pool
task/DAG concurrency
source-aware limits
```

## Production lesson

Dynamic mapping must be bounded.

---

# 100. Debugging Scenario 5 — Quality Failure Prevents Publish

## Problem

Quality fails.

## Expected behavior

```text
quality
   ↓
failure path
```

not:

```text
quality failed
   ↓
unsafe publish
```

## Investigation

Check:

```text
quality result
branch
trigger rules
publish dependency
```

---

# 101. Debugging Scenario 6 — Failure Notification Never Runs

## Problem

A failure alert task is unexpectedly skipped.

## Likely cause

The alert uses a success-only trigger rule.

## Fix

Use an appropriate failure-oriented trigger rule such as:

```text
one_failed
```

and reason about all upstream states.

---

# 102. Debugging Scenario 7 — Unexpected Skipped Tasks

## Problem

Branching produces many skipped tasks.

## Investigation

Determine:

```text
selected branch
non-selected branches
downstream trigger rules
```

## Root cause

The workflow designer forgot that branch decisions create skipped states.

## Production lesson

Branching and trigger rules must be designed together.

---

# 103. Debugging Scenario 8 — DAG Runs Overlap

## Problem

Two runs process the same logical resource concurrently.

## Investigation

Check:

```text
schedule
run duration
max_active_runs
task-level concurrency
pools
idempotency
```

## Fix

Use an appropriate run concurrency limit if overlap is unsafe.

---

# 104. Debugging Scenario 9 — Historical Run Processes Wrong Date

## Problem

A historical run processes today's data.

## Root cause

The task uses:

```python
datetime.now()
```

instead of the run's interval.

## Fix

Use:

```text
data_interval_start
data_interval_end
```

or an appropriate structured runtime context.

## Production lesson

Historical correctness depends on interval-aware processing.

---

# 105. Debugging Scenario 10 — Huge DataFrame in XCom

## Problem

A TaskFlow task returns a massive DataFrame.

## Why dangerous

```text
metadata storage pressure
serialization cost
slow task communication
memory usage
operational complexity
```

## Fix

Write data to:

```text
object storage
database
warehouse
```

and return:

```text
URI
table name
partition
ID
```

---

# 106. Failure Injection Lab

Perform controlled experiments.

## Experiment 1 — One mapped source fails

Make one extraction fail.

Observe:

```text
mapped instance state
downstream eligibility
quality behavior
```

## Experiment 2 — Quality gate fails

Observe:

```text
branch
publish
alert
```

## Experiment 3 — Wrong trigger rule

Deliberately choose a trigger rule that does not match the intended workflow.

Observe skipped/blocking behavior.

## Experiment 4 — Concurrent intervals

Run two intervals.

Observe:

```text
max_active_runs
task concurrency
pool behavior
```

## Experiment 5 — Remove interval inputs

Run a historical interval without passing the data interval.

Compare output behavior.

## Experiment 6 — Large XCom

Return a large object in a controlled test.

Document why it is an anti-pattern.

---

# 107. Common Mistakes

## 1. Heavy work at DAG parse time

**Why it happens:** Confusing workflow definition with execution.

**Why dangerous:** Parser and control-plane performance suffer.

**Better:** Execute expensive work in tasks.

---

## 2. Confusing task declaration with execution

**Why it happens:** TaskFlow looks like ordinary Python.

**Why dangerous:** The mental model becomes incorrect.

**Better:** Remember:

```text
DAG parse → task definition
worker runtime → task execution
```

---

## 3. Using current time instead of data interval

**Why dangerous:** Historical runs process the wrong data.

**Better:** Use interval-aware runtime context.

---

## 4. Passing large data through XCom

**Why dangerous:** Metadata and serialization become bottlenecks.

**Better:** Pass references.

---

## 5. Creating too many mapped tasks

**Why dangerous:** Scheduler, metadata DB, workers, and source systems can be overloaded.

**Better:** Bound mapping.

---

## 6. Ignoring source rate limits

**Why dangerous:** External systems can fail or throttle.

**Better:** Use pools and concurrency limits.

---

## 7. Creating one giant DAG

**Why dangerous:** Ownership, failure isolation, deployment, and observability degrade.

**Better:** One DAG per logical pipeline.

---

## 8. Meaningless Task Groups

**Why dangerous:** Groups add visual complexity without architectural meaning.

**Better:** Group by real pipeline responsibility.

---

## 9. Branching without understanding skipped states

**Why dangerous:** Downstream tasks can unexpectedly remain blocked.

**Better:** Design branching and trigger rules together.

---

## 10. Incorrect trigger rules

**Why dangerous:** Cleanup, alerting, joins, and publication can behave incorrectly.

**Better:** Explicitly model acceptable upstream states.

---

## 11. Business logic inside DAG files

**Why dangerous:** Harder to test, reuse, review, and deploy.

**Better:** Importable package/CLI logic.

---

## 12. Hard-coded secrets

**Why dangerous:** Secrets can enter source control and logs.

**Better:** Use supported Airflow/provider secret mechanisms. Topic 05 covers them in depth.

---

## 13. Ignoring timezones

**Why dangerous:** Scheduling and historical behavior become ambiguous.

**Better:** Adopt an explicit timezone policy.

---

## 14. Naive start dates

**Why dangerous:** Time interpretation can become inconsistent.

**Better:** Use timezone-aware dates.

---

## 15. Overusing Bash

**Why dangerous:** Complex shell code is difficult to test and maintain.

**Better:** Use Bash for existing CLI/system commands; use Python packages for complex application logic.

---

## 16. Using operators when TaskFlow is clearer

**Why dangerous:** Python-native workflows can become unnecessarily verbose.

**Better:** Use TaskFlow where it expresses the logic clearly.

---

## 17. Using TaskFlow for provider-native work

**Why dangerous:** You may recreate functionality already provided by a mature integration.

**Better:** Prefer a suitable provider operator when it clearly represents the external operation.

---

## 18. Ignoring idempotency

**Why dangerous:** Retries/reruns can duplicate or corrupt outputs.

**Better:** Design task operations to be deterministic and idempotent.

---

## 19. Unsafe overlapping DAG runs

**Why dangerous:** Multiple runs can modify the same resources concurrently.

**Better:** Decide explicitly whether overlap is safe and bound it when necessary.

---

## 20. Assuming Airflow guarantees data correctness

**Why dangerous:** Airflow coordinates execution; it does not automatically make business transformations correct.

**Better:** Combine orchestration with:

```text
idempotency
quality checks
data contracts
validation
observability
```

---

# 108. Production DAG Design Principles

## 1. Keep DAGs thin

```text
DAG
 ↓
coordinate
```

not:

```text
DAG
 ↓
implement entire application
```

## 2. Keep business logic outside the DAG

Use:

```text
Python package
SQL
dbt
CLI
Spark
```

## 3. Make tasks meaningful

A task should represent an operationally useful unit.

## 4. Make tasks interval-aware

Use the DAG run's intended interval.

## 5. Make tasks deterministic

Same inputs should produce the same intended result.

## 6. Make tasks idempotent

Reruns should not create incorrect duplicate effects.

## 7. Bound concurrency

Protect:

```text
source
database
worker
API
```

## 8. Use dynamic mapping carefully

Mapping is powerful but not unlimited.

## 9. Use Task Groups for logical structure

Group meaningful layers.

## 10. Use trigger rules deliberately

Model acceptable upstream states.

## 11. Keep secrets out of source

Never hard-code credentials.

## 12. Use provider integrations appropriately

Avoid rebuilding mature integrations.

## 13. Make ownership visible

Use appropriate metadata.

## 14. Avoid parse-time work

Keep DAG construction lightweight.

## 15. Keep DAGs testable

Separate business logic from orchestration.

---

# 109. Architecture Questions

## Architecture 1 — Daily Orders Pipeline

### Problem

Three source systems produce daily data.

### Requirements

```text
orders
customers
products
```

### Design

```text
dynamic extraction
→ silver
→ gold
→ quality
→ publish
```

### Reasoning

Mapping reduces repetitive DAG code.

A source-rate pool protects external systems.

### Trade-offs

More mapping improves flexibility but increases orchestration scale.

### Failure modes

Source failure, rate limiting, quality failure.

### Production considerations

Idempotency, interval-aware processing, bounded concurrency.

---

## Architecture 2 — 100 Source Tables

### Problem

100 source tables must be extracted.

### Design

Use dynamic mapping with:

```text
bounded concurrency
source pool
clear task naming
```

### Trade-off

Mapping is simpler than 100 manually authored tasks, but creates more task instances.

### Failure modes

Metadata growth and source overload.

---

## Architecture 3 — Strict API Rate Limits

### Problem

API permits only five concurrent requests.

### Design

```text
mapped extraction
      ↓
API pool = 5
```

### Production considerations

Also consider:

```text
API retry behavior
pagination
timeouts
idempotency
rate-limit responses
```

Detailed retry policy belongs to Topic 07.

---

## Architecture 4 — Quality-Gated Publication

### Problem

Publishing bad data is unacceptable.

### Design

```text
transform
   ↓
quality
   ↓
branch
 ├── pass → publish
 └── fail → alert
```

### Key concept

Publication must depend on the quality result.

---

## Architecture 5 — Historical Processing

### Problem

The pipeline must safely process old intervals.

### Design

Use:

```text
data_interval_start
data_interval_end
```

throughout the pipeline.

### Failure mode

Using wall-clock time causes historical runs to read current data.

---

## Architecture 6 — Temporary Resources

### Problem

The pipeline requires temporary staging.

### Design

```text
setup
 ↓
work
 ↓
quality
 ↓
teardown
```

### Production consideration

Teardown should remain effective for failure paths where appropriate.

---

## Architecture 7 — Quality Branching

### Problem

Only passing data should publish.

### Design

```text
quality
   ↓
branch
 ├── publish
 └── alert
```

Then design the trigger rules for joins/cleanup.

---

## Architecture 8 — dbt + Python

### Problem

Python handles ingestion/standardization and dbt handles warehouse transformation.

### Design

```text
Python CLI
   ↓
dbt build
   ↓
quality
   ↓
publish
```

Airflow coordinates.

Python/dbt implement.

---

## Architecture 9 — 100 Workflows

### Problem

A team operates many pipelines.

### Design

Use:

```text
one DAG per logical pipeline
ownership tags
consistent naming
shared package libraries
```

Avoid one giant DAG.

---

## Architecture 10 — Giant DAG Review

### Problem

One DAG contains:

```text
50 domains
200 tasks
multiple owners
multiple schedules
```

### Recommendation framework

Evaluate:

```text
logical boundaries
ownership
failure isolation
scheduling
deployment
resource domains
```

Split where the operational boundary is genuinely different.

---

# 110. Interview Questions — Basic

## 1. What is a DAG?

A DAG is a workflow definition containing tasks and dependency relationships.

## 2. What is `dag_id`?

It is the identifier used to distinguish a DAG within an Airflow environment.

## 3. What is a task?

A unit of orchestrated work.

## 4. What is an operator?

A reusable task abstraction representing a kind of operation.

## 5. What is TaskFlow?

A Python-native model for authoring Airflow tasks and dependencies using decorated Python functions.

## 6. What does `>>` mean?

It establishes a downstream dependency relationship.

## 7. What is a schedule?

It defines when workflow runs should be scheduled according to the DAG's scheduling configuration.

## 8. What is `catchup`?

It controls whether historical scheduled intervals are automatically considered for a DAG.

## 9. What is a Task Group?

A logical organizational container for related tasks.

## 10. What is dynamic task mapping?

A mechanism for generating task instances from runtime inputs.

---

# 111. Interview Questions — Moderate

## 1. Operators vs TaskFlow?

Operators are reusable operation abstractions, while TaskFlow provides Python-native function-based task authoring.

## 2. What does `@dag` do?

It defines a Python function as a DAG construction boundary.

## 3. What does `@task` do?

It converts a Python function into a TaskFlow task abstraction.

## 4. How are TaskFlow return values passed?

They commonly cross task boundaries through XCom-backed metadata.

## 5. What is Jinja?

A templating language used by Airflow to render runtime values into supported templated fields.

## 6. Why use `data_interval_start`?

It lets interval-driven tasks process the run's intended data window rather than relying on wall-clock time.

## 7. Why use `data_interval_end`?

It provides the end boundary for deterministic interval processing.

## 8. What is branching?

Conditional workflow path selection.

## 9. What is a trigger rule?

A condition describing when a downstream task is eligible based on upstream task states.

## 10. Why use pools?

To protect shared constrained resources by limiting concurrent task usage.

---

# 112. Interview Questions — Hard

## 1. What is a thin DAG?

A DAG that primarily coordinates workflow execution while business/data logic lives in reusable packages, SQL, dbt, CLIs, or other execution systems.

## 2. What are the risks of dynamic task mapping?

Too many mapped instances can overload:

```text
scheduler
metadata DB
workers
external systems
```

## 3. How do you control mapped concurrency?

Use resource-specific pools and appropriate DAG/task concurrency controls.

## 4. Why use Task Groups?

To improve logical organization and readability without pretending they are separate workflows.

## 5. Why are setup/teardown tasks useful?

They model temporary resource lifecycle and make cleanup responsibilities explicit.

## 6. Why is historical execution difficult?

Because tasks must use the run's intended interval rather than whatever date happens to be current at runtime.

## 7. How should Airflow orchestrate dbt?

Airflow should coordinate when dbt runs and what depends on it; dbt should own the transformation logic.

## 8. How should Airflow orchestrate external CLIs?

Airflow should invoke the existing CLI and provide the relevant runtime context, while the CLI owns the domain processing.

## 9. Why is idempotency important?

Because retries and reruns can otherwise produce duplicates or corrupt state.

## 10. How should a production DAG be structured?

As a thin, readable workflow with meaningful tasks, explicit dependencies, bounded concurrency, interval-aware execution, clear ownership, and reusable business logic outside the DAG.

---

# 113. Interview Questions — Advanced

## 1. How would you design a large Airflow DAG platform?

Start with:

```text
logical pipeline boundaries
ownership
task granularity
shared package architecture
resource controls
observability
```

Then scale mapping and concurrency according to actual workloads.

## 2. How do you safely map thousands of work items?

Do not start with “map thousands.”

First evaluate:

```text
source capacity
scheduler capacity
metadata volume
worker capacity
task duration
downstream fan-in
```

Then bound execution and consider whether batching is more appropriate.

## 3. How would you design a rate-limited API pipeline?

Use:

```text
dynamic mapping
+
source-specific pool
+
bounded concurrency
+
interval-aware requests
```

and make request processing idempotent.

## 4. How do trigger rules affect architecture?

They determine how downstream tasks respond to:

```text
success
failure
skipped
terminal states
```

Therefore they are part of workflow semantics, not merely task configuration.

## 5. How would you design a quality-gated pipeline?

```text
transform
 ↓
quality
 ↓
branch
 ├── pass → publish
 └── fail → alert/quarantine
```

Then verify cleanup and notification paths have appropriate trigger rules.

## 6. How do you combine TaskFlow and provider operators?

Use TaskFlow for Python-native logic and provider operators for external operations when those operators clearly express the integration.

## 7. How would you review a production DAG?

Inspect:

```text
parse-time work
task boundaries
interval handling
idempotency
XCom size
mapping scale
trigger rules
resource controls
secrets
ownership
testability
```

## 8. How do you isolate failure?

Use meaningful task boundaries, logical DAG boundaries, explicit quality gates, bounded resources, and appropriate failure paths.

## 9. How do you design reusable DAG logic?

Move domain logic into:

```text
Python packages
CLI tools
SQL
dbt
```

and keep the DAG focused on orchestration.

## 10. How would you design a reusable DAG platform?

Standardize:

```text
naming
ownership
tags
task patterns
interval handling
resource controls
logging
quality gates
deployment
review
```

while allowing domain-specific execution logic to remain in appropriate packages.

---

# 114. Final Knowledge Check

You should be able to explain:

## DAG fundamentals

- [ ] DAG ID
- [ ] schedule
- [ ] timezone-aware `start_date`
- [ ] catchup
- [ ] tags
- [ ] default arguments/configuration

## Operators

- [ ] Bash operator
- [ ] Python operator
- [ ] SQL operators
- [ ] provider operators

## Dependencies

- [ ] `>>`
- [ ] `<<`
- [ ] dependency chaining
- [ ] fan-out
- [ ] fan-in

## TaskFlow

- [ ] `@dag`
- [ ] `@task`
- [ ] Python-native task design
- [ ] task dependencies
- [ ] return values
- [ ] XCom boundary

## Templating

- [ ] Jinja
- [ ] `ds`
- [ ] `data_interval_start`
- [ ] `data_interval_end`
- [ ] `run_id`

## Organization

- [ ] Task Groups
- [ ] logical pipeline layers
- [ ] one DAG per logical pipeline
- [ ] ownership metadata

## Advanced execution

- [ ] dynamic task mapping
- [ ] `.expand()`
- [ ] `.partial()`
- [ ] branching
- [ ] short-circuiting
- [ ] trigger rules
- [ ] skipped states
- [ ] setup/teardown

## Concurrency

- [ ] `max_active_runs`
- [ ] `max_active_tasks`
- [ ] pools
- [ ] priority
- [ ] execution routing

## Integration

- [ ] Module 2.12 CLI
- [ ] interval-aware execution
- [ ] dbt
- [ ] quality gate
- [ ] publish
- [ ] source rate limits

## Production

- [ ] thin DAG principle
- [ ] importable package logic
- [ ] deterministic tasks
- [ ] idempotent tasks
- [ ] safe XCom usage
- [ ] no secrets in source
- [ ] bounded mapping
- [ ] meaningful task boundaries

## Hands-on

- [ ] complete `orders_daily`
- [ ] dynamic extraction
- [ ] task groups
- [ ] bronze → silver
- [ ] dbt gold
- [ ] quality gate
- [ ] branching
- [ ] publish
- [ ] setup/teardown
- [ ] past-date execution
- [ ] idempotency verification
- [ ] failure injection

---

# 115. Final Mental Model

```text
                 DAG DEFINITION
                       ↓
             DAG METADATA / SCHEDULE
                       ↓
                    TASKS
                       ↓
                 DEPENDENCIES
                       ↓
              TASKFLOW / OPERATORS
                       ↓
             TEMPLATED RUNTIME CONTEXT
                       ↓
          ┌────────────┴────────────┐
          ↓                         ↓
       MAPPED                    BRANCH
       TASKS                     LOGIC
          ↓                         ↓
          └────────────┬────────────┘
                       ↓
              TRIGGER RULES
                       ↓
             CONCURRENCY CONTROL
                       ↓
               TASK EXECUTION
                       ↓
       EXTERNAL SYSTEMS / CLI / DBT
```

Remember:

```text
DAG
= workflow definition.

Task
= unit of orchestrated work.

Operator
= reusable task abstraction.

TaskFlow
= Python-native task authoring model.

Dependency
= execution relationship.

Jinja
= runtime context templating.

Task Group
= logical organization.

Dynamic Mapping
= runtime-generated task instances.

Branching
= conditional workflow path.

Trigger Rule
= downstream execution condition.

Pool/Concurrency
= resource protection.

Thin DAG
= orchestration logic separated from business logic.
```

---

# 116. Scope Boundaries

This file is specifically:

```text
04-airflow-dags-operators-and-taskflow-api.md
```

It should **not** become the complete curriculum for later topics.

## Topic 05 — Connections, Variables, Hooks, XComs

XCom is explained only enough to understand TaskFlow return values and the small-metadata boundary.

Do not deeply teach:

- Connections;
- Variables;
- Hooks;
- custom XCom backends;
- secrets backends.

## Topic 06 — Sensors, Deferrable Operators, Data-Aware Scheduling

Do not deeply teach:

- sensors;
- deferrable operators;
- custom triggers;
- Asset scheduling.

## Topic 07 — Retries, Deadlines, Failure Callbacks

Do not teach the complete retry/deadline/callback curriculum here.

## Topic 08 — Backfills, Catch-up, Partitioned Runs

Catch-up and historical intervals are explained enough to author correct DAGs, but detailed backfill operations belong to Topic 08.

## Topics 09–10

Do not teach complete Dagster or Prefect implementations.

## Topic 11

Do not teach complete DAG testing/CI methodology.

The focus is:

> **How to author production-oriented Airflow DAGs using operators and TaskFlow API.**

---

# 117. Teaching Loop

For each major concept, use:

```text
What is it?
↓
Why does it exist?
↓
How does it work?
↓
Simple example
↓
Airflow code
↓
Execution behavior
↓
Failure mode
↓
Debugging
↓
Production use
↓
Trade-offs
↓
Exercise
↓
Interview question
↓
Architecture question
```

The progression should remain:

```text
basic tasks
→ dependencies
→ operators
→ TaskFlow
→ templating
→ task groups
→ mapping
→ branching
→ trigger rules
→ setup/teardown
→ concurrency
→ production pipeline
```

Do not introduce advanced mapping or trigger-rule behavior before the learner understands ordinary tasks and dependencies.

---

# 118. Final Engineering Principle

> **A production Airflow DAG should describe and coordinate the workflow, not become the workflow's entire implementation.**

A strong DAG should be:

```text
Readable
Thin
Interval-aware
Deterministic
Idempotent
Observable
Bounded
Testable
Version-controlled
Ownership-aware
```

Airflow is the orchestration layer.

The actual domain/data processing should generally live in appropriate execution systems:

```text
Python packages
SQL
dbt
Spark
APIs
Databases
Object storage
CLI applications
```

The final production mental model is:

```text
                 AIRFLOW
                    │
                    ▼
             DEFINE WORKFLOW
                    │
                    ▼
                  TASKS
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      OPERATORS            TASKFLOW
          │                   │
          └─────────┬─────────┘
                    ▼
             DEPENDENCIES
                    │
                    ▼
           RUNTIME CONTEXT
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       MAPPING             BRANCHING
          │                   │
          └─────────┬─────────┘
                    ▼
              TRIGGER RULES
                    │
                    ▼
             CONCURRENCY
                    │
                    ▼
           EXECUTION SYSTEMS
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Python      dbt       SQL
        CLI       Spark     APIs
```

The DAG coordinates.

The execution systems perform the actual work.

That separation is the foundation of production-grade Airflow DAG design.
