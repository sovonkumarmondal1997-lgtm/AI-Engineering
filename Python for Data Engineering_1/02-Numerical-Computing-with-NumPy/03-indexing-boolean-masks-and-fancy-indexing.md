# NumPy Indexing, Boolean Masks, and Fancy Indexing

> **Stage 2 — Python for Data Engineering**  
> **Module 2.2 — Numerical Computing with NumPy**  
> **Topic 03 — Indexing, Boolean Masks, and Fancy Indexing**  
> **Target:** NumPy 2.x

---

## Learning goals

By the end of this chapter, you should be able to:

- Select individual elements, rows, columns, and ranges from an `ndarray`.
- Work confidently with negative indices, slices, `...`, and multiple axes.
- Build Boolean masks for production-style filtering.
- Combine conditions correctly with `&`, `|`, and `~`.
- Explain why Python `and` and `or` do not work for element-wise NumPy conditions.
- Count and validate records using masks.
- Use integer-array/fancy indexing for arbitrary selection, lookup, and reordering.
- Find matching positions with `np.nonzero`, `np.flatnonzero`, and `np.argwhere`.
- Sort and rank data with `np.sort`, `np.argsort`, `np.lexsort`, and stable sorting.
- Use `np.argpartition` for top-k selection without fully sorting a large array.
- Use `np.unique`, `np.isin`, `np.intersect1d`, and `np.setdiff1d`.
- Use `np.searchsorted` for sorted lookup and range/bin assignment.
- Understand paired multidimensional fancy indexing and `np.ix_`.
- Predict whether a selection returns a view or copy.
- Implement deterministic "latest record per key" deduplication.
- Test NumPy selection logic against a small pure-Python reference implementation.
- Reason about memory and performance at million-row scale.

The central habit throughout this chapter is:

> **Before executing an indexing expression, predict its result shape, dtype when relevant, and whether it is a view or a copy.**

---

# 1. Introduction: indexing is data selection

NumPy indexing answers a simple question:

> **Which positions in this array do I want?**

That sounds basic, but data engineers repeatedly solve exactly this problem:

- keep only paid orders,
- remove invalid sensor readings,
- select the latest version of each CDC record,
- take the top 100 transactions,
- map numeric status codes to business labels,
- select a set of rows and columns,
- keep only records belonging to an allowed ID set,
- assign records to price bands,
- prepare a batch for downstream ML or analytics.

In SQL, these ideas appear as:

```sql
WHERE
ORDER BY
LIMIT
DISTINCT
IN
```

NumPy has different syntax, but the concepts are related.

| SQL idea | NumPy pattern | Typical purpose |
|---|---|---|
| `WHERE` | Boolean mask | Filter records |
| `ORDER BY` | `sort`, `argsort`, `lexsort` | Order data |
| `LIMIT` | `argpartition` + selection | Top-k |
| `DISTINCT` | `unique` | Unique values / deduplication support |
| `IN` | `isin` | Membership testing |
| Range lookup | `searchsorted` | Binning / interval lookup |

These are **conceptual correspondences**, not replacements for a SQL engine. SQL databases can optimize selection using indexes, statistics, query planners, distributed execution, and storage-level pruning. NumPy is an in-memory numerical array library.

The engineering lesson is still important:

> Large data systems become easier to reason about when you understand the mechanics of selection.

---

# 2. Refresher: the NumPy array mental model

Topic 01 introduced the `ndarray`. Topic 02 introduced vectorized operations and broadcasting. We only need a short refresher here.

A NumPy array can be thought of as:

```text
ndarray
├── values
├── shape
├── dtype
└── axes / positions
```

For example:

```python
import numpy as np

a = np.array(
    [
        [10, 20, 30],
        [40, 50, 60],
    ],
    dtype=np.int32,
)

print(a.shape)
print(a.dtype)
```

Output:

```text
(2, 3)
int32
```

There are 2 rows and 3 columns.

NumPy uses **zero-based indexing**:

```text
column:   0    1    2
          ↓    ↓    ↓
row 0    10   20   30
row 1    40   50   60
```

You can select by position, by range, by condition, or by another array of integer positions.

---

# 3. The three main selection mechanisms

NumPy gives us three major selection styles.

```text
1. Basic indexing / slicing
2. Boolean indexing
3. Integer-array (fancy) indexing
```

A useful first comparison:

| Mechanism | Example | Natural question | Typical result behavior |
|---|---|---|---|
| Basic indexing | `a[2]` | "Give me this position." | Scalar or lower-dimensional result |
| Slicing | `a[1:5]` | "Give me this range." | Usually a view |
| Boolean indexing | `a[a > 100]` | "Give me values satisfying this condition." | Copy |
| Fancy indexing | `a[[3, 0, 7]]` | "Give me exactly these positions." | Copy |

The view/copy details become critical later. For now, remember:

> **Basic slicing generally gives a view; Boolean and fancy indexing give copies.**

---

# 4. Basic indexing

## 4.1 One-dimensional indexing

Start with the smallest useful example:

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50])

print(a[0])
print(a[2])
print(a[-1])
```

Output:

```text
10
30
50
```

### How indexing works

```text
index:   0    1    2    3    4
value:  10   20   30   40   50
         ↑                   ↑
        a[0]                a[-1]
```

Negative indices count from the end:

```text
a[-1] → last element
a[-2] → second-to-last
```

This is useful when working with "latest" or "previous" positions in already ordered arrays.

### Common mistake

Trying to use an out-of-range index:

```python
a[10]
```

raises:

```text
IndexError
```

That is generally helpful: NumPy is telling you that the requested position does not exist.

---

# 5. Slicing

A slice has the general form:

```python
a[start:stop:step]
```

The `stop` boundary is exclusive.

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50, 60])

print(a[1:4])
print(a[:3])
print(a[3:])
print(a[::2])
print(a[::-1])
```

Output:

```text
[20 30 40]
[10 20 30]
[40 50 60]
[10 30 50]
[60 50 40 30 20 10]
```

### Read slices as a range

For:

```python
a[1:4]
```

read it as:

```text
start at 1
stop before 4
step by 1
```

So positions `1, 2, 3` are selected.

### Useful slice patterns

```python
a[:]       # all values
a[1:]      # from index 1 to the end
a[:-1]     # everything except the last value
a[::2]     # every second value
a[::-1]    # reverse
```

---

# 6. Multidimensional indexing

For a 2-D array, the comma separates axis selections.

```python
import numpy as np

a = np.array(
    [
        [10, 20, 30, 40],
        [50, 60, 70, 80],
        [90, 100, 110, 120],
    ]
)

print(a[1, 2])
print(a[0, :])
print(a[:, 1])
print(a[1:3, 2:4])
```

Output:

```text
70
[10 20 30 40]
[ 20  60 100]
[[ 70  80]
 [110 120]]
```

The axis interpretation is:

```text
a[row, column]
```

So:

```python
a[1, 2]
```

means:

```text
row 1, column 2
```

---

## 6.1 Selecting rows

```python
a[0, :]
```

means:

> Take row 0 and all columns.

The shorter form is:

```python
a[0]
```

Both select the first row.

---

## 6.2 Selecting columns

```python
a[:, 1]
```

means:

> Take every row, column 1.

This is a common pattern when an array represents a matrix of features:

```text
rows    = records
columns = features
```

For a Data Engineering pipeline, selecting a single numeric feature column might look like:

```python
temperature = sensor_matrix[:, 2]
```

---

# 7. The ellipsis `...`

The ellipsis means:

> "Fill in all unspecified axes."

For example:

```python
import numpy as np

a = np.arange(24).reshape(2, 3, 4)

last_feature = a[..., -1]

print(a.shape)
print(last_feature.shape)
print(last_feature)
```

Output:

```text
(2, 3, 4)
(2, 3)
[[ 3  7 11]
 [15 19 23]]
```

The expression:

```python
a[..., -1]
```

is equivalent here to:

```python
a[:, :, -1]
```

Why is this useful?

Suppose your data is:

```text
(days, stores, products)
```

and you always want the final product position:

```python
sales[..., -1]
```

You do not have to hard-code how many leading axes exist.

---

# 8. Three-dimensional indexing

Consider:

```python
sales.shape == (365, 50, 200)
```

Interpret the axes as:

```text
days × stores × products
```

Examples:

```python
sales[10, :, 25]   # one day, every store, one product
sales[:, 4, :]     # every day, one store, every product
sales[..., 25]     # every day, every store, one product
```

Predict before running:

```text
sales[10, :, 25].shape
→ (50,)

sales[:, 4, :].shape
→ (365, 200)

sales[..., 25].shape
→ (365, 50)
```

This is the first major engineering habit:

> **Do not guess what an indexing operation returns. Predict the shape first.**

---

# 9. Slicing multidimensional arrays

Slices can be applied independently to different axes.

```python
import numpy as np

a = np.arange(30).reshape(5, 6)

print(a[:, 0])
print(a[:, 1:4])
print(a[::2, ::-1])
```

The expression:

```python
a[:, 1:4]
```

means:

```text
all rows
columns 1, 2, 3
```

The expression:

```python
a[::2, ::-1]
```

means:

```text
every second row
all columns in reverse order
```

### Prediction exercise

Before executing:

```python
a = np.arange(24).reshape(6, 4)
result = a[1:5:2, 1:4]
```

write:

```text
Result shape:
View or copy:
Why:
```

The answer can be checked after you reason about it.

---

# 10. Slicing and views

Basic slicing is important not only because it selects data, but because it can share memory with the original array.

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50])

b = a[1:4]

print(b)
print(np.shares_memory(a, b))
```

Output:

```text
[20 30 40]
True
```

That means `b` is typically a **view** of `a`.

Changing the view can therefore change the source:

```python
b[0] = 999

print(a)
```

Output:

```text
[ 10 999  30  40  50]
```

This behavior becomes a major production concern later, but it is useful to know now.

---

# 11. Boolean masks

## 11.1 What is a Boolean mask?

A Boolean mask is an array of `True` and `False` values describing which positions satisfy a condition.

```python
import numpy as np

a = np.array([10, 150, 20, 200, 30])

mask = a > 100

print(mask)
print(a[mask])
```

Output:

```text
[False  True False  True False]
[150 200]
```

Visual model:

```text
values:  10   150   20   200   30
mask:     F    T     F    T     F
                ↓         ↓
result:        150       200
```

The process is:

```text
condition
    ↓
Boolean array
    ↓
selection
```

This is NumPy's most important filtering mechanism.

---

# 12. Comparisons create Boolean arrays

Comparisons are element-wise:

```python
import numpy as np

a = np.array([10, 20, 30, 40])

print(a > 20)
print(a == 30)
print(a != 10)
print(a <= 20)
```

Output:

```text
[False False  True  True]
[False False  True False]
[False  True  True  True]
[ True  True False False]
```

This is the bridge between vectorization and indexing:

```text
Topic 02:
vectorized comparison
        ↓
Boolean array

Topic 03:
Boolean array
        ↓
selection
```

---

# 13. Combining Boolean conditions

NumPy uses element-wise Boolean operators:

```text
&
|
~
```

They mean:

```text
&  AND
|  OR
~  NOT
```

## 13.1 AND with `&`

```python
import numpy as np

a = np.array([5, 20, 40, 80, 120])

mask = (a > 10) & (a < 100)

print(mask)
print(a[mask])
```

Output:

```text
[False  True  True  True False]
[20 40 80]
```

Every element must satisfy both conditions.

---

## 13.2 OR with `|`

```python
a = np.array([1, 3, 5, 7, 9])

mask = (a == 1) | (a == 7)

print(a[mask])
```

Output:

```text
[1 7]
```

---

## 13.3 NOT with `~`

```python
a = np.array([0, 1, 0, 1])

mask = ~(a == 0)

print(mask)
print(a[mask])
```

Output:

```text
[False  True False  True]
[1 1]
```

---

# 14. Why parentheses matter

Write:

```python
(a > 10) & (a < 100)
```

rather than:

```python
a > 10 & a < 100
```

The second form can be interpreted according to Python's operator precedence in a way you did not intend.

The safest engineering rule is:

> **Put parentheses around each comparison before using `&`, `|`, or `~`.**

This makes intent obvious and prevents precedence bugs.

---

# 15. Why `and` and `or` fail

A common beginner mistake is:

```python
(a > 10) and (a < 100)
```

This is not the right operation for arrays.

Python's:

```text
and
or
not
```

operate using scalar truth semantics. NumPy needs element-by-element logic.

Use:

```python
(a > 10) & (a < 100)
```

instead.

Conceptually:

```text
Python `and`
→ "Is this entire object truthy?"

NumPy `&`
→ "Compare these Boolean elements pair-by-pair."
```

If you try:

```python
import numpy as np

a = np.array([10, 20, 30])

a > 10 and a < 30
```

NumPy raises an error such as:

```text
ValueError: The truth value of an array with more than one element is ambiguous.
```

The problem is that an array has multiple Boolean values. Python cannot reduce them to one scalar truth value automatically.

Use:

```python
(a > 10) & (a < 30)
```

instead.

Likewise:

```text
and → &
or  → |
not → ~
```

---

# 16. A production filtering pattern

Suppose we have:

```python
import numpy as np

order_id = np.array([101, 102, 103, 104, 105])
status_code = np.array([1, 2, 1, 3, 1])
amount_cents = np.array([5000, 15000, 22000, 8000, 50000])
```

Assume:

```text
1 = pending
2 = paid
3 = cancelled
```

Filter paid orders over 10,000 cents:

```python
mask = (status_code == 2) & (amount_cents > 10_000)

print(mask)
print(order_id[mask])
print(amount_cents[mask])
```

The useful pattern is:

```text
build one Boolean condition
          ↓
apply it to every aligned column
```

Because these arrays are aligned by row, using the same mask keeps the selected records consistent.

---

# 17. Counting and testing masks

Boolean arrays can also be treated as 0/1 values for common counting operations.

```python
import numpy as np

mask = np.array([True, False, True, True, False])

print(mask.sum())
print(mask.mean())
print(np.any(mask))
print(np.all(mask))
print(np.count_nonzero(mask))
```

Output:

```text
3
0.6
True
False
3
```

Why does `mask.mean()` produce `0.6`?

Because conceptually:

```text
True  → 1
False → 0
```

So:

```text
(1 + 0 + 1 + 1 + 0) / 5
= 3 / 5
= 0.6
```

This is useful for quality rates:

```python
quality_mask = np.array([True, True, True, False, True])

pass_rate = quality_mask.mean()
```

The result is the proportion passing the rule.

---

## 17.1 Common mask questions

### How many records are invalid?

```python
invalid_count = np.count_nonzero(~valid_mask)
```

### Does at least one bad record exist?

```python
has_bad_records = np.any(~valid_mask)
```

### Did every record pass?

```python
all_valid = np.all(valid_mask)
```

### What fraction passed?

```python
pass_rate = valid_mask.mean()
```

These are basic building blocks for data-quality pipelines.

---

# 18. Boolean masks and aligned columns

In a column-oriented in-memory design, you may have:

```python
order_id
customer_id
amount_cents
status_code
```

with all arrays having the same length.

Build one mask:

```python
mask = (
    (status_code == 2)
    & (amount_cents > 10_000)
)
```

Then apply it consistently:

```python
selected_order_id = order_id[mask]
selected_customer_id = customer_id[mask]
selected_amount = amount_cents[mask]
```

A common engineering mistake is applying different filters independently to aligned arrays. That can destroy row alignment.

Think of the mask as the record-selection decision:

```text
row 0 → keep?
row 1 → keep?
row 2 → keep?
...
```

Use the same mask for every column belonging to those rows.

---

# 19. Fancy indexing: selecting arbitrary positions

Boolean masks answer:

> Which rows satisfy a condition?

Fancy indexing answers:

> Which exact integer positions do I want?

Example:

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50, 60])

positions = np.array([3, 0, 5])

result = a[positions]

print(result)
print(result.shape)
```

Output:

```text
[40 10 60]
(3,)
```

The order in `positions` becomes the order of the result.

```text
positions = [3, 0, 5]

a[3] → 40
a[0] → 10
a[5] → 60
```

That makes fancy indexing useful for:

- arbitrary row selection,
- reordering,
- lookup-table operations,
- sampling by known positions.

---

# 20. Fancy indexing is a copy

Unlike basic slicing, integer-array indexing returns a copy.

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50])
b = a[[1, 3]]

print(np.shares_memory(a, b))
```

Output:

```text
False
```

Changing `b` does not change `a`:

```python
b[0] = 999

print(a)
print(b)
```

Output:

```text
[10 20 30 40 50]
[999  40]
```

This is useful for safety, but it also means the selected result consumes separate memory.

---

# 21. Lookup tables

A powerful pattern is:

```python
lookup[code_array]
```

Suppose status codes are:

```python
status_code = np.array([0, 2, 1, 2, 0])
```

and the lookup table stores labels:

```python
labels = np.array(["pending", "paid", "cancelled"])
```

Then:

```python
result = labels[status_code]

print(result)
```

Output:

```text
['pending' 'cancelled' 'paid' 'cancelled' 'pending']
```

The numeric code acts as a position.

A similar pattern is useful for rates:

```python
tax_rate_by_country = np.array([
    0.00,
    0.05,
    0.12,
    0.18,
])

country_code = np.array([3, 1, 3, 2])

tax_rate = tax_rate_by_country[country_code]
```

This combines the ideas from Topic 02:

```text
integer code
    ↓
fancy indexing
    ↓
per-record rate
    ↓
vectorized arithmetic
```

### Production warning

Lookup codes must be valid indices.

For example, if the lookup has length 4, a code of `7` is invalid. Validate code ranges before indexing.

---

# 22. `np.take`

`np.take` is another explicit way to select by integer positions.

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50])

positions = np.array([4, 1, 1, 0])

print(np.take(a, positions))
```

Output:

```text
[50 20 20 10]
```

This is conceptually similar to:

```python
a[positions]
```

For multidimensional arrays, `axis=` makes the intended axis explicit.

```python
matrix = np.arange(12).reshape(3, 4)

print(np.take(matrix, [0, 2], axis=0))
```

Output:

```text
[[ 0  1  2  3]
 [ 8  9 10 11]]
```

Use `np.take` when explicit axis-oriented selection improves readability.

---

# 23. Finding matching positions

Sometimes you do not want the selected values yet. You want the **positions** where a condition is true.

NumPy provides:

```python
np.nonzero
np.flatnonzero
np.argwhere
```

These are related, but they return positions in different forms.

---

# 24. `np.nonzero`

For a one-dimensional mask:

```python
import numpy as np

a = np.array([10, 20, 30, 40])

mask = a > 20

positions = np.nonzero(mask)

print(positions)
```

Output:

```text
(array([2, 3]),)
```

For multidimensional arrays, `np.nonzero` returns one index array per axis.

```python
a = np.array(
    [
        [0, 5, 0],
        [7, 0, 9],
    ]
)

positions = np.nonzero(a > 0)

print(positions)
```

Output:

```text
(array([0, 1, 1]), array([1, 0, 2]))
```

This means:

```text
(0, 1)
(1, 0)
(1, 2)
```

---

# 25. `np.flatnonzero`

`np.flatnonzero` returns the indices into a flattened version.

```python
import numpy as np

a = np.array(
    [
        [0, 5, 0],
        [7, 0, 9],
    ]
)

positions = np.flatnonzero(a > 0)

print(positions)
```

Output:

```text
[1 3 5]
```

Flattened positions correspond to:

```text
flat array:
index: 0 1 2 3 4 5
value: 0 5 0 7 0 9
          ↑   ↑   ↑
          1   3   5
```

Use it when a flat positional index is exactly what the downstream algorithm needs.

---

# 26. `np.argwhere`

`np.argwhere` returns coordinate rows.

```python
import numpy as np

a = np.array(
    [
        [0, 5, 0],
        [7, 0, 9],
    ]
)

coordinates = np.argwhere(a > 0)

print(coordinates)
```

Output:

```text
[[0 1]
 [1 0]
 [1 2]]
```

Each row is a coordinate:

```text
[row, column]
```

This is often easier to read when debugging multidimensional selections.

---

## 26.1 Position-finding comparison

| Function | Typical output | Best mental model |
|---|---|---|
| `np.nonzero(mask)` | one index array per axis | "Give me coordinates split by axis." |
| `np.flatnonzero(mask)` | one flat index array | "Give me positions in flattened order." |
| `np.argwhere(mask)` | rows of coordinates | "Give me explicit coordinates." |

---

# 27. Sorting with `np.sort`

`np.sort` returns sorted values.

```python
import numpy as np

amount = np.array([500, 100, 900, 300])

sorted_amount = np.sort(amount)

print(sorted_amount)
print(amount)
```

Output:

```text
[100 300 500 900]
[500 100 900 300]
```

`np.sort` does not rearrange the original array in place.

For a 2-D array, `axis=` controls the direction of sorting:

```python
matrix = np.array(
    [
        [30, 10, 20],
        [60, 40, 50],
    ]
)

print(np.sort(matrix, axis=1))
```

Output:

```text
[[10 20 30]
 [40 50 60]]
```

---

# 28. `np.argsort`: sorted positions instead of sorted values

`np.argsort` returns the indices that would sort an array.

```python
import numpy as np

amount = np.array([500, 100, 900, 300])

order = np.argsort(amount)

print(order)
print(amount[order])
```

Output:

```text
[1 3 0 2]
[100 300 500 900]
```

This distinction is extremely important.

```text
np.sort
→ sorted values

np.argsort
→ positions that produce sorted values
```

Why are positions useful?

Suppose several columns are aligned:

```python
order_id = np.array([101, 102, 103, 104])
amount = np.array([500, 100, 900, 300])
```

To sort every aligned column by amount:

```python
order = np.argsort(amount)

sorted_order_id = order_id[order]
sorted_amount = amount[order]

print(sorted_order_id)
print(sorted_amount)
```

Output:

```text
[102 104 101 103]
[100 300 500 900]
```

The same positional order is applied to every aligned column.

---

# 29. Stable sorting

A **stable sort** preserves the relative order of records that have equal sort keys.

This matters whenever ties exist.

```python
import numpy as np

amount = np.array([100, 50, 100, 50])
record_id = np.array([1, 2, 3, 4])

order = np.argsort(amount, kind="stable")

print(record_id[order])
print(amount[order])
```

Output:

```text
[2 4 1 3]
[50 50 100 100]
```

Notice the original relative order of equal amounts is preserved:

```text
50: record 2 before record 4
100: record 1 before record 3
```

### Why this matters

Data pipelines often have ties:

- two records share the same timestamp,
- multiple transactions have the same amount,
- several records have the same priority.

Stable ordering can make downstream behavior deterministic.

This becomes especially important when sorting before deduplication.

---

# 30. Multi-key sorting with `np.lexsort`

Many data-engineering problems require more than one sort key.

Suppose we want:

```text
primary key   = customer_id
secondary key = updated_at
```

Example:

```python
import numpy as np

customer_id = np.array([20, 10, 20, 10])
updated_at = np.array([300, 100, 200, 300])

order = np.lexsort((updated_at, customer_id))

print(order)
print(customer_id[order])
print(updated_at[order])
```

Output:

```text
[1 3 2 0]
[10 10 20 20]
[100 300 200 300]
```

The important rule is:

> **`np.lexsort` uses the last key as the primary sort key.**

In:

```python
np.lexsort((updated_at, customer_id))
```

`customer_id` is primary and `updated_at` breaks ties.

Think:

```text
keys = (secondary, primary)
```

This detail is easy to reverse accidentally.

---

# 31. `lexsort` and deterministic ordering

For a production pipeline, you may need:

```text
primary: order_id ascending
secondary: updated_at descending
tertiary: ingestion_sequence ascending
```

The exact key transformation depends on the desired direction, but the engineering idea is:

```text
business key
    ↓
timestamp
    ↓
tie-breaker
    ↓
deterministic row order
```

That is the foundation for "latest record per key."

Without deterministic ordering, "keep one record" can become "keep whichever record happened to appear first after an unstable or accidental ordering."

---

# 32. Top-k selection with `np.argpartition`

Suppose you have ten million transaction amounts but need only the top 100.

A full sort asks NumPy to order all ten million values.

But your actual question is only:

> Which 100 values are largest?

`np.argpartition` is designed for this kind of partial selection.

```python
import numpy as np

rng = np.random.default_rng(42)
amount = rng.integers(0, 1_000_000, size=20)
k = 5

candidate_positions = np.argpartition(amount, -k)[-k:]
top_order = candidate_positions[np.argsort(amount[candidate_positions])[::-1]]

print(amount[top_order])
```

The two-stage pattern is:

```text
large array
    ↓
argpartition
    ↓
top-k candidates
    ↓
sort only k candidates
    ↓
ordered top-k
```

Visualized:

```text
10,000,000 values
        ↓
   argpartition
        ↓
  100 candidates
        ↓
 sort only 100
        ↓
  ordered top 100
```

### Important detail

The result of `argpartition` is **not fully sorted**.

It guarantees partitioning around the requested position, not complete ordering of every element.

Therefore, if you need ranked top-k output:

```python
candidates = np.argpartition(amount, -k)[-k:]
top_k = candidates[np.argsort(amount[candidates])[::-1]]
```

This is often a better fit than a complete sort when only a small top-k subset matters.

---

# 33. `np.unique`

`np.unique` finds unique values.

```python
import numpy as np

status = np.array([2, 1, 2, 3, 1, 2])

print(np.unique(status))
```

Output:

```text
[1 2 3]
```

It has several useful return options.

## 33.1 `return_counts=True`

```python
values, counts = np.unique(
    status,
    return_counts=True,
)

print(values)
print(counts)
```

Output:

```text
[1 2 3]
[2 3 1]
```

This is useful for frequency analysis.

## 33.2 `return_index=True`

```python
values, first_positions = np.unique(
    status,
    return_index=True,
)

print(values)
print(first_positions)
```

The returned positions identify where each unique value was first selected according to NumPy's documented behavior for that operation.

This becomes useful for deduplication once we deliberately establish the desired ordering first.

## 33.3 `return_inverse=True`

```python
customer = np.array(["A", "B", "A", "C", "B", "A"])

values, inverse = np.unique(
    customer,
    return_inverse=True,
)

print(values)
print(inverse)
```

A possible output is:

```text
['A' 'B' 'C']
[0 1 0 2 1 0]
```

The `inverse` array maps each original value to a unique group code.

Conceptually:

```text
A → 0
B → 1
C → 2
```

This is useful when a later algorithm wants compact integer group identifiers.

---

# 34. `np.isin`

`np.isin` performs element-wise membership testing.

```python
import numpy as np

status = np.array([1, 2, 3, 4, 2])

allowed = np.array([1, 3])

mask = np.isin(status, allowed)

print(mask)
print(status[mask])
```

Output:

```text
[ True False  True False False]
[1 3]
```

Common Data Engineering uses:

- allowed status codes,
- blocked IDs,
- selected customer IDs,
- category filters,
- reference-list validation.

Think of it as a vectorized membership mask.

---

# 35. `np.intersect1d`

`np.intersect1d` returns values common to both arrays.

```python
import numpy as np

left = np.array([1, 2, 3, 4])
right = np.array([3, 4, 5, 6])

print(np.intersect1d(left, right))
```

Output:

```text
[3 4]
```

Conceptually:

```text
left  = {1, 2, 3, 4}
right = {3, 4, 5, 6}

intersection = {3, 4}
```

Use this for set-style comparisons between ID collections or category domains.

---

# 36. `np.setdiff1d`

`np.setdiff1d(a, b)` returns values present in `a` but not in `b`.

```python
import numpy as np

source_ids = np.array([1, 2, 3, 4, 5])
known_ids = np.array([2, 4])

print(np.setdiff1d(source_ids, known_ids))
```

Output:

```text
[1 3 5]
```

This is useful for questions such as:

```text
Which incoming IDs are not present in the reference set?
```

---

# 37. Set-operation comparison

| Function | Question |
|---|---|
| `unique(a)` | What distinct values exist? |
| `isin(a, values)` | Is each element a member of this set? |
| `intersect1d(a, b)` | Which values exist in both? |
| `setdiff1d(a, b)` | Which values exist in `a` but not `b`? |

These functions are convenient, but remember that each has its own ordering, duplicate, and memory behavior. Read the function contract when those details matter to a production pipeline.

---

# 38. `np.searchsorted`

`np.searchsorted` answers:

> Where should a value be inserted into a sorted array to keep it sorted?

Start simply:

```python
import numpy as np

edges = np.array([10, 20, 30, 40])

print(np.searchsorted(edges, 25))
```

Output:

```text
2
```

The value `25` belongs between:

```text
20 and 30
```

So position `2` is the insertion point.

---

## 38.1 `side="left"` and `side="right"`

For values exactly equal to an edge:

```python
edges = np.array([10, 20, 30, 40])

print(np.searchsorted(edges, 20, side="left"))
print(np.searchsorted(edges, 20, side="right"))
```

Output:

```text
1
2
```

The distinction matters for interval boundaries.

---

# 39. Price-band classification with `searchsorted`

Suppose business rules define:

```text
0
1000
5000
10000
```

as band boundaries.

```python
import numpy as np

edges = np.array([0, 1_000, 5_000, 10_000])

amount = np.array([500, 1_000, 2_000, 7_000, 15_000])

band = np.searchsorted(edges, amount, side="right") - 1

print(band)
```

The important idea is not the exact business definition but the pattern:

```text
sorted boundaries
       ↓
searchsorted
       ↓
integer interval/band
```

This is useful for:

- price bands,
- latency buckets,
- age ranges,
- score ranges,
- risk bands,
- metric thresholds.

### Requirement

The array used for binary-search insertion must be sorted according to the search order. Feeding unsorted boundaries can produce incorrect classifications.

---

# 40. Searchsorted as a vectorized lookup tool

Imagine you have:

```text
thresholds:
[100, 500, 1000, 5000]
```

and thousands of incoming values.

A Python loop might ask one value at a time:

```text
Which interval contains this value?
```

`searchsorted` lets NumPy perform the search for the whole vector:

```python
positions = np.searchsorted(thresholds, values)
```

This is one reason it is useful in batch-processing code.

---

# 41. Multidimensional fancy indexing

This is where indexing becomes more subtle.

Consider:

```python
import numpy as np

a = np.array(
    [
        [10, 20, 30, 40],
        [50, 60, 70, 80],
        [90, 100, 110, 120],
    ]
)

rows = np.array([0, 2])
cols = np.array([1, 3])

print(a[rows, cols])
```

Output:

```text
[20 120]
```

Why?

Because paired integer arrays select coordinate pairs:

```text
(rows[0], cols[0]) → (0, 1) → 20
(rows[1], cols[1]) → (2, 3) → 120
```

Visual:

```text
rows = [0, 2]
cols = [1, 3]

a[rows, cols]

→ (a[0,1], a[2,3])
→ (20, 120)
```

This is **paired coordinate selection**.

It is not:

> "Give me every combination of these rows and columns."

For that, you need broadcasting of index arrays or `np.ix_`.

---

# 42. Combining fancy indexing with broadcasting

Now consider:

```python
rows = np.array([0, 2])
cols = np.array([1, 3])

result = a[rows[:, None], cols]

print(result)
```

Output:

```text
[[ 20  40]
 [100 120]]
```

Why?

First:

```python
rows[:, None]
```

changes:

```text
rows.shape
→ (2,)

rows[:, None].shape
→ (2, 1)
```

Then:

```text
(2, 1)
(2,)
```

broadcast to:

```text
(2, 2)
```

The selected coordinate combinations are:

```text
(0,1) (0,3)
(2,1) (2,3)
```

Visual:

```text
rows[:, None]      → (2, 1)
cols               → (2,)

broadcast index grid:

(0,1)  (0,3)
(2,1)  (2,3)

result shape → (2, 2)
```

This is directly connected to Topic 02's broadcasting rules.

---

# 43. `np.ix_`

`np.ix_` provides a clear way to express a Cartesian product of row and column selections.

```python
import numpy as np

a = np.array(
    [
        [10, 20, 30, 40],
        [50, 60, 70, 80],
        [90, 100, 110, 120],
    ]
)

rows = np.array([0, 2])
cols = np.array([1, 3])

result = a[np.ix_(rows, cols)]

print(result)
```

Output:

```text
[[ 20  40]
 [100 120]]
```

Compare:

```python
a[rows, cols]
```

which means paired coordinates:

```text
(0, 1)
(2, 3)
```

versus:

```python
a[np.ix_(rows, cols)]
```

which means all row/column combinations:

```text
(0,1)  (0,3)
(2,1)  (2,3)
```

### Mental rule

```text
a[rows, cols]
→ pair positions

a[rows[:, None], cols]
→ broadcast combinations

a[np.ix_(rows, cols)]
→ explicit Cartesian-product selection
```

---

# 44. View vs copy: the rule to remember

At this point the central rules are:

```text
Basic slicing
→ generally a view

Boolean indexing
→ copy

Fancy integer indexing
→ copy
```

Prove it rather than memorizing it.

---

## 44.1 Basic slicing

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50])

b = a[1:4]

print(np.shares_memory(a, b))
```

Output:

```text
True
```

---

## 44.2 Boolean indexing

```python
b = a[a > 20]

print(np.shares_memory(a, b))
```

Output:

```text
False
```

---

## 44.3 Fancy indexing

```python
b = a[[1, 3]]

print(np.shares_memory(a, b))
```

Output:

```text
False
```

### Why engineers care

A view can be dangerous because a mutation can affect the source.

A copy can be expensive because it needs new storage.

So every selection has two questions:

```text
What records did I select?
How was that result represented in memory?
```

---

# 45. The chained-indexing bug

This is one of the most important bugs in NumPy selection code.

Consider:

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50])
mask = a > 20

a[mask][0] = 999

print(a)
```

Output:

```text
[10 20 30 40 50]
```

Why did nothing happen?

Break it into steps:

```text
a[mask]
    ↓
new selected array (copy)
    ↓
[0]
    ↓
modify that copy
    ↓
original `a` unchanged
```

The problematic expression is:

```python
a[mask][0] = 999
```

The first selection:

```python
a[mask]
```

creates a copy.

The assignment then changes the copy.

---

# 46. Correct masked assignment

Direct masked assignment is different:

```python
a = np.array([10, 20, 30, 40, 50])

mask = a > 20

a[mask] = 0

print(a)
```

Output:

```text
[10 20  0  0  0]
```

The important distinction is:

```text
retrieval:

selected = a[mask]
→ selected is a copy

direct assignment:

a[mask] = 0
→ assignment is applied to the original array
```

Do not summarize this incorrectly as:

> "Boolean indexing is always a no-op."

It is not. The selection result is a copy, but NumPy provides specialized assignment semantics for direct indexed assignment.

---

# 47. Prediction-first practice

Before executing each expression, write:

```text
Result shape:
View or copy:
Why:
```

Use:

```python
import numpy as np

a = np.arange(12).reshape(3, 4)
rows = np.array([0, 2])
cols = np.array([1, 3])
```

Predict these:

```python
a[1:3]
a[a > 5]
a[[1, 2]]
a[:, 0]
a[..., -1]
a[rows, cols]
a[rows[:, None], cols]
a[np.ix_(rows, cols)]
```

Do not run the code first.

The goal is not speed. The goal is developing a reliable mental simulator of NumPy.

---

# 48. Production pattern: latest record per key

This is one of the most valuable patterns in this topic.

Imagine order records arriving multiple times:

```text
order_id
customer_id
updated_at
status_code
amount_cents
```

Example:

```python
import numpy as np

order_id = np.array([101, 102, 101, 103, 102, 101])
customer_id = np.array([10, 20, 10, 30, 20, 10])
updated_at = np.array([100, 200, 300, 150, 400, 350])
status_code = np.array([1, 1, 2, 1, 2, 3])
amount_cents = np.array([5000, 7000, 5500, 9000, 7200, 5600])
```

`order_id=101` occurs three times:

```text
101 @ 100
101 @ 300
101 @ 350
```

We want:

```text
101 @ 350
```

not an arbitrary version.

---

# 49. Deduplication step 1: define the desired ordering

We want records ordered by:

```text
order_id ascending
updated_at descending
```

There is an important complication:

`np.lexsort` sorts ascending by its keys. A simple way to request descending timestamps is to transform the timestamp key.

For non-negative integer timestamps:

```python
order = np.lexsort((-updated_at, order_id))
```

The last key is primary:

```text
primary   = order_id
secondary = -updated_at
```

So within each order, later timestamps come first.

Let's inspect:

```python
order = np.lexsort((-updated_at, order_id))

print(order_id[order])
print(updated_at[order])
```

The values will be grouped by `order_id`, with newest records first within each group.

---

# 50. Deduplication step 2: find the first position of each key

After the deliberate sort:

```text
same key
   ↓
newest first
   ↓
first row for each key = desired row
```

Now:

```python
sorted_order_id = order_id[order]

_, first_positions = np.unique(
    sorted_order_id,
    return_index=True,
)
```

Because `sorted_order_id` is already ordered by our business rule, the first occurrence of each key is the record we want.

But note something important:

> `first_positions` are positions inside the **sorted order**, not positions in the original arrays.

So the original row positions are:

```python
latest_positions = order[first_positions]
```

Now use them to select every aligned column:

```python
latest_order_id = order_id[latest_positions]
latest_customer_id = customer_id[latest_positions]
latest_updated_at = updated_at[latest_positions]
latest_status_code = status_code[latest_positions]
latest_amount_cents = amount_cents[latest_positions]
```

---

# 51. Deduplication pattern visualized

```text
duplicate records
       ↓
lexsort by key + timestamp
       ↓
same key grouped together
       ↓
latest record placed first
       ↓
unique(..., return_index=True)
       ↓
first position per key
       ↓
map back to original row positions
       ↓
select aligned columns
       ↓
latest record per key
```

The critical idea is:

> **`unique` does not know what "latest" means. You define that meaning through ordering first.**

---

# 52. Complete latest-record example

```python
import numpy as np

order_id = np.array([101, 102, 101, 103, 102, 101])
customer_id = np.array([10, 20, 10, 30, 20, 10])
updated_at = np.array([100, 200, 300, 150, 400, 350])
status_code = np.array([1, 1, 2, 1, 2, 3])
amount_cents = np.array([5000, 7000, 5500, 9000, 7200, 5600])

# 1. Sort by order_id ascending, then updated_at descending.
order = np.lexsort((-updated_at, order_id))

# 2. Work with order IDs in the deliberate sort order.
sorted_order_id = order_id[order]

# 3. Find the first row of each order ID.
_, first_positions = np.unique(
    sorted_order_id,
    return_index=True,
)

# 4. Convert sorted positions back to original row positions.
latest_positions = order[first_positions]

# 5. Apply the selected original positions to every aligned column.
latest_order_id = order_id[latest_positions]
latest_customer_id = customer_id[latest_positions]
latest_updated_at = updated_at[latest_positions]
latest_status_code = status_code[latest_positions]
latest_amount_cents = amount_cents[latest_positions]

print(latest_order_id)
print(latest_updated_at)
print(latest_status_code)
print(latest_amount_cents)
```

The exact row order of the output follows the ordering produced by the sort. The essential correctness property is:

```text
one output row per order_id
and
the timestamp is the latest timestamp for that order
```

---

# 53. Ties and deterministic deduplication

What if two records have:

```text
order_id = 101
updated_at = 350
```

at the same timestamp?

Then "latest" is not enough to identify a unique record.

Production systems need a tie-breaker, for example:

```text
ingestion_sequence
source_event_id
version_number
```

A deterministic ordering could be:

```text
order_id
updated_at
ingestion_sequence
```

The exact key order and ascending/descending direction should reflect the business rule.

Engineering rule:

> **If a deduplication rule can encounter ties, define the tie-breaker explicitly.**

Otherwise, a correct-looking pipeline can produce inconsistent results across runs or upstream arrival orders.

---

# 54. Preserving aligned columns

NumPy does not know that:

```python
order_id
customer_id
updated_at
amount_cents
```

belong together conceptually.

That relationship exists because you keep them aligned by position.

So after computing:

```python
latest_positions
```

apply the same positional selection to every aligned array:

```python
order_id = order_id[latest_positions]
customer_id = customer_id[latest_positions]
updated_at = updated_at[latest_positions]
amount_cents = amount_cents[latest_positions]
```

This is the array equivalent of selecting rows from a table.

A common bug is selecting one column and forgetting to apply the same row positions to the others.

---

# 55. Missing or invalid timestamps

A real pipeline may contain missing or invalid timestamps.

This chapter does not yet teach NumPy's complete missing-value model; that belongs to Topic 05. But you should recognize the issue:

```text
What does "latest" mean if updated_at is missing?
```

You need a business rule such as:

```text
missing timestamp → always last
```

or:

```text
missing timestamp → quarantine record
```

Do not let an implicit sort order define business behavior accidentally.

---

# 56. Performance and memory reasoning

Indexing is not only about correctness. It affects resource consumption.

## Basic slicing

Often inexpensive because it can return a view:

```text
source buffer
     ↑
   slice
```

No full independent copy of the selected values is normally required.

## Boolean indexing

The selected result is a new array:

```text
source
  ↓
mask evaluation
  ↓
new selected array
```

The selected data needs storage.

## Fancy indexing

Also produces a copy:

```text
source
  ↓
integer positions
  ↓
new selected array
```

For a huge selection, this can consume substantial memory.

---

# 57. Example: memory implications

Suppose you have:

```text
10,000,000 int64 values
```

Each value needs 8 bytes of raw element storage.

So the source array is approximately:

```text
10,000,000 × 8
= 80,000,000 bytes
≈ 76.3 MiB
```

A Boolean-selected result containing several million values needs another allocation.

That means a pipeline can temporarily hold:

```text
source array
+
mask
+
selected result
+
other intermediate data
```

The exact peak depends on the expression and how long references remain alive.

Engineering rule:

> **Do not estimate memory from the final result alone. Think about all arrays alive at the same time.**

---

# 58. Full sorting versus top-k

Suppose:

```text
N = 10,000,000
k = 100
```

If the requirement is:

> "Give me the top 100."

A complete `argsort` of all ten million positions does work that is not needed for the final answer.

The pattern:

```python
candidates = np.argpartition(values, -k)[-k:]
top_k = candidates[np.argsort(values[candidates])[::-1]]
```

limits the full ordering step to the small candidate set.

This is one example of an important data-engineering principle:

> **Match the algorithm to the actual question.**

Do not fully sort the universe when you only need a small extreme subset.

---

# 59. Repeated selection and unnecessary copies

Compare:

```python
selected = a[a > 100]
selected = selected[selected < 1000]
```

with a single combined mask:

```python
selected = a[(a > 100) & (a < 1000)]
```

The second form is often clearer and can avoid retaining multiple intermediate selected arrays.

This does not mean:

> "Always combine everything."

Readability and measurement matter.

The engineering process is:

```text
write correct code
    ↓
measure
    ↓
inspect memory if needed
    ↓
optimize a real bottleneck
```

---

# 60. Hands-on exercise: `select_and_dedupe.py`

The roadmap's production exercise combines filtering, ranking, lookup, binning, and deduplication.

You will work with:

```text
order_id
customer_id
updated_at
status_code
amount_cents
```

The same logical order may appear in multiple versions.

Your goal is to build the selection logic using NumPy only.

---

## Exercise setup

Generate deterministic test data:

```python
import numpy as np

rng = np.random.default_rng(42)

n_rows = 100_000

order_id = rng.integers(
    1,
    25_000,
    size=n_rows,
    dtype=np.int64,
)

customer_id = rng.integers(
    1,
    10_000,
    size=n_rows,
    dtype=np.int64,
)

updated_at = rng.integers(
    1_700_000_000,
    1_700_900_000,
    size=n_rows,
    dtype=np.int64,
)

status_code = rng.integers(
    0,
    3,
    size=n_rows,
    dtype=np.int8,
)

amount_cents = rng.integers(
    100,
    2_000_000,
    size=n_rows,
    dtype=np.int64,
)
```

For the exercise, treat:

```text
0 = pending
1 = paid
2 = cancelled
```

The roadmap's exact semantic labels can be adjusted to your data model, but the code must consistently apply the chosen rule.

---

## Task 1 — Filter paid orders over 10,000 cents in the last 7 days

Define a cutoff.

For example, use:

```python
cutoff = updated_at.max() - 7 * 24 * 60 * 60
```

Then build one mask:

```text
status is paid
AND amount > 10,000
AND updated_at >= cutoff
```

Requirements:

1. Use `&`.
2. Put parentheses around each condition.
3. Predict the mask shape before running the code.
4. Apply the same mask to every aligned column you need.
5. Count how many records passed.

Before coding, write:

```text
Mask shape:
Expected dtype:
How many True values:
```

---

## Task 2 — Find the top 100 orders by amount

Requirements:

1. Use `np.argpartition`.
2. Select the candidate top 100.
3. Sort only those 100 candidates.
4. Return the final positions in descending amount order.
5. Apply those positions to `order_id` and `amount_cents`.

Target pattern:

```text
all rows
  ↓
argpartition
  ↓
100 candidates
  ↓
sort 100
  ↓
top 100
```

Do not use a full `argsort` for the main solution.

Then implement a tiny reference version with full sorting so you can verify correctness on a smaller dataset.

---

## Task 3 — Keep the latest version of each `order_id`

Requirements:

1. Use `np.lexsort`.
2. Order by `order_id`.
3. Within an order, place the newest `updated_at` first.
4. Use `np.unique(..., return_index=True)`.
5. Map the selected positions back to the original arrays.
6. Preserve all aligned columns.
7. Define a deterministic tie-breaker if timestamps tie.

Before coding, describe the algorithm in plain language.

Do not write a one-line solution until you can explain each intermediate array.

---

## Task 4 — Status lookup

Create a lookup array:

```python
status_labels = np.array(
    ["pending", "paid", "cancelled"],
)
```

Map:

```python
status_code
```

to labels by integer indexing.

Then validate that every `status_code` is within the lookup-table bounds before indexing.

---

## Task 5 — Price bands

Create sorted band edges such as:

```python
band_edges = np.array(
    [0, 1_000, 10_000, 100_000, 1_000_000],
)
```

Use:

```python
np.searchsorted(...)
```

to assign every amount to an interval.

Test boundary values deliberately:

```text
0
999
1000
10000
100000
```

and explain the result for each boundary.

---

## Task 6 — Pure-Python reference implementation

Create tiny input data by hand.

Implement the same business logic with Python lists and loops.

Then implement the NumPy version.

Compare them with:

```python
np.testing.assert_array_equal(...)
```

for integer outputs where exact equality is appropriate.

The pure-Python implementation is not the production solution. It is a **correctness oracle**.

---

# 61. Testing strategy

The best way to gain confidence in vectorized selection code is to compare it against simple reference logic.

Start with tiny data where you can calculate the answer by inspection.

Example:

```python
import numpy as np

values = np.array([10, 20, 30, 40])

expected = np.array([20, 30, 40])
actual = values[values > 10]

np.testing.assert_array_equal(actual, expected)
```

---

## 61.1 Required edge cases

Your tests should include:

### Empty array

```python
empty = np.array([], dtype=np.int64)
```

Questions:

```text
Does filtering work?
Does sorting work?
What shape is returned?
```

### One row

Ensure indexing does not accidentally assume multiple rows.

### No matching rows

```python
mask = values > 1_000_000
```

The result should be an empty array with predictable shape and dtype.

### All rows match

Verify the complete selection path.

### Duplicate keys

Essential for deduplication.

### Tied timestamps

Essential for deterministic tie-breaking.

### Repeated fancy indices

For example:

```python
positions = np.array([2, 2, 0])
```

Confirm repeated selections are intentional.

### Negative indices

Test the boundaries:

```python
a[-1]
a[-len(a)]
```

### Top-k with `k=1`

This catches shape/partition mistakes.

### Top-k with `k == len(a)`

Make sure the algorithm handles the full-length boundary correctly.

### `searchsorted` boundaries

Explicitly test values exactly equal to each edge.

---

# 62. A useful test pattern for deduplication

For a small dataset:

```python
order_id = np.array([101, 101, 102, 102])
updated_at = np.array([10, 30, 20, 15])
```

The correct latest rows are:

```text
101 → timestamp 30
102 → timestamp 20
```

A pure-Python reference can be written in a straightforward way:

```python
latest = {}

for i, key in enumerate(order_id):
    timestamp = updated_at[i]

    if key not in latest or timestamp > latest[key][1]:
        latest[key] = (i, timestamp)

expected_positions = np.array(
    [latest[key][0] for key in sorted(latest)]
)
```

Then compare the NumPy implementation.

Why use such a simple reference?

Because complexity should live in the optimized solution, not in the test oracle.

---

# 63. Debugging NumPy indexing problems

When an indexing result surprises you, inspect the fundamentals first.

Useful inspection:

```python
print(a.shape)
print(a.dtype)
print(a.ndim)
```

For a Boolean filter:

```python
print(mask.shape)
print(mask.dtype)
print(np.count_nonzero(mask))
```

For broadcasting-related index arrays:

```python
print(rows.shape)
print(cols.shape)
print(np.broadcast_shapes(rows.shape, cols.shape))
```

When selection memory behavior matters:

```python
print(np.shares_memory(a, selected))
```

The debugging workflow should be:

```text
unexpected result
      ↓
inspect shapes
      ↓
inspect dtypes
      ↓
inspect index arrays / masks
      ↓
predict the selection semantics
      ↓
check view/copy behavior
      ↓
fix the smallest incorrect assumption
```

---

# 64. Debugging bug 1: using `and`

Broken:

```python
import numpy as np

a = np.array([10, 20, 30])

mask = (a > 10) and (a < 30)
```

### Symptom

A `ValueError` about the truth value of an array being ambiguous.

### Root cause

Python `and` expects scalar truth semantics.

### Correct code

```python
mask = (a > 10) & (a < 30)
```

### Prevention

Remember:

```text
and → &
or  → |
not → ~
```

for element-wise Boolean array operations.

---

# 65. Debugging bug 2: missing parentheses

Broken:

```python
mask = a > 10 & a < 100
```

### Symptom

The expression may be parsed in an unintended way or produce a confusing error.

### Root cause

Operator precedence.

### Correct code

```python
mask = (a > 10) & (a < 100)
```

### Prevention

Always parenthesize comparisons inside NumPy Boolean expressions.

---

# 66. Debugging bug 3: unexpected result shape

Suppose:

```python
a = np.arange(12).reshape(3, 4)

rows = np.array([0, 2])
cols = np.array([1, 3])

result = a[rows, cols]
```

If you expected a 2×2 matrix, you will be surprised.

The actual semantics are paired coordinates:

```text
(0, 1)
(2, 3)
```

so the result shape is:

```text
(2,)
```

### Prevention

Always ask:

```text
Are my index arrays paired?
Or do I want every combination?
```

Use `np.ix_` or explicit index broadcasting for the Cartesian-product case.

---

# 67. Debugging bug 4: chained assignment

Broken:

```python
a[mask][0] = 5
```

### Symptom

The intended element in `a` is unchanged.

### Root cause

`a[mask]` creates a copy.

### Correct alternatives

If you know the Boolean condition identifies the exact assignment set:

```python
a[mask] = 0
```

Or, if you specifically need the first matching position:

```python
positions = np.flatnonzero(mask)

if positions.size:
    a[positions[0]] = 5
```

This makes the target position explicit.

---

# 68. Debugging bug 5: fancy indexing uses too much memory

Example:

```python
selected = very_large_array[very_large_positions]
```

### Symptom

Unexpected memory growth.

### Root cause

Fancy indexing creates a new array.

### Inspection

```python
print(selected.nbytes)
print(np.shares_memory(very_large_array, selected))
```

### Prevention

Ask whether you actually need a materialized copy.

In some workflows, preserving positions and processing in batches can reduce peak memory.

Do not automatically add `.copy()` or avoid all copies. The correct decision depends on the ownership and lifetime of the data.

---

# 69. Debugging bug 6: full sort for a top-k problem

Broken approach:

```python
order = np.argsort(values)[-100:]
```

This fully sorts the input.

### Root cause

The algorithm answers a harder question than necessary.

### Better approach

```python
candidate = np.argpartition(values, -100)[-100:]
order = candidate[np.argsort(values[candidate])]
```

Reverse the candidate order when descending output is required.

### Prevention

Ask:

> "Do I need the full ranking, or only the top-k set?"

---

# 70. Debugging bug 7: wrong `lexsort` key order

Suppose:

```python
order = np.lexsort((timestamp, customer_id))
```

Remember:

> The **last** key is primary.

Therefore:

```text
customer_id = primary
timestamp   = secondary
```

If you accidentally reverse the keys, you may get a completely different grouping and deduplication result.

### Prevention

Before using `lexsort`, write:

```text
Primary key:
Secondary key:
Tie-breaker:
```

Then construct the key tuple in the correct order.

---

# 71. Debugging bug 8: deduplication keeps the wrong row

A common broken approach is:

```python
values, positions = np.unique(
    order_id,
    return_index=True,
)
```

and assuming those positions mean:

> latest record per key.

They do not.

`unique` cannot infer your business rule.

You first need:

```text
business ordering
→ deterministic sequence
→ select desired occurrence
```

Then `unique(return_index=True)` can help identify the selected row positions.

### Prevention

Write the business rule first:

```text
For each order:
keep the row with maximum updated_at.
If tied:
keep the row with maximum ingestion_sequence.
```

Then encode that ordering explicitly.

---

# 72. Production applications

These concepts appear throughout real Data Engineering systems.

## 72.1 Data filtering

Remove invalid records before transformation:

```text
valid sensor range
AND
known device
AND
timestamp in expected window
```

NumPy expression:

```python
mask = (
    (temperature >= -40)
    & (temperature <= 85)
    & np.isin(device_status, allowed_statuses)
)

clean = temperature[mask]
```

---

## 72.2 CDC latest-record selection

CDC streams can contain multiple changes for the same entity.

The pattern:

```text
business key
+
event/update timestamp
+
tie-breaker
```

can be ordered deterministically and reduced to one current version.

---

## 72.3 Top transaction analysis

Risk and analytics systems may ask:

```text
top 100 transactions
top 1% amounts
largest anomalies
```

`argpartition` can be appropriate when only a small top-k set is required.

---

## 72.4 Lookup

Numeric status or category codes can be mapped through lookup arrays.

This can be useful for compact batch transformations.

---

## 72.5 Binning

`searchsorted` can classify:

```text
latency
amount
score
age
risk
```

into predefined ranges.

---

## 72.6 Data-quality checks

Boolean masks provide the raw mechanism for:

```text
invalid row count
missing threshold
range violations
domain violations
```

For example:

```python
invalid = (amount_cents < 0) | (amount_cents > maximum_amount)
invalid_rate = invalid.mean()
```

---

## 72.7 Batch preparation

Before handing a batch to another system, you may select:

```text
eligible rows
required columns
required IDs
specific feature positions
```

The selection logic must remain explicit and testable.

---

# 73. Selection and SQL: a practical mental bridge

It is helpful to translate concepts between tools without pretending they are identical.

### SQL `WHERE`

```sql
WHERE amount_cents > 10000
```

Conceptually:

```python
mask = amount_cents > 10_000
amount_cents[mask]
```

### SQL `ORDER BY`

```sql
ORDER BY amount_cents
```

Conceptually:

```python
order = np.argsort(amount_cents)
```

### SQL `LIMIT 100`

Conceptually:

```python
candidate = np.argpartition(amount_cents, -100)[-100:]
```

### SQL `DISTINCT`

Conceptually:

```python
np.unique(customer_id)
```

### SQL `IN`

Conceptually:

```python
np.isin(customer_id, allowed_ids)
```

The bridge is useful because it lets Data Engineers carry familiar relational thinking into in-memory numerical processing.

---

# 74. Performance checklist

Before optimizing selection code, ask:

```text
1. How many rows are being processed?
2. Is the selection a view or a copy?
3. How much memory does the result require?
4. Do I really need a full sort?
5. Do I only need top-k?
6. Am I creating repeated intermediate selections?
7. Are index arrays much smaller than the selected data?
8. Is the input already ordered?
9. Do I need deterministic tie-breaking?
10. Can I test the algorithm on a tiny reference dataset first?
```

Avoid guessing about exact speed.

Actual performance depends on:

- hardware,
- NumPy version,
- dtype,
- shape,
- memory layout,
- cache behavior,
- input distribution,
- operation,
- number of allocations.

---

# 75. Common mistakes

## Mistake 1 — using `and` instead of `&`

**Why it happens:** Python scalar habits.

**Broken:**

```python
(a > 10) and (a < 100)
```

**Correct:**

```python
(a > 10) & (a < 100)
```

**Prevention:** Remember element-wise Boolean operators.

---

## Mistake 2 — using `or` instead of `|`

**Broken:**

```python
(a == 1) or (a == 5)
```

**Correct:**

```python
(a == 1) | (a == 5)
```

---

## Mistake 3 — missing parentheses

**Broken:**

```python
a > 10 & a < 100
```

**Correct:**

```python
(a > 10) & (a < 100)
```

---

## Mistake 4 — treating scalar indexing like slicing

```python
a[2]
```

and:

```python
a[2:3]
```

are not the same shape-wise.

A scalar index can reduce a dimension; a slice preserves a length-1 axis.

Predict shape before using either one.

---

## Mistake 5 — misunderstanding negative indices

```python
a[-1]
```

means the last element.

It does not mean "index minus one from zero in some arithmetic sense."

---

## Mistake 6 — chained indexing

**Broken:**

```python
a[mask][0] = 5
```

**Correct approach:** perform the assignment on the original array or explicitly compute a target position.

---

## Mistake 7 — assuming Boolean indexing returns a view

It returns a copy.

Verify with:

```python
np.shares_memory(a, selected)
```

---

## Mistake 8 — assuming fancy indexing returns a view

Integer-array indexing returns a copy.

---

## Mistake 9 — misunderstanding `a[rows, cols]`

This pairs coordinates:

```text
(rows[0], cols[0])
(rows[1], cols[1])
...
```

It does not automatically form every row/column combination.

---

## Mistake 10 — misunderstanding `np.ix_`

`np.ix_` is useful when you want a Cartesian product of selected row and column indices.

---

## Mistake 11 — using `argsort` for every top-k problem

Full sorting is not necessary when only a small top-k set is needed.

Use `argpartition` followed by sorting only the candidates.

---

## Mistake 12 — unstable sorting during deduplication

If ties exist, an unspecified ordering can make "which row wins?" ambiguous.

Use deterministic keys and stable ordering where required.

---

## Mistake 13 — incorrect `lexsort` key order

The last key is primary.

Write the intended hierarchy down before coding.

---

## Mistake 14 — using `searchsorted` with unsorted boundaries

The search input must satisfy the sortedness requirement.

---

## Mistake 15 — calling `unique` before defining business ordering

`unique` does not know your definition of "latest."

First establish the ordering that makes the desired record the selected occurrence.

---

## Mistake 16 — creating large copies repeatedly

Repeated Boolean or fancy selections can increase peak memory.

Measure before optimizing, then simplify or batch the computation when there is a demonstrated bottleneck.

---

# 76. Prediction drills

For each expression, write:

```text
Result shape:
View or copy:
Why:
```

before running it.

Use:

```python
import numpy as np

a = np.arange(20).reshape(5, 4)
mask = a[:, 0] > 5
rows = np.array([0, 2, 4])
cols = np.array([1, 3])
```

## Drill 1

```python
a[1:4]
```

## Drill 2

```python
a[:, 1]
```

## Drill 3

```python
a[..., -1]
```

## Drill 4

```python
a[mask]
```

## Drill 5

```python
a[[1, 4]]
```

## Drill 6

```python
a[rows, cols]
```

## Drill 7

```python
a[rows[:, None], cols]
```

## Drill 8

```python
a[np.ix_(rows, cols)]
```

## Drill 9

```python
a[::-1]
```

## Drill 10

```python
a[1:4, 1:3]
```

For each one, explain the result rather than memorizing a table.

---

# 77. Checkpoint

Do not look back at the chapter for the first attempt.

## Core questions

### 1. Why does this fail?

```python
a[(a > 1) and (a < 5)]
```

State the correct version and explain why.

### 2. What do these operators mean for NumPy Boolean arrays?

```text
&
|
~
```

### 3. Which selection styles return views?

State the general rule for:

```text
basic slicing
Boolean indexing
integer/fancy indexing
```

### 4. Why can this fail to change the original?

```python
a[mask][0] = 5
```

### 5. Why can this change the original?

```python
a[mask] = 0
```

### 6. What is the difference between:

```python
np.sort(a)
np.argsort(a)
```

### 7. When should you consider `argpartition` instead of a full sort?

### 8. Which key is primary in:

```python
np.lexsort((secondary, primary))
```

### 9. What must be true about the search array used by `np.searchsorted`?

### 10. What is the difference between:

```python
a[rows, cols]
```

and:

```python
a[np.ix_(rows, cols)]
```

### 11. Explain how to implement "latest record per key."

Your explanation should include:

```text
ordering
→ unique positions
→ mapping back to original positions
→ aligned-column selection
```

---

# 78. Harder checkpoint exercises

## Exercise A — filter

Given:

```python
amount = np.array([50, 200, 500, 800])
status = np.array([1, 2, 2, 3])
```

select records where:

```text
status == 2
AND
amount >= 300
```

Predict the mask and result before running.

---

## Exercise B — top-k

Given one million values, find the largest 10 without fully sorting all one million values.

Explain:

```text
candidate selection
→ candidate sorting
```

---

## Exercise C — paired indexing

Given:

```python
a = np.arange(12).reshape(3, 4)
rows = np.array([0, 2])
cols = np.array([1, 3])
```

Predict:

```python
a[rows, cols]
```

Then predict:

```python
a[rows[:, None], cols]
```

Explain why they differ.

---

## Exercise D — searchsorted

Given:

```python
edges = np.array([10, 20, 50, 100])
```

Predict the insertion position for:

```text
9
10
11
49
50
101
```

for both:

```python
side="left"
side="right"
```

---

## Exercise E — latest record

Given:

```python
order_id = np.array([2, 1, 2, 1, 3])
updated_at = np.array([20, 10, 30, 50, 40])
```

Which rows should remain?

Do the reasoning manually before writing NumPy code.

---

# 79. Final mental model

The entire topic can be compressed into one hierarchy:

```text
BASIC INDEXING
→ position-based selection

SLICING
→ range-based selection
→ generally a view

BOOLEAN MASKING
→ condition-based selection
→ copy

FANCY INDEXING
→ arbitrary-position selection
→ copy

SORTING
→ ordering

ARGPARTITION
→ top-k candidate selection

SEARCHSORTED
→ range / insertion lookup

LEXsort + UNIQUE
→ deterministic deduplication
```

Another useful picture is:

```text
Array
  ↓
Position
  ↓
Basic indexing
  ↓
Slicing
  ↓
Boolean condition
  ↓
Boolean mask
  ↓
Filtering
  ↓
Integer/fancy indexing
  ↓
Reordering / lookup
  ↓
Sorting / ranking
  ↓
Top-k
  ↓
Search / binning
  ↓
Deduplication
  ↓
Production data selection
```

---

# 80. Engineering decision framework

Before selecting data from a large NumPy array, ask:

```text
1. Am I selecting by position, condition, or arbitrary index?
2. What shape will the result have?
3. Is the result a view or a copy?
4. Will I modify the result?
5. Do I need a full sort or only top-k?
6. Do my keys need deterministic tie-breaking?
7. Is the search input sorted?
8. Could this operation create a large copy?
9. Can I express the selection as one vectorized operation?
10. How will I test empty, duplicate, boundary, and edge cases?
```

This checklist is more valuable than memorizing isolated APIs.

---

# 81. What to remember about memory

A selection expression has both **semantic** and **memory** consequences.

```text
What rows did I choose?
        +
How is the result stored?
```

For example:

```text
a[1:100]
→ often a view

a[a > 100]
→ copy

a[[1, 5, 7]]
→ copy
```

So a correct algorithm can still be a poor production implementation if it repeatedly materializes very large selections.

The right question is not:

> "Can NumPy do this?"

It is:

> "Can NumPy do this correctly, predictably, and within the memory/performance budget?"

---

# 82. Connection to Topic 04 — aggregations and axis semantics

Now you know how to **select the correct data**.

The next topic asks:

> **How do I summarize that selected data correctly?**

The learning sequence is:

```text
01 ndarray / dtype / memory
           ↓
02 vectorization / broadcasting
           ↓
03 indexing / masks / fancy indexing
           ↓
04 aggregations / axis semantics
```

For example:

```text
filter valid orders
        ↓
select paid orders
        ↓
select latest record per order
        ↓
aggregate revenue by customer/day/store
```

You need reliable selection before the aggregation can be trusted.

Topic 04 will build on exactly the operations learned here and focus on:

```text
sum
mean
min
max
percentiles
axis
group-style aggregation
```

---

# 83. Final review exercise

Without looking back, implement a small NumPy pipeline that:

1. Creates order data.
2. Filters records with a Boolean mask.
3. Counts rejected records.
4. Maps status codes through a lookup array.
5. Assigns price bands with `searchsorted`.
6. Finds the top 5 amounts using `argpartition`.
7. Sorts the top 5.
8. Deduplicates orders by latest timestamp using `lexsort` + `unique`.
9. Uses the same positional selection across every aligned column.
10. Tests the optimized implementation against a tiny pure-Python reference.

For each major selection step, write down:

```text
shape:
dtype:
view/copy:
memory implication:
```

When you can do that without guessing, you have moved beyond memorizing indexing syntax and started reasoning like a Data Engineer.
