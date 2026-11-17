# Sources, Seeds, Snapshots, and Incremental Models in dbt

**Curriculum path:** `Stage 2C — Data Engineering_3/06-dbt-and-Analytics-Engineering/02-sources-seeds-snapshots-and-incremental-models.md`  
**Lab path:** `experiments/02_sources_incremental/`  
**Example domain:** Jaffle Shop-style customers and event/payment activity  
**Progression:** Beginner → Intermediate → Advanced

> **Roadmap alignment:** This lesson follows Topic 02 of `roadmap-dbt-and-Analytics-Engineering.md`: sources and freshness; seeds; snapshots; incremental models and strategies; late data, idempotency, snapshot pitfalls, large-table patterns, and when incremental dbt is the wrong tool. Later topics cover macros/packages, tests/contracts, governance, and deployment in greater depth.

## Learning outcomes

By completing this lesson and lab, you should be able to:

- Declare raw warehouse inputs with `sources.yml`, reference them with `source()`, and interpret freshness checks.
- Use seeds for small, version-controlled reference data and understand when not to use them.
- Explain how timestamp and check snapshots preserve SCD Type 2 history, including metadata and hard-delete behavior.
- Build an incremental model using `is_incremental()`, `{{ this }}`, a reliable watermark, a unique key, and deduplication.
- Compare append, merge, delete+insert, insert_overwrite, and microbatch while accounting for adapter support.
- Handle late-arriving records, retries, backfills, schema changes, and full refreshes safely.
- Design snapshots and incremental pipelines for reliability at scale, and recognize low-latency use cases that need a different architecture.

---

## 1. Sources: declare the raw-layer boundary

### 1.1 What is a dbt source?

A **source** declares a relation that already exists in the warehouse but is not built as a dbt model. Typical sources are raw tables loaded by ingestion tools, CDC pipelines, application exports, or platform jobs.

A source declaration gives dbt metadata about the upstream relation: its name, database/catalog, schema, description, columns, and optional freshness configuration. It also creates a documented lineage boundary between ingestion and transformation.

A source declaration does **not** load the data. Your ingestion process must create and populate the raw relation before dbt models can query it.

Use `source()` in model SQL rather than hard-coding the physical table name:

```sql
select
    event_id,
    customer_id,
    event_type,
    event_ts,
    loaded_at
from {{ source('app', 'events') }}
```

The two arguments identify the source name and table name declared in YAML. `source()` resolves the relation and records the dependency in dbt's graph, similarly to how `ref()` records model dependencies.

### 1.2 Example source YAML

Create `models/sources.yml`:

```yaml
version: 2

sources:
  - name: app
    description: "Raw application data populated by the ingestion pipeline."
    schema: raw
    tables:
      - name: events
        description: "Raw event records. One row per source event version."
        config:
          loaded_at_field: loaded_at
          freshness:
            warn_after:
              count: 12
              period: hour
            error_after:
              count: 24
              period: hour
        columns:
          - name: event_id
            description: "Stable identifier for the logical event."
          - name: customer_id
            description: "Customer associated with the event."
          - name: event_type
            description: "Business event category."
          - name: event_ts
            description: "Timestamp at which the event occurred."
          - name: loaded_at
            description: "Timestamp at which ingestion loaded this row."

      - name: customers
        description: "Current customer records from the application."
        columns:
          - name: customer_id
            description: "Stable customer identifier."
          - name: full_name
            description: "Customer's current display name."
          - name: email
            description: "Customer email address."
          - name: updated_at
            description: "Source-reported last update timestamp."
```

**Version compatibility:** Current dbt source configuration commonly nests `loaded_at_field` and `freshness` under the individual table's `config`, as shown for `events`. This is intentionally table-scoped: the `customers` table below does not have a `loaded_at` column and must not inherit this freshness policy. Older dbt Core versions and older project examples may use the legacy top-level form. Follow the syntax supported by your installed dbt version; do not mix both forms without checking the version's documentation. This example omits `database` so the adapter's default database/catalog resolution applies; specify it explicitly if your project requires a different one.

### 1.3 Why keep a raw-layer boundary?

A healthy raw boundary makes responsibilities clear:

- Ingestion owns extraction, loading, and source-level delivery guarantees.
- Raw relations preserve enough source information to investigate changes and replay data.
- dbt models normalize and transform those inputs.
- Source freshness provides a signal about data arrival, not proof that all records are correct or complete.

Do not put complex business joins in a source declaration. A source describes an existing relation; transformation logic belongs in models.

### 1.4 Source freshness

Freshness asks: **How old is the latest recorded load timestamp?** dbt compares the maximum `loaded_at_field` value with the current time and evaluates it against thresholds.

```bash
dbt source freshness
```

With the example thresholds:

- Age up to 12 hours: within the warning threshold.
- Older than 12 hours but not older than 24 hours: warning state.
- Older than 24 hours: error state.

The exact command exit status and how warnings/errors are surfaced depend on dbt version, invocation options, and orchestrator policy. Treat freshness results as operational signals and configure your job to fail or alert according to the required SLA.

Freshness is only meaningful if `loaded_at` is trustworthy. It should represent ingestion/arrival time, not an event's business timestamp. A source can have a recent load timestamp and still be missing an entire partition.

**Common failure modes**
- `loaded_at_field` is null or not timestamp-compatible.
- The field is event time rather than load time, making quiet periods look stale.
- The raw relation is empty, so no maximum timestamp can be calculated.
- The source uses a different timezone or future timestamps.
- Freshness is configured but the scheduled job never runs `dbt source freshness`.

Inspect `target/sources.json` (where emitted by the installed version) and terminal output, and check the actual maximum timestamp in the warehouse.

---

## 2. Seeds: small, version-controlled reference data

A **seed** is a CSV file stored in the dbt project and loaded into the warehouse by `dbt seed`. Seeds are useful for small, relatively static reference lists that benefit from code review: status mappings, country-code overrides, small classification tables, or controlled business mappings.

Example `seeds/event_type_mapping.csv`:

```csv
event_type,event_family,is_billable
page_view,engagement,false
signup,acquisition,false
purchase,commerce,true
refund,commerce,false
```

Load and inspect it:

```bash
dbt seed --select event_type_mapping
dbt show --select event_type_mapping
```

`dbt show` availability depends on dbt/adapter version; otherwise query the seeded relation directly.

Configure seed types if needed. For example, seed column types are adapter-specific and may be configured in `dbt_project.yml`:

```yaml
seeds:
  jaffle_shop:
    event_type_mapping:
      +column_types:
        event_type: varchar
        event_family: varchar
        is_billable: boolean
```

The type names must match the target adapter's SQL dialect. If the CSV has booleans or dates, inspect how the adapter parses them and set types explicitly where deterministic behavior matters.

**Use seeds when**
- The dataset is small enough to review in version control.
- Changes are infrequent and should go through a pull request.
- A CSV is an appropriate source of truth.

**Do not use seeds when**
- The file is large, frequently updated, or contains operational/transactional records.
- The CSV contains secrets, personal data, or credentials.
- A system of record or ingestion pipeline should own the data.
- Loading the file repeatedly would be a poor substitute for incremental ingestion.

A seed is not the same as an ingestion source. `source()` points to an externally managed relation; a seed is a project-managed CSV that dbt loads.

---

## 3. Snapshots: preserve changing records as SCD Type 2 history

### 3.1 Why snapshots exist

A source table often shows only the current customer state. If a customer's address changes from `10 River Road` to `22 Lake Street`, overwriting the old value loses the historical address unless the source itself retains versions.

A dbt **snapshot** compares the current source rows with previously recorded snapshot state and stores historical versions. This is a common way to implement **Slowly Changing Dimension Type 2 (SCD2)**.

A snapshot is not a complete CDC system. It only observes states when it runs. If a value changes twice between snapshot executions, the intermediate state may never be captured.

### 3.2 Snapshot metadata and validity intervals

dbt snapshot relations typically contain metadata such as:

- `dbt_valid_from`: when this version became valid in snapshot history.
- `dbt_valid_to`: when this version stopped being the current version; commonly `NULL` for the current row.
- `dbt_scd_id`: identifier for the snapshot version.
- `dbt_updated_at`: timestamp associated with the version according to the strategy.

Some older examples call the validity columns `valid_from` and `valid_to`; current dbt-generated metadata uses `dbt_valid_from` and `dbt_valid_to` by default. Verify naming and options in the installed version.

For a customer address change, the history may look like:

| customer_id | address | dbt_valid_from | dbt_valid_to |
|---|---|---|---|
| 42 | 10 River Road | 2026-01-01 | 2026-03-10 |
| 42 | 22 Lake Street | 2026-03-10 | `NULL` |

The validity timestamps reflect snapshot observation and configured update timestamps—not necessarily the exact real-world moment a change occurred.

### 3.3 Timestamp strategy

Use the timestamp strategy when the source has a trustworthy `updated_at` field that changes whenever any tracked attribute changes.

Create `snapshots/customers_timestamp_snapshot.sql`:

```sql
{% snapshot customers_timestamp_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

select
    customer_id,
    full_name,
    email,
    address,
    updated_at
from {{ source('app', 'customers') }}

{% endsnapshot %}
```

Behavior:
1. `unique_key` identifies the logical record across versions.
2. dbt compares the current row's `updated_at` with the prior snapshot state.
3. When the timestamp indicates a change, dbt expires the old version and inserts a new version.
4. When the timestamp does not change, dbt generally treats the record as unchanged—even if an attribute changed incorrectly without its timestamp updating.

Timestamp strategy is often simpler and more efficient than checking every tracked column, but it depends on source timestamp quality. It can miss changes if the source does not update `updated_at`, updates it non-deterministically, or has timestamp precision collisions.

### 3.4 Check strategy

Use the check strategy when there is no reliable update timestamp, or when you intentionally want dbt to compare selected columns.

Create `snapshots/customers_check_snapshot.sql`:

```sql
{% snapshot customers_check_snapshot %}

{{
    config(
        target_schema='snapshots_check',
        unique_key='customer_id',
        strategy='check',
        check_cols=['full_name', 'email', 'address']
    )
}}

select
    customer_id,
    full_name,
    email,
    address,
    updated_at
from {{ source('app', 'customers') }}

{% endsnapshot %}
```

Behavior:
- dbt compares the configured `check_cols` for each `unique_key`.
- A change to any checked column creates a new version.
- A change to an unlisted column does not by itself trigger a new version.

Prefer a list of meaningful columns over `check_cols: all` when practical; adding volatile or irrelevant fields can create unnecessary history churn. Check strategy may do more comparison work and still cannot capture a change that occurred and reverted between snapshot runs.

**Do not run two snapshot definitions into the same target relation.** The examples use different target schemas so they can be compared independently. On platforms where schema/database resolution differs, configure their destinations explicitly.

### 3.5 Hard deletes

A **hard delete** occurs when a source row disappears entirely. Snapshot behavior is version-dependent and configurable.

In dbt versions that support the `hard_deletes` option (introduced in newer dbt Core releases, including the 1.9-era behavior), the options may include:

- `ignore`: do not record a deletion event as a new historical version.
- `invalidate`: expire the current snapshot row when the source row is absent.
- `new_record`: record a deletion as a new snapshot version with deletion metadata.

Example on a compatible version:

```jinja
{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at',
        hard_deletes='new_record'
    )
}}
```

Do not assume `hard_deletes` is available on older versions or behaves identically across adapters. Older projects may use `invalidate_hard_deletes=true`, which is not interchangeable with every newer option. Check the installed dbt version and adapter documentation before relying on deletion history.

### 3.6 Snapshot design pitfalls

- **Unreliable `updated_at`:** timestamps that fail to change, move backward, or have coarse precision can hide changes.
- **Snapshot too infrequently:** intermediate states may be missed.
- **Snapshot of volatile derived data:** values that change due to nondeterministic logic or upstream recomputation can create meaningless history.
- **Duplicate `unique_key`:** the source must have one current row per key; duplicate keys can produce incorrect snapshot behavior.
- **Snapshot-of-snapshot:** snapshotting a relation that already contains historical versions often creates confusing or redundant history. Snapshot the authoritative current-state source unless there is a deliberate, documented reason not to.
- **Misinterpreting validity:** `dbt_valid_from` is not necessarily the source's event-effective timestamp. Use source-provided effective dates when the business requires true valid-time history.

### 3.7 Build a dimension from snapshot history

A downstream SCD2 dimension can select snapshot history and rename metadata into business-facing validity fields:

```sql
select
    customer_id,
    full_name,
    email,
    address,
    dbt_valid_from as valid_from,
    dbt_valid_to as valid_to,
    dbt_valid_to is null as is_current
from {{ ref('customers_timestamp_snapshot') }}
```

This is illustrative: a dbt snapshot is a snapshot resource, and the exact way downstream `ref()` resolves snapshot relations should be checked for the installed dbt version. In a project, place this model in the model path and ensure the snapshot resource is built before it. For event-time joins, decide whether a fact's timestamp should match `valid_from <= event_time < valid_to`, and handle the open-ended current interval. A production SCD2 dimension should also define its surrogate-key and unknown-member policies.

---

## 4. Incremental models: process only the necessary data

### 4.1 What makes a model incremental?

A table model usually rebuilds its full result. An **incremental model** builds a relation on its first run, then processes a subset of rows on later runs according to SQL filters and the configured adapter strategy.

Incremental processing can lower compute and build time for large datasets, but it adds statefulness: correctness depends on the watermark, unique key, deduplication, late-data policy, schema-change behavior, and recovery procedure.

### 4.2 `is_incremental()` and `{{ this }}`

- `is_incremental()` evaluates true when the model is configured as incremental, the target relation already exists, and the invocation is not doing a full refresh. The exact internal conditions depend on dbt version/adapter, but it is false on the first build and during a full-refresh build.
- `{{ this }}` resolves to the current model's target relation. In an incremental model, it lets SQL read previously materialized rows from the same model.

Example pattern:

```sql
{% if is_incremental() %}
where event_ts >= (
    select coalesce(max(event_ts), timestamp '1900-01-01')
    from {{ this }}
)
{% endif %}
```

On the first build, the filter is omitted and the query selects the initial dataset. On subsequent builds, it reads the existing target to determine a watermark. On `dbt run --full-refresh --select fct_events`, the incremental condition is disabled while dbt rebuilds the model according to full-refresh semantics.

A naive maximum timestamp filter can still miss late-arriving data, timestamp ties, updates to old records, or records whose event time is not monotonic. Use a lookback window and a reliable key when the business requires replay safety.

### 4.3 A robust `fct_events` incremental model

Assume the source relation has these columns:

- `event_id`: stable unique identifier for the logical event.
- `customer_id`, `event_type`, `event_ts`: business attributes.
- `source_updated_at`: timestamp that changes when the source corrects an event.
- `loaded_at`: when ingestion delivered the row.

The model uses `loaded_at` as an ingestion watermark to find new arrivals and a lookback window to replay recent ingestion time. It uses `event_id` as the merge key and ranks duplicate source versions deterministically before merge.

Create `models/marts/fct_events.sql`:

```sql
{{
    config(
        materialized='incremental',
        unique_key='event_id',
        incremental_strategy='merge',
        on_schema_change='append_new_columns'
    )
}}

with source_rows as (

    select
        cast(event_id as varchar) as event_id,
        cast(customer_id as integer) as customer_id,
        cast(event_type as varchar) as event_type,
        cast(event_ts as timestamp) as event_ts,
        cast(source_updated_at as timestamp) as source_updated_at,
        cast(loaded_at as timestamp) as loaded_at
    from {{ source('app', 'events') }}

    {% if is_incremental() %}
    where loaded_at >= (
        select coalesce(
            max(loaded_at) - interval '2 days',
            timestamp '1900-01-01'
        )
        from {{ this }}
    )
    {% endif %}

),

deduplicated as (

    select
        event_id,
        customer_id,
        event_type,
        event_ts,
        source_updated_at,
        loaded_at,
        row_number() over (
            partition by event_id
            order by source_updated_at desc, loaded_at desc
        ) as row_num
    from source_rows

)

select
    event_id,
    customer_id,
    event_type,
    event_ts,
    source_updated_at,
    loaded_at
from deduplicated
where row_num = 1
```

This SQL uses DuckDB-compatible interval syntax for the local lab. For other adapters, confirm timestamp casts and interval syntax; use adapter-appropriate SQL where necessary.

**Important correctness condition:** the ordering columns must break ties deterministically. If two versions share both `source_updated_at` and `loaded_at` but differ in payload, add a stable source sequence/version or ingestion record identifier. `row_number()` without a total ordering can select different winners across runs.

**Why use `loaded_at` for the extraction watermark?** It captures late-arriving events whose `event_ts` is old but which were just loaded. The lookback reprocesses recent ingestion timestamps in case of delayed batches or corrected source records. The unique key lets merge update existing event rows instead of appending duplicate keys.

The lookback cannot capture an arbitrarily late correction if its `loaded_at` is outside the lookback and the source fails to provide a reliable changed-record feed. For such cases, use a larger/reconfigurable lookback, source CDC/change tracking, periodic reconciliation, or a controlled backfill.

### 4.4 First build versus later builds

| Invocation | `is_incremental()` | Expected behavior |
|---|---:|---|
| First `dbt run --select fct_events` when target does not exist | False | Select all available source rows; create target |
| Subsequent incremental run | True | Apply watermark/lookback filter, deduplicate, and merge by `event_id` |
| `dbt run --full-refresh --select fct_events` | False | Recompute the complete model and replace/rebuild the target as supported by adapter |
| Target relation manually dropped | False | Behaves like an initial build |

A model can be configured incremental yet behave like a full build when the target does not exist. Do not interpret the config alone as proof that only new rows are read.

### 4.5 Choosing a watermark

A **watermark** defines how the model finds candidate rows to process.

| Candidate field | Strength | Risk |
|---|---|---|
| `event_ts` | Natural business-time ordering | Late-arriving events can have old event timestamps |
| `source_updated_at` | Can capture source corrections | Unreliable source clocks, unchanged timestamps, and precision collisions |
| `loaded_at` | Tracks ingestion arrival, including late business events | Corrections to old rows need a fresh load timestamp or CDC feed |
| Monotonic ingestion ID | Efficient boundary for append-only streams | Does not capture updates unless the feed emits new versions |

Use a field that reflects the change process you need to capture. For CDC, consider a source version, commit sequence, or ingestion offset rather than assuming an event timestamp is sufficient.

---

## 5. Incremental strategies and adapter differences

dbt exposes several incremental strategies, but not every adapter supports every strategy or option. Strategy names are not proof of identical SQL semantics across platforms.

| Strategy | Concept | Suitable use | Main risk / limitation |
|---|---|---|---|
| `append` | Insert selected rows without updating existing keys | Strictly append-only data with no replay duplicates | Reruns can create duplicates; updates to existing rows are not applied |
| `merge` | Match rows by `unique_key`; update matches and insert new keys | CDC/upsert-style event or entity tables | Requires adapter support and correct unique-key/dedup logic; duplicate source keys can cause failures or nondeterministic updates |
| `delete+insert` | Delete target rows matching keys/partitions, then insert candidate rows | Adapters/workloads where merge is unavailable or not preferred | Atomicity, affected scope, and SQL semantics vary; key/partition selection must be correct |
| `insert_overwrite` | Replace data in selected partitions/segments | Partitioned time-series or event facts | Requires platform-specific partition support and correct partition selection; can erase omitted rows in overwritten partitions |
| `microbatch` | Process time-based batches over an event-time column, often with lookback/retry controls | Very large time-series datasets where batch boundaries aid recovery | Newer/version- and adapter-dependent; event-time and batch configuration must match platform behavior |

Example configurations (verify support before use):

```sql
-- Append-only, only if the input cannot replay existing keys
{{ config(materialized='incremental', incremental_strategy='append') }}

-- Upsert-style model, if the adapter supports merge
{{ config(materialized='incremental', incremental_strategy='merge', unique_key='event_id') }}

-- Alternative strategy; adapter-specific support required
{{ config(materialized='incremental', incremental_strategy='delete+insert', unique_key='event_id') }}

-- Partition replacement; requires supported partition configuration
{{ config(materialized='incremental', incremental_strategy='insert_overwrite') }}

-- Microbatch; example only for a compatible adapter/version
{{ config(
    materialized='incremental',
    incremental_strategy='microbatch',
    event_time='event_ts',
    begin='2026-01-01',
    batch_size='day'
) }}
```

These are configuration fragments, not one combined runnable model. `insert_overwrite` commonly needs adapter-specific partition configuration. Microbatch requires event-time and batch configuration, and it is not automatically equivalent to key-based upsert: for example, `dbt-duckdb` documents that `unique_key` is ignored for microbatch. Check the installed adapter documentation for the actual supported strategy names, required fields, and limitations. Do not select a strategy solely because it appears in a generic dbt example.

**DuckDB adapter note:** the `dbt-duckdb` adapter documents support for `append`, `delete+insert`, `merge`, and `microbatch` on incremental table models. Its documented `merge` strategy requires DuckDB 1.4.0 or newer; its microbatch strategy requires dbt Core 1.9 or newer and does not perform `unique_key`-based upserts. Confirm the versions actually installed with `uv run dbt --version` and `uv run python -c "import duckdb; print(duckdb.__version__)"`, and recheck the adapter README before relying on these version-dependent details. See [dbt-duckdb incremental strategy documentation](https://github.com/duckdb/dbt-duckdb#incremental-strategy-configuration).

### 5.1 Unique keys and merge safety

A `unique_key` tells dbt how to match incoming rows to target rows for strategies that use keys. It does not automatically enforce uniqueness in every adapter, and it does not deduplicate the source query for you.

Before a merge:
1. Ensure the key is non-null and stable.
2. Deduplicate the candidate source rows by key.
3. Use a deterministic ordering to choose the winning version.
4. Understand whether the adapter's merge updates all columns or only configured columns.
5. Test reruns and correction scenarios.

A composite key can be appropriate when the logical record is identified by multiple fields, but do not create it with ambiguous raw concatenation. Use a safe deterministic encoding or a supported key-generation macro when available.

### 5.2 Full refresh

Use full refresh to rebuild an incremental model from the complete source query:

```bash
dbt run --full-refresh --select fct_events
```

Use this when changing model logic, repairing corrupted incremental state, validating a backfill, or responding to an incompatible historical transformation. It can be expensive on large datasets, so select only the necessary models and schedule it deliberately.

Full refresh recomputes from data currently available to the model. It cannot recover source history that ingestion has already discarded. Compare the refreshed result to the incremental result using row counts, key uniqueness, and aggregates—not row count alone.

---

## 6. Schema changes with `on_schema_change`

Incremental models have a physical target schema that may differ from the columns emitted by the current model SQL. `on_schema_change` controls how dbt reacts to detected top-level column changes. It does **not** backfill historical values for newly added columns.

| Setting | Typical behavior | Important caveat |
|---|---|---|
| `ignore` | Do not synchronize detected schema changes; adapter may continue with old target schema | New model columns may not be present in target; behavior/failure can vary by adapter |
| `append_new_columns` | Add newly introduced columns to the target | Existing historical rows get `NULL` for the new column unless separately backfilled |
| `sync_all_columns` | Synchronize additions and removals, and where supported data-type changes | Type changes may be expensive or unsupported; removed columns can break consumers |
| `fail` | Fail when a schema change is detected | Good for enforcing explicit schema review; exact detection depends on adapter |

Example:

```sql
{{
    config(
        materialized='incremental',
        unique_key='event_id',
        incremental_strategy='merge',
        on_schema_change='fail'
    )
}}
```

Choose `fail` when an unexpected schema change must be reviewed before deployment. Choose `append_new_columns` when additive evolution is acceptable and consumers can handle the new field. Do not assume `append_new_columns` fills historical values: run a backfill or full refresh if historical completeness is required.

Nested/struct column changes, type alterations, and relation replacement semantics differ by warehouse. Test each policy on a disposable target before using it in production.

---

## 7. Advanced reliability: late data, idempotency, and backfills

### 7.1 Late-arriving data and lookback windows

A late-arriving event is delivered after its business timestamp, sometimes after the incremental model has already advanced its watermark.

Suppose the target has processed ingestion timestamps through March 10. On March 12, ingestion delivers an event whose `event_ts` is March 7 but whose `loaded_at` is March 12. If the model filters on `event_ts > max(event_ts)`, it may never see the event. Filtering on ingestion time and replaying a lookback window is safer when ingestion time is reliable.

A lookback window is a deliberate trade-off:
- Longer lookback improves tolerance for late data and replayed corrections.
- Longer lookback scans more rows and increases compute.
- A finite lookback cannot guarantee capture of arbitrarily late data.
- Merge/upsert or deterministic deduplication is needed to make reprocessing safe.

For a 500-million-row events table, design the policy explicitly:
1. Choose a watermark that represents new/changed data.
2. Define a stable event key or composite key.
3. Deduplicate candidate versions deterministically.
4. Choose a lookback based on observed delivery lateness and SLA.
5. Record failure/retry behavior and how to replay a date range.
6. Periodically reconcile counts/keys or backfill beyond the normal lookback.

### 7.2 Idempotency

A pipeline is **idempotent** when rerunning the same logical input does not change the final result beyond the intended deterministic state.

For dbt incremental models, this generally requires:
- Stable keys.
- A deterministic winner when source records repeat.
- An appropriate upsert/replace strategy.
- A watermark/lookback that can safely replay data.
- No dependence on nondeterministic expressions as record identity.
- Controlled schema changes and recovery procedures.

`append` is not idempotent when a retry inserts the same event again unless upstream input is strictly deduplicated and the strategy/target enforces uniqueness. `merge` is often a better fit for replayable CDC or event corrections, but only if the unique key and source deduplication are correct.

### 7.3 Safe backfills

For a backfill:
1. Identify the date/key range and the intended source-of-truth records.
2. Confirm the model can reprocess that range without duplicates.
3. Prefer a targeted strategy or a separate backfill target where supported.
4. Run on a non-production target first.
5. Compare key uniqueness, row counts, and business aggregates.
6. Promote the corrected output using a reviewed, recoverable procedure.

Do not casually change a global watermark to an old date and run against production. Depending on the strategy, that can duplicate rows, overwrite too much data, or consume substantial compute.

### 7.4 Deletes and updates in incremental facts

A merge handles incoming matched keys only if the source query emits those keys. If a source row disappears and the incremental query no longer includes it, the target row usually remains unless the model explicitly processes delete events or uses a strategy that replaces the affected partition/scope.

For CDC sources, model delete indicators or tombstones intentionally. Do not assume `merge` automatically deletes target records absent from the source query.

---

## 8. Large-table patterns: partitioning, clustering, and `incremental_predicates`

For large tables, incremental strategy alone may not be enough. Platform-specific partitioning and clustering can reduce the amount of data scanned or rewritten.

Illustrative BigQuery-style configuration:

```sql
{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key='event_id',
        partition_by={
            "field": "event_date",
            "data_type": "date",
            "granularity": "day"
        },
        cluster_by=['customer_id', 'event_type']
    )
}}
```

This configuration is **warehouse-specific**, not portable DuckDB SQL. Check the adapter's current documentation for exact property names and supported data types.

`incremental_predicates` can add conditions to the incremental strategy's target-side matching/query behavior on supported adapters. It is often used to limit the target scan during a merge, for example to recent partitions. However, restricting the target to recent rows can cause an old event key to fail to match its existing row and be inserted again. The predicate must be consistent with the maximum age of updates/late arrivals and the unique-key semantics.

Illustrative Snowflake-style expression only; exact SQL syntax, aliases, and support are adapter-specific:

```sql
{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key='event_id',
        incremental_predicates=[
            "DBT_INTERNAL_DEST.event_date >= dateadd(day, -7, current_date)"
        ]
    )
}}
```

This expression is not DuckDB-portable. It illustrates the concept: constrain target-side scanning to a recent window. Verify generated SQL and ensure old-key corrections are either included by the predicate or handled by a separate backfill/reconciliation path.

---

## 9. When not to use dbt incremental

dbt incremental models are typically run in scheduled/batch transformations. They are not a general replacement for stream processors or sub-second serving systems.

Consider streaming engines, CDC consumers, or warehouse-native dynamic tables when requirements demand:
- Very low latency or continuous processing.
- Event-time windows and watermarks managed continuously.
- Stateful stream joins or complex event-time semantics.
- Continuous change propagation with operational guarantees beyond a scheduled dbt job.

Some warehouses provide dynamic tables or similar managed refresh features; availability and behavior are platform-specific. The architectural choice depends on latency, throughput, replay semantics, cost, and operational expertise—not on whether SQL can express the transformation.

---

## 10. Hands-on lab: `experiments/02_sources_incremental/`

This lab uses DuckDB for local repeatability and keeps the example consistent: raw `app.events`, raw `app.customers`, seed `event_type_mapping`, incremental `fct_events`, and a customer snapshot. The lab demonstrates the concepts locally; production adapter behavior must be verified separately.

### 10.1 Lab structure

```text
experiments/02_sources_incremental/
├── pyproject.toml
├── uv.lock
└── jaffle_shop/
    ├── dbt_project.yml
    ├── models/
    │   ├── sources.yml
    │   └── marts/
    │       └── fct_events.sql
    ├── snapshots/
    │   └── customers_check_snapshot.sql
    ├── seeds/
    │   └── event_type_mapping.csv
    └── load_lab_data.py
```

Create a project and install dependencies from this directory:

```bash
uv init --python 3.12
uv add dbt-core dbt-duckdb duckdb
uv run dbt init jaffle_shop
```

After initialization, enter the generated project directory and create the files shown in the tree:

```bash
cd jaffle_shop
```

Run all subsequent `dbt` and `load_lab_data.py` commands from this directory. Use the profile generated by your installed `dbt-duckdb` version as the authoritative profile template. Configure it to use the same DuckDB file that `load_lab_data.py` writes to.

### 10.2 Raw input data and loader

Create `load_lab_data.py`:

```python
import argparse
from pathlib import Path

import duckdb

ROOT = Path(__file__).parent
DB_PATH = ROOT / "jaffle_shop.duckdb"


def initialize(con):
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute("""
        CREATE OR REPLACE TABLE raw.events (
            event_id VARCHAR,
            customer_id INTEGER,
            event_type VARCHAR,
            event_ts TIMESTAMP,
            source_updated_at TIMESTAMP,
            loaded_at TIMESTAMP
        )
    """)
    con.execute("""
        INSERT INTO raw.events VALUES
        ('e1', 1, 'signup',   '2026-10-01 09:00:00', '2026-10-01 09:01:00', '2026-10-01 10:00:00'),
        ('e2', 1, 'purchase', '2026-10-01 11:00:00', '2026-10-01 11:02:00', '2026-10-01 12:00:00')
    """)
    con.execute("""
        CREATE OR REPLACE TABLE raw.customers (
            customer_id INTEGER,
            full_name VARCHAR,
            email VARCHAR,
            address VARCHAR,
            updated_at TIMESTAMP
        )
    """)
    con.execute("""
        INSERT INTO raw.customers VALUES
        (1, 'Ada Lovelace', 'ada@example.test', '10 River Road', '2026-10-01 08:00:00'),
        (2, 'Grace Hopper', 'grace@example.test', '5 Harbour Way', '2026-10-01 08:00:00')
    """)


def append_day_two(con):
    con.execute("""
        INSERT INTO raw.events VALUES
        ('e3', 2, 'page_view', '2026-10-02 10:00:00', '2026-10-02 10:01:00', '2026-10-02 10:05:00')
    """)


def append_late_event(con):
    con.execute("""
        INSERT INTO raw.events VALUES
        ('e4', 2, 'purchase', '2026-09-28 14:00:00', '2026-10-03 09:00:00', '2026-10-03 09:05:00')
    """)


def update_customer(con):
    con.execute("""
        UPDATE raw.customers
        SET address = '22 Lake Street',
            updated_at = TIMESTAMP '2026-10-03 10:00:00'
        WHERE customer_id = 1
    """)


def make_source_stale(con):
    con.execute("""
        UPDATE raw.events
        SET loaded_at = TIMESTAMP '2026-10-01 10:00:00'
    """)


ACTIONS = {
    "init": initialize,
    "day2": append_day_two,
    "late": append_late_event,
    "update-customer": update_customer,
    "stale": make_source_stale,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=ACTIONS)
    args = parser.parse_args()

    with duckdb.connect(str(DB_PATH)) as connection:
        ACTIONS[args.action](connection)

    print(f"Applied action {args.action!r} to {DB_PATH}")
```

The `init` action resets the lab's raw tables to day-one state. Other actions mutate the existing database without resetting it. Use `init` only when deliberately restarting the exercise; when restarting after `fct_events` already exists, also run a controlled `--full-refresh` (or remove the disposable lab target relation) so rows from a previous run do not remain in the target.

### 10.3 Project configuration

A minimal `dbt_project.yml`:

```yaml
name: jaffle_shop
version: "1.0.0"
config-version: 2
profile: jaffle_shop

model-paths: ["models"]
seed-paths: ["seeds"]
snapshot-paths: ["snapshots"]
test-paths: ["tests"]
analysis-paths: ["analyses"]
macro-paths: ["macros"]

clean-targets:
  - target
  - dbt_packages
```

Use the matching profile generated by `dbt init`. Example only; confirm profile field names with the installed adapter:

```yaml
jaffle_shop:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "/absolute/path/to/experiments/02_sources_incremental/jaffle_shop/jaffle_shop.duckdb"
      schema: analytics
      threads: 4
```

### 10.4 Source declarations and freshness

Create `models/sources.yml`:

```yaml
version: 2

sources:
  - name: app
    description: "Raw application data loaded by the lab loader."
    schema: raw
    tables:
      - name: events
        description: "Raw application events."
        config:
          loaded_at_field: loaded_at
          freshness:
            warn_after: {count: 12, period: hour}
            error_after: {count: 24, period: hour}
      - name: customers
        description: "Current customer state."
```

Freshness is configured only on `events`. The `customers` fixture has no ingestion `loaded_at` field, so it must not inherit this policy or use its business `updated_at` as an ingestion-freshness signal. If the installed dbt version expects the older top-level freshness syntax, use that version's documented equivalent; do not paste both alternatives into the same YAML file.

Run:

```bash
uv run python load_lab_data.py init
uv run dbt debug --target dev
uv run dbt source freshness
```

The day-one fixture timestamps are deliberately old relative to the current date, so the source should be stale under the 12-hour/24-hour thresholds. A stale result is expected, not a dbt SQL failure. To observe a fresh state, update `loaded_at` to a recent timestamp in the raw table, rerun freshness, and then restore old timestamps with `uv run python load_lab_data.py stale`. Freshness measures the newest load timestamp, not event time.

### 10.5 Seed the reference mapping

Create `seeds/event_type_mapping.csv`:

```csv
event_type,event_family,is_billable
page_view,engagement,false
signup,acquisition,false
purchase,commerce,true
```

Run:

```bash
uv run dbt seed --select event_type_mapping
```

Expected: dbt creates a relation for the mapping. Query it to verify the three rows. The seed is a small reference list, not the raw events feed.

### 10.6 Build `fct_events`

Create `models/marts/fct_events.sql` using the incremental model in Section 4.3. Current `dbt-duckdb` documentation lists `merge` support for incremental table models when DuckDB is version 1.4.0 or newer. Verify the actual DuckDB and adapter versions in your environment before running the lab. If your installed versions do not support `merge`, use a strategy documented for those exact versions and record the change; do not silently assume compatibility.

Run the first build:

```bash
uv run dbt run --select fct_events
```

Expected initial rows: `e1` and `e2` (2 events).

Append day two and run again. Append day two without resetting the database:

```bash
uv run python load_lab_data.py day2
```

Then:

```bash
uv run dbt run --select fct_events
```

Expected: `e3` is added; total 3 distinct event IDs.

Append the late event without resetting the database:

```bash
uv run python load_lab_data.py late
uv run dbt run --select fct_events
```

Expected: `e4` appears despite its older `event_ts`, because its `loaded_at` is new. Total 4 distinct event IDs.

Verify:

```sql
select count(*) as rows, count(distinct event_id) as distinct_event_ids
from analytics.fct_events;
```

Expected: `rows = 4`, `distinct_event_ids = 4`. Adjust the schema/relation name to match the profile and adapter naming behavior.

Run the model a second time without changing raw data. The row count and distinct-key count should remain 4. If duplicates appear, inspect the configured strategy, generated SQL, source deduplication, and unique key.

### 10.7 Customer snapshot with check strategy

Create `snapshots/customers_check_snapshot.sql`:

```sql
{% snapshot customers_check_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='check',
        check_cols=['full_name', 'email', 'address']
    )
}}

select
    customer_id,
    full_name,
    email,
    address,
    updated_at
from {{ source('app', 'customers') }}

{% endsnapshot %}
```

Run:

```bash
uv run dbt snapshot
```

Expected first run: one snapshot version for each of the two customers.

Now update customer 1 and run the snapshot again:

```bash
uv run python load_lab_data.py update-customer
uv run dbt snapshot
```

Inspect the snapshot relation using the warehouse SQL client. Expected for customer 1: two versions, the old address with a non-null `dbt_valid_to`, and the new address with `dbt_valid_to is null`. Customer 2 should still have one current version.

Snapshots only record states observed at snapshot execution time. If the source changes twice between runs, an intermediate version can be missed.

### 10.8 Schema-change exercise

After the first incremental build, add a column to the raw events table and include it in the model SQL, for example. This is a one-time mutation; do not rerun `init` afterward because it resets the table:

```sql
alter table raw.events add column device_type varchar;
update raw.events set device_type = 'web' where event_id in ('e1', 'e2', 'e3', 'e4');
```

Then add `device_type` to the model's `source_rows` CTE and final projection. Each policy must be tested against a target relation that still has the **pre-change schema**; otherwise a prior `append_new_columns` or `sync_all_columns` run can make the next test appear to pass without exercising the change. The most reproducible approach is to define separate dbt profile outputs pointing to the same DuckDB file but different target schemas, then build the baseline model into each target before changing the source/model. Add outputs like these under the existing `jaffle_shop.outputs` profile (keep the same DuckDB `path` as `dev`):

```yaml
dev_ignore:
  type: duckdb
  path: "/absolute/path/to/jaffle_shop.duckdb"
  schema: analytics_ignore
  threads: 4
dev_append:
  type: duckdb
  path: "/absolute/path/to/jaffle_shop.duckdb"
  schema: analytics_append
  threads: 4
dev_sync:
  type: duckdb
  path: "/absolute/path/to/jaffle_shop.duckdb"
  schema: analytics_sync
  threads: 4
dev_fail:
  type: duckdb
  path: "/absolute/path/to/jaffle_shop.duckdb"
  schema: analytics_fail
  threads: 4
```

Before adding `device_type` to the raw table/model, run the baseline model once with each target (for example, `uv run dbt run --target dev_ignore --select fct_events`). Then add the source column and model projection. Use one policy per test run; configure it in the model's `config()` block, not as a standalone SQL statement:

```sql
{{ config(on_schema_change='ignore') }}
```

Repeat the experiment with `append_new_columns`, `sync_all_columns`, and `fail`, restoring a clean pre-change target for each policy. Verify actual target columns and build outcomes for the installed adapter. Typical expectations: `ignore` does not synchronize the target schema and may fail when the model references a new output column; `append_new_columns` adds the column but does not backfill old rows; `sync_all_columns` synchronizes detected additions/removals and supported type changes; `fail` stops the build when a change is detected. Restore the intended production configuration after the experiment.

### 10.9 Controlled full refresh

First capture the incremental result's row count, distinct key count, and aggregates. Then run:

```bash
uv run dbt run --full-refresh --select fct_events
```

Re-run the same validation query. Compare:
- Total rows.
- Distinct event keys.
- Min/max event timestamps.
- Counts by event type.
- Any business aggregate relevant to the model.

The full-refresh result should match the intended complete source result. For the four fixture events, the expected row count is 4. If a column was added after earlier incremental builds, full refresh may also populate historical values for that column because all source rows are reprocessed. It cannot recover data absent from the raw source.

### 10.10 Failure diagnosis

| Symptom | Likely cause | What to check |
|---|---|---|
| `source()` relation not found | Wrong source name/table, wrong database file, or raw table not loaded | `models/sources.yml`, profile path, and raw schema |
| Freshness fails unexpectedly | Stale/null/wrong load timestamp or incorrect source config nesting | Query `max(loaded_at)`, inspect freshness output, confirm version syntax |
| Seed type is wrong | CSV inference or adapter-specific type behavior | Configure seed column types and inspect the loaded relation |
| Snapshot does not create a new version | `updated_at` did not change, check columns exclude the change, or snapshot was not rerun | Inspect source row and snapshot strategy |
| Duplicate events after rerun | Append strategy, incorrect key, duplicate source versions, or nondeterministic deduplication | Inspect compiled SQL and count duplicate `event_id` values |
| Late event is missing | Filter uses business event time, `loaded_at` was not updated, or lookback is too short | Inspect source timestamps and compiled watermark predicate |
| Merge fails | Adapter lacks merge support or source contains duplicate keys | Verify adapter docs and deduplicate input before merge |
| New column is absent | `on_schema_change` policy or adapter behavior | Inspect target schema; run controlled full refresh if historical backfill is required |
| Full refresh differs from incremental result | Incremental filter, key, dedup, deletion, or schema logic is wrong | Compare key sets and per-key values, not only row counts |

---

## 11. Common mistakes and production rules

1. **Incremental model without a unique key:** choose a stable logical key and validate it.
2. **Watermark on a non-monotonic field:** use ingestion/change timestamps or a CDC sequence when business event time can arrive out of order.
3. **Trusting `updated_at` blindly:** verify how and when it is updated, its precision, timezone, and null behavior.
4. **No deduplication before merge:** multiple candidate rows for one key can cause errors or unstable results.
5. **Assuming merge deletes missing rows:** deletions need explicit handling.
6. **Treating `on_schema_change` as a backfill:** it synchronizes schema, not historical values.
7. **Snapshotting volatile derived data:** snapshot authoritative, stable source state.
8. **Snapshotting too infrequently:** intermediate changes can be lost.
9. **Using seeds as an ingestion mechanism:** seeds are for small, reviewed reference data.
10. **Using incremental dbt for sub-second freshness:** choose a streaming/CDC architecture when latency requirements demand it.

---

## 12. Knowledge checkpoint and completion criteria

Answer these without looking at the lesson:

1. What does a source declaration do, and what does it not do?
2. Why should freshness use ingestion time rather than event time?
3. When is a seed appropriate, and when should data come from ingestion instead?
4. How do timestamp and check snapshots differ?
5. What do `dbt_valid_from` and `dbt_valid_to` represent?
6. Why can a timestamp snapshot miss a change?
7. What does `is_incremental()` return on first build, later builds, and full refresh?
8. Why is `{{ this }}` useful in an incremental model?
9. Why is a stable `unique_key` insufficient without source deduplication?
10. How does a lookback window help late data, and what can it still miss?
11. What is the difference between `append`, `merge`, `delete+insert`, `insert_overwrite`, and `microbatch`?
12. Why does `on_schema_change='append_new_columns'` not backfill historical values?
13. How would you prove that incremental output matches a full refresh?
14. Why can snapshotting a snapshot be problematic?
15. For a 500-million-row events table, specify the watermark, key, dedup rule, lookback, recovery plan, and reconciliation check.

### Ready-to-move-on checklist

- [ ] Declare sources and run freshness checks.
- [ ] Load and query a small seed.
- [ ] Explain the raw-layer boundary.
- [ ] Create a snapshot and inspect SCD2 history.
- [ ] Build an incremental `fct_events` with a stable key and watermark.
- [ ] Load day one, day two, and a late-arriving row without duplicates.
- [ ] Compare schema-change policies on a disposable target.
- [ ] Run a full refresh and prove result equivalence using key and aggregate checks.
- [ ] Explain why the selected strategy is supported by the actual adapter/version.

---

## 13. Version and execution verification notes

- dbt Core and adapters evolve separately. Record `dbt --version` and consult the documentation for the installed adapter before relying on merge, delete+insert, insert_overwrite, microbatch, hard-delete options, or schema synchronization.
- Source freshness YAML syntax has evolved; current examples commonly use source-level `config`, while older releases may expect legacy fields. Use the syntax supported by your version.
- `microbatch` is a newer, adapter-dependent capability and requires more than setting a strategy string. Configure event time, batch behavior, and lookback according to the installed adapter.
- DuckDB is the local learning environment, but not every production warehouse feature is emulated identically by `dbt-duckdb`. Treat warehouse-specific partitioning, clustering, `incremental_predicates`, and deletion semantics as adapter-specific.
- The snippets are statically reviewed learning examples. Unless you execute the commands in your environment, do not interpret them as runtime-tested. Record actual outcomes and any adapter-specific changes in your lab notes.
- Official references for version-sensitive behavior: [dbt incremental models](https://docs.getdbt.com/docs/build/incremental-models), [dbt snapshots](https://docs.getdbt.com/docs/build/snapshots), [dbt source freshness](https://docs.getdbt.com/docs/deploy/source-freshness), and [dbt-duckdb incremental strategies](https://github.com/duckdb/dbt-duckdb#incremental-strategy-configuration).
