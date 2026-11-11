# Roadmap — Gap Module G1: Docker Essentials for Data Labs

This is the learning roadmap for the first gap module, **Docker Essentials
for Data Labs**. It tells you **what** to learn about using Docker as a data
engineer, **in what order**, **how** to learn each topic, and **how to
prove to yourself** that you have learned it before you move on.

**When to take it:** after Stage 2 Module 2.3 and **before Module 2.4**.
From Module 2.4 onwards, almost every exercise runs services in containers:
MinIO (object storage), PostgreSQL, Kafka, Spark, Airflow, and more. This
module makes you confident **running, connecting, persisting, configuring,
troubleshooting, and cleaning up** those containers and ready-made Docker
Compose stacks.

**What this module is not:** it does **not** teach writing Dockerfiles,
building images, multi-stage builds, or authoring Compose files. That is
Module 2.18 (Containers, Infrastructure, and CI/CD for Data). Here you are a
confident **user and operator** of containers; in Module 2.18 you become
their **author**.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain containers, images, tags, digests, and registries well enough to
  pull and run the right image for your machine.
- Run PostgreSQL, MinIO, Kafka, and Redis in containers, and know when a
  service is actually **ready**, not just started.
- Connect your Python code, command-line tools, and other containers to
  containerised services — and fix the classic "connection refused" and
  Kafka "advertised listener" problems.
- Keep data safe across restarts with **volumes** and **bind mounts**, back
  it up, and avoid deleting it by accident.
- Configure containers with environment variables and files without
  leaking secrets.
- Diagnose failing containers from logs, exit codes, and inspection.
- Operate provided **Docker Compose** stacks: start subsets, read logs,
  restart services, reset state safely.
- Keep a multi-service data lab within your laptop's memory and CPU.
- Reclaim disk space safely and keep your Docker installation healthy.
- Work around platform differences on Windows with WSL2, macOS (including
  ARM), and Linux.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Processes, signals, exit codes | Stage 0 — OS Fundamentals, Stage 1 — Module 1.5 | A container is a process; exit codes explain failures |
| Filesystems and permissions | Stage 0 — OS Fundamentals and Command Line | Volumes, bind mounts, and ownership problems |
| Environment variables | Stage 0 — OS Fundamentals and Command Line | Container configuration |
| Local networking, ports, `localhost` | Stage 0 — OS Fundamentals (local networking for development) | Port publishing and container networking |
| Shell, pipes, quoting | Stage 0 — Command Line | Every Docker command is a shell command |
| Secrets and local security hygiene | Stage 0 — Developer Environment | Keeping passwords out of commands and files |
| Configuration from environment, psycopg-style connection strings | Stage 1 — Module 1.5 / Stage 2 — Modules 2.1–2.3 | Connecting Python to containerised services |

**Tools needed:**

- **Docker Engine** with the Docker Compose v2 plugin (`docker compose`),
  installed through Docker Desktop (Windows/macOS) or natively on Linux —
  or an alternative runtime such as Podman, Colima, or Rancher Desktop
  (commands are mostly compatible; differences are covered in Topic 10).
- On Windows: **WSL2** with a Linux distribution, and Docker integrated
  with it.
- `psql` (or a GUI), the MinIO client `mc` (optional — you can run it in a
  container), and Python with `psycopg`, `boto3`, and `confluent-kafka` for
  connection tests.
- At least 8 GB of RAM (16 GB recommended for the later Stage 2 stacks).

---

## 3. How the module is organised

The ten topics are grouped into four phases. Work through them **in
order**.

```text
Phase A — Running Containers                        (Basics)
  01 Containers, images, and registries (for users)
  02 Running databases and services in containers

Phase B — Connecting and Persisting                 (Basics → Intermediate)
  03 Ports, networks, and service discovery
  04 Volumes, bind mounts, and data persistence
  05 Environment variables and configuration for containers

Phase C — Operating Stacks                          (Intermediate)
  06 Logs, exec, and troubleshooting containers
  07 Using Docker Compose stacks

Phase D — Keeping Your Machine Healthy              (Intermediate → Advanced)
  08 Resource limits and laptop capacity
  09 Cleanup, disk usage, and housekeeping
  10 Docker Desktop, WSL2, and platform differences

Consolidate
  practice-questions.md
  Module mini-project: your personal data lab (→ Projects/01-dockerized-local-data-lab.md)
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07 ──► 08 ──► 09 ──► 10
what   run a  reach  keep   config  fix   run a  fit it  keep   make it
it is  service it    its    it      it    whole  on your disk   work on
                     data                 stack  laptop  clean  your OS
```

Why this order:

- You must know what an image and a container are (01) before running
  services (02).
- A running service is useless until you can reach it (03), keep its data
  (04), and configure it (05).
- Troubleshooting (06) comes before Compose (07) because every Compose
  problem is a container problem underneath.
- Capacity (08), cleanup (09), and platform quirks (10) are what keep a
  multi-service data lab usable for months.

---

## 4. Suggested schedule

About **1–1.5 weeks at 8–10 hours per week**.

| Days | Work |
| --- | --- |
| 1 | Topic 01 — images and registries · Topic 02 — running services |
| 2 | Topic 03 — ports and networks |
| 3 | Topic 04 — volumes and persistence · Topic 05 — configuration |
| 4 | Topic 06 — troubleshooting |
| 5 | Topic 07 — Compose stacks |
| 6 | Topic 08 — resources · Topic 09 — cleanup · Topic 10 — platform differences |
| 7–8 | Practice questions · mini-project |

---

## 5. How to study every topic (the container-operator loop)

```text
Read → Predict → Run → Connect → Inspect → Break it → Diagnose → Fix
→ Clean up → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Predict** what will happen before each command (which port, which
   data survives, what the logs will say).
3. **Run** the container or stack.
4. **Connect** to it from the host and from another container.
5. **Inspect** it: `docker ps`, `docker inspect`, `docker logs`,
   `docker stats`.
6. **Break it** on purpose: wrong password, port conflict, missing volume,
   too little memory, wrong image architecture.
7. **Diagnose** from evidence only — logs, exit codes, inspect output —
   before searching the internet.
8. **Fix** it and confirm.
9. **Clean up** everything you created (you will learn how in Topic 09).
10. **Write down** the command, the symptom, and the fix in
    `module-g1-notes.md` — this becomes your personal Docker troubleshooting
    guide.
11. **Explain aloud** what Docker did behind each command.

Keep one `docker_lab/` folder with a `notes/` directory and one subfolder
per topic for any small files you mount into containers.

---

## 6. Phase A — Running Containers (Basics)

### Topic 01 — [Containers, images, and registries (for users)](01-containers-images-and-registries-for-users.md)

**Why it comes first:** Every later command pulls an image and starts a
container from it. Knowing exactly what you are running — and for which
CPU architecture — avoids a whole class of confusing errors.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What a container is: an isolated process with its own filesystem, network, and resource limits — **not** a virtual machine |
| Basics | Images (read-only templates made of layers) vs containers (running or stopped instances of an image) |
| Basics | Registries (Docker Hub, GitHub Container Registry, cloud registries); **repository**, **tag**, and the default `latest` tag |
| Basics | Core lifecycle commands: `docker pull`, `run`, `ps` / `ps -a`, `stop`, `start`, `restart`, `rm`, `images`, `rmi` |
| Basics | Useful `run` options: `--name`, `-d` (detached), `--rm` (remove when stopped), `-it` (interactive terminal) |
| Intermediate | **Tags vs digests**: tags can move; digests (`image@sha256:...`) identify exact content — pin versions for reproducible labs |
| Intermediate | **Official and verified images**, reading an image's documentation page (supported tags, environment variables, volumes, ports) |
| Intermediate | **Image architecture**: `linux/amd64` vs `linux/arm64`; multi-architecture images; `--platform`; emulation and its performance cost |
| Intermediate | Restart policies (`no`, `on-failure`, `unless-stopped`, `always`) and when to use them for a local lab |
| Advanced | Registry rate limits for anonymous pulls and logging in to a registry |
| Advanced | Image trust basics: prefer official or well-maintained images, pin versions, and avoid random images from unknown publishers |
| Advanced | Container runtimes and compatible tools (Docker Engine, containerd, Podman) — awareness |

**How to learn it**

1. Read the topic file.
2. Pull the same image by tag and by digest; inspect both with
   `docker image inspect` and compare.
3. Read the Docker Hub pages for the PostgreSQL, MinIO, and Kafka images you
   will use in Stage 2, and list their tags, ports, volumes, and required
   environment variables.

**Hands-on exercise — `docker_lab/01/`**

1. Run `hello-world`, then an interactive `python:3.12-slim` container and
   start a Python prompt inside it.
2. Run a detached container with a name, stop it, start it again, and
   remove it; observe `docker ps -a` at each step.
3. Run a container with `--rm` and confirm it disappears when stopped.
4. Pull a specific PostgreSQL version by tag, then pin it by digest in your
   notes.
5. Check the architecture of your machine and of a pulled image; if you are
   on ARM, run an `amd64`-only image with `--platform` and note the speed
   difference.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain container vs image vs virtual machine.
- [ ] Explain tags vs digests and why labs should pin versions.
- [ ] Manage the container lifecycle with confidence.
- [ ] Check and choose an image's architecture.

**Common mistakes:** using `latest` and getting a new major version by
surprise; confusing stopping with removing; piling up stopped containers;
running unknown images from untrusted publishers.

---

### Topic 02 — [Running databases and services in containers](02-running-databases-and-services-in-containers.md)

**Why here:** Data engineering labs are mostly **stateful services**:
databases, object stores, brokers. Each has its own start-up behaviour,
required settings, and readiness signals.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Running **PostgreSQL**: required environment variables (e.g. password), default database and user, the data directory, and connecting with `psql` |
| Basics | Running **MinIO**: server command, API port vs web console port, root credentials, and creating a bucket |
| Basics | Running **Redis** as a simple example of a key-value service |
| Intermediate | Running **Kafka** in KRaft mode (single node for learning): node id, listeners, and why its network settings are more complex (continued in Topic 03) |
| Intermediate | **Started vs ready**: a container can be "Up" while the service inside is still initialising; readiness checks such as `pg_isready`, health endpoints, and image health checks (`docker inspect` health status) |
| Intermediate | **Initialisation hooks**: running SQL scripts on first start of a database container (e.g. an init-scripts directory), and why they run only once per data volume |
| Intermediate | Choosing versions to match production (the same major PostgreSQL version as your target) |
| Advanced | One-off client containers (e.g. running `psql` or the MinIO client from a container instead of installing them) |
| Advanced | Services that need other services (e.g. a schema registry needing Kafka) — ordering and readiness |
| Advanced | Running services only on `localhost` of your machine and not exposing them to your network (continued in Topic 03) |

**How to learn it**

1. Read the topic file.
2. For each service, write a "service card": image and version, ports,
   required environment variables, data directory, readiness check, and a
   connection test.
3. Time how long each service takes from "container started" to "ready".

**Hands-on exercise — `docker_lab/02/`**

1. Run PostgreSQL, create a table with `psql`, and query it from Python
   with `psycopg`.
2. Run MinIO, create a bucket through the console and with the MinIO client
   in a one-off container, and upload a file from Python with `boto3`
   (custom endpoint URL).
3. Run a single-node Kafka in KRaft mode, create a topic, produce and
   consume a message with the Kafka console tools inside the container.
4. Add an init SQL script to PostgreSQL and show that it runs on first
   start but not on restart.
5. Write a small `wait_until_ready.py` that polls PostgreSQL, MinIO, and
   Kafka until each is ready (with timeouts) — you will reuse it in tests.

**Checkpoint:**

- [ ] Run and connect to PostgreSQL, MinIO, Redis, and Kafka.
- [ ] Explain the difference between started and ready, and check
      readiness.
- [ ] Use init scripts and explain when they run.
- [ ] Use one-off client containers.

**Common mistakes:** connecting before the service is ready; expecting init
scripts to rerun on an existing volume; mixing MinIO's API and console
ports; using a different major database version than production.

---

## 7. Phase B — Connecting and Persisting (Basics → Intermediate)

### Topic 03 — [Ports, networks, and service discovery](03-ports-networks-and-service-discovery.md)

**Why here:** "Connection refused" is the most common problem in container
labs. It almost always comes from confusing *where* `localhost` is and
*which* network a client is on.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Publishing ports**: `-p HOST_PORT:CONTAINER_PORT`; reaching a service from your machine at `localhost:HOST_PORT` |
| Basics | Port conflicts (e.g. a local PostgreSQL already on 5432) and choosing another host port |
| Basics | **`localhost` inside a container means the container itself**, not your machine |
| Intermediate | **User-defined networks** and **DNS by container name**: containers on the same network reach each other at `service-name:container-port` — no publishing needed |
| Intermediate | Why the default bridge network is different, and why labs should use named networks (and why Compose creates one for you) |
| Intermediate | Reaching your host machine from a container (`host.docker.internal` and platform differences) |
| Intermediate | Binding published ports to `127.0.0.1` so lab services are not reachable from your Wi-Fi network |
| Advanced | **Kafka listeners and advertised listeners**: why clients on your host and clients in other containers need different addresses, and how a two-listener set-up solves it |
| Advanced | Diagnosing networks: `docker network ls/inspect`, testing connectivity from a temporary troubleshooting container (e.g. `nc`, `curl`, `nslookup`) |
| Advanced | Host networking mode and its platform limitations — awareness |

**How to learn it**

1. Read the topic file.
2. Draw a diagram of your machine, a Docker network, three containers, and
   the published ports; label what address each client must use.
3. Reproduce the Kafka advertised-listener problem before fixing it.

**Hands-on exercise — `docker_lab/03/`**

1. Start PostgreSQL publishing `5432` while another process already uses it;
   read the error and republish on `5433`.
2. Create a network `datalab`; run PostgreSQL and a Python container on it;
   connect from Python using the container name as host.
3. Show that `localhost:5432` fails from inside the Python container and
   explain why.
4. Run Kafka with a single listener, show that a host client can connect
   but then fails (or vice versa for a container client); fix it with
   separate internal and external listeners.
5. Bind MinIO to `127.0.0.1` only and verify it is not reachable from
   another device (or by your machine's network IP).

**Checkpoint:**

- [ ] Publish ports and resolve port conflicts.
- [ ] Explain `localhost` inside vs outside containers.
- [ ] Connect containers by name on a user-defined network.
- [ ] Configure Kafka listeners for host and container clients.
- [ ] Troubleshoot connectivity with a helper container.

**Common mistakes:** using `localhost` inside containers; publishing every
port to all interfaces; relying on the default bridge network; copying
Kafka settings without understanding advertised listeners.

---

### Topic 04 — [Volumes, bind mounts, and data persistence](04-volumes-bind-mounts-and-data-persistence.md)

**Why here:** A container's writable layer disappears with the container.
Your lab databases, lake files, and Kafka logs must survive restarts — and
you must never lose them by accident.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The container writable layer and why data inside it is lost when the container is removed |
| Basics | **Named volumes** (managed by Docker) — the default choice for database data |
| Basics | **Bind mounts** (a host directory mounted into the container) — for code, config files, and sample data you edit |
| Basics | Mounting read-only (`:ro`) for configuration and input data |
| Intermediate | Which path to mount for each service (e.g. the PostgreSQL data directory, MinIO's data directory, Kafka's log directory) — read the image documentation |
| Intermediate | **Anonymous volumes** created automatically by images, and how they silently pile up |
| Intermediate | **Permissions and ownership** with bind mounts on Linux and WSL2: user ids inside vs outside the container, "permission denied" errors, and fixes |
| Intermediate | Inspecting and listing volumes: `docker volume ls/inspect` |
| Advanced | **Backing up and restoring** a volume with a temporary container (archive the volume's contents to a file on the host) |
| Advanced | Resetting a lab deliberately: removing volumes only when you intend to lose data |
| Advanced | Performance: bind mounts across operating-system boundaries (e.g. Windows files mounted into Linux containers) can be much slower — keep lab data inside the Linux filesystem (Topic 10) |
| Advanced | `tmpfs` mounts for fast, disposable data (e.g. test databases) |

**How to learn it**

1. Read the topic file.
2. Run PostgreSQL three ways — no volume, named volume, bind mount — create
   data, remove and recreate the container, and record what survives.
3. Create a "permission denied" error with a bind mount and fix it.

**Hands-on exercise — `docker_lab/04/`**

1. Run PostgreSQL with a named volume `pgdata`, load 100,000 rows, remove
   the container, start a new one on the same volume, and verify the rows.
2. Mount a local `sample_data/` folder read-only into a Python container and
   read a CSV from it.
3. Back up `pgdata` to a `.tar.gz` file, delete the volume, restore it, and
   verify the data.
4. Find and remove anonymous volumes left by earlier exercises (after
   checking they are not needed).
5. Compare load time for a database whose data lives on a named volume vs a
   bind mount (and, on Windows, vs a mount from the Windows filesystem).

**Checkpoint:**

- [ ] Choose between named volumes, bind mounts, and tmpfs.
- [ ] Persist and restore service data across container recreation.
- [ ] Back up and restore a volume.
- [ ] Fix bind-mount permission problems.

**Common mistakes:** storing database data in the container layer; deleting
volumes with a cleanup command without checking; bind-mounting database
data directories from slow cross-OS paths; forgetting that an existing
volume keeps old settings and passwords.

---

### Topic 05 — [Environment variables and configuration for containers](05-environment-variables-and-configuration-for-containers.md)

**Why here:** Every service image is configured through environment
variables and files. Doing this carelessly leaks passwords into shell
history, logs, and inspection output.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Passing variables with `-e NAME=value` and reading them inside a container |
| Basics | `--env-file` with a file of variables (kept out of Git) |
| Basics | Documented variables of each image (e.g. database user, password, database name; MinIO root user and password) |
| Intermediate | **Precedence**: values set on the command line vs env files vs image defaults |
| Intermediate | **Mounting configuration files** (e.g. a database config file or Kafka properties) instead of long variable lists |
| Intermediate | **Variables that only apply on first initialisation** (e.g. database passwords stored in an existing volume) — why changing them later "does nothing" |
| Intermediate | Passing connection settings to your own Python code in containers via environment variables (Stage 1 configuration patterns) |
| Advanced | **Where secrets leak**: shell history, process lists, `docker inspect` output, logs, and committed env files — and how to avoid each |
| Advanced | Docker's file-based secrets (e.g. `*_FILE` variables supported by some images) — awareness |
| Advanced | Local-only credentials: using separate, disposable passwords for labs and never reusing real ones |

**How to learn it**

1. Read the topic file.
2. For PostgreSQL, MinIO, and Kafka, list every environment variable you
   used, its purpose, and whether it applies only on first start.
3. Search `docker inspect` output and your shell history for your lab
   password — then fix how you pass it.

**Hands-on exercise — `docker_lab/05/`**

1. Create `lab.env` (in `.gitignore`) with PostgreSQL and MinIO credentials
   and start both services with `--env-file`.
2. Change the PostgreSQL password in `lab.env`, restart the container, and
   explain why login still requires the old password; fix it properly.
3. Mount a custom PostgreSQL configuration file (e.g. a changed logging
   setting) and verify it took effect.
4. Run a small Python container that reads its database settings from
   environment variables and connects.
5. Use a file-based secret variable where the image supports it.

**Checkpoint:**

- [ ] Configure services with variables, env files, and mounted files.
- [ ] Explain first-initialisation-only settings.
- [ ] Keep secrets out of history, Git, and logs.

**Common mistakes:** passwords typed directly into commands; env files
committed to Git; changing settings that only apply on first start and
wondering why nothing happens; reusing real passwords in labs.

---

## 8. Phase C — Operating Stacks (Intermediate)

### Topic 06 — [Logs, exec, and troubleshooting containers](06-logs-exec-and-troubleshooting-containers.md)

**Why here:** Containers fail — they exit immediately, restart in loops,
run out of memory, or cannot connect. A methodical approach turns hours of
guessing into minutes of diagnosis.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `docker logs` with `-f`, `--tail`, `--since`, and timestamps |
| Basics | `docker exec -it <container> sh|bash` and running tools inside (e.g. `psql`, `kafka-topics`) |
| Basics | `docker ps -a` status: up, exited, restarting — and the **exit code** |
| Intermediate | Reading **exit codes**: `0` (finished), `1` (application error), `137` (killed — often out of memory), `139` (crash), `143` (terminated by a stop signal) |
| Intermediate | `docker inspect` for state, health, mounts, networks, environment, and the restart count |
| Intermediate | **Crash loops**: containers restarting forever because of a configuration error, and how to stop and investigate them |
| Intermediate | `docker stats` for live CPU and memory; `docker events` for what Docker is doing |
| Intermediate | A **troubleshooting method**: symptom → status and exit code → logs → inspect (config, mounts, network) → reproduce inside the container → fix → verify |
| Advanced | Debugging a container that exits immediately (override the command to keep it running, or run the image interactively) |
| Advanced | Helper troubleshooting containers with network tools, attached to the same network |
| Advanced | Copying files in and out of containers (`docker cp`) for inspection |
| Advanced | Common data-lab failure signatures: wrong credentials, port already in use, missing volume path, out of memory (e.g. Kafka or Spark JVM), wrong architecture, initialisation scripts failing, unreachable dependencies |

**How to learn it**

1. Read the topic file.
2. Build a troubleshooting checklist from the method above and keep it in
   your notes.
3. Ask a friend (or write a script) to break your lab in hidden ways, then
   diagnose each problem using only Docker commands.

**Hands-on exercise — `docker_lab/06/` — "Broken lab" drills**

Diagnose and fix each scenario, recording symptom, evidence, cause, and fix:

1. PostgreSQL exits immediately (missing required password variable).
2. A container restarts in a loop because of a bad configuration file.
3. Kafka is killed with exit code `137` under a small memory limit.
4. A Python container cannot reach PostgreSQL (wrong host name / network).
5. An init script has a SQL error and the database starts without the
   expected tables.
6. MinIO cannot write to a bind mount (permission denied).
7. A service fails because another container is already using its port.

**Checkpoint:**

- [ ] Read logs, exit codes, and inspect output efficiently.
- [ ] Diagnose immediate exits and crash loops.
- [ ] Recognise out-of-memory kills.
- [ ] Follow a repeatable troubleshooting method.

**Common mistakes:** restarting repeatedly without reading logs; searching
the internet before checking the exit code; editing files inside containers
instead of fixing the mounted source; ignoring warnings at start-up.

---

### Topic 07 — [Using Docker Compose stacks](07-using-docker-compose-stacks.md)

**Why here:** Every later Stage 2 module ships a `docker-compose.yml` with
several services. You must be able to operate those stacks confidently —
even before you learn to write them in Module 2.18.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What Compose does: starts a group of containers, their network, and their volumes from one file |
| Basics | Core commands: `docker compose up -d`, `ps`, `logs -f <service>`, `stop`, `start`, `restart <service>`, `down` |
| Basics | Reading a Compose file **as a user**: services, images, ports, volumes, environment, and dependencies |
| Basics | `docker compose` (v2 plugin) vs the legacy `docker-compose` command |
| Intermediate | **`down` vs `down -v`**: stopping and removing containers vs also deleting named volumes (your data) |
| Intermediate | **Profiles**: starting only part of a stack (`--profile kafka`) to save memory |
| Intermediate | **Project names** (`-p`) and running two copies of a stack without collisions |
| Intermediate | `docker compose config` to see the fully resolved configuration (variables substituted, files merged) |
| Intermediate | Variable substitution from a `.env` file in the project directory vs `env_file` passed into containers — the difference, from a user's point of view |
| Intermediate | `docker compose exec <service> ...` and `docker compose run --rm <service> ...` for one-off commands |
| Advanced | Combining files with `-f` (e.g. a base file plus a local override) |
| Advanced | Updating images safely (`pull` then `up -d`) and recreating a single service |
| Advanced | Waiting for a stack to be healthy before running tests; using health status shown by `docker compose ps` |
| Advanced | Knowing when a problem is in the Compose file (to fix in Module 2.18) vs in how you run it |

**How to learn it**

1. Read the topic file.
2. Take a provided Compose file (for example a PostgreSQL + MinIO + Kafka
   stack from a Stage 2 module) and annotate every line with what it means.
3. Run `docker compose config` and compare it with the original file.

**Hands-on exercise — `docker_lab/07/`**

Using a provided lab stack (PostgreSQL, MinIO, Kafka, schema registry,
Redis — with profiles):

1. Start only the `core` profile, then add the `kafka` profile; observe
   memory use each time.
2. Tail the logs of one service, restart it, and check its health.
3. Run a one-off `psql` session with `docker compose exec` and a one-off
   Python script with `docker compose run --rm`.
4. Stop the stack with `down` and restart it; verify data survives. Then use
   `down -v` in a **copy** of the stack (different project name) and observe
   the data loss.
5. Override one setting (e.g. a published port) with a local override file,
   without editing the provided file.
6. Write a `lab.sh` (or `Makefile`) with `up`, `down`, `logs`, `reset`, and
   `status` commands for your future labs.

**Checkpoint:**

- [ ] Operate a multi-service Compose stack end to end.
- [ ] Use profiles and project names.
- [ ] Explain `down` vs `down -v`.
- [ ] Run one-off commands and override settings without editing the
      provided file.

**Common mistakes:** `down -v` by habit; starting every profile on a laptop
that cannot hold them; editing a shared Compose file instead of overriding
it; confusing the project `.env` file with container environment files.

---

## 9. Phase D — Keeping Your Machine Healthy (Intermediate → Advanced)

### Topic 08 — [Resource limits and laptop capacity](08-resource-limits-and-laptop-capacity.md)

**Why here:** Later Stage 2 stacks (Kafka, Spark, Airflow, Flink, a
catalog, monitoring) can exceed a laptop's memory. You need to measure,
limit, and plan capacity — or your machine will slow to a crawl.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | How much memory and CPU Docker has available on your machine (Docker Desktop settings, WSL2 limits, or the whole host on Linux) |
| Basics | Measuring usage with `docker stats` |
| Intermediate | Per-container limits: `--memory` and `--cpus` (and equivalent Compose settings you will read in provided stacks) |
| Intermediate | What happens at the limit: **memory** → the container is killed (exit code 137); **CPU** → the container is throttled (slower, not killed) |
| Intermediate | **JVM services in containers** (Kafka, Spark, Flink, some catalogs): heap settings must fit inside the container limit, with headroom |
| Intermediate | Estimating a stack's footprint: add up per-service memory at idle and under load (a first taste of Module 2.21's estimation) |
| Advanced | Running only the profiles each exercise needs; stopping idle stacks |
| Advanced | Swap and its effect on performance; why a lab "hangs" instead of failing |
| Advanced | When to move a lab to a small cloud VM instead of your laptop (and the cost trade-off) |

**How to learn it**

1. Read the topic file.
2. Measure idle and loaded memory of each service you ran in this module
   and build a capacity table.
3. Deliberately exceed a memory limit and a CPU limit and compare the
   symptoms.

**Hands-on exercise — `docker_lab/08/`**

1. Record idle and loaded memory/CPU for PostgreSQL, MinIO, Kafka, and
   Redis; project the footprint of a full Stage 2 streaming stack.
2. Run Kafka with a memory limit smaller than its heap and observe the
   kill; fix the heap setting so it fits.
3. Run a CPU-heavy Python container with `--cpus=0.5` and measure the
   slowdown.
4. Set your Docker/WSL2 memory limit deliberately (Topic 10) and document
   the value you chose and why.
5. Write a "lab budget" for your machine: which profiles can run together.

**Checkpoint:**

- [ ] Measure container resource usage.
- [ ] Set memory and CPU limits and explain their effects.
- [ ] Size JVM services inside containers.
- [ ] Plan which services fit on your machine together.

**Common mistakes:** unlimited stacks that freeze the laptop; JVM heaps
larger than container limits; leaving heavy stacks running in the
background for days.

---

### Topic 09 — [Cleanup, disk usage, and housekeeping](09-cleanup-disk-usage-and-housekeeping.md)

**Why here:** Images, stopped containers, volumes, build caches, and logs
silently consume tens of gigabytes. Cleaning up carelessly deletes lab data;
never cleaning up fills your disk.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `docker system df` to see space used by images, containers, volumes, and caches |
| Basics | Removing stopped containers and unused images deliberately |
| Intermediate | **Prune commands** and exactly what each deletes: containers, dangling vs unused images, networks, build cache — and **volumes** (the dangerous one) |
| Intermediate | Dangling images and unused images left by updates |
| Intermediate | **Container log growth**: log files growing without limit, and log size and rotation settings |
| Intermediate | Labelling or naming lab resources so you know what is safe to delete |
| Advanced | A weekly housekeeping routine and a "reset one lab" routine that never touches other labs' volumes |
| Advanced | Where Docker stores data on each platform, and reclaiming space from the virtual disk used by Docker Desktop/WSL2 after cleanup (Topic 10) |
| Advanced | Keeping backups of important volumes before any cleanup (Topic 04) |

**How to learn it**

1. Read the topic file.
2. Run `docker system df` and write down what is using space and why.
3. Predict what each prune command will delete, then run it in a safe
   environment (after backing up anything valuable).

**Hands-on exercise — `docker_lab/09/`**

1. Record `docker system df` before and after a full clean-up of stopped
   containers, dangling images, and build cache.
2. Identify unused volumes, decide which ones hold data you need, back them
   up, and remove only the rest.
3. Configure log size limits for a noisy container and verify log files stop
   growing.
4. Write `housekeeping.sh` that shows usage, removes safe items, and asks
   for confirmation before touching volumes.
5. On Windows/WSL2 or macOS, check whether the virtual disk shrank after
   cleanup and follow the platform's procedure to reclaim space if needed.

**Checkpoint:**

- [ ] Explain what uses disk space in Docker.
- [ ] Use prune commands safely, knowing exactly what each removes.
- [ ] Limit container log growth.
- [ ] Maintain a safe housekeeping routine.

**Common mistakes:** running a "prune everything including volumes" command
and losing lab databases; never cleaning up until the disk is full;
unlimited container logs.

---

### Topic 10 — [Docker Desktop, WSL2, and platform differences](10-docker-desktop-wsl2-and-platform-differences.md)

**Why last:** Everything so far works on every platform — but with
differences in performance, networking, file permissions, memory limits,
and line endings that cause confusing bugs. Knowing your platform's quirks
saves hours in every later module.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | How Docker runs on each platform: natively on Linux; inside a lightweight Linux virtual machine on Windows (WSL2 backend) and macOS |
| Basics | Docker Desktop's role, its settings, and its licensing terms for larger organisations (check current terms) — and alternative runtimes (Podman, Colima, Rancher Desktop) |
| Intermediate | **WSL2 specifics**: keep projects and data inside the Linux filesystem (e.g. your home directory in the distribution), not under `/mnt/c`, for speed and correct permissions |
| Intermediate | **WSL2 resource settings** (memory, CPUs, swap) through its configuration file, and restarting WSL for changes to apply |
| Intermediate | **Line endings**: Windows CRLF line endings breaking shell scripts and config files mounted into Linux containers — Git settings and editor settings to prevent it |
| Intermediate | **Networking differences**: reaching the host from containers, `localhost` forwarding between Windows and WSL2, and host networking support |
| Intermediate | **macOS on Apple silicon (ARM)**: multi-architecture images, emulated `amd64` images, and their performance cost |
| Advanced | File-change watching and bind-mount performance across platforms |
| Advanced | Clock drift in virtual machines after sleep, and its effect on time-sensitive services and tokens |
| Advanced | Reclaiming disk space from Docker's virtual disk on Windows and macOS |
| Advanced | Writing lab instructions that work on all three platforms |

**How to learn it**

1. Read the topic file.
2. Write a short "my platform" page in your notes: runtime, Docker version,
   resource limits, where your projects live, and known quirks.
3. Reproduce one platform-specific bug (e.g. CRLF in a mounted script, or
   slow bind mounts from the Windows filesystem) and fix it.

**Hands-on exercise — `docker_lab/10/`**

1. Measure a database load and a file-heavy Python job with the project in
   the Linux filesystem vs a Windows-mounted path (on WSL2), or vs a bind
   mount on macOS; record the difference.
2. Set explicit memory and CPU limits for WSL2 or Docker Desktop and verify
   them with `docker info` and `docker stats`.
3. Mount a shell script with CRLF endings into a container, observe the
   error, and fix it with Git and editor settings.
4. Connect from a container to a service running on your host machine and
   document the correct address on your platform.
5. On ARM machines, run an image that exists only for `amd64` and document
   the performance impact and alternatives.

**Checkpoint:**

- [ ] Explain how Docker runs on your platform.
- [ ] Configure WSL2 or Docker Desktop resources deliberately.
- [ ] Avoid slow and permission-breaking file locations.
- [ ] Prevent line-ending and architecture problems.

**Common mistakes:** working from `/mnt/c` in WSL2; not limiting WSL2
memory; CRLF scripts in containers; assuming instructions written for Linux
behave identically on macOS and Windows.

---

## 10. Consolidate — practice questions

When all ten topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Predict the outcome of the commands or the cause of the symptom.
2. Reproduce it in a disposable environment.
3. Diagnose from logs, exit codes, and inspect output.
4. Fix it and explain the root cause in one or two sentences.
5. Add the lesson to your personal troubleshooting guide.

---

## 11. Module mini-project — your personal data lab

This mini-project is expanded in
[`../00-Gap-Modules-Overview/Projects/01-dockerized-local-data-lab.md`](../00-Gap-Modules-Overview/Projects/01-dockerized-local-data-lab.md).
The short version:

**Goal:** Assemble and operate a reusable data lab you will use throughout
Stage 2 — without writing Dockerfiles.

1. **Services:** PostgreSQL, MinIO, Kafka (KRaft, with host and container
   listeners), a schema registry, and Redis, operated from a provided or
   adapted Compose stack with profiles (`core`, `kafka`, `cache`).
2. **Connectivity:** a Python `lab_check.py` that verifies every service is
   ready and reachable from the host **and** from a container on the lab
   network.
3. **Persistence:** named volumes for all stateful services, a backup and
   restore script, and a documented "reset" procedure.
4. **Configuration:** credentials in an ignored env file, bound to
   `127.0.0.1`, with no secrets in history or Git.
5. **Capacity:** a resource budget table for your machine and limits that
   keep the lab within it.
6. **Operations:** `lab.sh` or a `Makefile` with `up`, `down`, `status`,
   `logs`, `backup`, `restore`, `reset`, and `housekeeping` commands.
7. **Troubleshooting guide:** your notes from Topic 06 drills and platform
   quirks from Topic 10.

**Grading yourself:** from a clean machine, the lab starts and passes
`lab_check.py` in under 10 minutes using only your README; restarting and
resetting behave exactly as documented; and a friend can diagnose a broken
service using your troubleshooting guide.

---

## 12. Module self-assessment — exit criteria

Only move to Module 2.4 when you can tick every box without looking at your
notes:

- [ ] I can pull, run, and manage containers, and choose image versions and
      architectures deliberately.
- [ ] I can run PostgreSQL, MinIO, Kafka, and Redis and check readiness.
- [ ] I can connect to services from the host and from other containers,
      including Kafka with the right listeners.
- [ ] I can persist, back up, restore, and reset service data safely.
- [ ] I can configure containers without leaking secrets.
- [ ] I can diagnose container failures from logs, exit codes, and inspect
      output.
- [ ] I can operate Compose stacks with profiles, overrides, and one-off
      commands.
- [ ] I can keep my lab within my machine's resources and disk.
- [ ] I know my platform's Docker quirks and how to avoid them.
- [ ] I have finished the practice questions and the mini-project.

---

## 13. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Docker documentation — "Get started", running containers, networking overview, volumes and bind mounts, logs, resource constraints, pruning | 01–09 |
| Docker Compose documentation — CLI reference, profiles, environment variables, merging files | 07 |
| Official image documentation pages for PostgreSQL, MinIO, Apache Kafka, and Redis | 02, 03, 05 |
| Microsoft documentation — WSL2 best practices, `.wslconfig`, Docker Desktop WSL2 backend | 10 |
| Docker Desktop documentation for your platform (settings, resource limits, disk usage) | 08–10 |
| Confluent / Apache Kafka documentation on listeners and advertised listeners | 03 |

---

## 14. Where this module leads

| This module's skill | Where you use it next |
| --- | --- |
| MinIO and object storage in containers | Module 2.4 (DuckDB/Polars over object storage) and every later lake exercise |
| PostgreSQL in containers | Modules 2.6, 2.7, and all projects |
| Kafka listeners and persistence | Module 2.16 and Projects 02 and 05 |
| Operating Compose stacks with profiles | Modules 2.13–2.20 |
| Resource budgeting | Module 2.14 (Spark) and Module 2.21 (performance and capacity) |
| Troubleshooting method | Every lab, and on-call practices in Module 2.20 |
| Writing your own Dockerfiles and Compose files | **Module 2.18** — the author's side of containers |
| Remote servers and long-running services | Gap Module G2 — Linux and Shell for Data Servers |

Containers are the workbench of modern data engineering. The habits you
build here — pin versions, wait for readiness, know which network you are
on, keep data in volumes and back it up, keep secrets out of commands, read
the logs before guessing, and clean up deliberately — will save you time in
every module that follows.
