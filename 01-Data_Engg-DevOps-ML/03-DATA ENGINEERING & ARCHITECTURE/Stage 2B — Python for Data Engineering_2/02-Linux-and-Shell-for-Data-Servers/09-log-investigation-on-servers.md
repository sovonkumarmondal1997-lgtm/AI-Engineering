# Log Investigation on Servers

> **Stage 2B — Linux and Shell for Data Servers**  
> **Topic 09 — Log Investigation on Servers**  
> **Phase C — Diagnosing Servers**

## Learning Objective

By the end of this module, you should be able to investigate a production Data Engineering failure on a Linux server by finding the right logs, narrowing the incident window, searching current and rotated logs, analyzing structured JSON logs, correlating application/system/kernel/database evidence, reconstructing the incident timeline, preserving evidence, and documenting the resolution.

The central skill is **evidence-based investigation**.

A production Data Engineer does not simply search for the word `ERROR`. A production Data Engineer reconstructs what happened.

---

# 1. Why Log Investigation Matters

A production pipeline is a chain of components:

```text
API / source
    ↓
ingestion service
    ↓
queue / stream
    ↓
transformer
    ↓
database / warehouse
    ↓
downstream consumer
```

When something fails, the visible symptom may appear far away from the original cause.

For example:

```text
Database latency increases
        ↓
consumer requests time out
        ↓
consumer retries
        ↓
backlog grows
        ↓
memory usage grows
        ↓
OOM killer terminates process
        ↓
systemd restarts service
```

If you look only at the final application error, you may incorrectly conclude that the application caused the incident.

The logs are evidence distributed across multiple layers:

```text
Application logs
      +
systemd journal
      +
kernel logs
      +
database logs
      +
resource observations
      ↓
incident timeline
```

## What This Module Teaches

You will learn to:

- find application and system logs;
- follow logs during a live incident;
- navigate large logs efficiently;
- understand log rotation;
- search rotated and compressed logs;
- investigate exact time windows;
- normalize timestamps and time zones;
- work with structured JSON/JSONL logs;
- use `jq` to filter and summarize log events;
- count and group errors;
- trace a `run_id` across services;
- correlate application, database, systemd, and kernel evidence;
- investigate OOM events;
- understand journal disk usage and retention;
- preserve evidence before changing production state;
- write an incident-investigation runbook.

## Prerequisites

This module assumes you already know:

- basic shell navigation;
- files and directories;
- `grep`, `sort`, `uniq`, `cut`;
- pipes and redirection;
- permissions;
- processes and signals;
- basic SSH;
- systemd service basics;
- `journalctl` fundamentals;
- server resource monitoring;
- disk/inode concepts;
- `jq`, csvkit, Miller, and DuckDB CLI fundamentals.

Those subjects are refreshed only where they directly support log investigation.

---

# 2. The Core Mental Model

Think of a server incident as a distributed evidence problem.

```text
                    INCIDENT
                       |
        +--------------+--------------+
        |              |              |
   Application      Systemd         Kernel
      logs          journal          logs
        |              |              |
        +--------------+--------------+
                       |
                    Database
                       |
                       v
                 Correlated timeline
                       |
                       v
              Root cause hypothesis
                       |
                       v
                Verified conclusion
```

A useful investigation asks five questions first:

```text
WHEN?
WHERE?
WHAT SERVICE?
WHAT IDENTIFIER?
WHAT EVIDENCE?
```

More concretely:

1. **When** did the incident start and end?
2. **Where** is the relevant service running?
3. **What service** is affected?
4. **What identifier** can connect events — `run_id`, request ID, job ID, PID, order ID?
5. **What evidence** supports the conclusion?

The goal is not to collect every line.

The goal is to collect the **smallest sufficient set of evidence** that explains the incident.

---

# 3. Where Logs Live

Linux services do not all log in the same place.

A practical mental model is:

```text
Application
    ↓
application log file

systemd service
    ↓
systemd journal

Linux kernel
    ↓
kernel/system logs

Database
    ↓
database-specific logs

Incident
    ↓
correlate all evidence
```

## 3.1 Application Log Files

A Python service might write:

```text
/var/log/myapp/app.log
```

A Data Engineering application might instead use:

```text
/var/log/orders-consumer/orders.log
```

Or it may emit JSON Lines:

```text
/var/log/orders-consumer/app.jsonl
```

The actual path is application-specific.

Do not assume every service writes to `/var/log`.

Some applications write to:

- stdout/stderr;
- a systemd journal;
- a dedicated application directory;
- a logging agent;
- a container runtime;
- a database-managed location.

## 3.2 `/var/log`

`/var/log` is a conventional location for file-based system and application logs.

Examples you may encounter include:

```text
/var/log/syslog
/var/log/messages
/var/log/auth.log
/var/log/kern.log
/var/log/nginx/
```

Exact files vary by distribution and configuration.

The important lesson is:

> `/var/log` is a location convention, not a guarantee that all logs are there.

## 3.3 systemd Journal

A systemd-managed service may log directly to the journal.

For example:

```bash
journalctl -u orders-consumer.service
```

This is often preferable to hunting for a file when the service is configured for journal-based logging.

Follow the service live:

```bash
journalctl -u orders-consumer.service -f
```

## 3.4 Kernel Logs

Kernel events provide evidence that application logs may never contain.

Examples include:

- OOM kills;
- device problems;
- filesystem events;
- networking problems;
- kernel warnings.

Useful commands:

```bash
journalctl -k
```

and, where appropriate:

```bash
dmesg
```

On many modern systemd systems, the journal is the more convenient source for kernel evidence.

## 3.5 Database Logs

Databases may have their own logging configuration.

Examples of evidence include:

- slow queries;
- connection exhaustion;
- authentication failures;
- transaction failures;
- lock contention;
- replication problems.

A database timeout in an application log should often trigger the question:

> What was the database doing at the same time?

## 3.6 Why Different Services Use Different Mechanisms

Logging is an application and platform design choice.

For example:

```text
Python service → JSONL file
systemd service → journal
PostgreSQL → database log
reverse proxy → access log
kernel → journal
container → stdout/stderr
```

Therefore, a production investigation must identify the actual evidence source rather than assuming one universal log file exists.

---

# 4. Historical Investigation vs Live Monitoring

There are two different activities.

## Historical Investigation

You are investigating something that already happened.

Example:

```text
Incident:
14:32–14:47 UTC yesterday
```

You should narrow the evidence to that time window.

## Live Monitoring

The failure is happening now.

You may want to watch new events as they arrive:

```bash
tail -f /var/log/myapp/app.log
```

or:

```bash
journalctl -u orders-consumer.service -f
```

These activities complement each other.

```text
Historical
    ↓
What happened?

Live
    ↓
What is happening now?
```

Do not blindly follow a huge file when the incident occurred six hours ago. Define the historical window first.

---

# 5. Reading and Following Logs

## 5.1 `tail`

See the most recent lines:

```bash
tail -n 100 /var/log/myapp/app.log
```

This is a useful first look because you usually want recent context before switching to live following.

## 5.2 `tail -f`

Follow new lines as they are appended:

```bash
tail -f /var/log/myapp/app.log
```

This is useful when:

- a service is currently failing;
- you are reproducing a problem;
- you are validating recovery;
- you need to see what happens after a configuration change.

Stop following with:

```text
Ctrl+C
```

## 5.3 Follow With Context

A common pattern is:

```bash
tail -n 100 -f /var/log/myapp/app.log
```

This first displays recent context and then continues following new lines.

## 5.4 `less +F`

`less` has a follow mode:

```bash
less +F /var/log/myapp/app.log
```

Press:

```text
Ctrl+C
```

to stop following and return to normal `less` navigation.

This is useful because you can switch between:

```text
live following
        ↕
historical navigation
```

within the same tool.

## 5.5 `journalctl -f`

For a systemd service:

```bash
journalctl -u orders-consumer.service -f
```

This follows new journal events for that service.

A useful operational sequence is:

```bash
systemctl status orders-consumer.service
journalctl -u orders-consumer.service --since "15 minutes ago"
journalctl -u orders-consumer.service -f
```

First understand the service state, then inspect recent evidence, then follow it live if necessary.

## 5.6 Avoid Following Enormous Files Blindly

This is risky:

```bash
tail -f /var/log/everything.log
```

if the file contains unrelated high-volume traffic.

Prefer:

```bash
tail -n 200 /var/log/myapp/app.log
```

or a service-filtered journal:

```bash
journalctl -u orders-consumer.service -f
```

The principle is:

> Narrow the evidence before increasing the amount of evidence you consume.

---

# 6. Paging and Searching Logs With `less`

Large logs are datasets.

You should not routinely open multi-gigabyte logs in a graphical editor.

## 6.1 Basic Usage

```bash
less /var/log/myapp/app.log
```

Useful keys:

| Key | Meaning |
|---|---|
| `/pattern` | Search forward |
| `n` | Next match |
| `N` | Previous match |
| `G` | Go to end |
| `g` | Go to beginning |
| `q` | Quit |

Example:

```text
/ERROR
```

Then:

```text
n
```

to move to the next occurrence.

Search useful signals:

```text
ERROR
WARN
OOM
timeout
connection
failed
retry
```

## 6.2 Why `less` Is Useful

`less` is designed for viewing large text without requiring a GUI editor to load the entire file into an interactive editing session.

It supports:

- paging;
- search;
- navigation;
- partial reading;
- follow mode.

For server-side investigation, that is exactly what you need.

## 6.3 Search Context, Not Just the Matching Line

Finding:

```text
ERROR database timeout
```

does not prove that the database timeout is the root cause.

Inspect nearby events.

You may discover:

```text
14:32:01 connection pool exhausted
14:32:02 database timeout
14:32:03 retry scheduled
14:32:04 backlog increased
```

The surrounding context often tells a more useful story than the matching line alone.

---

# 7. Log Rotation

Log rotation is one of the most important operational concepts in log investigation.

Without rotation:

```text
app.log
   ↓
grows
   ↓
grows
   ↓
grows
   ↓
disk fills
   ↓
pipeline fails
```

Logs are data, and data consumes storage.

## 7.1 Why Rotate Logs?

Rotation prevents one log file from growing forever.

A common lifecycle is:

```text
app.log
app.log.1
app.log.2.gz
app.log.3.gz
...
```

Conceptually:

```text
current
  ↓
recent rotated
  ↓
older compressed
```

## 7.2 Rotation Policies

A rotation policy can be based on:

- time;
- size;
- both time and size.

Common schedules include:

```text
daily
weekly
```

Retention may be expressed as:

```text
rotate 14
```

meaning retain a configured number of rotated generations.

Compression reduces storage use:

```text
app.log.2.gz
```

## 7.3 Why Delayed Compression Exists

A common policy is:

```text
app.log
app.log.1
app.log.2.gz
```

The newest rotated file may remain uncompressed for a period before compression.

This is what `delaycompress` is designed to support.

---

# 8. `logrotate` Configuration

A realistic configuration might look like:

```text
/var/log/myapp/app.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

## 8.1 Directive-by-Directive Explanation

### `daily`

Attempt rotation daily.

It does not necessarily mean every invocation must rotate the file; other conditions and state matter.

### `rotate 14`

Keep 14 rotated generations.

### `compress`

Compress older rotated logs.

### `delaycompress`

Delay compression of the most recently rotated file until a subsequent rotation.

### `missingok`

Do not treat a missing log file as a fatal rotation error.

### `notifempty`

Do not rotate an empty log.

### `copytruncate`

Copy the existing file to the rotated destination and then truncate the original file.

This can be useful for applications that keep the original file descriptor open, but it has trade-offs discussed below.

## 8.2 Size-Based Rotation

A policy may also include a size threshold, for example:

```text
size 100M
```

The exact combination of time and size rules should be understood rather than copied mechanically.

The operational question is:

> What happens if this service becomes extremely noisy between scheduled rotations?

---

# 9. New-File Rotation vs `copytruncate`

This distinction matters during real investigations.

## 9.1 Approach A — Create a New File

Conceptually:

```text
old file
    ↓
rename
    ↓
new file created
    ↓
application writes to new file
```

The application must be able to reopen or otherwise use the new file appropriately.

This approach can be cleaner when the application supports log reopening.

## 9.2 Approach B — `copytruncate`

Conceptually:

```text
existing app.log
      ↓
copy contents
      ↓
rotated file
      ↓
truncate original app.log
      ↓
same open file descriptor remains associated with original file
```

The application may continue writing through an already-open descriptor.

## 9.3 Why File Descriptors Matter

A process does not simply write to a filename.

It opens a file and obtains a file descriptor.

Conceptually:

```text
application process
       |
       v
file descriptor
       |
       v
inode / file
```

The filename and the open file object are related, but they are not identical concepts.

Therefore:

> "The file was renamed" does not automatically mean "the application is now writing to the new filename."

## 9.4 Why `copytruncate` Has Trade-Offs

During copy-and-truncate, there can be a window in which log data changes while copying occurs.

That means:

- very busy logs can be difficult to capture perfectly;
- some writes can race with the copy;
- the approach can have a small loss/duplication risk depending on application behavior and timing.

For high-value production logging, an application-aware reopen strategy is often preferable when supported.

## 9.5 Investigation Implication

If a rotation happened and the expected current log looks strangely quiet, investigate:

- which file the process has open;
- whether rotation used rename/create or `copytruncate`;
- whether the service reopened the log;
- whether logs went to the journal instead;
- whether a rotated file contains the missing events.

A useful command when investigating open files is:

```bash
lsof -p <PID>
```

or, where appropriate:

```bash
lsof | grep '/var/log/myapp'
```

Use this carefully on large systems because broad `lsof` output can be substantial.

---

# 10. Searching Rotated and Compressed Logs

A common production mistake is searching only:

```text
app.log
```

when the incident happened yesterday.

The relevant evidence may be:

```text
app.log.1
app.log.2.gz
```

## 10.1 `zgrep`

Search compressed text directly:

```bash
zgrep "ERROR" /var/log/myapp/*.gz
```

More realistic:

```bash
zgrep -Ei "error|failed|timeout" /var/log/myapp/*.gz
```

## 10.2 `zcat`

Stream decompressed content:

```bash
zcat /var/log/myapp/app.log.2.gz
```

Pipe it into another command:

```bash
zcat /var/log/myapp/app.log.2.gz | grep "timeout"
```

Or inspect with `less`:

```bash
zcat /var/log/myapp/app.log.2.gz | less
```

## 10.3 Search Current + Rotated + Compressed

For text logs:

```bash
grep -Ei "error|failed|timeout" /var/log/myapp/app.log /var/log/myapp/app.log.1
zgrep -Ei "error|failed|timeout" /var/log/myapp/*.gz
```

Do not assume a single glob captures every naming convention. Inspect the directory first:

```bash
ls -lh /var/log/myapp/
```

## 10.4 Search by Correlation Identifier

If you have:

```text
run_id=abc123
```

search for it:

```bash
grep -R "run_id=abc123" /var/log/myapp/
```

For compressed files:

```bash
zgrep -H "run_id=abc123" /var/log/myapp/*.gz
```

If logs are JSONL, prefer `jq` for field-aware filtering.

---

# 11. Time-Window Investigation

The single most effective way to reduce log noise is to define the incident window.

Suppose:

```text
incident started: 14:32 UTC
incident ended:   14:47 UTC
```

Do not begin by searching millions of lines across an entire day.

Start with:

```text
START TIME
END TIME
SERVICE
RUN ID
ERROR SIGNAL
```

## 11.1 systemd Journal Time Window

```bash
journalctl \
  --since "2026-10-06 14:32:00" \
  --until "2026-10-06 14:47:00"
```

For a service:

```bash
journalctl -u orders-consumer.service \
  --since "2026-10-06 14:32:00" \
  --until "2026-10-06 14:47:00"
```

The structure is:

```text
journalctl
    ↓
-u
    ↓
specific service
    ↓
--since
    ↓
start boundary
    ↓
--until
    ↓
end boundary
```

## 11.2 Relative Time Windows

During a live investigation:

```bash
journalctl -u orders-consumer.service --since "1 hour ago"
```

or:

```bash
journalctl -k --since "30 minutes ago"
```

Relative windows are convenient, but incident records should eventually be normalized to explicit timestamps.

## 11.3 Plain Text Logs

Plain text logs do not automatically provide a universal time-range query interface.

You may need to combine:

```bash
grep
awk
sed
head
tail
```

with knowledge of the timestamp format.

For example, if lines begin with an ISO timestamp:

```text
2026-10-06T14:32:10Z ...
```

you can first narrow by date and then refine the time range using a format-aware script or `awk`.

The exact command depends on the log format.

Do not copy a timestamp filter without verifying the actual timestamp layout.

---

# 12. Time Zones and UTC

Time zones can destroy an otherwise correct investigation.

Consider:

```text
Application:
2026-10-06T14:35:22Z

Database:
2026-10-06 20:05:22 IST

Operator laptop:
20:05 local time
```

These can represent the same instant.

The `Z` suffix means UTC.

India Standard Time is UTC+05:30.

Therefore:

```text
14:35:22 UTC
+
05:30
=
20:05:22 IST
```

## 12.1 The Production Rule

Before building an incident timeline:

> Know what timezone every timestamp represents.

## 12.2 Why Mixed Time Zones Cause False Timelines

Suppose an operator writes:

```text
20:05 database timeout
20:06 application error
```

while the application's `20:06` was actually UTC.

You could accidentally construct a completely false sequence.

## 12.3 Normalize First

A robust investigation uses a normalized timeline:

```text
UTC
14:35:22 database event
14:35:23 application timeout
14:35:24 retry
14:35:30 memory pressure
```

Then retain the original timestamp and source timezone where needed.

## 12.4 Production Data Servers

Production data systems commonly use UTC to reduce ambiguity across:

- regions;
- servers;
- databases;
- cloud services;
- operators;
- scheduled jobs.

This module focuses on reasoning about timestamps. Topic 10 covers broader server hygiene and UTC operational policy.

---

# 13. Structured JSON Logs

Traditional text logging might look like:

```text
2026-10-06 14:32:10 ERROR failed to process order 123
```

A structured event can look like:

```json
{
  "timestamp": "2026-10-06T14:32:10Z",
  "level": "ERROR",
  "service": "orders-consumer",
  "run_id": "abc123",
  "order_id": "123",
  "message": "failed to process order"
}
```

The second representation gives each important attribute its own field.

## 13.1 Why Structured Logs Matter

Structured logs are easier to:

- filter;
- group;
- correlate;
- aggregate;
- search;
- ship to centralized platforms;
- analyze programmatically.

Instead of searching text for:

```text
abc123
```

you can ask:

```text
run_id == abc123
```

Instead of parsing a message to discover the level, you have:

```json
"level": "ERROR"
```

## 13.2 Useful Data Engineering Fields

A production Data Engineering log may include:

```text
timestamp
level
service
environment
run_id
request_id
job_id
component
dataset
partition
attempt
pid
message
error_type
duration_ms
```

Do not add every possible field indiscriminately. Log fields should support diagnosis and correlation.

---

# 14. JSON Lines / JSONL

A particularly useful server-log format is JSON Lines:

```text
{"timestamp":"2026-10-06T14:32:10Z","level":"INFO","run_id":"abc123","message":"started"}
{"timestamp":"2026-10-06T14:32:11Z","level":"ERROR","run_id":"abc123","message":"database timeout"}
{"timestamp":"2026-10-06T14:32:12Z","level":"INFO","run_id":"abc123","message":"retry scheduled"}
```

Each line is an independent JSON object.

That makes JSONL convenient for:

- streaming;
- line-oriented command-line tools;
- `jq`;
- log shippers;
- incremental processing.

A malformed record on one line is easier to isolate than a malformed giant JSON document containing thousands of events.

---

# 15. Investigating JSON Logs With `jq`

Topic 08 introduced `jq`. Here we apply it specifically to incident investigation.

## 15.1 Filter Errors

```bash
jq 'select(.level == "ERROR")' app.jsonl
```

Meaning:

```text
read each JSON event
      ↓
keep events where level == ERROR
```

## 15.2 Filter One Run

```bash
jq 'select(.run_id == "abc123")' app.jsonl
```

## 15.3 Filter One Component

```bash
jq 'select(.component == "database")' app.jsonl
```

## 15.4 Extract Useful Fields

```bash
jq -r '
  select(.level == "ERROR")
  | [.timestamp, .service, .message]
  | @tsv
' app.jsonl
```

`-r` emits raw strings rather than JSON-quoted strings.

The output can be used in another command-line pipeline.

## 15.5 Combine Conditions

```bash
jq '
  select(
    .level == "ERROR"
    and .service == "orders-consumer"
  )
' app.jsonl
```

Another example:

```bash
jq '
  select(
    .run_id == "abc123"
    and (.level == "ERROR" or .level == "WARN")
  )
' app.jsonl
```

## 15.6 Missing vs Null Fields

Not every event necessarily contains every field.

For example:

```json
{"level":"INFO","message":"started"}
```

has no `run_id`.

Another event may contain:

```json
{"level":"INFO","run_id":null,"message":"started"}
```

These are different states.

Use defensive expressions when necessary:

```bash
jq -r '.run_id // "missing"'
```

This turns `null` into the fallback value.

## 15.7 Extract Timestamps

```bash
jq -r '.timestamp' app.jsonl
```

For an investigation:

```bash
jq -r '
  select(.level == "ERROR")
  | [.timestamp, .service, .component, .message]
  | @tsv
' app.jsonl
```

This produces a compact event stream suitable for timeline analysis.

---

# 16. Counting and Grouping Log Events

A log becomes more useful when you turn raw events into evidence.

Questions include:

- How many errors occurred?
- Which error is most common?
- Which service produced the most errors?
- When did the error rate spike?
- Which component was involved?
- What was the first occurrence?
- What was the latest occurrence?

## 16.1 Raw Text Count

For a simple text log:

```bash
grep "ERROR" app.log | wc -l
```

This counts matching lines.

It is useful as a quick approximation.

But it has limitations.

One physical line is not always one semantic event.

## 16.2 Structured Event Count

For JSONL:

```bash
jq -c 'select(.level == "ERROR")' app.jsonl | wc -l
```

Now you are counting JSON events that satisfy a field condition.

## 16.3 Top Error Messages

A simple structured approach:

```bash
jq -r '
  select(.level == "ERROR")
  | .message
' app.jsonl |
sort |
uniq -c |
sort -nr
```

This produces a frequency ranking.

## 16.4 Group by Service

```bash
jq -r '
  select(.level == "ERROR")
  | .service
' app.jsonl |
sort |
uniq -c |
sort -nr
```

## 16.5 Group by Component

```bash
jq -r '
  select(.level == "ERROR")
  | .component // "unknown"
' app.jsonl |
sort |
uniq -c |
sort -nr
```

## 16.6 First and Latest Occurrence

For sorted ISO-8601 UTC timestamps:

```bash
jq -r '
  select(.level == "ERROR")
  | .timestamp
' app.jsonl |
sort |
head -n 1
```

Latest:

```bash
jq -r '
  select(.level == "ERROR")
  | .timestamp
' app.jsonl |
sort |
tail -n 1
```

This assumes the timestamp representation sorts chronologically. Verify the format before relying on that property.

---

# 17. Errors Per Minute

A useful incident metric is:

```text
errors per minute
```

It can reveal a spike that a total error count hides.

For ISO timestamps, one practical approach is to extract the minute prefix.

For example:

```bash
jq -r '
  select(.level == "ERROR")
  | .timestamp[0:16]
' app.jsonl |
sort |
uniq -c |
sort -nr
```

If:

```text
2026-10-06T14:32:10Z
```

is the timestamp, the prefix:

```text
2026-10-06T14:32
```

represents the minute.

A more explicit output:

```bash
jq -r '
  select(.level == "ERROR")
  | .timestamp[0:16]
' app.jsonl |
sort |
uniq -c |
awk '{print $2, $1}'
```

This is a practical technique, but the exact timestamp format must be verified first.

## 17.1 Why Spikes Matter

Compare:

```text
14:30  2 errors
14:31  3 errors
14:32  4 errors
14:33  250 errors
14:34  310 errors
14:35  280 errors
```

This tells you much more than:

```text
Total errors = 849
```

The spike may identify the beginning of the failure mode.

---

# 18. Building an Incident Timeline

A log investigation should eventually produce a timeline.

For example:

```text
14:30:01  database latency increases
14:31:12  consumer retries begin
14:32:04  queue backlog grows
14:34:15  memory usage increases
14:36:22  consumer becomes slow
14:38:09  OOM killer terminates process
14:38:10  systemd restarts service
14:39:02  retries resume
```

## 18.1 What to Extract

Useful timeline attributes include:

- timestamp;
- first occurrence;
- last occurrence;
- service;
- component;
- run ID;
- request ID;
- job ID;
- process ID;
- level;
- message;
- database evidence;
- resource evidence.

## 18.2 Symptoms vs Causes

Suppose:

```text
14:32 database timeout
14:33 retry storm
14:34 memory grows
14:38 OOM
```

The OOM is a real event.

It may still be a **downstream symptom** rather than the root cause.

The investigation must ask:

> What changed before memory growth?

and:

> Why did the database timeout begin?

## 18.3 First Occurrence Is Often More Valuable Than Loudest Occurrence

The loudest error may occur after the original failure.

For example:

```text
14:31 database connection pressure
14:32 timeout
14:32 retry
14:33 retry
14:34 retry
14:35 retry
```

The repeated retry messages may be numerous, but the first connection-pressure evidence may be more causally informative.

---

# 19. Correlating Multiple Log Sources

This is one of the most important production skills in this module.

A complete incident story may require:

```text
Application logs
        +
systemd journal
        +
kernel logs
        +
database logs
        +
resource observations
```

## 19.1 Example Correlation Chain

```text
Application:
database timeout

        ↓

Database:
slow query / connection pressure

        ↓

Application:
retry storm

        ↓

Server:
memory pressure

        ↓

Kernel:
OOM killer

        ↓

systemd:
service restarted
```

No single source necessarily contains this complete story.

## 19.2 Correlation Keys

Useful keys include:

```text
timestamp
run_id
request_id
job_id
PID
service
component
dataset
partition
```

Correlation is stronger when multiple independent signals agree.

## 19.3 Cross-Source Investigation Example

Application:

```text
2026-10-06T14:35:01Z ERROR database timeout run_id=abc123
```

Database:

```text
2026-10-06T14:35:00Z connection pool exhausted
```

Kernel:

```text
2026-10-06T14:38:09Z Out of memory: Killed process ...
```

systemd:

```text
14:38:10 orders-consumer.service: Main process exited
14:38:10 orders-consumer.service: Scheduled restart job
```

The sequence is stronger than any individual line.

---

# 20. Kernel Logs and OOM Investigation

Topic 06 introduced memory pressure and OOM behavior. Topic 09 connects that resource evidence to logs.

## 20.1 Kernel Evidence

Use:

```bash
journalctl -k
```

or:

```bash
dmesg
```

Search for OOM evidence:

```bash
journalctl -k | grep -i oom
```

A broader search:

```bash
journalctl -k | grep -Ei 'out of memory|killed process'
```

## 20.2 What You Might See

A kernel message may indicate:

```text
Out of memory
Killed process 12345 (python)
```

The exact wording varies by kernel version and distribution.

The important evidence is:

- an OOM event occurred;
- a process was selected for termination;
- the PID/process name may be available;
- the event has a timestamp.

## 20.3 Prove the Chain

Do not say:

> "The application probably ran out of memory."

Build evidence:

```text
memory pressure observed
        ↓
kernel OOM event
        ↓
process PID killed
        ↓
systemd detects exit
        ↓
systemd restarts service
        ↓
application emits startup logs
```

Useful commands:

```bash
journalctl -k --since "2026-10-06 14:30:00" --until "2026-10-06 14:45:00"
```

and:

```bash
journalctl -u orders-consumer.service \
  --since "2026-10-06 14:30:00" \
  --until "2026-10-06 14:45:00"
```

Then correlate timestamps.

---

# 21. Journal Disk Usage and Retention

Logs can become an operational problem themselves.

Check journal disk usage:

```bash
journalctl --disk-usage
```

The journal may use persistent storage, runtime storage, or both depending on system configuration.

## 21.1 Important Retention Concepts

Common journal settings include:

```text
SystemMaxUse
SystemKeepFree
RuntimeMaxUse
MaxRetentionSec
```

### `SystemMaxUse`

Caps the disk space used by persistent journal files.

### `SystemKeepFree`

Protects a configured amount of free filesystem space.

### `RuntimeMaxUse`

Controls runtime journal usage.

### `MaxRetentionSec`

Places a time-oriented retention constraint.

Exact behavior depends on the journal configuration and system.

## 21.2 Why This Matters

A bad retention policy can create:

```text
high log volume
    ↓
journal grows
    ↓
disk pressure
    ↓
services fail to write
    ↓
pipeline failure
```

Therefore, log storage is part of server reliability.

## 21.3 Evidence Preservation Warning

During an active incident, do not blindly delete journal files to free space.

First ask:

```text
What evidence will disappear?
```

Capture relevant evidence before making destructive changes whenever practical.

---

# 22. Preserving Log Evidence

A restart can fix a symptom while destroying useful evidence.

Before changing production state, ask:

> What evidence will disappear?

## 22.1 Evidence to Consider

Preserve, where relevant:

- current application logs;
- rotated logs;
- compressed logs;
- journal entries;
- kernel evidence;
- service status;
- timestamps;
- configuration;
- process information;
- resource observations.

## 22.2 Initial Preservation Snapshot

A practical first-pass collection may include:

```bash
date -u
systemctl status orders-consumer.service
journalctl -u orders-consumer.service --since "30 minutes ago"
journalctl -k --since "30 minutes ago"
df -h
free -h
ps aux
```

The exact commands should be adapted to the incident.

## 22.3 Save Evidence to a Separate Location

For example:

```bash
mkdir -p incident-evidence-2026-10-06
```

Then capture command output:

```bash
journalctl -u orders-consumer.service \
  --since "2026-10-06 14:30:00" \
  --until "2026-10-06 14:45:00" \
  > incident-evidence-2026-10-06/service-journal.txt
```

Kernel evidence:

```bash
journalctl -k \
  --since "2026-10-06 14:30:00" \
  --until "2026-10-06 14:45:00" \
  > incident-evidence-2026-10-06/kernel.txt
```

Record collection time:

```bash
date -u > incident-evidence-2026-10-06/collection-time.txt
```

## 22.4 Checksums

For evidence copies:

```bash
sha256sum incident-evidence-2026-10-06/*
```

This gives you an integrity record for the collected files.

## 22.5 Read-Only Evidence Copies

Where operationally appropriate, treat the evidence directory as immutable after collection.

For example:

```bash
chmod -R a-w incident-evidence-2026-10-06/
```

Do not use permissions as a substitute for proper evidence management, but avoid accidentally editing collected evidence.

## 22.6 Do Not Turn This Into Forensics

The purpose here is production Data Engineering incident investigation, not legal digital forensics.

The practical principle is:

```text
observe
→ capture evidence
→ reason
→ act
→ verify
```

not:

```text
restart
→ hope
```

---

# 23. Centralized Logging Awareness

SSH plus `grep` is useful, but it does not scale indefinitely.

A production architecture often looks like:

```text
Application
    ↓
log collector / agent
    ↓
central log platform
    ↓
search / dashboards / alerts
```

## 23.1 Why Centralize Logs?

Centralized systems can provide:

- aggregation;
- indexing;
- centralized search;
- retention;
- correlation;
- alerting;
- access controls;
- cross-host investigation.

Examples of technologies you should recognize:

- Elastic / ELK;
- OpenSearch;
- Loki;
- Splunk;
- cloud logging platforms;
- OpenTelemetry logging concepts.

This is awareness, not a full centralized observability course.

A later observability and incident-response module can cover the architecture and operations more deeply.

---

# 24. Data Engineering Incident Scenarios

## 24.1 Failed Ingestion

```text
API ingestion fails
        ↓
application log
        ↓
HTTP 500
        ↓
retry
        ↓
database timeout
```

Investigation:

1. identify the affected ingestion service;
2. define the incident window;
3. inspect application logs;
4. correlate request/run IDs;
5. inspect database evidence;
6. determine whether the HTTP failure is primary or downstream.

## 24.2 OOM Consumer

```text
Database slowdown
        ↓
consumer backlog
        ↓
memory growth
        ↓
OOM killer
        ↓
systemd restart
```

Do not stop at:

```text
OOM killed process
```

Investigate what caused the memory growth.

## 24.3 Disk Fills From Logs

```text
application becomes noisy
        ↓
log volume increases
        ↓
rotation misconfigured
        ↓
disk fills
        ↓
pipeline fails
```

Evidence may include:

```bash
df -h
journalctl --disk-usage
du -sh /var/log/*
```

Then inspect rotation configuration.

## 24.4 Timezone Confusion

```text
application: 14:30 UTC
database:    20:00 IST
operator:    20:00 local
```

Normalize before correlating.

---

# 25. Hands-on Labs — `server_lab/09/`

The following exercises are documented inside this module.

Do not create the directory automatically as part of studying this Markdown file.

A suggested local lab layout is:

```text
server_lab/
└── 09/
    ├── logs/
    ├── evidence/
    ├── exercises/
    └── runbooks/
```

Use synthetic data in a disposable environment. Never paste real production secrets, API tokens, private keys, passwords, or sensitive customer data into a training lab.

---

# 26. Lab 1 — Logrotate

## Objective

Configure rotation for the Topic 05 job's application log:

```text
daily
14 copies
compressed
```

and verify the rotation.

## Exercise

### Step 1 — Identify the service

```bash
systemctl status orders-consumer.service
```

Determine where its logs are actually written.

If the service uses the journal, use:

```bash
journalctl -u orders-consumer.service
```

If it uses an application file, identify that file.

### Step 2 — Inspect the current log

```bash
ls -lh /var/log/myapp/
tail -n 50 /var/log/myapp/app.log
```

### Step 3 — Create a test rotation policy

In a disposable lab environment, create a configuration resembling:

```text
/var/log/myapp/app.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

### Step 4 — Validate the configuration

Use the system's `logrotate` validation/test capabilities before forcing a rotation.

A common dry-run form is:

```bash
logrotate -d /etc/logrotate.d/myapp
```

Read the output rather than assuming success.

### Step 5 — Force a test rotation

In a disposable lab only:

```bash
logrotate -f /etc/logrotate.d/myapp
```

### Step 6 — Inspect results

```bash
ls -lh /var/log/myapp/
```

You should reason about files such as:

```text
app.log
app.log.1
app.log.2.gz
```

The exact result depends on the current rotation state and policy.

### Step 7 — Generate new entries

Trigger the Topic 05 service or write controlled test entries through the application's normal test mechanism.

Then inspect:

```bash
tail -n 50 /var/log/myapp/app.log
```

### Step 8 — Investigate the file descriptor

If the expected file behavior is confusing:

```bash
pgrep -af orders-consumer
```

Then:

```bash
lsof -p <PID>
```

Determine which log file the process actually has open.

## Lab Questions

1. Which file contains the newest events?
2. Which file contains the pre-rotation events?
3. Which files are compressed?
4. Did the application reopen the log?
5. Was `copytruncate` used?
6. What would change if the application supported a clean log-reopen signal?

## Production Lesson

Rotation is not only about naming files.

It is about understanding the relationship among:

```text
filename
file descriptor
process
rotation policy
new writes
```

---

# 27. Lab 2 — OOM + Database Slowdown Incident

This is the major incident investigation lab.

## Scenario

You receive an alert:

> `orders-consumer` repeatedly restarts and processing is delayed.

The intended causal chain is:

```text
Database slowdown
        ↓
consumer retries
        ↓
consumer backlog
        ↓
memory growth
        ↓
OOM kill
        ↓
systemd restart
```

Your job is to prove or disprove this chain.

## Evidence Sources

Use:

```text
systemd journal
application JSON logs
kernel logs
database logs
resource observations
```

## Investigation Steps

### Step 1 — Define the Window

Write down:

```text
START:
END:
TIMEZONE:
```

Do not proceed until you know what the timestamps mean.

### Step 2 — Check Service State

```bash
systemctl status orders-consumer.service
```

### Step 3 — Inspect Application Logs

```bash
journalctl -u orders-consumer.service \
  --since "2026-10-06 14:30:00" \
  --until "2026-10-06 14:45:00"
```

If JSONL is file-based:

```bash
jq '
  select(
    .timestamp >= "2026-10-06T14:30:00Z"
    and .timestamp <= "2026-10-06T14:45:00Z"
  )
' app.jsonl
```

Verify the timestamp semantics before using lexical comparisons.

### Step 4 — Find Database Evidence

Search the database log for:

```text
slow query
timeout
connection
lock
```

Do not assume the application error is the first event.

### Step 5 — Check Kernel Evidence

```bash
journalctl -k \
  --since "2026-10-06 14:30:00" \
  --until "2026-10-06 14:45:00"
```

Search:

```bash
journalctl -k \
  --since "2026-10-06 14:30:00" \
  --until "2026-10-06 14:45:00" |
grep -Ei 'oom|out of memory|killed process'
```

### Step 6 — Check Service Restart Evidence

```bash
journalctl -u orders-consumer.service \
  --since "2026-10-06 14:30:00" \
  --until "2026-10-06 14:45:00" |
grep -Ei 'exit|failed|restart|started|stopped'
```

### Step 7 — Build a Minute-by-Minute Timeline

Produce:

```text
14:30
14:31
14:32
...
14:45
```

For every important minute, record:

```text
source
timestamp
service
event
identifier
interpretation
```

### Step 8 — Separate Cause From Symptoms

Your final analysis must explicitly identify:

```text
first database symptom
first application symptom
retry behavior
memory pressure
OOM event
process termination
service restart
recovery
```

Then answer:

> Which event is the root cause, and which events are downstream consequences?

Do not accept "OOM" as the root cause without evidence explaining why memory grew.

---

# 28. Lab 3 — Errors Per Minute and Top 5 Errors

## Objective

Produce:

1. errors per minute;
2. top 5 error messages;

for the last 24 hours from current, rotated, and compressed logs.

## Step 1 — Locate All Logs

```bash
ls -lh /var/log/myapp/
```

Identify:

```text
current
rotated
compressed
```

## Step 2 — Search Compressed Logs

```bash
zgrep -Ei '"level":"ERROR"|ERROR' /var/log/myapp/*.gz
```

Adapt the pattern to the actual log format.

## Step 3 — Structured JSON Approach

For JSONL files:

```bash
jq -r '
  select(.level == "ERROR")
  | .timestamp[0:16]
' /var/log/myapp/app.jsonl |
sort |
uniq -c |
awk '{print $2, $1}'
```

This produces a minute-level error count for the supplied file.

For a real 24-hour investigation, include the relevant rotated JSONL files as well and ensure the time window is explicitly enforced.

## Step 4 — Top 5 Error Messages

```bash
jq -r '
  select(.level == "ERROR")
  | .message // "missing-message"
' /var/log/myapp/app.jsonl |
sort |
uniq -c |
sort -nr |
head -n 5
```

## Step 5 — Text Log Approach

For simple text logs:

```bash
grep -hEi "ERROR|FAILED|TIMEOUT" /var/log/myapp/app.log /var/log/myapp/app.log.1 |
sort
```

For compressed logs:

```bash
zgrep -hEi "ERROR|FAILED|TIMEOUT" /var/log/myapp/*.gz
```

## Compare the Approaches

Text matching is quick but fragile.

Structured JSON filtering is generally more robust because:

```text
field == ERROR
```

is more precise than:

```text
line contains ERROR
```

A message may contain the word `ERROR` without its severity being `ERROR`.

---

# 29. Lab 4 — Trace One `run_id` Across Two Services

## Scenario

Two services process the same pipeline run:

```text
extract-service
transform-service
```

Both emit JSONL.

You need to trace:

```text
run_id=abc123
```

## Step 1 — Filter the Run

```bash
jq '
  select(.run_id == "abc123")
' extract-service.jsonl
```

and:

```bash
jq '
  select(.run_id == "abc123")
' transform-service.jsonl
```

## Step 2 — Create a Compact View

```bash
jq -r '
  select(.run_id == "abc123")
  | [.timestamp, .service, .level, .component, .message]
  | @tsv
' extract-service.jsonl
```

Repeat for the transform service.

## Step 3 — Combine and Sort

```bash
{
  jq -r '
    select(.run_id == "abc123")
    | [.timestamp, .service, .level, .component, .message]
    | @tsv
  ' extract-service.jsonl

  jq -r '
    select(.run_id == "abc123")
    | [.timestamp, .service, .level, .component, .message]
    | @tsv
  ' transform-service.jsonl
} | sort
```

If timestamps are normalized ISO-8601 UTC strings, lexical sorting is useful.

Verify that assumption first.

## Deliverable

Reconstruct:

```text
run started
    ↓
extract began
    ↓
extract completed
    ↓
transform began
    ↓
transform failed / succeeded
```

Identify the first failure and the downstream effects.

---

# 30. Lab 5 — Failed Run Investigation Runbook

Write a production-style runbook titled:

> **How to investigate a failed run on a server**

Use this structure:

```text
Symptom
   ↓
Initial checks
   ↓
Relevant logs
   ↓
Time window
   ↓
Search commands
   ↓
Correlation
   ↓
Evidence
   ↓
Likely causes
   ↓
Verification
   ↓
Fix
   ↓
Post-fix validation
```

## Required Runbook Content

### Symptom

Example:

```text
Scheduled ingestion run failed.
```

### Initial Checks

```bash
systemctl status ingestion.service
date -u
df -h
free -h
```

### Relevant Logs

Identify:

```text
application
systemd
kernel
database
```

### Time Window

Record:

```text
start
end
timezone
```

### Search Commands

Include commands for:

```text
current logs
rotated logs
compressed logs
journal
JSONL
kernel
```

### Correlation

Document identifiers:

```text
run_id
request_id
job_id
PID
service
```

### Evidence

State what proves the hypothesis.

### Likely Causes

Rank hypotheses rather than listing unrelated possibilities.

### Verification

Explain how to test each hypothesis.

### Fix

Describe the smallest justified change.

### Post-Fix Validation

Confirm:

```text
service healthy
run succeeds
errors stop
backlog recovers
resource pressure resolves
```

The runbook should be usable by another engineer at 3 a.m.

---

# 31. Break/Fix Exercises

These exercises force you to investigate instead of memorize.

## Failure 1 — Log File Grows Without Rotation

### Scenario

```text
/var/log/myapp/app.log
```

grows continuously.

### Symptoms

```text
df -h
```

shows declining free space.

### Expected Evidence

```bash
ls -lh /var/log/myapp/
df -h
```

### Investigation Steps

1. inspect log size;
2. inspect rotation configuration;
3. determine whether rotation is scheduled;
4. inspect recent rotation history;
5. identify whether journal storage is also contributing.

### Root Cause

Rotation policy is absent, disabled, or incorrect.

### Fix

Configure and validate an appropriate rotation policy.

### Verification

Generate controlled logs and verify rotation.

### Production Lesson

Log volume is part of capacity planning.

---

## Failure 2 — Rotation Happens but the Application Writes Unexpectedly

### Scenario

`app.log` rotates, but the expected new events appear in a surprising location.

### Investigation

Check:

```bash
lsof -p <PID>
```

and inspect:

```text
rotation method
file descriptor
application reopen behavior
```

### Root Cause

Filename rotation and open file descriptors were treated as the same thing.

### Production Lesson

A process writes through file descriptors, not filenames alone.

---

## Failure 3 — Important Incident Exists Only in `.gz`

### Scenario

The current log looks clean.

The incident happened yesterday.

### Expected Evidence

```bash
ls -lh /var/log/myapp/
zgrep -Ei "error|failed|timeout" /var/log/myapp/*.gz
```

### Root Cause

The investigation searched only the current file.

### Production Lesson

Historical evidence often lives in rotated and compressed logs.

---

## Failure 4 — Local Time vs UTC

### Scenario

The operator believes the database event happened 5.5 hours after the application error.

### Investigation

Compare:

```text
Z suffix
timezone offset
server timezone
database timezone
operator timezone
```

### Root Cause

Timestamps were compared without normalization.

### Production Lesson

No incident timeline is trustworthy until timestamp semantics are known.

---

## Failure 5 — Application Failure Hides an OOM Event

### Scenario

Application logs end with:

```text
worker failed
```

### Investigation

```bash
journalctl -k | grep -Ei 'oom|out of memory|killed process'
```

### Root Cause

Kernel evidence reveals process termination.

### Production Lesson

Application logs are only one layer of the system.

---

## Failure 6 — Same Error, Different `run_id`

### Scenario

Two pipeline runs contain:

```text
database timeout
```

but only one run is failing.

### Investigation

Filter:

```bash
jq 'select(.run_id == "abc123")' app.jsonl
```

and compare with the other run.

### Root Cause

Message text alone was used as the correlation key.

### Production Lesson

Prefer structured identifiers over generic error strings.

---

## Failure 7 — Journal Consumes Too Much Disk

### Scenario

Disk usage is high and journal storage is significant.

### Investigation

```bash
journalctl --disk-usage
df -h
```

Then inspect journal retention configuration.

### Root Cause

Uncontrolled or unexpectedly high journal volume/retention.

### Production Lesson

Observability data has operational cost.

---

## Failure 8 — Service Restarted Before Evidence Collection

### Scenario

An operator restarts the service immediately.

### Investigation Problem

The restart may have changed:

- process state;
- memory state;
- open files;
- current logs;
- journal sequence;
- temporary evidence.

### Root Cause

Remediation happened before evidence preservation.

### Production Lesson

When safe, observe and capture before changing state.

---

## Failure 9 — JSON Contains Missing/Null Fields

### Scenario

Some events have no `component`.

### Investigation

Use defensive queries:

```bash
jq -r '.component // "unknown"' app.jsonl
```

### Root Cause

The investigation assumed every event had a complete schema.

### Production Lesson

Production log schemas evolve and may contain null or missing fields.

---

## Failure 10 — Current Log Looks Clean

### Scenario

No failure appears in:

```text
app.log
```

### Investigation

Inspect:

```text
app.log.1
app.log.2.gz
```

### Root Cause

The incident had already rotated out of the current file.

### Production Lesson

Current state and historical state are different evidence sets.

---

# 32. Production Investigation Workflow

Use this sequence as a reusable investigation method.

```text
1. Define the incident window
2. Confirm timezone
3. Identify affected service
4. Check service status
5. Inspect recent logs
6. Follow logs if the issue is live
7. Search rotated/compressed logs
8. Search by run_id/request_id/component
9. Check kernel/system logs
10. Check database logs
11. Correlate timestamps
12. Build timeline
13. Separate symptoms from causes
14. Preserve evidence
15. Apply fix
16. Verify recovery
17. Document incident
```

## Why This Order?

It moves from:

```text
scope
→ evidence
→ correlation
→ hypothesis
→ action
→ verification
```

rather than:

```text
random grep
→ guess
→ restart
```

### Do Not:

```text
Don't restart first.
Don't grep randomly.
Don't assume the first ERROR is the root cause.
Don't ignore rotated logs.
Don't ignore time zones.
Don't trust one log source.
```

---

# 33. Practical Decision Tree

```text
Something failed
      |
      v
Is it currently happening?
      |
   +--+--+
   |     |
  YES    NO
   |     |
tail /   define incident
journal  window
   |     |
   +-----+
      |
      v
Which service?
      |
      v
systemd status + service logs
      |
      v
Application error?
   +--+--+
   |     |
  YES    NO
   |     |
JSON/text kernel/system/database
   |
   v
Can it be correlated by run_id?
   |
   v
Build timeline
   |
   v
Preserve evidence
   |
   v
Fix + verify
```

## Decision Tree Usage

The tree is not a replacement for reasoning.

At each branch ask:

```text
What evidence would make this branch true?
```

For example:

```text
Application error?
```

means:

```text
Do application logs actually contain evidence
that the application initiated the failure?
```

not:

```text
Did I find an ERROR string?
```

---

# 34. Failed Run Investigation Runbook

## Symptom

A scheduled Data Engineering run failed or is repeatedly retrying.

## Initial Checks

```bash
date -u
systemctl status <service>
df -h
free -h
```

## Relevant Logs

Identify:

```text
application log
systemd journal
kernel journal
database log
rotated logs
compressed logs
```

## Define the Window

Record:

```text
incident_start_utc
incident_end_utc
timezone_source
```

## Search

For a systemd service:

```bash
journalctl -u <service> \
  --since "YYYY-MM-DD HH:MM:SS" \
  --until "YYYY-MM-DD HH:MM:SS"
```

For live evidence:

```bash
journalctl -u <service> -f
```

For text:

```bash
grep -Ei "error|failed|timeout" <log>
```

For compressed:

```bash
zgrep -Ei "error|failed|timeout" <log>.gz
```

For JSONL:

```bash
jq '
  select(.run_id == "abc123")
' <log>.jsonl
```

## Correlation

Look for:

```text
run_id
request_id
job_id
PID
service
component
timestamp
```

## Evidence

Record:

```text
command
timestamp
output
interpretation
```

## Likely Causes

Rank them:

```text
1. database connection pressure
2. application retry storm
3. memory growth
4. OOM termination
```

Do not treat this as a conclusion until verified.

## Verification

Ask:

```text
What independent evidence supports the hypothesis?
```

## Fix

Apply the smallest justified operational change.

## Post-Fix Validation

Verify:

```bash
systemctl status <service>
journalctl -u <service> --since "10 minutes ago"
```

Then verify application-level recovery:

```text
new runs succeed
backlog declines
error rate normalizes
```

---

# 35. Common Mistakes

## Mistake 1 — Logs Grow Without Rotation

Why it fails:

```text
logs → disk exhaustion → service failure
```

Fix:

- define rotation;
- define retention;
- monitor disk usage;
- test rotation.

## Mistake 2 — Copy-Transform/Truncate Surprises

Do not assume that rotating a filename automatically changes what a running process writes to.

Understand:

```text
process
file descriptor
inode
filename
```

## Mistake 3 — Searching Only the Current File

Historical evidence may be in:

```text
app.log.1
app.log.2.gz
```

## Mistake 4 — Mixing Time Zones

Never correlate:

```text
20:05
```

without knowing the timezone.

## Mistake 5 — Restarting Before Evidence Collection

A restart can change or remove evidence.

## Mistake 6 — Treating the First ERROR as Root Cause

The first visible error may itself be downstream.

## Mistake 7 — Ignoring Kernel Logs

An application may say:

```text
worker stopped
```

while the kernel says:

```text
Killed process
```

## Mistake 8 — Ignoring Database Logs

A database timeout often deserves investigation at the database layer.

## Mistake 9 — Searching Massive Logs Without a Window

Always narrow:

```text
time
service
identifier
```

before broad searching.

## Mistake 10 — Deleting Logs During an Incident

Freeing disk may be necessary in an emergency, but deleting evidence blindly can make diagnosis impossible.

Capture relevant evidence first when practical.

## Mistake 11 — Ignoring Compressed Archives

A `.gz` file may contain the only evidence of yesterday's incident.

## Mistake 12 — Assuming Timestamps Are UTC

The presence or absence of a timezone marker matters.

## Mistake 13 — Confusing Symptoms With Causes

```text
OOM
```

is an event.

It is not automatically the root cause.

---

# 36. Command Reference

This is an investigation-oriented reference, not a man-page dump.

| Command | Purpose | Example | Common Mistake |
|---|---|---|---|
| `tail` | View recent lines | `tail -n 100 app.log` | Reading an arbitrary number without context |
| `tail -f` | Follow a live file | `tail -f app.log` | Following the wrong or huge file |
| `less` | Navigate a large log | `less app.log` | Opening huge logs in an editor |
| `less +F` | Follow and navigate | `less +F app.log` | Forgetting `Ctrl+C` exits follow mode |
| `grep` | Search text | `grep -Ei "error|timeout" app.log` | Ignoring time window |
| `zgrep` | Search compressed logs | `zgrep "ERROR" *.gz` | Searching only current logs |
| `zcat` | Decompress to stdout | `zcat app.log.2.gz` | Producing enormous terminal output |
| `journalctl` | Query journal | `journalctl --since "1 hour ago"` | Not narrowing scope |
| `journalctl -u` | Filter by service | `journalctl -u orders-consumer.service` | Using the wrong unit |
| `journalctl -f` | Follow journal | `journalctl -u orders-consumer.service -f` | Watching unrelated services |
| `journalctl -k` | Query kernel logs | `journalctl -k` | Assuming application logs contain kernel evidence |
| `--since` | Start time boundary | `--since "2026-10-06 14:32:00"` | Wrong timezone |
| `--until` | End time boundary | `--until "2026-10-06 14:47:00"` | Making an overly broad window |
| `journalctl --disk-usage` | Journal storage usage | `journalctl --disk-usage` | Deleting evidence blindly |
| `dmesg` | Kernel ring-buffer evidence | `dmesg` | Treating it as the only kernel source |
| `logrotate` | Rotate logs | `logrotate -d config` | Forcing rotation on production without review |
| `jq` | Query JSON logs | `jq 'select(.level=="ERROR")' app.jsonl` | Assuming every field exists |
| `wc` | Count lines | `wc -l` | Equating lines with semantic events |
| `sort` | Sort extracted evidence | `sort` | Sorting timestamps without verifying format |
| `uniq` | Count repeated values | `uniq -c` | Forgetting that input must be sorted for grouping |
| `head` | Take first records | `head -n 20` | Assuming first record is root cause |
| `tail` | Take final records | `tail -n 20` | Treating latest event as root cause |

---

# 37. Realistic Investigation Command Patterns

## Service Status

```bash
systemctl status orders-consumer.service
```

Use when:

- service state is uncertain;
- investigating a restart;
- validating recovery.

## Recent Service Logs

```bash
journalctl -u orders-consumer.service --since "1 hour ago"
```

## Live Service Logs

```bash
journalctl -u orders-consumer.service -f
```

## Kernel Evidence

```bash
journalctl -k --since "30 minutes ago"
```

## Journal Disk Usage

```bash
journalctl --disk-usage
```

## Text Errors

```bash
grep -Ei "error|failed|timeout" /var/log/myapp/app.log
```

## Compressed Errors

```bash
zgrep -Ei "error|failed|timeout" /var/log/myapp/*.gz
```

## JSON Errors

```bash
jq 'select(.level == "ERROR")' app.jsonl
```

## Trace a Run

```bash
jq -r '
  select(.run_id == "abc123")
  | [.timestamp,.service,.level,.message]
  | @tsv
' app.jsonl
```

The point is not memorization.

The point is understanding:

```text
scope
→ filter
→ extract
→ correlate
```

---

# 38. Explain Commands, Don't Just Memorize Them

Consider:

```bash
journalctl -u orders-consumer.service \
  --since "2026-10-06 14:32:00" \
  --until "2026-10-06 14:47:00"
```

Read it as:

```text
journalctl
    ↓
query the journal

-u
    ↓
select one systemd service

orders-consumer.service
    ↓
the affected service

--since
    ↓
start boundary

--until
    ↓
end boundary
```

This mental parsing skill matters more than memorizing one command.

---

# 39. Production Safety Rules

Log investigation can itself cause operational damage if done carelessly.

## Rule 1 — Observe Before Acting

Prefer:

```text
observe
→ capture evidence
→ reason
→ act
→ verify
```

## Rule 2 — Treat Deletion as Destructive

Commands that delete or truncate evidence require explicit justification.

Do not casually use:

```bash
rm
```

on production logs during an active incident.

## Rule 3 — Be Careful With Rotation Tests

Do not force rotation against an unknown production configuration merely because you want to see what happens.

Use a disposable lab for learning.

## Rule 4 — Restart Only With a Reason

A restart can:

- destroy process state;
- change memory evidence;
- close file descriptors;
- alter log behavior;
- remove transient state.

## Rule 5 — Never Put Secrets in Logs or Training Data

Do not intentionally create examples containing:

- passwords;
- API tokens;
- private keys;
- cloud credentials;
- customer-sensitive data.

Use synthetic values.

---

# 40. Practice Questions

## Level 1 — Fundamentals

1. What is a log?
2. Why can application logs and system logs contain different evidence?
3. What is `/var/log`?
4. What is the systemd journal?
5. When would you use `tail -f`?
6. What does `less +F` provide?
7. Why are logs rotated?
8. Why are rotated logs often compressed?
9. Why might a database have its own logs?
10. Why should an investigation define a time window?

## Level 2 — Command-Line Investigation

11. How would you inspect the last 100 lines of a log?
12. How would you follow a systemd service live?
13. How would you search a `.gz` log?
14. How would you inspect kernel logs?
15. How would you check journal disk usage?
16. Why is `less` useful for large logs?
17. How would you search for `ERROR` and `timeout`?
18. How would you investigate a log from yesterday?
19. Why is `grep` alone insufficient for many incidents?
20. What is the purpose of `--since` and `--until`?

## Level 3 — Structured Logs

21. What is JSON logging?
22. What is JSONL?
23. Why is `run_id` useful?
24. How would you filter errors with `jq`?
25. How would you select one `run_id`?
26. How do you handle missing fields?
27. How would you extract timestamp and message?
28. How would you group errors by service?
29. How would you find the top error messages?
30. How would you calculate errors per minute?

## Level 4 — Incident Investigation

31. Why might the first `ERROR` not be the root cause?
32. How would you correlate application and database logs?
33. How would you investigate an OOM kill?
34. How would you prove that systemd restarted a service after an OOM?
35. How would you reconstruct a timeline?
36. Why do time zones matter?
37. How would you investigate an incident that occurred yesterday?
38. Why should you inspect compressed logs?
39. Why preserve evidence before restarting?
40. What evidence would you capture before making a production change?

## Level 5 — Production Scenarios

41. A pipeline fails every morning at 02:00. How would you investigate?
42. A consumer restarts repeatedly but application logs show no clear error. What sources would you inspect?
43. A database timeout is followed by an OOM. How would you determine causality?
44. A service log rotated but the application seems to write somewhere unexpected. What would you inspect?
45. Journal storage is consuming significant disk. What would you investigate?
46. Two services emit the same error message. How would you determine which run failed?
47. The current log contains no evidence of yesterday's incident. What would you do?
48. An operator asks you to restart immediately. What evidence should you consider first?
49. How would you build a runbook for a recurring failed run?
50. How would you explain to a junior engineer why log investigation is a Data Engineering skill?

---

# 41. Interview Questions

## Beginner

### 1. What is a log?

**Model Answer:**  
A log is a record of events produced by an application, service, database, operating system, or kernel. It provides evidence about what happened and when.

**Why the Answer Matters:**  
It establishes that logs are evidence, not just debugging text.

**Common Weak Answer:**  
"Logs show errors."

**Senior-Level Answer:**  
Logs are time-stamped operational evidence emitted by different system layers. Effective incident investigation correlates them to reconstruct system behavior.

### 2. Where are Linux logs stored?

**Model Answer:**  
File-based logs are commonly found under `/var/log`, while systemd-managed services often write to the systemd journal. Applications and databases may use their own configured locations.

**Why the Answer Matters:**  
There is no universal single log location.

**Common Weak Answer:**  
"All Linux logs are in `/var/log`."

**Senior-Level Answer:**  
Determine the service's logging mechanism first, then inspect the appropriate source — file, journal, database log, container runtime, or centralized logging system.

### 3. What does `tail -f` do?

**Model Answer:**  
It displays the end of a file and continues showing new lines as they are appended.

**Why the Answer Matters:**  
It is fundamental for live incident observation.

**Common Weak Answer:**  
"It reads a file."

**Senior-Level Answer:**  
It is a live-following technique for file-based logs; it is most useful after narrowing to the relevant service and recent context.

### 4. Why use `less` for large logs?

**Model Answer:**  
It provides efficient paging, searching, and navigation without requiring a graphical editor.

**Why the Answer Matters:**  
Server logs can be very large.

**Common Weak Answer:**  
"Because it is easier."

**Senior-Level Answer:**  
`less` supports targeted navigation and search over large text streams and can switch into follow mode with `+F`.

## Intermediate

### 5. What is `logrotate`?

**Model Answer:**  
A mechanism for rotating log files according to time/size policies and applying retention and compression rules.

**Why the Answer Matters:**  
Without rotation, logs can consume all disk space.

**Common Weak Answer:**  
"It deletes old logs."

**Senior-Level Answer:**  
Rotation is a lifecycle policy involving naming, retention, compression, and application file-descriptor behavior.

### 6. Why compress rotated logs?

**Model Answer:**  
Older logs are usually accessed less frequently, so compression reduces storage consumption while retaining evidence.

**Why the Answer Matters:**  
Historical evidence remains useful.

**Common Weak Answer:**  
"To make files smaller."

**Senior-Level Answer:**  
Compression balances retention requirements with disk capacity and makes long-term local evidence more affordable.

### 7. What is `copytruncate`?

**Model Answer:**  
It copies a log to a rotated file and then truncates the original file, allowing an application with an open file descriptor to continue using the original file object.

**Why the Answer Matters:**  
It explains surprising post-rotation behavior.

**Common Weak Answer:**  
"It renames the log."

**Senior-Level Answer:**  
It avoids requiring an application to reopen a renamed file, but copy/truncate introduces race and potential data-loss trade-offs for high-volume writers.

### 8. Why can `copytruncate` cause problems?

**Model Answer:**  
The file can change while it is being copied, creating a window where writes race with rotation.

**Why the Answer Matters:**  
Rotation can affect evidence integrity.

**Common Weak Answer:**  
"It is slower."

**Senior-Level Answer:**  
Copy-and-truncate can produce small consistency windows and may lose or duplicate boundary writes depending on application behavior and timing.

### 9. How do you search `.gz` logs?

**Model Answer:**

```bash
zgrep "ERROR" app.log.2.gz
```

or:

```bash
zcat app.log.2.gz | grep "ERROR"
```

**Why the Answer Matters:**  
Historical incidents often live in compressed logs.

**Common Weak Answer:**  
"Unzip everything first."

**Senior-Level Answer:**  
Use streaming tools to avoid unnecessary extraction and preserve the archive.

### 10. Why should production systems use UTC?

**Model Answer:**  
UTC provides a common reference across servers, regions, applications, and databases.

**Why the Answer Matters:**  
Incident timelines depend on correct ordering.

**Common Weak Answer:**  
"UTC is simpler."

**Senior-Level Answer:**  
UTC eliminates many ambiguity and daylight-saving problems when correlating distributed events, while original source timestamps should still be retained where relevant.

## Advanced

### 11. How would you investigate an OOM-killed Data Engineering service?

**Model Answer:**  
I would establish the incident window, inspect service logs, inspect kernel evidence with `journalctl -k`, correlate the killed PID with the service, review memory-pressure observations, inspect preceding application/database events, and verify systemd restart behavior.

**Why the Answer Matters:**  
OOM is a cross-layer incident.

**Common Weak Answer:**  
"Check `free -h`."

**Senior-Level Answer:**  
Build an evidence chain from memory pressure to kernel OOM selection to process termination to service restart, then investigate what caused the memory growth.

### 12. How would you correlate application and kernel logs?

**Model Answer:**  
Normalize timestamps, define a narrow time window, identify the service/PID, and compare application events with kernel events.

**Why the Answer Matters:**  
No single layer has the complete story.

**Common Weak Answer:**  
"Use grep."

**Senior-Level Answer:**  
Use independent identifiers and synchronized timestamps to establish causal sequence rather than relying on message similarity.

### 13. How would you reconstruct a production incident timeline?

**Model Answer:**  
I would establish UTC boundaries, collect relevant sources, identify first and last occurrences, correlate run IDs/PIDs/service names, and order events chronologically.

**Why the Answer Matters:**  
Timeline reconstruction separates cause from symptoms.

**Common Weak Answer:**  
"Read the logs."

**Senior-Level Answer:**  
Create an evidence table with timestamp, source, service, identifier, event, interpretation, and confidence.

### 14. How do you investigate a failure that occurred yesterday?

**Model Answer:**  
Define the exact window, identify current and rotated logs, search compressed archives, query historical journal entries, normalize timestamps, and correlate all relevant sources.

**Why the Answer Matters:**  
Current logs may no longer contain the evidence.

**Common Weak Answer:**  
"Look in yesterday's log."

**Senior-Level Answer:**  
Treat log retention and rotation as part of the evidence model and verify that the search covers every generation that could contain the event.

### 15. How do you distinguish root cause from downstream symptoms?

**Model Answer:**  
Find the earliest reliable anomaly and test whether later events can be explained by it, while checking independent evidence.

**Why the Answer Matters:**  
The loudest error is often not the cause.

**Common Weak Answer:**  
"The first ERROR is the root cause."

**Senior-Level Answer:**  
Use temporal precedence, causal plausibility, cross-source corroboration, and controlled verification to distinguish root cause from consequences.

---

# 42. Knowledge Check

Use this as a completion checklist.

- [ ] Can I identify where a service's logs live?
- [ ] Can I distinguish application logs from systemd and kernel logs?
- [ ] Can I follow a service's logs live?
- [ ] Can I use `less` to investigate a large log?
- [ ] Can I investigate yesterday's incident?
- [ ] Can I search rotated logs?
- [ ] Can I search compressed `.gz` logs?
- [ ] Can I configure and reason about `logrotate`?
- [ ] Can I explain `copytruncate`?
- [ ] Can I reason about file descriptors during rotation?
- [ ] Can I define a precise incident window?
- [ ] Can I normalize timestamps to UTC?
- [ ] Can I explain structured JSON logging?
- [ ] Can I filter JSON logs with `jq`?
- [ ] Can I handle missing/null fields?
- [ ] Can I count errors per minute?
- [ ] Can I find the top error messages?
- [ ] Can I trace a `run_id` across services?
- [ ] Can I identify an OOM kill from kernel evidence?
- [ ] Can I correlate application + database + kernel + systemd logs?
- [ ] Can I preserve evidence before restarting?
- [ ] Can I build a minute-by-minute incident timeline?
- [ ] Can I distinguish symptoms from root causes?
- [ ] Can I write a production failed-run investigation runbook?
- [ ] Can I explain when centralized logging becomes preferable to local SSH investigation?

If any answer is "no", return to the corresponding section and repeat the lab.

---

# 43. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Where |
|---|---|---|
| Application log files | ✅ | §3 |
| systemd journal | ✅ | §3, §5, §11 |
| `/var/log` | ✅ | §3 |
| Relationship between application/service/system logs | ✅ | §2–§3, §19 |
| Kernel logs | ✅ | §3, §20 |
| `tail -f` | ✅ | §5 |
| `tail -n 100 -f` | ✅ | §5 |
| `less +F` | ✅ | §5–§6 |
| `journalctl -f` | ✅ | §5 |
| Log paging/search | ✅ | §6 |
| `logrotate` | ✅ | §7–§8 |
| Rotation frequency | ✅ | §7–§8 |
| Daily rotation | ✅ | §7–§8 |
| Weekly rotation awareness | ✅ | §7 |
| Size-based rotation | ✅ | §8 |
| Retention count | ✅ | §8 |
| Compression | ✅ | §7–§8 |
| Delayed compression | ✅ | §7–§8 |
| New-file rotation | ✅ | §9 |
| `copytruncate` | ✅ | §9 |
| File descriptors | ✅ | §9 |
| Long-running processes | ✅ | §9 |
| Deleted/open-file implications | ✅ | §9 |
| Rotation investigation implications | ✅ | §9 |
| `zgrep` | ✅ | §10 |
| `zcat` | ✅ | §10 |
| Current + rotated + compressed search | ✅ | §10 |
| Time-window extraction | ✅ | §11 |
| Timezone handling | ✅ | §12 |
| UTC | ✅ | §12 |
| Structured JSON logs | ✅ | §13 |
| JSONL | ✅ | §14 |
| `jq` filtering | ✅ | §15 |
| `select` | ✅ | §15 |
| `-r` | ✅ | §15 |
| Null/missing fields | ✅ | §15 |
| Timestamp extraction | ✅ | §15 |
| `run_id` | ✅ | §15, §29 |
| `level` | ✅ | §13–§15 |
| `component` | ✅ | §15–§16 |
| Counting events | ✅ | §16 |
| Grouping by error type/message | ✅ | §16 |
| Grouping by service | ✅ | §16 |
| Grouping by component | ✅ | §16 |
| Grouping by minute | ✅ | §17 |
| First occurrence | ✅ | §16, §18 |
| Latest occurrence | ✅ | §16 |
| Errors per minute | ✅ | §17, Lab 3 |
| Top 5 errors | ✅ | Lab 3 |
| Incident timeline | ✅ | §18 |
| Application correlation | ✅ | §19 |
| systemd correlation | ✅ | §19–§20 |
| Kernel correlation | ✅ | §19–§20 |
| Database correlation | ✅ | §19 |
| OOM investigation | ✅ | §20, Lab 2 |
| Journal disk usage | ✅ | §21 |
| Journal retention | ✅ | §21 |
| Evidence preservation | ✅ | §22 |
| Centralized logging awareness | ✅ | §23 |
| `server_lab/09` exercise 1 | ✅ | Lab 1 |
| `server_lab/09` exercise 2 | ✅ | Lab 2 |
| `server_lab/09` exercise 3 | ✅ | Lab 3 |
| `server_lab/09` exercise 4 | ✅ | Lab 4 |
| `server_lab/09` exercise 5 | ✅ | Lab 5 |
| Break/fix exercises | ✅ | §31 |
| Production investigation workflow | ✅ | §32 |
| Decision tree | ✅ | §33 |
| Failed-run runbook | ✅ | §34 |
| Command reference | ✅ | §36 |
| Common mistakes | ✅ | §35 |
| Practice questions | ✅ | §40 |
| Interview questions | ✅ | §41 |
| Knowledge check | ✅ | §42 |
| Production safety guidance | ✅ | §39 |
| Final mental model | ✅ | §44 |

**Audit result: all explicitly required Topic 09 concepts and exercises are covered in this module.**

---

# 44. Final Quality and Safety Review

Before considering this module complete, verify:

- [x] Beginner concepts lead naturally into advanced incident investigation.
- [x] Data Engineering context is used throughout.
- [x] Application, service, kernel, and database logs are distinguished.
- [x] Live and historical investigation are distinguished.
- [x] `tail`, `less`, and `journalctl` are explained rather than merely listed.
- [x] Log rotation is explained conceptually and operationally.
- [x] `copytruncate` trade-offs are explained.
- [x] Rotated and compressed logs are included.
- [x] Time windows and timezone normalization are included.
- [x] UTC is included.
- [x] Structured JSON/JSONL logging is taught.
- [x] `jq` is used practically.
- [x] Missing/null fields are considered.
- [x] Error aggregation and errors-per-minute analysis are included.
- [x] Incident timeline reconstruction is included.
- [x] Cross-source correlation is included.
- [x] OOM/kernel investigation is included.
- [x] Journal disk usage and retention are included.
- [x] Evidence preservation is included.
- [x] Centralized logging is included only at awareness level.
- [x] All five `server_lab/09` exercises are included.
- [x] Break/fix exercises are included.
- [x] A reusable production workflow is included.
- [x] A failed-run runbook is included.
- [x] Practice questions are included.
- [x] Interview questions include model answers and senior-level framing.
- [x] Knowledge check is included.
- [x] Roadmap coverage audit is included.
- [x] Destructive operations are treated with explicit operational caution.
- [x] No real credentials are required.
- [x] Synthetic data is recommended for labs.

## Operational Safety Rule

Whenever an operation could:

- delete logs;
- truncate files;
- remove evidence;
- restart a service;
- modify retention;
- alter production state;

reason first:

```text
observe
→ capture evidence
→ reason
→ act
→ verify
```

Do not teach:

```text
restart
→ hope
```

---

# 45. Final Mental Model

```text
LOG INVESTIGATION

1. FIND
   Where is the evidence?

2. NARROW
   What service?
   What time window?
   What run_id?

3. SEARCH
   Current + rotated + compressed logs.

4. STRUCTURE
   Extract timestamps, levels, components, IDs, messages.

5. CORRELATE
   Application
   + systemd
   + kernel
   + database
   + resource evidence

6. RECONSTRUCT
   Build the timeline.

7. DISTINGUISH
   Symptom ≠ root cause.

8. PRESERVE
   Capture evidence before destructive actions.

9. FIX
   Apply the smallest justified fix.

10. VERIFY
    Confirm recovery from evidence.

11. DOCUMENT
    Turn the investigation into a runbook.
```

> **A production Data Engineer does not simply read logs.**
>
> **A production Data Engineer uses logs as evidence to reconstruct what happened on the system.**

## Completion Standard

You are ready to move forward when you can independently take a realistic failed Data Engineering run and:

```text
find the evidence
    ↓
define the time window
    ↓
normalize timestamps
    ↓
search current + rotated + compressed logs
    ↓
filter structured JSON logs
    ↓
trace identifiers across services
    ↓
correlate application + database + systemd + kernel evidence
    ↓
reconstruct the timeline
    ↓
separate symptoms from causes
    ↓
preserve evidence
    ↓
apply and verify a justified fix
    ↓
document the investigation as a runbook
```

That is the production-grade skill this Topic 09 module is designed to build.
