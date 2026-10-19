# HBase and Wide-Column Storage on HDFS

> **Roadmap location:** Stage 2C — Data Engineering_3 → `02-Hadoop-Ecosystem-and-Legacy-Big-Data/05-hbase-and-wide-column-on-hdfs.md`  
> **Module position:** Topic 05 — Phase C: Wide-Column and Legacy Tooling  
> **Purpose:** Understand, operate, troubleshoot, and plan migration of existing HBase systems. This is a legacy-platform engineering lesson, not a recommendation to choose HBase for every new application.

## 1. Learning objectives

After completing this lesson, you should be able to:

- Explain why HBase was added to Hadoop and when low-latency random access is a better fit than batch-oriented HDFS files.
- Explain HDFS, ZooKeeper, HMaster, RegionServers, regions, and `hbase:meta`.
- Model tables using row keys, column families, qualifiers, cells, timestamps, and versions.
- Use HBase shell to create, insert, retrieve, scan, and delete data.
- Design sorted row keys for user events, including newest-first reads, and reason about hotspots, salting, hashing, and reverse timestamps.
- Trace writes through WAL and MemStore into HFiles, and reads through caches and StoreFiles.
- Explain flushes, compactions, region splits, balancing, Bloom filters, filters, and operational symptoms.
- Access HBase through Python's Thrift gateway while understanding client and security compatibility constraints.
- Evaluate HBase against Cassandra and DynamoDB based on access patterns, consistency, operations, and cost.
- Explain snapshot/export/bulk-load options and plan migration to Bigtable, Cassandra, DynamoDB, or a lakehouse.

## 2. Prerequisites and roadmap sequence

| Prerequisite | Why it matters |
|---|---|
| Linux shell, permissions, processes, logs | Inspect services, configuration, and server logs. |
| HDFS: NameNode, DataNodes, blocks, replication, HA | HBase stores durable files in HDFS in a conventional on-premises deployment. |
| YARN and distributed processing | Bulk-load preparation and Spark jobs may run as distributed Hadoop jobs. HBase RegionServers are not YARN containers. |
| MapReduce and Spark | Useful for exports, bulk-load pipelines, and analytical processing. |
| NoSQL/distributed databases (Module 2C.1) | Provides the comparison baseline for wide-column models, partition keys, and consistency. |
| Python, bytes, exceptions, virtual environments | HBase keys and values are bytes; Python clients must match the actual Thrift endpoint. |

**Roadmap sequence:** HDFS → YARN → MapReduce/Spark → Hive → HBase → legacy ingestion/orchestration → Hadoop-to-lakehouse migration. HBase follows Hive because they solve different access problems: Hive commonly scans and aggregates large datasets, while HBase serves keyed, low-latency reads and writes. The next topic covers Sqoop, Flume, and Oozie; the final topic covers migration and validation.

## 3. What HBase is—and why Hadoop needed it

Apache HBase is a distributed, sparse, persistent, sorted, wide-column NoSQL database modeled after Google's Bigtable design. It supports large tables with row-key-based random reads and writes across a cluster.

HDFS is excellent at storing large files and streaming them through batch jobs. It is not, by itself, a database API for efficiently updating one logical record or looking up a row by key. An application that needs one user's current profile, to append an event, or to fetch a small range should not have to scan a multi-terabyte file.

HBase adds a serving layer:

- **HDFS** stores durable HBase data files and WAL files in a typical Hadoop deployment.
- **HBase** manages table metadata, row-key ordering, regions, writes, reads, versions, and compaction.
- **Spark/MapReduce** can process large datasets in parallel, including HBase data, but are not substitutes for HBase's point-read API.
- **Hive** is primarily a SQL analytics layer, not a replacement for HBase's row-level serving path.

### 3.1 Good-fit workloads

- User profiles, device state, or account attributes fetched by a known key.
- Time-ordered events per user/device when the key supports the required range query.
- Large sparse tables where different rows contain different qualifiers.
- High write throughput with predictable row-key or range access patterns.
- Legacy Hadoop systems needing random access to distributed data.

### 3.2 Poor-fit workloads

- Ad hoc relational joins and arbitrary SQL predicates without a designed key.
- Workloads that routinely scan the entire table for analytics.
- Applications needing many secondary indexes unless an additional indexing/query layer is designed and operated.
- Tiny datasets where distributed-cluster overhead dominates.
- Workloads whose access patterns cannot be expressed efficiently with row keys, row ranges, and family/qualifier selection.

**Key distinction:** HBase does not automatically index every column like a conventional relational database. Its primary access structure is the sorted row key. A filter on a non-key column may still require scanning many rows.

## 4. Architecture: components and request path

### 4.1 Main components

| Component | Responsibility |
|---|---|
| **HMaster** | Coordinates administrative operations such as table creation, region assignment, balancing, and recovery. It is not normally in the data path for every `Get` or `Put`. |
| **RegionServer** | Serves reads/writes for assigned regions; manages MemStores, StoreFiles/HFiles, caches, flushes, and compactions. |
| **Region** | A contiguous range of sorted row keys for one table. Regions split as they grow and are assigned to RegionServers. |
| **`hbase:meta`** | System table containing region metadata used by clients and cluster services to locate regions. |
| **ZooKeeper** | In common deployments, coordinates service discovery and cluster coordination. Exact responsibilities vary by HBase version and configuration. |
| **HDFS** | Stores HFiles, WALs, and durable filesystem state in a conventional HDFS-backed cluster. |
| **HBase client** | Locates the region for a row key, sends RPCs to RegionServers, and handles movement/retries according to client behavior. |

HMaster is important for cluster control, but ordinary reads/writes go directly to the RegionServer hosting the region after location is resolved.

### 4.2 Logical architecture

```text
Application / HBase client
          |
          | locate region (cache + hbase:meta as needed)
          v
    RegionServer RPC
          |
          +---- read ----> MemStore / BlockCache / HFiles
          |
          +---- write ---> WAL + MemStore
                              |
                              | flush
                              v
                            HFiles
                              |
                              v
                             HDFS

HMaster ---- assigns/moves regions, balances cluster, manages tables
ZooKeeper - coordination/service discovery (deployment/version dependent)
HDFS ------ durable files and replication; not the row-level database API
```

### 4.3 Request path

1. The client uses configuration and cluster metadata to find the RegionServer responsible for the row key.
2. It sends the request directly to that RegionServer.
3. The RegionServer serves from in-memory structures or durable HFiles, as appropriate.
4. If a region moved or split, the client refreshes location information and retries within its configured limits.

HMaster is not a mandatory proxy for every data request. This separation avoids making the master the normal throughput bottleneck.

### 4.4 Regions and sorted ranges

```text
Table: events_by_user
Region A: [start, "user#40...")
Region B: ["user#40...", "user#80...")
Region C: ["user#80...", end)
```

The boundaries are illustrative and may change. A split creates daughter regions with smaller key ranges; it does not create a different logical table.

### 4.5 HBase and HDFS have different responsibilities

HBase generally stores HFiles and WAL files in HDFS. HDFS replicates blocks and provides filesystem durability; HBase organizes cells into sorted files and implements database behavior.

Do not manually rename, delete, or edit HBase-managed files in its HDFS directory. Use supported HBase tools for snapshots, restores, exports, and bulk loads.

## 5. HBase data model

HBase is called a wide-column store, but it is not a relational table with a fixed set of columns, nor is it identical to Cassandra's CQL model.

### 5.1 Table, row key, family, qualifier, cell

- **Table:** named collection of rows.
- **Row key:** unique key stored as bytes and ordered lexicographically by HBase's byte comparison. Its design determines efficient access and distribution.
- **Column family:** schema-defined group of qualifiers configured at table creation or alteration. Families are stored and managed separately.
- **Column qualifier:** column name within a family. Qualifiers are flexible and need not be predeclared individually.
- **Cell:** value at the intersection of row key, family, qualifier, and timestamp/version.
- **Timestamp/version:** a cell can retain multiple versions. A simple `get` normally returns the newest visible version unless version selection is requested.

A cell can be described as:

```text
(row key, family:qualifier, timestamp) -> value bytes
```

For example:

```text
("user#0042", "p:name", 1792400000000) -> "Mina"
("user#0042", "p:city", 1792400000000) -> "Pune"
("user#0042", "e:last_event", 1792400100000) -> "login"
```

HBase stores values as bytes. Applications are responsible for consistent encoding/decoding of strings, numbers, JSON, Avro, or other representations.

### 5.2 Sparse rows and flexible qualifiers

```text
row user#0042:
  p:name = Mina
  p:city = Pune
  e:last_event = login

row user#0043:
  p:name = Arjun
  p:preferred_language = en
  e:last_event = purchase
```

The row is sparse: a missing qualifier is not the same as an empty string. Applications should define how they distinguish absent, empty, deleted, and unknown values.

### 5.3 Versioned cells

When a family retains multiple versions, writes to the same row/family/qualifier can leave multiple timestamped versions, subject to version-retention configuration and compaction/deletion behavior.

```text
hbase> put 'user_events', 'user#0042', 'p:name', 'Mina', 1792400000000
hbase> put 'user_events', 'user#0042', 'p:name', 'Mina S', 1792400100000
hbase> get 'user_events', 'user#0042', {COLUMN => 'p:name', VERSIONS => 3}
```

These timestamps are illustrative. Choose a timestamp strategy deliberately. Client-supplied timestamps are useful for replay/backfill, but out-of-order or duplicate timestamps can change which version is visible. Consider clock skew, event time, and retry behavior.

A family configured with `VERSIONS => 1` retains one version for ordinary reads after cleanup/compaction rules apply; do not treat this as a permanent audit-history mechanism. Define retention explicitly if business history must be retained.

### 5.4 Column-family design trade-offs

Families are physical and operational boundaries, not just labels.

- Use a small number of families, often one or a few, rather than a family for every logical field.
- Group qualifiers with similar access patterns, retention, compression, and performance requirements.
- Define families before a large load; alter family design only with a migration/alteration plan.
- Each family has Store/MemStore-related structures and StoreFiles; too many families increase memory, file, flush, and compaction overhead.
- Avoid grouping unrelated high-churn and cold data when their retention/access requirements differ materially.
- Do not treat families as indexes. A qualifier is not automatically a secondary index.

Example:

| Family | Example qualifiers | Reason |
|---|---|---|
| `p` (profile) | `name`, `city`, `tier` | Small profile attributes commonly fetched together. |
| `e` (event) | `type`, `payload`, `source` | Event attributes with a separate access/retention pattern. |

This is a teaching example, not a universal recommendation. For append-only events, storing each event as a separate row may be better than repeatedly overwriting fields in a profile row.

## 6. HBase shell: create, put, get, scan, delete

The commands use consistent names. They assume a compatible shell connected to a test cluster and sufficient table permissions. Syntax and options can vary across HBase releases and vendor distributions; check the reference guide for the installed version.

### 6.1 Create a table with two families

```text
hbase> create 'user_events', {NAME => 'p', VERSIONS => 1}, {NAME => 'e', VERSIONS => 3}

hbase> describe 'user_events'
hbase> list
```

### 6.2 Insert rows

```text
hbase> put 'user_events', 'user#0042', 'p:name', 'Mina'
hbase> put 'user_events', 'user#0042', 'p:city', 'Pune'
hbase> put 'user_events', 'user#0042', 'e:type', 'login'
hbase> put 'user_events', 'user#0042', 'e:event_time', '2026-10-19T09:00:00Z'

hbase> put 'user_events', 'user#0043', 'p:name', 'Arjun'
hbase> put 'user_events', 'user#0043', 'p:city', 'Kolkata'
hbase> put 'user_events', 'user#0043', 'e:type', 'purchase'
```

The shell stores literal values as bytes. Numeric values used for comparisons/sorting need deliberate binary or string encoding; text strings are not automatically parsed as numbers.

### 6.3 Retrieve and scan

```text
hbase> get 'user_events', 'user#0042'
hbase> get 'user_events', 'user#0042', {COLUMN => 'p'}
hbase> get 'user_events', 'user#0042', {COLUMN => 'e:type'}

hbase> scan 'user_events'
hbase> scan 'user_events', {COLUMNS => ['p:name', 'e:type']}
hbase> scan 'user_events', {STARTROW => 'user#0042', STOPROW => 'user#0044'}
```

HBase scans are ordered by row key. A bounded range is usually much more efficient than a whole-table scan. Check stop-row boundary semantics and filter syntax against the deployed version when designing exact range queries. Selecting a family/qualifier reduces returned data; it does not create a secondary index.

### 6.4 Delete a cell or row

```text
hbase> delete 'user_events', 'user#0042', 'p:city'
hbase> deleteall 'user_events', 'user#0043'
```

`delete` removes a cell/version according to command semantics; `deleteall` is a separate shell command for removing all cells in a row. Verify behavior before use. Delete markers (tombstones) may remain until compaction and retention rules remove obsolete data. A successful delete does not mean old bytes immediately disappear from every HFile.

**Safety:** use destructive commands only in a disposable lab or after reviewing table, row, and authorization scope.

## 7. Row-key design: the most important modeling decision

HBase sorts rows lexicographically by row-key bytes. This enables efficient point lookups and contiguous range scans, but a poor key can create uneven load or make required queries expensive.

A good row key balances:

1. **Query locality:** related rows should be retrievable with a bounded key range.
2. **Write distribution:** concurrent writes should not all target one region.
3. **Uniqueness:** distinct logical records need distinct keys.
4. **Ordering:** key encoding should sort the way the application expects.
5. **Size:** row keys are repeated in storage and RPCs; keep them compact but understandable.
6. **Evolution:** the key must remain parseable and stable across application changes.

### 7.1 Events by user, newest first

Suppose the dominant query is: “Return the newest events for user `u123`.” A useful logical key is:

```text
user_id # reverse_timestamp # event_id
```

Where `reverse_timestamp = MAX_FIXED_WIDTH_TIMESTAMP - event_timestamp`. `event_id` breaks ties so two events at the same timestamp do not collide. If timestamps are decimal strings, reverse them numerically and pad to a fixed width; do not reverse the timestamp's characters.

```python
MAX_TS = 9_999_999_999_999  # illustrative 13-digit timestamp domain

def event_row_key(user_id: str, event_time_ms: int, event_id: str) -> bytes:
    if not 0 <= event_time_ms <= MAX_TS:
        raise ValueError(f"event_time_ms must be between 0 and {MAX_TS}")
    if not user_id or "#" in user_id or not event_id or "#" in event_id:
        raise ValueError("user_id and event_id must be non-empty and must not contain '#'")
    reverse_ts = MAX_TS - event_time_ms
    return f"{user_id}#{reverse_ts:013d}#{event_id}".encode("utf-8")
```

Because the reversed timestamp gets smaller as event time gets newer, lexicographic order within a user prefix places newer events first, provided the timestamp encoding is fixed-width and the timestamp range is valid. A query can scan the user's prefix and stop after enough rows.

The design gives locality for per-user reads, but does not automatically distribute writes evenly: all rows for one user share a prefix, and a very active user can be hot. If writes arrive globally in monotonically increasing timestamp order, a key beginning with the timestamp can direct most new writes to the current end of the keyspace.

### 7.2 Hotspot formation

A hotspot occurs when a small number of regions or RegionServers receive a disproportionate share of requests or bytes. Symptoms include elevated p95/p99 latency, uneven request rates, write queues, flush/compaction pressure, and one RegionServer being much busier than peers.

Common causes:

- Keys start with a monotonically increasing timestamp or sequence.
- A single tenant/user receives most writes.
- All clients use one fixed prefix.
- A range scan repeatedly targets the same region.
- A few oversized rows or large values dominate I/O.

Region splitting does not guarantee that a hotspot disappears. A monotonically increasing key may simply make the newest writes land in the newest daughter region.

### 7.3 Salting

Add a small shard prefix:

```text
salt # user_id # reverse_timestamp # event_id
```

Example deterministic salt:

```python
import hashlib

def stable_salt(user_id: str, shards: int = 16) -> str:
    digest = hashlib.sha256(user_id.encode("utf-8")).digest()
    return f"{digest[0] % shards:02d}"
```

This spreads different users, but does **not** split one extremely hot user's writes across shards. For that case, derive the shard from event ID or another high-cardinality value, while preserving queryability.

Trade-offs:

- More evenly distributed writes may require query fan-out.
- A query for one user may scan every salt bucket, merge results, and preserve newest-first order across buckets.
- Salt count is a data-model choice; changing it later may require dual-read logic or migration.
- Salting changes row-key layout and range/prefix access. It does not preserve every existing query automatically.

### 7.4 Hashing, reversing, and composite keys

**Hashing:** a hash prefix spreads keys across the keyspace. Hashing the entire key distributes writes but destroys natural locality for user/time queries. A hash prefix followed by the logical key preserves some locality within each shard, but queries must know which shards to inspect. Hashing a tenant ID distributes tenants, not writes within one dominant tenant.

**Reverse timestamp:** useful for newest-first ordering within a logical prefix. It does not by itself spread writes if the logical prefix is fixed and current writes remain concentrated in one range.

**Reverse identifier:** reversing a domain name or identifier can change prefix distribution for some datasets, but can make common queries less natural. Test the actual key distribution.

**Composite key:** concatenate stable components with an unambiguous delimiter or length-prefix encoding. Escape delimiters or ensure they cannot occur in components; otherwise parsing collisions can occur. For binary keys, define byte order and encoding explicitly.

### 7.5 Strategy comparison

| Strategy | Helps with | Costs / risks |
|---|---|---|
| `timestamp#id` | Time-range scans | Monotonically increasing writes can hotspot the newest region. |
| `user#reverse_timestamp#id` | Newest-first events per user | One hot user may still dominate one region. |
| `salt#user#reverse_timestamp#id` | Spreads writes across salt buckets | User query fans out across buckets and results must be merged. |
| `hash(user)#user#timestamp#id` | Spreads different users | Does not split one hot user's writes; global time scans become difficult. |
| `hash(event_id)#user#timestamp#id` | Can split one hot user's event writes | Querying one user's newest events requires multi-shard fan-out and merge. |

### 7.6 Validate a key design

- Generate representative keys, including peak traffic and skewed tenants.
- Count writes per salt/prefix and estimate distribution.
- Test point lookups, bounded scans, newest-first ordering, duplicate timestamps, and pagination.
- Estimate query fan-out and merge cost after salting.
- Verify that region split points can be pre-created or adjusted if needed.
- Record a migration strategy if the row-key design may change.

## 8. Write path: WAL, MemStore, HFiles

### 8.1 Conceptual write flow

```text
Client Put/Delete
       |
       v
RegionServer validates/routes mutation
       |
       +----> Write-Ahead Log (WAL) ----> durable log files on HDFS
       |
       +----> MemStore (in-memory, per Store/family)
                         |
                         | threshold / pressure / flush request
                         v
                    immutable HFile(s)
                         |
                         v
                        HDFS
```

Exact internals, buffering, acknowledgment rules, and WAL implementation depend on HBase version and configuration. The invariant is that the WAL records mutations so they can be recovered if a RegionServer fails before MemStore data is flushed to HFiles.

### 8.2 WAL durability

The Write-Ahead Log records mutations before they are considered safely represented in the in-memory write path. If a RegionServer fails before a flush, recovery replays relevant WAL edits to reconstruct unflushed data. If the WAL write fails, the mutation should fail rather than be acknowledged as though durable.

Do not assume every write has identical latency or durability settings. HBase exposes write durability options and configuration controls; changing them can affect acknowledged-write guarantees. Relaxed durability must be an explicit application-level decision supported by a documented recovery-point objective.

### 8.3 MemStore and HFiles

Each Store maintains in-memory updates for a column family within a region. Reads must account for current MemStore data as well as older persisted StoreFiles, so a recent successful write can be visible before the next HFile flush.

When MemStore pressure or configured thresholds trigger a flush, HBase writes sorted data to HFiles in HDFS. HFiles are immutable sorted storage files. Updates accumulate in memory and later create new files; compaction merges files and applies retention/deletion cleanup as appropriate. This supports high write throughput but creates ongoing file-management work.

### 8.4 Compaction

- **Minor compaction:** merges some StoreFiles, often reducing file count; it does not necessarily rewrite all files or remove every obsolete cell.
- **Major compaction:** rewrites all eligible StoreFiles in a Store and can apply version/tombstone cleanup, subject to retention and configuration. It is I/O-intensive and should not be triggered casually across a large production cluster.

Compaction affects disk I/O, read amplification, write amplification, CPU, temporary space, and latency. It is a normal operational process, not simply a repair action.

### 8.5 Region splits

As regions grow beyond configured policies/thresholds, HBase may split a region into daughter regions. Splits change the mapping from row-key ranges to regions and can temporarily add I/O and metadata activity. Pre-splitting can help a known write distribution at initial load, but poor split points can create imbalance. Splitting alone does not fix bad key design.

## 9. Read path: MemStore, BlockCache, Bloom filters, HFiles

### 9.1 Conceptual read flow

```text
Client Get / Scan
       |
       v
RegionServer + region's Stores
       |
       +--> relevant MemStore data
       |
       +--> BlockCache for HFile blocks
                    |
             cache hit? ---- yes ---> cached block
                    |
                    no
                    v
             read relevant HFile block from HDFS
       |
       v
Merge/filter versions and return requested cells
```

This is conceptual; exact call ordering and optimizations vary by version and read type. A read may consult several StoreFiles and merge cells according to timestamps, deletes, filters, and version limits.

### 9.2 BlockCache

BlockCache holds frequently accessed HFile blocks in memory to reduce repeated storage reads. Effectiveness depends on working-set size, access locality, cache configuration, and competition with MemStore/JVM/off-heap memory. High read I/O and latency can indicate poor cache behavior, but a low hit rate is not automatically a bug when random access exceeds the cache's working set.

### 9.3 Bloom filters

Bloom filters can help determine that an HFile does not contain a requested row or row/column combination, depending on configuration. A negative result can avoid an unnecessary HFile lookup; a positive means “possibly present,” not “definitely present.” False positives are possible. Bloom filters do not create a general secondary index and do not make arbitrary non-key predicates efficient.

### 9.4 Filters and scans

Filters can restrict rows/cells returned by a scan, reducing result volume and sometimes enabling server-side evaluation. They do not necessarily eliminate underlying row traversal. A filter on a non-key column can still require visiting many rows, so constrain the scan by row-key range whenever possible. Exact filter names, combinations, and shell syntax vary by release.

- `Get` by complete row key is the natural point-read path.
- A bounded `Scan` over a contiguous row-key range can be efficient.
- A full-table scan is expensive and can compete with serving traffic.
- Filtering after a broad scan is not equivalent to an index lookup.

For analytical queries, export/read into Spark or lakehouse storage when appropriate rather than repeatedly running large scans against a latency-sensitive HBase cluster.

## 10. Region management, balancing, and troubleshooting

### 10.1 Balancing

HMaster's balancer can move regions between RegionServers. Equal region counts do not guarantee equal traffic: one region can be much hotter than ten quiet regions. Before changing balancing settings, inspect request rate, read/write latency, region size, StoreFile count, compaction queues, and traffic skew. Rebalancing cannot compensate for fundamentally poor row-key design.

### 10.2 Symptoms and investigation

| Symptom | Possible causes | Investigation |
|---|---|---|
| One RegionServer has high CPU/request rate | Hot region, hot prefix, skewed tenant, scan-heavy client | Compare per-region/per-server request rates; inspect key distribution and client patterns. |
| Write latency rises periodically | MemStore flush pressure, WAL latency, compaction backlog, HDFS/DataNode latency | Correlate latency with flush/compaction metrics, WAL errors, and HDFS health. |
| Read latency rises after data growth | BlockCache pressure, many StoreFiles, broad scans, cold working set | Inspect cache hit/miss, file counts, scan ranges, and I/O latency. |
| Many StoreFiles or compaction backlog | High write rate, frequent flushes, insufficient compaction throughput | Review MemStore/flush settings and compaction metrics; change one setting at a time. |
| Region count/size is uneven | Skewed keyspace, splits, uneven traffic, assignment | Inspect boundaries and load, not just region count. |
| Client errors after region movement | Stale location cache, network failures, retries exhausted, incompatible config | Inspect client/RegionServer logs, assignment state, and network path. |
| WAL/recovery errors | HDFS failure, disk pressure, permissions/configuration, failed RegionServer | Follow deployment recovery runbook; never delete WAL files manually. |

### 10.3 Disciplined troubleshooting sequence

1. Define the failure: table, family, row-key range, client, start time, latency percentile, and error.
2. Check cluster health: HMaster/RegionServer state, region assignment, HDFS health, free space, recent failures.
3. Check skew: requests/bytes by RegionServer and region, hot prefixes, tenant distribution.
4. Check storage pressure: MemStore, flush queues, StoreFile counts, compaction queues, HDFS latency.
5. Check read efficiency: BlockCache, Bloom filter usefulness, broad scans, unnecessary returned columns.
6. Check client behavior: connection reuse, retry storms, scan caching/batching, request size, timeouts.
7. Change one variable at a time, record before/after metrics, and define rollback criteria.
8. Use the distribution's runbooks for reassignment, major compaction, WAL recovery, and cluster-wide changes.

Do not copy tuning values from another cluster without evidence. Tuning depends on version, workload, hardware, and distribution.

## 11. Coprocessors, filters, and Apache Phoenix

### 11.1 Coprocessors

Coprocessors allow code to execute within HBase server-side lifecycle or as endpoint services, depending on type. They can reduce round trips but execute inside a trusted server process. Validate exact HBase compatibility, class loading/dependencies, upgrade/rollback, CPU/memory impact, authorization, and failure isolation. Treat coprocessor JARs as privileged code; do not install arbitrary JARs on shared production clusters.

### 11.2 Filters

Filters are often a safer first option when an operation can be expressed as row/cell filtering during a scan. They reduce returned data but do not provide arbitrary indexing or guarantee irrelevant rows will not be visited.

### 11.3 Apache Phoenix

Apache Phoenix provides a SQL layer over HBase, including SQL-oriented schemas and query planning. It can simplify selected applications, but does not turn HBase into a general relational engine with unlimited joins and indexes at no cost. Verify exact Phoenix/HBase/JDK compatibility, indexing and transaction behavior, and operational constraints. Include Phoenix metadata and index maintenance in a migration plan.

## 12. Python through Thrift and HappyBase

HBase's native client ecosystem is Java-oriented. Python can access HBase through the Thrift gateway. **HappyBase is a third-party Python wrapper over Thrift, not an Apache-maintained HBase client.** It is useful for learning and carefully validated integrations, but protocol, transport, Python dependency, authentication, TLS, and server compatibility must be checked before production use.

### 12.1 Prerequisites

- Running HBase cluster and a Thrift gateway enabled by an administrator.
- Host, port, transport/protocol, and authentication settings matching the gateway.
- Compatible `happybase` and `thrift` packages.
- Network access restricted to trusted application hosts.
- Test table and non-privileged account.
- For Kerberos/TLS/proxy-user deployments, verify that the gateway and Python client support the required security path. Do not assume a plain HappyBase connection provides production-grade authentication or encryption.

The conventional Thrift port is often `9090`, but do not assume it is open or configured identically in every distribution.

Example environment setup (pin versions only after testing them against your gateway):

```bash
uv init hbase-python-lab
cd hbase-python-lab
uv add happybase
```

### 12.2 Basic connection and read/write

Assume the gateway is configured for the matching transport/protocol and `user_events` exists with families `p` and `e`.

```python
from __future__ import annotations

import os
import happybase

host = os.environ.get("HBASE_THRIFT_HOST", "localhost")
port = int(os.environ.get("HBASE_THRIFT_PORT", "9090"))

connection = happybase.Connection(
    host=host,
    port=port,
    timeout=10_000,  # HappyBase documents timeout in milliseconds
    autoconnect=True,
    transport="buffered",
    protocol="binary",
)

try:
    table = connection.table("user_events")
    table.put(
        b"user#0042",
        {
            b"p:name": b"Mina",
            b"p:city": b"Pune",
            b"e:type": b"login",
        },
    )

    row = table.row(b"user#0042")
    print(row.get(b"p:name"))
    print(row.get(b"e:type"))

    for row_key, cells in table.scan(row_prefix=b"user#"):
        print(row_key, cells)
finally:
    connection.close()
```

This teaching example does not configure TLS, Kerberos, retries, structured logging, connection pooling, schema migration, or application-level validation. Do not put credentials in source code; use a secret-management system.

### 12.3 Bytes and production considerations

```python
name = "Mina"
row_key = "user#0042".encode("utf-8")
value = name.encode("utf-8")
decoded_name = value.decode("utf-8")
```

For structured data, define a stable serialization format and schema-evolution policy. Do not assume a value written as text `"42"` is stored as an integer.

Production checklist:

- Reuse connections appropriately; test connection-pooling behavior before concurrent use.
- Set timeouts, bounded retries, and idempotency behavior.
- Batch writes when appropriate, while bounding batch size and understanding failures.
- Match the Thrift server's transport/protocol to client settings.
- Confirm client compatibility against the deployed HBase version and vendor distribution.
- Validate authentication/TLS and authorization with the security team.
- Test the actual dependency set in CI; package installation does not prove wire-protocol compatibility.

Alternatives include the Java HBase client, a version-compatible Spark connector/HBase API, a generated Thrift client, or a REST gateway where its trade-offs fit. The Java API is the most direct HBase-native option; generated Thrift code is more verbose and still requires protocol management.

## 13. Spark-HBase integration

Spark and HBase complement one another: HBase serves online key/range access; Spark processes large datasets and can read/write HBase through compatible connectors/APIs; a lakehouse is often better for repeatable analytical scans, SQL joins, historical reporting, and data science.

### 13.1 Compatibility is a deployment requirement

There is no universal “add the connector” instruction. Check the exact HBase, Spark, Scala binary, Hadoop, JDK, shaded-client dependency, and security combination. Connector artifacts may be released separately from HBase core. Follow official connector release notes and make required configuration such as `hbase-site.xml` available to Spark.

### 13.2 Safe integration pattern

1. Start with a small table and bounded row-key range.
2. Use a compatible connector or HBase input API.
3. Reuse one HBase connection per Spark partition/task where appropriate, not per row.
4. Bound scan size and parallelism so analytics do not overwhelm serving traffic.
5. For large loads, evaluate bulk-load workflows that generate HFiles and load them with supported HBase tools instead of millions of individual RPC writes.
6. Design for retries and idempotency: Spark task retries can repeat writes.
7. Compare source/output counts, key coverage, and representative values.

### 13.3 Snapshot-based Spark reading

A snapshot is not generic Parquet/CSV. It captures table metadata and references to HFiles. `ExportSnapshot` copies snapshot-related files and metadata between compatible HBase filesystem/root locations; it does not convert data into an arbitrary Spark source. Spark must use an HBase-aware reader or convert through a supported pipeline to Parquet/Iceberg.

The following Scala example illustrates a distributed read with HBase 2.x's `TableSnapshotInputFormat` and Spark's `newAPIHadoopRDD`. Treat it as a **version-pinned template**, not a universal drop-in: compile and test it against the exact HBase, Hadoop, Spark, Scala, and JDK versions deployed. It assumes the snapshot named below is visible under the configured `hbase.rootdir` (for example, after `ExportSnapshot`), and that the job identity can read the snapshot/HFiles and write to the temporary restore and output paths.

```scala
import org.apache.hadoop.fs.Path
import org.apache.hadoop.hbase.{CellUtil, HBaseConfiguration}
import org.apache.hadoop.hbase.client.Result
import org.apache.hadoop.hbase.io.ImmutableBytesWritable
import org.apache.hadoop.hbase.mapreduce.TableSnapshotInputFormat
import org.apache.hadoop.hbase.util.Bytes
import org.apache.hadoop.mapreduce.Job
import org.apache.spark.sql.Row
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types._

val spark = SparkSession.builder().appName("HBaseSnapshotToParquet").getOrCreate()

// Use the exported snapshot's HBase root, not a directory containing only copied HFiles.
val conf = HBaseConfiguration.create(spark.sparkContext.hadoopConfiguration)
conf.set("hbase.rootdir", "hdfs://target-namenode:8020/hbase")
val job = Job.getInstance(conf)
val snapshotName = "user_events_lab_snapshot"
// Must be writable by the job identity and must NOT be under hbase.rootdir.
val restoreDir = new Path("hdfs://target-namenode:8020/tmp/hbase-snapshot-restore-user-events")
TableSnapshotInputFormat.setInput(job, snapshotName, restoreDir)

val cellRdd = spark.sparkContext
  .newAPIHadoopRDD(
    job.getConfiguration,
    classOf[TableSnapshotInputFormat],
    classOf[ImmutableBytesWritable],
    classOf[Result]
  )
  .flatMap { case (_, result) =>
    result.rawCells().toSeq.map { cell =>
      Row(
        Bytes.toString(CellUtil.cloneRow(cell)),
        Bytes.toString(CellUtil.cloneFamily(cell)),
        Bytes.toString(CellUtil.cloneQualifier(cell)),
        cell.getTimestamp,
        Bytes.toString(CellUtil.cloneValue(cell))
      )
    }
  }

val schema = StructType(Seq(
  StructField("row_key", StringType, nullable = false),
  StructField("family", StringType, nullable = false),
  StructField("qualifier", StringType, nullable = false),
  StructField("timestamp", LongType, nullable = false),
  StructField("value", StringType, nullable = true)
))
val cells = spark.createDataFrame(cellRdd, schema)
cells.show(truncate = false)
println(s"cell_count=${cells.count()}")
// Use a new, approved output path for each lab run; this overwrites that path.
cells.write.mode("overwrite").parquet("hdfs://target-namenode:8020/warehouse/lab/user_events_cells_parquet")
spark.stop()
```

This demonstration decodes values as UTF-8 strings because the lab data is textual. For arbitrary binary values, preserve bytes or apply the source application's actual serialization. `restoreDir` is a temporary working directory; choose a unique path and clean it only after the job completes. Snapshot files are security-sensitive: direct filesystem reads can bypass HBase-level authorization, so enforce HDFS permissions and run under an approved identity. The snapshot must not be deleted while a job is reading it.

The Spark code has not been executed here. Before running it, confirm the exact API signatures and dependencies for the selected release, configure HBase/Hadoop credentials and filesystem access, compile it, and validate cell counts and representative values against the source table.

## 14. HBase vs Cassandra vs DynamoDB

These systems are not interchangeable implementations of one architecture. Their data models, partitioning, consistency, operations, and pricing differ.

| Dimension | Apache HBase | Apache Cassandra | Amazon DynamoDB |
|---|---|---|---|
| Deployment | Commonly self-managed on Hadoop/HDFS; managed variants exist | Self-managed or managed distributions/services | AWS managed service |
| Data model | Sorted row key → families → qualifiers/cells with versions | CQL tables, partition key and clustering columns; query-oriented model | Items keyed by partition key and optional sort key; flexible attributes |
| Primary access | Row-key `Get`, ordered row ranges, scans | Partition-key queries and clustering-key ranges | Key operations and supported query/index paths |
| Partitioning | Regions hold contiguous key ranges; HFiles in HDFS in conventional deployments | Token-based partitioning and replicas | Service-managed partitioning/replication; physical internals abstracted |
| Consistency | Strong reads on primary-region path in conventional architecture; region replicas have separate semantics | Tunable consistency depending on replication and read/write consistency levels | Eventually consistent reads by default for many operations, with strongly consistent options for supported operations/regions; global tables have distinct multi-region semantics |
| Secondary access | No automatic general-purpose index; additional systems such as Phoenix may add SQL/indexing | Secondary indexes/materialized views have trade-offs; model around primary-key queries | GSI/LSI with service-specific constraints and costs |
| Transactions | Row-level atomicity for mutations; not general relational multi-row transactions | Lightweight conditional transactions have costs; not general ACID joins | Conditional writes and transactions within service-defined limits/costs |
| Operations | HDFS/HBase services, compaction, regions, capacity, upgrades, security unless managed | Replicas, repair, compaction, topology, capacity unless managed | AWS operates infrastructure; users manage keys, capacity mode, indexes, throttling, IAM, and data design |
| Cost drivers | Hardware/cluster operations, storage, replication, support, engineering/on-call | Nodes/service, replication, compaction, repair, network, staffing | Read/write requests, storage, backups, indexes, streams, replication, transfer |
| Common fit | Existing Hadoop estate, sparse tables, low-latency keyed access/range scans | Distributed applications needing its partition/clustering model and configurable consistency | AWS-native managed key-value/document workloads fitting service constraints |
| Migration risk | Preserve row-key order, versions, timestamps, deletes, and HBase metadata | Redesign primary keys/access patterns; validate consistency and repair behavior | Redesign keys/indexes and cost/capacity model; map types and conditional semantics |

### 14.1 Consistency caveats

- **HBase:** ordinary reads on the primary region path are strongly consistent in the conventional architecture. Region replicas and specialized read modes can offer different consistency/availability trade-offs.
- **Cassandra:** consistency is configurable and depends on replication factor, read/write consistency levels, and deployment. “Cassandra is eventually consistent” is an oversimplification.
- **DynamoDB:** consistency options differ by operation and region/global-table mode. Do not assume strong consistency is available for every access pattern or multi-region configuration.

Validate the actual product/version/service configuration rather than relying on a one-line label.

### 14.2 Choosing a target

- **Bigtable:** consider a managed wide-column serving model when its row-key/access model and cloud fit match.
- **Cassandra:** consider when the workload needs its partition/clustering model and the team can support the operational or managed-service model.
- **DynamoDB:** consider for AWS-native managed key-value/document workloads that fit its key/index/transaction constraints.
- **Lakehouse:** consider for analytical history, large scans, SQL joins, governance, and data science—not low-latency online serving by itself.

## 15. Snapshots, exports, bulk loads, and migration

Migration begins with access-pattern discovery, not a blind file copy.

### 15.1 HBase snapshots

A snapshot is a point-in-time table metadata view that references the HFiles making up the table. Creating a snapshot generally avoids copying all table data immediately, but snapshot retention can prevent old HFiles from being reclaimed. Snapshots are not a substitute for a complete backup/restore test or a security review.

```text
hbase> snapshot 'user_events', 'user_events_migration_2026_10'
hbase> list_snapshots
```

Before snapshotting:

- Confirm source table and namespace.
- Check disk capacity and snapshot retention policy.
- Verify operator authorization; snapshot/restore privileges depend on HBase authorization configuration.
- Document whether table ACLs, namespace permissions, encryption keys, and service identities must be recreated at the target. Snapshot data does not automatically migrate external security/governance policies.
- Record snapshot name/time, table schema, family settings, and source cluster/version.

### 15.2 ExportSnapshot

`ExportSnapshot` copies a snapshot's HFiles and metadata to another HBase root/filesystem location. It commonly runs a MapReduce-style copy job, so compatible Hadoop configuration, filesystem access, credentials, network paths, and permissions are required.

Illustrative command; substitute actual cluster URIs and verify options with the installed version:

```bash
hbase org.apache.hadoop.hbase.snapshot.ExportSnapshot \
  -snapshot user_events_migration_2026_10 \
  -copy-to hdfs://target-namenode:8020/hbase \
  -mappers 8
```

The target path should be the intended HBase root for the target cluster, not an arbitrary directory assumed to be a table export. If source/target filesystems differ, configure and validate filesystem connectors and credentials. Never copy files into a live HBase root by manually manipulating HFiles.

### 15.3 Snapshot vs export vs logical export vs bulk load

- **Snapshot:** captures table metadata and HFile references.
- **ExportSnapshot:** copies snapshot files/metadata between suitable filesystem/root locations.
- **Snapshot scanner/input format:** lets compatible HBase-aware code read snapshot data without treating it as plain text.
- **Logical export:** reads rows and writes a portable format or target database using a defined schema/serialization.
- **Bulk load:** prepares HFiles that match target HBase requirements and loads them through supported HBase tools.

For Spark, the exported snapshot must be read with a compatible HBase snapshot API/input format and matching dependencies, or converted through an HBase-aware process into Parquet/Iceberg. A raw `spark.read.parquet(...)` call will not read HFiles as Parquet.

### 15.4 Bulk loading into HBase

Bulk loading is useful for large initial loads:

1. Define target table/family schema.
2. Transform source data into correctly keyed HBase cells.
3. Generate HFiles with tools compatible with target HBase version, schema, region layout, and filesystem.
4. Load HFiles through the supported bulk-load mechanism.
5. Validate row counts, key ranges, versions, and representative values.

Bulk loading bypasses much of the ordinary per-row client write path, but has strict requirements. Do not assume HFiles generated for one version/schema can be loaded into any HBase cluster.

### 15.5 Migration plan by target

**To Bigtable**
- Map HBase row keys to Bigtable row keys and preserve key-order/access patterns.
- Map families/qualifiers and timestamps/versions to target schema and retention behavior.
- Validate import tooling for the specific service.
- Compare point reads, range scans, throughput, latency, IAM, encryption, backups, and operational limits.

**To Cassandra**
- Redesign the HBase row-key model as Cassandra partition keys and clustering columns.
- Check partition size, read/write patterns, replication factor, consistency levels, TTLs, tombstones, repair, and compaction.
- HBase cell versions do not automatically map one-to-one to Cassandra rows/versions; define the model explicitly.

**To DynamoDB**
- Map each HBase row to an item and choose partition/sort keys based on actual query patterns.
- Determine whether secondary indexes or a separate search/analytics system are needed.
- Validate item-size limits, index projection, conditional writes, throughput/throttling, and cost.
- Decide how versions and deletes map to attributes, history items, TTL, or audit storage.

**To a lakehouse**
- Preserve row key, family, qualifier, timestamp/version, and value type in an explicit schema, such as a normalized cell table or domain-oriented denormalized table.
- Define how deletes/tombstones, duplicate versions, and audit requirements are represented.
- Use Spark or another compatible HBase-aware reader to convert data to Parquet/Iceberg/Delta.
- Do not treat the lakehouse as a replacement for low-latency online reads unless an online serving layer is also designed.

### 15.6 Validation and cutover checklist

- [ ] Inventory tables, families, version settings, TTLs, row-key patterns, volumes, and query clients.
- [ ] Capture snapshots and record source schema/configuration.
- [ ] Map every critical access pattern to a target query/API.
- [ ] Define mapping for timestamps, versions, deletes/tombstones, null/missing values, and binary encodings.
- [ ] Validate counts at table and partition/key-range level.
- [ ] Compare deterministic checksums/hashes over canonicalized records.
- [ ] Compare sampled point reads, range scans, and business queries.
- [ ] Test late/out-of-order events, retries, duplicate writes, and delete behavior.
- [ ] Measure representative p50/p95/p99 latency and throughput in a controlled test; do not infer performance from architecture alone.
- [ ] Review security, encryption, identities, audit logs, backup, restore, and retention.
- [ ] Run old and new paths in parallel where feasible.
- [ ] Define cutover window, rollback criteria, and owners.
- [ ] Retain source until acceptance and rollback windows close; then plan decommissioning.

## 16. Hands-on labs

These labs are for a disposable local/training cluster. A small Docker Compose cluster may suffice for data-model and shell practice, but it is not a production performance benchmark. Images and versions are distribution-specific; pin compatible versions and follow their setup instructions. Do not expose HBase RPC or Thrift ports to untrusted networks.

### Lab 1 — Create a table with two families, insert and scan

**Goal:** Practice the data model and shell.

1. Connect to the lab HBase shell.
2. Create `user_events` with `p` and `e` families.
3. Insert at least five rows, including two events for the same user.
4. Run a full scan, a family-limited `get`, and a bounded scan.
5. Delete one cell in a test row and inspect the result.
6. Record behavior for an absent qualifier and for multiple versions.

**Evidence:** `describe 'user_events'`; output for `put`, `get`, bounded `scan`; a short explanation of point-read versus scan. **Checkpoint:** explain row key/family/qualifier and safely delete a test cell.

### Lab 2 — Sequential keys, hotspot hypothesis, and salting

**Goal:** Understand hotspots without pretending a tiny local cluster predicts production.

1. In a disposable table, load sequential keys such as `000000000001`, `000000000002`, and so on.
2. If supported, pre-split into multiple regions with documented split keys; otherwise record the limitation and use a key-distribution simulation.
3. Load a meaningful number of records at a controlled rate while observing per-region/RegionServer request rates and latency. Do not run an uncontrolled load generator.
4. Compare sequential keys with `salt#sequence` or a hash-prefix strategy.
5. Demonstrate that a query over salted keys must fan out across buckets and merge results.
6. Compare `user#reverse_timestamp#event_id` with `salt#user#reverse_timestamp#event_id`; state which query becomes harder.

A small lab may not create measurable hotspotting because it lacks enough nodes, regions, and concurrent traffic. If no cluster metrics are available, simulate lexicographic ranges and label the result as a model, not an experiment.

**Checkpoint:** explain why increasing keys can concentrate writes and why salting adds query complexity.

### Lab 3 — Snapshot export and Spark reading

**Goal:** Distinguish snapshot metadata, HFiles, and analytical formats.

1. Insert sample data into `user_events`.
2. Create a snapshot, e.g. `user_events_lab_snapshot`, and record schema/family settings.
3. Run `ExportSnapshot` to a separate compatible HBase root/filesystem location using the command for the installed version.
4. Configure Spark with compatible HBase/Hadoop dependencies, the exported root, credentials, and a writable temporary restore directory outside `hbase.rootdir`.
5. Adapt and compile the version-pinned Scala example in Section 13.3 (or use the supported HBase snapshot API for the chosen release) to transform cells into a DataFrame with row key, family, qualifier, timestamp, and value columns.
6. Alternatively, read through a compatible HBase connector and write canonical Parquet; label this a logical conversion, not direct Parquet reading of HFiles.
7. Compare expected row/cell counts and representative values; do not treat a compile or job submission as proof of data correctness.

**Checks:** confirm Spark/Scala/Hadoop/HBase/connector versions, filesystem credentials, and permissions. Do not use a raw Parquet reader on HFiles or run against production without approval.

**Checkpoint:** explain why `ExportSnapshot` is not a generic CSV/Parquet export and identify the Spark-compatible reader.

### Lab 4 — One-page migration design

Write a one-page design for moving `user_events` to Bigtable, Cassandra, DynamoDB, or a lakehouse. Include:

1. **Workload:** point reads, range scans, write-rate assumptions, size, latency goals, retention.
2. **Data mapping:** row key, families/qualifiers, timestamps/versions, tombstones/deletes, binary values, TTL.
3. **Target model:** keys, indexes, partitioning, query mapping, denormalization.
4. **Data movement:** snapshot/export, logical export, bulk load, or Spark conversion; tools and compatibility assumptions.
5. **Validation:** counts, canonical checksums, range coverage, sampled queries, late events, duplicates, deletes.
6. **Operations:** identity/security, encryption, backups/restore, monitoring, capacity/cost, on-call ownership.
7. **Cutover:** parallel run, freeze/dual-write strategy, rollback trigger, decommission criteria.
8. **Risks:** at least three specific risks, each with mitigation and owner.

**Checkpoint:** a reviewer can see how every critical access pattern is supported and how correctness will be proven.

## 17. Common mistakes

- Treating HBase as a relational database with automatic indexes on every column.
- Choosing a row key only for write speed, then discovering reads require full-table scans.
- Using a monotonically increasing timestamp as the leading key without analyzing write distribution.
- Assuming salting is free; it changes query access and often requires fan-out/merge.
- Hashing a tenant ID and assuming it splits one hot tenant's traffic.
- Creating too many families or using families as a substitute for logical schema design.
- Treating WAL, MemStore, and HFiles as interchangeable layers.
- Triggering major compactions or region moves without checking load and capacity.
- Assuming Bloom filters create secondary indexes or guarantee faster scans.
- Running broad analytical scans against latency-sensitive serving traffic without workload isolation.
- Assuming `ExportSnapshot` creates Parquet/CSV or a database-independent export.
- Assuming a connector built for one Scala/HBase/Spark version works with another.
- Using HappyBase in production without checking Thrift protocol, transport, authentication, TLS, and dependencies.
- Assuming snapshots migrate ACLs, IAM, encryption keys, or all governance metadata.
- Simplifying consistency as “Cassandra is eventually consistent” or “DynamoDB is always strongly consistent.”
- Treating a tiny local cluster as a production throughput benchmark.

## 18. Interview questions with model answers

**Q1. Why was HBase needed in Hadoop?** HDFS/MapReduce are strong for large-file storage and batch processing, but do not provide a convenient low-latency row-level random read/write API. HBase adds a sorted wide-column database for keyed lookups and ranges.

**Q2. Does every HBase read pass through HMaster?** No. The client locates a region, commonly using cached metadata and `hbase:meta`, then sends the request directly to the hosting RegionServer. HMaster coordinates administration and region assignment.

**Q3. Family versus qualifier?** A family is a schema-defined physical/operational grouping with settings such as versions and storage behavior. A qualifier is a flexible column name within the family.

**Q4. Why is row-key design important?** It determines lexicographic order, range locality, and request distribution. It affects whether queries are point lookups or bounded scans and whether writes hotspot a narrow range.

**Q5. How retrieve newest events per user?** Use `user_id#reverse_timestamp#event_id`, with fixed-width `MAX_TIMESTAMP - event_timestamp`. Scan the user prefix. If that user becomes hot, shard/salt may help but reads fan out and results must be merged.

**Q6. Why can monotonically increasing keys hotspot?** New keys sort at one end, concentrating inserts on the region owning that range. Splits may leave newest writes concentrated in the newest region.

**Q7. What does WAL do?** Records mutations so they can be replayed if a RegionServer fails before MemStore data is flushed to HFiles. It is a recovery path, not the final sorted-file representation.

**Q8. What happens during a MemStore flush?** Buffered updates are written as new immutable HFiles. Many small flushes can create many StoreFiles and increase compaction work.

**Q9. Minor versus major compaction?** Minor compaction merges some StoreFiles. Major compaction rewrites all eligible files for a Store and can apply version/tombstone cleanup subject to policy; it is I/O-intensive.

**Q10. What does a Bloom filter do?** It can rule out that an HFile contains a row or row/column combination, avoiding some file lookups. A positive means “possibly present”; it is not a secondary index.

**Q11. Does a filter make a full scan cheap?** Not necessarily. It can reduce results but may still traverse many rows. Constrain by row-key range first.

**Q12. HBase versus Cassandra?** HBase uses sorted row-key ranges served by regions and commonly HDFS; Cassandra uses partition/clustering keys distributed by token partitioning with replication and configurable consistency. Their schema, repair, compaction, consistency, and operations differ.

**Q13. HBase versus DynamoDB?** DynamoDB is an AWS managed service with partition/sort keys, index options, and service-specific capacity/transaction/consistency semantics. Migration requires modeling queries and constraints, not just copying bytes.

**Q14. What does `ExportSnapshot` export?** Snapshot-related HFiles and metadata to a suitable filesystem/HBase root. It does not create CSV or Parquet; use an HBase-aware reader or logical conversion.

**Q15. What check before HappyBase?** Verify Thrift gateway version, transport/protocol, Python/Thrift dependencies, timeout/retry behavior, authentication, TLS, and server configuration. Package installation does not prove production compatibility.

**Q16. Why might HBase be wrong for a new workload?** Ad hoc SQL joins, broad analytical scans, complex transaction needs, or minimal-operations managed-service goals may fit another database or lakehouse better. Choose from access patterns, consistency, scale, team capability, and TCO.

## 19. Final self-assessment checklist

### Foundations and architecture
- [ ] Explain HBase relative to HDFS, Hive, MapReduce, and Spark.
- [ ] Draw the client → region lookup → RegionServer data path.
- [ ] Explain HMaster, RegionServers, regions, `hbase:meta`, ZooKeeper, and HDFS.
- [ ] Explain why HBase is not a general relational database with automatic secondary indexes.

### Data model and shell
- [ ] Explain row keys, families, qualifiers, cells, timestamps, and versions.
- [ ] Explain why too many families can hurt operations.
- [ ] Create a two-family table and run `put`, `get`, `scan`, and `delete` safely.
- [ ] Explain tombstones and why delete may not immediately reclaim physical bytes.

### Row keys and storage internals
- [ ] Design a key for newest-first events per user.
- [ ] Explain hotspots and distinguish hot tenants from increasing keys.
- [ ] Explain salting/hash trade-offs and query fan-out.
- [ ] Trace writes through WAL/MemStore/HFiles and reads through MemStore/BlockCache/HFiles.
- [ ] Explain Bloom filters, flushes, compactions, region splits, and balancing.

### Python and integrations
- [ ] Connect to a test Thrift gateway with explicitly compatible configuration.
- [ ] Explain byte encoding and third-party wrapper versus official client.
- [ ] Verify Spark/HBase/Scala/Hadoop connector compatibility.
- [ ] Explain why snapshots require an HBase-aware reader, not a generic Parquet reader.

### Migration
- [ ] Compare HBase, Cassandra, and DynamoDB without collapsing their consistency/operational differences.
- [ ] Explain snapshot versus `ExportSnapshot` versus logical export versus bulk load.
- [ ] Write a migration design with mapping, validation, security, cutover, rollback, and cost risks.
- [ ] Identify compatibility assumptions requiring verification against the actual distribution.

## 20. Technical references and version discipline

Use documentation for the exact HBase and Hadoop versions installed. Vendor distributions may backport changes or alter supported integrations.

- Apache HBase Reference Guide: https://hbase.apache.org/book.html
- Apache HBase architecture: https://hbase.apache.org/docs/architecture/
- Apache HBase RegionServer/WAL documentation: https://hbase.apache.org/docs/architecture/regionserver/
- Apache HBase backup and snapshots: https://hbase.apache.org/docs/operational-management/backup-and-snapshots/
- Apache HBase snapshot scanning (`TableSnapshotInputFormat` / `TableSnapshotScanner`): https://hbase.apache.org/docs/architecture/snapshot-scanner/
- Apache HBase security and data access: https://hbase.apache.org/docs/security/data-access/
- Apache HBase and Spark: https://hbase.apache.org/docs/spark/
- Apache HBase connectors repository: https://github.com/apache/hbase-connectors
- HappyBase documentation: https://happybase.readthedocs.io/en/latest/

**Version note:** shell syntax, snapshot/export options, WAL implementation, ZooKeeper responsibilities, connector artifacts, and client security behavior can differ by release and distribution. Confirm the deployed version, supported JDK, exact connector artifact, Thrift mode, and authorization model before applying commands to a real cluster. No benchmark results or lab execution claims are made in this lesson.
