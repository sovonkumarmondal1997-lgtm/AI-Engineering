# 04 — Warehouse, Lakehouse, and Table Format Design

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Define a **data warehouse**, **data lake**, and **lakehouse** as architectural patterns without treating any label as a universally standardized product definition.
2. Distinguish the **storage system**, **table format/table-management layer**, **catalog**, **query or processing engine**, and **data platform**.
3. Explain why a directory of files does not, by itself, provide table-level transactions, coordinated concurrent writes, dependable schema evolution, snapshots, or time travel.
4. Describe the conceptual roles of data files, metadata, transaction logs or equivalent commit metadata, snapshots, manifests, schema metadata, partition metadata, and atomic commits.
5. Explain how readers discover a table through a catalog and use table metadata to determine which data files belong to a consistent version.
6. Identify which table-management capabilities are general concepts and which depend on a particular implementation, catalog, engine, and version.
7. Compare warehouse-only, lakehouse-oriented, and combined architectures against workload fit, governance, interoperability, operations, cost, skills, openness, concurrency, and maintenance.
8. Estimate the storage consequences of retained snapshots and rewritten data, and explain the conflict between time travel and personal-data erasure.
9. Produce a defensible option evaluation with explicit assumptions, a rejected alternative, maintenance ownership, and validation criteria.
10. Connect Topic 3 decisions about object storage and file formats to this topic, and identify the downstream links to Topic 5 (layout) and Topic 7 (retention) without prematurely solving those topics.

**Core principle:** select an architecture from workload and governance requirements, then identify the layers and capabilities required to satisfy them. Do not select it from a product label alone.

## 2. Why the topic matters in real-world data architecture

Analytical systems often start with files arriving in object storage. As usage grows, teams need to know which files represent the current table, which schema applies, whether a failed writer exposed partial output, how concurrent writers coordinate, and whether an older version can be queried. Those needs are not automatically met by placing files in a folder.

A warehouse, a lake, and a lakehouse are related but not interchangeable ideas:

- A **data warehouse** commonly provides a managed analytical environment with SQL access, workload optimisation, and integrated governance. The service may manage storage, metadata, and execution together.
- A **data lake** commonly stores varied source and analytical data in files or objects, often on low-cost scalable storage. The lake may hold raw, standardized, and curated data, but files alone do not guarantee table semantics.
- A **lakehouse** commonly combines lake-style storage and openness with a table-management layer and engines that provide selected warehouse-like capabilities over managed tables. The exact guarantees depend on the table format, catalog, engines, and operating model.

These are architectural patterns, not universal contracts. A vendor may use the same label for a different set of capabilities. The architecture review must therefore ask what the system actually guarantees.

Confusing the layers creates predictable failures:

- A folder of Parquet files is called a lakehouse even though no shared table metadata or commit protocol coordinates readers and writers.
- A table format is mistaken for a complete database or platform, even though compute, identity, governance, orchestration, and operational tooling may be separate.
- Multiple engines are assumed to interoperate because they can read the same file format, even though they may not share catalog semantics or support the same table features.
- Time travel is enabled without estimating retained-file growth or checking whether old snapshots conflict with erasure requirements.
- A managed warehouse and a lakehouse are both deployed without a clear workload reason, creating duplicated data, pipelines, permissions, and operational burden.

The objective is not to prove that one pattern is always best. It is to make the boundaries, guarantees, costs, and responsibilities explicit enough that a design can be tested and maintained.

## 3. Prerequisite knowledge

Complete or review these prerequisites before continuing:

- **Database and storage architecture, Topics 1–3:** analytical versus operational workloads; database-category selection; object, block, and file storage; row-oriented and column-oriented formats; compression, schema representation, and small-file effects.
- **Data architecture patterns, Topic 2:** the warehouse, data lake, and lakehouse patterns and their broader system context.
- **Conceptual, logical, and physical data modeling, Topics 4–5:** dimensional models, facts and dimensions, grain, and historical modeling.
- **Schema evolution and compatibility, Topic 7:** how changes affect producers, consumers, and historical records.

### Terms used in this lesson

| Term | Meaning in this lesson |
|---|---|
| **Object storage** | A storage system that stores objects addressed by keys, usually with object metadata and service-defined access semantics. It is not automatically a POSIX filesystem or a transactional table manager. |
| **Data file** | A physical file or object containing records, such as CSV, JSON Lines, or a columnar binary format. |
| **Table metadata** | Information describing a managed table's schema, current state, data-file membership, partition information, and other properties. |
| **Commit metadata / transaction log** | A record of table changes or committed table states. Implementations use different representations and protocols. |
| **Snapshot** | A logically consistent table state identified by a version, commit, or equivalent metadata reference. |
| **Manifest** | A metadata structure that lists or describes data files and may include partition values, statistics, or related information. Not every implementation uses a structure named “manifest.” |
| **Catalog / metastore** | A service or metadata registry through which engines locate table definitions and associated metadata. The catalog may also integrate identity, permissions, and governance. |
| **Query / processing engine** | Software that executes SQL, transformations, or analytical jobs against data and interprets the supported table metadata. |
| **Atomic commit** | A publication step in which a table change becomes visible as a complete committed state rather than as a partially published state. The guarantee and scope must be checked for the chosen implementation. |
| **Interoperability** | The ability of different engines and tools to read or modify the same table correctly under a shared set of format, catalog, and feature guarantees. Reading the same file encoding alone is not full interoperability. |

**Scope boundary:** this lesson explains table-format concepts generically. It does not assume a specific table format. Later topics revisit physical layout (Topic 5), cross-system consistency (Topic 6), and retention and storage tiers (Topic 7).

## 4. Beginner-level learning sequence

### 4.1 Start with a simple analogy, then use precise terms

Imagine a library:

- **Storage system:** the building and shelves where physical books are kept.
- **Table format/table-management layer:** the rules and index that identify which pages or editions belong to the current, valid collection and how a new edition is published.
- **Catalog:** the registry that tells people where a collection is and how to locate it.
- **Query engine:** the reader or research service that interprets the index and retrieves relevant material.
- **Data platform:** the wider library operation—identity checks, staff workflows, monitoring, access policies, scheduling, and support.

The analogy is imperfect: digital systems may combine these functions, and a table format is not necessarily a separate deployed service. The important point is that **where bytes live** is not the same question as **what those bytes mean as a table**, and neither question is the same as **who can access or operate the whole environment**.

### 4.2 The layers and their responsibilities

| Layer or concern | Primary responsibility | Examples of capabilities | What it does not automatically provide |
|---|---|---|---|
| **Storage system** | Persists bytes and exposes storage operations | Object storage; file storage; warehouse-managed storage | Table schema, consistent table snapshots, SQL execution, business definitions |
| **Data files / file format** | Encodes records physically | CSV, JSON Lines, row-oriented binary records, columnar files | Table-level transaction protocol, global schema governance, coordinated concurrent commits |
| **Table format / table-management layer** | Defines managed-table metadata and change semantics | Commit metadata, snapshots, schema tracking, file membership, partition metadata, supported update/delete operations | Compute capacity, identity management, orchestration, organization-wide governance by itself |
| **Catalog / metastore** | Makes table definitions discoverable and links names to metadata | Names, locations or identifiers, schema references, table properties, registration and access integration | A guarantee that every engine supports every table feature; data processing itself |
| **Query / processing engine** | Reads and transforms data | SQL execution, batch processing, interactive analytics, model-training reads | Shared correctness if it ignores or misinterprets the table's metadata protocol |
| **Data platform** | Operates the environment end to end | Compute, catalog, governance, orchestration, identity, monitoring, lineage, access interfaces, cost controls | A single universal architecture or automatic compatibility among every component |
| **Business catalog / governance layer** | Describes data meaning, ownership, sensitivity, and approved use | Business glossary, classifications, lineage, stewardship, policy workflows | Physical table commits or file-level consistency by itself |

A single product may combine several rows. A warehouse service may manage storage, table metadata, cataloging, compute, access control, and monitoring behind one interface. A lakehouse design may assemble components from different providers. The logical responsibilities still exist even when users do not operate each one separately.

### 4.3 What is a data warehouse?

A **data warehouse** is an analytical data environment designed to make governed, integrated data available for reporting, analysis, and often business intelligence (BI). Common characteristics include:

- managed analytical storage and metadata;
- SQL-oriented access and optimisation;
- integration of data from multiple source systems;
- controls for users, roles, and sometimes finer-grained data access;
- workload management, monitoring, and operational support.

**Benefits:** a relatively integrated operating model, mature analytical query capabilities, and fewer separately managed components for many workloads.

**Limitations and risks:** cost and scaling behaviour depend on the service and workload; data and metadata may be less portable than a file-oriented design; non-SQL, unstructured, or specialised processing may require additional systems; and a warehouse does not eliminate data modeling, quality, governance, or retention work.

The term does not guarantee a specific transaction model, security feature, performance level, or portability property. Those must be verified for the actual service and configuration.

### 4.4 What is a data lake?

A **data lake** is a storage-centered architecture for keeping data from different sources and at different levels of processing, often as files or objects. It commonly separates raw or landed data from standardized and curated datasets.

**Benefits:** flexible ingestion, support for varied data types and formats, potential reuse of source data, and a separation between storage and many compute choices.

**Limitations and risks:** raw files may lack enforced schema, coordinated updates, a single authoritative table state, or dependable concurrent-write behaviour. Discovery, quality, permissions, lifecycle policies, and small-file management must be designed. A lake can be well governed, but governance does not arise automatically from storing data in a lake.

A lake can contain managed tables, warehouse exports, files for machine learning, and non-tabular objects. “Lake” describes a broader storage pattern, not one mandatory file format or one query engine.

### 4.5 What is a lakehouse?

A **lakehouse** is a pattern that commonly places a table-management layer over lake-style storage and uses one or more engines to access managed tables. It aims to combine some of the openness and storage flexibility of a lake with table-level capabilities commonly associated with warehouses.

A conceptual arrangement is:

```text
Consumers and workloads
  BI / SQL analytics     Data science / ML     Batch processing
          \                    |                    /
           +--------- Query / processing engines --+
                              |
                    Catalog / metastore
                              |
                Table format / table metadata
          schema • commits • snapshots • file membership
                              |
             Data files in a storage system
        object storage / file storage / other supported storage

Cross-cutting platform services:
identity and permissions • governance • orchestration • monitoring
lineage • quality checks • cost management • operational ownership
```

The diagram is conceptual, not a required deployment topology. Catalog calls, metadata storage, identity, and execution may be integrated or distributed differently by implementation.

**Potential benefits:** multiple compatible engines can work on shared data; file and table choices may be more open; data can serve analytical and machine-learning workloads without always copying it into a separate store; and versioned table states can improve recovery and auditability.

**Limitations and risks:** these benefits depend on supported features and disciplined operations. A lakehouse can require substantial engineering for catalog integration, engine compatibility, compaction, metadata maintenance, schema changes, permissions, snapshot expiration, and recovery. It is not automatically cheaper or faster than a warehouse.

### 4.6 Table format versus database versus platform

A **table format/table-management layer is not a database and is not an entire platform**. It describes how a managed table's state and changes are represented and interpreted. It may enable transaction-like behaviour over files, but it does not independently provide every capability of a database service.

A **database or warehouse service** may package storage, metadata, query execution, security, workload management, and operational features. A **data platform** is broader still: it includes the technology and operating processes that make data available and safe to use.

A platform may combine several technologies—for example, a managed warehouse for high-concurrency reporting, object storage for source archives, and a table-management layer for shared curated data. Conversely, a table format may be used by several engines within one platform or across more than one platform, subject to compatibility and governance constraints.

### 4.7 Why plain files alone are insufficient for managed-table guarantees

Suppose a job writes a day's transactions into a folder as many files. A reader lists the folder while the job is still writing. Without a defined table-management protocol, the reader may see only some files, duplicate output from a retry, or files from different logical versions. A schema may be inferred differently by different readers. A delete operation may remove one file while another copy or older version remains elsewhere.

A folder and a file format answer questions such as “how are records encoded?” and “where are these objects stored?” They do not, on their own, define:

- which complete set of files constitutes the current table;
- how concurrent writers detect conflicting changes;
- whether readers see a consistent committed state;
- how schema changes are tracked and validated;
- which previous versions are available for time travel;
- how updates and deletes are represented and made visible;
- how table names resolve consistently across engines.

A table format can define mechanisms for these concerns, but the actual guarantees depend on its protocol, implementation, catalog, storage assumptions, and engine support. Do not infer that a file format such as Parquet or CSV provides table-level transactions merely because it can encode rows.

### 4.8 Beginner check: answer before moving on

1. If bytes are stored in object storage, which layer answers how those bytes are physically persisted? **Storage system.**
2. If an engine needs to know which files belong to version 42 of a table, which mechanism supplies that table state? **The table metadata/commit protocol, typically discovered through a catalog or equivalent metadata reference.**
3. If a team needs identity management, scheduled jobs, monitoring, lineage, and cost controls, is a table format alone sufficient? **No; these are platform and governance responsibilities.**
4. If two engines can read the same columnar file encoding, does that prove they can safely write the same managed table? **No; format, catalog, commit, and feature compatibility must be verified.**

### 4.9 Layer-mapping exercise: place the capability in the right layer

For each item, identify its primary layer. Some capabilities span layers; choose the layer primarily responsible and note any dependency.

| # | Capability to classify | Your answer |
|---:|---|---|
| 1 | Persisting object bytes under a key | __________________ |
| 2 | Encoding rows into a columnar binary file | __________________ |
| 3 | Recording which data files belong to a committed table version | __________________ |
| 4 | Registering a table name and resolving it to metadata | __________________ |
| 5 | Executing a SQL query over selected columns | __________________ |
| 6 | Scheduling a nightly ingestion workflow and retrying failed tasks | __________________ |
| 7 | Tracking a table schema and validating a supported schema change | __________________ |
| 8 | Defining organization-wide ownership and business meaning for a sensitive field | __________________ |
| 9 | Publishing a new table state so readers do not see a half-committed table update | __________________ |
| 10 | Enforcing user or role permissions for a query | __________________ |
| 11 | Compacting many small data files into fewer files while preserving table correctness | __________________ |
| 12 | Monitoring job failures and allocating operational ownership | __________________ |
| 13 | Reading a prior table snapshot for an audit query | __________________ |
| 14 | Applying an access policy consistently across storage, catalog, and query interfaces | __________________ |

**Answer guidance**

| # | Primary layer | Reason / dependency |
|---:|---|---|
| 1 | Storage system | It persists and exposes the object. |
| 2 | Data file / file format | It defines the physical encoding, not table-level transactions. |
| 3 | Table format / table-management layer | Commit metadata or equivalent identifies the committed file set. |
| 4 | Catalog / metastore | It makes the table discoverable and resolves its metadata reference. |
| 5 | Query / processing engine | The engine plans and executes the query, using metadata it understands. |
| 6 | Data platform / orchestration | Workflow scheduling and retries are platform operations. |
| 7 | Table format plus schema governance | The table layer tracks schema; platform policy and producer/consumer compatibility may add controls. |
| 8 | Business catalog / governance | Ownership, classification, and meaning are governance concerns. |
| 9 | Table format / commit protocol | Atomic publication is a table-management guarantee, subject to implementation and storage assumptions. |
| 10 | Platform security and/or engine/catalog | The exact enforcement point varies; permissions must cover all access paths. |
| 11 | Platform maintenance job using table-aware operations | Compaction is operational work, but it must respect the table format's commit protocol. |
| 12 | Data platform / operations | Monitoring and ownership are operational capabilities. |
| 13 | Table format plus compatible engine | The table metadata identifies the snapshot; the engine must support querying it. |
| 14 | Platform governance and security architecture | Effective enforcement spans the relevant access paths and components. |

The mapping is intentionally not a claim that every capability lives in one standalone product. The point is to identify responsibility, interface, and dependencies. A managed product may implement multiple layers behind one API.

## 5. Intermediate-level learning sequence

### 5.1 How managed-table metadata works conceptually

A table stored as files needs a reliable description of which files are logically part of the table. A table-management layer typically stores metadata that points to data files and describes properties such as schema, partition values, file statistics, and table versions. The exact metadata structures and publication protocol differ by implementation.

A simplified conceptual model is:

```text
Catalog entry: finance.transactions
            |
            v
Table metadata / current commit reference
            |
            v
Snapshot S42
   | schema version
   | partition information
   | file references and optional statistics
   +---- file A
   +---- file B
   +---- file C
```

This is a teaching model, not a prescribed on-disk layout. Some implementations use a sequence of transaction-log entries; others use metadata files, manifests, snapshot references, or a combination. Avoid assuming every implementation has an object literally named “manifest” or stores all metadata in one place.

The engine uses the catalog to resolve the table, reads metadata through the supported protocol, determines the relevant file set, and then reads those files. The metadata layer helps the engine avoid treating every object in a storage prefix as current table data.

### 5.2 Commit sequence and reader visibility

A generic table update can be described in stages:

1. A writer reads the current table state and determines the intended change.
2. It writes new data files, and may write additional metadata, without yet making those files part of the committed table state.
3. It attempts to publish a new commit referencing the correct file set and metadata.
4. The commit mechanism checks relevant conflicts or preconditions according to the implementation.
5. If the commit succeeds, readers that resolve the new state can see the new snapshot. Readers already using the prior snapshot may continue to see that prior consistent state.
6. If the commit fails, the new files may be unreferenced or otherwise require cleanup; they must not be assumed to be part of the table simply because they exist in storage.

The critical idea is **atomic publication of table state**, not necessarily a single atomic write of every data file. Data files may be written separately; the commit protocol determines when they become visible as table content.

This model has important qualifications:

- The implementation must document its atomicity and isolation guarantees.
- A failed writer can leave unreferenced files, which may require a safe orphan-cleanup process.
- Concurrent writers may conflict if they both modify overlapping state or assumptions. Retry logic must re-read the latest state and re-plan when required; blindly replaying an old commit can corrupt results or repeatedly fail.
- Atomicity across one table does not imply atomicity across multiple tables, external systems, or an entire pipeline. Cross-table guarantees must be separately verified.
- Readers and writers must use compatible implementations of the table protocol. A tool that directly lists and reads files while ignoring metadata may observe incomplete or stale results.

### 5.3 Snapshots, versions, and time travel

A **snapshot** represents a logically consistent table state. A later commit may add files, remove files from the current view, update metadata, or change schema. A time-travel query asks an engine to read a supported historical snapshot or version rather than the current one.

Useful applications include:

- reproducing a report or model input from a prior table state;
- investigating when data changed;
- comparing before-and-after states;
- recovering from certain logical mistakes, if the relevant data and metadata remain available and the implementation supports the recovery operation.

A snapshot is not necessarily a full physical copy of every row. Multiple snapshots may reference the same unchanged data files. However, files superseded by later updates may remain stored while historical snapshots reference them. Metadata also consumes storage and may increase planning work. Therefore, snapshot retention has real cost even if snapshots share files.

Time travel is not a substitute for a complete backup, disaster-recovery plan, or business audit process. It can fail to help if the relevant metadata or data files have been expired, corrupted, deleted, or made inaccessible. A rollback may itself create a new commit rather than erase history; the exact semantics depend on the implementation.

### 5.4 Schema tracking and evolution

Managed-table metadata commonly records the table schema and may define rules for schema changes. A schema change can affect current readers, old snapshots, and downstream jobs.

Examples:

- **Add a nullable column:** may be compatible with many readers, but only if engines and downstream consumers handle the new field as expected.
- **Rename a column:** may be safe only if the table metadata preserves column identity or the ecosystem has a coordinated rename mechanism. A simple name-based reader may treat it as a missing old column plus a new column.
- **Change a data type:** may require validation or rewriting, and may not be compatible with all existing data or engines.
- **Remove a column:** can break consumers and may not remove values from old snapshots or historical files.
- **Change nested fields or nullability:** compatibility depends on the schema model and implementation.

Do not call a change “safe” solely because the table metadata accepted it. Validate producers, all consuming engines, historical snapshots, data quality checks, and downstream contracts. This lesson connects to schema evolution in the data-modeling stage; it does not replace that topic.

### 5.5 Partition metadata and manifests

A table-management layer may track partition values and file-level statistics. Query engines can use this information to avoid reading irrelevant files, depending on the engine, query predicates, metadata quality, and physical layout.

A **manifest** commonly describes a set of data files and associated metadata. Manifests or equivalent structures can help engines discover the table's contents without listing and inspecting every object. This can improve planning efficiency at scale, but it also creates metadata that must be updated, compacted, or otherwise maintained when files change.

Important distinctions:

- **Partition metadata** describes logical grouping and values; it does not itself guarantee that the physical layout is optimal.
- **File statistics** may help skip data, but they are only useful when correctly produced and interpreted by the engine.
- **Metadata pruning** can reduce planning or scan work, but its effect must be measured against actual queries.
- Topic 5 covers partitioning, indexing, clustering, and data layout in detail. Here, focus on how the table layer represents and coordinates those choices.

### 5.6 Updates, upserts, merges, and deletes

An **upsert** updates a matching record or inserts it if no match exists. A **merge** often combines matched updates/deletes with unmatched inserts according to a condition. The semantics depend on the data model and operation definition.

Files are often immutable or treated as immutable once written. A table implementation may therefore apply updates by rewriting affected files, recording delete information, creating replacement files, or using another supported mechanism. Different designs have different read amplification, write amplification, metadata, and maintenance consequences.

Capabilities vary. Before assuming that a table supports row-level deletes, merge operations, concurrent upserts, or efficient deletes, verify:

1. the table format's specification and the selected implementation's supported feature set;
2. the engine's support for the operation and its version;
3. catalog and concurrency requirements;
4. isolation and conflict behaviour;
5. how deleted or replaced records are handled in old snapshots;
6. the cleanup and retention process needed to reclaim storage.

A logical delete from the current table view does not necessarily mean the bytes have been physically erased. Old snapshots, retained files, replicas, caches, exports, and downstream copies may continue to contain the value.

### 5.7 Catalogs, metastores, and engine discovery

A **catalog** or **metastore** commonly maps a table name to a location or identifier and supplies table properties or a reference to table metadata. It gives engines a shared way to discover a table instead of relying on each user to manually locate a folder.

A typical discovery path is:

1. The user submits a table name to an engine.
2. The engine asks its configured catalog to resolve the name and retrieve the table definition or metadata reference.
3. The engine reads the table metadata using a supported protocol.
4. The engine plans the query using the schema, snapshot, file membership, partition information, and any supported statistics.
5. The engine reads the relevant data files and returns results.

A **technical catalog/metastore** is not identical to a **business catalog**. The technical catalog helps software locate and interpret tables. A business catalog commonly adds business definitions, ownership, sensitivity classifications, lineage, and stewardship workflows. These may be integrated, but the distinction remains useful.

A catalog entry does not automatically guarantee that every engine interprets a table the same way. Check whether engines share the same catalog, authentication model, table-format protocol, feature support, and concurrency rules. Separate catalogs that point to the same storage location may disagree about metadata or ownership unless coordinated.

### 5.8 Multi-engine interoperability

Interoperability means more than “engine A and engine B can both read Parquet.” A credible shared-table design needs compatible behaviour for:

- locating the table and its current metadata;
- interpreting schema, types, partition metadata, and snapshots;
- respecting the commit protocol when writing;
- supporting the features used by the table, including updates or deletes where needed;
- handling concurrent operations, conflicts, retries, and failures;
- applying identity and permissions consistently;
- preserving correct results after maintenance operations such as compaction or snapshot expiration.

A read-only engine may be compatible for a narrow workload while not being qualified to write. An engine may support basic reads but not a newer feature or a particular schema change. Compatibility matrices and versioned integration tests are more reliable than assuming that a format's openness guarantees universal support.

### 5.9 Intermediate exercise: explain an upsert and concurrent read

**Scenario:** Table `risk.card_activity` is at snapshot `S42`. A writer wants to update a transaction's risk category and insert a new transaction. A dashboard query starts while the writer is working.

Write a numbered explanation that covers:

1. how the writer discovers `S42`;
2. how it determines which records are affected;
3. what files or metadata it may write before committing;
4. what the dashboard sees if it began against `S42`;
5. what a new reader sees after the commit succeeds;
6. what happens if a competing writer changes overlapping state first;
7. what unreferenced files or stale snapshots may require later;
8. why this single-table explanation does not prove atomicity across a risk table and a finance table.

**Answer guidance:** the writer resolves the current metadata, plans from a known snapshot, writes candidate changes, and attempts a commit under the implementation's conflict rules. A reader already bound to `S42` should continue to read that consistent state if the engine and implementation provide snapshot isolation as assumed. After a successful commit, a new reader resolves the newer snapshot. A conflicting writer may force a retry or fail. Cleanup must be table-aware and safe. Cross-table consistency requires separate guarantees or a workflow-level design.

## 6. Advanced-level learning sequence

### 6.1 Transaction guarantees and concurrency limits

Do not reduce transaction behaviour to a checkbox called “ACID” (atomicity, consistency, isolation, durability). Ask which guarantees are implemented and in what scope.

| Question | Why it matters | Evidence to obtain |
|---|---|---|
| What is the atomic commit boundary? | A table commit may not cover a pipeline or multiple tables. | Specification, implementation documentation, failure tests |
| What isolation does a reader receive? | Readers may see an older consistent snapshot or a newer committed state. | Documented read semantics and concurrent-read tests |
| How are write conflicts detected? | Two writers may change the same table or overlapping partitions. | Conflict rules, retry behaviour, test results |
| What happens on retry? | Replaying stale assumptions may duplicate or lose intended changes. | Idempotency design, re-read/re-plan logic, failure injection |
| Are multi-table commits supported? | A business transaction may update multiple related tables. | Explicit multi-table guarantee; otherwise design a reconciliation or publication workflow |
| What are the storage assumptions? | Atomic metadata publication may rely on specific storage and catalog semantics. | Supported storage/catalog combinations and documented assumptions |

High write contention on a hot partition or common table state can increase conflicts. Possible mitigations include separating ownership, reducing overlapping write windows, batching changes, using a different partitioning or table design, or serializing selected writers. Each option should be validated against freshness, throughput, and correctness needs. Do not promise conflict-free writes without evidence.

### 6.2 Metadata management at scale

As a table accumulates files, commits, manifests, statistics, and snapshots, metadata can grow. Query planning may become slower if an engine must process a large metadata graph or many small files. Table maintenance may include:

- **Compaction:** rewriting small files into a more suitable file set while preserving logical table contents.
- **Metadata compaction or consolidation:** reducing the overhead of reading a long sequence of commit or metadata records, where the implementation supports it.
- **Snapshot expiration:** removing old snapshot references after the retention policy allows it.
- **Orphan-file cleanup:** finding files not referenced by valid table metadata and deleting them only after a safe grace period and validation.
- **Statistics refresh or recomputation:** where supported and needed for planning.
- **Schema-change coordination:** testing producers and consumers before incompatible changes.

These are not interchangeable jobs. Compaction changes physical files; snapshot expiration changes historical availability; orphan cleanup removes unreferenced objects; metadata consolidation changes how metadata is represented. Their schedules, safety checks, and owners should be explicit.

Maintenance can itself create load, write amplification, temporary storage growth, or commit conflicts. A cleanup process that deletes files without consulting table metadata can break readers or historical snapshots. Conversely, never cleaning up can increase storage cost and planning complexity.

### 6.3 Maintenance and snapshot-retention arithmetic

A simple first-order estimate is:

```text
retained_storage ≈ live_data_storage + retained_superseded_data + metadata_storage
```

If a workload rewrites data, a rough estimate for retained superseded data is:

```text
retained_superseded_data ≈ daily_rewritten_data × retention_days
```

This is a planning approximation, not a universal formula. It assumes a relatively steady rewrite rate and that the rewritten bytes remain retained throughout the period. It can overestimate or underestimate actual use because snapshots share unchanged files, rewrites vary, deletes and compaction have different patterns, and metadata or temporary files add overhead. Measure actual storage and use the implementation's retention semantics.

**Illustrative example — not a benchmark or universal storage multiplier**

Assumptions:

- Current live table data: `100 TB`.
- Average data rewritten or superseded each day by merges and corrections: `2 TB/day`.
- Superseded files remain physically retained for `7 days` because historical snapshots can reference them.
- Ignore metadata, replicas, temporary compaction output, compression changes, and other datasets for this first-order estimate.

Calculation:

```text
retained superseded data ≈ 2 TB/day × 7 days = 14 TB
estimated table data stored ≈ 100 TB + 14 TB = 114 TB
```

The `114 TB` estimate is only a simplified illustration. It is not a guarantee that seven days of snapshots add exactly 14 TB. Use observed rewrite volume, snapshot references, physical storage metrics, and the selected implementation's cleanup behaviour to refine the estimate.

**Why retention is an architecture decision:** longer time-travel windows can help audits and recovery but can retain superseded data and personal information. Shorter retention may reduce cost and exposure but can limit recovery and reproducibility. A retention policy should identify the business purpose, minimum required history, maximum permitted retention, deletion obligations, and accountable owner.

### 6.4 Time travel, deletion, and erasure obligations

Time travel and data erasure can conflict. Deleting a record from the current table state may only remove it from the current logical view. The value may remain in:

- old snapshots and files referenced by them;
- delete markers or change files, depending on implementation;
- replicas, exports, caches, backups, and downstream copies;
- source archives or logs outside the table;
- derived datasets and model-training extracts.

For personal data subject to an erasure obligation, the architecture must define what “deleted” means and how it is proven. The exact legal interpretation depends on the applicable requirements and legal advice; do not infer a universal legal rule from a table format.

A defensible design should:

1. identify the authoritative source and every known copy or derivative;
2. determine whether deletion is logical, physical, or both for each layer;
3. define how snapshots are expired or rewritten and when underlying files can be safely reclaimed;
4. account for replicas, caches, exports, and backup expiry or exception processes;
5. prevent a rollback or reprocessing job from reintroducing erased data;
6. retain only the history justified by audit, recovery, and legal requirements;
7. record evidence of the deletion workflow without retaining the sensitive value in the evidence itself.

If a system cannot selectively remove a value from retained immutable data, the policy may require a controlled rewrite or expiration of the affected files and snapshots. That can be expensive and must be tested. Do not promise immediate physical erasure if the architecture only guarantees removal from the current logical table view.

### 6.5 Schema evolution across historical snapshots and engines

Schema compatibility is a system property, not just a metadata update. A new schema may be accepted by the table layer yet cause a consumer to fail, reinterpret data, or return inconsistent results. Historical snapshots can retain older schemas and old files, so readers may need to interpret multiple schema versions.

A schema-change validation plan should include:

- intended semantic change and compatibility classification;
- representative old and new files;
- current and historical snapshot reads;
- every engine and connector in the supported matrix;
- null, missing-field, nested-field, and type-conversion behaviour;
- downstream models, reports, data contracts, and data-quality rules;
- rollback or forward-fix steps and their limits;
- effect on personal data, retention, and physical rewrites.

A column rename that works in one engine may appear as a dropped and added column in another if identity metadata is not interpreted consistently. A type widening that one engine supports may be unsupported or lossy in another. Document these cases rather than assuming “open format” means identical semantics everywhere.

### 6.6 Openness, portability, and lock-in

Openness is multidimensional. Evaluate separately:

1. **Data-file openness:** can data be read using documented file encodings and tools?
2. **Table-metadata openness:** is the table state represented by a documented format or protocol that independent implementations can use?
3. **Catalog portability:** can table registrations, identities, and metadata references be migrated without relying on proprietary services?
4. **Engine interoperability:** can the chosen engines read and, where needed, write the same features correctly?
5. **Governance portability:** can access policies, lineage, and audit evidence move with the data or be reconstructed?
6. **Operational portability:** can the team operate compaction, snapshots, recovery, monitoring, and upgrades outside one managed platform?

A file format can be open while the surrounding catalog, security model, or operational services are proprietary. A managed warehouse can be operationally simpler while creating dependency on its query interface, metadata model, or export process. Neither “open” nor “managed” is an automatic verdict; identify the exit requirements and test a realistic migration path.

### 6.7 Cost and total cost of ownership

A fair comparison includes more than the price per stored terabyte. Consider:

- storage and retained historical data;
- compute for ingestion, transformations, interactive queries, and maintenance;
- data transfer, requests, and retrieval charges where applicable;
- duplicated data between a warehouse and lakehouse;
- catalog, governance, orchestration, monitoring, and security services;
- engineering time for table maintenance, compatibility testing, and incident response;
- operational on-call burden and skills availability;
- migration and exit costs;
- costs of meeting recovery, audit, and erasure requirements.

A managed warehouse may reduce the number of components the team must operate, though its actual unit cost and lock-in must be evaluated. A lakehouse may improve reuse and portability but require stronger engineering ownership. A hybrid may be justified when workloads have materially different needs, but it introduces synchronization, duplication, and policy consistency costs.

**Illustrative TCO worksheet — fill with local evidence, not assumed prices**

| Cost category | Warehouse-only | Lakehouse-oriented | Combined |
|---|---|---|---|
| Primary storage and history | Estimate from measured retained data | Estimate object/file data plus snapshots and metadata | Count both systems and overlap |
| Query/processing compute | Measure BI and transformation workload | Measure each engine and maintenance job | Measure warehouse and lakehouse workloads separately |
| Ingestion and data movement | Include required loading/replication | Include file ingestion and table commits | Include cross-system sync and retries |
| Governance and catalog | Include service and operating costs | Include catalog integration and policy enforcement | Include policy synchronization and duplicated controls |
| Maintenance engineering | Include platform operations and modeling | Include compaction, snapshot expiry, cleanup, compatibility | Include both sets plus reconciliation |
| Retention/erasure | Test supported deletion and history policy | Test snapshots, files, and all copies | Test both stores and the movement path |
| Exit/migration | Estimate export, conversion, and revalidation | Estimate metadata/catalog/engine migration | Include both platforms and cross-system dependencies |

A TCO sketch should record the time horizon, currency, unit assumptions, usage profile, retention window, growth, staffing assumptions, and uncertainty. Avoid comparing a warehouse's fully managed cost with a lakehouse's storage bill while omitting compute and people costs.

### 6.8 Structured option-evaluation framework

Score each option against the actual workload. The table below is a starting framework, not a universal ranking.

| Criterion | Warehouse-oriented | Lakehouse-oriented | Combined warehouse + lakehouse |
|---|---|---|---|
| BI and concurrent SQL reporting | Often a strong default when the selected service meets concurrency and latency needs; validate with representative queries | Can work well when engines and table layout meet workload needs; validate planning and concurrency | Keep high-concurrency or tightly governed reporting in the warehouse when evidence supports it |
| Varied data and ML workflows | May require staging, exports, or additional services for some data types/workloads | Often flexible for file-oriented and distributed processing; feature support varies | Can preserve flexible lake storage and provide a separate serving environment |
| Table transactions and history | Service-specific managed semantics; verify scope and retention | Depends on table format, catalog, engine, and commit protocol | Must verify guarantees separately in each store and during movement between them |
| Governance | May be integrated in the service; still requires correct policy design | Can be strong but may span storage, catalog, engine, and orchestration | Must reconcile identities, classifications, lineage, and deletion across both |
| Interoperability and openness | Service interfaces and export paths determine portability | Potentially strong at file/table layers, but catalog and feature support matter | Requires interoperable movement and consistent definitions across systems |
| Operational complexity | Often fewer separately managed components | More responsibility for compatibility and table maintenance unless managed | Highest component and synchronization burden in many designs |
| Cost drivers | Compute/usage model, storage, concurrency, data movement, service charges | Storage, compute, metadata, maintenance, requests, staffing | Duplicate storage/compute plus synchronization and two operating models |
| Skills and staffing | SQL, modeling, warehouse operations, governance | Distributed processing, table protocol, catalog, storage and maintenance | Both skill sets plus integration and reconciliation |
| Concurrency | Verify service-specific transaction and workload guarantees | Verify concurrent-write protocol, conflict behaviour, and engine support | Verify each store and any cross-store publication consistency |
| Data openness | Depends on export formats, metadata, and service coupling | Depends on open file/table metadata and compatible engines | Depends on both stores and the portability of data movement/contracts |
| Maintenance obligations | Service-managed work may reduce but not eliminate customer responsibility | Compaction, metadata, snapshot retention, schema compatibility, cleanup | Lakehouse maintenance plus warehouse operations and sync/reconciliation |
| Best fit when | Governed SQL analytics dominates and managed operation is valuable | Shared file-based analytical data, multiple compatible engines, or flexible processing is a priority | Distinct workload needs justify the additional integration and duplicated operations |

**Decision method:** define must-have constraints first; then score viable options against workload evidence, governance, skills, cost, and operational risk. Document which criteria are hard gates and which are preferences. Do not hide a hard compliance or correctness requirement inside an averaged score.

### 6.9 Validation criteria before selecting an architecture

Validate a candidate with a proof of concept and operational tests, not a product label or a synthetic benchmark alone.

| Area | Validation test | Evidence to retain |
|---|---|---|
| Workload fit | Run representative BI, batch, and ML/data-science queries using realistic data volume and concurrency | Query plans, result correctness, latency/throughput distributions, resource use; label test conditions |
| Commit correctness | Inject writer failure before and during commit; inspect reader-visible states | No partial table state exposed beyond documented semantics; recovery steps recorded |
| Concurrent writes | Run overlapping writers, including a hot partition or shared key case | Conflict rate, retry success, lost/duplicate update checks, runbook |
| Catalog and engines | Read the same table from every planned engine; test supported writes and schema changes | Versioned compatibility matrix and reproducible integration tests |
| Schema evolution | Add, rename, widen, and remove fields in a controlled test as applicable | Expected results for current and historical snapshots and all consumers |
| Snapshot and erasure | Delete a synthetic personal-data record, expire or rewrite history under policy, and inspect all known copies | Evidence of logical and physical deletion behaviour, timing, and limitations |
| Maintenance | Generate small files and superseded data; run compaction, snapshot expiration, and orphan cleanup in a test environment | Correctness checks, storage before/after, job duration, conflict/rollback handling |
| Security | Test authorized and unauthorized access through each engine and direct storage path | Evidence that policies are enforced consistently; documented bypasses and mitigations |
| Cost | Measure storage, compute, requests, transfer, maintenance, and engineering effort over a representative window | Assumptions, units, workload profile, uncertainty, and reproducible cost model |
| Portability | Export or migrate a representative table and metadata to the intended alternative | Data correctness, schema fidelity, history/metadata loss, downtime and manual work |

A validation result is valid only for the tested versions, configuration, data shape, and workload. Record those conditions. If the evidence is inconclusive, state what remains unknown rather than claiming the option is proven.

## 7. Industry-application exercises

### Exercise 1 — Design Northbridge Bank's analytical storage

**Northbridge Bank is a fictional illustrative case.** No actual bank data, production requirements, vendor selection, or measured performance is implied.

Assume the bank needs to combine:

- card transactions for risk and fraud analysis;
- finance data for controlled reporting and reconciliation;
- selected customer attributes that may include personal data;
- historical source records for investigation;
- analytical data for batch feature generation and model development.

The bank has a small platform team and wants reliable operations. Exact data volume, freshness targets, concurrency, retention periods, legal obligations, and budget are **not specified**; your first task is to identify them as discovery questions, not invent values.

Produce three designs:

1. **Minimal baseline:** one managed analytical environment or one clearly bounded storage-and-query approach that meets the confirmed requirements with the fewest operational components.
2. **Lakehouse alternative:** object storage plus a selected table-management approach, catalog, compatible engines, governance controls, and named maintenance ownership.
3. **Combined alternative:** a lakehouse or lake for broad source/ML reuse plus a warehouse for a justified reporting or serving workload.

For each design, include:

- logical layers and data flow;
- table/file representations at each stage;
- catalog and engine assumptions;
- transaction and concurrency boundaries;
- security, governance, and personal-data controls;
- snapshot/time-travel and deletion policy;
- maintenance tasks and named roles accountable for them;
- storage, compute, transfer, staffing, and duplication cost drivers;
- at least one rejected alternative and the reason for rejecting it;
- validation tests and the evidence needed before approval.

**Do not assume a combination is automatically more mature.** If one system meets the confirmed workload and governance needs, the extra platform may be unnecessary complexity.

### Exercise 2 — Layer mapping and architecture review

Use the 14-item layer-mapping exercise in Section 4.9. Then select any three items that span layers—for example, permissions, compaction, and schema evolution—and explain:

1. which component performs the immediate operation;
2. which other layers it depends on;
3. who owns the end-to-end result;
4. what failure would look like if one layer were misconfigured.

### Exercise 3 — Commit conflict and recovery

Two teams write to the same managed table during the same time window. Their jobs sometimes fail with commit conflicts.

Create a troubleshooting plan that distinguishes:

- a genuine overlapping-write conflict from an authentication, catalog, or storage failure;
- safe retries from unsafe blind replay;
- workload changes (batching, ownership separation, scheduling) from table-design changes;
- evidence needed to show no duplicate, missing, or stale records;
- how a reader behaves while commits are in progress;
- whether a related second table can be updated atomically (do not assume so).

Your plan must name an owner for the conflict policy and define a measurable acceptance criterion based on the workload's actual requirements.

### Exercise 4 — Storage cost grows without live-data growth

Assume the current logical table size is stable, but physical storage increases over several weeks. Investigate possible causes:

- retained snapshots referencing superseded files;
- high rewrite volume from merges or compaction;
- small-file proliferation and extra metadata;
- orphan files left after failed jobs;
- duplicate exports or copies outside the table;
- retention rules that do not match the intended policy.

Create a diagnostic checklist that compares logical live data, physical object storage, referenced historical files, metadata size, job history, and cleanup logs. Do not assume snapshots are the cause until the evidence supports it.

### Exercise 5 — Time travel versus erasure

A synthetic customer record must be erased, but historical snapshots are retained for investigation.

Document:

1. the definition of deletion that applies to this case;
2. every known system and copy to inspect;
3. whether the table implementation can remove the value from retained snapshots;
4. snapshot expiry, file rewrite, backup, replica, cache, and export handling;
5. how to prevent reintroduction by replay or rollback;
6. the evidence retained to demonstrate completion without retaining the erased value;
7. the operational and storage costs of the chosen method.

Flag any legal interpretation for the responsible legal/compliance owner. A table-format operation alone cannot establish that all copies have been erased.

### Exercise 6 — Build a defensible option evaluation

Choose warehouse-oriented, lakehouse-oriented, and combined designs for a specified workload. Fill in the table below with evidence, not adjectives.

| Evaluation item | Required answer |
|---|---|
| Workload profile | Query types, concurrency, data variety, freshness, update pattern, and ML/BI needs |
| Hard constraints | Compliance, erasure, residency, interoperability, latency, recovery, and access requirements |
| Assumptions and unknowns | Values, units, sources, confidence, and owner to resolve each unknown |
| Candidate architecture | Components mapped to storage, table management, catalog, engines, and platform |
| Transaction model | Atomicity boundary, isolation, conflict detection, retries, and cross-table limitations |
| Maintenance | Compaction, metadata maintenance, snapshot expiry, orphan cleanup, schema changes, and owners |
| Cost sketch | Storage, historical data, compute, transfer, requests, staffing, duplication, and migration |
| Rejected alternative | Specific reason tied to a requirement or measured trade-off |
| Validation | Test cases, dataset/workload, success criteria, evidence, and known limitations |
| Decision and review trigger | Chosen option, decision owner, date/review point, and conditions that would reopen the choice |

## 8. Practical scenarios and case-based reasoning

### Scenario A — “The files are there, so the table must be complete”

A downstream query lists all objects under a date prefix and reads every file. A failed ingestion attempt left partial files, and a retry wrote a second copy of some records.

**Reasoning:** the prefix is a storage organization, not necessarily a committed table definition. Use a table-aware reader and a defined commit protocol, or design explicit ingestion manifests and idempotency for the raw-file workflow. Determine how retries are deduplicated and how incomplete attempts are quarantined. Validate counts, keys, and business invariants before publishing the data to consumers.

**Failure lesson:** object existence is not evidence that an object belongs to the current logical table state.

### Scenario B — “Storage cost doubled, but the current table size did not”

The logical table has approximately the same row count and current size, but the storage bill rises.

**Reasoning:** inspect retained snapshots and superseded files, rewrite/compaction patterns, orphan cleanup, metadata, replicas, exports, and lifecycle rules. Compare physical bytes with the files referenced by the current snapshot and by retained snapshots. Check whether retention jobs are failing or whether the rewrite workload changed.

**Failure lesson:** logical table size and physical bytes retained are different measures. Do not shorten snapshot retention until recovery, audit, and erasure requirements are understood.

### Scenario C — “Two engines read the table, so they can both write it”

An interactive SQL engine can read a table, and a batch engine can read the same columnar files. The team proposes allowing both to update the table.

**Reasoning:** reading the same file encoding proves only file-level compatibility. Test catalog resolution, table metadata interpretation, supported features, commit protocol, conflict detection, schema evolution, and permissions for both engines. If only one engine is qualified to write, enforce that ownership and keep other engines read-only until validated.

**Failure lesson:** shared storage is not a shared transaction protocol.

### Scenario D — “The platform calls itself a lakehouse”

A product description uses the word “lakehouse,” but it is unclear whether it exposes open table metadata, shared catalog access, or engine-independent writes.

**Reasoning:** ask what bytes are stored where, how a table's current state is represented, which catalog is authoritative, what commit and isolation guarantees exist, which engines can read and write each feature, how access policies are enforced, and what data/metadata can be exported. Test a representative table rather than deciding from marketing terminology.

**Failure lesson:** architecture is established by behaviour and guarantees, not by branding.

### Scenario E — “We need the lakehouse and warehouse because that is the modern pattern”

The team proposes two analytical systems before confirming workload requirements.

**Reasoning:** list the distinct workload that each system serves. If the warehouse is needed only because the lakehouse is unfamiliar, or the lakehouse only because it sounds cheaper, the design is not yet justified. Compare the incremental benefits against duplicated storage, pipeline synchronization, governance parity, data freshness, on-call ownership, and migration burden.

**Failure lesson:** hybrid architecture is a response to a demonstrated need, not a maturity badge.

### Scenario F — “Time travel means we can always recover or audit”

A team assumes a historical query can always reproduce an old report and prove a data value existed.

**Reasoning:** establish retention duration, metadata durability, file retention, engine support for historical reads, time-zone/version semantics where relevant, and whether the historical state has been expired. Separate reproducibility from legal evidence and disaster recovery. Validate a real recovery exercise and record the limits.

**Failure lesson:** historical query capability exists only while the required metadata and data remain available and valid.

## 9. Expected outputs and deliverables

Before marking this topic complete, produce the following artifacts in your own working notes or the roadmap's designated project location:

1. **Layer-distinction table** covering storage, file format, table-management layer, catalog/metastore, engine, platform, and business governance.
2. **Capability-placement exercise** with at least ten capabilities classified and justifications for cross-layer items.
3. **Table-format workflow** describing table discovery, read, commit, upsert/delete, conflict, failure, and cleanup behaviour.
4. **Option-evaluation matrix** comparing warehouse-oriented, lakehouse-oriented, and combined architectures against the workload and governance requirements.
5. **Maintenance and retention sketch** covering compaction, metadata maintenance, snapshot expiry, orphan cleanup, and responsible owners.
6. **Cost worksheet** with units, assumptions, retention window, rewrite volume, duplicated data, compute, transfer, and engineering effort. Distinguish illustrative estimates from measured values.
7. **Northbridge Bank logical design** with a minimal baseline, alternatives, explicit unknowns, and a rejected alternative.
8. **Validation plan** with representative workloads, failure injection, engine compatibility tests, security checks, and evidence to retain.
9. **Answers to Topic 4 practice questions**, corrected after checking the reasoning below.

### Topic 4 practice questions and answer guidance

**1. Why is a table format not a database?**

A table format defines how managed-table state and changes are represented and interpreted. It does not necessarily provide a complete query service, compute scheduling, identity system, organization-wide governance, operational tooling, or all database capabilities. Some platforms integrate these responsibilities, but they remain conceptually distinct.

**2. Can a platform exist without a particular table format?**

Yes. A platform can use a managed warehouse's own storage and metadata model, use several table-management technologies, or provide services around raw files and databases. The platform is the wider environment; a particular table format is one possible table-management component.

**3. What should a reader see if a writer fails halfway?**

Under a correctly implemented and supported atomic commit protocol, a reader should see a valid committed snapshot rather than a partially published table state. Files written before a failed commit may remain unreferenced and need safe cleanup. This answer must be qualified by the selected implementation's guarantees and the reader's use of the table protocol.

**4. How long should snapshots be retained?**

There is no universal duration. Set retention from recovery objectives, audit/reproducibility needs, data-change rate, storage cost, legal and policy requirements, and erasure obligations. Validate that the policy is enforced and that physical files can be reclaimed safely.

**5. How should an upsert with a transaction log be described?**

The writer resolves a current snapshot, plans matched updates and unmatched inserts, writes candidate files or change metadata, and attempts a commit under the table's conflict rules. Readers using an earlier snapshot continue to see that snapshot if the implementation provides the assumed consistency; new readers see the committed state after publication. A conflict may require re-planning or a retry. Old files may remain until safe expiration and cleanup.

**6. Which workload might still be better served by a managed warehouse?**

A workload dominated by governed SQL reporting, high concurrent access, and an operating model that values integrated management may favour a warehouse if a representative test confirms the required latency, concurrency, controls, and cost. This is a hypothesis to validate, not a universal product claim.

**7. Which maintenance task is most likely to be forgotten?**

There is no universal answer. Snapshot expiration, orphan cleanup, compaction, and metadata maintenance are common candidates because they may not be visible to a user who only sees successful queries. Select the risk that matches the proposed design and assign an owner, schedule, alert, and evidence of completion.

**8. How do you decide whether a “lakehouse” label matters?**

Ignore the label until the implementation's storage, table metadata, commit guarantees, catalog, engine compatibility, governance, retention, and operational responsibilities are understood. Test the capabilities required by the workload and compare the evidence with alternatives.

## 10. Common mistakes and misconceptions

1. **Treating storage, table format, and platform as interchangeable.** Bytes, table state, and operational services are different responsibilities even when packaged together.
2. **Calling any folder of columnar files a lakehouse.** A managed-table protocol, metadata discovery, and supported engines must exist for the required semantics.
3. **Assuming a table format is a database.** It does not necessarily supply a query engine, identity, governance, orchestration, or a complete operational service.
4. **Assuming a catalog guarantees correctness.** It helps resolve table definitions; correctness still depends on metadata, commit protocol, engine behaviour, and permissions.
5. **Assuming all engines support every table feature.** Compatibility must be verified for actual engine and connector versions and for the features in use.
6. **Assuming atomicity across multiple tables.** A single-table commit guarantee does not automatically cover a multi-table business transaction or an end-to-end pipeline.
7. **Treating snapshots as free copies or as free history.** Snapshots may share files, but superseded data and metadata can remain stored and incur cost.
8. **Confusing logical deletion with physical erasure.** Old snapshots, files, replicas, exports, and caches may retain values after they disappear from the current table view.
9. **Running generic object deletion against managed-table files.** Removing objects without consulting the table protocol can break current readers or historical snapshots.
10. **Assuming compaction is risk-free.** It consumes resources, can create temporary storage, and must coordinate with concurrent writers and snapshot retention.
11. **Ignoring metadata growth and small files.** Both can increase planning overhead and operational cost even if the logical data volume is stable.
12. **Calling schema evolution safe because the commit succeeded.** Consumers, engines, old snapshots, types, and contracts still need compatibility testing.
13. **Comparing only storage price.** Compute, transfer, catalog, governance, staffing, maintenance, duplicated data, and exit costs matter.
14. **Adding a warehouse and lakehouse without distinct workload reasons.** Hybrid designs create synchronization, duplication, policy, and on-call complexity.
15. **Choosing by vendor label or popularity.** Define required guarantees and validate them using the actual workload.
16. **Treating time travel as a backup or legal audit system.** Historical reads depend on retained data and metadata and do not automatically satisfy disaster-recovery or evidentiary requirements.
17. **Failing to name maintenance owners.** An unowned cleanup job is not an operating model.
18. **Using unqualified performance claims.** Results depend on data shape, query pattern, engine, layout, concurrency, configuration, and measurement conditions.

## 11. Mastery criteria

You have mastered this topic when you can demonstrate all of the following without relying on product marketing language:

- **Layer clarity:** explain the difference between storage, data files, table management, catalog, engine, platform, and business governance, including cases where one product combines them.
- **Mechanism accuracy:** explain how metadata, commits, snapshots, manifests or equivalents, schema tracking, and file references work together.
- **Failure reasoning:** describe what readers and writers can observe during a failed or concurrent commit, and identify the implementation guarantees that must be tested.
- **Qualified claims:** distinguish general table-format concepts from features that vary by implementation and engine.
- **Interoperability reasoning:** identify the catalog, format, engine, version, write-protocol, and security dependencies required for shared access.
- **Retention reasoning:** quantify a first-order estimate for retained superseded data, state assumptions and limitations, and explain how snapshots affect erasure.
- **Architecture selection:** compare warehouse, lakehouse, and combined designs against explicit workload, governance, operations, skills, openness, concurrency, and cost criteria.
- **Maintenance ownership:** assign responsible roles for compaction, metadata maintenance, snapshot expiry, orphan cleanup, schema change, and incident response.
- **Evidence-based validation:** specify representative tests and measurable acceptance criteria rather than claiming untested performance or guarantees.
- **Case-based judgment:** justify a minimal baseline for Northbridge Bank and state what new evidence would justify a lakehouse or combined architecture.

## 12. Completion gate

Do not mark Topic 4 complete until every item below is satisfied.

- [ ] The layer table and capability-mapping exercise have been reviewed; no storage/table-format/platform confusion remains.
- [ ] The table-format workflow explains discovery, read, commit, upsert/delete, concurrent conflict, failure, and cleanup.
- [ ] Transaction, snapshot, schema-evolution, and multi-engine claims are qualified by implementation and engine support.
- [ ] The architecture option evaluation compares warehouse-oriented, lakehouse-oriented, and combined designs against explicit workload and governance criteria.
- [ ] The selected option includes maintenance tasks, accountable owners, and a reasoned rejected alternative.
- [ ] The cost worksheet shows units, formulas, assumptions, retention duration, and rewrite volume; another reviewer can reproduce the arithmetic.
- [ ] The snapshot/time-travel section explicitly addresses storage growth, logical versus physical deletion, erasure obligations, replicas/copies, and retention policy.
- [ ] The Northbridge Bank case is labelled fictional and illustrative; unknown requirements are identified rather than invented.
- [ ] The validation plan covers workload fit, commit failures, concurrency, engine compatibility, schema evolution, permissions, maintenance, erasure, and portability where relevant.
- [ ] Topic 4 practice questions have been answered and corrected.

**Completion standard:** the architecture decision is defensible because its layers, guarantees, trade-offs, maintenance cost, retention/erasure impact, and validation evidence are explicit—not because it uses the label “warehouse,” “lakehouse,” or “open table format.”
