# 11 — Method Chaining and `pipe`

---

## Chapter purpose

You already know the core pandas operations from Topics 01–10. This topic is about **how to compose those operations into a readable, testable, reusable DataFrame pipeline**.

The roadmap motivation is:

> You now know the operations. This topic is about writing them as a readable, testable pipeline instead of a long script of mutations.

Method chaining is not merely a formatting trick. Used deliberately, it can make the data flow visible, keep transformations local, make reusable functions easy to compose, and give you clear places to inspect and validate intermediate states.

The target production principle is:

> A good pandas pipeline should make the sequence of transformations visible, make each important step independently testable, and make failures observable.

A second principle is just as important:

> Method chaining is useful only when it improves clarity. A short, readable chain is preferable to a clever, unreadable chain.

This chapter therefore teaches both **how to chain** and **when to stop chaining**.

## Learning outcomes

By the end of this chapter, you should be able to:

- explain why pandas methods can be chained;
- identify whether the next method can receive the object returned by the previous method;
- use `assign()` to create derived columns inside a chain;
- use lambdas in `assign()` when later expressions depend on earlier expressions in the same `assign()`;
- use `pipe()` to insert DataFrame-level custom functions;
- design small, named, testable transformation functions;
- format long chains clearly;
- break a chain into named intermediate results when that improves comprehension;
- insert logging and invariant checks with `pipe()`;
- explain why `inplace=True` is discouraged in this chapter's style;
- understand the design and trade-offs of custom DataFrame accessors;
- unit-test individual pipeline steps and integration-test the full pipeline;
- build the `silver_pipeline.py` exercise with at least eight `pipe()` steps.

## How to study this topic

Follow the roadmap's learning method rather than reading the chapter as an API reference:

1. Read one concept at a time and predict the object returned by each operation.
2. Take the messiest script you built in Topics 05–08 and rewrite it as a sequence of named `pipe()` steps.
3. Compare the original and refactored versions for readability, testability, and debugging.
4. For every meaningful step, write down its input, output, and invariant.
5. Practice breaking long chains at real phase boundaries instead of forcing everything into one expression.
6. Unit-test individual functions on tiny frames, then integration-test the complete chain.
7. Re-run the same pipeline at representative data sizes when performance or memory matters.

Use this loop repeatedly:

```text
Predict
  ↓
Execute
  ↓
Inspect
  ↓
Assert
  ↓
Explain
```

The goal is not to memorize chaining syntax. The goal is to become able to look at a DataFrame pipeline and explain the state transition at every stage.

# 1. Why Method Chaining Matters

A Data Engineering transformation is easier to maintain when a reader can answer:

1. What is the input?
2. What happens first?
3. What does each step change?
4. Where can validation occur?
5. What is the final output?

A mutation-heavy script can hide the sequence because the same variable is repeatedly reassigned or mutated.

```python
df = load_data()

df = df.rename(columns={
    "qty": "quantity",
    "price": "unit_price",
})
df = df.astype({"quantity": "int64"})
df = df.query("quantity > 0")
df["revenue"] = df["quantity"] * df["unit_price"]
df = df.sort_values("revenue", ascending=False)
df = df.drop(columns=["debug_flag"])
```

This is not inherently wrong. Every statement is understandable in isolation. The problem appears as the pipeline becomes larger: transformation order becomes harder to scan, reusable logic gets mixed with one-off logic, and intermediate validation often gets omitted.

The equivalent flow can be expressed as a chain:

```python
result = (
    df
    .rename(columns={
        "qty": "quantity",
        "price": "unit_price",
    })
    .astype({"quantity": "int64"})
    .query("quantity > 0")
    .assign(revenue=lambda d: d["quantity"] * d["unit_price"])
    .sort_values("revenue", ascending=False)
    .drop(columns=["debug_flag"])
)
```

The chain makes the direction of travel visible:

```text
raw DataFrame
    ↓
rename
    ↓
astype
    ↓
query
    ↓
assign
    ↓
sort
    ↓
drop
    ↓
result
```

The important engineering question is not "Does chaining look nicer?" It is:

> Does this representation make the transformation easier to understand, validate, test, and change?

# 2. What Is Method Chaining?

Method chaining means calling another method on the object returned by the previous method.

The simple shape is:

```text
object
  ↓
method 1
  ↓
returned object
  ↓
method 2
  ↓
returned object
  ↓
method 3
```

In pandas, many DataFrame transformations return another DataFrame. That makes code such as `df.rename(...).query(...).sort_values(...)` possible.

```python
result = (
    df
    .rename(columns={"qty": "quantity"})
    .query("quantity > 0")
    .sort_values("quantity", ascending=False)
)
```

A chain works only when the output of one operation is a valid input for the next operation.

That sounds obvious, but it is a common debugging skill.

For example, `sort_values()` returns a DataFrame, so another DataFrame method can follow it. By contrast, `shape` returns a tuple. You cannot continue with `.query()` on that tuple.

```python
shape = df.shape
print(shape)

# This is wrong because `shape` is a tuple, not a DataFrame:
# df.shape.query("quantity > 0")
```

### Mental model

Do not memorize "everything can be chained."

Memorize:

> **A method can be chained only when the object it returns supports the next operation you want.**

# 3. Returning New DataFrames and Knowing Return Types

For production work, learn to ask the return-type question before chaining:

> What object comes out of this step?

Typical pandas operations can return:

| Return kind | Example | Can I keep using DataFrame methods? |
| --- | --- | --- |
| DataFrame | `rename`, `query`, `assign`, `sort_values` | Usually yes |
| Series | `df["revenue"]` | No longer a DataFrame |
| scalar | `df["revenue"].sum()` | No DataFrame chain after this |
| tuple | `df.shape` | No |
| Index | `df.columns` | No |
| boolean | `df["x"].isna().all()` | No |

The exact return type is part of the method contract.

A useful beginner exercise is to inspect it:

```python
result = df.rename(columns={"qty": "quantity"})

print(type(result))
print(result)
```

### Common mistake

A learner sees dots and assumes the dot itself is the important thing.

The dot is not the important thing. **The returned object is.**

### Production habit

When a chain breaks unexpectedly, reduce it to two steps:

```python
step = df.first_operation(...)
print(type(step))
print(step.head())
```

Then add the next method.

# 4. Basic Chaining

A readable multiline chain usually uses surrounding parentheses and one method per line.

```python
result = (
    df
    .rename(columns={"qty": "quantity"})
    .query("quantity > 0")
    .sort_values("quantity", ascending=False)
)
```

This formatting gives each transformation a visual line.

### Why parentheses?

The outer parentheses allow a Python expression to continue across lines without backslash characters.

### Why one method per line?

A reviewer can scan the sequence quickly:

```text
rename
query
sort_values
```

The same chain on one line is harder to inspect:

```python
result = df.rename(columns={"qty": "quantity"}).query("quantity > 0").sort_values("quantity", ascending=False)
```

The one-line version is valid Python, but readability falls as the chain grows.

# 5. Chaining with Existing pandas Operations

This topic should build on operations you already learned.

A useful transformation might:

1. standardize column names;
2. enforce known types;
3. filter invalid records;
4. create derived values;
5. sort the final result.

```python
orders = pd.DataFrame(
    {
        "order_id": ["A101", "A102", "A103", "A104"],
        "qty": [2, 0, 3, 1],
        "unit_price": [100.0, 250.0, 75.0, 50.0],
        "status": ["paid", "cancelled", "paid", "paid"],
    }
)

result = (
    orders
    .rename(columns={"qty": "quantity"})
    .astype({"quantity": "int64"})
    .query("quantity > 0")
    .assign(revenue=lambda d: d["quantity"] * d["unit_price"])
    .query("status == 'paid'")
    .sort_values("revenue", ascending=False)
)

print(result)
```

Expected logical result:

- the row with quantity zero is removed;
- only paid orders remain;
- `revenue` is calculated before the final sort;
- the output is ordered by revenue descending.

This is a good example of the chain communicating the transformation order.

# 6. `assign()`

`DataFrame.assign()` adds new columns or replaces existing columns and returns a new DataFrame.

The basic pattern is:

```python
result = df.assign(
    revenue=df["quantity"] * df["unit_price"],
)
```

The returned DataFrame contains the original columns plus `revenue`.

Current pandas documentation describes `assign()` as returning a new object. Callable values are evaluated against the DataFrame, and multiple assignment expressions are evaluated in order; later expressions may refer to columns created earlier in the same `assign()`. 

### Why `assign()` is valuable in a chain

Direct assignment is state mutation:

```python
df["revenue"] = df["quantity"] * df["unit_price"]
```

`assign()` turns that column creation into a chainable transformation:

```python
result = (
    df
    .assign(revenue=lambda d: d["quantity"] * d["unit_price"])
)
```

The important idea is not that direct assignment is forbidden. The idea is that `assign()` fits naturally into a transformation pipeline.

# 7. `assign()` with Ordinary Values

You can assign scalars, Series, arrays, or other valid column values.

```python
result = df.assign(
    country_code="IN",
)
```

Every row receives `"IN"`.

You can also use an existing Series when you deliberately want that Series to align with the DataFrame's index:

```python
result = df.assign(
    gross_amount=df["quantity"] * df["unit_price"],
)
```

This can be fine when the expression clearly references the input DataFrame.

Inside a longer chain, however, lambda form is often clearer because the expression explicitly says:

> compute this from the DataFrame that exists at this point in the chain.

# 8. `assign()` with Lambdas

The lambda receives the DataFrame being assigned to.

A common convention is to call that DataFrame `d`:

```python
result = (
    df
    .assign(
        revenue=lambda d: d["quantity"] * d["unit_price"],
    )
)
```

Mental model:

```text
current DataFrame
       ↓
lambda d
       ↓
derived Series
       ↓
new column
```

The lambda does not receive one row at a time. It receives the DataFrame for that `assign()` operation.

### Why lambdas help

They keep the calculation close to the point where the column is created and avoid reaching back to an outer variable that may no longer represent the current pipeline state.

# 9. `assign()` Can Reference an Earlier Column in the Same Call

This is one of the most important details in the roadmap.

The assignment expressions are processed in order. A later callable can refer to a column created earlier in the same `assign()`.

```python
result = df.assign(
    revenue=lambda d: d["quantity"] * d["unit_price"],
    revenue_usd=lambda d: d["revenue"] / d["fx_rate"],
)
```

Suppose:

- `quantity = 2`
- `unit_price = 100`
- `fx_rate = 80`

Then `revenue = 200` and `revenue_usd = 2.5`.

The second expression can see `revenue` because the first expression created it before the second expression was evaluated. This ordering behavior is explicitly documented by pandas. 

### Prediction exercise

Before running the next example, predict the columns:

```python
df = pd.DataFrame(
    {
        "quantity": [2, 3],
        "unit_price": [10.0, 20.0],
    }
)

result = df.assign(
    revenue=lambda d: d["quantity"] * d["unit_price"],
    double_revenue=lambda d: d["revenue"] * 2,
)

print(result)
```

Expected columns:

```text
quantity
unit_price
revenue
double_revenue
```

### Reversing the dependency

This order is invalid because `revenue` has not yet been created:

```python
# KeyError because revenue does not exist at this point.
# result = df.assign(
#     double_revenue=lambda d: d["revenue"] * 2,
#     revenue=lambda d: d["quantity"] * d["unit_price"],
# )
```

The code is syntactically valid but semantically wrong. That distinction matters in data engineering: syntax validation cannot prove a transformation contract is correct.

# 10. `assign()` Ordering as a Dependency Graph

You can think of a multi-column `assign()` as a tiny dependency graph:

```text
quantity ──┐
           ├──> revenue ──> revenue_usd
price ─────┘
```

The sequence must respect the dependency direction.

```python
result = (
    df
    .assign(
        revenue=lambda d: d["quantity"] * d["unit_price"],
        tax=lambda d: d["revenue"] * d["tax_rate"],
        total=lambda d: d["revenue"] + d["tax"],
    )
)
```

This is readable because the columns are introduced in dependency order.

### Production rule

Keep each lambda small. If the dependency graph becomes difficult to understand, move the business rule into a named transformation function.

# 11. `assign()` Common Mistakes

## Mistake 1 — Reference before creation

The second expression cannot reference a column that has not yet been assigned.

## Mistake 2 — Typo in a column name

A lambda such as `d["unit_prcie"]` fails only when the pipeline reaches that expression.

## Mistake 3 — Accidental outer-scope dependency

This can be unclear:

```python
unit_price = df["unit_price"]

result = (
    df
    .assign(revenue=lambda d: d["quantity"] * unit_price)
)
```

Prefer to use `d["unit_price"]` when the value belongs to the current DataFrame state.

## Mistake 4 — Giant lambda

A lambda containing ten business rules is a sign that the step should have a name.

## Mistake 5 — Hidden mutation

`assign()` callables are intended to compute values, not mutate the input DataFrame. Pandas documents that the callable should not change the input object. 

Use a named function when the transformation needs more explanation or multiple operations.

# 12. `pipe()`

`pipe()` inserts a custom function into a pandas chain.

Mental model:

```text
DataFrame
   ↓
pipe()
   ↓
custom_function(DataFrame)
   ↓
returned DataFrame
   ↓
next chain step
```

The pandas documentation describes `DataFrame.pipe()` as applying chainable functions that expect a Series or DataFrame. The main advantage is readability and composability, not automatic speed. 

```python
def add_revenue(df):
    return df.assign(
        revenue=lambda d: d["quantity"] * d["unit_price"],
    )

result = df.pipe(add_revenue)
```

Conceptually:

```python
df.pipe(add_revenue)
```

means:

```python
add_revenue(df)
```

but the pipe form makes the custom transformation visible as one stage in a larger pipeline.

# 13. Why `pipe()` Exists

Built-in pandas methods are powerful, but real Data Engineering logic includes organization-specific rules:

- "drop test orders";
- "standardize source-system columns";
- "apply the order business contract";
- "add our revenue definition";
- "validate required identifiers".

Those rules often deserve names and tests.

`pipe()` lets them participate in a chain without forcing all logic into giant lambdas.

```python
def standardise_columns(df):
    return df.rename(
        columns={
            "Order ID": "order_id",
            "Customer ID": "customer_id",
        }
    )

def drop_test_orders(df):
    return df.query("order_id.str.startswith('TEST') == False", engine="python")

def add_revenue(df):
    return df.assign(
        revenue=lambda d: d["quantity"] * d["unit_price"]
    )

result = (
    raw
    .pipe(standardise_columns)
    .pipe(drop_test_orders)
    .pipe(add_revenue)
)
```

The names communicate business intent much better than an anonymous series of expressions.

# 14. `pipe()` vs Direct Function Calls

Both are valid:

### Direct nesting

```text
add_revenue(drop_test_orders(standardise_columns(raw)))
```

### Pipeline form

```text
raw
→ standardise_columns
→ drop_test_orders
→ add_revenue
```

Code:

```python
result = (
    raw
    .pipe(standardise_columns)
    .pipe(drop_test_orders)
    .pipe(add_revenue)
)
```

As the number of functions grows, pipe form usually makes the order easier to scan. The function call itself does not become faster merely because you used `pipe()`. It becomes easier to compose.

# 15. Passing Arguments Through `pipe()`

The DataFrame is passed as the first positional argument by default. Additional positional or keyword arguments can be supplied.

```python
def filter_country(df, country):
    return df.loc[df["country"] == country].copy()

result = (
    df
    .pipe(filter_country, country="IN")
)
```

Think of it as:

```python
filter_country(df, country="IN")
```

The DataFrame is the pipeline value; the extra arguments configure the function.

# 16. `pipe()` with Multiple Arguments

A function can take additional parameters:

```python
def add_tax(df, tax_rate, column="amount"):
    return df.assign(
        tax=lambda d: d[column] * tax_rate,
        total=lambda d: d[column] * (1 + tax_rate),
    )

result = (
    df
    .pipe(
        add_tax,
        tax_rate=0.18,
        column="amount",
    )
)
```

The call is equivalent in meaning to:

```python
add_tax(df, tax_rate=0.18, column="amount")
```

### Common mistake

Mixing up the pipeline DataFrame and function parameters.

Write the function so that the DataFrame input is easy to recognize, usually as the first parameter.

# 17. Pure Transformation Functions

A useful pipeline function is a **small, predictable transformation**.

A practical definition:

> A transformation function should derive its output from its inputs without unexpectedly changing external state.

Perfect mathematical purity is not required for every production system, but hidden mutation makes pipelines much harder to reason about.

Example:

```python
def add_revenue(df):
    return df.assign(
        revenue=lambda d: d["quantity"] * d["unit_price"]
    )
```

This function has:

- a clear input;
- a clear output;
- no file write;
- no global variable mutation;
- no logging side effect;
- no network call.

That makes it easy to test.

# 18. Named Pipeline Steps

The roadmap examples are intentionally descriptive:

- `standardise_columns`
- `drop_test_orders`
- `add_revenue`

Prefer names that describe business meaning.

Compare:

```text
.pipe(step_1)
.pipe(step_2)
.pipe(step_3)
```

with:

```text
.pipe(standardise_columns)
.pipe(drop_test_orders)
.pipe(add_revenue)
```

A good function name acts like documentation.

During an incident, a log line such as:

```text
pipeline_step=drop_test_orders
rows=985421
```

is immediately more useful than:

```text
pipeline_step=step_2
```

Naming is part of operational design, not just style.

# 19. Building a Pipeline from Named Functions

Start with a small set of focused steps.

```python
def standardise_columns(df):
    return df.rename(
        columns={
            "Order ID": "order_id",
            "Qty": "quantity",
            "Price": "unit_price",
        }
    )

def cast_types(df):
    return df.astype(
        {
            "quantity": "int64",
            "unit_price": "float64",
        }
    )

def drop_test_orders(df):
    return df.loc[~df["order_id"].str.startswith("TEST")].copy()

def add_revenue(df):
    return df.assign(
        revenue=lambda d: d["quantity"] * d["unit_price"]
    )

def sort_orders(df):
    return df.sort_values("order_id")

result = (
    raw
    .pipe(standardise_columns)
    .pipe(cast_types)
    .pipe(drop_test_orders)
    .pipe(add_revenue)
    .pipe(sort_orders)
)
```

Once the pipeline reaches five to eight readable stages, the value of `pipe()` becomes especially visible: every custom step has a name and every step receives the output from the previous stage.

# 20. Method Chaining + `pipe()`

Built-in pandas operations and custom functions can coexist:

```python
silver = (
    raw
    .rename(columns={
        "Order ID": "order_id",
        "Qty": "quantity",
        "Price": "unit_price",
    })
    .astype({
        "quantity": "int64",
        "unit_price": "float64",
    })
    .query("quantity > 0")
    .pipe(standardise_columns)
    .pipe(drop_test_orders)
    .assign(
        revenue=lambda d: d["quantity"] * d["unit_price"],
    )
    .pipe(add_revenue_tax)
    .sort_values("order_id")
)
```

There is a deliberate distinction:

| Kind of step | Typical representation |
| --- | --- |
| Generic pandas transformation | `.rename(...)`, `.astype(...)`, `.query(...)` |
| Simple derived column | `.assign(...)` |
| Business-significant DataFrame transformation | `.pipe(named_function)` |
| Validation/logging stage | `.pipe(check_step, ...)` |

Avoid duplicating a calculation in both `assign()` and a custom function. Each step should have one clear purpose.

# 21. Why Small Functions Matter

A function like this is easy to understand:

```python
def drop_test_orders(df):
    return df.loc[~df["order_id"].str.startswith("TEST")].copy()
```

A giant function like `process_everything()` tends to hide multiple contracts:

```python
def process_everything(df):
    # rename columns
    # cast types
    # filter bad rows
    # join dimensions
    # calculate revenue
    # validate
    # write files
    # send notifications
    return df
```

The giant function is difficult to:

- unit-test narrowly;
- reuse safely;
- debug by stage;
- review;
- reason about failure.

Keep the pipeline functions focused and compose them.

# 22. Function Contracts

Every transformation should have an implicit or explicit contract.

Example: `standardise_columns`

**Input**

A DataFrame containing source-system column names.

**Output**

A DataFrame using the pipeline's canonical column names.

**Invariant**

The transformation does not intentionally change the number of rows.

Example: `drop_test_orders`

**Input**

A standardized orders DataFrame.

**Output**

A DataFrame with test orders removed.

**Invariant**

No remaining order ID satisfies the test-order rule.

This contract-oriented thinking is useful because it tells you what to test.

# 23. One Method per Line

For a short chain, one line can be acceptable. For a production chain, prefer a multiline form when the line becomes difficult to scan.

```python
result = (
    df
    .rename(columns={"qty": "quantity"})
    .astype({"quantity": "int64"})
    .query("quantity > 0")
    .assign(revenue=lambda d: d["quantity"] * d["unit_price"])
    .sort_values("revenue", ascending=False)
)
```

The reader can visually compare the sequence with the business process.

Avoid compressing the same work into one long line:

```python
result = df.rename(columns={"qty": "quantity"}).astype({"quantity": "int64"}).query("quantity > 0").assign(revenue=lambda d: d["quantity"] * d["unit_price"]).sort_values("revenue", ascending=False)
```

# 24. Parentheses for Chains

Parentheses are preferred over backslash continuation for multiline pandas expressions.

Good:

```python
result = (
    df
    .rename(columns={"qty": "quantity"})
    .query("quantity > 0")
    .sort_values("quantity")
)
```

Be careful not to put a trailing semicolon, accidental comma, or other expression outside the parentheses that changes the returned object.

The practical rule is:

> Start the expression with `(` and close it after the final operation.

# 25. When a Chain Is Too Long

A chain should improve comprehension, not become a wall of operations.

Suppose you have:

```text
raw input
→ column cleanup
→ type enforcement
→ row filtering
→ dimension join
→ business rule
→ feature creation
→ deduplication
→ quality checks
→ output formatting
```

Putting all of that into one expression may technically work but can be harder to understand.

A named intermediate stage can be clearer:

```python
typed = (
    raw
    .rename(columns=column_map)
    .astype(order_schema)
)

clean = (
    typed
    .pipe(drop_invalid_orders)
    .pipe(drop_test_orders)
)

silver = (
    clean
    .pipe(add_revenue)
    .pipe(validate_orders)
)
```

The three names communicate architectural stages. That can be more valuable than maximizing the number of chained calls.

# 26. Long Chain vs Named Intermediate Results

| Situation | Prefer | Reason |
| --- | --- | --- |
| Short linear cleanup | Chain | Transformation is easy to scan |
| Reusable phase | Named variable | Phase has a meaningful boundary |
| Complex branch | Named variable | Branches are clearer |
| Debug checkpoint | Named variable or `pipe(check)` | Intermediate state becomes inspectable |
| Business-significant stage | Named function + `pipe()` | Gives the stage a contract and tests |
| Tiny one-off expression | Inline | Function wrapping adds noise |

Practical rule:

> **Use chaining to communicate flow; use names to communicate important boundaries.**

# 27. Debugging Method Chains with `log_shape`

A chain does not have to be opaque.

A helper can observe a stage and still return the DataFrame:

```python
def log_shape(df, name):
    print(f"{name}: rows={len(df)}, cols={df.shape[1]}")
    return df

result = (
    df
    .pipe(log_shape, "raw")
    .pipe(clean_orders)
    .pipe(log_shape, "after_clean")
    .pipe(add_revenue)
    .pipe(log_shape, "after_revenue")
)
```

The critical line is `return df`. Without it, the next chained method receives `None`.

For production pipelines, replace ad hoc `print()` statements with the logging system used by your application, but keep the helper's return contract.

# 28. A `check()` Helper

A check function validates an invariant and returns the DataFrame if the invariant passes:

```python
def check(df, name):
    required = {"order_id", "customer_id", "revenue"}
    missing = required.difference(df.columns)

    if missing:
        raise ValueError(
            f"{name}: missing required columns: {sorted(missing)}"
        )

    return df
```

This gives you a reusable validation boundary:

```text
transform
   ↓
check
   ↓
next transform
```

A check can validate things such as:

- required columns;
- minimum row count;
- key uniqueness;
- acceptable null rates;
- numeric domain rules.

Do not invent invariants only to make the example pass. An invariant should correspond to a real pipeline or business contract.

# 29. Logging Mid-Chain

During learning, `print()` is convenient. In production, a standard logging framework is usually preferable because logs can carry severity, timestamps, pipeline identifiers, and structured fields.

Keep the example narrow:

```python
import logging

logger = logging.getLogger(__name__)

def log_shape(df, name):
    logger.info(
        "pipeline_step=%s rows=%d columns=%d",
        name,
        len(df),
        df.shape[1],
    )
    return df
```

The helper still returns the DataFrame. Logging is an observation side effect; the transformation contract remains unchanged.

Do not turn this topic into a logging tutorial. The important lesson is:

> A diagnostic stage can participate in a chain if it observes the DataFrame and returns it unchanged.

# 30. The `check_step()` Helper

The hands-on exercise requires a helper shaped like:

```text
check_step(df, name, min_rows=..., unique=...)
```

A useful implementation is:

```python
import logging
from collections.abc import Iterable

logger = logging.getLogger(__name__)

def check_step(df, name, min_rows=None, unique=None):
    logger.info(
        "pipeline_step=%s rows=%d",
        name,
        len(df),
    )

    if min_rows is not None and len(df) < min_rows:
        raise ValueError(
            f"{name}: expected at least {min_rows} rows; got {len(df)}"
        )

    if unique is not None:
        if isinstance(unique, str):
            columns = [unique]
        else:
            columns = list(unique)

        missing = set(columns).difference(df.columns)
        if missing:
            raise ValueError(
                f"{name}: uniqueness columns missing: {sorted(missing)}"
            )

        if df.duplicated(subset=columns).any():
            raise ValueError(
                f"{name}: uniqueness invariant failed for {columns}"
            )

    return df
```

Why return `df`?

Because `pipe()` expects a function that produces the next pipeline value. A check is therefore designed as:

```text
DataFrame
  ↓
check_step
  ↓
same DataFrame
```

If the invariant fails, raise a clear error. Do not silently continue.

# 31. Pipeline Invariants

Examples of meaningful invariants:

| Invariant | Example meaning |
| --- | --- |
| Required columns exist | The stage satisfies the schema contract |
| Minimum row count | A source was not accidentally truncated |
| `order_id` unique | The stage represents one row per order |
| `amount >= 0` | Negative values are invalid under the business contract |
| `customer_id` not null | Downstream customer joins require a key |
| Status in allowed set | Only known workflow states are accepted |

An invariant must be based on a known contract. `min_rows=1000` is meaningful only if fewer than 1,000 rows actually indicates a problem in that pipeline.

```python
def check_non_negative_revenue(df):
    if (df["revenue"] < 0).any():
        raise ValueError("revenue invariant failed")
    return df
```

Small domain checks can be composed just like transformations.

# 32. Logging + Validation in a Chain

A validation step can be placed exactly where the corresponding invariant should hold.

```python
silver = (
    raw
    .pipe(check_step, "raw", min_rows=1_000)
    .pipe(standardise_columns)
    .pipe(check_step, "standardized", min_rows=1_000)
    .pipe(drop_test_orders)
    .pipe(check_step, "after_test_filter", min_rows=100)
    .pipe(add_revenue)
    .pipe(check_non_negative_revenue)
    .pipe(check_step, "revenue_added", unique="order_id")
)
```

This provides observability without destroying the pipeline structure.

When a run fails, you can ask:

> What was the last completed stage?

and:

> Which invariant failed there?

That is much more actionable than discovering a wrong final DataFrame several functions later.

# 33. Avoiding `inplace=True`

The roadmap specifically teaches avoiding `inplace=True`.

For example:

```python
df.drop(columns=["debug_flag"], inplace=True)
```

This operation mutates the DataFrame and returns `None`. Current pandas documentation makes the return contract explicit: when `inplace=True`, `drop()` returns `None`; with the default `False`, it returns a DataFrame. 

That makes the in-place form unsuitable for a chain:

```python
# This breaks because drop(..., inplace=True) returns None.
# result = (
#     df
#     .drop(columns=["debug_flag"], inplace=True)
#     .query("quantity > 0")
# )
```

Prefer the returned-object style:

```python
result = (
    df
    .drop(columns=["debug_flag"])
    .query("quantity > 0")
)
```

Or, when a named state is clearer:

```python
df = df.drop(columns=["debug_flag"])
```

The lesson is **clear data flow and composability**. In this chapter's style, `inplace=True` provides no useful compositional benefit because it does not return the DataFrame needed by the next chain step. Do not turn that into an absolute performance claim that returned-object style is always faster or uses less memory.

# 34. `inplace=True` Anti-Pattern in a Mutation-Heavy Script

Consider a script with many in-place mutations:

```python
df.drop(columns=["debug_flag"], inplace=True)
df.rename(columns={"qty": "quantity"}, inplace=True)
df["revenue"] = df["quantity"] * df["unit_price"]
df.sort_values("order_id", inplace=True)
```

The state of `df` changes repeatedly. The individual lines are legal, but the transformation history is distributed across mutations.

A composed style makes the data flow explicit:

```python
result = (
    df
    .drop(columns=["debug_flag"])
    .rename(columns={"qty": "quantity"})
    .assign(
        revenue=lambda d: d["quantity"] * d["unit_price"]
    )
    .sort_values("order_id")
)
```

Again, the point is not that in-place mutation is forbidden Python. The point is that this chapter's pipeline design benefits from return values.

# 35. `pipe()` vs `apply()`

These methods solve different problems.

| Tool | What receives the function? | Typical purpose |
| --- | --- | --- |
| `pipe()` | The whole DataFrame/Series object | DataFrame-level transformation |
| `apply()` | Elements, rows, columns, or groups depending on the call | Element/axis/group function application |

Example of `pipe()`:

```python
def add_revenue(df):
    return df.assign(
        revenue=lambda d: d["quantity"] * d["unit_price"]
    )

result = df.pipe(add_revenue)
```

The whole DataFrame arrives in `add_revenue`.

An `apply()` example is conceptually different:

```python
result = df["amount"].apply(lambda value: value * 1.18)
```

Here the function receives individual Series values.

Pandas documentation explicitly describes `pipe()` as receiving the whole Series or DataFrame, and contrasts it with operations that work element-by-element. 

Do not replace every `apply()` with `pipe()`. Choose based on the level of the transformation.

# 36. `pipe()` vs `assign()`

Use this mental model:

| Tool | Primary purpose | Example |
| --- | --- | --- |
| `assign()` | Create or replace columns | `assign(revenue=...)` |
| `pipe()` | Insert a custom DataFrame-level function | `pipe(add_revenue)` |

`assign()` is ideal when the transformation is naturally expressed as one or more column definitions:

```python
result = (
    df
    .assign(
        revenue=lambda d: d["quantity"] * d["unit_price"],
        is_large=lambda d: d["revenue"] >= 1000,
    )
)
```

`pipe()` is ideal when the operation deserves a named function:

```python
result = (
    df
    .pipe(apply_order_business_rules)
)
```

A useful boundary is:

> If the logic is mainly "define these columns", consider `assign()`. If it is a meaningful DataFrame-level transformation with its own contract, consider `pipe()`.")

# 37. Team-Wide Custom DataFrame Accessors

Pandas can be extended with custom DataFrame accessors.

The API is:

```python
pd.api.extensions.register_dataframe_accessor
```

This can create a readable team-specific namespace such as:

```text
df.dq.null_report()
df.dq.duplicate_report("order_id")
```

The goal is not to make pandas "magically know" your business rules. The goal is to package a small, reusable internal API for behavior that a team repeatedly uses.

Current pandas exposes custom extension APIs under `pandas.api.extensions`. 

# 38. When Custom Accessors May Help

A custom accessor can be reasonable when the behavior is:

- repeated across many pipelines;
- domain-specific;
- easy to name;
- focused;
- documented;
- covered by tests.

Examples:

```text
df.dq.null_report()
df.dq.duplicate_report("order_id")
df.finance.validate_amounts()
df.customer.standardized_key()
```

Use a custom accessor only when the namespace makes the team's code clearer.

A normal function is often enough for a transformation used in one or two places.

# 39. Registering an Accessor

A minimal DataFrame accessor looks like this:

```python
import pandas as pd

@pd.api.extensions.register_dataframe_accessor("dq")
class DataQualityAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def null_report(self):
        return (
            self._obj.isna()
            .sum()
            .rename("null_count")
            .to_frame()
            .assign(
                null_rate=lambda d: d["null_count"] / len(self._obj)
            )
        )
```

Break the implementation down:

1. The decorator registers the namespace `dq`.
2. Pandas constructs the accessor with the DataFrame.
3. The accessor stores that DataFrame as `_obj`.
4. Methods operate on `_obj`.
5. Methods return useful results.

After registration:

```python
df.dq.null_report()
```

### Design caution

Registration is global within the Python process. Choose a namespace that is unlikely to collide with another installed extension.

# 40. `dq.null_report()`

A simple report can make data-quality inspection reusable:

```python
df = pd.DataFrame(
    {
        "order_id": ["A1", "A2", "A3"],
        "customer_id": ["C1", None, "C3"],
        "amount": [10.0, None, 30.0],
    }
)

print(df.dq.null_report())
```

Expected logical output:

| column | null_count | null_rate |
| --- | ---: | ---: |
| order_id | 0 | 0.0 |
| customer_id | 1 | approximately 0.3333 |
| amount | 1 | approximately 0.3333 |

The report itself is a DataFrame, which makes it easy to inspect or feed into another report-building step.

# 41. `dq.duplicate_report(key)`

Another useful team helper is duplicate detection:

```python
import pandas as pd

@pd.api.extensions.register_dataframe_accessor("dq")
class DataQualityAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def null_report(self):
        counts = self._obj.isna().sum()
        return counts.rename("null_count").to_frame()

    def duplicate_report(self, key):
        if key not in self._obj.columns:
            raise KeyError(f"Missing key column: {key}")

        duplicate_mask = self._obj.duplicated(
            subset=[key],
            keep=False,
        )

        return self._obj.loc[duplicate_mask].copy()
```

Then:

```python
df.dq.duplicate_report("order_id")
```

The function should have a clear contract: does it return all duplicate rows, only duplicate keys, counts, or a summary? Pick one and document it.

# 42. Custom Accessor Design Risks

Custom accessors are powerful enough to be overused.

### Risk 1 — Hiding too much logic

`df.dq.run_everything()` tells the reader almost nothing.

### Risk 2 — Surprising mutations

A method called `null_report()` should not silently reorder or modify the DataFrame.

### Risk 3 — Namespace conflicts

An accessor name such as `dq` becomes part of your team's API.

### Risk 4 — Poor discoverability

A new engineer may not know what `dq` means unless it is documented.

### Risk 5 — Difficult testing

An accessor that contains hundreds of lines becomes a second framework inside the project.

### Risk 6 — Over-abstraction

If one function is used once, a normal named function may be much clearer.

Production rule:

> Prefer a normal function until the accessor abstraction clearly improves repeated team usage.

# 43. Testing Individual Pipeline Steps

Each named transformation should be independently testable on a tiny DataFrame.

Example:

```python
def add_revenue(df):
    return df.assign(
        revenue=lambda d: d["quantity"] * d["unit_price"]
    )
```

```python
import pandas as pd
from pandas.testing import assert_frame_equal

raw = pd.DataFrame(
    {
        "quantity": [2, 3],
        "unit_price": [10.0, 20.0],
    }
)

expected = raw.assign(
    revenue=[20.0, 60.0],
)

actual = add_revenue(raw)

assert_frame_equal(actual, expected)
```

A unit test should check behavior:

- column exists;
- values are correct;
- schema is correct;
- edge cases behave as designed;
- input expectations are clear.

# 44. Testing the Whole Chain

Individual functions can pass while the integrated pipeline still fails because a function's output does not match the next function's expectation.

An integration test should therefore exercise the actual composition:

```python
def build_silver_orders(raw):
    return (
        raw
        .pipe(standardise_columns)
        .pipe(drop_test_orders)
        .pipe(add_revenue)
    )

result = build_silver_orders(raw_orders)
```

Verify:

- complete output schema;
- expected row count;
- expected values;
- key uniqueness;
- business invariants;
- expected behavior for malformed input.

Unit tests ask:

> Does this step work?

Integration tests ask:

> Do these steps work together?

# 45. Testing Pure Transformations with Tiny Frames

Keep unit-test fixtures small.

Good fixture:

```python
raw = pd.DataFrame(
    {
        "order_id": ["A1", "TEST-1", "A2"],
        "quantity": [2, 1, 3],
        "unit_price": [10.0, 99.0, 5.0],
    }
)
```

This fixture lets a test prove that `drop_test_orders()` removes exactly one record and leaves the other values intact.

```python
def drop_test_orders(df):
    return df.loc[
        ~df["order_id"].str.startswith("TEST")
    ].copy()

clean = drop_test_orders(raw)

assert clean["order_id"].tolist() == ["A1", "A2"]
assert len(clean) == 2
```

Small deterministic inputs make failures easier to understand than a 10-million-row production sample.

# 46. Debugging by Replacing `pipe()` with Intermediate Variables

A chain can be temporarily expanded during an incident.

Starting point:

```python
result = (
    df
    .pipe(step_a)
    .pipe(step_b)
    .pipe(step_c)
)
```

Temporary debugging form:

```python
step1 = step_a(df)
print(step1.head())

step2 = step_b(step1)
print(step2.head())

step3 = step_c(step2)
print(step3.head())
```

This exposes each intermediate state. Once the defect is found, you can restore the chain or insert a permanent check step.

This is a debugging technique, not a rule that named intermediates are bad.

# 47. Debugging with `check` / `log` Steps

A production-oriented alternative is to make important boundaries visible inside the chain:

```python
result = (
    df
    .pipe(check_step, "input", min_rows=1)
    .pipe(step_a)
    .pipe(check_step, "after_a", min_rows=1)
    .pipe(step_b)
    .pipe(check_step, "after_b", min_rows=1)
)
```

A check function can fail close to the stage that introduced a bad state.

That reduces the search area during debugging.

# 48. Production Pipeline Architecture

A common Data Engineering shape is:

```text
Raw / Bronze
     ↓
standardise
     ↓
type / clean
     ↓
remove invalid records
     ↓
business transformations
     ↓
validate
     ↓
Silver
```

The important idea is not the word "Silver" itself. The important idea is that a DataFrame pipeline can mirror a documented data-contract flow.

```python
def build_silver_orders(raw):
    return (
        raw
        .pipe(check_step, "raw")
        .pipe(standardise_columns)
        .pipe(cast_order_types)
        .pipe(clean_order_values)
        .pipe(drop_test_orders)
        .pipe(add_revenue)
        .pipe(validate_order_keys)
        .pipe(check_step, "silver_ready", unique="order_id")
    )
```

The pipeline is now readable at the architecture level. An engineer can inspect the function and understand the intended stage sequence before opening each transformation's implementation.

# 49. Hands-On Exercise — `silver_pipeline.py`

**Do not create `silver_pipeline.py` as part of this Markdown chapter.** This section is the complete exercise specification.

The roadmap requires you to take the messiest transformation work from earlier topics and rewrite it as a chain of `pipe()` steps.

## Task 1 — Build `build_silver_orders()`

Implement:

```text
build_silver_orders(raw: pd.DataFrame) -> pd.DataFrame
```

The function must contain **at least eight `pipe()` steps**.

The exact reusable functions should come from your exercise environment or be defined in the exercise file. This chapter does not modify earlier topic files.

A strong conceptual chain is:

```python
def build_silver_orders(raw: pd.DataFrame) -> pd.DataFrame:
    return (
        raw
        .pipe(check_step, "raw")
        .pipe(standardise_columns)
        .pipe(cast_order_types)
        .pipe(clean_order_values)
        .pipe(drop_test_orders)
        .pipe(add_revenue)
        .pipe(add_customer_features)
        .pipe(validate_order_keys)
        .pipe(check_step, "silver_ready", unique="order_id")
    )
```

Your eight-plus `pipe()` stages should have meaningful names. Do not create eight empty wrappers just to satisfy a number; each stage must represent real work or validation.

### Suggested stage contracts

| Step | Purpose | Example invariant |
| --- | --- | --- |
| `check_step("raw")` | Observe source state | Minimum source rows |
| `standardise_columns` | Canonical names | Required names exist |
| `cast_order_types` | Expected dtypes | Numeric fields typed |
| `clean_order_values` | Known cleaning rules | No impossible values |
| `drop_test_orders` | Remove test records | Test IDs absent |
| `add_revenue` | Derive revenue | Revenue calculation defined |
| `add_customer_features` | Add domain columns | Expected feature columns exist |
| `validate_order_keys` | Validate key quality | `order_id` unique |
| final `check_step` | Verify Silver contract | Final schema/invariants pass |

## Task 2 — Implement `check_step()`

Use:

```python
check_step(
    df,
    name,
    min_rows=...,
    unique=...,
)
```

It must:

- log the step name;
- log row count;
- validate `min_rows`;
- validate uniqueness when requested;
- raise a clear error on invariant violation;
- return `df`.

A reference implementation:

```python
def check_step(df, name, min_rows=None, unique=None):
    logger.info("step=%s rows=%d", name, len(df))

    if min_rows is not None and len(df) < min_rows:
        raise ValueError(
            f"{name}: minimum-row invariant failed"
        )

    if unique is not None:
        columns = [unique] if isinstance(unique, str) else list(unique)
        if df.duplicated(subset=columns).any():
            raise ValueError(
                f"{name}: uniqueness invariant failed: {columns}"
            )

    return df
```

## Task 3 — Insert checks throughout the chain

At important boundaries, use:

```text
raw
 → check
 → clean
 → check
 → standardize
 → check
 → enrich
 → check
 → final validation
```

Choose meaningful step names rather than generic `step1`, `step2`, and `step3`.

## Task 4 — Unit-test every transformation

Each named function should have small tests for:

- happy path;
- empty input;
- malformed input where relevant;
- boundary values;
- schema behavior;
- row-count behavior;
- invariants.

## Task 5 — Integration-test the complete pipeline

Run:

```python
build_silver_orders(raw)
```

against a small realistic DataFrame.

Verify:

- output schema;
- expected row count;
- expected values;
- key uniqueness;
- invariant behavior.

## Task 6 — Register and test the `dq` accessor

Register the `dq` accessor and provide:

```python
df.dq.null_report()
df.dq.duplicate_report("order_id")
```

Test both methods.

# 50. Complete Mutation-Heavy → Chain Refactor Exercise

Use a deliberately mutation-heavy script first:

```python
df = raw.copy()

df = df.rename(columns={"qty": "quantity"})
df["status"] = df["status"].str.strip().str.lower()
df = df.drop(columns=["debug_flag"])
df["revenue"] = df["quantity"] * df["unit_price"]
df = df.sort_values("order_id")
```

Refactor it:

```python
result = (
    raw
    .rename(columns={"qty": "quantity"})
    .assign(
        status=lambda d: d["status"].str.strip().str.lower(),
    )
    .drop(columns=["debug_flag"])
    .assign(
        revenue=lambda d: d["quantity"] * d["unit_price"],
    )
    .sort_values("order_id")
)
```

Compare the two versions for:

- readability;
- testability;
- debugging;
- reuse;
- code review.

Do not judge the refactor only by character count. The goal is to communicate the transformation contract.

# 51. Prediction-First Learning

Before executing important examples, predict what will happen.

Ask:

1. What object does this pandas method return?
2. Can the next method accept that object?
3. Which columns exist after `assign()`?
4. Can a later `assign()` lambda see an earlier column?
5. What DataFrame reaches `pipe()`?
6. What happens if a pipe function returns `None`?
7. What happens if a check helper does not return `df`?
8. How many rows should remain after each filter?
9. Which invariant should hold after each stage?
10. Where should a failure first become visible?

Use:

```text
Predict
   ↓
Execute
   ↓
Inspect
   ↓
Assert
   ↓
Explain
```

This loop is especially valuable when learning pipelines because it trains you to reason about **state transitions** rather than memorizing syntax.

# 52. Prediction Exercise Set

Predict first, then execute and verify.

### Exercise 1

Will this continue as a DataFrame chain?

```python
result = df.rename(columns={"qty": "quantity"}).query("quantity > 0")
```

### Exercise 2

What is the type of `df.shape`? Can `.query()` follow it?

### Exercise 3

What columns exist after this `assign()`?

```python
result = df.assign(
    revenue=lambda d: d["quantity"] * d["unit_price"],
    double_revenue=lambda d: d["revenue"] * 2,
)
```

### Exercise 4

Which `assign()` dependency order is valid?

### Exercise 5

What DataFrame reaches `filter_country`?

```python
result = df.pipe(filter_country, country="IN")
```

### Exercise 6

What happens if `filter_country()` returns `None`?

### Exercise 7

How many rows remain after a filter that excludes all records?

### Exercise 8

Which invariant should fail if a supposedly unique key becomes duplicated?

### Exercise 9

At which stage should a missing-column error be detected?

### Exercise 10

What is the output of a `log_shape()` function that returns `df`?

### Exercise 11

What happens to a chain after a `check_step()` that raises?

### Exercise 12

What should `dq.null_report()` return?

### Exercise 13

What records should `dq.duplicate_report("order_id")` expose?

### Exercise 14

Why can all unit tests pass while an integration pipeline still fail?

### Exercise 15

Which additional intermediate objects might increase peak memory in a long transformation chain?

For every question use:

```text
Predict → Execute → Inspect → Assert → Explain
```

# 53. Debugging Section

The goal of debugging is not just to make the error disappear. It is to identify **which pipeline contract was broken and at what stage**.

For each case below:

- **Buggy code**
- **Expected behavior**
- **Actual behavior**
- **Root cause**
- **Corrected code**
- **Prevention rule**

should be documented and practiced.

## 1. Chaining a scalar result


**Buggy or diagnostic example**

```python
# buggy
# result = df["amount"].sum().query("amount > 0")

# corrected
result = (
    df
    .query("amount > 0")
    .assign(total_amount=lambda d: d["amount"].sum())
)
```

**Expected behavior**

Expected a DataFrame chain, but `sum()` returns a scalar.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Move scalar aggregation to a terminal operation or store it separately.

## 2. Chaining a Series when a DataFrame is required


**Buggy or diagnostic example**

```python
series = df["amount"]
# series.query(...) is not a DataFrame query on the original frame

result = df.query("amount > 0")
```

**Expected behavior**

The next operation must match the object type.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

A column selection changes the pipeline value from DataFrame to Series.

## 3. Missing parentheses around a multiline chain


**Buggy or diagnostic example**

```python
result = (
    df
    .rename(columns={"qty": "quantity"})
    .query("quantity > 0")
)
```

**Expected behavior**

The expression must be syntactically enclosed when split across lines.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Use surrounding parentheses for the chain.

## 4. Overly long unreadable chain


**Buggy or diagnostic example**

```python
result = (
    df
    .rename(...)
    .astype(...)
    .query(...)
    .merge(...)
    .assign(...)
    .drop_duplicates(...)
    .sort_values(...)
)
```

**Expected behavior**

Shorten or split at meaningful boundaries.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

The issue is readability, not pandas correctness.

## 5. `assign()` references a column before it exists


**Buggy or diagnostic example**

```python
# wrong ordering
# df.assign(double=lambda d: d["revenue"] * 2,
#           revenue=lambda d: d["quantity"] * d["unit_price"])

# corrected
df.assign(
    revenue=lambda d: d["quantity"] * d["unit_price"],
    double=lambda d: d["revenue"] * 2,
)
```

**Expected behavior**

Later assignment sees earlier assignments, not future ones.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Respect dependency order.

## 6. Incorrect lambda parameter


**Buggy or diagnostic example**

```python
# wrong
# df.assign(revenue=lambda x: df["quantity"] * df["unit_price"])

# preferred
df.assign(
    revenue=lambda d: d["quantity"] * d["unit_price"]
)
```

**Expected behavior**

The lambda should clearly use the current DataFrame.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Use the callable parameter consistently.

## 7. Overly complex lambda


**Buggy or diagnostic example**

```python
# replace this with a named function
def calculate_revenue(df):
    return df.assign(
        revenue=lambda d: (
            d["quantity"] * d["unit_price"] * (1 - d["discount_rate"])
        )
    )
```

**Expected behavior**

Business logic deserves a named function when it is hard to scan.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

The lambda became a hidden mini-program.

## 8. `pipe()` function returns `None`


**Buggy or diagnostic example**

```python
def bad_step(df):
    print(df.shape)
    # missing return

# corrected
def good_step(df):
    print(df.shape)
    return df
```

**Expected behavior**

The next chain step receives `None`.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Every pass-through observation step must return the DataFrame.

## 9. Incorrect `pipe()` arguments


**Buggy or diagnostic example**

```python
def filter_country(df, country):
    return df.loc[df["country"] == country]

result = df.pipe(filter_country, country="IN")
```

**Expected behavior**

Arguments must match the function signature.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Treat `pipe()` as a readable function call.

## 10. Hidden external side effect


**Buggy or diagnostic example**

```python
notifications_sent = []

def transform(df):
    notifications_sent.append("started")
    return df.assign(flag=True)
```

**Expected behavior**

A transformation unexpectedly changes external state.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Keep transformations focused; perform orchestration side effects outside them.

## 11. Function mutates global/external state


**Buggy or diagnostic example**

```python
config = {"run_count": 0}

def step(df):
    config["run_count"] += 1
    return df
```

**Expected behavior**

Repeated pipeline runs can have state-dependent behavior.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Make external state explicit or isolate side effects.

## 12. A step silently changes row count


**Buggy or diagnostic example**

```python
def accidental_filter(df):
    return df.query("amount > 0")
```

**Expected behavior**

Row count changes only when the contract expects it.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Check row-count behavior at that stage.

## 13. `check_step()` does not return `df`


**Buggy or diagnostic example**

```python
def bad_check(df, name):
    if len(df) == 0:
        raise ValueError("empty")
    # missing return
```

**Expected behavior**

Pipeline should continue with the same DataFrame.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Return `df` after successful validation.

## 14. Logging step returns `None`


**Buggy or diagnostic example**

```python
def bad_log(df, name):
    logger.info("%s %s", name, df.shape)
    return df
```

**Expected behavior**

A logging helper must return the input object.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Treat diagnostic helpers as pass-through pipeline stages.

## 15. Incorrect invariant


**Buggy or diagnostic example**

```python
def check_unique_customer(df):
    if df["customer_id"].is_unique:
        return df
    raise ValueError("customer_id must be unique")
```

**Expected behavior**

Only assert uniqueness when one row per customer is truly the contract.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

The invariant was copied from a different grain.

## 16. `inplace=True` breaks the chain


**Buggy or diagnostic example**

```python
# wrong
# result = df.drop(columns=["x"], inplace=True).query("amount > 0")

# corrected
result = (
    df
    .drop(columns=["x"])
    .query("amount > 0")
)
```

**Expected behavior**

`drop(..., inplace=True)` returns `None`.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Use returned-object transformations in the chain.

## 17. Too many steps hide the failure


**Buggy or diagnostic example**

```python
# many anonymous operations in one chain
# ...
```

**Expected behavior**

Failure location is difficult to identify.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Break at logical phases or insert check/log steps.

## 18. Custom accessor namespace conflict


**Buggy or diagnostic example**

```python
# avoid choosing an accessor name already used in the environment
@pd.api.extensions.register_dataframe_accessor("dq")
class DataQualityAccessor:
    ...
```

**Expected behavior**

The namespace should be unique in the Python process.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Choose and document a project-owned namespace.

## 19. Custom accessor hides mutations


**Buggy or diagnostic example**

```python
def mutate_report(self):
    self._obj["debug"] = True
    return self._obj
```

**Expected behavior**

A method named like a report should not silently mutate production data.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Return a report or make mutation explicit and named.

## 20. Accessor returns wrong type


**Buggy or diagnostic example**

```python
def null_report(self):
    return self._obj.isna().sum()
```

**Expected behavior**

A caller expecting a report DataFrame may receive a Series.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Document and test the accessor's return type.

## 21. Unit step passes, integration fails


**Buggy or diagnostic example**

```python
# each function works on its own,
# but one returns an unexpected column name
```

**Expected behavior**

The contract between steps is inconsistent.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Add integration tests and explicit function contracts.

## 22. Step changes expected schema


**Buggy or diagnostic example**

```python
def step(df):
    return df.drop(columns=["customer_id"])
```

**Expected behavior**

Downstream code no longer receives a required column.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Validate schema at the boundary where the column is required.

## 23. Unit test validates implementation instead of behavior


**Buggy or diagnostic example**

```python
# weak test:
# assert function.__name__ == "add_revenue"

# stronger:
# assert output["revenue"].tolist() == [20.0, 60.0]
```

**Expected behavior**

The test can pass even when the transformation is wrong.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Assert business behavior and output contracts.

## 24. Tiny data passes, production-sized data fails


**Buggy or diagnostic example**

```python
# representative logic may be correct for tiny input
# but performance/memory can fail at scale
```

**Expected behavior**

Workload shape was not included in validation.

**Actual behavior**

The failure or surprising result follows from the stated bug.

**Root cause**

The pipeline contract and the returned object/state no longer match.

**Prevention rule**

Benchmark representative data sizes and monitor memory when scale matters.

# 54. Testing Strategy

Testing should operate at several levels.

## 54.1 Unit tests

Each named transformation is tested independently.

For example:

```python
def test_add_revenue():
    raw = pd.DataFrame(
        {
            "quantity": [2, 3],
            "unit_price": [10.0, 20.0],
        }
    )

    result = add_revenue(raw)

    assert result["revenue"].tolist() == [20.0, 60.0]
```

Test:

- happy path;
- empty input;
- invalid input;
- boundary values;
- schema;
- row-count behavior;
- invariants.

## 54.2 `assign()` tests

Check that:

- newly created columns exist;
- dependency ordering is respected;
- calculated values are correct.

```python
def test_assign_dependency_order():
    df = pd.DataFrame({"quantity": [2], "unit_price": [10.0]})

    result = df.assign(
        revenue=lambda d: d["quantity"] * d["unit_price"],
        double_revenue=lambda d: d["revenue"] * 2,
    )

    assert result["revenue"].tolist() == [20.0]
    assert result["double_revenue"].tolist() == [40.0]
```

## 54.3 `pipe()` tests

Check that:

- the function receives a DataFrame;
- it returns a DataFrame when required;
- arguments are passed correctly.

```python
def add_tax(df, tax_rate):
    return df.assign(
        tax=lambda d: d["amount"] * tax_rate
    )

def test_pipe_arguments():
    df = pd.DataFrame({"amount": [100.0]})
    result = df.pipe(add_tax, tax_rate=0.18)
    assert result["tax"].tolist() == [18.0]
```

## 54.4 `check_step()` tests

Test:

- valid data passes;
- minimum-row violation raises;
- uniqueness violation raises;
- error messages identify the stage;
- the DataFrame is returned on success.

```python
import pytest

def test_check_step_min_rows():
    df = pd.DataFrame({"id": [1]})

    with pytest.raises(ValueError, match="minimum-row"):
        check_step(df, "small_stage", min_rows=2)
```

## 54.5 Full pipeline integration tests

Verify:

- final schema;
- expected row count;
- business invariants;
- required non-null values;
- expected derived columns;
- important values.

```python
def test_build_silver_orders(raw_orders):
    result = build_silver_orders(raw_orders)

    assert "revenue" in result.columns
    assert result["order_id"].is_unique
    assert (result["revenue"] >= 0).all()
```

## 54.6 Custom accessor tests

Test:

```python
df.dq.null_report()
df.dq.duplicate_report("order_id")
```

Use `pandas.testing` helpers where exact DataFrame equality matters.

```python
from pandas.testing import assert_frame_equal

def test_null_report():
    df = pd.DataFrame(
        {
            "a": [1, None],
            "b": [1, 2],
        }
    )

    expected = pd.DataFrame(
        {
            "null_count": [1, 0],
        },
        index=["a", "b"],
    )

    actual = df.dq.null_report()[["null_count"]]

    assert_frame_equal(actual, expected)
```

# 55. Edge Cases

A production pipeline should explicitly decide what happens for the following cases.

| Edge case | Robust handling |
| --- | --- |
| Empty input DataFrame | Define whether empty is valid; check before destructive stages |
| One-row DataFrame | Ensure scalar assumptions do not replace DataFrame logic |
| Zero-row intermediate result | Let the pipeline fail or continue intentionally based on contract |
| Function returns Series unexpectedly | Validate return type at the boundary |
| Function returns `None` | Raise immediately rather than allowing a later obscure failure |
| Missing required columns | Fail with the stage and missing names |
| All rows removed by a filter | Check whether this is a legitimate outcome |
| Very long chain | Break at a meaningful phase |
| Duplicate keys | Use an explicit uniqueness invariant where required |
| Null-heavy DataFrame | Test null behavior before production |
| `assign()` dependency ordering | Define columns in dependency order |
| Required function parameter missing | Give the function an explicit signature |
| Keyword collision | Use descriptive, non-conflicting parameter names |
| Logging/check step raises unexpectedly | Treat it as a pipeline contract failure and include stage context |
| Accessor registered twice | Keep accessor registration in one importable module |
| Invalid DataFrame state entering accessor | Validate assumptions and raise useful errors |
| Unit test passes but integration test fails | Add contract and integration coverage |

The robust response is not always "fail." It is:

> Define the expected behavior, make it observable, and test it.

# 56. Performance Engineering

Method chaining itself is **not** a magic optimization.

A chain can still:

- perform multiple full DataFrame passes;
- allocate intermediate objects;
- create temporary columns;
- execute expensive joins or sorts;
- add logging/check overhead;
- increase peak memory.

`pipe()` improves composition and readability; it does not automatically reduce runtime. Pandas documents this directly: `DataFrame.pipe()` promotes clean, modular design but does not improve performance on its own. 

### What to measure

Use representative inputs and compare equivalent logic.

```python
from time import perf_counter

start = perf_counter()
result = build_silver_orders(raw)
elapsed = perf_counter() - start

print(f"elapsed_seconds={elapsed:.4f}")
```

For performance experiments:

- use the same input data;
- measure equivalent transformations;
- repeat measurements when practical;
- warm up relevant code when appropriate;
- record pandas/Python/environment versions;
- compare output equality;
- inspect memory when peak usage matters.

Do not claim a chain is faster just because it has fewer lines.

# 57. Memory Considerations

Readable chaining and memory behavior are separate dimensions.

A pipeline can be readable while still producing large intermediates.

Watch for:

- temporary derived columns;
- repeated filtering of large frames;
- large merge outputs;
- unnecessary wide DataFrames;
- retained intermediate variables;
- debugging copies.

For example, this creates a temporary intermediate column:

```python
result = (
    df
    .assign(
        normalized_amount=lambda d: d["amount"] / d["fx_rate"]
    )
    .query("normalized_amount > 100")
)
```

The example may be perfectly reasonable. The production question is whether the additional column and other transformations fit the workload's memory budget.

This topic only introduces the concern. Detailed chunked processing and memory reduction belong later in the roadmap.

# 58. Method-Chaining Production Style Guide

## Prefer

```python
result = (
    df
    .rename(columns=column_map)
    .assign(
        revenue=lambda d: d["quantity"] * d["unit_price"],
    )
    .query("revenue > 0")
    .pipe(validate_orders)
    .sort_values("order_id")
)
```

## Avoid

- giant one-line chains;
- hidden side effects;
- unexplained lambdas;
- arbitrary `inplace=True`;
- silent quality checks;
- functions that return inconsistent types;
- chains that cannot be understood in code review.

### Formatting rule

One meaningful transformation per line is a strong default.

### Naming rule

Use function names that explain domain meaning.

### Boundary rule

Break a chain when a distinct phase deserves a name.

### Validation rule

Put important invariants near the stage where they become true.

# 59. Code Review Checklist

Before approving a pipeline, ask:

- [ ] Does the chain clearly communicate the transformation?
- [ ] Does each method return an appropriate object for the next step?
- [ ] Are complex business rules extracted into named functions?
- [ ] Are `pipe()` functions small and testable?
- [ ] Are lambdas short and readable?
- [ ] Are important invariants checked?
- [ ] Do logging/check helpers return the DataFrame?
- [ ] Is `inplace=True` avoided in the chain?
- [ ] Is the chain short enough to understand?
- [ ] Are intermediate variables used where they improve clarity?
- [ ] Are individual steps unit-tested?
- [ ] Is the complete pipeline integration-tested?
- [ ] Is a custom accessor genuinely useful?
- [ ] Does the pipeline contract document expected input/output behavior?
- [ ] Are production-scale performance and memory concerns considered where relevant?

# 60. Pipeline Contract Template

Use this template when designing a production DataFrame pipeline:

```text
Pipeline name:
Input:
Output:

Step 1:
Invariant:

Step 2:
Invariant:

Step 3:
Invariant:

Final schema:
Expected row-count behavior:
Failure behavior:
Logging:
Tests:
Performance considerations:
Memory considerations:
```

A contract turns a chain from "a sequence of code" into "a sequence of defined transformations.

# 61. Advanced Design Principles

### Principle 1 — One transformation step should have one clear purpose

This improves testing and diagnosis.

### Principle 2 — Prefer named functions for meaningful business logic

Names make contracts visible.

### Principle 3 — Use `pipe()` to compose those functions

The pipeline becomes an architectural sequence.

### Principle 4 — Keep `assign()` expressions simple

Use lambdas for local column calculations, not giant business programs.

### Principle 5 — Make intermediate invariants observable

Validation close to a transformation reduces debugging distance.

### Principle 6 — Use custom accessors only when repeated team-wide behavior justifies the abstraction

A namespace should clarify code, not impress readers.

### Principle 7 — Use chains to communicate data flow, not to compress code

A chain exists for comprehension, not line-count competition.

# 62. Common Mistakes Summary

| Mistake | Why it happens | Correct approach |
| --- | --- | --- |
| Chaining a method that returns a scalar | Treating every method as a DataFrame transformation | Know the return type before chaining |
| Chaining a Series when a DataFrame is expected | Column selection changed the pipeline object | Keep DataFrame-level steps on the DataFrame |
| Overly long chains | Trying to keep everything in one expression | Break at meaningful stages |
| Overly complex lambdas | Avoiding named functions | Extract business logic into small functions |
| `pipe()` function returns `None` | Logging/check function forgotten to return | Always return `df` when the next step needs it |
| `check_step()` fails to return `df` | Confusing validation with terminal processing | Return the unchanged DataFrame after success |
| Hidden side effects | Mixing orchestration with transformation | Keep transformation functions focused |
| Excessive custom accessors | Over-engineering reusable helpers | Start with normal functions |
| `inplace=True` in a chain | Expecting it to return a DataFrame | Use returned-object transformations |
| Missing invariant checks | Assuming the final result will reveal the problem | Validate at important boundaries |
| Insufficient tests | Testing only the happy path | Unit-test steps and integration-test composition |
| `assign()` dependency written backward | Forgetting evaluation order | Define dependent columns after their inputs |
| Anonymous pipeline step names | Optimizing for typing speed | Name business transformations |
| Treating chain length as a quality metric | Confusing compactness with readability | Optimize for understanding |

# 63. Checkpoint

You should now be able to complete these roadmap requirements:

1. **Rewrite a mutation-heavy script as a method chain.**
2. **Use `assign()` with a lambda that references a column created earlier.**
3. **Log and assert invariants in the middle of a chain.**
4. **Explain why `inplace=True` is discouraged.**

Then verify your advanced understanding:

- What does `pipe()` add that direct function calls do not?
- Why is `pipe()` a DataFrame-level composition tool?
- How do you design a small pure-ish transformation?
- Why do meaningful function names matter during incidents?
- How do you decide when to break a chain?
- Why must `check_step()` return `df`?
- When is a custom accessor justified?
- What are the risks of a custom accessor?
- What is the difference between a unit test and a whole-pipeline integration test?
- Why is method chaining not a performance guarantee?
- How can intermediate transformations affect peak memory?

### Exit test

Without looking at the chapter, build a five-to-eight-step pipeline from raw orders and explain:

1. the purpose of every step;
2. the input and output contract;
3. the invariant at two boundaries;
4. one unit test;
5. one integration test.

# 64. Cheat Sheet

## Method chaining

```python
result = (
    df
    .rename(...)
    .astype(...)
    .query(...)
    .assign(...)
    .sort_values(...)
)
```

## `assign()`

```python
df.assign(
    revenue=lambda d: d["quantity"] * d["unit_price"],
)
```

## `assign()` dependency ordering

```python
df.assign(
    revenue=lambda d: d["quantity"] * d["unit_price"],
    revenue_usd=lambda d: d["revenue"] / d["fx_rate"],
)
```

## `pipe()`

```python
df.pipe(clean_orders)
```

## `pipe()` arguments

```python
df.pipe(
    add_tax,
    tax_rate=0.18,
)
```

## Logging/check step

```python
(
    df
    .pipe(check_step, "raw")
    .pipe(clean_orders)
    .pipe(check_step, "clean")
)
```

## Custom accessor

```python
df.dq.null_report()
df.dq.duplicate_report("order_id")
```

## Avoid in a chain

```python
df.drop(columns=["x"], inplace=True)
```

## Prefer

```python
df = df.drop(columns=["x"])
```

or:

```python
result = (
    df
    .drop(columns=["x"])
    .query("amount > 0")
)
```

## Mental model

```text
method chaining = compose pandas operations
assign          = create/replace columns inside the chain
pipe            = insert your DataFrame-level function
named steps     = readable/testable business transformations
check_step      = observe + validate + return DataFrame
custom accessor = reusable team-specific DataFrame API
```

# 65. Production Data Engineering Use Cases

## Silver pipeline

```text
raw
  ↓
standardise
  ↓
type
  ↓
clean
  ↓
validate
  ↓
derive
  ↓
output
```

## Customer data

Normalize source columns, validate identifiers, and package reusable checks.

## Orders

Calculate revenue, remove test records, enforce order-key uniqueness, and validate business rules.

## Event data

Filter malformed events and derive canonical fields in small reusable transformations.

## Data quality

Insert `check_step()` calls where contracts become true.

The exact transformations depend on the source system, target schema, and business contract.

# 66. Production Anti-Patterns

## Giant one-line chains

**Why it looks attractive:** fewer vertical lines.

**What can go wrong:** code review and incident debugging become difficult.

**Safer approach:** one method per line and named stages at meaningful boundaries.

## Giant lambdas

**Why it looks attractive:** no extra function definition.

**What can go wrong:** business logic becomes anonymous and hard to test.

**Safer approach:** extract a named function.

## Silent quality checks

**Why it looks attractive:** the pipeline keeps running.

**What can go wrong:** bad data reaches later stages.

**Safer approach:** fail, quarantine, or explicitly record according to the pipeline contract.

## Hidden side effects

**Why it looks attractive:** one function "does everything."

**What can go wrong:** repeated runs have surprising state changes.

**Safer approach:** keep transformation and orchestration concerns separate.

## Over-engineered custom accessors

**Why it looks attractive:** the API looks elegant.

**What can go wrong:** the project gains an internal framework that only one person understands.

**Safer approach:** start with ordinary functions.

## In-place mutation

**Why it looks attractive:** fewer assignments.

**What can go wrong:** it breaks chainability and obscures the returned-object flow.

**Safer approach:** return transformed DataFrames and compose them.

# 67. SQL / Data-Platform Connection

A pandas chain can visually resemble a logical ELT flow:

```text
source
→ filter
→ derive
→ transform
→ validate
→ output
```

For example:

| Logical step | pandas style |
| --- | --- |
| Select/filter rows | `query`, boolean indexing |
| Derive columns | `assign` |
| Rename fields | `rename` |
| Custom business transformation | `pipe(function)` |
| Sort | `sort_values` |
| Validate | `pipe(check_step, ...)` |

However, pandas chaining is **not** the same thing as a database query plan.

A pandas expression executes through pandas' DataFrame machinery. It does not automatically become a database execution plan or guaranteed lazy query.

The transferable Data Engineering lesson is the **explicit transformation flow**, not an assumption about execution engines.

# 68. Reusability Guidelines

Create a named function when:

- logic is reused;
- logic is business-significant;
- logic is complex;
- logic deserves a test;
- logic makes a pipeline easier to read.

Do not create a function merely to wrap a one-line operation that is already clearer inline.

Example where a function adds value:

```python
def drop_test_orders(df):
    return df.loc[
        ~df["order_id"].str.startswith("TEST")
    ].copy()
```

Example where a wrapper may add noise:

```python
def sort_by_order_id(df):
    return df.sort_values("order_id")
```

That wrapper is not automatically wrong. It is useful only when the name or reuse communicates domain meaning beyond the built-in call.

# 69. Final Learning Workflow

Use this workflow when converting an existing pandas script into a production-style pipeline:

```text
1. Start with clear named transformations
        ↓
2. Make each transformation return a DataFrame
        ↓
3. Compose custom functions with pipe
        ↓
4. Use assign for derived columns
        ↓
5. Insert validation/logging steps
        ↓
6. Format one method per line
        ↓
7. Break long chains into named stages when needed
        ↓
8. Unit-test each step
        ↓
9. Integration-test the full chain
        ↓
10. Benchmark only when performance matters
```

The discipline is more important than the syntax.

# 70. Final Roadmap Coverage Checklist

## Basics

- [x] method chaining
- [x] methods returning new frames
- [x] `rename`
- [x] `astype`
- [x] `query`
- [x] `assign`
- [x] `sort_values`
- [x] one-method-per-line formatting
- [x] parenthesized chains
- [x] `assign()` with lambdas
- [x] lambda referencing a column created earlier in the same chain
- [x] dependency ordering inside `assign`

## Intermediate

- [x] `pipe(func, *args)`
- [x] `pipe` keyword arguments
- [x] passing DataFrame into custom functions
- [x] small pure/named transformation steps
- [x] `standardise_columns`
- [x] `drop_test_orders`
- [x] `add_revenue`
- [x] composing transformations with `pipe`
- [x] chain length/readability
- [x] when to name intermediate results

## Advanced

- [x] debugging chains
- [x] `log_shape`
- [x] `check`
- [x] `check_step`
- [x] logging row counts
- [x] invariant assertions
- [x] `inplace=True` discouraged
- [x] rationale for avoiding `inplace`
- [x] custom DataFrame accessor
- [x] `pd.api.extensions.register_dataframe_accessor`
- [x] `dq` accessor
- [x] `df.dq.null_report()`
- [x] `df.dq.duplicate_report(key)`
- [x] accessor design trade-offs
- [x] unit testing individual steps
- [x] integration testing entire chain

## Hands-on exercise

- [x] `silver_pipeline.py` fully specified
- [x] `build_silver_orders(raw: pd.DataFrame) -> pd.DataFrame`
- [x] at least eight `pipe()` steps
- [x] `check_step`
- [x] `min_rows`
- [x] uniqueness validation
- [x] logging
- [x] unit tests
- [x] integration test
- [x] `dq` accessor
- [x] `null_report`
- [x] `duplicate_report`

## Quality

- [x] prediction-first exercises
- [x] debugging
- [x] testing
- [x] edge cases
- [x] performance considerations
- [x] memory considerations
- [x] production examples
- [x] anti-patterns
- [x] code-review checklist
- [x] pipeline contract
- [x] SQL/data-platform connection
- [x] checkpoint
- [x] common mistakes
- [x] cheat sheet

# 71. Quick Reference to Official pandas Documentation

This chapter is aligned with the pandas 3.0 documentation current at the time of authoring.

- `DataFrame.assign`
- `DataFrame.pipe`
- User-defined functions and `DataFrame.pipe`
- `DataFrame.drop`
- pandas API reference, including extension APIs

The official pandas documentation is versioned. The current documentation checked for this chapter is pandas **3.0.6**. 

# Appendix A — Roadmap Fidelity

This chapter preserves the Topic 11 roadmap sequence:

```text
Basic
  → method chaining
  → returned DataFrames
  → rename / astype / query / assign / sort_values
  → formatting chains
  → assign lambdas and dependency ordering

Intermediate
  → pipe()
  → arguments
  → named pure-ish transformations
  → standardise_columns
  → drop_test_orders
  → add_revenue
  → chain readability and boundaries

Advanced
  → log_shape / check / check_step
  → logging + invariants
  → avoiding inplace=True
  → custom DataFrame accessors
  → unit and integration testing

Exercise
  → silver_pipeline.py
  → at least eight pipe() steps
  → check_step
  → logging and invariants
  → unit tests
  → integration tests
  → dq accessor

Finish
  → debugging
  → edge cases
  → performance
  → production style
  → checkpoint
  → common mistakes
  → cheat sheet
```

The roadmap's central idea remains the organizing principle: **write known pandas operations as a readable, testable pipeline rather than as an unstructured sequence of mutations.**

# Appendix B — One-Page Mental Model

```text
                ┌──────────────────────────┐
                │        DataFrame         │
                └────────────┬─────────────┘
                             │
                    built-in pandas method
                             │
                             ▼
                ┌──────────────────────────┐
                │     transformed frame    │
                └────────────┬─────────────┘
                             │
                         .assign()
                             │
                             ▼
                ┌──────────────────────────┐
                │    derived columns        │
                └────────────┬─────────────┘
                             │
                           .pipe()
                             │
                             ▼
                ┌──────────────────────────┐
                │   named business step    │
                └────────────┬─────────────┘
                             │
                             ▼
                     validation/check
                             │
                             ▼
                ┌──────────────────────────┐
                │    next pipeline stage   │
                └──────────────────────────┘
```

Remember:

- **chain** = show DataFrame flow;
- **assign** = define derived columns;
- **pipe** = compose custom DataFrame-level logic;
- **named function** = give business logic a contract;
- **check** = make invariants observable;
- **custom accessor** = expose repeated team-wide behavior;
- **intermediate variable** = mark an important phase boundary.

## Final rule

> **Use chains to make data flow visible, use named functions to make business logic testable, and use checks to make pipeline correctness observable.**
