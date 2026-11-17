# Disk Space, Inodes, and Large-File Management

> **Stage 2B — Gap Module G2: Linux and Shell for Data Servers**  
> **Topic 07:** Disk space, inodes, and large-file management  
> **Audience:** Data Engineers progressing from Linux fundamentals to production server operations  
> **Learning loop:** Read → Do → Make it repeatable → Break it → Diagnose from evidence → Fix → Write the runbook entry → Explain aloud

---

## 0. Module Purpose

Full disks are one of the most common causes of failed Data Engineering workloads. The immediate symptom may be:

```text
No space left on device
```

but the underlying cause can be very different:

- application logs grew unexpectedly;
- `/tmp` or `/var/tmp` consumed the root filesystem;
- Spark created large shuffle or spill files;
- a Python/pandas workflow used substantial temporary storage;
- package or `pip` caches accumulated;
- Docker images, layers, writable data, or volumes grew;
- old CSV/Parquet exports were never retired;
- millions of tiny files exhausted **inodes** even though free disk blocks remained;
- a deleted file stayed open by a running process;
- a data filesystem was not mounted and a workload wrote into the underlying directory on the root filesystem;
- an external sort consumed its temporary filesystem.

This module teaches you to reason about the storage system rather than memorizing cleanup commands.

The central operational flow is:

```text
Understand storage
    ↓
Measure storage
    ↓
Find what consumes storage
    ↓
Distinguish capacity from inode exhaustion
    ↓
Find hidden storage consumers
    ↓
Safely reclaim space
    ↓
Choose appropriate storage locations
    ↓
Handle large files efficiently
    ↓
Prevent recurrence
```

---

# 1. Why Disk Management Matters in Data Engineering

Data Engineering workloads are unusually capable of producing temporary and intermediate data.

A small input can generate a much larger working set:

```text
Input data
   ↓
parse
   ↓
filter
   ↓
join
   ↓
sort
   ↓
shuffle
   ↓
aggregate
   ↓
temporary/spill data
   ↓
output
```

The final output might be 5 GB while the peak temporary footprint is 40 GB.

That means capacity planning cannot be based only on final output size.

### 1.1 The production question

Do not ask only:

> "How much data will this pipeline produce?"

Ask:

> "What is the peak storage footprint while this pipeline is running, including temporary files, logs, caches, spill, and concurrent jobs?"

### 1.2 Typical Data Engineering storage consumers

| Consumer | Example | Typical risk |
|---|---|---|
| Logs | application/service/debug logs | gradual growth |
| Temporary files | `/tmp`, application temp | sudden growth |
| Spark spill | shuffle/sort/join intermediate data | large bursts |
| Python/pandas temp | intermediate files | workload-dependent |
| Package caches | pip/package manager | gradual growth |
| Docker | images/layers/volumes | hidden host consumption |
| Exports | CSV/Parquet snapshots | retention failure |
| Backups | local archives | capacity exhaustion |
| Tiny files | fragments/partitions/artifacts | inode exhaustion |
| External sort | `sort` temporary runs | large temporary footprint |

### 1.3 Production mindset

The first response to a disk alert should not be:

```bash
rm -rf ...
```

It should be:

```text
Measure
→ identify
→ classify
→ determine ownership
→ understand retention
→ reclaim safely
→ verify
→ prevent recurrence
```

---

# 2. Storage Mental Model

A useful Linux storage model is:

```text
Physical / virtual storage
        ↓
Block device
        ↓
Filesystem
        ↓
Mount point
        ↓
Directories
        ↓
Files
```

These layers are related, but they are not the same thing.

## 2.1 Disk

A disk is the storage medium presented to the operating system. In a cloud VM it may be virtualized storage rather than a physical disk.

Think:

```text
"Where does the storage capacity come from?"
```

## 2.2 Block device

A block device provides block-addressable storage to Linux.

Examples can look like:

```text
/dev/sda
/dev/sdb
/dev/nvme0n1
```

A block device may contain:

- a filesystem directly;
- partitions;
- another storage abstraction.

## 2.3 Filesystem

A filesystem organizes storage so Linux can manage files and directories.

Common Linux filesystems include:

```text
ext4
xfs
```

This topic does not attempt to teach filesystem internals in depth.

The important Data Engineering questions are:

- how much capacity is available?
- how much is consumed?
- how many inodes remain?
- where is the filesystem mounted?
- what workloads are writing to it?
- what happens when it fills?

## 2.4 Mount point

A mount point is a directory where a filesystem becomes accessible.

For example:

```text
/data
```

can be the mount point for a dedicated data filesystem.

The mental model is:

```text
/dev/sdb1
    ↓
filesystem
    ↓
mounted at /data
```

## 2.5 File and directory

A file stores data.

A directory organizes filesystem entries.

A very large file consumes storage blocks. A huge number of files can additionally consume a large number of inodes.

That distinction becomes critical later.

---

# 3. Disk Capacity vs Filesystem Capacity

There are two related but different questions.

### Question A

> How large is the underlying storage device?

### Question B

> How much usable filesystem space is currently consumed?

A Data Engineer needs both perspectives.

A block device can be large while a particular filesystem is nearly full.

Likewise, a filesystem can report free blocks but have no free inodes.

---

# 4. `df` — Filesystem Usage

The first command for a disk-space incident is usually:

```bash
df -h
```

Typical output:

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        80G   76G  4.0G  95% /
/dev/sdb1       500G  210G  290G  43% /data
tmpfs             8G     0    8G   0% /run
```

Interpret it as:

| Column | Meaning |
|---|---|
| Filesystem | filesystem/device identity |
| Size | filesystem capacity reported in human-readable units |
| Used | consumed filesystem space |
| Avail | available space for normal use |
| Use% | percentage used |
| Mounted on | mount point |

## 4.1 Identify the important filesystems

Look for:

```text
/
 /data
 /tmp
 /var
Docker-related mounts or host storage
```

Do not assume `/data` is actually mounted merely because the directory exists.

Verify the mount.

Useful commands include:

```bash
findmnt /data
```

and:

```bash
mount
```

## 4.2 Why `df` is a filesystem-level view

`df` answers:

> "How much space does this filesystem report as used and available?"

It does not directly tell you which directory owns the space.

For that, use `du`.

---

# 5. `du` — Directory Usage

`du` answers a different question:

> "How much filesystem space is consumed by this directory tree?"

Basic usage:

```bash
du
```

Human-readable summary:

```bash
du -sh .
```

Top-level directory usage:

```bash
du -h --max-depth=1 /data
```

A recursive listing that can be sorted:

```bash
du -ah /data | sort -h
```

### 5.1 Important options

- `-h` — human-readable units
- `-s` — summary
- `--max-depth=1` — inspect one directory level
- `-a` — include files as well as directories
- `sort -h` — sort human-readable sizes

### 5.2 A practical progression

Start broad:

```bash
df -h
```

Identify the filesystem:

```text
/data is 92% full
```

Then narrow:

```bash
du -h --max-depth=1 /data
```

Suppose:

```text
120G /data/logs
450G /data/raw
380G /data/tmp
```

Now inspect the largest area:

```bash
du -h --max-depth=1 /data/raw
```

Then inspect specific subtrees or large files.

### 5.3 Why `du` can be expensive

`du` must walk directory trees and inspect filesystem metadata.

A tree containing millions of files can take substantial time and generate substantial I/O.

Do not reflexively run:

```bash
du -ah /
```

on a large production server.

Prefer a staged investigation:

```text
df
→ identify filesystem
→ inspect top-level directories
→ narrow scope
→ inspect likely consumers
```

### 5.4 Permissions matter

You may not be able to inspect every directory as an ordinary user.

Use the minimum privileges necessary, and understand what you are scanning.

---

# 6. Finding the Largest Directories and Files

A reliable investigation follows this hierarchy:

```text
Which filesystem?
       ↓
Which directory?
       ↓
Which subdirectory?
       ↓
Which files?
       ↓
What workload created them?
```

For a known data filesystem:

```bash
du -h --max-depth=1 /data | sort -h
```

For a narrower subtree:

```bash
du -h --max-depth=1 /data/tmp | sort -h
```

For file-level inspection:

```bash
du -ah /data/tmp | sort -h | tail -n 20
```

The final command is useful on a bounded tree, but avoid using it indiscriminately on enormous production filesystems.

## 6.1 A better operational pattern

```text
df -h
↓
select filesystem
↓
du --max-depth=1
↓
select largest directory
↓
repeat
↓
inspect files
```

This makes the investigation evidence-driven.

---

# 7. `ncdu` — Interactive Disk Exploration

`ncdu` is an interactive disk-usage analyzer.

It can make exploration easier when a directory tree is complicated.

Conceptually:

```bash
ncdu /data
```

It provides an interactive view of directory sizes.

## 7.1 When `ncdu` is useful

Use it when:

- you need to explore a large directory hierarchy;
- you want an interactive alternative to repeated `du` commands;
- you are investigating an unfamiliar data disk.

## 7.2 `du` vs `ncdu`

| Tool | Strength |
|---|---|
| `df` | filesystem capacity |
| `du` | scriptable directory/file usage |
| `ncdu` | interactive exploration |

`ncdu` does **not** replace understanding `df`.

A good mental model is:

```text
df = filesystem view
du = directory accounting view
ncdu = interactive exploration
```

## 7.3 Limitations

`ncdu` still needs to traverse filesystem content.

Permission restrictions and huge directory trees can affect what it can inspect and how long it takes.

---

# 8. Common Data Engineering Space Hogs

## 8.1 Logs

Logs can include:

```text
application logs
service logs
debug logs
failed-job logs
audit logs
```

A verbose logging configuration can create a storage incident even when the pipeline's actual data volume is stable.

Questions:

```text
Who owns the logs?
What is the retention policy?
Is log rotation configured?
Is the application still writing the file?
Can old logs be archived safely?
```

Do not delete active logs blindly.

## 8.2 Temporary directories

Common locations include:

```text
/tmp
/var/tmp
```

and application-specific locations.

Temporary data may be created by:

- Python applications;
- sorting;
- database clients;
- analytical engines;
- compression/decompression;
- ETL/ELT tools.

## 8.3 Spark spill

Spark can create substantial local intermediate data during operations such as:

- shuffle;
- sort;
- joins;
- aggregation;
- memory pressure that causes spill.

The important operational model is:

```text
Spark workload
    ↓
intermediate data
    ↓
local temporary/spill storage
    ↓
disk consumption
```

This is an awareness topic, not a Spark-internals course.

## 8.4 pandas and Python temporary data

Large Python workflows may use temporary storage for intermediate operations or files.

Do not assume:

```text
Python process
=
RAM only
```

A production workflow may involve both memory and disk.

## 8.5 Package and pip caches

Package managers can accumulate caches.

For example:

```text
pip cache
OS package caches
```

Before cleaning a cache, understand:

- whether it is required;
- whether it is managed centrally;
- whether cleaning it affects reproducibility or future installation speed.

## 8.6 Docker data

Docker can consume host disk through:

```text
images
layers
container writable layers
volumes
build/cache data
```

This connects directly to G1 Docker Essentials.

Do not manually delete Docker-managed filesystem data.

Use Docker's own inspection and cleanup mechanisms according to the ownership model.

## 8.7 Old exports and backups

Examples:

```text
CSV exports
Parquet snapshots
debug dumps
backups
temporary extracts
```

The safe questions are:

```text
Can this data be deleted?
Who owns it?
Is there a retention policy?
Is it currently being used?
Is it the only copy?
Can it be restored?
```

---

# 9. Inodes — A Second Finite Storage Resource

One of the most important concepts in this module is:

> **Disk space and inodes are two different finite resources.**

A simplified model:

```text
Filesystem capacity
    ├── data blocks
    └── inode structures
```

A filesystem can have:

```text
free disk space
```

and still fail to create a new file because:

```text
inodes are exhausted
```

Check inode usage with:

```bash
df -i
```

Typical output:

```text
Filesystem      Inodes   IUsed   IFree IUse% Mounted on
/dev/root      5242880 5200000   42880   99% /
```

Important fields:

| Field | Meaning |
|---|---|
| Inodes | inode capacity |
| IUsed | inodes consumed |
| IFree | free inodes |
| IUse% | inode percentage used |

## 9.1 Capacity vs inode exhaustion

Think:

```text
BLOCK EXHAUSTION
"No room for more data bytes"

vs

INODE EXHAUSTION
"No metadata slots for more files/directories"
```

The exact filesystem behavior depends on filesystem design, but the operational distinction is essential.

---

# 10. Why Millions of Small Files Are Dangerous

A workload with millions of tiny files can create operational problems even when their total byte size is not enormous.

Examples:

```text
one-file-per-record
one-file-per-event
small ingestion fragments
small Spark output files
temporary artifacts
partition fragments
```

The design pattern becomes:

```text
Millions of tiny files
        ↓
inode consumption
        ↓
filesystem metadata overhead
        ↓
slower directory operations
        ↓
operational problems
```

A better Data Engineering design often involves:

```text
batch small files
→ compact data
→ choose appropriate file formats
→ avoid one-file-per-record patterns
```

The detailed compaction strategy belongs to later storage/data-platform modules; this module teaches the operational consequence.

---

# 11. Deleted-but-Open Files

This is a critical Linux troubleshooting concept.

Consider:

```text
Process opens file
       ↓
file contains 50 GB
       ↓
directory entry is deleted
       ↓
process still holds file descriptor
       ↓
directory listing no longer shows file
       ↓
filesystem blocks remain allocated
```

Therefore:

```text
df shows space consumed
```

while:

```text
du may not show the file
```

The simplified model is:

```text
File deleted
    ↓
Directory entry removed
    ↓
Process still has file open
    ↓
Blocks remain allocated
    ↓
df still reports usage
    ↓
du cannot account for the missing path
```

## 11.1 Find deleted-open files

A useful command is:

```bash
lsof +L1
```

This can identify files with link counts below the expected value, including deleted-open files.

Look for:

```text
COMMAND
PID
USER
FD
TYPE
SIZE/OFF
NAME
```

## 11.2 Why the disk is not immediately freed

Linux can keep the underlying file data alive while a process still has an open reference.

Space is released when the relevant process closes the file descriptor and no other references remain.

## 11.3 Safe remediation

Do not "delete it again."

Instead:

```text
identify process
    ↓
understand why it owns the file
    ↓
determine whether rotation/close/restart is safe
    ↓
use the application's normal lifecycle
    ↓
verify disk recovery
```

A restart may be appropriate in some cases, but it is not a universal first response.

---

# 12. When `df` and `du` Disagree

A classic incident:

```bash
df -h
```

reports:

```text
/dev/root   80G   76G   4G   95% /
```

But:

```bash
du -sh /*
```

does not explain anything close to 76 GB.

Do not immediately delete files.

Possible explanations include:

```text
deleted-but-open files
different filesystems/mounts
hidden mount points
filesystem metadata or reserved space
```

The key diagnostic question is:

> What is consuming blocks that the directory tree I inspected does not account for?

A practical sequence:

```bash
df -h
```

then:

```bash
df -i
```

then targeted:

```bash
du -h --max-depth=1 /
```

and, when appropriate:

```bash
lsof +L1
```

Then inspect mounts:

```bash
findmnt
```

The goal is reconciliation, not guesswork.

---

# 13. Block Devices and `lsblk`

Use:

```bash
lsblk
```

to inspect block devices, partitions, and mount relationships.

Example:

```text
NAME        SIZE TYPE MOUNTPOINT
sda          80G disk
└─sda1       80G part /
sdb         500G disk
└─sdb1      500G part /data
```

A useful mental model:

```text
/dev/sda
   └── partition
        └── filesystem
             └── mounted at /
```

and:

```text
/dev/sdb
   └── partition
        └── filesystem
             └── mounted at /data
```

## 13.1 Device names are not stable identities

Do not build persistent storage configuration around assumptions such as:

```text
/dev/sdb is always my data disk
```

Device enumeration can change.

For persistent mounts, use stable identifiers such as filesystem UUIDs.

---

# 14. Adding a Data Disk

A conceptual workflow is:

```text
New disk
   ↓
Identify device
   ↓
Confirm it is the correct device
   ↓
Create partition if appropriate
   ↓
Create filesystem
   ↓
Create mount point
   ↓
Mount
   ↓
Verify
   ↓
Obtain UUID
   ↓
Configure persistent mount
   ↓
Test safely
```

## 14.1 Inspect the device

```bash
lsblk
```

You may also use:

```bash
blkid
```

## 14.2 Create a filesystem

For a disposable practice device, an example may be:

```bash
sudo mkfs.ext4 /dev/sdb1
```

> **DESTRUCTIVE OPERATION:** `mkfs` creates a filesystem and can destroy existing data on the target device. Never run it against an unverified device.

Before any destructive command:

```text
identify device
→ verify size
→ verify expected state
→ verify it is disposable/new
→ only then modify it
```

## 14.3 Create a mount point

```bash
sudo mkdir -p /data
```

## 14.4 Mount

```bash
sudo mount /dev/sdb1 /data
```

Verify:

```bash
findmnt /data
```

and:

```bash
df -h /data
```

## 14.5 Verify ownership and permissions

A mounted filesystem may initially be owned by `root`.

Data Engineering applications often require a service account or controlled group ownership.

Do not solve this by making the filesystem world-writable.

Use least privilege.

---

# 15. Filesystem Creation — Awareness

Common Linux filesystem choices include:

```text
ext4
xfs
```

At this level, the important point is that filesystem choice can affect operational characteristics such as:

- workload behavior;
- file counts;
- file sizes;
- performance characteristics;
- platform defaults;
- durability and operational requirements.

Do not turn this module into a filesystem-internals course.

You should be able to ask:

> "Which filesystem am I using, where is it mounted, and what workload is using it?"

---

# 16. Mounting and `findmnt`

You can inspect mounts with:

```bash
mount
```

A more focused command is:

```bash
findmnt /data
```

or:

```bash
findmnt
```

## 16.1 The hidden-directory trap

Suppose:

```text
/data
```

already contains files.

Then you mount another filesystem on:

```text
/data
```

The old files are not necessarily deleted.

They are hidden underneath the mounted filesystem.

Conceptually:

```text
Before mount:

/data
 ├── old-file-1
 └── old-file-2

After mounting another filesystem:

/data
 └── contents of mounted filesystem
```

This can produce confusing investigations.

If you unmount later, the underlying files may become visible again.

---

# 17. Persistent Mounts with `/etc/fstab`

A manual mount:

```bash
sudo mount /dev/sdb1 /data
```

does not necessarily survive a reboot.

Persistent mounts are commonly configured in:

```text
/etc/fstab
```

A conceptual UUID-based entry:

```text
UUID=<uuid>  /data  ext4  defaults  0  2
```

## 17.1 Understand the fields

```text
UUID=<uuid>   /data   ext4   defaults   0   2
   │            │        │       │       │   │
device       mount   fs type  options  dump fsck order
identity     point
```

The exact last fields depend on filesystem and platform conventions, but the important operational pattern is stable identity plus verified mount configuration.

## 17.2 Why UUIDs?

Avoid relying blindly on:

```text
/dev/sdb1
```

because device names can change across boots or environments.

Use:

```bash
blkid
```

to identify the filesystem UUID.

## 17.3 Validate before rebooting

A safer sequence is:

```bash
sudo mount -a
```

then:

```bash
findmnt /data
```

and:

```bash
df -h /data
```

> **Operational caution:** A malformed `/etc/fstab` entry can cause boot or service-start problems. Never edit it casually and reboot immediately.

---

# 18. Failure-Tolerant Mount Configuration

Not every data disk is equally critical.

Consider:

```text
Root filesystem
    ↓
critical operating system storage

Optional data disk
    ↓
important workload storage but potentially recoverable
```

For optional mounts, `nofail` may be appropriate in some environments.

Conceptually:

```text
UUID=<uuid> /data ext4 defaults,nofail 0 2
```

`nofail` can prevent an unavailable optional filesystem from becoming a boot blocker.

But do not add it everywhere without understanding the consequence.

The design question is:

> Is this storage optional enough that the server should remain available if the mount is unavailable?

---

# 19. Data Directory Design

A production Data Engineering server may separate storage responsibilities.

For example:

```text
/
├── operating system
├── system configuration
└── service state

/data
├── raw
├── intermediate
├── output
└── working

/data/tmp
└── temporary/spill

logs
└── application/service logs
```

The exact layout depends on workload and platform.

The important principle is:

> Do not allow uncontrolled temporary growth to compete blindly with critical operating-system storage.

---

# 20. Temporary and Spill Directories

Temporary data can be more dangerous than final output because it is often transient and can grow rapidly.

A simplified design:

```text
Root filesystem
    ├── OS
    ├── logs
    ├── application
    └── uncontrolled temp  ← risky

Dedicated data filesystem
    ├── data
    ├── temporary processing
    ├── spill
    └── intermediate files
```

This is not a universal architecture, but it is a useful production design pattern.

---

# 21. `TMPDIR`

Many Unix-compatible programs use environment variables to select temporary storage.

For example:

```bash
export TMPDIR=/data/tmp
```

Verify the directory:

```bash
mkdir -p /data/tmp
```

Then ensure appropriate permissions.

A process started with the environment may use:

```text
/data/tmp
```

instead of the default temporary directory.

## 21.1 Important limitation

Do not assume every application honors `TMPDIR`.

The correct operational approach is:

```text
configure
→ run
→ observe actual filesystem usage
→ verify
```

rather than:

```text
set TMPDIR
→ assume success
```

---

# 22. Python Temporary Directories

Python exposes temporary-file functionality through the standard library.

Example:

```python
import tempfile

with tempfile.NamedTemporaryFile() as f:
    print(f.name)
```

The location is influenced by the process environment and platform configuration.

Inspect the actual result rather than assuming it.

For example:

```bash
TMPDIR=/data/tmp python app.py
```

A production workflow should ensure:

```text
/data/tmp
exists
is writable by the service
has sufficient capacity
has appropriate retention/cleanup behavior
```

---

# 23. Spark Local and Spill Directories

Spark workloads can use local storage for:

```text
shuffle
sort
spill
temporary local data
```

A relevant configuration concept is:

```text
spark.local.dir
```

The operational objective is not to memorize Spark internals.

It is to understand:

```text
Spark job
   ↓
local intermediate data
   ↓
filesystem consumption
   ↓
disk pressure
```

If Spark local storage is placed on the root filesystem, a large job can threaten the entire server.

A dedicated local data filesystem can isolate that risk when the deployment architecture supports it.

---

# 24. DuckDB Temporary Directory

DuckDB can use temporary storage for operations that cannot remain entirely in memory.

Think:

```text
memory
+
temporary disk
=
large analytical workload
```

The exact setting depends on the DuckDB workflow/version.

In Python, a workload can be configured to use an appropriate temporary directory, for example:

```python
import duckdb

con = duckdb.connect()
con.execute("SET temp_directory = '/data/tmp/duckdb'")
```

Verify the directory exists and has enough capacity before executing a large operation.

The operational lesson is:

> Analytical engines can consume temporary disk even when their final output is small.

---

# 25. Handling Huge Files

A large file should not automatically become:

```python
data = read_everything_into_memory(...)
```

Instead consider:

```text
inspect
→ sample
→ stream
→ process incrementally
→ split when appropriate
→ compress
→ external-sort when necessary
```

The key mental model is:

```text
Large file
≠
load entire file into RAM
```

---

# 26. `head` and `tail`

For inspection:

```bash
head -n 20 large.csv
```

and:

```bash
tail -n 20 large.csv
```

These are useful because they let you inspect a small portion without intentionally loading the entire file into an application.

Examples:

```bash
head -n 5 data.csv
tail -n 5 data.csv
```

Use inspection tools for inspection.

Do not confuse:

```text
sampling/inspection
```

with:

```text
full processing
```

---

# 27. Counting Lines Efficiently

A standard tool is:

```bash
wc -l large.csv
```

It must still scan the file, so the operation has an I/O cost.

But it does not require an application to hold the entire file in memory.

Think in three dimensions:

```text
CPU cost
I/O cost
memory cost
```

A command can have low memory use while still requiring substantial I/O.

---

# 28. Splitting Large Files

Use:

```bash
split
```

For example:

```bash
split -l 1000000 large.csv chunk_
```

This splits by line count.

You can also split by byte size, depending on the use case.

## 28.1 Important CSV caveat

Naive line-based splitting is not always semantically safe for arbitrary CSV.

A CSV record may contain embedded newlines inside quoted fields.

Therefore:

```text
line-based split
```

is safe only when the file format and downstream assumptions make that acceptable.

Consider:

- headers;
- quoted fields;
- embedded newlines;
- record boundaries;
- downstream recombination.

Do not teach `split` as a universal CSV partitioning solution.

---

# 29. Reading Compressed Files Without Decompressing to Disk

A common anti-pattern is:

```text
100 GB compressed file
        ↓
fully decompress
        ↓
100+ GB uncompressed copy
        ↓
process
```

When only inspection or streaming is needed, use:

```text
compressed file
    ↓
stream decompression
    ↓
pipe
    ↓
consumer
```

For gzip:

```bash
zcat data.csv.gz | head
```

For Zstandard:

```bash
zstdcat data.csv.zst | head
```

You can also stream into other Unix tools:

```bash
zcat data.csv.gz | wc -l
```

The benefit is avoiding an unnecessary full decompressed copy.

---

# 30. Large-File Sorting

A difficult production question is:

> How do you sort a file larger than RAM?

Unix `sort` can use external sorting techniques.

Conceptually:

```text
Large input
    ↓
read manageable chunks
    ↓
sort chunks
    ↓
write temporary runs
    ↓
merge runs
    ↓
final sorted output
```

This means:

```text
RAM
+
temporary disk
=
external sort
```

The temporary disk can become a major storage consumer.

---

# 31. `sort` Buffer and Temporary Directory

Useful concepts include:

```text
-S / --buffer-size
-T / --temporary-directory
```

Example:

```bash
sort -S 2G -T /data/tmp input.txt > output.txt
```

Interpretation:

- `-S 2G` controls the sort's memory buffer;
- `-T /data/tmp` directs temporary files to the selected directory;
- `>` writes final output to the destination.

The exact optimal buffer depends on the system and workload.

Do not assume:

```text
more RAM allocation = always faster
```

because disk throughput, concurrency, CPU, and available temporary capacity also matter.

---

# 32. External Sort Data Engineering Example

Suppose:

```text
20 GB CSV
```

must be sorted, but the server cannot safely hold the entire dataset in RAM.

A risky design:

```text
sort 20 GB
↓
temporary data appears on /
↓
root filesystem fills
↓
job fails
↓
services become unhealthy
```

A safer workflow:

```text
Check free disk
    ↓
Check inode usage
    ↓
Choose dedicated temporary filesystem
    ↓
Set sort buffer
    ↓
Run
    ↓
Monitor disk
    ↓
Verify output
    ↓
Clean temporary data if appropriate
```

This directly connects Topic 06:

```text
CPU / memory / I/O monitoring
```

with Topic 07:

```text
capacity / filesystem / temporary storage management
```

---

# 33. Parallel Compression

Two useful tools are:

```text
zstd
pigz
```

Compression is a resource trade-off.

It consumes:

```text
CPU
+
I/O
```

while reducing:

```text
storage
+
network transfer volume
```

Parallel compression can improve throughput on multicore systems.

## 33.1 `zstd`

A simple example:

```bash
zstd large.csv
```

## 33.2 `pigz`

`pigz` is a parallel implementation of gzip-compatible compression.

Example:

```bash
pigz large.csv
```

Exact throughput depends on:

- CPU;
- storage throughput;
- compression level;
- data compressibility;
- concurrency.

---

# 34. Compression Levels

Higher compression can produce smaller output, but often at increased CPU cost.

Think:

```text
Higher compression
    ↓
smaller output
    ↓
more CPU/time
```

versus:

```text
Faster/lower compression
    ↓
larger output
    ↓
less CPU/time
```

Choose based on:

- storage cost;
- CPU availability;
- pipeline latency;
- downstream read speed;
- network transfer requirements.

There is no universally best compression level.

---

# 35. Filesystem and Mount Options — Awareness

Data Engineers do not need to become filesystem-kernel specialists for this module.

They should understand that:

```text
filesystem choice
+
mount options
+
I/O characteristics
+
file count
+
file size
+
durability requirements
```

can influence workload behavior.

Common filesystems to recognize:

```text
ext4
xfs
```

The goal is awareness:

> "Could filesystem or mount configuration be relevant to this storage problem?"

not:

> "Can I tune every filesystem parameter?"

---

# 36. Disk Usage Alerts and Growth-Rate Projections

Capacity management should be proactive.

The simple model is:

```text
Current disk usage
+
growth rate
=
future capacity risk
```

Example:

```text
Disk = 70% full
Growth = 5% per day
```

A crude projection is:

```text
remaining headroom = 30 percentage points
estimated threshold time ≈ 30 / 5 = 6 days
```

Real systems are not perfectly linear, so this is a planning estimate, not a guarantee.

## 36.1 Alerting concepts

Use:

```text
warning threshold
critical threshold
growth-rate monitoring
forecasting
```

The thresholds should reflect the workload.

A system with large bursty spill may need more headroom than a stable archival server.

---

# 37. Data Engineering Storage Design

A production storage design should distinguish:

```text
Raw data
Intermediate data
Temporary data
Spill data
Logs
Outputs
Caches
```

They do not necessarily belong on the same filesystem.

## 37.1 Design questions

Before deploying a workload, ask:

```text
How much space does the workload need?
What is the peak temporary usage?
Where does spill occur?
What happens during concurrent jobs?
What happens if the disk fills?
Can the data be deleted?
How long should it be retained?
What is the recovery plan?
```

## 37.2 Peak, not average

Suppose two jobs each need:

```text
20 GB average
```

but each can temporarily require:

```text
80 GB
```

Concurrent execution changes the capacity requirement dramatically.

Think:

```text
peak workload
+
concurrency
+
system overhead
+
recovery headroom
```

---

# 38. Production Disk Incident Methodology

The central troubleshooting framework is:

```text
DISK ALERT
    ↓
Which filesystem?
    ↓
df -h
    ↓
Capacity or inode problem?
    ↓
df -i
    ↓
What directory is large?
    ↓
du / ncdu
    ↓
What type of data?
    ↓
logs / temp / spill / exports / cache / application
    ↓
Could deleted-open files explain the difference?
    ↓
lsof
    ↓
Could mounts/devices explain the view?
    ↓
lsblk / findmnt
    ↓
Can it be safely reclaimed?
    ↓
Who owns the data?
    ↓
Fix
    ↓
Verify
    ↓
Prevent recurrence
```

The first question is not:

> "What can I delete?"

It is:

> **"What is consuming the storage, and why?"**

---

# 39. Production-Safe Remediation Framework

Use this sequence:

```text
1. Measure
2. Identify
3. Classify
4. Determine ownership
5. Check retention
6. Choose reversible/safe remediation
7. Execute
8. Verify
9. Document
10. Prevent recurrence
```

## 39.1 Measure

Examples:

```bash
df -h
df -i
```

## 39.2 Identify

Examples:

```bash
du -h --max-depth=1 /data
ncdu /data
```

## 39.3 Classify

Ask:

```text
log?
temp?
spill?
cache?
export?
backup?
active data?
```

## 39.4 Determine ownership

Ask:

```text
Which service owns it?
Which team owns it?
Is a process actively writing it?
```

## 39.5 Check retention

Do not delete data simply because it is large.

## 39.6 Verify

After remediation:

```bash
df -h
df -i
```

Then verify the workload.

---

# 40. Hands-On `server_lab/07/`

Use a dedicated practice area:

```text
server_lab/
└── 07/
    ├── README.md
    ├── scripts/
    ├── fixtures/
    ├── logs/
    ├── tmp/
    ├── sort-work/
    └── runbook.md
```

Use disposable VMs/containers where appropriate.

> **Never perform filesystem-filling or inode-exhaustion experiments on production.**

---

## Lab 1 — Find Top Space Consumers

### Objective

Diagnose a server where one filesystem is nearly full.

### Steps

1. Inspect filesystems:

```bash
df -h
```

2. Identify the full filesystem.
3. Inspect its top-level directories:

```bash
du -h --max-depth=1 /data | sort -h
```

4. Narrow the investigation.
5. Find large files.
6. Classify them.
7. Clean only explicitly safe candidates.
8. Verify recovery.

### Required explanation

Write down:

```text
Why did I use df?
Why did I use du?
Why did I narrow the scan?
What owns the largest data?
Why is deletion safe?
How did I verify recovery?
```

---

# 41. Lab 2 — Exhaust Inodes

> **SAFETY:** Disposable environment only.

Create many tiny files:

```bash
mkdir -p /data/inode-lab
for i in $(seq 1 100000); do
    touch "/data/inode-lab/file-$i"
done
```

Observe:

```bash
df -i /data
```

Then:

```bash
df -h /data
```

Compare:

```text
byte usage
vs
inode usage
```

Clean:

```bash
rm -rf /data/inode-lab
```

Then verify:

```bash
df -i /data
```

### Design question

How would you redesign a Data Engineering workload that creates millions of tiny files?

Expected concepts:

```text
batching
compaction
appropriate file formats
avoiding one-file-per-record
```

---

# 42. Lab 3 — Deleted-but-Open Log

> **SAFETY:** Disposable practice environment only.

Create a writer:

```bash
mkdir -p /data/deleted-open
python3 - <<'PY' &
import time

f = open("/data/deleted-open/app.log", "wb")
while True:
    f.write(b"x" * 1024 * 1024)
    f.flush()
    time.sleep(0.2)
PY
echo $! > /tmp/log-writer.pid
```

Observe:

```bash
df -h /data
du -sh /data/deleted-open
```

Remove the directory entry:

```bash
rm /data/deleted-open/app.log
```

Now compare:

```bash
df -h /data
du -sh /data/deleted-open
```

Find the process:

```bash
lsof +L1
```

Stop it safely:

```bash
kill "$(cat /tmp/log-writer.pid)"
```

Then verify:

```bash
df -h /data
```

### Learning outcome

You should be able to explain why:

```text
du no longer shows the file
```

while:

```text
df still shows consumed space
```

until the open descriptor is released.

---

# 43. Lab 4 — Add a Data Disk

Use a disposable VM or safe loopback-based environment.

Workflow:

```text
identify device
→ verify device
→ create filesystem
→ mount
→ verify
→ get UUID
→ configure fstab
→ validate
```

Inspect:

```bash
lsblk
```

Create a filesystem only on a verified disposable target:

```bash
sudo mkfs.ext4 /dev/<VERIFIED_DEVICE>
```

> **DESTRUCTIVE:** Replace `<VERIFIED_DEVICE>` only after confirming it is disposable. Never experiment with `mkfs` on a production disk.

Mount:

```bash
sudo mkdir -p /data
sudo mount /dev/<VERIFIED_DEVICE> /data
```

Verify:

```bash
findmnt /data
df -h /data
```

Get UUID:

```bash
sudo blkid /dev/<VERIFIED_DEVICE>
```

Configure `/etc/fstab` with the verified UUID.

Validate:

```bash
sudo mount -a
findmnt /data
```

Only test reboot persistence in a disposable environment where recovery access is available.

---

# 44. Lab 5 — Temporary Directory Placement

Create:

```bash
sudo mkdir -p /data/tmp
```

Configure a practice process:

```bash
TMPDIR=/data/tmp python3 -c 'import tempfile; print(tempfile.gettempdir())'
```

Expected concept:

```text
/data/tmp
```

Then demonstrate temporary data for:

```text
Python
DuckDB
Spark local/spill awareness
```

Verify actual usage with:

```bash
df -h /data
du -h --max-depth=1 /data/tmp
```

The goal is to prove placement rather than merely assume it.

---

# 45. Lab 6 — Large Compressed CSV

Generate a sufficiently large synthetic dataset in a disposable filesystem.

For example, create repeated records and compress them.

Inspect without full decompression:

```bash
zcat data.csv.gz | head -n 20
```

Count records:

```bash
zcat data.csv.gz | wc -l
```

For Zstandard:

```bash
zstdcat data.csv.zst | head -n 20
```

Use a dedicated temporary directory for external sorting:

```bash
mkdir -p /data/sort-work
```

Example pipeline:

```bash
zcat data.csv.gz \
  | sort -T /data/sort-work \
  > /data/output/sorted.csv
```

Monitor:

```bash
df -h /data
df -i /data
```

For a real large workload, choose a sort buffer appropriate to the machine:

```bash
sort -S 2G -T /data/sort-work ...
```

### Learning outcome

You should be able to explain:

```text
large file
≠
load everything into RAM
```

and:

```text
external sort
=
memory
+
temporary disk
```

---

# 46. Break/Fix Scenarios

Every scenario should be worked using:

```text
Symptom
Evidence
Hypothesis
Commands
Interpretation
Root cause
Safe fix
Verification
Prevention
Runbook entry
```

---

## Scenario 1 — Root Filesystem 95% Full

### Symptom

```text
No space left on device
```

### Investigation

```bash
df -h
df -i
```

Then narrow:

```bash
du -h --max-depth=1 /
```

### Questions

- Which filesystem is full?
- Is the problem blocks or inodes?
- Which directory is largest?
- Is it safe to remove anything?
- Is a mount missing?

---

# 47. Scenario 2 — `df` Full, `du` Does Not Explain It

Start with:

```bash
df -h
```

Then:

```bash
du -h --max-depth=1 /
```

If the numbers do not reconcile, investigate:

```bash
lsof +L1
```

and:

```bash
findmnt
```

Possible root cause:

```text
deleted-but-open file
```

Do not immediately restart arbitrary services.

---

# 48. Scenario 3 — Inodes 100% Consumed

Evidence:

```bash
df -i
```

Suppose:

```text
IUse% = 100%
```

but:

```bash
df -h
```

still reports free capacity.

Investigate small-file-heavy directories.

Use bounded `du` scans and directory inspection.

Root cause might be:

```text
millions of tiny temporary files
```

Fix:

```text
safe cleanup
+
workload redesign
+
compaction/batching
```

---

# 49. Scenario 4 — Spark Job Fails with `No space left on device`

Determine whether the full filesystem is:

```text
root filesystem
temporary filesystem
Spark local/spill location
output filesystem
```

Inspect:

```bash
df -h
df -i
findmnt
```

Then inspect relevant directories.

Ask:

```text
Where is spark.local.dir?
How much temporary data did the job generate?
Was the data disk mounted?
Was the root filesystem used accidentally?
Was another concurrent job consuming the same disk?
```

---

# 50. Scenario 5 — Large Sort Fills Disk

Symptom:

```text
sort process still running
disk usage rapidly increasing
```

Check:

```bash
df -h
```

and the temporary directory:

```bash
du -h --max-depth=1 /data/sort-work
```

Root cause:

```text
external sort temporary runs
```

Fix may involve:

```text
dedicated temporary filesystem
appropriate sort buffer
sufficient headroom
workload redesign
```

Do not simply increase the buffer without considering temporary storage.

---

# 51. Scenario 6 — Data Disk Not Mounted After Reboot

Check:

```bash
findmnt /data
```

Then:

```bash
lsblk
blkid
```

Inspect the persistent configuration:

```bash
cat /etc/fstab
```

Look for:

```text
wrong UUID
wrong filesystem type
wrong mount point
syntax/configuration error
missing device
```

Validate:

```bash
sudo mount -a
```

Then:

```bash
findmnt /data
```

---

# 52. Scenario 7 — Huge Compressed File

Requirement:

```text
Process a huge compressed dataset
without creating an unnecessary full decompressed copy.
```

Prefer:

```bash
zcat data.csv.gz | consumer
```

or:

```bash
zstdcat data.csv.zst | consumer
```

Inspect:

```bash
zcat data.csv.gz | head
```

Count:

```bash
zcat data.csv.gz | wc -l
```

The key decision is whether the consumer can operate as a stream.

---

# 53. Troubleshooting Decision Tree

When the alert is:

```text
NO SPACE LEFT ON DEVICE
```

use:

```text
                    NO SPACE LEFT ON DEVICE
                              |
                              v
                           df -h
                              |
                              v
                     Which filesystem?
                              |
                              v
                           df -i
                       /               \
                      /                 \
             inode exhaustion       block exhaustion
                  |                       |
                  v                       v
            find tiny files          du / ncdu
                                          |
                                          v
                                  Which directories?
                                          |
                                          v
                                  Which workload?
                                          |
                 +----------------+-------+----------------+
                 |                |       |                |
               logs             temp     spill           exports
                 |                |       |                |
                 +----------------+-------+----------------+
                                          |
                                          v
                                  df vs du mismatch?
                                      /       \
                                    yes        no
                                     |          |
                                     v          v
                                  lsof       reclaim safely
                                +L1 / mounts       |
                                     |              v
                                     v           verify
                              deleted-open          |
                                files?              v
                                     |          prevent recurrence
                                     v
                                  safe fix
```

A second branch should always consider:

```text
Is the expected data disk actually mounted?
```

Use:

```bash
findmnt
lsblk
```

---

# 54. Production Runbook: Disk Space / Inode Exhaustion

## Symptom

Examples:

```text
No space left on device
jobs failing
database unable to write
Spark job failing
logs failing
server alerts
```

## Step 1 — Identify filesystem

```bash
df -h
```

Record:

```text
filesystem
size
used
available
Use%
mount point
```

## Step 2 — Check inodes

```bash
df -i
```

Determine:

```text
block exhaustion?
inode exhaustion?
both?
```

## Step 3 — Find consumers

```bash
du -h --max-depth=1 /data | sort -h
```

Use:

```bash
ncdu /data
```

when appropriate.

## Step 4 — Investigate mismatch

If `df` and `du` do not reconcile:

```bash
lsof +L1
```

Then inspect mounts:

```bash
findmnt
```

## Step 5 — Inspect devices

```bash
lsblk
blkid
```

Confirm expected data filesystems are mounted.

## Step 6 — Identify workload

Classify:

```text
logs
temp
spill
exports
cache
Docker
application data
```

## Step 7 — Remediation

Only perform evidence-based remediation.

Examples:

```text
remove expired data according to retention policy
rotate/archive logs
stop or reconfigure runaway workload
move future temporary/spill storage
restore missing data mount
reclaim safe cache
```

Do not blindly remove active data.

## Step 8 — Verification

Confirm:

```text
space recovered
inode usage normal
application recovered
filesystem correctly mounted
new writes succeed
```

Commands:

```bash
df -h
df -i
findmnt
```

## Step 9 — Prevention

Examples:

```text
retention policies
log rotation
temporary-directory placement
dedicated data disks
capacity alerts
growth forecasting
small-file compaction
workload concurrency limits
runbook updates
```

---

# 55. Common Mistakes

## Mistake 1 — Blindly deleting large files

Size does not imply expendability.

## Mistake 2 — Deleting files owned by active processes

This may create deleted-open files or disrupt the application.

## Mistake 3 — Confusing `df` with `du`

Remember:

```text
df = filesystem accounting
du = directory-tree accounting
```

## Mistake 4 — Ignoring inode exhaustion

Always consider:

```bash
df -i
```

during a mysterious file-creation failure.

## Mistake 5 — Ignoring deleted-open files

If:

```text
df >> du
```

investigate `lsof`.

## Mistake 6 — Filling the root filesystem with temporary data

Use appropriate storage placement.

## Mistake 7 — Unbounded temporary directories

Temporary does not mean small.

## Mistake 8 — Running `mkfs` against the wrong disk

This can destroy data.

## Mistake 9 — Trusting `/dev/sdX` for persistent storage

Use stable identifiers such as UUIDs.

## Mistake 10 — Editing `/etc/fstab` without testing

Validate with:

```bash
mount -a
```

before rebooting.

## Mistake 11 — Forgetting that mounting hides underlying files

A mount can make pre-existing files underneath the mount point invisible.

## Mistake 12 — Decompressing huge files unnecessarily

Use streaming decompression.

## Mistake 13 — Loading huge files entirely into RAM

Use streaming, batching, or external processing.

## Mistake 14 — Sorting huge files without planning temporary disk

External sort can consume substantial space.

## Mistake 15 — Running inode-exhaustion experiments on production

Never.

## Mistake 16 — Running disk-fill experiments on production

Never.

## Mistake 17 — Assuming every application respects `TMPDIR`

Verify actual behavior.

## Mistake 18 — Assuming more disk fixes bad file-layout design

Millions of tiny files can remain operationally expensive.

## Mistake 19 — Failing to plan peak temporary usage

Average usage is not enough.

## Mistake 20 — Ignoring growth rate

A filesystem at 70% today may be an incident tomorrow if growth is rapid.

## Mistake 21 — Treating "disk full" as only a cleanup problem

The real fix may be:

```text
storage placement
retention
concurrency
compaction
capacity planning
application configuration
```

---

# 56. Command Reference

| Command | Purpose | Typical example | Inspect | Common mistake | Production caution |
|---|---|---|---|---|---|
| `df -h` | Filesystem capacity | `df -h` | `Used`, `Avail`, `Use%` | assuming it identifies the largest directory | confirm filesystem/mount |
| `df -i` | Inode capacity | `df -i` | `IUse%`, `IFree` | checking only bytes | use for file-creation failures |
| `du -sh` | Directory summary | `du -sh /data` | total tree usage | scanning huge trees blindly | bound the scope |
| `du -h --max-depth=1` | Top-level usage | `du -h --max-depth=1 /data` | large directories | confusing it with `df` | use targeted scans |
| `ncdu` | Interactive usage analysis | `ncdu /data` | directory hierarchy | assuming it is free of scan cost | permissions and size matter |
| `lsof` | Open-file/process inspection | `lsof +L1` | process/file descriptor | restarting without diagnosis | identify owner first |
| `lsof +L1` | Deleted-open files | `lsof +L1` | deleted-open descriptors | "delete again" | release descriptor safely |
| `lsblk` | Block-device topology | `lsblk` | disks/partitions/mounts | assuming device names | verify target before writes |
| `blkid` | Filesystem identity | `blkid` | UUID/type | copying wrong UUID | verify device |
| `mount` | Mount inspection/action | `mount` | active mounts | mounting over populated paths | understand hidden files |
| `findmnt` | Focused mount inspection | `findmnt /data` | source/type/options | assuming directory means mounted | verify expected filesystem |
| `mount -a` | Test fstab mounts | `sudo mount -a` | configuration validity | rebooting first | validate before reboot |
| `head` | Inspect beginning | `head -n 20 file` | first records | treating as full validation | file format may need deeper checks |
| `tail` | Inspect end | `tail -n 20 file` | final records | assuming tail works efficiently for every special format | understand file type |
| `wc -l` | Count newline characters | `wc -l file` | line count | assuming exact record count for arbitrary formats | still scans the file |
| `split` | Split files | `split -l 1000000 file chunk_` | chunking | breaking CSV semantics | understand record boundaries |
| `zcat` | Stream gzip | `zcat file.gz \| head` | decompressed stream | fully decompressing first | consumer must handle stream |
| `zstdcat` | Stream Zstandard | `zstdcat file.zst \| head` | decompressed stream | creating unnecessary copy | verify tool availability |
| `sort` | Sorting/external sorting | `sort -T /data/tmp file` | sorted output/temp usage | ignoring temp disk | monitor storage |
| `zstd` | Compression | `zstd file` | output size/time | assuming one level is best | CPU/storage trade-off |
| `pigz` | Parallel gzip | `pigz file` | throughput/output | ignoring CPU contention | consider concurrent workload |

---

# 57. Practice Questions

## 57.1 Conceptual

1. What is the difference between a block device and a filesystem?
2. What is a mount point?
3. What question does `df` answer?
4. What question does `du` answer?
5. Why can `df` and `du` disagree?
6. What is an inode?
7. Why can a filesystem have free bytes but no free inodes?
8. Why are millions of tiny files dangerous?
9. What is a deleted-but-open file?
10. Why can deleted-open files remain visible to `df` but not `du`?
11. Why are temporary files important in Data Engineering?
12. Why can a Spark job consume much more disk than its final output?
13. Why should a data disk sometimes be separate from the root filesystem?
14. What does UUID-based mounting solve?
15. Why should `fstab` be validated before reboot?
16. What does `nofail` conceptually accomplish?
17. Why might a large analytical query use temporary disk?
18. Why is streaming decompression useful?
19. How does external sorting handle data larger than RAM?
20. Why does compression involve both CPU and storage trade-offs?

## 57.2 Command Questions

21. Which command checks filesystem usage?
22. Which command checks inode usage?
23. How do you inspect the top-level usage of `/data`?
24. How do you interactively inspect disk usage?
25. How do you find deleted-open files?
26. How do you inspect block devices?
27. How do you find a filesystem UUID?
28. How do you inspect the mount for `/data`?
29. How do you validate `/etc/fstab` without rebooting?
30. How do you inspect the first 20 lines of a huge CSV?
31. How do you count newline-delimited records?
32. How do you stream a gzip file to `head`?
33. How do you direct `sort` temporary files to `/data/tmp`?

## 57.3 Output Interpretation

Given:

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        80G   76G  4G   95% /
/dev/sdb1       500G  210G 290G  43% /data
```

34. Which filesystem is at immediate capacity risk?
35. Is `/data` currently the problem?
36. What should you inspect next?

Given:

```text
Filesystem      Inodes  IUsed  IFree IUse%
/dev/root       5000000 4995000 5000 100%
```

37. What type of exhaustion is this?
38. What type of workload might cause it?
39. What would you investigate?

Given:

```text
df -h → 90% used
du    → only 60% explained
```

40. What hypotheses should you test?

## 57.4 Incident Scenarios

41. A pipeline reports `No space left on device`. Build your first five commands.
42. A Spark job has small output but fails during a shuffle. What storage questions do you ask?
43. A server has millions of tiny files. Why might adding 1 TB not solve the immediate operational problem?
44. A log file was deleted but disk space did not return. Explain.
45. A data disk is missing after reboot. What do you inspect?
46. A 20 GB compressed CSV must be sorted on a 4 GB RAM server. Design the workflow.
47. A large sort fills `/`. How would you prevent recurrence?
48. A Python workflow creates large temporary files on `/tmp`. How would you investigate and redirect future temporary data?
49. A server has a full root filesystem but a mostly empty `/data` filesystem. What design problem might exist?
50. A production cleanup script deletes files by size alone. Why is this dangerous?

## 57.5 Design Questions

51. Design storage for two concurrent batch jobs with high temporary usage.
52. How would you separate raw, intermediate, temporary, logs, and outputs?
53. What information should a disk-capacity alert contain?
54. How would you project future disk exhaustion?
55. What retention questions should be answered before deleting old exports?
56. How would you prevent small-file inode exhaustion?
57. How would you make an optional data mount failure-tolerant?
58. What evidence would justify restarting a service because of a deleted-open file?

---

# 58. Interview Questions with Model Answers

## Beginner

### 1. What is the difference between disk space and inodes?

**Model answer:** Disk space represents storage blocks available for file data, while inodes represent filesystem metadata structures used to track files and directories. A filesystem can have free bytes but no free inodes, preventing creation of additional files.

### 2. What does `df -h` show?

**Model answer:** `df` reports filesystem-level capacity and usage. `-h` makes the values human-readable. It tells me which filesystem is full but not directly which directory consumed the space.

### 3. What does `du` show?

**Model answer:** `du` estimates the space consumed by files and directories in a filesystem tree. It is useful for locating large directories and files.

### 4. Why can a filesystem have free space but no inodes?

**Model answer:** A workload can create a very large number of tiny files. The files may consume relatively few data blocks while consuming most available inode structures.

### 5. What is a mount point?

**Model answer:** A mount point is a directory where a filesystem is attached to the Linux directory hierarchy.

## Intermediate

### 6. Why can `df` and `du` disagree?

**Model answer:** Possible reasons include deleted-but-open files, different mounts, hidden files beneath mount points, and filesystem-level metadata or reserved space. I would investigate rather than assume that missing `du` usage means the filesystem is healthy.

### 7. What is a deleted-but-open file?

**Model answer:** The directory entry has been removed, but a running process still has the file open. The filesystem blocks remain allocated until the open reference is released.

### 8. How would you find deleted-open files?

**Model answer:**

```bash
lsof +L1
```

Then I would identify the process, understand its ownership and lifecycle, and use a safe close/rotation/restart procedure if appropriate.

### 9. Why should `/etc/fstab` generally use UUIDs?

**Model answer:** Device names such as `/dev/sdb1` are not guaranteed to remain stable across environments or boots. UUIDs provide a stable filesystem identity.

### 10. Why can a Spark job fill a server's disk even when output is small?

**Model answer:** Spark may generate large intermediate local data during shuffle, sort, join, aggregation, or spill. Peak temporary usage can be much larger than final output.

### 11. Why should temporary data sometimes live on a separate filesystem?

**Model answer:** Isolation prevents a temporary or spill-heavy workload from consuming the root filesystem and destabilizing the operating system or unrelated services.

## Advanced

### 12. How would you diagnose `No space left on device` in production?

**Model answer:**

```text
df -h
→ identify filesystem
→ df -i
→ determine blocks vs inodes
→ du/ncdu for consumers
→ lsof +L1 if df/du disagree
→ lsblk/findmnt for storage topology
→ identify workload and ownership
→ reclaim safely
→ verify
→ prevent recurrence
```

### 13. How would you safely process a 20 GB compressed CSV on a memory-constrained server?

**Model answer:** I would avoid full decompression and full in-memory loading. I would inspect and stream it using `zcat` or `zstdcat`, use incremental processing or an external sort if needed, place temporary data on a dedicated filesystem, monitor disk usage, and verify the output.

### 14. How does external sorting work when data exceeds RAM?

**Model answer:** The sorter processes manageable chunks, sorts them, writes temporary runs to disk, and then merges those runs. Therefore external sorting trades memory pressure for disk I/O and temporary storage.

### 15. What are the trade-offs between compression ratio, CPU, I/O, and storage?

**Model answer:** Higher compression can reduce storage and network transfer but usually requires more CPU and time. Faster compression can use more storage but reduce pipeline latency. The correct choice depends on workload and infrastructure constraints.

### 16. How would you prevent a temporary spill workload from taking down the operating system?

**Model answer:** Separate temporary/spill storage from critical root storage when appropriate, provision enough peak capacity, monitor disk and inode usage, set sensible workload/concurrency limits, establish cleanup/retention policies, and alert before critical thresholds.

---

# 59. Knowledge Check

You should be able to answer **yes** to each item before considering Topic 07 complete.

- [ ] Can I explain disk vs filesystem?
- [ ] Can I use `df`?
- [ ] Can I use `du`?
- [ ] Can I use `ncdu`?
- [ ] Can I identify common Data Engineering space consumers?
- [ ] Can I explain inodes?
- [ ] Can I diagnose inode exhaustion?
- [ ] Can I find deleted-but-open files?
- [ ] Can I use `lsof`?
- [ ] Can I inspect block devices?
- [ ] Can I safely mount a data disk in a disposable environment?
- [ ] Can I use UUIDs for persistent mounts?
- [ ] Can I validate `fstab` safely?
- [ ] Can I explain `nofail`?
- [ ] Can I place temporary files on the correct filesystem?
- [ ] Can I explain `TMPDIR`?
- [ ] Can I explain Spark local/spill storage?
- [ ] Can I explain DuckDB temporary storage?
- [ ] Can I inspect huge files safely?
- [ ] Can I use `head`, `tail`, and `wc`?
- [ ] Can I use `split` appropriately?
- [ ] Can I inspect compressed files without fully decompressing them?
- [ ] Can I use external sorting?
- [ ] Can I control sort temporary storage?
- [ ] Can I explain `zstd` and `pigz`?
- [ ] Can I reason about compression trade-offs?
- [ ] Can I diagnose `No space left on device`?
- [ ] Can I write a production disk-incident runbook?

---

# 60. Production Decision Framework

When choosing a remediation, classify the problem first.

| Situation | First question | Typical direction |
|---|---|---|
| Root filesystem full | What consumes it? | identify logs/temp/application |
| Data filesystem full | What workload owns growth? | retention/capacity/layout |
| Inodes full | Why are there so many entries? | small-file investigation |
| `df` > `du` | What is hidden from directory accounting? | `lsof`, mounts |
| Spark failure | Where is local/spill storage? | inspect Spark temp filesystem |
| Sort failure | Where are temporary runs? | dedicated temp filesystem |
| Missing data disk | Is the expected mount active? | `findmnt`, `lsblk`, `fstab` |
| Huge compressed file | Do I need a full decompressed copy? | stream |
| Rapid growth | How fast is it growing? | forecast and alert |

---

# 61. Three-Minute Operator Reference

When you receive:

```text
No space left on device
```

run the investigation mentally as:

```text
1. Which filesystem?
   df -h

2. Blocks or inodes?
   df -i

3. Which directories?
   du / ncdu

4. Does df match du?
   If not: lsof +L1 / findmnt

5. What workload?
   logs / temp / spill / exports / cache / application

6. Is the expected data disk mounted?
   lsblk / findmnt

7. What can safely be reclaimed?
   ownership + retention + activity

8. Verify.
   df -h
   df -i

9. Prevent recurrence.
   placement + retention + alerts + capacity planning
```

---

# 62. Core Mental Models

## Storage Model

```text
BLOCK DEVICE
      ↓
FILESYSTEM
      ↓
MOUNT POINT
      ↓
DIRECTORIES
      ↓
FILES
```

## Disk Incident Model

```text
DISK FULL
   ↓
df -h
   ↓
WHICH FILESYSTEM?
   ↓
df -i
   ↓
SPACE OR INODES?
   ↓
du / ncdu
   ↓
WHICH DATA?
   ↓
lsof
   ↓
ANY DELETED-OPEN FILES?
   ↓
lsblk / findmnt
   ↓
FIX
   ↓
VERIFY
   ↓
PREVENT
```

## Large-File Model

```text
Huge file
   ↓
Do not automatically load it into RAM
   ↓
Inspect
   ↓
Stream
   ↓
Compress/decompress through pipes
   ↓
Split when appropriate
   ↓
External-sort when necessary
   ↓
Use dedicated temporary storage
   ↓
Monitor disk usage
```

## Data Engineering Storage Model

```text
RAW DATA
   +
INTERMEDIATE DATA
   +
TEMPORARY DATA
   +
SPILL DATA
   +
LOGS
   +
EXPORTS
   +
CACHE
        ↓
STORAGE CAPACITY
        +
INODE CAPACITY
        +
I/O CAPACITY
        ↓
SERVER HEALTH
```

---

# 63. Production Safety Rules

The following rules should become habitual:

1. **Measure before deleting.**
2. **Measure before restarting.**
3. **Identify ownership before changing data.**
4. **Check retention requirements.**
5. **Distinguish active data from disposable data.**
6. **Treat `mkfs` as destructive.**
7. **Verify devices before filesystem operations.**
8. **Validate `fstab` before rebooting.**
9. **Never run disk-fill or inode-exhaustion experiments on production.**
10. **Do not assume `TMPDIR` is honored without verification.**
11. **Plan for peak temporary usage, not only average usage.**
12. **Verify the fix at the filesystem and application levels.**
13. **Document the root cause and prevention step.**

---

# 64. Scope Boundaries

This module intentionally does **not** become a complete course on:

- advanced filesystem internals;
- RAID;
- LVM;
- Kubernetes storage;
- cloud storage architecture;
- Spark internals;
- Prometheus;
- Grafana;
- database administration.

Those areas may be mentioned when directly relevant, but they remain awareness/context unless explicitly required elsewhere in the roadmap.

The target capability is:

> **A Data Engineer who can reason about Linux storage, diagnose disk/inode exhaustion, safely operate data disks and temporary storage, and process large files without creating avoidable resource failures.**

---

# 65. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Where Taught |
|---|---|---|
| Finding space usage with `du` | ✅ Covered | Sections 5–6 |
| Sorting `du` results | ✅ Covered | Sections 5–6 |
| Depth limits | ✅ Covered | Section 5 |
| `ncdu` | ✅ Covered | Section 7 |
| Logs as space consumers | ✅ Covered | Section 8 |
| Temporary directories | ✅ Covered | Sections 8, 20–22 |
| Spark spill files | ✅ Covered | Sections 8, 23 |
| pandas temporary data | ✅ Covered | Sections 8, 22 |
| Package/pip caches | ✅ Covered | Section 8 |
| Docker data | ✅ Covered | Section 8 |
| Old exports | ✅ Covered | Section 8 |
| Inodes | ✅ Covered | Sections 9–10 |
| `df -i` | ✅ Covered | Section 9 |
| Millions of tiny files | ✅ Covered | Section 10 |
| Deleted-but-open files | ✅ Covered | Section 11 |
| `lsof` | ✅ Covered | Sections 11–12 |
| `lsblk` | ✅ Covered | Section 13 |
| Data disk | ✅ Covered | Sections 14, 37 |
| Filesystem creation | ✅ Covered | Sections 14–15 |
| Mounting | ✅ Covered | Sections 16–17 |
| Persistent mounts | ✅ Covered | Section 17 |
| UUID | ✅ Covered | Section 17 |
| `/etc/fstab` | ✅ Covered | Section 17 |
| Failure-tolerant mounting | ✅ Covered | Section 18 |
| `TMPDIR` | ✅ Covered | Section 21 |
| Spark local directories | ✅ Covered | Section 23 |
| DuckDB temporary directory | ✅ Covered | Section 24 |
| Large-file inspection | ✅ Covered | Sections 25–27 |
| `head` / `tail` | ✅ Covered | Section 26 |
| Line counting | ✅ Covered | Section 27 |
| `split` | ✅ Covered | Section 28 |
| `zcat` | ✅ Covered | Section 29 |
| `zstdcat` | ✅ Covered | Section 29 |
| External sorting | ✅ Covered | Sections 30–32 |
| sort buffer | ✅ Covered | Section 31 |
| sort temporary directory | ✅ Covered | Sections 31–32 |
| Parallel compression | ✅ Covered | Section 33 |
| `zstd` | ✅ Covered | Section 33 |
| `pigz` | ✅ Covered | Section 33 |
| Compression levels | ✅ Covered | Section 34 |
| Filesystem awareness | ✅ Covered | Section 35 |
| Mount-option awareness | ✅ Covered | Section 35 |
| Disk usage alerts | ✅ Covered | Section 36 |
| Growth-rate projections | ✅ Covered | Section 36 |
| CPU/I/O/storage trade-offs | ✅ Covered | Sections 32–34, 36 |
| Production diagnosis | ✅ Covered | Sections 38–39 |
| `server_lab/07` | ✅ Covered | Sections 40–45 |
| Large-file lab | ✅ Covered | Section 45 |
| Inode exhaustion lab | ✅ Covered | Section 41 |
| Deleted-open-file lab | ✅ Covered | Section 42 |
| Data-disk lab | ✅ Covered | Section 43 |
| Temporary-directory lab | ✅ Covered | Section 44 |
| Checkpoint | ✅ Covered | Section 59 |
| Common mistakes | ✅ Covered | Section 55 |

**Audit result: all specified Topic 07 requirements are covered.**

---

# 66. Final Quality and Safety Audit

## Completeness

- Topic 07 scope is covered from storage fundamentals through production diagnosis.
- Required commands are explained with operational interpretation.
- Hands-on labs are included.
- Break/fix scenarios are included.
- Runbook and decision tree are included.
- Practice and interview sections are included.
- Final checkpoint and coverage audit are included.

## Progressive difficulty

```text
Basic
→ filesystem/storage model
→ df/du
→ inode diagnosis
→ mounts/data disks
→ temporary/spill placement
→ large-file processing
→ external sorting/compression
→ production incident response
```

## Teaching pattern

For difficult concepts, the module uses:

```text
simple explanation
→ technical explanation
→ command
→ example
→ interpretation
→ production application
```

## Safety

Destructive operations are explicitly marked, especially:

```text
mkfs
mount/umount
rm
filesystem-filling experiments
inode-exhaustion experiments
```

Disposable environments are required for destructive labs.

## Production mindset

The module consistently emphasizes:

```text
measure before deleting
measure before restarting
identify ownership
understand retention
verify the fix
prevent recurrence
```

## Credential hygiene

No real credentials, secrets, tokens, private keys, passwords, or production connection strings are required by the learning module. Use placeholders and disposable environments for practice.

---

# 67. Completion Criteria

Topic 07 is complete when the learner can independently handle an incident such as:

```text
"No space left on device"
```

using:

```text
Identify filesystem
    ↓
Determine blocks vs inodes
    ↓
Find consumers
    ↓
Investigate deleted-open files
    ↓
Inspect mounts/devices
    ↓
Identify workload
    ↓
Reclaim/fix safely
    ↓
Verify recovery
    ↓
Prevent recurrence
```

The learner should also be able to explain why:

```text
large file
≠
load everything into memory
```

and design a safe workflow using:

```text
streaming
+
compression
+
external sorting
+
dedicated temporary storage
+
capacity monitoring
```

The final skill is not memorizing:

```bash
df
du
lsof
lsblk
```

The final skill is being able to **think about storage as a production Data Engineer**.


---

# 68. Final Operator Exercise

Perform this exercise in a disposable Linux practice server.

## Situation

You receive:

```text
ALERT: / is 94% full
Pipeline failed: No space left on device
```

## Your task

Without deleting anything initially, produce an evidence-backed diagnosis.

Start with:

```bash
df -h
df -i
```

Then determine:

```text
1. Which filesystem is full?
2. Is it block or inode pressure?
3. Which top-level directory consumes the most space?
4. Is the expected data disk actually mounted?
5. Are there deleted-open files?
6. Is the consumer logs, temp, spill, cache, exports, Docker, or application data?
7. What is safe to reclaim?
8. What should be changed to prevent recurrence?
```

Use the appropriate commands:

```bash
du -h --max-depth=1 ...
ncdu ...
lsof +L1
lsblk
findmnt
```

For a large-file workload, demonstrate that you can avoid an unnecessary full decompressed copy:

```bash
zcat data.csv.gz | head -n 20
```

and, when appropriate:

```bash
zcat data.csv.gz | sort -T /data/tmp -S 2G > /data/output/sorted.csv
```

Finally, write a short incident note:

```text
Symptom:
Evidence:
Root cause:
Safe remediation:
Verification:
Prevention:
```

If you can complete this without guessing, you have reached the intended Topic 07 operational capability.
