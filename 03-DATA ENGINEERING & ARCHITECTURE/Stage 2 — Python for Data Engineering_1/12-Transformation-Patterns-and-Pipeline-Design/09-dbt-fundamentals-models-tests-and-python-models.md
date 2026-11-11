# dbt Fundamentals, Models, Tests, and Python Models

> **Stage 2 — Python for Data Engineering**  
> **Module 2.12 — Transformation Patterns and Pipeline Design**  
> **Topic 09 — dbt Fundamentals, Models, Tests, and Python Models**

This chapter teaches dbt from absolute beginner level through production-oriented Data Engineering and Analytics Engineering practice.

The progression is:

```text
concept
→ why it exists
→ problem it solves
→ internal mechanics
→ simple example
→ realistic example
→ coding
→ testing
→ debugging
→ production usage
→ trade-offs
→ architecture
→ interview reasoning
```

The central mental model is:

```text
raw/source data
      ↓
dbt models
      ↓
tested transformation layer
      ↓
analytics-ready data
```

> **dbt primarily transforms data that already exists in a data platform.**

dbt is not a universal ingestion, orchestration, or application-processing system. Production architecture normally places dbt inside a larger data platform.

## 1. Why dbt Exists

Traditional transformation systems often start as a collection of SQL scripts. That works until the number of datasets, engineers, consumers, and deployment environments grows.

Common problems include:

- large SQL scripts;
- duplicated SQL;
- unclear dependencies;
- weak testing;
- difficult lineage;
- unclear ownership;
- poor documentation;
- transformation logic mixed together;
- difficult incremental processing;
- difficult collaboration;
- difficult deployment.

dbt addresses these problems by treating transformation logic as a managed project with models, dependencies, tests, documentation, configuration, and a dependency graph.

The basic ELT distinction is:

```text
EXTRACT
source systems → extracted data

LOAD
extracted data → warehouse/lakehouse

TRANSFORM
warehouse/lakehouse → analytics-ready datasets
```

dbt primarily lives in the transformation stage:

```text
source systems
      ↓
 ingestion
      ↓
raw / bronze
      ↓
     dbt
      ↓
staging → intermediate → marts
```

This is why dbt is commonly associated with **ELT** rather than traditional application-managed ETL.


## 2. dbt vs ETL Tools

Traditional ETL commonly looks like:

```text
source → application/process → transformed output
```

ELT looks like:

```text
source → warehouse/lakehouse → transformations
```

dbt provides a transformation-development layer around SQL and supported Python models:

```text
warehouse/lakehouse
      ↓
SQL/Python transformation definitions
      ↓
managed transformation DAG
      ↓
tested/documented datasets
```

dbt is particularly useful for:

- SQL-based transformations;
- dependency management;
- data tests;
- documentation;
- lineage;
- incremental models;
- reusable macros;
- controlled deployment workflows;
- analytics engineering conventions.

dbt is not primarily designed to:

- extract arbitrary operational data;
- manage every ingestion protocol;
- perform arbitrary external side effects;
- replace general application logic;
- replace every distributed-compute workload;
- become a universal orchestration platform.

A production system can therefore use an ingestion system, an orchestrator, dbt, a warehouse/lakehouse, observability, and CI/CD together.


## 3. Core dbt Mental Model

The core concepts are:

| Concept | Beginner definition |
|---|---|
| Project | The dbt application/project boundary |
| Model | A transformation definition |
| Source | A declaration of upstream raw data |
| `ref()` | A reference to another dbt model and dependency declaration |
| Dependency | A relationship saying one node needs another |
| DAG | Directed graph of transformations |
| Materialization | How a model becomes a database object |
| Test | A check of a data invariant |
| Seed | A small static CSV-based dataset managed by dbt |
| Snapshot | A mechanism for preserving historical versions of changing records |
| Macro | Reusable Jinja-generated SQL logic |
| Jinja | Template language used by dbt to generate SQL/configuration |
| Profile | Connection/environment configuration |
| Adapter | dbt's interface to a particular data platform |
| Target | The environment against which dbt is operating |
| Compilation | Turning dbt/Jinja definitions into executable SQL/artifacts |
| Execution | Running the resulting operations against the data platform |

The conceptual workflow is:

```text
dbt project
    ↓
models + sources + tests + macros + seeds + snapshots
    ↓
parse
    ↓
compile
    ↓
dependency graph
    ↓
execute
    ↓
warehouse/lakehouse objects
```

A critical distinction is:

```text
Jinja/dbt compilation
        ↓
compiled SQL
        ↓
database execution
```

Jinja does not execute relational SQL. The database executes the compiled SQL.


## 4. dbt Project Structure

A conventional project contains:

```text
dbt_project.yml
profiles.yml

models/
seeds/
snapshots/
macros/
tests/
analyses/
packages.yml
```

### `dbt_project.yml`

Project-level configuration describes how the project is organized and configured.

### `profiles.yml`

Connection/environment information is normally handled through profiles. Secrets should not be hard-coded into source-controlled transformation files.

### `models/`

Contains transformation model definitions and model configuration.

### `seeds/`

Contains small static CSV datasets that are intentionally managed as project data.

### `snapshots/`

Contains snapshot definitions for historical record tracking.

### `macros/`

Contains reusable Jinja macros.

### `tests/`

Contains custom/singular test SQL and related test definitions.

### `analyses/`

Contains analytical SQL that is useful for analysis but is not necessarily a materialized model.

### `packages.yml`

Declares dbt packages where package management is used.

Keep these concerns separate:

```text
project configuration
    ≠
connection profile
    ≠
model configuration
```

Environment-specific settings should be externalized appropriately, and secrets should be supplied through secure environment/credential mechanisms rather than committed to source control.


## 5. dbt Core and dbt-duckdb Local Learning Environment

The roadmap uses **dbt Core + dbt-duckdb** for local learning.

DuckDB is useful for learning because it provides a local analytical SQL engine without requiring a remote warehouse just to understand dbt concepts.

A conceptual workflow is:

```bash
dbt init
dbt debug
dbt run
dbt test
dbt build
```

These commands are not magic.

### `dbt init`

Creates the initial project structure.

### `dbt debug`

Checks important configuration/connectivity assumptions.

### `dbt run`

Builds selected dbt models.

### `dbt test`

Runs configured data tests.

### `dbt build`

Runs a broader build workflow that includes selected models and associated tests/seeds/snapshots according to dbt's build semantics.

The exact output and supported behavior can vary with dbt and adapter versions. Always verify the installed version's command behavior.


## 6. First dbt Model

A model is a transformation definition.

Example:

`models/staging/stg_orders.sql`

```sql
select
    order_id,
    customer_id,
    order_date,
    status,
    amount
from raw_orders
```

The model definition is SQL.

dbt can materialize that definition according to the configured materialization.

Conceptually:

```text
stg_orders.sql
      ↓
dbt compilation
      ↓
compiled SQL
      ↓
database execution
      ↓
database relation
```

Do not confuse:

```text
model definition
```

with:

```text
materialized relation
```

The `.sql` file is code/configuration in the dbt project. The resulting view/table/incremental relation is a database object.


## 7. `ref()` — The Core Dependency Mechanism

Instead of hard-coding a relation:

```sql
select *
from analytics.stg_orders
```


prefer:

```sql
select *
from {{ ref('stg_orders') }}
```


`ref()` does several important things:

- identifies a dependency;
- contributes to the DAG;
- allows dbt to determine execution order;
- supports environment-aware relation naming;
- improves lineage.

A realistic dependency chain is:

```text
raw_orders
    ↓
stg_orders
    ↓
int_order_lines
    ↓
fct_orders
    ↓
fct_daily_revenue
```

Hard-coded relation names hide the dependency from dbt. `ref()` makes the relationship explicit to the transformation framework.


## 8. Sources

Sources represent upstream data that exists outside dbt's model graph.

Example:

```yaml
sources:
  - name: raw
    description: Raw order-platform datasets.
    tables:
      - name: orders
        description: Raw orders arriving from the operational platform.
      - name: order_lines
        description: Raw order-line records.
```


A model can reference a source with:

```sql
select *
from {{ source('raw', 'orders') }}
```


The distinction is:

```text
source()
    = external/upstream dataset

ref()
    = another dbt model
```

Sources can carry:

- ownership information;
- descriptions;
- freshness expectations;
- tests;
- lineage metadata.

The conceptual flow is:

```text
external/raw table
      ↓ source()
staging model
      ↓ ref()
intermediate model
      ↓ ref()
mart
```


## 9. DAG and Dependency Order

A **Directed Acyclic Graph (DAG)** is a dependency graph where edges have direction and cycles are not allowed.

You can understand it without advanced graph theory:

```text
node = dataset/model
edge = dependency
```

Example:

```text
raw_orders
    ↓
stg_orders
    ↓
int_orders
    ↓
fct_orders
    ↓
fct_daily_revenue
```

dbt can use the dependency graph to determine which upstream models must be available before downstream models execute.

A cycle would look conceptually like:

```text
A → B → C → A
```

That cannot be resolved as a normal acyclic transformation dependency because each node ultimately waits on another node in the cycle.

DAGs are operationally useful because they support:

- dependency ordering;
- lineage;
- targeted execution;
- impact analysis;
- debugging;
- CI selection;
- upstream/downstream reasoning.


## 10. Model Layers and Grain

A common model organization is:

```text
models/
├── staging/
├── intermediate/
└── marts/
```

### Staging

Staging models generally:

- standardize names;
- cast types;
- clean basic source-specific irregularities;
- expose source data consistently.

Naming commonly uses:

```text
stg_
```

### Intermediate

Intermediate models contain reusable transformations between source-shaped staging data and consumer-oriented marts.

Naming commonly uses:

```text
int_
```

### Marts

Marts are consumer-oriented analytical datasets.

Common prefixes include:

```text
fct_
dim_
```

### Grain

Every important model should have a clearly stated grain.

Example:

```text
stg_orders
grain: one row per raw order record

fct_order_lines
grain: one row per order line

dim_customer
grain: one row per customer version/current state,
depending on the model design
```

Grain determines whether tests such as `unique` make sense.

A uniqueness test is not meaningful until the engineer knows what one row represents.


## 11. Materializations

A materialization determines how a model becomes a database object.

Core materializations include:

- view;
- table;
- incremental;
- ephemeral;
- materialized views where supported.

Conceptual comparison:

| Materialization | Storage | Build cost | Query performance | Typical use | Trade-off |
|---|---|---|---|---|---|
| View | Logical relation | Usually low at build time | Query-time computation | Lightweight transformations | Repeated query work |
| Table | Persisted relation | Full build cost | Usually strong | Expensive reusable transformations | Storage + rebuild cost |
| Incremental | Persisted subset/updated relation | Processes selected work | Usually strong | Large changing datasets | More correctness complexity |
| Ephemeral | Not persisted as normal relation | Compilation/query expansion | Depends on resulting SQL | Small reusable SQL components | Can make compiled SQL complex |
| Materialized view | Engine-managed persisted object | Engine-specific | Often strong | Platform-supported workloads | Adapter/engine dependent |

Do not reduce the decision to "incremental is faster."

Incremental models can be faster because they avoid recomputing historical data, but they introduce:

- key correctness requirements;
- late-data handling;
- schema evolution;
- duplicate handling;
- merge semantics;
- backfill complexity;
- state/history considerations.

The right choice depends on workload shape and correctness requirements.


## 12. View Materialization

A view generally stores the query definition rather than persisting the transformed rows in the same way as a table.

Conceptually:

```text
model SQL
    ↓
view definition
    ↓
query executes against underlying data
```

Advantages:

- low transformation storage footprint;
- simple dependency behavior;
- useful for lightweight transformations;
- fresh results when underlying data changes.

Trade-offs:

- expensive computation can be repeated at query time;
- downstream consumers may repeatedly execute complex joins/aggregations;
- performance depends on the underlying platform and query workload.

Views are useful when computation is relatively inexpensive or when query-time freshness and simplicity are more valuable than persisted computation.


## 13. Table Materialization

A table materialization persists transformed rows:

```text
model
  ↓
build
  ↓
materialized table
  ↓
consumer queries table
```

Tables are useful when:

- transformations are expensive;
- many consumers repeatedly query the result;
- persistence improves workload performance;
- rebuilding on the chosen schedule is acceptable.

Costs include:

- storage;
- build time;
- full rebuild cost;
- refresh scheduling;
- potential contention/resource consumption.

For a very large fact table, blindly rebuilding the entire table on every run can become operationally expensive. That is one reason incremental processing exists.


## 14. Ephemeral Models

An ephemeral model is not persisted as a normal table/view relation.

Conceptually:

```text
ephemeral model
      ↓
compiled into dependent SQL
      ↓
not persisted as a normal relation
```

Ephemeral models can improve:

- SQL reuse;
- modularity;
- local transformation composition.

But they can also increase:

- compiled SQL size;
- query complexity;
- debugging difficulty;
- repeated computation if reused broadly.

Use them for relatively small reusable transformations where not materializing a separate relation is beneficial.

Do not turn every model into an ephemeral model merely to avoid creating database objects.


## 15. Incremental Models

Incremental models are a major production pattern.

Compare:

```text
FULL REFRESH
→ process all historical data
```

with:

```text
INCREMENTAL
→ process newly arrived or changed data
```

Suppose a fact table contains ten years of orders.

A full rebuild might scan all ten years.

An incremental run may process only the relevant new/changed interval.

The benefit comes from avoiding unnecessary historical recomputation.

The cost is additional correctness complexity:

```text
incremental model
+
unique key
+
incremental predicate
+
late-data strategy
+
deduplication
+
schema-evolution strategy
=
production-safe incremental processing
```

Incremental models are therefore not simply a performance switch.


## 16. `is_incremental()` and `{{ this }}`

`is_incremental()` lets a model change its SQL behavior depending on whether dbt is executing it incrementally.

A conceptual example:

```sql
select *
from {{ source('raw', 'orders') }}

{% if is_incremental() %}
where loaded_at > (
    select coalesce(max(loaded_at), '1900-01-01')
    from {{ this }}
)
{% endif %}
```


The important cases are:

### First run

The target relation may not yet exist as an incremental target. The incremental condition should therefore not accidentally eliminate the initial dataset.

### Incremental run

`is_incremental()` evaluates in the incremental context and the model can restrict source work.

### Full-refresh run

A full refresh intentionally rebuilds the model, so incremental-only filtering must not incorrectly restrict the rebuild.

### `{{ this }}`

`{{ this }}` refers to the current model's target relation in the dbt context.

The precise compiled relation depends on target/environment configuration.

An engineer should inspect compiled SQL rather than guessing what a template means.


## 17. `unique_key` and Incremental Correctness

A unique key identifies the logical record that an incremental strategy should update/merge rather than blindly append, where the chosen strategy and adapter support that behavior.

Example:

```yaml
models:
  - name: fct_order_lines
    config:
      materialized: incremental
      unique_key: order_line_id
```


The key must match the intended grain.

Failure modes include:

### Missing key

The model may not be able to identify changed existing records correctly.

### Non-unique key

Multiple records can map to one logical identity, producing incorrect updates or ambiguous merge behavior.

### Duplicate source records

A duplicate source can produce duplicate target effects if not deduplicated appropriately.

### Changed records after initial load

A record already present in the target may need to be updated.

These concepts connect directly to earlier Module 2.12 topics:

```text
deduplication
+
merge-based loads
+
idempotency
+
late-arriving data
```

The question is not merely "does the model run?"

It is:

> Does repeated and changed input converge to the correct target state?


## 18. Incremental Strategies

Where supported by the relevant dbt version and adapter, incremental strategies can include:

- append;
- merge;
- delete+insert;
- insert_overwrite;
- microbatch.

These are not interchangeable.

| Strategy | Conceptual behavior | Useful shape | Main concern |
|---|---|---|---|
| Append | Add new rows | Immutable/event-like data | Updates/duplicates |
| Merge | Match and update/insert | Mutable records with stable key | Key correctness and merge cost |
| Delete+insert | Remove matching scope then insert | Replaceable logical scope | Correct delete scope |
| Insert overwrite | Replace partitions/scope | Partition-oriented datasets | Adapter/partition semantics |
| Microbatch | Process bounded time batches | Large time-series workloads | Batch orchestration/state |

Always verify supported strategies for the installed dbt version and adapter.

For each strategy ask:

```text
What is the data shape?
What defines identity?
What happens to duplicates?
How are updates represented?
What is replaced?
What is scanned?
What happens during failure?
How is a historical correction handled?
```


## 19. Lookback Windows and Late Data

A strict watermark such as:

```sql
where loaded_at > (
    select max(loaded_at)
    from {{ this }}
)
```


can miss records that arrive late or are corrected after the previous maximum.

A lookback window instead reprocesses a bounded period:

```sql
where loaded_at >= (
    select max(loaded_at) - interval '3 days'
    from {{ this }}
)
```


The exact interval is workload-dependent.

Lookbacks help with:

- late-arriving records;
- out-of-order events;
- delayed ingestion;
- upstream retries;
- corrections arriving after the original processing window.

The trade-off is:

```text
larger lookback
→ more recomputation
→ greater late-data coverage

smaller lookback
→ lower cost
→ greater risk of missing late data
```

This directly connects to Topic 04's late-arriving-data and reprocessing-window concepts.

A lookback still requires idempotent effects. Reprocessing three days is only safe if those repeated effects converge correctly.


## 20. `on_schema_change`

Incremental models can encounter source columns being added or changed.

`on_schema_change` expresses how schema evolution should be handled.

Conceptual behaviors include:

- ignore;
- fail;
- append new columns;
- synchronize columns where supported.

The exact supported values and behavior can vary by dbt version and adapter.

A production decision should explicitly answer:

```text
What happens when a column is added?
What happens when a type changes?
Should the pipeline fail?
Should the target evolve?
Who reviews the change?
How are downstream consumers protected?
```

Schema evolution is a contract and operational concern, not just a DDL detail.


## 21. Full Refresh

A full refresh can be requested with:

```bash
dbt run --full-refresh
```


A full refresh can be appropriate for:

- historical corrections;
- transformation-logic changes;
- corrupted targets;
- migrations;
- schema changes;
- deliberately rebuilding an incremental model.

It should not become the universal solution to every incremental problem.

A full refresh can be expensive for very large datasets.

Before using it, ask:

```text
Can the correction be targeted?
Can the affected interval be rebuilt?
Can the incremental logic be repaired?
What is the expected compute cost?
What downstream consumers are affected?
```


## 22. Microbatch

Where supported by the relevant dbt version and adapter, microbatch processing divides a large time range into smaller independently processed batches.

Conceptually:

```text
large time range
      ↓
small time batches
      ↓
process independently
```

Benefits can include:

- bounded work;
- easier recovery;
- parallelism;
- predictable resource usage.

Trade-offs include:

- additional state/coordination;
- batch-boundary correctness;
- more complex failure recovery;
- adapter/version-specific behavior.

Microbatch should therefore be treated as a workload-specific execution strategy, not an automatic replacement for all incremental models.

When teaching or implementing a microbatch feature, verify the installed dbt version and adapter documentation because behavior is version/adapter dependent.


## 23. dbt Testing

Transformation code without data tests is incomplete.

Tests turn assumptions into executable checks.

Important categories include:

- schema/data tests;
- singular tests;
- generic tests;
- custom tests.

The basic built-in test patterns include:

- `not_null`;
- `unique`;
- `accepted_values`;
- `relationships`.

Think of a test as an invariant:

```text
expected condition
        ↓
test query
        ↓
pass/fail result
```

A production test should answer:

> What bad state is this test preventing?


## 24. `not_null`

A `not_null` test checks that a column does not contain null values.

Example:

```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - not_null
```


Conceptually, it protects an invariant like:

```text
order_id IS NOT NULL
```

For a business-critical identifier, a null value can prevent joins, break downstream logic, or create records that cannot be uniquely identified.

Do not add `not_null` merely because a column "looks important." Define the model contract and grain first.


## 25. `unique`

A uniqueness test checks whether a column is unique within the tested model.

Example:

```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
```


The critical distinction is:

```text
unique field
```

versus:

```text
unique business entity
```

If a model's grain is one row per order line, `order_id` may legitimately repeat.

The correct key might be:

```text
order_line_id
```

Therefore:

> **Tests must match the model grain.**


## 26. `accepted_values`

Controlled vocabularies should be tested explicitly.

Example:

```yaml
models:
  - name: fct_orders
    columns:
      - name: status
        tests:
          - accepted_values:
              values:
                - pending
                - shipped
                - cancelled
```


This prevents unexpected values such as:

```text
shiped
SHIPPED
complete
unknown_business_state
```

unless those values are intentionally part of the contract.

The test converts a business vocabulary assumption into executable validation.


## 27. `relationships`

A relationship test checks referential integrity.

Conceptually:

```text
fct_orders.customer_id
        ↓
dim_customer.customer_id
```

A relationship test detects orphan records where a foreign-key-like value has no corresponding parent.

Example:

```yaml
models:
  - name: fct_orders
    columns:
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customer')
              field: customer_id
```


This is especially important in analytical models because broken relationships can silently change aggregates and joins.


## 28. Singular Tests

A singular test is SQL that represents a specific business rule.

The important pattern is:

```text
test query returns bad records
        ↓
zero rows = pass
non-zero rows = failure
```

Example: an order should not have a negative revenue amount.

```sql
select
    order_id,
    revenue
from {{ ref('fct_orders') }}
where revenue < 0
```


If this query returns any rows, the invariant is violated.

Singular tests are useful when a business rule does not fit a simple reusable generic test.


## 29. Generic Tests

A generic test is a reusable, parameterized validation definition.

Conceptually:

```text
generic test
     ↓
parameters
     ↓
reusable validation
     ↓
many models/columns
```

Generic tests are useful when the same rule occurs across many datasets.

For example, an organization may define a reusable test that checks whether a column contains only values permitted by a configuration.

The engineering benefit is consistency:

```text
one definition
→ many uses
→ one maintained behavior
```

The risk is abstraction for abstraction's sake. A generic test should remain understandable to the engineers operating the data platform.


## 30. Test Severity

Tests can have operational severity such as:

- `warn`;
- `error`.

Where supported by the relevant dbt version/adapter, related controls can include:

- `warn_if`;
- `error_if`;
- `store_failures`.

Conceptually:

```text
warning
→ signal
→ pipeline may continue depending on configuration

error
→ correctness failure
→ pipeline/build behavior is affected
```

A warning is not the same thing as a correctness guarantee.

For each test, define:

```text
What does failure mean?
Who owns it?
Does it block publication?
What happens to downstream consumers?
```


## 31. Source Freshness

Source freshness asks:

> **Is the upstream source arriving on time?**

Freshness is different from data correctness.

A source can be:

```text
fresh but wrong
```

or:

```text
correct but stale
```

A conceptual source definition may include freshness expectations based on an ingestion timestamp:

```yaml
sources:
  - name: raw
    tables:
      - name: orders
        loaded_at_field: loaded_at
        freshness:
          warn_after:
            count: 2
            period: hour
          error_after:
            count: 6
            period: hour
```


Exact configuration support can depend on dbt version/adapter.

Operationally:

```text
freshness failure
      ↓
upstream SLA violation
      ↓
downstream data may be incomplete/stale
      ↓
operational decision
```

Freshness should therefore connect to pipeline SLAs and incident response.


## 32. Seeds

Seeds are small static datasets managed by dbt.

Appropriate examples include:

- country codes;
- status mappings;
- small reference mappings;
- static business classifications.

They are not a replacement for large operational datasets or general ingestion.

A useful mental model is:

```text
small, version-controlled reference data
→ seed
```

rather than:

```text
large changing source system
→ seed
```

The choice should reflect ownership, update frequency, volume, and operational needs.


## 33. Jinja Fundamentals

Jinja is the template language used by dbt to generate dynamic SQL/configuration.

Two important syntactic forms are:

```jinja
{{ expression }}
```


and:

```jinja
{% control_statement %}
```


For example:

```sql
select
    order_id,
    amount
from {{ ref('stg_orders') }}

{% if target.name == 'dev' %}
where order_date >= current_date - interval '30 days'
{% endif %}
```


The critical execution distinction is:

```text
Jinja executes during dbt compilation.
SQL executes in the data platform.
```

Jinja generates SQL. It does not become a second database language.

This distinction is essential when debugging.


## 34. Macros

Macros package reusable Jinja/SQL logic.

Example:

```jinja
{% macro cents_to_dollars(column_name) %}
    {{ column_name }} / 100.0
{% endmacro %}
```


Use it in a model:

```sql
select
    order_id,
    {{ cents_to_dollars('amount_cents') }} as amount_dollars
from {{ ref('stg_orders') }}
```


Macros provide:

- reusability;
- abstraction;
- standardization;
- maintainability.

But macros can also be overused.

A useful rule is:

> Abstract repeated, stable logic when the abstraction makes the resulting SQL easier to understand.

Do not build a hidden programming language inside Jinja.


## 35. Jinja/SQL Safety

Dynamic SQL requires disciplined boundaries.

Production practices include:

- controlled identifiers;
- allowlists;
- configuration validation;
- avoiding arbitrary user-controlled SQL fragments;
- readable templates;
- inspecting compiled SQL.

This connects directly to metadata/config-driven pipeline design.

For example, an allowlist can restrict permitted relation names:

```jinja
{% set allowed_relations = ['orders', 'customers', 'products'] %}

{% if relation_name not in allowed_relations %}
    {{ exceptions.raise_compiler_error(
        'Unsupported relation: ' ~ relation_name
    ) }}
{% endif %}
```


The exact helper behavior can vary by dbt version, so verify against the installed environment.

The principle is stable:

```text
configuration
→ validation
→ controlled SQL generation
```

rather than:

```text
arbitrary external string
→ SQL fragment
```


## 36. Snapshots and SCD Type 2

Suppose a customer changes status:

```text
customer_id = 101
status = bronze
```

Later:

```text
customer_id = 101
status = gold
```

If only the current row is stored, historical analysis cannot easily answer:

> What status did customer 101 have last quarter?

SCD Type 2 preserves versions.

A conceptual structure is:

```text
customer_id
name
status
valid_from
valid_to
is_current
```

Example history:

| customer_id | status | valid_from | valid_to | is_current |
|---|---|---|---|---|
| 101 | bronze | 2026-01-01 | 2026-06-01 | false |
| 101 | gold | 2026-06-01 | null | true |

dbt snapshots provide a mechanism for capturing changing source records historically.

Important concepts include:

- snapshot purpose;
- timestamp strategy;
- check strategy;
- historical versions;
- current-state queries;
- historical-state queries.

A snapshot is therefore closely related to Data Modelling's SCD Type 2 concept.


## 37. Snapshot Strategies and Trade-Offs

Two major conceptual strategies are timestamp-based change detection and check-based change detection.

### Timestamp strategy

Uses a reliable modification timestamp.

It is attractive when the source provides a trustworthy update timestamp.

### Check strategy

Compares selected columns to detect changes.

It can be useful when reliable timestamps are unavailable, but the comparison scope and change semantics must be carefully designed.

Trade-offs include:

- storage growth;
- update detection;
- timestamp reliability;
- historical correctness;
- schema changes;
- backfills;
- operational complexity.

Snapshots are not free history. They introduce storage and operational requirements.

A historical model must also define what "current" means and how late corrections are represented.


## 38. Unit Tests vs Data Tests

These concepts answer different questions.

### Unit test

Validates transformation logic in isolation or against controlled inputs.

Example:

```text
given input rows
→ transformation
→ expected result
```

### Data test

Validates an invariant on actual model/source data.

Example:

```text
fct_orders.order_id must be unique
```

A useful distinction is:

```text
unit test
→ "Does this logic behave as designed?"

data test
→ "Does the produced dataset satisfy this invariant?"
```

Both can be valuable.

Data tests are especially important because a transformation can be logically correct while real upstream data violates assumptions.


## 39. Model Contracts

A model contract communicates:

> **This model promises a defined structure.**

Conceptually, a contract can specify:

- expected columns;
- data types;
- schema guarantees;
- producer/consumer expectations;
- breaking-change behavior.

Contracts improve reliability by making model interfaces explicit.

For a critical mart, consumers should not need to guess:

```text
Does this column exist?
What type is it?
Can it disappear?
Can its type change?
What is the grain?
```

A contract is not the same as a data test.

```text
contract
→ structural/interface expectation

data test
→ data-state invariant
```

Both can be used together.


## 40. Model Versions

Model interfaces sometimes need explicit versioning.

Conceptually:

```text
model v1
model v2
```

Versioning can help manage:

- breaking changes;
- consumer migration;
- deprecation;
- compatibility;
- staged adoption.

A breaking change should not be hidden as if it were a harmless column rename.

The engineering question is:

> How can producers change a model while giving downstream consumers a controlled migration path?

Exact model-version syntax is version-dependent, so verify it against the installed dbt version.


## 41. Python Models

dbt supports Python models for transformations that are better expressed in Python or require Python-native capabilities.

Potential use cases include:

- transformations difficult to express clearly in SQL;
- Python-native libraries;
- advanced statistical transformations;
- specialized logic.

Python models should not automatically replace SQL.

For relational transformations, SQL often remains a natural and efficient default because the data platform is optimized around relational execution.

Use Python when it provides a meaningful capability or clarity benefit.


## 42. Python Model Example

A conceptual Python model looks like:

```python
def model(dbt, session):
    dbt.config(materialized="table")

    orders = dbt.ref("stg_orders")

    result = (
        orders
        .filter(orders["amount"] > 0)
    )

    return result
```


The exact Python model API and dataframe/runtime behavior are adapter- and dbt-version-dependent. The example illustrates the conceptual lifecycle:

```text
model configuration
      ↓
input relation
      ↓
Python transformation
      ↓
returned dataframe/relation
      ↓
dbt-supported execution environment
```

Before using a Python model in production, verify:

- supported adapter;
- execution runtime;
- available libraries;
- dataframe API;
- dependency management;
- resource limits;
- serialization behavior.


## 43. Python Model Trade-Offs

### Advantages

- access to Python ecosystem;
- complex logic;
- familiar language for Python engineers;
- specialized libraries.

### Trade-offs

- execution environment;
- performance;
- serialization;
- warehouse/runtime support;
- dependency management;
- debugging;
- scalability;
- reproducibility.

The decision should be:

```text
Can SQL express this clearly and efficiently?
       ↓ yes
Prefer SQL

       ↓ no / specialized requirement
Evaluate Python model
```

Python is a specialized tool, not a universal replacement for relational SQL.


## 44. Documentation

Production data engineering includes documentation.

Useful dbt documentation can describe:

- models;
- columns;
- sources;
- tests;
- lineage;
- downstream consumers.

Conceptually:

```bash
dbt docs generate
dbt docs serve
```


Documentation reduces the amount of implicit knowledge required to operate the platform.

A good model description should explain:

```text
what the dataset represents
what one row means
who owns it
important business semantics
important assumptions
```

Documentation and tests complement each other:

```text
documentation
→ explains the contract

tests
→ enforce selected invariants
```


## 45. Lineage

The DAG provides lineage.

Example:

```text
source
  ↓
staging
  ↓
intermediate
  ↓
mart
  ↓
dashboard
```

Lineage supports:

- upstream tracing;
- downstream impact analysis;
- dependency understanding;
- debugging;
- change planning.

For an incident:

```text
dashboard metric changed
        ↓
trace downstream
        ↓
fct_daily_revenue
        ↓
fct_order_lines
        ↓
stg_order_lines
        ↓
raw_order_lines
```

This is much easier when dependencies are explicit through `ref()` and `source()`.


## 46. Exposures

Exposures conceptually represent downstream consumers such as:

- dashboards;
- reports;
- applications;
- analytical products.

They help connect the transformation DAG to real consumers.

For example:

```text
fct_daily_revenue
       ↓
executive revenue dashboard
```

When a model changes, exposure information improves impact analysis because the engineer can reason about which downstream products depend on it.


## 47. Slim CI and State-Aware Workflows

A large project may contain hundreds or thousands of models.

If one model changes, rebuilding everything for every pull request can be expensive.

State-aware workflows compare:

```text
previous production state
+
current branch
```

to identify changed nodes and their relevant graph.

A common conceptual selector is:

```text
state:modified+
```

and `defer` can allow appropriate references to existing state in supported workflows.

The conceptual process is:

```text
previous production state
        +
current branch
        ↓
identify changed nodes
        ↓
select affected graph
        ↓
test/build targeted scope
```

Exact selection syntax and state behavior are version-dependent. Verify the installed dbt version.

The principle is stable:

> CI should spend compute where code/data-logic changes require it, while preserving enough upstream context to validate the change.


## 48. `dbt build` and Model Selection

`dbt build` is a broader build command than running only model execution.

Conceptually:

```bash
dbt build --select fct_orders+
```


The exact selection syntax and build behavior are version-dependent.

Model selection can target:

- a model;
- upstream dependencies;
- downstream dependencies;
- tags;
- paths;
- state-based selections.

Selection is useful for:

- development;
- CI;
- debugging;
- backfills;
- targeted rebuilds.

A key operational principle is:

> Select the smallest graph that provides sufficient correctness evidence for the task.


## 49. `dbt compile` and Compiled SQL

`dbt compile` is one of the most important debugging tools.

Conceptually:

```text
Jinja + dbt context
        ↓
compiled SQL
        ↓
database execution
```

When a model fails, inspect compiled SQL before blindly rerunning the whole project.

Compiled SQL helps identify:

- incorrect Jinja logic;
- wrong references;
- unexpected filters;
- malformed SQL;
- environment-specific behavior;
- incremental predicates.

The debugging workflow is:

```text
read failure
→ select affected model
→ compile
→ inspect generated SQL
→ inspect upstream inputs
→ test a smaller scope
→ fix
→ rerun targeted graph
```


## 50. dbt Limitations

dbt should be understood honestly.

It is not a universal:

- extraction framework;
- ingestion platform;
- external-side-effect engine;
- application runtime;
- distributed processing solution for every workload;
- orchestration system for every cross-system workflow.

A production platform may therefore need separate capabilities for:

```text
ingestion
orchestration
storage
transformation
testing
observability
deployment
CI/CD
```

dbt can occupy the transformation and data-quality/documentation portion without pretending to provide the entire platform.

Tool choice should be based on workload requirements rather than forcing every problem into dbt.


## 51. Version and Adapter Awareness

dbt features can vary by:

- dbt version;
- adapter;
- execution engine.

Therefore, for version/adapter-dependent behavior:

1. explicitly identify the dependency;
2. do not present syntax as universally guaranteed;
3. teach the underlying concept;
4. provide a roadmap-aligned example;
5. explain how to verify support in the installed environment.

This is especially important for:

- incremental strategies;
- microbatch behavior;
- Python models;
- materialized views;
- contracts/versioning features;
- state-aware workflows;
- advanced selection syntax.

Production engineers should distinguish:

```text
conceptual guarantee
```

from:

```text
specific implementation syntax
```


## 52. Complete Hands-On dbt Project

Use an order-platform scenario.

The conceptual architecture is:

```text
raw sources
    ↓
staging
    ↓
intermediate
    ↓
marts
```

### Sources

```text
raw_orders
raw_order_lines
raw_customers
raw_products
```

### Staging

```text
stg_orders
stg_order_lines
stg_customers
stg_products
```

### Intermediate

```text
int_order_lines
int_customer_orders
```

### Marts

```text
dim_customer
fct_order_lines
fct_daily_revenue
```

These are conceptual model definitions for this chapter. They do not imply creating additional project files.

A useful dependency graph is:

```text
raw_orders ───────→ stg_orders ───────────┐
raw_order_lines ──→ stg_order_lines → int_order_lines
raw_customers ────→ stg_customers ────────┤
raw_products ─────→ stg_products ─────────┘
                                              ↓
                                      fct_order_lines
                                              ↓
                                      fct_daily_revenue

stg_customers → dim_customer
```

The exact graph should reflect the actual grain and business relationships of the implementation.


## 53. Hands-On Source Freshness

Define a source with an ingestion timestamp and freshness expectations.

Conceptually:

```text
source definition
+
loaded_at metadata
+
freshness expectation
+
freshness failure
```

A stale source should trigger an operational decision rather than being silently treated as current.

Example decision path:

```text
source freshness fails
        ↓
determine impact
        ↓
prevent publication if required
        ↓
notify owner
        ↓
restore source
        ↓
rerun affected transformations
```

The exact thresholds are workload-specific.


## 54. Hands-On Customer Snapshot

Design a customer history snapshot:

```text
customer history
      ↓
SCD Type 2 snapshot
      ↓
historical customer dimension
```

The historical result can support:

### Current-state query

```sql
where is_current = true
```

### Historical query

```sql
where valid_from <= :as_of_timestamp
  and (valid_to > :as_of_timestamp or valid_to is null)
```

The exact snapshot columns and strategy depend on the dbt version and snapshot implementation.

The key analytical property is preservation of historical versions rather than only the latest state.


## 55. Hands-On `fct_order_lines` Incremental Model

The fact model should explicitly define:

- grain;
- unique key;
- incremental filter;
- lookback window;
- appropriate incremental strategy;
- late-arriving record behavior;
- schema-change behavior;
- full-refresh escape hatch.

Conceptual model:

```sql
{{ config(
    materialized='incremental',
    unique_key='order_line_id'
) }}

with source_rows as (

    select *
    from {{ ref('stg_order_lines') }}

    {% if is_incremental() %}
    where loaded_at >= (
        select coalesce(
            max(loaded_at) - interval '3 days',
            '1900-01-01'
        )
        from {{ this }}
    )
    {% endif %}

),

deduplicated as (

    select *
    from source_rows
    qualify row_number() over (
        partition by order_line_id
        order by loaded_at desc
    ) = 1

)

select *
from deduplicated
```


The exact SQL syntax is adapter-dependent; `QUALIFY` is not universally supported.

The important design is:

```text
bounded lookback
+
deduplication
+
stable unique key
+
idempotent incremental strategy
```


## 56. Hands-On `fct_daily_revenue`

Define the grain:

```text
one row per calendar day
```

A conceptual model is:

```sql
select
    order_date,
    sum(revenue) as daily_revenue,
    count(*) as order_line_count,
    count(distinct customer_id) as customer_count
from {{ ref('fct_order_lines') }}
group by order_date
```


Important production questions:

- Is the source fact complete for the day?
- Can late records change historical days?
- Does the model need incremental rebuild windows?
- What is the business definition of revenue?
- Are refunds included?
- What is the contract?
- What tests prove the grain?


## 57. Hands-On Python Model

Use Python only when it provides a meaningful capability.

A conceptual example could calculate a specialized statistical transformation:

```python
def model(dbt, session):
    dbt.config(materialized="table")

    source = dbt.ref("stg_customer_orders")

    # Illustrative only:
    # the exact dataframe API depends on the execution runtime.
    result = specialized_python_transformation(source)

    return result
```


The Python model is appropriate when the transformation requires Python-native logic that would be substantially less clear or practical in SQL.

Compare:

```text
SQL solution
→ relational operations
→ usually natural for joins/aggregations/window logic

Python solution
→ Python ecosystem
→ useful for specialized algorithms/statistics
```

The decision should be based on execution environment, performance, dependencies, maintainability, and reproducibility.


## 58. Testing the Complete Project

The project should include tests for:

- `not_null`;
- `unique`;
- `accepted_values`;
- `relationships`;
- business-rule singular tests;
- source freshness;
- model contracts where applicable.

Example conceptual test matrix:

| Dataset | Test | Invariant |
|---|---|---|
| `stg_orders` | not_null | order ID exists |
| `fct_order_lines` | unique | line ID matches grain |
| `fct_orders` | relationships | customer exists |
| `fct_orders` | accepted_values | status vocabulary is controlled |
| `fct_daily_revenue` | singular | revenue rule is satisfied |
| raw source | freshness | source arrives on time |
| critical mart | contract | interface remains defined |

Testing should be tied to business risk rather than test-count vanity.


## 59. Reconciliation: Incremental vs Full Rebuild

Incremental correctness should be validated against a full rebuild.

Conceptually:

```text
incremental result
       vs
full rebuild result
```

Compare:

- row counts;
- aggregates;
- duplicate counts;
- missing partitions;
- checksums/fingerprints where appropriate.

For example:

```text
incremental daily revenue
vs
full-refresh daily revenue
```

If they differ, investigate:

```text
incremental predicate
unique key
late data
deduplication
source completeness
non-deterministic logic
```

A reconciliation test is one of the strongest ways to validate incremental transformation correctness.


## 60. Idempotency

Run the same model multiple times:

```text
run 1
run 2
run 3
```

The result should converge to the same correct dataset.

Things that can break idempotency include:

- non-deterministic expressions;
- incorrect incremental predicates;
- duplicate source records;
- incorrect `unique_key`;
- unstable ordering;
- time-dependent transformations.

The production question is:

> If this model is retried after a partial failure, will the final result still be correct?

Idempotency connects dbt directly to the earlier transformation-pipeline topics.


## 61. Failure Scenarios and Debugging

Use the following incident pattern:

```text
SYMPTOM
→ ROOT CAUSE
→ INVESTIGATION
→ FIX
→ PREVENTION
```

### 1. Source is stale

**Symptom:** freshness test fails.

**Root cause:** upstream data has not arrived.

**Investigation:** inspect source arrival timestamp and upstream pipeline status.

**Fix:** restore upstream or prevent downstream publication.

**Prevention:** freshness monitoring and ownership.

### 2. Source schema changes

**Symptom:** model/build failure.

**Root cause:** unexpected column/type change.

**Investigation:** inspect schema diff and model configuration.

**Fix:** handle schema evolution deliberately.

**Prevention:** contracts and schema-change strategy.

### 3. Duplicate source rows arrive

**Symptom:** unique test fails.

**Root cause:** upstream duplicate or missing deduplication.

**Investigation:** inspect duplicate keys and source ingestion history.

**Fix:** correct source handling/deduplicate.

**Prevention:** uniqueness tests and source contracts.

### 4. Late records arrive

**Symptom:** historical partition is incomplete.

**Root cause:** strict watermark excluded late data.

**Investigation:** compare arrival time and event/business time.

**Fix:** reprocess the appropriate lookback window.

**Prevention:** explicit late-data strategy.

### 5. Incremental unique key is wrong

**Symptom:** duplicates or incorrect updates.

**Root cause:** key does not represent model grain.

**Investigation:** profile key cardinality.

**Fix:** redesign key/deduplication.

**Prevention:** grain-first model design.

### 6. Incremental model misses old records

**Symptom:** full rebuild differs from incremental result.

**Root cause:** overly narrow incremental predicate.

**Investigation:** compare missing records against source arrival/update timing.

**Fix:** repair predicate/lookback and rebuild affected scope.

**Prevention:** reconciliation tests.

### 7. Snapshot timestamp is unreliable

**Symptom:** changes are missed or history is incorrect.

**Root cause:** update timestamp does not reliably represent change.

**Investigation:** compare source change history to timestamp behavior.

**Fix:** use an appropriate strategy or source correction.

**Prevention:** source contract for change timestamps.

### 8. Python model fails

**Symptom:** Python model execution error.

**Root cause:** runtime/library/API/resource problem.

**Investigation:** inspect adapter/runtime logs and model input.

**Fix:** correct supported runtime behavior.

**Prevention:** pin/test dependencies and keep Python use focused.

### 9. Data test fails

**Symptom:** build/test reports failing rows.

**Root cause:** actual data violates an invariant.

**Investigation:** inspect returned failure rows.

**Fix:** repair data or transformation depending on ownership.

**Prevention:** correct upstream contract and monitoring.

### 10. Model contract fails

**Symptom:** structural/interface validation fails.

**Root cause:** model output changed unexpectedly.

**Investigation:** compare expected and actual schema.

**Fix:** migrate consumers or restore compatibility.

**Prevention:** controlled model interface changes.

### 11. Logic change requires historical rebuild

**Symptom:** new logic changes historical outputs.

**Root cause:** transformation semantics changed.

**Investigation:** identify affected models/time range.

**Fix:** targeted or full historical rebuild as appropriate.

**Prevention:** versioning, impact analysis, reconciliation.

### 12. Dependency change affects downstream models

**Symptom:** downstream model/test breaks.

**Root cause:** upstream interface or semantics changed.

**Investigation:** use lineage/DAG.

**Fix:** migrate or rebuild affected downstream graph.

**Prevention:** contracts, tests, documentation, CI.


## 62. Systematic dbt Debugging

Do not blindly rerun the entire project.

Use:

```text
1. Identify failed node
2. Read the error
3. Compile the model
4. Inspect compiled SQL
5. Inspect upstream dependencies
6. Inspect target/incremental state
7. Run the smallest useful selection
8. Compare against known-good/full-refresh behavior
9. Fix
10. Re-run targeted graph
```

Useful commands include:

```bash
dbt compile --select fct_order_lines
dbt run --select fct_order_lines
dbt test --select fct_order_lines
dbt build --select fct_order_lines+
```


Exact selector behavior is version-dependent.

The key is targeted investigation, not indiscriminate recomputation.


## 63. Anti-Patterns

| Anti-pattern | Problem | Consequence | Safer pattern |
|---|---|---|---|
| One giant dbt model | Too much logic in one node | Hard to test/debug | Layered models |
| Hard-coded table names everywhere | Hidden dependencies | Weak lineage/environment portability | `ref()`/`source()` |
| No staging layer | Raw quirks spread everywhere | Duplication | Standardized staging |
| No tests | Assumptions are implicit | Silent data defects | Explicit invariants |
| Tests ignore grain | Wrong uniqueness assumptions | False failures or missed defects | Define grain first |
| Overusing macros | Hidden complexity | Harder SQL | Abstract stable repetition |
| Overusing Jinja | SQL becomes template program | Debugging complexity | Keep templates simple |
| Jinja as programming language | Excessive dynamic behavior | Unmaintainability | Keep business logic in models |
| Python for SQL-friendly work | Unnecessary runtime complexity | Cost/debugging issues | Prefer SQL where sufficient |
| Incremental without correctness strategy | Missed/duplicate data | Historical inconsistency | Key + lookback + reconciliation |
| No lookback | Late records missed | Incomplete history | Reprocessing window |
| Incorrect `unique_key` | Wrong merge identity | Duplicates/lost updates | Grain-aligned key |
| Ignoring schema evolution | Surprise failures | Broken pipelines | Explicit strategy |
| Full-refresh for every problem | Excessive compute | Slow/costly recovery | Targeted repair |
| No source freshness | Stale inputs invisible | Stale outputs | Freshness checks |
| No model contracts | Interfaces implicit | Breaking downstream changes | Contracts for critical models |
| No documentation | Tribal knowledge | Slow operations | Model/source documentation |
| Treating dbt as ingestion | Wrong tool boundary | Complex platform | Separate ingestion |
| Rebuild everything for small change | Wasteful CI | Slow feedback | Targeted/state-aware selection |
| Ignoring compiled SQL | Debugging templates instead of execution | Slow diagnosis | Inspect compiled SQL |
| Assuming adapters are identical | Unsupported syntax/features | Production failures | Version/adapter awareness |


## 64. Production Architecture

A production transformation architecture can be represented as:

```text
                     Sources
                        |
                        v
                 Ingestion Layer
                        |
                        v
                    Raw/Bronze
                        |
                        v
                       dbt
                        |
             +----------+----------+
             |                     |
             v                     v
         Staging              Source tests
             |
             v
        Intermediate
             |
             v
           Marts
             |
       +-----+------+
       |            |
       v            v
 Dashboards    Applications
```

dbt belongs primarily in the transformation layer.

A complete production platform still needs:

### Ingestion

Moves data from operational/external systems into the data platform.

### Orchestration

Schedules and coordinates workflows.

### Transformation

dbt models transform warehouse/lakehouse data.

### Testing

Data tests, source freshness, contracts, and additional validation.

### Documentation

Model/column/source semantics.

### Observability

Monitors failures, freshness, volume, quality, and runtime behavior.

### Deployment

Controls promotion of transformation code.

### CI/CD

Validates changes before production deployment.

dbt alone should not be presented as the entire data platform.


## 65. Production Trade-Offs

### View vs table

**View:** less persisted transformed storage but more query-time work.

**Table:** persisted computation and generally predictable query access, at the cost of build/storage.

### Table vs incremental

**Table:** simpler correctness model, potentially expensive rebuilds.

**Incremental:** less recomputation, greater correctness complexity.

### SQL vs Python model

**SQL:** natural for relational transformations.

**Python:** useful for specialized logic/libraries, but requires supported runtime and careful performance/reproducibility management.

### Snapshot vs custom SCD2

**Snapshot:** standardized dbt-oriented historical capture.

**Custom SCD2:** more explicit control over specialized business semantics.

### Generic tests vs custom tests

**Generic:** reusable and standardized.

**Custom:** precise business rule.

### Centralized macros vs local SQL

**Macros:** useful for repeated stable logic.

**Local SQL:** often easier to understand for one-off business transformations.

### Full refresh vs incremental rebuild

**Full refresh:** simple correctness model, potentially expensive.

**Incremental rebuild:** lower scope/cost, more complex selection/correctness.

### Broad CI vs slim CI

**Broad CI:** wider validation coverage, more compute/time.

**Slim CI:** faster targeted feedback, requires trustworthy state/dependency selection.

### Strict contracts vs flexible schemas

**Strict contracts:** stronger interfaces, potentially slower schema evolution.

**Flexible schemas:** easier evolution, weaker guarantees.

There is no universal winner. The appropriate choice depends on correctness, scale, latency, cost, ownership, and operational requirements.


## 66. Exercises

### Basic — 1
Explain dbt in your own words and identify where it sits in ELT.

### Basic — 2
Create a conceptual dbt project tree and explain each directory.

### Basic — 3
Write a simple staging SQL model.

### Basic — 4
Rewrite a hard-coded model reference using `ref()`.

### Basic — 5
Write a source YAML definition for `raw.orders`.

### Basic — 6
Draw the DAG for source → staging → intermediate → mart.

### Basic — 7
Choose view/table/ephemeral for three small transformation examples and explain why.

### Basic — 8
Write YAML for `not_null`, `unique`, and `accepted_values`.

### Basic — 9
Write a singular test that returns orders with negative revenue.

### Basic — 10
Explain the difference between `dbt compile`, `dbt run`, `dbt test`, and `dbt build`.

### Moderate — 11
Design a staging/intermediate/mart structure for an e-commerce order platform.

### Moderate — 12
Build an incremental model with `is_incremental()`.

### Moderate — 13
Choose and justify a `unique_key` for order-line grain.

### Moderate — 14
Design a three-day lookback for late-arriving records.

### Moderate — 15
Write a source freshness configuration and explain the operational response.

### Moderate — 16
Write a reusable macro that converts cents to dollars.

### Moderate — 17
Write a generic test concept for a controlled status vocabulary.

### Moderate — 18
Design a customer SCD2 snapshot and explain timestamp vs check strategy.

### Moderate — 19
Write a model contract concept for a critical revenue mart.

### Moderate — 20
Use model selection to target a model and its downstream graph; explain the version-dependent syntax.

### Hard — 21
Design an incremental `fct_order_lines` model that handles duplicates and late data.

### Hard — 22
Compare incremental output against a full rebuild and design reconciliation checks.

### Hard — 23
Debug a unique test failure caused by a non-unique `unique_key`.

### Hard — 24
Design a source freshness incident workflow.

### Hard — 25
Design a snapshot for changing customer status and explain historical queries.

### Hard — 26
Design generic and singular tests for a financial reporting model.

### Hard — 27
Design a SQL/Python boundary for a specialized statistical transformation.

### Hard — 28
Design a contract migration from model v1 to v2 without silently breaking consumers.

### Hard — 29
Design slim CI for a project containing 500 models.

### Hard — 30
Investigate a compiled SQL failure caused by Jinja logic.

### Advanced — 31
Design dbt for a one-billion-row orders dataset, including materialization, incremental strategy, late-data handling, tests, and backfill.

### Advanced — 32
Design an SCD2 customer history architecture that supports point-in-time analytics.

### Advanced — 33
Design a dbt testing strategy for a financial reporting mart where false positives are expensive.

### Advanced — 34
Design source freshness monitoring for a critical upstream source with a strict SLA.

### Advanced — 35
Design dbt CI for a 1,000-model project using state-aware selection and defer where supported.

### Advanced — 36
Design model contracts for critical marts and a consumer migration strategy.

### Advanced — 37
Design safe historical backfill for an incremental model after a transformation bug.

### Advanced — 38
Design SQL + Python model boundaries for a large analytical platform.

### Advanced — 39
Design dbt around an existing ingestion and orchestration platform without duplicating responsibilities.

### Advanced — 40
Present a complete production dbt architecture and defend every major trade-off.


## 67. Interview Questions

### Basic — Question 1
**What is dbt?**

**Expected answer:** A transformation framework that manages transformation definitions, dependencies, testing, documentation, and execution against supported data platforms.

**Senior insight:** dbt is primarily a transformation layer, not an ingestion platform.

### Basic — Question 2
**Why is dbt associated with ELT?**

**Expected answer:** Data is loaded into the warehouse/lakehouse first and transformed there.

**Senior insight:** dbt takes advantage of the data platform's computational engine.

### Basic — Question 3
**What is a dbt model?**

**Expected answer:** A transformation definition that dbt can compile and materialize.

**Senior insight:** A model file is not the same thing as its resulting database relation.

### Basic — Question 4
**What is `ref()`?**

**Expected answer:** A model reference that also declares a dependency.

**Senior insight:** `ref()` is both a relation reference and a DAG declaration.

### Basic — Question 5
**What is `source()`?**

**Expected answer:** A reference to declared upstream source data.

**Senior insight:** Sources create ownership/freshness/documentation/lineage context around external data.

### Basic — Question 6
**What is a DAG?**

**Expected answer:** A directed acyclic graph of dependencies.

**Senior insight:** The DAG enables ordering, lineage, selection, and impact analysis.

### Basic — Question 7
**What are materializations?**

**Expected answer:** Strategies controlling how model definitions become database objects.

**Senior insight:** Materialization is a workload decision, not a purely stylistic preference.

### Basic — Question 8
**What is an incremental model?**

**Expected answer:** A model that avoids recomputing the entire historical dataset on every run by processing a selected scope.

**Senior insight:** Incremental processing saves work but introduces correctness complexity.

### Basic — Question 9
**What does `dbt test` do?**

**Expected answer:** Executes configured data validations.

**Senior insight:** Tests encode dataset invariants.

### Basic — Question 10
**What is a snapshot?**

**Expected answer:** A mechanism for preserving historical versions of changing records.

**Senior insight:** Snapshots support historical state analysis such as SCD2 patterns.

### Moderate — Question 11
**How does `is_incremental()` work?**

**Expected answer:** It allows model SQL to conditionally apply incremental logic based on execution context.

**Senior insight:** First-run, incremental, and full-refresh behavior must all be considered.

### Moderate — Question 12
**Why does an incremental model need a `unique_key`?**

**Expected answer:** When updates/merges need a stable identity for logical records.

**Senior insight:** The key must match the model grain.

### Moderate — Question 13
**How do you handle late-arriving data?**

**Expected answer:** Use an appropriate lookback/reprocessing window and idempotent effects.

**Senior insight:** Late-data correctness is a design property, not just a filter change.

### Moderate — Question 14
**What is the difference between a source and a model?**

**Expected answer:** A source is upstream data external to the dbt model graph; a model is transformation logic managed by dbt.

**Senior insight:** This distinction clarifies lineage and ownership.

### Moderate — Question 15
**What is a generic test?**

**Expected answer:** A reusable parameterized validation.

**Senior insight:** Reuse should improve consistency without hiding business semantics.

### Moderate — Question 16
**What is a singular test?**

**Expected answer:** A SQL test representing a specific business rule, where returned bad rows indicate failure.

**Senior insight:** Zero rows means the tested invariant currently holds.

### Moderate — Question 17
**What is source freshness?**

**Expected answer:** Validation that upstream data arrived within expected timing.

**Senior insight:** Freshness and correctness are separate dimensions.

### Moderate — Question 18
**Why use snapshots?**

**Expected answer:** To preserve historical versions of changing records.

**Senior insight:** Historical correctness requires knowing what was true at a prior point in time.

### Moderate — Question 19
**What are model contracts?**

**Expected answer:** Explicit expectations around model structure/interfaces.

**Senior insight:** Contracts protect consumers from unexpected breaking changes.

### Moderate — Question 20
**What is slim CI?**

**Expected answer:** A state-aware approach that focuses validation/build work on changed or affected graph areas.

**Senior insight:** State-aware CI reduces feedback cost without abandoning dependency-aware correctness.

### Hard — Question 21
**When would you choose a table over an incremental model?**

**Expected answer:** When rebuild cost is acceptable or correctness simplicity is more valuable than incremental complexity.

**Senior insight:** Incremental is not automatically better.

### Hard — Question 22
**When would you choose an incremental model over a table?**

**Expected answer:** When historical recomputation is expensive and the workload has a reliable incremental boundary.

**Senior insight:** The savings must outweigh correctness and operational complexity.

### Hard — Question 23
**How would you prove an incremental model is correct?**

**Expected answer:** Compare it with a full rebuild, test duplicates/invariants, and exercise late-data/retry scenarios.

**Senior insight:** Reconciliation provides stronger evidence than trusting the incremental query.

### Hard — Question 24
**How can an incorrect unique key corrupt an incremental model?**

**Expected answer:** It can merge unrelated records or fail to merge records that represent the same logical entity.

**Senior insight:** Key correctness is a grain question.

### Hard — Question 25
**What should happen when a source becomes stale?**

**Expected answer:** Operational policy should determine whether downstream processing is blocked, warned, or allowed with explicit degradation.

**Senior insight:** Freshness should connect to ownership and SLAs.

### Hard — Question 26
**What are the trade-offs of snapshots?**

**Expected answer:** Historical fidelity versus storage growth, change detection complexity, timestamp reliability, and operational cost.

**Senior insight:** Historical state is valuable but not free.

### Hard — Question 27
**When should Python models be used?**

**Expected answer:** When Python-native capabilities provide meaningful value that is difficult or inappropriate to express in SQL.

**Senior insight:** SQL should generally remain the default for relational transformations when sufficient.

### Hard — Question 28
**Why inspect compiled SQL?**

**Expected answer:** Because Jinja/dbt definitions are transformed into executable SQL and failures may be visible only in the generated SQL.

**Senior insight:** Compiled SQL is a primary debugging artifact.

### Hard — Question 29
**How should contracts and tests work together?**

**Expected answer:** Contracts protect structural interfaces; tests validate data-state invariants.

**Senior insight:** Neither replaces the other.

### Hard — Question 30
**What does dbt not solve?**

**Expected answer:** It is not a universal ingestion, extraction, application, or cross-system orchestration platform.

**Senior insight:** Production architecture needs explicit tool boundaries.

### Advanced — Question 31
**Design dbt for a billion-row fact table.**

**Expected answer:** Define grain and keys, use an appropriate incremental strategy, bounded lookback, partition-aware processing where supported, validation, reconciliation, and deliberate full-refresh/backfill procedures.

**Senior insight:** The hard part is correctness under change, not simply reducing scanned rows.

### Advanced — Question 32
**How would you design late-arriving order-event processing?**

**Expected answer:** Use a business/event-time model, bounded lookback/reprocessing, deduplication, idempotent writes, and reconciliation.

**Senior insight:** Arrival time and event time must not be conflated.

### Advanced — Question 33
**How would you design SCD2 customer history?**

**Expected answer:** Define change-detection semantics, preserve effective validity intervals, support current/historical queries, test uniqueness/non-overlap, and handle corrections.

**Senior insight:** Historical correctness depends on reliable change semantics.

### Advanced — Question 34
**How would you design dbt tests for financial reporting?**

**Expected answer:** Combine structural tests, uniqueness/relationships, business-rule tests, reconciliation to trusted totals, freshness, and appropriate failure severity.

**Senior insight:** Test selection should follow financial risk and reporting invariants.

### Advanced — Question 35
**How would you design source freshness monitoring?**

**Expected answer:** Define loaded-at semantics, expected arrival windows, warn/error thresholds, owners, incident response, and downstream publication policy.

**Senior insight:** A freshness alert without an ownership/runbook path is only a notification.

### Advanced — Question 36
**How would you design CI for 1,000 models?**

**Expected answer:** Use state-aware changed-node selection, relevant upstream/downstream context, defer where appropriate, targeted tests, and production-state artifacts.

**Senior insight:** CI correctness depends on reliable state and graph semantics.

### Advanced — Question 37
**How would you design contracts for critical marts?**

**Expected answer:** Define stable columns/types/interfaces, ownership, compatibility rules, migration/deprecation process, and validation.

**Senior insight:** A contract is an organizational interface, not merely YAML syntax.

### Advanced — Question 38
**How would you choose SQL vs Python models?**

**Expected answer:** Start with SQL for relational work and use Python where specialized capabilities justify the additional runtime/dependency complexity.

**Senior insight:** The boundary should be intentional and observable.

### Advanced — Question 39
**How would you perform a safe historical backfill?**

**Expected answer:** Define affected scope, validate source completeness, isolate/backfill targeted models, compare results, protect downstream consumers, and document the change.

**Senior insight:** Backfills are production changes, not just reruns.

### Advanced — Question 40
**How would you design a production dbt architecture around existing ingestion/orchestration?**

**Expected answer:** Keep ingestion and scheduling responsibilities outside dbt where appropriate, use dbt for transformations/tests/docs/lineage, integrate CI/CD and observability, and define clear ownership boundaries.

**Senior insight:** A maintainable platform has explicit boundaries rather than one tool owning everything.


## 68. Architecture Interview Questions

### Architecture 1 — One-billion-row orders dataset

**Requirements**

- very large fact table;
- late data;
- updates;
- reliable reporting;
- bounded compute.

**Assumptions**

The data platform supports the chosen incremental strategy and the source provides a usable identity/update signal.

**Architecture**

```text
raw_orders
   ↓
stg_orders
   ↓
deduplicated incremental fact
   ↓
fct_order_lines
   ↓
daily aggregate
```

**Incremental strategy**

Use a key-aligned incremental strategy and bounded lookback.

**Testing**

Uniqueness, not-null, relationships, business rules, freshness, reconciliation.

**Failure handling**

Retry idempotently, inspect incremental target state, rebuild affected scope.

**Trade-off**

More incremental complexity versus reduced historical compute.

### Architecture 2 — Late-arriving order events

Use event-time semantics, arrival-time metadata, lookback/reprocessing windows, deduplication, and reconciliation against a trusted rebuild.

### Architecture 3 — SCD2 customer history

Use snapshot/change-detection semantics, effective intervals, current-state access, historical point-in-time access, and tests for key integrity and interval correctness.

### Architecture 4 — Financial reporting tests

Combine structural tests, business-rule singular tests, relationships, freshness, reconciliation, and appropriate failure severity. Critical metrics should have independent reasonableness/reconciliation checks where possible.

### Architecture 5 — Source freshness monitoring

Define source ownership, loaded-at semantics, freshness thresholds, warning/error policy, downstream impact, and incident runbook.

### Architecture 6 — 1,000-model CI

Use production state, state-aware changed selection, appropriate upstream/downstream context, defer where supported, and targeted tests. Keep a broader scheduled validation path for additional confidence.

### Architecture 7 — Critical model contracts

Define model interface, types, grain, ownership, compatibility expectations, migration/deprecation process, and automated enforcement.

### Architecture 8 — SQL + Python boundary

Keep SQL for relational operations and introduce Python for specialized transformations that justify runtime complexity. Validate supported execution environments and resource constraints.

### Architecture 9 — Safe historical backfill

Identify exact affected scope, validate source state, isolate the backfill, rebuild idempotently, compare against expected results, and coordinate downstream publication.

### Architecture 10 — dbt around existing ingestion/orchestration

```text
source systems
      ↓
ingestion
      ↓
raw/bronze
      ↓
orchestrator
      ↓
dbt
      ↓
staging → intermediate → marts
      ↓
tests/docs/observability
      ↓
consumers
```

Keep ownership explicit:

```text
ingestion
→ moves data

orchestrator
→ schedules/co-ordinates

dbt
→ transforms/tests/documents

data platform
→ stores/executes data
```


## 69. Study Loop

Use the roadmap study loop:

```text
1. Read
2. Define the run contract
3. Build
4. Run twice
5. Run for the past
6. Break
7. Verify invariants
8. Change the logic and rebuild
9. Write it down
10. Explain it aloud
```

### Read

Understand dbt concepts before copying syntax.

### Define the run contract

Specify:

```text
inputs
outputs
grain
dependencies
materialization
incremental boundary
tests
freshness expectations
contracts
```

### Build

Implement the model graph.

### Run twice

Verify idempotency.

### Run for the past

Test historical incremental correctness.

### Break

Introduce:

- duplicates;
- late records;
- schema changes;
- test failures;
- stale sources;
- incorrect keys.

### Verify invariants

Compare:

```text
incremental result
vs
full rebuild
```

### Change logic and rebuild

Determine affected historical data and rebuild intentionally.

### Write it down

Document assumptions, grain, ownership, failure behavior, and trade-offs.

### Explain aloud

Explain why:

```text
ref()
source()
materializations
incrementals
snapshots
tests
contracts
Python models
```

exist and how they interact.


## 70. Mental Models

> **dbt is primarily a transformation framework, not an ingestion platform.**

> **`ref()` is both a relation reference and a dependency declaration.**

> **Sources describe where data comes from; models describe how data is transformed.**

> **Tests encode data invariants.**

> **Incremental models trade recomputation for correctness complexity.**

> **Jinja generates SQL; the database executes SQL.**

> **Snapshots preserve historical state.**

> **Python models are a specialized tool, not a replacement for SQL.**

> **Compiled SQL is part of debugging.**

> **A model's grain determines which tests are meaningful.**

> **A full refresh is a deliberate rebuild mechanism, not a universal repair strategy.**


## 71. Common Beginner Confusions

| Confusion | Correct distinction |
|---|---|
| dbt vs database | dbt defines/manages transformation workflows; the database executes SQL |
| dbt vs orchestrator | dbt focuses on transformation; orchestration coordinates broader workflows |
| dbt model vs table | Model is a definition; table is one possible materialized result |
| model vs source | Model is managed transformation; source is upstream data |
| `ref()` vs `source()` | Model dependency vs external source declaration |
| Jinja vs SQL | Jinja generates; SQL executes |
| compile vs run | Compile generates executable artifacts; run executes models |
| run vs build | Build is a broader build workflow |
| view vs table | Query-time computation vs persisted relation |
| table vs incremental | Full persisted rebuild vs selected/changed processing |
| incremental vs snapshot | Efficient current transformation vs historical change capture |
| snapshot vs SCD2 | dbt snapshot is a mechanism commonly used to implement historical versioning/SCD2 patterns |
| seed vs source | Small static project data vs external/upstream data |
| data test vs unit test | Dataset invariant vs logic behavior |
| macro vs model | Reusable template logic vs transformation node |
| SQL model vs Python model | Relational SQL transformation vs Python-runtime transformation |
| DAG vs execution engine | Dependency structure vs actual compute execution |
| contract vs test | Structural interface guarantee vs data-state validation |
| documentation vs lineage | Human-readable semantics vs dependency relationships |


## 72. Complete Knowledge Checklist

- [ ] dbt purpose
- [ ] ELT
- [ ] dbt project
- [ ] dbt Core
- [ ] dbt-duckdb
- [ ] project structure
- [ ] profiles
- [ ] models
- [ ] sources
- [ ] `ref()`
- [ ] `source()`
- [ ] DAG
- [ ] staging/intermediate/marts
- [ ] grain
- [ ] materializations
- [ ] views
- [ ] tables
- [ ] ephemeral
- [ ] incremental
- [ ] `unique_key`
- [ ] incremental strategies
- [ ] lookback
- [ ] late data
- [ ] `on_schema_change`
- [ ] full refresh
- [ ] microbatch
- [ ] tests
- [ ] generic tests
- [ ] singular tests
- [ ] `not_null`
- [ ] `unique`
- [ ] `accepted_values`
- [ ] `relationships`
- [ ] severity
- [ ] source freshness
- [ ] seeds
- [ ] Jinja
- [ ] macros
- [ ] snapshots
- [ ] SCD2
- [ ] contracts
- [ ] model versions
- [ ] Python models
- [ ] Python model trade-offs
- [ ] documentation
- [ ] lineage
- [ ] exposures
- [ ] model selection
- [ ] `dbt compile`
- [ ] `dbt run`
- [ ] `dbt test`
- [ ] `dbt build`
- [ ] slim CI
- [ ] state-aware selection
- [ ] defer
- [ ] idempotency
- [ ] incremental/full rebuild reconciliation
- [ ] debugging
- [ ] failure recovery
- [ ] production architecture
- [ ] dbt limitations


## 73. Final Exit Criteria

The learner is ready to move forward when they can independently:

1. Explain dbt in simple terms.
2. Explain where dbt fits in an ELT architecture.
3. Create a dbt project.
4. Build staging/intermediate/mart models.
5. Explain and use `ref()`.
6. Define and use sources.
7. Explain DAG execution.
8. Choose an appropriate materialization for a workload.
9. Build an incremental model.
10. Explain `unique_key` and incremental correctness.
11. Handle late-arriving data using lookback.
12. Handle schema evolution.
13. Use full refresh deliberately.
14. Write data tests.
15. Write singular tests.
16. Define source freshness.
17. Use seeds appropriately.
18. Write basic Jinja.
19. Create reusable macros.
20. Build an SCD2 snapshot.
21. Explain model contracts.
22. Explain model versions.
23. Build a Python model.
24. Explain SQL vs Python model trade-offs.
25. Generate documentation.
26. Understand lineage.
27. Understand slim CI/state-aware workflows.
28. Debug compiled SQL.
29. Reconcile incremental output against full rebuild.
30. Explain dbt's production boundaries.
31. Design a production-grade dbt transformation layer.
32. Explain the architecture aloud to another engineer.


## 74. Final Self-Review and Quality Control

Before considering this chapter complete, verify:

- every roadmap-aligned Topic 09 concept is present;
- every major concept progresses from beginner to advanced;
- major concepts include examples;
- SQL examples are understandable;
- YAML examples are understandable;
- Jinja examples are understandable;
- Python model examples identify runtime/version/adapter dependencies;
- incremental processing is explained deeply;
- snapshots are explained deeply;
- testing is explained deeply;
- source freshness is explained;
- contracts and versions are explained;
- slim CI is explained;
- dbt limitations are explained;
- failure scenarios are included;
- debugging is included;
- anti-patterns are included;
- production architecture is included;
- exercises are included;
- interview questions are included;
- architecture questions are included;
- the final checklist is included;
- exit criteria are included.

### Final safety principle

This chapter is self-contained. The hands-on project is documented conceptually inside this Markdown file; it does not require creating additional files to understand the design.

The exact dbt syntax of version/adapter-dependent features must always be checked against the installed dbt version and adapter before production use.
