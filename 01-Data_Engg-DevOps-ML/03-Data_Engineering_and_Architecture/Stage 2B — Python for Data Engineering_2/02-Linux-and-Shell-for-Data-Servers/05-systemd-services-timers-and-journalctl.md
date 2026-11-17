# Topic 05 — systemd Services, Timers, and journalctl

> **Stage 2B — Gap Module G2: Linux and Shell for Data Servers**  
> **Focus:** Production-oriented Linux service supervision, scheduled jobs, journaling, failure recovery, and resource controls for Data Engineers.

---

## 0. Module Objective

This module teaches how to operate **Linux-hosted Data Engineering services and scheduled workloads with systemd**.

The progression is:

```text
Beginner
   ↓
Intermediate
   ↓
Advanced
   ↓
Production Data Engineering Operations
```

By the end, you should be able to:

- explain why systemd exists
- understand systemd units and service lifecycle
- create and operate `.service` units
- use `systemctl`
- distinguish `start` from `enable`
- safely reload modified unit files
- configure `ExecStart`, `WorkingDirectory`, `User`, and `EnvironmentFile`
- investigate services with `journalctl`
- filter logs by unit, time, priority, and output format
- configure restart behavior
- recognize restart loops and start-limit protection
- understand graceful shutdown and `SIGTERM`
- configure service stop timeouts and kill behavior
- create timer-driven batch jobs
- use `OnCalendar`
- validate schedules with `systemd-analyze calendar`
- use `Persistent=true` for missed scheduled runs
- use randomized timer delays
- build `Type=oneshot` services
- reason about overlapping scheduled jobs
- use `After=`, `Wants=`, and `Requires=`
- apply CPU and memory controls
- understand basic systemd hardening
- understand user services and logout independence
- compare systemd with tmux, cron, and distributed orchestrators
- practice systemd on WSL2 when systemd is enabled
- troubleshoot failed services from evidence
- write operational runbooks

---

# 1. Start With the Problem

Imagine an engineer connects to a server:

```text
SSH
  ↓
run Python script
  ↓
process starts
  ↓
SSH session closes
  ↓
what happens?
```

For an interactive one-off job, `tmux` may be appropriate.

But consider a service that must run continuously:

```text
Kafka consumer
Python API
file processor
ingestion worker
pipeline helper
```

You do not want the service to depend on:

- an engineer staying logged in
- a terminal remaining open
- someone manually restarting it after every failure
- a shell environment being configured correctly
- an operator remembering how to start it after reboot

You need a machine-managed lifecycle.

That is where systemd fits.

> **systemd provides a machine-managed way to start, stop, supervise, restart, schedule, and observe processes and services on Linux.**

---

# 2. Why Data Engineers Need systemd

Data Engineering often includes workloads that run directly on Linux servers.

Examples:

```text
Python consumer
      ↓
PostgreSQL / Kafka / API
```

```text
Hourly extraction
      ↓
Python script
      ↓
Object storage
```

```text
File watcher
      ↓
new data
      ↓
processing
```

```text
Local API
      ↓
systemd service
```

The operational questions become:

- Who starts the process?
- What happens after reboot?
- What happens when it crashes?
- Where do I find its logs?
- How do I stop it safely?
- What if it fails repeatedly?
- What if it consumes too much memory?
- What if a scheduled job was missed during downtime?
- What if two scheduled executions overlap?
- What must start first?
- Which user should run it?
- How do I investigate an incident at 3 a.m.?

systemd gives you a common server-local mechanism for these concerns.

---

# 3. What systemd Is

At a high level:

```text
systemd
   |
   +-- service lifecycle
   |
   +-- timers
   |
   +-- dependencies
   |
   +-- process supervision
   |
   +-- resource controls
   |
   +-- journal integration
```

A common misconception is:

> "systemd is just Linux's cron."

It is not.

A better mental model is:

```text
systemd
=
server-local lifecycle manager
```

Timers are one part of systemd.

Services are another.

Logging integration, dependencies, resource controls, startup activation, and process supervision are additional capabilities.

---

# 4. The Core Systemd Mental Model

Remember these relationships:

```text
SERVICE
=
What should run?

TIMER
=
When should it run?

SYSTEMCTL
=
How do I operate it?

JOURNALCTL
=
What happened?

RESTART POLICY
=
What happens when it fails?

DEPENDENCIES
=
What must be available/order first?

RESOURCE LIMITS
=
How much can it consume?

USER
=
With whose permissions does it run?
```

And the broader G2 model:

```text
tmux
=
Human interactive operations

systemd
=
Server-local machine-managed lifecycle

orchestrator
=
Distributed workflow management
```

This distinction will be repeated throughout the module because it is central to production judgment.

---

# 5. systemd Units

A **unit** is a resource or object managed by systemd.

For this module, focus primarily on:

```text
.service
.timer
```

There are many other systemd unit types, but learning the entire systemd taxonomy is outside this module.

The most important relationship is:

```text
orders-extract.timer
        |
        | triggers
        v
orders-extract.service
        |
        v
Python batch job
```

Mental model:

```text
.service
=
process/service lifecycle

.timer
=
schedule/trigger
```

---

# 6. Where Unit Files Live

Systemd can load units from several locations.

Common administrator-managed locations include:

```text
/etc/systemd/system/
```

Distribution-provided units commonly appear under locations such as:

```text
/usr/lib/systemd/system/
```

or on some distributions:

```text
/lib/systemd/system/
```

For custom server applications, a common operational pattern is:

```text
/etc/systemd/system/my-service.service
```

Do not assume every Linux distribution uses exactly the same filesystem layout for packaged units.

For custom practice units, `/etc/systemd/system/` is the important location to understand.

---

# 7. `systemctl`

`systemctl` is the primary command-line interface for operating systemd units.

Core commands:

```bash
systemctl start myservice
systemctl stop myservice
systemctl restart myservice
systemctl status myservice

systemctl enable myservice
systemctl disable myservice

systemctl daemon-reload
```

These commands do different things.

Do not memorize them as a single list.

Understand the state transitions they produce.

---

# 8. `start`

Command:

```bash
systemctl start orders-consumer.service
```

Meaning:

> Ask systemd to start the service now.

Conceptually:

```text
inactive
   |
   | start
   v
active
```

`start` changes current runtime state.

It does not by itself mean:

> "Start this automatically after every reboot."

That is a different concern.

---

# 9. `stop`

Command:

```bash
systemctl stop orders-consumer.service
```

Meaning:

> Ask systemd to stop the service now.

For a well-behaved application, stopping generally gives it an opportunity to terminate gracefully.

Conceptually:

```text
active
   |
   | stop
   v
deactivating
   |
   v
inactive
```

The actual shutdown behavior depends on the service and systemd configuration.

---

# 10. `restart`

Command:

```bash
systemctl restart orders-consumer.service
```

Conceptually:

```text
running
   ↓
stop
   ↓
start
   ↓
running
```

Restart is useful after configuration changes or controlled recovery.

But there is an important incident-response principle:

> **Do not blindly restart a failing service before collecting useful evidence.**

A restart can change the state you are trying to investigate.

A better incident workflow is:

```text
status
  ↓
logs
  ↓
evidence
  ↓
diagnosis
  ↓
fix
  ↓
restart/start
  ↓
verify
```

---

# 11. `status`

Command:

```bash
systemctl status orders-consumer.service
```

This is usually your first diagnostic command.

Typical information includes:

- whether the unit is loaded
- whether it is active
- whether it failed
- main PID
- process state
- recent log messages
- exit status
- timestamps
- restart information where available

A conceptual status result may look like:

```text
● orders-consumer.service
   Loaded: loaded
   Active: active (running)
 Main PID: 1842
```

Or:

```text
Active: failed
```

The exact formatting varies by distribution and systemd version.

---

# 12. `enable`

Command:

```bash
systemctl enable orders-consumer.service
```

`enable` configures the unit for automatic activation through its configured installation relationships.

The key distinction is:

```text
start
=
start now

enable
=
configure automatic activation
```

Do not teach yourself:

```text
enable = start
```

That is incorrect.

---

# 13. `enable --now`

A common convenience form is:

```bash
systemctl enable --now orders-consumer.service
```

Conceptually:

```text
enable
+
start now
```

Use it when you intentionally want both behaviors.

This is especially convenient during controlled service deployment.

---

# 14. `disable`

Command:

```bash
systemctl disable orders-consumer.service
```

This removes the configured automatic activation relationship.

It does not necessarily mean:

> "Stop the service that is running right now."

Therefore:

```text
stop
=
runtime state

disable
=
future automatic activation
```

For a running service, you may need both operations depending on the desired outcome:

```bash
systemctl stop orders-consumer.service
systemctl disable orders-consumer.service
```

Do not execute broad service changes on production hosts without understanding their consequences.

---

# 15. `daemon-reload`

After changing a unit file:

```bash
sudo systemctl daemon-reload
```

systemd needs to reload the unit configuration.

Typical workflow:

```text
Edit unit
   ↓
daemon-reload
   ↓
status
   ↓
start/restart
   ↓
verify
```

A common mistake is:

```text
edit unit file
   ↓
restart
```

without first reloading the unit configuration.

The operational habit is:

```bash
systemctl daemon-reload
```

after changing unit definitions.

`daemon-reload` does not itself restart every service.

It tells systemd to reread unit configuration.

---

# 16. Start vs Enable — Critical Distinction

| Command | Immediate runtime effect | Future automatic activation |
|---|---|---|
| `start` | starts unit | no |
| `stop` | stops unit | no |
| `restart` | restarts unit | no |
| `enable` | not necessarily started | configures activation |
| `disable` | does not necessarily stop | removes activation |
| `enable --now` | starts now | configures activation |

This distinction is one of the most common systemd interview and production questions.

---

# 17. A Production Data Engineering Service

Consider an orders consumer:

```text
Kafka / queue
      |
      v
orders-consumer
      |
      v
PostgreSQL / API / storage
```

We want:

- a dedicated service account
- explicit working directory
- explicit Python interpreter
- environment configuration
- restart on failure
- delay between restarts
- network ordering
- logs in the journal

A realistic unit:

```ini
[Unit]
Description=Orders Consumer
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pipeline
WorkingDirectory=/opt/orders-consumer
ExecStart=/opt/orders-consumer/.venv/bin/python /opt/orders-consumer/consumer.py
Restart=on-failure
RestartSec=10
EnvironmentFile=/etc/orders-consumer/environment

[Install]
WantedBy=multi-user.target
```

Do not copy this into production without adapting paths, users, dependencies, and security requirements.

---

# 18. `[Unit]`

The `[Unit]` section describes relationships and general metadata.

Example:

```ini
[Unit]
Description=Orders Consumer
After=network-online.target
Wants=network-online.target
```

Important directives here include:

```text
Description
After
Wants
Requires
```

The section is not where the application command itself normally belongs.

That belongs in `[Service]`.

---

# 19. `[Service]`

The `[Service]` section describes how the service process is run.

Example:

```ini
[Service]
Type=simple
User=pipeline
WorkingDirectory=/opt/orders-consumer
ExecStart=/opt/orders-consumer/.venv/bin/python /opt/orders-consumer/consumer.py
Restart=on-failure
RestartSec=10
EnvironmentFile=/etc/orders-consumer/environment
```

This is where the operational lifecycle becomes concrete.

---

# 20. `[Install]`

The `[Install]` section describes how the unit participates in enablement.

Example:

```ini
[Install]
WantedBy=multi-user.target
```

This helps systemd determine the activation relationship created by:

```bash
systemctl enable orders-consumer.service
```

The important mental model is:

```text
[Unit]
=
relationships and description

[Service]
=
how the process runs

[Install]
=
how enablement hooks the unit into activation
```

---

# 21. `ExecStart`

Example:

```ini
ExecStart=/opt/orders-consumer/.venv/bin/python /opt/orders-consumer/consumer.py
```

This defines the command systemd should execute.

A production service should generally use explicit paths.

Compare:

```ini
ExecStart=python consumer.py
```

with:

```ini
ExecStart=/opt/orders-consumer/.venv/bin/python /opt/orders-consumer/consumer.py
```

The second is more explicit.

Interactive shells may have:

```text
PATH
virtual environment
aliases
shell startup files
```

A service should not depend on an engineer's interactive shell configuration.

---

# 22. Why Virtual Environment Paths Matter

A Data Engineering application may use:

```text
/opt/orders-consumer/.venv/
```

with dependencies installed there.

Therefore:

```ini
ExecStart=/opt/orders-consumer/.venv/bin/python /opt/orders-consumer/consumer.py
```

makes the runtime environment explicit.

This reduces surprises such as:

```text
works manually
      ↓
fails under systemd
      ↓
wrong Python
      ↓
missing package
```

---

# 23. `WorkingDirectory`

Example:

```ini
WorkingDirectory=/opt/orders-consumer
```

This defines the process's working directory.

Why it matters:

A program may use relative paths:

```python
open("config.json")
```

Under an interactive shell:

```text
/home/user/project
```

may be the working directory.

Under systemd, that assumption may be false.

Explicitly setting:

```ini
WorkingDirectory=/opt/orders-consumer
```

makes relative-path behavior predictable.

Prefer explicit paths in production applications when practical.

---

# 24. `User`

Example:

```ini
User=pipeline
```

This determines the user identity under which the service process runs.

The security principle is:

> **Do not run a service as root when it does not need root privileges.**

A dedicated service account can limit the blast radius of:

- application bugs
- compromised dependencies
- accidental writes
- unsafe commands

This module introduces the principle.

Topic 10 covers deeper server-user and sudo management.

---

# 25. `EnvironmentFile`

Example:

```ini
EnvironmentFile=/etc/orders-consumer/environment
```

The application can then receive configuration through environment variables.

For example, a protected environment file might conceptually contain:

```text
APP_ENV=production
DATABASE_HOST=db.internal
DATABASE_PORT=5432
LOG_LEVEL=INFO
```

Do not put real credentials into learning examples.

Environment files should have permissions appropriate to the sensitivity of their contents.

---

# 26. Configuration vs Secrets

Keep these concepts separate:

```text
application code
        |
        v
service definition
        |
        v
runtime configuration
        |
        v
secret management
```

An `EnvironmentFile` is a convenient way to supply environment variables.

It is not automatically a complete enterprise secret-management solution.

Avoid:

```ini
Environment=DATABASE_PASSWORD=real-password
```

in shared unit files.

For production systems, use the organization's approved secret-management mechanism.

---

# 27. Service Lifecycle

A simplified lifecycle:

```text
inactive
   |
   | start
   v
activating
   |
   v
active
   |
   | stop
   v
deactivating
   |
   v
inactive
```

Failure can produce:

```text
active
   |
   | process exits unexpectedly
   v
failed
```

With a restart policy:

```text
active
   |
   | failure
   v
restart delay
   |
   v
starting again
```

Understanding these states makes `systemctl status` much more useful.

---

# 28. `Type=simple`

For a normal long-running foreground application:

```ini
Type=simple
```

is a common choice.

The process started by `ExecStart` is treated as the service's main process.

For Python consumers and APIs that remain in the foreground, this is usually a natural model.

Do not teach the application to daemonize itself unless there is a specific reason.

Systemd is already the supervisor.

---

# 29. Why Foreground Processes Fit systemd

A common old-style daemon pattern is:

```text
start process
    ↓
fork
    ↓
background
    ↓
detach
```

For systemd-managed applications, prefer:

```text
systemd
   ↓
foreground process
   ↓
systemd supervises lifecycle
```

This makes:

- process identity
- exit status
- restart behavior
- logging

easier for systemd to manage.

---

# 30. `journalctl`

`journalctl` queries the systemd journal.

Basic command:

```bash
journalctl
```

This can produce a large amount of information.

For a specific service:

```bash
journalctl -u orders-consumer.service
```

The key operational lesson:

> **Do not search an entire server's journal when you already know the failing service. Narrow the evidence first.**

---

# 31. `journalctl -u`

Use:

```bash
journalctl -u orders-consumer.service
```

This filters logs by systemd unit.

This is one of the most useful commands in the module.

For an incident:

```text
Service failed
    ↓
systemctl status
    ↓
journalctl -u service
```

Then narrow further by time or priority.

---

# 32. Follow Logs With `-f`

Command:

```bash
journalctl -u orders-consumer.service -f
```

This follows new entries as they arrive.

Useful when:

- starting a service
- reproducing a failure
- observing a restart
- testing graceful shutdown
- validating a configuration change

Mental model:

```text
application
    ↓
stdout/stderr
    ↓
journal
    ↓
journalctl -f
    ↓
operator
```

---

# 33. Time Filtering With `--since`

Examples:

```bash
journalctl --since "1 hour ago"
```

```bash
journalctl -u orders-consumer.service \
    --since "2026-10-06 10:00:00"
```

Time filtering is critical during incidents.

Suppose:

```text
Pipeline failed between 02:00 and 02:15.
```

Do not inspect six hours of logs if a fifteen-minute window answers the question.

---

# 34. Time Filtering With `--until`

Example:

```bash
journalctl \
    --since "2026-10-06 02:00:00" \
    --until "2026-10-06 02:15:00"
```

Combined with a unit:

```bash
journalctl -u orders-consumer.service \
    --since "2026-10-06 02:00:00" \
    --until "2026-10-06 02:15:00"
```

This lets you reconstruct a bounded incident timeline.

---

# 35. Priority Filtering

A useful command:

```bash
journalctl -p err
```

For a service:

```bash
journalctl -u orders-consumer.service -p err
```

Priority filtering is useful for finding errors quickly.

But do not make this mistake:

> "Only inspect error-level logs."

An error often requires surrounding informational messages to explain the sequence that produced it.

Use:

```text
error filter
+
surrounding timeline
```

rather than error filtering alone.

---

# 36. Journal Priority Levels

At a practical level, systemd's journal supports priorities such as:

```text
emerg
alert
crit
err
warning
notice
info
debug
```

A useful operational command is:

```bash
journalctl -p err
```

Depending on the range syntax used, priority filters can include multiple severity levels.

The important skill is understanding that:

```text
priority
=
severity classification
```

not:

```text
priority
=
complete incident context
```

---

# 37. Journal Output Formats

Useful formats include:

```bash
journalctl -o short
```

```bash
journalctl -o short-iso
```

```bash
journalctl -o cat
```

```bash
journalctl -o json
```

Use them intentionally.

| Format | Useful for |
|---|---|
| `short` | normal human-readable logs |
| `short-iso` | clear ISO-style timestamps |
| `cat` | message-focused output |
| `json` | structured processing |

Do not choose a format just because it looks technically advanced.

Choose it because it helps the investigation.

---

# 38. Status vs Journal

A useful distinction:

```text
systemctl status
=
current state + summary
```

```text
journalctl
=
historical evidence
```

For an incident:

```text
status
  ↓
What is happening now?

journal
  ↓
What happened before?
```

You usually need both.

---

# 39. Restart Behavior

A long-running Data Engineering service should often recover from transient failures.

Example:

```ini
Restart=on-failure
```

This means systemd should restart the service when it terminates unsuccessfully under conditions covered by the policy.

A simple model:

```text
consumer running
      ↓
unexpected failure
      ↓
systemd notices
      ↓
restart policy
      ↓
consumer starts again
```

This is useful for:

- consumers
- ingestion workers
- small APIs
- pipeline agents

It is not a replacement for diagnosing persistent application failures.

---

# 40. `RestartSec`

Example:

```ini
RestartSec=10
```

This inserts a delay before restart.

Without a sensible delay:

```text
crash
 ↓
restart
 ↓
crash
 ↓
restart
 ↓
crash
```

can become an aggressive loop.

With a delay:

```text
crash
 ↓
wait 10 seconds
 ↓
restart
```

The correct value depends on the service.

---

# 41. Start-Limit Protection

A service that continuously crashes can produce:

```text
start
 ↓
crash
 ↓
restart
 ↓
crash
 ↓
restart
 ↓
...
```

This is a **restart loop**.

Systemd provides start-rate limiting to prevent unlimited rapid activation attempts.

Depending on systemd version/configuration, operators may encounter controls such as:

```ini
StartLimitIntervalSec=
StartLimitBurst=
```

These settings limit how many starts can occur within a period.

The exact effective behavior depends on the unit and systemd version.

The operational lesson is:

> **Restart policies must be paired with protection against pathological restart loops.**

---

# 42. Diagnosing a Restart Loop

Start with:

```bash
systemctl status orders-consumer.service
```

Then:

```bash
journalctl -u orders-consumer.service
```

Look for:

```text
started
failed
restart
started
failed
restart
```

Then narrow:

```bash
journalctl -u orders-consumer.service \
    --since "10 minutes ago"
```

The key question is:

> **What caused the original process failure?**

Do not focus only on the fact that systemd restarted it.

---

# 43. Graceful Shutdown

A production Data Engineering process should be designed to shut down safely.

Typical model:

```text
systemctl stop
      ↓
SIGTERM
      ↓
application receives signal
      ↓
stop accepting new work
      ↓
finish/record safe state
      ↓
close files/connections
      ↓
exit
```

This matters for:

- database connections
- network connections
- files
- checkpoints
- consumer offsets
- in-flight processing

---

# 44. `SIGTERM`

`SIGTERM` is the conventional graceful-termination signal.

A Python process can handle it.

Example:

```python
import signal
import sys
import time

stopping = False

def handle_sigterm(signum, frame):
    global stopping
    stopping = True
    print("SIGTERM received; shutting down gracefully")

signal.signal(signal.SIGTERM, handle_sigterm)

while not stopping:
    # Process one unit of work.
    time.sleep(1)

print("Cleanup complete")
sys.exit(0)
```

This is intentionally simple.

The production application should define what "safe shutdown" means for its own workload.

---

# 45. Graceful Shutdown for Consumers

A consumer should ideally:

```text
receive SIGTERM
       ↓
stop taking new work
       ↓
finish safe in-flight work
       ↓
commit/checkpoint where appropriate
       ↓
close resources
       ↓
exit
```

A poor shutdown strategy may cause:

- duplicate work
- lost in-memory state
- uncommitted offsets
- partial files
- abandoned database transactions

The exact behavior depends on the application and processing guarantees.

---

# 46. Stop Timeouts

A graceful shutdown cannot be allowed to wait forever.

Conceptually:

```text
SIGTERM
   ↓
grace period
   ↓
process still running
   ↓
systemd may force termination
```

A unit can configure a stop timeout such as:

```ini
TimeoutStopSec=30
```

The appropriate value depends on the application's shutdown behavior.

A value that is too small can kill a healthy cleanup process.

A value that is too large can leave stuck processes around for too long.

---

# 47. Kill Behavior

The conceptual progression is:

```text
SIGTERM
   ↓
graceful shutdown opportunity
   ↓
TimeoutStopSec
   ↓
forced termination if necessary
```

Systemd supports controls for how processes are terminated.

For this module, the important production lesson is:

> **Design the application to respond to graceful termination, then use a bounded timeout so shutdown cannot hang forever.**

---

# 48. Systemd Timers

A timer is a unit that activates another unit according to a schedule.

Mental model:

```text
orders-extract.timer
        |
        | trigger
        v
orders-extract.service
        |
        v
Python extraction
```

A timer is therefore not the batch job itself.

```text
timer
=
when

service
=
what
```

This separation is one of systemd's most useful design patterns.

---

# 49. `OnCalendar`

A timer can use calendar scheduling:

```ini
[Timer]
OnCalendar=hourly
```

This expresses:

> Run according to the systemd interpretation of an hourly calendar schedule.

Other expressions can specify dates/times.

The important skill is learning to validate schedules rather than guessing.

---

# 50. Validate Schedules

Use:

```bash
systemd-analyze calendar "hourly"
```

You can also validate a more explicit expression:

```bash
systemd-analyze calendar "*-*-* 01:00:00"
```

The command helps show:

- normalized interpretation
- next scheduled occurrence
- calendar parsing

Mental model:

```text
write schedule
      ↓
validate
      ↓
inspect next trigger
      ↓
deploy
```

---

# 51. `Persistent=true`

Example:

```ini
[Timer]
OnCalendar=hourly
Persistent=true
```

Consider:

```text
01:00 scheduled job
      ↓
server offline
      ↓
server starts at 04:00
      ↓
Persistent=true
      ↓
missed activation can be triggered
```

This is valuable for batch Data Engineering workloads.

But it creates a critical application requirement:

> **The job should be safe to execute after a delayed/missed schedule.**

If the job is not idempotent, a catch-up run may produce duplicates or inconsistent state.

---

# 52. Missed-Run Reasoning

Suppose:

```text
hourly extraction
```

is intended to produce:

```text
data for the previous hour
```

If the server is down for three hours, a single catch-up invocation may not be equivalent to three historical executions.

The batch job must understand:

```text
What period should this run process?
```

A robust design often uses explicit data intervals rather than assuming:

```text
run time = data time
```

This is a Data Engineering design concern, not merely a systemd setting.

---

# 53. Randomized Timer Delay

Systemd supports timer jitter using:

```ini
RandomizedDelaySec=60
```

Conceptually:

```text
scheduled time
      ↓
random delay
      ↓
actual activation
```

Why?

Suppose 100 servers all execute:

```text
00:00:00
```

at once.

That can create:

```text
network spike
database spike
API spike
storage spike
```

Randomized delay spreads the load.

---

# 54. Trade-Off of Randomized Delay

Jitter is useful when:

- exact execution time is not critical
- many hosts run similar workloads
- dependencies are shared
- a thundering-herd effect is possible

It may be inappropriate when:

- exact timing is a hard business requirement
- downstream processing expects a precise boundary

The decision is operational.

---

# 55. `Type=oneshot`

A batch job often uses:

```ini
Type=oneshot
```

Mental model:

```text
start
  ↓
run command
  ↓
complete
  ↓
exit
```

Compare:

```text
long-running service
=
stay active
```

with:

```text
oneshot service
=
perform work and finish
```

Examples of oneshot jobs:

- hourly extraction
- validation
- cleanup
- file processing
- batch export

---

# 56. Timer + Oneshot Architecture

A complete pattern:

```text
orders-extract.timer
        |
        v
orders-extract.service
        |
        v
/opt/orders/.venv/bin/python extract.py
        |
        v
exit
```

Service:

```ini
[Unit]
Description=Extract Orders

[Service]
Type=oneshot
User=pipeline
WorkingDirectory=/opt/orders
ExecStart=/opt/orders/.venv/bin/python /opt/orders/extract.py
```

Timer:

```ini
[Unit]
Description=Run Orders Extraction Hourly

[Timer]
OnCalendar=hourly
Persistent=true
RandomizedDelaySec=60

[Install]
WantedBy=timers.target
```

This is a central Topic 05 pattern.

---

# 57. Preventing Overlapping Runs

Consider:

```text
10:00
job starts
   ↓
job takes 90 minutes
   ↓
11:00
timer activates again
```

Potential consequences:

- duplicate processing
- duplicate files
- database contention
- conflicting writes
- resource exhaustion

Systemd's service activation model matters here: a service unit cannot simply have multiple independent active instances under the same unit name.

However:

> **Do not interpret that as a universal distributed lock or a guarantee against all forms of duplicate work.**

A robust batch job should still be designed around:

- idempotency
- unique run identifiers
- data intervals
- locks where appropriate
- atomic output publication

Systemd solves server-local activation concerns, not all data-consistency problems.

---

# 58. Dependency Semantics

Three directives are especially important:

```ini
After=
Wants=
Requires=
```

They are not synonyms.

---

# 59. `After=`

Example:

```ini
After=network-online.target
```

Meaning:

> If both units are being started, order this unit after the specified unit.

Important:

```text
After=
=
ordering
```

It does not by itself mean:

> Start the other unit.

This distinction is frequently misunderstood.

---

# 60. `Wants=`

Example:

```ini
Wants=network-online.target
```

Conceptually:

> When this unit is activated, systemd should also try to activate the wanted unit.

It is a weaker dependency relationship than `Requires=`.

Think:

```text
Wants
=
please start this related unit too
```

Failure semantics are not the same as `Requires=`.

---

# 61. `Requires=`

Example:

```ini
Requires=postgresql.service
```

Conceptually:

> Establish a stronger dependency relationship with the required unit.

The behavior when a required unit fails or becomes inactive depends on systemd's dependency semantics and transaction state.

The important mental model:

```text
After
=
ordering

Wants
=
weak relationship / activation request

Requires
=
stronger requirement relationship
```

---

# 62. Network Dependencies

A data service may use:

```ini
After=network-online.target
Wants=network-online.target
```

This is useful when the service needs network connectivity.

But do not claim:

```text
network-online.target
=
Internet is guaranteed
```

Actual network-online behavior depends on the host's networking implementation.

An external database, API, or object store may still be unavailable.

Your application must still handle dependency failure.

---

# 63. Resource Limits

systemd can apply resource controls to services.

Why?

Suppose:

```text
Python worker
     ↓
unexpected memory growth
     ↓
server memory pressure
     ↓
other workloads affected
```

A service-level resource limit can help contain the impact.

Think:

```text
application
   ↓
systemd resource boundary
   ↓
server
```

Resource controls are not a substitute for application optimization.

---

# 64. Memory Limits

A service can use a memory limit such as:

```ini
MemoryMax=1G
```

Conceptually:

```text
service memory
      |
      v
configured ceiling
      |
      +--> within limit: continue
      |
      +--> exceeds limit: systemd/cgroup enforcement
```

The exact resulting failure behavior should be observed in the target environment and systemd version.

Use the journal and service status to investigate the outcome.

Do not confuse:

```text
application has a memory leak
```

with:

```text
systemd correctly enforced a configured memory limit
```

Both can be true at the same time.

---

# 65. CPU Limits

Systemd can control CPU resources through cgroup-related settings.

A common modern control is:

```ini
CPUQuota=50%
```

Conceptually, the service is constrained to approximately half of one CPU's worth of CPU time over the relevant accounting interval.

CPU controls can prevent one service from monopolizing CPU.

But:

```text
CPU limit ↓
      ↓
resource impact ↓
      ↓
job duration may ↑
```

Resource controls are trade-offs.

---

# 66. Resource Limits Must Be Evidence-Based

Do not choose:

```ini
MemoryMax=128M
CPUQuota=10%
```

just because small numbers look safe.

Instead:

```text
observe normal workload
       ↓
measure resource usage
       ↓
understand variability
       ↓
set reasonable boundary
       ↓
test failure behavior
       ↓
monitor
```

Topic 06 covers deeper server-wide resource diagnosis.

---

# 67. Basic Service Hardening

The roadmap requires awareness rather than a complete systemd hardening course.

Important examples:

```ini
NoNewPrivileges=true
ProtectSystem=...
PrivateTmp=true
```

These controls can reduce the blast radius of a compromised or buggy process.

Hardening must be tested.

A setting that is excellent for one application may break another.

---

# 68. `NoNewPrivileges`

Example:

```ini
NoNewPrivileges=true
```

Conceptually:

> Prevent the service and its descendants from gaining additional privileges through mechanisms that would otherwise allow privilege escalation.

This is a defense-in-depth control.

Do not treat it as a complete security boundary.

---

# 69. Read-Only System Paths

Systemd provides controls such as:

```ini
ProtectSystem=full
```

or more restrictive values depending on the desired policy and systemd version.

The purpose is to reduce the ability of the service to modify protected system paths.

Before applying a read-only policy, determine:

```text
What does the application need to write?
```

For example:

```text
/opt/app/output
```

may need write access while:

```text
/etc
/usr
```

should not.

Hardening is an application-compatibility exercise.

---

# 70. `PrivateTmp`

Example:

```ini
PrivateTmp=true
```

This provides the service with an isolated temporary-directory environment.

Conceptually:

```text
Service A → private /tmp view
Service B → private /tmp view
```

This reduces accidental or malicious interaction through shared temporary files.

Again, test applications that intentionally communicate through `/tmp`.

---

# 71. User Services

Systemd can also manage user-level units.

For example:

```bash
systemctl --user status myservice.service
```

This operates within the user's systemd manager rather than the system-wide manager.

Conceptually:

```text
system manager
    |
    +-- system services

user manager
    |
    +-- user services
```

User services are useful in some development and personal-server scenarios.

Production server daemons commonly use system-level units and dedicated service accounts.

---

# 72. User Services and Logout

A user service may be tied to the user's session lifecycle depending on how the user manager is configured.

For a service to remain active independently of login sessions, systemd supports user lingering.

An administrator can enable lingering for a user with:

```bash
loginctl enable-linger username
```

This is an operational decision.

Do not enable lingering casually on shared systems.

The important concept is:

```text
interactive login
≠
systemd-managed service lifecycle
```

---

# 73. systemd vs tmux

| Requirement | Better fit |
|---|---|
| One-off interactive backfill | tmux |
| Interactive debugging | tmux |
| Long-running human-operated shell | tmux |
| Always-running consumer | systemd |
| Local API service | systemd |
| Hourly batch job | systemd timer |
| Complex distributed DAG | orchestrator |

Mental model:

```text
tmux
=
human session

systemd
=
machine-managed lifecycle
```

Once a job becomes a durable server service, it should generally stop depending on a human session.

---

# 74. systemd vs cron

Cron remains useful.

### Cron strengths

- simple
- familiar
- widely available
- suitable for straightforward scheduled commands

### systemd timer strengths

- integrated with service units
- journal integration
- dependency relationships
- resource controls
- service lifecycle management
- restart behavior
- missed-run behavior with `Persistent=true`
- centralized systemd operational model

A useful decision:

```text
simple legacy schedule
        ↓
cron may be sufficient

server-managed scheduled service
        ↓
systemd timer

complex multi-step workflow
        ↓
orchestrator
```

Do not claim cron is obsolete.

---

# 75. systemd vs Orchestrators

Systemd is primarily:

```text
server-local
```

An orchestrator is designed for:

```text
workflow-level / distributed execution
```

Examples include:

- Airflow
- Dagster
- managed workflow platforms

A complex pipeline might look like:

```text
extract
  ↓
validate
  ↓
transform
  ↓
load
  ↓
quality check
  ↓
publish
```

If that workflow requires:

- many tasks
- DAG dependencies
- distributed execution
- retries
- centralized scheduling
- workflow history
- backfills
- task-level observability

then systemd alone is usually the wrong abstraction.

---

# 76. The Architectural Boundary

Remember:

```text
tmux
=
interactive human work

systemd
=
server-local process lifecycle

orchestrator
=
distributed workflow management
```

Using the wrong layer creates operational debt.

Do not use:

```text
tmux
```

as a permanent service manager.

Do not use:

```text
systemd
```

as a replacement for a full distributed workflow orchestrator.

---

# 77. WSL2 Practice

WSL2 can be used for systemd practice when systemd is enabled.

Check:

```bash
ps -p 1 -o comm=
```

On a system using systemd as PID 1, you may see:

```text
systemd
```

If systemd is not enabled, systemd-based labs may not behave like a normal Linux VM.

A typical WSL configuration can enable systemd through `/etc/wsl.conf`:

```ini
[boot]
systemd=true
```

Then restart WSL from Windows as appropriate.

Because WSL behavior depends on version and configuration, verify the environment rather than assuming it.

For realistic server behavior, a full Linux VM is preferable.

---

# 78. Practice Environment

Use one of:

1. Linux VM
2. Multipass
3. Vagrant
4. WSL2 with systemd enabled
5. another disposable Linux server

Never use a production server for beginner break/fix exercises.

For systemd, a full Linux VM is usually more realistic than an ordinary application container because containers do not necessarily run systemd as PID 1.

---

# 79. Hands-On Lab Environment

Create a safe lab:

```text
server_lab/
└── 05/
    ├── orders-consumer/
    ├── extract-orders/
    └── notes/
```

The learning loop is:

```text
Read
  ↓
Do it on a real practice server
  ↓
Make it repeatable
  ↓
Break it
  ↓
Diagnose from evidence
  ↓
Fix
  ↓
Write runbook entry
  ↓
Explain aloud
```

Do not merely read these labs.

---

# 80. Hands-On Lab 1 — Service

## Objective

Turn a small Python worker into a systemd-managed service.

## Architecture

```text
systemd
   |
   v
orders-consumer.service
   |
   v
Python worker
```

## Prerequisites

- disposable Linux VM or WSL2 with systemd
- Python
- a non-production user
- sudo access for the practice environment

## Step 1 — Create application directory

```bash
sudo mkdir -p /opt/orders-consumer
sudo chown "$USER":"$USER" /opt/orders-consumer
```

## Step 2 — Create a simple worker

```bash
cat > /opt/orders-consumer/consumer.py <<'PY'
import signal
import sys
import time

stopping = False

def handle_sigterm(signum, frame):
    global stopping
    stopping = True
    print("SIGTERM received", flush=True)

signal.signal(signal.SIGTERM, handle_sigterm)

print("orders consumer started", flush=True)

while not stopping:
    print("consumer heartbeat", flush=True)
    time.sleep(5)

print("consumer shutting down", flush=True)
sys.exit(0)
PY
```

## Step 3 — Create a service user

Only on the disposable lab machine:

```bash
sudo useradd --system \
    --home /opt/orders-consumer \
    --shell /usr/sbin/nologin \
    pipeline
```

If the user already exists, do not create it again.

Set ownership:

```bash
sudo chown -R pipeline:pipeline /opt/orders-consumer
```

## Step 4 — Create the unit

```bash
sudo tee /etc/systemd/system/orders-consumer.service >/dev/null <<'UNIT'
[Unit]
Description=Practice Orders Consumer
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pipeline
WorkingDirectory=/opt/orders-consumer
ExecStart=/usr/bin/python3 /opt/orders-consumer/consumer.py
Restart=on-failure
RestartSec=5
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
UNIT
```

## Step 5 — Reload

```bash
sudo systemctl daemon-reload
```

## Step 6 — Start

```bash
sudo systemctl start orders-consumer.service
```

## Step 7 — Inspect

```bash
systemctl status orders-consumer.service
```

## Step 8 — Read logs

```bash
journalctl -u orders-consumer.service --since "5 minutes ago"
```

## Step 9 — Follow logs

```bash
journalctl -u orders-consumer.service -f
```

Press `Ctrl-C` to stop following.

## Step 10 — Stop

```bash
sudo systemctl stop orders-consumer.service
```

## Step 11 — Restart

```bash
sudo systemctl restart orders-consumer.service
```

## Step 12 — Enable

```bash
sudo systemctl enable orders-consumer.service
```

## Step 13 — Disable

```bash
sudo systemctl disable orders-consumer.service
```

## Verification

Confirm:

```bash
systemctl status orders-consumer.service
```

and:

```bash
journalctl -u orders-consumer.service --since "10 minutes ago"
```

## Key takeaway

The application is no longer dependent on an engineer's terminal session.

---

# 81. Hands-On Lab 2 — Failure and Restart

## Objective

Observe systemd restart behavior.

## Break the application

Modify the worker temporarily:

```python
raise RuntimeError("intentional practice failure")
```

Restart:

```bash
sudo systemctl restart orders-consumer.service
```

Observe:

```bash
systemctl status orders-consumer.service
```

Then:

```bash
journalctl -u orders-consumer.service --since "5 minutes ago"
```

## Expected pattern

```text
service starts
    ↓
application fails
    ↓
systemd detects failure
    ↓
Restart=on-failure
    ↓
RestartSec delay
    ↓
systemd attempts restart
```

If the service keeps failing, observe whether systemd eventually limits activation attempts.

## What to investigate

- exit status
- timestamps
- restart count
- original application error
- start-limit behavior

## Key takeaway

A restart policy can recover transient failures, but it cannot repair a permanently broken application.

---

# 82. Hands-On Lab 3 — Timer

## Objective

Create a timer-driven oneshot extraction.

## Service

Create:

```bash
sudo tee /etc/systemd/system/extract-orders.service >/dev/null <<'UNIT'
[Unit]
Description=Practice Orders Extraction

[Service]
Type=oneshot
User=pipeline
WorkingDirectory=/opt/orders-consumer
ExecStart=/usr/bin/python3 /opt/orders-consumer/extract.py
UNIT
```

Create the extraction script:

```bash
sudo tee /opt/orders-consumer/extract.py >/dev/null <<'PY'
from datetime import datetime, timezone

now = datetime.now(timezone.utc).isoformat()
print(f"orders extraction ran at {now}", flush=True)
PY
```

Ensure ownership:

```bash
sudo chown pipeline:pipeline /opt/orders-consumer/extract.py
```

## Timer

```bash
sudo tee /etc/systemd/system/extract-orders.timer >/dev/null <<'UNIT'
[Unit]
Description=Run Orders Extraction Hourly

[Timer]
OnCalendar=hourly
Persistent=true
RandomizedDelaySec=60
Unit=extract-orders.service

[Install]
WantedBy=timers.target
UNIT
```

## Reload

```bash
sudo systemctl daemon-reload
```

## Enable and start

```bash
sudo systemctl enable --now extract-orders.timer
```

## Inspect timers

```bash
systemctl list-timers
```

## Inspect the timer

```bash
systemctl status extract-orders.timer
```

## Inspect the service

```bash
journalctl -u extract-orders.service --since "2 hours ago"
```

---

# 83. Hands-On Lab 4 — Validate the Timer Schedule

Before trusting a calendar expression:

```bash
systemd-analyze calendar "hourly"
```

Try:

```bash
systemd-analyze calendar "*-*-* 01:00:00"
```

Observe the normalized schedule and next occurrence.

## Objective

Learn to validate rather than guess.

## Failure scenario

Create an incorrect schedule.

For example, deliberately choose a time you did not intend.

Validate it before installing it.

## Key takeaway

A timer expression is configuration, not magic.

---

# 84. Hands-On Lab 5 — Missed Timer

## Objective

Understand:

```ini
Persistent=true
```

Simulate or reason through:

```text
01:00
scheduled run

01:00–04:00
server unavailable

04:00
server returns
```

With:

```ini
Persistent=true
```

systemd can trigger the missed activation after the timer becomes active again.

## Investigation

Inspect:

```bash
systemctl status extract-orders.timer
```

and:

```bash
journalctl -u extract-orders.service
```

## Critical question

Is the batch job safe to run after a delay?

If not, fix the job's data-interval and idempotency behavior rather than blindly relying on the timer.

---

# 85. Hands-On Lab 6 — Journal Investigation

## Objective

Reconstruct a service failure from logs.

Create a staged incident:

```text
consumer starts
      ↓
dependency becomes unavailable
      ↓
consumer fails
      ↓
systemd restarts
      ↓
consumer fails again
```

Use:

```bash
systemctl status orders-consumer.service
```

Then:

```bash
journalctl -u orders-consumer.service
```

Then narrow:

```bash
journalctl -u orders-consumer.service \
    --since "15 minutes ago"
```

Then:

```bash
journalctl -u orders-consumer.service \
    --since "15 minutes ago" \
    -p err
```

Finally inspect the surrounding timeline without the severity filter.

## Required output

Write:

```text
Symptom:
Evidence:
Timeline:
Root cause:
Fix:
Verification:
Prevention:
```

---

# 86. Hands-On Lab 7 — Resource Limits

## Objective

Observe a controlled memory limit.

Create a safe practice process that intentionally allocates memory.

Do this only on a disposable VM.

A conceptual Python process:

```python
import time

blocks = []

while True:
    blocks.append(bytearray(10 * 1024 * 1024))
    time.sleep(1)
```

Do not run this on a production server.

Configure a deliberately small practice limit:

```ini
[Service]
MemoryMax=100M
```

Start the service.

Observe:

```bash
systemctl status memory-test.service
```

Then:

```bash
journalctl -u memory-test.service
```

## Explain

Distinguish:

```text
application memory growth
```

from:

```text
systemd/cgroup enforcement
```

The limit is a containment mechanism, not a fix for an application bug.

---

# 87. Hands-On Lab 8 — Graceful Shutdown

## Objective

Observe:

```text
systemctl stop
    ↓
SIGTERM
    ↓
cleanup
    ↓
exit
```

Use the earlier Python worker.

Run:

```bash
sudo systemctl start orders-consumer.service
```

Then:

```bash
sudo systemctl stop orders-consumer.service
```

Read:

```bash
journalctl -u orders-consumer.service --since "2 minutes ago"
```

You should see evidence that the application received the termination request and performed its shutdown path.

## Break it

Temporarily make the application ignore or delay shutdown.

Observe the effect of:

```ini
TimeoutStopSec=20
```

## Key takeaway

Graceful shutdown is an application design responsibility supported by systemd.

---

# 88. Break/Fix Scenario 1 — Wrong `ExecStart`

## Symptom

```text
Active: failed
```

## Evidence

```bash
systemctl status orders-consumer.service
```

Then:

```bash
journalctl -u orders-consumer.service --since "10 minutes ago"
```

## Diagnosis

The executable path does not exist.

Check:

```bash
ls -l /opt/orders-consumer/.venv/bin/python
```

or the configured interpreter path.

## Fix

Correct `ExecStart`.

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart orders-consumer.service
```

## Verification

```bash
systemctl status orders-consumer.service
```

---

# 89. Break/Fix Scenario 2 — Wrong Working Directory

## Symptom

Application says:

```text
file not found
```

although the file exists.

## Evidence

Inspect:

```ini
WorkingDirectory=
```

and application paths.

## Diagnosis

The application uses a relative path but systemd starts it somewhere else.

## Fix

Set the correct working directory or change the application to use explicit paths.

## Verification

Restart and inspect the journal.

---

# 90. Break/Fix Scenario 3 — Missing Environment File

## Symptom

Application reports missing configuration.

## Evidence

```bash
systemctl status orders-consumer.service
journalctl -u orders-consumer.service
```

Check:

```bash
ls -l /etc/orders-consumer/environment
```

## Diagnosis

The configured environment file is absent or unreadable.

## Fix

Correct the file path and permissions.

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart orders-consumer.service
```

## Prevention

Validate required runtime configuration before deployment.

---

# 91. Break/Fix Scenario 4 — Wrong User Permissions

## Symptom

```text
Permission denied
```

## Evidence

Check the service user:

```ini
User=pipeline
```

Then inspect ownership:

```bash
ls -ld /opt/orders-consumer
ls -l /opt/orders-consumer
```

## Diagnosis

The process does not have the permissions required for its intended files.

## Fix

Correct ownership or permissions rather than changing the service to root unnecessarily.

## Key takeaway

Do not solve every permissions problem with:

```ini
User=root
```

---

# 92. Break/Fix Scenario 5 — Application Exits Immediately

## Symptom

Service starts and quickly becomes inactive or failed.

## Evidence

```bash
systemctl status orders-consumer.service
journalctl -u orders-consumer.service
```

## Diagnosis

The application itself may be exiting.

Inspect the exit code and logs.

## Fix

Fix the application or its configuration.

Do not blindly increase restart frequency.

---

# 93. Break/Fix Scenario 6 — Restart Loop

## Symptom

Repeated:

```text
start
fail
restart
fail
```

## Evidence

```bash
systemctl status orders-consumer.service
journalctl -u orders-consumer.service --since "10 minutes ago"
```

## Diagnosis

Find the first meaningful application error.

## Fix

Fix the root cause.

Do not simply disable restart policy.

---

# 94. Break/Fix Scenario 7 — Timer Schedule Wrong

## Symptom

The job runs at an unexpected time.

## Evidence

```bash
systemctl list-timers
```

and:

```bash
systemd-analyze calendar "your-expression"
```

## Diagnosis

The calendar expression does not represent the intended schedule.

## Fix

Correct the timer.

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart extract-orders.timer
```

## Verification

Inspect:

```bash
systemctl status extract-orders.timer
systemctl list-timers
```

---

# 95. Break/Fix Scenario 8 — Missed Timer Behavior

## Symptom

A scheduled job did not execute while the server was down.

## Evidence

Inspect:

```bash
systemctl status extract-orders.timer
systemctl list-timers
journalctl -u extract-orders.service
```

## Diagnosis

Determine:

- whether `Persistent=true` is configured
- whether the timer was active
- whether the service executed after startup

## Fix

Configure appropriate persistence if catch-up behavior is required.

Then verify that the batch job is safe to catch up.

---

# 96. Break/Fix Scenario 9 — Overlapping Batch Work

## Symptom

A long-running batch appears to conflict with the next scheduled execution.

## Evidence

Inspect:

```bash
systemctl status extract-orders.service
systemctl status extract-orders.timer
journalctl -u extract-orders.service
```

## Diagnosis

Determine whether:

- the same service was already active
- another process instance exists
- the application itself launched parallel workers
- the schedule is too frequent for the workload

## Fix

Use appropriate service activation semantics and, when necessary, application-level locking/idempotency.

Do not assume a timer is a distributed scheduler.

---

# 97. Break/Fix Scenario 10 — Memory Limit Triggered

## Symptom

The service terminates after consuming too much memory.

## Evidence

```bash
systemctl status service-name
journalctl -u service-name
```

Then inspect the unit:

```bash
systemctl cat service-name
```

Look for:

```ini
MemoryMax=
```

## Diagnosis

Determine whether the configured limit was reached.

## Fix

Do not immediately increase the limit.

Ask:

```text
Is the workload expected to use more memory?
Is the application leaking memory?
Is the input unexpectedly large?
Is the limit appropriate?
```

---

# 98. Break/Fix Scenario 11 — Graceful Stop Fails

## Symptom

The service does not stop promptly.

## Evidence

```bash
systemctl status service-name
journalctl -u service-name
```

Inspect:

```ini
TimeoutStopSec=
```

and the application's signal handling.

## Diagnosis

The application may not handle `SIGTERM` correctly or may be stuck in cleanup.

## Fix

Improve application shutdown behavior.

Use a reasonable stop timeout.

Do not simply increase the timeout indefinitely.

---

# 99. Break/Fix Scenario 12 — Forgot `daemon-reload`

## Symptom

You edited a unit but systemd behaves as if the old configuration still exists.

## Evidence

```bash
systemctl cat orders-consumer.service
```

Then inspect the file on disk.

## Diagnosis

systemd has not reloaded the modified unit definition.

## Fix

```bash
sudo systemctl daemon-reload
```

Then:

```bash
sudo systemctl restart orders-consumer.service
```

## Key takeaway

Configuration changes require a deliberate reload workflow.

---

# 100. Troubleshooting Decision Tree

Use:

```text
Service not working
       |
       v
systemctl status
       |
       +--> Unit not found?
       |       |
       |       +--> verify unit name/path
       |
       +--> Failed?
       |       |
       |       +--> journalctl -u
       |
       +--> Restarting?
       |       |
       |       +--> inspect restart loop
       |
       +--> Activating?
       |       |
       |       +--> inspect dependencies/startup
       |
       +--> Running but unhealthy?
               |
               +--> inspect application logs/state
```

Then:

```text
journal evidence
       |
       +--> configuration?
       |
       +--> permissions?
       |
       +--> dependency?
       |
       +--> resource limit?
       |
       +--> application failure?
       |
       +--> network/service dependency?
```

The operator's responsibility is:

> **Diagnose from evidence before changing the system.**

---

# 101. Timer Troubleshooting Decision Tree

```text
Timer did not run
       |
       v
systemctl status timer
       |
       v
systemctl list-timers
       |
       +--> Timer inactive?
       |       |
       |       +--> start/enable appropriately
       |
       +--> Schedule wrong?
       |       |
       |       +--> systemd-analyze calendar
       |
       +--> Service failed?
       |       |
       |       +--> journalctl -u service
       |
       +--> Server was down?
       |       |
       |       +--> inspect Persistent=true
       |
       +--> Timer active but unexpected timing?
               |
               +--> inspect calendar + randomized delay
```

---

# 102. Journal Investigation Workflow

A production incident should follow:

```text
1. systemctl status
2. journalctl -u
3. narrow time window
4. inspect errors
5. inspect surrounding context
6. identify exit/restart behavior
7. determine root cause
8. fix
9. restart only when appropriate
10. verify
```

This is the systemd version of the G2 operator loop.

---

# 103. A 3 a.m. Service Runbook

## Service is down

```bash
systemctl status orders-consumer.service
```

Then:

```bash
journalctl -u orders-consumer.service --since "30 minutes ago"
```

If necessary:

```bash
journalctl -u orders-consumer.service \
    --since "30 minutes ago" \
    -p err
```

Identify:

```text
configuration
permissions
dependency
resource
application
```

Fix the cause.

If the unit file changed:

```bash
sudo systemctl daemon-reload
```

Then:

```bash
sudo systemctl restart orders-consumer.service
```

Verify:

```bash
systemctl status orders-consumer.service
journalctl -u orders-consumer.service --since "5 minutes ago"
```

---

# 104. 3 a.m. Timer Runbook

## Timer did not run

Start with:

```bash
systemctl status extract-orders.timer
```

Then:

```bash
systemctl list-timers
```

Validate:

```bash
systemd-analyze calendar "hourly"
```

Inspect the service:

```bash
journalctl -u extract-orders.service
```

Check:

```text
timer active?
schedule correct?
service successful?
server was down?
Persistent=true?
randomized delay?
```

Then verify the next trigger.

---

# 105. 3 a.m. Restart-Loop Runbook

```text
Service repeatedly crashes
       ↓
systemctl status
       ↓
journalctl -u
       ↓
narrow time range
       ↓
identify original error
       ↓
inspect RestartSec
       ↓
inspect start-limit behavior
       ↓
fix root cause
       ↓
verify stable operation
```

Do not treat:

```text
restart loop
```

as the root cause.

It is usually a symptom of an underlying failure.

---

# 106. Production Safety Rules

Follow these rules:

- avoid unnecessary root services
- use dedicated service accounts
- protect environment files
- do not expose secrets in shared unit files
- use restart policies thoughtfully
- prevent pathological restart loops
- investigate before restarting
- set resource limits based on evidence
- make scheduled jobs idempotent where possible
- understand missed-run behavior
- test timer schedules
- use dependencies deliberately
- test graceful shutdown
- do not apply aggressive hardening without compatibility testing
- do not use systemd as a substitute for distributed orchestration

---

# 107. Security Considerations

## Least privilege

Prefer:

```ini
User=pipeline
```

over:

```ini
User=root
```

when root privileges are not required.

## Environment files

Protect:

```text
/etc/orders-consumer/environment
```

according to the sensitivity of its values.

## Hardening

Use controls such as:

```ini
NoNewPrivileges=true
PrivateTmp=true
```

and suitable `ProtectSystem` settings when compatible.

## Resource containment

Use:

```ini
MemoryMax=
CPUQuota=
```

when justified.

Security and reliability are related:

```text
least privilege
+
resource containment
+
controlled lifecycle
=
smaller blast radius
```

---

# 108. Service Configuration Validation

Before deploying a service, verify:

```text
ExecStart exists
WorkingDirectory exists
User exists
EnvironmentFile exists
paths are readable
output directories are writable
dependencies are understood
```

Inspect a unit:

```bash
systemctl cat orders-consumer.service
```

Then:

```bash
systemctl status orders-consumer.service
```

A useful principle:

> **Make configuration explicit enough that another operator can understand it without asking the original author.**

---

# 109. Why systemd Services Should Usually Stay in the Foreground

A systemd service should normally run its primary process in the foreground.

Good:

```text
systemd
   ↓
python consumer.py
   ↓
foreground
```

Less useful:

```text
systemd
   ↓
shell script
   ↓
daemonize
   ↓
background process
```

The second pattern can complicate process tracking, exit status, and lifecycle supervision.

Let systemd manage the process lifecycle.

---

# 110. Data Engineering Scenario — Orders Consumer

Architecture:

```text
Kafka / queue
       |
       v
orders-consumer.service
       |
       v
Python worker
       |
       +--> PostgreSQL
       |
       +--> object storage
```

Recommended concerns:

```text
User
WorkingDirectory
ExecStart
EnvironmentFile
Restart=on-failure
RestartSec
TimeoutStopSec
MemoryMax
CPUQuota
```

Operational workflow:

```text
start
  ↓
status
  ↓
journal
  ↓
monitor
  ↓
failure
  ↓
restart
  ↓
verify
```

---

# 111. Data Engineering Scenario — Hourly Extraction

Architecture:

```text
extract-orders.timer
       |
       v
extract-orders.service
       |
       v
Python extractor
       |
       v
landing/object storage
```

Timer:

```ini
[Timer]
OnCalendar=hourly
Persistent=true
RandomizedDelaySec=60
```

Service:

```ini
[Service]
Type=oneshot
User=pipeline
ExecStart=/opt/orders/.venv/bin/python /opt/orders/extract.py
```

Production questions:

- What interval is this run responsible for?
- Is it idempotent?
- What happens after downtime?
- What if the extraction takes longer than an hour?
- Where are outputs published?
- How is failure detected?
- How is the run verified?

---

# 112. Data Engineering Scenario — File Processor

```text
incoming directory
       |
       v
file processor service
       |
       v
validation
       |
       v
transform
       |
       v
output
```

systemd can supervise the long-running process.

But systemd does not automatically provide:

- distributed task scheduling
- data lineage
- DAG visualization
- business-level retry semantics
- cross-server workflow coordination

Know the boundary.

---

# 113. Data Engineering Scenario — API Service

```text
systemd
   |
   v
Python API
   |
   +--> database
   +--> storage
   +--> internal services
```

systemd can:

- start the API
- restart after failure
- provide logs
- constrain resources
- control shutdown
- start it after boot

A reverse proxy/load balancer and application-level health checking are separate concerns.

---

# 114. Data Engineering Scenario — Periodic Cleanup

```text
cleanup.timer
      |
      v
cleanup.service
      |
      v
temporary artifacts
```

This is a good systemd timer use case when:

- work is local to one server
- schedule is simple
- job is operational rather than a complex DAG

---

# 115. Idempotency

A scheduled job should ideally be safe to run more than once.

Suppose:

```text
extract_orders
```

runs twice.

A poorly designed job may create:

```text
orders_2026-10-06.csv
orders_2026-10-06_2.csv
```

or duplicate database rows.

A more robust job may use:

```text
run identifier
data interval
upsert
atomic publication
checkpoint
```

The exact strategy depends on the data system.

The systemd timer cannot solve idempotency for you.

---

# 116. Missed Runs and Idempotency

`Persistent=true` increases the importance of idempotency.

Why?

```text
scheduled run
     ↓
server offline
     ↓
server returns
     ↓
catch-up run
```

The job must know:

```text
What data should I process?
```

Do not assume:

```text
"run now"
```

means:

```text
"process the period that was missed."
```

Data Engineering applications should explicitly model processing intervals where required.

---

# 117. Dependency Failure vs Service Failure

Suppose:

```text
orders consumer
      ↓
PostgreSQL unavailable
```

The service may be:

```text
active
```

but unhealthy.

Systemd's service state is not a complete application health model.

This distinction matters:

```text
process alive
≠
application healthy
```

For advanced production systems, health checks and application observability may be required.

Systemd remains the local process supervisor.

---

# 118. Common Mistakes

## Mistake 1 — Confusing start and enable

Remember:

```text
start = now
enable = future activation
```

## Mistake 2 — Forgetting daemon-reload

After changing a unit:

```bash
systemctl daemon-reload
```

## Mistake 3 — Running everything as root

Use a dedicated service account when possible.

## Mistake 4 — Blindly restarting

Investigate logs first.

## Mistake 5 — Infinite restart assumptions

Use `RestartSec` and start-limit protection.

## Mistake 6 — No graceful shutdown

Handle `SIGTERM`.

## Mistake 7 — Timer schedule guessed incorrectly

Validate with:

```bash
systemd-analyze calendar
```

## Mistake 8 — Assuming Persistent means "run every missed occurrence"

It provides catch-up behavior, but application semantics still matter.

## Mistake 9 — Ignoring overlap

A long-running batch requires deliberate concurrency/idempotency design.

## Mistake 10 — Overusing hardening settings

Hardening can break legitimate application behavior.

## Mistake 11 — Using systemd for distributed DAGs

Use an orchestrator when workflow complexity requires it.

## Mistake 12 — Treating journal errors as root cause

Errors are evidence; investigate the surrounding timeline.

---

# 119. Command Reference

## Service lifecycle

```bash
systemctl start SERVICE
```

Start now.

```bash
systemctl stop SERVICE
```

Stop now.

```bash
systemctl restart SERVICE
```

Stop and start according to service lifecycle rules.

```bash
systemctl status SERVICE
```

Inspect current state.

---

## Enablement

```bash
systemctl enable SERVICE
```

Configure automatic activation.

```bash
systemctl disable SERVICE
```

Remove automatic activation.

```bash
systemctl enable --now SERVICE
```

Enable and start now.

---

## Unit configuration

```bash
systemctl daemon-reload
```

Reload unit definitions.

```bash
systemctl cat SERVICE
```

Inspect the unit definition.

---

## Timers

```bash
systemctl list-timers
```

List timers and their schedule information.

```bash
systemctl status TIMER
```

Inspect a timer.

```bash
systemd-analyze calendar "hourly"
```

Validate a calendar expression.

---

## Journal

```bash
journalctl
```

Query the journal.

```bash
journalctl -u SERVICE
```

Filter by unit.

```bash
journalctl -u SERVICE -f
```

Follow a unit's logs.

```bash
journalctl --since "1 hour ago"
```

Filter by time.

```bash
journalctl --since "..." --until "..."
```

Bound a time window.

```bash
journalctl -p err
```

Filter by priority.

```bash
journalctl -o short-iso
```

Use ISO-style timestamps.

---

# 120. Useful Unit Inspection Commands

```bash
systemctl cat orders-consumer.service
```

Shows the unit definition as systemd sees it.

```bash
systemctl show orders-consumer.service
```

Shows systemd's parsed properties.

```bash
systemctl is-active orders-consumer.service
```

Useful for scripting.

```bash
systemctl is-enabled orders-consumer.service
```

Checks enablement state.

For troubleshooting, combine inspection commands rather than relying on one command.

---

# 121. Practical Service Deployment Sequence

Use:

```text
1. Create application
2. Create service account
3. Set application ownership
4. Create environment/configuration
5. Create unit
6. Inspect unit
7. daemon-reload
8. start
9. status
10. journal
11. verify behavior
12. enable if appropriate
13. document
```

This sequence is intentionally repetitive.

Operational reliability comes from repeatable process.

---

# 122. Practical Timer Deployment Sequence

Use:

```text
1. Create oneshot service
2. Test service manually
3. Validate calendar expression
4. Create timer
5. daemon-reload
6. enable --now timer
7. list-timers
8. inspect service journal
9. test missed-run behavior
10. document
```

Do not schedule an untested batch command first and debug it later.

---

# 123. Test the Service Before the Timer

A critical operational rule:

> **Test the service independently before scheduling it.**

First:

```bash
systemctl start extract-orders.service
```

Then:

```bash
systemctl status extract-orders.service
journalctl -u extract-orders.service
```

Only after the service works should you add:

```text
extract-orders.timer
```

This isolates failure domains.

---

# 124. Operational Runbook Template

Use this format:

```text
Service:
Purpose:
Owner:
Service account:
Unit file:
Environment file:
Working directory:
ExecStart:
Dependencies:
Restart policy:
Resource limits:
Timer:
Schedule:
Persistence:
Randomized delay:

Start:
Stop:
Restart:
Status:
Logs:
Timer inspection:

Known failure modes:
Recovery:
Verification:
Escalation:
```

This becomes part of your `server_lab/05/` notes.

---

# 125. Break/Fix Learning Loop

Use the exact G2 loop:

```text
Read
→ Do it on a real practice server
→ Make it repeatable
→ Break it
→ Diagnose from evidence
→ Fix
→ Write the runbook entry
→ Explain aloud
```

For every failure, record:

```text
Symptom
Commands used
Evidence
Root cause
Fix
Verification
Prevention
```

Do not skip the explanation step.

If you can fix a failure but cannot explain why it failed, your operational understanding is incomplete.

---

# 126. Practice Questions — Basic

Every question includes:

```text
Question
Expected Thinking
Solution
Explanation
```

## Basic 1 — What is systemd?

### Expected Thinking

Think about server-local lifecycle management.

### Solution

systemd is a Linux system and service manager that can start, stop, supervise, schedule, and manage services and related resources.

### Explanation

It is broader than a scheduler.

---

## Basic 2 — What is a systemd unit?

### Expected Thinking

Think of an object managed by systemd.

### Solution

A unit is a systemd-managed resource definition. This module focuses primarily on service and timer units.

### Explanation

Unit types provide different systemd management capabilities.

---

## Basic 3 — What is a service unit?

### Solution

A `.service` unit defines how a process or service should be started and managed.

### Explanation

It can include the command, user, working directory, restart behavior, dependencies, and resource controls.

---

## Basic 4 — What does `systemctl start` do?

### Solution

It asks systemd to start the specified unit now.

### Explanation

It changes current runtime state; it does not by itself configure future automatic activation.

---

## Basic 5 — What does `systemctl enable` do?

### Solution

It configures a unit for automatic activation according to its `[Install]` relationships.

### Explanation

Enablement and immediate startup are different concepts.

---

## Basic 6 — Why use `daemon-reload`?

### Solution

To make systemd reread modified unit definitions.

### Explanation

Editing a file on disk does not mean systemd has already incorporated the new configuration.

---

## Basic 7 — What does `ExecStart` define?

### Solution

The command systemd should execute for the service.

### Explanation

Production services should generally use explicit executable paths.

---

## Basic 8 — What is `WorkingDirectory`?

### Solution

The working directory from which the service process runs.

### Explanation

It makes relative-path behavior predictable.

---

## Basic 9 — Why specify `User`?

### Solution

To control the identity under which the service runs and avoid unnecessary root privileges.

### Explanation

Least privilege reduces blast radius.

---

## Basic 10 — What is `journalctl`?

### Solution

A command-line interface for querying the systemd journal.

### Explanation

It is a primary tool for investigating service history.

---

# 127. Practice Questions — Moderate

## Moderate 1 — Start vs Enable

### Question

What is the difference between:

```bash
systemctl start myservice
```

and:

```bash
systemctl enable myservice
```

### Expected Thinking

Separate runtime state from future activation.

### Solution

`start` starts the service now. `enable` configures automatic activation.

### Explanation

A service can be enabled without currently running.

---

## Moderate 2 — Why `daemon-reload`?

### Question

You edit a unit file and restart the service. Why might systemd still use old configuration?

### Solution

Because systemd may not have reloaded the changed unit definition.

### Explanation

Run:

```bash
systemctl daemon-reload
```

before restarting.

---

## Moderate 3 — Why `RestartSec`?

### Solution

It delays restart attempts.

### Explanation

The delay reduces aggressive restart loops and gives dependencies or transient failures time to recover.

---

## Moderate 4 — Why `Restart=on-failure`?

### Solution

It asks systemd to restart a service when it terminates unsuccessfully under the policy.

### Explanation

It is useful for long-running consumers and workers.

---

## Moderate 5 — Why can `journalctl -p err` be insufficient?

### Solution

Errors may lack the surrounding context needed to understand the sequence.

### Explanation

Investigate the timeline around the error.

---

## Moderate 6 — What is a timer?

### Solution

A systemd timer schedules or triggers a service unit.

### Explanation

The timer defines when; the service defines what.

---

## Moderate 7 — Why `Persistent=true`?

### Solution

It allows a timer to catch up after the system was unavailable during a scheduled activation.

### Explanation

The job still needs correct idempotency and interval semantics.

---

## Moderate 8 — What is `Type=oneshot`?

### Solution

A service type for work that runs and exits rather than remaining continuously active.

### Explanation

It is well suited to timer-triggered batch jobs.

---

## Moderate 9 — What does `After=` do?

### Solution

It establishes startup ordering relative to another unit.

### Explanation

It does not itself activate the other unit.

---

## Moderate 10 — What does `Wants=` do?

### Solution

It establishes a weaker relationship that causes the wanted unit to be started as part of the transaction.

### Explanation

Failure semantics differ from `Requires=`.

---

# 128. Practice Questions — Hard

## Hard 1 — Service Keeps Crashing

### Question

A Python consumer restarts every five seconds. What do you investigate?

### Expected Thinking

Do not focus only on restarting.

### Solution

Inspect:

```bash
systemctl status consumer.service
journalctl -u consumer.service --since "10 minutes ago"
```

Find the original application failure, then inspect restart and start-limit behavior.

### Explanation

The restart loop is a symptom.

---

## Hard 2 — Timer Missed

### Question

An hourly job's server was offline for three hours. What does `Persistent=true` change?

### Solution

It allows the timer to trigger a missed activation after the system becomes active again.

### Explanation

It does not automatically reproduce every missed hourly execution as separate runs.

---

## Hard 3 — Long-Running Batch

### Question

An hourly batch takes 90 minutes. What risks should you consider?

### Solution

Potential overlap, duplicate work, resource contention, and incorrect interval semantics.

### Explanation

Use systemd activation semantics plus application-level idempotency/locking where needed.

---

## Hard 4 — Service Runs Manually but Fails Under systemd

### Solution

Check:

- `ExecStart`
- `WorkingDirectory`
- `User`
- environment
- permissions
- PATH assumptions
- virtual environment
- dependencies

### Explanation

Interactive shell state is not the same as a systemd execution environment.

---

## Hard 5 — Service Runs as Root

### Question

Should you simply leave it as root because it works?

### Solution

No. Determine the minimum required permissions and use a dedicated account where practical.

### Explanation

Least privilege reduces the impact of application compromise or bugs.

---

## Hard 6 — Memory Limit

### Question

A service is killed after exceeding `MemoryMax`. Is the limit necessarily wrong?

### Solution

No.

### Explanation

The limit may be correctly protecting the server while also revealing an application workload problem.

---

## Hard 7 — Timer Schedule

### Question

How do you validate an `OnCalendar` expression?

### Solution

Use:

```bash
systemd-analyze calendar "expression"
```

### Explanation

It helps show how systemd interprets the expression and the next occurrence.

---

## Hard 8 — Graceful Shutdown

### Question

Why is `SIGTERM` preferable to immediate forced termination for a data consumer?

### Solution

It gives the application an opportunity to stop new work, complete safe work, commit/checkpoint state, close resources, and exit cleanly.

### Explanation

Forced termination can leave incomplete state.

---

## Hard 9 — Dependency

### Question

What is the difference between:

```ini
After=postgresql.service
```

and:

```ini
Requires=postgresql.service
```

### Solution

`After=` controls ordering if both are activated. `Requires=` establishes a stronger dependency relationship.

### Explanation

Neither should be interpreted as a guarantee that a database is application-ready.

---

## Hard 10 — Timer vs Orchestrator

### Question

When should an hourly systemd timer become an orchestrator workflow?

### Solution

When the workflow needs multi-step DAG semantics, distributed execution, centralized scheduling/history, complex retries, backfills, or cross-system task dependencies.

### Explanation

Systemd is server-local lifecycle management.

---

# 129. Practice Questions — Advanced

## Advanced 1 — Design a Consumer Service

### Question

Design a production-oriented systemd unit for a Python consumer.

### Expected Thinking

Include:

- dedicated user
- working directory
- explicit Python
- environment
- restart policy
- graceful shutdown
- resource boundaries

### Solution

A reasonable pattern:

```ini
[Unit]
Description=Orders Consumer
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pipeline
WorkingDirectory=/opt/orders
ExecStart=/opt/orders/.venv/bin/python /opt/orders/consumer.py
EnvironmentFile=/etc/orders/environment
Restart=on-failure
RestartSec=10
TimeoutStopSec=30
MemoryMax=1G
CPUQuota=80%

[Install]
WantedBy=multi-user.target
```

### Explanation

The actual values must be derived from workload behavior and environment requirements.

---

## Advanced 2 — Production Incident

### Question

The consumer is restarting continuously after a database credential change.

### Solution

Investigate:

```bash
systemctl status consumer.service
journalctl -u consumer.service --since "15 minutes ago"
```

Inspect the environment configuration and permissions.

Do not simply disable the restart policy.

### Explanation

The underlying configuration error is the real issue.

---

## Advanced 3 — Missed Batch

### Question

A daily extraction uses `Persistent=true`, but a server was offline for two days. What should the application do?

### Solution

The application should explicitly determine which data interval needs processing.

### Explanation

A single catch-up invocation is not automatically equivalent to processing each missed business interval.

---

## Advanced 4 — Resource Containment

### Question

Why would you set both restart behavior and memory limits?

### Solution

Restart behavior improves availability after failures; resource limits contain resource impact.

### Explanation

They solve different problems.

---

## Advanced 5 — Hardening

### Question

Why shouldn't you blindly apply `ProtectSystem`, `PrivateTmp`, and `NoNewPrivileges` to every service?

### Solution

They can break applications that legitimately require certain permissions, filesystem writes, or privilege behavior.

### Explanation

Security hardening must be tested against actual application requirements.

---

# 130. Interview Preparation

## What is systemd?

systemd is a Linux system and service manager used for process lifecycle management, startup, dependencies, timers, resource controls, and logging integration.

## What is a systemd unit?

A unit is a systemd-managed object defined by configuration.

## What is a service unit?

A `.service` unit defines how a process/service is run and supervised.

## What is a timer?

A `.timer` unit schedules or triggers another unit, commonly a service.

## Difference between start and enable?

`start` changes current runtime state; `enable` configures automatic activation.

## Why is daemon-reload needed?

It makes systemd reread changed unit definitions.

## What is ExecStart?

The command systemd starts for the service.

## Why specify WorkingDirectory?

It makes the process's working directory explicit and prevents surprises with relative paths.

## Why use User instead of root?

Least privilege.

## What is EnvironmentFile?

A unit directive that loads environment variables from a file.

## What is journalctl?

The command-line interface for querying the systemd journal.

## How do you inspect service logs?

```bash
journalctl -u service-name
```

## How do you follow service logs?

```bash
journalctl -u service-name -f
```

## How do you inspect a time window?

```bash
journalctl --since "..." --until "..."
```

## What does Restart=on-failure do?

It requests restart after unsuccessful service termination under the policy.

## Why RestartSec?

It delays restart attempts and reduces aggressive restart loops.

## What is start-limit protection?

A mechanism that prevents repeated rapid service starts from continuing indefinitely.

## What is graceful shutdown?

Giving the application an opportunity to clean up and exit safely before forced termination.

## What is SIGTERM?

A conventional request for graceful process termination.

## What is a oneshot service?

A service intended to run a command/job and then exit.

## What is Persistent=true?

A timer setting that enables catch-up behavior for a missed timer activation after the system becomes active again.

## What is OnCalendar?

A timer directive defining a calendar-based schedule.

## How do you validate a timer schedule?

```bash
systemd-analyze calendar "expression"
```

## Difference between After, Wants, and Requires?

```text
After
=
ordering

Wants
=
weaker dependency/activation relationship

Requires
=
stronger dependency relationship
```

## How do resource limits help?

They contain service resource consumption and reduce the chance that one process harms the entire host.

## When would you use tmux?

For interactive, human-operated, one-off long-running work.

## When would you use cron?

For simple scheduling where systemd lifecycle integration is unnecessary.

## When would you use an orchestrator?

For complex, distributed, multi-step workflows.

## How would you troubleshoot a crashing service?

Start with:

```bash
systemctl status
journalctl -u
```

narrow the time window, identify the original failure, fix it, then verify stable operation.

---

# 131. Final Knowledge Check

You should be able to demonstrate all of the following.

## Fundamentals

- [ ] Explain why systemd exists
- [ ] Explain what a unit is
- [ ] Explain service units
- [ ] Explain timer units
- [ ] Explain systemd as a server-local lifecycle manager

## systemctl

- [ ] Start a service
- [ ] Stop a service
- [ ] Restart a service
- [ ] Inspect status
- [ ] Enable a service
- [ ] Disable a service
- [ ] Explain `enable --now`
- [ ] Run `daemon-reload`

## Service configuration

- [ ] Write `[Unit]`
- [ ] Write `[Service]`
- [ ] Write `[Install]`
- [ ] Use `ExecStart`
- [ ] Use `WorkingDirectory`
- [ ] Use `User`
- [ ] Use `EnvironmentFile`
- [ ] Use explicit virtual-environment paths

## Journal

- [ ] Use `journalctl`
- [ ] Filter with `-u`
- [ ] Follow with `-f`
- [ ] Filter with `--since`
- [ ] Filter with `--until`
- [ ] Filter priorities
- [ ] Use output formats
- [ ] Reconstruct an incident timeline

## Restart and shutdown

- [ ] Configure `Restart=on-failure`
- [ ] Configure `RestartSec`
- [ ] Recognize restart loops
- [ ] Understand start-limit protection
- [ ] Explain SIGTERM
- [ ] Test graceful shutdown
- [ ] Understand stop timeout
- [ ] Understand forced termination

## Timers

- [ ] Create a timer
- [ ] Use `OnCalendar`
- [ ] Validate schedules
- [ ] Use `Persistent=true`
- [ ] Use `RandomizedDelaySec`
- [ ] Build a oneshot service
- [ ] Inspect `list-timers`
- [ ] Reason about missed runs
- [ ] Reason about overlapping jobs

## Dependencies

- [ ] Explain `After=`
- [ ] Explain `Wants=`
- [ ] Explain `Requires=`
- [ ] Use network ordering appropriately

## Resources and hardening

- [ ] Apply memory limits
- [ ] Apply CPU controls
- [ ] Understand limit-triggered failure
- [ ] Explain `NoNewPrivileges`
- [ ] Explain read-only system protection
- [ ] Explain `PrivateTmp`
- [ ] Test hardening rather than blindly applying it

## User services

- [ ] Understand `systemctl --user`
- [ ] Understand user service lifecycle
- [ ] Understand lingering/logout behavior

## Architecture

- [ ] Compare tmux and systemd
- [ ] Compare systemd and cron
- [ ] Compare systemd and orchestrators
- [ ] Know when systemd is the wrong abstraction

## Operations

- [ ] Diagnose a failed service
- [ ] Diagnose a restart loop
- [ ] Diagnose a failed timer
- [ ] Diagnose a missed timer
- [ ] Diagnose a resource-limit failure
- [ ] Diagnose a shutdown problem
- [ ] Write a service runbook
- [ ] Write a timer runbook

---

# 132. Topic 05 Checkpoint

You have completed Topic 05 when you can do all of the following on a disposable Linux server:

- [ ] Write and manage service and timer units.
- [ ] Configure restarts.
- [ ] Configure graceful stops.
- [ ] Configure resource limits.
- [ ] Use `Persistent=true`.
- [ ] Test calendar expressions.
- [ ] Read service logs efficiently with `journalctl`.
- [ ] Investigate a restart loop.
- [ ] Investigate a timer failure.
- [ ] Choose correctly between systemd, cron, and an orchestrator.

The checkpoint is not:

> "I have read the systemd documentation."

The checkpoint is:

> **"I can operate a service, break it, diagnose it from evidence, fix it, verify it, and explain why the system behaved that way."**

---

# 133. Final Production Decision Framework

When deciding whether to use systemd, ask:

```text
Is the workload server-local?
        |
        +-- yes
              |
              v
Does it need a managed process lifecycle?
        |
        +-- yes → systemd service
```

For scheduled work:

```text
Is the schedule simple and server-local?
        |
        +-- yes
              |
              v
systemd timer
```

For a simple legacy schedule:

```text
cron may be sufficient
```

For a complex workflow:

```text
multiple tasks
dependencies
retries
backfills
distributed execution
central visibility
        |
        v
orchestrator
```

---

# 134. Production Service Design Checklist

Before deploying:

- [ ] Dedicated service user considered
- [ ] `ExecStart` uses explicit paths
- [ ] Working directory exists
- [ ] Environment configuration exists
- [ ] Environment permissions are appropriate
- [ ] Application can handle SIGTERM
- [ ] Stop timeout is reasonable
- [ ] Restart policy is intentional
- [ ] Restart delay is intentional
- [ ] Start-limit behavior is understood
- [ ] Resource limits are evidence-based
- [ ] Dependencies are deliberate
- [ ] Hardening has been tested
- [ ] Logs are visible through journalctl
- [ ] Operator runbook exists

---

# 135. Production Timer Design Checklist

Before deploying:

- [ ] Service works when run independently
- [ ] Schedule validated with `systemd-analyze calendar`
- [ ] `OnCalendar` is correct
- [ ] `Persistent=true` decision is explicit
- [ ] Randomized delay considered
- [ ] Job is idempotent where practical
- [ ] Data interval semantics are explicit
- [ ] Overlap behavior is understood
- [ ] Output publication is safe
- [ ] Failure is visible in the journal
- [ ] Operator can inspect the next trigger
- [ ] Recovery procedure exists

---

# 136. Topic Boundaries

This module is intentionally focused.

Do not turn it into a complete course on:

- SSH fundamentals
- SSH tunnels
- tmux
- rsync
- rclone
- detailed CPU/memory diagnosis
- detailed disk/inode management
- jq
- csvkit
- Miller
- DuckDB
- logrotate
- full Linux user administration
- cloud infrastructure

Those topics belong elsewhere in G2.

Useful references:

```text
Topic 01
=
SSH and jump hosts

Topic 02
=
SSH tunnels

Topic 03
=
tmux

Topic 04
=
scp / rsync / rclone

Topic 06
=
server resource diagnosis

Topic 07
=
disk and inode management

Topic 08
=
command-line data tools

Topic 09
=
log investigation

Topic 10
=
users, sudo, packages, server hygiene
```

This module can reference those topics without duplicating them.

---

# 137. Final Mental Model

Memorize this:

```text
SERVICE
=
What should run?

TIMER
=
When should it run?

SYSTEMCTL
=
How do I operate it?

JOURNALCTL
=
What happened?

RESTART POLICY
=
What happens when it fails?

DEPENDENCIES
=
What must be available/order first?

RESOURCE LIMITS
=
How much can it consume?

USER
=
With whose permissions does it run?
```

And:

```text
tmux
=
Human interactive operations

systemd
=
Server-local machine-managed lifecycle

orchestrator
=
Distributed workflow management
```

---

# 138. Final Operational Principle

A production Data Engineer should not think:

> "How do I keep this Python script running?"

Instead think:

```text
What should run?
      ↓
Who should run it?
      ↓
Where should it run?
      ↓
How should it start?
      ↓
What dependencies must be available?
      ↓
What happens if it fails?
      ↓
How quickly should it restart?
      ↓
How do I prevent restart loops?
      ↓
How should it shut down?
      ↓
How much CPU/memory may it consume?
      ↓
When should it run?
      ↓
What if the server was offline?
      ↓
How do I inspect what happened?
      ↓
How do I recover?
      ↓
When does this belong in an orchestrator instead?
```

That is the production skill this module is designed to build.

---

# 139. Roadmap Coverage Audit

| Required Topic 05 capability | Covered |
|---|---:|
| What systemd is | Yes |
| Units | Yes |
| Relevant unit types | Yes |
| Service units | Yes |
| `systemctl` | Yes |
| `start` | Yes |
| `stop` | Yes |
| `restart` | Yes |
| `status` | Yes |
| `enable` | Yes |
| `disable` | Yes |
| `daemon-reload` | Yes |
| Service unit structure | Yes |
| `ExecStart` | Yes |
| `WorkingDirectory` | Yes |
| `User` | Yes |
| `EnvironmentFile` | Yes |
| `journalctl` | Yes |
| `journalctl -u` | Yes |
| `journalctl -f` | Yes |
| `--since` | Yes |
| `--until` | Yes |
| Priority filtering | Yes |
| Output formats | Yes |
| Restart behavior | Yes |
| `Restart=on-failure` | Yes |
| `RestartSec` | Yes |
| Start-limit protection | Yes |
| Graceful shutdown | Yes |
| SIGTERM | Yes |
| Stop timeout | Yes |
| Kill behavior | Yes |
| Timers | Yes |
| `OnCalendar` | Yes |
| `Persistent=true` | Yes |
| Randomized delay | Yes |
| `systemd-analyze calendar` | Yes |
| Oneshot services | Yes |
| Overlap considerations | Yes |
| `After=` | Yes |
| `Wants=` | Yes |
| `Requires=` | Yes |
| Resource limits | Yes |
| Memory limits | Yes |
| CPU limits | Yes |
| `NoNewPrivileges` | Yes |
| Read-only system paths | Yes |
| `PrivateTmp` | Yes |
| User services | Yes |
| Logout independence | Yes |
| systemd vs cron | Yes |
| systemd vs orchestrators | Yes |
| WSL2 practice | Yes |
| Hands-on exercises | Yes |
| Break/fix | Yes |
| Journal investigation | Yes |
| Timer investigation | Yes |
| Service troubleshooting | Yes |
| Data Engineering use cases | Yes |
| Checkpoint | Yes |
| Common mistakes | Yes |
| Runbooks | Yes |

---

# 140. Quality and Safety Audit

The completed module follows these principles:

- [x] Beginner → intermediate → advanced progression
- [x] Data Engineering examples
- [x] Explicit production boundaries
- [x] No real credentials
- [x] Disposable practice environment
- [x] Destructive service commands clearly contextualized
- [x] Evidence-first troubleshooting
- [x] Restart loops explicitly covered
- [x] Graceful shutdown explicitly covered
- [x] Missed-run semantics explicitly covered
- [x] Timer schedule validation included
- [x] Resource limits covered without duplicating Topic 06
- [x] Hardening covered at awareness level
- [x] User services covered at awareness/practical level
- [x] tmux/systemd/cron/orchestrator boundary is explicit
- [x] Labs are executable in a Linux practice environment
- [x] Break/fix scenarios use symptom → evidence → diagnosis → fix → verification
- [x] Final checkpoint included
- [x] Roadmap coverage audit included

---

# 141. Module Completion

You are ready to move to Topic 06 when you can confidently perform this workflow on a practice server:

```text
Write service
    ↓
Run service
    ↓
Inspect status
    ↓
Read journal
    ↓
Configure restart
    ↓
Test failure
    ↓
Diagnose restart behavior
    ↓
Implement graceful shutdown
    ↓
Create oneshot service
    ↓
Create timer
    ↓
Validate schedule
    ↓
Test Persistent behavior
    ↓
Apply resource controls
    ↓
Investigate a failure
    ↓
Write runbook
    ↓
Explain the architecture
```

The final outcome is not command memorization.

It is the ability to operate a Linux-hosted Data Engineering workload as a **reliable server-managed process**, while knowing when the problem has moved beyond systemd into the domain of a distributed workflow orchestrator.
