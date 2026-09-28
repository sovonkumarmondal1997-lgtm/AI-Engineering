# DuckDB In-Process Analytics

> **Stage 2 — Python for Data Engineering**  
> **Module 2.4 — Columnar Engines: Arrow, Polars, and DuckDB**  
> **Topic 05 — DuckDB In-Process Analytics**
>
> This chapter is written as a production-oriented learning chapter. The goal is not to memorize DuckDB syntax. The goal is to understand DuckDB as an embedded analytical database engine, how it executes analytical SQL, how it interoperates with pandas/Polars/Arrow, how it manages resources, and where its architectural boundaries are.

---

# 1. Learning Objectives

After completing this chapter, you should be able to:

- explain what DuckDB is and what **in-process** means
- distinguish DuckDB from SQLite and PostgreSQL
- create in-memory and persistent DuckDB databases
- use `duckdb.sql(...)` and `duckdb.connect(...)`
- create tables, views, and CTAS relations
- query pandas, Polars, and Arrow objects directly
- understand replacement scans
- retrieve results as Python objects, pandas, Polars, Arrow, and NumPy
- write analytical SQL that uses DuckDB's analytics-friendly features
- use `GROUP BY ALL`, `SELECT * EXCLUDE`, `REPLACE`, `QUALIFY`, `ASOF JOIN`, `PIVOT`, and `UNPIVOT`
- use the DuckDB relational Python API
- use parameterized SQL safely
- read `EXPLAIN` output
- use `EXPLAIN ANALYZE` to connect plans to actual execution
- reason about columnar and vectorized execution
- reason about CPU parallelism, memory, temporary disk, and out-of-core execution
- configure `memory_limit`, `threads`, and `temp_directory`
- understand transactions and ACID properties
- understand DuckDB's process/concurrency model and why concurrent writers require care
- understand DuckDB extensions at an appropriate depth
- use DuckDB as a local analytical warehouse and warehouse-SQL test double
- identify SQL dialect portability risks
- choose a database/data-processing architecture from workload characteristics rather than slogans
- combine DuckDB, Polars, Arrow, pandas, and Parquet without unnecessary data movement
- investigate performance using plans and measurements
- validate correctness after performance changes

The central outcome is:

> You should be able to look at a Data Engineering workload and explain **where the data lives, where the computation runs, what the execution plan is doing, what resources it consumes, and why DuckDB is or is not an appropriate architectural component**.

---

# 2. Prerequisites

This topic builds on:

- Python fundamentals
- SQL fundamentals
- PostgreSQL basics
- SQLite basics
- OLTP vs OLAP
- Apache Arrow
- pandas
- Polars
- Parquet
- lazy/query-optimization concepts from the preceding Polars topics

You do not need to have memorized DuckDB. This chapter introduces DuckDB from first principles.

A useful mental map of the preceding topics is:

```text
Arrow
  ↓
in-memory columnar representation / interchange

Parquet
  ↓
on-disk columnar format

Polars
  ↓
DataFrame and expression-oriented processing engine

DuckDB
  ↓
SQL-oriented analytical database + query engine
```

These systems overlap in capability, but they are not the same abstraction.

---

# 3. Why DuckDB Exists

Consider a common Data Engineering problem:

> You have analytical files and want to run serious SQL over them, but the workload does not necessarily justify operating a database server or distributed cluster.

Examples include:

- local Parquet analysis
- ad-hoc data investigation
- ETL transformations
- data-quality checks
- feature preparation
- CI validation
- analytical unit tests
- local warehouse development
- serverless or batch-style analytical work
- SQL over DataFrames

For such workloads, a client/server database can introduce operational components that are not always necessary:

```text
Python application
      |
      | network
      v
database server
      |
      v
storage
```

DuckDB supports another model:

```text
Python process
  ├── application code
  └── DuckDB engine
          |
          +── memory
          +── local database file
          +── files/data sources
```

The key idea is **embedded analytical execution**.

DuckDB is not a universal database replacement. Its architecture is optimized around analytical workloads and embedded use.

---

# 4. What Does “In-Process” Mean?

## 4.1 The simplest mental model

A process is a running program.

With a traditional client/server database:

```text
Application process
       |
       | network / IPC
       v
Database server process
       |
       v
Storage
```

With DuckDB:

```text
Application process
       |
       +------------------+
       |                  |
       v                  v
Application code      DuckDB engine
                          |
                          v
                     storage / files
```

The analytical engine executes inside the application's process.

That means there is normally no separately managed DuckDB database server that the Python client must contact for each query.

## 4.2 Why this matters

The in-process architecture can simplify:

- local setup
- CI jobs
- tests
- data exploration
- single-node ETL
- reproducible development environments

It also changes the operational model.

The DuckDB engine shares the process's:

- CPU resources
- memory budget
- operating-system limits
- file permissions
- lifecycle

A large query is therefore also a large resource consumer of the process that launched DuckDB.

## 4.3 Trade-offs

The same simplicity introduces boundaries:

- there is no conventional central DuckDB server to coordinate many application clients
- file access and concurrency need deliberate design
- DuckDB is not intended to be a general-purpose high-concurrency OLTP backend
- resource management belongs partly to the embedding application

**Production lesson:** embedded databases reduce infrastructure overhead, but they do not remove architecture decisions.

---

# 5. DuckDB vs SQLite vs PostgreSQL

These systems are all relational and SQL-capable, but their design centers differ.

| Concern | SQLite | PostgreSQL | DuckDB |
|---|---|---|---|
| Primary emphasis | Embedded transactional/local storage | General-purpose client/server relational DB | Embedded analytical/OLAP workloads |
| Server process | No separate server | Yes | No separate server required |
| Typical deployment | Local application file | Central service | Application process or local analytics |
| Analytical SQL | Available | Strong | Core design goal |
| OLTP workload | Common fit | Core workload | Not the primary target |
| Local file workflow | Excellent | Possible but not the main model | Excellent |
| Large analytical scans | Not its main strength | Capable | Core strength |
| Shared multi-user server | No | Yes | Not the normal architecture |
| Local analytics over files/DataFrames | Limited by workflow | Usually external to core server workflow | First-class use case |

Do not turn this table into a ranking.

The engineering question is not:

> “Which database is better?”

It is:

> “What workload and deployment model do I actually have?”

### Example

A mobile app storing user settings:

```text
application → local transactional database
```

A web application serving many concurrent users:

```text
application fleet → PostgreSQL server
```

A Data Engineer analyzing a Parquet dataset locally:

```text
Python → DuckDB → Parquet
```

Those are different problems.

---

# 6. Install and Verify DuckDB

The roadmap environment uses `uv`:

```bash
uv add duckdb
```

Verify from Python:

```python
import duckdb

print(duckdb.__version__)
```

This matters because DuckDB evolves quickly.

For version-sensitive functionality:

1. inspect the installed version
2. prefer current stable documentation
3. test the exact API in your environment
4. do not assume an older example is still current

Particularly version-sensitive areas include:

- relational Python API methods
- extension availability
- result-conversion APIs
- configuration settings
- remote filesystem capabilities
- newer protocol/concurrency features

**Learning rule:** an API example in this chapter is a teaching starting point; your installed version is the final authority.

---

# 7. Your First DuckDB Query

Start with the smallest useful query:

```python
import duckdb

result = duckdb.sql(
    """
    SELECT 1 AS value
    """
)

print(result)
```

Conceptually:

```text
SQL text
   ↓
DuckDB parser
   ↓
DuckDB relation/result
```

The returned object is not just a Python list. DuckDB's Python API gives you a relation/result object that can be consumed in different representations.

For a small result:

```python
rows = duckdb.sql("SELECT 1 AS value").fetchall()
print(rows)
```

This produces Python-native rows.

For broader interoperability:

```python
df = duckdb.sql("SELECT 1 AS value").df()
pl_df = duckdb.sql("SELECT 1 AS value").pl()
arrow_table = duckdb.sql("SELECT 1 AS value").arrow()
numpy_data = duckdb.sql("SELECT 1 AS value").fetchnumpy()
```

The official Python API currently documents these conversion methods and related connection APIs:  
<https://duckdb.org/docs/current/clients/python/reference/>

---

# 8. `duckdb.sql(...)` vs `duckdb.connect(...)`

## 8.1 Convenience SQL execution

This is convenient:

```python
import duckdb

duckdb.sql("SELECT 42 AS answer").show()
```

DuckDB uses a global in-memory connection for this style by default.

That makes it excellent for:

- experiments
- quick scripts
- notebooks
- small examples
- teaching

## 8.2 Explicit connections

For more controlled lifecycle management:

```python
import duckdb

con = duckdb.connect()
try:
    con.sql("SELECT 42 AS answer").show()
finally:
    con.close()
```

You can also connect directly to a database file:

```python
con = duckdb.connect("warehouse.duckdb")
```

This gives you an explicit database handle whose lifecycle you control.

## 8.3 Why connections matter

A connection lets you reason about:

- database identity
- persistence
- lifecycle
- session settings
- transactions
- extensions
- resource configuration

**Production lesson:** use explicit connections when database lifecycle or settings matter.

---

# 9. In-Memory DuckDB

An in-memory database is useful when persistence is unnecessary.

```python
import duckdb

con = duckdb.connect(":memory:")

try:
    con.sql("""
        CREATE TABLE customers AS
        SELECT * FROM (
            VALUES
                (1, 'Asha'),
                (2, 'Ravi')
        ) AS t(customer_id, name)
    """)

    rows = con.sql("""
        SELECT *
        FROM customers
        ORDER BY customer_id
    """).fetchall()

    print(rows)
finally:
    con.close()
```

Mental model:

```text
Python process
     |
     v
DuckDB database state
     |
     └── memory
```

Advantages:

- simple
- fast to initialize
- ideal for tests
- easy to reset

Trade-off:

```text
process exits
   ↓
database state disappears
```

Use in-memory mode when persistence is not part of the requirement.

---

# 10. Persistent DuckDB Database

A persistent database is stored in a DuckDB database file.

```python
import duckdb

con = duckdb.connect("warehouse.duckdb")

con.sql("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id BIGINT,
        customer_id BIGINT,
        amount DOUBLE
    )
""")

con.sql("""
    INSERT INTO orders VALUES
        (1, 101, 120.50),
        (2, 102, 80.00)
""")

con.sql("""
    SELECT *
    FROM orders
    ORDER BY order_id
""").show()

con.close()
```

Architecture:

```text
Python
  ↓
DuckDB connection
  ↓
warehouse.duckdb
```

A persistent database is useful for:

- local analytical warehouses
- repeatable development
- data-quality testing
- prototyping transformations
- small-to-medium analytical applications

The database file is not the same concept as a Parquet file.

```text
DuckDB file
=
database storage format

Parquet
=
portable columnar data file format
```

---

# 11. Tables, Views, and CTAS

## 11.1 Tables

A table stores data as a database relation.

```sql
CREATE TABLE orders (
    order_id BIGINT,
    customer_id BIGINT,
    amount DOUBLE
);
```

## 11.2 Views

A view stores a query definition rather than a second independent copy of the underlying result.

```sql
CREATE VIEW paid_orders AS
SELECT *
FROM orders
WHERE status = 'PAID';
```

A useful mental model:

```text
Table
=
stored relation

View
=
saved relational logic
```

## 11.3 CTAS

CTAS means:

```sql
CREATE TABLE ... AS SELECT ...
```

Example:

```sql
CREATE TABLE daily_sales AS
SELECT
    order_date,
    SUM(amount) AS revenue
FROM orders
GROUP BY order_date;
```

CTAS is useful when you want to materialize a transformation for reuse.

### Materialization decision

Ask:

- Will the result be reused?
- Is recomputation expensive?
- Is persistence required?
- Is the output a stable analytical layer?

**Production lesson:** a view is a logic boundary; a table is a storage boundary.

---

# 12. Loading Data Into DuckDB

DuckDB can work with:

- tables
- files
- pandas DataFrames
- Polars DataFrames
- Arrow objects
- Python-generated data

For this chapter, focus on the in-process interoperability model.

Typical workflow:

```text
Python object
    ↓
DuckDB SQL
    ↓
analytical result
```

and:

```text
Parquet / database table
    ↓
DuckDB
    ↓
SQL transformation
    ↓
Arrow / Polars / pandas
```

Direct remote object-storage querying is intentionally not taught in depth here; that belongs to the next topic.

---

# 13. Querying Python Objects Directly

One of DuckDB's most useful embedded-analytics features is the ability to query Python objects directly.

### pandas

```python
import duckdb
import pandas as pd

orders_df = pd.DataFrame(
    {
        "order_id": [1, 2, 3],
        "customer_id": [10, 10, 20],
        "amount": [100.0, 50.0, 80.0],
    }
)

result = duckdb.sql("""
    SELECT
        customer_id,
        SUM(amount) AS revenue
    FROM orders_df
    GROUP BY customer_id
    ORDER BY customer_id
""")

result.show()
```

### Polars

```python
import duckdb
import polars as pl

orders_pl = pl.DataFrame(
    {
        "order_id": [1, 2, 3],
        "customer_id": [10, 10, 20],
        "amount": [100.0, 50.0, 80.0],
    }
)

duckdb.sql("""
    SELECT customer_id, SUM(amount) AS revenue
    FROM orders_pl
    GROUP BY customer_id
""").show()
```

DuckDB's current documentation describes direct querying of Polars through the Python scope, using its Arrow integration; `pyarrow` is required for the documented Polars integration path:  
<https://duckdb.org/docs/current/guides/python/polars>

### Arrow

The same architecture applies to Arrow objects.

Conceptually:

```text
pandas / Polars / Arrow object
            ↓
     Python process scope
            ↓
        DuckDB SQL
```

This can eliminate explicit “load this DataFrame into a temporary database table first” boilerplate.

---

# 14. Replacement Scans

## 14.1 What is a replacement scan?

Suppose you write:

```sql
SELECT *
FROM orders_df;
```

but `orders_df` is not a table in the DuckDB catalog.

DuckDB can resolve the Python object by name in the Python process and replace the missing table reference with a scan of that object.

Mental model:

```text
SQL says:
FROM orders_df

        ↓

DuckDB checks catalog
        ↓
not a catalog table
        ↓
Python replacement scan
        ↓
find Python object named orders_df
        ↓
scan object
```

The feature is called a **replacement scan**.

DuckDB's documentation describes the mechanism as a callback path that can replace an unresolved table read with a table function; its Python documentation shows pandas DataFrames being resolved by name in Python scope.  
<https://duckdb.org/docs/current/guides/python/import_pandas>  
<https://duckdb.org/docs/current/clients/c/python/replacement_scans>

## 14.2 Why it matters

Replacement scans are valuable because:

- Python remains the orchestration language
- SQL remains the analytical language
- unnecessary manual registration can be avoided
- data movement can be reduced conceptually
- local DataFrame analysis becomes very concise

## 14.3 Scope and lifetime matter

A Python object is still a Python object.

This can fail:

```python
def build_query():
    local_df = make_dataframe()

    return duckdb.sql("""
        SELECT COUNT(*)
        FROM local_df
    """)
```

The exact behavior depends on when the relation is consumed and what object remains in scope.

The production-safe lesson is:

> Do not treat a Python variable name as if it were a permanent database table.

For long-lived workflows, make object lifetime explicit and test the exact behavior you depend on.

---

# 15. Result Retrieval APIs

The required result forms are:

| Method | Typical representation | Useful when |
|---|---|---|
| `.fetchall()` | Python rows/tuples | Small result sets |
| `.df()` | pandas DataFrame | pandas-based downstream code |
| `.pl()` | Polars DataFrame | Polars-based downstream code |
| `.arrow()` | Arrow table | Arrow interchange |
| `.fetchnumpy()` | NumPy arrays/dict | Numeric NumPy workflows |

Current DuckDB Python documentation documents these conversions:  
<https://duckdb.org/docs/current/clients/python/overview>  
<https://duckdb.org/docs/current/clients/python/reference/>

The important engineering question is:

> How much data am I moving out of DuckDB?

A query can be efficient inside DuckDB but expensive if the result is then materialized into an unnecessarily large Python object.

---

# 16. `.fetchall()`

```python
rows = duckdb.sql("""
    SELECT order_id, amount
    FROM orders
    WHERE amount > 100
""").fetchall()
```

This produces Python-native rows.

Good for:

- a few configuration rows
- lookup results
- small summaries
- tests

Dangerous for:

- millions of rows
- tens of millions of rows
- large analytical result sets

Why?

```text
DuckDB result
    ↓
Python objects
    ↓
many Python allocations
    ↓
memory pressure
```

The analytical engine may have handled the query efficiently, but the final conversion can still become the bottleneck.

---

# 17. `.df()`

```python
result_df = duckdb.sql("""
    SELECT customer_id, SUM(amount) AS revenue
    FROM orders
    GROUP BY customer_id
""").df()
```

Use pandas at the edge when:

- a downstream library expects pandas
- a visualization package expects pandas
- a user explicitly needs a pandas object
- the result is reasonably sized

Avoid unnecessary conversion:

```text
Parquet
 ↓
DuckDB
 ↓
pandas
 ↓
Polars
```

if the actual next step is better kept in DuckDB or Polars.

---

# 18. `.pl()`

```python
result_pl = duckdb.sql("""
    SELECT customer_id, SUM(amount) AS revenue
    FROM orders
    GROUP BY customer_id
""").pl()
```

This is useful when SQL does the heavy relational work and Polars does the next DataFrame transformation.

A practical hybrid:

```text
Parquet
  ↓
DuckDB SQL
  ↓
small/medium analytical result
  ↓
Polars
  ↓
Python-specific transformation
```

Use the boundary intentionally.

---

# 19. `.arrow()`

```python
result_arrow = duckdb.sql("""
    SELECT *
    FROM orders
    WHERE amount > 100
""").arrow()
```

Arrow is valuable as an interoperability boundary because it represents columnar data and is used by many modern analytical systems.

Mental model:

```text
DuckDB
   ↓
Arrow
   ↓
Polars / pandas / Arrow-native tools
```

The important caveat:

> Arrow interoperability does not automatically mean every conversion path is zero-copy.

Exact memory behavior depends on data types, API path, versions, and operations performed afterward.

Zero-copy internals belong to the Arrow-focused topic rather than this chapter.

---

# 20. `.fetchnumpy()`

```python
arrays = duckdb.sql("""
    SELECT amount, quantity
    FROM order_lines
""").fetchnumpy()
```

This provides a Python mapping of columns to NumPy arrays.

Useful for:

- numerical analysis
- scientific workflows
- NumPy-specific downstream code
- model inputs when NumPy is the chosen boundary

Not automatically ideal when:

- data has rich nested structures
- strings dominate
- the next stage is SQL
- the next stage is naturally Polars/Arrow

Choose the representation based on the next computation.

---

# 21. Why DuckDB Is Fast

DuckDB's analytical performance comes from several complementary design choices.

## 21.1 Columnar execution

Analytical queries often touch only a subset of columns:

```sql
SELECT SUM(amount)
FROM orders
WHERE status = 'PAID';
```

An analytical engine can focus computation on:

- `amount`
- `status`

rather than treating every column as equally important.

## 21.2 Vectorized execution

Instead of conceptual execution like:

```text
row 1 → operator
row 2 → operator
row 3 → operator
...
```

DuckDB uses vector/batch-oriented execution:

```text
vector
  ↓
operator
  ↓
vector
  ↓
next operator
```

This reduces per-row overhead and works well with modern CPU hardware.

## 21.3 Parallel execution

DuckDB can use multiple CPU threads:

```text
CPU
├── worker
├── worker
├── worker
└── worker
```

Parallelism can help scans, joins, aggregations, and other operators where the query plan exposes useful independent work.

But parallelism is constrained by:

- dependencies
- I/O
- memory
- operator characteristics
- available cores

## 21.4 Cost-based optimization

SQL describes the result you want.

The optimizer determines how to execute it.

Conceptually:

```text
SQL
 ↓
parse
 ↓
logical representation
 ↓
optimization
 ↓
physical plan
 ↓
vectorized execution
 ↓
result
```

This is why:

> SQL text is not the same thing as execution work.

---

# 22. Columnar Execution

Consider:

```sql
SELECT
    SUM(amount)
FROM orders
WHERE status = 'PAID';
```

From an analytical perspective, the engine wants to avoid unnecessary work.

Conceptually:

```text
orders table
 ├── order_id       not needed
 ├── customer_id    not needed
 ├── status         needed for filter
 ├── amount         needed for sum
 └── description    not needed
```

This helps reduce:

- bytes touched
- memory traffic
- CPU work

When data is already stored in a columnar format such as Parquet, the storage format can complement this execution style.

---

# 23. Vectorized Execution

Think about computing:

```sql
SELECT amount * quantity AS revenue
FROM order_lines;
```

A row-at-a-time conceptual approach is:

```text
read one row
multiply
write one row
repeat
```

Vectorized execution is closer to:

```text
read a vector of amounts
read a vector of quantities
multiply vectors
produce output vector
```

This better matches:

- CPU caches
- SIMD-friendly operations
- tight loops in native code
- parallel execution

Do not interpret “vectorized” as “every operator always has identical low-level behavior.” Complex operators can have very different execution strategies.

---

# 24. Parallel Execution

The high-level relationship is:

```text
more independent work
        ↓
more CPU parallelism
        ↓
potentially shorter wall time
```

But:

```text
more threads
        ↓
more simultaneous work/state
        ↓
possibly more memory pressure
```

This is why thread count is a resource setting, not a universal “speed knob.”

A shared machine may prefer fewer threads to protect:

- other services
- operating-system stability
- CI jobs
- container memory headroom

---

# 25. Cost-Based Optimization

Consider:

```sql
SELECT
    c.customer_segment,
    SUM(o.amount) AS revenue
FROM orders o
JOIN customers c
  ON o.customer_id = c.customer_id
WHERE o.status = 'PAID'
GROUP BY c.customer_segment;
```

The logical query says:

```text
scan
 ↓
filter
 ↓
join
 ↓
group
```

The optimizer can choose a physical strategy based on:

- estimated cardinalities
- operator costs
- join strategies
- available statistics
- expression simplification
- data access properties

Do not memorize one fixed optimizer rule set.

Instead learn to ask:

> What physical plan did the engine choose, and was that plan appropriate for this workload?

That question leads directly to `EXPLAIN`.

---

# 26. DuckDB Analytics-Friendly SQL

DuckDB has SQL features that make analytical queries concise.

Required features:

- `GROUP BY ALL`
- `SELECT * EXCLUDE`
- `REPLACE`
- `QUALIFY`
- `ASOF JOIN`
- `PIVOT`
- `UNPIVOT`
- FROM-first syntax
- list functions
- struct functions

For each feature, use this pattern:

```text
problem
  ↓
syntax
  ↓
tiny example
  ↓
business use
  ↓
caveat
```

These features are documented in DuckDB's current SQL reference.

---

# 27. `GROUP BY ALL`

Without `GROUP BY ALL`:

```sql
SELECT
    customer_id,
    order_date,
    SUM(amount) AS revenue
FROM orders
GROUP BY customer_id, order_date;
```

With DuckDB:

```sql
SELECT
    customer_id,
    order_date,
    SUM(amount) AS revenue
FROM orders
GROUP BY ALL;
```

The idea is:

> group by every selected column that is not itself an aggregate.

This is convenient because the selected grouping columns and the group-by granularity stay aligned.

Current DuckDB documentation explicitly describes `GROUP BY ALL` as a way to reduce repeated column lists and avoid granularity mismatches:  
<https://duckdb.org/docs/lts/sql/query_syntax/groupby>

---

# 28. `SELECT * EXCLUDE`

Wide analytical tables are common.

Suppose:

```text
orders
├── order_id
├── customer_id
├── amount
├── status
├── internal_debug_flag
├── raw_payload
└── ingestion_metadata
```

You want everything except two columns:

```sql
SELECT *
EXCLUDE (raw_payload, ingestion_metadata)
FROM orders;
```

This is more maintainable than manually writing every remaining column.

DuckDB's current star-expression documentation supports `EXCLUDE` and `REPLACE`:  
<https://duckdb.org/docs/current/sql/expressions/star>

**Production use:** useful for evolving analytical schemas where a wide table changes over time.

---

# 29. `REPLACE`

You can replace a projected column expression:

```sql
SELECT *
REPLACE (
    lower(status) AS status
)
FROM orders;
```

Or:

```sql
SELECT *
REPLACE (
    amount * 1.18 AS amount
)
FROM orders;
```

The important idea is:

```text
keep most columns
+
override selected columns
```

This reduces repetitive projection lists.

Use it carefully when downstream schema contracts depend on exact names and types.

---

# 30. `QUALIFY`

A common analytical task is:

> Keep the latest order per customer.

Traditional SQL often uses a subquery:

```sql
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY order_ts DESC
        ) AS rn
    FROM orders
)
SELECT *
FROM ranked
WHERE rn = 1;
```

DuckDB's `QUALIFY` lets the window result be filtered directly:

```sql
SELECT
    *,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY order_ts DESC
    ) AS rn
FROM orders
QUALIFY rn = 1;
```

`QUALIFY` is specifically for filtering window-function results and can avoid a subquery/CTE for this pattern.  
<https://duckdb.org/docs/current/sql/query_syntax/qualify>

### Business use cases

- latest-version records
- top-N within each category
- deduplication
- customer rankings

### Caveat

The result depends on a deterministic ordering rule. If ties are possible, include a stable tie-breaker.

---

# 31. `ASOF JOIN`

## Business problem

You have events and time-varying reference data.

Example:

```text
Trades
ticker  trade_time        quantity
AAPL    10:05             100
AAPL    10:08              50

Prices
ticker  price_time        price
AAPL    10:00             200
AAPL    10:07             202
```

For the 10:05 trade, the relevant price is the latest price at or before that time.

DuckDB:

```sql
SELECT
    t.ticker,
    t.trade_time,
    t.quantity,
    p.price
FROM trades t
ASOF JOIN prices p
    ON t.ticker = p.ticker
   AND t.trade_time >= p.price_time;
```

The key semantics are:

```text
match keys equal
+
time/order condition satisfied
+
choose nearest prior reference row
```

DuckDB's current documentation specifies that an `ASOF` join requires an inequality on the ordering field and that the left/right order matters.  
<https://duckdb.org/docs/current/sql/query_syntax/from>

Typical Data Engineering uses:

- FX rates
- market prices
- slowly-changing time-varying reference data
- sensor state
- tariff/rate history

---

# 32. `PIVOT`

Pivot transforms long data into a wider analytical representation.

Example source:

```text
customer | month | revenue
---------+-------+--------
A        | Jan   | 100
A        | Feb   | 120
B        | Jan   |  80
```

Conceptual result:

```text
customer | Jan | Feb
---------+-----+----
A        | 100 | 120
B        |  80 | NULL
```

DuckDB's simplified syntax includes:

```sql
PIVOT sales
ON month
USING SUM(revenue)
GROUP BY customer;
```

The exact available syntax is version-sensitive, so test the installed release when building production code.

Current DuckDB documentation describes both simplified and standard `PIVOT` syntax.  
<https://duckdb.org/docs/lts/sql/statements/pivot>

### Caveats

Pivot can:

- increase the number of columns dramatically
- create wide output
- make downstream schema contracts harder
- require awareness of the distinct pivot values

Use it deliberately, often at the reporting boundary rather than deep inside a normalized transformation pipeline.

---

# 33. `UNPIVOT`

UNPIVOT reverses the shape:

```text
customer | Jan | Feb
---------+-----+----
A        | 100 | 120
```

to:

```text
customer | month | revenue
---------+-------+--------
A        | Jan   | 100
A        | Feb   | 120
```

A DuckDB simplified form is:

```sql
UNPIVOT monthly_sales
ON Jan, Feb
INTO
    NAME month
    VALUE revenue;
```

Current DuckDB documentation supports simplified and SQL-standard `UNPIVOT` forms.  
<https://duckdb.org/docs/current/sql/statements/unpivot>

Useful for:

- normalizing reporting extracts
- preparing data for aggregations
- loading wide spreadsheet-shaped data into analytical pipelines

---

# 34. FROM-First Syntax

DuckDB supports a SQL style in which the `FROM` clause can appear first.

Example:

```sql
FROM orders
SELECT
    customer_id,
    SUM(amount) AS revenue
GROUP BY ALL;
```

This style can make some analytical workflows easier to compose because the input relation is visually established first.

Use the style that makes the query easiest for your team to review. Do not force FROM-first syntax merely because DuckDB supports it.

The current DuckDB SQL documentation includes FROM-first examples and syntax:  
<https://duckdb.org/docs/current/sql/query_syntax/from>

---

# 35. List Functions

DuckDB supports `LIST` values.

A list can be created with:

```sql
SELECT [1, 2, 3] AS numbers;
```

or:

```sql
SELECT list_value(1, 2, 3) AS numbers;
```

Some useful operations include:

```sql
SELECT
    [1, 2, 3] AS xs,
    len([1, 2, 3]) AS length,
    list_contains([1, 2, 3], 2) AS has_two;
```

Transform a list:

```sql
SELECT list_transform(
    [1, 2, 3],
    x -> x * 10
) AS scaled;
```

The exact lambda/list-function syntax should be tested against the installed version.

Current DuckDB documentation describes `LIST`, `list_value`, `length`/`len`, `list_contains`, `list_transform`, and many other list functions.  
<https://duckdb.org/docs/current/sql/data_types/list>  
<https://duckdb.org/docs/lts/sql/functions/list>

### Data Engineering use cases

- arrays from semi-structured sources
- grouped values
- compact feature representations
- nested analytical attributes

Do not confuse a `LIST` with a fixed-length numerical matrix.

---

# 36. Struct Functions

A `STRUCT` contains named fields.

Create one:

```sql
SELECT struct_pack(
    customer_id := 101,
    segment := 'gold'
) AS customer;
```

You can also use struct notation:

```sql
SELECT {
    'customer_id': 101,
    'segment': 'gold'
} AS customer;
```

Extract a field:

```sql
SELECT struct_extract(customer, 'segment')
FROM some_table;
```

Current DuckDB documentation supports `struct_pack` and `struct_extract`:  
<https://duckdb.org/docs/stable/sql/data_types/struct>  
<https://duckdb.org/docs/current/sql/functions/struct>

This is useful when working with nested analytical data while still staying inside SQL.

---

# 37. DuckDB Relational Python API

SQL is not the only way to compose operations in Python.

DuckDB exposes a relational API where transformations can be chained.

Conceptual example:

```python
import duckdb

rel = duckdb.sql("""
    SELECT *
    FROM orders
""")

filtered = rel.filter("amount > 100")
projected = filtered.project("customer_id, amount")

print(projected.fetchall())
```

An aggregation can be expressed through the relational API as well:

```python
summary = (
    duckdb.sql("SELECT customer_id, amount FROM orders")
    .aggregate(
        "SUM(amount) AS revenue",
        "customer_id"
    )
)
```

Current relational API documentation lists lazy-evaluated transformation methods such as `filter`, `project`, `select`, `aggregate`, `join`, `sort`, and `limit`.  
<https://www.duckdb.org/docs/current/clients/python/relational_api>

Important version note:

> Relational API method signatures can evolve. Check the installed API before putting a signature into shared production code.

---

# 38. SQL vs Relational API

| Concern | SQL | Relational API |
|---|---|---|
| Declarative analytics | Natural | Possible |
| Human-readable query review | Strong | Depends on composition |
| Dynamic programmatic composition | Good with generated expressions/CTEs | Strong |
| Data-engineering team familiarity | Usually high | Varies |
| Python-centric pipelines | Natural | Natural |

Do not choose based on ideology.

Use SQL when:

- transformation logic is naturally relational
- analysts and Data Engineers review the query
- SQL readability matters

Use the relational API when:

- programmatic composition is valuable
- you want chained relation transformations
- Python controls the structure of the workflow

---

# 39. Parameterized Queries

Parameterized SQL is a production security requirement.

Unsafe pattern:

```python
customer_id = user_input

query = f"""
    SELECT *
    FROM orders
    WHERE customer_id = {customer_id}
"""
```

Or:

```python
query = "SELECT * FROM orders WHERE customer_id = " + user_input
```

Why is this dangerous?

Because SQL syntax and user data become mixed.

For example, if an application expects:

```text
customer_id = 42
```

but accepts raw text, an attacker may attempt to inject SQL syntax.

Use a parameter:

```python
import duckdb

customer_id = 42

rows = duckdb.execute(
    """
    SELECT *
    FROM orders
    WHERE customer_id = ?
    """,
    [customer_id]
).fetchall()
```

The SQL structure remains fixed while the value is supplied separately.

DuckDB's security documentation recommends prepared statements/parameterized queries for untrusted values and explicitly warns against string concatenation.  
<https://duckdb.org/docs/current/operations_manual/securing_duckdb/overview>

**Production lesson:** dynamic SQL structure and dynamic data values are different problems. Parameterize values.

---

# 40. `EXPLAIN`

`EXPLAIN` is the beginning of query-engine thinking.

```sql
EXPLAIN
SELECT
    customer_id,
    SUM(amount) AS revenue
FROM orders
WHERE status = 'PAID'
GROUP BY customer_id;
```

Mental model:

```text
EXPLAIN
=
"What plan will DuckDB use?"
```

You are looking for operators such as:

```text
TABLE_SCAN
   ↓
FILTER
   ↓
PROJECTION
   ↓
HASH_GROUP_BY
   ↓
ORDER
```

The exact plan text is version- and query-dependent.

Do not memorize one screenshot.

Learn the categories:

- scan
- filter
- projection
- join
- aggregate
- sort/order
- window
- materialization or other physical operators

---

# 41. `EXPLAIN ANALYZE`

`EXPLAIN ANALYZE` goes further:

```sql
EXPLAIN ANALYZE
SELECT
    customer_id,
    SUM(amount) AS revenue
FROM orders
WHERE status = 'PAID'
GROUP BY customer_id;
```

Mental model:

```text
EXPLAIN
=
planned work

EXPLAIN ANALYZE
=
planned work
+
actual execution information
```

DuckDB's current documentation states that `EXPLAIN ANALYZE` executes the query and reports runtime performance information for operators, including estimated and actual cardinalities.  
<https://duckdb.org/docs/current/guides/meta/explain_analyze>

### What to inspect

Look for:

- expensive operators
- actual row counts
- estimated cardinality vs actual cardinality
- scan volume
- operator timing
- unexpected plan shape

Important concurrency nuance:

> Operator timings can add up to more than query wall time when multiple threads execute in parallel, because those timings are cumulative across work.

Do not compare an operator's cumulative timing directly to wall-clock time without understanding parallel execution.

---

# 42. Query Plan Reading

Start with:

```text
Scan
  ↓
Filter
  ↓
Join
  ↓
Aggregate
  ↓
Sort
```

Ask:

### Scan

- How much data is read?
- Which columns are needed?
- Is the source file format appropriate?

### Filter

- Does it greatly reduce rows?
- Could it be applied earlier?

### Join

- Which side is large?
- Could the join multiply rows?
- Is the join key selective?

### Aggregate

- How many groups exist?
- Does state grow with cardinality?

### Sort

- Is global ordering really required?
- Could the business requirement be satisfied with a top-N or partitioned order?

This is query-engine reasoning.

---

# 43. Resource Settings

DuckDB exposes resource-related settings.

The required settings are:

```sql
SET memory_limit = '4GB';
SET threads = 4;
SET temp_directory = '/tmp/duckdb_tmp';
```

Current DuckDB configuration documentation describes these settings and their defaults.  
<https://duckdb.org/docs/current/configuration/overview>

You can inspect settings:

```sql
SELECT current_setting('memory_limit');
```

or:

```sql
SELECT *
FROM duckdb_settings()
WHERE name IN (
    'memory_limit',
    'threads',
    'temp_directory'
);
```

---

# 44. `memory_limit`

Example:

```sql
SET memory_limit = '4GB';
```

Why use a limit?

- shared-machine protection
- CI predictability
- container resource management
- deliberate capacity planning
- preventing a single analytical query from consuming the entire host

A memory limit is not a magic guarantee that every query will complete.

A query can still fail because:

- the workload requires more state than allowed
- temporary storage is insufficient
- execution needs resources outside the controlled memory budget
- the output itself is too large for the chosen downstream representation

**Production lesson:** resource limits are guardrails, not mathematical proofs of query feasibility.

---

# 45. `threads`

Example:

```sql
SET threads = 4;
```

Thread count affects:

- CPU parallelism
- potential throughput
- simultaneous intermediate work
- memory pressure
- contention with other processes

More threads can help:

```text
under-utilized CPU
+
parallelizable query
=
possible speedup
```

More threads can hurt:

```text
memory-constrained query
+
more concurrent work
=
higher memory pressure
```

Tune with measurements.

---

# 46. `temp_directory`

Example:

```sql
SET temp_directory = '/fast/duckdb_tmp';
```

Temporary storage matters because DuckDB may use temporary disk space during execution.

Operational requirements:

- directory must exist and be writable
- enough free space must be available
- disk throughput matters
- storage failures can become query failures

Do not assume the default temporary directory is always appropriate for production.

For a container, explicitly consider:

```text
container writable layer
vs
mounted fast volume
```

---

# 47. Out-of-Core Execution

Out-of-core execution exists for workloads where all intermediate working data cannot fit comfortably in RAM.

Conceptually:

```text
large input
   ↓
process portions
   ↓
maintain execution state
   ↓
spill temporary state if necessary
   ↓
continue
   ↓
final result
```

The crucial distinction is:

> Out-of-core execution extends the feasible working set; it does not make disk as fast as RAM.

This is why a query can be feasible but slower once it becomes spill-heavy.

---

# 48. Spilling to Disk

Spilling means moving temporary execution state from memory to disk and later reading it back.

Conceptually:

```text
RAM
 ↓
memory pressure
 ↓
temporary state written to disk
 ↓
later read back
 ↓
continue computation
```

Advantages:

- more workloads can complete
- lower peak RAM pressure
- useful for larger aggregations/sorts/joins

Costs:

- additional disk I/O
- filesystem dependency
- disk capacity requirements
- potentially much higher runtime

Never fabricate a claim such as “spilling is exactly N times slower.”

The real cost depends on:

- storage hardware
- workload
- compression
- operator
- data distribution
- thread count
- operating system
- caching

---

# 49. Memory Investigation Exercise

Create an experiment using a local database.

### Step 1

Run a moderate aggregation.

### Step 2

Set a lower memory limit:

```sql
SET memory_limit = '1GB';
```

### Step 3

Set a dedicated temporary directory:

```sql
SET temp_directory = '/path/to/duckdb_tmp';
```

### Step 4

Run a larger aggregation.

### Step 5

Observe:

- success/failure
- runtime
- temporary-directory usage
- process memory
- query plan

### Step 6

Use:

```sql
EXPLAIN ANALYZE
...
```

The objective is not to force a specific spill message.

The objective is:

```text
resource constraint
   ↓
actual observation
   ↓
evidence
   ↓
engineering conclusion
```

---

# 50. Transactions and ACID

A transaction groups changes into a unit that can commit or roll back.

Basic example:

```sql
BEGIN TRANSACTION;

INSERT INTO orders
VALUES (1001, 42, 250.0);

COMMIT;
```

Rollback example:

```sql
BEGIN TRANSACTION;

DELETE FROM orders
WHERE order_id = 1001;

ROLLBACK;
```

## ACID

### Atomicity

All changes in the transaction succeed together or are rolled back together.

### Consistency

Transactions preserve the database's defined consistency guarantees.

### Isolation

Concurrent operations do not simply observe arbitrary partial state.

### Durability

Committed changes survive according to the database's persistence guarantees.

DuckDB documents transactional behavior, rollback, and snapshot isolation:  
<https://duckdb.org/docs/current/sql/statements/transactions>

This chapter is not a complete database transaction course. The focus is understanding how transactions fit DuckDB's embedded analytical architecture.

---

# 51. DuckDB Concurrency Model

This is one of the most important architectural boundaries.

A useful simplified model is:

```text
One process
  ├── many reads
  ├── multiple worker threads
  └── controlled writes within the process
```

Across multiple processes, the design is different.

Current DuckDB documentation describes:

- read-write mode for one process
- read-only access for multiple processes
- concurrency inside a process using MVCC/optimistic concurrency control
- multiple concurrent writes within the same process when they do not conflict
- limitations for multi-process writing to the same native database file in the conventional architecture

Source:  
<https://duckdb.org/docs/current/connect/concurrency>

Because the current DuckDB ecosystem is evolving quickly, do not turn an older “single writer” sentence into an absolute description of every new DuckDB protocol or table format. For the standard embedded `.duckdb` file workflow taught here, design multi-process writes very cautiously.

---

# 52. Why DuckDB Is NOT PostgreSQL

DuckDB and PostgreSQL are both SQL databases, but their architecture and optimization goals differ.

Do not say:

> “DuckDB is bad.”

Instead say:

> DuckDB is optimized for a different class of workloads.

DuckDB is not the normal choice for:

- high-concurrency transactional web backends
- large fleets of application workers independently writing the same database
- centralized user/auth/session storage
- conventional server-side OLTP architecture
- a general-purpose multi-user database service

PostgreSQL's client/server architecture is designed around shared application access and transactional workloads.

DuckDB's embedded architecture is designed around analytical execution inside a process.

---

# 53. Why DuckDB Is NOT a Shared Multi-User Server

Imagine:

```text
Client A ──┐
Client B ──┼──> Shared central DuckDB server
Client C ──┘
```

That is not DuckDB's normal architectural model.

The usual embedded model is:

```text
Process A → DuckDB
Process B → DuckDB
Process C → DuckDB
```

Each process has its own embedding context.

For the standard native DuckDB file workflow, shared multi-process writes should not be treated like PostgreSQL server connections. Current DuckDB documentation provides specific guidance around read-only multi-process access and write limitations.  
<https://duckdb.org/docs/current/connect/concurrency>

**Production question:**

> Do I need one analytical engine embedded in each batch job, or one shared transactional server?

Those are different architectures.

---

# 54. Extensions

DuckDB supports optional extensions.

The basic lifecycle is:

```sql
INSTALL extension_name;
LOAD extension_name;
```

`INSTALL` makes an extension available locally; `LOAD` makes it available to the current session.

Current DuckDB documentation explains that some core extensions can autoload, while others require explicit installation/loading.  
<https://duckdb.org/docs/stable/extensions/overview>  
<https://duckdb.org/docs/current/sql/statements/load_and_install>

Production considerations:

- extension availability
- version compatibility
- network requirements for installation
- security/repository policy
- reproducibility in containers and CI

---

# 55. Required Extension Awareness

This chapter only teaches awareness-level knowledge.

| Extension | Problem solved | Typical use | Production caveat |
|---|---|---|---|
| `httpfs` | HTTP/S3-style filesystem access | File/object-store analytics | Credentials, network, latency |
| `json` | JSON processing | Semi-structured analytics | Schema variability |
| `delta` | Delta Lake interoperability | Read/write Delta tables | Version/table-feature compatibility |
| `iceberg` | Apache Iceberg interoperability | Lakehouse tables | Catalog/table-format compatibility |
| `spatial` | Geospatial analytics | Geometry and spatial functions | Specialized types/functions |

## `httpfs`

Current DuckDB documentation describes `httpfs` as an extension for HTTP(S) and S3 API access.  
<https://duckdb.org/docs/current/core_extensions/httpfs/overview>

Basic conceptual loading:

```sql
INSTALL httpfs;
LOAD httpfs;
```

Many core-extension workflows can autoload; explicit loading is useful when making dependencies visible.

## `json`

The JSON extension supports JSON-oriented operations. It may be built into a distribution and can be autoloadable.  
<https://duckdb.org/docs/current/data/json/installing_and_loading>

## `delta`

The Delta extension provides Delta Lake interoperability.  
<https://duckdb.org/docs/current/core_extensions/delta>

## `iceberg`

The Iceberg extension supports Apache Iceberg table access and is evolving alongside DuckDB releases.  
<https://duckdb.org/docs/stable/core_extensions/iceberg/overview>

## `spatial`

The Spatial extension supports geospatial processing and is not simply assumed to be loaded automatically in every workflow.  
<https://duckdb.org/docs/current/core_extensions/spatial/overview>

This topic does not deeply teach remote storage, Delta Lake, Iceberg, or geospatial architecture. Those belong to later topics.

---

# 56. DuckDB as a Local Development Warehouse

A useful local architecture is:

```text
raw Parquet
     ↓
DuckDB
     ↓
staging
     ↓
silver transformations
     ↓
gold metrics
```

Example:

```python
import duckdb

con = duckdb.connect("local_warehouse.duckdb")

con.sql("""
    CREATE OR REPLACE TABLE silver_orders AS
    SELECT
        order_id,
        customer_id,
        order_date,
        amount
    FROM read_parquet('bronze/orders/*.parquet')
    WHERE amount > 0
""")

con.sql("""
    CREATE OR REPLACE TABLE gold_customer_revenue AS
    SELECT
        customer_id,
        SUM(amount) AS revenue
    FROM silver_orders
    GROUP BY ALL
""")

con.close()
```

This is useful for:

- local transformation development
- CI
- testing
- prototyping
- reproducible analytical work
- validating SQL logic before promoting it elsewhere

---

# 57. DuckDB as a Warehouse Test Double

A **test double** is a local replacement used to exercise logic without depending on the full production dependency.

Example architecture:

```text
Production:
SQL → cloud warehouse

Local test:
SQL → DuckDB
```

Potential advantages:

- fast feedback
- lower remote dependency
- deterministic test datasets
- simpler developer onboarding

But:

```text
DuckDB success
    ≠
production warehouse compatibility proven
```

Differences may include:

- SQL dialect
- data types
- functions
- DDL/DML semantics
- transaction model
- extensions
- optimizer behavior
- performance characteristics

Use DuckDB as a test double when the SQL and semantics are close enough for the intended test.

---

# 58. Dialect Differences

“SQL” is a family of languages, not one perfectly identical implementation.

Watch for:

- date/time functions
- casting syntax
- arrays vs lists
- JSON behavior
- identifier handling
- `QUALIFY`
- vendor-specific functions
- DDL syntax
- transaction behavior
- extension-only functionality

A useful engineering phrase is:

> “DuckDB-compatible” does not automatically mean “warehouse-compatible.”

### Compatibility test design

If production SQL is intended for another engine:

```text
unit semantics tests
+
dialect compatibility tests
+
integration tests against target engine
```

DuckDB can reduce feedback time, but it should not eliminate target-engine validation when compatibility is important.

---

# 59. Required Hands-On Project — `duckdb_warehouse.py`

**Do not create the actual file in this chapter.** This section specifies the exercise the learner will implement later.

Goal:

> Build a small persistent analytical warehouse in DuckDB.

Create:

```text
lab.duckdb
```

with:

```text
raw_orders
customers
products
```

loaded from the Module 2.3 bronze Parquet outputs.

Target project architecture:

```text
Bronze Parquet
     ↓
DuckDB
     ↓
raw_* tables
     ↓
silver transformations
     ↓
gold analytical models
```

---

# 60. Project Step 1 — Persistent Database

Use:

```python
import duckdb

con = duckdb.connect("lab.duckdb")
```

Explain:

- the file is persistent
- the connection owns the session
- database state survives process termination
- local warehouse development becomes reproducible

Always close the connection when the workflow ends:

```python
con.close()
```

A robust real application may use `try/finally` or a context-management pattern around lifecycle-sensitive resources.

---

# 61. Project Step 2 — Create Raw Tables

Create the raw layer from bronze data.

Conceptual pattern:

```sql
CREATE OR REPLACE TABLE raw_orders AS
SELECT *
FROM read_parquet('bronze/orders/*.parquet');
```

Equivalent patterns can be used for:

- customers
- products

Immediately verify the schema:

```sql
DESCRIBE raw_orders;
```

and row counts:

```sql
SELECT COUNT(*) AS row_count
FROM raw_orders;
```

Also validate:

- expected key columns exist
- timestamps have expected types
- amounts are numeric
- required fields are not unexpectedly null

---

# 62. Project Step 3 — Build Silver and Gold

## Silver: deduplicate

Use a stable versioning rule:

```sql
CREATE OR REPLACE TABLE silver_orders AS
SELECT *
FROM raw_orders
QUALIFY
    ROW_NUMBER() OVER (
        PARTITION BY order_id
        ORDER BY updated_at DESC, ingestion_id DESC
    ) = 1;
```

The tie-breaker must be deterministic.

## Gold: customer revenue

```sql
CREATE OR REPLACE TABLE gold_customer_revenue AS
SELECT
    customer_id,
    SUM(amount) AS revenue,
    COUNT(*) AS order_count
FROM silver_orders
GROUP BY ALL;
```

## ASOF example

Suppose rates are time-varying:

```sql
SELECT
    o.order_id,
    o.order_ts,
    o.currency,
    o.amount,
    r.rate_to_usd
FROM silver_orders o
ASOF LEFT JOIN fx_rates r
    ON o.currency = r.currency
   AND o.order_ts >= r.rate_ts;
```

## Pivot example

```sql
PIVOT (
    SELECT
        customer_id,
        month_name,
        revenue
    FROM customer_monthly_revenue
)
ON month_name
USING SUM(revenue)
GROUP BY customer_id;
```

Your exact production query should be tested in the installed DuckDB version.

---

# 63. Project Step 4 — Query pandas and Polars Directly

Create a DataFrame:

```python
import pandas as pd

customers_pd = pd.DataFrame(
    {
        "customer_id": [1, 2, 3],
        "segment": ["gold", "silver", "gold"],
    }
)
```

Query directly:

```python
duckdb.sql("""
    SELECT segment, COUNT(*) AS customers
    FROM customers_pd
    GROUP BY segment
""").show()
```

Create a Polars DataFrame:

```python
import polars as pl

customers_pl = pl.DataFrame(
    {
        "customer_id": [1, 2, 3],
        "segment": ["gold", "silver", "gold"],
    }
)
```

Query directly:

```python
duckdb.sql("""
    SELECT segment, COUNT(*) AS customers
    FROM customers_pl
    GROUP BY segment
""").show()
```

Return Arrow when appropriate:

```python
arrow_result = duckdb.sql("""
    SELECT *
    FROM customers_pl
""").arrow()
```

Document:

- object type
- query
- result type
- reason for choosing the boundary

---

# 64. Project Step 5 — Low Memory Limit

Configure:

```sql
SET memory_limit = '1GB';
SET temp_directory = '/path/to/dedicated-temp';
```

Then run a sufficiently large aggregation.

Do not ask:

> “Did DuckDB print exactly the same spill message as the tutorial?”

Ask:

- Did the query complete?
- Did runtime change?
- Did temp storage usage change?
- Did memory stay within the intended budget?
- What does `EXPLAIN ANALYZE` show?
- Was the temporary directory large and fast enough?

This is an investigation exercise, not a scripted output exercise.

---

# 65. Project Step 6 — Parameterized Query

Build:

```sql
SELECT
    order_id,
    customer_id,
    amount
FROM raw_orders
WHERE customer_id = ?;
```

Supply the value separately from Python.

Record why this is better than constructing SQL with an f-string.

---

# 66. Project Step 7 — Tests

Specify tests using an in-memory database.

Test:

### Schema

- required tables exist
- required columns exist
- data types are expected

### Correctness

- row counts meet expectations
- deduplication produces one current record per expected key
- revenue aggregates match independent checks

### Parameterized filtering

Given:

```text
customer_id = X
```

verify only records for X are returned.

### Aggregate correctness

Compare DuckDB's result to a trusted small-data implementation.

The actual pytest file is **not** created in this chapter.

---

# 67. Query Comparison — pandas vs Polars vs DuckDB

Run the same ten analytical questions using:

- pandas
- Polars
- DuckDB SQL

Suggested questions:

1. total orders
2. total revenue
3. daily revenue
4. customer revenue
5. top-10 customers
6. latest order per customer
7. order count by status
8. monthly revenue pivot
9. as-of FX enrichment
10. nested/list attribute extraction

For each implementation record:

| Dimension | Observation |
|---|---|
| Readability | How easy is the logic to understand? |
| Execution model | DataFrame operations or SQL engine? |
| Memory behavior | Where does data materialize? |
| Data movement | How many format boundaries? |
| Testability | How easy is the transformation to validate? |
| Portability | How portable is the expression/query? |
| Operational fit | Where would it run naturally? |

Do not declare one system universally superior.

The purpose is abstraction selection.

---

# 68. SQL Example Set

## 68.1 Filtering

```sql
SELECT *
FROM orders
WHERE status = 'PAID';
```

Business use:

> isolate business-valid records before expensive transformations.

## 68.2 Aggregation

```sql
SELECT
    customer_id,
    SUM(amount) AS revenue
FROM orders
GROUP BY ALL;
```

Business use:

> customer-level metrics.

## 68.3 Multi-table joins

```sql
SELECT
    o.order_id,
    c.segment,
    p.category,
    o.amount
FROM orders o
JOIN customers c
  ON o.customer_id = c.customer_id
JOIN products p
  ON o.product_id = p.product_id;
```

## 68.4 Top-N

```sql
SELECT *
FROM customer_revenue
ORDER BY revenue DESC
LIMIT 10;
```

## 68.5 Window calculation

```sql
SELECT
    customer_id,
    order_id,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id
    ) AS customer_total
FROM orders;
```

## 68.6 Deduplication with `QUALIFY`

```sql
SELECT *
FROM orders
QUALIFY
    ROW_NUMBER() OVER (
        PARTITION BY order_id
        ORDER BY updated_at DESC
    ) = 1;
```

## 68.7 `ASOF JOIN`

```sql
SELECT
    o.order_id,
    o.order_ts,
    r.rate
FROM orders o
ASOF LEFT JOIN fx_rates r
    ON o.currency = r.currency
   AND o.order_ts >= r.rate_ts;
```

## 68.8 Pivot

```sql
PIVOT monthly_sales
ON month
USING SUM(revenue)
GROUP BY customer_id;
```

## 68.9 Unpivot

```sql
UNPIVOT monthly_sales
ON jan, feb, mar
INTO
    NAME month
    VALUE revenue;
```

## 68.10 Lists

```sql
SELECT
    list_value(10, 20, 30) AS values,
    list_contains(list_value(10, 20, 30), 20) AS found;
```

## 68.11 Struct extraction

```sql
SELECT
    struct_extract(
        struct_pack(
            customer_id := 10,
            tier := 'gold'
        ),
        'tier'
    ) AS tier;
```

## 68.12 CTAS

```sql
CREATE TABLE daily_sales AS
SELECT
    order_date,
    SUM(amount) AS revenue
FROM orders
GROUP BY ALL;
```

## 68.13 View

```sql
CREATE VIEW paid_orders AS
SELECT *
FROM orders
WHERE status = 'PAID';
```

## 68.14 Parameterized query

```python
duckdb.execute(
    """
    SELECT *
    FROM orders
    WHERE customer_id = ?
    """,
    [42],
).fetchall()
```

---

# 69. Debugging Section

## Problem 1 — “DuckDB should behave exactly like PostgreSQL”

### Symptom

A PostgreSQL query or function is copied into DuckDB and fails.

### Root cause

SQL dialects and database features differ.

### Diagnosis

- isolate the failing syntax
- check DuckDB documentation
- check whether the feature is an extension
- rewrite using DuckDB-supported semantics

### Corrected approach

Create a dialect-translation layer or use compatible SQL where possible.

### Production lesson

Do not use a local SQL engine as proof that target-engine SQL will always behave identically.

---

## Problem 2 — Multiple processes write the same DuckDB file

### Symptom

Concurrent jobs encounter locks/conflicts or unsupported access patterns.

### Root cause

The embedded file architecture is not equivalent to a central PostgreSQL server.

### Diagnosis

- list processes
- identify readers vs writers
- check access mode
- inspect database-file ownership/lifecycle

### Corrected approach

- serialize writes where appropriate
- use one writer process
- expose read-only copies to readers where suitable
- consider a different architecture when many concurrent writers are a requirement

### Production lesson

Concurrency is an architectural property, not a function you enable with one setting.

---

## Problem 3 — Huge result pulled into pandas

### Symptom

SQL is fast, then Python memory usage spikes.

### Root cause

`.df()` materializes the result as a pandas DataFrame.

### Diagnosis

Compare:

```python
duckdb.sql(query).show()
```

with:

```python
duckdb.sql(query).df()
```

and measure process memory.

### Corrected approach

- aggregate before conversion
- select fewer columns
- keep computation in DuckDB
- return Arrow/Polars only at the necessary boundary

### Production lesson

The output conversion is part of the workload.

---

## Problem 4 — Unsafe SQL string formatting

### Symptom

Unexpected SQL behavior or injection exposure.

### Root cause

Data values are concatenated into SQL text.

### Diagnosis

Search for:

```python
f"...{value}..."
```

and:

```python
"... " + value
```

### Corrected approach

Use:

```sql
WHERE customer_id = ?
```

with parameter binding.

### Production lesson

Treat SQL structure and user-provided values as different channels.

---

## Problem 5 — Memory usage exceeds expectations

### Symptom

A query runs but consumes more RAM than anticipated.

### Root cause

Possible reasons include:

- large intermediate state
- joins
- sorts
- high-cardinality aggregation
- too many threads
- large output conversion

### Diagnosis

1. `EXPLAIN`
2. `EXPLAIN ANALYZE`
3. process-level memory measurement
4. inspect result size
5. check thread setting
6. check memory limit
7. inspect temporary storage

### Corrected approach

Change one factor at a time and measure.

---

## Problem 6 — Temporary disk fills

### Symptom

A large query fails during out-of-core execution.

### Root cause

Temporary storage is insufficient.

### Diagnosis

Check:

```bash
df -h
```

and inspect the configured temp directory.

### Corrected approach

- choose a dedicated volume
- verify free capacity
- use faster storage where justified
- reduce working set if possible
- avoid assuming unlimited disk spill capacity

### Production lesson

Out-of-core means memory pressure moves partly into a disk-capacity problem.

---

## Problem 7 — Query is slow but `EXPLAIN ANALYZE` is ignored

### Symptom

The developer keeps rewriting SQL without knowing what is expensive.

### Root cause

Optimization by intuition.

### Diagnosis

Run:

```sql
EXPLAIN ANALYZE ...
```

### Corrected approach

Find:

- expensive scan
- large join
- large sort
- unexpectedly large cardinality
- repeated conversion

Then make one measured change.

### Production lesson

Performance engineering is an evidence loop.

---

## Problem 8 — Replacement scan behaves unexpectedly

### Symptom

`SELECT * FROM df` fails or references a different object than expected.

### Root cause

Python object name/scope/lifetime assumptions.

### Diagnosis

- print `type(df)`
- print `id(df)` if necessary
- inspect local/global scope
- reduce the query to a tiny reproducible example

### Corrected approach

Keep object lifetime explicit or materialize a table when persistence/reproducibility matters.

### Production lesson

A Python variable is not a database table contract.

---

## Problem 9 — Warehouse SQL differs in DuckDB

### Symptom

A locally passing query fails in production.

### Root cause

Dialect differences.

### Diagnosis

Compare:

- functions
- types
- syntax
- null handling
- date/time semantics
- extensions

### Corrected approach

Add target-engine integration tests.

### Production lesson

Local compatibility accelerates development but does not replace target-engine validation.

---

## Problem 10 — Extension is unavailable

### Symptom

A function or table function cannot be found.

### Root cause

Extension not installed/loaded, wrong version, or unsupported distribution.

### Diagnosis

Inspect:

```sql
SELECT *
FROM duckdb_extensions();
```

Then check installation/loading rules.

### Corrected approach

Use:

```sql
INSTALL extension_name;
LOAD extension_name;
```

when appropriate, and pin/reproduce the environment.

### Production lesson

Extensions are runtime dependencies and belong in your deployment contract.

---

# 70. Common Mistakes

Avoid these:

- opening the same DuckDB file for uncontrolled concurrent writes from several processes
- formatting user values directly into SQL
- pulling huge results into pandas unnecessarily
- treating DuckDB as an OLTP database
- treating DuckDB as a central shared SQL server
- ignoring temporary-disk requirements
- assuming all SQL dialects are identical
- increasing thread count without resource testing
- assuming `memory_limit` guarantees success
- relying only on `EXPLAIN` when actual runtime information is needed
- ignoring output-conversion cost
- materializing temporary tables when a relation can stay inside DuckDB
- moving between DuckDB, pandas, and Polars without a reason
- using database file persistence when an in-memory test would be sufficient
- assuming extensions are always available everywhere
- allowing test-double SQL to drift away from production SQL
- optimizing runtime while failing to validate correctness

---

# 71. Performance Engineering Perspective

Ask five questions repeatedly:

> **Where is the data?**

> **Where is the computation?**

> **Where are the copies?**

> **How much data is being scanned?**

> **Which operator is expensive?**

Then classify the bottleneck:

```text
CPU-bound
memory-bound
I/O-bound
concurrency-bound
```

A useful workflow is:

```text
Write query
    ↓
EXPLAIN
    ↓
EXPLAIN ANALYZE
    ↓
Find expensive operator
    ↓
Measure resources
    ↓
Change one thing
    ↓
Measure again
    ↓
Validate correctness
```

Do not optimize based on one anecdotal run.

---

# 72. Memory and Data-Movement Perspective

Connect the module's systems together:

```text
Parquet
   ↓
DuckDB
   ↓
Arrow
   ↓
Polars / pandas
```

Potentially problematic path:

```text
Parquet
   ↓
DuckDB
   ↓
pandas
   ↓
Polars
   ↓
NumPy
```

Each boundary may involve:

- conversion
- copies
- allocation
- serialization
- dtype handling
- increased memory pressure

This does not mean conversions are always bad.

Conversions are justified when the next tool provides the capability you actually need.

**Engineering principle:**

> Every data-format boundary should have a reason.

---

# 73. Production Architecture Examples

## Pattern 1 — Local Analytics

```text
Parquet
   ↓
DuckDB
   ↓
SQL
   ↓
Arrow / report
```

Use for:

- analyst workflows
- local investigation
- reproducible data exploration

---

## Pattern 2 — Python ETL

```text
Python orchestration
        ↓
DuckDB
        ↓
analytical transformation
        ↓
Parquet
```

Use for:

- batch transformation
- local/serverless data pipelines
- data-quality transformations

---

## Pattern 3 — DataFrame + SQL Hybrid

```text
Polars / pandas
      ↓
   DuckDB SQL
      ↓
Arrow / Polars result
```

Use when:

- DataFrame work is convenient at the edges
- SQL is clearer for joins/aggregations

---

## Pattern 4 — CI/Test Environment

```text
pytest
  ↓
DuckDB in-memory DB
  ↓
SQL validation
```

Use for:

- transformation tests
- SQL semantics tests
- reproducible fixtures

**Production lesson:** DuckDB is particularly useful when analytical logic is valuable but operational infrastructure should remain small.

---

# 74. When DuckDB Is a Good Fit

Workload characteristics often suitable for DuckDB include:

- local analytical queries
- single-node ETL
- Parquet analytics
- embedded analytics
- CI testing
- ad-hoc investigations
- development warehouses
- moderate-sized analytical transformations
- batch jobs where one process can own the analytical execution

The word **moderate** is workload-dependent.

Measure:

- data volume
- peak memory
- CPU
- I/O
- execution state
- concurrency
- SLA

---

# 75. When DuckDB May NOT Be the Right Fit

Use caution when requirements include:

- highly concurrent OLTP
- many simultaneous writers
- central multi-user database service
- distributed computation beyond one machine's practical capacity
- organizational constraints requiring a managed warehouse
- target-engine semantics that must exactly match another platform

Do not treat this as a “never” list.

The correct architecture depends on the workload.

---

# 76. DuckDB vs Polars

| Concern | DuckDB | Polars |
|---|---|---|
| Primary interface | SQL | DataFrame expressions |
| Analytical database | Yes | No |
| Persistent local DB | Yes | No |
| Local file analytics | Strong | Strong |
| SQL-heavy workflow | Natural | Possible but not primary |
| Expression-centric transformation | Available through relational API | Core model |
| Native DataFrame model | Interoperates | Native |
| Database tables/views | Yes | No |

They often complement each other:

```text
Parquet
   ↓
DuckDB SQL
   ↓
Arrow
   ↓
Polars
```

or:

```text
Polars
   ↓
DuckDB SQL
   ↓
Polars
```

There is no requirement to choose one tool for every task.

---

# 77. DuckDB + Polars + Arrow Architecture

A useful architecture diagram:

```text
                ┌─────────────┐
                │   Parquet   │
                └──────┬──────┘
                       │
                       v
                ┌─────────────┐
                │   DuckDB    │
                │     SQL     │
                └──────┬──────┘
                       │
                     Arrow
                    /     \
                   v       v
               Polars    pandas
```

Roles:

### Parquet

Portable on-disk columnar format.

### DuckDB

SQL-oriented analytical execution engine.

### Arrow

Interoperability representation.

### Polars

Expression-oriented DataFrame processing.

### pandas

Python DataFrame ecosystem and broad downstream library compatibility.

The architecture is powerful because each layer has a distinct responsibility.

---

# 78. Senior Data Engineer Design Exercise

For each scenario decide which combination makes sense:

- DuckDB
- Polars
- pandas
- PostgreSQL
- Spark
- cloud warehouse

But do not answer with “tool X is best.”

Use this reasoning framework:

1. What is the workload?
2. How large is the data?
3. What is the expected concurrency?
4. Is persistence required?
5. Is SQL or DataFrame composition more natural?
6. What are the memory limits?
7. What is the deployment model?
8. What operational complexity is acceptable?
9. What is the output?
10. What trade-offs are acceptable?

### Scenario prompts

**Scenario A:** 20 GB of Parquet analyzed nightly in a single container.

**Scenario B:** An application with thousands of concurrent user requests and frequent tiny transactions.

**Scenario C:** A local developer wants to test warehouse SQL without a cloud connection.

**Scenario D:** A 20 TB transformation already requires distributed storage and multi-machine execution.

**Scenario E:** A data-quality CI job needs deterministic SQL checks over a 500 MB fixture.

**Scenario F:** A Python pipeline performs complex DataFrame feature engineering and a few large SQL joins.

The answer is a workload-based architecture, not a ranking.

---

# 79. Explain-Aloud Exercises

## Exercise A

Explain “in-process analytical database” in 30 seconds.

A strong answer should mention:

- engine runs inside the application process
- no separate server is required
- architecture is convenient for embedded analytics
- resource/concurrency boundaries differ from a client/server DB

## Exercise B

Explain DuckDB vs PostgreSQL without saying one is “better.”

## Exercise C

Explain why DuckDB can query a pandas DataFrame directly.

## Exercise D

Explain why `.fetchall()` can be dangerous on a huge result.

## Exercise E

Explain `EXPLAIN` vs `EXPLAIN ANALYZE`.

## Exercise F

Explain disk spilling in your own words.

## Exercise G

Explain why more threads can increase resource pressure.

## Exercise H

Explain why DuckDB is not a shared transactional server.

## Exercise I

Explain why Arrow is useful between DuckDB and Polars.

## Exercise J

Explain why DuckDB can act as a local warehouse without becoming your organization's central OLTP database.

---

# 80. Interview Preparation

## Beginner

### 1. What is DuckDB?

**Answer:** DuckDB is an analytical database and query engine designed to run efficiently in-process. It is especially useful for OLAP workloads such as aggregations, joins, scans, and local analytics.

### 2. What does in-process mean?

**Answer:** The DuckDB engine runs inside the same operating-system process as the application that embeds it. A separate database server process is not required for normal embedded operation.

### 3. What is the difference between DuckDB and SQLite?

**Answer:** SQLite is widely used as an embedded transactional relational database. DuckDB is designed primarily around analytical/OLAP processing, columnar execution, vectorized execution, and analytical query patterns.

### 4. What is the difference between DuckDB and PostgreSQL?

**Answer:** PostgreSQL is a general-purpose client/server relational database used for many transactional and server-side workloads. DuckDB is primarily an embedded analytical engine. Their deployment and concurrency models differ.

### 5. What does `duckdb.connect()` do?

**Answer:** It creates a DuckDB connection. The connection can be in-memory or associated with a persistent database file such as `warehouse.duckdb`.

## Intermediate

### 6. What is a replacement scan?

**Answer:** It is the mechanism by which an unresolved table reference can be replaced by a scan of another object, such as a Python DataFrame, when the relevant integration is active.

### 7. Why can DuckDB query a pandas or Polars DataFrame directly?

**Answer:** DuckDB's Python integration can resolve Python-scope DataFrame objects and expose them to the SQL engine. This avoids requiring a manual copy into a persistent DuckDB table for every query.

### 8. Why is DuckDB good for OLAP?

**Answer:** Its execution architecture emphasizes analytical scans, vectorized computation, parallel execution, efficient aggregation/join processing, and column-oriented access patterns.

### 9. What is vectorized execution?

**Answer:** Instead of processing one row at a time conceptually, operators process batches/vectors of values, reducing per-row overhead and improving hardware efficiency.

### 10. What is `QUALIFY`?

**Answer:** `QUALIFY` filters rows based on window-function results without requiring a separate subquery solely for that filtering step.

### 11. Why use `ASOF JOIN`?

**Answer:** It expresses temporal matching such as finding the latest reference record at or before an event timestamp.

### 12. What is `GROUP BY ALL`?

**Answer:** It groups by all selected columns that are not aggregates, reducing repeated column lists and keeping projection/granularity aligned.

### 13. What is a persistent DuckDB database?

**Answer:** A DuckDB database backed by a persistent file, allowing its tables and data to survive process termination.

## Advanced

### 14. How does DuckDB differ architecturally from a client/server database?

**Answer:** DuckDB can execute directly inside the application process rather than requiring a separately managed database server and network connection. This reduces deployment overhead but changes concurrency, operational, and multi-user assumptions.

### 15. Why does DuckDB use columnar/vectorized execution?

**Answer:** Analytical workloads often process many rows but only selected columns and apply the same operations to large batches of values. Columnar/vectorized execution can reduce unnecessary data movement and per-row overhead.

### 16. How would you investigate a slow DuckDB query?

**Answer:** Establish a reproducible workload, run `EXPLAIN`, run `EXPLAIN ANALYZE`, identify expensive operators and unexpected cardinalities, measure CPU/memory/I/O behavior, make one targeted change, rerun, and validate correctness.

### 17. How would you parameterize SQL safely?

**Answer:** Keep SQL structure static and pass user values as parameters using placeholders such as `?`. Avoid string concatenation or f-string interpolation for untrusted values.

### 18. How does out-of-core execution help?

**Answer:** It allows some workloads to operate beyond available RAM by processing in chunks and potentially moving temporary state to disk. It increases feasible workload size at the cost of additional I/O and storage dependency.

### 19. What role does `temp_directory` play?

**Answer:** It identifies where DuckDB can place temporary execution files. A suitable directory must have enough capacity and appropriate performance.

### 20. Why can multiple writers be problematic?

**Answer:** Embedded database files do not provide the same multi-process server coordination model as PostgreSQL. Concurrency within one process is more flexible than uncontrolled concurrent writes from multiple processes.

### 21. Why is DuckDB unsuitable as a conventional OLTP backend?

**Answer:** Its architecture is centered on analytical workloads, not thousands of concurrent small transactional requests and multi-tenant server-side application access.

### 22. How would you use DuckDB as a test double?

**Answer:** Use DuckDB to run analytical SQL against controlled local fixtures, then validate important semantics against the target production warehouse because dialect and execution differences remain.

### 23. What dialect compatibility problems could appear?

**Answer:** Function names, casting, date/time behavior, list/array syntax, identifiers, extensions, DDL/DML syntax, and vendor-specific features can differ.

### 24. How would you combine DuckDB, Polars, and Arrow?

**Answer:** Keep heavy relational work in the engine that fits the transformation, use Arrow as an efficient interoperability boundary where appropriate, and avoid unnecessary conversions. One valid architecture is Parquet → DuckDB SQL → Arrow → Polars.

---

# 81. Practice Problems

## Basic — 10

### B1
Install DuckDB with `uv` and print its version.

**Answer:** Use `uv add duckdb`, then import `duckdb` and print `duckdb.__version__`.

### B2
Create an in-memory DuckDB database and execute `SELECT 42`.

**Answer:** `con = duckdb.connect(":memory:")`, then `con.sql("SELECT 42").fetchall()`.

### B3
Create a persistent database file named `lab.duckdb`.

**Answer:** `duckdb.connect("lab.duckdb")`.

### B4
Create a table containing `id` and `amount`.

**Answer:** Use `CREATE TABLE` with appropriate numeric types.

### B5
Create a view containing only paid orders.

**Answer:** `CREATE VIEW paid_orders AS SELECT ... WHERE status = 'PAID'`.

### B6
Create a daily revenue table using CTAS.

**Answer:** `CREATE TABLE daily_revenue AS SELECT order_date, SUM(amount) ... GROUP BY order_date`.

### B7
Return a query as Python rows.

**Answer:** call `.fetchall()`.

### B8
Return a query as pandas.

**Answer:** call `.df()`.

### B9
Return a query as Polars.

**Answer:** call `.pl()`.

### B10
Return a query as Arrow.

**Answer:** call `.arrow()`.

---

## Moderate — 10

### M1
Query a pandas DataFrame directly.

**Answer:** create `orders_df` and use `SELECT * FROM orders_df` in DuckDB SQL. DuckDB's Python integration resolves the DataFrame by name.

### M2
Query a Polars DataFrame directly.

**Answer:** create `orders_pl` and use `SELECT * FROM orders_pl`.

### M3
Explain replacement scans.

**Answer:** an unresolved SQL table name can be replaced by a scan of a relevant Python-scope object through DuckDB's replacement-scan mechanism.

### M4
Write a `GROUP BY ALL` query for customer revenue.

**Answer:**
```sql
SELECT customer_id, SUM(amount) AS revenue
FROM orders
GROUP BY ALL;
```

### M5
Exclude `raw_payload` from a wide table.

**Answer:**
```sql
SELECT * EXCLUDE (raw_payload)
FROM orders;
```

### M6
Normalize status values with `REPLACE`.

**Answer:**
```sql
SELECT *
REPLACE (upper(status) AS status)
FROM orders;
```

### M7
Find the latest order per customer.

**Answer:** use `ROW_NUMBER()` with `QUALIFY`.

### M8
Explain an as-of join use case.

**Answer:** time-varying reference data such as FX rates or market prices.

### M9
Convert a monthly wide table back to long format.

**Answer:** use `UNPIVOT`.

### M10
Build an Arrow result.

**Answer:** execute the query and call `.arrow()`.

---

## Hard — 10

### H1
Use `EXPLAIN` to inspect a grouped query.

**Answer:** prepend `EXPLAIN` and inspect scan, filter, aggregate, join, sort, and other physical operators.

### H2
Use `EXPLAIN ANALYZE` to investigate actual runtime.

**Answer:** prepend `EXPLAIN ANALYZE`; interpret actual cardinality and operator timing rather than relying on intuition.

### H3
Set a 2 GB memory limit.

**Answer:**
```sql
SET memory_limit = '2GB';
```

### H4
Restrict DuckDB to four threads.

**Answer:**
```sql
SET threads = 4;
```

### H5
Set a dedicated temporary directory.

**Answer:**
```sql
SET temp_directory = '/path/to/tmp';
```

### H6
Explain why a query can spill even though its source file is smaller than RAM.

**Answer:** compressed source size is not execution working-set size. Intermediates, decompression, joins, sorting, aggregation state, and output can increase resource needs.

### H7
Explain why `.fetchall()` can dominate memory.

**Answer:** it materializes the full result into Python-native row objects.

### H8
Explain why increasing threads can increase memory pressure.

**Answer:** more workers can produce more concurrent intermediate state and buffers.

### H9
Explain the transaction concept.

**Answer:** group changes into atomic units that can commit or roll back.

### H10
Explain why multi-process concurrent writing needs special care.

**Answer:** the embedded native database-file architecture is not equivalent to a centralized transactional server.

---

## Advanced — 10

### A1
Design a local warehouse using DuckDB and bronze Parquet.

**Answer:** connect to a persistent `.duckdb` file, create raw tables from Parquet, build silver transformations, then materialize gold metrics as tables or views.

### A2
Design a CI test double for warehouse SQL.

**Answer:** load controlled fixtures into an in-memory DuckDB database, run SQL assertions, then use target-engine integration tests for important dialect compatibility.

### A3
Explain three ways to reduce data movement between DuckDB and Python.

**Answer:** keep transformations in DuckDB until an edge is needed, return Arrow/Polars rather than Python row objects for analytical data, and avoid converting to pandas only to immediately convert again.

### A4
Investigate a query that is CPU-fast but memory-heavy.

**Answer:** inspect `EXPLAIN ANALYZE`, find high-state operators, reduce columns/rows, reduce output size, tune threads, and use memory limits/temp storage where appropriate.

### A5
Investigate a query that becomes slow with a low memory limit.

**Answer:** determine whether temporary disk usage increased, inspect temp-directory capacity and I/O, then compare execution with a higher but controlled memory budget.

### A6
Explain a test where DuckDB passes but PostgreSQL fails.

**Answer:** the test validated SQL semantics only against DuckDB; dialect and target-engine integration differences remain.

### A7
Choose the boundary between DuckDB and Polars.

**Answer:** place SQL-heavy joins/aggregations where SQL is clearer, then hand a reasonably sized result to Polars when expression-oriented transformations are more natural.

### A8
Design a parameterized customer lookup service using DuckDB.

**Answer:** use a prepared query with `?`, avoid string interpolation, validate result size, and bound access/concurrency according to the embedded architecture.

### A9
Explain how Arrow fits into DuckDB/Polars interoperability.

**Answer:** Arrow provides a common columnar representation that can reduce friction and unnecessary custom serialization between engines, subject to type and API-path details.

### A10
Explain when a single-node DuckDB architecture should be reconsidered.

**Answer:** when one machine cannot meet memory/CPU/I/O/SLA requirements, when concurrency requirements exceed the embedded model, or when organizational architecture requires a different managed/distributed platform.

---

# 82. Final Practical Lab

> **Build a small local analytical warehouse using DuckDB.**

The learner must:

1. create a persistent DuckDB database
2. load bronze data
3. create tables
4. create views
5. deduplicate data
6. build analytical metrics
7. use `QUALIFY`
8. use `ASOF JOIN`
9. build a pivot report
10. query pandas directly
11. query Polars directly
12. return Arrow
13. parameterize a query
14. inspect `EXPLAIN`
15. inspect `EXPLAIN ANALYZE`
16. set a memory limit
17. configure a temporary directory
18. test a larger aggregation
19. validate correctness
20. document architectural limitations

Deliver a short engineering note:

```text
What problem did DuckDB solve?
What remained inside DuckDB?
Where did data leave DuckDB?
What resource bottleneck did you observe?
What concurrency assumptions did you make?
How would the architecture change at larger scale?
```

---

# 83. Benchmarking Requirements

Never fabricate benchmark numbers.

Every comparison between DuckDB, Polars, or pandas must document:

- data size
- row count
- column count
- file format
- query/business logic
- CPU
- RAM
- operating system
- DuckDB version
- Polars version
- pandas version
- thread settings
- repetition count
- cache/warm state when relevant

Measure:

- wall-clock time
- peak memory where practical
- output conversion time where relevant
- correctness

For file-based workflows, also consider:

- bytes read
- files touched
- output size

The benchmark contract is:

```text
same data
+
same business logic
+
same hardware
+
same environment
+
same measurement method
```

Then compare:

```text
runtime
peak memory
correctness
```

The benchmark tells you what happened in that environment.

It does not prove a universal ranking.

---

# 84. Correctness Requirements

The rule is:

```text
faster
≠
correct
```

Every optimization experiment must validate:

### Row count

Do both implementations produce the expected number of rows?

### Schema

Do names and data types remain correct?

### Aggregates

Do totals, counts, averages, and other business metrics match?

### Values

Do important record-level values match?

### Ordering

If order is semantically relevant, specify it.

If output order is not semantically defined, sort both results before comparison.

### Example

```python
expected = ...
actual = ...

# Compare after canonical sorting when order is not meaningful.
```

**Production rule:**

> Performance optimization without correctness validation is an unacceptable Data Engineering practice.

---

# 85. Version Awareness

DuckDB evolves quickly.

For version-sensitive APIs:

1. check `duckdb.__version__`
2. read current documentation
3. run a minimal reproducibility test
4. document assumptions
5. avoid deprecated syntax
6. do not invent function signatures

Pay special attention to:

- relational API
- result conversion
- extensions
- memory settings
- remote-access features
- concurrency model
- new SQL features

A good documentation comment is:

```text
Verified against DuckDB version X.Y.Z on YYYY-MM-DD.
Re-check before upgrading DuckDB.
```

Do not write a version claim unless you actually ran the version check.

---

# 86. Technical Accuracy Requirements

Be precise about:

- in-process architecture
- embedded database terminology
- OLAP vs OLTP
- replacement scans
- Python object lifetime
- columnar processing
- vectorized execution
- parallelism
- optimizer concepts
- SQL execution plans
- parameter binding
- `EXPLAIN`
- `EXPLAIN ANALYZE`
- memory limits
- temporary storage
- spilling
- transactions
- ACID semantics
- concurrency
- single-process vs multi-process access
- extensions
- local warehouse design
- test-double limitations
- dialect portability

Avoid technically misleading statements such as:

> “DuckDB is just SQLite but faster.”

or:

> “DuckDB replaces PostgreSQL.”

or:

> “If DuckDB completed the query, memory is no longer a concern.”

The correct mental model is workload-specific architecture.

---

# 87. Important Architectural Lesson

Memorize this:

```text
DuckDB is not just “a SQL library.”

DuckDB is an analytical database engine
embedded into the process.
```

Why does that matter?

Because a database engine includes:

- query parsing
- optimization
- execution planning
- execution operators
- storage
- transactions
- resource management
- concurrency behavior
- extensibility

Thinking this way changes how you debug.

You stop asking only:

> “What SQL should I write?”

and start asking:

> “What execution does this SQL cause?”

---

# 88. Important Performance Lesson

Use this model:

```text
SQL syntax
    ↓
query plan
    ↓
physical execution
    ↓
resource usage
    ↓
actual performance
```

Therefore:

> Two SQL queries can return the same result while doing very different amounts of work.

That is why:

```sql
EXPLAIN
```

and:

```sql
EXPLAIN ANALYZE
```

matter.

The query string is the beginning of performance analysis, not the end.

---

# 89. Important Data-Movement Lesson

Data movement can become part of the workload.

Potentially expensive path:

```text
Parquet
   ↓
DuckDB
   ↓
pandas
   ↓
Polars
```

Potentially simpler path when appropriate:

```text
Parquet
   ↓
DuckDB
   ↓
Arrow
```

The goal is not “never convert.”

The goal is:

> **Convert only when the next tool needs the conversion.**

Do not assume every Arrow boundary is zero-copy. Exact behavior depends on the objects, data types, conversion path, and versions.

---

# 90. Common Production Questions

## Should I persist everything in DuckDB?

No universal rule.

Persist when:

- the result is reused
- recomputation is expensive
- you need stable local state
- a local warehouse file is part of the workflow

Use in-memory when:

- the database is disposable
- tests should start clean
- persistence has no business value

---

## When should I use a DuckDB file versus in-memory mode?

Use a file when persistence matters.

Use memory when lifecycle is intentionally temporary.

---

## Can multiple processes write the same DuckDB file?

Do not assume PostgreSQL-like multi-process write semantics. Check the current concurrency documentation for your DuckDB version and design around the supported access model.

For the standard embedded workflow, uncontrolled concurrent writers should be treated as a design problem.

---

## Can many readers use a DuckDB file?

Read-only multi-process access is supported in the documented model. Verify exact access mode and file-system assumptions for production.

---

## Should I use DuckDB as an application backend?

For conventional high-concurrency OLTP, a client/server database such as PostgreSQL is often a more natural architectural model.

The decision must be based on workload requirements.

---

## Should I use DuckDB in CI?

Yes, it can be very useful for analytical SQL tests, local fixtures, and deterministic development workflows.

Still validate target-engine compatibility where required.

---

## Can DuckDB replace PostgreSQL?

Do not treat them as interchangeable. They solve different architectural problems.

---

## Can DuckDB replace Spark?

Not as a general architectural statement.

Single-node embedded analytics and distributed computation address different scale and operational requirements.

---

## Can DuckDB replace a cloud warehouse?

Sometimes a workload can be moved to an embedded engine; sometimes organizational scale, governance, concurrency, or platform requirements make a warehouse appropriate.

Evaluate the actual workload.

---

## Can DuckDB query data without loading it into a table?

Yes, depending on the source and integration path. Python DataFrame replacement scans are one example. File-oriented capabilities become a major topic in Topic 06.

---

## When should I convert results to pandas?

When downstream code genuinely needs pandas and the result size is appropriate.

---

## When should I keep results in DuckDB?

When another SQL transformation is still required.

---

## When should I return Arrow?

When Arrow is the natural interoperability boundary.

---

## How do I investigate memory pressure?

Use:

```text
EXPLAIN
EXPLAIN ANALYZE
+
process memory measurements
+
thread settings
+
memory_limit
+
temp-directory observations
```

Then reason about joins, aggregates, sorts, result size, and data conversion.

---

## How do I investigate a slow query?

Use:

```text
EXPLAIN
    ↓
EXPLAIN ANALYZE
    ↓
expensive operator
    ↓
resource measurement
    ↓
one controlled change
    ↓
re-measure
    ↓
validate correctness
```

---

# 91. Mastery Checklist

- [ ] I understand what DuckDB is.
- [ ] I understand “in-process.”
- [ ] I can explain DuckDB vs SQLite vs PostgreSQL.
- [ ] I can install and verify DuckDB.
- [ ] I can use `duckdb.sql()`.
- [ ] I can use `duckdb.connect()`.
- [ ] I understand in-memory databases.
- [ ] I understand persistent DuckDB databases.
- [ ] I understand tables.
- [ ] I understand views.
- [ ] I understand CTAS.
- [ ] I can query pandas DataFrames directly.
- [ ] I can query Polars DataFrames directly.
- [ ] I can query Arrow tables directly.
- [ ] I understand replacement scans.
- [ ] I can use `.fetchall()`.
- [ ] I can use `.df()`.
- [ ] I can use `.pl()`.
- [ ] I can use `.arrow()`.
- [ ] I understand `.fetchnumpy()`.
- [ ] I understand columnar execution.
- [ ] I understand vectorized execution.
- [ ] I understand parallel execution.
- [ ] I understand cost-based optimization.
- [ ] I can use `GROUP BY ALL`.
- [ ] I can use `SELECT * EXCLUDE`.
- [ ] I can use `REPLACE`.
- [ ] I can use `QUALIFY`.
- [ ] I can use `ASOF JOIN`.
- [ ] I understand `PIVOT`.
- [ ] I understand `UNPIVOT`.
- [ ] I understand FROM-first syntax.
- [ ] I can work with list functions.
- [ ] I can work with struct functions.
- [ ] I understand the relational Python API.
- [ ] I can use parameterized queries.
- [ ] I understand SQL injection risk.
- [ ] I can read `EXPLAIN`.
- [ ] I can read `EXPLAIN ANALYZE`.
- [ ] I understand `memory_limit`.
- [ ] I understand `threads`.
- [ ] I understand `temp_directory`.
- [ ] I understand out-of-core execution.
- [ ] I understand disk spilling.
- [ ] I understand transactions.
- [ ] I understand ACID.
- [ ] I understand DuckDB concurrency.
- [ ] I understand the standard embedded/native-file single-writer-style operational boundary and current concurrency nuances.
- [ ] I understand why DuckDB is not PostgreSQL.
- [ ] I understand why DuckDB is not a shared multi-user server.
- [ ] I understand DuckDB extensions.
- [ ] I understand `httpfs`.
- [ ] I understand `json`.
- [ ] I understand `delta`.
- [ ] I understand `iceberg`.
- [ ] I understand `spatial`.
- [ ] I understand DuckDB as a local development warehouse.
- [ ] I understand DuckDB as a test double.
- [ ] I understand SQL dialect differences.
- [ ] I completed `duckdb_warehouse.py`.
- [ ] I completed the performance investigation.
- [ ] I completed the replacement-scan lab.
- [ ] I completed the parameterized-query lab.
- [ ] I can explain DuckDB architecture aloud.

---

# 92. Final Mastery Assessment

> **Important:** Do not look at the answer key until you have attempted the whole assessment.

## Part A — Fundamentals (15)

### A1
Define DuckDB in one technically accurate sentence.

### A2
Explain “in-process.”

### A3
Why is DuckDB particularly suited to OLAP-style workloads?

### A4
Give one architectural distinction between DuckDB and PostgreSQL.

### A5
Give one architectural distinction between DuckDB and SQLite.

### A6
What is the difference between an in-memory and persistent DuckDB database?

### A7
What does `duckdb.sql(...)` provide?

### A8
What does `duckdb.connect(...)` provide?

### A9
What is a table?

### A10
What is a view?

### A11
What does CTAS mean?

### A12
Why is `.fetchall()` inappropriate for many huge analytical outputs?

### A13
What is Arrow's role in the DuckDB/Polars ecosystem?

### A14
What is a replacement scan?

### A15
Why is understanding the embedded architecture important?

---

## Part B — SQL and Python (15)

### B1
Write a Python example that connects to an in-memory DuckDB database.

### B2
Write SQL to create a `customers` table.

### B3
Write SQL to create a view containing active customers.

### B4
Write CTAS SQL for daily sales.

### B5
Write SQL using `GROUP BY ALL`.

### B6
Write SQL using `SELECT * EXCLUDE`.

### B7
Write SQL using `REPLACE`.

### B8
Write a latest-row query using `QUALIFY`.

### B9
Write an `ASOF JOIN` for FX rates.

### B10
Write a simple `PIVOT`.

### B11
Write a simple `UNPIVOT`.

### B12
Create and inspect a list.

### B13
Create and extract a struct field.

### B14
Write a parameterized query with `?`.

### B15
Return a DuckDB result as Polars.

---

## Part C — Query Plan Analysis (10)

### C1
What question does `EXPLAIN` answer?

### C2
What additional information does `EXPLAIN ANALYZE` provide?

### C3
Why can operator timings sum to more than wall-clock time?

### C4
What does a table scan represent?

### C5
Why is a large join worth inspecting?

### C6
Why is a global sort often a candidate for investigation?

### C7
Why can cardinality estimates matter?

### C8
What would an unexpected large intermediate row count suggest?

### C9
Why can the SQL text alone be misleading for performance analysis?

### C10
Describe the optimization loop from plan to validated improvement.

---

## Part D — Resource and Memory Management (10)

### D1
Set `memory_limit` to 4 GB.

### D2
Set DuckDB to four threads.

### D3
Set a temporary directory.

### D4
Explain why a low memory limit can make a query slower.

### D5
Explain spilling.

### D6
Explain why temporary disk capacity is a production dependency.

### D7
Explain how thread count and memory are related.

### D8
Explain why result conversion can cause a memory spike.

### D9
Name three operators/workloads that can create substantial intermediate state.

### D10
Give three measurements you would collect during a memory investigation.

---

## Part E — Concurrency and Architecture (10)

### E1
Why is DuckDB not a conventional OLTP server?

### E2
Why can multiple concurrent writers be problematic?

### E3
What is the difference between concurrency within a process and between processes?

### E4
When is an in-memory database a good fit?

### E5
When is a persistent DuckDB file a good fit?

### E6
Why can DuckDB be a good local warehouse?

### E7
Why can DuckDB be useful in CI?

### E8
What makes DuckDB useful as a test double?

### E9
Why does a test double not prove full warehouse compatibility?

### E10
Name three signals that indicate you may need another architecture.

---

## Part F — Debugging (10)

### F1
A query is fast in DuckDB but the Python process runs out of memory. What do you inspect first?

### F2
A query works in DuckDB but not PostgreSQL.

### F3
A second process cannot safely write the same DuckDB file.

### F4
A spill-heavy query fills its temporary volume.

### F5
A result conversion to pandas causes memory growth.

### F6
SQL uses f-string interpolation for user values.

### F7
A replacement scan cannot resolve the expected DataFrame.

### F8
An extension function is missing.

### F9
A query is slow but no plan has been inspected.

### F10
A developer raises `threads` and now receives OOM failures.

---

## Part G — Senior Data Engineering Design (10)

### G1
Design a local warehouse for 200 GB of Parquet on one machine.

### G2
Design a CI environment for analytical SQL testing.

### G3
Design a Python ETL flow that uses DuckDB and Polars together.

### G4
Design a low-memory DuckDB pipeline.

### G5
Design a parameterized SQL service with a DuckDB backend.

### G6
Decide whether a workload belongs in DuckDB or PostgreSQL based on requirements.

### G7
Decide whether a workload belongs in DuckDB or Spark based on scale and architecture.

### G8
Design a DuckDB test-double strategy for a cloud warehouse.

### G9
Design a data-movement-minimizing DuckDB/Arrow/Polars pipeline.

### G10
Explain when you would move from single-node DuckDB to a distributed/cloud architecture.

---

# 93. Complete Answer Key

## Part A — Fundamentals

### A1 Answer

DuckDB is an embedded analytical database and query engine designed primarily for OLAP workloads.

### A2 Answer

“In-process” means the DuckDB engine runs inside the same OS process as the application that embeds it.

### A3 Answer

DuckDB is designed around analytical scans, vectorized execution, parallelism, and SQL patterns such as aggregations and joins.

### A4 Answer

PostgreSQL is a client/server relational database, while DuckDB is primarily an embedded analytical engine.

### A5 Answer

SQLite is commonly used for embedded transactional storage; DuckDB is designed primarily for analytical execution.

### A6 Answer

An in-memory database does not persist its database state to a durable database file; a persistent DuckDB database stores database state in a file.

### A7 Answer

`duckdb.sql(...)` provides convenient SQL execution and returns a DuckDB relation/result that can be converted to several output formats.

### A8 Answer

`duckdb.connect(...)` gives explicit control over a DuckDB database connection and can point to an in-memory database or persistent file.

### A9 Answer

A table is a stored relation containing data.

### A10 Answer

A view is a saved query definition that represents a logical relation.

### A11 Answer

CTAS means `CREATE TABLE AS SELECT`; it materializes a query result into a table.

### A12 Answer

Because `.fetchall()` materializes every result row as Python objects, potentially multiplying memory overhead.

### A13 Answer

Arrow provides a columnar interoperability representation between DuckDB and other analytical systems such as Polars.

### A14 Answer

A replacement scan can resolve an otherwise unknown table reference by replacing it with a scan of another object, such as a Python DataFrame.

### A15 Answer

Because deployment, memory, concurrency, persistence, and debugging are all affected by the fact that the analytical engine runs inside the application process.

---

## Part B — SQL and Python

### B1 Answer

```python
import duckdb

con = duckdb.connect(":memory:")
```

### B2 Answer

```sql
CREATE TABLE customers (
    customer_id BIGINT,
    name VARCHAR
);
```

### B3 Answer

```sql
CREATE VIEW active_customers AS
SELECT *
FROM customers
WHERE is_active = TRUE;
```

### B4 Answer

```sql
CREATE TABLE daily_sales AS
SELECT
    order_date,
    SUM(amount) AS revenue
FROM orders
GROUP BY ALL;
```

### B5 Answer

```sql
SELECT
    customer_id,
    order_date,
    SUM(amount) AS revenue
FROM orders
GROUP BY ALL;
```

### B6 Answer

```sql
SELECT *
EXCLUDE (raw_payload)
FROM orders;
```

### B7 Answer

```sql
SELECT *
REPLACE (upper(status) AS status)
FROM orders;
```

### B8 Answer

```sql
SELECT *
FROM orders
QUALIFY
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY updated_at DESC, order_id DESC
    ) = 1;
```

### B9 Answer

```sql
SELECT
    o.order_id,
    o.currency,
    o.order_ts,
    r.rate
FROM orders o
ASOF LEFT JOIN fx_rates r
    ON o.currency = r.currency
   AND o.order_ts >= r.rate_ts;
```

### B10 Answer

A valid current DuckDB form is conceptually:

```sql
PIVOT monthly_sales
ON month
USING SUM(revenue)
GROUP BY customer_id;
```

### B11 Answer

```sql
UNPIVOT monthly_sales
ON jan, feb, mar
INTO
    NAME month
    VALUE revenue;
```

### B12 Answer

```sql
SELECT
    [10, 20, 30] AS values,
    len([10, 20, 30]) AS n;
```

### B13 Answer

```sql
SELECT struct_extract(
    struct_pack(
        customer_id := 10,
        tier := 'gold'
    ),
    'tier'
) AS tier;
```

### B14 Answer

```python
duckdb.execute(
    """
    SELECT *
    FROM orders
    WHERE customer_id = ?
    """,
    [42],
).fetchall()
```

### B15 Answer

```python
result = duckdb.sql("SELECT * FROM orders").pl()
```

---

## Part C — Query Plan Analysis

### C1 Answer

`EXPLAIN` shows the planned execution structure.

### C2 Answer

`EXPLAIN ANALYZE` executes the query and adds actual runtime/cardinality information.

### C3 Answer

Parallel workers can execute operators simultaneously, so cumulative operator times can exceed total wall-clock time.

### C4 Answer

A table scan reads data from a relation or file source into the execution pipeline.

### C5 Answer

Joins can create large intermediate results and require substantial state, especially when both inputs are large.

### C6 Answer

Global ordering can require significant work and memory relative to a simple filter.

### C7 Answer

Cardinality estimates influence planning decisions; large estimation errors can lead to poor strategies.

### C8 Answer

It suggests a transformation is not reducing the dataset as expected or that a join is multiplying rows.

### C9 Answer

Two queries with similar SQL shape can have different physical plans and resource costs.

### C10 Answer

```text
measure baseline
   ↓
EXPLAIN
   ↓
EXPLAIN ANALYZE
   ↓
find expensive operator
   ↓
make targeted change
   ↓
remeasure
   ↓
validate correctness
```

---

## Part D — Resource and Memory Management

### D1 Answer

```sql
SET memory_limit = '4GB';
```

### D2 Answer

```sql
SET threads = 4;
```

### D3 Answer

```sql
SET temp_directory = '/path/to/tmp';
```

### D4 Answer

A lower memory limit can force more temporary work to disk or make previously feasible operations fail.

### D5 Answer

Spilling moves temporary execution state from memory to disk and reads it back when needed.

### D6 Answer

If temporary storage fills, execution may fail even when system RAM is sufficient.

### D7 Answer

More threads can increase simultaneous work and therefore increase memory pressure.

### D8 Answer

Conversion to pandas, Python rows, or another representation may materialize a large final result and require additional allocation.

### D9 Answer

Examples:

- large joins
- high-cardinality aggregations
- global sorts

### D10 Answer

Examples:

- wall time
- peak process memory
- temporary-disk usage

---

## Part E — Concurrency and Architecture

### E1 Answer

DuckDB is optimized around embedded analytical execution rather than conventional high-concurrency OLTP server workloads.

### E2 Answer

Multiple processes do not automatically share the same write-coordination model as a central client/server database.

### E3 Answer

Within one process, DuckDB can use multiple threads and its concurrency controls. Across processes, access to the same database file follows a different, more constrained model.

### E4 Answer

In-memory mode is useful for disposable tests, small experiments, and workflows where persistence has no value.

### E5 Answer

A persistent file is useful for local warehouses, repeatable development, reusable tables, and durable analytical state.

### E6 Answer

It can provide database-style SQL, persistence, and analytical execution without requiring a separately operated server.

### E7 Answer

It can run analytical SQL deterministically in a local test process with minimal infrastructure.

### E8 Answer

It can approximate analytical SQL behavior locally before sending workloads to a more complex production platform.

### E9 Answer

Dialect, type, extension, optimizer, transaction, and performance differences can remain.

### E10 Answer

Examples:

- one-machine resources no longer satisfy the workload
- concurrency requirements exceed the embedded model
- centralized platform/governance requirements dominate

---

## Part F — Debugging

### F1 Answer

Inspect result size, output conversion, `EXPLAIN ANALYZE`, high-state operators, threads, memory limits, and process-level memory.

### F2 Answer

Check dialect/function/type differences and validate against the actual PostgreSQL environment.

### F3 Answer

Reassess the writer/process architecture; serialize writes or use a different storage/serving architecture when required.

### F4 Answer

Inspect temporary storage capacity, choose a dedicated volume, and reduce execution working set where possible.

### F5 Answer

Avoid materializing an oversized result into pandas; aggregate/filter first or choose a more suitable boundary.

### F6 Answer

Replace interpolation with parameter binding:

```sql
WHERE customer_id = ?
```

### F7 Answer

Check Python scope and object lifetime, variable naming, and installed integration support. Build a tiny reproducible example.

### F8 Answer

Check extension installation/loading and DuckDB version.

### F9 Answer

Run `EXPLAIN` followed by `EXPLAIN ANALYZE`.

### F10 Answer

Reduce threads, measure memory again, and determine whether additional parallelism was increasing simultaneous intermediate state.

---

## Part G — Senior Data Engineering Design

### G1 Answer

Use a persistent DuckDB database on a machine with enough CPU/RAM/local storage, read Parquet into transformations, control resources, measure peak memory, and partition work logically where semantics permit. If the single-node SLA or resource envelope cannot be met, move to a larger/distributed architecture.

### G2 Answer

Use an in-memory DuckDB database with small deterministic fixtures. Validate schemas, row counts, aggregates, and critical SQL semantics. Add target-engine integration tests for production compatibility.

### G3 Answer

Use DuckDB for SQL-heavy joins/aggregations and Polars for expression-oriented transformations where that makes the code clearer. Use Arrow as an intentional interoperability boundary.

### G4 Answer

Reduce rows and columns early, avoid unnecessary output materialization, cap threads appropriately, configure `memory_limit`, provide sufficient temp storage, and measure `EXPLAIN ANALYZE` plus OS-level resource usage.

### G5 Answer

Use parameterized queries, bound the expected result size, use explicit connections, and confirm that application concurrency requirements fit DuckDB's embedded model. If they do not, use a client/server transactional architecture.

### G6 Answer

Choose based on workload:

```text
high-concurrency transactions
→ client/server OLTP architecture

embedded analytical transformation
→ DuckDB may fit
```

Do not decide from database popularity or benchmark headlines.

### G7 Answer

DuckDB is appropriate for single-node analytical workloads within the machine's practical limits. Spark becomes relevant when distributed computation, cluster-scale data movement, or organizational distributed-platform requirements become central.

### G8 Answer

Use DuckDB locally for fast SQL feedback, fixtures, and semantics tests; run targeted integration tests against the production warehouse.

### G9 Answer

Keep data inside DuckDB for as much relational processing as practical, avoid unnecessary pandas conversion, and use Arrow/Polars only at meaningful boundaries.

### G10 Answer

Move away from single-node DuckDB when:

- resource requirements exceed one machine
- SLAs cannot be met
- concurrency needs exceed the embedded architecture
- fault tolerance/distributed processing becomes necessary
- organizational platform requirements make another architecture preferable

---

# 94. Final “Teach It Back” Exercise

Close your notes and explain the following in your own words.

## Part 1 — Architecture

1. What is DuckDB?
2. What does in-process mean?
3. Why is DuckDB analytical?
4. Why is DuckDB different from PostgreSQL?
5. Why is DuckDB different from SQLite?

## Part 2 — Execution

6. Why can DuckDB be fast?
7. What is columnar execution?
8. What is vectorized execution?
9. What is parallel execution?
10. Why does the optimizer matter?
11. What is a physical query plan?
12. Why does `EXPLAIN ANALYZE` matter?

## Part 3 — Python interoperability

13. What are replacement scans?
14. Why can DuckDB query pandas directly?
15. Why can DuckDB query Polars directly?
16. Why is Arrow useful?
17. When would you use `.fetchall()`?
18. When would you use `.df()`?
19. When would you use `.pl()`?
20. When would you use `.arrow()`?

## Part 4 — Resource management

21. Why can a query need more RAM than the input file size?
22. What does `memory_limit` do?
23. What does `threads` do?
24. Why does thread count affect memory?
25. What is `temp_directory`?
26. What is spilling?
27. Why is temporary disk part of capacity planning?

## Part 5 — Architecture boundaries

28. Why is DuckDB not a conventional OLTP server?
29. Why can concurrent writers be problematic?
30. Why can DuckDB be a local warehouse?
31. Why can DuckDB be useful in CI?
32. Why does a test double not guarantee production compatibility?
33. When would you combine DuckDB with Polars?
34. When would you use Arrow as the interchange boundary?
35. When would you stop scaling the single-node design?

A strong teach-back answer should connect:

```text
workload
  ↓
architecture
  ↓
query plan
  ↓
execution
  ↓
resources
  ↓
interoperability
  ↓
correctness
  ↓
production boundary
```

---

# 95. Production Mental Model

The entire topic can be reduced to one engineering model:

```text
                 WORKLOAD
                    │
                    v
             ┌─────────────┐
             │   DuckDB    │
             │  SQL/query  │
             │    engine   │
             └──────┬──────┘
                    │
          ┌─────────┼─────────┐
          │         │         │
          v         v         v
        CPU       Memory     Disk
          │         │         │
          └─────────┼─────────┘
                    │
                    v
                RESULT
                    │
          ┌─────────┼─────────┐
          v         v         v
        Arrow     Polars    pandas
```

The Senior Data Engineer asks:

```text
Where is the data?
Where does it get computed?
How much is scanned?
What is the physical plan?
Which operator is expensive?
Where are the copies?
How much memory is required?
Can temporary storage handle spills?
How many concurrent users/writers exist?
What is the persistence requirement?
Does the SQL dialect match production?
Does the single-node architecture meet the SLA?
```

That is the difference between:

```text
"knowing DuckDB syntax"
```

and:

```text
"engineering with DuckDB."
```

---

# 96. Final Topic Boundary — What Comes Next

This topic focused on DuckDB's **embedded analytical engine**.

The next topic moves deeper into:

```text
DuckDB
   ↓
querying files
   ↓
object storage / remote data
   ↓
file-based analytical workflows
```

Do not prematurely combine this topic with the full remote-storage architecture.

The current mastery goal is:

> Understand DuckDB as a serious single-node analytical engine and be able to reason about its SQL, execution, resource management, interoperability, concurrency boundaries, and production role.

---

# 97. Final Reference Notes

Current official DuckDB documentation used for API and architecture verification while preparing this chapter:

- Python client API: <https://duckdb.org/docs/current/clients/python/reference/>
- Python overview/result conversion: <https://duckdb.org/docs/current/clients/python/overview>
- pandas integration/replacement scans: <https://duckdb.org/docs/current/guides/python/import_pandas>
- Polars integration: <https://duckdb.org/docs/current/guides/python/polars>
- Relational Python API: <https://www.duckdb.org/docs/current/clients/python/relational_api>
- `EXPLAIN ANALYZE`: <https://duckdb.org/docs/current/guides/meta/explain_analyze>
- Configuration: <https://duckdb.org/docs/current/configuration/overview>
- Concurrency: <https://duckdb.org/docs/current/connect/concurrency>
- Transactions: <https://duckdb.org/docs/current/sql/statements/transactions>
- Extensions: <https://duckdb.org/docs/stable/extensions/overview>
- Parameterized-query/security guidance: <https://duckdb.org/docs/current/operations_manual/securing_duckdb/overview>
- `GROUP BY ALL`: <https://duckdb.org/docs/lts/sql/query_syntax/groupby>
- `SELECT * EXCLUDE` / `REPLACE`: <https://duckdb.org/docs/current/sql/expressions/star>
- `QUALIFY`: <https://duckdb.org/docs/current/sql/query_syntax/qualify>
- `ASOF JOIN`: <https://duckdb.org/docs/current/sql/query_syntax/from>
- `PIVOT`: <https://duckdb.org/docs/lts/sql/statements/pivot>
- `UNPIVOT`: <https://duckdb.org/docs/current/sql/statements/unpivot>
- Lists: <https://duckdb.org/docs/current/sql/data_types/list>
- Structs: <https://duckdb.org/docs/stable/sql/data_types/struct>

> **Version reminder:** DuckDB changes quickly. Before using version-sensitive syntax in production, check the installed DuckDB version and current official documentation.


---

# 98. Final Quality-Control Summary

This chapter intentionally covers the complete Topic 05 scope:

- database fundamentals
- DuckDB architecture
- in-process execution
- SQLite/PostgreSQL comparison
- Python API
- in-memory and persistent databases
- tables, views, CTAS
- result retrieval
- Python replacement scans
- pandas/Polars/Arrow interoperability
- columnar/vectorized/parallel execution
- optimizer and query plans
- analytical SQL extensions
- relational Python API
- parameterized queries and SQL injection prevention
- `EXPLAIN` and `EXPLAIN ANALYZE`
- memory/resource configuration
- out-of-core execution and spilling
- transactions and ACID
- concurrency boundaries
- extensions
- local development warehouse patterns
- test-double patterns
- SQL dialect portability
- hands-on warehouse project
- benchmarking discipline
- correctness validation
- debugging
- production architecture
- senior interview preparation
- practice problems and answer keys
- final mastery assessment and answer key
- teach-back exercise

The required scope is complete without turning later remote-storage, lakehouse, zero-copy, GPU, or distributed-system topics into separate deep chapters.
