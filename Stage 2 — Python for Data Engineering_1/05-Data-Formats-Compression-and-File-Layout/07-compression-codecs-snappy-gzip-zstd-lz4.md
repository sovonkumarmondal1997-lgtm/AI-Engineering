# Compression Codecs — Snappy, gzip, Zstandard, LZ4

> **Stage 2 → Python for Data Engineering → Module 2.5 — Data Formats, Compression, and File Layout → Phase D → Topic 07**

## Learning Objectives

By the end of this module, you should be able to:

- Explain why data compression exists in production data systems.
- Distinguish original size, compressed size, compression ratio, compression speed, and decompression speed.
- Explain storage, I/O, network, CPU, latency, and egress trade-offs.
- Explain the typical characteristics of Snappy, gzip/Deflate, Zstandard (zstd), and LZ4.
- Compare codecs without declaring a universal winner.
- Understand compression levels and diminishing returns.
- Distinguish encoding from compression.
- Explain splittability and why a gzip-compressed whole-file text stream behaves differently from internally compressed Parquet, ORC, or Avro.
- Explain why sorting can improve compression opportunities.
- Choose codecs using workload, data characteristics, access frequency, infrastructure, cost, and compatibility.
- Think about hot, warm, and cold data differently.
- Reason about per-column compression in columnar formats.
- Recognize data that is hard to compress because it is already compressed, encrypted, or highly random.
- Understand zstd trained dictionaries at an awareness level.
- Evaluate codec compatibility across readers and writers.
- Build a repeatable compression benchmark and interpret its results correctly.
- Model storage, compute, network, and egress cost.
- Explain codec choices in architecture reviews and production planning.

### The central principle

> **Compression is a systems trade-off between bytes stored or transferred and the CPU/time required to compress and decompress those bytes.**

There is no universally best codec.

The engineering question is:

> **Which codec and level produce an acceptable measured trade-off for this workload, this data distribution, this access pattern, this infrastructure, and these consumers?**

---

## Prerequisites

This topic assumes you have already completed:

- Topic 01 — Row-Oriented vs Columnar Storage
- Topic 02 — Parquet Internals
- Topic 03 — Reading/Writing Parquet with PyArrow
- Topic 04 — Avro
- Topic 05 — ORC and Format Selection
- Topic 06 — Nested/Semi-Structured Data

You should already understand:

- row-oriented vs columnar storage
- Parquet row groups, column chunks, and pages
- basic Parquet encodings and statistics
- Arrow/PyArrow
- Avro block-level compression
- file layout
- basic dataset and query concepts

This chapter does **not** re-teach those topics in full. It connects them to compression.

---

# 1. Why Compression Matters

Imagine a lake containing 100 TB of logical data.

That data is read, written, copied, queried, replicated, and sometimes transferred outside the region or cloud.

Without compression:

```text
100 TB logical data
      ↓
100 TB stored/transferred
```

With a measured compression ratio of 4:1:

```text
100 TB logical data
      ↓
25 TB compressed
```

That can reduce:

- bytes stored
- bytes read from storage
- bytes transferred over a network
- object-storage traffic
- egress volume

But compression is not free.

```text
More compression
      ↓
more algorithmic work
      ↓
more CPU/time
```

So a useful mental model is:

```text
Compression
    │
    ├── fewer bytes
    │      ├── lower storage
    │      ├── lower I/O
    │      └── lower transfer
    │
    └── more CPU work
           ├── compression CPU
           └── decompression CPU
```

The winning design is not necessarily the one with the smallest file.

The winning design is the one that fits the complete system.

---

## A small numerical example

Suppose:

```text
Uncompressed dataset = 1 TB
Compressed dataset   = 250 GB
```

Then:

```text
Compression ratio = 1 TB / 250 GB
                  = 4:1

Space savings = 1 - (250 GB / 1 TB)
              = 75%
```

The physical storage saving is meaningful.

But the query engine still needs to:

1. fetch compressed bytes,
2. decompress them,
3. decode them,
4. execute the query.

Therefore:

```text
Storage cost ↓
I/O volume ↓

but

CPU work ↑ or remains material
```

The actual runtime impact must be measured.

---

# 2. Compression in a Data Pipeline

A simplified analytical pipeline looks like this:

```text
Source Data
    ↓
Encoding / Data Representation
    ↓
Compression Codec
    ↓
Compressed Bytes
    ↓
Storage / Network
    ↓
Decompression
    ↓
Decoded Representation
    ↓
Query / Transformation
```

For a columnar format such as Parquet, a useful conceptual path is:

```text
Logical Values
      ↓
Parquet Encoding
      ↓
Compression Codec
      ↓
Compressed Page/Block Bytes
      ↓
Storage
```

For an Avro object container file, the physical organization is different, but the same systems principle applies:

```text
Records
   ↓
Avro binary encoding
   ↓
Block compression
   ↓
Compressed blocks
```

The important idea is:

> **The format determines how data is organized; the codec determines how the encoded representation is compressed.**

---

# 3. What Compression Actually Does

Compression is easiest to understand through redundancy.

Consider:

```text
AAAAAAAABBBBBBBBCCCCCCCC
```

A simple conceptual representation could describe runs rather than repeating every character.

Real codecs use much more sophisticated techniques, but the intuition is the same:

```text
Repeated / predictable patterns
            ↓
more compact representation
```

For lossless data compression:

```text
Original data
     ↓
Compress
     ↓
Compressed data
     ↓
Decompress
     ↓
Original data exactly recovered
```

### Lossless compression

Lossless compression preserves the original information exactly.

The codecs discussed in this chapter are used for lossless data compression in the data-engineering contexts covered here:

- Snappy
- gzip/Deflate
- Zstandard
- LZ4

Lossy compression is different. Images, audio, and video can sometimes intentionally discard information to reduce size. That is not the model we are using for analytical data files.

---

## What compression does not do

Compression does not automatically:

- make a format columnar,
- create useful query indexes,
- fix poor partitioning,
- fix too many files,
- make arbitrary predicates cheap,
- remove the need for schema design.

For example:

```text
Bad layout
    +
Excellent compression
```

can still produce poor query performance.

Compression solves one dimension of the physical-data problem.

---

# 4. Compression Ratio

A common metric is:

```text
Compression Ratio
=
Uncompressed Size / Compressed Size
```

Example:

```text
Uncompressed = 100 GB
Compressed   = 25 GB

Ratio = 100 / 25
      = 4:1
```

Another useful metric is space savings:

```text
Space Savings
=
1 - (Compressed Size / Uncompressed Size)
```

For the same example:

```text
1 - (25 / 100)
= 0.75
= 75%
```

### Do not confuse these two metrics

A ratio of:

```text
4:1
```

means the compressed representation is one quarter of the original size.

That corresponds to:

```text
75% space savings
```

---

## Why ratio is not enough

Suppose Codec A:

```text
100 GB → 20 GB
```

and Codec B:

```text
100 GB → 25 GB
```

Codec A produces a smaller file.

But suppose:

```text
Codec A
→ very high CPU cost

Codec B
→ modest CPU cost
```

For a hot dataset queried thousands of times a day, the smaller file may not automatically produce the lowest total cost or latency.

So always treat ratio as one measurement among several:

| Metric | Question |
| --- | --- |
| Compression ratio | How much does the data shrink? |
| Compression speed | How expensive is writing? |
| Decompression speed | How expensive is reading? |
| CPU utilization | How much compute is consumed? |
| Read latency | How quickly can the workload complete? |
| Storage cost | How much space is consumed over time? |
| Transfer cost | How much data crosses the network? |

---

# 5. Compression Speed

**Compression speed** describes how quickly a codec converts input into compressed output.

Possible measurements include:

```text
GB/s
MB/s
seconds/GB
```

A writer may be constrained by:

```text
Input generation
     ↓
Transformation
     ↓
Compression
     ↓
Storage write
```

If compression becomes the slowest stage, the codec is on the critical path.

Compression throughput depends on:

- CPU model
- number of CPU cores
- data distribution
- input type
- compression level
- implementation
- memory behavior
- parallelism
- library version
- operating-system environment

Therefore a benchmark number without an environment is incomplete.

---

# 6. Decompression Speed

**Decompression speed** describes how quickly compressed bytes are restored into a representation the reader can decode and query.

This matters especially when:

- the same data is queried frequently,
- scans are large,
- storage is fast,
- the workload is CPU-bound,
- interactive latency matters.

A hot dataset can execute this path repeatedly:

```text
Storage
  ↓
Read compressed bytes
  ↓
Decompress
  ↓
Decode
  ↓
Execute
```

If decompression consumes a large share of CPU, a codec with a more favorable decompression cost may be economically attractive even if another codec produces smaller files.

Again, measure the actual workload.

---

# 7. Storage, Network, I/O, and CPU Trade-offs

The central trade-off can be visualized as:

```text
Less Compression
      ↓
More Bytes
      ↓
More I/O
      ↓
Potentially Less Compression CPU

More Compression
      ↓
Fewer Bytes
      ↓
Less I/O
      ↓
Potentially More CPU
```

The actual outcome depends on the infrastructure.

### Fast local storage

If storage bandwidth is high and CPU is constrained:

```text
I/O may be less painful
CPU may matter more
```

### Slow object-storage path

If reading from remote object storage is expensive:

```text
Fewer bytes transferred
may have a meaningful benefit
```

### High egress workload

If data frequently crosses a cloud boundary:

```text
Compressed bytes ↓
→ network transfer volume ↓
→ potentially lower egress cost
```

The decision therefore spans several layers:

```text
                 Codec
                   │
       ┌───────────┼───────────┐
       ↓           ↓           ↓
     Storage      Network      CPU
       │           │           │
       └───────────┼───────────┘
                   ↓
                 Cost
                   ↓
                Latency
```

---

# 8. Snappy

Snappy is a lossless compression codec designed with a strong emphasis on speed.

The useful engineering characterization is:

> **Snappy trades some compression density for fast processing.**

That makes it a candidate for workloads where:

- data is read frequently,
- low decompression overhead matters,
- CPU is valuable,
- moderate compression is sufficient,
- a format such as Parquet or ORC already provides structure around compressed units.

Do not interpret "speed-oriented" as:

> Snappy is always the fastest codec.

Performance depends on:

- implementation,
- CPU,
- data,
- reader,
- writer,
- workload.

### Conceptual trade-off

```text
Snappy
   ↓
speed-oriented processing
   +
moderate size reduction
   ↓
useful candidate for hot workloads
```

---

## Snappy in a Parquet pipeline

PyArrow can write Parquet with Snappy:

```python
import pyarrow as pa
import pyarrow.parquet as pq

table = pa.table({
    "country": ["IN", "US", "IN", "UK"],
    "amount": [100.0, 250.0, 180.0, 120.0],
})

pq.write_table(
    table,
    "orders.snappy.parquet",
    compression="snappy",
)
```

What changed?

```text
Arrow Table
    ↓
Parquet encoding
    ↓
Snappy compression
    ↓
Parquet file
```

The exact physical output depends on other writer settings too.

---

# 9. gzip / Deflate

gzip is a broadly interoperable compressed format built around the DEFLATE compression method.

In Parquet, the `GZIP` codec refers specifically to the gzip format used for pages, rather than treating a whole Parquet file as one gzip stream.

That distinction matters.

For a raw text file:

```text
orders.csv
    ↓
gzip
    ↓
orders.csv.gz
```

For Parquet:

```text
Parquet
    ↓
row groups
    ↓
column chunks
    ↓
pages
    ↓
GZIP-compressed page data
```

These are different physical designs.

gzip is often used where:

- broad compatibility is useful,
- stronger compression is valuable,
- CPU cost is acceptable,
- transfer or archival matters,
- legacy systems already expect gzip.

Do not claim gzip is universally better for archival data. That is a workload decision.

---

# 10. Zstandard (zstd)

Zstandard, commonly called **zstd**, is a modern lossless compression codec with tunable compression levels.

The useful systems mental model is:

```text
lower zstd level
      ↓
less compression effort
      ↓
typically lower CPU cost

higher zstd level
      ↓
more compression effort
      ↓
potentially smaller output
```

The relationship is not linear.

A higher level does not guarantee a proportionally smaller result.

The exact compression ratio and CPU cost depend on the data.

---

## zstd in Parquet

PyArrow supports zstd for Parquet writing:

```python
import pyarrow.parquet as pq

pq.write_table(
    table,
    "orders.zstd.parquet",
    compression="zstd",
)
```

A level can also be supplied where supported by the relevant API:

```python
pq.write_table(
    table,
    "orders.zstd-3.parquet",
    compression="zstd",
    compression_level=3,
)
```

Do not assume that a level is valid for every codec or every library version. Verify the target environment.

---

# 11. LZ4

LZ4 is strongly oriented toward fast compression and decompression.

The engineering idea is:

> **Use LZ4 when very low compression/decompression overhead is important and a somewhat larger representation may be an acceptable trade-off.**

Again, this is a workload characteristic, not a universal ranking.

LZ4 can be relevant for:

- low-latency pipelines,
- high-throughput processing,
- intermediate data,
- frequently accessed data where CPU overhead matters.

### Important Parquet naming detail

Modern Parquet distinguishes:

- historical `LZ4`
- `LZ4_RAW`

The Apache Parquet specification marks historical `LZ4` as deprecated and recommends interoperable `LZ4_RAW` for new writer APIs. PyArrow documents `lz4_raw` as an alias for the raw codec in supported environments. Verify the exact behavior of the installed version before standardizing on an API spelling.

---

# 12. Comparing the Main Codecs

Use this as a starting framework, not a ranking:

| Codec | Typical characteristic | Compression effort | Typical trade-off | Candidate workload |
| --- | --- | --- | --- | --- |
| Snappy | speed-oriented | relatively low | more bytes may remain | hot/interactivity-sensitive |
| gzip | stronger compression emphasis | higher | more CPU | transfer/archive-oriented cases |
| zstd | tunable range | configurable | adjustable size/CPU balance | broad workload range |
| LZ4 | strongly speed-oriented | low | often more bytes | low-latency/high-throughput cases |

### Additional Codec Awareness

The roadmap also names three further lossless codecs. Treat this as awareness of workload fit, not as a ranking:

| Codec | Ratio | Speed | Splittable | When to Use |
| --- | --- | --- | --- | --- |
| Brotli | high | slower to compress | not as a standalone compressed stream | cold/archival-style data where ratio matters more than maximum throughput |
| bzip2 | high | slow | yes, on its own, because the format is block-oriented | large batch files where splittability is useful |
| xz | very high | slow | not as a standalone compressed stream | cold/archival data; not a default for frequently read hot data |

bzip2 is splittable on its own because its format is block-oriented. Whether a reader actually exploits that depends on the reader and the deployment.

Brotli and xz suit cold data, where reads are rare and stored bytes dominate the cost. They are not universally better than gzip or zstd. Splittability depends on the container or reader, so verify it for your stack.

The word **typical** is important.

These are not guarantees.

A useful benchmark may overturn the expected result for a specific dataset.

---

# 13. Compression Levels

Some codecs expose a compression level.

Think:

```text
Level
  ↓
Algorithmic effort
  ↓
CPU time
  ↓
Compressed size
```

But the relationship is not perfectly linear.

For example, a benchmark might show:

```text
Level 1  → 30 GB
Level 3  → 27 GB
Level 9  → 25 GB
Level 19 → 24.5 GB
```

These values are **illustrative only**.

They are not benchmark results.

The engineering question is:

```text
Additional CPU cost
        vs
Additional storage/network savings
```

---

# 14. Diminishing Returns

Compression often has diminishing returns as algorithmic effort increases.

A conceptual curve is:

```text
Compressed
Size
 │
 │\
 │ \
 │  \
 │   \____
 │        \__
 └──────────────→ Compression effort
```

Early increases in effort can sometimes remove significant redundancy.

Later increases may produce small additional savings.

This matters because production jobs have finite CPU budgets.

For hot data:

```text
tiny storage gain
+
large CPU increase
```

may be an unattractive trade-off.

For cold data stored for years:

```text
small additional size reduction
×
very large retained volume
×
long retention period
```

may justify more compression effort.

Measure the real data.

---

# 15. Encoding vs Compression

This distinction is essential.

Use this conceptual pipeline:

```text
Logical Values
      ↓
Encoding
      ↓
Compression
      ↓
Compressed Bytes
```

### Encoding

Encoding changes the representation of values.

Examples:

- dictionary encoding
- run-length encoding (RLE)
- delta encoding
- byte-stream split

### Compression

Compression reduces the size of the encoded representation.

Examples:

- Snappy
- GZIP
- ZSTD
- LZ4

So:

> **Encoding changes representation; compression reduces the size of that representation.**

For a Parquet column:

```text
country values
    ↓
dictionary/RLE-style representation
    ↓
compression
    ↓
final page bytes
```

Sorting can improve both stages because it can make similar values closer together.

---

# 16. Splittability

**Splittability** means that a large data source can be divided into independently processable sections.

This matters because distributed systems prefer:

```text
Large input
   ↓
many logical pieces
   ↓
many workers
   ↓
parallel processing
```

Splittability is about the **organization of compressed data**, not simply whether compression exists.

---

## Uncompressed CSV

A large uncompressed CSV can generally be processed in chunks from different byte offsets, with care around record boundaries.

```text
CSV
├── bytes 0..N
├── bytes N..2N
└── bytes 2N..3N
```

A worker can start near an offset and seek to the next complete line.

---

## gzip-compressed CSV

A single gzip stream is not generally splittable in that straightforward way.

```text
CSV
   ↓
one gzip stream
   ↓
one compressed stream
```

Random workers cannot simply start decompressing at arbitrary byte offsets as though each offset were an independent gzip stream.

---

## Internally compressed analytical formats

Parquet, ORC, and Avro can organize compressed data inside higher-level physical units.

Examples:

```text
Parquet
→ row groups
→ column chunks
→ pages

ORC
→ stripes
→ internal streams

Avro
→ blocks
→ sync markers
```

Compression can therefore coexist with parallelism.

This is one reason:

> **"Compressed" does not mean "non-splittable."**

---

# 17. `.csv.gz` vs Compressed Parquet

Compare these two designs.

### `.csv.gz`

```text
CSV records
     ↓
gzip whole stream
     ↓
compressed file
```

Typical properties:

- simple
- portable
- human-readable before compression
- difficult to parallelize through arbitrary points in one gzip stream
- no native column pruning
- parsing is still required after decompression

### Compressed Parquet

```text
Rows
 ↓
row groups
 ↓
column chunks
 ↓
pages
 ↓
encoding
 ↓
compression
```

Typical properties:

- column-oriented
- supports projection of requested columns
- can use statistics for skipping where available and selective
- compressed internal units preserve file-structure-aware processing
- typed representation reduces the need for text parsing

Neither is "bad".

They solve different problems.

A partner may explicitly want:

```text
orders.csv.gz
```

That requirement can be perfectly legitimate even when the internal lake uses Parquet.

---

# 18. A Small Query Comparison

Suppose a dataset contains:

```text
20 columns
1 billion rows
```

and a query needs:

```text
2 columns
```

A columnar file may only need to read the relevant column chunks/pages for those columns, subject to the engine, format, and layout.

A raw row-oriented text representation often requires reading the records and parsing the record structure.

Now add compression:

```text
Column pruning
+
Encoding
+
Compression
```

can reduce the amount of data that needs to cross the storage boundary.

But do not assume:

> "2 columns means exactly 10% of bytes."

Different columns have different widths, encodings, compression, metadata, and execution costs.

---

# 19. Sorting and Compression

Sorting can improve compression opportunities because similar values become adjacent.

### Random order

```text
US
IN
CA
US
DE
IN
US
CA
```

### Sorted order

```text
CA
CA
DE
IN
IN
US
US
US
```

The sorted version has more local repetition.

That can help:

- dictionary-style representation,
- run-length encoding,
- general-purpose compression,
- statistics used for range filtering.

So:

```text
Sorting
   ↓
more local regularity
   ↓
potentially better encoding
   ↓
potentially better compression
```

But sorting has costs:

- CPU
- memory
- shuffle/merge work
- write complexity
- possible impact on other query patterns

Therefore sorting should also be treated as a measurable workload decision.

---

# 20. Data Characteristics That Affect Compression

Before benchmarking a codec, inspect the data.

Important characteristics include:

- cardinality
- repetition
- value distribution
- string length
- numeric distribution
- sortedness
- null frequency
- binary content
- existing compression
- randomness / high entropy

---

## Low-cardinality example

```text
country

IN
IN
US
IN
UK
IN
US
IN
```

Repeated values create opportunities for compact representation.

---

## High-cardinality example

```text
customer_id

b6c2...
1f91...
aa02...
7d18...
...
```

Unique or near-unique identifiers often provide fewer repeated patterns.

That does **not** mean every identifier is incompressible.

The exact result depends on the identifier structure and surrounding encoding.

---

## Long text

```text
description
```

Repeated vocabulary and patterns can provide useful redundancy.

The actual ratio must still be measured.

---

# 21. Choosing Codecs by Workload

Start with the workload, not the codec.

Ask:

1. How often is the data read?
2. How often is it written?
3. How much data is processed?
4. Is latency important?
5. Is CPU constrained?
6. Is storage expensive?
7. Is network transfer expensive?
8. Is egress significant?
9. Which consumers must read the data?
10. Which codecs do those consumers support?

Then shortlist candidates.

---

# 22. Hot, Warm, and Cold Data

A useful classification is:

### Hot

Read frequently.

### Warm

Read periodically.

### Cold

Rarely read.

This can affect which trade-off is attractive.

```text
Hot
 ↓
decompression/read behavior matters strongly

Warm
 ↓
balance storage and CPU

Cold
 ↓
storage and long-term transfer may matter more
```

This is a heuristic.

A cold dataset with severe operational CPU constraints can produce a different answer.

Likewise, a hot dataset may justify stronger compression if remote I/O dominates.

---

# 23. Streaming and Messaging Workloads

Compression decisions also occur in:

- event pipelines,
- messaging,
- ingestion,
- CDC transport.

For streaming data, consider:

- compression latency,
- decompression latency,
- CPU usage,
- payload size,
- message size limits,
- consumer compatibility.

For example:

```text
Application
   ↓
Event serialization
   ↓
Optional compression
   ↓
Message transport
   ↓
Consumer
```

The "best" codec for a message pipeline may be influenced more by end-to-end latency than by long-term storage ratio.

Connect this to the earlier Avro topic:

```text
Avro
+
block compression
```

can be useful when typed, compact record movement is required.

---

# 24. Per-Column Compression

Columnar formats allow physical behavior to vary by column.

Consider:

```text
country
status
description
random_uuid
image_bytes
```

These columns are not equally compressible.

### `country`

Low cardinality.

```text
IN
US
IN
IN
UK
...
```

### `description`

Long text.

### `random_uuid`

High uniqueness.

### `image_bytes`

May already be compressed.

The principle is:

> **Compression should be considered per column when the format and tooling allow it.**

This is a physical-layout decision, not just a file-level decision.

PyArrow documents per-column compression settings for Parquet writing:

```python
import pyarrow.parquet as pq

pq.write_table(
    table,
    "orders.parquet",
    compression={
        "country": "zstd",
        "description": "zstd",
    },
)
```

Only specify per-column settings that the target API actually supports.

---

# 25. Incompressible and Already-Compressed Data

Some data provides little additional redundancy.

Examples include:

- JPEG
- PNG
- compressed video
- compressed archives
- cryptographically random bytes
- some encrypted payloads

Conceptually:

```text
Already compressed
       ↓
little remaining redundancy
       ↓
limited additional size reduction
       ↓
compression CPU still consumed
```

Therefore:

> **Not every byte field deserves another round of general-purpose compression.**

In a Parquet dataset containing:

```text
description
image_bytes
country
```

the image bytes may dominate less-compressible content while the text/categorical columns behave differently.

Measure by column where possible.

---

# 26. Encrypted / High-Entropy Data

Encryption is designed to remove recognizable structure.

Therefore:

```text
Plaintext
   ↓
compress
   ↓
encrypt
```

can often expose more useful compression opportunities than:

```text
Plaintext
   ↓
encrypt
   ↓
attempt to compress ciphertext
```

The second path normally encounters ciphertext that is intentionally difficult to compress.

This chapter is not a cryptography course. The engineering lesson is simply:

> **Compression generally benefits from redundancy; encryption intentionally obscures redundancy.**

---

# 27. Zstandard Trained Dictionaries

Zstd supports trained dictionaries for workloads containing many small, structurally similar payloads.

The basic idea:

```text
Many similar small messages
          ↓
Learn common patterns
          ↓
Build dictionary
          ↓
Compress each message using dictionary
```

Potential use cases include:

- repeated JSON payloads,
- event records with stable structure,
- API responses,
- small documents.

Potential costs include:

- dictionary training,
- dictionary lifecycle management,
- versioning,
- distributing dictionaries,
- compatibility between producers and consumers.

This is an awareness topic.

Do not adopt trained dictionaries merely because they exist.

---

# 28. Codec Compatibility

A codec is useful only if the required consumers can read it.

Think:

```text
Producer
    ↓
Format + Codec
    ↓
Storage
    ↓
Consumer
```

The consumer must support both:

```text
file format
+
codec
```

Compatibility can vary by:

- engine,
- library,
- version,
- deployment packaging,
- file-format feature set.

Typical systems to test include:

- PyArrow
- DuckDB
- Polars
- Spark
- Trino

Do not assume every release supports exactly the same codec set.

The Apache Parquet implementation-status page currently shows broad support for Snappy, GZIP, ZSTD, and LZ4_RAW across several implementations, while historical LZ4 is deprecated. Always test the versions you actually deploy.

---

# 29. Cost Modeling

A practical monthly model is:

```text
Monthly Total Cost
=
Storage Cost
+
Compute Cost
+
Network / Transfer Cost
+
Egress Cost
```

The point is not to produce an exact cloud bill in this chapter.

The point is to understand the variables.

---

## Basic storage model

Let:

```text
R = raw size
C = compression ratio
P = storage price per GB-month
```

Then:

```text
Compressed size = R / C

Monthly storage cost
= (R / C) × P
```

Suppose:

```text
R = 10 TB
C = 4
```

Then:

```text
Compressed size = 2.5 TB
```

If the storage price is represented as:

```text
P_storage
```

then:

```text
monthly storage
= 2.5 TB × P_storage
```

Do not insert live provider pricing unless you are explicitly doing current pricing research.

---

# 30. Add Compute Cost

Compression can change CPU usage.

A simplified model is:

```text
Total Cost
=
Storage
+
Compression CPU
+
Decompression CPU
+
Network
+
Egress
```

For example:

```text
Codec A
→ smaller files
→ higher compression CPU

Codec B
→ larger files
→ lower compression CPU
```

If data is written once and read thousands of times, decompression can dominate the trade-off.

If data is written continually but rarely read, compression CPU on the write path may matter more.

This is why workload classification comes first.

---

# 31. A More Complete Cost Model

Define:

```text
S = compressed storage volume

W = number of writes

R = number of reads

B_read = bytes read

CPU_compress = total compression CPU

CPU_decompress = total decompression CPU

N = network transfer bytes

E = egress bytes
```

Then reason conceptually:

```text
Monthly Cost
=
f(S)
+
f(CPU_compress)
+
f(CPU_decompress)
+
f(N)
+
f(E)
```

The exact functions depend on your infrastructure.

The important point is that:

> **Storage is only one part of the economics.**

---

# 32. Storage Cost Model Exercise

Fill out a scenario like:

```text
Raw size          = 10 TB
Codec A ratio     = measured_A
Codec B ratio     = measured_B
Storage price     = chosen assumption
Monthly reads     = measured workload
CPU price         = chosen assumption
Egress volume     = measured workload
```

Then compare:

```text
Codec A total cost estimate
vs
Codec B total cost estimate
```

Document assumptions explicitly.

The result should be a model, not a false claim about a universal cheapest codec.

---

# 33. Required Codec Benchmark

The roadmap requires an exercise named:

```text
codec_benchmark.py
```

Because the file-safety rule forbids creating additional files, the complete implementation is shown **inside this Markdown file only**.

The learner should create the script locally when performing the exercise.

The benchmark must use the same orders dataset and compare:

- no compression
- Snappy
- gzip
- LZ4
- zstd level 1
- zstd level 3
- zstd level 9
- zstd level 19

Record:

- file size
- write time
- full-read time
- one-column-read time

Run every measurement at least three times.

---

## Benchmark implementation

```python
from __future__ import annotations

import statistics
import time
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


OUTPUT_DIR = Path("benchmark_output")
OUTPUT_DIR.mkdir(exist_ok=True)

ROWS = 1_000_000
SEED = 42


def build_orders(num_rows: int = ROWS) -> pa.Table:
    """Create a deterministic synthetic orders table."""
    order_ids = list(range(1, num_rows + 1))

    countries = ["IN", "US", "GB", "DE", "SG"]
    statuses = ["PENDING", "PAID", "CANCELLED"]

    country_values = [
        countries[(i * 17 + SEED) % len(countries)]
        for i in range(num_rows)
    ]
    status_values = [
        statuses[(i * 7 + SEED) % len(statuses)]
        for i in range(num_rows)
    ]

    amount_values = [
        float((i * 37) % 100_000) / 100.0
        for i in range(num_rows)
    ]

    created_at_values = [
        f"2025-01-{(i % 28) + 1:02d}"
        for i in range(num_rows)
    ]

    return pa.table(
        {
            "order_id": pa.array(order_ids, type=pa.int64()),
            "country": pa.array(country_values, type=pa.string()),
            "status": pa.array(status_values, type=pa.string()),
            "amount": pa.array(amount_values, type=pa.float64()),
            "created_at": pa.array(created_at_values, type=pa.string()),
        }
    )


def write_once(
    table: pa.Table,
    path: Path,
    compression: str | None,
    compression_level: int | None = None,
) -> float:
    """Write Parquet once and return elapsed seconds."""
    kwargs = {
        "compression": compression,
    }

    if compression_level is not None:
        kwargs["compression_level"] = compression_level

    start = time.perf_counter()

    pq.write_table(
        table,
        path,
        **kwargs,
    )

    return time.perf_counter() - start


def read_full_once(path: Path) -> float:
    """Read all columns once and return elapsed seconds."""
    start = time.perf_counter()
    pq.read_table(path)
    return time.perf_counter() - start


def read_one_column_once(path: Path, column: str = "amount") -> float:
    """Read one column once and return elapsed seconds."""
    start = time.perf_counter()
    pq.read_table(path, columns=[column])
    return time.perf_counter() - start


def median_of_runs(values: list[float]) -> float:
    return statistics.median(values)


def benchmark_case(
    table: pa.Table,
    name: str,
    compression: str | None,
    compression_level: int | None = None,
    repetitions: int = 3,
) -> dict[str, float | str | int | None]:
    path = OUTPUT_DIR / f"{name}.parquet"

    write_times: list[float] = []
    full_read_times: list[float] = []
    one_column_times: list[float] = []

    for _ in range(repetitions):
        if path.exists():
            path.unlink()

        write_times.append(
            write_once(
                table,
                path,
                compression,
                compression_level,
            )
        )

        full_read_times.append(read_full_once(path))
        one_column_times.append(read_one_column_once(path))

    size_bytes = path.stat().st_size

    return {
        "codec": name,
        "level": compression_level,
        "file_size_bytes": size_bytes,
        "write_median_seconds": median_of_runs(write_times),
        "full_read_median_seconds": median_of_runs(full_read_times),
        "one_column_median_seconds": median_of_runs(one_column_times),
    }


def main() -> None:
    table = build_orders()

    cases = [
        ("none", None, None),
        ("snappy", "snappy", None),
        ("gzip", "gzip", None),
        ("lz4", "lz4_raw", None),
        ("zstd_1", "zstd", 1),
        ("zstd_3", "zstd", 3),
        ("zstd_9", "zstd", 9),
        ("zstd_19", "zstd", 19),
    ]

    results = [
        benchmark_case(
            table,
            name,
            compression,
            level,
            repetitions=3,
        )
        for name, compression, level in cases
    ]

    columns = [
        "codec",
        "level",
        "file_size_bytes",
        "write_median_seconds",
        "full_read_median_seconds",
        "one_column_median_seconds",
    ]

    print("\t".join(columns))

    for row in results:
        print(
            "\t".join(
                str(row[column])
                for column in columns
            )
        )


if __name__ == "__main__":
    main()
```

### Important benchmark notes

The code intentionally does **not** contain hard-coded benchmark results.

Run it on your own environment and record the observed values.

The example uses `lz4_raw` rather than treating historical Parquet `LZ4` and interoperable `LZ4_RAW` as interchangeable names. Check the installed PyArrow release if your environment differs.

The benchmark is intentionally simple. It is not a full performance harness.

---

# 34. Benchmark Measurement Table

Create a results table:

| Codec | Level | File Size | Write Time | Full Read | One-Column Read |
| --- | --- | ---: | ---: | ---: | ---: |
| none | — | | | | |
| snappy | — | | | | |
| gzip | actual/default | | | | |
| lz4_raw | — | | | | |
| zstd | 1 | | | | |
| zstd | 3 | | | | |
| zstd | 9 | | | | |
| zstd | 19 | | | | |

Populate this from measurement.

Do **not** populate it with invented numbers.

---

# 35. Three-Run Measurement Rule

Each important measurement should be repeated.

At minimum:

```text
run 1
run 2
run 3
```

Useful summary statistics include:

- minimum
- median
- mean

For performance engineering, median is often a useful first summary because it is less sensitive to one unusually slow run than the mean.

But always retain the underlying measurements.

Why do timings vary?

- filesystem cache
- object-store state
- CPU scheduling
- background processes
- thermal behavior
- garbage collection in some runtimes
- query warm-up
- dataset generation effects

One timing is rarely enough to standardize a production codec policy.

---

# 36. Cold vs Warm Cache

A codec can look different under different cache states.

### Cold-ish read

The relevant data is not already resident in the useful cache.

```text
Storage / network
      ↓
major source of latency
```

### Warm read

Some data may already be cached.

```text
CPU / decompression
      ↓
may become a larger share of work
```

Conceptually:

```text
Cold-ish
→ I/O effects may dominate

Warm
→ CPU/decompression effects may become more visible
```

Do not claim this behavior is guaranteed.

The correct approach is to record cache state and interpret the benchmark accordingly.

---

# 37. Fair Compression Benchmarking

A fair codec experiment changes one important variable at a time.

Keep constant:

- logical dataset
- schema
- row count
- data-generation seed
- file format
- row-group settings
- page settings
- writer implementation
- machine
- storage environment
- query
- measurement procedure

Change:

- codec
- compression level, when level is the experiment variable

The core rule is:

> **Change one knob at a time.**

Bad experiment:

```text
Codec changes
+
Row-group size changes
+
Sort order changes
+
Dictionary setting changes
```

You cannot confidently attribute the result.

Good experiment:

```text
same everything
+
only codec changes
```

---

# 38. Compression Benchmark vs End-to-End Query Benchmark

A **codec benchmark** isolates compression behavior more directly.

An **end-to-end query benchmark** includes many additional variables:

```text
Observed Query Runtime
=
Format Effects
+
Codec Effects
+
Engine Effects
+
Query Plan
+
I/O
+
Cache
+
CPU
+
Dataset Layout
```

For example:

```text
DuckDB + Parquet + zstd
```

does not tell you that the same codec will produce the same result in:

```text
Spark + Parquet + zstd
```

The reader implementation matters.

Therefore:

> **A benchmark result is evidence for a specific environment and workload, not a universal truth about a codec.**

---

# 39. CSV gzip vs Parquet Experiment

The roadmap requires an experiment comparing:

- a large CSV compressed with gzip
- the same CSV compressed with zstd
- equivalent Parquet

### Procedure

1. Create a large orders dataset.
2. Write `orders.csv`.
3. Compress it as `orders.csv.gz`.
4. Compress it as `orders.csv.zst`.
5. Write the same logical data as Parquet.
6. Query all three with DuckDB or Polars.
7. Compare:
   - file size,
   - full-scan time,
   - one-column access,
   - filtered-query behavior,
   - observed parallel-read behavior where the tool exposes it.
8. Explain why the gzip file cannot be split as a single compressed stream.

Create the two compressed files from the same `orders.csv`:

```bash
gzip -c orders.csv > orders.csv.gz
zstd -f orders.csv -o orders.csv.zst
```

Read them with DuckDB `read_csv` and read Parquet with `read_parquet`:

```sql
SELECT COUNT(*) FROM read_csv('orders.csv.gz', compression = 'gzip');
SELECT COUNT(*) FROM read_csv('orders.csv.zst', compression = 'zstd');
SELECT COUNT(*) FROM read_parquet('orders.parquet');
```

DuckDB can usually detect compression from the file extension. The explicit `compression` argument is shown for clarity. Confirm support in your installed DuckDB version.

Keep the query semantically equivalent.

Do not assume every engine exposes the same "bytes read" metric for every format.

---

## Conceptual comparison

```text
orders.csv.gz
    ↓
gzip stream
    ↓
decompress
    ↓
parse text
    ↓
execute
```

versus:

```text
orders.parquet
    ↓
inspect metadata
    ↓
select relevant columns/pages
    ↓
decompress required data
    ↓
decode typed values
    ↓
execute
```

`orders.csv.zst` follows the same path as `orders.csv.gz`: a compressed CSV, then text parsing, then the query.

### Parallel query execution vs splitting the compressed stream

```sql
SET threads = 8;

SELECT COUNT(*)
FROM read_csv('orders.csv.gz', compression = 'gzip');
```

```text
orders.csv.gz
    ↓
one gzip-compressed stream
    ↓
cannot be divided into independent compressed byte ranges
    ↓
a parallel reader cannot simply split it into independent gzip chunks
```

Setting the DuckDB thread count does not make a single gzip stream splittable. The compressed stream itself cannot simply be divided into independent byte ranges for parallel decompression.

This does not mean the whole query is necessarily single-threaded. Other stages of execution may still use parallelism. Parallel query execution is different from parallel splitting of the compressed input stream. Parquet avoids the problem because each row group, column chunk and page is compressed independently.

The formats have different physical capabilities.

The comparison involves more than compressed file size: compression ratio, decompression work, text parsing, column pruning, filtering, parallel-read characteristics and file structure. The results depend on the workload, so measure in your environment.

Do not compare them only by compressed file size.

---

# 40. Sorting Experiment

The roadmap requires a sorting experiment.

Choose one codec.

For example:

```text
zstd level 3
```

Then create:

### Dataset A

Random order.

### Dataset B

Sorted by:

```text
country, created_at
```

Write both using the same:

- schema
- codec
- compression level
- row-group settings
- page settings

Measure:

- file size
- write time
- relevant query time
- row-group statistics where useful

Conceptual expectation:

```text
Random
 ↓
less local repetition

Sorted
 ↓
more local repetition
```

But the actual effect must be measured.

Sorting can also affect query statistics:

```text
Sort order
    ↓
tighter ranges
    ↓
more useful pruning
```

That is why sorting belongs to physical-layout engineering, not just compression.

---

# 41. Hot/Warm/Cold Recommendation Table

After your benchmark, fill this table:

| Data Tier | Observed Read Pattern | Observed Codec Trade-off | Candidate Setting | Evidence |
| --- | --- | --- | --- | --- |
| Hot | frequent reads | | | |
| Warm | periodic reads | | | |
| Cold | rare reads | | | |

Do not fill this with a preselected codec.

Build the recommendation from your own measurements.

---

# 42. Per-Column Compression in Practice

Suppose a Parquet table has:

```text
country
status
description
customer_id
image_bytes
```

The physical characteristics differ.

A reasonable engineering process is:

```text
Inspect data characteristics
       ↓
Identify candidate codecs/settings
       ↓
Benchmark representative columns
       ↓
Measure file and query impact
       ↓
Decide whether per-column settings are justified
```

Do not add complexity unless the benefit is measurable.

A per-column policy can increase:

- configuration complexity,
- documentation requirements,
- testing requirements,
- interoperability testing.

---

# 43. Compression + Encoding Example

Consider:

```text
country

IN
IN
US
IN
UK
IN
US
```

A columnar writer may first use a compact value encoding strategy.

Conceptually:

```text
Dictionary
0 → IN
1 → US
2 → UK

Encoded sequence
0, 0, 1, 0, 2, 0, 1
```

Then:

```text
encoded representation
       ↓
compression codec
       ↓
final bytes
```

This explains why:

> **A codec does not operate in isolation from the format's encoding strategy.**

---

# 44. Stop and Think — Compression Ratio

Raw data:

```text
100 GB
```

Compressed data:

```text
25 GB
```

Calculate:

1. compression ratio
2. space savings

### Answer

```text
Compression ratio
= 100 / 25
= 4:1

Space savings
= 1 - (25 / 100)
= 75%
```

The same dataset still requires decompression when read.

---

# 45. Stop and Think — Smaller File

A codec produces:

```text
Codec A → 20 GB
Codec B → 25 GB
```

But:

```text
Codec A → 5× CPU
Codec B → 1× CPU
```

Is Codec A automatically better?

### Answer

No.

The decision depends on:

- storage cost,
- read frequency,
- write frequency,
- CPU cost,
- network cost,
- egress,
- latency,
- compatibility.

---

# 46. Stop and Think — gzip Splittability

A 100 GB `.csv.gz` file exists.

Can ten workers simply take arbitrary byte offsets and independently decompress their regions as if each offset were a complete input stream?

### Answer

Not in the straightforward way expected for a splittable file format.

A conventional gzip file represents a compressed stream. An arbitrary byte offset is not automatically a valid independent decompression starting point.

A format may instead preserve parallelism through independently processable internal units.

---

# 47. Stop and Think — Compressed Parquet

A Parquet file uses zstd.

Does that automatically mean:

```text
entire file = one giant non-splittable zstd stream
```

### Answer

No.

Parquet organizes data into internal structures such as row groups, column chunks, and pages. Compression applies to those physical units rather than turning the whole file into a single opaque compression stream.

The exact page/compression structure is part of the Parquet implementation/specification.

---

# 48. Stop and Think — UUID Compression

A UUID column contains one mostly unique identifier per row.

Will dictionary encoding necessarily produce major compression gains?

### Answer

No.

Dictionary encoding benefits from repeated values. A mostly unique column may produce a large dictionary and weaker gains.

That does not mean the column is inherently incompressible. Other encodings or general compression may still find some structure.

---

# 49. Stop and Think — JPEG

A Parquet binary column contains JPEG images.

After compression the file barely shrinks.

Is that automatically a bug?

### Answer

No.

JPEG is already a compressed representation, so there may be little remaining redundancy for another general-purpose compressor to exploit.

The extra compression work can still consume CPU even when size savings are small.

---

# 50. Stop and Think — zstd Levels

Suppose a benchmark reports:

```text
zstd 9
→ 100 GB

zstd 19
→ 98 GB
```

but:

```text
zstd 19
→ 2× compression CPU
```

What question matters?

### Answer

Whether the extra 2% reduction justifies the extra CPU, time, and resulting compute cost.

The answer depends on:

- retention period,
- storage/network pricing,
- write frequency,
- read frequency,
- CPU price,
- operational priorities.

---

# 51. Debugging Common Compression Problems

## Problem 1 — Compression Ratio Is Surprisingly Poor

### Symptom

```text
Expected:
much smaller file

Observed:
only modest size reduction
```

### Possible causes

- high-cardinality data,
- random values,
- encrypted bytes,
- already-compressed payloads,
- weak redundancy,
- unexpected data distribution,
- codec settings.

### Inspect

```text
column cardinality
value repetition
data type
existing compression
codec
level
```

### Measure

Compare:

```text
raw size
encoded size where available
compressed size
```

### Lesson

Compression behavior is a property of the **data plus representation plus codec**.

---

## Problem 2 — Compression Made the Query Slower

### Symptom

The compressed file is smaller, but query latency increased.

### Possible causes

- decompression became CPU-heavy,
- the workload was already I/O-light,
- cache state changed,
- query execution dominates,
- different row-group/page behavior,
- codec overhead is significant for this workload.

### Inspect

```text
bytes read
CPU utilization
cache state
read time
decompression cost
```

### Lesson

Smaller storage is not synonymous with faster queries.

---

## Problem 3 — Higher zstd Level Barely Helps

### Symptom

```text
level 9 → 25.0 GB
level 19 → 24.8 GB
```

but write CPU increases substantially.

### Inspect

- measured ratio,
- compression time,
- data characteristics,
- read/write frequency.

### Lesson

This is a classic diminishing-return decision.

---

## Problem 4 — gzip File Cannot Be Parallelized as Expected

### Symptom

Workers cannot independently start reading arbitrary portions.

### Cause

The data was stored as one gzip stream.

### Inspect

Determine whether the source is:

```text
one compressed stream
```

or:

```text
many independently processable compressed units
```

### Lesson

Splittability depends on file/container structure.

---

## Problem 5 — Two Columns Behave Differently

### Symptom

The same codec produces very different compression behavior across columns.

### Likely causes

- cardinality,
- text length,
- repetition,
- sorting,
- data distribution,
- encoding choices.

### Lesson

Columnar data is inherently heterogeneous.

---

## Problem 6 — File Is Small but Query Is Still Expensive

### Possible causes

- CPU-heavy decompression,
- expensive filtering,
- many files,
- poor row-group layout,
- insufficient pruning,
- query execution cost,
- large number of values decoded.

### Lesson

Compression is only one layer of the performance stack.

---

## Problem 7 — Consumer Cannot Read the File

### Likely causes

- unsupported codec,
- unsupported format feature,
- library version mismatch,
- missing optional codec support.

### Fix

Validate:

```text
writer version
reader version
format support
codec support
```

Do not solve an interoperability problem by changing production data blindly.

---

## Problem 8 — Benchmark Results Are Inconsistent

### Investigate

- cache state,
- warm-up,
- background processes,
- CPU scheduling,
- object-storage variability,
- dataset generation,
- first-read vs repeated-read effects.

### Lesson

A benchmark needs experimental discipline.

---

# 52. Common Mistakes

## 1. Choosing maximum compression for everything

Why it is risky:

- higher CPU,
- longer writes,
- diminishing returns,
- possible latency impact.

---

## 2. Assuming the smallest file is always fastest

File size does not capture:

- CPU,
- query execution,
- cache effects,
- layout,
- engine behavior.

---

## 3. Assuming the fastest codec always minimizes total cost

A fast codec may produce more bytes.

Those bytes can create:

- higher storage,
- higher transfer,
- higher egress.

---

## 4. Comparing codecs on different datasets

This invalidates much of the comparison.

Keep the logical input identical.

---

## 5. Measuring only file size

You need at least:

- write time,
- read time,
- representative query behavior.

---

## 6. Measuring only write time

A codec can be cheap to write and expensive to read.

---

## 7. Measuring only read time

A codec can be excellent for reads but expensive at ingestion scale.

---

## 8. Ignoring decompression CPU

Read-heavy analytical systems can expose decompression cost repeatedly.

---

## 9. Ignoring network and egress

Remote data movement can materially change the trade-off.

---

## 10. Ignoring storage price

Long-lived datasets multiply small differences in compressed size.

---

## 11. Ignoring data distribution

Codec behavior depends on actual redundancy.

---

## 12. Confusing encoding and compression

For example:

```text
dictionary encoding
```

is not the same thing as:

```text
zstd compression
```

---

## 13. Assuming compression destroys splittability

It depends on how compression is organized.

---

## 14. Treating `.csv.gz` as equivalent to internally compressed Parquet

They have different physical structures and capabilities.

---

## 15. Assuming sorting always gives huge gains

Sorting can help, but the effect depends on the data and workload.

---

## 16. Applying the same strategy blindly to every column

Columns differ.

---

## 17. Compressing already-compressed data

You may add CPU work without meaningful size reduction.

---

## 18. Assuming encrypted data will compress well

Encryption intentionally removes recognizable redundancy.

---

## 19. Choosing an unsupported codec

A technically attractive codec is useless if the required reader cannot consume it.

---

## 20. Treating another team's benchmark as universal truth

Different:

- data,
- engines,
- hardware,
- versions,
- storage paths

produce different outcomes.

---

## 21. Treating zstd level 19 as automatically better than lower levels

"More compression effort" is not the same as "better production result."

---

## 22. Ignoring hot/warm/cold access frequency

A codec decision should reflect how the data is actually used.

---

# 53. Production Architecture

Compression belongs in the physical data architecture:

```text
Source
  ↓
Encoding / Serialization
  ↓
File Format
  ↓
Compression
  ↓
Object Storage
  ↓
Query Engine
  ↓
Decompression
  ↓
Execution
```

A platform policy can therefore look conceptually like:

```text
Workload
   ↓
Compression Policy
   ├── Codec
   ├── Level
   └── Column-specific settings
   ↓
Storage
   ↓
Monitoring
   ├── Size
   ├── CPU
   ├── Read Time
   └── Cost
```

The key production insight is:

> **Codec policy is part of platform engineering, not merely a writer configuration detail.**

---

# 54. Hot / Warm / Cold Architecture

A deliberate platform may reason like this:

```text
HOT
→ frequently queried
→ read/decompression behavior is important

WARM
→ periodically queried
→ balance CPU and storage

COLD
→ rarely queried
→ storage/transfer savings may carry more weight
```

This is a starting heuristic.

A platform should validate it using its own measurements.

---

# 55. Production Case Study — 100 TB Historical Events

A company stores:

```text
100 TB historical event data
```

Access pattern:

```text
20 TB queried every day
30 TB queried weekly
50 TB rarely queried
```

The platform team evaluates:

- Snappy
- gzip
- zstd level 1
- zstd level 3
- zstd level 9
- zstd level 19
- LZ4

### Question 1

Should the entire dataset necessarily use one codec?

### Reasoning

Not necessarily.

The access-frequency distribution suggests different tiers may have different economics.

But whether multiple policies are worthwhile depends on:

- operational complexity,
- actual measured differences,
- retention,
- storage cost,
- query CPU,
- migration/rewriting cost.

---

### Question 2

What measurements matter?

At minimum:

- size,
- write time,
- full-read time,
- relevant query time,
- CPU,
- transfer volume,
- cache conditions.

---

### Question 3

How should hot/warm/cold influence evaluation?

It changes the weighting of metrics.

For example:

```text
Hot
→ repeated read/decompression cost matters more

Cold
→ retained storage volume may matter more
```

---

### Question 4

What costs need to be modeled?

```text
storage
+
write CPU
+
read/decompression CPU
+
network
+
egress
```

---

### Question 5

What compatibility needs to be checked?

Test actual readers:

```text
PyArrow
DuckDB
Polars
Spark
Trino
```

for the exact production versions.

---

### Question 6

What should be tested before standardization?

```text
Representative data
+
Representative queries
+
Representative storage
+
Representative consumers
```

Then document the measured decision.

No universal codec should be selected from the chapter alone.

---

# 56. Monthly Cost Scenario

Use variables:

```text
Data Volume
Storage Price
Read Volume
CPU Cost
Network / Egress Cost
Compression Ratio
Compression CPU
Decompression CPU
```

Then:

```text
Total Monthly Cost
=
Storage
+
Compute
+
Network
+
Egress
```

Consider two codecs:

```text
Codec A
→ smaller files
→ higher CPU

Codec B
→ larger files
→ lower CPU
```

There are workloads where A can be attractive.

There are workloads where B can be attractive.

The decision depends on measured economics.

---

# 57. Codec Policy Document

A production team can maintain a table like:

| Data Class | Codec Candidate | Level | Reason | Evidence | Exception |
| --- | --- | --- | --- | --- | --- |
| Hot | | | | | |
| Warm | | | | | |
| Cold | | | | | |

A good policy is:

- measurable,
- versioned,
- reviewable,
- exception-aware.

The table is a decision record, not a list of permanent truths.

---

# 58. How to Evaluate a New Codec

Do not memorize every codec.

Learn a reusable evaluation process:

```text
New Codec
   ↓
Read Documentation
   ↓
Check Format Support
   ↓
Check Consumers
   ↓
Benchmark Compression
   ↓
Benchmark Decompression
   ↓
Measure Size
   ↓
Measure CPU
   ↓
Model Cost
   ↓
Test Reliability
   ↓
Decision
```

Ask:

- Does the target file format support it?
- Do all required consumers support it?
- What is the writer CPU cost?
- What is the reader CPU cost?
- What size reduction occurs on our data?
- Does it affect latency?
- Does it affect splitting/parallelism?
- Is operational complexity acceptable?
- What happens during upgrades?
- Can the choice be rolled back?

---

# 59. Required Python Coding Examples

## Example 1 — Compress a Bytes Object with gzip

Python's standard library provides a `gzip` interface for compression and decompression.

```python
from __future__ import annotations

import gzip

payload = b"IN " * 10_000

compressed = gzip.compress(payload)

print(f"original:   {len(payload):,} bytes")
print(f"compressed: {len(compressed):,} bytes")

restored = gzip.decompress(compressed)

assert restored == payload

print("round-trip verified")
```

### What to observe

The final assertion verifies:

```text
original bytes
==
decompressed bytes
```

This is lossless compression behavior.

---

## Example 2 — Calculate Ratio and Savings

```python
def compression_metrics(
    original_size: int,
    compressed_size: int,
) -> tuple[float, float]:
    ratio = original_size / compressed_size
    savings = 1 - (compressed_size / original_size)
    return ratio, savings


ratio, savings = compression_metrics(
    original_size=100 * 1024**3,
    compressed_size=25 * 1024**3,
)

print(f"ratio: {ratio:.2f}:1")
print(f"savings: {savings:.1%}")
```

Expected conceptual result:

```text
ratio: 4.00:1
savings: 75.0%
```

---

## Example 3 — Verify Decompression Equality

```python
import gzip

original = b"hello" * 1_000
compressed = gzip.compress(original)
decompressed = gzip.decompress(compressed)

print(original == decompressed)
```

Expected:

```text
True
```

The important lesson is not Python's API.

The lesson is:

```text
Compression
→ no information loss

Decompression
→ restores original bytes
```

---

# 60. Example 4 — Parquet Compression with PyArrow

```python
from __future__ import annotations

import pyarrow as pa
import pyarrow.parquet as pq

table = pa.table(
    {
        "country": ["IN", "IN", "US", "IN", "UK"],
        "status": ["PAID", "PAID", "PENDING", "PAID", "CANCELLED"],
        "amount": [100.0, 150.0, 200.0, 75.0, 120.0],
    }
)

pq.write_table(
    table,
    "orders_snappy.parquet",
    compression="snappy",
)

pq.write_table(
    table,
    "orders_zstd.parquet",
    compression="zstd",
)

print("files written")
```

This demonstrates two codec choices while keeping the logical dataset the same.

It does **not** demonstrate that one is better.

---

# 61. Example 5 — zstd Levels

```python
from pathlib import Path

import pyarrow.parquet as pq

levels = [1, 3, 9, 19]

for level in levels:
    path = Path(f"orders_zstd_{level}.parquet")

    pq.write_table(
        table,
        path,
        compression="zstd",
        compression_level=level,
    )

    print(level, path.stat().st_size)
```

### Engineering lesson

This creates a measurement opportunity:

```text
zstd level
    ↓
file size
+
write time
+
read time
```

Do not interpret the output before measuring repeated runs.

---

# 62. Example 6 — Benchmark Helper

```python
from time import perf_counter
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def timed(operation: Callable[[], T]) -> tuple[T, float]:
    start = perf_counter()
    result = operation()
    elapsed = perf_counter() - start
    return result, elapsed
```

Use it like:

```python
_, seconds = timed(
    lambda: pq.read_table("orders_zstd_3.parquet")
)

print(f"full read: {seconds:.4f}s")
```

The helper separates:

```text
operation
```

from:

```text
measurement
```

That makes experiments easier to repeat consistently.

---

# 63. Example 7 — File-Size Helper

```python
from pathlib import Path


def file_size_bytes(path: str | Path) -> int:
    return Path(path).stat().st_size


size = file_size_bytes("orders_zstd_3.parquet")
print(f"{size:,} bytes")
```

Again, file size is only one metric.

---

# 64. Example 8 — One-Column Read

```python
import pyarrow.parquet as pq

table = pq.read_table(
    "orders_zstd_3.parquet",
    columns=["amount"],
)

print(table.schema)
```

This connects compression to the columnar concepts learned earlier:

```text
Query asks for one column
      ↓
column pruning
      ↓
only relevant column data needs to be processed
      ↓
codec decompresses the relevant data
```

The exact I/O behavior depends on the file and reader.

---

# 65. Encoding, Compression, and Sorting Together

Consider a `country` column.

```text
IN
IN
IN
US
US
CA
CA
```

A columnar writer may exploit repetition through encoding.

Then:

```text
encoded values
     ↓
compression
```

Sorting can make similar values more local.

Thus:

```text
sort order
   ↓
value locality
   ↓
encoding opportunity
   ↓
compression opportunity
```

This is why physical layout and compression cannot always be evaluated independently.

---

# 66. Codec Compatibility Checklist

Before changing a production codec:

- [ ] Verify the file format supports it.
- [ ] Verify every required writer supports it.
- [ ] Verify every required reader supports it.
- [ ] Verify deployed library versions.
- [ ] Test representative files.
- [ ] Test old readers if backward compatibility is required.
- [ ] Test cloud/platform tooling.
- [ ] Document exceptions.
- [ ] Plan rollback/rewrite behavior.

---

# 67. Production Data-Engineering Checklist

Before standardizing a codec:

- [ ] Workload classified.
- [ ] Data characteristics understood.
- [ ] Hot/warm/cold access pattern understood.
- [ ] Candidate codecs identified.
- [ ] Compression levels identified.
- [ ] Consumer compatibility verified.
- [ ] File format supports the selected codec.
- [ ] Benchmark environment documented.
- [ ] File size measured.
- [ ] Write time measured.
- [ ] Full-read time measured.
- [ ] One-column-read time measured.
- [ ] Decompression cost considered.
- [ ] Network cost considered.
- [ ] Storage cost considered.
- [ ] Egress considered.
- [ ] Sorting effect tested where relevant.
- [ ] Already-compressed data considered.
- [ ] Exception policy documented.
- [ ] Decision backed by evidence.

---

# 68. Production Code Review Exercise

Suppose a team submits:

```python
# Maximum compression is always better.

compression_level = 19
codec = "zstd"
```

and uses it for every dataset.

As a reviewer, ask:

1. What is the workload?
2. How frequently is the data read?
3. How frequently is it written?
4. What is the measured size reduction?
5. What is the measured compression CPU?
6. What is the measured decompression CPU?
7. What is the storage price?
8. Is network/egress significant?
9. Do consumers support the codec/settings?
10. Did the team benchmark lower levels?

A production correction is not simply:

> "Use level 3."

The correction is:

```text
Workload
   ↓
Benchmark
   ↓
Cost Model
   ↓
Compatibility
   ↓
Policy
```

---

# 69. Debugging Decision Tree

### File unexpectedly large

```text
File unexpectedly large
        ↓
Check data distribution
        ↓
Check encoding
        ↓
Check codec
        ↓
Check compression level
        ↓
Check already-compressed fields
        ↓
Check sorting
        ↓
Measure again
```

### Query unexpectedly slower

```text
Query unexpectedly slower
        ↓
Check bytes read
        ↓
Check I/O
        ↓
Check decompression CPU
        ↓
Check cache state
        ↓
Check codec/level
        ↓
Compare alternative
```

These are investigation paths, not guaranteed fixes.

---

# 70. Nested and Semi-Structured Data Consideration

From Topic 06, you know that one Parquet dataset may contain:

- scalar columns,
- lists,
- structs,
- maps,
- nested structures.

Compression can behave differently across these physical representations.

For example:

```text
low-cardinality scalar
→ potentially strong redundancy

nested free-form metadata
→ potentially sparse / heterogeneous

binary media
→ may already be compressed
```

Therefore:

> **Compression analysis should reflect actual column structure, not just total file size.**

---

# 71. Why Sorting Is a Dual Optimization

Sorting can affect:

### Compression

```text
similar values together
→ more representation redundancy
```

### Statistics

```text
tighter ranges
→ potentially stronger predicate skipping
```

Therefore:

```text
Sort order
     ↓
┌────┴────┐
↓         ↓
Compression  Pruning
```

This is why a sort decision can have effects beyond compression alone.

---

# 72. Architecture Review Example

A senior engineer should be able to say:

> "We evaluated the codec using our representative data and production query patterns. We measured file size, write time, full-read time, one-column-read time, CPU, and transfer volume across repeated runs. We also checked compatibility with our deployed readers. The resulting choice is a workload-specific trade-off rather than a claim that this codec is universally superior."

That is a defensible architecture statement because it is:

- scoped,
- measured,
- reproducible,
- compatibility-aware,
- open to future re-evaluation.

---

# 73. Interview Questions

## Basic

### 1. What is compression?

**Model answer:**  
Compression is a lossless representation technique that reduces the number of bytes required to store or transfer data. It generally trades CPU work for fewer bytes.

### 2. Why do we compress data?

**Model answer:**  
To reduce storage, I/O, and network transfer volume. Compression can also improve latency when the saved I/O is more expensive than the CPU required to decompress.

### 3. What is compression ratio?

**Model answer:**  

```text
Uncompressed size / compressed size
```

A ratio of 4:1 means the compressed representation is one quarter of the original size.

### 4. Why is CPU involved?

**Model answer:**  
Compression performs computational work to find a smaller representation, and reading compressed data requires decompression work.

---

## Intermediate

### 5. How is Snappy different conceptually from gzip?

**Model answer:**  
Both are lossless codecs, but Snappy is generally positioned toward fast processing while gzip commonly emphasizes stronger compression at greater CPU cost. The exact outcome depends on the data and implementation.

### 6. Why does zstd expose compression levels?

**Model answer:**  
To let users select different points on the speed-versus-compression-effort trade-off.

### 7. What is LZ4 optimized for?

**Model answer:**  
LZ4 is strongly speed-oriented, making it a candidate when compression/decompression latency and throughput are more important than maximizing compression ratio.

### 8. What is encoding vs compression?

**Model answer:**  
Encoding changes the representation of values; compression reduces the size of that representation. They are separate physical stages.

### 9. What is splittability?

**Model answer:**  
The ability to process different portions of a large data source independently, which can enable parallel work across workers.

### 10. Why is `.csv.gz` different from compressed Parquet?

**Model answer:**  
A `.csv.gz` file commonly contains one gzip stream around text records. Parquet organizes encoded/compressed data into internal analytical units such as pages and row groups, enabling format-aware selective and parallel processing.

---

## Advanced

### 11. Why can sorting improve compression?

**Model answer:**  
Sorting can place similar values next to each other, increasing opportunities for compact encoding and general-purpose compression.

### 12. Why can the same codec behave differently on two columns?

**Model answer:**  
Columns have different cardinality, repetition, lengths, value distributions, null rates, and encodings. Compression acts on the actual representation, not merely the column name.

### 13. Why can already-compressed data compress poorly?

**Model answer:**  
An earlier compression algorithm has already removed much of the available redundancy, leaving less structure for another general-purpose compressor to exploit.

### 14. How do compression levels create diminishing returns?

**Model answer:**  
Increasing algorithmic effort can continue to reduce size, but later increases may produce progressively smaller gains while consuming substantially more CPU and time.

### 15. Why can internally compressed analytical files preserve parallelism?

**Model answer:**  
Because compression can be applied to independently processable physical units inside the container, rather than wrapping the entire file in one opaque stream.

---

## Senior / Architecture

### 16. How would you choose codecs for a 100 TB lake?

**Model answer:**  
Classify workloads and data tiers, measure representative data and queries, compare size/write/read/decompression behavior, model storage/compute/network/egress cost, verify reader compatibility, and document the result as a revisitable policy.

### 17. Would you use one codec for hot and cold data?

**Model answer:**  
Not automatically. Access frequency changes the relative value of decompression CPU versus long-term storage and transfer savings. A single codec may still be preferable if the operational simplicity outweighs the measured benefit of multiple policies.

### 18. How would you model storage vs compute cost?

**Model answer:**  
Estimate compressed volume, retention, read/write frequency, compression CPU, decompression CPU, network transfer, and egress. Compare total workload-level cost rather than storage size alone.

### 19. How would you benchmark codecs fairly?

**Model answer:**  
Hold the dataset, schema, format, writer settings, environment, queries, storage path, and measurement procedure constant. Change only the codec/level under test, run repeated measurements, record cache conditions, and retain raw results.

### 20. How would you evaluate a new codec?

**Model answer:**  
Check format support and consumers first, then benchmark compression and decompression on representative data, measure size and CPU, evaluate compatibility and operational complexity, model total cost, and run an end-to-end workload test before adoption.

### 21. How would you defend a codec choice in an architecture review?

**Model answer:**  
Present the workload assumptions, measured trade-offs, consumer-compatibility results, cost model, operational implications, and known exceptions. Avoid claiming the codec is universally best.

---

# 74. Practical Scenarios

## Scenario 1 — Hot Analytical Data

A Parquet dataset is queried continuously throughout the business day.

### Ask

What should matter when selecting a codec?

### Reasoning

Consider:

- decompression cost,
- read latency,
- CPU utilization,
- bytes transferred,
- file size,
- storage medium,
- query concurrency.

Do not decide from the codec name alone.

---

## Scenario 2 — Long-Term Archive

A dataset is retained for years and rarely queried.

### Ask

Should the decision emphasize the exact same metrics as hot data?

### Reasoning

The relative value of:

- storage savings,
- long-term transfer reduction,

may increase.

But:

- archival retrieval time,
- rewrite cost,
- CPU,
- compatibility,

still matter.

---

## Scenario 3 — High-Entropy Data

A dataset contains encrypted/random-looking payloads.

### Ask

What compression result would you expect conceptually?

### Reasoning

Likely limited additional redundancy is available.

The correct action is to measure rather than assume zero compression benefit.

---

## Scenario 4 — Partner Export

A partner requires:

```text
CSV.gz
```

### Ask

What considerations exist?

### Reasoning

The partner's compatibility requirement is a hard constraint.

You may still use Parquet internally:

```text
Parquet
   ↓
export transformation
   ↓
CSV
   ↓
gzip
   ↓
partner
```

The external format does not have to dictate the internal storage format.

---

## Scenario 5 — Mixed Columns

A Parquet dataset contains:

- low-cardinality categories,
- long descriptions,
- random IDs,
- JPEG images.

### Ask

Should every column necessarily be treated identically?

### Reasoning

Not necessarily.

Different columns can have different compression characteristics.

But per-column customization adds operational complexity, so it should be justified by measurement.

---

# 75. New-Codec Evaluation Exercise

A new compression codec claims:

> "Smaller files with comparable decompression speed."

Do not accept the statement at face value.

Create an evaluation plan:

```text
Claim
  ↓
Representative Dataset
  ↓
Controlled Benchmark
  ↓
Size
  ↓
Compression CPU
  ↓
Decompression CPU
  ↓
Read Latency
  ↓
End-to-End Query
  ↓
Compatibility
  ↓
Operational Cost
  ↓
Decision
```

The correct conclusion comes from evidence.

---

# 76. Production Reliability

A codec change can affect reliability as well as performance.

Think about:

- failed writes,
- corrupted outputs,
- unsupported readers,
- library upgrades,
- backfills,
- historical file compatibility,
- recovery time.

A robust rollout pattern is:

```text
Benchmark
   ↓
Compatibility Test
   ↓
Canary Data
   ↓
Validation
   ↓
Controlled Rollout
   ↓
Monitor
   ↓
Re-evaluate
```

Do not rewrite an entire lake because a microbenchmark looks promising.

---

# 77. Codec Policy Design

A production organization may maintain:

```text
Dataset
    ↓
Workload Class
    ↓
Codec Policy
    ↓
Versioned Implementation
    ↓
Monitoring
```

An exception should explain:

- why the default policy was insufficient,
- what measurements justify the exception,
- which consumers depend on it,
- when the decision should be revisited.

---

# 78. Format and Codec Are Separate Decisions

Do not confuse:

```text
Format
```

with:

```text
Codec
```

For example:

```text
Parquet
+
Snappy
```

and:

```text
Parquet
+
zstd
```

are two physical realizations of the same logical format.

Likewise:

```text
CSV
+
gzip
```

is a different format/container arrangement from:

```text
Parquet
+
gzip
```

The surrounding format determines how the compression is organized and how a reader can navigate the data.

---

# 79. Compression and Small Files

Compression interacts with file sizing.

Very small files may have:

- limited redundancy,
- higher metadata overhead,
- many separate compression contexts,
- lower compression efficiency.

Large well-batched files can sometimes give compressors more data to work with.

However:

```text
bigger files
```

can also affect:

- parallelism,
- memory,
- rewrite cost.

This topic does not replace Topic 09's detailed small-files treatment.

The key connection is:

> **File layout influences how effectively compression can be used.**

---

# 80. Compression and Partitioning

Partitioning can also influence compression.

For example:

```text
year=2025/month=01
year=2025/month=02
```

may produce subsets with more locally consistent values.

But excessive partitioning creates many small files.

Therefore:

```text
Partitioning
+
File sizing
+
Sorting
+
Encoding
+
Compression
```

must be designed together.

The detailed partitioning decision belongs to Topic 08.

---

# 81. Compression and Object Storage

Object storage changes the economics because data is frequently:

- remote,
- request-based,
- transferred through a network path.

This makes byte reduction more valuable in many workloads.

But compression can also increase CPU use inside the query engine.

Therefore an object-storage workload should measure:

```text
bytes transferred
+
decompression CPU
+
query time
```

not merely:

```text
file size
```

---

# 82. Production Decision Log

A concise codec decision can be documented like this:

```text
Workload:
  Daily analytical scans over historical events.

Data:
  High repetition in categories, high uniqueness in IDs.

Candidates:
  Snappy, zstd levels 1/3/9.

Measured:
  File size
  Write time
  Full-read time
  One-column-read time
  CPU
  Network volume

Compatibility:
  Verified against deployed readers.

Decision:
  [fill from measured evidence]

Reason:
  [fill from measured evidence]

Exceptions:
  [fill as required]

Review trigger:
  [new engine/library/data distribution/cost change]
```

This is stronger than:

> "Team standard says zstd."

---

# 83. Mini Decision Exercise

Suppose you are given:

```text
Dataset:
20 TB

Write frequency:
daily

Read frequency:
hourly

Typical query:
10% of columns

Storage:
remote object storage

CPU:
moderate budget

Consumer:
multiple engines
```

### Build the decision

Ask:

1. Which codecs should be benchmarked?
2. Which metrics matter most?
3. What compatibility tests are required?
4. Would you test multiple zstd levels?
5. Would you measure one-column reads?
6. Would sorting matter?
7. How would you document the final decision?

### Model reasoning

The workload is read-heavy and uses remote storage, so both:

```text
compressed bytes
```

and:

```text
decompression CPU
```

matter.

A reasonable benchmark would include multiple speed/ratio points rather than only the strongest compression level.

The final choice should come from measured evidence plus consumer compatibility.

---

# 84. Review: What a Senior Engineer Looks At

When a teammate proposes:

```text
compression="zstd"
compression_level=19
```

do not immediately approve or reject it.

Ask:

```text
Why?
 ↓
What workload?
 ↓
What data?
 ↓
What measured ratio?
 ↓
What write CPU?
 ↓
What decompression CPU?
 ↓
What storage savings?
 ↓
What network savings?
 ↓
Which consumers?
 ↓
Which versions?
 ↓
What alternatives?
 ↓
What evidence?
```

That is physical data engineering reasoning.

---

# 85. Connection to Earlier Topics

This topic builds directly on earlier physical-layout concepts.

### Topic 02

Parquet internals introduced:

```text
row groups
column chunks
pages
encodings
statistics
```

Now add:

```text
compression
```

The combined mental model becomes:

```text
Values
 ↓
Encoding
 ↓
Compression
 ↓
Page/Block Bytes
```

### Topic 03

PyArrow exposed writer controls.

Now those settings can be interpreted as physical decisions:

```text
compression
compression_level
```

instead of arbitrary API parameters.

### Topic 04

Avro introduced block-level compression.

Now compare:

```text
Avro blocks
vs
Parquet pages
vs
ORC internal units
```

The goal is to understand how the surrounding container organizes compressed data.

---

# 86. Connection to Future Topics

Later roadmap topics go deeper into:

- partitioning,
- small files,
- cloud storage,
- performance,
- scaling,
- cost optimization.

This chapter provides the compression foundation those topics build upon.

Do not optimize a codec in isolation from the wider physical layout.

---

# 87. Final Compression Decision Framework

Use this process:

```text
             START
               │
               ↓
        Understand Workload
               │
               ↓
        Understand Data Shape
               │
               ↓
        Classify Hot/Warm/Cold
               │
               ↓
        Identify Consumers
               │
               ↓
         Shortlist Codecs
               │
               ↓
        Check Compatibility
               │
               ↓
          Benchmark Fairly
               │
          ┌────┼────┐
          ↓    ↓    ↓
         Size CPU  Time
          │    │    │
          └────┼────┘
               ↓
          Model Total Cost
               │
               ↓
        Test Real Workload
               │
               ↓
        Select Codec/Level
               │
               ↓
        Document Evidence
               │
               ↓
         Monitor in Prod
               │
               ↓
       Re-evaluate Later
```

Do not ask:

> **Which compression codec is best?**

Ask:

> **Which codec and compression level produce the best measured trade-off for this workload, this data distribution, this access pattern, this infrastructure, and these consumers?**

---

# 88. Final Master Mental Model

```text
                DATA
                 │
                 ↓
              Encoding
                 │
                 ↓
             Compression
                 │
          ┌──────┼───────┐
          ↓      ↓       ↓
        Size    CPU     Time
          │      │       │
          └──────┼───────┘
                 ↓
          Storage / Network
                 │
                 ↓
            Decompression
                 │
                 ↓
             Query Engine
                 │
                 ↓
              Workload
                 │
                 ↓
                Cost
```

A good compression decision is:

```text
GOOD COMPRESSION DECISION
=
Data Characteristics
+
Workload
+
Read Frequency
+
Write Frequency
+
Codec Behavior
+
Compression Level
+
I/O
+
CPU
+
Storage Cost
+
Network Cost
+
Compatibility
+
Measured Evidence
```

---

# 89. Final "Remember This"

1. **Compression trades CPU work for fewer bytes.**
2. **Compression ratio, compression speed, and decompression speed are different metrics.**
3. **The smallest file is not automatically the fastest or cheapest.**
4. **Snappy is speed-oriented; gzip/Deflate emphasizes stronger compression; zstd provides a tunable range; LZ4 is strongly speed-oriented.**
5. **These are workload characteristics, not universal rankings.**
6. **Compression levels create a trade-off, often with diminishing returns.**
7. **Encoding and compression are different stages.**
8. **Sorting can improve both encoding/compression opportunities and query statistics.**
9. **Splittability depends on file/container organization, not simply whether compression exists.**
10. **A `.csv.gz` stream behaves differently from compressed internal units in Parquet, ORC, or Avro.**
11. **Different columns can have very different compression behavior.**
12. **Already-compressed and high-entropy data may compress poorly.**
13. **Codec compatibility is part of production design.**
14. **Storage, CPU, network, and egress costs all belong in the decision.**
15. **Hot, warm, and cold data may justify different strategies.**
16. **Benchmark with the real workload before standardizing.**
17. **A codec policy should be evidence-based and revisitable.**

---

# 90. Learning Checkpoint

Do not move forward until you can explain all of the following without looking at your notes.

## Core understanding

- [ ] I can explain why compression exists.
- [ ] I can explain compression ratio.
- [ ] I can explain compression speed.
- [ ] I can explain decompression speed.
- [ ] I can explain the I/O/CPU trade-off.

## Codec understanding

- [ ] I can describe the typical characteristics of Snappy.
- [ ] I can describe the typical characteristics of gzip/Deflate.
- [ ] I can describe the typical characteristics of zstd.
- [ ] I can describe the typical characteristics of LZ4.
- [ ] I can explain compression levels.
- [ ] I can explain diminishing returns.

## Physical-layout understanding

- [ ] I can distinguish encoding from compression.
- [ ] I can explain why sorting can help compression.
- [ ] I can define splittability.
- [ ] I can explain why `.csv.gz` differs from internally compressed Parquet.
- [ ] I can explain how Parquet/ORC/Avro can preserve parallel processing while using compression.

## Production understanding

- [ ] I can classify a workload as hot, warm, or cold.
- [ ] I can reason about per-column compression.
- [ ] I can identify already-compressed/high-entropy data.
- [ ] I can explain codec compatibility.
- [ ] I can model storage + compute + network + egress cost.
- [ ] I can design a fair codec benchmark.
- [ ] I can explain why one benchmark does not define a universal winner.
- [ ] I can build an evidence-based codec policy.

## Required experiment

- [ ] I ran no compression.
- [ ] I ran Snappy.
- [ ] I ran gzip.
- [ ] I ran LZ4.
- [ ] I ran zstd level 1.
- [ ] I ran zstd level 3.
- [ ] I ran zstd level 9.
- [ ] I ran zstd level 19.
- [ ] I repeated measurements at least three times.
- [ ] I recorded file size.
- [ ] I recorded write time.
- [ ] I recorded full-read time.
- [ ] I recorded one-column-read time.
- [ ] I performed the CSV gzip vs Parquet experiment.
- [ ] I performed the sorting experiment.
- [ ] I completed the hot/warm/cold recommendation table.
- [ ] I created a simple cost model.

---

# 91. Final Practical Assignment

Take one real dataset from your learning project.

Document:

```text
Dataset
Schema
Volume
Growth
Read frequency
Write frequency
Storage medium
Consumers
Hot/Warm/Cold class
```

Then produce:

```text
Candidate codecs
↓
Benchmark plan
↓
Measurements
↓
Cost model
↓
Compatibility results
↓
Codec choice
↓
Exceptions
↓
Monitoring plan
```

Your final written conclusion should contain the sentence:

> **"This codec choice is a workload-specific decision supported by measurements, compatibility checks, and cost analysis."**

Then explain the evidence behind it.

---

# 92. Codec Policy Review Triggers

A mature platform should revisit codec policy when meaningful assumptions change.

Examples:

- new query engine,
- new storage backend,
- major library upgrade,
- materially different data distribution,
- significant storage-price change,
- significant network/egress-price change,
- new consumer,
- new latency requirement,
- new retention requirement,
- new file-format feature.

A codec policy is not a permanent law.

It is a current engineering decision based on current evidence.

---

# 93. Final Architecture Review Checklist

Before approving a production codec change, ask:

```text
1. What workload are we optimizing?
2. What data characteristics matter?
3. What codec candidates were measured?
4. What compression levels were measured?
5. What is the size difference?
6. What is the write CPU difference?
7. What is the read/decompression difference?
8. What is the end-to-end query impact?
9. What is the network/egress impact?
10. What are the consumer compatibility constraints?
11. What happens to historical files?
12. What is the rollback plan?
13. What operational complexity is introduced?
14. What evidence supports the decision?
15. When will we re-evaluate it?
```

If these questions cannot be answered, the codec decision is probably not production-ready.

---

# 94. References

Use primary documentation when verifying exact codec or library behavior:

- Apache Parquet — Compression specification: https://parquet.apache.org/docs/file-format/data-pages/compression/
- Apache Parquet — Implementation status: https://parquet.apache.org/docs/file-format/implementationstatus/
- Apache Arrow / PyArrow — Reading and writing Parquet: https://arrow.apache.org/docs/python/parquet.html
- Apache Arrow / PyArrow — Parquet documentation and compatibility details: https://arrow.apache.org/docs/python/parquet/
- Python standard library — `gzip`: https://docs.python.org/3/library/gzip.html

> **Version discipline:** codec names, aliases, default settings, and supported compression levels can vary by library and release. Verify the exact API in the environment used for production.

---

# 95. Final Takeaway

The most important lesson of this entire topic is not a codec name.

It is a way of thinking:

```text
DATA
 ↓
Understand redundancy
 ↓
Understand workload
 ↓
Understand access frequency
 ↓
Understand infrastructure
 ↓
Choose candidate codec/level
 ↓
Benchmark
 ↓
Measure
 ↓
Model cost
 ↓
Verify compatibility
 ↓
Deploy deliberately
 ↓
Monitor
 ↓
Re-evaluate
```

Compression engineering is ultimately an exercise in balancing:

```text
bytes
+
CPU
+
latency
+
storage
+
network
+
egress
+
compatibility
+
operational complexity
```

> **Good Data Engineers do not maximize compression. They optimize the system-level trade-off that the workload actually needs.**
