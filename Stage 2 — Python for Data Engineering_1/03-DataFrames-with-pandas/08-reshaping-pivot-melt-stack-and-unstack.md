# 08 — Reshaping: `pivot`, `melt`, `stack`, and `unstack`

> **Stage 2 — Python for Data Engineering → Module 2.3 — DataFrames with pandas**
>
> **Topic 08:** Reshaping: `pivot`, `melt`, `stack`, and `unstack`  
> **Level:** Beginner → Intermediate → Advanced → Production-oriented
>
> **Core mental model:**  
> **Dimensions + Measures + Shape**
>
> **Core production principle:**  
> **Reshaping must preserve business meaning, not merely produce the desired visual layout.**

---

## 0. Learning contract

The authoritative Module 2.3 roadmap places this topic after grouping and before time-series, method-chaining, Copy-on-Write, and chunked-processing topics. The specific roadmap scope is:

```text
Basics
  long/tidy vs wide
  melt
  id_vars
  value_vars
  var_name
  value_name
  pivot
  duplicate index/column pair behavior

Intermediate
  pivot_table
  aggfunc
  fill_value
  margins
  multiple values
  stack / unstack
  MultiIndex
  crosstab
  flattening MultiIndex columns

Advanced
  wide_to_long
  embedded dimensions such as sales_2023
  get_dummies
  one-hot encoding
  column-explosion risk
  missing cells
  missing vs zero
  shape-driven performance
  very wide frames
  very long frames
```

The roadmap's learning method is:

```text
1. Read the topic.
2. Move one dataset wide → long → wide.
3. Assert the original result is recovered.
4. Predict the output shape of every reshape before running it.
```

The roadmap exercise is `reshape_reports.py`, with five tasks:

```text
1. Melt a spreadsheet-style monthly file.
2. Build a country × month revenue report with pivot_table and margins.
3. Show pivot failing on duplicate keys and fix it appropriately.
4. Unstack a groupby result and flatten the output columns.
5. Round-trip wide → long → wide and assert equality.
```

The checkpoint is:

```text
Explain long vs wide and when each is right.
Explain why pivot fails where pivot_table succeeds.
Flatten MultiIndex columns into clean names.
Distinguish missing cells from true zeros after reshaping.
```

---

# 1. Why Reshaping Matters in Data Engineering

Real data rarely arrives in exactly the shape that every downstream consumer needs.

The same business information may appear as:

### Spreadsheet-style wide data

```text
country | Jan | Feb | Mar
IN      | 100 | 120 | 90
US      | 200 | 250 | 300
```

### Pipeline-friendly long data

```text
country | month | revenue
IN      | Jan   | 100
IN      | Feb   | 120
IN      | Mar   | 90
US      | Jan   | 200
US      | Feb   | 250
US      | Mar   | 300
```

### Reporting output

```text
country | Jan | Feb | Mar | Total
IN      | 100 | 120 | 90  | 310
US      | 200 | 250 | 300 | 750
```

These tables can represent the same underlying business information.

But they have different **shapes**, and that shape changes how data is:

- filtered;
- grouped;
- validated;
- stored;
- serialized;
- consumed by reporting tools;
- consumed by machine-learning workflows;
- compared in tests.

## A reshape is a data-model transformation

It is tempting to think:

> "Reshaping only changes the display."

That is too shallow.

When you move:

```text
month
```

from:

```text
column names
```

into:

```text
a row value
```

you have changed the representation of a dimension.

When you move:

```text
month
```

from rows into columns, you have changed the axis on which the dimension is represented.

When you use:

```python
pivot_table(..., aggfunc="sum")
```

you have also defined what duplicate observations mean.

So:

```text
reshape
+
possibly aggregate
```

can change semantics if the transformation is designed incorrectly.

---

# 2. The Core Mental Model: Dimensions + Measures + Shape

When you look at a DataFrame, classify its columns.

## Dimensions

Dimensions describe **who, what, where, when, or which category**.

Examples:

```text
customer_id
country
product_id
month
channel
status
year
```

## Measures

Measures are values you want to:

- report;
- aggregate;
- compare;
- model.

Examples:

```text
revenue
quantity
cost
orders
profit
```

## Shape

Shape describes how dimensions and measures are arranged.

For example:

```text
wide:
country | Jan | Feb | Mar
```

means:

```text
country = dimension
Jan/Feb/Mar = encoded dimension values represented as columns
revenue = measure stored in those columns
```

While:

```text
long:
country | month | revenue
```

means:

```text
country = dimension
month = dimension
revenue = measure
```

This is usually easier for a general-purpose pipeline because the structure of the table is stable even when new months arrive.

---

# 3. "One Row Represents..." — The First Question

Before reshaping, finish this sentence:

> **One row represents ________.**

Examples:

```text
One row represents one country.
```

or:

```text
One row represents one country-month observation.
```

or:

```text
One row represents one country-product-month observation.
```

This is your **grain**.

The grain determines whether a reshape is safe.

## Example

Wide:

```text
country | Jan | Feb | Mar
IN      | 100 | 120 | 90
```

One row represents:

```text
one country
```

Long:

```text
country | month | revenue
IN      | Jan   | 100
IN      | Feb   | 120
IN      | Mar   | 90
```

One row represents:

```text
one country-month observation
```

That sentence should be written before every major reshape.

---

# 4. Long (tidy) vs wide formats — Long vs Wide

## 4.1 Wide

A wide DataFrame places different values of a dimension across columns.

Example:

```python
wide = pd.DataFrame(
    {
        "country": ["IN", "US"],
        "Jan": [100, 200],
        "Feb": [120, 250],
        "Mar": [90, 300],
    }
)
```

Shape:

```text
2 rows × 4 columns
```

Grain:

```text
one row per country
```

## 4.2 Long

A long DataFrame stores the dimension as a column.

```python
long = pd.DataFrame(
    {
        "country": [
            "IN", "IN", "IN",
            "US", "US", "US",
        ],
        "month": [
            "Jan", "Feb", "Mar",
            "Jan", "Feb", "Mar",
        ],
        "revenue": [
            100, 120, 90,
            200, 250, 300,
        ],
    }
)
```

Shape:

```text
6 rows × 3 columns
```

Grain:

```text
one row per country-month
```

## Prediction

Before transforming:

```text
2 countries
×
3 value columns
=
6 long rows
```

The row count prediction is:

```text
6
```

---

# 5. Why Long/Tidy Is Often a Strong Pipeline Default

Long/tidy representation often makes pipeline logic straightforward because:

```text
one observation
→ one row

one variable
→ one column

one value
→ one cell
```

A long table can make:

- filtering predictable;
- grouping natural;
- SQL loading easier;
- schema evolution easier;
- validation easier;
- new dimension values less disruptive.

For example:

```text
country | month | revenue
```

does not require creating:

```text
Jan
Feb
Mar
Apr
...
```

columns just because a new month appears.

## But long is not always better

Wide data can be appropriate for:

- presentation;
- matrix-style reports;
- certain feature matrices;
- systems requiring fixed columns;
- human-readable spreadsheet exports.

Therefore:

> Long is a strong general-purpose pipeline representation, not a universal law.

Choose based on:

```text
semantics
+
consumer
+
workload
+
schema contract
```

---

# 6. Tidy Data Principles

A practical tidy-data model is:

```text
one observation per row
one variable per column
one value per cell
```

Reshaping becomes easier when you can identify:

```text
identifier variables
+
measured variables
```

For:

```text
country | Jan | Feb | Mar
```

you might identify:

```text
identifier:
country

measured variables:
Jan
Feb
Mar
```

The reshape:

```text
wide → long
```

turns:

```text
Jan
Feb
Mar
```

into values in a new variable column:

```text
month
```

while the measurements move into:

```text
revenue
```

---

# 7. `melt()` — Wide to Long

`melt` unpivots wide columns into rows.

Basic pattern:

```python
long_df = df.melt()
```

But production code should usually state the intended identifiers and measured columns explicitly.

The roadmap requires:

```text
id_vars
value_vars
var_name
value_name
```

---

# 8. `melt()` Mental Model

Think:

```text
Several value columns
        ↓
one variable column
        +
one value column
```

Example:

```text
BEFORE

country | Jan | Feb | Mar
IN      | 100 | 120 | 90
US      | 200 | 250 | 300
```

After:

```text
AFTER

country | month | revenue
IN      | Jan   | 100
IN      | Feb   | 120
IN      | Mar   | 90
US      | Jan   | 200
US      | Feb   | 250
US      | Mar   | 300
```

Predict:

```text
2 input rows
×
3 value columns
=
6 output rows
```

Then execute.

---

# 9. `melt()` with `id_vars`

Use:

```python
long_df = df.melt(
    id_vars=["country"],
)
```

`id_vars` means:

> Columns that identify the original observation and should remain attached to every generated row.

Example:

```python
wide = pd.DataFrame(
    {
        "country": ["IN", "US"],
        "Jan": [100, 200],
        "Feb": [120, 250],
        "Mar": [90, 300],
    }
)

long_df = wide.melt(
    id_vars=["country"],
)
```

Conceptually:

```text
country
```

is repeated because it identifies each original row.

## Multiple identifier columns

Suppose:

```text
country
product_id
Jan
Feb
Mar
```

Then:

```python
long_df = wide.melt(
    id_vars=["country", "product_id"],
)
```

Now each:

```text
country + product_id
```

combination remains attached to every month row.

### Common mistake

Do not place a measure column into `id_vars` merely because it "looks important."

Ask:

> Is this column identifying the observation, or measuring the observation?

---

# 10. `melt()` with `value_vars`

`value_vars` tells pandas which columns should be unpivoted.

```python
long_df = wide.melt(
    id_vars=["country"],
    value_vars=["Jan", "Feb", "Mar"],
)
```

This is safer for production pipelines when the DataFrame contains metadata columns that should not be melted.

Example:

```python
wide = pd.DataFrame(
    {
        "country": ["IN", "US"],
        "source_system": ["erp", "crm"],
        "Jan": [100, 200],
        "Feb": [120, 250],
    }
)
```

Use:

```python
long_df = wide.melt(
    id_vars=["country", "source_system"],
    value_vars=["Jan", "Feb"],
)
```

### Why explicit `value_vars` helps

Without them, pandas may treat every non-identifier column as a value variable.

That can accidentally melt:

```text
source_system
load_date
batch_id
```

into your measurement structure.

---

# 11. `var_name`

Use:

```python
var_name="month"
```

instead of a generic:

```text
variable
```

Example:

```python
long_df = wide.melt(
    id_vars=["country"],
    value_vars=["Jan", "Feb", "Mar"],
    var_name="month",
)
```

Now the output communicates the domain meaning.

```text
country | month | value
```

is less informative than:

```text
country | month | revenue
```

---

# 12. `value_name`

Use:

```python
value_name="revenue"
```

Example:

```python
long_df = wide.melt(
    id_vars=["country"],
    value_vars=["Jan", "Feb", "Mar"],
    var_name="month",
    value_name="revenue",
)
```

Now the transformation produces a clean schema:

```text
country
month
revenue
```

This matters for:

- downstream SQL;
- Parquet;
- tests;
- documentation;
- analysts;
- schema validation.

---

# 13. Complete `melt()` Example

```python
import pandas as pd

wide = pd.DataFrame(
    {
        "country": ["IN", "US"],
        "Jan": [100, 200],
        "Feb": [120, 250],
        "Mar": [90, 300],
    }
)

long_df = wide.melt(
    id_vars=["country"],
    value_vars=["Jan", "Feb", "Mar"],
    var_name="month",
    value_name="revenue",
)

print(long_df)
```

Expected:

```text
  country month  revenue
0      IN   Jan      100
1      US   Jan      200
2      IN   Feb      120
3      US   Feb      250
4      IN   Mar       90
5      US   Mar      300
```

Exact row ordering is less important than the transformation semantics.

Check:

```python
assert len(long_df) == len(wide) * 3
```

---

# 14. `melt()` Output-Shape Reasoning

For a simple DataFrame with:

```text
R rows
K value_vars
```

the generated long data has approximately:

```text
R × K
```

rows.

The word "approximately" matters for generalized use because:

- indexes;
- specialized input structures;
- downstream filtering;
- later transformations

can change what you observe.

For the ordinary DataFrame case shown here, the direct row-count prediction is exact.

## Prediction habit

Before:

```python
df.melt(...)
```

write:

```text
input rows:
value_vars:
expected output rows:
```

Then assert.

---

# 15. `melt()` Common Mistakes

## Mistake 1 — Melting an identifier

Wrong:

```python
wide.melt(
    id_vars=["Jan"]
)
```

when `Jan` is a monthly measure.

Correct:

```python
wide.melt(
    id_vars=["country"],
    value_vars=["Jan", "Feb"],
)
```

## Mistake 2 — Forgetting a metadata identifier

Wrong:

```python
wide.melt(
    id_vars=["country"],
)
```

when:

```text
source_system
```

must remain attached.

Correct:

```python
wide.melt(
    id_vars=["country", "source_system"],
)
```

## Mistake 3 — Accidentally melting all columns

Use explicit `value_vars` when schema is important.

## Mistake 4 — Wrong row-count expectation

If:

```text
10 rows × 12 month columns
```

then expect:

```text
120 long rows
```

before any later filtering.

---

# 16. Mixed Value Types During `melt()`

If value columns contain incompatible types:

```text
Jan → integer
Feb → string
Mar → float
```

the resulting value column may require a common representation.

That can affect:

- dtype;
- memory;
- downstream aggregation;
- validation.

Production pattern:

```text
inspect value columns
→ decide canonical measurement dtype
→ melt
→ validate result dtype
```

Do not assume a reshape fixes inconsistent source typing.

---

# 17. `pivot()` — Long to Wide

`pivot()` changes a long representation into a wide representation.

Basic form:

```python
wide = df.pivot(
    index="country",
    columns="month",
    values="revenue",
)
```

The three roles are:

```text
index   → rows
columns → columns
values  → cells
```

---

# 18. `pivot()` Mental Model

Start with:

```text
country | month | revenue
IN      | Jan   | 100
IN      | Feb   | 120
US      | Jan   | 200
US      | Feb   | 250
```

Then:

```python
wide = long_df.pivot(
    index="country",
    columns="month",
    values="revenue",
)
```

Result conceptually:

```text
month      Jan  Feb
country
IN         100  120
US         200  250
```

The dimension:

```text
month
```

moved from a row value into column labels.

---

# 19. `pivot()` Parameters

## `index`

Defines the row dimension:

```python
index="country"
```

## `columns`

Defines the values that become columns:

```python
columns="month"
```

## `values`

Defines what populates the cells:

```python
values="revenue"
```

Together:

```python
df.pivot(
    index="country",
    columns="month",
    values="revenue",
)
```

means:

> Make one row per country, one column per month, and place revenue in the cells.

---

# 20. `pivot()` Key Uniqueness Requirement

This is one of the most important rules in the chapter.

For:

```python
df.pivot(
    index="country",
    columns="month",
    values="revenue",
)
```

each:

```text
country + month
```

pair must identify one value.

In other words:

```text
(country, month)
```

must be unique for a lossless simple pivot.

Why?

Because this:

```text
country | month | revenue
IN      | Jan   | 100
IN      | Jan   | 125
```

does not tell pandas which value belongs in:

```text
IN × Jan
```

Should it be:

```text
100
```

or:

```text
125
```

or:

```text
225
```

Pandas refuses to guess.

---

# 21. Deliberately Trigger the `pivot()` Failure

```python
import pandas as pd

df = pd.DataFrame(
    {
        "country": ["IN", "IN", "US"],
        "month": ["Jan", "Jan", "Jan"],
        "revenue": [100, 125, 200],
    }
)

wide = df.pivot(
    index="country",
    columns="month",
    values="revenue",
)
```

Expected behavior:

```text
ValueError
```

because:

```text
(IN, Jan)
```

appears twice.

### Why the error is useful

The error protects you from silently choosing one observation.

The data is telling you:

> Your intended wide-table grain is not unique.

---

# 22. Debugging Duplicate Pivot Keys

Before pivoting, validate:

```python
duplicate_pairs = (
    df.duplicated(
        subset=["country", "month"],
        keep=False,
    )
)

bad = df.loc[duplicate_pairs]
```

Or:

```python
pair_counts = (
    df.groupby(
        ["country", "month"],
        dropna=False,
    )
    .size()
)

duplicate_pairs = pair_counts.loc[
    pair_counts > 1
]
```

The second version is especially useful because it shows:

```text
which key pair
+
how many observations
```

---

# 23. What To Do When Pivot Keys Are Duplicated

Do not automatically write:

```python
pivot_table(..., aggfunc="sum")
```

until you know what duplicate rows mean.

Possible explanations:

```text
multiple transactions
duplicate source records
multiple revisions
multiple products within a country-month
late-arriving corrections
```

The correct response depends on the data model.

You have at least two broad options:

### Option A — Aggregate

If duplicates represent legitimate multiple observations:

```python
pd.pivot_table(
    df,
    index="country",
    columns="month",
    values="revenue",
    aggfunc="sum",
)
```

### Option B — Resolve duplicates first

If duplicate rows violate a business key, fix or quarantine the data before pivoting.

The operation is different:

```text
aggregate legitimate observations
```

versus:

```text
repair invalid duplicates
```

---

# 24. `pivot()` vs `pivot_table()`

| Aspect | `pivot` | `pivot_table` |
|---|---|---|
| Main purpose | Reshape unique observations | Reshape and aggregate |
| Duplicate index/column pairs | Raises error | Can aggregate |
| Aggregation | No | Yes, via `aggfunc` |
| Best use | One value per target cell | Multiple observations per target cell |
| Semantic question | "Which value belongs here?" | "How should multiple values be combined?" |

Memorize:

> `pivot` expects uniqueness.  
> `pivot_table` lets you define what duplicates mean.

---

# 25. `pivot_table()`

Basic:

```python
summary = pd.pivot_table(
    df,
    index="country",
    columns="month",
    values="revenue",
    aggfunc="sum",
)
```

This is essentially:

```text
group by index dimensions
+
group by column dimensions
+
aggregate values
+
reshape
```

So `pivot_table` combines:

```text
grouping
+
aggregation
+
reshaping
```

---

# 26. `aggfunc`

`aggfunc` defines what to do when multiple observations belong to the same target cell.

Examples:

```python
aggfunc="sum"
```

```python
aggfunc="mean"
```

```python
aggfunc="count"
```

## `sum`

Use when multiple rows represent additive contributions:

```text
transactions
→ monthly revenue
```

## `mean`

Use when the target metric is conceptually an average.

## `count`

Use for row/observation counts, subject to the same null semantics as the selected count operation.

### Critical rule

> Aggregation is a business meaning decision.

Do not use:

```python
aggfunc="sum"
```

just because `pivot()` failed.

---

# 27. `pivot_table()` Example with Sum

```python
df = pd.DataFrame(
    {
        "country": [
            "IN", "IN", "IN",
            "US",
        ],
        "month": [
            "Jan", "Jan", "Feb",
            "Jan",
        ],
        "revenue": [
            100, 50, 120,
            200,
        ],
    }
)

result = pd.pivot_table(
    df,
    index="country",
    columns="month",
    values="revenue",
    aggfunc="sum",
)
```

For:

```text
IN + Jan
```

the source contains:

```text
100
50
```

so:

```text
sum = 150
```

The duplicate cell now has a defined meaning.

---

# 28. `pivot_table()` with Mean

```python
result = pd.pivot_table(
    df,
    index="country",
    columns="month",
    values="revenue",
    aggfunc="mean",
)
```

For:

```text
IN + Jan
```

the result is:

```text
(100 + 50) / 2
=
75
```

That may be correct for:

```text
average transaction amount
```

but incorrect for:

```text
monthly revenue
```

This is why the aggregation function is part of the business logic.

---

# 29. `pivot_table()` with Count

```python
result = pd.pivot_table(
    df,
    index="country",
    columns="month",
    values="revenue",
    aggfunc="count",
)
```

This counts non-null values in the chosen measure.

If the actual question is:

```text
number of rows/events
```

consider whether `size`-style semantics are more appropriate before designing the report. `pivot_table` can use custom functions, but the business meaning still needs to be explicit.

---

# 30. `fill_value`

`fill_value` fills missing cells in the resulting pivot table.

Example:

```python
result = pd.pivot_table(
    df,
    index="country",
    columns="month",
    values="revenue",
    aggfunc="sum",
    fill_value=0,
)
```

This is convenient.

It is also dangerous.

---

# 31. Missing Cell Does Not Automatically Mean Zero

Suppose:

```text
country | month | revenue
IN      | Jan   | 100
IN      | Mar   | 120
```

There is no February observation.

After pivot:

```text
Jan   Feb   Mar
100   NaN   120
```

The `NaN` can mean:

```text
no observation exists
```

It does not inherently mean:

```text
revenue = 0
```

This distinction is critical.

---

# 32. Missing vs Zero — Deep Semantic Example

Consider a store-month report.

## Scenario A — no row exists

```text
IN + Feb
```

There is no source observation.

Meaning might be:

```text
unknown
not reported
closed
source missing
```

Representing it as:

```text
0
```

could hide the distinction.

## Scenario B — store operated and made zero sales

There is an explicit source record:

```text
IN + Feb + revenue=0
```

This is a true zero.

## Scenario C — source system failed

No row exists because the source failed to deliver data.

That is neither necessarily:

```text
zero
```

nor:

```text
normal missing
```

It is a data-quality problem.

### Production rule

Before:

```python
fill_value=0
```

write down:

> **What exactly does zero mean in this dataset?**

---

# 33. When `fill_value=0` Is Appropriate

It can be appropriate when the data model guarantees:

```text
absence of a row
=
zero measure
```

For example, a fully enumerated event table might explicitly define every:

```text
store × month
```

combination and encode no sales as zero.

But even then, validate that the source really has that contract.

---

# 34. `margins=True`

Use:

```python
margins=True
```

to include aggregate totals.

Example:

```python
result = pd.pivot_table(
    df,
    index="country",
    columns="month",
    values="revenue",
    aggfunc="sum",
    margins=True,
)
```

Conceptually, the result adds:

```text
All
```

for totals.

---

# 35. `margins=True` Example

Suppose:

```text
country | month | revenue
IN      | Jan   | 100
IN      | Feb   | 120
US      | Jan   | 200
US      | Feb   | 250
```

A sum pivot with margins conceptually contains:

```text
month      Jan  Feb  All
country
IN         100  120  220
US         200  250  450
All        300  370  670
```

This is useful for reports.

---

# 36. `margins=True` Is Not Always "Just Add Everything"

The exact meaning of a margin depends on:

```text
aggregation function
missing data
filters
multiple values
categorical behavior
```

For:

```text
sum
```

totals are naturally additive.

For:

```text
mean
```

the `All` total is a mean over the underlying values according to the pivot-table aggregation semantics; it is not necessarily the simple average of the displayed cell averages.

### Production rule

> Validate margins against the underlying raw data, not merely against the visible pivot cells.

---

# 37. Multiple Values in `pivot_table()`

You can pivot multiple measure columns:

```python
result = pd.pivot_table(
    df,
    index="country",
    columns="month",
    values=["revenue", "orders"],
    aggfunc="sum",
)
```

Now the output contains more than one value dimension.

Conceptually:

```text
revenue × month
orders  × month
```

---

# 38. MultiIndex Columns from Multiple Values

The result may have columns such as:

```text
(revenue, Jan)
(revenue, Feb)
(orders, Jan)
(orders, Feb)
```

This is a `MultiIndex` on the columns.

That is useful internally because the hierarchy is explicit.

It can be awkward for:

```text
CSV
Excel consumers
SQL tables
APIs
schema validators
```

---

# 39. Understanding MultiIndex Columns

A MultiIndex column has levels.

Example:

```text
level 0 = metric
level 1 = month
```

So:

```python
("revenue", "Jan")
```

means:

```text
metric = revenue
month  = Jan
```

This structure can be very useful during analytical work.

But downstream systems often prefer:

```text
revenue_Jan
```

rather than tuple labels.

---

# 40. Flattening MultiIndex Columns

A common readable strategy:

```python
result.columns = [
    "_".join(
        str(part)
        for part in column
        if part not in (None, "")
    ).rstrip("_")
    if isinstance(column, tuple)
    else str(column)
    for column in result.columns
]
```

This turns:

```text
("revenue", "Jan")
```

into:

```text
revenue_Jan
```

and:

```text
("orders", "Jan")
```

into:

```text
orders_Jan
```

## Why flatten?

Production file schemas are often easier to consume when columns are:

```text
single strings
predictable
stable
documented
```

---

# 41. Safer Flattening Helper

For repeated pipelines, use a tested helper:

```python
def flatten_columns(
    columns,
    separator="_",
):
    flattened = []

    for column in columns:
        if isinstance(column, tuple):
            parts = [
                str(part)
                for part in column
                if part not in (None, "")
            ]
            flattened.append(
                separator.join(parts)
            )
        else:
            flattened.append(str(column))

    return flattened
```

Then:

```python
result.columns = flatten_columns(
    result.columns
)
```

### Test cases

Include:

```text
ordinary string column
tuple with two levels
tuple with an empty level
tuple containing None
```

Do not assume all MultiIndexes have the same structure.

---

# 42. `stack()`

`stack` moves a column level onto the row index.

The mental model:

```text
columns
   ↓
index
```

Pandas documents `stack()` as moving prescribed column levels to the index. In pandas 3.0, the new `future_stack=True` implementation is the current/default implementation; its `dropna` and `sort` parameters do not affect the result and should not be supplied with that implementation. citeturn241491search2turn241491search3

---

# 43. `stack()` Example

Start with:

```python
wide = pd.DataFrame(
    {
        "Jan": [100, 200],
        "Feb": [120, 250],
    },
    index=pd.Index(
        ["IN", "US"],
        name="country",
    ),
)
```

Calling:

```python
longer = wide.stack()
```

moves:

```text
Jan
Feb
```

into an additional index level.

Conceptually:

```text
country  month
IN       Jan       100
         Feb       120
US       Jan       200
         Feb       250
```

Now:

```text
country + month
```

form the hierarchical index.

---

# 44. Why `stack()` Fits MultiIndex Data

Suppose columns already have two levels:

```text
revenue  Jan
revenue  Feb
orders   Jan
orders   Feb
```

`stack()` can move one column level into the index while preserving the other column level.

This makes it useful when working with analytical outputs that already contain hierarchical axes.

---

# 45. `unstack()`

`unstack` does the reverse conceptual movement:

```text
index
  ↓
columns
```

Pandas documents `unstack()` as pivoting an index level to the column axis. citeturn241491search7

Example:

```python
series = pd.Series(
    [100, 120, 200, 250],
    index=pd.MultiIndex.from_tuples(
        [
            ("IN", "Jan"),
            ("IN", "Feb"),
            ("US", "Jan"),
            ("US", "Feb"),
        ],
        names=["country", "month"],
    ),
    name="revenue",
)

wide = series.unstack(
    "month"
)
```

Conceptually:

```text
month      Jan  Feb
country
IN         100  120
US         200  250
```

---

# 46. `stack()` vs `unstack()`

| Operation | Movement | Mental model |
|---|---|---|
| `stack` | columns → index | Stack columns vertically into index levels |
| `unstack` | index → columns | Move an index level sideways into columns |

Memorize:

```text
stack
→ columns become rows/index levels

unstack
→ index levels become columns
```

These are often conceptual inverses, but exact round trips can depend on:

```text
missing combinations
ordering
duplicate keys
dtype
index/column metadata
```

---

# 47. `stack()` / `unstack()` and MultiIndex

A MultiIndex is the natural partner of these operations.

Example:

```python
index = pd.MultiIndex.from_product(
    [
        ["IN", "US"],
        ["Jan", "Feb"],
    ],
    names=["country", "month"],
)
```

This represents:

```text
(country, month)
```

as a hierarchical row index.

Then:

```python
series.unstack("month")
```

moves:

```text
month
```

to columns.

And:

```python
wide.stack()
```

can move a column level back into the index.

---

# 48. Groupby → `unstack()` Reporting Pattern

This is directly relevant to the roadmap exercise.

Start with:

```python
grouped = (
    df.groupby(
        ["country", "month"],
        dropna=False,
    )["revenue"]
    .sum()
)
```

Now:

```text
index:
country
month
```

Then:

```python
report = grouped.unstack("month")
```

The result becomes a report:

```text
month      Jan  Feb  Mar
country
IN         ...
US         ...
```

This pattern is useful for turning a grouped MultiIndex result into a human-readable matrix.

---

# 49. Flattening After `unstack()`

If unstacking multiple value dimensions creates MultiIndex columns, flatten them before writing to simple file formats.

Pattern:

```python
report = grouped.unstack()

report.columns = flatten_columns(
    report.columns
)
```

Then inspect:

```python
print(report.columns)
```

and assert:

```python
assert all(
    isinstance(column, str)
    for column in report.columns
)
```

---

# 50. `crosstab()`

`crosstab` is primarily a tool for **frequency tables**.

Think:

```text
dimension A
×
dimension B
→ counts
```

Examples:

```text
country × status
device_type × outcome
segment × order_state
```

Basic example:

```python
counts = pd.crosstab(
    df["country"],
    df["status"],
)
```

---

# 51. `crosstab()` Example

```python
df = pd.DataFrame(
    {
        "country": [
            "IN", "IN", "IN",
            "US", "US",
        ],
        "status": [
            "paid", "paid", "cancelled",
            "paid", "cancelled",
        ],
    }
)

counts = pd.crosstab(
    df["country"],
    df["status"],
)
```

Conceptually:

```text
status   cancelled  paid
country
IN              1      2
US              1      1
```

This answers:

> How frequently does each status occur inside each country?

---

# 52. `crosstab()` vs `pivot_table()`

| Tool | Primary purpose |
|---|---|
| `crosstab` | Frequency/count relationships |
| `pivot_table` | Flexible aggregation/reporting |

Use:

```python
pd.crosstab(...)
```

when the main question is:

```text
How many?
```

Use:

```python
pd.pivot_table(...)
```

when the main question is:

```text
What measure should be aggregated into these cells?
```

`crosstab` can support more than simple counts, but frequency analysis is its most natural role.

Do not use a frequency table API merely because the output visually resembles a pivot.

---

# 53. `wide_to_long()`

`wide_to_long()` is useful when a wide schema encodes a dimension inside column names.

Example:

```text
customer_id | sales_2023 | sales_2024 | sales_2025
```

The column names contain:

```text
measure = sales
dimension = year
```

The desired long form is:

```text
customer_id | year | sales
```

---

# 54. `wide_to_long()` Example

```python
wide = pd.DataFrame(
    {
        "customer_id": ["C1", "C2"],
        "sales_2023": [1000, 1200],
        "sales_2024": [1100, 1400],
        "sales_2025": [1300, 1500],
    }
)

long = pd.wide_to_long(
    wide,
    stubnames="sales",
    i="customer_id",
    j="year",
    sep="_",
    suffix=r"\d+",
).reset_index()
```

Conceptually:

```text
customer_id | year | sales
C1          | 2023 | 1000
C1          | 2024 | 1100
C1          | 2025 | 1300
C2          | 2023 | 1200
C2          | 2024 | 1400
C2          | 2025 | 1500
```

---

# 55. `wide_to_long()` Mental Model

Read:

```text
sales_2023
sales_2024
sales_2025
```

as:

```text
measure:
sales

dimension:
year

encoded dimension values:
2023
2024
2025
```

`wide_to_long` recovers the hidden dimension from the column names.

This is useful with legacy/reporting schemas where dimensions have already been embedded into names.

---

# 56. `wide_to_long()` Parameters

Important parameters:

### `stubnames`

The common measure prefix:

```python
stubnames="sales"
```

### `i`

Identifier columns:

```python
i="customer_id"
```

### `j`

New dimension column:

```python
j="year"
```

### `sep`

Separator:

```python
sep="_"
```

### `suffix`

Pattern matching the embedded dimension:

```python
suffix=r"\d+"
```

The exact regex needs to match the source naming convention.

---

# 57. `get_dummies()`

`get_dummies()` converts categorical variables into indicator columns.

Example:

```python
df = pd.DataFrame(
    {
        "country": ["IN", "US", "IN", "GB"],
    }
)

encoded = pd.get_dummies(
    df,
    columns=["country"],
)
```

Conceptually:

```text
country_IN
country_US
country_GB
```

Each row contains an indicator for the observed category.

Current pandas documentation describes `get_dummies` as converting categorical variables into 0/1 indicator variables and supports options such as `dummy_na`, `columns`, `sparse`, `drop_first`, and `dtype`. citeturn241491search5

---

# 58. `get_dummies()` Example

```python
df = pd.DataFrame(
    {
        "customer_id": ["C1", "C2", "C3"],
        "segment": [
            "Gold",
            "Silver",
            "Gold",
        ],
    }
)

encoded = pd.get_dummies(
    df,
    columns=["segment"],
    dtype="int8",
)
```

Conceptually:

```text
customer_id | segment_Gold | segment_Silver
C1          | 1            | 0
C2          | 0            | 1
C3          | 1            | 0
```

The exact default dtype can differ from the example because this code intentionally requests `int8`.

---

# 59. One-Hot Encoding and the ML Connection

One-hot encoding is common when an algorithm expects numeric indicator features.

For example:

```text
country
IN
US
GB
```

becomes:

```text
country_IN
country_US
country_GB
```

This is a representation transformation.

The important Data Engineering lesson here is:

> A single logical dimension can become many physical columns.

That can be convenient for modeling.

It can also be expensive.

---

# 60. Column Explosion with `get_dummies()`

Suppose:

```text
product_id
```

has:

```text
100,000 unique values
```

One-hot encoding could create on the order of:

```text
100,000 indicator columns
```

for that one categorical feature.

If you have:

```text
millions of rows
×
100,000 categories
```

you have created a very wide feature matrix.

Potential effects:

```text
memory pressure
wide serialization
slow scans
large metadata overhead
difficult schemas
```

This is the **column explosion** problem.

---

# 61. High-Cardinality Examples

Be cautious with one-hot encoding for:

```text
user_id
product_id
transaction_id
URL
device_id
email
```

These can have very high cardinality.

One-hot encoding is not automatically wrong, but the representation is usually driven by the downstream modeling/design problem rather than by a generic "encode every category" rule.

---

# 62. `get_dummies()` and Missing Categories

Pandas also supports:

```python
dummy_na=True
```

when you explicitly want a separate missing-value indicator.

Example:

```python
encoded = pd.get_dummies(
    df,
    columns=["country"],
    dummy_na=True,
)
```

This can distinguish:

```text
country = missing
```

from:

```text
country = one of the known categories
```

The choice is semantic.

Do not assume missing should always become a dedicated category.

---

# 63. `from_dummies()` as a Round-Trip Companion

Current pandas also provides `from_dummies()` to reverse an appropriate dummy-coded representation. citeturn241491search10

Example concept:

```python
recovered = pd.from_dummies(
    encoded[
        [
            "country_IN",
            "country_US",
            "country_GB",
        ]
    ],
    sep="_",
)
```

The more important lesson is:

```text
encoding
→ changed representation
→ test what information remains recoverable
```

---

# 64. Missing Cells Created by Reshaping

> **Roadmap concept:** missing cells created by reshaping must be distinguished from observed zero values.

This deserves its own mental model.

Suppose source data is:

```text
country | month | revenue
IN      | Jan   | 100
IN      | Mar   | 120
```

The set of observed keys is:

```text
(IN, Jan)
(IN, Mar)
```

There is no:

```text
(IN, Feb)
```

When you create a wide matrix with:

```python
pivot(...)
```

pandas may create the structural cell:

```text
IN × Feb
```

with:

```text
NaN
```

That cell did not exist in the input.

---

# 65. Structural Missingness vs Source Missingness

A missing cell after reshaping can be caused by:

### Structural absence

No row existed for that dimension combination.

### Source missing value

The row existed, but the measure itself was missing.

These are not necessarily the same.

Example:

```text
country | month | revenue
IN      | Jan   | NaN
```

After pivot, `IN × Jan` is missing.

But this means:

```text
row existed
measure missing
```

Contrast with:

```text
country | month | revenue
IN      | Feb   | [no row]
```

After pivot, `IN × Feb` is also missing.

Now the meaning is:

```text
combination absent
```

The shape alone does not tell you which story is true.

---

# 66. Missing vs Zero Validation

A strong production approach is to maintain enough source information to distinguish:

```text
observation exists?
```

from:

```text
measure value?
```

For example:

```python
df["observation_count"] = 1
```

Then:

```python
summary = pd.pivot_table(
    df,
    index="country",
    columns="month",
    values="observation_count",
    aggfunc="sum",
)
```

This helps answer:

> Was there at least one source observation for this cell?

Do not use this as a universal data model, but it is a useful diagnostic technique.

---

# 67. Shape-Driven Performance

Reshaping changes computational shape.

Two DataFrames can contain the same logical information but have very different costs.

Example:

```text
wide:
1,000,000 rows × 3,000 columns
```

versus:

```text
long:
3,000,000,000 logical observation rows
```

Neither is automatically better.

The right question is:

> Which shape matches the workload and stays within resource limits?

---

# 68. Very Wide DataFrames — wide frames with thousands of columns

A wide DataFrame may be created by:

```text
pivot
pivot_table
get_dummies
feature engineering
sensor matrices
report generation
```

Risks include:

```text
large schema
column metadata overhead
expensive serialization
memory pressure
hard-to-read code
tooling limitations
```

A thousand columns is already operationally different from twenty.

Ten thousand columns is another scale again.

---

# 69. Very Long DataFrames — long frames with millions of rows

A long DataFrame may contain:

```text
country
month
product
metric
value
```

instead of hundreds or thousands of metric columns.

Potential benefits:

```text
stable schema
easy filtering
easy grouping
simple schema evolution
```

Potential costs:

```text
more rows
larger row-level overhead
more repeated dimension values
more scanning in some workloads
```

Again:

> Shape is an engineering trade-off, not a universal preference.

---

# 70. Shape Budget Thinking

Before an expensive reshape, estimate:

```text
input shape
+
dimension cardinalities
+
expected output shape
+
memory implications
```

This is your **shape budget**.

## Melt estimate

For:

```text
R rows
K value columns
```

expect roughly:

```text
R × K
```

rows.

## Pivot estimate

Potential width is related to:

```text
unique index values
×
unique column values
```

subject to observed combinations, missing combinations, and other options.

## One-hot estimate

Potential width is related to:

```text
number of categorical values
```

for each encoded feature.

---

# 71. Example Shape Budget

Suppose:

```text
input rows = 2,000,000
month columns = 12
```

A melt can create approximately:

```text
24,000,000 rows
```

before considering downstream filtering.

That may be correct.

It may also be a large intermediate dataset.

Before running:

```python
df.melt(...)
```

ask:

```text
Can the machine hold the result?
Is long format required?
Can the operation be pushed downstream?
Can I process partitions independently?
```

Chunked processing belongs to Topic 13, so this chapter only teaches the shape-awareness decision.

---

# 72. Round-Trip Validation

The roadmap requires:

```text
wide → long → wide
```

and then:

```text
assert original == reconstructed
```

The purpose is to learn:

> A reshape can be tested for information preservation.

---

# 73. Simple Lossless Round Trip

Start:

```python
wide = pd.DataFrame(
    {
        "country": ["IN", "US"],
        "Jan": [100, 200],
        "Feb": [120, 250],
        "Mar": [90, 300],
    }
)
```

Melt:

```python
long = wide.melt(
    id_vars=["country"],
    value_vars=["Jan", "Feb", "Mar"],
    var_name="month",
    value_name="revenue",
)
```

Pivot:

```python
wide_again = (
    long.pivot(
        index="country",
        columns="month",
        values="revenue",
    )
    .reset_index()
)
```

Now compare after normalizing column order.

---

# 74. Round-Trip Normalization

Pivoted columns may be reordered.

Normalize:

```python
wide_normalized = (
    wide.sort_index(
        axis=1
    )
    .reset_index(drop=True)
)

wide_again = (
    wide_again.sort_index(
        axis=1
    )
    .reset_index(drop=True)
)
```

Then:

```python
from pandas.testing import assert_frame_equal

assert_frame_equal(
    wide_normalized,
    wide_again,
)
```

The key point is:

> Normalize only differences that are legitimately caused by the reshape.

Do not sort away a semantic problem just to make a test pass.

---

# 75. Round-Trip Conditions

A clean wide → long → wide round trip generally needs:

```text
unique identifying keys
no unintended aggregation
no information discarded
consistent value typing
controlled missingness
known column ordering differences
known index metadata
```

If the long form contains duplicate:

```text
country + month
```

then:

```python
pivot()
```

cannot reconstruct the original one-to-one mapping without an additional rule.

---

# 76. When Round Trips Are Not Lossless

A round trip may fail or change information when you:

- aggregate duplicates;
- drop rows;
- collapse categories;
- replace missing with zeros;
- remove identifier columns;
- discard an index;
- encode categories without preserving the category mapping;
- change dtypes.

This is why:

```text
reshape
```

and:

```text
reshape + aggregate
```

must be treated as different operations.

---

# 77. SQL / Data Model Connection

Many SQL systems expose operations conceptually similar to:

```text
PIVOT
UNPIVOT
```

The pandas relationships are:

| Concept | pandas |
|---|---|
| UNPIVOT | `melt()` |
| PIVOT with unique cells | `pivot()` |
| PIVOT with aggregation | `pivot_table()` |
| Frequency cross-tabulation | `crosstab()` |

Exact syntax and capabilities differ across database engines.

The useful engineering lesson is:

```text
wide ↔ long
```

is a data-model transformation, not merely a visualization trick.

---

# 78. Production Reshaping Pattern: Spreadsheet Input

Suppose a monthly spreadsheet contains:

```text
customer_id | Jan | Feb | Mar | Apr
```

First move it to long:

```python
long = wide.melt(
    id_vars=["customer_id"],
    value_vars=["Jan", "Feb", "Mar", "Apr"],
    var_name="month",
    value_name="revenue",
)
```

Now downstream logic can work at:

```text
customer + month
```

grain.

This makes:

```text
filters
groupby
validation
SQL loading
```

more predictable.

---

# 79. Production Reshaping Pattern: Reporting

Suppose the trusted long table is:

```text
country
month
revenue
```

Create the reporting matrix:

```python
report = pd.pivot_table(
    long,
    index="country",
    columns="month",
    values="revenue",
    aggfunc="sum",
    margins=True,
)
```

Then:

```text
validate totals
flatten columns if required
write report
```

The wide shape is a reporting product, not necessarily the canonical storage shape.

---

# 80. Production Reshaping Pattern: Frequency Analysis

For:

```text
country × status
```

counts:

```python
counts = pd.crosstab(
    orders["country"],
    orders["status"],
)
```

Use this for:

```text
data-quality reports
operational monitoring
distribution analysis
QA checks
```

---

# 81. Production Reshaping Pattern: Legacy Columns

If a legacy source has:

```text
sales_2023
sales_2024
sales_2025
```

recover:

```text
year
sales
```

with:

```python
pd.wide_to_long(...)
```

Then normalize into the pipeline's preferred shape.

---

# 82. Production Reshaping Pattern: Feature Matrix

A model-training feature matrix may require:

```text
one row per entity
many numeric feature columns
```

That is a legitimate wide shape.

But before creating it:

```text
What is the entity grain?
How many features?
How many categories?
How much memory?
Does the model need dense columns?
```

A wide output can be correct for the model while being inappropriate as the canonical storage model.

---

# 83. Production Reshaping Principles

## Principle 1 — Define the grain

```text
one row represents...
```

## Principle 2 — Identify dimensions and measures

Do not let column names become an undocumented schema.

## Principle 3 — Check key uniqueness

Especially before:

```python
pivot()
```

## Principle 4 — Do not aggregate duplicates blindly

Determine what duplicate observations mean.

## Principle 5 — Preserve missing-value meaning

Do not turn:

```text
no observation
```

into:

```text
zero
```

without a contract.

## Principle 6 — Budget shape before executing

Estimate:

```text
rows
columns
memory
```

## Principle 7 — Keep output schemas predictable

Flatten MultiIndex columns when required by consumers.

## Principle 8 — Validate round trips where losslessness is expected

---

# 84. Reshaping Anti-Patterns

## Anti-pattern 1 — Automatic `fill_value=0`

```python
pd.pivot_table(
    df,
    ...,
    fill_value=0,
)
```

### Why it looks reasonable

Reports often prefer zeros.

### Risk

Missing and zero can mean different things.

### Safer alternative

First determine whether:

```text
no cell
=
zero
```

is guaranteed.

---

# 85. Anti-Pattern 2 — Sum Away Duplicate Pivot Keys

```python
pd.pivot_table(
    df,
    ...,
    aggfunc="sum",
)
```

### Why it looks reasonable

It solves the duplicate-key error.

### Risk

The duplicates may be:

```text
bad source records
```

rather than:

```text
legitimate transactions to aggregate
```

### Safer alternative

Profile duplicates first.

---

# 86. Anti-Pattern 3 — Leaving MultiIndex Columns in Output Files

### Why it looks reasonable

The internal DataFrame is readable enough in a notebook.

### Risk

Downstream systems may not handle hierarchical columns cleanly.

### Safer alternative

Flatten into documented strings before file/database export.

---

# 87. Anti-Pattern 4 — One-Hot Encoding High-Cardinality IDs

```python
pd.get_dummies(
    df,
    columns=["user_id"],
)
```

### Why dangerous

Potentially creates one column per user.

### Safer alternative

Use a representation appropriate to the ML/data model rather than blindly expanding identifiers.

---

# 88. Anti-Pattern 5 — Reshaping Without Shape Prediction

### Code

```python
long = df.melt(...)
```

### Risk

A seemingly harmless 5-million-row input can become a 60-million-row intermediate.

### Safer alternative

Calculate:

```text
rows × value columns
```

first.

---

# 89. Anti-Pattern 6 — Assuming Wide Is Always Better for Reports

Wide is visually attractive.

But a report with:

```text
500 columns
```

may be difficult to:

- validate;
- serialize;
- consume;
- maintain.

Choose the report grain and required columns deliberately.

---

# 90. Anti-Pattern 7 — Assuming Long Is Always Better

A wide feature matrix may be exactly what an ML consumer requires.

The correct question is:

> Which consumer and workload need which shape?

---

# 91. Anti-Pattern 8 — Failing to Reconcile Totals

If revenue should be preserved:

```python
before_total = df["revenue"].sum()
```

and after a valid reshape:

```python
after_total = ...
```

compare them.

A reshape that unexpectedly changes the total may reveal:

```text
dropped rows
duplicate aggregation
wrong measure selection
incorrect missing handling
```

---

# 92. Reconciliation After Reshaping

For a pure reshaping that does not filter or aggregate, a measure total should usually remain the same.

Example:

```python
before_total = long_df["revenue"].sum()

wide = long_df.pivot(
    index="country",
    columns="month",
    values="revenue",
)

after_total = (
    wide.to_numpy(
        dtype="float64"
    ).sum()
)
```

For simple non-missing data, these should reconcile.

But if the data contains:

```text
missing values
aggregation
filters
```

the validation must account for those semantics.

---

# 93. Reconciliation with Aggregation

If:

```python
pivot_table(
    ...,
    aggfunc="sum",
)
```

combines multiple source rows into one cell, total revenue may still reconcile because `sum` is additive.

But this must be tested.

For a grouping:

```python
before = df["revenue"].sum()

after = (
    df.groupby(
        ["country", "month"],
        dropna=False,
    )["revenue"]
    .sum()
    .sum()
)
```

A valid additive aggregation should reconcile when:

```text
rows are all included
same value semantics
missing handling is compatible
```

---

# 94. Reconciliation Warning: Mean

Suppose you pivot with:

```python
aggfunc="mean"
```

The sum of displayed means is not expected to equal the source sum.

Similarly:

```text
mean of means
```

is not generally the same as:

```text
global mean
```

This is another reason to define the metric before choosing `aggfunc`.

---

# 95. Validation Strategy

## For `melt`

Validate:

```text
expected output rows
identifier columns preserved
expected variable values
expected value column
```

## For `pivot`

Validate:

```text
index + columns pair unique
expected row dimension
expected column dimension
```

## For `pivot_table`

Validate:

```text
aggregation function
expected cell values
expected margins
expected missing behavior
```

## For `stack` / `unstack`

Validate:

```text
expected index levels
expected columns
expected shape
```

## For `get_dummies`

Validate:

```text
expected categories
expected columns
expected indicator values
```

## For round trips

Validate:

```text
structure
values
dtypes where relevant
ordering after normalization
```

---

# 96. `melt` Validation Example

```python
expected_rows = (
    len(wide) * 3
)

long = wide.melt(
    id_vars=["country"],
    value_vars=["Jan", "Feb", "Mar"],
    var_name="month",
    value_name="revenue",
)

assert len(long) == expected_rows

assert set(
    long["month"]
) == {
    "Jan",
    "Feb",
    "Mar",
}
```

---

# 97. `pivot` Validation Example

Before:

```python
duplicate_count = (
    df.duplicated(
        subset=["country", "month"]
    ).sum()
)

assert duplicate_count == 0
```

Then:

```python
wide = df.pivot(
    index="country",
    columns="month",
    values="revenue",
)
```

The assertion makes the key contract visible.

---

# 98. `pivot_table` Validation Example

```python
result = pd.pivot_table(
    df,
    index="country",
    columns="month",
    values="revenue",
    aggfunc="sum",
)
```

For a hand-computed fixture:

```python
assert result.loc[
    "IN", "Jan"
] == 150
```

This proves that duplicate rows were intentionally summed.

---

# 99. Testing Flattened Columns

```python
flat = flatten_columns(
    result.columns
)

assert all(
    isinstance(column, str)
    for column in flat
)

assert len(flat) == len(
    set(flat)
)
```

The second assertion is important.

Flattening can accidentally create name collisions.

For example:

```text
("a", "b_c")
("a_b", "c")
```

both flatten to:

```text
a_b_c
```

unless the naming contract handles collisions.

---

# 100. Flattening Collision Prevention

A production helper should detect collisions.

```python
def flatten_columns_checked(
    columns,
    separator="_",
):
    flattened = []

    for column in columns:
        if isinstance(column, tuple):
            parts = [
                str(part)
                for part in column
                if part not in (None, "")
            ]
            name = separator.join(parts)
        else:
            name = str(column)

        flattened.append(name)

    if len(flattened) != len(
        set(flattened)
    ):
        raise ValueError(
            "Flattened column names are not unique."
        )

    return flattened
```

This converts a silent schema problem into a visible failure.

---

# 101. Debugging Section

The following cases are common reshape failures.

---

## Debug 1 — Wrong `id_vars`

### Buggy code

```python
df.melt(
    id_vars=["Jan"]
)
```

### Expected

Country should remain an identifier.

### Actual

January becomes an identifier.

### Root cause

The roles of dimension and measure were misclassified.

### Correct

```python
df.melt(
    id_vars=["country"],
    value_vars=["Jan", "Feb"],
)
```

### Prevention

State:

```text
identifier columns =
```

before melting.

---

## Debug 2 — Wrong `value_vars`

### Buggy

```python
df.melt(
    id_vars=["country"]
)
```

### Expected

Only monthly columns should be melted.

### Actual

Metadata columns may also be melted.

### Correct

```python
df.melt(
    id_vars=["country", "source_system"],
    value_vars=["Jan", "Feb", "Mar"],
)
```

### Prevention

Explicitly list measured columns in production contracts.

---

## Debug 3 — Unexpected Number of Rows After `melt`

### Symptom

Expected 120 rows, got 240.

### Root cause

Twice as many value columns were melted.

### Inspect

```python
print(value_vars)
print(len(value_vars))
```

### Prevention

Predict:

```text
input_rows × value_column_count
```

---

## Debug 4 — Metadata Was Melted

### Symptom

```text
load_date
```

appears inside:

```text
month
```

### Root cause

It was not included in `id_vars`.

### Correct

Keep metadata columns as identifiers.

---

## Debug 5 — `pivot()` Raises on Duplicate Pairs

### Symptom

`ValueError`.

### Root cause

`index + columns` pair is not unique.

### Inspect

```python
df.groupby(
    ["country", "month"]
).size().loc[lambda s: s > 1]
```

### Correct

Choose:

```text
aggregate
or
fix duplicate data
```

before pivoting.

---

## Debug 6 — Wrong `pivot_table` Aggregation

### Symptom

Monthly revenue seems too low.

### Root cause

`mean` was used where `sum` was required.

### Correct

Use the business metric's proper aggregation.

### Prevention

Write the metric definition before choosing `aggfunc`.

---

## Debug 7 — `fill_value=0` Hides Missing Data

### Symptom

Report shows clean zeros everywhere.

### Root cause

Missing cells were filled without verifying semantics.

### Correct

Keep missing when:

```text
no observation ≠ zero
```

### Prevention

Document the meaning of a missing cell.

---

## Debug 8 — Misunderstanding `margins=True`

### Symptom

`All` row does not match the sum of visible averages.

### Root cause

`mean` is not additive.

### Correct

Validate margins against raw data and aggregation semantics.

---

## Debug 9 — Unexpected MultiIndex Columns

### Symptom

Columns look like:

```text
('revenue', 'Jan')
```

### Root cause

Multiple `values` or multiple aggregation levels.

### Correct

Keep MultiIndex for analytical work or flatten for downstream file schemas.

---

## Debug 10 — Incorrect MultiIndex Flattening

### Symptom

Two distinct columns become the same string.

### Root cause

Naive joining of levels.

### Correct

Use a tested flatten helper that checks uniqueness.

---

## Debug 11 — Confusing `stack` and `unstack`

### Symptom

Dimension moves in the opposite direction.

### Root cause

Wrong mental model.

### Correct

```text
stack:
columns → index

unstack:
index → columns
```

---

## Debug 12 — Wrong MultiIndex Level

### Symptom

The wrong dimension moves to columns.

### Root cause

Unstacked:

```python
unstack(0)
```

instead of:

```python
unstack("month")
```

### Prevention

Name index levels and use names.

---

## Debug 13 — Using `crosstab` for Revenue

### Symptom

You need:

```text
revenue
```

but created counts.

### Root cause

`crosstab` was chosen for a metric aggregation problem.

### Correct

Use `pivot_table`.

---

## Debug 14 — `wide_to_long` Pattern Does Not Match

### Symptom

Year column is missing or source columns remain untouched.

### Root cause

The `stubnames`, `sep`, or `suffix` pattern does not match actual column names.

### Inspect

```python
print(df.columns.tolist())
```

### Prevention

Test the naming pattern on a tiny fixture first.

---

## Debug 15 — One-Hot Encoding Explodes Width

### Symptom

Thousands of columns are created.

### Root cause

High category cardinality.

### Inspect

```python
print(
    df["product_id"].nunique()
)
```

### Correct

Choose a representation suited to the downstream use case.

---

## Debug 16 — Huge DataFrame After Reshape

### Symptom

Memory use spikes.

### Root causes

```text
melt expansion
pivot width
get_dummies
large MultiIndex
```

### Correct

Predict shape and estimate memory before running.

---

## Debug 17 — Missing Cells Interpreted as Zeros

### Symptom

Business report says "zero sales" where source had no observation.

### Root cause

`fill_value=0`.

### Correct

Preserve missingness or use an explicitly justified zero policy.

---

## Debug 18 — Duplicate Rows Were Silently Aggregated

### Symptom

`pivot_table` produces plausible values, but source duplicates were never examined.

### Root cause

Aggregation masked a data-quality issue.

### Correct

Profile key duplicates before deciding `aggfunc`.

---

## Debug 19 — Round Trip Does Not Equal Original

### Symptom

`assert_frame_equal` fails.

### Possible causes

```text
column order
row order
index metadata
dtype
duplicate keys
aggregation
missing cells
```

### Correct

Classify the difference.

Normalize only expected structural differences.

---

## Debug 20 — Totals Changed

### Symptom

Revenue before and after reshape differs.

### Root causes

```text
rows dropped
duplicate aggregation
measure column changed
missing values handled differently
```

### Correct

Reconcile source and reshaped totals.

---

## Debug 21 — Column Order Causes False Failure

### Symptom

Values are correct but test fails.

### Root cause

Expected and actual columns are ordered differently.

### Correct

Normalize column order if ordering is not part of the business contract.

---

## Debug 22 — Row Order Causes False Failure

### Symptom

Round-trip has the same rows but in different order.

### Correct

Sort by the intended identifiers before equality testing if order is not semantically meaningful.

Do not sort blindly if order is meaningful to the consumer.

---

# 102. Edge Cases

## 102.1 Empty DataFrame

```python
empty = pd.DataFrame(
    {
        "country": pd.Series(
            dtype="string"
        ),
        "Jan": pd.Series(
            dtype="float64"
        ),
    }
)

long = empty.melt(
    id_vars=["country"],
    value_vars=["Jan"],
    var_name="month",
    value_name="revenue",
)
```

Expected:

```text
zero rows
predictable schema
```

Test the schema.

---

## 102.2 One-row DataFrame

A single row with three value columns becomes:

```text
3 long rows
```

Predict before execution.

---

## 102.3 One-column DataFrame

If the only column is an identifier:

```python
df.melt(
    id_vars=["country"]
)
```

there may be no measured columns.

This should be treated as a schema/contract case rather than assumed to produce a meaningful dataset.

---

## 102.4 No `value_vars`

If there are no value columns to melt, the transformation has no measurement dimension.

Production code should validate this explicitly.

---

## 102.5 Duplicate Pivot Pairs

```text
(country, month)
```

appears multiple times.

Expected:

```text
pivot
→ error
```

unless uniqueness has been restored.

---

## 102.6 Every Pair Is Duplicated

If every target cell contains multiple observations, `pivot_table` requires a defined aggregation.

---

## 102.7 Missing Values in Long Data

```text
country | month | revenue
IN      | Jan   | NaN
```

After pivot, the cell stays missing.

Do not automatically interpret this as:

```text
no row existed
```

---

## 102.8 Missing Combination

No row exists for:

```text
IN + Feb
```

The pivot can create a structural missing cell.

Distinguish this from a source row with:

```text
revenue = NaN
```

---

## 102.9 True Zero

```text
revenue = 0
```

must remain distinguishable from:

```text
revenue = NaN
```

when business semantics require the distinction.

---

## 102.10 All-Zero Data

A matrix can legitimately contain:

```text
0
```

in every cell.

Do not "clean" it into missing because zero looks suspicious.

---

## 102.11 No Observations for an Entire Dimension Combination

Example:

```text
country = GB
month = Jan
```

never appears.

Decide whether the report should display:

```text
NaN
```

or:

```text
0
```

based on the source contract.

---

## 102.12 Multiple Aggregation Values

When values include:

```text
revenue
orders
```

expect a MultiIndex on columns unless you flatten intentionally.

---

## 102.13 Empty Categories

Categorical variables can carry categories not observed in the current batch.

Understand how the chosen reshaping operation handles them and test output shape rather than assuming category metadata equals observed data.

---

## 102.14 One Unique Category

A pivot with one category can still create a single-column report.

Do not build code that assumes at least two categories.

---

## 102.15 High-Cardinality `get_dummies`

Thousands of categories can produce thousands of columns.

Estimate width first.

---

## 102.16 MultiIndex with One Level

A one-level index behaves differently from a multi-level index in some reshaping workflows.

Name levels where practical.

---

## 102.17 MultiIndex with Multiple Levels

Always know:

```text
which level
```

you intend to move.

Prefer named levels when possible.

---

## 102.18 Columns with Spaces

Wide source columns may contain:

```text
sales 2023
```

or:

```text
Revenue Jan
```

Use a naming contract before reshaping and validate resulting names.

---

## 102.19 Duplicate Source Rows

Duplicate records can look like legitimate duplicate pivot keys.

Profile them before choosing:

```text
deduplication
or
aggregation
```

---

## 102.20 Totals Changed After Deduplication

Deduplicating before a pivot can change totals.

That may be correct if source duplicates are errors.

It must be measured and documented.

---

# 103. Performance Engineering

Reshaping can be a memory problem before it is a CPU problem.

Major cost drivers include:

```text
input rows
output rows
output columns
unique categories
number of MultiIndex levels
number of measured columns
duplication/aggregation
dtype representation
```

---

# 104. Measure Shape and Memory

Use:

```python
rows, columns = df.shape
```

and:

```python
memory_bytes = (
    df.memory_usage(
        deep=True
    ).sum()
)
```

A useful summary:

```python
print(
    f"rows={len(df):,}, "
    f"columns={df.shape[1]:,}, "
    f"memory={memory_bytes / 1024**2:.1f} MiB"
)
```

This gives you a concrete baseline.

---

# 105. `melt` Performance

Melt can increase row count dramatically.

Example:

```text
5,000,000 rows
×
12 month columns
=
60,000,000 long rows
```

That may be correct.

But every generated row has overhead.

Before execution:

```text
estimate output rows
estimate required memory
confirm consumer actually needs long form
```

---

# 106. `pivot` Performance

Pivot can increase width.

If:

```text
100,000 unique countries
×
10,000 unique products
```

were all represented as potential axes, the theoretical matrix space would be enormous.

Even if only a fraction of combinations exist, the reshaped representation can be unsuitable.

Do not create giant matrices just because the API allows it.

---

# 107. `pivot_table` Performance

`pivot_table` combines:

```text
grouping
+
aggregation
+
reshape
```

So its cost depends on:

- number of groups;
- dimension cardinality;
- number of measures;
- aggregation function;
- output width.

Use only the value columns and dimensions you need.

---

# 108. `get_dummies` Performance

The biggest risk is often width.

Example:

```text
1,000,000 rows
×
20,000 categories
```

can produce a very large feature matrix.

Consider:

```text
category cardinality
sparse/dense representation
downstream model requirements
```

The appropriate representation depends on the consumer.

Current pandas supports a `sparse` option, which can be relevant when the resulting indicator matrix is sufficiently sparse. citeturn241491search5

---

# 109. MultiIndex Overhead

MultiIndex is powerful but carries hierarchy metadata.

A report with:

```text
3 column levels
```

and thousands of columns can become more complex to inspect and serialize.

Use MultiIndex intentionally for analytical steps.

Flatten when the downstream interface requires simple names.

---

# 110. Unnecessary Intermediate DataFrames

Avoid retaining huge intermediates longer than necessary.

For example:

```python
long = wide.melt(...)
filtered = long.loc[...]
report = filtered.pivot_table(...)
```

This may be easy to read but can require substantial memory at large scale.

At production scale, consider:

```text
shape
memory
lifecycle of intermediates
```

without sacrificing readability prematurely.

---

# 111. Serialization Considerations

Wide output can create:

```text
very large headers
very wide records
```

Long output can create:

```text
many more rows
```

The best serialization layout depends on the downstream format and consumer.

For example:

```text
Parquet
SQL tables
CSV
Excel
```

have different operational characteristics.

This chapter focuses on choosing and validating shape; the detailed file-I/O contract is Topic 02.

---

# 112. Benchmarking Reshapes

Use:

```python
from time import perf_counter

start = perf_counter()

result = df.melt(
    ...
)

elapsed = (
    perf_counter() - start
)

print(
    f"{elapsed:.3f} seconds"
)
```

Do not invent benchmark numbers.

Measure:

```text
same input
same output semantics
same environment
same columns
same dtypes
```

Record:

```text
input rows
input columns
output rows
output columns
memory before
memory after
runtime
pandas version
Python version
environment
```

---

# 113. Shape-Driven Performance Experiment

Build a family of datasets:

```text
100,000 rows
1,000,000 rows
5,000,000 rows
```

and:

```text
3 value columns
6 value columns
12 value columns
```

For `melt`, compare:

```text
rows × value_columns
```

against:

```text
runtime
memory
```

The goal is not to memorize a benchmark number.

The goal is to observe how shape affects cost.

---

# 114. Production Rule for Performance

Do not claim:

```text
long is faster
```

or:

```text
wide is faster
```

or:

```text
pivot is faster than melt
```

as a universal rule.

Use:

> Choose the representation according to semantics and consumer requirements, then benchmark the actual workload.

---

# 115. Shape Budget Before Production Reshape

Before running a large reshape, document:

```text
Input shape:
Expected output shape:
Peak intermediate shape:
Expected memory class:
Downstream consumer:
Required schema:
```

Example:

```text
Input:
5,000,000 rows × 14 columns

Melt:
12 measured columns

Expected long rows:
60,000,000

Consumer:
analytics table

Risk:
large intermediate
```

This is an engineering review artifact.

---

# 116. Prediction-First Reshape Exercises

## Exercise 1 — Melt

```text
50,000 rows
12 month columns
```

Predict:

```text
600,000 long rows
```

before executing.

---

## Exercise 2 — Pivot

```text
10 countries
12 observed months
```

If every combination exists:

```text
10 output rows
12 value columns
```

If only 90 combinations exist, do not assume the source has information for all 120 possible combinations.

---

## Exercise 3 — Pivot duplicates

```text
IN + Jan = 3 observations
US + Jan = 2 observations
```

Question:

> Can `pivot()` choose one value?

Answer:

```text
No.
```

You need uniqueness or an aggregation policy.

---

## Exercise 4 — Get dummies

```text
country = 5 categories
```

Question:

> How many category columns are potentially created?

Answer:

```text
5
```

subject to options such as dropping a category.

---

## Exercise 5 — Get dummies at scale

```text
product_id = 100,000 unique values
```

Question:

> What is the width risk?

Answer:

```text
potentially ~100,000 indicator columns
```

---

## Exercise 6 — Stack

A DataFrame has:

```text
2 index rows
3 columns
```

Question:

> If you stack the single column level, what happens conceptually?

Answer:

```text
column labels become an additional row-index level
```

---

## Exercise 7 — Unstack

A Series has:

```text
country × month
```

in its MultiIndex.

Question:

> What happens with `unstack("month")`?

Answer:

```text
month becomes columns
```

---

## Exercise 8 — Missing vs zero

Source has:

```text
IN + Jan + revenue=0
US + Jan + [no row]
```

Question:

> Should both cells necessarily become zero after pivot?

Answer:

```text
No.
```

The first is an observed zero. The second is an absent observation.

---

## Exercise 9 — Margins

A `pivot_table` uses:

```python
aggfunc="mean"
```

Question:

> Is the All column necessarily the simple average of visible month cells?

Answer:

```text
No.
```

Validate it against the underlying data semantics.

---

## Exercise 10 — Round trip

You have:

```text
2 countries × 3 months
```

Question:

> How many long rows should `melt` create?

Answer:

```text
6
```

Question:

> Can `pivot` reverse it?

Answer:

```text
Yes,
if country + month is unique
and no information was discarded.
```

---

# 117. SQL / Data Engineering Quick Comparison

| Data operation | pandas |
|---|---|
| Unpivot | `melt()` |
| Pivot with unique cells | `pivot()` |
| Pivot with aggregation | `pivot_table()` |
| Cross-tabulation | `crosstab()` |

Conceptual SQL/reporting mental model:

```text
UNPIVOT
  ↓
melt

PIVOT with unique cell mapping
  ↓
pivot

PIVOT with duplicate cell aggregation
  ↓
pivot_table
```

Exact SQL syntax differs by database engine.

---

# 118. Hands-on Exercise — `reshape_reports.py`

> **Do not create `reshape_reports.py` for this Markdown task.**
>
> This section is the complete implementation specification for the learner.

## Exercise objective

Build a production-style reporting transformation that demonstrates:

```text
wide → long
long → wide
duplicate-key detection
aggregation during reshape
missing-vs-zero reasoning
MultiIndex manipulation
column flattening
round-trip validation
shape prediction
```

Every task must begin with a written shape contract.

---

# 119. Exercise Task 1 — Melt a Spreadsheet-Style Monthly File

Input example:

```text
customer_id | country | Jan | Feb | Mar | ... | Dec
```

Goal:

```text
customer_id | country | month | revenue
```

Required operation:

```python
long = wide.melt(
    id_vars=[
        "customer_id",
        "country",
    ],
    value_vars=[
        "Jan",
        "Feb",
        "Mar",
        # ...
        "Dec",
    ],
    var_name="month",
    value_name="revenue",
)
```

Before running, calculate:

```text
expected_rows
=
input_rows × 12
```

unless the chosen source structure differs.

### Required assertions

```python
assert len(long) == (
    len(wide) * 12
)
```

and:

```python
assert set(
    long["month"]
) == {
    "Jan", "Feb", "Mar",
    # ...
    "Dec",
}
```

### Production questions

```text
What does one long row represent?
Which columns are identifiers?
Which columns are measures?
Can a month value be missing?
Does missing mean no data or zero?
```

---

# 120. Exercise Task 2 — Country × Month Revenue Report

Take the long dataset:

```text
country
month
revenue
```

Create:

```text
country × month revenue report
```

Required operation:

```python
report = pd.pivot_table(
    long,
    index="country",
    columns="month",
    values="revenue",
    aggfunc="sum",
    margins=True,
)
```

### Required explanation

State:

```text
What does each row represent?
What does each month column represent?
What does All mean?
Why is sum the correct or incorrect aggregation?
```

Do not choose `sum` by habit.

### Required validation

Compare:

```python
source_total = (
    long["revenue"].sum()
)
```

to the appropriately interpreted total in the report.

---

# 121. Exercise Task 3 — Demonstrate `pivot()` Failure

Construct:

```text
country | month | revenue
IN      | Jan   | 100
IN      | Jan   | 125
```

Attempt:

```python
wide = df.pivot(
    index="country",
    columns="month",
    values="revenue",
)
```

Expected:

```text
ValueError
```

### Required investigation

Find:

```python
df.groupby(
    ["country", "month"]
).size().loc[
    lambda s: s > 1
]
```

Then decide:

```text
legitimate multiple observations
or
bad duplicate key
```

### Option A — Aggregate

```python
fixed = pd.pivot_table(
    df,
    index="country",
    columns="month",
    values="revenue",
    aggfunc="sum",
)
```

### Option B — Resolve duplicates

If duplicates are invalid, correct the source or deduplicate under a documented business rule.

The learner must explain why the chosen solution is semantically correct.

---

# 122. Exercise Task 4 — `unstack()` a Groupby Result

Start with:

```python
grouped = (
    long.groupby(
        ["country", "month"],
        dropna=False,
    )["revenue"]
    .sum()
)
```

Then:

```python
report = grouped.unstack(
    "month"
)
```

### Required tasks

1. Inspect the MultiIndex before unstacking.
2. Predict the report's row and column dimensions.
3. Unstack month.
4. Inspect the resulting columns.
5. Flatten any MultiIndex columns.
6. Assert the expected schema.

### Production question

Why might:

```python
unstack()
```

be useful for a report but not necessarily ideal as the canonical pipeline representation?

---

# 123. Exercise Task 5 — Wide → Long → Wide Round Trip

Start with:

```text
wide
```

Melt:

```text
wide → long
```

Then:

```text
long → wide
```

using:

```python
pivot()
```

Normalize:

```text
column ordering
index
```

only where necessary.

Then:

```python
from pandas.testing import assert_frame_equal

assert_frame_equal(
    original,
    reconstructed,
)
```

### Required condition

The round trip must preserve:

```text
identifier values
dimension values
measure values
missingness
```

### Required failure exercise

Break the condition by introducing:

```text
duplicate country-month rows
```

or:

```text
aggregated values
```

and observe why the round trip stops being lossless.

---

# 124. Exercise Shape Contract

Before each exercise task, write:

```text
Current shape:
Target shape:
Current grain:
Target grain:
Identifier columns:
Measure columns:
Potential duplicate keys:
Expected row count:
Expected column count:
Missing-cell policy:
Aggregation rule:
Validation rule:
```

This is the production mindset the exercise is meant to build.

---

# 125. Exercise Tests

When the learner later implements `reshape_reports.py`, the accompanying tests should verify:

```text
melt row count
melt identifier preservation
melt variable/value names
pivot duplicate failure
pivot_table aggregation
margins
unstack result
flattened column names
round-trip equality
missing-vs-zero semantics
total reconciliation
```

No test should exist merely to demonstrate that pandas can execute a method.

---

# 126. Testing Strategy with pytest

Use small deterministic fixtures.

A reshape test should answer:

```text
Did the transformation preserve the intended information?
Did it create the intended shape?
Did it introduce or remove rows?
Did it aggregate?
Did it change missingness?
```

---

# 127. `melt` Tests

Test:

```python
def test_melt_row_count():
    long = wide.melt(
        id_vars=["country"],
        value_vars=[
            "Jan",
            "Feb",
            "Mar",
        ],
        var_name="month",
        value_name="revenue",
    )

    assert len(long) == (
        len(wide) * 3
    )
```

Also test:

```text
country values preserved
month values correct
revenue values correct
```

---

# 128. `pivot` Tests

Test successful unique-key pivot:

```python
def test_pivot_unique_pairs():
    result = df.pivot(
        index="country",
        columns="month",
        values="revenue",
    )

    assert result.loc[
        "IN", "Jan"
    ] == 100
```

Then test duplicate failure.

---

# 129. `pivot_table` Tests

Test:

```text
sum
mean
count
fill_value
margins
multiple values
```

Example:

```python
def test_pivot_table_sum():
    result = pd.pivot_table(
        df,
        index="country",
        columns="month",
        values="revenue",
        aggfunc="sum",
    )

    assert result.loc[
        "IN", "Jan"
    ] == 150
```

---

# 130. `stack` / `unstack` Tests

Verify:

```text
expected index levels
expected columns
expected shape
```

Example:

```python
def test_unstack_month():
    result = (
        grouped.unstack(
            "month"
        )
    )

    assert "Jan" in result.columns
```

For stronger tests, compare against a fully hand-built expected DataFrame.

---

# 131. `crosstab` Tests

```python
counts = pd.crosstab(
    df["country"],
    df["status"],
)

assert counts.loc[
    "IN", "paid"
] == 2
```

Test the exact frequency relationship.

---

# 132. `wide_to_long` Tests

Verify:

```text
customer_id preserved
year extracted correctly
sales value preserved
```

Example:

```python
assert set(
    long["year"].astype(str)
) == {
    "2023",
    "2024",
    "2025",
}
```

---

# 133. `get_dummies` Tests

Verify expected indicator columns:

```python
encoded = pd.get_dummies(
    df,
    columns=["country"],
)

expected_columns = {
    "country_IN",
    "country_US",
    "country_GB",
}

assert expected_columns <= set(
    encoded.columns
)
```

Also validate actual indicator values.

---

# 134. Round-Trip Test

Use:

```python
from pandas.testing import (
    assert_frame_equal,
)
```

Example:

```python
assert_frame_equal(
    original.sort_index(axis=1),
    reconstructed.sort_index(axis=1),
)
```

If row order can change:

```python
original_normalized = (
    original
    .sort_values(["country"])
    .reset_index(drop=True)
)

reconstructed_normalized = (
    reconstructed
    .sort_values(["country"])
    .reset_index(drop=True)
)

assert_frame_equal(
    original_normalized,
    reconstructed_normalized,
)
```

Only normalize dimensions that are not business-significant.

---

# 135. Testing Missing vs Zero

Create a fixture with both:

```text
observed zero
absent combination
```

Then verify that reshaping does not accidentally make them indistinguishable.

For example:

```python
source = pd.DataFrame(
    {
        "country": [
            "IN",
        ],
        "month": [
            "Jan",
        ],
        "revenue": [
            0,
        ],
    }
)
```

And deliberately omit:

```text
IN + Feb
```

The test should prove:

```text
Jan = 0
Feb = missing
```

before any policy-driven fill.

---

# 136. Reconciliation Test

For additive revenue:

```python
before = (
    long["revenue"].sum()
)

report = pd.pivot_table(
    long,
    index="country",
    columns="month",
    values="revenue",
    aggfunc="sum",
)

after = (
    report
    .to_numpy(
        dtype="float64"
    )
    .sum()
)

assert before == after
```

This exact check assumes the matrix contains the same additive observations and missing-value semantics are compatible.

---

# 137. Edge-Case Test Matrix

| Case | Required test |
|---|---|
| Empty input | shape/schema remains predictable |
| One row | expected melt expansion |
| One column | no accidental measurement assumptions |
| Duplicate pivot pair | `pivot` raises |
| Duplicate pair aggregated | expected `aggfunc` result |
| Missing value | remains missing unless policy says otherwise |
| Missing combination | structural missingness is understood |
| Zero | remains distinguishable from missing |
| MultiIndex | expected levels |
| Flattening | names are unique |
| High cardinality | output width estimated |
| `get_dummies` | expected indicators |
| Round trip | values preserved |
| Margins | totals match raw semantics |

---

# 138. Shape-Driven Performance Checklist

```text
[ ] What is input row count?
[ ] What is input column count?
[ ] How many value columns are being melted?
[ ] How many unique pivot-column values exist?
[ ] How many duplicate key pairs exist?
[ ] How many categories are being one-hot encoded?
[ ] What is expected output shape?
[ ] Could output have thousands of columns?
[ ] Could output have tens of millions of rows?
[ ] What is memory before?
[ ] What is expected memory pressure?
[ ] Is the shape required by the consumer?
[ ] Can the transformation be simplified?
[ ] Have I benchmarked the real workload?
```

---

# 139. Production Reshaping Checklist

## Before reshaping

```text
[ ] What does one row represent?
[ ] What are my dimensions?
[ ] What are my measures?
[ ] What is the current shape?
[ ] What is the target shape?
[ ] What is the target grain?
[ ] Which keys should be unique?
[ ] Could duplicates exist?
[ ] What does missing mean?
[ ] What does zero mean?
[ ] Could the reshape create millions of rows?
[ ] Could the reshape create thousands of columns?
```

## During reshaping

```text
[ ] Did I select the correct identifiers?
[ ] Did I select the correct measures?
[ ] Did I predict output shape?
[ ] If duplicates exist, did I define an aggregation rule?
[ ] Did I preserve missing-value meaning?
[ ] Did I inspect the result?
[ ] Did I inspect MultiIndex levels?
```

## After reshaping

```text
[ ] Does the output grain match the contract?
[ ] Are row/column counts expected?
[ ] Are columns readable?
[ ] Are MultiIndex columns intentionally handled?
[ ] Are missing cells meaningful?
[ ] Are totals reconciled?
[ ] Did tests pass?
[ ] Is memory acceptable?
```

---

# 140. Reshape Decision Tree

```text
Do I need wide → long?
        |
       YES
        ↓
      melt()

Do I need long → wide
and every index/column pair is unique?
        |
       YES
        ↓
      pivot()

Do I need long → wide
and duplicate target cells require aggregation?
        |
       YES
        ↓
   pivot_table()

Do I have a MultiIndex
and want an index level moved to columns?
        |
       YES
        ↓
    unstack()

Do I have columns
and want a column level moved to the index?
        |
       YES
        ↓
      stack()

Do I need a frequency table?
        |
       YES
        ↓
   crosstab()

Do column names encode a dimension
such as sales_2023?
        |
       YES
        ↓
  wide_to_long()

Do I need indicator columns for categories?
        |
       YES
        ↓
  get_dummies()
```

The decision is based on **intent**, not familiarity with method names.

---

# 141. Wide / Long / Pivot Decision Guide

```text
Source is spreadsheet-style:
country | Jan | Feb | Mar
        ↓
Need pipeline-friendly observations?
        ↓
melt()

Source is long:
country | month | revenue
        ↓
Need a unique report matrix?
        ↓
pivot()

Source is long with repeated country-month observations?
        ↓
Need aggregation?
        ↓
pivot_table()

Source is a MultiIndex object?
        ↓
Need index → columns?
        ↓
unstack()

Need columns → index?
        ↓
stack()
```

---

# 142. `melt` / `pivot` Round-Trip Design

Ideal pattern:

```text
WIDE
  |
  | melt
  v
LONG
  |
  | pivot
  v
WIDE AGAIN
```

For a lossless round trip:

```text
identifying key is unique
+
no aggregation
+
no row filtering
+
no information discarded
```

Then:

```python
assert_frame_equal(
    original,
    reconstructed,
)
```

after legitimate normalization of:

```text
index
row order
column order
```

---

# 143. Common Mistakes Summary

| Mistake | Why it happens | Correct approach |
|---|---|---|
| `fill_value=0` hiding missing data | Zero looks cleaner in reports | Preserve missing unless zero is explicitly the correct meaning |
| Exploding column counts with `get_dummies` on high-cardinality columns | Every category becomes a physical column | Estimate cardinality and choose an appropriate representation |
| Leaving `MultiIndex` columns in output files | MultiIndex is convenient during analysis | Flatten and validate unique names for simple output schemas |
| Using `pivot` when target pairs are duplicated | Assumes one value per cell | Validate uniqueness first |
| Using `pivot_table` as an automatic `pivot` repair | Aggregation masks the root cause | Determine whether duplicates are legitimate |
| Melting metadata columns | `value_vars` omitted or `id_vars` incomplete | Explicitly define identifiers and measures |
| Wrong row-count expectations after `melt` | Expansion was not predicted | Calculate input rows × value columns |
| Confusing `stack` with `unstack` | Axis movement is unclear | columns → index = stack; index → columns = unstack |
| Using `crosstab` for metric aggregation | Frequency output resembles a pivot | Use `pivot_table` for arbitrary measures |
| Ignoring shape before one-hot encoding | Focus stays on syntax | Estimate category cardinality and output width |
| Treating missing cells as zero | Structural absence is mistaken for numeric zero | Define missing/zero semantics |
| Aggregating duplicates blindly | The first solution that avoids an error seems convenient | Profile duplicate keys and define business meaning |
| Not reconciling totals | Reshape "looks correct" | Compare business measures before/after |
| Assuming long is always better | Pipelines often prefer long | Choose based on semantics and consumer |
| Assuming wide is always better | Reports often look better wide | Evaluate schema, memory, and consumer needs |

The first three mistakes above are explicitly called out by the roadmap.

> **Roadmap wording:** `fill_value=0` hiding missing data; exploding column counts with `get_dummies` on high-cardinality columns; leaving `MultiIndex` columns in output files.
 fileciteturn18file0

---

# 144. Production Shape Review

Before approving a reshape in code review, ask:

```text
1. What does one input row represent?
2. What does one output row represent?
3. Which dimensions moved?
4. Which measures moved?
5. Did row count increase?
6. Did column count increase?
7. Did duplicates exist?
8. Did aggregation occur?
9. What does a missing output cell mean?
10. Does zero mean the same thing?
11. Are MultiIndex labels expected?
12. Could the shape become operationally large?
13. Did business totals reconcile?
14. Is the output schema documented?
```

This checklist is more useful than memorizing isolated API signatures.

---

# 145. Data Product Thinking

A reshaped DataFrame that leaves your transformation boundary should have:

```text
grain
schema
null semantics
ordering contract
aggregation semantics
shape expectations
```

Example:

```text
Dataset:
country_month_revenue

Grain:
one row per country-month

Columns:
country
month
revenue

Key:
(country, month)

Missing policy:
missing means no recorded observation

Zero policy:
zero means observed zero revenue

Aggregation:
sum of source transactions

Output consumer:
reporting layer
```

Now the reshape is a defined product.

---

# 146. Production Scenario: E-Commerce Reporting

Source:

```text
order rows
```

Pipeline aggregation:

```text
country + month
```

Report:

```text
country | Jan | Feb | Mar | All
```

A clean architecture is often:

```text
transactional/long data
        ↓
validated aggregation
        ↓
wide report
```

The wide table is a consumer-specific representation.

---

# 147. Production Scenario: Banking Reporting

Illustrative example:

```text
transaction data
        ↓
branch + month
        ↓
revenue / transaction metrics
        ↓
report matrix
```

Important checks:

```text
branch identifiers
month representation
duplicate source records
missing branches
zero-activity branches
total reconciliation
```

This is an illustrative data-engineering scenario, not a universal banking architecture.

---

# 148. Production Scenario: ML Feature Matrix

Source:

```text
customer + feature + value
```

Potential model input:

```text
customer | feature_A | feature_B | feature_C
```

This is a legitimate wide representation.

But before pivoting:

```text
is customer + feature unique?
how many features?
how many customers?
how much memory?
```

If the feature cardinality is huge, a wide matrix can become difficult to manage.

---

# 149. Production Scenario: Device Metrics

A telemetry table might be:

```text
device_id
timestamp
metric_name
value
```

A reporting layer might reshape into:

```text
device_id
timestamp
temperature
pressure
battery
```

That can be useful for a specific consumer.

But the long form may be a better canonical representation because:

```text
new metrics
```

can be added without changing the table's structural schema.

Again:

> Shape is chosen for the consumer and workload.

---

# 150. Production Scenario: Legacy Spreadsheet Migration

Legacy:

```text
sales_2023
sales_2024
sales_2025
```

Migration pattern:

```text
legacy wide
    ↓
wide_to_long
    ↓
canonical long
    ↓
validation
    ↓
Gold/report-specific wide output when needed
```

This separates:

```text
canonical data model
```

from:

```text
presentation format
```

---

# 151. Production Validation: Before and After

For any reshape, capture:

```text
shape_before
shape_after
measure_total_before
measure_total_after
duplicate_key_count_before
missing_cell_count_after
output_column_count
memory_before
memory_after
```

Example:

```python
metrics_before = {
    "rows": len(df),
    "columns": df.shape[1],
    "revenue": df["revenue"].sum(),
}
```

Then after the transformation create the corresponding metrics.

This creates an auditable reshape record.

---

# 152. Shape Reconciliation Template

```python
before_rows = len(df)
before_columns = df.shape[1]

before_total = (
    df["revenue"].sum()
)

# reshape

after_rows = len(result)
after_columns = result.shape[1]

# calculate an equivalent after_total

print(
    {
        "before_rows": before_rows,
        "after_rows": after_rows,
        "before_columns": before_columns,
        "after_columns": after_columns,
        "before_total": before_total,
        "after_total": after_total,
    }
)
```

The exact reconciliation formula depends on the shape and aggregation.

The point is to make the change measurable.

---

# 153. Performance Experiment Design

A serious benchmark should compare:

```text
same source data
same business semantics
same final result
```

Example questions:

```text
How does melt runtime scale with value column count?
How does pivot width affect memory?
How does get_dummies width affect memory?
What happens when category cardinality rises?
```

Use:

```python
from time import perf_counter
```

and:

```python
df.memory_usage(deep=True).sum()
```

Do not benchmark only on a toy DataFrame if the production issue happens at millions of rows.

---

# 154. What Not to Optimize Yet

This chapter should not become:

```text
time-series optimization
method chaining
Copy-on-Write
chunked processing
Spark
Polars
DuckDB
```

Those are covered elsewhere in the roadmap.

Here, optimize your reasoning about:

```text
shape
memory
columns
rows
duplicates
missingness
```

and know when the reshape itself is the bottleneck.

---

# 155. Master Checklist

## Conceptual

- [ ] I can explain wide and long.
- [ ] I can explain tidy data.
- [ ] I can state what one row represents.
- [ ] I can identify dimensions and measures.
- [ ] I understand that reshape can change data representation semantics.

## `melt`

- [ ] `id_vars`
- [ ] `value_vars`
- [ ] `var_name`
- [ ] `value_name`
- [ ] row-count prediction
- [ ] identifier preservation

## `pivot`

- [ ] `index`
- [ ] `columns`
- [ ] `values`
- [ ] duplicate-key failure
- [ ] uniqueness validation

## `pivot_table`

- [ ] `aggfunc`
- [ ] sum
- [ ] mean
- [ ] count
- [ ] `fill_value`
- [ ] missing-vs-zero semantics
- [ ] `margins`
- [ ] multiple values
- [ ] MultiIndex columns

## MultiIndex

- [ ] `stack`
- [ ] `unstack`
- [ ] named levels
- [ ] flattening

## Other reshape tools

- [ ] `crosstab`
- [ ] `wide_to_long`
- [ ] `get_dummies`

## Advanced

- [ ] one-hot encoding
- [ ] column explosion
- [ ] missing cells
- [ ] missing vs zero
- [ ] wide performance
- [ ] long performance
- [ ] shape budgeting
- [ ] memory awareness

## Validation

- [ ] duplicate checks
- [ ] shape checks
- [ ] total reconciliation
- [ ] round-trip `assert_frame_equal`
- [ ] schema checks

---

# 156. Checkpoint

The roadmap checkpoint is the minimum completion standard. fileciteturn18file0

## 1. Explain long vs wide and when each is appropriate

You should be able to say:

```text
Long:
one observation per row; dimensions remain columns.

Wide:
one dimension is often represented across columns.

Long is often a strong pipeline default because schema and filtering
remain stable as dimension values change.

Wide can be appropriate for reports, matrices, and consumers that require it.
```

---

## 2. Explain why `pivot` fails where `pivot_table` succeeds

You should be able to say:

```text
pivot requires each index + columns pair to identify one value.

pivot_table can handle repeated pairs because it applies an aggregation rule.
```

You must also explain:

> `pivot_table` is not merely a workaround. Its `aggfunc` defines what duplicate observations mean.

---

## 3. Flatten MultiIndex columns

Given:

```text
("revenue", "Jan")
("revenue", "Feb")
("orders", "Jan")
("orders", "Feb")
```

produce:

```text
revenue_Jan
revenue_Feb
orders_Jan
orders_Feb
```

and verify the names remain unique.

---

## 4. Distinguish missing cells from true zeros

You should be able to explain:

```text
missing cell
≠
observed zero
```

and give a concrete business example.

---

# 157. Additional Self-Check

Answer these without looking back.

### Question 1

What does `id_vars` mean?

### Question 2

What does `value_vars` mean?

### Question 3

If a 100-row DataFrame is melted across 12 value columns, what is the direct expected long row count?

### Question 4

What combination must be unique for:

```python
wide = df.pivot(
    index="country",
    columns="month",
    values="revenue",
)
```

to work without aggregation?

### Question 5

Why is `pivot_table(..., aggfunc="sum")` not an automatic data-cleaning operation?

### Question 6

What does `fill_value=0` potentially hide?

### Question 7

What does `margins=True` add?

### Question 8

Why can `mean` margins differ from the average of displayed cell means?

### Question 9

What does `stack()` move?

### Question 10

What does `unstack()` move?

### Question 11

What is `crosstab()` primarily useful for?

### Question 12

When is `wide_to_long()` especially convenient?

### Question 13

Why can `get_dummies()` create a schema problem?

### Question 14

What is column explosion?

### Question 15

Why can a missing output cell after pivot mean different things?

### Question 16

What should a round-trip test prove?

### Question 17

What should you predict before a reshape?

### Question 18

What business measure should you reconcile?

### Question 19

When should MultiIndex columns be flattened?

### Question 20

Why is shape a production concern?

---

# 158. Cheat Sheet

## Wide → Long

```python
df.melt(
    id_vars=...,
    value_vars=...,
    var_name=...,
    value_name=...,
)
```

Mental model:

```text
melt
=
wide → long
```

---

## Long → Wide

```python
df.pivot(
    index=...,
    columns=...,
    values=...,
)
```

Requires:

```text
unique index + columns combinations
```

---

## Pivot with aggregation

```python
pd.pivot_table(
    df,
    index=...,
    columns=...,
    values=...,
    aggfunc=...,
    fill_value=...,
    margins=True,
)
```

Mental model:

```text
pivot_table
=
group + aggregate + reshape
```

---

## Stack

```python
df.stack()
```

Mental model:

```text
columns → index
```

For pandas 3.0's current stack implementation, treat `future_stack=True` behavior as the current model and follow the current documentation for the `dropna`/`sort` implications. citeturn241491search2

---

## Unstack

```python
df.unstack(...)
```

Mental model:

```text
index → columns
```

---

## Frequency table

```python
pd.crosstab(
    df["country"],
    df["status"],
)
```

Mental model:

```text
crosstab
=
frequency relationship
```

---

## Embedded dimensions

```python
pd.wide_to_long(
    df,
    stubnames="sales",
    i="customer_id",
    j="year",
    sep="_",
    suffix=r"\d+",
)
```

Mental model:

```text
sales_2023
→ sales + year=2023
```

---

## One-hot encoding

```python
pd.get_dummies(
    df,
    columns=["country"],
)
```

Mental model:

```text
category
→ indicator columns
```

---

## MultiIndex flattening

```python
df.columns = [
    "_".join(
        str(part)
        for part in column
        if part not in (None, "")
    )
    if isinstance(column, tuple)
    else str(column)
    for column in df.columns
]
```

Production requirement:

```text
verify resulting names are unique
```

---

## Round-trip testing

```python
from pandas.testing import (
    assert_frame_equal,
)

assert_frame_equal(
    original,
    reconstructed,
)
```

Normalize only:

```text
legitimate ordering/index differences
```

---

## Shape checks

```python
df.shape
```

```python
df.memory_usage(
    deep=True
).sum()
```

---

## Benchmark

```python
from time import perf_counter

start = perf_counter()

result = ...

elapsed = (
    perf_counter() - start
)

print(
    f"{elapsed:.3f} seconds"
)
```

---

# 159. SQL / Data Engineering Quick Reference

| SQL/reporting idea | pandas |
|---|---|
| Unpivot | `melt()` |
| Pivot unique cells | `pivot()` |
| Pivot aggregated cells | `pivot_table()` |
| Frequency cross-tab | `crosstab()` |

Use this as a conceptual mapping, not a guarantee of identical database syntax.

---

# 160. Reshaping Learning Order

Follow this progression.

## Basic

1. Why reshaping matters
2. Long vs wide
3. Tidy-data mental model
4. `melt`
5. `id_vars`
6. `value_vars`
7. `var_name`
8. `value_name`
9. predicting row expansion
10. `pivot`
11. `index`
12. `columns`
13. `values`
14. pivot uniqueness requirement
15. pivot failure on duplicates

## Intermediate

16. `pivot_table`
17. `aggfunc`
18. `fill_value`
19. `margins`
20. multiple values
21. MultiIndex columns
22. flattening MultiIndex columns
23. `stack`
24. `unstack`
25. `stack` vs `unstack`
26. `crosstab`

## Advanced

27. `wide_to_long`
28. encoded dimensions in column names
29. `get_dummies`
30. column explosion
31. missing cells
32. missing vs zero
33. shape-driven performance
34. very wide frames
35. very long frames
36. round-trip validation
37. shape-budget thinking
38. production reshaping decisions

Then:

39. SQL/data-model connection
40. `reshape_reports.py`
41. debugging
42. testing
43. edge cases
44. performance
45. reconciliation
46. production checklist
47. checkpoint
48. common mistakes
49. cheat sheet

---

# 161. Prediction-First Master Loop

For every important reshape:

```text
1. State the current grain.
        ↓
2. Identify dimensions.
        ↓
3. Identify measures.
        ↓
4. State the target grain.
        ↓
5. Predict row count.
        ↓
6. Predict column count.
        ↓
7. Check duplicate keys.
        ↓
8. Decide whether aggregation is needed.
        ↓
9. Decide what missing cells mean.
        ↓
10. Execute.
        ↓
11. Inspect shape and schema.
        ↓
12. Assert expected values.
        ↓
13. Reconcile totals.
        ↓
14. Measure memory/runtime.
        ↓
15. Explain why the result is correct.
```

This is the core skill of Topic 08.

---

# 162. Final Production Mental Model

```text
                 RESHAPING
                     |
       +-------------+-------------+
       |                           |
    DIMENSIONS                  MEASURES
       |                           |
       +-------------+-------------+
                     |
                   SHAPE
                     |
        +------------+------------+
        |            |            |
      LONG          WIDE       MULTIINDEX
        |            |            |
      melt          pivot      stack/unstack
                     |
               pivot_table
                     |
                  aggregate
                     |
              missing semantics
                     |
               output schema
                     |
             shape + memory budget
                     |
              validation/reconcile
```

The production sequence is:

```text
DEFINE GRAIN
    ↓
IDENTIFY DIMENSIONS + MEASURES
    ↓
CHECK UNIQUENESS
    ↓
PREDICT SHAPE
    ↓
CHOOSE RESHAPE OPERATION
    ↓
DEFINE DUPLICATE/AGGREGATION SEMANTICS
    ↓
DEFINE MISSING VS ZERO
    ↓
EXECUTE
    ↓
VALIDATE SHAPE
    ↓
VALIDATE VALUES
    ↓
RECONCILE MEASURES
    ↓
CHECK MEMORY/PERFORMANCE
    ↓
PUBLISH DEFINED OUTPUT SCHEMA
```

---

# 163. Topic 08 Exit Criteria

Do not finish this topic merely because you can remember:

```python
df.melt(...)
df.pivot(...)
```

Finish when you can take an unfamiliar DataFrame and answer:

```text
What does one row represent?

Which columns are dimensions?

Which columns are measures?

Is the current representation wide or long?

What shape does the consumer need?

How many rows should the reshape create?

How many columns should it create?

Are the target keys unique?

If they are not unique, what do duplicate observations mean?

Should I use pivot or pivot_table?

What aggregation function is semantically correct?

What does a missing cell mean?

Does zero mean the same thing?

Will MultiIndex appear?

Should MultiIndex columns be flattened?

Could get_dummies create thousands of columns?

Could melt create tens of millions of rows?

How will I validate the result?

How will I reconcile business totals?

Can I prove a wide → long → wide round trip?

How much memory will the chosen shape require?
```

That is the production-grade reshaping skill this topic is designed to build.

---

# 164. Official pandas References

The chapter targets current pandas 3.x APIs. Re-check the exact installed version when reproducing examples.

- pandas reshaping and pivot tables user guide:  
  https://pandas.pydata.org/docs/user_guide/reshaping.html

- `DataFrame.pivot`:  
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pivot.html

- `pandas.pivot_table`:  
  https://pandas.pydata.org/docs/reference/api/pandas.pivot_table.html

- `DataFrame.stack`:  
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.stack.html

- `DataFrame.unstack`:  
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.unstack.html

- `pandas.get_dummies`:  
  https://pandas.pydata.org/docs/reference/api/pandas.get_dummies.html

- `pandas.from_dummies`:  
  https://pandas.pydata.org/docs/reference/api/pandas.from_dummies.html

- pandas general functions:  
  https://pandas.pydata.org/docs/reference/general_functions.html

The current pandas 3.0 documentation confirms the core reshaping family (`pivot`, `pivot_table`, `stack`, `unstack`, `melt`, `wide_to_long`, `get_dummies`, and `crosstab`) and documents the pandas 3.0 behavior of `stack` and `observed=True` in `pivot_table`. citeturn241491search3turn241491search1

---

# 165. Final Master Checklist

## Basics

- [ ] long/tidy format
- [ ] wide format
- [ ] when long is appropriate
- [ ] `melt`
- [ ] `id_vars`
- [ ] `value_vars`
- [ ] `var_name`
- [ ] `value_name`
- [ ] `pivot`
- [ ] duplicate index/column pair behavior

## Intermediate

- [ ] `pivot_table`
- [ ] `aggfunc`
- [ ] `fill_value`
- [ ] `margins`
- [ ] multiple values
- [ ] `stack`
- [ ] `unstack`
- [ ] MultiIndex levels
- [ ] `crosstab`
- [ ] flattening MultiIndex columns

## Advanced

- [ ] `wide_to_long`
- [ ] columns such as `sales_2023`
- [ ] `get_dummies`
- [ ] one-hot encoding
- [ ] column-explosion risk
- [ ] missing cells after reshape
- [ ] missing vs zero
- [ ] shape-driven performance
- [ ] thousands of columns
- [ ] millions of rows

## Learning requirements

- [ ] wide → long → wide round trip
- [ ] output-shape prediction
- [ ] `reshape_reports.py` complete specification
- [ ] spreadsheet-style monthly melt
- [ ] country × month revenue report
- [ ] `pivot` failure due to duplicates
- [ ] fix using `pivot_table` or justified deduplication
- [ ] `unstack` groupby result
- [ ] flatten output columns
- [ ] round-trip assertion
- [ ] debugging
- [ ] testing
- [ ] edge cases
- [ ] performance
- [ ] reconciliation
- [ ] production patterns
- [ ] checkpoint
- [ ] common mistakes
- [ ] cheat sheet

---

# Final One-Page Memory Anchor

```text
LONG
= one observation per row

WIDE
= dimensions represented across columns

melt
= wide → long

pivot
= long → wide
  requires unique index + columns pairs

pivot_table
= long → wide + aggregation

stack
= columns → index

unstack
= index → columns

crosstab
= frequency/count table

wide_to_long
= recover dimensions encoded in column names

get_dummies
= category → indicator columns
```

And the most important production questions are:

```text
What is my grain?
What are my dimensions?
What are my measures?
What keys must be unique?
How many rows will I create?
How many columns will I create?
Will I aggregate?
What does missing mean?
What does zero mean?
Can the shape fit in memory?
Can I reconcile totals?
Can I prove the reshape preserved meaning?
```

That is the standard to carry forward into Topic 09 and the rest of the production pandas curriculum.
