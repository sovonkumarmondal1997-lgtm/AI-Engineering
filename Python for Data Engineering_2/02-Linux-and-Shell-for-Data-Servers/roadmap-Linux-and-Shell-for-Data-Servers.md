# Roadmap — Gap Module G2: Linux and Shell for Data Servers

This is the learning roadmap for the second gap module, **Linux and Shell
for Data Servers**. It tells you **what** to learn about working on remote
Linux servers as a data engineer, **in what order**, **how** to learn each
topic, and **how to prove to yourself** that you have learned it before you
move on.

**When to take it:** after Gap Module G1 (Docker Essentials) and **before
Stage 2 Module 2.9** (Data Ingestion) — or alongside Module 2.13
(Orchestration) at the latest. From then on you will SSH into servers,
reach web UIs and databases through bastions, move large files, run
long jobs, schedule services, and investigate problems on machines you
cannot click around in.

**What this module is not:** it does **not** repeat Stage 0. Navigation,
file operations, viewing and searching files, text processing (`grep`,
`sed`, `awk`, `sort`, `uniq`, `cut`), pipes and redirection, environment
variables, shell scripts, permissions, quoting, processes, signals, and
basic SSH keys for GitHub are assumed. This module adds the **server-side**
skills Stage 0 does not cover.

---

## 1. Module outcome

By the end of this module you will be able to:

- Connect securely to servers behind bastions with SSH config files, keys,
  agents, and jump hosts.
- Reach databases and web UIs (Airflow, Spark, Grafana, MinIO) on private
  servers through **SSH tunnels**.
- Run long data jobs that survive disconnections with **tmux**, and know
  when a job belongs in a proper service instead.
- Move large datasets reliably between machines and cloud storage with
  **rsync** and **rclone**, and verify integrity.
- Run pipelines and services with **systemd** units and timers, and read
  their logs with **journalctl**.
- Diagnose slow or failing servers: CPU, memory pressure, the OOM killer,
  disk I/O, and network connections.
- Manage disk space, inodes, data disks, and very large files.
- Inspect and transform data on the command line with **jq**, **csvkit**,
  **Miller**, and the **DuckDB CLI**.
- Investigate problems across application, service, and system logs,
  including rotated logs.
- Keep servers safe and tidy: service accounts, least-privilege `sudo`,
  packages and updates, SSH hardening, time sync, and UTC.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Command line, text processing, pipes, scripts, quoting, permissions | Stage 0 — Command Line | Used in every topic; **not** re-taught |
| Processes, signals, filesystems, virtual memory, OS tools overview, local networking | Stage 0 — OS Fundamentals | Server diagnosis builds on these; **not** re-taught |
| Git, GitHub, and SSH key basics; secrets hygiene | Stage 0 — Developer Environment | Extended here to servers, agents, and jump hosts |
| CLI programs, exit codes, logging | Stage 1 — Modules 1.5 and 1.10 | Services and log investigation |
| Running containers and services | Gap Module G1 | Practice servers run in containers or VMs |
| JSON Lines, CSV, Parquet basics | Stage 1 — Module 1.5; Stage 2 — Modules 2.3–2.5 | Command-line data tools |

**Practice environment (choose one):**

- **Containers (free, fastest):** run two or three SSH-enabled Linux
  containers on a private Docker network — one as a **bastion** with a
  published SSH port, others reachable only through it (uses Gap Module G1
  skills).
- **Local VMs:** lightweight Ubuntu VMs (e.g. Multipass, Vagrant, or an
  additional WSL distribution).
- **Small cloud VMs:** one public bastion and one private server in a cloud
  account with a budget alert (Module 2.17) — destroy them after each
  session.

Some topics (systemd, disks, OOM killer) behave most realistically on a
full VM; on WSL2, enable systemd in the distribution's configuration if you
use it for practice.

---

## 3. How the module is organised

The ten topics are grouped into four phases. Work through them **in
order**.

```text
Phase A — Reaching Servers                           (Basics → Intermediate)
  01 Remote servers: SSH config, keys, and jump hosts
  02 SSH tunnels and port forwarding for data tools
  03 tmux and long-running sessions

Phase B — Moving Data and Running Services           (Intermediate)
  04 File transfer at scale: scp, rsync, and rclone
  05 systemd services, timers, and journalctl

Phase C — Diagnosing Servers                         (Intermediate → Advanced)
  06 Server resource monitoring: CPU, memory, disk, and I/O
  07 Disk space, inodes, and large-file management
  08 Command-line data tools: jq, csvkit, Miller, and DuckDB CLI
  09 Log investigation on servers

Phase D — Keeping Servers Safe                        (Advanced)
  10 Users, sudo, packages, and server hygiene

Consolidate
  practice-questions.md
  Module mini-project: operating a pipeline on a remote server
    (→ Projects/02-remote-server-pipeline-operations.md)
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07 ──► 08 ──► 09 ──► 10
get    reach  keep   move   run    see    manage inspect find    keep it
in     its    work   data   jobs   what's disks  data    what    safe
       tools  alive         as     wrong         on the  happened
                            services             server
```

Why this order:

- You must connect (01) before you can tunnel (02) or keep sessions alive
  (03).
- Moving data (04) and running services (05) are the everyday work on a
  data server.
- Diagnosis (06–09) needs something running to diagnose.
- Hygiene (10) comes last because it touches accounts, services, packages,
  and SSH from all earlier topics.

---

## 4. Suggested schedule

About **1.5–2 weeks at 8–10 hours per week**.

| Days | Work |
| --- | --- |
| 1 | Set up the practice environment · Topic 01 — SSH config and jump hosts |
| 2 | Topic 02 — tunnels · Topic 03 — tmux |
| 3 | Topic 04 — rsync and rclone |
| 4–5 | Topic 05 — systemd services, timers, journalctl |
| 6 | Topic 06 — resource monitoring |
| 7 | Topic 07 — disks and large files |
| 8 | Topic 08 — command-line data tools |
| 9 | Topic 09 — log investigation · Topic 10 — server hygiene |
| 10–11 | Practice questions · mini-project |

---

## 5. How to study every topic (the server-operator loop)

```text
Read → Do it on a real (practice) server → Make it repeatable → Break it
→ Diagnose from evidence → Fix → Write the runbook entry → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Do it on a practice server**, not only on your laptop.
3. **Make it repeatable**: put every step in a config file, unit file, or
   script — never rely on remembering commands.
4. **Break it**: drop the connection, fill the disk, kill a process, remove
   a permission, stop a service.
5. **Diagnose from evidence**: logs, status output, metrics — before
   searching the internet.
6. **Fix** it and verify.
7. **Write a runbook entry** in `module-g2-notes.md`: symptom, commands you
   ran, cause, fix.
8. **Explain aloud** what happened on the server, step by step.

Keep a `server_lab/` folder containing your SSH config snippets, unit files,
scripts, and runbook notes — this becomes your personal server toolkit.

---

## 6. Phase A — Reaching Servers (Basics → Intermediate)

### Topic 01 — [Remote servers: SSH config, keys, and jump hosts](01-remote-servers-ssh-config-keys-and-jump-hosts.md)

**Why it comes first:** Data servers usually sit in private networks behind
a bastion. Typing long SSH commands with IPs and key paths is error-prone;
a well-kept SSH configuration makes access fast, repeatable, and safe.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | SSH client and server roles; `ssh user@host`, ports, and the first-connection **host key** prompt |
| Basics | Key types (prefer Ed25519), passphrases, public vs private keys, and `authorized_keys` on the server (`ssh-copy-id`) |
| Basics | The **SSH config file** (`~/.ssh/config`): `Host` aliases, `HostName`, `User`, `Port`, `IdentityFile`, `IdentitiesOnly` |
| Intermediate | **ssh-agent**: loading keys once per session; why **agent forwarding** is risky on shared bastions and what to use instead |
| Intermediate | **Jump hosts / bastions** with `ProxyJump` (`-J`) to reach private servers in one command |
| Intermediate | **Host key verification**: `known_hosts`, what a changed host key warning means, and never disabling checks blindly |
| Intermediate | Keeping connections alive (`ServerAliveInterval`) and speeding up repeated connections with connection multiplexing (`ControlMaster`, `ControlPath`, `ControlPersist`) |
| Advanced | Separate keys per purpose and environment; key rotation and removal of old keys from servers |
| Advanced | Short-lived SSH certificates and cloud-provider access services that avoid open SSH ports altogether (e.g. session managers or identity-aware proxies) — awareness |
| Advanced | Running a single remote command non-interactively in scripts (`ssh host 'command'`) with correct quoting |

**How to learn it**

1. Read the topic file.
2. Set up a bastion and a private server (containers or VMs) where the
   private server is reachable only from the bastion.
3. Write an SSH config so that `ssh data-private` reaches the private server
   through the bastion with no extra flags.

**Hands-on exercise — `server_lab/01/`**

1. Generate an Ed25519 key with a passphrase; load it in `ssh-agent`.
2. Install your public key on the bastion and private server; disable
   password logins on your practice servers.
3. Write `~/.ssh/config` entries for `data-bastion` and `data-private` using
   `ProxyJump`, keep-alives, and connection multiplexing.
4. Rebuild the private server so its host key changes; observe the warning,
   verify the new fingerprint, and update `known_hosts` safely.
5. Run a remote command from a script (e.g. check free disk space on
   `data-private`) and use its exit code.

**Checkpoint — you are ready to move on when you can:**

- [ ] Reach a private server through a bastion with one short command.
- [ ] Explain host key verification and respond correctly to a changed key.
- [ ] Explain the risks of agent forwarding and the safer alternative.
- [ ] Manage keys per purpose and remove old ones.

**Common mistakes:** unprotected private keys; `StrictHostKeyChecking no`
everywhere; agent forwarding to untrusted hosts; one key for everything
forever.

---

### Topic 02 — [SSH tunnels and port forwarding for data tools](02-ssh-tunnels-and-port-forwarding-for-data-tools.md)

**Why here:** Airflow, Spark, Grafana, MinIO consoles, and databases on
private servers are (correctly) not exposed to the internet. Tunnels let
you use them from your laptop as if they were local — safely.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Local forwarding** (`-L local_port:target_host:target_port`): reach a private database or web UI through SSH |
| Basics | Using the forwarded port from `psql`, a browser, or Python code (`localhost:local_port`) |
| Basics | Running tunnels without a shell (`-N`) and in the background (`-f`), and closing them |
| Intermediate | Forwarding through a bastion to a service on a private host (combining `ProxyJump` and `-L`) |
| Intermediate | Defining tunnels in the SSH config file (`LocalForward`) so they are repeatable |
| Intermediate | **Binding safety**: forwarding only on `127.0.0.1` so colleagues on your network cannot use your tunnel |
| Intermediate | **Remote forwarding** (`-R`) — exposing a local service to a server (and why it needs care) |
| Advanced | **Dynamic forwarding** (`-D`, a SOCKS proxy) for browsing several internal web UIs |
| Advanced | Keeping tunnels up with auto-reconnecting tools, and when that is appropriate |
| Advanced | Alternatives you will meet: `kubectl port-forward` (Module 2.18) and cloud port-forwarding sessions — awareness |
| Advanced | When a tunnel is **not** the right answer: production applications should use private networking, not personal tunnels |

**How to learn it**

1. Read the topic file.
2. On the private server, run PostgreSQL and a small web UI (e.g. MinIO
   console or Grafana) in containers bound to `127.0.0.1` on that server.
3. Draw each tunnel: your port, the bastion, the target host, the target
   port.

**Hands-on exercise — `server_lab/02/`**

1. Open a tunnel to PostgreSQL on `data-private` and query it with `psql`
   and with a Python script from your laptop.
2. Add `LocalForward` entries for the database and the web UI to your SSH
   config and start both with one command.
3. Show that a tunnel bound to all interfaces is reachable from another
   machine on your network; rebind it to `127.0.0.1`.
4. Open a SOCKS proxy and browse two internal web UIs.
5. Write a small `tunnels.sh` to open, check, and close your standard
   tunnels.

**Checkpoint:**

- [ ] Reach private databases and UIs through local forwarding via a
      bastion.
- [ ] Define tunnels in the SSH config.
- [ ] Explain local, remote, and dynamic forwarding and their risks.

**Common mistakes:** exposing databases publicly instead of tunnelling;
tunnels bound to all interfaces; forgotten background tunnels; building
production integrations on personal tunnels.

---

### Topic 03 — [tmux and long-running sessions](03-tmux-and-long-running-sessions.md)

**Why here:** Backfills, large copies, and data investigations can take
hours. A dropped Wi-Fi connection must not kill them.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why jobs die when SSH disconnects (the hang-up signal), and ways to prevent it |
| Basics | **tmux** sessions: create, name, detach, list, and reattach |
| Basics | Windows and panes for running a job, watching logs, and monitoring resources side by side |
| Intermediate | Scrollback and copy mode; saving pane output to a file |
| Intermediate | A minimal tmux configuration (prefix, mouse, history size, status line) |
| Intermediate | Sharing a session for pair debugging (and the security implications) |
| Intermediate | Alternatives: `nohup`, `setsid`, and GNU `screen` — when you might meet them |
| Advanced | **When tmux is the wrong tool**: recurring or production jobs belong in systemd services/timers (Topic 05) or an orchestrator (Module 2.13) — tmux is for interactive, one-off work |
| Advanced | Recording what you ran (session logging, shell history with timestamps) for incident notes |

**How to learn it**

1. Read the topic file.
2. Start a long-running job over SSH without tmux, disconnect, and observe
   it die; repeat with tmux.
3. Build a standard three-pane layout for "run, watch logs, watch
   resources".

**Hands-on exercise — `server_lab/03/`**

1. In a named tmux session on `data-private`, start a 30-minute data job
   (e.g. a large DuckDB conversion or a synthetic backfill), detach, close
   the laptop's connection, reconnect, and reattach.
2. Create a layout with the job, `tail -f` of its log, and a resource
   monitor.
3. Capture the job's pane output to a file for your notes.
4. Write a short note on which of today's tasks should become a systemd
   timer instead.

**Checkpoint:**

- [ ] Keep long interactive jobs alive across disconnections.
- [ ] Work efficiently with sessions, windows, and panes.
- [ ] Explain when to use tmux, `nohup`, systemd, or an orchestrator.

**Common mistakes:** long jobs run directly in an SSH shell; "production"
jobs living forever in someone's tmux session; forgotten sessions holding
resources.

---

## 7. Phase B — Moving Data and Running Services (Intermediate)

### Topic 04 — [File transfer at scale: scp, rsync, and rclone](04-file-transfer-at-scale-scp-rsync-and-rclone.md)

**Why here:** Data engineers move large files constantly — partner drops,
exports, backups, lake prefixes. Transfers must be resumable, verifiable,
and must never delete the wrong thing.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `scp` and `sftp` for simple, one-off transfers (including through jump hosts) |
| Basics | **rsync** essentials: archive mode (`-a`), verbose and progress output, compression over the network (`-z`), and running over SSH |
| Basics | The **trailing-slash rule** in rsync (copy a directory vs its contents) |
| Intermediate | **Dry runs** (`--dry-run`) before every real sync; `--partial` / resumable transfers; `--exclude` patterns |
| Intermediate | **`--delete` and mirror semantics**: powerful and dangerous — always dry-run first |
| Intermediate | Integrity: checksums (`sha256sum`, rsync checksum mode) and manifests of transferred files (Module 2.9) |
| Intermediate | **rclone** for object storage (S3, GCS, Azure, MinIO): remotes, `copy` vs `sync`, `--dry-run`, `check`, parallel transfers, bandwidth limits |
| Advanced | Streaming archives over SSH (`tar` piped through `ssh`) and on-the-fly compression (`zstd`) |
| Advanced | Transferring very large files: splitting, parallel streams, and resuming |
| Advanced | Throttling transfers so they do not starve production traffic |
| Advanced | Moving data between regions or clouds: egress costs (Module 2.17) and when a managed transfer service is better — awareness |

**How to learn it**

1. Read the topic file.
2. Predict the result of `rsync src dst/` vs `rsync src/ dst/` and verify.
3. Configure an rclone remote for your MinIO (Gap Module G1) or a cloud
   bucket.

**Hands-on exercise — `server_lab/04/`**

1. Generate 20 GB of files (many small and a few large) on `data-private`.
2. Copy them to your laptop with rsync over the bastion; interrupt midway
   and resume; verify with a SHA-256 manifest.
3. Mirror a directory with `--delete` after a dry run; show what would have
   been deleted with the wrong trailing slash.
4. Upload a partitioned dataset to object storage with rclone using
   parallel transfers; verify with `rclone check`.
5. Stream a compressed archive of a directory over SSH without creating a
   temporary file; compare time and bytes transferred with rsync.
6. Throttle a transfer to a fixed bandwidth and measure it.

**Checkpoint:**

- [ ] Transfer and resume large datasets with rsync over jump hosts.
- [ ] Use dry runs and understand `--delete` and trailing slashes.
- [ ] Verify transfers with checksums.
- [ ] Copy and sync to object storage with rclone.

**Common mistakes:** `rsync --delete` without a dry run; the wrong trailing
slash; unverified transfers; saturating a shared network link.

---

### Topic 05 — [systemd services, timers, and journalctl](05-systemd-services-timers-and-journalctl.md)

**Why here:** On a single server, systemd is how you run long-lived
services (an API, a consumer, an agent) and scheduled jobs reliably —
with restarts, logs, resource limits, and missed-run handling that cron
lacks (Module 2.13).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Units and unit files; `systemctl start`, `stop`, `restart`, `status`, `enable`, `disable`, and `daemon-reload` |
| Basics | A **service unit** for a Python job: `ExecStart`, `WorkingDirectory`, `User`, `EnvironmentFile` |
| Basics | **journalctl** for a unit: `-u`, `-f`, `--since`, `--until`, priority filters, and output formats |
| Intermediate | Restart behaviour: `Restart=on-failure`, `RestartSec`, and start-limit protections against crash loops |
| Intermediate | Stopping gracefully: `SIGTERM` handling in your code (Module 2.10), stop timeouts, and kill signals |
| Intermediate | **Timers**: `OnCalendar` schedules, `Persistent=true` to run missed jobs after downtime, randomised delays, and testing schedules with `systemd-analyze calendar` |
| Intermediate | **Oneshot** services for batch jobs triggered by timers; preventing overlapping runs |
| Intermediate | Dependencies and ordering (`After=`, `Wants=`, `Requires=`), e.g. start after the network is online |
| Advanced | **Resource limits** per service (memory and CPU caps) and what happens when they are hit |
| Advanced | Basic **hardening** options (no new privileges, read-only system paths, private temp directories) — awareness |
| Advanced | User services (`systemctl --user`) and keeping them running after logout |
| Advanced | systemd timers vs cron vs an orchestrator: when each is appropriate (building on Module 2.13's "limits of cron") |
| Advanced | On WSL2: enabling systemd for practice |

**How to learn it**

1. Read the topic file.
2. Turn a Python CLI from earlier modules (e.g. your API extractor from
   Module 2.9) into a oneshot service with a timer.
3. Stop the server during a scheduled time and confirm the missed run
   happens after restart.

**Hands-on exercise — `server_lab/05/`**

1. Write `extract-orders.service` (oneshot, running as a dedicated user,
   environment from a protected file) and `extract-orders.timer` (hourly,
   persistent, with a small randomised delay).
2. Write `orders-consumer.service` (long-running Kafka consumer or small
   API) with `Restart=on-failure`, graceful stop, and memory limits.
3. Break the consumer's configuration and watch systemd's restart and
   start-limit behaviour; read the errors with `journalctl`.
4. Exceed the memory limit and find the kill in the journal.
5. Compare the timer with a cron entry: list what systemd gives you that cron
   did not.

**Checkpoint:**

- [ ] Write and manage service and timer units.
- [ ] Configure restarts, graceful stops, and resource limits.
- [ ] Use `Persistent=true` and test calendar expressions.
- [ ] Read service logs efficiently with journalctl.
- [ ] Choose between systemd, cron, and an orchestrator.

**Common mistakes:** services running as root; secrets in unit files;
forgetting `daemon-reload`; no restart limits (endless crash loops); timers
without `Persistent=true` for jobs that must not be skipped.

---

## 8. Phase C — Diagnosing Servers (Intermediate → Advanced)

### Topic 06 — [Server resource monitoring: CPU, memory, disk, and I/O](06-server-resource-monitoring-cpu-memory-disk-and-io.md)

**Why here:** "The job is slow" or "the server is stuck" is the start of
many incidents. You need to tell quickly whether the problem is CPU,
memory, disk, network — or the job itself.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Load average and what it means relative to the number of CPU cores (`uptime`, `nproc`) |
| Basics | Memory: used vs available vs buffers/cache (`free -h`) — why "free memory is low" is often fine |
| Basics | Interpreting interactive monitors (from Stage 0's tools overview) for **data workloads**: which process, which state, which resource |
| Intermediate | `vmstat` for run queue, swapping, and I/O wait; `iostat` for disk utilisation and latency; `pidstat` for per-process usage over time |
| Intermediate | **I/O wait** and slow disks: recognising a disk-bound job |
| Intermediate | **Memory pressure** and **swap**: why a server "hangs" before it crashes |
| Intermediate | **The OOM killer**: how Linux chooses a process to kill, and finding the evidence in the kernel log (`dmesg`, `journalctl -k`) |
| Intermediate | Network connections and ports in use (`ss`), and connections piling up (e.g. database connection leaks from Module 2.7) |
| Advanced | Pressure stall information (`/proc/pressure/*`) as a direct measure of CPU, memory, and I/O pressure |
| Advanced | Historical data with `sar` (from the `sysstat` package) for "what happened at 3 a.m.?" |
| Advanced | Control groups (cgroups) as the mechanism behind container and systemd limits |
| Advanced | Connecting to metrics systems: node exporters and dashboards (Module 2.20) — awareness |
| Advanced | A **diagnosis method**: symptom → which resource is saturated → which process → why → fix (tune, limit, move, or scale) |

**How to learn it**

1. Read the topic file.
2. Create four artificial problems on a practice server — CPU saturation,
   memory exhaustion, heavy disk I/O, many open connections — and record
   how each looks in each tool.
3. Build a one-page "which tool for which question" cheat sheet.

**Hands-on exercise — `server_lab/06/`**

1. Run a CPU-heavy data job and a disk-heavy one (e.g. large sort with
   spill) at the same time; identify which is bottlenecked by what.
2. Exhaust memory with a pandas job until the OOM killer acts; find the
   kernel log entry and name the killed process.
3. Leak database connections from a Python script and find them with `ss`
   and PostgreSQL's activity view.
4. Enable `sysstat` history, create a slowdown, and investigate it
   afterwards with `sar`.
5. Write a runbook entry: "server is slow — first five commands".

**Checkpoint:**

- [ ] Interpret load average, memory, swap, and I/O wait.
- [ ] Identify CPU-, memory-, and I/O-bound problems.
- [ ] Find OOM-killer events.
- [ ] Investigate past incidents with historical data.

**Common mistakes:** panicking about low "free" memory; ignoring swap
activity; restarting servers before collecting evidence; guessing instead
of measuring.

---

### Topic 07 — [Disk space, inodes, and large-file management](07-disk-space-inodes-and-large-file-management.md)

**Why here:** Full disks are among the most common causes of failed data
jobs — from logs, temporary files, spills, caches, or millions of tiny
files. Data servers also often need extra data disks.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Finding what uses space quickly (`du` with sorting and depth limits, and interactive analysers such as `ncdu`) — beyond Stage 0's basics |
| Basics | Common space hogs on data servers: logs, temporary directories, Spark and pandas spill files, package and pip caches, Docker data (Gap Module G1), old exports |
| Intermediate | **Inodes**: a disk can be "full" with free space when it runs out of inodes (`df -i`) — usually from millions of tiny files |
| Intermediate | **Deleted-but-open files**: space not released until the process holding the file closes it (finding them with `lsof`) |
| Intermediate | Adding a **data disk**: listing block devices (`lsblk`), creating a filesystem, mounting it, and making the mount permanent safely (by UUID, with a failure-tolerant option) |
| Intermediate | Directing temporary and spill files to the right disk (e.g. `TMPDIR`, Spark local directories, DuckDB temp directory) |
| Intermediate | **Large files on the command line**: `head`/`tail` on huge files, counting lines fast, `split`, reading compressed files without decompressing to disk (`zcat`, `zstdcat`) |
| Advanced | Sorting files larger than memory with `sort` using buffer-size and temporary-directory options |
| Advanced | Parallel compression tools (e.g. multi-threaded `zstd`, `pigz`) and choosing compression levels (Module 2.5) |
| Advanced | Filesystem choices and mount options that matter for data workloads — awareness |
| Advanced | Early warning: disk-usage alerts at thresholds and growth-rate projections (Module 2.20) |

**How to learn it**

1. Read the topic file.
2. Fill a practice disk three different ways — one big file, millions of
   tiny files, and a deleted-but-open log — and diagnose each.
3. Attach an extra disk to a VM (or a loopback file on a container host) and
   mount it permanently.

**Hands-on exercise — `server_lab/07/`**

1. Find the top ten directories and files using space on your practice
   server and clean safe candidates.
2. Exhaust inodes with tiny files and diagnose it; clean up and propose a
   design fix (e.g. batching small files — Module 2.5).
3. Keep a process writing to a deleted log file, show the missing space,
   and release it.
4. Mount a new data disk at `/data`, make it permanent, and point DuckDB's
   and Python's temporary directories at it.
5. Count lines, sample rows, and sort a 20 GB compressed CSV without ever
   decompressing it to disk.

**Checkpoint:**

- [ ] Find and fix space problems, including inodes and open deleted files.
- [ ] Add and mount a data disk safely.
- [ ] Control where temporary and spill files go.
- [ ] Handle files larger than memory on the command line.

**Common mistakes:** deleting files a running process still writes to;
unbounded temp directories on the root disk; `fstab` entries that stop a
server from booting; decompressing huge files just to look at them.

---

### Topic 08 — [Command-line data tools: jq, csvkit, Miller, and DuckDB CLI](08-command-line-data-tools-jq-csvkit-miller-and-duckdb-cli.md)

**Why here:** On a server — during an incident, while checking a partner
file, or before writing any Python — the fastest way to inspect data is
often a one-line command. These tools go beyond Stage 0's text processing
by understanding JSON, CSV, and Parquet properly.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **jq**: pretty-printing, selecting fields, filtering with `select`, mapping arrays, raw output (`-r`), compact output (`-c`) |
| Basics | Working with **JSON Lines** (one object per line) and API responses (Module 2.9) |
| Basics | **csvkit**: viewing (`csvlook`), column selection (`csvcut`), filtering (`csvgrep`), statistics (`csvstat`), and converting from Excel and JSON |
| Intermediate | **Miller (`mlr`)**: CSV/TSV/JSON processing with named fields — filter, sort, aggregate (`stats1`), join, and format conversion |
| Intermediate | **DuckDB CLI**: querying CSV, JSON, and Parquet files directly with SQL, sampling, schema inspection, and converting files (e.g. CSV → Parquet) |
| Intermediate | jq for transformations: building new objects, grouping, converting JSON to CSV, handling missing fields and nulls |
| Intermediate | Choosing the right tool: quick look (jq/csvlook), row-wise edits (Miller), analytical questions (DuckDB), anything reusable (Python) |
| Advanced | Very large JSON: streaming parsing with jq's streaming mode, or DuckDB's JSON reader |
| Advanced | Parallel command-line processing across many files (e.g. GNU `parallel`) |
| Advanced | Faster CSV tool alternatives written in Rust — awareness |
| Advanced | Reproducibility: saving useful one-liners as scripts with comments, and knowing when to move to Python (Stage 2 modules) |

**How to learn it**

1. Read the topic file.
2. Take the same dataset in CSV, JSON Lines, and Parquet and answer the same
   five questions with each tool that supports the format.
3. Build a personal cheat sheet of your 20 most useful one-liners.

**Hands-on exercise — `server_lab/08/`**

1. From a paginated API response saved as JSON (Module 2.9), extract fields,
   flatten nested items, and output CSV with jq.
2. Profile a messy partner CSV with `csvstat`; find rows with invalid values
   using `csvgrep` or Miller.
3. Aggregate revenue by day and country with Miller, then with DuckDB SQL;
   compare results.
4. Convert a 5 GB CSV to partitioned Parquet with the DuckDB CLI and query
   it.
5. Process 500 JSON Lines files in parallel to count events per type.

**Checkpoint:**

- [ ] Query and reshape JSON with jq.
- [ ] Inspect and clean CSV with csvkit and Miller.
- [ ] Answer analytical questions over files with the DuckDB CLI.
- [ ] Choose the right tool and know when to switch to Python.

**Common mistakes:** parsing CSV or JSON with `cut`/`sed` (breaks on quotes
and nesting); unreadable 200-character one-liners with no record; loading
huge files into memory when streaming is available.

---

### Topic 09 — [Log investigation on servers](09-log-investigation-on-servers.md)

**Why here:** When something goes wrong on a server, the answer is usually
in a log — application logs, service logs, or the kernel log. The skill is
finding the right lines quickly across rotated, compressed, and multiple
log sources.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Where logs live: application log files, the systemd journal (Topic 05), and system logs under `/var/log` |
| Basics | Following logs live (`tail -f`, `less +F`, `journalctl -f`) and paging through them |
| Intermediate | **Log rotation** with `logrotate`: rotate count, size and time triggers, compression, and the difference between creating a new file and copying-then-truncating |
| Intermediate | Searching **rotated and compressed** logs together (`zgrep`, `zcat`) |
| Intermediate | Extracting a **time window** from logs and working with time zones (servers in UTC — Topic 10) |
| Intermediate | **Structured JSON logs** (Module 2.20) investigated with jq: filter by `run_id`, level, or component |
| Intermediate | Counting and grouping: errors per minute, top error messages, first occurrence — building a timeline |
| Advanced | **Correlating** across sources: application, service, kernel (e.g. OOM kills), and database logs by timestamp and run id |
| Advanced | Journal disk usage and retention settings |
| Advanced | Logs as evidence: preserving them before restarts or cleanup during incidents (Module 2.20) |
| Advanced | Shipping logs to central systems instead of reading them on servers — awareness (Module 2.20) |

**How to learn it**

1. Read the topic file.
2. Configure logrotate for a practice application and verify rotation and
   compression.
3. Reconstruct a timeline of a staged incident using only logs.

**Hands-on exercise — `server_lab/09/`**

1. Configure logrotate for your Topic 05 job's log file (daily, 14 copies,
   compressed) and verify it with a forced rotation.
2. Stage an incident: the consumer service is OOM-killed after a database
   slowdown. Using journal, application JSON logs, kernel logs, and database
   logs, build a minute-by-minute timeline.
3. Produce "errors per minute" and "top 5 error messages" for the last 24
   hours from rotated, compressed logs.
4. Extract all lines for one `run_id` across two services with jq.
5. Write a runbook entry: "how to investigate a failed run on a server".

**Checkpoint:**

- [ ] Find and follow logs from applications, systemd, and the kernel.
- [ ] Configure and reason about log rotation.
- [ ] Search rotated and compressed logs and extract time windows.
- [ ] Correlate events across log sources into a timeline.

**Common mistakes:** logs growing without rotation; copy-truncate
surprises for applications that keep file handles; searching only the
current file; mixing time zones in a timeline.

---

## 9. Phase D — Keeping Servers Safe (Advanced)

### Topic 10 — [Users, sudo, packages, and server hygiene](10-users-sudo-packages-and-server-hygiene.md)

**Why last:** Every earlier topic created accounts, services, keys, and
files on servers. This topic makes sure those servers stay secure,
consistent, and maintainable.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Users and groups; **service accounts** (system users with no login shell) for running jobs and services (Topic 05) |
| Basics | `sudo` and least privilege: editing sudoers safely (`visudo`), granting only the commands needed |
| Basics | Package management on Debian/Ubuntu (`apt update`, `upgrade`, install, remove, show versions) |
| Intermediate | **Security updates**: applying them regularly and automatically (unattended upgrades) while controlling restarts |
| Intermediate | Pinning or holding versions of critical packages (e.g. a database client) |
| Intermediate | **SSH hardening**: disable password logins and direct root login, limit which users may connect |
| Intermediate | Firewall basics (e.g. `ufw`): allow only needed ports, and prefer private networking plus bastions |
| Intermediate | **Time**: time synchronisation services, and running servers in **UTC** to avoid time-zone bugs in data |
| Intermediate | File permissions for secrets and environment files (owner-only access), and never world-readable credentials (Stage 0 secrets hygiene applied to servers) |
| Advanced | Auditing access: login history, `sudo` logs, and review of `authorized_keys` |
| Advanced | Brute-force protection tools — awareness |
| Advanced | A **server bootstrap checklist** (users, SSH, firewall, updates, time, disks, monitoring, logrotate) — and turning it into a script |
| Advanced | The **immutable-infrastructure mindset**: rebuild servers from images and code (Module 2.18) rather than hand-editing them; "pets vs cattle" |

**How to learn it**

1. Read the topic file.
2. Harden your practice private server and verify each change from outside
   (e.g. password login refused).
3. Turn your manual steps into a bootstrap script and run it on a fresh
   server.

**Hands-on exercise — `server_lab/10/`**

1. Create a `pipeline` service account; run your Topic 05 services as that
   user; grant a limited sudo rule (e.g. restart only those services) to an
   `operator` group.
2. Disable password and root SSH logins; restrict SSH to named users;
   configure a firewall allowing SSH only from the bastion.
3. Enable automatic security updates; hold one package at a fixed version.
4. Set the server time zone to UTC and verify time synchronisation.
5. Secure the environment file with credentials (owner-only) and verify
   another user cannot read it.
6. Write `bootstrap.sh` that applies your checklist idempotently to a fresh
   server; run it twice and confirm the second run changes nothing.

**Checkpoint:**

- [ ] Run services under dedicated accounts with least-privilege sudo.
- [ ] Keep packages updated and critical versions pinned.
- [ ] Harden SSH and restrict network access.
- [ ] Run servers in UTC with synchronised time.
- [ ] Bootstrap a server repeatably and explain the immutable-infrastructure
      mindset.

**Common mistakes:** everything running as root; shared personal accounts;
servers never patched; local time zones on data servers; hand-tuned servers
nobody can rebuild.

---

## 10. Consolidate — practice questions

When all ten topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Restate the symptom or task in one sentence.
2. List the commands you would run first and what each could reveal.
3. Reproduce the situation on a practice server.
4. Diagnose from evidence, fix, and verify.
5. Write the runbook entry you would want at 3 a.m.

---

## 11. Module mini-project — operating a pipeline on a remote server

This mini-project is expanded in
[`../00-Gap-Modules-Overview/Projects/02-remote-server-pipeline-operations.md`](../00-Gap-Modules-Overview/Projects/02-remote-server-pipeline-operations.md).
The short version:

**Goal:** Deploy and operate a small data pipeline on a private Linux
server reachable only through a bastion — using only the skills of this
module and Gap Module G1.

1. **Access:** SSH config with jump host, keys per purpose, tunnels to the
   pipeline's database and a web UI.
2. **Server:** bootstrapped by an idempotent script (service account, SSH
   hardening, firewall, updates, UTC, time sync, logrotate, data disk at
   `/data`).
3. **Pipeline:** an hourly extraction job as a systemd oneshot service with
   a persistent timer, and a long-running consumer or API as a restartable
   service with resource limits.
4. **Data movement:** partner files pulled with rsync (verified with
   checksums) and outputs synced to object storage with rclone.
5. **Diagnosis:** a staged incident (disk fills with spill files, then the
   consumer is OOM-killed) investigated with monitoring tools and logs,
   resulting in a timeline and fixes.
6. **Runbook:** access, deploy, start/stop, check status, read logs, free
   disk space, rotate credentials, and rebuild the server from scratch.

**Grading yourself:** a fresh server reaches a working state from your
scripts in under 30 minutes; the pipeline survives reboots, disconnections,
and missed schedules; the staged incident is diagnosed from evidence within
15 minutes using your runbook; and no service runs as root.

---

## 12. Module self-assessment — exit criteria

Only continue with Module 2.9 when you can tick every box without looking at
your notes:

- [ ] I can reach private servers through bastions with a clean SSH
      configuration.
- [ ] I can use tunnels to reach databases and web UIs safely.
- [ ] I can keep long interactive jobs alive and know when they belong in a
      service instead.
- [ ] I can move and verify large datasets with rsync and rclone.
- [ ] I can run jobs and services with systemd units and timers and read
      their logs.
- [ ] I can diagnose CPU, memory, I/O, and connection problems, including
      OOM kills.
- [ ] I can manage disk space, inodes, data disks, and large files.
- [ ] I can inspect data on the command line with jq, csvkit, Miller, and
      DuckDB.
- [ ] I can investigate incidents across rotated and structured logs.
- [ ] I can keep a server secure and rebuild it from a script.
- [ ] I have finished the practice questions and the mini-project.

---

## 13. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| OpenSSH manual pages (`ssh`, `ssh_config`, `sshd_config`, `ssh-keygen`) | 01, 02, 10 |
| tmux documentation and manual page | 03 |
| rsync and rclone documentation | 04 |
| systemd documentation (`systemd.service`, `systemd.timer`, `systemd.exec`, `journalctl`) | 05, 09 |
| *Systems Performance*, 2nd edition — Brendan Gregg (Addison-Wesley), and his Linux performance tool diagrams | 06, 07 |
| `sysstat` (`sar`, `iostat`, `pidstat`) documentation | 06 |
| jq manual, csvkit documentation, Miller documentation, DuckDB CLI documentation | 08 |
| `logrotate` manual page | 09 |
| Ubuntu Server documentation — users, security, automatic updates, firewall, time synchronisation | 10 |
| *The Linux Command Line* — William Shotts (free online) — for any gaps from Stage 0 | All topics |

---

## 14. Where this module leads

| This module's skill | Where you use it next |
| --- | --- |
| SFTP, rsync, checksums, file registries | Module 2.9 — file-drop ingestion |
| systemd timers vs cron vs orchestrators | Module 2.13 — Orchestration |
| Resource diagnosis, OOM kills, spill directories | Modules 2.14 (Spark) and 2.21 (performance) |
| Server logs and timelines | Module 2.20 — observability and incident response |
| Tunnels to private services | Modules 2.13–2.17 (Airflow, Spark UI, cloud databases) |
| Bootstrap scripts and the immutable-infrastructure mindset | Module 2.18 — containers, Terraform, CI/CD |
| Command-line data inspection | Every module, and incident response on any server |
| Cloud-native access and managed services | Gap Modules G3/G4 — AWS or Databricks deep dive |

Most data platforms still run on Linux somewhere underneath — in a VM, a
container, or a managed node. The habits you build here — reach servers
through bastions, keep secrets and services off root, dry-run every
destructive command, measure before you restart, read the logs to build a
timeline, and make every server rebuildable from code — are what make you
calm and effective when production misbehaves.
