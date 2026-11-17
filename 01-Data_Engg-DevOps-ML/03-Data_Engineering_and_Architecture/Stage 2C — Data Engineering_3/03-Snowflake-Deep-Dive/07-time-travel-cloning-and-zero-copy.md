# Snowflake Time Travel, Cloning, and Zero-Copy

> **Stage:** Stage 2C — Data Engineering_3  
> **Module:** 03-Snowflake-Deep-Dive  
> **Topic:** 07 — Time Travel, cloning, and zero-copy  
> **Lab directory:** `experiments/07_time_travel/`

## Why this topic matters

Production data changes and production systems fail: a deployment can run the wrong `UPDATE`, a pipeline can delete valid rows, an engineer can drop an object, or a migration can produce an incorrect schema. Snowflake provides several related capabilities, but they solve different problems:

- **Time Travel** lets an authorized role query, clone, or restore supported historical states while the data remains within its applicable retention window.
- **`UNDROP`** restores a supported dropped object to its most recent state before it was dropped, if it remains recoverable.
- **Zero-copy cloning** creates a writable logical copy that initially reuses existing micro-partitions rather than copying all table data.
- **Fail-safe** is a Snowflake-managed recovery service after Time Travel expires for eligible permanent data. It is not a self-service query interface or a guaranteed customer-controlled restore mechanism.
- **Replication and failover** address a different failure domain: availability and recovery across accounts/regions, when configured and supported.

None of these alone is a complete backup and disaster-recovery strategy. Production recovery also needs defined recovery point objectives (RPOs), recovery time objectives (RTOs), independent reproducible sources, tested runbooks, appropriate access control, and evidence that recovery actually worked.

## Learning objectives

By the end of this lesson, you should be able to:

- Query historical table data with `AT` and `BEFORE` using timestamps, offsets, and statement IDs.
- Explain retention periods and why edition, object type, configuration, and account policy matter.
- Restore dropped tables, schemas, and databases with `UNDROP` when still eligible.
- Choose between querying history, cloning a historical state, and restoring an object in place.
- Explain Time Travel, Fail-safe, and zero-copy cloning without promising indefinite recovery or zero storage cost.
- Recover safely from accidental `UPDATE`, `DELETE`, and `DROP` operations.
- Create isolated dev/test clones, protect sensitive data, and understand clone behavior for grants, streams, tasks, and external tables.
- Read storage signals in `SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS` and reason about permanent versus transient tables.
- Recognize the role of database replication, failover groups, and blue/green deployment patterns.
- Design a repeatable lab and CI workflow with validation, cleanup, and cost controls.

## Prerequisites

You should already understand:

- SQL `SELECT`, `WHERE`, `UPDATE`, `DELETE`, `DROP`, `CREATE TABLE`, transactions, and object qualification.
- Snowflake databases, schemas, tables, roles, grants, warehouses, and query history.
- Micro-partitions at a conceptual level.
- Why raw, silver, and gold layers have different retention, reproducibility, and availability needs.
- Basic deployment and test lifecycle concepts.

Use a **disposable lab database** and a role authorized to create/drop lab objects. Never run recovery experiments against production or an irreplaceable dataset.

## 1. Recovery vocabulary and mental model

### 1.1 Historical data lifecycle

```text
Current table data
      |
      | UPDATE / DELETE / TRUNCATE / DROP / replacement
      v
Historical version retained for Time Travel
      |  Query with AT/BEFORE, clone historically, or UNDROP dropped object
      |
      | retention window expires
      v
Fail-safe (eligible permanent data; Snowflake-managed recovery only)
      |
      | Fail-safe period completes and no clone retains the bytes
      v
Historical bytes are eventually eligible for purge
```

This diagram is conceptual. Actual storage lifecycle transitions are handled by Snowflake background processes; do not assume a retention change or purge is instantaneous.

### 1.2 Time Travel vs Fail-safe vs cloning

| Capability | Main purpose | Customer-initiated? | What it can do | Important limit |
|---|---|---:|---|---|
| Time Travel | Inspect/recover a prior state | Yes, with permissions | Historical `SELECT`, historical clone, `UNDROP` while eligible | Only within effective retention and supported object constraints |
| `UNDROP` | Restore a dropped object | Yes, with permissions | Restore supported object to its most recent pre-drop state | Fails if same-name object conflicts or object is no longer recoverable |
| Zero-copy clone | Isolated writable point-in-time copy | Yes, with permissions | Test changes without initially duplicating all table data | Later writes, added tables, and divergence can add storage; clone is not a backup by itself |
| Fail-safe | Emergency data recovery after Time Travel | No direct self-service historical query | Snowflake may recover eligible permanent data through its managed process | Not a user-facing historical query feature or an RTO guarantee |
| Replication/failover | Cross-account/region continuity | Requires advance configuration | Replicate supported objects and activate a secondary environment | Edition, object, region, lag, and configuration constraints apply |

**Core distinction:** Time Travel is a customer-accessible historical data feature. Fail-safe is a managed recovery layer for eligible permanent data after Time Travel. Cloning is a way to create an independent logical object from a current or retained historical state.

## 2. Beginner — Time Travel

### 2.1 How historical states are accessed

Snowflake tracks historical changes for supported objects according to the effective `DATA_RETENTION_TIME_IN_DAYS` policy. When data changes, the platform preserves enough historical information to reconstruct eligible prior states. For ordinary table queries, add `AT (...)` or `BEFORE (...)` immediately after the table reference in the `FROM` clause.

- `AT` requests the state at the specified point, inclusive of changes made by a statement/transaction at that point according to the documented semantics.
- `BEFORE` requests a point immediately before completion of the referenced statement. It does **not** mean “before the statement began.”
- Timestamp values must be interpreted with care: explicitly cast timestamps and use a known time zone. A timestamp without an explicit time-zone-aware type can be interpreted as UTC/session mapping behavior may affect results.
- An `OFFSET` is a negative number of seconds from now, for example `-300` for five minutes ago.
- `STATEMENT` uses a query ID. The query ID must be within the supported statement-ID lookup period (currently 14 days); older cases should use a known timestamp instead. The referenced historical data must still be inside the table's retention window.

### 2.2 Example table for the lab

The following script creates a small permanent table with a few rows. It needs database/schema creation rights for the setup, `CREATE TABLE` in the target schema, and normal `SELECT`/DML privileges for the exercises. Use a fresh, dedicated lab database; the script intentionally fails if its names already exist. Do not change it to `CREATE OR REPLACE` as a shortcut because that can replace valuable objects.

```sql
-- Use a fresh, dedicated lab database name. These CREATE statements intentionally
-- fail if the name already exists; inspect existing resources rather than reusing
-- or replacing them blindly.
CREATE DATABASE TT_LAB_DB;
CREATE SCHEMA TT_LAB_DB.LAB;
USE DATABASE TT_LAB_DB;
USE SCHEMA LAB;

CREATE TABLE ORDERS_LAB (
    ORDER_ID NUMBER(10,0) NOT NULL,
    CUSTOMER_ID NUMBER(10,0) NOT NULL,
    ORDER_STATUS VARCHAR(20),
    ORDER_AMOUNT NUMBER(12,2),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
DATA_RETENTION_TIME_IN_DAYS = 1;

INSERT INTO ORDERS_LAB (ORDER_ID, CUSTOMER_ID, ORDER_STATUS, ORDER_AMOUNT)
VALUES
    (101, 501, 'PAID', 125.00),
    (102, 502, 'PENDING', 80.00),
    (103, 503, 'PAID', 240.00);

SELECT * FROM ORDERS_LAB ORDER BY ORDER_ID;
```

**Inputs:** three synthetic orders. **Output:** three rows. `CREATE OR REPLACE` is convenient for a disposable lab, but it replaces the existing object and can create another historical version. Do not use it casually in production recovery.

### 2.3 Query by offset

```sql
SELECT ORDER_ID, ORDER_STATUS, ORDER_AMOUNT
FROM TT_LAB_DB.LAB.ORDERS_LAB AT (OFFSET => -60 * 5)
ORDER BY ORDER_ID;
```

This requests a state from approximately five minutes earlier. It can fail if the table did not exist then, historical data is unavailable, or the point lies outside effective retention. The exact result depends on what operations occurred during the interval.

### 2.4 Query by timestamp

```sql
SELECT ORDER_ID, ORDER_STATUS, ORDER_AMOUNT
FROM TT_LAB_DB.LAB.ORDERS_LAB
  AT (TIMESTAMP => '2026-10-18 12:00:00 +00:00'::TIMESTAMP_TZ)
ORDER BY ORDER_ID;
```

Replace the illustrative timestamp with a real timestamp within the applicable retention window. The explicit `TIMESTAMP_TZ` cast makes the intended UTC offset visible. Do not copy the sample time if it is outside your lab's history.

### 2.5 Query by statement ID

The statement ID should be captured immediately after the statement of interest, from the client/query history. The example below uses a placeholder, not a valid query ID:

```sql
SELECT ORDER_ID, ORDER_STATUS, ORDER_AMOUNT
FROM TT_LAB_DB.LAB.ORDERS_LAB
  BEFORE (STATEMENT => '<UPDATE_QUERY_ID>')
ORDER BY ORDER_ID;
```

Use a real query ID, such as the ID returned by Snowsight Query History or `LAST_QUERY_ID()` captured in the same session after the target statement. `BEFORE(STATEMENT => ...)` shows the table immediately before that statement completed. `AT(STATEMENT => ...)` is also available for supported statement types.

**Important limitations:**

- Time Travel does not provide history before an object was created.
- Historical data must still be retained; an extended retention value does not retroactively reconstruct history that was already unavailable.
- Historical queries use current object column definitions and current access-control requirements; do not assume the old schema or old privileges are restored by querying old rows.
- Time Travel has restrictions for some object types. Hybrid tables, for example, have more limited historical-query syntax; verify object-specific documentation before relying on generic examples.
- A Time Travel query is not a general audit log of every query or user action. Use query/access history and application logs for forensic questions.

### 2.6 `AT` versus `BEFORE`

| Syntax | Meaning | Typical use |
|---|---|---|
| `AT (TIMESTAMP => ...)` | Historical state at a time | Compare against a known deployment time |
| `AT (OFFSET => -N)` | State N seconds ago | Quick investigation of recent changes |
| `AT (STATEMENT => id)` | State at the statement's reference point | Reproduce state associated with a known query ID |
| `BEFORE (STATEMENT => id)` | State immediately before completion of that statement | Inspect data before a bad DML statement |

When multiple transactions execute concurrently, `BEFORE(STATEMENT => ...)` is not necessarily equivalent to the exact state at the start of the statement. For high-confidence recovery, use the documented semantics, inspect query history, and validate row counts and business invariants.

## 3. Retention periods and object-specific behavior

### 3.1 General retention model

Snowflake's standard Time Travel retention is generally **1 day (24 hours)**. Extended retention up to **90 days** requires Enterprise Edition or higher for eligible permanent databases, schemas, and tables. Standard Edition generally supports 0 or 1 day. Temporary and transient tables are limited to 0 or 1 day and have no Fail-safe period. The effective behavior depends on object type, edition, object-level overrides, inherited parameters, and any account-level minimum retention policy.

| Object category | General Time Travel guidance | Fail-safe guidance | Notes |
|---|---|---|---|
| Permanent table/schema/database | Standard default is 1 day; Enterprise+ can configure eligible objects up to 90 days | Generally 7 days after Time Travel for eligible permanent data | Verify the actual object and account parameters |
| Transient table | 0 or 1 day | None | Use only if data is reproducible or another recovery path exists |
| Temporary table | 0 or 1 day, with retention ending when dropped/session ends | None | Session-scoped and not appropriate for durable recovery |
| Unsupported/specialized object types | Varies | Varies | Check current object-specific docs before designing recovery |

**Do not assume every object in a database inherits the same effective value.** A database/schema can set defaults for contained objects that do not override them. Account-level policy may also affect the effective minimum. Dropped objects retain the retention behavior they had when dropped; changing the current schema/database setting does not necessarily rewrite retention for already-dropped children.

### 3.2 Inspect current settings

```sql
SHOW PARAMETERS LIKE 'DATA_RETENTION_TIME_IN_DAYS' IN ACCOUNT;
SHOW PARAMETERS LIKE 'DATA_RETENTION_TIME_IN_DAYS' IN DATABASE TT_LAB_DB;
SHOW PARAMETERS LIKE 'DATA_RETENTION_TIME_IN_DAYS' IN SCHEMA TT_LAB_DB.LAB;
SHOW PARAMETERS LIKE 'DATA_RETENTION_TIME_IN_DAYS' IN TABLE TT_LAB_DB.LAB.ORDERS_LAB;
```

**Privileges:** visibility of account settings and object access varies by role; use an authorized administrator when required. `SHOW PARAMETERS` is a discovery step, not a complete guarantee of effective retention for every historical object.

For a disposable table, a setting can be changed as follows:

```sql
ALTER TABLE TT_LAB_DB.LAB.ORDERS_LAB
  SET DATA_RETENTION_TIME_IN_DAYS = 1;
```

Do not lower retention globally to make a lab expire faster. Lowering a setting can reduce recoverability for many objects; retention changes and purging are not a safe way to simulate failure against real data.

### 3.3 Retention is not indefinite recovery

If the requested point is outside the effective retention period, a historical query or historical clone fails. Once Time Travel expires, historical data is no longer available for customer querying or normal `UNDROP`. Eligible permanent data may enter Fail-safe, but that is not a user-controlled substitute for Time Travel. Transient and temporary tables have no Fail-safe recovery path.

Use a safe retention-expiry exercise: inspect configured settings, calculate the boundary, and document the expected failure. If you want to observe an actual expired object, create a disposable transient table with no valuable data and arrange a controlled wait that is consistent with its retention settings. Never shorten account-wide retention or delete valuable data merely to force an experiment.

## 4. `UNDROP` for dropped objects

`UNDROP` restores the most recent version of a supported dropped object to its original database/schema while the object remains recoverable through Time Travel. Common forms are:

```sql
UNDROP TABLE TT_LAB_DB.LAB.ORDERS_LAB;
UNDROP SCHEMA TT_LAB_DB.LAB;
UNDROP DATABASE TT_LAB_DB;
```

Run only the command appropriate to an object you intentionally dropped in the disposable lab. If an object with the same name already exists, `UNDROP` fails; rename or remove the conflicting object only after confirming it is safe. If multiple versions with the same name were dropped, identify the intended dropped object using `SNOWFLAKE.ACCOUNT_USAGE.TABLES.TABLE_ID` (or the supported object-history source) and use the documented `IDENTIFIER(<table_id>)` form for `UNDROP TABLE`. For example, `UNDROP TABLE IDENTIFIER(123456);` is illustrative only: replace `123456` with the actual numeric table ID returned for the intended dropped version. Do not use a query ID in place of a table ID. Not all object types are undroppable; hybrid tables have restrictions.

### 4.1 Find dropped objects

```sql
SHOW TABLES HISTORY LIKE 'ORDERS_LAB' IN SCHEMA TT_LAB_DB.LAB;

-- If multiple dropped versions exist, find the intended table_id in Account Usage.
-- Account Usage can lag; verify the row and deleted timestamp before restoring.
SELECT TABLE_ID, TABLE_NAME, TABLE_SCHEMA, TABLE_CATALOG, CREATED, DELETED
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLES
WHERE TABLE_CATALOG = 'TT_LAB_DB'
  AND TABLE_SCHEMA = 'LAB'
  AND TABLE_NAME = 'ORDERS_LAB'
  AND DELETED IS NOT NULL
ORDER BY DELETED;

-- Only after verifying the intended TABLE_ID, use the documented ID form:
-- UNDROP TABLE IDENTIFIER(<actual_numeric_table_id>);
```

History output can show dropped versions and `DROPPED_ON`. If an object has passed retention and has been purged, it may no longer appear in history. `SHOW ... HISTORY` is useful for discovery; it is not a promise that a restore will succeed.

### 4.2 Recovery after a mistaken drop

```text
Confirm exact account/database/schema/table
             |
             v
Inspect SHOW TABLES HISTORY / query history
             |
             v
Check for name conflict and retention eligibility
             |
             v
UNDROP TABLE <fully-qualified-name>
             |
             v
Validate row counts, keys, recent writes, grants, and downstream dependencies
             |
             v
Record incident, stop destructive retries, and restore pipeline safely
```

For a dropped schema or database, first consider the wider blast radius. Restoring a container can bring back multiple objects; it does not mean downstream tasks, integrations, grants, or external dependencies are all correctly operational.

## 5. Intermediate — Recover from bad `UPDATE` or `DELETE`

### 5.1 The safest default: inspect, then recover into a separate object

Do not immediately overwrite the production table with an assumed historical state. First identify the bad statement, inspect the historical rows, compare counts and business keys, and create a recovery candidate. Validate the candidate and choose an explicit merge/replace plan with appropriate approvals.

```sql
-- Example: inspect the table immediately before a known bad UPDATE.
SELECT ORDER_ID, ORDER_STATUS, ORDER_AMOUNT
FROM TT_LAB_DB.LAB.ORDERS_LAB
  BEFORE (STATEMENT => '<BAD_UPDATE_QUERY_ID>')
ORDER BY ORDER_ID;
```

The placeholder must be replaced by the real query ID. This query is read-only and is preferred as the first diagnostic action.

### 5.2 Recover a table by cloning a historical point

```sql
CREATE TABLE TT_LAB_DB.LAB.ORDERS_RECOVERY_CANDIDATE
  CLONE TT_LAB_DB.LAB.ORDERS_LAB
  BEFORE (STATEMENT => '<BAD_UPDATE_QUERY_ID>');

SELECT COUNT(*) AS ROW_COUNT,
       COUNT(DISTINCT ORDER_ID) AS DISTINCT_ORDER_IDS
FROM TT_LAB_DB.LAB.ORDERS_RECOVERY_CANDIDATE;
```

This creates a writable table clone representing the source table at the specified historical point, provided the historical data remains available and the source object supports this syntax. It does **not** automatically replace the original table. Review schema, constraints, grants, policies, downstream references, and concurrent writes before using it for restoration.

### 5.3 Compare current and historical state

For small lab data, a simple query is sufficient. In production, compare by stable business keys and account for inserts, deletes, duplicate keys, and legitimate writes that happened after the incident.

```sql
SELECT ORDER_ID, ORDER_STATUS, ORDER_AMOUNT
FROM TT_LAB_DB.LAB.ORDERS_LAB
ORDER BY ORDER_ID;

SELECT ORDER_ID, ORDER_STATUS, ORDER_AMOUNT
FROM TT_LAB_DB.LAB.ORDERS_LAB
  BEFORE (STATEMENT => '<BAD_UPDATE_QUERY_ID>')
ORDER BY ORDER_ID;
```

For production, prefer a controlled reconciliation that identifies which rows are affected by the bad operation. Restoring an entire historical table can discard valid writes that occurred after the bad statement. Time Travel recovers a state, not a business-aware merge policy.

### 5.4 Restore strategy decision table

| Incident | First action | Candidate recovery | Main risk |
|---|---|---|---|
| Incorrect update to a few rows | Capture query ID; inspect before/after | Reconstruct affected rows or merge from historical state | Overwriting legitimate later updates |
| Accidental delete | Confirm deletion statement and expected keys | Historical query/clone; merge deleted keys back | Reintroducing rows that were intentionally deleted later |
| Table dropped | Inspect history and conflicts | `UNDROP TABLE` or clone historical state if appropriate | Restoring wrong version or restoring dependencies incompletely |
| Table truncated | Confirm statement and blast radius | Historical clone/query within retention | Large recovery and storage impact |
| Bad schema migration | Stop downstream writes; identify DDL/DML and dependency changes | Clone a known-good schema/database, then validate | Historical data and current metadata may not align exactly |
| Retention expired | Stop assuming Time Travel can help | Restore from independent backup/source or engage Snowflake support for eligible Fail-safe recovery | No guaranteed self-service restore or RTO |
| Region/account outage | Invoke DR plan | Configured replication/failover or external source rebuild | Replication lag and unreplicated objects |

## 6. Zero-copy cloning

### 6.1 What “zero-copy” means

A clone is a new writable logical object whose initial table data references existing micro-partitions. Creating the clone does not immediately duplicate the entire physical table data. Source and clone initially share the same underlying storage representation. They are logically independent: changing rows in the source does not change the clone's logical result, and changing rows in the clone does not change the source's result.

As either object changes, Snowflake writes new micro-partitions or retains historical bytes as needed. Additional storage may be charged for modified data, new tables, and old bytes retained for Time Travel, Fail-safe, or other clones. Therefore, **zero-copy does not mean permanently zero storage cost**.

```text
Before clone:
  SOURCE table ─────► [P1] [P2] [P3] [P4]

Immediately after clone:
  SOURCE table ─────► [P1] [P2] [P3] [P4]
  DEV clone    ─────► [P1] [P2] [P3] [P4]  (shared existing micro-partitions)

After DEV modifies data in P2 and inserts new rows:
  SOURCE table ─────► [P1] [P2] [P3] [P4]
  DEV clone    ─────► [P1] [P2'] [P3] [P4] [P5]
                              ^ new/diverged storage as needed
```

The drawing is conceptual, not a guarantee that each SQL update maps to exactly one micro-partition or a fixed number of bytes. Snowflake manages physical layout internally.

### 6.2 Clone a table, schema, or database

```sql
-- Table clone
CREATE TABLE TT_LAB_DB.LAB.ORDERS_CLONE
  CLONE TT_LAB_DB.LAB.ORDERS_LAB;

-- Schema clone (use a separate target schema name)
CREATE SCHEMA TT_LAB_DB.LAB_CLONE
  CLONE TT_LAB_DB.LAB;

-- Database clone (use a separate target database name)
CREATE DATABASE TT_LAB_DB_CLONE
  CLONE TT_LAB_DB;
```

**Inputs:** source object and a new target name. **Output:** writable clone. **Privileges:** table cloning generally requires `SELECT` on the source table plus appropriate privileges on the source and target containers; schema/database cloning requires relevant privileges such as `USAGE`/ownership according to object and operation. Use the official `CREATE ... CLONE` privilege matrix for the exact role design. These examples may fail if target names already exist; use fresh lab names rather than replacing objects without inspection.

### 6.3 Clone a historical state

```sql
CREATE TABLE TT_LAB_DB.LAB.ORDERS_CLONE_BEFORE_BAD_UPDATE
  CLONE TT_LAB_DB.LAB.ORDERS_LAB
  BEFORE (STATEMENT => '<BAD_UPDATE_QUERY_ID>');
```

A historical clone is useful when you need an isolated, writable recovery candidate. Historical cloning is limited to retained data and supported object types. For schemas/databases, some child objects may not be cloned; review the specific cloning limitations before assuming the clone is complete. A historical schema/database clone can fail if a child table's required historical data is outside that child's retention, unless a supported option such as `IGNORE TABLES WITH INSUFFICIENT DATA RETENTION` is deliberately used; skipping tables changes completeness. Historical schema cloning also has task-specific limitations, so verify the resulting object inventory and task state.

### 6.4 Storage measurement is an observation, not a promise

To compare before/after storage, take a baseline and then observe the table-level metrics after a controlled write. Account Usage views can have latency, so results may not update immediately.

```sql
SELECT TABLE_CATALOG,
       TABLE_SCHEMA,
       TABLE_NAME,
       IS_TRANSIENT,
       ACTIVE_BYTES,
       TIME_TRAVEL_BYTES,
       FAILSAFE_BYTES,
       RETAINED_FOR_CLONE_BYTES,
       DELETED,
       TABLE_CREATED,
       TABLE_DROPPED
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS
WHERE TABLE_CATALOG IN ('TT_LAB_DB', 'TT_LAB_DB_CLONE')
  AND TABLE_SCHEMA IN ('LAB', 'LAB_CLONE')
ORDER BY TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME;
```

This query requires permission to read the relevant `SNOWFLAKE.ACCOUNT_USAGE` data (often through an appropriate monitoring role or granted database role). Adjust the catalog/schema filters to the actual target objects. Metrics describe billed/retained storage categories; they are not a byte-perfect per-statement estimate of what a clone operation “cost.”

## 7. Clone considerations and common traps

### 7.1 Grants and ownership

Do not assume every grant on a source object is copied to its clone. The cloned database/schema container itself does not inherit grants on the source container; when a database or schema is cloned, child objects can inherit the grants on those child objects. For individual objects, grant-copy behavior depends on whether the object-specific `CREATE ... CLONE` syntax supports `COPY GRANTS` and whether it is specified. After cloning, explicitly inspect container and child-object grants/ownership, then apply least-privilege target-environment grants.

### 7.2 Streams

When a database or schema containing source tables and streams is cloned, unconsumed records in the cloned streams are not available as if the source stream's pending change set had been copied. A clone's historical table data begins at the clone point. Do not treat a cloned stream as a durable copy of the source stream's pending offset/change history. Recreate or reinitialize change capture deliberately when required.

### 7.3 Tasks and alerts

Tasks in a cloned database/schema are generally created suspended. Do not assume they will run automatically. Inspect task definitions and fully qualified references; decide whether the clone should run tasks at all. Resuming a cloned task without reviewing its targets can cause duplicate writes or accidental changes to shared production objects. Alerts are also suspended by default when cloned.

### 7.4 External tables and references

External tables are not cloned as ordinary child objects in a database/schema clone. Other object definitions (views, tasks, streams) may preserve references to fully qualified source objects. Review SQL definitions for hard-coded database/schema names, external locations, integrations, and shared objects before using a clone as an isolated environment.

### 7.5 Policies, tags, and sensitive data

A clone may contain production PII. Do not assume cloning automatically sanitizes it. Snowflake cloning can preserve or remap masking and row-access policy references depending on whether policy objects live inside or outside the cloned container. Foreign policy references and tag-based masking can behave differently from local policy references.

Before giving developers access:

1. Create the clone in a restricted schema/database.
2. Inspect tables, views, grants, tags, masking policies, and row access policies.
3. Validate the effective behavior using the actual developer role, not only an administrator role.
4. Apply a supported masking/sanitization process and verify outputs.
5. Grant access only after the privacy check passes.
6. Record cleanup/expiry ownership for the clone.

A clone is not a privacy boundary by itself. Policy correctness must be tested.

## 8. Storage costs, `TABLE_STORAGE_METRICS`, and transient tables

### 8.1 What the storage categories mean

`SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS` provides table-level storage information, including dropped tables while they still incur storage costs. Key columns include:

- `ACTIVE_BYTES`: active data bytes owned/billed to the table.
- `TIME_TRAVEL_BYTES`: bytes in Time Travel.
- `FAILSAFE_BYTES`: bytes in Fail-safe.
- `RETAINED_FOR_CLONE_BYTES`: deleted bytes still retained because a clone or qualifying backup references them.
- `IS_TRANSIENT`: whether the table is transient/temporary.
- `DELETED`, `TABLE_DROPPED`, and `TABLE_ENTERED_FAILSAFE`: lifecycle signals for historical object versions.

Storage bytes are owned/billed according to Snowflake's storage accounting rules; cloning does not transfer all original bytes to the clone. A source table can still show retained storage after changes or drops because a clone references older bytes. Multiple historical versions can also appear for the same table name.

### 8.2 Storage-cost reasoning

Do not estimate retention cost as “whole table size × number of days” in every case. Snowflake generally retains the historical information needed to restore changed/deleted rows, so the storage impact often depends on churn; dropping or truncating a table can require retaining a much larger prior state. Measure with Account Usage after allowing for its reporting latency.

A useful conceptual model is:

```text
Incremental historical storage ≈ bytes needed to preserve changed/deleted data
                                + full-state retention effects for DROP/TRUNCATE
                                + bytes retained because clones still reference data
```

This is a reasoning aid, not a billing formula. The actual bill depends on object history, table type, change pattern, retention configuration, clone divergence, and account billing rules.

### 8.3 Permanent vs transient vs temporary

| Type | Lifetime | Time Travel | Fail-safe | Appropriate use |
|---|---|---|---|---|
| Permanent | Until dropped | 0–1 day on Standard; eligible objects up to 90 days on Enterprise+ | Generally 7 days | Durable raw/silver/gold data and data needing the strongest built-in recovery path |
| Transient | Until dropped | 0 or 1 day | None | Reproducible intermediate data with an independent rebuild path |
| Temporary | Session-scoped | 0 or 1 day; ends on drop/session end | None | Short-lived session work |

Do not make a critical raw or gold table transient solely to save storage. First quantify the cost and define a tested reload/rebuild path, source retention, recovery time, and ownership. Transient/temporary tables cannot rely on Fail-safe after Time Travel ends.

### 8.4 Observe storage for the lab

Run the `TABLE_STORAGE_METRICS` query before creating a clone, after creating it, and after a controlled update/insert in the clone. Record:

- When the query was run and the Account Usage freshness caveat.
- The source/clone table names and `CLONE_GROUP_ID` if included in your query.
- Which bytes changed and which stayed shared/retained.
- Whether any increase is attributable to actual changes, retained history, or unrelated lab objects.

Do not claim that changing exactly 1% of logical rows must create exactly 1% additional storage. Updates operate on internal storage structures and compression; the ratio is an experiment result, not a guarantee.

## 9. Advanced — database replication and disaster recovery awareness

Time Travel protects a historical window within Snowflake's data lifecycle. Cloning gives an isolated logical copy within the relevant environment. Neither automatically provides independent cross-region recovery from every account, region, credential, or operational failure.

Snowflake supports database replication and, for eligible configurations, replication/failover groups. Availability depends on edition and the objects being replicated. Database/share replication is available more broadly; replication of additional account objects and failover/failback has Business Critical-or-higher constraints in the current documentation. Cross-region/cross-cloud support and object eligibility should be checked for the account and region before a design is approved.

A DR design should specify:

- **RPO:** how much recent data may be lost, considering replication lag and source availability.
- **RTO:** how long it may take to activate and validate the secondary environment.
- What is replicated (databases, users/roles/integrations or other account objects where supported).
- What is not replicated or needs separate provisioning, secrets, network configuration, external storage permissions, and integrations.
- How secondary objects are monitored and how failover/failback is rehearsed.
- How data residency, encryption, legal holds, and access governance apply in both regions.

Do not present replication as instantaneous or automatically consistent with every external system. Use the current replication and failover documentation for supported objects, schedule, lag, prerequisites, and operational steps.

## 10. Advanced — blue/green deployment with clones and `SWAP WITH`

A blue/green approach reduces deployment risk by testing a candidate separately and then switching object names after validation. It is not a substitute for compatibility planning or rollback design.

```text
BLUE (current production)
      |
      +---- clone to GREEN
                 |
                 +-- apply migration
                 +-- run validation and application tests
                 +-- inspect grants, policies, references, and jobs
                 |
            approval gate
                 |
        controlled SWAP WITH
                 |
GREEN becomes active name; former BLUE receives the alternate name
                 |
       smoke tests + monitoring + rollback decision
```

For a table-level demonstration:

```sql
-- Use only disposable lab objects with compatible structures.
CREATE TABLE TT_LAB_DB.LAB.ORDERS_BLUE (
    ORDER_ID NUMBER(10,0),
    ORDER_STATUS VARCHAR(20),
    ORDER_AMOUNT NUMBER(12,2)
);

INSERT INTO TT_LAB_DB.LAB.ORDERS_BLUE
SELECT ORDER_ID, ORDER_STATUS, ORDER_AMOUNT
FROM TT_LAB_DB.LAB.ORDERS_LAB;

CREATE TABLE TT_LAB_DB.LAB.ORDERS_GREEN
  CLONE TT_LAB_DB.LAB.ORDERS_BLUE;

-- Perform candidate-only changes and validate GREEN first.
-- Do not run this swap until both names and dependencies are understood.
ALTER TABLE TT_LAB_DB.LAB.ORDERS_BLUE
  SWAP WITH TT_LAB_DB.LAB.ORDERS_GREEN;
```

`SWAP WITH` exchanges object names; it does not merge data. Application references that resolve by name may begin using the other table immediately. Validate object types, privileges, dependencies, streams, policies, and consumer behavior. Use a deployment approval gate and an explicit rollback procedure. A table swap does not automatically reverse side effects in downstream systems or undo data written after the switch.

For schema/database-level deployments, confirm the supported `SWAP WITH` syntax for the specific object type and ensure dependencies do not remain hard-coded to the old database/schema. Keep the first lab at table level to make the behavior easier to observe.

## 11. Retention policy design for raw, silver, and gold

Retention should follow data criticality, reproducibility, compliance, and cost—not a single default applied without analysis.

| Layer | Typical design questions | Example direction (not a universal policy) |
|---|---|---|
| Raw/landing | Can source files be replayed? How long does source storage retain them? How much incident investigation is needed? | Permanent where raw data is an important evidence/recovery source; align Snowflake retention with source retention and compliance |
| Silver/conformed | Can it be rebuilt from raw? Are CDC changes/late-arriving data recoverable? | Permanent for business-critical conformed data; shorter retention only with verified replay and recovery SLAs |
| Gold/serving | Can it be rebuilt from silver? What are freshness and service requirements? | Permanent if serving continuity matters; transient only when rebuild is tested, acceptable, and policy-compliant |
| Temporary ETL work | Is it truly ephemeral and reproducible? | Temporary/transient only when lack of Fail-safe is acceptable |

For each layer, record the effective retention, source-of-truth, expected churn, data owner, restore runbook, RPO/RTO, and storage/cost owner. Avoid increasing retention indiscriminately: longer retention can increase storage cost, especially on high-churn tables or tables that are frequently truncated/reloaded.

## 12. Compliance and data deletion

Time Travel and Fail-safe can preserve historical bytes after a row is changed or deleted. That can conflict with a simplistic interpretation of “delete the row and all copies immediately.” Conversely, turning off retention is not automatically a complete legal-erasure procedure because background storage lifecycle processes and clone references matter.

For personal data or regulated datasets:

- Consult the organization's privacy/legal retention policy before changing retention settings or deleting data.
- Inventory source tables, clones, downstream tables, exports, external storage, backups, and replicated copies.
- Understand which data is retained for Time Travel, Fail-safe, and clones, and when it becomes eligible for purge.
- Document whether a legal hold, statutory retention, deletion request, or incident-response requirement applies.
- Use approved data lifecycle controls and verify outcomes through supported monitoring. Do not promise immediate physical erasure based only on a successful `DELETE` statement.
- Restrict access to historical data; current access-control requirements apply to historical queries, but historical access is still a privacy risk if too many roles can query it.

This lesson is not legal advice. A compliance deletion design must be reviewed against current Snowflake documentation and the applicable law and contract.

## 13. Production recovery runbooks

### Runbook A — incorrect `UPDATE`/`DELETE`

1. **Stop the damage:** pause the pipeline/task or revoke the specific write path if safe; avoid repeated retries.
2. **Record evidence:** query ID, user/role, warehouse, target object, execution time, SQL text, and incident scope.
3. **Confirm retention:** inspect the object's effective settings and whether the historical point is still accessible.
4. **Read before writing:** use `BEFORE(STATEMENT => query_id)` to inspect history; compare row counts, keys, aggregates, and known invariants.
5. **Create a candidate:** historical clone or a narrowly scoped reconstruction. Never overwrite the source before validation.
6. **Reconcile subsequent writes:** separate incident-caused changes from legitimate changes after the incident.
7. **Approve and restore:** use a reviewed `MERGE`, replacement, or controlled swap appropriate to the incident.
8. **Validate:** row counts, duplicate keys, financial/business totals, constraints, masking/access, downstream models, and freshness.
9. **Resume in stages:** restart dependent jobs in a controlled order and watch for duplicate or replayed writes.
10. **Document:** cause, recovery point, data loss (if any), elapsed time, cost, and prevention actions.

### Runbook B — dropped object

1. Verify the account, database, schema, object name, and exact incident time.
2. Inspect `SHOW ... HISTORY` and query history; check whether a same-name replacement exists.
3. Confirm the object remains within its applicable retention and is eligible for `UNDROP`.
4. Restore the most recent dropped version or use an object identifier when multiple versions require selection and the command supports it.
5. Validate data, grants, ownership, policies, dependencies, and task state.
6. If `UNDROP` is not available, stop repeated attempts; evaluate historical cloning or independent rebuild/backup paths. Fail-safe is not a self-service guarantee.

### Runbook C — bad deployment

1. Stop rollout and isolate candidate writes.
2. Capture migration version, query IDs, source schema/database, and time of deployment.
3. Create a clone of the known-good state if still available and permitted.
4. Run migration and data validation in the candidate environment.
5. Verify policy/grant mappings and fully qualified references.
6. Use an approved swap/cutover only after application compatibility checks.
7. Keep rollback candidates until the defined rollback window ends, while understanding their storage cost and sensitive-data exposure.

### Runbook D — retention expired

1. Do not claim Time Travel or `UNDROP` can recover the data if the historical state is no longer retained.
2. Check whether an independent source, backup, export, replicated database, or rebuildable upstream remains available.
3. For eligible permanent data, escalate through the approved Snowflake support process if Fail-safe recovery may apply. It is Snowflake-managed and not guaranteed to satisfy a chosen RTO.
4. For transient/temporary data after retention, rely on independent replay/rebuild paths; there is no Fail-safe period.
5. Record data loss, recovery limitations, and corrective changes to backup/retention design.

## 14. Hands-on lab — `experiments/07_time_travel/`

### Lab goals

You will: (1) recover from an incorrect update using a statement identifier; (2) drop and restore a disposable table; (3) investigate retention safely; (4) clone a schema and observe storage behavior after modifying a small subset; (5) build a clone/migrate/test/cleanup workflow; and (6) reason about repeated reloads and retention costs.

### 14.1 Suggested project layout

```text
experiments/07_time_travel/
├── README.md
├── 01_setup.sql
├── 02_bad_update_recovery.sql
├── 03_undrop_table.sql
├── 04_retention_inspection.sql
├── 05_clone_storage_observation.sql
├── 06_ci_clone_migrate_test.sql
└── 07_reload_retention_cost_model.md
```

These are suggested files for the lab, not additional deliverables in this task. The examples below can be copied into them.

### 14.2 Setup and permissions

Use a dedicated disposable database and a small auto-suspending warehouse. A role needs privileges to use the warehouse/database/schema and create/modify/drop lab objects. Cloning requires privileges on source objects and target containers. `UNDROP` requires the applicable ownership/management privileges. Reading Account Usage metrics may require a monitoring role/database role grant. Ask your Snowflake administrator to grant the minimum privileges needed; do not use `ACCOUNTADMIN` as a routine lab role.

```sql
CREATE WAREHOUSE TT_LAB_WH
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

-- Use a fresh, dedicated lab database name. These CREATE statements intentionally
-- fail if the name already exists; inspect existing resources rather than reusing
-- or replacing them blindly.
CREATE DATABASE TT_LAB_DB;
CREATE SCHEMA TT_LAB_DB.LAB;
USE WAREHOUSE TT_LAB_WH;
USE DATABASE TT_LAB_DB;
USE SCHEMA LAB;
```

The role running these commands needs the appropriate create/usage privileges. If a trial account or organizational policy prevents creating a warehouse, use an existing approved small warehouse and record that constraint.

### 14.3 Exercise 1 — controlled bad update and historical recovery

Create the table and data in a fresh disposable lab database. This script intentionally fails if `ORDERS_LAB` already exists; inspect it and choose a new lab database/name rather than rerunning a destructive replacement.

```sql
CREATE TABLE TT_LAB_DB.LAB.ORDERS_LAB (
    ORDER_ID NUMBER(10,0),
    CUSTOMER_ID NUMBER(10,0),
    ORDER_STATUS VARCHAR(20),
    ORDER_AMOUNT NUMBER(12,2)
)
DATA_RETENTION_TIME_IN_DAYS = 1;

INSERT INTO TT_LAB_DB.LAB.ORDERS_LAB VALUES
    (101, 501, 'PAID', 125.00),
    (102, 502, 'PENDING', 80.00),
    (103, 503, 'PAID', 240.00);
```

Record the baseline:

```sql
SELECT COUNT(*) AS ROWS_BEFORE,
       SUM(ORDER_AMOUNT) AS AMOUNT_BEFORE
FROM TT_LAB_DB.LAB.ORDERS_LAB;
```

Run a deliberately incorrect but contained update:

```sql
UPDATE TT_LAB_DB.LAB.ORDERS_LAB
SET ORDER_STATUS = 'CANCELLED';

SELECT LAST_QUERY_ID() AS BAD_UPDATE_QUERY_ID;
```

Copy the returned query ID somewhere safe. Then inspect the historical state:

```sql
SELECT ORDER_ID, ORDER_STATUS, ORDER_AMOUNT
FROM TT_LAB_DB.LAB.ORDERS_LAB
  BEFORE (STATEMENT => '<PASTE_BAD_UPDATE_QUERY_ID>')
ORDER BY ORDER_ID;
```

Expected observation: the query shows the rows before the bad update completed, normally retaining the original statuses. Now create a recovery candidate:

```sql
CREATE TABLE TT_LAB_DB.LAB.ORDERS_RECOVERY_CANDIDATE
  CLONE TT_LAB_DB.LAB.ORDERS_LAB
  BEFORE (STATEMENT => '<PASTE_BAD_UPDATE_QUERY_ID>');

SELECT COUNT(*) AS RECOVERY_ROWS,
       SUM(ORDER_AMOUNT) AS RECOVERY_AMOUNT
FROM TT_LAB_DB.LAB.ORDERS_RECOVERY_CANDIDATE;
```

Validate before deciding whether to use the candidate. For the lab, compare the rows and totals; do not automatically replace `ORDERS_LAB`. In production, reconcile legitimate later writes and use an approved recovery plan.

### 14.4 Exercise 2 — `DROP` and `UNDROP`

Use a disposable copy so the original lab table remains available:

```sql
CREATE TABLE TT_LAB_DB.LAB.DROP_ME_LAB
  CLONE TT_LAB_DB.LAB.ORDERS_LAB;

DROP TABLE TT_LAB_DB.LAB.DROP_ME_LAB;

SHOW TABLES HISTORY LIKE 'DROP_ME_LAB' IN SCHEMA TT_LAB_DB.LAB;

UNDROP TABLE TT_LAB_DB.LAB.DROP_ME_LAB;

SELECT COUNT(*) FROM TT_LAB_DB.LAB.DROP_ME_LAB;
```

Expected observation: the dropped table appears in history while it remains retained; `UNDROP` restores the most recent dropped version if it is eligible and no same-name object blocks restoration. Verify the row count and data. This test demonstrates restoration within retention; it does not simulate Fail-safe or prove recovery after expiry.

### 14.5 Exercise 3 — retention expiry, safely

Inspect settings and history:

```sql
SHOW PARAMETERS LIKE 'DATA_RETENTION_TIME_IN_DAYS' IN TABLE TT_LAB_DB.LAB.DROP_ME_LAB;
SHOW TABLES HISTORY LIKE 'DROP_ME_LAB' IN SCHEMA TT_LAB_DB.LAB;
```

Write down the configured retention, drop time, expected eligibility boundary, and actual observed status. **Do not** drop valuable data and wait for it to expire. Do not lower account/database retention to force the experiment. To observe actual expiry, use only a disposable transient object with synthetic data, after confirming the current parameter behavior and arranging an adequate wait. Expiry and background purging may not occur at an exact second, and Account Usage/history views can lag. If the environment cannot safely wait, record the expected behavior from official docs and treat the expiry case as a design review, not a completed runtime experiment.

### 14.6 Exercise 4 — clone a schema and observe storage

For a large dataset, the roadmap suggests a 100 GB schema. That size may be expensive or unavailable in a trial. Use a proportionate synthetic table first, then document why results do not extrapolate linearly to 100 GB.

Create a table with enough rows for measurable data volume, or use an approved existing lab dataset:

```sql
CREATE TABLE TT_LAB_DB.LAB.CLONE_SOURCE AS
SELECT SEQ4() AS ID,
       UNIFORM(1, 1000000, RANDOM()) AS VALUE_N,
       RPAD('x', 100, 'x') AS PAYLOAD
FROM TABLE(GENERATOR(ROWCOUNT => 100000));

CREATE SCHEMA TT_LAB_DB.LAB_CLONE
  CLONE TT_LAB_DB.LAB;
```

This statement intentionally fails if `CLONE_SOURCE` already exists; inspect it or use a fresh disposable lab schema rather than replacing an existing table. This generates synthetic data; it is not intended to create exactly 100 GB. The generated table size depends on compression and Snowflake storage behavior. If cloning the entire `LAB` schema would include other lab objects you do not want, create a dedicated schema for this exercise and clone only that schema.

Capture the storage baseline:

```sql
SELECT TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, CLONE_GROUP_ID,
       ACTIVE_BYTES, TIME_TRAVEL_BYTES, FAILSAFE_BYTES,
       RETAINED_FOR_CLONE_BYTES, IS_TRANSIENT
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS
WHERE TABLE_CATALOG IN ('TT_LAB_DB')
  AND TABLE_NAME = 'CLONE_SOURCE'
ORDER BY TABLE_SCHEMA, TABLE_NAME;
```

Make a controlled modification in the clone only:

```sql
UPDATE TT_LAB_DB.LAB_CLONE.CLONE_SOURCE
SET VALUE_N = VALUE_N + 1
WHERE ID BETWEEN 1 AND 1000;

INSERT INTO TT_LAB_DB.LAB_CLONE.CLONE_SOURCE (ID, VALUE_N, PAYLOAD)
VALUES (-1, 7, 'new clone-only row');
```

Wait for Account Usage metrics to become available and rerun the query. Compare source and clone results, active bytes, Time Travel bytes, Fail-safe bytes, and retained-for-clone bytes. Explain why the clone initially reuses data but diverges after writes. Do not expect exactly 1% of changed rows to equal exactly 1% of bytes.

**Cost control:** a 100 GB test can create storage and warehouse costs. Use a small warehouse, avoid repeated large updates, set auto-suspend, and remove lab clones when finished. If you use a smaller sample, state that it demonstrates behavior rather than production-scale billing.

### 14.7 Exercise 5 — CI-style clone → migration → tests → cleanup

This example uses a disposable table clone and a toy migration. In a real CI pipeline, use an isolated schema/database name per build, unique identifiers, a least-privilege service role, and a `finally`/cleanup step even when tests fail.

```sql
-- Start from a stable source table; use a unique target name per run.
CREATE TABLE TT_LAB_DB.LAB.CI_ORDERS_CANDIDATE
  CLONE TT_LAB_DB.LAB.ORDERS_LAB;

-- Example migration on the candidate only.
ALTER TABLE TT_LAB_DB.LAB.CI_ORDERS_CANDIDATE
  ADD COLUMN CI_MIGRATION_FLAG BOOLEAN DEFAULT FALSE;

-- Example smoke tests.
SELECT COUNT(*) AS ROW_COUNT
FROM TT_LAB_DB.LAB.CI_ORDERS_CANDIDATE;

SELECT COUNT(*) AS MISSING_IDS
FROM TT_LAB_DB.LAB.CI_ORDERS_CANDIDATE
WHERE ORDER_ID IS NULL;

-- Cleanup only after test evidence has been recorded.
DROP TABLE TT_LAB_DB.LAB.CI_ORDERS_CANDIDATE;
```

Expected result: the candidate can be migrated without changing the source table. The smoke tests should report the expected row count and zero missing IDs for the sample. If a test fails, preserve diagnostic output and then clean up the disposable candidate. In CI, ensure cleanup is performed after failure as well; a manually run SQL script does not guarantee this automatically.

A production-grade CI workflow additionally validates grants, masking, row access policies, view references, task state, stream assumptions, migration reversibility, and application compatibility. Avoid resuming cloned tasks until references and targets have been audited.

### 14.8 Exercise 6 — repeated reloads and retention cost model

Compare two conceptual loading patterns:

- **Pattern A:** append/merge incrementally, changing a small fraction of rows.
- **Pattern B:** repeatedly `TRUNCATE` or replace a large table with a full reload.

Use actual `TABLE_STORAGE_METRICS` snapshots and warehouse/query history to observe costs. Do not infer exact historical storage from logical row count alone. The Time Travel storage impact of frequent full reloads may be substantially different from small incremental changes because Snowflake may need to retain a prior full state for truncate/drop-style operations.

Create a notes table or Markdown report with these columns:

| Experiment | Table type | Retention days | Load/update pattern | Logical rows changed | Active bytes | Time Travel bytes | Fail-safe bytes | Clone-retained bytes | Observation |
|---|---|---:|---|---:|---:|---:|---:|---:|---|
| Baseline | Permanent | 1 | Initial load | Record | Record | Record | Record | Record | Account Usage freshness noted |
| Incremental | Permanent | 1 | Small update | Record | Record | Record | Record | Record | Actual measurement only |
| Reload | Permanent | 1 | Truncate/reload | Record | Record | Record | Record | Record | Actual measurement only |
| Transient comparison | Transient | 1 | Synthetic test | Record | Record | Record | Record | Record | No Fail-safe; recovery risk documented |

Do not fill this table with invented values. The objective is to learn which categories change and how long they remain visible, not to claim a universal cost ratio.

### 14.9 Cleanup

Confirm the objects belong to this lab before dropping them. Preserve any notes/results you need first.

```sql
DROP TABLE IF EXISTS TT_LAB_DB.LAB.ORDERS_RECOVERY_CANDIDATE;
DROP TABLE IF EXISTS TT_LAB_DB.LAB.DROP_ME_LAB;
DROP TABLE IF EXISTS TT_LAB_DB.LAB.CLONE_SOURCE;
DROP TABLE IF EXISTS TT_LAB_DB.LAB.CI_ORDERS_CANDIDATE;
DROP SCHEMA IF EXISTS TT_LAB_DB.LAB_CLONE;
-- Drop the database and warehouse only if dedicated exclusively to this lab:
-- DROP DATABASE TT_LAB_DB;
-- DROP WAREHOUSE TT_LAB_WH;
```

`DROP` itself creates historical versions according to the object's retention behavior and may continue to incur storage charges. Do not assume cleanup removes all historical bytes immediately. Never run the commented database/warehouse drops if they contain unrelated work or are shared.

## 15. Troubleshooting guide

| Symptom | Likely cause | Safe response |
|---|---|---|
| Historical query says data is unavailable | Wrong timestamp cast/time zone, object did not yet exist, point outside retention, or unsupported object syntax | Check the query ID/time zone, object creation time, effective retention, and object-specific docs |
| `AT(STATEMENT => ...)` cannot find the query | Invalid query ID or statement lookup window exceeded | Retrieve exact ID; for older statements use a known timestamp if retained |
| `UNDROP` reports a name conflict | A current object has the same name | Inspect both versions; rename/remove only the confirmed disposable conflicting object |
| `UNDROP` fails after retention | Object is no longer eligible for Time Travel restoration | Stop retrying; check independent backups/rebuild sources and approved support path for eligible permanent data |
| Clone creation fails | Missing privileges, existing target name, unsupported child object, insufficient retention for historical clone | Verify source/target privileges, choose a fresh target, inspect unsupported objects and historical point |
| Clone exposes production PII | Clone is not automatically sanitized; policy reference behavior differs | Restrict access, test effective masking under target roles, sanitize before granting access |
| Cloned task runs against production | Fully qualified references remain pointed to source objects | Keep tasks suspended, inspect definitions and dependencies, only resume after target isolation is proven |
| Storage metrics do not change immediately | Account Usage latency/background lifecycle processing | Wait and re-query; record timestamps; do not interpret a stale snapshot as zero cost |
| Clone storage grows more than expected | Changes affect storage structures; new tables/data and retained history add bytes | Compare metrics and change pattern; avoid assuming logical row percentage equals byte percentage |
| Table appears in Fail-safe but cannot be undropped | Fail-safe is not user-facing `UNDROP` retention | Use approved support/DR/rebuild process; do not promise recovery timing |

## 16. Common mistakes

- Treating Time Travel as indefinite backup or assuming every object supports the same syntax.
- Confusing the 1-day standard retention with the Enterprise+ extended-retention maximum of 90 days for eligible permanent objects.
- Assuming an object-level parameter proves the effective retention for dropped objects or every child object.
- Believing Fail-safe is a customer-accessible historical query engine or a guaranteed restore SLA.
- Running `UNDROP` without checking for a same-name replacement or multiple dropped versions.
- Restoring an entire historical table without reconciling legitimate writes made after the incident.
- Treating zero-copy as zero ongoing storage cost.
- Assuming a schema/database clone includes external tables, every grant, or all pending stream change records.
- Resuming cloned tasks before reviewing their references and target tables.
- Assuming production masking is guaranteed to remain correct after cloning into a different schema/database.
- Using transient tables for critical data without an independent replay/recovery path.
- Lowering account-wide retention to force a lab test.
- Extrapolating a small synthetic storage test to 100 GB or claiming a fixed storage ratio without measurement.
- Dropping lab resources without checking ownership or whether they contain unrelated work.

## 17. Practice questions with answers

### Q1. What is the difference between `AT` and `BEFORE`?
**Answer:** `AT` requests a state at the specified point. `BEFORE(STATEMENT => id)` requests the point immediately before completion of the referenced statement; it does not necessarily represent the table state at the statement's start.

### Q2. What is the standard Time Travel retention period?
**Answer:** Generally 1 day (24 hours). Extended retention up to 90 days requires Enterprise Edition or higher for eligible permanent objects. Actual behavior depends on object type and configuration.

### Q3. Can I query data after the Time Travel window expires because Fail-safe exists?
**Answer:** No. Fail-safe is a Snowflake-managed recovery service for eligible permanent data, not a customer-facing historical query interface or guaranteed restore path.

### Q4. What does `UNDROP TABLE` restore?
**Answer:** The most recent dropped version of the table to its original schema, if it remains eligible for Time Travel restoration and no same-name object blocks it. It does not automatically reconcile downstream systems.

### Q5. Why is a clone called zero-copy?
**Answer:** It initially reuses existing micro-partitions instead of physically copying all data. It is writable and logically independent, but changes, new data, and retained historical bytes can add storage cost.

### Q6. Does cloning a schema guarantee every object and grant is copied?
**Answer:** No. Some object types such as external tables are not cloned as ordinary child objects; container grants and object grants have specific rules; streams and tasks have important behaviors. Review official clone considerations and validate the resulting environment.

### Q7. Why is cloning production not the same as anonymizing production?
**Answer:** A clone may contain the same sensitive data. Policy objects may be cloned or remapped depending on their location and references. Access must remain restricted until effective masking and sanitization are verified.

### Q8. When should a table be transient?
**Answer:** Only when it is short-lived or reproducible and the organization accepts no Fail-safe period. Critical data should not be made transient solely to save storage without a tested recovery plan.

### Q9. Why might a small update still add more storage than the logical row percentage suggests?
**Answer:** Physical storage is organized into micro-partitions and compression structures; the mapping between logical rows and physical bytes is not one-to-one. The actual result must be measured.

### Q10. Is a clone a complete DR strategy?
**Answer:** No. It is an isolated logical copy within the relevant environment. Cross-region/account DR requires deliberate replication/failover design, plus testing of object coverage, lag, credentials, integrations, RPO, and RTO.

### Q11. Why might a full reload retain more historical storage than an incremental update?
**Answer:** Snowflake may need to retain a prior full state for drop/truncate-style operations, whereas incremental changes may require preserving only affected historical data. Actual storage depends on the operation and retention lifecycle.

### Q12. What should you do if the historical point is outside retention?
**Answer:** Do not promise Time Travel recovery. Check independent backups, replayable sources, replicas, and rebuild paths; for eligible permanent data, follow the approved Snowflake support process for possible Fail-safe recovery.

## 18. Topic 07 checkpoint

Use this checklist to decide whether you are ready to continue:

- [ ] Query and restore data with Time Travel.
- [ ] Explain Fail-safe vs Time Travel.
- [ ] Use cloning for dev/test safely.
- [ ] Explain the storage cost of retention.

You should be able to complete the following without notes:

1. Use `AT` and `BEFORE` with timestamp, offset, and statement ID, explaining the differences and limits.
2. State the standard retention behavior and qualify extended retention by edition, object type, and configuration.
3. Recover a dropped disposable table using `UNDROP` and validate the restored version.
4. Create a historical clone after a controlled bad update and explain why it is a candidate, not an automatic production restore.
5. Explain shared micro-partitions, clone divergence, and storage metrics.
6. Identify clone caveats for grants, streams, tasks, external tables, and policies.
7. Explain why transient tables have no Fail-safe and define the recovery conditions required before using them.
8. Describe a tested recovery runbook and distinguish data recovery from cross-region disaster recovery.

## 19. Official documentation and further reading

The official documentation is authoritative for current syntax, edition limits, supported object types, and privilege requirements. Re-check these pages before applying the patterns to production because Snowflake features and edition constraints can change.

- [Understanding and using Time Travel](https://docs.snowflake.com/en/user-guide/data-time-travel)
- [AT | BEFORE query syntax](https://docs.snowflake.com/en/sql-reference/constructs/at-before)
- [UNDROP TABLE](https://docs.snowflake.com/en/sql-reference/sql/undrop-table)
- [UNDROP object command reference](https://docs.snowflake.com/en/sql-reference/sql/undrop)
- [UNDROP SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/undrop-schema)
- [CREATE ... CLONE](https://docs.snowflake.com/en/sql-reference/sql/create-clone)
- [Cloning considerations](https://docs.snowflake.com/en/user-guide/object-clone)
- [TABLE_STORAGE_METRICS](https://docs.snowflake.com/en/sql-reference/account-usage/table_storage_metrics)
- [Data storage considerations](https://docs.snowflake.com/en/user-guide/tables-storage-considerations)
- [Storage costs for Time Travel and Fail-safe](https://docs.snowflake.com/en/user-guide/data-cdp-storage-costs)
- [Replicating databases and account objects](https://docs.snowflake.com/en/user-guide/account-replication-config)
- [Failing over account objects](https://docs.snowflake.com/en/user-guide/account-replication-failover-failback)

---

**Completion standard:** You have learned this topic when you can safely inspect a historical state, build and validate a recovery candidate, restore a dropped lab object, explain the storage consequences of retention and cloning, and describe what your chosen recovery mechanism cannot guarantee.
