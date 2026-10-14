# Cleanup, Disk Usage, and Housekeeping

## Learning Objectives

By the end of this module, you should be able to:

- Explain why Docker consumes disk space even after containers are stopped.
- Measure Docker disk usage with `docker system df` and `docker system df -v`.
- Distinguish images, containers, volumes, networks, logs, and build cache.
- Identify stopped containers, dangling images, unused images, and reclaimable resources.
- Use Docker prune commands deliberately rather than blindly.
- Explain why volume cleanup is materially more dangerous than image or cache cleanup.
- Protect important PostgreSQL, MinIO, Kafka, Redis, and other persistent lab data.
- Control container log growth with log size limits and rotation.
- Use names and labels to identify resources safely.
- Perform a progressive weekly housekeeping routine.
- Reset one Docker Compose lab without destroying another lab's volumes.
- Build and understand a defensive `housekeeping.sh` script.
- Understand Docker data locations conceptually on Linux, Windows/WSL2, and macOS.
- Distinguish logical Docker cleanup from physical Docker Desktop/WSL2 virtual-disk reclamation.
- Diagnose disk-capacity incidents using evidence before deleting anything.

---

## Why Docker Disk Management Matters

Docker makes Data Engineering labs convenient because PostgreSQL, MinIO, Kafka, Redis, Schema Registry, Spark, Airflow, and Flink can run locally without installing every dependency directly on the host.

That convenience has a cost: **Docker stores data for the resources you create.**

A long-running Data Engineering lab can accumulate:

```text
Images
Stopped containers
Volumes
Container logs
Build cache
Unused networks
Old image versions
Temporary resources
```

A common beginner assumption is:

> "I stopped the containers, so the disk space should be free."

That is not generally true.

Stopping a container changes its runtime state. It does not automatically remove:

- the stopped container;
- its writable container layer;
- the image used to create it;
- its named volumes;
- unrelated images;
- unrelated volumes;
- build cache;
- Docker-managed log data.

Think of cleanup as several separate operations:

```text
Stop container
    ↓
Container remains

Remove container
    ↓
Container metadata/writable layer removed
    ↓
Image may still remain
    ↓
Volume may still remain

Remove image
    ↓
Image becomes unavailable locally
    ↓
May need to be pulled again

Remove volume
    ↓
Persistent data may be permanently lost

Remove build cache
    ↓
Future builds may need more work/downloads

Control/remove logs
    ↓
Log-related disk consumption decreases
```

The professional habit is therefore:

```text
Measure
  ↓
Identify
  ↓
Classify
  ↓
Backup if necessary
  ↓
Delete deliberately
  ↓
Measure again
```

Never make `docker system prune` your mental model of housekeeping.

---

## Prerequisites

You should already understand:

- basic Docker containers and images;
- `docker run`, `docker ps`, and `docker stop`;
- Docker volumes;
- Docker Compose;
- basic container logs;
- basic resource limits;
- PostgreSQL, MinIO, Kafka, and Redis as local Data Engineering services.

Relevant previous topics are:

```text
Topic 01 → Containers, Images, and Registries
Topic 02 → Databases and Services in Containers
Topic 03 → Ports, Networks, and Service Discovery
Topic 04 → Volumes and Data Persistence
Topic 05 → Environment Variables and Configuration
Topic 06 → Logs, Exec, and Troubleshooting
Topic 07 → Docker Compose Stacks
Topic 08 → Resource Limits and Laptop Capacity
Topic 09 → Cleanup, Disk Usage, and Housekeeping
Topic 10 → Docker Desktop, WSL2, and Platform Differences
```

Topic 04 is especially important because persistent volumes are the main data-loss boundary in cleanup work.

---

# 1. Docker Disk-Space Mental Model

## 1.1 The big picture

A useful mental model is:

```text
Docker storage
│
├── Images
│
├── Containers
│
├── Volumes
│
├── Build cache
│
├── Container logs
│
└── Other Docker-managed data
```

These categories are related but are not interchangeable.

| Category | What it is | Why it uses disk | Usually safe to remove? | Main risk |
|---|---|---|---|---|
| Images | Read-only application filesystem layers | Downloaded image layers | Sometimes | Future pulls required |
| Containers | Container metadata and writable layer | Runtime changes and metadata | Stopped containers can often be removed | Losing stopped-container state |
| Volumes | Persistent storage | Database/object/message data | Only after confirming data is disposable | **Data loss** |
| Networks | Docker network definitions | Small amount of metadata | Unused networks can generally be removed | Misclassification |
| Logs | Application stdout/stderr retained by logging system | Noisy services | Control/rotate carefully | Loss of diagnostic history |
| Build cache | Reusable build artifacts | Previous image builds | Usually reclaimable | Slower future builds |

### Critical distinction

```text
Unused
≠
Unimportant
```

A volume can be unused by currently running containers while still containing valuable historical data.

A local image can be unused today but useful for an offline or bandwidth-constrained environment.

A stopped container can contain configuration clues that help diagnose an earlier failure.

---

## 1.2 Why Data Engineering labs grow quickly

Consider a local stack:

```text
PostgreSQL
MinIO
Kafka
Redis
Schema Registry
Spark
Airflow
Flink
```

Repeated experimentation can create:

```text
postgres:16
postgres:15
redis:7
multiple Kafka image versions
old application images
stopped test containers
PostgreSQL volumes
MinIO object-storage volumes
Kafka data volumes
large container logs
build cache
temporary networks
```

The disk footprint can therefore grow even if only a small part of the stack is currently running.

---

# 2. Measuring Disk Usage with `docker system df`

## 2.1 The first command

Before deleting anything, run:

```bash
docker system df
```

This is the starting point because it gives you a Docker-level view of where space is being consumed.

A representative output may look conceptually like:

```text
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          12        5         8.2GB     4.1GB
Containers      14        3         1.1GB     900MB
Local Volumes   8         4         24GB      11GB
Build Cache     17                  3.4GB     3.4GB
```

The exact formatting and values depend on your Docker version and local state.

### Important fields

- **TOTAL** — resources in that category.
- **ACTIVE** — resources currently associated with active use where applicable.
- **SIZE** — estimated storage consumed by the category.
- **RECLAIMABLE** — space Docker identifies as potentially reclaimable.

Do not interpret `RECLAIMABLE` as:

> "Delete this immediately."

It means:

> "Docker considers this space potentially reclaimable under relevant cleanup semantics."

You still need to understand what the resource is and whether your lab depends on it.

---

## 2.2 Verbose inspection

Use:

```bash
docker system df -v
```

The verbose view is especially useful before cleanup because it gives more detail about individual resources.

A safe workflow is:

```text
docker system df
       ↓
Where is the largest category?
       ↓
docker system df -v
       ↓
Which specific resources are responsible?
       ↓
Is the resource needed?
       ↓
Backup if required
       ↓
Delete selected resources
```

---

## 2.3 Example investigation

Suppose:

```text
Docker total footprint ≈ 70 GB
```

You discover:

```text
Images        18 GB
Containers     2 GB
Volumes       42 GB
Build cache    8 GB
```

The wrong response is:

```bash
docker system prune -a
```

The better response is:

```text
42 GB is in volumes.
    ↓
Identify volumes.
    ↓
Determine which contain PostgreSQL/MinIO/Kafka state.
    ↓
Back up valuable data.
    ↓
Remove only disposable state.
```

This is the central skill of Topic 09: **reasoning before deleting**.

---

# 3. Inspecting Images, Containers, Volumes, and Networks

## 3.1 Containers

List running containers:

```bash
docker ps
```

List all containers, including stopped ones:

```bash
docker ps -a
```

Why `docker ps -a` matters:

```text
docker ps
    ↓
running containers only

docker ps -a
    ↓
running + stopped containers
```

Stopped containers still consume some storage and can accumulate over time.

---

## 3.2 Images

List images:

```bash
docker images
```

or:

```bash
docker image ls
```

Typical columns include:

```text
REPOSITORY
TAG
IMAGE ID
CREATED
SIZE
```

Example:

```text
REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
postgres     16        abc123...      ...           430MB
postgres     15        def456...      ...           410MB
redis        7         ghi789...      ...           120MB
```

An image being large does not automatically mean it is safe to remove.

---

## 3.3 Volumes

List volumes:

```bash
docker volume ls
```

Inspect a specific volume:

```bash
docker volume inspect <volume>
```

A volume can contain:

```text
PostgreSQL database files
MinIO object data
Kafka data
Redis persistence
Application state
```

Treat a volume as **data**, not as disposable Docker metadata.

---

## 3.4 Networks

List networks:

```bash
docker network ls
```

Networks generally consume much less disk than images and volumes, but unused networks can accumulate and make a lab harder to understand.

---

## 3.5 Safe inspection workflow

Use:

```text
Measure
  ↓
docker system df
  ↓
Inspect details
  ↓
docker system df -v
  ↓
List resources
  ↓
docker ps -a
docker images
docker volume ls
docker network ls
  ↓
Classify
  ↓
Backup important data
  ↓
Delete deliberately
  ↓
Measure again
```

---

# 4. Removing Stopped Containers

## 4.1 Why stopped containers remain

When you run:

```bash
docker stop my-container
```

Docker stops the process but does not remove the container.

The container remains available for:

```bash
docker start my-container
```

That is useful operationally, but it means storage remains allocated.

---

## 4.2 Identify stopped containers

Run:

```bash
docker ps -a
```

Look for states such as:

```text
Exited (...)
Created
```

Before removing one, ask:

1. Is this container still needed?
2. Is it part of a Compose project?
3. Does it contain useful diagnostic state?
4. Is its persistent data stored in a volume?
5. Can it be recreated from the image/Compose definition?

---

## 4.3 Remove one container

```bash
docker rm <container>
```

For example:

```bash
docker rm old-postgres-test
```

Removing a container does **not** automatically mean:

```text
image deleted
volume deleted
network deleted
```

Those resources have separate lifecycles.

---

## 4.4 Batch cleanup

Docker provides:

```bash
docker container prune
```

This removes stopped containers according to Docker's prune semantics.

Before using it, inspect:

```bash
docker ps -a
```

and confirm that stopped containers are disposable.

---

# 5. Understanding Docker Images

## 5.1 Image layers

Docker images are built from layers.

Conceptually:

```text
Application image
│
├── Base OS/runtime layer
├── Dependency layer
├── Application layer
└── Configuration/metadata
```

Multiple images can share layers. Therefore, the displayed image size is not necessarily equal to the exact additional disk consumption caused by that image.

This is another reason to use:

```bash
docker system df
```

rather than manually adding every displayed image size.

---

## 5.2 Repository, tag, image ID, and size

Example:

```text
REPOSITORY   TAG     IMAGE ID      CREATED      SIZE
postgres     16      abc123        ...          430MB
```

Interpretation:

- `postgres` — repository.
- `16` — tag.
- `abc123` — local image identifier.
- `CREATED` — image metadata.
- `SIZE` — reported image size.

Tags are mutable names. If exact reproducibility matters, a digest is more precise than a human-friendly tag.

---

## 5.3 Dangling images

A dangling image commonly appears as:

```text
<none>   <none>
```

Dangling images are generally image layers that are no longer associated with a tagged image reference.

They can appear after image rebuilds or updates.

A useful distinction is:

```text
Dangling image
    ↓
Usually untagged / orphaned image state

Unused image
    ↓
Image not currently used by a container under relevant Docker semantics

Currently used image
    ↓
Referenced by a container
```

Do not treat all three categories as identical.

---

## 5.4 Image updates

Suppose your lab originally uses:

```text
postgres:15
```

and later you pull:

```text
postgres:16
```

The older image may remain locally.

Repeated updates can therefore leave several image versions:

```text
postgres:14
postgres:15
postgres:16
```

Keeping old versions can be useful for compatibility testing, but keeping every historical version forever consumes disk.

The correct decision is:

```text
Do I still need this image locally?
```

not:

```text
Is this image old?
```

---

# 6. Docker Prune Commands

Prune commands are cleanup tools. They are not substitutes for understanding your storage model.

## 6.1 Prune overview

| Command | Primary target | Typical effect | Main risk |
|---|---|---|---|
| `docker container prune` | stopped containers | removes stopped containers | loss of stopped-container state |
| `docker image prune` | dangling images | removes dangling images | usually low |
| `docker image prune -a` | unused images | removes images not used by containers under command semantics | future re-pulls |
| `docker network prune` | unused networks | removes unused networks | misclassification |
| `docker volume prune` | unused volumes | removes volumes meeting prune criteria | **DATA LOSS** |
| `docker builder prune` | build cache | removes build cache | slower future builds |
| `docker system prune` | multiple unused resource categories | broad cleanup | broader impact |
| `docker system prune -a` | broader unused resources | more aggressive cleanup | significant cleanup |

Exact affected resources depend on Docker version and command options. Always consult the command's current help output when using unfamiliar filters or options:

```bash
docker <command> --help
```

---

## 6.2 `docker container prune`

```bash
docker container prune
```

### What it does

Targets stopped containers according to Docker's prune rules.

### What it does not mean

It does not mean:

```text
delete images
delete volumes
delete all logs everywhere
delete all networks
```

### Safe use

First:

```bash
docker ps -a
```

Then remove containers that are confirmed disposable.

### Dangerous example

You stop a failed PostgreSQL container because you want to investigate it later, then run container pruning and lose that stopped container's metadata.

The database volume may still exist, but the stopped container itself is gone.

### Verify

```bash
docker ps -a
docker system df
```

---

## 6.3 `docker image prune`

```bash
docker image prune
```

This targets dangling images under the command's default semantics.

It is generally less destructive than:

```bash
docker image prune -a
```

Inspect first:

```bash
docker images
```

Use:

```bash
docker system df -v
```

when you need more context.

---

## 6.4 `docker image prune -a`

```bash
docker image prune -a
```

This is broader.

It can remove images that are not currently used by containers under Docker's prune semantics, not merely `<none>:<none>` dangling images.

### Main consequence

If you later need one of those images, Docker may need to download it again.

That can matter when:

- bandwidth is limited;
- you work offline;
- image pulls are slow;
- a registry is unavailable;
- a particular historical version is needed.

### Safe decision

Ask:

```text
Do I need this image locally?
Can I re-pull it?
Is the image intentionally retained for testing?
```

---

## 6.5 `docker network prune`

```bash
docker network prune
```

This removes unused networks according to Docker's rules.

Before using it:

```bash
docker network ls
```

If you use Compose, remember that project networks are normally created and managed as part of the project's lifecycle.

Do not confuse:

```text
unused network
```

with:

```text
network used by another project
```

---

## 6.6 `docker volume prune`

This is the high-risk command:

```bash
docker volume prune
```

It can remove unused Docker volumes according to Docker's prune semantics.

The word **unused** is the danger.

Consider:

```text
PostgreSQL container removed
        ↓
PostgreSQL volume remains
        ↓
Volume currently attached to no container
        ↓
Docker may consider it unused
        ↓
Volume prune may remove it
        ↓
Database files may be permanently lost
```

Therefore:

```bash
docker volume prune
```

should never be treated as routine "garbage collection" without first identifying what the volumes contain.

Inspect:

```bash
docker volume ls
docker volume inspect <volume>
```

and, when necessary, inspect the containers/projects that previously used the volume.

### Safe principle

> An unused volume is not necessarily an unimportant volume.

---

## 6.7 `docker builder prune`

```bash
docker builder prune
```

This removes build cache according to the selected builder and command semantics.

The normal consequence is not database data loss. Instead, future builds may take longer because cached layers/artifacts are gone.

Use it when:

```text
Build cache is consuming substantial space
AND
You accept slower future builds.
```

---

## 6.8 `docker system prune`

```bash
docker system prune
```

This is a broader cleanup operation that can affect multiple categories of unused resources.

Because it combines categories, understand its current scope before execution:

```bash
docker system prune --help
```

Do not rely on memory alone when operating a production-like environment.

---

## 6.9 `docker system prune -a`

```bash
docker system prune -a
```

This is more aggressive because it broadens image cleanup beyond dangling images.

Use it only when you understand:

- which images you need;
- which containers you need;
- whether future image pulls are acceptable;
- whether persistent volumes require protection.

### Important distinction

Neither `docker system prune` nor `docker system prune -a` should be your automatic first response to a full disk.

The first response is:

```bash
docker system df
docker system df -v
```

---

# 7. Volumes and Data-Loss Risk

## 7.1 Image, container, and volume are different things

Remember:

```text
Image
  ≠
Container
  ≠
Volume
```

For PostgreSQL:

```text
postgres container
       │
       ▼
postgres-data volume
       │
       ▼
database files
```

Removing the container does not necessarily remove the volume.

That separation is exactly what makes persistent data survive container recreation.

It is also what makes careless volume cleanup dangerous.

---

## 7.2 Inspect a volume

List:

```bash
docker volume ls
```

Inspect:

```bash
docker volume inspect <volume>
```

Depending on the Docker environment, inspection exposes metadata such as:

- volume name;
- driver;
- mountpoint;
- labels;
- creation-related metadata where available;
- other driver-specific information.

Do not assume the `Mountpoint` is directly browsable from the host on Docker Desktop; platform virtualization changes that model.

---

## 7.3 Determine what uses a volume

A useful inspection pattern is to examine container mounts:

```bash
docker ps -a --format '{{.ID}}\t{{.Names}}'
```

Then inspect likely containers:

```bash
docker inspect <container>
```

For a known volume, you can search container metadata on Linux/macOS shells with appropriate tools, but do not assume every shell has the same utilities.

For Compose projects, project-scoped resource names and labels are often more reliable than guessing from names.

---

## 7.4 Unused vs unimportant

These are different questions:

```text
Is the volume currently attached?
        AND
Does the data matter?
```

A volume can be:

```text
Unused + valuable
Unused + disposable
Used + valuable
Used + disposable
```

Cleanup should be based on **data importance**, not only attachment state.

---

# 8. Backing Up Important Data Before Cleanup

Topic 04 established persistence and backup concepts. Topic 09 applies those concepts before destructive housekeeping.

The operational principle is:

> Before destructive cleanup, persistent data that matters should be backed up.

Use:

```text
Identify volume
    ↓
Determine whether data matters
    ↓
Backup
    ↓
Verify backup
    ↓
Cleanup
    ↓
Restore if necessary
```

---

## 8.1 PostgreSQL application-consistent backup

For PostgreSQL, prefer a database-aware backup rather than treating raw database files as ordinary files.

For example:

```bash
docker exec -t pg-lab \
  pg_dump -U dataeng -d datalab \
  > datalab-backup.sql
```

This creates a logical SQL backup.

You can restore into a suitable PostgreSQL database with:

```bash
cat datalab-backup.sql | \
docker exec -i pg-lab \
psql -U dataeng -d datalab
```

For larger or more structured backups, `pg_dump` custom format can be useful:

```bash
docker exec -t pg-lab \
  pg_dump -U dataeng -d datalab -Fc \
  > datalab-backup.dump
```

Restore with:

```bash
cat datalab-backup.dump | \
docker exec -i pg-lab \
pg_restore -U dataeng -d datalab --clean --if-exists
```

Use restore options deliberately and understand their consequences.

---

## 8.2 Filesystem copy vs application-consistent backup

Do not confuse:

```text
Filesystem copy
```

with:

```text
Application-consistent database backup
```

A raw volume archive may capture database files while the database is actively changing. That does not automatically make it a valid, application-consistent backup.

For databases, prefer database-native backup mechanisms when appropriate.

For object storage such as MinIO, backup strategy depends on the storage architecture and whether the data can be recreated.

---

## 8.3 Verify backups

A backup is not trustworthy merely because a command completed.

At minimum verify:

```bash
ls -lh datalab-backup.sql
```

For serious workflows, test restoration into a disposable environment.

The operational loop is:

```text
Backup
  ↓
Verify
  ↓
Cleanup
```

not:

```text
Backup
  ↓
Assume
  ↓
Delete
```

---

# 9. Container Log Growth

## 9.1 Why logs consume disk

A useful mental model is:

```text
Application
    ↓
stdout / stderr
    ↓
Docker logging mechanism
    ↓
retained log data
    ↓
disk consumption
```

A noisy service can produce large amounts of output.

Examples include:

- Kafka;
- Python applications;
- Airflow;
- Spark;
- PostgreSQL;
- services stuck in restart loops;
- applications logging exceptions repeatedly.

A container can be healthy while still producing too many logs.

---

## 9.2 Inspect logs

Use:

```bash
docker logs <container>
```

Limit output:

```bash
docker logs --tail 100 <container>
```

Show recent activity:

```bash
docker logs --since 1h <container>
```

These commands help you understand log behavior, but **reading logs does not control log growth**.

---

## 9.3 A noisy-container example

Suppose:

```text
Python application
    ↓
exception every second
    ↓
restart
    ↓
exception every second
    ↓
restart
    ↓
...
```

You may get:

```text
large logs
+
CPU usage
+
container restart activity
+
disk pressure
```

This is not merely a cleanup problem.

It is also an application/troubleshooting problem.

The correct response is:

```text
Inspect logs
    ↓
Find the underlying failure
    ↓
Fix the failure
    ↓
Control log retention
```

---

# 10. Log Size Limits and Rotation

## 10.1 Why rotation matters

Without rotation:

```text
log
 ↓
grows
 ↓
grows
 ↓
grows
 ↓
disk fills
```

With rotation:

```text
log
 ↓
reaches size limit
 ↓
rotates
 ↓
older log managed/removed according to policy
 ↓
disk usage controlled
```

Log rotation is therefore a capacity-control mechanism.

---

## 10.2 Compose example

A Compose service can specify logging configuration such as:

```yaml
services:
  postgres:
    image: postgres:16
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

Conceptually:

- `max-size: "10m"` limits the size at which a log file is rotated.
- `max-file: "3"` controls the number of retained rotated files under the logging configuration.
- Rotation prevents unbounded growth under the configured logging driver.

Exact behavior depends on the logging driver and Docker environment.

---

## 10.3 Rotation is not blind deletion

A poor strategy is:

```text
Delete logs whenever disk usage is high.
```

A better strategy is:

```text
Control log volume
      ↓
Rotate predictably
      ↓
Retain enough history for troubleshooting
      ↓
Use centralized logging when the environment requires it
```

This module only covers operator-level Docker log retention. It is not a complete observability or centralized logging course.

---

# 11. Naming and Labeling Lab Resources

Safe cleanup depends on knowing **what belongs to what**.

## 11.1 Good names

Prefer:

```text
de-lab-postgres
de-lab-minio
de-lab-kafka
de-lab-redis
```

over:

```text
test1
postgres2
container_new
```

Meaningful names make commands and incident investigations easier.

---

## 11.2 Docker labels

Labels provide structured metadata.

Example:

```bash
docker run \
  --name de-lab-postgres \
  --label project=data-engineering-lab \
  --label environment=local \
  postgres:16
```

You can use labels to support:

```text
Identification
    ↓
Filtering
    ↓
Automation
    ↓
Safer cleanup
```

Inspect labels with:

```bash
docker inspect de-lab-postgres
```

---

## 11.3 Compose project identity

For Compose, explicitly naming the project can make resource ownership easier to reason about:

```bash
docker compose -p lab-a up -d
```

Another project can use:

```bash
docker compose -p lab-b up -d
```

Now the two labs have distinct project identities.

This is particularly useful when you need to reset one lab without touching another.

---

# 12. Safe Cleanup Strategy

Cleanup should become progressively more destructive.

A professional hierarchy is:

```text
Level 1 — Inspect
    ↓
Level 2 — Remove stopped containers
    ↓
Level 3 — Remove dangling images
    ↓
Level 4 — Remove clearly unused images
    ↓
Level 5 — Remove unused networks
    ↓
Level 6 — Clean build cache
    ↓
Level 7 — Review volumes manually
    ↓
Level 8 — Backup important data
    ↓
Level 9 — Remove selected disposable volumes
    ↓
Level 10 — Reclaim platform virtual disk if required
```

Why this order?

Because early actions generally have lower consequences, while later actions can destroy persistent state.

---

## 12.1 The operational loop

For every cleanup operation:

```text
What am I deleting?
        ↓
Why is it safe?
        ↓
What depends on it?
        ↓
Do I need a backup?
        ↓
Delete
        ↓
Verify
```

---

# 13. Weekly Housekeeping Routine

A local Data Engineering laptop benefits from a predictable weekly routine.

## Step 1 — Check host disk space

Use your operating system's disk-usage tools.

Examples on Linux/macOS:

```bash
df -h
```

On Windows, use the operating system's storage view or PowerShell tools appropriate to your environment.

The exact host command is platform-specific.

---

## Step 2 — Check Docker usage

```bash
docker system df
```

If something looks unexpectedly large:

```bash
docker system df -v
```

---

## Step 3 — Identify stopped containers

```bash
docker ps -a
```

Remove only containers that are confirmed disposable.

---

## Step 4 — Review images

```bash
docker images
```

Look for:

```text
dangling images
old versions
large images no longer needed
```

Do not delete images merely because they are old.

---

## Step 5 — Review volumes

```bash
docker volume ls
```

Ask:

```text
Which volumes contain valuable data?
Which are disposable?
Which belong to another lab?
```

Back up important state before destructive cleanup.

---

## Step 6 — Check noisy containers

Use:

```bash
docker ps
docker logs --tail 100 <container>
```

For suspected high log volume, inspect logging configuration and application behavior.

---

## Step 7 — Clean safe resources

Examples:

```bash
docker container prune
```

and, when appropriate:

```bash
docker image prune
```

Do not automatically perform volume cleanup.

---

## Step 8 — Back up important state

For PostgreSQL:

```bash
docker exec -t pg-lab \
  pg_dump -U dataeng -d datalab \
  > datalab-backup.sql
```

Verify the backup.

---

## Step 9 — Remove selected disposable volumes

Only after identification and backup:

```bash
docker volume rm <volume>
```

Prefer explicit selection over broad volume pruning when data is important.

---

## Step 10 — Measure again

```bash
docker system df
```

Compare before and after.

---

## Weekly checklist

```text
[ ] Check host disk space
[ ] Run docker system df
[ ] Run docker system df -v if needed
[ ] Review stopped containers
[ ] Review old/dangling images
[ ] Review volumes
[ ] Check noisy services
[ ] Clean safe candidates
[ ] Back up important state
[ ] Remove selected disposable volumes
[ ] Measure again
[ ] Consider platform-level reclamation only if necessary
```

---

# 14. Resetting One Lab Safely

This is one of the most important operational patterns in a multi-lab environment.

Imagine:

```text
Lab A → Kafka + Redis
Lab B → PostgreSQL + MinIO
Lab C → Spark
```

You want to reset Lab A.

You do **not** want to execute a global cleanup that could remove Lab B's PostgreSQL or MinIO data.

---

## 14.1 Project-scoped identity

Start Lab A with:

```bash
docker compose -p lab-a up -d
```

Lab B:

```bash
docker compose -p lab-b up -d
```

This gives you a project boundary.

---

## 14.2 Safe reset sequence

```text
Identify project
       ↓
List its containers
       ↓
Identify its networks
       ↓
Identify its volumes
       ↓
Backup important volumes
       ↓
Stop project
       ↓
Remove only project resources
       ↓
Verify other labs remain intact
```

For a project where its persistent data is intentionally disposable:

```bash
docker compose -p lab-a down -v
```

**Warning:** `-v` removes volumes associated with that Compose project according to Compose semantics. Do not use it unless you have explicitly decided that those volumes and their data are disposable or backed up.

A safer reset when preserving volumes is:

```bash
docker compose -p lab-a down
```

Then recreate:

```bash
docker compose -p lab-a up -d
```

---

## 14.3 Reset vs global cleanup

These are different operations:

```text
Reset this lab
    ≠
Clean the entire Docker installation
```

Prefer the smallest scope that solves the problem.

That principle reduces accidental cross-lab damage.

---

# 15. Building `housekeeping.sh`

A small housekeeping script should favor safety over cleverness.

The goal is:

```text
Show usage
   ↓
Show relevant resources
   ↓
Clean safe candidates
   ↓
Ask before volume operations
   ↓
Never blindly run destructive volume cleanup
   ↓
Show usage afterward
```

## 15.1 Example script

Save the following as:

```text
docker_lab/09/housekeeping.sh
```

```bash
#!/usr/bin/env bash

set -euo pipefail

echo "========================================"
echo "Docker Housekeeping"
echo "========================================"

echo
echo "Docker disk usage BEFORE cleanup:"
docker system df

echo
echo "Stopped containers:"
docker ps -a --filter status=exited

echo
echo "Images:"
docker image ls

echo
echo "Volumes:"
docker volume ls

echo
echo "Networks:"
docker network ls

echo
echo "----------------------------------------"
echo "Safe cleanup candidates"
echo "----------------------------------------"

read -r -p "Remove stopped containers? [y/N] " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    docker container prune
else
    echo "Skipped stopped-container cleanup."
fi

read -r -p "Remove dangling images? [y/N] " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    docker image prune
else
    echo "Skipped dangling-image cleanup."
fi

read -r -p "Clean build cache? [y/N] " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    docker builder prune
else
    echo "Skipped build-cache cleanup."
fi

echo
echo "----------------------------------------"
echo "Volume cleanup"
echo "----------------------------------------"
echo "Volume cleanup is intentionally NOT automatic."
echo "Review volumes manually before removing any."

read -r -p "Do you want to review unused volumes now? [y/N] " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    docker volume ls
    echo
    echo "No automatic volume deletion is performed."
    echo "Use explicit docker volume rm only after confirming:"
    echo "  1. the volume is disposable;"
    echo "  2. important data is backed up;"
    echo "  3. the volume does not belong to another lab."
else
    echo "Skipped volume review."
fi

echo
echo "Docker disk usage AFTER cleanup:"
docker system df

echo
echo "Housekeeping complete."
```

---

## 15.2 Why `set -euo pipefail`?

The script uses:

```bash
set -euo pipefail
```

Conceptually:

- `-e` — stop when an unexpected command fails.
- `-u` — treat unset variables as errors.
- `pipefail` — propagate failures through pipelines.

This is defensive shell scripting.

It does not make a script automatically safe, but it reduces several common classes of scripting mistakes.

---

## 15.3 Make it executable

On Linux/macOS/WSL:

```bash
chmod +x housekeeping.sh
```

Run:

```bash
./housekeeping.sh
```

The script intentionally does **not** execute:

```bash
docker volume prune
```

automatically.

That is a deliberate safety boundary.

---

## 15.4 Script design principle

A safe housekeeping script should:

```text
Be explicit
Be inspectable
Ask before destructive actions
Avoid global deletion
Protect persistent data
Show before/after state
```

Avoid clever one-liners such as:

```bash
docker system prune -a --volumes -f
```

as a default housekeeping strategy.

The shorter command is not the safer command.

---

# 16. Where Docker Stores Data

Docker's storage architecture differs by platform.

## 16.1 Linux

On a native Linux Docker Engine installation, Docker uses a storage area governed by its Docker data-root configuration.

A common default is under:

```text
/var/lib/docker
```

but do not assume this path is universal.

Inspect the configuration:

```bash
docker info
```

Look for storage-related information such as the Docker root directory/data-root reported by your installation.

The correct principle is:

> Discover the configured Docker storage location rather than assuming a hard-coded path.

---

## 16.2 Windows + WSL2

Docker Desktop commonly uses a Linux environment backed by virtualized storage.

Conceptually:

```text
Windows host
    ↓
Docker Desktop
    ↓
WSL2/Linux environment
    ↓
Docker data
    ↓
Virtual disk storage
```

The exact physical file location and management model depend on Docker Desktop and WSL configuration.

Do not treat a Linux path such as:

```text
/var/lib/docker
```

as the physical Windows disk path.

---

## 16.3 macOS

Docker Desktop uses a Linux virtualized environment:

```text
macOS
   ↓
Docker Desktop
   ↓
Linux VM/environment
   ↓
Docker data
   ↓
Virtual disk
```

The exact physical location depends on the Docker Desktop implementation and configuration.

---

## 16.4 Why this matters

Docker-level storage and host-level storage are related but not identical.

You may see:

```text
docker system df
```

decrease significantly while the host's Docker virtual disk file remains approximately the same size.

That leads to the next concept.

---

# 17. Docker Desktop, WSL2, and Virtual Disk Reclamation

## 17.1 Logical cleanup vs physical reclamation

A crucial concept is:

> Deleting Docker resources and shrinking the underlying virtual disk are not necessarily the same operation.

Conceptually:

```text
Docker cleanup
      ↓
Docker-managed data decreases
      ↓
Virtual disk has free space internally
      ↓
Virtual disk file may still remain large
      ↓
Platform-specific reclamation may be required
```

This is particularly relevant to:

```text
Windows + WSL2
macOS + Docker Desktop
```

---

## 17.2 Why this happens

Virtual disks often behave like allocated storage containers.

Suppose a virtual disk grows to:

```text
100 GB
```

You clean Docker data and only need:

```text
40 GB
```

Internally, the virtual disk may now contain:

```text
40 GB used
60 GB free
```

But the physical virtual-disk file may still be around its previously allocated size.

Therefore:

```text
Docker storage used
≠
physical virtual-disk file size
```

---

## 17.3 Reclamation is platform-specific

Reclaiming physical space can involve:

- WSL2 virtual disk management on Windows;
- Docker Desktop storage management;
- VM/disk compaction mechanisms;
- platform-specific administrative tools.

These procedures vary by Docker Desktop version, WSL2 configuration, filesystem, and platform.

Therefore do **not** blindly execute a VM/storage command copied from an unrelated environment.

Before any virtual-disk operation:

1. clean Docker resources first;
2. confirm valuable data is backed up;
3. understand the Docker Desktop/WSL2 storage model;
4. follow the appropriate current platform documentation;
5. verify the target virtual disk;
6. avoid destructive operations unless you fully understand their effect.

This is intentionally an advanced awareness topic. Detailed platform-specific procedures belong with Topic 10.

---

# 18. Hands-On Lab — `docker_lab/09/`

Create the lab directory:

```text
docker_lab/
└── 09/
    ├── housekeeping.sh
    └── notes.md
```

The only required artifact from this module is the learning document; the lab files above are exercises for your local practice.

---

## Exercise 1 — Before/After Disk Measurement

Run:

```bash
docker system df
```

Record:

```text
Images:
Containers:
Local Volumes:
Build Cache:
```

Then inspect:

```bash
docker system df -v
```

Clean selected safe candidates:

```bash
docker container prune
```

and:

```bash
docker image prune
```

Optionally clean build cache:

```bash
docker builder prune
```

Measure again:

```bash
docker system df
```

Answer:

1. Which category decreased?
2. Which category did not change?
3. Why?
4. Did the Docker host disk usage change by exactly the same amount?
5. If not, why might the numbers differ?

---

## Exercise 2 — Identify Unused Volumes

Run:

```bash
docker volume ls
```

For candidate volumes:

```bash
docker volume inspect <volume>
```

Determine:

```text
Which volumes contain valuable data?
Which volumes are disposable?
Which volumes belong to another lab?
```

Back up important PostgreSQL data.

Then remove only a disposable volume:

```bash
docker volume rm <disposable-volume>
```

Verify:

```bash
docker volume ls
docker system df
```

Confirm that the valuable data still exists.

---

## Exercise 3 — Log Growth

Use a test container that produces controlled output.

For example:

```bash
docker run -d \
  --name log-lab \
  busybox \
  sh -c 'i=0; while true; do echo "log-line-$i"; i=$((i+1)); done'
```

Observe:

```bash
docker logs --tail 20 log-lab
```

Inspect Docker usage:

```bash
docker system df
```

Do not let an intentionally noisy test run indefinitely.

Stop it:

```bash
docker stop log-lab
```

Remove it:

```bash
docker rm log-lab
```

For a real Compose service, configure controlled log rotation such as:

```yaml
logging:
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"
```

Verify the behavior in your environment.

---

## Exercise 4 — Build `housekeeping.sh`

Create:

```text
docker_lab/09/housekeeping.sh
```

Use the example from Section 15.

Test it first in a disposable environment.

Confirm that it:

```text
[ ] Shows Docker usage
[ ] Shows relevant resources
[ ] Asks before safe cleanup actions
[ ] Does not blindly delete volumes
[ ] Shows final Docker usage
```

---

## Exercise 5 — Platform Virtual Disk

On Windows/WSL2 or macOS/Docker Desktop:

1. Record the host storage footprint.
2. Run `docker system df`.
3. Clean disposable Docker data.
4. Run `docker system df` again.
5. Observe whether the host's Docker virtual disk footprint changed by the same amount.
6. Document the platform-specific reclamation procedure using the appropriate current platform documentation.
7. Do not blindly execute destructive VM/storage operations.

---

# 19. Break/Fix Exercises

## Scenario 1 — Disk is nearly full

### Symptom

Your laptop reports very little free space.

### Investigation

Run:

```bash
docker system df
docker system df -v
docker ps -a
docker images
docker volume ls
```

### Reasoning

Determine whether the major consumer is:

```text
images
containers
volumes
build cache
logs/other Docker data
```

### Decision

Do not prune everything.

Clean the largest safe category first.

### Verification

Measure again:

```bash
docker system df
```

---

## Scenario 2 — PostgreSQL volume appears unused

### Symptom

A PostgreSQL container has been removed and its volume appears unused.

### Wrong response

```bash
docker volume prune
```

### Correct investigation

```bash
docker volume ls
docker volume inspect <volume>
```

Determine:

```text
Does the volume contain the PostgreSQL database?
Does the database matter?
Was it backed up?
Does another lab expect it?
```

Only after answering these questions should you consider removal.

---

## Scenario 3 — Large reclaimable image space

### Symptom

`docker system df` reports significant reclaimable image space.

### Decision questions

```text
Do I need offline copies?
Do I need older versions?
Can I re-pull them?
Is the registry available?
Are the images used by any current container?
```

Then choose between:

```bash
docker image prune
```

or broader image cleanup.

---

## Scenario 4 — Huge container logs

### Symptom

A service has very large logs.

### Investigation

```bash
docker logs --tail 100 <container>
```

Determine whether the service is:

```text
legitimately verbose
or
stuck in an error/restart loop
```

Then:

```text
Fix application behavior
+
configure appropriate log retention
```

---

## Scenario 5 — A volume was deleted

### Symptom

A cleanup operation removed a PostgreSQL volume.

### Root cause

The volume was treated as Docker garbage rather than persistent application state.

### Prevention

```text
Identify data
    ↓
Backup
    ↓
Verify backup
    ↓
Cleanup
```

### Recovery

Restore from the tested backup where possible.

This scenario demonstrates why volume cleanup requires a different risk level.

---

## Scenario 6 — Docker resources deleted but disk file remains large

### Symptom

```bash
docker system df
```

shows much less data, but the Docker Desktop/WSL2 disk footprint remains large.

### Explanation

Logical Docker cleanup freed space inside the virtual disk, but the underlying virtual disk was not necessarily compacted.

### Next step

Investigate platform-specific reclamation.

Do not confuse:

```text
free space inside virtual disk
```

with:

```text
smaller physical virtual disk file
```

---

# 20. Real-World Data Engineering Scenarios

## Scenario A — PostgreSQL development lab

### Symptom

Old PostgreSQL containers exist, but the database volume must survive.

### Investigation

```bash
docker ps -a
docker volume ls
docker volume inspect <volume>
```

### Decision

Remove obsolete containers but retain the important volume.

### Verification

Restart/recreate the PostgreSQL container and confirm the database remains.

---

## Scenario B — Kafka development lab

### Symptom

Kafka logs, image versions, and persistent data consume significant space.

### Investigation

```bash
docker system df -v
docker images
docker logs --tail 100 kafka
docker volume ls
```

### Decision

Separate:

```text
logs
images
Kafka persistent state
```

Do not delete Kafka data merely because it is not currently attached.

---

## Scenario C — MinIO

### Symptom

MinIO's persistent volume is large.

### Investigation

Determine whether the objects are test data or valuable datasets.

### Decision

Back up or export important data before deleting the volume.

---

## Scenario D — Compose stack reset

### Requirement

Reset Kafka without destroying PostgreSQL.

### Approach

Use separate Compose projects:

```bash
docker compose -p kafka-lab up -d
docker compose -p postgres-lab up -d
```

Reset only:

```bash
docker compose -p kafka-lab down
docker compose -p kafka-lab up -d
```

If Kafka volumes are intentionally disposable:

```bash
docker compose -p kafka-lab down -v
```

Do not use `-v` unless you explicitly want those project volumes removed.

---

## Scenario E — Laptop almost full

### Symptom

The host has only a few GB remaining.

### Investigation

```text
Host disk
   ↓
Docker system df
   ↓
Images?
Containers?
Volumes?
Build cache?
Logs?
Virtual disk allocation?
```

### Decision

Clean progressively.

### Verification

Measure both:

```text
Docker logical usage
+
host filesystem usage
```

---

## Scenario F — Long-running local Data Engineering lab

Create a weekly policy:

```text
Weekly:
    Inspect
    Clean safe resources
    Review volumes
    Verify backups
    Check logs
    Measure again
```

This is more reliable than waiting for:

```text
disk full
    ↓
emergency cleanup
```

---

# 21. Safe vs Dangerous Operations

| Operation | Risk | Why |
|---|---|---|
| Inspect disk usage | Low | Read-only |
| Inspect volumes | Low | Read-only |
| Remove stopped containers | Low–Medium | Stopped container state disappears |
| Remove dangling images | Low | Usually reclaimable image state |
| Remove unused images | Medium | Images may need to be downloaded again |
| Remove unused networks | Low–Medium | Network resources disappear |
| Remove build cache | Low–Medium | Future builds can be slower |
| Remove volumes | High | Persistent data may be permanently lost |
| Delete/replace Docker virtual disk | Very High | Can destroy substantial Docker state |

The key lesson:

> Not all cleanup operations have the same blast radius.

---

# 22. Common Mistakes

## Mistake 1 — Running `docker system prune` without understanding scope

Why it fails:

You are delegating a storage decision to a broad cleanup command.

Better:

```bash
docker system df
docker system df -v
```

first.

---

## Mistake 2 — Running volume cleanup blindly

Why it fails:

Unused does not mean disposable.

---

## Mistake 3 — "Everything must be deleted"

Why it fails:

You may delete:

- database state;
- object data;
- Kafka state;
- useful images;
- diagnostic containers.

---

## Mistake 4 — Accidentally deleting PostgreSQL data

Cause:

Treating a volume as temporary Docker metadata.

Prevention:

```text
volume = data
```

---

## Mistake 5 — Assuming stopped containers consume zero disk

Stopping changes execution state, not storage ownership.

---

## Mistake 6 — Assuming removing a container removes its volume

Usually false for named volumes.

This separation is a feature of persistent storage.

---

## Mistake 7 — Ignoring log growth

A healthy container can still generate excessive logs.

---

## Mistake 8 — Waiting until the disk is full

Emergency cleanup encourages risky decisions.

Prefer weekly housekeeping.

---

## Mistake 9 — Keeping every image version forever

Historical images have value only when the value exceeds their storage cost.

---

## Mistake 10 — Poor resource names

Names such as:

```text
test1
test2
new-postgres
```

make ownership unclear.

---

## Mistake 11 — No labels

Labels make automation and identification easier.

---

## Mistake 12 — Resetting the entire Docker environment

If one lab is broken, reset that lab.

Do not destroy unrelated projects.

---

## Mistake 13 — Not verifying backups

A backup that has never been restored is an assumption.

---

## Mistake 14 — Confusing Docker usage with host usage

Docker's logical accounting and the host's filesystem accounting measure different layers of the system.

---

## Mistake 15 — Assuming Docker Desktop automatically shrinks its virtual disk

Cleanup may free internal space without shrinking the underlying virtual disk file.

---

# 23. Mental Models

## 23.1 Docker disk model

```text
Docker Disk
│
├── Images
├── Containers
├── Volumes
├── Logs
└── Build Cache
```

---

## 23.2 Safe cleanup model

```text
Inspect
  ↓
Classify
  ↓
Backup
  ↓
Clean
  ↓
Verify
  ↓
Reclaim
```

---

## 23.3 Lifecycle model

```text
Container created
      ↓
Container running
      ↓
Container stopped
      ↓
Container removed
      ↓
Image may still exist
      ↓
Volume may still exist
      ↓
Logs/cache may still exist
```

---

## 23.4 Risk model

```text
Read-only inspection
        ↓
Stopped-container cleanup
        ↓
Image cleanup
        ↓
Network cleanup
        ↓
Build-cache cleanup
        ↓
Volume cleanup
        ↓
Virtual-disk operations
```

As you move downward, the potential blast radius increases.

---

# 24. Command Reference

## Measure

```bash
docker system df
docker system df -v
```

## Containers

```bash
docker ps
docker ps -a
docker rm <container>
docker container prune
```

## Images

```bash
docker images
docker image ls
docker image prune
docker image prune -a
```

## Volumes

```bash
docker volume ls
docker volume inspect <volume>
docker volume rm <volume>
docker volume prune
```

**High risk:** volume deletion can permanently remove persistent data.

## Networks

```bash
docker network ls
docker network prune
```

## Logs

```bash
docker logs <container>
docker logs --tail 100 <container>
docker logs --since 1h <container>
```

## Build cache

```bash
docker builder prune
```

## Broad cleanup

```bash
docker system prune
docker system prune -a
```

Review scope before execution.

## Docker environment

```bash
docker info
```

Use this to understand the Docker installation and storage environment.

## Compose projects

```bash
docker compose -p lab-a up -d
docker compose -p lab-a down
docker compose -p lab-a down -v
```

`down -v` is destructive to project volumes; use it only when intentional.

---

# 25. Practice Questions

## Beginner

1. What does `docker system df` show?
2. Why does stopping a container not necessarily free its storage?
3. What is a Docker volume?
4. What is a dangling image?
5. What is the difference between `docker ps` and `docker ps -a`?
6. Why can a container log consume disk space?
7. Why is a volume different from a container?
8. What is build cache?

---

## Intermediate

1. What is the difference between dangling and unused images?
2. What is the difference between `docker image prune` and `docker image prune -a`?
3. Why is `docker volume prune` dangerous?
4. What does `docker container prune` remove?
5. What does `docker builder prune` remove?
6. Why can removing an image increase future startup time?
7. Why should important PostgreSQL data be backed up before destructive cleanup?
8. Why does log rotation help laptop capacity?
9. How do Docker labels improve housekeeping?
10. Why is `docker system df -v` useful?

---

## Advanced

1. Design a weekly housekeeping strategy for a Data Engineering laptop.
2. How would you reset one Compose project without touching another project's volumes?
3. How would you diagnose a 100 GB Docker footprint?
4. How would you prevent logs from exhausting disk space?
5. Why might Docker cleanup not reduce the physical size of a Docker Desktop virtual disk?
6. How would you distinguish a valuable unused volume from a disposable unused volume?
7. When would retaining multiple versions of an image be justified?
8. Why is a logical PostgreSQL backup preferable to treating live database files as ordinary files?
9. What evidence would you collect before deleting a large volume?
10. How would you design a housekeeping script for a team-shared development machine?

---

## Scenario-Based

### Scenario 1

A laptop has 15 GB free. Docker reports 80 GB of storage.

Explain your investigation sequence.

### Scenario 2

A PostgreSQL volume is 25 GB and currently has no attached container.

Should you delete it?

Explain your reasoning.

### Scenario 3

A Kafka container has produced 20 GB of logs.

What questions do you ask before simply deleting the logs?

### Scenario 4

You need to reset `lab-a`, but `lab-b` contains important PostgreSQL data.

Design the safest reset sequence.

### Scenario 5

`docker system df` falls from 90 GB to 45 GB, but the Docker Desktop virtual disk still appears close to 90 GB.

Explain what happened.

---

# 26. Interview Practice

## Q1. Where does Docker disk usage come from?

### Model answer

Docker disk usage can come from image layers, container writable layers and metadata, persistent volumes, build cache, container logs, and other Docker-managed data. `docker system df` provides the first high-level view.

---

## Q2. What is the difference between a stopped container and a removed container?

### Model answer

A stopped container no longer runs, but its container metadata and writable layer remain. Removing the container deletes that container object. Its image and named volumes can remain independently.

---

## Q3. What is a dangling image?

### Model answer

A dangling image is generally an untagged image state that is no longer associated with a useful tag reference, commonly displayed as `<none>:<none>`. It can arise after image updates or rebuilds.

---

## Q4. Difference between `docker image prune` and `docker image prune -a`?

### Model answer

`docker image prune` targets dangling images under its default semantics. `docker image prune -a` is broader and can remove images that are not currently used by containers. The broader operation can require future image re-pulls.

---

## Q5. Why is `docker volume prune` dangerous?

### Model answer

Volumes contain persistent application state. A volume can be unused by currently running containers while still containing valuable PostgreSQL, MinIO, Kafka, or other data. Removing it can permanently destroy that data.

---

## Q6. How would you safely reset one Docker Compose lab?

### Model answer

Give the project a distinct Compose project name, identify its containers, networks, and volumes, back up important state, then use project-scoped `docker compose down` and recreate the project. Only use `down -v` when its volumes are explicitly disposable or backed up.

---

## Q7. How do you control Docker log growth?

### Model answer

First identify why the application is producing logs. Then configure an appropriate Docker logging driver and retention policy, such as `json-file` with `max-size` and `max-file` where appropriate. In larger environments, centralized logging may be preferable.

---

## Q8. Why can Docker cleanup leave the host virtual disk large?

### Model answer

Docker cleanup can free storage internally without automatically shrinking the underlying virtual disk allocation. Docker Desktop and WSL2 can use virtual disks whose physical file size does not immediately contract when internal blocks become free.

---

## Q9. What is your cleanup philosophy?

### Model answer

Measure first, classify resources, back up important state, remove the least destructive resources first, verify the result, and only then consider more aggressive or platform-level reclamation.

---

## Q10. What makes a housekeeping script safe?

### Model answer

It should be explicit, defensive, reviewable, project-aware where possible, conservative around volumes, confirmation-driven for destructive actions, and able to show before-and-after storage state.

---

# 27. Final Knowledge Check

You should be able to say:

```text
[ ] I can explain where Docker disk space goes.
[ ] I can use docker system df confidently.
[ ] I can use docker system df -v for detailed investigation.
[ ] I can inspect images, containers, volumes, and networks.
[ ] I understand dangling vs unused images.
[ ] I understand every major prune command.
[ ] I know why volume pruning is dangerous.
[ ] I can back up important persistent data before cleanup.
[ ] I understand the difference between filesystem copies and database-aware backups.
[ ] I understand container log growth.
[ ] I can configure log size limits and rotation.
[ ] I can identify lab resources through names and labels.
[ ] I can perform a safe weekly housekeeping routine.
[ ] I can reset one lab without destroying another lab.
[ ] I understand Docker storage on Linux.
[ ] I understand Docker Desktop/WSL2 storage at a conceptual level.
[ ] I understand Docker Desktop/macOS virtual-disk storage at a conceptual level.
[ ] I understand logical Docker cleanup vs virtual-disk reclamation.
[ ] I can write a safe housekeeping script.
[ ] I can diagnose a Docker disk-space incident.
```

---

# 28. Topic Completion Checklist

## Foundations

- [ ] I understand why Docker consumes disk space.
- [ ] I can distinguish stopping, removing, and pruning.
- [ ] I understand images, containers, volumes, logs, and build cache.

## Measurement

- [ ] I can use `docker system df`.
- [ ] I can use `docker system df -v`.
- [ ] I can compare before/after cleanup.

## Cleanup

- [ ] I can remove stopped containers deliberately.
- [ ] I understand dangling images.
- [ ] I understand unused images.
- [ ] I understand all major prune commands.
- [ ] I know the risks of broad cleanup.

## Persistent Data

- [ ] I treat volumes as application state.
- [ ] I can inspect volumes.
- [ ] I can determine whether a volume matters.
- [ ] I can back up PostgreSQL data.
- [ ] I understand that raw filesystem copies are not automatically database-consistent backups.

## Logs

- [ ] I can inspect container logs.
- [ ] I understand unbounded log growth.
- [ ] I can configure log size limits and rotation.

## Housekeeping

- [ ] I use meaningful names.
- [ ] I understand Docker labels.
- [ ] I can perform weekly housekeeping.
- [ ] I can reset one lab safely.
- [ ] I can avoid affecting another lab.

## Automation

- [ ] I understand `housekeeping.sh`.
- [ ] I can explain `set -euo pipefail`.
- [ ] I can make destructive operations confirmation-driven.
- [ ] I do not automate blind volume deletion.

## Platform Awareness

- [ ] I understand Docker data-root concepts on Linux.
- [ ] I understand Docker Desktop/WSL2 virtual storage.
- [ ] I understand Docker Desktop/macOS virtual storage.
- [ ] I know that logical cleanup and physical disk reclamation are different.

---

# 29. Roadmap Coverage Audit

This module intentionally covers every Topic 09 requirement:

| Roadmap concept | Covered |
|---|---|
| `docker system df` | Yes |
| Images disk usage | Yes |
| Containers disk usage | Yes |
| Volumes disk usage | Yes |
| Build-cache disk usage | Yes |
| Stopped-container removal | Yes |
| Unused-image removal | Yes |
| Docker prune commands | Yes |
| Exact prune semantics | Yes |
| Container pruning | Yes |
| Dangling image pruning | Yes |
| Unused image pruning | Yes |
| Network pruning | Yes |
| Build-cache pruning | Yes |
| Volume pruning and danger | Yes |
| Dangling vs unused images | Yes |
| Old image versions | Yes |
| Container log growth | Yes |
| Log size limits | Yes |
| Log rotation | Yes |
| Naming and labels | Yes |
| Weekly housekeeping | Yes |
| Safe single-lab reset | Yes |
| Cross-lab volume protection | Yes |
| Docker storage locations | Yes |
| Docker Desktop/WSL2 reclamation | Yes |
| Topic 10 relationship | Yes |
| Backup before cleanup | Yes |
| Topic 04 relationship | Yes |
| `housekeeping.sh` | Yes |
| `docker_lab/09/` exercises | Yes |
| Break/fix exercises | Yes |
| Real-world Data Engineering scenarios | Yes |
| Safe vs dangerous operations | Yes |
| Mental models | Yes |
| Command reference | Yes |
| Practice questions | Yes |
| Interview practice | Yes |
| Final knowledge check | Yes |

---

# 30. Scope Boundary

This topic is part of:

```text
Stage 2B
→ Gap Module G1
→ Docker Essentials for Data Labs
→ Phase D — Keeping Your Machine Healthy
→ Topic 09 — Cleanup, Disk Usage, and Housekeeping
```

It is an **operator/user-level Docker module**.

It does not attempt to become a complete course on:

- Dockerfile authoring;
- image building;
- multi-stage builds;
- CI/CD image pipelines;
- Kubernetes;
- container orchestration;
- centralized enterprise logging;
- advanced Docker internals.

Those topics belong elsewhere in the roadmap.

Topic 09 only introduces enough surrounding concepts to make disk management and housekeeping safe and understandable.

---

# 31. Professional Takeaway

The most important skill in Docker housekeeping is not memorizing:

```bash
docker system prune
```

It is learning to reason about ownership, persistence, risk, and evidence.

A production-minded Data Engineer thinks like this:

```text
Disk is filling
      ↓
Measure
      ↓
Find the category
      ↓
Find the specific resource
      ↓
Determine ownership
      ↓
Determine data importance
      ↓
Back up if necessary
      ↓
Choose the smallest safe cleanup
      ↓
Verify
      ↓
Measure again
      ↓
Reclaim platform storage only when justified
```

Remember the ten operational principles:

1. **Measure before deleting.**
2. **Stopped does not mean unnecessary.**
3. **Unused does not automatically mean disposable.**
4. **Volumes contain state; treat them as data.**
5. **Back up important state before destructive cleanup.**
6. **Use naming and labels to make resources identifiable.**
7. **Prefer scoped cleanup over global cleanup.**
8. **Clean progressively from least destructive to most destructive.**
9. **Measure after cleanup.**
10. **Docker cleanup and virtual-disk reclamation are separate concepts.**

If you can apply those principles consistently, you can keep a Docker-based Data Engineering lab healthy for months instead of repeatedly reaching a full disk and performing emergency cleanup.
