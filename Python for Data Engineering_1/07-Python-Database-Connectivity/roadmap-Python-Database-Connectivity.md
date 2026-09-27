# Roadmap — Module 2.7: Python Database Connectivity

This is the learning roadmap for the seventh module of Stage 2, **Python for
Data Engineering**. It tells you **what** to learn about connecting Python
to databases, **in what order**, **how** to learn each topic, and **how to
prove to yourself** that you have learned it before you move on.

In Module 2.6 you wrote production-grade SQL from `.sql` files. Real
pipelines, though, run SQL **from Python**: extracting tables into Parquet,
loading files into staging tables, running merges, recording pipeline runs,
and applying schema migrations. The boundary between Python and the
database is where many production incidents start — SQL injection,
connections left open until the database refuses new ones, transactions
left "idle in transaction" for hours, row-by-row inserts that take all
night, and extraction jobs that load 50 million rows into memory and
crash. This module teaches you to cross that boundary safely and fast.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain the Python **DB-API (PEP 249)**: connections, cursors, fetching,
  parameter styles, and the standard exception hierarchy.
- Connect to PostgreSQL with **psycopg 3**, configure connections securely,
  and map Python types to PostgreSQL types correctly.
- Write **parameterized queries** for values and safely compose dynamic
  identifiers — and explain exactly how SQL injection works.
- Control **transactions** from Python: commit, rollback, savepoints,
  autocommit, isolation levels, and retries on serialization failures and
  deadlocks.
- Use **connection pooling** (psycopg_pool, SQLAlchemy pools, PgBouncer)
  and size pools correctly.
- Use **SQLAlchemy Core** for database-agnostic, composable SQL, table
  metadata, and reflection.
- Decide when the **SQLAlchemy ORM** helps (application-style metadata
  tables) and when it hurts (bulk data movement).
- Manage schema changes with **Alembic** migrations, including safe
  migrations on large tables.
- Load data fast with `executemany`, multi-row inserts, and **`COPY`**, and
  measure the difference.
- Extract large tables with **server-side cursors** and streaming — with
  bounded memory — into Parquet.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.6. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Environment variables, secrets hygiene, local networking | Stage 0 — OS Fundamentals and Developer Environment | Connection settings and passwords never live in code |
| Exceptions and useful errors | Stage 1 — Module 1.3 | Mapping database errors to pipeline behaviour |
| Environment configuration, input validation | Stage 1 — Module 1.5 | Connection configuration per environment |
| Mocking and test doubles | Stage 1 — Module 1.7 | Testing code that talks to databases |
| Protocols, dependency boundaries, layered design | Stage 1 — Module 1.8 | Keeping database access behind a clean interface |
| Context managers, decorators (retry), iterators and generators | Stage 1 — Module 1.9 | Connections, transactions, retries, and streaming results |
| Configuration, safe logging, idempotency | Stage 1 — Module 1.10 | Never logging credentials; re-runnable loads |
| pandas `read_sql` / `to_sql` basics | Stage 2 — Module 2.3 | This module explains what happens underneath |
| Arrow and ADBC awareness | Stage 2 — Module 2.4 | Arrow-native database transfer in Topics 09–10 |
| Parquet writing with `ParquetWriter` | Stage 2 — Module 2.5 | Streaming extracts into Parquet |
| SQL, transactions, isolation, locking, `MERGE`, SCD | Stage 2 — Module 2.6 | **SQL itself is not re-taught**; this module is about running it from Python |

**Tools needed:**

- Python 3.12+ in a `uv` project: `uv add "psycopg[binary,pool]" sqlalchemy
  alembic pandas pyarrow polars adbc-driver-postgresql`.
- PostgreSQL 16+ in Docker (reuse your Module 2.6 `docker-compose.yml`),
  plus a second database (or schema) acting as the "warehouse" target.
- Optionally **PgBouncer** in Docker for Topic 05.
- `sqlite3` from the standard library for Topic 01 comparisons.
- `pytest`; tests run against the real PostgreSQL container (containerised
  test automation is covered in Module 2.19).

---

## 3. How the module is organised

The ten topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — The Driver Layer                     (Basics)
  01 DB-API (PEP 249): connections and cursors
  02 PostgreSQL from Python with psycopg

Phase B — Correct and Safe Queries             (Basics → Intermediate)
  03 Parameterized queries and SQL injection
  04 Transaction control from Python

Phase C — Connections in Production            (Intermediate)
  05 Connection pooling

Phase D — Abstraction Layers                   (Intermediate → Advanced)
  06 SQLAlchemy Core: engine and metadata
  07 SQLAlchemy ORM: when to use and avoid
  08 Schema migrations with Alembic

Phase E — Moving Large Data                    (Advanced)
  09 Bulk loading with COPY and executemany
  10 Server-side cursors and streaming large results

Consolidate
  practice-questions.md
  Module mini-project: PostgreSQL → lake → warehouse sync tool
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07 ──► 08 ──► 09 ──► 10
standard real   safe    atomic  shared  portable objects schema  fast    bounded
interface driver values changes conns   SQL      (or not) changes writes  memory
                                                                          reads
```

Why this order:

- The DB-API (01) is the contract every Python driver follows; psycopg
  (02) is one concrete implementation.
- Safety (03) and transactions (04) must be right before you share
  connections across threads and jobs (05).
- SQLAlchemy (06–07) sits on top of drivers, pools, and transactions — it
  only makes sense once you know what it wraps.
- Alembic (08) is built on SQLAlchemy metadata.
- Bulk loading (09) and streaming extraction (10) are the data engineer's
  main daily work with databases, and use everything above.

---

## 4. Suggested schedule

About **4 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — DB-API · Topic 02 — psycopg · Topic 03 — parameterized queries |
| 2 | Topic 04 — transactions · Topic 05 — pooling · Topic 06 — SQLAlchemy Core |
| 3 | Topic 07 — ORM · Topic 08 — Alembic · Topic 09 — bulk loading |
| 4 | Topic 10 — streaming extraction · practice questions · mini-project |

---

## 5. How to study every topic (the database-boundary loop)

```text
Read → Predict what the database sees → Write the code → Watch the server
→ Test success and failure → Measure → Harden → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Predict** exactly what SQL, parameters, and transactions the database
   will receive from your Python code.
3. **Write the code** in a small function with a clear interface.
4. **Watch the server** — not just your Python output. Turn on statement
   logging (`log_statement = 'all'` in your local PostgreSQL) and query
   `pg_stat_activity` to see connections, their state (`active`, `idle`,
   `idle in transaction`), and running queries.
5. **Test success and failure**: kill the database mid-query, violate a
   constraint, time out, run two copies at once.
6. **Measure** time, rows per second, memory, and number of connections.
7. **Harden**: timeouts, retries, closing resources, logging without
   secrets.
8. **Write down** the rule you learned in `module-2.7-notes.md`.
9. **Explain aloud** what happened on both sides of the connection.

Keep a single `db_lab/` `uv` project:

```text
db_lab/
├── docker-compose.yml   # source PostgreSQL, warehouse PostgreSQL, PgBouncer
├── .env.example         # connection settings template (no real secrets)
├── src/db_lab/          # one module per topic
├── migrations/          # Alembic (from Topic 08)
└── tests/
```

---

## 6. Phase A — The Driver Layer (Basics)

### Topic 01 — [DB-API (PEP 249): connections and cursors](01-db-api-pep-249-connections-and-cursors.md)

**Why it comes first:** Almost every Python database driver — sqlite3,
psycopg, DuckDB, Snowflake, MySQL, Oracle — follows PEP 249. Learn the
contract once, and every driver feels familiar.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The layers: your code → driver (DB-API) → network protocol → database server |
| Basics | `connect()`, `Connection` (`cursor`, `commit`, `rollback`, `close`), `Cursor` (`execute`, `executemany`, `fetchone`, `fetchmany`, `fetchall`, `close`) |
| Basics | Cursor attributes: `description` (column names and types), `rowcount`, `arraysize` |
| Basics | Using `sqlite3` (standard library) as a zero-setup DB-API example |
| Intermediate | **Parameter styles** (`paramstyle`): `qmark` (`?`), `numeric` (`:1`), `named` (`:name`), `format` (`%s`), `pyformat` (`%(name)s`) — each driver picks one or more |
| Intermediate | The standard **exception hierarchy**: `Error` → `InterfaceError`, `DatabaseError` → `DataError`, `OperationalError`, `IntegrityError`, `InternalError`, `ProgrammingError`, `NotSupportedError` — and which ones are worth retrying |
| Intermediate | Implicit transactions: DB-API connections start a transaction on the first statement and need `commit()` (details in Topic 04) |
| Intermediate | Context managers differ by driver: e.g. `with sqlite3.connect(...)` commits or rolls back but does **not** close the connection; always check your driver's documentation |
| Advanced | `threadsafety` levels and why connections should not be shared between threads without care |
| Advanced | Writing driver-agnostic helper functions (fetch as dicts, iterate in batches with `fetchmany`) |
| Advanced | Limits of the DB-API: no standard for connection strings, pooling, bulk loading, or async — why higher layers (SQLAlchemy, ADBC) exist |

**How to learn it**

1. Read the topic file.
2. Read PEP 249 itself — it is short — and make a one-page cheat sheet.
3. Run the same five operations in `sqlite3` and DuckDB's Python API and
   list the differences in parameter style and behaviour.

**Hands-on exercise — `dbapi_basics.py`**

1. With `sqlite3`, create a table, insert rows with parameters, and fetch
   them with `fetchone`, `fetchmany(100)`, and `fetchall`.
2. Print `cursor.description` and build dict rows from it.
3. Trigger an `IntegrityError` (duplicate key) and a `ProgrammingError`
   (bad SQL); catch each by its DB-API class.
4. Show that without `commit()`, a second connection does not see your
   inserts.
5. Write `iter_rows(cursor, batch_size)` — a generator using `fetchmany` —
   and test it with an empty table, one row, and many rows.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain the roles of a connection and a cursor.
- [ ] Name the five DB-API parameter styles.
- [ ] Map three common failures to their DB-API exception classes.
- [ ] Explain why `fetchall()` on a large table is dangerous.

**Common mistakes:** forgetting `commit()`; assuming every driver's
context manager closes the connection; catching bare `Exception` and
swallowing database errors.

---

### Topic 02 — [PostgreSQL from Python with psycopg](02-postgresql-from-python-with-psycopg.md)

**Why here:** PostgreSQL is the most common OLTP source and a common
metadata store in data platforms. **psycopg 3** is its modern Python
driver; you will still meet `psycopg2` in older code.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Installing `psycopg[binary]`; `psycopg.connect()` with a connection string (`postgresql://user@host:5432/db`) or keyword arguments |
| Basics | Configuration from environment variables (`PGHOST`, `PGUSER`, `PGDATABASE`, …), `.pgpass`, and your own settings loader — never hard-coded passwords |
| Basics | `conn.execute(...)` shortcut, `with conn.cursor() as cur:`, and `with psycopg.connect(...) as conn:` (commits on success, rolls back on error, and closes) |
| Intermediate | **Row factories**: `dict_row`, `namedtuple_row`, `class_row(MyDataclass)` |
| Intermediate | **Type adaptation**: `int` ↔ `integer/bigint`, `Decimal` ↔ `numeric`, timezone-aware `datetime` ↔ `timestamptz`, `date`, `UUID`, lists ↔ arrays, `Jsonb(...)` ↔ `jsonb`, `None` ↔ `NULL` |
| Intermediate | Timezones: the session `TimeZone` setting and why your code should always send and expect timezone-aware UTC datetimes |
| Intermediate | Connection options: `connect_timeout`, `application_name` (visible in `pg_stat_activity`), `sslmode`, and server settings such as `statement_timeout` via `options` |
| Intermediate | Specific error classes in `psycopg.errors` (e.g. `UniqueViolation`, `SerializationFailure`, `DeadlockDetected`, `QueryCanceled`) and SQLSTATE codes |
| Advanced | Server-side parameter binding (psycopg 3's default) vs client-side binding (`ClientCursor`); automatic prepared statements and when they cause trouble (e.g. behind some connection poolers) |
| Advanced | Pipeline mode for reducing network round trips |
| Advanced | Binary vs text transfer, and custom type adapters (e.g. for an enum or a domain type) |
| Advanced | `LISTEN` / `NOTIFY` and async connections (`AsyncConnection`) — awareness level; async patterns are taught in Module 2.10 |
| Advanced | Differences from `psycopg2` you will meet in legacy code (context-manager behaviour, `extras.execute_values`, `copy_expert`) |

**How to learn it**

1. Read the topic file.
2. Round-trip every Python type listed above through a PostgreSQL table
   and assert the values come back identical.
3. Watch your connection in `pg_stat_activity` while your script runs,
   using a distinctive `application_name`.

**Hands-on exercise — `pg_client.py`**

1. Write `get_connection(settings)` that reads settings from environment
   variables, sets `application_name`, `connect_timeout`, and a
   `statement_timeout`, and never logs the password.
2. Query orders with `dict_row` and with `class_row(Order)` using a
   dataclass.
3. Insert rows containing `Decimal`, UTC `datetime`, `UUID`, a list, and a
   `Jsonb` value; read them back and compare.
4. Trigger a statement timeout and catch `QueryCanceled`; trigger a
   duplicate key and catch `UniqueViolation`.
5. Test all of the above against the Docker PostgreSQL.

**Checkpoint:**

- [ ] Connect securely using environment-based configuration.
- [ ] Use row factories to return dicts or dataclasses.
- [ ] Explain how Python datetimes map to `timestamptz`.
- [ ] Set a statement timeout and handle the error it raises.
- [ ] Explain server-side vs client-side parameter binding.

**Common mistakes:** naive datetimes; credentials in code or logs; no
timeouts (a stuck query blocks a pipeline forever); relying on
`psycopg2`-era behaviour with psycopg 3.

---

## 7. Phase B — Correct and Safe Queries (Basics → Intermediate)

### Topic 03 — [Parameterized queries and SQL injection](03-parameterized-queries-and-sql-injection.md)

**Why here:** Before you write a single production query from Python, you
must know how to pass values safely. SQL injection is still one of the most
common and damaging security flaws.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What SQL injection is: user- or data-controlled text becoming part of the SQL command |
| Basics | The rule: **never** build SQL with f-strings, `%` formatting, `+`, or `.format()` for values |
| Basics | Placeholders: `%s` and `%(name)s` in psycopg; `?` in sqlite3 and DuckDB; `:name` in SQLAlchemy `text()` |
| Intermediate | Why placeholders are safe: values are sent separately from the SQL text (or escaped by the driver) |
| Intermediate | Things that **cannot** be parameters: table names, column names, `ORDER BY` direction, SQL keywords |
| Intermediate | Composing dynamic SQL safely with `psycopg.sql`: `sql.SQL`, `sql.Identifier`, `sql.Literal`, `sql.Placeholder`, and `.join()` |
| Intermediate | **Allowlists** for dynamic choices (sort columns, table names from configuration) |
| Intermediate | Lists of values: `WHERE id = ANY(%s)` with a Python list, instead of building `IN (...)` strings |
| Advanced | `LIKE` patterns: escaping `%` and `_` in user-supplied search text |
| Advanced | Second-order injection: malicious values stored in the database and later used in dynamic SQL (e.g. a table name read from a config table) |
| Advanced | Defence in depth: least-privilege database roles for pipelines, read-only users for extraction, no superuser connections from application code |
| Advanced | Injection beyond SQL for data engineers: shell commands, file paths, and templated SQL in orchestration and dbt-style tools |

**How to learn it**

1. Read the topic file.
2. Build a deliberately vulnerable search function in a throwaway local
   database and exploit it yourself (e.g. `' OR '1'='1`, a `UNION`-based
   data leak, and a destructive statement). Never do this against any
   system you do not own.
3. Fix it and prove the exploit no longer works.

**Hands-on exercise — `safe_queries.py`**

1. Write a vulnerable `find_customers(name)` and a safe version; write
   tests that feed classic injection strings to both and show the
   difference.
2. Write `export_table(table_name, columns, order_by, direction)` that
   builds a query with `psycopg.sql` from an allowlist loaded from
   configuration, and rejects anything else.
3. Fetch orders for a list of 10,000 ids with `= ANY(%s)`.
4. Implement a safe "contains" search that escapes `%` and `_`.
5. Create a read-only PostgreSQL role for extraction and show that an
   `UPDATE` through it fails.

**Checkpoint:**

- [ ] Explain SQL injection with an example.
- [ ] Pass values with placeholders in psycopg, sqlite3, and SQLAlchemy.
- [ ] Compose dynamic identifiers safely with `psycopg.sql` and an
      allowlist.
- [ ] Explain why a least-privilege role limits damage.

**Common mistakes:** "it's only internal data, so f-strings are fine";
quoting values by hand; passing identifiers as parameters (which fails) and
then falling back to string formatting.

---

### Topic 04 — [Transaction control from Python](04-transaction-control-from-python.md)

**Why here:** Module 2.6 taught transactions in SQL. From Python, the risk
is different: transactions opened implicitly by the driver and left open
while Python does other work, or errors that leave a connection unusable.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | psycopg's default: a transaction begins with the first statement and lasts until `commit()` or `rollback()` |
| Basics | `with conn.transaction():` blocks — commit on success, rollback on exception |
| Basics | Autocommit mode (`autocommit=True`) and when you need it (e.g. `CREATE DATABASE`, `VACUUM`, some maintenance commands) |
| Intermediate | Nested `conn.transaction()` blocks as **savepoints**: handling one bad batch without losing the whole run |
| Intermediate | The failed-transaction state: after an error, every statement fails until you roll back |
| Intermediate | Setting isolation level and read-only mode from Python |
| Intermediate | **"Idle in transaction"**: what it is, how to see it in `pg_stat_activity`, why it blocks vacuum and DDL, and `idle_in_transaction_session_timeout` |
| Intermediate | Keeping transactions short: never call an API, read a file, or sleep inside an open database transaction |
| Advanced | **Retries**: which errors are safe to retry (serialization failure, deadlock, some connection errors) and which are not (constraint violations, syntax errors); retrying the **whole** transaction, with backoff (reuse your Stage 1 retry decorator) |
| Advanced | Connection loss during `COMMIT`: you may not know whether it committed — designing loads to be idempotent so a retry is always safe |
| Advanced | Recording pipeline runs: a `pipeline_runs` table updated in its own short transaction so a failed load still leaves an audit record |
| Advanced | Transactions across two databases (e.g. source and warehouse): why there is no simple atomic commit, two-phase commit (awareness), and the practical alternative of idempotent, checkpointed steps |

**How to learn it**

1. Read the topic file.
2. Run a script that opens a transaction and then sleeps; watch its
   `idle in transaction` state in `pg_stat_activity` and try an
   `ALTER TABLE` from another session.
3. Draw a timeline of a retry after a serialization failure.

**Hands-on exercise — `transactions.py`**

1. Load 100 batches of rows inside one transaction, each batch inside a
   savepoint; make batch 37 violate a constraint; roll back only that
   batch, record it in a `rejected_batches` table, and commit the rest.
2. Show the failed-transaction state after an error without a savepoint,
   and recover from it.
3. Reproduce a serialization failure with two concurrent Python processes
   at `SERIALIZABLE`, and fix it with a retry wrapper that re-runs the
   whole transaction; test that non-retryable errors are not retried.
4. Write a `pipeline_run` context manager that inserts a `running` row,
   and updates it to `succeeded` or `failed` in separate short
   transactions.
5. Set `idle_in_transaction_session_timeout` for your pipeline role and
   show it closing a stuck session.

**Checkpoint:**

- [ ] Use `conn.transaction()` and savepoints from Python.
- [ ] Explain and detect "idle in transaction".
- [ ] Decide which database errors to retry and retry correctly.
- [ ] Explain why idempotent loads matter when a commit's outcome is
      unknown.

**Common mistakes:** long transactions around slow Python code; retrying
only the failed statement instead of the whole transaction; retrying
integrity errors; forgetting that the driver opened a transaction for a
simple `SELECT`.

---

## 8. Phase C — Connections in Production (Intermediate)

### Topic 05 — [Connection pooling](05-connection-pooling.md)

**Why here:** Opening a PostgreSQL connection is expensive (a new server
process, authentication, TLS). Services and parallel pipelines must reuse
connections — and must not exhaust the server's connection limit.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why pooling: connection setup cost, `max_connections`, and memory per server connection |
| Basics | A pool: a set of open connections that code borrows and returns |
| Basics | `psycopg_pool.ConnectionPool`: `min_size`, `max_size`, `timeout`, and `with pool.connection() as conn:` |
| Intermediate | Pool health: `max_idle`, `max_lifetime`, connection checks, and reconnecting after the database restarts |
| Intermediate | **Pool sizing**: small pools are usually faster than big ones; the total across all processes must fit under the server limit |
| Intermediate | Pool exhaustion: waiting, timeouts, and **connection leaks** (connections never returned) |
| Intermediate | Pools and concurrency: one pool per process; threads sharing a pool; connections after `fork()` in multiprocessing must not be reused |
| Advanced | **PgBouncer**: session vs transaction vs statement pooling; what breaks in transaction pooling (session state, some prepared-statement setups, `LISTEN`, advisory locks held across transactions) |
| Advanced | When not to pool in the application: short-lived batch jobs, serverless functions (pool outside, e.g. PgBouncer or a managed proxy) |
| Advanced | Monitoring: pool statistics, `pg_stat_activity` counts per `application_name`, and alerting before connections run out |
| Advanced | Async pools (`AsyncConnectionPool`) — awareness; used with asyncio in Module 2.10 |

**How to learn it**

1. Read the topic file.
2. Measure the time to open and close a connection 1,000 times vs borrowing
   from a pool 1,000 times.
3. Set `max_connections` low on your local PostgreSQL and exhaust it with
   parallel workers, then fix it with a pool and with PgBouncer.

**Hands-on exercise — `pooling.py`**

1. Benchmark connection-per-query vs a `ConnectionPool` for 5,000 small
   queries.
2. Run 32 threads against a pool of size 5 and log wait times; find the
   pool size that gives the best throughput.
3. Create a connection leak on purpose (a code path that never returns a
   connection) and show the pool timing out; fix it with a context
   manager.
4. Restart PostgreSQL mid-run and show the pool recovering.
5. Put PgBouncer in transaction mode between your workers and PostgreSQL;
   list what still works and what breaks (e.g. session-level `SET`).

**Checkpoint:**

- [ ] Explain why pools improve performance and protect the server.
- [ ] Size a pool given workers, processes, and `max_connections`.
- [ ] Detect and fix a connection leak.
- [ ] Explain PgBouncer's pooling modes and their trade-offs.

**Common mistakes:** a new pool per request; huge pools "for speed";
sharing connections across forked processes; using session features behind
a transaction-mode pooler.

---

## 9. Phase D — Abstraction Layers (Intermediate → Advanced)

### Topic 06 — [SQLAlchemy Core: engine and metadata](06-sqlalchemy-core-engine-and-metadata.md)

**Why here:** SQLAlchemy is the standard database toolkit in Python. Core
is its SQL layer — used by pandas `read_sql` / `to_sql`, Alembic, Airflow,
and countless pipelines. Data engineers use Core far more than the ORM.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The **Engine**: `create_engine("postgresql+psycopg://...")`, dialects and drivers in the URL, `echo=True` to log SQL |
| Basics | `with engine.connect() as conn:` (you commit) vs `with engine.begin() as conn:` (commit on success, rollback on error) |
| Basics | Raw SQL with `text()` and bound parameters (`:name`); results with `.all()`, `.one()`, `.scalar()`, `.mappings()` |
| Intermediate | **MetaData** and `Table` / `Column` definitions; creating tables with `metadata.create_all()` for tests |
| Intermediate | **Reflection**: loading existing table definitions with `Table(..., autoload_with=engine)` and `inspect(engine)` |
| Intermediate | The SQL expression language: `select()`, `where()`, `join()`, `group_by()`, `func.*`, `insert()`, `update()`, `delete()` — composable, parameterised queries |
| Intermediate | Executing many rows: `conn.execute(insert(table), list_of_dicts)` and SQLAlchemy 2.0's "insertmanyvalues" batching |
| Intermediate | Engine pooling options: `pool_size`, `max_overflow`, `pool_pre_ping`, `pool_recycle`, `NullPool` |
| Advanced | Dialect-specific constructs: PostgreSQL `insert(...).on_conflict_do_update(...)` for upserts |
| Advanced | Building dynamic queries safely from configuration (column lists, filters) with the expression language instead of strings |
| Advanced | Seeing generated SQL: `str(stmt)` and compiling for a dialect (and why `literal_binds` is for debugging only) |
| Advanced | Integration: pandas `read_sql` / `to_sql` with an engine; Polars `read_database` / `write_database` |
| Advanced | Portability limits: what is truly database-agnostic and what is not (types, upserts, `COPY`) |

**How to learn it**

1. Read the topic file.
2. Rewrite five of your Module 2.6 queries in the SQLAlchemy expression
   language and print the generated SQL for PostgreSQL and SQLite.
3. Reflect an existing database schema and print its tables, columns,
   types, and keys.

**Hands-on exercise — `core_repository.py`**

1. Define `orders`, `customers`, and `pipeline_runs` as `Table` objects in
   one shared `MetaData`.
2. Build a `select` that joins, filters by a dynamic set of optional
   filters (country list, date range, min amount), groups, and orders —
   with no string formatting.
3. Upsert a batch of 10,000 customer rows with `on_conflict_do_update`.
4. Reflect a table you did not define and copy it to another database
   with the same structure.
5. Test the repository functions against PostgreSQL, and one of them
   against SQLite to see portability limits.

**Checkpoint:**

- [ ] Explain the Engine, Connection, and dialect.
- [ ] Explain `connect()` vs `begin()`.
- [ ] Build parameterised dynamic queries with the expression language.
- [ ] Reflect an existing schema.
- [ ] Write a PostgreSQL upsert with SQLAlchemy Core.

**Common mistakes:** creating an engine per query (it owns a pool — create
it once); `text()` with f-strings; assuming generated SQL is portable
everywhere.

---

### Topic 07 — [SQLAlchemy ORM: when to use and avoid](07-sqlalchemy-orm-when-to-use-and-avoid.md)

**Why here:** You will meet the ORM in application codebases and internal
tools. A data engineer must know how it works, where it shines, and why it
is usually the wrong tool for moving large amounts of data.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What an ORM does: maps rows to Python objects and tracks changes |
| Basics | SQLAlchemy 2.0 style: `DeclarativeBase`, `Mapped[...]`, `mapped_column()` |
| Basics | `Session`, `sessionmaker`, adding, querying (`session.execute(select(Model))`, `session.scalars(...)`), and committing |
| Intermediate | Unit of work and identity map: changes are flushed as SQL at flush/commit time |
| Intermediate | Relationships (`relationship()`), foreign keys, and loading related objects |
| Intermediate | The **N+1 query problem** from lazy loading, and eager loading with `selectinload` and `joinedload` |
| Intermediate | Session lifecycle: one session per unit of work, `expire_on_commit`, detached objects |
| Advanced | **Where the ORM fits in data engineering**: pipeline metadata (runs, watermarks, job configs, data-quality results), internal admin tools, and APIs over small operational tables |
| Advanced | **Where to avoid it**: bulk loads, large extracts, set-based transformations — per-object overhead makes it orders of magnitude slower than Core, `COPY`, or SQL |
| Advanced | ORM bulk operations (`session.execute(insert(Model), list_of_dicts)`) and their limits |
| Advanced | Mixing ORM and Core in one codebase with the same `MetaData` |
| Advanced | Validation layers: ORM models vs Pydantic models (Module 2.11) and why they should not be the same class for external data |

**How to learn it**

1. Read the topic file.
2. Log all SQL (`echo=True`) while using the ORM, and count the queries
   sent for a simple loop over parents and children.
3. Load 1 million rows via ORM objects, ORM bulk insert, Core, and (after
   Topic 09) `COPY`; record the timings.

**Hands-on exercise — `pipeline_metadata_orm.py`**

1. Model pipeline metadata with the ORM: `Pipeline`, `PipelineRun`
   (status, start, end, rows in/out, error message), and `Watermark`
   (table name, last value).
2. Write functions `start_run`, `finish_run`, `get_watermark`,
   `set_watermark` — the kind of small, transactional operations the ORM is
   good at.
3. Produce the N+1 problem when listing pipelines with their last 5 runs;
   fix it with `selectinload` and count queries before and after.
4. Benchmark inserting 1 million order rows via ORM objects vs Core and
   write a short "ORM usage policy" for your team.

**Checkpoint:**

- [ ] Define ORM models in SQLAlchemy 2.0 style.
- [ ] Explain the unit of work and identity map.
- [ ] Detect and fix an N+1 query problem.
- [ ] Explain when to use the ORM and when not to, with numbers.

**Common mistakes:** loading millions of rows as ORM objects; long-lived
global sessions; lazy loading inside loops; using ORM models as the
schema for external data.

---

### Topic 08 — [Schema migrations with Alembic](08-schema-migrations-with-alembic.md)

**Why here:** Tables change over time. Alembic records every change as a
versioned migration script, so every environment (local, CI, staging,
production) has exactly the same schema.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why migrations: schema changes as code, reviewed, versioned, and repeatable |
| Basics | `alembic init`, `alembic.ini`, `env.py`, and connecting it to your settings (not a hard-coded URL) |
| Basics | `alembic revision -m "..."`, `upgrade head`, `downgrade -1`, `current`, `history` |
| Intermediate | **Autogenerate** from SQLAlchemy `MetaData` (`--autogenerate`) and its limits: renames look like drop + add; some type, constraint, and server-default changes are missed — always review the generated script |
| Intermediate | Operations: `op.create_table`, `op.add_column`, `op.create_index`, `op.alter_column`, `op.execute` for raw SQL |
| Intermediate | **Data migrations** (backfilling a new column) vs schema migrations, and keeping them separate |
| Intermediate | Running migrations in CI and before deployments; the `alembic_version` table |
| Advanced | **Safe migrations on large tables** (building on Module 2.6): `lock_timeout` inside migrations, `CREATE INDEX CONCURRENTLY` (outside a transaction), adding nullable columns first, backfilling in batches |
| Advanced | **Expand and contract** (zero-downtime changes): add new → dual-write/backfill → switch readers → remove old |
| Advanced | Offline mode (`alembic upgrade head --sql`) to produce SQL for review by a DBA |
| Advanced | Branches and merges when two developers create migrations in parallel; `alembic stamp` for existing databases |
| Advanced | Where Alembic fits: OLTP and metadata databases. In warehouses and lakehouses, schemas are usually managed by transformation tools (dbt, Module 2.12) and table-format schema evolution (Module 2.15) |

**How to learn it**

1. Read the topic file.
2. Start an empty database and evolve it through ten migrations, then
   downgrade all the way and upgrade again.
3. Deliberately autogenerate a column rename and see why it would lose
   data; fix the migration by hand.

**Hands-on exercise — `migrations/`**

1. Put your Topic 06–07 tables under Alembic control with an initial
   migration.
2. Add a `currency` column to a 10-million-row `orders` table using
   expand-and-contract: nullable column → batched backfill (in a separate
   data migration) → `NOT NULL` constraint.
3. Add an index with `CREATE INDEX CONCURRENTLY` from a migration.
4. Set `lock_timeout` in `env.py` and show a migration failing fast
   instead of blocking production queries.
5. Generate the offline SQL for review and add a CI step (a script) that
   runs `upgrade head` then `downgrade base` on a fresh database.

**Checkpoint:**

- [ ] Create, apply, and roll back migrations.
- [ ] Explain the limits of autogenerate.
- [ ] Apply a safe migration to a large table.
- [ ] Explain expand-and-contract.

**Common mistakes:** trusting autogenerate blindly; editing migrations
that already ran in production; mixing large data backfills into schema
migrations; migrations without lock timeouts.

---

## 10. Phase E — Moving Large Data (Advanced)

### Topic 09 — [Bulk loading with COPY and executemany](09-bulk-loading-with-copy-and-executemany.md)

**Why here:** Loading data is a data engineer's core job. The difference
between the slowest and fastest loading method is often **100× or more**.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why row-by-row inserts are slow: one network round trip and one transaction per row in autocommit mode |
| Basics | The loading ladder: single inserts → one transaction → `executemany` → multi-row `INSERT ... VALUES` → `COPY` → binary `COPY` |
| Basics | `cursor.executemany(sql, rows)` (psycopg 3 batches it efficiently using pipeline mode) |
| Intermediate | **`COPY ... FROM STDIN`** with psycopg 3: `with cur.copy("COPY t (cols) FROM STDIN") as copy:` and `copy.write_row(row)`; text, CSV, and binary formats |
| Intermediate | Loading from files and generators without holding everything in memory |
| Intermediate | The **staging pattern** (from Module 2.6): `COPY` into a staging table (optionally `UNLOGGED`), validate, then `MERGE` / upsert into the target in one transaction |
| Intermediate | Batch sizes and commit frequency: trade-offs between speed, memory, lock duration, and restartability |
| Intermediate | Loading from pandas and Polars: `to_sql(method=...)` with a custom `COPY` method; Polars `write_database` |
| Advanced | Arrow-native loading with **ADBC** (`adbc_driver_postgresql`, `adbc_ingest`) from Arrow tables and Parquet files |
| Advanced | Speeding up large loads: dropping and recreating indexes, deferring constraints, `ANALYZE` after loading, avoiding triggers |
| Advanced | Data-type and encoding issues during `COPY`: NULL markers, delimiters and quotes inside values, timestamps with time zones, `Decimal` precision |
| Advanced | Error handling: one bad row fails the whole `COPY` — pre-validating, splitting batches to find bad rows, and quarantining them |
| Advanced | Other paths: `COPY TO` / `FROM` server-side files (permissions), DuckDB's `postgres` extension for moving data between Parquet and PostgreSQL (awareness), and warehouse bulk-load commands (Module 2.17) |

**How to learn it**

1. Read the topic file.
2. Before running anything, predict the ranking and rough rows-per-second
   of every method on the loading ladder.
3. Measure them all on the same 1 million rows and compare with your
   predictions.

**Hands-on exercise — `bulk_loader.py`**

1. Implement every rung of the loading ladder for 1 million orders and
   record rows per second in a results table.
2. Build `copy_parquet_to_staging(path, table)` that streams a Parquet file
   batch by batch (Module 2.5) into PostgreSQL with `COPY`, using bounded
   memory.
3. Implement the full staging pattern: `COPY` into staging → validation
   queries → `MERGE` into target → drop staging, all idempotent.
4. Load a file containing a few bad rows; find them by splitting batches,
   write them to a quarantine table, and load the rest.
5. Load the same Parquet file with ADBC and compare speed with `COPY`.
6. Test that loading the same file twice leaves the target unchanged.

**Checkpoint:**

- [ ] Rank loading methods by speed and explain why.
- [ ] Load data with `COPY` from Python, including from Parquet.
- [ ] Implement the staging → validate → merge pattern.
- [ ] Handle bad rows without losing the whole load.

**Common mistakes:** autocommit row-by-row inserts; `to_sql` with defaults
for millions of rows; loading straight into the final table with no
validation; keeping indexes during huge initial loads.

---

### Topic 10 — [Server-side cursors and streaming large results](10-server-side-cursors-and-streaming-large-results.md)

**Why last:** Extraction is the other half of data movement. Extracting a
large table naively loads it all into memory; this topic teaches you to
stream it — the foundation of ingestion pipelines in Module 2.9.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Client-side cursors: the whole result is sent to Python on `execute`, even if you call `fetchmany` |
| Basics | **Server-side (named) cursors**: `conn.cursor(name="extract")` keeps the result on the server and sends rows in batches (`itersize`, `fetchmany`) |
| Basics | Iterating over a named cursor with bounded memory |
| Intermediate | Named cursors need a transaction; `withhold=True` for cursors that outlive a commit, and its cost |
| Intermediate | Streaming with SQLAlchemy: `execution_options(stream_results=True)` and `yield_per`; pandas `read_sql(..., chunksize=...)` (which only streams when the engine streams) |
| Intermediate | `COPY (query) TO STDOUT` from psycopg for the fastest bulk extraction |
| Intermediate | Streaming into files: writing batches to Parquet with `ParquetWriter` and to CSV, with explicit Arrow schemas |
| Advanced | Long-running reads and the database: they hold a snapshot (and can delay cleanup, per Module 2.6); running extracts on read replicas; statement timeouts for extraction roles |
| Advanced | **Resumable extraction**: keyset pagination (Module 2.6) with checkpoints so a failed extract restarts where it stopped instead of from zero |
| Advanced | Consistent snapshots across several tables (one transaction at `REPEATABLE READ`) vs per-table extraction |
| Advanced | Arrow-native extraction: ADBC `fetch_arrow_table` / record batch readers, and other Arrow-first connectors (awareness) — compared with row-based fetching |
| Advanced | Handling network failures mid-stream: detecting partial files, writing to temporary paths, and committing atomically (Stage 1 safe writes, Module 2.5 atomic outputs) |

**How to learn it**

1. Read the topic file.
2. Extract a 20-million-row table with a client-side cursor, a named
   cursor, `COPY TO STDOUT`, and ADBC; record peak memory and time for
   each.
3. Kill an extraction halfway and design how it should restart.

**Hands-on exercise — `extractor.py`**

1. Build `extract_table_to_parquet(conn, query, path, batch_size)` using a
   named cursor and `ParquetWriter`; peak memory must stay flat regardless
   of table size.
2. Add a `COPY TO STDOUT` variant (CSV) and an ADBC Arrow variant; compare
   speed and memory.
3. Make the extraction resumable using keyset pagination on
   `(updated_at, id)` with a checkpoint saved after each batch; kill and
   resume it, and prove no rows are missing or duplicated.
4. Extract three related tables from one consistent snapshot.
5. Write output to a temporary path and rename only after the extract
   completes and row counts reconcile with a `COUNT(*)` on the source
   snapshot.
6. Test with an empty table, a table with one row, and a large table.

**Checkpoint:**

- [ ] Explain client-side vs server-side cursors.
- [ ] Extract a table larger than RAM with flat memory.
- [ ] Make an extraction resumable and prove it is complete.
- [ ] Explain the effect of long-running reads on the source database.

**Common mistakes:** `fetchall()` or `read_sql` without streaming on large
tables; extracting from the primary database during peak hours; partial
output files after a crash; `OFFSET` pagination that skips or repeats rows
while data changes.

---

## 11. Consolidate — practice questions

When all ten topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Draw what happens on the **Python side** and the **database side**:
   connections, transactions, statements, and rows moved.
2. Decide the tool (driver, Core, ORM, `COPY`, ADBC) and justify it.
3. Implement it as a small function with a clear interface.
4. Test success and failure cases against the real database.
5. Measure time, memory, and connections used.
6. Check `pg_stat_activity` for leftover connections or open transactions.

---

## 12. Module mini-project — PostgreSQL → lake → warehouse sync tool

This is the proof that you have finished the module.

**Scenario:** An operational PostgreSQL database (orders, customers,
products, payments; tens of millions of rows) must be copied every night
into a lake (Parquet on MinIO or local disk) and loaded into a separate
PostgreSQL "warehouse" — without hurting the source database.

Build `pg_sync/`, a `uv` project and CLI (`argparse` from Stage 1) with:

1. **Configuration** — connection settings per environment from environment
   variables; a least-privilege, read-only extraction role with a statement
   timeout; no secrets in code or logs.
2. **Metadata** — an ORM-modelled metadata schema (`pipelines`,
   `pipeline_runs`, `watermarks`, `rejected_rows`) managed by **Alembic**
   migrations.
3. **Extraction** — server-side cursor or `COPY TO STDOUT` streaming into
   Parquet with explicit schemas; incremental extraction using a simple
   `updated_at` high-water mark (the full pattern comes in Module 2.9);
   resumable after failure; atomic output files.
4. **Loading** — `COPY` into staging tables, validation queries, then an
   idempotent `MERGE` / upsert into warehouse tables; SCD Type 2 for
   customers (from Module 2.6); bad rows quarantined.
5. **Reliability** — a connection pool for parallel table loads (sized
   against `max_connections`), short transactions, retries on
   serialization failures and deadlocks only, and a `pipeline_runs` record
   for every run.
6. **Evidence** — a benchmark table (rows per second, peak memory,
   connections used) for extraction and loading methods.
7. **Tests** — pytest tests against Docker PostgreSQL: SQL-injection
   attempts on every dynamic identifier, kill-and-resume extraction,
   re-running a load twice (no changes), constraint violations in one
   batch, and no leftover connections or open transactions after a run.

**Grading yourself:** a full sync of a table larger than your RAM runs with
flat memory; a killed run resumes and produces exactly the same warehouse
as an uninterrupted run; no query anywhere is built with string
formatting; and `pg_stat_activity` is clean after every run.

---

## 13. Module self-assessment — exit criteria

Only move to Module 2.8 when you can tick every box without looking at your
notes:

- [ ] I can explain the DB-API contract and its exception hierarchy.
- [ ] I can connect to PostgreSQL with psycopg securely and handle types
      and time zones correctly.
- [ ] I can prevent SQL injection for values and identifiers.
- [ ] I can control transactions, savepoints, and retries from Python.
- [ ] I can size and operate connection pools and explain PgBouncer modes.
- [ ] I can use SQLAlchemy Core for dynamic, parameterised queries and
      reflection.
- [ ] I can decide when the ORM is appropriate and fix N+1 problems.
- [ ] I can manage schema changes safely with Alembic.
- [ ] I can bulk load with `COPY` and the staging pattern.
- [ ] I can stream large extracts with bounded memory and resume them.
- [ ] I have finished all practice questions and the mini-project.

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| PEP 249 — Python Database API Specification v2.0 | 01 |
| psycopg 3 documentation — basic usage, adaptation, transactions, `COPY`, server-side cursors, connection pools | 02, 03, 04, 05, 09, 10 |
| SQLAlchemy 2.0 documentation — Unified Tutorial, Core, ORM, and "Working with Engines and Connections" | 06, 07 |
| Alembic documentation — tutorial, autogenerate, and operation reference | 08 |
| PostgreSQL documentation — `COPY`, connection settings, `pg_stat_activity`, and "Populating a Database" | 02, 04, 09, 10 |
| PgBouncer documentation — pooling modes and feature compatibility | 05 |
| OWASP — SQL Injection Prevention Cheat Sheet | 03 |
| Apache Arrow ADBC documentation — PostgreSQL driver | 09, 10 |

---

## 15. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Keys, grain, and warehouse table design | 2.8 Data Modelling for Analytics |
| Watermarks, incremental extraction, CDC | 2.9 Data Ingestion and Extraction Patterns |
| Async drivers and pools | 2.10 Concurrency and Parallelism in Practice |
| Validating rows before loading | 2.11 Data Validation, Contracts, and Quality |
| Checkpoints, resumability, merge-based loads | 2.12 Transformation Patterns and Pipeline Design |
| Airflow connections and hooks | 2.13 Orchestration and Workflow Management |
| JDBC reads and writes in Spark | 2.14 PySpark — data sources and save modes |
| Warehouse connectors and bulk loads | 2.17 Cloud Storage and Cloud Data Platforms |
| Cloud secrets managers for connection credentials | 2.18 Containers, Infrastructure, and CI/CD |
| Database tests with containers | 2.19 Testing Data Pipelines — Testcontainers |
| Access control and least privilege | 2.20 Observability, Lineage, Governance, and Security |

Every data pipeline eventually talks to a database. The habits you build
here — parameters always, short transactions, bounded memory, idempotent
loads, and watching what the server actually sees — are what separate a
script that works on your laptop from a pipeline you can trust in
production.
