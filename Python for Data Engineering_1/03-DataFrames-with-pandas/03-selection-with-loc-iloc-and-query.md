# 03 — Selection with `loc`, `iloc`, and `query`

This chapter teaches precise DataFrame selection from beginner level to production-oriented Data Engineering practice. The goal is not to memorize indexing syntax. The goal is to reason about **what rows, what columns, what labels, what positions, and what business records** your code is selecting before you execute it.

The chapter uses the modern pandas 3.x mental model from the module roadmap. Pandas documents `.loc` as primarily label-based and `.iloc` as primarily integer-position based; label slices include both endpoints while positional slices follow Python-style exclusive upper bounds. Boolean selection uses `&`, `|`, and `~`, with parentheses required around conditions.

## 1. Why Selection Matters in Data Engineering

Selection is where a DataFrame stops being “all the source data” and becomes the exact subset a downstream operation is allowed to use. A one-row error can later become a wrong aggregation, a bad join, an incorrect report, or a broken ML feature dataset.

A useful pipeline picture is:

```text
Source DataFrame
      ↓
Precise selection
      ↓
Validation
      ↓
Transformation
      ↓
Aggregation / join / output
```

Suppose a revenue report should include only paid orders from India, the United States, and Great Britain during Q1. If the filter accidentally includes pending orders or excludes one valid country, every later revenue number can still be internally consistent while being wrong.

The central engineering question is:

> **Am I selecting by what the row is called, by where the row is located, or by whether the row satisfies a business condition?**

## 2. Prerequisites and Mental Model

You already know that a pandas DataFrame has rows, columns, and an Index. For this chapter, make one distinction permanent in your thinking:

**A label is not the same thing as a position.**

```python
import pandas as pd

df = pd.DataFrame(
    {
        "order_id": [101, 102, 103],
        "amount": [500, 800, 1200],
    },
    index=[10, 20, 30],
)

print(df)
print("row label at first position:", df.index[0])
print("first row by position:")
print(df.iloc[0])
print("row with label 10:")
print(df.loc[10])
```

Expected meaning: the first row happens to have position `0`, but its label is `10`. `.iloc[0]` means “first position.” `.loc[10]` means “row whose label is 10.” The values are the same in this tiny example, but the meaning is different.

## 3. Column Selection Basics

### Selecting one column with `df["col"]`

**What it is:** The expression `df["col"]` selects one named column and returns a `Series`.

**Why it exists:** A Series is the natural one-dimensional result when one column is requested.

**Data Engineering use case:** Use it when a transformation operates on one field.

**Common mistake:** Forgetting that the result is a Series and writing code that expects a DataFrame.

**Production consideration:** Check `type(result)`, `result.shape`, and `result.name` at API boundaries.

```python
amount = df["amount"]
print(type(amount))
print(amount.shape)
print(amount.name)
```

For three rows, the shape is `(3,)`. The index is preserved because the column remains aligned to the DataFrame’s row index.

### Selecting multiple columns with `df[["a", "b"]]`

**What it is:** Passing a list of column labels returns a DataFrame.

**Why it exists:** A list communicates that multiple columns are required and preserves the order in the list.

**Data Engineering use case:** Use it to define a deliberate downstream schema.

**Common mistake:** Using `df["a", "b"]` instead of `df[["a", "b"]]`.

**Production consideration:** Be explicit about column order when output consumers or tests depend on schema order.

```python
small = df[["order_id", "amount"]]
print(type(small))
print(small.shape)
print(small.columns.tolist())
```

For three rows and two columns, the shape is `(3, 2)`. Selecting one column and selecting multiple columns therefore change the object type and shape.

| Expression | Result | Typical shape for 3 source rows |
|---|---|---|
| `df["amount"]` | `Series` | `(3,)` |
| `df[["amount"]]` | `DataFrame` | `(3, 1)` |
| `df[["order_id", "amount"]]` | `DataFrame` | `(3, 2)` |
| `df["missing"]` | raises `KeyError` | — |

## 4. `loc` — Label-Based Selection

`.loc` is the primary tool when the selection meaning depends on labels. Pandas defines `.loc` as primarily label based; it can also take boolean arrays and supports row/column selection together. Label slices include both the start and stop labels when present.

Think of `.loc` as asking:

> “Which rows/columns have these labels?”

```python
df = pd.DataFrame(
    {
        "order_id": [101, 102, 103, 104, 105, 106],
        "amount": [500, 800, 1200, 300, 900, 1500],
        "country": ["IN", "US", "IN", "GB", "US", "IN"],
    },
    index=[0, 1, 2, 3, 4, 5],
)

print(df.loc[2])
print(df.loc[2, "amount"])
print(df.loc[2:4])
print(df.loc[:, ["order_id", "amount"]])
print(df.loc[2:4, ["order_id", "amount"]])
```

Important examples: `df.loc[2]` selects the row whose label is `2`; `df.loc[:, ...]` means all rows; `df.loc[2:4]` includes labels `2`, `3`, and `4`.

### Inclusive Label Slices: `loc[0:5]`

This is one of the most common pandas mistakes. Label-based slicing is inclusive at the end when the endpoint exists. Positional slicing is not.

```python
df = pd.DataFrame({"value": range(8)}, index=range(8))

loc_result = df.loc[0:5]
iloc_result = df.iloc[0:5]

print(len(loc_result))
print(len(iloc_result))
```

Expected output is `6` followed by `5`. `loc[0:5]` asks for labels 0 through 5. `iloc[0:5]` asks for positions 0 through 4.

| Expression | Interpretation | Stop endpoint | Rows returned here |
|---|---|---|---:|
| `df.loc[0:5]` | labels 0 through 5 | included | 6 |
| `df.iloc[0:5]` | positions 0 through 4 | excluded | 5 |

### Non-Default Indexes: Labels Still Mean Labels

A production DataFrame may have an Index such as customer IDs, timestamps, or arbitrary labels. After filtering, the index may no longer be `0..n-1`.

```python
df = pd.DataFrame(
    {"amount": [100, 200, 300, 400, 500]},
    index=[101, 103, 105, 110, 120],
)

print(df.loc[103:110])
print(df.iloc[1:4])
```

Both selections identify the same three rows in this example, but for different reasons: `.loc[103:110]` follows labels; `.iloc[1:4]` follows positions. Changing the index labels would change the `.loc` selection but not the `.iloc` positions.

## 5. `iloc` — Position-Based Selection

`.iloc` is the primary tool for integer-position selection. Positions are zero-based. Slices use Python/NumPy semantics: start included, stop excluded. Pandas documents that non-slice out-of-bounds positions raise `IndexError`, while slice bounds may be out of bounds.

```python
print(df.iloc[0])
print(df.iloc[0, 0])
print(df.iloc[0:3])
print(df.iloc[:, 0])
print(df.iloc[[0, 2, 4]])
print(df.iloc[-1])
print(df.iloc[-2:])
```

Use `.iloc` when the requirement itself is positional: first ten rows, last ten rows, the third column, or a schema-driven fixed position. Do not use position when the requirement is “customer 12345” or “records for March 2026”; those are label/business conditions.

## 6. `loc` vs `iloc` — Deep Comparison

| Question | `.loc` | `.iloc` |
|---|---|---|
| Selection basis | Labels | Integer positions |
| Single row | `df.loc[label]` | `df.iloc[position]` |
| Slice end | Inclusive when endpoint is present | Exclusive |
| Column by name | `df.loc[:, "amount"]` | Not by name directly |
| Column by position | Possible only by composing with positional column selection | `df.iloc[:, 2]` |
| Negative position | Not its main meaning | Supported |
| Business-key selection | Usually appropriate | Usually not |
| First/last N by current order | Possible but less direct | Natural |
| Typical risk | Confusing labels with positions | Assuming positions carry business meaning |

A reliable mental test is: **“What would I write in a data contract?”** If the contract says a label/key/date, prefer label-aware selection. If it says first/last N positions in the current ordering, positional selection may be the right tool.

### Choosing the selection basis

Every selection in this chapter rests on one of five bases. Decide the basis first, then pick the tool.

| Requirement says… | Basis | Typical tool |
|---|---|---|
| “customer 12345”, “March 2026”, “country IN” | label / key | `.loc[label]`, `.loc[mask]` on a meaningful Index |
| “first 10 rows”, “the third column” | position | `.iloc[...]` |
| “orders over 1,000 that are paid” | condition | boolean mask with `.loc`, or `query()` |
| “all numeric columns”, “all text columns” | dtype | `select_dtypes()` |
| “every column starting with `customer_`” | name pattern | `filter(like=...)` or `filter(regex=...)` |

If a requirement is phrased in business terms, it almost never means position. When you catch yourself using `.iloc` for a business rule, the rule is probably depending on row order that nothing guarantees.

## 7. Boolean Filtering

A boolean condition produces a boolean Series aligned with the DataFrame index. Passing that boolean result to `.loc` selects rows where the condition is true.

```python
mask = df["amount"] > 100
print(mask)
filtered = df.loc[mask]
print(filtered)
```

The mask answers one question per row: should this row be kept? Because the mask is aligned with the DataFrame index, selection remains tied to row identity.

### Combining Conditions with `&`, `|`, and `~`

For pandas boolean expressions, use `&` for element-wise AND, `|` for element-wise OR, and `~` for element-wise NOT. Parentheses are required around the individual conditions. Pandas explicitly documents this rule.

```python
mask = (df["amount"] > 100) & (df["country"] == "IN")
result = df.loc[mask]
print(result)
```

This is wrong:

```python
# WRONG: Python's scalar `and` does not combine pandas Series element by element.
# mask = (df["amount"] > 100) and (df["country"] == "IN")
```

The key idea: a pandas condition is a vector of booleans, not one scalar boolean. Python’s `and` and `or` are scalar logical operators and therefore are not the correct tools for element-wise Series conditions.

## 8. `isin()`

`isin` asks whether each value belongs to a supplied collection. It is clearer than manually chaining many equality checks.

```python
approved_countries = ["IN", "US", "GB"]
mask = df["country"].isin(approved_countries)
selected = df.loc[mask]
not_selected = df.loc[~mask]

print(mask.sum())
print(selected)
print(not_selected)
```

Typical applications include approved countries, allowed statuses, selected customer IDs, and other reference lists. For very large or repeatedly reused lookup collections, measure the chosen approach rather than assuming a particular container or expression is always faster.

## 9. `between()`

`between` provides a readable range condition. The default is inclusive at both ends.

```python
mask = df["amount"].between(100, 500)
print(df.loc[mask, ["order_id", "amount"]])
```

`between(100, 500)` is equivalent in intent to `(amount >= 100) & (amount <= 500)` for the default inclusivity. State your boundary semantics when business rules depend on them.

## 10. `isna()` and `notna()`

Missing-value selection should be explicit. `isna()` identifies missing values and `notna()` identifies values that are not missing.

```python
df = pd.DataFrame(
    {
        "order_id": [101, 102, 103],
        "amount": [500.0, None, 900.0],
        "customer_id": ["C1", "C2", None],
    }
)

missing_amounts = df.loc[df["amount"].isna()]
complete_customers = df.loc[df["customer_id"].notna()]

print(missing_amounts)
print(complete_customers)
```

Do not confuse an empty string such as `""` with a missing value unless the source contract says it should be interpreted as missing. That distinction starts at ingestion and continues into selection.

### Unknown predicates: what a missing value does to a condition

A comparison against a missing value is not “true” and not “false”; the answer is unknown. How pandas reports that depends on the dtype.

```python
amount_float = pd.Series([500.0, None, 1500.0])
amount_nullable = pd.Series([500, None, 1500], dtype="Int64")

print((amount_float >= 1000).tolist())     # [False, False, True]
print((amount_nullable >= 1000).tolist())  # [False, <NA>, True]
```

With NumPy float columns, the unknown row silently becomes `False`. With nullable dtypes such as `Int64`, the unknown row stays `<NA>`, so the mask has three states. `.loc[mask]` does not select a row whose mask value is `<NA>`, but the row is not “rejected by the rule” either: it was never evaluated.

Make the decision explicit, and count it:

```python
mask = amount_nullable >= 1000
unknown = mask.isna()

selected = amount_nullable.loc[mask.fillna(False)]

print("selected:", len(selected), "unknown:", int(unknown.sum()))
```

`fillna(False)` states the policy “unknown means not selected”. If a missing amount should instead be quarantined or treated as a data error, select it with `isna()` separately. Topic 04 covers three-valued logic in detail.

## 11. Combining Selection Conditions

Complex filters are easier to audit when you build a named mask instead of one enormous expression.

```python
mask = (
    df["status"].eq("paid")
    & df["country"].isin(["IN", "US", "GB"])
    & df["amount"].between(1000, 10000)
    & df["customer_id"].notna()
)

result = df.loc[mask, ["order_id", "customer_id", "country", "amount"]]

print("matching rows:", mask.sum())
print("match rate:", mask.mean())
print(mask.value_counts())
```

A mask becomes an observable object. You can count it, inspect it, test it, reuse it, and log its match rate. That is useful when investigating why a production batch suddenly contains fewer rows.

Prediction checklist before execution:

- What is the expected row count?
- Which conditions can exclude the same row?
- Can nulls make a condition false or unknown?
- What exact columns should the result contain?

## 12. `query()`

`DataFrame.query()` lets you express row filters as a string expression evaluated against the DataFrame’s columns. It can be concise and readable for many business-style filters.

```python
result = df.query("amount > 100")
print(result)
```

```python
result = df.query("status == 'paid' and amount > 100")
print(result)
```

Query expressions intentionally look different from ordinary Python/Series expressions. The DataFrame’s columns become names in the expression environment. This is convenient, but a string expression can be harder to debug when it becomes overly complex.

### `@local_variable` in `query()`

When a query needs a Python variable from the surrounding scope, prefix that variable with `@`.

```python
minimum_amount = 1000
selected = df.query("amount >= @minimum_amount")
print(selected)
```

The `@` means “use the Python variable named `minimum_amount`.” This is especially useful for parameterized filtering functions.

### Backticks for Column Names with Spaces

Column names that are not valid Python identifiers can be referenced in `query()` with backticks.

```python
df = pd.DataFrame({
    "customer country": ["IN", "US", "IN"],
    "amount": [100, 250, 500],
})

selected = df.query("`customer country` == 'IN'")
print(selected)
```

Backticks make the column name part of the query expression unambiguous. In production, stable column naming conventions are often easier to maintain, but source schemas do not always give you that luxury.

## 13. Boolean Filtering vs `query()`

| Dimension | Boolean mask + `.loc` | `query()` |
|---|---|---|
| Expression form | Native Python/Series operations | String expression |
| Reusable mask | Excellent | Less direct |
| External parameters | Native Python variables | `@variable` |
| Complex custom Python logic | Flexible | More constrained |
| Readability for simple business filters | Good | Often very good |
| Debugging intermediate conditions | Excellent | Can be less direct |
| Potential `numexpr` use | Not the defining feature | Can help for supported expressions |
| Performance | Depends on workload | Can be faster in some cases |

Neither style is universally faster. The pandas documentation notes that `.query()` may use an expression engine such as `numexpr`, but actual performance depends on the expression, data types, size, and environment. Treat performance as a measurement problem, not a rule of thumb.

### Choosing between `query()` and a mask

Prefer `query()` when:

- the filter is a short, self-contained business rule that reads like SQL;
- external values arrive as parameters (`@minimum_amount`);
- the rule will be reviewed by people who read SQL more comfortably than pandas.

Prefer a boolean mask when:

- you need to inspect, count, or log individual conditions (`mask.sum()`, `mask.mean()`);
- the same mask is reused for filtering and assignment;
- the condition uses Python logic that `query()` cannot express;
- you want an IDE, linter, or refactoring tool to see the column names (they are strings inside `query()`).

Whichever you choose, the two styles must agree. A cheap regression test is to compute both and compare:

```python
by_mask = df.loc[(df["amount"] > 100) & (df["country"] == "IN")]
by_query = df.query("amount > 100 and country == 'IN'")

pd.testing.assert_frame_equal(by_mask, by_query)
```

Note that `query()` with extension dtypes (nullable integers, for example) may switch to the Python engine, and pandas can report that with a warning. That is a behavior detail to check in your environment, not a correctness problem.

## 14. Correct Assignment Through Selection

Selection and assignment are different jobs. When the intention is to modify the original DataFrame, use one explicit `.loc[row_condition, column]` selection.

```python
mask = df["amount"] > 10000
df["high_value"] = False
df.loc[mask, "high_value"] = True

mask_review = df["status"].eq("paid") & (df["country"] == "IN")
df.loc[mask_review, "risk_flag"] = "REVIEW"
```

This states exactly which rows and which column are being modified. Deep Copy-on-Write mechanics belong to Topic 12, but the selection habit starts here.

### Initialize the target column before a conditional assignment

If the column does not exist yet, `.loc[mask, "new_column"] = True` creates it only for the selected rows. Every other row has no value at all, so pandas fills them with `NaN` and the column silently becomes `object`.

```python
orders = pd.DataFrame({"amount": [50, 12000, 300]})

orders.loc[orders["amount"] >= 10000, "high_value"] = True
print(orders["high_value"].dtype)      # object
print(orders["high_value"].tolist())   # [nan, True, nan]
```

That column is not a boolean flag: `~orders["high_value"]` raises `TypeError` on the `NaN` rows, and a missing value now carries meaning nobody chose. Initialize first:

```python
orders = pd.DataFrame({"amount": [50, 12000, 300]})

orders["high_value"] = False
orders.loc[orders["amount"] >= 10000, "high_value"] = True

print(orders["high_value"].dtype)      # bool
print(orders["high_value"].tolist())   # [False, True, False]
```

Initialization gives every row an intentional default, a predictable dtype, and a contract that can be tested: `orders["high_value"].dtype == "bool"` and no missing values. Use a nullable default (for example `pd.array([pd.NA] * len(orders), dtype="boolean")`) only when “not evaluated” is a real state that downstream code must see.

Incorrect pattern to avoid in production code:

```python
# Avoid chained selection for assignment:
# df[df["amount"] > 10000]["high_value"] = True
```

The engineering rule is: **when assigning back to the original DataFrame, select the rows and target column in one `.loc[...]` operation.**

## 15. `at` and `iat`

`at` and `iat` are scalar accessors. Use `at` for one label-based cell and `iat` for one position-based cell.

```python
df = pd.DataFrame(
    {"amount": [100, 200, 300], "country": ["IN", "US", "GB"]},
    index=[101, 102, 103],
)

print(df.at[101, "amount"])
print(df.iat[0, 0])
```

| Accessor | Meaning | Example |
|---|---|---|
| `at` | scalar by label | `df.at[101, "amount"]` |
| `iat` | scalar by position | `df.iat[0, 0]` |
| `loc` | label-aware general selection | `df.loc[101, "amount"]` |
| `iloc` | position-aware general selection | `df.iloc[0, 0]` |

Use `at`/`iat` when one cell is explicitly the unit of work. They are not substitutes for broad filtering.

## 16. `where()` and `mask()`

Filtering removes rows. `where()` and `mask()` are conditional replacement tools: they preserve the object’s shape while changing selected values.

```python
df = pd.DataFrame({"amount": [100, -50, 200]})

filtered = df.loc[df["amount"] >= 0]
masked = df["amount"].mask(df["amount"] < 0)
where_result = df["amount"].where(df["amount"] >= 0, other=0)

print(filtered)
print(masked)
print(where_result)

assert len(filtered) == 2
assert len(masked) == len(df)
assert len(where_result) == len(df)
```

Filtering changes row count because unwanted rows disappear. `mask`/`where` keep the same number of rows and replace values that do not satisfy the condition. Pandas describes `where` as the shape-preserving alternative when you need to retain the original dimensionality.

| Goal | Typical operation | Row count |
|---|---|---|
| Remove invalid rows | `df.loc[condition]` | Can decrease |
| Replace invalid values | `df["amount"].mask(condition)` | Preserved |
| Keep values meeting a condition, replace the rest | `df["amount"].where(condition, replacement)` | Preserved |

## 17. `select_dtypes()`

`select_dtypes()` selects columns based on dtype rather than hard-coded names. This is useful for generic profiling and transformations.

```python
numeric = df.select_dtypes(include="number")
textual = df.select_dtypes(include="string")
boolean = df.select_dtypes(include="bool")
non_numeric = df.select_dtypes(exclude="number")
```

This is useful when a generic function must find all numeric measures or all text fields. For critical production schemas, explicit named columns can still be clearer because dtype alone may be too broad a rule.

### `object` is not “text” in pandas 3.x

Before pandas 3, string columns were stored as `object`, so `select_dtypes(include=object)` was a common way to find “all string columns”. That habit is no longer reliable:

- pandas 3.x infers string data as a dedicated default string dtype, displayed as `str`, not as `object`;
- `object` is generic Python-object storage. A column of dicts, lists, `Decimal` values, or mixed types is `object`, and it is not text;
- pandas 3.0 still lets `include=object` match `str` columns for backward compatibility, but it emits a warning saying that behavior is deprecated and will be removed.

Select text columns explicitly on pandas 3.x:

```python
df = pd.DataFrame(
    {
        "order_id": [1, 2],
        "country": ["IN", "US"],
        "note": pd.Series(["a", "b"], dtype="string"),
        "payload": pd.Series([{"k": 1}, [2]], dtype=object),
    }
)

print(df.select_dtypes(include="str").columns.tolist())
# ['country', 'note']
```

For code that must run on both pandas 2.x and 3.x, list the string dtypes and the legacy object dtype together:

```python
compatible = df.select_dtypes(include=["object", "string"])
print(compatible.columns.tolist())
# ['country', 'note', 'payload']
```

The `payload` column is included because it is `object`. That is the price of compatibility: on pandas 2.x you cannot separate real text from other objects by dtype alone. If the distinction matters, check the values (for example with `pd.api.types.infer_dtype`) or select by explicit column names.

## 18. `filter()` by Column Name Pattern

`filter()` can select labels by a name pattern. It can use `like=` or `regex=`.

```python
amount_columns = df.filter(like="amount")
customer_columns = df.filter(regex=r"^customer_")
```

This is useful for families of fields such as `customer_id`, `customer_country`, and `customer_segment`. It is a label-selection operation, not a row-condition filter.

## 19. MultiIndex Selection

A MultiIndex represents multiple levels of row labels. It can model a grain such as `(country, month)`. Selection becomes a question of which level or combination of levels you want.

```python
import pandas as pd

index = pd.MultiIndex.from_tuples(
    [
        ("IN", "2025-01"),
        ("IN", "2025-02"),
        ("US", "2025-01"),
        ("US", "2025-02"),
    ],
    names=["country", "month"],
)

df = pd.DataFrame({"revenue": [100, 120, 200, 220]}, index=index)

print(df.loc["IN"])
print(df.loc[("IN", "2025-01")])
```

`df.loc["IN"]` selects all rows in the first level with country `IN`. `df.loc[("IN", "2025-01")]` identifies a specific combination of levels.

### `pd.IndexSlice`

For more explicit MultiIndex slicing, `pd.IndexSlice` provides a readable way to build multi-level indexers.

```python
idx = pd.IndexSlice
selected = df.loc[idx["IN", "2025-01":"2025-02"], :]
print(selected)
```

Read this as: for the first index level choose `IN`; for the second level choose the inclusive label range from `2025-01` to `2025-02`; select all columns.

### Selecting Across a MultiIndex Level

When the requirement is “one month across all countries,” the second level is the target dimension.

```python
selected = df.loc[idx[:, "2025-01"], :]
print(selected)
```

The first `:` means every country; the second label selects one month. This is the power and complexity of a hierarchical row index: the selection statement mirrors the grain.

### Sorting Considerations

MultiIndex operations are easier to reason about when level ordering is intentional and the index is sorted when ordering-dependent selection or lookup behavior requires it.

```python
df = df.sort_index()
print(df.index)
```

Do not assume sorting automatically makes every operation faster. The point is predictability and compatibility with operations that benefit from ordered index structure.

### Unsorted MultiIndex: what fails and what does not

Row order is part of a MultiIndex's contract. Build one in arrival order, as a source system might deliver it:

```python
import pandas as pd

index = pd.MultiIndex.from_tuples(
    [
        ("US", "2025-01"),
        ("IN", "2025-02"),
        ("US", "2025-02"),
        ("IN", "2025-01"),
    ],
    names=["country", "month"],
)

unsorted_df = pd.DataFrame({"revenue": [100, 120, 200, 220]}, index=index)
idx = pd.IndexSlice

print(unsorted_df.index.is_monotonic_increasing)  # False
```

Exact lookups still work on this unsorted index:

```python
print(unsorted_df.loc[("US", "2025-02")])   # revenue 200
print(unsorted_df.loc["IN"])                # both IN rows
```

An ordered range slice across levels does not:

```python
try:
    unsorted_df.loc[idx["IN", "2025-01":"2025-02"], :]
except pd.errors.UnsortedIndexError as exc:
    print(type(exc).__name__, exc)
# UnsortedIndexError MultiIndex slicing requires the index to be lexsorted: ...
```

Sort the index, and the same logical slice succeeds:

```python
sorted_df = unsorted_df.sort_index()

print(sorted_df.index.is_monotonic_increasing)  # True
print(sorted_df.loc[idx["IN", "2025-01":"2025-02"], :])
#                  revenue
# country month
# IN      2025-01      220
#         2025-02      120
```

The rules to remember:

- not every MultiIndex operation needs sorting; exact tuple or single-label lookup works on an unsorted index;
- ordered range slicing across multiple levels can require a sorted (lexsorted) MultiIndex, and pandas raises `UnsortedIndexError` when it does;
- do not “fix” this by catching the error; call `sort_index()` deliberately;
- production code should state its ordering requirement explicitly, for example by asserting `df.index.is_monotonic_increasing` before slicing, so a change in upstream row order fails loudly.

### Reasoning about row grain with a MultiIndex

A MultiIndex encodes a grain: `(country, month)` means one row per country per month. Before selecting, check that the grain holds:

```python
assert sorted_df.index.is_unique
```

If the index is not unique, `.loc[("IN", "2025-01")]` can return several rows instead of one, and code that expects a scalar or a single row will break or, worse, quietly use the wrong row. A selection like `idx[:, "2025-01"]` (“one month across all countries”) returns one row per country only when the grain is unique. State the grain, assert it, then select.

## 20. DatetimeIndex Partial-String Selection

A DatetimeIndex lets label-aware selection express time ranges naturally. Partial string selection such as `"2025-03"` can select the matching month when the index contains timestamps compatible with that expression.

```python
dates = pd.date_range("2025-03-01", periods=12, freq="D")
df = pd.DataFrame({"events": range(12)}, index=dates)
df = df.sort_index()

print(df.loc["2025-03"])
print(df.loc["2025-03-05":"2025-03-08"])
```

Sorting the DatetimeIndex first makes the intended temporal order explicit and supports predictable range-style selection. The detailed resampling/rolling mechanics come later in Topic 09.

## 21. Selection After Filtering — Index Awareness

Filtering usually preserves the existing index labels; it does not automatically renumber them.

```python
df = pd.DataFrame(
    {"amount": [500, 1500, 700, 2000]},
    index=[10, 11, 12, 13],
)
filtered = df.loc[df["amount"] > 1000]

print(filtered.index.tolist())
print(filtered.iloc[0])

# This asks for label 0, not "the first remaining row".
# filtered.loc[0] would raise KeyError here because label 0 is absent.
```

This is why “the first remaining row” should be expressed with `.iloc[0]`, while “the row with label 11” should be expressed with `.loc[11]`. If a fresh `0..n-1` index is actually required for an output contract, reset it intentionally rather than assuming it already exists.

## 22. Empty Selection Results

A filter may legitimately match no rows. Production code must treat an empty result as a valid state unless the business contract says zero matches are an error.

```python
result = df.loc[df["amount"] > 10_000_000]

print(result.empty)
print(len(result))
print(result.shape)
```

A robust filtering function should return a DataFrame with the expected columns and dtypes even when no rows match.

```python
import pandas as pd

ORDERS_COLUMNS = {
    "order_id": "string",
    "amount": "Float64",
    "country": "string",
}

def empty_orders() -> pd.DataFrame:
    return pd.DataFrame({
        name: pd.Series(dtype=dtype)
        for name, dtype in ORDERS_COLUMNS.items()
    })

def filter_orders(df: pd.DataFrame, minimum_amount: float) -> pd.DataFrame:
    mask = df["amount"] >= minimum_amount
    result = df.loc[mask, list(ORDERS_COLUMNS)]
    if result.empty:
        return empty_orders()
    return result
```

The function makes an important promise: its output schema remains predictable even when the row count is zero. That is valuable for batch pipelines whose downstream stages still expect the same columns and types.

## 23. Performance Engineering for Selection

Selection performance has several dimensions: CPU time, memory allocation, repeated scans, parsing of query expressions, and the size of intermediate boolean masks.

### Repeated Filtering vs Reusing a Mask

```python
# Repeated scans may repeat the same work.
first = df.loc[df["amount"] > 1000]
second = df.loc[df["amount"] > 1000]

# If the same condition is reused, compute it once.
large_amount = df["amount"] > 1000
first = df.loc[large_amount]
second = df.loc[large_amount & df["country"].eq("IN")]
```

A reused mask can improve clarity and avoid repeated construction when the exact condition is needed multiple times. Measure the real workload before claiming a significant speedup.

### Combined Mask vs Multiple Sequential Filters

```python
combined = df.loc[(df["amount"] > 1000) & (df["country"] == "IN")]

stepwise = df.loc[df["amount"] > 1000]
stepwise = stepwise.loc[stepwise["country"] == "IN"]
```

Both can be correct. The combined mask often makes the business rule easier to see and can avoid materializing an unnecessary intermediate DataFrame. The best choice should be measured on the actual dataset and kept readable.

### Large `isin()` Collections

When filtering millions of rows against a large reference collection, the membership test can become a meaningful part of runtime. The main production rule is not “always use a set” or “always use a list”; it is “measure the real workload and keep the rule explicit.” If the same reference set is reused across many operations, precomputing or caching the appropriate representation may help.

### `query()` and `numexpr`

For some large numeric expressions, `query()` can use `numexpr`, which may reduce some intermediate expression overhead. This is workload-dependent; string parsing, dtypes, expression support, DataFrame size, and the execution environment all matter. Benchmark rather than assume.

```python
from time import perf_counter

start = perf_counter()
result_mask = df.loc[(df["amount"] > 1000) & (df["country"] == "IN")]
mask_seconds = perf_counter() - start

start = perf_counter()
result_query = df.query("amount > 1000 and country == 'IN'")
query_seconds = perf_counter() - start

print({"mask_seconds": mask_seconds, "query_seconds": query_seconds})
```

For a fair benchmark, run each method multiple times on the same data, avoid including DataFrame construction in the timed region, and verify that both methods produce equivalent results before comparing timings.

A timing comparison between two implementations that return different rows is meaningless, so make the equivalence check part of the benchmark:

```python
from time import perf_counter

def best_of(func, repeats=5):
    timings = []
    for _ in range(repeats):
        start = perf_counter()
        func()
        timings.append(perf_counter() - start)
    return min(timings)

def with_mask():
    return df.loc[(df["amount"] > 1000) & (df["country"] == "IN")]

def with_query():
    return df.query("amount > 1000 and country == 'IN'")

pd.testing.assert_frame_equal(with_mask(), with_query())

print({"mask_seconds": best_of(with_mask), "query_seconds": best_of(with_query)})
```

Report the data size and pandas version next to the numbers. Timings from a 1,000-row frame say little about a 1,000,000-row frame.

## 24. SQL `WHERE` → pandas Translation

Selection is easier to master when you can translate business conditions between SQL-style thinking and pandas expressions. Each example below uses the same conceptual dataset.

```python
df = pd.DataFrame({
    "order_id": [101, 102, 103, 104],
    "amount": [500, 1500, 2500, 50],
    "country": ["IN", "US", "IN", "GB"],
    "status": ["paid", "paid", "pending", "paid"],
    "customer_id": ["C1", "C2", None, "C4"],
    "created_at": pd.to_datetime([
        "2025-01-05", "2025-02-10", "2025-03-15", "2025-04-01"
    ]),
})
```

### 01. Equality

**SQL-style condition:**

```sql
status = 'paid'
```

**pandas mask / `.loc`:**

```python
df.loc[df["status"].eq("paid")]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("status == 'paid'")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 02. Inequality

**SQL-style condition:**

```sql
amount > 1000
```

**pandas mask / `.loc`:**

```python
df.loc[df["amount"] > 1000]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("amount > 1000")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 03. AND

**SQL-style condition:**

```sql
status = 'paid' AND amount > 1000
```

**pandas mask / `.loc`:**

```python
df.loc[(df["status"] == "paid") & (df["amount"] > 1000)]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("status == 'paid' and amount > 1000")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 04. OR

**SQL-style condition:**

```sql
country = 'IN' OR country = 'GB'
```

**pandas mask / `.loc`:**

```python
df.loc[df["country"].isin(["IN", "GB"])]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("country in ['IN', 'GB']")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 05. NOT

**SQL-style condition:**

```sql
NOT status = 'pending'
```

**pandas mask / `.loc`:**

```python
df.loc[~df["status"].eq("pending")]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("status != 'pending'")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 06. IN

**SQL-style condition:**

```sql
country IN ('IN', 'US', 'GB')
```

**pandas mask / `.loc`:**

```python
df.loc[df["country"].isin(["IN", "US", "GB"])]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("country in ['IN', 'US', 'GB']")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 07. BETWEEN

**SQL-style condition:**

```sql
amount BETWEEN 500 AND 2000
```

**pandas mask / `.loc`:**

```python
df.loc[df["amount"].between(500, 2000)]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("amount >= 500 and amount <= 2000")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 08. NULL

**SQL-style condition:**

```sql
customer_id IS NULL
```

**pandas mask / `.loc`:**

```python
df.loc[df["customer_id"].isna()]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("customer_id != customer_id")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 09. NOT NULL

**SQL-style condition:**

```sql
customer_id IS NOT NULL
```

**pandas mask / `.loc`:**

```python
df.loc[df["customer_id"].notna()]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("customer_id == customer_id")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 10. Multiple predicates

**SQL-style condition:**

```sql
status = 'paid' AND country IN ('IN', 'US') AND amount >= 1000
```

**pandas mask / `.loc`:**

```python
df.loc[(df["status"] == "paid") & df["country"].isin(["IN", "US"]) & (df["amount"] >= 1000)]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("status == 'paid' and country in ['IN', 'US'] and amount >= 1000")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 11. Date lower bound

**SQL-style condition:**

```sql
created_at >= DATE '2025-02-01'
```

**pandas mask / `.loc`:**

```python
df.loc[df["created_at"] >= pd.Timestamp("2025-02-01")]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("created_at >= '2025-02-01'")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 12. Date range

**SQL-style condition:**

```sql
created_at >= DATE '2025-01-01' AND created_at < DATE '2025-04-01'
```

**pandas mask / `.loc`:**

```python
df.loc[(df["created_at"] >= "2025-01-01") & (df["created_at"] < "2025-04-01")]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("created_at >= '2025-01-01' and created_at < '2025-04-01'")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 13. High-value paid orders

**SQL-style condition:**

```sql
status = 'paid' AND amount > 1000
```

**pandas mask / `.loc`:**

```python
df.loc[(df["status"] == "paid") & (df["amount"] > 1000), ["order_id", "amount"]]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("status == 'paid' and amount > 1000")[["order_id", "amount"]]
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 14. Invalid records

**SQL-style condition:**

```sql
amount < 0 OR customer_id IS NULL
```

**pandas mask / `.loc`:**

```python
df.loc[(df["amount"] < 0) | (df["customer_id"].isna())]
```

**pandas `query()` equivalent where appropriate:**

```python
df.query("amount < 0 or customer_id != customer_id")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

### 15. Parameterized filter

**SQL-style condition:**

```sql
amount >= :minimum_amount
```

**pandas mask / `.loc`:**

```python
minimum_amount = 1000
df.loc[df["amount"] >= minimum_amount]
```

**pandas `query()` equivalent where appropriate:**

```python
minimum_amount = 1000
df.query("amount >= @minimum_amount")
```

**Prediction:** Before running it, state the expected number of matching rows and identify which business rule removes each non-matching row. Treat row count as a first-class invariant.

## 25. Hands-on Exercise — `order_filters.py`

The roadmap exercise uses a 1,000,000-row orders DataFrame. This section is the complete exercise specification; create the `.py` implementation and tests in your existing lab project, but keep the exercise itself here in the chapter.

### Scenario

You have one million synthetic orders with columns: `order_id`, `customer_id`, `country`, `status`, `amount`, and `created_at`. The dataset should be large enough to make filtering and memory choices observable, but should be reduced if the local machine cannot handle one million rows comfortably.

### Exercise 1 — Paid Orders

Select paid orders from exactly three countries, within Q1, and above a defined amount threshold. Implement it first with `.loc` + boolean masks, then with `.query()`. Explicitly select the output columns.

```python
countries = ["IN", "US", "GB"]
start = "2025-01-01"
end = "2025-04-01"
minimum_amount = 1000

mask = (
    orders["status"].eq("paid")
    & orders["country"].isin(countries)
    & (orders["created_at"] >= start)
    & (orders["created_at"] < end)
    & orders["amount"].ge(minimum_amount)
)

paid_q1 = orders.loc[
    mask,
    ["order_id", "customer_id", "country", "status", "amount", "created_at"],
]

paid_q1_query = orders.query(
    "status == 'paid' and country in @countries and "
    "created_at >= @start and created_at < @end and "
    "amount >= @minimum_amount"
)[["order_id", "customer_id", "country", "status", "amount", "created_at"]]
```

### Exercise 2 — Flag High-Value Orders

Create `high_value` and set it to `True` only for rows over the agreed threshold. Initialize the column first, then use one `.loc` assignment.

```python
orders["high_value"] = False

high_value_mask = orders["amount"] >= 10000

orders.loc[high_value_mask, "high_value"] = True
```

Initialization is preferable to creating the column through the `.loc` assignment alone:

- every row receives an intentional default state;
- the target column has a predictable boolean dtype;
- partial assignment does not create a column whose missing values determine its semantics.

Test that every row marked `True` meets the threshold and that every row above the threshold is marked `True`.

### Exercise 3 — Replace Negative Amounts

Use `mask()` to replace invalid negative amounts with missing values without removing rows. Verify that the DataFrame shape is unchanged.

```python
rows_before = len(orders)

negative_amount = orders["amount"] < 0
orders["amount"] = orders["amount"].mask(negative_amount)

assert len(orders) == rows_before
```

The row count is saved before the operation so the assertion compares the result with the original, not with itself.

### Exercise 4 — Positional Selection

Use `.iloc` to select the first 10 rows and last 10 rows. Assert both result shapes. This should test position, not label identity.

```python
first_10 = orders.iloc[:10]
last_10 = orders.iloc[-10:]

assert first_10.shape[0] == min(10, len(orders))
assert last_10.shape[0] == min(10, len(orders))
```

### Exercise 5 — DatetimeIndex Selection

Create or use a sorted DatetimeIndex and select one date range with `.loc`. Verify the minimum and maximum timestamps in the result are inside the requested range.

### Exercise 6 — Empty-Result Function

Write `filter_orders(df, minimum_amount, countries, start, end)` so that it returns a correctly typed empty DataFrame when no rows match. Test normal matches, zero matches, all rows matching, and an empty input DataFrame.

## 26. Debugging Selection Problems

For each bug use the diagnostic sequence: **Symptom → Root cause → Inspect → Correct → Prevention.**

### Bug 1 — `and` instead of `&`

**Buggy code:**

```python
mask = (df["amount"] > 100) and (df["country"] == "IN")
```

**Correct approach:**

```python
mask = (df["amount"] > 100) & (df["country"] == "IN")
```

**Why:** Boolean Series are element-wise vectors; Python `and` expects a single truth value.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 2 — `or` instead of `|`

**Buggy code:**

```python
mask = (df["country"] == "IN") or (df["country"] == "US")
```

**Correct approach:**

```python
mask = (df["country"] == "IN") | (df["country"] == "US")
```

**Why:** Use element-wise boolean operators.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 3 — Missing parentheses

**Buggy code:**

```python
mask = df["amount"] > 100 & df["country"].eq("IN")
```

**Correct approach:**

```python
mask = (df["amount"] > 100) & (df["country"].eq("IN"))
```

**Why:** Parenthesize each comparison.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 4 — `iloc` with a label

**Buggy code:**

```python
df.iloc[101]
```

**Correct approach:**

```python
row = df.loc[101]
```

**Why:** `iloc` means position, not label.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 5 — Assuming the index is `0..n-1`

**Buggy code:**

```python
filtered.loc[0]
```

**Correct approach:**

```python
first_row = filtered.iloc[0]
```

**Why:** Filtering usually preserves index labels.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 6 — Series/DataFrame type surprise

**Buggy code:**

```python
df["amount"][0]
```

**Correct approach:**

```python
result = df[["amount"]]
```

**Why:** Single bracket selects one Series; double bracket selects a DataFrame.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 7 — Missing column

**Buggy code:**

```python
df.loc[:, ["order_id", "revenue"]]
```

**Correct approach:**

```python
required = ["order_id", "revenue"]
missing = [col for col in required if col not in df.columns]
if missing:
    raise KeyError(f"Missing required columns: {missing}")
result = df.loc[:, required]
```

**Why:** Treat missing columns as a schema problem, not something to silently ignore.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 8 — Chained assignment pattern

**Buggy code:**

```python
df[df["amount"] > 1000]["high_value"] = True
```

**Correct approach:**

```python
df.loc[df["amount"] > 1000, "high_value"] = True
```

**Why:** Select rows and target column in one assignment.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 9 — Filtering instead of replacement

**Buggy code:**

```python
df = df.loc[df["amount"] >= 0]
```

**Correct approach:**

```python
df["amount"] = df["amount"].mask(df["amount"] < 0)
```

**Why:** Filtering removes rows; `mask` preserves shape.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 10 — Wrong `query` variable syntax

**Buggy code:**

```python
minimum_amount = 1000; df.query("amount >= minimum_amount")
```

**Correct approach:**

```python
minimum_amount = 1000
result = df.query("amount >= @minimum_amount")
```

**Why:** Local Python variables need `@` in a query expression.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 11 — Column name with spaces

**Buggy code:**

```python
df.query("customer country == 'IN'")
```

**Correct approach:**

```python
result = df.query("`customer country` == 'IN'")
```

**Why:** Backticks escape non-identifier column names in query expressions.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 12 — MultiIndex confusion

**Buggy code:**

```python
df.loc["IN", "2025-01"]
```

**Correct approach:**

```python
result = df.loc[("IN", "2025-01")]
```

**Why:** The row index has multiple levels and tuple semantics matter.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 13 — Partial datetime selection on the wrong index

**Buggy code:**

```python
df.loc["2025-03"]
```

**Correct approach:**

```python
df = df.sort_index()
result = df.loc["2025-03"]
```

**Why:** Partial-string selection is label-aware and index-type dependent; validate the index first.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 14 — Assuming a filter always returns rows

**Buggy code:**

```python
result.iloc[0]
```

**Correct approach:**

```python
def first_row_or_empty(result):
    if result.empty:
        return result
    return result.iloc[0]
```

**Why:** Zero matches are a legitimate state unless the business contract says otherwise.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

### Bug 15 — Boolean indexer mismatch with `iloc`

**Buggy code:**

```python
df.iloc[some_boolean_series, 1]
```

**Correct approach:**

```python
result = df.iloc[some_boolean_series.to_numpy(), 1]
```

**Why:** `.loc` understands an aligned boolean Series; `.iloc` is position-oriented and should receive a boolean array for this pattern.

**Prevention:** Add a small assertion or schema/index check around the operation when the assumption matters.

## 27. Production Data Engineering Patterns

### Valid transaction filtering

Build one named mask for required business conditions and log the number and percentage of retained rows.

### Paid-order selection

Treat status semantics as part of the rule; do not substitute a numeric shortcut such as amount > 0.

### High-value transactions

Keep the threshold in a named variable so the rule is reviewable and testable.

### Quarantine selection

Select records that violate a rule into a quarantine DataFrame while preserving enough columns to explain the failure.

### Incremental batch selection

Select by explicit date/time or batch fields rather than relying on row position.

### Date partition selection

Use a DatetimeIndex or explicit timestamp conditions with clear timezone assumptions.

### Reference-list filtering

Use `isin` for approved/allowed sets and validate the size and meaning of the reference data.

### Zero-result handling

Return a stable schema and decide explicitly whether “zero rows” is success, warning, or failure.

### ML/AI feature selection

Select only the fields needed by the feature transformation to reduce accidental leakage and unnecessary work.

Selection quality is a correctness problem. It also supports idempotency, auditability, reproducibility, downstream joins, aggregations, metrics, and feature-data construction because later stages depend on the exact population selected here.

## 28. Testing Strategy

Selection tests should assert semantics, not merely that code runs.

| Test category | Example invariant |
|---|---|
| Selected rows | `set(result["order_id"]) == expected_ids` |
| Selected columns | `result.columns.tolist() == expected_columns` |
| `loc` slicing | stop label included when present |
| `iloc` slicing | stop position excluded |
| Boolean filters | every row satisfies the intended predicate |
| `isin` | every selected value belongs to the reference set |
| `between` | boundaries behave as documented for the chosen inclusivity |
| Missing values | `.isna()` / `.notna()` produce expected counts |
| Query | query result equals mask-based result |
| Assignment | only intended rows/column values changed |
| `where`/`mask` | row count and index unchanged |
| MultiIndex | expected levels/labels are present |
| Datetime selection | all returned timestamps are within the intended range |
| Empty result | schema remains stable when zero rows match |

```python
import pandas as pd

expected = pd.DataFrame(
    {
        "order_id": [102, 103],
        "amount": [1500, 2500],
    },
    index=[1, 2],
)

result = df.loc[df["amount"] >= 1500, ["order_id", "amount"]]
pd.testing.assert_frame_equal(result, expected)
```

When complete DataFrames must match, `pandas.testing.assert_frame_equal` checks more than values alone. That is important because a correct set of values with the wrong index or wrong columns can still be an incorrect transformation.

Test the semantics of the selection, not only its output on one happy-path frame. Use a small frame where every boundary is present:

```python
df = pd.DataFrame(
    {
        "order_id": [1, 2, 3, 4, 5],
        "amount": [99, 100, 500, 501, None],
        "country": ["IN", "IN", "US", "IN", "IN"],
    },
    index=[10, 11, 12, 13, 14],
)

mask = df["amount"].between(100, 500) & df["country"].eq("IN")
result = df.loc[mask]

assert result["order_id"].tolist() == [2]              # boundary 100 included, 500 belongs to US
assert result.index.tolist() == [11]                   # labels preserved, not renumbered
assert not df["amount"].isna().loc[mask].any()         # a missing amount is never selected
assert df.loc[10:11].shape[0] == 2                     # loc slice end is inclusive
assert df.iloc[10:11].shape[0] == 0                    # iloc slice past the end is empty, not an error
```

Each assertion pins one rule: boundary inclusivity, index preservation, null handling, and the `loc`/`iloc` difference. A test that only checks that the code runs would pass even if any of those rules changed.

## 29. Prediction-First Practice

Before running each example below, write down: **rows, columns, dtypes, index, selection basis, and expected meaning.**

### Prediction 1 — Non-default labels

```python
b = df.loc[103:110]
```

**Your task:** Predict which labels are included and how many rows are returned.

### Prediction 2 — First positions

```python
b = df.iloc[:5]
```

**Your task:** Predict the five positions selected even if the index labels are unrelated.

### Prediction 3 — Boolean mask

```python
b = df.loc[df["amount"] > 1000]
```

**Your task:** Predict the row count and preserved index labels.

### Prediction 4 — Membership

```python
b = df.loc[df["country"].isin(["IN", "US"])]
```

**Your task:** Predict which distinct countries can appear in the result.

### Prediction 5 — Conditional replacement

```python
b = df["amount"].mask(df["amount"] < 0)
```

**Your task:** Predict that Series length stays unchanged.

### Prediction 6 — MultiIndex tuple

```python
b = df.loc[("IN", "2025-01")]
```

**Your task:** Predict the exact level combination selected.

### Prediction 7 — Datetime partial string

```python
b = df.loc["2025-03"]
```

**Your task:** Predict the time span returned, assuming a sorted DatetimeIndex.

### Prediction 8 — One-column selection

```python
b = df["amount"]
```

**Your task:** Predict `Series`, not `DataFrame`, and shape `(n,)`.

### Prediction 9 — Two-column selection

```python
b = df[["order_id", "amount"]]
```

**Your task:** Predict `DataFrame` and shape `(n, 2)`.

### Prediction 10 — Query parameter

```python
b = df.query("amount >= @minimum_amount")
```

**Your task:** Predict the same business subset as the equivalent boolean mask.

## 30. Common Mistakes Summary

| Mistake | Why it happens | Correct pattern |
|---|---|---|
| `and` / `or` with Series | Scalar Python logic is not element-wise Series logic | `&` / `|` with parentheses |
| Missing parentheses | Python/operator precedence surprises | Parenthesize each comparison |
| `iloc` with labels | Label and position are confused | Use `.loc[label]` for labels |
| Assuming index is `0..n-1` | Filtering preserves labels | Inspect `df.index`; use `iloc` for positions |
| Expecting `df["col"]` to be a DataFrame | Single-column selection returns Series | Use `df[["col"]]` for one-column DataFrame |
| Selecting a missing column | Source schema changed or typo | Validate `df.columns` / schema contract |
| Chained assignment | Selection and mutation are mixed implicitly | `df.loc[mask, "col"] = value` |
| Using filtering to replace invalid values | Filtering drops rows | `where` / `mask` |
| Wrong query local-variable syntax | Query has its own expression scope | `@variable` |
| Query column with spaces fails | Name is not a simple identifier | Backticks |
| MultiIndex selection feels inconsistent | Multiple levels require tuple/level semantics | Use tuples or `IndexSlice` |
| Partial datetime selection surprises | Index is not the expected datetime type/order | Validate and sort the DatetimeIndex |
| Zero-match result crashes downstream | Code assumes at least one row | Check `.empty` and keep schema stable |

## 31. Selection Cheat Sheet

| Goal | Pattern | Meaning |
|---|---|---|
| One column | `df["col"]` | Series |
| Multiple columns | `df[["a", "b"]]` | DataFrame, explicit order |
| Row by label | `df.loc[label]` | Label-based |
| Rows by label slice | `df.loc[start:stop]` | Inclusive stop label |
| Rows + columns | `df.loc[rows, cols]` | Label-aware on both axes |
| Row by position | `df.iloc[pos]` | Position-based |
| Rows by position slice | `df.iloc[start:stop]` | Exclusive stop position |
| First/last N | `df.iloc[:N]`, `df.iloc[-N:]` | Position-based |
| Boolean rows | `df.loc[mask]` | Condition-based |
| Membership | `df.loc[df["col"].isin(values)]` | Set membership |
| Range | `df.loc[df["col"].between(low, high)]` | Inclusive by default |
| Missing values | `df.loc[df["col"].isna()]` | Missing-only selection |
| Query string | `df.query("...")` | Expression-based filtering |
| Query local variable | `df.query("amount >= @minimum_amount")` | External Python parameter |
| Query name with spaces | `df.query("`customer country` == 'IN'")` | Backtick identifier |
| Single cell by label | `df.at[label, "col"]` | Scalar |
| Single cell by position | `df.iat[pos, col_pos]` | Scalar |
| Shape-preserving replacement | `df["col"].where(...)` / `.mask(...)` | Replace values, keep rows |
| Select numeric columns | `df.select_dtypes(include="number")` | Dtype-based |
| Select columns by pattern | `df.filter(like="amount")` / `regex=...` | Label pattern |
| MultiIndex slice | `df.loc[pd.IndexSlice[...], :]` | Level-aware selection |
| Empty-result check | `result.empty` | Zero-row detection |

## 32. Checkpoint

Do not move on until you can answer these without looking at your notes:

1. Why can `df.loc[0:5]` and `df.iloc[0:5]` return different row counts?
2. How do you use a Python local variable inside `query()`?
3. How do you assign to a filtered subset correctly in one statement?
4. What is the difference between filtering and `where()` / `mask()`?
5. When is `.loc` a better semantic fit than `.iloc`?
6. What happens to the index after filtering?
7. Why can a correct row population still be wrong if the output columns are not explicit?
8. How would you test that a boolean filter returned exactly the expected business records?
9. When is `query()` easier to read than a mask, and when is a mask easier to debug?
10. How do you select one month across all countries in a MultiIndex?
11. How would you handle a legitimate zero-row result in a production function?
12. What performance claims about selection should be measured instead of assumed?

## 33. Final Mental Model

```text
ROWS + COLUMNS + INDEX
          ↓
   What is the selector basis?
          ↓
   ┌───────────────┬───────────────┐
   │ label / key   │ position      │
   │      ↓        │      ↓        │
   │     loc       │     iloc      │
   └───────────────┴───────────────┘
          ↓
 business condition?
          ↓
 boolean mask / query
          ↓
 exactly which rows and columns?
          ↓
 validate row count + schema + index
```

The core rules are simple, but they become powerful when used together:

1. **Use labels when meaning depends on identity.**
2. **Use positions when meaning depends on location/order.**
3. **Use boolean conditions for business rules.**
4. **Use `.loc[mask, "column"] = value` for explicit assignment.**
5. **Use `where`/`mask` when rows must stay in place.**
6. **Inspect the Index after filtering.**
7. **Treat empty results as a designed state, not an exception by default.**
8. **Measure selection performance on realistic data instead of relying on slogans.**

## 34. Connection to Topic 04 and Later Topics

Topic 03 gives you precise selection. The next topic, dtype design, makes those selected columns semantically and operationally correct. Later topics build on the same selection habit for cleaning, grouping, joins, reshaping, time series, method chaining, and scalable processing.

A useful dependency chain is:

```text
Topic 01: Series / DataFrame / Index
        ↓
Topic 02: safe reading / writing
        ↓
Topic 03: precise selection
        ↓
Topic 04: intentional dtypes
        ↓
cleaning → groupby → joins → reshaping → time → production pipelines
```

Selection is therefore not a small pandas syntax topic. It is one of the places where a Data Engineer converts an ambiguous source frame into a precisely defined working population.

## Appendix A — A Small End-to-End Selection Example

```python
import pandas as pd

df = pd.DataFrame({
    "order_id": [101, 102, 103, 104, 105],
    "customer_id": ["C1", "C2", None, "C4", "C5"],
    "country": ["IN", "US", "IN", "GB", "IN"],
    "status": ["paid", "pending", "paid", "paid", "cancelled"],
    "amount": [1200.0, 800.0, 2500.0, 1600.0, -20.0],
})

minimum_amount = 1000
allowed_countries = ["IN", "US", "GB"]

mask = (
    df["status"].eq("paid")
    & df["country"].isin(allowed_countries)
    & df["amount"].ge(minimum_amount)
    & df["customer_id"].notna()
)

selected = df.loc[
    mask,
    ["order_id", "customer_id", "country", "amount"],
]

assert "status" not in selected.columns
assert (selected["amount"] >= minimum_amount).all()
assert selected["country"].isin(allowed_countries).all()
assert selected["customer_id"].notna().all()

print(selected)
```

Expected business result: orders 101, 103, and 104 satisfy the filter. The important lesson is not the three-row answer; it is that the rule is visible, testable, and tied directly to the intended population and output schema.

## Appendix B — Practical Review Checklist

Before merging a selection step into a production pipeline, ask:

- What exactly is one row?
- What is the current Index and does it carry business meaning?
- Is this selection label-based, positional, or condition-based?
- Is the `.loc` slice end intentionally inclusive?
- Is the `.iloc` slice end intentionally exclusive?
- Are boolean conditions parenthesized and composed with `&`, `|`, `~`?
- Could nulls affect the predicate?
- Could the selected row count legitimately be zero?
- Are output columns explicit?
- Am I filtering rows or replacing values?
- If assigning, am I selecting rows and the target column in one `.loc` call?
- Does MultiIndex selection match the actual row grain?
- Is the DatetimeIndex suitable and sorted for the intended range selection?
- Have I written assertions for row count, schema, and business invariants?
- Have I measured performance on data sizes that resemble production?
