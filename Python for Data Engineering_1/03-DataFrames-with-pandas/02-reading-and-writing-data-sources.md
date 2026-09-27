# Topic 02 — Reading and Writing Data Sources

> **Stage 2 — Python for Data Engineering**  
> **Module 2.3 — DataFrames with pandas**  
> **Topic 02 — Reading and writing data sources**

## Central learning question

> **How do I read external data into pandas without silently changing its meaning, schema, identifiers, timestamps, or missing values—and how do I write it back reliably?**

A production ingestion step is not just:

```python
df = pd.read_csv("orders.csv")
```

It is a contract:

```text
SOURCE
  ↓
FORMAT IDENTIFICATION
  ↓
READER / PARSER CONFIGURATION
  ↓
EXPLICIT SCHEMA
  ↓
MISSING-VALUE POLICY
  ↓
IDENTIFIER + TIMESTAMP PRESERVATION
  ↓
MALFORMED-INPUT POLICY
  ↓
VALIDATED DATAFRAME
  ↓
TRANSFORMATION
  ↓
EXPLICIT OUTPUT SCHEMA
  ↓
RELIABLE WRITE
  ↓
ROUND-TRIP VERIFICATION
```

This chapter teaches pandas I/O from first principles through production-oriented ingestion decisions.

## Learning outcomes

By the end of this topic, you should be able to:

- read and write CSV, JSON Lines, Parquet, Excel, and SQL sources;
- configure delimiters, headers, column names, encodings, compression, and selected columns;
- prevent identifiers such as ZIP codes and order IDs from losing leading zeros;
- parse dates deterministically when a source format is known;
- define source-specific missing-value tokens without silently changing legitimate strings;
- handle malformed input deliberately and account for skipped records;
- understand why CSV and Parquet have different schema and analytical characteristics;
- use `read_parquet()` column pruning and filters appropriately;
- understand `engine="pyarrow"` and `dtype_backend`;
- combine multiple input files with deterministic ordering and schema validation;
- write stable output schemas and use temporary-path finalization patterns;
- prove important write/read round trips with `pd.testing.assert_frame_equal()`;
- measure I/O runtime and memory instead of assuming an optimization is beneficial;
- build a reusable reader contract for production pipelines.

The roadmap targets **pandas 3.x** as the primary behavior model. Where an important historical behavior matters, this chapter calls it out rather than teaching legacy behavior as current.

# 1. Introduction — Why I/O Is a Data Engineering Problem

A DataFrame exists in memory. Production data usually does not.

Your input may be:

- a CSV exported by a vendor;
- a JSON Lines response from an API;
- a Parquet dataset in object storage;
- an Excel workbook maintained by an operations team;
- a relational database table;
- a compressed file;
- dozens of daily files matching a naming pattern.

The moment data crosses that boundary, representation becomes part of correctness.

Consider an order identifier:

```text
001234
```

If the source field is an identifier and the reader interprets it as an integer, the value may become:

```text
1234
```

The numeric magnitude is unchanged, but the **identifier is corrupted** because `"001234"` and `"1234"` can represent different business identifiers.

The same issue appears with:

```text
ZIP code:      00123
Customer ID:   00008421
Product code:  07-001
Account code:  000019
```

The fundamental distinction is:

```text
numeric measurement
    → quantity used in arithmetic

identifier
    → label used to identify an entity
```

They may both contain digits, but they have different semantics.

## Another source of silent corruption: dates

Consider:

```text
01/02/2026
```

Depending on the source convention, that may mean January 2 or February 1.

A production pipeline should not ask a parser to guess when the source contract already tells you the format.

## Another source of silent change: missing-value tokens

Suppose a source contains:

```text
status
NA
ACTIVE
UNKNOWN
```

If `"NA"` is a legitimate status code, turning it into a missing value changes the meaning of the record.

Therefore:

> **Parsing is part of the data contract.**

## Two failure classes

### Semantic corruption

The pipeline runs successfully but changes meaning.

```text
"001234"
   ↓
1234
```

or:

```text
"NA"
   ↓
missing
```

or:

```text
01/02/2026
   ↓
wrong calendar date
```

### Operational failure

The pipeline cannot safely process the input.

Examples:

- wrong encoding;
- malformed rows;
- truncated file;
- unexpected columns;
- missing required columns;
- schema drift;
- connection failure;
- excessive memory use.

A good ingestion layer makes both classes visible.

## A production principle

> **Read data according to an explicit contract whenever correctness matters.**

# 2. Data Formats — Big Picture

Different formats make different trade-offs.

| Property | CSV | JSON Lines | Parquet | Excel | SQL table |
|---|---|---|---|---|---|
| Representation | text | record-oriented text | columnar binary | workbook/document | database-managed |
| Human-readable | yes | yes | no | yes | through SQL tools |
| Explicit analytical schema | weak | application-dependent | strong | workbook-dependent | database schema |
| Typical use | interchange/export | APIs/logs/events | analytics/data lake | business workflows | operational/analytical databases |
| Column pruning | limited | limited | strong when supported | sheet/range-oriented | strong through query |
| Compression | optional/external | often external | built into ecosystem | package-based | storage-engine dependent |
| Type preservation | limited | JSON type system | strong | workbook-dependent | database schema |
| Typical Data Engineering role | boundary format | ingestion boundary | analytical storage | organizational boundary | durable source/target |

No format wins universally.

Use the format that fits the boundary.

A common Data Engineering pattern is:

```text
external CSV / JSON / Excel
        ↓
pandas ingestion
        ↓
explicit schema + validation
        ↓
Parquet
        ↓
downstream analytics / processing
```

That pattern does not mean CSV is "bad." It means text interchange and analytical storage solve different problems.

## Format selection should consider

1. Who produces the data?
2. Who consumes it?
3. Does the source carry reliable schema information?
4. Are identifiers sensitive to formatting?
5. How large is the data?
6. What columns are typically queried?
7. What is the expected compression ratio?
8. Is human editing required?
9. Is the data database-backed?
10. Is the file part of a reproducible pipeline?

# 3. CSV Fundamentals

CSV is a text-based tabular representation.

A simple file may look like:

```text
order_id,amount,country
00123,1000,IN
00124,2500,US
```

The file contains:

- rows;
- delimiters;
- fields;
- an optional header row;
- text encoding;
- quoting rules;
- source-specific missing-value tokens;
- values that the parser must interpret.

A CSV file does **not** inherently carry pandas dtype semantics such as:

```text
Int64
boolean
category
datetime64[ns, UTC]
```

The parser has to construct pandas columns from text.

That is why a CSV reader is doing more work than merely splitting strings.

## The ingestion mental model

```text
CSV bytes
  ↓
decode using encoding
  ↓
split into records
  ↓
handle quoting
  ↓
recognize fields
  ↓
interpret missing tokens
  ↓
infer or apply types
  ↓
build DataFrame
```

Every stage can affect correctness.

# 4. `read_csv()`

The basic call is:

```python
import pandas as pd

df = pd.read_csv("orders.csv")
```

This is useful for exploration.

For production, start by asking what you expect the result to be.

### Prediction-first habit

Before running the reader, write down:

```text
Expected rows:        ?
Expected columns:     ?
Expected dtypes:      ?
Expected nulls:       ?
Expected identifiers: strings?
Expected timestamps:  datetime?
Expected index:       default RangeIndex?
```

This habit turns I/O from trial-and-error into contract enforcement.

## First inspection

```python
import pandas as pd

df = pd.read_csv("orders.csv")

print(df.head())
print(df.shape)
print(df.columns.tolist())
print(df.dtypes)
print(df.index)
```

A useful rule:

> **Inspect before transforming.**

If the schema is already wrong at read time, later transformations may simply hide the problem.

# 5. CSV Parameters

## 5.1 `sep`

`sep` controls the field delimiter.

Comma:

```python
df = pd.read_csv("orders.csv", sep=",")
```

Tab-separated:

```python
df = pd.read_csv("orders.tsv", sep="\t")
```

Semicolon-separated:

```python
df = pd.read_csv("orders.csv", sep=";")
```

Custom delimiter:

```python
df = pd.read_csv("orders.dat", sep="|")
```

### Common failure

A pipe-delimited file read with the default comma separator can become a one-column DataFrame.

Expected:

```text
order_id | amount | country
```

Incorrectly parsed:

```text
"order_id | amount | country"
```

The DataFrame may still exist, so this is a schema validation problem rather than necessarily a parser exception.

## Production check

```python
expected_columns = ["order_id", "amount", "country"]

assert df.columns.tolist() == expected_columns
```

## 5.2 `header`

By default, pandas typically uses the first row as column labels.

For a file with no header:

```text
101,1000,IN
102,2500,US
```

use:

```python
df = pd.read_csv(
    "orders.csv",
    header=None,
)
```

You can combine `header=None` with `names=`:

```python
df = pd.read_csv(
    "orders.csv",
    header=None,
    names=["order_id", "amount", "country"],
)
```

## 5.3 `names`

Use `names=` when the source has no usable header or you want an explicit column schema.

```python
df = pd.read_csv(
    "orders.csv",
    header=None,
    names=["order_id", "amount", "country"],
)
```

Do not casually overwrite a real source header without understanding whether the first line is being consumed as data or metadata.

## Contract check

```python
expected = ["order_id", "amount", "country"]

assert df.columns.tolist() == expected
```

## 5.4 `usecols`

Read only the columns you need.

```python
df = pd.read_csv(
    "orders.csv",
    usecols=["order_id", "amount"],
)
```

This matters for both performance and memory.

Read everything, then drop:

```python
df = pd.read_csv("orders.csv")
df = df[["order_id", "amount"]]
```

Read only what is needed:

```python
df = pd.read_csv(
    "orders.csv",
    usecols=["order_id", "amount"],
)
```

The second design can avoid parsing and materializing unnecessary columns in the first place.

> **Schema-aware reading is usually better than reading everything and discarding most of it later.**

## 5.5 `index=False`

When writing a normal row-oriented CSV output:

```python
df.to_csv(
    "orders_clean.csv",
    index=False,
)
```

If you accidentally write the DataFrame index, a later reader may see an extra column such as:

```text
Unnamed: 0
```

The accidental pattern is:

```python
df.to_csv("orders.csv")
```

Later:

```python
reloaded = pd.read_csv("orders.csv")
print(reloaded.columns.tolist())
```

A typical symptom is:

```text
['Unnamed: 0', 'order_id', 'amount', 'country']
```

The index was serialized as data.

This is not always wrong—sometimes you intentionally need the index—but it should be deliberate.

## 5.6 `encoding`

Encoding maps bytes to text.

UTF-8 is a common modern choice:

```python
df = pd.read_csv(
    "customers.csv",
    encoding="utf-8",
)
```

A legacy source may use Latin-1:

```python
df = pd.read_csv(
    "customers.csv",
    encoding="latin-1",
)
```

A wrong encoding can cause:

- decoding errors;
- corrupted characters;
- unexpected symbols;
- failed parsing.

Store the source encoding in the reader contract when it is known.

## 5.7 `compression`

Pandas can read and write supported compressed files.

```python
df = pd.read_csv(
    "orders.csv.gz",
    compression="gzip",
)
```

Writing:

```python
df.to_csv(
    "orders.csv.gz",
    index=False,
    compression="gzip",
)
```

Compression usually trades:

```text
smaller storage
+
lower transfer size
```

for:

```text
CPU work to compress/decompress
```

Whether compression improves end-to-end pipeline performance depends on storage and CPU characteristics.

# 6. Writing CSV

Basic:

```python
df.to_csv(
    "orders_clean.csv",
    index=False,
)
```

A more explicit write:

```python
columns = [
    "order_id",
    "customer_id",
    "amount",
    "country",
]

df[columns].to_csv(
    "orders_clean.csv",
    index=False,
    encoding="utf-8",
)
```

The engineering idea is the output contract.

```text
Expected columns
Expected order
Expected types/representations
Expected row count
Expected encoding
Expected delimiter
Expected index behavior
```

## Writing a tab-separated file

```python
df.to_csv(
    "orders.tsv",
    sep="\t",
    index=False,
)
```

## Writing compressed CSV

```python
df.to_csv(
    "orders.csv.gz",
    index=False,
    compression="gzip",
)
```

## Stable output schema

```python
OUTPUT_COLUMNS = [
    "order_id",
    "customer_id",
    "amount",
    "created_at",
]

output = df[OUTPUT_COLUMNS]

assert output.columns.tolist() == OUTPUT_COLUMNS

output.to_csv(
    "orders_clean.csv",
    index=False,
)
```

This prevents accidental column-order drift.

# 7. JSON Lines

## What is JSON Lines?

JSON Lines stores one JSON object per line.

Example:

```text
{"order_id":"001","amount":1000}
{"order_id":"002","amount":2000}
{"order_id":"003","amount":1500}
```

This is convenient for:

- APIs;
- logs;
- event-like records;
- incremental ingestion;
- systems that naturally emit one record at a time.

It is different from one giant JSON array:

```json
[
  {"order_id": "001", "amount": 1000},
  {"order_id": "002", "amount": 2000}
]
```

## Reading JSON Lines

```python
import pandas as pd

df = pd.read_json(
    "orders.jsonl",
    lines=True,
)
```

## Writing JSON Lines

```python
df.to_json(
    "orders.jsonl",
    orient="records",
    lines=True,
)
```

`orient="records"` means each row becomes an object.

`lines=True` means those objects are written one per line.

## JSONL and identifiers

A record such as:

```json
{"order_id":"000123","amount":1200}
```

communicates that the identifier is textual.

Do not convert identifiers to numbers merely because their characters are digits.

## Prediction exercise

Given:

```text
{"country":"IN","amount":100}
{"country":"US","amount":200}
{"country":"IN","amount":300}
```

predict:

```text
rows = 3
columns = 2
```

Then verify:

```python
assert df.shape == (3, 2)
assert df.columns.tolist() == ["country", "amount"]
```

# 8. Parquet Fundamentals

Parquet is a columnar binary storage format designed for analytical workloads.

Conceptually:

```text
CSV
→ rows encoded as text

Parquet
→ columns stored in a typed analytical format
```

Pandas commonly uses PyArrow for Parquet interoperability:

```python
import pandas as pd

df = pd.read_parquet(
    "orders.parquet",
    engine="pyarrow",
)
```

Writing:

```python
df.to_parquet(
    "orders.parquet",
    engine="pyarrow",
)
```

## Why Parquet preserves types better than CSV

A CSV file essentially stores text representations:

```text
1000
2026-01-15
001234
```

The reader has to infer or apply meaning.

Parquet carries schema information with stored data. This makes it much better suited to preserving analytical types across read/write boundaries.

That does not mean a round trip should be assumed to preserve every DataFrame property identically. Verify what matters.

## Analytical advantages

Parquet is especially useful when you commonly need:

```text
only a few columns
+
a subset of rows
```

because its storage model supports column pruning and, where supported by the engine/layout, row-group or partition filtering.

## Typical Data Engineering pattern

```text
raw CSV / JSON / Excel
      ↓
pandas ingestion contract
      ↓
validated DataFrame
      ↓
Parquet
      ↓
analytical reads
```

# 9. CSV vs Parquet

| Property | CSV | Parquet |
|---|---|---|
| Representation | Text | Binary columnar |
| Human-readable | Yes | No |
| Schema embedded | Limited | Stronger |
| Type preservation | Reader-dependent | Strong |
| Column pruning | Limited | Strong |
| Compression | Optional | Integrated into format/ecosystem |
| Typical analytics read | More parsing | More analytical-friendly |
| Easy manual editing | Yes | No |
| Typical role | Interchange/boundary | Analytics/lake storage |

CSV is often exactly the right choice at a system boundary.

Examples:

- a vendor only exports CSV;
- an operations team sends a simple tabular file;
- a simple external integration expects CSV.

The production improvement is not "replace every CSV."

It is:

```text
receive CSV
→ apply explicit contract
→ validate
→ convert to a more analytical representation when appropriate
```

# 10. Excel

Excel is common because organizations use spreadsheets as operational interfaces.

Read:

```python
import pandas as pd

df = pd.read_excel(
    "orders.xlsx",
    sheet_name="Orders",
)
```

Write:

```python
df.to_excel(
    "orders_report.xlsx",
    sheet_name="Orders",
    index=False,
)
```

For `.xlsx` files, `openpyxl` is a common engine.

## `sheet_name`

Read one sheet:

```python
df = pd.read_excel(
    "workbook.xlsx",
    sheet_name="Orders",
)
```

Read multiple sheets:

```python
sheets = pd.read_excel(
    "workbook.xlsx",
    sheet_name=["Orders", "Customers"],
)
```

When multiple sheets are requested, pandas can return multiple DataFrames in a mapping-like result.

## Header rows

Suppose a workbook looks like:

```text
Company Revenue Report
Generated: 2026-01-31

order_id    amount
001         1000
002         1500
```

The actual column header is not necessarily row 0.

A reader may need:

```python
df = pd.read_excel(
    "report.xlsx",
    sheet_name="Orders",
    header=2,
)
```

The exact value depends on the workbook layout.

## Merged cells

Merged cells are a spreadsheet presentation feature.

A visual spreadsheet may look like:

```text
          Q1 Report
--------------------------------
Order ID | Amount | Country
```

but the underlying cell structure may contain blanks created by merged cells or title rows.

The ingestion rule is:

> **Treat spreadsheets as presentation-oriented inputs unless a stable tabular contract has been established.**

Inspect the result before continuing.

Excel is not "bad." It is useful at organizational boundaries, especially where humans need to edit or consume the workbook.

# 11. Explicit Typing — `dtype=`

This is one of the most important production controls.

Without an explicit contract:

```python
df = pd.read_csv("orders.csv")
```

the parser can infer types.

Inference is convenient in exploration.

Inference is risky when:

- leading zeros matter;
- nulls occur in integer fields;
- source values mix representations;
- a column contains identifiers;
- reproducibility matters;
- a source changes over time.

## Explicit schema example

```python
df = pd.read_csv(
    "orders.csv",
    dtype={
        "order_id": "string",
        "customer_id": "string",
        "quantity": "Int64",
    },
)
```

The choice `"string"` tells the reader that the field has string semantics, not numeric measurement semantics.

`"Int64"` is a pandas nullable integer dtype. It can represent integer values while supporting missing values.

## Inspect the result

```python
print(df.dtypes)

assert df["order_id"].dtype.name == "string"
assert str(df["quantity"].dtype) == "Int64"
```

## Why explicit typing helps

```text
source contract
    ↓
explicit dtype
    ↓
predictable DataFrame
    ↓
predictable transformations
    ↓
predictable output
```

## Reader contract example

```python
CUSTOMER_SCHEMA = {
    "customer_id": "string",
    "country": "string",
    "postal_code": "string",
    "age": "Int64",
}
```

Then:

```python
customers = pd.read_csv(
    "customers.csv",
    dtype=CUSTOMER_SCHEMA,
)
```

This is easier to audit than relying on whatever inference happened to occur today.

# 12. `parse_dates`

Dates should become datetime values at a deliberate point in ingestion.

A source might contain:

```text
created_at
2026-01-15
2026-01-16
```

Read and parse:

```python
df = pd.read_csv(
    "orders.csv",
    parse_dates=["created_at"],
)
```

Then inspect:

```python
print(df["created_at"].dtype)
```

The exact dtype representation should be verified rather than assumed.

## Why parse dates early?

A datetime-aware column can support:

- chronological comparisons;
- time-based grouping;
- duration calculations;
- later resampling and time-series operations.

If the source contract is known, deterministic parsing is preferable to guessing.

# 13. `date_format`

Suppose a source specifies:

```text
DD/MM/YYYY
```

Example:

```text
05/01/2026
```

Use the known format:

```python
df = pd.read_csv(
    "orders.csv",
    parse_dates=["created_at"],
    date_format="%d/%m/%Y",
)
```

## Why this matters

Consider:

```text
01/02/2026
```

Without knowing the convention, an engineer cannot safely infer whether the date means:

```text
1 February 2026
```

or:

```text
January 2 2026
```

If the source documentation says `DD/MM/YYYY`, encode that decision.

> **A parser should not be asked to guess what the source contract already tells you.**

# 14. `na_values`

`na_values` defines source tokens that should be interpreted as missing.

Example:

```python
df = pd.read_csv(
    "customers.csv",
    na_values=["N/A", "NULL", ""],
)
```

Now a source token such as:

```text
N/A
```

can become a missing value.

But not every unusual string should be treated as missing.

Consider:

```text
status
NA
ACTIVE
UNKNOWN
```

If `"NA"` is a legitimate status code, converting it to missing is wrong.

> **Only declare a token missing when the source contract says it means missing.**

Possible source-specific tokens include:

```text
N/A
NULL
MISSING
-9999
```

but their meaning is not universal.

# 15. `keep_default_na=False`

Pandas has built-in missing-value token handling.

When a source uses strings such as `"NA"` or `"null"` as legitimate text, default token interpretation can be undesirable.

You can disable the default token set:

```python
df = pd.read_csv(
    "customers.csv",
    keep_default_na=False,
)
```

Then explicitly decide which tokens should be missing:

```python
df = pd.read_csv(
    "customers.csv",
    keep_default_na=False,
    na_values=["", "MISSING"],
)
```

This creates a clearer contract:

```text
default missing tokens
→ disabled

source-specific missing tokens
→ explicitly listed
```

## Important distinction

`keep_default_na=False` does not mean "there are no missing values."

It means:

> Do not automatically apply pandas' default textual NA-token interpretation.

You still control missingness through source-aware options and validation.

# 16. Identifier Preservation

Identifiers are one of the common ingestion traps.

Treat these as strings unless the source semantics and downstream requirements say otherwise:

- ZIP codes;
- phone numbers;
- customer IDs;
- order IDs;
- account numbers;
- product codes;
- external references.

## The leading-zero problem

Input:

```text
001234
001235
001236
```

Desired semantic model:

```text
string identifier
```

Read explicitly:

```python
df = pd.read_csv(
    "customers.csv",
    dtype={
        "customer_id": "string",
        "postal_code": "string",
    },
)
```

Verify:

```python
assert df["customer_id"].iloc[0] == "001234"
assert df["postal_code"].iloc[0] == "00123"
```

## Why not store IDs as integers?

Arithmetic makes no sense for most identifiers.

```text
customer_id = 001234
```

does not mean:

```text
1234 customers
```

It is a label.

> **Digits do not automatically make a field numeric.**

# 17. Bad Input — Malformed CSV

Real input is often imperfect.

Example:

```text
expected:
order_id,amount,country

bad:
1001,2500,IN,EXTRA_FIELD
```

or:

```text
1002,2500
```

## `on_bad_lines`

Pandas provides `on_bad_lines` to control malformed rows.

For exploratory work:

```python
df = pd.read_csv(
    "orders.csv",
    on_bad_lines="warn",
)
```

Or, where skipping is explicitly acceptable:

```python
df = pd.read_csv(
    "orders.csv",
    on_bad_lines="skip",
)
```

## The production danger

Skipping a row is data loss.

A pipeline must distinguish:

```text
file parsed successfully
```

from:

```text
all expected source records were preserved
```

Therefore:

> **Every skipped input row should be observable and accounted for.**

If exact skipped-row details cannot be captured by the chosen reader configuration, use a separate validation/counting step rather than pretending the loss is harmless.

## Production question

Do not ask:

> "Did the file load?"

Ask:

> "Did the file load under the expected schema, and can I account for every rejected record?"

# 18. CSV Quoting

Quoting protects field boundaries when a value contains the delimiter.

Example:

```text
order_id,address,amount
1001,"New York, NY",2500
```

The comma in:

```text
"New York, NY"
```

belongs inside the address field.

Incorrect parsing could split it into two columns.

## Debugging

When columns unexpectedly shift:

1. inspect the raw line;
2. check the delimiter;
3. inspect quoting;
4. inspect header interpretation;
5. verify the number of parsed columns;
6. compare against the source contract.

Schema invariant:

```python
assert df.columns.tolist() == [
    "order_id",
    "address",
    "amount",
]
```

A simple schema assertion can catch a surprising number of ingestion failures.

# 19. Thousands and Decimal Separators

Numbers are not formatted the same way in every locale.

US-style:

```text
1,234.56
```

Common European-style:

```text
1.234,56
```

Pandas supports explicit controls:

```python
df = pd.read_csv(
    "sales.csv",
    thousands=",",
    decimal=".",
)
```

For a source using:

```text
1.234,56
```

a corresponding configuration can be:

```python
df = pd.read_csv(
    "sales.csv",
    thousands=".",
    decimal=",",
)
```

## Why explicit parsing matters

If punctuation is not interpreted according to the source convention, the column may remain textual or be parsed incorrectly.

A production reader contract should document the convention:

```text
amount
→ numeric
→ thousands="."
→ decimal=","
→ source convention explicitly documented
```

# 20. BOMs / Byte Order Marks

A UTF-8 BOM can appear at the beginning of a text file.

A symptom can be an unexpected first column name:

```text
"\ufefforder_id"
```

instead of:

```text
"order_id"
```

## Diagnose it

```python
df = pd.read_csv("orders.csv")

print(repr(df.columns[0]))
```

If you see:

```text
'\ufefforder_id'
```

you have evidence of a BOM-related header issue.

## Encoding-aware reading

A common strategy for UTF-8 files carrying a BOM is:

```python
df = pd.read_csv(
    "orders.csv",
    encoding="utf-8-sig",
)
```

Then verify:

```python
assert df.columns[0] == "order_id"
```

Do not blindly strip unusual characters from all inputs. Identify the encoding behavior and apply the narrowest correct fix.

# 21. SQL — `read_sql`

Pandas can read SQL query results into a DataFrame.

A conceptual SQLAlchemy setup:

```python
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("sqlite:///orders.db")

df = pd.read_sql(
    "SELECT order_id, amount FROM orders",
    con=engine,
)
```

`read_sql()` provides a DataFrame-oriented interface over SQL sources. The database remains responsible for database-side storage and query execution.

## Why use SQL before pandas?

If the database can filter and project efficiently, request:

```text
required rows
+
required columns
```

rather than retrieving an entire table.

Example:

```python
query = """
SELECT order_id, customer_id, amount
FROM orders
WHERE country = :country
"""

df = pd.read_sql(
    query,
    con=engine,
    params={"country": "IN"},
)
```

The exact parameter behavior depends on the database/driver, so keep the database-specific layer explicit.

## Scope boundary

This topic introduces pandas-side SQL I/O. Deep database concepts belong later in the roadmap.

# 22. SQL — `to_sql`

Write a DataFrame to a SQL table:

```python
df.to_sql(
    "orders_clean",
    con=engine,
    if_exists="replace",
    index=False,
)
```

Common `if_exists` policies:

```text
fail
replace
append
```

Choose deliberately.

## `append`

```python
df.to_sql(
    "orders_clean",
    con=engine,
    if_exists="append",
    index=False,
)
```

`append` does not automatically make a pipeline idempotent. Running the same load twice can create duplicates.

## `replace`

```python
df.to_sql(
    "orders_clean",
    con=engine,
    if_exists="replace",
    index=False,
)
```

This can be useful for full refreshes or temporary targets but is not automatically the right production default.

## `fail`

```python
df.to_sql(
    "orders_clean",
    con=engine,
    if_exists="fail",
    index=False,
)
```

Use this when an existing target should be treated as unexpected.

## Production questions

Before `to_sql`, decide:

- What is the target grain?
- Is the load append or replace?
- What happens on retry?
- How are duplicates prevented?
- What schema should the target have?
- Is the write transactional?
- What batch size is safe?

# 23. `chunksize` with SQL

Large writes do not necessarily belong in one giant database insert operation.

Example:

```python
df.to_sql(
    "orders_clean",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=10_000,
    method="multi",
)
```

Conceptually:

```text
DataFrame
   ↓
10,000-row batch
   ↓
database
   ↓
10,000-row batch
   ↓
database
   ↓
...
```

## Why `chunksize`?

It can help control:

- request size;
- parameter counts;
- transient memory;
- batch size;
- database pressure.

## Why `method="multi"`?

It can batch multiple rows into an insert operation where supported by the backend.

Do not assume every database has identical behavior.

## Batch-size trade-off

```text
larger chunks
→ fewer round trips
→ potentially larger requests / more pressure

smaller chunks
→ smaller requests
→ potentially more overhead
```

There is no universal best value. Measure under real conditions.

# 24. Reading from URLs

Pandas readers can work with URL-based inputs where the reader supports them.

Example:

```python
import pandas as pd

df = pd.read_csv(
    "https://example.com/orders.csv",
)
```

The syntax is simple. Production reliability is not.

Remote-input failure modes include:

```text
network failure
authentication failure
timeout
changed content
partial content
unexpected format
rate limits
```

Therefore, the surrounding pipeline should define:

- how authentication is handled;
- how failures are surfaced;
- how retries are performed;
- how downloaded content is validated;
- how source version/date is tracked.

Pandas is the DataFrame/I/O layer, not a complete remote-data reliability framework.

# 25. Compressed Sources

Compression can apply to text-based data such as CSV.

```python
df = pd.read_csv(
    "orders.csv.gz",
    compression="gzip",
)
```

Writing:

```python
df.to_csv(
    "orders.csv.gz",
    compression="gzip",
    index=False,
)
```

Compression trades:

```text
less storage / transfer
```

for:

```text
CPU work
```

Measure end-to-end behavior rather than assuming that a smaller file is faster.

# 26. Many Files with `glob` + `pd.concat`

Daily file ingestion often looks like:

```text
data/
├── orders_2026-01-01.csv
├── orders_2026-01-02.csv
├── orders_2026-01-03.csv
└── ...
```

Use deterministic file discovery:

```python
from pathlib import Path

files = sorted(
    Path("data").glob("orders_*.csv")
)

print(files)
```

Read:

```python
frames = [
    pd.read_csv(path)
    for path in files
]
```

Combine:

```python
df = pd.concat(
    frames,
    ignore_index=True,
)
```

## Why `sorted()`?

Filesystem enumeration order should not be treated as a business ordering rule.

## Why `ignore_index=True`?

Per-file indexes usually do not represent a meaningful global identifier for a stacked dataset.

## Important limitation

This pattern materializes every DataFrame before concatenating. For many large files, memory usage can become significant.

Later Topic 13 covers chunked and memory-aware processing in depth.

# 27. Reading Many Files — Schema Consistency

Suppose:

```text
orders_01.csv
order_id,amount,country

orders_02.csv
order_id,amount,country

orders_03.csv
order_id,amount
```

A simple concatenation may produce missing values for the absent column.

That may be correct—or it may be schema drift.

## Compare columns before combining

```python
from pathlib import Path
import pandas as pd

files = sorted(Path("data").glob("orders_*.csv"))

expected_columns = [
    "order_id",
    "amount",
    "country",
]

frames = []

for path in files:
    frame = pd.read_csv(path)

    if frame.columns.tolist() != expected_columns:
        raise ValueError(
            f"Schema mismatch in {path}"
        )

    frames.append(frame)

df = pd.concat(
    frames,
    ignore_index=True,
)
```

## Why not let `concat()` decide?

`concat()` combines data structurally. It cannot tell you whether a difference is:

```text
intentional schema evolution
```

or:

```text
producer defect
```

The ingestion contract must define that decision.

## Also check dtypes

```python
expected_dtypes = {
    "order_id": "string",
    "amount": "Float64",
    "country": "string",
}
```

For production, compare actual dtypes against the declared contract.

# 28. PyArrow CSV Engine

Pandas can use different CSV parsing engines.

A pandas 3.x reader can dispatch through PyArrow:

```python
df = pd.read_csv(
    "orders.csv",
    engine="pyarrow",
)
```

## Why use the PyArrow engine?

For supported workloads, it can provide faster parsing and supports multithreaded CSV reading.

But:

> **Do not assume `engine="pyarrow"` is always faster.**

Performance depends on:

- file structure;
- column count;
- data types;
- hardware;
- storage;
- parser features required;
- workload size.

## Engine selection is also a compatibility decision

Different engines can have different supported options and behavior.

Therefore:

```text
default engine
vs
PyArrow engine
```

is both a behavior and performance choice.

## Benchmark pattern

```python
from time import perf_counter
import pandas as pd

start = perf_counter()

df = pd.read_csv(
    "orders.csv",
    engine="pyarrow",
)

elapsed = perf_counter() - start

print(f"rows={len(df):,}")
print(f"seconds={elapsed:.3f}")
```

Benchmark the same input and configuration when comparing engines.

# 29. `dtype_backend`

Pandas supports backend choices for nullable DataFrame dtypes.

Two important options in the roadmap are:

```python
dtype_backend="numpy_nullable"
```

and:

```python
dtype_backend="pyarrow"
```

## NumPy nullable backend

```python
df = pd.read_csv(
    "orders.csv",
    dtype_backend="numpy_nullable",
)
```

This asks pandas to use nullable pandas dtypes where available.

## PyArrow backend

```python
df = pd.read_csv(
    "orders.csv",
    dtype_backend="pyarrow",
)
```

This produces Arrow-backed nullable columns where supported.

## Engine vs backend

These are different concepts:

```text
engine="pyarrow"
→ how input is parsed

dtype_backend="pyarrow"
→ how resulting DataFrame columns are represented
```

They should not be treated as synonyms.

## Inspect the result

```python
print(df.dtypes)
```

Backend choice can affect:

- nullability;
- underlying representation;
- interoperability;
- memory characteristics;
- downstream behavior.

Treat it as part of the DataFrame schema decision.

# 30. Parquet Column Pruning

Suppose a Parquet dataset contains:

```text
order_id
customer_id
country
quantity
unit_price
discount
created_at
campaign
device
```

but the current step only needs:

```text
order_id
amount
created_at
```

Read only those columns:

```python
df = pd.read_parquet(
    "orders.parquet",
    columns=[
        "order_id",
        "amount",
        "created_at",
    ],
    engine="pyarrow",
)
```

## Why this matters

Reading all columns and dropping most later:

```python
df = pd.read_parquet("orders.parquet")
df = df[
    ["order_id", "amount", "created_at"]
]
```

can require more I/O, decoding, memory, and processing than necessary.

> **Prune as early as the storage format allows.**

# 31. Parquet Filters

Pandas can pass row filters through the Parquet engine.

```python
df = pd.read_parquet(
    "orders.parquet",
    filters=[
        ("country", "==", "IN"),
    ],
    engine="pyarrow",
)
```

Depending on dataset layout and metadata, filters can allow the underlying system to avoid materializing irrelevant row groups or partitions.

## Conceptual comparison

Read everything:

```text
all rows
  ↓
DataFrame
  ↓
filter country == IN
```

Filter-aware read:

```text
Parquet metadata / layout
  ↓
relevant groups where possible
  ↓
DataFrame
```

Do not promise zero irrelevant I/O. Filtering behavior depends on format, engine, layout, partitioning, and predicate.

## Example

```python
df = pd.read_parquet(
    "orders.parquet",
    filters=[
        ("country", "==", "IN"),
        ("year", ">=", 2026),
    ],
    engine="pyarrow",
)
```

# 32. `partition_cols`

When writing a Parquet dataset, you can partition by selected columns:

```python
df.to_parquet(
    "orders_dataset",
    engine="pyarrow",
    partition_cols=["country", "year"],
)
```

Conceptually:

```text
orders_dataset/
├── country=IN/
│   ├── year=2025/
│   └── year=2026/
└── country=US/
    ├── year=2025/
    └── year=2026/
```

The exact file layout is managed by the Parquet engine.

## Why partition?

A useful partition key often appears in common filtering patterns:

```text
country
year
month
```

may be more useful than:

```text
customer_id
```

## Partition trade-offs

Too little partitioning:

```text
harder to eliminate irrelevant data
```

Too much partitioning:

```text
many tiny files
metadata overhead
filesystem/object-store overhead
```

> **Partition for meaningful access patterns, not for every column.**

# 33. Reliable Writing

A production writer should not assume that:

```python
df.to_parquet("final/output.parquet")
```

is automatically an atomic publish operation.

A careful local-filesystem pattern is:

```text
DataFrame
  ↓
prepare schema
  ↓
write temporary path
  ↓
validate
  ↓
rename/finalize
```

## Example

```python
from pathlib import Path
import os

final_path = Path("output/orders.parquet")
temp_path = final_path.with_suffix(".tmp.parquet")

df.to_parquet(
    temp_path,
    engine="pyarrow",
)

os.replace(
    temp_path,
    final_path,
)
```

`os.replace()` provides a strong finalization pattern on typical local filesystems, but object-storage semantics differ.

## Why not write directly to the final name?

A crash during writing can leave:

```text
partial file
corrupt file
truncated output
```

A downstream consumer may still discover the path.

The broader lesson:

> **Separate construction of an output from publication of that output.**

# 34. Deterministic Column Order

Column order affects:

- CSV readability;
- schema contracts;
- downstream consumers;
- stable tests;
- manual inspection;
- reproducible output.

Example:

```python
OUTPUT_COLUMNS = [
    "order_id",
    "customer_id",
    "amount",
    "created_at",
]

output = df[OUTPUT_COLUMNS]

assert output.columns.tolist() == OUTPUT_COLUMNS
```

Then:

```python
output.to_csv(
    "orders_clean.csv",
    index=False,
)
```

Do not rely on accidental ordering after joins, assignments, concatenation, or reshaping.

# 35. Explicit Output Schemas

An output contract can define:

```python
EXPECTED_COLUMNS = [
    "order_id",
    "customer_id",
    "amount",
    "created_at",
]
```

And, where appropriate:

```python
EXPECTED_DTYPES = {
    "order_id": "string",
    "customer_id": "string",
    "amount": "Float64",
}
```

A lightweight validator:

```python
def validate_output_schema(
    df,
    expected_columns,
):
    actual = df.columns.tolist()

    if actual != expected_columns:
        raise ValueError(
            f"Unexpected columns: {actual}"
        )
```

Use it:

```python
validate_output_schema(
    df,
    EXPECTED_COLUMNS,
)
```

The writer should not be the first place where a schema problem is discovered.

Preferred flow:

```text
transform
 ↓
validate
 ↓
write
```

# 36. Round-Trip Testing

A round trip means:

```text
DataFrame
   ↓
write
   ↓
file
   ↓
read
   ↓
DataFrame
   ↓
compare
```

For Parquet:

```python
original.to_parquet(
    "orders.parquet",
    engine="pyarrow",
)

loaded = pd.read_parquet(
    "orders.parquet",
    engine="pyarrow",
)

pd.testing.assert_frame_equal(
    original,
    loaded,
)
```

This tests more than file existence.

You are testing:

- columns;
- values;
- index;
- dtypes;
- row ordering where relevant;
- missing values;
- timestamp representations.

## CSV round trip

```python
original.to_csv(
    "orders.csv",
    index=False,
)

loaded = pd.read_csv(
    "orders.csv",
)

print(loaded.dtypes)
```

A CSV round trip may not preserve every pandas dtype automatically, so an explicit read contract may be required.

## Important lesson

A file being readable is not proof that the round trip preserved the intended schema.

Test what the contract requires.

# 37. Reader Contract

A **reader contract** is the explicit agreement between a source and the ingestion code.

| Column | Expected dtype | Missing tokens | Date format | Required? | Notes |
|---|---|---|---|---|---|
| customer_id | string | none | — | yes | preserve leading zeros |
| postal_code | string | `""` | — | no | identifier |
| created_at | datetime | `""` | `%d/%m/%Y` | yes | normalize later |
| amount | Float64 | `N/A` | — | yes | numeric measurement |

The contract can also include:

```text
delimiter
encoding
header position
quoting
decimal convention
malformed-row policy
required columns
source version
```

## Why contracts matter

Without a contract:

```text
parser behavior
+
source changes
+
type inference
+
default NA handling
```

can interact unpredictably.

With a contract:

```text
source
 ↓
known assumptions
 ↓
explicit parser configuration
 ↓
predictable DataFrame
```

## A contract dictionary

```python
READER_CONTRACT = {
    "encoding": "latin-1",
    "sep": ",",
    "dtype": {
        "customer_id": "string",
        "postal_code": "string",
        "amount": "Float64",
    },
    "parse_dates": ["created_at"],
    "date_format": "%d/%m/%Y",
    "keep_default_na": False,
    "na_values": ["", "N/A"],
}
```

Then:

```python
df = pd.read_csv(
    "customers.csv",
    **READER_CONTRACT,
)
```

This centralizes ingestion assumptions.

# 38. Reader Contract vs Type Inference

## Inference

Good for:

- exploration;
- notebooks;
- quick investigations;
- unknown input discovery.

Advantages:

```text
convenient
low setup
```

Risks:

```text
source changes can change inferred dtypes
identifiers can be misclassified
nulls can change type
mixed values can produce unexpected representations
```

## Explicit contract

Better when:

- the source is recurring;
- downstream schema matters;
- reproducibility matters;
- identifiers require exact representation;
- null semantics matter;
- failure must be detected early.

The correct conclusion is:

> **Inference is convenient; explicit contracts are safer for recurring production ingestion.**

# 39. Debugging Data I/O Problems

The debugging pattern for I/O is:

```text
Symptom
  ↓
Inspect raw source
  ↓
Inspect reader configuration
  ↓
Inspect DataFrame schema
  ↓
Compare against contract
  ↓
Fix the narrowest cause
  ↓
Add an invariant/test
```

## Bug 1 — Leading zeros disappear

### Symptom

```text
source:
001234

DataFrame:
1234
```

### Root cause

The identifier was inferred or converted as numeric.

### Inspect

```python
print(df["customer_id"].dtype)
print(df["customer_id"].head())
```

### Correct

```python
df = pd.read_csv(
    "customers.csv",
    dtype={
        "customer_id": "string",
    },
)
```

### Prevention

Classify identifiers separately from numeric measurements.

---

## Bug 2 — `"NA"` unexpectedly becomes missing

### Symptom

```text
source:
status = "NA"

DataFrame:
status = missing
```

### Root cause

Default textual NA-token interpretation may have been applied.

### Correct approach

```python
df = pd.read_csv(
    "customers.csv",
    keep_default_na=False,
)
```

Or define source-specific missing tokens:

```python
df = pd.read_csv(
    "customers.csv",
    keep_default_na=False,
    na_values=["", "MISSING"],
)
```

### Prevention

Document domain codes separately from missing tokens.

---

## Bug 3 — Dates parsed incorrectly

### Symptom

```text
01/02/2026
```

has the wrong calendar meaning.

### Root cause

Ambiguous parsing.

### Correct

```python
df = pd.read_csv(
    "orders.csv",
    parse_dates=["created_at"],
    date_format="%d/%m/%Y",
)
```

### Prevention

Store the source date format in the reader contract.

---

## Bug 4 — `Unnamed: 0` appears

### Symptom

```text
columns =
['Unnamed: 0', 'order_id', 'amount']
```

### Root cause

The DataFrame Index was serialized to CSV.

### Correct

```python
df.to_csv(
    "orders.csv",
    index=False,
)
```

---

## Bug 5 — Wrong encoding

### Symptom

A CSV fails with a decoding error or characters appear corrupted.

### Root cause

The reader used the wrong encoding.

### Correct

```python
df = pd.read_csv(
    "customers.csv",
    encoding="latin-1",
)
```

---

## Bug 6 — CSV columns shift

### Symptom

A row expected to have 3 columns produces 4.

### Root cause

Quoted delimiters were interpreted incorrectly or the source is malformed.

### Inspect

```text
1001,"New York, NY",2500
```

### Prevention

Test representative rows containing delimiters inside fields and validate the resulting schema.

---

## Bug 7 — BOM corrupts the first column name

### Symptom

```python
print(repr(df.columns[0]))
```

may return:

```text
'﻿order_id'
```

### Correct

```python
df = pd.read_csv(
    "orders.csv",
    encoding="utf-8-sig",
)
```

---

## Bug 8 — Malformed rows are silently skipped

### Symptom

Row count is lower than expected.

### Root cause

A permissive malformed-row policy discarded records.

### Prevention

Track rejected-row counts and causes.

---

## Bug 9 — Daily files have inconsistent schemas

### Symptom

Concatenation produces unexpected missing columns or changed dtypes.

### Root cause

Schema drift.

### Correct

Validate every file before combining.

---

## Bug 10 — Parquet round trip differs

### Symptom

```python
pd.testing.assert_frame_equal(
    original,
    loaded,
)
```

fails.

### Inspect

```python
print(original.dtypes)
print(loaded.dtypes)

print(original.index)
print(loaded.index)

print(original.columns)
print(loaded.columns)
```

Then determine which difference violates the intended contract.

---

## Bug 11 — SQL write uses too-large batches

### Symptom

An insert is slow or creates excessive database/network pressure.

### Starting point

```python
df.to_sql(
    "orders_clean",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=10_000,
    method="multi",
)
```

Benchmark safe batch sizes under the real workload.

---

## Bug 12 — Full Parquet read wastes resources

### Symptom

Memory usage is unnecessarily high.

### Better

```python
df = pd.read_parquet(
    "orders.parquet",
    columns=["order_id", "amount"],
    engine="pyarrow",
)
```

Add filters where appropriate.

# 40. Hands-on Exercise — `io_contracts.py`

This exercise turns the chapter into a production-style ingestion problem.

## Scenario

You receive:

```text
customers.csv
```

with:

- identifiers containing leading zeros;
- `"N/A"` and `""` as null tokens;
- dates using `DD/MM/YYYY`;
- Latin-1 encoding;
- two malformed lines.

Your job is to build a reader contract instead of relying on inference.

## Task 1 — Read with defaults

Start with:

```python
import pandas as pd

df = pd.read_csv(
    "customers.csv",
)
```

Do not fix anything yet.

Inspect:

```python
print(df.head())
print(df.shape)
print(df.columns.tolist())
print(df.dtypes)
print(df.isna().sum())
```

Document:

- incorrect dtypes;
- missing-value interpretation;
- leading-zero corruption risk;
- date parsing behavior;
- malformed-row behavior;
- encoding issues.

Write down the problems before fixing them.

## Task 2 — Build `read_customers(path)`

Design:

```python
def read_customers(path) -> pd.DataFrame:
    ...
```

The function should encode the source contract using:

- explicit `dtype`;
- `na_values`;
- `keep_default_na=False`;
- `date_format`;
- `encoding`;
- `on_bad_lines`.

Starting structure:

```python
import pandas as pd

CUSTOMER_DTYPES = {
    "customer_id": "string",
    "postal_code": "string",
    "name": "string",
}

def read_customers(path):
    return pd.read_csv(
        path,
        dtype=CUSTOMER_DTYPES,
        parse_dates=["signup_date"],
        date_format="%d/%m/%Y",
        na_values=["", "N/A"],
        keep_default_na=False,
        encoding="latin-1",
        on_bad_lines="warn",
    )
```

Adapt exact column names to the source fixture.

## Task 3 — Bad-line accounting

The source contains two malformed lines.

Your ingestion process must make the loss observable.

Do not merely rely on:

```python
on_bad_lines="skip"
```

and move on.

Your design should answer:

```text
How many source rows were expected?
How many were read?
How many were rejected?
Why were they rejected?
```

Key lesson:

```text
successful parsing
≠
complete ingestion
```

## Task 4 — Parquet output

Write the validated DataFrame:

```python
df.to_parquet(
    "customers.parquet",
    engine="pyarrow",
)
```

Validate the intended columns before writing.

## Task 5 — Round-trip test

Read the Parquet result:

```python
loaded = pd.read_parquet(
    "customers.parquet",
    engine="pyarrow",
)
```

Then:

```python
pd.testing.assert_frame_equal(
    df,
    loaded,
)
```

If a deliberate representation difference exists, configure the assertion narrowly and explain why.

## Task 6 — SQLite

Create a local SQLAlchemy engine:

```python
from sqlalchemy import create_engine

engine = create_engine(
    "sqlite:///customers.db"
)
```

Write:

```python
df.to_sql(
    "customers",
    con=engine,
    if_exists="replace",
    index=False,
)
```

Read:

```python
loaded_sql = pd.read_sql(
    "SELECT * FROM customers",
    con=engine,
)
```

Inspect:

```python
print(loaded_sql.dtypes)
print(loaded_sql.columns)
```

Document expected type differences between pandas and SQLite.

## Task 7 — Large CSV benchmark

The roadmap calls for approximately a 1 GB CSV benchmark.

> **Never intentionally destabilize your computer just to meet an exercise size.**

Compare:

```text
default CSV engine
vs
engine="pyarrow"
```

Benchmark pattern:

```python
from time import perf_counter
import pandas as pd

def benchmark_csv(path, engine=None):
    start = perf_counter()

    if engine is None:
        df = pd.read_csv(path)
    else:
        df = pd.read_csv(
            path,
            engine=engine,
        )

    elapsed = perf_counter() - start

    return {
        "engine": engine or "default",
        "rows": len(df),
        "seconds": elapsed,
    }

default_result = benchmark_csv(
    "large_orders.csv",
)

pyarrow_result = benchmark_csv(
    "large_orders.csv",
    engine="pyarrow",
)

print(default_result)
print(pyarrow_result)
```

Record:

```text
engine
row count
runtime
memory observation
notes
```

Do not conclude that one engine always wins.

# 41. Testing Requirements

I/O tests should verify more than "the file exists."

Test:

- expected columns;
- expected row count;
- dtypes;
- identifier preservation;
- null counts;
- parsed dates;
- malformed-row handling;
- Parquet round trip;
- output column order;
- schema expectations.

## Schema test

```python
expected_columns = [
    "customer_id",
    "postal_code",
    "name",
    "signup_date",
]

assert df.columns.tolist() == expected_columns
```

## Row-count test

```python
assert len(df) == expected_row_count
```

## Identifier test

```python
assert df["customer_id"].dtype.name == "string"
assert df["customer_id"].iloc[0] == "000123"
```

## DataFrame comparison

```python
pd.testing.assert_frame_equal(
    expected,
    actual,
)
```

## Round-trip test

```python
df.to_parquet(
    "result.parquet",
    engine="pyarrow",
)

loaded = pd.read_parquet(
    "result.parquet",
    engine="pyarrow",
)

pd.testing.assert_frame_equal(
    df,
    loaded,
)
```

A DataFrame with correct values but the wrong index or dtype can still be incorrect.

# 42. Prediction-First Exercises

Before executing an I/O operation, predict:

```text
Expected rows:
Expected columns:
Expected dtypes:
Expected missing values:
Expected identifier representation:
Expected date representation:
Expected index:
```

## Example A — Explicit identifier dtype

```python
df = pd.read_csv(
    "customers.csv",
    dtype={
        "customer_id": "string",
    },
)
```

Predict:

```text
customer_id remains textual
leading zeros preserved
```

Verify:

```python
assert df["customer_id"].dtype.name == "string"
```

## Example B — Missing-token policy

```python
df = pd.read_csv(
    "customers.csv",
    keep_default_na=False,
)
```

Ask:

```text
Which tokens are still considered missing?
Which strings remain ordinary strings?
```

The complete answer depends on the source and the rest of the reader configuration.

## Example C — Parquet column pruning

```python
df = pd.read_parquet(
    "orders.parquet",
    columns=["order_id", "amount"],
    engine="pyarrow",
)
```

Predict:

```text
rows:
eligible rows from the source

columns:
2

index:
depends on stored/read representation
```

Verify:

```python
assert df.columns.tolist() == [
    "order_id",
    "amount",
]
```

## Example D — CSV output

```python
df.to_csv(
    "orders.csv",
    index=False,
)
```

Predict:

```text
the pandas Index is not emitted as a separate data column
```

## Example E — Multiple input files

```python
from pathlib import Path

files = sorted(
    Path("data").glob("orders_*.csv")
)
```

Before reading, predict:

```text
Which files match?
In what deterministic order?
Do all files have the same schema?
```

# 43. Performance Reasoning

I/O performance is a system problem.

Think of total time as:

```text
I/O time
+
parsing time
+
conversion time
+
memory allocation
+
decompression
+
downstream processing
```

For remote sources, add:

```text
network transfer
latency
authentication/setup
```

For databases:

```text
query execution
database serialization
network transfer
```

For Parquet:

```text
file access
column decoding
filtering
materialization
```

## Benchmark correctly

When comparing readers, control:

```text
same input
same columns
same machine
same storage
same workload
```

Measure:

```python
from time import perf_counter

start = perf_counter()

df = pd.read_csv(
    "orders.csv",
)

elapsed = perf_counter() - start

print(elapsed)
```

For memory:

```python
print(
    df.memory_usage(deep=True).sum()
)
```

## Performance questions

```text
Can I read fewer columns?
Can I filter earlier?
Can I use Parquet for recurring analytical reads?
Can I reduce unnecessary dtype widening?
Is compression reducing network cost?
Is decompression CPU now the bottleneck?
Is the parser engine appropriate?
```

Do not optimize because an option "sounds faster."

Measure.

# 44. Memory Reasoning

A DataFrame consumes memory after parsing.

A useful principle is:

```text
smaller source file
≠
smaller in-memory DataFrame
```

A compressed CSV can be small on disk and expand substantially in memory.

## Early column pruning

CSV:

```python
df = pd.read_csv(
    "orders.csv",
    usecols=[
        "order_id",
        "amount",
    ],
)
```

Parquet:

```python
df = pd.read_parquet(
    "orders.parquet",
    columns=[
        "order_id",
        "amount",
    ],
    engine="pyarrow",
)
```

## Intentional types

```python
df = pd.read_csv(
    "orders.csv",
    dtype={
        "order_id": "string",
        "quantity": "Int64",
    },
)
```

The type chosen for a column affects correctness and later memory use.

## Schema-aware ingestion

Prefer:

```text
read required columns
→ read with intended types
→ validate
→ transform
```

over:

```text
read every column
→ infer everything
→ transform
→ drop most columns
```

Topic 13 later expands this into full chunked memory reduction.

# 45. Production Data Engineering Applications

## API and file ingestion

```text
API / file
   ↓
pandas reader
   ↓
reader contract
   ↓
validation
```

## Bronze ingestion

The goal is often source fidelity:

```text
source
   ↓
read with documented configuration
   ↓
durable raw representation
   ↓
record source metadata
```

Do not silently clean values before understanding their semantics.

## Silver transformation

After ingestion, enforce:

```text
schema
missing-value semantics
identifier representation
timestamp interpretation
quality rules
```

## Data lake ingestion

A common transition is:

```text
CSV / JSON / Excel
    ↓
validated pandas DataFrame
    ↓
Parquet
```

## Reporting exports

Humans may need:

```text
CSV
Excel
```

The output should still have a stable schema.

## Database integration

Pandas can bridge:

```text
SQL
 ↕
DataFrame
 ↕
files
```

## Reconciliation

A strong ingestion process can record:

```text
source rows
read rows
rejected rows
output rows
```

and, where meaningful:

```text
input totals
output totals
```

This is where I/O meets data quality.

# 46. Format-Selection Decision Framework

A practical starting point:

```text
Need human editing?
    ↓
Excel / CSV

Need simple record interchange?
    ↓
CSV / JSONL

Need analytical typed storage?
    ↓
Parquet

Need database-managed data?
    ↓
SQL
```

Format choice also depends on:

- source and consumer;
- scale;
- schema stability;
- query patterns;
- storage;
- compression;
- interoperability;
- operational constraints.

## Example — vendor CSV

```text
vendor produces CSV
large daily volume
```

Use a strict CSV reader contract, validate, and convert to a more analytical format where appropriate.

## Example — analytics data lake

```text
large typed data
repeated selective reads
```

Parquet is aligned with this access pattern.

## Example — operational database

```text
database owns current state
```

Read through SQL rather than exporting everything to CSV simply because pandas can read files.

# 47. Common Mistakes

## Mistake 1 — Relying on type inference in production

Broken:

```python
df = pd.read_csv("orders.csv")
```

Better:

```python
df = pd.read_csv(
    "orders.csv",
    dtype={
        "order_id": "string",
    },
)
```

Prevention: maintain a reader contract.

## Mistake 2 — Writing the DataFrame index into CSV accidentally

Broken:

```python
df.to_csv("orders.csv")
```

Better:

```python
df.to_csv(
    "orders.csv",
    index=False,
)
```

## Mistake 3 — Mixing date formats silently

Use explicit known formats:

```python
date_format="%d/%m/%Y"
```

## Mistake 4 — Leaving half-written output files after a crash

Write to a temporary path and finalize intentionally.

## Mistake 5 — Losing leading zeros

Use string dtypes for identifiers.

## Mistake 6 — Treating legitimate `"NA"` as missing

Use `keep_default_na=False` when source semantics require it.

## Mistake 7 — Silently skipping malformed rows

Record rejected-row counts and causes.

## Mistake 8 — Assuming daily files share one schema

Validate before concatenation.

## Mistake 9 — Reading every Parquet column

Use `columns=` at read time.

## Mistake 10 — Assuming PyArrow is always faster

Benchmark under the real workload.

## Mistake 11 — Assuming Parquet preserves every DataFrame property exactly

Use round-trip tests.

## Mistake 12 — Using SQL append without thinking about retries

Define idempotency separately from the pandas write call.

## Mistake 13 — Using huge SQL chunks without measurement

Benchmark batch size.

## Mistake 14 — Treating `pd.concat()` as schema validation

Combining frames does not prove source compatibility.

# 48. Checkpoint

Do not move on until you can answer these without looking at the chapter.

## Core understanding

- Why is reading a source a schema/data-quality operation?
- Why can CSV parsing corrupt identifiers?
- Why does Parquet preserve types more effectively than CSV?
- When is Excel a reasonable input?

## CSV

- What does `sep` control?
- What happens with `header=None`?
- When do you use `names=`?
- Why is `usecols` useful?
- Why is `index=False` commonly used for tabular CSV outputs?
- Why can encoding errors occur?
- What is the trade-off introduced by compression?

## JSON Lines

- What does `lines=True` mean?
- What does `orient="records"` mean?
- Why is JSONL convenient for APIs and records?

## Schema

- Why is `dtype=` important?
- Why should many IDs be strings?
- What problem does `parse_dates` solve?
- Why does `date_format=` matter for ambiguous dates?
- When should `na_values` be used?
- What does `keep_default_na=False` protect you from?

## Bad input

- What problem does `on_bad_lines` address?
- Why is skipping a malformed row a data-quality event?
- Why can quoting change the interpreted column count?
- What are thousands and decimal separators?
- What is a BOM?

## SQL

- What does `read_sql()` do?
- What does `to_sql()` do?
- What is `chunksize`?
- Why might `method="multi"` help?
- Why does `append` not automatically mean idempotent?

## Parquet

- What is column pruning?
- What are Parquet filters?
- What does `partition_cols` do?
- Why should partition columns reflect access patterns?

## Reliability

- Why use deterministic column order?
- Why validate an output schema before writing?
- Why test write → read → compare?
- Why might CSV round trips require an explicit read contract?
- Why are temporary-path finalization patterns useful?

# 49. Final Mental Model

Use this hierarchy whenever you build a pandas ingestion step:

```text
SOURCE
  ↓
FORMAT IDENTIFICATION
  ↓
READER CONFIGURATION
  ↓
EXPLICIT SCHEMA
  ↓
MISSING-VALUE POLICY
  ↓
IDENTIFIER / TIMESTAMP PRESERVATION
  ↓
MALFORMED-INPUT POLICY
  ↓
DATAFRAME
  ↓
VALIDATION
  ↓
TRANSFORMATION
  ↓
EXPLICIT OUTPUT SCHEMA
  ↓
RELIABLE WRITE
  ↓
ROUND-TRIP TEST
```

## Production checklist

Before reading a production source, ask:

```text
1. What format is this?

2. What is the expected schema?

3. Which columns must remain strings?

4. Which columns are dates?

5. What tokens mean missing?

6. Which strings must NOT become missing?

7. What encoding is used?

8. How should malformed rows be handled?

9. Can I read only required columns?

10. Does the output format preserve the required types?

11. Is the output schema deterministic?

12. Can the write fail partially?

13. How will I verify the round trip?

14. How will I measure runtime and memory?
```

That list is a practical ingestion contract in miniature.

# 50. Connection to Topic 03

The module dependency is:

```text
01 Series / DataFrame / Index
            ↓
02 Reading and writing data sources
            ↓
03 Selection with loc / iloc / query
```

Topic 01 taught what a DataFrame and Index mean.

Topic 02 teaches how external data becomes that DataFrame while preserving its intended schema and semantics.

Topic 03 will use the resulting DataFrame to select exactly the rows and columns needed for transformation.

The dependency is:

```text
understand the object
        ↓
read it correctly
        ↓
select from it precisely
```

Do not treat these as disconnected pandas APIs. They are stages of the same engineering model.

# Code Quality Requirements

All examples are written for the pandas 3.x learning path in the roadmap.

They should:

- use clear variable names;
- prefer explicit configuration over hidden assumptions;
- use deterministic data whenever exact results are discussed;
- include assertions for important invariants;
- avoid unnecessary libraries;
- make source semantics visible in code.

Typical imports:

```python
import pandas as pd
```

When needed:

```python
import numpy as np
```

For SQLAlchemy examples:

```python
from sqlalchemy import create_engine
```

## Version-aware behavior

This chapter uses pandas 3.x as the primary reference.

Pandas 3.x also includes major behavior changes outside this topic, including Copy-on-Write and the default dedicated string dtype. Those are covered in their dedicated module topics rather than re-taught here.

# Technical Accuracy Notes

## CSV

CSV is text-based and does not inherently preserve pandas dtype semantics. Important type decisions therefore belong in the reader contract.

## Parquet

Parquet carries stronger schema/type information than CSV and is designed for analytical workloads, but round-trip requirements should still be tested.

## `dtype=`

Explicit dtypes reduce dangerous inference and make ingestion reproducible.

## `keep_default_na=False`

Use it when default textual NA-token interpretation conflicts with source semantics. Pair it with source-specific `na_values` where appropriate.

## Identifiers

Do not classify an identifier as numeric solely because it contains digits.

## `parse_dates`

Use explicit date parsing when the source format is known. Avoid making ambiguous date meaning implicit.

## Excel

Merged cells and presentation-oriented layouts can complicate ingestion.

## `on_bad_lines`

Skipping malformed rows is a policy choice, not a neutral technical detail.

## PyArrow CSV engine

It can be advantageous for supported workloads, but benchmark it under actual data and hardware.

## `dtype_backend`

Backend selection changes underlying column representation and can influence nullability, interoperability, and downstream behavior.

## Parquet filters

Filters can help the backend avoid unnecessary materialization depending on layout and engine behavior. They are not a universal promise of zero irrelevant I/O.

## Partitioning

Partition for meaningful access patterns. Avoid designs that create excessive small files or extreme partition counts.

## Reliable writes

Temporary-path plus finalization is a useful local-file pattern. Object storage has different publication semantics.

## Round-trip testing

Test actual contract requirements: values, columns, index, dtypes, null semantics, and ordering when those properties matter.

# Required Visual Explanations

## Reader contract

```text
Source
  ↓
Reader configuration
  ↓
Schema
  ↓
Null policy
  ↓
Date policy
  ↓
Malformed-row policy
  ↓
Validated DataFrame
```

## CSV type-loss example

```text
CSV text
"00123"
    ↓ type inference
123
    ↓
identifier meaning changed
```

With an explicit string contract:

```text
CSV text
"00123"
    ↓ dtype="string"
"00123"
    ↓
identifier preserved
```

## Format comparison

```text
CSV
→ text
→ flexible
→ weak schema preservation

JSONL
→ record-oriented
→ API/log friendly

Parquet
→ columnar
→ typed
→ analytical
```

## Reliable write

```text
DataFrame
   ↓
temporary output
   ↓
validation
   ↓
final rename / publish
```

## Round trip

```text
DataFrame
   ↓
write
   ↓
file
   ↓
read
   ↓
DataFrame
   ↓
assert_frame_equal
```

# Depth Requirement

For every major concept in this chapter, build the learner through:

```text
What is it?
↓
Why does it exist?
↓
How does it work?
↓
Simple example
↓
Code
↓
Expected result
↓
Explanation
↓
Data Engineering use case
↓
Common mistake
↓
Production consideration
```

The learner should be able to study this topic directly from this Markdown file without relying on another beginner pandas I/O tutorial.

# Final Module Integration

This chapter sits between the object model of Topic 01 and the selection mechanics of Topic 03.

```text
Topic 01
→ understand Series / DataFrame / Index

Topic 02
→ bring external data into those objects correctly

Topic 03
→ select and assign precisely
```

A useful production principle is:

> **Bad input cannot be repaired reliably by clever downstream transformations if its meaning was already lost at ingestion.**

# Production I/O Rule: Reliable Writing

Reliable writing means **reliable writing and reliable output publication**, not merely successfully calling `to_csv()` or `to_parquet()`.

```text
validate schema
→ write temporary path
→ validate the produced artifact where appropriate
→ finalize / publish
→ verify the output
```

The exact finalization mechanism depends on the storage system, but the engineering objective remains the same: downstream consumers should not mistake an incomplete artifact for a valid production output.
