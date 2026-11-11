# Volumes, Bind Mounts, and Data Persistence

> **Gap Module G1 — Docker Essentials for Data Labs — Topic 04**  
> **Phase B — Connecting and Persisting**

This module teaches how container storage works, why container-local data is ephemeral, and how Docker volumes and bind mounts provide persistence for Data Engineering labs.

The central idea is:

> **Container lifecycle ≠ data lifecycle**

The learner should finish this module able to reason about:

```text
Where does the data actually live?
        ↓
What happens when the container stops?
        ↓
What happens when the container is removed?
        ↓
Is the data stored in the container writable layer?
        ↓
Is it stored in a named volume?
        ↓
Is it a host bind mount?
        ↓
Can I inspect the actual mount?
        ↓
Can I back it up and restore it?
```

This is not a Docker storage cheat sheet. It progresses from filesystem fundamentals to practical persistence, permissions, backup/restore, performance awareness, and Data Engineering operational patterns.

## Scope Boundary

This module focuses on **volumes, bind mounts, persistence, inspection, permissions, and storage operations**.

It intentionally does not become a full course on:

- environment variables and secrets;
- general container troubleshooting;
- Docker Compose;
- resource limits;
- cleanup/housekeeping beyond storage-safe deletion;
- Dockerfile/image construction;
- Kubernetes persistent volumes;
- full platform administration.

Those topics belong elsewhere in the G1 roadmap.

## 1. Learning Objectives

By the end of this module you should be able to:

- Explain a container filesystem and its writable layer.
- Explain why container-local data can disappear when a container is removed.
- Distinguish container-local storage from persistent storage.
- Create, inspect, attach, reuse, and safely delete Docker volumes.
- Explain named and anonymous volumes.
- Use both `-v` and `--mount` syntax.
- Explain mount source and destination paths.
- Use bind mounts for local datasets, source files, configuration files, and exported results.
- Compare named volumes and bind mounts using operational trade-offs rather than absolute rules.
- Explain persistence across `stop`, `start`, `restart`, `rm`, and recreation.
- Persist PostgreSQL data at its data directory.
- Persist MinIO object data.
- Understand persistence considerations for Kafka and Redis at the Docker-storage level.
- Share volumes safely between containers and understand concurrent-access limitations.
- Use read-only mounts for reference data and other appropriate inputs.
- Diagnose UID/GID and host/container permission mismatches.
- Inspect volumes and container mounts rather than guessing.
- Understand volume lifecycle and the destructive nature of volume deletion/pruning.
- Explain why persistence is not backup.
- Perform a practical Docker-volume backup and restore workflow.
- Understand why live database filesystem backups require consistency considerations.
- Understand volume drivers conceptually.
- Recognize storage-performance differences across workloads and platforms.
- Design a practical persistent-storage pattern for a local Data Engineering lab.

## 2. Why Data Persistence Matters in Data Engineering

Data Engineering services are stateful even when their containers are disposable.

Examples:

### PostgreSQL

PostgreSQL stores database files in its data directory. If those files exist only in the container's writable layer, removing the container removes the database state.

A production-minded lab therefore separates:

```text
PostgreSQL process
        ↓
container
        ↓
persistent data directory
        ↓
volume
```

The database process can be replaced while its data remains.

### Kafka

Kafka stores log segments and other state on disk. A Kafka learning lab that needs topics and messages to survive container replacement needs persistent storage for the relevant Kafka data directory.

This module does not teach Kafka's full storage architecture; it teaches the Docker persistence boundary.

### MinIO

Object data must live on persistent storage if objects should survive container replacement.

### Redis

Redis illustrates an important distinction:

```text
Application state
        ≠
Docker storage persistence
```

Redis can keep working state in memory, and Redis itself has persistence mechanisms. Docker persistence determines whether the filesystem containing those persistence files survives container lifecycle changes.

The professional principle is:

> **First understand which application data must survive. Then choose where that data should live.**

## 3. Prerequisites

This topic follows Topics 01–03.

You should already understand:

- containers and images;
- starting and stopping containers;
- PostgreSQL, MinIO, Redis, and Kafka as containerized services;
- ports;
- container networking;
- basic service connectivity.

A useful refresh is:

```text
Image
  ↓
Container
  ↓
Application process
  ↓
Application writes files
```

Topic 04 adds:

```text
Application writes files
        ↓
Where are those files stored?
        ↓
Container writable layer
        OR
Persistent volume
        OR
Host bind mount
```

Do not confuse networking persistence with storage persistence. A network determines **how services communicate**; a mount determines **where files are stored**.

## 4. Container Filesystem and Writable Layer

A Docker image is assembled from image layers. Conceptually, those image layers provide the application filesystem that a container starts from.

When the container runs, Docker provides a writable layer above the image layers.

A simplified model is:

```text
Container
│
├── Image layers
│     └── generally read-only
│
└── Container writable layer
      └── application writes
```

If a process creates:

```text
/app/output/result.json
```

and `/app/output` is not a mounted volume or bind mount, the write belongs to the container's writable layer.

### Why this matters

The writable layer is associated with the container instance.

Therefore:

```text
stop
start
```

keeps the same container and its writable layer.

But:

```text
rm
```

removes the container and its container-local writable data.

### Demonstration

Run a temporary container:

```bash
docker run -it --name storage-demo alpine sh
```

Inside it:

```sh
echo "hello" > /data.txt
cat /data.txt
```

Exit:

```sh
exit
```

The container still exists. Start it again:

```bash
docker start storage-demo
docker exec storage-demo cat /data.txt
```

The file remains.

Now remove the container:

```bash
docker rm storage-demo
```

Create a new container:

```bash
docker run --rm alpine cat /data.txt
```

The new container does not have the old file.

The key distinction is:

> **The file survived a stop/start because the container survived. It did not survive container removal because it was stored only in the container writable layer.**

## 5. Why Container-Local Data Is Ephemeral

"Ephemeral" means that the data's lifetime is tied to something temporary.

Container-local storage is useful for:

- temporary processing;
- caches;
- scratch files;
- generated intermediate artifacts;
- data that can be regenerated.

It is a poor default for state that must survive container replacement.

Think of the lifecycle:

```text
Container A
    │
    ├── writable layer
    │      └── database files
    │
    └── application
          ↓
       remove
          ↓
Container A is gone
          ↓
writable-layer data is gone
```

Compare that with a volume:

```text
Container A
    │
    └── mounts postgres_data
                │
                ▼
             Volume
                │
             database
                │
        remove Container A
                │
                ▼
             Volume
                │
             still exists
                │
                ▼
        Container B mounts it
```

This is the foundation of Docker persistence.

## 6. Docker Volumes

A Docker volume is a persistent storage object managed by Docker.

Create one:

```bash
docker volume create data_volume
```

List volumes:

```bash
docker volume ls
```

Inspect one:

```bash
docker volume inspect data_volume
```

A volume has its own lifecycle independent of the container that mounts it.

The conceptual relationship is:

```text
Container
   ↓
mounted volume
   ↓
Docker-managed persistent storage
```

### Volume lifecycle

```text
create
  ↓
attach
  ↓
use
  ↓
detach
  ↓
reuse
  ↓
backup
  ↓
delete
```

Deleting a container does not automatically mean deleting a named volume.

That independence is exactly what makes a named volume useful for stateful services.

## 7. Named Volumes

A named volume has an explicit Docker-managed name.

Create:

```bash
docker volume create postgres_data
```

Run PostgreSQL with it:

```bash
docker run -d   --name postgres   -e POSTGRES_PASSWORD=localdevpassword   -v postgres_data:/var/lib/postgresql/data   postgres:16
```

The mapping is:

```text
postgres_data
      ↓
/var/lib/postgresql/data
      ↓
PostgreSQL data files
```

### Why naming matters

A named volume:

- is easy to identify;
- can be deliberately reused;
- can be inspected;
- is independent of a particular container name;
- makes backup and recovery workflows easier to reason about.

Lifecycle:

```text
Volume created
      ↓
Container A mounts volume
      ↓
Container A writes data
      ↓
Container A removed
      ↓
Volume still exists
      ↓
Container B mounts same volume
      ↓
Data remains available
```

### Reuse

After removing a PostgreSQL container, a replacement can mount:

```text
postgres_data:/var/lib/postgresql/data
```

and recover the existing database state, assuming the replacement is compatible with that data directory.

### Important operational warning

A volume is data. Do not treat:

```bash
docker volume rm postgres_data
```

as harmless housekeeping.

## 8. Anonymous Volumes

An anonymous volume is a volume created without a deliberate human-readable volume name.

They can be useful when an image declares a volume or when a short-lived workload does not need an explicitly managed storage identity.

The operational trade-off is discoverability.

Compare:

```text
postgres_data
```

with an automatically generated anonymous volume identifier.

For Data Engineering labs, named volumes are generally easier to reason about because you can explicitly answer:

> "Which persistent storage belongs to PostgreSQL?"

### Important distinction

Anonymous does not mean "not persistent."

An anonymous volume can persist independently of the container. The difference is primarily how explicitly the storage object is named and managed.

Use named volumes when the data has operational significance.

## 9. Bind Mounts

A bind mount maps a specific host file or directory into a container.

Using modern syntax:

```bash
docker run --rm   --name data-reader   --mount type=bind,src=/path/on/host,dst=/data   alpine
```

Short syntax:

```bash
docker run --rm   --name data-reader   -v /path/on/host:/data   alpine
```

The relationship is:

```text
Host directory
      │
      │ bind mount
      ▼
Container /data
```

A bind mount gives the host direct visibility into the files.

### Source and destination

```text
src = host path
dst = container path
```

For example:

```text
src=/home/user/datasets
dst=/data
```

means files under the host directory are visible through `/data` inside the container.

### Operational consequences

Bind mounts make the host path part of the application's storage design. Therefore:

- host permissions matter;
- path syntax matters;
- host filesystem performance matters;
- the directory must exist/be accessible as expected;
- the storage lifecycle is controlled by the host filesystem, not Docker's volume object lifecycle.

## 10. Volume vs Bind Mount

| Characteristic | Named Volume | Bind Mount |
|---|---|---|
| Storage managed by | Docker | User/host |
| Source | Docker-managed storage | Explicit host path |
| Portability | Generally easier | Host-path dependent |
| Host visibility | Less direct | Direct |
| Common use | Persistent service data | Development files/data exchange |
| Lifecycle | Independent Docker object | Host path controls data |
| Permissions | Runtime-dependent | Host permissions are important |
| Best fit | Stateful service data | Local datasets, source, exports |

This is a decision guide, not an absolute law.

Consider:

- operating system;
- Docker runtime;
- workload;
- security;
- permissions;
- portability;
- backup requirements;
- development workflow;
- filesystem performance.

A named volume is often convenient for PostgreSQL data. A bind mount is often convenient for local Parquet/CSV data that the host needs to inspect directly.

But either mechanism can be technically appropriate when its operational trade-offs are understood.

## 11. Mount Source and Destination

A mount has two critical sides:

```text
SOURCE
  ↓
DESTINATION
```

For a named volume:

```bash
-v postgres_data:/var/lib/postgresql/data
```

the source is:

```text
postgres_data
```

and the destination is:

```text
/var/lib/postgresql/data
```

The destination is especially important because the application expects its data at a particular location.

### Correct path

```text
postgres_data
      ↓
/var/lib/postgresql/data
```

### Incorrect conceptual pattern

```text
postgres_data
      ↓
/some/unrelated/path
```

The volume may be working perfectly while PostgreSQL continues using another directory.

This creates a dangerous illusion:

> "I mounted a volume, so my database must be persistent."

Not necessarily.

Persistence depends on mounting the persistent storage at the application's actual data path.

### Mounting over existing container files

A mount can hide the content that would otherwise appear at the destination from the underlying image/container filesystem.

Therefore, understand the destination before mounting over it.

## 12. Persistence Across Container Lifecycle

The following experiment establishes the most important lifecycle distinction.

| Operation | Container | Named Volume | Container-local data |
|---|---|---|---|
| `docker stop` | Survives | Survives | Survives |
| `docker start` | Same container | Survives | Survives |
| `docker restart` | Same container | Survives | Survives |
| `docker rm` | Removed | Survives | Removed |
| Recreate container | New container | Survives if remounted | Old local data is gone |

### Scenario A — stop/start

```bash
docker stop my-container
docker start my-container
```

The same container returns, so its writable layer remains.

### Scenario B — restart

```bash
docker restart my-container
```

The same container is stopped and started. Its mounted volumes remain attached and its writable layer remains.

### Scenario C — remove

```bash
docker rm my-container
```

The container is removed. Data stored only in its writable layer is removed with it.

A named volume remains unless explicitly removed.

### Scenario D — replacement

Create a new container and mount the existing volume:

```text
Container B
    ↓
same named volume
    ↓
old persistent data
```

This is the fundamental reason persistent storage decouples data lifecycle from container lifecycle.

## 13. PostgreSQL Persistence

PostgreSQL is the primary database example because it makes the storage boundary concrete.

The conceptual architecture is:

```text
PostgreSQL container
        ↓
/var/lib/postgresql/data
        ↓
postgres_data volume
```

### Step 1 — Create the volume

```bash
docker volume create postgres_data
```

### Step 2 — Start PostgreSQL

```bash
docker run -d   --name postgres   -e POSTGRES_USER=dataeng   -e POSTGRES_PASSWORD=localdevpassword   -e POSTGRES_DB=datalab   -v postgres_data:/var/lib/postgresql/data   postgres:16
```

### Step 3 — Create test data

Connect using your available PostgreSQL client and create a table:

```sql
CREATE TABLE pipeline_runs (
    run_id integer PRIMARY KEY,
    pipeline_name text NOT NULL,
    status text NOT NULL
);

INSERT INTO pipeline_runs
VALUES
    (1, 'daily_orders', 'success'),
    (2, 'customer_snapshot', 'success'),
    (3, 'inventory_sync', 'running');
```

Verify:

```sql
SELECT * FROM pipeline_runs ORDER BY run_id;
```

### Step 4 — Stop and start

```bash
docker stop postgres
docker start postgres
```

Reconnect and verify the rows.

### Step 5 — Remove the container

```bash
docker rm -f postgres
```

The container is gone. Check:

```bash
docker volume ls
```

`postgres_data` should still exist.

### Step 6 — Create a replacement

```bash
docker run -d   --name postgres-replacement   -e POSTGRES_USER=dataeng   -e POSTGRES_PASSWORD=localdevpassword   -e POSTGRES_DB=datalab   -v postgres_data:/var/lib/postgresql/data   postgres:16
```

Reconnect and verify:

```sql
SELECT * FROM pipeline_runs ORDER BY run_id;
```

The data should still be present.

### Operational lesson

The volume is what decoupled PostgreSQL's data lifecycle from the original container lifecycle.

Do not conclude that any arbitrary PostgreSQL image version can safely reuse every existing data directory. Database compatibility and upgrade procedures remain application-level concerns.

## 14. MinIO Persistence

MinIO is the object-storage example.

The conceptual pattern is:

```text
MinIO container
      ↓
MinIO data directory
      ↓
Docker volume
```

Use the MinIO image's documented data directory for the version you are running.

The experiment is:

1. Create a named volume.
2. Start MinIO with that volume mounted at its data directory.
3. Create a bucket.
4. Upload a test object.
5. Stop/remove the container.
6. Start a compatible replacement using the same volume.
7. Verify that the bucket/object state remains.

The key learning target is Docker persistence, not a complete MinIO administration course.

### What to prove

```text
Object exists
      ↓
Container removed
      ↓
Volume remains
      ↓
Replacement container mounts volume
      ↓
Object still exists
```

Always verify the correct MinIO data directory for the image/version used in the lab.

## 15. Sharing Volumes Between Containers

A volume can be mounted by more than one container.

Conceptually:

```text
             ┌───────────────┐
             │ Container A   │
             │ Writer        │
             └───────┬───────┘
                     │
                     ▼
              ┌────────────┐
              │   Volume   │
              │ shared_data│
              └──────┬─────┘
                     │
                     ▼
             ┌───────────────┐
             │ Container B   │
             │ Reader        │
             └───────────────┘
```

Example:

```bash
docker volume create shared_data
```

Writer:

```bash
docker run --rm   --mount type=volume,src=shared_data,dst=/shared   alpine sh -c 'echo "generated dataset" > /shared/result.txt'
```

Reader:

```bash
docker run --rm   --mount type=volume,src=shared_data,dst=/shared,readonly   alpine cat /shared/result.txt
```

### Critical warning

A shared volume does not automatically make concurrent application writes safe.

For example, do not assume that two PostgreSQL instances can safely share the same database data directory merely because Docker permits both containers to mount it.

Database storage has application-level locking and consistency requirements.

The safe principle is:

> **Share files deliberately; share database data directories only according to the database system's supported architecture.**

## 16. Read-Only Mounts

A mount can be read-only.

With `--mount`:

```bash
docker run --rm   --mount type=volume,src=data_volume,dst=/data,readonly   alpine sh
```

The container can read the mounted data but should not be able to modify it through that mount.

A read-only bind mount can similarly be expressed using the appropriate `--mount` options.

### Useful Data Engineering cases

- reference datasets;
- immutable test fixtures;
- shared input data;
- configuration material that a process should not modify;
- reproducible local pipeline inputs.

### Why it matters

Read-only access reduces accidental mutation.

It is not a complete security boundary. Host access, container privileges, filesystem behavior, and other controls still matter.

### Verification

Try:

```sh
echo "should fail" > /data/test.txt
```

and observe the write failure.

Then explain:

```text
The network can be healthy.
The volume can exist.
The mount can be correct.
The write can still fail because the mount is read-only.
```

## 17. Permissions, UID, GID, and Ownership

Bind mounts make host/container identity differences especially visible.

A process has a user identity, commonly represented by:

- UID — user ID;
- GID — group ID.

Inspect identity:

```bash
id
```

Inspect file ownership:

```bash
ls -la
```

The important mental model is:

```text
Host user
    ≠
Container user
```

A host file may be owned by one UID/GID while the process inside the container runs as another.

The result can be:

```text
Permission denied
```

### Diagnose before changing permissions

Ask:

1. Which process is writing?
2. What UID/GID is it using?
3. Who owns the host file/directory?
4. What permissions are assigned?
5. Is the mount read-only?
6. Is the filesystem itself imposing additional restrictions?

### Do not use `chmod 777` as the first fix

Blindly doing:

```bash
chmod 777 /path
```

can hide the actual ownership problem and unnecessarily grant broad permissions.

A better engineering workflow is:

```text
Observe identity
      ↓
Inspect ownership
      ↓
Inspect mode
      ↓
Understand required access
      ↓
Apply the smallest appropriate fix
      ↓
Verify
```

For production-like labs, deliberately create one permission mismatch and diagnose it rather than memorizing a permission command.

## 18. Inspecting Volumes and Mounts

Inspect actual runtime state instead of relying on what you remember typing.

### List volumes

```bash
docker volume ls
```

### Inspect a volume

```bash
docker volume inspect postgres_data
```

Important information can include:

- volume name;
- driver;
- mountpoint;
- labels/options where applicable;
- runtime metadata.

### Inspect the container

```bash
docker inspect postgres
```

Look for the container's mount information.

The conceptual structure is:

```text
Container
   ↓
Mount
   ↓
Source
   ↓
Destination
   ↓
Read/write mode
```

Use inspection to answer:

- Does the volume exist?
- Is the expected volume attached?
- Is the destination correct?
- Is the mount read-only?
- Which storage driver is used?
- What is the volume mountpoint?
- Is the container actually using the storage you think it is?

### Professional habit

> **Inspect the actual runtime configuration before changing it.**

## 19. Volume Lifecycle and Safe Deletion

A volume has a lifecycle independent of the container.

```text
create
  ↓
attach
  ↓
use
  ↓
detach
  ↓
reuse
  ↓
backup
  ↓
delete
```

Create:

```bash
docker volume create data_volume
```

Remove a specific volume:

```bash
docker volume rm data_volume
```

Prune unused volumes:

```bash
docker volume prune
```

### Why pruning is dangerous

An unused volume can still contain valuable data.

For example:

```text
PostgreSQL container removed
        ↓
volume remains
        ↓
volume is currently not attached
        ↓
volume contains the only copy of local test data
        ↓
docker volume prune
        ↓
data may be destroyed
```

Therefore:

> **A volume being unused by a running container does not mean its data is worthless.**

Before deleting persistent storage, establish:

- what the volume contains;
- whether the data is recoverable elsewhere;
- whether a backup exists;
- whether the volume is truly disposable.

Treat volume deletion as a destructive operation.

## 20. Backup vs Persistence

One of the most important professional distinctions is:

```text
Persistence
=
data survives container lifecycle
```

while:

```text
Backup
=
independent recoverable copy of data
```

A persistent volume can still be lost through:

- accidental deletion;
- filesystem failure;
- host failure;
- corruption;
- operator error;
- an application-level destructive operation.

Therefore:

> **Persistence is not backup.**

A local PostgreSQL volume protects against replacing a container. It does not automatically protect against deleting the volume.

A proper lab should therefore think in two separate dimensions:

```text
Container lifecycle
        ↓
Persistence mechanism

Data protection
        ↓
Backup/recovery mechanism
```

## 21. Volume Backup and Restore

A common Docker-volume backup pattern uses a temporary helper container.

Conceptually:

```text
Volume
  ↓
temporary helper container
  ↓
archive
  ↓
host backup location
```

### Backup pattern

Suppose:

```text
postgres_data
```

is the volume.

A helper container can mount:

- the source volume at `/source`;
- a host bind-mounted backup directory at `/backup`.

A generic pattern is:

```bash
mkdir -p ./volume-backups

docker run --rm   --mount type=volume,src=postgres_data,dst=/source,readonly   --mount type=bind,src="$PWD/volume-backups",dst=/backup   alpine   sh -c 'tar czf /backup/postgres_data.tar.gz -C /source .'
```

This produces an archive under:

```text
./volume-backups/postgres_data.tar.gz
```

### What happened?

```text
postgres_data
      ↓
/source in helper container
      ↓
tar
      ↓
/backup in helper container
      ↓
host ./volume-backups
```

### Restore pattern

Create a new volume:

```bash
docker volume create postgres_restore
```

Then use a helper container to extract the archive:

```bash
docker run --rm   --mount type=volume,src=postgres_restore,dst=/target   --mount type=bind,src="$PWD/volume-backups",dst=/backup,readonly   alpine   sh -c 'tar xzf /backup/postgres_data.tar.gz -C /target'
```

Now inspect or mount `postgres_restore` from a compatible application container.

### Verify the restore

Never assume an archive is valid because the command exited successfully.

Verify:

```text
backup created
      ↓
archive exists
      ↓
restore completed
      ↓
replacement application mounts restored volume
      ↓
expected data is present
```

### Important database warning

A filesystem archive of a live database volume is not automatically an application-consistent database backup. See the next section.

## 22. Backup Consistency

A persistent filesystem does not automatically mean an application-consistent backup.

For a database such as PostgreSQL, files can be changing while the backup is being created.

Therefore:

```text
Storage persistence
       ≠
Application-consistent backup
```

### PostgreSQL example

A filesystem-level copy can be useful in certain controlled scenarios, but database-aware backup mechanisms such as logical backups (`pg_dump`) provide a different consistency model.

The important distinction is:

```text
Docker volume backup
    =
filesystem/storage operation

pg_dump
    =
PostgreSQL-aware logical database backup
```

This module does not replace PostgreSQL's backup documentation.

### Professional question

Before backing up a live stateful service, ask:

1. What consistency guarantee do I need?
2. Is the application still writing?
3. Does the application provide a supported backup mechanism?
4. Can the storage snapshot be considered crash-consistent?
5. How will I verify the restore?

For a local learning lab, explicitly demonstrate the difference between **copying storage** and **performing an application-aware backup**.

## 23. Volume Drivers

Docker volumes are an abstraction. The underlying storage implementation can vary.

At a basic level, Docker commonly uses the local volume driver for local persistent storage.

Conceptually:

```text
Application
    ↓
Docker volume abstraction
    ↓
Volume driver
    ↓
Actual storage
```

Advanced environments can use other storage backends or volume plugins.

For this module, you only need to understand:

- a volume is not synonymous with one physical storage technology;
- Docker provides a management abstraction;
- the driver determines how the volume is implemented;
- local development commonly uses Docker-managed local storage.

Inspect the driver:

```bash
docker volume inspect data_volume
```

Do not turn this module into a third-party volume-plugin tutorial.

## 24. Storage Performance Considerations

Storage choice affects Data Engineering workloads differently.

At a high level, consider:

- local filesystem performance;
- bind-mount overhead;
- Docker Desktop filesystem translation;
- Linux filesystem behavior;
- metadata-heavy workloads;
- database workloads;
- large-file workloads;
- many-small-file workloads.

### Example comparison

A bind mount may be very convenient for:

```text
Host Parquet/CSV
      ↓
Processing container
```

because the host needs direct visibility.

But a database workload such as PostgreSQL can have very different I/O characteristics.

Likewise, a Kafka workload may involve sustained log-segment writes.

### Platform awareness

On Linux, containers often interact with the host filesystem more directly.

On Docker Desktop, containers run through a platform layer and host filesystem access can have different performance characteristics.

On Windows + WSL2 and macOS, filesystem boundaries can further affect behavior.

Do not infer performance solely from functional correctness:

```text
"It works"
    ≠
"It is the best storage choice for this workload"
```

Measure before optimizing. Full platform details belong to Topic 10.

## 25. Platform Considerations

Bind mounts depend on host filesystem behavior, so the runtime platform matters.

Consider:

- Linux;
- macOS;
- Windows;
- Docker Desktop;
- WSL2.

Relevant differences include:

### Path syntax

Host path conventions differ.

### Permissions

Linux-style UID/GID behavior may not map identically to every desktop environment.

### Filesystem sharing

Docker Desktop environments mediate access between the host filesystem and Linux containers.

### Performance

Large datasets and metadata-heavy workloads can behave differently across filesystem boundaries.

### WSL2

The location of files within Windows-mounted versus Linux-side filesystems can affect performance and behavior.

The scope here is intentionally limited:

> **Understand enough platform behavior to choose and troubleshoot storage mounts.**

The complete platform curriculum belongs to Topic 10.

## 26. Data Engineering Storage Patterns

### Pattern 1 — PostgreSQL state

```text
PostgreSQL container
      ↓
named volume
      ↓
/var/lib/postgresql/data
```

Use this when database state must survive container replacement.

### Pattern 2 — Local Parquet input

```text
Host datasets/
      ↓
bind mount
      ↓
/data
      ↓
processing container
```

Useful when the host needs direct access to input files.

### Pattern 3 — Exported results

```text
processing container
      ↓
/output
      ↓
bind mount
      ↓
host output/
```

Useful when generated results need to be inspected or consumed by host tools.

### Pattern 4 — Shared reference dataset

```text
named volume
      ↓
container A (read-only)
      +
container B (read-only)
```

Use only when concurrent access semantics are appropriate.

### Pattern 5 — MinIO object data

```text
MinIO
  ↓
documented data directory
  ↓
named volume
```

The objective is persistence of object storage state.

### Pattern 6 — Kafka local state

```text
Kafka
  ↓
documented Kafka data directory
  ↓
persistent storage
```

Keep exact directory/configuration details aligned with the Kafka distribution/image in use.

### Pattern 7 — Temporary processing scratch

```text
Container writable layer
```

Use when the data is intentionally disposable and reproducible.

The key question is always:

> **Does this data need to survive replacement of the container?**

## 27. Hands-On Persistence Lab

Build a complete local persistence lab.

## Lab objective

Prove, rather than assume, that persistent storage decouples data from the container lifecycle.

### Exercise 1 — Container-local storage

Run:

```bash
docker run -it --name ephemeral-demo alpine sh
```

Inside:

```sh
echo "temporary" > /tmp/example.txt
cat /tmp/example.txt
```

Exit, start again, and verify the file.

Then remove the container and recreate it.

Record the result.

### Exercise 2 — Named volume

Create:

```bash
docker volume create postgres_data
```

Inspect:

```bash
docker volume inspect postgres_data
```

### Exercise 3 — PostgreSQL persistence

Run PostgreSQL using:

```text
postgres_data
    ↓
/var/lib/postgresql/data
```

Create a database table and test data.

### Exercise 4 — Stop/start

```bash
docker stop postgres
docker start postgres
```

Verify the data.

### Exercise 5 — Remove/recreate

Remove the container but keep the volume.

Create a replacement container using the same volume.

Verify the data again.

### Exercise 6 — Inspect the mount

Use:

```bash
docker inspect postgres-replacement
```

Find the mount and record:

```text
source
destination
read/write mode
```

### Exercise 7 — Bind mount

Create a host directory:

```bash
mkdir -p ./lab-data
```

Run:

```bash
docker run --rm   --mount type=bind,src="$PWD/lab-data",dst=/data   alpine   sh -c 'echo "hello from container" > /data/result.txt'
```

Verify from the host:

```bash
cat ./lab-data/result.txt
```

### Exercise 8 — Read-only mount

Run a container with the directory mounted read-only.

Attempt:

```sh
echo "should fail" > /data/test.txt
```

Record the error and explain why.

### Exercise 9 — Permission experiment

Create a host file/directory with restrictive permissions.

Inside the container:

```bash
id
ls -la /data
```

Diagnose the mismatch without using `chmod 777` as a shortcut.

### Exercise 10 — Volume backup

Back up the PostgreSQL volume using a helper container and an archive.

Verify that the archive exists.

### Exercise 11 — Restore

Create a new volume and restore the archive into it.

Mount the restored volume into a compatible test container.

### Exercise 12 — Verify recovery

Prove that the expected data is present.

Your lab notes should record:

```text
Experiment
Command
Expected result
Observed result
Why it happened
Evidence
```

## 28. Break/Fix Troubleshooting Lab

For each failure, follow:

```text
Symptom
   ↓
Hypothesis
   ↓
Inspection
   ↓
Root cause
   ↓
Fix
   ↓
Verification
```

### Failure 1 — Container removed and data expected to survive

**Symptom:** file/database is gone.

**Likely cause:** data was stored only in the container writable layer.

**Inspect:** determine whether a volume was mounted.

**Fix:** mount appropriate persistent storage.

**Verify:** recreate the container and confirm data survives.

### Failure 2 — Wrong mount path

**Symptom:** application starts with unexpected or empty state.

**Likely cause:** volume is mounted somewhere other than the application's data directory.

**Inspect:** `docker inspect <container>`.

**Fix:** mount at the correct application data path.

**Verify:** application uses the mounted storage.

### Failure 3 — Wrong volume name

**Symptom:** replacement container appears empty.

**Likely cause:** it mounted a different volume.

**Inspect:**

```bash
docker volume ls
docker inspect <container>
```

**Fix:** attach the intended volume.

### Failure 4 — Volume exists but is not mounted

**Symptom:** expected volume is present but application writes elsewhere.

**Fix:** verify the container's mount configuration.

### Failure 5 — Permission denied

**Symptom:** application cannot read/write.

**Inspect:**

```bash
id
ls -la
```

and the host-side ownership/mode where applicable.

**Fix:** align ownership/permissions with the required process identity.

### Failure 6 — Read-only mount causes write failure

**Symptom:** read succeeds; write fails.

**Root cause:** mount is intentionally read-only.

**Verification:** inspect mount mode.

### Failure 7 — Volume accidentally deleted

**Symptom:** volume no longer exists.

**Response:** check whether a valid backup exists.

**Lesson:** persistence without backup is not a complete recovery strategy.

### Failure 8 — Wrong bind-mount host directory

**Symptom:** container sees an empty or unexpected dataset.

**Inspect:** verify the absolute/expanded host path.

**Fix:** mount the intended directory.

### Failure 9 — PostgreSQL starts with unexpected/empty data

Possible causes include:

- wrong volume;
- wrong destination;
- new empty volume;
- initialization against empty storage.

Inspect the actual mounts before changing PostgreSQL settings.

### Failure 10 — Shared database directory

**Symptom:** two database instances attempt to use the same files.

**Root concern:** database-level storage concurrency and locking, not Docker's ability to mount a volume twice.

**Correct approach:** follow the database's supported topology rather than treating a volume as a generic shared database filesystem.

## 29. Real-World Data Engineering Scenarios

### Scenario 1 — PostgreSQL container replacement

A developer replaces PostgreSQL and discovers an empty database.

**Diagnosis:** Was the original database directory stored in a named volume? Was the same volume mounted at the correct destination?

**Expected design:**

```text
postgres_data
    ↓
/var/lib/postgresql/data
```

### Scenario 2 — Local Parquet processing

A processing container needs direct access to Parquet files on the host.

**Likely choice:** bind mount.

Why?

- host already owns the dataset;
- host needs direct visibility;
- processing container consumes the files.

### Scenario 3 — Shared dataset

Two containers need the same local dataset.

**Possible design:** shared volume or bind mount, preferably read-only when neither container should mutate the source.

**Question:** Does the workload require concurrent writes? If yes, application-level consistency must be considered.

### Scenario 4 — Database persistence

PostgreSQL must survive container recreation.

**Design:** named volume at the documented PostgreSQL data directory.

**Verification:** remove container, recreate it, mount same volume, query known data.

### Scenario 5 — Backup

A local Data Engineering lab contains valuable test data.

**Question:** Is persistence enough?

**Answer:** No.

A separate backup copy is required if recovery matters.

### Scenario 6 — Storage performance

A developer bind-mounts a large dataset and notices slow processing on a desktop platform.

**Diagnosis:** inspect filesystem location and runtime platform before changing application code.

**Lesson:** functional correctness does not guarantee optimal storage performance.

## 30. Common Mistakes

### 1. Assuming container-local storage is permanent

**Why it happens:** the file remains after a restart, so the learner assumes it is persistent.

**Correct model:** stop/start preserves the same container; removal destroys its writable layer.

### 2. Confusing `stop` with `rm`

**Why it happens:** both make the application unavailable.

**Correct model:** `stop` preserves the container; `rm` removes it.

### 3. Deleting a volume accidentally

**Why it happens:** volumes are mistaken for disposable Docker metadata.

**Correct model:** a volume can contain the only copy of important lab data.

### 4. Using the wrong mount destination

**Why it happens:** the learner assumes any mounted directory becomes application storage.

**Correct model:** the application must write to the mounted destination.

### 5. Mounting an empty host directory over expected container files

**Why it happens:** bind mounts replace the visible content at the destination.

**Correct model:** inspect what the application expects at that path.

### 6. Using the wrong volume name

**Why it happens:** similar volume names are easy to confuse.

**Correct model:** verify with `docker volume ls` and `docker inspect`.

### 7. Forgetting to remount a volume

**Why it happens:** the replacement container has a new filesystem.

**Correct model:** persistence exists only along the storage path that is actually mounted.

### 8. Ignoring filesystem permissions

**Why it happens:** host and container users are assumed to be identical.

**Correct model:** inspect UID/GID and ownership.

### 9. Using `chmod 777` as the first solution

**Why it happens:** it can appear to fix access immediately.

**Correct model:** diagnose ownership and required access first.

### 10. Assuming persistence equals backup

**Why it happens:** data survives container replacement.

**Correct model:** backups protect against storage/data loss beyond container lifecycle.

### 11. Backing up a live database without considering consistency

**Why it happens:** a volume is treated as an ordinary directory.

**Correct model:** database-aware backup semantics matter.

### 12. Sharing database storage incorrectly

**Why it happens:** Docker permits multiple mounts.

**Correct model:** application-level concurrency and storage semantics still apply.

### 13. Assuming bind mounts behave identically on every OS

**Why it happens:** the same Docker command looks portable.

**Correct model:** host paths, permissions, filesystem sharing, and performance can differ.

### 14. Using `docker volume prune` without understanding consequences

**Why it happens:** "unused" is mistaken for "unimportant."

**Correct model:** an unattached volume may contain valuable recoverable data.

## 31. Mental Models

### Mental Model 1 — Image

```text
Image
=
template
```

An image provides the starting filesystem and application environment.

### Mental Model 2 — Container

```text
Container
=
running instance
```

It has its own lifecycle and writable layer.

### Mental Model 3 — Container writable layer

```text
Container writable layer
=
container lifecycle-bound storage
```

Useful for temporary state; unsafe as the default location for state that must survive container removal.

### Mental Model 4 — Volume

```text
Volume
=
Docker-managed persistent storage
```

Its lifecycle is independent of the container that mounts it.

### Mental Model 5 — Bind mount

```text
Bind mount
=
host path mapped into container
```

The host filesystem controls the underlying path.

### Mental Model 6 — Lifecycle separation

```text
Container lifecycle
    ≠
Data lifecycle
```

### Mental Model 7 — Recovery separation

```text
Persistence
    ≠
Backup
```

### Mental Model 8 — Mount correctness

```text
Storage exists
    ≠
Application is using it
```

The volume must be mounted at the correct application data path.

### Mental Model 9 — Inspection

```text
What I intended
    ≠
What is running
```

Use:

```bash
docker inspect
docker volume inspect
```

to verify the runtime state.

## 32. Command Reference

### List volumes

```bash
docker volume ls
```

**Purpose:** list Docker volumes.

**Expected behavior:** displays available volume objects.

### Create a volume

```bash
docker volume create data_volume
```

**Purpose:** create named persistent storage.

**Expected behavior:** returns the volume name.

### Inspect a volume

```bash
docker volume inspect data_volume
```

**Purpose:** inspect driver, mountpoint, name, and metadata.

**Warning:** mountpoint visibility does not mean the application is using the volume correctly.

### Remove a volume

```bash
docker volume rm data_volume
```

**Purpose:** delete a volume.

**Warning:** potentially destructive; verify backups and usage first.

### Prune unused volumes

```bash
docker volume prune
```

**Purpose:** remove unused volumes according to Docker's pruning rules.

**Warning:** unused does not mean unimportant.

### Run with a named volume

```bash
docker run   --name postgres   -v postgres_data:/var/lib/postgresql/data   postgres:16
```

**Purpose:** mount named volume at the PostgreSQL data path.

### Run with `--mount`

```bash
docker run   --name postgres   --mount type=volume,src=postgres_data,dst=/var/lib/postgresql/data   postgres:16
```

**Purpose:** explicit mount configuration.

### Bind mount with `--mount`

```bash
docker run --rm   --mount type=bind,src="$PWD/data",dst=/data   alpine
```

**Purpose:** expose a host directory inside the container.

### Bind mount with `-v`

```bash
docker run --rm   -v "$PWD/data:/data"   alpine
```

**Purpose:** shorter bind-mount syntax.

### Read-only volume

```bash
docker run --rm   --mount type=volume,src=data_volume,dst=/data,readonly   alpine
```

**Purpose:** prevent writes through that mount.

### Inspect container mounts

```bash
docker inspect <container>
```

**Purpose:** verify actual mount source, destination, and mode.

### Container lifecycle

```bash
docker stop <container>
docker start <container>
docker restart <container>
docker rm <container>
```

**Purpose:** test how container lifecycle affects local and persistent data.

### Identity and permissions

Inside a container:

```bash
id
ls -la /data
```

**Purpose:** identify UID/GID and inspect ownership/modes.

### Backup pattern

```bash
mkdir -p ./volume-backups

docker run --rm   --mount type=volume,src=postgres_data,dst=/source,readonly   --mount type=bind,src="$PWD/volume-backups",dst=/backup   alpine   sh -c 'tar czf /backup/postgres_data.tar.gz -C /source .'
```

**Purpose:** create a simple archive of a volume.

**Warning:** this is a filesystem-level backup pattern, not automatically an application-consistent live database backup.

### Restore pattern

```bash
docker volume create postgres_restore

docker run --rm   --mount type=volume,src=postgres_restore,dst=/target   --mount type=bind,src="$PWD/volume-backups",dst=/backup,readonly   alpine   sh -c 'tar xzf /backup/postgres_data.tar.gz -C /target'
```

**Purpose:** extract an archive into a new volume.

**Verification:** mount the restored volume into a compatible test environment and verify expected data.

## 33. Practice Questions

## Beginner

### 1. What is a Docker volume?

**Answer:** A Docker-managed storage object that can outlive the container using it.

**Why it matters:** It separates persistent data from the container lifecycle.

**Example:**

```bash
docker volume create data_volume
```

### 2. What is a bind mount?

**Answer:** A mapping of a specific host file or directory into a container.

**Example:**

```bash
--mount type=bind,src="$PWD/data",dst=/data
```

### 3. Why can container-local data disappear?

**Answer:** Because it may exist only in the container writable layer, which is removed with the container.

### 4. What happens when a container is removed?

**Answer:** The container and its writable-layer data are removed. A separately managed named volume can remain.

## Intermediate

### 5. Volume vs bind mount?

**Answer:** A named volume is managed by Docker; a bind mount exposes an explicit host path.

### 6. Why does mount destination matter?

**Answer:** The application must write its state to the mounted destination for the persistent storage to contain that state.

### 7. Why does a volume survive container removal?

**Answer:** The volume is a separate Docker storage object with its own lifecycle.

### 8. How do you inspect a volume?

```bash
docker volume inspect <volume>
```

### 9. How do you diagnose a permission problem?

Inspect:

```bash
id
ls -la
```

and compare process identity with file ownership/mode.

## Advanced

### 10. Why is persistence different from backup?

**Answer:** Persistence survives container lifecycle changes; backup provides an independent recoverable copy.

### 11. Why can filesystem-level database backup be problematic?

**Answer:** The application may be modifying files during the copy, so the resulting archive may not have the required application-consistency guarantees.

### 12. When would you use a bind mount instead of a named volume?

**Answer:** When direct host filesystem access is a requirement, such as local datasets or exported results.

### 13. What happens if two database containers share the same data directory?

**Answer:** Docker can mount the storage, but database-level concurrency and locking rules still apply. This is not automatically a supported or safe architecture.

### 14. How would you design persistent storage for a local Data Engineering lab?

**Answer:** Use named volumes for stateful services such as PostgreSQL and MinIO where appropriate, bind mounts for host-managed datasets/exports, read-only mounts for immutable reference data, and a separate backup strategy for valuable state.

## 34. Interview Practice

### 1. What is the difference between a Docker volume and a bind mount?

**Short answer:** A volume is Docker-managed storage; a bind mount maps an explicit host path.

**Detailed answer:** Volumes have their own Docker lifecycle and are convenient for stateful service data. Bind mounts expose host filesystem locations directly and therefore inherit host path and permission concerns.

**Data Engineering example:** PostgreSQL database files commonly fit a named volume; local Parquet input commonly fits a bind mount.

### 2. What happens to data when a container is removed?

**Short answer:** Data in the container writable layer is removed; separately managed volumes can remain.

**Example:** `docker rm postgres` removes container-local files but does not inherently delete `postgres_data`.

### 3. How do you persist PostgreSQL data in Docker?

**Short answer:** Mount persistent storage at the PostgreSQL data directory.

**Example:**

```text
postgres_data → /var/lib/postgresql/data
```

### 4. What is the difference between container-local storage and persistent storage?

**Short answer:** Container-local storage follows the container lifecycle; persistent storage has an independent storage lifecycle.

### 5. How would you troubleshoot PostgreSQL starting with an empty database?

**Strong approach:**

1. Inspect the container.
2. Verify the mount exists.
3. Verify the source volume.
4. Verify the destination path.
5. Verify the replacement container mounted the intended volume.
6. Check whether the volume itself is new/empty.
7. Check whether initialization occurred against empty storage.

### 6. How do you inspect Docker volume configuration?

Use:

```bash
docker volume inspect postgres_data
docker inspect postgres
```

### 7. Why are permissions different between host and container?

Because the process inside the container can run under a different UID/GID from the host user, and host filesystem permissions still apply to bind-mounted paths.

### 8. Why is `chmod 777` not an appropriate default fix?

Because it grants broad permissions without diagnosing the underlying ownership/access requirement and can weaken the security posture.

### 9. Does persistence provide backup?

No. Persistence protects against some container lifecycle events. Backup provides an independent recovery copy.

### 10. How would you back up a Docker volume?

Use a helper container to mount the volume and archive its contents to a host backup directory, while considering application consistency for stateful services.

### 11. What are consistency concerns when backing up a live database?

The database can modify files during the copy. A filesystem archive may not provide the application-level consistency guarantee required for reliable recovery.

### 12. When would you choose bind mounts over named volumes?

When direct host filesystem access is useful or required, such as local datasets, development source, or exported output.

### 13. What happens if a container is recreated without remounting its previous volume?

The replacement container gets a new filesystem state and does not automatically see the old persistent data.

### 14. What risks are associated with `docker volume prune`?

It can remove unused volumes that contain valuable data. "Unused" means not currently attached according to Docker's criteria, not necessarily disposable.

### 15. How would you design persistent storage for PostgreSQL + MinIO + Kafka?

Give each stateful service an explicitly managed persistent storage path appropriate to its image/application, keep host-managed datasets in deliberate bind mounts when required, avoid unsafe shared database directories, and establish backup/recovery procedures for state that matters.

## 35. Final Knowledge Check

You have completed the conceptual portion when you can answer these without memorization:

1. What is the container writable layer?
2. Why does `stop` preserve container-local files while `rm` removes them?
3. What is the difference between a named volume and an anonymous volume?
4. What is a bind mount?
5. Which side of a bind mount is controlled by the host?
6. Why does mount destination matter?
7. What happens to a named volume when its container is removed?
8. How do you prove PostgreSQL data survived container replacement?
9. Why does a read-only mount reject writes?
10. How do UID/GID mismatches produce permission errors?
11. Why is `chmod 777` a poor default troubleshooting strategy?
12. What information does `docker volume inspect` provide?
13. What information does `docker inspect` provide about mounts?
14. Why is an unused volume not necessarily disposable?
15. Why is persistence not backup?
16. What is the difference between a filesystem-level volume archive and a PostgreSQL-aware backup?
17. Why can sharing a volume between containers be safe for one workload but unsafe for a database data directory?
18. How can platform differences affect bind mounts?
19. Why can a storage design be functionally correct but still perform poorly?
20. What storage pattern would you choose for PostgreSQL data, local Parquet input, and exported pipeline output?

### The final explanation you should be able to give

> **A container has its own writable layer, but that layer is tied to the container lifecycle. If application data needs to survive container replacement, I need persistent storage. Docker volumes provide Docker-managed persistent storage, while bind mounts expose a specific host path inside the container. I need to choose the appropriate storage mechanism, mount it at the correct application data directory, verify the actual mount configuration, understand permissions, and separately plan backups because persistence alone is not backup.**

## 36. Module Completion Checklist

### Filesystem fundamentals

- [ ] I understand image layers.
- [ ] I understand the container writable layer.
- [ ] I can explain why container-local data is lifecycle-bound.
- [ ] I understand the difference between stopping and removing a container.

### Docker volumes

- [ ] I can create a named volume.
- [ ] I can list volumes.
- [ ] I can inspect a volume.
- [ ] I understand named volumes.
- [ ] I understand anonymous volumes.
- [ ] I can attach a volume to a container.
- [ ] I can reuse a volume with a replacement container.
- [ ] I understand volume lifecycle.

### Bind mounts

- [ ] I can use `-v`.
- [ ] I can use `--mount`.
- [ ] I understand source and destination.
- [ ] I understand host-path ownership and permissions.
- [ ] I can use a bind mount for local datasets.
- [ ] I can use a bind mount for exported results.
- [ ] I understand read-only mounts.

### Stateful services

- [ ] I can persist PostgreSQL data.
- [ ] I can explain MinIO persistence.
- [ ] I understand the storage role for Kafka and Redis at the required scope.
- [ ] I understand why the correct application data directory matters.

### Inspection and troubleshooting

- [ ] I can inspect volume configuration.
- [ ] I can inspect container mount configuration.
- [ ] I can diagnose a wrong volume.
- [ ] I can diagnose a wrong mount destination.
- [ ] I can diagnose permission errors.
- [ ] I can diagnose read-only mount failures.
- [ ] I can diagnose missing persistence after container recreation.

### Data safety

- [ ] I understand that volume deletion can destroy data.
- [ ] I understand why `docker volume prune` is potentially destructive.
- [ ] I understand persistence vs backup.
- [ ] I can perform a basic volume archive backup.
- [ ] I can restore into a new volume.
- [ ] I understand database backup consistency concerns.
- [ ] I know that backup verification matters.

### Operational awareness

- [ ] I understand volume drivers conceptually.
- [ ] I understand storage-performance considerations.
- [ ] I understand platform-specific bind-mount considerations.
- [ ] I can choose between a named volume and bind mount using workload requirements.
- [ ] I can explain the professional mental model:

```text
Container lifecycle
        ≠
Storage lifecycle
        ≠
Backup lifecycle
```

### Final mastery standard

You are ready to move on when you can independently build, destroy, recreate, inspect, back up, restore, and explain a persistent PostgreSQL lab without confusing container lifecycle with data lifecycle.

## 37. Roadmap Coverage Audit

The supplied Topic 04 specification requires the following concepts. This final audit confirms coverage.

- [x] Filesystem fundamentals
- [x] Container writable layer
- [x] Image layers
- [x] Ephemeral container-local data
- [x] Persistent data
- [x] Docker volumes
- [x] Named volumes
- [x] Anonymous volumes
- [x] Bind mounts
- [x] Host paths
- [x] Mount points
- [x] Mount source and destination
- [x] Read-write mounts
- [x] Read-only mounts
- [x] `-v`
- [x] `--mount`
- [x] Volume lifecycle
- [x] Persistence across stop/start/restart/rm/recreate
- [x] PostgreSQL persistence
- [x] PostgreSQL data directory
- [x] First initialization vs existing persistent data
- [x] MinIO persistence
- [x] Redis persistence distinction at Docker-storage scope
- [x] Kafka persistence awareness at Docker-storage scope
- [x] Sharing volumes between containers
- [x] Concurrent-access/consistency considerations
- [x] Permissions
- [x] UID/GID
- [x] Ownership
- [x] Root vs non-root awareness
- [x] Safe permission troubleshooting
- [x] Why `chmod 777` is not the default fix
- [x] Volume inspection
- [x] Container mount inspection
- [x] `docker volume ls`
- [x] `docker volume create`
- [x] `docker volume inspect`
- [x] `docker volume rm`
- [x] `docker volume prune`
- [x] Persistence vs backup
- [x] Volume backup
- [x] Volume restore
- [x] Backup verification
- [x] Backup consistency
- [x] PostgreSQL filesystem backup vs logical backup awareness
- [x] Volume driver awareness
- [x] Storage performance awareness
- [x] Linux/macOS/Windows/Docker Desktop/WSL2 considerations
- [x] Data Engineering storage patterns
- [x] Hands-on persistence lab
- [x] Break/fix troubleshooting lab
- [x] Real-world Data Engineering scenarios
- [x] Common mistakes
- [x] Mental models
- [x] Command reference
- [x] Practice questions
- [x] Interview practice
- [x] Final knowledge check
- [x] Module completion checklist

### Scope audit

This module remains focused on Topic 04 — Volumes, Bind Mounts, and Data Persistence. It references networking, configuration, troubleshooting, Compose, resource limits, cleanup, and platform topics only where required to explain storage behavior; it does not replace their dedicated curricula.
