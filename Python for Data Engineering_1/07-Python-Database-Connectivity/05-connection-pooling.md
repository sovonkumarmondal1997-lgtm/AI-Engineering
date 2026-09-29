# Connection Pooling

## Learning Objectives

By the end of this module, you should be able to:

- Explain what a PostgreSQL connection represents.
- Explain why repeatedly opening and closing database connections can be expensive.
- Explain why PostgreSQL connections are limited server resources.
- Define a connection pool and explain its borrow/use/return lifecycle.
- Use `psycopg_pool.ConnectionPool`.
- Configure `min_size`, `max_size`, `timeout`, and key connection-lifecycle controls.
- Explain why a larger pool is not automatically faster.
- Build a connection-capacity model across processes, replicas, services, and pools.
- Treat PostgreSQL `max_connections` as a capacity constraint rather than a target.
- Diagnose pool exhaustion.
- Detect and prevent connection leaks.
- Explain pool health, connection checks, `max_idle`, and `max_lifetime`.
- Reason about recovery after a PostgreSQL restart.
- Understand concurrency as a relationship between application workers, pool capacity, and database capacity.
- Explain why pools are generally process-local and why connections must not simply be reused across `fork()`.
- Benchmark connection-per-query versus pooled connections.
- Benchmark different pool sizes under concurrent load.
- Monitor pool behavior and correlate it with `pg_stat_activity`.
- Explain what PgBouncer is and how it differs from an application-level pool.
- Explain session, transaction, and statement pooling.
- Identify session-dependent features that require special treatment under transaction pooling.
- Explain why prepared statements may need compatibility planning with poolers.
- Explain why `LISTEN` and session-level advisory locks depend on session continuity.
- Recognize when application-level pooling may not be appropriate.
- Reason about short-lived batch jobs and serverless connection storms.
- Understand how pooling, retries, transaction duration, and database latency interact.
- Build a production connection-pooling decision framework.
- Defend pool-sizing and pooler decisions in architecture reviews.

---

## Prerequisites

You should already have completed:

- `01-db-api-pep-249-connections-and-cursors.md`
- `02-postgresql-from-python-with-psycopg.md`
- `03-parameterized-queries-and-sql-injection.md`
- `04-transaction-control-from-python.md`

The previous topics established:

```text
DB-API
   ↓
psycopg 3
   ↓
safe SQL construction
   ↓
transaction control
```

This topic asks a different question:

> **How should many pieces of application code safely share a limited number of PostgreSQL connections?**

Do not confuse the concepts.

```text
Transaction
    =
unit of database work

Connection
    =
database session/resource

Connection pool
    =
manager of reusable connections

PgBouncer
    =
external connection pooler/proxy
```

> **Scope boundary:** Topic 06 introduces SQLAlchemy Core. Topic 07 covers ORM. Topic 08 covers Alembic. Topic 09 covers bulk loading. Topic 10 covers large-result streaming. Those subjects are referenced only where connection management intersects them.

---

# Why Connection Pooling Exists

A database connection is not just a Python object.

It represents a real connection and PostgreSQL server-side session.

Opening one involves work such as:

```text
Python request
    ↓
network connection setup
    ↓
authentication
    ↓
TLS negotiation/setup when configured
    ↓
PostgreSQL session creation
    ↓
ready for SQL
```

Then closing it releases the server-side session.

For a long-lived service, repeatedly doing this:

```python
for _ in range(1000):
    with psycopg.connect(...) as conn:
        conn.execute("SELECT 1")
```

can add substantial connection-management overhead.

The exact cost depends on:

- network topology;
- authentication;
- TLS configuration;
- server load;
- operating-system behavior;
- connection frequency.

Do not assume one universal connection-creation cost.

But the architectural principle is stable:

> **If many operations need database access, creating a fresh PostgreSQL connection for every operation is often wasteful.**

A pool reuses connections instead.

---

# 1. What Is a PostgreSQL Connection?

A PostgreSQL connection is a client-to-server communication relationship that also corresponds to a PostgreSQL session.

The simplest mental model is:

```text
Python process
      ↓
psycopg connection
      ↓
PostgreSQL session
```

That session can have:

- transaction state;
- session settings;
- application identity;
- server-side resources;
- network state.

This is why a connection is more than a socket.

A connection object in Python is the client-side representation of that relationship.

## 1.1 A connection has a lifecycle

Conceptually:

```text
created
  ↓
authenticated
  ↓
usable
  ↓
transaction work
  ↓
idle / reused
  ↓
closed or replaced
```

In a pooled application, the physical connection can stay alive across many logical units of application work.

---

# 2. Why Repeated Connections Are Expensive

Consider:

```python
for customer_id in customer_ids:
    with psycopg.connect(...) as conn:
        conn.execute(
            "SELECT name FROM customers WHERE id = %s",
            (customer_id,),
        )
```

The logical work is:

```text
query customer 1
query customer 2
query customer 3
...
```

But the physical work may be:

```text
connect → query → close
connect → query → close
connect → query → close
...
```

A pool changes the architecture to:

```text
create pool
    ↓
create a bounded set of connections
    ↓
borrow
    ↓
query
    ↓
return
    ↓
reuse
```

## 2.1 Connection setup costs

Potential costs include:

- DNS/network setup;
- TCP setup;
- TLS negotiation;
- authentication;
- PostgreSQL backend/session initialization.

The exact sequence and cost vary.

## 2.2 Server-side cost

PostgreSQL also has to maintain a backend for each connection.

That means connection count affects server resources.

Relevant concerns include:

- memory;
- process/thread/backend management;
- authentication work;
- scheduling;
- file descriptors and network resources;
- query concurrency.

The exact resource model depends on PostgreSQL version and deployment architecture.

The production principle is:

> **A database connection is a finite server resource.**

---

# 3. What Is a Connection Pool?

A connection pool is a managed set of reusable database connections.

Imagine:

```text
Pool
├── Connection 1
├── Connection 2
├── Connection 3
├── Connection 4
└── Connection 5
```

Application code does not normally own those connections permanently.

Instead, it borrows one.

```text
Application needs database work
          ↓
      borrow
          ↓
       use
          ↓
 transaction finishes
          ↓
       return
```

The physical connection can then be reused by another worker.

---

# 4. Pool vs Connection

| Concept | Meaning |
|---|---|
| Connection | One database session/resource |
| Pool | Manager of multiple reusable connections |
| Borrow | Application gets temporary access to a pooled connection |
| Return | Application gives the connection back to the pool |
| Pool close | Pool intentionally shuts down managed connections |

The most important distinction is:

```text
logical use of a connection
    ≠
physical lifetime of the PostgreSQL connection
```

A worker might use:

```text
Connection 3
```

for 20 milliseconds.

The PostgreSQL session represented by Connection 3 may remain open for hours.

That is the whole point of pooling.

---

# 5. `psycopg_pool.ConnectionPool`

psycopg 3's pool implementation is provided by the separate `psycopg_pool` package.

For a project managed with `uv`:

```bash
uv add psycopg_pool
```

A typical import is:

```python
from psycopg_pool import ConnectionPool
```

## 5.1 First pool

```python
from psycopg_pool import ConnectionPool


with ConnectionPool(
    conninfo="postgresql://...",
    min_size=2,
    max_size=10,
) as pool:
    with pool.connection() as conn:
        row = conn.execute("SELECT 1").fetchone()

        print(row)
```

This shows the key lifecycle:

```text
create pool
   ↓
pool manages connections
   ↓
borrow
   ↓
execute
   ↓
return
   ↓
close pool
```

The official psycopg 3 pool API exposes settings including `min_size`, `max_size`, `timeout`, `max_idle`, `max_lifetime`, connection checks, and pool statistics. citeturn499735search0turn499735search1

## 5.2 Why use a pool context manager?

This:

```python
with ConnectionPool(...) as pool:
    ...
```

makes startup/shutdown lifecycle visible in code.

It is especially useful for long-running applications that create one process-local pool and close it during controlled shutdown.

---

# 6. Pool Lifecycle

A pool itself has a lifecycle.

```text
pool constructed
     ↓
pool opened / started
     ↓
connections become available
     ↓
workers borrow
     ↓
workers return
     ↓
pool may grow/shrink within limits
     ↓
pool closes during shutdown
```

## 6.1 Basic explicit lifecycle

```python
from psycopg_pool import ConnectionPool


pool = ConnectionPool(
    conninfo="postgresql://...",
    min_size=2,
    max_size=10,
)

try:
    with pool.connection() as conn:
        print(conn.execute("SELECT 1").fetchone())
finally:
    pool.close()
```

The exact pool opening behavior can be controlled explicitly in current psycopg pool versions; using a pool as a context manager is a clear lifecycle pattern.

## 6.2 Why lifecycle matters

A pool that is never closed can leave resources behind during process shutdown.

A pool created repeatedly can create unnecessary connections.

A well-designed application chooses a lifecycle aligned with the runtime.

For example:

```text
long-lived web service
    → pool lives for process lifetime

worker process
    → pool lives for worker lifetime

short batch job
    → pool may not be necessary

serverless function
    → consider runtime reuse + external pooling/proxy
```

The correct answer depends on runtime architecture.

---

# 7. Borrow / Use / Return

The central pool lifecycle is:

```text
BORROW
   ↓
USE
   ↓
RETURN
```

With psycopg:

```python
with pool.connection() as conn:
    conn.execute(
        "SELECT id FROM customers WHERE id = %s",
        (123,),
    )
```

At context exit, the connection is returned to the pool rather than intentionally destroyed as a normal pooled resource.

Current psycopg pool documentation describes `pool.connection()` as a context manager that waits for an available connection, applies normal connection-context transaction behavior on exit, and returns the connection to the pool. citeturn499735search0turn499735search1

## 7.1 Returning is not closing

This distinction is critical:

```text
RETURN TO POOL
    ≠
CLOSE DATABASE CONNECTION
```

The pool keeps the physical connection for reuse when its lifecycle policy allows.

---

# 8. Transaction Semantics When Using a Pool

Topic 04 taught transaction lifecycle.

Now apply that knowledge to pooling.

The correct lifecycle is:

```text
borrow connection
      ↓
transaction
      ↓
commit / rollback
      ↓
return connection
```

The connection must not return to the pool carrying accidental application state.

## 8.1 Safe pattern

```python
with pool.connection() as conn:
    with conn.transaction():
        conn.execute(...)
        conn.execute(...)
```

This gives:

```text
borrow
   ↓
transaction begins
   ↓
work
   ↓
commit/rollback
   ↓
connection returns
```

## 8.2 Why is this important?

Suppose worker A uses:

```text
Connection 2
```

and leaves an uncommitted transaction behind.

Then worker B receives the same physical connection.

Now B inherits unexpected database session state.

That creates a correctness boundary violation.

## 8.3 Production rule

> **Never return a connection to the pool with unintended transaction or session state.**

---

# 9. `min_size`, `max_size`, and `timeout`

These are the first configuration controls to understand.

## 9.1 `min_size`

`min_size` represents the minimum pool capacity the pool tries to maintain.

Example:

```python
ConnectionPool(
    conninfo="postgresql://...",
    min_size=2,
    max_size=10,
)
```

Conceptually:

```text
minimum managed connections = 2
```

Why might this help?

A long-lived service can have some ready-to-use connections rather than always starting from zero.

Trade-off:

```text
higher min_size
    +
faster readiness for bursty requests
    -
more idle database connections
```

## 9.2 `max_size`

`max_size` limits how many connections the pool can manage.

Example:

```python
max_size=10
```

Conceptually:

```text
at most 10 connections from this pool
```

This is important because:

> **`max_size` is a concurrency and capacity control, not merely a performance setting.**

## 9.3 `timeout`

`timeout` limits how long a client waits to obtain a connection.

If all connections are busy:

```text
pool full
   ↓
new request waits
   ↓
timeout reached
   ↓
PoolTimeout
```

This is much safer than allowing an application request to wait indefinitely.

---

# 10. Why Larger Pools Are Not Automatically Faster

A very common beginner intuition is:

> "If 5 connections are good, 50 connections must be faster."

That does not follow.

Consider:

```text
more workers
    ↓
more concurrent database queries
    ↓
more CPU contention
    ↓
more I/O contention
    ↓
more lock contention
    ↓
longer queries
    ↓
connections remain busy longer
    ↓
throughput may decrease
```

The key principle is:

```text
Concurrency ≠ unlimited parallelism
```

PostgreSQL has finite:

- CPU;
- memory;
- storage throughput;
- locks;
- connection capacity;
- cache/buffer capacity.

A huge application pool can simply increase the number of clients competing for the same underlying resources.

## 10.1 Small pools can be faster

A deliberately bounded pool can sometimes produce:

```text
fewer concurrent queries
    ↓
less contention
    ↓
shorter individual execution times
    ↓
better overall throughput
```

This is workload-dependent.

Never standardize a pool size based on a slogan.

---

# 11. Pool Sizing

Pool sizing is an architecture problem.

Start with:

```text
pool size must be derived from system constraints
```

Do not begin with:

> "What number should `max_size` be?"

Begin with:

> "How much concurrent database work does this application actually need, and how much database capacity can it safely consume?"

---

# 12. PostgreSQL `max_connections`

PostgreSQL has a configured connection capacity:

```text
max_connections
```

Treat it as a **constraint**.

Do not treat it as a target.

If PostgreSQL allows 200 connections, it does not follow that one application should consume all 200.

You need reserve capacity for:

- administrators;
- monitoring;
- migrations;
- maintenance;
- other services;
- operational recovery.

## 12.1 Simple capacity formula

A planning upper bound can be approximated as:

```text
possible application connections
≈
instances
×
processes per instance
×
pool max_size
```

Then add other independent connection consumers.

This is a planning model, not a complete capacity model.

---

# 13. Pool Sizing Example

Suppose:

```text
6 application instances
×
4 worker processes
×
pool max_size = 5
```

Then:

```text
6 × 4 × 5
=
120 possible application connections
```

Now imagine:

```text
PostgreSQL max_connections = 100
```

This architecture cannot safely assume all pools can fully expand simultaneously.

The important observation is not:

> "Pool size 5 is bad."

It is:

> **The product of replicas, processes, and pool sizes matters.**

---

# 14. Pool Capacity Must Include All Pools

Suppose you have:

```text
Service A → 4 replicas → pool max 5
Service B → 3 replicas → pool max 4
Service C → 2 replicas → pool max 3
```

Possible application connections:

```text
A = 4 × 5 = 20
B = 3 × 4 = 12
C = 2 × 3 = 6

Total = 38
```

Now add:

```text
admin/monitoring = 10
other client = 12
```

Potential demand is:

```text
60 connections
```

If the server's connection capacity is 70, the reserve is much smaller than it first appeared.

This is why connection planning must consider the whole platform.

---

# 15. Operational Reserve

Always leave room for operations.

A database that is permanently at its connection ceiling is harder to operate.

Imagine an incident:

```text
application uses all connections
        ↓
database slows
        ↓
operator tries to connect
        ↓
no connection capacity
```

That is an operational failure.

The exact reserve percentage should be based on the environment.

The general principle is:

> **Capacity planning must include the people and systems needed to recover the database.**

---

# 16. Pool Sizing Exercise

Given:

```text
PostgreSQL max_connections = 200

Application:
8 instances
4 worker processes each

Other known consumers:
30 connections
```

Your task is to choose a **starting range**, not a magical exact number.

## Step 1 — Calculate process count

```text
8 × 4 = 32 processes
```

## Step 2 — Apply candidate pool sizes

For a candidate:

```text
pool max_size = 3
```

possible application connections:

```text
32 × 3 = 96
```

Total including other consumers:

```text
96 + 30 = 126
```

## Step 3 — Reserve operational headroom

You still need to ask:

- How much transient growth is possible?
- Are there hidden clients?
- How long are connections held?
- Does PgBouncer exist?
- What does the benchmark show?

The exercise is intentionally open-ended.

There is no universal correct pool size from `max_connections` alone.

---

# 17. Pool Exhaustion

Suppose:

```text
max_size = 4
```

and four workers are already using all connections:

```text
Pool
[BUSY]
[BUSY]
[BUSY]
[BUSY]
```

Worker five asks for a connection:

```text
Worker 5
   ↓
pool.connection()
   ↓
wait
```

If one connection returns before timeout:

```text
connection becomes available
   ↓
Worker 5 proceeds
```

If not:

```text
timeout
   ↓
PoolTimeout
```

## 17.1 Why exhaustion matters

Pool exhaustion creates queueing.

Queueing creates latency.

Latency can trigger retries.

Retries can create more queueing.

That can become a failure cascade.

---

# 18. Pool Exhaustion Scenario

Consider:

```text
Pool max_size = 2

Worker A → connection 1
Worker B → connection 2
Worker C → waits
Worker D → waits
Worker E → waits
```

Now imagine A's query becomes slow.

```text
A = busy longer
B = busy
C/D/E = waiting
```

The root cause might be:

- slow SQL;
- lock contention;
- network latency;
- database overload.

It is not necessarily:

```text
pool too small
```

This distinction is important.

Increasing the pool might simply make PostgreSQL process more simultaneous slow work.

---

# 19. Connection Leaks

A **connection leak** happens when application code borrows a pooled connection and fails to return it.

Bad example:

> ⚠️ **INTENTIONALLY BROKEN TRAINING EXAMPLE**

```python
conn = pool.getconn()

if some_condition:
    return

pool.putconn(conn)
```

If `some_condition` is true:

```text
borrow
  ↓
early return
  ↓
no putconn()
  ↓
connection leaked
```

## 19.1 Why one leak matters

Suppose:

```text
pool max_size = 5
```

One leak leaves at most four usable connections.

Repeated leaks can eventually produce:

```text
5 leaked connections
    ↓
0 available
    ↓
all new callers wait
    ↓
PoolTimeout
```

The pool did exactly what it was configured to do.

The application failed to return resources.

---

# 20. Safe Borrowing with Context Managers

Preferred pattern:

```python
with pool.connection() as conn:
    conn.execute("SELECT 1")
```

The context manager makes the return path explicit.

Even with context managers, transaction behavior still matters.

A useful pattern is:

```python
with pool.connection() as conn:
    with conn.transaction():
        conn.execute(...)
```

This keeps:

```text
transaction lifecycle
+
connection lifecycle
```

visible.

---

# 21. Leak Detection Exercise

> ⚠️ **INTENTIONALLY BROKEN TRAINING EXAMPLE**
>
> Use only a local PostgreSQL environment.

## Task

1. Create a pool with:
   ```text
   max_size = 2
   ```
2. Borrow two connections.
3. Deliberately fail to return one or both.
4. Attempt another checkout.
5. Observe the wait.
6. Observe `PoolTimeout`.
7. Fix the code with context management.
8. Repeat the test.

### Prediction

Before running, predict:

```text
How many connections can the third caller obtain?
How long will it wait?
What exception should appear?
```

### Production lesson

> Connection leaks consume concurrency capacity silently until the pool becomes unavailable.

---

# 22. Pool Health

Pooled connections can become unhealthy.

Examples:

```text
PostgreSQL restart
network interruption
server closes connection
session killed
idle timeout
```

A pool therefore needs lifecycle and health management.

Important concepts include:

- connection checks;
- `max_idle`;
- `max_lifetime`;
- reconnect behavior;
- replacement of broken connections.

Current psycopg pool documentation exposes `check` callbacks and `ConnectionPool.check_connection()` for validating a connection when it is acquired, as well as `max_idle`, `max_lifetime`, and reconnect controls. citeturn499735search0turn499735search1

---

# 23. `max_idle`

`max_idle` controls how long a connection can remain unused before it may be closed.

The key design idea is:

```text
pool grows
   ↓
usage decreases
   ↓
extra idle connections remain unused
   ↓
max_idle reached
   ↓
extra connection may be retired
```

This is especially relevant when:

```text
min_size < max_size
```

and the pool is allowed to grow temporarily.

The objective is not to destroy useful connections constantly.

It is to avoid retaining excess idle capacity forever.

---

# 24. `max_lifetime`

`max_lifetime` limits how long a pooled connection remains alive before it is retired and replaced.

Conceptually:

```text
connection created
       ↓
used many times
       ↓
lifetime limit reached
       ↓
retire
       ↓
new connection
```

Why can lifecycle rotation be useful?

Long-lived applications operate for days or weeks.

Over time, infrastructure conditions can change:

- network paths;
- server configuration;
- load patterns;
- infrastructure proxies;
- session-level state.

A bounded lifetime can help rotate connections deliberately.

Do not claim that old connections are inherently bad.

The production question is:

> **What connection lifetime fits this environment and workload?**

---

# 25. Connection Checks

A pool can use a health check when a connection is obtained.

Conceptually:

```text
borrow request
    ↓
health check
    ↓
healthy?
   / \
 yes  no
  ↓    ↓
give  replace
```

In current psycopg pool documentation, a `check` callback can be supplied to validate connections when `connection()` or `getconn()` is called. `ConnectionPool.check_connection` is provided as a simple check implementation. citeturn499735search0turn499735search1

Example:

```python
from psycopg_pool import ConnectionPool


pool = ConnectionPool(
    conninfo="postgresql://...",
    min_size=2,
    max_size=10,
    check=ConnectionPool.check_connection,
)
```

Trade-off:

```text
health check
    +
better chance of giving a healthy connection
    -
extra work/network round trip
```

Health checking should therefore be chosen deliberately.

---

# 26. Database Restart Recovery

Suppose the architecture is:

```text
Python workers
      ↓
ConnectionPool
      ↓
PostgreSQL
```

Now PostgreSQL restarts.

Existing physical connections can become invalid.

A production pool needs to respond to that condition by allowing broken connections to fail and be replaced as appropriate.

The exact recovery timing depends on:

- server restart duration;
- reconnect configuration;
- network state;
- workload;
- whether requests are currently using the broken connections.

Do not assume all in-flight operations will transparently succeed.

Some operations will fail and require application-level handling.

---

# 27. Database Restart Lab

> **LOCAL LAB ONLY**

## Task

1. Start Docker PostgreSQL.
2. Start a Python process using `ConnectionPool`.
3. Execute repeated small queries.
4. Restart PostgreSQL.
5. Continue the workload.
6. Observe failures and subsequent recovery.

### Record

- errors that occurred;
- time until PostgreSQL became reachable;
- time until pool work succeeded again;
- whether replacement connections were created;
- what happened to in-flight operations.

### Questions

- Did the pool itself "know" PostgreSQL restarted?
- Which errors happened at the worker level?
- Did later checkouts succeed?
- Did the database connection count recover?

### Production lesson

> A resilient pool can recover connection resources, but it cannot magically make failed application operations successful.

---

# 28. Connection Checks and Lifecycle

Think of three separate concepts:

```text
health
lifetime
idleness
```

### Health

Is the connection usable now?

### Lifetime

Has the connection lived long enough that we want to rotate it?

### Idleness

Has the connection been unused for long enough that we want fewer idle resources?

These correspond to different operational goals.

Do not use one setting as a substitute for the others.

---

# 29. Pool and Concurrency

A pool becomes a concurrency boundary.

Suppose:

```text
Worker A ─┐
Worker B ─┼──→ Pool ───→ PostgreSQL
Worker C ─┤
Worker D ─┘
```

If:

```text
pool max_size = 2
```

then:

```text
Worker A → Connection 1
Worker B → Connection 2
Worker C → waits
Worker D → waits
```

The application can have 32 workers without having 32 PostgreSQL connections.

That is one of the biggest benefits of a pool.

---

# 30. Concurrency Is Not the Same as Pool Size

Suppose:

```text
32 worker threads
pool max_size = 5
```

The application can schedule 32 units of work.

But only up to five can concurrently hold pooled connections.

This can be completely intentional.

The pool acts like a gate:

```text
32 workers
   ↓
pool capacity = 5
   ↓
at most 5 database operations holding connections
```

The others wait.

This can protect the database from excessive concurrency.

But if the workload legitimately needs more concurrency and the database can support it, the pool may become the bottleneck.

That is why measurement matters.

---

# 31. One Pool Per Process

A pool is application-process state.

Different processes generally have separate memory spaces.

Therefore, the usual architecture is:

```text
Process 1
   ↓
Pool A
   ↓
connections

Process 2
   ↓
Pool B
   ↓
connections

Process 3
   ↓
Pool C
   ↓
connections
```

This means:

```text
pool size is not globally shared
```

If each process has:

```text
max_size = 5
```

and you have:

```text
8 processes
```

the possible connections are:

```text
8 × 5 = 40
```

This multiplication is easy to miss.

---

# 32. Why One Process Needs Its Own Pool

A pool manages state in process memory.

A connection object similarly represents a session that should be controlled within the process architecture that created it.

A process-local pool provides:

```text
clear ownership
+
clear lifecycle
+
no cross-process sharing
```

For example:

```text
worker process starts
    ↓
create its own pool
    ↓
serve work
    ↓
close pool
    ↓
process exits
```

This is particularly important in multi-process server deployments.

---

# 33. Fork Safety

A fork duplicates a process's memory state.

That does **not** mean a live database connection can safely be duplicated and simultaneously driven by parent and child processes.

The safe mental model is:

```text
Parent process
    ↓
fork()
   ↙ ↘
Child A  Child B

Each child should establish its own database connections/pool.
```

## 33.1 What not to do

> ⚠️ **INTENTIONALLY UNSAFE TRAINING EXAMPLE**

```python
pool = ConnectionPool(...)

# Process creation/fork occurs here.

# Child process attempts to reuse
# the inherited pool/connection state.
```

Do not rely on inherited live connections.

## 33.2 Safer approach

```text
create process
      ↓
initialize process-local pool
      ↓
process handles work
```

### Production lesson

> **Connection ownership must align with process boundaries.**

---

# 34. Pool Exhaustion and Queueing

Suppose:

```text
Pool max_size = 5
32 worker threads
```

At most five workers can hold connections simultaneously.

The remaining workers wait.

This creates a queue:

```text
5 active connections
      ↓
27 waiting workers
```

The important metric is not only:

```text
number of connections
```

but also:

```text
how long workers wait for connections
```

A pool can be correctly sized and still show meaningful queueing during bursts.

Or it can be badly sized and show constant queueing.

You must measure.

---

# 35. Connection-Per-Query vs Pool Benchmark

The roadmap requires a benchmark comparing connection-per-query against a pool for 5,000 small queries.

This should be a real measurement.

Do not use fabricated numbers.

## 35.1 Approach A — Connection per query

Conceptually:

```python
for _ in range(5_000):
    with psycopg.connect(...) as conn:
        conn.execute("SELECT 1")
```

## 35.2 Approach B — Connection pool

```python
with ConnectionPool(
    conninfo="postgresql://...",
    min_size=2,
    max_size=10,
) as pool:
    for _ in range(5_000):
        with pool.connection() as conn:
            conn.execute("SELECT 1")
```

## 35.3 Measure

At minimum record:

```text
total elapsed time
queries completed
errors
```

Where practical also record:

```text
connection creation count
checkout/wait time
database-side connection count
```

## 35.4 Benchmark rules

Keep constant:

- Python version;
- machine/container resources;
- PostgreSQL instance;
- SQL;
- database location;
- dataset/environment;
- authentication/TLS settings.

Warm up before measuring.

Run multiple trials.

Use summary statistics rather than one lucky run.

## 35.5 Expected reasoning

Do not start with:

> "Pooling is faster."

Start with:

> "How much connection setup overhead exists in this environment, and how much does reuse reduce it?"

---

# 36. 32 Threads vs Pool Size 5

The roadmap requires a concurrency experiment with:

```text
32 worker threads
pool max_size = 5
```

## 36.1 What to measure

Record:

- total elapsed time;
- throughput;
- pool wait time;
- timeout count;
- database connection count.

## 36.2 Then vary pool size

Try candidates such as:

```text
1
2
4
5
8
12
16
```

The exact values are experimental choices.

Do not assume which one will win.

## 36.3 The actual lesson

The output should look like:

| Pool size | Total time | Throughput | Avg wait | Timeout count |
|---:|---:|---:|---:|---:|
| 1 | measure | measure | measure | measure |
| 2 | measure | measure | measure | measure |
| 4 | measure | measure | measure | measure |
| 5 | measure | measure | measure | measure |
| 8 | measure | measure | measure | measure |
| 12 | measure | measure | measure | measure |
| 16 | measure | measure | measure | measure |

Do not fill this table with invented results.

### Production lesson

> **The correct pool size is an empirical property of a workload and its database capacity.**

---

# 37. Observability

Connection pooling is difficult to operate if you cannot see what it is doing.

Useful application-side concepts include:

- pool size;
- available connections;
- checked-out connections;
- waiters;
- checkout latency;
- connection creation failures;
- timeout count;
- reconnect events.

Current psycopg pool versions expose pool statistics through methods such as `get_stats()` and `pop_stats()`, with counters including pool size, available connections, and requests waiting. These stats should be treated as operational metrics rather than as a rigid forever-stable interface. citeturn499735search1

## 37.1 Example stats inspection

```python
from psycopg_pool import ConnectionPool

with ConnectionPool(
    conninfo="postgresql://...",
    min_size=2,
    max_size=10,
) as pool:
    stats = pool.get_stats()
    print(stats)
```

The exact counters can vary by psycopg pool version.

---

# 38. PostgreSQL-Side Observability with `pg_stat_activity`

Application metrics should be correlated with PostgreSQL.

For example:

```sql
SELECT
    application_name,
    state,
    count(*)
FROM pg_stat_activity
GROUP BY application_name, state
ORDER BY application_name, state;
```

This can help answer:

```text
How many sessions exist?
How many are active?
How many are idle?
Which application owns them?
```

## 38.1 Two-sided observability

Think:

```text
Application pool metrics
        +
PostgreSQL session metrics
```

Together they tell a much stronger story.

---

# 39. Pool Metrics

A useful conceptual metric set includes:

| Metric | What it tells you |
|---|---|
| pool size | Current managed capacity |
| available connections | Idle capacity now |
| checked-out connections | Current concurrency |
| requests waiting | Queue depth |
| checkout latency | How long callers wait for capacity |
| connection creation latency | Cost of creating physical sessions |
| pool timeout count | Requests/jobs unable to obtain capacity |
| broken/replaced connections | Health/recovery activity |
| pool utilization | How close the pool is to its limit |
| PostgreSQL connection count | Server-side connection pressure |
| PostgreSQL active/idle state | What sessions are doing |

Do not assign universal alert thresholds.

A "high" value depends on workload.

---

# 40. Monitoring Before Failure

The objective is to identify pressure before users see outages.

Useful indicators include:

```text
high pool utilization
+
rising wait time
+
rising timeout rate
+
high PostgreSQL connection count
+
long query duration
```

These signals should be interpreted together.

For example:

### High utilization + low wait

The pool may be serving the workload effectively.

### High utilization + high wait

Possible capacity mismatch or slow database work.

### Low utilization + high latency

The bottleneck may be somewhere other than pool size.

### High connection count + low throughput

Excessive concurrency may be increasing contention.

These are hypotheses, not conclusions.

---

# 41. PgBouncer

PgBouncer is an external connection pooler for PostgreSQL.

Architecture:

```text
Many application clients
        ↓
     PgBouncer
        ↓
fewer backend PostgreSQL connections
        ↓
   PostgreSQL
```

It can help decouple:

```text
number of client connections
```

from:

```text
number of PostgreSQL server connections
```

The critical distinction is:

```text
Application pool
    =
connection reuse inside an application process

PgBouncer
    =
external reuse/assignment of PostgreSQL server connections
```

Both can exist together:

```text
Python
  ↓
application pool
  ↓
PgBouncer
  ↓
PostgreSQL
```

But the architecture becomes more complex.

---

# 42. Why PgBouncer Exists

Suppose there are:

```text
20 application instances
×
100 client connections each
```

but the database does not need 2,000 active server sessions.

PgBouncer can place many client connections in front of a smaller backend connection pool.

This is especially useful where:

- clients are numerous;
- client connections are short-lived;
- PostgreSQL connection capacity is constrained;
- application runtimes create bursts of connections.

The exact architecture depends on workload and pooling mode.

---

# 43. Application Pool vs PgBouncer

| Concern | Application pool | PgBouncer |
|---|---|---|
| Location | Inside application process | External service/proxy |
| Main role | Reuse connections among application tasks | Reuse backend PostgreSQL connections among clients |
| Scope | One process/pool | Across client connections visible to the pooler |
| Process multiplication | Yes | External shared layer can reduce backend connection pressure |
| Session continuity | Usually preserved by the same physical connection | Depends on pooling mode |
| Application lifecycle | Process-local | Independent service lifecycle |

This is why the two should not be mentally collapsed into one concept.

---

# 44. PgBouncer Pooling Modes

PgBouncer supports three important modes:

```text
session
transaction
statement
```

The current PgBouncer documentation defines them by when the server connection can be reassigned. citeturn560933search0turn560933search2

---

## 44.1 Session pooling

Conceptually:

```text
client connects
    ↓
server connection assigned
    ↓
client keeps server connection
    ↓
client disconnects
    ↓
server connection returns to pool
```

Session pooling preserves the strongest session continuity.

This is usually the least disruptive pooling mode for session-oriented applications.

---

## 44.2 Transaction pooling

Conceptually:

```text
client transaction
      ↓
server connection assigned
      ↓
BEGIN ... COMMIT
      ↓
server connection released
```

The next transaction from the same client may use a different PostgreSQL server connection.

This provides more aggressive backend reuse.

But it weakens session continuity.

The critical mental model is:

> **The logical application client is no longer guaranteed to stay attached to one PostgreSQL backend session across transactions.**

---

## 44.3 Statement pooling

The most aggressive mode:

```text
statement starts
    ↓
server connection assigned
    ↓
statement completes
    ↓
connection released
```

PgBouncer documentation notes that multi-statement transactions are disallowed in statement pooling because they require connection continuity. citeturn560933search0turn560933search2

This mode has the strongest compatibility constraints.

---

# 45. PgBouncer Feature Compatibility

The main question is:

> **Does this feature depend on PostgreSQL session continuity?**

If yes, aggressive transaction/statement pooling may be incompatible or require additional architecture/configuration.

---

# 46. Session State

Consider:

```sql
SET search_path = analytics;
```

or:

```sql
SET TimeZone = 'UTC';
```

If a client performs one transaction on backend session A and a later transaction on backend session B, session-local state can become a source of surprises.

Modern PgBouncer can track some PostgreSQL-reported session parameters, but that does not make arbitrary session state universally transparent. The safest architectural assumption is that transaction pooling weakens session affinity. citeturn560933search0

### Production lesson

> Do not assume session state follows a logical client through transaction pooling.

---

# 47. Prepared Statements and Poolers

Prepared statements are an important compatibility example.

A prepared statement can be associated with backend session state.

That creates an architectural concern:

```text
Application
    ↓
PgBouncer transaction mode
    ↓
backend session can change
```

### Important current nuance

Modern PgBouncer versions can support protocol-level named prepared statements in transaction and statement pooling when `max_prepared_statements` is enabled. PgBouncer tracks and prepares statements on backend connections as needed. However, SQL-level `PREPARE` / `EXECUTE` / `DEALLOCATE` semantics are not handled the same way by that feature. citeturn560933search0turn560933search1

Therefore, the correct production question is:

> **Which prepared-statement mechanism is the application using, which PgBouncer version/configuration is deployed, and are the two compatible?**

Do not use the oversimplified rule:

> "Prepared statements never work with transaction pooling."

That is no longer accurate.

---

# 48. `LISTEN` / `NOTIFY` Compatibility

`LISTEN` is inherently session-oriented.

Conceptually:

```text
session A
   ↓
LISTEN channel
   ↓
notifications delivered to that session
```

If transaction pooling can move the logical client between backend sessions, a persistent `LISTEN` subscription cannot be assumed to remain attached to one backend.

Therefore:

```text
transaction pooling
+
persistent LISTEN dependency
=
compatibility problem
```

Use a session-oriented architecture when the application depends on stable listening state, or isolate the listener connection from the transaction-pooled workload.

The same principle applies to many session-dependent features.

---

# 49. Advisory Locks

PostgreSQL advisory locks come in different forms.

The important distinction here is:

```text
session-level advisory lock
```

versus:

```text
transaction-level advisory lock
```

A session-level advisory lock is tied to the physical PostgreSQL session.

If transaction pooling changes the backend session between logical transactions, session-level advisory-lock assumptions can break.

Therefore:

> **Do not assume session-level advisory locks survive transaction-pool reassignment.**

Transaction-level advisory locks have different semantics because their lifetime is tied to the transaction.

---

# 50. Compatibility Table

| Feature | Session pooling | Transaction pooling | Statement pooling |
|---|---|---|---|
| Multi-statement transactions | Yes | Yes | No |
| Session-local state | Generally preserved | Requires care | Highly constrained |
| `LISTEN` | Compatible with session continuity | Generally unsuitable for persistent listening | Unsuitable |
| Session-level advisory locks | Compatible | Unsafe as a session-affinity assumption | Unsafe |
| Prepared statements | Session semantics | Depends on mechanism/version/configuration | Depends on mechanism/version/configuration |
| Session-dependent features | Strongest compatibility | Restricted | Most restricted |

This is a design aid, not a substitute for testing the exact deployed versions/configuration.

---

# 51. Application Pool + PgBouncer

A layered architecture can look like:

```text
Python workers
      ↓
psycopg_pool
      ↓
PgBouncer
      ↓
PostgreSQL
```

Why might a team use both?

The application pool can control:

```text
how many concurrent database operations a process issues
```

PgBouncer can control:

```text
how many backend PostgreSQL server connections are maintained externally
```

Those are different controls.

## 51.1 Why two layers add complexity

Now you have:

```text
application pool capacity
+
PgBouncer pool capacity
+
PostgreSQL capacity
```

If the layers are badly sized, the application can:

- queue unnecessarily;
- create excessive clients;
- make operational diagnosis harder;
- interact poorly with session state.

Do not automatically maximize both pools.

---

# 52. When Not to Pool in the Application

Application pooling is useful, but it is not mandatory.

The roadmap specifically requires considering:

- short-lived batch jobs;
- serverless functions;
- external pooling infrastructure.

---

# 53. Short-Lived Batch Jobs

Suppose a job:

```text
starts
  ↓
opens one connection
  ↓
does work
  ↓
closes
  ↓
exits
```

If the job runs once every hour, a large application pool may add more complexity than value.

For a short-lived workload, a small connection count may be enough.

The correct question is:

> **How much connection reuse is actually available during this process lifetime?**

---

# 54. Serverless Functions

Serverless runtimes may create many independent execution contexts.

Suppose:

```text
100 function instances
```

and each creates:

```text
pool max_size = 5
```

The theoretical application-side connection demand can become:

```text
100 × 5 = 500
```

That can overwhelm a database quickly.

The issue is not that pooling is intrinsically bad.

The issue is that:

```text
pooling happens independently inside each runtime instance
```

A managed database proxy or external pooler can be more appropriate in architectures where many short-lived clients share a database.

Do not prescribe one vendor or platform.

---

# 55. Serverless Connection Storm

Conceptual architecture:

```text
request burst
     ↓
many cold starts
     ↓
many process-local pools
     ↓
many connection attempts
     ↓
database connection spike
```

This can create a connection storm even though each individual function seems reasonable.

The correct capacity question is:

> **What is the maximum aggregate connection demand across all concurrently running instances?**

---

# 56. Serverless: Pooling Is Not Automatically Wrong

A mature design can use:

```text
runtime connection reuse
+
careful pool limits
+
external proxy/pooler
```

or:

```text
small direct connection usage
```

depending on platform behavior.

The decision depends on:

- invocation concurrency;
- container reuse;
- database connection capacity;
- latency requirements;
- external pooling options.

---

# 57. Connection Pooling Failure Cascades

A pool is part of a larger control system.

Consider:

```text
Database becomes slower
       ↓
Queries hold connections longer
       ↓
Connections remain checked out longer
       ↓
Pool fills
       ↓
New requests wait
       ↓
Pool timeout
       ↓
Application retries
       ↓
More pressure
       ↓
Database becomes slower
```

This is a feedback loop.

The important point:

> **Pool exhaustion may be a symptom of slow database work rather than the root cause.**

---

# 58. Pooling + Retries

Topic 04 introduced retries.

Now combine the ideas.

Suppose:

```text
10 workers
×
1 connection each
```

and a transient failure causes all ten workers to retry simultaneously.

Now you may have:

```text
original work
+
retry work
```

competing for the same pool.

If the pool is already near capacity, retries can increase wait time and timeout probability.

The architecture must therefore consider:

```text
retry policy
+
pool capacity
+
query duration
```

Do not re-teach transaction retry implementation here.

The lesson is the interaction.

---

# 59. Connection Leak + Retry Cascade

An especially dangerous sequence is:

```text
connection leak
    ↓
available pool capacity decreases
    ↓
pool waits increase
    ↓
timeouts begin
    ↓
application retries
    ↓
more work is submitted
    ↓
pool exhaustion worsens
```

This is why a small resource-management bug can look like a major database incident.

Production diagnosis should therefore ask:

```text
Are we slow?
Are we exhausted?
Are we leaking?
Are we retrying?
Are we creating too many connections?
```

---

# 60. Connection Pool vs Database Connection Limit

Never confuse:

```text
pool max_size
```

with:

```text
PostgreSQL max_connections
```

The pool controls the potential number of PostgreSQL connections **managed by that pool**.

`max_connections` is the database server's configured connection capacity.

With several processes:

```text
Process 1 pool max 5
Process 2 pool max 5
Process 3 pool max 5
```

potential connections are:

```text
15
```

not:

```text
5
```

This is one of the most common capacity-planning mistakes.

---

# 61. Multi-Service Pool Sizing

Consider:

```text
Service A:
4 replicas × 4 workers × pool 5 = 80

Service B:
3 replicas × 2 workers × pool 4 = 24

Other consumers:
20
```

Potential total:

```text
80 + 24 + 20
= 124
```

Now ask:

- What is `max_connections`?
- How much operational reserve exists?
- Is PgBouncer between clients and PostgreSQL?
- Do all pools actually need their maximum simultaneously?
- How long are connections held?
- Are retries increasing demand?

The purpose is not to calculate one "correct" number from arithmetic alone.

The arithmetic reveals possible upper bounds.

---

# 62. Health, Lifetime, and Rotation

A production pool should have a lifecycle policy.

Think:

```text
connection created
       ↓
health checked as appropriate
       ↓
used
       ↓
returned
       ↓
idle/lifetime policies applied
       ↓
retire/replace when necessary
```

## 62.1 Why rotate?

Rotation can help manage:

- very old sessions;
- infrastructure changes;
- connection churn patterns;
- long-running process behavior.

Again, the goal is controlled lifecycle, not constant reconnection.

---

# 63. Async Pools

The roadmap requires awareness of:

```python
AsyncConnectionPool
```

Current psycopg pool documentation provides an asynchronous pool with an interface similar to `ConnectionPool`, using asynchronous methods and `AsyncConnection` objects. citeturn499735search0

Conceptually:

```text
synchronous application
    ↓
ConnectionPool

asynchronous application
    ↓
AsyncConnectionPool
```

The lifecycle is similar:

```text
borrow
  ↓
await database work
  ↓
return
```

A conceptual example:

```python
from psycopg_pool import AsyncConnectionPool


async with AsyncConnectionPool(
    conninfo="postgresql://...",
    min_size=2,
    max_size=10,
) as pool:
    async with pool.connection() as conn:
        await conn.execute("SELECT 1")
```

Detailed async programming belongs to Module 2.10.

---

# 64. Connection Pool Anti-Patterns

## Anti-pattern 1 — Create a new pool per request

### Why beginners do it

"Pooling is better, so I'll create a pool for each request."

### What actually happens

Each request creates its own pool and potentially its own connections.

### Production consequence

More connection churn and more complexity.

### Correct mental model

A pool should have a lifecycle aligned with the application process.

---

## Anti-pattern 2 — Huge pools "for speed"

### Beginner belief

More connections mean more parallelism.

### Actual problem

More database concurrency can create contention.

### Production consequence

Higher latency and possibly lower throughput.

### Correct mental model

Measure the concurrency sweet spot.

---

## Anti-pattern 3 — Never close the pool

### Beginner belief

"The process will eventually exit."

### Actual problem

Controlled shutdown becomes less predictable.

### Production consequence

Resource leakage or messy shutdown behavior.

### Correct mental model

Pool lifecycle belongs to application lifecycle.

---

## Anti-pattern 4 — Leak checked-out connections

### Actual problem

Pool capacity disappears one connection at a time.

### Production consequence

Exhaustion and timeouts.

### Correct mental model

Borrow → use → return must always have a safe return path.

---

## Anti-pattern 5 — Share inherited connections across fork

### Actual problem

Physical connection/session state is not a safe process-shared object.

### Production consequence

Unpredictable database communication.

### Correct mental model

Create process-local pools after process creation.

---

## Anti-pattern 6 — Ignore total connections across replicas

### Actual problem

Each process/container has its own pool.

### Production consequence

Aggregate connection demand is much larger than a single-pool configuration suggests.

### Correct mental model

Capacity is calculated platform-wide.

---

## Anti-pattern 7 — Use session features behind transaction-mode PgBouncer

### Actual problem

Backend session can change across transactions.

### Production consequence

Session state becomes nondeterministic.

### Correct mental model

Evaluate feature/session affinity explicitly.

---

## Anti-pattern 8 — Large application pools inside serverless

### Actual problem

Many function instances create many independent pools.

### Production consequence

Connection storm.

### Correct mental model

Aggregate across all concurrent runtime instances.

---

## Anti-pattern 9 — Add retries without considering pool pressure

### Actual problem

Retries create more concurrent attempts.

### Production consequence

Pool exhaustion becomes more likely.

### Correct mental model

Pool and retry design are coupled.

---

## Anti-pattern 10 — Use pool size as database performance tuning

### Actual problem

A pool controls client concurrency, not SQL efficiency.

### Production consequence

More connections can make a slow database slower.

### Correct mental model

Tune the workload and database based on measurements.

---

# 65. Connection Pool Design Patterns

## Pattern A — Long-Lived Service

```text
process starts
    ↓
create pool
    ↓
workers borrow/return
    ↓
service runs
    ↓
shutdown
    ↓
close pool
```

Suitable for long-lived application processes.

---

## Pattern B — Worker Process

```text
worker starts
    ↓
create process-local pool
    ↓
process jobs
    ↓
close pool
```

Each worker owns its own pool.

---

## Pattern C — Short Batch Job

```text
job starts
    ↓
small number of direct connections
    ↓
complete work
    ↓
close
```

Pooling may or may not provide meaningful value.

---

## Pattern D — Serverless

```text
function instance
    ↓
small/direct or carefully bounded connection usage
    ↓
external proxy/pooler where appropriate
    ↓
PostgreSQL
```

Aggregate concurrency matters more than one function's configuration.

---

## Pattern E — PgBouncer Architecture

```text
application
    ↓
reasonable application pool
    ↓
PgBouncer
    ↓
PostgreSQL
```

Use when there is a real architectural need.

Do not add an external pooler simply because it is popular.

---

# 66. Complete Hands-On Lab

The following lab progresses from basic mechanics to architecture.

---

## Stage 1 — Basic Pool

Create:

```python
from psycopg_pool import ConnectionPool
```

Then:

```python
with ConnectionPool(
    conninfo="postgresql://...",
    min_size=2,
    max_size=5,
) as pool:
    with pool.connection() as conn:
        print(conn.execute("SELECT 1").fetchone())
```

### Prediction

How many connections can the pool manage?

---

## Stage 2 — Borrow/Return

Run:

```python
with pool.connection() as conn:
    ...
```

Then inspect pool stats before and after.

### Explain

```text
before
→ available connection

during
→ checked out

after
→ returned
```

---

## Stage 3 — Pool Exhaustion

Use:

```text
max_size = 2
```

Run at least three concurrent tasks that hold connections deliberately.

Observe:

```text
2 busy
1 waiting
```

### Prediction

What will the third task do?

---

## Stage 4 — Leak

Intentionally omit return/close handling.

Observe:

```text
PoolTimeout
```

---

## Stage 5 — Fix Leak

Use:

```python
with pool.connection() as conn:
    ...
```

Verify the next checkout succeeds.

---

## Stage 6 — Benchmark

Compare:

```text
connection-per-query
vs
ConnectionPool
```

using 5,000 small queries.

Record real measurements.

---

## Stage 7 — Pool Sizing

Run 32 worker threads while varying pool size.

Measure:

```text
throughput
wait time
timeout count
database connections
```

---

## Stage 8 — PostgreSQL Restart

Restart PostgreSQL while the pool is active.

Observe:

```text
connection failure
replacement/reconnect
recovery
```

---

## Stage 9 — PgBouncer

Place PgBouncer between the application and PostgreSQL.

Test transaction pooling.

---

## Stage 10 — Compatibility Tests

Test:

```text
SET session state
prepared statements
LISTEN
session-level advisory locks
```

Record which operations depend on session continuity.

---

# 67. `pooling.py` Exercise

The roadmap requires an exercise equivalent to `pooling.py`.

No additional file is required by this document. Implement the exercise inside the existing lab project.

## Objective

Build an experimental connection-pooling program that measures:

- connection reuse;
- pool capacity;
- queueing;
- leaks;
- recovery;
- pool sizing;
- pooler compatibility.

## Required tasks

### Task 1 — 5,000 query benchmark

Compare:

```text
connection-per-query
```

versus:

```text
ConnectionPool
```

Record:

- total elapsed time;
- throughput;
- connection creation count if measurable;
- errors.

---

### Task 2 — 32 threads, pool size 5

Use 32 worker threads.

Start with:

```text
max_size = 5
```

Measure:

- wait time;
- completion time;
- throughput;
- timeout count.

---

### Task 3 — Vary pool size

Test several sizes.

Example:

```text
1
2
4
5
8
12
16
```

Do not assume which is optimal.

---

### Task 4 — Leak a connection

Deliberately fail to return one.

Observe:

```text
pool capacity decreases
```

Then provoke pool timeout.

---

### Task 5 — Fix the leak

Use context management.

Repeat the experiment.

---

### Task 6 — Restart PostgreSQL

Observe:

```text
broken connections
replacement
recovery
```

---

### Task 7 — PgBouncer

Run through PgBouncer in transaction mode.

---

### Task 8 — Test session-dependent features

Check:

- `SET search_path`;
- prepared statements;
- `LISTEN`;
- session-level advisory locks.

Document what depends on physical session continuity.

## Learner prediction

Before each task write:

```text
What should happen?
Why?
Which resource is the limiting factor?
What PostgreSQL-side evidence should I expect?
```

## Production takeaway

A pool is not proven correct because the query returned a row.

It is proven operationally useful when:

```text
capacity
+
correctness
+
health
+
recovery
+
observability
```

all behave as designed.

---

# 68. Benchmark Methodology

A pool benchmark must be fair.

## 68.1 Keep the environment constant

Use the same:

- PostgreSQL instance;
- Docker/container resources;
- Python version;
- psycopg/psycopg_pool version;
- SQL;
- network path;
- authentication configuration.

## 68.2 Warm up

Do not measure only the first request.

The first request can include:

- startup;
- connection creation;
- cache warm-up;
- Python import overhead.

Run warm-up iterations before collecting the main measurements.

## 68.3 Repeated trials

Do multiple trials.

Record:

```text
median
p95/p99 where practical
total throughput
```

Do not rely on one wall-clock result.

## 68.4 Measure pool waiting

Pool performance is not just query duration.

A request can spend:

```text
5 ms executing
+
80 ms waiting for a connection
```

The application experiences 85 ms.

That wait is part of the system behavior.

## 68.5 Measure errors

Record:

- pool timeouts;
- database errors;
- connection errors.

A configuration that has high throughput but also frequent timeouts is not automatically successful.

---

# 69. What the Benchmark Should Answer

Do not ask:

> "What pool size should I use?"

Ask:

> "What pool sizes produce acceptable throughput, latency, database pressure, and failure behavior for this workload?"

A useful result might be:

```text
pool 1:
low DB pressure
high queueing

pool 5:
higher throughput
moderate wait

pool 12:
similar throughput
more DB contention

pool 16:
no meaningful gain
higher latency
```

Those are example patterns only.

Do not insert them into your real benchmark.

Your measured environment decides the result.

---

# 70. Failure Injection

A connection pool should be tested under failure, not only success.

Include:

- hold connections longer than normal;
- leak one;
- stop PostgreSQL;
- restart PostgreSQL;
- create more workers than pool capacity;
- use deliberately slow local SQL;
- keep transactions open longer than expected;
- trigger application retries while the pool is under pressure.

For every failure, ask:

```text
What happened?
Why?
How long did recovery take?
Which resource was constrained?
```

---

# 71. Debugging Exercises

## Problem 1 — Pool timeout

### Symptoms

```text
PoolTimeout
```

### Root cause candidates

- all connections busy;
- slow queries;
- leaked connections;
- excessive concurrency;
- pool too small for workload.

### Debug

Inspect:

```text
pool utilization
requests waiting
query durations
pg_stat_activity
```

### Production lesson

Pool timeout is a symptom. Find the cause.

---

## Problem 2 — Connection leak

### Symptoms

Pool gradually becomes exhausted.

### Root cause

A checkout path does not always return the connection.

### Fix

Use:

```python
with pool.connection():
    ...
```

### Prevention

Review early returns and exception paths.

---

## Problem 3 — Pool too large

### Symptoms

Increasing pool size decreases throughput.

### Root cause

More concurrent queries create more contention.

### Debug

Compare:

```text
pool size
DB CPU
DB I/O
query latency
lock waits
throughput
```

### Production lesson

More concurrency can reduce throughput.

---

## Problem 4 — Forked workers reuse inherited connections

### Symptoms

Unexpected connection failures or broken communication after forking.

### Root cause

Connections/pool state was created before process boundaries were established.

### Fix

Create a process-local pool after process startup/fork.

### Production lesson

Process ownership matters.

---

## Problem 5 — PostgreSQL restarted

### Symptoms

Existing operations fail.

Later operations succeed.

### Root cause

Previously established connections became invalid.

### Debug

Compare:

```text
connection errors
pool replacement activity
PostgreSQL availability
```

### Production lesson

Recovery of future checkouts does not guarantee recovery of failed in-flight work.

---

## Problem 6 — PgBouncer transaction mode breaks session state

### Symptoms

A `SET` configuration appears inconsistent across requests/transactions.

### Root cause

Logical client is not guaranteed to keep the same backend session.

### Fix

Either:

- remove the session-state dependency;
- use session pooling;
- explicitly configure supported parameter tracking;
- isolate session-dependent work.

### Production lesson

Session semantics matter.

---

## Problem 7 — `LISTEN` stops behaving as expected

### Root cause

Persistent listening requires session continuity.

### Fix

Use an architecture where the listening connection remains attached to the same PostgreSQL session.

### Production lesson

Event-listening state is not interchangeable with ordinary transaction work.

---

## Problem 8 — Prepared statement compatibility problem

### Symptoms

Errors occur only when PgBouncer transaction pooling is introduced.

### Root cause possibilities

- application uses SQL-level prepared statements;
- PgBouncer prepared-statement tracking is disabled;
- client and pooler versions/configurations differ;
- migration changes result/argument types and cached plans become stale.

### Fix

Inspect:

```text
prepared-statement mechanism
PgBouncer mode
PgBouncer version
max_prepared_statements
application behavior
```

### Production lesson

Version/configuration compatibility matters.

---

## Problem 9 — Serverless connection storm

### Symptoms

Database connection count spikes during traffic bursts.

### Root cause

Many runtime instances create independent pools/connections.

### Fix

Model aggregate concurrency and evaluate external pooling/proxy options.

### Production lesson

Scale-out multiplies connection demand.

---

## Problem 10 — Retry storm causes pool exhaustion

### Symptoms

Pool timeout rate increases after transient database failures.

### Root cause

Retries multiply concurrent attempts.

### Fix

Coordinate:

```text
retry count
backoff
concurrency
pool size
database capacity
```

### Production lesson

Resilience mechanisms can amplify load.

---

# 72. Transaction + Pool Interaction Lab

Topic 04 is a prerequisite.

Consider:

```text
Pool size = 3

Worker A:
long transaction

Worker B:
short transaction

Worker C:
short transaction

Worker D:
needs a connection
```

A simple illustration:

```text
Connection 1 → A
Connection 2 → B
Connection 3 → C
                    ↓
Worker D → waits
```

Now suppose:

```text
A holds transaction for 30 seconds
```

Connection 1 remains occupied.

If B and C also become slow, D waits even longer.

The important lesson:

> **Long transactions reduce pool availability because the transaction holds the connection.**

This is why connection pooling and transaction design must be considered together.

---

# 73. Failure Cascade Case Study

Suppose the database suddenly becomes slower.

```text
Database becomes slower
        ↓
transactions last longer
        ↓
connections remain checked out longer
        ↓
pool fills
        ↓
wait times rise
        ↓
pool timeouts occur
        ↓
application retries
        ↓
more concurrent attempts
        ↓
more pressure on database
```

Now ask:

1. Is pool size definitely the root cause?
2. Is SQL slower?
3. Is the database CPU-bound?
4. Is storage saturated?
5. Are locks causing waits?
6. Are connections being leaked?
7. Are retries multiplying load?

This is production reasoning.

---

# 74. Production Dashboard Thinking

Interpret metrics as a system.

## High pool utilization + low wait

Could indicate:

```text
pool is being efficiently used
```

But verify that database latency remains healthy.

## High utilization + high wait

Possible causes:

```text
pool capacity too low
query duration too high
database slow
burst concurrency
```

## Low utilization + high latency

The bottleneck may be:

```text
database execution
network
external dependency
application processing
```

Pool size is not necessarily the problem.

## High connection count + low throughput

Potential interpretation:

```text
too much database concurrency
```

This can increase contention.

Again, these are hypotheses.

Measure before changing configuration.

---

# 75. Pool Metrics and `pg_stat_activity`

A good operational investigation correlates application and database state.

Example:

```text
Application:
pool_max = 10
pool_available = 0
requests_waiting = 25

PostgreSQL:
active sessions = 10
query durations rising
```

This suggests the pool is full because all connections are busy.

Now compare:

```text
Application:
pool_max = 10
pool_available = 8
requests_waiting = 0

PostgreSQL:
latency high
```

Increasing the pool would have little reason based on those observations.

The database-side bottleneck is elsewhere.

---

# 76. Production Design Checklist

## Connection Pool Production Checklist

### Configuration

- Is pool lifecycle aligned with process lifecycle?
- Is `max_size` bounded?
- Is `timeout` configured?
- Is `min_size` deliberate?
- Are credentials configured securely?
- Are `max_idle` and `max_lifetime` considered?

### Capacity

- How many application processes exist?
- How many instances/replicas exist?
- How many pools exist?
- What is the maximum possible connection count?
- What is PostgreSQL `max_connections`?
- How much operational reserve exists?
- Are there hidden/other consumers?

### Health

- What happens after PostgreSQL restarts?
- Can broken connections be replaced?
- Are health checks appropriate?
- Is connection lifetime managed?

### Correctness

- Are connections always returned?
- Are transaction boundaries completed before return?
- Can session state leak between logical operations?
- Are connection-owning objects process-local?

### Concurrency

- How many database operations can happen simultaneously?
- What happens when the pool is exhausted?
- What is the measured checkout wait?
- Are retries increasing demand?

### Pooler

- Is PgBouncer present?
- Which pooling mode?
- Do session features require affinity?
- Are prepared statements compatible?
- Does `LISTEN` depend on stable sessions?
- Are advisory locks session-level or transaction-level?

### Serverless / Batch

- Does application pooling have enough lifetime to provide reuse?
- Can many runtime instances create connection storms?
- Is external pooling available?

---

# 77. Production Hardening

## From Working Pool Code to Production Pool Architecture

### Level 1 — No pooling

```python
with psycopg.connect(...) as conn:
    ...
```

Useful for simple scripts and workloads with low connection reuse.

### Level 2 — Basic pool

```python
with ConnectionPool(
    conninfo="postgresql://...",
    min_size=2,
    max_size=8,
) as pool:
    ...
```

Provides connection reuse.

### Level 3 — Safe lifecycle

```python
with pool.connection() as conn:
    ...
```

Makes borrow/return behavior explicit.

### Level 4 — Bounded concurrency

Use:

```text
max_size
+
checkout timeout
```

to create a deliberate concurrency boundary.

### Level 5 — Health management

Evaluate:

```text
check
max_idle
max_lifetime
reconnect behavior
```

### Level 6 — Observability

Measure:

```text
pool utilization
wait time
timeouts
connection creation
PostgreSQL connection count
```

### Level 7 — Multi-process capacity model

Account for:

```text
replicas
processes
workers
pools
other services
```

### Level 8 — PgBouncer where justified

Evaluate:

```text
client connection count
backend capacity
session requirements
pooling mode
feature compatibility
```

The maturity progression is:

```text
working code
    ↓
controlled resource lifecycle
    ↓
bounded concurrency
    ↓
health
    ↓
observability
    ↓
platform-wide capacity
    ↓
architecture-level pooling
```

---

# 78. Internal Mechanics — What Happens When a Connection Is Borrowed?

Consider:

```python
with pool.connection() as conn:
    conn.execute("SELECT 1")
```

Conceptually:

## Step 1 — Application asks the pool

```text
pool.connection()
```

The pool looks for usable capacity.

## Step 2 — Idle connection exists

If an idle connection is available:

```text
idle connection
    ↓
borrow
```

## Step 3 — No idle connection, but capacity remains

If:

```text
current size < max_size
```

the pool can create additional capacity.

Current psycopg pool documentation notes that connection creation is handled by background workers for normal `ConnectionPool` behavior, rather than directly by the requesting client thread. citeturn499735search1

## Step 4 — Capacity exhausted

If:

```text
current size = max_size
```

the client waits.

```text
wait
  ↓
connection returns
  ↓
client continues
```

or:

```text
timeout
  ↓
PoolTimeout
```

## Step 5 — Application uses connection

```python
conn.execute("SELECT 1")
```

## Step 6 — Context exits

The connection is returned to the pool.

The normal connection context behavior applies to transaction completion, and unusable connections can be replaced according to pool behavior. citeturn499735search0

## Step 7 — Pool manages lifetime

The pool may:

- keep the connection idle;
- retire it after `max_idle`;
- retire it after `max_lifetime`;
- replace it if unhealthy.

The key distinction is:

```text
Borrowing a connection
    ≠
creating a new PostgreSQL connection
```

A mature engineer asks which operation actually occurred.

---

# 79. Application Pool vs PgBouncer Internal Model

## Application pool

```text
Worker
  ↓
Application pool
  ↓
PostgreSQL connection
```

The pool decides which process-local connection to lend to a worker.

## PgBouncer

```text
Client
  ↓
PgBouncer
  ↓
PostgreSQL server connection
```

PgBouncer decides which server connection is assigned according to pooling mode.

## Why this matters

The physical connection can have session-specific state.

Therefore:

```text
application pool
```

and:

```text
PgBouncer pooling mode
```

affect different parts of the lifecycle.

---

# 80. Pooling and Transaction Pooling

A useful distinction:

```text
Application pool:
"Give me a reusable connection."

PgBouncer transaction pool:
"Give me a PostgreSQL server connection for this transaction."
```

This explains why transaction pooling can aggressively reuse backend sessions.

But it also explains why:

```text
SET
PREPARE
LISTEN
session advisory locks
```

can become compatibility concerns.

The logical client and physical server session are no longer the same concept.

---

# 81. Testing Strategy

Connection pools need tests for both correctness and operational failure.

## Test categories

### Pool construction

- correct configuration;
- expected minimum/maximum size.

### Checkout

- connection can be borrowed;
- connection becomes unavailable while in use.

### Return

- returned after success;
- returned after exception.

### Pool timeout

- all capacity intentionally occupied;
- next request reaches timeout.

### Leak

- leaked checkout reduces available capacity;
- fixed code restores capacity.

### Health

- broken connection is detected/replaced as configured.

### PostgreSQL restart

- existing work can fail;
- new work can recover.

### Concurrency

- multiple workers share pool correctly;
- no pool over-expansion beyond configured limits.

### Transaction cleanup

- connection is not returned with unintended transaction state.

### Shutdown

- pool closes during process shutdown.

### Process boundaries

- pools are created within their owning process;
- no inherited connection sharing.

### PgBouncer compatibility

- session settings;
- prepared statements;
- `LISTEN`;
- advisory locks.

Do not create a separate test file for this chapter; the examples are intentionally kept inline.

---

# 82. Inline Test Example — Pool Timeout

```python
import time
from concurrent.futures import ThreadPoolExecutor

from psycopg_pool import ConnectionPool, PoolTimeout


def hold_connection(pool: ConnectionPool) -> None:
    with pool.connection() as conn:
        conn.execute("SELECT 1")
        time.sleep(2)


def test_pool_exhaustion():
    with ConnectionPool(
        conninfo="postgresql://...",
        min_size=2,
        max_size=2,
        timeout=0.2,
    ) as pool:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(hold_connection, pool)
                for _ in range(3)
            ]

            errors = 0

            for future in futures:
                try:
                    future.result()
                except PoolTimeout:
                    errors += 1

        assert errors >= 1
```

Timing can make concurrent tests nondeterministic.

The educational objective is the capacity model:

```text
2 connections
3 borrowers
    ↓
at least one must wait
```

---

# 83. Inline Test Example — Safe Return

```python
def use_pool(pool: ConnectionPool) -> int:
    with pool.connection() as conn:
        row = conn.execute("SELECT 1").fetchone()

    return row[0]
```

After the `with` block:

```text
connection returned
```

The function does not need to explicitly return the connection.

---

# 84. Interview Questions

## Basic

### 1. What is connection pooling?

A managed set of reusable database connections.

### 2. Why is opening a PostgreSQL connection expensive?

Because connection establishment includes network, authentication, session setup, and other environment-dependent work.

### 3. What is `min_size`?

The minimum number of connections the pool tries to maintain.

### 4. What is `max_size`?

The maximum number of connections the pool can manage.

### 5. What is pool `timeout`?

The maximum time a borrower waits to acquire a connection before the pool reports failure.

### 6. What happens when all connections are busy?

New borrowers wait up to the configured timeout or fail sooner if another queue limit/configuration applies.

---

## Intermediate

### 7. Why can a larger connection pool be slower?

Because it increases database concurrency and can increase contention for CPU, I/O, locks, memory, and other resources.

### 8. How do you size a pool?

Start with:

```text
database capacity
+
replicas
+
processes
+
workers
+
query duration
+
other connection consumers
```

Then benchmark.

### 9. What is a connection leak?

A borrowed connection that is not returned correctly.

### 10. Why should one pool exist per process?

Because the pool is process-local application state and connections should be owned within the process that created them.

### 11. Why can't connections simply be shared across forked processes?

A fork duplicates process memory but does not turn a live network/database session into a safe process-shared resource.

### 12. What happens when PostgreSQL restarts?

Existing connections may fail; the pool can recreate future capacity according to its health/reconnect behavior, while in-flight operations may still fail and need application handling.

---

## Advanced

### 13. How do application pool size and PostgreSQL `max_connections` interact?

Aggregate possible connections across all pools must remain within the database's safe capacity with operational reserve.

### 14. How would you size pools across 10 replicas?

Build an aggregate model:

```text
10 replicas
×
processes per replica
×
max_size
+
other consumers
```

Then validate against measured concurrency and database capacity.

### 15. Why can retries create connection pressure?

Retries create additional concurrent work. If the original attempts still occupy connections, retries can increase pool occupancy.

### 16. What is PgBouncer?

An external PostgreSQL connection pooler/proxy that can reuse backend server connections among many client connections.

### 17. What is the difference between session and transaction pooling?

Session pooling keeps a backend connection for the client session; transaction pooling returns the backend after each transaction.

### 18. Why can `LISTEN` break under transaction pooling?

Because listening is session-specific and the logical client is not guaranteed to remain attached to the same backend session.

### 19. Why can session-level advisory locks break?

Because session-level locks belong to the physical PostgreSQL session, which can change under transaction pooling.

### 20. How can prepared statements interact with poolers?

Prepared-state/session assumptions can conflict with backend reassignment. Modern PgBouncer can support protocol-level prepared statements in transaction/statement modes with configuration, but SQL-level prepare semantics remain distinct. citeturn560933search0turn560933search1

### 21. When would you avoid an application-level pool?

Potentially in very short-lived workloads with little opportunity for reuse, or where an external pooler/proxy is the better connection-management layer.

### 22. How would you investigate pool exhaustion?

Correlate:

```text
pool size
pool available
requests waiting
checkout latency
timeouts
query durations
PostgreSQL connection states
```

---

# 85. Architecture Questions

## 1. Design a connection strategy for a Python ETL worker with 32 concurrent tasks.

Reason from:

```text
task concurrency
+
expected query duration
+
database capacity
+
pool capacity
+
timeout
```

Do not assume:

```text
pool = 32
```

is correct.

---

## 2. PostgreSQL supports 300 connections. Multiple services share it. How do you construct a capacity model?

Start by calculating:

```text
sum of possible connections across all services
+
administrative reserve
```

Then compare this with:

```text
real measured concurrency
```

and the architecture of any external pooler.

---

## 3. A team doubles pool size but throughput decreases. How do you investigate?

Compare:

```text
before/after
query latency
DB CPU
DB I/O
lock waits
connection count
throughput
```

Ask whether the larger pool increased contention.

---

## 4. A service experiences intermittent pool timeouts. What metrics and PostgreSQL views do you inspect?

Application:

```text
pool_available
requests_waiting
checkout latency
timeouts
```

Database:

```sql
pg_stat_activity
```

Also inspect query duration and other database health signals.

---

## 5. PostgreSQL restarts and the application takes minutes to recover. How do you diagnose it?

Trace:

```text
database availability
→ connection failures
→ pool reconnect behavior
→ checkout behavior
→ retry policy
→ recovery time
```

---

## 6. A serverless workload creates too many PostgreSQL connections. What alternatives would you evaluate?

Consider:

```text
smaller per-instance connection usage
+
runtime reuse
+
external database proxy/pooler
+
concurrency limits
```

---

## 7. PgBouncer transaction mode is used and developers report inconsistent session state. Why?

Because logical client transactions can execute on different PostgreSQL backend sessions.

Session state is therefore not automatically stable across transactions.

---

## 8. A workload depends on `LISTEN` / `NOTIFY`. What pooling constraints exist?

The listener needs stable session affinity.

Do not treat it like ordinary transaction-pooled request traffic.

---

## 9. An application uses prepared statements and PgBouncer. What compatibility questions should you investigate?

Ask:

```text
What type of prepared statement?
What PgBouncer version?
What pool mode?
Is max_prepared_statements enabled?
Does the client rely on SQL-level PREPARE?
Are migrations changing result types?
```

---

## 10. How would you choose between application pooling, PgBouncer, both, or neither?

Reason from:

```text
workload
+
runtime model
+
concurrency
+
database capacity
+
connection reuse opportunity
+
session-state requirements
+
operational complexity
+
measurement
```

There is no universal best architecture.

---

# 86. Connection Pool Code Review Checklist

## Lifecycle

- Is the pool created at the correct lifecycle boundary?
- Is a new pool accidentally created per request?
- Is the pool closed correctly?
- Are process-local pools created after process creation?

## Capacity

- Is `max_size` bounded?
- Is the total possible connection count known?
- Are all replicas and worker processes included?
- Is PostgreSQL `max_connections` treated as a constraint?
- Is operational reserve available?

## Borrow/Return

- Are connections always returned?
- Can early returns leak connections?
- Are exception paths safe?
- Is context management used?

## Transaction State

- Are transactions committed/rolled back before return?
- Can a connection return to the pool with unintended state?
- Are long transactions holding connections too long?

## Health

- What happens after PostgreSQL restart?
- Are broken connections replaced?
- Are health checks configured deliberately?
- Are `max_idle` and `max_lifetime` appropriate?

## Concurrency

- How many workers can request connections?
- What happens when the pool is exhausted?
- What is measured checkout wait?
- Are retries increasing demand?

## PgBouncer

- Is PgBouncer present?
- Which pooling mode?
- Is session state required?
- Are prepared statements compatible?
- Does `LISTEN` require a dedicated session?
- Are advisory locks session-level?
- Are migration-time session-state assumptions safe?

## Runtime Model

- Is this a long-lived service?
- Is this a worker process?
- Is this a short-lived batch?
- Is this serverless?
- Could application-level pooling create a connection storm?

---

# 87. Transaction + Pool Interaction in Code Review

When you see:

```python
with pool.connection() as conn:
    with conn.transaction():
        do_expensive_python_work()
        conn.execute(...)
```

ask:

> Why is the expensive Python work inside the transaction?

It may be accidental.

A better pattern may be:

```python
prepare_data()

with pool.connection() as conn:
    with conn.transaction():
        write_data()
```

This reduces the time that:

```text
connection
+
transaction
```

are occupied.

Remember:

> **A pooled connection is still a real PostgreSQL connection.**

Pooling does not make long transaction scope free.

---

# 88. Pool Sizing Decision Framework

Before choosing a pool size, ask these ten questions.

## 1. How many application processes exist?

Count real processes.

## 2. How many instances/replicas exist?

Scale-out multiplies connections.

## 3. What is maximum concurrent database work?

Use actual workload concurrency.

## 4. How long are connections occupied?

A 50 ms query and a 5-minute query create very different pool demands.

## 5. What is PostgreSQL's connection capacity?

Know:

```text
max_connections
```

and operational reserve.

## 6. What other consumers need connections?

Include:

- administration;
- monitoring;
- migrations;
- other services.

## 7. Is PgBouncer present?

If yes, distinguish:

```text
client connections
```

from:

```text
backend server connections
```

## 8. What happens when the pool is exhausted?

Define:

```text
wait
timeout
backpressure
retry
```

## 9. What does the benchmark say?

Measure:

```text
throughput
latency
wait
DB pressure
```

## 10. What is the operational reserve?

Leave room for:

```text
incident response
maintenance
scaling bursts
```

---

# 89. Worked Pool-Sizing Reasoning

Suppose:

```text
Application:
12 replicas

Each replica:
3 worker processes

Candidate pool:
max_size = 4
```

Potential application connections:

```text
12 × 3 × 4
=
144
```

Now suppose other clients require:

```text
25
```

Potential total:

```text
169
```

If PostgreSQL has:

```text
max_connections = 200
```

that leaves only:

```text
31
```

connections for reserve.

Is that safe?

You do not know yet.

You need to ask:

- Are all 144 connections actually needed?
- How long are queries?
- Is PgBouncer used?
- Are there burst conditions?
- What other hidden consumers exist?
- What happens during deployments when old and new replicas coexist?
- Do retries temporarily increase demand?

This is why pool sizing is an architecture problem rather than a one-line configuration choice.

---

# 90. Deployment Rollout Capacity

An advanced capacity issue appears during deployment.

Suppose:

```text
old version:
10 replicas

new version:
10 replicas
```

During a rolling deployment, there can be a period where:

```text
old replicas + new replicas
```

both exist.

If each replica has its own pool, connection demand can temporarily increase.

For example:

```text
normal:
10 replicas × 4 connections = 40

rollout overlap:
20 replicas × 4 connections = 80
```

A capacity model that considers only steady state can miss this transient.

Production pool sizing should therefore consider:

```text
steady state
+
deployment state
+
failure/retry state
```

---

# 91. Pooling and Horizontal Scaling

Horizontal scaling multiplies process-local pools.

```text
1 replica
    ↓
1 pool
    ↓
5 connections

10 replicas
    ↓
10 pools
    ↓
50 connections
```

A database does not know that each group of five came from a separate application process.

It sees:

```text
50 PostgreSQL sessions
```

This is why platform teams must coordinate application capacity with database capacity.

---

# 92. Pooling and Autoscaling

Autoscaling can create connection spikes.

```text
load increases
   ↓
replicas increase
   ↓
new pools created
   ↓
new connections created
```

A scaling system can therefore increase database pressure even before query volume grows proportionally.

A good architecture asks:

> What is the maximum connection increase caused by one scaling event?

This matters especially when:

- autoscaling is rapid;
- serverless instances are ephemeral;
- database capacity is fixed.

---

# 93. Connection Pool and Backpressure

A bounded pool can provide useful backpressure.

Suppose:

```text
100 workers
pool max = 10
```

The pool does not allow all 100 workers to consume database connections at once.

This can protect PostgreSQL.

The waiting workers experience:

```text
backpressure
```

But if waiting becomes too long, the system should fail deliberately rather than queue forever.

That is why:

```text
timeout
```

matters.

---

# 94. Pool Timeout as a Control

A pool timeout is not just an error.

It is a policy statement:

> "If database capacity is unavailable for this long, this operation should stop waiting."

This can be preferable to:

```text
unbounded queue
```

because unbounded queues can turn a temporary database slowdown into a memory and latency problem inside the application.

---

# 95. Pool Health After Broken Connections

Imagine:

```text
pool
[healthy]
[healthy]
[broken]
[healthy]
```

If the broken connection is handed to a worker, the worker discovers failure during use.

With a health-check policy:

```text
borrow
 ↓
check
 ↓
broken detected
 ↓
discard
 ↓
replacement
```

The trade-off is additional work on checkout.

There is no universal answer.

Use health checks when their operational value justifies the cost.

---

# 96. Connection Lifetime and Session State

Long-lived physical connections can accumulate session state.

Examples include:

```sql
SET search_path ...
SET TimeZone ...
SET application_name ...
```

A connection pool therefore benefits from returning connections to a predictable baseline.

This is one reason pool reset/health lifecycle matters.

The application should avoid leaving arbitrary state behind for the next borrower.

Current psycopg pool documentation includes a `reset` callback that is invoked on a connection after it is returned, with the connection expected to be left in an idle/clean state when reset completes. citeturn499735search0

This is an advanced extension point; use it deliberately rather than building a reset framework prematurely.

---

# 97. Application Pool State Hygiene

A pooled connection may survive many logical requests.

Therefore:

```text
request A
    ↓
uses connection 3
    ↓
leaves session state
    ↓
request B
    ↓
receives connection 3
```

If request B assumes defaults, the application can become nondeterministic.

The production principle is:

> **A pooled connection must have predictable state when handed to the next borrower.**

That includes:

- transaction state;
- session settings;
- prepared/session state;
- temporary objects or other session-scoped behavior where relevant.

---

# 98. Pooling Architecture and Security

Connection pooling interacts with security because the physical connection belongs to a database identity.

Do not create one superuser pool simply because it is easier.

The same least-privilege principles from Topic 03 apply.

For example:

```text
read-only extractor
    ↓
pool
    ↓
PostgreSQL
```

is a safer boundary than:

```text
application
    ↓
superuser pool
    ↓
PostgreSQL
```

A pool does not reduce privileges.

It only changes connection reuse.

---

# 99. Pooling and Read/Write Roles

Some architectures separate:

```text
read pool
+
write pool
```

with different database identities or endpoints.

Conceptually:

```text
read workers
    ↓
read pool
    ↓
read endpoint

write workers
    ↓
write pool
    ↓
write endpoint
```

The decision depends on the deployment.

The important principle is:

> Pool configuration does not replace database authorization design.

---

# 100. Pooling and Connection Strings

A pool usually receives connection information that it uses whenever it creates or replaces physical connections.

Conceptually:

```text
pool configuration
    ↓
connection creation
    ↓
same connection policy
```

This is another reason to centralize configuration.

Avoid:

```text
service A → pool connection string X
service B → pool connection string Y
```

when both are supposed to target the same environment and should follow the same policy.

---

# 101. What a Pool Does Not Solve

Connection pooling does not automatically solve:

- slow SQL;
- poor indexes;
- inefficient joins;
- bad transaction scope;
- SQL injection;
- duplicate data;
- incorrect retry logic;
- schema design;
- data-quality problems.

It only addresses one class of problem:

```text
database connection lifecycle and concurrency
```

This distinction prevents overusing the abstraction.

---

# 102. Connection Pooling Is a Resource-Management Problem

Return to the full mental model:

```text
Application concurrency
        +
Database connection limits
        +
Connection creation cost
        +
Server resource consumption
        +
Workload duration
        +
Process/thread architecture
        +
Pooler architecture
        +
Operational constraints
```

Every configuration decision belongs somewhere in that model.

---

# 103. A Senior Engineer's Pooling Review

Suppose someone proposes:

```python
ConnectionPool(
    conninfo="postgresql://...",
    min_size=20,
    max_size=100,
)
```

Do not respond:

> "100 is too high."

Ask:

```text
How many application processes?
How many replicas?
What is query concurrency?
How long are connections held?
What is max_connections?
What other services use the database?
Is PgBouncer present?
What does the benchmark show?
What is the failure-mode behavior?
```

This changes the conversation from opinion to capacity modeling.

---

# 104. Production Architecture Decision

A mature decision can look like:

```text
Requirement
    ↓
Workload characterization
    ↓
Connection demand model
    ↓
Candidate architectures
    ├── direct connection
    ├── application pool
    ├── PgBouncer
    └── both
    ↓
benchmark + failure testing
    ↓
operational review
    ↓
decision
```

The important point is that pooling is an architectural decision, not a library checkbox.

---

# 105. Common Mistakes

## Mistake 1 — Creating a new pool per request

### Beginner belief

Pooling is useful, so every request should create one.

### What actually happens

Each request builds a new resource manager.

### Production consequence

More connection churn and complexity.

### Correct mental model

Pool lifetime should match process/application lifetime.

---

## Mistake 2 — Huge pools "for speed"

### Beginner belief

More concurrency means more throughput.

### What actually happens

Database contention rises.

### Production consequence

Latency and throughput may get worse.

### Correct mental model

Find the measured concurrency sweet spot.

---

## Mistake 3 — Sharing connections across forked processes

### Beginner belief

Fork copies the Python object, so it should work.

### What actually happens

A live database session is not a safe process-shared resource.

### Production consequence

Unpredictable communication/session state.

### Correct mental model

Create process-local connections after the process boundary is established.

---

## Mistake 4 — Using session features behind transaction pooling

### Beginner belief

The logical client remains the same, so the session remains the same.

### What actually happens

The backend connection can change across transactions.

### Production consequence

Session state becomes unreliable.

### Correct mental model

Transaction pooling trades session affinity for backend connection reuse.

---

## Mistake 5 — Ignoring total connections

### Beginner belief

My pool has max 5, so the application has 5 database connections.

### What actually happens

Every process/replica can have its own pool.

### Production consequence

Connection count multiplies.

### Correct mental model

Capacity is platform-wide.

---

## Mistake 6 — Treating `max_connections` as a target

### Beginner belief

We should use all available connections.

### What actually happens

Database and operational reserve disappear.

### Production consequence

Incidents become harder to recover.

### Correct mental model

`max_connections` is a constraint.

---

## Mistake 7 — No checkout timeout

### Beginner belief

Waiting longer is safer.

### What actually happens

Requests can queue indefinitely.

### Production consequence

Latency and memory grow.

### Correct mental model

Bound waiting explicitly.

---

## Mistake 8 — No health policy

### Beginner belief

A connection is healthy until it is closed.

### What actually happens

Network/server failures can invalidate idle sessions.

### Production consequence

A broken connection may reach application code.

### Correct mental model

Health is a lifecycle concern.

---

## Mistake 9 — Retrying when the pool is full

### Beginner belief

Retry will eventually succeed.

### What actually happens

Each retry competes for the same scarce capacity.

### Production consequence

Retry storm.

### Correct mental model

Retry policy and pool capacity must be designed together.

---

## Mistake 10 — Assuming PgBouncer makes every application feature transparent

### Beginner belief

PgBouncer only changes connection count.

### What actually happens

Pooling mode can change session continuity semantics.

### Production consequence

`SET`, `LISTEN`, prepared statements, and locks may behave differently.

### Correct mental model

A pooler is part of the application's database architecture.

---

# 106. Final Mental Model

## The Connection Pool Mental Model

```text
A PostgreSQL connection is a limited server resource.

A pool reuses a controlled number of those resources.

Application concurrency can exceed pool size.

When the pool is full:
    callers wait or time out.

A larger pool is not automatically faster.

The correct pool size depends on:
    workload
    concurrency
    database capacity
    process/replica count
    query duration
    architecture
    measurement
```

Now distinguish the three layers:

```text
Application Pool
    ↓
controls connection reuse inside a process


PgBouncer
    ↓
controls/reuses PostgreSQL server connections across clients


PostgreSQL max_connections
    ↓
server-side connection capacity constraint
```

And finally:

```text
Connection lifecycle
+
Transaction lifecycle
+
Concurrency
+
Database capacity
+
Operational visibility
```

That is the heart of Topic 05.

---

# 107. Final Review

## What You Now Understand

You now understand:

- what a PostgreSQL connection represents;
- why connection creation can be expensive;
- why server connections are limited resources;
- what a connection pool is;
- borrow/use/return semantics;
- `ConnectionPool`;
- `min_size`;
- `max_size`;
- `timeout`;
- transaction cleanup before returning connections;
- pool lifecycle;
- pool exhaustion;
- connection leaks;
- `max_idle`;
- `max_lifetime`;
- health checks;
- database restart recovery;
- pool sizing;
- process/replica multiplication;
- `max_connections`;
- fork safety;
- concurrency;
- PgBouncer;
- session/transaction/statement pooling;
- session-state compatibility;
- prepared-statement compatibility;
- `LISTEN`;
- advisory locks;
- serverless connection storms;
- batch-job trade-offs;
- pool/retry interaction;
- operational monitoring;
- async pool awareness;
- failure cascades;
- architecture-level pool decisions.

## What You Can Implement

You should be able to:

- create and use a `ConnectionPool`;
- borrow and return connections safely;
- configure pool limits;
- avoid connection leaks;
- handle pool exhaustion deliberately;
- inspect pool statistics;
- correlate pool behavior with `pg_stat_activity`;
- test restart recovery;
- model aggregate database connection demand;
- evaluate PgBouncer;
- reason about pooling modes;
- test session-dependent features;
- choose between direct connections, application pooling, PgBouncer, or a layered design based on requirements.

## What You Can Debug

You should be able to diagnose:

```text
PoolTimeout
connection leak
over-sized pool
under-sized pool
long transaction occupying pool capacity
database restart
broken connection
fork misuse
serverless connection storm
PgBouncer session-state incompatibility
prepared statement incompatibility
LISTEN/session-affinity issues
retry-induced pool exhaustion
```

## What Comes Next

Next:

`06-sqlalchemy-core-engine-and-metadata.md`

That topic introduces SQLAlchemy Core and a higher-level abstraction over database engines, connections, SQL expressions, metadata, and pooling.

Do not re-teach SQLAlchemy here.

The purpose of Topic 05 is to make connection lifecycle and pooling behavior understandable before higher-level abstractions hide some of that machinery.

---

# 108. Production Rules to Remember

1. **Connections are limited server resources.**
2. **Pools exist to reuse connections.**
3. **Borrow → use → return.**
4. **Never leak checked-out connections.**
5. **Keep pool sizes bounded.**
6. **Bigger pools are not automatically faster.**
7. **Size pools using total process and replica concurrency.**
8. **Treat `max_connections` as a server constraint.**
9. **Leave operational reserve.**
10. **Keep pools process-local.**
11. **Never casually reuse connections across `fork()`.**
12. **Monitor pool utilization and wait time.**
13. **Test database-restart behavior.**
14. **Understand the difference between application pooling and PgBouncer.**
15. **Know which session features require session continuity.**
16. **Treat prepared statements as a compatibility concern when poolers are introduced.**
17. **Do not automatically add application pooling to short-lived jobs or serverless workloads.**
18. **Design retry policy and pool capacity together.**
19. **Use timeouts so exhaustion fails deliberately.**
20. **Measure before changing pool size.**

---

# 109. One-Page Operational Cheat Sheet

```text
CONNECTION
    = one PostgreSQL session/resource

POOL
    = manager of reusable connections

BORROW
    = obtain temporary access

RETURN
    = give connection back to pool

min_size
    = minimum managed pool capacity

max_size
    = maximum managed connections

timeout
    = maximum wait for checkout

max_idle
    = retirement policy for excess idle connections

max_lifetime
    = connection rotation policy

PoolTimeout
    = connection unavailable within allowed wait

ONE POOL PER PROCESS
    = normal process-local ownership model

FORK
    = create process-local connections after process boundary

max_connections
    = database capacity constraint

POOL EXHAUSTION
    = all available connections are busy

CONNECTION LEAK
    = borrowed connection not returned

PGBOUNCER
    = external PostgreSQL connection pooler

SESSION POOLING
    = backend connection held for client session

TRANSACTION POOLING
    = backend connection held for transaction

STATEMENT POOLING
    = backend connection reused after each statement

LISTEN
    = session-oriented feature

SESSION-LEVEL ADVISORY LOCK
    = session-oriented state

PREPARED STATEMENTS
    = compatibility depends on mechanism + pool mode + versions/configuration

SERVERLESS
    = aggregate connection demand can grow rapidly

POOL SIZING
    = workload + concurrency + capacity + process count + measurement
```

---

# 110. Capacity-Planning Worksheet

Use this worksheet before setting a production pool size.

```text
PostgreSQL:
max_connections = __________

Operational reserve = __________

Other consumers = __________

Application:
replicas = __________

processes per replica = __________

worker concurrency per process = __________

Candidate pool max_size = __________

Application connection upper bound:
replicas × processes × pool max
= __________

Potential total including other consumers:
= __________

Observed average connection occupancy = __________

Observed peak connection occupancy = __________

Observed checkout wait = __________

Observed query duration = __________

Observed throughput = __________

Observed timeout rate = __________

PgBouncer present? yes / no

Pooling mode = __________

Session-dependent features? yes / no

Prepared statements? yes / no

LISTEN? yes / no

Session-level advisory locks? yes / no

Operational reserve sufficient? yes / no

Decision:
____________________________________________
```

The worksheet is more valuable than memorizing a pool-size number.

---

# 111. Benchmark Worksheet

Record the actual measurements from your environment.

| Experiment | Pool size | Workers | Queries | Total time | Throughput | Wait | Timeouts | DB connections |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Connection-per-query | N/A | 1 | 5,000 | measure | measure | N/A | measure | measure |
| Pool | 1 | 1 | 5,000 | measure | measure | measure | measure | measure |
| Pool | 2 | 1 | 5,000 | measure | measure | measure | measure | measure |
| Pool | 4 | 32 | workload | measure | measure | measure | measure | measure |
| Pool | 5 | 32 | workload | measure | measure | measure | measure | measure |
| Pool | 8 | 32 | workload | measure | measure | measure | measure | measure |
| Pool | 12 | 32 | workload | measure | measure | measure | measure | measure |
| Pool | 16 | 32 | workload | measure | measure | measure | measure | measure |

Do not replace "measure" with numbers from another environment.

---

# 112. Decision Framework: Direct Connection vs Pool

## Direct connection may be reasonable when

```text
short-lived process
+
very low request volume
+
little opportunity for reuse
```

## Application pool may be reasonable when

```text
long-lived process
+
repeated database access
+
many concurrent workers
+
bounded database capacity requirement
```

## PgBouncer may be reasonable when

```text
many client connections
+
backend PostgreSQL connections need tighter control
+
shared external pool layer makes operational sense
```

## Both may be reasonable when

```text
application needs process-local concurrency control
+
platform needs external backend connection control
```

The decision should still consider session-state requirements and measured workload behavior.

---

# 113. Final Production Scenario

Imagine a production system:

```text
10 container replicas
3 worker processes per container
pool max_size = 5
```

Potential connections:

```text
10 × 3 × 5
=
150
```

The database allows:

```text
max_connections = 200
```

But also requires:

```text
30 connections
```

for other services and operational access.

Now:

```text
150 + 30 = 180
```

Only 20 remain.

Then a deployment starts and temporarily creates:

```text
5 additional replicas
```

Potential connection demand becomes:

```text
15 × 3 × 5 = 225
```

before other consumers.

The architecture is now unsafe even though:

```text
pool max_size = 5
```

looked small in isolation.

This is the production lesson:

> **Pool size must be multiplied by the entire deployment topology.**

---

# 114. Final Architecture Mental Model

```text
                    APPLICATION PLATFORM
                           |
          +----------------+----------------+
          |                |                |
       Replica A        Replica B        Replica C
          |                |                |
       Process 1         Process 1        Process 1
          |                |                |
        Pool A            Pool B          Pool C
          |                |                |
          +----------------+----------------+
                           |
                      PgBouncer
                           |
                   PostgreSQL Server
                           |
                   max_connections
```

Every layer creates a capacity boundary.

The correct engineering question is:

```text
How many logical clients exist?
How many processes exist?
How many pools exist?
How many physical PostgreSQL connections can exist?
How many are actually needed?
How long are they occupied?
What happens during failure and retry?
What happens during deployment?
What does the database observe?
```

---

# 115. Scope Boundary Before Topic 06

You should finish Topic 05 with this mental model:

```text
Connection
    ↓
Transaction/resource lifecycle
    ↓
Pool
    ↓
Borrow / return
    ↓
Capacity
    ↓
Exhaustion
    ↓
Leak detection
    ↓
Health
    ↓
Pool sizing
    ↓
Concurrency
    ↓
Process boundaries
    ↓
Fork safety
    ↓
PgBouncer
    ↓
Pooling modes
    ↓
Feature compatibility
    ↓
Operational monitoring
```

The next topic is:

`06-sqlalchemy-core-engine-and-metadata.md`

Topic 06 will add a higher-level abstraction.

Do not lose the lower-level mental model.

Even when SQLAlchemy manages engines, connections, and pools, production debugging often requires understanding the resources underneath.

---

# 116. Final Quality Audit

Before considering this topic complete, verify:

- [ ] Only `05-connection-pooling.md` was modified.
- [ ] No other files were created or changed.
- [ ] The module starts from beginner-level connection concepts.
- [ ] The module progresses to advanced production architecture.
- [ ] Why pooling exists is explained.
- [ ] Connection creation cost is explained.
- [ ] PostgreSQL connection resources are explained.
- [ ] `ConnectionPool` is demonstrated.
- [ ] `min_size` is explained.
- [ ] `max_size` is explained.
- [ ] `timeout` is explained.
- [ ] Pool lifecycle is explained.
- [ ] Borrow/return semantics are explained.
- [ ] Transaction cleanup before returning connections is explained.
- [ ] Pool health is explained.
- [ ] `max_idle` is covered.
- [ ] `max_lifetime` is covered.
- [ ] Connection health checks are covered.
- [ ] Database restart recovery is demonstrated.
- [ ] Pool sizing is explained using multiple processes/instances.
- [ ] PostgreSQL `max_connections` is treated as a constraint.
- [ ] Operational reserve is discussed.
- [ ] Pool exhaustion is demonstrated.
- [ ] Connection leaks are demonstrated.
- [ ] Leak timeout is demonstrated.
- [ ] 32-thread / pool-size-5 exercise is included.
- [ ] Connection-per-query vs pool benchmark is included.
- [ ] Measurement guidance is included.
- [ ] No fabricated benchmark numbers are included.
- [ ] One-pool-per-process is explained.
- [ ] Fork safety is explained.
- [ ] PgBouncer is explained.
- [ ] Session pooling is explained.
- [ ] Transaction pooling is explained.
- [ ] Statement pooling is introduced.
- [ ] Session-state compatibility is explained.
- [ ] Prepared-statement compatibility is explained.
- [ ] `LISTEN` compatibility is explained.
- [ ] Advisory-lock compatibility is explained.
- [ ] Application pool vs PgBouncer distinction is clear.
- [ ] Cases where application pooling should not be used are covered.
- [ ] Short-lived batch jobs are covered.
- [ ] Serverless connection storms are covered.
- [ ] Monitoring and observability are covered.
- [ ] `pg_stat_activity` is used.
- [ ] Async pool awareness is included.
- [ ] Pooling failure cascades are explained.
- [ ] Retry interaction is explained.
- [ ] Failure-injection exercises are included.
- [ ] Debugging exercises are included.
- [ ] Anti-patterns are included.
- [ ] Production design patterns are included.
- [ ] Production hardening is included.
- [ ] Testing strategy is included.
- [ ] Code review checklist is included.
- [ ] Pool sizing framework is included.
- [ ] Interview questions are included.
- [ ] Architecture questions are included.
- [ ] Roadmap requirements are preserved.
- [ ] Topic 06+ material is not prematurely taught.
- [ ] Every major concept has a practical coding or operational example.
- [ ] The learner is taught to measure rather than guess.

---

# 117. Final Completion Standard

This is not a short explanation of `ConnectionPool`.

A learner who carefully studies this module and completes the exercises should be able to:

```text
understand PostgreSQL connection lifecycle
        ↓
implement a psycopg connection pool
        ↓
control concurrency
        ↓
diagnose exhaustion and leaks
        ↓
reason about pool size across workers/replicas
        ↓
respect process and fork boundaries
        ↓
evaluate PgBouncer modes
        ↓
test session-state compatibility
        ↓
observe the system with pool metrics + pg_stat_activity
        ↓
design recovery around restart/failure
        ↓
defend connection-management decisions
```

The final engineering mindset is:

```text
Do not ask:

“How big should my pool be?”

Ask:

“What concurrency does my workload require?”

“How much database capacity do I have?”

“How many processes and replicas exist?”

“How long are connections occupied?”

“What does measurement show?”

“What happens when the pool is exhausted?”

“What happens after a database restart?”

“Which pooling architecture fits this runtime?”

“Which session-dependent features does the application require?”
```

That is the production connection-pooling mindset.
