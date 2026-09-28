# The Small-Files Problem and Target File Sizing

## Learning Objectives

By the end of this module, you should be able to:

- explain the small-files problem in simple terms;
- explain why "small" is contextual rather than a universal byte threshold;
- explain file-open, footer/metadata, listing, object-request, compression, and distributed-task overhead;
- identify small-file causes such as micro-batches, streaming writes, over-partitioning, parallel writers, and tiny deltas;
- reason about the practical analytical Parquet starting range of approximately 128 MB–1 GB without treating it as a law;
- explain the trade-off between file size and useful parallelism;
- recognize oversized files as a different failure mode;
- prevent small files at write time using row limits, writer coordination, and batching;
- build a file-health report with file counts, total bytes, distributions, and percentiles;
- identify unhealthy partitions with configurable thresholds;
- compact a partition with `pyarrow.dataset` into fewer, better-sized files;
- optionally sort data during compaction when the layout benefit justifies the extra work;
- publish compacted output through a temporary location and validate it before cleanup;
- reason about crash safety, idempotency, concurrent readers, and concurrent writers;
- explain why plain directory datasets do not provide table-level transaction isolation;
- monitor file health and schedule compaction based on workload value and cost;
- benchmark before and after compaction without fabricating results;
- defend target-file-sizing and compaction decisions in architecture reviews and interviews.

The central skill is not memorizing a number. It is making a **measured file-layout decision** for a real workload.

---

## Prerequisites

This topic assumes you have already completed:

1. Topic 01 — Row-Oriented vs Columnar Storage
2. Topic 02 — Parquet Internals: Row Groups, Pages, and Statistics
3. Topic 03 — Reading and Writing Parquet with PyArrow
4. Topic 04 — Avro Files and Row-Oriented Formats
5. Topic 05 — ORC and Format Selection Trade-offs
6. Topic 06 — Nested / Semi-Structured Data: Flatten and Explode
7. Topic 07 — Compression Codecs: Snappy, gzip, Zstandard, LZ4
8. Topic 08 — Partitioning and Hive-Style Directory Layouts

You should already understand Parquet, row groups, compression, partitioning, Hive-style paths, object-storage basics, PyArrow dataset writing, and DuckDB querying.

Do not re-learn those topics here. We will use only the pieces needed to reason about file count, file size, and compaction.

---

# The Core Mental Model

> **A data lake has both a data-volume problem and a file-count problem.**

Two datasets can contain the same logical bytes and still have very different operational costs:

```text
Large Dataset
     │
     ├── Few healthy-sized files
     │       ↓
     │   Lower metadata/request overhead
     │   Fewer file-management operations
     │
     └── Thousands / millions of tiny files
             ↓
        More opens and reads
        More metadata work
        More listings
        More objects and requests
        More scheduling/task overhead
        Potentially worse compression
        More operational complexity
```

There is also an opposite failure mode:

```text
Too Small
    ↓
Too Many Files
    ↓
Metadata / Listing / Request / Task Overhead

Too Large
    ↓
Too Few / Huge Files
    ↓
Poorer Parallelism / Heavy Rewrites / More Writer Memory

Target Range
    ↓
Enough Files for Useful Parallelism
    +
Healthy File Sizes
    +
Manageable Metadata
    +
Efficient Queries
```

There is **no universal perfect file size**. A target is a workload-and-environment parameter that should be proposed, measured, and revisited.

---

# The File-Layout Learning Loop

Use the roadmap's measure-first loop throughout this topic:

```text
Read
  ↓
Predict size & bytes read
  ↓
Write the file
  ↓
Inspect metadata / layout
  ↓
Query
  ↓
Measure size, time, bytes, requests where observable
  ↓
Change one knob
  ↓
Measure again
  ↓
Write down the result
  ↓
Explain the result aloud
```

The discipline matters. A compaction project without before/after measurements is just a rewrite project with an assumption attached.

---

# 1. Why File Count Matters

## What is it?

File count is the number of physical objects the analytical engine must discover, consider, open, or scan to answer queries against a dataset.

For a partitioned Parquet dataset, imagine:

```text
orders/
├── year=2026/month=09/day=27/
│   ├── part-00001.parquet
│   ├── part-00002.parquet
│   └── ...
└── year=2026/month=09/day=28/
    ├── part-00001.parquet
    ├── part-00002.parquet
    └── ...
```

The partition layout decides **which directories are candidates**. File sizing decides **how many physical files exist inside those candidates**.

## Why does it exist?

A lake needs files because storage systems, filesystems, and object stores work with physical objects. Query engines therefore operate over file fragments rather than a single magical infinite table.

## What physically happens?

For a query, an engine may need to:

1. discover candidate paths;
2. inspect file metadata;
3. inspect Parquet metadata/statistics where useful;
4. schedule work to read data fragments;
5. decode selected columns and row groups;
6. combine results.

The exact sequence and parallelism depend on the engine. Do not reduce the process to "one file equals one task" or "every engine performs exactly the same metadata requests."

## Simple example

```text
Dataset = 100 GB

Design A:
100 files × 1 GB

Design B:
10,000 files × ~10 MB
```

Both contain approximately the same logical data.

Ask yourself:

> Which design creates more per-file overhead?

Design B potentially creates much more work around file discovery, metadata, opens, requests, and scheduling, even before considering the actual bytes of payload data.

```text
Same logical bytes
       ≠
Same operational cost
```

Do not claim a fixed runtime difference from this example. The measured difference depends on engine, storage, caching, query, and hardware.

## Production example

A streaming order pipeline writes one file every minute into `year/month/day`. After 30 days, the partition tree can contain tens of thousands of objects. A later analytical query that touches the recent days may be logically simple but operationally expensive because the engine has to deal with a large number of physical fragments.

## Measure

Track at least:

- total file count;
- files per partition;
- total bytes;
- average, median, p95, and p99 file size;
- bytes scanned by a representative query;
- query latency;
- object-store request behavior when instrumentation is available.

## Trade-off

Fewer files are not automatically better. You need enough files to expose useful parallelism and avoid excessively large rewrite units.

## Common mistake

> "We have a lot of data, so a lot of files must be good."

The important question is not whether the dataset is large. It is whether the **physical fragmentation matches the workload and execution environment**.

## Production implication

File count is a first-class layout metric. It belongs in architecture discussions, not only in cleanup scripts.

---

# 2. What Is a Small File?

## What is it?

A file is **small** when the overhead associated with managing and reading that file is large relative to the amount of useful data the file contains, given the workload and infrastructure.

That makes "small" contextual.

A file that is perfectly acceptable for a tiny local dataset may be an unhealthy unit in a billion-row analytical lake.

## Factors that change the meaning of "small"

| Factor | Why it matters |
| --- | --- |
| Dataset size | File count compounds as datasets grow |
| File count | Determines fragmentation and metadata surface area |
| Average file size | Useful baseline, but not enough by itself |
| Size distribution | Reveals tails hidden by averages |
| Query workload | Frequent narrow reads have different needs from full scans |
| Engine | Planning and task models differ |
| Storage system | Local filesystem, HDFS, object store, and gateways behave differently |
| Format | Parquet, ORC, Avro, and text formats have different metadata behavior |
| Metadata behavior | Some engines cache or centralize metadata; others rediscover it |
| Parallelism | Smaller files can expose more concurrency, up to a point |
| Rewrite frequency | Frequently updated data needs manageable rewrite units |

## The roadmap's practical range

For analytical Parquet, this roadmap uses a practical starting range of approximately:

> **128 MB to 1 GB per file**

This range is a **baseline for experimentation**, not a universal requirement.

Do not use the following reasoning:

```text
< 128 MB = always bad
128 MB–1 GB = always good
> 1 GB = always bad
```

Use this instead:

```text
Candidate target range
      ↓
Benchmark on the workload
      ↓
Check parallelism, memory, metadata and rewrite behavior
      ↓
Adopt a documented range
```

## Production implication

Your standard should say something like "our initial target is X–Y under workload Z," not "the correct file size is X."

---

# 3. The Six Costs of Too Many Small Files

The major costs are:

1. file open/read overhead;
2. footer and metadata overhead;
3. directory/prefix listing overhead;
4. object-storage request overhead and charges, where applicable;
5. weaker compression efficiency in some datasets;
6. excessive distributed task/scheduling overhead.

These costs can overlap. A single physical file can incur several of them during one query.

---

# 4. File Open and Read Overhead

## Physical model

A file interaction can involve work such as:

```text
Open / establish access
        ↓
Obtain file metadata
        ↓
Read needed metadata/footer
        ↓
Read selected data
        ↓
Close / release resources
```

The exact sequence depends on the storage and reader implementation.

With 10,000 files, the engine may need to manage many more physical objects than with 100 files holding the same total bytes.

## Why this matters

Suppose a query really needs only 8 GB of data. It is not enough to say:

> "The engine reads 8 GB, so file layout does not matter."

The engine may also have to manage the metadata and coordination for every candidate file.

## Production example

A dashboard query repeatedly scans the last seven days. If each day contains thousands of tiny files, the query can spend a meaningful fraction of its work coordinating many fragments rather than processing payload bytes.

## Measure

On a local experiment, use system tracing or client instrumentation where available. On an object store, use storage logs/metrics or a controlled request counter where possible.

Avoid assuming a request count without evidence.

## Trade-off

Larger files reduce per-file overhead but can reduce the amount of independent work available to parallel readers.

## Common mistake

Confusing **bytes scanned** with **total work performed**.

---

# 5. Footer and Metadata Overhead

Parquet stores schema and file-level metadata in its footer. Topic 02 covered the physical details; here the important idea is repetition.

Conceptually:

```text
1 Parquet file
    ↓
1 file-level metadata surface

10,000 Parquet files
    ↓
10,000 file-level metadata surfaces
```

An engine may use some or all of those metadata surfaces to discover schemas, row groups, statistics, and candidate data. The exact behavior varies by engine and reader.

## Why many tiny files amplify metadata work

If a partition contains thousands of tiny Parquet files, each file carries some amount of structural metadata relative to its payload.

A useful mental model is:

```text
Useful payload per file
----------------------
Metadata + coordination cost per file
```

As the useful payload shrinks, the fixed-ish management work becomes more significant relative to the payload.

## Measure

For Parquet datasets, compare:

- file count;
- median file size;
- total file sizes;
- query planning time if your engine exposes it;
- query wall-clock time;
- bytes read.

Do not claim exact metadata request counts unless measured or documented for the engine.

---

# 6. Directory / Prefix Listing Overhead

Connect this section directly to Topic 08.

A dataset may have:

```text
Dataset
  ↓
Many partitions
  ↓
Many directories / prefixes
  ↓
Many files / objects
```

The discovery layer can therefore become an operational part of the query.

## Local filesystem vs object storage

A local filesystem has directory metadata and system calls. An object store exposes objects and prefix/listing operations rather than a POSIX directory in the same sense.

Do not assume their behavior is identical.

## Why listing matters

Large object collections can require more discovery work. The engine may need to know which objects exist before it can decide what to scan.

## Production implication

Partition design and file count interact:

```text
Over-partitioning
      +
Frequent writes
      ↓
More prefixes
      +
More files
      ↓
More discovery work
```

A well-designed partition scheme can still become unhealthy if the writer pattern generates too many objects inside each partition.

---

# 7. Object-Storage Request Costs

Object stores commonly expose request-oriented APIs such as `LIST`, `GET`, and metadata/head-style operations. Pricing and exact semantics vary by provider and product.

The important engineering point is:

> The number and pattern of object operations can change when file count changes, even when logical data volume does not.

For example:

```text
1,000 large objects
vs
100,000 tiny objects
```

may produce very different request patterns.

Do not hard-code cloud pricing into a generic design standard unless it is verified for the exact provider, region, storage class, and time period.

## Measure

Prefer:

- storage-client instrumentation;
- gateway or proxy access logs;
- server metrics;
- controlled request counters;
- a MinIO test environment for reproducible local experiments.

Provider/tool-specific metrics should be version-checked before use.

---

# 8. Poor Compression

Compression is not the only reason files should be sized carefully, but file fragmentation can influence compression behavior.

Tiny files may provide less repeated data and less opportunity for the compressor's local context or dictionary mechanisms to exploit repetition. The effect depends on the codec, encoding, data distribution, and file writer.

Conceptually:

```text
One logical dataset
       ↓
Fewer larger files
       ↓
More repeated values per physical file
       ↓
Potentially better compression context
```

versus:

```text
Same dataset
       ↓
Many tiny files
       ↓
Less context per file
       ↓
Potentially worse compression
```

Do not claim that every codec always compresses a fragmented dataset worse by a fixed amount.

For a fair experiment, keep the codec and compression level constant and change only the file layout.

---

# 9. Distributed Task Explosion

A distributed engine may turn file fragments or groups of fragments into units of work.

Conceptually:

```text
10,000 tiny files
      ↓
Many candidate fragments
      ↓
Many units of work
      ↓
Scheduler / coordination overhead
      ↓
Less useful work per task
```

This is why the small-files problem is often especially visible in distributed environments.

But do not simplify it to:

> one file = one task.

Engines can combine files, split files, use larger scan partitions, or apply engine-specific scheduling strategies.

## Production implication

The right question is:

> How does this engine turn my physical layout into execution work?

That is more useful than memorizing a universal file-to-task mapping.

---

# 10. Common Causes of Small Files

The roadmap calls out five recurring causes:

| Cause | What it looks like | Why it happens | Typical prevention |
| --- | --- | --- | --- |
| Frequent micro-batches | many files created close together in time | each trigger writes independently | batch records before writing |
| Streaming writes | continuous trickle of tiny outputs | low-latency ingestion | tune buffering/flush policy |
| Over-partitioning | many tiny partition directories | high-cardinality or overly fine keys | revisit partition scheme |
| Parallel writers | many files per partition per batch | workers write independently | coalesce or coordinate writes |
| Tiny incremental deltas | repeated small append files | daily/hourly changes are individually tiny | merge or compact deltas |

The same root cause can appear in different forms.

---

# 11. Micro-Batches and Streaming Writes

## The classic pattern

Imagine a streaming or micro-batch pipeline that writes one output file per minute:

```text
08:00 → file A
08:01 → file B
08:02 → file C
08:03 → file D
...
```

The data may arrive continuously, but analytical storage usually benefits from a different physical cadence.

## Why it happens

The writer is optimizing for **ingestion latency**, while the analytical reader is optimizing for **scan efficiency**.

Those are different objectives.

## Detection signals

Look for:

- timestamps clustered around job triggers;
- many files with nearly identical creation times;
- a large number of similarly tiny Parquet objects;
- file count growing almost linearly with ingestion triggers.

## Prevention options

### Buffer then batch

```text
Incoming records
      ↓
Short-lived buffer
      ↓
Larger batch
      ↓
Parquet writer
```

### Write small files, then compact

This is often reasonable when ingestion latency matters and the storage layer supports a safe compaction workflow.

### Use a storage system/table format with stronger write/commit semantics

Later modules cover table formats in more depth. The current topic only needs the awareness that transaction-aware table layers can make concurrent compaction much safer than raw directory manipulation.

## Trade-off

Longer buffering can improve file health but may increase data freshness latency. The correct buffer window is therefore a workload requirement, not a universal best practice.

---

# 12. Over-Partitioning

Topic 08 covered the partition-design mechanics. Here the concern is the interaction with file count.

Suppose you partition by `customer_id` and have millions of customers:

```text
orders/
├── customer_id=1/
├── customer_id=2/
├── customer_id=3/
├── ...
└── customer_id=1,000,000/
```

Even if the dataset contains substantial total volume, individual partitions can be tiny.

The interaction is:

```text
High-cardinality partition key
       ↓
Many partitions
       ↓
Little data per partition
       ↓
Tiny files / tiny directories
```

## Detection

For each partition record:

- partition count;
- file count;
- total bytes;
- median file size.

The health report in this module is designed to expose exactly this pattern.

## Prevention

Use a partition key and granularity that matches actual query filters and creates meaningful data volumes per partition. Sorting or clustering within larger partitions may be preferable to another partition level when appropriate.

---

# 13. Parallel Writers

Imagine:

```text
100 workers
×
10 partitions
=
Many concurrent writer/partition combinations
```

Even when the partition scheme is sensible, each writer may independently produce files.

## Why this causes fragmentation

Suppose each worker writes only a small amount to a partition before its task completes. You can end up with:

```text
partition A/
  worker-01.parquet
  worker-02.parquet
  worker-03.parquet
  ...
```

Each file may be valid and individually useful. The problem is aggregate fragmentation.

## Prevention

- reduce excessive writer fan-out;
- coalesce output when the engine allows it;
- use batch-oriented writes;
- avoid a file-per-worker-per-partition pattern for tiny amounts of data;
- benchmark writer throughput against resulting file counts.

Do not prescribe a universal number of writers. The right setting depends on data volume, partition cardinality, CPU, storage, and latency requirements.

---

# 14. Tiny Incremental Deltas

A common pattern is:

```text
Morning job → 15 MB
Noon job    → 8 MB
Evening job → 20 MB
```

Each delta is useful on its own, but a high-frequency append pattern can create a large population of small files over time.

This is especially common when changes are append-only and no downstream process merges them.

## Detection

Plot file count over time by partition:

```text
File Count
│
│             /
│           /
│         /
│       /
│______/____________ Time
```

A steadily growing count with a stable small median is a strong signal that the write path or compaction cadence needs attention.

## Prevention

Either:

1. batch updates before writing; or
2. explicitly operate a compaction process with clear health thresholds.

---

# 15. The Target File Size Problem

Choosing file size sounds simple until you realize that several objectives pull in opposite directions.

You want:

- few enough files to control metadata and request overhead;
- enough files to expose useful read parallelism;
- files that compress reasonably well;
- files that can be rewritten without excessive cost;
- writer memory requirements that fit the runtime;
- a layout that works across common query patterns.

This is an optimization problem, not a single constant.

---

# 16. The Roadmap's 128 MB–1 GB Range

Use approximately **128 MB–1 GB** as a practical analytical Parquet starting range.

Why a range?

Because different workloads need different trade-offs.

A rough mental model:

```text
Smaller target
  → more files
  → potentially more parallelism
  → more metadata/request overhead

Larger target
  → fewer files
  → less per-file overhead
  → potentially less independent parallelism
  → larger rewrite units
```

The target range must also be interpreted in relation to partition volume.

A partition holding only 80 MB of total data cannot magically produce a 256 MB file without combining data from elsewhere, which may violate the partitioning design.

Therefore:

> Target file sizing and partition sizing must be designed together.

---

# 17. Why File Size Is a Trade-off

A useful engineering view is:

```text
File size
   │
   ├── Too small → coordination overhead
   │
   ├── Healthy range → balanced
   │
   └── Too large → weak parallelism / expensive rewrites
```

Factors to evaluate:

- data volume per partition;
- query concurrency;
- scan selectivity;
- engine scheduling model;
- CPU availability;
- storage bandwidth;
- object-store behavior;
- codec and compression ratio;
- row width;
- update/rewrite frequency.

Do not optimize one dimension while ignoring the others.

---

# 18. The Opposite Problem — Files That Are Too Large

Avoiding small files does **not** mean "make every file gigantic."

A partition containing:

```text
1 × 10 GB file
```

might be perfectly acceptable for one workload and inefficient for another.

Potential issues include:

- less read parallelism;
- fewer independent units for scheduling;
- large rewrite costs if one portion changes;
- larger writer-memory requirements;
- larger failure/retry units;
- slower recovery after partial failures;
- more data that may be rewritten than the logical change requires.

A better model is:

```text
Too small
  → too much overhead

Too large
  → too little useful parallelism / expensive rewrites

Healthy range
  → balance
```

Do not infer that every 10 GB file must be split. Measure the workload first.

---

# 19. Rows Per File vs Bytes Per File

This is one of the most important concepts in the chapter.

Suppose you configure:

```text
1,000,000 rows per file
```

That does **not** define the physical size in bytes.

One million rows can have very different physical sizes depending on:

- average row width;
- strings vs numeric columns;
- null frequency;
- nested fields;
- encoding;
- compression;
- data repetition;
- sort order.

For example:

```text
1,000,000 narrow numeric rows
        vs
1,000,000 wide text-heavy rows
```

can result in drastically different Parquet sizes.

Therefore:

> **A row-count target is an indirect proxy for file size.**

It is useful for writer control, but it is not a byte-level guarantee.

---

# 20. Preventing Small Files at Write Time

The three prevention mechanisms in the roadmap are:

1. control rows per file;
2. reduce excessive writer parallelism per partition;
3. batch incoming writes.

Conceptually:

```text
Small incoming batches
        ↓
Buffer
        ↓
Batch
        ↓
Write healthy-sized files
```

Prevention is usually cheaper than repeatedly repairing a layout after the fact.

But prevention can increase ingestion latency or introduce buffering state. That is why compaction remains useful when freshness requirements make tiny initial writes unavoidable.

---

# 21. `max_rows_per_file`

PyArrow's dataset writer provides `max_rows_per_file` to cap how many rows are placed into an output file. The documented default is no row-per-file limit (`0`), and the writer also has controls for row groups and open-file behavior. The important limitation is that a row cap is **not a byte-size guarantee**. citeturn169376search0

## Example

```python
from pathlib import Path

import pyarrow as pa
import pyarrow.dataset as ds


def write_partitioned_dataset(table: pa.Table, output_root: str | Path) -> None:
    output_root = Path(output_root)

    ds.write_dataset(
        data=table,
        base_dir=output_root,
        format="parquet",
        partitioning=["year", "month"],
        partitioning_flavor="hive",
        max_rows_per_file=1_000_000,
        # Keep row-group controls explicit for a benchmark.
        min_rows_per_group=100_000,
        max_rows_per_group=100_000,
        existing_data_behavior="error",
    )
```

### What the important arguments mean

- `max_rows_per_file` limits rows per physical file.
- `min_rows_per_group` and `max_rows_per_group` control row-group formation; these are separate from file size.
- `existing_data_behavior="error"` is useful for a first write because it avoids silently overwriting an existing output.
- The partitioning settings decide where files are created, not the byte size of each file.

Current PyArrow documentation also notes that reducing `max_open_files` too aggressively can fragment writes into additional small files; this is a useful example of two writer controls interacting rather than acting independently. citeturn169376search0

## Production lesson

Treat row limits as a **write-control knob**, then measure the resulting byte distribution. Do not write a policy that says "1,000,000 rows means 256 MB."

---

# 22. Writer Parallelism

Consider this simplified model:

```text
Partitions
   ×
Writers
   ×
Micro-batches
   ↓
Physical file count
```

This is not a literal exact formula for every engine, but it is a useful risk model.

## Example

Suppose each batch is only 100 MB and 20 workers participate. If every worker independently touches multiple partitions, the output can be fragmented even though the total batch volume looks reasonable.

## Engineering response

Ask:

1. How much data does each writer receive?
2. How many partitions does each writer touch?
3. Does the writer keep file handles open long enough to accumulate useful data?
4. Does the execution engine coalesce small outputs?
5. Does the dataset writer expose a configurable parallelism/open-file limit?

The goal is not to minimize writer count. It is to avoid producing a tiny object for every writer/partition combination.

---

# 23. Batching

Suppose the application receives:

```text
10,000 records
     ↓
Buffer
     ↓
50,000 records
     ↓
Write
```

Compared with writing every 10,000 records independently, batching can reduce file count and may improve compression and metadata efficiency.

## Trade-off

Batching adds latency:

```text
Smaller batch
  → fresher data
  → more frequent writes
  → more files

Larger batch
  → fewer writes
  → better physical efficiency
  → potentially higher freshness latency
```

The right batch size or interval is a requirement to be measured, not a universal constant.

---

# 24. File Health

"File health" is broader than average file size.

Track at least:

- file count;
- total bytes;
- size distribution;
- partition-level statistics.

Conceptual example:

```text
Healthy partition:
20 files
most files 300–600 MB

Unhealthy partition:
8,000 files
most files 2–10 MB
```

An average can hide both situations.

## A useful health view

```text
Partition
   │
   ├── File count
   ├── Total bytes
   ├── p50 size
   ├── p95 size
   ├── p99 size
   ├── % below minimum
   ├── % above preferred maximum
   └── Status
```

---

# 25. File-Size Distributions and Percentiles

At minimum, examine:

- minimum;
- maximum;
- mean;
- median / p50;
- p90;
- p95;
- p99.

Suppose:

```text
Average = 300 MB
```

That might hide a distribution like:

```text
many files near 5 MB
many files near 20 MB
some files near 300 MB
few files near 2 GB
```

The average alone does not tell you whether the partition has a small-file tail, an oversized-file tail, or both.

A better mental model is:

```text
lower tail ← distribution → upper tail
   p01        p50        p95   p99
```

The policy may therefore need:

- a lower-bound threshold;
- a preferred range;
- an upper-bound threshold.

---

# 26. Required File-Health Lab: `file_health_report(root)`

The roadmap requires a complete reference implementation inside this Markdown file. **Do not create a separate `file_health_report.py` file.**

The function below is intentionally local-filesystem oriented so the mechanics are easy to inspect. A production object-store implementation should use the storage layer's native listing/stat APIs instead of assuming `Path.rglob()` works remotely.

```python
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def _partition_key(root: Path, parquet_path: Path) -> str:
    """Infer a simple partition label from the file's parent path.

    This is intentionally educational. Real production code should parse
    partition keys explicitly rather than treating the relative parent path
    as the canonical partition identifier.
    """
    relative_parent = parquet_path.relative_to(root).parent
    if str(relative_parent) == ".":
        return "__ROOT__"
    return str(relative_parent)


def _percentile(series: pd.Series, q: float) -> float:
    """Return a percentile in bytes using pandas' quantile implementation."""
    return float(series.quantile(q))


def file_health_report(
    root: str | Path,
    *,
    min_target_bytes: int,
    max_target_bytes: int,
    unhealthy_fraction: float = 0.50,
) -> pd.DataFrame:
    """Return file-health metrics grouped by partition path.

    Parameters
    ----------
    root:
        Local dataset root containing Parquet files.
    min_target_bytes:
        Lower edge of the preferred size range.
    max_target_bytes:
        Upper edge of the preferred size range.
    unhealthy_fraction:
        Fraction of files outside the preferred range that marks a
        partition unhealthy. Keep this configurable per environment.
    """
    root = Path(root)

    if min_target_bytes <= 0:
        raise ValueError("min_target_bytes must be positive")
    if max_target_bytes < min_target_bytes:
        raise ValueError("max_target_bytes must be >= min_target_bytes")
    if not 0.0 <= unhealthy_fraction <= 1.0:
        raise ValueError("unhealthy_fraction must be between 0 and 1")
    if not root.exists():
        raise FileNotFoundError(root)

    rows: list[dict[str, object]] = []
    for path in root.rglob("*.parquet"):
        if path.is_file():
            rows.append(
                {
                    "partition": _partition_key(root, path),
                    "path": str(path),
                    "size_bytes": path.stat().st_size,
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=[
                "partition",
                "files",
                "total_mb",
                "min_mb",
                "p50_mb",
                "mean_mb",
                "p90_mb",
                "p95_mb",
                "p99_mb",
                "max_mb",
                "small_fraction",
                "large_fraction",
                "status",
            ]
        )

    frame = pd.DataFrame(rows)
    reports: list[dict[str, object]] = []

    for partition, group in frame.groupby("partition", sort=True):
        sizes = group["size_bytes"].astype("float64")
        small_fraction = float((sizes < min_target_bytes).mean())
        large_fraction = float((sizes > max_target_bytes).mean())

        if small_fraction >= unhealthy_fraction:
            status = "SMALL_FILES"
        elif large_fraction >= unhealthy_fraction:
            status = "OVERSIZED_FILES"
        elif small_fraction > 0 or large_fraction > 0:
            status = "MIXED_RANGE"
        else:
            status = "HEALTHY"

        reports.append(
            {
                "partition": partition,
                "files": int(len(sizes)),
                "total_mb": float(sizes.sum() / (1024**2)),
                "min_mb": float(sizes.min() / (1024**2)),
                "p50_mb": _percentile(sizes, 0.50) / (1024**2),
                "mean_mb": float(sizes.mean() / (1024**2)),
                "p90_mb": _percentile(sizes, 0.90) / (1024**2),
                "p95_mb": _percentile(sizes, 0.95) / (1024**2),
                "p99_mb": _percentile(sizes, 0.99) / (1024**2),
                "max_mb": float(sizes.max() / (1024**2)),
                "small_fraction": small_fraction,
                "large_fraction": large_fraction,
                "status": status,
            }
        )

    report = pd.DataFrame(reports)
    return report.sort_values(
        by=["status", "files"],
        ascending=[True, False],
        ignore_index=True,
    )


if __name__ == "__main__":
    report = file_health_report(
        "./orders",
        min_target_bytes=128 * 1024**2,
        max_target_bytes=1 * 1024**3,
        unhealthy_fraction=0.50,
    )
    print(report.to_string(index=False))
```

## Example report shape

The values below are placeholders only to show the column layout. They are **not measured results**:

```text
partition                  files  total_mb  p50_mb  p95_mb  p99_mb  status
year=2026/month=09/day=27     ...       ...      ...      ...      ...  HEALTHY
year=2026/month=09/day=28     ...       ...      ...      ...      ...  SMALL_FILES
```

The learner's run must generate the real numbers.

## Why these metrics?

- `files` measures fragmentation directly.
- `total_mb` provides context for the partition volume.
- `p50` shows the typical file.
- `p95` and `p99` expose tails.
- `small_fraction` turns file-size observations into a configurable health signal.
- `large_fraction` prevents a "fix" that simply creates oversized files.

## Production warning

The `_partition_key()` helper is deliberately simple. Real implementations should use explicit parsing based on the dataset's partition contract, especially when partition directory names contain arbitrary paths or when data can be stored in multiple layouts.

---

# 27. Health Thresholds

Do not hard-code:

```text
healthy = exactly X MB
```

Instead configure:

```python
min_target_bytes
max_target_bytes
unhealthy_fraction
```

You may also add:

- maximum file count per partition;
- maximum fraction of oversized files;
- freshness exceptions;
- special rules for low-volume partitions;
- workload-specific priority.

## Example policy logic

```text
if healthy:
    skip
elif too many small files:
    candidate for compaction
elif too many oversized files:
    candidate for split/rewrite
else:
    review mixed distribution
```

A threshold is a policy decision. It should be documented with its workload assumptions.

---

# 28. Compaction

> **Compaction combines many small files into fewer, better-sized files.**

Conceptually:

```text
Before
├── 5 MB
├── 7 MB
├── 12 MB
├── 9 MB
├── 6 MB
└── ...

          ↓ COMPACTION

After
├── 350 MB
├── 400 MB
└── ...
```

Potential benefits include:

- fewer files to discover;
- lower metadata overhead;
- fewer object interactions;
- fewer execution fragments;
- potentially better compression;
- potentially better locality and statistics when sorting is used.

These are **potential** benefits, not guaranteed outcomes.

Compaction itself costs resources, so the process is not free.

---

# 29. What Compaction Actually Does

Think of compaction as:

```text
Identify unhealthy partition
        ↓
Discover files
        ↓
Read data
        ↓
Combine
        ↓
Optional sort / organization
        ↓
Write new files
        ↓
Validate
        ↓
Publish
        ↓
Cleanup old data later
```

The resource model is:

```text
Compaction Cost
=
Read Existing Files
+
CPU / Sort
+
Write New Files
+
Validation
+
Temporary Storage
+
Object Requests
```

Therefore:

> Compaction is a performance optimization that consumes resources to improve future work.

---

# 30. Compaction with `pyarrow.dataset`

PyArrow's dataset API can discover a collection of Parquet fragments and scan them as one dataset. Its scanner supports filtering and batch reads; `to_table()` materializes the selected data into memory, while `to_batches()` provides record-batch iteration. Current documentation describes dataset fragments as the physical files consumed by a `FileSystemDataset`. citeturn305983search0

For a moderate-sized partition, the simplest educational flow is:

```python
import pyarrow.dataset as ds

partition = ds.dataset("./orders/year=2026/month=09/day=28", format="parquet")
table = partition.to_table()
```

To inspect how many files participate:

```python
fragments = list(partition.get_fragments())
print("input files:", len(fragments))
```

A filter can be pushed to the dataset layer when supported by the format and metadata:

```python
filtered = partition.to_table(
    filter=ds.field("status") == "COMPLETE",
)
```

The current PyArrow documentation notes that dataset filters can use partition information and file-format metadata such as Parquet statistics when possible. citeturn305983search0

## Important production nuance

`to_table()` reads all selected data into memory. That is convenient for a teaching example but is not automatically appropriate for a very large partition. For larger partitions, design a batch-oriented compaction implementation around `to_batches()` or a more scalable engine, and explicitly benchmark memory use.

---

# 31. Target Bytes

The roadmap asks for:

```python
def compact_partition(path, target_bytes):
    ...
```

The target is expressed in bytes because the real policy concerns **physical file size**.

But there is a catch:

> You do not know the exact final Parquet byte size before compression and encoding are applied.

Therefore `target_bytes` is an approximate planning target, not a guarantee.

## An empirical estimator

One useful approximation is:

```text
estimated physical bytes per row
=
input parquet bytes / input row count
```

Then:

```text
estimated rows per output file
≈
target_bytes / estimated physical bytes per row
```

This is only a starting estimate. Sorting, value distributions, dictionary behavior, row-group choices, and compression can change the resulting file size.

## Better production approach

1. estimate from recent physical data;
2. write a representative sample;
3. inspect resulting sizes;
4. adjust the row target;
5. re-measure;
6. document the observed range.

---

# 32. Sorting During Compaction

The roadmap requires compacted files to be considered **well-sized and sorted** when sorting is appropriate.

Sorting can help because it may improve:

- locality of similar values;
- compression opportunities;
- Parquet statistics usefulness;
- clustering for common filters;
- pruning effectiveness for some workloads.

But sorting is not free.

```text
Sort
 ↓
CPU + memory + I/O
 ↓
Potentially better physical layout
```

Therefore:

> Sort only when the query/layout benefit justifies the extra compaction cost.

Do not universally sort every dataset during every compaction.

Example:

```python
sorted_table = table.sort_by([
    ("event_date", "ascending"),
    ("customer_id", "ascending"),
])
```

The best sort keys come from actual query patterns, not from habit.

---

# 33. Progressive Compaction Algorithm

Use this sequence in production design reviews:

```text
1. Identify partition
2. Discover files
3. Measure health
4. Select eligible files
5. Read through dataset API
6. Reorder / sort where appropriate
7. Write new files to temp location
8. Validate row count and schema
9. Validate file distribution
10. Publish / swap
11. Verify publication
12. Remove old files only after safe publication
```

Each step has a failure mode.

## Step 1 — Identify partition

Avoid compacting the entire lake by default. Operate on an explicit partition or a controlled set of partitions.

## Step 2 — Discover files

Take a consistent snapshot of the input set as far as the storage system and operational design allow.

## Step 3 — Measure health

Use the same health metrics as the monitoring process.

## Step 4 — Select eligible files

Prefer targeted compaction over rewriting healthy files.

## Step 5 — Read

Use `pyarrow.dataset` for format-aware scanning.

## Step 6 — Sort where justified

Treat sorting as a separate cost and benchmark variable.

## Step 7 — Write temp output

Never publish partially written production files.

## Step 8 — Validate

At minimum:

- schema compatibility;
- input/output row counts;
- data correctness checks;
- expected output file count;
- output size distribution.

## Step 9 — Publish

Use an appropriate local or object-store publication method and clearly document its guarantees.

## Step 10 — Cleanup

Only after successful publication and after the reader-safety policy says the old files can be removed.

---

# 34. Safe Compaction

The safe conceptual pattern is:

```text
Old partition
    ↓
Read
    ↓
Temporary output
    ↓
Validate
    ↓
Commit / publish
    ↓
Readers see new state according to the commit mechanism
    ↓
Old files removed later
```

The critical rule is:

> **Never delete the old files first and hope the new files finish successfully.**

That creates a direct window for missing data if the compaction job crashes.

---

# 35. Temporary Output

Suppose production data lives under:

```text
production/orders/year=2026/month=09/day=28/
```

Write compaction output somewhere isolated:

```text
_temp/compaction/run-123/
```

The temporary location should not be included in normal dataset discovery.

## Validate before publish

Check:

- row count;
- schema;
- expected columns;
- duplicate behavior;
- data correctness;
- expected file count;
- size distribution;
- sorting requirement if enabled.

A temporary prefix is a **publication boundary**, not merely a scratch directory.

---

# 36. Swap / Commit

On a local filesystem, rename/replace operations can have stronger semantics than equivalent operations implemented over an object store.

On object storage, a logical "rename" may actually involve copy/delete or other object operations and therefore may not provide the same atomic semantics as a local filesystem rename.

Use careful language:

> **Publication semantics depend on the storage system and commit strategy.**

Common patterns include:

### Local best-effort directory replacement

Useful for a teaching lab and some controlled local jobs, but still requires a clearly defined crash policy.

### Manifest-based publication

Readers resolve the active version through metadata/manifest state. New output can be fully written before the active pointer changes.

### Table-format commit

A lakehouse table format provides a metadata/transaction layer designed for versioned table state and concurrent operations. Detailed table-format internals are deferred to the later module specified by the roadmap.

---

# 37. Crash Safety

Scenario:

```text
Compaction started
     ↓
New files partially written
     ↓
Process crashes
```

Desired property:

> **The last valid dataset state remains readable.**

A temporary prefix helps because partial output is isolated from the production path.

After a crash, the system should be able to:

- leave old data intact;
- identify abandoned temp output;
- quarantine or clean abandoned output;
- retry compaction safely.

Do not claim that a plain directory automatically provides perfect transactional recovery.

---

# 38. Idempotent Compaction

Idempotency means:

> Running the operation repeatedly should not continually multiply logical data or create duplicate state.

Conceptually:

```text
Before:
100 small files

Run compaction:
→ 10 healthier files

Run again:
→ no logical duplication
→ healthy input can be skipped
```

## How to approach idempotency

- deterministic or well-defined input selection;
- explicit run identifiers for temp output;
- replacement rather than append semantics;
- publication after validation;
- cleanup separated from publication;
- clear rules for already healthy partitions.

A common anti-pattern is:

```text
read old files
write new files alongside old files
repeat
```

That is not compaction. It is duplication.

---

# 39. Required Idempotency Test

### Test 1 — Compact once

Run compaction on an unhealthy partition.

Verify:

- logical row count;
- representative values;
- file-size distribution.

### Test 2 — Run again

Run the same compaction logic again.

Verify:

- no duplicate rows;
- no runaway file growth;
- stable partition state;
- or a clean no-op because the partition is now healthy.

### Test 3 — Compact an already healthy partition

Verify that policy logic can skip it or avoid making a harmful rewrite.

---

# 40. Concurrent Readers

Consider:

```text
Reader A
   ↓
starts scanning old files

Compactor
   ↓
writes new files

Compactor
   ↓
removes old files
```

A reader may still need old objects after the compactor has decided that the new files are published.

## Risks

- a reader sees missing objects;
- a reader sees a partial mixed state;
- a retry observes a different file set;
- a query fails after a file disappears.

## Mitigations

Depending on architecture:

- delay deletion of old files;
- keep a grace period;
- use versioned paths;
- use manifests/snapshots;
- use a table format with stronger isolation semantics.

There is no universal safe deletion delay. It depends on reader lifetime, caching, retries, storage semantics, and the reader/commit model.

---

# 41. Concurrent Writers

Now add writers:

```text
Writer A
    +
Compactor
    +
Writer B
```

Potential problems:

- compactor reads a file that a writer is still producing;
- a new writer creates files while the compactor is selecting inputs;
- writer updates are accidentally lost during replacement;
- data is duplicated if both old and new versions survive;
- a partition can become internally inconsistent.

## Plain-directory requirement

Operational coordination is required.

Examples include:

- scheduling compaction during a known write boundary;
- locking/leases outside the raw files themselves;
- writing immutable batch versions;
- using a table format with transaction-aware commits.

Do not imply that merely using a temp directory solves concurrent-writer coordination. It solves only one part: partial-output exposure.

---

# 42. Plain Directories vs Table Formats

Awareness only.

A plain directory is roughly:

```text
files + directories
```

A lakehouse table format adds a logical metadata/transaction layer:

```text
logical table
+
metadata / transaction state
```

That additional layer can support stronger mechanisms around:

- commits;
- snapshots;
- reader isolation;
- concurrent writer coordination;
- compaction planning.

The roadmap introduces these internals later in the table-format module. The key takeaway now is:

> **Raw files solve storage. They do not automatically solve transactional table state.**

---

# 43. File-Health Monitoring

Treat file health as a dataset SLO-like operational signal, even if the exact thresholds vary by platform.

Conceptual pipeline:

```text
Dataset
   ↓
Scheduled health scan
   ↓
Partition metrics
   ↓
Threshold evaluation
   ↓
Alert / queue compaction
```

Track per partition:

- file count;
- total bytes;
- mean;
- median / p50;
- p95;
- p99;
- smallest files;
- largest files;
- unhealthy-file percentage.

A dashboard can therefore look like:

| Partition | File Count | p50 | p95 | p99 | Total Size | Health |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `...` | ... | ... | ... | ... | ... | ... |
| `...` | ... | ... | ... | ... | ... | ... |

Use real measurements from the learner's environment; do not fill the table with made-up production values.

---

# 44. File-Health Alerts

Configurable example rules:

```text
ALERT:
> configured fraction of files below minimum target

ALERT:
partition file count above configured maximum

ALERT:
p95 or p99 file size outside configured policy range
```

A useful alert contains enough context to take action:

```text
partition
file_count
p50
p95
p99
small_fraction
large_fraction
total_bytes
last_compaction_time
```

Avoid alerts that only say "small files detected." The operator needs enough information to judge severity and cost.

---

# 45. Compaction Scheduling

Do not compact everything on every run.

A useful prioritization model considers:

### Recent partitions

These often receive new small files continuously.

### Frequently queried partitions

Compaction can create direct downstream value if the partition is on a hot query path.

### Highly unhealthy partitions

High file counts and small p50/p95 values indicate physical fragmentation.

### Rarely queried historical partitions

They may be lower priority because their future query savings may not justify the immediate rewrite cost.

Scheduling dimensions:

- freshness;
- query frequency;
- health severity;
- compaction cost;
- storage budget;
- current system load.

---

# 46. Compaction Frequency

There is no universal cadence.

Possible strategies:

- continuous/background;
- hourly;
- daily;
- event-triggered;
- threshold-triggered.

Evaluate the trade-off:

```text
More frequent compaction
→ healthier files sooner
→ more compaction work

Less frequent compaction
→ lower maintenance cost
→ unhealthy layout persists longer
```

A good scheduler is usually **trigger-driven plus resource-aware**, rather than "run every day because that is easy."

---

# 47. Required Bad-Dataset Simulation

The roadmap explicitly asks for one file per minute over one month.

Mathematically:

```text
1 file / minute
× 60 minutes / hour
× 24 hours / day
× 30 days
=
43,200 files
```

This is intentionally a bad dataset.

Do not add extra assumptions about partitions or object counts beyond the exercise definition.

## Simulation exercise

Generate small Parquet files that look like streaming outputs.

A minimal local simulation can use a small batch repeated across timestamps:

```python
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


def simulate_streaming_writer(root: str | Path, minutes: int = 60) -> None:
    root = Path(root)
    start = datetime(2026, 9, 1, tzinfo=timezone.utc)

    for offset in range(minutes):
        ts = start + timedelta(minutes=offset)
        partition = (
            root
            / f"year={ts.year}"
            / f"month={ts.month:02d}"
            / f"day={ts.day:02d}"
        )
        partition.mkdir(parents=True, exist_ok=True)

        table = pa.table(
            {
                "event_time": [ts],
                "order_id": [f"order-{offset:08d}"],
                "amount": [1.0],
            }
        )
        pq.write_table(table, partition / f"part-{offset:08d}.parquet")
```

For a real lab, scale the loop to the exact number of files you want to study. Start smaller while validating code, then generate the intentionally unhealthy dataset.

---

# 48. Bad-Dataset Query Experiment

Run the same query before and after compaction.

## Before

Measure:

- file count;
- file sizes;
- p50/p95/p99;
- query runtime;
- bytes read where available;
- object-storage request behavior where observable.

## Compact

Perform only the layout change you are testing.

## After

Measure exactly the same metrics.

Use a table like:

| State | Files | Median Size | p95 Size | Query Time | Bytes Read | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Before |  |  |  |  |  |  |
| After |  |  |  |  |  |  |

Do not fabricate any value.

---

# 49. MinIO Object-Storage Experiment

The roadmap requires a MinIO experiment because it gives you a controlled S3-compatible environment for observing object interactions.

Conceptually:

```text
Tiny Parquet files
      ↓
MinIO
      ↓
DuckDB
      ↓
Benchmark
```

Then:

```text
Compaction
      ↓
Healthier-sized files
      ↓
MinIO
      ↓
DuckDB
      ↓
Benchmark again
```

## Control variables

Keep constant:

- dataset;
- query;
- schema;
- codec;
- storage environment;
- machine/resources;
- query parameters.

Change:

```text
file layout / compaction state
```

Then separately test sorting as a second experiment if desired.

---

# 50. Request-Count Measurement

There is no single universal MinIO metric name that should be copied blindly into this chapter. Metric names and instrumentation details can depend on version, deployment, and how clients connect.

Use one of these measurement approaches:

1. MinIO server metrics available in your deployment;
2. access logs;
3. a reverse proxy or gateway request counter;
4. storage-client instrumentation;
5. controlled experiments that count selected request classes.

Document exactly what you measured:

```text
Measurement method:
MinIO version:
Client:
Request categories counted:
Cache state:
Workload:
```

Do not turn an observed request count in MinIO into a universal statement about every object-storage provider.

---

# 51. PyArrow File Discovery and Size Inspection

For local datasets, Python's `pathlib` makes a simple file-health inspection tool easy to understand.

```python
from pathlib import Path

root = Path("./orders")
parquet_files = [p for p in root.rglob("*.parquet") if p.is_file()]

print("file count:", len(parquet_files))

for path in parquet_files[:10]:
    size_mb = path.stat().st_size / (1024**2)
    print(f"{size_mb:10.2f} MB  {path}")
```

For large object stores, replace this local traversal with the storage connector's listing/stat mechanism.

---

# 52. Percentile Calculation

Using pandas is straightforward and already established in the roadmap environment.

```python
import pandas as pd

sizes = [5, 7, 12, 20, 300, 350, 400, 2_000]  # example numbers only
sizes_series = pd.Series(sizes, dtype="float64")

p50 = sizes_series.quantile(0.50)
p95 = sizes_series.quantile(0.95)
p99 = sizes_series.quantile(0.99)

print("p50:", p50)
print("p95:", p95)
print("p99:", p99)
```

Do not use the example values as evidence about a real dataset.

Percentile algorithms can also differ in their interpolation conventions. For operations work, consistency matters: use the same tool/method across monitoring and benchmark reports.

---

# 53. Compacting a Partition: Complete Reference Implementation

The function below is deliberately labeled **educational/reference**.

It demonstrates the core sequence:

```text
Discover → Read → Estimate → Optional Sort → Write Temp → Validate → Publish
```

It is intended for a moderate local partition. It should not be interpreted as a complete production-grade transactional compactor for a distributed object store.

```python
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

import pyarrow as pa
import pyarrow.dataset as ds


def _count_parquet_files(path: Path) -> int:
    return sum(1 for p in path.rglob("*.parquet") if p.is_file())


def _parquet_bytes(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*.parquet") if p.is_file())


def _validate_compacted_output(
    input_table: pa.Table,
    output_path: Path,
) -> pa.Table:
    output_dataset = ds.dataset(output_path, format="parquet")
    output_table = output_dataset.to_table()

    if input_table.schema != output_table.schema:
        raise ValueError(
            "Output schema does not match input schema."
        )

    if input_table.num_rows != output_table.num_rows:
        raise ValueError(
            f"Row-count mismatch: {input_table.num_rows} != "
            f"{output_table.num_rows}"
        )

    # This equality check is deliberately strict for the educational lab.
    # We preserve input row order by using one threaded writer with
    # preserve_order=True. If a production writer deliberately reorders data,
    # replace this with a canonical content check appropriate to the table.
    if not input_table.equals(output_table):
        raise ValueError("Input and output rows/values are not identical.")

    return output_table


def _publish_local_partition_best_effort(
    temp_path: Path,
    target_path: Path,
) -> Path | None:
    """Publish a local directory using a backup rename.

    This is intentionally a best-effort local example. It is NOT a claim that
    a plain directory swap provides general transactional isolation.
    """
    backup_path = target_path.with_name(
        f"{target_path.name}.__backup__{uuid.uuid4().hex[:12]}"
    )

    target_existed = target_path.exists()
    if target_existed:
        target_path.rename(backup_path)

    try:
        temp_path.rename(target_path)
    except Exception:
        # Try to restore the old target if publication failed.
        if target_existed and backup_path.exists() and not target_path.exists():
            backup_path.rename(target_path)
        raise

    return backup_path if target_existed else None


def compact_partition(
    path: str | Path,
    target_bytes: int,
    *,
    sort_columns: list[tuple[str, str]] | None = None,
) -> dict[str, object]:
    """Compact one local Parquet partition into approximately target-sized files.

    Important limitations:
    - The function materializes the partition as one Arrow Table.
    - target_bytes is converted to an approximate row target based on the
      observed physical bytes-per-row of the existing input.
    - Final compressed sizes are not guaranteed to equal target_bytes.
    - Publication is a best-effort local directory replacement, not a
      transactional object-store commit protocol.
    """
    if target_bytes <= 0:
        raise ValueError("target_bytes must be positive")

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(source)

    dataset = ds.dataset(source, format="parquet")
    input_table = dataset.to_table()

    input_file_count = _count_parquet_files(source)
    input_bytes = _parquet_bytes(source)

    if input_table.num_rows == 0:
        return {
            "status": "SKIP_EMPTY",
            "input_files": input_file_count,
            "input_bytes": input_bytes,
        }

    # Empirical starting estimate. Existing compressed Parquet bytes are a
    # better signal than raw Arrow memory size for this particular goal.
    bytes_per_row = input_bytes / input_table.num_rows
    estimated_rows = max(1, int(target_bytes / bytes_per_row))

    working_table = input_table
    if sort_columns:
        working_table = working_table.sort_by(sort_columns)

    temp_path = source.parent / (
        f".{source.name}.__compaction_tmp__{uuid.uuid4().hex}"
    )
    temp_path.mkdir(parents=True, exist_ok=False)

    try:
        ds.write_dataset(
            data=working_table,
            base_dir=temp_path,
            format="parquet",
            max_rows_per_file=estimated_rows,
            # Keep row-group settings explicit for this educational lab.
            min_rows_per_group=min(100_000, estimated_rows),
            max_rows_per_group=min(100_000, estimated_rows),
            basename_template="part-{i}.parquet",
            use_threads=False,
            preserve_order=True,
            existing_data_behavior="error",
        )

        _validate_compacted_output(working_table, temp_path)

        output_files = _count_parquet_files(temp_path)
        output_bytes = _parquet_bytes(temp_path)

        backup_path = _publish_local_partition_best_effort(
            temp_path,
            source,
        )

        # Cleanup happens only after successful publication. Keep the returned
        # backup path so an operator can choose a safer delayed-deletion policy.
        return {
            "status": "PUBLISHED",
            "input_files": input_file_count,
            "input_bytes": input_bytes,
            "output_files": output_files,
            "output_bytes": output_bytes,
            "estimated_rows_per_file": estimated_rows,
            "backup_path": str(backup_path) if backup_path else None,
        }
    except Exception:
        # Production systems should record this failure and use a lifecycle/
        # quarantine policy for any abandoned temporary output.
        if temp_path.exists():
            shutil.rmtree(temp_path, ignore_errors=True)
        raise
```

## Why this implementation is deliberately not "fully production-ready"

It makes the following compromises for teachability:

- it materializes the whole partition into memory;
- it estimates bytes-per-row from existing files;
- it performs a local directory publication pattern;
- it leaves backup cleanup to a separate operational decision;
- it does not implement a distributed lock or writer lease;
- it does not implement a table-format transaction log.

Those are not bugs in the lesson. They are explicit boundaries.

---

# 54. Production-Scale Compaction Notes

For much larger partitions, a production implementation should challenge the assumption that the entire partition fits comfortably in memory.

The current PyArrow dataset API exposes batch-oriented scanning via `to_batches()` and scanner controls such as batch size and read-ahead. citeturn305983search0

A production architecture can therefore use:

```text
Dataset scanner
      ↓
Record batches
      ↓
Optional sorting strategy
      ↓
Incremental writer
      ↓
Target-sized files
```

But global sorting across arbitrarily large input is a different engineering problem from simply sorting one in-memory table. For very large datasets, use an engine that supports the required external-sort or distributed execution pattern and benchmark it against the business requirement.

---

# 55. Compaction Selection

Do not compact every file in every partition.

A basic selection policy is:

```text
Healthy
  → skip

Unhealthy + enough eligible files
  → compact

Already being compacted
  → skip / coordinate

Insufficient data to form useful output
  → wait
```

Eligibility can be based on:

- file below minimum preferred size;
- unhealthy partition status;
- sufficient aggregate bytes/files to make the rewrite worthwhile;
- no conflicting compaction job;
- no active rewrite window that would make the input set unstable.

---

# 56. Compaction Cost Model

A simple conceptual model is:

```text
Compaction Cost
=
Read Existing Files
+
CPU / Sort
+
Write New Files
+
Validation
+
Temporary Storage
+
Object Requests
```

Potential future savings:

```text
Future Query Savings
=
Fewer Metadata Operations
+
Fewer Files
+
Potentially Better Reads
+
Potentially Better Compression
```

Therefore:

> **Is the future savings worth the compaction cost?**

That is the business/architecture question.

---

# 57. Compaction ROI

Use this conceptual model:

```text
Compaction ROI
≈
Expected Future Savings
−
Compaction Cost
```

This is not a complete accounting formula. It ignores many business and engineering factors.

It becomes more attractive when:

```text
same partition
×
many future queries
×
meaningful file-fragmentation overhead
```

It becomes less attractive when:

```text
rarely queried
+
expensive rewrite
+
low fragmentation severity
```

The purpose is to teach **cost-aware maintenance**, not "compact whenever the file count looks ugly."

---

# 58. Before/After Measurement

### Before

Measure:

- file count;
- total bytes;
- size distribution;
- query runtime;
- bytes read where available;
- object-store request behavior.

### After

Measure the exact same metrics using the exact same workload.

Use this structure:

```text
Metric                 Before      After      Delta
--------------------------------------------------
File count             ...         ...        ...
Total bytes            ...         ...        ...
p50                    ...         ...        ...
p95                    ...         ...        ...
Query time             ...         ...        ...
Bytes read             ...         ...        ...
Request behavior       ...         ...        ...
```

Do not fill the delta from a hypothetical example. Measure it.

---

# 59. Fair Compaction Benchmark

Keep constant:

- dataset;
- query;
- engine;
- machine;
- storage;
- schema;
- codec;
- partition;
- query parameters;
- query concurrency, when the test is a concurrency benchmark.

Change:

> **File layout / compaction state**

Then run a separate experiment when comparing:

> **Compaction + sorting**

This isolates sorting as an additional variable.

## Warm vs cold cache

Run separate labeled tests when cache behavior matters:

```text
Cold / first read
vs
Warm / repeated read
```

Do not compare one cold run before compaction with one warm run after compaction and call the difference a compaction effect.

---

# 60. Debugging Small Files

Use this pattern for every incident:

> **symptom → possible cause → inspect → measure → fix → lesson**

## Problem 1 — "Thousands of Parquet files suddenly appeared."

Possible causes:

- streaming/micro-batches;
- over-partitioning;
- writer parallelism;
- tiny deltas.

Inspect:

```text
file creation timestamps
files per partition
p50/p95/p99
writer/task configuration
partition cardinality
```

Lesson: inspect the write path, not only the storage layer.

## Problem 2 — "Average file size looks healthy, but queries are still slow."

Investigate:

- p95/p99;
- file count;
- partition pruning;
- row-group layout;
- query selectivity;
- metadata/planning time.

An acceptable average can coexist with a very unhealthy distribution.

## Problem 3 — "Compaction increased query cost."

Investigate:

- files became too large;
- sorting is expensive;
- compression settings changed unintentionally;
- useful parallelism was reduced;
- the benchmark changed cache state.

## Problem 4 — "Compaction duplicated data."

Investigate:

- append instead of replacement;
- old and new files visible together;
- incorrect commit logic;
- stale input discovery;
- non-idempotent retries.

## Problem 5 — "Readers fail during compaction."

Investigate:

- old files deleted too early;
- partial output became discoverable;
- concurrent readers crossed a publication boundary;
- object-store publication semantics were assumed to be transactional.

## Problem 6 — "Compaction keeps running on healthy partitions."

Investigate:

- missing health threshold;
- unstable discovery;
- non-deterministic eligibility;
- policy that always rewrites instead of conditionally compacting.

## Problem 7 — "One partition becomes huge after compaction."

Investigate:

- skew;
- too-large target;
- very high partition volume;
- incorrect grouping of partition paths.

## Problem 8 — "File count improved, but object request count did not."

Investigate:

- instrumentation method;
- query behavior;
- metadata caching;
- partition discovery;
- whether the benchmark actually reached the same objects.

Lesson: a metric changing only in the expected direction is not evidence of causality.

---

# 61. Common Mistakes

## 1. Treating every file under 128 MB as automatically bad

A file is contextual. Small historical partitions or low-volume workloads may not justify immediate rewrites.

## 2. Treating 128 MB–1 GB as a universal law

It is a practical starting range, not a specification of correctness.

## 3. Optimizing only the average

Averages can hide both small-file and oversized tails.

## 4. Ignoring p95/p99

Tail behavior matters when a few partitions contain extreme fragmentation or giant files.

## 5. Producing one giant file per partition

This may destroy useful parallelism and make rewrites expensive.

## 6. Compacting everything every time

Maintenance itself costs CPU, I/O, storage, and request budget.

## 7. Compacting healthy partitions unnecessarily

A healthy partition may have little future value to gain.

## 8. Deleting old files before new files are committed

A failure can leave the dataset incomplete.

## 9. Writing directly into the production partition during compaction

Readers can observe partial output.

## 10. Ignoring concurrent readers

Readers may still depend on old objects after publication.

## 11. Ignoring concurrent writers

The compactor can race with new data and lose or duplicate updates.

## 12. Making compaction non-idempotent

Retries can multiply logical data.

## 13. Creating new small files during compaction

The rewrite may simply move the same fragmentation problem to new paths.

## 14. Ignoring sort cost

Sorting can dominate the maintenance job.

## 15. Changing codecs while testing compaction

You no longer know which change caused the measured effect.

## 16. Comparing different queries before and after

The benchmark is no longer controlled.

## 17. Ignoring object-storage request overhead

Large object counts can change request patterns independently of total bytes.

## 18. Ignoring query frequency

A rarely used partition may not justify an expensive rewrite.

## 19. Assuming row-count targets guarantee byte-size targets

Row width and compression vary.

## 20. Ignoring partition skew

A single hot partition can dominate the maintenance workload.

## 21. Using one fixed target for every dataset

Different row widths and workload patterns need different settings.

## 22. Assuming fewer files always means faster queries

Parallelism and layout quality also matter.

## 23. Assuming more files always means more parallelism and therefore better performance

The overhead can exceed the benefit.

## 24. Ignoring abandoned temp output

Failed compaction can accumulate storage debt if temporary paths are not cleaned up.

---

# 62. Production File-Sizing Policy

A production standard should be a **range plus evidence**, not a universal number.

## File Layout Standard

```text
Dataset:
Partition scheme:
Preferred file-size range:
Minimum acceptable size:
Maximum preferred size:
Health metrics:
Compaction trigger:
Compaction priority:
Sort policy:
Writer batching:
Writer parallelism:
Concurrency policy:
Temporary-output strategy:
Validation:
Cleanup policy:
Monitoring:
Alert thresholds:
Owner:
Review cadence:
```

The roadmap's practical baseline of approximately **128 MB–1 GB** may be used as a starting hypothesis for analytical Parquet, then refined through measurement.

---

# 63. Production Compaction Policy

Example policy:

```text
Compact when:
- partition is unhealthy;
- sufficient files are eligible;
- expected query savings justify cost;
- no conflicting writer/compaction exists.

Do not compact when:
- partition is already healthy;
- another compaction is running;
- data is being actively rewritten;
- validation fails;
- the cost budget for the current window is exhausted.
```

This is a template. The exact thresholds and scheduling rules must be configured for the environment.

---

# 64. Compaction Scheduler Model

Use this architecture:

```text
Every scheduling cycle
        ↓
Scan file health
        ↓
Rank unhealthy partitions
        ↓
Estimate compaction cost
        ↓
Estimate workload benefit
        ↓
Select candidates
        ↓
Compact within resource budget
        ↓
Validate
        ↓
Publish
        ↓
Record outcome
```

Resource awareness matters because a compactor competes with query engines and ingestion jobs for CPU, memory, I/O, and object-store capacity.

---

# 65. Production Case Study

## Scenario

A retail lake receives:

- streaming order events;
- frequent daily updates;
- hourly micro-batches.

Its layout is:

```text
year/month/day/
```

Each day contains thousands of files, commonly around:

```text
2 MB
7 MB
12 MB
20 MB
```

Most queries hit the most recent seven days.

## Questions

1. What is the problem?
2. What caused it?
3. What metrics should be collected?
4. What target range should be considered?
5. Which partitions should be prioritized?
6. How should compaction work?
7. Should compaction sort?
8. How should concurrent readers be handled?
9. How should compaction be made idempotent?
10. How would you prove the change improved the system?

## Worked reasoning

### 1. Problem

The physical layout is highly fragmented relative to the analytical workload. The thousands-of-files-per-day pattern indicates a file-count problem in addition to a data-volume problem.

### 2. Likely causes

The scenario explicitly contains streaming plus hourly micro-batches, so frequent independent writes are a strong candidate. Parallel writer behavior and daily deltas should also be inspected rather than assumed away.

### 3. Metrics

Collect:

- file count by partition;
- total bytes;
- p50/p95/p99;
- small-file percentage;
- query latency for representative seven-day queries;
- bytes read if available;
- request behavior where measurable.

### 4. Target

Start with the roadmap's approximate 128 MB–1 GB analytical Parquet range as a hypothesis. Then check how much data each day actually contains, the engine's parallelism, query concurrency, and rewrite cost.

### 5. Priority

Recent partitions deserve attention because they are both heavily queried and continuously affected by the write pattern. Very old, rarely queried partitions may be lower priority.

### 6. Compaction

Select unhealthy partitions, write to a temporary path, validate, publish safely, and delay cleanup according to the reader/concurrency policy.

### 7. Sorting

Sort only on columns that match important query patterns and only after measuring whether the improved layout offsets the extra compaction cost.

### 8. Concurrent readers

Do not delete old files immediately after writing the new files. Use a publication strategy and a cleanup grace period appropriate to the reader model, or move to a table format with stronger isolation semantics.

### 9. Idempotency

Compaction must replace logical input state rather than append duplicate copies. A second run on already healthy output should either skip or leave an equivalent logical state.

### 10. Proving improvement

Run the same query before and after, on the same engine/storage environment, with the same codec/schema/query parameters. Compare file count, distribution, query time, bytes, and request behavior. Do not fabricate performance improvements.

---

# 66. Architecture Review Scenario

## Proposed design

```text
one file per streaming micro-batch per partition
```

Review it across six dimensions:

- file-count growth;
- object-store interactions;
- compression;
- distributed task overhead;
- query performance;
- downstream compaction cost.

## Alternative A — buffer → batch → write

```text
Streaming events
      ↓
Buffer
      ↓
Batch
      ↓
Healthy file write
```

Trade-off: potentially higher freshness latency.

## Alternative B — small files → scheduled compaction

```text
Streaming events
      ↓
Small files
      ↓
Scheduled compaction
      ↓
Healthy files
```

Trade-off: more operational maintenance and temporary rewrite cost.

## Architecture lesson

The right design depends on the relative importance of:

- ingestion latency;
- query latency;
- storage/request cost;
- operational complexity;
- concurrency requirements.

---

# 67. Large-File Scenario

Suppose a partition contains:

```text
1 × 10 GB file
```

Ask:

- Is this automatically good?
- How much parallelism is exposed?
- What happens if only a small portion of the partition changes?
- What writer memory might be required?
- Does the query engine benefit from more independent files?

The answer is workload dependent.

The goal is balance, not minimizing file count at any cost.

---

# 68. File-Count Mathematics

Example:

```text
Dataset = 1 TB
Target = 256 MB
```

A first-order estimate is:

```text
1 TB / 256 MB
```

Using binary units for consistency:

```text
1 TiB / 256 MiB = 4096
```

That is a **conceptual estimate**, not a promise of exactly 4,096 output files.

Actual output can differ because of:

- uneven partitions;
- compression;
- variable row sizes;
- writer controls;
- final small remainder files;
- parallel writer behavior;
- data-dependent encodings.

Always measure the actual result.

---

# 69. Partition + File-Size Interaction

Connect to Topic 08:

```text
Partition too fine
    → more partitions
    → less data per partition
    → more small files

Partition too coarse
    → fewer partitions
    → more data per partition
    → potentially larger files
```

Therefore:

> **Partition design and file-size design must be evaluated together.**

You cannot pick partition granularity first and file target later without checking the resulting data volume per partition.

---

# 70. Partition + Writer Parallelism

Use this conceptual model:

```text
Partitions
   ×
Writers
   ×
Micro-batches
   ↓
File Count
```

A reasonable partition scheme can still generate an unhealthy layout when writer fan-out is too high.

A useful architecture review asks for an explicit estimate of:

```text
files per batch per partition
×
batches per day
×
partitions per day
```

Then compare that growth with the compaction cadence and storage lifecycle.

---

# 71. File-Size Distribution

Instead of one average, inspect:

```text
p50
p90
p95
p99
```

Conceptual distribution:

```text
Most files: 5–20 MB
Some files: 300 MB
Few files: 2 GB
```

A policy may therefore define:

```text
lower bound
preferred range
upper bound
```

This is more expressive than one target number.

---

# 72. Monitoring Dashboard Concept

A useful operational view is:

| Partition | File Count | p50 | p95 | p99 | Total Size | Health |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `...` |  |  |  |  |  |  |
| `...` |  |  |  |  |  |  |

Use the dashboard to support:

- alerting;
- compaction scheduling;
- operational review;
- trend analysis.

Do not create a dashboard artifact for this lesson. The table is the conceptual design only.

---

# 73. Compaction Observability

A production compactor should record at least:

- partition;
- input file count;
- input bytes;
- output file count;
- output bytes;
- compaction duration;
- rows processed;
- sort performed or not;
- validation status;
- publication status;
- failure reason.

A structured event might look like:

```text
run_id: ...
partition: ...
input_files: ...
input_bytes: ...
output_files: ...
output_bytes: ...
rows: ...
sort: true/false
duration_seconds: ...
validation: PASS/FAIL
publish: PASS/FAIL
failure_reason: ...
```

This turns compaction from a mysterious background script into an observable production subsystem.

---

# 74. Failed Compaction

Desired behavior:

```text
Compaction
    ↓
Validation fails
    ↓
DO NOT publish
    ↓
Old data remains intact
    ↓
Quarantine / clean temp output
    ↓
Record failure
```

A failure should be visible to operators and retryable without duplicating data.

---

# 75. Retry Behavior

A failed compaction should ideally be retryable.

Use:

- unique temporary run identifiers;
- deterministic or well-defined input selection;
- validation on every attempt;
- old valid state retained until publication succeeds.

Do not claim that a retry can always resume from the exact byte where a previous compaction stopped. A safer default is often to restart from a clean, validated input set.

---

# 76. Compaction Test Plan

## Correctness

The logical rows and values must remain unchanged.

## Row count

```text
input rows = output rows
```

unless the compaction operation intentionally applies a documented transformation, which a pure compaction should not.

## Schema

Input and output schema must be compatible.

## Idempotency

Running twice must not duplicate logical data.

## Crash behavior

Partial temp output must not corrupt the last valid state.

## Unaffected partitions

Partitions outside the selected compaction set remain unchanged.

## File health

Output should meet the configured target range as closely as practical.

## Sorting

If sorting is required, verify the specified sort order.

---

# 77. Required Hands-On Lab — `compactor.py`

The roadmap requires a hands-on script named `compactor.py`, but the file-safety rule for this learning artifact prohibits physically creating that script.

Therefore, **the complete lab implementation belongs in this Markdown file only**.

## Part 1 — Streaming writer simulation

Create many small Parquet files under:

```text
year/month/day
```

Start with dozens, then scale to hundreds or thousands while testing. For the full conceptual exercise, the one-file-per-minute/month model gives 43,200 files.

## Part 2 — File-health report

Implement:

```python
file_health_report(root)
```

Report:

- file count;
- total size;
- p50;
- p95;
- p99;
- health status.

## Part 3 — Compaction

Implement:

```python
compact_partition(path, target_bytes)
```

using `pyarrow.dataset`.

## Part 4 — Sorting

Add an optional sort key driven by a real query pattern.

## Part 5 — Temporary prefix

Write new files to an isolated temporary location.

## Part 6 — Publication

Use an appropriate best-effort local method for the lab and explicitly document why it is not a universal object-store transaction protocol.

## Part 7 — Cleanup

Delete/expire old data only after successful publication and according to reader-safety assumptions.

## Part 8 — Tests

Prove:

- same rows;
- same values;
- idempotency;
- crash safety assumptions;
- reader-safety assumptions.

## Part 9 — Benchmark

Measure:

- query time;
- file count;
- size distribution;
- object-store request behavior on MinIO where measurable.

---

# 78. File-Health CLI / Tool Design

A production platform could expose conceptual commands such as:

```text
file-health-report
compact --partition year=2026/month=09/day=28
dry-run
```

A dry-run command should show what would happen without changing the dataset.

Do not create CLI files as part of this module.

---

# 79. Dry-Run Compaction

A dry run should report:

- eligible files;
- input file count;
- input bytes;
- estimated output file count;
- target range;
- estimated work;
- conflicting jobs if known.

Example:

```text
DRY RUN
Partition: year=2026/month=09/day=28
Eligible files: ...
Input bytes: ...
Estimated output files: ...
Target range: ...
Estimated read/write work: ...
Action: COMPACT / WAIT / SKIP
```

A dry run is a safety mechanism because it lets operators inspect the plan before mutating data.

---

# 80. Compaction Eligibility

Example policy:

```text
eligible if:
file size < minimum threshold

AND

partition health requires compaction

AND

no conflicting writer/compaction exists
```

Keep actual thresholds configurable.

A more mature policy can also require:

- minimum aggregate eligible bytes;
- minimum file count;
- maximum resource budget;
- positive expected savings estimate.

---

# 81. Cost-Aware Compaction

Use this as a conceptual prioritization model:

```text
Priority
≈
Health Severity
×
Query Importance
×
Expected Savings
÷
Compaction Cost
```

This is **not** a required exact production formula.

It is a way to make the trade-offs visible.

For example, a partition with severe fragmentation and very high query frequency should be examined before a rarely queried historical partition with the same file count.

---

# 82. Connection to Future Topics

The roadmap intentionally keeps this chapter focused.

Later topics cover:

- **Module 2.15** — lakehouse table formats and stronger commit/compaction mechanisms;
- **Module 2.20** — deeper file-health/observability architecture;
- **Module 2.21** — deeper performance, scaling, and cost optimization.

Use those later modules for deeper mechanisms instead of duplicating them here.

---

# 83. Stop-and-Think Exercises

## Exercise A — 5,000 tiny files

A partition contains:

```text
5,000 files
average size = 8 MB
```

What operational problems might this create?

### Reasoning guide

Discuss:

- high file count;
- metadata/discovery work;
- object operations;
- execution fragmentation;
- possible compression inefficiency.

Do not claim a specific runtime penalty without measurement.

## Exercise B — Healthy p50, bad p99

A partition has:

```text
p50 = 300 MB
p95 = 320 MB
p99 = 2.5 GB
```

Is the average or p50 enough to understand file health?

Discuss the upper tail and whether the 2.5 GB files create a separate operational concern.

## Exercise C — Ten 1 GB files

```text
10 files × 1 GB
```

Could this still be problematic?

Discuss useful read parallelism, concurrent queries, and rewrite size.

## Exercise D — Rows do not equal bytes

Why does:

```text
max_rows_per_file = 1,000,000
```

not guarantee a 256 MB file?

Discuss row width, encoding, compression, nulls, and nested fields.

## Exercise E — Crash after write

Compaction writes replacement files, then crashes before old files are removed.

What should happen?

Desired reasoning: the old valid state should remain available; new files should have been published only after validation; abandoned temp output should be detectable.

## Exercise F — Reader is already scanning

Why can deleting old files immediately be risky?

Discuss reader lifetime and storage-object availability.

## Exercise G — Rarely queried history

A partition is queried once per year and has 500 tiny files.

Should it automatically be compacted immediately?

Discuss query value versus compaction cost.

---

# 84. Interview Questions

## Basic

### What is the small-files problem?

**Model answer:** It is a state where a dataset is fragmented into many files whose per-file management and I/O overhead becomes significant relative to their useful payload, hurting operational efficiency.

### Why do many small files hurt?

**Model answer:** They can increase file-open, metadata, listing, object-request, compression, and execution-coordination overhead. The exact impact depends on engine and storage.

### What is target file size?

**Model answer:** A workload-specific physical file-size range intended to balance file-management overhead, parallelism, compression, memory use, and rewrite cost.

### What is compaction?

**Model answer:** A read/rewrite operation that combines many small files into fewer, better-sized files and optionally reorganizes the data.

## Intermediate

### What are the major costs of small files?

Explain the six costs from this module.

### Why do micro-batches create small files?

Each trigger may produce a small output independently, so file count grows with trigger frequency.

### Why does over-partitioning create small files?

It distributes a fixed data volume across too many partition values, reducing data per partition.

### Why is 128 MB–1 GB not a universal rule?

Because row width, workload, engine, object store, query concurrency, partition volume, and rewrite patterns vary.

### Why are percentiles useful?

They reveal distribution tails that a single average can hide.

## Advanced

### Why can oversized files also be problematic?

They can reduce parallelism, create large rewrite units, increase writer memory requirements, and make failures/retries more expensive.

### How do you prevent small files at write time?

Control rows per file, manage writer parallelism, and batch inputs.

### Why is row count not a reliable byte-size target?

Physical size depends on row width, encoding, compression, nested data, and data distributions.

### What happens during compaction?

Files are selected, read, optionally sorted, rewritten to temporary output, validated, published, and old files are cleaned up only after safety conditions are met.

### Why write to a temporary location?

To isolate partial output from normal readers and keep the last valid dataset state intact if the job fails.

### What does idempotent compaction mean?

Repeated execution does not multiply logical data or continually degrade the layout.

## Senior / Architecture

### How would you design file-health monitoring?

Measure file counts and size distributions by partition, calculate p50/p95/p99 and out-of-range fractions, record trends, and turn policy violations into a prioritized compaction queue.

### How would you prioritize partitions?

Use health severity, query importance, expected future savings, compaction cost, freshness, and resource availability.

### How would you make compaction safe under concurrent readers?

Keep new output isolated, validate it, publish through a clearly defined version/manifest/commit mechanism, and delay removal of old files until the reader-safety policy allows it.

### How would you handle concurrent writers?

Coordinate compaction with writers through scheduling/leases/locks or use a transaction-aware table format; do not assume directory operations alone provide isolation.

### How would you measure compaction ROI?

Compare the cost of rewriting data with measured future query savings and operational savings under realistic workload frequency.

### When would you not compact?

When the partition is healthy, rarely queried, too small to benefit materially, actively being rewritten, or too expensive to maintain under the current resource budget.

### Why do lakehouse table formats help with compaction?

They add a metadata/transaction layer that can represent table versions and coordinate publication more reliably than a raw directory of files.

### How would you design a target-file-size policy for a multi-team data platform?

Start with a documented baseline range, define exceptions, measure workload outcomes, keep thresholds configurable, and require teams to justify deviations with evidence.

---

# 85. Practical Scenarios

## Scenario 1 — Streaming Explosion

A streaming pipeline creates one Parquet file every minute.

Discuss:

- monthly file count;
- partition growth;
- causes;
- prevention vs compaction.

## Scenario 2 — High-Cardinality Partitioning

Partitioning by customer ID creates millions of tiny files.

Connect the problem to Topic 08 and propose alternative physical organization such as a coarser partition plus sorting/clustering where the workload supports it.

## Scenario 3 — Healthy Average, Bad Tail

Average size is acceptable, but p95/p99 reveals many tiny files.

Discuss why distribution-aware health metrics are needed.

## Scenario 4 — Giant File

One partition contains a 10 GB file.

Discuss whether the file should be split based on workload rather than a hard rule.

## Scenario 5 — Concurrent Compaction

Readers and writers remain active while compaction runs.

Discuss publication boundaries and why raw directories do not automatically provide transactional isolation.

## Scenario 6 — Low-Value Historical Partition

A partition is rarely queried.

Discuss whether the future savings justify the immediate rewrite cost.

---

# 86. Production Code Review Exercise

## Flawed pattern

```python
# delete old files
# then write compacted files
```

### Failure mode

A crash between deletion and successful output leaves the dataset incomplete or unavailable.

## Safer conceptual pattern

```text
write temp
    ↓
validate
    ↓
publish
    ↓
delete old later
```

This is safer because the valid old state remains available until replacement output has been validated.

## Another flawed pattern

```python
for small_file in files:
    compact(small_file)
```

This defeats the purpose because each input file is compacted independently. The compactor needs to **combine a set of eligible files into fewer larger files**.

---

# 87. Compaction Policy Decision Tree

```text
Is the partition unhealthy?
        │
       No
        ↓
      Skip

       Yes
        ↓
Is it frequently queried / operationally important?
        │
       No
        ↓
Evaluate cost before compacting

       Yes
        ↓
Are enough files eligible?
        │
       No
        ↓
      Wait

       Yes
        ↓
Estimate compaction cost
        ↓
Estimate future savings
        ↓
Check writer / compaction conflicts
        ↓
Compact
        ↓
Validate
        ↓
Publish safely
        ↓
Cleanup after reader-safe period
```

---

# 88. Production File-Layout Decision Model

Use this mental model:

```text
Desired File Layout
=
Dataset Size
+
Partition Volume
+
Query Parallelism
+
Storage Behavior
+
Writer Pattern
+
Compression
+
Rewrite Frequency
+
Reader Concurrency
+
Operational Cost
```

These are not arithmetic terms. They are the dimensions of the decision.

A file target that is reasonable in one environment can be poor in another because one or more of these dimensions changed.

---

# 89. Target File Size Decision Framework

Ask these questions before standardizing a target:

1. How much data enters each partition?
2. How many files are generated per batch?
3. How frequently are the partitions queried?
4. Which engine reads the data?
5. What level of parallelism is useful?
6. What is the average row width?
7. Which codec and compression level are used?
8. What is the file-size distribution today?
9. How often is the data rewritten?
10. What does the benchmark evidence show?

Then choose a **target range**, not a magic number.

---

# 90. Final File Health Standard

Ready-to-adapt policy template:

```text
Dataset:
Partition scheme:
Preferred file-size range:
Minimum acceptable size:
Maximum preferred size:
Health metrics:
Compaction trigger:
Compaction priority:
Sort policy:
Writer batching:
Writer parallelism:
Concurrency policy:
Temporary-output strategy:
Validation:
Cleanup policy:
Monitoring:
Alert thresholds:
Owner:
Review cadence:
```

Do not insert universal numeric thresholds. The roadmap's approximate 128 MB–1 GB range is the only numeric baseline here, and it remains a starting hypothesis.

---

# 91. Final Learning Checkpoint

You should now be able to:

- explain four costs of small files;
- choose a target file size for a dataset and justify it;
- compact a partition safely and idempotently;
- explain why compaction on plain files is risky under concurrent readers;
- explain why small files occur;
- explain the opposite problem of oversized files;
- explain the 128 MB–1 GB practical range as a guideline, not a law;
- build a file-health report;
- calculate percentiles;
- identify unhealthy partitions;
- prevent small files at write time;
- use `max_rows_per_file`;
- reason about writer parallelism;
- batch micro-batches;
- compact with `pyarrow.dataset`;
- use temporary output;
- validate before publication;
- test idempotency;
- test crash behavior;
- reason about concurrent readers/writers;
- measure before/after query performance;
- measure object-storage request behavior where available;
- design compaction scheduling;
- write a file-size policy.

---

# 92. Final Master Mental Model

```text
                 DATASET
                    │
                    ↓
                PARTITIONS
                    │
                    ↓
                  FILES
                    │
             ┌──────┴──────┐
             ↓             ↓
         Too Small      Too Large
             │             │
             ↓             ↓
       Too Much Cost    Too Little
        per File        Parallelism
             │             │
             └──────┬──────┘
                    ↓
              HEALTHY RANGE
                    │
                    ↓
             MONITOR HEALTH
                    │
            ┌───────┴────────┐
            ↓                ↓
         Healthy          Unhealthy
            │                │
           Skip          Evaluate Cost
                             │
                             ↓
                         COMPACTION
                             │
                    ┌────────┴────────┐
                    ↓                 ↓
                TEMP OUTPUT        VALIDATE
                    │                 │
                    └────────┬────────┘
                             ↓
                          PUBLISH
                             ↓
                       SAFE CLEANUP
                             ↓
                         MONITOR
```

And the compact summary:

```text
Good File Layout
=
Healthy File Count
+
Healthy Size Distribution
+
Useful Parallelism
+
Low Metadata Overhead
+
Reasonable Object Requests
+
Good Compression
+
Safe Operations
```

---

# 93. Final "Remember This"

1. **Small files create overhead even when the total logical data volume is unchanged.**
2. **File count matters in addition to total bytes.**
3. **The major costs include file open/read work, footer/metadata work, listing overhead, object-storage requests, poor compression, and excessive distributed tasks.**
4. **Micro-batches, streaming writes, over-partitioning, parallel writers, and tiny deltas are common causes.**
5. **Approximately 128 MB–1 GB is a useful analytical Parquet starting range from the roadmap, not a universal law.**
6. **Files that are too large create a different set of problems.**
7. **Rows per file are only an indirect proxy for bytes per file.**
8. **Percentiles reveal file-health problems that averages can hide.**
9. **Compaction is a read → rewrite → validate → publish operation and therefore has a cost.**
10. **Write compacted output to a temporary location before publishing it.**
11. **Never delete the old data before the replacement has been validated and safely published.**
12. **Compaction should be idempotent.**
13. **Concurrent readers and writers make plain-directory compaction difficult to make transactional.**
14. **Do not compact every partition automatically; prioritize based on health, workload value, and cost.**
15. **Measure file count, size distribution, query performance, and object-storage behavior before and after compaction.**
16. **The goal is not the fewest files. The goal is a healthy physical layout for the workload.**

---

# 94. Roadmap Common-Mistake Verification

Before considering the topic complete, verify that you can explain why the following are dangerous:

- compacting by deleting old files before new ones are committed;
- compacting everything every time;
- producing one gigantic file per partition regardless of volume;
- monitoring only the average file size;
- ignoring p95/p99;
- confusing row-count and byte-size targets;
- making compaction non-idempotent;
- ignoring concurrent-reader hazards;
- assuming object-store publication is equivalent to local filesystem rename;
- ignoring compaction cost;
- allowing a compactor and writer to race without coordination;
- leaving abandoned temporary output indefinitely.

---

# 95. Code Accuracy Rule

This is a production Data Engineering learning module.

All examples should:

- target Python 3.12+;
- use accurate PyArrow dataset APIs;
- use accurate PyArrow Parquet APIs;
- be runnable as educational examples;
- explain important lines;
- avoid fabricated output;
- avoid fabricated benchmark results;
- avoid hard-coded credentials;
- use deterministic synthetic data where appropriate.

The examples in this module were checked against current Apache Arrow Python API documentation for the dataset writer/scanner patterns used here. PyArrow's `write_dataset` exposes row/file controls including `max_rows_per_file`, `min_rows_per_group`, `max_rows_per_group`, `max_open_files`, and output handling parameters; the exact behavior should still be verified against the version pinned by the learner's project. citeturn169376search0

When behavior is version-sensitive:

1. verify the official documentation;
2. state the project version assumption;
3. do not invent parameters;
4. distinguish educational code from production guarantees.

---

# 96. Object-Storage Accuracy Rule

Do not claim:

- all object stores have identical request costs;
- all object stores have identical listing behavior;
- all object stores implement rename the same way;
- all object stores provide the same consistency/isolation guarantees.

Use this rule:

> **Object-storage semantics and costs vary by implementation, but large object counts commonly increase metadata, listing, and request overhead.**

MinIO is used here as the roadmap's S3-compatible experimental environment. Results from MinIO should not automatically be generalized to every cloud object store.

---

# 97. Benchmark Integrity Rule

Never fabricate:

- query runtimes;
- file counts;
- object request counts;
- file-size distributions;
- compression improvements;
- CPU savings;
- storage savings.

All such values must be measured by the learner's experiment.

Use measurement templates and record the exact environment:

```text
Engine:
Version:
Machine:
Storage:
Dataset:
Codec:
Query:
Cache condition:
Concurrency:
Date:
```

---

# 98. Fair Compaction Experiment

For the primary before/after experiment, keep constant:

- dataset;
- query;
- engine;
- schema;
- codec;
- storage;
- hardware;
- query parameters.

Change only:

> **file layout / compaction state**

Then separately evaluate:

> **compaction + sorting**

when sorting itself is an experimental variable.

A clean experiment isolates causes before combining optimizations.

---

# 99. Depth Boundary

This module owns:

- small-files problem;
- file count;
- file size;
- file-size distributions;
- percentiles;
- causes;
- prevention;
- target sizing;
- oversized-file trade-offs;
- compaction;
- safe publication;
- idempotency;
- concurrency risks;
- file-health monitoring;
- scheduling;
- compaction ROI;
- MinIO before/after experiment.

It does not re-teach in depth:

### Topic 08

Detailed partitioning design.

### Topic 07

Detailed codec analysis.

### Topic 02

Deep Parquet internals.

### Later lakehouse-table-format module

Deep transaction and table-format mechanisms.

### Module 2.20

Full observability architecture.

### Module 2.21

Deep performance/scaling/cost optimization.

Reference those topics where relevant, but keep this chapter centered on **file health and compaction**.

---

# 100. Final Self-Review

## Fundamentals

- [x] definition of small files;
- [x] contextual nature of "small";
- [x] file count;
- [x] total bytes;
- [x] file open/read overhead;
- [x] footer metadata overhead;
- [x] listing overhead;
- [x] object-storage requests;
- [x] poor compression;
- [x] distributed task overhead.

## Causes

- [x] micro-batches;
- [x] streaming;
- [x] over-partitioning;
- [x] parallel writers;
- [x] tiny deltas.

## File sizing

- [x] 128 MB–1 GB practical range;
- [x] range is not universal;
- [x] parallelism trade-off;
- [x] oversized files;
- [x] rows vs bytes;
- [x] workload/environment dependence.

## Prevention

- [x] `max_rows_per_file`;
- [x] writer parallelism;
- [x] batching;
- [x] partition interaction.

## File health

- [x] file count;
- [x] total bytes;
- [x] average;
- [x] median;
- [x] p90;
- [x] p95;
- [x] p99;
- [x] unhealthy thresholds;
- [x] monitoring.

## Compaction

- [x] definition;
- [x] read/rewrite;
- [x] target bytes;
- [x] `pyarrow.dataset`;
- [x] optional sorting;
- [x] temporary output;
- [x] validation;
- [x] publish/swap;
- [x] cleanup;
- [x] idempotency;
- [x] crash safety;
- [x] concurrent readers;
- [x] concurrent writers;
- [x] plain-directory limitations.

## Scheduling

- [x] recent partitions;
- [x] frequently queried partitions;
- [x] unhealthy partitions;
- [x] cost-aware scheduling;
- [x] configurable frequency.

## Required lab

- [x] one-file-per-minute simulation;
- [x] thousands of files;
- [x] `file_health_report`;
- [x] percentiles;
- [x] `compact_partition`;
- [x] `pyarrow.dataset`;
- [x] target bytes;
- [x] sorting;
- [x] temporary prefix;
- [x] safe publication;
- [x] idempotency test;
- [x] crash-safety exercise;
- [x] correctness test;
- [x] MinIO;
- [x] query before/after;
- [x] object-storage request measurement where available.

## Production

- [x] debugging;
- [x] common mistakes;
- [x] file-size policy;
- [x] compaction policy;
- [x] observability;
- [x] production case study;
- [x] architecture review;
- [x] interview questions;
- [x] practical scenarios;
- [x] checkpoint;
- [x] final decision framework.

## File Safety

The learning constraints for this artifact are:

- only `09-small-files-problem-and-target-file-sizing.md` is the intended output;
- no helper scripts are required to understand or execute the lab;
- no benchmark result files are generated here;
- no roadmap files are modified;
- no unfinished placeholders are required for core content.

---

# Practical Completion Challenge

Before moving to Topic 10, complete this sequence on your own dataset or a deterministic synthetic dataset:

```text
1. Generate / select a partitioned Parquet dataset.
2. Create a deliberately fragmented version.
3. Run file_health_report().
4. Record p50/p95/p99 and file count.
5. Pick a provisional target range.
6. Explain why that range is reasonable.
7. Compact one unhealthy partition.
8. Validate rows and schema.
9. Test a second compaction run.
10. Query before and after with the exact same query.
11. Measure runtime and bytes where available.
12. Run the MinIO experiment when available.
13. Document the result as a file-sizing policy.
14. Explain the decision aloud without saying "because 256 MB is the standard."
```

The final sentence is deliberate. The production skill is not knowing a number. The production skill is knowing **why your number is appropriate for this workload and what evidence would cause you to change it**.

---

# One-Page Architecture Summary

```text
                 INGESTION
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
      BATCH WRITE           STREAM WRITE
          │                     │
          ↓                     ↓
     HEALTHY OUTPUT       SMALL OUTPUTS
                                │
                                ↓
                         FILE-HEALTH SCAN
                                │
                     ┌──────────┴──────────┐
                     ↓                     ↓
                  HEALTHY              UNHEALTHY
                     │                     │
                    SKIP                   ↓
                                   COST / BENEFIT CHECK
                                             │
                                             ↓
                                         COMPACTION
                                             │
                     ┌───────────────────────┴─────────────────────┐
                     ↓                                             ↓
               TEMP OUTPUT                                     VALIDATION
                     │                                             │
                     └───────────────────────┬─────────────────────┘
                                             ↓
                                          PUBLISH
                                             ↓
                                      SAFE CLEANUP
                                             ↓
                                        MONITOR
```

The operational loop is:

> **Prevent what you can, measure what you produce, compact what is unhealthy, publish safely, and verify the workload improvement.**

That is the core data-engineering habit this topic is intended to build.
