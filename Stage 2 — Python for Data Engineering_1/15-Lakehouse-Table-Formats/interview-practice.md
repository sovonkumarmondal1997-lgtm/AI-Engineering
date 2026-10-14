# Module 2.15 — Lakehouse Table Formats
# Interview Practice and Solutions

## Purpose

This interview-practice set is designed to evaluate whether a learner can reason about the production engineering problems covered by Module 2.15 — Lakehouse Table Formats. The questions progress from foundational interview scenarios to senior-level architecture, troubleshooting, security, operations, and format-selection decisions.

The set is grounded in the module scope: open table formats, Delta Lake, Apache Iceberg, Apache Hudi, ACID row-level changes, CDC, time travel and versioning, compaction and data layout, retention and maintenance, catalogs, governance, credential vending, and multi-engine access.

## How to Use This Practice Set

For each question, answer the **Problem** aloud before reading the **Solution**. A strong interview response should explain the reasoning, identify the metadata/control-plane implications, state assumptions, discuss failure and retry behavior, and describe how the result would be verified in production.

Use the progression as follows:

- **Basic:** explain core concepts and apply them to small production scenarios.
- **Moderate:** connect two or more concepts and explain a diagnostic or implementation approach.
- **Hard:** reason through production failures, concurrency, CDC, maintenance, and trade-offs.
- **Advanced:** defend architecture and platform decisions as a senior Data Engineer / Data Platform Engineer.

---

# Part 1 — Basic Interview Questions

## Question 1 — Why a Lakehouse Needs a Table Format

### Difficulty
Basic

### Topics Covered
- 01 — Why Open Table Formats Exist

### Problem
Your team has 20 TB of Parquet files in object storage. Analysts report inconsistent results when two pipelines write at the same time, and engineers have no reliable way to inspect or restore an earlier table state. A hiring manager asks: “Why can’t we just treat the Parquet directory as the table, and what does an open table format add?”

### Solution
Start by separating the **data files** from the **table state**. Parquet gives an efficient columnar file representation, but a directory of files does not by itself provide an atomic transaction boundary, reliable row-level changes, table history, coordinated concurrent commits, or a durable description of which files constitute the current table state.

An open table format adds a metadata/transaction layer over object storage. The table format records committed changes, identifies active and obsolete files, supports schema and partition metadata, and gives readers a consistent table snapshot. Delta does this through its transaction log; Iceberg through its metadata/snapshot/manifest hierarchy; Hudi through its timeline and table services.

The architectural result is a lakehouse table: open files remain in object storage, while table metadata provides database-like correctness and operational features.

A strong interview answer should also distinguish the **table format** from the **catalog**. The format defines table state and transaction semantics; a catalog provides a discoverable name/namespace and may participate in governance and commit coordination.

### Why This Works
The key insight is that Parquet is a file format, not a complete table-management protocol.

### Interviewer Look-For
- Clear distinction between physical files, logical table state, metadata, and catalog responsibilities.
- Correct use of the table-format concepts rather than directory-level file manipulation.
- Reasoning that connects the immediate symptom to the underlying lakehouse design.

## Question 2 — Parquet Failure During a Write

### Difficulty
Basic

### Topics Covered
- 01 — Why Open Table Formats Exist

### Problem
A Spark job writes 500 Parquet files for a daily load and is killed after writing 320 files. A query starts immediately afterward and reads the directory directly. What can go wrong, and why does a table format change the failure model?

### Solution
A direct directory reader may observe a mixture of old and newly written files. The directory does not inherently tell the reader that the 320 newly created files belong to an uncommitted transaction. This can produce partial or inconsistent results.

With a table format, the write is represented as a transaction/commit. Readers resolve the committed table state from the format's metadata rather than simply listing every physical file. If the writer fails before committing, the uncommitted files are not part of the logical table state; they can later be cleaned up according to the format's maintenance rules.

The interview point is not that object storage suddenly becomes transactional. The table format creates a logical transaction boundary above the physical files.

### Why This Works
Logical table state and physical files are different concepts; a failed write must not automatically become visible table state.

### Interviewer Look-For
- Clear distinction between physical files, logical table state, metadata, and catalog responsibilities.
- Correct use of the table-format concepts rather than directory-level file manipulation.
- Reasoning that connects the immediate symptom to the underlying lakehouse design.

## Question 3 — ACID in a Lakehouse

### Difficulty
Basic

### Topics Covered
- 01 — Why Open Table Formats Exist
- 05 — ACID MERGE/UPDATE/DELETE

### Problem
An interviewer asks whether “ACID on a data lake” means that every Parquet file itself becomes a database page. Explain what ACID means at the table level.

### Solution
At the table level, ACID means the table-format transaction mechanism provides a controlled commit boundary and a consistent interpretation of table state.

**Atomicity:** a logical change becomes visible as a committed state rather than exposing half of the intended operation.

**Consistency:** table invariants such as schema and supported table-format rules are maintained.

**Isolation:** concurrent operations are coordinated so conflicting commits do not silently overwrite one another.

**Durability:** once a commit is accepted, the metadata describing that committed state persists.

The physical Parquet files remain ordinary objects. The table format's metadata and commit protocol make those files behave as versions of a logical table.

### Why This Works
Explain ACID as a property of the table-management protocol, not as a claim that Parquet itself implements database transactions.

### Interviewer Look-For
- Clear distinction between physical files, logical table state, metadata, and catalog responsibilities.
- Correct use of the table-format concepts rather than directory-level file manipulation.
- Reasoning that connects the immediate symptom to the underlying lakehouse design.

## Question 4 — Reading a Delta Transaction Log

### Difficulty
Basic

### Topics Covered
- 02 — Delta Lake Transaction Log

### Problem
A Delta table contains `_delta_log` files. A junior engineer says, “Those JSON files are just audit logs; the query engine can ignore them and scan all Parquet files.” How would you correct them?

### Solution
The transaction log is part of the table's authoritative state-management mechanism. Delta commits record actions such as files being added or removed and table metadata/protocol information. A reader uses the committed log history, and checkpoints can summarize state so the engine does not need to replay every JSON commit indefinitely.

The current table is therefore reconstructed from the committed transaction history/checkpoint state. Physical Parquet files that are not active according to the table state are not automatically current table data.

The correct mental model is:

`transaction log/checkpoint → current logical file set → physical Parquet reads`.

Treating the log as optional audit text breaks the table's consistency model.

### Why This Works
Delta's log is not ancillary logging; it is central to reconstructing table state.

### Interviewer Look-For
- Clear distinction between physical files, logical table state, metadata, and catalog responsibilities.
- Correct use of the table-format concepts rather than directory-level file manipulation.
- Reasoning that connects the immediate symptom to the underlying lakehouse design.

## Question 5 — Iceberg Metadata Tree

### Difficulty
Basic

### Topics Covered
- 03 — Apache Iceberg Snapshots and Manifests

### Problem
An interviewer gives you this chain: table metadata → snapshot → manifest list → manifests → data files. Explain why Iceberg uses multiple metadata layers instead of keeping one giant list of files.

### Solution
Each layer has a different responsibility.

The table metadata identifies the current table state and its snapshots and schema/partition information. A snapshot represents a particular committed table state. The manifest list identifies the manifests associated with that snapshot. Manifests contain file-level metadata and statistics used to determine which files belong to the snapshot and which can be skipped.

This hierarchy allows metadata to be managed incrementally and supports snapshot-based reads, pruning, and efficient planning without requiring a single monolithic file containing every table decision.

When debugging, trace from the current snapshot downward rather than starting with an arbitrary object-storage listing.

### Why This Works
The metadata hierarchy separates table version selection from file-level planning and pruning.

### Interviewer Look-For
- Clear distinction between physical files, logical table state, metadata, and catalog responsibilities.
- Correct use of the table-format concepts rather than directory-level file manipulation.
- Reasoning that connects the immediate symptom to the underlying lakehouse design.

## Question 6 — Hudi COW vs MOR

### Difficulty
Basic

### Topics Covered
- 04 — Apache Hudi Overview

### Problem
A Hudi workload receives frequent updates but also serves frequent analytical reads. An interviewer asks you to explain the difference between Copy-on-Write and Merge-on-Read before recommending a table type.

### Solution
With **Copy-on-Write (COW)**, updates are incorporated into base files as part of the write path. Reads can therefore use the base representation without the same level of merge work.

With **Merge-on-Read (MOR)**, updates can be recorded separately and reconciled with base data during reads or later table services such as compaction. MOR can reduce write amplification for update-heavy workloads, but introduces additional read/maintenance complexity.

The correct choice depends on the workload's read latency, write frequency, update volume, compaction budget, and incremental-processing needs. Do not choose purely because one mode is “faster.”

### Why This Works
COW generally favors simpler/faster reads at the cost of more write work; MOR shifts some work toward reads and table services.

### Interviewer Look-For
- Clear distinction between physical files, logical table state, metadata, and catalog responsibilities.
- Correct use of the table-format concepts rather than directory-level file manipulation.
- Reasoning that connects the immediate symptom to the underlying lakehouse design.

## Question 7 — Why CDC Needs Ordering and Deduplication

### Difficulty
Basic

### Topics Covered
- 05 — ACID MERGE/UPDATE/DELETE

### Problem
A CDC stream contains two updates for the same customer followed by a delete. Events can be replayed and may arrive more than once. Why can't the pipeline simply MERGE every event in arrival order?

### Solution
Arrival order is not necessarily business/event order, and duplicate delivery can make a non-idempotent pipeline apply the same logical change repeatedly.

The pipeline should establish a deterministic event identity, deduplicate repeated events, and order competing changes using the source's sequence/version/timestamp semantics where those semantics are valid. Then the resulting latest state can be applied through a deterministic MERGE/update/delete process.

The exact ordering key must come from the source contract; blindly using ingestion time can produce incorrect state.

Verification should compare expected source state with the target state and include replay testing.

### Why This Works
CDC correctness depends on identity, ordering semantics, and idempotent application—not simply on using MERGE syntax.

### Interviewer Look-For
- Clear distinction between physical files, logical table state, metadata, and catalog responsibilities.
- Correct use of the table-format concepts rather than directory-level file manipulation.
- Reasoning that connects the immediate symptom to the underlying lakehouse design.

## Question 8 — Time Travel and Retention

### Difficulty
Basic

### Topics Covered
- 06 — Time Travel and Table Versioning
- 08 — VACUUM/Retention/Maintenance

### Problem
A data scientist asks for a table version from 30 days ago. The platform team configured aggressive physical cleanup after 7 days. Why might time travel fail even though the table format supports historical versions?

### Solution
Time travel depends on both the logical history and the physical files needed to materialize that historical state. Retaining metadata alone is insufficient if the physical data files required by an old snapshot/version have already been removed.

Therefore, retention and cleanup policies must be aligned with historical access requirements. A 30-day reproducibility requirement conflicts with a policy that physically removes required files after seven days.

The team should define the required retention window, account for long-running readers and reproducibility use cases, and only perform physical cleanup when it is safe under that policy.

### Why This Works
Historical reproducibility is constrained by physical retention, not just by the existence of version identifiers.

### Interviewer Look-For
- Clear distinction between physical files, logical table state, metadata, and catalog responsibilities.
- Correct use of the table-format concepts rather than directory-level file manipulation.
- Reasoning that connects the immediate symptom to the underlying lakehouse design.

## Question 9 — Small Files and Query Performance

### Difficulty
Basic

### Topics Covered
- 07 — Compaction/Z-Ordering/Liquid Clustering

### Problem
A pipeline creates 100,000 tiny Parquet files per day. Storage is growing and queries are slow even though the amount of data is moderate. What is your first hypothesis?

### Solution
The first hypothesis is a **small-file problem**. A large number of tiny files increases metadata/listing overhead and causes queries to open and plan against many file objects. It can also make downstream maintenance more expensive.

The correct response is to measure file counts and file-size distribution, identify which jobs create the fragmentation, and then use an appropriate compaction strategy. After compaction, measure query planning time, scan time, file count, and storage/compute cost.

Do not assume “more files means more parallelism” is always beneficial; excessive file counts can overwhelm the benefits.

### Why This Works
File layout is part of table performance. Diagnose with measurements before changing layout.

### Interviewer Look-For
- Clear distinction between physical files, logical table state, metadata, and catalog responsibilities.
- Correct use of the table-format concepts rather than directory-level file manipulation.
- Reasoning that connects the immediate symptom to the underlying lakehouse design.

## Question 10 — Catalog vs Table Format

### Difficulty
Basic

### Topics Covered
- 09 — Catalogs/Hive Metastore/Glue/Unity/Polaris

### Problem
A team says, “We use Iceberg, so we don't need a catalog.” Explain the difference between the two and why a catalog matters in a multi-engine environment.

### Solution
The **table format** defines how table state, metadata, snapshots, files, and commits are represented. A **catalog** provides a way to register and resolve logical table identifiers such as `catalog.schema.table`, and can provide governance, namespace management, and—depending on the implementation—commit coordination or credential-related capabilities.

In a multi-engine environment, Spark, PyIceberg, and other engines need a consistent way to locate the same table and metadata. A catalog provides that shared discovery/control plane.

Some table configurations can operate with simpler/local catalog mechanisms, but enterprise multi-engine architectures commonly need a shared catalog with appropriate security and operational guarantees.

### Why This Works
Do not conflate physical storage, table-format metadata, and catalog discovery/governance.

### Interviewer Look-For
- Clear distinction between physical files, logical table state, metadata, and catalog responsibilities.
- Correct use of the table-format concepts rather than directory-level file manipulation.
- Reasoning that connects the immediate symptom to the underlying lakehouse design.

---

# Part 2 — Moderate Interview Questions

## Question 11 — Reconstructing a Delta Table State

### Difficulty
Moderate

### Topics Covered
- 02 — Delta Lake Transaction Log
- 06 — Time Travel

### Problem
You inspect a Delta table and find these conceptual commits: commit 0 adds A and B; commit 1 removes A and adds C; commit 2 adds D. A teammate says the current table contains A, B, C, and D. How do you determine the actual current state?

### Solution
Treat the transaction history as a state transition sequence.

Start with the initial active-file set: `{A, B}`. Commit 1 removes A and adds C, giving `{B, C}`. Commit 2 adds D, giving `{B, C, D}`.

The important interview point is that an `add` or `remove` action is interpreted relative to the previously committed state. You do not determine the table by scanning all objects and taking every file that exists.

In a real investigation, inspect the actual Delta log/checkpoint state and table history rather than relying on a simplified reconstruction.

### Why This Works
The current table is a logical active-file set derived from committed actions, not a directory listing.

### Interviewer Look-For
- Multi-step reasoning rather than memorized definitions.
- Evidence-first debugging and explicit verification.
- Awareness of correctness, performance, retention, and operational implications.

## Question 12 — Why Delta Checkpoints Exist

### Difficulty
Moderate

### Topics Covered
- 02 — Delta Lake Transaction Log

### Problem
A Delta table has accumulated a very large number of transaction-log JSON commits. Explain why checkpoints help and what they do not change.

### Solution
Replaying every historical JSON commit becomes increasingly expensive. A checkpoint provides a summarized representation of table state at a particular point so readers can start from that state and process only the later commits needed to reach the requested version.

Checkpoints therefore improve metadata-read efficiency; they do not eliminate the transaction history concept or turn physical Parquet files into transactional database pages.

During troubleshooting, use the checkpoint plus subsequent log entries to understand how the current state was reconstructed.

### Why This Works
Checkpoints optimize state reconstruction; they are an acceleration mechanism for the metadata history.

### Interviewer Look-For
- Multi-step reasoning rather than memorized definitions.
- Evidence-first debugging and explicit verification.
- Awareness of correctness, performance, retention, and operational implications.

## Question 13 — Tracing an Iceberg Query

### Difficulty
Moderate

### Topics Covered
- 03 — Apache Iceberg Snapshots and Manifests

### Problem
An Iceberg query filters on a date range. Walk through how a reader can move from a table name to the relevant data files without scanning every object in storage.

### Solution
First resolve the table through the catalog and locate the current table metadata. The metadata identifies the current snapshot. The snapshot references a manifest list. The manifest list identifies manifests containing file-level information.

The engine evaluates manifest/file metadata, including partition information and statistics where applicable, to prune files that cannot satisfy the query. It then reads the remaining data files.

With hidden partitioning and partition evolution, the query should be expressed in terms of table columns; the table metadata handles how those columns are physically organized.

### Why This Works
Iceberg separates snapshot selection from manifest/file planning, enabling metadata-driven pruning.

### Interviewer Look-For
- Multi-step reasoning rather than memorized definitions.
- Evidence-first debugging and explicit verification.
- Awareness of correctness, performance, retention, and operational implications.

## Question 14 — CDC Replay After a Failure

### Difficulty
Moderate

### Topics Covered
- 05 — ACID MERGE/UPDATE/DELETE
- 06 — Time Travel

### Problem
A CDC job successfully commits 80% of a batch, then the orchestrator reports failure and retries the entire batch. How would you design the retry so already-applied changes are not duplicated or incorrectly re-ordered?

### Solution
First determine whether the table operation itself committed atomically. If the intended transaction committed, the retry must recognize that the batch/event identities were already applied rather than blindly replaying them.

Use stable source event identifiers and a deterministic ordering/version rule. Deduplicate the retry input before applying changes. The target merge condition should identify the business key, while the update logic should prevent an older event from overwriting a newer state.

Finally, inspect table history/metadata to determine what actually committed before deciding what to replay. A reported orchestration failure is not proof that the data transaction failed.

### Why This Works
Separate orchestration state from table transaction state. The source of truth for committed data is the table's commit history.

### Interviewer Look-For
- Multi-step reasoning rather than memorized definitions.
- Evidence-first debugging and explicit verification.
- Awareness of correctness, performance, retention, and operational implications.

## Question 15 — Recovering from a Bad Table Version

### Difficulty
Moderate

### Topics Covered
- 06 — Time Travel and Table Versioning

### Problem
A production deployment accidentally writes incorrect values to a table. Analysts noticed the problem after several commits. Describe a safe recovery workflow rather than immediately deleting files.

### Solution
1. Identify the bad time/version from table history.
2. Inspect the affected versions and determine the exact change boundary.
3. Compare the known-good and bad states to understand what changed.
4. Choose the supported recovery mechanism—such as restore/rollback or a corrective write—based on the format and operational requirements.
5. Preserve evidence and validate downstream dependencies.
6. Verify the recovered table with business/data-quality checks.

Do not manually delete historical Parquet files. Physical cleanup is a separate maintenance concern and can destroy the files required for historical reads.

### Why This Works
Recovery is a metadata/state operation first; physical cleanup comes later and only under an explicit retention policy.

### Interviewer Look-For
- Multi-step reasoning rather than memorized definitions.
- Evidence-first debugging and explicit verification.
- Awareness of correctness, performance, retention, and operational implications.

## Question 16 — Diagnosing a Small-File Explosion

### Difficulty
Moderate

### Topics Covered
- 07 — Compaction/Z-Ordering/Liquid Clustering
- 08 — Table Maintenance

### Problem
A streaming ingestion pipeline changed from 500 MB files to millions of 5 MB files. Query latency and storage costs increased. What measurements would you collect before enabling compaction?

### Solution
Collect at least: file count over time, file-size distribution, partition/file distribution, query planning and scan latency, bytes read, write throughput, compaction frequency/cost, and the workload's common filter columns.

Then identify the producer of the tiny files and determine whether compaction can safely consolidate them without creating oversized files or excessive write amplification.

Measure the post-compaction state against the baseline. The objective is not “fewer files” by itself; it is better end-to-end performance and cost without harming write latency or operational correctness.

### Why This Works
Compaction is an optimization. Establish a measurable before/after baseline and avoid optimizing the wrong bottleneck.

### Interviewer Look-For
- Multi-step reasoning rather than memorized definitions.
- Evidence-first debugging and explicit verification.
- Awareness of correctness, performance, retention, and operational implications.

## Question 17 — Choosing Z-Ordering

### Difficulty
Moderate

### Topics Covered
- 07 — Compaction/Z-Ordering/Liquid Clustering

### Problem
A 5 TB table is frequently filtered by `customer_id`, `region`, and `event_date`. The team proposes Z-Ordering on all three columns immediately. What questions do you ask first?

### Solution
Ask which predicates dominate production queries, the cardinality and distribution of each column, existing partitioning, current file sizes, and whether data skipping is actually the bottleneck.

Z-Ordering is useful when co-locating values improves file-level skipping for important query predicates. It is not a universal replacement for partitioning, and adding many columns without workload evidence can reduce its effectiveness and increase maintenance cost.

Apply the optimization only after measuring current pruning behavior and then compare query latency, files scanned, bytes read, and maintenance cost.

### Why This Works
Layout optimization must follow workload patterns and measured pruning opportunities, not column-count intuition.

### Interviewer Look-For
- Multi-step reasoning rather than memorized definitions.
- Evidence-first debugging and explicit verification.
- Awareness of correctness, performance, retention, and operational implications.

## Question 18 — Retention Policy Conflict

### Difficulty
Moderate

### Topics Covered
- 06 — Time Travel
- 08 — Retention/Maintenance

### Problem
The platform wants seven-day cleanup, while an ML team requires 30-day reproducibility of training data. How would you reconcile the requirements?

### Solution
First distinguish the exact reproducibility requirement: whether the ML team needs the complete historical table state, a specific versioned dataset, or only selected training inputs.

If historical table files must remain available for 30 days, a seven-day physical cleanup policy is incompatible with that requirement. Establish a retention tier or protected dataset strategy so required training versions remain recoverable while unrelated data follows shorter retention.

Coordinate snapshot/version retention and physical file cleanup. Document the retention contract and verify that cleanup jobs cannot delete protected history prematurely.

### Why This Works
Retention is a product/operational contract. Cleanup cannot be designed independently of reproducibility requirements.

### Interviewer Look-For
- Multi-step reasoning rather than memorized definitions.
- Evidence-first debugging and explicit verification.
- Awareness of correctness, performance, retention, and operational implications.

## Question 19 — Catalog Visibility Debugging

### Difficulty
Moderate

### Topics Covered
- 09 — Catalogs/Hive Metastore/Glue/Unity/Polaris
- 03 — Iceberg Metadata

### Problem
Spark can query an Iceberg table, but PyIceberg reports that the table does not exist. List the first areas you would investigate.

### Solution
Check the catalog configuration used by each engine: catalog type, endpoint/URI, warehouse/object-storage location, authentication, namespace, and exact table identifier.

Then verify that both engines resolve the same catalog namespace and table metadata. Check permissions and whether one engine is using a different catalog instance or stale configuration.

If the table exists but the engines observe different states, inspect snapshot/metadata references and compatibility/version issues. The goal is to prove whether the problem is discovery, authorization, metadata location, or stale/incompatible client behavior.

### Why This Works
“Table not found” is a discovery/control-plane symptom until proven otherwise.

### Interviewer Look-For
- Multi-step reasoning rather than memorized definitions.
- Evidence-first debugging and explicit verification.
- Awareness of correctness, performance, retention, and operational implications.

## Question 20 — Hudi Incremental Processing

### Difficulty
Moderate

### Topics Covered
- 04 — Apache Hudi Overview

### Problem
A downstream job wants only changes since its last successful run from a Hudi table. What Hudi concepts would you investigate, and what correctness questions would you ask?

### Solution
Investigate the Hudi timeline and incremental query capabilities, along with the table's record-key and ordering-field semantics. Determine what timeline boundary represents the downstream job's last successful checkpoint.

Then verify that the chosen incremental range corresponds to the desired committed changes and understand how the table type and compaction affect the read path.

Correctness questions include: what identifies a record, what orders competing updates, what happens after retries, and how the consumer stores and advances its own checkpoint.

### Why This Works
Incremental processing requires a well-defined table timeline and consumer checkpoint, not just a timestamp filter.

### Interviewer Look-For
- Multi-step reasoning rather than memorized definitions.
- Evidence-first debugging and explicit verification.
- Awareness of correctness, performance, retention, and operational implications.

---

# Part 3 — Hard Interview Questions

## Question 21 — Concurrent MERGE Conflicts

### Difficulty
Hard

### Topics Covered
- 02 — Delta Transaction Log
- 05 — ACID MERGE/UPDATE/DELETE

### Problem
Two independent jobs MERGE changes into the same Delta table at nearly the same time. Both read the table before either commit is visible. One job fails with a concurrency conflict. Explain why this is preferable to silently losing one job's updates and how you would design retries.

### Solution
The conflict indicates that the table's concurrency mechanism detected an incompatible change between the job's read assumptions and the current committed state. Failing the conflicting transaction protects correctness instead of silently overwriting another writer.

The retry should re-read the current table state and recompute the affected operation when necessary. Do not blindly resubmit the exact stale transaction assumptions. Make the input batch idempotent, bound retries, and instrument conflict rates.

If the workload permits, reduce unnecessary overlap by partitioning work or assigning non-overlapping write scopes. However, partitioning is a contention-reduction technique, not a substitute for correct transaction handling.

### Why This Works
A visible conflict is usually safer than silent lost updates. Correct retries must be based on fresh state.

### Interviewer Look-For
- Production-grade reasoning about concurrency, idempotency, CDC, physical layout, maintenance, and security.
- Explicit trade-offs and measurable verification criteria.
- Separation of logical correctness from physical storage operations.

## Question 22 — CDC + SCD Type 2 Design

### Difficulty
Hard

### Topics Covered
- 05 — ACID MERGE/UPDATE/DELETE
- 06 — Time Travel

### Problem
A customer dimension must preserve historical versions. CDC sends inserts, updates, and deletes, sometimes with duplicate events. Design the table-update logic at a high level.

### Solution
Use a stable business key plus an event ordering/version field. First deduplicate events by event identity and choose the correct latest event per business key according to the source ordering contract.

For an update that changes tracked attributes, close the currently active SCD2 row and create a new version with effective timestamps/version metadata. A delete should follow the documented business semantics—such as closing/deactivating the current row or recording a deletion state.

Make the operation idempotent so replaying the same CDC batch does not create duplicate history. Validate that each business key has at most one active version and that effective intervals are coherent.

### Why This Works
SCD2 correctness is a state-model problem layered on top of CDC ordering, deduplication, and atomic table writes.

### Interviewer Look-For
- Production-grade reasoning about concurrency, idempotency, CDC, physical layout, maintenance, and security.
- Explicit trade-offs and measurable verification criteria.
- Separation of logical correctness from physical storage operations.

## Question 23 — COW vs MOR for an Update-Heavy Workload

### Difficulty
Hard

### Topics Covered
- 04 — Apache Hudi Overview
- 05 — ACID MERGE/UPDATE/DELETE
- 07 — Compaction

### Problem
A 50 TB table receives frequent updates throughout the day, but analysts expect low-latency reads. Compare Hudi COW and MOR and make a conditional recommendation.

### Solution
COW writes updated base-file state, which can make reads simpler and lower-latency but can increase write amplification for frequent updates. MOR can record changes separately and defer some work to reads or compaction, reducing immediate rewrite cost but adding read/maintenance complexity.

If analytical reads are extremely latency-sensitive and update volume is manageable, COW may be attractive. If update frequency is very high and write amplification is the dominant bottleneck, MOR may be preferable—provided the platform can support the resulting compaction and read behavior.

The final decision should be based on measured write/read latency, update volume, file growth, compaction cost, and operational SLOs.

### Why This Works
There is no format-independent winner; the workload determines where the system should spend compute and I/O.

### Interviewer Look-For
- Production-grade reasoning about concurrency, idempotency, CDC, physical layout, maintenance, and security.
- Explicit trade-offs and measurable verification criteria.
- Separation of logical correctness from physical storage operations.

## Question 24 — Right-to-Be-Forgotten Across History

### Difficulty
Hard

### Topics Covered
- 05 — DELETE
- 06 — Time Travel
- 08 — Retention/Maintenance

### Problem
A customer requests complete deletion. The current table no longer contains the customer after a logical DELETE, but older table versions may still reference files containing the record. How do you reason about compliance deletion?

### Solution
Treat the operation as both logical and physical.

First perform the supported logical deletion/correction so the current table no longer exposes the record. Then identify historical versions and obsolete physical files that can still contain the record. Retention, snapshot expiration, orphan-file cleanup, and physical deletion must be coordinated so those files eventually cease to be retained.

Finally, verify through current-state queries, historical/metadata inspection where appropriate, and storage-level cleanup evidence that retained copies are not still accessible under the defined policy.

The exact commands depend on the table format and retention configuration; the architectural requirement is to avoid assuming that a logical DELETE immediately erases every historical physical copy.

### Why This Works
Compliance deletion requires understanding the gap between logical table state and physical historical data.

### Interviewer Look-For
- Production-grade reasoning about concurrency, idempotency, CDC, physical layout, maintenance, and security.
- Explicit trade-offs and measurable verification criteria.
- Separation of logical correctness from physical storage operations.

## Question 25 — Iceberg Partition Evolution

### Difficulty
Hard

### Topics Covered
- 03 — Apache Iceberg Snapshots and Manifests

### Problem
A table was originally partitioned by day, but the workload now needs better organization for a different access pattern. The team fears that changing the partition strategy will require rewriting every historical file. How would you explain Iceberg's partition-evolution model?

### Solution
Iceberg separates the table's logical schema from the physical partition specification and supports partition evolution. New data can use a new partitioning scheme while older data retains its prior physical organization.

Queries are planned using the table metadata and partition information associated with the relevant data. This avoids requiring a full historical rewrite merely to change the partition specification.

The engineering decision is still workload-driven: assess pruning, file distribution, historical/new-data behavior, and whether a rewrite is justified for performance. Partition evolution changes how future data is organized; it does not magically optimize every old file.

### Why This Works
Partition evolution separates logical table evolution from an all-at-once physical rewrite.

### Interviewer Look-For
- Production-grade reasoning about concurrency, idempotency, CDC, physical layout, maintenance, and security.
- Explicit trade-offs and measurable verification criteria.
- Separation of logical correctness from physical storage operations.

## Question 26 — Metadata-First Incident Investigation

### Difficulty
Hard

### Topics Covered
- 02 — Delta Transaction Log
- 03 — Iceberg Metadata
- 06 — Time Travel

### Problem
A table suddenly returns fewer rows. The object-storage directory still contains all the expected Parquet files. How would you investigate without immediately restoring or rewriting the table?

### Solution
Start with the logical table state, not the directory listing.

For Delta, inspect table history, transaction-log commits, add/remove actions, and checkpoints around the time of the incident. Determine which files became active or inactive.

For Iceberg, identify the current snapshot and trace it through metadata, the manifest list, manifests, and file entries. Compare the current snapshot with the last known-good snapshot.

Then determine whether the row loss is caused by an intentional logical change, a bad commit, filtering/pruning behavior, schema/partition interpretation, or missing physical files. Only after establishing the root cause should you choose restore or corrective action.

### Why This Works
When physical storage and logical state disagree, the table-format metadata is the first diagnostic surface.

### Interviewer Look-For
- Production-grade reasoning about concurrency, idempotency, CDC, physical layout, maintenance, and security.
- Explicit trade-offs and measurable verification criteria.
- Separation of logical correctness from physical storage operations.

## Question 27 — Z-Ordering vs Partitioning

### Difficulty
Hard

### Topics Covered
- 07 — Z-Ordering/Liquid Clustering
- 01 — Open Table Formats

### Problem
A team wants to partition a high-cardinality `customer_id` column because nearly every query filters by customer. Explain why this may be a poor design and how clustering/data skipping could be evaluated instead.

### Solution
High-cardinality partitioning can create excessive partition/file fragmentation and many small directories or files. The better approach may be to partition on a lower-cardinality, frequently selective dimension such as date while using file-level organization/clustering for customer-oriented access.

Evaluate actual query predicates, selectivity, file-size distribution, pruning behavior, and maintenance cost. Z-Ordering or liquid clustering may improve locality/data skipping without creating one partition per customer.

The final choice should be validated with representative queries rather than inferred from the existence of a filter predicate alone.

### Why This Works
Partitioning changes coarse physical organization; clustering/data skipping can provide finer locality without exploding partition counts.

### Interviewer Look-For
- Production-grade reasoning about concurrency, idempotency, CDC, physical layout, maintenance, and security.
- Explicit trade-offs and measurable verification criteria.
- Separation of logical correctness from physical storage operations.

## Question 28 — Maintenance vs Long-Running Readers

### Difficulty
Hard

### Topics Covered
- 06 — Time Travel
- 08 — VACUUM/Retention/Maintenance

### Problem
A nightly cleanup job removes old files, but a long-running analytical job occasionally fails because it started before cleanup. How would you redesign the maintenance policy?

### Solution
Identify the reader's maximum expected lifetime and the table-format mechanisms used to protect historical snapshots. Cleanup must not remove files still required by valid readers or supported historical access.

Define retention with a safety margin, monitor long-running readers/jobs, and schedule physical cleanup only after the protected window. If the platform supports snapshot/version-aware retention controls, integrate those into the policy.

Also make the cleanup job observable: record what it intends to remove, what retention boundary it uses, and whether any active readers or protected versions conflict with that boundary.

### Why This Works
Retention should be derived from reader lifetimes and reproducibility requirements, not an arbitrary cleanup interval.

### Interviewer Look-For
- Production-grade reasoning about concurrency, idempotency, CDC, physical layout, maintenance, and security.
- Explicit trade-offs and measurable verification criteria.
- Separation of logical correctness from physical storage operations.

## Question 29 — Catalog and Credential Vending

### Difficulty
Hard

### Topics Covered
- 09 — Catalogs/Governance

### Problem
Your organization wants Spark and DuckDB to access the same Iceberg tables, but neither engine should store long-lived object-storage credentials. Describe the control flow you would propose.

### Solution
Use a shared catalog/control plane that can authenticate the engine principal, authorize the table/namespace operation, and—where supported—provide temporary or scoped storage credentials.

Conceptually:

`Engine → Catalog → authorization/credential decision → temporary storage access → object storage`.

The catalog remains responsible for logical table discovery and governance, while object storage remains the physical data plane.

The design should enforce least privilege, short credential lifetimes, auditability, and separation between catalog permissions and raw storage permissions. Exact credential-vending support depends on the selected catalog and engine integration, so implementation must be validated against the actual versions deployed.

### Why This Works
Credential vending reduces long-lived secret exposure but does not eliminate the need for storage and catalog authorization design.

### Interviewer Look-For
- Production-grade reasoning about concurrency, idempotency, CDC, physical layout, maintenance, and security.
- Explicit trade-offs and measurable verification criteria.
- Separation of logical correctness from physical storage operations.

## Question 30 — Designing an Idempotent Table Write

### Difficulty
Hard

### Topics Covered
- 02 — Delta Transaction Log
- 05 — MERGE/CDC

### Problem
A daily pipeline may be retried three times by the orchestrator. What properties must the table-writing step have so that three executions produce the same intended result as one execution?

### Solution
The input batch needs a stable identity or deterministic key, and the write operation must recognize already-applied records rather than creating duplicates.

For CDC, use source event IDs and ordering/version semantics. For snapshot-style loads, use deterministic merge keys or replace semantics appropriate to the table design. Make the transaction boundary explicit and verify what actually committed before retrying.

After retries, validate row counts, uniqueness/business-key constraints, latest-version semantics, and table history. Idempotency is not “run it again and hope”; it is a designed property of the input identity and write operation.

### Why This Works
Idempotency requires deterministic identity and state transitions, plus verification of committed state.

### Interviewer Look-For
- Production-grade reasoning about concurrency, idempotency, CDC, physical layout, maintenance, and security.
- Explicit trade-offs and measurable verification criteria.
- Separation of logical correctness from physical storage operations.

---

# Part 4 — Advanced Interview Questions

## Question 31 — Multi-Engine Iceberg State Mismatch

### Difficulty
Hard

### Topics Covered
- 03 — Iceberg Metadata
- 09 — Catalogs

### Problem
Spark sees a newly committed Iceberg snapshot, while another engine reads an older snapshot. The table name is identical. What is your debugging tree?

### Solution
First prove that both engines use the same catalog and namespace. Then compare the resolved table metadata location and current snapshot ID.

If the catalog is shared but the reader still sees an older state, investigate client-side caching, stale metadata, transaction/catalog consistency, and engine/library version compatibility. Also verify permissions: a failure to access the latest metadata can present differently depending on the client.

Finally, compare the snapshot IDs and metadata files directly to determine whether the discrepancy is catalog discovery, caching, permissions, or actual metadata incompatibility.

### Why This Works
A multi-engine consistency incident should be decomposed into catalog identity, metadata identity, snapshot identity, and client behavior.

### Interviewer Look-For
- Senior-level synthesis across multiple module topics.
- Explicit requirements, constraints, alternatives, trade-offs, and operational consequences.
- Ability to defend a recommendation rather than merely name a technology.

## Question 32 — Enterprise Lakehouse Architecture

### Difficulty
Advanced

### Topics Covered
- 01
- 03
- 09
- README / Mini-project

### Problem
Design a multi-engine lakehouse for Bronze, Silver, and Gold data on object storage. Spark performs large transformations; PyIceberg and DuckDB perform Python/interactive reads. The platform requires shared discovery, governance, reproducibility, and open storage.

### Solution
Use an open table format appropriate to the required workload and a shared catalog/control plane for table discovery and governance. Organize Bronze, Silver, and Gold into explicit namespaces and define which principals can read or write each layer.

Keep object storage as the data plane and table metadata as the table-state layer. Spark can perform distributed writes, while PyIceberg/DuckDB use the same catalog and table metadata for reads.

For reproducibility, retain identifiable table versions/snapshots or materialized dataset references for critical ML/analytics workloads. Define maintenance and retention policies separately from query access, and instrument metadata, file counts, storage, query latency, and failed commits.

A senior answer must explain not only components but ownership boundaries: storage, table format, catalog, engines, governance, and maintenance.

### Why This Works
The architecture succeeds when the control plane, table-state layer, data plane, and engines have clear responsibilities.

### Interviewer Look-For
- Senior-level synthesis across multiple module topics.
- Explicit requirements, constraints, alternatives, trade-offs, and operational consequences.
- Ability to defend a recommendation rather than merely name a technology.

## Question 33 — Delta vs Iceberg Decision

### Difficulty
Advanced

### Topics Covered
- 02 — Delta
- 03 — Iceberg
- 06 — Time Travel
- 09 — Catalogs

### Problem
An enterprise already uses Spark heavily but now requires broader multi-engine interoperability, centralized cataloging, schema/partition evolution, and long-term open-table portability. You must choose between Delta Lake and Iceberg. How would you make the decision?

### Solution
Do not choose based on a generic claim that one format is “better.” Build a workload matrix covering: transaction/commit model, metadata architecture, snapshot/versioning behavior, schema evolution, partition evolution, delete/update semantics, engine compatibility, catalog architecture, maintenance tooling, governance requirements, and operational expertise.

Prototype the highest-risk workloads with representative data: concurrent writes, CDC/merge patterns, time-travel/recovery, metadata planning, maintenance, and multi-engine reads. Measure correctness, latency, storage overhead, operational complexity, and compatibility.

If multi-engine openness and the target ecosystem align strongly with Iceberg's metadata/catalog model, Iceberg may be favored. If existing Delta/Spark capabilities and operational maturity dominate, Delta may be favored. The recommendation must be tied to measured requirements and migration cost.

### Why This Works
Format selection is an engineering decision under workload and ecosystem constraints, not a popularity contest.

### Interviewer Look-For
- Senior-level synthesis across multiple module topics.
- Explicit requirements, constraints, alternatives, trade-offs, and operational consequences.
- Ability to defend a recommendation rather than merely name a technology.

## Question 34 — Delta vs Iceberg vs Hudi for CDC

### Difficulty
Advanced

### Topics Covered
- 02 — Delta
- 03 — Iceberg
- 04 — Hudi
- 05 — CDC

### Problem
A platform processes heavy CDC with frequent updates, needs incremental downstream processing, and also requires multiple engines to read the same data. Compare Delta, Iceberg, and Hudi and recommend how you would run an evaluation.

### Solution
Evaluate the three formats against the actual CDC lifecycle: ingestion identity/order, upsert/delete semantics, concurrency, incremental-read mechanisms, metadata behavior, COW/MOR trade-offs where applicable, compaction/maintenance, and multi-engine support.

Hudi deserves specific attention for its timeline, record-key/ordering semantics, COW/MOR table types, incremental queries, and table services. Delta should be evaluated around transaction-log commits, MERGE semantics, concurrency, and change-feed capabilities where used. Iceberg should be evaluated around snapshots, metadata/manifests, delete files, evolution, and the target catalog/multi-engine ecosystem.

Build a controlled benchmark with replayed CDC, duplicates, out-of-order events, concurrent writers, historical reads, and downstream incremental consumers. Select the format based on correctness, operational burden, ecosystem compatibility, and measured performance.

### Why This Works
The evaluation must test the complete CDC lifecycle rather than comparing benchmark numbers in isolation.

### Interviewer Look-For
- Senior-level synthesis across multiple module topics.
- Explicit requirements, constraints, alternatives, trade-offs, and operational consequences.
- Ability to defend a recommendation rather than merely name a technology.

## Question 35 — Metadata Reconstruction Challenge

### Difficulty
Advanced

### Topics Covered
- 02 — Delta Transaction Log
- 03 — Iceberg Metadata

### Problem
During an incident, you are given a last-known-good table state and a current state but no application logs. For Delta you have transaction-log actions; for Iceberg you have metadata, snapshots, manifest lists, and manifests. Explain how you would reconstruct what changed.

### Solution
For Delta, establish the relevant version boundary, start from the applicable checkpoint/state, and replay subsequent add/remove and metadata actions to identify file-set changes and table-property/schema changes.

For Iceberg, identify the relevant snapshots in table metadata, compare snapshot metadata, then trace each snapshot through its manifest list and manifests. Compare file additions/deletions and partition/statistical metadata.

In both cases, distinguish logical state changes from physical object existence. Then map file-level changes back to the application operation that likely caused them. Preserve the evidence before running cleanup or restoration.

The senior-level skill is the ability to reconstruct state from metadata without assuming that application logs are the authoritative record.

### Why This Works
Metadata is an operational evidence source. Learn to trace state transitions rather than guessing from object storage.

### Interviewer Look-For
- Senior-level synthesis across multiple module topics.
- Explicit requirements, constraints, alternatives, trade-offs, and operational consequences.
- Ability to defend a recommendation rather than merely name a technology.

## Question 36 — Automated Maintenance Architecture

### Difficulty
Advanced

### Topics Covered
- 07 — Layout
- 08 — Maintenance

### Problem
Design a maintenance service for a lakehouse with compaction, clustering, snapshot expiration, VACUUM/physical cleanup, and orphan-file cleanup. It must be safe during concurrent writes and support compliance and cost objectives.

### Solution
Separate maintenance into logically distinct services/jobs with explicit safety windows.

**Compaction/clustering:** trigger based on measurable file/layout conditions and workload impact.

**Snapshot expiration/retention:** remove historical metadata only when policy permits.

**Physical cleanup:** remove obsolete files only after the retention boundary and reader/reproducibility checks.

**Orphan cleanup:** identify files that are not referenced by valid table metadata, using format-supported mechanisms rather than directory heuristics alone.

Every job should be idempotent, observable, bounded, and retryable. Record candidates, actions, bytes affected, duration, failures, and post-maintenance metrics. Schedule maintenance to minimize contention with heavy writes, and maintain a documented emergency stop mechanism.

Compliance retention must override cost optimization when the two conflict.

### Why This Works
Maintenance is a controlled lifecycle, not a single VACUUM command.

### Interviewer Look-For
- Senior-level synthesis across multiple module topics.
- Explicit requirements, constraints, alternatives, trade-offs, and operational consequences.
- Ability to defend a recommendation rather than merely name a technology.

## Question 37 — Catalog Architecture for Multi-Engine Analytics

### Difficulty
Advanced

### Topics Covered
- 09 — Catalogs

### Problem
An enterprise is choosing among Hive Metastore, AWS Glue Data Catalog, Unity Catalog, and an Iceberg REST catalog such as Polaris. Spark, Python clients, and multiple analytics engines must share Iceberg tables. How would you structure the decision?

### Solution
Define requirements first: cloud/provider constraints, supported engines, Iceberg compatibility, namespace management, authentication, authorization, credential vending, audit requirements, high availability, operational ownership, and lock-in tolerance.

Then evaluate each candidate against those requirements rather than treating the products as interchangeable. Hive Metastore is a familiar metadata service in many Hadoop/Spark environments. Glue integrates strongly with AWS. Unity Catalog provides a governed control plane in the Databricks ecosystem. Iceberg REST/Polaris-style catalogs are designed around interoperable Iceberg catalog access and multi-engine patterns.

Run compatibility tests with the exact Spark, PyIceberg, DuckDB/other client versions and the chosen storage authentication model. Select the catalog that minimizes operational and interoperability risk for the actual platform.

### Why This Works
Catalog selection is primarily a control-plane and interoperability decision; the table format and storage layer remain separate concerns.

### Interviewer Look-For
- Senior-level synthesis across multiple module topics.
- Explicit requirements, constraints, alternatives, trade-offs, and operational consequences.
- Ability to defend a recommendation rather than merely name a technology.

## Question 38 — Credential Vending Security Review

### Difficulty
Advanced

### Topics Covered
- 09 — Catalogs/Governance

### Problem
A proposed platform lets every Spark cluster store a long-lived cloud storage key in its configuration so that it can read lakehouse data. As the senior engineer, reject or redesign the approach. What would you propose?

### Solution
Prefer short-lived, scoped access where the chosen catalog/integration supports credential vending or equivalent temporary authorization.

The engine authenticates to the catalog using its workload identity. The catalog evaluates namespace/table permissions and supplies temporary, least-privilege storage access. The engine then accesses the required objects without possessing a reusable long-lived storage secret.

The design must include credential lifetime limits, audit trails, revocation/rotation procedures, separation of read and write permissions, and failure behavior when credentials expire.

Also verify the actual implementation capabilities of the selected catalog and cloud provider. “Credential vending” is an architectural pattern, not a license to invent unsupported APIs.

### Why This Works
The goal is to minimize blast radius: short-lived credentials, least privilege, centralized authorization, and auditable access.

### Interviewer Look-For
- Senior-level synthesis across multiple module topics.
- Explicit requirements, constraints, alternatives, trade-offs, and operational consequences.
- Ability to defend a recommendation rather than merely name a technology.

## Question 39 — Production Incident: Slow Queries, High Storage, Broken History

### Difficulty
Advanced

### Topics Covered
- 06 — Time Travel
- 07 — Layout
- 08 — Maintenance

### Problem
After a month of growth, query latency increases, storage costs spike, thousands of small files appear, and users report that older time-travel queries no longer work. A maintenance job also failed twice. Give a senior-level investigation plan.

### Solution
Use an evidence-driven sequence:

1. **Observation:** measure file counts, file-size distribution, bytes scanned, planning time, query latency, storage growth, maintenance failures, and retention configuration.
2. **Hypotheses:** small-file fragmentation, ineffective clustering, excessive obsolete files, premature retention cleanup, or failed maintenance backlog.
3. **Evidence:** inspect table metadata/history, maintenance logs, active/obsolete file state, snapshot/version retention, and workload predicates.
4. **Root cause:** determine whether layout fragmentation explains performance/cost and whether retention cleanup explains broken history.
5. **Remediation:** restore appropriate retention first if history is required; repair maintenance; compact/recluster based on measured workload; avoid unsafe cleanup.
6. **Prevention:** add file-layout, retention, maintenance-health, and historical-read monitoring.

Do not “fix” the incident by deleting more files. That could worsen both storage correctness and reproducibility.

### Why This Works
The correct response connects performance, storage, maintenance, and retention instead of treating each symptom as an isolated incident.

### Interviewer Look-For
- Senior-level synthesis across multiple module topics.
- Explicit requirements, constraints, alternatives, trade-offs, and operational consequences.
- Ability to defend a recommendation rather than merely name a technology.

## Question 40 — WAP / Branch-Based Publishing

### Difficulty
Advanced

### Topics Covered
- 06 — Time Travel and Table Versioning
- 03 — Iceberg

### Problem
A team wants to build a new transformation against production data, validate the result, and publish it only after audit approval. The module teaches versioning/branching concepts for this type of workflow. Design the high-level process.

### Solution
Create an isolated version/work area supported by the selected table format/catalog, perform the transformation there, and validate the resulting snapshot against data-quality and business checks. Keep production consumers pointed at the published/main state until approval.

After approval, publish the validated version through the supported branch/tag or equivalent write-audit-publish mechanism. Preserve an identifiable version for auditability and rollback.

The important distinction is between **writing data** and **publishing a table state**. The workflow reduces the risk of exposing an unapproved intermediate state while preserving reproducibility.

### Why This Works
Write–audit–publish separates experimentation from production visibility and makes the accepted table state explicit.

### Interviewer Look-For
- Senior-level synthesis across multiple module topics.
- Explicit requirements, constraints, alternatives, trade-offs, and operational consequences.
- Ability to defend a recommendation rather than merely name a technology.

---

# Final Coverage Map

| Major Topic | Basic | Moderate | Hard | Advanced |
|---|:---:|:---:|:---:|:---:|
| Why open table formats exist / Parquet limitations | ✓ |  | ✓ | ✓ |
| ACID and logical vs physical table state | ✓ | ✓ | ✓ | ✓ |
| Delta transaction log / checkpoints / state reconstruction | ✓ | ✓ | ✓ | ✓ |
| Delta concurrency / idempotency |  | ✓ | ✓ | ✓ |
| Iceberg snapshots / manifests / metadata tree | ✓ | ✓ | ✓ | ✓ |
| Iceberg partitioning / evolution / pruning |  |  | ✓ | ✓ |
| Hudi timeline / COW / MOR / incremental processing | ✓ | ✓ | ✓ | ✓ |
| MERGE / UPDATE / DELETE / CDC | ✓ | ✓ | ✓ | ✓ |
| CDC deduplication / ordering / SCD2 | ✓ | ✓ | ✓ | ✓ |
| Time travel / rollback / reproducibility | ✓ | ✓ | ✓ | ✓ |
| Compaction / small files | ✓ | ✓ | ✓ | ✓ |
| Z-Ordering / clustering / data layout |  | ✓ | ✓ | ✓ |
| Retention / VACUUM / snapshot expiration / cleanup | ✓ | ✓ | ✓ | ✓ |
| Right-to-be-forgotten / physical deletion |  |  | ✓ | ✓ |
| Catalogs / namespaces / multi-engine discovery | ✓ | ✓ | ✓ | ✓ |
| Governance / permissions / credential vending |  |  | ✓ | ✓ |
| Multi-engine architecture / compatibility |  | ✓ | ✓ | ✓ |
| Production maintenance / observability / cost |  | ✓ | ✓ | ✓ |
| Delta vs Iceberg vs Hudi selection |  |  |  | ✓ |

## Interview Standard

A strong candidate should be able to move from **symptom → metadata/state → root cause → safe operation → verification → prevention**. For architecture questions, the expected pattern is **requirements → constraints → alternatives → trade-offs → recommendation → implementation → failure modes → operations**.

## Validation

- Basic questions: **10**
- Moderate questions: **10**
- Hard questions: **10**
- Advanced questions: **10**
- **Total: 40**
- Every question contains a realistic problem followed immediately by a solution.
- The questions collectively span the major Module 2.15 topics.
