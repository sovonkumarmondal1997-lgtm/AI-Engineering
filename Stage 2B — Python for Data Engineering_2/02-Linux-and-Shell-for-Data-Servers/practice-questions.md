# Practice Questions — Linux and Shell for Data Servers

## How to Use This Practice Set

This is the complete practical assessment for **G2 — Linux and Shell for Data Servers**: exactly 40 questions, distributed across Basic, Moderate, Hard, and Advanced difficulty.

Every solution follows:

```text
Problem
→ Evidence
→ Hypothesis
→ Test
→ Fix
→ Verification
→ Production Lesson
```

Use a disposable Linux practice environment. Never use real production credentials, private keys, API tokens, or customer data.

## Practice Environment

A useful practice topology contains a bastion, a private Linux data server, a systemd-managed sample service, synthetic CSV/JSONL/Parquet data, synthetic logs, and optional PostgreSQL.

## Difficulty Progression

| Level | Expected capability |
|---|---|
| Basic | One primary concept plus a few commands |
| Moderate | 2–3 concepts plus diagnostic reasoning |
| Hard | Multiple topics, troubleshooting, interpretation, verification |
| Advanced | Multi-system diagnosis, architecture, security/reliability trade-offs, incident response |


# Part 1 — Basic

## Question 1 — SSH to a Data Server

### Difficulty
Basic

### Topics Covered
- 01 SSH

### Problem

You are given a Linux data server named `data01`, reachable as user `operator` on port `22`. Your SSH private key is stored at `~/.ssh/data01_ed25519`. Establish a secure SSH connection and explain the role of the user, host, port, and key.

### What You Need to Determine

1. Which SSH command should you use?
2. What does each important argument mean?
3. How do you verify that you reached the intended server?


### Solution

### Step 1 — Understand the problem

The target is a named Linux server and authentication is key-based. Start with the least complicated direct SSH command.

### Step 2 — Connect

```bash
ssh -i ~/.ssh/data01_ed25519 operator@data01
```

`-i` selects the identity file. `operator` is the remote user and `data01` is the destination hostname. If SSH uses its default port 22, no `-p` option is necessary.

### Step 3 — Verify

```bash
whoami
hostname
id
```

`whoami` should show `operator`; `hostname` should identify the expected server; `id` confirms the effective UID and groups.

### Step 4 — Diagnose unexpected identity

If authentication unexpectedly falls back to another key, use:

```bash
ssh -v -i ~/.ssh/data01_ed25519 operator@data01
```

Use verbose output for diagnosis rather than changing security settings blindly.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

SSH parameters describe an access path: identity → user → host → transport. Verification after connection is part of safe operations.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 2 — SSH Config for a Data Server

### Difficulty
Basic

### Topics Covered
- 01 SSH

### Problem

You repeatedly connect to `data01` as `operator` using `~/.ssh/data01_ed25519`. Create an SSH config entry so that `ssh data01` is sufficient.

### What You Need to Determine

1. Which file should contain the configuration?
2. Which directives are required?
3. How do you test the alias?


### Solution

### Step 1 — Configure

Edit:

```text
~/.ssh/config
```

Add:

```sshconfig
Host data01
    HostName data01.internal
    User operator
    IdentityFile ~/.ssh/data01_ed25519
    IdentitiesOnly yes
```

`Host` defines the local alias. `HostName` is the actual destination. `User` fixes the remote account. `IdentityFile` selects the intended key. `IdentitiesOnly yes` helps prevent unrelated agent keys from being offered.

### Step 2 — Protect the config

```bash
chmod 600 ~/.ssh/config
```

### Step 3 — Test

```bash
ssh data01
```

Then:

```bash
hostname
whoami
```

### Step 4 — Diagnose

If the alias does not behave as expected:

```bash
ssh -G data01
```

This displays the effective configuration SSH will use.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

SSH config converts repeated connection knowledge into a reusable, reviewable operator interface. It also reduces typing errors.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 3 — Reach a Private Server Through a Bastion

### Difficulty
Basic

### Topics Covered
- 01 SSH

### Problem

`data-private` has no public route. You can reach `bastion`, and from there the private server is reachable. Configure and use `ProxyJump`.

### What You Need to Determine

1. What is the correct connection pattern?
2. What does `-J` mean?
3. How can you make it persistent?


### Solution

### Step 1 — Connect

```bash
ssh -J bastion operator@data-private
```

`-J` means ProxyJump. SSH first reaches `bastion`, then uses it as the jump path to `data-private`.

### Step 2 — Make it reusable

```sshconfig
Host bastion
    HostName bastion.example
    User operator
    IdentityFile ~/.ssh/bastion_ed25519

Host data-private
    HostName 10.0.2.20
    User operator
    IdentityFile ~/.ssh/data_private_ed25519
    ProxyJump bastion
```

Then:

```bash
ssh data-private
```

### Step 3 — Verify

```bash
hostname
ip route
```

Confirm the destination is the private server, not the bastion.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

A bastion is a controlled entry point. `ProxyJump` makes the intended network path explicit and repeatable.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 4 — Local SSH Tunnel to PostgreSQL

### Difficulty
Basic

### Topics Covered
- 02 Tunnels

### Problem

PostgreSQL listens on the private server at port `5432` and is not publicly reachable. You need to use a local PostgreSQL client through SSH.

### What You Need to Determine

1. What kind of forwarding is required?
2. What command creates the tunnel?
3. How does the local port map to the remote service?


### Solution

### Step 1 — Create the tunnel

```bash
ssh -N -L 15432:127.0.0.1:5432 data-private
```

`-L local_port:destination_host:destination_port` creates local forwarding. Here local `15432` maps through SSH to PostgreSQL at `127.0.0.1:5432` from the server's perspective. `-N` means no remote shell command is requested.

### Step 2 — Connect locally

```bash
psql -h 127.0.0.1 -p 15432 -U orders_reader orders
```

The PostgreSQL client connects to the local endpoint; SSH carries traffic to the private database.

### Step 3 — Verify

Confirm the tunnel process is running and then test the database connection. Bind the local endpoint only as broadly as required; localhost is the safer default.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

SSH tunneling lets an operator reach private data tools without exposing the database publicly.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 5 — Keep a Long-Running Job Alive with tmux

### Difficulty
Basic

### Topics Covered
- 03 tmux

### Problem

You start a 90-minute ingestion command over SSH. Your laptop may sleep or disconnect. Keep the process running and return to it later.

### What You Need to Determine

1. How should you start the job?
2. How do you detach?
3. How do you reattach?


### Solution

### Step 1 — Create a named session

```bash
tmux new -s ingestion
```

### Step 2 — Run the job

```bash
python ingest.py
```

The process runs inside the tmux session.

### Step 3 — Detach

Press:

```text
Ctrl-b d
```

The tmux server keeps the session alive after your SSH terminal disconnects.

### Step 4 — Reattach

```bash
tmux attach -t ingestion
```

List sessions first if needed:

```bash
tmux ls
```

### Step 5 — Know the boundary

tmux is useful for interactive, operator-driven long-running work. A recurring production service belongs in systemd or an orchestrator rather than depending on an engineer remembering to attach to tmux.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

tmux protects interactive work from terminal/session loss; it is not a replacement for production service management.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 6 — Choose rsync for a Directory Transfer

### Difficulty
Basic

### Topics Covered
- 04 Transfers

### Problem

You must move a large directory containing many files from `server-a:/data/raw/` to `server-b:/data/raw/`. You expect the transfer may be interrupted.

### What You Need to Determine

1. Which tool is preferable?
2. What basic command would you use?
3. Why is it preferable to repeatedly using scp?


### Solution

### Step 1 — Choose the tool

Use `rsync` for a large directory transfer that may need to resume.

### Step 2 — Perform a dry run

```bash
rsync -av --dry-run /data/raw/ operator@server-b:/data/raw/
```

`-a` enables archive-style recursive transfer and preservation behavior. `-v` is verbose. `--dry-run` shows intended changes without modifying the destination.

### Step 3 — Execute

```bash
rsync -av --partial /data/raw/ operator@server-b:/data/raw/
```

`--partial` keeps partial transfer data so an interrupted transfer can resume more efficiently.

### Step 4 — Verify

Run a second dry run. A clean result means rsync sees little or nothing left to transfer.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

For large operational transfers, resumability and a dry-run capability make rsync safer and more efficient than treating every interruption as a fresh copy.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 7 — Check a systemd Service

### Difficulty
Basic

### Topics Covered
- 05 systemd

### Problem

A pipeline service called `orders-consumer.service` is reported as unavailable. Before restarting anything, determine its current state.

### What You Need to Determine

1. Which command checks the service?
2. How do you start/stop/restart it when appropriate?
3. What evidence should you collect first?


### Solution

### Step 1 — Inspect

```bash
systemctl status orders-consumer.service
```

This shows whether the service is active, failed, its main PID, and recent service-related information.

### Step 2 — Inspect logs

```bash
journalctl -u orders-consumer.service --since "15 minutes ago"
```

Do this before blindly restarting so the failure evidence is preserved.

### Step 3 — Operate only after diagnosis

```bash
sudo systemctl restart orders-consumer.service
```

Then:

```bash
systemctl is-active orders-consumer.service
```

Expected representative result:

```text
active
```

Do not interpret a successful restart as proof that the underlying issue is permanently fixed.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Production operations should follow observe → diagnose → change → verify, not restart → hope.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 8 — Inspect Recent systemd Logs

### Difficulty
Basic

### Topics Covered
- 05 systemd
- 09 Logs

### Problem

`orders-consumer.service` failed a few minutes ago. You need only the recent service journal rather than the entire system log.

### What You Need to Determine

1. Which command filters by service?
2. How do you restrict the time window?
3. How do you follow new entries?


### Solution

### Step 1 — Recent service logs

```bash
journalctl -u orders-consumer.service --since "15 minutes ago"
```

`-u` selects the systemd unit. `--since` limits the time window.

### Step 2 — Follow new entries

```bash
journalctl -u orders-consumer.service -f
```

`-f` follows new journal entries, similar to following a live log.

### Step 3 — Interpret

Look for the first meaningful error, not merely the last message. Correlate the timestamp with service state and application behavior.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Narrow time and service filters reduce investigation noise and help build a reliable incident timeline.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 9 — First Resource Check

### Difficulty
Basic

### Topics Covered
- 06 Monitoring

### Problem

A batch job is unexpectedly slow. You do not yet know whether CPU, memory, or load is the main problem.

### What You Need to Determine

1. Which commands give a quick first view?
2. What does load average tell you?
3. Why should you avoid guessing from one metric?


### Solution

### Step 1 — Check load and CPU

```bash
uptime
nproc
```

`uptime` shows load averages and uptime. `nproc` shows the number of available processing units.

### Step 2 — Inspect processes

```bash
top
```

Look for CPU saturation, memory use, and processes consuming resources.

### Step 3 — Inspect memory

```bash
free -h
```

Look at `available`, not merely `free`.

### Step 4 — Form a hypothesis

If CPU is not saturated but tasks are blocked, investigate memory pressure or I/O rather than declaring the server CPU-bound.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Resource diagnosis is comparative. CPU, memory, load, and I/O must be interpreted together.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 10 — Run a Service Under a Dedicated Account

### Difficulty
Basic

### Topics Covered
- 10 Hygiene

### Problem

A Python pipeline is currently running as `root`. Redesign the service so it runs under a dedicated non-interactive service account named `pipeline`.

### What You Need to Determine

1. Why is root a poor default?
2. How should the account be created?
3. How do you verify the service identity?


### Solution

### Step 1 — Create the account

```bash
sudo useradd --system --home /nonexistent --shell /usr/sbin/nologin pipeline
```

`--system` creates a service-oriented account. `--shell /usr/sbin/nologin` prevents normal interactive login.

### Step 2 — Configure systemd

The unit should contain:

```ini
[Service]
User=pipeline
Group=pipeline
```

### Step 3 — Verify

```bash
systemctl cat orders-consumer.service
ps -eo user,pid,cmd | grep orders-consumer
```

The process should show `pipeline` rather than `root`.

### Step 4 — Verify file access

Grant the service only the directories and resources it actually needs.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

A dedicated service identity reduces blast radius, clarifies ownership, and supports least privilege.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.

# Part 2 — Moderate

## Question 11 — 11 — Verify an Unexpected Host-Key Warning

### Difficulty
Moderate

### Topics Covered
- 01 SSH

### Problem

SSH warns that the host key for `data01` differs from the previously recorded key. Determine the safe response.

### What You Need to Determine

1. What evidence should you verify before changing `known_hosts`?
2. Why should you not blindly delete the old key?
3. How do you inspect the stored entry?


### Solution

### Step 1 — Treat the warning as security-relevant

Do not bypass host-key verification merely to make the connection work.

### Step 2 — Inspect the stored entry

```bash
ssh-keygen -F data01
```

This finds matching entries in `known_hosts`.

### Step 3 — Verify the server identity out of band

Confirm with the infrastructure owner or trusted server inventory whether the host was rebuilt or its SSH host key legitimately changed.

### Step 4 — Update only after verification

If the change is legitimate, remove the obsolete entry using the controlled mechanism:

```bash
ssh-keygen -R data01
```

Then reconnect and verify the newly presented fingerprint through a trusted channel.

### Step 5 — Record the reason

Document whether the server was rebuilt, rotated, or otherwise changed.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Host-key verification protects against connecting to the wrong machine. A changed key is evidence to investigate, not an annoyance to suppress.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 12 — 12 — Keep an SSH Connection Alive

### Difficulty
Moderate

### Topics Covered
- 01 SSH

### Problem

An SSH session to a remote server drops during periods of inactivity. Configure client keepalives without confusing them with application-level health checks.

### What You Need to Determine

1. Which SSH settings can help?
2. Where can they be configured?
3. What problem do keepalives actually solve?


### Solution

### Step 1 — Configure client keepalives

For a specific host:

```sshconfig
Host data01
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

`ServerAliveInterval` sends an SSH-level keepalive request after the configured idle period. `ServerAliveCountMax` controls how many unanswered requests are tolerated.

### Step 2 — Test

```bash
ssh data01
```

Observe whether the connection survives the previously problematic idle period.

### Step 3 — Interpret correctly

Keepalives help detect or maintain idle network sessions. They do not make a broken application healthy and do not replace monitoring.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Keepalives solve session-liveness problems; they are not a substitute for service health checks or incident diagnosis.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 13 — 13 — Avoid Unnecessary Agent-Key Exposure

### Difficulty
Moderate

### Topics Covered
- 01 SSH

### Problem

Your SSH agent contains many keys and a bastion path is required. Explain why forwarding an agent through servers can increase risk and choose a safer approach.

### What You Need to Determine

1. What is the risk?
2. When can agent forwarding be dangerous?
3. What safer configuration can reduce accidental key use?


### Solution

### Step 1 — Identify the exposure

An SSH agent holds credentials that may authorize access to other systems. Forwarding access to that agent through an intermediate server increases the trust placed in the intermediate host.

### Step 2 — Prefer explicit identities

Use host-specific `IdentityFile` settings and, when appropriate:

```sshconfig
IdentitiesOnly yes
```

### Step 3 — Use ProxyJump

Prefer:

```bash
ssh -J bastion data-private
```

when it satisfies the access requirement, rather than unnecessarily forwarding the agent.

### Step 4 — Verify the path

```bash
ssh -G data-private
```

Confirm the intended identity and proxy configuration.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Credentials should be exposed only where necessary. Proxying a connection is not the same as forwarding a credential agent.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 14 — 14 — Build a Persistent PostgreSQL Tunnel

### Difficulty
Moderate

### Topics Covered
- 02 Tunnels
- 01 SSH

### Problem

A private PostgreSQL server is reachable only through `bastion`. An analyst needs a local connection to it for 30 minutes without an interactive remote shell.

### What You Need to Determine

1. How do you combine ProxyJump and local forwarding?
2. Why use `-N`?
3. How should the local bind address be chosen?


### Solution

### Step 1 — Create the tunnel

```bash
ssh -N -L 127.0.0.1:15432:127.0.0.1:5432 -J bastion data-private
```

`-L` creates local forwarding. Binding to `127.0.0.1` limits the local listener to the operator's machine. `-J` routes through the bastion. `-N` requests no remote shell.

### Step 2 — Connect

```bash
psql -h 127.0.0.1 -p 15432 -U orders_reader orders
```

### Step 3 — Verify the listener

```bash
ss -ltnp | grep 15432
```

### Step 4 — Stop safely

Terminate the SSH process when the tunnel is no longer required.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Bind tunnel endpoints narrowly. A tunnel is an access path and should not accidentally become a new network service for every local user/interface.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 15 — 15 — Decide Whether tmux or systemd Is Appropriate

### Difficulty
Moderate

### Topics Covered
- 03 tmux
- 05 systemd

### Problem

A developer asks you to keep a production ingestion process alive inside tmux permanently because SSH disconnects have killed it before. Decide whether this is appropriate.

### What You Need to Determine

1. What problem does tmux solve?
2. What should run under systemd instead?
3. What transitional workflow is reasonable?


### Solution

### Step 1 — Separate interactive work from services

tmux protects an interactive process from terminal loss.

systemd provides service lifecycle management, restart behavior, boot integration, logs, and controlled execution.

### Step 2 — Use tmux for investigation or manual one-off work

```bash
tmux new -s investigation
```

### Step 3 — Move recurring production work to systemd

A service should have a unit with an explicit service account, working directory, restart policy, and environment.

### Step 4 — Verify the production service

```bash
systemctl status orders-consumer.service
journalctl -u orders-consumer.service --since "30 minutes ago"
```

The recurring pipeline should not depend on a human maintaining an interactive tmux session.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

tmux is an operator tool. systemd is a service manager. Choosing the correct lifecycle mechanism is an operational design decision.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 16 — 16 — Resume a Large rsync Transfer Safely

### Difficulty
Moderate

### Topics Covered
- 04 Transfers

### Problem

A 100 GB directory transfer was interrupted at 62 GB. You need to resume it without blindly overwriting unrelated destination data.

### What You Need to Determine

1. What should you inspect first?
2. Which rsync options help?
3. How do you verify the intended changes before execution?


### Solution

### Step 1 — Dry-run the intended transfer

```bash
rsync -av --partial --dry-run /data/raw/ operator@server-b:/data/raw/
```

### Step 2 — Interpret

The dry run shows what rsync would change. Investigate unexpected deletions or destination paths before proceeding.

### Step 3 — Resume

```bash
rsync -av --partial /data/raw/ operator@server-b:/data/raw/
```

Do not add `--delete` unless the destination is explicitly intended to mirror the source and the deletion semantics have been reviewed.

### Step 4 — Verify

Repeat the dry run. For important datasets, perform an integrity-oriented verification appropriate to the data and transfer design.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

A resumable transfer plus dry-run reduces operational risk. Never use destructive synchronization flags casually.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 17 — 17 — Choose Copy vs Sync with rclone

### Difficulty
Moderate

### Topics Covered
- 04 Transfers

### Problem

You must copy a dataset into an object-storage destination for archival, but the destination may contain additional files that must not be removed.

### What You Need to Determine

1. Should this be a copy or mirror-style operation?
2. What risk does sync introduce?
3. How do you verify the result?


### Solution

### Step 1 — Choose semantics

Use a copy-style workflow when the requirement is "add/update destination data" and existing destination objects must not be removed.

Conceptually:

```bash
rclone copy /data/archive remote:archive
```

### Step 2 — Dry-run when supported

```bash
rclone copy --dry-run /data/archive remote:archive
```

### Step 3 — Verify

Use rclone's listing/check capabilities appropriate to the configured remote and dataset.

### Step 4 — Avoid accidental mirroring

A sync operation intentionally makes the destination resemble the source and can delete destination objects. Do not select it unless that is the requirement.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Copy and synchronization have different deletion semantics. Tool choice must follow the desired state, not habit.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 18 — 18 — Diagnose a Restarting systemd Service

### Difficulty
Moderate

### Topics Covered
- 05 systemd
- 09 Logs

### Problem

A service repeatedly starts and exits. `systemctl status` shows it cycling. Determine whether systemd is restarting a failed application or whether the application is healthy.

### What You Need to Determine

1. Which unit settings should you inspect?
2. Which logs should you inspect?
3. How do you distinguish application failure from systemd behavior?


### Solution

### Step 1 — Inspect the unit

```bash
systemctl cat orders-consumer.service
```

Look for:

```ini
Restart=on-failure
RestartSec=5
```

### Step 2 — Inspect recent logs

```bash
journalctl -u orders-consumer.service --since "20 minutes ago"
```

Find the first application error preceding each exit.

### Step 3 — Inspect current state

```bash
systemctl status orders-consumer.service
```

### Step 4 — Diagnose

If the process exits with a configuration or dependency error and systemd restarts it, the restart policy is a symptom amplifier, not the root cause.

### Step 5 — Fix and verify

Correct the underlying application/configuration issue, then:

```bash
systemctl restart orders-consumer.service
systemctl is-active orders-consumer.service
```

Confirm it remains active rather than merely surviving one restart.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Automatic restart is useful for recoverable failures, but repeated restarts can hide the actual root cause. Diagnose the first failure.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 19 — 19 — Diagnose CPU vs Memory vs I/O

### Difficulty
Moderate

### Topics Covered
- 06 Monitoring

### Problem

A pipeline has slowed dramatically. `top` shows moderate CPU utilization, but users report that the server feels stuck. Determine the next diagnostic path.

### What You Need to Determine

1. Which commands distinguish CPU, memory, and I/O pressure?
2. What does `vmstat` contribute?
3. When would `iostat` and `pidstat` help?


### Solution

### Step 1 — Check memory

```bash
free -h
```

Look at available memory and swap behavior rather than only the free column.

### Step 2 — Check virtual memory behavior

```bash
vmstat 1 5
```

Pay attention to run queue, blocked processes, swap activity, and I/O-related columns.

### Step 3 — Check storage

```bash
iostat -xz 1 5
```

Look for high utilization, latency, and queueing.

### Step 4 — Identify the responsible process

```bash
pidstat -dru 1 5
```

This helps distinguish which process is consuming CPU, memory, or I/O.

### Step 5 — Form the hypothesis

Moderate CPU does not rule out I/O-bound or memory-pressure behavior. Correlate the evidence before changing the workload.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

The correct diagnostic question is not "is CPU high?" but "which resource is constraining progress?".

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 20 — 20 — Disk Full vs Inodes Full

### Difficulty
Moderate

### Topics Covered
- 07 Disk
- 09 Logs

### Problem

A service reports `No space left on device`. `df -h` shows 40% free space. Determine the likely cause and investigation path.

### What You Need to Determine

1. What second capacity dimension must you check?
2. Which commands help identify many-small-file problems?
3. How can deleted-open files complicate the diagnosis?


### Solution

### Step 1 — Check inodes

```bash
df -i
```

If inode usage is near 100%, the filesystem can fail file creation even while byte capacity remains available.

### Step 2 — Identify small-file-heavy locations

```bash
du -x --inodes /var 2>/dev/null | sort -n | tail
```

Use a narrower path when necessary.

### Step 3 — Check deleted-open files

```bash
sudo lsof +L1
```

A deleted file may continue consuming disk space while a process keeps it open.

### Step 4 — Correlate with logs and services

```bash
journalctl --since "30 minutes ago"
```

Determine whether log growth, temporary files, or application behavior caused the condition.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Disk capacity has at least two operational dimensions: bytes and inodes. Deleted-open files create a third important diagnostic pattern.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.

# Part 3 — Hard

## Question 21 — 21 — Consumer Failure: systemd → Journal → Resources

### Difficulty
Hard

### Topics Covered
- 05 systemd
- 06 Monitoring
- 09 Logs

### Problem

A systemd-managed consumer failed during a high-volume ingestion window. The service is currently inactive. You must determine whether the cause was an application error, OOM, or resource saturation before restarting it.

### What You Need to Determine

1. What evidence should be collected first?
2. How do you test the OOM hypothesis?
3. How do you distinguish resource symptoms from application errors?


### Solution

### Step 1 — Preserve the incident window

Record the approximate failure time and avoid immediately restarting until enough evidence is collected.

### Step 2 — Inspect service state

```bash
systemctl status orders-consumer.service
```

### Step 3 — Inspect application/service logs

```bash
journalctl -u orders-consumer.service --since "30 minutes ago"
```

### Step 4 — Check kernel evidence

```bash
journalctl -k --since "30 minutes ago"
```

Look for OOM-killer messages or other kernel events.

### Step 5 — Check resources

```bash
free -h
vmstat 1 5
iostat -xz 1 5
```

Use historical `sar` data when available to determine whether the resource condition preceded the failure.

### Step 6 — Diagnose

If kernel evidence shows an OOM kill, the service exit is a consequence. If the journal shows a configuration exception without resource evidence, the application failure is more likely causal.

### Step 7 — Fix and verify

Apply the narrowest safe fix, then restart:

```bash
sudo systemctl restart orders-consumer.service
systemctl is-active orders-consumer.service
```

Continue observing logs and resources after recovery.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

A service failure is an evidence-correlation problem. systemd tells you lifecycle state; the journal and kernel tell you why; resource tools explain pressure.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 22 — 22 — Disk Exhaustion from Spill and Logs

### Difficulty
Hard

### Topics Covered
- 07 Disk
- 06 Monitoring
- 09 Logs

### Problem

A server reports `No space left on device` during a large analytical job. The application uses temporary/spill storage and system logs have also grown.

### What You Need to Determine

1. How do you determine whether bytes or inodes are exhausted?
2. How do you identify the largest contributors?
3. How do you safely recover space without deleting live data?


### Solution

### Step 1 — Check filesystem capacity

```bash
df -h
df -i
```

This separates byte exhaustion from inode exhaustion.

### Step 2 — Locate large directories

```bash
du -xhd1 /data 2>/dev/null | sort -h
du -xhd1 /var 2>/dev/null | sort -h
```

### Step 3 — Check open deleted files

```bash
sudo lsof +L1
```

### Step 4 — Inspect workload spill/temp locations

Identify where the application or analytical engine writes temporary data. Do not delete files merely because their names look temporary; establish whether the process still needs them.

### Step 5 — Investigate logs

```bash
journalctl --disk-usage
```

Also inspect rotated logs under the relevant logging directories.

### Step 6 — Recover safely

Remove only confirmed obsolete files according to the application's retention semantics. Prefer fixing runaway retention or spill configuration over repeatedly deleting data.

### Step 7 — Verify

```bash
df -h
```

Then verify the application can continue and monitor whether the filesystem begins filling again.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Capacity incidents require root-cause analysis, not emergency deletion alone. Spill, logs, open deleted files, and inode exhaustion require different remedies.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 23 — 23 — Resume and Verify a 100 GB Partner Transfer

### Difficulty
Hard

### Topics Covered
- 04 Transfers
- 07 Disk

### Problem

A partner file transfer stopped at 70 GB. The destination has limited free space and the transfer must be resumed without creating an accidental second copy or exhausting the disk.

### What You Need to Determine

1. How do you validate destination capacity?
2. Which transfer workflow is safest?
3. How do you verify integrity after completion?


### Solution

### Step 1 — Check destination capacity

```bash
df -h /data/incoming
df -i /data/incoming
```

Confirm both bytes and inodes are sufficient.

### Step 2 — Dry-run rsync

```bash
rsync -av --partial --dry-run /data/partner/ operator@server-b:/data/incoming/
```

Inspect the proposed changes.

### Step 3 — Resume

```bash
rsync -av --partial /data/partner/ operator@server-b:/data/incoming/
```

### Step 4 — Verify

Repeat the dry run and, for operationally critical data, use a checksum/integrity strategy appropriate to the transfer.

### Step 5 — Avoid destructive synchronization

Do not add `--delete` unless mirroring is explicitly required and reviewed.

### Step 6 — Document

Record source, destination, transfer method, verification result, and any interruption.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Large-file transfer is both a networking and capacity problem. Destination disk health must be checked before and after transfer.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 24 — 24 — Private PostgreSQL Access Through Bastion and Tunnel

### Difficulty
Hard

### Topics Covered
- 01 SSH
- 02 Tunnels
- 10 Hygiene

### Problem

PostgreSQL is private. Operators must connect through a bastion, and the database server must not be exposed publicly. Design the operator workflow.

### What You Need to Determine

1. How should SSH config represent the path?
2. How should local forwarding be bound?
3. Which firewall boundary should protect PostgreSQL?


### Solution

### Step 1 — Use ProxyJump

```sshconfig
Host bastion
    HostName bastion.example
    User operator
    IdentityFile ~/.ssh/bastion_ed25519

Host db-private
    HostName 10.0.2.30
    User operator
    IdentityFile ~/.ssh/db_operator_ed25519
    ProxyJump bastion
```

### Step 2 — Create a local tunnel

```bash
ssh -N -L 127.0.0.1:15432:127.0.0.1:5432 db-private
```

### Step 3 — Connect locally

```bash
psql -h 127.0.0.1 -p 15432 -U orders_reader orders
```

### Step 4 — Apply network controls

PostgreSQL should be reachable only from approved private sources. The database should not be opened to the public Internet merely to simplify operator access.

### Step 5 — Verify

```bash
ss -ltn | grep 15432
```

Then verify database connectivity and close the tunnel when finished.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Network architecture and SSH configuration work together. A private database should remain private; tunnels provide controlled operator access.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 25 — 25 — Structured Log Investigation with jq

### Difficulty
Hard

### Topics Covered
- 08 CLI Data
- 09 Logs

### Problem

A pipeline failed for `run_id=abc123`. Application logs are JSONL and include `timestamp`, `level`, `run_id`, `component`, and `message`. Build a focused investigation.

### What You Need to Determine

1. How do you filter by run ID?
2. How do you restrict to errors?
3. How do you preserve a useful timeline?


### Solution

### Step 1 — Filter the run

```bash
jq -c 'select(.run_id == "abc123")' app.jsonl
```

`-c` emits compact JSON, useful for line-oriented processing.

### Step 2 — Narrow to errors

```bash
jq -c 'select(.run_id == "abc123" and .level == "ERROR")' app.jsonl
```

### Step 3 — Extract timeline fields

```bash
jq -r 'select(.run_id == "abc123") | [.timestamp, .level, .component, .message] | @tsv' app.jsonl
```

`-r` emits raw strings rather than JSON-quoted strings.

### Step 4 — Correlate

Compare the application timeline with:

```bash
journalctl --since "02:00" --until "02:30"
```

and relevant rotated logs.

### Step 5 — Diagnose

Do not declare root cause from one error line. Correlate the first failure, dependent errors, and system evidence.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Structured logs become powerful when filtered by stable identifiers such as run IDs and aligned with a time window.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 26 — 26 — Choose csvkit, Miller, or DuckDB

### Difficulty
Hard

### Topics Covered
- 08 CLI Data

### Problem

A 5 GB CSV needs schema inspection, a filtered aggregate, and conversion to Parquet. Choose the appropriate command-line tool(s) and justify the workflow.

### What You Need to Determine

1. Which tool is best for quick CSV inspection?
2. Which is useful for streaming transformations?
3. Which is strong for SQL analytics and Parquet output?


### Solution

### Step 1 — Inspect with csvkit

```bash
csvlook sample.csv | head
csvstat sample.csv
```

`csvlook` provides readable inspection; `csvstat` provides column statistics.

### Step 2 — Use Miller for streaming-style field operations

For example:

```bash
mlr --csv filter '$status == "SUCCESS"' sample.csv > success.csv
```

Miller is convenient for record-oriented transformations without writing a Python program.

### Step 3 — Use DuckDB for analytical SQL and Parquet

```bash
duckdb -c "COPY (SELECT * FROM read_csv_auto('sample.csv') WHERE status = 'SUCCESS') TO 'success.parquet' (FORMAT PARQUET);"
```

### Step 4 — Verify

Inspect the resulting Parquet with DuckDB:

```bash
duckdb -c "SELECT count(*) FROM 'success.parquet';"
```

### Step 5 — Decide when to move to Python

Move to Python when business logic, testing, API integration, complex state, or maintainability exceeds what concise CLI workflows can safely express.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Tool choice should follow the job: csvkit for inspection, Miller for record transformations, DuckDB for SQL analytics and columnar data workflows.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 27 — 27 — Diagnose an OOM-Killed Consumer

### Difficulty
Hard

### Topics Covered
- 06 Monitoring
- 05 systemd
- 09 Logs

### Problem

A consumer repeatedly restarts. The application log ends abruptly, and systemd shows the process exited unexpectedly. Determine whether the Linux OOM killer is involved.

### What You Need to Determine

1. Which kernel evidence should you inspect?
2. Which memory commands help?
3. How do you distinguish OOM from an application exception?


### Solution

### Step 1 — Inspect kernel messages

```bash
journalctl -k --since "30 minutes ago" | grep -Ei 'oom|out of memory|killed process'
```

### Step 2 — Inspect memory state

```bash
free -h
vmstat 1 5
```

Look for memory pressure and swap behavior.

### Step 3 — Inspect service logs

```bash
journalctl -u orders-consumer.service --since "30 minutes ago"
```

An abrupt application log ending combined with a kernel OOM message is strong evidence of an external kill.

### Step 4 — Inspect systemd behavior

```bash
systemctl cat orders-consumer.service
```

Look for restart policy and resource controls.

### Step 5 — Fix

Choose an evidence-based fix: reduce memory pressure, correct workload behavior, adjust an appropriate resource limit, or change processing strategy. Do not simply increase limits without understanding the workload.

### Step 6 — Verify

Observe:

```bash
systemctl is-active orders-consumer.service
free -h
journalctl -u orders-consumer.service -f
```

and confirm the repeated kill pattern has stopped.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

The OOM killer is a kernel-level event. Application logs alone may not contain the root-cause evidence.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 28 — 28 — Log Rotation and Compressed History

### Difficulty
Hard

### Topics Covered
- 09 Logs
- 07 Disk

### Problem

An application log has rotated. The current file contains no evidence for a failure that occurred yesterday. Older files are compressed.

### What You Need to Determine

1. How do you locate rotated logs?
2. How do you search compressed logs?
3. How do you avoid searching only today's file?


### Solution

### Step 1 — List log files

```bash
ls -lh /var/log/myapp/
```

Look for numbered and compressed files such as `.1` or `.gz`.

### Step 2 — Search compressed logs

```bash
zgrep -n 'abc123' /var/log/myapp/*.gz
```

Or inspect a compressed file:

```bash
zcat /var/log/myapp/app.log.2.gz | grep 'abc123'
```

### Step 3 — Define the incident window

Use the actual failure timestamp and search the files covering that period.

### Step 4 — Correlate with journal

```bash
journalctl --since "yesterday 02:00" --until "yesterday 03:00"
```

### Step 5 — Preserve evidence

Do not delete or rotate away the evidence while investigating unless the retention process requires it and evidence has been captured.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Production investigations must include rotated and compressed history. Current logs are only one slice of the evidence.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 29 — 29 — Scheduled Extraction Did Not Run

### Difficulty
Hard

### Topics Covered
- 05 systemd
- 09 Logs
- 10 Hygiene

### Problem

An hourly extraction is implemented as a systemd timer. The operator expected it to run after the server was offline overnight, but no run occurred.

### What You Need to Determine

1. What timer and service settings should you inspect?
2. What does `Persistent=true` change?
3. How do you distinguish timer failure from service failure?


### Solution

### Step 1 — Inspect the timer

```bash
systemctl status orders-extract.timer
systemctl cat orders-extract.timer
```

Look for `OnCalendar=` and whether `Persistent=true` is configured.

### Step 2 — Inspect timer schedule

```bash
systemctl list-timers --all
```

### Step 3 — Inspect the service

```bash
systemctl status orders-extract.service
journalctl -u orders-extract.service --since "24 hours ago"
```

### Step 4 — Understand persistence

`Persistent=true` causes a missed calendar activation to be triggered after the timer becomes active again, subject to systemd timer semantics. It does not mean every missed occurrence is replayed indefinitely.

### Step 5 — Check permissions/environment

If the timer fired but the service failed, investigate its user, working directory, environment, credentials, and application logs.

### Step 6 — Verify

Confirm both timer scheduling and successful service completion.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

A timer and its service are separate failure domains. Diagnose scheduling and execution independently.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 30 — 30 — Harden a Server Without Locking Yourself Out

### Difficulty
Hard

### Topics Covered
- 10 Hygiene
- 01 SSH

### Problem

You need to disable SSH password authentication, disable direct root login, restrict users, and add a firewall rule on a remote server. Design a safe change procedure.

### What You Need to Determine

1. What must be tested before changing SSH?
2. How do you validate SSH configuration?
3. How do you protect the recovery path while changing firewall rules?


### Solution

### Step 1 — Establish recovery

Keep the current administrative session open and confirm a second key-based connection path through the bastion.

### Step 2 — Validate intended SSH settings

Conceptually:

```text
PasswordAuthentication no
PermitRootLogin no
AllowUsers operator
```

Then:

```bash
sudo sshd -t
```

### Step 3 — Apply and test

Reload/restart SSH only after validation, then open a second session and confirm access.

### Step 4 — Configure firewall carefully

Allow SSH from the bastion/source network rather than from everywhere.

### Step 5 — Verify from the bastion

```bash
ssh operator@data-private
```

Only close the original recovery session after the new path works.

### Step 6 — Record the change

Document the settings, firewall rule, verification, and rollback/recovery path.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Remote hardening is a change-management problem. The safest procedure preserves a known-good access path until the replacement path is proven.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.

# Part 4 — Advanced

## Question 31 — 31 — Full Production Incident: Consumer Failure

### Difficulty
Advanced

### Topics Covered
- 01 SSH
- 05 systemd
- 06 Monitoring
- 09 Logs

### Problem

At 02:13 UTC, a private data-server consumer stops processing partner events. The server is reachable only through a bastion. The service is failed, application logs are incomplete, and the database appears healthy. Conduct an evidence-based incident investigation.

### What You Need to Determine

1. How do you access the server safely?
2. What evidence do you collect before changing state?
3. How do you separate application, resource, and kernel causes?
4. How do you verify recovery and document the incident?


### Solution

### Step 1 — Establish the access path

Use the configured bastion path:

```bash
ssh data-private
```

Do not bypass the intended network architecture by exposing the private server.

### Step 2 — Establish the time window

Use the known UTC failure time: 02:13 UTC. Keep the investigation bounded around that event.

### Step 3 — Inspect service state

```bash
systemctl status orders-consumer.service
```

### Step 4 — Inspect service logs

```bash
journalctl -u orders-consumer.service --since "02:00" --until "02:30"
```

### Step 5 — Inspect kernel evidence

```bash
journalctl -k --since "02:00" --until "02:30"
```

Check for OOM, storage, or other kernel events.

### Step 6 — Inspect resources

```bash
free -h
vmstat 1 5
iostat -xz 1 5
df -h
df -i
```

Use `sar` if historical data is available.

### Step 7 — Correlate application evidence

Inspect the relevant structured/rotated logs using `jq`, `zgrep`, or other appropriate tools. Correlate by `run_id`, timestamp, and component.

### Step 8 — Form and test the hypothesis

Example: if the kernel shows OOM immediately before the service exit, memory pressure is causal and the systemd failure is secondary.

### Step 9 — Fix and verify

Apply the narrowest safe fix. Restart only after evidence is captured:

```bash
sudo systemctl restart orders-consumer.service
systemctl is-active orders-consumer.service
```

Continue observing logs and resource behavior.

### Step 10 — Document

Record:

```text
symptom
root cause
contributing factors
evidence
fix
verification
preventive action
```

Write a runbook entry.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

A senior operator does not treat "service failed" as the root cause. The incident is reconstructed from access, service, kernel, resource, and application evidence.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 32 — 32 — Disk Pressure → Slowdown → OOM → Restart

### Difficulty
Advanced

### Topics Covered
- 06 Monitoring
- 07 Disk
- 05 systemd
- 09 Logs

### Problem

A data-processing job creates large spill files. Disk usage reaches 96%, I/O latency rises, the job slows, memory pressure increases, the kernel kills the process, and systemd restarts it. Explain the causal chain and identify root cause versus symptoms.

### What You Need to Determine

1. Which observations are symptoms?
2. What evidence proves the causal sequence?
3. What should be fixed first?
4. How do you prevent recurrence?


### Solution

### Step 1 — Reconstruct the timeline

Correlate:

```text
spill growth
→ disk pressure
→ I/O latency
→ application slowdown
→ memory growth
→ OOM
→ systemd restart
```

### Step 2 — Validate disk evidence

```bash
df -h
df -i
du -xhd1 /data 2>/dev/null | sort -h
```

Check whether spill/temporary storage is the dominant consumer.

### Step 3 — Validate I/O pressure

```bash
iostat -xz 1 5
pidstat -d 1 5
```

### Step 4 — Validate OOM

```bash
journalctl -k --since "30 minutes ago" | grep -Ei 'oom|out of memory|killed process'
```

### Step 5 — Identify the root cause

If the workload's spill behavior caused the disk and subsequent resource cascade, the OOM and systemd restart are downstream effects.

### Step 6 — Fix

Address spill volume, storage capacity, workload configuration, or processing strategy. Do not merely increase memory or disable restart behavior.

### Step 7 — Verify

Confirm:

```text
disk headroom restored
I/O latency normal
memory stable
no OOM events
service remains healthy
```

### Step 8 — Prevent

Add capacity monitoring, retention controls, workload guardrails, and a documented runbook.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Senior diagnosis distinguishes the initiating failure from secondary symptoms. Restarting the process does not remove a resource cascade.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 33 — 33 — Failed Hourly Extraction After Server Downtime

### Difficulty
Advanced

### Topics Covered
- 05 systemd
- 09 Logs
- 10 Hygiene
- 06 Monitoring

### Problem

An hourly systemd timer did not produce an expected extraction after the server was offline for six hours. The service account also recently lost read permission on its source directory.

### What You Need to Determine

1. How do you determine whether the timer fired?
2. What does `Persistent=true` imply?
3. How do you test the service account permissions?
4. How do you distinguish scheduling from authorization failure?


### Solution

### Step 1 — Inspect timer state

```bash
systemctl status orders-extract.timer
systemctl list-timers --all
systemctl cat orders-extract.timer
```

Check `OnCalendar=` and `Persistent=true`.

### Step 2 — Inspect service evidence

```bash
journalctl -u orders-extract.service --since "8 hours ago"
```

If the service attempted to run and failed with permission errors, the timer itself is not the root cause.

### Step 3 — Verify service identity

```bash
systemctl cat orders-extract.service
```

Identify `User=`.

Then inspect source permissions:

```bash
namei -l /data/source
ls -ld /data/source
```

### Step 4 — Test the actual access boundary

Use a safe read-only test under the service identity where appropriate. Do not grant broad permissions as a workaround.

### Step 5 — Fix

Restore the minimum required read permission to the service account/group.

### Step 6 — Verify

Confirm a successful service execution and inspect the next scheduled activation.

### Step 7 — Document

Record whether the missed run was due to timer semantics, service failure, or permissions.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Timer scheduling, service execution, and filesystem authorization are distinct layers. Treating them as one problem leads to wasted remediation.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 34 — 34 — Secure Remote Architecture for Data Tools

### Difficulty
Advanced

### Topics Covered
- 01 SSH
- 02 Tunnels
- 10 Hygiene
- 05 systemd

### Problem

Design a secure operator path to a public bastion, private data server, private PostgreSQL server, and private web UI. Operators need SSH access, database access, and temporary browser access without making internal services public.

### What You Need to Determine

1. What should be public?
2. How should ProxyJump be used?
3. How should database/UI access be tunneled?
4. Which firewall rules are appropriate?
5. How should users and keys be controlled?


### Solution

### Step 1 — Define network boundaries

```text
Internet
   |
   v
Bastion
   |
private network
   +--> data-server
          +--> PostgreSQL
          +--> web UI
```

Only the bastion needs controlled public administrative ingress.

### Step 2 — Use SSH config

```sshconfig
Host bastion
    HostName bastion.example
    User operator
    IdentityFile ~/.ssh/bastion_ed25519

Host data-private
    HostName 10.0.2.20
    User operator
    IdentityFile ~/.ssh/data_private_ed25519
    ProxyJump bastion
```

### Step 3 — Tunnel PostgreSQL

```bash
ssh -N -L 127.0.0.1:15432:127.0.0.1:5432 data-private
```

### Step 4 — Tunnel a private web UI

```bash
ssh -N -L 127.0.0.1:18080:127.0.0.1:8080 data-private
```

Then use the local browser endpoint.

### Step 5 — Firewall

Allow SSH to the bastion from approved sources. Allow private server SSH only from the bastion/private network. Keep PostgreSQL and internal UI ports private.

### Step 6 — Identity

Use named operator accounts, key authentication, no direct root SSH, and least-privilege sudo.

### Step 7 — Verify

Test each access path independently and confirm internal ports are not publicly reachable.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Secure architecture reduces exposure before individual commands are considered. Tunnels provide controlled access without turning private services into public endpoints.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 35 — 35 — 500 GB Data Movement Decision

### Difficulty
Advanced

### Topics Covered
- 04 Transfers
- 07 Disk
- 10 Hygiene
- 08 CLI Data

### Problem

A 500 GB dataset must move from a Linux server to another server, and a second copy must be placed into object storage. The transfer may be interrupted and the destination must retain unrelated files.

### What You Need to Determine

1. When would you choose rsync?
2. When would rclone be appropriate?
3. How do you protect destination data?
4. How do you verify integrity and capacity?


### Solution

### Step 1 — Define each destination

For server-to-server transfer, use `rsync` because resumability and incremental synchronization are valuable.

```bash
rsync -av --partial --dry-run /data/export/ operator@server-b:/data/export/
```

For object storage, use `rclone copy` because the destination is an object-storage remote:

```bash
rclone copy --dry-run /data/export remote:archive
```

### Step 2 — Check capacity

```bash
df -h /data/export
df -i /data/export
```

### Step 3 — Execute only after dry-run review

Use the same commands without `--dry-run`.

### Step 4 — Preserve unrelated destination data

Do not use mirror-style deletion unless the requirement explicitly says the destination must match the source.

### Step 5 — Verify

Use transfer checks/checksum mechanisms supported by the tool and environment. Compare expected object/file counts and sizes where appropriate.

### Step 6 — Consider operational cost

For cloud/object-storage destinations, include bandwidth and egress implications in the design.

### Step 7 — Record

Document source, destination, tool, options, verification method, and final result.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Senior transfer design begins with semantics: copy, resume, mirror, object storage, integrity, capacity, and cost are separate requirements.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 36 — 36 — Build a Multi-Source Incident Timeline

### Difficulty
Advanced

### Topics Covered
- 09 Logs
- 08 CLI Data
- 05 systemd
- 06 Monitoring

### Problem

A pipeline failed at 02:13 UTC. Evidence is spread across application JSONL, systemd journal, kernel logs, rotated/compressed logs, and resource history. Build a defensible incident timeline.

### What You Need to Determine

1. How do you normalize the time window?
2. How do you filter structured logs?
3. How do you correlate system and application evidence?
4. How do you preserve evidence?


### Solution

### Step 1 — Define the UTC window

For example:

```text
02:00–02:30 UTC
```

Keep the same window across sources.

### Step 2 — Query the systemd journal

```bash
journalctl --since "02:00" --until "02:30"
```

Service-specific:

```bash
journalctl -u orders-consumer.service --since "02:00" --until "02:30"
```

### Step 3 — Query kernel evidence

```bash
journalctl -k --since "02:00" --until "02:30"
```

### Step 4 — Filter JSONL

```bash
jq -c 'select(.run_id == "abc123")' app.jsonl
```

### Step 5 — Search rotated/compressed logs

```bash
zgrep -n 'abc123' /var/log/myapp/*.gz
```

### Step 6 — Check resource history

Use `sar` if available, or inspect the relevant historical metrics.

### Step 7 — Construct the timeline

```text
02:11 resource pressure begins
02:12 application latency rises
02:13 process exits
02:13 kernel records event
02:13 systemd attempts restart
02:14 restart fails
```

Use only timestamps supported by evidence.

### Step 8 — Preserve evidence

Copy or retain relevant log excerpts and record commands and time windows. Avoid modifying evidence unnecessarily.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Incident timelines are evidence products. Never invent missing timestamps; distinguish observed facts from hypotheses.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 37 — 37 — Unexpected SSH Key and Possible Compromise

### Difficulty
Advanced

### Topics Covered
- 10 Hygiene
- 01 SSH
- 09 Logs
- 05 systemd

### Problem

An unfamiliar SSH public key appears in `operator`'s `authorized_keys`. You need to investigate whether it represents legitimate access or a security incident.

### What You Need to Determine

1. What evidence should you preserve?
2. Which logs should you inspect?
3. Why might rebuilding be preferable to only deleting the key?


### Solution

### Step 1 — Preserve evidence

Record the file metadata and relevant configuration before changing access.

```bash
ls -l ~/.ssh/authorized_keys
cat ~/.ssh/authorized_keys
```

Do not expose private keys.

### Step 2 — Inspect login history

```bash
last
lastlog
```

### Step 3 — Inspect SSH-related logs

```bash
journalctl | grep -Ei 'sshd|ssh'
```

Use the relevant time window and correlate source addresses where available.

### Step 4 — Inspect privilege activity

```bash
journalctl | grep -Ei 'sudo'
```

Also review unexpected service/account activity.

### Step 5 — Contain through an approved process

Remove unauthorized access only after preserving the evidence needed for the incident response process. Rotate credentials/keys through the appropriate controlled mechanism.

### Step 6 — Assess rebuildability

If server integrity cannot be trusted, deleting one key does not prove that the host is clean. A known-good rebuild from trusted images/configuration can provide stronger assurance.

### Step 7 — Verify

Confirm authorized access paths, SSH hardening, firewall boundaries, service identities, and audit evidence after recovery.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Security incidents require evidence preservation and scope assessment. Removing one artifact is not proof that the host is trustworthy again.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 38 — 38 — Turn a Two-Year-Old Server into a Rebuildable Server

### Difficulty
Advanced

### Topics Covered
- 10 Hygiene
- 05 systemd
- 07 Disk
- 09 Logs

### Problem

A data server has accumulated two years of manual changes. Nobody knows exactly which packages, users, SSH rules, service units, permissions, or time settings are required. Design a path toward a rebuildable server.

### What You Need to Determine

1. What state must be inventoried?
2. What belongs in bootstrap automation?
3. How do you prove idempotency?
4. How does this lead toward immutable infrastructure?


### Solution

### Step 1 — Inventory

Capture:

```text
users/groups
sudo rules
packages and versions
SSH configuration
firewall
timezone/time sync
service units/timers
data directories
secret locations
log policies
resource limits
```

### Step 2 — Define the desired state

Separate required configuration from historical accidents.

### Step 3 — Build bootstrap automation

Create a version-controlled bootstrap process that creates service accounts, installs approved packages, configures services, establishes directories/permissions, and applies safe baseline configuration.

### Step 4 — Make it idempotent

Run:

```bash
bash -n bootstrap.sh
sudo bash bootstrap.sh
sudo bash bootstrap.sh
```

The second execution should converge rather than duplicate or damage state.

### Step 5 — Test on a clean server

Do not trust the script merely because it works on the original server. Test on a disposable server.

### Step 6 — Move toward immutable infrastructure

Once the desired state is encoded and tested, build replacement servers from known images plus configuration rather than continuing to accumulate manual changes.

### Step 7 — Preserve state deliberately

Data and secrets should have explicit lifecycle/storage mechanisms; not every server-local artifact should be baked into an image.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Rebuildability turns undocumented operational knowledge into executable infrastructure. The goal is not automation for its own sake; it is predictable replacement.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 39 — 39 — Production Package Upgrade Breaks a Database Client

### Difficulty
Advanced

### Topics Covered
- 10 Hygiene
- 05 systemd
- 09 Logs
- 06 Monitoring

### Problem

A database client package was upgraded during maintenance. The next scheduled pipeline fails authentication or behavior checks. Determine the installed/candidate versions, correlate the service failure, and design a controlled recovery.

### What You Need to Determine

1. How do you inspect package state?
2. How do you correlate the upgrade with the failure?
3. When is a temporary hold justified?
4. How do you avoid uncontrolled package drift?


### Solution

### Step 1 — Inspect package state

```bash
apt policy <package>
dpkg -l <package>
```

Record installed and candidate versions.

### Step 2 — Inspect service evidence

```bash
journalctl -u orders-consumer.service --since "30 minutes ago"
systemctl status orders-consumer.service
```

### Step 3 — Correlate

Establish whether the failure began immediately after the package change and whether application evidence supports a compatibility issue.

### Step 4 — Recover deliberately

Use the organization's approved package rollback/version-management process. If compatibility testing requires a temporary hold:

```bash
sudo apt-mark hold <package>
```

Then document the reason and review date.

### Step 5 — Verify

Test the pipeline with the known-good package state and confirm the service remains healthy.

### Step 6 — Prevent drift

Do not leave the package held indefinitely. Test the newer version in a controlled environment and remove the hold when the compatibility issue is resolved:

```bash
sudo apt-mark unhold <package>
```

### Step 7 — Improve

Pin or control critical versions only with documented ownership and a maintenance lifecycle.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

Production package management balances security with compatibility. A temporary control is useful only when it has an owner, reason, and exit plan.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.
## Question 40 — 40 — G2 3 a.m. Production Simulation

### Difficulty
Advanced

### Topics Covered
- 01 SSH
- 02 Tunnels
- 03 tmux
- 04 Transfers
- 05 systemd
- 06 Monitoring
- 07 Disk
- 08 CLI Data
- 09 Logs
- 10 Hygiene

### Problem

At 03:00 UTC, a partner ingestion pipeline is failing. The private server is reachable only through a bastion. A 120 GB transfer is incomplete, the systemd consumer is restarting, disk usage is high, JSONL logs contain multiple run IDs, and operators suspect memory pressure. The server is also due for a hygiene review. Conduct the complete response.

### What You Need to Determine

1. How do you access the server safely?
2. What evidence do you collect before changing state?
3. How do you diagnose the transfer, service, disk, and memory symptoms?
4. How do you use jq/DuckDB or other CLI tools appropriately?
5. How do you recover safely?
6. What preventive actions belong in the runbook?


### Solution

### Step 1 — Access through the intended architecture

```bash
ssh data-private
```

The SSH config should encode the bastion/ProxyJump path. Do not expose the private server to the Internet as an emergency shortcut.

### Step 2 — Establish the incident window

Normalize all evidence to UTC and define a bounded window around 03:00.

### Step 3 — Inspect service state before restarting

```bash
systemctl status orders-consumer.service
journalctl -u orders-consumer.service --since "02:30" --until "03:15"
```

### Step 4 — Inspect kernel/resource evidence

```bash
journalctl -k --since "02:30" --until "03:15"
free -h
vmstat 1 5
iostat -xz 1 5
```

Look specifically for OOM events and I/O pressure.

### Step 5 — Inspect disk and inodes

```bash
df -h
df -i
du -xhd1 /data 2>/dev/null | sort -h
sudo lsof +L1
```

Determine whether the 120 GB transfer, application spill, logs, or deleted-open files are consuming capacity.

### Step 6 — Investigate structured logs

If logs are JSONL:

```bash
jq -c 'select(.run_id == "affected-run")' app.jsonl
```

Then extract a timeline:

```bash
jq -r 'select(.run_id == "affected-run") | [.timestamp,.level,.component,.message] | @tsv' app.jsonl
```

Use DuckDB when SQL-style aggregation or large-file analytical inspection is more appropriate.

### Step 7 — Inspect the transfer

Check destination capacity first:

```bash
df -h /data/incoming
df -i /data/incoming
```

Then dry-run the resumable transfer:

```bash
rsync -av --partial --dry-run /data/partner/ operator@server-b:/data/incoming/
```

Resume only after reviewing the planned changes.

### Step 8 — Diagnose the causal chain

Distinguish:

```text
symptom
→ contributing factor
→ root cause
→ secondary failure
```

For example, spill growth could cause disk/I/O pressure, which could contribute to memory pressure and ultimately OOM. The systemd restart is then a recovery mechanism, not the root cause.

### Step 9 — Recover safely

Apply the smallest safe change supported by evidence. Do not delete live data or use destructive sync flags merely to make the incident disappear.

Restart only after evidence collection:

```bash
sudo systemctl restart orders-consumer.service
systemctl is-active orders-consumer.service
```

### Step 10 — Observe recovery

Continue:

```bash
journalctl -u orders-consumer.service -f
```

and monitor disk, memory, and I/O. Confirm the service remains healthy and the underlying resource condition does not return.

### Step 11 — Review server hygiene

After service recovery, inspect:

```text
service account
sudo scope
package state
SSH hardening
firewall exposure
UTC/time synchronization
secret permissions
bootstrap/rebuildability
```

Do not make unrelated hardening changes during the critical recovery path unless required for containment.

### Step 12 — Write the incident/runbook entry

Document:

```text
impact
timeline
evidence
root cause
contributing factors
recovery
verification
preventive actions
owner
```

Then convert repeatable fixes into automation and monitoring.

### Why This Solution Works

This approach separates evidence collection from remediation, uses the narrowest relevant diagnostic tool, explains important command semantics, and verifies the resulting state. Exact output varies by server and workload.

### Production Lesson

The capstone tests the complete G2 operating loop: secure access → evidence collection → diagnosis → safe remediation → verification → prevention. Senior Data Engineering operations are about selecting evidence and making controlled decisions, not memorizing more commands.

### Common Mistakes

- Restarting, deleting, or changing configuration before collecting sufficient evidence.
- Using broader privileges or network exposure than the task requires.
- Treating a symptom as the root cause.
- Skipping verification after a change.

# G2 Topic Coverage Matrix

| Topic | Basic | Moderate | Hard | Advanced | Covered? |
|---|---:|---:|---:|---:|---|
| 01 SSH | 3 | 3 | 1 | 3 | ✅ |
| 02 Tunnels | 1 | 1 | 1 | 2 | ✅ |
| 03 tmux | 1 | 1 | 0 | 1 | ✅ |
| 04 Transfers | 1 | 2 | 1 | 1 | ✅ |
| 05 systemd | 2 | 3 | 2 | 4 | ✅ |
| 06 Monitoring | 1 | 1 | 3 | 4 | ✅ |
| 07 Disk | 0 | 1 | 3 | 2 | ✅ |
| 08 CLI Data | 0 | 1 | 2 | 1 | ✅ |
| 09 Logs | 1 | 3 | 3 | 4 | ✅ |
| 10 Hygiene | 1 | 2 | 1 | 4 | ✅ |

## Major Sub-Concept Coverage

| Sub-concept | Questions |
|---|---|
| SSH config, keys, host verification, ProxyJump, bastions, keepalives, agent risk | 1–3, 11–13, 24, 30, 34, 37, 40 |
| SSH `-L` tunnels and safe local binding | 4, 14, 24, 34, 40 |
| tmux and lifecycle choice | 5, 15, 40 |
| scp/rsync/rclone, resume, dry-run, integrity, copy vs sync | 6, 16–17, 23, 35, 40 |
| systemd, restart policies, timers, `Persistent=true`, journalctl | 7–8, 18, 21, 29, 31–34, 36, 37, 39–40 |
| CPU, memory, I/O, OOM, resource evidence | 9, 19, 21–22, 27, 31–32, 36, 39–40 |
| Disk space, inodes, deleted-open files, spill/large files | 20, 22–23, 32, 35, 40 |
| jq, csvkit, Miller, DuckDB, JSONL, CSV, Parquet | 25–26, 35–36, 40 |
| Rotated/compressed logs, time windows, UTC, correlation | 8, 18, 25, 28, 31, 36–38, 40 |
| Users, service accounts, sudo, packages, SSH hardening, firewall, secrets, bootstrap | 10, 24, 30, 33–34, 37–40 |

# Final G2 Self-Assessment

- [ ] Can I securely access a private server through a bastion?
- [ ] Can I create and use SSH configuration correctly?
- [ ] Can I safely investigate an unexpected host-key change?
- [ ] Can I create a localhost-bound SSH tunnel?
- [ ] Can I keep an interactive data job alive with tmux?
- [ ] Can I decide when tmux should be replaced by systemd?
- [ ] Can I reliably move large files with rsync?
- [ ] Can I use rclone with correct copy/sync semantics?
- [ ] Can I operate systemd services and timers?
- [ ] Can I investigate a failed service with journalctl?
- [ ] Can I distinguish CPU, memory, and I/O pressure?
- [ ] Can I identify OOM evidence?
- [ ] Can I diagnose disk and inode exhaustion?
- [ ] Can I find deleted-but-open files?
- [ ] Can I inspect CSV/JSON/Parquet from the CLI?
- [ ] Can I choose between csvkit, Miller, and DuckDB?
- [ ] Can I investigate rotated and compressed logs?
- [ ] Can I correlate application, systemd, kernel, and resource evidence?
- [ ] Can I run services under dedicated service accounts?
- [ ] Can I apply least-privilege sudo?
- [ ] Can I manage packages and controlled security updates?
- [ ] Can I harden SSH without locking myself out?
- [ ] Can I restrict network exposure with a firewall and private networking?
- [ ] Can I maintain UTC and synchronized time?
- [ ] Can I protect credentials with appropriate permissions?
- [ ] Can I investigate unexpected SSH access?
- [ ] Can I bootstrap a server repeatably?
- [ ] Can I test idempotency?
- [ ] Can I explain immutable infrastructure and pets vs cattle?
- [ ] Can I diagnose a realistic 3 a.m. production-like incident from evidence?
- [ ] Can I write an incident/runbook entry after recovery?

## Final Assessment Standard

For Hard and Advanced scenarios, explicitly distinguish:

```text
Symptom
vs
Root Cause
vs
Contributing Factor
vs
Fix
vs
Preventive Measure
```

The final operating standard is:

```text
Observe
→ preserve evidence
→ diagnose
→ change safely
→ verify
→ document
→ prevent recurrence
```
