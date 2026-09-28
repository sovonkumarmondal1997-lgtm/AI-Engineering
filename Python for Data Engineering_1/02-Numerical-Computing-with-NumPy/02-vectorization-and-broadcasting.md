# Topic 02 — Vectorization and Broadcasting

> **Stage 2 — Python for Data Engineering**  
> **Module 2.2 — Numerical Computing with NumPy**  
> **Topic:** Vectorization and Broadcasting  
> **Target:** NumPy 2.x

---

## 1. Introduction

Vectorization is one of the central ideas that turns NumPy from a convenient array container into a practical numerical-computing engine.

At the beginner level, it is tempting to think about a dataset one record at a time:

```text
row 1 → calculate
row 2 → calculate
row 3 → calculate
...
row N → calculate
```

That is exactly how a Python loop is commonly written. The problem is that a large numerical workload may contain millions of values. Repeatedly executing Python-level loop logic creates overhead that is often much larger than the arithmetic itself.

NumPy encourages a different way of thinking:

```text
whole array → one array expression → bulk numerical operation
```

For example, instead of writing:

```python
line_totals = []
for qty, unit_price in zip(quantities, unit_prices):
    line_totals.append(qty * unit_price)
```

you can write:

```python
line_totals = quantities * unit_prices
```

The second form is not merely shorter. For supported operations, NumPy moves the element-wise iteration into its optimized implementation rather than repeatedly executing Python bytecode for each element.

Broadcasting extends the same idea. It lets NumPy combine arrays whose shapes are compatible without you manually constructing repeated copies of the smaller input.

For a Data Engineer, these ideas matter because batch transformations commonly look like:

- calculate millions of order totals,
- apply a tax or exchange rate by category,
- normalize numerical columns,
- cap sensor values,
- classify records using thresholds,
- calculate quality indicators,
- transform feature batches before model inference.

The important production lesson is:

> **Vectorization is about expressing a computation in array operations. Broadcasting is about making compatible shapes participate in those array operations. Neither concept removes the need to reason about memory, dtype, numerical correctness, or output size.**

### What you should be able to do after this chapter

By the end of this topic, you should be able to:

- replace many Python numerical loops with genuine NumPy array operations,
- identify common NumPy universal functions (ufuncs),
- use `np.where`, `np.select`, and `np.clip` for vectorized conditional logic,
- predict whether two shapes can broadcast,
- manually calculate a broadcasting result shape,
- use `np.newaxis`, `None`, and `reshape` to express intended dimensions,
- use `reduce`, `accumulate`, `outer`, and `at` on appropriate ufuncs,
- recognize when broadcasting creates a dangerous `N × M` result,
- use chunking to bound memory for large computations,
- reduce unnecessary temporary arrays with `out=` and carefully chosen in-place operations,
- understand why `np.vectorize` and `np.apply_along_axis` are not replacements for genuine vectorization,
- handle `inf`, `nan`, division by zero, and invalid floating-point operations intentionally,
- benchmark loop and vectorized implementations instead of assuming one is faster,
- test vectorized code against a simple reference implementation.

---

## 2. Why vectorization matters in Data Engineering

A data pipeline often processes columns rather than individual Python objects. This makes array-oriented computation a natural fit.

Consider an order table with five million rows:

```text
quantity         → 5,000,000 numeric values
unit_price_cents → 5,000,000 numeric values
```

A common transformation is:

```text
line_total_cents = quantity × unit_price_cents
```

You could process rows one by one. But if the operation is simply element-wise multiplication, there is no business reason to write Python control flow around every row.

NumPy lets you express the transformation at the level of the entire batch:

```python
line_total_cents = quantity * unit_price_cents
```

This style is closely related to other Data Engineering systems:

| Tool or concept | Connection |
|---|---|
| pandas | Many DataFrame column operations eventually rely on array-oriented kernels. |
| Arrow | Columnar buffers make bulk operations over columns natural. |
| Polars | Expression-based transformations are explicitly column oriented. |
| Spark | Distributed DataFrame operations express transformations over datasets rather than Python row loops. |
| SQL | `SELECT amount * tax_rate` is also declarative, set-oriented computation. |
| ML pipelines | Numeric feature batches are frequently represented as arrays or tensors. |

The specific implementation differs across systems, but the engineering idea is similar: **describe the operation over a collection instead of hand-writing per-record control flow when the operation is naturally element-wise.**

### Vectorized does not mean “shorter code”

This is an important distinction.

A five-line expression is not automatically better than a ten-line loop. The relevant questions are:

1. Does the expression perform the same computation?
2. Is the implementation efficient for the workload?
3. Does it use acceptable memory?
4. Is it numerically correct?
5. Is it easy to test and maintain?

A vectorized expression can still be a bad production implementation if it creates a huge intermediate array or hides a business rule that nobody can understand.

---

## 3. Python loops versus NumPy vectorization

### 3.1 Start with ordinary Python

Suppose we need to multiply every value by `2`.

```python
values = [10, 20, 30, 40]

result = []
for value in values:
    result.append(value * 2)

print(result)
```

Output:

```text
[20, 40, 60, 80]
```

This is correct and perfectly reasonable for a tiny list.

### 3.2 The NumPy version

```python
import numpy as np

values = np.array([10, 20, 30, 40])
result = values * 2

print(result)
```

Output:

```text
[20 40 60 80]
```

The key difference is how you express the operation. You tell NumPy to multiply the array by `2` and NumPy applies the supported element-wise operation across the array.

### 3.3 The internal mental model

A useful simplified model is:

```text
Python loop
    ↓
Python bytecode executes repeatedly
    ↓
per-element Python operations
    ↓
result
```

versus:

```text
NumPy expression
    ↓
ufunc / NumPy array operation
    ↓
optimized native/compiled iteration over data
    ↓
result
```

The second path does still contain iteration internally. The difference is that the iteration for supported operations is handled by NumPy's implementation rather than by a Python `for` statement invoking Python-level logic for every element.

### 3.4 Why this can be much faster

Python has overhead associated with repeatedly executing interpreter-level operations. NumPy can work with homogeneous typed memory and optimized numerical kernels.

The speed-up depends on:

- array size,
- operation type,
- dtype,
- memory layout and access pattern,
- whether a result must be allocated,
- temporary arrays,
- CPU capabilities,
- and what the alternative Python implementation is doing.

Do **not** memorize “NumPy is always faster.”

The better rule is:

> **For large, homogeneous numerical arrays, compare a Python-level loop with an operation implemented by NumPy's native array machinery, then measure the actual workload.**

### 3.5 Where a Python loop can still be appropriate

Not every problem is naturally vectorizable.

A Python loop can be reasonable when:

- each record requires a complex Python object interaction,
- the algorithm has irregular branching that has no useful NumPy equivalent,
- the dataset is tiny,
- I/O dominates the workload,
- readability would suffer from a forced vectorized formulation.

The goal is not “never write loops.” The goal is to stop writing Python loops when the problem is naturally a bulk array operation.

---

## 4. Universal functions (ufuncs)

A **universal function**, usually abbreviated **ufunc**, is a NumPy object designed to apply an operation element-by-element to array inputs, while handling broadcasting, dtype resolution, and other array semantics.

Examples include ufuncs and ufunc-like functions such as:

```python
np.add
np.subtract
np.multiply
np.divide
np.sqrt
np.exp
np.log
np.abs
np.round
```

The Python operators themselves often map to ufunc operations when arrays are involved. For example:

```python
a + b
```

corresponds conceptually to an element-wise add operation.

### 4.1 Why ufuncs exist

Imagine having to implement separate optimized code for every combination of:

- scalar + scalar,
- array + scalar,
- array + array,
- different compatible shapes,
- different numeric dtypes.

A ufunc provides a common mechanism for element-wise array computation.

### 4.2 Inspecting a ufunc

```python
import numpy as np

print(np.add)
print(type(np.add))
```

A NumPy version may display information similar to:

```text
<ufunc 'add'>
<class 'numpy.ufunc'>
```

The exact object representation is less important than the idea: `np.add` is a ufunc, not an ordinary Python function that happens to take arrays.

---

## 5. Arithmetic vectorization

NumPy supports the common arithmetic operators element-wise for array inputs.

### Addition

```python
import numpy as np

revenue = np.array([100, 200, 300])
refunds = np.array([10, 20, 30])

net = revenue - refunds
print(net)
```

Output:

```text
[ 90 180 270]
```

### Multiplication

```python
quantity = np.array([2, 5, 3])
unit_price = np.array([100, 250, 400])

line_total = quantity * unit_price
print(line_total)
```

Output:

```text
[ 200 1250 1200]
```

### Division

```python
amount = np.array([100.0, 200.0, 300.0])
units = np.array([4.0, 5.0, 6.0])

average = amount / units
print(average)
```

Output:

```text
[25.         40.         50.        ]
```

### Exponentiation

```python
values = np.array([1.0, 2.0, 3.0])
print(values ** 2)
```

Output:

```text
[1. 4. 9.]
```

### Data Engineering use case

Arithmetic vectorization is useful for:

```text
quantity × price
amount × exchange_rate
usage × unit_cost
raw_signal × calibration_factor
```

When the formula is genuinely element-wise, this is usually the first style to try.

---

## 6. Mathematical ufuncs

The roadmap requires several mathematical operations because they are common in data transformation and numerical feature preparation.

### 6.1 `np.sqrt`

```python
import numpy as np

values = np.array([1.0, 4.0, 9.0, 16.0])
result = np.sqrt(values)

print(result)
```

Output:

```text
[1. 2. 3. 4.]
```

**Use case:** square-root transformations, distances, scientific measurements.

### 6.2 `np.exp`

```python
x = np.array([0.0, 1.0, 2.0])
print(np.exp(x))
```

Output:

```text
[1.         2.71828183 7.3890561 ]
```

**Use case:** exponential transforms and formulas used in statistics or modeling.

### 6.3 `np.log`

```python
x = np.array([1.0, 10.0, 100.0])
print(np.log(x))
```

**Use case:** log transforms of positive quantities with a highly skewed distribution.

Important: `log(0)` is not a normal finite value; it produces `-inf` under NumPy's floating-point rules. Handling such values is covered later.

### 6.4 `np.abs`

```python
errors = np.array([-3.0, 2.0, -1.0, 4.0])
absolute_error = np.abs(errors)
print(absolute_error)
```

Output:

```text
[3. 2. 1. 4.]
```

**Use case:** absolute differences, magnitude of errors, tolerance checks.

### 6.5 `np.round`

```python
values = np.array([1.234, 5.678, 9.999])
print(np.round(values, 2))
```

Output:

```text
[1.23 5.68 10.  ]
```

Rounding is useful for display or specific business logic, but it should not be confused with choosing an exact representation for financial values.

### 6.6 `np.clip`

`np.clip` is both a common ufunc-like numerical operation and a useful business-rule tool.

```python
scores = np.array([-10, 20, 50, 120])
clipped = np.clip(scores, 0, 100)

print(clipped)
```

Output:

```text
[  0  20  50 100]
```

Think of it as:

```text
below lower bound → lower bound
inside range      → unchanged
above upper bound → upper bound
```

---

## 7. Comparison operations produce arrays of booleans

Comparisons are vectorized too.

```python
import numpy as np

amount = np.array([500, 1500, 2500, 800])
mask = amount > 1000

print(mask)
```

Output:

```text
[False  True  True False]
```

Other common comparisons include:

```python
a == 0
a != 10
a <= threshold
a >= threshold
a < limit
```

The result is another array. This is an important bridge to Topic 03, where these boolean results will become masks for selecting data.

### Element-wise boolean logic

For NumPy arrays, use element-wise boolean operators:

```python
mask = (amount > 1000) & (amount < 3000)
```

Do not write:

```python
mask = (amount > 1000) and (amount < 3000)
```

The Python `and` and `or` operators are designed around single truth values, while NumPy comparisons produce arrays of truth values.

Parentheses are important because comparison and bitwise operator precedence can otherwise produce unexpected parsing.

---

## 8. Vectorized conditional logic

Many data transformations contain rules such as:

```text
if condition:
    value A
else:
    value B
```

or:

```text
if condition 1:
    small
elif condition 2:
    medium
else:
    large
```

NumPy provides array-oriented tools for these patterns.

---

## 9. `np.where`

### What it is

`np.where(condition, value_if_true, value_if_false)` selects values element-by-element based on a condition.

### Example

```python
import numpy as np

amount = np.array([500, 1500, 2500, 800])

label = np.where(amount >= 1000, "high", "normal")
print(label)
```

Output:

```text
['normal' 'high' 'high' 'normal']
```

### Internal mental model

For each position `i`:

```text
condition[i] is True  → choose true_value[i]
condition[i] is False → choose false_value[i]
```

The condition and selected values themselves can participate in broadcasting when their shapes are compatible.

### Data Engineering use cases

- flag suspicious transactions,
- label records as valid/invalid,
- apply two business-rule outcomes,
- replace a set of values with a fallback value.

Example:

```python
raw_temperature = np.array([-5.0, 20.0, 80.0])
status = np.where(raw_temperature > 60, "alarm", "normal")
print(status)
```

### Common mistake

Do not build a Python loop merely to perform a simple two-way selection that can naturally be represented by `where`.

---

## 10. `np.select`

`np.select` is useful when there are multiple ordered conditions.

Suppose order sizes are:

```text
< 1000 cents        → small
1000–4999 cents     → medium
>= 5000 cents       → large
```

```python
import numpy as np

amount = np.array([500, 1200, 3500, 7000])

conditions = [
    amount < 1000,
    amount < 5000,
]

choices = [
    "small",
    "medium",
]

labels = np.select(conditions, choices, default="large")
print(labels)
```

Output:

```text
['small' 'medium' 'medium' 'large']
```

### Important detail: condition order matters

`np.select` evaluates the conditions in order. When more than one condition could be true for an element, the first matching condition determines the selected value.

Therefore, write conditions in a deliberate order.

### `where` vs `select`

| Tool | Natural use |
|---|---|
| `np.where` | Two-way condition: true vs false. |
| `np.select` | Multiple ordered conditions and a default. |
| `np.clip` | Numeric lower/upper bounds. |

---

## 11. `np.clip`

`np.clip` is the natural tool when the business rule is simply a lower and/or upper bound.

```python
import numpy as np

battery = np.array([-3.0, 20.0, 50.0, 105.0])
normalized = np.clip(battery, 0.0, 100.0)

print(normalized)
```

Output:

```text
[  0.  20.  50. 100.]
```

### Data Engineering examples

- cap an impossible sensor value,
- constrain a score to a valid range,
- implement a rate limit,
- enforce a bounded numerical business rule before downstream processing.

Do not confuse clipping with fixing the underlying data-quality problem. A value outside the expected range may be an actual data defect. Whether it should be clipped, rejected, quarantined, or investigated is a business/data-quality decision.

---

# 12. Broadcasting — first principles

Broadcasting is the mechanism that allows NumPy to operate on arrays with compatible but different shapes.

Start with the simplest case:

```python
import numpy as np

a = np.array([1, 2, 3])
result = a + 10

print(result)
```

Output:

```text
[11 12 13]
```

Here:

```text
a.shape      = (3,)
scalar shape = ()
result       = (3,)
```

A scalar can participate naturally in an element-wise operation with every element.

Now consider two arrays:

```python
prices = np.array([100, 200, 300])
discounts = np.array([0.10, 0.20, 0.15])

final_price = prices * (1 - discounts)
print(final_price)
```

Each position is combined with the corresponding position.

Broadcasting becomes more interesting when dimensions differ.

---

## 13. The three broadcasting rules

NumPy's standard broadcasting rules are:

1. **Compare shapes from the rightmost dimension.**
2. **Two dimensions are compatible when they are equal or one of them is `1`.**
3. **If one shape has fewer dimensions, the missing leading dimensions are treated as `1`.**

These rules are the foundation. Memorizing them is less important than applying them mechanically.

### Rule 1 — align from the right

Suppose:

```text
A shape = (5, 1, 3)
B shape =    (4, 3)
```

Pad the shorter shape on the left with `1`:

```text
A = (5, 1, 3)
B = (1, 4, 3)
```

Now compare:

```text
5 vs 1 → compatible
1 vs 4 → compatible
3 vs 3 → compatible
```

Therefore the result shape is:

```text
(5, 4, 3)
```

Visual form:

```text
          A: (5, 1, 3)
          B:    (4, 3)
               ↓
Pad left: B: (1, 4, 3)
               ↓
Compare:   5   1   3
           1   4   3
           ─────────
Result:    5   4   3
```

### Rule 2 — equal or one

These dimensions are compatible:

```text
5 and 5
5 and 1
1 and 5
1 and 1
```

These are incompatible:

```text
5 and 4
8 and 6
3 and 2
```

### Rule 3 — missing dimensions act like `1`

For:

```text
A = (3, 4)
B = (4,)
```

Think of `B` as:

```text
B = (1, 4)
```

Then:

```text
A = (3, 4)
B = (1, 4)
Result = (3, 4)
```

---

## 14. Broadcasting does not mean “copy the smaller array”

A common beginner explanation is:

> “NumPy copies the smaller array until it matches the larger one.”

That is not a good mental model.

Broadcasting is primarily a **shape/iteration mechanism**. NumPy can often conceptually reuse the smaller operand across the repeated positions without physically allocating a full repeated copy of that operand.

However, the **output of the operation can still require a full allocation**.

That distinction is critical for production memory reasoning.

For example:

```python
result = matrix + vector
```

may avoid materializing a repeated copy of `vector`, but `result` is still an actual array containing every result element.

Later we will see why that matters enormously for pairwise operations.

---

# 15. Predict shapes before executing code

One of the most valuable NumPy habits is:

> **Predict the shape before you run the operation.**

Do not depend on trial-and-error.

For every array operation, ask:

```text
What is shape A?
What is shape B?
How do the dimensions align from the right?
Which dimensions become the result dimensions?
```

Then verify using:

```python
np.broadcast_shapes(shape_a, shape_b)
```

### Example 1

```text
(5,) + (5,)
```

Result:

```text
(5,)
```

### Example 2

```text
(5,) + (1,)
```

Result:

```text
(5,)
```

### Example 3

```text
(5, 1) + (1, 4)
```

Compare:

```text
5 vs 1 → 5
1 vs 4 → 4
```

Result:

```text
(5, 4)
```

### Example 4

```text
(3, 4) + (4,)
```

Pad the second shape:

```text
(3, 4)
(1, 4)
```

Result:

```text
(3, 4)
```

### Example 5

```text
(2, 3, 4) + (4,)
```

Think:

```text
(2, 3, 4)
(1, 1, 4)
```

Result:

```text
(2, 3, 4)
```

### Example 6

```text
(2, 3, 4) + (3, 1)
```

Pad the second shape:

```text
(2, 3, 4)
(1, 3, 1)
```

Result:

```text
(2, 3, 4)
```

### Example 7

```text
(5, 1, 3) + (4, 3)
```

Pad the second shape:

```text
(5, 1, 3)
(1, 4, 3)
```

Result:

```text
(5, 4, 3)
```

### Example 8 — incompatible

```text
(5, 2) + (3,)
```

Pad:

```text
(5, 2)
(1, 3)
```

Compare the final dimensions:

```text
2 vs 3 → incompatible
```

So broadcasting fails.

### Verify programmatically

```python
import numpy as np

print(np.broadcast_shapes((5, 1, 3), (4, 3)))
print(np.broadcast_shapes((3, 4), (4,)))
```

Output:

```text
(5, 4, 3)
(3, 4)
```

For an incompatible case:

```python
import numpy as np

try:
    print(np.broadcast_shapes((5, 2), (3,)))
except ValueError as exc:
    print(type(exc).__name__, exc)
```

The precise exception text can vary between NumPy versions, but the key result is that NumPy raises a broadcasting-related `ValueError` because the dimensions are incompatible.

---

# 16. A 20-shape prediction drill

Predict first. Run second.

| # | Shape A | Shape B | Broadcastable? | Result shape |
|---:|---|---|---|---|
| 1 | `(5,)` | `(5,)` | Yes | `(5,)` |
| 2 | `(5,)` | `(1,)` | Yes | `(5,)` |
| 3 | `(5, 1)` | `(1, 4)` | Yes | `(5, 4)` |
| 4 | `(3, 4)` | `(4,)` | Yes | `(3, 4)` |
| 5 | `(2, 3, 4)` | `(4,)` | Yes | `(2, 3, 4)` |
| 6 | `(2, 3, 4)` | `(3, 1)` | Yes | `(2, 3, 4)` |
| 7 | `(5, 1, 3)` | `(4, 3)` | Yes | `(5, 4, 3)` |
| 8 | `(8, 1, 6, 1)` | `(7, 1, 5)` | Yes | `(8, 7, 6, 5)` |
| 9 | `(10, 3)` | `(1, 3)` | Yes | `(10, 3)` |
| 10 | `(10, 1)` | `(7,)` | Yes | `(10, 7)` |
| 11 | `(4, 5, 6)` | `(6,)` | Yes | `(4, 5, 6)` |
| 12 | `(4, 5, 6)` | `(5, 1)` | Yes | `(4, 5, 6)` |
| 13 | `(4, 5, 6)` | `(4, 1, 1)` | Yes | `(4, 5, 6)` |
| 14 | `(6, 1)` | `(6, 1, 8)` | Yes | `(6, 6, 8)` |
| 15 | `(4, 3)` | `(2, 3)` | No | — |
| 16 | `(9, 1, 2)` | `(7, 2)` | Yes | `(9, 7, 2)` |
| 17 | `(9, 2, 1)` | `(7, 2)` | No | — |
| 18 | `(2, 1, 4, 1)` | `(3, 1, 4)` | Yes | `(2, 3, 4, 4)` |
| 19 | `(100,)` | `()` | Yes | `(100,)` |
| 20 | `(12, 1, 4)` | `(7, 4)` | Yes | `(12, 7, 4)` |

### Important warning about the drill

Do not merely memorize the table. Re-derive the answer from the three rules.

A strong NumPy engineer should be able to explain *why* the shape is what it is.

---

# 17. `np.newaxis` and `None`

A very common challenge is that your data is numerically correct but has the wrong dimensionality for the operation you want.

`np.newaxis` adds a dimension of size `1`.

`None` is an equivalent spelling in indexing contexts.

For example:

```python
import numpy as np

x = np.array([10, 20, 30])

print(x.shape)
print(x[:, np.newaxis].shape)
print(x[None, :].shape)
```

Output:

```text
(3,)
(3, 1)
(1, 3)
```

These shapes are not interchangeable.

### Mental model

A one-dimensional array:

```text
(n,)
```

can be viewed as:

```text
(n, 1) → column-like form

(1, n) → row-like form
```

### Visualize the difference

```text
x = [10 20 30]
shape = (3,)
```

Column-like:

```text
[10]
[20]
[30]
shape = (3, 1)
```

Row-like:

```text
[10 20 30]
shape = (1, 3)
```

### Equivalent syntax

```python
column = x[:, np.newaxis]
column_2 = x[:, None]

row = x[np.newaxis, :]
row_2 = x[None, :]
```

The difference is shape, not the underlying values.

---

# 18. Column-wise normalization with broadcasting

Suppose:

```python
X.shape == (n_rows, n_features)
```

and you calculate:

```python
mean = X.mean(axis=0)
std = X.std(axis=0)
```

Then:

```text
mean.shape == (n_features,)
std.shape  == (n_features,)
```

This naturally works with:

```python
Z = (X - mean) / std
```

because NumPy aligns the final dimension of `X` with the final dimension of `mean` and `std`.

For a small example:

```python
import numpy as np

X = np.array(
    [
        [10.0, 100.0],
        [20.0, 200.0],
        [30.0, 300.0],
    ]
)

mean = X.mean(axis=0)
std = X.std(axis=0)

Z = (X - mean) / std

print("X.shape   =", X.shape)
print("mean.shape=", mean.shape)
print("std.shape =", std.shape)
print("Z.shape   =", Z.shape)
```

All three are aligned around the feature dimension.

### Production lesson

When you work with a 2-D batch, explicitly document which dimension means:

```text
rows       = observations / records
columns    = features / measurements
```

A mathematically valid broadcast can still be semantically wrong if your shape convention is wrong.

---

# 19. `reshape` for broadcasting

`reshape` is another way to make intended dimensions explicit.

Consider rates for four categories:

```python
import numpy as np

rates = np.array([0.05, 0.10, 0.15, 0.20])

print(rates.shape)
print(rates.reshape(1, -1).shape)
print(rates.reshape(-1, 1).shape)
```

Output:

```text
(4,)
(1, 4)
(4, 1)
```

The meanings are:

```text
rates.reshape(1, -1)
→ one row, four columns
→ (1, 4)
```

and:

```text
rates.reshape(-1, 1)
→ four rows, one column
→ (4, 1)
```

### Why this matters

Suppose:

```text
X.shape = (10, 4)
```

and you have one rate per feature:

```text
rates.shape = (4,)
```

Then:

```python
adjusted = X * rates
```

naturally applies each feature rate to every row.

But if the values represent one rate per row:

```text
row_rates.shape = (10,)
```

you need:

```python
adjusted = X * row_rates[:, None]
```

Now:

```text
X            = (10, 4)
row_rates    = (10, 1)
result       = (10, 4)
```

### Rule of thumb

Use shape-changing operations to express intent clearly:

```text
(1, n) → broadcast across rows
(n, 1) → broadcast across columns
```

The exact phrase “across rows” can be confusing, so rely on shapes rather than language alone. Draw the dimensions.

---

# 20. Common production broadcasting patterns

## Pattern A — Column centering

```python
centered = X - X.mean(axis=0)
```

If:

```text
X.shape = (n_rows, n_features)
X.mean(axis=0).shape = (n_features,)
```

then broadcasting subtracts the corresponding feature mean from every row.

### Why this is useful

Common in:

- feature preprocessing,
- sensor calibration,
- numerical analysis,
- batch statistics.

---

## Pattern B — Column min-max scaling

The common formula is:

```python
mins = X.min(axis=0)
maxs = X.max(axis=0)

scaled = (X - mins) / (maxs - mins)
```

Shapes:

```text
X      → (n_rows, n_features)
mins   → (n_features,)
maxs   → (n_features,)
scaled → (n_rows, n_features)
```

### Important edge case: constant columns

If a column has:

```text
max == min
```

then the denominator is zero.

A robust production implementation must define what to do. Options include:

- treating the constant feature as all zeros,
- dropping the feature,
- recording it as a data-quality condition,
- using a domain-specific fallback.

Do not blindly suppress the warning and continue without deciding what the business meaning is.

---

## Pattern C — Per-column normalization

For standardization:

```python
mean = X.mean(axis=0)
std = X.std(axis=0)

normalized = (X - mean) / std
```

Again, zero-standard-deviation columns need explicit handling.

---

## Pattern D — Pairwise differences

Suppose:

```python
a.shape == (N,)
b.shape == (M,)
```

You can write:

```python
pairwise = a[:, None] - b[None, :]
```

Shapes become:

```text
a[:, None] → (N, 1)
b[None, :]  → (1, M)
result      → (N, M)
```

This is extremely useful for pairwise calculations.

It is also extremely dangerous for large `N` and `M`, because the result can be enormous. We return to this in the memory section.

---

## Pattern E — Per-category rates using a lookup array

Suppose each order has an integer country code:

```text
0 → country A
1 → country B
2 → country C
```

and a lookup array contains a tax rate per country:

```python
import numpy as np

country_code = np.array([0, 2, 1, 0], dtype=np.int8)
tax_rate = np.array([0.05, 0.20, 0.10], dtype=np.float64)

order_tax_rate = tax_rate[country_code]
print(order_tax_rate)
```

Output:

```text
[0.05 0.1  0.2  0.05]
```

Then:

```python
amount = np.array([1000, 2000, 3000, 4000], dtype=np.float64)
tax = amount * order_tax_rate
```

This pattern combines:

```text
integer category code
        ↓
lookup array
        ↓
per-row rates
        ↓
vectorized arithmetic
```

The exact indexing mechanics will be covered much more deeply in Topic 03.

---

# 21. Ufunc methods: `reduce`, `accumulate`, `outer`, and `at`

A ufunc is not only callable like:

```python
np.add(a, b)
```

Selected ufuncs also expose methods that represent different computation patterns.

---

## 21.1 `reduce`

`reduce` repeatedly combines values along an axis using the ufunc operation.

Example:

```python
import numpy as np

values = np.array([1, 2, 3, 4])
print(np.add.reduce(values))
```

Output:

```text
10
```

For addition, this is conceptually similar to `sum()`.

A useful mental model is:

```text
(((1 + 2) + 3) + 4) → 10
```

For multiplication:

```python
values = np.array([2, 3, 4])
print(np.multiply.reduce(values))
```

Output:

```text
24
```

### Why use `reduce`?

It is useful when the operation itself is naturally represented by a ufunc and you want the ufunc's reduction behavior.

For ordinary sums, `np.sum` is usually clearer to readers. Learn `reduce` because it exposes the underlying ufunc model and becomes useful when you work with other binary ufuncs.

---

## 21.2 `accumulate`

`accumulate` keeps the intermediate results.

```python
import numpy as np

values = np.array([1, 2, 3, 4])
result = np.add.accumulate(values)

print(result)
```

Output:

```text
[ 1  3  6 10]
```

Conceptually:

```text
1
1 + 2        = 3
1 + 2 + 3    = 6
1 + 2 + 3 + 4= 10
```

This is useful for:

- running totals,
- cumulative counts,
- cumulative products,
- state-like numerical accumulations.

---

## 21.3 `outer`

`outer` applies the ufunc to every pair from two inputs.

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([10, 20])

result = np.multiply.outer(a, b)
print(result)
print(result.shape)
```

Output:

```text
[[10 20]
 [20 40]
 [30 60]]
(3, 2)
```

This is closely related to pairwise broadcasting.

The warning is the same: every pair means `N × M` outputs.

---

## 21.4 `at`

`ufunc.at` performs an **unbuffered in-place operation** on selected positions.

A simple accumulation example:

```python
import numpy as np

amount = np.array([10, 20, 30, 40])
labels = np.array([0, 1, 0, 1])

groups = np.zeros(2, dtype=np.int64)

np.add.at(groups, labels, amount)

print(groups)
```

Output:

```text
[40 60]
```

Why?

```text
label 0 → 10 + 30 = 40
label 1 → 20 + 40 = 60
```

Now compare plain indexed `+=` when an index repeats:

```python
a = np.zeros(3, dtype=np.int64)
idx = np.array([0, 0, 1])

a[idx] += 1
print(a)
```

Output:

```text
[1 1 0]
```

Index `0` occurs twice, but only one update is applied. The correct repeated-update behavior is:

```python
a = np.zeros(3, dtype=np.int64)
np.add.at(a, idx, 1)

print(a)
```

Output:

```text
[2 1 0]
```

`np.add.at` expresses the required unbuffered repeated updates, so repeated index `0` is incremented twice.

### Why is `at` important?

Some indexing operations use buffered behavior, which means repeated indices can produce surprising results if you expect repeated updates to accumulate one by one.

`np.add.at` explicitly represents repeated indexed updates as unbuffered operations.

### Performance note

Do not assume `np.add.at` is the fastest possible group-aggregation method for every problem. It solves a specific repeated-update semantic. Different algorithms such as sorting plus reductions or `np.bincount` can be more efficient for some datasets.

---

# 22. Pairwise broadcasting and the hidden memory problem

Now we reach one of the most important production ideas in this topic.

Consider:

```python
a[:, None] - b[None, :]
```

with:

```text
a.shape = (100_000,)
b.shape = (100_000,)
```

Broadcasting gives:

```text
a[:, None] → (100_000, 1)
b[None, :]  → (1, 100_000)
result      → (100_000, 100_000)
```

That is:

```text
10,000,000,000 elements
```

Ten billion elements.

### Memory calculation

Memory is approximately:

```text
number of elements × bytes per element
```

For `float64`:

```text
10,000,000,000 × 8 bytes
= 80,000,000,000 bytes
≈ 80 GB
```

That is only the output array.

A machine with 32 GB or 64 GB RAM cannot comfortably materialize that result.

### Important distinction

The dangerous statement is **not**:

> “Broadcasting always copies the inputs.”

Instead:

> “Broadcasting can describe a huge output shape, and the result may need to be materialized at that size.”

This distinction is central to production NumPy work.

### Example: a smaller case

```python
import numpy as np

a = np.array([1.0, 2.0, 3.0])
b = np.array([10.0, 20.0])

result = a[:, None] - b[None, :]

print(result)
print(result.shape)
```

Output:

```text
[[ -9. -19.]
 [ -8. -18.]
 [ -7. -17.]]
(3, 2)
```

The calculation is perfectly reasonable for three by two elements.

The engineering question is what happens when `3` and `2` become `100,000` and `100,000`.

---

# 23. Chunking to control memory

When a full vectorized operation would create too much output, process the problem in chunks.

### Mental model

```text
large input
    ↓
split into manageable blocks
    ↓
compute one block
    ↓
consume/store/reduce result
    ↓
next block
    ↓
...
```

### Example: chunked pairwise distances

Suppose:

```python
x.shape == (N,)
y.shape == (M,)
```

and you need pairwise absolute differences, but cannot afford a full `N × M` array.

```python
import numpy as np


def pairwise_abs_difference_chunked(x, y, chunk_size=10_000):
    results = []

    for start in range(0, len(x), chunk_size):
        stop = min(start + chunk_size, len(x))
        block = np.abs(x[start:stop, None] - y[None, :])
        results.append(block)

    return np.concatenate(results, axis=0)
```

This example still ultimately stores the full result because it returns the concatenated matrix. That is fine only when the **final** result itself fits in memory.

A better production design often consumes each chunk immediately:

```python
for start in range(0, len(x), chunk_size):
    stop = min(start + chunk_size, len(x))
    block = np.abs(x[start:stop, None] - y[None, :])

    # Consume block here:
    # write it, reduce it, score it, aggregate it, etc.
```

Now peak memory is approximately tied to the chosen chunk size instead of the whole `N × M` result.

### Choosing a chunk size

There is no universal “correct” chunk size.

Consider:

- available RAM,
- dtype size,
- number of simultaneous arrays,
- output width,
- downstream processing,
- CPU/cache behavior,
- I/O characteristics.

The trade-off is:

```text
larger chunks
→ fewer iterations
→ often better throughput
→ more memory

smaller chunks
→ lower peak memory
→ more iterations
→ potentially more overhead
```

Measure representative values rather than guessing.

---

# 24. Temporary arrays

This expression looks compact:

```python
result = a * b + c
```

But it can conceptually involve:

```text
temporary = a * b
result    = temporary + c
```

If `a`, `b`, and `c` are very large arrays, the temporary can substantially increase peak memory.

### Example

Suppose three arrays each contain:

```text
100 million float64 values
```

One array is roughly:

```text
100,000,000 × 8 bytes = 800,000,000 bytes ≈ 0.8 GB
```

A calculation that needs multiple simultaneous arrays can require several gigabytes even though the final result is only one array.

### Important engineering principle

> **Concise code and low peak memory are not the same property.**

Do not rewrite every expression into low-level form. First measure whether temporary allocations are actually a bottleneck.

---

# 25. Reducing temporary allocations with `out=`

Many NumPy operations accept an `out=` argument.

Instead of:

```python
result = np.multiply(a, b)
```

you can sometimes do:

```python
result = np.empty_like(a)
np.multiply(a, b, out=result)
```

Now you provide the destination storage explicitly.

### Multi-step example

Suppose:

```python
result = a * b + c
```

The first form can require a temporary for `a * b` and a separate allocation for the final result.

You can instead write:

```python
t = np.multiply(a, b)
np.add(t, c, out=t)
result = t
```

Here `t` is reused for the second step.

The key idea is storage reuse:

```text
inputs
  ↓
ufunc
  ↓
preallocated output
```

### When `out=` is useful

- very large arrays,
- repeated operations in a pipeline,
- controlled memory allocation,
- hot numerical kernels.

### Important constraints

The output array must be compatible with the operation's shape and dtype requirements. You must also understand whether aliasing inputs and outputs is safe for the specific operation.

`out=` is an optimization tool, not a magic switch that guarantees lower peak memory for every expression.

---

# 26. In-place operations

In-place operators such as:

```python
a += 1
a *= 2
```

modify an existing array rather than assigning a new array object for the transformed values.

Example:

```python
import numpy as np

a = np.array([1, 2, 3], dtype=np.int64)
a += 10

print(a)
```

Output:

```text
[11 12 13]
```

### Why in-place operations can help

They can avoid allocating a separate result array when the original storage can safely be reused.

### Why in-place operations can be dangerous

They mutate the input.

If another part of your program expects the original values, an in-place operation can cause a correctness bug.

The production trade-off is:

```text
less allocation / less memory
        vs
mutation / aliasing risk
```

Topic 06 will go deeply into views and copies. For now, remember the basic safety question:

> **Is the input allowed to change?**

If not, do not use an in-place update blindly.

---

## 27. In-place dtype pitfalls

Suppose:

```python
import numpy as np

values = np.array([1, 2, 3], dtype=np.int64)
values += 0.5
```

This is not equivalent to silently turning `values` into floating point.

The in-place operation must write the result back into the existing integer array, and NumPy's casting rules do not allow the floating-point result to be stored as `int64` under the normal in-place operation semantics.

You should expect a casting-related error rather than automatic promotion of the array's dtype.

If floating-point values are required, create an appropriate floating array explicitly:

```python
values = np.array([1, 2, 3], dtype=np.float64)
values += 0.5

print(values)
```

Output:

```text
[1.5 2.5 3.5]
```

### Engineering lesson

In-place operations make storage reuse explicit, so dtype compatibility matters more visibly.

---

# 28. `np.vectorize` is not genuine vectorization

A very common misconception is:

```python
fast_function = np.vectorize(my_function)
```

therefore:

```text
my_function → converted into a fast NumPy kernel
```

That is not what `np.vectorize` does.

NumPy documents `np.vectorize` as a convenience wrapper that applies a Python function element by element, using broadcasting rules for the inputs. It provides vectorized-looking syntax, but does not transform arbitrary Python code into a native high-performance ufunc.

### Example

```python
import numpy as np


def classify(x):
    return "high" if x >= 100 else "normal"

values = np.array([50, 100, 150])
classify_vectorized = np.vectorize(classify)

print(classify_vectorized(values))
```

This is convenient. But it should not be described as a performance optimization comparable to replacing a Python loop with a genuine NumPy ufunc.

### What it is good for

- convenience,
- adapting a small Python function to array-shaped inputs,
- prototyping logic when no native vectorized expression exists.

### What it is not

It is not equivalent to:

```text
Python function
→ compiled NumPy kernel
```

### Benchmarking the misconception

A useful lab is to compare:

```text
1. Python loop
2. np.vectorize
3. genuine NumPy expression
```

For example:

```python
import time
import numpy as np


def square_python(x):
    return x * x

values = np.arange(1_000_000, dtype=np.int64)

start = time.perf_counter()
loop_result = np.array([square_python(x) for x in values])
loop_time = time.perf_counter() - start

square_vectorized = np.vectorize(square_python)
start = time.perf_counter()
vectorize_result = square_vectorized(values)
vectorize_time = time.perf_counter() - start

start = time.perf_counter()
numpy_result = values * values
numpy_time = time.perf_counter() - start

np.testing.assert_array_equal(loop_result, vectorize_result)
np.testing.assert_array_equal(loop_result, numpy_result)

print("loop     ", loop_time)
print("vectorize", vectorize_time)
print("numpy    ", numpy_time)
```

Exact timings depend on your machine and NumPy/Python versions, so do not put fixed timing numbers into tests.

The important result is conceptual: `np.vectorize` retains Python-level function calls; a genuine array expression such as `values * values` uses NumPy's native implementation of multiplication.

---

# 29. `np.apply_along_axis` is also not genuine vectorization

`np.apply_along_axis` can be convenient when you have a Python callable that you want to apply to one-dimensional slices of an array.

For example:

```python
import numpy as np

X = np.array(
    [
        [1, 2, 3],
        [4, 5, 6],
    ]
)


def value_range(row):
    return row.max() - row.min()

result = np.apply_along_axis(value_range, axis=1, arr=X)
print(result)
```

Output:

```text
[2 2]
```

This can be useful as a convenience API.

But it should not be interpreted as:

```text
arbitrary Python function
→ automatically converted into a native vectorized kernel
```

The callable is still executed repeatedly for slices.

### When it may be useful

- rapid prototyping,
- convenience for functions that already work on one-dimensional slices,
- readable code when performance is not the main concern.

### When performance matters

Ask whether the operation can instead be expressed using:

- built-in NumPy reductions,
- ufuncs,
- broadcasting,
- matrix/array operations,
- other native NumPy primitives.

Benchmark before and after.

---

# 30. Floating-point behavior in vectorized code

Vectorization changes how you express a computation. It does not remove the limitations of floating-point arithmetic.

You must still reason about:

- `nan`,
- `inf`,
- `-inf`,
- division by zero,
- invalid mathematical operations,
- rounding and accumulated error.

### 30.1 Division by zero

Use floating arrays when demonstrating IEEE-style floating-point behavior:

```python
import numpy as np

x = np.array([1.0, 2.0, 0.0])
y = np.array([0.0, 0.0, 0.0])

result = x / y
print(result)
```

You should see `inf` values for positive nonzero values divided by zero, along with NumPy's floating-point warning behavior for the operation.

The exact warning display can vary by environment, but the resulting values are the important part.

### 30.2 Invalid operations

```python
import numpy as np

x = np.array([-1.0, 0.0, 1.0])
result = np.sqrt(x)

print(result)
```

The negative element produces `nan`, while valid nonnegative values produce finite results.

### 30.3 Logarithm of zero

```python
import numpy as np

x = np.array([0.0, 1.0, 10.0])
result = np.log(x)

print(result)
```

The zero input produces `-inf`.

### Engineering lesson

Do not equate “the operation completed” with “the data is valid.”

A vectorized transformation can produce a perfectly valid NumPy array that contains values your downstream business process cannot accept.

---

# 31. `np.errstate`

`np.errstate` lets you control how NumPy handles floating-point exceptions for a block of code.

The relevant categories include:

- `divide`,
- `over`,
- `under`,
- `invalid`.

### Basic example

```python
import numpy as np

x = np.array([1.0, 0.0])

with np.errstate(divide="ignore", invalid="ignore"):
    result = x / x

print(result)
```

The resulting values can still contain `nan` or other exceptional values. The context changes error handling behavior; it does **not** repair the numerical data.

### Why this matters

You may decide that a particular calculation is expected to produce special values and want explicit downstream handling rather than noisy warnings.

For example:

```python
with np.errstate(divide="ignore", invalid="ignore"):
    ratio = numerator / denominator

bad = ~np.isfinite(ratio)
```

Now you can inspect the exceptional results explicitly.

### Important engineering principle

> **Suppressing a floating-point warning is not the same as fixing the underlying data.**

Bad pattern:

```python
with np.errstate(all="ignore"):
    result = complicated_expression(data)
```

with no follow-up validation.

Better pattern:

```python
with np.errstate(divide="ignore", invalid="ignore"):
    result = numerator / denominator

invalid = ~np.isfinite(result)

# Decide what the pipeline should do with invalid values.
```

This connects directly to the missing-value and quality-validation work in later topics.

---

# 32. Debugging vectorization and broadcasting problems

When a vectorized calculation looks wrong, do not stare at the expression. Inspect the arrays.

Start with:

```python
print(a.shape)
print(b.shape)
print(a.dtype)
print(b.dtype)
print(a.ndim)
print(b.ndim)
```

For broadcasting questions:

```python
print(np.broadcast_shapes(a.shape, b.shape))
```

For deeper exploration:

```python
broadcast = np.broadcast(a, b)
print(broadcast.shape)
```

---

## Bug 1 — unexpected `(n, n)` result

### Symptom

You expected a vector of length `n`, but received a matrix of shape `(n, n)`.

### Typical cause

A pairwise broadcast such as:

```python
a[:, None] - b[None, :]
```

was unintentionally created.

### Diagnosis

```python
print(a.shape)
print(b.shape)
print(a[:, None].shape)
print(b[None, :].shape)
```

### Prevention rule

Before adding a dimension, write down the intended result shape.

---

## Bug 2 — `(n,)` vs `(n, 1)` confusion

### Symptom

An operation produces a shape you did not expect.

Example:

```python
import numpy as np

x = np.array([1, 2, 3])
y = np.array([10, 20])

print((x[:, None] + y[None, :]).shape)
```

Result:

```text
(3, 2)
```

That is correct pairwise broadcasting.

If your business logic expected element-by-element addition, your shape design is wrong.

### Prevention rule

Always label your dimensions conceptually:

```text
(n_records,)
(n_features,)
(n_records, n_features)
```

Then reshape deliberately.

---

## Bug 3 — accidental broadcasting silently succeeds

Some bugs are more dangerous than exceptions because the calculation succeeds.

Suppose:

```python
row_values.shape == (1000,)
column_values.shape == (1000, 1)
```

You wanted an element-by-element result of 1,000 values.

Writing:

```python
row_values * column_values
```

succeeds. NumPy interprets the first operand as `(1, 1000)`:

```text
(1,    1000)
(1000, 1)
```

and produces:

```text
(1000, 1000)
```

rather than the intended 1,000-element result. That is one million elements instead of one thousand, with no error.

A compact fix:

```python
result = row_values * column_values.ravel()
```

The important idea is to make the intended dimension explicit and check the result shape.

---

## Bug 4 — `inf` or `nan` appears

### Symptom

A pipeline suddenly contains non-finite values.

### Inspect

```python
bad = ~np.isfinite(result)
print("bad count:", np.count_nonzero(bad))
```

Separate the cases:

```python
print("nan:", np.count_nonzero(np.isnan(result)))
print("inf:", np.count_nonzero(np.isinf(result)))
```

### Root causes

Common examples:

- zero denominators,
- logarithm of zero,
- invalid square roots,
- overflow,
- upstream missing or corrupt data.

### Prevention rule

Do not hide the warning and stop there. Define how exceptional values should be handled.

---

## Bug 5 — huge temporary array

### Symptom

Memory usage spikes during an expression.

### Example

```python
result = a[:, None] - b[None, :]
```

### Inspect

```python
print("result shape:", result.shape)
print("elements:", result.size)
print("bytes:", result.nbytes)
```

### Fix

Choose among:

- chunking,
- reduction without storing the full matrix,
- a different algorithm,
- a database/columnar/distributed engine for larger-scale processing.

---

## Bug 6 — `np.vectorize` assumed to be fast

### Symptom

Someone replaces a Python loop with `np.vectorize` and expects a large speed-up.

### Diagnosis

Benchmark:

```text
Python loop
np.vectorize
native NumPy expression
```

### Prevention rule

Ask:

> “What NumPy primitive actually implements this operation?”

Use that primitive when one exists.

---

# 33. Benchmarking: measure before optimizing

A production engineer should never say:

> “This is vectorized, so it is definitely faster.”

Measure it.

The roadmap requires realistic sizes, not ten-element toy inputs.

### Timing with `time.perf_counter`

```python
import time
import numpy as np

values = np.arange(5_000_000, dtype=np.float64)

start = time.perf_counter()
loop_result = [x * 2.0 for x in values]
loop_time = time.perf_counter() - start

start = time.perf_counter()
vectorized_result = values * 2.0
vectorized_time = time.perf_counter() - start

print("loop:", loop_time)
print("vectorized:", vectorized_time)
print("speedup:", loop_time / vectorized_time)
```

This benchmark demonstrates the workflow, but exact timings depend on the machine, Python version, NumPy version, CPU, and system load.

### Timing with `timeit`

For repeated small computations, `timeit` can be convenient:

```python
import timeit

loop_time = timeit.timeit(
    "[x * 2 for x in values]",
    setup="values = range(100_000)",
    number=10,
)
```

For larger array workloads, `perf_counter` around the operation can be straightforward and readable.

### Benchmark design checklist

Use:

```text
small input
→ correctness

large input
→ performance
```

Watch out for:

- timing data creation instead of the operation,
- including file I/O when you are trying to measure computation,
- extremely tiny arrays,
- one-time initialization effects,
- different workloads between versions,
- measuring only one noisy execution.

The goal is not to produce an impressive number. The goal is to make a trustworthy comparison.

---

# 34. Testing vectorized code

The safest way to build vectorized transformations is to keep a simple reference implementation.

### Step 1 — tiny input

```python
quantities = [2, 5, 3]
prices = [100, 250, 400]
```

### Step 2 — Python reference

```python
reference = []
for q, p in zip(quantities, prices):
    reference.append(q * p)
```

### Step 3 — NumPy implementation

```python
import numpy as np

vectorized = np.array(quantities) * np.array(prices)
```

### Step 4 — compare

```python
np.testing.assert_array_equal(reference, vectorized)
```

For floating-point results:

```python
np.testing.assert_allclose(reference, vectorized)
```

### Why both tools?

Integer arithmetic can often be checked exactly.

Floating-point computations may differ by very small amounts because of representation and operation ordering, so tolerance-based comparison is usually more appropriate.

---

# 35. Required edge cases for vectorized transformations

At minimum, test:

- empty arrays,
- one-element arrays,
- zero values,
- negative values where valid,
- very large values,
- mismatched shapes,
- divide-by-zero cases,
- `nan`,
- `inf`.

### Empty array example

```python
import numpy as np

empty = np.array([], dtype=np.float64)
result = empty * 2

print(result.shape)
print(result.dtype)
```

Expected shape:

```text
(0,)
```

### One element

```python
x = np.array([5])
print(x * 2)
```

### Non-finite values

```python
x = np.array([1.0, np.nan, np.inf])
print(x * 2)
```

The `nan` and `inf` values demonstrate that vectorization propagates numerical states according to the operation's floating-point semantics.

---

# 36. Hands-on exercise — `vectorized_transforms.py`

This is the production-style exercise required by the Module 2.2 roadmap.

**Roadmap practice step:** Convert five loop-based functions from your Stage 1 projects into vectorized NumPy versions.

## Scenario

You have **5,000,000 generated order records**.

Use the conceptual dataset from Topic 01. The dataset should contain at least:

```text
quantity
unit_price_cents
country_code
four numeric features
```

Use NumPy's modern random generator:

```python
rng = np.random.default_rng(42)
```

Generate deterministic test data so your correctness experiments are reproducible.

### Important constraints

The exercise is designed to teach:

```text
reference loop
    ↓
vectorized implementation
    ↓
correctness comparison
    ↓
shape reasoning
    ↓
benchmark
    ↓
memory reasoning
```

---

## Task 1 — line totals

Compute:

```text
line_total_cents = quantity × unit_price_cents
```

### Starter specification

Use suitable integer dtypes based on the range of values.

The maximum business values are `quantity = 500` and `unit_price_cents = 10,000,000`, so the maximum product is:

```text
500 × 10,000,000 = 5,000,000,000
```

This does not fit in `uint32`, so the NumPy multiplication must use `dtype=np.int64`.

Write a pure-Python reference version first.

Then write the NumPy version.

Example reference structure:

```python
reference = []
for q, price in zip(quantity.tolist(), unit_price_cents.tolist()):
    reference.append(q * price)
```

Vectorized form:

```python
line_total_cents = np.multiply(
    quantity,
    unit_price_cents,
    dtype=np.int64,
)
```

### Requirements

- compare the outputs,
- inspect the result dtype,
- reason about integer overflow explicitly (maximum product `5,000,000,000`),
- benchmark both implementations.

---

## Task 2 — country tax rates

Create a lookup array such as:

```python
tax_rates = np.array([0.05, 0.10, 0.15, 0.20], dtype=np.float64)
```

Generate integer country codes between `0` and `3`.

Map:

```text
country_code → tax rate
```

using an array lookup, not pandas.

Example pattern:

```python
order_tax_rate = tax_rates[country_code]
```

Then calculate tax:

```python
tax_amount = line_total_cents * order_tax_rate
```

### Requirements

- explain the lookup shape,
- explain the resulting rate-array shape,
- verify the first few values manually,
- compare to a tiny Python reference implementation.

---

## Task 3 — order size buckets

Classify orders as:

```text
small
medium
large
```

Use `np.select`.

For example, define thresholds such as:

```text
small  < 1,000 cents
medium < 5,000 cents
large  otherwise
```

Example structure:

```python
conditions = [
    line_total_cents < 1_000,
    line_total_cents < 5_000,
]

choices = ["small", "medium"]

bucket = np.select(conditions, choices, default="large")
```

### Requirements

Test boundary values explicitly:

```text
999
1000
4999
5000
```

This is a common production pattern: always test values exactly at the boundary.

---

## Task 4 — column-wise min-max scaling

Create:

```text
features.shape = (n_rows, 4)
```

Compute column-wise scaling:

```python
mins = features.min(axis=0)
maxs = features.max(axis=0)

scaled = (features - mins) / (maxs - mins)
```

### Requirements

Before running the code, write down:

```text
features.shape
mins.shape
maxs.shape
scaled.shape
```

Then verify them in Python.

### Edge case

Introduce a constant column where:

```text
min == max
```

Decide how your implementation should handle it.

Your decision should be documented in a comment or explanatory Markdown text.

---

## Task 5 — benchmark every loop/vectorized pair

Create a benchmark table with these columns:

| Operation | Loop time | Vectorized time | Speedup |
|---|---:|---:|---:|
| Line total | measured | measured | calculated |
| Tax calculation | measured | measured | calculated |
| Bucket classification | measured | measured | calculated |
| Feature scaling | measured | measured | calculated |

Do not hard-code timing values.

Use:

```python
import time
```

or:

```python
import timeit
```

### Speed-up formula

```text
speedup = loop_time / vectorized_time
```

A speed-up larger than `1` means the vectorized implementation took less time under that benchmark.

Do not report the benchmark as a universal law. It describes the workload and machine on which you measured it.

---

## Task 6 — correctness

For integer outputs:

```python
np.testing.assert_array_equal(reference, vectorized)
```

For floating-point outputs:

```python
np.testing.assert_allclose(reference, vectorized)
```

Test:

- normal input,
- empty input,
- one-element input,
- zero amounts,
- large amounts,
- boundary buckets,
- invalid denominator for min-max scaling,
- non-finite input if your transform permits it.

---

# 37. Mini benchmark lab: why `np.vectorize` is different

Use a small pure-Python function that performs a scalar transformation.

```python
import time
import numpy as np


def classify_scalar(value):
    return "high" if value >= 100 else "normal"

values = np.arange(1_000_000)

start = time.perf_counter()
loop_result = np.array([classify_scalar(x) for x in values])
loop_time = time.perf_counter() - start

classify_vectorized = np.vectorize(classify_scalar)

start = time.perf_counter()
wrapped_result = classify_vectorized(values)
wrapped_time = time.perf_counter() - start

start = time.perf_counter()
native_result = np.where(values >= 100, "high", "normal")
native_time = time.perf_counter() - start

print("loop:", loop_time)
print("np.vectorize:", wrapped_time)
print("native np.where:", native_time)

np.testing.assert_array_equal(loop_result, wrapped_result)
np.testing.assert_array_equal(loop_result, native_result)
```

Again, do not expect identical timings on different machines.

The important lesson is architectural:

```text
Python scalar function
→ repeated Python execution

np.vectorize
→ convenient repeated Python execution

np.where
→ genuine NumPy array operation
```

---

# 38. Production memory reasoning

When reviewing a vectorized pipeline, ask two separate questions:

## Compute efficiency

```text
How much Python-level work is being avoided?
```

## Memory efficiency

```text
How many arrays exist simultaneously, and how large are they?
```

A calculation can be fast but memory-hungry.

For example:

```python
result = a[:, None] - b[None, :]
```

may use a highly optimized numerical operation while still failing because the output is too large.

### A useful review template

For every large transformation write:

```text
input shapes:
input dtypes:
expected output shape:
expected output dtype:
estimated output bytes:
known temporaries:
peak-memory risk:
chunking required?
```

This is the numerical equivalent of doing a capacity check before deploying a service.

---

# 39. Production Data Engineering use cases

## 39.1 Order and transaction processing

```python
line_total = quantity * unit_price
```

Typical concerns:

- integer overflow,
- currency representation,
- memory size,
- validation of negative values.

## 39.2 Tax or exchange-rate application

```python
tax = amount * tax_rate_by_row
```

The row-level rate can be produced by a lookup array.

## 39.3 Sensor calibration

```python
corrected = raw_values * gain + offset
```

Broadcasting can apply one gain/offset per sensor channel across a batch.

## 39.4 Quality thresholds

```python
is_outlier = np.abs(error) > threshold
```

This creates an element-wise quality flag array.

## 39.5 Feature preparation

```python
scaled = (X - mins) / (maxs - mins)
```

This is common before downstream ML computation.

## 39.6 Batch scoring

A model or numerical scoring formula can operate on a whole batch rather than Python row-by-row logic.

## 39.7 Aggregated pipeline metrics

Cumulative operations and element-wise transformations can build monitoring statistics before the data reaches a DataFrame or warehouse.

### The production trade-off

```text
Vectorization
→ often less Python overhead
→ often high throughput
→ concise array expressions
→ but possible large outputs
→ possible temporary allocations
→ numerical errors still exist
```

A good Data Engineer optimizes **compute and memory together**.

---

# 40. Common mistakes

## Mistake 1 — accidental `N × N` broadcasting

**Why it happens:** adding `None` or `newaxis` without calculating the final shape.

**Example:**

```python
result = a[:, None] - b[None, :]
```

**Correct approach:** calculate `N × M` before execution and choose chunking if needed.

**Prevention:** always write input shapes and expected output shape first.

---

## Mistake 2 — confusing `(n,)` and `(n, 1)`

**Why it happens:** a one-dimensional array does not visually communicate whether the values should represent rows or columns.

**Correct approach:** use `[:, None]`, `[None, :]`, or explicit `reshape`.

**Prevention:** document your shape conventions.

---

## Mistake 3 — assuming `np.vectorize` is fast

**Why it happens:** the name contains “vectorize.”

**Correct approach:** find a native NumPy primitive when one exists.

**Prevention:** benchmark loop vs `np.vectorize` vs true array expression.

---

## Mistake 4 — using `and` / `or` for array conditions

**Bad:**

```python
(a > 10) and (a < 20)
```

**Good:**

```python
(a > 10) & (a < 20)
```

Use parentheses around each comparison.

---

## Mistake 5 — assuming concise expressions have low peak memory

**Why it happens:** intermediate arrays are not visible in the source code.

**Correct approach:** reason about temporaries and measure memory if needed.

**Prevention:** use `out=`, controlled in-place updates, or chunking where profiling demonstrates a need.

---

## Mistake 6 — large pairwise calculation without chunking

**Why it happens:** the small example works perfectly.

**Correct approach:** extrapolate `result.size` and `result.nbytes` to production dimensions before running the operation.

---

## Mistake 7 — mutating an input with in-place operations

**Why it happens:** `+=` looks harmless.

**Correct approach:** confirm that mutation is part of the function contract.

---

## Mistake 8 — suppressing warnings without defining behavior

**Why it happens:** warnings make a pipeline noisy.

**Correct approach:** use `np.errstate` only as part of an explicit error-handling policy and validate the resulting values.

---

## Mistake 9 — benchmarking only ten elements

**Why it happens:** toy examples are convenient.

**Correct approach:** use small datasets for correctness and realistic large datasets for performance conclusions.

---

# 41. A production review checklist

Before approving a large NumPy transformation, review it with these questions:

### Shape

- What are the input shapes?
- Is every broadcast intentional?
- What is the exact output shape?

### Dtype

- What is the input dtype?
- What will the output dtype be?
- Could arithmetic overflow?
- Could floating-point precision matter?

### Memory

- How many arrays exist at once?
- Does the expression create temporaries?
- What is the output's `nbytes`?
- Could broadcasting create a huge matrix?
- Would chunking bound peak memory?

### Numerical correctness

- Can the operation produce `nan` or `inf`?
- What should happen for division by zero?
- Are constant columns possible?
- Is tolerance-based testing needed?

### Mutation

- Is in-place modification allowed?
- Does downstream code depend on the original input?

### Performance

- Was the workload benchmarked?
- Is the benchmark realistic?
- Are you measuring only the operation you intended to compare?

---

# 42. Checkpoint — self-test

Do not look at answers while taking this checkpoint. Write your reasoning down first.

## Question 1

State the three broadcasting rules from memory.

## Question 2

Predict the shape:

```text
(5, 1, 3) + (4, 3)
```

Explain each aligned dimension.

## Question 3

Predict the shape:

```text
(8, 1, 6, 1) + (7, 1, 5)
```

Do not run the code until you have written your answer.

## Question 4

Why does this produce a matrix?

```python
a[:, None] - b[None, :]
```

What is the result shape when:

```text
a.shape = (100_000,)
b.shape = (100_000,)
```

## Question 5

Why is this statement incorrect?

> “Broadcasting always copies the smaller array.”

## Question 6

What is the difference between:

```python
x[:, None]
x[None, :]
```

for `x.shape == (5,)`?

## Question 7

When would you use:

```python
np.where
```

rather than:

```python
np.select
```

## Question 8

Give one case where `np.clip` is a more natural expression than `np.where`.

## Question 9

What does this do?

```python
np.add.accumulate([1, 2, 3, 4])
```

## Question 10

What does `np.add.at` provide that ordinary indexed assignment does not reliably express for repeated indexed updates?

## Question 11

Why can this be memory-dangerous?

```python
a[:, None] - b[None, :]
```

## Question 12

Name two ways to reduce peak memory in a large NumPy transformation.

## Question 13

Why can `a * b + c` consume more memory than the final result alone suggests?

## Question 14

What is the purpose of `out=`?

## Question 15

Why can `a += 0.5` fail when `a` is an integer array?

## Question 16

Why is `np.vectorize` not equivalent to a native NumPy ufunc?

## Question 17

Why is `np.apply_along_axis` not a general solution for high-performance vectorization?

## Question 18

What is the difference between `inf` and `nan` at a high level?

## Question 19

What categories can `np.errstate` control?

## Question 20

Why should a production engineer benchmark vectorized code instead of assuming it is faster?

### Checkpoint exit criterion

You are ready to move forward when you can answer these questions **without looking at the chapter**, and explain the reasoning rather than only giving a final shape or definition.

---

# 43. Final mental model

Use this hierarchy when reasoning about NumPy transformations:

```text
Array
  ↓
Vectorized operation
  ↓
Ufunc / array primitive
  ↓
Element-wise computation
  ↓
Broadcasting
  ↓
Shape alignment
  ↓
Result shape
  ↓
Result allocation
  ↓
Potential temporaries
  ↓
Peak memory
  ↓
Performance
```

The most important production mental model is:

```text
Do not start with:
“How do I write the loop?”

Start with:
“What array operation describes the computation?”

Then ask:
“What are the shapes?”
“What will broadcast?”
“What will be allocated?”
“What numerical edge cases exist?”
“How will I test it?”
“How will I benchmark it?”
```

---

# 44. The engineering questions to ask before writing a NumPy transformation

Before committing a large transformation, ask:

```text
1. Can this be expressed as a ufunc or another native NumPy array operation?
2. What are the input shapes?
3. What will the output shape be?
4. Will broadcasting occur?
5. Could broadcasting create a huge output?
6. Will intermediate arrays be created?
7. Can out= reduce allocations?
8. Is in-place mutation safe?
9. Is chunking required?
10. How will floating-point errors be handled?
11. Have I benchmarked the implementation?
```

This checklist turns NumPy from “syntax I remember” into an engineering discipline.

---

# 45. Connection to Topic 03 — Indexing, Boolean Masks, and Fancy Indexing

Topic 02 taught you how to **compute on arrays**.

The next topic teaches you how to **select the right data from those arrays**.

The dependency chain is:

```text
01 ndarray / dtype / memory layout
            ↓
02 vectorization / broadcasting
            ↓
03 indexing / boolean masks / fancy indexing
            ↓
04 aggregations / axis semantics
            ↓
05 missing values
            ↓
06 views / copies / memory efficiency
```

This order matters.

You first need to understand that NumPy expressions operate over whole arrays. Then you need to understand how to select subsets of those arrays efficiently.

For example, Topic 03 will build directly on comparisons from this chapter:

```python
mask = amount > 1000
```

That boolean array becomes a selection mechanism:

```python
filtered = amount[mask]
```

You will also learn how indexing interacts with views and copies, which connects back to the memory reasoning introduced here.

---

# 46. Summary table

| Concept | Core idea | Data Engineering relevance |
|---|---|---|
| Vectorization | Express a supported computation over an array rather than writing Python element loops. | Faster batch transformations for large homogeneous numeric data. |
| Ufunc | NumPy element-wise operation with array-aware semantics. | Arithmetic and mathematical transformations. |
| `np.where` | Two-way element-wise conditional selection. | Flags and two-outcome rules. |
| `np.select` | Multiple ordered conditions. | Business-rule classification. |
| `np.clip` | Enforce numerical lower/upper bounds. | Capping and bounded transformations. |
| Broadcasting | Align compatible shapes for array operations. | Per-column/per-row parameters and batch transforms. |
| `newaxis` / `None` | Add a dimension of size 1. | Explicit shape control for broadcasting. |
| `reshape` | Change array shape without changing the element count. | Make row/column semantics explicit. |
| `reduce` | Collapse values using a ufunc. | Ufunc-level aggregation reasoning. |
| `accumulate` | Keep cumulative intermediate values. | Running totals and cumulative metrics. |
| `outer` | Apply a ufunc to all pairs. | Pairwise calculations; potentially memory-heavy. |
| `at` | Perform unbuffered indexed updates. | Repeated indexed accumulation. |
| Chunking | Process data in bounded blocks. | Controls peak memory. |
| `out=` | Write an operation into preallocated storage. | Reduce allocations when appropriate. |
| In-place ops | Update an existing array. | Lower allocation at the cost of mutation risk. |
| `np.vectorize` | Convenience wrapper around repeated Python calls. | Useful for convenience, not a native-performance substitute. |
| `np.apply_along_axis` | Apply a Python callable to array slices. | Convenience/prototyping; not automatic native vectorization. |
| `np.errstate` | Control NumPy floating-point error handling. | Intentional handling of divide/overflow/invalid conditions. |

---

# 47. Practical completion checklist

Before marking Topic 02 complete, you should be able to demonstrate all of the following from memory or by reasoning:

- [ ] I can explain vectorization without saying that NumPy “removes all loops.”
- [ ] I can explain why large Python numerical loops can be slower than native NumPy operations.
- [ ] I can identify common ufuncs and use them in realistic transformations.
- [ ] I can use `np.where`, `np.select`, and `np.clip` correctly.
- [ ] I can state the three broadcasting rules.
- [ ] I can predict broadcasting result shapes manually.
- [ ] I can verify a shape with `np.broadcast_shapes`.
- [ ] I understand `(n,)`, `(n, 1)`, and `(1, n)` as different shapes.
- [ ] I can use `np.newaxis`, `None`, and `reshape` to express intended dimensions.
- [ ] I can explain column centering and min-max scaling through broadcasting.
- [ ] I can explain the pairwise broadcast pattern.
- [ ] I understand why a pairwise broadcast can create an enormous result.
- [ ] I can use chunking to control memory.
- [ ] I can explain temporary arrays and peak memory.
- [ ] I understand the purpose of `out=`.
- [ ] I can explain the benefits and risks of in-place operations.
- [ ] I understand why integer arrays may reject floating-point in-place updates.
- [ ] I can explain why `np.vectorize` is not genuine vectorization.
- [ ] I can explain why `np.apply_along_axis` is not an automatic performance optimizer.
- [ ] I can identify `nan` and `inf` outcomes in numerical transformations.
- [ ] I can use `np.errstate` without confusing warning suppression with data validation.
- [ ] I can debug shape and broadcasting problems systematically.
- [ ] I can benchmark loop and vectorized implementations with realistic input sizes.
- [ ] I can test a vectorized implementation against a simple reference implementation.
- [ ] I have completed the `vectorized_transforms.py` exercise specification.

---

# 48. Reference notes

For continued study, use the NumPy documentation for the exact version installed in your project. The most relevant areas are:

- NumPy broadcasting documentation
- NumPy universal-function documentation
- `numpy.vectorize`
- `numpy.apply_along_axis`
- `numpy.errstate`
- NumPy reference documentation for ufunc methods

When NumPy behavior changes between major versions, prefer the documentation for the version actually installed in the project rather than relying on older examples from memory.

---

## Final takeaway

A production NumPy engineer thinks in **arrays, shapes, kernels, allocations, and correctness** rather than rows alone.

The sequence to internalize is:

```text
Python loop
    ↓
array expression
    ↓
ufunc / native NumPy primitive
    ↓
broadcast shapes intentionally
    ↓
predict the output
    ↓
check memory
    ↓
handle numerical edge cases
    ↓
test against a reference
    ↓
benchmark realistically
```

When these habits become automatic, NumPy stops feeling like a collection of syntax tricks and starts behaving like an engineering tool for high-throughput numerical data processing.
