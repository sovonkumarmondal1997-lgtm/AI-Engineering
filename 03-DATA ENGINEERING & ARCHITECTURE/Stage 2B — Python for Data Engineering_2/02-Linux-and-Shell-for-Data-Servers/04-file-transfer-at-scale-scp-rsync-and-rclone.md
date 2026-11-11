# Topic 04 — File Transfer at Scale: `scp`, `rsync`, and `rclone`

> **Stage 2B — Gap Module G2: Linux and Shell for Data Servers**  
> **Module:** 04 — File Transfer at Scale  
> **Audience:** Data Engineers operating Linux servers and data platforms  
> **Progression:** Beginner → Intermediate → Advanced → Production Operations

---

## Module Objective

This module teaches the operational skills required to move data reliably between Linux systems and object storage.

The goal is not to memorize commands. The goal is to develop the judgment to answer:

> **What data am I moving, where is it going, what can go wrong, how can I resume it, how can I prove it arrived intact, and how do I avoid harming production while moving it?**

By the end, you should be comfortable moving small files, large directory trees, multi-gigabyte datasets, archives, and object-storage data while understanding the consequences of synchronization, deletion, bandwidth consumption, and cloud data movement.

---

## Scope and Boundaries

This is **Topic 04 of G2 — Linux and Shell for Data Servers**.

### This module deeply covers

- file-transfer fundamentals
- `scp`
- `sftp` awareness
- bastion/jump-host transfers
- `rsync`
- archive mode
- progress reporting
- trailing-slash semantics
- `--dry-run`
- `--exclude`
- `--partial`
- resumable transfers
- `--delete` safety
- SHA-256 verification
- checksum manifests
- rsync checksum mode
- `rclone`
- S3, GCS, Azure Blob, and MinIO concepts
- `rclone copy`
- `rclone sync`
- `rclone check`
- parallel transfers
- bandwidth limiting
- huge-file strategies
- streaming archives
- `tar` over SSH
- on-the-fly compression with zstd
- bastion-based movement
- interruption and recovery
- cloud egress awareness
- managed-transfer awareness
- Data Engineering transfer scenarios
- break/fix
- troubleshooting
- production transfer runbooks

### This module does not deeply teach

- SSH fundamentals, keys, or key lifecycle — see Topic 01
- SSH tunneling — see Topic 02
- `tmux` — see Topic 03
- `systemd` — Topic 05
- CPU/memory monitoring — Topic 06
- disk and inode management — Topic 07
- `jq`, csvkit, Miller, or DuckDB — Topic 08
- log investigation — Topic 09
- users, sudo, packages, and server hygiene — Topic 10

Those topics may be referenced where they intersect with file transfer, but they are not repeated here.

---

# 1. What Does "Moving Data" Actually Mean?

At the simplest level, moving data means copying bytes from one storage location to another.

Common paths include:

```text
Laptop
   |
   v
Linux Server
```

```text
Server
   |
   v
Server
```

```text
Server
   |
   v
Object Storage
```

```text
Object Storage
   |
   v
Server
```

```text
Object Storage
   |
   v
Object Storage
```

A Data Engineer may move:

- partner files
- raw datasets
- batch exports
- database dumps
- pipeline outputs
- logs
- backups
- staging data
- Parquet datasets
- CSV datasets
- JSON/JSONL datasets
- archived data
- model-training datasets
- intermediate processing results

The operational problem becomes much more interesting when the dataset is large.

> **How do we move potentially huge amounts of data reliably without corruption, accidental deletion, unnecessary retransmission, or unnecessary network cost?**

That is the problem this module solves.

---

# 2. Why File Size Changes the Engineering Problem

A 10 MB transfer and a 1 TB transfer are both "copy operations," but operationally they are very different.

Consider:

```text
10 MB
100 MB
10 GB
100 GB
1 TB+
```

For small data, a failed transfer may be an inconvenience.

For a 1 TB transfer, failure can mean:

- hours of network utilization
- repeated CPU work
- repeated disk reads
- incomplete destination data
- expensive cloud egress
- production network contention
- difficult recovery
- operator uncertainty

Large transfers require reasoning about:

- network bandwidth
- transfer duration
- interruptions
- retries
- resumability
- destination disk capacity
- CPU
- compression
- integrity
- cloud egress
- destination capacity
- source-file stability
- remote API limits

## 2.1 A Simple Transfer-Time Model

Ignoring protocol overhead and other bottlenecks:

```text
transfer time ≈ data size / effective throughput
```

For example, a nominal 100 GB dataset at an effective 100 MB/s takes approximately:

```text
100,000 MB / 100 MB/s
≈ 1,000 seconds
≈ 16.7 minutes
```

At an effective 20 MB/s:

```text
100,000 MB / 20 MB/s
≈ 5,000 seconds
≈ 83 minutes
```

Real transfers can be slower because of:

- protocol overhead
- disk speed
- CPU
- encryption
- compression
- network congestion
- object-storage API behavior
- remote throttling
- many-small-file metadata overhead

The lesson is not to become a networking mathematician.

The lesson is:

> **At scale, transfer time and resource consumption become operational concerns.**

---

# 3. The Three Main Tools

This module centers on three tools:

```text
scp
rsync
rclone
```

A useful first mental model is:

```text
ONE-OFF SSH FILE
       |
      scp

REPEATED SERVER SYNCHRONIZATION
       |
     rsync

OBJECT STORAGE / CLOUD DATA MOVEMENT
       |
     rclone

STREAMING ARCHIVE
       |
tar + SSH + compression
```

This is a starting point, not a rigid law. Tool choice depends on the source, destination, size, reliability requirements, synchronization semantics, and operational constraints.

---

# 4. `scp` Fundamentals

## 4.1 What Is `scp`?

`scp` is a command-line file-copy utility that uses SSH to transfer files between systems.

Basic shape:

```bash
scp source destination
```

The important idea is:

```text
local/remote source
       |
       v
      SSH
       |
       v
local/remote destination
```

Because `scp` uses SSH-based transport, normal SSH authentication and connectivity rules apply.

---

## 4.2 Local → Remote

Example:

```bash
scp data.csv dataeng@server:/data/incoming/
```

Breakdown:

```text
scp
```

Run the secure-copy command.

```text
data.csv
```

Local source file.

```text
dataeng@server
```

Remote user and host.

```text
:/data/incoming/
```

Destination directory on the remote server.

Mental model:

```text
Laptop
  |
  | SSH transfer
  v
server:/data/incoming/data.csv
```

---

## 4.3 Remote → Local

Example:

```bash
scp dataeng@server:/data/output/result.csv ./result.csv
```

This means:

```text
Remote:
server:/data/output/result.csv

        |
        | SSH
        v

Local:
./result.csv
```

This is useful for retrieving:

- generated reports
- pipeline outputs
- diagnostic artifacts
- one-off exports
- completed database dumps

---

## 4.4 Remote → Remote

`scp` can also support remote-to-remote transfers, but exact behavior depends on the implementation and options used.

Do not assume that every remote-to-remote pattern behaves like a local-to-remote transfer.

For operational work, explicitly reason about:

```text
source host
destination host
authentication path
network path
where the bytes actually travel
```

When the workflow becomes repeated, large, resumable, or complex, `rsync` or `rclone` is usually a better starting point.

---

# 5. `scp` Directory Transfers

Use `-r` for recursive directory transfer:

```bash
scp -r dataset/ dataeng@server:/data/
```

This tells `scp` to recursively copy the directory tree.

Example:

```text
dataset/
├── raw/
│   ├── a.csv
│   └── b.csv
├── processed/
│   └── result.parquet
└── metadata.json
```

A recursive copy can move the directory tree to the remote host.

## Why `scp -r` is useful

It is useful for:

- small or moderate one-off directory transfers
- quick operational movement
- simple administrative workflows
- environments where `scp` is already available

## Why it is not usually the best tool for repeated large synchronization

Suppose you transferred:

```text
500 GB
```

yesterday and only:

```text
2 GB
```

changed today.

A synchronization-oriented tool can reason about the destination and avoid retransmitting unchanged data.

That is where `rsync` becomes much more useful.

> Do not dismiss `scp` as simply "old." Its operational value is simplicity. The trade-off is that it provides fewer synchronization-oriented controls than `rsync`.

---

# 6. `scp` Through a Bastion

A common production architecture is:

```text
Laptop
   |
   v
Bastion
   |
   v
Private Data Server
```

The private server is not directly reachable from the laptop.

With a jump host:

```bash
scp -o ProxyJump=bastion \
    dataset.csv \
    data-server:/data/incoming/
```

Conceptually:

```text
Laptop
   |
   | SSH connection through jump host
   v
Bastion
   |
   | onward SSH path
   v
Private Data Server
```

The important point is that the bastion is part of the SSH connection path.

If your Topic 01 SSH configuration already defines the bastion and `ProxyJump`, you can often use a short host alias instead:

```bash
scp dataset.csv data-server:/data/incoming/
```

provided the SSH configuration is set up appropriately.

Do not duplicate the full SSH-key and jump-host course here. The operational lesson is:

> **File transfer inherits the network reachability and SSH path used to reach the destination.**

---

# 7. `sftp` Awareness

`sftp` provides an interactive SSH-based file-transfer workflow.

Start it with:

```bash
sftp dataeng@server
```

Inside an SFTP session, commands such as:

```text
ls
pwd
cd
lcd
get
put
mkdir
```

can be used to navigate and transfer files.

A simple example:

```text
sftp> put report.csv /data/incoming/
sftp> get /data/output/result.csv
```

Use SFTP when an interactive file-transfer workflow is convenient.

This module does not turn SFTP into a separate course. The primary tools remain:

```text
scp
rsync
rclone
```

---

# 8. `scp` Limitations

`scp` is a strong choice for:

- one-off files
- simple transfers
- quick operational movement

It is less suitable for:

- interrupted multi-hour transfers
- repeated synchronization
- huge directory trees
- complex exclusions
- synchronization with deletion semantics
- integrity-aware synchronization workflows
- object storage

That leads to the next tool.

---

# 9. Why `rsync` Exists

Imagine:

```text
Yesterday:
500 GB transferred

Today:
2 GB changed
```

You do not want to retransmit the entire 500 GB if the destination can be updated incrementally.

`rsync` is designed around this problem.

High-level model:

```text
             compare
Source --------------------> Destination
  |                              |
  |                              |
  +------ transfer needed ------>|
```

The objective is:

> **Transfer only the data required to bring the destination up to date.**

This makes `rsync` especially valuable for:

- repeated server synchronization
- large directory trees
- backups
- staging datasets
- exports
- migrations
- incremental operational transfers

---

# 10. Basic `rsync`

Basic syntax:

```bash
rsync source destination
```

A common Data Engineering pattern is:

```bash
rsync -av source/ dataeng@server:/data/
```

Breakdown:

```text
rsync
```

The synchronization tool.

```text
-a
```

Archive mode.

```text
-v
```

Verbose output.

```text
source/
```

Local source directory contents.

```text
dataeng@server:/data/
```

Remote destination.

---

# 11. Archive Mode — `rsync -a`

Archive mode is commonly written:

```bash
rsync -a source/ destination/
```

Conceptually, archive mode enables a set of preservation behaviors appropriate for recursively copying a filesystem tree.

It generally includes:

- recursion
- preservation of permissions
- preservation of modification times
- preservation of symbolic links
- preservation of ownership/group metadata where possible
- preservation of relevant filesystem attributes included by archive mode

A useful conceptual expansion is:

```text
-a ≈ recursive + preserve important filesystem metadata
```

Actual ownership and group preservation depends on:

- operating system
- filesystem
- user privileges
- remote permissions
- platform behavior

Do not assume an unprivileged process can preserve metadata that it is not allowed to set.

---

# 12. Verbose and Progress Output

A practical command is:

```bash
rsync -av --progress source/ destination/
```

Important options:

```text
-v
    verbose output

--progress
    progress for individual files
```

For large transfers involving many files, a useful overall progress view is:

```bash
rsync -av --info=progress2 source/ destination/
```

`--info=progress2` provides an aggregate progress view rather than printing detailed progress for every file.

For huge directory trees, excessive verbosity can become noisy.

Operationally, choose output that helps answer:

```text
Is the transfer alive?
How much has moved?
Is throughput reasonable?
Is the command making the changes I expected?
```

---

# 13. Trailing-Slash Semantics — Critical rsync Knowledge

This is one of the most important details in the entire module.

Compare:

```bash
rsync -av data/ server:/backup/data/
```

with:

```bash
rsync -av data server:/backup/
```

They are not equivalent.

Suppose the source is:

```text
data/
├── a.csv
├── b.csv
└── c.csv
```

## 13.1 Source With a Trailing Slash

```bash
rsync -av data/ server:/backup/data/
```

Means:

> Copy the **contents** of `data/` into the destination.

Result:

```text
/backup/data/
├── a.csv
├── b.csv
└── c.csv
```

## 13.2 Source Without a Trailing Slash

```bash
rsync -av data server:/backup/
```

Means:

> Copy the **directory itself** into `/backup/`.

Result:

```text
/backup/
└── data/
    ├── a.csv
    ├── b.csv
    └── c.csv
```

## 13.3 Mental Model

```text
data/
   |
   +-- trailing slash
   |
   +--> contents

data
   |
   +-- no trailing slash
   |
   +--> directory itself
```

This is not cosmetic syntax.

A wrong slash can put a dataset at the wrong path, create unexpected nesting, or cause a later synchronization command to operate on the wrong directory.

Before a production transfer:

```bash
pwd
ls
```

and explicitly verify the intended source and destination.

Then use:

```bash
--dry-run
```

when appropriate.

---

# 14. `--dry-run`: Predict Before You Change

`--dry-run` is one of the most important safety features in operational file movement.

Example:

```bash
rsync -av --dry-run source/ destination/
```

It asks rsync to show the changes it intends to make without performing the actual synchronization.

Mental model:

```text
Predict
   ↓
Dry-run
   ↓
Inspect
   ↓
Execute
   ↓
Verify
```

Make this habit especially strong before:

- large synchronizations
- new commands
- unfamiliar paths
- destructive operations
- `--delete`

---

# 15. `--exclude`

Suppose a dataset contains:

```text
dataset/
├── raw/
├── processed/
├── logs/
├── temp/
└── checkpoints/
```

You may not want to transfer logs and temporary files.

Example:

```bash
rsync -av \
    --exclude '*.tmp' \
    --exclude 'logs/' \
    source/ destination/
```

Important ideas:

- exclusion patterns control which paths are skipped
- directory patterns should be written intentionally
- pattern behavior depends on where the pattern matches in the tree
- test complex exclusion rules with `--dry-run`

A safe workflow is:

```bash
rsync -av \
    --dry-run \
    --exclude '*.tmp' \
    --exclude 'logs/' \
    source/ destination/
```

Inspect the output before executing the real transfer.

---

# 16. `--delete`: Powerful and Dangerous

Consider:

```bash
rsync -av --delete source/ destination/
```

The important meaning is:

> Files that exist at the destination but no longer exist in the source may be deleted.

Example:

```text
SOURCE                         DESTINATION

a.csv                          a.csv
b.csv                          b.csv
                               old.csv
```

With synchronization semantics:

```text
source/ → destination/
```

and `--delete`, the extra:

```text
old.csv
```

may be removed.

This is exactly what you want when creating a true mirror.

It is also exactly what you do **not** want when the destination contains data that must be retained.

---

# 17. Safe `--delete` Workflow

Never treat this as a casual copy/paste command:

```bash
rsync -av --delete source/ destination/
```

First perform:

```bash
rsync -av --delete --dry-run source/ destination/
```

Then inspect the output.

Ask:

1. Is the source correct?
2. Is the destination correct?
3. Is the trailing slash correct?
4. Are the deletions expected?
5. Are excluded files handled correctly?
6. Is this definitely the intended mirror?

Only then execute:

```bash
rsync -av --delete source/ destination/
```

Operational rule:

> **Dry-run → inspect → execute → verify.**

Never demonstrate destructive synchronization against real production data while learning.

---

# 18. `--partial` and Interrupted Transfers

Suppose you transfer:

```text
100 GB
```

and the transfer reaches:

```text
70 GB
```

before the network disconnects.

```text
100 GB file
     |
     v
70 GB transferred
     |
     X network failure
```

A default interrupted transfer may leave no usable partial file, depending on rsync's temporary-file behavior and options.

With:

```bash
rsync --partial ...
```

rsync keeps the partially transferred file instead of discarding it.

For example:

```bash
rsync -av --partial \
    large-file.bin \
    dataeng@server:/data/
```

When the command is run again, rsync can use the existing partial destination state to avoid unnecessary retransmission.

For more controlled environments, rsync also supports a partial-directory pattern such as:

```bash
rsync -av --partial-dir=.rsync-partial \
    source/ destination/
```

This can keep incomplete transfer state separate from final filenames.

Do not assume every transfer resumes identically under every combination of options, filesystems, and source changes. Always verify the final destination.

---

# 19. Interruption and Resume Lab

Use synthetic data only.

Create a large test file:

```bash
mkdir -p ~/data-transfer-lab/source ~/data-transfer-lab/destination

dd if=/dev/zero \
   of=~/data-transfer-lab/source/large-file.bin \
   bs=1M \
   count=2048
```

This creates a roughly 2 GiB synthetic file.

Start:

```bash
rsync -av --partial --progress \
    ~/data-transfer-lab/source/ \
    ~/data-transfer-lab/destination/
```

Interrupt it deliberately:

```text
Ctrl-C
```

Inspect:

```bash
ls -lh ~/data-transfer-lab/destination/
```

Restart:

```bash
rsync -av --partial --progress \
    ~/data-transfer-lab/source/ \
    ~/data-transfer-lab/destination/
```

Observe:

- whether a partial file remains
- how much data is transferred on retry
- whether the destination reaches the expected size
- whether the final checksum matches

The objective is not merely "make the command work."

The objective is to understand:

> **What state exists after failure, and how does the next invocation use that state?**

---

# 20. SHA-256 Integrity Verification

A transfer can report success without you independently verifying the resulting data.

Distinguish:

```text
Transfer completed
```

from:

```text
Transfer completed
+
Data integrity verified
```

For important data, use SHA-256.

Example:

```bash
sha256sum dataset.csv
```

Output resembles:

```text
<sha256-digest>  dataset.csv
```

The exact digest depends on the file.

A hash provides a content-derived fingerprint.

If the same file content is hashed independently at source and destination, matching SHA-256 values provide strong evidence that the contents match.

---

# 21. SHA-256 Manifest Workflow

For multiple files, create a manifest.

Example:

```bash
cd source/
sha256sum *.csv > checksums.sha256
```

The manifest looks conceptually like:

```text
<digest-1>  customers.csv
<digest-2>  orders.csv
<digest-3>  products.csv
```

Transfer the data and the manifest.

At the destination:

```bash
cd destination/
sha256sum -c checksums.sha256
```

Expected successful output resembles:

```text
customers.csv: OK
orders.csv: OK
products.csv: OK
```

A failure may look like:

```text
orders.csv: FAILED
```

This gives you a repeatable verification workflow:

```text
Source
  |
  v
Generate SHA-256 manifest
  |
  v
Transfer data
  |
  v
Transfer manifest
  |
  v
Verify destination
```

## What a checksum proves

A matching checksum provides strong evidence that the bytes represented by the checked file match the bytes used to produce the reference digest.

## What a checksum does not prove

A checksum does not prove:

- that you copied the correct dataset
- that the source itself was correct
- that the business data is semantically valid
- that the destination path is the one you intended
- that a file was not changed after the checksum was generated

Integrity is one layer of operational correctness, not the entire correctness model.

---

# 22. rsync Checksum Mode

Rsync normally uses metadata such as file size and modification time to decide whether a file appears unchanged.

Checksum mode:

```bash
rsync -avc source/ destination/
```

The `-c` option tells rsync to use file-content checksums when determining whether files differ.

Conceptually:

```text
Normal rsync
metadata comparison
       ↓
decide whether to transfer

rsync -c
content checksum comparison
       ↓
decide whether to transfer
```

Checksum mode can be useful when metadata cannot be trusted as the sole change indicator.

The trade-off is important:

- files must be read to calculate checksums
- this increases disk I/O
- it can increase CPU work
- large datasets can take significant time to scan

Therefore:

> `-c` is a tool for a specific integrity/comparison need, not a flag that should automatically be added to every transfer.

---

# 23. rsync over SSH

The common production pattern is:

```bash
rsync -av \
    source/ \
    dataeng@server:/data/
```

For remote synchronization, rsync commonly uses SSH as its transport.

Conceptually:

```text
Local filesystem
      |
      v
    rsync
      |
      | SSH
      | encrypted transport
      v
Remote rsync
      |
      v
Remote filesystem
```

The SSH layer provides:

- authentication
- encrypted transport
- remote connectivity

The rsync layer provides:

- synchronization logic
- incremental transfer behavior
- metadata handling
- exclusions
- deletion semantics
- progress reporting
- partial-transfer handling

This separation is useful to understand.

---

# 24. rsync Through a Bastion

If the destination is reachable only through a bastion, reuse the SSH path established in Topic 01.

For example:

```bash
rsync -av \
    -e 'ssh -J bastion' \
    source/ \
    data-server:/data/incoming/
```

The conceptual path is:

```text
Laptop
   |
   v
Bastion
   |
   v
Private Data Server
```

A more maintainable production setup is often to put the `ProxyJump` relationship in SSH configuration and let rsync invoke SSH normally:

```bash
rsync -av \
    source/ \
    data-server:/data/incoming/
```

provided the SSH config already defines the jump path.

The data path remains:

```text
source
  ↓
laptop
  ↓
bastion path
  ↓
private server
```

Do not confuse a bastion with a permanent staging area. A jump host is primarily a connectivity path unless the architecture explicitly makes it a transfer server.

---

# 25. Large Dataset Transfer Architecture

A realistic Data Engineering environment may look like:

```text
Partner Files
     |
     v
Bastion / Transfer Server
     |
     v
Data Server
     |
     v
Object Storage
```

Different edges may use different tools.

For example:

```text
Partner → Linux server
        |
       scp/rsync

Linux server → Object Storage
        |
      rclone

Server → Server
        |
      rsync
```

Tool choice follows the destination and operational semantics.

---

# 26. `rclone`: Why It Exists

`rclone` is designed for working with filesystems and many remote storage systems, including object-storage services.

A useful mental model:

```text
Local filesystem
       |
       v
     rclone
       |
       v
Remote/object storage
```

Common object-storage targets include:

- Amazon S3
- Google Cloud Storage
- Azure Blob Storage
- MinIO
- other supported remote backends

`rclone` is particularly useful when the destination is not simply another Linux filesystem reachable through SSH.

---

# 27. Object Storage Mental Model

Object storage is commonly organized conceptually as:

```text
bucket
  |
  +-- prefix/
       |
       +-- file.parquet
       +-- file-002.parquet
```

Do not over-interpret filesystem semantics.

Object storage is not simply "a remote Linux disk."

It is typically accessed through an API, and operations can involve:

- object metadata
- API calls
- remote consistency characteristics
- request limits
- concurrency
- object lifecycle rules
- network transfer
- storage costs
- data-transfer costs

For this module, focus on operator behavior rather than provider certification details.

---

# 28. Configured `rclone` Remotes

`rclone` uses named remotes.

Conceptual examples:

```text
s3prod:
gcsarchive:
azurearchive:
minio:
```

A remote name is just a configured profile. The exact name depends on the environment.

For example:

```text
s3prod:company-data/exports
```

could conceptually mean:

```text
remote = s3prod
bucket = company-data
prefix = exports
```

Protect the configuration and credentials used by rclone.

Never put real credentials into a learning module or commit them to source control.

Useful awareness command:

```bash
rclone listremotes
```

This shows configured remote names.

---

# 29. `rclone copy`

Basic pattern:

```bash
rclone copy source remote:path
```

Example:

```bash
rclone copy ./exports s3prod:data/exports
```

The important semantic distinction is:

> **`copy` transfers new and changed data without making the destination an exact mirror by deleting unrelated destination objects.**

Conceptually:

```text
SOURCE
a.csv
b.csv

DESTINATION
a.csv
b.csv
old.csv

rclone copy

DESTINATION
a.csv
b.csv
old.csv
```

The unrelated `old.csv` is not automatically removed just because it is absent from the source.

This often makes `copy` a safer starting point for data movement.

---

# 30. `rclone sync`

Basic pattern:

```bash
rclone sync source remote:path
```

Its goal is synchronization:

> **Make the destination reflect the source.**

This can involve deleting destination objects that are not present in the source.

Example:

```text
SOURCE
a.parquet
b.parquet

DESTINATION
a.parquet
b.parquet
old.parquet
```

A sync operation may remove:

```text
old.parquet
```

Therefore:

```text
rclone copy
```

and:

```text
rclone sync
```

must never be treated as interchangeable.

---

# 31. `rclone sync` Safety

Before:

```bash
rclone sync source remote:path
```

use:

```bash
rclone sync --dry-run source remote:path
```

Inspect what it proposes.

A safe operational workflow is:

```text
Confirm source
      ↓
Confirm remote/path
      ↓
Dry-run
      ↓
Inspect additions/changes/deletions
      ↓
Execute
      ↓
Verify
```

Object storage can contain valuable historical or shared data. A synchronization command aimed at the wrong prefix can cause significant operational damage.

---

# 32. `rclone check`

Use:

```bash
rclone check source remote:path
```

The purpose is to compare source and destination and identify differences.

Conceptually:

```text
Local source
    |
    | compare
    v
Object-storage destination
    |
    v
Differences reported
```

This is useful after a transfer when you want an independent comparison rather than simply trusting that the transfer command returned successfully.

The exact comparison mechanisms depend on the backend and available metadata/checksum behavior.

---

# 33. Object Storage Examples

The remote names below are illustrative only.

## Amazon S3

```text
s3:bucket/path
```

## Google Cloud Storage

```text
gcs:bucket/path
```

## Azure Blob

```text
azure:container/path
```

## MinIO

```text
minio:bucket/path
```

The exact remote configuration depends on the environment.

Do not assume:

```text
s3:
gcs:
azure:
minio:
```

are automatically configured. They are examples of remote aliases.

---

# 34. Safe MinIO Practice Environment

If your broader Data Engineering lab already uses MinIO, it is an excellent target for practicing object-storage movement without requiring real cloud credentials.

A useful architecture is:

```text
Local Dataset
     |
     v
   rclone
     |
     v
   MinIO
```

Use synthetic data only.

Practice:

```text
copy
dry-run
sync
check
parallelism
bandwidth limiting
cleanup
```

This lets you learn destructive semantics without risking a real production bucket.

---

# 35. Parallel Transfers

For many-object workloads, transferring multiple objects concurrently can improve throughput.

Conceptually:

```text
Sequential

file A
  ↓
file B
  ↓
file C
  ↓
file D
```

versus:

```text
Parallel

file A ─┐
file B ─┼──> destination
file C ─┤
file D ─┘
```

Potential benefits:

- higher throughput
- better use of network capacity
- better utilization for many small objects

But more concurrency is not automatically better.

It can increase:

- CPU usage
- disk I/O
- memory use
- network utilization
- object-storage API requests
- remote throttling
- contention with production traffic

The engineering question is not:

> "How high can I make concurrency?"

It is:

> **"What concurrency gives acceptable throughput without violating system and service limits?"**

---

# 36. Transfer Throttling

An unrestricted transfer can consume shared resources.

It may:

- saturate network bandwidth
- increase application latency
- consume CPU
- consume disk I/O
- compete with production workloads
- hit object-storage request limits
- increase cloud-transfer costs in some architectures

For rclone, bandwidth limiting can be controlled with:

```bash
--bwlimit
```

For example, an illustrative limit:

```bash
rclone copy \
    --bwlimit 20M \
    ./exports \
    s3prod:data/exports
```

The exact acceptable limit should come from the environment and operational requirements.

Treat throttling as a production-safety control, not merely a performance penalty.

---

# 37. Choosing Parallelism and Throttling Together

These controls interact.

Suppose you increase concurrency:

```text
concurrency ↑
```

but leave bandwidth unrestricted:

```text
network demand ↑↑
```

You may get:

```text
throughput ↑
production impact ↑
```

A safer model is:

```text
Desired throughput
      |
      +--> concurrency
      |
      +--> bandwidth limit
      |
      +--> disk capacity
      |
      +--> remote API limits
```

Tune the system based on evidence.

Do not blindly maximize every knob.

---

# 38. Many Small Files vs Few Huge Files

These workloads behave differently.

## Many small files

```text
1,000,000 files × 1 MB
```

can involve substantial:

- filesystem metadata operations
- object-storage API requests
- directory traversal
- connection/request overhead

## Few huge files

```text
10 files × 100 GB
```

can be dominated by:

- sustained throughput
- retry behavior
- resumability
- disk bandwidth
- network duration

The best transfer strategy depends partly on the file shape.

This is one reason Data Engineering formats such as partitioned Parquet datasets can behave differently from a single giant archive.

---

# 39. Handling Huge Files

For huge files, think about:

- resumability
- stable source data
- destination capacity
- checksum verification
- network duration
- disk I/O
- compression
- parallel streams
- whether the file should exist as one object at all

Do not split a huge file simply because you can.

First ask:

> Is this file format and storage architecture appropriate for the workload?

For example, a multi-terabyte monolithic export may be less operationally convenient than a partitioned dataset when downstream systems can consume partitioned data.

---

# 40. Splitting Huge Files

Linux provides:

```bash
split
```

For example:

```bash
split -b 5G huge-file.bin part-
```

This creates chunks approximately 5 GiB each.

Conceptually:

```text
huge-file.bin
      |
      v
part-aa
part-ab
part-ac
...
```

Reassemble:

```bash
cat part-* > huge-file-restored.bin
```

Then verify integrity:

```bash
sha256sum huge-file.bin
sha256sum huge-file-restored.bin
```

## Why splitting can help

- smaller retry units
- easier movement through constrained systems
- parallel movement of independent chunks
- easier staging in some workflows

## Risks

- more files to track
- more metadata
- ordering concerns
- manifest management
- reassembly requirement
- application complexity

A better architecture may be to produce naturally partitioned data rather than repeatedly splitting and reassembling monolithic files.

---

# 41. Parallel Streams — Awareness

Large transfers can sometimes use multiple network streams or connections.

Potential benefit:

```text
single stream
     ↓
limited by one flow

multiple streams
     ↓
potentially higher aggregate throughput
```

But parallel streams also add:

- connection overhead
- complexity
- network contention
- remote-service load
- fairness concerns

The correct lesson is:

> **Parallelism is a resource-allocation decision, not a universal optimization.**

This module requires awareness and judgment, not mastery of every specialized multi-stream transfer product.

---

# 42. Streaming Archives Over SSH

Sometimes you want to transfer a directory without first creating an archive file on disk.

Use:

```bash
tar -cf - directory/ | \
ssh server 'tar -xf - -C /destination/'
```

Data flow:

```text
Local directory
      |
      v
tar creates stream
      |
      v
SSH transports stream
      |
      v
Remote tar extracts
      |
      v
Destination
```

The important detail is:

> **No intermediate archive file needs to be created on the source.**

---

# 43. Understanding `tar -cf -`

This command:

```bash
tar -cf - directory/
```

means approximately:

```text
-c    create archive
-f -  write archive to stdout
```

So instead of:

```bash
tar -cf archive.tar directory/
```

you produce a stream.

That stream is then piped into SSH.

---

# 44. On-the-Fly Compression With zstd

A streaming pattern is:

```bash
tar -cf - directory/ | \
zstd | \
ssh server 'zstd -d | tar -xf - -C /destination/'
```

Data flow:

```text
Directory
   |
   v
 tar
   |
   v
archive stream
   |
   v
 zstd compression
   |
   v
 SSH
   |
   v
 zstd decompression
   |
   v
 tar extraction
   |
   v
Destination
```

This avoids creating a large intermediate archive.

---

# 45. Why zstd Can Be Useful

zstd is useful because it provides a practical balance between:

- compression ratio
- compression speed
- decompression speed
- CPU consumption

Compression can reduce network transfer volume when the data is compressible.

But compression is not automatically beneficial.

For already-compressed formats such as:

```text
.parquet
.gz
.zip
.jpeg
.mp4
```

additional compression may provide little benefit while consuming CPU.

A useful decision model is:

```text
If network is the bottleneck
        |
        +--> compression may help

If CPU is the bottleneck
        |
        +--> compression may hurt

If data is already compressed
        |
        +--> compression may provide little benefit
```

---

# 46. Streaming vs Staging

## Staged archive

```text
Directory
   |
   v
Archive on disk
   |
   v
Transfer
   |
   v
Extract
```

Advantages:

- archive can be retained
- can be checksummed independently
- can be transferred later
- can be inspected as an artifact

Disadvantages:

- requires additional disk space
- creates an intermediate file
- may require time to build before transfer begins

## Streaming

```text
Directory
   |
   v
Archive stream
   |
   v
Compress
   |
   v
SSH
   |
   v
Decompress
   |
   v
Extract
```

Advantages:

- avoids intermediate archive storage
- can begin transferring immediately
- useful when disk space is constrained

Disadvantages:

- recovery can be less convenient
- a failure may require rerunning the stream
- verification requires deliberate design

Choose based on the operational situation.

---

# 47. Transfer Through a Bastion: Practical Pattern

Architecture:

```text
Laptop
   |
   v
Bastion
   |
   v
Private Server
```

## `scp`

```bash
scp -o ProxyJump=bastion \
    dataset.csv \
    data-server:/data/incoming/
```

## `rsync`

```bash
rsync -av \
    -e 'ssh -J bastion' \
    dataset/ \
    data-server:/data/incoming/dataset/
```

Or, if Topic 01 SSH configuration already defines the jump host:

```bash
rsync -av \
    dataset/ \
    data-server:/data/incoming/dataset/
```

The important operational question is:

> **Where do the bytes travel, and which host is actually carrying the traffic?**

A bastion architecture does not eliminate bandwidth or resource considerations.

---

# 48. Verifying a Multi-Hop Transfer

The network path can be complex:

```text
Source
  ↓
Laptop
  ↓
Bastion
  ↓
Private Server
  ↓
Destination
```

Integrity still follows a simple model:

```text
Source
  ↓
Transfer
  ↓
Destination
  ↓
Checksum verification
```

Generate a source checksum:

```bash
sha256sum dataset.tar.zst > dataset.tar.zst.sha256
```

Transfer both:

```bash
scp -o ProxyJump=bastion \
    dataset.tar.zst \
    dataset.tar.zst.sha256 \
    data-server:/data/incoming/
```

Then on the destination:

```bash
cd /data/incoming/
sha256sum -c dataset.tar.zst.sha256
```

The complexity of the network path does not remove the need for verification.

---

# 49. Transfer Interruption Scenarios

Large transfers fail in many ways.

## Scenario A — Network disconnect

```text
80 GB transfer
    |
    X
network failure
```

## Scenario B — SSH session drops

The transfer process may terminate if it was tied to the interactive session.

For long-running manual transfers, Topic 03's `tmux` can help keep the operator's shell alive:

```text
tmux
  |
  +--> rsync
```

Do not use tmux as a substitute for a proper service or orchestrated workflow.

## Scenario C — Laptop sleeps

The local network connection may disappear.

## Scenario D — Destination disk fills

The transfer may fail after significant data has already been written.

Check capacity before large transfers:

```bash
df -h
```

## Scenario E — Source file changes during transfer

The resulting destination may not represent one stable version of the source.

Each failure requires evidence-based diagnosis.

Do not simply restart blindly.

---

# 50. Destination Capacity

Before a large transfer:

```bash
df -h
```

Look at:

```text
Filesystem
Size
Used
Avail
Use%
Mounted on
```

The most important value for the immediate transfer is available capacity on the destination filesystem.

A destination with:

```text
1 TB total
950 GB used
```

does not have 1 TB available.

It has roughly:

```text
50 GB available
```

and filesystem reservations, concurrent workloads, and temporary files can make the effective safe capacity smaller.

Inode capacity can also matter, especially for millions of small files, but detailed inode management belongs to Topic 07.

---

# 51. Files Changing During Transfer

Copying an actively changing file can produce operational surprises.

Examples:

- active log file
- database dump still being written
- generated CSV
- active export
- temporary processing output

Suppose:

```text
export.csv
```

is still being generated while you copy it.

The destination may not represent a stable completed export.

Safer patterns include:

## Stable completion

Only transfer after the producer has finished writing.

## Temporary filename

Write:

```text
export.csv.tmp
```

then rename when complete:

```text
export.csv
```

The consumer watches for the final name.

## Manifest after completion

Generate the checksum only after the file is stable:

```bash
sha256sum export.csv > export.csv.sha256
```

This module does not turn atomic-file design into a separate course, but the principle is essential:

> **Do not treat a file as a stable dataset artifact while its producer is still mutating it.**

---

# 52. Production Data Integrity Workflow

This is one of the most important workflows in the module.

```text
1. Identify source
       ↓
2. Confirm destination
       ↓
3. Check available disk
       ↓
4. Estimate transfer size
       ↓
5. Decide tool
       ↓
6. Dry-run
       ↓
7. Transfer
       ↓
8. Monitor
       ↓
9. Resume if interrupted
       ↓
10. Verify integrity
       ↓
11. Record result
       ↓
12. Clean up temporary data
```

Do not skip directly from:

```text
"I need to move this"
```

to:

```bash
rsync ...
```

Production operators first establish what should happen.

---

# 53. Tool Selection Decision Tree

Use this as the first decision framework:

```text
Need to move data
      |
      +--> One small/one-off SSH file?
      |          |
      |          +--> scp
      |
      +--> Repeated server-to-server synchronization?
      |          |
      |          +--> rsync
      |
      +--> Object storage / cloud remote?
      |          |
      |          +--> rclone
      |
      +--> Huge directory as a stream?
                 |
                 +--> tar + SSH + compression
```

Then apply qualifiers:

```text
size
resumability
destination type
deletion semantics
integrity requirements
network constraints
cloud cost
production impact
```

---

# 54. `scp` vs `rsync` vs `rclone`

| Capability | `scp` | `rsync` | `rclone` |
|---|---|---|---|
| One-off SSH file | Excellent | Good | Not primary |
| Directory transfer | Yes with `-r` | Excellent | Yes |
| Incremental server sync | Limited | Excellent | Good for supported remotes |
| Resume-oriented workflows | Less capable | Strong | Strong for supported remotes |
| Exclude patterns | Limited | Excellent | Supported |
| Destructive mirror semantics | Not its main role | `--delete` | `sync` |
| SSH transport | Yes | Commonly | Can use supported SSH/SFTP remotes, but not its core object-storage role |
| Object storage | Not primary | Not primary | Excellent |
| S3/GCS/Azure/MinIO | Not primary | Not primary | Supported through configured remotes |
| Check/verification workflow | External tools | Strong options | `rclone check` |
| Dry-run | Not the main workflow | `--dry-run` | `--dry-run` |
| Parallel object transfers | Not a core feature | Limited by workflow | Strong concurrency controls |
| Best use case | Simple SSH copy | Server/filesystem synchronization | Object-storage/cloud movement |

### Important caveats

- "Resume" is not one universal behavior; it depends on the tool, options, file state, and backend.
- `rsync` is not an object-storage API abstraction in the same way as rclone.
- `rclone sync` can delete destination objects.
- `rsync --delete` can delete destination files.
- A successful command does not automatically mean an independently verified business-correct transfer.

---

# 55. Copy vs Sync

This distinction must become automatic.

```text
copy
=
move/add data
```

```text
sync
=
make destination reflect source
```

A copy workflow generally does not imply:

```text
delete everything that is not in source
```

A synchronization workflow may.

Therefore:

```text
rclone copy
```

and:

```text
rclone sync
```

have materially different risk profiles.

Likewise:

```text
rsync
```

and:

```text
rsync --delete
```

should not be mentally treated as the same operation.

---

# 56. Transfer Completion vs Integrity Verification

Remember:

```text
transfer succeeded
      ≠
data integrity independently verified
```

For critical datasets:

```text
Transfer
   ↓
Verify
   ↓
Record
```

Verification can include:

- SHA-256 manifests
- `sha256sum -c`
- rsync checksum comparison where appropriate
- `rclone check`
- file counts
- expected sizes
- application-level validation

Use the appropriate level of verification for the business impact.

---

# 57. Dry-Run vs Actual Operation

```text
dry-run
=
inspect intended changes
```

```text
actual run
=
make changes
```

A dry-run is not a guarantee that the eventual run cannot fail.

It is a way to detect incorrect assumptions before making changes.

This is particularly valuable for:

```bash
rsync --delete --dry-run ...
```

and:

```bash
rclone sync --dry-run ...
```

---

# 58. Bandwidth vs Throughput

The theoretical network capacity is not necessarily the transfer speed you will observe.

For example:

```text
1 Gbps network
```

does not mean every file transfer will achieve:

```text
125 MB/s
```

Real throughput can be limited by:

- source disk
- destination disk
- CPU
- encryption
- compression
- packet overhead
- congestion
- remote service limits
- many-small-file overhead

Use observed metrics rather than assuming link speed equals application throughput.

---

# 59. Resumability vs Retry

These concepts are related but not identical.

```text
retry
=
run the transfer again
```

```text
resumability
=
continue efficiently from an incomplete state
```

A retry can potentially retransmit substantial data.

A resumable workflow may reuse the existing partial state.

Therefore, for large transfers:

```text
failure
  ↓
inspect partial state
  ↓
resume appropriately
  ↓
verify
```

is better than:

```text
failure
  ↓
blindly start over
```

---

# 60. Cloud Egress Cost Awareness

Data movement can create financial cost.

Examples:

```text
Cloud Region A
      |
      v
Cloud Region B
```

or:

```text
Cloud A
   |
   v
Cloud B
```

Potential cost dimensions include:

- egress
- cross-region transfer
- cross-provider movement
- repeated copies
- unnecessary downloads
- architecture that moves the same data repeatedly

This module does not provide current provider pricing.

The architectural lesson is:

> **Data movement is part of cloud architecture and can be part of the cost model.**

Before a large transfer, ask:

```text
Do we really need to move these bytes?
Can we process closer to the data?
Can we transfer once and reuse?
Is there a lower-cost path?
```

---

# 61. Managed Transfer Services — Awareness

At enterprise scale, organizations may use specialized managed transfer infrastructure for:

- large migrations
- cross-cloud transfers
- scheduled bulk movement
- high-volume data migration
- controlled enterprise data movement

The key distinction is:

```text
Operator tools
    |
    +--> scp
    +--> rsync
    +--> rclone

Enterprise migration infrastructure
    |
    +--> specialized managed transfer services
```

You should understand:

> `scp`, `rsync`, and `rclone` are essential operator tools, but very large enterprise migrations may require specialized managed infrastructure.

This is awareness-level content, not a cloud-provider service comparison.

---

# 62. Production Bandwidth and Resource Impact

A transfer can be technically successful and still be an operational failure.

Example:

```text
Production network
      |
      +---- API traffic
      |
      +---- database traffic
      |
      +---- monitoring
      |
      +---- 10 TB transfer
```

If the transfer consumes the majority of available bandwidth:

```text
latency ↑
application performance ↓
```

Other resources can also be affected:

```text
disk I/O
CPU
memory
object-storage request capacity
```

The production principle is:

> **A successful transfer can still be an operational failure if it starves production traffic.**

---

# 63. Hands-On Lab 1 — rsync at Scale

Use synthetic data.

Create:

```text
~/data-transfer-lab/
├── source/
└── destination/
```

Commands:

```bash
mkdir -p \
    ~/data-transfer-lab/source/raw \
    ~/data-transfer-lab/source/processed \
    ~/data-transfer-lab/source/logs \
    ~/data-transfer-lab/source/temp \
    ~/data-transfer-lab/destination
```

Create sample files:

```bash
printf 'customer_id,name\n1,Ada\n2,Grace\n' \
    > ~/data-transfer-lab/source/raw/customers.csv

printf 'id,value\n1,100\n2,200\n' \
    > ~/data-transfer-lab/source/processed/result.csv

printf 'temporary\n' \
    > ~/data-transfer-lab/source/temp/example.tmp

printf 'debug log\n' \
    > ~/data-transfer-lab/source/logs/pipeline.log
```

Create a larger synthetic file:

```bash
dd if=/dev/zero \
   of=~/data-transfer-lab/source/raw/test-1gb.bin \
   bs=1M \
   count=1024
```

## Exercise A — Initial synchronization

```bash
rsync -av --info=progress2 \
    ~/data-transfer-lab/source/ \
    ~/data-transfer-lab/destination/
```

Inspect the destination.

## Exercise B — Modify the source

```bash
printf '\n3,Katherine\n' \
    >> ~/data-transfer-lab/source/raw/customers.csv
```

Run:

```bash
rsync -av --info=progress2 \
    ~/data-transfer-lab/source/ \
    ~/data-transfer-lab/destination/
```

Observe what changes.

## Exercise C — Exclusions

```bash
rsync -av --dry-run \
    --exclude '*.tmp' \
    --exclude 'logs/' \
    ~/data-transfer-lab/source/ \
    ~/data-transfer-lab/destination/
```

Inspect the planned changes.

## Exercise D — Partial transfer

Start a large transfer with:

```bash
rsync -av --partial --progress \
    ~/data-transfer-lab/source/ \
    ~/data-transfer-lab/destination/
```

Interrupt it.

Then resume it.

## Exercise E — Checksum verification

Create a manifest:

```bash
cd ~/data-transfer-lab/source/raw
sha256sum customers.csv result.csv test-1gb.bin > checksums.sha256
```

Copy the files and manifest to the destination and verify:

```bash
cd ~/data-transfer-lab/destination/raw
sha256sum -c checksums.sha256
```

## Exercise F — Safe delete demonstration

Create an extra destination-only file:

```bash
touch ~/data-transfer-lab/destination/old-file.txt
```

First:

```bash
rsync -av --delete --dry-run \
    ~/data-transfer-lab/source/ \
    ~/data-transfer-lab/destination/
```

Verify that the planned deletion is understood.

Only in this synthetic lab, execute:

```bash
rsync -av --delete \
    ~/data-transfer-lab/source/ \
    ~/data-transfer-lab/destination/
```

Then confirm:

```bash
test ! -e ~/data-transfer-lab/destination/old-file.txt \
    && echo "old-file.txt removed as expected"
```

Never use this learning pattern against real production directories.

---

# 64. Hands-On Lab 2 — rclone With MinIO or Another Safe Remote

Preferred practice target:

```text
MinIO
```

if it already exists in the broader Data Engineering lab.

Do not require real cloud credentials.

## Step 1 — Inspect remotes

```bash
rclone listremotes
```

Confirm the expected test remote exists.

## Step 2 — Inspect the remote

Use an environment-specific command such as:

```bash
rclone lsd minio:
```

Replace `minio:` with your configured test remote.

## Step 3 — Copy

```bash
rclone copy \
    ./exports \
    minio:test-data/exports
```

## Step 4 — Dry-run

Before synchronization:

```bash
rclone sync --dry-run \
    ./exports \
    minio:test-data/exports
```

Read the proposed changes.

## Step 5 — Controlled sync

Only against a disposable test path:

```bash
rclone sync \
    ./exports \
    minio:test-data/exports
```

## Step 6 — Check

```bash
rclone check \
    ./exports \
    minio:test-data/exports
```

## Step 7 — Experiment with concurrency

Observe how throughput changes as transfer concurrency is adjusted.

Do not blindly maximize concurrency.

## Step 8 — Apply a bandwidth limit

For example:

```bash
rclone copy \
    --bwlimit 20M \
    ./exports \
    minio:test-data/exports
```

Observe:

- transfer speed
- CPU
- network use
- impact on other workloads

## Step 9 — Clean up

Delete only the controlled test objects using the appropriate rclone command after confirming the target path.

---

# 65. Hands-On Lab 3 — Streaming Archive Over SSH

Use two Linux systems or two practice containers.

Create sample data:

```bash
mkdir -p ~/streaming-lab/source
printf 'alpha\n' > ~/streaming-lab/source/a.txt
printf 'beta\n'  > ~/streaming-lab/source/b.txt
```

Create the destination directory on the remote system:

```bash
ssh dataeng@server 'mkdir -p /tmp/streaming-lab/destination'
```

Stream without an intermediate archive:

```bash
tar -cf - ~/streaming-lab/source/ | \
ssh dataeng@server \
    'tar -xf - -C /tmp/streaming-lab/destination/'
```

Verify:

```bash
ssh dataeng@server \
    'find /tmp/streaming-lab/destination -type f -print'
```

Now use zstd:

```bash
tar -cf - ~/streaming-lab/source/ | \
zstd | \
ssh dataeng@server \
    'zstd -d | tar -xf - -C /tmp/streaming-lab/destination/'
```

Explain:

1. where the archive is created
2. where compression occurs
3. what crosses SSH
4. where decompression occurs
5. where files are extracted
6. why no intermediate `.tar` file is required

---

# 66. Hands-On Lab 4 — Bastion-Based Transfer

Use:

```text
Laptop
   |
   v
Bastion
   |
   v
Private Data Server
```

Do not use production data.

## Exercise A — scp

```bash
scp -o ProxyJump=bastion \
    dataset.csv \
    data-server:/data/incoming/
```

## Exercise B — rsync

```bash
rsync -av \
    -e 'ssh -J bastion' \
    dataset/ \
    data-server:/data/incoming/dataset/
```

## Exercise C — interruption

Interrupt a sufficiently large synthetic transfer.

## Exercise D — resume

Restart with:

```bash
rsync -av --partial \
    -e 'ssh -J bastion' \
    dataset/ \
    data-server:/data/incoming/dataset/
```

## Exercise E — verify

Generate a checksum manifest at the source and verify it at the destination.

## Exercise F — document

Write a runbook entry containing:

```text
Transfer objective
Source
Destination
Tool
Command
Expected behavior
Observed result
Verification
Failure
Fix
Final status
```

---

# 67. Break/Fix Exercises

The purpose of these exercises is to develop operational diagnosis rather than command memorization.

For every scenario use:

```text
Symptom
   ↓
Evidence
   ↓
Diagnosis
   ↓
Root Cause
   ↓
Fix
   ↓
Verification
   ↓
Prevention
```

And follow the G2 learning loop:

```text
Read
  ↓
Do
  ↓
Make repeatable
  ↓
Break
  ↓
Diagnose from evidence
  ↓
Fix
  ↓
Verify
  ↓
Write runbook entry
  ↓
Explain aloud
```

---

## Scenario 1 — Wrong Destination Path

### Symptom

The transfer succeeds but the data is not where expected.

### Evidence

```bash
pwd
ls -la
find destination/ -maxdepth 3 -type f
```

### Diagnosis

Check:

- source path
- destination path
- current working directory
- trailing slash

### Root Cause

Incorrect destination assumption or path.

### Fix

Correct the command after a dry-run.

### Verification

Confirm the expected destination tree.

---

## Scenario 2 — Wrong Trailing Slash

### Symptom

You expected:

```text
/backup/data/a.csv
```

but got:

```text
/backup/data/data/a.csv
```

### Evidence

Inspect the directory tree.

### Diagnosis

The command copied the directory itself rather than its contents.

### Root Cause

Incorrect use of:

```text
data
```

versus:

```text
data/
```

### Fix

Correct the source path and test with `--dry-run`.

---

## Scenario 3 — Unexpected Destination Files

### Symptom

Destination contains files not present in source.

### Evidence

```bash
find source/ -type f | sort
find destination/ -type f | sort
```

### Diagnosis

Determine whether those destination-only files are:

- expected historical data
- unrelated data
- stale mirror contents

### Fix

Do not immediately use `--delete`.

First establish the intended synchronization semantics.

---

## Scenario 4 — `--delete` Would Remove Important Files

### Symptom

Dry-run shows many deletions.

### Evidence

```bash
rsync -av --delete --dry-run source/ destination/
```

### Diagnosis

The destination is not currently a pure mirror.

### Root Cause

Destructive mirror semantics are being applied to a destination containing retained data.

### Fix

Stop. Reconfirm requirements.

Possible outcomes:

- remove `--delete`
- change destination
- change source
- create a dedicated mirror path
- explicitly document deletion policy

### Verification

Run the dry-run again and ensure all deletions are intentional.

---

## Scenario 5 — Transfer Interrupted at 60%

### Symptom

Large transfer stopped unexpectedly.

### Evidence

```bash
ls -lh destination/
```

and inspect the transfer command's previous output.

### Diagnosis

Determine whether partial transfer state exists.

### Fix

Resume with an appropriate rsync command:

```bash
rsync -av --partial ...
```

### Verification

Run a checksum comparison after completion.

---

## Scenario 6 — Destination Disk Nearly Full

### Symptom

Transfer fails with a write or space-related error.

### Evidence

```bash
df -h
```

If needed, inspect inode capacity as covered in Topic 07.

### Diagnosis

Destination lacks sufficient safe capacity.

### Fix

Do not simply rerun.

Resolve capacity or choose a suitable destination.

### Verification

Recheck available capacity and transfer state.

---

## Scenario 7 — Checksum Mismatch

### Symptom

```text
file.csv: FAILED
```

### Evidence

Generate fresh source and destination hashes:

```bash
sha256sum source/file.csv
sha256sum destination/file.csv
```

### Diagnosis

Determine whether:

- source changed
- destination changed
- wrong file was copied
- transfer was incomplete
- verification manifest was stale

### Fix

Establish the correct stable source and retransmit.

### Verification

Generate a new manifest after the source is stable.

---

## Scenario 8 — Object-Storage Remote Misconfigured

### Symptom

`rclone` cannot access the expected remote.

### Evidence

```bash
rclone listremotes
```

Then inspect the configured remote according to your environment.

### Diagnosis

Determine whether:

- remote name is wrong
- configuration is missing
- credentials are unavailable
- endpoint is wrong
- network access is unavailable

### Fix

Correct configuration using the approved environment process.

Never paste secrets into the shell history or source repository unnecessarily.

---

## Scenario 9 — Transfer Saturates Network Bandwidth

### Symptom

Production services become slow during a transfer.

### Evidence

Observe:

- transfer throughput
- network utilization
- application latency
- host resource use

### Diagnosis

Transfer is competing with production traffic.

### Fix

Throttle or reschedule the transfer.

For rclone:

```bash
--bwlimit
```

may be appropriate.

### Prevention

Define transfer windows and resource budgets.

---

## Scenario 10 — Source File Changes During Transfer

### Symptom

Destination checksum does not match the expected source artifact.

### Evidence

Check:

```bash
stat source/file
stat destination/file
```

and compare hashes.

### Diagnosis

Source may have changed while being copied.

### Fix

Produce a stable source artifact before transfer.

### Prevention

Use:

```text
temporary name
      ↓
write completely
      ↓
verify
      ↓
atomic rename
      ↓
transfer
```

---

# 68. Transfer Troubleshooting Decision Tree

When a transfer fails:

```text
Transfer failed
      |
      +--> Authentication/connectivity?
      |         |
      |         +--> Verify SSH/network path
      |
      +--> Source exists?
      |         |
      |         +--> Verify path and permissions
      |
      +--> Destination exists?
      |         |
      |         +--> Verify path
      |
      +--> Enough disk?
      |         |
      |         +--> df -h
      |
      +--> Permissions?
      |         |
      |         +--> Verify write access
      |
      +--> Network interrupted?
      |         |
      |         +--> inspect partial state
      |
      +--> Source changed?
      |         |
      |         +--> establish stable artifact
      |
      +--> Destination changed?
      |         |
      |         +--> inspect synchronization semantics
      |
      +--> Checksum mismatch?
      |         |
      |         +--> regenerate and compare hashes
      |
      +--> Object-storage/API issue?
      |         |
      |         +--> inspect remote configuration and service response
      |
      +--> Bandwidth/throttling issue?
                |
                +--> inspect throughput and production impact
```

The operator's job is to gather evidence before selecting a fix.

---

# 69. Command Safety Rules

This topic contains commands that can delete data.

The two commands that deserve special attention are:

```bash
rsync --delete
```

and:

```bash
rclone sync
```

Before using them:

```text
1. Understand source
2. Understand destination
3. Understand deletion semantics
4. Confirm path
5. Dry-run
6. Inspect output
7. Execute
8. Verify
```

Never normalize destructive synchronization as a routine copy/paste operation.

Use safe local or disposable test directories while learning.

---

# 70. Data Engineering Use Cases

## 70.1 Partner File Ingestion

```text
Partner Server
      |
      | rsync/scp
      v
Landing Server
      |
      v
Data Pipeline
```

Questions:

- Is the source stable?
- Does the partner support resumable transfer?
- How is integrity verified?
- What happens if the file arrives twice?
- Where is the checksum recorded?

---

## 70.2 Daily Database Exports

```text
Database export
      |
      v
rsync
      |
      v
Data Server
```

Questions:

- Is the export complete before transfer?
- Is the destination large enough?
- Can the transfer resume?
- Is the export checksum recorded?

---

## 70.3 Object Storage Ingestion

```text
Local/Server
      |
      v
rclone
      |
      v
S3 / MinIO / GCS / Azure Blob
```

Questions:

- `copy` or `sync`?
- What is the remote prefix?
- What happens to existing objects?
- Is dry-run required?
- How is the result verified?

---

## 70.4 Backup Movement

```text
Server
   |
   v
Archive
   |
   v
Object Storage
```

Consider:

- checksum
- encryption requirements
- retention
- bandwidth
- egress
- lifecycle
- restore verification

---

## 70.5 Large Migration

```text
Old Environment
      |
      v
Bulk Transfer
      |
      v
New Environment
```

At this scale, ask:

- Can the network sustain the transfer?
- How long will it take?
- How will interruption be handled?
- Is parallelism required?
- Is cloud egress material?
- Is managed transfer infrastructure more appropriate?

---

## 70.6 Cross-Region Movement

```text
Region A
   |
   v
Region B
```

The engineering decision includes:

```text
data volume
transfer duration
egress
cross-region charges
production impact
recovery plan
```

---

# 71. Production File-Transfer Runbook

Use this when a transfer matters.

## 3 a.m. Runbook

```text
1. Identify source and destination
2. Confirm destination capacity
3. Estimate data volume
4. Choose scp / rsync / rclone
5. Perform dry-run if applicable
6. Start transfer
7. Monitor progress
8. Handle interruption
9. Verify integrity
10. Confirm destination contents
11. Record transfer result
12. Clean temporary artifacts
```

## Transfer record

Record:

```text
Transfer objective:
Source:
Destination:
Tool:
Command:
Expected behavior:
Start time:
Observed throughput:
Interruption:
Recovery action:
Verification method:
Verification result:
Final status:
Operator:
Notes:
```

This turns an ad-hoc command into an operationally auditable action.

---

# 72. Common Operational Mistakes

## Mistake 1 — Wrong source path

Always verify:

```bash
pwd
ls -la
```

before a large operation.

## Mistake 2 — Wrong destination

Confirm the destination explicitly.

## Mistake 3 — Ignoring trailing slashes

Understand:

```text
data/
```

versus:

```text
data
```

## Mistake 4 — Using `--delete` casually

Always dry-run first.

## Mistake 5 — Treating `rclone sync` like `rclone copy`

They have different deletion semantics.

## Mistake 6 — Assuming success means integrity

Verify important data.

## Mistake 7 — Ignoring destination capacity

Check:

```bash
df -h
```

## Mistake 8 — Blindly increasing parallelism

More concurrency can harm the system.

## Mistake 9 — Ignoring production bandwidth

A successful transfer can still cause an outage.

## Mistake 10 — Copying unstable files

Transfer completed artifacts rather than actively changing files.

## Mistake 11 — Putting credentials in commands or repositories

Protect configuration and secrets.

## Mistake 12 — Restarting without inspecting partial state

Understand what survived the interruption.

## Mistake 13 — Ignoring cloud egress

Large repeated movements can become expensive.

## Mistake 14 — Treating a bastion as free bandwidth

The bastion is part of the network path and can carry the traffic load.

---

# 73. Production Safety Checklist

Before transfer:

- [ ] Source path verified
- [ ] Destination path verified
- [ ] Destination host verified
- [ ] Destination capacity checked
- [ ] Data volume estimated
- [ ] Tool selected intentionally
- [ ] Source files are stable
- [ ] Dry-run performed where appropriate
- [ ] Destructive semantics understood
- [ ] Network impact considered
- [ ] Cloud egress considered
- [ ] Credentials protected

During transfer:

- [ ] Progress monitored
- [ ] Throughput reasonable
- [ ] Production traffic unaffected
- [ ] Destination capacity remains sufficient
- [ ] Errors investigated rather than ignored

After transfer:

- [ ] Destination contents verified
- [ ] Integrity verified where required
- [ ] Checksum manifest recorded
- [ ] Temporary files cleaned
- [ ] Transfer result documented

---

# 74. Practice Questions

Each question uses:

```text
Question
Expected Thinking
Solution
Explanation
```

---

## Basic 1

### Question

What is the primary purpose of `scp`?

### Expected Thinking

Identify its role as a simple SSH-based file-transfer tool.

### Solution

`scp` transfers files between local and remote systems using SSH-based connectivity.

### Explanation

It is well suited to straightforward one-off file movement.

---

## Basic 2

### Question

What does `scp -r` do?

### Expected Thinking

Think recursively through a directory tree.

### Solution

It enables recursive directory transfer.

### Explanation

Without recursion, a directory cannot be copied as a complete tree in the same way.

---

## Basic 3

### Question

What does `rsync -a` mean conceptually?

### Expected Thinking

Think recursive copying plus preservation of filesystem metadata.

### Solution

Archive mode recursively transfers a directory tree while preserving a useful set of filesystem attributes where permissions allow.

### Explanation

Archive mode is a convenient bundle of preservation behavior.

---

## Basic 4

### Question

What does `--dry-run` do?

### Expected Thinking

Think "predict, don't execute."

### Solution

It shows the changes a command intends to make without applying them.

### Explanation

It is especially important before destructive synchronization.

---

## Basic 5

### Question

What is the main difference between `rclone copy` and `rclone sync`?

### Expected Thinking

Focus on deletion semantics.

### Solution

`copy` transfers data without making the destination an exact mirror by deleting unrelated destination objects; `sync` aims to make the destination match the source and can delete destination objects.

### Explanation

This makes `sync` more dangerous when used against a shared or historical destination.

---

## Basic 6

### Question

What command calculates a SHA-256 hash?

### Solution

```bash
sha256sum file
```

### Explanation

The resulting digest can be compared with a trusted reference digest.

---

## Basic 7

### Question

Why can a trailing slash matter in rsync?

### Solution

It changes whether the contents of a directory or the directory itself is copied into the destination.

### Explanation

This can materially change the resulting directory tree.

---

## Basic 8

### Question

What does `--partial` help with?

### Solution

It preserves partial transfer state after an interrupted rsync transfer.

### Explanation

This can make subsequent recovery more efficient than discarding the partial file.

---

## Basic 9

### Question

What is MinIO useful for in this module?

### Solution

It can provide a safe S3-compatible object-storage practice environment.

### Explanation

It lets learners practice rclone without requiring real cloud credentials.

---

## Basic 10

### Question

What does cloud egress mean at a high level?

### Solution

It refers to data leaving a cloud environment or service and can incur network-transfer charges depending on the architecture and provider.

### Explanation

Large data movement therefore has both technical and financial implications.

---

## Moderate 1

### Question

Why might you choose rsync instead of scp for a repeated 500 GB dataset?

### Expected Thinking

Consider incremental synchronization.

### Solution

Rsync can identify unchanged data and transfer only what is required to update the destination.

### Explanation

This can dramatically reduce repeated network transfer.

---

## Moderate 2

### Question

Explain the difference:

```bash
rsync -av data/ server:/backup/
```

and:

```bash
rsync -av data server:/backup/
```

### Solution

The first copies the contents of `data/` into `/backup/`; the second copies the `data` directory itself into `/backup/`.

### Explanation

The destination tree differs because of trailing-slash semantics.

---

## Moderate 3

### Question

Why is this safer:

```bash
rsync -av --delete --dry-run source/ destination/
```

than:

```bash
rsync -av --delete source/ destination/
```

### Solution

The dry-run reveals proposed changes, including deletions, before they are applied.

### Explanation

It gives the operator an opportunity to detect a wrong source, destination, or synchronization assumption.

---

## Moderate 4

### Question

What is a SHA-256 manifest?

### Solution

A file containing filenames and their SHA-256 digests, which can later be used to verify the transferred files.

### Explanation

It creates a repeatable integrity-verification artifact.

---

## Moderate 5

### Question

Why might `rsync -c` be slower?

### Solution

It requires content checksums, causing more file reads and CPU/I/O work.

### Explanation

This can be expensive for large datasets.

---

## Moderate 6

### Question

Why can `rclone` be preferable to rsync for S3 movement?

### Solution

Rclone is designed to work with object-storage/cloud remotes through a unified remote abstraction.

### Explanation

S3 is not simply a remote POSIX filesystem.

---

## Moderate 7

### Question

Why can too much rclone parallelism be harmful?

### Solution

It can saturate network bandwidth, increase CPU/disk use, trigger API throttling, or interfere with production traffic.

### Explanation

Concurrency is a resource-management decision.

---

## Moderate 8

### Question

When might streaming tar over SSH be useful?

### Solution

When you want to transfer a directory as a stream without creating a large intermediate archive file.

### Explanation

It can save staging disk space.

---

## Moderate 9

### Question

Why might zstd not help much when transferring Parquet files?

### Solution

Parquet commonly contains compressed/encoded data already, so additional compression may provide limited benefit while consuming CPU.

### Explanation

Compression should be evaluated against the actual data format.

---

## Moderate 10

### Question

What should you check before a large transfer?

### Solution

At minimum:

- source
- destination
- destination capacity
- data volume
- transfer method
- expected network impact
- dry-run where appropriate

### Explanation

Preparation reduces preventable operational failures.

---

## Hard 1

### Question

A 2 TB rsync transfer fails after 1.5 TB. What should you do first?

### Expected Thinking

Do not blindly restart.

### Solution

Inspect the destination and transfer state, determine whether partial data exists, confirm source stability, verify destination capacity, then resume appropriately.

### Explanation

The goal is recovery based on evidence, not repeated full retransmission.

---

## Hard 2

### Question

A dry-run of `rsync --delete` proposes deleting 400 GB from the destination. What should you do?

### Solution

Stop and investigate.

Confirm:

- source
- destination
- trailing slash
- intended mirror semantics
- whether destination-only files are supposed to be retained

Do not execute until the deletion set is understood.

### Explanation

Large unexpected deletions are an operational stop condition.

---

## Hard 3

### Question

A destination checksum does not match the source checksum. Give three possible explanations.

### Solution

Possible explanations include:

1. source changed during transfer
2. destination data is incomplete or incorrect
3. the verification manifest is stale or refers to a different source version

### Explanation

A checksum mismatch is evidence that should trigger investigation, not automatic blame of the network.

---

## Hard 4

### Question

Why can transferring one 1 TB file behave differently from transferring one million 1 MB files?

### Solution

The million-file workload has far more metadata, object/API requests, directory traversal, and connection/request overhead.

### Explanation

Total bytes alone do not determine transfer behavior.

---

## Hard 5

### Question

Why might you use a bandwidth limit even if the transfer could go faster?

### Solution

To protect shared production bandwidth and prevent the transfer from increasing application latency or starving other workloads.

### Explanation

Maximum throughput is not always the operational objective.

---

## Hard 6

### Question

Why can a bastion become a transfer bottleneck?

### Solution

If the data path traverses the bastion, its network interfaces, CPU, and connection capacity can become part of the transfer's resource constraints.

### Explanation

A jump host is not an invisible network abstraction.

---

## Hard 7

### Question

Why is transferring an actively written database dump risky?

### Solution

The destination may receive a file that does not represent one stable completed artifact.

### Explanation

The source should generally be finalized before transfer.

---

## Hard 8

### Question

When would `rclone copy` be safer than `rclone sync`?

### Solution

When the goal is to add/update destination objects without deleting destination-only objects.

### Explanation

`copy` has less destructive synchronization semantics.

---

## Hard 9

### Question

Why is `--dry-run` not a substitute for understanding a command?

### Solution

A dry-run only shows what the tool believes it will do under the current inputs. It does not fix a fundamentally wrong source, destination, or business assumption.

### Explanation

Operators still need to reason about intent.

---

## Hard 10

### Question

Why might a checksum manifest be generated only after an export completes?

### Solution

Because generating it earlier could hash an incomplete or changing file.

### Explanation

Integrity verification is meaningful only when the reference artifact is stable.

---

## Advanced 1

### Question

Design a safe workflow for moving 500 GB from a private server to S3 through an operational environment.

### Expected Thinking

Include destination semantics, capacity, network impact, verification, and recovery.

### Solution

A reasonable workflow:

```text
Confirm source stability
      ↓
Confirm S3 remote/path
      ↓
Estimate volume and cost
      ↓
Check local capacity
      ↓
Dry-run rclone copy
      ↓
Run transfer with controlled concurrency/bandwidth
      ↓
Monitor
      ↓
Recover if interrupted
      ↓
rclone check
      ↓
Record result
```

### Explanation

The transfer is treated as an operational workflow rather than a single command.

---

## Advanced 2

### Question

You are asked to synchronize:

```text
/data/exports/
```

to:

```text
/data/archive/
```

and the destination contains historical files. Should you automatically use `--delete`?

### Solution

No.

### Explanation

First determine whether the requirement is:

```text
copy new/current exports
```

or:

```text
maintain an exact mirror
```

Historical destination files may be intentionally retained.

---

## Advanced 3

### Question

A team wants to maximize rclone concurrency to accelerate a migration. What questions should you ask first?

### Solution

Ask:

- What is the network capacity?
- What is the source disk throughput?
- What is the destination service's request limit?
- What is the acceptable production impact?
- Is API throttling expected?
- What bandwidth should be reserved for production?
- What is the transfer window?
- What is the cost impact?

### Explanation

Concurrency should be constrained by the weakest relevant resource.

---

## Advanced 4

### Question

When is streaming tar over SSH preferable to rsync?

### Solution

It can be preferable when the requirement is a one-time streaming movement of a directory tree and you want to avoid creating a large intermediate archive.

### Explanation

Rsync is generally better for repeated synchronization; streaming tar is useful for a one-time stream-oriented transfer.

---

## Advanced 5

### Question

Why might a large enterprise migration justify managed transfer infrastructure rather than a hand-built rsync workflow?

### Solution

Because enterprise migrations may require:

- high-volume throughput
- specialized orchestration
- monitoring
- scheduling
- multi-cloud movement
- operational controls
- migration-specific reliability

### Explanation

Operator tools remain important, but the scale and operational requirements may exceed what a manually managed command provides.

---

# 75. Interview Practice

## 1. What is `scp`?

`scp` is an SSH-based command-line tool for copying files between systems.

## 2. Why choose rsync over scp?

For repeated or large synchronization where incremental transfer, exclusions, metadata preservation, partial-transfer handling, and controlled synchronization are valuable.

## 3. What does rsync archive mode do?

It enables recursive transfer and preservation of a useful set of filesystem metadata, subject to platform and privilege constraints.

## 4. Explain the trailing-slash difference.

`source/` means the contents of the source directory; `source` means the directory itself.

## 5. What does `--dry-run` do?

It previews intended changes without applying them.

## 6. Why is `--delete` dangerous?

It can remove destination files that are not present in the source.

## 7. How would you safely use `rsync --delete`?

Use a dry-run first, inspect deletions, confirm source/destination semantics, then execute and verify.

## 8. How can you resume a large interrupted rsync transfer?

Use an appropriate resumable workflow, commonly involving `--partial`, inspect the existing partial state, rerun rsync, and verify the final data.

## 9. What does `--partial` do?

It keeps partially transferred files rather than discarding them when a transfer is interrupted.

## 10. What is rsync checksum mode?

`rsync -c` uses file-content checksums to decide whether files differ rather than relying primarily on metadata.

## 11. How would you verify a 100 GB transfer?

Use a stable source artifact, generate SHA-256 checksums or a manifest, transfer it, and verify at the destination.

## 12. What is a SHA-256 manifest?

A list of files and their SHA-256 digests used for repeatable integrity verification.

## 13. What is rclone?

A command-line data movement tool that provides a unified interface for local filesystems and many remote/cloud/object-storage systems.

## 14. Difference between `rclone copy` and `rclone sync`?

`copy` transfers data without making the destination an exact mirror; `sync` aims to make the destination match the source and can delete destination objects.

## 15. How would you safely test rclone sync?

Use a disposable destination and:

```bash
rclone sync --dry-run source remote:path
```

Then inspect proposed changes.

## 16. What does `rclone check` do?

It compares source and destination and reports differences according to the available backend comparison mechanisms.

## 17. How would you transfer data to S3?

Configure a secure rclone remote and use:

```bash
rclone copy source s3remote:bucket/path
```

with the actual remote name and path defined by the environment.

## 18. Why can parallel transfers help?

They can increase aggregate throughput, especially for workloads with many independent objects.

## 19. Why can too much parallelism hurt?

It can saturate bandwidth, consume CPU/disk resources, trigger API throttling, and affect production traffic.

## 20. Why throttle transfers?

To protect shared resources and control production impact.

## 21. What is cloud egress?

Data transfer leaving a cloud service or region that may incur network-transfer charges.

## 22. How would you stream an archive over SSH?

Use:

```bash
tar -cf - directory/ | ssh server 'tar -xf - -C /destination/'
```

## 23. When would you use a managed transfer service?

For large enterprise migrations or complex high-volume movement where specialized reliability, scheduling, monitoring, and migration controls are needed.

## 24. How would you transfer data through a bastion?

Use SSH jump-host support, such as:

```bash
scp -o ProxyJump=bastion ...
```

or:

```bash
rsync -e 'ssh -J bastion' ...
```

or rely on a configured SSH `ProxyJump`.

---

# 76. Final Knowledge Check

You should be able to demonstrate all of the following without copying a command blindly.

## `scp`

- [ ] Use `scp` for a one-off file
- [ ] Transfer a directory with `scp -r`
- [ ] Retrieve a remote file
- [ ] Transfer through a bastion
- [ ] Explain when `scp` is not the best tool

## `rsync`

- [ ] Use basic rsync
- [ ] Explain `-a`
- [ ] Use verbose output
- [ ] Use progress reporting
- [ ] Explain `--info=progress2`
- [ ] Explain trailing slashes
- [ ] Use `--dry-run`
- [ ] Use `--exclude`
- [ ] Explain `--delete`
- [ ] Safely demonstrate `--delete`
- [ ] Use `--partial`
- [ ] Recover from an interrupted transfer
- [ ] Use rsync over SSH
- [ ] Transfer through a bastion
- [ ] Explain checksum mode

## Integrity

- [ ] Generate SHA-256 hashes
- [ ] Build a checksum manifest
- [ ] Verify a manifest
- [ ] Distinguish transfer success from independent verification
- [ ] Diagnose a checksum mismatch

## `rclone`

- [ ] Understand configured remotes
- [ ] Use `rclone copy`
- [ ] Explain `copy` vs `sync`
- [ ] Use `rclone sync`
- [ ] Use `--dry-run`
- [ ] Use `rclone check`
- [ ] Understand object-storage remotes
- [ ] Work conceptually with S3
- [ ] Work conceptually with GCS
- [ ] Work conceptually with Azure Blob
- [ ] Work conceptually with MinIO
- [ ] Reason about concurrency
- [ ] Apply bandwidth limits

## Large transfers

- [ ] Estimate transfer duration
- [ ] Check destination capacity
- [ ] Handle interruption
- [ ] Understand many-small-file vs huge-file behavior
- [ ] Explain splitting
- [ ] Understand parallel-stream awareness
- [ ] Stream an archive over SSH
- [ ] Use zstd appropriately
- [ ] Compare streaming vs staging

## Production judgment

- [ ] Protect production bandwidth
- [ ] Protect CPU and disk
- [ ] Consider API throttling
- [ ] Consider cloud egress
- [ ] Choose the right tool
- [ ] Avoid destructive synchronization mistakes
- [ ] Verify important transfers
- [ ] Document a large transfer
- [ ] Write a transfer runbook
- [ ] Diagnose from evidence instead of restarting blindly

---

# 77. Final Transfer Decision Model

Memorize the following:

```text
ONE-OFF SSH FILE
       ↓
      scp
```

```text
REPEATED SERVER SYNCHRONIZATION
       ↓
     rsync
```

```text
OBJECT STORAGE / CLOUD DATA MOVEMENT
       ↓
     rclone
```

```text
STREAMING ARCHIVE
       ↓
tar + SSH + compression
```

Then apply the production controls:

```text
Before transfer:
    Understand destination

Before destructive sync:
    Dry-run

After important transfer:
    Verify integrity

During production transfer:
    Protect shared resources

For huge enterprise migrations:
    Consider managed transfer infrastructure
```

---

# 78. The Production Mental Model

A Data Engineer should stop thinking:

> "Which command copies this file?"

and start thinking:

> **"What transfer workflow makes this movement reliable, recoverable, verifiable, cost-aware, and safe for the systems sharing the path?"**

The workflow is:

```text
Understand
    ↓
Plan
    ↓
Choose tool
    ↓
Check capacity
    ↓
Dry-run
    ↓
Transfer
    ↓
Monitor
    ↓
Recover if necessary
    ↓
Verify
    ↓
Document
```

That is the operational skill this module is designed to build.

---

# 79. Topic 04 Coverage Audit

The module covers the required Topic 04 roadmap concepts:

| Roadmap requirement | Covered |
|---|---:|
| File-transfer fundamentals | Yes |
| `scp` | Yes |
| `sftp` awareness | Yes |
| Bastion/jump-host transfers | Yes |
| `rsync` | Yes |
| `rsync -a` | Yes |
| Verbose/progress options | Yes |
| Compression with `-z` awareness | Yes |
| Trailing-slash semantics | Yes |
| Directory vs contents behavior | Yes |
| `--dry-run` | Yes |
| `--partial` | Yes |
| Resumable transfers | Yes |
| `--exclude` | Yes |
| `--delete` | Yes |
| Why `--delete` is dangerous | Yes |
| Dry-run before destructive synchronization | Yes |
| SHA-256 verification | Yes |
| `sha256sum` | Yes |
| rsync checksum mode | Yes |
| Manifests | Yes |
| `rclone` | Yes |
| Object storage | Yes |
| S3 | Yes |
| GCS | Yes |
| Azure Blob | Yes |
| MinIO | Yes |
| `rclone copy` | Yes |
| `rclone sync` | Yes |
| `rclone check` | Yes |
| rclone dry-run | Yes |
| Parallel transfers | Yes |
| Bandwidth limiting | Yes |
| Streaming archives over SSH | Yes |
| `tar \| ssh` | Yes |
| On-the-fly compression | Yes |
| zstd | Yes |
| Huge-file handling | Yes |
| Splitting files | Yes |
| Parallel-stream awareness | Yes |
| Resumability | Yes |
| Transfer throttling | Yes |
| Protecting production traffic | Yes |
| Cloud egress awareness | Yes |
| Managed-transfer awareness | Yes |
| Data Engineering scenarios | Yes |
| Hands-on exercises | Yes |
| Transfer verification | Yes |
| Interruption/recovery | Yes |
| Topic checkpoint | Yes |
| Common operational mistakes | Yes |

---

# 80. Quality and Safety Audit

Before considering this topic complete, confirm:

- [x] Beginner-to-production progression
- [x] Data Engineering framing
- [x] Commands are explained rather than dumped
- [x] Destructive commands carry explicit warnings
- [x] `rsync --delete` requires a dry-run workflow
- [x] `rclone sync` is explicitly treated as potentially destructive
- [x] Trailing-slash behavior is demonstrated
- [x] Resumability is demonstrated
- [x] SHA-256 integrity verification is demonstrated
- [x] Object-storage movement is covered
- [x] Production bandwidth impact is covered
- [x] Cloud egress awareness is covered
- [x] No real credentials are used
- [x] No real production infrastructure is required
- [x] MinIO is preferred for safe object-storage practice where available
- [x] Topic boundaries avoid duplicating the rest of G2
- [x] Troubleshooting follows evidence-based diagnosis
- [x] Transfer runbook is included
- [x] Final tool-selection mental model is included

---

# 81. Scope Boundary Reminder

This module teaches file transfer and synchronization.

When you need:

```text
SSH fundamentals
```

go to Topic 01.

When you need:

```text
SSH tunnels / port forwarding
```

go to Topic 02.

When you need:

```text
tmux / long-running interactive sessions
```

go to Topic 03.

When you need:

```text
systemd services and timers
```

go to Topic 05.

When you need:

```text
CPU / memory / I/O diagnosis
```

go to Topic 06.

When you need:

```text
disk / inode management
```

go to Topic 07.

When you need:

```text
CLI data inspection
```

go to Topic 08.

When you need:

```text
server log investigation
```

go to Topic 09.

When you need:

```text
users / sudo / package management / server hygiene
```

go to Topic 10.

The purpose of this boundary is to keep Topic 04 focused:

> **Move data reliably, safely, efficiently, and verifiably.**

---

# 82. Final Takeaway

A production Data Engineer should be able to look at a transfer request and quickly reason:

```text
What am I moving?
       ↓
How large is it?
       ↓
Where is it going?
       ↓
Filesystem or object storage?
       ↓
One-off or synchronization?
       ↓
Can it be interrupted?
       ↓
How will I resume?
       ↓
Could the command delete data?
       ↓
How will I verify integrity?
       ↓
What will it cost?
       ↓
What production resources will it consume?
```

Then select:

```text
scp
```

for simple one-off SSH transfers,

```text
rsync
```

for incremental server/filesystem synchronization,

```text
rclone
```

for object-storage and cloud data movement,

or:

```text
tar + SSH + compression
```

for an appropriate one-time streaming archive workflow.

The final production principle is:

> **Understand the transfer, predict its impact, execute it safely, recover intelligently, verify the result, and document what happened.**
