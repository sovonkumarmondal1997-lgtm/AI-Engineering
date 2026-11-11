# Object Storage and File Format Selection

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Distinguish block, file, and object storage by storage unit, access interface, update behavior, typical use, and limitations.
- Explain object keys, metadata, prefix-based logical organization, and why object storage is not a conventional file system or row-update database.
- Design a logical data-lake layout with explicit access-control, lifecycle, retention, and deletion rules.
- Compare row-oriented text, row-oriented binary/record, and columnar analytical formats against actual workloads.
- Explain schema representation and evolution, type fidelity, nulls, nested data, interoperability, compression, and column/predicate pruning.
- Estimate raw and compressed size, file count, and approximate scan time with stated units and assumptions.
- Diagnose small-file and metadata-overhead problems and propose a workload-appropriate compaction strategy.
- Recommend a storage layout and format with evidence, rejected alternatives, governance controls, and a validation plan.

**Scope:** This is a vendor-neutral architecture lesson. CSV, JSON Lines, Parquet, and other format names are illustrative examples, not endorsements or universal requirements. No storage-service-specific commands are required.

## 2. Why the topic matters in real-world data architecture

Storage organization and file format affect nearly every downstream operation: ingestion, query cost, interoperability, schema changes, security, retention, and deletion. A format that is easy to produce may be expensive to scan; a format that scans efficiently may be inconvenient for streaming writes or human inspection. A prefix layout that looks tidy may still be unsafe if access and lifecycle rules are unclear.

The architecture decision is not “Which format is most popular?” It is:

1. What data must be stored and for how long?
2. How will producers write it and consumers read it?
3. Which columns, records, time ranges, and filters do consumers need?
4. What schema changes are expected?
5. Which engines must interoperate?
6. What are the size, file-count, scan, governance, and operating-cost consequences?

### 2.1 Storage system versus file format versus layout

These are different decisions.

| Layer | Question answered | Example |
|---|---|---|
| Storage system | Where do bytes live, and through what interface are they accessed? | Object storage |
| File format | How are bytes encoded into records, fields, types, and metadata? | CSV, JSON Lines, a binary record format, Parquet |
| Logical layout | How are objects grouped and governed? | Prefixes by data domain, dataset, date, and processing state |
| Table-management layer | How are files managed as a logical table with metadata and coordinated changes? | A table format or catalog layer; covered in Topic 4 |

A file format does not itself provide every capability of a database or table-management layer. A folder-like prefix does not automatically enforce retention, access control, or transactional consistency.

**Check your understanding:** If data are stored as Parquet objects under date-based prefixes, which parts are the storage system, format, and logical layout?

## 3. Prerequisite knowledge

The roadmap expects the following:

- **Topic 1:** OLTP/OLAP workloads and operational/analytical separation.
- **Topic 2:** relational, NoSQL, and specialized database selection.
- **Module 2D.2 Topic 3:** data volume and growth estimation.
- **Module 2D.4 Topic 7:** schema evolution and backward compatibility.

You should be able to identify a dataset's producer, consumers, approximate volume, and important query patterns. You do not need deep storage-service administration knowledge.

If a required input is unavailable, record it as **Unknown** rather than silently inventing a value. For worked examples, this lesson labels invented figures as **illustrative assumptions**.

## 4. Beginner-level learning sequence

### 4.1 Distinguish block, file, and object storage

Think of the three as different interfaces for organizing and accessing bytes.

| Dimension | Block storage | File storage | Object storage |
|---|---|---|---|
| Storage unit | Addressable blocks exposed as a volume | Files and directories | Objects addressed by keys, with metadata |
| Access interface | Block-device read/write operations; a file system or database may sit above it | File-system operations such as open, read, write, rename, and directory traversal | Commonly API operations such as put, get, head, and list; exact interface varies |
| Update behavior | Can overwrite selected blocks | Can modify file contents according to file-system semantics | Commonly replaces an object by writing a new object version or replacing the whole object; do not assume arbitrary in-place byte/row updates |
| Typical use | Database volumes, virtual-machine disks, boot volumes | Shared team files, home directories, applications needing shared file semantics | Data lakes, backups, media, logs, archives, large datasets |
| Strength | Fine-grained random I/O when the stack is designed for it | Familiar shared file semantics and directory organization | Scalable object addressing, metadata, and lifecycle controls in many services |
| Limitation | The application or upper layer must manage data structures and semantics | Directory/file operations and scale depend on the file system and deployment | Not a conventional POSIX file system or row-update database; listing, request, and metadata behavior must be considered |

These are category-level tendencies, not guarantees for every implementation. Performance, durability, consistency, and update semantics depend on the particular system and configuration.

**Why it matters:** A data lake commonly stores files as objects. Writing a new object is straightforward, but changing one logical row inside a large object generally requires producing a replacement object or using a table-management layer that coordinates file-level changes.

**Example:** A transaction export containing 5 million rows is one object. To correct one row in a plain object, a pipeline may need to rewrite the object or write a corrected replacement and manage which version consumers should read. A table format can add higher-level update semantics, but that is a separate layer.

**When object storage is a poor fit:** An application that requires frequent, low-latency updates to individual records and multi-record transactions should not treat raw objects as its database.

**Check your understanding:** Why is “update customer 42 in this object” not the same operation as updating a row in a transactional database?

### 4.2 Object keys, metadata, and prefixes

An **object** is a stored payload plus system- or user-defined metadata. An **object key** identifies the object within a storage namespace. A **prefix** is a shared leading part of keys used to group objects logically.

For example, these keys might represent a dataset organized by processing area and event date:

```text
landing/card_transactions/ingest_date=2026-10-19/batch-001.jsonl
standardized/card_transactions/event_date=2026-10-19/part-0001.parquet
curated/card_transactions/month=2026-10/part-0001.parquet
```

The prefixes resemble directories, but object storage may implement them as naming conventions rather than real directories. Listing a prefix may require a metadata/list operation. Large numbers of objects can make discovery and listing expensive, depending on the service and client behavior.

Metadata can record information such as schema version, producer, ingestion timestamp, classification, or checksum. Do not put secrets, personal identifiers, account numbers, or other sensitive values in object keys: keys can appear in logs, audit trails, URLs, monitoring, and support tools.

**Object operations, conceptually:**

- **Write/put:** create an object at a key, or replace it according to the system's versioning and overwrite semantics.
- **Read/get:** retrieve the object payload, sometimes with supported range reads.
- **Inspect/head:** retrieve metadata without necessarily downloading the payload.
- **List:** discover keys under a prefix; listing guarantees and cost vary by service.
- **Delete:** remove or mark an object according to the storage system's versioning, retention, and deletion behavior.

Do not assume that a multi-object update is atomic. Do not assume an object key rename is a cheap atomic directory operation; it may be implemented as copy plus delete. Verify the actual storage contract before relying on it.

**Useful when:** Files are durable units of ingestion, analytics, backup, or exchange.

**Poor fit:** A design that needs frequent individual-row updates, foreign-key enforcement, or a transaction spanning many independent objects without an additional management layer.

**Check your understanding:** If a prefix is named `curated/customer/`, does that name by itself guarantee that only approved consumers can read the objects? Why not?

### 4.3 Organizing a data lake

A **data lake** is a logical collection of data stored in scalable storage, often including files in object storage. One common pattern separates data by processing state:

- **Raw/landing:** the source representation as received, with minimal transformation and enough metadata to trace the source.
- **Standardized:** validated, typed, normalized, and consistently named records.
- **Curated:** datasets shaped for known business or analytical use cases.

These are useful logical boundaries, not universal mandatory folder names. A domain-oriented layout, separate buckets/containers, or another convention may be more appropriate when access boundaries, lifecycle, or ownership differ.

A sound layout defines, for each area:

1. Owner and purpose.
2. Authoritative source and lineage.
3. Expected format and schema/version policy.
4. Allowed producer and consumer identities.
5. Encryption, audit, and data-classification requirements.
6. Retention and deletion behavior.
7. Lifecycle/tiering policy and restore expectations.
8. Quality checks and publication conditions.

#### Illustrative prefix layout and policy

The following is a fictional teaching example, not a universal prescription.

| Logical prefix | Purpose and format policy | Access rule | Lifecycle/deletion rule |
|---|---|---|---|
| `landing/card_transactions/` | Source payloads and ingestion metadata; text or source-native format where replay and inspection matter | Ingestion identity writes; a small restricted engineering group reads; general analysts have no direct access | Short, documented replay window; delete or expire only after downstream validation and any applicable hold check |
| `standardized/card_transactions/` | Validated records with explicit types and schema version; candidate typed record or columnar format | Pipeline identity writes; approved engineering and data-quality roles read | Retain according to operational recovery and audit need; track lineage to landing batch |
| `curated/card_transactions/` | Consumer-oriented analytical datasets; candidate columnar format when scans justify it | Consumer-specific read grants; no broad access by default | Retention owned by dataset owner and policy authority; deletion must cover derived copies and managed table metadata |
| `quarantine/card_transactions/` | Invalid or suspicious records, with reason codes separated from sensitive payload where possible | Restricted data-quality/security roles only | Short, explicit review window; no indefinite accumulation |
| `metadata/dataset-contracts/` | Dataset definitions, schema versions, owners, quality and lineage metadata | Maintainers write; consumers read | Version and retain contracts according to change/audit policy; avoid embedding secrets |

Use neutral identifiers in keys. Do not expose account numbers, customer names, email addresses, payment card numbers, or secret tokens in object names.

A prefix alone is not a security boundary unless the platform's authorization policies actually bind to it. If two areas require materially different access or lifecycle controls, separate namespaces or storage resources may make the policy easier to enforce; validate the actual policy behavior.

**Check your understanding:** Why might quarantine data require stricter access than curated analytics, even if both contain the same broad dataset?

### 4.4 File-format families

A format determines how records and fields are represented in bytes. Choose based on producers, consumers, schema needs, and query shape—not popularity.

| Format family | Illustrative examples | Conceptual organization | Strengths | Limitations / poor fit |
|---|---|---|---|---|
| Row-oriented text | CSV, JSON Lines (JSONL/NDJSON) | Records are represented as text, often one record per line for JSON Lines | Human-inspectable; broad interoperability; useful for exchange, debugging, and landing | Parsing cost; type ambiguity; repeated field names/delimiters; null and escaping rules can be ambiguous; often inefficient for repeatedly scanning a few columns |
| Row-oriented binary/record | Schema-aware binary record formats; Avro is an illustrative example | Records are encoded as binary fields, often with an explicit or external schema | Compact record-oriented encoding; useful for event exchange and schema-aware ingestion | Consumers need compatible readers and schema handling; column-only analytical scans may read/decode more fields than necessary |
| Columnar analytical binary | Parquet is an illustrative example | Values are organized by column within row groups or comparable units, with metadata that can support selective reads | Can support column pruning, predicate pruning, compression, and efficient analytical scans | Not human-readable; writer/reader compatibility matters; small files and poor layout reduce efficiency; not ideal as a simple hand-edited interchange file |

No format guarantees a specific performance result. Encoding, compression codec, file size, schema, reader implementation, query engine, network, and data distribution all matter.

**Check your understanding:** If consumers repeatedly read 4 fields from a dataset with 80 fields, why might a columnar format be worth evaluating?

## 5. Intermediate-level learning sequence

### 5.1 Compare formats against the workload

Start with evidence about the work:

- **Write pattern:** one-time bulk loads, periodic batches, continuous small writes, or frequent replacement?
- **Read pattern:** whole-record reads, selective field reads, range scans, filters, joins, or full export?
- **Schema variability:** stable typed schema, evolving nested fields, or loosely structured payloads?
- **Volume and file count:** bytes per day, retention horizon, number of objects, and expected growth.
- **Consumers:** how many tools or engines must read the data, and which format features do they support?
- **Governance:** sensitivity, access-control boundaries, audit, retention, deletion, residency, and legal holds.
- **Lifecycle:** how long is data hot, warm, cold, or eligible for deletion, and what does retrieval cost?
- **Operations:** who owns compaction, schema compatibility, monitoring, and incident response?

#### Selection comparison matrix

| Workload property | Text (CSV/JSON Lines) | Row-oriented binary/record | Columnar analytical |
|---|---|---|---|
| Human inspection | Often good, subject to size and escaping | Usually poor without a reader | Usually poor without a reader |
| Schema/type fidelity | Requires conventions; CSV especially can be ambiguous | Often explicit or schema-associated | Typed columns and schema metadata, with compatibility dependent on format and tools |
| Nested values | Possible but conventions vary; JSON represents nesting naturally | Depends on format/schema | Supported by many columnar formats, but nested semantics and interoperability must be checked |
| Streaming/event exchange | Often easy to emit and inspect | Often suitable when schema-aware encoding is needed | Usually more natural for analytical files/batches than individual event messages |
| Scan a few columns from many rows | Often requires parsing broad records | May decode records more broadly | Often supports column pruning |
| Predicate pruning | Limited unless external metadata/indexing helps | Depends on format and reader | May use statistics and row-group metadata; effectiveness depends on writer, query, and data distribution |
| Interoperability | Broad but semantic ambiguity is a risk | Requires reader/schema compatibility | Strong only where required engines support the relevant features and types |
| Compression | Text can compress well but repeats syntax | Binary encoding and compression may reduce size | Column similarity can help compression; actual ratio must be measured |
| Schema evolution | Contract and parsing rules must be managed | Schema evolution rules vary by format | Schema evolution support and compatibility vary; test additions, removals, renames, and type changes |
| Typical poor fit | Repeated large analytical scans where parsing and selective reads dominate | Human-edited exports or workloads needing efficient column-only scans | Small manual exchanges or consumers lacking compatible readers |

### 5.2 Schema representation and evolution

A **schema** defines fields, names, types, nullability, nesting, and sometimes semantic constraints. **Schema evolution** is a controlled change to that definition over time.

Important distinctions:

- **Type fidelity:** a typed integer is not the same as the string `"123"`. Text consumers may infer types differently, especially for identifiers with leading zeros, decimals, timestamps, or empty fields.
- **Null versus missing versus empty:** `null`, a missing JSON property, an empty string, and a CSV empty field may not mean the same thing. Define semantics explicitly.
- **Nested data:** JSON naturally expresses nested objects and arrays. Binary and columnar formats may also support nesting, but consumers must agree on representation and supported types.
- **Backward compatibility:** can an old reader process new data? For example, adding an optional field may be compatible in some systems, while changing a field's type or meaning may not be.
- **Forward compatibility:** can a newer reader process older data? Defaults, optional fields, and schema resolution rules matter.
- **Rename and deletion:** renaming a field may be interpreted as removing one field and adding another unless field identity is tracked by the format or schema system.
- **Semantic compatibility:** even if a parser succeeds, changing currency units, timestamp meaning, or identifier semantics can break consumers.

Do not rely on a format name alone to guarantee compatibility. Maintain versioned dataset contracts, test representative old and new readers, and document allowed changes.

**Example:** A CSV field `customer_id` contains `000731`. If a consumer infers it as a number, the leading zeros may be lost. If it is an identifier, specify a string type in the contract and validate the consumer behavior.

**Validation approach:** test an old producer/new reader and new producer/old reader where those combinations are expected to coexist. Include nulls, missing fields, nested values, precision-sensitive decimals, timestamps/time zones, and invalid records.

**Check your understanding:** Why can a schema-compatible field addition still cause a downstream failure?

### 5.3 Compression, column pruning, and predicate pruning

**Compression** reduces bytes stored or transferred by encoding repeated or predictable data more compactly. A **compression ratio** in this lesson means `raw size / compressed size`; a ratio of 4 means the compressed payload is one quarter of raw size.

**Column pruning** means a reader avoids reading columns not required by a query, where the format and reader support it. **Predicate pruning** means metadata can help skip row groups or data regions that cannot satisfy a filter.

These capabilities are conditional. For example, columnar files may store statistics for row groups, but if a predicate is not selective or the values are poorly clustered, little data may be skipped. A format does not automatically solve partition design or query planning.

Compression trade-offs include:

- Lower stored bytes and potentially lower transfer volume.
- CPU cost to compress and decompress.
- Different compression ratios across data types and cardinality.
- Possible effects on parallelism and read granularity.
- Compatibility constraints among writers and readers.

Use measurements on representative data. Do not assume a universal compression ratio or scan throughput.

**Check your understanding:** If compression cuts bytes by 70% but doubles the CPU time for decompression, is it automatically better? What else must be measured?

### 5.4 The small-file problem, file size, and compaction

A **small-file problem** occurs when a dataset is split into many tiny objects. Each file may require listing, metadata processing, opening, scheduling, and format initialization. The overhead can dominate useful work, and large numbers of objects make operations such as discovery and compaction more complex.

At the other extreme, a few very large files can limit parallelism, make retries expensive, or force readers to process more data than needed. There is no universal target file size. The appropriate size depends on query engine behavior, object-store request costs, partitioning, compression, concurrency, memory, and the workload.

**Compaction** combines many smaller files into fewer larger files, preserving the intended logical records and schema. It needs a safe publication strategy so readers do not observe a partial output or accidentally read both old and new copies. Raw landing may intentionally preserve source batches for replay, while standardized or curated areas may be compacted for analytics.

A partition is a logical slice of data, often by date, tenant, region, or another filterable attribute. A **target file size** is a planning assumption for each output file, not a guarantee. A **partition size** is the total data volume assigned to a logical partition.

A useful planning formula is:

```text
files_per_partition = partition_size / target_file_size
```

The result may be fractional in arithmetic, but actual file counts are integers. If the result is not an integer, round up for a simple capacity estimate. For a simple capacity estimate, use `ceil(partition_size / target_file_size)` when estimating how many files are needed to hold a partition; do not interpret that as a command to pad data or as a prediction of actual writer output. Actual output may vary because of compression, uneven partitions, writer behavior, parallel tasks, and minimum/maximum constraints.

**When compaction helps:** repeated analytical scans suffer from too many tiny files and the data can be safely rewritten.

**When it may not help:** the dataset is small, rarely queried, or the compaction cost exceeds the query and metadata savings; or the raw record-preservation policy forbids rewriting the landing objects.

**Check your understanding:** Why is “make every file as large as possible” not a safe universal rule?

### 5.5 Quantitative worksheet: raw size, compressed size, file count, and scan time

All values below are **illustrative assumptions**, not benchmarks or recommendations.

#### A. Raw and compressed size

Formula:

```text
raw_size = record_count × average_uncompressed_record_size
compressed_size = raw_size / compression_ratio
```

Assumptions:

- Records per day: `12,000,000 records/day`
- Average uncompressed record size: `800 bytes/record`
- Assumed compression ratio: `4:1` (raw bytes divided by compressed bytes)

Calculation:

```text
raw_size
= 12,000,000 records/day × 800 bytes/record
= 9,600,000,000 bytes/day
= 9.6 GB/day (decimal; 1 GB = 10^9 bytes)

compressed_size
= 9,600,000,000 bytes/day ÷ 4
= 2,400,000,000 bytes/day
= 2.4 GB/day
```

Interpretation: under the assumed ratio, the stored payload is 25% of raw size, a reduction of 7.2 GB/day. This estimate excludes metadata, indexes, manifests, replication/copies, and other overhead unless explicitly added. The ratio must be measured on representative data.

#### B. File count by partition

Assumptions:

- One day's compressed data: `2.4 GB/day`
- Data is evenly distributed across `24 hourly partitions`.
- Illustrative target file size: `128 MB/file` (decimal MB = 10^6 bytes).

Formula:

```text
partition_size = daily_compressed_size / partitions_per_day
files_per_partition = partition_size / target_file_size
```

Calculation:

```text
partition_size
= 2,400 MB/day ÷ 24 partitions/day
= 100 MB/partition

files_per_partition
= 100 MB/partition ÷ 128 MB/file
= 0.78125 file/partition
```

A fractional result means one file per partition would be sufficient in a simple planning model; the target size is not a command to pad each partition to 128 MB. The daily estimate is 24 files/day if one output file is produced per hourly partition. Actual writers may create multiple files because of parallel tasks, skew, or commit behavior. If the data instead arrived as 1-minute micro-batches, the raw landing layer could have up to 1,440 small objects/day before compaction, assuming one object per batch. This is a separate illustrative write pattern, not an assertion that every pipeline creates exactly one file per minute.

#### C. Approximate scan time

Formula:

```text
scan_time ≈ bytes_scanned / effective_scan_throughput
```

Illustrative assumptions for a planning exercise:

- Bytes scanned: `2.4 GB = 2,400,000,000 bytes`
- Effective aggregate scan throughput: `300 MB/s = 300,000,000 bytes/s`

Calculation:

```text
scan_time ≈ 2,400,000,000 bytes ÷ 300,000,000 bytes/s
          ≈ 8 seconds
```

This is only a byte-throughput lower-level estimate, not a performance promise. Actual elapsed time can be higher or lower due to parallelism, metadata, request latency, network, decompression, encoding, filtering, partition pruning, cache state, compute scheduling, and concurrent workloads. If a query scans only selected columns or prunes most partitions, `bytes_scanned` may be far below total dataset size; if it must parse text or scan everything, it may be closer to the full payload.

#### D. Worksheet template

Fill in measured or explicitly assumed values.

| Input/output | Value | Unit | Evidence or assumption |
|---|---:|---|---|
| Record count | Unknown | records/day | Producer metrics or estimate |
| Average raw record size | Unknown | bytes/record | Sample measurement |
| Raw volume | Calculate | bytes/day | Count × size |
| Compression ratio | Unknown | ratio | Measure on representative sample |
| Compressed volume | Calculate | bytes/day | Raw volume ÷ ratio |
| Partition count | Unknown | partitions/day | Chosen from access patterns |
| Target file size | Unknown | bytes/file | Workload-dependent design assumption |
| Estimated files | Calculate | files/partition and files/day | Partition size ÷ target size, rounded up for planning |
| Bytes scanned per query | Unknown | bytes/query | Query plan or sample measurement |
| Effective scan throughput | Unknown | bytes/s | Measured under representative load |
| Approximate scan time | Calculate | seconds/query | Bytes scanned ÷ throughput |

**Check your understanding:** Which inputs in this worksheet should be measured before a production commitment, and which are architecture choices?

## 6. Advanced-level learning sequence

### 6.1 Interoperability and downstream tooling

Interoperability means different producers, readers, and processing engines can exchange data without silently changing its meaning. Test more than whether a reader can open a file.

Validate:

- Primitive types and precision, including decimal scale.
- Null, missing, empty, and default-value semantics.
- Nested arrays/objects and field naming.
- Timestamp precision, timezone conventions, and date handling.
- Compression codec and encoding support.
- Schema evolution and field identity.
- Predicate/column pruning behavior where relevant.
- Error behavior for malformed or unexpected data.
- Compatibility across the versions of the actual consumer tools.

A text format may be preferable for an external exchange contract because it is inspectable and widely supported. A typed binary format may be preferable for schema-aware event records. A columnar format may be preferable for repeated analytical scans. The correct answer depends on the actual consumer set and test results.

### 6.2 Logical prefix design, access control, and lifecycle

A prefix layout should reflect operational boundaries, not only visual neatness. For every prefix, define an owner, writer identities, reader identities, retention source, deletion process, audit requirements, and recovery expectations.

Do not assume that a prefix name enforces access. Test authorization with both permitted and denied identities. Use least privilege: a pipeline that writes landing data may not need to read curated data, and an analyst who reads curated data may not need raw payload access.

Lifecycle rules may transition data to a lower-cost tier or expire it after a policy-defined period. The storage price is not the whole cost: retrieval charges, restore delays, request costs, minimum storage durations, and operational handling can change the result. The actual pricing and policy constraints must be verified for the chosen platform; this lesson does not assign universal values.

**Deletion obligations:** A deletion request may affect objects, copies, derived datasets, snapshots, metadata, indexes, caches, and backups. If data are embedded in immutable files, deletion may require rewriting affected files, applying a supported deletion/erasure mechanism, or isolating and expiring the entire containing object when policy permits. The design must reconcile privacy obligations with legally required retention and holds; the applicable authority must confirm the actual rules. Do not promise deletion that the architecture cannot verify.

### 6.3 Immutability and safe publication

Object storage is often used with immutable or append-oriented data, but immutability is an architectural policy and sometimes a storage feature—not a universal guarantee. Versioning, retention locks, overwrites, and deletion semantics differ by service and configuration.

A safe batch publication process typically separates:

1. Write new objects to a temporary or run-specific prefix.
2. Validate record counts, schema, checksums/control totals, and quality rules.
3. Publish a manifest, table metadata update, or other agreed completion marker.
4. Make consumers read only published outputs.
5. Retire old outputs according to the retention and rollback policy.

This is conceptual pseudocode, not a service-specific implementation:

```text
write(run_prefix, output_objects)
validate(run_prefix)
if validation_passes:
    publish_completion_marker(run_prefix, manifest)
else:
    quarantine(run_prefix)
    alert_owner()
```

Inputs: a unique run prefix, expected schema and quality checks, and a publication mechanism. Output: either a validated published run or a quarantined failed run. Limitation: a completion marker alone does not make a multi-object update transactional; consumers and recovery logic must obey the publication contract, and the chosen platform's consistency semantics must be verified.

### 6.4 Industry case: Northbridge Bank (fictional and illustrative)

Assume, purely for teaching, that fictional Northbridge Bank receives card-transaction events continuously, retains source payloads for replay, and serves analytical reporting over historical transactions.

Potential design:

- **Landing:** preserve source payloads and ingestion metadata in a replayable form. Text such as JSON Lines may help inspect events, but typed source formats may be better if the producer contract and consumer tooling support them.
- **Standardized:** validate required fields, types, timestamps, and duplicate/event identifiers; produce a typed representation with a versioned schema.
- **Curated:** choose a columnar format if measurements show that analytical consumers scan subsets of fields across many transactions.
- **Compaction:** combine small standardized/curated outputs on a schedule or threshold derived from observed object count, query behavior, and freshness requirements. Keep raw objects when source replay/audit policy requires them.
- **Governance:** restrict raw and quarantine payloads; publish curated fields only to authorized groups; define retention and deletion across all copies and derived outputs.
- **Validation:** measure bytes written, compressed size, objects per partition, listing/metadata time, query bytes scanned, elapsed query time, schema-compatibility failures, and deletion completion.

This is not a claim about any real bank, legal requirement, workload volume, or benchmark.

### 6.5 Select using evidence and reject alternatives explicitly

Use this repeatable process:

1. **State requirements:** purpose, owner, consumers, retention, security classification, and freshness.
2. **Characterize the workload:** records/bytes per time unit, write frequency, query shapes, columns selected, filters, scan horizon, and concurrency.
3. **Shortlist formats:** choose two or three plausible candidates and a baseline.
4. **Compare:** type fidelity, schema evolution, interoperability, compression, scan/pruning behavior, file count, and lifecycle implications.
5. **Quantify:** calculate raw and compressed bytes, expected file count, and scan-time estimates with units.
6. **Test:** use representative data and consumer tools; record actual file sizes, compatibility, object count, bytes scanned, elapsed time, and failure behavior.
7. **Decide:** choose the simplest option meeting the evidence-backed requirements.
8. **Record a rejected alternative:** give a specific mismatch, not “it is too complex.”
9. **Define revisit triggers:** for example, measured object count exceeds the compaction threshold, new consumers cannot read the format, schema changes become incompatible, or query cost/latency misses the agreed target.
10. **Assign ownership:** name who operates schema changes, compaction, retention, and deletion verification.

#### Format decision matrix template

| Criterion | Evidence to collect | Candidate A | Candidate B | Candidate C |
|---|---|---|---|---|
| Producer/write pattern | Batch size, frequency, update/append behavior | Unknown | Unknown | Unknown |
| Consumer/read pattern | Whole records, selected columns, filters, scan horizon | Unknown | Unknown | Unknown |
| Schema/type needs | Nulls, nesting, decimal/timestamp precision, change frequency | Unknown | Unknown | Unknown |
| Interoperability | Required engines and versions; test results | Unknown | Unknown | Unknown |
| Compression and size | Raw sample size, compressed sample size, ratio | Unknown | Unknown | Unknown |
| File count and layout | Partition size, object count, listing/metadata overhead | Unknown | Unknown | Unknown |
| Governance/lifecycle | Access rules, retention, deletion, audit, retrieval | Unknown | Unknown | Unknown |
| Operating cost | Compute, storage, requests, people, incidents | Unknown | Unknown | Unknown |
| Decision/rejected alternative | Evidence-based fit and specific mismatch | Unknown | Unknown | Unknown |

“Unknown” is a prompt to measure or document an assumption, not a zero value.

## 7. Industry-application exercises

### Exercise A — Six datasets

For each dataset, select a storage type and candidate format, state the workload evidence, and reject one alternative.

1. A source-system export that must be inspected during ingestion failures.
2. A schema-aware stream of nested business events.
3. A multi-year analytical table where most queries read a few columns across many rows.
4. A set of small daily configuration documents read as whole records.
5. A dataset consumed by several engines whose nested-type support is not yet verified.
6. An archive that is rarely queried but has strict retrieval and deletion obligations.

**Answer guidance:**

1. Object storage is a plausible storage type; text may aid inspection, but choose based on source semantics and replay requirements. Reject a columnar-only landing format if it makes operational inspection and source fidelity impractical for the team.
2. Object storage may hold batches, while a schema-aware row-oriented binary/record format may fit the event contract. Reject plain CSV if nested types and type fidelity are essential and conventions are not reliably enforced.
3. Object storage plus a columnar format is a strong candidate if representative tests show pruning and scan benefits. Reject repeatedly parsing text if measurements show excess scan/parse cost.
4. A general-purpose database or object storage may both work depending on update/query needs. Do not introduce a lakehouse-style layout automatically for a small dataset; reject the more complex option if no measured requirement justifies it.
5. Run compatibility tests first. Prefer the format all required engines can read with correct semantics; reject a format feature that one required engine silently misinterprets.
6. Object storage can fit, but tier, format readability, retention, and deletion design must be tested. Reject a tier/format combination if restore time, retrieval cost, or deletion limitations conflict with confirmed requirements.

These are reasoned examples; another answer can be correct if it cites different evidence and trade-offs.

### Exercise B — Streaming source, tiny files

**Illustrative assumptions:** a producer emits one file every minute, 24 hours/day, for 30 days.

Formula:

```text
objects_per_day = files_per_minute × minutes_per_hour × hours_per_day
objects_per_30_days = objects_per_day × 30 days
```

Calculation:

```text
objects_per_day = 1 file/min × 60 min/hour × 24 hour/day
                = 1,440 files/day

objects_per_30_days = 1,440 files/day × 30 days
                    = 43,200 files/30 days
```

**Partition-multiplier example (illustrative):** if each minute's write produces one file in each of 10 partitions, then:

```text
files_per_day = 1,440 writes/day × 10 partitions_written_per_write
              = 14,400 files/day
```

Assume those files together contain `10 GB/day` of uncompressed data (decimal units, `1 GB = 1,000 MB`). If the volume is evenly distributed across those 14,400 files, the mean is:

```text
average_file_size = 10,000 MB/day ÷ 14,400 files/day
                  ≈ 0.6944 MB/file
                  ≈ 0.7 MB/file
```

This average is a planning illustration, not a guarantee: skew, compression, parallel writers, and variable record sizes change actual file sizes. It demonstrates why write frequency multiplied by the number of partitions written per batch matters. It does not establish a universal target file size.

Design a landing format, a compaction schedule/trigger, and a curated format. State what must be validated before source files can be retired. A good answer may keep small source batches in landing for replay, compact standardized outputs to reduce metadata overhead, and use a columnar curated format if analytical access patterns justify it. It should not claim that a fixed target file size is universally correct.

### Exercise C — Analysts scan a 40 TB CSV archive for three columns

Questions:

- What evidence would you gather about bytes scanned, query frequency, latency/cost, and filters?
- Would a columnar representation reduce the data read for these queries? Under what conditions?
- What conversion compute, temporary storage, validation, and dual-format retention costs would be incurred?
- How would you compare a one-time conversion with repeated scan savings?
- What schema, null, timestamp, decimal, and encoding semantics must remain unchanged?

**Answer guidance:** A columnar conversion is a candidate, not an automatic win. Estimate how often the archive is scanned, how much of the 40 TB is actually read, and the conversion/validation cost. Test representative queries and reconcile row counts and key aggregates. Preserve or document semantic differences before switching consumers.

### Exercise D — Deletion from immutable files

A fictional customer requests deletion of their data from files containing many customers.

List the affected objects and derived copies; identify whether records can be removed individually through a managed table/deletion layer or whether files must be rewritten; check legal holds and retention policy with the appropriate owner; define verification across landing, standardized, curated, snapshots, indexes, and backups; and document what cannot be immediately removed and why. Do not assert a legal outcome without confirmed requirements.

### Exercise E — Two engines, different format support

List the required engines and versions, the schema features used, and the behavior each engine must preserve. Test reading the same representative data, including nulls, decimals, nested arrays, timestamps, and schema changes. Choose a common supported feature subset or an explicit conversion boundary if needed. Reject a format based only on a single successful “file opened” test.

## 8. Practical scenarios and case-based reasoning

### Scenario 1: The first tool chooses the format

A team selects CSV because the ingestion tool emits it easily. Later, analysts repeatedly scan a large history for a small set of fields.

**Reasoning:** The producer's convenience is only one criterion. Measure query frequency, bytes scanned, parse cost, schema ambiguity, and downstream conversion cost. Compare retaining CSV, producing a typed record format, and creating a columnar analytical copy. Keep CSV if exchange/inspection value outweighs the measured analytical penalty; otherwise introduce a justified conversion stage.

### Scenario 2: One file per record

A pipeline writes one object per event. Object count and listing time rise.

**Reasoning:** Quantify objects per hour/day and the consumer's file-open/metadata overhead. Consider buffering or compaction at a boundary consistent with freshness and replay needs. Do not compact away the only source copy if audit or replay policy requires preservation.

### Scenario 3: A schema change silently breaks consumers

A producer changes a decimal amount to a string, or renames a field without coordinating readers.

**Reasoning:** Define the schema contract and compatibility policy. Test old/new producer-reader combinations. Preserve semantic types, publish a new version when needed, and monitor schema validation failures. A file that parses is not necessarily semantically compatible.

### Scenario 4: Lifecycle rules conflict with investigation needs

A team moves old objects to an archival tier, then discovers that restoring them is slow or costly.

**Reasoning:** Estimate storage, retrieval, request, and operational costs; identify restore-time requirements; assign retention ownership; and test retrieval before adopting the lifecycle rule. Storage price alone is not total cost.

### Scenario 5: A deletion request cannot be completed

A customer record exists in multiple immutable files and downstream copies.

**Reasoning:** Trace lineage and copies, establish retention/hold constraints, select a supported deletion or rewrite method, and verify completion. Design for deletion before ingestion; do not rely on a manual search across unknown prefixes.

## 9. Expected outputs and deliverables

Complete and retain these outputs for review:

1. **Storage-type comparison:** block, file, and object storage, including access and update semantics.
2. **Format comparison table:** text, row-oriented binary/record, and columnar formats, with workload evidence for each choice.
3. **File-count and size worksheet:** raw size, compressed size, partition size, estimated file count, bytes scanned, and approximate scan time. Include formulas, units, assumptions, and a reproducible calculation.
4. **Logical prefix layout:** purpose, owner, format/schema policy, producer/consumer access, lifecycle, retention, deletion, and audit rules for every prefix.
5. **Northbridge Bank design note:** explicitly fictional, with a justified landing-to-curated strategy.
6. **Validation plan:** representative data, required readers, schema evolution tests, size/scan measurements, and governance checks.
7. **Practice answers:** completed and corrected exercises.

Do not fill unknowns with invented production requirements. Mark them **Unknown**, then propose how to obtain the evidence.

## 10. Common mistakes and misconceptions

- **Treating object storage as a file system with row updates.** Objects are usually handled as whole payloads; row-level semantics need an appropriate database or management layer.
- **Choosing a format because it is fashionable.** Popularity does not prove fit for the actual producer, readers, schema, or cost profile.
- **Writing tiny files indefinitely.** Object count and per-file metadata work can dominate useful processing.
- **Ignoring listing and metadata overhead.** File count is an operational and query-planning variable, not just a cosmetic detail.
- **Assuming columnar always wins.** It can help analytical scans, but may be a poor fit for small exchanges, record-at-a-time consumption, or unsupported readers.
- **Assuming text has no schema.** Text still has semantics; if they are undocumented, they are merely implicit and fragile.
- **Assuming compression ratios are fixed.** Data characteristics and codecs change results; measure representative samples.
- **Assuming a prefix enforces access.** Actual authorization policies must be configured and tested.
- **Designing prefixes without lifecycle and ownership rules.** Data can become inaccessible, over-retained, or expensive to retrieve.
- **Forgetting deletion obligations.** Copies, derived datasets, snapshots, and backups may outlive the primary object.
- **Treating immutability as an excuse not to design deletion.** Retention and erasure requirements must be addressed before the format and layout are finalized.
- **Confusing a file format with a table format or data platform.** Topic 4 covers table-management features; plain files alone do not supply all table semantics.

## 11. Mastery criteria

You are ready to proceed when you can:

- Explain block, file, and object storage without confusing their access/update semantics.
- Choose a format by listing producer and consumer access patterns, schema needs, and interoperability evidence.
- Explain how nulls, types, nesting, schema evolution, compression, and pruning affect consumers.
- Reproduce the raw/compressed size, file-count, and scan-time calculations with correct units.
- Explain why file count and target size are workload-dependent and define a compaction trigger.
- Design prefixes with named owners, least-privilege access, retention, lifecycle, and deletion rules.
- Compare at least two viable options and reject one with a specific evidence-based reason.
- State what remains unknown, how it will be measured, and what would cause the decision to be revisited.

## 12. Completion gate

Do not mark Topic 3 complete until every item is checked. This file follows the roadmap’s twelve-section Topic 3 structure:

- [ ] Storage-type comparison correctly distinguishes block, file, and object storage.
- [ ] Format comparison cites workload properties for each selected and rejected format.
- [ ] Worksheet shows formulas, units, assumptions, and independently reproducible arithmetic for raw size, compressed size, file count, and scan-time estimate.
- [ ] Prefix layout lists purpose, owner, access-control rules, lifecycle/retention, and deletion obligations for each logical area.
- [ ] Schema evolution and interoperability tests cover relevant types, nulls, nested fields, and consumer compatibility.
- [ ] Small-file/compaction strategy includes write-frequency × partitions-per-write arithmetic, an evidence-based trigger, and trade-offs.
- [ ] Northbridge Bank case is clearly labeled fictional and illustrative.
- [ ] Topic 3 practice questions and exercises are answered and corrected.
- [ ] No unsupported benchmark, universal target size, or guaranteed compression/performance claim remains.

**Final self-check:** Could another engineer reproduce your arithmetic, understand why the format fits the access pattern, verify the access/lifecycle policy for each prefix, and identify the evidence that would make you change the design? If not, the decision package is not yet complete.
