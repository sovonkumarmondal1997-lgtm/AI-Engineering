# Command-Line Data Tools: jq, csvkit, Miller, and DuckDB CLI

> **Stage 2B — Gap Module G2: Linux and Shell for Data Servers**  
> **Topic 08:** Command-line data tools: `jq`, `csvkit`, Miller, and DuckDB CLI  
> **Learning loop:** Read → Do → Make it repeatable → Break it → Diagnose from evidence → Fix → Document → Explain aloud

---

## 1. Why Command-Line Data Tools Matter

A Data Engineer working on a Linux server frequently needs to answer questions such as:

```text
What fields are in this API response?
Which records failed?
How many events arrived today?
Which countries are present?
Why is this partner CSV malformed?
What is the total revenue?
What is the schema of this Parquet file?
Can I convert this CSV to Parquet without writing Python?
```

For many of these questions, writing a full Python program is unnecessary.

A good command-line workflow can be:

```text
inspect
→ profile
→ filter
→ transform
→ aggregate
→ validate
→ decide
```

The goal of this topic is **not** to turn every problem into a one-liner.

The goal is to make you capable of choosing the smallest tool that correctly answers the question.

### The professional question

Do not ask:

> "Which command do I remember?"

Ask:

> "What data structure do I have, what question am I asking, and which tool understands that structure best?"

---

# 2. Where These Tools Fit in Data Engineering

The tools in this topic have different strengths.

| Tool | Primary strength | Typical format |
|---|---|---|
| `jq` | JSON inspection/transformation | JSON/JSONL |
| `csvkit` | CSV inspection/profile/conversion | CSV/JSON/Excel |
| Miller (`mlr`) | record-oriented filtering/transformation/aggregation | CSV/TSV/JSON |
| DuckDB CLI | SQL analytics directly over files | CSV/JSON/Parquet |
| GNU `parallel` | independent work across many inputs | any command |
| Python | reusable/complex/testable workflows | anything with suitable libraries |

A useful mental model is:

```text
jq
  ↓
Understand and reshape JSON

csvkit
  ↓
Inspect and profile CSV

Miller
  ↓
Transform and aggregate named records

DuckDB
  ↓
Ask analytical SQL questions over files

GNU parallel
  ↓
Run independent operations concurrently

Python
  ↓
Build complex, reusable, testable workflows
```

---

# 3. Structured Data vs Plain Text

Stage 0 teaches generic text tools such as:

```text
grep
cut
sed
awk
sort
uniq
```

Those tools remain valuable.

But structured formats contain semantics that simple text splitting does not understand.

## 3.1 CSV is not "just comma-separated text"

Consider:

```csv
customer_id,company,city
101,"Acme, Inc.","New York"
102,"Data Labs","Kolkata"
```

A naive:

```bash
cut -d, -f2 data.csv
```

can misunderstand the comma inside:

```text
"Acme, Inc."
```

A CSV-aware tool understands quoting and field boundaries.

## 3.2 JSON is hierarchical

Consider:

```json
{
  "customer": {
    "name": "Alice",
    "address": {
      "city": "Kolkata"
    }
  }
}
```

There is no meaningful equivalent of:

```text
field 1
field 2
field 3
```

The data has:

```text
object
 └── customer
      ├── name
      └── address
           └── city
```

A JSON-aware tool can traverse that structure.

## 3.3 Parquet is not line-oriented text

Parquet contains structured, typed, columnar data.

You should not approach it as:

```bash
grep ...
```

Instead use a tool that understands the format, such as DuckDB.

---

# 4. JSON Fundamentals

Before learning `jq`, understand what it processes.

JSON supports:

- objects;
- key/value pairs;
- arrays;
- strings;
- numbers;
- booleans;
- `null`;
- nested structures.

Example:

```json
{
  "id": 101,
  "customer": {
    "name": "Alice",
    "country": "IN"
  },
  "amount": 1250.50,
  "active": true,
  "items": [
    {
      "sku": "A100",
      "quantity": 2
    },
    {
      "sku": "B200",
      "quantity": 1
    }
  ]
}
```

Think of the structure as:

```text
object
├── id
├── customer
│   ├── name
│   └── country
├── amount
├── active
└── items
    ├── object
    └── object
```

Before writing a `jq` expression, identify:

```text
What is the root?
What are the objects?
Where are the arrays?
Which fields can be missing?
Which fields are numeric?
```

---

# 5. JSON Objects and Arrays

## 5.1 Object

An object contains named fields:

```json
{
  "id": 101,
  "country": "IN"
}
```

Conceptually:

```text
key → value
```

## 5.2 Array

An array contains multiple values:

```json
[
  "IN",
  "US",
  "GB"
]
```

An array can contain objects:

```json
[
  {"id": 1, "country": "IN"},
  {"id": 2, "country": "US"}
]
```

## 5.3 Nested array

Data APIs frequently return:

```json
{
  "orders": [
    {
      "id": 1,
      "items": [
        {"sku": "A", "qty": 2},
        {"sku": "B", "qty": 1}
      ]
    }
  ]
}
```

The data shape matters.

```text
orders
  ↓
array
  ↓
order object
  ↓
items
  ↓
array
  ↓
item object
```

---

# 6. JSON Lines / NDJSON

JSON Lines, often called JSONL or NDJSON, represents one JSON value per line.

Example:

```json
{"id":1,"event":"login","country":"IN"}
{"id":2,"event":"purchase","country":"US"}
{"id":3,"event":"logout","country":"IN"}
```

This differs from one large JSON array:

```json
[
  {"id":1},
  {"id":2},
  {"id":3}
]
```

## Why JSONL matters

JSONL is useful for:

- event streams;
- logs;
- API exports;
- ingestion pipelines;
- batch processing;
- incremental processing.

A large JSONL file can be processed record by record more naturally than one enormous nested document.

---

# 7. API Responses and Pagination

A common Data Engineering workflow is:

```text
API
 ↓
JSON response
 ↓
inspect
 ↓
extract records
 ↓
flatten
 ↓
validate
 ↓
store
```

A response might look like:

```json
{
  "page": 1,
  "next_page": 2,
  "items": [
    {
      "id": 101,
      "customer": {
        "name": "Alice",
        "country": "IN"
      }
    },
    {
      "id": 102,
      "customer": {
        "name": "Bob",
        "country": "US"
      }
    }
  ]
}
```

You may need:

```text
.items[]
```

rather than processing the whole response.

Pagination belongs to the broader ingestion workflow, but command-line tools are excellent for inspecting and validating saved API responses.

---

# 8. jq Fundamentals

`jq` is a command-line JSON processor.

Start with:

```bash
jq .
```

Given:

```json
{"id":101,"country":"IN"}
```

it produces formatted JSON:

```json
{
  "id": 101,
  "country": "IN"
}
```

The important model is:

```text
JSON input
   ↓
jq filter/expression
   ↓
JSON output
```

---

# 9. jq Pretty-Printing

Pretty-printing is useful during incident investigation.

```bash
jq . response.json
```

For a nested document:

```bash
jq . response.json
```

makes the hierarchy visible.

This is often the first step:

```text
What is this payload?
```

before:

```text
How do I transform it?
```

---

# 10. jq Field Selection

For:

```json
{
  "id": 101,
  "customer": {
    "name": "Alice",
    "country": "IN"
  }
}
```

select:

```bash
jq '.id' response.json
```

Output:

```text
101
```

Select a nested field:

```bash
jq '.customer.name' response.json
```

Output:

```text
"Alice"
```

Select country:

```bash
jq '.customer.country' response.json
```

The syntax:

```text
.customer.name
```

means:

```text
root
 → customer
 → name
```

---

# 11. jq Arrays

For:

```json
{
  "items": [
    {"sku": "A100", "quantity": 2},
    {"sku": "B200", "quantity": 1}
  ]
}
```

select the array:

```bash
jq '.items' response.json
```

Select each element:

```bash
jq '.items[]' response.json
```

Select a field from each object:

```bash
jq '.items[].sku' response.json
```

Output:

```text
"A100"
"B200"
```

The `[]` operation means:

```text
iterate over array elements
```

---

# 12. jq `select` Filtering

Filtering is one of the most important `jq` skills.

For JSONL:

```json
{"id":1,"status":"success","amount":500}
{"id":2,"status":"failed","amount":900}
{"id":3,"status":"success","amount":1500}
```

Filter successful records:

```bash
jq 'select(.status == "success")' events.jsonl
```

Filter by amount:

```bash
jq 'select(.amount > 1000)' events.jsonl
```

Combine conditions:

```bash
jq 'select(.status == "success" and .amount > 1000)' events.jsonl
```

Alternative:

```bash
jq 'select(.country == "IN" or .country == "US")' events.jsonl
```

The mental model is:

```text
each input record
       ↓
evaluate condition
       ↓
true → emit
false → discard
```

---

# 13. jq Mapping Arrays

Suppose:

```json
{
  "items": [
    {"sku": "A100", "quantity": 2},
    {"sku": "B200", "quantity": 1}
  ]
}
```

Extract all SKUs:

```bash
jq '.items | map(.sku)' response.json
```

Output:

```json
[
  "A100",
  "B200"
]
```

The mental model:

```text
array
 ↓
map
 ↓
apply expression to every element
 ↓
new array
```

---

# 14. jq Raw Output — `-r`

Without `-r`:

```bash
jq '.customer.name' response.json
```

may produce:

```text
"Alice"
```

With:

```bash
jq -r '.customer.name' response.json
```

the output is:

```text
Alice
```

Raw output is useful when piping into:

```text
shell commands
scripts
CSV generation
other programs
```

For example:

```bash
jq -r '.customer.name' response.json | sort
```

---

# 15. jq Compact Output — `-c`

Pretty JSON:

```bash
jq '.'
```

Compact JSON:

```bash
jq -c '.'
```

For JSONL-oriented workflows, compact output is useful:

```bash
jq -c '.items[]' response.json
```

The difference is:

```text
pretty
→ optimized for humans

compact
→ optimized for machine-oriented pipelines
```

---

# 16. jq Transformations

You can construct a new object.

Input:

```json
{
  "id": 101,
  "customer": {
    "name": "Alice",
    "country": "IN"
  },
  "amount": 1250
}
```

Command:

```bash
jq '{
  id: .id,
  customer_name: .customer.name,
  country: .customer.country,
  amount: .amount
}' response.json
```

Output:

```json
{
  "id": 101,
  "customer_name": "Alice",
  "country": "IN",
  "amount": 1250
}
```

This is useful when an API schema does not match the schema required downstream.

---

# 17. Building Calculated Fields

Suppose:

```json
{
  "quantity": 3,
  "unit_price": 25
}
```

Create revenue:

```bash
jq '{quantity, unit_price, revenue: (.quantity * .unit_price)}' order.json
```

Output:

```json
{
  "quantity": 3,
  "unit_price": 25,
  "revenue": 75
}
```

The key idea is:

```text
source fields
    ↓
derived field
```

This is appropriate for simple transformations.

Complex business rules should generally move toward Python or a proper transformation layer.

---

# 18. Missing Fields and Nulls

Production API payloads are rarely perfect.

These are different concepts:

```text
missing field
null
empty string
zero
false
```

Example:

```json
{"id":1,"country":"IN"}
{"id":2,"country":null}
{"id":3}
{"id":4,"country":""}
```

Do not treat them as automatically equivalent.

## 18.1 Default values

A useful jq pattern is:

```bash
jq '.country // "UNKNOWN"' data.jsonl
```

This can provide a fallback for null/missing-like values.

## 18.2 Explicit null check

```bash
jq 'select(.country == null)' data.jsonl
```

Use this when investigating missingness.

## 18.3 Why this matters

If you silently replace:

```text
null
```

with:

```text
UNKNOWN
```

you have changed the data semantics.

Document intentional normalization.

---

# 19. Grouping and Aggregation with jq

For JSONL:

```json
{"country":"IN","amount":100}
{"country":"IN","amount":250}
{"country":"US","amount":300}
```

A common conceptual operation is:

```text
group by country
→ sum amount
```

One approach is:

```bash
jq -s '
  group_by(.country)
  | map({
      country: .[0].country,
      total: (map(.amount) | add)
    })
' orders.jsonl
```

The `-s` option slurps inputs into an array before processing.

This is powerful, but it changes the memory model.

For very large JSONL datasets, do not blindly use `-s`.

Prefer a streaming-capable approach or DuckDB when the analytical question is large enough to justify it.

---

# 20. JSON to CSV with jq

A common requirement is:

```text
JSON
 ↓
select/reshape
 ↓
CSV
```

For:

```json
{"id":1,"country":"IN","revenue":100}
{"id":2,"country":"US","revenue":200}
```

you can use:

```bash
jq -r '[.id, .country, .revenue] | @csv' orders.jsonl
```

Output:

```csv
1,"IN",100
2,"US",200
```

For production output, handle headers separately:

```bash
{
  printf '%s\n' 'id,country,revenue'
  jq -r '[.id, .country, .revenue] | @csv' orders.jsonl
} > orders.csv
```

The `@csv` formatter handles CSV quoting more safely than manually joining fields with commas.

---

# 21. Very Large JSON and jq Streaming

A large JSON document can exceed comfortable memory limits if processed naively.

Conceptually:

```text
2 GB JSON
 ↓
naive whole-document processing
 ↓
large memory footprint
```

`jq` provides streaming-related capabilities, including:

```bash
jq --stream
```

Streaming mode changes the shape of the input delivered to the filter. It is powerful but more complex than ordinary jq expressions.

The key lesson is not:

> "Always use `--stream`."

It is:

> Choose the processing model based on dataset size, structure, operation, and memory constraints.

For analytical questions over large JSON/JSONL, DuckDB's JSON reader may be easier than constructing a complex streaming jq program.

---

# 22. csvkit Overview

`csvkit` provides CSV-aware command-line utilities.

Important tools include:

```text
csvlook
csvcut
csvgrep
csvstat
```

It also includes conversion utilities for formats such as Excel and JSON.

The mental model:

```text
CSV
 ↓
csvkit
 ↓
inspect
profile
select
filter
convert
```

---

# 23. csvlook

Quickly inspect a CSV:

```bash
csvlook orders.csv
```

This helps you understand:

```text
headers
columns
row structure
quoted values
obvious anomalies
```

Use it early when receiving an unfamiliar CSV.

---

# 24. csvcut

List columns:

```bash
csvcut -n orders.csv
```

Select named columns:

```bash
csvcut -c customer_id,country,revenue orders.csv
```

The advantage is that the command is explicitly CSV-aware.

This is preferable to assuming:

```text
column 3 always means revenue
```

when named fields are available.

---

# 25. csvgrep

Filter CSV records.

Example:

```bash
csvgrep -c country -m IN orders.csv
```

Conceptually:

```text
country column
+
matching value IN
=
matching records
```

It is useful for simple filtering.

For more expressive record transformations, Miller may be a better choice.

---

# 26. csvstat

Profile a CSV:

```bash
csvstat orders.csv
```

This can provide useful information about:

- columns;
- inferred types;
- counts;
- numeric summaries;
- missingness/uniqueness-related statistics depending on data and version.

Use it when validating an unfamiliar partner file.

A useful workflow:

```text
csvlook
 ↓
csvstat
 ↓
identify suspicious columns
 ↓
csvcut/csvgrep/mlr
```

---

# 27. csvkit Conversion

csvkit also provides tools for conversion workflows.

Examples include utilities for working with:

```text
CSV
JSON
Excel
```

A typical workflow is:

```text
partner.xlsx
    ↓
convert
    ↓
partner.csv
    ↓
csvstat
    ↓
validate
```

Conversion is not validation.

Always inspect the converted data before trusting it.

---

# 28. Messy CSV Handling

A partner CSV might contain:

```csv
order_id,country,revenue
1001,IN,1000
1002,US,not_available
1003,"IN",1250
1004,,900
```

Questions include:

```text
Is revenue numeric?
How many country values are missing?
Are quoted values equivalent?
Which records are invalid?
```

Start with:

```bash
csvlook partner.csv
csvstat partner.csv
csvcut -n partner.csv
```

Then narrow:

```bash
csvcut -c order_id,country,revenue partner.csv
```

For richer transformations, move to Miller.

---

# 29. Miller Fundamentals

Miller (`mlr`) is a command-line tool designed around named records and fields.

It is especially useful when you need to:

```text
filter
sort
aggregate
join
convert
```

structured records.

A simplified mental model:

```text
record
├── customer_id
├── country
├── revenue
└── event_date
```

Miller operates on named fields rather than treating the record as anonymous comma-separated text.

---

# 30. Miller Filtering

A typical Miller filter:

```bash
mlr --csv filter '$revenue > 1000' orders.csv
```

Another:

```bash
mlr --csv filter '$country == "IN"' orders.csv
```

Multiple conditions:

```bash
mlr --csv filter '$country == "IN" && $revenue > 1000' orders.csv
```

The learner should understand:

```text
$revenue
```

means a named field.

Do not memorize syntax without understanding the record model.

---

# 31. Miller Sorting

Sort by a field:

```bash
mlr --csv sort -f revenue orders.csv
```

Descending order can be expressed with Miller's sorting options.

For example:

```bash
mlr --csv sort -nr revenue orders.csv
```

Sorting large datasets can have substantial CPU, memory, and temporary-storage implications.

Connect this to Topic 07:

```text
large sort
→ resource consumption
→ possible temporary disk use
```

---

# 32. Miller Aggregation with `stats1`

Miller can perform grouped statistics.

A common pattern is:

```bash
mlr --csv stats1 -a sum -f revenue -g country orders.csv
```

Conceptually:

```text
group by country
→ sum revenue
```

For counts:

```bash
mlr --csv stats1 -a count -f order_id -g country orders.csv
```

The exact available aggregators/options depend on the installed Miller version, so use:

```bash
mlr --help
```

for the environment's authoritative syntax.

---

# 33. Miller Joins

Suppose:

```text
customers.csv
orders.csv
```

and both contain:

```text
customer_id
```

A join conceptually means:

```text
customers
   +
orders
   ↓
match on customer_id
```

Miller supports join operations.

Before joining, inspect:

```text
key uniqueness
missing keys
data types
expected cardinality
```

A join can be technically successful while semantically wrong.

For example:

```text
duplicate customer_id
```

may multiply records.

The lesson is:

> Validate the join key before trusting the join result.

---

# 34. Miller Format Conversion

Miller can work across structured record formats such as:

```text
CSV
TSV
JSON
```

A workflow might be:

```text
CSV
 ↓
filter
 ↓
transform
 ↓
JSON
```

or:

```text
JSON
 ↓
normalize
 ↓
CSV
```

This is useful when moving between tools.

---

# 35. DuckDB CLI Fundamentals

DuckDB provides an analytical SQL engine that can query files directly.

Start:

```bash
duckdb
```

Then:

```sql
SELECT 1;
```

The key mental model is:

```text
file
 ↓
DuckDB reader
 ↓
SQL
 ↓
result
```

You do not necessarily need to load the entire dataset into a database first.

---

# 36. Querying CSV with DuckDB

Query a CSV directly:

```sql
SELECT *
FROM 'orders.csv'
LIMIT 10;
```

Aggregate:

```sql
SELECT
    country,
    SUM(revenue) AS total_revenue
FROM 'orders.csv'
GROUP BY country
ORDER BY total_revenue DESC;
```

This is where DuckDB becomes particularly useful:

```text
structured file
+
SQL
+
analytical engine
```

---

# 37. Querying JSON with DuckDB

DuckDB can read JSON/JSONL using its JSON functionality.

For example, depending on the installed DuckDB version and file structure:

```sql
SELECT *
FROM read_json_auto('events.jsonl')
LIMIT 10;
```

Or use the JSON table function appropriate to the installed version.

Always verify available functions with DuckDB help/documentation in the environment.

The comparison is:

```text
jq
→ explicit JSON transformations

DuckDB
→ SQL-oriented analytical questions
```

---

# 38. Querying Parquet

DuckDB can query Parquet directly:

```sql
SELECT *
FROM 'orders.parquet'
LIMIT 10;
```

Aggregate:

```sql
SELECT
    country,
    SUM(revenue) AS total_revenue
FROM 'orders.parquet'
GROUP BY country;
```

This makes DuckDB extremely useful for server-side inspection of analytical datasets.

---

# 39. Sampling Data

Do not scan a multi-gigabyte dataset unnecessarily just to understand its shape.

Start with:

```sql
SELECT *
FROM 'orders.parquet'
LIMIT 20;
```

For a quick random sample, depending on the workflow:

```sql
SELECT *
FROM 'orders.parquet'
USING SAMPLE 1000 ROWS;
```

The exact sampling syntax should be verified against the installed DuckDB version.

The principle is:

```text
inspection
≠
full analysis
```

---

# 40. Schema Inspection

Before running analysis, inspect the schema.

Examples include:

```sql
DESCRIBE SELECT *
FROM 'orders.csv';
```

For Parquet:

```sql
DESCRIBE SELECT *
FROM 'orders.parquet';
```

You can also inspect a relation's columns through DuckDB's metadata facilities.

The questions are:

```text
What columns exist?
What types were inferred?
Are numeric columns actually numeric?
Are dates typed correctly?
```

Schema inference should be verified rather than blindly trusted.

---

# 41. SQL Analytics Over Files

Common operations:

```sql
SELECT
WHERE
GROUP BY
ORDER BY
LIMIT
```

Common aggregates:

```sql
COUNT(*)
SUM(revenue)
AVG(revenue)
MIN(revenue)
MAX(revenue)
```

Example:

```sql
SELECT
    country,
    COUNT(*) AS orders,
    SUM(revenue) AS revenue,
    AVG(revenue) AS average_order
FROM 'orders.csv'
WHERE revenue IS NOT NULL
GROUP BY country
ORDER BY revenue DESC;
```

This is often much clearer than constructing a long shell pipeline.

---

# 42. File-to-File Transformations

DuckDB can act as a file transformation engine.

Conceptually:

```text
CSV
 ↓
read
 ↓
SQL transformation
 ↓
Parquet
```

or:

```text
JSON
 ↓
read
 ↓
normalize/filter
 ↓
Parquet
```

This is often preferable to writing a custom script for a simple analytical conversion.

---

# 43. CSV to Parquet

A common pattern is:

```sql
COPY (
    SELECT *
    FROM 'orders.csv'
)
TO 'orders.parquet'
(FORMAT PARQUET);
```

You can transform while converting:

```sql
COPY (
    SELECT
        order_id,
        country,
        CAST(revenue AS DOUBLE) AS revenue
    FROM 'orders.csv'
)
TO 'orders.parquet'
(FORMAT PARQUET);
```

This makes the workflow:

```text
CSV
→ infer/read
→ transform
→ type/validate
→ Parquet
```

---

# 44. Partitioned Parquet

Partitioning can organize output by a field.

Conceptually:

```text
orders/
├── country=IN/
├── country=US/
└── country=GB/
```

DuckDB can write partitioned Parquet using an appropriate partitioned-output workflow, for example:

```sql
COPY (
    SELECT *
    FROM 'orders.csv'
)
TO 'orders_partitioned'
(FORMAT PARQUET, PARTITION_BY (country));
```

Syntax and behavior should be checked against the installed DuckDB version.

## Choosing a partition key

A good partition key should generally:

- have useful query selectivity;
- avoid extreme cardinality;
- be stable;
- align with common access patterns.

Bad partitioning can produce:

```text
too many tiny files
```

which connects directly to Topic 07's inode and small-file concerns.

---

# 45. DuckDB and Large Files

DuckDB is useful for large file analytics because it can execute analytical operations directly over files.

Still, large does not mean:

```text
"ignore resource usage."
```

Monitor:

```text
memory
CPU
disk I/O
temporary storage
```

especially for:

```text
large joins
sorts
aggregations
conversions
```

Connect this to Topic 06:

```text
resource monitoring
```

and Topic 07:

```text
disk/inode management
```

---

# 46. Same Dataset — Multi-Tool Comparison

Use one logical dataset in multiple representations:

```text
orders.csv
orders.jsonl
orders.parquet
```

Ask:

1. How many records?
2. What countries exist?
3. What is total revenue?
4. Which country has the most revenue?
5. Which records have missing/invalid values?

A useful decision table:

| Task | jq | csvkit | Miller | DuckDB | Python |
|---|---|---|---|---|---|
| JSON inspection | Excellent | Limited | Good | Good | Excellent |
| CSV inspection | No | Excellent | Good | Good | Excellent |
| Simple row filtering | Excellent for JSON | Good | Excellent | Excellent | Excellent |
| JSON transformation | Excellent | Limited | Good | Good | Excellent |
| CSV profiling | No | Excellent | Good | Excellent | Excellent |
| Record aggregation | Good | Limited | Excellent | Excellent | Excellent |
| Joins | Possible/awkward | Limited | Good | Excellent | Excellent |
| Parquet analytics | No | No | Limited | Excellent | Excellent |
| SQL analytics | No | No | No | Excellent | Excellent |
| Complex reusable logic | Poor fit | Poor fit | Moderate | Moderate | Excellent |

The table is not a ranking.

It is a decision aid.

---

# 47. Tool-Selection Framework

Use this decision model:

```text
Quick JSON inspection
→ jq

Quick CSV inspection/profile
→ csvlook / csvstat

Select CSV columns
→ csvcut

Simple CSV filtering
→ csvgrep

Record-oriented filtering/transformation
→ Miller

Grouped record aggregation
→ Miller

Analytical question
→ DuckDB

CSV / JSON / Parquet analytics
→ DuckDB

Many independent files
→ GNU parallel

Complex reusable workflow
→ Python
```

The best tool is the simplest one that:

```text
understands the data
+
produces correct results
+
is readable
+
is reproducible
+
fits the scale
```

---

# 48. jq vs csvkit vs Miller vs DuckDB vs Python

## Use jq when

```text
data is JSON
structure matters
you need extraction/transformation
```

## Use csvkit when

```text
data is CSV
you need quick inspection/profile/selection
```

## Use Miller when

```text
records have named fields
you need filtering/sorting/aggregation/joining
```

## Use DuckDB when

```text
the question is analytical
SQL makes the logic clearer
data is CSV/JSON/Parquet
```

## Use Python when

```text
logic is complex
workflow is reusable
tests are needed
error handling is substantial
external APIs/state are involved
```

---

# 49. Very Large JSON

For very large JSON, evaluate:

```text
file structure
operation
memory
CPU
I/O
required output
```

Possible strategies:

```text
JSONL
→ jq streaming/record processing

Large analytical JSON
→ DuckDB JSON reader

Complex reusable workflow
→ Python
```

Do not assume:

```text
jq = always memory efficient
DuckDB = always faster
Python = always slower
```

Benchmark representative workloads when performance matters.

---

# 50. GNU `parallel`

GNU `parallel` can run independent commands concurrently.

Conceptually:

```text
500 independent files
        ↓
process each file
        ↓
parallel workers
        ↓
aggregate results
```

Example:

```bash
parallel -j 4 'jq -r ".event_type" {} | sort | uniq -c > {.}.counts' ::: data/*.jsonl
```

The exact command should be tested on a small sample before scaling it.

## Concurrency is a resource decision

More workers can mean:

```text
higher throughput
```

but also:

```text
more CPU
more memory
more disk I/O
more open files
more output contention
```

Start conservatively:

```bash
parallel -j 2 ...
```

Then increase only after observing the server.

---

# 51. Parallel Processing Across 500 JSONL Files

A practical pattern is:

```text
500 files
 ↓
each file independently count events
 ↓
write small result per file
 ↓
aggregate result files
```

This is safer than having every worker write to the same output simultaneously.

A better architecture:

```text
worker 1 → result-001
worker 2 → result-002
worker 3 → result-003
...
              ↓
          final merge
```

This reduces output coordination problems.

---

# 52. Rust-Based CSV Alternatives — Awareness

There are high-performance CSV/data command-line tools written in Rust.

Examples in the ecosystem include tools such as:

```text
xsv
qsv
```

Treat these as awareness rather than another full curriculum.

Evaluate alternatives when:

```text
CSV processing is a measurable bottleneck
```

not merely because:

```text
"Rust is faster."
```

Performance depends on:

```text
input
operation
CPU
storage
tool implementation
```

Benchmark representative data.

---

# 53. Reproducible One-Liners

A command that worked once is not necessarily a production workflow.

Bad:

```bash
jq ... | mlr ... | awk ... | sed ... | sort ... | ...
```

if nobody can explain it.

Better:

```text
exploratory command
        ↓
validated command
        ↓
documented command
        ↓
small script
        ↓
tested workflow
```

---

# 54. Turning One-Liners into Scripts

Use:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

Example:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="${1:?Usage: $0 orders.jsonl}"

# Keep only successful orders.
jq 'select(.status == "success")' "$INPUT"
```

Benefits:

```text
clear arguments
comments
error handling
repeatability
version control
```

A script is not automatically production-ready, but it is usually easier to reason about than an undocumented command copied from shell history.

---

# 55. When to Move to Python

Stay with command-line tools for:

```text
one-off inspection
simple filtering
small transformations
quick incident analysis
basic profiling
```

Move to Python when you need:

```text
complex business logic
many transformation stages
reusable functions
unit tests
structured error handling
API clients
state
configuration
complex schemas
integration with other systems
maintainability
```

The transition is:

```text
one-liner
→ script
→ Python module
→ pipeline/orchestrated workflow
```

Do not treat moving to Python as failure.

It is a complexity-management decision.

---

# 56. Readability Rule

Shorter is not automatically better.

Compare:

```text
200-character one-liner
```

with:

```text
5 clear commands
```

The second may be superior if it is:

```text
readable
debuggable
testable
documented
```

A production Data Engineer optimizes for:

```text
correctness
+
clarity
+
repeatability
```

not line-count minimization.

---

# 57. Hands-On `server_lab/08/`

Recommended structure:

```text
server_lab/
└── 08/
    ├── README.md
    ├── api/
    │   └── responses/
    ├── csv/
    │   ├── partner.csv
    │   └── cleaned/
    ├── jsonl/
    ├── parquet/
    ├── parallel/
    ├── scripts/
    └── runbook.md
```

Use synthetic or sanitized data.

Never place real secrets, credentials, customer PII, or production exports in the lab.

---

# 58. Lab 1 — API JSON → CSV with jq

Create or save a representative API response.

Example:

```json
{
  "page": 1,
  "items": [
    {
      "id": 101,
      "customer": {"name": "Alice", "country": "IN"},
      "amount": 1250
    },
    {
      "id": 102,
      "customer": {"name": "Bob", "country": "US"},
      "amount": 900
    }
  ]
}
```

Inspect:

```bash
jq . response.json
```

Extract records:

```bash
jq '.items[]' response.json
```

Build a flat object:

```bash
jq '.items[] | {
  id: .id,
  customer_name: .customer.name,
  country: .customer.country,
  amount: .amount
}' response.json
```

Produce CSV:

```bash
{
  printf '%s\n' 'id,customer_name,country,amount'
  jq -r '.items[] | [.id, .customer.name, .customer.country, .amount] | @csv' response.json
} > output.csv
```

Verify:

```bash
csvlook output.csv
csvstat output.csv
```

### Required skills

- nested extraction;
- arrays;
- mapping;
- missing/null handling;
- raw output;
- CSV encoding;
- validation.

---

# 59. Lab 2 — Messy Partner CSV

Create a deliberately imperfect file:

```csv
order_id,country,revenue
1001,IN,1000
1002,US,not_available
1003,"IN",1250
1004,,900
1005,GB,1800
```

Inspect:

```bash
csvlook partner.csv
```

Profile:

```bash
csvstat partner.csv
```

List columns:

```bash
csvcut -n partner.csv
```

Select:

```bash
csvcut -c order_id,country,revenue partner.csv
```

Filter:

```bash
csvgrep -c country -m IN partner.csv
```

Then use Miller for richer validation/transformation.

Document:

```text
What was invalid?
Why?
What was cleaned?
What was rejected?
```

---

# 60. Lab 3 — Miller vs DuckDB

Given:

```text
orders.csv
```

calculate revenue by country with Miller:

```bash
mlr --csv stats1 -a sum -f revenue -g country orders.csv
```

Then DuckDB:

```sql
SELECT
    country,
    SUM(revenue) AS total_revenue
FROM 'orders.csv'
GROUP BY country
ORDER BY total_revenue DESC;
```

Compare:

| Dimension | Miller | DuckDB |
|---|---|---|
| Syntax | record DSL | SQL |
| Quick stream transform | Excellent | Good |
| Aggregation | Excellent | Excellent |
| Multi-step analytical query | Moderate | Excellent |
| Parquet | Limited | Excellent |
| Familiarity for SQL users | Moderate | Excellent |

Verify that both produce the same totals.

---

# 61. Lab 4 — 5 GB CSV to Partitioned Parquet

> Use a disposable practice environment with enough storage headroom. Do not perform this lab on a constrained production root filesystem.

First inspect:

```sql
DESCRIBE SELECT *
FROM 'large.csv';
```

Sample:

```sql
SELECT *
FROM 'large.csv'
LIMIT 20;
```

Profile:

```sql
SELECT
    COUNT(*) AS rows,
    COUNT(DISTINCT country) AS countries,
    SUM(revenue) AS revenue
FROM 'large.csv';
```

Convert:

```sql
COPY (
    SELECT *
    FROM 'large.csv'
)
TO 'orders_parquet'
(FORMAT PARQUET, PARTITION_BY (country));
```

Inspect:

```bash
find orders_parquet -maxdepth 2 -type f | head
```

Query:

```sql
SELECT
    country,
    SUM(revenue) AS revenue
FROM 'orders_parquet/**/*.parquet'
GROUP BY country;
```

Observe:

```text
input size
output size
query behavior
number of files
partition layout
```

Connect this to Topic 07:

```text
partitioning
→ many files
→ inode/storage implications
```

---

# 62. Lab 5 — 500 JSONL Files in Parallel

Create 500 small synthetic JSONL files.

Each file can contain:

```json
{"event_type":"login"}
{"event_type":"purchase"}
{"event_type":"logout"}
```

Process independently:

```bash
mkdir -p results

parallel -j 4 '
  jq -r ".event_type" {} |
  sort |
  uniq -c > results/{/.}.counts
' ::: jsonl/*.jsonl
```

Aggregate the results afterward.

Measure resource impact:

```text
CPU
memory
disk I/O
```

Do not immediately use:

```bash
-j 100
```

A server has finite resources.

---

# 63. Break/Fix Scenarios

Use the operator loop:

```text
Symptom
→ Evidence
→ Hypothesis
→ Command
→ Observation
→ Root cause
→ Fix
→ Verification
→ Prevention
```

## Scenario 1 — jq Missing Nested Field

Symptom:

```text
null
```

for a customer field.

Investigate:

```bash
jq '.customer'
```

Then:

```bash
jq '.customer.name'
```

Determine whether the field is:

```text
missing
null
empty
```

Fix the expression only after understanding the schema.

---

## Scenario 2 — CSV Parsing Breaks

Input:

```csv
id,company,city
1,"Acme, Inc.","New York"
```

A naive:

```bash
cut -d, -f2
```

can produce incorrect results.

Use:

```bash
csvcut -c company file.csv
```

Explain why a CSV-aware parser is required.

---

## Scenario 3 — Invalid Revenue

Symptom:

```text
revenue aggregation fails
```

Inspect:

```bash
csvstat orders.csv
```

Then use Miller/DuckDB to isolate malformed values.

Do not silently convert invalid business data to zero without an explicit rule.

---

## Scenario 4 — Miller Aggregation Unexpected

Check:

```text
field names
data types
grouping keys
missing values
duplicate keys
```

Compare against DuckDB:

```sql
SELECT country, SUM(revenue)
FROM 'orders.csv'
GROUP BY country;
```

If results differ, identify why rather than choosing the answer you expected.

---

## Scenario 5 — DuckDB Schema Inference Is Wrong

Example:

```text
revenue inferred as VARCHAR
```

Inspect:

```sql
DESCRIBE SELECT *
FROM 'orders.csv';
```

Then explicitly cast where appropriate:

```sql
SELECT CAST(revenue AS DOUBLE)
FROM 'orders.csv';
```

Investigate malformed rows before declaring the source clean.

---

## Scenario 6 — 5 GB CSV Is Slow

Ask:

```text
Do I need all columns?
Do I need all rows?
Can I filter early?
Would Parquet be a better representation?
Is storage or CPU the bottleneck?
```

Use Topic 06 monitoring concepts.

---

## Scenario 7 — GNU parallel Overwhelms Server

Symptoms:

```text
CPU 100%
I/O wait high
memory pressure
jobs slowing down
```

Reduce:

```bash
parallel -j 2 ...
```

or another conservative concurrency.

Then observe again.

---

## Scenario 8 — One-Liner Becomes Unmaintainable

Symptom:

```text
Nobody can explain the command.
```

Refactor:

```text
one-liner
→ documented script
→ tests
→ Python if complexity continues
```

---

# 64. Troubleshooting Decision Tree

```text
                 UNKNOWN DATA FILE
                        |
                        v
                 IDENTIFY FORMAT
                        |
        +---------------+---------------+
        |               |               |
       JSON            CSV           PARQUET
        |               |               |
        v               v               v
       jq          csvkit/Miller      DuckDB
        |               |               |
        +---------------+---------------+
                        |
                        v
                    WHAT QUESTION?
                        |
       +----------------+----------------+
       |                |                |
    Inspect          Transform       Analyze
       |                |                |
 jq/csvlook        jq/mlr/csvkit      DuckDB
       |                |                |
       +----------------+----------------+
                        |
                        v
                 MANY FILES?
                        |
                      yes
                        |
                        v
                  GNU parallel
                        |
                        v
                RESOURCE PRESSURE?
                        |
                        v
              Topic 06 monitoring
                        |
                        v
               COMPLEX / REUSABLE?
                        |
                       yes
                        |
                        v
                     Python
```

---

# 65. 20 Most Useful Command-Line Data One-Liners

## 1. Pretty-print JSON

**Purpose:** understand a payload.

```bash
jq . response.json
```

## 2. Select a JSON field

```bash
jq '.customer.name' response.json
```

## 3. Iterate over an array

```bash
jq '.items[]' response.json
```

## 4. Filter JSONL

```bash
jq 'select(.status == "success")' events.jsonl
```

## 5. Raw JSON value

```bash
jq -r '.customer.name' response.json
```

## 6. Compact JSON

```bash
jq -c '.' response.json
```

## 7. Build a new JSON object

```bash
jq '{id, country: .customer.country}' response.json
```

## 8. JSON to CSV

```bash
jq -r '[.id, .country, .revenue] | @csv' orders.jsonl
```

## 9. Inspect CSV

```bash
csvlook orders.csv
```

## 10. List CSV columns

```bash
csvcut -n orders.csv
```

## 11. Select CSV columns

```bash
csvcut -c order_id,country,revenue orders.csv
```

## 12. Filter CSV

```bash
csvgrep -c country -m IN orders.csv
```

## 13. Profile CSV

```bash
csvstat orders.csv
```

## 14. Miller filter

```bash
mlr --csv filter '$revenue > 1000' orders.csv
```

## 15. Miller sort

```bash
mlr --csv sort -nr revenue orders.csv
```

## 16. Miller aggregate

```bash
mlr --csv stats1 -a sum -f revenue -g country orders.csv
```

## 17. DuckDB CSV query

```bash
duckdb -c "SELECT country, SUM(revenue) FROM 'orders.csv' GROUP BY country;"
```

## 18. DuckDB Parquet query

```bash
duckdb -c "SELECT * FROM 'orders.parquet' LIMIT 10;"
```

## 19. DuckDB schema inspection

```bash
duckdb -c "DESCRIBE SELECT * FROM 'orders.parquet';"
```

## 20. Process many JSONL files

```bash
parallel -j 4 'jq -r ".event_type" {} | sort | uniq -c' ::: jsonl/*.jsonl
```

**Rule:** Treat these as starting points, not commands to copy blindly into production.

---

# 66. Production Runbook — Inspecting an Unknown Data File

## Step 1 — Identify the file

```bash
file data
ls -lh data
```

## Step 2 — Estimate scale

```bash
du -h data
```

Ask:

```text
Is it KB, MB, GB, or TB?
```

## Step 3 — Do not load huge data blindly

For text-like data:

```bash
head -n 20 data
```

For compressed data, stream where possible.

## Step 4 — Determine structure

### JSON

```bash
jq . data.json
```

### CSV

```bash
csvlook data.csv
csvstat data.csv
```

### Parquet

```bash
duckdb -c "DESCRIBE SELECT * FROM 'data.parquet';"
```

## Step 5 — Sample

```bash
jq -c 'select(...)' data.jsonl | head
```

or:

```sql
SELECT *
FROM 'data.parquet'
LIMIT 20;
```

## Step 6 — Profile

Ask:

```text
row count?
nulls?
types?
distinct values?
numeric ranges?
```

## Step 7 — Investigate suspicious records

Use:

```text
jq
csvgrep
Miller
DuckDB
```

## Step 8 — Answer the business/operational question

Use DuckDB when the question is naturally:

```sql
SELECT ...
GROUP BY ...
ORDER BY ...
```

## Step 9 — Validate output

Never assume:

```text
command succeeded
=
answer is correct
```

Check:

```text
counts
types
totals
sample records
```

## Step 10 — Decide whether the workflow should persist

If it is one-off:

```text
documented command
```

If repeated:

```text
script
```

If complex:

```text
Python/pipeline
```

---

# 67. Quick Runbooks by Format

## JSON

```text
jq .
→ inspect structure
→ select fields
→ select/filter records
→ transform
→ validate
```

## JSONL

```text
jq -c
→ process record-by-record
→ filter
→ aggregate carefully
→ use streaming for large workloads
```

## CSV

```text
csvlook
→ csvstat
→ csvcut
→ csvgrep
→ Miller if transformations grow
```

## Parquet

```text
DuckDB
→ DESCRIBE
→ sample
→ filter
→ aggregate
→ validate
```

---

# 68. Common Mistakes

## Mistake 1 — Parsing CSV with `cut`

CSV quoting makes naive delimiter splitting unsafe.

## Mistake 2 — Parsing JSON with `grep`

JSON is hierarchical and can contain arbitrary whitespace/order/nesting.

## Mistake 3 — Ignoring quoted CSV fields

A comma inside a quoted field is not necessarily a delimiter.

## Mistake 4 — Ignoring nested JSON

Use structured traversal rather than string matching.

## Mistake 5 — Treating missing, null, empty, and zero as equivalent

They may have different business meanings.

## Mistake 6 — Assuming all JSON is JSONL

A JSON array and JSONL are different structures.

## Mistake 7 — Loading huge files unnecessarily

Sample and stream first.

## Mistake 8 — Writing unreadable one-liners

Clarity beats cleverness.

## Mistake 9 — Unlimited GNU parallel

Concurrency is a resource-management decision.

## Mistake 10 — Using the wrong tool for analytical questions

DuckDB may be much clearer than a complex shell pipeline.

## Mistake 11 — Using Python for trivial one-off inspection

Avoid unnecessary engineering.

## Mistake 12 — Staying in shell too long

Move to Python when complexity requires it.

## Mistake 13 — Not validating output

Successful execution does not prove semantic correctness.

## Mistake 14 — Not checking schema

Type inference can surprise you.

## Mistake 15 — Silently changing data types

Casting is a data transformation; document it.

## Mistake 16 — Ignoring malformed partner files

Bad input should be measured and handled intentionally.

## Mistake 17 — Failing to document useful commands

A useful investigation should become reusable knowledge.

## Mistake 18 — Creating non-reproducible workflows

Do not rely on undocumented shell history.

## Mistake 19 — Aggregating huge JSON with jq `-s` without considering memory

Slurping changes the memory model.

## Mistake 20 — Creating excessive Parquet partitions

Too many small files can create storage and inode problems.

---

# 69. Command Reference

## jq

| Command | Purpose |
|---|---|
| `jq .` | pretty-print |
| `jq '.field'` | select field |
| `jq '.array[]'` | iterate array |
| `jq 'select(...)'` | filter |
| `jq -r` | raw output |
| `jq -c` | compact output |
| `map(...)` | transform array elements |
| `@csv` | CSV encoding |
| `jq --stream` | streaming-oriented parsing |

Typical use:

```text
JSON inspection/transformation
```

Common mistake:

```text
using complex jq where DuckDB/Python would be clearer
```

---

## csvkit

| Tool | Purpose |
|---|---|
| `csvlook` | visual inspection |
| `csvcut` | column selection |
| `csvgrep` | row filtering |
| `csvstat` | profiling/statistics |
| conversion tools | format conversion |

Typical use:

```text
quick CSV investigation
```

Common mistake:

```text
treating CSV as unstructured text
```

---

## Miller

Core capabilities:

```text
filter
sort
stats1
join
format conversion
```

Typical use:

```text
record-oriented transformation
```

Common mistake:

```text
forgetting that aggregation/join correctness depends on field types and keys
```

---

## DuckDB CLI

Core concepts:

```text
duckdb
SELECT
FROM 'file'
LIMIT
DESCRIBE
GROUP BY
ORDER BY
CSV
JSON
Parquet
COPY
PARTITION_BY
```

Typical use:

```text
analytical SQL directly over files
```

Common mistake:

```text
assuming SQL correctness without checking schema/data quality
```

---

## GNU parallel

```text
parallel
```

Typical use:

```text
independent processing across many files
```

Common mistake:

```text
unbounded concurrency
```

---

# 70. Interview Questions with Model Answers

## Beginner

### 1. Why do Data Engineers need `jq`?

**Answer:** APIs, event streams, and operational data frequently arrive as JSON. `jq` lets a Data Engineer inspect, filter, extract, and reshape that data directly on a Linux server without immediately writing Python.

### 2. What is JSONL?

**Answer:** JSON Lines is a format where each line contains an independent JSON value, usually an object. It is useful for events, logs, ingestion, and incremental processing.

### 3. What does `jq -r` do?

**Answer:** It emits strings as raw text instead of JSON-quoted strings, which is useful when piping values into shell commands or other programs.

### 4. What does `csvstat` do?

**Answer:** It provides quick profiling information about CSV columns and values, helping identify types, counts, missingness, and suspicious data.

### 5. What is Miller?

**Answer:** Miller is a command-line data-processing tool centered on named fields and records. It is particularly useful for filtering, sorting, aggregation, joins, and format conversion.

### 6. What is DuckDB?

**Answer:** DuckDB is an analytical SQL engine that can query files such as CSV, JSON, and Parquet directly, making it useful for ad hoc data analysis without first loading the data into a server database.

---

## Intermediate

### 7. Why should you not parse arbitrary CSV with `cut`?

**Answer:** CSV supports quoted fields, including fields containing commas, quotes, and sometimes newlines. A delimiter-based text tool does not understand CSV semantics, so it can split records incorrectly.

### 8. How would you flatten nested JSON?

**Answer:** First inspect the structure with `jq`. Then traverse nested objects and arrays, construct a flat object, and emit it as JSON or CSV. For complex flattening, I would consider Python or DuckDB rather than building an opaque jq expression.

### 9. When would you choose Miller over csvkit?

**Answer:** csvkit is excellent for quick CSV inspection and basic column/filter/statistics operations. Miller becomes attractive when I need richer record-oriented transformations, sorting, aggregation, joins, or format conversion.

### 10. When would you choose DuckDB over Miller?

**Answer:** I would choose DuckDB when the question is naturally analytical or relational, especially for grouping, joins, SQL expressions, Parquet, or multi-file analysis.

### 11. How do you inspect a Parquet file from the CLI?

**Answer:**

```bash
duckdb -c "DESCRIBE SELECT * FROM 'data.parquet';"
```

Then I would sample and query it with SQL.

### 12. How do you handle missing JSON fields?

**Answer:** First distinguish missing from null and other representations. Then use explicit jq logic such as `//` where a documented default is appropriate, or preserve null/missing semantics when they carry meaning.

---

## Advanced

### 13. How would you process multi-GB JSON without loading everything into memory?

**Answer:** I would first determine whether the data is JSONL or one large JSON document. For JSONL, process records incrementally. For large structured analytical queries, DuckDB's JSON reader may be simpler. For one large document, jq streaming mode may be appropriate. The strategy depends on the operation and memory constraints.

### 14. How would you parallelize hundreds of independent files?

**Answer:** Use GNU parallel with bounded concurrency, produce independent outputs per input, and aggregate them afterward. I would start with a small `-j` value and observe CPU, memory, and I/O before increasing concurrency.

### 15. How would you prevent GNU parallel from overwhelming a server?

**Answer:** Bound worker count, understand whether the workload is CPU- or I/O-bound, monitor the server, and choose concurrency based on available resources rather than the number of files.

### 16. When should a one-liner become a shell script?

**Answer:** When it is reused, has multiple stages, needs parameters, error handling, comments, or operational documentation.

### 17. When should a shell workflow become Python?

**Answer:** When logic becomes complex, reusable functions/tests are needed, error handling is substantial, external APIs/state are involved, or maintainability becomes more important than command-line convenience.

### 18. How would you choose between jq, Miller, and DuckDB during an incident?

**Answer:** I would classify the data and question first. JSON extraction/transformation suggests jq; record-oriented CSV/TSV operations suggest Miller; analytical questions over CSV/JSON/Parquet suggest DuckDB. I would choose the simplest tool that preserves correctness and remains readable.

---

# 71. Practice Questions

## JSON

1. Extract a nested customer name with jq.
2. Extract every item SKU from an order payload.
3. Filter JSONL to successful events.
4. Filter orders with revenue above 1,000.
5. Build a new object with selected fields.
6. Create a derived revenue field.
7. Handle a missing country field.
8. Distinguish null from empty string.
9. Convert JSONL records to CSV.
10. Explain when `-s` can create memory pressure.

## CSV

11. Inspect an unfamiliar CSV.
12. List all columns.
13. Select three columns.
14. Filter rows by country.
15. Profile a partner CSV.
16. Explain why `cut` is unsafe for quoted CSV.
17. Identify invalid numeric values.
18. Convert a source file and validate the result.

## Miller

19. Filter records by revenue.
20. Sort by revenue descending.
21. Aggregate revenue by country.
22. Count records by event type.
23. Join two files on a key.
24. Identify risks of duplicate join keys.
25. Convert CSV to another structured format.

## DuckDB

26. Query the first ten CSV rows.
27. Inspect a CSV schema.
28. Query JSON/JSONL.
29. Query Parquet.
30. Calculate revenue by country.
31. Calculate daily revenue.
32. Find the top five countries by revenue.
33. Convert CSV to Parquet.
34. Create partitioned Parquet.
35. Explain the benefits and risks of partitioning.

## Tool Selection

36. You have a small API response. Which tool?
37. You have a 4 GB partner CSV and need column statistics. Which tool?
38. You need grouped revenue by country. Which tool?
39. You need to join two CSV files. Which tool?
40. You need a reusable validation workflow with tests. Which tool?
41. You have 500 independent JSONL files. How do you process them?
42. A one-liner has become 250 characters long. What do you do?
43. A DuckDB query reports an unexpected numeric type. How do you investigate?
44. A parallel workflow causes high I/O wait. What do you change?
45. A Parquet conversion creates thousands of tiny files. What design issue might exist?

## Production Scenarios

46. A partner sends a malformed CSV at 2 a.m. How do you investigate?
47. An API response has a new nested field. How do you safely adapt extraction?
48. A JSON file is 15 GB. How do you choose the processing approach?
49. A server is CPU-constrained and you need to process 500 files. How do you choose concurrency?
50. A recurring one-liner is now part of a daily production process. What should happen next?

---

# 72. Knowledge Check

Before completing Topic 08, verify:

- [ ] I can explain JSON objects and arrays.
- [ ] I can explain JSONL.
- [ ] I can inspect JSON with `jq`.
- [ ] I can select nested JSON fields.
- [ ] I can iterate arrays.
- [ ] I can filter with `select`.
- [ ] I can map arrays.
- [ ] I can use `-r`.
- [ ] I can use `-c`.
- [ ] I can build new JSON objects.
- [ ] I can create derived fields.
- [ ] I can distinguish missing, null, empty, zero, and false.
- [ ] I can transform JSON into CSV.
- [ ] I understand jq streaming awareness.
- [ ] I can inspect CSV with `csvlook`.
- [ ] I can list/select columns with `csvcut`.
- [ ] I can filter with `csvgrep`.
- [ ] I can profile with `csvstat`.
- [ ] I can explain why CSV-aware tools matter.
- [ ] I can filter with Miller.
- [ ] I can sort with Miller.
- [ ] I can aggregate with `stats1`.
- [ ] I can reason about Miller joins.
- [ ] I can convert formats with Miller.
- [ ] I can query CSV with DuckDB.
- [ ] I can query JSON with DuckDB.
- [ ] I can query Parquet with DuckDB.
- [ ] I can inspect schemas.
- [ ] I can aggregate with SQL.
- [ ] I can convert CSV to Parquet.
- [ ] I understand partitioned Parquet.
- [ ] I can process independent files with GNU parallel.
- [ ] I can bound concurrency.
- [ ] I understand Rust-based CSV alternatives at an awareness level.
- [ ] I can turn useful one-liners into scripts.
- [ ] I know when to move to Python.
- [ ] I can choose the right tool for a production problem.
- [ ] I can validate command output rather than trusting exit status alone.

---

# 73. Final Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Where Taught |
|---|---|---|
| jq pretty-printing | ✅ Covered | Sections 8–9 |
| jq field selection | ✅ Covered | Section 10 |
| jq `select` filtering | ✅ Covered | Section 12 |
| jq array mapping | ✅ Covered | Section 13 |
| jq `-r` raw output | ✅ Covered | Section 14 |
| jq `-c` compact output | ✅ Covered | Section 15 |
| JSON Lines | ✅ Covered | Section 6 |
| API response handling | ✅ Covered | Section 7 |
| csvlook | ✅ Covered | Section 23 |
| csvcut | ✅ Covered | Section 24 |
| csvgrep | ✅ Covered | Section 25 |
| csvstat | ✅ Covered | Section 26 |
| csvkit conversion | ✅ Covered | Section 27 |
| Miller named fields | ✅ Covered | Section 29 |
| Miller filtering | ✅ Covered | Section 30 |
| Miller sorting | ✅ Covered | Section 31 |
| Miller `stats1` aggregation | ✅ Covered | Section 32 |
| Miller joins | ✅ Covered | Section 33 |
| Miller format conversion | ✅ Covered | Section 34 |
| DuckDB CLI | ✅ Covered | Section 35 |
| CSV querying | ✅ Covered | Section 36 |
| JSON querying | ✅ Covered | Section 37 |
| Parquet querying | ✅ Covered | Section 38 |
| Sampling | ✅ Covered | Section 39 |
| Schema inspection | ✅ Covered | Section 40 |
| SQL aggregation | ✅ Covered | Section 41 |
| CSV → Parquet | ✅ Covered | Section 43 |
| Partitioned Parquet | ✅ Covered | Section 44 |
| jq transformations | ✅ Covered | Sections 16–20 |
| Building new JSON objects | ✅ Covered | Section 16 |
| Grouping | ✅ Covered | Section 19 |
| Missing/null handling | ✅ Covered | Section 18 |
| Tool selection | ✅ Covered | Sections 46–48 |
| jq vs csvkit vs Miller vs DuckDB vs Python | ✅ Covered | Section 46 |
| Large JSON | ✅ Covered | Sections 21 and 49 |
| jq streaming awareness | ✅ Covered | Sections 21 and 49 |
| DuckDB JSON reader | ✅ Covered | Section 37 |
| GNU parallel | ✅ Covered | Sections 50–51 |
| Parallel processing across many files | ✅ Covered | Sections 50–51 |
| Rust CSV alternatives awareness | ✅ Covered | Section 52 |
| Reproducible one-liners | ✅ Covered | Sections 53–54 |
| Saving scripts with comments | ✅ Covered | Section 54 |
| When to move to Python | ✅ Covered | Section 55 |
| `server_lab/08` | ✅ Covered | Section 57 |
| API JSON → CSV exercise | ✅ Covered | Section 58 |
| Messy partner CSV exercise | ✅ Covered | Section 59 |
| Miller vs DuckDB aggregation | ✅ Covered | Section 60 |
| 5 GB CSV → partitioned Parquet | ✅ Covered | Section 61 |
| 500 JSONL files in parallel | ✅ Covered | Section 62 |
| Checkpoint | ✅ Covered | Section 72 |
| Common mistakes | ✅ Covered | Section 68 |
| Production runbook | ✅ Covered | Sections 66–67 |

**Audit result: all specified Topic 08 roadmap requirements are covered.**

---

# 74. Final Quality and Safety Review

## Completeness

This module covers:

```text
JSON
JSONL
jq
csvkit
Miller
DuckDB CLI
Parquet
GNU parallel
tool selection
reproducibility
Python migration
```

## Progressive difficulty

```text
structured-data fundamentals
→ jq
→ csvkit
→ Miller
→ DuckDB
→ multi-tool workflows
→ large data
→ parallel processing
→ production decision-making
```

## Data Engineering relevance

Examples use:

```text
API responses
events
orders
revenue
countries
partner files
Parquet
large datasets
server-side investigations
```

## Large-data safety

The module repeatedly emphasizes:

```text
sample first
stream when possible
avoid unnecessary memory usage
bound concurrency
monitor CPU/memory/I/O
plan temporary storage
```

## Correctness

The module teaches:

```text
successful command
≠
correct answer
```

Output should be validated through:

```text
counts
samples
types
totals
schema
```

## Credential safety

The labs use synthetic/sanitized data and do not require:

```text
real passwords
private keys
API tokens
production credentials
customer exports
```

## Scope boundary

This is not a complete course in:

```text
Python
SQL
Spark
database administration
API engineering
Parquet internals
```

Those subjects are used only enough to teach command-line Data Engineering operations and tool selection.

---

# 75. Production Decision Framework

When receiving an unknown data file:

```text
1. Identify format
2. Estimate size
3. Sample safely
4. Understand structure/schema
5. Profile quality
6. Ask the actual question
7. Choose the simplest appropriate tool
8. Validate the result
9. Document useful logic
10. Move to script/Python when complexity grows
```

A practical selection matrix:

| Situation | Preferred starting point |
|---|---|
| Inspect nested JSON | `jq` |
| Filter JSONL | `jq` |
| JSON → CSV | `jq` |
| Inspect CSV | `csvlook` |
| Profile CSV | `csvstat` |
| Select CSV columns | `csvcut` |
| Simple CSV filter | `csvgrep` |
| Record transformation | Miller |
| Record aggregation | Miller |
| Join structured files | Miller or DuckDB |
| Analytical query | DuckDB |
| Parquet analysis | DuckDB |
| CSV → Parquet | DuckDB |
| Many independent files | GNU `parallel` |
| Complex reusable workflow | Python |

---

# 76. Three-Minute Operator Reference

```text
UNKNOWN FILE
    ↓
What format?
    ↓
JSON → jq
CSV → csvkit/Miller
Parquet → DuckDB
    ↓
What question?
    ↓
Inspect → jq/csvlook
Filter → jq/csvgrep/mlr
Transform → jq/mlr
Aggregate → mlr/DuckDB
Analyze → DuckDB
    ↓
Large?
    ↓
Sample/stream
    ↓
Many files?
    ↓
Bounded GNU parallel
    ↓
Reusable?
    ↓
Script
    ↓
Complex?
    ↓
Python
```

Remember:

```text
Correctness
>
Cleverness
```

and:

```text
Simple
+
Structured-data aware
+
Validated
+
Repeatable
```

is the target.

---

# 77. Core Mental Model

```text
jq
=
Understand and transform JSON

csvkit
=
Inspect and profile CSV

Miller
=
Transform and aggregate named records

DuckDB
=
Ask analytical SQL questions directly over files

GNU parallel
=
Run independent file operations concurrently

Python
=
Build reusable, complex, testable workflows
```

And the complete workflow:

```text
UNKNOWN DATA
      ↓
IDENTIFY FORMAT
      ↓
SAMPLE
      ↓
UNDERSTAND STRUCTURE / SCHEMA
      ↓
PROFILE
      ↓
FILTER / TRANSFORM
      ↓
ANALYZE
      ↓
VALIDATE OUTPUT
      ↓
DOCUMENT
      ↓
REUSE?
   /       \
 NO         YES
 |           |
one-off    script
             |
        complexity grows?
          /       \
        NO         YES
        |           |
      script      Python
```

The final lesson is:

> **The goal is not to know the most shell one-liners. The goal is to become a Data Engineer who can quickly inspect and reason about structured data on a server, choose the right tool for the question, produce correct results, and know when a command-line workflow should become a proper script or Python/data pipeline.**

---

# 78. Completion Criteria

Topic 08 is complete when the learner can independently:

```text
Inspect an unknown JSON response
        ↓
Extract nested fields with jq
        ↓
Filter JSONL
        ↓
Handle null/missing fields
        ↓
Convert JSON to CSV
        ↓
Profile a partner CSV
        ↓
Filter/select CSV fields
        ↓
Transform and aggregate with Miller
        ↓
Query CSV/JSON/Parquet with DuckDB
        ↓
Convert CSV to Parquet
        ↓
Reason about partitioning
        ↓
Process many files with bounded parallelism
        ↓
Document the workflow
        ↓
Decide whether to stay in shell or move to Python
```

The professional capability is not command memorization.

It is:

```text
FORMAT AWARENESS
+
TOOL SELECTION
+
CORRECTNESS
+
RESOURCE AWARENESS
+
REPRODUCIBILITY
+
MAINTAINABILITY
```
