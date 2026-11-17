# Dagster Software-Defined Assets

> **Stage 2 — Python for Data Engineering**  
> **Module 2.13 — Orchestration and Workflow Management**  
> **Topic 09 — Dagster Software-Defined Assets**

This chapter teaches Dagster from absolute fundamentals through production-oriented Data Engineering architecture.

> **Core idea:** instead of thinking primarily `Task A → Task B → Task C`, think about the **data assets** the platform must produce, how those assets depend on one another, how they are materialized, partitioned, checked, observed, and maintained.

The supplied Topic 09 roadmap is the authoritative scope for this chapter. fileciteturn29file0L195-L267

---

## 1. Learning Objectives

By the end of this chapter you should be able to:

- explain asset-centric orchestration;
- distinguish tasks from data assets;
- define assets with `@asset`;
- model dependencies and use `deps`;
- explain materializations and metadata;
- assemble definitions with `Definitions`;
- create jobs and asset selections;
- use schedules and sensors;
- use resources and I/O managers correctly;
- design daily, static, multi-dimensional, and dynamic partitions;
- reason about partitioned backfills;
- create asset checks;
- integrate dbt assets;
- explain declarative automation;
- reason about lineage, freshness, metadata, and run history;
- explain ops/graphs and when lower-level execution structures are appropriate;
- structure a Dagster project/code location;
- use the local development workflow;
- test assets and failure modes;
- design production architecture;
- compare Airflow and Dagster philosophies without ranking them.

### Production mental model

For every asset ask:

1. What data object does this represent?
2. What does it depend on?
3. How is it materialized?
4. Where is it persisted?
5. What partition is being processed?
6. What external resource does it need?
7. What validates it?
8. What metadata explains it?
9. How fresh must it be?
10. What depends on it?
11. How do I rerun one partition?
12. How do I backfill historical partitions safely?

---

## 2. Prerequisites

You should already understand:

- Python functions and decorators;
- basic SQL and relational databases;
- ETL/ELT;
- DAGs and dependency graphs;
- scheduling;
- sensors;
- retries and failure handling;
- partitions and backfills.

Earlier Module 2.13 topics are used for comparison rather than re-taught in full.

---

# 3. Why Asset-Centric Orchestration Exists

Consider a task-oriented pipeline:

```text
extract_orders
      ↓
transform_orders
      ↓
publish_orders
```

This describes execution.

Now consider the data-oriented representation:

```text
orders_raw
      ↓
orders_bronze
      ↓
orders_silver
      ↓
orders_gold
```

This describes the durable data products.

### Task-centric question

> What work should execute, and in what order?

### Asset-centric question

> What data should exist, what does it depend on, and what is its current state?

Neither approach is universally superior.

Task-oriented execution is useful for transient work such as:

- calling an API;
- submitting a compute job;
- sending a notification;
- running a migration.

Asset-oriented modeling is particularly useful when the platform revolves around:

- tables;
- files;
- feature datasets;
- analytics products;
- partitions;
- lineage;
- freshness;
- materialization history.

### Comparison

| Concept | Task-centric | Asset-centric |
|---|---|---|
| Primary object | Work/task | Data asset |
| Dependency | Task dependency | Data dependency |
| Main question | What executes? | What data should exist? |
| Lineage | Often derived | Core concept |
| Rerun unit | Task/run | Asset/partition |
| Operational view | Task/run state | Asset/materialization state |

**Checkpoint:** If the orchestration system disappeared, what durable data objects would still matter? Those are strong asset candidates.

---

# 4. What Is a Software-Defined Asset?

A useful definition is:

> **A named data object whose production logic and dependencies are defined in code.**

Modern Dagster documentation uses the `@asset` decorator as the common entry point for defining assets. citeturn0search0

```python
import dagster as dg

@dg.asset
def orders():
    return ...
```

This definition has:

- an asset identity;
- computation;
- dependency information;
- materialization behavior;
- a place in the asset graph.

### Meaningful asset names

Prefer:

```text
orders_bronze
orders_silver
daily_revenue
customer_dimension
feature_customer_daily
```

over implementation-only names such as:

```text
run_step_3
execute_query
process_task
```

An asset should represent a meaningful data object, not every helper function.

---

# 5. `@asset`

A minimal asset:

```python
import dagster as dg

@dg.asset
def raw_orders():
    return [
        {"order_id": 1, "amount": 100},
        {"order_id": 2, "amount": 200},
    ]
```

A context-aware asset:

```python
@dg.asset
def raw_orders(context: dg.AssetExecutionContext):
    context.log.info("Materializing raw_orders")
    return ...
```

### Production boundary

Keep:

```text
Asset
 └── data/business computation

Resource
 └── external-system access

I/O manager
 └── persistence/load boundary

Asset check
 └── validation

Metadata
 └── operational context
```

Do not put the entire platform into one asset function.

---

# 6. Asset Dependencies

Dependencies form the asset graph.

```python
@dg.asset
def raw_orders():
    ...

@dg.asset
def silver_orders(raw_orders):
    ...

@dg.asset
def daily_revenue(silver_orders):
    ...
```

Dagster can infer:

```text
raw_orders
    ↓
silver_orders
    ↓
daily_revenue
```

The function parameter communicates that `silver_orders` needs the `raw_orders` asset value.

### Why dependencies matter

Correct dependencies support:

- execution ordering;
- lineage;
- impact analysis;
- targeted selection;
- automation;
- partition propagation;
- debugging.

### Hidden dependency anti-pattern

```python
@dg.asset
def silver_orders():
    return query_table("bronze_orders")
```

If the graph does not represent the important dependency, the orchestration system has less information about the true data relationship.

**Rule:** model important data dependencies explicitly.

---

# 7. `deps`

Sometimes an asset depends on another asset without consuming its value as a Python argument.

Current Dagster documentation demonstrates:

```python
@dg.asset
def upstream():
    ...

@dg.asset(deps=[upstream])
def downstream():
    ...
```

This expresses:

```text
upstream
   ↓
downstream
```

without requiring:

```python
def downstream(upstream):
```

### Function parameter vs `deps`

| Requirement | Typical approach |
|---|---|
| Consume upstream value | Function parameter |
| Graph dependency without value input | `deps` |
| Important dependency currently hidden | Make it explicit |
| No real relationship | Do not add dependency |

Use `deps` intentionally; it should communicate a real dependency, not decorate an inaccurate graph.

---

# 8. Materializations

A **materialization** is the act/result of producing or updating an asset.

```text
asset definition
      ↓
execution
      ↓
materialization
      ↓
physical data object
```

A materialization is operational evidence.

An operator may need to know:

- asset;
- partition;
- run;
- status;
- timestamp;
- metadata;
- output location;
- downstream impact.

### Materialization lifecycle

```text
select asset
   ↓
run computation
   ↓
persist result
   ↓
record materialization
   ↓
evaluate downstream state
```

A successful function execution is not the complete operational story.

---

# 9. Materialization Metadata

Useful metadata includes:

- row count;
- partition;
- source path;
- storage path;
- processing timestamp;
- processing duration;
- schema information;
- quality result.

Example conceptual event:

```text
asset: daily_revenue
partition: 2026-10-02
row_count: 12450
source: orders_silver
storage_path: ...
```

### Do not emit secrets

Never put:

- passwords;
- access tokens;
- private keys;
- connection strings containing secrets

into metadata or logs.

Metadata should explain data state without becoming a security leak.

---

# 10. `Definitions`

`Definitions` assembles the Dagster application definitions.

Conceptually:

```text
Definitions
 ├── assets
 ├── jobs
 ├── resources
 ├── schedules
 ├── sensors
 └── checks / related definitions
```

Example:

```python
import dagster as dg

@dg.asset
def raw_orders():
    ...

@dg.asset
def silver_orders(raw_orders):
    ...

defs = dg.Definitions(
    assets=[raw_orders, silver_orders],
)
```

### Why this matters

The project needs a loadable boundary for:

- assets;
- resources;
- jobs;
- schedules;
- sensors;
- checks.

This also creates an important CI validation point.

---

# 11. Jobs and Asset Selection

An asset answers:

> What data object exists and how is it computed?

A job answers:

> Which selected definitions should execute together?

Production systems need targeted execution.

Examples:

```text
daily_orders_job
finance_gold_job
customer_dimensions_job
```

### Selection can target

- one asset;
- an asset plus downstream;
- an asset plus upstream;
- a group/layer;
- a filtered graph region;
- selected partitions.

Dagster's current selection syntax supports graph-aware asset queries and job definitions. citeturn0search3

### Why selection matters

Selective execution supports:

- targeted reruns;
- debugging;
- controlled backfills;
- partial deployments;
- cost management.

**Production principle:** do not materialize the entire graph merely because one partition failed.

---

# 12. Schedules

A schedule is time-driven orchestration.

```text
clock
 ↓
schedule evaluation
 ↓
selected assets/job
 ↓
run
 ↓
materialization
```

A practical daily requirement might be:

```text
07:00 every day
```

### Production questions

- Which timezone?
- Which assets?
- What happens if data is late?
- What happens after downtime?
- How does the schedule interact with partitions?
- Is time really the trigger, or is data readiness the trigger?

A schedule is appropriate when cadence is the primary requirement.

It should not be used simply because it is familiar.

---

# 13. Sensors

A sensor reacts to a condition.

```text
condition
   ↓
sensor evaluation
   ↓
decision
   ↓
run request
```

Examples:

- new file;
- upstream event;
- API job completion;
- external state;
- partition availability.

### Schedule vs sensor

| Mechanism | Trigger | Best fit | Trade-off |
|---|---|---|---|
| Schedule | Time | Predictable cadence | May run before data exists |
| Sensor | Condition/event | Data/event-driven | Adds evaluation complexity |

### Sensor production questions

- How is readiness determined?
- How are duplicates prevented?
- What if the event never arrives?
- What deadline applies?
- What if the external system is unavailable?
- How is sensor health monitored?

Do not confuse:

```text
file exists
```

with:

```text
file is complete and valid
```

---

# 14. Resources

Resources provide reusable interfaces/configuration for external systems.

```text
Asset
  ↓
Resource
  ↓
External system
```

Examples:

- PostgreSQL;
- object storage;
- APIs;
- warehouses;
- reusable clients.

### Why resources help

Without a resource:

```python
@dg.asset
def orders():
    client = create_client(
        password="..."
    )
```

With a resource-oriented design:

```text
Asset
  ↓
configured resource
  ↓
external service
```

Benefits include:

- environment separation;
- dependency injection;
- testability;
- reusable configuration;
- controlled connection setup.

### Resource boundary

A resource should generally provide infrastructure access.

It should not become:

```text
Resource
 └── all business transformation logic
```

Keep transformation logic in assets.

---

# 15. PostgreSQL Resource Lab

Architecture:

```text
Dagster Asset
     ↓
PostgreSQL Resource
     ↓
PostgreSQL
```

Design requirements:

- externalized credentials;
- environment-specific configuration;
- controlled connection lifecycle;
- test substitution;
- least privilege;
- clear failure behavior.

Conceptual usage:

```python
@dg.asset
def source_orders(postgres):
    return postgres.query(
        "select order_id, amount from orders"
    )
```

The exact resource class depends on the selected integration/version.

### Failure injection

Break PostgreSQL availability and investigate:

1. resource initialization;
2. network;
3. credentials;
4. database health;
5. connection limits.

Do not replace a production failure with fake data.

---

# 16. Object-Storage Resource Lab

Conceptual architecture:

```text
Asset
  ↓
Object-storage resource/client
  ↓
Bucket
  ↓
Object
```

Separate:

```text
bucket
prefix
environment
credentials
client configuration
```

from transformation logic.

For partitioned data:

```text
orders_silver/
  date=2026-10-01/
  date=2026-10-02/
```

The exact physical layout is a storage-design choice.

---

# 17. Resources vs Direct Clients

Libraries such as:

```python
psycopg
boto3
requests
```

can sometimes be used directly.

Use a resource when it materially improves:

- reuse;
- configuration;
- dependency injection;
- testing;
- lifecycle management.

Do not create abstractions merely to create abstractions.

| Situation | Direct client | Resource |
|---|---:|---:|
| One tiny use | Often fine | Optional |
| Shared configuration | Less convenient | Strong fit |
| Many assets | Repetition | Strong fit |
| Test substitution | Manual | Natural |
| Complex lifecycle | Harder | Often clearer |

---

# 18. I/O Managers

An I/O manager controls how asset inputs and outputs are stored and loaded.

```text
Asset computation
      ↓
I/O manager
      ↓
Storage
```

and:

```text
Upstream asset
      ↓
I/O manager
      ↓
Downstream asset
```

### Resource vs I/O manager

**Resource:**

> How do I interact with an external service?

**I/O manager:**

> How are asset inputs and outputs persisted and loaded?

### Why use one?

It can centralize:

- serialization;
- deserialization;
- storage paths;
- partition-aware persistence;
- loading behavior.

Do not put business transformations into an I/O manager.

Current Dagster documentation also makes clear that I/O managers are not mandatory for every modern asset pattern; choose them where the persistence abstraction provides value.

---

# 19. Simple I/O Manager Example

Illustrative structure:

```python
import dagster as dg

class SimpleIOManager(dg.IOManager):
    def handle_output(self, context, obj):
        path = self._path_for(context)
        # serialize obj to path
        ...

    def load_input(self, context):
        path = self._path_for(context)
        # deserialize
        return ...

    def _path_for(self, context):
        # Build a deterministic asset/partition path.
        ...
```

The exact storage implementation is deliberately omitted.

### Production concerns

- deterministic paths;
- partition isolation;
- serialization compatibility;
- overwrite semantics;
- atomic writes;
- retention;
- permissions;
- recovery from partial writes.

---

# 20. Partitions

A partition is a defined slice of an asset.

```text
orders_daily
├── 2026-10-01
├── 2026-10-02
├── 2026-10-03
└── ...
```

Partitions enable:

- incremental processing;
- targeted reruns;
- failure isolation;
- historical backfills;
- selective materialization.

The roadmap requires four forms:

1. daily/time partitions;
2. static partitions;
3. multi-dimensional partitions;
4. dynamic partitions.

Current Dagster documentation describes time-based, category-based, two-dimensional, and dynamic partitioning. citeturn0search8

---

# 21. Daily Partitions

Conceptually:

```python
daily = dg.DailyPartitionsDefinition(
    start_date="2026-01-01"
)

@dg.asset(partitions_def=daily)
def orders_silver(context: dg.AssetExecutionContext):
    partition = context.partition_key
    ...
```

### Production contract

Define:

- business timezone;
- boundary semantics;
- source window;
- partition key;
- output location;
- late-data behavior.

For example:

```text
partition = 2026-10-02
```

should map deterministically to the intended business-day data.

### Partition-aware SQL

```sql
SELECT *
FROM orders
WHERE order_date = :partition_date;
```

Do not accidentally process the entire table for one selected partition.

---

# 22. Static Partitions

Static partitions use a known set of keys.

```text
region
├── us
├── eu
└── apac
```

Good candidates:

- region;
- fixed business domain;
- known source system;
- stable category.

The partition key represents the category rather than time.

---

# 23. Multi-Dimensional Partitions

Example:

```text
date × region
```

creates:

```text
2026-10-01 × us
2026-10-01 × eu
2026-10-02 × us
2026-10-02 × eu
```

Useful when both dimensions are operationally meaningful.

### Cost of complexity

More dimensions mean more:

- partitions;
- mappings;
- storage paths;
- backfill combinations;
- operational states.

Use multi-dimensional partitions because the data model requires them, not because the feature exists.

---

# 24. Dynamic Partitions

Dynamic partitions support key spaces that change over time.

```text
new tenant
   ↓
partition registered
   ↓
asset can process tenant
```

Examples:

- tenants;
- customers;
- newly onboarded sources.

### Governance

Define:

- who creates keys;
- how keys are validated;
- how keys are removed;
- retention;
- backfill behavior;
- disabled-tenant behavior.

Dynamic does not mean ungoverned.

---

# 25. Partitioned Asset Dependencies

Partition mappings are not always one-to-one.

### One-to-one

```text
orders[day]
   ↓
silver[day]
```

### Many-to-one

```text
daily[01]
daily[02]
daily[03]
   ↓
monthly[month]
```

### Many-to-many

Regional/global models can require multiple upstream partitions.

For every partitioned edge document:

```text
upstream partition
       ↓
mapping rule
       ↓
downstream partition(s)
```

Incorrect partition mappings are correctness bugs.

---

# 26. Partitioned Backfills

A partitioned backfill is historical materialization of selected partitions.

```text
asset
 ↓
selected partitions
 ↓
materialization
 ↓
validation
```

Reasons include:

- corrected transformation logic;
- missing historical data;
- source corrections;
- newly created assets.

### Safe backfill checklist

Before launching:

- identify exact partitions;
- verify upstream availability;
- understand overwrite semantics;
- bound concurrency;
- assess external-system load;
- define validation;
- define failure recovery;
- understand downstream impact.

### 30-partition exercise

```text
orders_daily
2026-09-01 → 2026-09-30
```

Practice:

1. materialize one partition;
2. materialize the range;
3. inject one failure;
4. rerun only that partition;
5. validate output;
6. inspect lineage.

Do not fabricate runtime numbers.

---

# 27. Asset Checks

Asset checks validate expectations about assets.

```text
Asset
 ↓
Materialization
 ↓
Asset Check
 ↓
Pass / Fail
```

Examples:

- uniqueness;
- non-empty output;
- row-count bounds;
- null-rate constraints;
- freshness;
- schema expectations;
- business rules.

### Example

```text
orders_silver
     ↓
unique(order_id)
     ↓
check
     ↓
pass/fail
```

A critical check should have an operational response.

For example:

```text
check fails
    ↓
do not blindly publish downstream
    ↓
investigate
```

An asset check is not automatically a replacement for a complete data-quality platform.

---

# 28. Asset Checks vs Data-Quality Frameworks

Relevant systems include:

- Pandera;
- Great Expectations;
- Soda;
- SQL-based checks.

The architectural relationship can be:

```text
data-quality implementation
          ↓
asset check result
          ↓
Dagster operational state
```

Use Dagster checks for orchestration-integrated validation.

Avoid duplicating the same rule in many systems without a reason.

---

# 29. dbt Integration

Dagster can represent dbt models in its asset graph.

```text
Dagster
   ↓
dagster-dbt
   ↓
dbt models
   ↓
asset graph
```

Modern integration uses concepts including:

- `@dbt_assets`;
- `DbtCliResource`;
- `DbtProject`.

Older tutorials may show APIs that are no longer current. Current Dagster changelog documentation explicitly notes removal of older dbt asset-loading APIs in favor of modern patterns. citeturn0search1

### Conceptual graph

```text
bronze_orders
    ↓
dbt staging
    ↓
dbt intermediate
    ↓
dbt revenue
```

The purpose is not simply to "run dbt from Dagster." The purpose is to place dbt data products into a broader asset-oriented graph.

---

# 30. Declarative Automation

Declarative automation describes when assets should materialize based on asset state and dependencies.

```text
upstream updated
       ↓
downstream eligible
       ↓
automation condition
       ↓
materialize
```

### Imperative

```text
run A
then run B
then run C
```

### Declarative

```text
B depends on A.
When the required state is satisfied,
B becomes eligible.
```

Modern Dagster uses `AutomationCondition` for declarative automation. The exact condition should always be checked against the pinned Dagster version. Dagster's changelog documents the evolution of this system and deprecation of older auto-materialization APIs. citeturn1search0

### Declarative does not remove engineering

You still need:

- correct dependencies;
- correct partitions;
- idempotent computation;
- checks;
- observability;
- failure handling;
- concurrency controls.

---

# 31. Metadata, Lineage, Freshness, and Run History

These concepts form the operational picture.

### Metadata

> What do we know about this materialization?

### Lineage

> Where did it come from and what depends on it?

```text
raw
 ↓
bronze
 ↓
silver
 ↓
gold
```

### Freshness

> Is it current enough for its intended use?

```text
gold_revenue
expected by 07:00
```

### Run history

> What happened over time?

```text
run-101 → success
run-102 → failure
run-103 → success
```

### Debugging path

```text
stale asset
   ↓
partition
   ↓
run history
   ↓
upstream lineage
   ↓
metadata/checks
   ↓
resource failure
   ↓
targeted recovery
```

Freshness is not the same as correctness:

```text
fresh but wrong
```

and:

```text
correct but stale
```

are both possible.

---

# 32. Ops/Graphs and When They Are Needed

Dagster also provides lower-level execution concepts such as ops and graphs.

### Ops

Represent units of computation/execution.

### Graphs

Compose computational units.

### Relationship

```text
Assets
  = data-product abstraction

Ops/Graphs
  = execution/computation abstraction
```

### Prefer assets when

- durable data products are primary;
- lineage matters;
- materialization matters;
- partitions matter;
- downstream relationships are data relationships.

### Consider ops/graphs when

- execution logic is complex;
- work is transient;
- no meaningful durable data object exists;
- reusable lower-level computational structure is needed.

Do not model every internal helper as an asset.

---

# 33. Project Structure and Code Locations

A production-oriented organization might be:

```text
dagster_project/
├── pyproject.toml
├── src/
│   └── dagster_project/
│       ├── definitions.py
│       ├── assets/
│       │   ├── bronze.py
│       │   ├── silver.py
│       │   └── gold.py
│       ├── resources/
│       ├── checks/
│       └── jobs/
└── tests/
```

This is an educational structure, not a mandatory layout.

### Why boundaries matter

Separate:

- asset computation;
- resources;
- checks;
- orchestration definitions;
- tests.

A **code location** is a deployment/discovery boundary through which Dagster loads definitions.

Avoid one enormous source file.

---

# 34. Local Development

Current Dagster documentation uses the `dg` CLI for modern local development and documents `dg dev` as launching the local webserver/daemon environment. The project roadmap names `dagster dev`; use the command exposed by the project's pinned version rather than assuming CLI compatibility. citeturn0search4turn0search6

Development loop:

```text
edit
 ↓
reload definitions
 ↓
inspect asset graph
 ↓
materialize
 ↓
inspect logs/metadata
 ↓
test/fix
```

Use local development to inspect:

- assets;
- graph;
- materializations;
- runs;
- logs;
- checks;
- schedules;
- sensors.

Local development is not the production deployment architecture.

---

# 35. End-to-End Bronze → Silver → Gold Lab

Target:

```text
Bronze Orders
      ↓
Silver Orders
      ↓
Gold Revenue
```

### Asset definitions

```python
import dagster as dg

@dg.asset
def bronze_orders():
    ...

@dg.asset
def silver_orders(bronze_orders):
    ...

@dg.asset
def gold_revenue(silver_orders):
    ...
```

### Definitions

```python
defs = dg.Definitions(
    assets=[
        bronze_orders,
        silver_orders,
        gold_revenue,
    ],
)
```

Extend the lab with:

- PostgreSQL resource;
- object-storage I/O;
- daily partitions;
- asset checks;
- metadata;
- schedule or sensor;
- lineage;
- freshness;
- dbt integration;
- declarative automation.

### Expected graph

```text
bronze_orders
      ↓
silver_orders
      ↓
gold_revenue
```

---

# 36. PostgreSQL Lab

Design:

```text
Dagster Asset
     ↓
Postgres Resource
     ↓
PostgreSQL
```

Test:

- valid connection;
- unavailable database;
- invalid credentials;
- permission failure;
- query failure;
- schema drift.

Recovery:

```text
failure
 ↓
identify external dependency
 ↓
restore
 ↓
rerun affected asset/partition
```

Never hard-code credentials.

---

# 37. Object-Storage I/O Lab

Design:

```text
Asset
 ↓
I/O Manager
 ↓
Object Storage
```

For:

```text
orders_silver
partition=2026-10-02
```

use deterministic partition-aware storage semantics such as:

```text
orders_silver/date=2026-10-02/
```

Test:

- write;
- read;
- partition isolation;
- overwrite behavior;
- missing object;
- unavailable storage;
- permission failure.

---

# 38. Asset Check Lab

Implement conceptual checks for:

```text
orders_silver
```

including:

- unique `order_id`;
- non-empty result;
- acceptable row count;
- freshness.

For each check define:

```text
measurement
failure condition
metadata
operational response
ownership
```

Do not re-teach the complete data-quality curriculum here.

---

# 39. Sensor Lab

Scenario:

```text
Partner data arrives
       ↓
Sensor detects readiness
       ↓
Run request
       ↓
Bronze asset
```

Readiness should be more meaningful than "file exists" when necessary.

For example:

```text
file exists
+
done marker
+
stable size
+
valid schema
```

Define late-data behavior and duplicate prevention.

---

# 40. dbt Lab

Target:

```text
Bronze
  ↓
dbt staging
  ↓
dbt intermediate
  ↓
dbt gold
```

Validate:

- asset representation;
- asset keys;
- dependencies;
- materialization;
- selection;
- dbt failures;
- test/check integration.

Keep the scope focused on Dagster/dbt integration.

---

# 41. Declarative Automation Lab

Target behavior:

```text
Bronze updated
      ↓
Silver eligible
      ↓
Silver materializes
      ↓
Gold eligible
      ↓
Gold materializes
```

Reason about:

- dependency state;
- missing partitions;
- upstream updates;
- failed checks;
- stale assets;
- unnecessary repeated materialization.

Do not hard-code version-specific automation APIs without checking the project's pinned version.

---

# 42. Partitioned Backfill Lab

Create:

```text
30 daily partitions
```

Practice:

1. materialize one partition;
2. materialize a range;
3. inject one failed partition;
4. rerun only the failed partition;
5. validate;
6. inspect lineage and metadata.

Then design a:

```text
180-day backfill
```

with bounded concurrency, validation, and recovery.

Do not fabricate runtime/cost numbers.

---

# 43. Failure Injection Lab

Inject at least:

1. PostgreSQL unavailable;
2. object storage unavailable;
3. asset computation exception;
4. asset check failure;
5. missing partition;
6. incorrect partition key;
7. invalid upstream dependency;
8. dbt model failure;
9. resource configuration error;
10. sensor condition never occurs.

For each failure document:

```text
symptom
cause
where to look
recovery
prevention
test that should catch it
```

### General debugging flow

```text
Failure
  ↓
Definition?
  ├── yes → fix/validate
  └── no
       ↓
Resource/I/O?
  ├── yes → inspect dependency
  └── no
       ↓
Partition?
  ├── yes → inspect key/mapping
  └── no
       ↓
Computation?
  ├── yes → inspect logs/tests
  └── no
       ↓
Check/automation?
```

---

# 44. Testing Dagster Assets

### Unit tests

Test asset computation and business logic.

### Resource tests

Test external-system interfaces using fakes, mocks, or local services.

### Asset-check tests

Test:

```text
valid → pass
invalid → fail
```

### Partition tests

Test:

```text
partition key
→ expected input window
→ expected output
```

Include boundary/timezone cases.

### Integration tests

Use appropriate local infrastructure such as:

```text
Docker PostgreSQL
MinIO/object storage
dbt project
```

### Definitions validation

Verify that:

- assets load;
- jobs load;
- resources resolve;
- schedules load;
- sensors load;
- checks load.

### CI progression

```text
Lint
 ↓
Definitions validation
 ↓
Unit tests
 ↓
Asset checks
 ↓
Integration tests
 ↓
Deployment validation
```

Topic 11 covers broader orchestration testing; this section focuses on Dagster assets.

---

# 45. Production Recovery Design

### Asset computation failure

Rerun the affected asset/partition after fixing the cause.

### Resource failure

Restore the external dependency and rerun affected work.

### Asset check failure

Do not blindly publish downstream data.

### Partition failure

Isolate and rerun the affected partition.

### dbt failure

Inspect the failing model/dependency and rerun the appropriate selection.

### Sensor failure

Inspect both sensor evaluation and the external readiness condition.

The production principle is:

> **Recover the smallest safe scope supported by the evidence.**

---

# 46. Resource and Cost Management

Cost drivers include:

- unnecessary materialization;
- large backfills;
- excessive partitions;
- database load;
- object-storage operations;
- external API calls;
- concurrency.

Asset selection can be a cost-control mechanism:

```text
identify affected assets
        ↓
identify affected partitions
        ↓
select required scope
        ↓
materialize
```

Never claim exact savings without measurements.

If benchmarking:

```text
environment
workload
methodology
limitations
```

must be documented.

---

# 47. Airflow vs Dagster Perspective

Remain neutral.

### Airflow commonly emphasizes

- tasks;
- DAGs;
- operators;
- scheduling;
- task dependencies;
- explicit workflow control;
- broad ecosystem.

### Dagster emphasizes

- software-defined assets;
- asset graph;
- materializations;
- lineage;
- partitions;
- asset checks;
- declarative automation.

### Same data pipeline

```text
raw_orders
   ↓
silver_orders
   ↓
gold_revenue
```

An Airflow implementation may center the execution tasks that create those outputs.

A Dagster implementation can make the outputs themselves the primary orchestration objects.

### Choice depends on

- team experience;
- pipeline style;
- asset-centric requirements;
- ecosystem;
- deployment model;
- operational requirements;
- existing infrastructure.

Do not rank them.

---

# 48. Production Architecture

Conceptual architecture:

```text
                   ┌───────────────────────┐
                   │   Dagster Instance    │
                   └───────────┬───────────┘
                               │
                     ┌─────────┴─────────┐
                     ↓                   ↓
                  Assets             Schedules
                     │                   │
                     ↓                   ↓
                Asset Graph          Sensors
                     │
            ┌────────┼─────────┐
            ↓        ↓         ↓
         Resource   I/O      Checks
            │       Manager      │
            ↓        ↓           ↓
       PostgreSQL  Storage     Quality
            │        │
            └────────┴───────────┐
                                 ↓
                              Data Assets
```

Design:

- orchestration layer;
- asset definitions;
- resources;
- persistence;
- checks;
- scheduling;
- sensors;
- lineage;
- metadata;
- secrets;
- deployment;
- observability;
- concurrency;
- recovery.

---

# 49. Production Asset Design Principles

1. Name assets clearly.
2. Keep computation focused.
3. Make dependencies explicit.
4. Keep resources reusable.
5. Separate persistence from computation.
6. Make partition semantics explicit.
7. Validate outputs.
8. Emit useful metadata.
9. Avoid unnecessary recomputation.
10. Design for reruns.
11. Keep secrets externalized.
12. Test definitions in CI.
13. Design lineage intentionally.
14. Define freshness expectations.
15. Treat backfills as controlled production operations.

---

# 50. Common Anti-Patterns

### 1. Every task becomes an asset

**Problem:** meaningless asset graph.

**Better:** expose meaningful data products.

### 2. Hard-coded secrets

**Problem:** security risk.

**Better:** resources/external configuration.

### 3. Hidden dependencies

**Problem:** incorrect lineage/automation.

**Better:** function dependency or `deps`.

### 4. Hard-coded storage paths

**Problem:** partition/environment collisions.

**Better:** deterministic configured persistence.

### 5. Business logic in resources

**Problem:** poor separation.

**Better:** resource = external access; asset = computation.

### 6. Business logic in I/O manager

**Problem:** persistence layer becomes transformation layer.

**Better:** I/O manager = persistence/load.

### 7. Ignoring partition boundaries

**Problem:** wrong data slice.

**Better:** test partition semantics.

### 8. Materializing everything

**Problem:** unnecessary work.

**Better:** asset selection.

### 9. No checks for critical data

**Problem:** invalid data propagates.

**Better:** asset checks with defined response.

### 10. Overusing sensors

**Problem:** unnecessary control-loop complexity.

**Better:** use schedules/dependencies/declarative automation where appropriate.

### 11. Monolithic assets

**Problem:** poor testing and recovery.

**Better:** coherent data-product boundaries.

### 12. Non-idempotent computation

**Problem:** unsafe reruns/backfills.

**Better:** deterministic, rerunnable design.

---

# 51. Code Review Exercises

For each example: identify the issue, explain impact, provide corrected design, explain the reasoning.

### Bad 1 — password in asset

```python
@dg.asset
def orders():
    password = "real-password"
```

Correct direction:

```text
Asset
 ↓
configured resource
 ↓
external credentials
```

### Bad 2 — persistence everywhere

```python
@dg.asset
def silver():
    data = transform(...)
    write_to_s3(data, "hard-coded/path")
    return data
```

Correct direction:

```text
Asset computation
+
appropriate persistence abstraction
```

### Bad 3 — hidden dependency

```python
@dg.asset
def silver():
    return query_table("bronze_orders")
```

Correct direction:

```text
explicit dependency
```

### Bad 4 — partition ignored

```python
@dg.asset(partitions_def=daily)
def orders(context):
    return read_entire_year()
```

Correct direction:

```text
partition key/window
        ↓
correct source slice
```

### Bad 5 — giant asset

```text
ingest
clean
aggregate
publish
validate
notify
```

all inside one asset.

Correct direction:

```text
coherent durable data products
+
implementation-level internal steps where appropriate
```

### Bad 6 — no revenue checks

Correct direction:

```text
gold_revenue
    ↓
critical checks
    ↓
safe publication
```

### Bad 7 — resource owns transformations

Correct direction:

```text
Asset → transformation
Resource → external access
```

### Bad 8 — every run materializes everything

Correct direction:

```text
change surface
 ↓
asset selection
 ↓
targeted materialization
```

---

# 52. Architecture Exercises

1. Design a bronze/silver/gold asset graph.
2. Design daily partitioned assets.
3. Design a multi-region asset.
4. Design a PostgreSQL-backed asset.
5. Design object-storage I/O.
6. Design revenue asset checks.
7. Design sensor-driven partner ingestion.
8. Design dbt integration.
9. Design declarative downstream materialization.
10. Design a 180-day partition backfill.
11. Decide whether a workflow belongs in assets or ops/graphs.
12. Compare the same pipeline in Airflow and Dagster without ranking them.

For every architecture exercise explain:

- data products;
- dependencies;
- partitions;
- resources;
- persistence;
- checks;
- triggering;
- failure recovery;
- testing;
- observability.

---

# 53. Progressive Practical Exercises

## Beginner

- create a simple asset;
- create an upstream/downstream graph;
- use `Definitions`;
- materialize an asset;
- inspect metadata.

## Intermediate

- add PostgreSQL resource;
- add object-storage I/O;
- create asset checks;
- create a schedule;
- create a sensor;
- create daily partitions.

## Advanced

- create multi-dimensional partitions;
- create dynamic partitions;
- perform a partitioned backfill;
- integrate dbt;
- emit asset metadata;
- design declarative automation.

## Expert / Production

Design:

```text
SFTP/API
   ↓
Bronze Asset
   ↓
Silver Asset
   ↓
dbt Gold
   ↓
Asset Checks
   ↓
Published Data Product
```

with:

- resources;
- I/O manager;
- partitions;
- sensor;
- checks;
- lineage;
- freshness;
- tests;
- production deployment considerations.

---

# 54. Final Practical Challenge

A company receives orders from:

```text
SFTP / API / PostgreSQL
          ↓
       Bronze
          ↓
       Silver
          ↓
        Gold
          ↓
      Analytics
```

Requirements:

- asset-oriented design;
- daily partitions;
- PostgreSQL resource;
- object-storage persistence;
- asset checks;
- dbt integration;
- sensor-driven ingestion;
- declarative downstream materialization;
- metadata;
- lineage;
- freshness visibility;
- partitioned backfills;
- selective reruns;
- testing;
- production observability.

### Design deliverables

1. asset graph;
2. asset identities;
3. dependency strategy;
4. resource design;
5. I/O strategy;
6. partition strategy;
7. check strategy;
8. schedule/sensor strategy;
9. declarative automation;
10. dbt integration;
11. metadata;
12. lineage;
13. freshness;
14. backfill strategy;
15. selective rerun strategy;
16. testing;
17. production deployment;
18. operational checklist.

### Expected architecture

```text
Sources
  │
  ├── SFTP
  ├── API
  └── PostgreSQL
        │
        ↓
  Bronze Assets
        ↓
  Silver Assets
        ↓
    dbt Gold
        ↓
  Asset Checks
        ↓
Published Data Product
```

### Expected operational controls

```text
Partitions
Resources
I/O
Checks
Sensors
Schedules
Declarative Automation
Metadata
Lineage
Freshness
Backfills
Tests
Observability
```

---

# 55. Relationship to Other Module 2.13 Topics

### Topic 01

DAGs and scheduling concepts provide the graph foundation.

### Topic 04

Airflow DAGs/operators/TaskFlow provide the task-centric comparison.

### Topic 06

Sensors and data-aware scheduling explain trigger mechanisms.

### Topic 07

Retries/failure handling provide broader recovery context.

### Topic 08

Backfills and partitioned runs provide the historical-processing foundation.

### Topic 10

Prefect provides a separate orchestration philosophy for comparison.

### Topic 11

Testing/validation provides the broader testing context.

Do not duplicate those chapters. Use them for conceptual connections.

---

# 56. Relationship to Earlier Data Engineering Modules

### Module 2.9 — Data Ingestion

```text
Ingestion
   ↓
Bronze Asset
```

### Module 2.11 — Data Validation and Quality

```text
Asset
 ↓
Validation
 ↓
Asset Check / quality system
```

### Module 2.12 — Transformation Patterns and Pipeline Design

```text
Ingestion
   ↓
Asset
   ↓
Transformation
   ↓
Asset
   ↓
Quality
   ↓
Published Asset
```

Dagster provides orchestration around these data-engineering practices; it does not replace them.

---

# 57. Learning Checkpoints

After each major concept, ask:

- What does this asset represent?
- What data does it produce?
- What does it depend on?
- When is it materialized?
- Where is it stored?
- What resource does it need?
- How is its output persisted?
- What partition is being processed?
- What happens if the asset check fails?
- How would you rerun one partition?
- How would you backfill 30 partitions?
- How would you know the asset is stale?
- How would you trace upstream lineage?
- When would you use an op/graph instead?
- When might Airflow's task-centric model fit the problem?

These questions test engineering reasoning rather than memorization.

---

# 58. Observability Checklist

Monitor or inspect:

| Signal | Operational purpose |
|---|---|
| Asset materialization history | Proves when data was produced |
| Partition state | Finds missing/failed slices |
| Asset metadata | Explains output characteristics |
| Run status | Shows execution outcome |
| Asset checks | Shows validation state |
| Freshness | Shows timeliness |
| Upstream/downstream lineage | Supports root cause and impact analysis |
| Sensor status | Shows event-driven health |
| Schedule status | Shows time-driven health |
| Backfill status | Shows historical recovery state |
| Resource failures | Shows external-system problems |

The operator should be able to move from:

```text
stale asset
   ↓
partition
   ↓
run
   ↓
upstream
   ↓
resource/check
   ↓
recovery
```

without guessing.

---

# 59. Testing and Validation Checklist

Validate:

- [ ] asset definitions;
- [ ] dependency graph;
- [ ] `Definitions`;
- [ ] resources;
- [ ] I/O managers;
- [ ] partition behavior;
- [ ] asset checks;
- [ ] schedules;
- [ ] sensors;
- [ ] dbt integration;
- [ ] materialization behavior;
- [ ] failure behavior;
- [ ] selective reruns;
- [ ] backfills.

### Validation hierarchy

```text
Python works
   ↓
Definitions load
   ↓
Graph is correct
   ↓
One asset works
   ↓
One partition works
   ↓
Checks work
   ↓
Integration works
   ↓
Recovery works
```

---

# 60. Production Review Checklist

## Asset modeling

- [ ] Meaningful asset names.
- [ ] Coherent asset boundaries.
- [ ] No meaningless task-as-asset conversion.
- [ ] No giant monolithic asset.

## Dependencies

- [ ] Explicit dependencies.
- [ ] Correct `deps`.
- [ ] Correct lineage.
- [ ] Correct partition mapping.

## Infrastructure

- [ ] Secrets externalized.
- [ ] Resources have clear ownership.
- [ ] I/O persistence is deterministic.
- [ ] Environment separation is explicit.

## Partitions

- [ ] Business timezone defined.
- [ ] Boundary semantics defined.
- [ ] Partition storage isolated.
- [ ] Backfill strategy documented.

## Quality

- [ ] Critical checks defined.
- [ ] Failure response defined.
- [ ] Freshness expectation defined.

## Operations

- [ ] Run history inspectable.
- [ ] Metadata useful.
- [ ] Sensors monitored.
- [ ] Schedules monitored.
- [ ] Backfills bounded.
- [ ] Targeted reruns documented.

## Testing

- [ ] Definitions validated in CI.
- [ ] Unit tests.
- [ ] Resource tests.
- [ ] Partition tests.
- [ ] Check tests.
- [ ] Integration tests.
- [ ] Failure injection.

---

# 61. Exactly 40 Interview Questions

## 10 Basic

### 1. What is a software-defined asset?

A named data object whose production logic and dependencies are defined in code.

### 2. What does `@asset` do?

It declares a Python function as a Dagster asset definition.

### 3. What is an asset dependency?

A relationship describing which upstream data an asset relies on.

### 4. What is `deps`?

An explicit way to declare an asset dependency when the upstream value is not represented as a function argument.

### 5. What is a materialization?

The act/result of producing or updating an asset.

### 6. What is an asset graph?

A graph of assets and their dependencies.

### 7. What is `Definitions`?

The assembly boundary for assets and other Dagster definitions.

### 8. What is an asset job?

An execution boundary that targets a selected set of assets.

### 9. What is an asset selection?

A graph-aware query describing which assets should be targeted.

### 10. What is a resource?

A reusable interface/configuration boundary for an external system or service.

## 10 Moderate

### 11. When should a function parameter be used instead of `deps`?

When the downstream computation consumes the upstream asset value.

### 12. Why is materialization metadata useful?

It provides operational context such as partition, row count, source, and storage information.

### 13. Why use partitions?

To process and operate on independently addressable slices of an asset.

### 14. What is a static partition?

A partition from a predefined finite key set.

### 15. What is a dynamic partition?

A partition key from a set that can evolve at runtime.

### 16. What is a multi-dimensional partition?

A partition combining dimensions such as date and region.

### 17. What is a partitioned backfill?

Historical materialization of selected partitions.

### 18. How does a schedule differ from a sensor?

A schedule is time-driven; a sensor is condition/event-driven.

### 19. What is an I/O manager?

A persistence/load abstraction for asset inputs and outputs.

### 20. How does an I/O manager differ from a resource?

A resource provides external-service access; an I/O manager handles asset persistence/loading.

## 10 Hard

### 21. Why is asset-centric orchestration useful for analytics platforms?

Because durable data products, dependencies, materializations, partitions, checks, lineage, and freshness become first-class operational concepts.

### 22. How would you design a daily partitioned asset?

Define business-time semantics, partition definition, source window, partition-aware processing, deterministic output, and boundary tests.

### 23. Why are partition mappings difficult?

Because upstream and downstream assets can have one-to-one, one-to-many, or many-to-one relationships.

### 24. How would you safely backfill 180 partitions?

Bound scope and concurrency, verify inputs, control external-system load, validate results, isolate failures, and understand downstream effects.

### 25. When should you use an I/O manager?

When persistence/loading benefits from a reusable abstraction for serialization, paths, partition handling, and storage access.

### 26. How should dbt be integrated?

Use the current `dagster-dbt` asset APIs and connect dbt models to the broader Dagster asset graph.

### 27. What is declarative automation?

Expressing when an asset should materialize based on state and dependencies rather than manually encoding every execution path.

### 28. Why not make every function an asset?

Because assets should represent meaningful data products; otherwise the asset graph becomes noisy and semantically weak.

### 29. How would you debug stale revenue?

Find the stale partition, inspect run history, trace upstream lineage, inspect checks/metadata/resources, then rerun the smallest safe scope.

### 30. How would you test a Dagster asset system?

Use unit, resource, partition, check, definitions, integration, dbt, and failure/recovery tests.

## 10 Advanced

### 31. How would you design bronze/silver/gold asset boundaries?

Represent meaningful durable data products, keep transformations focused, model true dependencies, define partitions and checks, and avoid exposing every internal step.

### 32. How would you design a partner-file sensor?

Define readiness, prevent duplicate launches, handle late/missing data, define deadlines, externalize credentials, test it, and monitor sensor health.

### 33. How can asset checks interact with automation?

Checks can act as validation boundaries and, where configured, prevent unsafe downstream materialization. Exact configuration is version-sensitive.

### 34. How would you design date × region partitions?

Use independent dimensions, define mappings, isolate storage, validate combinations, and bound selection/backfills.

### 35. How would you govern dynamic tenant partitions?

Use an authoritative tenant registry, validate keys, control lifecycle, and monitor partition state.

### 36. How would you prevent a large backfill from overwhelming PostgreSQL?

Bound concurrency, batch work, select only required assets, monitor database load, and coordinate with capacity limits.

### 37. How would you compare Airflow and Dagster?

Airflow commonly centers task/DAG orchestration; Dagster emphasizes software-defined assets and asset state. Choose based on team, workload, ecosystem, deployment, and operational requirements.

### 38. When are ops/graphs preferable?

When execution structure or transient computation is the primary abstraction and no meaningful durable asset should be exposed for every step.

### 39. What makes a Dagster asset platform production-grade?

Correct modeling, explicit dependencies, secure resources, deterministic persistence, partition semantics, checks, metadata, lineage, freshness, tests, recovery, and observability.

### 40. What is the key mental shift?

Start with the data objects and their lifecycle rather than starting with the task sequence.

---

# 62. Final Knowledge Checklist

You should be able to answer **YES** to:

- [ ] Can I explain software-defined assets?
- [ ] Can I explain asset-centric orchestration?
- [ ] Can I create `@asset`?
- [ ] Can I define dependencies?
- [ ] Can I use `deps`?
- [ ] Can I explain materialization?
- [ ] Can I use `Definitions`?
- [ ] Can I create jobs?
- [ ] Can I select assets?
- [ ] Can I create schedules?
- [ ] Can I create sensors?
- [ ] Can I use resources?
- [ ] Can I explain I/O managers?
- [ ] Can I distinguish resources from I/O managers?
- [ ] Can I create daily partitions?
- [ ] Can I explain static partitions?
- [ ] Can I explain multi-dimensional partitions?
- [ ] Can I explain dynamic partitions?
- [ ] Can I perform partitioned backfills?
- [ ] Can I create asset checks?
- [ ] Can I integrate dbt?
- [ ] Can I explain declarative automation?
- [ ] Can I use asset metadata?
- [ ] Can I understand lineage?
- [ ] Can I reason about freshness?
- [ ] Can I inspect run history?
- [ ] Can I explain ops/graphs?
- [ ] Can I decide between assets and ops/graphs?
- [ ] Can I design a production asset architecture?
- [ ] Can I compare Airflow and Dagster without reducing the comparison to a ranking?

---

# 63. Final Mental Model

```text
                 DATA PRODUCTS
                       │
                       ↓
              Software-Defined Assets
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
       Dependencies          Partitions
             │                   │
             └─────────┬─────────┘
                       ↓
                 Materialization
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
      Resources       I/O         Checks
          │          Manager         │
          ↓            ↓            ↓
     External       Storage       Quality
      Systems
                       │
                       ↓
                    Metadata
                       │
                       ↓
                    Lineage
                       │
                       ↓
                   Freshness
                       │
                       ↓
                  Run History
                       │
                       ↓
              Operational Decisions
```

The production principle is:

> **Model meaningful data products, make dependencies explicit, partition deliberately, separate computation from infrastructure, validate outputs, record useful metadata, expose lineage and freshness, and make historical recovery safe.**

---

# 64. Scope and Version Discipline

This chapter intentionally does **not** become:

- a complete Airflow tutorial;
- a complete Prefect tutorial;
- a complete dbt tutorial;
- a complete data-quality tutorial;
- a generic Python tutorial.

Dagster APIs evolve. Before using an example in a production repository:

1. inspect the project's pinned Dagster version;
2. inspect the corresponding official documentation;
3. verify imports/signatures;
4. run a minimal test;
5. add integration coverage for infrastructure-dependent behavior.

Do not copy obsolete tutorials simply because they appear in search results.

The official Dagster documentation currently demonstrates modern `@asset` usage and asset selection. citeturn0search0turn0search3

Current Dagster documentation/changelog also documents the modern declarative automation direction around `AutomationCondition` and the evolution away from older auto-materialization APIs. citeturn1search0

---

# 65. Source Alignment

The chapter follows the supplied Topic 09 specification and its required sequence from asset-centric motivation through production architecture and interview preparation. fileciteturn29file0L2355-L2365

The roadmap explicitly requires `@asset`, dependencies, `deps`, materializations, `Definitions`, jobs, selections, schedules, sensors, resources, I/O managers, partitions, backfills, checks, dbt integration, declarative automation, metadata, lineage, freshness, run history, ops/graphs, project/code locations, `dagster dev`, production architecture, and Airflow comparison. fileciteturn29file0L2260-L2293

The roadmap also requires exactly 40 interview questions divided into Basic, Moderate, Hard, and Advanced levels. fileciteturn29file0L1869-L1908

It requires progressive practical exercises and the SFTP/API/PostgreSQL → Bronze → Silver → Gold → Analytics final challenge. fileciteturn29file0L1912-L2025
