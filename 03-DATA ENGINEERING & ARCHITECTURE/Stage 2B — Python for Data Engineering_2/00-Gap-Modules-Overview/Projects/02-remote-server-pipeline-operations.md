# Project Roadmap — Remote Server Pipeline Operations

This is the end-to-end roadmap for **Gap Project 02: Remote Server Pipeline
Operations**, the project for **Gap Module G2 — Linux and Shell for Data
Servers**. It takes you from nothing to a **production-grade** small data
pipeline running on a **private Linux server that is reachable only
through a bastion** — deployed, scheduled, monitored, backed up,
recoverable, secured, and documented well enough that someone else can
operate it.

"Production grade" here means: the server can be rebuilt from scripts in
minutes; the pipeline survives reboots, disconnections, and missed
schedules; deployments are atomic and can be rolled back; failures alert a
human with enough context to act; data is backed up and restorable; no
service runs as root; and every routine and emergency task has a written,
tested procedure.

It is written as a sequence of **milestones**. Each milestone has a goal,
tasks, deliverables, and **acceptance criteria**. Commit and tag the
repository at the end of each milestone (`m0`, `m1`, …).

---

## 1. Why this project matters

Even in a world of managed services, data engineers constantly work on
Linux machines: VMs running extractors and agents, edge servers receiving
partner files, database hosts, Spark and Airflow nodes, and the machines
underneath managed platforms when things go wrong. Typical real-world
problems include:

- a nightly job that silently stopped after a reboot;
- a partner file processed while still uploading;
- a full disk from spill files and unrotated logs;
- a service killed by the OOM killer with no alert;
- a deployment that broke production with no way back;
- a server nobody can rebuild because it was configured by hand years ago;
- shared root access and passwords in world-readable files.

This project makes you solve each of these deliberately, on a server you
cannot click around in.

---

## 2. Project goal and scope

### Goal

Build and operate `pipeline-host`, consisting of:

1. **Infrastructure**: a bastion host, a private **data server**, and a
   simulated **partner server** — with the data server reachable only
   through the bastion.
2. **Access**: key-based SSH with jump hosts, tunnels for internal tools,
   and an access guide.
3. **Bootstrap**: an idempotent script that turns a fresh server into a
   hardened, ready data server.
4. **Deployment**: atomic, versioned releases of a Python pipeline package
   with one-command rollback.
5. **Pipeline workloads**:
   - an **hourly extraction job** (API or generated source) writing Parquet
     and JSON Lines to a data disk;
   - a **partner file pull** over SSH/rsync with completeness checks,
     checksums, and a file registry;
   - a **long-running service** (a small consumer or HTTP API) that must
     stay up;
   - an **upload of outputs** to object storage with rclone.
6. **Scheduling and supervision** with systemd services and timers.
7. **Monitoring and alerting** for failures, freshness, disk, and memory.
8. **Backups and recovery**, including a rebuild-from-scratch drill.
9. **Incident drills**, a runbook, and a security review.

### In scope

- Linux server operations using the skills from Gap Modules G1 and G2:
  SSH, tunnels, tmux, rsync/rclone, systemd, journald, monitoring tools,
  disk management, command-line data tools, logrotate, users, sudo,
  packages, firewall, time sync.
- Python for the pipeline code and small checks.

### Out of scope (covered later)

- Orchestrators such as Airflow (Module 2.13), container-based deployment
  and infrastructure as code (Module 2.18), and managed cloud services
  (Modules 2.17, G3, G4). The final retrospective asks what each would
  change.

---

## 3. Prerequisites and timing

- **Gap Modules G1 and G2** completed.
- Stage 0 and Stage 1 skills (command line, OS fundamentals, Python,
  testing, configuration, logging).
- Optional but helpful: Modules 2.1–2.5 for the data-format parts.

**Estimated effort:** about **1.5–2 weeks** at 8–10 hours per week.

---

## 4. Requirements and service levels (write them down in M0)

| Requirement | Target |
| --- | --- |
| **Access** | The data server has no public SSH; access only via the bastion with keys |
| **Freshness** | Hourly extraction outputs are at most **90 minutes** old; partner files are processed within **30 minutes** of a complete delivery |
| **Resilience** | Jobs and services survive reboots and SSH disconnections; missed schedules run after downtime |
| **Availability** | The long-running service restarts automatically after crashes, within limits |
| **Detection** | A failed run, a stale output, a disk above 80%, or a crash-looping service triggers an alert within **15 minutes** |
| **Deployments** | Releases are atomic; rollback in **under 2 minutes** |
| **Recovery** | A destroyed data server is rebuilt, redeployed, and restored in **under 30 minutes** |
| **Security** | No service runs as root; no password logins; secrets readable only by the service account; firewall allows SSH only from the bastion |
| **Operability** | Every routine and incident procedure is written and has been executed at least once |

---

## 5. Target architecture

```text
 your laptop
   │  ssh (keys, ProxyJump) · tunnels (127.0.0.1 only)
   ▼
 ┌──────────────┐      private network (no public access)       ┌────────────────────┐
 │  bastion     │ ─────────────────────────────────────────────►│  data server       │
 │  (public SSH)│                                               │  /opt/pipeline/…   │
 └──────────────┘                                               │  /data (data disk) │
                                                                │  systemd units     │
 ┌──────────────┐   rsync over SSH (pull, read-only key)        │  - extract.timer   │
 │ partner      │ ◄─────────────────────────────────────────────│  - partner-pull.timer
 │ server       │   files + .done markers + manifests           │  - service (API/   │
 └──────────────┘                                               │    consumer)       │
                                                                │  - healthcheck.timer
                                                                │  - backup.timer    │
                                                                └─────────┬──────────┘
                                                                          │ rclone (outputs, backups)
                                                                          ▼
                                                           object storage (MinIO lab or cloud bucket)
                                                                          │
                                                                alerts → webhook / email / chat
```

### Practice environment options

| Option | How | Notes |
| --- | --- | --- |
| **Containers** | SSH-enabled Linux containers on private Docker networks (bastion on two networks; data and partner servers only on the private one) | Cheapest and fastest; systemd inside containers needs special images or is simulated — prefer VMs for systemd realism |
| **Local VMs** (recommended) | Three small Ubuntu VMs (e.g. Multipass or Vagrant) with a host-only/private network | Realistic systemd, disks, OOM behaviour |
| **Cloud VMs** | A bastion in a public subnet and servers in a private subnet, with a budget alert | Most realistic; destroy after each session |

Record your choice in an ADR.

---

## 6. Repository structure

```text
pipeline-host/
├── README.md                      # what it is, how to access, how to deploy, how to operate
├── ssh/
│   └── config.example             # Host entries for bastion, data server, partner (no keys)
├── bootstrap/
│   ├── bootstrap.sh               # idempotent server set-up
│   ├── files/                     # sshd drop-ins, sudoers rule, logrotate, journald, sysstat, firewall
│   └── verify.sh                  # checks that the server matches the desired state
├── app/                           # the Python pipeline package (uv project)
│   ├── src/pipeline/              # extract, partner_pull, service, healthcheck, upload
│   ├── tests/
│   └── pyproject.toml / uv.lock
├── deploy/
│   ├── deploy.sh                  # build → upload → install → switch → restart → verify
│   ├── rollback.sh
│   └── units/                     # systemd service and timer files
├── ops/
│   ├── status.sh                  # one-screen operational status
│   ├── backup.sh / restore.sh
│   ├── inspect/                   # jq / csvkit / Miller / DuckDB inspection scripts
│   └── tunnels.sh
├── docs/
│   ├── requirements.md
│   ├── architecture.md
│   ├── access-guide.md
│   ├── runbook.md
│   ├── incidents/                 # drill timelines and post-mortems
│   ├── security-review.md
│   └── adr/
└── .github/workflows/ci.yml       # lint and tests (optional but recommended)
```

---

## 7. Milestones overview

```text
M0   Framing: requirements, architecture, and decisions
M1   Practice infrastructure: bastion, data server, and partner server
M2   Access: SSH configuration, keys, jump hosts, and tunnels
M3   Server bootstrap: an idempotent, hardened data server
M4   Application packaging and atomic deployments
M5   Data movement: partner pulls and object-storage uploads
M6   Services and scheduling with systemd
M7   Monitoring, health checks, and alerting
M8   Command-line data inspection toolkit
M9   Backups, recovery, and rebuild from scratch
M10  Incident drills and post-mortems
M11  Security review and hygiene
M12  Documentation, operations checklists, and hand-over
(M13 Optional stretch goals)
```

---

## 8. Milestones

### M0 — Framing: requirements, architecture, and decisions

**Goal:** A clear definition of what the server must do, how well, and how
you will prove it.

**Tasks**

1. Write `docs/requirements.md` from Section 4, adjusted to your
   environment.
2. Draw the architecture (Section 5) in `docs/architecture.md`, including
   every network path, port, user, and directory.
3. Define the **directory layout** on the data server, for example:
   `/opt/pipeline/releases/<version>`, `/opt/pipeline/current` (symlink),
   `/etc/pipeline/` (configuration and secrets), `/data/landing`,
   `/data/output`, `/data/tmp`, `/data/state`, `/var/log/pipeline`.
4. Write ADRs: practice environment, source for the extraction job (a
   public/mock API or generated data), long-running service choice, alert
   channel, and object storage target.

**Acceptance criteria**

- [ ] Requirements are measurable.
- [ ] Every path, user, port, and network in the design is documented.

---

### M1 — Practice infrastructure: bastion, data server, and partner server

**Goal:** A realistic network where the data server is private.

**Tasks**

1. Create the three hosts with your chosen option; give the data server an
   **additional disk** (virtual disk or loopback file) for `/data`.
2. Ensure only the bastion is reachable from your laptop; the data server
   and partner server accept connections only from the private network.
3. On the partner server, create a `partner` upload area and a script that
   simulates deliveries: CSV files uploaded **slowly** (partial file visible
   for a while), then a `.done` marker and a manifest with checksums and row
   counts — sometimes late, sometimes re-sent, occasionally corrupted.
4. Record hosts, addresses, and roles in `docs/architecture.md`.

**Acceptance criteria**

- [ ] The data server is unreachable from your laptop except through the
      bastion.
- [ ] The partner simulator produces all delivery behaviours on demand.

---

### M2 — Access: SSH configuration, keys, jump hosts, and tunnels

**Goal:** Fast, safe, repeatable access — for you and for the pipeline.

**Tasks**

1. Create separate Ed25519 keys (with passphrases for humans): one for your
   admin access, one for the deployment script, and a **restricted key** the
   data server uses to pull from the partner server (read-only, limited to
   the partner directory, no shell where possible).
2. Write `ssh/config.example` with `ProxyJump`, keep-alives, connection
   multiplexing, and per-host keys (`IdentitiesOnly`).
3. **Pin host keys**: record fingerprints in `known_hosts`; document how to
   handle a legitimate host-key change.
4. Configure **tunnels** (`LocalForward`, bound to `127.0.0.1`) to the data
   server's database or status page; write `ops/tunnels.sh` to open, check,
   and close them.
5. Write `docs/access-guide.md`: how to get access, connect, open tunnels,
   and revoke a key.

**Acceptance criteria**

- [ ] `ssh data-server` works in one command through the bastion.
- [ ] The partner-pull key can read partner files and nothing else.
- [ ] Tunnels are bound to localhost only and documented.

---

### M3 — Server bootstrap: an idempotent, hardened data server

**Goal:** A fresh server becomes a ready, hardened data server by running
one script — and running it again changes nothing.

**Tasks**

1. Write `bootstrap/bootstrap.sh` (Bash, `set -euo pipefail`, clear logging)
   that idempotently:
   - sets time zone to **UTC** and enables time synchronisation;
   - installs and pins required packages (Python toolchain via `uv`,
     `rsync`, `rclone`, `jq`, `csvkit`/Miller, DuckDB CLI, `sysstat`,
     `tmux`, a firewall tool);
   - creates the **`pipeline` service account** (no login shell) and an
     `operators` group with a **limited sudo rule** (e.g. only
     start/stop/restart/status of pipeline units and reading their logs);
   - hardens SSH (no password auth, no root login, allowed users only);
   - configures the **firewall** (SSH only from the bastion; service port
     only from the bastion/private network);
   - formats (if new) and mounts the **data disk** at `/data` by UUID with a
     failure-tolerant option; creates the directory layout with correct
     ownership and permissions;
   - installs **logrotate** rules, **journald** size limits, and enables
     **sysstat** history;
   - enables automatic security updates.
2. Write `bootstrap/verify.sh` that checks every desired state and prints
   pass/fail.
3. Run bootstrap on a fresh server, run it again, and verify.

**Acceptance criteria**

- [ ] A fresh server passes `verify.sh` after one bootstrap run.
- [ ] A second run makes no changes (report says "already configured").
- [ ] Password SSH and root SSH are refused; SSH from outside the bastion is
      blocked.
- [ ] `/data` survives a reboot; the server boots even if the data disk is
      missing (documented behaviour).

---

### M4 — Application packaging and atomic deployments

**Goal:** Code reaches the server reproducibly, switches over atomically,
and can be rolled back in seconds.

**Tasks**

1. Build the pipeline as a Python package (`app/`) with a `uv` lock file,
   tests, and CLI entry points: `pipeline extract`, `pipeline partner-pull`,
   `pipeline serve`, `pipeline healthcheck`, `pipeline upload`.
2. The extraction job: fetch data from the chosen source for a **data
   interval** (the hour), write Parquet and JSON Lines to
   `/data/output/<dataset>/dt=YYYY-MM-DD/hour=HH/` atomically (temp file then
   rename), and record run metadata (start, end, rows, status) in
   `/data/state`. It must be idempotent for the same hour.
3. Write `deploy/deploy.sh`:
   - run tests locally;
   - build a release artefact (source plus lock file, or a wheel) tagged
     with the Git commit;
   - `rsync` it to `/opt/pipeline/releases/<version>` over the jump host;
   - create the virtual environment on the server from the lock file;
   - atomically switch the `/opt/pipeline/current` symlink;
   - reload/restart units; run `pipeline healthcheck`;
   - keep the last N releases.
4. Write `deploy/rollback.sh` that switches `current` to the previous
   release and restarts services.
5. Store configuration in `/etc/pipeline/pipeline.toml` and secrets in
   `/etc/pipeline/secrets.env` (owner `pipeline`, mode `0600`).

**Acceptance criteria**

- [ ] A deployment takes one command and verifies itself.
- [ ] Rolling back takes under 2 minutes and restores the previous
      behaviour.
- [ ] Rerunning the extraction for the same hour produces identical output.
- [ ] Secrets are readable only by the `pipeline` user.

---

### M5 — Data movement: partner pulls and object-storage uploads

**Goal:** Files move reliably, completely, exactly once, and verifiably.

**Tasks**

1. `pipeline partner-pull`:
   - list partner deliveries over SSH with the restricted key;
   - process only deliveries with a **`.done` marker**;
   - `rsync` files to `/data/landing/partner/<delivery>/` with partial-file
     handling;
   - verify **SHA-256 checksums** and row counts against the manifest;
   - record each file in a **file registry** (SQLite or PostgreSQL in
     `/data/state`) with status, checksum, and timestamps, so each delivery
     is processed exactly once (Module 2.9 ideas);
   - handle corrected re-sends and quarantine corrupted files with a
     reason.
2. `pipeline upload`: sync `/data/output` to object storage with **rclone**
   (`copy`, never `sync` with deletes unless intended), **throttled**, with
   `rclone check` verification and a run record.
3. Use `rsync --dry-run` and `rclone --dry-run` in tests of the scripts.

**Acceptance criteria**

- [ ] Half-uploaded files are never processed.
- [ ] Re-running the pull does not reprocess completed deliveries.
- [ ] Corrupted files are quarantined and alerted, not loaded.
- [ ] Uploaded outputs verify with checksums; bandwidth stays within the
      configured limit.

---

### M6 — Services and scheduling with systemd

**Goal:** Jobs run on schedule, never overlap, recover from downtime, and
services stay up — all supervised by systemd.

**Tasks**

1. Write unit files in `deploy/units/`:
   - `pipeline-extract.service` (oneshot, `User=pipeline`,
     `EnvironmentFile=`, working directory, timeouts) and
     `pipeline-extract.timer` (hourly, `Persistent=true`, small randomised
     delay);
   - `pipeline-partner-pull.service` + `.timer` (every 10 minutes,
     persistent);
   - `pipeline-upload.service` + `.timer`;
   - `pipeline-service.service` (the long-running consumer or API):
     `Restart=on-failure`, restart delay, start-limit protection, graceful
     stop with `SIGTERM` handling in your code, **`MemoryMax`** and CPU
     quota;
   - basic hardening options (no new privileges, read-only system paths,
     private temp directory, write access only to needed paths).
2. Prevent **overlapping runs** (oneshot semantics plus a lock file in the
   code) and document the behaviour when a run takes longer than its
   interval.
3. Add an **`OnFailure=`** unit (`pipeline-alert@.service`) that sends an
   alert with the failed unit name and the last log lines (M7).
4. Test: reboot the server and confirm timers and services resume; stop the
   server over a scheduled time and confirm missed runs execute after boot.

**Acceptance criteria**

- [ ] All units run as `pipeline`, never root.
- [ ] Missed runs execute after downtime; runs never overlap.
- [ ] The service restarts after crashes and stops cleanly.
- [ ] Every failure triggers the `OnFailure` alert.

---

### M7 — Monitoring, health checks, and alerting

**Goal:** Problems are detected within 15 minutes and explained clearly.

**Tasks**

1. `pipeline healthcheck` (run by `pipeline-healthcheck.timer` every 5
   minutes) checks and reports:
   - **freshness**: age of the latest successful extract and partner
     delivery vs SLOs;
   - **failed units** and crash-looping services;
   - **disk** usage and inodes on `/` and `/data` (warn at 80%, critical at
     90%);
   - **memory pressure** and recent **OOM kills** (kernel log);
   - **time sync** status;
   - **object-storage upload** backlog.
2. Send alerts to your chosen channel (webhook to chat, email, or a local
   receiver) with: host, check, value, threshold, since when, and runbook
   link. Deduplicate repeated alerts (e.g. re-alert only every hour while a
   problem continues).
3. Write `ops/status.sh`: one screen showing units and timers (next and last
   runs), last run results, freshness, disk, memory, and open alerts.
4. Keep **sysstat** history and document how to investigate past
   slowdowns (G2 Topic 06).

**Acceptance criteria**

- [ ] Each detection requirement in Section 4 has an automated check.
- [ ] Alerts contain enough context to start diagnosis without logging in.
- [ ] `ops/status.sh` answers "is everything healthy?" in one screen.

---

### M8 — Command-line data inspection toolkit

**Goal:** Operators can validate data on the server quickly — and the
pipeline uses the same checks as pre-flight gates.

**Tasks**

1. Write scripts in `ops/inspect/`:
   - `partner_file_profile.sh`: row counts, column stats, invalid values in
     a partner CSV (csvkit or Miller);
   - `output_summary.sh`: rows per hour and basic aggregates from Parquet
     outputs using the **DuckDB CLI**;
   - `api_sample.sh`: extract and flatten fields from saved API responses
     with **jq**;
   - `find_run.sh`: all log lines for a run id across journal and
     application logs (jq for JSON logs).
2. Integrate a **pre-flight check** into partner processing (e.g. required
   columns and non-negative amounts) that quarantines files failing basic
   rules.

**Acceptance criteria**

- [ ] Each script runs in seconds on realistic file sizes and is documented
      with examples.
- [ ] A malformed partner file is caught by the pre-flight check.

---

### M9 — Backups, recovery, and rebuild from scratch

**Goal:** Losing the server is an inconvenience, not a disaster.

**Tasks**

1. Decide what must be backed up: configuration (without secrets, or with
   secrets encrypted), the file registry and run state, outputs not yet
   uploaded, and any database on the server.
2. `ops/backup.sh` run by `pipeline-backup.timer`: create consistent
   backups, upload them to object storage with rclone, keep a retention
   policy, and record a manifest with checksums.
3. `ops/restore.sh`: restore state and configuration onto a fresh server.
4. **Rebuild drill**: destroy the data server; create a new one; run
   `bootstrap.sh`, `deploy.sh`, and `restore.sh`; re-add secrets through your
   documented procedure; verify with `verify.sh`, `status.sh`, and one
   pipeline run. Time the whole process.

**Acceptance criteria**

- [ ] Backups run automatically and are verified.
- [ ] A rebuild from scratch completes in under 30 minutes, with no
      duplicated or lost partner deliveries afterwards.

---

### M10 — Incident drills and post-mortems

**Goal:** You can diagnose realistic failures from evidence, quickly, and
turn each into an improvement.

**Tasks**

Run each drill, record a **timeline** built from logs (G2 Topic 09), fix
it, and write a short **blameless post-mortem** in `docs/incidents/` with at
least one prevention action:

1. **Disk fills** with spill/temp files during extraction.
2. **The service is OOM-killed** after a data spike (find it in the kernel
   log; tune `MemoryMax` or the code).
3. **Deleted-but-open log file** holding disk space.
4. **Half-uploaded partner file** and a **corrupted re-send**.
5. **Missed schedule** after a long outage (verify persistent timers).
6. **Bad deployment** breaks the extract job → rollback.
7. **Clock drift** after time sync is disabled (effect on partition
   timestamps).
8. **Host key change** on the data server after a rebuild (handled
   correctly, not by disabling checks).

**Acceptance criteria**

- [ ] Each drill was detected by an alert (or a gap was found and fixed).
- [ ] Each has a log-based timeline and a post-mortem with an implemented
      prevention.
- [ ] Mean time to detect and recover is recorded per drill.

---

### M11 — Security review and hygiene

**Goal:** The server is secure by design, and you can prove it.

**Tasks**

1. Verify from outside: password login refused; root login refused; SSH
   from non-bastion addresses blocked; the service port not reachable
   publicly.
2. Review users, groups, sudo rules, and `authorized_keys` on every host;
   remove anything unnecessary.
3. **Rotate** the partner-pull key and the deployment key following your
   access guide; confirm old keys no longer work.
4. Check file permissions of configuration, secrets, logs, and data
   directories; ensure logs contain no secrets or personal data.
5. Review systemd hardening of each unit (e.g. with systemd's security
   analysis command) and improve the weakest.
6. Confirm automatic security updates are applied and reboots are planned.
7. Record findings and fixes in `docs/security-review.md`.

**Acceptance criteria**

- [ ] All outside-in checks pass.
- [ ] Key rotation is proven.
- [ ] No service runs as root; no world-readable secrets.
- [ ] Findings and fixes are documented.

---

### M12 — Documentation, operations checklists, and hand-over

**Goal:** Someone else can operate the pipeline without you.

**Tasks**

1. Finalise the **README**: purpose, architecture diagram, access, deploy,
   rollback, status, and links.
2. Finalise the **runbook**: daily checks, weekly checks (disk trends,
   updates, backups verified), deploy and rollback, adding a partner,
   reprocessing an hour or a delivery, rotating keys and secrets, each alert
   with its response, and rebuilding the server.
3. **Hand-over test**: give a colleague (or yourself in a fresh account)
   access through the access guide and ask them to deploy a small change,
   handle a staged alert, and reprocess an hour — timing each task.
4. Write a **retrospective**, including what would change with an
   orchestrator (Module 2.13), containers and infrastructure as code
   (Module 2.18), and managed services (Module 2.17, G3/G4).

**Acceptance criteria**

- [ ] The hand-over tasks succeed using only the documentation.
- [ ] The runbook covers every alert and routine task.
- [ ] The retrospective states concrete improvements.

---

### M13 — Optional stretch goals

- **Configuration management:** rewrite `bootstrap.sh` as an Ansible
  playbook (or similar) and compare.
- **Infrastructure as code:** create the cloud VMs, networks, and firewall
  rules with Terraform (Module 2.18).
- **Metrics:** install a node exporter and a small Prometheus + Grafana
  stack for server and pipeline metrics (Module 2.20).
- **Session-manager access:** replace public SSH on the bastion with a
  cloud session manager (G3) and compare.
- **Containerised services:** run the service with a container managed by
  systemd and compare with the plain virtual-environment deployment.
- **Two data servers:** add a standby server and a failover procedure.

---

## 9. Definition of done

- [ ] The data server is private, reachable only through the bastion with
      keys; tunnels documented.
- [ ] A fresh server is bootstrapped, deployed, and restored in under 30
      minutes; bootstrap is idempotent and verified.
- [ ] Atomic deployments and sub-2-minute rollbacks.
- [ ] Extraction, partner pulls, uploads, and the long-running service run
      under systemd as a non-root user, surviving reboots and downtime.
- [ ] Partner files processed exactly once with completeness and checksum
      checks; outputs uploaded and verified.
- [ ] Health checks and alerts meet the detection target; one-screen
      status.
- [ ] Backups automated and restores proven.
- [ ] Eight incident drills completed with timelines and post-mortems.
- [ ] Security review passed; key rotation proven.
- [ ] README, access guide, runbook, ADRs, security review, and
      retrospective complete; hand-over test passed.

---

## 10. Evaluation rubric (self or peer review)

Score each area from 0 to 3. A production-grade project scores **at least 2
in every area** and **3 in Recoverability, Security, and Operability**.

| Area | What a "3" looks like |
| --- | --- |
| Access | Jump-host access, restricted keys, pinned host keys, localhost tunnels, documented revocation |
| Reproducibility | Idempotent bootstrap with verification; rebuild from scratch timed and repeatable |
| Deployment | Atomic releases, self-verifying deploys, fast tested rollback |
| Data movement | Completeness markers, checksums, exactly-once registry, verified uploads |
| Scheduling and supervision | Persistent timers, no overlaps, restart policies, resource limits, hardening |
| Monitoring and alerting | Freshness, failures, disk, memory, OOM, and time sync covered; actionable alerts |
| Recoverability | Automated verified backups; rebuild drill under target |
| Incident handling | Eight drills with log timelines and implemented preventions |
| Security | Non-root services, least-privilege sudo, SSH hardening, firewall, key rotation, secret permissions |
| Operability | Status command, runbook, access guide, and a successful hand-over |

---

## 11. Common pitfalls to avoid

- Configuring the server by hand and "remembering" the steps.
- Services or timers running as root.
- Jobs running inside someone's tmux session instead of systemd.
- Processing partner files without a completeness signal.
- `rclone sync` or `rsync --delete` without a dry run.
- Timers without `Persistent=true` for jobs that must not be skipped.
- Deployments that overwrite the running code in place.
- Alerts without context, or no alert for "nothing happened" (stale data).
- Backups that were never restored.
- Disabling host-key checking to "fix" a changed key.
- Local time zones on the server.

---

## 12. Suggested timeline

| Day | Milestones |
| --- | --- |
| 1 | M0 framing · M1 infrastructure |
| 2 | M2 access · M3 bootstrap |
| 3 | M4 packaging and deployment |
| 4 | M5 data movement |
| 5 | M6 systemd services and timers |
| 6 | M7 monitoring and alerting · M8 inspection toolkit |
| 7 | M9 backups and rebuild drill |
| 8–9 | M10 incident drills and post-mortems |
| 10 | M11 security review · M12 documentation and hand-over |
| Optional | M13 stretch goals |

---

## 13. What to show in a portfolio or interview

Be ready to explain:

1. How the network and access are designed (bastion, keys, tunnels).
2. How a fresh server becomes production-ready in minutes, idempotently.
3. How deployments are atomic and rollbacks are fast.
4. How partner files are processed exactly once and verified.
5. Why systemd timers and services instead of cron and tmux — and where an
   orchestrator would take over.
6. How failures and stale data are detected and alerted.
7. What your rebuild drill proved, with timings.
8. Two incident drills: evidence, timeline, fix, and prevention.
9. What the security review found and fixed.

A README with the architecture diagram, a short demo (deploy → break →
alert → diagnose → rollback → rebuild), and the runbook show that you can
operate data systems on real servers — a skill that stays valuable no matter
which platform your team uses.
