# Logs, Exec, and Troubleshooting Containers

**Stage 2B — Python for Data Engineering_2**  
**Gap Module G1 — Docker Essentials for Data Labs**  
**Topic 06 — Logs, Exec, and Troubleshooting Containers**  
**Phase C — Operating Stacks**

> **Core idea:** Troubleshooting is not random command execution. It is evidence-driven hypothesis testing: observe the symptom, collect evidence, test the smallest reasonable hypothesis, identify the root cause, make one relevant change, and verify the result.

---

## 1. Learning Objectives

By the end of this module, you should be able to:

- Explain what troubleshooting means.
- Distinguish a symptom from a cause and a root cause.
- Distinguish Docker/container state from application/service state.
- Perform a disciplined first-response investigation.
- Use `docker ps` and `docker ps -a` as evidence sources.
- Interpret exit status without inventing meanings for arbitrary non-zero codes.
- Use `docker logs`, including following, tailing, and time filtering.
- Understand the difference between container stdout/stderr and application log files.
- Use `docker exec` safely and purposefully.
- Work with images that have `sh` but not `bash`, or lack common diagnostic tools.
- Run targeted commands inside a container without opening an interactive shell.
- Inspect processes with `docker top` and suitable in-container tools.
- Understand why PID 1 matters during container troubleshooting.
- Inspect filesystem state, configuration, mounts, and runtime metadata.
- Distinguish container started, application initialized, application ready, and application healthy.
- Diagnose restart loops.
- Classify failures as configuration, storage, networking, dependency, application, or possible resource failures.
- Troubleshoot PostgreSQL, MinIO, Redis, and Kafka-style services.
- Use temporary diagnostic containers instead of unnecessarily mutating service containers.
- Read logs causally and identify the first meaningful failure.
- Build incident timelines.
- Preserve evidence before destructive actions.
- Reproduce failures in a controlled way.
- Apply a repeatable troubleshooting decision tree.
- Document the root cause, fix, and verification.

### The operational progression

```text
Observe
   ↓
Collect evidence
   ↓
Form hypothesis
   ↓
Inspect
   ↓
Reproduce
   ↓
Identify root cause
   ↓
Fix
   ↓
Verify
   ↓
Document
```

---

# 2. What Troubleshooting Means

## 2.1 Simple definition

**Troubleshooting is the disciplined process of finding why something is not behaving as expected and restoring correct behavior.**

Suppose:

```text
PostgreSQL container is not usable.
```

That is a **symptom**.

Possible causes include:

```text
- process crashed
- startup failed
- configuration is invalid
- storage is unavailable
- permissions are wrong
- service is still initializing
- network connectivity is broken
```

Therefore:

```text
"Container is not working"
```

is not a root cause.

A useful investigation converts a vague symptom into a specific explanation.

---

## 2.2 Symptom

A symptom is what you observe.

Examples:

```text
Connection refused
Container exited
Application keeps restarting
No data appears
Kafka client cannot connect
PostgreSQL is running but queries fail
```

---

## 2.3 Cause

A cause is something that contributes to the observed problem.

Example:

```text
PostgreSQL was not ready when the client connected.
```

---

## 2.4 Root cause

A root cause is the underlying condition that explains the failure sufficiently to prevent recurrence or correctly remediate it.

For example:

```text
PostgreSQL initialization failed because the persistent data directory
contained incompatible state.
```

The downstream symptom might be:

```text
Python application receives connection refused.
```

The connection error is real, but it is not necessarily the root cause.

---

## 2.5 Evidence

Evidence is information you can observe and verify.

Examples:

```text
docker ps -a
docker logs <container>
docker inspect <container>
docker top <container>
docker exec <container> ...
```

Evidence is stronger than assumptions.

---

## 2.6 Hypothesis

A hypothesis is a testable explanation.

For example:

> "I suspect PostgreSQL is running but has not become ready."

Test it with:

```bash
docker exec postgres pg_isready
```

A good hypothesis predicts something observable.

---

## 2.7 Verification

Verification proves that the proposed fix actually solved the problem.

Do not stop at:

```text
"I changed something and the error disappeared."
```

Verify the intended behavior.

For example:

```text
PostgreSQL starts
    ↓
PostgreSQL becomes ready
    ↓
Client connects
    ↓
Test query succeeds
```

---

# 3. Container State vs Application State

One of the most important concepts in Docker troubleshooting is:

```text
Docker/container state
        ≠
Application/service state
```

A container can be:

```text
running
```

while the application inside it is:

```text
starting
not ready
misconfigured
stuck
or unhealthy
```

For example:

```text
Container:
running

Application:
not ready
```

Or:

```text
Container:
exited

Application:
process crashed
```

This explains why:

```bash
docker ps
```

is useful but insufficient.

> **A running container does not automatically mean the application is healthy or ready.**

---

# 4. First-Response Troubleshooting Workflow

When a Data Engineering service fails, resist the temptation to immediately restart or recreate it.

Begin with evidence.

## Step 1 — Check running containers

```bash
docker ps
```

## Step 2 — Check all containers

```bash
docker ps -a
```

## Step 3 — Read logs

```bash
docker logs <container>
```

## Step 4 — Inspect metadata and state

```bash
docker inspect <container>
```

## Step 5 — Inspect from inside, when appropriate

```bash
docker exec <container> ...
```

The first-response pattern is:

```text
Observe
   ↓
Collect evidence
   ↓
Form hypothesis
   ↓
Inspect
   ↓
Test
   ↓
Change one relevant thing
   ↓
Verify
```

### The rule

> **Do not change five things at once.**

If you simultaneously change:

- environment variables,
- volumes,
- ports,
- networks,
- image versions,

you may eventually make the system work but lose the ability to explain why it failed.

That is poor troubleshooting.

---

# 5. `docker ps` and `docker ps -a`

## 5.1 `docker ps`

Run:

```bash
docker ps
```

It shows currently running containers.

Useful information includes:

- container ID
- name
- image
- command
- created time
- status
- ports

Example shape:

```text
CONTAINER ID   IMAGE          COMMAND       STATUS         PORTS
abc123         postgres:16    ...           Up 2 minutes   5432/tcp
```

The important question is:

> Is the container currently running?

---

## 5.2 `docker ps -a`

Run:

```bash
docker ps -a
```

This includes stopped and exited containers.

This is essential when a container appears to have "disappeared" from `docker ps`.

For example:

```text
CONTAINER ID   IMAGE        STATUS
abc123         postgres     Exited (1) ...
```

The container did not disappear.

It stopped.

---

## 5.3 What to inspect

When investigating, look at:

| Field | Why it matters |
|---|---|
| Container ID | Identifies the runtime object |
| Name | Useful for commands |
| Image | Confirms what was launched |
| Command | Helps identify intended process |
| Created time | Helps establish timeline |
| Status | Running, exited, restarting, etc. |
| Ports | Helps establish exposure |

Do not treat this as a complete Docker CLI reference. The purpose is evidence collection.

---

# 6. Container Exit Codes

A simplified process lifecycle is:

```text
Process starts
     ↓
Process runs
     ↓
Process exits
     ↓
Exit code recorded
```

An exit code provides a clue about how the process ended.

## Exit code `0`

Conventionally:

```text
0 = successful process termination
```

A container whose main process exits with code `0` may therefore have completed normally.

That does not necessarily mean the service behaved as a long-running service should. The process may simply have completed its command.

## Non-zero exit codes

A non-zero exit code indicates that the process ended in a way the process/runtime treats as unsuccessful.

But do not invent universal meanings for arbitrary non-zero values.

Use:

```bash
docker ps -a
```

and:

```bash
docker inspect <container>
```

to inspect state and exit information.

Then use:

```bash
docker logs <container>
```

to understand why.

### Professional principle

> **An exit code tells you that a process ended and provides a clue; logs and process context explain why.**

---

# 7. `docker logs`

The first log command to learn is:

```bash
docker logs <container>
```

For example:

```bash
docker logs postgres
```

Logs are often the first detailed evidence source because they show what the main application process reported.

---

## 7.1 Follow logs

For real-time investigation:

```bash
docker logs -f postgres
```

This is useful while:

- a service starts,
- a database initializes,
- Kafka starts,
- an application enters a restart loop,
- a service becomes ready,
- a shutdown occurs.

Stop following with the normal terminal interrupt.

---

## 7.2 Limit output

Instead of reading thousands of lines:

```bash
docker logs --tail 100 postgres
```

This retrieves the most recent 100 lines.

Use a smaller window when you already know approximately when the failure happened.

---

## 7.3 Filter by time

For example:

```bash
docker logs --since 10m postgres
```

This focuses on recent events.

You can combine practical filtering with shell tools where available:

```bash
docker logs postgres 2>&1 | grep -i error
```

But do not assume that searching for the word `error` is enough.

A warning may be important.

A fatal error may not contain the exact word `error`.

A later error may simply be a consequence of an earlier failure.

---

# 8. Logging Mental Model

Understand where `docker logs` gets its information.

```text
Application
    ↓
stdout / stderr
    ↓
Container runtime
    ↓
docker logs
```

This means:

```bash
docker logs <container>
```

does **not** magically inspect every file inside the container.

There is a difference between:

```text
container stdout/stderr
```

and:

```text
application log files inside the filesystem
```

An application could write:

```text
/var/log/application.log
```

without sending the same content to stdout/stderr.

In that case:

```bash
docker logs <container>
```

may not show the application log file.

You may need to inspect the file:

```bash
docker exec <container> cat /var/log/application.log
```

if the container is running and the path exists.

---

# 9. Following Logs During Startup

A common troubleshooting workflow is:

```bash
docker logs -f postgres
```

Then observe the sequence:

```text
container starts
    ↓
configuration is read
    ↓
initialization occurs
    ↓
database starts
    ↓
database becomes ready
```

If startup fails, you want to know **where in the sequence it failed**.

A good investigation asks:

1. What was the first meaningful message?
2. Did initialization complete?
3. Did the service bind/listen?
4. Did readiness occur?
5. Did a dependency fail first?
6. Did the process terminate?

This is much more useful than merely looking for red-looking text.

---

# 10. `docker exec`

`docker exec` runs a new process inside an existing running container.

Basic example:

```bash
docker exec -it <container> sh
```

This opens an interactive shell if the image contains `sh`.

The important concept is:

```text
Existing container
       │
       │ docker exec
       ▼
New diagnostic process
inside the existing container
```

It does **not** create another container.

It does **not** restart the existing application.

It starts an additional process inside the already-running container.

---

## 10.1 Why `exec` is useful

You can inspect:

- environment variables,
- files,
- directories,
- processes,
- service readiness,
- application-specific commands.

Examples:

```bash
docker exec <container> env
```

```bash
docker exec <container> ls -la
```

```bash
docker exec <container> pg_isready
```

The key is to use `exec` purposefully.

---

# 11. Shell and Tool Availability

Not every image contains:

```bash
bash
```

Therefore:

```bash
docker exec -it container bash
```

may fail.

Try:

```bash
docker exec -it container sh
```

when the image provides `sh`.

Minimal images may intentionally omit:

- `bash`
- `ps`
- `curl`
- `nc`
- `nslookup`
- package managers
- editors
- other diagnostic tools

This is not necessarily a problem with the image.

A small runtime image may intentionally contain only what the application needs.

### Professional principle

> **Do not assume every image has the same Linux toolset.**

---

# 12. Targeted `docker exec` Commands

You do not always need an interactive shell.

Often a targeted command is safer and clearer.

## Check environment

```bash
docker exec <container> env
```

## Check one configuration value

```bash
docker exec <container> printenv APP_ENV
```

## Check PostgreSQL readiness

```bash
docker exec postgres pg_isready
```

## Inspect a directory

```bash
docker exec <container> ls -la /path
```

## Read a file

```bash
docker exec <container> cat /path/to/file
```

This gives two styles:

```text
Interactive inspection
```

versus:

```text
Targeted inspection
```

Targeted inspection is often preferable in an incident because the question is explicit:

> "Does this file exist?"

rather than:

> "Let me open a shell and start exploring randomly."

---

# 13. Process Inspection and `docker top`

Troubleshooting sometimes requires knowing whether the expected application process is actually running.

Docker provides:

```bash
docker top <container>
```

For example:

```bash
docker top postgres
```

This can help answer:

- What process is running?
- What command started it?
- Is the expected service process present?

Inside a container, you may also have:

```bash
ps
```

but tool availability depends on the image.

Do not assume `ps` exists.

### Critical mental model

```text
Container running
        ≠
Expected application process healthy
```

A running container can contain a process that is stuck, waiting, misconfigured, or otherwise not serving the intended workload.

---

# 14. PID 1 and Process Lifecycle

The main process in a normal container commonly becomes PID 1 inside that container.

This matters because PID 1 is closely tied to:

- process lifecycle,
- signal handling,
- shutdown,
- termination behavior.

During troubleshooting, it is useful to ask:

```text
What is PID 1?
What command started it?
Is it still running?
How does it respond to termination?
```

The goal here is not to teach Linux init systems.

The operational takeaway is:

> **The lifecycle of the container is strongly connected to the lifecycle of its main process.**

If the main process exits, the container normally stops unless a restart mechanism causes it to be started again.

---

# 15. Filesystem Inspection

When a service is running but behaving incorrectly, inspect its filesystem state.

Examples:

```bash
docker exec <container> ls -la
```

or:

```bash
docker exec <container> ls -la /path
```

Read a relevant file:

```bash
docker exec <container> cat /path/to/file
```

Useful questions include:

- Does the expected file exist?
- Is the path correct?
- Is the directory empty?
- Is a configuration file present?
- Is the data directory mounted?
- Are permissions wrong?
- Is a log file being written somewhere unexpected?

For Data Engineering services, examples include:

```text
configuration files
application directories
database data directories
object-storage data directories
log files
```

Topic 04 covers storage and persistence in depth. Here, filesystem inspection is being used as a diagnostic technique.

---

# 16. Environment and Configuration Inspection

Topic 05 established runtime configuration.

In this module, configuration becomes an evidence source.

For example:

```bash
docker exec <container> env
```

or:

```bash
docker inspect <container>
```

Suppose the application is expected to receive:

```text
DATABASE_HOST=postgres
```

but the actual configuration is:

```text
DATABASE_HOST=localhost
```

That is strong evidence of a configuration problem.

The diagnostic pattern is:

```text
Expected configuration
        vs
Actual configuration
```

Examples of configuration failures:

```text
wrong database host
wrong database name
missing credential
wrong port
wrong log level
```

Do not reteach Topic 05 here. Use configuration inspection only to answer troubleshooting questions.

---

# 17. `docker inspect`

Run:

```bash
docker inspect <container>
```

This returns detailed Docker metadata.

Useful areas include:

- container state,
- exit code,
- startup command,
- environment configuration,
- mounts,
- networking information,
- restart state,
- image information.

The mistake is to dump the entire JSON output and stare at it.

Instead, ask a question.

Examples:

> Did the container exit?

Inspect state.

> What command was started?

Inspect process/command configuration.

> Is the expected volume mounted?

Inspect mounts.

> What environment did Docker configure?

Inspect environment.

> Is the container restarting?

Inspect restart-related state.

Use `docker inspect` as an evidence tool, not as a generic JSON-reading exercise.

### Security reminder

Inspection output may contain sensitive configuration. Avoid sharing raw inspection output publicly without reviewing it.

---

# 18. Health and Readiness

This is a critical Data Engineering concept.

A service can be:

```text
started
```

but not:

```text
ready
```

and it may be:

```text
ready
```

without being fully:

```text
healthy
```

Think of the lifecycle as:

```text
Created
   ↓
Process starts
   ↓
Application initializes
   ↓
Application becomes ready
   ↓
Application serves requests
```

---

## 18.1 PostgreSQL example

A PostgreSQL container may be running while PostgreSQL is still initializing.

Use:

```bash
docker exec postgres pg_isready
```

The result gives a service-specific readiness signal.

Therefore:

```text
docker ps
```

and:

```text
pg_isready
```

answer different questions.

```text
docker ps
    ↓
Is the container running?

pg_isready
    ↓
Is PostgreSQL accepting readiness checks?
```

---

## 18.2 Kafka example

Likewise:

```text
Kafka process started
```

does not necessarily mean:

```text
Kafka client can successfully connect
```

Kafka can be affected by:

- initialization,
- listener configuration,
- advertised addresses,
- network reachability,
- broker readiness.

Topic 03 covers listener/networking behavior in depth. Here, use those concepts as diagnostic dependencies.

---

# 19. Healthcheck Awareness

Docker health checks can provide another signal.

Conceptually:

```text
running
+
health status
+
application readiness
```

are different observations.

A container can be:

```text
running
```

while its health check reports an unhealthy state.

Do not confuse Docker health status with a universal application definition of "healthy."

A health check is a test designed for that image/service.

This module does not teach Dockerfile `HEALTHCHECK` authoring in depth.

The operational skill is knowing that health information can add evidence to your diagnosis.

---

# 20. Startup vs Readiness vs Failure

Use this model:

```text
Container created
       ↓
Process starts
       ↓
Application initializes
       ↓
Application becomes ready
       ↓
Application serves requests
```

Possible failure stages include:

```text
creation failure
startup failure
initialization failure
readiness failure
runtime failure
```

Examples:

### Startup failure

The main process exits immediately.

### Initialization failure

PostgreSQL starts but cannot initialize its database state.

### Readiness failure

The process remains alive but the service is not yet accepting connections.

### Runtime failure

The service becomes ready and later crashes or stops behaving correctly.

Logs, process inspection, readiness checks, and client tests help identify which stage failed.

---

# 21. Restart Loops

A restart loop looks conceptually like:

```text
Container starts
      ↓
Application crashes
      ↓
Container exits
      ↓
Restart
      ↓
Application crashes
      ↓
Repeat
```

The danger is responding by repeatedly restarting the service without collecting evidence.

Instead:

```bash
docker ps -a
```

Then:

```bash
docker logs <container>
```

Then:

```bash
docker inspect <container>
```

Ask:

1. What process is failing?
2. What is the exit state?
3. What was the first meaningful log message?
4. What configuration was present?
5. What changed before the restart loop began?

### Professional rule

> **A restart loop is evidence of a recurring failure, not a reason to keep restarting blindly.**

---

# 22. Common Startup Failure Categories

A useful diagnostic taxonomy is:

## 22.1 Configuration failure

Examples:

```text
missing environment variable
invalid value
incorrect credentials
wrong service endpoint
```

Evidence may come from:

```bash
docker inspect
docker exec ... env
docker logs
```

---

## 22.2 Storage failure

Examples:

```text
wrong mount
permission problem
incorrect data directory
unexpected existing state
```

Evidence may come from:

```bash
docker inspect
docker exec ... ls -la
docker logs
```

---

## 22.3 Networking failure

Examples:

```text
wrong hostname
wrong port
service unreachable
DNS problem
```

Evidence may come from:

```bash
docker network inspect
```

and suitable diagnostic containers/tools.

---

## 22.4 Dependency failure

Examples:

```text
database not ready
Kafka dependency unavailable
object-storage service unavailable
```

A service can be correctly configured while its dependency is unavailable.

---

## 22.5 Application failure

Examples:

```text
application exception
invalid initialization
incompatible state
```

Logs and process inspection are often primary evidence.

---

## 22.6 Resource failure

Examples:

```text
memory exhaustion
disk exhaustion
```

Resource limits are covered later in the roadmap, so here treat them as a possible diagnostic category rather than a full resource-management lesson.

---

# 23. Network Troubleshooting

Topic 03 is the networking prerequisite.

Do not relearn the whole networking curriculum here.

Instead, use this troubleshooting chain:

```text
Client location
    ↓
Hostname
    ↓
DNS
    ↓
Port
    ↓
Network membership
    ↓
TCP connectivity
    ↓
Application readiness
```

For example, if a Python client cannot connect to PostgreSQL, ask:

1. Where is the client running?
2. What hostname is it using?
3. Does that hostname resolve in the client's network context?
4. Is the port correct?
5. Are the containers on the expected network?
6. Is TCP connectivity possible?
7. Is PostgreSQL actually ready?

Useful diagnostic commands can include:

```bash
docker network inspect <network>
```

and, in an appropriate environment:

```bash
nslookup <hostname>
```

```bash
nc -vz <hostname> <port>
```

```bash
curl http://<hostname>:<port>
```

Use only tools that exist in the diagnostic environment.

If the service image is minimal, use a temporary diagnostic container.

---

# 24. Storage Troubleshooting

Topic 04 is the storage prerequisite.

Use the following diagnostic questions:

```text
Is the volume mounted?
Is the mount path correct?
Is the directory empty?
Are permissions correct?
Is the application reading the expected path?
```

Inspect mounts:

```bash
docker inspect <container>
```

Inspect filesystem state:

```bash
docker exec <container> ls -la /path
```

The purpose is not to reteach volume mechanics.

The purpose is to answer:

> **Does the runtime storage state explain the observed failure?**

---

# 25. Configuration Troubleshooting

Topic 05 is the configuration prerequisite.

The central diagnostic comparison is:

```text
Expected configuration
        vs
Actual configuration
```

Example:

```text
Expected:
DATABASE_HOST=postgres

Actual:
DATABASE_HOST=localhost
```

The application may then fail because the runtime configuration does not match the intended architecture.

Inspect:

```bash
docker exec <container> printenv DATABASE_HOST
```

or:

```bash
docker inspect <container>
```

The important lesson is:

> **When behavior is wrong, inspect the configuration the process actually received rather than the configuration you remember supplying.**

---

# 26. PostgreSQL Troubleshooting

Consider this incident:

```text
PostgreSQL container is running,
but the application cannot connect.
```

Do not immediately recreate PostgreSQL.

Use an evidence sequence.

## Step 1 — Check container state

```bash
docker ps
```

If it is missing:

```bash
docker ps -a
```

---

## Step 2 — Read logs

```bash
docker logs postgres
```

Look for:

- initialization errors,
- configuration errors,
- permission errors,
- shutdown messages,
- readiness messages.

---

## Step 3 — Check readiness

```bash
docker exec postgres pg_isready
```

Now you have a service-level signal.

---

## Step 4 — Inspect configuration

```bash
docker exec postgres printenv
```

Review only what is needed, especially avoiding exposure of passwords.

---

## Step 5 — Inspect container metadata

```bash
docker inspect postgres
```

Check:

- mounts,
- state,
- network information,
- configured environment,
- restart behavior.

---

## Step 6 — Check network path

If the client is another container, verify its network context and hostname.

Topic 03 provides the full networking curriculum.

---

## Step 7 — Check storage if initialization looks wrong

If PostgreSQL reports an unexpected database state, inspect mounts and persistent data assumptions.

Topic 04 provides the full persistence curriculum.

---

## Step 8 — Verify

A successful fix should result in:

```text
PostgreSQL running
        ↓
PostgreSQL ready
        ↓
Client reaches PostgreSQL
        ↓
Test query succeeds
```

---

# 27. MinIO Troubleshooting

Suppose a Data Engineering application cannot use MinIO.

Use:

```text
container state
    ↓
logs
    ↓
configuration
    ↓
readiness
    ↓
endpoint behavior
    ↓
connectivity
    ↓
credentials
```

Start with:

```bash
docker ps -a
```

Then:

```bash
docker logs <minio-container>
```

Inspect runtime configuration:

```bash
docker inspect <minio-container>
```

If the container is running:

```bash
docker exec <minio-container> env
```

Inspect the relevant storage path if initialization or persistence is suspect.

The key is to distinguish:

```text
service not started
```

from:

```text
service started but client cannot connect
```

and:

```text
service reachable but authentication fails
```

These are different failure classes.

---

# 28. Redis Troubleshooting

A concise Redis workflow is:

```text
Container state
    ↓
Logs
    ↓
Process state
    ↓
Configuration
    ↓
Client connectivity
    ↓
Readiness
```

Start:

```bash
docker ps -a
```

Then:

```bash
docker logs redis
```

If running:

```bash
docker exec redis redis-cli ping
```

when the image/container provides the Redis CLI.

A successful response such as:

```text
PONG
```

is evidence that the Redis server responds to that check.

It does not prove every application-level client configuration is correct.

---

# 29. Kafka Troubleshooting

Kafka deserves more careful reasoning because multiple layers can fail.

Start with:

```bash
docker ps -a
```

Then:

```bash
docker logs <kafka-container>
```

Check whether the broker completed startup.

Then inspect configuration:

```bash
docker inspect <kafka-container>
```

Relevant configuration may include:

- broker settings,
- listeners,
- advertised addresses.

Then reason about the client location:

```text
Kafka listener configuration
        +
advertised address
        +
client location
        +
network
        +
port
```

A Kafka client may receive a connection failure even when the broker process itself is running.

For example:

```text
Broker starts
    ↓
Client reaches bootstrap endpoint
    ↓
Broker advertises an address
    ↓
Client attempts advertised address
    ↓
Advertised address is unreachable
    ↓
Client fails
```

This is why a Kafka connection problem cannot always be solved by checking only whether the container is running.

Topic 03 covers the full listener/networking model. Here, the focus is diagnosis.

---

# 30. Temporary Diagnostic Containers

A professional technique is to use a temporary container for diagnostics.

Conceptually:

```text
Production/data service container
          │
          │ do not mutate unnecessarily
          ▼
Temporary diagnostic container
          │
          ├── DNS check
          ├── TCP check
          ├── HTTP check
          └── connectivity test
```

Why?

Because production-oriented service images may intentionally be minimal.

You may need:

```text
curl
nc
nslookup
```

but the application image may not contain them.

Instead of modifying the application container, create a temporary diagnostic environment with the tools you need.

For example, a helper image can be attached to the same relevant network and used to test:

```text
DNS resolution
TCP reachability
HTTP/API reachability
```

The exact helper image can vary. The important pattern is:

> **Use a disposable diagnostic environment rather than mutating the service image simply to debug it.**

---

# 31. Do Not "Fix" by Installing Random Tools

Suppose a service container does not contain `curl`.

A weak response is:

```text
Install curl into the running container.
```

This mutates the runtime environment and can make the incident harder to reproduce.

A better approach is:

```text
Service container
    │
    │ remains unchanged
    ▼
Temporary diagnostic container
    │
    ├── curl
    ├── nc
    └── nslookup
```

This reinforces:

- reproducibility,
- clean service environments,
- separation of application runtime and diagnostic tooling.

The rule is:

> **Do not mutate the running service container unnecessarily just because debugging tools are missing.**

---

# 32. Log Interpretation and Causal Reasoning

Logs are evidence, not an answer key.

A log stream can contain:

```text
INFO
WARNING
ERROR
fatal startup messages
stack traces
repeated messages
```

Do not assume every `ERROR` is the root cause.

For example:

```text
Database initialization failed
        ↓
Database never becomes ready
        ↓
Python application gets connection refused
        ↓
Pipeline fails
```

The final application message might be:

```text
Connection refused
```

But the database initialization failure happened first.

### Professional principle

> **Find the earliest meaningful failure in the sequence.**

---

# 33. First Failure vs Downstream Failure

Consider:

```text
PostgreSQL initialization failure
        ↓
PostgreSQL never becomes ready
        ↓
Python application gets connection refused
        ↓
Pipeline fails
```

The observed symptom is:

```text
pipeline failed
```

A downstream error is:

```text
connection refused
```

The primary failure is:

```text
PostgreSQL initialization failed
```

The root cause may be further upstream:

```text
incompatible persistent state
```

A useful mental model is:

```text
Root cause
   ↓
Primary failure
   ↓
Secondary failure
   ↓
Observed symptom
```

This prevents you from "fixing" the final symptom while leaving the underlying problem intact.

---

# 34. Troubleshooting Decision Tree

Use this decision tree as a repeatable framework.

```text
Is the container running?
        │
      NO
        │
        ▼
Check docker ps -a
        │
        ▼
Check exit state
        │
        ▼
Check logs
```

If the container is running:

```text
Container running?
        │
       YES
        │
        ▼
Is the application ready?
        │
      NO
        │
        ▼
Check logs
Check health/readiness
Check configuration
Check storage
```

If the application is ready:

```text
Application ready?
        │
       YES
        │
        ▼
Can the client connect?
        │
      NO
        │
        ▼
Check hostname
Check DNS
Check network
Check port
Check advertised address
```

If the client can connect but the workload still fails:

```text
Check application-level behavior
        ↓
Check data/state assumptions
        ↓
Check dependencies
        ↓
Check recent changes
```

This is a decision framework, not a rigid script.

---

# 35. Incident Timeline

Timestamps help establish causality.

Build a simple timeline:

```text
12:01 container started
12:01 configuration loaded
12:01 database initialization began
12:02 initialization failed
12:02 readiness failed
12:02 client connection failed
```

Now you can reason:

```text
Initialization failure
        happened before
client connection failure
```

Therefore the connection error may be downstream.

A timeline can be built from:

- Docker timestamps,
- log timestamps,
- deployment/change timestamps,
- command history,
- monitoring observations.

The goal is to answer:

> **What happened first?**

---

# 36. Troubleshooting Without Destroying Evidence

One of the most important operational habits is:

> **Do not immediately delete/recreate a broken container before collecting evidence.**

Why?

Because the failed container may contain:

- useful logs,
- exit status,
- configuration,
- filesystem state,
- mount information,
- process state.

A safer sequence is:

```text
Inspect
   ↓
Capture evidence
   ↓
Diagnose
   ↓
Fix
   ↓
Recreate only when appropriate
```

Recreation may eventually be the right fix.

But it should be an informed action.

---

# 37. Reproducing Failures

A professional engineer asks:

> **Can I reproduce the problem?**

Controlled reproduction is more useful than random experimentation.

Examples:

### Configuration failure

Set:

```text
DATABASE_HOST=wrong-host
```

and reproduce the connection failure.

### Storage failure

Use an intentionally incorrect mount configuration in a disposable lab.

### Network failure

Place a diagnostic client in a different network context.

### Readiness failure

Start the client before the dependency is ready and observe the behavior.

The purpose is to isolate one variable at a time.

---

# 38. Break/Fix Lab

This lab intentionally creates failures.

For every failure, use:

```text
Symptom
   ↓
Evidence
   ↓
Hypothesis
   ↓
Test
   ↓
Root cause
   ↓
Fix
   ↓
Verification
```

Do not skip the evidence step.

---

## Failure 1 — Container exits immediately

### Symptom

The expected service is not in:

```bash
docker ps
```

### Evidence

```bash
docker ps -a
```

Then:

```bash
docker logs <container>
```

And:

```bash
docker inspect <container>
```

### Questions

- What is the exit status?
- What command was started?
- What is the first meaningful log message?

### Fix

Address the actual root cause.

### Verification

Start the service again and verify both process state and application readiness.

---

## Failure 2 — Application starts but is not ready

### Symptom

```text
docker ps
```

shows the container running.

But the client cannot connect.

### Hypothesis

The application may still be initializing.

### Evidence

```bash
docker logs -f <container>
```

Use an application-specific readiness check where available.

For PostgreSQL:

```bash
docker exec postgres pg_isready
```

### Fix

Do not automatically modify configuration. First determine whether the service simply needs time or whether initialization has failed.

---

## Failure 3 — Wrong environment variable

Expected:

```text
DATABASE_HOST=postgres
```

Actual:

```text
DATABASE_HOST=localhost
```

Inspect:

```bash
docker exec <container> printenv DATABASE_HOST
```

### Root cause

Actual runtime configuration does not match intended configuration.

### Verification

Correct the configuration and verify the resulting connection.

---

## Failure 4 — Wrong volume mount

### Symptom

The application cannot find expected data.

### Evidence

```bash
docker inspect <container>
```

Check mounts.

Then:

```bash
docker exec <container> ls -la /expected/path
```

### Questions

- Is the mount present?
- Is the path correct?
- Is the directory empty?
- Is the application reading that exact path?

---

## Failure 5 — Permission denied

### Symptom

Logs report permission-related errors.

### Evidence

Inspect:

```bash
docker exec <container> ls -la /path
```

If available:

```bash
docker exec <container> id
```

### Reasoning

Compare:

```text
process identity
```

with:

```text
filesystem ownership/permissions
```

Do not "fix" permissions blindly with broad, unsafe changes.

---

## Failure 6 — DNS/service discovery failure

### Symptom

A client cannot resolve a service hostname.

### Hypothesis

The client may not be on the expected Docker network.

### Evidence

```bash
docker network inspect <network>
```

Then use a temporary diagnostic container to perform a DNS lookup if appropriate:

```bash
nslookup <service-name>
```

### Root cause

Possibilities include:

- wrong network,
- wrong service/container name,
- DNS context mismatch.

---

## Failure 7 — Port/connectivity problem

### Symptom

The service appears running, but a client cannot establish a TCP connection.

### Evidence

Use a suitable diagnostic environment:

```bash
nc -vz <hostname> <port>
```

Check network membership:

```bash
docker network inspect <network>
```

### Reasoning

Separate:

```text
DNS failure
```

from:

```text
TCP connection failure
```

from:

```text
application readiness failure
```

---

## Failure 8 — PostgreSQL initialization issue

### Symptom

PostgreSQL is running but does not contain expected initial state.

### Evidence

```bash
docker logs postgres
```

Then:

```bash
docker inspect postgres
```

Inspect mounts and persistent state assumptions.

### Root cause possibilities

- data directory was already initialized,
- initialization configuration was misunderstood,
- storage points to unexpected state,
- initialization failed.

Do not delete persistent data simply to make the lab appear to work.

---

## Failure 9 — Kafka listener problem

Trace the connection:

```text
Client location
      ↓
Bootstrap address
      ↓
Kafka broker
      ↓
Advertised address
      ↓
Client attempts advertised address
      ↓
Network/port reachability
```

Inspect configuration:

```bash
docker inspect <kafka-container>
```

Read logs:

```bash
docker logs <kafka-container>
```

The objective is to identify which layer is wrong.

---

## Failure 10 — Restart loop

### Symptom

The container repeatedly starts and stops.

### Evidence

```bash
docker ps -a
```

Then:

```bash
docker logs <container>
```

Then:

```bash
docker inspect <container>
```

### Root cause

Find the first meaningful failure.

Do not treat the restart itself as the root cause.

---

# 39. Real-World Data Engineering Scenarios

## Scenario 1 — Morning pipeline failure

At 08:00, an ingestion pipeline cannot connect to PostgreSQL.

PostgreSQL appears to be running.

### Investigation

```bash
docker ps
```

Then:

```bash
docker logs postgres
```

Then:

```bash
docker exec postgres pg_isready
```

Then inspect the client configuration.

Questions:

- Is PostgreSQL ready?
- Is the hostname correct?
- Is the client on the correct network?
- Did PostgreSQL fail initialization?
- Did anything change before 08:00?

---

## Scenario 2 — Empty database after restart

A learner restarts a PostgreSQL stack and finds the expected data missing.

Possible categories:

```text
persistence
wrong volume
initialization
configuration
```

Investigate:

```bash
docker inspect postgres
```

and inspect the data path.

Do not assume the application "lost data" until the actual storage state is verified.

---

## Scenario 3 — Kafka producer cannot connect

The Kafka container is:

```text
running
```

but the producer fails.

Investigate:

```text
broker startup
    ↓
broker readiness
    ↓
listener configuration
    ↓
advertised address
    ↓
client location
    ↓
network path
```

Do not stop at:

```bash
docker ps
```

---

## Scenario 4 — MinIO client failure

A Python application cannot use MinIO.

Separate:

```text
service startup
```

from:

```text
endpoint configuration
```

from:

```text
connectivity
```

from:

```text
credentials
```

Use logs and runtime configuration as evidence.

---

## Scenario 5 — Container constantly restarting

The application container repeatedly restarts.

A weak approach is:

```bash
docker restart app
```

again and again.

A better approach is:

```bash
docker ps -a
docker logs app
docker inspect app
```

Then identify the first recurring failure.

---

## Scenario 6 — Application says "connection refused"

Treat:

```text
connection refused
```

as a symptom.

Possible underlying causes:

```text
service not running
service not ready
wrong hostname
wrong port
wrong network
listener problem
application initialization failure
```

The message tells you that a connection attempt failed.

It does not automatically tell you why.

---

# 40. Professional Troubleshooting Checklist

Use this checklist during incidents:

```text
[ ] What exactly is failing?
[ ] Is the container running?
[ ] Did the process exit?
[ ] What is the exit code?
[ ] What do the logs say?
[ ] What was the first meaningful error?
[ ] Is the application ready?
[ ] What configuration is actually present?
[ ] Is the expected process running?
[ ] Is storage mounted correctly?
[ ] Are permissions correct?
[ ] Is the service reachable?
[ ] Is DNS correct?
[ ] Is the port correct?
[ ] Is the dependency ready?
[ ] Can the failure be reproduced?
[ ] What changed?
[ ] What is the root cause?
[ ] Did the fix actually work?
[ ] Did I document what happened?
```

The checklist is deliberately ordered from broad observation toward increasingly specific diagnosis.

---

# 41. Command Reference

This is a troubleshooting-focused reference, not a complete Docker CLI manual.

| Command | Purpose | Example | Expected behavior | When to use |
|---|---|---|---|---|
| `docker ps` | List running containers | `docker ps` | Shows active containers | First response |
| `docker ps -a` | List all containers | `docker ps -a` | Includes exited containers | Investigating stopped/missing containers |
| `docker logs` | Read container stdout/stderr | `docker logs postgres` | Shows available log stream | Startup/runtime failures |
| `docker logs -f` | Follow logs | `docker logs -f postgres` | Streams new log lines | Startup/readiness/restart investigation |
| `docker logs --tail` | Limit recent logs | `docker logs --tail 100 postgres` | Shows last 100 lines | Large logs |
| `docker logs --since` | Filter recent time window | `docker logs --since 10m postgres` | Shows recent logs | Time-focused incidents |
| `docker inspect` | Inspect container metadata | `docker inspect postgres` | Detailed runtime state/config | State, mounts, environment, networking |
| `docker exec` | Run a process inside a running container | `docker exec postgres pg_isready` | Executes command | Targeted inspection |
| `docker exec -it ... sh` | Open interactive shell | `docker exec -it app sh` | Interactive shell if available | Exploratory inspection |
| `docker top` | Inspect container processes | `docker top postgres` | Shows processes | Process diagnosis |
| `docker stats` | Observe resource usage | `docker stats postgres` | Live resource metrics | Resource symptom awareness |
| `docker port` | Show published ports | `docker port postgres` | Shows port mappings | Host/container exposure checks |
| `docker network inspect` | Inspect network membership/config | `docker network inspect data-lab` | Network details | Connectivity diagnosis |
| `docker volume inspect` | Inspect a volume | `docker volume inspect postgres_data` | Volume metadata | Storage diagnosis |
| `docker restart` | Restart container | `docker restart postgres` | Stops/starts container | Only after evidence collection or when appropriate |
| `docker stop` | Stop container | `docker stop postgres` | Stops container | Controlled shutdown |
| `docker start` | Start stopped container | `docker start postgres` | Starts existing container | Recovery after investigation |

### Service-level diagnostic example

PostgreSQL:

```bash
pg_isready
```

From inside the container:

```bash
docker exec postgres pg_isready
```

This provides an application/service-level readiness signal rather than only a Docker container-state signal.

---

# 42. Common Mistakes

## 1. Looking only at `docker ps`

**Why it happens:** Running looks like success.

**Problem:** The application may not be ready or healthy.

**Better:** Combine:

```bash
docker ps
docker logs
readiness check
```

---

## 2. Assuming running means ready

A running process may still be initializing.

Use service-specific readiness checks where available.

---

## 3. Restarting repeatedly without collecting evidence

Restarting can destroy useful context and does not explain the failure.

Collect evidence first.

---

## 4. Reading only the final log line

The final error may be downstream.

Search backward for the earliest meaningful failure.

---

## 5. Ignoring the first meaningful error

For example:

```text
database initialization failed
        ↓
connection refused
```

The connection refusal may be secondary.

---

## 6. Deleting a failed container before inspecting it

You may lose useful evidence.

Inspect first.

---

## 7. Assuming every image contains `bash`

Minimal images may provide only:

```bash
sh
```

or no shell suitable for interactive diagnosis.

---

## 8. Assuming every image contains `ps`, `curl`, `nc`, or debugging tools

Use a temporary diagnostic container when appropriate.

---

## 9. Installing random tools into production/data containers

This mutates the runtime environment.

Prefer external diagnostics.

---

## 10. Confusing configuration failure with network failure

A wrong hostname can look like a network issue.

Inspect actual configuration.

---

## 11. Confusing network failure with readiness failure

A service can be reachable at the network layer but not ready at the application layer.

---

## 12. Confusing storage failure with application failure

An application may be behaving correctly but reading an unexpected or inaccessible data directory.

---

## 13. Ignoring permissions

A file can exist but still be inaccessible to the process.

---

## 14. Ignoring persistent state during database troubleshooting

Existing state can explain surprising initialization behavior.

---

## 15. Treating `connection refused` as a root cause

It is a symptom of a failed connection attempt.

Find out why the target refused or could not accept the connection.

---

## 16. Changing multiple things simultaneously

If you change:

```text
hostname
port
volume
network
environment
```

at once, you cannot reliably determine which change fixed the problem.

---

## 17. Not verifying the fix

A command completing successfully does not necessarily prove the service is healthy.

Test the actual intended behavior.

---

## 18. Not documenting what changed

If the incident is not documented, the same problem may be rediscovered later.

---

# 43. Mental Models

## Mental Model 1 — Running ≠ Ready

```text
Running
   ≠
Ready
```

A process can be alive while the application is still initializing or unable to serve requests.

---

## Mental Model 2 — Container State ≠ Application Health

```text
Container state
      ≠
Application health
```

Docker tells you about the container. Application-specific checks tell you about the service.

---

## Mental Model 3 — Logs = Evidence

```text
Logs
=
Evidence
```

Logs are observations that help test hypotheses.

They are not automatically the root cause.

---

## Mental Model 4 — `docker exec` = Inspect the Existing Container

```text
docker exec
=
inspect/run a process inside the existing running container
```

It does not create a new container.

---

## Mental Model 5 — Symptom ≠ Root Cause

```text
Symptom
   ≠
Root cause
```

For example:

```text
connection refused
```

may be caused by:

```text
database initialization failure
```

---

## Mental Model 6 — First Meaningful Failure > Last Visible Error

```text
First meaningful failure
        >
Last visible error
```

Downstream systems often report consequences of upstream failures.

---

## Mental Model 7 — Troubleshooting = Hypothesis Testing

```text
Troubleshooting
=
hypothesis testing
```

A professional investigation asks:

> What do I think is wrong, what evidence would support it, and what evidence would disprove it?

---

## Mental Model 8 — Temporary Diagnostic Container > Mutating Service Container

```text
Temporary diagnostic container
        >
mutating application container for debugging
```

This preserves reproducibility and keeps the application runtime clean.

---

# 44. ASCII Diagrams

## Container state vs application state

```text
                 Container
              ┌───────────────┐
              │               │
              │ Docker State  │
              │               │
              │ running       │
              │ exited        │
              │ restarting    │
              │               │
              └───────┬───────┘
                      │
                      │ contains
                      ▼
              ┌───────────────┐
              │ Application   │
              │               │
              │ starting      │
              │ ready         │
              │ failed        │
              │ unhealthy     │
              └───────────────┘
```

---

## Evidence-driven troubleshooting

```text
Symptom
   ↓
Collect logs
   ↓
Inspect state
   ↓
Check readiness
   ↓
Check config
   ↓
Check storage
   ↓
Check connectivity
   ↓
Identify root cause
   ↓
Fix
   ↓
Verify
```

---

## Diagnostic surfaces

```text
Application
    │
    ├── stdout/stderr
    │       ↓
    │   docker logs
    │
    ├── process
    │       ↓
    │   docker top / exec
    │
    ├── filesystem
    │       ↓
    │   docker exec
    │
    └── runtime metadata
            ↓
        docker inspect
```

---

## Incident causality

```text
Root Cause
    ↓
Primary Failure
    ↓
Secondary Failure
    ↓
Observed Symptom
```

Your job is to move upward in this chain until you can explain the root cause.

---

# 45. Practice Questions

## Beginner

1. What is troubleshooting?
2. What is a symptom?
3. What is a root cause?
4. What does `docker ps` show?
5. What does `docker ps -a` show?
6. What does `docker logs` do?
7. What does `docker exec` do?
8. Why might a container not appear in `docker ps`?

## Intermediate

1. Why can a running container still be unusable?
2. What is the difference between stdout/stderr and application log files?
3. How do you investigate a container that exited?
4. How do you inspect environment variables?
5. How do you inspect mounts?
6. How do you determine whether a service is ready?
7. Why might `bash` not exist in a container?
8. Why should you avoid repeatedly restarting a failing container?
9. What does `docker inspect` help you determine?
10. Why is `connection refused` not automatically a root cause?

## Advanced

1. How would you troubleshoot a PostgreSQL container that is running but rejecting connections?
2. How would you diagnose a restart loop?
3. How would you distinguish a configuration problem from a networking problem?
4. Why should you inspect the first meaningful failure?
5. Why can a temporary troubleshooting container be better than modifying the application container?
6. How would you investigate a Kafka connection failure?
7. How would you preserve evidence during an incident?
8. How would you construct a timeline for a failed Data Engineering pipeline?
9. How would you prove that a proposed fix actually solved the problem?
10. How would you determine whether a connection error is caused by service readiness, DNS, TCP reachability, or application configuration?

These questions test reasoning rather than memorization.

---

# 46. Interview Practice

## 1. What is your standard workflow for troubleshooting a Docker container?

**Strong answer:**

I first define the exact symptom, then inspect `docker ps` and `docker ps -a`, collect logs, inspect container state and configuration, and determine whether the application is actually ready. I form a specific hypothesis, test it with targeted evidence, change one relevant thing, and verify the result. I document the root cause and resolution.

---

## 2. What is the difference between `docker ps` and `docker ps -a`?

**Strong answer:**

`docker ps` shows running containers. `docker ps -a` includes stopped and exited containers, so it is essential when a service is no longer running.

---

## 3. How do you troubleshoot a container that exits immediately?

**Strong answer:**

I use `docker ps -a` to inspect the status and exit information, then `docker logs <container>` to identify the process failure and `docker inspect <container>` for state, command, environment, mounts, and other relevant metadata. I do not recreate the container before collecting evidence unless there is a compelling operational reason.

---

## 4. How do you use `docker logs` effectively?

**Strong answer:**

I start with `docker logs`, then narrow the investigation with `--tail`, `--since`, and `-f` when monitoring startup or runtime behavior. I focus on the sequence of events and the first meaningful failure rather than blindly searching for the word "error."

---

## 5. What is `docker exec` used for?

**Strong answer:**

`docker exec` runs a new process inside an existing running container. It is useful for targeted inspection of environment variables, files, readiness commands, or application-specific diagnostics.

---

## 6. What if the container does not have `bash`?

**Strong answer:**

I check whether `sh` exists. If the image is intentionally minimal and lacks useful diagnostic tools, I use targeted commands where available or a temporary diagnostic container rather than modifying the application container unnecessarily.

---

## 7. How do you inspect the main process?

**Strong answer:**

I can use `docker top <container>` and, when available, process inspection tools inside the container. I also inspect the startup command and understand that the main container process commonly runs as PID 1.

---

## 8. How do you distinguish "running" from "ready"?

**Strong answer:**

Container state tells me whether the process is running. Readiness is an application/service-level property. For example, I can use `pg_isready` to check whether PostgreSQL is accepting readiness checks even when the container is already running.

---

## 9. How would you troubleshoot PostgreSQL in Docker?

**Strong answer:**

I would check container state, read logs, run `pg_isready`, inspect configuration and mounts, verify network reachability from the client, and check persistent state if initialization behavior is unexpected. I would test the actual client connection only after identifying which layer appears to be failing.

---

## 10. How would you troubleshoot Kafka in Docker?

**Strong answer:**

I would first verify broker startup and logs, then inspect the listener and advertised-address configuration, determine where the client is running, and trace the client path through the advertised address, network, and port. A running Kafka container does not prove that every client can connect.

---

## 11. What information does `docker inspect` provide?

**Strong answer:**

It provides detailed container metadata including state, exit information, command configuration, environment, mounts, networking details, restart state, and image information. I use it to answer a specific diagnostic question rather than reading the entire JSON blindly.

---

## 12. Why should you not immediately delete a failed container?

**Strong answer:**

The failed container may contain useful evidence such as logs, exit state, configuration, mounts, and filesystem state. I preserve and inspect that evidence before taking destructive action.

---

## 13. What is the difference between a symptom and root cause?

**Strong answer:**

A symptom is what I observe, such as `connection refused`. The root cause is the underlying condition that explains the failure, such as PostgreSQL initialization failing because of incompatible persistent state.

---

## 14. How do you diagnose a restart loop?

**Strong answer:**

I inspect `docker ps -a`, collect logs, inspect container state, identify the first recurring meaningful failure, and determine why the main process exits. I avoid repeatedly restarting without learning anything new.

---

## 15. How would you debug a networking problem without modifying the application container?

**Strong answer:**

I inspect Docker network membership and use a temporary diagnostic container attached to the relevant network. From there I can test DNS, TCP connectivity, or HTTP behavior using appropriate tools.

---

## 16. Why is evidence collection important before changing configuration?

**Strong answer:**

Without evidence, troubleshooting becomes trial and error. Evidence allows me to test a specific hypothesis and preserve the information needed to explain the root cause.

---

## 17. How would you troubleshoot a pipeline that suddenly cannot connect to its database?

**Strong answer:**

I would first establish whether the database container is running, read its logs, check readiness, inspect the client's actual database configuration, verify network and DNS reachability, check ports, and review recent changes. I would determine whether the database failed, the client configuration changed, or the network path broke.

---

## 18. How would you document the root cause and resolution?

**Strong answer:**

I would document the symptom, evidence collected, timeline, tested hypotheses, root cause, exact corrective change, verification results, and any follow-up prevention. The record should allow another engineer to reproduce the reasoning.

---

# 47. Final Knowledge Check

You should now be able to explain these in your own words:

1. What is troubleshooting?
2. What is the difference between container state and application state?
3. What does `docker ps -a` reveal?
4. How do you troubleshoot an exited container?
5. How does `docker logs` work?
6. What is the difference between stdout/stderr and application log files?
7. What does `docker exec` do?
8. Why might `bash` not exist?
9. How do you inspect processes?
10. How do you inspect container configuration?
11. How do you determine whether a service is ready?
12. How do you diagnose a restart loop?
13. How do you investigate storage problems?
14. How do you investigate configuration problems?
15. How do you investigate network problems?
16. How would you troubleshoot PostgreSQL?
17. How would you troubleshoot Kafka?
18. Why is the first meaningful failure important?
19. Why should evidence be collected before destructive actions?
20. What is the difference between symptom, cause, and root cause?
21. Why are temporary diagnostic containers useful?
22. What does a professional troubleshooting workflow look like?

A strong learner should be able to explain the reasoning behind each answer, not merely name a Docker command.

---

# 48. Module Completion Checklist

## Troubleshooting fundamentals

- [ ] I can explain troubleshooting in my own words.
- [ ] I can distinguish symptom, cause, root cause, evidence, hypothesis, and verification.
- [ ] I understand why a running container is not necessarily a ready application.
- [ ] I can follow an evidence-first troubleshooting workflow.
- [ ] I avoid changing multiple variables simultaneously.

## Container inspection

- [ ] I can use `docker ps`.
- [ ] I can use `docker ps -a`.
- [ ] I can interpret container status.
- [ ] I can inspect exit information.
- [ ] I can use `docker inspect`.
- [ ] I can use `docker top`.
- [ ] I understand the importance of the main process/PID 1.

## Logs

- [ ] I can use `docker logs`.
- [ ] I can follow logs with `-f`.
- [ ] I can limit logs with `--tail`.
- [ ] I can filter logs with `--since`.
- [ ] I understand stdout/stderr versus internal log files.
- [ ] I can identify the first meaningful failure.

## Exec and filesystem inspection

- [ ] I can use `docker exec`.
- [ ] I understand interactive versus targeted inspection.
- [ ] I know that `bash` may not exist.
- [ ] I can use `sh` when available.
- [ ] I can inspect environment variables.
- [ ] I can inspect files and directories.
- [ ] I can run service-specific readiness commands.

## Readiness and service troubleshooting

- [ ] I can distinguish started, ready, and healthy.
- [ ] I can diagnose a restart loop.
- [ ] I can troubleshoot PostgreSQL systematically.
- [ ] I can troubleshoot MinIO systematically.
- [ ] I can troubleshoot Redis systematically.
- [ ] I can troubleshoot Kafka systematically.
- [ ] I can distinguish configuration, storage, networking, dependency, and application failures.

## Professional diagnosis

- [ ] I can formulate a testable hypothesis.
- [ ] I can use a temporary diagnostic container.
- [ ] I preserve evidence before destructive actions.
- [ ] I can construct an incident timeline.
- [ ] I can reproduce a failure in a controlled way.
- [ ] I verify the fix.
- [ ] I can document the root cause and resolution.

---

# 49. Roadmap Coverage Audit

| Topic 06 requirement | Covered |
|---|---:|
| Troubleshooting fundamentals | Yes |
| Symptom/cause/root cause/evidence/hypothesis | Yes |
| Container vs application state | Yes |
| First-response workflow | Yes |
| `docker ps` / `docker ps -a` | Yes |
| Exit codes | Yes |
| `docker logs` | Yes |
| Following/filtering logs | Yes |
| stdout/stderr vs internal log files | Yes |
| `docker exec` | Yes |
| Shell/tool availability | Yes |
| Targeted exec commands | Yes |
| Process inspection | Yes |
| PID 1 | Yes |
| Filesystem inspection | Yes |
| Environment/configuration inspection | Yes |
| `docker inspect` | Yes |
| Health/readiness | Yes |
| Startup/readiness/failure distinction | Yes |
| Restart loops | Yes |
| Failure taxonomy | Yes |
| Network troubleshooting | Yes |
| Storage troubleshooting | Yes |
| Configuration troubleshooting | Yes |
| PostgreSQL troubleshooting | Yes |
| MinIO troubleshooting | Yes |
| Redis troubleshooting | Yes |
| Kafka troubleshooting | Yes |
| Temporary diagnostic containers | Yes |
| Avoiding runtime mutation for debugging | Yes |
| Log interpretation | Yes |
| First failure vs downstream failure | Yes |
| Decision tree | Yes |
| Incident timeline | Yes |
| Evidence preservation | Yes |
| Failure reproduction | Yes |
| Break/fix lab | Yes |
| Real-world Data Engineering scenarios | Yes |
| Professional checklist | Yes |
| Command reference | Yes |
| Common mistakes | Yes |
| Mental models | Yes |
| ASCII diagrams | Yes |
| Practice questions | Yes |
| Interview practice | Yes |
| Final knowledge check | Yes |
| Module completion checklist | Yes |

---

# 50. Scope Boundary

This module deliberately does **not** become a complete course on:

- Docker networking,
- Docker volumes,
- environment-variable configuration,
- Docker Compose,
- resource limits,
- disk cleanup,
- Docker Desktop/WSL2,
- Dockerfile authoring,
- image building,
- Kubernetes troubleshooting.

These are separate modules or later curriculum.

They can be used as diagnostic dependencies.

For example:

```text
Networking knowledge
        ↓
diagnose connectivity

Volume knowledge
        ↓
diagnose storage

Configuration knowledge
        ↓
diagnose runtime settings
```

But the teaching focus here remains:

> **logs + exec + evidence-driven troubleshooting.**

---

# 51. Final Professional Takeaway

The most important skill in this module is not memorizing:

```bash
docker logs
docker exec
docker inspect
```

It is learning to think like an operator.

When a Data Engineering service fails:

```text
Observe
   ↓
Collect evidence
   ↓
Form hypothesis
   ↓
Inspect
   ↓
Reproduce
   ↓
Identify root cause
   ↓
Fix
   ↓
Verify
   ↓
Document
```

A professional engineer does not begin with:

> "What command can I run?"

They begin with:

> "What exactly is the symptom, what evidence do I have, and what hypothesis can I test?"

That distinction is what turns Docker troubleshooting from trial-and-error into engineering.

The operational mental model to retain is:

```text
Container state
      +
Application state
      +
Logs
      +
Process state
      +
Configuration
      +
Storage
      +
Network reachability
      +
Readiness
      =
Evidence for root-cause diagnosis
```

And the final rule is:

> **Do not change five things at once. Collect evidence, test one hypothesis at a time, identify the root cause, make the smallest relevant change, and verify the intended behavior.**
