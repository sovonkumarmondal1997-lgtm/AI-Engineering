# Topic 06 — Snowpark Python and UDFs

**Stage:** Stage 2C — Data Engineering_3  
**Module:** 2C.3 — Snowflake Deep Dive  
**Target path:** `Stage 2C — Data Engineering_3/03-Snowflake-Deep-Dive/06-snowpark-python-and-udfs.md`  
**Hands-on lab:** `experiments/06_snowpark/`

> **Syllabus rule:** This lesson follows Topic 06 of `roadmap-Snowflake-Deep-Dive.md`. It teaches Snowpark data engineering, programmability, testing, performance, and security. Snowpark ML, model registry, feature store, Pandas on Snowflake, and Snowpark Container Services are awareness topics here—not full courses.

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Explain the Snowpark architecture and distinguish client-side Python from work executed by Snowflake.
- Create and close a `Session`; read tables and build DataFrames with `select`, `filter`, `join`, `group_by`, and `with_column`.
- Explain lazy evaluation, SQL pushdown, generated-query inspection, and the costs of `collect()`, `show()`, and `to_pandas()`.
- Choose Snowpark, pandas, PySpark, or SQL for a workload.
- Create scalar UDFs, vectorized/batch UDFs, UDTFs, UDAFs, and Python stored procedures.
- Register packages and staged imports, understand the Anaconda package channel, and deploy code reproducibly.
- Explain owner’s-rights and caller’s-rights procedure behavior.
- Test pure Python logic and Snowpark DataFrame transformations locally, then validate Snowflake-specific behavior with integration tests.
- Schedule a stored procedure with a task and recognize how Snowpark code fits into dbt Python models.
- Design a fair scalar-versus-vectorized benchmark, reason about warehouse memory, and avoid unsupported performance claims.
- Apply least privilege, secrets, network rules, and external access integrations when code needs an external API.

## 2. Prerequisites and setup

You should already be comfortable with Python functions, modules, virtual environments, package management, SQL joins and aggregations, Snowflake tables and schemas, warehouses, roles, and basic cost control. You do not need to be an ML researcher to complete this lesson.

### 2.1 Local development environment

The roadmap recommends Python 3.12+ and a `uv` project. Snowflake’s local-testing framework has its own supported-version matrix, so check the current documentation and your chosen Snowpark package before pinning the runtime.

```bash
uv init snowpark-topic06
cd snowpark-topic06
uv python pin 3.12
uv add snowflake-snowpark-python snowflake-connector-python pandas
uv add --dev pytest
# Optional local DataFrame emulator; use a compatible Snowpark release.
uv add "snowflake-snowpark-python[localtest]"
```

For the `src/` layout used in this lesson, add this test configuration to `pyproject.toml` so `pytest` can import modules from `src/`:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

**What this does:** `uv` manages the local environment; `snowflake-snowpark-python` provides the DataFrame API; the connector is the transport/authentication layer used by Snowpark; `pandas` is needed for local examples and vectorized handlers; `pytest` runs tests. The `localtest` extra enables Snowflake’s local DataFrame testing framework (Snowpark Python 1.18.0 or later per current documentation; confirm the current supported Python/package matrix). Lock dependencies in `uv.lock` and review upgrades deliberately.

Do not assume a package installed in your local environment is automatically installed in Snowflake’s Python runtime. Local and server-side dependency environments are separate.

### 2.2 Connection configuration

Use environment variables, a supported authentication method, or a managed identity/key-pair configuration. Do not commit credentials or place passwords in a notebook, source file, or lesson example.

```python
# src/snowflake_session.py
import os
from snowflake.snowpark import Session


def create_session() -> Session:
    """Create a Snowpark session from externally supplied configuration."""
    required = ("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_ROLE",
                "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA")
    missing = [key for key in required if not os.environ.get(key)]
    if missing:
        raise RuntimeError(f"Missing required Snowflake settings: {', '.join(missing)}")

    connection_parameters = {
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "role": os.environ["SNOWFLAKE_ROLE"],
        "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
        "database": os.environ["SNOWFLAKE_DATABASE"],
        "schema": os.environ["SNOWFLAKE_SCHEMA"],
        # Use a supported authenticator, such as externalbrowser or key-pair auth,
        # according to your organization's identity policy.
        "authenticator": os.environ.get("SNOWFLAKE_AUTHENTICATOR", "externalbrowser"),
    }
    return Session.builder.configs(connection_parameters).create()
```

**Inputs/outputs:** reads non-secret connection settings from the environment and returns a live `Session`; authentication is handled by the configured Snowflake mechanism. **Privileges:** the role needs `USAGE` on the warehouse, database, and schema, plus the object privileges required by the operation. **Cleanup:** close the session in a `finally` block or context-managed application lifecycle. This example is intended for an interactive/local client, not as the body of a stored procedure (Snowflake supplies the procedure’s session).

Example caller:

```python
from snowflake_session import create_session

session = create_session()
try:
    session.sql("SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE() ").show()
finally:
    session.close()
```

This executes a query against Snowflake. It is not a local simulation. The role must be able to use the selected warehouse; no table privileges are needed for this metadata query beyond those required by the account configuration.

### 2.3 Safe lab conventions

Use a dedicated lab database and schema, a small warehouse with auto-suspend, a query tag such as `TOPIC06_SNOWPARK_LAB`, and a resource monitor/budget where available. Avoid running a 10-million-row benchmark until the small-data version works and cost expectations are understood. Replace example database/schema names with names you are authorized to create.

## 3. Architecture: where Python runs

Snowpark is a client library and API, not a separate compute engine that automatically runs all Python on your laptop. Most DataFrame transformations build a logical plan. Snowpark translates supported operations into SQL, submits work to Snowflake when an action requires results, and returns results or metadata to the client. A Python UDF or procedure is different: its handler executes in Snowflake-managed Python runtime, under the relevant function/procedure execution model.

```text
LOCAL PYTHON PROCESS                         SNOWFLAKE ACCOUNT
┌──────────────────────────┐                 ┌────────────────────────────┐
│ Python application       │                 │ Cloud services             │
│  Session / credentials   │  SQL / request  │ parse, optimize, authorize  │
│  DataFrame logical plan  ├────────────────►│ query planning              │
│  select/filter/join/...  │                 └─────────────┬──────────────┘
└─────────────┬────────────┘                               │ execution plan
              │ action: collect/show/write                  ▼
              │                                  ┌─────────────────────────┐
              │                                  │ Virtual warehouse        │
              │                                  │ scans / joins / groups   │
              │                                  │ SQL expressions          │
              │                                  └────────────┬────────────┘
              │                                               │
              │                                  ┌────────────▼────────────┐
              │                                  │ Python UDF / UDTF /     │
              │                                  │ procedure handler when  │
              │                                  │ explicitly invoked      │
              │                                  └────────────┬────────────┘
              ◄──────── rows / status / metadata ─────────────┘
```

The diagram is conceptual. Actual scheduling, exchanges, and execution details are controlled by Snowflake; do not infer a physical plan from the Python method chain alone.

### 3.1 Local code versus server-side work

| Operation | Where it primarily happens | Important caveat |
|---|---|---|
| Python imports, configuration, function calls building a DataFrame | Local client | A method chain is usually plan construction, not row processing. |
| `session.table(...)`, `select`, `filter`, `join`, `group_by`, `with_column` | Client builds a plan; Snowflake executes when triggered | Supported expressions are translated to SQL; not every arbitrary Python function is pushdown-compatible. |
| `df.collect()` | Snowflake computes; rows are transferred to client | Can transfer an unbounded amount of data if the plan is not bounded. |
| `df.show()` | Executes a query to display sample rows | Convenient for inspection; not a free local preview. |
| `df.to_pandas()` | Snowflake computes; result materializes as a local pandas DataFrame | The returned rows and columns consume local memory and network bandwidth. |
| Python UDF/UDTF/vectorized UDF | Snowflake-managed Python runtime | Adds Python-runtime and serialization overhead; performance depends on workload and implementation. |
| Python stored procedure | Snowflake-managed Python runtime | It receives a Snowpark `Session` from Snowflake and can orchestrate SQL/DataFrame operations. |
| Local testing framework | Local Python process | It emulates supported DataFrame behavior; it does not prove live-account permissions, SQL semantics, or warehouse performance. |

## 4. Beginner: DataFrames and lazy evaluation

### 4.1 Read a table and build a plan

```python
from snowflake.snowpark.functions import col, lower, trim, count, sum as sum_

raw = session.table("LAB_DB.RAW.EVENTS")
clean = (
    raw.filter(col("EVENT_ID").is_not_null())
       .with_column("EVENT_TYPE", lower(trim(col("EVENT_TYPE"))))
       .select("EVENT_ID", "USER_ID", "EVENT_TS", "EVENT_TYPE", "AMOUNT")
)
```

**Imports:** Snowpark’s `col`, `lower`, `trim`, and aggregation functions create Snowflake expressions; `sum` is aliased to `sum_` to avoid shadowing Python’s built-in. **Session:** uses the already configured `session`. **Privileges:** `USAGE` on the warehouse/database/schema and `SELECT` on the source table. **Input/output:** the input is `LAB_DB.RAW.EVENTS`; `clean` is a Snowpark DataFrame plan with normalized `EVENT_TYPE` and selected columns. **Execution:** the chained transformations normally do not fetch all rows immediately. **Cleanup:** close the session when the caller is finished.

This is not equivalent to calling Python’s built-in `lower()` on every row locally. The imported Snowpark functions build SQL expressions.

### 4.2 Core DataFrame operations

```python
from snowflake.snowpark.functions import col, lit, when, count, sum as sum_

# SELECT / FILTER
selected = session.table("LAB_DB.RAW.EVENTS").select(
    col("EVENT_ID"), col("USER_ID"), col("EVENT_TS"), col("AMOUNT")
)
recent = selected.filter(col("EVENT_TS") >= lit("2026-01-01"))

# JOIN
users = session.table("LAB_DB.RAW.USERS").select("USER_ID", "COUNTRY")
joined = recent.join(users, on="USER_ID", how="left")

# WITH_COLUMN
classified = joined.with_column(
    "AMOUNT_BAND",
    when(col("AMOUNT") >= 100, lit("HIGH")).otherwise(lit("NORMAL")),
)

# GROUP_BY / AGGREGATE
summary = classified.group_by("COUNTRY", "AMOUNT_BAND").agg(
    count("EVENT_ID").alias("EVENT_COUNT"),
    sum_("AMOUNT").alias("TOTAL_AMOUNT"),
)
```

**Behavior:** each method returns a DataFrame describing a transformation; `join` may increase rows if the join key is not unique on the right side, so check cardinality. `lit()` creates a literal expression. `when(...).otherwise(...)` is a SQL conditional expression. The last line is a grouped aggregate, not a Python loop. **Privileges:** read privileges on both input tables. **Execution:** an action such as `summary.show()` or `summary.write...` triggers work. **Cleanup:** session lifecycle belongs to the calling application.

### 4.3 Equivalent SQL and Snowpark

SQL:

```sql
SELECT COUNTRY, AMOUNT_BAND,
       COUNT(EVENT_ID) AS EVENT_COUNT,
       SUM(AMOUNT) AS TOTAL_AMOUNT
FROM (
  SELECT e.EVENT_ID, e.AMOUNT, u.COUNTRY,
         CASE WHEN e.AMOUNT >= 100 THEN 'HIGH' ELSE 'NORMAL' END AS AMOUNT_BAND
  FROM LAB_DB.RAW.EVENTS AS e
  LEFT JOIN LAB_DB.RAW.USERS AS u ON e.USER_ID = u.USER_ID
  WHERE e.EVENT_TS >= '2026-01-01'
) AS filtered_events
GROUP BY COUNTRY, AMOUNT_BAND;
```

Equivalent Snowpark construction:

```python
from snowflake.snowpark.functions import col, lit, when, count, sum as sum_

events = session.table("LAB_DB.RAW.EVENTS").filter(
    col("EVENT_TS") >= lit("2026-01-01")
)
users = session.table("LAB_DB.RAW.USERS")
result = (
    events.join(users, events["USER_ID"] == users["USER_ID"], how="left")
    .select(
        events["EVENT_ID"].alias("EVENT_ID"),
        events["AMOUNT"].alias("AMOUNT"),
        users["COUNTRY"].alias("COUNTRY"),
        when(events["AMOUNT"] >= 100, lit("HIGH"))
        .otherwise(lit("NORMAL")).alias("AMOUNT_BAND"),
    )
    .group_by("COUNTRY", "AMOUNT_BAND")
    .agg(count("EVENT_ID").alias("EVENT_COUNT"),
         sum_("AMOUNT").alias("TOTAL_AMOUNT"))
)
```

The examples express the same business transformation, assuming compatible column types and the same join multiplicity. The DataFrame API is useful when transformations are assembled in Python, reused, or parameterized. SQL may be clearer for SQL-native logic. Snowpark does not make SQL unnecessary.

### 4.4 Lazy evaluation and SQL pushdown

A DataFrame chain is generally lazy: Snowpark builds a plan and Snowflake evaluates it when an action needs the result. This lets the optimizer combine and reorder eligible operations. Filters, projections, joins, and aggregates expressed with supported Snowpark APIs are typically translated into SQL rather than run as a Python loop in the client. Lazy does not mean that no client-side work occurs: Python constructs the plan, and some operations may trigger metadata or query requests. An action can execute a query even if it returns only a small result.

Common actions include:

- `collect()` — returns all result rows as local `Row` objects.
- `show()` — executes a query and prints a bounded sample for inspection; do not use it as proof that the full dataset was processed in the same way as a production write.
- `to_pandas()` — materializes the result in local memory as pandas; use only when the result is intentionally small enough for the client.
- `count()` — executes a count query and returns the scalar count.
- `write.save_as_table(...)` — executes a write.

Avoid calling `collect()` simply to iterate over millions of rows in Python. Keep filtering, joins, aggregations, and expressions inside Snowflake whenever they can be represented in SQL.

#### Inspecting generated SQL

The roadmap asks you to inspect `df.queries`. Availability and exact contents depend on the Snowpark version and plan. Treat it as a diagnostic interface, not a guarantee that one particular SQL string will be generated.

```python
plan = session.table("LAB_DB.RAW.EVENTS").filter(col("EVENT_TYPE") == lit("purchase"))

# Inspect only if supported by the installed Snowpark version.
queries = getattr(plan, "queries", None)
if queries is None:
    print("This Snowpark version does not expose df.queries here; use query history/profile.")
else:
    print(queries)

# A real action executes the plan.
plan.limit(10).show()
```

This code prints the API’s reported query representation if available; it does **not** hard-code or invent a generated SQL string. For authoritative execution evidence, use Snowflake Query History and Query Profile after an actual action. The `limit(10)` bounds returned rows but does not guarantee a particular physical execution cost.

### 4.5 Writing results to a table

```python
# Writes the aggregate to a lab-owned table.
summary.write.mode("overwrite").save_as_table("LAB_DB.GOLD.EVENT_SUMMARY")
```

**Input/output:** a DataFrame plan becomes the contents of `LAB_DB.GOLD.EVENT_SUMMARY`. **Privileges:** appropriate `USAGE` privileges plus `CREATE TABLE` in the destination schema and write privileges on the target as required by the selected write mode. **Behavior:** `overwrite` replaces existing target contents/schema behavior according to the API and options; do not use it blindly on a production table. **Cleanup:** drop only lab objects that you own and no longer need.

For incremental production updates, design explicit merge/idempotency logic rather than assuming `append` or `overwrite` is always correct. For example, a full rebuild into a disposable gold table can be acceptable; a shared production table usually needs a controlled deployment and write strategy.

### 4.6 `collect()`, `show()`, and `to_pandas()` compared

| Method | Returns | Appropriate use | Risk |
|---|---|---|---|
| `collect()` | List of local Snowpark `Row` objects | Small bounded results or application logic that truly needs each row | Network transfer and client memory can grow with every row. |
| `show()` | Displays a sample; return value is not a result DataFrame | Debugging schemas and sample values | Executes work and can incur query/warehouse cost. |
| `to_pandas()` | Local pandas `DataFrame` | Deliberately small extracts or a workflow that needs pandas locally | Large results can exhaust client RAM and incur large transfer costs. |

`to_pandas()` is not “pandas running inside Snowflake.” It transfers results to the client. Snowpark has separate capabilities for server-side Python and pandas-oriented execution patterns; do not conflate them.

### 4.7 Snowpark versus pandas versus PySpark

| Dimension | Snowpark Python | pandas | PySpark |
|---|---|---|---|
| Main execution | Snowflake SQL engine for supported DataFrame plans; Python handlers for UDF/procedure code | In-process Python memory | Spark distributed execution engine |
| Data location | Usually stays in Snowflake until explicitly fetched | Local process memory unless backed by another integration | Cluster/storage environment connected to Spark |
| Best fit | Transforming Snowflake-resident data and invoking Snowflake-native capabilities | Small in-memory datasets, local analysis, test fixtures | Large distributed transformations across a Spark lakehouse/platform |
| Main risks | Poor SQL shape, unnecessary UDFs, excessive result materialization, warehouse cost | Memory limits and single-machine execution | Cluster operations, shuffles, infrastructure and platform complexity |
| Similarity | DataFrame-style API | DataFrame API | DataFrame API |
| Difference to remember | API syntax is not identical to pandas/PySpark; execution semantics differ | Many operations execute eagerly in local memory | Spark uses its own optimizer and distributed execution model |

Choose by data gravity, operational ownership, required libraries, governance, scale, and cost—not by syntax preference alone.

### 4.8 Useful functions from `snowflake.snowpark.functions`

Common SQL-expression builders include:

- Columns and literals: `col`, `lit`.
- String cleanup: `trim`, `lower`, `upper`, `length`, `regexp_replace`, `split`, `concat`, `coalesce`.
- Conditional/null logic: `when`, `iff`, `coalesce`, `is_null` patterns through column expressions.
- Aggregation: `count`, `sum`, `avg`, `min`, `max`, `count_distinct` (check the exact API spelling for your installed version).
- Date/time: `current_timestamp`, `date_trunc`, `datediff`, `to_date`.
- Windowing: `row_number`, `rank`, `lag`, `lead`, `sum`/`avg` over a `Window` specification.

These functions create expressions that Snowpark can translate into Snowflake SQL. Prefer them to Python callbacks when a native SQL expression expresses the same logic. Consult the API reference for signatures and version-specific details.

## 5. Intermediate: Python functions that execute in Snowflake

A UDF is a reusable function callable in SQL. A UDTF can emit zero, one, or many rows per input row. A UDAF maintains aggregation state across input rows. A stored procedure performs an operation or workflow and returns a result/status; it is not itself a row-wise expression. Vectorized UDFs process batches using pandas objects rather than calling a handler once per row.

| Object | Input | Output | Typical purpose |
|---|---|---|---|
| Scalar UDF | One row’s arguments per handler invocation (conceptually) | One scalar result | Specialized parsing or business logic not practical in SQL |
| Vectorized/batch UDF | A batch represented by pandas Series/DataFrame | One result per input row | Batch-oriented Python libraries and array operations |
| UDTF | Input row arguments | Zero or more output rows | Split/parse a field into a relation |
| UDAF | A group/partition of input values through aggregation callbacks | One aggregate result per group | Custom aggregation not adequately expressed by built-in SQL aggregates |
| Stored procedure | Explicit procedure arguments and a supplied Snowpark `Session` | One procedure return value/status | Multi-step orchestration, DDL/DML, controlled workflows |

### 5.1 Scalar UDF

```python
from snowflake.snowpark.functions import udf
from snowflake.snowpark.types import StringType


def normalize_event_type(value: str) -> str | None:
    if value is None:
        return None
    return value.strip().lower()

normalize_event_type_udf = udf(
    func=normalize_event_type,
    name="LAB_DB.GOLD.NORMALIZE_EVENT_TYPE",
    input_types=[StringType()],
    return_type=StringType(),
    is_permanent=False,
    replace=True,
    session=session,
)

session.table("LAB_DB.RAW.EVENTS").select(
    normalize_event_type_udf(col("EVENT_TYPE")).alias("EVENT_TYPE_NORMALIZED")
).limit(20).show()
```

**Imports/configuration:** `udf` registers the Python callable; `StringType` declares Snowflake input/output types; `session` is the live client session. **Input/output:** nullable string to nullable normalized string. **Privileges:** read access to the source and permission to create/use the temporary function in the current session/schema. For a permanent function, also configure a stage and package deployment as required and grant the relevant schema/function privileges. **Execution:** the `show()` action runs the query and invokes the UDF on matching rows. **Cleanup:** this is temporary (`is_permanent=False`) and scoped to the session; close the session. The name is illustrative and should be changed to an authorized lab schema.

Keep the handler deterministic and side-effect-free when possible. SQL `LOWER(TRIM(...))` can do this simple example more directly; this UDF is instructional, not a recommendation to use Python for basic string cleanup.

### 5.2 Vectorized (batch) UDF

Vectorized UDFs can reduce per-row Python invocation overhead for workloads that benefit from batch operations. They are not guaranteed to be faster: batch serialization, pandas allocation, batch size, warehouse memory, data skew, and the handler’s algorithm all matter.

```sql
CREATE FUNCTION LAB_DB.GOLD.NORMALIZE_EVENT_TYPE_BATCH(V STRING)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = 3.12
PACKAGES = ('pandas')
HANDLER = 'normalize_batch'
AS
$$
import pandas as pd
from _snowflake import vectorized

@vectorized(input=pd.DataFrame)
def normalize_batch(batch):
    values = batch[0].astype("string")
    normalized = values.str.strip().str.lower()
    return normalized.astype(object).where(batch[0].notna(), None)
$$;
```

Call it in SQL or from a Snowpark DataFrame after registration:

```python
from snowflake.snowpark.functions import call_udf, col

session.table("LAB_DB.RAW.EVENTS").select(
    call_udf("LAB_DB.GOLD.NORMALIZE_EVENT_TYPE_BATCH", col("EVENT_TYPE"))
    .alias("EVENT_TYPE_NORMALIZED")
).limit(20).show()
```

**Why SQL DDL here:** the `_snowflake.vectorized` decorator with a pandas `DataFrame` input is an explicit documented batch-UDF registration pattern. A one-argument UDF’s input is available as `batch[0]`; the output must have the same length as the input batch. **Inputs/outputs:** a batch of nullable strings becomes normalized strings with nulls preserved. **Privileges:** create/use function privileges and permission to use the declared pandas package/runtime. **Execution:** the handler runs in Snowflake’s Python runtime, not in the client process. **Cleanup:** drop the function after the lab if it is disposable. This example is documented-pattern guidance, not a claim of live execution.

### 5.3 Python UDTF: one messy string into multiple rows

A table function is appropriate when one input value can yield multiple output records. The example splits a delimited list, trims whitespace, drops empty tokens, and emits one row per token.

```python
from snowflake.snowpark.functions import udtf
from snowflake.snowpark.types import StringType, StructField, StructType

class SplitTags:
    def process(self, raw_value: str):
        if raw_value is None:
            return
        for token in raw_value.replace(";", ",").split(","):
            cleaned = token.strip()
            if cleaned:
                yield (cleaned.lower(),)

split_tags = udtf(
    SplitTags,
    output_schema=StructType([StructField("TAG", StringType())]),
    input_types=[StringType()],
    name="LAB_DB.GOLD.SPLIT_TAGS",
    is_permanent=False,
    replace=True,
    session=session,
)

source = session.create_dataframe(
    [["Snowflake, Python; SQL"], ["AI,, Data Engineering"], [None]],
    schema=["RAW_TAGS"],
)
source.join_table_function(split_tags(source["RAW_TAGS"])).show()
```

**Imports/configuration:** `udtf` registers a class with a `process` generator; `StructType` declares the table-shaped output. **Input/output:** a nullable string becomes zero or more rows containing `TAG`. Expected non-null example tokens are `snowflake`, `python`, `sql`, `ai`, `data engineering`. **Privileges:** temporary function creation/use and access to any source table if using a table rather than the inline fixture. **Execution:** the final `show()` executes the table function. **Cleanup:** the temporary function/session ends with the session.

The exact convenience API for joining a UDTF may vary by Snowpark release; verify the installed version’s `join_table_function` signature. The handler’s `process` semantics and output schema are the core contract. For production, define behavior for quotes, escaped delimiters, Unicode whitespace, token limits, and malformed values.

### 5.4 UDAF: custom aggregation state

Use a UDAF only when built-in SQL aggregates are insufficient. The aggregate class typically implements state initialization, per-row accumulation, state merging, and finalization. This conceptual example calculates a product across non-null numeric inputs; the actual registration API must match the installed Snowpark release and supported SQL types.

```python
from snowflake.snowpark.functions import udaf
from snowflake.snowpark.types import FloatType

class ProductUDAF:
    def __init__(self):
        self.product = 1.0
        self.seen_value = False

    @property
    def aggregate_state(self):
        return (self.product, self.seen_value)

    def accumulate(self, value):
        if value is not None:
            self.product *= float(value)
            self.seen_value = True

    def merge(self, other_state):
        other_product, other_seen = other_state
        if other_seen:
            self.product *= other_product
            self.seen_value = True

    def finish(self):
        return self.product if self.seen_value else None

product_udaf = udaf(
    ProductUDAF,
    name="LAB_DB.GOLD.PRODUCT_UDAF",
    return_type=FloatType(),
    input_types=[FloatType()],
    replace=False,
    session=session,
)

result = session.table("LAB_DB.RAW.EVENTS").agg(product_udaf(col("AMOUNT")))
result.show()
```

**Imports/configuration:** `udaf` registers the handler; `FloatType` declares the SQL type; `col` is imported in the calling module as in earlier examples. **Input/output:** aggregates non-null `AMOUNT` values into one floating-point result; all-null input returns `NULL`. **Privileges:** create/use function privileges and read access to the source table. **Execution:** the `show()` action invokes the UDAF. **Cleanup:** drop the UDAF after the lab if disposable. The `aggregate_state` property, `accumulate`, `merge`, and `finish` are required handler methods; the state must be serializable. A product aggregate can overflow/underflow and may not be numerically stable; it is a teaching example, not a recommended financial calculation. Prefer `SUM`, `AVG`, and other built-ins whenever possible.

### 5.5 Packages, Anaconda channel, and staged imports

Snowflake supports curated third-party packages from its Anaconda channel and also supports importing staged Python files. Package availability depends on the runtime and account configuration; check the package selector/documentation rather than assuming any PyPI package is available. For reproducibility, record package names and compatible versions, keep handler code small, and test deployment in the target account.

**Example: permanent scalar UDF with package declaration**

```python
from snowflake.snowpark.functions import udf
from snowflake.snowpark.types import FloatType

# The built-in math module is part of Python; no external package is required.
def safe_log(value: float) -> float | None:
    import math
    if value is None or value <= 0:
        return None
    return math.log(value)

safe_log_udf = udf(
    func=safe_log,
    name="LAB_DB.GOLD.SAFE_LOG",
    input_types=[FloatType()],
    return_type=FloatType(),
    is_permanent=True,
    stage_location="@LAB_DB.GOLD.CODE_STAGE",
    # Fail on a name collision; do not silently replace an existing object.
    replace=False,
    session=session,
)
```

**Requirements:** the named stage must exist and the active role must have the necessary stage/schema/function privileges. Permanent Python UDF registration uses a stage for deployment artifacts; this example has no third-party `packages` because `math` is in the standard library. **Input/output:** positive numeric value to natural logarithm, otherwise `NULL`. **Execution:** function registration creates a reusable database object; invoking it in SQL/DataFrame actions executes it. **Cleanup:** drop the function and stage only if they were created for this lab and are no longer needed.

For a third-party package, use `packages=[...]` with an account-supported package/version and the relevant Snowflake package policy/Anaconda configuration. Do not invent a version pin or assume `pip install` on the client deploys it to Snowflake.

**Example: importing a helper module from a stage (SQL deployment shape)**

```sql
-- Requires a stage and uploaded Python file owned by the lab.
CREATE FUNCTION LAB_DB.GOLD.CLEAN_CODE(V STRING)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = 3.12
HANDLER = 'clean_code'
IMPORTS = ('@LAB_DB.GOLD.CODE_STAGE/text_helpers.py')
AS
$$
from text_helpers import clean_code
$$;
```

This shows the staged-import pattern; `text_helpers.py` must exist at the exact stage path and define `clean_code`. The deployment role needs privileges to create the function and read the stage. Runtime versions and import paths must be verified against the account’s current supported versions. Treat this DDL as a deployment example: the staged file must be uploaded before creation, and a name collision should be resolved deliberately rather than by replacing an object. Cleanup should remove the function and staged file only after confirming nothing else uses them.

### 5.6 Python stored procedure for multi-step logic

A stored procedure is suited to a controlled workflow that performs several statements and returns status. It is not a replacement for declarative SQL transformations when one SQL query can do the job.

```python
from snowflake.snowpark.functions import col, lower, trim, coalesce, lit, count, sum as sum_
from snowflake.snowpark.types import StringType
from snowflake.snowpark.functions import sproc


def refresh_event_summary(session) -> str:
    source = session.table("LAB_DB.RAW.EVENTS")
    valid_events = source.filter(
        col("EVENT_ID").is_not_null() & (trim(col("EVENT_ID")) != lit(""))
    )
    summary = (
        valid_events
        .with_column("EVENT_TYPE", coalesce(lower(trim(col("EVENT_TYPE"))), lit("unknown")))
        .group_by("EVENT_TYPE")
        .agg(count("EVENT_ID").alias("EVENT_COUNT"),
             sum_("AMOUNT").alias("TOTAL_AMOUNT"))
    )
    summary.write.mode("overwrite").save_as_table("LAB_DB.GOLD.EVENT_SUMMARY")
    return "SUCCESS"

refresh_event_summary_proc = sproc(
    func=refresh_event_summary,
    name="LAB_DB.GOLD.REFRESH_EVENT_SUMMARY",
    return_type=StringType(),
    is_permanent=True,
    stage_location="@LAB_DB.GOLD.CODE_STAGE",
    packages=["snowflake-snowpark-python"],
    replace=False,
    session=session,
)

refresh_event_summary_proc()
```

**Prerequisite:** create `LAB_DB.GOLD.CODE_STAGE` as an internal named stage and ensure the deployment role can use it. Permanent registration uploads handler code/dependencies to the stage and creates a reusable procedure; a task cannot reliably call a session-scoped temporary procedure, so this example is permanent. **Imports/configuration:** `sproc` registers the Python handler; Snowflake supplies the procedure `session` argument. **Input/output:** no explicit input parameters; reads `LAB_DB.RAW.EVENTS`, overwrites `LAB_DB.GOLD.EVENT_SUMMARY`, and returns `SUCCESS`. **Privileges:** registration and execution require appropriate schema/function/stage privileges; execution rights determine table access. The current role must be able to read the source and create/overwrite the target, unless a deliberately configured rights model changes the effective access. **Execution:** the procedure’s DataFrame action writes the result; it runs in Snowflake-managed Python. **Cleanup:** drop the permanent procedure and lab output tables only after the task has been suspended and evidence retained.

For production, consider atomicity, failure handling, idempotency, schema evolution, and whether overwrite is safe. Do not assume a multi-step workflow is automatically an all-or-nothing transaction. Avoid dynamic SQL assembled from untrusted identifiers. In this lesson, the output table is disposable and fully rebuilt; never use this overwrite pattern on a shared production target without an explicit publication/recovery design.

### 5.7 Owner’s rights versus caller’s rights

- **Owner’s rights (the default for Snowflake stored procedures unless specified otherwise):** runs primarily with the procedure owner’s privileges. This can delegate a narrowly scoped operation without granting callers direct access to every underlying object. Use strict input validation and avoid turning a privileged procedure into a generic arbitrary-SQL endpoint.
- **Caller’s rights:** runs with the caller’s privileges and more directly reflects the caller’s session context. It is appropriate when the caller must use their own accessible objects/session state.
- A procedure cannot simultaneously be both owner’s-rights and caller’s-rights. The context and restrictions differ; test the real deployment role, not just the developer’s administrator role.

Illustrative SQL to declare rights explicitly:

```sql
CREATE PROCEDURE LAB_DB.GOLD.RETURN_STATUS()
RETURNS STRING
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
BEGIN
  RETURN 'CALLER_CONTEXT';
END;
$$;
```

This is a SQL procedure solely to demonstrate the `EXECUTE AS CALLER` clause; it is not a Python procedure example. The role needs create-procedure privileges in the schema and usage on relevant database/schema objects. It returns a string and performs no data access. Drop the procedure after the rights demonstration if it is disposable. Python procedures can similarly specify `EXECUTE AS OWNER` or `EXECUTE AS CALLER` in their SQL DDL; confirm the exact syntax generated by your deployment tool.

### 5.8 UDFs, tasks, and dbt Python models

A Snowflake task can call a stored procedure. A task provides scheduling/dependency orchestration; it does not change the procedure’s internal rights model.

```sql
CREATE TASK LAB_DB.GOLD.REFRESH_EVENT_SUMMARY_TASK
  WAREHOUSE = LAB_WH
  SCHEDULE = 'USING CRON 0 * * * * UTC'
AS
  CALL LAB_DB.GOLD.REFRESH_EVENT_SUMMARY();

-- Start scheduling only after confirming the target and permissions.
ALTER TASK LAB_DB.GOLD.REFRESH_EVENT_SUMMARY_TASK RESUME;
```

**Privileges:** create/manage task, use the warehouse, execute the procedure, and access referenced objects through the procedure’s rights model. A task created suspended should be reviewed before resume. **Input/output:** every hour, invokes the procedure; the gold table is updated according to the procedure. **Cleanup:** `ALTER TASK ... SUSPEND`, then drop the task if no longer needed. This schedule is illustrative; use the desired cadence and timezone explicitly.

**dbt Python models:** Snowpark Python models are supported on Snowflake and are executed through Snowflake’s Python/Snowpark environment. They require a compatible dbt adapter/runtime configuration and follow dbt’s model materialization and deployment rules. Use them when Python logic adds real value; use SQL models for ordinary relational transformations. Verify the supported dbt adapter versions and package rules in the current dbt/Snowflake docs before deploying. This lesson does not prescribe a full dbt setup.

### 5.9 Pandas on Snowflake, Snowpark ML, registry, feature store, and containers — awareness

- **Pandas on Snowflake:** a capability for pandas-oriented workflows that execute in Snowflake-managed infrastructure; distinct from downloading all data with `to_pandas()`. Confirm its current API, availability, and workload limitations before adoption.
- **Snowpark ML:** APIs for feature engineering and ML workflows close to Snowflake data. This is not a reason to force every model-training workload into Snowflake.
- **Model Registry:** stores model versions as governed Snowflake objects and supports inference workflows through supported interfaces. Model support, serving paths, and privileges depend on the model/runtime and account configuration.
- **Feature Store:** supports managing and serving feature definitions/values for ML workflows; learn its role in consistency and reuse rather than treating this lesson as a full feature-store course.
- **Snowpark Container Services:** runs containerized workloads in Snowflake-managed infrastructure for use cases needing custom environments or serving patterns beyond standard UDFs. It brings image, compute pool, security, and operational concerns; it is awareness-only here.

## 6. Advanced performance engineering

### 6.1 Keep relational work in SQL

Before writing Python, ask whether the transformation is a filter, join, group-by, window, cast, conditional, or built-in string/date operation. If yes, prefer native Snowpark expressions or SQL. Avoid `collect()` loops that fetch rows and issue one statement per row. Avoid UDFs for logic already handled well by native SQL.

### 6.2 Vectorized versus scalar UDFs

Vectorization may help when work is batch-friendly and pandas/NumPy operations reduce Python-level per-row overhead. It may not help for tiny datasets, trivial handlers, memory-heavy logic, or workloads dominated by warehouse scans and joins. Batch size and memory pressure matter. A memory-optimized warehouse may help when the Python workload is memory-constrained, but it costs differently; measure before changing size.

**Fair benchmark design for 10 million rows**

1. Generate or load one deterministic 10-million-row input table once; record schema, null distribution, value distribution, and generation method.
2. Implement identical semantics for scalar and vectorized handlers, including nulls and malformed values. Validate results before timing.
3. Compare against native SQL (`LOWER(TRIM(...))`) as a baseline when it expresses the same logic.
4. Use the same source table, selected columns, warehouse size, query tag, role, and comparable cache conditions. Record whether the result cache was used; do not mix cached and uncached runs without reporting it.
5. Run multiple trials, alternate execution order, report median and spread, and avoid drawing conclusions from one run.
6. Capture query ID, elapsed time, bytes scanned, partitions scanned, warehouse size, queue time, spills, and credits where available. Distinguish warehouse compute from client transfer time.
7. Keep output semantics and row counts identical; check nulls and edge cases. Do not time `to_pandas()` for one method and only server-side execution for another.
8. Start on a small scale and estimate cost before the 10-million-row run. Stop if the expected spend exceeds the lab budget.

No benchmark results are provided here because no live Snowflake account execution was performed for this lesson. Performance claims are hypotheses to test, not promised speedups.

### 6.3 Memory and batching

Vectorized handlers operate on batches, not necessarily the whole table at once. Do not assume the full 10 million rows fit in one pandas DataFrame. Minimize copies, select only needed columns, avoid retaining batches globally, and handle null/type conversion explicitly. Use a warehouse type/size supported for the workload and measure memory/spilling evidence; do not assume a memory-optimized warehouse automatically makes the code faster.

### 6.4 Profiling and observability

Use Query History, Query Profile, query tags, and task/procedure logs to answer:

- Did the plan scan too much data?
- Are joins multiplying rows unexpectedly?
- Is time spent queued, scanning, aggregating, transferring, or in Python execution?
- Does the query cache affect the measurement?
- Did the function’s package import or handler fail before query execution?

Do not publish raw credentials, sensitive rows, or secrets in query tags/logs. Tags should be stable and non-sensitive, such as `TOPIC06_BENCHMARK_SCALAR`.

## 7. Security: API access, secrets, and network rules

A Python UDF/procedure cannot simply make arbitrary network calls because a local Python environment can. External access must be explicitly configured by an authorized administrator. The usual pattern is:

1. Create a network rule for the permitted destination host/port.
2. Create a Snowflake secret holding the credential/token.
3. Create an external access integration that permits the network rule and secret.
4. Grant the required integration/secret privileges to the deployment role.
5. Reference the integration and secret in the UDF/procedure definition.
6. Retrieve the secret through the supported Snowflake secret API in the handler.
7. Log status and request IDs safely; enforce timeouts, rate limits, retries, and data minimization.

Illustrative configuration skeleton (administrator-owned; adapt to your provider and secret type):

```sql
-- Example only: restrict the host to a specific external API.
-- Create this dedicated schema first if it does not already exist and you are
-- authorized to create it; do not reuse an unrelated security schema.
CREATE SCHEMA LAB_DB.SECURITY;
CREATE NETWORK RULE LAB_DB.SECURITY.API_EGRESS_RULE
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('api.example.com:443');

-- The secret itself must be created using the correct secret type and secure credential source.
-- Do not substitute a literal API key in this script.
-- CREATE SECRET ...;

-- Run only after LAB_DB.SECURITY.API_TOKEN_SECRET has been created securely.
CREATE EXTERNAL ACCESS INTEGRATION LAB_API_ACCESS
  ALLOWED_NETWORK_RULES = (LAB_DB.SECURITY.API_EGRESS_RULE)
  ALLOWED_AUTHENTICATION_SECRETS = (LAB_DB.SECURITY.API_TOKEN_SECRET)
  ENABLED = TRUE;
```

**Inputs/outputs:** creates a narrowly scoped network rule and integration; the secret creation statement is intentionally omitted because the correct syntax depends on the authentication method. The integration statement will fail until the referenced secret exists. **Privileges:** administrative privileges to create network rules/integrations/secrets and grants such as usage on the integration and read on the secret for the deploying role. **Execution:** this DDL configures permission boundaries; it does not call the API. **Cleanup:** revoke grants, disable/drop integration, and drop lab secrets/rules when no longer needed, following organizational procedures.

For a handler, retrieve a generic secret through Snowflake’s supported API rather than reading a literal token from source. For example, the handler-side pattern is `token = _snowflake.get_generic_secret_string("api_token")`; the deployed function/procedure must map that alias to the secret and attach the integration. In Snowpark registration APIs, the relevant options are `secrets={"api_token": "LAB_DB.SECURITY.API_TOKEN_SECRET"}` and `external_access_integrations=["LAB_API_ACCESS"]`; SQL DDL uses `SECRETS = ('api_token' = LAB_DB.SECURITY.API_TOKEN_SECRET)` and `EXTERNAL_ACCESS_INTEGRATIONS = (LAB_API_ACCESS)`. These are configuration patterns, not a complete API client. Use `requests` only if the package is allowed and configured, and set explicit connect/read timeouts. The external host must match the network rule. Do not bypass the integration, embed credentials in source, or send PII to an external service without authorization, a lawful purpose, and data-processing approval. Handle non-2xx responses and rate limits. External calls can make retries non-idempotent; design idempotency keys where the external API supports them.

## 8. Local testing and integration testing

### 8.1 Separate pure business logic from Snowflake I/O

A testable boundary is a pure function that accepts values and returns values. DataFrame construction and Snowflake reads/writes live in separate functions. This lets `pytest` cover most edge cases without credentials, while a smaller integration suite proves that the target Snowflake account accepts the deployed objects and SQL.

```python
# src/event_rules.py

def normalize_event_type(value: str | None) -> str | None:
    if value is None:
        return None
    result = value.strip().lower()
    return result or None


def is_valid_event(event_id: str | None, amount: float | None) -> bool:
    return event_id is not None and event_id.strip() != "" and amount is not None and amount >= 0
```

No Snowpark import is needed; this is pure Python and runs locally. It takes strings/numbers and returns normalized values/boolean. No Snowflake privileges or session are needed. Cleanup is not applicable.

```python
# tests/test_event_rules.py
import pytest
from event_rules import normalize_event_type, is_valid_event

@pytest.mark.parametrize(
    ("value", "expected"),
    [(" Purchase ", "purchase"), ("", None), ("  ", None), (None, None)],
)
def test_normalize_event_type(value, expected):
    assert normalize_event_type(value) == expected

@pytest.mark.parametrize(
    ("event_id", "amount", "expected"),
    [("e1", 0.0, True), ("e2", 2.5, True), ("", 2.0, False), ("e3", -1, False), (None, 1, False)],
)
def test_is_valid_event(event_id, amount, expected):
    assert is_valid_event(event_id, amount) is expected
```

Run with `uv run pytest`. These tests validate only the pure Python rules, not Snowflake type coercion or UDF deployment.

### 8.2 Snowpark local testing framework

Snowflake provides a local testing framework that emulates supported Snowpark DataFrame operations without connecting to an account. The current documentation requires a compatible Snowpark version and optional `localtest` dependency; confirm exact requirements for your version. The framework does not support every operation—`Session.sql(...)` is not generally supported in local mode, so favor DataFrame APIs or mock SQL responses in tests. Current documentation specifies Snowpark Python 1.18.0 or later for the local testing framework; validate the actual dependency lock and supported Python version before relying on it in CI.

```python
# tests/test_snowpark_local.py
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, lower, trim


def test_normalization_dataframe():
    session = Session.builder.config("local_testing", True).create()
    try:
        df = session.create_dataframe(
            [[1, " Purchase "], [2, "REFUND"], [3, None]],
            schema=["EVENT_ID", "EVENT_TYPE"],
        )
        actual = (
            df.with_column("EVENT_TYPE", lower(trim(col("EVENT_TYPE"))))
              .sort("EVENT_ID")
              .collect()
        )
        assert [row["EVENT_TYPE"] for row in actual] == ["purchase", "refund", None]
    finally:
        session.close()
```

**Inputs/outputs:** in-memory fixture rows to locally emulated DataFrame rows. **Privileges:** none for a purely local test. **Execution:** this uses the local emulator, not Snowflake. **Cleanup:** closes the local session. If an operation is unsupported by the emulator, either simplify the test boundary or test it in an integration test against a dedicated Snowflake schema.

### 8.3 Integration tests

Use a separate test schema and small deterministic fixtures. Verify the deployed UDF/UDTF/procedure output, privileges, package availability, SQL semantics, task behavior, and cleanup. Do not let tests overwrite production tables. For external APIs, use a mock server or a non-production credential and a strict network allowlist. Integration tests cost credits and should be tagged/monitored.

## 9. Required hands-on lab — `experiments/06_snowpark/`

### 9.1 Deliverable layout

Create these files in the existing project’s `experiments/06_snowpark/` folder (or equivalent path in the repo):

```text
experiments/06_snowpark/
├── README.md
├── requirements.md
├── sql/
│   ├── 01_setup.sql
│   ├── 02_test_data.sql
│   ├── 03_task.sql
│   └── 99_cleanup.sql
├── src/
│   ├── session_config.py
│   ├── pipeline.py
│   ├── handlers.py
│   └── procedures.py
└── tests/
    ├── test_event_rules.py
    ├── test_snowpark_local.py
    └── test_snowflake_integration.py
```

This is the lab layout to create, not a claim that these files already exist.

### 9.2 Setup SQL and sample data

```sql
-- 01_setup.sql — run once with an authorized lab role in a fresh disposable namespace.
-- If any database/warehouse names already exist, STOP and choose new names;
-- these statements intentionally fail rather than replacing existing objects.
CREATE DATABASE LAB_DB;
CREATE SCHEMA LAB_DB.RAW;
CREATE SCHEMA LAB_DB.GOLD;
CREATE STAGE LAB_DB.GOLD.CODE_STAGE;

CREATE WAREHOUSE LAB_WH
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

CREATE TABLE LAB_DB.RAW.EVENTS (
  EVENT_ID STRING,
  USER_ID STRING,
  EVENT_TS TIMESTAMP_NTZ,
  EVENT_TYPE STRING,
  AMOUNT NUMBER(12,2),
  TAGS STRING
);
```

```sql
-- 02_test_data.sql — deterministic, small fixture.
INSERT INTO LAB_DB.RAW.EVENTS VALUES
  ('e1','u1','2026-01-01 10:00:00',' Purchase ',25.00,'Snowflake, Python'),
  ('e2','u1','2026-01-01 11:00:00','PURCHASE',75.00,'SQL; Data Engineering'),
  ('e3','u2','2026-01-02 09:00:00',' refund ',10.00,'Python,,AI'),
  ('e4','u2','2026-01-03 12:00:00',NULL,0.00,NULL),
  (NULL,'u3','2026-01-03 13:00:00','purchase',5.00,'invalid event id');
```

Run `02_test_data.sql` once against this freshly created fixture. Do not rerun the inserts without first resetting this disposable lab table, or rows will be duplicated. **Expected result:** the pipeline below excludes rows with missing/blank `EVENT_ID`, normalizes event type, maps missing type to `unknown`, and aggregates by event type. `purchase` should include `e1` and `e2` (count 2, sum 100.00), `refund` should include `e3` (count 1, sum 10.00), and `unknown` should include `e4` (count 1, sum 0.00). Validate the actual sums and counts with SQL before proceeding.

### 9.3 Pipeline: clean, aggregate, and write gold

```python
# src/pipeline.py
from snowflake.snowpark import Session, DataFrame
from snowflake.snowpark.functions import col, lower, trim, coalesce, lit, count, sum as sum_


def build_event_summary(session: Session) -> DataFrame:
    events = session.table("LAB_DB.RAW.EVENTS")
    clean = (
        events.filter(col("EVENT_ID").is_not_null() & (trim(col("EVENT_ID")) != lit("")))
        .with_column("EVENT_TYPE", coalesce(lower(trim(col("EVENT_TYPE"))), lit("unknown")))
        .select("EVENT_ID", "EVENT_TYPE", "AMOUNT")
    )
    return clean.group_by("EVENT_TYPE").agg(
        count("EVENT_ID").alias("EVENT_COUNT"),
        sum_("AMOUNT").alias("TOTAL_AMOUNT"),
    )


def write_event_summary(session: Session) -> str:
    summary = build_event_summary(session)
    summary.write.mode("overwrite").save_as_table("LAB_DB.GOLD.EVENT_SUMMARY")
    return "SUCCESS"
```

**Imports:** typed `Session`/`DataFrame` and Snowpark SQL expressions. **Inputs/outputs:** source table to aggregate DataFrame; writer stores `LAB_DB.GOLD.EVENT_SUMMARY` and returns status. **Privileges:** source `SELECT`, destination schema usage/create and target write privileges. **Execution:** `build_event_summary` builds a lazy plan; the write triggers execution. **Cleanup:** drop the gold table only after validating and saving any evidence you need.

For production, consider writing to a versioned/staging table and swapping/publishing only after validation rather than blindly overwriting a shared gold table. Add deterministic handling for invalid amounts and duplicates based on business requirements.

### 9.4 Rewrite one SQL transformation and inspect the plan

First run the SQL version:

```sql
SELECT LOWER(TRIM(EVENT_TYPE)) AS EVENT_TYPE, COUNT(*) AS N
FROM LAB_DB.RAW.EVENTS
WHERE EVENT_ID IS NOT NULL
GROUP BY LOWER(TRIM(EVENT_TYPE));
```

Then express it with Snowpark:

```python
from snowflake.snowpark.functions import col, lower, trim, count

df = (
    session.table("LAB_DB.RAW.EVENTS")
    .filter(col("EVENT_ID").is_not_null())
    .group_by(lower(trim(col("EVENT_TYPE"))).alias("EVENT_TYPE"))
    .agg(count("*").alias("N"))
)
queries = getattr(df, "queries", None)
print(queries if queries is not None else "Inspect Query History/Profile after df.show().")
df.show()
```

Check the results against SQL, remembering that SQL grouping places `NULL` into its own group and the example SQL does not filter blank IDs. The purpose is to compare semantics and generated query evidence, not to assume a fixed generated SQL string.

### 9.5 Scalar and vectorized UDF benchmark

Use the scalar and vectorized handlers from Sections 5.1 and 5.2. Register them with unique names in the lab schema. Compare both against native SQL for the same normalization rule. Validate row counts, null handling, and normalized output before timing.

The roadmap proposes 10 million rows. Do not start there automatically. Generate a small fixture, validate equivalence, estimate warehouse usage, then run the full benchmark only with explicit budget approval. Record query IDs, warehouse size, elapsed time, cache conditions, scanned bytes/partitions, spills, and credits. Compare server-side execution boundaries consistently: do not include client `to_pandas()` transfer time for one version while excluding it for another. Separate compile/setup time from execution where the question requires it, repeat trials, report medians and variability, and compare correctness before speed. No results should be entered until measured in your own account.

### 9.6 UDTF parsing exercise

Use `SplitTags` from Section 5.3 against the `TAGS` column. Expected tokens for `e1` include `snowflake` and `python`; `e2` includes `sql` and `data engineering`; `e3` includes `python` and `ai`. Decide whether empty tokens, duplicate tags, case folding, and `NULL` input should be retained or discarded. Assert the contract with tests.

### 9.7 Wrap the pipeline in a Python stored procedure

Deploy a permanent procedure using the same logic as `write_event_summary`, with a named internal stage such as `LAB_DB.GOLD.CODE_STAGE` created first. Permanent procedure registration requires the account’s supported package/runtime configuration and privileges; a deployment can use Snowpark’s `sproc` registration with `is_permanent=True`, `stage_location`, and package settings or SQL DDL generated by an approved deployment tool. A session-scoped temporary procedure is not appropriate for a task that runs in a separate session. Keep handler dependencies minimal.

Example call and schedule:

```sql
CALL LAB_DB.GOLD.REFRESH_EVENT_SUMMARY();

CREATE TASK LAB_DB.GOLD.REFRESH_EVENT_SUMMARY_TASK
  WAREHOUSE = LAB_WH
  SCHEDULE = 'USING CRON 0 * * * * UTC'
AS
  CALL LAB_DB.GOLD.REFRESH_EVENT_SUMMARY();

-- Inspect definition/permissions before resuming.
ALTER TASK LAB_DB.GOLD.REFRESH_EVENT_SUMMARY_TASK RESUME;
```

**Privileges:** procedure creation and execution, task create/operate, warehouse usage, and table/schema access through the configured rights model. **Input/output:** task runs the procedure hourly and refreshes the gold aggregate. **Behavior:** tasks run asynchronously; verify completion through task history and table results. **Cleanup:** suspend task first, then drop task/procedure and lab tables/warehouse/database if disposable. Never drop a shared database or warehouse.

### 9.8 Unit tests

At minimum, test:

- `NULL`, empty strings, whitespace, mixed case, and malformed delimiters.
- Zero and negative amounts, missing event IDs, duplicate IDs, and null timestamps.
- Expected aggregate counts and sums.
- UDTF output cardinality and order if order is part of the contract.
- Scalar and vectorized UDF semantic equivalence on the same fixture.
- Local DataFrame transformations using the local testing framework.
- Integration behavior against the deployed Snowflake function/procedure and role permissions.

Example equivalence test for pure handlers:

```python
import pandas as pd
from event_rules import normalize_event_type


def normalize_batch(values: pd.Series) -> pd.Series:
    normalized = values.astype("string").str.strip().str.lower()
    return normalized.astype(object).where(values.notna(), None)


def test_scalar_and_batch_equivalence():
    values = [" Purchase ", "REFUND", None, "", "  "]
    expected = [normalize_event_type(v) for v in values]
    actual = normalize_batch(pd.Series(values)).tolist()
    assert actual == expected
```

This test runs locally and does not benchmark Snowflake. It verifies business semantics only.

### 9.9 Cleanup SQL

```sql
-- 99_cleanup.sql — execute only in the disposable lab environment after verifying ownership.
ALTER TASK IF EXISTS LAB_DB.GOLD.REFRESH_EVENT_SUMMARY_TASK SUSPEND;
DROP TASK IF EXISTS LAB_DB.GOLD.REFRESH_EVENT_SUMMARY_TASK;
DROP PROCEDURE IF EXISTS LAB_DB.GOLD.REFRESH_EVENT_SUMMARY();
DROP FUNCTION IF EXISTS LAB_DB.GOLD.NORMALIZE_EVENT_TYPE(STRING);
DROP FUNCTION IF EXISTS LAB_DB.GOLD.NORMALIZE_EVENT_TYPE_BATCH(STRING);
DROP FUNCTION IF EXISTS LAB_DB.GOLD.SPLIT_TAGS(STRING);
DROP FUNCTION IF EXISTS LAB_DB.GOLD.SAFE_LOG(FLOAT);
DROP FUNCTION IF EXISTS LAB_DB.GOLD.CLEAN_CODE(STRING);
DROP AGGREGATE FUNCTION IF EXISTS LAB_DB.GOLD.PRODUCT_UDAF(FLOAT);
DROP PROCEDURE IF EXISTS LAB_DB.GOLD.RETURN_STATUS();
DROP TABLE IF EXISTS LAB_DB.GOLD.EVENT_SUMMARY;
DROP TABLE IF EXISTS LAB_DB.RAW.EVENTS;
-- Drop stage/warehouse/database only if created solely for this lab and unused.
-- DROP STAGE IF EXISTS LAB_DB.GOLD.CODE_STAGE;
-- Drop the database last; it removes remaining lab-owned objects.
-- DROP WAREHOUSE IF EXISTS LAB_WH;
-- DROP DATABASE IF EXISTS LAB_DB;
```

Check actual signatures before dropping overloaded functions/procedures. The cleanup script is a checklist, not a substitute for reviewing object ownership/dependencies.

### 9.10 Troubleshooting

| Symptom | Likely cause | Response |
|---|---|---|
| Authentication/session creation fails | Wrong account identifier, unsupported authenticator, missing environment setting | Verify account/auth method and environment; never paste credentials into source. |
| `SELECT`/`CREATE` privilege error | Role lacks object/schema/warehouse privileges | Use least-privilege grants; do not switch to `ACCOUNTADMIN` as a routine fix. |
| Package cannot be resolved | Package not in supported Anaconda channel, blocked by package policy, or runtime mismatch | Check package selector/runtime support and account package policy. |
| Staged import fails | Wrong stage path, file absent, wrong handler name, or missing stage privileges | `LIST` the stage, verify the file/module and exact handler name. |
| Vectorized UDF returns mismatched results | Null conversion, output length/order mismatch, incompatible handler signature | Test edge cases and verify the deployed API form/version. |
| `df.queries` missing | API/version does not expose it in that context | Inspect Query History/Profile after an actual action. |
| Local test fails on `Session.sql` | Local emulator limitation | Test DataFrame operations locally; mock SQL or use an integration test for SQL. |
| Task does not run | Task suspended, schedule not reached, warehouse/role/procedure privilege issue | Inspect task state/history and procedure errors; verify privileges and schedule. |
| Benchmark results vary | Cache, warehouse state/size, concurrency, data distribution, query compilation, or measurement boundaries differ | Record conditions, repeat trials, compare medians and query profiles. |
| Unexpected aggregate counts | Join fan-out, null semantics, duplicates, blank identifiers, or filter mismatch | Compare input/output row counts and make business rules explicit. |

## 10. Common mistakes and better practices

1. **Calling `to_pandas()` on a huge result.** Filter/aggregate in Snowflake first; only transfer a bounded result intentionally.
2. **Using Python for simple SQL work.** Prefer native expressions for joins, casts, filters, aggregates, and common string/date operations.
3. **Assuming every DataFrame method runs immediately.** Most build a plan; actions trigger execution.
4. **Treating `show()` as free.** It may execute a warehouse query.
5. **Forgetting package dependencies.** Declare packages/imports and verify account/runtime support.
6. **Assuming local packages equal server packages.** Local environment and Snowflake runtime are separate.
7. **Using a scalar UDF for a batch-friendly operation without measurement.** Compare SQL, scalar, and vectorized alternatives under equivalent conditions.
8. **Assuming vectorized always wins.** Memory, serialization, batch size, and handler logic can dominate.
9. **Putting secrets in code or logs.** Use Snowflake secrets and tightly scoped external access integrations.
10. **Overprivileged stored procedures.** Choose rights deliberately, validate inputs, and keep privileged operations narrow.
11. **Using overwrite casually.** Protect production targets with staged writes, validation, and controlled publication.
12. **Confusing local testing with integration testing.** Emulator tests do not prove deployment, privileges, package resolution, task scheduling, or real query plans.
13. **Benchmarking without controlling cache and workload.** Record conditions and repeat runs.
14. **Ignoring task lifecycle/cost.** Tasks execute asynchronously; inspect history and suspend/drop disposable tasks.
15. **Building a UDF when a UDTF is required (or vice versa).** Scalar UDF returns one value; UDTF returns a relation; UDAF aggregates; a procedure orchestrates.

## 11. Practice questions with answers

### Q1. What does a Snowpark DataFrame represent?
**Answer:** A logical description of a query/transformation. Most DataFrame operations do not immediately retrieve rows; an action causes Snowflake to execute the plan.

### Q2. Why can Snowpark reduce data movement compared with pandas?
**Answer:** Supported operations can execute in Snowflake next to the stored data. pandas usually operates on data materialized in local memory unless another execution integration is used.

### Q3. When would `collect()` be appropriate?
**Answer:** For a deliberately small result that the Python application needs. For large results, keep computation in Snowflake and avoid pulling all rows to the client.

### Q4. What is the key difference between a scalar UDF and a UDTF?
**Answer:** A scalar UDF returns one scalar result per input row; a UDTF can return zero or more output rows per input row.

### Q5. What does a UDAF provide?
**Answer:** A custom aggregation implemented with state accumulation, merge, and finalization behavior. Built-in SQL aggregates should be preferred when sufficient.

### Q6. Why might a vectorized UDF be faster?
**Answer:** Batch operations can reduce per-row Python overhead and exploit vectorized libraries. The outcome depends on batch size, data, memory, serialization, and handler implementation and must be measured.

### Q7. Why is `df.queries` not sufficient proof of runtime behavior?
**Answer:** It is a diagnostic representation whose availability/content can vary by version and plan. Query History/Profile after an actual action provides execution evidence.

### Q8. What is the difference between a stored procedure and a UDF?
**Answer:** A UDF is called as an expression and returns a scalar or table-shaped result; a stored procedure runs a controlled operation/workflow and may perform multi-step SQL/DataFrame work.

### Q9. How do owner’s rights and caller’s rights differ?
**Answer:** Owner’s-rights procedures run primarily with owner privileges; caller’s-rights procedures run with caller privileges/context. Select intentionally and grant access narrowly.

### Q10. Does `pip install` locally install a dependency for a permanent UDF?
**Answer:** No. Server-side packages must be declared through Snowflake’s supported package/import mechanism and be available under the target runtime/account policy.

### Q11. What does the local testing framework prove?
**Answer:** It can test supported Snowpark DataFrame transformations locally. It does not prove live SQL semantics, permissions, package deployment, warehouse performance, task execution, or external access configuration.

### Q12. What must be configured before a UDF can call an external API?
**Answer:** A network rule, secret, external access integration, appropriate grants, and references to the integration/secret in the function/procedure definition; the handler must use supported secret APIs and comply with the allowlist.

### Q13. When should SQL be preferred over Snowpark Python?
**Answer:** When the operation is naturally relational and can be expressed clearly and efficiently in SQL. Snowpark is valuable for Python composition and server-side custom logic, not for replacing SQL by default.

### Q14. What makes a scalar/vectorized benchmark fair?
**Answer:** Equivalent semantics and input data, same warehouse and query conditions, controlled cache/concurrency, multiple trials, recorded query IDs and cost/performance evidence, and clear boundaries for client transfer versus server execution.

### Q15. How should a Snowpark procedure be scheduled?
**Answer:** Create a Snowflake task that calls the procedure, grant least-privilege task/warehouse/procedure access, resume it only after reviewing the target and schedule, then monitor history and suspend/drop it when no longer required.

## 12. Topic 06 checkpoint

You are ready to move on when you can do these without copying the lesson:

- [ ] Explain how Snowpark executes: lazy plan construction, SQL pushdown where supported, and action-triggered execution.
- [ ] Create a `Session`, read a table, use `select`, `filter`, `join`, `group_by`, and `with_column`, and write a result table.
- [ ] Explain `collect()`, `show()`, and `to_pandas()` costs and choose an appropriate result boundary.
- [ ] Compare Snowpark, pandas, and PySpark based on execution and data location.
- [ ] Implement or explain scalar UDFs, vectorized/batch UDFs, UDTFs, UDAFs, and stored procedures.
- [ ] Register code with supported packages/imports and verify runtime/package compatibility.
- [ ] Explain owner’s-rights versus caller’s-rights procedure behavior.
- [ ] Run pure Python unit tests, local DataFrame tests, and a small live integration test.
- [ ] Build and monitor a task that invokes a Snowpark stored procedure.
- [ ] Benchmark scalar versus vectorized implementations without inventing results or ignoring cache/cost.
- [ ] Explain external access integrations, secrets, and network rules at a design level.
- [ ] Choose SQL, Snowpark, or external Spark based on data gravity, libraries, operations, and cost.

## 13. Official references

Use the current documentation for the Snowpark/Python version deployed in your account; signatures and package/runtime support can change.

- [Snowpark Python Developer Guide](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)
- [Snowpark DataFrames](https://docs.snowflake.com/en/developer-guide/snowpark/python/working-with-dataframes)
- [Creating Python UDFs](https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-introduction)
- [Python UDF handler examples](https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-examples)
- [Vectorized Python UDFs / batch API](https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-batch)
- [Python UDTFs](https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-tabular-functions)
- [Python UDAFs](https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-aggregate-functions)
- [Creating Snowpark stored procedures](https://docs.snowflake.com/en/developer-guide/snowpark/python/creating-sprocs)
- [Caller’s rights and owner’s rights](https://docs.snowflake.com/en/developer-guide/stored-procedure/stored-procedures-rights)
- [Local testing framework](https://docs.snowflake.com/en/developer-guide/snowpark/python/testing-locally)
- [Writing tests for Snowpark Python](https://docs.snowflake.com/en/developer-guide/snowpark/python/testing-python-snowpark)
- [External network access overview](https://docs.snowflake.com/en/developer-guide/external-network-access/external-network-access-overview)
- [Creating and using external access integrations](https://docs.snowflake.com/en/developer-guide/external-network-access/creating-using-external-network-access)
- [Python secret API](https://docs.snowflake.com/en/developer-guide/external-network-access/secret-api-reference)
- [Snowflake Model Registry overview](https://docs.snowflake.com/en/developer-guide/snowflake-ml/model-registry/overview)

---

**Source-of-truth note:** The syllabus, learning order, required lab, checkpoint, and common mistakes follow Topic 06 of `roadmap-Snowflake-Deep-Dive.md`; the target path is confirmed by `Roadmap_ptree.md`. API details should be checked against the current Snowflake documentation for the deployed Snowpark release.
