# Running Databases and Services in Containers

> **Gap Module G1 — Docker Essentials for Data Labs | Topic 02**
>
> A beginner-to-advanced, production-oriented guide to running, validating, connecting to, and operating containerized Data Engineering services.

---

## 1. Learning Objectives

By the end of this module, you should be able to:

- Explain what a containerized data service is.
- Distinguish a container, application process, database server, client, and data.
- Explain why **container started** does not necessarily mean **service ready**.
- Run PostgreSQL in a container.
- Understand PostgreSQL startup variables, default user, default database, and data directory.
- Connect to PostgreSQL with `psql` and Python.
- Validate PostgreSQL readiness with `pg_isready`.
- Run MinIO as local object storage.
- Distinguish the MinIO S3-compatible API from its browser console.
- Create and use a bucket.
- Connect to MinIO with `mc` and Python/boto3.
- Run Redis as a local key-value service.
- Perform basic Redis operations.
- Explain Kafka's broker/topic/producer/consumer model.
- Explain Kafka KRaft mode and a single-node learning topology.
- Understand Kafka node IDs and listeners at an introductory level.
- Create, produce to, and consume from a Kafka topic.
- Validate service readiness rather than merely checking container state.
- Understand initialization hooks and PostgreSQL first-start behavior.
- Explain why initialization scripts do not normally rerun on every restart.
- Select service versions deliberately and match PostgreSQL major versions with target environments.
- Use one-off client containers for tools such as `psql` and `mc`.
- Reason about service dependencies and the difference between ordering and readiness.
- Prefer local-only exposure for services that only need to be accessed from the developer machine.
- Measure startup-to-ready time.
- Build a reusable service card for each data service.
- Apply professional operational reasoning to a local Data Engineering platform.

### The central question

Do not finish this module thinking only:

> "I know the Docker command."

Finish it thinking:

> **"I know what service I am running, which image/version it uses, what it requires, how it initializes, when it is actually ready, how to verify it, how a client connects to it, and what other services depend on it."**

---

# 2. Scope Boundary

This module is **Topic 02** of G1 — Docker Essentials for Data Labs.

The purpose is to learn:

> **How to run and understand containerized data services.**

It is intentionally not a complete Docker course.

## Detailed topics deferred to later modules

| Later topic | Boundary |
|---|---|
| Topic 03 — Ports, Networks, and Service Discovery | Full Docker networking, DNS, service discovery, network design, and advanced listener troubleshooting |
| Topic 04 — Volumes, Bind Mounts, and Data Persistence | Complete persistence and storage curriculum |
| Topic 05 — Environment Variables and Configuration | Configuration architecture, secrets, `.env`, and secure configuration patterns |
| Topic 06 — Logs, Exec, and Troubleshooting | Systematic troubleshooting methodology and detailed log analysis |
| Topic 07 — Docker Compose | Compose authoring and multi-service stack management |
| Topic 08 — Resource Limits | CPU, memory, and resource-control curriculum |
| Topic 09 — Cleanup | Systematic image/container/volume cleanup |
| Topic 10 — Docker Desktop / WSL2 / Platform Differences | Platform-specific operational differences |

These concepts are mentioned only where they are necessary to understand a service.

For example:

- PostgreSQL persistence is mentioned, but the complete volume curriculum is not taught.
- Networking is introduced, but Topic 03 owns the detailed networking curriculum.
- Environment variables are demonstrated because service images require them, but Topic 05 owns configuration and secret management.
- Readiness and basic health inspection are taught because they are fundamental to operating services, but Topic 06 owns systematic troubleshooting.
- A multi-service dependency is discussed conceptually, but Topic 07 owns Compose orchestration.

---

# 3. Connection to Topic 01

Topic 01 established the foundation:

```text
Containers + Images + Registries
              ↓
          Topic 02
              ↓
    Real Data Engineering Services
```

From Topic 01, you should already understand:

- image;
- container;
- `docker pull`;
- `docker run`;
- container lifecycle;
- tags;
- digests;
- image architecture.

Now we apply those concepts to real infrastructure:

```text
PostgreSQL
MinIO
Redis
Kafka
```

The progression is:

```text
Image
  ↓
Container
  ↓
Service process
  ↓
Ready service
  ↓
Client
  ↓
Data Engineering workload
```

The key change is that we are no longer treating containers as generic examples.

We are operating **actual data-platform infrastructure**.

---

# 4. What Is a Containerized Data Service?

Start with the simplest model.

Suppose you want PostgreSQL.

Without containers, you install PostgreSQL directly on your machine.

With containers:

```text
PostgreSQL image
       ↓
PostgreSQL container
       ↓
PostgreSQL server process
       ↓
Client
```

The same idea applies to other services:

```text
MinIO image
    ↓
MinIO container
    ↓
Object-storage server
    ↓
Python / mc / browser

Redis image
    ↓
Redis container
    ↓
Redis server
    ↓
Redis client

Kafka image
    ↓
Kafka container
    ↓
Kafka broker
    ↓
Producer / Consumer
```

## 4.1 Container

The container is the runtime environment and lifecycle object managed by Docker.

It gives the service process an isolated execution environment.

## 4.2 Application process

The actual program doing the work.

Examples:

- PostgreSQL server process;
- MinIO server;
- Redis server;
- Kafka broker.

## 4.3 Database/server

The service that listens for client requests.

For PostgreSQL:

```text
PostgreSQL server
    ↓
accept connection
    ↓
execute SQL
    ↓
return result
```

## 4.4 Client

A client is a program that talks to the server.

Examples:

```text
psql → PostgreSQL
Python/psycopg → PostgreSQL
boto3 → MinIO
mc → MinIO
redis-cli → Redis
Kafka producer → Kafka
Kafka consumer → Kafka
```

## 4.5 Data

Data is the state managed by the service.

Examples:

- PostgreSQL rows and indexes;
- MinIO objects;
- Redis keys;
- Kafka records.

A useful mental model is:

```text
Container
    contains/runs
Service process
    manages
Data
    accessed by
Client
```

The service process and its data are not the same thing.

---

# 5. The Most Important Concept: Started vs Ready

One of the most common beginner mistakes is assuming:

```bash
docker ps
```

showing:

```text
Up 5 seconds
```

means the application is ready.

It does not necessarily mean that.

## 5.1 The lifecycle

A database may progress through:

```text
Container created
      ↓
Container started
      ↓
Service process starts
      ↓
Configuration loaded
      ↓
Internal initialization
      ↓
Database/storage structures become available
      ↓
Network endpoint begins accepting requests
      ↓
READY
```

Therefore:

```text
Container Started
        ≠
Service Ready
```

## 5.2 PostgreSQL example

Immediately after starting PostgreSQL:

```text
Docker
  ↓
container starts
  ↓
postgres process starts
  ↓
database checks/initializes state
  ↓
PostgreSQL accepts connections
```

If a Python ingestion job connects during the middle of this sequence, the connection can fail even though:

```bash
docker ps
```

already reports the container as running.

## 5.3 Why this matters in Data Engineering

Consider:

```text
Pipeline starts
     ↓
PostgreSQL container starts
     ↓
Pipeline immediately connects
     ↓
Connection refused
```

The problem may not be:

> "PostgreSQL is broken."

The problem may be:

> "The pipeline raced the database startup."

Professional systems reason about **readiness**, not merely process existence.

---

# 6. Four Useful Service States

For operational reasoning, distinguish:

```text
1. Container exists
2. Container is running
3. Service process is running
4. Service is ready for client requests
```

For a database:

```text
Container exists
       ↓
Container running
       ↓
PostgreSQL process running
       ↓
PostgreSQL accepting connections
       ↓
READY
```

For Kafka:

```text
Container exists
       ↓
Kafka process starts
       ↓
KRaft metadata/controller initialization
       ↓
Broker becomes operational
       ↓
Clients can perform expected operations
       ↓
READY
```

This distinction becomes critical when multiple services depend on one another.

---

# 7. PostgreSQL in a Container

## 7.1 What is PostgreSQL?

PostgreSQL is a relational database management system.

At a high level:

```text
Client
  ↓
PostgreSQL server
  ↓
SQL
  ↓
Database
  ↓
Schema
  ↓
Tables
  ↓
Rows
```

The client/server model is what matters for this module.

You do not need to learn advanced database design here.

Your objective is:

> **Operate PostgreSQL as a containerized Data Engineering dependency.**

---

# 8. PostgreSQL Image Selection

Select a deliberate major version.

For example:

```bash
docker pull postgres:16
```

The reference:

```text
postgres:16
│       │
│       └── tag / major version
└──────── repository
```

## Why version selection matters

Suppose the target environment runs PostgreSQL 16.

A local lab using a completely different major release can introduce compatibility differences.

A useful engineering principle is:

> **When compatibility matters, align the local major version with the target environment.**

Do not blindly use:

```bash
postgres:latest
```

for a production-like learning environment.

A deliberate version makes the lab easier to reason about and reproduce.

---

# 9. PostgreSQL Required Configuration

The official PostgreSQL image uses environment variables for important initial configuration.

The core variables in this module are:

```text
POSTGRES_PASSWORD
POSTGRES_USER
POSTGRES_DB
```

## 9.1 `POSTGRES_PASSWORD`

Defines the password for the initialized PostgreSQL user.

## 9.2 `POSTGRES_USER`

Defines the user created during initial database setup.

## 9.3 `POSTGRES_DB`

Defines the initial database created for the initialized user.

These variables are especially important on first initialization.

---

# 10. Running PostgreSQL

For a disposable local lab:

```bash
docker run -d \
  --name pg-lab \
  -e POSTGRES_USER=dataeng \
  -e POSTGRES_PASSWORD=localdevpassword \
  -e POSTGRES_DB=datalab \
  -p 127.0.0.1:5432:5432 \
  postgres:16
```

> **Scope note:** The `-p` option is used here only to make the service reachable from a host-side client. Full Docker networking and port architecture belong to Topic 03.

## Line-by-line explanation

### `docker run`

Create and start a new container.

### `-d`

Run it in detached mode.

### `--name pg-lab`

Give the container a predictable name.

### `-e POSTGRES_USER=dataeng`

Configure the initial PostgreSQL user.

### `-e POSTGRES_PASSWORD=localdevpassword`

Configure the local lab password.

### `-e POSTGRES_DB=datalab`

Configure the initial database.

### `-p 127.0.0.1:5432:5432`

Make PostgreSQL available only through the local machine's loopback interface.

Conceptually:

```text
Host localhost:5432
        ↓
Container PostgreSQL:5432
```

### `postgres:16`

Use PostgreSQL major version 16.

## Local credential warning

`localdevpassword` is intentionally simple for a disposable learning environment.

Do **not** treat this as a production secret-management pattern.

Production secrets management belongs to Topic 05.

---

# 11. PostgreSQL Default User and Database

The exact initialization behavior depends on the image configuration and values supplied at startup.

With:

```bash
-e POSTGRES_USER=dataeng
-e POSTGRES_DB=datalab
```

you are explicitly asking the image's initialization process to establish:

```text
User:
dataeng

Database:
datalab
```

If `POSTGRES_USER` is omitted, the official PostgreSQL image commonly uses its documented default user behavior.

The important professional habit is:

> **Do not guess image-specific defaults. Read the image documentation and make important lab configuration explicit.**

---

# 12. PostgreSQL Data Directory

PostgreSQL needs a data directory containing its database cluster state.

Conceptually:

```text
PostgreSQL server
       ↓
PostgreSQL data directory
       ↓
Database cluster
       ↓
Databases / tables / indexes / metadata
```

The official image uses its documented PostgreSQL data directory.

For the official PostgreSQL image, the standard location is:

```text
/var/lib/postgresql/data
```

## Why it matters

If the container is disposable and no persistent storage is configured:

```text
Container removed
      ↓
Container-specific writable state removed
      ↓
Database state may be lost
```

The complete volume/persistence curriculum is Topic 04.

For this topic, remember:

> **A database container is not automatically a durable database platform.**

---

# 13. PostgreSQL Initialization

On first initialization, the image performs database setup.

Conceptually:

```text
Container starts
      ↓
Data directory is empty/uninitialized
      ↓
PostgreSQL initialization
      ↓
Initial user/database configuration
      ↓
Initialization scripts
      ↓
PostgreSQL ready
```

This first-start behavior is central to understanding PostgreSQL containers.

If the data directory already contains an initialized PostgreSQL cluster, the image does not simply recreate the database from scratch every time the container starts.

---

# 14. Connecting with `psql`

`psql` is a PostgreSQL client.

The relationship is:

```text
psql client
    ↓
PostgreSQL server
    ↓
database
```

Example:

```bash
psql -h localhost -p 5432 -U dataeng -d datalab
```

## Explain every argument

### `-h localhost`

Connect to the host machine.

### `-p 5432`

Use PostgreSQL's standard port.

### `-U dataeng`

Authenticate as the `dataeng` user.

### `-d datalab`

Connect to the `datalab` database.

---

# 15. Basic `psql` Validation

Once connected:

```sql
SELECT version();
```

This verifies that PostgreSQL is responding.

Then:

```sql
SELECT current_database();
```

This verifies the active database.

You can also inspect the current user:

```sql
SELECT current_user;
```

Expected conceptual result:

```text
database: datalab
user:     dataeng
server:   PostgreSQL 16.x
```

---

# 16. Simple PostgreSQL Data Test

Create a table:

```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT
);
```

Insert rows:

```sql
INSERT INTO customers (id, name)
VALUES
    (1, 'Alice'),
    (2, 'Bob');
```

Query:

```sql
SELECT * FROM customers;
```

Expected result:

```text
 id | name
----+-------
  1 | Alice
  2 | Bob
```

This is intentionally simple.

The purpose is to prove:

```text
Container
  ↓
PostgreSQL
  ↓
Connection
  ↓
SQL
  ↓
Stored data
```

---

# 17. Connecting from Python

A Data Engineer will often access PostgreSQL from Python rather than manually through `psql`.

Install the client library in your Python environment:

```bash
pip install "psycopg[binary]"
```

Then:

```python
import psycopg

conn = psycopg.connect(
    "host=localhost "
    "port=5432 "
    "dbname=datalab "
    "user=dataeng "
    "password=localdevpassword"
)

with conn.cursor() as cur:
    cur.execute("SELECT current_database(), version()")
    print(cur.fetchone())

conn.close()
```

The flow is:

```text
Python
  ↓
psycopg
  ↓
TCP connection
  ↓
PostgreSQL
  ↓
SQL
  ↓
Result
```

This same pattern appears in:

- ingestion jobs;
- ETL/ELT pipelines;
- validation scripts;
- data-quality checks;
- application services.

---

# 18. PostgreSQL Readiness with `pg_isready`

A dedicated readiness utility is:

```bash
pg_isready
```

From a host where the utility is installed:

```bash
pg_isready -h localhost -p 5432
```

A successful result indicates that PostgreSQL is accepting the type of connection being tested.

The important mental model is:

```text
docker ps
    ↓
"container is running"

pg_isready
    ↓
"PostgreSQL is accepting connections"
```

Those are different questions.

---

# 19. PostgreSQL Readiness Loop

A simple Python readiness loop:

```python
import subprocess
import time

for attempt in range(30):
    result = subprocess.run(
        ["pg_isready", "-h", "localhost", "-p", "5432"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("PostgreSQL is ready")
        break

    print(f"Waiting for PostgreSQL... attempt {attempt + 1}")
    time.sleep(1)
else:
    raise RuntimeError("PostgreSQL did not become ready")
```

The pattern is more important than the exact implementation:

```text
Check
  ↓
Not ready?
  ↓ yes
Wait
  ↓
Check again
  ↓
Ready?
  ↓ yes
Continue
```

This is much safer than:

```text
sleep(10)
```

because fixed sleeps guess how long startup will take.

---

# 20. Health Checks and `docker inspect`

Container health is different from simple container state.

A Docker image or container can have a health check defined.

When a health check exists, inspect the container:

```bash
docker inspect pg-lab
```

Look for health information under the container state, conceptually:

```text
State
 ├── Status
 ├── Running
 └── Health
      ├── Status
      ├── FailingStreak
      └── Log
```

A health status might be:

```text
starting
healthy
unhealthy
```

Not every image defines a useful health check.

Therefore:

> **No health status does not automatically mean the service is broken.**

The application-specific readiness mechanism may be more authoritative.

---

# 21. MinIO in a Container

## 21.1 What is MinIO?

MinIO is an object-storage server with an S3-compatible API.

A useful model:

```text
Object Storage
     ↓
Bucket
     ↓
Object
```

For example:

```text
Bucket: data-lab

Objects:
  raw/customers.csv
  raw/orders.json
  curated/sales.parquet
```

MinIO is particularly useful in local Data Engineering labs because it provides object storage without requiring a cloud account.

---

# 22. Why Object Storage Matters

Many modern data platforms use object storage as a fundamental storage layer.

Examples:

```text
S3
Azure Blob Storage
Google Cloud Storage
MinIO
```

A local MinIO service lets you practice concepts such as:

- buckets;
- objects;
- object keys;
- S3-compatible APIs;
- data-lake style layouts.

Later Stage 2 work can use MinIO as a local stand-in for cloud object storage.

---

# 23. MinIO API vs Web Console

This distinction is essential.

MinIO exposes different interfaces for different users.

```text
                 MinIO
                /     \
               /       \
              ↓         ↓
          API endpoint   Console
              ↓            ↓
       Python / boto3     Browser
       S3 clients         Human UI
```

The API is for programmatic access.

The console is for human administration and observation through a web interface.

Do not confuse:

```text
S3 API endpoint
```

with:

```text
Web console endpoint
```

A Python S3 client should talk to the API endpoint.

---

# 24. MinIO Ports

The exact image/version command should be taken from the current image documentation.

Conceptually, a typical MinIO local lab exposes:

```text
9000 → S3-compatible API
9001 → Web console
```

A common local-only mapping is:

```text
127.0.0.1:9000 → MinIO API
127.0.0.1:9001 → MinIO console
```

The critical mental model is:

```text
localhost:9000
    ↓
programmatic object-storage API

localhost:9001
    ↓
browser-based console
```

Always verify the current image documentation before copying a service command into a lab.

---

# 25. MinIO Root Credentials

Modern MinIO deployments commonly use root credentials during server initialization.

The exact variable names and command-line conventions depend on the image/version documentation.

A common conceptual configuration is:

```text
MINIO_ROOT_USER
MINIO_ROOT_PASSWORD
```

For a disposable local lab:

```text
root-user:     minioadmin
root-password: minioadminpassword
```

These are **local learning credentials only**.

Never reuse them in a production system.

---

# 26. Running MinIO

A typical local-only learning setup can be represented as:

```bash
docker run -d \
  --name minio-lab \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadminpassword \
  -p 127.0.0.1:9000:9000 \
  -p 127.0.0.1:9001:9001 \
  minio/minio server /data --console-address ":9001"
```

### Important

The exact MinIO image and startup command can evolve.

Before running it in a real lab, verify the current image documentation.

The conceptual configuration is:

```text
MinIO server
     ↓
data directory
     ↓
API endpoint
     ↓
console endpoint
```

---

# 27. Creating a MinIO Bucket

A bucket is the top-level logical namespace for objects.

Conceptually:

```text
MinIO
  ↓
Bucket
  ↓
Object
```

Example bucket:

```text
data-lab
```

Then:

```text
data-lab/
├── raw/
├── staging/
└── curated/
```

These are object-key prefixes, not necessarily traditional directories.

---

# 28. Creating a Bucket Through the Console

Open the MinIO console in a browser using the documented console address.

For the common local mapping:

```text
http://127.0.0.1:9001
```

Sign in using the local lab credentials.

Create:

```text
data-lab
```

Then upload a small file.

This gives you a complete validation chain:

```text
Container
  ↓
MinIO server
  ↓
Console
  ↓
Bucket
  ↓
Object
```

---

# 29. MinIO Client (`mc`)

`mc` is the MinIO command-line client.

Conceptually:

```text
mc
 ↓
MinIO API
 ↓
Bucket/object operations
```

A typical workflow is:

```bash
mc alias set local http://127.0.0.1:9000 minioadmin minioadminpassword
```

Then:

```bash
mc mb local/data-lab
```

List buckets:

```bash
mc ls local
```

Upload a file:

```bash
mc cp sample.csv local/data-lab/
```

List objects:

```bash
mc ls local/data-lab/
```

The exact CLI behavior should be checked against the installed `mc` version.

---

# 30. MinIO with Python and boto3

The S3-compatible API is especially useful to Data Engineers.

Install:

```bash
pip install boto3
```

Create a client:

```python
import boto3

client = boto3.client(
    "s3",
    endpoint_url="http://127.0.0.1:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadminpassword",
    region_name="us-east-1",
)
```

Create a bucket:

```python
client.create_bucket(Bucket="data-lab")
```

Upload a file:

```python
client.upload_file(
    "sample.csv",
    "data-lab",
    "raw/sample.csv",
)
```

List objects:

```python
response = client.list_objects_v2(Bucket="data-lab")

for obj in response.get("Contents", []):
    print(obj["Key"])
```

The important point is:

```text
Python
  ↓
boto3
  ↓
S3-compatible API
  ↓
MinIO
  ↓
Bucket
  ↓
Object
```

This becomes useful later with:

- Spark;
- DuckDB;
- Polars;
- lakehouse exercises;
- ingestion pipelines.

---

# 31. Redis in a Container

## 31.1 What is Redis?

Redis is commonly used as a high-speed key-value data store.

The simplest model is:

```text
Key → Value
```

For example:

```text
"user:1001" → "Sovon"
```

or:

```text
"pipeline:last_run" → "2026-10-06T15:30:00"
```

Redis is commonly used for:

- caching;
- temporary state;
- counters;
- session-like state;
- fast lookups.

This module does not teach advanced Redis architecture.

---

# 32. Running Redis

A simple learning container:

```bash
docker run -d \
  --name redis-lab \
  -p 127.0.0.1:6379:6379 \
  redis:7
```

Check:

```bash
docker ps
```

Then connect using Redis CLI if available:

```bash
redis-cli -h 127.0.0.1 -p 6379
```

---

# 33. Basic Redis Operations

Set a value:

```text
SET name "Data Engineer"
```

Retrieve it:

```text
GET name
```

Expected:

```text
"Data Engineer"
```

Set another value:

```text
SET pipeline:last_status "success"
```

Retrieve:

```text
GET pipeline:last_status
```

The mental model is:

```text
SET key value
      ↓
Redis stores key/value
      ↓
GET key
      ↓
value
```

---

# 34. Kafka in KRaft Mode

Kafka requires a different mental model from PostgreSQL and Redis.

PostgreSQL:

```text
Client
  ↓
Database
```

Redis:

```text
Client
  ↓
Key-value service
```

Kafka:

```text
Producer
    ↓
  Broker
    ↓
  Topic
    ↓
Consumer
```

Kafka is an event-streaming platform.

---

# 35. Kafka Fundamentals

## Broker

A Kafka broker is a Kafka server responsible for receiving, storing, and serving records.

## Topic

A named stream/category of records.

Example:

```text
orders
```

## Producer

Writes records to Kafka.

```text
Producer
   ↓
Topic
```

## Consumer

Reads records from Kafka.

```text
Topic
   ↓
Consumer
```

## Partition

A topic can be divided into partitions for scalable storage and processing.

For this module, understand the concept without going deep into partition assignment or consumer-group internals.

---

# 36. What Is KRaft?

Historically, Kafka deployments commonly used ZooKeeper for cluster metadata and coordination.

Kafka's KRaft mode uses Kafka itself for this metadata management.

Conceptually:

```text
Older architecture
Kafka
  ↕
ZooKeeper

KRaft architecture
Kafka
  ↓
Kafka metadata/controller quorum
```

KRaft simplifies the architecture by removing the separate ZooKeeper dependency.

For this learning module, the important concept is:

> **A Kafka KRaft deployment can run its controller and broker roles without ZooKeeper.**

---

# 37. Single-Node Kafka for Learning

A single-node Kafka environment is useful for local development.

Conceptually:

```text
┌──────────────────────────┐
│ Kafka Node               │
│                          │
│ Broker role              │
│ Controller role         │
│ KRaft metadata           │
└──────────────────────────┘
```

This is not equivalent to a production multi-node Kafka cluster.

It is a learning environment.

A single node cannot provide the same fault tolerance or scalability characteristics as a properly designed production cluster.

---

# 38. Kafka Node ID

A Kafka node needs an identity.

Conceptually:

```text
Kafka cluster
      ↓
Kafka node
      ↓
Node ID
```

For a single-node learning system, you may use:

```text
node.id=1
```

The node ID identifies the Kafka server within the Kafka cluster topology.

It becomes more important as the cluster grows beyond one node.

---

# 39. Kafka Roles

In a KRaft setup, a node can have broker and controller roles.

Conceptually:

```text
Kafka node
 ├── broker
 └── controller
```

For a single-node learning environment, one node can perform both roles.

This is convenient for local learning but is intentionally simpler than production cluster architecture.

---

# 40. Kafka Listeners — Introductory Mental Model

Kafka networking is more subtle than a simple database connection.

A listener represents an endpoint where Kafka accepts connections.

Conceptually:

```text
listener
   ↓
protocol + address + port
```

For example:

```text
HOST:9092
```

But Kafka also needs clients to know **what address they should use to reach the broker**.

This is why Kafka configuration often involves concepts such as:

- listeners;
- advertised listeners;
- internal client endpoint;
- external client endpoint.

A simplified model is:

```text
Container client
       ↓
Internal listener

Host client
       ↓
External listener
```

### Scope boundary

This module introduces the concepts only.

Full Kafka listener/network troubleshooting belongs primarily to Topic 03.

---

# 41. A Typical Single-Node Kafka Configuration

The exact environment variables depend on the chosen Kafka image.

Do not blindly copy a configuration between Kafka images.

A generic KRaft configuration conceptually requires values corresponding to:

```text
process roles
node ID
controller quorum voters
listeners
advertised listeners
broker listener
controller listener
```

The important lesson is:

> **Kafka images are not interchangeable configuration interfaces.**

Always read the documentation for the specific image/version you selected.

---

# 42. Produce and Consume a Kafka Message

Once Kafka is ready, create a topic.

A typical Kafka CLI workflow is conceptually:

```bash
kafka-topics.sh \
  --bootstrap-server <broker-endpoint> \
  --create \
  --topic orders \
  --partitions 1 \
  --replication-factor 1
```

Describe the topic:

```bash
kafka-topics.sh \
  --bootstrap-server <broker-endpoint> \
  --describe \
  --topic orders
```

Start a producer:

```bash
kafka-console-producer.sh \
  --bootstrap-server <broker-endpoint> \
  --topic orders
```

Enter:

```text
order-001
```

Start a consumer:

```bash
kafka-console-consumer.sh \
  --bootstrap-server <broker-endpoint> \
  --topic orders \
  --from-beginning
```

The conceptual flow:

```text
Console producer
      ↓
orders topic
      ↓
Kafka broker
      ↓
Console consumer
```

The exact command paths vary by image. Use the commands supplied by the selected Kafka distribution/image.

---

# 43. Kafka Readiness

A running Kafka container does not automatically mean Kafka is ready for the operation you want to perform.

You may observe:

```text
Container: Up
```

while Kafka is still:

```text
initializing metadata
starting controller
starting broker
loading configuration
opening listeners
```

Therefore:

```text
Kafka container running
       ≠
Kafka ready
```

Readiness should be tested with an application-aware check.

For example, a useful validation is whether the broker responds to an administrative operation:

```bash
kafka-topics.sh \
  --bootstrap-server <broker-endpoint> \
  --list
```

If the command can communicate successfully with the broker, that is stronger evidence than simply observing `docker ps`.

---

# 44. Service Readiness Patterns

Different services have different readiness mechanisms.

| Service | Useful readiness/validation mechanism |
|---|---|
| PostgreSQL | `pg_isready`, connection/query |
| MinIO | API request/health endpoint or client operation |
| Redis | Redis ping/CLI operation |
| Kafka | Kafka CLI/API operation against the broker |
| Container | `docker ps` / container state |

The principle is:

> **Prefer a service-specific readiness test over a generic container-state test.**

---

# 45. Health Endpoints

Some services expose health endpoints.

Conceptually:

```text
HTTP health endpoint
        ↓
service health state
```

For example:

```text
GET /health
```

may return a success response when the service is ready.

Do not assume every image exposes the same endpoint.

Read the selected image/service documentation.

---

# 46. Docker Health Status

If an image defines a Docker health check, inspect:

```bash
docker inspect <container-name>
```

Look under the state information.

Conceptually:

```text
Status: running

Health:
    Status: healthy
```

Possible states include:

```text
starting
healthy
unhealthy
```

A health check is useful because it can turn an application-specific condition into container metadata.

But remember:

> **Health-check availability depends on the image/configuration.**

No health check does not automatically mean no readiness mechanism exists.

---

# 47. Initialization Hooks

Initialization hooks answer the question:

> "What should happen automatically the first time this service gets initialized?"

A general database initialization sequence is:

```text
Container starts
       ↓
Data directory checked
       ↓
Empty/uninitialized?
       ↓ yes
Initial database setup
       ↓
Initialization scripts
       ↓
Service ready
```

Initialization is different from ordinary startup.

---

# 48. PostgreSQL Initialization SQL Scripts

The official PostgreSQL image supports initialization scripts in its documented initialization directory.

The standard location is:

```text
/docker-entrypoint-initdb.d/
```

Suppose you have:

```text
init.sql
```

containing:

```sql
CREATE TABLE pipeline_runs (
    run_id SERIAL PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    status TEXT NOT NULL
);
```

The conceptual startup arrangement is:

```text
PostgreSQL container
       ↓
first initialization
       ↓
/docker-entrypoint-initdb.d/init.sql
       ↓
CREATE TABLE pipeline_runs
```

---

# 49. Why Initialization Scripts Do Not Run on Every Restart

This is critical.

Consider:

```text
First start
    ↓
Empty PostgreSQL data directory
    ↓
Initialize database
    ↓
Run init SQL
    ↓
Database ready
```

Then:

```text
docker restart pg-lab
    ↓
Existing PostgreSQL data directory
    ↓
Existing database cluster
    ↓
Normal startup
```

The initialization script is not intended to behave like:

```text
"Run this SQL every time PostgreSQL starts."
```

It is closer to:

> **"Run this setup when initializing a new database cluster."**

That is why changing an initialization script after the database has already been initialized may appear to have no effect.

---

# 50. Initialization and Data State

This concept connects directly to persistence.

Suppose:

```text
PostgreSQL data directory
        ↓
contains initialized database
```

Restarting the container keeps that existing database state.

If you create a completely fresh database state, the initialization process can occur again.

Conceptually:

```text
Existing state
    ↓
restart
    ↓
reuse state

Fresh state
    ↓
initialization
    ↓
init scripts
```

Topic 04 will teach the storage mechanics in depth.

For Topic 02, the key lesson is:

> **Initialization is tied to initial database state, not ordinary container restart.**

---

# 51. Service Version Selection

Version selection is an engineering decision, not a random tag choice.

Consider PostgreSQL.

If the target environment uses:

```text
PostgreSQL 16
```

prefer a compatible local image such as:

```text
postgres:16
```

rather than:

```text
postgres:latest
```

when production parity matters.

## Factors

Consider:

- major version;
- compatibility;
- client/server compatibility;
- production parity;
- documentation;
- support lifecycle;
- reproducibility;
- upgrade plans.

The same principle applies to:

```text
Redis
MinIO
Kafka
```

Use an intentional supported version.

---

# 52. One-Off Client Containers

A powerful pattern is:

> **Run a client tool in a temporary container instead of installing it permanently on the host.**

Why?

Your host might otherwise accumulate:

```text
psql
mc
redis-cli
Kafka CLI
database drivers
multiple versions
```

This can create dependency conflicts.

Instead:

```text
Host
  ↓
Docker
  ↓
temporary client container
  ↓
service
```

This keeps the host cleaner and can improve version alignment.

---

# 53. One-Off `psql` Client Container

Suppose PostgreSQL is running and reachable through the host.

You can use a PostgreSQL image that contains `psql` as a temporary client.

Conceptually:

```bash
docker run --rm -it \
  postgres:16 \
  psql ...
```

When the client needs to connect to a service running on the host, the exact host-address mechanism differs across Docker platforms.

On Linux, you may need an explicit host gateway mapping such as:

```bash
--add-host host.docker.internal:host-gateway
```

Then:

```bash
docker run --rm -it \
  --add-host host.docker.internal:host-gateway \
  postgres:16 \
  psql \
  -h host.docker.internal \
  -p 5432 \
  -U dataeng \
  -d datalab
```

The precise networking mechanism is intentionally not explored further here; Topic 03 owns that curriculum.

The important pattern is:

```text
Temporary PostgreSQL client
        ↓
PostgreSQL service
```

---

# 54. Why One-Off Clients Are Useful

Benefits include:

### Cleaner host

No permanent installation required.

### Version alignment

A PostgreSQL 16 image can provide a matching `psql` client.

### Reproducibility

The tool environment is defined by an image.

### Disposable

Use it, exit it, remove it.

This is particularly useful in CI-like local exercises and reproducible data labs.

---

# 55. One-Off MinIO Client Container

The same concept applies to `mc`.

Conceptually:

```text
Temporary mc container
        ↓
MinIO API
```

You can use a MinIO client image or an image documented for running `mc`.

The exact image/reference should be selected from current MinIO documentation.

A conceptual workflow:

```bash
docker run --rm -it <mc-image> ...
```

Then:

```text
configure alias
      ↓
create bucket
      ↓
upload/list object
```

The client disappears after the operation.

---

# 56. Service Dependencies

Real Data Engineering systems rarely contain only one service.

For example:

```text
Kafka
  ↓
Schema Registry
```

The Schema Registry depends on Kafka.

Another example:

```text
Python ingestion service
      ↓
PostgreSQL
```

The ingestion service depends on PostgreSQL.

The important question is:

> **What does "depends on" actually mean?**

---

# 57. Ordering vs Readiness

This distinction is fundamental.

### Ordering

```text
Start A
   ↓
Start B
```

### Readiness

```text
Start A
   ↓
Wait until A is ready
   ↓
Start B / connect B
```

These are not the same.

A service can start after its dependency starts:

```text
Kafka container starts
       ↓
Schema Registry starts
```

but Kafka may still be initializing.

Then:

```text
Schema Registry
       ↓
tries Kafka
       ↓
Kafka not ready
       ↓
connection failure
```

Professional orchestration reasons about readiness.

---

# 58. Kafka → Schema Registry Example

Conceptually:

```text
┌───────────────┐
│ Kafka         │
│ broker        │
└───────┬───────┘
        │
        │ dependency
        ▼
┌───────────────┐
│ Schema        │
│ Registry      │
└───────────────┘
```

Correct reasoning:

```text
Kafka container started
        ↓
Kafka initialized
        ↓
Kafka ready
        ↓
Schema Registry starts/connects
        ↓
Schema Registry ready
```

Incorrect reasoning:

```text
Kafka container started
        ↓
Schema Registry immediately assumes Kafka is ready
```

This distinction becomes especially important in multi-service Compose environments, which are covered later.

---

# 59. Local-Only Service Exposure

A local Data Engineering lab often does not need to expose services to the wider network.

If only your machine needs access, prefer a local binding such as:

```text
127.0.0.1
```

Conceptually:

```text
Your machine
     ↓
127.0.0.1
     ↓
Local service
```

rather than:

```text
All network interfaces
     ↓
Service
```

This is a basic security principle:

> **Do not expose a service beyond the audience that needs it.**

This is not a replacement for authentication or network security.

It is simply a safer default for local development.

---

# 60. Why Local-Only Exposure Matters

Suppose PostgreSQL is only needed by your local Python pipeline.

There is little reason for another machine on the network to access:

```text
5432
```

Similarly:

```text
MinIO
Redis
Kafka
```

should not be unnecessarily exposed.

Use local-only mappings for development whenever possible.

The complete networking curriculum is Topic 03.

---

# 61. Service Cards

Create a service card whenever you introduce a new containerized service.

Use:

```text
Service:
Image:
Version:
Purpose:
Ports:
Required environment variables:
Data directory:
Readiness check:
Connection test:
Client:
Dependencies:
```

A service card forces you to answer the operational questions before running the service.

---

# 62. PostgreSQL Service Card

```text
Service:
PostgreSQL

Image:
postgres

Version:
16

Purpose:
Relational database for structured Data Engineering workloads.

Ports:
5432/tcp

Required environment variables:
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB

Data directory:
/var/lib/postgresql/data

Readiness check:
pg_isready

Connection test:
psql / psycopg

Client:
psql / Python psycopg

Dependencies:
None for the basic local lab.
```

---

# 63. MinIO Service Card

```text
Service:
MinIO

Image:
MinIO server image selected from current documentation

Version:
Intentionally selected supported version

Purpose:
Local S3-compatible object storage.

Ports:
API: commonly 9000
Console: commonly 9001

Required configuration:
Root credentials
Server startup configuration

Data directory:
/data in the common server configuration

Readiness check:
Service/API health or successful client operation

Connection test:
mc / boto3

Client:
mc / Python boto3

Dependencies:
None for the basic local lab.
```

---

# 64. Redis Service Card

```text
Service:
Redis

Image:
redis

Version:
7

Purpose:
Fast key-value storage, caching, and temporary state.

Ports:
6379/tcp

Required environment variables:
None for the basic unauthenticated local lab

Data directory:
Not the focus of this topic

Readiness check:
Redis PING / CLI connection

Connection test:
redis-cli

Client:
redis-cli / Python Redis client

Dependencies:
None for the basic local lab.
```

---

# 65. Kafka Service Card

```text
Service:
Kafka

Image:
Selected Kafka distribution/image

Version:
Intentionally selected supported version

Purpose:
Event streaming and message transport.

Ports:
Defined by the selected listener configuration

Required configuration:
KRaft role configuration
Node ID
Controller quorum
Listeners
Advertised listeners where required

Data directory:
Kafka log/data directory defined by the selected image

Readiness check:
Kafka CLI/API administrative operation

Connection test:
Topic listing / producer / consumer

Client:
Kafka CLI / application client

Dependencies:
None in a single-node KRaft learning setup.
```

---

# 66. Startup-Time Measurement

A professional data engineer should care about:

> **How long does the container take to become actually usable?**

Measure:

```text
container start
      ↓
service ready
```

Do not measure only:

```text
docker run command duration
```

because the command can return before the service is ready when using detached mode.

---

# 67. PostgreSQL Startup Measurement

A simple shell pattern:

```bash
start=$(date +%s)

docker start pg-lab >/dev/null

until pg_isready -h localhost -p 5432 >/dev/null 2>&1; do
    sleep 1
done

end=$(date +%s)

echo "PostgreSQL ready in $((end - start)) seconds"
```

The exact number will vary with:

- machine speed;
- cold/warm state;
- image;
- database initialization;
- workload;
- host platform.

The lesson is the measurement methodology.

---

# 68. Redis Startup Measurement

A conceptual loop:

```text
start timer
   ↓
start Redis
   ↓
PING
   ↓
not ready?
   ↓
wait
   ↓
PING
   ↓
PONG
   ↓
stop timer
```

Redis may become ready quickly, but measuring it reinforces the same operational pattern.

---

# 69. MinIO Startup Measurement

Use an API/client operation as the readiness boundary.

Conceptually:

```text
start MinIO
   ↓
wait
   ↓
API/health request
   ↓
successful response
   ↓
READY
```

Do not assume the browser loading alone is your only readiness test.

---

# 70. Kafka Startup Measurement

Kafka usually requires more initialization than a trivial key-value service.

A useful readiness boundary is:

```text
start timer
   ↓
start Kafka
   ↓
wait
   ↓
Kafka administrative operation succeeds
   ↓
READY
```

For example:

```bash
kafka-topics.sh \
  --bootstrap-server <broker-endpoint> \
  --list
```

If the command can successfully communicate with the broker, you have stronger evidence that Kafka is usable.

---

# 71. Why Startup-to-Ready Time Matters

Readiness latency affects:

- integration tests;
- local labs;
- automated pipelines;
- CI;
- service orchestration;
- developer experience.

Suppose a test suite launches:

```text
PostgreSQL
Kafka
MinIO
Redis
```

If the test starts immediately after container creation, race conditions are likely.

Instead:

```text
Start
  ↓
Wait for readiness
  ↓
Run integration tests
```

This makes the workflow deterministic.

---

# 72. Complete Hands-On Lab — `docker_lab/02`

Create:

```text
docker_lab/
└── 02/
    ├── README.md
    ├── notes.md
    └── init.sql
```

The lab should be performed in stages.

---

# 73. Lab Exercise 1 — PostgreSQL

## Goal

Run PostgreSQL and prove that it is actually usable.

### Step 1 — Pull

```bash
docker pull postgres:16
```

### Step 2 — Run

```bash
docker run -d \
  --name pg-lab \
  -e POSTGRES_USER=dataeng \
  -e POSTGRES_PASSWORD=localdevpassword \
  -e POSTGRES_DB=datalab \
  -p 127.0.0.1:5432:5432 \
  postgres:16
```

### Step 3 — Check container state

```bash
docker ps
```

Record the result.

### Step 4 — Check readiness

```bash
pg_isready -h localhost -p 5432
```

### Step 5 — Connect

```bash
psql -h localhost -p 5432 -U dataeng -d datalab
```

### Step 6 — Validate

```sql
SELECT version();
SELECT current_database();
SELECT current_user;
```

### Step 7 — Create test data

```sql
CREATE TABLE pipeline_runs (
    run_id SERIAL PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    status TEXT NOT NULL
);

INSERT INTO pipeline_runs (pipeline_name, status)
VALUES
    ('customer_ingestion', 'success'),
    ('orders_ingestion', 'running');

SELECT * FROM pipeline_runs;
```

### Step 8 — Python connection

Use `psycopg` to execute:

```sql
SELECT COUNT(*) FROM pipeline_runs;
```

### Step 9 — Measure startup

Record:

```text
container started:
service ready:
startup-to-ready:
```

---

# 74. Lab Exercise 2 — MinIO

## Goal

Run local object storage and validate both interfaces.

### Step 1

Pull the documented MinIO image/version.

### Step 2

Start the server using the documented command.

Use local-only mappings.

### Step 3

Identify:

```text
API endpoint
Console endpoint
```

### Step 4

Open the console.

### Step 5

Create:

```text
data-lab
```

### Step 6

Create a file:

```text
sample.csv
```

Example:

```csv
id,name
1,Alice
2,Bob
```

### Step 7

Upload it to:

```text
data-lab/raw/sample.csv
```

### Step 8

List it using `mc`.

### Step 9

List it using Python/boto3.

### Step 10

Record startup-to-ready time.

---

# 75. Lab Exercise 3 — Redis

Run:

```bash
docker run -d \
  --name redis-lab \
  -p 127.0.0.1:6379:6379 \
  redis:7
```

Connect:

```bash
redis-cli -h 127.0.0.1 -p 6379
```

Test:

```text
PING
```

Expected:

```text
PONG
```

Then:

```text
SET pipeline:last_status success
GET pipeline:last_status
```

Record:

```text
container start time:
first successful PING:
startup-to-ready:
```

---

# 76. Lab Exercise 4 — Kafka

## Goal

Run a single-node Kafka KRaft environment.

### Step 1

Select a documented Kafka image/version.

### Step 2

Read its documentation before running it.

Record:

```text
image:
version:
node ID:
process roles:
listeners:
advertised listeners:
controller configuration:
```

### Step 3

Start the broker.

### Step 4

Check:

```bash
docker ps
```

### Step 5

Wait for application-level readiness.

### Step 6

Create a topic:

```text
orders
```

### Step 7

Produce:

```text
order-001
```

### Step 8

Consume the message.

### Step 9

Record startup-to-ready time.

### Step 10

Explain:

```text
node
broker
controller
topic
producer
consumer
```

---

# 77. Lab Exercise 5 — PostgreSQL Initialization SQL

Create:

```text
docker_lab/02/init.sql
```

Contents:

```sql
CREATE TABLE pipeline_runs (
    run_id SERIAL PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    status TEXT NOT NULL
);
```

Start a fresh PostgreSQL lab container with the script mounted into:

```text
/docker-entrypoint-initdb.d/
```

For example:

```bash
docker run -d \
  --name pg-init-lab \
  -e POSTGRES_USER=dataeng \
  -e POSTGRES_PASSWORD=localdevpassword \
  -e POSTGRES_DB=datalab \
  -p 127.0.0.1:5433:5432 \
  -v "$PWD/docker_lab/02/init.sql:/docker-entrypoint-initdb.d/init.sql:ro" \
  postgres:16
```

> **Scope note:** This example introduces a bind mount only because the initialization mechanism requires a file to be supplied to the container. Topic 04 owns the full storage curriculum.

Check:

```bash
psql -h localhost -p 5433 -U dataeng -d datalab
```

Then:

```sql
SELECT * FROM pipeline_runs;
```

The table should already exist.

---

# 78. Lab Exercise 6 — Prove Initialization Is First-Start Behavior

Insert:

```sql
INSERT INTO pipeline_runs (pipeline_name, status)
VALUES ('first_run', 'success');
```

Then restart:

```bash
docker restart pg-init-lab
```

Reconnect and query:

```sql
SELECT * FROM pipeline_runs;
```

The existing data should still be present.

Now change the SQL initialization file and restart the container.

Ask:

> Did the new SQL automatically execute?

Expected concept:

> No. Restarting an already initialized PostgreSQL data directory is not the same as initializing a new database cluster.

---

# 79. Lab Exercise 7 — One-Off `psql`

Use a temporary PostgreSQL client container.

Your objective is to prove:

```text
No permanent psql installation
        ↓
temporary client image
        ↓
PostgreSQL service
```

Record:

- client image;
- client version;
- server version;
- connection result.

Explain whether the client and server versions are intentionally aligned.

---

# 80. Lab Exercise 8 — One-Off `mc`

Use a temporary MinIO client container.

Perform:

```text
alias configuration
    ↓
bucket listing
    ↓
object listing
```

Then remove the client container automatically.

The objective is to practice disposable tooling.

---

# 81. Lab Exercise 9 — Dependency Readiness

Create a simple conceptual dependency:

```text
Kafka
  ↓
Dependent client
```

Start the client before Kafka is ready.

Observe the failure.

Then:

```text
Kafka
  ↓
wait for readiness
  ↓
dependent client
```

Repeat.

Record:

```text
Failure cause:
Readiness signal:
Correct startup sequence:
```

The point is not to build a complete orchestration system.

The point is to understand the dependency model.

---

# 82. Break/Fix Exercise 1 — PostgreSQL Too Early

Start PostgreSQL and immediately attempt a connection.

Possible result:

```text
connection refused
```

Do not conclude that PostgreSQL is broken.

Instead:

```bash
docker ps
```

then:

```bash
pg_isready -h localhost -p 5432
```

Wait until the readiness check succeeds.

### Lesson

```text
Started ≠ Ready
```

---

# 83. Break/Fix Exercise 2 — Wrong Credentials

Attempt:

```bash
psql \
  -h localhost \
  -p 5432 \
  -U wronguser \
  -d datalab
```

Diagnose the authentication failure.

Ask:

- Is the container running?
- Is PostgreSQL ready?
- Is the user correct?
- Is the database correct?
- Is the password correct?

Do not immediately restart the container.

---

# 84. Break/Fix Exercise 3 — MinIO Endpoint Confusion

Suppose you configure boto3 with:

```python
endpoint_url="http://127.0.0.1:9001"
```

when the S3 API is on the API endpoint.

The browser console may work at:

```text
9001
```

while the S3 API is on:

```text
9000
```

### Diagnose

```text
Console endpoint
    ≠
S3 API endpoint
```

### Correct mental model

```text
Browser → Console
boto3/mc → API
```

---

# 85. Break/Fix Exercise 4 — Kafka Too Early

Attempt:

```bash
kafka-topics.sh --list ...
```

while Kafka is still starting.

If it fails, ask:

```text
Is the container running?
Is Kafka initialized?
Is the broker ready?
Is the endpoint correct?
```

The first question is not necessarily:

> "Is Docker broken?"

---

# 86. Break/Fix Exercise 5 — Initialization Script Expectation

Modify:

```text
init.sql
```

Restart PostgreSQL.

Observe that the changed initialization SQL does not simply execute again.

Explain:

```text
restart
    ≠
fresh initialization
```

---

# 87. Break/Fix Exercise 6 — Dependency Ordering

Start a dependent service before Kafka is ready.

Observe:

```text
dependency started
       ≠
dependency ready
```

Then implement a readiness-aware sequence conceptually:

```text
Start Kafka
    ↓
Check Kafka readiness
    ↓
Start dependent service
```

---

# 88. Real-World Scenario 1 — Python Job Gets Connection Refused

### Situation

A Python ingestion job starts immediately after PostgreSQL.

It receives:

```text
connection refused
```

### Incorrect diagnosis

> PostgreSQL is broken.

### Better diagnosis

```text
Container running?
        ↓
PostgreSQL process running?
        ↓
PostgreSQL ready?
        ↓
Connection attempted?
```

The likely issue may be a startup race.

### Engineering response

Use an application-aware readiness check before opening the pipeline's database connection.

---

# 89. Real-World Scenario 2 — Init SQL Did Not Change the Schema

### Situation

You modify:

```text
init.sql
```

and restart PostgreSQL.

The database schema does not change.

### Why?

The database was already initialized.

The initialization directory is primarily a **first-initialization mechanism**, not a migration engine.

### Better mental model

```text
init.sql
    ↓
new database initialization
```

not:

```text
init.sql
    ↓
every restart
```

---

# 90. Real-World Scenario 3 — MinIO Console Works, Python Fails

### Situation

A developer can open MinIO in the browser, but boto3 cannot connect.

### Investigation

Check whether the Python client is using:

```text
API endpoint
```

or:

```text
Console endpoint
```

The browser may use the console.

Python should use the S3-compatible API.

---

# 91. Real-World Scenario 4 — Kafka Is "Up" but Producer Fails

### Situation

```bash
docker ps
```

shows Kafka:

```text
Up
```

but a producer cannot publish.

### Possible reasoning

```text
Container running
       ↓
Kafka initialization
       ↓
Broker ready?
       ↓
Listener reachable?
       ↓
Advertised address correct?
```

The full listener troubleshooting belongs to Topic 03, but Topic 02 should teach you not to equate `Up` with ready.

---

# 92. Real-World Scenario 5 — Too Many Local Client Installations

A developer has installed:

```text
psql
redis-cli
mc
Kafka CLI
```

on the host.

Different projects require different versions.

### Better approach

Use one-off client containers where practical:

```text
PostgreSQL image → psql
MinIO client image → mc
Kafka image → Kafka CLI
```

This can reduce host dependency conflicts.

---

# 93. Real-World Scenario 6 — Schema Registry Starts Too Early

### Situation

```text
Kafka starts
Schema Registry starts
Schema Registry fails
```

### Investigation

Kafka may have been started but not ready.

### Correct model

```text
Kafka container starts
       ↓
Kafka ready
       ↓
Schema Registry starts
       ↓
Schema Registry ready
```

### Core lesson

> **Dependency ordering is weaker than dependency readiness.**

---

# 94. Local Data Engineering Architecture

A local data lab can combine the services:

```text
                         Python Data Jobs
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        PostgreSQL           MinIO            Kafka
              │                │                │
              │                │                ▼
              │                │            Consumers
              │                │
              └────────────────┴───────────────┐
                                               │
                                             Redis
```

A more realistic conceptual pipeline:

```text
Source/API
    ↓
Python ingestion
    ↓
Kafka ───────────────→ streaming consumers
    │
    ↓
Python transformation
    │
    ├────────→ PostgreSQL
    │
    └────────→ MinIO
                  ↓
            Parquet / raw data
```

Redis can support fast temporary state or caching.

This architecture prepares you for later Data Engineering topics without teaching those topics here.

---

# 95. Service-to-Service Thinking

For every service, ask:

```text
Who starts me?
Who do I depend on?
Who depends on me?
How do I know I am ready?
How do clients connect?
What data do I own?
What version am I?
```

This is much stronger than memorizing individual Docker commands.

---

# 96. Production-Oriented Version Selection

A production-oriented Data Engineer should record service versions.

For example:

```text
PostgreSQL: 16
Redis: 7
Kafka: selected supported release
MinIO: selected supported release
```

Do not use:

```text
latest
latest
latest
latest
```

without understanding what those references mean.

## Why?

Because the environment is part of your pipeline.

A pipeline can fail because:

```text
code changed
```

but also because:

```text
service version changed
```

Therefore:

```text
Application reproducibility
        +
Infrastructure reproducibility
        =
More reliable Data Engineering
```

---

# 97. Version Matching With Production

Suppose production runs:

```text
PostgreSQL 16
```

Your local environment should generally use:

```text
PostgreSQL 16
```

when compatibility is the objective.

This does not mean:

> "Always run the same version forever."

It means:

> **Make version differences intentional.**

If production is being upgraded to PostgreSQL 17, build a test environment around the intended upgrade and test compatibility deliberately.

---

# 98. Service Readiness as a Contract

A useful advanced concept is a **readiness contract**.

A service is ready when it satisfies the condition that downstream consumers require.

For PostgreSQL:

```text
TCP port open
```

may not be sufficient.

A stronger contract is:

```text
PostgreSQL accepts authenticated connections
```

For Redis:

```text
PING → PONG
```

For Kafka:

```text
broker accepts administrative/client operations
```

For MinIO:

```text
API responds to an appropriate request
```

Therefore:

> **Readiness should be defined in terms of usable service behavior, not merely process existence.**

---

# 99. Startup vs Readiness Matrix

| Observation | What it proves | What it does not prove |
|---|---|---|
| `docker ps` shows container | Container is running | Application is fully ready |
| Process exists | Process started | Dependency is usable |
| Port appears open | Something is listening | Authentication/application health |
| Health check is healthy | Configured health test passed | Every application workflow succeeds |
| `pg_isready` succeeds | PostgreSQL accepts readiness connection | Your credentials/query are correct |
| Kafka CLI succeeds | Broker responds to that operation | Every Kafka client/network configuration is correct |
| MinIO API succeeds | API is responding | Browser console behavior |
| Redis `PING` → `PONG` | Redis responds | Your application logic is correct |

This matrix is a useful operational mental model.

---

# 100. Initialization vs Readiness

Do not confuse these concepts.

### Initialization

```text
Prepare the service's initial state.
```

### Readiness

```text
The service is usable for the required operation.
```

Example:

```text
PostgreSQL initialization
        ↓
database/user created
        ↓
PostgreSQL starts
        ↓
PostgreSQL ready
```

Initialization may be complete before readiness is reached.

---

# 101. Initialization vs Migration

A common beginner mistake is treating initialization scripts as migrations.

### Initialization

Usually establishes a new environment:

```text
CREATE DATABASE
CREATE initial tables
CREATE initial users
```

### Migration

Changes an existing schema from one known version to another.

For example:

```text
v1 schema
   ↓
migration
   ↓
v2 schema
```

This module only teaches initialization.

Do not use initialization SQL as a substitute for a production schema-migration strategy.

---

# 102. One-Off Tools as Reproducible Infrastructure

A one-off client container is itself a small reproducible environment:

```text
Client image
    ↓
Known tool version
    ↓
Known runtime
    ↓
Connect to service
    ↓
Remove client
```

This pattern is especially useful for:

- database administration;
- object-storage inspection;
- Kafka administration;
- CI integration tests;
- temporary debugging.

---

# 103. Safe Local Exposure

For local-only services, prefer:

```text
127.0.0.1
```

when the service does not need remote access.

Examples:

```text
PostgreSQL → 127.0.0.1:5432
Redis      → 127.0.0.1:6379
MinIO API  → 127.0.0.1:9000
MinIO UI   → 127.0.0.1:9001
```

The principle is:

```text
Minimum necessary exposure
```

This is a basic security habit that should become automatic.

---

# 104. Command Reference — PostgreSQL

| Command | Purpose | Example |
|---|---|---|
| `docker pull` | Pull PostgreSQL image | `docker pull postgres:16` |
| `docker run` | Start PostgreSQL | `docker run -d --name pg-lab ...` |
| `docker ps` | Check container | `docker ps` |
| `docker inspect` | Inspect container state/health | `docker inspect pg-lab` |
| `pg_isready` | Check PostgreSQL readiness | `pg_isready -h localhost -p 5432` |
| `psql` | Connect to PostgreSQL | `psql -h localhost -p 5432 -U dataeng -d datalab` |
| `docker restart` | Restart container | `docker restart pg-lab` |
| `docker stop` | Stop container | `docker stop pg-lab` |

---

# 105. Command Reference — MinIO

| Command | Purpose | Example |
|---|---|---|
| `docker run` | Start MinIO | Use documented MinIO server command |
| `mc alias set` | Configure client endpoint | `mc alias set local ...` |
| `mc ls` | List buckets/objects | `mc ls local` |
| `mc mb` | Create bucket | `mc mb local/data-lab` |
| `mc cp` | Copy/upload object | `mc cp sample.csv local/data-lab/` |
| `docker inspect` | Inspect container state | `docker inspect minio-lab` |

Remember:

```text
mc / boto3 → API
Browser → console
```

---

# 106. Command Reference — Redis

| Command | Purpose | Example |
|---|---|---|
| `docker run` | Start Redis | `docker run -d --name redis-lab redis:7` |
| `redis-cli` | Connect to Redis | `redis-cli -h 127.0.0.1 -p 6379` |
| `PING` | Validate response | `PING` |
| `SET` | Set key | `SET name "Data Engineer"` |
| `GET` | Retrieve key | `GET name` |

---

# 107. Command Reference — Kafka

Exact command paths vary by Kafka distribution/image.

Common conceptual commands include:

```bash
kafka-topics.sh
kafka-console-producer.sh
kafka-console-consumer.sh
```

Examples:

```bash
kafka-topics.sh \
  --bootstrap-server <broker> \
  --list
```

```bash
kafka-topics.sh \
  --bootstrap-server <broker> \
  --create \
  --topic orders \
  --partitions 1 \
  --replication-factor 1
```

```bash
kafka-console-producer.sh \
  --bootstrap-server <broker> \
  --topic orders
```

```bash
kafka-console-consumer.sh \
  --bootstrap-server <broker> \
  --topic orders \
  --from-beginning
```

Always use the syntax supplied by the selected Kafka distribution.

---

# 108. Common Mistakes

## Mistake 1 — Assuming `docker ps` means ready

### Why it happens

The container says:

```text
Up
```

### Correct model

```text
running ≠ ready
```

### Correct approach

Use a service-aware readiness check.

---

## Mistake 2 — Connecting immediately after startup

### Why it happens

Startup feels instantaneous.

### Correct model

Services may initialize internally.

### Correct approach

Wait for readiness.

---

## Mistake 3 — Wrong PostgreSQL credentials

### Why it happens

The learner assumes defaults.

### Correct model

Startup configuration determines the initialized user/password/database.

### Correct approach

Document the values used for the local lab.

---

## Mistake 4 — Assuming the default database/user

### Correct approach

Read the official image documentation and explicitly configure important values.

---

## Mistake 5 — Confusing MinIO API and console

### Correct model

```text
API → application
Console → browser
```

---

## Mistake 6 — Using `latest` casually

### Correct model

Service versions are infrastructure dependencies.

---

## Mistake 7 — Expecting initialization SQL on every restart

### Correct model

```text
initialization ≠ restart
```

---

## Mistake 8 — Treating initialization as migrations

Initialization is primarily first-start setup.

Schema migration is a different operational concern.

---

## Mistake 9 — Treating Kafka like PostgreSQL

Kafka is an event-streaming platform.

It has:

```text
brokers
topics
partitions
producers
consumers
```

---

## Mistake 10 — Ignoring Kafka startup time

Kafka can require more initialization than a simple local key-value service.

Use application-aware readiness.

---

## Mistake 11 — Assuming dependency order equals readiness

```text
A starts
  ↓
B starts
```

does not prove:

```text
A ready
  ↓
B can use A
```

---

## Mistake 12 — Installing every client locally

Use one-off client containers when practical.

---

## Mistake 13 — Exposing local services unnecessarily

Prefer:

```text
127.0.0.1
```

for host-only development where appropriate.

---

## Mistake 14 — Using production credentials in local labs

Use disposable local credentials.

Do not copy real production secrets into learning environments.

---

# 109. Practice Questions — Beginner

## Q1. What is a containerized database?

**Answer:** A database server process running inside a container managed by a container runtime.

**Why it matters:** It lets you run database infrastructure in a reproducible local environment without installing the complete database platform directly onto the host.

---

## Q2. What is PostgreSQL?

**Answer:** A relational database management system that accepts SQL requests from clients.

---

## Q3. What is MinIO?

**Answer:** An object-storage server that exposes an S3-compatible API.

---

## Q4. What is a Redis key-value store?

**Answer:** A service that associates keys with values for fast lookup and commonly supports caching and temporary state.

---

## Q5. What is Kafka?

**Answer:** A distributed event-streaming platform built around brokers, topics, partitions, producers, and consumers.

---

## Q6. What is a Kafka broker?

**Answer:** A Kafka server that receives, stores, and serves records.

---

## Q7. What is a Kafka topic?

**Answer:** A named stream/category into which producers write records and from which consumers read records.

---

## Q8. What is a bucket in MinIO?

**Answer:** A top-level object-storage namespace containing objects.

---

## Q9. What does `psql` do?

**Answer:** It is a command-line client for connecting to PostgreSQL and executing SQL.

---

## Q10. What is `pg_isready`?

**Answer:** A PostgreSQL utility used to check whether a PostgreSQL server is accepting connections.

---

# 110. Practice Questions — Intermediate

## Q11. Why can a container be running while PostgreSQL is not ready?

**Answer:** The PostgreSQL process can still be initializing its database state and configuration after the container itself has started.

---

## Q12. Why does `pg_isready` matter?

**Answer:** It tests PostgreSQL readiness rather than merely confirming that the container exists or is running.

---

## Q13. What is the difference between MinIO API and console?

**Answer:** The API is intended for programmatic object-storage operations; the console is a browser-oriented management interface.

---

## Q14. Why does Kafka require more networking awareness?

**Answer:** Kafka clients need to connect to broker endpoints, and Kafka can distinguish between listener endpoints and the addresses advertised to clients.

---

## Q15. What is KRaft?

**Answer:** Kafka's architecture for managing Kafka metadata and controller functionality without requiring ZooKeeper.

---

## Q16. Why do PostgreSQL initialization scripts behave differently on first startup?

**Answer:** They are designed to participate in initial database-cluster creation. An already initialized data directory is reused during ordinary restarts.

---

## Q17. Why is service readiness more useful than `docker ps` for pipeline startup?

**Answer:** A pipeline needs the service to accept its required operations, not merely for the container process to exist.

---

# 111. Practice Questions — Advanced

## Q18. Why is readiness more important than startup order?

**Answer:** Starting a dependency first does not guarantee that it has completed initialization and can serve requests.

---

## Q19. How would you design a local multi-service data lab?

**Answer:**

```text
Select service versions
       ↓
Run services with local-only exposure
       ↓
Define readiness checks
       ↓
Validate each service independently
       ↓
Document dependencies
       ↓
Start dependent workloads only after dependencies are ready
```

---

## Q20. Why use one-off client containers?

**Answer:** They reduce host-level installations, improve version alignment, and make client tooling disposable and reproducible.

---

## Q21. How should service versions be selected?

**Answer:** Select supported versions deliberately, align major versions with target environments where compatibility matters, and avoid treating `latest` as an immutable production reference.

---

## Q22. What happens when a dependent service starts before Kafka is ready?

**Answer:** It can fail its connection or initialization attempts. A robust workflow waits for Kafka's application-level readiness before allowing the dependent service to proceed.

---

# 112. Data Engineering Interview Practice

## Q1. How would you run PostgreSQL locally using Docker?

### Short answer

I would select a deliberate PostgreSQL major version, configure a disposable local user/database/password, bind PostgreSQL only to localhost when host access is required, start the container, and validate readiness with `pg_isready`.

### Detailed explanation

A professional local setup is more than:

```bash
docker run postgres
```

I would identify:

```text
image
version
credentials
database
port
readiness
persistence requirements
```

Then validate an actual connection.

### Practical example

```bash
docker run -d \
  --name pg-lab \
  -e POSTGRES_USER=dataeng \
  -e POSTGRES_PASSWORD=localdevpassword \
  -e POSTGRES_DB=datalab \
  -p 127.0.0.1:5432:5432 \
  postgres:16

pg_isready -h localhost -p 5432
```

---

## Q2. How do you know PostgreSQL is ready?

### Short answer

Use an application-aware check such as `pg_isready`, followed by an actual connection/query when necessary.

### Detailed explanation

`docker ps` only tells me that the container is running.

I want:

```text
PostgreSQL accepting connections
```

### Practical example

```bash
pg_isready -h localhost -p 5432
```

---

## Q3. What is `pg_isready`?

### Short answer

A PostgreSQL utility for checking server readiness/connection acceptance.

### Practical example

```bash
pg_isready -h localhost -p 5432
```

---

## Q4. What happens during PostgreSQL container initialization?

### Short answer

If the data directory is uninitialized, the image initializes a PostgreSQL database cluster and applies the configured initial user/database settings and supported initialization scripts.

### Practical example

```text
empty data directory
       ↓
database initialization
       ↓
init SQL
       ↓
ready
```

---

## Q5. Why don't PostgreSQL init scripts normally execute on every restart?

### Short answer

Because they are tied to initial database-cluster creation rather than ordinary service restart.

### Practical example

```text
first initialization → init.sql
restart → reuse existing cluster
```

---

## Q6. What is MinIO?

### Short answer

An S3-compatible object-storage server useful for local Data Engineering and lakehouse development.

### Practical example

```text
Python
 ↓
boto3
 ↓
MinIO API
 ↓
bucket
 ↓
Parquet object
```

---

## Q7. What is the difference between MinIO API and console?

### Short answer

The API is for programmatic object-storage access; the console is for browser-based administration and observation.

### Practical example

```text
boto3 → API
mc    → API
browser → console
```

---

## Q8. How would Python connect to MinIO?

### Short answer

Use an S3-compatible library such as boto3 with a custom MinIO endpoint and credentials.

### Practical example

```python
client = boto3.client(
    "s3",
    endpoint_url="http://127.0.0.1:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadminpassword",
)
```

---

## Q9. What is Redis useful for in a Data Engineering lab?

### Short answer

Redis can provide fast key-value storage for caching, counters, temporary state, and simple lookups.

---

## Q10. What is Kafka?

### Short answer

Kafka is an event-streaming platform built around brokers, topics, partitions, producers, and consumers.

---

## Q11. What is KRaft?

### Short answer

KRaft is Kafka's architecture for managing metadata/controller responsibilities within Kafka without ZooKeeper.

---

## Q12. What is a Kafka broker?

### Short answer

A Kafka server that accepts and serves records.

---

## Q13. What is a Kafka topic?

### Short answer

A named stream/category of records.

---

## Q14. What is a Kafka node ID?

### Short answer

An identifier for a Kafka node within the cluster.

---

## Q15. Why is Kafka startup/readiness more complex?

### Short answer

Kafka has more internal roles and metadata initialization than a simple standalone database/key-value service, particularly in KRaft mode.

---

## Q16. What is the difference between dependency order and dependency readiness?

### Short answer

Order says which service starts first. Readiness says whether the dependency is actually usable.

### Practical example

```text
Kafka started
    ≠
Kafka ready
```

---

## Q17. Why use one-off client containers?

### Short answer

They provide disposable, version-controlled client tools without permanently installing every dependency on the host.

---

# 113. Production Engineering Mindset

Develop these habits throughout your Data Engineering career.

## Habit 1 — Ask "ready?" not "running?"

Bad:

```text
docker ps → looks good
```

Better:

```text
service-specific readiness check
```

---

## Habit 2 — Make versions intentional

Bad:

```text
latest
```

Better:

```text
selected supported version
```

---

## Habit 3 — Understand initialization

Ask:

```text
When does initialization occur?
What triggers it?
Will restart trigger it?
What happens with existing state?
```

---

## Habit 4 — Document dependencies

For every service:

```text
depends on:
used by:
readiness:
```

---

## Habit 5 — Keep local credentials disposable

Never copy production secrets into local labs.

---

## Habit 6 — Minimize network exposure

If a service is local-only:

```text
127.0.0.1
```

is often the appropriate development boundary.

---

## Habit 7 — Measure readiness

Do not guess:

```text
sleep 10
```

when you can test:

```text
service is ready
```

---

## Habit 8 — Prefer reproducible tooling

Use one-off client containers where appropriate.

---

# 114. Mental Models You Must Remember

## Mental Model 1

```text
Container running
       ≠
Service ready
```

---

## Mental Model 2

```text
Database container
       ↓
Database server
       ↓
Client connection
```

---

## Mental Model 3

```text
MinIO
 ├── API → programmatic clients
 └── Console → humans/browser
```

---

## Mental Model 4

```text
Kafka
 ├── Broker
 ├── Controller
 ├── Topic
 ├── Producer
 └── Consumer
```

---

## Mental Model 5

```text
Initialization
       ≠
Restart
```

---

## Mental Model 6

```text
Dependency started
       ≠
Dependency ready
```

---

## Mental Model 7

```text
Service version
      +
Configuration
      +
Readiness
      +
Connection
      =
Usable local dependency
```

---

## Mental Model 8

```text
Image
  ↓
Container
  ↓
Service process
  ↓
Ready service
  ↓
Client
  ↓
Data Engineering workload
```

---

# 115. Final Knowledge Checkpoint

Before moving to Topic 03, you should be able to answer all of the following without notes.

### Containerized services

- [ ] What is a containerized data service?
- [ ] What is the difference between container and service process?
- [ ] What is the difference between server and client?
- [ ] Where does the service's data live conceptually?

### PostgreSQL

- [ ] What is PostgreSQL?
- [ ] How do you select a PostgreSQL image version?
- [ ] What are `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`?
- [ ] What is the default PostgreSQL data directory?
- [ ] How do you connect with `psql`?
- [ ] How do you connect from Python?
- [ ] How do you test readiness with `pg_isready`?
- [ ] What happens during first initialization?

### MinIO

- [ ] What is object storage?
- [ ] What is MinIO?
- [ ] What is a bucket?
- [ ] What is an object?
- [ ] What is the MinIO API?
- [ ] What is the MinIO console?
- [ ] Which endpoint should boto3 use?
- [ ] How do you create a bucket?
- [ ] How do you upload an object?

### Redis

- [ ] What is Redis?
- [ ] What is a key-value store?
- [ ] How do you test Redis?
- [ ] What do `SET` and `GET` do?

### Kafka

- [ ] What is Kafka?
- [ ] What is a broker?
- [ ] What is a topic?
- [ ] What is a producer?
- [ ] What is a consumer?
- [ ] What is a partition?
- [ ] What is KRaft?
- [ ] What is a node ID?
- [ ] What is a listener?
- [ ] Why does Kafka require more networking awareness?

### Readiness

- [ ] Why does `docker ps` not prove readiness?
- [ ] How do you validate PostgreSQL readiness?
- [ ] How do you validate Redis?
- [ ] How do you validate Kafka?
- [ ] How do health checks fit into the model?

### Initialization

- [ ] What is an initialization hook?
- [ ] How does PostgreSQL init SQL work?
- [ ] Why does it normally run only during initial database setup?
- [ ] Why is restart different from initialization?
- [ ] Why is initialization not a replacement for migrations?

### Advanced operations

- [ ] What is a one-off client container?
- [ ] Why use a temporary `psql` container?
- [ ] Why use a temporary `mc` container?
- [ ] What is a service dependency?
- [ ] What is the difference between ordering and readiness?
- [ ] Why should local services use local-only exposure where appropriate?
- [ ] How do you measure startup-to-ready time?

---

# 116. Final Mastery Checklist

You have mastered Topic 02 when you can demonstrate all of the following.

## Fundamentals

- [ ] Explain containerized services from first principles.
- [ ] Distinguish container, process, server, client, and data.
- [ ] Explain started vs ready.

## PostgreSQL

- [ ] Select PostgreSQL 16 deliberately.
- [ ] Run PostgreSQL locally.
- [ ] Configure the initial user.
- [ ] Configure the password.
- [ ] Configure the database.
- [ ] Explain the PostgreSQL data directory.
- [ ] Connect using `psql`.
- [ ] Execute SQL.
- [ ] Connect using Python/psycopg.
- [ ] Validate readiness with `pg_isready`.
- [ ] Explain initialization behavior.
- [ ] Explain restart vs initialization.

## MinIO

- [ ] Explain object storage.
- [ ] Run MinIO locally.
- [ ] Identify API and console endpoints.
- [ ] Configure local root credentials.
- [ ] Create a bucket.
- [ ] Upload an object.
- [ ] List objects with `mc`.
- [ ] Connect with boto3.
- [ ] Explain why API and console are different.

## Redis

- [ ] Run Redis.
- [ ] Connect with Redis CLI.
- [ ] Use `PING`.
- [ ] Use `SET`.
- [ ] Use `GET`.
- [ ] Explain a key-value service.

## Kafka

- [ ] Explain Kafka's purpose.
- [ ] Explain broker.
- [ ] Explain topic.
- [ ] Explain producer.
- [ ] Explain consumer.
- [ ] Explain partition at a high level.
- [ ] Explain KRaft.
- [ ] Explain node ID.
- [ ] Explain broker/controller roles.
- [ ] Explain listeners at an introductory level.
- [ ] Run a single-node learning setup.
- [ ] Create a topic.
- [ ] Produce a record.
- [ ] Consume a record.
- [ ] Validate broker readiness.

## Readiness and dependencies

- [ ] Explain why `docker ps` is insufficient.
- [ ] Use application-aware readiness checks.
- [ ] Understand health-check status.
- [ ] Explain dependency ordering vs readiness.
- [ ] Diagnose a startup race.

## Initialization

- [ ] Create a PostgreSQL initialization SQL script.
- [ ] Understand `/docker-entrypoint-initdb.d/`.
- [ ] Explain first-start behavior.
- [ ] Explain why restart does not normally rerun initialization scripts.
- [ ] Explain the relationship between initialized state and persistence.

## Advanced operational patterns

- [ ] Use a one-off `psql` client container.
- [ ] Use a one-off `mc` client container.
- [ ] Explain why disposable client environments are useful.
- [ ] Build service cards.
- [ ] Measure startup-to-ready time.
- [ ] Use local-only exposure when appropriate.
- [ ] Select versions deliberately.

## Professional reasoning

You should be able to answer:

> **"If this service is a dependency of my Data Engineering pipeline, how do I know it is actually ready, how do I connect to it, how do I reproduce the environment, and what does it depend on?"**

If you can answer that confidently, the objective of Topic 02 has been achieved.

---

# 117. Roadmap Coverage Audit

The following checklist maps the required Topic 02 roadmap items to this module.

| Required concept | Covered |
|---|---|
| PostgreSQL | ✓ |
| PostgreSQL required environment variables | ✓ |
| Default database | ✓ |
| Default user | ✓ |
| PostgreSQL data directory | ✓ |
| `psql` | ✓ |
| MinIO | ✓ |
| MinIO server command | ✓ |
| MinIO API port | ✓ |
| MinIO web console port | ✓ |
| MinIO root credentials | ✓ |
| Creating a bucket | ✓ |
| Redis | ✓ |
| Redis key-value model | ✓ |
| Kafka in KRaft mode | ✓ |
| Single-node Kafka | ✓ |
| Kafka node ID | ✓ |
| Kafka listeners | ✓ |
| Started vs Ready | ✓ |
| Readiness checks | ✓ |
| `pg_isready` | ✓ |
| Health endpoints | ✓ |
| Docker image health checks | ✓ |
| `docker inspect` health status | ✓ |
| Initialization hooks | ✓ |
| PostgreSQL initialization SQL | ✓ |
| First-start behavior | ✓ |
| Initialization/data-state relationship | ✓ |
| Service version selection | ✓ |
| PostgreSQL major-version matching | ✓ |
| One-off client containers | ✓ |
| One-off `psql` | ✓ |
| One-off `mc` | ✓ |
| Service dependencies | ✓ |
| Kafka → dependent service example | ✓ |
| Ordering vs readiness | ✓ |
| Local-only exposure | ✓ |
| `127.0.0.1` | ✓ |
| Service cards | ✓ |
| Startup-to-ready measurement | ✓ |
| `docker_lab/02` | ✓ |
| Break/fix exercises | ✓ |
| Real-world scenarios | ✓ |
| Mental models | ✓ |
| Command reference | ✓ |
| Common mistakes | ✓ |
| Practice questions | ✓ |
| Interview practice | ✓ |
| Final checkpoint | ✓ |
| Final mastery checklist | ✓ |

---

# 118. Final Professional Mental Model

A professional Data Engineer does not operate a service by thinking only:

```text
docker run
```

Instead, think:

```text
                 DATA SERVICE
                      │
                      ▼
                Select image
                      │
                      ▼
                Select version
                      │
                      ▼
                Understand config
                      │
                      ▼
                Start container
                      │
                      ▼
             Understand initialization
                      │
                      ▼
              Check service readiness
                      │
                      ▼
                 Connect client
                      │
                      ▼
                Validate operation
                      │
                      ▼
              Understand dependencies
                      │
                      ▼
              Operate reproducibly
```

The deepest lesson in Topic 02 is:

> **A running container is only the beginning. A Data Engineer must understand the service inside it, its initialization lifecycle, its readiness contract, its client interface, its dependencies, its version, and the boundaries around its exposure.**

That is the foundation required before moving into the deeper networking, persistence, configuration, troubleshooting, Compose, resource, cleanup, and platform topics of G1.
