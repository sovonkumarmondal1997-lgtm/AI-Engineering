# Roadmap — Module 2.15: Lakehouse Table Formats

This is the learning roadmap for the fifteenth module of Stage 2, **Python
for Data Engineering**. It tells you **what** to learn about open table
formats and the lakehouse, **in what order**, **how** to learn each topic,
and **how to prove to yourself** that you have learned it before you move
on.

Throughout Stage 2 you hit the same wall from different directions. In
Module 2.5, compaction on plain Parquet files was unsafe with concurrent
readers. In Module 2.12, partition overwrites needed temp-then-swap tricks.
In Module 2.14, you killed a Spark write halfway and readers saw partial
data. A directory of Parquet files is **not a table**: it has no
transactions, no reliable updates or deletes, no history, and no safe way
to change its layout.

**Open table formats** — Delta Lake, Apache Iceberg, and Apache Hudi — fix
this by adding a metadata layer on top of Parquet files in object storage:
atomic commits, `MERGE` / `UPDATE` / `DELETE`, schema evolution, time
travel, and safe maintenance. Together with a **catalog**, they turn a data
lake into a **lakehouse**: warehouse-like reliability on open files that
many engines can read. This module teaches how they work inside, how to
operate them, and how to choose between them.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain the problems of plain file-based data lakes and how open table
  formats solve them.
- Explain **Delta Lake's transaction log**: commits, actions, checkpoints,
  protocol and table features, and optimistic concurrency.
- Explain **Apache Iceberg's metadata tree**: table metadata, snapshots,
  manifest lists, manifests, delete files, hidden partitioning, and
  partition evolution.
- Explain **Apache Hudi's** timeline, table types (copy-on-write and
  merge-on-read), and where it fits.
- Run **ACID `MERGE`, `UPDATE`, and `DELETE`** on lake tables from Spark and
  from Python, and handle concurrent writers.
- Use **time travel**, restore, change feeds, branches, and tags for
  auditing, reproducibility, recovery, and write–audit–publish.
- Keep tables fast with **compaction, sorting, Z-ordering, and liquid
  clustering**.
- Keep tables cheap and compliant with **vacuum, snapshot expiry,
  retention, and orphan-file cleanup**.
- Explain and choose **catalogs** — Hive Metastore, AWS Glue, Unity
  Catalog, Apache Polaris, and Iceberg REST catalogs — for multi-engine
  access and governance.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.14. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Filesystems, atomic rename, object storage behaviour | Stage 0 / Stage 1 — Module 1.10 (safe file writes) | Why atomic commits on object storage need a metadata layer |
| Warehouse vs lake vs lakehouse, medallion layers | Stage 2 — Module 2.1 | This module builds the lakehouse concretely |
| Arrow, DuckDB and Polars over files, object storage with MinIO | Stage 2 — Module 2.4 | Non-Spark engines reading table formats |
| Parquet internals, statistics, partitioning, small files, Avro | Stage 2 — Module 2.5 | Table formats are metadata over these files; **not** re-taught |
| SQL `MERGE`, transactions, isolation, SCD Type 2 | Stage 2 — Module 2.6 | Semantics carried over to lake tables |
| SCD types, grain, event data | Stage 2 — Module 2.8 | Modelling what you store in the tables |
| CDC events, deletes, incremental extraction | Stage 2 — Module 2.9 | Applying changes to lake tables |
| Schema evolution rules, WAP, quarantine | Stage 2 — Module 2.11 | Implemented natively by table formats |
| Merge-based loads, incremental processing, backfills, state | Stage 2 — Module 2.12 | Patterns re-implemented on tables |
| Scheduling maintenance, backfills | Stage 2 — Module 2.13 | Table maintenance jobs are orchestrated |
| Spark DataFrames, SQL, partitioning, AQE, save modes, the atomicity problem | Stage 2 — Module 2.14 | Spark is the main engine in this module |

**Tools needed:**

- PySpark 4.x with the **Delta Lake** Spark package and the **Iceberg**
  Spark runtime package — use versions documented as compatible with your
  Spark version.
- Python-native libraries: **`deltalake`** (delta-rs) and **`pyiceberg`**
  (with its SQL/SQLite catalog for local work, and PyArrow).
- **DuckDB** (with its `delta` and `iceberg` extensions) and **Polars**
  (`scan_delta`, `scan_iceberg`) for multi-engine reads.
- MinIO in Docker as object storage.
- An **Iceberg REST catalog** in Docker (for example Apache Polaris or
  another open-source REST catalog implementation) for Topic 09.
- Optionally **Apache Hudi** via its Spark bundle for Topic 04.

**A note on versions:** table formats evolve quickly (Delta Lake table
features, the Iceberg format-version 3 specification, Hudi 1.x, and new
catalog projects). Engine support differs by version: an engine may read a
table but not write it, or may not support a newer table feature. Always
check the compatibility matrix of every engine you use against the table
features you enable.

---

## 3. How the module is organised

The nine topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — The Problem                                (Basics)
  01 Why open table formats exist

Phase B — Inside the Three Formats                   (Intermediate → Advanced)
  02 Delta Lake transaction log
  03 Apache Iceberg snapshots and manifests
  04 Apache Hudi overview

Phase C — Working with Tables                        (Intermediate → Advanced)
  05 ACID merge, update, and delete on data lakes
  06 Time travel and table versioning

Phase D — Keeping Tables Healthy                     (Advanced)
  07 Compaction, Z-ordering, and liquid clustering
  08 Vacuum, retention, and table maintenance

Phase E — The Catalog Layer                          (Advanced)
  09 Catalogs: Hive Metastore, Glue, Unity, and Polaris

Consolidate
  practice-questions.md
  Module mini-project: an operated, multi-engine lakehouse
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07 ──► 08 ──► 09
why     Delta   Iceberg Hudi    change  go back fast    cheap &  find and
tables  log     tree    timeline data    in time layout compliant govern
                                safely                           tables
```

Why this order:

- The problem (01) comes first so every feature has a reason.
- Delta (02) has the simplest internal model (an ordered log of JSON
  commits), so it is the easiest way to learn how table formats work;
  Iceberg (03) and Hudi (04) are then understood by comparison.
- Row-level changes (05) and time travel (06) are the everyday features.
- Maintenance (07–08) is what keeps those features fast and affordable.
- Catalogs (09) come last because they sit above tables of every format
  and decide how engines find, commit to, and govern them.

---

## 4. Suggested schedule

About **4 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — why table formats · Topic 02 — Delta transaction log |
| 2 | Topic 03 — Iceberg snapshots and manifests · Topic 04 — Hudi overview |
| 3 | Topic 05 — merge, update, delete · Topic 06 — time travel · Topic 07 — compaction and clustering |
| 4 | Topic 08 — vacuum and maintenance · Topic 09 — catalogs · practice questions · mini-project |

---

## 5. How to study every topic (the table-format loop)

```text
Read → Predict the metadata change → Run the operation → Inspect the files
→ Read the table from another engine → Break it (concurrency, crash, deletion)
→ Measure files, bytes, and time → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Predict** exactly which files will be added, removed, or rewritten,
   and which metadata files will change, before any operation.
3. **Run the operation** (create, append, `MERGE`, `DELETE`, `OPTIMIZE`,
   `VACUUM`, …) with Spark or a Python library.
4. **Inspect the files** in MinIO: data files, log or metadata files,
   manifests — and the table's own history and metadata tables.
5. **Read the table from another engine** (DuckDB, Polars, PyIceberg,
   delta-rs) to confirm interoperability.
6. **Break it**: concurrent writers, a job killed mid-commit, a reader
   using an old version while maintenance runs.
7. **Measure** file counts, file sizes, bytes scanned, and query time
   before and after.
8. **Write down** the rule you learned in `module-2.15-notes.md`.
9. **Explain aloud** what happened in the metadata, step by step.

Keep one `lakehouse_lab/` project:

```text
lakehouse_lab/
├── docker-compose.yml   # MinIO, REST catalog, (optional) Spark cluster
├── conf/                # Spark configs for Delta and Iceberg
├── src/lakehouse_lab/   # table creation, loads, maintenance, inspection tools
├── notebooks_or_scripts/# step-by-step experiments per topic
└── tests/
```

---

## 6. Phase A — The Problem (Basics)

### Topic 01 — [Why open table formats exist](01-why-open-table-formats-exist.md)

**Why it comes first:** Every feature of a table format solves a specific
failure of plain files. Seeing those failures clearly makes the rest of the
module make sense.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | A directory of Parquet files is a *dataset*, not a *table*: no transactions, no schema enforcement, no history |
| Basics | Problems of plain lakes: partial writes visible to readers, no atomic multi-file commits, no row-level updates or deletes, unsafe concurrent writers, schema drift across files, expensive directory listings, the small-files problem |
| Basics | The idea of a table format: a **metadata layer** that records exactly which files make up each version of a table |
| Intermediate | Features table formats add: **ACID transactions**, **snapshot isolation** for readers, **`MERGE` / `UPDATE` / `DELETE`**, schema enforcement and evolution, **time travel**, and file-level statistics for data skipping |
| Intermediate | The lakehouse architecture: open files + table format + catalog + many engines (Spark, Trino, DuckDB, Flink, warehouses) |
| Intermediate | The three main formats — **Delta Lake**, **Apache Iceberg**, **Apache Hudi** — and their origins and communities |
| Advanced | Hive-style tables (directory partitions in a metastore) as the predecessor, and why they were not enough |
| Advanced | Interoperability efforts: reading one format as another (e.g. Delta UniForm, Apache XTable) and converging features across formats |
| Advanced | Where table formats fit vs cloud warehouses (Module 2.17) and when plain Parquet is still fine (write-once, read-only datasets) |

**How to learn it**

1. Read the topic file.
2. Reproduce three plain-lake failures from earlier modules: a partial
   write seen by a reader, a lost update from two concurrent writers, and
   an impossible row-level delete.
3. List, for each failure, the table-format feature that solves it.

**Hands-on exercise — `experiments/01_plain_lake_failures/`**

1. With Spark, write a Parquet dataset to MinIO and kill the job halfway;
   read it with DuckDB and document what is visible.
2. Run two concurrent overwrites of the same partition; document the
   result.
3. Try to delete one customer's rows from a 1-billion-row Parquet dataset;
   estimate the rewrite cost.
4. Repeat steps 1–2 with a Delta table and an Iceberg table and document
   the difference.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain why a directory of files is not a table.
- [ ] List the features table formats add and the problem each solves.
- [ ] Describe the lakehouse architecture.
- [ ] Name the three main formats and their origins.

**Common mistakes:** believing table formats are new *file* formats (they
still store Parquet); assuming every engine supports every format feature;
using table formats for data that never changes.

---

## 7. Phase B — Inside the Three Formats (Intermediate → Advanced)

### Topic 02 — [Delta Lake transaction log](02-delta-lake-transaction-log.md)

**Why here:** Delta's design — an ordered log of commits next to the data
files — is the clearest way to understand how any table format provides
transactions on object storage.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Table layout: Parquet data files plus the `_delta_log/` directory of numbered JSON commit files |
| Basics | Creating, appending to, and overwriting Delta tables from Spark and from Python (`deltalake` / delta-rs) |
| Basics | `DESCRIBE HISTORY` and reading the log with delta-rs |
| Intermediate | **Actions** in a commit: `add` (with file statistics), `remove`, `metaData` (schema, partitioning, configuration), `protocol`, `commitInfo`, and `txn` (application transaction ids) |
| Intermediate | Reconstructing a table version: replaying commits from the latest **checkpoint** (Parquet summaries written periodically) |
| Intermediate | **Optimistic concurrency**: writers read a version, write new files, and try to commit the next log entry atomically; conflicts are detected and retried or rejected |
| Intermediate | Schema **enforcement** (reject mismatched writes) and **evolution** (`mergeSchema`, adding columns), plus `CHECK` constraints, `NOT NULL`, and generated columns |
| Advanced | **Protocol versions and table features** (e.g. deletion vectors, column mapping, change data feed, clustering, type widening, `VARIANT`): what enabling a feature means for which engines can still read or write the table |
| Advanced | Atomic commits on object storage: how "put if absent" or a coordination service makes log commits safe, and why some storage setups need extra configuration |
| Advanced | Idempotent writes with application transaction ids (useful for retries from orchestrators and streams) |
| Advanced | Reading Delta tables without Spark: delta-rs, DuckDB's `delta` extension, Polars `scan_delta` |

**How to learn it**

1. Read the topic file.
2. Create a Delta table and perform ten operations (append, overwrite,
   schema change, delete, update, `OPTIMIZE`); after each, open the new
   JSON commit and write down every action.
3. Draw how a reader reconstructs version 12 from a checkpoint at version
   10 plus commits 11 and 12.

**Hands-on exercise — `src/lakehouse_lab/delta_internals.py`**

1. Write a small **log reader** in Python that lists commits, operations,
   files added and removed per version, and the current file set — then
   compare it with `DESCRIBE HISTORY` and delta-rs's view.
2. Run two concurrent writers (Spark and delta-rs, or two Spark jobs)
   appending and updating the same table; observe conflicts and retries.
3. Enable a table feature (e.g. deletion vectors) and check which of your
   readers (DuckDB, Polars, delta-rs) still read the table.
4. Enforce a schema: show a rejected write, then an allowed schema
   evolution.
5. Add a `CHECK` constraint and show a violating write being rejected.

**Checkpoint:**

- [ ] Describe the `_delta_log` structure and the main actions.
- [ ] Explain how checkpoints speed up reading the log.
- [ ] Explain optimistic concurrency and conflicts.
- [ ] Explain table features and their compatibility impact.
- [ ] Read and write Delta tables with and without Spark.

**Common mistakes:** editing files inside a table directory by hand;
enabling table features without checking reader support; assuming schema
evolution is on by default.

---

### Topic 03 — [Apache Iceberg snapshots and manifests](03-apache-iceberg-snapshots-and-manifests.md)

**Why here:** Iceberg takes a different approach: a tree of metadata files
and a catalog pointer, designed for very large tables and many engines.
It is the format most broadly adopted across vendors and warehouses.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The metadata tree: **catalog pointer** → **table metadata file** (JSON) → **snapshots** → **manifest list** (Avro) → **manifest files** (Avro) → **data files** (Parquet) |
| Basics | Creating and writing Iceberg tables from Spark and from Python (`pyiceberg` with a local SQL catalog) |
| Basics | **Metadata tables**: `snapshots`, `history`, `files`, `manifests`, `partitions` — querying the table about itself |
| Intermediate | How a commit works: write new data and metadata files, then atomically swap the catalog's pointer to the new table metadata (the catalog is the commit point) |
| Intermediate | **Hidden partitioning**: partition transforms (`day(ts)`, `month(ts)`, `bucket(n, col)`, `truncate(n, col)`) so queries filter on real columns and never on partition columns |
| Intermediate | **Partition evolution**: changing the partition scheme without rewriting old data |
| Intermediate | **Schema evolution with column ids**: safe add, drop, rename, reorder, and type widening |
| Intermediate | Manifest-level and file-level statistics for pruning, and why queries rarely list directories |
| Advanced | **Row-level deletes** in format version 2: position delete files and equality delete files; copy-on-write vs merge-on-read write modes |
| Advanced | Format version 3 (awareness): deletion vectors, row lineage, new types such as `VARIANT`, default values — and engine support |
| Advanced | Sort orders defined on the table and their effect on writes |
| Advanced | Reading Iceberg without Spark: PyIceberg to Arrow, DuckDB's `iceberg` extension, Polars `scan_iceberg`; and support in warehouses and query engines (Module 2.17) |

**How to learn it**

1. Read the topic file.
2. Create an Iceberg table, append three times, delete some rows, and
   evolve the partition scheme; after each step, open the metadata JSON,
   manifest list, and manifests (Avro, readable with tools from Module 2.5)
   and draw the tree.
3. Query every metadata table after each step.

**Hands-on exercise — `src/lakehouse_lab/iceberg_internals.py`**

1. Create `silver.trips` with hidden partitioning `day(pickup_ts)`; show
   that a filter on `pickup_ts` prunes files without mentioning a partition
   column.
2. Evolve the partitioning from `day` to `month` for new data; query across
   both layouts.
3. Rename and add columns and show old files are still read correctly
   (column ids).
4. Delete rows in merge-on-read mode and inspect the delete files; then
   rewrite in copy-on-write mode and compare files and read speed.
5. Write the same data with PyIceberg (from a PyArrow table) and read it in
   Spark, DuckDB, and Polars.

**Checkpoint:**

- [ ] Draw Iceberg's metadata tree from memory.
- [ ] Explain why the catalog pointer swap is the commit.
- [ ] Explain hidden partitioning and partition evolution.
- [ ] Explain position vs equality deletes and copy-on-write vs
      merge-on-read.
- [ ] Read and write Iceberg tables from Python and Spark.

**Common mistakes:** adding explicit date columns to partition on instead
of using transforms; forgetting that the catalog is required; letting
merge-on-read delete files pile up without compaction.

---

### Topic 04 — [Apache Hudi overview](04-apache-hudi-overview.md)

**Why here:** Hudi was built for fast upserts and incremental processing on
lakes — especially CDC-heavy workloads. You may meet it in existing
platforms, so you need to understand its model and trade-offs even if you
choose Delta or Iceberg.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Hudi's purpose: record-level upserts and deletes with incremental pulls on data lakes |
| Basics | **Record keys**, partition paths, and the **precombine / ordering field** that decides which version of a record wins |
| Basics | The **timeline**: instants (commits, delta commits, compactions, cleans, rollbacks) stored under `.hoodie/` |
| Intermediate | **Table types**: **copy-on-write** (rewrite Parquet files on update — fast reads) vs **merge-on-read** (append updates to log files, merge later — fast writes) |
| Intermediate | **Query types**: snapshot, read-optimised, and **incremental** queries (changes since an instant) |
| Intermediate | Write operations: `upsert`, `insert`, `bulk_insert`, `delete`, `insert_overwrite` |
| Intermediate | **Indexes** for locating records (e.g. bloom, simple, bucket, and record-level indexes) and the metadata table |
| Advanced | **Table services**: compaction, clustering, and cleaning — inline vs asynchronous |
| Advanced | Concurrency control options and the direction of recent Hudi versions |
| Advanced | Comparing Hudi with Delta and Iceberg: strengths (upsert-heavy CDC, incremental pulls) vs ecosystem breadth and Python-native tooling |

**How to learn it**

1. Read the topic file.
2. If using Hudi: create copy-on-write and merge-on-read tables from Spark,
   upsert a CDC stream (from Module 2.9), and compare files and read times.
3. If not installing Hudi: study its documentation's diagrams and map every
   concept to its Delta and Iceberg equivalent.

**Hands-on exercise — `experiments/04_hudi/`**

1. Upsert 10 batches of CDC changes into a copy-on-write table and a
   merge-on-read table; record write time, read time, and file counts.
2. Run an incremental query returning only records changed since a chosen
   instant.
3. Run compaction on the merge-on-read table and observe the timeline.
4. Fill in a comparison table: Delta vs Iceberg vs Hudi (commit model,
   row-level change mechanism, partitioning, incremental reads, Python
   support, engine ecosystem, maintenance).

**Checkpoint:**

- [ ] Explain record keys, the ordering field, and the timeline.
- [ ] Explain copy-on-write vs merge-on-read in Hudi.
- [ ] Explain incremental queries and table services.
- [ ] Compare Hudi with Delta and Iceberg.

**Common mistakes:** choosing merge-on-read without scheduling compaction;
a wrong ordering field so old records win; comparing formats only on
feature lists instead of on your workload.

---

## 8. Phase C — Working with Tables (Intermediate → Advanced)

### Topic 05 — [ACID merge, update, and delete on data lakes](05-acid-merge-update-and-delete-on-data-lakes.md)

**Why here:** The biggest practical gain from table formats is changing
data in place — upserting CDC changes, maintaining SCD dimensions, and
deleting a person's data on request — with transactional guarantees.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `MERGE INTO`, `UPDATE`, and `DELETE` in Spark SQL on Delta and Iceberg tables (SQL semantics from Module 2.6) |
| Basics | Python-native equivalents: delta-rs merge, update, and delete; PyIceberg delete, overwrite with a filter, and upsert |
| Basics | Replacing a partition or a filtered range atomically (e.g. `replaceWhere`-style overwrites, dynamic overwrites) |
| Intermediate | How row-level changes are stored: **copy-on-write** (rewrite affected files) vs **merge-on-read** (delete files or deletion vectors plus new files) — write cost vs read cost |
| Intermediate | Applying **CDC** to lake tables: deduplicate and order changes per key, then one `MERGE` with inserts, updates, and deletes (patterns from Modules 2.9 and 2.12) |
| Intermediate | **SCD Type 2** dimensions on lake tables |
| Intermediate | Merge performance: restricting the target with partition or clustering predicates, file pruning, and avoiding full-table rewrites |
| Advanced | **Concurrency**: isolation levels offered by each format, conflicts between concurrent `MERGE`s or between a `MERGE` and compaction, retries, and designing writers to avoid conflicts (partition-scoped writes, single writer per table) |
| Advanced | Idempotent and exactly-once writes (transaction ids, `MERGE` conditions that make replays harmless) |
| Advanced | **Right-to-be-forgotten deletes**: logical delete, then physical removal of old files through vacuum or expiry (Topic 08) — and proving the data is gone |
| Advanced | Change data feeds and incremental reads for downstream consumers (Delta change data feed, Iceberg incremental reads, Hudi incremental queries) |

**How to learn it**

1. Read the topic file.
2. For one `MERGE`, predict how many files will be rewritten in
   copy-on-write and merge-on-read modes; measure.
3. Run two concurrent merges into the same table and document the result
   in each format.

**Hands-on exercise — `src/lakehouse_lab/merges.py`**

1. Apply 30 days of CDC events (from Module 2.9) to `silver.customers` with
   `MERGE` in Delta and Iceberg; prove the result equals the source
   database.
2. Maintain `gold.dim_customer` as SCD Type 2 with `MERGE`.
3. Implement the same upsert with delta-rs and with PyIceberg from Python
   (no Spark) on a smaller table.
4. Compare copy-on-write and merge-on-read for a workload with many small
   updates: write time, files created, and read time.
5. Run two concurrent writers updating different partitions and then the
   same partition; handle conflicts with retries.
6. Delete one customer everywhere (bronze, silver, gold) and document what
   still exists in old files until Topic 08.

**Checkpoint:**

- [ ] Run `MERGE`, `UPDATE`, and `DELETE` on Delta and Iceberg tables.
- [ ] Explain copy-on-write vs merge-on-read for row-level changes.
- [ ] Apply CDC changes and SCD Type 2 correctly.
- [ ] Handle concurrent writers and conflicts.
- [ ] Explain why a delete is not immediately a physical deletion.

**Common mistakes:** merging undeduplicated CDC batches; merges that scan
the entire table daily; concurrent jobs writing the same partitions with
no conflict handling; telling compliance teams data is deleted before
old files are removed.

---

### Topic 06 — [Time travel and table versioning](06-time-travel-and-table-versioning.md)

**Why here:** Because every commit produces a new version, you can read
the table as it was, undo mistakes, reproduce past results, and publish
changes safely.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Reading old versions: by version number or snapshot id, and by timestamp (Spark SQL `VERSION AS OF` / `TIMESTAMP AS OF`, and Python library equivalents) |
| Basics | Table history: who changed what, when, with which operation |
| Basics | **Restore / rollback** to a previous version after a bad write |
| Intermediate | Use cases: auditing, debugging "what changed?", reproducible reports, and pinning ML training data to an exact version |
| Intermediate | Comparing versions to find changed rows (diffing two snapshots) |
| Intermediate | **Change feeds**: Delta's change data feed and Iceberg's incremental/changelog reads for downstream incremental processing |
| Advanced | **Branches and tags** (Iceberg): named snapshots for releases and audits; isolated branches for experiments |
| Advanced | **Write–audit–publish** natively (Module 2.11): write to a branch or staged snapshot, run checks, then publish by fast-forwarding or cherry-picking |
| Advanced | Cloning tables (e.g. Delta shallow and deep clones) for testing and experiments |
| Advanced | The limit of time travel: retention and vacuum (Topic 08) decide how far back you can go |
| Advanced | Bitemporal questions (Module 2.12) and how table versions help answer "what did we know on date X?" |

**How to learn it**

1. Read the topic file.
2. Perform a sequence of writes and a deliberate "bad" write; find it in
   history, inspect the difference, and roll back.
3. Pin a report to a table version and show it stays identical while the
   table keeps changing.

**Hands-on exercise — `src/lakehouse_lab/time_travel.py`**

1. Build a `diff_versions(table, v1, v2)` tool that returns inserted,
   deleted, and changed rows between two versions.
2. Simulate a bad transformation deploy that corrupts `gold.daily_revenue`;
   detect it, compare versions, and restore.
3. Create an ML training dataset pinned to a tag or version and record it
   in run metadata.
4. Implement WAP with Iceberg branches: write the daily load to an audit
   branch, run your Module 2.11 checks against the branch, and publish only
   if they pass.
5. Consume Delta's change data feed to update a downstream aggregate
   incrementally.

**Checkpoint:**

- [ ] Read tables as of a version or timestamp.
- [ ] Restore a table after a bad write.
- [ ] Use change feeds for incremental consumers.
- [ ] Implement WAP with branches or staged commits.
- [ ] Explain how retention limits time travel.

**Common mistakes:** treating time travel as a backup strategy (vacuum
removes old files); relying on timestamps when versions are exact;
forgetting to record which version a report or model used.

---

## 9. Phase D — Keeping Tables Healthy (Advanced)

### Topic 07 — [Compaction, Z-ordering, and liquid clustering](07-compaction-z-ordering-and-liquid-clustering.md)

**Why here:** Streaming appends, frequent merges, and merge-on-read deletes
all create many small files and scattered data. Table formats let you fix
layout **transactionally**, while readers keep working.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why tables degrade: small files, delete files and deletion vectors accumulating, poorly clustered data (the problems from Module 2.5, now fixable safely) |
| Basics | **Compaction** (bin-packing small files into target-sized files): Delta `OPTIMIZE`, Iceberg `rewrite_data_files`, Hudi compaction and clustering |
| Basics | Compaction as a normal commit: readers are never broken |
| Intermediate | **Sorting and clustering** data within files so statistics prune effectively (sort orders from Module 2.5) |
| Intermediate | **Z-ordering**: multi-column clustering that keeps rows close in several dimensions; `OPTIMIZE ... ZORDER BY` and Iceberg's z-order rewrite strategy |
| Intermediate | **Liquid clustering** (Delta): declaring clustering keys (`CLUSTER BY`), incremental clustering, and changing keys without a full rewrite — as an alternative to partitioning plus Z-ordering |
| Intermediate | Rewriting manifests / metadata to speed up planning on very large tables (e.g. Iceberg `rewrite_manifests`) |
| Advanced | Choosing clustering columns: the most common filters and join keys; how many columns are useful; interaction with partitioning (coarse partitions + clustering) |
| Advanced | Write-time optimisations (optimised writes, auto-compaction, target file sizes) vs scheduled compaction |
| Advanced | Conflicts between compaction and concurrent writers, and how each format handles them |
| Advanced | Cost and scheduling: compacting only recent or frequently queried partitions; measuring the benefit in bytes scanned |

**How to learn it**

1. Read the topic file.
2. Degrade a table on purpose with thousands of small appends and many
   merge-on-read deletes; record file counts and query times.
3. Apply compaction, then sorting, then Z-ordering or liquid clustering,
   measuring after each step.

**Hands-on exercise — `src/lakehouse_lab/layout.py`**

1. Build a `table_health(table)` report: file count, size distribution,
   delete files or deletion vectors, snapshot count, and manifest count.
2. Degrade `silver.trips` with 5,000 small appends; compact it to target
   file sizes in Delta and Iceberg; compare before/after health and query
   time.
3. Z-order (or sort) the table by `pickup_zone` and `pickup_ts`; measure
   files skipped for typical filters using query plans (Module 2.14).
4. Convert a Delta table to liquid clustering, change its clustering keys,
   and measure the effect.
5. Run compaction while another job is appending; observe conflict
   handling.

**Checkpoint:**

- [ ] Explain why tables degrade and how compaction fixes them.
- [ ] Explain sorting, Z-ordering, and liquid clustering.
- [ ] Choose clustering columns from query patterns.
- [ ] Measure the benefit of layout changes.

**Common mistakes:** Z-ordering on too many or rarely-filtered columns;
compacting the whole table every hour; forgetting merge-on-read delete
files; partitioning finely *and* clustering, fighting each other.

---

### Topic 08 — [Vacuum, retention, and table maintenance](08-vacuum-retention-and-table-maintenance.md)

**Why here:** Every commit keeps old files for time travel. Without
cleanup, storage costs grow forever and deleted personal data is never
physically removed. With careless cleanup, you break readers and lose
history you needed.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why old files accumulate: every rewrite (merge, compaction, overwrite) leaves the previous files for time travel |
| Basics | **Delta `VACUUM`**: removing files no longer referenced by versions within the retention period; the default retention and the safety check against short retention |
| Basics | **Iceberg snapshot expiry** (`expire_snapshots`) and **orphan file removal** (`remove_orphan_files`) |
| Intermediate | Log and metadata retention: Delta log cleanup and checkpoints; Iceberg metadata file limits and cleanup settings |
| Intermediate | Choosing retention: time-travel needs (audits, debugging, reproducibility) vs storage cost vs compliance deadlines |
| Intermediate | The danger of short retention: long-running readers or writers failing because files they need were deleted |
| Intermediate | **Physical deletion for compliance**: delete rows → rewrite files → vacuum/expire past versions → verify no file containing the data remains |
| Advanced | Orphan files from failed writes and why removing them requires a safe age threshold |
| Advanced | **A maintenance plan per table**: compaction, clustering, snapshot expiry, orphan cleanup, manifest rewrites, statistics — with schedules based on write patterns |
| Advanced | Orchestrating maintenance with Airflow or Dagster (Module 2.13), with locks or scheduling to avoid conflicts with writers |
| Advanced | Monitoring table health and storage over time (Module 2.20); managed "predictive" maintenance features on vendor platforms (awareness) |

**How to learn it**

1. Read the topic file.
2. Calculate storage growth for a table with daily full-partition
   rewrites and 30-day retention.
3. Run vacuum with a very short retention while a long query is reading an
   old version (in your lab only) and observe the failure.

**Hands-on exercise — `src/lakehouse_lab/maintenance.py`**

1. Measure storage for `silver.customers` after 30 days of merges, then run
   `VACUUM` (Delta) and `expire_snapshots` + `remove_orphan_files` (Iceberg)
   with a chosen retention; measure again.
2. Complete the right-to-be-forgotten flow from Topic 05: delete the
   customer, expire or vacuum, then prove (by scanning every remaining data
   file) that no copy of their rows remains.
3. Create orphan files by killing a write, then remove them safely.
4. Write a maintenance policy per table (bronze, silver, gold) and
   implement it as a maintenance DAG in Airflow or Dagster.
5. Show time travel failing for a version older than retention, and explain
   it to a stakeholder.

**Checkpoint:**

- [ ] Explain vacuum, snapshot expiry, and orphan cleanup.
- [ ] Choose retention periods and justify them.
- [ ] Physically delete personal data and prove it.
- [ ] Design and orchestrate a table maintenance plan.

**Common mistakes:** never vacuuming (unbounded storage); disabling the
retention safety check casually; running orphan cleanup with a short
threshold while writes are in progress; assuming `DELETE` satisfies
compliance by itself.

---

## 10. Phase E — The Catalog Layer (Advanced)

### Topic 09 — [Catalogs: Hive Metastore, Glue, Unity, and Polaris](09-catalogs-hive-metastore-glue-unity-and-polaris.md)

**Why last:** Tables need names, discovery, and — for Iceberg — a place to
commit. The catalog is also where access control and governance live, and
it decides which engines can work with your lakehouse.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What a catalog does: maps names (`catalog.schema.table`) to table metadata locations; lists namespaces and tables |
| Basics | For Iceberg, the catalog is the **commit coordinator** (atomic pointer swap); for Delta, the log itself is the source of truth and the catalog mainly provides names and governance |
| Basics | Three-level namespaces and how engines configure catalogs |
| Intermediate | **Hive Metastore (HMS)**: the long-standing Thrift service backed by a relational database; strengths and limits |
| Intermediate | **AWS Glue Data Catalog**: managed metastore on AWS (Module 2.17) |
| Intermediate | **Unity Catalog**: governance-centred catalog from Databricks, also available as an open-source project — permissions, lineage, and multi-format tables |
| Intermediate | **Iceberg REST catalog specification** and implementations such as **Apache Polaris** (and other open-source REST catalogs); why a standard catalog API enables many engines |
| Intermediate | Simple catalogs for development: file- or SQL-based catalogs (e.g. PyIceberg's SQL catalog on SQLite) |
| Advanced | **Governance** through catalogs: access control on catalogs, schemas, and tables; **credential vending** (engines receive short-lived storage credentials from the catalog instead of holding long-lived keys) |
| Advanced | Multi-engine access: Spark writes, Trino/DuckDB/Polars/warehouses read — and what each engine supports per catalog |
| Advanced | Versioned catalogs (Git-like branching across many tables, e.g. Project Nessie) — awareness |
| Advanced | Newer approaches that store table metadata in a database (e.g. DuckLake) and managed table offerings from cloud providers — awareness |
| Advanced | Choosing a catalog: formats, engines, cloud, governance needs, open standards, and lock-in |

**How to learn it**

1. Read the topic file.
2. Run an Iceberg REST catalog in Docker, connect Spark, PyIceberg, and
   DuckDB to it, and create, write, and read tables from each.
3. Draw your lakehouse with the catalog in the centre: engines, storage,
   credentials, and permissions.

**Hands-on exercise — `catalog/`**

1. Start an Iceberg REST catalog (for example Apache Polaris) backed by
   MinIO; create `bronze`, `silver`, and `gold` namespaces.
2. Write tables from Spark; read them from PyIceberg, DuckDB, and Polars
   through the same catalog.
3. Configure a read-only principal for analysts and a read-write principal
   for pipelines; show a denied write.
4. Configure credential vending (if your catalog supports it) so engines do
   not hold long-lived MinIO keys.
5. Compare with a Hive-Metastore-style setup (or PyIceberg's SQL catalog)
   and write a catalog decision record.

**Checkpoint:**

- [ ] Explain what catalogs do for Delta and for Iceberg.
- [ ] Compare Hive Metastore, Glue, Unity Catalog, and Iceberg REST
      catalogs such as Polaris.
- [ ] Connect several engines to one catalog.
- [ ] Explain credential vending and catalog-level access control.
- [ ] Choose a catalog for a given platform.

**Common mistakes:** tables written by one engine and invisible to others
because they use different catalogs; long-lived storage keys in every
engine; choosing a catalog without checking engine support for the formats
and features you use.

---

## 11. Consolidate — practice questions

When all nine topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Choose the format (Delta, Iceberg, Hudi, or plain Parquet) and catalog,
   and justify the choice.
2. Predict the metadata and file changes of each operation.
3. Choose write modes (copy-on-write or merge-on-read), partitioning, and
   clustering.
4. Plan maintenance and retention, including compliance deletes.
5. Implement it and verify from at least two engines.
6. Measure files, bytes scanned, and time before and after.

---

## 12. Module mini-project — an operated, multi-engine lakehouse

This is the proof that you have finished the module.

**Scenario:** Your orders platform (Modules 2.9–2.14) now needs a real
lakehouse: CDC changes applied continuously, GDPR deletions honoured,
analysts querying with different engines, and ML models trained on
reproducible snapshots — all on open storage.

Build `lakehouse/` on MinIO with:

1. **Catalog** — an Iceberg REST catalog (e.g. Apache Polaris) with
   `bronze`, `silver`, and `gold` namespaces, separate principals for
   pipelines and analysts, and (where supported) credential vending.
2. **Tables** — bronze as append-only Iceberg tables; silver and gold as
   Iceberg tables with hidden partitioning and sort orders; one gold table
   additionally built in Delta Lake (with liquid clustering) for
   comparison.
3. **Changes** — CDC applied to `silver.customers` and `silver.orders` with
   deduplicated `MERGE`s; `gold.dim_customer` as SCD Type 2; idempotent
   daily loads.
4. **Safety** — write–audit–publish using Iceberg branches with your
   Module 2.11 checks; a restore drill after a simulated bad deploy; a
   concurrency drill with two writers.
5. **Versioning** — a version-pinned ML training dataset recorded in run
   metadata; a `diff_versions` tool; an incremental consumer using change
   feeds.
6. **Compliance** — an end-to-end right-to-be-forgotten process (delete →
   rewrite → expire/vacuum → verification scan) with an audit record.
7. **Maintenance** — a per-table maintenance policy (compaction,
   clustering or Z-order, snapshot expiry, orphan cleanup, manifest
   rewrites) run by an Airflow or Dagster DAG, plus a table health report.
8. **Multi-engine access** — Spark writes; PyIceberg, DuckDB, and Polars
   read through the catalog; a small Python-only (no Spark) job using
   PyIceberg or delta-rs for a lightweight table.
9. **Decision record** — Delta vs Iceberg vs Hudi and catalog choice for
   this platform, backed by your measurements.

**Grading yourself:** readers never see partial writes; bad data never
reaches published gold; any published table can be restored and any past
report reproduced within retention; a deleted customer's data is provably
gone from storage after the maintenance cycle; and every engine reads the
same tables through one catalog.

---

## 13. Module self-assessment — exit criteria

Only move to Module 2.16 when you can tick every box without looking at your
notes:

- [ ] I can explain why plain data lakes need table formats.
- [ ] I can explain Delta's transaction log and optimistic concurrency.
- [ ] I can explain Iceberg's metadata tree, hidden partitioning, and
      partition evolution.
- [ ] I can explain Hudi's table types and timeline.
- [ ] I can run ACID `MERGE`, `UPDATE`, and `DELETE`, apply CDC, and handle
      concurrent writers.
- [ ] I can use time travel, restore, change feeds, branches, and WAP.
- [ ] I can compact and cluster tables and measure the benefit.
- [ ] I can design retention and maintenance, including provable
      physical deletion.
- [ ] I can explain and choose catalogs and connect multiple engines.
- [ ] I have finished all practice questions and the mini-project.

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Delta Lake documentation and the Delta transaction log protocol specification | 02, 05–08 |
| Apache Iceberg documentation and table specification (format versions 2 and 3), Spark procedures reference | 03, 05–08 |
| PyIceberg and delta-rs (`deltalake`) documentation | 02, 03, 05, 06 |
| Apache Hudi documentation — concepts, table types, timeline, table services | 04 |
| *Delta Lake: The Definitive Guide* — Denny Lee, Tristen Wentling, Scott Haines, Prashanth Babu (O'Reilly) | 02, 05–08 |
| *Apache Iceberg: The Definitive Guide* — Tomer Shiran, Jason Hughes, Alex Merced (O'Reilly) | 03, 05–09 |
| The CIDR 2021 paper "Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics" | 01 |
| Iceberg REST catalog specification; Apache Polaris and Unity Catalog (open source) documentation | 09 |
| DuckDB `delta` and `iceberg` extension documentation; Polars documentation on Delta and Iceberg | 02, 03, 09 |

---

## 15. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Streaming writes into Delta and Iceberg tables; exactly-once sinks | 2.16 Streaming and Event-Driven Data |
| Managed lakehouse and catalog services; warehouses reading Iceberg | 2.17 Cloud Storage and Cloud Data Platforms |
| Maintenance jobs and catalogs as infrastructure; CI for table changes | 2.18 Containers, Infrastructure, and CI/CD for Data |
| Testing table operations and contract regression | 2.19 Testing Data Pipelines |
| Catalog-based governance, lineage, access control, and compliance deletes | 2.20 Observability, Lineage, Governance, and Security |
| Storage and compute cost of rewrites, clustering, and retention | 2.21 Performance, Scaling, and Cost Optimization |
| Versioned training data and feature tables on the lakehouse | 2.22 Serving Data for Analytics, ML, and AI |

Table formats turn files into tables, but tables still need care. The
habits you build here — predict every metadata change, choose write modes
deliberately, publish only audited data, maintain layout and retention on
a schedule, and prove deletions — are what make an open lakehouse as
reliable as any warehouse while staying open to every engine.
