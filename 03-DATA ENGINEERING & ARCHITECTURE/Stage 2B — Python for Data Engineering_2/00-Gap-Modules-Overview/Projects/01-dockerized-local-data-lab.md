# Project Roadmap — Dockerized Local Data Lab

This is the end-to-end roadmap for **Gap Project 01: Dockerized Local Data
Lab**, the project for **Gap Module G1 — Docker Essentials for Data Labs**.
It takes you from an empty repository to a **production-grade local data
lab**: a reproducible, secure, documented, and easy-to-operate set of
containerised services (PostgreSQL, MinIO, Kafka, a schema registry, and
Redis) that you will use as your workbench for the rest of Stage 2.

"Production grade" for a local lab means: anyone can start it from a clean
clone with one command, it behaves the same every time, it never loses data
by accident, it never exposes services or secrets, it fits in the machine's
resources, it can be diagnosed quickly when something breaks, and it is
documented well enough that someone else can run it without you.

It is written as a sequence of **milestones**. Each milestone has a goal,
tasks, deliverables, and **acceptance criteria**. Commit and tag the
repository at the end of each milestone (`m0`, `m1`, …).

---

## 1. Why this project matters

From Module 2.4 onwards, nearly every exercise needs services: object
storage for the lake, a database, a message broker, a schema registry, a
cache. Without a well-built lab, you lose hours to:

- services that "sometimes" start;
- "connection refused" because of `localhost` confusion or Kafka listeners;
- lost data after a careless `down -v`;
- passwords committed to Git or printed in logs;
- a laptop frozen by containers using all memory;
- a full disk from old images, volumes, and logs;
- instructions that only work on one operating system.

This project turns those lessons from Gap Module G1 into a lab you can
trust — and a small but real example of engineering an internal platform
for other people (including your future self).

---

## 2. Project goal and scope

### Goal

Build `data-lab`, a repository that provides:

1. A **Compose-based stack** of PostgreSQL, MinIO, Kafka (KRaft), a schema
   registry, and Redis — grouped into **profiles** so users start only what
   they need.
2. **Idempotent initialisation** of buckets, databases, schemas, topics, and
   sample data.
3. **Verified connectivity** from the host and from containers on the lab
   network, including correctly configured Kafka listeners.
4. **Data safety**: persistent volumes, backups, restores, and a guarded
   reset.
5. **Safe configuration**: no secrets in Git, history, or logs; services
   bound to `127.0.0.1` only.
6. **Resource budgeting**: known footprints per profile and limits that keep
   the lab within the machine's capacity.
7. An **operations CLI** (`make` or `lab.sh`) for every routine task.
8. A **troubleshooting guide** and a `doctor` command that collects
   diagnostics.
9. **Housekeeping** that keeps disk usage under control.
10. **Automated checks** (locally and in CI) proving the lab works.
11. **Documentation** that lets someone else run and maintain it.

### In scope

- Operating and adapting a Compose stack (using vendor-documented images
  and example configurations, and override files).
- Scripts in Bash and Python for initialisation, checks, backups, and
  operations.

### Out of scope (covered later)

- Writing custom Dockerfiles, multi-stage builds, and authoring Compose
  files from scratch → **Module 2.18** (you will refactor this lab there).
- Spark, Airflow, Flink, and monitoring stacks → added as new profiles in
  later modules (stretch goals list them).

---

## 3. Prerequisites and timing

- **Gap Module G1** completed (all ten topics).
- Stage 0 (command line, OS fundamentals, developer environment) and Stage 1
  (Python, testing, configuration).
- A machine with at least 8 GB RAM (16 GB recommended), Docker Engine with
  Compose v2, and — on Windows — WSL2 with the repository stored **inside
  the Linux filesystem**.

**Estimated effort:** about **1–1.5 weeks** at 8–10 hours per week.

---

## 4. Requirements for the lab (write them down in M0)

| Requirement | Target |
| --- | --- |
| **Cold start** (from a clean clone, images not yet pulled) | `core` profile healthy in under 10 minutes on a typical home connection |
| **Warm start** (images present) | All requested profiles healthy in under 2 minutes |
| **Health** | `make check` reports every running service as ready and reachable from host and network |
| **Repeatability** | Running `make up` and `make init` twice changes nothing |
| **Data safety** | Stopping, restarting, and upgrading the lab never loses data; destructive commands require explicit confirmation and take a backup first |
| **Security** | All published ports bound to `127.0.0.1`; no real credentials; no secrets in Git, logs, or shell history |
| **Resources** | The full lab (all profiles) stays within a documented memory budget (e.g. 6 GB); `core` alone within ~2 GB |
| **Disk** | Housekeeping keeps Docker disk usage within a documented budget |
| **Portability** | Works on Linux and WSL2 (and documented for macOS, including ARM) |
| **Operability** | Every routine task has one command; any common failure is diagnosable with `make doctor` and the troubleshooting guide |

---

## 5. Target design

```text
                     your machine (127.0.0.1 only)
  ┌───────────────────────────────────────────────────────────────────────┐
  │  host tools & Python ── localhost:<published ports> ──┐               │
  │                                                        ▼               │
  │  ┌──────────────────────── Docker network: datalab ─────────────────┐ │
  │  │ profile core : postgres  ·  minio  ·  init-core (one-shot)        │ │
  │  │ profile kafka: kafka (KRaft, internal + external listeners)       │ │
  │  │                schema-registry  ·  init-kafka (one-shot)          │ │
  │  │ profile cache: redis                                               │ │
  │  │ profile tools: kafka-ui (optional) · workbench (Python + clients) │ │
  │  └────────────────────────────────────────────────────────────────────┘ │
  │  named volumes: pg_data · minio_data · kafka_data · redis_data         │
  │  backups/  (host folder, git-ignored)                                  │
  └───────────────────────────────────────────────────────────────────────┘
```

**Connection matrix** (you will complete it in M4):

| Service | From your host | From a container on `datalab` |
| --- | --- | --- |
| PostgreSQL | `127.0.0.1:<pg_port>` | `postgres:5432` |
| MinIO API / console | `127.0.0.1:<api_port>` / `127.0.0.1:<console_port>` | `minio:9000` |
| Kafka | `127.0.0.1:<external_port>` (external listener) | `kafka:<internal_port>` (internal listener) |
| Schema registry | `127.0.0.1:<registry_port>` | `schema-registry:<port>` |
| Redis | `127.0.0.1:<redis_port>` | `redis:6379` |

---

## 6. Repository structure

```text
data-lab/
├── README.md                    # quick start, profiles, connection matrix, commands
├── Makefile                     # (or lab.sh) the operations CLI
├── compose.yaml                 # base stack (adapted from vendor examples)
├── compose.override.example.yaml# per-user overrides (ports, limits) — copy to compose.override.yaml
├── .env.example                 # variables for Compose substitution (ports, versions) — no secrets
├── secrets/                     # generated local secrets (git-ignored), e.g. pg_password.txt
├── init/
│   ├── postgres/                # SQL executed on first init (schemas, roles, sample tables)
│   ├── minio/                   # bucket and policy set-up script
│   └── kafka/                   # topic definitions (name, partitions, config)
├── scripts/
│   ├── generate_secrets.sh
│   ├── lab_check.py             # readiness and connectivity checks (host + network)
│   ├── seed_data.py             # sample data loader (orders, customers, events)
│   ├── backup.sh / restore.sh
│   ├── reset.sh                 # guarded reset with automatic backup
│   ├── housekeeping.sh
│   └── doctor.sh                # diagnostics bundle
├── docs/
│   ├── requirements.md
│   ├── service-cards.md         # per service: image, version, digest, ports, env, volumes, readiness
│   ├── capacity.md              # measured footprints and budgets
│   ├── platform-notes.md        # WSL2 / macOS / Linux specifics
│   ├── troubleshooting.md       # symptom → evidence → cause → fix
│   ├── runbook.md               # upgrades, backups, resets, recovery
│   └── adr/                     # decisions (versions, profiles, registry choice, …)
├── tests/                       # pytest wrappers around checks
├── .gitattributes               # LF line endings for scripts and configs
├── .gitignore                   # secrets/, backups/, compose.override.yaml, .env
└── .github/workflows/lab-ci.yml # CI smoke test (M11)
```

---

## 7. Milestones overview

```text
M0   Framing: requirements, platform notes, and decisions
M1   Repository baseline and safety rails
M2   Service selection, versions, and service cards
M3   The stack: profiles, network, volumes, health, and init services
M4   Connectivity: host vs network, Kafka listeners, and lab_check
M5   Data safety: persistence, seed data, backups, restores, and reset
M6   Configuration and secrets
M7   Resource budgeting and limits
M8   The operations CLI
M9   Troubleshooting guide and the doctor command
M10  Housekeeping and disk budget
M11  Cross-platform verification and automated tests (local + CI)
M12  Documentation, upgrade procedure, and hand-over
(M13 Optional stretch goals)
```

---

## 8. Milestones

### M0 — Framing: requirements, platform notes, and decisions

**Goal:** Know exactly what the lab must do, for whom, on which machines.

**Tasks**

1. Write `docs/requirements.md` from Section 4, adjusted to your machine
   (RAM, CPU, disk, operating system).
2. List the **users** of the lab: you in each Stage 2 module, and a
   classmate or colleague who clones it. Note what each needs (services,
   ports, sample data).
3. Write `docs/platform-notes.md`: Docker runtime and version, WSL2 or
   Docker Desktop resource settings, where the repository lives, and known
   quirks (Gap Module G1 Topic 10).
4. Write the first ADRs: which schema registry image, which profiles exist,
   version-pinning policy (tags **and** digests).

**Acceptance criteria**

- [ ] Requirements have numeric targets.
- [ ] Platform notes describe your actual environment.
- [ ] ADRs record the first decisions with alternatives.

---

### M1 — Repository baseline and safety rails

**Goal:** A repository that makes the safe way the easy way from the first
commit.

**Tasks**

1. Create the structure from Section 6.
2. `.gitignore`: `secrets/`, `backups/`, `.env`, `compose.override.yaml`,
   local data folders.
3. `.gitattributes`: force LF line endings for `*.sh`, `*.sql`, `*.yaml`,
   `*.py`, and config files (prevents CRLF bugs on Windows).
4. `pre-commit` with a **secret scanner** (e.g. gitleaks), YAML and shell
   linting (e.g. `yamllint`, `shellcheck`), and Python formatting (Ruff).
5. A minimal README with the project purpose and "status: under
   construction".

**Acceptance criteria**

- [ ] Committing a fake password is blocked by the secret scanner.
- [ ] Shell scripts pass `shellcheck`; YAML passes `yamllint`.
- [ ] Files checked out on Windows keep LF endings.

---

### M2 — Service selection, versions, and service cards

**Goal:** Every service is chosen deliberately, pinned, and documented.

**Tasks**

1. For each service, write a **service card** in `docs/service-cards.md`:
   image and publisher (prefer official or vendor images), version tag and
   **digest**, supported architectures, ports (container and published),
   required and optional environment variables, data directory to persist,
   readiness check, first-init behaviour, and documentation link.
2. Verify each image supports your CPU architecture (and note emulation on
   ARM if needed).
3. Choose major versions that match what Stage 2 modules use (e.g. a
   PostgreSQL version with logical replication features used in Module 2.9
   and Project 02; Kafka 4.x in KRaft mode).
4. Record upgrade notes: how you will bump versions later (M12).

**Acceptance criteria**

- [ ] Every service card is complete, including digest and readiness check.
- [ ] No image uses `latest`.
- [ ] Every image runs natively (or the emulation cost is documented).

---

### M3 — The stack: profiles, network, volumes, health, and init services

**Goal:** A stack that starts reliably, only as much as needed, and
initialises itself idempotently.

**Tasks**

1. Build `compose.yaml` by **adapting vendor-documented examples** (you are
   operating and configuring, not authoring from scratch — full authoring is
   Module 2.18):
   - services assigned to profiles `core` (PostgreSQL, MinIO), `kafka`
     (Kafka, schema registry), `cache` (Redis), `tools` (a Kafka web UI and
     a `workbench` Python container);
   - one named network `datalab`;
   - named volumes for every stateful service;
   - published ports bound to **`127.0.0.1`**, with port numbers from
     `.env` so users can change them;
   - health checks (from image documentation) and start-up ordering based on
     health.
2. Add **one-shot init services** that run after dependencies are healthy
   and are **idempotent**:
   - `init-core`: create MinIO buckets (`landing`, `lake`, `backups`) and
     policies; PostgreSQL schemas and a least-privilege `app` role (SQL files
     that run only on first init, plus a re-runnable script for later
     changes);
   - `init-kafka`: create topics from `init/kafka/topics.yaml` with
     partitions and retention, skipping existing ones.
3. Provide `compose.override.example.yaml` for personal changes (ports,
   limits) — never edit `compose.yaml` for personal preferences.
4. Configure **log size limits** for every service (json-file max size and
   file count).

**Acceptance criteria**

- [ ] `docker compose --profile core up -d` starts only PostgreSQL, MinIO,
      and `init-core`; adding `--profile kafka` adds Kafka services.
- [ ] Running init services twice changes nothing and reports "already
      exists".
- [ ] `docker compose ps` shows all long-running services as healthy.
- [ ] No port is published on `0.0.0.0`.

---

### M4 — Connectivity: host vs network, Kafka listeners, and lab_check

**Goal:** Every service is reachable from the host **and** from the lab
network with the correct address — proven automatically.

**Tasks**

1. Configure Kafka with **two listeners**: an internal one advertised as
   `kafka:<port>` for containers, and an external one advertised as
   `localhost:<port>` for host clients (G1 Topic 03). Configure the schema
   registry to use the internal listener.
2. Complete the **connection matrix** in the README.
3. Write `scripts/lab_check.py` (Python, standard library plus client
   libraries) that, with timeouts and clear output:
   - checks readiness of each **running** service (skips services whose
     profile is not active);
   - connects to PostgreSQL and runs a query;
   - lists MinIO buckets and writes/reads/deletes a test object;
   - produces and consumes a test message on Kafka and registers/reads a
     test schema;
   - sets and gets a Redis key;
   - exits non-zero with a precise message on the first failure.
4. Run the same checks **inside** the `workbench` container using internal
   addresses (`make check-network`).

**Acceptance criteria**

- [ ] `lab_check.py` passes from the host and from the workbench container.
- [ ] A Kafka client on the host and one in a container can both produce and
      consume.
- [ ] Failures name the service, the address tried, and the likely cause.

---

### M5 — Data safety: persistence, seed data, backups, restores, and reset

**Goal:** Lab data survives everything except an explicit, confirmed reset
— and even then, a backup exists.

**Tasks**

1. Verify persistence: restart containers, recreate containers, and restart
   the Docker engine; data remains.
2. Write `scripts/seed_data.py` to load a small, **seeded** sample dataset
   (customers, orders, events) into PostgreSQL, MinIO (as Parquet or JSON
   Lines), and a Kafka topic — idempotently.
3. Write `scripts/backup.sh`:
   - PostgreSQL: a logical dump (`pg_dump`) **and/or** a volume archive
     taken with the service stopped;
   - MinIO: mirror buckets to `backups/` (or archive the volume);
   - Kafka and Redis: volume archives (documenting that Kafka backups are
     for lab convenience, not production practice);
   - timestamped backup folders with a manifest (service, method, size,
     checksum).
4. Write `scripts/restore.sh` that restores a chosen backup into an empty
   stack and verifies it with `lab_check.py` and row counts.
5. Write `scripts/reset.sh`: shows exactly what will be deleted, requires
   typing a confirmation word, **takes a backup first**, then removes
   containers and volumes for the chosen profiles only.

**Acceptance criteria**

- [ ] Data survives container recreation and engine restarts.
- [ ] Backup → reset → restore brings back identical row counts, objects,
      and topic contents (verified by a script).
- [ ] `reset` cannot run without confirmation and always backs up first.
- [ ] Seeding twice does not duplicate data.

---

### M6 — Configuration and secrets

**Goal:** Configuration is easy to change, and secrets never leak.

**Tasks**

1. Separate **non-secret configuration** (`.env` for Compose substitution:
   ports, versions, profiles) from **secrets** (`secrets/*.txt`,
   git-ignored).
2. Write `scripts/generate_secrets.sh` that creates random lab passwords on
   first run (never overwriting existing ones) with owner-only file
   permissions.
3. Pass secrets to services using file-based secret variables where images
   support them (G1 Topic 05); otherwise use environment variables sourced
   from the secret files at start-up — never typed in commands.
4. Make scripts read credentials from the secret files; mask them in all
   output.
5. Document first-initialisation-only settings (e.g. changing the
   PostgreSQL password requires a procedure, not just editing a file) in
   `docs/runbook.md`.
6. Check leakage: search `docker inspect` output, script output, and shell
   history for the generated passwords; fix any exposure you find.

**Acceptance criteria**

- [ ] A fresh clone generates its own secrets; none are committed.
- [ ] No password appears in logs, script output, or shell history.
- [ ] The password-rotation procedure works and is documented.

---

### M7 — Resource budgeting and limits

**Goal:** The lab fits comfortably on the machine, and users know which
profiles they can run together.

**Tasks**

1. Measure idle and loaded memory and CPU for each service with
   `docker stats` (load: seed data plus a short produce/consume and query
   burst).
2. Set memory and CPU limits per service in the override example; size the
   **Kafka JVM heap** (and any other JVM service) to fit inside its limit
   with headroom.
3. Configure the Docker runtime or WSL2 memory and CPU limits deliberately
   (G1 Topics 08, 10) and document them.
4. Write `docs/capacity.md`: per-service footprint, per-profile totals, and
   a table of which profile combinations fit on 8 GB and 16 GB machines.
5. Test the limit: run with too little memory for Kafka and record the
   symptom (exit code 137) in the troubleshooting guide.

**Acceptance criteria**

- [ ] Measured footprints for every service and profile are documented.
- [ ] The full lab stays within the documented budget under load.
- [ ] Limits prevent the lab from freezing the machine.

---

### M8 — The operations CLI

**Goal:** Every routine task is one short, safe, self-documenting command.

**Tasks**

Create a `Makefile` (or `lab.sh`) with at least:

| Command | Behaviour |
| --- | --- |
| `make help` | Lists all commands with one-line descriptions |
| `make up PROFILES="core kafka"` | Generates secrets if missing, starts profiles, waits for health, runs init |
| `make down` | Stops and removes containers, **keeps** volumes |
| `make status` | Services, health, published ports, profile summary |
| `make logs SERVICE=kafka` | Follows logs for one service |
| `make check` / `make check-network` | Runs `lab_check.py` from host / inside workbench |
| `make seed` | Loads sample data idempotently |
| `make psql` / `make kafka-shell` / `make mc` | Opens a client session inside the network |
| `make backup` / `make restore BACKUP=<id>` | Backup and restore |
| `make reset PROFILES=...` | Guarded reset (confirmation + backup) |
| `make housekeeping` | Safe cleanup (M10) |
| `make doctor` | Diagnostics bundle (M9) |

Every command prints what it is doing, fails with a clear message and
non-zero exit code, and is safe to run twice.

**Acceptance criteria**

- [ ] A new user can operate the lab using only `make help` and the README.
- [ ] All commands are idempotent and fail clearly.
- [ ] No command deletes volumes except `reset`.

---

### M9 — Troubleshooting guide and the doctor command

**Goal:** Common failures are diagnosed in minutes, by anyone.

**Tasks**

1. Run the **broken-lab drills** from G1 Topic 06 against your lab and add
   each to `docs/troubleshooting.md` in the format: **symptom → commands to
   run → evidence → cause → fix**. Include at least:
   - port already in use;
   - PostgreSQL failing on missing or changed password;
   - Kafka client connecting then failing (listener misconfiguration);
   - Kafka OOM-killed (exit code 137);
   - permission denied on a bind mount;
   - init service failing and leaving a service half-configured;
   - CRLF line endings in a mounted script;
   - disk full;
   - wrong image architecture.
2. Write `scripts/doctor.sh` that collects, into a timestamped folder
   (secrets redacted): Docker and Compose versions, `docker info` summary,
   runtime resource limits, `docker compose ps` with health, the last 200
   log lines per service, `docker system df`, disk space, port listeners,
   and the results of `lab_check.py`.

**Acceptance criteria**

- [ ] Every drill is documented with a verified fix.
- [ ] `make doctor` produces a redacted bundle that is enough to diagnose
      each drill without further access.

---

### M10 — Housekeeping and disk budget

**Goal:** The lab's disk usage stays predictable, and cleanup never
destroys lab data.

**Tasks**

1. Set a **disk budget** (e.g. images ≤ 10 GB, volumes ≤ 20 GB, logs ≤ 1 GB)
   in `docs/capacity.md`.
2. Label lab resources (project name, labels) so cleanup can target them
   precisely.
3. Write `scripts/housekeeping.sh`:
   - show `docker system df` before and after;
   - remove stopped lab containers, dangling images, and old build cache;
   - list unused **volumes** but never delete them without explicit
     confirmation (and never lab data volumes);
   - delete backups older than a retention period (keeping the latest N);
   - report whether the platform's virtual disk needs compaction (WSL2 or
     macOS) and link to the procedure.
4. Verify log size limits keep container logs within budget.

**Acceptance criteria**

- [ ] Housekeeping frees space without touching lab data volumes.
- [ ] Backups follow the retention rule.
- [ ] Disk usage stays within budget after a week of normal use.

---

### M11 — Cross-platform verification and automated tests (local + CI)

**Goal:** Prove the lab works — repeatedly, on more than one machine — and
keep proving it after changes.

**Tasks**

1. Wrap checks in **pytest** (`tests/`): start the `core` (and optionally
   `kafka`) profile, run `lab_check.py`, run seed and backup/restore
   round-trip tests, and tear down.
2. Add a **CI workflow** (GitHub Actions on an Ubuntu runner) that on every
   pull request: runs linters and the secret scanner, starts the `core`
   profile with generated secrets, waits for health, runs the checks, and
   tears everything down (keep it within CI resource limits).
3. Verify on **WSL2** (and on a second environment if possible — Linux,
   macOS, or a colleague's machine); record results and differences in
   `docs/platform-notes.md`.
4. Measure cold-start and warm-start times against the M0 targets.
5. Run the full sequence 5 times in a row (up → seed → check → backup → reset
   → restore → check) to prove repeatability.

**Acceptance criteria**

- [ ] CI passes on every pull request.
- [ ] The repeatability sequence passes 5 times in a row.
- [ ] Cold and warm start times meet the targets (or deviations are
      explained).
- [ ] At least one environment other than your own has run the lab
      successfully (or the plan for it is documented).

---

### M12 — Documentation, upgrade procedure, and hand-over

**Goal:** Someone else can run, fix, and upgrade the lab without you.

**Tasks**

1. Finalise the **README**: what the lab is, prerequisites, quick start (3
   commands), profiles and their footprints, connection matrix, command
   list, where data lives, and links to docs.
2. Finalise `docs/runbook.md`:
   - **upgrade procedure**: back up → change the pinned version and digest
     in `.env`/service cards → pull → recreate one service at a time →
     `make check` → roll back to the previous version and restore the backup
     if checks fail;
   - password rotation, full recovery from backups, and moving the lab to a
     new machine.
3. Perform one real **upgrade** (e.g. a minor version bump of PostgreSQL or
   MinIO) following the runbook, and one deliberate **rollback**.
4. **Hand-over test**: give the repository to someone else (or use a fresh
   user account/VM) and time how long it takes them to reach a green
   `make check` using only the README.
5. Write a short **retrospective**: what went wrong, what you would change
   when you author the stack yourself in Module 2.18.

**Acceptance criteria**

- [ ] A new user reaches a green `make check` from the README alone within
      the cold-start target plus 10 minutes.
- [ ] An upgrade and a rollback have been executed successfully by following
      the runbook.
- [ ] All docs are consistent with the actual commands and behaviour.

---

### M13 — Optional stretch goals

- **Future profiles:** add `spark` (Module 2.14), `airflow` (Module 2.13),
  `lakehouse` (an Iceberg REST catalog — Module 2.15), `observability`
  (Prometheus and Grafana — Module 2.20), and `sftp` (Module 2.9) profiles,
  each with capacity measurements and checks.
- **Dev container:** a development-container configuration so an IDE opens
  directly inside the `workbench`.
- **Alternative runtimes:** verify the lab on Podman or Colima and document
  differences.
- **Metrics:** export container metrics to a small Prometheus + Grafana
  profile.
- **Module 2.18 refactor:** after Module 2.18, rewrite the stack from
  scratch as an author (custom images, cleaner Compose design) and compare.

---

## 9. Definition of done

- [ ] One command starts any combination of profiles to a healthy, checked
      state; running it twice changes nothing.
- [ ] Connectivity is verified from the host and from the network, including
      Kafka with dual listeners.
- [ ] Data survives restarts and upgrades; backup → reset → restore is
      proven; resets are guarded.
- [ ] No secret in Git, logs, output, or history; all ports bound to
      `127.0.0.1`.
- [ ] Documented, enforced resource and disk budgets.
- [ ] Operations CLI, troubleshooting guide, and doctor bundle cover common
      failures.
- [ ] Local tests and CI pass; repeatability and cross-platform results
      recorded.
- [ ] README, service cards, capacity, platform notes, runbook (including
      upgrades), ADRs, and retrospective complete.

---

## 10. Evaluation rubric (self or peer review)

Score each area from 0 to 3. A production-grade lab scores **at least 2 in
every area** and **3 in Reliability, Data safety, and Security**.

| Area | What a "3" looks like |
| --- | --- |
| Reliability | Health-gated, idempotent start and init; repeatability proven 5× and in CI |
| Connectivity | Correct host/network addressing; Kafka listeners right; automated checks with clear failures |
| Data safety | Volumes everywhere; tested backup/restore; guarded reset with automatic backup |
| Security | Localhost-only ports; generated secrets; no leaks; secret scanning enforced |
| Resource awareness | Measured footprints; limits and JVM sizing; profile combinations documented |
| Operability | Complete, idempotent CLI; doctor bundle; troubleshooting guide from real drills |
| Maintainability | Pinned versions with digests; upgrade and rollback executed via runbook |
| Portability | LF enforcement; verified on WSL2 plus another environment or clearly documented |
| Documentation | A stranger reaches green checks from the README alone |

---

## 11. Common pitfalls to avoid

- Using `latest` tags, so the lab changes under you.
- Publishing ports on all interfaces.
- `docker compose down -v` in a script or muscle memory.
- Init scripts that fail on the second run.
- A single Kafka listener that works only from the host or only from
  containers.
- Passwords in `compose.yaml`, `.env` committed to Git, or typed into
  commands.
- Starting every profile on an 8 GB laptop.
- Keeping the repository under `/mnt/c` on WSL2.
- CRLF line endings in shell scripts.
- A troubleshooting guide written from memory instead of real drills.

---

## 12. Suggested timeline

| Day | Milestones |
| --- | --- |
| 1 | M0 framing · M1 repository baseline · M2 service cards |
| 2 | M3 stack, profiles, and init services |
| 3 | M4 connectivity and `lab_check` |
| 4 | M5 data safety · M6 configuration and secrets |
| 5 | M7 resources · M8 operations CLI |
| 6 | M9 troubleshooting and doctor · M10 housekeeping |
| 7 | M11 tests and CI |
| 8 | M12 documentation, upgrade, hand-over, retrospective |
| Optional | M13 stretch goals |

---

## 13. What to show in a portfolio or interview

This small project demonstrates platform thinking. Be ready to explain:

1. How the lab guarantees a healthy, repeatable start (health checks,
   idempotent init).
2. Why Kafka needs separate internal and external listeners.
3. How you prevent data loss (volumes, backups, guarded reset, tested
   restore).
4. How secrets are generated, stored, and kept out of logs and Git.
5. How you sized memory (including JVM heaps) and which profiles fit where.
6. How someone diagnoses a failure with `make doctor` and the
   troubleshooting guide.
7. How you upgrade a service safely and roll back.
8. What CI proves on every change.

A short README, a demo recording (clean clone → `make up` → `make check` →
backup → reset → restore → `make check`), and the troubleshooting guide are
enough to show you can build tooling other engineers can rely on.
