# Stage 2 — Python for Data Engineering
# Module 2.2 — Numerical Computing with NumPy
# Practice Questions

## Purpose

This workbook is the consolidation and applied-practice set for the complete Module 2.2 — Numerical Computing with NumPy. It is designed to test whether you can **reason about NumPy arrays before executing code**, implement correct transformations, break edge cases, measure performance and memory behavior, and explain production trade-offs.

The set contains exactly **32 independent questions**:

- **8 Basic** — individual concepts
- **8 Moderate** — combinations of concepts
- **8 Hard** — realistic multi-step Data Engineering problems
- **8 Advanced** — production-oriented engineering decisions under constraints

Every problem is followed immediately by its **Solution / How to Solve** so that you can compare your reasoning after attempting the problem.

### Recommended learning loop

```text
Predict
→ Implement
→ Verify
→ Break edge cases
→ Measure
→ Explain
```

### How to use this workbook

1. Read only the **Problem** first.
2. Write down the input shape, dtype, expected output shape, and any view/copy or memory behavior you expect.
3. Attempt the implementation independently.
4. Verify with assertions or explicit checks.
5. Test at least one relevant edge case.
6. Read the provided solution and compare the reasoning, not only the code.
7. Re-solve the problem without looking at the solution.

For difficult and advanced questions, explain your design decision aloud as if you were reviewing a production pipeline.

---

# Basic — Questions 01–08

## Question 01 — Audit an Array's Physical Footprint

**Difficulty:** Basic

**Topics tested:** `ndarray`, `shape`, `ndim`, `size`, `dtype`, `itemsize`, `nbytes`, dtype memory reasoning.

### Problem

A data-ingestion step produces this array:

```python
import numpy as np

events = np.array(
    [
        [101, 250, 1],
        [102, 400, 2],
        [103, 125, 3],
        [104, 900, 4],
    ],
    dtype=np.int32,
)
```

Before the pipeline continues, you must document its physical representation.

### What you need to determine/build

Determine:

1. `ndim`
2. `shape`
3. `size`
4. `dtype`
5. `itemsize`
6. `nbytes`
7. whether the array is C-contiguous
8. the raw number of bytes occupied by the numerical elements

Then explain how the raw storage would change if the same values were stored as `int64`.

### Constraints / assumptions

- Use NumPy only.
- Do not estimate memory from the Python syntax.
- Show the calculations explicitly.

### Expected skills

- Reading ndarray metadata.
- Connecting element count and dtype width to memory.
- Reasoning about why dtype selection matters at scale.

### Solution / How to Solve

#### Step 1 — Understand the problem

There are 4 rows and 3 columns, so the array contains 12 integer elements.

#### Step 2 — Predict shape/dtype/memory behavior

Because the array is explicitly `int32`:

- `ndim = 2`
- `shape = (4, 3)`
- `size = 12`
- `itemsize = 4` bytes
- `nbytes = 12 × 4 = 48` bytes

A standard 2-D C-order array created this way is C-contiguous.

#### Step 3 — Choose the NumPy approach

The ndarray metadata is the authoritative way to inspect this object.

#### Step 4 — Implement

```python
import numpy as np

events = np.array(
    [
        [101, 250, 1],
        [102, 400, 2],
        [103, 125, 3],
        [104, 900, 4],
    ],
    dtype=np.int32,
)

print("ndim:", events.ndim)
print("shape:", events.shape)
print("size:", events.size)
print("dtype:", events.dtype)
print("itemsize:", events.itemsize)
print("nbytes:", events.nbytes)
print("C_CONTIGUOUS:", events.flags["C_CONTIGUOUS"])

events64 = events.astype(np.int64)
print("int64 nbytes:", events64.nbytes)
```

#### Step 5 — Explain the implementation

`nbytes` is derived from the array's elements and their dtype width. The Python object itself has additional metadata overhead, so `nbytes` should be interpreted as the raw element-buffer size, not the full process memory footprint.

`int64` uses 8 bytes per element, so 12 elements require 96 bytes.

#### Step 6 — Verify the result

```python
assert events.ndim == 2
assert events.shape == (4, 3)
assert events.size == 12
assert events.dtype == np.int32
assert events.itemsize == 4
assert events.nbytes == 48
assert events.flags["C_CONTIGUOUS"]

assert events64.dtype == np.int64
assert events64.nbytes == 96
```

#### Step 7 — Edge cases / production considerations

At production scale, 2× the element width can become a large memory difference. Always choose the smallest dtype that safely represents the domain and the required downstream operations.

**Key lesson:** memory planning starts with `size × itemsize`, not with intuition about how compact the data “looks.”

---

## Question 02 — Build Arrays Without Accidental Defaults

**Difficulty:** Basic

**Topics tested:** `np.zeros`, `np.ones`, `np.full`, `np.empty`, `np.arange`, `np.linspace`, `np.random.default_rng`, explicit dtype choice.

### Problem

A batch-processing job needs:

- a 5-element integer status array initialized to zero,
- a 4×3 matrix initialized to `7.5`,
- six equally spaced thresholds from `0.0` to `1.0`,
- reproducible random sensor readings between 10 and 20.

Create each array with deliberate dtype choices and explain why `np.empty` is inappropriate when initialized values matter.

### What you need to determine/build

Create:

- `status` as `int16`
- `weights` as `float32`
- `thresholds` as floating-point values
- `readings` as reproducible floating-point values

### Constraints / assumptions

- Use a fixed RNG seed.
- `weights` must contain exactly `7.5` in every element.
- Do not use `np.empty` for data that requires known initial values.

### Expected skills

- Selecting array-construction functions.
- Using deterministic random generation.
- Understanding the semantic difference between `empty` and initialized constructors.

### Solution / How to Solve

#### Step 1 — Understand the problem

Different constructors express different intent. `zeros`, `ones`, and `full` establish known values. `linspace` controls the number of evenly spaced points. `default_rng` gives a reproducible random generator.

#### Step 2 — Predict shape/dtype/memory behavior

- `status`: shape `(5,)`, dtype `int16`
- `weights`: shape `(4, 3)`, dtype `float32`
- `thresholds`: shape `(6,)`
- `readings`: shape `(8,)` in this implementation

#### Step 3 — Choose the NumPy approach

Use the constructor that directly matches the semantic requirement instead of creating an object and then mutating it into the desired state.

#### Step 4 — Implement

```python
import numpy as np

status = np.zeros(5, dtype=np.int16)
weights = np.full((4, 3), 7.5, dtype=np.float32)
thresholds = np.linspace(0.0, 1.0, num=6)

rng = np.random.default_rng(42)
readings = rng.uniform(10.0, 20.0, size=8).astype(np.float32)
```

#### Step 5 — Explain the implementation

`np.empty` allocates storage without initializing the elements to a chosen value. Its contents should be treated as unspecified until every element is assigned.

`astype(np.float32)` is used after random generation here to make the desired numeric storage explicit.

#### Step 6 — Verify the result

```python
assert status.shape == (5,)
assert status.dtype == np.int16
assert np.array_equal(status, np.zeros(5, dtype=np.int16))

assert weights.shape == (4, 3)
assert weights.dtype == np.float32
assert np.all(weights == np.float32(7.5))

assert thresholds.shape == (6,)
assert np.isclose(thresholds[0], 0.0)
assert np.isclose(thresholds[-1], 1.0)

assert readings.shape == (8,)
assert readings.dtype == np.float32
assert np.all((readings >= 10.0) & (readings < 20.0))
```

#### Step 7 — Edge cases / production considerations

When constructing arrays in production, the constructor communicates intent and helps prevent accidental uninitialized data. Always distinguish “allocate storage” from “initialize meaningful values.”

**Key lesson:** choose the constructor whose semantics match the data contract.

---

## Question 03 — Predict a Broadcasted Result Before Running It

**Difficulty:** Basic

**Topics tested:** broadcasting, shape prediction, `np.newaxis`, `np.broadcast_shapes`.

### Problem

You have:

```python
import numpy as np

prices = np.array([100.0, 120.0, 80.0])
tax_rate = np.array([[0.05], [0.10]])
```

You want to apply two different tax rates to the same three prices.

### What you need to determine/build

Before executing the multiplication, determine:

- Input shape A
- Input shape B
- Aligned dimensions
- Whether broadcasting is valid
- Result shape

Then compute the result and verify your prediction programmatically.

### Constraints / assumptions

- Explain the alignment from the rightmost dimensions.
- Do not simply run the code and report the output.

### Expected skills

- Manual broadcasting prediction.
- Using `np.broadcast_shapes`.
- Understanding `(3,)` versus `(2, 1)`.

### Solution / How to Solve

#### Step 1 — Understand the problem

`prices` is shape `(3,)`, which behaves as `(1, 3)` for broadcasting alignment.

`tax_rate` is shape `(2, 1)`.

#### Step 2 — Predict shape/dtype/memory behavior

Align from the right:

```text
tax_rate     (2, 1)
prices       (1, 3)
             ------
result       (2, 3)
```

Every dimension is either equal or `1`, so the multiplication is valid.

#### Step 3 — Choose the NumPy approach

Element-wise multiplication is a ufunc operation and naturally uses broadcasting.

#### Step 4 — Implement

```python
import numpy as np

prices = np.array([100.0, 120.0, 80.0])
tax_rate = np.array([[0.05], [0.10]])

result = prices * tax_rate

print(result)
print("shape:", result.shape)
```

Expected numeric result:

```text
[[105.  126.   84. ]
 [110.  132.   88. ]]
```

#### Step 5 — Explain the implementation

The `(2, 1)` array is logically applied across the three price columns. Broadcasting does not require you to manually build a `(2, 3)` copy of `tax_rate`.

#### Step 6 — Verify the result

```python
assert np.broadcast_shapes(prices.shape, tax_rate.shape) == (2, 3)

expected = np.array(
    [
        [105.0, 126.0, 84.0],
        [110.0, 132.0, 88.0],
    ]
)

np.testing.assert_allclose(result, expected)
```

#### Step 7 — Edge cases / production considerations

A common production failure is confusing a `(n,)` vector with an explicit column `(n, 1)`. A one-dimensional array does not mean “column” or “row” until a shape context gives it that role.

**Key lesson:** always predict aligned shapes manually before trusting a broadcasted expression.

---

## Question 04 — Filter Valid Transactions with a Boolean Mask

**Difficulty:** Basic

**Topics tested:** Boolean masks, `&`, parentheses, `sum`, `mean`, `any`, `all`, `count_nonzero`.

### Problem

Given:

```python
amounts = np.array([1200, 450, 9000, 25000, 800, 15000])
status = np.array(["paid", "failed", "paid", "paid", "paid", "failed"])
```

Select transactions that are:

- at least 1,000 currency units,
- and have status `"paid"`.

Then report:

1. the selected amounts,
2. the number of matching rows,
3. the fraction of all rows that match,
4. whether at least one such transaction exists,
5. whether every input row matches.

### What you need to determine/build

Build one Boolean mask and use it for every requested metric.

### Constraints / assumptions

Use `&`, not Python `and`.

### Expected skills

- Element-wise Boolean logic.
- Mask reuse.
- Counting and validating filters.

### Solution / How to Solve

#### Step 1 — Understand the problem

The condition is the intersection of two element-wise conditions.

#### Step 2 — Predict shape/dtype/memory behavior

Both conditions have shape `(6,)`, so the combined mask also has shape `(6,)` and dtype `bool`.

#### Step 3 — Choose the NumPy approach

Create one mask and reuse it. This avoids inconsistent filtering logic in later statements.

#### Step 4 — Implement

```python
import numpy as np

amounts = np.array([1200, 450, 9000, 25000, 800, 15000])
status = np.array(["paid", "failed", "paid", "paid", "paid", "failed"])

mask = (amounts >= 1000) & (status == "paid")
selected = amounts[mask]

match_count = np.count_nonzero(mask)
match_rate = mask.mean()
has_match = mask.any()
all_match = mask.all()

print(selected)
print(match_count, match_rate, has_match, all_match)
```

The selected values are:

```text
[ 1200  9000 25000]
```

#### Step 5 — Explain the implementation

Each comparison creates a Boolean array. Parentheses make the precedence explicit. Boolean indexing produces a selected array with independent storage.

#### Step 6 — Verify the result

```python
expected = np.array([1200, 9000, 25000])

np.testing.assert_array_equal(selected, expected)
assert match_count == 3
assert np.isclose(match_rate, 0.5)
assert has_match is True
assert all_match is False
```

#### Step 7 — Edge cases / production considerations

An empty selection is valid and should be handled intentionally. For example, downstream aggregation should not assume at least one match exists.

**Key lesson:** build one explicit mask, then reuse it for selection and quality metrics.

---

## Question 05 — Predict Aggregation Axes

**Difficulty:** Basic

**Topics tested:** `sum`, `mean`, axis semantics, result shapes, `keepdims=True`.

### Problem

A batch contains sales for 2 stores across 3 products:

```python
sales = np.array(
    [
        [10, 20, 30],
        [40, 50, 60],
    ],
    dtype=np.int64,
)
```

Determine:

- total sales per product,
- total sales per store,
- total sales overall,
- average sales per store for each product using `keepdims=True`.

### What you need to determine/build

Before running each aggregation, predict the result shape.

### Constraints / assumptions

- Explain which axis disappears.
- Show why `keepdims=True` changes only the shape, not the values.

### Expected skills

- Axis reasoning.
- Reduction semantics.
- Shape prediction.

### Solution / How to Solve

#### Step 1 — Understand the problem

The shape is `(stores, products) = (2, 3)`.

#### Step 2 — Predict shape/dtype/memory behavior

- `axis=0`: combine stores → one result per product → `(3,)`
- `axis=1`: combine products → one result per store → `(2,)`
- `axis=None`: combine everything → scalar
- `axis=0, keepdims=True`: one result per product but keep axis → `(1, 3)`

#### Step 3 — Choose the NumPy approach

Use reductions that directly match the business grain.

#### Step 4 — Implement

```python
import numpy as np

sales = np.array(
    [
        [10, 20, 30],
        [40, 50, 60],
    ],
    dtype=np.int64,
)

per_product = sales.sum(axis=0)
per_store = sales.sum(axis=1)
overall = sales.sum()
avg_per_product_keepdims = sales.mean(axis=0, keepdims=True)

print(per_product)
print(per_store)
print(overall)
print(avg_per_product_keepdims)
```

Expected values:

```text
[50 70 90]
[ 60 150]
210
[[25. 35. 45.]]
```

#### Step 5 — Explain the implementation

Axis `0` represents the store dimension, so reducing it leaves products. Axis `1` represents the product dimension, so reducing it leaves stores.

#### Step 6 — Verify the result

```python
np.testing.assert_array_equal(per_product, np.array([50, 70, 90]))
np.testing.assert_array_equal(per_store, np.array([60, 150]))
assert overall == 210

np.testing.assert_allclose(
    avg_per_product_keepdims,
    np.array([[25.0, 35.0, 45.0]]),
)

assert avg_per_product_keepdims.shape == (1, 3)
```

#### Step 7 — Edge cases / production considerations

A wrong axis can produce a numerically valid but semantically incorrect KPI. In production, document the intended business grain before writing the reduction.

**Key lesson:** axis choice is a business-semantics decision, not just a syntax choice.

---

## Question 06 — Detect NaN, Sentinel, NaT, and Infinity

**Difficulty:** Basic

**Topics tested:** `np.isnan`, sentinels, `NaT`, `np.isnat`, `np.isinf`, `np.isfinite`, NaN semantics.

### Problem

A telemetry batch contains:

```python
values = np.array([10.0, np.nan, -9999.0, np.inf, -np.inf, 25.0])
timestamps = np.array(
    ["2026-01-01", "NaT", "2026-01-03"],
    dtype="datetime64[D]",
)
```

Build explicit masks for:

- NaN values,
- the `-9999` sentinel,
- positive or negative infinity,
- finite values,
- `NaT` timestamps.

### What you need to determine/build

Report the count of each category and explain why `np.nan == np.nan` cannot be used to detect missing numeric values.

### Constraints / assumptions

- Treat `-9999` as a domain-specific sentinel only because the input contract explicitly says so.
- Do not replace values with zeros.

### Expected skills

- Distinguishing missing representations.
- Boolean masks.
- Data-quality semantics.

### Solution / How to Solve

#### Step 1 — Understand the problem

NaN, infinity, sentinel values, and `NaT` are different conditions.

#### Step 2 — Predict shape/dtype/memory behavior

All masks derived from `values` have shape `(6,)` and dtype `bool`. The timestamp mask has shape `(3,)`.

#### Step 3 — Choose the NumPy approach

Use the detection function that matches the representation.

#### Step 4 — Implement

```python
import numpy as np

values = np.array([10.0, np.nan, -9999.0, np.inf, -np.inf, 25.0])
timestamps = np.array(
    ["2026-01-01", "NaT", "2026-01-03"],
    dtype="datetime64[D]",
)

nan_mask = np.isnan(values)
sentinel_mask = values == -9999.0
inf_mask = np.isinf(values)
finite_mask = np.isfinite(values)
nat_mask = np.isnat(timestamps)

counts = {
    "nan": np.count_nonzero(nan_mask),
    "sentinel": np.count_nonzero(sentinel_mask),
    "infinity": np.count_nonzero(inf_mask),
    "finite": np.count_nonzero(finite_mask),
    "nat": np.count_nonzero(nat_mask),
}
print(counts)
```

Expected counts:

```text
{'nan': 1, 'sentinel': 1, 'infinity': 2, 'finite': 3, 'nat': 1}
```

#### Step 5 — Explain the implementation

`np.isnan` detects NaN. `np.isinf` detects either sign of infinity. `np.isfinite` is true only for finite numeric values. `np.isnat` is for datetime/timedelta missing values.

The sentinel is not a mathematical NaN; it is a domain convention, so it must be detected according to the source contract.

#### Step 6 — Verify the result

```python
assert np.count_nonzero(nan_mask) == 1
assert np.count_nonzero(sentinel_mask) == 1
assert np.count_nonzero(inf_mask) == 2
assert np.count_nonzero(finite_mask) == 3
assert np.count_nonzero(nat_mask) == 1

assert np.isnan(np.nan)
assert not (np.nan == np.nan)
```

#### Step 7 — Edge cases / production considerations

Do not assume `0` or `-1` is missing without a documented source contract. Treat missingness as a semantic/data-quality problem.

**Key lesson:** detect the representation that the data source actually uses.

---

## Question 07 — View or Copy? Predict Then Prove

**Difficulty:** Basic

**Topics tested:** basic slicing, Boolean indexing, fancy indexing, views, copies, `np.shares_memory`, mutation.

### Problem

Given:

```python
a = np.array([10, 20, 30, 40, 50, 60])
```

Compare:

```python
b = a[1:4]
c = a[a > 20]
d = a[[1, 3, 5]]
```

Before executing mutations, predict whether each result is a view or a copy.

### What you need to determine/build

For `b`, `c`, and `d`:

- predict view/copy,
- verify memory sharing,
- mutate the result,
- show whether `a` changes.

### Constraints / assumptions

Use `np.shares_memory` as the primary verification.

### Expected skills

- Distinguishing slicing from advanced indexing.
- Understanding mutation through shared storage.

### Solution / How to Solve

#### Step 1 — Understand the problem

Basic slicing and advanced indexing have different memory behavior.

#### Step 2 — Predict shape/dtype/memory behavior

- `b = a[1:4]` → view when basic slicing is used.
- `c = a[a > 20]` → Boolean indexing → copy.
- `d = a[[1, 3, 5]]` → fancy integer indexing → copy.

#### Step 3 — Choose the NumPy approach

Use `np.shares_memory` to prove actual overlap.

#### Step 4 — Implement

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50, 60])

b = a[1:4]
c = a[a > 20]
d = a[[1, 3, 5]]

print(np.shares_memory(a, b))
print(np.shares_memory(a, c))
print(np.shares_memory(a, d))

b[0] = 999
c[0] = 888
d[0] = 777

print(a)
```

Expected sharing:

```text
True
False
False
```

After mutation, only `b` changes `a`.

#### Step 5 — Explain the implementation

`b` points at part of the original buffer. `c` and `d` contain selected values in independent storage.

#### Step 6 — Verify the result

```python
assert np.shares_memory(a, b)
assert not np.shares_memory(a, c)
assert not np.shares_memory(a, d)

assert a[1] == 999
assert 888 not in a
assert 777 not in a
```

#### Step 7 — Edge cases / production considerations

A small slice can also keep a very large source allocation alive. Copying is not always bad; sometimes a small intentional copy lets the large parent buffer be released.

**Key lesson:** selection syntax is also a memory-ownership decision.

---

## Question 08 — Preserve Money and Large IDs Correctly

**Difficulty:** Basic

**Topics tested:** floating-point precision, `0.1 + 0.2`, integer minor units, large integer IDs, `2**53`, dtype choice.

### Problem

A payment pipeline receives:

- monetary amounts such as `19.99`,
- customer IDs that may be larger than `2**53`.

Explain why these two data types should not automatically be treated the same way.

### What you need to determine/build

1. Demonstrate that `0.1 + 0.2` is not represented exactly as decimal `0.3`.
2. Show a safe integer-minor-unit representation for money.
3. Demonstrate the `2**53` precision boundary for integer-to-`float64` conversion.

### Constraints / assumptions

- Use NumPy only.
- Do not claim floating point can never represent decimal values exactly; explain the specific binary representation issue.

### Expected skills

- Numerical correctness.
- Dtype selection.
- Precision-risk identification.

### Solution / How to Solve

#### Step 1 — Understand the problem

Binary floating point does not represent every decimal fraction exactly. Large integer identifiers can also lose exactness when converted to `float64`.

#### Step 2 — Predict shape/dtype/memory behavior

A NumPy `int64` can exactly represent integers in its supported range. `float64` has about 53 bits of integer precision.

#### Step 3 — Choose the NumPy approach

Use integer minor units for fixed-precision money and preserve identifiers as integers.

#### Step 4 — Implement

```python
import numpy as np

sum_float = np.float64(0.1) + np.float64(0.2)
print(repr(sum_float))
print(sum_float == np.float64(0.3))

price_cents = np.array([1999, 2500, 1050], dtype=np.int64)
total_cents = price_cents.sum()

limit = 2**53
large_ids = np.array([limit, limit + 1], dtype=np.int64)
converted = large_ids.astype(np.float64)

print(large_ids)
print(converted)
print(converted[0] == converted[1])
```

#### Step 5 — Explain the implementation

Integer cents avoid binary floating-point representation for exact whole-cent arithmetic. For IDs, converting `2**53`-scale integers to `float64` can collapse distinct integers into the same floating-point value.

#### Step 6 — Verify the result

```python
assert total_cents == 5549
assert sum_float != np.float64(0.3)

assert large_ids[0] != large_ids[1]
assert converted[0] == converted[1]
```

#### Step 7 — Edge cases / production considerations

This does not mean “never use float.” Float is appropriate for many measurements and scientific quantities. The rule is to match representation to semantic requirements.

**Key lesson:** dtype selection is a correctness decision, not merely a memory optimization.

---

# Moderate — Questions 09–16

## Question 09 — Vectorize a Transaction Transformation

**Difficulty:** Moderate

**Topics tested:** vectorization, arithmetic, `np.where`, `np.clip`, comparisons, whole-array operations.

### Problem

A transaction batch contains:

```python
quantity = np.array([1, 4, 10, 2, 8])
unit_price = np.array([100.0, 50.0, 25.0, 80.0, 40.0])
```

Business rules:

- `gross = quantity * unit_price`
- quantities above 5 receive a 10% discount
- negative-adjusted values are not possible in this source, but the final amount must be clipped to a minimum of `0`
- create a `risk_bucket` where gross values under 200 are `"low"` and all others are `"normal"`

### What you need to determine/build

Implement the transformation without a Python loop. Return `net_amount` and `risk_bucket`.

### Constraints / assumptions

- Use vectorized NumPy operations.
- Do not use `np.vectorize`.
- Explain why a whole-array expression is preferred here.

### Expected skills

- Vectorized transformations.
- Conditional vectorization.
- Avoiding Python-level loops.

### Solution / How to Solve

#### Step 1 — Understand the problem

Compute the base value, apply a conditional discount, clip to the allowed range, then classify.

#### Step 2 — Predict shape/dtype/memory behavior

Every numeric input is shape `(5,)`. The numeric results remain shape `(5,)`. The string output is also one value per transaction.

#### Step 3 — Choose the NumPy approach

Use direct arithmetic plus `np.where` and `np.clip`.

#### Step 4 — Implement

```python
import numpy as np

quantity = np.array([1, 4, 10, 2, 8])
unit_price = np.array([100.0, 50.0, 25.0, 80.0, 40.0])

gross = quantity * unit_price
net_amount = np.where(quantity > 5, gross * 0.90, gross)
net_amount = np.clip(net_amount, 0.0, None)

risk_bucket = np.where(net_amount < 200.0, "low", "normal")

print(gross)
print(net_amount)
print(risk_bucket)
```

Expected values:

```text
[100. 200. 250. 160. 320.]
[100. 200. 225. 160. 288.]
['low' 'normal' 'normal' 'low' 'normal']
```

#### Step 5 — Explain the implementation

NumPy applies arithmetic element by element over the entire array. `np.where` selects from two vectorized alternatives without writing a Python loop.

#### Step 6 — Verify the result

```python
np.testing.assert_allclose(
    net_amount,
    np.array([100.0, 200.0, 225.0, 160.0, 288.0]),
)

assert risk_bucket.tolist() == ["low", "normal", "normal", "low", "normal"]
```

#### Step 7 — Edge cases

Check an empty batch and a batch containing a quantity exactly equal to 5.

**Key lesson:** vectorization is about changing the computation model, not merely shortening the code.

---

## Question 10 — Column-wise Normalization with Broadcasting

**Difficulty:** Moderate

**Topics tested:** broadcasting, `np.newaxis`, `reshape`, `mean`, `std`, shape prediction.

### Problem

A feature matrix has shape `(4, 3)`:

```python
X = np.array(
    [
        [10.0, 100.0, 1000.0],
        [20.0, 110.0, 1010.0],
        [30.0, 120.0, 1020.0],
        [40.0, 130.0, 1030.0],
    ]
)
```

Normalize each column using:

```text
(X - column_mean) / column_std
```

### What you need to determine/build

Before executing:

- predict `column_mean.shape`,
- predict `column_std.shape`,
- predict the normalized result shape,
- explain why `keepdims=True` is useful here.

### Constraints / assumptions

- Use vectorized NumPy code.
- Avoid Python loops.

### Expected skills

- Broadcasting shape reasoning.
- Reductions followed by broadcasted transformation.

### Solution / How to Solve

#### Step 1 — Understand the problem

Each column is an independent feature. We want one mean and one standard deviation per column.

#### Step 2 — Predict shape/dtype/memory behavior

`X.mean(axis=0, keepdims=True)` and `X.std(axis=0, keepdims=True)` both have shape `(1, 3)`. They broadcast over the four rows, giving a result of shape `(4, 3)`.

#### Step 3 — Choose the NumPy approach

Use a reduction with `keepdims=True`, then broadcast the statistics back over rows.

#### Step 4 — Implement

```python
import numpy as np

X = np.array(
    [
        [10.0, 100.0, 1000.0],
        [20.0, 110.0, 1010.0],
        [30.0, 120.0, 1020.0],
        [40.0, 130.0, 1030.0],
    ]
)

mean = X.mean(axis=0, keepdims=True)
std = X.std(axis=0, keepdims=True)

normalized = (X - mean) / std

print(mean.shape)
print(std.shape)
print(normalized.shape)
```

#### Step 5 — Explain the implementation

The reduction removes the row dimension mathematically but preserves it structurally with `keepdims=True`. This gives shapes that broadcast naturally against the original matrix.

#### Step 6 — Verify the result

```python
assert mean.shape == (1, 3)
assert std.shape == (1, 3)
assert normalized.shape == (4, 3)

np.testing.assert_allclose(
    normalized.mean(axis=0),
    np.zeros(3),
    atol=1e-12,
)
np.testing.assert_allclose(
    normalized.std(axis=0),
    np.ones(3),
    atol=1e-12,
)
```

#### Step 7 — Edge cases / production considerations

If a column is constant, its standard deviation is zero. The pipeline needs an explicit policy for that case rather than silently accepting invalid values.

**Key lesson:** `keepdims=True` often makes downstream broadcasting safer and clearer.

---

## Question 11 — Price Bands with `searchsorted`

**Difficulty:** Moderate

**Topics tested:** `searchsorted`, vectorized lookup, binning, `np.digitize`, comparisons.

### Problem

A pricing service defines bands:

```python
upper_bounds = np.array([100, 500, 1000])
labels = np.array(["low", "medium", "high", "premium"])
```

Incoming prices are:

```python
prices = np.array([50, 100, 101, 500, 501, 1000, 1001])
```

Classify each price into:

- `low` for prices below or equal to 100,
- `medium` for 101–500,
- `high` for 501–1000,
- `premium` above 1000.

### What you need to determine/build

Use `np.searchsorted` to obtain the band index and map it to `labels`.

Also explain what changes if `side="right"` is replaced by `side="left"`.

### Constraints / assumptions

- Do not use a Python loop.
- Boundary behavior must be explicit.

### Expected skills

- Vectorized lookup.
- Boundary reasoning.
- `searchsorted` semantics.

### Solution / How to Solve

#### Step 1 — Understand the problem

For each price, we need the first upper bound that is greater than or equal to the price. That corresponds to `side="left"` with the appropriate upper-bound convention.

#### Step 2 — Predict shape/dtype/memory behavior

The output index array has shape `(7,)`. Mapping through `labels` also gives shape `(7,)`.

#### Step 3 — Choose the NumPy approach

Use `searchsorted` to locate insertion positions in sorted boundaries.

#### Step 4 — Implement

```python
import numpy as np

upper_bounds = np.array([100, 500, 1000])
labels = np.array(["low", "medium", "high", "premium"])
prices = np.array([50, 100, 101, 500, 501, 1000, 1001])

band_index = np.searchsorted(upper_bounds, prices, side="left")
band_labels = labels[band_index]

print(band_index)
print(band_labels)
```

Expected labels:

```text
['low' 'low' 'medium' 'medium' 'high' 'high' 'premium']
```

#### Step 5 — Explain the implementation

For `100`, the insertion position on the left is `0`, keeping it in the first band. `101` produces index `1`. Values larger than the last bound produce index `3`, selecting `"premium"`.

#### Step 6 — Verify the result

```python
expected = np.array(
    ["low", "low", "medium", "medium", "high", "high", "premium"]
)

assert band_index.shape == prices.shape
assert band_labels.tolist() == expected.tolist()
```

#### Step 7 — Edge cases / production considerations

Boundary choices are part of the business definition. Always test exact boundary values such as `100`, `500`, and `1000`.

**Key lesson:** vectorized lookup is often a better fit than repeated scalar conditionals for large batches.

---

## Question 12 — Solve a Top-3 Problem Without Fully Sorting Everything

**Difficulty:** Moderate

**Topics tested:** `np.argpartition`, `np.argsort`, top-k selection, subset sorting, memory/performance reasoning.

### Problem

Given:

```python
scores = np.array([91, 15, 88, 73, 99, 42, 95, 67, 81])
```

Return the top 3 scores in descending order **and their original positions**.

Then explain why a full sort may be unnecessary when `k` is much smaller than `N`.

### What you need to determine/build

Implement a top-k solution using `argpartition`, then sort only the selected subset.

### Constraints / assumptions

- Do not assume `argpartition` itself returns the top 3 in sorted order.
- Handle `k=1` correctly in your reasoning.

### Expected skills

- Partial selection.
- Sorting a selected subset.
- Performance-oriented algorithm selection.

### Solution / How to Solve

#### Step 1 — Understand the problem

We need membership in the top 3 first, then ordering among those 3.

#### Step 2 — Predict shape/dtype/memory behavior

`argpartition` returns an index array with the same shape as `scores`. We only keep the final `k` positions.

#### Step 3 — Choose the NumPy approach

For descending top-k, partition using `-scores`.

#### Step 4 — Implement

```python
import numpy as np

scores = np.array([91, 15, 88, 73, 99, 42, 95, 67, 81])
k = 3

candidate_positions = np.argpartition(-scores, kth=k - 1)[:k]
order = np.argsort(-scores[candidate_positions])

top_positions = candidate_positions[order]
top_scores = scores[top_positions]

print(top_positions)
print(top_scores)
```

Expected result:

```text
[4 6 0]
[99 95 91]
```

#### Step 5 — Explain the implementation

`argpartition` identifies the top-k region without guaranteeing internal ordering. Sorting only that small region costs much less than sorting all `N` values when `k << N`.

#### Step 6 — Verify the result

```python
expected_positions = np.array([4, 6, 0])
expected_scores = np.array([99, 95, 91])

np.testing.assert_array_equal(top_positions, expected_positions)
np.testing.assert_array_equal(top_scores, expected_scores)

assert top_scores[0] >= top_scores[1] >= top_scores[2]
```

#### Step 7 — Edge cases / production considerations

Test:

- `k=1`
- `k == len(scores)`
- tied values

For ties, define whether any order is acceptable or whether deterministic tie-breaking is required.

**Key lesson:** use partial selection when the business question is “find the top-k,” not “fully order the entire dataset.”

---

## Question 13 — Aggregate a 3-D Store Dataset Correctly

**Difficulty:** Moderate

**Topics tested:** 3-D arrays, axis semantics, tuple axes, `keepdims`, result-shape prediction.

### Problem

A dataset has shape:

```text
(days, stores, products) = (2, 3, 4)
```

Create:

```python
sales = np.arange(24).reshape(2, 3, 4)
```

You need:

1. sales per day,
2. sales per store,
3. sales per product,
4. overall sales,
5. sales per day while keeping dimensions.

### What you need to determine/build

For each result, state which axes are reduced and the resulting shape.

### Constraints / assumptions

- Manually predict all shapes before code execution.
- Use a tuple of axes for at least one aggregation.

### Expected skills

- Higher-dimensional axis reasoning.
- Tuple-axis reductions.
- Shape prediction.

### Solution / How to Solve

#### Step 1 — Understand the problem

The dimensions are:

```text
axis 0 = day
axis 1 = store
axis 2 = product
```

#### Step 2 — Predict shape/dtype/memory behavior

- per day: reduce `(1, 2)` → `(2,)`
- per store: reduce `(0, 2)` → `(3,)`
- per product: reduce `(0, 1)` → `(4,)`
- overall: reduce all axes → scalar
- per day with `keepdims=True`: reduce `(1, 2)` → `(2, 1, 1)`

#### Step 3 — Choose the NumPy approach

Use tuple axes to state the business grain explicitly.

#### Step 4 — Implement

```python
import numpy as np

sales = np.arange(24).reshape(2, 3, 4)

per_day = sales.sum(axis=(1, 2))
per_store = sales.sum(axis=(0, 2))
per_product = sales.sum(axis=(0, 1))
overall = sales.sum()
per_day_keepdims = sales.sum(axis=(1, 2), keepdims=True)

print("per_day:", per_day)
print("per_store:", per_store)
print("per_product:", per_product)
print("overall:", overall)
print("per_day_keepdims shape:", per_day_keepdims.shape)
```

#### Step 5 — Explain the implementation

The tuple `(1, 2)` means “collapse store and product dimensions while retaining day.” This is often clearer than performing multiple reductions sequentially.

#### Step 6 — Verify the result

```python
assert per_day.shape == (2,)
assert per_store.shape == (3,)
assert per_product.shape == (4,)
assert overall.shape == ()

assert per_day_keepdims.shape == (2, 1, 1)

np.testing.assert_array_equal(per_day, np.array([66, 210]))
np.testing.assert_array_equal(per_store, np.array([36, 92, 128]))
np.testing.assert_array_equal(per_product, np.array([30, 34, 38, 42]))
assert overall == 276
```

#### Step 7 — Edge cases / production considerations

In real pipelines, encode dimension meaning clearly. Axis mistakes are especially dangerous in 3-D and higher-dimensional tensors because the output can look plausible.

**Key lesson:** always attach a semantic name to each axis before reducing it.

---

## Question 14 — Compute NaN-Safe API Latency Metrics

**Difficulty:** Moderate

**Topics tested:** NaN-aware reductions, missingness, `std`, `ddof`, percentiles, `nanargmax`.

### Problem

An API latency batch contains:

```python
latency_ms = np.array([120.0, np.nan, 140.0, 500.0, 200.0, np.nan, 180.0])
```

Compute:

- ordinary mean,
- NaN-safe mean,
- NaN-safe median,
- NaN-safe p95,
- NaN-safe maximum,
- position of the maximum among the original array.

Also determine the sample standard deviation using `ddof=1`.

### What you need to determine/build

Explain why the ordinary mean is not the right metric when NaN means “missing measurement.”

### Constraints / assumptions

- Do not replace NaN with zero.
- Explain the denominator implied by NaN-safe statistics.

### Expected skills

- Missing-data semantics.
- NaN-safe metrics.
- Percentile and `ddof` reasoning.

### Solution / How to Solve

#### Step 1 — Understand the problem

There are 5 valid latency values and 2 missing observations.

#### Step 2 — Predict shape/dtype/memory behavior

All scalar metrics are scalars. `np.nanargmax` returns the original-array index of the maximum finite/non-NaN value.

#### Step 3 — Choose the NumPy approach

Use `np.nan*` reductions because missing measurements should be excluded rather than interpreted as zero.

#### Step 4 — Implement

```python
import numpy as np

latency_ms = np.array([120.0, np.nan, 140.0, 500.0, 200.0, np.nan, 180.0])

ordinary_mean = latency_ms.mean()
safe_mean = np.nanmean(latency_ms)
safe_median = np.nanmedian(latency_ms)
safe_p95 = np.nanpercentile(latency_ms, 95)
safe_max = np.nanmax(latency_ms)
max_position = np.nanargmax(latency_ms)
sample_std = np.nanstd(latency_ms, ddof=1)

valid_count = np.count_nonzero(~np.isnan(latency_ms))

print(ordinary_mean)
print(safe_mean)
print(safe_median)
print(safe_p95)
print(safe_max)
print(max_position)
print(sample_std)
print(valid_count)
```

#### Step 5 — Explain the implementation

`nanmean` ignores NaN values. The denominator is therefore the count of non-NaN observations, not the total array length.

`ddof=1` is a sample-standard-deviation convention. It is not interchangeable with the default population-style `ddof=0`.

#### Step 6 — Verify the result

```python
assert np.isnan(ordinary_mean)

assert np.isclose(safe_mean, 228.0)
assert np.isclose(safe_median, 180.0)
assert np.isclose(safe_max, 500.0)
assert max_position == 3
assert valid_count == 5

expected_std = np.std(
    np.array([120.0, 140.0, 500.0, 200.0, 180.0]),
    ddof=1,
)
assert np.isclose(sample_std, expected_std)
```

#### Step 7 — Edge cases / production considerations

All-NaN arrays require an explicit policy. A NaN-safe function does not automatically solve the business question of what to do when no valid data exists.

**Key lesson:** NaN-safe mathematics changes the population being summarized; document that semantic change.

---

## Question 15 — Keep the Latest Record per Key Deterministically

**Difficulty:** Moderate

**Topics tested:** `np.lexsort`, deterministic ordering, stable sorting, `np.unique(return_index=True)`, deduplication.

### Problem

You receive CDC-style records:

```python
order_id = np.array([101, 102, 101, 103, 102, 101])
updated_at = np.array([5, 3, 7, 2, 9, 7])
amount = np.array([100, 200, 110, 50, 250, 120])
```

Keep exactly one record per `order_id`: the latest `updated_at`. If timestamps tie, keep the last input occurrence.

### What you need to determine/build

Implement deterministic latest-record selection and return the selected original positions.

### Constraints / assumptions

- Explain why ordering must be established before `unique(return_index=True)`.
- Preserve aligned columns.

### Expected skills

- Multi-key ordering.
- Stable/deterministic deduplication.
- Aligned-array indexing.

### Solution / How to Solve

#### Step 1 — Understand the problem

We need the row ordering to be:

1. `order_id` ascending
2. `updated_at` descending
3. original position descending for a deterministic “last occurrence wins” tie rule

#### Step 2 — Predict shape/dtype/memory behavior

The final selected positions contain one row per unique order ID, so shape `(3,)`.

#### Step 3 — Choose the NumPy approach

`np.lexsort` provides multi-key ordering. Because `lexsort` uses the last key as the primary key, carefully construct the keys.

#### Step 4 — Implement

```python
import numpy as np

order_id = np.array([101, 102, 101, 103, 102, 101])
updated_at = np.array([5, 3, 7, 2, 9, 7])
amount = np.array([100, 200, 110, 50, 250, 120])

original_pos = np.arange(order_id.size)

# Primary: order_id ascending
# Secondary: updated_at descending
# Tertiary: original position descending
sort_pos = np.lexsort(
    (
        -original_pos,
        -updated_at,
        order_id,
    )
)

sorted_order_id = order_id[sort_pos]
unique_keys, first_sorted_positions = np.unique(
    sorted_order_id,
    return_index=True,
)

selected_positions = sort_pos[first_sorted_positions]
selected_order_id = order_id[selected_positions]
selected_amount = amount[selected_positions]

print(selected_positions)
print(selected_order_id)
print(selected_amount)
```

For `101`, the later timestamp value is tied at positions 2 and 5, so position 5 wins.

#### Step 5 — Explain the implementation

After sorting, the first occurrence of each key is the desired record because the sort order already encodes the business rule. `return_index=True` gives the positions in the sorted representation, which are then mapped back to original row positions.

#### Step 6 — Verify the result

```python
expected_positions = np.array([5, 4, 3])

np.testing.assert_array_equal(selected_positions, expected_positions)
np.testing.assert_array_equal(
    selected_order_id,
    np.array([101, 102, 103]),
)
np.testing.assert_array_equal(
    selected_amount,
    np.array([120, 250, 50]),
)
```

#### Step 7 — Edge cases / production considerations

Test:

- duplicated keys,
- tied timestamps,
- one record per key,
- empty input.

**Key lesson:** deduplication is an ordering problem first and a uniqueness problem second.

---

## Question 16 — Estimate Memory and Decide on a View, Copy, or Memmap

**Difficulty:** Moderate

**Topics tested:** `.nbytes`, dtype memory, slices, view retention, contiguity, `np.load(..., mmap_mode="r")`, memory mapping, production memory reasoning.

### Problem

A telemetry file contains `50_000_000` `float32` values.

1. Estimate the raw element storage in MiB.
2. Explain why a slice such as `arr[:1000]` can still keep the entire source allocation alive.
3. Explain when making a small `.copy()` can reduce retained memory.
4. Explain why a `.npy` file can be processed through `np.load(..., mmap_mode="r")` instead of fully materializing it.

### What you need to determine/build

Give the numerical memory estimate and the design decision for a pipeline with limited RAM.

### Constraints / assumptions

Use binary units:

```text
1 MiB = 1024 × 1024 bytes
```

### Expected skills

- Memory estimation.
- View retention reasoning.
- Memmap and chunking decisions.

### Solution / How to Solve

#### Step 1 — Understand the problem

A `float32` element uses 4 bytes.

#### Step 2 — Predict shape/dtype/memory behavior

Raw storage:

```text
50,000,000 × 4 = 200,000,000 bytes
```

In MiB:

```text
200,000,000 / (1024²) ≈ 190.73 MiB
```

#### Step 3 — Choose the NumPy approach

Use `.nbytes` for an in-memory array and `np.load(..., mmap_mode="r")` when the source is a `.npy` file and the full array need not be materialized.

#### Step 4 — Implement

```python
import numpy as np

n = 50_000_000
bytes_required = n * np.dtype(np.float32).itemsize
mib_required = bytes_required / (1024**2)

print(bytes_required)
print(mib_required)

# A small slice is normally a view.
arr = np.arange(10_000, dtype=np.float32)
small_view = arr[:1000]

print(np.shares_memory(arr, small_view))
```

#### Step 5 — Explain the implementation

A view does not automatically own a smaller buffer. The small slice can keep the original buffer alive as long as the slice remains reachable.

If the slice is logically long-lived and tiny compared with the source, this can be a good case for:

```python
small_copy = small_view.copy()
```

After the copy becomes independent, the much larger source buffer may become reclaimable when no references remain.

For a large `.npy`, use:

```python
mapped = np.load("telemetry.npy", mmap_mode="r")
```

and then process it in chunks.

#### Step 6 — Verify the result

```python
assert bytes_required == 200_000_000
assert np.isclose(mib_required, 190.73486328125)

assert np.shares_memory(arr, small_view)

small_copy = small_view.copy()
assert not np.shares_memory(arr, small_copy)
```

#### Step 7 — Edge cases / production considerations

Memory mapping does not make storage as fast as RAM. Access patterns still matter because pages are fetched through the operating system's virtual-memory and page-cache machinery.

**Key lesson:** a view is cheap to create, but its lifetime can have a large memory consequence.

---

# Hard — Questions 17–24

## Question 17 — Debug Two Separate Indexing Bugs

**Difficulty:** Hard

**Topics tested:** Boolean masks, `&`, operator precedence, chained indexing, view/copy behavior, masked assignment.

### Problem

The following code is intended to set all values between 10 and 100 to `5`:

```python
import numpy as np

a = np.array([3, 12, 25, 150, 80, 7])

a[(a > 10) and (a < 100)] = 5
a[a < 100][0] = 99
```

The engineer reports that both lines are wrong or misleading.

Diagnose both problems and provide correct code.

### What you need to determine/build

For each bug:

1. state the symptom,
2. identify the root cause,
3. provide the correct code,
4. explain whether the selected object is a view or copy,
5. provide a prevention rule.

### Constraints / assumptions

Do not replace the second line with a different business requirement. Preserve the intent: update the first element among values below 100.

### Expected skills

- Debugging.
- Element-wise Boolean logic.
- Understanding advanced indexing copies.
- Safe mutation.

### Solution / How to Solve

#### Step 1 — Understand the problem

The first line uses Python's scalar `and` operator on arrays. The second line uses Boolean indexing and then attempts mutation on its result.

#### Step 2 — Predict shape/dtype/memory behavior

The Boolean expression should produce a `(6,)` mask. Boolean indexing creates a copy, so mutating that selected array will not mutate `a`.

#### Step 3 — Choose the NumPy approach

Use `&` with parentheses for element-wise logic and perform the second update through the original array using the mask.

#### Step 4 — Implement

```python
import numpy as np

a = np.array([3, 12, 25, 150, 80, 7])

mask = (a > 10) & (a < 100)
a[mask] = 5

below_100 = a < 100
first_position = np.flatnonzero(below_100)[0]
a[first_position] = 99

print(a)
```

Final array:

```text
[ 3 99  5 150  5  7]
```

#### Step 5 — Explain the implementation

`and` asks for one Python truth value, while NumPy comparisons produce an array of truth values. `&` performs element-wise AND.

The expression `a[a < 100]` returns a copy. Assigning into that copy cannot update the source.

#### Step 6 — Verify the result

```python
expected = np.array([3, 99, 5, 150, 5, 7])
np.testing.assert_array_equal(a, expected)
```

#### Step 7 — Edge cases / production considerations

If there are no values below 100, indexing `[0]` would fail. A robust production function should check whether the candidate set is non-empty before selecting the first position.

**Key lesson:** separate “select values” from “assign back to the original array.”

---

## Question 18 — Diagnose Integer Overflow in a Reduction

**Difficulty:** Hard

**Topics tested:** integer dtypes, overflow, accumulation dtype, `sum`, dtype planning, numerical correctness.

### Problem

A transaction pipeline stores cents in `int16`:

```python
import numpy as np

amounts = np.array([30_000, 30_000, 30_000], dtype=np.int16)
total = amounts.sum()
```

The engineer expects `90_000` but gets an incorrect result.

### What you need to determine/build

1. Explain why the result is wrong.
2. Inspect the relevant dtypes.
3. Fix the aggregation safely.
4. Decide whether the source array itself should be widened.

### Constraints / assumptions

- Preserve the source values exactly.
- Explain the difference between changing the accumulation dtype and changing storage dtype.

### Expected skills

- Overflow diagnosis.
- Reduction dtype reasoning.
- Production dtype planning.

### Solution / How to Solve

#### Step 1 — Understand the problem

`int16` cannot represent `90_000` because its signed range is only:

```text
-32,768 to 32,767
```

#### Step 2 — Predict shape/dtype/memory behavior

`amounts` is `int16`. The reduction can accumulate in a dtype that is not wide enough for the expected result in this example, so the sum wraps to an incorrect integer result.

#### Step 3 — Choose the NumPy approach

Use a wider accumulation dtype:

```python
amounts.sum(dtype=np.int64)
```

If the domain's totals routinely exceed the source dtype's capacity, reconsider the source storage dtype too.

#### Step 4 — Implement

```python
import numpy as np

amounts = np.array([30_000, 30_000, 30_000], dtype=np.int16)

unsafe_total = amounts.sum()
safe_total = amounts.sum(dtype=np.int64)

print("source dtype:", amounts.dtype)
print("unsafe total:", unsafe_total)
print("safe total:", safe_total)
print("safe dtype:", safe_total.dtype)
```

#### Step 5 — Explain the implementation

There are two distinct decisions:

- **storage dtype:** how each element is represented,
- **accumulation dtype:** how the reduction is performed.

A wider accumulation dtype can solve a reduction-overflow problem without immediately changing the source array.

#### Step 6 — Verify the result

```python
assert safe_total == 90_000
assert safe_total.dtype == np.dtype(np.int64)

assert amounts.dtype == np.dtype(np.int16)
```

#### Step 7 — Edge cases / production considerations

Do not choose a storage dtype only from individual values. Consider the range of derived quantities and aggregates.

**Key lesson:** safe element storage and safe accumulation are related but separate engineering decisions.

---

## Question 19 — Clean and Summarize Sensor Data Without Lying

**Difficulty:** Hard

**Topics tested:** NaN, sentinel, infinity, validity masks, missingness rates, NaN-safe aggregation, per-device grouping concepts.

### Problem

A sensor batch is represented by aligned arrays:

```python
device = np.array(["A", "A", "A", "B", "B", "B"])
reading = np.array([10.0, -9999.0, np.nan, 100.0, np.inf, 120.0])
```

The source contract says:

- `-9999` means missing reading,
- `NaN` means missing reading,
- infinity is invalid,
- a device must be quarantined if more than 33% of its readings are invalid.

For valid readings only, compute one mean per device. Do not impute.

### What you need to determine/build

Build:

1. a validity mask,
2. an invalid-rate metric per device,
3. a quarantine decision per device,
4. valid mean per device.

### Constraints / assumptions

- A finite value is valid.
- Do not treat `0` as missing.
- Use NumPy-only grouping logic with masks and `np.unique`.

### Expected skills

- Missingness semantics.
- Validity masks.
- Group-style aggregation without pandas.
- Quality thresholds.

### Solution / How to Solve

#### Step 1 — Understand the problem

The valid condition is:

```text
not sentinel
AND not NaN
AND finite
```

#### Step 2 — Predict shape/dtype/memory behavior

`valid_mask` is `(6,)` Boolean. Unique devices are `["A", "B"]`.

Device A has 1 valid out of 3; device B has 2 valid out of 3.

#### Step 3 — Choose the NumPy approach

Use `np.unique(..., return_inverse=True)` to create group codes, then aggregate with `np.bincount` or Boolean masks.

Because invalid readings must not enter the mean, use a masked sum/count formulation.

#### Step 4 — Implement

```python
import numpy as np

device = np.array(["A", "A", "A", "B", "B", "B"])
reading = np.array([10.0, -9999.0, np.nan, 100.0, np.inf, 120.0])

valid_mask = (
    (reading != -9999.0)
    & ~np.isnan(reading)
    & np.isfinite(reading)
)

devices, group_codes = np.unique(device, return_inverse=True)

valid_values = np.where(valid_mask, reading, 0.0)
valid_indicator = valid_mask.astype(np.int64)

sum_by_device = np.bincount(group_codes, weights=valid_values)
count_by_device = np.bincount(
    group_codes,
    weights=valid_indicator,
)

mean_by_device = np.full(devices.shape, np.nan, dtype=np.float64)

has_data = count_by_device > 0
mean_by_device[has_data] = (
    sum_by_device[has_data] / count_by_device[has_data]
)

total_count_by_device = np.bincount(group_codes)
invalid_rate = 1.0 - (count_by_device / total_count_by_device)

quarantine = invalid_rate > (1.0 / 3.0)

print("devices:", devices)
print("mean:", mean_by_device)
print("invalid_rate:", invalid_rate)
print("quarantine:", quarantine)
```

Expected logical result:

```text
devices: ['A' 'B']
mean: [ 10. 110.]
invalid_rate: [0.666..., 0.333...]
quarantine: [ True False]
```

#### Step 5 — Explain the implementation

The representation is intentionally not “sentinel → zero.” Instead, `valid_mask` preserves the source semantics while allowing numeric aggregation through a separate validity indicator.

For device A, 2 of 3 rows are invalid, so the invalid rate exceeds one-third.

For device B, one of 3 rows is invalid, so the rate is exactly one-third and does not exceed the threshold.

#### Step 6 — Verify the result

```python
np.testing.assert_array_equal(
    valid_mask,
    np.array([True, False, False, True, False, True]),
)

np.testing.assert_allclose(
    mean_by_device,
    np.array([10.0, 110.0]),
)

np.testing.assert_allclose(
    invalid_rate,
    np.array([2 / 3, 1 / 3]),
)

np.testing.assert_array_equal(
    quarantine,
    np.array([True, False]),
)
```

#### Step 7 — Edge cases / production considerations

Handle all-invalid groups explicitly. Also distinguish invalid reasons when operational reporting requires it; a validity mask is useful because “missing,” “overflow,” and “physically impossible” can have different meanings.

A common one-dimensional forward-fill building block from the missing-data chapter is `np.maximum.accumulate`. For example, positions of observed values can be propagated forward:

```python
values = np.array([10.0, np.nan, 12.0, np.nan, 15.0])
observed = ~np.isnan(values)
last_seen_position = np.where(
    observed,
    np.arange(values.size),
    -1,
)
last_seen_position = np.maximum.accumulate(last_seen_position)

filled = values.copy()
missing = ~observed
filled[missing] = filled[last_seen_position[missing]]
```

This pattern is only correct when the data is already in the intended entity/time order. A production forward-fill must not cross device boundaries unintentionally.

**Key lesson:** cleaning data must preserve the semantics of why a value is invalid.

---

## Question 20 — Fix a Naïve Chunked Mean and Explain Why It Is Wrong

**Difficulty:** Hard

**Topics tested:** chunking, partial sums/counts, mean merging, min/max, numerical correctness.

### Problem

A huge array cannot fit comfortably in memory. The engineer processes three chunks and does this:

```python
chunk_means = [np.mean(chunk) for chunk in chunks]
global_mean = np.mean(chunk_means)
```

Explain why this is wrong when chunks have different sizes, and build the correct chunked mean/min/max computation.

### What you need to determine/build

Return:

- total count,
- total sum,
- global mean,
- global minimum,
- global maximum.

Then compare against full-array results on a small deterministic test array.

### Constraints / assumptions

- Chunk sizes are not equal.
- Use partial sums and counts.
- Explain why percentiles are different and cannot generally be merged by averaging chunk percentiles.

### Expected skills

- Chunked aggregation.
- Correct merge semantics.
- Verification against a full-array reference.

### Solution / How to Solve

#### Step 1 — Understand the problem

A mean is not a simple average of chunk means unless every chunk has equal count.

#### Step 2 — Predict shape/dtype/memory behavior

Each chunk contributes a scalar sum and scalar count. The merged result is also scalar.

#### Step 3 — Choose the NumPy approach

Track:

```text
total_sum
total_count
global_min
global_max
```

and derive:

```text
mean = total_sum / total_count
```

#### Step 4 — Implement

```python
import numpy as np

data = np.arange(1, 11, dtype=np.float64)
chunks = [
    data[:2],
    data[2:5],
    data[5:],
]

total_sum = 0.0
total_count = 0
global_min = np.inf
global_max = -np.inf

for chunk in chunks:
    total_sum += chunk.sum()
    total_count += chunk.size
    global_min = min(global_min, chunk.min())
    global_max = max(global_max, chunk.max())

global_mean = total_sum / total_count

print(total_count, total_sum, global_mean, global_min, global_max)
```

Expected result:

```text
10 55.0 5.5 1.0 10.0
```

#### Step 5 — Explain the implementation

The correct weighted mean is:

```text
(sum of all chunk sums) / (sum of all counts)
```

A simple average of chunk means weights every chunk equally, regardless of size.

Likewise:

- global min = minimum of chunk minima,
- global max = maximum of chunk maxima.

Percentiles do not have the same simple merge rule; averaging chunk p95 values generally does not produce the global p95.

#### Step 6 — Verify the result

```python
np.testing.assert_allclose(global_mean, data.mean())
assert total_count == data.size
assert total_sum == data.sum()
assert global_min == data.min()
assert global_max == data.max()
```

#### Step 7 — Edge cases / production considerations

Test unequal chunk sizes, empty chunks if your pipeline may create them, and very large sums with an adequate accumulation dtype.

**Key lesson:** know which statistics are mergeable from small sufficient summaries and which are not.

---

## Question 21 — Prevent an Accidental `(N, N)` Memory Explosion

**Difficulty:** Hard

**Topics tested:** broadcasting, pairwise differences, memory estimation, chunking, temporary allocations.

### Problem

An engineer wants pairwise differences between two 50,000-element vectors:

```python
a = np.arange(50_000, dtype=np.float64)
b = np.arange(50_000, dtype=np.float64)

diff = a[:, None] - b[None, :]
```

This would logically produce shape `(50_000, 50_000)`.

### What you need to determine/build

1. Predict the result shape.
2. Estimate the raw result-array memory in GiB.
3. Explain why broadcasting itself is not “free” once a materialized result is requested.
4. Redesign the calculation using chunks.

### Constraints / assumptions

- You may not materialize the full `(N, N)` matrix.
- The exact downstream business operation is the row-wise minimum absolute difference to any value in `b`.
- Use chunking and `np.abs`.

### Expected skills

- Broadcasting prediction.
- Memory estimation.
- Chunked numerical design.
- Temporary-memory awareness.

### Solution / How to Solve

#### Step 1 — Understand the problem

Shapes:

```text
a[:, None] -> (50_000, 1)
b[None, :] -> (1, 50_000)
```

Broadcast result:

```text
(50_000, 50_000)
```

#### Step 2 — Predict shape/dtype/memory behavior

There are 2.5 billion output elements.

At 8 bytes each:

```text
2,500,000,000 × 8 = 20,000,000,000 bytes
```

That is approximately 18.63 GiB for one raw `float64` result array, before considering additional temporaries.

#### Step 3 — Choose the NumPy approach

Process only a manageable chunk of `a` against all of `b`.

#### Step 4 — Implement

```python
import numpy as np

a = np.arange(50_000, dtype=np.float64)
b = np.arange(50_000, dtype=np.float64)

chunk_size = 1_000
result = np.empty(a.size, dtype=np.float64)

for start in range(0, a.size, chunk_size):
    stop = min(start + chunk_size, a.size)
    chunk = a[start:stop]

    distances = np.abs(chunk[:, None] - b[None, :])
    result[start:stop] = distances.min(axis=1)
```

#### Step 5 — Explain the implementation

Only the chunk-by-`b` matrix is materialized. Its shape is at most:

```text
(1000, 50_000)
```

That is 50 million `float64` values, about 381.47 MiB for the raw distance matrix. This is still substantial, so production code may need a smaller chunk size or a more specialized algorithm.

The important point is that peak memory is now controlled rather than proportional to `N²` for the entire input.

#### Step 6 — Verify the result

```python
small_a = np.array([0.0, 10.0, 25.0])
small_b = np.array([2.0, 12.0, 40.0])

reference = np.min(
    np.abs(small_a[:, None] - small_b[None, :]),
    axis=1,
)

np.testing.assert_allclose(
    reference,
    np.array([2.0, 2.0, 13.0]),
)
```

#### Step 7 — Edge cases / production considerations

Even a chunked broadcast may remain expensive when one dimension is enormous. The production question is not merely “Can broadcasting express this?” but “Can the resulting computation fit the memory and runtime budget?”

**Key lesson:** shape prediction should happen before allocating a potentially huge broadcasted result.

---

## Question 22 — Numerical Correctness Under Large Batch Aggregation

**Difficulty:** Hard

**Topics tested:** float precision, accumulation dtype, `ddof`, `std`, integer-to-float concerns, comparison testing.

### Problem

A monitoring job reports:

```python
latency = np.array(
    [1000.0, 1000.1, 999.9, 1000.2, 999.8],
    dtype=np.float32,
)
```

The engineer uses:

```python
mean = latency.mean(dtype=np.float32)
std_population = latency.std(dtype=np.float32, ddof=0)
std_sample = latency.std(dtype=np.float32, ddof=1)
```

You need to explain:

1. why `ddof=0` and `ddof=1` answer different statistical questions,
2. why exact equality is a poor general assertion for floating-point results,
3. when a wider accumulation dtype can be justified.

### What you need to determine/build

Produce both standard deviations and a test against a float64 reference with a tolerance.

### Constraints / assumptions

Do not claim `float32` is always wrong. Focus on the relationship between precision requirements and accumulation.

### Expected skills

- Numerical correctness.
- Statistical semantics.
- Floating-point testing.

### Solution / How to Solve

#### Step 1 — Understand the problem

`ddof=0` calculates the population-style standard deviation. `ddof=1` uses one degree of freedom fewer and is the common sample-standard-deviation convention.

#### Step 2 — Predict shape/dtype/memory behavior

All three metrics are scalar. The source remains `float32`.

#### Step 3 — Choose the NumPy approach

Use a wider accumulation dtype for a reference when precision matters and use tolerance-based testing.

#### Step 4 — Implement

```python
import numpy as np

latency = np.array(
    [1000.0, 1000.1, 999.9, 1000.2, 999.8],
    dtype=np.float32,
)

mean32 = latency.mean(dtype=np.float32)
std_population = latency.std(dtype=np.float32, ddof=0)
std_sample = latency.std(dtype=np.float32, ddof=1)

mean64 = latency.mean(dtype=np.float64)
std_sample64 = latency.std(dtype=np.float64, ddof=1)

print("mean32:", mean32)
print("mean64:", mean64)
print("population std:", std_population)
print("sample std:", std_sample)
```

#### Step 5 — Explain the implementation

`float32` is often appropriate when its precision and memory trade-offs match the application. But for sensitive aggregates, a wider accumulation dtype can reduce rounding error without necessarily changing the stored input dtype.

#### Step 6 — Verify the result

```python
assert std_population != std_sample

np.testing.assert_allclose(
    mean32,
    mean64,
    rtol=1e-6,
    atol=1e-6,
)

np.testing.assert_allclose(
    std_sample,
    std_sample64,
    rtol=1e-6,
    atol=1e-6,
)
```

#### Step 7 — Edge cases / production considerations

For financial values, choose representations based on exactness requirements. For large aggregates, also consider integer overflow when summing narrow integer arrays.

**Key lesson:** numerical precision is an engineering parameter that should be tested at the required tolerance.

---

## Question 23 — Stop a Function from Mutating Its Caller

**Difficulty:** Hard

**Topics tested:** views, copies, aliasing, `.copy()`, read-only arrays, `flags.writeable`, API design, contiguity.

### Problem

A preprocessing function receives an input array and normalizes the first column in place:

```python
def normalize_first_column(data):
    first_col = data[:, 0]
    first_col -= first_col.mean()
    return data
```

A caller expects the input `raw` to remain unchanged.

### What you need to determine/build

1. explain the aliasing bug,
2. create a non-mutating version,
3. write a test that proves the input did not change,
4. show how a read-only input can act as a defensive check.

### Constraints / assumptions

- The function may allocate a new array intentionally.
- Do not solve the problem by changing the caller's expectation.

### Expected skills

- Aliasing diagnosis.
- Safe API design.
- Mutation testing.
- View/copy reasoning.

### Solution / How to Solve

#### Step 1 — Understand the problem

`data[:, 0]` is a basic slice and therefore a view of the first column. `-=` mutates the shared buffer.

#### Step 2 — Predict shape/dtype/memory behavior

The safe implementation will create independent storage for the returned array.

#### Step 3 — Choose the NumPy approach

Call `.copy()` at the function boundary when output mutation must not affect the input.

#### Step 4 — Implement

```python
import numpy as np

def normalize_first_column(data):
    result = np.asarray(data).copy()
    first_col = result[:, 0]
    first_col -= first_col.mean()
    return result

raw = np.array(
    [
        [10.0, 100.0],
        [20.0, 200.0],
        [30.0, 300.0],
    ]
)

before = raw.copy()
normalized = normalize_first_column(raw)

print(raw)
print(normalized)
```

#### Step 5 — Explain the implementation

The function makes one deliberate ownership decision: the returned result must be independent. Internal slicing can then safely mutate the copied storage.

A read-only source can provide an additional guard:

```python
raw.flags.writeable = False
```

Attempted mutation of the original should fail.

#### Step 6 — Verify the result

```python
np.testing.assert_array_equal(raw, before)
assert not np.shares_memory(raw, normalized)

raw.flags.writeable = False

try:
    raw[0, 0] = 999.0
except ValueError:
    pass
else:
    raise AssertionError("Expected a write-protection error")
```

#### Step 7 — Edge cases / production considerations

Do not copy every array by default. Copy only when independent ownership is part of the contract, mutation is expected, or retention/lifetime considerations justify it.

**Key lesson:** ownership should be explicit at API boundaries where mutation could corrupt upstream data.

---

## Question 24 — Merge Chunk Statistics Without Averaging Means or Percentiles

**Difficulty:** Hard

**Topics tested:** chunked aggregation, weighted mean, variance merging concept, percentile limitations, numerical accuracy.

### Problem

Two chunks contain:

```python
chunk_a = np.array([10.0, 20.0, 30.0])
chunk_b = np.array([100.0, 110.0])
```

The engineer proposes:

```python
global_mean = np.mean([chunk_a.mean(), chunk_b.mean()])
```

and similarly suggests averaging each chunk's p95 to estimate the global p95.

### What you need to determine/build

1. Compute the correct global mean.
2. Explain the weighted structure required to merge means.
3. Explain the concept behind merging variance from chunk summary statistics.
4. Explain why averaging chunk percentiles is not generally valid.
5. Produce a test comparing the exact global mean against the merged calculation.

### Constraints / assumptions

Do not implement a full general quantile algorithm.

### Expected skills

- Mergeable statistics.
- Numerical correctness.
- Understanding the limits of chunk summaries.

### Solution / How to Solve

#### Step 1 — Understand the problem

Chunk means represent different numbers of observations, so a simple unweighted average gives equal weight to unequal sample sizes.

#### Step 2 — Predict shape/dtype/memory behavior

Each chunk contributes scalar `sum`, `count`, and potentially other sufficient statistics.

#### Step 3 — Choose the NumPy approach

Merge means through total sum divided by total count.

#### Step 4 — Implement

```python
import numpy as np

chunk_a = np.array([10.0, 20.0, 30.0])
chunk_b = np.array([100.0, 110.0])

sum_a, count_a = chunk_a.sum(), chunk_a.size
sum_b, count_b = chunk_b.sum(), chunk_b.size

global_mean = (sum_a + sum_b) / (count_a + count_b)
reference_mean = np.concatenate([chunk_a, chunk_b]).mean()

print(global_mean)
print(reference_mean)
```

The correct mean is:

```text
54.0
```

The naïve average of chunk means would be:

```text
(20 + 105) / 2 = 62.5
```

#### Step 5 — Explain the implementation

Mean is mergeable from sum and count.

Variance is more complicated because you need enough information about both within-chunk variation and differences between chunk means. A correct merge formula uses counts, means, and within-group sum-of-squared-deviation information; simply averaging the chunk variances is not generally correct.

Percentiles are different again. A global percentile depends on the combined distribution order, so chunk p95 values cannot generally be averaged to obtain the global p95.

#### Step 6 — Verify the result

```python
assert np.isclose(global_mean, 54.0)
assert np.isclose(global_mean, reference_mean)
assert not np.isclose(
    np.mean([chunk_a.mean(), chunk_b.mean()]),
    reference_mean,
)
```

#### Step 7 — Edge cases / production considerations

Unequal chunk sizes are the easiest way to expose the naïve-mean bug. Production aggregation designs should classify metrics by whether and how they can be merged.

**Key lesson:** choose chunk summaries based on the algebra of the statistic you need.

---

# Advanced — Questions 25–32

## Question 25 — Build a Memory-Conscious Transaction Metrics Pipeline

**Difficulty:** Advanced

**Topics tested:** dtype planning, vectorization, Boolean masks, top-k, aggregation, views/copies, temporary allocations, memory reasoning.

### Problem

You receive 10 million transaction rows with these logical columns:

- `transaction_id`
- `customer_id`
- `quantity`
- `unit_price_cents`
- `status_code`

Requirements:

1. Keep IDs exact.
2. Compute line totals in cents.
3. Filter only successful transactions with positive quantity.
4. Find the top 100 transactions by amount.
5. Compute total successful sales.
6. Avoid unnecessary full-size copies.
7. Explain which operations are views and which allocate copies.

### What you need to determine/build

Design a NumPy-only approach for the batch. You do not need to generate all 10 million rows in the answer, but your solution must show the core operations and memory reasoning.

Estimate the raw memory for:

- 10 million `int64` transaction IDs,
- 10 million `int64` customer IDs,
- 10 million `int16` quantities,
- 10 million `int64` prices,
- 10 million `int8` status codes.

### Constraints / assumptions

- `status_code == 1` means success.
- `quantity >= 0`.
- `quantity * unit_price_cents` may exceed `int32`, so use a safe accumulation dtype.
- Do not use pandas.

### Expected skills

- Production dtype planning.
- Vectorization.
- Masking.
- Top-k.
- Memory estimation.
- Avoiding unnecessary copies.

### Solution / How to Solve

#### Step 1 — Understand the problem

The first goal is to keep source storage compact while preserving correctness. The second is to avoid turning every intermediate expression into a full 10-million-element copy.

#### Step 2 — Predict shape/dtype/memory behavior

Raw source storage:

```text
transaction_id: 10,000,000 × 8 = 80 MB
customer_id:    10,000,000 × 8 = 80 MB
quantity:       10,000,000 × 2 = 20 MB
price:          10,000,000 × 8 = 80 MB
status:         10,000,000 × 1 = 10 MB
```

Total raw element storage ≈ 270,000,000 bytes ≈ 257.49 MiB.

A Boolean mask over 10 million rows is another ~10 MB.

#### Step 3 — Choose the NumPy approach

Compute line totals with explicit `int64` accumulation. Build one success mask and reuse it. Use `argpartition` for top-k.

#### Step 4 — Implement

```python
import numpy as np

n = 10_000

rng = np.random.default_rng(7)

transaction_id = np.arange(1, n + 1, dtype=np.int64)
customer_id = rng.integers(1, 100_000, size=n, dtype=np.int64)
quantity = rng.integers(0, 20, size=n, dtype=np.int16)
unit_price_cents = rng.integers(100, 50_000, size=n, dtype=np.int64)
status_code = rng.integers(0, 2, size=n, dtype=np.int8)

line_total_cents = np.multiply(
    quantity,
    unit_price_cents,
    dtype=np.int64,
)

success_mask = (status_code == 1) & (quantity > 0)

successful_positions = np.flatnonzero(success_mask)
successful_amounts = line_total_cents[successful_positions]

total_successful_sales = successful_amounts.sum(dtype=np.int64)

k = min(100, successful_amounts.size)

if k:
    candidate = np.argpartition(
        -successful_amounts,
        kth=k - 1,
    )[:k]
    order = np.argsort(-successful_amounts[candidate])
    top_positions_in_selection = candidate[order]

    top_original_positions = successful_positions[top_positions_in_selection]
    top_transaction_ids = transaction_id[top_original_positions]
    top_amounts = line_total_cents[top_original_positions]
else:
    top_transaction_ids = np.empty(0, dtype=np.int64)
    top_amounts = np.empty(0, dtype=np.int64)
```

#### Step 5 — Explain the implementation

The line-total result is a new array, but aligned source columns do not need to be copied merely to filter rows. `flatnonzero` produces the selected positions; advanced indexing into the source columns then creates selected arrays.

For a truly large workload, even the selected amount array could be avoided or processed in chunks if memory budgets are tight.

#### Step 6 — Verify the result

```python
assert line_total_cents.shape == quantity.shape
assert line_total_cents.dtype == np.int64

assert total_successful_sales == line_total_cents[success_mask].sum(
    dtype=np.int64
)

if top_amounts.size:
    assert top_amounts.size <= 100
    assert np.all(
        top_amounts[:-1] >= top_amounts[1:]
    )

    reference = np.sort(line_total_cents[success_mask])[-top_amounts.size:]
    np.testing.assert_array_equal(
        np.sort(top_amounts),
        reference,
    )
```

#### Step 7 — Edge cases / production considerations

Important edge cases:

- zero successful rows,
- fewer than 100 successful rows,
- duplicated amounts,
- quantity overflow if the domain range grows,
- source arrays that are reused by later pipeline stages.

**Engineering lesson:** production NumPy design is not “make everything vectorized.” It is “preserve correctness while controlling dtype width, copies, temporaries, and peak memory.”

---

## Question 26 — Design a Deterministic CDC Latest-State Extract

**Difficulty:** Advanced

**Topics tested:** `lexsort`, stable/deterministic ordering, `unique(return_index=True)`, aligned columns, fancy indexing, missing timestamps.

### Problem

A CDC batch contains 12 update events for customer records:

```python
customer_id = np.array([10, 10, 20, 30, 20, 10, 30, 20, 40, 40, 30, 10])
version = np.array([1, 2, 1, 1, 3, 3, 2, 2, 1, 2, 3, 3])
status = np.array(
    ["A", "B", "A", "A", "C", "C", "B", "B", "A", "C", "D", "D"]
)
```

Keep one row per customer using the highest `version`. If the same `(customer_id, version)` appears multiple times, keep the last input occurrence.

### What you need to determine/build

Return deterministic selected original positions and use them to retrieve all aligned columns.

### Constraints / assumptions

- The batch order is not guaranteed to be sorted.
- Use NumPy only.
- The tie rule must be deterministic.

### Expected skills

- Multi-key ordering.
- Latest-state extraction.
- Correct aligned-column selection.
- Deterministic tie handling.

### Solution / How to Solve

#### Step 1 — Understand the problem

The ordering rule is:

1. customer ascending,
2. version descending,
3. original position descending.

Then take the first row for each customer after sorting.

#### Step 2 — Predict shape/dtype/memory behavior

There are four unique customers, so four rows survive.

#### Step 3 — Choose the NumPy approach

Use `lexsort` and then `unique(return_index=True)`.

#### Step 4 — Implement

```python
import numpy as np

customer_id = np.array([10, 10, 20, 30, 20, 10, 30, 20, 40, 40, 30, 10])
version = np.array([1, 2, 1, 1, 3, 3, 2, 2, 1, 2, 3, 3])
status = np.array(
    ["A", "B", "A", "A", "C", "C", "B", "B", "A", "C", "D", "D"]
)

original_pos = np.arange(customer_id.size)

sort_pos = np.lexsort(
    (
        -original_pos,
        -version,
        customer_id,
    )
)

sorted_customer_id = customer_id[sort_pos]

unique_customer_ids, first_positions = np.unique(
    sorted_customer_id,
    return_index=True,
)

selected_positions = sort_pos[first_positions]

selected_customers = customer_id[selected_positions]
selected_versions = version[selected_positions]
selected_status = status[selected_positions]

print(selected_positions)
print(selected_customers)
print(selected_versions)
print(selected_status)
```

Expected state:

```text
customers: [10 20 30 40]
versions:  [3 3 3 2]
status:    ['D' 'C' 'D' 'C']
```

#### Step 5 — Explain the implementation

For customer 10, version 3 appears at positions 5 and 11, so the last occurrence, position 11, wins. The same ordering logic resolves all ties before uniqueness is applied.

#### Step 6 — Verify the result

```python
np.testing.assert_array_equal(
    selected_customers,
    np.array([10, 20, 30, 40]),
)

np.testing.assert_array_equal(
    selected_versions,
    np.array([3, 3, 3, 2]),
)

np.testing.assert_array_equal(
    selected_status,
    np.array(["D", "C", "D", "C"]),
)
```

#### Step 7 — Edge cases / production considerations

Test duplicate keys, tied versions, a single record per key, and empty input. If version semantics can be missing or invalid, define that policy before sorting.

**Engineering lesson:** deterministic deduplication is a correctness requirement for state reconstruction.

---

## Question 27 — Process a Memory-Mapped Sensor File in Chunks

**Difficulty:** Advanced

**Topics tested:** `.npy`, `np.save`, `np.load(..., mmap_mode="r")`, chunking, partial aggregation, NaN/sentinel/infinity handling, rolling windows.

### Problem

A `.npy` file contains a large `float32` sensor stream. Some values may be:

- `NaN`,
- `-9999.0`,
- `+inf`,
- `-inf`.

The file is larger than comfortable RAM capacity.

You must compute:

1. count of valid readings,
2. global valid mean,
3. global valid minimum,
4. global valid maximum,
5. a 60-sample rolling mean for one manageable chunk.

### What you need to determine/build

Use memory mapping and chunked processing. Normalize invalid representations into a validity rule without modifying the source file.

### Constraints / assumptions

- Valid means finite and not equal to `-9999`.
- Do not load the complete file into a normal ndarray.
- The rolling calculation only needs one selected chunk.

### Expected skills

- Memory mapping.
- Chunked aggregation.
- Missing/invalid data handling.
- Stride-based rolling views.

### Solution / How to Solve

#### Step 1 — Understand the problem

The array must remain file-backed. The valid-mask computation can operate chunk by chunk.

#### Step 2 — Predict shape/dtype/memory behavior

`mmap_mode="r"` returns a memory-mapped array-like object whose data is file-backed. A chunk slice is a view-like region of the mapped data.

#### Step 3 — Choose the NumPy approach

Use:

```python
np.load(path, mmap_mode="r")
```

then maintain scalar partial statistics across chunks.

#### Step 4 — Implement

```python
import numpy as np

path = "sensor_stream.npy"

# A .npy file can be opened as a memory-mapped array without
# materializing the complete file as a normal in-memory ndarray.
mapped = np.load(
    path,
    mmap_mode="r",
    allow_pickle=False,
)

chunk_size = 1_000_000

total_sum = np.float64(0.0)
total_count = 0
global_min = np.inf
global_max = -np.inf

for start in range(0, mapped.size, chunk_size):
    stop = min(start + chunk_size, mapped.size)
    chunk = mapped[start:stop]

    valid = np.isfinite(chunk) & (chunk != -9999.0)
    valid_values = chunk[valid]

    if valid_values.size:
        total_sum += valid_values.sum(dtype=np.float64)
        total_count += valid_values.size
        global_min = min(global_min, valid_values.min())
        global_max = max(global_max, valid_values.max())

global_mean = total_sum / total_count if total_count else np.nan

# Rolling work on one manageable chunk only.
rolling_chunk = np.asarray(mapped[:100_000])
window = 60

if rolling_chunk.size >= window:
    windows = np.lib.stride_tricks.sliding_window_view(
        rolling_chunk,
        window_shape=window,
    )
    rolling_valid = (
        np.isfinite(windows)
        & (windows != -9999.0)
    )
    rolling_sum = np.where(rolling_valid, windows, 0.0).sum(axis=1)
    rolling_count = rolling_valid.sum(axis=1)

    rolling_mean = np.full(
        windows.shape[0],
        np.nan,
        dtype=np.float64,
    )

    have_data = rolling_count > 0
    rolling_mean[have_data] = (
        rolling_sum[have_data] / rolling_count[have_data]
    )
else:
    rolling_mean = np.empty(0, dtype=np.float64)
```

#### Step 5 — Explain the implementation

Only accessed pages are brought into memory through the operating system's memory-management machinery. The entire file is not materialized as an ordinary in-memory array.

The rolling windows are a stride-based view of one manageable chunk, but the subsequent reduction still performs real computation over overlapping values.

#### Step 6 — Verify the result

For a small mapped test file:

```python
reference = np.asarray(mapped[:10_000])

valid = np.isfinite(reference) & (reference != -9999.0)
valid_values = reference[valid]

if valid_values.size:
    assert np.isclose(
        global_mean,
        valid_values.mean(),
        rtol=1e-6,
        atol=1e-6,
    )
```

#### Step 7 — Edge cases / production considerations

- all values invalid,
- file shorter than one chunk,
- final chunk smaller than `chunk_size`,
- windows containing no valid values,
- random-access patterns that cause many page faults.

**Engineering lesson:** memmap controls materialization, while chunking controls computation footprint.

---

## Question 28 — Reduce Peak Memory by at Least 40% and Prove It

**Difficulty:** Advanced

**Topics tested:** temporaries, `out=`, in-place operations, reusable buffers, `tracemalloc`, peak memory, correctness testing.

### Problem

A preprocessing stage starts from:

```python
result = (a - a.mean()) / a.std() * 100 + 5
```

with a large floating-point array `a`.

The team wants a lower-allocation implementation and requires a learning benchmark of at least **40% lower measured peak allocation**.

### What you need to determine/build

1. Measure the baseline with `tracemalloc`.
2. Rewrite the pipeline to reduce temporary arrays using `out=` and in-place operations where safe.
3. Verify numerical equivalence.
4. Compute the percentage peak-memory reduction.
5. Explain why a successful result on one machine does not make 40% a universal production guarantee.

### Constraints / assumptions

- Do not mutate the caller's `a`.
- Reuse an explicitly allocated destination buffer.
- Use `float64` for the exercise.
- Treat `tracemalloc` as an allocation-comparison tool, not as a full OS RSS monitor.

### Expected skills

- Peak-memory measurement.
- Temporary elimination.
- Mutation safety.
- Performance-vs-memory trade-off reasoning.

### Solution / How to Solve

#### Step 1 — Understand the problem

The baseline can create multiple full-size temporaries. The optimized version should reuse a caller-independent work buffer.

#### Step 2 — Predict shape/dtype/memory behavior

Both implementations produce one `(N,)` `float64` output. The key difference is the number of intermediate allocations and their lifetimes.

#### Step 3 — Choose the NumPy approach

Compute mean and standard deviation once, then transform a copy using in-place operations and `out=`.

#### Step 4 — Implement

```python
import tracemalloc
import numpy as np

rng = np.random.default_rng(11)
a = rng.normal(loc=100.0, scale=15.0, size=1_000_000).astype(np.float64)

def baseline(x):
    return (x - x.mean()) / x.std() * 100.0 + 5.0

def optimized(x):
    result = x.copy()

    mean = x.mean()
    std = x.std()

    np.subtract(result, mean, out=result)
    np.divide(result, std, out=result)
    np.multiply(result, 100.0, out=result)
    np.add(result, 5.0, out=result)

    return result

def measure_peak(func, x):
    tracemalloc.start()
    result = func(x)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, current, peak

baseline_result, _, baseline_peak = measure_peak(baseline, a)
optimized_result, _, optimized_peak = measure_peak(optimized, a)

reduction_percent = (
    (baseline_peak - optimized_peak) / baseline_peak
) * 100.0

print("baseline peak:", baseline_peak)
print("optimized peak:", optimized_peak)
print("reduction %:", reduction_percent)
```

#### Step 5 — Explain the implementation

The optimized function deliberately makes one independent result copy because it must not mutate `x`. After that, the transformation reuses that buffer.

The baseline expression may involve several full-size intermediates whose lifetimes overlap.

`tracemalloc` is useful for comparing allocation behavior, but it is not a complete measurement of total operating-system process RSS or every native allocation.

#### Step 6 — Verify the result

```python
np.testing.assert_allclose(
    optimized_result,
    baseline_result,
    rtol=1e-12,
    atol=1e-12,
)

assert not np.shares_memory(a, optimized_result)

assert reduction_percent >= 40.0, (
    "The learning benchmark was not reached; "
    "investigate allocations, input size, and measurement conditions."
)
```

#### Step 7 — Edge cases / production considerations

If the measured reduction is below 40%, inspect the allocation behavior instead of changing the metric. A smaller or larger input can alter allocator behavior and the observed ratio.

Also consider whether in-place mutation would be safe for a specific production caller. This exercise intentionally avoids mutating the input.

**Engineering lesson:** memory optimization is valid only when measured and paired with correctness tests.

---

## Question 29 — Redesign a Broadcasted Transformation Under a Hard Memory Budget

**Difficulty:** Advanced

**Topics tested:** broadcasting, memory estimation, chunking, vectorization, `out=`, peak-memory reasoning.

### Problem

You must subtract every hourly temperature in a 100,000-row sensor batch from every one of 20,000 reference temperatures.

The straightforward approach is:

```python
result = sensor[:, None] - reference[None, :]
```

The output would have shape `(100_000, 20_000)`.

You are given a strict memory budget that cannot accommodate this result.

### What you need to determine/build

1. Prove the shape mathematically.
2. Estimate raw `float32` output storage.
3. Explain why the broadcast syntax is correct but the full materialization is operationally unsafe.
4. Redesign the computation in chunks with a fixed output destination for one downstream summary: the minimum difference per sensor.

### Constraints / assumptions

- Use `float32`.
- Do not materialize the full matrix.
- Keep peak temporary storage bounded by a chosen chunk size.

### Expected skills

- Memory budgeting.
- Broadcasting redesign.
- Chunking.
- Use of `out=` and reductions.

### Solution / How to Solve

#### Step 1 — Understand the problem

Broadcasting expresses the pairwise relation cleanly, but the materialized output size is enormous.

#### Step 2 — Predict shape/dtype/memory behavior

Output elements:

```text
100,000 × 20,000 = 2,000,000,000
```

At 4 bytes each:

```text
8,000,000,000 bytes ≈ 7.45 GiB
```

That is only the raw result buffer.

#### Step 3 — Choose the NumPy approach

Chunk the sensor dimension and compute only the local pairwise matrix.

#### Step 4 — Implement

```python
import numpy as np

rng = np.random.default_rng(21)

sensor = rng.normal(25.0, 5.0, size=100_000).astype(np.float32)
reference = rng.normal(25.0, 5.0, size=20_000).astype(np.float32)

chunk_size = 256
best_distance = np.empty(sensor.size, dtype=np.float32)

for start in range(0, sensor.size, chunk_size):
    stop = min(start + chunk_size, sensor.size)
    chunk = sensor[start:stop]

    distances = np.empty(
        (chunk.size, reference.size),
        dtype=np.float32,
    )

    np.subtract(
        chunk[:, None],
        reference[None, :],
        out=distances,
    )
    np.abs(distances, out=distances)

    best_distance[start:stop] = distances.min(axis=1)
```

#### Step 5 — Explain the implementation

The largest temporary now has shape `(256, 20_000)`, not `(100_000, 20_000)`.

The operation remains fully vectorized within each chunk while controlling peak memory.

#### Step 6 — Verify the result

```python
tiny_sensor = np.array([10.0, 20.0, 50.0], dtype=np.float32)
tiny_reference = np.array([12.0, 18.0, 40.0], dtype=np.float32)

expected = np.min(
    np.abs(
        tiny_sensor[:, None] - tiny_reference[None, :]
    ),
    axis=1,
)

assert expected.shape == (3,)
np.testing.assert_allclose(
    expected,
    np.array([2.0, 2.0, 10.0], dtype=np.float32),
)
```

#### Step 7 — Edge cases / production considerations

Choose chunk size from the actual memory budget, not an arbitrary “large enough” value. Measure runtime as well because smaller chunks can add loop overhead.

**Engineering lesson:** broadcasting and chunking are complementary tools; use broadcasting inside a memory-safe execution boundary.

---

## Question 30 — Diagnose Hidden Copies at an Interoperability Boundary

**Difficulty:** Advanced

**Topics tested:** contiguity, transpose, `strides`, `.flags`, `np.ascontiguousarray`, zero-copy concept, buffer protocol, `__array_interface__`.

### Problem

A large matrix is created:

```python
import numpy as np

a = np.arange(12, dtype=np.float64).reshape(3, 4)
b = a.T
```

A downstream native component expects C-contiguous memory. The engineer assumes `b` is “just a transpose” and therefore carries no performance or memory consequence.

### What you need to determine/build

1. Inspect the shape and strides of `a` and `b`.
2. Determine contiguity.
3. Explain why `b` may force a copy at a downstream boundary.
4. Use `np.ascontiguousarray` to prepare the input when required.
5. Explain the zero-copy concept and what `__array_interface__` exposes.

### Constraints / assumptions

- Do not claim that every downstream library always copies.
- Treat the copy as a compatibility requirement when the consumer explicitly requires C-contiguous storage.

### Expected skills

- Layout reasoning.
- Interoperability.
- Hidden-copy diagnosis.

### Solution / How to Solve

#### Step 1 — Understand the problem

Transpose changes axis order and strides. It often creates a view, but that view may not be C-contiguous.

#### Step 2 — Predict shape/dtype/memory behavior

- `a.shape == (3, 4)`
- `b.shape == (4, 3)`
- `b` typically shares memory with `a`
- `b` is generally not C-contiguous

#### Step 3 — Choose the NumPy approach

Inspect flags before deciding whether a layout-conversion copy is needed.

#### Step 4 — Implement

```python
import numpy as np

a = np.arange(12, dtype=np.float64).reshape(3, 4)
b = a.T

print("a.shape:", a.shape)
print("a.strides:", a.strides)
print("a C:", a.flags["C_CONTIGUOUS"])

print("b.shape:", b.shape)
print("b.strides:", b.strides)
print("b C:", b.flags["C_CONTIGUOUS"])
print("shares:", np.shares_memory(a, b))

c = np.ascontiguousarray(b)

print("c C:", c.flags["C_CONTIGUOUS"])
print("c shares with a:", np.shares_memory(a, c))

print(a.__array_interface__)
```

#### Step 5 — Explain the implementation

`b` is a different logical view over the same underlying storage. A consumer that requires C-contiguous storage cannot necessarily consume the same strided representation directly.

`np.ascontiguousarray` returns the original array when it is already appropriately contiguous; otherwise it creates a contiguous copy.

`__array_interface__` exposes metadata describing array memory, shape, strides, and dtype-related representation. It is one interoperability mechanism, not the only one.

#### Step 6 — Verify the result

```python
assert np.shares_memory(a, b)
assert not b.flags["C_CONTIGUOUS"]

assert c.flags["C_CONTIGUOUS"]
assert np.array_equal(c, b)

assert isinstance(
    a.__array_interface__,
    dict,
)
assert "shape" in a.__array_interface__
assert "strides" in a.__array_interface__
assert "typestr" in a.__array_interface__
```

#### Step 7 — Edge cases / production considerations

Zero-copy interoperability is a capability, not a promise. Dtype, layout, lifetime, ownership, and consumer requirements all matter.

**Engineering lesson:** at high-throughput boundaries, layout metadata can be as important as the values themselves.

---

## Question 31 — Repair a NumPy 2 API Boundary with `copy=False` and Read-Only Input

**Difficulty:** Advanced

**Topics tested:** NumPy 2 copy semantics, `np.array(copy=False)`, `np.asarray`, read-only arrays, mutation safety, API design.

### Problem

An API boundary contains:

```python
def transform(x):
    x = np.array(x, copy=False)
    x += 1
    return x
```

A caller sometimes passes a Python list and sometimes passes a read-only ndarray. The code makes unsafe assumptions about copying and mutability.

### What you need to determine/build

1. Explain the NumPy 2 meaning of `copy=False`.
2. Explain why a Python list may cause the operation to fail rather than silently allocating a copy.
3. Rewrite the function for one of these contracts:

> “The function returns an independently mutable result and never mutates caller-owned input.”

4. Add a test covering:
   - Python list input,
   - ndarray input,
   - read-only ndarray input.

### Constraints / assumptions

- Use NumPy 2 semantics.
- The function must not mutate caller-owned input.
- Do not rely on “copy only if convenient” semantics for `copy=False`.

### Expected skills

- Version-correct API reasoning.
- Ownership contracts.
- Mutation safety.
- `np.asarray`.

### Solution / How to Solve

#### Step 1 — Understand the problem

In current NumPy 2 semantics, `np.array(x, copy=False)` means that copying is not permitted. When an ndarray cannot be returned without a copy, an exception can be raised.

That is different from treating `copy=False` as a soft preference.

#### Step 2 — Predict shape/dtype/memory behavior

The safe API wants its own mutable storage regardless of whether the caller provides a list, a normal ndarray, or a read-only ndarray.

#### Step 3 — Choose the NumPy approach

First normalize array-like input with `np.asarray`, then explicitly `.copy()` because independent ownership is part of the API contract.

#### Step 4 — Implement

```python
import numpy as np

def transform(x):
    result = np.asarray(x).copy()
    result += 1
    return result

source = np.array([1, 2, 3], dtype=np.int64)
read_only = np.array([10, 20, 30], dtype=np.int64)
read_only.flags.writeable = False

from_list = transform([4, 5, 6])
from_array = transform(source)
from_read_only = transform(read_only)

print(from_list)
print(from_array)
print(from_read_only)
```

#### Step 5 — Explain the implementation

`np.asarray` is appropriate when normalizing array-like inputs without requiring an unnecessary copy at that stage. The explicit `.copy()` is then intentional because the function promises independent mutable output.

This is an example where “avoid all copies” would conflict with the correctness contract.

#### Step 6 — Verify the result

```python
np.testing.assert_array_equal(from_list, np.array([5, 6, 7]))
np.testing.assert_array_equal(from_array, np.array([2, 3, 4]))
np.testing.assert_array_equal(from_read_only, np.array([11, 21, 31]))

np.testing.assert_array_equal(
    source,
    np.array([1, 2, 3]),
)

np.testing.assert_array_equal(
    read_only,
    np.array([10, 20, 30]),
)

assert not np.shares_memory(source, from_array)
assert not np.shares_memory(read_only, from_read_only)
```

#### Step 7 — Edge cases / production considerations

An API that needs zero-copy behavior should document that as a separate contract. Do not hide a required ownership copy behind ambiguous API behavior.

**Engineering lesson:** `copy=False` is a semantic constraint, while `.copy()` can be a deliberate correctness boundary.

---

## Question 32 — Design a Complete Module-2.2 Quality and Memory Gate

**Difficulty:** Advanced

**Topics tested:** ndarray/dtypes, vectorization, broadcasting, masks, aggregations, missing values, views/copies, memory mapping, chunking, testing, production judgment.

### Problem

You are reviewing a NumPy-only batch pipeline that ingests sensor events with aligned arrays:

```python
device_id = np.array([101, 101, 102, 102, 103, 103, 103], dtype=np.int64)
reading = np.array([10.0, -9999.0, 20.0, np.nan, 30.0, np.inf, 40.0])
threshold = np.array([15.0, 15.0, 15.0, 15.0, 35.0, 35.0, 35.0])
```

The pipeline must:

1. identify valid readings,
2. flag valid readings above threshold,
3. calculate per-device valid mean,
4. calculate overall p95 on valid readings,
5. preserve input arrays,
6. avoid unnecessary copies,
7. be extensible to a `.npy` batch larger than RAM,
8. expose enough diagnostics to catch dtype, memory, and mutation mistakes.

### What you need to determine/build

Design the core implementation and explain:

- dtype decisions,
- mask semantics,
- broadcast behavior,
- grouping strategy,
- aggregation decisions,
- missing-value policy,
- how you would convert the design to chunked/memmap execution,
- how you would test non-mutation,
- where views and copies occur.

### Constraints / assumptions

- `-9999` is a missing sentinel.
- NaN is missing.
- infinity is invalid.
- Threshold comparison should only apply to valid readings.
- No imputation is required.
- Use NumPy only.
- Do not mutate the original inputs.

### Expected skills

- Integrating the entire module.
- Designing for correctness, memory safety, and scalability.
- Explaining trade-offs rather than merely producing code.

### Solution / How to Solve

#### Step 1 — Understand the problem

The pipeline is easiest to reason about as:

```text
source arrays
→ validity mask
→ valid-only business condition
→ group codes
→ partial/full aggregations
→ diagnostics
```

The central constraint is that invalid values must not silently become valid business data.

#### Step 2 — Predict shape/dtype/memory behavior

All input arrays are shape `(7,)`.

The validity mask is `(7,)` Boolean.

Threshold comparison is `(7,)` because all thresholds are aligned element by element.

The unique device array has shape `(3,)`.

#### Step 3 — Choose the NumPy approach

Use:

- `np.isfinite` + sentinel detection for validity,
- `np.where` or direct masked assignment for valid threshold flags,
- `np.unique(..., return_inverse=True)` for device groups,
- `np.bincount` for sum/count,
- `np.nanpercentile` only after invalid non-NaN values have also been removed,
- explicit copies only where mutation safety requires them.

#### Step 4 — Implement

```python
import numpy as np

device_id = np.array(
    [101, 101, 102, 102, 103, 103, 103],
    dtype=np.int64,
)
reading = np.array(
    [10.0, -9999.0, 20.0, np.nan, 30.0, np.inf, 40.0],
    dtype=np.float64,
)
threshold = np.array(
    [15.0, 15.0, 15.0, 15.0, 35.0, 35.0, 35.0],
    dtype=np.float64,
)

reading_before = reading.copy()
threshold_before = threshold.copy()

valid = (
    np.isfinite(reading)
    & (reading != -9999.0)
)

above_threshold = valid & (reading > threshold)

devices, group_codes = np.unique(
    device_id,
    return_inverse=True,
)

valid_values = np.where(valid, reading, 0.0)
valid_indicator = valid.astype(np.int64)

sum_by_device = np.bincount(
    group_codes,
    weights=valid_values,
)
count_by_device = np.bincount(
    group_codes,
    weights=valid_indicator,
)

mean_by_device = np.full(
    devices.shape,
    np.nan,
    dtype=np.float64,
)

has_valid = count_by_device > 0
mean_by_device[has_valid] = (
    sum_by_device[has_valid] / count_by_device[has_valid]
)

overall_valid_values = reading[valid]

if overall_valid_values.size:
    overall_p95 = np.percentile(
        overall_valid_values,
        95,
    )
else:
    overall_p95 = np.nan

print("valid:", valid)
print("above threshold:", above_threshold)
print("devices:", devices)
print("means:", mean_by_device)
print("overall p95:", overall_p95)
```

#### Step 5 — Explain the implementation

The validity mask prevents `-9999`, NaN, and infinity from influencing business metrics.

The threshold condition is combined with validity so an invalid observation cannot be flagged as a real threshold violation.

`np.unique(..., return_inverse=True)` turns arbitrary device IDs into compact group codes. `np.bincount` then performs group-style sums and counts.

The source arrays are not modified.

For a larger-than-RAM `.npy` batch, the same logical algorithm can be executed chunk by chunk. The global mean can be merged using total sums and counts. The global percentile is the difficult part: a naïve average of chunk p95 values is not valid, so an exact percentile may require a different data strategy.

For explicit file-backed storage, `np.memmap` is another API worth recognizing:

```python
mapped = np.memmap(
    "sensor_stream.raw",
    dtype=np.float32,
    mode="r",
    shape=(10_000_000,),
)
```

Use the raw-file form only when the binary layout and shape are already part of the file contract. For NumPy-native persisted arrays, `.npy` plus `np.load(..., mmap_mode="r")` preserves the array metadata.

When loading data from a source that you do not fully trust, keep:

```python
np.load(path, allow_pickle=False)
```

as the safe default unless object deserialization is explicitly required.

#### Step 6 — Verify the result

```python
np.testing.assert_array_equal(
    valid,
    np.array([True, False, True, False, True, False, True]),
)

np.testing.assert_array_equal(
    above_threshold,
    np.array([False, False, True, False, False, False, True]),
)

np.testing.assert_array_equal(
    devices,
    np.array([101, 102, 103]),
)

np.testing.assert_allclose(
    mean_by_device,
    np.array([10.0, 20.0, 35.0]),
)

assert np.isclose(
    overall_p95,
    np.percentile(
        np.array([10.0, 20.0, 30.0, 40.0]),
        95,
    ),
)

np.testing.assert_array_equal(reading, reading_before)
np.testing.assert_array_equal(threshold, threshold_before)
```

#### Step 7 — Edge cases / production considerations

A production quality gate should additionally test:

- empty batches,
- all-invalid batches,
- one-device batches,
- very large integer IDs,
- dtype validation,
- chunk boundaries,
- memory usage,
- non-contiguous inputs,
- accidental mutation,
- exact handling of missing sentinels,
- threshold semantics at equality boundaries.

For a memmap implementation, monitor runtime and access pattern as well as memory. For memory-sensitive execution, the raw `.nbytes` of inputs is only the starting point; include temporaries, outputs, and process overhead in the memory budget.

**Engineering lesson:** Module 2.2 is complete only when you can connect array representation, vectorized computation, selection, aggregation, missingness, and memory behavior into one correct production pipeline.

---

# Module Coverage Map

| Question | Difficulty | Primary topics | Secondary topics |
|---|---|---|---|
| 01 | Basic | ndarray metadata, dtype, memory | contiguity |
| 02 | Basic | array creation, dtype | deterministic RNG |
| 03 | Basic | broadcasting | `newaxis`, shape prediction |
| 04 | Basic | Boolean masks | counting, validation |
| 05 | Basic | axis semantics | `keepdims` |
| 06 | Basic | NaN, sentinel, NaT, infinity | validity masks |
| 07 | Basic | views/copies | slicing, mutation |
| 08 | Basic | float precision, dtype | large integer IDs |
| 09 | Moderate | vectorization | `where`, `clip` |
| 10 | Moderate | broadcasting | reductions, `keepdims` |
| 11 | Moderate | `searchsorted` | binning |
| 12 | Moderate | `argpartition` | top-k, sorting |
| 13 | Moderate | 3-D aggregation | tuple axes, `keepdims` |
| 14 | Moderate | NaN-safe aggregation | percentiles, `ddof` |
| 15 | Moderate | `lexsort`, deduplication | `unique(return_index=True)` |
| 16 | Moderate | memory estimation | views, retention, memmap |
| 17 | Hard | mask debugging, aliasing | chained indexing |
| 18 | Hard | integer overflow | accumulation dtype |
| 19 | Hard | validity masks | grouped metrics |
| 20 | Hard | chunking | mergeable statistics |
| 21 | Hard | broadcasting memory risk | chunking, temporaries |
| 22 | Hard | numerical correctness | precision, `ddof` |
| 23 | Hard | views/copies | read-only arrays |
| 24 | Hard | chunked statistics | variance/percentile limits |
| 25 | Advanced | end-to-end transactions | dtype, top-k, memory |
| 26 | Advanced | CDC latest state | deterministic dedup |
| 27 | Advanced | memmap + chunking | missing data, rolling windows |
| 28 | Advanced | peak memory | `tracemalloc`, `out=` |
| 29 | Advanced | memory-budgeted broadcasting | chunking, `out=` |
| 30 | Advanced | contiguity and interop | zero-copy concepts |
| 31 | Advanced | NumPy 2 copy semantics | API ownership, read-only |
| 32 | Advanced | full-module integration | quality, memory, scalability |

# Topic Coverage Summary

| Topic | Covered? | Question numbers |
|---|---|---|
| ndarray / dtypes / memory layout | Yes | 01, 02, 08, 16, 18, 22, 25, 30, 32 |
| vectorization / broadcasting | Yes | 03, 09, 10, 21, 25, 29, 32 |
| indexing / masks / fancy indexing | Yes | 04, 07, 11, 12, 15, 17, 19, 25, 26, 32 |
| aggregations / axis semantics | Yes | 05, 13, 14, 18, 19, 20, 22, 24, 25, 27, 32 |
| NaN / missing / sentinels | Yes | 06, 08, 14, 19, 24, 27, 32 |
| views / copies / memory efficiency | Yes | 07, 16, 17, 21, 23, 25, 27, 28, 29, 30, 31, 32 |

# Final Self-Assessment

Before considering Module 2.2 mastered, you should be able to answer “yes” to all of these:

- I can predict array shape before executing common NumPy operations.
- I can predict and inspect dtype and raw memory usage.
- I can reason through broadcasting from the rightmost dimensions.
- I can distinguish basic slicing from Boolean/fancy indexing.
- I can select the correct aggregation axis from business semantics.
- I can handle NaN, sentinel, NaT, and infinity intentionally.
- I can explain integer overflow and floating-point precision risks.
- I can build deterministic latest-record selection with ordering plus uniqueness.
- I can choose `argpartition` when a top-k problem does not require a full sort.
- I can reason about which statistics can be merged across chunks.
- I can explain view, copy, aliasing, ownership, and mutation risk.
- I can prove memory overlap with `np.shares_memory`.
- I understand the conservative role of `np.may_share_memory`.
- I can use `.copy()` deliberately rather than automatically.
- I can use read-only arrays as a mutation-safety mechanism.
- I understand NumPy 2 `copy=False` semantics and the role of `np.asarray`.
- I can reduce temporary allocations with in-place operations and `out=`.
- I can estimate peak memory rather than relying only on final output size.
- I can use chunking and memory mapping when data does not fit comfortably in RAM.
- I can explain why `sliding_window_view` can avoid input-window copies but does not make computation free.
- I understand why raw `as_strided` is dangerous.
- I can inspect contiguity and reason about downstream copies.
- I understand the zero-copy concept and the role of the buffer protocol / `__array_interface__`.
- I can explain why NumPy is powerful for dense numerical arrays but is not itself a distributed data-engineering execution engine.
- I measure runtime and memory behavior instead of assuming an optimization is effective.

## Final Engineering Question

For any large NumPy operation, ask:

```text
1. What is the input shape?
2. What is the input dtype?
3. What is the output shape?
4. What is the output dtype?
5. Will this return a view or a copy?
6. Does the result share memory with the source?
7. Who owns the underlying buffer?
8. Can mutation affect another pipeline stage?
9. How many temporary arrays are created?
10. What is the peak memory?
11. Can the dtype be safely smaller?
12. Can I use `out=`?
13. Can I safely use an in-place operation?
14. Should I chunk the computation?
15. Should I memory-map the input?
16. Is the array contiguous?
17. Could an interoperability boundary make a hidden copy?
18. Does the numerical representation preserve correctness?
19. What happens for empty/all-invalid/overflow/tie cases?
20. Have I verified the result with deterministic tests?
```

The goal is not to memorize 32 solutions. The goal is to develop the habit of predicting **shape, dtype, memory, ownership, mutation, and performance** before writing production NumPy code.
