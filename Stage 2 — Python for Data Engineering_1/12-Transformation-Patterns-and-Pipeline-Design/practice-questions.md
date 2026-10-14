# Module 2.12 — Transformation Patterns and Pipeline Design
# Practice Questions and Solutions

## How to Use This Practice Set

This practice set contains exactly 40 production-oriented questions across the nine topics of Module 2.12.

Use the learning loop:

```text
Read
→ Define the run contract
→ Build
→ Run twice
→ Run for the past
→ Break
→ Verify invariants
→ Change logic and rebuild
→ Write it down
→ Explain aloud
```

Before reading each solution:

- write your assumptions;
- identify the data grain;
- define the run interval;
- identify invariants;
- consider duplicate input;
- consider retries and partial failure;
- consider late data;
- consider how you would prove correctness.

The questions intentionally progress from foundational implementation to senior production architecture. The solution follows each problem immediately so the file can also serve as a guided learning chapter.

# Part I — Basic


# Part II — Moderate


# Part III — Hard


# Part IV — Advanced


## Question 1 — Separate a badly structured orders pipeline

### Problem

A single Python script reads CSV files, applies business logic, writes database tables, and reads environment variables from inside transformation functions. The same script is difficult to test and rerun safely.

### Your Task

Refactor the design into extract, transform, and load boundaries. Identify what belongs at the edges and what should remain a pure transformation.

### Expected Thinking

Think about deterministic inputs, explicit dependencies, a RunContext, thin CLI behavior, and readers/writers at the edges. A transformation should not need to know how files are opened or where outputs are written.

### Solution

1. Make extraction produce an explicit dataset and metadata such as logical date and source partition.
2. Pass a `RunContext` containing `run_id`, logical date/data interval, environment, and configuration.
3. Keep business transformation functions pure: input rows plus explicit configuration produce output rows.
4. Make validation a step contract around the transformation.
5. Keep loading in a separate writer that owns database/object-store behavior.
6. Let the CLI assemble the context and invoke the pipeline rather than embedding business logic.

A conceptual structure is:

```text
CLI
 ↓
RunContext
 ↓
reader → transform → validation → writer
             ↓
       deterministic output
```

### Why This Solution Works

The design isolates side effects at the boundaries. The transformation can be tested with small in-memory data and produces the same result for the same input/context. A failed write can be retried without rerunning unrelated business logic.

### Production Considerations

In production, persist run metadata, use explicit configuration, validate schemas with the module's Pandera patterns, make partition outputs immutable where appropriate, and add observability around each step.

### Common Mistakes

Common mistakes: creating one replacement 'god function'; reading environment variables inside transformation code; calling `now()` during transformation; relying on hidden global state; and mixing database writes into pure business logic.

### Key Takeaway

Separate side effects from deterministic transformation logic so each step has a clear contract and can be independently tested and retried.

## Question 2 — Identify deterministic and non-deterministic transformations

### Problem

An orders transformation adds `processed_at = now()`, randomly samples five rows for debugging, and selects whichever record currently appears as the 'latest' customer row without an explicit ordering rule.

### Your Task

Identify which behaviors are non-deterministic and redesign the transformation so the same partition and run contract produce the same result.

### Expected Thinking

Look for hidden time, randomness, and unspecified ordering. Determinism requires every value affecting the result to come from explicit inputs or stable rules.

### Solution

`now()` is non-deterministic because two executions produce different timestamps. Replace it with an explicit run timestamp in `RunContext` if the timestamp is part of the output contract.

Random sampling is non-deterministic. For deterministic diagnostics, use a stable hash-based sample or an explicitly seeded deterministic method.

'Latest' without a deterministic ordering is also unsafe. Use a defined ordering such as:

```sql
row_number() over (
    partition by customer_id
    order by updated_at desc, sequence_number desc, record_id desc
)
```

The final tie-breaker makes equal timestamps deterministic.

### Why This Solution Works

Deterministic behavior allows retries, reconciliation, backfills, and tests to compare results reliably. Hidden time/randomness can cause two executions over identical inputs to disagree.

### Production Considerations

Record the run timestamp in the run contract, document timezone semantics, and use deterministic sampling when reproducible diagnostics are required.

### Common Mistakes

A common mistake is assuming `updated_at DESC` is sufficient when multiple records share the same timestamp. Another is replacing `now()` with another implicit system clock.

### Key Takeaway

A production transformation should make every result-affecting choice explicit and reproducible.

## Question 3 — Choose a basic load strategy

### Problem

Three datasets arrive daily: an immutable daily event partition, a mutable customer table keyed by `customer_id`, and a small corrected daily aggregate that must completely replace its affected partition.

### Your Task

Choose a load strategy for each dataset and justify the choice.

### Expected Thinking

Match the write pattern to the data shape rather than choosing one strategy globally.

### Solution

Use:

1. Immutable event partition → **append**, provided the source is truly immutable and duplicates are impossible or separately controlled.
2. Mutable customer table → **merge/upsert**, because existing logical records can change.
3. Corrected daily aggregate → **partition overwrite**, because the affected partition is the replacement unit.

The choices are driven by identity and mutation semantics, not by preference.

### Why This Solution Works

Each strategy minimizes unnecessary work while preserving the intended target state. Append fits immutable additions; merge handles mutable identity; partition overwrite replaces a known complete scope.

### Production Considerations

In production, verify source guarantees, define duplicate handling, measure partition sizes, and use partition predicates or clustering to control merge/overwrite cost.

### Common Mistakes

Choosing append for mutable data; using merge without a reliable key; or overwriting a partition that is not actually complete are common failures.

### Key Takeaway

Load strategy follows data shape: immutable additions, mutable identities, and replaceable partitions need different write semantics.

## Question 4 — Deduplicate a small CDC batch

### Problem

A batch contains these records:

```text
customer_id | status | updated_at           | sequence_number
101         | gold   | 2026-09-01 10:00:00  | 7
101         | gold   | 2026-09-01 10:00:00  | 7
101         | silver | 2026-09-01 09:00:00 | 6
102         | gold   | 2026-09-01 11:00:00  | 2
```

### Your Task

Return one winning version per `customer_id`.

### Expected Thinking

First remove exact duplicates, then define a deterministic winner for business-key duplicates. Use the strongest available version/order columns.

### Solution

Use `customer_id` as the business key and rank by `updated_at DESC, sequence_number DESC`.

Conceptually:

```sql
with ranked as (
    select *,
           row_number() over (
               partition by customer_id
               order by updated_at desc,
                        sequence_number desc
           ) as rn
    from changes
)
select customer_id, status, updated_at, sequence_number
from ranked
where rn = 1;
```

The winners are customer 101 = `gold` sequence 7 and customer 102 = `gold` sequence 2.

### Why This Solution Works

The ranking makes the winner explicit and deterministic. Exact duplicates receive the same rank ordering, and the strongest version wins.

### Production Considerations

In production, add a deterministic final tie-breaker if timestamps and sequence numbers can still tie. Validate key uniqueness after deduplication and define delete/tombstone behavior.

### Common Mistakes

Using `max(updated_at)` independently for each column; sorting without a deterministic tie-breaker; or assuming exact duplicate removal solves multiple versions.

### Key Takeaway

Deduplication must define logical identity and a deterministic winning-version rule.

## Question 5 — Choose partition-based incremental processing

### Problem

A daily orders fact table is partitioned by `order_date`. Only yesterday's source partition changes during normal operation, while rare historical corrections are handled separately.

### Your Task

Design the normal incremental run and explain when a full rebuild is unnecessary.

### Expected Thinking

Use the partition as the natural unit of work. Separate normal incremental processing from deliberate historical backfills.

### Solution

For the normal run, identify the target date from the run contract and rebuild only that partition:

```text
run date = 2026-09-30
        ↓
process source order_date = 2026-09-30
        ↓
replace target partition 2026-09-30
```

If a historical correction affects 2026-09-20, run a targeted backfill for that partition rather than rebuilding the entire table.

### Why This Solution Works

Partition-scoped processing bounds work and makes recovery easier. It also makes correctness easier to reason about because each execution has an explicit interval.

### Production Considerations

In production, record partition status, row counts, logic version, and timestamps. Use atomic replacement where supported and prevent normal runs from being starved by large backfills.

### Common Mistakes

Using the current wall-clock time as the partition; rebuilding all history for every correction; or allowing a backfill to overwrite an unrelated partition.

### Key Takeaway

A partition is a useful incremental unit when the data model and business correction boundaries align with it.

## Question 6 — Distinguish event time and load time

### Problem

An order event occurred at 09:00 but was loaded at 12:00. Another event occurred at 10:00 but was loaded at 11:00.

### Your Task

Explain which timestamp should determine business-day attribution and which should determine ingestion monitoring.

### Expected Thinking

Separate when the business event happened from when the platform received it. They answer different questions.

### Solution

Use `event_time` for business-time attribution such as daily revenue and `loaded_at` for ingestion monitoring/incremental arrival logic.

```text
event_time → "When did the order happen?"
loaded_at  → "When did the platform receive it?"
```

The first event belongs to the 09:00 business interval even though it arrived at 12:00.

### Why This Solution Works

Conflating the timestamps can move late events into the wrong business partition or make freshness and lateness measurements impossible.

### Production Considerations

Also track processing time where relevant. Define timezone semantics explicitly and retain both event and ingestion timestamps for auditability.

### Common Mistakes

Using `loaded_at` as business time; assuming arrival order equals event order; or dropping one timestamp because they appear redundant.

### Key Takeaway

Event time describes business reality; load time describes ingestion reality.

## Question 7 — Construct a deterministic hash key

### Problem

A customer record has `customer_id = " C-1001 "` and must produce a stable surrogate key across Python and SQL systems.

### Your Task

Design the canonicalization steps before hashing.

### Expected Thinking

Hashing is only cross-system deterministic if both systems serialize exactly the same canonical value.

### Solution

Canonicalize first:

```text
trim whitespace
→ normalize case if contract requires it
→ encode UTF-8
→ hash with SHA-256
```

For example, conceptually:

```python
canonical = customer_id.strip().upper()
key = sha256(canonical.encode("utf-8")).hexdigest()
```

The SQL implementation must apply exactly the same normalization and encoding rules.

### Why This Solution Works

The hash function is deterministic, but it cannot compensate for different input bytes. Canonical serialization is therefore part of the key contract.

### Production Considerations

Document null tokens, case rules, Unicode normalization if required, numeric/timestamp formatting, and hex/binary storage representation.

### Common Mistakes

Hashing the raw string in one system and a trimmed/uppercased string in another; using locale-dependent formatting; or assuming plain hashing anonymizes an identifier.

### Key Takeaway

Cross-system hash parity is primarily a serialization-contract problem.

## Question 8 — Diagnose lookup fan-out

### Problem

An order has one product ID. The product lookup unexpectedly contains two active rows for that product ID, and the order revenue total doubles after the join.

### Your Task

Identify the cause and redesign the lookup validation.

### Expected Thinking

A one-to-many lookup where a many-to-one relationship was expected causes fan-out. Validate the lookup key before joining.

### Solution

Check lookup-key uniqueness:

```sql
select product_id, count(*) as n
from product_lookup
group by product_id
having count(*) > 1;
```

If `product_id` should identify exactly one active row, the query must return zero rows. Fix or quarantine the invalid reference data before enrichment.

### Why This Solution Works

The revenue did not change because of arithmetic; it changed because one fact row became multiple rows during the join.

### Production Considerations

Add uniqueness checks, coverage metrics, explicit missing-match policy, and point-in-time logic when the lookup is time-varying.

### Common Mistakes

Using `distinct` after the join to hide fan-out; accepting duplicate lookup keys; or assuming every join is many-to-one.

### Key Takeaway

Validate lookup cardinality before trusting enriched measures.

## Question 9 — Design a DatasetConfig

### Problem

An organization processes many similarly shaped datasets. Each dataset needs a source, target, key columns, partition column, load strategy, owner, and quality rules.

### Your Task

Design a minimal validated configuration schema.

### Expected Thinking

Separate configuration from executable code and validate the configuration before runtime execution.

### Solution

A conceptual Pydantic model is:

```python
from pydantic import BaseModel

class DatasetConfig(BaseModel):
    name: str
    source: str
    target: str
    keys: list[str]
    load_strategy: str
    partition_column: str | None = None
    owner: str
    quality_rules: list[str] = []
```

Add validation so `load_strategy` is constrained to supported values and required fields are present.

### Why This Solution Works

Validation prevents malformed metadata from reaching the generic engine. The engine can then select reusable behavior from a small supported vocabulary.

### Production Considerations

In production, use strict schemas, environment overlays, secrets outside configuration, configuration tests, dry-run plans, ownership/SLA metadata, and a custom-code escape hatch for genuinely exceptional datasets.

### Common Mistakes

Putting arbitrary Python/SQL into every config; allowing unsupported strategy names; and treating YAML as an unbounded programming language.

### Key Takeaway

Configuration should describe supported behavior, not become a second application language.

## Question 10 — Explain checkpoint state and dbt relationships

### Problem

A pipeline processes `orders/2026-09-30`. It writes a durable output and then records the partition as `COMPLETE`. Separately, a dbt model transforms a raw orders source into a staging model.

### Your Task

Explain what the checkpoint means and distinguish a dbt `source()` from `ref()`.

### Expected Thinking

A checkpoint is a durable statement about pipeline progress. A source represents upstream data; `ref()` represents a dbt-managed model dependency.

### Solution

The correct checkpoint invariant is:

```text
COMPLETE
⇒ durable valid output exists
```

For dbt:

```sql
{{ source('raw', 'orders') }}
```

declares external/upstream data, while:

```sql
{{ ref('stg_orders') }}
```

references another dbt model and creates a dependency in the DAG.

### Why This Solution Works

State enables resume/recovery, while dbt's dependency declarations make transformation order and lineage explicit.

### Production Considerations

Persist checkpoint state durably, record row counts/logic version/timestamps, and ensure state is committed only after durable output. For dbt, use source freshness/tests and inspect compiled SQL when debugging.

### Common Mistakes

Writing COMPLETE before output; treating source and model as interchangeable; or assuming a checkpoint alone makes a step idempotent.

### Key Takeaway

State records progress; `source()` and `ref()` describe different kinds of transformation dependencies.

# Part II — Moderate


## Question 11 — Refactor a transformation around RunContext

### Problem

A daily pipeline has functions that call `datetime.now()`, read `ENV` directly, and infer the input partition from the machine clock.

### Your Task

Refactor the design so a test can execute the same logical interval twice with identical results.

### Expected Thinking

Move run-specific facts into explicit context and make transformation functions consume them rather than discover them implicitly.

### Solution

Define:

```python
from dataclasses import dataclass
from datetime import datetime, date

@dataclass(frozen=True)
class RunContext:
    run_id: str
    logical_date: date
    run_timestamp: datetime
    environment: str
```

Pass `RunContext` to orchestration/steps. Derive the source partition from `logical_date`, not `datetime.now()`. Use `run_timestamp` only when it is intentionally part of the output contract.

### Why This Solution Works

The transformation now has explicit inputs. Running the same logical date with the same source data and configuration can produce the same output.

### Production Considerations

Persist the context/run record, define timezone conventions, validate interval boundaries, and ensure retries reuse the intended logical interval rather than creating a new hidden interval.

### Common Mistakes

Leaving one hidden `now()` call; reading environment variables inside pure logic; or generating a new logical date during retry.

### Key Takeaway

A run contract should make time, environment, and identity explicit rather than implicit global state.

## Question 12 — Merge CDC changes with a version guard

### Problem

A customer table receives CDC records:

```text
customer_id | status | updated_at | sequence_number
10          | gold   | 12:00      | 20
10          | silver | 11:59      | 19
```

The records can arrive out of order.

### Your Task

Write a merge design that prevents the older version from overwriting the newer version.

### Expected Thinking

First identify the target's logical key, then compare source version information against the target before updating.

### Solution

A PostgreSQL-style conceptual merge is:

```sql
merge into dim_customer as t
using incoming as s
on t.customer_id = s.customer_id
when matched
 and s.sequence_number > t.sequence_number
then update set
    status = s.status,
    updated_at = s.updated_at,
    sequence_number = s.sequence_number
when not matched then
    insert (customer_id, status, updated_at, sequence_number)
    values (s.customer_id, s.status, s.updated_at, s.sequence_number);
```

If multiple source rows for the same key arrive in one batch, deduplicate them first.

### Why This Solution Works

The version guard makes state monotonic: an older sequence cannot replace a newer one.

### Production Considerations

Use a trustworthy version/sequence source, define tie-breakers, handle tombstones, deduplicate within the batch, and add reconciliation/uniqueness checks.

### Common Mistakes

Using `updated_at` without considering equal timestamps; merging duplicate source rows; or updating every match regardless of version.

### Key Takeaway

Out-of-order CDC requires explicit version ordering and a guard against stale updates.

## Question 13 — Compute affected partitions from changed orders

### Problem

An order correction for `order_date = 2026-09-15` changes daily revenue. Your downstream aggregate is partitioned by order date.

### Your Task

Determine what must be recomputed and explain why a source-row change can propagate to a downstream partition.

### Expected Thinking

Trace the dependency graph from the changed row to the aggregate grain. Recompute the affected downstream partition rather than blindly rebuilding all history.

### Solution

If `fct_daily_revenue` has grain one row per day, a correction to an order dated 2026-09-15 affects the 2026-09-15 aggregate.

```text
changed order
   ↓
fct_order_lines
   ↓
fct_daily_revenue / 2026-09-15
```

Rebuild that partition after validating all required source inputs.

### Why This Solution Works

The affected scope follows the downstream model's grain, not merely the source record's existence.

### Production Considerations

Maintain dependency-aware invalidation, track affected partitions, preserve logic versions, and ensure concurrent normal runs cannot overwrite a backfill unexpectedly.

### Common Mistakes

Recomputing only the source row when the downstream aggregation needs the whole partition; or rebuilding the entire table for one correction.

### Key Takeaway

Incremental correctness requires propagating change to every downstream unit whose derived value can change.

## Question 14 — Choose a late-data lookback from a distribution

### Problem

Observed ingestion lateness over 1 million records is:

```text
p95 = 18 hours
p99 = 46 hours
maximum observed = 5 days
```

The daily fact pipeline currently uses a 24-hour lookback.

### Your Task

Choose an initial lookback policy and explain what happens to records arriving beyond it.

### Expected Thinking

Use the required correctness target, not merely the average lateness. The lookback should cover the chosen percentile plus operational margin, while exceptions need a separate repair path.

### Solution

If the operational goal is to cover at least p99 of ordinary late arrivals, 24 hours is insufficient because p99 is 46 hours.

A reasonable initial policy is, for example:

```text
lookback = 72 hours
```

because it covers p99 plus margin. The exact value must be validated against cost and business requirements.

Records beyond the window should be measured and sent to targeted reprocessing/manual correction rather than silently discarded.

### Why This Solution Works

The lookback converts a statistical lateness profile into an explicit correctness/cost policy. A finite window cannot guarantee all possible lateness.

### Production Considerations

Track lateness continuously, monitor the fraction beyond the window, periodically reassess p95/p99, and maintain targeted backfill procedures.

### Common Mistakes

Choosing p95 when the business requires near-p99 coverage; using the maximum observed value forever without cost analysis; or assuming a lookback eliminates all late-data problems.

### Key Takeaway

A lookback is a measured operational policy, not an arbitrary interval.

## Question 15 — Make Python and SQL hashes agree

### Problem

Python hashes `C-1001` after trimming whitespace and uppercasing. SQL hashes the raw database value. Both teams report different SHA-256 values.

### Your Task

Diagnose the discrepancy and define a cross-system canonical serialization contract.

### Expected Thinking

Compare bytes, not visual values. Hash equality requires identical canonical strings, encoding, and formatting.

### Solution

Define:

```text
trim
→ uppercase
→ explicit NULL token if applicable
→ canonical numeric/timestamp formatting
→ UTF-8 encoding
→ SHA-256
```

Then implement the exact same sequence in Python and SQL. For multiple columns, specify column order and delimiters explicitly, for example:

```text
customer_id || '|' || normalized_segment
```

before UTF-8 SHA-256 hashing.

### Why This Solution Works

SHA-256 itself is deterministic. The disagreement comes from different input serialization before hashing.

### Production Considerations

Publish the canonicalization contract as part of the schema/data contract, add cross-engine golden test vectors, and test NULL, Unicode, timestamps, whitespace, and numeric edge cases.

### Common Mistakes

Comparing only the hash algorithm name; ignoring column order; or assuming SQL and Python automatically normalize strings identically.

### Key Takeaway

Hash parity requires identical canonical bytes, not merely the same hash function.

## Question 16 — Point-in-time FX enrichment

### Problem

An order occurred on September 10. The FX table contains multiple rates for the currency, each effective for a different period.

### Your Task

Design an as-of lookup that chooses the rate valid at the order's event time.

### Expected Thinking

This is not a current-state lookup. Match on currency and choose the latest reference record whose effective time is at or before the fact's event time.

### Solution

Conceptually:

```sql
select
    o.order_id,
    o.currency,
    o.order_time,
    fx.rate
from orders o
join fx_rates fx
  on fx.currency = o.currency
 and fx.effective_at <= o.order_time
qualify row_number() over (
    partition by o.order_id
    order by fx.effective_at desc
) = 1;
```

If the SQL engine does not support `QUALIFY`, use a subquery/CTE with `row_number()` and filter outside.

### Why This Solution Works

The as-of rule prevents today's reference value from rewriting historical meaning.

### Production Considerations

Validate FX-key uniqueness per effective timestamp, define missing-rate policy, measure coverage, and backfill affected historical periods when reference data is corrected.

### Common Mistakes

Joining only on currency; using the latest current rate; or allowing multiple equally valid effective rows without a deterministic tie-breaker.

### Key Takeaway

Time-varying reference data requires point-in-time semantics, not ordinary current-state enrichment.

## Question 17 — Validate metadata with Pydantic

### Problem

A YAML dataset definition contains `load_strategy: merg`, an empty owner, and a partition column for a dataset declared as unpartitioned.

### Your Task

Design validation that rejects the configuration before execution.

### Expected Thinking

Configuration validation should fail fast and encode supported combinations, not merely check that fields exist.

### Solution

Use a constrained schema conceptually:

```python
from typing import Literal
from pydantic import BaseModel, model_validator

class DatasetConfig(BaseModel):
    name: str
    source: str
    target: str
    keys: list[str]
    load_strategy: Literal[
        "append", "merge", "delete_insert", "overwrite"
    ]
    partition_column: str | None = None
    owner: str

    @model_validator(mode="after")
    def validate_strategy(self):
        if self.load_strategy == "merge" and not self.keys:
            raise ValueError("merge requires keys")
        return self
```

Also reject an invalid partition configuration according to the project's rules.

### Why This Solution Works

The generic engine receives only validated configurations, reducing runtime ambiguity and preventing typo-driven strategy selection.

### Production Considerations

Add YAML parsing tests, schema-versioning, environment overlays, secret separation, dry-run validation, and golden configuration fixtures.

### Common Mistakes

Accepting arbitrary strings and branching on them later; validating only syntax; or embedding secrets in YAML.

### Key Takeaway

A metadata-driven engine is safe only when its metadata has a strict, testable contract.

## Question 18 — Recover from a failed partition using a ledger

### Problem

A pipeline tracks `dataset × partition` in a partition ledger. Partition `2026-09-30` has `RUNNING`, while its worker crashed before completion.

### Your Task

Design the recovery logic.

### Expected Thinking

Distinguish incomplete state from durable valid output. A RUNNING record is not evidence that processing completed.

### Solution

Inspect the partition and determine whether a durable output exists and is valid. If not, mark the partition eligible for retry.

A safe state flow is:

```text
PENDING
  ↓
RUNNING
  ↓
write durable output
  ↓
validate
  ↓
COMPLETE
```

On crash:

```text
RUNNING
  ↓
retry/recover
```

The retry must be idempotent or replace the partition atomically.

### Why This Solution Works

The ledger records execution state, but correctness comes from the relationship between durable output and state. The final COMPLETE transition is the commit point.

### Production Considerations

Use stale-run detection, run IDs, timestamps, row counts, logic version, advisory locks where needed, and operational state-repair procedures.

### Common Mistakes

Treating RUNNING as complete; deleting the ledger record without inspecting output; or marking COMPLETE before validation.

### Key Takeaway

Resume logic must reconcile state with durable data, not trust a status field blindly.

## Question 19 — Design a dbt incremental model

### Problem

`fct_order_lines` is large and receives new and corrected rows. Each row has `order_line_id` and `loaded_at`.

### Your Task

Write a conceptual dbt model using an incremental filter, unique key, and lookback.

### Expected Thinking

The model needs a stable identity and a bounded arrival-time window. Deduplication should occur within the reprocessed scope.

### Solution

A conceptual dbt model is:

```sql
{{ config(
    materialized='incremental',
    unique_key='order_line_id'
) }}

with incoming as (
    select *
    from {{ ref('stg_order_lines') }}

    {% if is_incremental() %}
    where loaded_at >= (
        select max(loaded_at) - interval '3 days'
        from {{ this }}
    )
    {% endif %}
),

deduped as (
    select *
    from incoming
    qualify row_number() over (
        partition by order_line_id
        order by loaded_at desc
    ) = 1
)

select *
from deduped
```

The exact interval syntax and `QUALIFY` support depend on the adapter.

### Why This Solution Works

`is_incremental()` bounds normal work while the unique key and deduplication make repeated lookback processing converge toward one logical record.

### Production Considerations

Test incremental vs full-refresh equivalence, choose `on_schema_change` deliberately, document the lookback policy, and define full-refresh/backfill procedures.

### Common Mistakes

Using only `loaded_at > max(loaded_at)`; omitting the unique key; or assuming the adapter supports every SQL expression identically.

### Key Takeaway

A production incremental model combines bounded work with explicit identity and late-data correctness.

## Question 20 — Design dbt tests for a customer mart

### Problem

`dim_customer` is intended to contain one current row per customer. Status must be one of `active`, `inactive`, or `suspended`.

### Your Task

Design tests that validate the model's grain, required key, controlled status vocabulary, and relationship to an orders fact.

### Expected Thinking

Translate the model contract into data invariants.

### Solution

Use:

```yaml
models:
  - name: dim_customer
    columns:
      - name: customer_id
        tests:
          - not_null
          - unique

      - name: status
        tests:
          - accepted_values:
              values:
                - active
                - inactive
                - suspended

  - name: fct_orders
    columns:
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customer')
              field: customer_id
```

Add a singular test if there is a business rule such as prohibited customer states.

### Why This Solution Works

The tests correspond directly to the declared grain and business contract: one current row per customer, non-null identity, controlled status, and valid fact-to-dimension relationships.

### Production Considerations

Use appropriate severity, investigate failures rather than blindly disabling tests, and add source freshness/contract validation for critical upstream interfaces.

### Common Mistakes

Testing `unique` on a non-key attribute; omitting `not_null`; or using relationships when the model intentionally allows unknown members without documenting the policy.

### Key Takeaway

Good tests are executable statements of the model's grain and business invariants.

# Part III — Hard


## Question 21 — Debug duplicate CDC updates after retry

### Problem

A CDC worker retries a batch. The target now contains two rows for the same customer version. The source batch itself also contains a duplicate event.

### Your Task

Redesign the pipeline so retries and duplicate input converge to one correct target state.

### Expected Thinking

You need both within-batch deduplication and an idempotent target load. The retry must not create another logical record.

### Solution

First deduplicate source events by business key/version, keeping one deterministic winner.

Then use a merge keyed by the logical customer ID/version or the appropriate current-state key. If updates are mutable, guard updates by version.

The invariant is:

```text
same logical input processed N times
→ same target state
```

For a current-state table, an older sequence must never overwrite a newer sequence.

### Why This Solution Works

Deduplication handles duplicate input; merge/idempotency handles repeated execution. Neither alone is sufficient.

### Production Considerations

Record batch/run identity, use version guards, monitor duplicate rates, validate target uniqueness, and make the write atomic where possible.

### Common Mistakes

Only deduplicating the source and then appending; only using a merge without handling duplicate source keys; or relying on arrival order.

### Key Takeaway

Idempotency is an end-to-end property: input deduplication and target write semantics must work together.

## Question 22 — Late facts break an incremental aggregate

### Problem

A daily revenue model processes one day's orders. Two days later, a legitimate order for the old business date arrives. The daily aggregate is now understated.

### Your Task

Design a correction that handles late facts without rebuilding the entire history.

### Expected Thinking

Separate event-date partitioning from load-date arrival. Identify the affected business partition and reprocess a bounded or targeted scope.

### Solution

If the late order has `order_date = 2026-09-20`, mark the 2026-09-20 downstream aggregate stale.

A correction flow is:

```text
late fact detected
→ identify event-date partition
→ invalidate/reprocess affected partition
→ recompute daily revenue
→ validate/reconcile
→ mark complete
```

If lateness is normally within three days, a three-day lookback can catch routine cases. Beyond-window records need targeted backfill.

### Why This Solution Works

The aggregate is derived from business-date facts, so correctness requires recomputing the affected business partition even though the record arrived later.

### Production Considerations

Measure lateness distribution, choose an evidence-based lookback, track beyond-window exceptions, and protect month-end/financial close with explicit restatement procedures.

### Common Mistakes

Filtering only by load date; assuming late facts belong to the arrival day; or using a huge lookback without considering compute cost.

### Key Takeaway

Late-data correctness requires aligning incremental processing with the time semantics of the derived dataset.

## Question 23 — Correct a time-varying reference-data history

### Problem

A tax-rate table was corrected for July. Orders from July through September were enriched using the old rate.

### Your Task

Design a targeted historical correction.

### Expected Thinking

Reference data is part of transformation state. Changing it can invalidate previously computed facts.

### Solution

Identify the reference validity interval and affected fact partitions:

```text
tax correction: July 1–July 31
          ↓
orders whose event time falls in July
          ↓
recompute affected derived amounts
```

Validate coverage before and after the correction. If the affected downstream dataset is large, use a shadow target and atomic replacement where the module's backfill pattern supports it.

### Why This Solution Works

Point-in-time enrichment makes historical outputs depend on the reference version valid at the event time. A corrected reference therefore requires historical recomputation.

### Production Considerations

Version reference data, retain audit history, record transformation/version metadata, and maintain targeted backfill capability.

### Common Mistakes

Joining the current tax rate to historical orders; rebuilding unrelated months; or changing the lookup without recording which reference version was used.

### Key Takeaway

Reference-data corrections are data changes that can propagate historically through enriched facts.

## Question 24 — Hash-based SCD change detection

### Problem

A customer dimension has a business key and many attributes. The source sends a daily full extract, but no reliable per-column change flags.

### Your Task

Design a hash-diff approach to detect changed customer versions.

### Expected Thinking

Create a canonical representation of the tracked attributes, hash it deterministically, and compare the new hash to the current stored hash.

### Solution

For tracked columns:

```text
canonicalize values
→ serialize in fixed column order
→ SHA-256
→ compare source_hash with current_hash
```

If hashes differ, create a new SCD2 version; if they match, no attribute change occurred.

The canonicalization contract must specify NULL tokens, whitespace/case rules, numeric/timestamp formatting, timezone, and encoding.

### Why This Solution Works

A deterministic hash compresses a multi-column comparison into a stable fingerprint while preserving exact equality under the agreed serialization contract.

### Production Considerations

Keep the original business attributes as well as the hash, test cross-engine parity, monitor schema changes, and remember that plain hashing is not anonymization.

### Common Mistakes

Hashing raw concatenated values without delimiters; changing column order; treating different NULL representations as equivalent unintentionally; or using the hash as a secret identifier.

### Key Takeaway

Hash diffs are reliable only when canonical serialization is stable and explicitly governed.

## Question 25 — Build a metadata-driven engine safely

### Problem

You must process 500 datasets with common steps but different source/target names, keys, partitioning, quality rules, and load strategies.

### Your Task

Design a metadata-driven engine without turning YAML into an uncontrolled programming language.

### Expected Thinking

Separate declarative configuration from reusable code. Validate configuration and route supported strategies through registries/plugins.

### Solution

A safe design is:

```text
YAML
 ↓
Pydantic DatasetConfig
 ↓
validated execution plan
 ↓
load-strategy registry
 ↓
registered transformations
 ↓
generic pipeline engine
```

Configuration describes source, target, keys, partition, strategy, owner, SLA, and quality rules. A registry maps `merge` or `append` to trusted implementation functions.

### Why This Solution Works

The engine stays generic because the code implements a small set of supported behaviors while metadata selects them. Validation prevents arbitrary configuration from becoming executable code.

### Production Considerations

Add dry-run plans, golden tests, configuration versioning, environment overlays, safe identifier allowlists, secrets outside configuration, and a custom-code escape hatch for exceptional datasets.

### Common Mistakes

Adding dozens of special-case flags; allowing arbitrary SQL/Python fragments; or building a platform so generic that nobody can understand how a dataset executes.

### Key Takeaway

Metadata-driven design should reduce duplication without creating an opaque second programming language.

## Question 26 — Recover after a checkpoint ordering bug

### Problem

A worker writes `partition=2026-09-30, status=COMPLETE` and then crashes before the output file is durably committed. A retry sees COMPLETE and skips the partition.

### Your Task

Identify the correctness violation and redesign the checkpoint commit order.

### Expected Thinking

State must never claim successful durable work before the work is durable and validated.

### Solution

The current invariant is broken because:

```text
COMPLETE
```

does not imply durable output.

Correct order:

```text
write durable output
→ validate durable output
→ commit COMPLETE state
```

If the output write is atomic, commit state only after the atomic publish succeeds. Repair the incorrect COMPLETE record by inspecting the actual output and resetting/reprocessing the partition.

### Why This Solution Works

The checkpoint is a progress statement, so its truth depends on the durable output it describes. Reversing the order creates false completion.

### Production Considerations

Use transaction/atomic-publish semantics where available, row counts/checksums, state repair tooling, and chaos tests that deliberately fail between output and state commits.

### Common Mistakes

Treating the ledger as authoritative without verifying output; merely changing COMPLETE to FAILED without reprocessing; or committing state before validation.

### Key Takeaway

Checkpoint state must follow durable validated output, never precede it.

## Question 27 — Prevent concurrent processing of one partition

### Problem

Two workers start processing the same dataset partition at nearly the same time. Both see the partition as PENDING and both begin writing.

### Your Task

Design a concurrency guard and explain what correctness property it protects.

### Expected Thinking

A check-then-act race exists. Both workers can observe PENDING before either claims the work. The claim must be atomic.

### Solution

Use a durable state claim protected by a transaction and, where taught/supported, a PostgreSQL advisory lock.

Conceptually:

```text
begin transaction
→ acquire dataset/partition lock
→ verify current state
→ claim RUNNING
→ commit
→ process
```

If another worker cannot acquire the lock, it should not process the same partition concurrently.

### Why This Solution Works

The lock closes the race between observing state and claiming ownership. Idempotency remains necessary because locks do not eliminate crashes/retries.

### Production Considerations

Define lock scope, timeout behavior, stale-run recovery, and what happens if a worker dies while holding the lock. Combine concurrency control with durable state and idempotent writes.

### Common Mistakes

Using an in-memory lock; checking state without an atomic claim; or assuming a lock alone guarantees correct output after a crash.

### Key Takeaway

Concurrency control prevents overlapping ownership; idempotency protects correctness when execution is retried.

## Question 28 — Diagnose dbt incremental vs full-refresh mismatch

### Problem

A dbt `fct_order_lines` incremental run contains 10,000,000 rows, while a full-refresh build contains 10,020,000. Tests pass for uniqueness in both outputs.

### Your Task

Investigate the mismatch and identify likely root causes.

### Expected Thinking

Do not assume uniqueness proves completeness. Compare source scope, incremental predicate, late data, deduplication, and full-refresh semantics.

### Solution

Investigation:

1. Identify the 20,000-row difference using key anti-joins.
2. Check whether missing rows have `loaded_at` older than the incremental lookback.
3. Inspect whether source corrections occurred after initial processing.
4. Verify the `unique_key` and deduplication logic.
5. Compare the compiled SQL for incremental and full-refresh contexts.
6. Determine whether `on_schema_change` or logic changes altered historical behavior.

Likely root causes include an overly narrow predicate or late data beyond the lookback.

### Why This Solution Works

Full refresh establishes the historical transformation result; incremental processing is an optimization that must converge to it. A mismatch is evidence that the incremental contract is incomplete.

### Production Considerations

Automate reconciliation, track beyond-window late records, version transformation logic, and maintain targeted historical rebuild procedures.

### Common Mistakes

Checking only row counts; assuming a uniqueness test proves completeness; or immediately running full-refresh without diagnosing why incremental processing diverged.

### Key Takeaway

Incremental correctness should be demonstrated by reconciliation against the equivalent full rebuild.

## Question 29 — Design a snapshot with late-arriving dimension changes

### Problem

Customer status changes on June 1 but the update arrives June 5. The customer dimension is used for historical reporting.

### Your Task

Design the history model so the late change does not silently misrepresent the customer's state.

### Expected Thinking

Separate source arrival time from valid business time. Determine whether the snapshot mechanism can represent the correction and whether downstream facts require restatement.

### Solution

Preserve the source's effective/change timestamp when available. The historical model must represent:

```text
customer status
valid_from
valid_to
current-state indicator
```

Then determine which downstream point-in-time joins or aggregates are affected by the corrected historical state. If the late change alters historical analytical outputs, invalidate and reprocess the affected intervals.

### Why This Solution Works

A snapshot preserves versions, but a late-arriving version can change what was valid during an earlier business interval. Historical correctness may therefore propagate downstream.

### Production Considerations

Define timestamp reliability, correction policy, audit history, point-in-time join semantics, and targeted restatement procedures.

### Common Mistakes

Using load date as the customer's valid date; updating only the current row; or assuming a snapshot automatically repairs every downstream aggregate.

### Key Takeaway

Historical dimensions require explicit valid-time semantics and a plan for corrections that propagate into dependent datasets.

## Question 30 — Plan a safe month-long backfill

### Problem

A transformation bug affected 30 daily partitions. Each partition takes 8 minutes and requires 2 GB of temporary working storage. Normal daily runs must continue.

### Your Task

Estimate serial runtime and design a bounded backfill strategy.

### Expected Thinking

Calculate baseline cost, then choose bounded parallelism without starving normal workloads.

### Solution

Serial runtime:

```text
30 × 8 minutes = 240 minutes = 4 hours
```

A bounded pool of 4 workers gives an idealized lower bound of about:

```text
240 / 4 = 60 minutes
```

assuming independent partitions and no contention. In practice, expect overhead and resource constraints.

Use:

```text
identify affected partitions
→ validate inputs
→ process with bounded concurrency
→ checkpoint each partition
→ validate results
→ reconcile
→ publish/swap safely
```

Reserve capacity for normal runs rather than consuming all workers.

### Why This Solution Works

Backfills are parallelizable when partitions are independent, but unbounded parallelism can exhaust resources and delay normal production work.

### Production Considerations

Measure actual runtime/resource usage, use shadow outputs for risky corrections, track logic version, support resume after failure, and use atomic publication where appropriate.

### Common Mistakes

Assuming perfect linear speedup; using 30 concurrent workers because there are 30 partitions; or failing to reserve capacity for normal processing.

### Key Takeaway

Backfill performance is a constrained scheduling problem: maximize useful parallelism without compromising normal production service or correctness.

# Part IV — Advanced


## Question 31 — Design a production transformation layer for 500 datasets

### Problem

A company has 500 daily datasets. Most follow common patterns, but about 5% have special enrichment or load behavior. The platform needs deterministic reruns, backfills, state, ownership, quality rules, and operational visibility.

### Your Task

Design the architecture and explain where generic behavior ends and custom behavior begins.

### Expected Thinking

Start with a declarative dataset contract, then identify reusable pipeline primitives. Avoid putting executable business logic directly into configuration.

### Solution

Architecture:

```text
YAML metadata
   ↓
Pydantic DatasetConfig
   ↓
validated execution plan
   ↓
RunContext
   ↓
registered steps
   ├─ read
   ├─ normalize
   ├─ deduplicate
   ├─ enrich
   ├─ validate
   └─ load strategy
   ↓
partition ledger/checkpoints
   ↓
durable outputs
```

A registry maps supported strategies and transformations to trusted code. The 5% exceptions use a controlled custom-code escape hatch.

Every run has explicit logical interval, run ID, environment, configuration/version, and deterministic behavior.

### Why This Solution Works

The architecture reduces repeated code while retaining understandable execution semantics. State and run contracts make retries/backfills operationally tractable.

### Production Considerations

Add ownership/SLA metadata, dry-run plans, golden tests, configuration versioning, safe SQL identifier allowlists, observability, advisory locks, stale invalidation, and state-repair procedures.

### Common Mistakes

Making all behavior configurable; creating hundreds of flags; putting arbitrary SQL in YAML; or forcing exceptional datasets through a generic abstraction that obscures their semantics.

### Key Takeaway

A metadata-driven platform should be a constrained execution framework with explicit contracts, not an unrestricted programming language.

## Question 32 — Prove correctness of a CDC pipeline under retries and out-of-order delivery

### Problem

An order-status CDC pipeline receives duplicates, out-of-order versions, and late events. Workers may retry after partial failure.

### Your Task

Design the pipeline and state the invariants that establish correctness.

### Expected Thinking

Combine within-batch deduplication, version guards, idempotent merge behavior, and durable checkpoints. Define correctness before implementation.

### Solution

Use this flow:

```text
read CDC interval
→ deduplicate by order_id/version
→ select deterministic winner
→ merge with version guard
→ validate target invariants
→ commit partition/run state
```

Core invariants:

1. Duplicate input does not create duplicate logical state.
2. An older version cannot overwrite a newer version.
3. Reprocessing the same interval converges to the same target state.
4. COMPLETE state implies durable validated output.
5. A failed worker can retry without corrupting prior successful work.

### Why This Solution Works

The combination handles both bad input ordering and bad execution ordering. Version guards protect state monotonicity; idempotent merge protects retries; checkpoints protect resumability.

### Production Considerations

Use audit records, sequence/version metrics, duplicate-rate monitoring, partition ledger, advisory locks for concurrent ownership, and targeted repair for invalid historical state.

### Common Mistakes

Claiming exactly-once execution merely because a merge is used; ignoring duplicate source events; or committing checkpoints before durable validation.

### Key Takeaway

Exactly-once effects are achieved through system design—idempotent writes, identity/version semantics, state ordering, and recovery—not by assuming workers execute exactly once.

## Question 33 — Design a 12-month logic-change backfill

### Problem

A revenue transformation bug affects the last 12 months. The corrected logic changes 365 daily partitions. Normal production processing must continue and consumers cannot see a partially corrected history.

### Your Task

Design a safe backfill using transformation versioning, shadow output, bounded parallelism, validation, and atomic publication.

### Expected Thinking

Separate computation from publication. Compute corrected data independently, validate it, then publish as a controlled state transition.

### Solution

Plan:

```text
identify affected partitions
→ assign transform_version = v2
→ create shadow target
→ process partitions with bounded concurrency
→ checkpoint each partition
→ reconcile against expected totals
→ validate row counts/grain/quality
→ compare old vs new outputs
→ atomic swap/publish
→ mark v2 current
```

Normal runs continue on the production target while the shadow target is built, subject to the platform's consistency/publication design.

### Why This Solution Works

Shadow processing prevents partially corrected partitions from becoming visible. Versioning makes the historical semantics explicit and makes resume/invalidation decisions possible.

### Production Considerations

Define consumer impact, source completeness, resource reservations, rollback strategy, audit history, validation thresholds, and what happens if new production data overlaps the backfill interval.

### Common Mistakes

Updating production partitions one at a time; using full refresh without scope control; or swapping without reconciliation.

### Key Takeaway

A safe large backfill separates compute, validation, and publication and treats the backfill as a versioned production change.

## Question 34 — Design state and resumability for a multi-step pipeline

### Problem

A pipeline has six steps and processes 100 daily partitions. Each step can fail independently. Some outputs are expensive to recompute.

### Your Task

Design state so the pipeline can resume at the smallest safe unit without claiming false completion.

### Expected Thinking

Use both run-level and partition/step-level state. State should describe durable output and be committed only after validation.

### Solution

Use records conceptually like:

```text
run
  run_id
  logical_interval
  config_version
  status

partition_step
  dataset
  partition
  step
  status
  started_at
  completed_at
  row_count
  logic_version
```

A successful step follows:

```text
PENDING
→ RUNNING
→ durable output
→ validate
→ COMPLETE
```

On retry, check whether durable output and COMPLETE state exist. If output exists but state does not, repair or safely revalidate rather than blindly duplicating effects.

### Why This Solution Works

Fine-grained state reduces unnecessary recomputation while preserving explicit recovery semantics. The durable output is the evidence; the state record summarizes verified progress.

### Production Considerations

Use state CLI tooling, stale-run detection, advisory locks, audit records, chaos testing, and state-repair procedures. Decide which outputs are immutable and which are replaceable.

### Common Mistakes

Tracking only a single global watermark; storing state only in process memory; or marking a step complete before output validation.

### Key Takeaway

Resumability is a correctness feature: state must be durable, truthful, and aligned with the smallest safe unit of recovery.

## Question 35 — Design a concurrent pipeline with stale partition invalidation

### Problem

Two versions of transformation logic can exist during deployment. Some partitions were processed with version `v1`, while a business rule requires all affected partitions to use `v2`. A worker can also remain RUNNING indefinitely after a crash.

### Your Task

Design invalidation, stale detection, and safe recomputation.

### Expected Thinking

State must include logic version and timestamps. A partition can be logically stale even if its status is COMPLETE.

### Solution

For each partition:

```text
if status = COMPLETE
and logic_version = v1
and required_version = v2
→ INVALID
```

For stale RUNNING records, compare heartbeat/start time to an operational timeout. If stale, require safe ownership recovery before retry.

Then:

```text
invalidate
→ acquire partition ownership
→ recompute with v2
→ validate
→ commit COMPLETE(v2)
```

Downstream partitions whose inputs changed must also be invalidated/recomputed.

### Why This Solution Works

Status alone cannot determine validity. The output's logic version is part of its correctness identity.

### Production Considerations

Use explicit version metadata, dependency-aware invalidation, advisory locks, stale-run recovery, audit records, and a controlled state-repair CLI.

### Common Mistakes

Changing code without invalidating prior outputs; treating all COMPLETE partitions as current; or allowing two workers to repair the same stale partition concurrently.

### Key Takeaway

Pipeline state must represent both execution status and semantic validity.

## Question 36 — Design a production dbt silver-to-gold layer

### Problem

An order platform has raw orders, order lines, customers, and products. The gold layer needs `dim_customer`, `fct_order_lines`, and `fct_daily_revenue` with tests, freshness, incremental processing, and documentation.

### Your Task

Design the dbt project structure and model graph, including where snapshots, sources, tests, and Python models fit.

### Expected Thinking

Start with source declarations, then staging, intermediate, and marts. Define grain and materialization before writing SQL.

### Solution

A suitable conceptual graph is:

```text
sources
├─ raw_orders
├─ raw_order_lines
├─ raw_customers
└─ raw_products
       ↓
staging
├─ stg_orders
├─ stg_order_lines
├─ stg_customers
└─ stg_products
       ↓
intermediate
├─ int_order_lines
└─ int_customer_orders
       ↓
marts
├─ dim_customer       ← snapshot/history logic
├─ fct_order_lines    ← incremental + lookback
└─ fct_daily_revenue  ← tested aggregate
```

Use `source()` for raw datasets and `ref()` between dbt models. Add source freshness, `not_null`, `unique`, `accepted_values`, relationships, singular business-rule tests, documentation, and contracts for critical marts.

### Why This Solution Works

The layered graph isolates source-specific cleanup, reusable transformations, and consumer-facing semantics. Materializations can then be selected according to workload rather than mixing all concerns in one model.

### Production Considerations

Verify adapter support for incremental strategies, snapshots, Python models, contracts, and state-aware CI. Add reconciliation between incremental and full rebuild outputs.

### Common Mistakes

Putting all business logic in one mart; hard-coding raw table names; using Python for every transformation; or assuming dbt replaces ingestion/orchestration.

### Key Takeaway

A production dbt layer is a tested transformation graph with explicit grain, dependencies, materialization, interfaces, and operational boundaries.

## Question 37 — Diagnose a revenue fan-out incident

### Problem

Revenue is 2.0× higher after a new product-category enrichment. The fact table row count also increased. The lookup team says the category table is 'small' and the join is syntactically correct.

### Your Task

Diagnose the incident and design preventive controls.

### Expected Thinking

Measure row multiplication before looking at arithmetic. Compare pre/post join cardinality and validate lookup-key uniqueness.

### Solution

Investigation:

```sql
select product_id, count(*) as n
from product_category
group by product_id
having count(*) > 1;
```

Then compare:

```text
fact rows before join
vs
fact rows after join
```

If a product has two matching category rows, one fact row becomes two rows and revenue doubles.

Fix by making the reference key unique or by selecting the correct point-in-time/versioned record before joining. Add a lookup uniqueness test and a reconciliation invariant that enrichment does not unexpectedly change fact grain.

### Why This Solution Works

The join changed cardinality. Revenue doubled because measures were duplicated, not because the revenue calculation itself changed.

### Production Considerations

Monitor lookup coverage and fan-out, validate effective-date semantics, quarantine invalid reference data where appropriate, and maintain targeted historical backfill if corrected reference data changes past results.

### Common Mistakes

Using `distinct` after aggregation; filtering duplicates arbitrarily; or assuming a small lookup table cannot create fan-out.

### Key Takeaway

Every enrichment join has a cardinality contract, and measure correctness depends on preserving the intended fact grain.

## Question 38 — Design a 500-dataset checkpointed configuration engine

### Problem

A platform processes 500 datasets using YAML metadata. Each dataset has different owners, SLAs, partitions, and load strategies. Operators need dry runs, state visibility, resume, and safe configuration changes.

### Your Task

Design the metadata, validation, execution, and state architecture.

### Expected Thinking

Treat configuration as an API. Separate declaration, validation, execution planning, runtime state, and operational repair.

### Solution

Architecture:

```text
YAML
 ↓
Pydantic DatasetConfig
 ↓
config version
 ↓
dry-run execution plan
 ↓
registered strategy/step registry
 ↓
RunContext
 ↓
partition ledger + run ledger
 ↓
durable output
 ↓
validated COMPLETE
```

Configuration should include source, target, keys, load strategy, partitioning, quality rules, owner, SLA, and dependencies. Secrets remain outside configuration.

A state CLI should answer which datasets/partitions are RUNNING, COMPLETE, FAILED, stale, or invalidated.

### Why This Solution Works

Separating static metadata from dynamic state prevents configuration from becoming a mutable execution log. Versioning allows operators to identify which behavior produced each partition.

### Production Considerations

Use golden tests for configurations, environment overlays, allowlists for identifiers, advisory locks, stale invalidation, audit history, and a custom-code escape hatch.

### Common Mistakes

Putting status in YAML; changing configuration without versioning; or making every exception a new boolean flag.

### Key Takeaway

Metadata describes intended behavior; state records actual execution history. Keeping them separate is fundamental.

## Question 39 — Prove exactly-once effects under at-least-once execution

### Problem

Workers may execute the same partition multiple times because of retries. The platform cannot guarantee exactly-once worker execution, but consumers require exactly-once effects.

### Your Task

Explain how to design the system so at-least-once execution converges to exactly-once effects.

### Expected Thinking

Do not try to eliminate every retry. Make repeated execution produce the same durable result.

### Solution

Use an idempotent write contract.

For a replaceable partition:

```text
partition identity
→ write to isolated/staging target
→ validate
→ atomic replace/publish
```

For mutable records:

```text
stable business key
+
version guard
+
merge/upsert
```

For state:

```text
durable output
→ validation
→ COMPLETE
```

For every retry, the same logical partition/key/version should result in the same target state.

Correctness invariant:

```text
execute(input, N times)
=
execute(input, 1 time)
```

for all supported retry counts N.

### Why This Solution Works

Exactly-once effects are a property of durable state transitions and idempotent writes, not of execution count. A worker can run twice while the target still ends in one correct state.

### Production Considerations

Test retries and crash points with chaos testing, reconcile outputs, protect concurrent ownership, and define how side effects outside the database/object store are handled.

### Common Mistakes

Calling an at-least-once executor exactly-once; relying only on a checkpoint; or using append writes where duplicates are possible.

### Key Takeaway

Design for at-least-once execution and make the externally visible effect idempotent.

## Question 40 — Design the complete Module 2.12 transformation platform

### Problem

Design a production transformation platform for an orders domain that ingests CDC orders/customers, enriches with time-varying reference data, processes hundreds of datasets, supports backfills and late data, and publishes dbt gold models.

### Your Task

Produce an end-to-end architecture covering deterministic transformations, deduplication, incremental processing, late data, hashing, enrichment, metadata, checkpoints, concurrency, and dbt.

### Expected Thinking

Start with boundaries and invariants. Define the run contract and data grains before selecting technologies or implementation details.

### Solution

A coherent design is:

```text
sources
  ↓
ingestion/raw
  ↓
metadata-driven Python bronze→silver framework
  ├─ RunContext
  ├─ deterministic transformations
  ├─ deduplication
  ├─ hashing/change detection
  ├─ point-in-time enrichment
  ├─ Pandera validation
  ├─ load strategies
  ├─ partition ledger
  ├─ checkpoints
  ├─ advisory locks
  └─ stale invalidation
  ↓
dbt silver→gold
  ├─ sources/freshness
  ├─ staging
  ├─ intermediate
  ├─ marts
  ├─ incremental models
  ├─ snapshots
  ├─ data tests/contracts
  ├─ documentation/lineage
  └─ state-aware CI
  ↓
consumers
```

The run contract includes dataset, partition/data interval, run ID, configuration version, logic version, environment, and expected output.

Core invariants include:

```text
duplicate input → no duplicate logical target state
old version → cannot overwrite newer version
retry N times → same correct final state
COMPLETE → durable validated output
lookup join → preserves intended grain
incremental result ≈ full rebuild
stale logic version → invalidated/recomputed
```

Use bounded parallelism for backfills and reserve capacity for normal runs. Use shadow targets and atomic publication for risky historical corrections. Reconcile row counts, aggregates, duplicate counts, and fingerprints where appropriate.

### Why This Solution Works

The architecture combines the module's patterns rather than treating them as isolated techniques. Determinism supports idempotency; metadata supports scale; state supports recovery; lookbacks support late data; dbt provides the tested transformation DAG; reconciliation provides evidence of correctness.

### Production Considerations

Production implementation must define ownership, SLAs, observability, resource limits, security/secret handling, adapter-specific dbt behavior, operational repair, audit history, and deployment/version migration procedures. Test failure points explicitly through chaos scenarios.

### Common Mistakes

Common mistakes include choosing tools before defining invariants; using one universal load strategy; treating metadata as arbitrary code; relying on checkpoints without idempotent outputs; ignoring late reference-data corrections; and treating dbt as ingestion/orchestration.

### Key Takeaway

A production transformation platform is correct when its contracts, invariants, state transitions, retries, historical corrections, and consumer-facing outputs remain coherent under normal operation and failure—not merely when the happy-path run succeeds.

## Practice Set Coverage Summary

The 40 questions collectively cover:

| Module topic | Basic | Moderate | Hard | Advanced |
|---|---:|---:|---:|---:|
| 01 — Structuring ETL Code | ✓ | ✓ |  | ✓ |
| 02 — Deduplication and Merge Loads | ✓ | ✓ | ✓ | ✓ |
| 03 — Incremental Processing and Backfills | ✓ | ✓ | ✓ | ✓ |
| 04 — Late-Arriving Data and Reprocessing | ✓ | ✓ | ✓ | ✓ |
| 05 — Hashing and Change Detection | ✓ | ✓ | ✓ | ✓ |
| 06 — Lookups, Enrichment and Reference Data | ✓ | ✓ | ✓ | ✓ |
| 07 — Metadata and Config-Driven Pipelines | ✓ | ✓ | ✓ | ✓ |
| 08 — Checkpoints, State and Resumability | ✓ | ✓ | ✓ | ✓ |
| 09 — dbt | ✓ | ✓ | ✓ | ✓ |

The hardest questions intentionally combine multiple Module 2.12 patterns: deduplication + merge + version guards; incremental processing + late data; metadata + state; checkpoints + idempotency; enrichment + reconciliation; and dbt incremental correctness + full rebuild comparison.
