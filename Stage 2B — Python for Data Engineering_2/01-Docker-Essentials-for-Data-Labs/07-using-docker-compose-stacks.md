# Using Docker Compose Stacks

> **Stage 2B — Docker Essentials for Data Labs**  
> **Topic 07 — Using Docker Compose Stacks**  
> **Phase C — Operating Stacks**
>
> This module teaches the operational use of Docker Compose for reproducible, multi-container Data Engineering environments. It assumes familiarity with containers, images, PostgreSQL, MinIO, Redis, Kafka, ports, networks, volumes, environment variables, logs, `docker exec`, and basic container troubleshooting.

---

## 1. Learning Objectives

By the end of this module, you should be able to:

- Explain why multi-container Data Engineering environments benefit from Docker Compose.
- Explain the difference between a Compose project, service, container, image, network, volume, and configuration.
- Read an existing Compose stack without needing to become an advanced YAML author.
- Use modern Compose commands through `docker compose`.
- Start, stop, restart, inspect, and tear down a Compose stack.
- Understand service names as internal network identities.
- Distinguish a host-published port from an internal service port.
- Understand how Compose networks, volumes, and environment configuration participate in a stack.
- Understand service dependencies and the difference between startup ordering and application readiness.
- Inspect stack status and service-specific logs.
- Execute commands inside Compose services.
- Preserve persistent Data Engineering state while recreating containers.
- Understand the destructive implications of `docker compose down -v`.
- Troubleshoot multi-service failures systematically.
- Trace downstream failures back to upstream dependencies.
- Operate a reproducible local Data Engineering lab containing PostgreSQL, MinIO, Kafka, Schema Registry, and Redis.
- Verify that services are actually usable rather than assuming that `docker compose up -d` means the environment is ready.

### The central progression

```text
Single Container
      ↓
Multiple Containers
      ↓
Compose Stack
      ↓
Services
      ↓
Networks
      ↓
Volumes
      ↓
Configuration
      ↓
Dependencies
      ↓
Readiness
      ↓
Lifecycle Operations
      ↓
Troubleshooting
      ↓
Reproducible Data Engineering Lab
```

---

## 2. Why Multi-Container Data Engineering Needs Compose

A Data Engineering environment rarely consists of one process.

A realistic local lab may need:

```text
PostgreSQL
MinIO
Redis
Kafka
Schema Registry
Python application
```

Without Compose, you may manually execute several commands:

```bash
docker run ...
docker run ...
docker run ...
docker run ...
docker run ...
docker run ...
```

That creates several operational problems:

1. You have to remember many commands.
2. Every service needs the correct configuration.
3. Network relationships have to be recreated consistently.
4. Persistent storage has to be mounted correctly.
5. Service names and ports have to be remembered.
6. Dependencies are easy to start incorrectly.
7. Troubleshooting becomes harder because the environment is not represented as one coherent unit.
8. A new engineer has to reconstruct your environment from instructions.

Compose gives the environment an operational definition:

```text
Compose Stack
      ↓
multiple related services
      ↓
one operational unit
```

This is particularly valuable for Data Engineering because a pipeline often depends on several infrastructure services at once.

For example:

```text
Python ingestion pipeline
       │
       ├── PostgreSQL
       ├── MinIO
       ├── Kafka
       └── Redis
```

Compose does not make these services magically healthy. It gives you a consistent way to define and operate the group.

### Operational takeaway

> **Compose turns a collection of manually operated containers into a reproducible multi-service local environment.**

---

## 3. What Is Docker Compose?

Docker Compose is a tool for defining and operating a multi-container application or service stack.

Think of it as a coordinator for related containers.

### The basic mental model

```text
Compose Project
      │
      ├── Service A
      │      └── Container
      │
      ├── Service B
      │      └── Container
      │
      ├── Service C
      │      └── Container
      │
      ├── Network
      │
      └── Volumes
```

### Important terms

| Term | Meaning |
|---|---|
| Compose project | A logical Compose environment containing related services |
| Service | A logical application/infrastructure component declared in Compose |
| Container | The runtime instance that actually executes a service |
| Image | The packaged filesystem/application used to create a container |
| Network | The communication environment used by services |
| Volume | Persistent storage associated with service data |
| Configuration | Environment and other settings that control service behavior |
| Stack | The complete collection of related services operated together |

### Service versus container

A service is the logical component.

A container is a runtime instance.

For example:

```text
Service:
postgres

Runtime:
postgres container
```

The service definition describes what should exist. The container is the concrete runtime object Docker is operating.

This distinction matters when a container is recreated. The service identity remains part of the Compose application even though its container may be replaced.

### The operational view

When you read a Compose stack, ask:

```text
What services exist?
        ↓
What image does each service use?
        ↓
Which ports are host-facing?
        ↓
Which services communicate internally?
        ↓
Which services have persistent volumes?
        ↓
Which configuration does each service receive?
        ↓
Which services depend on others?
        ↓
How do I verify readiness?
```

---

## 4. Compose V2

Use the current Docker CLI-integrated Compose command:

```bash
docker compose
```

Check the installed Compose version:

```bash
docker compose version
```

A typical environment reports a Compose v2 implementation.

### Modern syntax

```bash
docker compose up
docker compose ps
docker compose logs
docker compose exec
docker compose down
```

### Older syntax

Historically, Compose was commonly invoked as:

```bash
docker-compose
```

For this roadmap, use:

```bash
docker compose
```

The important operational skill is not memorizing historical naming. It is recognizing the current command style and understanding that Compose operations are performed through the Docker CLI.

### Verification

```bash
docker compose version
```

If the command is unavailable, verify that Docker Desktop or an appropriate Docker Engine/Compose installation is available before troubleshooting the Compose stack itself.

---

## 5. Compose Projects

A Compose project is the logical environment created and operated by a Compose configuration.

Conceptually:

```text
Compose Project
    ↓
multiple services
    ↓
project-specific containers
    ↓
project-specific network
    ↓
project-associated volumes
```

A project boundary becomes especially useful when several Data Engineering labs exist on the same machine.

For example:

```text
analytics-lab
    ├── postgres
    ├── kafka
    └── minio

streaming-lab
    ├── kafka
    ├── schema-registry
    └── redis
```

You need to know which stack you are operating before running destructive or disruptive commands.

### Identify the stack

From the directory containing the Compose configuration:

```bash
docker compose ps
```

This gives a Compose-oriented view of the services in the current project.

For broader runtime visibility:

```bash
docker ps
```

### Operational takeaway

> **Before operating a stack, establish which Compose project you are actually operating.**

---

## 6. Reading a Compose Stack

You do not need to become an advanced Compose YAML author to operate a stack effectively.

You do need to read an existing stack.

A simplified Data Engineering stack might look like:

```yaml
services:
  postgres:
    image: postgres:16
    ports:
      - "5433:5432"
    environment:
      POSTGRES_DB: analytics
      POSTGRES_USER: analytics_user
      POSTGRES_PASSWORD: dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"

  redis:
    image: redis:7

  kafka:
    image: <kafka-image>

volumes:
  postgres_data:
```

The exact image and Kafka configuration depend on the stack and project conventions. The important operational question is how to read the structure.

### The important fields

| Field | Operational meaning |
|---|---|
| `services` | Defines the logical services in the stack |
| Service name | Logical identity of a service |
| `image` | Image used to create the service container |
| `ports` | Host-to-container published port mappings |
| `environment` | Environment configuration passed to the container |
| `volumes` | Persistent or mounted storage |
| `networks` | Network attachment information |
| `depends_on` | Declared startup/dependency relationship |

### Read, do not guess

When you encounter a stack, identify:

```text
Services
   ↓
Images
   ↓
Host ports
   ↓
Internal ports
   ↓
Volumes
   ↓
Environment configuration
   ↓
Dependencies
```

The goal is:

> **Read the stack → understand the architecture → operate it.**

---

## 7. Services

Service names are logical identities inside the Compose stack.

For example:

```text
postgres
minio
redis
kafka
schema-registry
```

A service name can be used by another container on the same Compose network.

Conceptually:

```text
service name
      ↓
network DNS identity
      ↓
other containers can reach the service
```

For PostgreSQL:

```text
postgres:5432
```

is an internal service endpoint when the PostgreSQL service is named `postgres`.

### Why this matters

Suppose a Python application runs inside the same Compose network.

The application should generally use:

```text
DATABASE_HOST=postgres
DATABASE_PORT=5432
```

not:

```text
DATABASE_HOST=localhost
```

`localhost` inside the Python container refers to the Python container itself.

This is an operational application of the networking concepts covered earlier.

---

## 8. Compose Networks

Compose normally creates a project network for the services in a stack.

Conceptually:

```text
Compose Stack
      │
      ▼
Project Network
      │
  ┌───┼──────┐
  ▼   ▼      ▼
 PG  MinIO  Redis
```

Services attached to the network can communicate using service names and container ports.

### Internal communication

If PostgreSQL listens on:

```text
5432
```

then another container can use:

```text
postgres:5432
```

It does not need the host-published port.

### Host-facing communication

A developer on the laptop might use:

```text
localhost:5433
```

if Compose publishes:

```yaml
ports:
  - "5433:5432"
```

Therefore:

```text
Container → Container
    ↓
postgres:5432

Host → Container
    ↓
localhost:5433
```

### Why not publish every port?

Internal communication can stay inside the Compose network.

Publishing every service port:

- increases the number of host endpoints;
- can create port conflicts;
- exposes services unnecessarily;
- makes the architecture harder to reason about.

Publish ports that the host genuinely needs to access.

---

## 9. Host Ports vs Service Ports

This distinction is one of the most important Compose concepts.

Consider:

```yaml
ports:
  - "5433:5432"
```

Read it as:

```text
HOST_PORT:CONTAINER_PORT
```

Therefore:

```text
Host:
localhost:5433

Container/service:
postgres:5432
```

### From the host

A host-side client uses:

```bash
psql -h localhost -p 5433 -U analytics_user -d analytics
```

### From another container

A container-side client uses:

```text
postgres:5432
```

### Common mistake

Do not automatically take:

```text
localhost:5433
```

and put it into a Python container.

Inside the Python container:

```text
localhost
```

means that Python container.

### Mental model

```text
Host client
    │
    ▼
localhost:5433
    │
    ▼
Docker published port
    │
    ▼
postgres:5432

Container client
    │
    ▼
postgres:5432
```

### Operational takeaway

> **Host-published ports are for host access. Container-to-container communication normally uses the service name and container port.**

---

## 10. Compose Volumes

Persistent storage is a core part of a Data Engineering stack.

For PostgreSQL, a Compose configuration may contain:

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

The conceptual relationship is:

```text
postgres service
      ↓
postgres_data volume
      ↓
/var/lib/postgresql/data
```

A named volume normally survives container recreation.

Therefore:

```text
Container deleted
      ↓
Volume still exists
      ↓
Database data can remain
```

### Why this matters

A database container is disposable runtime state.

The database's persistent data should not be treated as disposable simply because the container is.

### Important distinction

```text
Container lifecycle
≠
Volume lifecycle
```

### Destructive operation

This command can remove project volumes:

```bash
docker compose down -v
```

Treat it as a data-reset operation.

### Inspect volumes

Use Docker's runtime inspection when you need deeper visibility:

```bash
docker volume ls
docker volume inspect <volume>
```

Do not delete a volume merely because you are cleaning up containers unless data deletion is intentional.

---

## 11. Compose Environment Configuration

Compose can provide configuration to services through environment variables.

Example:

```yaml
environment:
  POSTGRES_DB: analytics
  POSTGRES_USER: analytics_user
  POSTGRES_PASSWORD: dev_password
```

The operational flow is:

```text
Compose configuration
        ↓
container environment
        ↓
application behavior
```

### Inspect the running container

You can inspect the container:

```bash
docker inspect <container>
```

For targeted environment inspection, you can also use:

```bash
docker compose exec postgres env
```

Use this carefully because environment variables can contain sensitive configuration.

### Configuration debugging

If the stack behaves unexpectedly, compare:

```text
Expected configuration
        ↓
Compose configuration
        ↓
Actual container configuration
        ↓
Application behavior
```

Do not assume the value you intended to configure is the value the running service actually received.

---

## 12. Starting a Stack

Start the stack in the foreground:

```bash
docker compose up
```

Start it in detached mode:

```bash
docker compose up -d
```

### What Compose may do

When starting a stack, Compose can:

1. Resolve the Compose configuration.
2. Pull required images when necessary.
3. Create required networks.
4. Create required volumes.
5. Create service containers.
6. Start service containers.
7. Display startup output.

### Foreground mode

```bash
docker compose up
```

is useful when you want to watch startup output directly.

### Detached mode

```bash
docker compose up -d
```

returns control of your terminal while services continue running.

### Critical distinction

This:

```text
Compose command returned
```

does **not** necessarily mean:

```text
All services are ready
```

The real lifecycle can be:

```text
Compose starts containers
        ↓
Container process starts
        ↓
Application initializes
        ↓
Application becomes ready
```

Always verify readiness for services that matter to your workflow.

---

## 13. Checking Stack Status

Use:

```bash
docker compose ps
```

This gives a Compose-oriented view of the stack.

You can also use:

```bash
docker ps
```

### Compose view

Think:

```text
What does this Compose project think its services look like?
```

### Docker runtime view

Think:

```text
What containers does Docker currently have?
```

Using both can be useful:

```text
Compose view
+
Docker runtime view
=
better operational visibility
```

### What to inspect

Look for:

- service;
- container;
- state;
- ports;
- whether a service has exited;
- whether a service appears repeatedly restarted.

A stack where one service is missing or exited should not be treated as healthy merely because other services are running.

---

## 14. Stack Logs

For all service logs:

```bash
docker compose logs
```

Follow logs:

```bash
docker compose logs -f
```

Inspect one service:

```bash
docker compose logs postgres
```

Follow one service:

```bash
docker compose logs -f postgres
```

Limit the amount of historical output:

```bash
docker compose logs --tail 100 postgres
```

### Why service-specific logs matter

Suppose:

```text
Kafka       running
PostgreSQL  running
Redis       running
Schema Reg. failing
```

Running:

```bash
docker compose logs
```

may produce a large amount of output.

Start with:

```bash
docker compose logs schema-registry
```

Then inspect the dependency:

```bash
docker compose logs kafka
```

This reduces noise and supports evidence-driven diagnosis.

### Operational rule

> **Find the failing service first, then read its logs and its upstream dependency logs.**

---

## 15. Executing Commands in Services

Compose provides a service-oriented command:

```bash
docker compose exec <service> <command>
```

For PostgreSQL readiness:

```bash
docker compose exec postgres pg_isready
```

For an interactive PostgreSQL client:

```bash
docker compose exec postgres psql -U analytics_user -d analytics
```

For Redis, the exact command depends on the Redis image and installed tools:

```bash
docker compose exec redis redis-cli ping
```

Expected Redis response:

```text
PONG
```

### Service name versus container name

With Compose, prefer the service identity:

```bash
docker compose exec postgres ...
```

rather than manually discovering and typing a generated container name.

### Interactive shell

If a shell exists in the image:

```bash
docker compose exec postgres sh
```

Not every image contains the same shell or diagnostic utilities.

### Non-interactive execution

For automation and checks:

```bash
docker compose exec -T postgres pg_isready
```

The exact use of TTY options depends on the command and environment.

### Operational takeaway

> **`docker compose exec` lets you investigate a service through its logical Compose identity instead of manually operating the container name.**

---

## 16. Started vs Ready

This is a major operational concept.

A container being in a running state does not prove that its application is ready.

The progression is:

```text
Compose starts container
        ↓
Container process starts
        ↓
Application initializes
        ↓
Application becomes ready
```

For PostgreSQL, verify readiness explicitly:

```bash
docker compose exec postgres pg_isready
```

A dependent application may fail if it connects before PostgreSQL finishes initialization.

### Example

```text
PostgreSQL container:
running

PostgreSQL server:
still initializing

Python application:
attempts connection

Result:
connection failure
```

A retry or readiness-aware startup strategy may be required.

### Kafka

For Kafka, do not assume:

```text
Kafka container running
```

means:

```text
Kafka broker usable by every client
```

Verify client connectivity or an appropriate broker-specific readiness signal for the image/distribution being used.

### Mental model

```text
Running
   ↓
Initializing
   ↓
Ready
   ↓
Usable
```

---

## 17. Service Dependencies

A Data Engineering stack commonly has relationships such as:

```text
Application
    ↓
depends on
PostgreSQL
```

or:

```text
Schema Registry
    ↓
depends on
Kafka
```

Compose supports dependency declarations such as:

```yaml
depends_on:
  - postgres
```

The operational meaning is that the stack declares a relationship between services.

### Important warning

Do not interpret:

```text
depends_on
```

as:

```text
service is fully ready
```

A dependency relationship and application readiness are separate concerns.

For example:

```text
Schema Registry
      ↓
depends_on Kafka
```

does not eliminate the need to verify that Kafka is actually usable.

### Correct mental model

```text
depends_on
=
startup relationship

actual readiness
=
application-specific readiness check
```

This distinction prevents many false assumptions in local Data Engineering environments.

---

## 18. Startup Order vs Readiness

### Bad mental model

```text
depends_on
=
service is ready
```

### Better mental model

```text
depends_on
=
startup relationship
```

Then:

```text
actual readiness
=
application-specific readiness check
```

For PostgreSQL:

```bash
docker compose exec postgres pg_isready
```

For Kafka, verify actual broker/client connectivity according to the Kafka distribution used by the stack.

### Why this matters

Suppose:

```text
docker compose up -d
```

starts:

```text
Kafka
Schema Registry
```

The Schema Registry may start before Kafka is usable.

You can therefore observe:

```text
Kafka container: running
Schema Registry: restarting
```

The correct investigation is not:

```text
"Schema Registry is broken."
```

It is:

```text
"Why is Schema Registry unable to use its Kafka dependency?"
```

That leads to better diagnosis.

---

## 19. Stopping a Stack

To stop the containers without removing them:

```bash
docker compose stop
```

This normally means:

```text
Containers:
stopped

Containers:
remain

Network:
remains associated with the project

Named volumes:
remain
```

You can resume the existing containers with:

```bash
docker compose start
```

### Use `stop` when

- you want a temporary pause;
- you want to preserve the existing container state;
- you expect to resume the stack.

### Operational distinction

```text
stop
=
temporarily stop the stack
```

It is not a complete teardown.

---

## 20. Bringing a Stack Down

To tear down the running Compose stack:

```bash
docker compose down
```

Normally this removes:

- project containers;
- the Compose-created network.

Named volumes normally remain unless explicitly removed.

### Destructive variant

```bash
docker compose down -v
```

This can remove the project's volumes.

For a PostgreSQL service using a named volume:

```text
down
    ↓
containers/network removed
    ↓
database volume normally remains

down -v
    ↓
containers/network removed
    ↓
database volume removed
    ↓
persistent database data may be lost
```

### Strong warning

Never casually run:

```bash
docker compose down -v
```

against a stack whose persistent data matters.

Use it when a complete reset is intentional, especially in a disposable lab.

---

## 21. Recreating Services

Compose may reuse an existing container or recreate a container when the effective service configuration requires it.

The key operational question is:

```text
What happens to the container?
What happens to the volume?
```

These are separate lifecycles.

Conceptually:

```text
Service configuration changes
        ↓
Container may be recreated
        ↓
Named volume may remain
        ↓
Persistent data can remain
```

This is why database persistence should be designed through volumes rather than through the lifetime of the database container itself.

### Re-starting versus recreating

A restart:

```bash
docker compose restart postgres
```

restarts the service container.

A normal stack operation may result in a container being recreated if its configuration changes.

Do not confuse:

```text
restart
```

with:

```text
data reset
```

A container restart should not inherently mean database data deletion.

---

## 22. Service-Specific Operations

When one service has a problem, operate on that service when possible.

Restart PostgreSQL:

```bash
docker compose restart postgres
```

Stop PostgreSQL:

```bash
docker compose stop postgres
```

Start PostgreSQL:

```bash
docker compose start postgres
```

Execute a command:

```bash
docker compose exec postgres pg_isready
```

### Why targeted operations are preferable

Suppose:

```text
PostgreSQL: healthy
MinIO: healthy
Redis: healthy
Kafka: healthy
Schema Registry: failing
```

There is usually little value in restarting everything.

Instead:

```text
Inspect Schema Registry
        ↓
Inspect Kafka dependency
        ↓
Fix the relevant issue
        ↓
Restart Schema Registry if appropriate
        ↓
Verify
```

Targeted operations reduce unnecessary disruption and make troubleshooting easier to reason about.

---

## 23. Inspecting and Validating the Stack

Use:

```bash
docker compose config
```

to inspect the resolved Compose configuration and identify configuration problems before or during operation.

It is useful for questions such as:

- What configuration is Compose resolving?
- Are the service definitions syntactically and structurally valid?
- What values are actually being represented by the Compose configuration?

Use:

```bash
docker compose ps
```

for stack-level runtime status.

For deeper container-level state:

```bash
docker inspect <container>
```

### Evidence hierarchy

When debugging:

```text
Compose configuration
        ↓
Runtime container configuration
        ↓
Service state
        ↓
Service logs
        ↓
Application readiness
        ↓
Actual client behavior
```

Do not replace evidence with assumptions.

### Practical workflow

```bash
docker compose config
docker compose ps
docker compose logs <service>
docker inspect <container>
```

Use only the level of inspection necessary to answer the current question.

---

## 24. Multi-Service Data Engineering Stack

A realistic local Data Engineering stack can contain:

```text
PostgreSQL
MinIO
Kafka
Schema Registry
Redis
```

Conceptually:

```text
                    Docker Compose Stack
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
 PostgreSQL              MinIO               Redis
       │                   │
       │                   │
       └────────── Data Applications ──────────┘

                     Kafka
                       │
                       ▼
                Schema Registry
```

A more operationally meaningful view is:

```text
                       Compose Project
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
        PostgreSQL        MinIO          Redis
             │              │              │
             │              │              │
             └────────── Python pipelines ─┘

                     Kafka
                       │
                       ▼
                Schema Registry
```

### Typical roles

| Service | Typical local Data Engineering role |
|---|---|
| PostgreSQL | Relational database, metadata, warehouse-like local target, pipeline state |
| MinIO | S3-compatible object storage for raw/processed files and lake-style experiments |
| Kafka | Event streaming and messaging |
| Schema Registry | Schema management for schema-aware Kafka workflows |
| Redis | Fast key-value state, caching, lightweight coordination, or lookup use cases |
| Python application | Ingestion, transformation, validation, orchestration-adjacent or test workloads |

Exact relationships depend on the project.

---

## 25. Stack Architecture

A useful architecture separates services into operational categories.

### Host-facing services

These are services a developer may access directly from the host.

Examples may include:

```text
PostgreSQL
MinIO API
MinIO console
Kafka client endpoint
Redis
```

Only publish ports that the local workflow actually requires.

### Internal services

These are primarily accessed by other containers.

Examples:

```text
Python application → postgres:5432
Python application → redis:6379
Schema Registry → kafka:<internal-port>
```

### Persistent services

Services whose data should survive container recreation.

Typical examples:

```text
PostgreSQL
MinIO
Kafka
```

depending on the stack and lab requirements.

### Dependency services

Services that another service requires.

Examples:

```text
Schema Registry
      ↓
Kafka
```

and:

```text
Python pipeline
      ↓
PostgreSQL
```

The stack should make these relationships understandable.

---

## 26. Local Data Engineering Lab

The operational mental model is:

```text
Developer Laptop
       │
       ▼
Docker Compose
       │
       ├── PostgreSQL
       │
       ├── MinIO
       │
       ├── Kafka
       │
       ├── Schema Registry
       │
       └── Redis
```

### Why this is valuable

A Compose-based lab provides:

- reproducibility;
- consistent local setup;
- fewer manual commands;
- predictable service names;
- reusable development infrastructure;
- easier onboarding;
- easier reset and recovery.

A new engineer can move from:

```text
"Install five infrastructure services manually"
```

to:

```text
"Understand the stack and operate it through Compose."
```

### The key principle

Compose is not the Data Engineering platform itself.

It is the local operational mechanism that makes the platform components easier to run together.

---

## 27. Compose Lifecycle

The most important lifecycle operations can be compared as follows.

| Command | Containers | Network | Named Volumes | Typical use |
|---|---|---|---|---|
| `docker compose up` | Create/start as needed | Create/use | Create/use/preserve | Start stack |
| `docker compose stop` | Stop | Remains | Remains | Temporarily stop |
| `docker compose start` | Start existing | Remains | Remains | Resume existing services |
| `docker compose restart` | Restart selected/all services | Remains | Remains | Restart |
| `docker compose down` | Remove project containers | Remove project network | Normally remain | Tear down stack |
| `docker compose down -v` | Remove project containers | Remove project network | Remove project volumes | Intentional destructive reset |

### Lifecycle model

```text
                    docker compose up
                           │
                           ▼
                    services created
                           │
                           ▼
                    containers started
                           │
                           ▼
                  applications initialize
                           │
                           ▼
                    services become ready
                           │
                           ▼
                     stack operational
```

### Important lesson

The lifecycle of a service container and the lifecycle of persistent data are different.

---

## 28. Persistence and Reset Strategies

### Temporary stop

```bash
docker compose stop
```

Mental model:

```text
stop
=
pause operational state
```

The containers remain.

### Normal teardown

```bash
docker compose down
```

Mental model:

```text
down
=
remove stack containers/network
```

Named volumes normally remain.

### Full data reset

```bash
docker compose down -v
```

Mental model:

```text
down -v
=
remove stack containers/network + project volumes
```

This is potentially destructive.

### Choose deliberately

| Goal | Operation |
|---|---|
| Temporarily stop services | `docker compose stop` |
| Resume existing services | `docker compose start` |
| Restart a service | `docker compose restart <service>` |
| Remove stack runtime objects | `docker compose down` |
| Delete stack volumes intentionally | `docker compose down -v` |

### Data Engineering rule

> **A reset strategy must state explicitly whether persistent data should survive.**

---

## 29. Compose Troubleshooting

A multi-service troubleshooting workflow should be systematic.

```text
1. docker compose ps
2. docker compose logs <service>
3. docker compose config
4. inspect service configuration
5. check readiness
6. check network/service name
7. check storage
8. check dependencies
9. reproduce
10. fix
11. verify
```

### Step 1 — Identify the failing service

```bash
docker compose ps
```

Do not start by changing configuration.

### Step 2 — Read service logs

```bash
docker compose logs <service>
```

### Step 3 — Inspect resolved configuration

```bash
docker compose config
```

### Step 4 — Inspect runtime state

```bash
docker inspect <container>
```

### Step 5 — Check readiness

For PostgreSQL:

```bash
docker compose exec postgres pg_isready
```

### Step 6 — Check networking

Ask:

```text
Is the client using the correct service name?
Is it using the correct container port?
Is it incorrectly using localhost?
```

### Step 7 — Check storage

Ask:

```text
Is the expected volume mounted?
Did the volume survive?
Was it accidentally deleted?
```

### Step 8 — Check dependencies

Ask:

```text
Is the upstream service usable?
```

### Step 9 — Reproduce

Change one relevant variable at a time.

### Step 10 — Fix

Make the smallest relevant change.

### Step 11 — Verify

Do not stop after the error disappears.

Verify the intended application behavior.

---

## 30. Dependency Troubleshooting

A common mistake is diagnosing the downstream service first.

Consider:

```text
Schema Registry
       ↓
Kafka
       ↓
Kafka fails
       ↓
Schema Registry fails
```

The Schema Registry error may be a consequence rather than the root cause.

### Investigation order

```text
Schema Registry failure
        ↓
Inspect Schema Registry logs
        ↓
Identify Kafka connection problem
        ↓
Inspect Kafka status/logs
        ↓
Verify Kafka readiness/connectivity
        ↓
Fix Kafka
        ↓
Recheck Schema Registry
```

Another example:

```text
Python pipeline
       ↓
PostgreSQL
       ↓
PostgreSQL not ready
       ↓
Python connection failure
```

The Python stack trace does not automatically mean the Python code is wrong.

### Professional rule

> **Downstream error does not necessarily mean downstream root cause.**

---

## 31. Networking Troubleshooting

Use the networking knowledge from the earlier networking module.

Suppose a Python service uses:

```text
DATABASE_HOST=postgres
DATABASE_PORT=5432
```

The path is:

```text
Python container
      ↓
postgres
      ↓
Compose DNS
      ↓
PostgreSQL service
```

### Common mistakes

#### Mistake 1 — `localhost`

Incorrect from inside the Python container:

```text
DATABASE_HOST=localhost
```

Correct concept:

```text
DATABASE_HOST=postgres
```

#### Mistake 2 — Wrong service name

If the service is named:

```text
postgres
```

do not assume:

```text
postgresql
database
pg
```

are valid DNS identities.

Read the Compose configuration.

#### Mistake 3 — Wrong internal port

If:

```yaml
ports:
  - "5433:5432"
```

the internal port is still:

```text
5432
```

#### Mistake 4 — Using the host port internally

A container should generally connect to:

```text
postgres:5432
```

rather than:

```text
localhost:5433
```

#### Mistake 5 — Service not ready

Correct hostname and port are insufficient if the service has not completed initialization.

---

## 32. Storage Troubleshooting

Use the persistence concepts from the volumes module.

When a database appears empty after a stack reset, investigate:

```text
Was the volume removed?
        ↓
Was a different volume used?
        ↓
Was the expected volume mounted?
        ↓
Was the data directory initialized again?
```

Inspect volumes:

```bash
docker volume ls
```

Inspect a specific volume:

```bash
docker volume inspect <volume>
```

Inspect the service's runtime mounts:

```bash
docker inspect <container>
```

### Common incident

> PostgreSQL starts successfully but the database appears empty after resetting the stack.

Do not immediately recreate or reinitialize the database.

First determine:

```text
Which volume was used?
Did the volume survive?
Was `down -v` executed?
Was the service attached to a different volume?
```

### Key lesson

```text
Container recreation
≠
Data deletion
```

but:

```text
Volume deletion
=
Potential persistent-data deletion
```

---

## 33. Configuration Troubleshooting

Use configuration knowledge from the environment-variable module.

The debugging chain is:

```text
Expected value
      ↓
Compose configuration
      ↓
Resolved configuration
      ↓
Running container environment
      ↓
Application behavior
```

Useful commands include:

```bash
docker compose config
```

and:

```bash
docker compose exec <service> env
```

plus:

```bash
docker inspect <container>
```

### Example

Suppose a Python pipeline cannot authenticate to PostgreSQL.

Do not immediately change the password.

Check:

```text
Which username does the pipeline use?
Which database does it use?
Which host does it use?
Which port does it use?
Did Compose provide the expected environment?
Is PostgreSQL initialized with the expected credentials?
```

Then change one relevant value and verify.

---

## 34. Stack Startup Failure

Consider:

```bash
docker compose up -d
```

Several services appear to start, but one service repeatedly exits.

Start with:

```bash
docker compose ps
```

Then:

```bash
docker compose logs <service>
```

Then:

```bash
docker compose config
```

If necessary:

```bash
docker inspect <container>
```

### Evidence-driven sequence

```text
Symptom
   ↓
Service status
   ↓
Service logs
   ↓
Resolved configuration
   ↓
Runtime inspection
   ↓
Root cause
   ↓
Smallest fix
   ↓
Verification
```

### Example diagnosis

Suppose:

```text
postgres: running
redis: running
minio: running
kafka: running
schema-registry: exited
```

Do not restart the entire stack.

Inspect:

```bash
docker compose logs schema-registry
```

If the logs show connection failure to Kafka, inspect:

```bash
docker compose logs kafka
```

Then verify Kafka connectivity/readiness.

---

## 35. Stack Readiness Failure

Consider:

```text
All containers appear running,
but the application cannot connect.
```

The investigation should distinguish:

```text
Container state
        ↓
Application state
        ↓
Dependency state
        ↓
Network connectivity
        ↓
Application readiness
```

### Example

```text
PostgreSQL:
container running

PostgreSQL:
server still initializing

Python:
attempts connection

Python:
connection refused
```

The correct conclusion is not:

```text
Python is broken.
```

The better conclusion is:

```text
Python attempted to use a dependency that was not ready.
```

Verify PostgreSQL:

```bash
docker compose exec postgres pg_isready
```

Then retry the application operation.

---

## 36. Break/Fix Lab

This laboratory is designed to make Compose operational knowledge practical.

> **Safety rule:** Perform destructive experiments only in a disposable lab. Never use `docker compose down -v` against important data.

For every failure, use:

```text
Symptom
→
Evidence
→
Hypothesis
→
Inspection
→
Root Cause
→
Fix
→
Verification
```

### Failure 1 — Wrong PostgreSQL configuration

Create a client configuration with an incorrect database name, username, or connection setting.

Diagnose:

```bash
docker compose ps
docker compose logs postgres
docker compose config
```

Determine whether:

- PostgreSQL is running;
- PostgreSQL is ready;
- the client is using the expected configuration.

Fix the client configuration and verify connectivity.

---

### Failure 2 — Wrong service hostname

Configure a containerized client to use:

```text
localhost
```

instead of:

```text
postgres
```

Expected symptom:

```text
connection failure
```

Diagnosis:

```text
Client is inside a container.
localhost means the client container.
```

Fix:

```text
postgres
```

and use the internal PostgreSQL port.

---

### Failure 3 — Wrong internal port

Suppose:

```yaml
ports:
  - "5433:5432"
```

Configure an internal client to use:

```text
postgres:5433
```

The client should instead use:

```text
postgres:5432
```

because `5433` is the host-published port.

---

### Failure 4 — PostgreSQL not ready

Start the stack and immediately run a dependent application.

The application fails even though the PostgreSQL container is running.

Investigate:

```bash
docker compose ps
docker compose logs postgres
docker compose exec postgres pg_isready
```

Explain:

```text
startup order
≠
readiness
```

---

### Failure 5 — Missing volume

Recreate a service while observing its persistence behavior.

Determine:

```text
Was the volume preserved?
Was the mount path correct?
Was a new volume created?
```

Use:

```bash
docker volume ls
docker volume inspect <volume>
docker inspect <container>
```

---

### Failure 6 — Accidental volume deletion

In a disposable lab only:

```bash
docker compose down -v
```

Observe that project volumes may be removed.

Bring the stack back:

```bash
docker compose up -d
```

Verify that the previous persistent state is no longer available if the removed volume was the only copy.

### Lesson

```text
down
≠
down -v
```

---

### Failure 7 — Kafka dependency problem

Create or use a scenario where Kafka is not usable.

Inspect:

```bash
docker compose ps
docker compose logs kafka
```

Then inspect dependent services.

Trace:

```text
Kafka problem
      ↓
Schema Registry problem
      ↓
downstream errors
```

Diagnose the upstream issue before changing the downstream service.

---

### Failure 8 — Schema Registry dependency failure

If Schema Registry cannot use Kafka:

```bash
docker compose logs schema-registry
docker compose logs kafka
```

Determine:

- whether Kafka is running;
- whether Kafka is ready;
- whether the Schema Registry is using the correct Kafka endpoint;
- whether the failure is upstream.

---

### Failure 9 — One service repeatedly restarts

Use:

```bash
docker compose ps
docker compose logs <service>
```

Then inspect:

```bash
docker inspect <container>
```

Find the first meaningful failure.

Do not repeatedly restart without collecting evidence.

---

### Failure 10 — Configuration mismatch

Create a mismatch between expected and actual environment configuration.

Compare:

```text
Expected
   ↓
Compose configuration
   ↓
Running container
```

Use:

```bash
docker compose config
docker compose exec <service> env
docker inspect <container>
```

Correct the relevant value and verify behavior.

---

## 37. Real-World Data Engineering Scenarios

### Scenario 1 — New developer onboarding

A new engineer needs:

```text
PostgreSQL
Kafka
MinIO
Redis
Schema Registry
```

Manual installation requires multiple setup procedures.

A Compose stack provides one operational environment.

The onboarding workflow becomes:

```text
Obtain project
      ↓
Read Compose stack
      ↓
docker compose up -d
      ↓
Check status
      ↓
Check readiness
      ↓
Begin development
```

The engineer still needs to understand what each service does. Compose reduces operational setup complexity; it does not remove the need for architecture knowledge.

---

### Scenario 2 — Local pipeline development

A Python ingestion pipeline needs PostgreSQL and MinIO.

The pipeline can use:

```text
postgres:5432
```

for PostgreSQL and the MinIO service name plus its internal API port for object storage.

Host-published ports can be used by tools running on the developer's laptop.

This creates a clear separation:

```text
Python container
    ↓
internal service names/ports

Developer laptop
    ↓
localhost + published ports
```

---

### Scenario 3 — Full local data platform

The engineer wants:

```text
Kafka
+
Schema Registry
+
PostgreSQL
+
MinIO
+
Redis
```

running as one reproducible environment.

Compose provides:

```text
one project
   ↓
multiple services
   ↓
shared network
   ↓
service discovery
   ↓
persistent storage where required
   ↓
repeatable lifecycle operations
```

The engineer must still verify dependency readiness.

---

### Scenario 4 — Database reset without losing data

The learner wants to recreate PostgreSQL without losing data.

The critical distinction is:

```text
recreate container
```

versus:

```text
delete volume
```

If the named volume remains mounted correctly:

```text
container recreated
      ↓
same persistent volume
      ↓
data remains
```

---

### Scenario 5 — Complete lab reset

The learner intentionally wants a clean environment.

In a disposable lab:

```bash
docker compose down -v
```

may be appropriate.

The command must be understood as:

```text
remove containers
+
remove project network
+
remove project volumes
```

Do not use this as a casual troubleshooting command.

---

### Scenario 6 — One service unavailable

Suppose:

```text
PostgreSQL: healthy
MinIO: healthy
Redis: healthy
Kafka: healthy
Schema Registry: unavailable
```

Do not automatically run:

```bash
docker compose restart
```

for the whole stack.

Instead:

```bash
docker compose logs schema-registry
docker compose logs kafka
```

Then perform targeted operations if required:

```bash
docker compose restart schema-registry
```

Verify the service after the restart.

---

## 38. Operational Best Practices

### 1. Start the entire environment with Compose

Prefer the stack definition over remembering many manual `docker run` commands.

### 2. Know the service names

Service names are important operational identities.

### 3. Know host-facing ports

Record which services need host access.

### 4. Know internal service ports

Do not confuse published host ports with container ports.

### 5. Know persistent volumes

Understand which services contain important state.

### 6. Check readiness

Do not assume:

```text
running = ready
```

### 7. Use service-specific logs

Prefer:

```bash
docker compose logs <service>
```

when diagnosing a particular failure.

### 8. Use service-specific operations

Prefer:

```bash
docker compose restart <service>
```

when only one service requires intervention.

### 9. Avoid destructive volume deletion

Treat:

```bash
docker compose down -v
```

as a deliberate data reset.

### 10. Keep the stack reproducible

Avoid undocumented manual changes that make one laptop behave differently from another.

### 11. Inspect effective configuration

Use:

```bash
docker compose config
```

when configuration is uncertain.

### 12. Document service relationships

A good local platform description should identify:

```text
service
port
volume
dependency
readiness check
```

---

## 39. Command Reference

### `docker compose version`

**Purpose**

Check Compose availability and version.

**Syntax**

```bash
docker compose version
```

**Expected behavior**

Prints the installed Compose version.

**Warning**

Do not confuse Compose availability with the health of your application stack.

---

### `docker compose up`

**Purpose**

Create and start the Compose stack.

**Syntax**

```bash
docker compose up
```

**Example**

```bash
docker compose up
```

**Expected behavior**

Services start and logs remain attached to the terminal.

**Warning**

Service startup does not prove application readiness.

---

### `docker compose up -d`

**Purpose**

Start the stack in detached mode.

**Syntax**

```bash
docker compose up -d
```

**Expected behavior**

Containers run in the background.

**Verification**

```bash
docker compose ps
```

**Warning**

Always perform readiness checks for important services.

---

### `docker compose ps`

**Purpose**

Inspect Compose project service status.

**Syntax**

```bash
docker compose ps
```

**Example**

```bash
docker compose ps
```

**Expected behavior**

Shows services and runtime state.

**Warning**

A running state does not necessarily mean the application is ready.

---

### `docker compose logs`

**Purpose**

Read stack logs.

**Syntax**

```bash
docker compose logs
```

**Example**

```bash
docker compose logs postgres
```

**Warning**

Large multi-service logs can hide the useful signal. Target the failing service when possible.

---

### `docker compose logs -f`

**Purpose**

Follow logs as they arrive.

**Syntax**

```bash
docker compose logs -f
```

**Example**

```bash
docker compose logs -f postgres
```

**Warning**

Stop following when enough evidence has been collected; do not treat log watching as diagnosis by itself.

---

### `docker compose logs --tail 100 postgres`

**Purpose**

Read the most recent PostgreSQL log lines.

**Expected behavior**

Limits the historical output and makes recent failures easier to inspect.

---

### `docker compose exec <service> <command>`

**Purpose**

Run a command inside a service container.

**Example**

```bash
docker compose exec postgres pg_isready
```

**Expected behavior**

The command executes inside the PostgreSQL service container.

**Warning**

The command must exist in the image.

---

### `docker compose stop`

**Purpose**

Stop services without tearing down the stack.

**Example**

```bash
docker compose stop
```

**Expected behavior**

Containers stop but remain available to start again.

**Warning**

This is not the same as removing the stack.

---

### `docker compose start`

**Purpose**

Start existing stopped containers.

**Example**

```bash
docker compose start
```

**Expected behavior**

Existing services are started.

---

### `docker compose restart`

**Purpose**

Restart services.

**Example**

```bash
docker compose restart postgres
```

**Expected behavior**

The selected service restarts.

**Warning**

Restarting is not a substitute for finding root cause.

---

### `docker compose down`

**Purpose**

Tear down the Compose runtime resources for the project.

**Example**

```bash
docker compose down
```

**Expected behavior**

Project containers and Compose network are removed; named volumes normally remain.

**Warning**

Do not assume all state is deleted.

---

### `docker compose down -v`

**Purpose**

Tear down the stack and remove project volumes.

**Example**

```bash
docker compose down -v
```

**Expected behavior**

Project containers/network and project volumes are removed.

**Warning**

This can destroy persistent Data Engineering state.

---

### `docker compose config`

**Purpose**

Inspect the resolved Compose configuration.

**Example**

```bash
docker compose config
```

**Expected behavior**

Displays the effective Compose configuration representation.

**Warning**

Treat configuration inspection as an evidence-gathering operation, not as a substitute for checking runtime behavior.

---

### `docker inspect <container>`

**Purpose**

Inspect deeper runtime configuration and state.

**Example**

```bash
docker inspect <container>
```

**Useful for**

- mounts;
- environment-related runtime information;
- networking;
- state;
- container configuration.

---

### PostgreSQL readiness

```bash
docker compose exec postgres pg_isready
```

**Purpose**

Verify whether PostgreSQL is accepting connections.

**Warning**

The exact command depends on the image containing `pg_isready`.

---

## 40. Common Mistakes

### 1. Treating Compose as magic

Compose coordinates services; it does not eliminate the need to understand them.

### 2. Not understanding what each service does

A stack is easier to troubleshoot when every service has a clear role.

### 3. Confusing service names with container names

Use the Compose service identity for Compose operations.

### 4. Using `localhost` incorrectly inside containers

`localhost` refers to the current container.

### 5. Using host ports for internal communication

Prefer:

```text
postgres:5432
```

over a host-published address for container-to-container traffic.

### 6. Assuming `depends_on` means application readiness

Dependency ordering is not the same as readiness.

### 7. Assuming all services are ready immediately after `up -d`

Initialization can take time.

### 8. Restarting the entire stack for a single-service problem

Target the affected service when appropriate.

### 9. Running `down -v` without realizing it deletes persistent volumes

This is one of the most dangerous local-lab mistakes.

### 10. Forgetting which services have persistent state

PostgreSQL and object storage commonly require persistent storage.

### 11. Ignoring service-specific logs

Stack-wide logs can obscure the failure.

### 12. Ignoring upstream dependency failures

A downstream failure may be a consequence.

### 13. Changing multiple configuration values at once

You lose the ability to know which change affected the result.

### 14. Not inspecting effective Compose configuration

When configuration is uncertain, inspect it rather than guessing.

### 15. Assuming a running container means a usable service

Verify readiness.

### 16. Treating Compose as a production orchestration replacement for Kubernetes

Compose is highly useful for local and development stacks, but production orchestration requirements can be substantially different.

### 17. Overcomplicating local stacks unnecessarily

Add services because the workflow needs them, not because a technology is fashionable.

---

## 41. Mental Models

### Mental Model 1

```text
Compose
=
operational definition of a multi-container stack
```

Compose gives related services a coherent operational boundary.

---

### Mental Model 2

```text
Service
=
logical application component
```

The service is the logical identity; the container is its runtime instance.

---

### Mental Model 3

```text
Service name
=
internal DNS identity
```

For example:

```text
postgres:5432
```

is an internal service endpoint when the service is named `postgres`.

---

### Mental Model 4

```text
Host port
≠
container/service port
```

Example:

```text
localhost:5433
        ↓
postgres:5432
```

---

### Mental Model 5

```text
Container started
≠
application ready
```

Always distinguish runtime state from application state.

---

### Mental Model 6

```text
depends_on
≠
full application readiness
```

Dependencies describe relationships; readiness must be verified.

---

### Mental Model 7

```text
Container lifecycle
≠
volume lifecycle
```

Recreating a database container does not inherently mean deleting its named volume.

---

### Mental Model 8

```text
docker compose down
≠
docker compose down -v
```

The second command adds project-volume removal.

---

### Mental Model 9

```text
One stack
=
multiple services
+
network
+
configuration
+
storage
+
dependencies
```

A useful Compose operator understands the entire relationship rather than memorizing one command.

---

## 42. Architecture Diagrams

### Basic Compose architecture

```text
                    Docker Compose
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
        PostgreSQL      Redis       MinIO
             │           │           │
             └───────────┼───────────┘
                         │
                  Project Network
```

### Data Engineering stack

```text
                         Compose Stack
                              │
          ┌───────────────────┼──────────────────┐
          │                   │                  │
          ▼                   ▼                  ▼
     PostgreSQL             MinIO              Redis
          │                   │                  │
          └──────────────┬────┴──────────────────┘
                         │
                  Python Data Apps

                       Kafka
                         │
                         ▼
                  Schema Registry
```

The Kafka → Schema Registry relationship is shown separately because Schema Registry commonly depends on Kafka while the database/object-store services support different pipeline workloads.

### Lifecycle diagram

```text
docker compose up
        ↓
services created
        ↓
containers started
        ↓
applications initialize
        ↓
services become ready
        ↓
stack operational
```

### Troubleshooting decision tree

```text
Stack problem
     │
     ▼
docker compose ps
     │
     ├── All services running?
     │        │
     │        ├── No → inspect failed service logs
     │        │
     │        └── Yes
     │
     ▼
Is application usable?
     │
     ├── No → check readiness
     │
     ▼
Check connectivity
     │
     ├── Wrong hostname?
     ├── Wrong port?
     ├── Wrong dependency?
     └── Wrong configuration?
     │
     ▼
Check storage if state is involved
     │
     ▼
Reproduce
     │
     ▼
Fix
     │
     ▼
Verify
```

---

## 43. Hands-On Data Engineering Lab

### Objective

Operate a complete local Data Engineering environment using Docker Compose.

The intended stack contains:

- PostgreSQL;
- MinIO;
- Kafka;
- Schema Registry;
- Redis.

Use the existing project Compose configuration and image conventions where applicable rather than inventing a production deployment.

### Step 1 — Understand the architecture

Before starting anything, document:

```text
Service
Role
Host port(s)
Internal port(s)
Persistent volume(s)
Dependencies
Readiness check
```

A simple table is useful:

| Service | Role | Host access | Persistence | Dependency |
|---|---|---|---|---|
| PostgreSQL | Relational data | Published DB port if needed | Database volume | None or application-specific |
| MinIO | Object storage | API/console ports if needed | Object-store volume | None |
| Redis | Key-value service | Port if needed | Usually workload-specific | None |
| Kafka | Streaming broker | Client port(s) if needed | Broker storage | None |
| Schema Registry | Schema service | Port if needed | Depends on stack | Kafka |

Exact ports and image-specific settings should come from the actual Compose configuration.

### Step 2 — Read the Compose configuration

Identify:

```text
services:
images:
ports:
environment:
volumes:
networks:
depends_on:
```

Do not modify the file merely to complete this exercise.

### Step 3 — Start the stack

```bash
docker compose up -d
```

### Step 4 — Inspect the stack

```bash
docker compose ps
```

Also inspect the broader Docker runtime when useful:

```bash
docker ps
```

### Step 5 — Inspect logs

```bash
docker compose logs
```

Then target individual services:

```bash
docker compose logs postgres
docker compose logs kafka
docker compose logs schema-registry
```

Use the exact service names from the stack.

### Step 6 — Check individual services

For PostgreSQL:

```bash
docker compose exec postgres pg_isready
```

For Redis, if `redis-cli` is present:

```bash
docker compose exec redis redis-cli ping
```

For Kafka and Schema Registry, perform service-specific connectivity/readiness checks appropriate to the stack's Kafka distribution.

### Step 7 — Verify internal service connectivity

Use a service or diagnostic client inside the Compose network.

Remember:

```text
container → service name → container port
```

not:

```text
container → localhost → host-published port
```

### Step 8 — Verify persistent storage

Inspect:

```bash
docker volume ls
```

and the relevant service container:

```bash
docker inspect <container>
```

Confirm that expected persistent services have the expected mounts.

### Step 9 — Verify configuration

Use:

```bash
docker compose config
```

Then inspect runtime configuration where necessary.

### Step 10 — Create test data

For PostgreSQL, create a small test table:

```sql
CREATE TABLE lab_test (
    id INTEGER PRIMARY KEY,
    message TEXT NOT NULL
);

INSERT INTO lab_test (id, message)
VALUES (1, 'compose-persistence-test');
```

Verify:

```sql
SELECT * FROM lab_test;
```

### Step 11 — Stop the stack

```bash
docker compose stop
```

### Step 12 — Start it again

```bash
docker compose start
```

### Step 13 — Verify data persistence

Check PostgreSQL again:

```sql
SELECT * FROM lab_test;
```

Expected result:

```text
1 | compose-persistence-test
```

The exact display depends on the client.

### Step 14 — Perform a targeted restart

Restart PostgreSQL:

```bash
docker compose restart postgres
```

Then verify:

```bash
docker compose exec postgres pg_isready
```

### Step 15 — Bring the stack down

```bash
docker compose down
```

### Step 16 — Bring it back up

```bash
docker compose up -d
```

### Step 17 — Verify what persisted

Check PostgreSQL data again.

This reinforces:

```text
container removal
≠
volume removal
```

### Step 18 — Perform a deliberate full reset

Only in the disposable lab:

```bash
docker compose down -v
```

Then:

```bash
docker compose up -d
```

Verify that the intentionally removed volume state is no longer present.

### Step 19 — Document the stack

Produce a local operational note containing:

```text
Services
Ports
Volumes
Dependencies
Readiness checks
Troubleshooting commands
```

### Step 20 — Explain the stack without commands

You should be able to explain:

```text
What each service does
        ↓
How services communicate
        ↓
Which ports are host-facing
        ↓
Which data persists
        ↓
Which services depend on others
        ↓
How readiness is verified
        ↓
How failures are diagnosed
```

---

## 44. Stack Operations Checklist

Use this checklist whenever you begin operating a new Compose Data Engineering stack.

```text
[ ] Understand the services
[ ] Know the service names
[ ] Know host-facing ports
[ ] Know internal service ports
[ ] Know persistent volumes
[ ] Know service dependencies
[ ] Start stack
[ ] Check stack status
[ ] Check logs
[ ] Check readiness
[ ] Test connectivity
[ ] Verify persistence
[ ] Restart individual services when appropriate
[ ] Stop stack safely
[ ] Understand down vs down -v
[ ] Verify final state
```

---

## 45. Practice Questions

### Beginner

1. What is Docker Compose?
2. What problem does Compose solve for Data Engineering?
3. What is a Compose stack?
4. What is a service?
5. How does a service differ from a container?
6. Why is Compose useful for multi-container local development?
7. What does `docker compose up -d` do?
8. Why does a running container not necessarily mean its application is ready?

### Intermediate

1. How do services communicate inside a Compose network?
2. What is the difference between a service name and a container name?
3. What is the difference between a host port and a container/service port?
4. If PostgreSQL is mapped as `5433:5432`, which port should a container use?
5. How do you inspect stack status?
6. How do you inspect logs for one service?
7. How do you execute a command inside a Compose service?
8. What does `docker compose stop` do?
9. What does `docker compose down` do?
10. Why can named volumes survive container removal?
11. What does `docker compose config` help you understand?

### Advanced

1. Why does `depends_on` not necessarily mean application readiness?
2. How would you troubleshoot a stack where Kafka is running but Schema Registry is failing?
3. How would you preserve PostgreSQL data while recreating its container?
4. What happens when `docker compose down -v` is used?
5. How would you design a reproducible local Data Engineering stack?
6. How would you troubleshoot a service that repeatedly restarts?
7. Why is service-specific troubleshooting often better than restarting the entire stack?
8. How would you determine whether a failure is caused by configuration, networking, storage, or dependency readiness?
9. Why can a downstream application error be caused by an upstream service?
10. How would you verify that a Compose stack is actually usable rather than merely running?

---

## 46. Interview Practice

### 1. What is Docker Compose?

**Strong answer:**

Docker Compose is a tool for defining and operating related services as a multi-container application or stack. In Data Engineering, it is particularly useful for reproducible local environments containing services such as PostgreSQL, Kafka, MinIO, Redis, and Schema Registry.

---

### 2. Why is Docker Compose useful for Data Engineering?

**Strong answer:**

Data Engineering workflows commonly depend on several infrastructure services simultaneously. Compose provides a consistent operational model for starting, stopping, inspecting, networking, configuring, and persisting those services as one local environment.

---

### 3. What is a Compose service?

**Strong answer:**

A service is a logical application or infrastructure component defined in the Compose configuration. It is not exactly the same thing as the runtime container. Compose uses the service identity to operate the corresponding container workload.

---

### 4. How do services communicate with each other?

**Strong answer:**

Services normally communicate through a Compose project network using service names as DNS identities and the internal container ports. They generally do not need to use host-published ports for internal communication.

---

### 5. What is the difference between service ports and published host ports?

**Strong answer:**

A service's container port is the port the application listens on inside the container. A published host port exposes that service through the host. For example, `5433:5432` means the host uses `localhost:5433`, while another container normally uses `postgres:5432`.

---

### 6. What happens when you run `docker compose up -d`?

**Strong answer:**

Compose resolves the stack configuration, creates required networks/volumes as needed, creates or reuses service containers, and starts them in detached mode. It does not automatically prove that every application has completed initialization and is ready.

---

### 7. What is the difference between `docker compose stop` and `docker compose down`?

**Strong answer:**

`stop` stops the service containers while leaving them available to start again. `down` removes the Compose project containers and network. Named volumes normally remain after `down`.

---

### 8. What is the difference between `docker compose down` and `docker compose down -v`?

**Strong answer:**

`down` normally removes project containers and the Compose network while retaining named volumes. `down -v` additionally removes project volumes, so it can destroy persistent database or object-store data.

---

### 9. How do you inspect Compose services?

**Strong answer:**

Use:

```bash
docker compose ps
```

and, when deeper runtime details are required, combine it with:

```bash
docker ps
docker inspect <container>
```

---

### 10. How do you inspect logs for one service?

```bash
docker compose logs <service>
```

For example:

```bash
docker compose logs postgres
```

To follow them:

```bash
docker compose logs -f postgres
```

---

### 11. How do you execute commands inside a Compose service?

Use:

```bash
docker compose exec <service> <command>
```

For example:

```bash
docker compose exec postgres pg_isready
```

---

### 12. Why doesn't `depends_on` automatically guarantee readiness?

**Strong answer:**

A dependency declaration expresses a service relationship or startup ordering. The dependency's application may still be initializing after its container has started. Readiness must therefore be established using an application-specific health or connectivity check.

---

### 13. How would you troubleshoot PostgreSQL inside a Compose stack?

**Strong answer:**

I would first identify the service state with `docker compose ps`, inspect PostgreSQL logs, inspect the resolved configuration, verify the PostgreSQL readiness state with `pg_isready`, check the network endpoint and credentials, inspect the volume if data is involved, and then reproduce and verify the fix.

---

### 14. How would you troubleshoot Kafka and Schema Registry?

**Strong answer:**

I would identify which service is actually failing, inspect Schema Registry logs, then inspect Kafka because Schema Registry depends on Kafka. I would verify Kafka's actual broker/client readiness and endpoint configuration before treating the downstream Schema Registry error as the root cause.

---

### 15. How would you preserve database data during service recreation?

**Strong answer:**

Keep PostgreSQL data on a named volume mounted to the database data directory. Recreating the container does not inherently remove the named volume. I would verify the mount and volume before performing any destructive teardown.

---

### 16. How would you design a local Data Engineering stack?

**Strong answer:**

I would define the required services, establish a clear internal network, publish only host-facing ports, attach persistent volumes to stateful services, configure services consistently, document dependencies and readiness checks, and provide a repeatable Compose lifecycle for onboarding and testing.

---

### 17. When would you restart one service instead of the entire stack?

**Strong answer:**

When one service has a localized failure and its dependencies are healthy. Restarting only that service minimizes disruption and preserves the ability to reason about the incident.

---

### 18. What are the limitations of Docker Compose compared with production orchestration platforms?

**Strong answer:**

Compose is highly useful for local and development multi-container environments, but production platforms can provide broader orchestration capabilities such as cluster scheduling, high availability, rolling deployments, service placement, autoscaling, and other operational controls. Compose should not be treated as a Kubernetes replacement.

---

## 47. Final Knowledge Check

Before considering this topic complete, you should be able to answer all of the following without looking at the module.

1. What problem does Docker Compose solve?
2. What is a Compose project?
3. What is a Compose service?
4. How does a service differ from a container?
5. How do services communicate?
6. What is the difference between a service port and a host-published port?
7. What happens when `docker compose up -d` is executed?
8. How do you inspect stack status?
9. How do you inspect logs for one service?
10. How do you execute commands inside a service?
11. What is the difference between started and ready?
12. What does `depends_on` accomplish?
13. Why is dependency ordering not the same as readiness?
14. What happens with `docker compose stop`?
15. What happens with `docker compose down`?
16. What is the danger of `docker compose down -v`?
17. How do Compose volumes provide persistence?
18. How does service configuration reach containers?
19. How would you troubleshoot a failed PostgreSQL service?
20. How would you troubleshoot Kafka and Schema Registry?
21. How would you troubleshoot a service that repeatedly restarts?
22. How would you preserve persistent data while recreating containers?
23. How would you operate a complete local Data Engineering stack reproducibly?

### Practical mastery test

You should also be able to perform this sequence without following a command-by-command tutorial:

```text
Read stack
   ↓
Identify services
   ↓
Identify ports
   ↓
Identify volumes
   ↓
Identify dependencies
   ↓
Start stack
   ↓
Check status
   ↓
Check readiness
   ↓
Test service connectivity
   ↓
Inspect logs
   ↓
Restart one service
   ↓
Stop stack
   ↓
Start stack
   ↓
Verify persistence
   ↓
Bring stack down
   ↓
Explain what remains
   ↓
Perform an intentional disposable reset
```

---

## 48. Module Completion Checklist

```text
[ ] I understand why Data Engineering labs need multiple containers.
[ ] I understand what Docker Compose is.
[ ] I understand Compose projects.
[ ] I understand services versus containers.
[ ] I can read an existing Compose stack.
[ ] I understand the `docker compose` command style.
[ ] I understand service names.
[ ] I understand Compose networking operationally.
[ ] I can distinguish host ports from container ports.
[ ] I understand Compose volume usage.
[ ] I understand Compose environment configuration.
[ ] I can start a stack.
[ ] I can inspect stack status.
[ ] I can inspect service logs.
[ ] I can execute commands inside services.
[ ] I understand started versus ready.
[ ] I understand service dependencies.
[ ] I understand why dependency order is not readiness.
[ ] I can stop and start a stack.
[ ] I can bring a stack down safely.
[ ] I understand the danger of `down -v`.
[ ] I can restart one service without restarting everything.
[ ] I can inspect resolved configuration.
[ ] I can troubleshoot stack startup failures.
[ ] I can troubleshoot dependency failures.
[ ] I can troubleshoot networking mistakes.
[ ] I can troubleshoot storage/persistence problems.
[ ] I can troubleshoot configuration problems.
[ ] I can trace downstream failures to upstream dependencies.
[ ] I can operate PostgreSQL, MinIO, Kafka, Schema Registry, and Redis as a local stack.
[ ] I can preserve persistent data during normal container lifecycle operations.
[ ] I can perform a deliberate disposable full reset.
[ ] I can explain the complete Compose stack architecture.
[ ] I can document services, ports, volumes, dependencies, and readiness checks.
```

---

## Roadmap Coverage Audit

This module implements the supplied Topic 07 specification across the following required areas:

| Roadmap area | Covered |
|---|---|
| Why multi-container Data Engineering needs Compose | Yes |
| Compose definition and mental model | Yes |
| Compose V2 / `docker compose` | Yes |
| Compose projects | Yes |
| Reading an existing Compose stack | Yes |
| Services | Yes |
| Compose networking | Yes |
| Host ports vs service ports | Yes |
| Compose volumes | Yes |
| Environment configuration | Yes |
| Starting stacks | Yes |
| Stack status | Yes |
| Stack logs | Yes |
| `docker compose exec` | Yes |
| Started vs ready | Yes |
| Dependencies | Yes |
| Startup order vs readiness | Yes |
| Stopping stacks | Yes |
| Bringing stacks down | Yes |
| `down -v` destructive reset | Yes |
| Service recreation | Yes |
| Service-specific operations | Yes |
| Stack inspection/validation | Yes |
| PostgreSQL / MinIO / Kafka / Schema Registry / Redis stack | Yes |
| Local Data Engineering lab | Yes |
| Lifecycle comparison | Yes |
| Persistence/reset strategies | Yes |
| Compose troubleshooting | Yes |
| Dependency troubleshooting | Yes |
| Network troubleshooting | Yes |
| Storage troubleshooting | Yes |
| Configuration troubleshooting | Yes |
| Startup failure scenario | Yes |
| Readiness failure scenario | Yes |
| Break/fix laboratory | Yes |
| Real-world scenarios | Yes |
| Operational best practices | Yes |
| Command reference | Yes |
| Common mistakes | Yes |
| Mental models | Yes |
| Architecture diagrams | Yes |
| Hands-on lab | Yes |
| Operations checklist | Yes |
| Practice questions | Yes |
| Interview practice | Yes |
| Final knowledge check | Yes |
| Completion checklist | Yes |

### Technical audit

The module intentionally reinforces these operational distinctions:

```text
Compose project
≠
individual service
≠
individual container
```

```text
Host port
≠
container/service port
```

```text
Container running
≠
application ready
```

```text
depends_on
≠
application readiness
```

```text
Container lifecycle
≠
volume lifecycle
```

```text
docker compose down
≠
docker compose down -v
```

### Scope audit

This module does **not** become a complete course on:

- Docker networking;
- Docker volumes;
- environment variables;
- container troubleshooting;
- resource limits;
- cleanup and housekeeping;
- Docker Desktop;
- WSL2;
- Dockerfile authoring;
- image building;
- Kubernetes;
- production cluster orchestration.

Those subjects are used as prerequisites or operational dependencies only.

The main focus remains:

> **Operating multi-container Compose stacks.**

---

## Final Professional Takeaway

A production-minded Data Engineer should not think of Docker Compose as merely a shorter way to type several `docker run` commands.

The stronger mental model is:

```text
Compose
   ↓
multi-service environment
   ↓
service relationships
   ↓
network
   ↓
persistent storage
   ↓
configuration
   ↓
dependencies
   ↓
readiness
   ↓
lifecycle
   ↓
troubleshooting
   ↓
reproducible Data Engineering lab
```

The goal is not simply to know:

```bash
docker compose up -d
```

The goal is to understand what happens after that command.

You should be able to answer:

```text
Which services started?
Which are actually ready?
How do they communicate?
Which ports are host-facing?
Which data persists?
Which services depend on others?
Which service is failing?
What evidence proves the failure?
What is the smallest safe fix?
How do I verify the fix?
```

That is the difference between **running Compose** and **operating a Compose-based Data Engineering environment professionally**.
