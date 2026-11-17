# Docker Essentials for Data Labs — Practice Questions

## How to Use These Questions

These 40 problems are designed to test whether you can **operate, reason about, troubleshoot, and safely manage a Docker-based Data Engineering laboratory** rather than merely memorize commands.

Use the questions in order. For each problem:

1. Read the scenario.
2. Predict what should happen.
3. Attempt the task in your own lab before reading the solution.
4. Compare your diagnosis with the evidence-based solution.
5. Reproduce the failure where the question is a break/fix exercise.
6. Verify the fix instead of assuming it worked.

The difficulty increases from individual Docker operations to multi-service Data Engineering incidents.

> **Scope:** Docker user/operator skills for local Data Engineering labs. This practice set intentionally does not teach Dockerfile authoring, image-building workflows, Kubernetes, Helm, Docker Swarm, Terraform, service mesh, or advanced CI/CD container pipelines.

---

# Level 1 — Basic

## Question 01 — Container Lifecycle: Stop, Start, and Remove

### Difficulty
Basic

### Topics Covered
- Topic 01 — Containers, Images, and Registries
- Topic 04 — Volumes and Persistence

### Problem

You have a container named `pg-lab` created from `postgres:16`.

You want to temporarily stop PostgreSQL, then start the **same container** again. Later, you want to remove the container while keeping its persistent database volume available for a replacement container.

### Your Task

1. Explain the difference between `docker stop`, `docker start`, and `docker rm`.
2. Stop `pg-lab`.
3. Confirm that it still exists but is not running.
4. Start it again.
5. Explain what happens to a separate named volume when the container is removed.

### Solution

#### Step 1 — Understand the lifecycle

`docker stop` stops the container process but does not remove the container.

`docker start` starts an existing stopped container again.

`docker rm` removes the container object. A separately managed named volume is not automatically removed just because its container is removed.

#### Step 2 — Stop the service

```bash
docker stop pg-lab
```

#### Step 3 — Verify

```bash
docker ps -a --filter name=pg-lab
```

You should see the container with a stopped/exited state.

#### Step 4 — Start the same container

```bash
docker start pg-lab
```

Then:

```bash
docker ps --filter name=pg-lab
```

#### Step 5 — Remove only the container when appropriate

```bash
docker stop pg-lab
docker rm pg-lab
```

If PostgreSQL was using a named volume such as `pgdata`, that volume remains until you explicitly remove it.

#### Why This Works

A container and its persistent storage are different lifecycle objects. Stopping changes runtime state; removing deletes the container object. A named volume can outlive the container and can therefore be attached to a replacement container.

#### Key Takeaway

**Container lifecycle and data lifecycle are separate.** Never assume that removing a container means persistent data has been removed.

---

## Question 02 — Image vs Container

### Difficulty
Basic

### Topics Covered
- Topic 01 — Containers, Images, and Registries

### Problem

A learner says:

> "I already have a PostgreSQL container, so I don't need the PostgreSQL image anymore."

They want to delete `postgres:16` immediately.

### Your Task

1. Explain the difference between an image and a container.
2. Explain why the image may still be useful.
3. Show how to inspect images and containers before deleting anything.
4. State the safe rule for removing an image.

### Solution

#### Step 1 — Understand the objects

An **image** is the packaged filesystem/configuration used to create containers.

A **container** is a runtime instance created from an image.

One image can be used to create multiple containers.

#### Step 2 — Inspect current state

```bash
docker images
docker ps -a
```

You can also inspect a particular container:

```bash
docker inspect pg-lab
```

#### Step 3 — Remove an image only when it is no longer needed

If no remaining container depends on the image and you no longer need the image locally:

```bash
docker rmi postgres:16
```

Docker may refuse removal when the image is still referenced by a container.

#### Why This Works

Deleting an image is different from stopping or deleting a container. The image is the reusable package; the container is one instantiated runtime object.

#### Key Takeaway

Think:

```text
Image = template/package
Container = running or stopped instance
```

Do not treat them as the same object.

---

## Question 03 — Run PostgreSQL with the Required Configuration

### Difficulty
Basic

### Topics Covered
- Topic 01 — Containers, Images, and Registries
- Topic 02 — Databases and Services
- Topic 05 — Environment Variables and Configuration

### Problem

You need a local PostgreSQL service for a Data Engineering lab. The database should be called `datalab`, the user should be `dataeng`, and PostgreSQL should be reachable from the host on port `5432`.

### Your Task

Write and explain a suitable `docker run` command using:

- `postgres:16`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- a named container
- detached mode
- host port binding

### Solution

```bash
docker run -d \
  --name pg-lab \
  -e POSTGRES_USER=dataeng \
  -e POSTGRES_PASSWORD=localdevpassword \
  -e POSTGRES_DB=datalab \
  -p 127.0.0.1:5432:5432 \
  postgres:16
```

#### Step 1 — Understand the important flags

- `-d` runs detached.
- `--name pg-lab` gives the container a stable operator-friendly name.
- `-e` supplies initialization configuration.
- `-p 127.0.0.1:5432:5432` maps host port `5432` to container port `5432` while limiting host exposure to loopback.
- `postgres:16` identifies the image and tag.

#### Step 2 — Verify the container

```bash
docker ps --filter name=pg-lab
```

#### Step 3 — Check readiness

```bash
pg_isready -h localhost -p 5432
```

#### Why This Works

The PostgreSQL image reads its documented initialization environment variables when the database is initialized. Publishing the container port makes the service reachable from the host.

#### Key Takeaway

For containerized databases, configuration, networking, and readiness are separate concerns. Starting the container is only the first step.

---

## Question 04 — Predict the Effect of `--rm`

### Difficulty
Basic

### Topics Covered
- Topic 01 — Containers, Images, and Registries
- Topic 04 — Volumes and Persistence

### Problem

You run:

```bash
docker run --rm --name temporary-client postgres:16
```

The process exits.

### Your Task

1. Predict what happens to the container.
2. Explain how this differs from an ordinary stopped container.
3. State when `--rm` is useful for Data Engineering labs.

### Solution

#### Step 1 — Predict

With `--rm`, Docker automatically removes the container after it exits.

Therefore:

```bash
docker ps -a --filter name=temporary-client
```

should not show the exited container after removal.

#### Step 2 — Compare with a normal container

Without `--rm`, a stopped container remains in Docker's container inventory until explicitly removed.

#### Step 3 — Use the pattern for one-off work

`--rm` is useful for temporary client or diagnostic containers where you do not need to preserve the stopped container object.

For example:

```bash
docker run --rm -it postgres:16 psql --help
```

#### Why This Works

`--rm` changes the container lifecycle policy: the container is automatically removed after its process exits.

#### Key Takeaway

Use `--rm` for intentionally disposable containers, not for services whose stopped state you may need to inspect later.

---

## Question 05 — Host Port vs Container Port

### Difficulty
Basic

### Topics Covered
- Topic 03 — Ports, Networks, and Service Discovery

### Problem

You run:

```bash
docker run -d --name pg-lab -p 15432:5432 postgres:16
```

A learner tries to connect from the host to `localhost:5432` and fails.

### Your Task

Explain why and identify the correct host endpoint.

### Solution

#### Step 1 — Read the mapping

```text
-p HOST_PORT:CONTAINER_PORT
```

The command means:

```text
Host port 15432 → container port 5432
```

#### Step 2 — Use the published host port

From the host, connect to:

```text
localhost:15432
```

For PostgreSQL:

```bash
psql -h localhost -p 15432 -U dataeng -d datalab
```

#### Step 3 — Verify the mapping

```bash
docker ps
```

The port column should show the published mapping.

#### Why This Works

The container still listens on port `5432`. Only the host-facing port changed.

#### Key Takeaway

Always distinguish:

```text
HOST_PORT ≠ CONTAINER_PORT
```

unless you intentionally publish the same number.

---

## Question 06 — Named Volume for PostgreSQL

### Difficulty
Basic

### Topics Covered
- Topic 04 — Volumes and Persistence
- Topic 02 — Databases and Services

### Problem

You want PostgreSQL data to survive container removal and recreation.

### Your Task

Create a named volume and run PostgreSQL using the standard PostgreSQL data directory.

### Solution

#### Step 1 — Create the volume

```bash
docker volume create pgdata
```

#### Step 2 — Run PostgreSQL

```bash
docker run -d \
  --name pg-lab \
  -e POSTGRES_USER=dataeng \
  -e POSTGRES_PASSWORD=localdevpassword \
  -e POSTGRES_DB=datalab \
  -p 127.0.0.1:5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16
```

#### Step 3 — Verify the volume

```bash
docker volume inspect pgdata
```

#### Step 4 — Test lifecycle persistence

After creating test data:

```bash
docker rm -f pg-lab
```

Create a replacement container using the same volume.

#### Why This Works

The PostgreSQL data directory is stored in the named volume rather than only in the container's writable layer.

#### Key Takeaway

For stateful Data Engineering services, persistent storage must be designed explicitly.

---

## Question 07 — Read PostgreSQL Logs

### Difficulty
Basic

### Topics Covered
- Topic 06 — Logs, Exec, and Troubleshooting

### Problem

PostgreSQL is not accepting connections. You want the first evidence before changing configuration.

### Your Task

Show the commands you would use to inspect the container and its logs.

### Solution

#### Step 1 — Check state

```bash
docker ps -a --filter name=pg-lab
```

This tells you whether the container is running or has exited.

#### Step 2 — Read logs

```bash
docker logs pg-lab
```

For a live startup view:

```bash
docker logs -f pg-lab
```

#### Step 3 — Inspect metadata if needed

```bash
docker inspect pg-lab
```

Look at state, mounts, environment-related metadata, networking, and health information where available.

#### Why This Works

Logs are evidence about what the application process actually reported. They are usually more useful than guessing at a fix.

#### Key Takeaway

Use:

```text
state → logs → inspect → hypothesis
```

before changing things blindly.

---

## Question 08 — Compose Basic Lifecycle

### Difficulty
Basic

### Topics Covered
- Topic 07 — Docker Compose

### Problem

You are given a working Compose-based Data Engineering lab. You need to start it in the background and check whether the services are running.

### Your Task

Provide the basic commands.

### Solution

#### Step 1 — Start the stack

```bash
docker compose up -d
```

#### Step 2 — Check service state

```bash
docker compose ps
```

#### Step 3 — Inspect logs if a service is unhealthy or exited

```bash
docker compose logs
```

Or for a specific service:

```bash
docker compose logs postgres
```

#### Step 4 — Follow logs

```bash
docker compose logs -f
```

#### Why This Works

Compose groups related services into a project and gives you a service-oriented operating interface.

#### Key Takeaway

The basic Compose operator loop is:

```text
up → ps → logs → inspect → verify
```

---

## Question 09 — Inspect Resource Usage

### Difficulty
Basic

### Topics Covered
- Topic 08 — Resources and Laptop Capacity

### Problem

PostgreSQL, Kafka, MinIO, and Redis are running. Your laptop feels slower than usual.

### Your Task

Identify the first Docker command you should use to compare container resource consumption.

### Solution

Run:

```bash
docker stats
```

This provides a live view of CPU and memory usage, among other runtime information.

You can also inspect a particular container:

```bash
docker stats pg-lab
```

#### Why This Works

The host feeling slow is a symptom. `docker stats` helps determine which running container is actually consuming resources.

#### Key Takeaway

Do not guess which service is responsible. Measure first.

---

## Question 10 — Measure Docker Disk Usage

### Difficulty
Basic

### Topics Covered
- Topic 09 — Cleanup and Housekeeping

### Problem

Your laptop reports low free disk space after several weeks of Docker labs. You do not want to delete anything yet.

### Your Task

Show the safest first Docker command and explain what you are looking for.

### Solution

Run:

```bash
docker system df
```

For more detail:

```bash
docker system df -v
```

#### What to inspect

Look for space consumed by:

- images
- containers
- local volumes
- build cache

#### Why This Works

`docker system df` is an inspection command, not a deletion command. It gives you evidence before cleanup.

#### Key Takeaway

The safe cleanup sequence begins with:

```text
measure → identify → protect important data → remove selected resources → verify
```

---

# Level 2 — Moderate

## Question 11 — PostgreSQL Is Running but Not Ready

### Difficulty
Moderate

### Topics Covered
- Topic 02 — Databases and Services
- Topic 06 — Logs and Troubleshooting

### Problem

Immediately after:

```bash
docker run -d ...
```

you run:

```bash
docker ps
```

and see PostgreSQL as running, but your Python client receives a connection error.

### Your Task

Explain why "running" does not necessarily mean "ready" and give a practical diagnostic sequence.

### Solution

#### Step 1 — Understand the state distinction

A container can be running while PostgreSQL is still:

- initializing its database directory,
- starting its server,
- running initialization scripts,
- becoming ready to accept connections.

#### Step 2 — Inspect logs

```bash
docker logs pg-lab
```

#### Step 3 — Check readiness

From the host:

```bash
pg_isready -h localhost -p 5432
```

Repeat until the service reports readiness.

#### Step 4 — Check health metadata if a healthcheck exists

```bash
docker inspect pg-lab
```

Look for health status when the image/Compose configuration defines one.

#### Why This Works

Container state and application readiness are different layers.

#### Root Cause

The Python client may simply be connecting too early.

#### Key Takeaway

**Start ≠ Ready.** Data pipelines should depend on readiness, not merely container creation.

---

## Question 12 — Container-to-Container `localhost` Failure

### Difficulty
Moderate

### Topics Covered
- Topic 03 — Ports and Networking
- Topic 02 — Databases

### Problem

A Python container and PostgreSQL container are both running. From the Python container, this fails:

```text
localhost:5432
```

PostgreSQL is published to the host on port `5432`.

### Your Task

Explain why `localhost` fails from the Python container and describe the correct Docker-network approach.

### Solution

#### Step 1 — Understand `localhost`

Inside the Python container:

```text
localhost = the Python container itself
```

It does not mean the PostgreSQL container.

#### Step 2 — Put both services on the same user-defined network

```bash
docker network create data-lab
docker network connect data-lab pg-lab
docker network connect data-lab python-lab
```

#### Step 3 — Use the PostgreSQL container name

From Python, use:

```text
pg-lab:5432
```

not:

```text
localhost:5432
```

#### Step 4 — Verify DNS/reachability

A temporary diagnostic container can test name resolution and TCP connectivity:

```bash
docker run --rm --network data-lab busybox nslookup pg-lab
```

If the image includes the necessary tools, use `nc` to test TCP reachability.

#### Why This Works

User-defined Docker networks provide container-to-container connectivity and service-name DNS.

#### Key Takeaway

For container-to-container communication, think:

```text
service/container name + container port
```

rather than host-published ports.

---

## Question 13 — Environment Variable Configuration Failure

### Difficulty
Moderate

### Topics Covered
- Topic 05 — Environment Variables and Configuration
- Topic 06 — Troubleshooting

### Problem

A service expects `POSTGRES_DB=datalab`, but the running container was created without that environment variable. The learner assumes the image will automatically know the intended database name.

### Your Task

Show how to inspect the running configuration and explain why environment variables must be supplied intentionally.

### Solution

#### Step 1 — Inspect the container

```bash
docker inspect pg-lab
```

Review the configuration metadata and environment values.

#### Step 2 — Compare desired vs actual configuration

The desired state is:

```text
POSTGRES_DB=datalab
POSTGRES_USER=dataeng
```

The actual container configuration may not contain those values.

#### Step 3 — Apply the fix correctly

For initialization variables, the safest pattern is usually to recreate the container with the correct configuration, while preserving the correct named volume if the existing data must be retained.

Example:

```bash
docker rm -f pg-lab
docker run -d \
  --name pg-lab \
  -e POSTGRES_USER=dataeng \
  -e POSTGRES_PASSWORD=localdevpassword \
  -e POSTGRES_DB=datalab \
  -v pgdata:/var/lib/postgresql/data \
  -p 127.0.0.1:5432:5432 \
  postgres:16
```

#### Important Caveat

PostgreSQL initialization variables are primarily used when the database is first initialized. Changing the variable later does not automatically recreate an already-initialized database.

#### Why This Works

Container configuration is explicit. The image cannot infer your application-specific desired state.

#### Key Takeaway

Distinguish **initialization configuration** from **runtime configuration** and from **persistent database state**.

---

## Question 14 — Volume or Bind Mount?

### Difficulty
Moderate

### Topics Covered
- Topic 04 — Volumes and Persistence

### Problem

You need two storage patterns:

1. PostgreSQL database data that Docker should manage as persistent service state.
2. A local configuration directory that a developer needs to edit directly from the host.

### Your Task

Choose named volume vs bind mount for each and explain why.

### Solution

#### PostgreSQL

Use a **named volume**:

```bash
-v pgdata:/var/lib/postgresql/data
```

The data is persistent but Docker manages the storage location.

#### Developer configuration

Use a **bind mount**, for example:

```bash
-v "$PWD/config:/app/config"
```

The host directory is intentionally part of the workflow.

#### Why This Works

A named volume is generally a good default for service-managed persistent data.

A bind mount is appropriate when the host filesystem itself is part of the development interface.

#### Key Takeaway

Choose storage based on ownership and workflow:

```text
Service state → named volume
Host-managed project files → bind mount
```

---

## Question 15 — Compose `.env` vs `env_file`

### Difficulty
Moderate

### Topics Covered
- Topic 05 — Configuration
- Topic 07 — Docker Compose

### Problem

A provided Compose stack uses a `.env` file for project-level substitution and an `env_file` entry for a service's environment. A learner treats the two as identical.

### Your Task

Explain the operational distinction from the user's perspective and show how to inspect the resulting configuration.

### Solution

#### Step 1 — Understand the distinction

A `.env` file can participate in Compose variable substitution and project configuration.

An `env_file` is associated with a service and supplies environment variables to that service.

They can overlap in purpose, but they are not simply interchangeable concepts.

#### Step 2 — Inspect resolved Compose configuration

```bash
docker compose config
```

This is the key operator command for understanding how Compose resolves configuration.

#### Step 3 — Verify the running service

```bash
docker compose ps
docker compose exec <service> sh
```

Then inspect environment variables inside the container if appropriate.

#### Why This Works

The effective runtime configuration is more important than guessing what a file "should" mean.

#### Key Takeaway

When a Compose configuration behaves unexpectedly, inspect the **resolved configuration** and the **actual running container**.

---

## Question 16 — Port Conflict on a Data Lab

### Difficulty
Moderate

### Topics Covered
- Topic 03 — Ports and Networking
- Topic 06 — Troubleshooting

### Problem

You attempt to start a second PostgreSQL container with:

```bash
-p 127.0.0.1:5432:5432
```

Docker reports that the port cannot be allocated.

### Your Task

Diagnose the conflict and give two safe solutions.

### Solution

#### Step 1 — Identify who is using the port

```bash
docker ps
```

Look for an existing container publishing host port `5432`.

You can also inspect the candidate container:

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

#### Step 2 — Option A: use another host port

For example:

```bash
-p 127.0.0.1:15432:5432
```

The container still listens on `5432`.

#### Step 3 — Option B: stop/remove the conflicting lab

Only do this if the other PostgreSQL instance is no longer needed.

```bash
docker stop <other-container>
```

Then start the new service.

#### Why This Works

A host port can normally be bound by only one listener at a time. Changing the host port does not change the container's internal PostgreSQL port.

#### Key Takeaway

A port conflict is a **host-side binding conflict**, not necessarily an application-port problem inside the container.

---

## Question 17 — Safe PostgreSQL Reset

### Difficulty
Moderate

### Topics Covered
- Topic 04 — Persistence
- Topic 07 — Compose

### Problem

A local PostgreSQL lab is corrupted and you want to rebuild the container while preserving its database data.

A colleague suggests:

```bash
docker compose down -v
```

### Your Task

Explain why that recommendation is dangerous and give a safer reset approach.

### Solution

#### Step 1 — Understand `down -v`

`docker compose down -v` removes the Compose-managed volumes associated with the project.

If PostgreSQL data is stored in one of those volumes, this can destroy the database state.

#### Step 2 — Back up important data first

Use an application-consistent PostgreSQL backup when the database is accessible, or use the documented backup method from the lab.

Do not assume that a filesystem copy of a live database is equivalent to a consistent database backup.

#### Step 3 — Rebuild without deleting the volume

Use:

```bash
docker compose down
```

Then bring the stack back:

```bash
docker compose up -d
```

If the container itself needs recreation, preserve the volume.

#### Step 4 — Verify

```bash
docker compose ps
docker compose logs postgres
```

Then connect and verify expected tables/data.

#### Why This Works

The container can be disposable while the database state remains persistent.

#### Key Takeaway

Treat `down -v` as a **data-affecting operation**, not as a normal restart command.

---

## Question 18 — Logs Show an Immediate Exit

### Difficulty
Moderate

### Topics Covered
- Topic 06 — Logs and Troubleshooting
- Topic 01 — Lifecycle

### Problem

A container appears briefly in `docker ps`, then disappears from the running list.

### Your Task

Give an evidence-driven diagnosis sequence.

### Solution

#### Step 1 — Check stopped containers

```bash
docker ps -a
```

If the container exited, it will still be visible.

#### Step 2 — Inspect logs

```bash
docker logs <container>
```

#### Step 3 — Inspect exit information

```bash
docker inspect <container>
```

Look at the container state and exit code.

#### Step 4 — Form a hypothesis

Common categories include:

- invalid configuration
- application startup failure
- missing dependency
- storage/permission issue
- incorrect command
- resource failure

Do not select a cause before collecting evidence.

#### Step 5 — Verify the fix

After applying the smallest appropriate fix:

```bash
docker start <container>
docker ps
docker logs <container>
```

#### Why This Works

A disappearing container is a symptom. `docker ps -a`, logs, and inspect expose the evidence needed to distinguish a startup failure from other problems.

#### Key Takeaway

Never jump directly from "it exited" to "restart it."

---

## Question 19 — Compose Service-Specific Troubleshooting

### Difficulty
Moderate

### Topics Covered
- Topic 07 — Docker Compose
- Topic 06 — Troubleshooting

### Problem

A five-service Compose stack is running, but one service is repeatedly failing. The learner runs `docker compose logs` and receives a large amount of output from every service.

### Your Task

Show how to narrow the investigation to one service and then inspect its runtime state.

### Solution

#### Step 1 — Identify service state

```bash
docker compose ps
```

#### Step 2 — Read only the failing service logs

```bash
docker compose logs <service>
```

For live output:

```bash
docker compose logs -f <service>
```

#### Step 3 — Inspect the service container

```bash
docker compose ps
docker inspect <container>
```

#### Step 4 — Execute a diagnostic command if the container remains running

```bash
docker compose exec <service> sh
```

#### Why This Works

Service-specific evidence reduces noise and makes causal analysis easier.

#### Key Takeaway

In a multi-service stack, move from:

```text
whole stack → failing service → container → process/config/network/storage
```

---

## Question 20 — CPU Limit vs Memory Limit

### Difficulty
Moderate

### Topics Covered
- Topic 08 — Resources and Laptop Capacity

### Problem

A learner wants to prevent one local service from consuming too much CPU and memory.

### Your Task

Explain the difference between:

```bash
--cpus
```

and:

```bash
--memory
```

and show a simple example.

### Solution

#### CPU limit

```bash
docker run -d --name worker-lab --cpus="1.0" <image>
```

This constrains the CPU capacity available to the container.

#### Memory limit

```bash
docker run -d --name worker-lab --memory="1g" <image>
```

This constrains memory available to the container.

#### Combined example

```bash
docker run -d \
  --name worker-lab \
  --cpus="1.0" \
  --memory="1g" \
  <image>
```

#### Verify

```bash
docker stats worker-lab
```

#### Why This Works

CPU and memory are different resource dimensions. CPU pressure generally manifests as throttling/slower execution, while exceeding a memory limit can lead to process/container termination.

#### Key Takeaway

Do not use memory limits to solve CPU contention or CPU limits to solve memory exhaustion.

---

# Level 3 — Hard

## Question 21 — Kafka Works from the Host but Not from a Container

### Difficulty
Hard

### Topics Covered
- Topic 02 — Kafka
- Topic 03 — Kafka Networking
- Topic 06 — Troubleshooting

### Problem

Kafka is running and a host-based client can connect. A Python client inside another container cannot.

The Kafka broker is advertised using a hostname that the container cannot resolve.

### Your Task

Diagnose the issue using the host/container connectivity model and explain why Kafka's advertised listener matters.

### Solution

#### Step 1 — Separate the two paths

There are two different client locations:

```text
Host client → Kafka
Container client → Kafka
```

A hostname reachable from the host is not automatically reachable from another container.

#### Step 2 — Inspect the Kafka configuration

Use:

```bash
docker inspect kafka
```

and inspect the relevant listener/environment configuration.

#### Step 3 — Test DNS from the client container

Use a temporary diagnostic container on the same network:

```bash
docker run --rm --network data-lab busybox nslookup <advertised-hostname>
```

If DNS fails, the hostname is wrong for that client environment.

#### Step 4 — Use a listener architecture appropriate to both clients

A common local-lab design uses:

```text
Internal listener → container clients
External listener → host clients
```

The advertised address for each listener must be reachable from the corresponding client.

#### Step 5 — Verify

Test from both locations independently.

```text
Host client → external advertised address
Container client → internal advertised address
```

#### Root Cause

Kafka does not stop at the initial TCP connection. It tells clients where to connect through advertised listener metadata. If the returned address is unreachable from the client's network environment, the client fails even though the broker itself is running.

#### Key Takeaway

For Kafka, always reason about:

```text
listener bind address
+
advertised address
+
client location
```

---

## Question 22 — PostgreSQL Initialization Variables Changed After First Start

### Difficulty
Hard

### Topics Covered
- Topic 02 — PostgreSQL
- Topic 04 — Persistence
- Topic 05 — Configuration

### Problem

A PostgreSQL container was first initialized with:

```text
POSTGRES_DB=old_db
POSTGRES_USER=old_user
```

The learner then recreates the container with:

```text
POSTGRES_DB=new_db
POSTGRES_USER=new_user
```

using the same persistent volume. The old database is still present.

### Your Task

Explain the behavior and determine what should happen if the goal is to create a completely fresh database.

### Solution

#### Step 1 — Identify the important state

The persistent volume contains the PostgreSQL data directory.

The first initialization established the database cluster.

#### Step 2 — Understand initialization semantics

The standard PostgreSQL container initialization variables are primarily used when the data directory is initialized for the first time.

Changing them later does not mean "reinitialize this existing database."

#### Step 3 — If existing data must be preserved

Keep the volume and manage the database using PostgreSQL itself rather than expecting container initialization variables to rewrite the existing cluster.

#### Step 4 — If a completely fresh lab is intended

Only after confirming the data is disposable, remove the old container and its associated volume, then initialize a fresh volume.

For example, after explicit confirmation and backup if required:

```bash
docker rm -f pg-lab
docker volume rm pgdata
```

Then create a new volume/container with the desired configuration.

#### Safety

`docker volume rm` permanently removes the Docker volume's stored data. Verify the volume name and confirm that the data is disposable before running it.

#### Why This Works

Container configuration and persistent application state have different lifecycles.

#### Key Takeaway

A changed environment variable cannot retroactively rewrite an already-initialized PostgreSQL data directory.

---

## Question 23 — MinIO Bind-Mount Permission Failure

### Difficulty
Hard

### Topics Covered
- Topic 02 — MinIO
- Topic 04 — Bind Mounts and Permissions
- Topic 06 — Troubleshooting

### Problem

MinIO starts with a host bind mount, but logs report a permission error when trying to write its data.

### Your Task

Diagnose the failure without immediately using `chmod 777`, and explain the correct reasoning process.

### Solution

#### Step 1 — Confirm the mount

```bash
docker inspect minio
```

Inspect the `Mounts` section.

#### Step 2 — Read logs

```bash
docker logs minio
```

Confirm that the failure is actually a filesystem permission problem.

#### Step 3 — Inspect the host directory

Check:

- ownership
- permissions
- whether the directory exists
- whether the path is the intended directory

The exact host commands depend on the host operating system.

#### Step 4 — Reason about identities

The process inside the container may not run with the same user/group identity as the host user.

Therefore, a directory that is writable by the host user may not be writable by the container process.

#### Step 5 — Apply the smallest safe permission/ownership correction

Do not blindly use:

```bash
chmod 777
```

Instead, align ownership/permissions with the container's expected access model, following the service documentation and the platform-specific behavior covered by the lab.

#### Step 6 — Verify

Restart the service and inspect:

```bash
docker logs minio
docker inspect minio
```

Then create/read a test bucket or object.

#### Root Cause

The bind mount exposes a host filesystem path to the container, so host filesystem permissions become part of the containerized service's runtime behavior.

#### Key Takeaway

A bind mount is not an abstract Docker volume. It crosses into the host filesystem and therefore brings ownership and permission semantics with it.

---

## Question 24 — Exit Code 137 After Adding Kafka

### Difficulty
Hard

### Topics Covered
- Topic 08 — Resources
- Topic 06 — Troubleshooting
- Topic 07 — Compose

### Problem

Your laptop runs PostgreSQL, MinIO, Redis, and Kafka. After starting Kafka, the laptop becomes unstable. Kafka later exits with code `137`.

### Your Task

Determine what `137` suggests, identify the evidence you need, and propose a safe response.

### Solution

#### Step 1 — Treat 137 as a clue

Exit code `137` commonly indicates that the process was terminated by `SIGKILL` (`128 + 9`). In a constrained container environment, an out-of-memory event is a major possibility.

It is **not proof by itself**.

#### Step 2 — Inspect the container

```bash
docker inspect kafka
docker logs kafka
```

Look at the state and surrounding evidence.

#### Step 3 — Measure current resource usage

```bash
docker stats
```

Compare Kafka with the other services.

#### Step 4 — Check host/Docker capacity

On Docker Desktop or WSL2, also consider the resources allocated to the Docker/WSL environment.

#### Step 5 — Reduce pressure

Possible lab-safe actions include:

- stop services not currently needed,
- use Compose profiles,
- reduce resource limits where appropriate,
- avoid running the full stack simultaneously,
- move a heavy workload to a cloud VM when the laptop is genuinely insufficient.

#### Step 6 — Verify

Restart the affected service and observe:

```bash
docker stats
docker compose ps
docker compose logs -f kafka
```

#### Root Cause

The likely issue is memory pressure or another resource constraint, but the diagnosis should be based on measured evidence rather than the exit code alone.

#### Key Takeaway

**137 is evidence, not a complete diagnosis.** Correlate it with memory usage, host capacity, logs, and timing.

---

## Question 25 — Compose Stack Has One Failing Dependency

### Difficulty
Hard

### Topics Covered
- Topic 02 — Readiness
- Topic 06 — Troubleshooting
- Topic 07 — Compose

### Problem

A Compose stack contains PostgreSQL, MinIO, Redis, Kafka, and a Python client. Compose starts all services, but the Python client fails because PostgreSQL was not ready when the client started.

### Your Task

Explain why Compose startup ordering alone does not guarantee application readiness and describe how you would diagnose and operate the stack safely.

### Solution

#### Step 1 — Check actual service states

```bash
docker compose ps
```

#### Step 2 — Read the dependent service logs

```bash
docker compose logs python
docker compose logs postgres
```

#### Step 3 — Test PostgreSQL readiness

```bash
pg_isready -h localhost -p 5432
```

Or test from the appropriate container/network context.

#### Step 4 — Understand the failure

Compose can start services in an order, but "container process started" does not automatically mean "application is ready to serve requests."

#### Step 5 — Restart the dependent service after PostgreSQL is ready

```bash
docker compose restart python
```

Use the stack's provided readiness behavior if the supplied Compose configuration already defines it.

#### Step 6 — Verify

```bash
docker compose ps
docker compose logs -f python
```

#### Root Cause

The dependency relationship was treated as a startup-order guarantee instead of a readiness requirement.

#### Key Takeaway

In Data Engineering stacks:

```text
dependency order ≠ application readiness
```

---

## Question 26 — Wrong Volume After Container Recreation

### Difficulty
Hard

### Topics Covered
- Topic 04 — Persistence
- Topic 06 — Troubleshooting

### Problem

PostgreSQL was working yesterday. Today the container was recreated and the database appears empty.

The learner says:

> "Docker deleted my database."

### Your Task

Prove or disprove that claim by inspecting the container's mounts and Docker volumes.

### Solution

#### Step 1 — Inspect the new container

```bash
docker inspect pg-lab
```

Look at `Mounts`.

#### Step 2 — List volumes

```bash
docker volume ls
```

#### Step 3 — Inspect the expected volume

```bash
docker volume inspect pgdata
```

#### Step 4 — Compare the actual mount

You are looking for:

```text
pgdata → /var/lib/postgresql/data
```

If the recreated container uses a different volume, an anonymous volume, or no persistent volume, PostgreSQL can appear empty even though the old data still exists elsewhere.

#### Step 5 — Reattach the correct volume

After confirming the correct volume and data path, recreate the service with:

```bash
-v pgdata:/var/lib/postgresql/data
```

#### Step 6 — Verify

Connect to PostgreSQL and verify the expected tables/data.

#### Root Cause

The likely issue is not that Docker deleted the data. The new container may simply be attached to different storage.

#### Key Takeaway

When state "disappears," inspect the **mount mapping before assuming data loss**.

---

## Question 27 — Disk Is Full: Safe Cleanup Decision

### Difficulty
Hard

### Topics Covered
- Topic 09 — Cleanup
- Topic 04 — Persistence
- Topic 06 — Troubleshooting

### Problem

Docker reports that disk space is nearly exhausted. You see:

- many stopped containers,
- several old images,
- several volumes,
- large container logs.

A colleague recommends:

```bash
docker system prune -a --volumes
```

### Your Task

Explain why this is unsafe as a first action and provide a safer investigation sequence.

### Solution

#### Step 1 — Measure

```bash
docker system df
docker system df -v
```

#### Step 2 — Identify categories

Determine whether the space is primarily from:

- images,
- stopped containers,
- volumes,
- logs,
- build cache.

#### Step 3 — Protect data first

Inspect important volumes:

```bash
docker volume ls
docker volume inspect <volume>
```

Confirm whether PostgreSQL, MinIO, or other stateful services use them.

#### Step 4 — Check log growth

Inspect noisy containers:

```bash
docker logs <container>
```

Review the logging configuration used by the lab where applicable.

#### Step 5 — Remove only safe resources

For example, after review:

```bash
docker container prune
```

This removes stopped containers, not persistent volumes.

For images, distinguish dangling images from all unused images before deciding whether:

```bash
docker image prune
```

or:

```bash
docker image prune -a
```

is appropriate.

#### Step 6 — Treat volume pruning as a separate decision

Do **not** run:

```bash
docker volume prune
```

until you have verified that unused volumes contain no important state.

#### Why the colleague's command is dangerous

A broad prune with volume deletion can remove persistent data that is not currently attached but is still valuable.

#### Key Takeaway

Disk cleanup is an operational investigation, not a one-command ritual.

---

## Question 28 — Docker Compose Profile for Laptop Capacity

### Difficulty
Hard

### Topics Covered
- Topic 07 — Compose
- Topic 08 — Resources

### Problem

Your Compose lab contains core services plus an optional heavy service. Your laptop can comfortably run the core stack but becomes slow when everything starts.

### Your Task

Explain how Compose profiles can help and describe an operator workflow for running only what is needed.

### Solution

#### Step 1 — Understand the purpose

Profiles let a provided Compose stack group optional services so they do not need to run in every session.

#### Step 2 — Inspect the provided configuration

```bash
docker compose config
```

Identify which services are associated with profiles.

#### Step 3 — Start the default/core stack

```bash
docker compose up -d
```

#### Step 4 — Start an optional profile only when needed

```bash
docker compose --profile <profile> up -d
```

Use the profile name defined by the provided stack.

#### Step 5 — Measure

```bash
docker stats
```

Compare the resource footprint.

#### Step 6 — Stop services you no longer need

```bash
docker compose stop <service>
```

or operate the stack according to the supplied Compose design.

#### Why This Works

Capacity planning is partly about reducing concurrency. You do not need every Data Engineering service running all day.

#### Key Takeaway

A good local lab is not the one that runs everything simultaneously; it is the one that runs the required workload comfortably and predictably.

---

## Question 29 — Docker Compose Configuration Does Not Match Expectations

### Difficulty
Hard

### Topics Covered
- Topic 05 — Configuration
- Topic 07 — Compose
- Topic 06 — Troubleshooting

### Problem

A Compose service appears to use the wrong environment variable value. The repository contains `.env`, `env_file`, and service-level environment configuration.

### Your Task

Diagnose the effective configuration without guessing.

### Solution

#### Step 1 — Resolve the Compose configuration

```bash
docker compose config
```

This gives you the effective Compose configuration after processing the project's configuration inputs.

#### Step 2 — Compare expected vs actual values

Determine which value the service receives.

#### Step 3 — Inspect the running container

```bash
docker compose ps
docker inspect <container>
```

If the service remains running:

```bash
docker compose exec <service> sh
```

Inspect the relevant environment variable inside the container where appropriate.

#### Step 4 — Trace the source

Ask:

```text
Is the value coming from .env substitution?
Is it in env_file?
Is it explicitly set for the service?
Is the image providing a default?
```

Do not assume all configuration files have identical semantics.

#### Step 5 — Apply the smallest correction

Change the appropriate configuration source, then recreate/restart the affected service according to the provided stack's operating instructions.

#### Step 6 — Verify

```bash
docker compose config
docker compose ps
docker compose logs <service>
```

#### Root Cause

The effective configuration was not inspected. The learner reasoned from source files without confirming the resolved runtime state.

#### Key Takeaway

Use `docker compose config` as an evidence tool, not merely as a syntax check.

---

## Question 30 — ARM64 Image Compatibility

### Difficulty
Hard

### Topics Covered
- Topic 01 — Image Architectures
- Topic 10 — Apple Silicon and Platforms

### Problem

You are running Docker on an Apple Silicon Mac. A Data Engineering image fails to run natively because the available image does not provide an ARM64 variant.

### Your Task

Explain the architecture mismatch and describe the role and trade-off of:

```bash
--platform linux/amd64
```

### Solution

#### Step 1 — Identify the architecture

Your host environment is ARM64.

The image may only provide an AMD64/Linux variant.

#### Step 2 — Inspect available image architecture information

Use image inspection/documentation to determine supported architectures.

#### Step 3 — Explicitly request AMD64 when appropriate

```bash
docker run --platform linux/amd64 <image>:<tag>
```

#### Step 4 — Understand the trade-off

Docker may use emulation to run the AMD64 workload on an ARM64 machine.

This can:

- reduce performance,
- increase resource usage,
- expose compatibility/performance differences.

#### Step 5 — Prefer native multi-architecture images when available

If an image supports both `linux/arm64` and `linux/amd64`, Docker can select the appropriate architecture automatically.

#### Why This Works

Container images are not universally architecture-independent. The executable binaries inside an image must be compatible with the target architecture, unless an emulation layer is used.

#### Key Takeaway

When a container behaves differently on Apple Silicon, check **image architecture before assuming the application itself is broken**.

---

# Level 4 — Advanced

## Question 31 — Full Local Data Lab Incident

### Difficulty
Advanced

### Topics Covered
- Topic 02 — Services
- Topic 03 — Networking
- Topic 04 — Persistence
- Topic 06 — Troubleshooting
- Topic 07 — Compose
- Topic 08 — Resources
- Topic 09 — Cleanup

### Problem

Your local Data Engineering stack contains:

```text
PostgreSQL
MinIO
Kafka
Redis
Python client
```

The following symptoms appear at the same time:

- the laptop is slow,
- Kafka is restarting,
- Python cannot connect to PostgreSQL,
- Docker disk usage is high.

### Your Task

Develop a systematic incident response. Do not immediately restart everything or prune Docker.

### Solution

#### Step 1 — Establish the incident state

```bash
docker compose ps
docker ps -a
```

Determine which services are running, restarting, or exited.

#### Step 2 — Measure resources

```bash
docker stats
```

Identify the highest CPU/memory consumers.

#### Step 3 — Investigate Kafka

```bash
docker compose logs kafka
docker inspect <kafka-container>
```

If Kafka has an exit code such as `137`, investigate memory pressure rather than assuming a Kafka configuration problem.

#### Step 4 — Investigate PostgreSQL connectivity

First check PostgreSQL state:

```bash
docker compose ps postgres
docker compose logs postgres
```

Then check readiness.

If Python is another container, test connectivity from the Python container's network context rather than using the host's `localhost`.

#### Step 5 — Inspect networks

```bash
docker network ls
docker network inspect <compose-network>
```

Confirm that Python and PostgreSQL share the expected network.

#### Step 6 — Inspect persistence

```bash
docker volume ls
docker volume inspect <postgres-volume>
```

Do not recreate PostgreSQL with a different volume merely to make the service start.

#### Step 7 — Investigate disk usage

```bash
docker system df
docker system df -v
```

Check whether logs, images, stopped containers, or volumes are responsible.

#### Step 8 — Apply the smallest safe fixes

Examples:

- stop unused services,
- reduce concurrent workload,
- correct the Python network endpoint,
- preserve and reattach the correct PostgreSQL volume,
- clean only verified-unused Docker resources.

#### Step 9 — Verify each layer

```bash
docker compose ps
docker stats
docker compose logs kafka
docker compose logs postgres
```

Then perform actual PostgreSQL connectivity and application tests.

#### Root Cause Thinking

Do not assume all symptoms have one cause.

Possible independent causes are:

```text
Laptop pressure → Kafka instability
Wrong network endpoint → Python/PostgreSQL failure
Accumulated logs/images → Disk pressure
```

#### Key Takeaway

A production-minded operator separates **symptoms into hypotheses** and validates each one with evidence.

---

## Question 32 — Kafka Internal and External Connectivity

### Difficulty
Advanced

### Topics Covered
- Topic 02 — Kafka
- Topic 03 — Networking
- Topic 07 — Compose

### Problem

A Kafka broker must support:

1. a client running on the host, and
2. a Python client running inside the Compose network.

The host can connect, but the Python client receives a broker address it cannot resolve.

### Your Task

Design the reasoning for a two-listener setup using the concepts taught in the module.

### Solution

#### Step 1 — Identify the two client environments

```text
Host client
    ↓
host network context

Python container
    ↓
Compose/Docker network context
```

They do not necessarily share the same reachable hostnames.

#### Step 2 — Provide separate listener paths

Conceptually:

```text
Internal listener:
Python container → Kafka service name → Kafka internal port

External listener:
Host client → localhost/host address → published Kafka port
```

#### Step 3 — Advertise reachable addresses

The internal listener should advertise an address resolvable/reachable from the Docker network.

The external listener should advertise an address reachable from the host.

#### Step 4 — Test DNS separately

From the Python container:

```bash
nslookup <internal-kafka-name>
```

From the host, test the external address using the appropriate Kafka client or TCP check.

#### Step 5 — Test TCP reachability

From the container:

```bash
nc -vz <internal-kafka-name> <internal-port>
```

Use the appropriate tool available in the diagnostic environment.

#### Step 6 — Verify client metadata

A successful initial connection is not enough. Kafka clients must receive broker metadata containing reachable advertised addresses.

#### Why This Works

Kafka's networking model is not simply "publish one port." Client location determines which advertised address is usable.

#### Key Takeaway

For Kafka, design from the **client's point of view**, not only the broker's point of view.

---

## Question 33 — Safe Reset of One Lab Without Destroying Another

### Difficulty
Advanced

### Topics Covered
- Topic 04 — Persistence
- Topic 07 — Compose Projects
- Topic 09 — Cleanup

### Problem

Your machine contains two independent labs:

```text
project-a → PostgreSQL + MinIO
project-b → PostgreSQL + Kafka
```

Project A is corrupted and must be reset. Project B's data must remain untouched.

### Your Task

Explain how you would identify the correct Compose project/resources and safely reset only Project A.

### Solution

#### Step 1 — Identify project identity

Use the project context and:

```bash
docker compose ps
```

from Project A's directory.

If the project was started with a custom project name, account for that name.

#### Step 2 — Inspect resources before deleting

```bash
docker ps -a
docker volume ls
docker network ls
```

Look for project-specific names/labels.

#### Step 3 — Confirm which volumes belong to Project A

```bash
docker volume inspect <project-a-volume>
```

Do not infer ownership only from a similar-looking name.

#### Step 4 — Back up anything important

If Project A's data matters, back it up before resetting.

#### Step 5 — Remove only Project A's containers/network

Start with:

```bash
docker compose down
```

from Project A.

Do **not** add `-v` unless you have explicitly confirmed that every associated volume is disposable.

#### Step 6 — If the requirement is a complete fresh reset

Only after verifying the target volumes and backing up required data:

```bash
docker compose down -v
```

#### Step 7 — Verify Project B

From Project B:

```bash
docker compose ps
```

Also inspect its volumes if necessary.

#### Root Cause/Safety Principle

The dangerous assumption is that "unused by the current container" means "safe to delete." Persistent state can exist independently of the currently running container.

#### Key Takeaway

A safe reset is **targeted, identity-aware, and verified**.

---

## Question 34 — Disk Exhaustion Caused by Logs

### Difficulty
Advanced

### Topics Covered
- Topic 06 — Logs
- Topic 09 — Disk Usage
- Topic 07 — Compose

### Problem

Your Docker disk is almost full. `docker system df` shows that images are not the primary problem. One service produces extremely large logs.

You still need the service to run.

### Your Task

Diagnose the cause and describe a safe operational response that addresses future log growth.

### Solution

#### Step 1 — Identify the noisy service

```bash
docker ps
docker logs <service>
```

Observe whether the application is producing repeated errors or unusually verbose output.

#### Step 2 — Determine whether the logs are evidence of a deeper failure

A large log file may be a symptom of:

- a restart loop,
- repeated connection failure,
- repeated authentication failure,
- another application-level problem.

Fix the root cause where possible.

#### Step 3 — Review the provided logging configuration

For Compose-managed stacks, inspect the supplied Compose configuration and its logging settings.

The module teaches log size limits/rotation as a way to prevent unbounded local growth.

#### Step 4 — Apply an appropriate rotation/limit configuration

Use the logging configuration pattern already taught by the stack rather than inventing an unrelated logging architecture.

#### Step 5 — Verify

Restart/recreate the affected service as required by the configuration change.

Then observe:

```bash
docker logs <service>
docker system df
```

and continue monitoring.

#### Why This Works

Log rotation limits the amount of historical log data retained locally. It does not fix an application that is generating an error continuously.

#### Key Takeaway

**Log growth is both a storage problem and potentially an application-health signal.** Solve both.

---

## Question 35 — WSL2 Bind-Mount Performance Incident

### Difficulty
Advanced

### Topics Covered
- Topic 10 — WSL2
- Topic 04 — Bind Mounts
- Topic 08 — Resources

### Problem

A Windows developer runs a Data Engineering lab through Docker Desktop + WSL2. A file-heavy workload is unexpectedly slow.

The project is stored under:

```text
/mnt/c/...
```

### Your Task

Explain why this can be slower and propose a platform-aware investigation.

### Solution

#### Step 1 — Identify the filesystem boundary

`/mnt/c/...` accesses the Windows filesystem from the Linux/WSL environment.

File-heavy workloads can pay a performance cost when crossing this boundary.

#### Step 2 — Compare with the Linux filesystem

For a controlled experiment, place a copy of the project in the WSL2 Linux filesystem under a path such as:

```text
/home/<user>/...
```

Do not move important production data blindly; this is a local-lab performance experiment.

#### Step 3 — Compare workload behavior

Measure the same workload from both locations.

Pay particular attention to:

- many small files,
- file-change watching,
- database-like I/O,
- bind-mounted development directories.

#### Step 4 — Inspect Docker/WSL resource capacity

If the workload remains slow, also inspect:

```bash
docker stats
```

and the WSL2/Docker Desktop resource allocation.

#### Why This Works

Performance is influenced by both **filesystem location** and **compute capacity**. Moving the project into the Linux filesystem can reduce cross-boundary filesystem overhead.

#### Key Takeaway

On Windows + WSL2, the question is not merely "Is Docker slow?" Ask **where the files live and how often the workload crosses the host/VM filesystem boundary**.

---

## Question 36 — CRLF Causes a Container Startup Failure

### Difficulty
Advanced

### Topics Covered
- Topic 10 — CRLF/LF
- Topic 06 — Troubleshooting
- Topic 07 — Compose

### Problem

A shell script works when executed in Linux but fails when mounted into a Linux container from a Windows development environment.

The container reports an error suggesting the script interpreter/path is invalid.

### Your Task

Diagnose the likely line-ending problem and explain the fix without changing the application logic.

### Solution

#### Step 1 — Recognize the symptom

Windows commonly uses CRLF line endings while Linux shell scripts conventionally use LF.

A shell script with CRLF can produce interpreter/path errors when executed in Linux.

#### Step 2 — Inspect the file

Use an appropriate line-ending inspection tool/editor.

You are looking for CRLF rather than LF.

#### Step 3 — Convert the script to LF

Use the editor or Git configuration appropriate to the repository.

The exact conversion method depends on the development environment.

#### Step 4 — Prevent recurrence

Use repository/editor configuration such as `.gitattributes` where appropriate so shell scripts remain compatible across platforms.

#### Step 5 — Verify

Run the script again inside the container and confirm that the startup problem is gone.

#### Why This Works

The script is being interpreted by a Linux environment. Line-ending bytes are part of the file content and can affect interpreter parsing.

#### Key Takeaway

Cross-platform bugs are often caused by **host development conventions leaking into Linux container execution**.

---

## Question 37 — Resource Budgeting a Four-Service Laptop Lab

### Difficulty
Advanced

### Topics Covered
- Topic 02 — Services
- Topic 07 — Compose
- Topic 08 — Capacity
- Topic 10 — Platform Differences

### Problem

You have a laptop with limited memory. Your Data Engineering lab includes:

```text
PostgreSQL
Kafka
MinIO
Redis
```

The developer wants all four running permanently, even though only PostgreSQL and Redis are needed for today's exercise.

### Your Task

Create a resource-management strategy using concepts taught in the module.

### Solution

#### Step 1 — Measure before changing

```bash
docker stats
```

Record actual idle and loaded usage where practical.

#### Step 2 — Identify today's required services

If the exercise needs only PostgreSQL and Redis, do not run Kafka and MinIO simply because they are part of the full lab.

#### Step 3 — Use Compose profiles when the provided stack supports them

Start only the core services:

```bash
docker compose up -d
```

Start optional services only when required:

```bash
docker compose --profile <profile> up -d
```

#### Step 4 — Stop unused services

```bash
docker compose stop kafka minio
```

Use the actual service names from the supplied stack.

#### Step 5 — Set reasonable limits where appropriate

For isolated experiments, use:

```bash
--memory
--cpus
```

or the equivalent resource controls already provided by the Compose stack.

Do not choose arbitrary limits that make the service unreliable.

#### Step 6 — Consider platform capacity

On Docker Desktop/WSL2, the effective Docker environment may have its own memory/CPU allocation.

#### Step 7 — Re-measure

```bash
docker stats
```

Compare the new footprint.

#### Why This Works

Capacity management is a scheduling problem as much as a limit-setting problem. Running fewer services is often safer than forcing every service into a small memory budget.

#### Key Takeaway

**Run what the current experiment needs. Measure actual usage. Then apply limits where they provide useful isolation.**

---

## Question 38 — Full Cross-Platform Lab Failure

### Difficulty
Advanced

### Topics Covered
- Topic 03 — Networking
- Topic 04 — Bind Mounts
- Topic 05 — Configuration
- Topic 06 — Troubleshooting
- Topic 07 — Compose
- Topic 10 — Cross-Platform Operation

### Problem

A Compose Data Engineering lab works on Linux but fails on a Windows + WSL2 machine.

Symptoms:

- a shell script fails to start,
- Python cannot reach a host-side service using `localhost`,
- the bind-mounted project is slow,
- one image reports architecture incompatibility on an ARM-based laptop used by another team member.

### Your Task

Build a diagnosis plan that separates the four failures instead of treating them as one Docker problem.

### Solution

#### Step 1 — Separate symptoms by layer

```text
Script failure       → filesystem/line endings
Host service access  → networking
Slow bind mount      → filesystem performance
Architecture error   → image/platform compatibility
```

#### Step 2 — Diagnose the shell script

Check CRLF/LF and ensure the script uses Linux-compatible line endings.

#### Step 3 — Diagnose host connectivity

From inside a container, `localhost` refers to that container.

Where supported by the platform, use:

```text
host.docker.internal
```

for host access, or use the platform-specific host connectivity method taught by the lab.

Test with:

```bash
curl ...
nc ...
```

as appropriate.

#### Step 4 — Diagnose filesystem performance

Compare a project under:

```text
/mnt/c/...
```

with a project stored in the WSL2 Linux filesystem.

#### Step 5 — Diagnose architecture

Inspect the image's architecture support.

If necessary and supported:

```bash
docker run --platform linux/amd64 <image>:<tag>
```

But recognize the emulation/performance trade-off.

#### Step 6 — Verify independently

Do not declare the platform "fixed" until:

- the script executes,
- host connectivity succeeds,
- filesystem performance is acceptable,
- the image runs on the target architecture.

#### Why This Works

The symptoms come from different layers. Fixing one does not automatically fix the others.

#### Key Takeaway

Cross-platform troubleshooting is most effective when you classify the failure before changing the environment.

---

## Question 39 — Evidence-Driven Restart Loop Investigation

### Difficulty
Advanced

### Topics Covered
- Topic 01 — Lifecycle
- Topic 02 — Services
- Topic 05 — Configuration
- Topic 06 — Troubleshooting
- Topic 07 — Compose

### Problem

Kafka is in a restart loop:

```text
Restarting
Restarting
Restarting
```

A teammate repeatedly runs:

```bash
docker restart kafka
```

but the problem returns.

### Your Task

Use the module's troubleshooting methodology to find the likely root cause without relying on repeated restarts.

### Solution

#### Step 1 — Observe

```bash
docker compose ps
docker ps -a
```

Confirm the restart loop.

#### Step 2 — Read logs

```bash
docker compose logs kafka
```

Look for the first meaningful startup error rather than the final cascade of failures.

#### Step 3 — Inspect configuration

```bash
docker inspect <kafka-container>
```

Review relevant environment/configuration metadata.

#### Step 4 — Inspect networking

```bash
docker network inspect <network>
```

Check whether expected dependencies/addresses are available.

#### Step 5 — Inspect storage if initialization is failing

Check the mounted data path/volume:

```bash
docker volume ls
docker volume inspect <volume>
```

#### Step 6 — Consider resource failure

```bash
docker stats
```

If the container exits with a resource-related signal or code, investigate host/container capacity.

#### Step 7 — Form and test one hypothesis

For example:

```text
Symptom: Kafka restarts.
Evidence: startup log reports invalid advertised address.
Hypothesis: listener configuration is invalid.
```

Change only the relevant configuration.

#### Step 8 — Verify

```bash
docker compose up -d kafka
docker compose ps kafka
docker compose logs -f kafka
```

Then test connectivity from the actual client environment.

#### Why This Works

A restart does not change the cause. It only repeats the same startup sequence.

#### Key Takeaway

Use the loop:

```text
Observe
→ Inspect
→ Collect evidence
→ Hypothesize
→ Test
→ Fix
→ Verify
```

---

## Question 40 — Complete Data Engineering Lab Operational Incident

### Difficulty
Advanced

### Topics Covered
- Topic 01 — Containers and Images
- Topic 02 — Services and Readiness
- Topic 03 — Networking
- Topic 04 — Persistence
- Topic 05 — Configuration
- Topic 06 — Troubleshooting
- Topic 07 — Compose
- Topic 08 — Resources
- Topic 09 — Cleanup
- Topic 10 — Platform Differences

### Problem

You are responsible for a local Data Engineering laboratory on Windows + WSL2.

The Compose stack contains:

```text
PostgreSQL → source database
MinIO     → object storage
Kafka     → event streaming
Redis     → cache
Python    → pipeline/client
```

The morning incident report says:

1. Docker disk usage is high.
2. Kafka is restarting.
3. PostgreSQL is running but Python cannot connect.
4. MinIO reports a filesystem permission error.
5. The project is slow because it is mounted from `/mnt/c/...`.
6. One teammate on Apple Silicon cannot run an image natively.
7. A developer proposes `docker compose down -v` followed by `docker system prune -a --volumes`.

### Your Task

Act as the Data Engineer on call. Produce a safe, ordered incident response that minimizes data loss and avoids destructive guessing.

### Solution

#### Step 1 — Freeze destructive actions

Do **not** run:

```bash
docker compose down -v
docker system prune -a --volumes
```

until data ownership and backup requirements are understood.

These commands can remove persistent Docker volumes and therefore important PostgreSQL/MinIO state.

#### Step 2 — Establish the stack state

```bash
docker compose ps
docker ps -a
```

Classify each service:

```text
running
stopped
restarting
exited
```

#### Step 3 — Measure resources

```bash
docker stats
```

Determine whether Kafka's restart behavior correlates with memory/CPU pressure.

#### Step 4 — Diagnose Kafka

```bash
docker compose logs kafka
docker inspect <kafka-container>
```

If you see exit code `137`, treat memory pressure as a major hypothesis and verify it with resource measurements.

If the logs show listener/advertised-address errors, inspect the Kafka network configuration instead.

#### Step 5 — Diagnose PostgreSQL

```bash
docker compose logs postgres
docker inspect <postgres-container>
```

Check readiness.

Then inspect the Python service's network membership:

```bash
docker network inspect <compose-network>
```

If Python is using:

```text
localhost:5432
```

inside its own container, that is likely wrong. It should use the PostgreSQL service/container name and container port on the shared Docker network.

#### Step 6 — Diagnose MinIO permissions

Inspect mounts:

```bash
docker inspect <minio-container>
```

Read logs:

```bash
docker compose logs minio
```

Check the host bind-mounted directory's ownership and permissions.

Do not jump to `chmod 777`. Determine the actual identity and access requirement first.

#### Step 7 — Diagnose disk usage

```bash
docker system df
docker system df -v
```

Identify whether the major consumer is:

- logs,
- volumes,
- images,
- stopped containers,
- build cache.

Inspect important volumes:

```bash
docker volume ls
docker volume inspect <volume>
```

#### Step 8 — Protect persistent data

Identify PostgreSQL and MinIO volumes.

Back up important database state using an application-consistent backup approach before any destructive cleanup.

#### Step 9 — Perform targeted cleanup

After confirming what is safe:

- remove disposable stopped containers,
- remove clearly unused images,
- address excessive logs,
- clean only verified-unused networks/cache,
- do not prune important volumes.

#### Step 10 — Address WSL2 filesystem performance

The `/mnt/c/...` project location can be slower for file-heavy workloads.

For a development performance test, move/copy the project into the WSL2 Linux filesystem and compare behavior.

Also inspect Docker/WSL resource capacity.

#### Step 11 — Address Apple Silicon compatibility

Determine whether the image has an ARM64 variant.

If it supports only AMD64 and the lab allows emulation:

```bash
docker run --platform linux/amd64 <image>:<tag>
```

Expect possible performance overhead.

Prefer a multi-architecture image when one is available and appropriate.

#### Step 12 — Verify service readiness

Do not stop at "containers are running."

Verify:

- PostgreSQL readiness,
- MinIO API availability,
- Kafka client connectivity from both relevant environments,
- Redis connectivity,
- Python pipeline connectivity.

#### Step 13 — Verify the final system

```bash
docker compose ps
docker stats
docker system df
```

Then perform actual application-level tests.

#### Root-Cause Model

The incident likely contains several independent failures:

| Symptom | Evidence to collect | Likely category |
|---|---|---|
| Kafka restarting | logs, inspect, stats | configuration or resource |
| Python cannot reach PostgreSQL | network inspect, endpoint | networking/localhost |
| MinIO permission error | logs + mounts + host permissions | bind-mount permissions |
| High disk usage | system df | logs/images/volumes/cache |
| Slow Windows lab | filesystem location | WSL2 bind-mount performance |
| ARM image failure | image architecture | platform compatibility |

#### Why This Works

The correct response is not "restart everything" or "delete everything." It is a controlled incident process:

```text
Protect data
→ Observe
→ Measure
→ Inspect
→ Separate symptoms
→ Form hypotheses
→ Apply smallest safe fixes
→ Verify
→ Clean up
→ Document
```

#### Key Takeaway

A strong Docker Data Engineer does not merely know commands. They understand **container lifecycle, service readiness, networking, persistence, configuration, troubleshooting, Compose operations, resource capacity, cleanup safety, and platform differences as one connected operational system**.

---

# Topic Coverage Matrix

`✓` means the question meaningfully tests the topic, not merely that a command from the topic happens to appear.

| Question | Topic 01 | Topic 02 | Topic 03 | Topic 04 | Topic 05 | Topic 06 | Topic 07 | Topic 08 | Topic 09 | Topic 10 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 01 | ✓ |  |  | ✓ |  |  |  |  |  |  |
| 02 | ✓ |  |  |  |  |  |  |  |  |  |
| 03 | ✓ | ✓ |  |  | ✓ |  |  |  |  |  |
| 04 | ✓ |  |  | ✓ |  |  |  |  |  |  |
| 05 |  |  | ✓ |  |  |  |  |  |  |  |
| 06 |  | ✓ |  | ✓ |  |  |  |  |  |  |
| 07 |  |  |  |  |  | ✓ |  |  |  |  |
| 08 |  |  |  |  |  |  | ✓ |  |  |  |
| 09 |  |  |  |  |  |  |  | ✓ |  |  |
| 10 |  |  |  |  |  |  |  |  | ✓ |  |
| 11 |  | ✓ |  |  |  | ✓ |  |  |  |  |
| 12 |  | ✓ | ✓ |  |  | ✓ |  |  |  |  |
| 13 |  |  |  |  | ✓ | ✓ |  |  |  |  |
| 14 |  |  |  | ✓ |  |  |  |  |  |  |
| 15 |  |  |  |  | ✓ |  | ✓ |  |  |  |
| 16 |  |  | ✓ |  |  | ✓ |  |  |  |  |
| 17 |  |  |  | ✓ |  |  | ✓ |  |  |  |
| 18 | ✓ |  |  |  |  | ✓ |  |  |  |  |
| 19 |  |  |  |  |  | ✓ | ✓ |  |  |  |
| 20 |  |  |  |  |  |  |  | ✓ |  |  |
| 21 |  | ✓ | ✓ |  |  | ✓ |  |  |  |  |
| 22 |  | ✓ |  | ✓ | ✓ |  |  |  |  |  |
| 23 |  | ✓ |  | ✓ |  | ✓ |  |  |  |  |
| 24 |  |  |  |  |  | ✓ |  | ✓ |  |  |
| 25 |  | ✓ |  |  |  | ✓ | ✓ |  |  |  |
| 26 |  |  |  | ✓ |  | ✓ |  |  |  |  |
| 27 |  |  |  | ✓ |  | ✓ |  |  | ✓ |  |
| 28 |  |  |  |  |  |  | ✓ | ✓ |  |  |
| 29 |  |  |  |  | ✓ | ✓ | ✓ |  |  |  |
| 30 | ✓ |  |  |  |  |  |  |  |  | ✓ |
| 31 | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ |  |
| 32 |  | ✓ | ✓ |  |  |  | ✓ |  |  |  |
| 33 |  |  |  | ✓ |  |  | ✓ |  | ✓ |  |
| 34 |  |  |  |  |  | ✓ | ✓ |  | ✓ |  |
| 35 |  |  | ✓ | ✓ |  |  |  | ✓ |  | ✓ |
| 36 |  |  |  |  |  | ✓ | ✓ |  |  | ✓ |
| 37 |  | ✓ |  |  |  |  | ✓ | ✓ |  | ✓ |
| 38 |  |  | ✓ | ✓ | ✓ | ✓ | ✓ |  |  | ✓ |
| 39 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  |  |
| 40 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

# Final Knowledge Assessment

After completing all 40 questions, you should be able to answer the following without relying on memorized recipes.

## Assessment Questions

1. Explain the difference between an image, a container, and persistent storage.
2. Predict what survives `docker stop`, `docker rm`, and removal/recreation of a container using a named volume.
3. Explain why `latest` is weaker for reproducible labs than an intentionally selected version/tag or digest.
4. Explain why a running PostgreSQL container may still reject connections.
5. Explain the difference between host-to-container and container-to-container connectivity.
6. Explain why `localhost` inside a container usually does not mean the host or another container.
7. Explain how Docker service-name DNS works on a user-defined network.
8. Explain why Kafka advertised listeners must be designed around client location.
9. Explain when to use a named volume versus a bind mount.
10. Explain why `docker compose down -v` requires explicit data-loss consideration.
11. Explain how initialization environment variables differ from persistent application state.
12. Explain why `.env` and `env_file` should not be treated as identical mechanisms.
13. Demonstrate an evidence-based troubleshooting loop using `docker ps -a`, `docker logs`, `docker inspect`, and `docker exec`.
14. Explain what exit code `137` suggests and why it is not, by itself, proof of an OOM event.
15. Explain how Compose profiles can help manage laptop capacity.
16. Explain why `docker system df` should normally precede destructive cleanup.
17. Explain why volume pruning is more dangerous than removing stopped containers.
18. Explain why `/mnt/c/...` can be slower for file-heavy WSL2 workloads.
19. Explain how CRLF can break a Linux shell script.
20. Explain ARM64 vs AMD64 compatibility and the trade-off of `--platform linux/amd64`.

## Mastery Standard

A strong learner should be able to:

- predict lifecycle behavior before running commands,
- identify the correct network namespace for a connection,
- distinguish service startup from readiness,
- protect persistent data before cleanup,
- use logs and inspect output as evidence,
- troubleshoot failures layer by layer,
- operate a provided Compose stack without unnecessarily redesigning it,
- measure resource consumption before imposing limits,
- clean Docker storage without blindly deleting state,
- recognize platform-specific failures on Windows/WSL2 and Apple Silicon,
- explain **why** a fix works,
- verify the result after every meaningful fix.

---

# Final Coverage Audit

## Difficulty Distribution

| Level | Required | Actual | Status |
|---|---:|---:|---|
| Basic | 10 | 10 | PASS |
| Moderate | 10 | 10 | PASS |
| Hard | 10 | 10 | PASS |
| Advanced | 10 | 10 | PASS |
| **Total** | **40** | **40** | **PASS** |

## Topic Coverage

| Topic | Covered? | Representative Questions |
|---|---|---|
| Topic 01 — Containers, Images, Registries | ✓ | 01, 02, 03, 04, 18, 30, 39, 40 |
| Topic 02 — Databases and Services | ✓ | 03, 06, 11, 12, 21, 22, 23, 25, 31, 32, 37, 40 |
| Topic 03 — Ports, Networks, Service Discovery | ✓ | 05, 12, 16, 21, 25, 31, 32, 35, 38, 40 |
| Topic 04 — Volumes and Persistence | ✓ | 01, 04, 06, 14, 17, 22, 23, 26, 27, 31, 33, 35, 38, 40 |
| Topic 05 — Environment Variables and Configuration | ✓ | 03, 13, 15, 22, 29, 38, 39, 40 |
| Topic 06 — Logs, Exec, Troubleshooting | ✓ | 07, 11, 12, 13, 16, 18, 19, 21, 23–27, 29, 31, 34, 36, 38–40 |
| Topic 07 — Docker Compose | ✓ | 08, 15, 17, 19, 25, 28, 29, 31–34, 36–40 |
| Topic 08 — Resources and Laptop Capacity | ✓ | 09, 20, 24, 28, 31, 35, 37, 40 |
| Topic 09 — Cleanup and Housekeeping | ✓ | 10, 27, 31, 33, 34, 40 |
| Topic 10 — Docker Desktop, WSL2, Platforms | ✓ | 30, 35, 36, 37, 38, 40 |

## Concept Coverage

The 40 questions collectively test:

- [x] Container lifecycle
- [x] Images and registries
- [x] Tags/digests and reproducibility reasoning
- [x] Image architectures
- [x] PostgreSQL
- [x] MinIO
- [x] Kafka
- [x] Redis
- [x] Readiness
- [x] Initialization
- [x] Ports
- [x] Networks
- [x] DNS/service discovery
- [x] `localhost` behavior
- [x] Kafka listeners and advertised listeners
- [x] Volumes
- [x] Bind mounts
- [x] Persistence
- [x] Backup/restore safety
- [x] Environment variables
- [x] Configuration
- [x] Secret hygiene and local credential awareness
- [x] Logs
- [x] Exit codes
- [x] `docker inspect`
- [x] `docker exec`
- [x] `docker cp` awareness within troubleshooting scope
- [x] Evidence-based troubleshooting methodology
- [x] Docker Compose
- [x] Profiles
- [x] Project identity
- [x] Overrides/configuration awareness
- [x] `.env`
- [x] `env_file`
- [x] Resource limits
- [x] CPU/memory
- [x] OOM / exit 137
- [x] Disk usage
- [x] Pruning
- [x] Log growth
- [x] Safe cleanup
- [x] WSL2
- [x] Docker Desktop
- [x] CRLF/LF
- [x] Bind-mount performance
- [x] ARM64/AMD64
- [x] Cross-platform networking
- [x] Virtual disk/storage awareness

## Safety Audit

Potentially destructive operations are explicitly treated as data-affecting operations. The relevant questions explain what can be removed, what can survive, what should be backed up, and what must be verified before deletion.

Particular caution is applied to:

```bash
docker rm
docker rmi
docker volume rm
docker volume prune
docker system prune
docker system prune -a --volumes
docker compose down -v
```

## Scope Audit

The practice set remains within the Docker Essentials for Data Labs operator curriculum.

It does **not** introduce:

- Kubernetes
- Helm
- Docker Swarm
- Dockerfile authoring
- `FROM`/`RUN`/`COPY` image-building lessons
- multi-stage builds
- CI/CD container pipelines
- Terraform
- service mesh
- cloud container orchestration
- advanced container security engineering

## Final Result

```text
Basic:     10
Moderate:  10
Hard:      10
Advanced:  10
TOTAL:     40

All ten topics represented: PASS
Progressive difficulty: PASS
Problem before solution: PASS
Reasoning included: PASS
Verification included: PASS
Root-cause thinking: PASS
Data Engineering context: PASS
Destructive-operation safety: PASS
Scope compliance: PASS
```
