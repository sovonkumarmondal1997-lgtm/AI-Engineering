# tmux and Long-Running Sessions

> **Stage 2B — Gap Module G2: Linux and Shell for Data Servers**  
> **Topic 03 — tmux and Long-Running Sessions**  
> **Progression:** Beginner → Intermediate → Advanced → Production Data Engineering Operations

---

## 1. Module Purpose

A Data Engineer frequently runs work on a remote Linux server:

```text
Data Engineer
     |
     | SSH
     v
Remote Linux Server
     |
     v
Long-running Data Job
```

The job may take minutes or hours.

The problem is that the SSH connection is not the same thing as the long-running work.

Your laptop can:

- sleep;
- lose Wi-Fi;
- lose VPN connectivity;
- close the terminal;
- lose the SSH connection;
- restart.

A remote interactive job can therefore become difficult to observe or control.

This topic teaches `tmux`, a terminal multiplexer that allows a persistent terminal workspace to remain on the remote server while your SSH connection comes and goes.

The deeper production lesson is more important:

> **tmux is an interactive operational workspace, not a production scheduler or service manager.**

A strong Data Engineer knows both how to use tmux and when **not** to use it.

---

# 2. Learning Outcomes

By the end of this module you should be able to:

- explain why SSH disconnects can affect interactive jobs;
- distinguish a terminal, shell, process, session, and SSH connection;
- explain the `SIGHUP`/hang-up concept without oversimplifying it;
- explain why tmux exists;
- describe the tmux client/server architecture;
- create named tmux sessions;
- detach from sessions;
- list sessions;
- reattach to sessions;
- create and manage windows;
- create and navigate panes;
- use scrollback and copy mode;
- capture pane output;
- create a minimal `.tmux.conf`;
- understand the prefix key;
- use mouse support when useful;
- configure a reasonable history buffer;
- understand the status line;
- understand session sharing and its security implications;
- compare tmux with `nohup`, `setsid`, and GNU `screen`;
- distinguish interactive tmux work from systemd-managed services;
- distinguish tmux from production workflow orchestration;
- operate a long-running Data Engineering job through an SSH disconnect/reconnect cycle;
- troubleshoot missing sessions, stopped jobs, missing output, and stale sessions;
- identify recurring work that should become a service, timer, or orchestrated workflow.

---

# 3. Prerequisites and Scope

Topic 01 established remote SSH access.

Topic 02 established SSH tunneling and port forwarding.

This topic assumes you can already:

- SSH into a remote Linux server;
- understand SSH sessions at a basic level;
- run shell commands;
- understand processes and signals at a foundational level.

The focus here is **remote interactive job operations**.

## Practice environment

Use a safe practice Linux server or VM.

Do not test long-running-job behavior against production systems.

A suitable lab looks like:

```text
Laptop
   |
   | SSH
   v
Remote Linux Server
   |
   +------------------+
   |                  |
   v                  v
tmux session       System resources
   |
   +-- pipeline
   +-- logs
   +-- monitoring
```

---

# 4. Start With the Real Problem

## 4.1 The common Data Engineering situation

Suppose you start:

```bash
python pipeline.py
```

over SSH.

The architecture is:

```text
Laptop
   |
   | SSH
   v
Remote Server
   |
   v
Shell
   |
   v
python pipeline.py
```

The job may run for two hours.

Then:

```text
Laptop sleeps
     ↓
Wi-Fi disconnects
     ↓
SSH disconnects
```

What happens next?

The correct answer is **not**:

> "SSH always kills the process."

Process behavior depends on the relationship between the process, shell, terminal, session, signal handling, and how the program was launched.

That is why understanding the underlying model matters.

---

# 5. Terminal vs Shell vs Process vs Session

These concepts are related but are not interchangeable.

## 5.1 Terminal

A terminal provides an interface through which you interact with a shell.

Historically this was a physical terminal.

Today it is commonly a terminal emulator on your laptop.

Conceptually:

```text
Terminal
   |
   v
Shell
```

---

## 5.2 Shell

A shell such as Bash interprets commands:

```bash
python pipeline.py
```

The shell launches the requested process.

Conceptually:

```text
Terminal
   |
   v
Bash
   |
   v
Python process
```

---

## 5.3 Process

A process is a running program instance.

For example:

```text
python pipeline.py
```

creates a Python process.

The shell is also a process.

---

## 5.4 Session

A process can belong to a process/session hierarchy with relationships to controlling terminals and process groups.

For this topic, think of a session as an execution context that helps explain why terminal disconnects can affect interactive work.

---

## 5.5 SSH connection

SSH is a network connection between:

```text
Your machine
      |
      v
Remote SSH server
```

The SSH connection carries an interactive terminal session when you request one.

It is therefore important to distinguish:

```text
SSH connection
```

from:

```text
tmux session
```

They are not the same object.

---

# 6. Hang-Up and `SIGHUP`

When a controlling terminal disappears, the operating system and shell may use the hang-up signal:

```text
SIGHUP
```

The exact result depends on:

- process relationships;
- process groups;
- shell behavior;
- signal handling;
- whether the process has been detached;
- how the process was started.

Therefore, avoid the simplistic rule:

> "SSH disconnect always kills every process."

A better mental model is:

```text
SSH connection
      ↓
terminal
      ↓
shell
      ↓
process
```

When the terminal/session relationship disappears, processes connected to that environment may receive hang-up-related behavior.

The operational lesson is:

> **Do not rely on an interactive SSH shell remaining available for a job that matters.**

---

# 7. Why tmux Exists

tmux creates a persistent terminal environment on the remote server.

Without tmux:

```text
Laptop
  |
 SSH
  |
Server
  |
Shell
  |
Job
```

If the SSH connection disappears, the interactive environment may also disappear or behave differently from what you expected.

With tmux:

```text
Laptop
  |
 SSH
  |
Server
  |
tmux server
  |
tmux session
  |
Shell / job
```

If SSH disconnects:

```text
SSH disconnect
      ↓
tmux continues
      ↓
Reconnect later
      ↓
Attach again
```

The key point is:

> **The tmux session lives on the remote server, not on your laptop.**

---

# 8. tmux Architecture

The useful conceptual components are:

```text
tmux client
tmux server
session
window
pane
shell/process
```

A practical mental model:

```text
tmux server
   |
   +-- Session: pipeline-run
   |      |
   |      +-- Window: main
   |      |      |
   |      |      +-- Pane 1: pipeline
   |      |      +-- Pane 2: logs
   |      |      +-- Pane 3: monitoring
   |      |
   |      +-- Window: debugging
   |
   +-- Session: investigation
```

## Components

### tmux server

The persistent server-side tmux process manages sessions.

### tmux client

The client connects your current terminal to the tmux server/session.

### Session

A persistent workspace containing windows.

### Window

A terminal workspace within a session.

### Pane

A subdivision of a window containing its own terminal.

### Shell/process

The commands and programs running inside panes.

---

# 9. Create a tmux Session

Start tmux:

```bash
tmux
```

Or explicitly create a session:

```bash
tmux new
```

Prefer named sessions for operational work:

```bash
tmux new -s pipeline
```

Now you have:

```text
tmux session: pipeline
```

## Why names matter

A server may contain:

```text
pipeline
backfill
incident
debugging
migration
```

A meaningful name tells you what a session is for.

---

# 10. Session Naming Discipline

Good names:

```text
pipeline
orders-backfill
customer-replay
spark-debug
migration
incident-2026-10-06
data-quality-check
```

Poor names:

```text
session1
test
new
foo
```

The goal is not to create a complicated naming standard.

The goal is:

> **Identify the purpose of a session at a glance.**

---

# 11. Detaching From a Session

The default tmux prefix is:

```text
Ctrl-b
```

To detach:

```text
Ctrl-b d
```

Break it down:

```text
Ctrl-b = tmux prefix
d      = detach
```

Detaching means:

> Leave the tmux session running while disconnecting your current terminal from it.

It does **not** mean:

> Stop the job.

The model is:

```text
Attach
  ↓
Detach
  ↓
tmux session continues
  ↓
Job continues
```

---

# 12. Listing Sessions

Use:

```bash
tmux ls
```

or:

```bash
tmux list-sessions
```

Example conceptual output:

```text
pipeline: 1 windows
backfill: 2 windows
incident: 3 windows
```

This lets you determine what already exists before creating duplicate sessions.

---

# 13. Reattaching to a Session

Attach to the most relevant session:

```bash
tmux attach -t pipeline
```

A common shorthand is:

```bash
tmux a -t pipeline
```

The full operational pattern is:

```text
SSH disconnect
     ↓
Reconnect
     ↓
tmux ls
     ↓
tmux attach -t pipeline
```

This is the central hands-on workflow of Topic 03.

---

# 14. The Core Long-Running Job Pattern

For an interactive long-running job:

```bash
ssh data-server
```

Then:

```bash
tmux new -s pipeline
```

Start the job:

```bash
python pipeline.py
```

Detach:

```text
Ctrl-b d
```

The session remains on the remote server.

Later:

```bash
ssh data-server
```

Then:

```bash
tmux ls
```

Reattach:

```bash
tmux attach -t pipeline
```

---

# 15. tmux Windows

A window is a full terminal workspace inside a tmux session.

Mental model:

```text
Session
  |
  +-- Window 0
  +-- Window 1
  +-- Window 2
```

Create a new window:

```text
Ctrl-b c
```

Next window:

```text
Ctrl-b n
```

Previous window:

```text
Ctrl-b p
```

## Practical Data Engineering layout

```text
Session: pipeline

Window 0 → pipeline
Window 1 → logs
Window 2 → monitoring
Window 3 → debugging
```

This keeps related operational work together without requiring many independent SSH connections.

---

# 16. Naming Windows

A useful operational workspace can have descriptive window names.

For example:

```text
pipeline
logs
monitoring
debugging
```

The exact command/key binding can vary with configuration, but the principle is simple:

> A window name should communicate its purpose.

Avoid turning window naming into an elaborate framework.

---

# 17. tmux Panes

A pane splits one window into multiple terminals.

Example:

```text
+----------------------+
| Pipeline              |
|                      |
+----------+-----------+
| Logs     | Monitor   |
|          |           |
+----------+-----------+
```

Common default bindings:

Vertical split:

```text
Ctrl-b %
```

Horizontal split:

```text
Ctrl-b "
```

The precise orientation depends on tmux terminology and version/configuration, so verify the result visually rather than relying on memory.

---

# 18. Pane Navigation

tmux allows you to move between panes without opening another SSH session.

This is useful when operating a pipeline:

```text
+-------------------------------+
| Pipeline                      |
| python pipeline.py            |
+----------------+--------------+
| Logs            | Monitoring |
| tail -f ...     | vmstat 2   |
+----------------+--------------+
```

The operator can inspect one pane, move to another, and return without losing the overall workspace.

---

# 19. Multi-Pane Data Engineering Workflow

Create a practical session:

```text
Session: pipeline
```

Use:

```text
Window 0: pipeline
    Pane 1 → run job
    Pane 2 → inspect logs

Window 1: monitoring
    Pane 1 → system observation
    Pane 2 → disk/memory checks

Window 2: debugging
    Pane 1 → database client
    Pane 2 → investigation commands
```

For example:

```text
Pane 1:
python pipeline.py

Pane 2:
tail -f application.log

Pane 3:
vmstat 2
```

This is one of tmux's strongest Data Engineering use cases:

> **A persistent interactive operational workspace.**

---

# 20. Scrollback and History

Long-running jobs can produce thousands of lines.

The terminal's visible screen is only a small window into that output.

tmux maintains a history buffer for pane output.

This allows you to inspect earlier output without rerunning the job.

For example:

```text
Current output
      ↑
      |
500 lines earlier
      |
Error message
```

This is useful when a long-running data job reports a failure that occurred several minutes earlier.

---

# 21. Copy Mode

tmux copy mode lets you inspect and navigate pane history.

The exact default bindings depend on whether the environment is using the standard emacs-style or vi-style mode, but the operational workflow is:

```text
Enter copy mode
      ↓
Scroll
      ↓
Search / locate text
      ↓
Select/copy if needed
      ↓
Exit copy mode
```

A common default entry is:

```text
Ctrl-b [
```

Once inside copy mode, use the configured movement/search keys.

## Why copy mode matters

Imagine a Spark or Python pipeline printed:

```text
...
INFO step 410
INFO step 411
ERROR connection timeout
...
```

and the error is now hundreds of lines above the current screen.

Copy mode lets you inspect the existing evidence rather than immediately rerunning the job.

---

# 22. Scrollback Is Not Application Logging

tmux history is useful, but it is not a replacement for durable application logs.

Think:

```text
tmux history
    =
terminal output buffer
```

versus:

```text
application logs
    =
durable operational record
```

Application logging should remain the authoritative mechanism for production observability.

tmux is an operator workspace.

---

# 23. Capturing Pane Output

tmux can capture pane content.

Basic command:

```bash
tmux capture-pane
```

To print captured output:

```bash
tmux capture-pane -p
```

You can redirect captured output where appropriate:

```bash
tmux capture-pane -p > pane-output.txt
```

This can be useful for:

- incident evidence;
- troubleshooting;
- sharing a relevant terminal excerpt;
- recording a diagnostic snapshot.

## Important limitation

Pane capture only captures what exists within the relevant pane's history.

It does not create a complete audit record of everything that happened on the server.

---

# 24. Capturing Evidence During an Incident

Suppose:

```text
pipeline
   |
   v
error appears
```

Before restarting the job:

```bash
tmux capture-pane -p > incident-pane-output.txt
```

Then inspect the evidence.

The operational philosophy is:

```text
Observe
   ↓
Capture evidence
   ↓
Diagnose
   ↓
Fix
```

rather than:

```text
Error
   ↓
Restart immediately
```

---

# 25. Minimal tmux Configuration

tmux reads configuration from:

```text
~/.tmux.conf
```

Do not treat this file as a theme-customization project.

For Data Engineering operations, a small configuration is usually enough.

Useful settings include:

- prefix;
- mouse support;
- history size;
- status line behavior.

---

# 26. Prefix Key

The default prefix is:

```text
Ctrl-b
```

The prefix tells tmux:

> The next key is a tmux command rather than normal terminal input.

For example:

```text
Ctrl-b d
```

means:

```text
prefix
+
detach
```

A user can change the prefix, but the important learning objective is understanding the prefix mechanism rather than memorizing someone else's configuration.

---

# 27. Mouse Support

A minimal configuration can enable:

```tmux
set -g mouse on
```

Mouse support can provide:

- pane selection;
- window selection;
- scrolling;
- pane resizing.

Keyboard-driven operation remains important on remote servers, especially when working through restricted environments.

Mouse support is useful, not mandatory.

---

# 28. History Size

A practical example:

```tmux
set -g history-limit 10000
```

This controls how much pane history tmux retains.

Why it matters:

```text
Too little history
    ↓
Useful incident output disappears
```

But extremely large history is not automatically better.

It consumes additional resources and can create unnecessary overhead.

Choose a reasonable value for the environment and workload.

---

# 29. Status Line

The tmux status line can provide useful context such as:

- session name;
- window name;
- active window;
- time;
- selected context.

For operational work, the status line should help answer:

```text
Which session am I in?
Which window am I viewing?
```

Do not turn this topic into a visual theme/customization tutorial.

---

# 30. Safe Minimal `.tmux.conf`

A small example:

```tmux
set -g mouse on
set -g history-limit 10000
set -g status-interval 5
```

This is intentionally small.

The objective is to understand configuration, not to copy a giant configuration file from the Internet.

## Configuration discipline

After changing configuration:

1. make one small change;
2. reload/test it;
3. confirm behavior;
4. keep the configuration understandable.

Avoid accumulating settings you cannot explain.

---

# 31. Reloading Configuration

Depending on the environment, you can reload the configuration from inside tmux.

A common command is:

```text
Ctrl-b :
```

Then:

```text
source-file ~/.tmux.conf
```

Or from a shell:

```bash
tmux source-file ~/.tmux.conf
```

Afterward, test the specific change.

---

# 32. Session Sharing

Multiple users can sometimes interact with the same tmux session when the operating-system permissions and tmux socket/session permissions allow it.

Potential use cases:

- pair debugging;
- incident response;
- teaching;
- live troubleshooting.

Conceptually:

```text
Engineer A
     \
      \
       +--> shared tmux session
      /
     /
Engineer B
```

This can be extremely useful.

It can also be extremely powerful.

---

# 33. Session-Sharing Security

A shared tmux session can expose:

- commands;
- database queries;
- environment variables;
- file paths;
- tokens;
- passwords;
- customer information;
- operational secrets;
- shell access.

Another participant may be able to execute commands, not merely observe the screen.

Therefore:

> **Do not share a tmux session merely because it is convenient.**

Before sharing, verify:

```text
Who is the other user?
What operating-system access do they have?
What can they see?
What can they execute?
What secrets might appear?
```

---

# 34. Secrets and Terminal Visibility

Be careful with commands such as:

```bash
some-command --password='secret'
```

A secret may appear in:

- the visible terminal;
- tmux history;
- shell history;
- process listings;
- captured pane output;
- incident recordings.

Prefer appropriate secret-management mechanisms.

The lesson is broader than tmux:

> **A terminal is an observable operational surface.**

---

# 35. Long-Running Data Job — Complete Exercise

A practical synthetic job might be:

```bash
python pipeline.py
```

or:

```bash
python extract_orders.py
```

Start a named session:

```bash
tmux new -s pipeline
```

Start the job:

```bash
python pipeline.py
```

Now detach:

```text
Ctrl-b d
```

The job should continue inside the tmux session.

Disconnect SSH.

Wait.

Reconnect:

```bash
ssh data-server
```

List sessions:

```bash
tmux ls
```

Reattach:

```bash
tmux attach -t pipeline
```

Inspect:

- current output;
- job progress;
- errors;
- completion state.

Then capture useful output:

```bash
tmux capture-pane -p > pipeline-pane-output.txt
```

Finally clean up the session if it is no longer needed.

---

# 36. Why the Disconnect Test Matters

Do not merely read:

> "tmux survives SSH disconnects."

Test it.

The experiment is:

```text
Start job
   ↓
Detach tmux
   ↓
Close SSH
   ↓
Wait
   ↓
Reconnect
   ↓
Attach tmux
   ↓
Observe job
```

This converts a theoretical statement into operational knowledge.

---

# 37. Simulating an SSH Disconnect

A controlled exercise:

### Step 1

SSH to the practice server.

```bash
ssh data-server
```

### Step 2

Create the session.

```bash
tmux new -s pipeline
```

### Step 3

Start a synthetic long-running command.

For example:

```bash
for i in $(seq 1 120); do
    printf '%s progress=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$i"
    sleep 5
done
```

### Step 4

Detach:

```text
Ctrl-b d
```

### Step 5

Close SSH.

### Step 6

Wait.

### Step 7

Reconnect:

```bash
ssh data-server
```

### Step 8

List sessions:

```bash
tmux ls
```

### Step 9

Reattach:

```bash
tmux attach -t pipeline
```

### Step 10

Inspect the output.

The goal is to verify that the tmux workspace persisted independently of your laptop's SSH connection.

---

# 38. Three-Pane Operational Workflow

A practical layout:

```text
+--------------------------------+
|                                |
|        Data Pipeline           |
|                                |
+----------------+---------------+
|                |               |
|     Logs       |   Monitoring  |
|                |               |
+----------------+---------------+
```

Example:

```text
Pane 1:
python pipeline.py

Pane 2:
tail -f application.log

Pane 3:
vmstat 2
```

You can replace the monitoring command with an appropriate tool available on the practice server.

The point is not the exact command.

The point is:

```text
Work
+
Evidence
+
System observation
```

in one persistent workspace.

---

# 39. Long-Running Data Engineering Use Cases

tmux is useful for **interactive, operator-driven** tasks such as:

## Backfills

```text
orders-backfill
```

A one-time historical data correction may run for hours.

## Large exports

```text
customer-export
```

A manually initiated export can be observed interactively.

## One-time migrations

```text
warehouse-migration
```

An operator may need to observe progress and intervene.

## Reprocessing

```text
failed-partitions
```

A Data Engineer may rerun selected partitions.

## Manual recovery scripts

A recovery command may require interactive observation.

## Data validation

```text
data-quality-check
```

A one-off validation job can run while the operator watches output.

## Incident debugging

```text
incident-2026-10-06
```

A persistent workspace can hold investigation commands, logs, and monitoring.

---

# 40. tmux Is Not a Production Scheduler

This is one of the most important lessons in Topic 03.

Do not turn:

```text
tmux
```

into:

```text
production scheduler
```

Bad architecture:

```text
Production pipeline
       |
       v
Engineer SSH session
       |
       v
tmux
```

Why is this bad?

Because the workflow depends on a human-managed interactive workspace.

Problems include:

- human dependency;
- weak observability;
- poor scheduling semantics;
- weak restart policy;
- no dependency management;
- difficult alerting;
- forgotten sessions;
- unclear ownership;
- poor reproducibility.

---

# 41. When tmux Is the Right Tool

Good examples:

```text
One-time 4-hour backfill
        ↓
tmux
```

```text
Interactive production investigation
        ↓
tmux
```

```text
One-off migration with operator supervision
        ↓
tmux
```

```text
Manual recovery procedure
        ↓
tmux
```

The common characteristic is:

> **A human is actively operating the work.**

---

# 42. When tmux Is the Wrong Tool

Bad examples:

```text
Always-running consumer
        ↓
tmux
```

Better:

```text
Always-running consumer
        ↓
systemd service
```

Bad:

```text
Hourly extraction
        ↓
tmux
```

Better:

```text
Hourly extraction
        ↓
systemd timer
```

Bad:

```text
Multi-step production DAG
        ↓
tmux
```

Better:

```text
Production DAG
        ↓
orchestrator
```

---

# 43. tmux vs systemd

The architectural distinction is:

```text
tmux
=
human-operated interactive workspace
```

versus:

```text
systemd
=
service/process supervision
```

Examples:

| Workload | Appropriate Tool |
|---|---|
| One-time interactive backfill | tmux |
| One-time supervised migration | tmux |
| Always-running consumer | systemd service |
| Long-running server process | systemd service |
| Scheduled server-side batch | systemd timer |
| Complex dependency graph | Orchestrator |

Topic 05 covers systemd in depth.

This topic only establishes the judgment needed to know when to move beyond tmux.

---

# 44. tmux vs Orchestrators

Production Data Engineering workflows may belong in:

- Airflow;
- Dagster;
- another workflow orchestrator;
- a managed workflow platform.

The core distinction:

```text
tmux
=
human-operated interactive workspace
```

```text
orchestrator
=
machine-managed workflow
```

An orchestrator provides capabilities such as:

- scheduling;
- dependencies;
- retries;
- state tracking;
- operational visibility;
- alerting;
- ownership;
- repeatability.

tmux is not designed to replace those capabilities.

---

# 45. `nohup`

A simpler way to detach a process from an interactive terminal is:

```bash
nohup python pipeline.py > pipeline.log 2>&1 &
```

This pattern combines:

```text
nohup
+
output redirection
+
background execution
```

## What `nohup` is for

`nohup` helps a command continue running when the terminal's hang-up would otherwise affect it.

It is useful for simple unattended commands.

## Limitations

Compared with tmux, `nohup` does not provide:

- a persistent interactive workspace;
- windows;
- panes;
- interactive reattachment;
- a rich operational session.

Think:

```text
nohup
=
simple process detachment
```

while:

```text
tmux
=
persistent interactive terminal workspace
```

---

# 46. `setsid`

`setsid` can start a program in a new session.

Example:

```bash
setsid command
```

The conceptual purpose is to alter the process/session relationship so the command is less tied to the current terminal/session.

The important learning objective is understanding that `setsid` is a process/session-management primitive.

It is not a replacement for tmux's interactive workspace.

---

# 47. GNU `screen`

GNU `screen` is another terminal multiplexer.

It solves a similar operational problem:

```text
SSH disconnect
       ↓
persistent remote terminal session
       ↓
reattach later
```

You may encounter `screen` on older servers or in organizations with established historical workflows.

The important distinction for this roadmap is:

```text
screen
=
another terminal multiplexer
```

rather than a reason to learn two full terminal-multiplexer ecosystems.

---

# 48. tmux vs nohup vs screen vs systemd vs Orchestrator

| Tool | Best For | Interactive? | Survives SSH Disconnect? | Scheduling? | Production Service Management? |
|---|---|---:|---:|---:|---:|
| **tmux** | Interactive operator work | Yes | Yes | No | No |
| **nohup** | Simple detached command | Limited | Often, depending on setup | No | No |
| **setsid** | Process/session detachment | No workspace | Can separate session relationship | No | No |
| **screen** | Persistent terminal workspace | Yes | Yes | No | No |
| **systemd** | Services and server timers | No interactive workspace | Yes | Timers | Yes |
| **orchestrator** | Production workflows | No | Yes | Yes | Workflow management |

The goal is not to memorize the table.

The goal is to answer:

> **What operational problem am I actually trying to solve?**

---

# 49. Recording Commands and Session Activity

The roadmap requires awareness of recording operational activity.

Possible mechanisms include:

- shell history;
- timestamped shell history;
- tmux pane capture;
- terminal/session recording;
- centralized audit mechanisms.

These can help during:

- incidents;
- production debugging;
- knowledge transfer;
- postmortems.

But recording introduces risk.

A recording can capture:

- passwords;
- tokens;
- customer information;
- sensitive commands;
- private data.

Therefore:

> **Do not enable session recording blindly.**

Understand the organization's privacy, security, and audit requirements first.

---

# 50. History Timestamps

Timestamped command history can help answer:

```text
What happened first?
```

during an incident.

A useful concept is:

```text
command A
10:31:02

command B
10:31:17

command C
10:32:05
```

This is valuable for reconstructing an operator timeline.

## Important distinction

Shell history timestamps are not the same as complete audit logging.

History can be:

- disabled;
- modified;
- incomplete;
- affected by shell configuration;
- missing commands executed through other mechanisms.

Treat it as one evidence source, not an authoritative audit system.

---

# 51. Incident Response Workflow

Scenario:

> A long-running data backfill appears to have stopped progressing.

Do not immediately restart it.

First:

```text
Reconnect
   ↓
Find tmux session
   ↓
Reattach
   ↓
Inspect job
   ↓
Inspect logs
   ↓
Observe resources
   ↓
Determine actual state
   ↓
Decide what to do
```

Useful actions may include:

```bash
tmux ls
```

then:

```bash
tmux attach -t orders-backfill
```

Then inspect:

- current output;
- application logs;
- process state;
- resource behavior;
- recent errors.

The principle is:

> **Observe first. Restart only after understanding the state.**

---

# 52. Session Hygiene

Good operational discipline includes:

- name sessions;
- close unused sessions;
- avoid dozens of abandoned sessions;
- know what each session does;
- document important sessions;
- avoid running production services manually;
- protect sensitive output;
- periodically inspect sessions.

List sessions:

```bash
tmux ls
```

A healthy operator should be able to explain why each important session exists.

---

# 53. Safe Session Termination

tmux provides commands such as:

```bash
tmux kill-session
```

and:

```bash
tmux kill-server
```

Understand the difference.

## Kill one session

```text
tmux kill-session
```

Terminates a selected tmux session.

## Kill the server

```text
tmux kill-server
```

Can terminate all sessions managed by that tmux server.

Treat the latter as destructive.

Never run it casually on a shared or important environment.

---

# 54. Troubleshooting: "My tmux Session Disappeared"

Start with:

```bash
tmux ls
```

Possible causes include:

- tmux server stopped;
- server rebooted;
- session was explicitly terminated;
- you are using a different user;
- the session belonged to a different environment.

Do not assume the job failed until you inspect evidence.

---

# 55. Troubleshooting: "My Job Stopped"

First determine whether tmux itself is still present:

```bash
tmux ls
```

Then inspect the session.

Determine:

- did the process exit normally?
- did it fail?
- was it killed?
- did the host reboot?
- did the process run out of resources?
- did the application terminate itself?

A tmux session can survive while the process inside it has already exited.

Therefore:

```text
tmux session exists
≠
job is running
```

---

# 56. Troubleshooting: "I Reattached but Output Is Missing"

Check:

- tmux history limit;
- pane history;
- whether output was redirected;
- application logs;
- whether the job already completed.

If history is too small:

```tmux
set -g history-limit 10000
```

can increase the buffer for future work.

But do not assume missing tmux output means the job never produced output.

---

# 57. Troubleshooting: "There Are Too Many Sessions"

Run:

```bash
tmux ls
```

Then identify:

```text
Which sessions are active?
Which are stale?
Which are important?
Which can be closed?
```

Session hygiene is part of operational correctness.

---

# 58. Troubleshooting: "I Started a Production Pipeline in tmux"

Do not simply answer:

> "Keep the tmux session alive."

Instead ask:

```text
Is this recurring?
Is it production-critical?
Does it need retries?
Does it need scheduling?
Does it need monitoring?
Does it need alerting?
Does it need restart policy?
Does it have dependencies?
```

If yes, move the workload toward:

```text
systemd
or
production orchestrator
```

depending on the workload.

The architectural correction matters more than preserving the tmux session.

---

# 59. Break/Fix Exercise 1 — Start Outside tmux

### Objective

Understand the problem tmux is intended to solve.

### Setup

SSH to a practice server:

```bash
ssh data-server
```

Run a synthetic long-running command directly:

```bash
for i in $(seq 1 120); do
    printf '%s progress=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$i"
    sleep 5
done
```

Disconnect SSH during execution.

### Symptom

The process may stop or behave differently from the expected persistent-job model.

### Evidence

Reconnect and inspect:

```bash
ps aux
```

### Diagnosis

The job was tied to an interactive environment without a persistent terminal multiplexer.

### Prevention

For interactive long-running work:

```text
tmux
```

or use an appropriate noninteractive process/service mechanism.

---

# 60. Break/Fix Exercise 2 — Start Inside tmux

### Objective

Compare behavior.

Create:

```bash
tmux new -s pipeline
```

Run the same synthetic job.

Detach:

```text
Ctrl-b d
```

Disconnect SSH.

Reconnect:

```bash
ssh data-server
```

List:

```bash
tmux ls
```

Attach:

```bash
tmux attach -t pipeline
```

### Expected lesson

The tmux workspace remains available independently of the SSH connection.

---

# 61. Break/Fix Exercise 3 — Unnamed Session Confusion

Create several sessions:

```bash
tmux new
```

and additional sessions.

Then:

```bash
tmux ls
```

### Symptom

You cannot easily determine which session is which.

### Diagnosis

The sessions were not named.

### Fix

Adopt meaningful names for operational sessions.

### Prevention

Create sessions with:

```bash
tmux new -s purpose
```

---

# 62. Break/Fix Exercise 4 — Forgotten Background Work

Suppose you have several sessions:

```bash
tmux ls
```

Some are weeks old.

### Task

Determine:

- which sessions are still needed;
- which contain active work;
- which are stale.

### Key lesson

A persistent session is useful only if someone knows why it exists.

---

# 63. Break/Fix Exercise 5 — Capture Incident Output

During a failure:

```bash
tmux capture-pane -p > incident-pane-output.txt
```

Inspect the file.

### Diagnosis

The captured output can preserve useful terminal evidence.

### Security check

Confirm the capture does not contain:

- passwords;
- tokens;
- private data.

---

# 64. Break/Fix Exercise 6 — Too Little History

Configure an intentionally small history limit in a practice environment.

Generate lots of output.

Observe that older lines disappear.

### Diagnosis

The pane history buffer is finite.

### Fix

Use a reasonable history limit:

```tmux
set -g history-limit 10000
```

### Prevention

Use application logs for durable records.

---

# 65. Break/Fix Exercise 7 — Shared Sensitive Session

Imagine a session contains:

```text
database credentials
API tokens
customer data
```

A second engineer requests access.

### Diagnosis

Sharing the session could expose sensitive information and shell capabilities.

### Correct response

Do not share automatically.

Use an appropriate, authorized collaboration/access mechanism and sanitize sensitive material.

---

# 66. Break/Fix Exercise 8 — Recurring Production Job in tmux

Suppose a team says:

> "Every night an engineer starts the extraction in tmux."

Evaluate:

```text
Scheduling
Retries
Monitoring
Alerting
Ownership
Restart policy
Dependencies
Auditability
```

### Diagnosis

This is a production automation problem.

### Architectural correction

Move the workload toward:

```text
systemd timer/service
```

or:

```text
orchestrator
```

as appropriate.

---

# 67. Troubleshooting Decision Tree

```text
Long-running job appears broken
            |
            v
     Is tmux session present?
            |
        +---+---+
        |       |
       NO      YES
        |       |
        v       v
Check server,  Reattach
user, reboot   and inspect
                  |
                  v
          Is process still running?
                  |
              +---+---+
              |       |
             NO      YES
              |       |
              v       v
       Inspect exit,  Inspect logs,
       error, signal  resources, state
              |       |
              +---+---+
                  |
                  v
           Understand state
                  |
                  v
             Decide action
```

The key principle is:

```text
Evidence first
```

---

# 68. Production Decision Framework

When deciding whether to use tmux, ask:

| Question | If Yes | Likely Direction |
|---|---|---|
| Is a human actively supervising the task? | Yes | tmux may fit |
| Is it a one-time operation? | Yes | tmux may fit |
| Must it run every hour/day? | Yes | systemd timer/orchestrator |
| Must it restart automatically? | Yes | systemd/orchestrator |
| Is it always running? | Yes | systemd service/orchestrator |
| Does it need dependency management? | Yes | Orchestrator |
| Does it need formal alerting? | Yes | Service/orchestrator |
| Is it production-critical? | Yes | Avoid human-dependent tmux operation |
| Does it need reproducible scheduling? | Yes | Automation/orchestration |

---

# 69. Data Engineering Architecture Examples

## One-time backfill

```text
Engineer
   |
   v
SSH
   |
   v
tmux
   |
   v
backfill
```

Appropriate when the engineer actively supervises the operation.

---

## Always-running consumer

```text
Consumer
   |
   v
systemd service
```

Not:

```text
Consumer
   |
   v
tmux
```

---

## Scheduled extraction

```text
Scheduler
   |
   v
Extraction
```

For a server-local simple schedule:

```text
systemd timer
```

For complex workflows:

```text
orchestrator
```

---

## Multi-step production pipeline

```text
Orchestrator
    |
    +-- extract
    |
    +-- validate
    |
    +-- transform
    |
    +-- load
    |
    +-- notify
```

tmux is not the workflow engine.

---

# 70. Hands-On End-to-End Lab

## Objective

Operate a long-running interactive Data Engineering job through an SSH disconnect/reconnect cycle while using a multi-pane tmux workspace.

## Architecture

```text
Laptop
   |
   | SSH
   v
Remote Linux Server
   |
   +--------------------------+
   |                          |
   v                          v
tmux session              System resources
   |
   +-- pipeline
   +-- logs
   +-- monitoring
```

## Prerequisites

You need:

- a practice Linux server;
- SSH access;
- tmux installed;
- Bash or another compatible shell;
- a safe synthetic long-running job.

## Step 1 — Connect

```bash
ssh data-server
```

## Step 2 — Create session

```bash
tmux new -s pipeline
```

## Step 3 — Create windows

Use:

```text
Ctrl-b c
```

Create a workflow such as:

```text
Window 0 → pipeline
Window 1 → logs
Window 2 → monitoring
```

## Step 4 — Create panes

Split the pipeline window.

Run the long-running job in one pane.

Use another for observation.

## Step 5 — Start synthetic job

```bash
for i in $(seq 1 120); do
    printf '%s progress=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$i"
    sleep 5
done
```

## Step 6 — Observe

Use the other panes for:

```text
logs
system observation
```

## Step 7 — Detach

```text
Ctrl-b d
```

## Step 8 — Disconnect SSH

Close the SSH connection.

## Step 9 — Wait

Allow the job to continue for a while.

## Step 10 — Reconnect

```bash
ssh data-server
```

## Step 11 — List sessions

```bash
tmux ls
```

## Step 12 — Reattach

```bash
tmux attach -t pipeline
```

## Step 13 — Inspect

Determine:

- current progress;
- whether the job is still running;
- whether it encountered errors;
- what output exists.

## Step 14 — Capture output

```bash
tmux capture-pane -p > pipeline-pane-output.txt
```

## Step 15 — Finish

Allow the job to complete.

## Step 16 — Clean up

Close the session when it is no longer required.

## Step 17 — Architecture judgment

Answer:

> Should this remain a tmux workflow?

Explain why or why not.

---

# 71. Lab Verification Checklist

After the end-to-end lab, verify:

- [ ] Session was named.
- [ ] Job was started inside tmux.
- [ ] Session was detached.
- [ ] SSH connection was closed.
- [ ] SSH was re-established.
- [ ] Session was found with `tmux ls`.
- [ ] Session was reattached.
- [ ] Job state was inspected.
- [ ] Output was captured.
- [ ] Session was cleaned up.
- [ ] You can explain why tmux survived the SSH disconnect.
- [ ] You can explain whether the workload belongs in tmux permanently.

---

# 72. Topic-Specific Practice Questions

These questions reinforce Topic 03 without replacing the broader G2 practice set.

## Basic

### 1. What problem does tmux solve?

**Expected Thinking**

Separate:

```text
SSH connection
```

from:

```text
persistent terminal workspace
```

**Solution**

tmux provides a persistent terminal workspace on the remote server so an operator can disconnect and later reconnect to the same interactive session.

**Explanation**

The tmux session is server-side.

---

### 2. What does `Ctrl-b d` do?

**Expected Thinking**

Think:

```text
prefix + detach
```

**Solution**

It detaches the current terminal from the tmux session without terminating the session.

---

### 3. How do you list sessions?

**Solution**

```bash
tmux ls
```

or:

```bash
tmux list-sessions
```

---

### 4. How do you create a named session?

**Solution**

```bash
tmux new -s pipeline
```

---

### 5. How do you reattach?

**Solution**

```bash
tmux attach -t pipeline
```

---

## Moderate

### 6. What is the difference between a tmux session and an SSH connection?

**Solution**

An SSH connection is a network connection to the remote server. A tmux session is a persistent terminal environment managed by tmux on that remote server.

---

### 7. Why is a named session better than an unnamed session?

**Solution**

It makes the purpose identifiable and reduces operational confusion when multiple sessions exist.

---

### 8. What is a tmux window?

**Solution**

A window is a full terminal workspace inside a tmux session.

---

### 9. What is a pane?

**Solution**

A pane is a terminal subdivision within a tmux window.

---

### 10. Why is tmux history not a replacement for application logs?

**Solution**

tmux history is a finite terminal-output buffer. Application logs are designed to provide durable operational records.

---

## Advanced

### 11. Explain `SIGHUP` without saying "SSH kills jobs."

**Solution**

When a controlling terminal disappears, a hang-up signal and related session behavior can affect processes associated with that terminal/session. Exact behavior depends on process relationships, signal handling, shell behavior, and how the process was launched.

---

### 12. A tmux session exists but the job is not running. What does that prove?

**Solution**

It proves the tmux workspace still exists. It does not prove that the process inside the workspace is alive.

---

### 13. Why can a background tmux session become operational debt?

**Solution**

Sessions can accumulate, become stale, contain sensitive information, confuse operators, and hide the fact that a workload should have been automated.

---

### 14. Why is `tmux kill-server` dangerous?

**Solution**

It can terminate all sessions managed by that tmux server, potentially disrupting multiple interactive jobs.

---

### 15. Why is a recurring production pipeline a poor fit for tmux?

**Solution**

It needs machine-managed scheduling, retries, monitoring, ownership, alerting, and restart behavior rather than dependence on a human-managed terminal workspace.

---

## Troubleshooting

### 16. `tmux ls` shows no session, but you expected one. What do you investigate?

**Solution**

Check:

- correct user;
- correct server;
- whether the tmux server stopped;
- whether the server rebooted;
- whether the session was terminated.

---

### 17. You reattach and see no recent output. What do you investigate?

**Solution**

Check:

- whether the job is still running;
- pane history size;
- output redirection;
- application logs;
- whether the job completed.

---

### 18. A session contains sensitive credentials. Should you share it?

**Solution**

No, not casually. Sharing can expose the credentials and provide shell-level access to another user.

---

### 19. A team starts a nightly extraction in tmux. What should you recommend?

**Solution**

Move the recurring workload into appropriate automation, such as a systemd timer/service or production orchestrator.

---

### 20. A long-running backfill is actively supervised by an engineer. Is tmux necessarily wrong?

**Solution**

No. A one-time, interactive, operator-supervised backfill can be a good tmux use case.

---

## Architecture

### 21. When should you prefer tmux over `nohup`?

**Solution**

When you need an interactive persistent terminal workspace, multiple panes/windows, observation, and later reattachment.

---

### 22. When might `nohup` be enough?

**Solution**

For a simple unattended command where you mainly need the process to continue independently of the interactive terminal and do not need a persistent interactive workspace.

---

### 23. Why might an older server use GNU `screen`?

**Solution**

`screen` is an established terminal multiplexer and may be part of an organization's historical operational practices.

---

### 24. When is systemd a better choice than tmux?

**Solution**

For services that should run independently of a human terminal and for scheduled server-side jobs using systemd timers.

---

### 25. When is an orchestrator a better choice?

**Solution**

For complex production workflows involving scheduling, dependencies, retries, state tracking, alerting, and multi-step execution.

---

## Security

### 26. What security risk does session sharing introduce?

**Solution**

Another participant may see commands and sensitive output and may have the ability to execute commands in the shared shell.

---

### 27. Why can pane capture be sensitive?

**Solution**

Captured output can contain passwords, tokens, customer data, internal endpoints, or other sensitive information.

---

### 28. Why should terminal recording be controlled?

**Solution**

Recording can create valuable audit/incident evidence but can also capture secrets and sensitive data.

---

### 29. Is shell history a complete audit record?

**Solution**

No. It may be incomplete or altered and does not capture every possible execution path.

---

### 30. What is the most important production judgment in Topic 03?

**Solution**

Know when tmux is an appropriate interactive operator tool and when the workload belongs in systemd or a production orchestrator.

---

# 73. Interview Preparation

## Q1. What problem does tmux solve?

**Answer**

It provides a persistent terminal workspace on a remote server so interactive work can continue independently of an individual SSH connection.

---

## Q2. What can happen when an SSH session disconnects?

**Answer**

The terminal and shell relationship can disappear, and processes associated with that environment may receive hang-up-related behavior. Exact outcomes depend on process/session relationships and signal handling.

---

## Q3. What is `SIGHUP`?

**Answer**

`SIGHUP` is the hang-up signal traditionally associated with a terminal/session becoming unavailable. Its effects depend on how processes and shells are structured and how they handle the signal.

---

## Q4. What is a tmux session?

**Answer**

A persistent terminal workspace managed by a tmux server on the remote machine.

---

## Q5. What is a tmux window?

**Answer**

A full terminal workspace inside a tmux session.

---

## Q6. What is a tmux pane?

**Answer**

A terminal subdivision inside a tmux window.

---

## Q7. How do you detach?

**Answer**

Using the default binding:

```text
Ctrl-b d
```

---

## Q8. How do you list sessions?

**Answer**

```bash
tmux ls
```

---

## Q9. How do you reattach?

**Answer**

```bash
tmux attach -t pipeline
```

---

## Q10. Why name sessions?

**Answer**

Meaningful names improve operational visibility and reduce confusion when multiple long-running tasks exist.

---

## Q11. How do you capture pane output?

**Answer**

```bash
tmux capture-pane -p
```

It can then be redirected to a file if appropriate.

---

## Q12. What is copy mode?

**Answer**

A tmux mode for navigating and inspecting pane history, including scrolling, searching, and selecting text.

---

## Q13. Why configure history size?

**Answer**

To retain enough terminal output for investigation without unnecessarily consuming resources.

---

## Q14. What are tmux security concerns?

**Answer**

Shared sessions and terminal output can expose credentials, tokens, customer data, commands, and shell access. Sessions should not be shared casually.

---

## Q15. tmux vs `nohup`?

**Answer**

tmux provides an interactive persistent workspace. `nohup` is a simpler mechanism for allowing a command to continue independently of a terminal hang-up.

---

## Q16. tmux vs `screen`?

**Answer**

Both are terminal multiplexers that support persistent interactive sessions. tmux is the primary tool taught here, while screen is included as awareness because it remains common on existing systems.

---

## Q17. tmux vs systemd?

**Answer**

tmux is human-operated interactive work. systemd is designed for service/process supervision and timers.

---

## Q18. tmux vs Airflow or another orchestrator?

**Answer**

tmux is a manual terminal workspace. An orchestrator is a machine-managed workflow system with scheduling, dependencies, retries, state, monitoring, and operational control.

---

## Q19. When should you not use tmux?

**Answer**

Do not use it as the permanent execution mechanism for production-critical services, recurring scheduled workloads, or complex workflows.

---

## Q20. How would you operate a long-running backfill safely?

**Answer**

Use a named tmux session for a one-time interactive backfill, observe progress and logs, detach safely, reconnect and reattach if needed, capture evidence during failures, verify final state, and clean up afterward. If the workload becomes recurring or operationally critical, move it into proper automation.

---

# 74. Production Safety Rules

Follow these rules:

- never use tmux as an excuse to avoid production automation;
- do not run production services manually in tmux;
- name sessions clearly;
- clean up abandoned sessions;
- protect sensitive information;
- do not paste secrets into visible terminals unnecessarily;
- do not share sessions casually;
- use proper application logging;
- verify job state before restarting;
- document manual operational work;
- move recurring work into proper automation.

A good tmux workflow is:

```text
Intentional
    ↓
Named
    ↓
Observable
    ↓
Documented
    ↓
Temporary
```

---

# 75. Topic Boundaries

This file is Topic 03.

Do not deeply teach:

- SSH key management;
- SSH config;
- SSH tunneling;
- rsync/rclone;
- systemd implementation;
- server resource monitoring;
- disk/inode management;
- jq/csvkit/Miller/DuckDB;
- log rotation;
- full Linux user management.

Those topics belong to other G2 modules.

Examples:

```text
Topic 01 → SSH access and identity
Topic 02 → SSH tunnels
Topic 04 → file transfer
Topic 05 → systemd
Topic 06 → resource monitoring
Topic 07 → disk management
Topic 08 → CLI data tools
Topic 09 → logs
Topic 10 → server hygiene
```

You may reference them for context.

For example:

> Use systemd for recurring server-side jobs; Topic 05 covers systemd in depth.

Do not duplicate those curricula here.

---

# 76. G2 Operational Learning Loop

Use the G2 operational philosophy:

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
Write the runbook entry
  ↓
Explain aloud
```

For Topic 03, the runbook entry should capture:

```text
Symptom
Commands
Evidence
Cause
Fix
Verification
```

This is more valuable than simply memorizing tmux shortcuts.

---

# 77. Three-Minute Operator Reference

## Create a session

```bash
tmux new -s pipeline
```

## List sessions

```bash
tmux ls
```

## Attach

```bash
tmux attach -t pipeline
```

## Detach

```text
Ctrl-b d
```

## New window

```text
Ctrl-b c
```

## Next window

```text
Ctrl-b n
```

## Previous window

```text
Ctrl-b p
```

## Split pane

```text
Ctrl-b %
```

or:

```text
Ctrl-b "
```

## Copy mode

```text
Ctrl-b [
```

## Capture pane

```bash
tmux capture-pane -p
```

## Capture to file

```bash
tmux capture-pane -p > pane-output.txt
```

## Kill a session

```bash
tmux kill-session -t pipeline
```

## Inspect sessions

```bash
tmux ls
```

---

# 78. 3 a.m. Operational Runbook

## Create a tmux session

```bash
tmux new -s pipeline
```

## Name it

Use a purpose-driven name:

```text
pipeline
orders-backfill
migration
incident-2026-10-06
```

## Start the long-running job

```bash
python pipeline.py
```

## Detach

```text
Ctrl-b d
```

## Reconnect later

```bash
ssh data-server
```

## List sessions

```bash
tmux ls
```

## Reattach

```bash
tmux attach -t pipeline
```

## Inspect output

Use the current pane and copy mode.

## Capture output

```bash
tmux capture-pane -p > incident-pane-output.txt
```

## Determine job state

Do not assume:

```text
tmux session exists
```

means:

```text
job exists
```

Inspect the actual process/application state.

## Safely terminate a session

Only after confirming the session is no longer required:

```bash
tmux kill-session -t pipeline
```

## Decide whether tmux remains appropriate

Ask:

```text
Is this one-time?
Is a human supervising it?
Is it interactive?
Does it need scheduling?
Does it need retries?
Does it need automatic restart?
Is it production-critical?
```

If the answer points toward automation:

```text
systemd
or
orchestrator
```

---

# 79. Final Knowledge Check

You should be able to demonstrate all of the following.

## SSH and process behavior

- [ ] Explain why SSH disconnects can affect interactive jobs.
- [ ] Explain terminal, shell, process, and session relationships.
- [ ] Explain `SIGHUP` conceptually.
- [ ] Avoid the false rule that "SSH disconnect always kills every process."

## tmux fundamentals

- [ ] Explain why tmux exists.
- [ ] Explain the tmux server/client model.
- [ ] Create a named session.
- [ ] Detach.
- [ ] List sessions.
- [ ] Reattach.

## Workspace management

- [ ] Create windows.
- [ ] Navigate windows.
- [ ] Create panes.
- [ ] Navigate panes.
- [ ] Use scrollback.
- [ ] Use copy mode.
- [ ] Capture pane output.

## Configuration

- [ ] Explain the tmux prefix.
- [ ] Understand mouse support.
- [ ] Configure a reasonable history limit.
- [ ] Understand the status line.
- [ ] Maintain a minimal `.tmux.conf`.

## Security

- [ ] Explain session-sharing risks.
- [ ] Protect secrets in terminal sessions.
- [ ] Understand the limitations of shell history.
- [ ] Understand recording risks.

## Alternatives

- [ ] Compare tmux with `nohup`.
- [ ] Compare tmux with `setsid`.
- [ ] Explain GNU `screen`.
- [ ] Explain when systemd is more appropriate.
- [ ] Explain when an orchestrator is more appropriate.

## Data Engineering operations

- [ ] Run a long-running interactive data job inside tmux.
- [ ] Survive an SSH disconnect/reconnect cycle.
- [ ] Use a multi-pane workflow.
- [ ] Capture evidence.
- [ ] Troubleshoot a missing or stopped job.
- [ ] Identify a workload that should become a systemd service/timer or orchestrated workflow.

---

# 80. Topic 03 Checkpoint

You have mastered Topic 03 when you can do this without blindly copying commands:

```text
SSH to server
      ↓
Create named tmux session
      ↓
Create useful windows/panes
      ↓
Start long-running interactive job
      ↓
Detach
      ↓
Disconnect SSH
      ↓
Reconnect
      ↓
Find session
      ↓
Reattach
      ↓
Inspect job
      ↓
Capture evidence
      ↓
Diagnose failures
      ↓
Complete/clean up
      ↓
Decide whether tmux should remain
```

More importantly, you should be able to explain:

```text
tmux
=
persistent interactive operator workspace
```

not:

```text
tmux
=
production scheduler
```

That distinction is the production-level skill this topic is designed to establish.

---

# 81. Roadmap Coverage Audit

The Topic 03 specification requires:

| Required Concept | Covered |
|---|---:|
| SSH disconnect impact | Yes |
| Hang-up behavior | Yes |
| `SIGHUP` concept | Yes |
| tmux fundamentals | Yes |
| Creating sessions | Yes |
| Naming sessions | Yes |
| Detaching | Yes |
| Listing sessions | Yes |
| Reattaching | Yes |
| Windows | Yes |
| Panes | Yes |
| Scrollback | Yes |
| Copy mode | Yes |
| Capturing/saving pane output | Yes |
| Minimal configuration | Yes |
| Prefix key | Yes |
| Mouse support | Yes |
| History size | Yes |
| Status line | Yes |
| Session sharing | Yes |
| Shared-session security | Yes |
| `nohup` | Yes |
| `setsid` | Yes |
| GNU `screen` | Yes |
| tmux vs systemd | Yes |
| tmux vs orchestrator | Yes |
| When tmux is wrong | Yes |
| Recurring jobs → automation | Yes |
| Recording/session activity awareness | Yes |
| History timestamps | Yes |
| Long-running data-job exercise | Yes |
| Multi-pane workflow | Yes |
| Identify jobs for systemd/orchestration | Yes |
| Common operational mistakes | Yes |
| Troubleshooting | Yes |
| Session hygiene | Yes |
| Production boundaries | Yes |
| Topic checkpoint | Yes |

---

# 82. Final File Quality Audit

- [x] Beginner → intermediate → advanced → production progression.
- [x] Data Engineering framing throughout.
- [x] SSH disconnect problem explained before tmux commands.
- [x] Terminal/session/process distinction explained.
- [x] `SIGHUP` explained without oversimplification.
- [x] tmux server/client/session/window/pane model explained.
- [x] Named sessions demonstrated.
- [x] Detach/list/attach workflow demonstrated.
- [x] Windows and panes explained.
- [x] Scrollback and copy mode included.
- [x] Pane capture included.
- [x] Minimal `.tmux.conf` included.
- [x] Prefix, mouse, history, and status line covered.
- [x] Session sharing and security risks covered.
- [x] `nohup`, `setsid`, and `screen` compared.
- [x] systemd/orchestrator boundary made explicit.
- [x] Long-running Data Engineering exercise included.
- [x] SSH disconnect/reconnect exercise included.
- [x] Multi-pane workflow included.
- [x] Break/fix scenarios included.
- [x] Troubleshooting decision tree included.
- [x] Incident-response reasoning included.
- [x] Session hygiene included.
- [x] Recording/history timestamp awareness included.
- [x] Practice questions included.
- [x] Interview questions and answers included.
- [x] Final knowledge check included.
- [x] Operational runbook included.
- [x] Roadmap coverage audit included.
- [x] Later G2 topics are not duplicated as full curricula.
- [x] No real credentials or production infrastructure required.
- [x] Destructive commands are explained before use.
- [x] Production judgment is emphasized.

---

# 83. Final Takeaway

The most important mental model in this topic is:

```text
SSH connection
      |
      v
Remote Linux server
      |
      v
tmux server
      |
      v
tmux session
      |
      +-- windows
      |     |
      |     +-- panes
      |
      +-- interactive jobs
```

Your SSH connection can disappear:

```text
SSH disconnect
      ↓
tmux remains
      ↓
job/workspace remains available
      ↓
SSH reconnect
      ↓
tmux attach
```

But tmux should not become a substitute for production automation.

Use:

```text
tmux
```

for:

```text
interactive
+
temporary
+
operator-supervised
```

work.

Use:

```text
systemd
```

for appropriate:

```text
services
+
server-side timers
+
process supervision
```

and use:

```text
orchestrators
```

for:

```text
scheduled
+
multi-step
+
dependency-aware
+
retryable
+
production workflows
```

The strongest Data Engineer is not the person who knows the most tmux shortcuts.

It is the person who can answer:

> **"What operational problem am I solving, what execution model does this workload require, and is tmux actually the correct tool?"**

That is the production judgment this topic is designed to develop.
