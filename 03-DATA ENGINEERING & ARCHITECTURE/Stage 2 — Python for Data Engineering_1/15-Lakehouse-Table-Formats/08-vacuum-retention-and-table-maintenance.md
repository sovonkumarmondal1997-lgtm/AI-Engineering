# CLAUDE CODE PROMPT — LEARN `08-vacuum-retention-and-table-maintenance.md`

## ROLE

Act as a **Senior Data Engineer with 10+ years of production experience** designing, building, operating, and optimizing large-scale data platforms and lakehouses.

You have deep production experience with:

- Apache Spark
- Delta Lake
- Apache Iceberg
- Apache Hudi
- Parquet
- object storage
- transactional lakehouse tables
- CDC pipelines
- streaming pipelines
- batch pipelines
- data retention
- table maintenance
- data governance
- disaster recovery
- data lifecycle management
- production observability
- cost optimization

You are my instructor.

Your job is to teach me the complete topic covered by:

```text
15-Lakehouse-Table-Formats/
└── 08-vacuum-retention-and-table-maintenance.md
```

Teach this topic progressively:

```text
Absolute Beginner
        ↓
Fundamentals
        ↓
Intermediate
        ↓
Advanced
        ↓
Production Data Engineering
```

Use simple language first.

Introduce advanced terminology only after the underlying mental model is clear.

The goal is NOT simply to teach me how to execute:

```text
VACUUM
DELETE
OPTIMIZE
EXPIRE SNAPSHOTS
```

The goal is to make me understand:

- why lakehouse tables accumulate obsolete files
- what obsolete files actually are
- why historical versions depend on retained files
- what retention means
- what VACUUM/cleanup operations do
- why cleanup is potentially dangerous
- how retention affects time travel
- how table maintenance differs across Delta Lake, Iceberg, and Hudi
- how to design safe retention policies
- how to schedule maintenance
- how to monitor maintenance
- how to avoid deleting data that is still required
- how maintenance affects cost
- how maintenance affects query performance
- how to operate table maintenance safely in production

---

# 1. STRICT FILE-SCOPE RULE

You are teaching **ONLY**:

```text
08-vacuum-retention-and-table-maintenance.md
```

Do NOT modify, rewrite, create, rename, delete, or update any other file in:

```text
15-Lakehouse-Table-Formats/
```

Do NOT modify:

```text
README.md
01-why-open-table-formats-exist.md
02-delta-lake-transaction-log.md
03-apache-iceberg-snapshots-and-manifests.md
04-apache-hudi-overview.md
05-acid-merge-update-and-delete-on-data-lakes.md
06-time-travel-and-table-versioning.md
07-compaction-z-ordering-and-liquid-clustering.md
09-catalogs-hive-metastore-glue-unity-and-polaris.md
practice-questions.md
```

You may READ prerequisite files if necessary for context.

However:

> **DO NOT MODIFY ANY OTHER FILE.**

All learning content, experiments, scripts, examples, notes, and implementation work must remain scoped to this topic.

---

# 2. AUTHORITATIVE ROADMAP RULE

Treat the existing Module 2.15 roadmap as the authoritative curriculum.

This lesson must focus on:

```text
VACUUM
Retention
Table maintenance
Obsolete files
Historical-state dependencies
Cleanup safety
Operational maintenance
```

Do not silently replace the roadmap with a different curriculum.

Use Delta Lake, Apache Iceberg, and Apache Hudi as implementation examples where appropriate.

However, clearly distinguish:

```text
Generic table-maintenance concept
        ↓
Delta-specific behavior
        ↓
Iceberg-specific behavior
        ↓
Hudi-specific behavior
        ↓
Engine/version-specific behavior
```

Never claim that all three formats implement maintenance identically.

If a feature or command is version-specific, state that explicitly.

---

# 3. CORE LEARNING OBJECTIVE

Build this mental model:

```text
Data arrives
    ↓
Table changes
    ↓
New files / new metadata
    ↓
Old files become obsolete
    ↓
Historical versions may still need them
    ↓
Retention policy determines how long they remain useful
    ↓
Maintenance identifies safe-to-remove data
    ↓
Cleanup removes obsolete physical data
    ↓
Storage cost decreases
    ↓
Operational health improves
```

The central principle must be:

> **Do not delete physical files merely because they are not part of the current table state. First determine whether they are still required by historical reads, active jobs, recovery procedures, retention requirements, or other consumers.**

---

# 4. START WITH THE BASIC QUESTION

Begin with:

> **Why do lakehouse tables accumulate old files?**

Use a simple example.

Initial table:

```text
table/
├── file-A.parquet
└── file-B.parquet
```

After an update:

```text
table/
├── file-A.parquet
├── file-B.parquet
└── file-C.parquet
```

Suppose the new table version no longer references:

```text
file-A.parquet
```

Explain:

```text
file-A.parquet
```

may still physically exist in object storage.

Ask:

> If the current table no longer uses this file, should we delete it immediately?

Do NOT answer immediately.

Make me reason about:

- time travel
- active readers
- failed jobs
- concurrent operations
- recovery
- retention
- compliance
- backups
- downstream consumers

Then introduce table maintenance.

---

# 5. LOGICAL TABLE STATE VS PHYSICAL STORAGE

This distinction is mandatory.

Explain:

```text
Logical table
```

versus:

```text
Physical files in object storage
```

Use:

```text
Current table state
        |
        +--> file-C
        +--> file-D
```

while storage may contain:

```text
file-A
file-B
file-C
file-D
file-E
```

Explain:

> Not every physical file currently present in object storage necessarily belongs to the current logical table state.

Then explain why the physical files cannot simply be deleted without understanding table history and retention.

---

# 6. OBSOLETE FILES

Define:

```text
obsolete file
```

carefully.

Explain that a file may become obsolete because:

- an UPDATE rewrote data
- a DELETE removed data
- a MERGE replaced files
- compaction rewrote files
- clustering reorganized data
- a failed job left an unreferenced file
- a table operation replaced an older physical representation

Create this mental model:

```text
Physical file exists
        |
        v
Referenced by current table?
        |
     +--+--+
     |     |
    Yes    No
           |
           v
     Is it still needed
     by history/recovery?
           |
        +--+--+
        |     |
       Yes    No
              |
              v
        Candidate for cleanup
```

Stress that:

> **Candidate for cleanup does not automatically mean safe to delete immediately.**

---

# 7. WHY CLEANUP EXISTS

Explain the problems caused by retaining obsolete files indefinitely.

Discuss:

- storage growth
- object-store costs
- metadata overhead
- operational clutter
- longer maintenance operations
- unnecessary storage consumption
- compliance/lifecycle management concerns

But also explain the opposite risk:

```text
Too much cleanup
```

can cause:

- loss of historical versions
- failed time-travel queries
- failed recovery
- broken long-running readers
- inability to reproduce historical data
- operational incidents

Teach:

```text
Retention
=
Storage cost
+
Historical accessibility
+
Recovery capability
+
Operational safety
```

---

# 8. RETENTION FUNDAMENTALS

Explain:

> What is a retention policy?

Start with a simple example:

```text
Keep historical data for 30 days.
```

Then ask:

> What exactly does "30 days" mean?

Discuss:

- 30 days of table history
- 30 days of data-file retention
- 30 days of metadata
- 30 days of audit information
- 30 days of backup retention

Explain that these are not necessarily the same thing.

---

# 9. RETENTION WINDOWS

Create examples:

```text
7 days
30 days
90 days
1 year
7 years
```

Explain how the appropriate retention period depends on:

- business requirements
- regulatory requirements
- recovery objectives
- time-travel requirements
- ML reproducibility
- backfill requirements
- debugging requirements
- storage cost
- downstream consumers

Do not prescribe one universal retention period.

---

# 10. TIME TRAVEL DEPENDENCY

Connect directly to the previous lesson.

Explain:

```text
Time travel
    ↓
Historical table state
    ↓
Historical metadata
    +
Historical data files
```

Therefore:

```text
Remove required historical files
        ↓
Old table version may become unreadable
```

Use:

```text
Version 100 → good
Version 101 → good
Version 102 → bad
```

Suppose Version 100 requires files that are later deleted.

Explain what happens.

---

# 11. TIME TRAVEL VS RETENTION

Teach:

```text
Time travel capability
```

does not mean:

```text
Unlimited historical access
```

Create this model:

```text
Table history
     |
     v
Retention policy
     |
     v
Maintenance
     |
     v
Old physical files removed
     |
     v
Historical state eventually unavailable
```

Explain this relationship carefully.

---

# 12. VACUUM

Now introduce:

```text
VACUUM
```

Explain it simply:

> VACUUM is a cleanup operation used by supported table systems to remove physical files that are no longer needed according to the system's retention and safety rules.

Do not present this as a universal definition across all formats.

Explain:

```text
Logical state
        ↓
Obsolete physical files
        ↓
Retention rules
        ↓
Cleanup
```

Then distinguish:

```text
table transaction
```

from:

```text
physical cleanup
```

---

# 13. VACUUM IS NOT DELETE FROM

Explicitly teach the difference.

```sql
DELETE FROM table
```

changes:

```text
logical table contents
```

while:

```text
VACUUM
```

or equivalent cleanup operations generally target:

```text
obsolete physical files
```

Create a comparison:

| Operation | Primary purpose |
|---|---|
| INSERT | Add logical records |
| UPDATE | Change logical records |
| DELETE | Remove logical records |
| MERGE | Apply logical mutations |
| Compaction | Improve physical layout |
| VACUUM/Cleanup | Remove obsolete physical data |
| Snapshot expiration | Remove old metadata/history references where supported |

Explain the distinction carefully.

---

# 14. VACUUM AND TABLE HISTORY

Use:

```text
Version 1
Version 2
Version 3
Version 4
```

Suppose the current table is:

```text
Version 4
```

but:

```text
Version 1
Version 2
```

are older than the retention policy.

Explain that maintenance may eventually remove physical data required for those historical states.

Therefore:

```text
Current state
≠
all historical states forever
```

---

# 15. DELTA LAKE VACUUM

Use Delta as the primary concrete example where appropriate.

Explain the conceptual relationship:

```text
Delta transaction history
        +
retained physical files
        ↓
time travel
```

Then:

```text
VACUUM
```

removes eligible obsolete data files.

Where supported by the installed environment, demonstrate the appropriate syntax.

For example, if compatible:

```sql
VACUUM delta.`/path/to/table` RETAIN 168 HOURS;
```

Explain every part.

Do not blindly execute destructive cleanup.

Use a disposable test table.

---

# 16. DELTA RETENTION SAFETY

Explain why aggressive retention is dangerous.

Discuss the conceptual relationship between:

```text
deleted-file retention
```

and:

```text
time-travel availability
```

Also explain why safety checks may exist to prevent dangerously short retention periods.

Do not tell me to bypass safety checks merely to make an example work.

If a test requires a shorter retention period:

> Explain the risks first and use an isolated disposable dataset.

---

# 17. DELTA VACUUM LAB

Create a small Delta table.

Perform:

```text
1. Initial write
2. Update
3. Delete
4. MERGE
5. Compaction/optimization where supported
```

Inspect:

```text
table history
data files
obsolete files
```

Then run a safe cleanup experiment.

After cleanup:

- inspect physical files
- inspect current table
- test historical access where appropriate
- explain what remains available
- explain what became unavailable

Do NOT manually delete files.

---

# 18. ICEBERG TABLE MAINTENANCE

Now explain the equivalent concepts in Iceberg.

Teach that Iceberg maintenance can involve operations such as:

```text
expire snapshots
rewrite data files
rewrite manifests
remove orphan files
```

where supported.

Explain the purpose of each at a high level.

Do not claim Iceberg has a universal command called `VACUUM`.

The important concept is:

> Iceberg has its own table-maintenance model for expiring historical snapshots and cleaning physical artifacts.

---

# 19. ICEBERG SNAPSHOT EXPIRATION

Explain:

```text
Snapshot 100
Snapshot 101
Snapshot 102
Snapshot 103
```

Suppose the retention policy says:

```text
retain recent snapshots
```

Explain:

```text
old snapshots
      ↓
expiration
      ↓
historical references removed
      ↓
eligible files can eventually be cleaned
```

Clearly distinguish:

```text
snapshot expiration
```

from:

```text
physical file deletion
```

Do not imply they are necessarily the same operation.

---

# 20. ICEBERG ORPHAN FILES

Explain the concept:

> A physical file may exist in storage without being referenced by valid table metadata.

Discuss possible causes:

- failed writes
- interrupted operations
- application bugs
- manual file creation
- abandoned data

Explain why blindly deleting unreferenced files can be dangerous.

Teach that orphan-file cleanup requires a safe retention window and careful coordination.

---

# 21. HUDI TABLE MAINTENANCE

Explain Hudi maintenance conceptually.

Connect:

```text
Hudi timeline
+
data files
+
log files
+
compaction
+
cleaning
```

Explain:

- cleaner
- compaction
- clustering where relevant
- archival concepts where relevant
- retention of older table state

Do not turn this into a full Hudi internals lesson.

Focus on:

> How Hudi keeps storage and table history manageable over time.

---

# 22. HUDI CLEANING

Explain the conceptual purpose of Hudi cleaning:

```text
old/unneeded file versions
        ↓
retention policy
        ↓
cleaning
```

Explain why cleaning too aggressively can interfere with:

- long-running readers
- historical access
- recovery
- incremental processing

Clearly state that exact behavior depends on Hudi configuration and table type.

---

# 23. COMPACTION VS VACUUM VS CLEANING

This comparison is mandatory.

Create:

| Operation | Main Purpose |
|---|---|
| Compaction | Consolidate/reorganize physical data |
| Clustering | Improve physical locality |
| VACUUM/Cleanup | Remove obsolete physical data |
| Snapshot expiration | Remove old historical references |
| Orphan cleanup | Remove unreferenced physical artifacts |

Then explain:

```text
Compaction
    ↓
creates/reorganizes files
    ↓
old files may become obsolete
    ↓
retention period passes
    ↓
cleanup
```

This relationship is extremely important.

---

# 24. MAINTENANCE LIFECYCLE

Build this complete model:

```text
Write
  ↓
New files
  ↓
Updates / deletes
  ↓
More files / obsolete files
  ↓
Compaction / clustering
  ↓
Additional obsolete files
  ↓
Retention period
  ↓
Cleanup / expiration
  ↓
Lower storage footprint
```

Explain every stage.

---

# 25. MAINTENANCE IS NOT FREE

Teach that maintenance consumes:

- compute
- memory
- network
- object-store I/O
- scheduling capacity
- temporary storage
- engineering effort

Compare:

```text
No maintenance
```

with:

```text
Aggressive maintenance
```

and:

```text
Policy-driven maintenance
```

Explain why the third is generally preferable.

---

# 26. MAINTENANCE FREQUENCY

Discuss:

```text
Hourly
Daily
Weekly
Threshold-based
Event-driven
```

Explain how to choose based on:

- ingestion volume
- mutation rate
- file growth
- table size
- query SLA
- historical-data requirements
- cost
- operational windows

Do not prescribe one schedule for every table.

---

# 27. RETENTION POLICY DESIGN

Teach me to create a policy with explicit dimensions.

For example:

```text
Table:
orders

Business retention:
7 years

Time-travel requirement:
30 days

Operational recovery:
14 days

ML reproducibility:
90 days

Physical cleanup:
after safe retention window
```

Explain why these requirements need to be reconciled.

Do not assume business retention and table-version retention are identical.

---

# 28. RETENTION MATRIX

Create a practical matrix:

| Requirement | Retention |
|---|---:|
| Current operational table | Continuous |
| Time travel | 30 days |
| Debugging | 14 days |
| ML reproducibility | 90 days |
| Compliance archive | 7 years |
| Backup | Separate policy |

Explain that these are example values only.

The actual values must come from business requirements.

---

# 29. LONG-RUNNING READERS

This is a critical safety concept.

Scenario:

```text
Reader starts
     ↓
Reader references older table state
     ↓
Cleanup runs
     ↓
Required files are deleted
```

Explain why this can cause problems.

Discuss:

- reader duration
- streaming jobs
- long-running Spark jobs
- backfills
- historical queries
- maintenance coordination

Teach:

> Retention must account for the maximum expected lifetime of readers and recovery operations.

---

# 30. ACTIVE JOB SAFETY

Explain why maintenance should not blindly run while critical jobs are active.

Consider:

```text
Streaming job
Backfill
Compaction
Cleanup
```

running concurrently.

Discuss:

- coordination
- retention buffers
- maintenance windows
- job duration
- monitoring
- safe sequencing

Do not claim that every system requires maintenance windows; explain the architecture-dependent nature.

---

# 31. FAILED JOBS AND ORPHAN FILES

Create this scenario:

```text
Job starts
   ↓
writes 500 files
   ↓
driver crashes
   ↓
commit never completes
```

Some files may remain physically present.

Explain:

```text
physical file exists
≠
file belongs to committed table state
```

Then explain how maintenance systems can eventually identify eligible orphan/obsolete files.

Do not teach manual deletion as the first response.

---

# 32. STORAGE COST MODEL

Teach a simple model:

```text
Storage Cost
=
Active Data
+
Historical Data
+
Obsolete Data
+
Metadata
```

Explain:

```text
Aggressive retention
→ lower storage
→ less historical accessibility

Long retention
→ higher storage
→ stronger recovery/history
```

Teach the trade-off explicitly.

---

# 33. COST OPTIMIZATION

Create a simple hypothetical example.

Suppose:

```text
Active table:
100 TB

Historical/obsolete data:
50 TB

Storage price:
X per TB-month
```

Calculate the approximate additional monthly storage cost.

Clearly label all numbers as hypothetical.

Then ask:

> Is the additional cost justified by the business requirement?

Teach that cost optimization is a business decision, not just a technical decision.

---

# 34. SECURITY AND GOVERNANCE

Explain how retention interacts with:

- data governance
- compliance
- right-to-delete requirements
- legal retention
- sensitive data
- audit requirements
- data minimization

Important distinction:

```text
Business data retention
```

versus:

```text
table-format historical retention
```

A table may retain an old physical file containing data that the current table no longer exposes.

Explain why deletion requirements may therefore require a deliberate lifecycle strategy.

Do not provide legal advice; explain the engineering implications.

---

# 35. RIGHT-TO-BE-FORGOTTEN / DATA DELETION

Use a conceptual example:

```text
Customer 101
```

must be deleted.

Explain why simply deleting it from the current table may not automatically remove all historical physical representations.

Teach the lifecycle:

```text
Logical deletion
      ↓
Historical versions
      ↓
Retention
      ↓
Physical cleanup
      ↓
Verification
```

Explain why this must be carefully coordinated.

Do not claim that VACUUM alone automatically guarantees complete deletion from every backup, replica, cache, or downstream system.

---

# 36. MAINTENANCE + TIME TRAVEL

Create this explicit relationship:

```text
Time Travel
     ↑
     |
Historical files
     |
Retention
     |
Maintenance
     |
Cleanup
```

Explain:

> Maintenance policies determine how far back the table can reliably support historical reads.

---

# 37. MAINTENANCE + COMPACTION

Connect to the previous topic.

Example:

```text
Before compaction:
1,000 files

After compaction:
100 files
```

The old 1,000 files may become obsolete.

Explain:

```text
Compaction
   ↓
new files
   ↓
old files become obsolete
   ↓
retention window
   ↓
cleanup
```

This is a core operational lifecycle.

---

# 38. MAINTENANCE + CLUSTERING

Similarly explain:

```text
Clustering
   ↓
rewrite physical layout
   ↓
old files become obsolete
   ↓
retention
   ↓
cleanup
```

Explain why physical optimization and cleanup must be designed together.

---

# 39. REQUIRED HANDS-ON LAB

Create a disposable local lakehouse maintenance laboratory.

Prefer:

```text
PySpark
+
Delta Lake
```

where compatible.

Introduce:

```text
Iceberg
Hudi
```

for format-specific maintenance concepts where practical.

Before running:

```text
Python
Java
Spark
Delta
Iceberg
Hudi
```

version checks are mandatory.

Never assume compatibility.

---

# 40. REQUIRED DELTA MAINTENANCE LAB

Create a disposable Delta table.

Perform:

```text
1. Initial write
2. UPDATE
3. DELETE
4. MERGE
5. Compaction/optimization where supported
6. Multiple table versions
```

Inspect:

```text
table history
data files
file counts
file sizes
obsolete files
```

Then demonstrate a safe cleanup process.

After cleanup:

```text
Current table
Historical access
Storage files
```

must be inspected.

Explain what changed.

---

# 41. REQUIRED ICEBERG MAINTENANCE LAB

Where supported:

1. Create multiple snapshots.
2. Inspect snapshot history.
3. Create rewritten data files.
4. Identify old snapshots.
5. Demonstrate snapshot expiration in a disposable environment.
6. Demonstrate safe orphan-file cleanup where supported.
7. Inspect the resulting metadata and physical files.

Clearly distinguish:

```text
snapshot expiration
```

from:

```text
orphan-file removal
```

and:

```text
data-file rewrite
```

---

# 42. REQUIRED HUDI MAINTENANCE LAB

Where supported:

1. Create a Hudi table.
2. Generate updates.
3. Create relevant file versions/log data.
4. Inspect timeline.
5. Demonstrate compaction where relevant.
6. Demonstrate cleaning/retention behavior in a disposable environment.
7. Inspect the result.

If the installed version does not support a particular feature:

> Do not fake the result.

Explain the version limitation.

---

# 43. REQUIRED RETENTION EXPERIMENT

Create a disposable table with several historical states.

For example:

```text
Version 1
Version 2
Version 3
Version 4
Version 5
```

Then configure a short test retention period.

Demonstrate:

```text
Before cleanup
    ↓
All historical states available
```

and after maintenance:

```text
Recent history available
Older history unavailable
```

Only perform destructive cleanup in a disposable test environment.

---

# 44. REQUIRED SAFETY EXPERIMENT

Intentionally create a scenario where:

```text
Historical version is still needed
```

Then ask:

> Should cleanup run?

Expected reasoning:

```text
No
```

until the required historical reader/recovery window has passed.

Explain why.

---

# 45. REQUIRED ORPHAN-FILE INVESTIGATION

Create or simulate:

```text
file exists physically
but is not referenced by current table metadata
```

Investigate:

```text
Is it:
- obsolete?
- orphaned?
- still needed by history?
- part of an incomplete operation?
```

Do not immediately delete it.

Teach the investigation process.

---

# 46. REQUIRED MAINTENANCE SCHEDULER DESIGN

Design a production workflow:

```text
Ingestion
    ↓
Measure table health
    ↓
Compaction needed?
    |
    +-- Yes → Compact
    |
    +-- No
    ↓
Clustering needed?
    |
    +-- Yes → Cluster
    |
    +-- No
    ↓
Retention threshold reached?
    |
    +-- Yes → Cleanup
    |
    +-- No
    ↓
Report health
```

Explain how to make every decision metric-driven.

---

# 47. MAINTENANCE OBSERVABILITY

Define metrics for:

## Storage

- active bytes
- obsolete bytes
- total bytes
- historical bytes
- file count

## Table health

- small-file ratio
- file-size distribution
- snapshot/version count
- metadata size

## Maintenance

- cleanup runtime
- compaction runtime
- clustering runtime
- files removed
- bytes removed
- bytes rewritten
- failure count

## Historical accessibility

- oldest available version
- oldest available timestamp
- retention window

---

# 48. MAINTENANCE ALERTS

Design alerts such as:

```text
Obsolete storage exceeds threshold
```

```text
Maintenance has not run for N days
```

```text
File count exceeds threshold
```

```text
Historical retention window below policy
```

```text
Cleanup removed unexpectedly large volume
```

```text
Maintenance job failed
```

Explain why each alert matters.

---

# 49. MAINTENANCE RUNBOOK

Create a production runbook.

When maintenance fails:

```text
1. Identify failed operation
2. Check table state
3. Check table history
4. Check active jobs
5. Check object-storage errors
6. Check metadata
7. Check recently created files
8. Check retention policy
9. Determine whether retry is safe
10. Retry or escalate
```

Explain each step.

---

# 50. SAFE CLEANUP CHECKLIST

Before cleanup, verify:

```text
1. Retention policy
2. Historical-read requirement
3. Long-running readers
4. Streaming jobs
5. Backfills
6. Recovery requirements
7. Backup policy
8. Compliance requirements
9. Table dependencies
10. Maintenance job health
11. Version compatibility
12. Dry-run/inspection capability where supported
```

Do not treat cleanup as a casual shell command.

---

# 51. COMMON MISCONCEPTIONS

Explicitly correct:

### Misconception 1

> "If a file is not in the current table, delete it."

Wrong.

It may still be needed by historical states or active operations.

### Misconception 2

> "VACUUM is the same as DELETE."

Wrong.

One is physical cleanup; the other changes logical table contents.

### Misconception 3

> "VACUUM deletes all old data."

Wrong.

Cleanup follows retention/safety rules and format-specific semantics.

### Misconception 4

> "Time travel works forever."

Wrong.

Historical access depends on retained metadata and physical data.

### Misconception 5

> "Longer retention is always better."

Wrong.

It increases storage and operational costs.

### Misconception 6

> "Shorter retention is always cheaper and therefore better."

Wrong.

It can reduce recovery, debugging, and reproducibility capabilities.

### Misconception 7

> "Compaction removes obsolete files immediately."

Not necessarily.

Explain the lifecycle.

### Misconception 8

> "Snapshot expiration and physical file deletion are always the same operation."

Wrong.

Explain the distinction.

### Misconception 9

> "An orphan file is automatically safe to delete."

Wrong.

Investigate its origin and retention requirements first.

### Misconception 10

> "Maintenance can run without considering active jobs."

Wrong.

Long-running readers and concurrent operations matter.

---

# 52. PRODUCTION RETENTION DESIGN EXERCISE

Give me this scenario:

> A company operates a 100 TB lakehouse with continuous CDC ingestion. Data changes throughout the day. The analytics team requires 30 days of time travel. The ML team requires 90-day reproducibility. Some Spark jobs can run for 12 hours. Compliance requires long-term retention outside the operational table.

Ask me to design:

```text
operational retention
time-travel retention
cleanup schedule
maintenance schedule
long-running-reader safety
ML reproducibility
compliance archive
monitoring
```

Then provide a model senior-engineer solution.

---

# 53. COST/PERFORMANCE EXERCISE

Give me a hypothetical example:

```text
Active data: 100 TB
Historical/obsolete data: 60 TB
```

Ask:

1. What is the storage impact?
2. What happens if retention is reduced?
3. What risks increase?
4. What requirements should determine the final policy?

Then provide the model reasoning.

Clearly label numerical assumptions as hypothetical.

---

# 54. PRODUCTION FAILURE SCENARIOS

Create at least 10 scenarios.

### Scenario 1

A team reduces retention to 24 hours.

Historical queries suddenly fail.

### Scenario 2

A long-running Spark job fails after maintenance.

### Scenario 3

Storage cost doubles despite stable active data.

### Scenario 4

Cleanup removes more files than expected.

### Scenario 5

A historical ML training dataset can no longer be reproduced.

### Scenario 6

An orphan-file cleanup deletes files that another process still needs.

### Scenario 7

Compaction creates large amounts of obsolete data.

### Scenario 8

Snapshot expiration removes required history.

### Scenario 9

Maintenance jobs repeatedly fail.

### Scenario 10

A right-to-delete request requires removal of historical representations.

For every scenario teach:

```text
Symptoms
↓
Possible causes
↓
Investigation
↓
Corrective action
↓
Prevention
```

---

# 55. CROSS-FORMAT COMPARISON

Create a high-level comparison:

| Maintenance Concern | Delta Lake | Iceberg | Hudi |
|---|---|---|---|
| Historical versions | Transaction history | Snapshots | Timeline |
| Physical cleanup | VACUUM-style cleanup | Snapshot/file cleanup mechanisms | Cleaning/retention mechanisms |
| Snapshot expiration | Format-specific | Important concept | Timeline/history retention |
| Orphan files | Format-specific | Important concept | Format-specific |
| Compaction | Supported concepts | Data-file rewrites | Especially important for MOR |
| Maintenance model | Format-specific | Format-specific | Format-specific |

Then explain each row.

Do not imply the commands or safety semantics are identical.

---

# 56. PERFORMANCE AND COST INVESTIGATION

When storage or maintenance costs increase, teach me to investigate:

```text
1. Active data growth
2. Historical data growth
3. Obsolete file growth
4. File count
5. Mutation rate
6. Compaction frequency
7. Clustering frequency
8. Retention period
9. Snapshot/version count
10. Failed jobs
11. Orphan files
12. Cleanup frequency
```

For each explain:

```text
What to measure
Why it matters
What abnormal behavior looks like
Possible remediation
```

---

# 57. VERSION COMPATIBILITY

Before running implementation examples, inspect:

```text
Python
Java
Spark
Delta
Iceberg
Hudi
```

versions.

Maintenance APIs and safety behavior can change between releases.

If a feature is unsupported:

1. identify the limitation
2. explain it
3. do not fake execution
4. use a supported alternative if appropriate
5. clearly state the assumption

---

# 58. CODING REQUIREMENTS

All code must be:

- executable
- minimal
- readable
- version-aware
- safe
- heavily explained

Do not provide destructive commands without first explaining their consequences.

Before any cleanup operation, explicitly state:

```text
WARNING:
This operation can permanently remove historical physical data.
Use only on disposable test data unless the retention policy has been validated.
```

Use dry-run/inspection capabilities where the implementation provides them.

Do not manually delete table files as a shortcut.

---

# 59. PREDICT → INSPECT → EXECUTE → VERIFY

For every maintenance experiment use:

```text
1. Explain
2. Predict
3. Inspect current state
4. Execute maintenance
5. Inspect metadata
6. Inspect physical files
7. Query table
8. Test historical state where appropriate
9. Measure storage impact
10. Explain result
```

Never execute cleanup blindly.

---

# 60. KNOWLEDGE CHECKPOINTS

After every major section ask 2–5 questions.

Examples:

```text
Why do obsolete files exist?

Why can't we immediately delete files that are no longer referenced by the current table?

What is the difference between logical deletion and physical cleanup?

What does VACUUM conceptually do?

Why does retention affect time travel?

Why are long-running readers important?

What is an orphan file?

Why are snapshot expiration and physical file deletion different concepts?

Why can aggressive cleanup cause data loss?

Why does maintenance have a cost?
```

Do not reveal answers immediately.

Let me reason first.

Then provide:

```text
Correct answer
Why it is correct
Common mistake
Production implication
```

---

# 61. BEGINNER → INTERMEDIATE → ADVANCED STRUCTURE

## LEVEL 1 — BEGINNER

Teach:

- physical files
- logical table state
- obsolete files
- retention
- cleanup
- VACUUM
- why cleanup is needed

Goal:

> I understand why lakehouse tables need lifecycle management.

---

## LEVEL 2 — INTERMEDIATE

Teach:

- historical-state dependencies
- time travel + retention
- Delta VACUUM
- Iceberg snapshot expiration
- Hudi cleaning
- orphan files
- maintenance scheduling
- compaction/cleanup lifecycle
- storage cost

Goal:

> I can safely operate basic table-maintenance workflows.

---

## LEVEL 3 — ADVANCED

Teach:

- retention architecture
- long-running readers
- concurrent maintenance
- recovery
- compliance implications
- cost optimization
- automated maintenance
- monitoring
- cross-format differences
- production runbooks
- right-to-delete implications

Goal:

> I can design a production-grade lakehouse table-maintenance and retention strategy.

---

# 62. PRACTICAL EXERCISES

Create at least 12 exercises:

```text
Exercise 1  → Identify obsolete files
Exercise 2  → Understand retention
Exercise 3  → Inspect table history
Exercise 4  → Run safe Delta cleanup
Exercise 5  → Investigate historical availability
Exercise 6  → Understand Iceberg snapshot expiration
Exercise 7  → Investigate orphan files
Exercise 8  → Understand Hudi cleaning
Exercise 9  → Design retention policy
Exercise 10 → Design maintenance schedule
Exercise 11 → Investigate storage-cost growth
Exercise 12 → Build production maintenance runbook
```

For each provide:

```text
Problem
Dataset/environment
Task
Expected reasoning
Success criteria
```

Do not immediately provide solutions.

---

# 63. FINAL CAPSTONE

Build:

# "Production Lakehouse Table Maintenance System"

Architecture:

```text
Data Ingestion
      |
      v
Lakehouse Table
      |
      +----> Compaction
      |
      +----> Clustering
      |
      +----> Version History
      |
      +----> Retention Policy
      |
      +----> Cleanup
      |
      v
Maintenance Monitoring
```

Implement or simulate:

1. continuous writes
2. updates/deletes
3. multiple table versions
4. physical file growth
5. compaction
6. obsolete files
7. retention policy
8. safe cleanup
9. historical-read verification
10. maintenance metrics
11. failure handling
12. storage-cost analysis

The final system must answer:

```text
What can be deleted?
When can it be deleted?
Why is it safe?
What historical states will become unavailable?
How much storage will be reclaimed?
What will maintenance cost?
```

---

# 64. FINAL MAINTENANCE POLICY DOCUMENT

At the end, create a concise production policy containing:

## Table

```text
Table name:
Owner:
Business criticality:
```

## Retention

```text
Operational retention:
Time-travel retention:
Recovery retention:
ML reproducibility retention:
Compliance retention:
```

## Maintenance

```text
Compaction:
Clustering:
Snapshot expiration:
Cleanup:
Orphan-file cleanup:
```

## Safety

```text
Long-running reader buffer:
Maintenance window:
Approval requirements:
Validation:
Rollback/recovery:
```

## Monitoring

```text
Storage:
File count:
Historical window:
Maintenance failures:
Cleanup volume:
```

Explain every field.

---

# 65. FINAL REVIEW

Create a one-page mental model:

```text
Data Changes
      ↓
New Files
      ↓
Old Files Become Obsolete
      ↓
Historical State May Still Need Them
      ↓
Retention Policy
      ↓
Safe Maintenance
      ↓
Cleanup / Expiration
      ↓
Storage Reclaimed
      ↓
Historical Window Reduced
```

Then create a glossary for:

- obsolete file
- orphan file
- retention
- retention window
- VACUUM
- cleanup
- snapshot expiration
- compaction
- clustering
- table history
- historical state
- long-running reader
- maintenance window
- storage lifecycle
- data lifecycle

---

# 66. INTERVIEW PREPARATION

Create:

### 10 Beginner Questions

Focused on:

- retention
- obsolete files
- cleanup
- VACUUM

### 10 Intermediate Questions

Focused on:

- time travel
- historical files
- Delta/Iceberg/Hudi maintenance
- orphan files
- maintenance scheduling

### 10 Advanced Questions

Focused on:

- production retention architecture
- long-running readers
- cost optimization
- compliance
- failure recovery
- automated maintenance
- cross-format design

Every advanced question must introduce a realistic engineering problem.

Provide model senior-engineer answers.

---

# 67. FINAL ASSESSMENT

Create:

## Part A — Concepts

10 questions.

## Part B — Code

5 practical questions.

## Part C — Debugging

5 maintenance incidents.

## Part D — Architecture

3 production design problems.

## Part E — Trade-offs

5 retention/maintenance decisions.

Do not give the answers immediately.

Evaluate my answers after I attempt them.

---

# 68. FINAL EXIT CRITERIA

Do not consider this lesson complete until I can independently explain:

1. Why obsolete files accumulate.
2. Logical table state vs physical storage.
3. What an obsolete file is.
4. What an orphan file is.
5. Why cleanup is necessary.
6. What retention means.
7. How retention affects time travel.
8. What VACUUM conceptually does.
9. VACUUM vs DELETE.
10. Compaction vs cleanup.
11. Clustering vs cleanup.
12. Delta VACUUM concepts.
13. Iceberg snapshot expiration.
14. Iceberg orphan-file cleanup.
15. Hudi cleaning.
16. How long-running readers affect retention.
17. How failed jobs can create orphan files.
18. How maintenance interacts with compaction.
19. How maintenance interacts with clustering.
20. How to design a safe retention window.
21. How to calculate retention/storage trade-offs.
22. How to monitor maintenance.
23. How to design automated maintenance.
24. How to troubleshoot failed cleanup.
25. How to handle historical-data requirements.
26. How to reason about compliance/data-deletion implications.
27. How Delta, Iceberg, and Hudi differ conceptually in maintenance.
28. How to build a production maintenance runbook.
29. How to safely validate a cleanup operation.
30. How to defend a retention policy to a production engineering team.

---

# 69. FINAL TEACHING PRINCIPLE

Throughout the entire lesson follow this principle:

> **Table maintenance is a lifecycle-management problem, not a collection of cleanup commands.**

Always reason through:

```text
Table State
    ↓
Physical Files
    ↓
File Changes
    ↓
Obsolete Files
    ↓
Historical Dependencies
    ↓
Retention Policy
    ↓
Safety Validation
    ↓
Maintenance
    ↓
Cleanup
    ↓
Verification
    ↓
Monitoring
```

Whenever you show a command such as:

```text
VACUUM
```

or:

```text
expire snapshots
```

or:

```text
clean
```

always explain:

```text
What exactly is being removed?
Why is it eligible?
Which table states depend on it?
Could a reader still need it?
What retention policy permits removal?
What historical access will be lost?
What storage will be reclaimed?
What happens if the operation fails?
How do we verify that the operation was safe?
```

Never teach:

> "VACUUM deletes old files."

Instead teach:

> **"VACUUM or an equivalent cleanup mechanism removes physical data that has become eligible for deletion under the table format's retention and safety model. The operation must be designed around historical-state requirements, active readers, recovery requirements, and the specific table format's semantics."**

The final outcome should be that I can **design, implement, monitor, troubleshoot, and safely operate production lakehouse table-maintenance workflows**, including retention, obsolete-file cleanup, historical-state preservation, storage-cost management, and safe lifecycle policies across Delta Lake, Apache Iceberg, and Apache Hudi.