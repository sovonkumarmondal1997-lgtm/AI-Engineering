# Streams, Tasks, and Dynamic Tables

**Roadmap location:** `Stage 2C — Data Engineering_3/03-Snowflake-Deep-Dive/05-streams-tasks-and-dynamic-tables.md`  
**Lab location:** `experiments/05_streams_tasks/`  
**Learning phase:** Phase C — Transformation and Programmability (Intermediate → Advanced)

> **Scope note:** This lesson follows Topic 05 of `roadmap-Snowflake-Deep-Dive.md` in the required order after Topics 01–04 and before Topic 06. SQL is designed for a disposable learning schema; adjust object names and privileges to your account. Examples using `CREATE OR REPLACE` are illustrative and can reset stream offsets, replace data, or affect grants/dependencies. Never run them against valuable objects. Syntax and feature availability can evolve, so verify current documentation before production deployment.

## Learning objectives

By the end, you should be able to:

- Explain the different jobs of change capture, orchestration, and declarative transformation.
- Create and inspect standard and append-only streams and interpret their metadata.
- Explain when a stream offset advances and why a successful committed DML statement is central to safe consumption.
- Create scheduled, serverless, and warehouse-based tasks, plus task graphs with dependencies and finalizers.
- Implement an idempotent stream-to-table CDC pipeline that handles inserts, updates, and deletes.
- Create dynamic tables with explicit target lag and refresh mode, and compare them with task-based ELT, materialized views, and dbt.
- Diagnose task failures, refresh lag, and stream staleness without risking valuable data.
- Monitor operations, control cost, and decide where external orchestration belongs.

## Prerequisites

You should already understand:

1. Snowflake databases, schemas, tables, roles, and warehouses (Topic 01).
2. Warehouse sizing, auto-suspend/resume, and compute billing (Topic 02).
3. Micro-partitions and pruning at a conceptual level (Topic 03).
4. Loading data into raw tables and handling ingestion retries (Topic 04).
5. Basic SQL joins, transactions, `MERGE`, primary-key concepts, and `GROUP BY`.

A Snowflake account with permission to create a database/schema, streams, tasks, dynamic tables, and a warehouse is needed for the full lab. Serverless tasks, notifications, and some monitoring features can have additional account, role, or cloud configuration requirements.

---

# 1. The three responsibilities

Streams, tasks, and dynamic tables are related, but not interchangeable.

| Capability | Main responsibility | Mental model | Typical use |
|---|---|---|---|
| **Stream** | Expose change data between source-table versions | Change cursor / offset | Find inserts, updates, and deletes since a prior offset |
| **Task** | Schedule or trigger SQL/procedure execution | Orchestrator / worker | Run `MERGE`, call a procedure, coordinate dependent steps |
| **Dynamic table** | Keep a declared query result refreshed to a freshness target | Managed, declarative transformation | Maintain silver/gold projections and aggregates without writing refresh DML |

A stream does not run a pipeline by itself. A task does not automatically capture source changes unless the SQL or procedure does so. A dynamic table is not a stream consumer and does not require a user-authored task to refresh when its scheduler is enabled. Give each independent CDC consumer its own stream; two tasks consuming the same stream do not each receive an independent copy of the same delta.

## Architecture: raw → stream → task → MERGE → silver → dynamic table → gold

```text
                    Change capture + imperative ELT
┌────────────┐   ┌────────────┐   ┌─────────────────┐   ┌────────────┐
│ RAW_ORDERS │──▶│ ORDERS_STR │──▶│ TASK / MERGE    │──▶│ SILVER     │
│ source     │   │ change     │   │ transactional   │   │ current row│
└────────────┘   └────────────┘   └─────────────────┘   └─────┬──────┘
                                                               │
                                                               ▼
                                                   ┌─────────────────────┐
                                                   │ GOLD_DYNAMIC_TABLE  │
                                                   │ declarative SELECT  │
                                                   └─────────────────────┘

Stream = what changed     Task = when/how SQL runs     Dynamic table = what result to maintain
```

### Production framing

- **Mechanism:** streams expose a change set; tasks execute SQL or procedures on a schedule or trigger; dynamic tables refresh a query result according to `TARGET_LAG`.
- **Purpose:** process changes without repeatedly rebuilding every downstream table by hand.
- **Trade-off:** more incremental behavior can reduce work, but adds correctness, dependency, monitoring, and operational complexity.
- **Failure mode:** a team confuses successful scheduling with correct business processing. A task can succeed while its SQL silently omits deletes or mishandles duplicate source keys.

---

# 2. Beginner — Streams and change tracking

## 2.1 What a stream is

A Snowflake stream records an **offset** on a source object and exposes the change data between that offset and the current source version. It does not copy and store a separate physical table of every changed row. When queried, it returns source columns plus metadata columns.

Create a stream on a raw table:

```sql
CREATE OR REPLACE STREAM orders_stream
  ON TABLE raw_orders;

-- Inspect stream configuration and staleness metadata.
DESCRIBE STREAM orders_stream;
SHOW STREAMS LIKE 'ORDERS_STREAM';

-- Inspect pending changes. This is a read, not a durable acknowledgement.
SELECT
  order_id,
  customer_id,
  order_status,
  METADATA$ACTION,
  METADATA$ISUPDATE,
  METADATA$ROW_ID
FROM orders_stream;
```

`CREATE OR REPLACE` is useful in an isolated lab, but replacing a stream resets its offset and can discard the prior pending-change view. Do not use it as a routine recovery step in production without a deliberate backfill/reconciliation plan.

### Standard vs append-only streams

| Stream type | Records exposed | Use when | Limitation |
|---|---|---|---|
| **Standard** (default) | Inserts, deletes, and update changes represented as delete/insert pairs | Maintaining current-state tables or CDC targets | Consumer must interpret change semantics correctly |
| **Append-only** (`APPEND_ONLY = TRUE`) | Insert changes only | Append-only event feeds where updates/deletes are irrelevant | Cannot maintain a correct current-state target if source rows can be updated or deleted |

```sql
CREATE OR REPLACE STREAM orders_stream
  ON TABLE raw_orders;

CREATE OR REPLACE STREAM order_events_append_stream
  ON TABLE raw_order_events
  APPEND_ONLY = TRUE;
```

A stream on a view and streams on external tables have different supported behavior and requirements. This lesson's CDC lab uses a standard stream on a native Snowflake table.

## 2.2 Stream metadata

| Column | Meaning | Important nuance |
|---|---|---|
| `METADATA$ACTION` | `INSERT` or `DELETE` change record | An update is normally represented by a pair of records |
| `METADATA$ISUPDATE` | `TRUE` when the record is part of an update operation | It helps distinguish update-pair records from standalone insert/delete operations |
| `METADATA$ROW_ID` | Identifier used to track a row in the source-object context | It is not a business primary key. It is generally stable for a row, but can change if change tracking is disabled and later re-enabled; do not use it as a substitute for your domain key |

For an update, a standard stream typically exposes a `DELETE` record for the old row and an `INSERT` record for the new row, with `METADATA$ISUPDATE = TRUE` on both. The net change set is between offsets, not a permanent audit log of every intermediate operation. If a row is inserted and then updated within the same offset interval, the stream can expose the resulting net row as an insert rather than an update pair. Use a durable source event log when every intermediate business event must be retained.

## 2.3 A simple example

```sql
CREATE OR REPLACE TABLE raw_orders (
  order_id       NUMBER NOT NULL,
  customer_id    NUMBER,
  order_status   VARCHAR,
  order_total    NUMBER(12,2),
  updated_at     TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE STREAM orders_stream ON TABLE raw_orders;

INSERT INTO raw_orders (order_id, customer_id, order_status, order_total)
VALUES (101, 9001, 'NEW', 125.00);

UPDATE raw_orders
SET order_status = 'PAID',
    order_total = 125.00,
    updated_at = CURRENT_TIMESTAMP()
WHERE order_id = 101;

SELECT order_id, order_status, METADATA$ACTION, METADATA$ISUPDATE, METADATA$ROW_ID
FROM orders_stream
ORDER BY order_id, METADATA$ACTION;
```

Expected behavior: the result reflects the net changes since the stream offset. Exact rows depend on the sequence of committed source changes and the offset boundary; do not assume the stream is a full event audit log.

## 2.4 Transactions and offset advancement

**Key rule:** querying a stream alone does not advance its offset. A DML transaction that consumes stream data advances the offset only when the transaction commits successfully; Snowflake also treats supported CTAS and `COPY INTO <location>` operations that read a stream as consuming operations. If the consuming transaction rolls back, its offset advance is not committed, so the change data remains available for retry. Do not use a CTAS from a stream as a harmless staging read: it can consume and advance the stream.

```text
BEGIN TRANSACTION
      │
      ▼
Read stream snapshot at transaction's start offset
      │
      ▼
INSERT / MERGE / DELETE target using stream data
      │
      ├── COMMIT succeeds ──▶ target changes commit + stream offset advances
      │
      └── ROLLBACK/failure ─▶ target DML rolls back + offset does not advance
```

Within an explicit transaction, stream queries use the stream position at the transaction start. Multiple statements can see the same change set; this is useful when they must be processed together. Avoid running a standalone `SELECT` against a stream and thinking that this acknowledges or consumes the records. Merely inspecting the stream does not commit an offset advance.

### Correctness boundary

A stream and transaction provide a useful atomic boundary for Snowflake DML, but **they do not guarantee exactly-once business processing across external APIs, emails, message brokers, or non-transactional side effects**. Correctness still depends on deterministic transformations, target keys, transaction boundaries, duplicate handling, and recovery design.

---

# 3. Beginner — Tasks and schedules

## 3.1 What a task does

A task executes SQL or calls supported stored procedures. Tasks can be scheduled using an interval or CRON expression, or can be triggered based on conditions such as stream data being available. A newly created task is suspended until resumed.

### Warehouse-based task

Use a named virtual warehouse when you want control over warehouse size, resource isolation, and query execution characteristics.

```sql
CREATE OR REPLACE TASK refresh_small_summary_task
  WAREHOUSE = TRANSFORM_WH
  SCHEDULE = '5 MINUTE'
AS
  MERGE INTO summary_orders AS t
  USING (
    SELECT order_status, COUNT(*) AS order_count
    FROM silver_orders
    GROUP BY order_status
  ) AS s
  ON t.order_status = s.order_status
  WHEN MATCHED THEN UPDATE SET order_count = s.order_count
  WHEN NOT MATCHED THEN INSERT (order_status, order_count)
    VALUES (s.order_status, s.order_count);

ALTER TASK refresh_small_summary_task RESUME;
```

This is a syntax illustration; the target and source tables must exist. For a tiny aggregate this task may be unnecessarily frequent or expensive. A full aggregate refresh pattern is not automatically incremental just because it runs in a task.

### Serverless task

A serverless task does not specify `WAREHOUSE`; Snowflake manages compute for supported task execution. Serverless task sizing and billing differ from a user-managed warehouse. Initial task runs and account configuration can affect whether a task can start; set a sensible task schedule and inspect history before using it for production SLAs.

```sql
CREATE OR REPLACE TASK serverless_maintenance_task
  SCHEDULE = '10 MINUTE'
  USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE = 'XSMALL'
AS
  CALL maintain_small_dimension();
```

The managed initial size is an initial sizing hint for serverless task execution, not a warehouse you can query or resize directly. Verify current task syntax, account support, and privilege requirements before deployment.

## 3.2 Interval and CRON schedules

```sql
-- Every five minutes.
CREATE OR REPLACE TASK every_five_minutes_task
  WAREHOUSE = TRANSFORM_WH
  SCHEDULE = '5 MINUTE'
AS
  CALL process_incremental_batch();

-- Every day at 03:17 in a named time zone.
CREATE OR REPLACE TASK daily_reconcile_task
  WAREHOUSE = TRANSFORM_WH
  SCHEDULE = 'USING CRON 17 3 * * * America/Los_Angeles'
AS
  CALL reconcile_silver_gold();
```

Choose a time zone explicitly for business schedules. CRON schedules are not a promise that a task starts at an exact wall-clock second; queueing, overlapping execution constraints, and runtime can affect observed timing. Avoid choosing a schedule so tight that one run regularly overlaps or nearly consumes the entire interval.

## 3.3 Task privileges and ownership

A role creating a task needs `CREATE TASK` on the schema and `USAGE` on the database/schema; a warehouse-based task also needs `USAGE` on its warehouse. The task owner needs `EXECUTE TASK` at the account level to run any task and all privileges required by the SQL/procedure. A serverless task additionally requires `EXECUTE MANAGED TASK` at the account level and omits `WAREHOUSE`. A role with `OPERATE` can resume/suspend a task but is not automatically authorized to read or modify every object that the task touches. Use a dedicated least-privilege owner role and verify current access-control requirements before production use.

---

# 4. Intermediate — CDC with streams and tasks

## 4.1 Design the current-state target

For a current-state silver table, the business key must be unique in the source change set. A `MERGE` is only deterministic when the source provides at most one effective row per target key for the merge operation. If upstream ingestion can deliver multiple changes for the same key in one batch, deduplicate or reduce the stream changes to a deterministic final state before merging.

The example below uses an explicit tombstone strategy: deletes are represented in silver as `IS_DELETED = TRUE` rather than physically deleting the target row. Tombstones make delete propagation observable and simplify audit/reconciliation. If the business requires physical deletes, change the merge logic deliberately and retain another reliable audit/replay source.

```sql
CREATE OR REPLACE TABLE raw_orders (
  order_id       NUMBER NOT NULL,
  customer_id    NUMBER,
  order_status   VARCHAR,
  order_total    NUMBER(12,2),
  source_seq     NUMBER NOT NULL,
  updated_at     TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE silver_orders (
  order_id       NUMBER NOT NULL,
  customer_id    NUMBER,
  order_status   VARCHAR,
  order_total    NUMBER(12,2),
  source_seq     NUMBER NOT NULL,
  updated_at     TIMESTAMP_NTZ,
  is_deleted     BOOLEAN DEFAULT FALSE,
  applied_at     TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE STREAM raw_orders_stream ON TABLE raw_orders;
```

## 4.2 Consume the stream with an idempotent MERGE

A basic CDC task can merge update/insert images and mark deletes. The example below assumes the source has a reliable, monotonically increasing `SOURCE_SEQ` per business key and that each update increments it. The reducer selects the highest sequence and prefers the `INSERT` image when the old and new images of one update are both present. If the source does not provide a reliable sequence, do not substitute a timestamp or `METADATA$ROW_ID` as event ordering; define and test a source-specific reducer instead.

```sql
CREATE OR REPLACE TASK apply_raw_orders_to_silver
  WAREHOUSE = TRANSFORM_WH
  SCHEDULE = '1 MINUTE'
AS
MERGE INTO silver_orders AS tgt
USING (
  SELECT
    order_id,
    customer_id,
    order_status,
    order_total,
    source_seq,
    updated_at,
    METADATA$ACTION AS change_action,
    METADATA$ISUPDATE AS is_update
  FROM raw_orders_stream
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY source_seq DESC,
             IFF(METADATA$ACTION = 'INSERT', 1, 0) DESC
  ) = 1
) AS src
ON tgt.order_id = src.order_id
WHEN MATCHED AND src.source_seq >= tgt.source_seq
  AND src.change_action = 'DELETE' AND NOT src.is_update
  THEN UPDATE SET
    tgt.source_seq = src.source_seq,
    tgt.is_deleted = TRUE,
    tgt.updated_at = src.updated_at,
    tgt.applied_at = CURRENT_TIMESTAMP()
WHEN MATCHED AND src.source_seq >= tgt.source_seq
  AND src.change_action = 'INSERT'
  THEN UPDATE SET
    tgt.customer_id = src.customer_id,
    tgt.order_status = src.order_status,
    tgt.order_total = src.order_total,
    tgt.source_seq = src.source_seq,
    tgt.updated_at = src.updated_at,
    tgt.is_deleted = FALSE,
    tgt.applied_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED AND src.change_action = 'INSERT'
  THEN INSERT (order_id, customer_id, order_status, order_total, source_seq, updated_at, is_deleted, applied_at)
  VALUES (src.order_id, src.customer_id, src.order_status, src.order_total, src.source_seq, src.updated_at, FALSE, CURRENT_TIMESTAMP())
WHEN NOT MATCHED AND src.change_action = 'DELETE' AND NOT src.is_update
  THEN INSERT (order_id, customer_id, order_status, order_total, source_seq, updated_at, is_deleted, applied_at)
  VALUES (src.order_id, src.customer_id, src.order_status, src.order_total, src.source_seq, src.updated_at, TRUE, CURRENT_TIMESTAMP());
```

**Important review point:** SQL above demonstrates the shape of a stream-consuming merge, but a production CDC algorithm must explicitly define how it handles multiple updates, update pairs, and delete/insert records for the same key within one stream offset. The safest production implementation should derive a final source state using a trustworthy sequence column or source CDC offset, and test all operation permutations. Do not blindly copy a timestamp/row-id tie-breaker as a universal event-ordering guarantee. A robust alternative is to stage the stream's full change set within one transaction, derive a deterministic latest state, then merge that result.

### Recommended robust pattern for complex CDC

When source events include a monotonic version or CDC sequence, use that sequence rather than a wall-clock timestamp to select the final state. Preserve delete intent before reducing update pairs. The following is an **interactive-session pattern**, not a task body: the staging table is created without reading the stream, then stream-consuming DML and target DML run in one explicit transaction. A CTAS such as `CREATE TEMP TABLE ... AS SELECT * FROM raw_orders_stream` is unsafe here because CTAS itself can consume the stream and commit the offset before the target merge succeeds.

```sql
-- Assumes raw_orders_stream exposes these source columns and metadata.
-- Create the empty staging table without selecting from the stream.
CREATE TEMP TABLE batch_orders_changes (
  order_id NUMBER,
  customer_id NUMBER,
  order_status VARCHAR,
  order_total NUMBER(12,2),
  source_seq NUMBER,
  updated_at TIMESTAMP_NTZ,
  change_action VARCHAR,
  is_update BOOLEAN,
  source_row_id VARCHAR
);

BEGIN TRANSACTION;

-- Reuse the temporary staging table safely: each transaction processes one batch.
DELETE FROM batch_orders_changes;

INSERT INTO batch_orders_changes (
  order_id, customer_id, order_status, order_total, source_seq,
  updated_at, change_action, is_update, source_row_id
)
SELECT
  order_id, customer_id, order_status, order_total, source_seq,
  updated_at, METADATA$ACTION, METADATA$ISUPDATE, METADATA$ROW_ID
FROM raw_orders_stream;

MERGE INTO silver_orders AS tgt
USING (
  SELECT order_id, customer_id, order_status, order_total, source_seq,
         updated_at, change_action, is_update
  FROM batch_orders_changes
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY source_seq DESC, IFF(change_action = 'INSERT', 1, 0) DESC
  ) = 1
) AS src
ON tgt.order_id = src.order_id
WHEN MATCHED AND src.source_seq >= tgt.source_seq
  AND src.change_action = 'DELETE' AND NOT src.is_update
  THEN UPDATE SET source_seq = src.source_seq, is_deleted = TRUE,
                  updated_at = src.updated_at, applied_at = CURRENT_TIMESTAMP()
WHEN MATCHED AND src.source_seq >= tgt.source_seq AND src.change_action = 'INSERT'
  THEN UPDATE SET customer_id = src.customer_id,
                  order_status = src.order_status,
                  order_total = src.order_total,
                  source_seq = src.source_seq,
                  updated_at = src.updated_at,
                  is_deleted = FALSE,
                  applied_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED AND src.change_action = 'INSERT'
  THEN INSERT (order_id, customer_id, order_status, order_total, source_seq, updated_at, is_deleted, applied_at)
       VALUES (src.order_id, src.customer_id, src.order_status, src.order_total, src.source_seq, src.updated_at, FALSE, CURRENT_TIMESTAMP())
WHEN NOT MATCHED AND src.change_action = 'DELETE' AND NOT src.is_update
  THEN INSERT (order_id, customer_id, order_status, order_total, source_seq, updated_at, is_deleted, applied_at)
       VALUES (src.order_id, src.customer_id, src.order_status, src.order_total, src.source_seq, src.updated_at, TRUE, CURRENT_TIMESTAMP());

-- Commit only after the target MERGE succeeds. If any statement fails, ROLLBACK.
COMMIT;
```

The staging table is created before the transaction without reading the stream; the `INSERT ... SELECT FROM stream` and target `MERGE` then share one transaction. If the merge fails, issue `ROLLBACK` so neither target DML nor the stream offset advance is committed. For a task, put this multi-statement logic in a tested stored procedure and have the task call it, or use one carefully designed stream-consuming `MERGE` as shown above. Do not run DDL inside the transaction and assume it rolls back with the DML. A stream can have multiple independent consumers only when each has its own stream offset; separate consumers should normally use separate streams.

## 4.3 Make the CDC task easier to reason about

For a simple lab source with one change per key per batch, the following `MERGE` pattern is easier to validate. It uses the stream to update current-state rows and handles explicit deletes. Before production, add a deterministic source sequence and a tested reducer for repeated changes per key.

```sql
CREATE OR REPLACE TASK apply_orders_cdc
  WAREHOUSE = TRANSFORM_WH
  SCHEDULE = '1 MINUTE'
AS
MERGE INTO silver_orders t
USING (
  SELECT order_id, customer_id, order_status, order_total, source_seq,
         updated_at, METADATA$ACTION AS action_name,
         METADATA$ISUPDATE AS is_update
  FROM raw_orders_stream
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY source_seq DESC, IFF(METADATA$ACTION = 'INSERT', 1, 0) DESC
  ) = 1
) s
ON t.order_id = s.order_id
WHEN MATCHED AND s.source_seq >= t.source_seq
  AND s.action_name = 'DELETE' AND NOT s.is_update
  THEN UPDATE SET source_seq = s.source_seq, is_deleted = TRUE,
                  updated_at = s.updated_at, applied_at = CURRENT_TIMESTAMP()
WHEN MATCHED AND s.source_seq >= t.source_seq AND s.action_name = 'INSERT'
  THEN UPDATE SET customer_id = s.customer_id,
                  order_status = s.order_status,
                  order_total = s.order_total,
                  source_seq = s.source_seq,
                  updated_at = s.updated_at,
                  is_deleted = FALSE,
                  applied_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED AND s.action_name = 'INSERT'
  THEN INSERT (order_id, customer_id, order_status, order_total, source_seq, updated_at, is_deleted, applied_at)
       VALUES (s.order_id, s.customer_id, s.order_status, s.order_total, s.source_seq, s.updated_at, FALSE, CURRENT_TIMESTAMP())
WHEN NOT MATCHED AND s.action_name = 'DELETE' AND NOT s.is_update
  THEN INSERT (order_id, customer_id, order_status, order_total, source_seq, updated_at, is_deleted, applied_at)
       VALUES (s.order_id, s.customer_id, s.order_status, s.order_total, s.source_seq, s.updated_at, TRUE, CURRENT_TIMESTAMP());
```

This simplified form still assumes the reducer's ordering matches the source's intended semantics. If your source cannot provide a reliable sequence, do not claim that this example resolves every multi-change-per-key case. Use a replayable raw event table, preserve source ordering metadata, and test carefully.

This is an alternative example to the earlier `apply_raw_orders_to_silver` task, not an additional consumer to run concurrently. Use one consumer per stream offset; if two independent pipelines need the same source changes, create a separate stream for each.

Resume the task only after the stream and target objects are created:

```sql
ALTER TASK apply_orders_cdc RESUME;
```

Verify:

```sql
SELECT * FROM silver_orders ORDER BY order_id;
SELECT SYSTEM$STREAM_HAS_DATA('RAW_ORDERS_STREAM');
```

`SYSTEM$STREAM_HAS_DATA` is useful for deciding whether a stream-triggered task should run. It is a signal, not a replacement for error handling. The task's DML still needs to commit for changes to be applied and the stream offset to advance.

## 4.4 Insert, update, delete walkthrough

```sql
INSERT INTO raw_orders (order_id, customer_id, order_status, order_total, source_seq)
VALUES (1001, 501, 'NEW', 49.95, 1),
       (1002, 502, 'NEW', 79.50, 1);

-- Run this as a later batch and increment the per-key sequence.
UPDATE raw_orders
SET order_status = 'PAID', order_total = 54.95,
    source_seq = 2, updated_at = CURRENT_TIMESTAMP()
WHERE order_id = 1001;

-- Delete in a separate batch after the prior change is consumed.
DELETE FROM raw_orders WHERE order_id = 1002;
```

Wait for the task run or execute the task manually in the lab. Check both raw and silver. Expected business state: order 1001 reflects the latest paid state; order 1002 is marked deleted if the chosen tombstone pattern is used. Exact stream records depend on offset boundaries and whether multiple operations occur before consumption.

### Idempotency and duplicates

- A committed `MERGE` keyed on a stable business key can be idempotent when repeated input represents the same final state.
- It does not deduplicate business events automatically. Duplicate event rows, out-of-order events, and multiple source versions still need explicit rules.
- If a task fails before commit, the transaction can be retried with the stream changes still available. If a task commits and then an external side effect fails, the external side effect requires its own idempotency key/outbox pattern.
- Do not use `METADATA$ROW_ID` as a universal event ID or business key.

---

# 5. Intermediate — Task graphs (DAGs)

A task graph coordinates multiple steps. The root task defines the schedule. Child tasks use `AFTER` to depend on parent tasks; siblings can run in parallel when dependencies permit. A task with multiple parents waits for its required parents. A finalizer task can perform cleanup or publish run status after the graph completes, including failed paths.

```text
                    ┌───────────────┐
                    │ ROOT: ingest  │  (schedule / trigger)
                    └───────┬───────┘
                            │ AFTER
                 ┌──────────┴──────────┐
                 ▼                     ▼
        ┌────────────────┐    ┌────────────────┐
        │ validate batch │    │ quality checks │
        └───────┬────────┘    └───────┬────────┘
                └──────────┬──────────┘
                           ▼
                  ┌────────────────┐
                  │ apply MERGE    │
                  └───────┬────────┘
                          ▼
                  ┌────────────────┐
                  │ FINALIZER      │ (status / cleanup)
                  └────────────────┘
```

## 5.1 Example graph

```sql
CREATE OR REPLACE TASK orders_root
  WAREHOUSE = TRANSFORM_WH
  SCHEDULE = '5 MINUTE'
  TASK_AUTO_RETRY_ATTEMPTS = 2
  SUSPEND_TASK_AFTER_NUM_FAILURES = 3
AS
  CALL prepare_orders_batch();

CREATE OR REPLACE TASK orders_validate
  WAREHOUSE = TRANSFORM_WH
  AFTER orders_root
AS
  CALL validate_orders_batch();

CREATE OR REPLACE TASK orders_quality
  WAREHOUSE = TRANSFORM_WH
  AFTER orders_root
AS
  CALL run_orders_quality_checks();

CREATE OR REPLACE TASK orders_apply
  WAREHOUSE = TRANSFORM_WH
  AFTER orders_validate, orders_quality
AS
  CALL apply_orders_batch();

-- Finalizer syntax and support can vary with task graph features/account rollout.
-- Verify current CREATE TASK ... FINALIZE syntax before using in production.
CREATE OR REPLACE TASK orders_finalizer
  WAREHOUSE = TRANSFORM_WH
  FINALIZE = orders_root
AS
  CALL publish_orders_run_status();
```

Enable the graph and its dependents in one operation:

```sql
SELECT SYSTEM$TASK_DEPENDENTS_ENABLE('ORDERS_ROOT');
```

Alternatively, resume each child and finalizer task first, then resume the root. Do not resume the root before dependents are enabled if you need the first scheduled run to execute the complete graph.

Creating a task does not automatically start it. For task graphs, follow current Snowflake guidance on enabling root, child, and finalizer tasks; validate dependencies in a test schema before relying on them.

## 5.2 Retries and failure semantics

Task graphs support retry configuration for eligible tasks/graphs, including automatic retry attempts for failed graph runs in supported configurations. Configure retries only after the operation is safe to repeat. Retries are not a substitute for idempotent DML. Avoid retrying irreversible external side effects unless the external endpoint supports idempotency keys.

Use `SYSTEM$STREAM_HAS_DATA('STREAM_NAME')` in a task `WHEN` condition to avoid unnecessary work when no changes are pending. The function can return `TRUE` when no rows are ultimately returned (a false positive), so the task must tolerate a no-op run; do not treat it as a correctness check or a replacement for monitoring actual task outcomes and stream age. Triggered tasks can reduce polling latency, but task execution still consumes compute and can incur per-run overhead.

---

# 6. Intermediate — Dynamic tables

## 6.1 Declarative transformation

A dynamic table stores the result of a `SELECT` and Snowflake manages background refresh to keep it within a **target lag**. The user describes *what* the result should be, not a custom `MERGE` procedure for every change.

```sql
CREATE OR REPLACE DYNAMIC TABLE gold_order_status_summary
  TARGET_LAG = '5 minutes'
  WAREHOUSE = TRANSFORM_WH
  REFRESH_MODE = INCREMENTAL
AS
SELECT
  order_status,
  COUNT(*) AS order_count,
  SUM(order_total) AS total_order_value
FROM silver_orders
WHERE is_deleted = FALSE
GROUP BY order_status;
```

The five-minute value is a **freshness target, not a guaranteed refresh interval or hard SLA**. Actual lag can exceed the target if refreshes take too long, upstream changes are large, the warehouse is undersized, or the pipeline is constrained. Monitor actual lag and refresh history.

### Target lag in dependency chains

For a chain of dynamic tables, Snowflake coordinates upstream/downstream refresh ordering. A downstream table's target lag must be compatible with upstream dependencies; do not make a downstream result promise to be fresher than the data it depends on. Intermediate tables can use `TARGET_LAG = DOWNSTREAM` when they should refresh only when needed by a downstream consumer. A leaf table that serves dashboards should have an explicit target lag.

## 6.2 Refresh modes

| Mode | Behavior | Best fit | Risk / trade-off |
|---|---|---|---|
| `INCREMENTAL` | Processes changes using supported incremental refresh logic | Compatible query shapes with relatively small changes | Creation fails if definition is unsupported; incremental work can still be expensive |
| `FULL` | Rebuilds the full result on each refresh | Unsupported incremental query shapes or high change volume | Can consume much more compute on large data |
| `ADAPTIVE` | Uses incremental refresh and can reinitialize when Snowflake detects bulk changes make it preferable | Mixed incremental and occasional bulk-reload patterns, where supported | Requires compatible query constructs; understand reinitialization cost |
| `AUTO` | Snowflake resolves a mode at creation time | Exploration/prototyping | Verify the resolved mode; it does not continuously switch modes based on every refresh |

For production, set `REFRESH_MODE` explicitly when predictable behavior is important, and verify the actual mode with `SHOW DYNAMIC TABLES`. Refresh-mode support and constraints can evolve; consult the current mode documentation for the SQL operators in your definition.

```sql
SHOW DYNAMIC TABLES LIKE 'GOLD_ORDER_STATUS_SUMMARY';

SELECT *
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(
  NAME => 'GOLD_ORDER_STATUS_SUMMARY',
  RESULT_LIMIT => 20
));
```

The exact Information Schema function availability and arguments depend on the account's Snowflake version and context. The table function is generally the most direct way to inspect recent refreshes; use the current reference linked below.

## 6.3 Compare dynamic tables with task-based gold

**Dynamic table option:** define the gold query once; Snowflake schedules refreshes to meet the target lag.

**Task-based option:** define a gold table and task/procedure that updates it. This offers control over custom logic, branching, error handling, and explicit merge semantics, but you own correctness and scheduling.

Example task-based summary refresh (simple full recomputation; for large data this can be expensive):

```sql
CREATE OR REPLACE TABLE gold_order_status_task AS
SELECT order_status, COUNT(*) AS order_count, SUM(order_total) AS total_order_value
FROM silver_orders
WHERE is_deleted = FALSE
GROUP BY order_status;

CREATE OR REPLACE TASK refresh_gold_order_status_task
  WAREHOUSE = TRANSFORM_WH
  SCHEDULE = '5 MINUTE'
AS
  CREATE OR REPLACE TABLE gold_order_status_task AS
  SELECT order_status, COUNT(*) AS order_count, SUM(order_total) AS total_order_value
  FROM silver_orders
  WHERE is_deleted = FALSE
  GROUP BY order_status;
```

This is a comparison pattern, not an automatic recommendation. Recreating a table can affect grants, dependencies, and consumers depending on the exact DDL. For a production task-based pipeline, prefer a deliberate `MERGE`/transactional pattern or a stable table-refresh design with known downstream dependencies. Do not compare costs from one run without controlling data volume, warehouse size, cache state, and frequency.

---

# 7. Choosing between streams/tasks, dynamic tables, materialized views, and dbt

| Tool | Best at | You own | Cost / operational considerations | Avoid when |
|---|---|---|---|---|
| **Streams + tasks** | Imperative CDC, deletes, custom branching, stored procedures, external side-effect coordination | DML logic, deduplication, transaction design, retries, task graph and monitoring | Warehouse/serverless task compute, task-run overhead, storage retention implications for streams | You only need a straightforward declarative query result and do not need custom processing |
| **Dynamic tables** | Declarative multi-step ELT with managed refresh and freshness goals | Query definition, target lag, refresh-mode choice, warehouse, observability | Refresh compute; full refresh or frequent short lag can be costly | Logic depends on unsupported query patterns or needs explicit imperative orchestration that is clearer in tasks |
| **Materialized views** | Speeding up repeated eligible query patterns over a base table | View definition and performance/cost validation | Automatic maintenance has storage/compute implications; SQL eligibility and limits apply | You need broad multi-step pipeline orchestration or transformations outside materialized-view support |
| **dbt** | Version-controlled SQL transformations, tests, documentation, environments, and deployment workflow | Project, dependency graph, tests, deployment/orchestration configuration | External runner/orchestrator plus Snowflake compute; dbt itself does not replace Snowflake's storage engine | You expect dbt alone to provide continuous CDC offsets or a Snowflake-managed dynamic-table refresh |

A common architecture combines them: streams/tasks for complex source CDC, dynamic tables for downstream declarative transformations, and dbt or Airflow/Dagster for cross-system dependencies and deployment workflows. Avoid overlapping orchestrators that independently schedule the same work without a clear ownership boundary.

---

# 8. Advanced — Stream staleness and recovery

## 8.1 Why a stream becomes stale

A stream depends on source-table history around its offset. If the offset falls outside the source object's retained historical data, the stream becomes stale and its unconsumed change data can no longer be relied upon. Snowflake can extend retention for streams within configured limits, which can add storage cost. Shared objects and object recreation have special limitations. Use `DESCRIBE STREAM` / `SHOW STREAMS` and inspect `STALE` and `STALE_AFTER` rather than assuming a stream is safe because a query returned no rows.

```sql
DESCRIBE STREAM raw_orders_stream;
SHOW STREAMS LIKE 'RAW_ORDERS_STREAM';
```

Calling `SYSTEM$STREAM_HAS_DATA` can help avoid staleness in the specific case where the stream is empty and the function returns `FALSE`; do not treat this as a blanket substitute for consuming changes within the retention window.

## 8.2 Safe recovery strategy

If a stream is stale, recreating it restores the ability to track **future** changes, but it does not recover the missing historical delta. Safe recovery generally requires:

1. Identify the last successfully applied watermark/version in the target and the interval at risk.
2. Determine whether the source table or an immutable raw/CDC archive can be re-read to rebuild that interval.
3. Reconcile or backfill silver from a trusted source snapshot/event log.
4. Recreate the stream at a known point only after defining how changes during the recovery window will be captured.
5. Validate row counts, key-level state, delete semantics, and duplicate behavior before resuming normal processing.

Do not blindly `CREATE OR REPLACE STREAM` and continue: this can hide a gap. If the source was recreated with `CREATE OR REPLACE TABLE`, the new object is not necessarily the same source object to which the original stream was attached.

### Safe lab alternative

Do not try to force a stream stale by suspending a task and waiting days or by changing retention on a valuable schema. Staleness timing depends on retention parameters and account behavior, so the result may not be deterministic in a short lab. Instead, inspect `STALE_AFTER`, document the retention window, and rehearse a recovery plan on a disposable table using a deliberately recreated source object in an isolated schema only if you understand the destructive implications. The reliable learning objective is recovery planning, not forcing a specific stale timestamp on demand.

---

# 9. Advanced — Monitoring and alerting

## 9.1 Task history

`TASK_HISTORY` returns task execution history, including failures and scheduled executions in the supported time window. Query the Information Schema table function in the database/schema context that contains the task, or use the corresponding account usage views for broader history where appropriate.

```sql
SELECT
  NAME,
  STATE,
  SCHEDULED_TIME,
  COMPLETED_TIME,
  ERROR_CODE,
  ERROR_MESSAGE,
  QUERY_ID
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
  SCHEDULED_TIME_RANGE_START => DATEADD('hour', -24, CURRENT_TIMESTAMP()),
  RESULT_LIMIT => 100
))
WHERE STATE = 'FAILED'
ORDER BY SCHEDULED_TIME DESC;
```

If the task name is known, pass `TASK_NAME => 'APPLY_ORDERS_CDC'` to narrow the result. The table function's history window is limited; use account usage/organization views when a longer retained history is required and the role has access.

## 9.2 Dynamic table refresh history

```sql
SELECT
  NAME,
  STATE,
  DATA_TIMESTAMP,
  REFRESH_START_TIME,
  REFRESH_END_TIME,
  QUERY_ID,
  ERROR_CODE,
  ERROR_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(
  NAME => 'GOLD_ORDER_STATUS_SUMMARY',
  RESULT_LIMIT => 100
))
ORDER BY REFRESH_START_TIME DESC;
```

Use the column names supported by the current function version; if your account returns a different schema, inspect the official reference and select the available columns. Track failed refreshes, duration, skipped refreshes, actual lag, and mode—not only whether the dynamic table exists.

## 9.3 Operational signals

| Signal | Why it matters | Typical response |
|---|---|---|
| Task failure count / consecutive failures | CDC may be falling behind | Inspect error, query ID, privileges, and source schema; retry only after safe remediation |
| Stream `STALE_AFTER` approaching | Pending change data may become inaccessible | Alert owner; ensure consumption or prepare reconciliation/backfill |
| Dynamic table lag above target | Consumers may see stale results | Check refresh duration, warehouse size, source change volume, query shape, and dependencies |
| Refresh mode unexpectedly `FULL` | Full scans may create cost spikes | Inspect `SHOW DYNAMIC TABLES` and `refresh_mode_reason`; revise query or explicitly choose mode |
| Unexpectedly empty stream | Could mean no changes, already consumed changes, or staleness/recreated source | Check source writes, offset, `STALE`, task history, and target reconciliation |
| Long-running/overlapping tasks | Queueing and delayed freshness | Reduce unnecessary work, optimize SQL, adjust schedule or compute, and make retries idempotent |

## 9.4 Alerts and notification integrations

Snowflake alerts can evaluate conditions on a schedule; notification integrations can send supported notifications through configured channels. Exact syntax and required privileges depend on the notification destination and current account setup. Keep the lab's alert concept simple and separate alert definition from the notification integration.

Illustrative alert for failed task runs, after validating the history query and permissions in your account:

```sql
-- Replace the query with a tested predicate for your account's history view.
CREATE OR REPLACE ALERT failed_task_alert
  WAREHOUSE = TRANSFORM_WH
  SCHEDULE = '5 MINUTE'
  IF (EXISTS (
    SELECT 1
    FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
      SCHEDULED_TIME_RANGE_START => DATEADD('minute', -10, CURRENT_TIMESTAMP()),
      RESULT_LIMIT => 100
    ))
    WHERE STATE = 'FAILED'
      AND NAME = 'APPLY_ORDERS_CDC'
  ))
  THEN
    CALL SYSTEM$SEND_EMAIL(
      'OPS_EMAIL_INTEGRATION',
      'data-platform-ops@example.com',
      'Snowflake task failure detected',
      'Review TASK_HISTORY and the failing task QUERY_ID.'
    );
```

This is a template, not a guaranteed drop-in statement: `SYSTEM$SEND_EMAIL` requires a configured email notification integration and authorized recipients, and alert syntax/privileges should be checked against current Snowflake documentation. Do not use placeholder email addresses or integration names in production. After creating an alert, resume it and test the delivery path with a non-sensitive test message.

Event tables are primarily an observability mechanism for supported telemetry/logging patterns; they do not replace task history, dynamic table refresh history, or stream health checks. Treat event tables as awareness-level context for this topic.

---

# 10. Cost and production engineering

## 10.1 Warehouse selection

- Use a dedicated, appropriately sized transformation warehouse when you need predictable isolation and direct control.
- Use serverless tasks when their managed execution model fits the workload and its pricing model is understood.
- For dynamic tables, the `WAREHOUSE` parameter runs scheduled refreshes; initializations/reinitializations can be more expensive. Where supported, `INITIALIZATION_WAREHOUSE` can separate expensive initial builds from steady-state incremental refreshes.
- Avoid running tiny tasks every minute on a large warehouse if the business only needs a 15-minute freshness window.

## 10.2 Target lag is a freshness goal

A shorter target lag can cause more frequent refresh work and higher cost, but it does not guarantee the target will always be met. Set the longest lag the business can tolerate, then tighten it only when measurement shows the need. For dynamic table chains, use `DOWNSTREAM` for intermediate tables that do not need an independent freshness target; give consumer-facing leaf tables explicit lag targets.

## 10.3 Incremental is not always cheaper

Incremental refresh is often effective when changes are small and query operators are supported, but it can still scan large portions of source tables. Full refresh can be appropriate for high change volume or unsupported query patterns. Compare actual refresh history and compute use for representative periods before choosing a mode.

## 10.4 Transaction and recovery controls

- Keep stream-consuming target DML in a transaction boundary that commits only when the intended change application succeeds.
- Use stable business keys and deterministic event ordering.
- Record source watermarks or CDC sequence IDs where available.
- Make merge logic idempotent and build reconciliation queries for counts, deletes, and key-level mismatches.
- Use bounded retries and alerts; do not hide permanent failures by retrying indefinitely.
- Do not couple a committed stream consumption to an unprotected external side effect.

## 10.5 External orchestration boundaries

Airflow, Dagster, and dbt can call Snowflake and coordinate work across systems. Decide which system owns scheduling, retries, dependency state, and deployment. A practical boundary is often:

- Snowflake tasks for small, Snowflake-local routines and task graphs.
- Dynamic tables for declarative transformations with a managed freshness goal.
- Airflow/Dagster for cross-system DAGs and dependencies outside Snowflake.
- dbt for versioned SQL models, tests, documentation, and deployment practices; pair with a scheduler for execution.

Do not schedule the same pipeline independently in both Snowflake and an external orchestrator unless the overlap is intentional and safe.

---

# 11. Hands-on lab — `experiments/05_streams_tasks/`

## Lab objective

Build a disposable raw → stream → task/MERGE → silver pipeline, verify inserts/updates/deletes, create a five-minute-lag gold dynamic table, compare it with a task-based result, inspect monitoring history, and rehearse safe staleness recovery.

## Prerequisites and safety

- Use a non-production database/schema and a small warehouse such as `XSMALL` where available.
- Have privileges to create/use the lab database/schema, tables, streams, tasks, and dynamic tables; `USAGE` on the selected warehouse; account-level `EXECUTE TASK` for task execution; and permission to create/resume alerts if doing the optional alert section. A serverless-task variant additionally requires account-level `EXECUTE MANAGED TASK`.
- For serverless tasks or notifications, account/role setup may require additional privileges. If not available, skip those portions rather than embedding credentials or weakening access controls.
- Start with a small dataset (tens or hundreds of rows). The lesson is about semantics, not stress testing.
- Never lower retention or replace source objects in a valuable schema to force a stale stream.
- The lab DDL is intentionally fail-fast: if the named database, schema, warehouse, or lab objects already exist, stop and choose a unique disposable name or clean up only objects you created. Do not change `CREATE` to `CREATE OR REPLACE` just to make reruns pass; `OR REPLACE` can destroy existing data or reset stream offsets.
- If using an approved existing warehouse, skip the warehouse creation and warehouse-drop statements; never drop a shared warehouse.

## Step 1 — Create the sandbox objects

```sql
-- Choose a unique disposable name. These CREATE statements intentionally fail
-- if the database/schema already exists; do not silently reuse existing objects.
CREATE DATABASE SNOWFLAKE_TOPIC05_LAB;
CREATE SCHEMA SNOWFLAKE_TOPIC05_LAB.ELT;
USE DATABASE SNOWFLAKE_TOPIC05_LAB;
USE SCHEMA ELT;

CREATE WAREHOUSE TOPIC05_WH
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

CREATE TABLE RAW_ORDERS (
  ORDER_ID NUMBER NOT NULL,
  CUSTOMER_ID NUMBER,
  ORDER_STATUS VARCHAR,
  ORDER_TOTAL NUMBER(12,2),
  SOURCE_SEQ NUMBER NOT NULL,
  UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE SILVER_ORDERS (
  ORDER_ID NUMBER NOT NULL,
  CUSTOMER_ID NUMBER,
  ORDER_STATUS VARCHAR,
  ORDER_TOTAL NUMBER(12,2),
  SOURCE_SEQ NUMBER NOT NULL,
  UPDATED_AT TIMESTAMP_NTZ,
  IS_DELETED BOOLEAN DEFAULT FALSE,
  APPLIED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE STREAM RAW_ORDERS_STREAM ON TABLE RAW_ORDERS;
```

If you lack permission to create a warehouse, use an approved existing warehouse and remove the warehouse DDL. Object names are lab-specific; do not execute the cleanup commands against a shared schema.

## Step 2 — Insert sample data and inspect the stream

```sql
INSERT INTO RAW_ORDERS (ORDER_ID, CUSTOMER_ID, ORDER_STATUS, ORDER_TOTAL, SOURCE_SEQ)
VALUES (1001, 501, 'NEW', 49.95, 1),
       (1002, 502, 'NEW', 79.50, 1),
       (1003, 503, 'NEW', 25.00, 1);

SELECT ORDER_ID, SOURCE_SEQ, METADATA$ACTION, METADATA$ISUPDATE, METADATA$ROW_ID
FROM RAW_ORDERS_STREAM
ORDER BY ORDER_ID;
```

Expected: insert change records are visible. The query alone does not acknowledge the changes. Keep the stream pending for the next step.

## Step 3 — Create a CDC task

For this controlled lab, each `ORDER_ID` receives one logical change between task runs and `SOURCE_SEQ` increases for each new row version. The delete carries the last source row version, and a later reinsert must use a greater sequence rather than reusing an old version. The merge logic can then choose the highest version for each key. In real pipelines, use the actual source CDC sequence and test update-pair/delete behavior against the source's contract.

```sql
CREATE TASK APPLY_RAW_ORDERS_TO_SILVER
  WAREHOUSE = TOPIC05_WH
  SCHEDULE = '1 MINUTE'
AS
MERGE INTO SILVER_ORDERS AS T
USING (
  SELECT ORDER_ID, CUSTOMER_ID, ORDER_STATUS, ORDER_TOTAL, SOURCE_SEQ,
         UPDATED_AT, METADATA$ACTION AS ACTION_NAME,
         METADATA$ISUPDATE AS IS_UPDATE
  FROM RAW_ORDERS_STREAM
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY ORDER_ID
    ORDER BY SOURCE_SEQ DESC,
             IFF(METADATA$ACTION = 'INSERT', 1, 0) DESC
  ) = 1
) AS S
ON T.ORDER_ID = S.ORDER_ID
WHEN MATCHED AND S.ACTION_NAME = 'DELETE' AND NOT S.IS_UPDATE
  THEN UPDATE SET T.IS_DELETED = TRUE, T.SOURCE_SEQ = S.SOURCE_SEQ,
                  T.UPDATED_AT = S.UPDATED_AT, T.APPLIED_AT = CURRENT_TIMESTAMP()
WHEN MATCHED AND S.ACTION_NAME = 'INSERT'
  THEN UPDATE SET T.CUSTOMER_ID = S.CUSTOMER_ID,
                  T.ORDER_STATUS = S.ORDER_STATUS,
                  T.ORDER_TOTAL = S.ORDER_TOTAL,
                  T.SOURCE_SEQ = S.SOURCE_SEQ,
                  T.UPDATED_AT = S.UPDATED_AT,
                  T.IS_DELETED = FALSE,
                  T.APPLIED_AT = CURRENT_TIMESTAMP()
WHEN NOT MATCHED AND S.ACTION_NAME = 'INSERT'
  THEN INSERT (ORDER_ID, CUSTOMER_ID, ORDER_STATUS, ORDER_TOTAL, SOURCE_SEQ, UPDATED_AT, IS_DELETED, APPLIED_AT)
       VALUES (S.ORDER_ID, S.CUSTOMER_ID, S.ORDER_STATUS, S.ORDER_TOTAL, S.SOURCE_SEQ, S.UPDATED_AT, FALSE, CURRENT_TIMESTAMP())
WHEN NOT MATCHED AND S.ACTION_NAME = 'DELETE' AND NOT S.IS_UPDATE
  THEN INSERT (ORDER_ID, CUSTOMER_ID, ORDER_STATUS, ORDER_TOTAL, SOURCE_SEQ, UPDATED_AT, IS_DELETED, APPLIED_AT)
       VALUES (S.ORDER_ID, S.CUSTOMER_ID, S.ORDER_STATUS, S.ORDER_TOTAL, S.SOURCE_SEQ, S.UPDATED_AT, TRUE, CURRENT_TIMESTAMP());

ALTER TASK APPLY_RAW_ORDERS_TO_SILVER RESUME;
```

This lab uses a **scheduled** task, so it intentionally has `SCHEDULE` and no `WHEN` clause. It can run a no-op merge when no rows are pending, so measure whether the simple one-minute schedule is appropriate. If you want event-driven behavior instead, use the separate triggered-task form below: Snowflake's triggered-task syntax uses `WHEN` and does **not** include `SCHEDULE`.

```sql
-- Alternative only: create this instead of the scheduled task above.
CREATE TASK APPLY_RAW_ORDERS_TO_SILVER_TRIGGERED
  WAREHOUSE = TOPIC05_WH
  WHEN SYSTEM$STREAM_HAS_DATA('RAW_ORDERS_STREAM')
AS
  MERGE INTO SILVER_ORDERS AS T
  USING (
    SELECT ORDER_ID, CUSTOMER_ID, ORDER_STATUS, ORDER_TOTAL, SOURCE_SEQ,
           UPDATED_AT, METADATA$ACTION AS ACTION_NAME,
           METADATA$ISUPDATE AS IS_UPDATE
    FROM RAW_ORDERS_STREAM
    QUALIFY ROW_NUMBER() OVER (
      PARTITION BY ORDER_ID
      ORDER BY SOURCE_SEQ DESC, IFF(METADATA$ACTION = 'INSERT', 1, 0) DESC
    ) = 1
  ) AS S
  ON T.ORDER_ID = S.ORDER_ID
  WHEN MATCHED AND S.ACTION_NAME = 'DELETE' AND NOT S.IS_UPDATE
    THEN UPDATE SET T.IS_DELETED = TRUE, T.APPLIED_AT = CURRENT_TIMESTAMP()
  WHEN MATCHED AND S.ACTION_NAME = 'INSERT'
    THEN UPDATE SET T.CUSTOMER_ID = S.CUSTOMER_ID,
                    T.ORDER_STATUS = S.ORDER_STATUS,
                    T.ORDER_TOTAL = S.ORDER_TOTAL,
                    T.SOURCE_SEQ = S.SOURCE_SEQ,
                    T.UPDATED_AT = S.UPDATED_AT,
                    T.IS_DELETED = FALSE,
                    T.APPLIED_AT = CURRENT_TIMESTAMP()
  WHEN NOT MATCHED AND S.ACTION_NAME = 'INSERT'
    THEN INSERT (ORDER_ID, CUSTOMER_ID, ORDER_STATUS, ORDER_TOTAL, SOURCE_SEQ, UPDATED_AT, IS_DELETED, APPLIED_AT)
         VALUES (S.ORDER_ID, S.CUSTOMER_ID, S.ORDER_STATUS, S.ORDER_TOTAL, S.SOURCE_SEQ, S.UPDATED_AT, FALSE, CURRENT_TIMESTAMP())
  WHEN NOT MATCHED AND S.ACTION_NAME = 'DELETE' AND NOT S.IS_UPDATE
    THEN INSERT (ORDER_ID, CUSTOMER_ID, ORDER_STATUS, ORDER_TOTAL, SOURCE_SEQ, UPDATED_AT, IS_DELETED, APPLIED_AT)
         VALUES (S.ORDER_ID, S.CUSTOMER_ID, S.ORDER_STATUS, S.ORDER_TOTAL, S.SOURCE_SEQ, S.UPDATED_AT, TRUE, CURRENT_TIMESTAMP());

ALTER TASK APPLY_RAW_ORDERS_TO_SILVER_TRIGGERED RESUME;
```

Do not run both scheduled and triggered versions against the same stream and target at the same time; competing consumers make the experiment harder to interpret and may split the change batches. Use one design at a time.

## Step 4 — Test inserts, updates, and deletes

**Run these as separate batches.** After each operation, wait for the task to complete successfully and confirm the expected silver state before issuing the next operation for the same key. This isolates each change set and prevents the lab's deliberately simple source-sequence reducer from being mistaken for a universal ordering strategy.

```sql
-- Batch A: insert a new row, then wait for the task to commit.
INSERT INTO RAW_ORDERS (ORDER_ID, CUSTOMER_ID, ORDER_STATUS, ORDER_TOTAL, SOURCE_SEQ)
VALUES (1004, 504, 'NEW', 150.00, 1);
```

After the task succeeds, verify `ORDER_ID = 1004` in silver. Then run the update as a separate batch:

```sql
-- Batch B: update an existing row; increment the source sequence.
UPDATE RAW_ORDERS
SET ORDER_STATUS = 'PAID', ORDER_TOTAL = 59.95,
    SOURCE_SEQ = 2, UPDATED_AT = CURRENT_TIMESTAMP()
WHERE ORDER_ID = 1001;
```

After the task succeeds, verify `ORDER_ID = 1001` reflects the new status and total. Finally, delete a row in its own batch:

```sql
-- Batch C: delete an existing row, then wait for the task to commit.
DELETE FROM RAW_ORDERS WHERE ORDER_ID = 1002;
```

Inspect pending stream metadata before task consumption when possible, then wait for the task run. Verify target state:

```sql
SELECT * FROM SILVER_ORDERS ORDER BY ORDER_ID;
-- A TRUE result can be a false positive; validate actual stream rows and task history.
SELECT SYSTEM$STREAM_HAS_DATA('RAW_ORDERS_STREAM');
SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
  TASK_NAME => 'APPLY_RAW_ORDERS_TO_SILVER',
  SCHEDULED_TIME_RANGE_START => DATEADD('hour', -2, CURRENT_TIMESTAMP()),
  RESULT_LIMIT => 50
)) ORDER BY SCHEDULED_TIME DESC;
```

Expected observations: inserts appear in silver; updates change the existing silver row; deletes follow the chosen tombstone policy. A successful task run should consume the stream through the committed DML transaction. If the task has not run yet, use the supported manual execution approach for your task configuration or wait for the schedule; do not consume the stream with a test DML statement before verifying the pipeline.

## Step 5 — Create the gold dynamic table

```sql
CREATE DYNAMIC TABLE GOLD_ORDER_STATUS_SUMMARY
  TARGET_LAG = '5 minutes'
  WAREHOUSE = TOPIC05_WH
  REFRESH_MODE = INCREMENTAL
AS
SELECT
  ORDER_STATUS,
  COUNT(*) AS ORDER_COUNT,
  SUM(ORDER_TOTAL) AS TOTAL_ORDER_VALUE
FROM SILVER_ORDERS
WHERE IS_DELETED = FALSE
GROUP BY ORDER_STATUS;

SHOW DYNAMIC TABLES LIKE 'GOLD_ORDER_STATUS_SUMMARY';
SELECT * FROM GOLD_ORDER_STATUS_SUMMARY ORDER BY ORDER_STATUS;
```

The creation statement may initialize the table immediately; the scheduler then aims to keep the table within the target lag. Do not assume a refresh occurs exactly every five minutes. If the query definition is not eligible for incremental refresh, Snowflake will reject the explicit mode; adjust the query or test `FULL` deliberately and compare costs.

## Step 6 — Compare with a task-based alternative

Create a separate table and a task that refreshes the same summary. Use a dedicated table to avoid two pipelines writing to the same target.

```sql
CREATE TABLE GOLD_ORDER_STATUS_TASK AS
SELECT ORDER_STATUS, COUNT(*) AS ORDER_COUNT, SUM(ORDER_TOTAL) AS TOTAL_ORDER_VALUE
FROM SILVER_ORDERS
WHERE IS_DELETED = FALSE
GROUP BY ORDER_STATUS;

CREATE TASK REFRESH_GOLD_ORDER_STATUS_TASK
  WAREHOUSE = TOPIC05_WH
  SCHEDULE = '5 MINUTE'
AS
  CREATE TABLE GOLD_ORDER_STATUS_TASK AS
  SELECT ORDER_STATUS, COUNT(*) AS ORDER_COUNT, SUM(ORDER_TOTAL) AS TOTAL_ORDER_VALUE
  FROM SILVER_ORDERS
  WHERE IS_DELETED = FALSE
  GROUP BY ORDER_STATUS;

ALTER TASK REFRESH_GOLD_ORDER_STATUS_TASK RESUME;
```

Compare output correctness, freshness, refresh duration, and compute. This task example intentionally recomputes the whole aggregate and is a simple baseline—not necessarily a production design. `CREATE OR REPLACE TABLE` can have dependency/grant implications; production should use a safer stable-target design.

## Step 7 — Inspect dynamic table refreshes

```sql
SELECT *
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(
  NAME => 'GOLD_ORDER_STATUS_SUMMARY', RESULT_LIMIT => 50
))
ORDER BY REFRESH_START_TIME DESC;
```

Record actual refresh state, duration, lag, query IDs, and errors. Compare at least several refreshes under similar input volume; a single observation is not enough to conclude which design is cheaper.

## Step 8 — Safe stream-staleness exercise

1. Run `DESCRIBE STREAM RAW_ORDERS_STREAM` and record `STALE` / `STALE_AFTER` if available.
2. Explain the table's `DATA_RETENTION_TIME_IN_DAYS` and `MAX_DATA_EXTENSION_TIME_IN_DAYS` settings.
3. Do **not** wait for or force a stale state on a valuable table. The exact time is account- and retention-dependent.
4. In a disposable schema, document a recovery plan: identify last applied source sequence, reconcile/backfill from `RAW_ORDERS`, recreate the stream only after defining a no-gap boundary, and validate row-level results.
5. If your account supports a disposable source-recreation demonstration, perform it only after understanding that `CREATE OR REPLACE TABLE` can invalidate the original stream. Then prove that recreating the stream alone does not restore the lost delta.

## Step 9 — Failure monitoring and alerting

First inspect task failures:

```sql
SELECT NAME, STATE, SCHEDULED_TIME, COMPLETED_TIME, ERROR_CODE, ERROR_MESSAGE, QUERY_ID
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
  TASK_NAME => 'APPLY_RAW_ORDERS_TO_SILVER',
  SCHEDULED_TIME_RANGE_START => DATEADD('hour', -24, CURRENT_TIMESTAMP()),
  RESULT_LIMIT => 100
))
WHERE STATE = 'FAILED'
ORDER BY SCHEDULED_TIME DESC;
```

Inspect stream health:

```sql
DESCRIBE STREAM RAW_ORDERS_STREAM;
SHOW STREAMS LIKE 'RAW_ORDERS_STREAM';
```

Optional email alert template (run only after an administrator has created and authorized `OPS_EMAIL_INTEGRATION`, and replace the recipient with a verified address):

```sql
CREATE ALERT TOPIC05_FAILED_TASK_ALERT
  WAREHOUSE = TOPIC05_WH
  SCHEDULE = '5 MINUTE'
  IF (EXISTS (
    SELECT 1
    FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
      TASK_NAME => 'APPLY_RAW_ORDERS_TO_SILVER',
      SCHEDULED_TIME_RANGE_START => DATEADD('minute', -10, CURRENT_TIMESTAMP()),
      RESULT_LIMIT => 100
    ))
    WHERE STATE = 'FAILED'
  ))
  THEN
    CALL SYSTEM$SEND_EMAIL(
      'OPS_EMAIL_INTEGRATION',
      'replace-with-verified-recipient@example.com',
      'Snowflake task failure detected',
      'Review TASK_HISTORY, the task QUERY_ID, and stream health.'
    );

ALTER ALERT TOPIC05_FAILED_TASK_ALERT RESUME;
```

The query is a teaching template: verify the current `CREATE ALERT` and `SYSTEM$SEND_EMAIL` syntax, privileges, recipient allow-list, and notification integration settings in your account. Because it checks a rolling ten-minute window every five minutes, it can send repeated notifications for the same failure; production alerting should add incident deduplication or a stateful notification boundary. Alerts are created suspended; resume only after reviewing the condition and recipient. If you lack permission to create alerts or email integrations, keep the monitoring queries and document how an external monitor would poll them. Never put secrets into task SQL or notification text.

## Step 10 — Cleanup

Suspend tasks and drop only the disposable objects created by this lab:

```sql
ALTER TASK IF EXISTS APPLY_RAW_ORDERS_TO_SILVER SUSPEND;
ALTER TASK IF EXISTS APPLY_RAW_ORDERS_TO_SILVER_TRIGGERED SUSPEND;
ALTER TASK IF EXISTS REFRESH_GOLD_ORDER_STATUS_TASK SUSPEND;
DROP TASK IF EXISTS APPLY_RAW_ORDERS_TO_SILVER;
DROP TASK IF EXISTS APPLY_RAW_ORDERS_TO_SILVER_TRIGGERED;
DROP TASK IF EXISTS REFRESH_GOLD_ORDER_STATUS_TASK;
DROP DYNAMIC TABLE IF EXISTS GOLD_ORDER_STATUS_SUMMARY;
DROP STREAM IF EXISTS RAW_ORDERS_STREAM;
DROP TABLE IF EXISTS GOLD_ORDER_STATUS_TASK;
DROP TABLE IF EXISTS SILVER_ORDERS;
DROP TABLE IF EXISTS RAW_ORDERS;
-- Only if this lab created TOPIC05_WH, and only after confirming it is disposable:
-- DROP WAREHOUSE IF EXISTS TOPIC05_WH;
-- Drop the schema/database only if created exclusively for this lab.
-- DROP SCHEMA IF EXISTS SNOWFLAKE_TOPIC05_LAB.ELT;
-- DROP DATABASE IF EXISTS SNOWFLAKE_TOPIC05_LAB;
```

If you created `TOPIC05_FAILED_TASK_ALERT`, suspend and drop it before cleanup (`ALTER ALERT TOPIC05_FAILED_TASK_ALERT SUSPEND; DROP ALERT TOPIC05_FAILED_TASK_ALERT;`). A suspended task does not incur repeated scheduled execution, but always verify status and clean up only objects created by this lab.

## Lab deliverables

Save in `experiments/05_streams_tasks/`:

- `01-setup.sql` — sandbox DDL and sample data.
- `02-stream-task-cdc.sql` — stream and task definitions.
- `03-dynamic-table-vs-task.sql` — gold alternatives.
- `04-monitoring.sql` — task/refresh history and stream-health queries.
- `README.md` — observed behavior, account limitations, and a recovery plan.

Do not record invented performance results. Label each result as an observed measurement, expected behavior, or a hypothesis to test.

---

# 12. Troubleshooting guide

| Symptom | Likely causes | Investigation / response |
|---|---|---|
| Stream query is empty | No committed changes since offset; changes already consumed; wrong source; stale stream | Check source DML history, `SYSTEM$STREAM_HAS_DATA`, `DESCRIBE STREAM`, and task history |
| Task remains suspended | New tasks start suspended; child task not enabled; root graph not resumed | Inspect task state and enable the graph according to current task-graph guidance |
| Task fails with privilege error | Task owner lacks object or warehouse privileges | Review execution role, ownership, warehouse `USAGE`, schema/object privileges |
| Task runs but silver is wrong | Missing delete handling, duplicate keys in source, incorrect sequence ordering, incorrect tombstone logic | Inspect stream rows and batch reduction; test each operation permutation |
| Task retries repeat effects | Non-idempotent DML or external side effect | Add stable keys/version guards and external idempotency controls |
| Stream becomes stale | Consumption gap exceeds available retention; source object replaced | Backfill/reconcile from retained source, then recreate stream at a defined boundary |
| Dynamic table is stale | Refresh runtime too long, target lag too tight, upstream bottleneck, warehouse sizing, failed refresh | Query refresh history and inspect dependency graph, query profile, and warehouse capacity |
| Dynamic table uses full refresh unexpectedly | Unsupported query operators or `AUTO` resolved to `FULL` | Inspect `SHOW DYNAMIC TABLES` and `refresh_mode_reason`; test supported query shape and explicit mode |
| High compute spend | Too-frequent tasks, oversized warehouse, full refreshes, repeated no-op runs | Lengthen schedule/target lag, trigger only when useful, tune SQL, compare measured credits |
| `SYSTEM$STREAM_HAS_DATA` is false but no output is expected | Stream is empty, already consumed, or staleness/source issue | Check staleness and source changes; don't treat the function as proof of end-to-end correctness |

---

# 13. Common mistakes

1. **Assuming a stream stores a permanent event log.** It exposes changes between offsets and can collapse intermediate operations into a net delta.
2. **Assuming a `SELECT` consumes a stream.** Offset advancement is tied to committed DML consumption.
3. **Assuming exactly-once business processing.** Transactions help within Snowflake; external side effects and business deduplication require explicit design.
4. **Ignoring update pairs.** Standard streams represent updates as delete/insert records; incorrect merge logic can tombstone an update.
5. **Merging duplicate source keys.** Deduplicate deterministically using a real source sequence before `MERGE`.
6. **Using append-only streams for mutable entities.** Updates and deletes will not be represented as needed for current-state maintenance.
7. **Leaving tasks suspended.** Task creation does not mean execution has begun.
8. **Retrying non-idempotent work.** Retries can multiply side effects unless the operation is safe to repeat.
9. **Treating target lag as a guaranteed interval.** It is a best-effort freshness target, not an exact schedule or hard SLA.
10. **Allowing accidental full refresh.** Verify refresh mode and query eligibility.
11. **Using the shortest possible target lag by default.** Freshness has a compute cost; match it to the business need.
12. **Forcing stream staleness on valuable data.** Rehearse recovery in an isolated schema and preserve a replayable source.
13. **Monitoring only task success.** Validate output correctness, stream age, refresh lag, query duration, and error details.
14. **Scheduling the same work twice.** Define clear ownership between Snowflake tasks, dynamic tables, and external orchestration.

---

# 14. Practice questions with answers

### 1. What does a stream store?

**Answer:** An offset on a source object that exposes change data between source versions; it is not a separate permanent event table.

### 2. How does a standard stream represent an update?

**Answer:** Usually as a delete/insert pair with `METADATA$ISUPDATE = TRUE` on both records. The net change set can depend on operations between offsets.

### 3. When does a stream offset advance?

**Answer:** When stream change data is consumed by DML and the transaction commits successfully. A failed/rolled-back transaction does not commit the offset advance.

### 4. What is the difference between a stream and a task?

**Answer:** The stream exposes changes; the task schedules or triggers execution of SQL/procedure logic that processes those changes.

### 5. Why is a `MERGE` not automatically exactly-once business processing?

**Answer:** Correctness depends on stable keys, deterministic source reduction, transaction boundaries, delete semantics, retries, and side effects outside Snowflake.

### 6. What does `SYSTEM$STREAM_HAS_DATA` do?

**Answer:** It indicates whether the stream has change data for task-trigger decisions. It does not replace transactional consumption or downstream correctness checks.

### 7. What is a task graph?

**Answer:** A set of dependent tasks, typically with a scheduled root and child tasks using `AFTER`; it can coordinate parallel work and finalization.

### 8. What does `TARGET_LAG = '5 minutes'` mean?

**Answer:** A freshness target of five minutes relative to source data, not a guarantee that the table refreshes exactly every five minutes.

### 9. When would you choose a dynamic table instead of streams and tasks?

**Answer:** When the desired transformation is naturally expressed as a supported `SELECT` and you want Snowflake to manage refreshes to a target lag, rather than owning imperative CDC logic.

### 10. When might a full refresh be preferable?

**Answer:** When incremental refresh is unsupported or when the changed-data volume makes a full rebuild more efficient. Validate with actual refresh history and cost data.

### 11. What happens when a stream becomes stale?

**Answer:** Its offset can no longer access the missing historical change set. Recreating the stream tracks future changes but does not restore the lost delta; reconciliation/backfill is required.

### 12. Which histories help diagnose failures?

**Answer:** `TASK_HISTORY` for task executions and `DYNAMIC_TABLE_REFRESH_HISTORY` for refresh state, timing, query IDs, and errors, subject to their documented retention windows and access requirements.

### 13. How should you reduce cost for a pipeline with a 15-minute business freshness requirement?

**Answer:** Start with a target lag/schedule that matches the requirement, use a right-sized isolated warehouse or suitable serverless task, avoid redundant refreshes, verify incremental mode, and measure real runtime/credits.

### 14. What is the role of dbt, Airflow, or Dagster?

**Answer:** They can manage SQL model workflows, tests, deployments, and cross-system orchestration. Define clear ownership rather than duplicating schedules already managed by Snowflake.

---

# 15. Roadmap checkpoint

Before moving to Topic 06, confirm you can:

- [ ] Explain how streams track changes and when offsets advance.
- [ ] Distinguish standard and append-only streams and interpret `METADATA$ACTION`, `METADATA$ISUPDATE`, and `METADATA$ROW_ID`.
- [ ] Create a task using an interval or CRON schedule and explain warehouse-based versus serverless execution.
- [ ] Build a task graph with dependencies and explain `SYSTEM$STREAM_HAS_DATA`, retries, and finalizers.
- [ ] Implement and test a CDC `MERGE` for inserts, updates, and deletes with deterministic key/version logic.
- [ ] Explain why a committed stream/task workflow is not, by itself, an exactly-once business guarantee.
- [ ] Create a dynamic table with a five-minute target lag and verify its refresh mode.
- [ ] Choose between streams/tasks, dynamic tables, materialized views, and dbt for a concrete workload.
- [ ] Diagnose task failures and dynamic-table refresh issues using history functions.
- [ ] Explain stream staleness and a safe reconciliation/recovery approach.
- [ ] Identify cost controls for warehouse selection, target lag, retries, and full refreshes.

**Checkpoint pass condition:** demonstrate a working sandbox CDC flow, explain the transaction/offset boundary, and write a short design note describing the recovery plan and the chosen ownership boundary between Snowflake and any external orchestrator.

---

# 16. Authoritative references

Use these official references to verify account-specific syntax, current limits, privileges, and feature behavior:

1. [Introduction to streams](https://docs.snowflake.com/en/user-guide/streams-intro) — offsets, metadata, transaction behavior, retention, and staleness.
2. [Introduction to tasks](https://docs.snowflake.com/en/user-guide/tasks-intro) — scheduling and triggered tasks.
3. [Task graphs](https://docs.snowflake.com/en/user-guide/tasks-graphs) — root/child/finalizer patterns and dependencies.
4. [TASK_HISTORY function](https://docs.snowflake.com/en/sql-reference/functions/task_history) — task execution history and arguments.
5. [Create a dynamic table](https://docs.snowflake.com/en/user-guide/dynamic-tables-create) — DDL, target lag, warehouse, and initialization.
6. [Set the target lag](https://docs.snowflake.com/en/user-guide/dynamic-tables-target-lag) — target lag semantics and dependency behavior.
7. [Dynamic table refresh modes](https://docs.snowflake.com/en/user-guide/dynamic-tables/refresh-modes) — `AUTO`, `FULL`, `INCREMENTAL`, `ADAPTIVE`, and constraints.
8. [DYNAMIC_TABLE_REFRESH_HISTORY function](https://docs.snowflake.com/en/sql-reference/functions/dynamic_table_refresh_history) — refresh status, timings, and errors.
9. [Choose and size warehouses for dynamic tables](https://docs.snowflake.com/en/user-guide/dynamic-tables/warehouse-selection) — warehouse and initialization compute.
10. [Alerts overview](https://docs.snowflake.com/en/user-guide/alerts) — alert setup, execution, and notification integration.

---

## Lab measurement discipline

This lesson supplies example SQL and expected behaviors; it does **not** claim that the SQL was executed against a live Snowflake account. Record measured results only after running the lab. For every result, capture the account/region and relevant edition or feature availability, warehouse size, source row count, timestamp, query ID, task/refresh state, and any observed credit metrics. Separate measured observations from expected behavior and hypotheses.
