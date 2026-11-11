# dbt Project Structure and Materializations

> **Stage:** 2C — Data Engineering_3  
> **Module:** 06 — dbt and Analytics Engineering  
> **Topic:** 01 — dbt project structure and materializations  
> **Lab:** `experiments/01_structure/`  
> **Level:** Beginner → Intermediate → Advanced  
> **Local adapter:** DuckDB (`dbt-duckdb`)

## Learning contract

By the end of this lesson, you should be able to:

- Explain dbt's role in ELT, including what dbt does and does not do.
- Initialize and configure a dbt Core project, separate development from production, and explain targets and profiles.
- Write models as SQL `SELECT` statements, connect them with `ref()`, and reason about the DAG.
- Use the core dbt commands and node-selection syntax.
- Organize a project into staging, intermediate, and marts layers.
- Select materializations based on data volume, query patterns, freshness, storage, build time, and warehouse cost.
- Define model grain, surrogate keys, and conformed dimensions.
- Explain schema and alias configuration, development isolation, multi-project patterns, dbt Mesh concepts, and Python-model constraints.
- Apply a readable SQL style, lint with SQLFluff, and complete the local lab with verifiable results.

**Scope note:** This is Topic 01. Sources, seeds, snapshots, incremental strategy design, tests/contracts, documentation governance, Semantic Layer, and orchestration are later topics. Seeds appear only as a practical way to provide small local lab inputs; this lesson does not teach their broader lifecycle.

---

## 1. The mental model: what dbt is

### 1.1 ELT and dbt's place in it

ELT means **Extract, Load, Transform**:

1. An ingestion tool extracts data from operational systems.
2. The data is loaded into a warehouse or lakehouse.
3. dbt transforms data already available in that analytical platform into dependable models for analysts, applications, and downstream data products.

For example, an application database might provide raw `orders`, `customers`, and `payments` tables. dbt can standardize their names and types, combine payments with orders, and publish a fact table for analytics.

dbt is primarily a **transformation development and execution framework**. It adds SQL/Jinja compilation, dependency-aware execution, configuration, testing integration, documentation metadata, and repeatable project conventions around warehouse transformations.

dbt does **not**, by itself:

- Extract data from an application or SaaS API.
- Load raw data into the warehouse as a general ingestion service.
- Replace a scheduler or orchestrator. A scheduled job may invoke `dbt build`, but scheduling is handled by an external scheduler or a managed dbt service.
- Make a poor data model correct automatically.
- Guarantee data quality merely because a model compiles or runs.

**Why it matters:** separating ingestion, transformation, and orchestration makes ownership and failure diagnosis clearer. If raw orders are missing, investigate ingestion/freshness first; if the raw data exists but revenue is wrong, inspect transformation logic and model grain.

### 1.2 How a dbt command becomes warehouse work

A useful simplified flow is:

```text
dbt project files
    │
    ├── SQL models
    ├── Jinja expressions (ref(), config(), variables, macros)
    ├── YAML configuration
    └── profile / target
          │
          ▼
   Parse project and discover dependencies
          │
          ▼
   Compile SQL + Jinja into adapter-appropriate SQL
          │
          ▼
   Execute statements through the adapter
          │
          ▼
   Warehouse objects (views, tables, incremental relations, ...)
```

The details vary by command and engine, but keep these distinctions clear:

- **Parsing** discovers project resources and dependencies.
- **Compilation** renders Jinja and resolves dbt constructs into SQL. `dbt compile` generally compiles without materializing the models.
- **Execution** submits SQL to the configured data platform through the adapter.
- **Materialization** is the strategy that determines how a model's result becomes or updates a database object.
- **DAG** means directed acyclic graph. A model that calls `ref('stg_orders')` declares an upstream dependency on that model. dbt uses the dependency graph to order work and determine selection.

dbt does not normally download all rows and transform them in Python. SQL models execute in the warehouse. This is a major reason to push set-based transformation to the platform that stores the data.

### 1.3 Models, `ref()`, and the DAG

A model is usually a `.sql` file containing a `SELECT` statement. dbt wraps that query in materialization logic according to its configuration.

Example `models/staging/stg_orders.sql`:

```sql
select
    order_id,
    customer_id,
    cast(order_date as date) as order_date,
    lower(status) as status
from {{ ref('raw_orders') }}
```

`ref('raw_orders')` does two jobs:

1. It resolves the model/seed name to the correct database relation for the active target.
2. It tells dbt that `stg_orders` depends on `raw_orders`, so the DAG and selection logic can account for that dependency.

Do not hard-code `database.schema.table` for another dbt model when `ref()` is appropriate. Hard-coded relations can break when a target, schema, alias, or environment changes, and dbt cannot infer the dependency from a literal string.

Acyclic dependency example:

```text
raw_orders ─────► stg_orders ──────┐
                                   ├──► int_orders_payments ───► fct_orders
raw_payments ──► stg_payments ─────┘

raw_customers ─► stg_customers ────────────────────────────────► dim_customers
```

The arrows point from an upstream dependency to a downstream consumer. A circular chain such as `model_a → model_b → model_a` cannot be topologically ordered and is invalid. Break circular business logic into a one-way dependency design.

---

## 2. Install and initialize a reproducible local project

### 2.1 Choose compatible versions

dbt Core and its adapters are versioned packages. Install an adapter that supports the dbt Core version you use; avoid independently upgrading one package and assuming every combination is compatible. The commands below use `uv`, matching the module roadmap. A Python 3.12+ environment is assumed.

From the directory where you keep learning projects:

```bash
mkdir dbt-lab
cd dbt-lab
uv init
uv add dbt-core dbt-duckdb sqlfluff sqlfluff-templater-dbt
uv run dbt --version
```

The command output identifies the installed Core and adapter versions. Record it in your notes. If dependency resolution fails, inspect the package compatibility information and pin a compatible set rather than bypassing the resolver.

`dbt-duckdb` allows a local DuckDB database file to act as the analytical platform. Other adapters connect dbt to platforms such as Snowflake, BigQuery, and Databricks, but adapter-specific materializations and features differ.

### 2.2 Initialize the project

Run:

```bash
uv run dbt init jaffle_shop
cd jaffle_shop
```

Follow the interactive prompts if your installed version asks for a connection. The exact prompt sequence can vary by dbt Core and adapter version. If you already created a project directory, do not initialize a second nested project accidentally.

For this lesson, use the following minimal DuckDB profile. Put it in `profiles.yml` at the project root for the lab and pass that directory explicitly. This is convenient locally; production credentials should be managed through the approved secret mechanism, not committed to Git.

`profiles.yml`:

```yaml
jaffle_shop:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ./jaffle_shop.duckdb
      schema: dev
      threads: 4
    prod:
      type: duckdb
      path: ./jaffle_shop_prod.duckdb
      schema: analytics
      threads: 4
```

Run dbt with `--profiles-dir .` while in this project directory. In a normal personal setup, `profiles.yml` is often kept under `~/.dbt/`; `--profiles-dir` lets the lab keep its profile beside the project. **Do not commit profiles containing credentials.** Add `profiles.yml`, DuckDB database files, `target/`, and `logs/` to `.gitignore`. Section 14 places this project inside the roadmap-prescribed `experiments/01_structure/` workspace; Section 2's `dbt-lab/jaffle_shop/` commands are a standalone bootstrap illustration, not a second lab path.

### 2.3 `dbt_project.yml` versus `profiles.yml`

These files solve different problems:

- `dbt_project.yml` describes the project: its name, model paths, resource configuration, and defaults.
- `profiles.yml` describes connection outputs: adapter, database/path, schema, threads, and targets.
- A **target** is a named output in a profile, such as `dev` or `prod`. `target.name` can be used in Jinja configuration when environment-aware behavior is justified.
- A **schema** is a namespace for relations in the database. Its physical naming can be affected by dbt's schema-generation macro and adapter behavior.

Example `dbt_project.yml`:

```yaml
name: jaffle_shop
version: "1.0.0"
config-version: 2
profile: jaffle_shop

model-paths: ["models"]
seed-paths: ["seeds"]
test-paths: ["tests"]
analysis-paths: ["analyses"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]
target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  jaffle_shop:
    +persist_docs:
      relation: true
      columns: true
    staging:
      +materialized: view
      +tags: ["staging"]
    intermediate:
      +materialized: view
      +tags: ["intermediate"]
    marts:
      +materialized: table
      +tags: ["marts"]

seeds:
  jaffle_shop:
    +schema: raw
```

`config-version: 2` is the dbt project configuration format, not the installed dbt Core major version. Model paths are relative to the project root. The `+` prefix marks a resource configuration property in this YAML configuration style.

Configuration can be set at project, folder, or model level. In the same configuration hierarchy, a more specific model-level setting generally overrides a broader folder/project default for that property. Command-line flags and adapter capabilities can affect execution; do not treat YAML precedence as the only influence on final behavior.

Example model-level override:

```sql
{{ config(materialized='view', alias='orders_current') }}

select ...
```

The ellipsis is illustrative and is not a complete runnable model. The complete lab files appear later.

### 2.4 Development and production targets

A target controls connection settings; it does not automatically make a production deployment safe. A useful separation is:

- `dev`: developer-owned local database/schema and fast iteration.
- `ci`: isolated schema or database per pull request/build.
- `prod`: controlled credentials and destination, invoked only by a production job.

Never assume that naming a target `prod` protects production. Access controls, deployment permissions, CI policy, and the configured database/schema must enforce that boundary. Avoid allowing a local developer profile to write to production by default.

Check project/profile resolution:

```bash
uv run dbt debug --profiles-dir .
uv run dbt parse --profiles-dir .
```

`dbt debug` checks connection/profile setup; `dbt parse` checks project parsing and resource definitions. Neither proves that every model query will execute successfully.

---

## 3. Layered project architecture

### 3.1 Why use layers?

Layers separate source cleanup from reusable business logic and consumer-facing data products. This limits the blast radius of change and makes each model easier to understand and validate.

| Layer | Responsibility | Typical naming | Typical materialization |
|---|---|---|---|
| Staging | Rename, cast, standardize, light cleanup; usually one model per raw input | `stg_orders`, `stg_customers`, `stg_payments` | View |
| Intermediate | Join, deduplicate, derive reusable business concepts | `int_orders_payments`, `int_customer_orders` | View or ephemeral; table when justified |
| Marts | Consumer-facing facts and dimensions with explicit grain and business meaning | `fct_orders`, `dim_customers` | Table, incremental, or a platform-supported materialized view |

These are conventions, not rigid laws. A layer should communicate responsibility, not simply be a folder for every model.

**Staging should usually remain close to its source.** Standardizing `status` or casting a date belongs there; implementing a complex revenue policy in staging makes every downstream consumer inherit business semantics too early.

**Intermediate models** centralize joins and reusable logic. Do not create an intermediate model for every trivial expression; use one when it clarifies logic or has multiple consumers.

**Marts** define the shape that analysts and applications consume. Their columns, grain, names, and semantics should be deliberate. Avoid exposing raw implementation details or uncontrolled `SELECT *` in a mart.

### 3.2 Complete lab project tree

The lab will use seed CSV files as small raw-like inputs. They are intentionally tiny and local; in production, these inputs would typically be loaded by an ingestion process. `+schema: raw` makes the seed resources use the configured schema-generation behavior for the raw layer; with the default schema macro and target schema `dev`, the resulting schema is normally `dev_raw`. This is not the same as declaring formal dbt sources, which is covered in Topic 02.

```text
experiments/01_structure/         # roadmap-prescribed lab workspace
├── .gitignore                    # ignores local secrets, databases, and artifacts
├── pyproject.toml                # uv environment and dependencies
└── jaffle_shop/                  # dbt project root; run dbt commands here
    ├── dbt_project.yml
    ├── profiles.yml              # local-only; do not commit
    ├── .sqlfluff
    ├── seeds/
    │   ├── raw_orders.csv
    │   ├── raw_customers.csv
    │   └── raw_payments.csv
    ├── models/
    │   ├── staging/
    │   │   ├── stg_orders.sql
    │   │   ├── stg_customers.sql
    │   │   └── stg_payments.sql
    │   ├── intermediate/
    │   │   └── int_orders_payments.sql
    │   └── marts/
    │       ├── fct_orders.sql
    │       └── dim_customers.sql
    ├── macros/
    │   └── generate_schema_name.sql  # optional environment-isolation example
    ├── tests/                     # optional singular tests added later
    ├── analyses/
    ├── snapshots/
    ├── target/                    # generated; do not commit
    └── logs/                      # generated; do not commit
```

### 3.3 Naming and grain

**Grain** is the precise meaning of one row in a relation. Write the grain down before writing joins.

| Model | Grain | Purpose | Suggested materialization |
|---|---|---|---|
| `stg_orders` | One row per `order_id` from raw orders | Standardized order attributes | View |
| `stg_customers` | One row per `customer_id` from raw customers | Standardized customer attributes | View |
| `stg_payments` | One row per `payment_id` from raw payments | Standardized payment attributes and amount | View |
| `int_orders_payments` | One row per `order_id`, with payments aggregated to that order | Join orders to payment totals without multiplying order rows | View for reusable logic |
| `fct_orders` | One row per `order_id` | Order-level analytical facts and payment totals | Table in this small lab |
| `dim_customers` | One row per `customer_id` | Customer dimension with a stable warehouse key | Table in this small lab |

The roadmap exercise has two distinct deliverables: (1) a paper design listing two intermediate models and three marts with their grains, and (2) a runnable core DAG implementing the explicitly required `int_orders_payments`, `fct_orders`, and `dim_customers`. Complete this planning table before coding; the two additional planned models do not need to be added to the core runnable DAG in this lesson.

| Planned model | Layer | Grain | Purpose | Implemented in core lab? |
|---|---|---|---|---|
| `int_orders_payments` | Intermediate | One row per order | Aggregate payment rows to order grain before joining | Yes |
| `int_customer_orders` | Intermediate | One row per customer | Aggregate order count and order-value measures by customer | Planning only |
| `fct_orders` | Mart | One row per order | Order-level measures and status | Yes |
| `fct_payments` | Mart | One row per payment | Payment-level amount, method, and order key | Planning only |
| `dim_customers` | Mart | One row per customer (or per customer version if historized) | Customer attributes and identity policy | Yes |

Do not add the planning-only models to the core DAG just to satisfy a count. They are design exercises that make the required two-intermediate/three-mart planning explicit while keeping the executable lab small and consistent with the roadmap's named implementation requirements.

A join can change grain. If an order has three payment records and you join those rows directly to an order table, that order appears three times. Aggregate payments to order grain first, then join. This is one of the most important correctness rules in analytical modelling.

---

## 4. Materializations: what changes when a model is built?

A materialization defines how dbt persists or exposes the result of a model. Exact support and implementation details depend on the adapter and platform.

### 4.1 Comparison

| Materialization | What dbt creates/does | Strengths | Costs and risks | Good fit |
|---|---|---|---|---|
| `view` | A database view whose query is evaluated when consumers query it | Low persisted storage; quick model build; source changes can be visible without rebuilding the view | Repeated downstream queries may re-run complex logic; query latency and warehouse compute can rise | Staging and lightweight intermediate models |
| `table` | A persisted table rebuilt by dbt according to adapter/materialization implementation | Predictable read performance; expensive transformations run at build time; stable snapshot between builds | Build time and storage; data can be stale between runs; full rebuilds can be expensive | Frequently queried marts and expensive joins/aggregations |
| `incremental` | Creates/updates a table using an incremental strategy after initial build | Avoids rebuilding all historical rows when designed correctly | More complex correctness, late-arriving data, deduplication, schema-change and recovery concerns; strategy support varies | Large append/change datasets with a reliable incremental design |
| `ephemeral` | Inlines the model SQL as a CTE in downstream compiled SQL; does not create a warehouse relation | Avoids a separate object; useful for small reusable transformations | Repeated/inlined SQL can make downstream SQL large or expensive; cannot be queried as a standalone relation | Small helper logic with limited fan-out |
| `materialized_view` | Requests a platform-managed materialized view where supported | May refresh/precompute results with platform-specific behavior | Adapter/warehouse support and refresh semantics differ; operational behavior is not universal | Platform-specific pre-aggregations or low-latency serving when supported |

The `materialized_view` option is not portable across all adapters. Verify support, refresh behavior, limitations, and configuration against the installed adapter and warehouse documentation before relying on it. If unsupported by DuckDB adapter/version combination, use `table` for the local comparison and treat materialized views as a platform-specific design option, not a required lab step.

### 4.2 Build time, query time, storage, and cost

Think in terms of total workload, not a blanket rule that tables are always faster:

- **View:** lower storage and often faster builds; repeated reads may recompute complex logic. A view does not guarantee fresh source data if upstream ingestion itself is stale.
- **Table:** spends compute at build time and storage to reduce repeated query work. A daily rebuild may be a poor choice for a huge table if only a small fraction changes.
- **Incremental:** can lower build cost, but only if change detection, unique keys, merge behavior, and late-arriving data are handled correctly. Incorrect incremental logic can silently omit or duplicate rows.
- **Ephemeral:** no standalone relation/storage; SQL is expanded into downstream queries, which may duplicate work or complicate query plans.
- **Materialized view:** behavior is controlled partly by the database engine. Refresh schedules, incremental refresh eligibility, and query rewrite behavior are platform-specific.

Cost is workload-specific. Compare build duration, query duration, bytes scanned or compute credits where available, storage, refresh frequency, concurrency, and correctness requirements. A local DuckDB timing is useful for learning the mechanics but is not evidence of cloud-warehouse cost at scale.

### 4.3 Materialization decision framework

For every model, answer these questions:

1. How many rows and how expensive is the transformation?
2. How often is it queried, and by how many consumers?
3. What freshness does the consumer require?
4. Is repeated computation more expensive than persisted storage and rebuilds?
5. Can the model be rebuilt deterministically?
6. If incremental, can updates/deletes/late-arriving data be identified safely?
7. Does the adapter support the chosen strategy and its options?
8. What is the recovery plan after a failed or incorrect build?

A defensible starting point for this lab is: staging as views, the reusable order-payment join as a view, and marts as tables. Then change one staging model from view to table and measure the difference under the same conditions.

### 4.4 Incremental and ephemeral cautions

This lesson introduces the options but does not implement a production incremental model. Incremental correctness requires a unique key or another sound merge/deduplication design, a reliable change filter, an understanding of adapter-specific strategies, and a full-refresh recovery path. See Topic 02 for the complete incremental treatment.

Ephemeral models are useful for tiny helper transformations, but do not use them indiscriminately. If a helper has many downstream consumers or expensive SQL, a persisted view/table may be easier to inspect and may avoid repeated expansion.

---

## 5. Implement the Jaffle Shop-style lab

The following files form one consistent minimal project. Create them exactly as shown. The raw CSVs contain small illustrative data, not a complete production dataset.

### 5.1 `.gitignore`

Create this file at `experiments/01_structure/.gitignore` (the workspace root, one directory above `jaffle_shop/`). The patterns intentionally cover the nested project and the parent `uv` environment.

```gitignore
profiles.yml
*.duckdb
*.duckdb.wal
target/
logs/
dbt_packages/
.venv/
__pycache__/
```

### 5.2 Seed inputs

`seeds/raw_orders.csv`:

```csv
order_id,customer_id,order_date,status
1,101,2025-01-03,completed
2,102,2025-01-04,returned
3,101,2025-01-05,completed
4,103,2025-01-06,shipped
```

`seeds/raw_customers.csv`:

```csv
customer_id,first_name,last_name,email
101,Ada,Lovelace,ada@example.com
102,Grace,Hopper,grace@example.com
103,Katherine,Johnson,katherine@example.com
```

`seeds/raw_payments.csv`:

```csv
payment_id,order_id,payment_method,amount_cents
1001,1,card,2500
1002,1,gift_card,500
1003,2,card,1200
1004,3,bank_transfer,3400
1005,4,card,1800
```

### 5.3 `dbt_project.yml`

Use the complete configuration from Section 2.3. It establishes `view` defaults for staging/intermediate, `table` defaults for marts, and the `raw` schema setting for seeds.

### 5.4 `profiles.yml`

Use the complete local profile from Section 2.2. Keep it untracked. For a clean lab, the target should be `dev`; switch to `prod` only when deliberately demonstrating a separate database.

### 5.5 Staging models

`models/staging/stg_orders.sql`:

```sql
with source as (

    select * from {{ ref('raw_orders') }}

),

renamed as (

    select
        cast(order_id as integer) as order_id,
        cast(customer_id as integer) as customer_id,
        cast(order_date as date) as order_date,
        lower(trim(status)) as status
    from source

)

select
    order_id,
    customer_id,
    order_date,
    status
from renamed
```

`models/staging/stg_customers.sql`:

```sql
with source as (

    select * from {{ ref('raw_customers') }}

),

renamed as (

    select
        cast(customer_id as integer) as customer_id,
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        lower(trim(email)) as email
    from source

)

select
    customer_id,
    first_name,
    last_name,
    email
from renamed
```

`models/staging/stg_payments.sql`:

```sql
with source as (

    select * from {{ ref('raw_payments') }}

),

renamed as (

    select
        cast(payment_id as integer) as payment_id,
        cast(order_id as integer) as order_id,
        lower(trim(payment_method)) as payment_method,
        cast(amount_cents as integer) as amount_cents,
        cast(amount_cents as decimal(12, 2)) / 100 as amount
    from source

)

select
    payment_id,
    order_id,
    payment_method,
    amount_cents,
    amount
from renamed
```

Staging intentionally does not implement complex business rules. It standardizes the input and preserves source-level grain.

### 5.6 Intermediate model

`models/intermediate/int_orders_payments.sql`:

```sql
with orders as (

    select
        order_id,
        customer_id,
        order_date,
        status
    from {{ ref('stg_orders') }}

),

payments_by_order as (

    select
        order_id,
        sum(amount) as payment_total,
        count(*) as payment_count
    from {{ ref('stg_payments') }}
    group by order_id

),

joined as (

    select
        orders.order_id,
        orders.customer_id,
        orders.order_date,
        orders.status,
        coalesce(payments_by_order.payment_total, 0) as payment_total,
        coalesce(payments_by_order.payment_count, 0) as payment_count
    from orders
    left join payments_by_order
        on orders.order_id = payments_by_order.order_id

)

select
    order_id,
    customer_id,
    order_date,
    status,
    payment_total,
    payment_count
from joined
```

**Grain:** one row per order. Payment rows are aggregated before joining, so multiple payments do not multiply orders. `coalesce` makes an order with no payment rows have a zero total/count; confirm that this meaning is appropriate for your business rather than treating it as universally correct.

### 5.7 Mart models

`models/marts/fct_orders.sql`:

```sql
with order_details as (

    select
        order_id,
        customer_id,
        order_date,
        status,
        payment_total,
        payment_count
    from {{ ref('int_orders_payments') }}

)

select
    order_id,
    customer_id,
    order_date,
    status,
    payment_total,
    payment_count,
    case
        when status = 'returned' then 0
        else payment_total
    end as recognized_payment_total
from order_details
```

**Grain:** one row per order. `payment_total` records observed payment amount; `recognized_payment_total` is a deliberately simple illustrative rule that zeroes the value for returned orders. This is not a universal accounting rule. A real finance-approved definition would specify refunds, partial returns, chargebacks, taxes, currency, and recognition timing.

`models/marts/dim_customers.sql`:

```sql
with customers as (

    select
        customer_id,
        first_name,
        last_name,
        email
    from {{ ref('stg_customers') }}

)

select
    customer_id,
    first_name,
    last_name,
    concat(first_name, ' ', last_name) as full_name,
    email
from customers
```

**Grain:** one row per customer. This basic dimension uses the source `customer_id` as its key. A production warehouse may require a surrogate key, historization, privacy controls, and a documented policy for changing customer identity.

### 5.8 DAG and model materialization map

```text
seed: raw_orders ───────► stg_orders ─────────┐
                                              │
seed: raw_payments ─────► stg_payments ───────┼──► int_orders_payments ───► fct_orders
                                              │
seed: raw_customers ────► stg_customers ──────────────────────────────────► dim_customers
```

| Resource | Default | Why |
|---|---|---|
| `raw_*` seeds | Table | Tiny local input tables loaded from CSV for the lab |
| `stg_*` | View | Lightweight standardization and minimal storage |
| `int_orders_payments` | View | Reusable join/aggregation logic; build is cheap |
| `fct_orders` | Table | Consumer-facing mart with stable read behavior |
| `dim_customers` | Table | Consumer-facing dimension |

### 5.9 Build and inspect

From the `jaffle_shop/` directory:

```bash
uv run dbt debug --profiles-dir .
uv run dbt seed --profiles-dir .
uv run dbt compile --profiles-dir .
uv run dbt run --profiles-dir .
uv run dbt test --profiles-dir .
uv run dbt build --profiles-dir .
```

The test command may report that no tests are defined; that is not evidence of data correctness. Topic 04 covers adding comprehensive tests. In this lab, verify the result directly with `dbt show`, DuckDB SQL, and the row/grain checks below.

- `dbt seed` loads the CSV files as relations.
- `dbt compile` renders SQL into the target directory without building the model relations.
- `dbt run` runs models but does not run the full seed/test/docs lifecycle.
- `dbt test` runs configured tests.
- `dbt build` runs selected resources in dependency-aware order and includes applicable seeds, models, tests, and snapshots according to selection and resource types. It is the usual command when you want a build plus its configured tests.
- `dbt show` previews a query/model result in supported versions/adapters; check `uv run dbt show --help` if the installed version exposes different options.
- `dbt docs generate` creates documentation artifacts; `dbt docs serve` serves the generated site locally.

Inspect compiled files under `target/compiled/jaffle_shop/` and execution artifacts such as `target/manifest.json` and `target/run_results.json`. Paths can vary slightly by installed version and configuration.

Preview models:

```bash
uv run dbt show --select fct_orders --profiles-dir .
uv run dbt show --select dim_customers --profiles-dir .
```

Expected logical output for `fct_orders`:

| order_id | customer_id | payment_total | payment_count | recognized_payment_total |
|---:|---:|---:|---:|---:|
| 1 | 101 | 30.00 | 2 | 30.00 |
| 2 | 102 | 12.00 | 1 | 0.00 |
| 3 | 101 | 34.00 | 1 | 34.00 |
| 4 | 103 | 18.00 | 1 | 18.00 |

Order row order is not guaranteed unless the query specifies `ORDER BY`. Values are the expected result from the supplied CSVs and SQL; they have not been claimed as runtime-tested in this document.

Expected logical output for `dim_customers` is three rows, one per customer, with full names Ada Lovelace, Grace Hopper, and Katherine Johnson.

---

## 6. Controlled view-versus-table experiment

The purpose is to compare a controlled change, not to assume a universal performance outcome.

1. Confirm `stg_orders` is configured as a view through the folder default.
2. Build the project and record the build duration.
3. Preview/query the downstream `fct_orders` result repeatedly and record observed duration if your tooling exposes it.
4. Change only `stg_orders` to a table:

   ```sql
   {{ config(materialized='table') }}

   with source as (

       select * from {{ ref('raw_orders') }}

   )

   select
       cast(order_id as integer) as order_id,
       cast(customer_id as integer) as customer_id,
       cast(order_date as date) as order_date,
       lower(trim(status)) as status
   from source
   ```

5. Run `uv run dbt run --select stg_orders+ --profiles-dir .` to rebuild that model and its descendants.
6. Repeat the same measurements with the same data and query conditions.
7. Restore the original staging SQL/configuration after the experiment.

Record at least:

| Variant | Build duration | Repeated downstream query duration | Stored object type | Interpretation |
|---|---:|---:|---|---|
| Staging as view | Fill in from observation | Fill in from observation | View | Baseline |
| Staging as table | Fill in from observation | Fill in from observation | Table | Compare; do not assume faster |

For a tiny local dataset, timings may be dominated by startup, caching, and measurement noise. Do multiple runs, compare medians, and do not generalize the results to a cloud warehouse. The expected qualitative trade-off is that a table adds build/storage work but may avoid repeated computation for more expensive transformations; the actual query planner may optimize views effectively.

---

## 7. Node selection: build exactly what you intend

Selection syntax is central to efficient development and CI. Run `uv run dbt --help` and `uv run dbt build --help` if options differ in your installed version.

### 7.1 Selection patterns

Assume the core DAG from Section 5.8.

| Command | Meaning |
|---|---|
| `dbt run --select stg_orders` | Run only `stg_orders` |
| `dbt run --select +fct_orders` | Select `fct_orders` and all its ancestors/parents |
| `dbt run --select fct_orders+` | Select `fct_orders` and its descendants/children |
| `dbt run --select +fct_orders+` | Select the model, its ancestors, and descendants |
| `dbt run --select tag:staging` | Select resources matching the `staging` tag in this project's configuration |
| `dbt run --select path:models/staging` | Select resources under the staging path; path selector syntax is supported in current dbt Core selection syntax |
| `dbt run --select stg_orders --exclude stg_customers` | Select `stg_orders`, excluding `stg_customers` (the exclusion is redundant in this exact example but illustrates the flag) |
| `dbt build --select state:modified+ --state path/to/prod_artifacts` | Select modified resources and downstream dependents relative to saved state artifacts |

`+model` means parents/upstream; `model+` means children/downstream. These are easy to reverse—draw the DAG and predict the selected nodes before executing.

The `staging` tag in `dbt_project.yml` is inherited by models in the staging folder. Tags are metadata selectors, not SQL filters.

`state:modified+` requires a usable comparison state, typically a prior production `manifest.json`, supplied by `--state`. The plus selects downstream dependents of modified resources. It is not a standalone magic command and should not be used without a deliberate state-artifact workflow. This lesson introduces the syntax; slim CI and `--defer` are developed in the performance topic.

### 7.2 Lab selection exercises

From the project root, predict and then run these:

```bash
# Only the staging model
uv run dbt run --select stg_orders --profiles-dir .

# fct_orders plus its parents
uv run dbt build --select +fct_orders --profiles-dir .

# fct_orders plus its children (likely none in the core graph)
uv run dbt build --select fct_orders+ --profiles-dir .

# All staging-tagged models
uv run dbt run --select tag:staging --profiles-dir .

# A folder selection
uv run dbt run --select path:models/staging --profiles-dir .

# Select a mart and exclude a particular upstream node
uv run dbt build --select +fct_orders --exclude stg_payments --profiles-dir .
```

The last command is a selection-mechanics demonstration, not a valid way to produce a complete `fct_orders` build if `stg_payments` is needed. Depending on selection and existing relations, dbt may skip required work or fail. Do not exclude a required ancestor in a production build unless the dependency is already intentionally satisfied by a safe defer/state setup.

For a production-state exercise, first preserve a manifest from a successful baseline build, then modify a model and run the state selector against that baseline. State selection behavior can depend on the dbt version and the state comparison; verify the selected nodes with `--print` where supported or inspect dbt's selection output before running.

---

## 8. Schema names, aliases, and developer isolation

### 8.1 Schema and alias are different

- **Schema** controls the namespace in which a relation is created.
- **Alias** controls the database relation name, independent of the model filename.
- The model filename/name remains important for `ref()` and dbt's graph. Use aliases only when the physical relation needs a different name for a clear reason.

Example:

```sql
{{ config(
    materialized='table',
    alias='orders'
) }}

select
    order_id,
    customer_id,
    order_date,
    status
from {{ ref('stg_orders') }}
```

This is a complete illustrative model only if the selected columns exist in `stg_orders`; as written, it is valid against the lab's staging schema. Avoid creating aliases that collide with other models in the same schema.

### 8.2 Default schema generation

With the default dbt schema-generation behavior, a custom schema configured on a resource is generally combined with the target schema rather than simply replacing it. For example, target schema `dev` and custom schema `raw` commonly produce `dev_raw`. This helps avoid collisions between developers. Adapter details can differ.

Do not casually replace `generate_schema_name`; it affects where many resources are built. If overriding it, preserve safe target isolation and validate its behavior for both `dev` and `prod`.

### 8.3 Custom schemas per layer and optional `generate_schema_name`

A project can assign a custom schema to each model layer. The following is an **optional replacement for the existing `models: jaffle_shop:` block**, not part of the lab's active `dbt_project.yml`. Use it only when your team intentionally wants separate physical schemas for each layer; retain any additional project-level settings your own project needs:

```yaml
models:
  jaffle_shop:
    +persist_docs:
      relation: true
      columns: true
    staging:
      +materialized: view
      +tags: ["staging"]
      +schema: staging
    intermediate:
      +materialized: view
      +tags: ["intermediate"]
      +schema: intermediate
    marts:
      +materialized: table
      +tags: ["marts"]
      +schema: marts
```

With the default schema-generation behavior and target schema `dev`, these custom schema names commonly resolve to `dev_staging`, `dev_intermediate`, and `dev_marts`. This preserves a developer-specific prefix while separating layers. If you enable this configuration, update your expected physical-schema names and permissions accordingly; dbt `ref()` dependencies continue to resolve the relations. Keep the lab's simpler active configuration unless you are deliberately testing custom schemas.

The default macro is often sufficient. If your team needs a custom rule, add `macros/generate_schema_name.sql`. The following example keeps the default target schema for resources with no custom schema and adds a custom layer suffix when one is specified:

```sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is not none -%}
        {%- set custom_schema_name = custom_schema_name | trim -%}
    {%- endif -%}
    {%- if custom_schema_name is none or custom_schema_name == '' -%}
        {{ default_schema }}
    {%- else -%}
        {{ default_schema }}_{{ custom_schema_name }}
    {%- endif -%}
{%- endmacro %}
```

This intentionally preserves the target schema prefix. Do not return a fixed schema such as `analytics` for every developer: that can cause collisions and overwrite risk. Test generated names with your actual target values and adapter before production use. The macro's `node` argument is available for more advanced policies but is unused here.

A common strategy is `dev_<developer>_staging`, `dev_<developer>_marts`, and stable production schemas. How names are assembled should be documented and consistent with permissions and cleanup procedures.

---

## 9. Dimensional modelling in dbt

### 9.1 Grain comes before columns

A fact table records events or measurements at a declared grain. A dimension describes the entities used to group or filter facts.

- `fct_orders`: one row per order.
- `dim_customers`: one row per customer in this simplified current-state example.
- `customer_id` in the fact is a foreign-key-like reference to the customer dimension's business key.

Never join two facts at incompatible grains without an explicit aggregation or allocation rule. For example, joining payment-grain rows directly to order-grain rows can duplicate order measures. Aggregate one side to the target grain first.

### 9.2 Surrogate keys and `generate_surrogate_key`

A **surrogate key** is a warehouse-managed identifier that does not carry business meaning. It can help when source identifiers collide across systems or when a dimension's historical versions need distinct keys. A **natural/business key** comes from the source domain, such as `customer_id`.

The `dbt_utils.generate_surrogate_key` macro is provided by the external `dbt_utils` package; it is not a built-in macro available automatically in every project. To use it, declare a compatible package version in `packages.yml`, run `dbt deps`, and follow the package's documented API/version. Example usage after installing the package:

```sql
{{ dbt_utils.generate_surrogate_key([
    'customer_id',
    'email'
]) }} as customer_key
```

This expression is illustrative and assumes those fields define the desired key inputs. Do not add mutable attributes such as email to a key unless changing email is intended to change the key. For a simple one-source customer dimension, `customer_id` may be sufficient. For multi-source identity, define a conformed identity policy before key generation.

Surrogate-key behavior for nulls and serialization is package-version dependent; use the macro rather than hand-concatenating columns without delimiters and null handling. Test collision/identity assumptions for the actual business key.

### 9.3 Conformed dimensions

A **conformed dimension** has consistent identity, definitions, and attributes across multiple fact tables or business processes. If sales and support facts both refer to `dim_customers`, they should use the same customer identity rules and agreed definitions. Merely giving two unrelated tables the same name does not make them conformed.

Conformed dimensions matter because they allow meaningful cross-process analysis without inconsistent customer counts or filters. They require governance of keys, attribute definitions, history, and ownership—not just SQL reuse.

---

## 10. Multi-environment, multi-project, and dbt Mesh concepts

### 10.1 Environments

Development, CI, staging, and production should have intentional target/schema/database policies. Environment isolation prevents a developer or pull request from replacing production relations and lets reviewers validate changes independently.

Common controls include:

- Different credentials and permissions for dev and production.
- Developer- or PR-specific schemas for ephemeral builds.
- Production artifacts retained for state comparison.
- Explicit deployment jobs and protected branches.
- A documented cleanup process for temporary schemas.
- A stable rule for target schema, custom schemas, aliases, and database names.

`target.name` can conditionally change behavior, but conditionals should be few and obvious. Do not bury business logic in environment checks or let two environments silently build incompatible schemas.

### 10.2 Multiple dbt projects

A single project is easier to understand and refactor while model ownership and scale are manageable. Split projects when domain ownership, deployment cadence, access boundaries, or team autonomy justify the extra coordination. A split introduces versioning, contracts/interfaces, dependency management, and more complex lineage.

### 10.3 dbt Mesh and cross-project references

**dbt Mesh** is an architectural approach for multiple dbt projects to publish and consume governed data products. Cross-project references require compatible dbt platform capabilities, project configuration, and supported versions; exact setup depends on whether you use dbt Cloud and which features are enabled. Do not assume ordinary `ref('model')` automatically resolves arbitrary models in another project.

At a conceptual level:

- A producer project owns a domain model and exposes an agreed interface.
- A consumer project declares a dependency on that published interface.
- Ownership, access, versions, freshness expectations, and breaking-change policy are explicit.
- Cross-project lineage and build/defer behavior are managed using the supported Mesh mechanisms.

For this lesson, understand the architecture and trade-offs; do not attempt cross-project references in the DuckDB lab.

---

## 11. Python models: when SQL is still better

dbt Python models are not a generic way to run arbitrary Python in every adapter. Execution depends on the platform and adapter: examples include Snowpark on Snowflake, PySpark on Databricks, and Python/DataFrame support on BigQuery under its supported environment. Support, dependencies, package availability, limitations, and output behavior differ. DuckDB local support should be checked against the installed `dbt-duckdb` version and its documented capabilities; this lab uses SQL only.

Use SQL when the transformation is relational: joins, filters, casts, window functions, and aggregations. SQL is usually easier for warehouse optimizers to plan and easier for analysts to inspect.

Consider Python when the computation genuinely benefits from a Python ecosystem or algorithm that is awkward in SQL and the target platform supports it reliably. Evaluate:

- Data movement and execution location.
- Dependency packaging and versioning.
- Runtime/compute cost.
- Reproducibility and determinism.
- Testing and debugging.
- Operational observability and maintainability.
- Whether the result could be expressed more simply in SQL.

Do not choose Python merely because the engineer is more comfortable with it. A Python model still participates in dbt's model/dependency workflow, but the runtime semantics and supported features are adapter-specific.

---

## 12. SQL style, CTE organization, and SQLFluff

### 12.1 Readable SQL as an engineering control

A model should have a clear purpose, explicit grain, stable output columns, and a dependency graph that can be understood during code review.

Prefer named CTEs over deeply nested subqueries when the CTEs represent meaningful steps:

```sql
with orders as (

    select
        order_id,
        customer_id,
        order_date
    from {{ ref('stg_orders') }}

),

orders_with_customer as (

    select
        orders.order_id,
        orders.order_date,
        customers.customer_id
    from orders
    left join {{ ref('stg_customers') }} as customers
        on orders.customer_id = customers.customer_id

)

select
    order_id,
    order_date,
    customer_id
from orders_with_customer
```

This is an illustrative pattern; the actual mart should select only columns needed by its consumers. CTEs improve readability but do not guarantee a physical materialization or a particular query plan. The warehouse optimizer determines execution details.

### 12.2 Common mistakes and anti-patterns

- **One giant model:** difficult to test, review, reuse, and troubleshoot. Split along meaningful responsibilities and grains.
- **Business logic in staging:** makes raw cleanup inconsistent with the staging layer's purpose and can hide business rules.
- **Everything as a table:** increases storage and rebuild work, including for cheap transformations.
- **Everything as a view:** can make repeated expensive logic slow for downstream consumers.
- **Circular dependencies:** impossible to order; redesign as a one-way graph.
- **Uncontrolled `SELECT *` in marts:** upstream schema changes can silently alter a consumer-facing contract, expose columns unintentionally, or create ambiguous joins. `SELECT *` can be useful temporarily in early staging, but explicitly select stable columns in marts.
- **No declared grain:** joins multiply rows and aggregates become wrong while SQL still runs.
- **Overuse of ephemeral models:** inlining may create huge compiled SQL and repeated work.
- **Unnecessary Python:** moves simple relational work away from the SQL engine and adds runtime/dependency complexity.
- **Unsafe schema customization:** developers collide with one another or overwrite production relations.

### 12.3 SQLFluff configuration

Install both SQLFluff and its dbt templater (already included in the setup commands). Create `.sqlfluff` at the project root:

```ini
[sqlfluff]
dialect = duckdb
templater = dbt
sql_file_exts = .sql
max_line_length = 100

[sqlfluff:templater:dbt]
project_dir = .
profiles_dir = .
profile = jaffle_shop
target = dev

[sqlfluff:indentation]
tab_space_size = 4
indented_joins = false
indented_using_on = false
```

SQLFluff configuration options can vary by version. If a setting is rejected, inspect `uv run sqlfluff config --show` and the documentation for the installed version. The dbt templater may invoke project parsing and need the same adapter/profile dependencies as dbt itself.

Run:

```bash
uv run sqlfluff lint models/
uv run sqlfluff fix models/ --force
uv run sqlfluff lint models/
```

Use `fix` carefully and inspect the diff. Automated formatting can change layout, but it cannot decide whether a join has the correct grain or whether business logic is correct. Do not suppress a rule just to make CI green without documenting why. If the project uses a different SQLFluff version or dialect, pin and validate the configuration consistently in local development and CI.

---

## 13. Core dbt command reference

| Command | Primary purpose | What it does not prove |
|---|---|---|
| `dbt init` | Create a starter project and connection setup | That the profile, model SQL, and permissions are all correct |
| `dbt debug` | Diagnose profile/connection configuration | That all models compile and execute |
| `dbt parse` | Parse resources and dependencies | That warehouse SQL is valid |
| `dbt compile` | Compile Jinja/model SQL | That the model relation was built or data is correct |
| `dbt run` | Execute selected models | That tests passed |
| `dbt test` | Execute configured tests | That untested business rules are correct |
| `dbt build` | Build selected resources and run applicable tests in dependency-aware order | That missing tests or weak assertions provide meaningful guarantees |
| `dbt show` | Preview a model/query result where supported | That the result is complete, performant at scale, or semantically correct |
| `dbt docs generate` | Generate documentation/catalog artifacts from project metadata and available relation metadata | That descriptions are complete or accurate |
| `dbt docs serve` | Serve generated documentation locally | That documentation is current unless regenerated |

For the lab:

```bash
uv run dbt docs generate --profiles-dir .
uv run dbt docs serve --profiles-dir .
```

Open the local URL printed by the command. Stop the server with the terminal interrupt key when finished. The exact URL and CLI options can vary by version.

---

## 14. Hands-on exercise: `experiments/01_structure/`

This exercise corresponds to the roadmap's Topic 01 lab. Work through the steps in order and retain evidence of the result.

### Task A — Initialize and inspect

From the repository/module root, create the roadmap-prescribed workspace and initialize a `uv` environment there:

```bash
mkdir -p experiments/01_structure
cd experiments/01_structure
uv init --bare
uv add dbt-core dbt-duckdb sqlfluff sqlfluff-templater-dbt
uv run dbt init jaffle_shop
cd jaffle_shop
```

The dbt project root is now `experiments/01_structure/jaffle_shop/`, inside the required `experiments/01_structure/` lab workspace. If the interactive `dbt init` flow creates or requests a connection/profile, keep the generated project directory and then use the DuckDB `profiles.yml` from Section 2.2. The `uv` environment lives in the parent lab workspace, so `uv run` from the child project uses that environment; if your `uv` version/workspace setup does not discover the parent project, run `uv run --project .. dbt ...` or create the `pyproject.toml` in the project root and install the dependencies there. Do not create a second nested `jaffle_shop/jaffle_shop/` directory.

1. Run `uv run dbt --version`, `uv run dbt debug --profiles-dir .`, and `uv run dbt parse --profiles-dir .`.
2. Confirm the profile's active target is `dev`.
3. Confirm `profiles.yml` and generated database/artifact files are ignored by Git.

**Evidence:** record the dbt Core/adapter versions and the successful profile/parse output.

### Task B — Build the layered DAG

1. Create the three CSV files and six model files from Section 5 in the `jaffle_shop/` project root.
2. Complete the planning table in Section 3.3, including both intermediate models, all three planned marts, and each model's grain.
3. Run `uv run dbt seed --profiles-dir .`.
4. Run `uv run dbt compile --profiles-dir .`, then inspect compiled SQL in `target/compiled/`.
5. Run `uv run dbt build --profiles-dir .`.
6. Draw the core DAG from Section 5.8 and explain every edge.

**Evidence:** the compiled model SQL exists; the `fct_orders` result has four rows and payment totals of 30, 12, 34, and 18; `dim_customers` has three rows. These are expected outcomes from the supplied fixture, not claims of having executed the commands in your environment.

### Task C — Validate grain manually

Use `dbt show` or query the DuckDB relations with a SQL client:

```sql
select count(*) as row_count,
       count(distinct order_id) as distinct_orders
from <your_dev_schema>.fct_orders;
```

Replace `<your_dev_schema>` with the physical schema resolved by your profile and schema-generation configuration. Do not paste angle-bracket placeholders literally into SQL. The expected counts are `4` and `4`.

For `dim_customers`, check `count(*) = count(distinct customer_id) = 3`. Then reason through what would happen if `stg_payments` were joined to orders before aggregation. Demonstrate the duplicate order rows with a scratch query if useful.

### Task D — Compare view and table

Follow Section 6. Keep the data, query, and environment constant. Record the build time and repeated-query time for both variants. Restore the original view configuration after collecting results.

**Evidence:** a completed comparison table with your actual observed timings, object type, and a short interpretation. If timings are too noisy, say so rather than inventing precision.

### Task E — Practice node selection

Run each selection command from Section 7.2. Before every command, write down the nodes you expect to be selected; afterward compare your prediction with dbt's selection output. Explain why `+fct_orders` includes parents and why `fct_orders+` includes children.

**Evidence:** selection notes for a single model, parent expansion, child expansion, tag selection, path selection, and an exclusion example.

### Task F — Lint and repair

1. Add `.sqlfluff` at the `jaffle_shop/` project root.
2. Run `uv run sqlfluff lint models/`.
3. Review every finding. Use `uv run sqlfluff fix models/` where appropriate; if your installed SQLFluff version supports/needs `--force` for unsafe fixes, apply it only after reviewing the proposed changes.
4. Re-run `uv run sqlfluff lint models/` and inspect the diff.
5. Manually verify that `ref()` calls, joins, output columns, and grain remain correct.

**Evidence:** final lint output and a brief note about at least one issue you corrected or why the initial files had no findings under your installed rule set.

### Troubleshooting guide

| Symptom | Likely cause | Investigation |
|---|---|---|
| `Could not find profile named ...` | Profile name mismatch or wrong `--profiles-dir` | Confirm `profile: jaffle_shop` matches the top-level profile key; run `dbt debug --profiles-dir .` |
| Adapter/profile error | Incompatible packages or malformed profile | Run `dbt --version`; inspect YAML indentation and installed adapter |
| `ref()` cannot resolve a node | Typo, missing model/seed file, or parse failure | Check the filename/resource name and run `dbt parse` |
| Relation/table not found | Seeds were not loaded, wrong target/schema, or upstream build missing | Run `dbt seed`; inspect target and generated relation names |
| Duplicate rows in `fct_orders` | Join multiplied the order grain | Aggregate payments to order grain before joining |
| Unexpected schema name | Default/custom schema generation or target schema differs from expectation | Inspect target config and `generate_schema_name`; do not hard-code a fix without checking environment isolation |
| SQLFluff cannot parse Jinja/dbt | Templater package missing or profile/project path wrong | Check `sqlfluff-templater-dbt`, `.sqlfluff`, and `profiles_dir` |
| `dbt show` option differs | Installed dbt version/adapter has different CLI support | Check `dbt show --help`; inspect the built relation with a compatible DuckDB client |
| Materialized view unsupported | Adapter or platform does not support that materialization/configuration | Verify adapter docs; use a supported materialization for the lab |
| `state:modified+` selects unexpectedly | Wrong/missing baseline manifest or state comparison | Verify `--state` points to the intended artifact and inspect selected nodes before execution |

### Completion criteria

- [ ] I can explain dbt's role in ELT and name what it does not do.
- [ ] I can distinguish project config, profile, target, schema, and alias.
- [ ] I can explain why every `ref()` is both relation resolution and a dependency declaration.
- [ ] I built staging models for orders, customers, and payments, plus `int_orders_payments`, `fct_orders`, and `dim_customers`.
- [ ] I can state the grain of every model and explain why payments are aggregated before joining to orders.
- [ ] I compared view and table behavior using measured results, without assuming the outcome.
- [ ] I can correctly predict parent/child node selection, tags, paths, exclusions, and the purpose of `state:modified+`.
- [ ] I understand the trade-offs among view, table, incremental, ephemeral, and materialized view.
- [ ] I ran SQLFluff, addressed its findings, and manually reviewed the resulting diff.
- [ ] I can explain when surrogate keys, conformed dimensions, Python models, and multi-project architecture are justified.

---

## 15. Review questions

Answer these without looking at the lesson, then check your reasoning.

1. Why does `ref('stg_orders')` do more than insert a table name into SQL?
2. What is the difference between `dbt compile`, `dbt run`, `dbt test`, and `dbt build`?
3. Why is a view often appropriate for staging but not automatically appropriate for every mart?
4. How can a join silently change the grain of `fct_orders`?
5. What can go wrong if every model is materialized as a table? What can go wrong if every model is a view?
6. Why is an incremental model not simply a faster table?
7. What is the difference between a schema and an alias?
8. Why must a custom `generate_schema_name` macro preserve development isolation?
9. What does `+fct_orders` select compared with `fct_orders+`?
10. Why does `state:modified+` require a saved state artifact?
11. When is a surrogate key useful, and why can including email be a poor key design?
12. Why might SQL be preferable to a Python model for joins and aggregations?
13. Why is `SELECT *` risky in a consumer-facing mart?
14. What does SQLFluff validate, and what kinds of correctness does it not validate?

## 16. Key takeaways

- dbt organizes, compiles, and executes warehouse transformations; it is not a general ingestion engine or scheduler.
- `ref()` connects relation resolution to the DAG, making builds and selections dependency-aware.
- Layers work when each model has one clear responsibility and a declared grain.
- Materialization is an engineering decision balancing build work, query work, storage, freshness, correctness, and adapter support.
- A table is not inherently better than a view; measure representative workloads.
- Incremental processing requires correctness and recovery design, not just a configuration flag.
- Schema generation and targets are part of environment safety. Validate physical relation names before deploying.
- Dimensional models depend on stable grain, well-defined keys, and conformed identity rules.
- SQLFluff can enforce style, but a clean lint report does not prove business correctness.
- Finish the analytics engineering loop: read, sketch the DAG, write, run, test, inspect, lint, and explain the model.

## Further reading

Prefer documentation matching the installed dbt Core and adapter versions:

- dbt documentation — <https://docs.getdbt.com/>
- dbt Core repository — <https://github.com/dbt-labs/dbt-core>
- dbt-duckdb adapter — <https://github.com/duckdb/dbt-duckdb>
- dbt-utils package — <https://github.com/dbt-labs/dbt-utils>
- SQLFluff documentation — <https://docs.sqlfluff.com/>

When documentation and an older tutorial disagree, verify the behavior against the installed version and adapter. In this lab, DuckDB is the local execution target; materialized-view support, Python model support, selection flags, and other adapter-specific capabilities must be verified rather than assumed.

**Verification boundary:** this lesson's examples and expected results are instructional specifications. They are not represented as having been executed against a live dbt/DuckDB installation. Before relying on them in a real environment, install compatible versions, run the lab commands, inspect compiled SQL and relations, and record the actual outputs. Static review cannot prove adapter execution, warehouse semantics, or measured performance.
