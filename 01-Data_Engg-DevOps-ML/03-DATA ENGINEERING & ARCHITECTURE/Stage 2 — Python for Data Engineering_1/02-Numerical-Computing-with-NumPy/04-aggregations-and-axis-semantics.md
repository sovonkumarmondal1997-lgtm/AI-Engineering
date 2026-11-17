# NumPy Aggregations and Axis Semantics

> **Stage 2 — Python for Data Engineering**  
> **Module 2.2 — Numerical Computing with NumPy**  
> **Topic 04 — Aggregations and Axis Semantics**  
> **Target:** NumPy 2.x

---

## Learning goals

By the end of this chapter, you should be able to:

- Explain what an aggregation and a reduction are.
- Use `sum`, `mean`, `min`, `max`, `argmin`, `argmax`, `std`, `var`, `prod`, `any`, and `all`.
- Reason about `axis=0`, `axis=1`, `axis=None`, and tuple axes instead of memorizing labels.
- Predict the output shape of a reduction before executing it.
- Use `keepdims=True` when the reduced result must remain broadcast-compatible.
- Aggregate 2-D and 3-D data correctly.
- Compute percentiles, quantiles, and medians, including p50, p95, and p99 latency.
- Understand `cumsum`, `cumprod`, and `np.diff`.
- Build group-style aggregates with `np.bincount`, `np.unique(return_inverse=True)`, `np.add.at`, and `np.add.reduceat`.
- Build histograms and assign records to bins with `np.histogram` and `np.digitize`.
- Reason about floating-point accuracy, pairwise summation, catastrophic cancellation, `ddof`, and wider accumulation dtypes.
- Detect and prevent integer overflow during reductions.
- Use `np.corrcoef` and `np.cov` for quick profiling.
- Aggregate data chunk-by-chunk when the entire dataset should not be loaded at once.
- Merge partial count/sum/min/max statistics correctly.
- Merge means and variances correctly rather than averaging chunk statistics naïvely.
- Explain why exact global percentiles cannot be obtained by simply averaging chunk percentiles.
- Design production-style metrics pipelines and test them against small, hand-computed examples.

The central habit throughout this chapter is:

> **Before executing an aggregation, identify what each axis means, decide which axis is being collapsed, and predict the output shape.**

---

# 1. Why aggregations matter in Data Engineering

Most production data pipelines transform large volumes of raw records into smaller sets of metrics.

Examples:

```text
transactions
    ↓
daily revenue

sensor readings
    ↓
per-device min / max / mean

API events
    ↓
p50 / p95 / p99 latency

orders
    ↓
count by customer / product / store

quality checks
    ↓
pass rate / invalid count
```

An **aggregation** summarizes many values into a smaller result.

For example:

```python
import numpy as np

amounts = np.array([100, 200, 300, 400])

total = amounts.sum()

print(total)
```

Output:

```text
1000
```

Four values became one value.

That operation is a **reduction**: many values are collapsed into fewer values.

The difficult part begins when the data has more than one dimension.

Suppose:

```text
rows    = days
columns = stores
```

Then:

```python
sales.sum(axis=0)
```

and:

```python
sales.sum(axis=1)
```

are both valid, but they answer different business questions.

A result can be numerically correct while semantically wrong.

For example:

```text
"I calculated a sum successfully."

does not guarantee:

"I calculated the sum the business requested."
```

That is why axis semantics are one of the most important parts of this topic.

---

# 2. Raw data versus summarized data

Think of a pipeline as moving from detail to summary:

```text
raw records
    ↓
selection / filtering
    ↓
clean records
    ↓
aggregation
    ↓
metrics
    ↓
dashboard / report / alert / feature
```

Aggregations support:

- dashboards,
- reporting,
- monitoring,
- SLA/SLO reporting,
- feature engineering,
- anomaly detection,
- customer metrics,
- operational analytics,
- data-quality reporting.

Examples:

### Daily sales

```text
2026-09-20 → 1,250,000 cents
2026-09-21 → 1,410,000 cents
2026-09-22 → 1,330,000 cents
```

### API performance

```text
p50 = 120 ms
p95 = 480 ms
p99 = 1200 ms
```

### Data-quality monitoring

```text
rows_processed = 10,000,000
invalid_rows = 12,000
pass_rate = 99.88%
```

The aggregation function is only part of the engineering decision. You must also define:

```text
What data?
Which axis?
Which statistic?
Which dtype?
What precision?
How much memory?
Can it be processed incrementally?
```

---

# 3. What is a reduction?

Start with one-dimensional data:

```python
import numpy as np

a = np.array([10, 20, 30, 40])

print(a.sum())
```

Output:

```text
100
```

Conceptually:

```text
[10, 20, 30, 40]
       ↓
      sum
       ↓
      100
```

A reduction collapses values into a summary.

Now consider a matrix:

```text
4 × 5
```

A reduction can collapse one dimension:

```text
4 × 5
   ↓
5 values
```

or the other:

```text
4 × 5
   ↓
4 values
```

or both:

```text
4 × 5
   ↓
1 value
```

This is why the `axis` argument matters.

---

# 4. Selection, transformation, and reduction are different

These three ideas should not be confused.

## Selection

Selection chooses some existing values.

```python
a[a > 100]
```

Conceptually:

```text
many values
    ↓
choose some values
```

## Transformation

A transformation usually keeps a corresponding result for each input value.

```python
a * 2
```

Conceptually:

```text
N values
  ↓
N transformed values
```

## Reduction

A reduction summarizes many values.

```python
a.sum()
```

Conceptually:

```text
N values
  ↓
1 summary
```

This distinction becomes extremely useful when reading a pipeline.

---

# 5. The core reduction functions

NumPy provides many reduction operations.

The core functions in this topic are:

```python
a.sum()
a.mean()
a.min()
a.max()
a.argmin()
a.argmax()
a.std()
a.var()
a.prod()
a.any()
a.all()
```

We will learn each one, then apply them across axes.

---

# 6. `sum`

## What is it?

`sum` adds values.

```python
import numpy as np

a = np.array([10, 20, 30])

print(a.sum())
```

Output:

```text
60
```

## Why use it?

Typical Data Engineering applications:

- total revenue,
- event counts,
- total bytes,
- total quantities,
- total sensor exposure.

Example:

```python
revenue_cents = np.array(
    [5000, 12000, 3000, 8000],
    dtype=np.int64,
)

total_revenue = revenue_cents.sum()

print(total_revenue)
```

Output:

```text
28000
```

The result represents 28,000 cents.

## Important consideration

The dtype used during accumulation matters. A narrow integer dtype may overflow. We return to this in the numerical-safety section.

---

# 7. `mean`

`mean` computes the arithmetic average.

```python
import numpy as np

latency = np.array([100, 120, 140, 160])

print(latency.mean())
```

Output:

```text
130.0
```

Conceptually:

```text
sum / count
```

Data Engineering uses:

- average order value,
- average sensor reading,
- average processing time,
- average throughput.

### Common mistake

Do not use mean when the business question concerns a tail.

For latency, for example:

```text
mean = typical arithmetic average
p95  = upper-tail threshold
p99  = more extreme upper-tail threshold
```

Averages and percentiles answer different questions.

---

# 8. `min` and `max`

```python
import numpy as np

a = np.array([12, 4, 25, 9])

print(a.min())
print(a.max())
```

Output:

```text
4
25
```

Use them for:

- minimum/maximum price,
- earliest/latest numeric counter,
- sensor ranges,
- smallest/largest batch,
- operational boundaries.

Be careful: `min` and `max` return **values**, not positions.

---

# 9. `argmin` and `argmax`

These functions return positions.

```python
import numpy as np

a = np.array([12, 4, 25, 9])

print(a.min())
print(a.argmin())

print(a.max())
print(a.argmax())
```

Output:

```text
4
1
25
2
```

The mental model is:

```text
min
→ "What is the smallest value?"

argmin
→ "Where is the smallest value?"

max
→ "What is the largest value?"

argmax
→ "Where is the largest value?"
```

This is useful when you need to retrieve an aligned record.

For example:

```python
order_id = np.array([101, 102, 103, 104])
amount = np.array([500, 100, 900, 300])

position = amount.argmax()

print(order_id[position])
print(amount[position])
```

Output:

```text
103
900
```

---

# 10. `std` and `var`

## Variance

Variance measures the average squared deviation around the mean.

## Standard deviation

Standard deviation is the square root of variance and is expressed in the same units as the input.

```python
import numpy as np

latency = np.array([100, 110, 120, 130, 140])

print(latency.var())
print(latency.std())
```

For an engineering workflow, the important first questions are:

```text
What does the spread mean?
What population am I describing?
What ddof should I use?
```

---

# 11. `ddof=0` versus `ddof=1`

NumPy's variance and standard deviation functions use a `ddof` parameter.

The divisor is conceptually:

```text
N - ddof
```

So:

```text
ddof=0
→ divide by N

ddof=1
→ divide by N-1
```

A simple demonstration:

```python
import numpy as np

x = np.array([2.0, 4.0, 6.0, 8.0])

population_std = x.std(ddof=0)
sample_std = x.std(ddof=1)

print(population_std)
print(sample_std)
```

The values are different because the divisor is different.

### Engineering interpretation

A common conceptual distinction is:

```text
ddof=0
→ describing the observed population itself

ddof=1
→ estimating population variance/std from a sample
```

The correct choice depends on the statistical question.

### Common mistake

Do not choose `ddof=1` simply because it "looks more statistical."

Define the population and sample semantics first.

---

# 12. `prod`

`prod` multiplies values together.

```python
import numpy as np

factors = np.array([2, 3, 4])

print(factors.prod())
```

Output:

```text
24
```

Typical uses are less common than sums, but the operation appears in:

- chained multiplicative adjustments,
- conversion factors,
- compounded ratios,
- cumulative multipliers.

Like `sum`, multiplication can overflow.

---

# 13. `any`

`any` asks:

> Does at least one value evaluate to true?

```python
import numpy as np

quality_ok = np.array([True, True, False, True])

print(quality_ok.any())
```

Output:

```text
True
```

This is useful for data quality:

```python
invalid = np.array([False, False, True, False])

if invalid.any():
    print("Bad records exist")
```

Output:

```text
Bad records exist
```

---

# 14. `all`

`all` asks:

> Do all values evaluate to true?

```python
import numpy as np

quality_ok = np.array([True, True, True])

print(quality_ok.all())
```

Output:

```text
True
```

For a contract check:

```python
ids_positive = np.array([101, 202, 303])

print(np.all(ids_positive > 0))
```

Output:

```text
True
```

These operations connect aggregation directly to validation.

---

# 15. The most important mental model: axes

Now we reach the core topic.

Consider:

```python
import numpy as np

a = np.array(
    [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
    ]
)
```

Shape:

```text
(3, 4)
```

Visualize it:

```text
          columns
            ↓
        0   1   2   3
      ┌───────────────
row 0 │ 1   2   3   4
row 1 │ 5   6   7   8
row 2 │ 9  10  11  12
      ↑
     rows
```

The array has two axes:

```text
axis 0
axis 1
```

The safest rule is:

> **The axis you reduce is the dimension that gets collapsed.**

Do not rely on a memorized phrase such as "axis 0 means rows" without understanding what is being removed.

---

# 16. Axis 0

Consider:

```python
a.sum(axis=0)
```

The input shape is:

```text
(3, 4)
```

`axis=0` collapses the first dimension.

That means:

```text
3 rows collapse
4 columns remain
```

So the output shape is:

```text
(4,)
```

Manual calculation:

```text
column 0: 1 + 5 + 9  = 15
column 1: 2 + 6 + 10 = 18
column 2: 3 + 7 + 11 = 21
column 3: 4 + 8 + 12 = 24
```

Therefore:

```python
print(a.sum(axis=0))
```

Output:

```text
[15 18 21 24]
```

Visual:

```text
          columns
        0   1   2   3
      ┌───────────────
      │ 1   2   3   4
      │ 5   6   7   8
      │ 9  10  11  12
      └───────────────
        ↓   ↓   ↓   ↓
       sum sum sum sum

       [15, 18, 21, 24]
```

Mental rule:

```text
axis=0
→ collapse the first dimension
→ keep one result per column
```

---

# 17. Axis 1

Now:

```python
a.sum(axis=1)
```

`axis=1` collapses the second dimension.

So:

```text
3 rows remain
4 columns collapse
```

Output shape:

```text
(3,)
```

Manual calculation:

```text
row 0: 1 + 2 + 3 + 4   = 10
row 1: 5 + 6 + 7 + 8   = 26
row 2: 9 + 10 + 11 + 12 = 42
```

Therefore:

```python
print(a.sum(axis=1))
```

Output:

```text
[10 26 42]
```

Visual:

```text
1  2  3  4  → 10
5  6  7  8  → 26
9 10 11 12  → 42
```

Mental rule:

```text
axis=1
→ collapse the second dimension
→ keep one result per row
```

---

# 18. Axis 0 versus axis 1

The difference is:

```text
Input shape: (3, 4)

axis=0
→ collapse size-3 dimension
→ output shape (4,)

axis=1
→ collapse size-4 dimension
→ output shape (3,)
```

A useful question is:

> **What remains after I remove the selected axis?**

That question is more reliable than memorizing labels.

---

# 19. Axis `None`

When:

```python
a.sum(axis=None)
```

NumPy reduces all dimensions.

```python
import numpy as np

a = np.array(
    [
        [1, 2],
        [3, 4],
    ]
)

print(a.sum(axis=None))
```

Output:

```text
10
```

The shape changes:

```text
(2, 2)
→ ()
```

The result is a scalar-like zero-dimensional result.

Conceptually:

```text
axis=0
→ collapse first dimension

axis=1
→ collapse second dimension

axis=None
→ collapse everything
```

For the total of an entire dataset, `axis=None` is often the clearest expression.

---

# 20. Axis summary table

| Input shape | Reduction | Output shape | What remains |
|---|---|---|---|
| `(3, 4)` | `axis=0` | `(4,)` | columns |
| `(3, 4)` | `axis=1` | `(3,)` | rows |
| `(3, 4)` | `axis=None` | `()` | nothing |
| `(3, 4)` | `axis=0, keepdims=True` | `(1, 4)` | column dimension + size-1 reduced dimension |
| `(3, 4)` | `axis=1, keepdims=True` | `(3, 1)` | row dimension + size-1 reduced dimension |

---

# 21. Prediction-first habit

For every aggregation, write:

```text
Input shape:
Axis:
Dimension being collapsed:
Expected output shape:
What each output value means:
```

For example:

```python
a = np.arange(24).reshape(4, 6)
result = a.sum(axis=1)
```

Reason first:

```text
Input shape: (4, 6)
Axis: 1
Collapsed dimension: size 6
Expected output shape: (4,)
Meaning: one sum per row
```

Only then execute it.

This habit prevents a large class of silent metric bugs.

---

# 22. At least 15 shape-prediction drills

Use:

```python
a = np.arange(24).reshape(4, 6)
b = np.arange(60).reshape(3, 4, 5)
```

Predict before running.

## Drill 1

```python
a.sum(axis=0)
```

Expected shape:

```text
(6,)
```

## Drill 2

```python
a.sum(axis=1)
```

Expected shape:

```text
(4,)
```

## Drill 3

```python
a.sum(axis=None)
```

Expected shape:

```text
()
```

## Drill 4

```python
a.mean(axis=0)
```

Shape:

```text
(6,)
```

## Drill 5

```python
a.max(axis=1)
```

Shape:

```text
(4,)
```

## Drill 6

```python
a.sum(axis=0, keepdims=True)
```

Shape:

```text
(1, 6)
```

## Drill 7

```python
a.sum(axis=1, keepdims=True)
```

Shape:

```text
(4, 1)
```

## Drill 8

```python
b.sum(axis=0)
```

Input:

```text
(3, 4, 5)
```

Output:

```text
(4, 5)
```

## Drill 9

```python
b.sum(axis=1)
```

Output:

```text
(3, 5)
```

## Drill 10

```python
b.sum(axis=2)
```

Output:

```text
(3, 4)
```

## Drill 11

```python
b.sum(axis=(0, 2))
```

Output:

```text
(4,)
```

## Drill 12

```python
b.mean(axis=(0, 1))
```

Output:

```text
(5,)
```

## Drill 13

```python
b.max(axis=(1, 2))
```

Output:

```text
(3,)
```

## Drill 14

```python
b.mean(axis=2, keepdims=True)
```

Output:

```text
(3, 4, 1)
```

## Drill 15

```python
b.sum(axis=None)
```

Output shape:

```text
()
```

Do not memorize these as isolated facts. Trace the dimensions being removed.

---

# 23. Higher-dimensional data: days, stores, products

Data Engineering frequently deals with arrays whose dimensions have business meaning.

Suppose:

```text
(days, stores, products)
```

and:

```text
sales.shape == (365, 50, 200)
```

Interpretation:

```text
axis 0 → day
axis 1 → store
axis 2 → product
```

Now the question becomes:

> Which business dimension should disappear?

---

# 24. Total sales per day

To get one number per day, collapse:

```text
stores + products
```

So:

```python
daily_sales = sales.sum(axis=(1, 2))
```

Input:

```text
(365, 50, 200)
```

Output:

```text
(365,)
```

Meaning:

```text
one total for each day
```

This is much easier to reason about if you state the semantic requirement first.

---

# 25. Total sales per store

To get one number per store, collapse:

```text
days + products
```

So:

```python
store_sales = sales.sum(axis=(0, 2))
```

Input:

```text
(365, 50, 200)
```

Output:

```text
(50,)
```

Meaning:

```text
one value per store
```

---

# 26. Total sales per product

Collapse:

```text
days + stores
```

```python
product_sales = sales.sum(axis=(0, 1))
```

Output:

```text
(200,)
```

Meaning:

```text
one total per product
```

---

# 27. Overall sales

Collapse everything:

```python
overall_sales = sales.sum(axis=None)
```

Output shape:

```text
()
```

Meaning:

```text
one number for the entire dataset
```

---

# 28. Tuple axes

A tuple allows multiple axes to be reduced together.

Example:

```python
sales.sum(axis=(0, 2))
```

For:

```text
(days, stores, products)
```

you are collapsing:

```text
days
products
```

and retaining:

```text
stores
```

Therefore:

```text
(365, 50, 200)
→ (50,)
```

This is one of the most useful advanced axis patterns.

---

# 29. `keepdims=True`

Normally, reduction removes the selected axis.

Example:

```python
import numpy as np

a = np.arange(12).reshape(3, 4)

print(a.sum(axis=1).shape)
```

Output:

```text
(3,)
```

With:

```python
a.sum(axis=1, keepdims=True)
```

the reduced axis remains, but its size becomes 1.

```python
print(a.sum(axis=1, keepdims=True).shape)
```

Output:

```text
(3, 1)
```

Visual:

```text
shape (3, 4)
        ↓
sum(axis=1)
        ↓
shape (3,)

versus

shape (3, 4)
        ↓
sum(axis=1, keepdims=True)
        ↓
shape (3, 1)
```

---

# 30. Why `keepdims=True` exists

The main reason is shape compatibility.

Suppose:

```text
X.shape = (n_rows, n_features)
```

You want to normalize every row by its row total.

Without `keepdims`:

```python
row_total = X.sum(axis=1)
```

The shape is:

```text
(n_rows,)
```

With:

```python
row_total = X.sum(axis=1, keepdims=True)
```

the shape is:

```text
(n_rows, 1)
```

That makes the broadcasting intent explicit:

```python
row_share = X / row_total
```

Every row receives the corresponding scalar denominator.

---

# 31. Production example: share of total

Suppose a 2-D matrix represents:

```text
rows = stores
columns = product categories
```

We can calculate the total per store:

```python
store_total = sales.sum(
    axis=1,
    keepdims=True,
)
```

Then:

```python
store_share = sales / store_total
```

Each row is divided by its own total.

This is a common example of aggregation feeding directly into broadcasting.

---

# 32. `mean`, `min`, and `max` with axes

All of the familiar reductions accept axis parameters.

```python
column_mean = a.mean(axis=0)
row_mean = a.mean(axis=1)

column_min = a.min(axis=0)
row_max = a.max(axis=1)
```

The shape reasoning is identical:

```text
choose axis
→ collapse that dimension
→ remaining dimensions form the output
```

This means learning `sum(axis=...)` is not just learning one function. It teaches a general NumPy pattern.

---

# 33. Percentiles, quantiles, and median

A mean answers:

> What is the arithmetic average?

A percentile answers:

> Below approximately what value does a chosen percentage of observations fall?

Common operational metrics include:

```text
p50
p95
p99
```

For latency, these are often more informative about the tail than the mean.

---

# 34. `np.median`

The median is the 50th percentile in a standard statistical sense.

```python
import numpy as np

latency = np.array([100, 120, 150, 1000, 1100])

print(np.median(latency))
```

Output:

```text
150.0
```

The median is much less affected by the extreme high values than the arithmetic mean.

---

# 35. `np.percentile`

Use:

```python
np.percentile(values, q)
```

where `q` is a percentage from 0 to 100.

Example:

```python
import numpy as np

latency = np.array([100, 120, 150, 200, 500])

print(np.percentile(latency, 50))
print(np.percentile(latency, 95))
```

The first asks for p50; the second asks for p95.

In a production system, always define what the percentile represents and which estimation method is being used when reproducible statistical semantics matter.

---

# 36. `np.quantile`

Quantile uses a 0-to-1 scale.

```python
import numpy as np

latency = np.array([100, 120, 150, 200, 500])

print(np.quantile(latency, 0.50))
print(np.quantile(latency, 0.95))
```

Conceptually:

```text
percentile:
50, 95

quantile:
0.50, 0.95
```

They express the same type of statistical idea on different scales.

---

# 37. p50, p95, and p99

For an API latency dataset:

```text
p50 → half the observations are at or below approximately this level
p95 → about 95% are at or below approximately this level
p99 → about 99% are at or below approximately this level
```

Why are p95 and p99 useful?

Suppose:

```text
mean = 120 ms
p99  = 1500 ms
```

The mean alone hides the tail.

A production monitoring dashboard may need both:

```text
mean
+
p95
+
p99
```

because users can experience the high tail even when the average looks healthy.

---

# 38. The `method=` parameter

NumPy percentiles can use different estimation methods.

For example:

```python
import numpy as np

values = np.array([10, 20, 30, 40])

p95_linear = np.percentile(
    values,
    95,
    method="linear",
)

p95_nearest = np.percentile(
    values,
    95,
    method="nearest",
)

print(p95_linear)
print(p95_nearest)
```

The exact results can differ because the methods answer slightly different questions about how the percentile is estimated between observed values.

The important engineering lesson is:

> **Statistical semantics should be explicit when exact reproducibility matters.**

Use the same method consistently across environments and versions when metrics are part of a contract.

---

# 39. Cumulative operations

A reduction collapses dimensions. A cumulative operation generally keeps a running state along an axis.

The required functions are:

```python
np.cumsum
np.cumprod
np.diff
```

---

# 40. `cumsum`

Consider daily revenue:

```python
import numpy as np

daily_revenue = np.array(
    [100, 200, 150, 300],
)

running = np.cumsum(daily_revenue)

print(running)
```

Output:

```text
[100 300 450 750]
```

The running total is:

```text
day 1 → 100
day 2 → 100 + 200 = 300
day 3 → 300 + 150 = 450
day 4 → 450 + 300 = 750
```

This is useful for:

- cumulative revenue,
- cumulative events,
- cumulative usage,
- running counters.

---

# 41. `cumprod`

```python
import numpy as np

factors = np.array([2, 3, 4])

print(np.cumprod(factors))
```

Output:

```text
[ 2  6 24]
```

Conceptually:

```text
2
2×3
2×3×4
```

It is useful for cumulative multiplicative effects.

---

# 42. `np.diff`

`np.diff` computes differences between neighboring values.

```python
import numpy as np

counter = np.array([100, 105, 113, 120])

change = np.diff(counter)

print(change)
```

Output:

```text
[5 8 7]
```

Conceptually:

```text
105 - 100 = 5
113 - 105 = 8
120 - 113 = 7
```

Notice the output is one element shorter:

```text
N
→ N-1
```

This is a common source of off-by-one bugs.

---

# 43. Period-over-period change

Suppose daily sales are:

```python
daily_sales = np.array(
    [100, 130, 125, 150],
)
```

Then:

```python
np.diff(daily_sales)
```

returns:

```text
[30, -5, 25]
```

Interpretation:

```text
day 2 - day 1
day 3 - day 2
day 4 - day 3
```

This pattern works for:

- day-over-day revenue,
- battery drain,
- event counters,
- cumulative usage.

---

# 44. Rolling 7-day totals using `cumsum`

A rolling total can be computed from cumulative sums.

Conceptually:

```text
daily values
     ↓
cumulative totals
     ↓
current cumulative
-
cumulative value 7 days earlier
     ↓
7-day total
```

For example:

```python
import numpy as np

daily = np.array(
    [10, 20, 30, 40, 50, 60, 70, 80, 90],
)

cumulative = np.cumsum(daily)

window = 7

rolling_7 = cumulative[window - 1:].copy()
rolling_7[1:] -= cumulative[:-window]

print(rolling_7)
```

The first output corresponds to the first complete seven-day window.

This is a useful pattern because it avoids repeatedly summing all seven values from scratch.

### Boundary rule

A rolling window must define what happens before a complete window exists.

Common choices include:

```text
only complete windows
or
partial windows
```

The pipeline contract must state which one is intended.

---

# 45. Group-style aggregation without pandas

NumPy does not have a DataFrame `groupby` API, but you can implement important group-style patterns with integer group identifiers.

Suppose:

```text
customer_idx
amount
```

and we need:

```text
total amount per customer
```

If customers are represented by compact integer IDs, `np.bincount` can be an excellent fit.

---

# 46. `np.bincount`

```python
import numpy as np

customer_idx = np.array([0, 1, 0, 2, 1, 0])
amount = np.array(
    [100, 200, 50, 300, 25, 75],
    dtype=np.int64,
)

revenue = np.bincount(
    customer_idx,
    weights=amount,
)

print(revenue)
```

Output:

```text
[225. 225. 300.]
```

Interpretation:

```text
customer 0 → 100 + 50 + 75 = 225
customer 1 → 200 + 25      = 225
customer 2 → 300           = 300
```

The output position is the group ID.

### Precision warning for weighted `bincount`

Weighted `np.bincount` returns floating-point totals, normally `float64`. `float64` cannot represent every integer exactly above `2**53`, so very large exact integer totals can lose units of precision:

```python
import numpy as np

group_idx = np.array([0, 0])
weights = np.array([2**53, 1], dtype=np.int64)

weighted = np.bincount(
    group_idx,
    weights=weights,
)

print(weighted)
print(weighted.dtype)
```

The mathematical result is `2**53 + 1`, but the `float64` result cannot represent that integer exactly (it is rounded to `2**53`).

An integer-preserving alternative:

```python
totals = np.zeros(1, dtype=np.int64)
np.add.at(totals, group_idx, weights)
```

---

# 47. Why `weights` matters

Without `weights`:

```python
np.bincount(customer_idx)
```

counts occurrences.

With:

```python
np.bincount(
    customer_idx,
    weights=amount,
)
```

it sums the associated weights per group.

That makes it useful for:

```text
weighted totals
revenue by customer
quantity by product
cost by category
```

---

# 48. Requirements for `bincount`

The group identifiers must be non-negative integers.

If your source keys are arbitrary strings:

```text
customer_A
customer_B
customer_C
```

you first need to encode them as compact integer group IDs.

That is where `np.unique(return_inverse=True)` becomes useful.

### `minlength`

Without `minlength`, `np.bincount` stops at the highest group ID present, so empty trailing groups can disappear and downstream array shapes can become inconsistent.

```python
import numpy as np

counts = np.bincount(
    np.array([0, 2, 2]),
    minlength=4,
)

print(counts)
```

Output:

```text
[1 0 2 0]
```

In production, pass `minlength` (the known number of groups) so every run returns the same shape.

---

# 49. `np.unique(return_inverse=True)`

Suppose:

```python
import numpy as np

customer = np.array(
    ["A", "B", "A", "C", "B", "A"],
)

groups, inverse = np.unique(
    customer,
    return_inverse=True,
)

print(groups)
print(inverse)
```

A deterministic result is:

```text
['A' 'B' 'C']
[0 1 0 2 1 0]
```

The `groups` array defines unique categories.

The `inverse` array assigns each original record a compact group code.

Conceptually:

```text
A → 0
B → 1
C → 2
```

---

# 50. Arbitrary keys → group codes → aggregation

The full pattern is:

```text
arbitrary group key
       ↓
np.unique(..., return_inverse=True)
       ↓
integer group IDs
       ↓
bincount / add.at
       ↓
group metrics
```

Example:

```python
import numpy as np

customer = np.array(
    ["A", "B", "A", "C", "B", "A"],
)
amount = np.array(
    [100, 200, 50, 300, 25, 75],
    dtype=np.float64,
)

groups, inverse = np.unique(
    customer,
    return_inverse=True,
)

totals = np.bincount(
    inverse,
    weights=amount,
)

print(groups)
print(totals)
```

Output:

```text
['A' 'B' 'C']
[225. 225. 300.]
```

This is a compact in-memory equivalent of an important group-by pattern.

---

# 51. `np.add.at`

Another way to build group sums is indexed accumulation with `np.add.at`.

```python
import numpy as np

group_idx = np.array([0, 1, 0, 2, 1, 0])
amount = np.array(
    [100, 200, 50, 300, 25, 75],
    dtype=np.int64,
)

totals = np.zeros(3, dtype=np.int64)

np.add.at(
    totals,
    group_idx,
    amount,
)

print(totals)
```

Output:

```text
[225 225 300]
```

---

# 52. Why `add.at` exists

Indexed updates can be subtle when indices repeat.

For example:

```text
group 0
group 1
group 0
```

A correct group accumulator must apply **every** contribution.

`np.add.at` performs unbuffered indexed updates, so repeated indices are accumulated one by one according to the operation.

Mental model:

```text
target[group_idx[i]] += amount[i]
for every i
```

but expressed through NumPy's indexed update mechanism.

### Production use

`add.at` is useful when:

- group IDs repeat,
- you need explicit accumulation semantics,
- an intermediate lookup array is being populated.

It may not always be the fastest method for every workload. Choose it for clear correctness first, then benchmark alternatives for a demonstrated bottleneck.

---

# 53. `np.add.reduceat`

`np.add.reduceat` performs reductions over segments described by start positions.

Start with sorted/grouped values:

```python
import numpy as np

values = np.array(
    [10, 20, 30, 40, 50, 60],
)

starts = np.array([0, 2, 5])

result = np.add.reduceat(
    values,
    starts,
)

print(result)
```

Output:

```text
[ 30 120  60]
```

The segments are conceptually:

```text
0:2 → [10, 20] → 30
2:5 → [30, 40, 50] → 120
5:end → [60] → 60
```

Therefore, for the code above, the correct result is:

```text
[ 30 120  60]
```

The key idea is:

> `reduceat` works naturally when group records are already arranged into contiguous segments.

It is useful when a prior ordering step has made group boundaries explicit.

### Important boundary rule

The start positions define each segment. The next start position determines the end of the current segment; the final segment runs to the end of the input.

### Starting from unsorted keys

`reduceat` needs contiguous segments, so unsorted keys must be ordered first:

```python
import numpy as np

keys = np.array([2, 0, 2, 1, 0, 2])
values = np.array([30, 10, 20, 40, 50, 60])

order = np.argsort(
    keys,
    kind="stable",
)

sorted_keys = keys[order]
sorted_values = values[order]

starts = np.flatnonzero(
    np.r_[True, np.diff(sorted_keys) != 0]
)

totals = np.add.reduceat(
    sorted_values,
    starts,
)

print(sorted_keys)
print(starts)
print(totals)
```

Output:

```text
[0 0 1 2 2 2]
[0 2 3]
[ 60  40 110]
```

The workflow is:

```text
unsorted keys
→ stable sort
→ contiguous equal-key groups
→ identify group starts
→ reduce each segment
```

`np.flatnonzero(np.r_[True, np.diff(sorted_keys) != 0])` marks the first position of every group.

### Boundary warning

If `starts[i] >= starts[i + 1]`, then `np.add.reduceat` does **not** represent an empty segment. It reduces the single element at `starts[i]`.

So `reduceat` is not an ordinary groupby replacement until contiguous segments have been established.

---

# 54. When to choose the three group patterns

| Pattern | Best fit |
|---|---|
| `bincount` | Compact non-negative integer group IDs |
| `unique(..., return_inverse=True)` + `bincount` | Arbitrary keys converted to integer group IDs |
| `add.at` | Explicit repeated indexed accumulation |
| `add.reduceat` | Already sorted/contiguous groups and segmented reductions |

In a real Data Engineering stack, pandas, Polars, SQL, Spark, or a database may be more natural for large relational group-bys. The NumPy patterns are valuable for understanding batch-level mechanics and for specialized numerical pipelines.

---

# 55. Histograms

A histogram summarizes a numeric distribution by counting observations in bins.

```python
import numpy as np

values = np.array(
    [1, 2, 2, 3, 4, 5, 6, 7, 8, 9],
)

counts, edges = np.histogram(
    values,
    bins=3,
)

print(counts)
print(edges)
```

Output:

```text
counts → [4 3 3]
edges  → [1.         3.66666667 6.33333333 9.        ]
```

`counts` tells you how many values fell into each interval.

`edges` defines the interval boundaries.

The bins are left-inclusive and right-exclusive, except the final bin, which also includes its right edge.

---

# 56. Why histograms matter in Data Engineering

Histograms can quickly reveal:

- suspicious distributions,
- extreme values,
- operational latency shape,
- transaction-size ranges,
- sensor measurement patterns,
- data drift.

They are often used during data profiling.

---

# 57. `np.digitize`

`np.digitize` maps numeric values to bin indices.

```python
import numpy as np

edges = np.array(
    [0, 100, 1000, 10_000],
)

amount = np.array(
    [50, 200, 5000, 20_000],
)

bins = np.digitize(
    amount,
    edges,
)

print(bins)
```

Output:

```text
[1 2 3 4]
```

With the default `right=False`:

```text
value < first edge
→ 0

edge[i-1] <= value < edge[i]
→ i

value >= last edge
→ len(edges)
```

The important concept is:

```text
numeric value
     ↓
interval boundaries
     ↓
bin/category ID
```

This is useful for:

- price bands,
- latency bands,
- risk bands,
- age groups,
- sensor ranges.

---

# 58. `histogram` versus `digitize`

The distinction is:

```text
np.histogram
→ summarize how many values fall in each bin

np.digitize
→ assign each individual value to a bin
```

For example:

```text
latency values
     ↓
digitize
     ↓
latency category per observation
```

while:

```text
latency values
     ↓
histogram
     ↓
counts per latency range
```

---

# 59. Numerical accuracy: why correct mathematics can still produce imperfect floating-point results

Computer arithmetic uses finite representations.

Therefore:

```text
mathematical operation
≠
exact real-number operation
```

in every floating-point case.

The order in which values are accumulated can affect the final floating-point result.

That matters for:

- large sums,
- variance,
- differences,
- repeated transformations,
- very large and very small values combined.

---

# 60. Pairwise summation

For floating-point sums, NumPy can use more numerically careful accumulation strategies in situations where they are applicable, including pairwise summation.

Conceptually, compare:

```text
linear accumulation:

(((a + b) + c) + d) + ...

versus

pairwise accumulation:

(a + b) + (c + d)
```

The second structure can reduce the accumulation of rounding error in many cases because values are combined in a more balanced way.

The important engineering point is not to assume a universal guarantee:

> **Numerical behavior depends on dtype, axis, implementation, and workload.**

For sensitive numerical pipelines, test the actual calculation and define acceptable tolerances.

### Demonstration: float32 accumulation

```python
import numpy as np

values = np.full(
    1_000_000,
    0.1,
    dtype=np.float32,
)

linear = np.float32(0.0)

for value in values:
    linear += value

np_total = values.sum()
expected = 100_000.0

print("linear float32:", linear)
print("np.sum:", np_total)
print("expected:", expected)
```

The exact displayed values are implementation-dependent, but the concept matters: naïve left-to-right `float32` accumulation accumulates substantial error, NumPy's reduction can use a more accurate strategy where applicable, and accumulation order matters. Do not treat these numbers as guarantees for every dtype, axis, or configuration.

---

# 61. Catastrophic cancellation

Catastrophic cancellation happens when subtracting nearly equal floating-point values causes significant precision to be lost.

Conceptual example:

```text
1.000001
-
1.000000
=
0.000001
```

If the original numbers have already lost precision in their low-order bits, the subtraction may leave a result with much less reliable information than expected.

This can matter in:

- variance calculations,
- change detection,
- differences between very large values,
- numerical transformations.

The practical lesson is:

> **Mathematically equivalent formulas are not always numerically equivalent in finite-precision arithmetic.**

### Demonstration: large-offset variance

```python
import numpy as np

x = np.array(
    [
        1_000_000_000_001.0,
        1_000_000_000_002.0,
        1_000_000_000_003.0,
        1_000_000_000_004.0,
        1_000_000_000_005.0,
    ],
    dtype=np.float64,
)

naive_variance = np.mean(x * x) - np.mean(x) ** 2
stable_variance = np.var(x)

print("naive:", naive_variance)
print("np.var:", stable_variance)
```

The mathematically correct population variance is `2.0`. The naïve `mean(x²) - mean(x)²` expression is numerically unstable at large offsets: catastrophic cancellation can produce a badly inaccurate or even negative result. `np.var` uses a numerically safer approach (deviations from the mean).

---

# 62. Dtype used during accumulation

Reduction functions can accept a `dtype` argument.

For example:

```python
import numpy as np

a = np.array(
    [1, 2, 3],
    dtype=np.int32,
)

total = a.sum(dtype=np.int64)

print(total)
print(total.dtype)
```

The source dtype and the accumulation dtype are different concepts:

```text
source storage dtype
        +
accumulation dtype
        ↓
result
```

This is especially important for integer reductions.

NumPy's documentation explicitly notes that using a larger dtype can help avoid overflow during reductions.

---

# 63. Integer overflow in reductions

Keep three things separate:

```text
source dtype
→ accumulation dtype
→ maximum mathematical total
→ overflow risk
```

Integer inputs narrower than the default integer are normally accumulated using the platform integer type. On a typical 64-bit platform this is `int64`. Therefore a plain `.sum()` on an `int16` or `int32` array does not automatically overflow merely because the source dtype is narrow:

```python
import numpy as np

values = np.array(
    [30_000, 30_000],
    dtype=np.int16,
)

total = values.sum()

print(total)
print(total.dtype)
```

Output on a typical 64-bit platform:

```text
60000
int64
```

The real risk is a total that exceeds the accumulation dtype itself.

---

# 64. Demonstrating reduction overflow

A genuine overflow needs a mathematical total outside the accumulation range, for example with `int64`:

```python
import numpy as np

values = np.array(
    [2**62, 2**62],
    dtype=np.int64,
)

true_total = 2**63
observed_total = values.sum()

print("true total:", true_total)
print("observed:", observed_total)
print("dtype:", observed_total.dtype)
```

The observed value is `-9223372036854775808`, not `2**63`:

```text
2**63 is outside the positive int64 range
→ fixed-width reduction cannot represent it
→ the result wraps
```

The exact overflowed value is less important than the engineering lesson: check the maximum mathematical total against the accumulation dtype.

`dtype=np.int64` is useful when a narrower source needs wider accumulation, but only when the mathematical result itself fits in `int64`. It does not make every possible integer aggregation safe.

---

# 65. A production overflow checklist

Before aggregating integer data, ask:

```text
1. What is the maximum individual value?
2. How many values can be aggregated?
3. What is the maximum possible total?
4. What dtype is used for accumulation?
5. Can the accumulation overflow?
6. What dtype does the downstream system expect?
```

For example:

```python
total = amount.sum(dtype=np.int64)
```

may be appropriate when source values are narrower but the total needs more range.

Do not blindly use `int64` for every operation. Use a dtype that safely covers the mathematical result and downstream contract.

---

# 66. Weighted means during chunking

Suppose two chunks have:

```text
chunk A:
count = 100
mean  = 10

chunk B:
count = 900
mean  = 20
```

A naïve average of the means gives:

```text
(10 + 20) / 2 = 15
```

That is wrong because the chunks have different sizes.

The correct global sum is:

```text
A sum = 100 × 10 = 1000
B sum = 900 × 20 = 18000

total sum = 19000
total count = 1000

global mean = 19000 / 1000
            = 19
```

Therefore:

> **Global mean must be weighted by the number of observations.**

An even better implementation pattern is to retain:

```text
total_sum
total_count
```

and compute:

```text
mean = total_sum / total_count
```

---

# 67. Chunked aggregation

Large data does not always need to fit into RAM simultaneously.

Instead of:

```text
load everything
    ↓
aggregate
```

you can use:

```text
chunk 1
   ↓
partial statistics

chunk 2
   ↓
partial statistics

chunk 3
   ↓
partial statistics

...
   ↓
merge
   ↓
global statistics
```

This is the foundation of streaming-style numerical aggregation.

---

# 68. Statistics that merge easily

For many aggregates, the merge operation is straightforward.

### Count

```text
global_count
= count_1 + count_2 + ...
```

### Sum

```text
global_sum
= sum_1 + sum_2 + ...
```

### Minimum

```text
global_min
= min(min_1, min_2, ...)
```

### Maximum

```text
global_max
= max(max_1, max_2, ...)
```

These are naturally composable.

---

# 69. Mean is mergeable through sum and count

Do not store only chunk means.

Instead retain:

```text
partial_sum
partial_count
```

Then:

```text
global_mean
=
sum(partial_sum)
/
sum(partial_count)
```

Example:

```python
import numpy as np

chunks = [
    np.array([10, 20, 30]),
    np.array([40, 50]),
]

total_sum = 0.0
total_count = 0

for chunk in chunks:
    total_sum += chunk.sum()
    total_count += chunk.size

global_mean = total_sum / total_count

print(global_mean)
```

Output:

```text
30.0
```

The loop controls chunking, while NumPy handles the numeric work inside each chunk.

---

# 70. A reusable partial-statistics structure

A production implementation can track:

```python
partial = {
    "count": chunk.size,
    "sum": chunk.sum(dtype=np.float64),
    "min": chunk.min(),
    "max": chunk.max(),
}
```

Then merge:

```python
global_count += partial["count"]
global_sum += partial["sum"]
global_min = min(global_min, partial["min"])
global_max = max(global_max, partial["max"])
```

The exact initialization and empty-input behavior need to be defined carefully in production code.

---

# 71. Variance is more difficult to merge

You should **not** simply average chunk variances.

Variance depends on both:

```text
within-chunk variation
+
differences between chunk means
```

Suppose chunk A and chunk B have the same internal spread but very different means.

The global dataset has more variability than either chunk alone because the groups themselves are far apart.

So:

```text
average(chunk variances)
```

is not generally equal to:

```text
global variance
```

---

# 72. Correct variance merging concept

Variance can be merged if you retain suitable sufficient statistics, such as:

```text
count
mean
sum of squared deviations / M2
```

A common numerically stable family of algorithms updates these values incrementally and can combine two summaries.

The key engineering idea is:

```text
per-chunk mean + per-chunk variation
+
difference between chunk means
+
chunk sizes
→
global variation
```

Do not treat variance as a simple associative "average this number" operation.

---

# 73. A stable chunk-merging formula

For two groups:

```text
n1, mean1, M2_1
n2, mean2, M2_2
```

define:

```text
delta = mean2 - mean1
n = n1 + n2
mean = mean1 + delta * n2 / n

M2 = M2_1 + M2_2 + delta^2 * n1 * n2 / n
```

Then the population variance is:

```text
variance = M2 / n
```

and a sample variance can use:

```text
variance = M2 / (n - 1)
```

when `n > 1`.

This is the kind of sufficient-statistics thinking that lets numerical pipelines scale while maintaining correct statistical semantics.

---

# 74. Why percentile values cannot simply be averaged

Suppose you compute:

```text
chunk 1 p95
chunk 2 p95
chunk 3 p95
```

It is tempting to calculate:

```text
global p95
≈ average(chunk p95 values)
```

That is not generally valid.

Why?

Because a percentile depends on the **global rank ordering** of all observations.

A chunk's p95 tells you only where 95% of that chunk's observations lie.

It does not tell you enough about how the complete distribution of all chunks is ordered.

Conceptually:

```text
chunk distributions
      ↓
global merged distribution
      ↓
global rank ordering
      ↓
global p95
```

You cannot replace this with:

```text
p95(chunk 1)
+
p95(chunk 2)
+
...
-------------------
number of chunks
```

and expect the exact global percentile.

---

# 75. Mergeable versus non-naïvely-mergeable statistics

A useful engineering classification is:

| Metric | Naïve chunk merge |
|---|---|
| Count | Add counts |
| Sum | Add sums |
| Min | Minimum of minima |
| Max | Maximum of maxima |
| Mean | Use total sum / total count |
| Variance | Requires sufficient statistics |
| Exact percentile | Cannot average chunk percentiles |

For exact global percentiles, you generally need more information about the distribution than one percentile value per chunk.

Scalable systems may use:

```text
full retained values
or
appropriate summaries / sketches
```

depending on whether exactness is required.

---

# 76. Chunked latency metrics

Suppose:

```text
10,000,000 latency values
```

and you want to process:

```text
1,000,000 values per chunk
```

For exact:

```text
count
sum
mean
min
max
```

you can process each chunk and merge the partial statistics.

Conceptual implementation:

```python
import numpy as np

rng = np.random.default_rng(42)

latency = rng.integers(
    50,
    2000,
    size=10_000_000,
    dtype=np.int32,
)

chunk_size = 1_000_000

total_sum = 0
total_count = 0
global_min = None
global_max = None

for start in range(0, latency.size, chunk_size):
    stop = min(
        start + chunk_size,
        latency.size,
    )

    chunk = latency[start:stop]

    total_sum += chunk.sum(
        dtype=np.int64,
    )
    total_count += chunk.size

    chunk_min = chunk.min()
    chunk_max = chunk.max()

    if global_min is None:
        global_min = chunk_min
        global_max = chunk_max
    else:
        global_min = min(
            global_min,
            chunk_min,
        )
        global_max = max(
            global_max,
            chunk_max,
        )

chunked_mean = total_sum / total_count

print(total_count)
print(chunked_mean)
print(global_min)
print(global_max)
```

The important design is:

```text
chunk → partial statistics → merge
```

not:

```text
chunk → store everything → calculate later
```

---

# 77. Verifying chunked results against full-array results

For correctness, calculate both versions on a manageable test dataset.

```python
full_sum = latency.sum(dtype=np.int64)
full_count = latency.size
full_mean = full_sum / full_count
full_min = latency.min()
full_max = latency.max()
```

Then compare:

```python
import numpy as np

np.testing.assert_equal(
    total_count,
    full_count,
)

np.testing.assert_equal(
    total_sum,
    full_sum,
)

np.testing.assert_equal(
    global_min,
    full_min,
)

np.testing.assert_equal(
    global_max,
    full_max,
)

np.testing.assert_allclose(
    chunked_mean,
    full_mean,
)
```

This gives you an explicit correctness proof for the chunked implementation.

---

# 78. Correlation with `np.corrcoef`

Correlation measures the degree to which two variables move together linearly.

```python
import numpy as np

temperature = np.array(
    [20, 22, 24, 26, 28],
    dtype=np.float64,
)

energy = np.array(
    [100, 110, 125, 135, 150],
    dtype=np.float64,
)

corr = np.corrcoef(
    temperature,
    energy,
)

print(corr)
```

The result is a correlation matrix.

Interpretation at a high level:

```text
+1 → strong positive linear relationship
 0 → little linear relationship
-1 → strong negative linear relationship
```

Use this for quick profiling, not as proof of causation.

### 2-D observation matrices: use `rowvar=False`

A matrix of shape `(n_samples, n_features)` has rows = observations and columns = variables/features. Use:

```python
np.corrcoef(X, rowvar=False)
```

rather than relying on the default `rowvar=True`:

```python
import numpy as np

X = np.array(
    [
        [20, 100],
        [22, 110],
        [24, 125],
        [26, 135],
        [28, 150],
    ],
    dtype=np.float64,
)

corr = np.corrcoef(
    X,
    rowvar=False,
)

print(corr)
print(corr.shape)
```

Expected shape:

```text
(2, 2)
```

Omitting `rowvar=False` treats each row as a variable and produces a `5 × 5` (`n_samples × n_samples`) matrix that describes the wrong entities.

---

# 79. Correlation does not prove causation

If two variables are strongly correlated:

```text
temperature
energy usage
```

you still cannot conclude:

> "Temperature causes energy usage."

Other variables may explain the relationship.

In a Data Engineering workflow, correlation is often useful for:

- exploratory profiling,
- feature screening,
- anomaly investigation,
- quick quality analysis.

It should not be confused with causal analysis.

---

# 80. Covariance with `np.cov`

Covariance measures how two variables vary together.

```python
import numpy as np

x = np.array([1, 2, 3, 4], dtype=np.float64)
y = np.array([2, 4, 6, 8], dtype=np.float64)

cov = np.cov(x, y)

print(cov)
```

A covariance matrix is returned.

Unlike correlation:

```text
correlation
→ normalized, scale-independent relationship

covariance
→ relationship retains scale information
```

Variance is the covariance of a variable with itself.

Again, these functions are particularly useful for quick numerical profiling in batch workflows.

---

# 81. Debugging aggregation problems

## Debugging NumPy Aggregation Problems

When a metric is wrong, begin with:

```python
print(a.shape)
print(a.dtype)
```

Then inspect the intended axis semantics.

For example:

```python
print("shape:", sales.shape)
print("daily:", sales.sum(axis=(1, 2)).shape)
print("store:", sales.sum(axis=(0, 2)).shape)
print("product:", sales.sum(axis=(0, 1)).shape)
```

The debugging workflow is:

```text
unexpected metric
      ↓
inspect input shape
      ↓
write down axis meanings
      ↓
identify collapsed axes
      ↓
predict output shape
      ↓
calculate a tiny example by hand
      ↓
compare NumPy result
```

---

# 82. Debugging bug 1: wrong axis

Suppose:

```text
sales.shape = (days, stores, products)
```

You need:

```text
sales per store
```

That means collapse:

```text
days + products
```

So:

```python
store_sales = sales.sum(axis=(0, 2))
```

A common mistake is:

```python
store_sales = sales.sum(axis=1)
```

But this collapses **stores**.

The result means something completely different.

### Prevention

Write the business meaning first:

```text
desired output:
one value per store

therefore:
preserve store axis

therefore:
reduce all other axes
```

---

# 83. Debugging bug 2: unexpected output shape

Given:

```python
a = np.arange(120).reshape(4, 5, 6)
```

Consider:

```python
result = a.sum(axis=1)
```

Do not guess.

Input:

```text
(4, 5, 6)
```

Collapse axis 1:

```text
(4, 6)
```

The result is not:

```text
(4, 5)
```

and not:

```text
(5, 6)
```

The remaining axes are:

```text
axis 0
axis 2
```

so the output shape is:

```text
(4, 6)
```

---

# 84. Debugging bug 3: missing `keepdims`

Suppose:

```python
X = np.arange(12, dtype=np.float64).reshape(3, 4)

row_sum = X.sum(axis=1)

print(X.shape)
print(row_sum.shape)
```

Output:

```text
(3, 4)
(3,)
```

If the intent is a row-wise denominator that should be explicitly aligned with each row, use:

```python
row_sum = X.sum(
    axis=1,
    keepdims=True,
)

print(row_sum.shape)
```

Output:

```text
(3, 1)
```

### Prevention

Use `keepdims=True` when preserving the reduced dimension as a length-one dimension improves broadcasting clarity.

---

# 85. Debugging bug 4: integer overflow

Broken pattern:

```python
values.sum(dtype=np.int16)
```

when the true sum is much larger than the `int16` range.

### Symptoms

The output is a valid-looking integer, but it is mathematically wrong.

### Root cause

The accumulation dtype cannot represent the total.

### Fix

Use an appropriate wider accumulation dtype:

```python
values.sum(dtype=np.int64)
```

### Prevention

Estimate the maximum possible aggregate before choosing the accumulation dtype.

---

# 86. Debugging bug 5: wrong `ddof`

If your statistical task requires a sample standard deviation but you use the population definition:

```python
x.std(ddof=0)
```

you may get a correct calculation of the wrong statistical quantity.

### Fix

Define the semantics explicitly:

```python
sample_std = x.std(ddof=1)
```

when sample estimation is the intended calculation.

---

# 87. Debugging bug 6: averaging chunk means

Broken conceptual approach:

```text
global_mean = (chunk_mean_1 + chunk_mean_2) / 2
```

This fails when chunk sizes differ.

### Fix

Track:

```text
sum
count
```

and compute:

```text
global_mean = total_sum / total_count
```

---

# 88. Debugging bug 7: averaging chunk p95 values

Broken:

```text
global_p95 = average(chunk_p95_values)
```

### Root cause

A percentile depends on the global rank distribution.

### Fix

Use an exact global computation when the data fits, or use an appropriate scalable percentile algorithm/summarization strategy when it does not.

Do not call the average of chunk p95s the global p95.

---

# 89. Debugging bug 8: rolling-total off-by-one

A `cumsum`-based rolling calculation can be wrong by one position.

Always write out a small example:

```text
day
1
2
3
...
```

and identify:

```text
window start
window end
cumulative index
```

Then verify against a hand-computed result.

### Prevention

Test:

```text
window = 1
window = 2
window = N
```

where appropriate.

---

# 90. Testing strategy

Aggregation tests should prove both:

```text
shape correctness
+
value correctness
```

A good pattern is:

```text
tiny input
   ↓
hand-computed expected result
   ↓
NumPy implementation
   ↓
assert shape
   ↓
assert values
```

---

# 91. Exact and tolerance assertions

For integer aggregation:

```python
import numpy as np

actual = np.array([10, 20, 30])
expected = np.array([10, 20, 30])

np.testing.assert_array_equal(
    actual,
    expected,
)
```

For floating-point results:

```python
actual = np.array([1.0 / 3.0])
expected = np.array([0.3333333333333333])

np.testing.assert_allclose(
    actual,
    expected,
)
```

The distinction matters because floating-point arithmetic may produce tiny representational differences even when the numerical result is correct within the desired tolerance.

---

# 92. Required edge cases

Test at least:

```text
empty array
one-element array
one-row matrix
single-column matrix
all-zero array
negative values where valid
duplicate group IDs
unequal chunk sizes
small integer dtypes
overflow-prone values
percentile boundary cases
```

Also test:

```text
axis=None
axis=0
axis=1
tuple axes
keepdims=True
```

for relevant functions.

---

# 93. Testing axis semantics with tiny data

A useful test matrix is:

```python
import numpy as np

a = np.array(
    [
        [1, 2, 3],
        [4, 5, 6],
    ]
)

expected_axis_0 = np.array([5, 7, 9])
expected_axis_1 = np.array([6, 15])

np.testing.assert_array_equal(
    a.sum(axis=0),
    expected_axis_0,
)

np.testing.assert_array_equal(
    a.sum(axis=1),
    expected_axis_1,
)
```

These tiny tests are powerful because you can verify them manually.

---

# 94. Performance and memory reasoning

Aggregation often has an attractive computational property:

```text
N input values
→ one pass over values
→ small output
```

But production performance still depends on:

- input size,
- dtype,
- number of scans,
- memory locality,
- intermediate arrays,
- chunking,
- numerical method,
- hardware.

Do not state a universal speedup.

Instead:

```text
measure on representative data
```

---

# 95. Full in-memory versus chunked aggregation

### Full in-memory

```text
load all data
     ↓
one/few vectorized reductions
```

Advantages:

```text
simple
often high throughput
easy to reason about
```

Costs:

```text
requires enough memory
```

### Chunked

```text
load chunk
   ↓
partial aggregate
   ↓
merge
   ↓
next chunk
```

Advantages:

```text
lower peak memory
works with data larger than comfortable RAM
```

Costs:

```text
Python control loop
merge logic
possible extra I/O overhead
some statistics are harder to merge
```

Choose based on the workload rather than ideology.

---

# 96. Production metrics architecture

A practical numerical metrics step might look like:

```text
source batch
    ↓
validate shape/dtype
    ↓
select valid records
    ↓
aggregate per required dimension
    ↓
compute percentiles
    ↓
merge partial statistics if chunked
    ↓
validate output shapes
    ↓
write metrics
```

At every stage, define:

```text
input shape
output shape
dtype
business meaning
```

---

# 97. SQL connection

The following mapping can help connect NumPy thinking to SQL:

| SQL concept | NumPy concept |
|---|---|
| `SUM()` | `np.sum()` |
| `AVG()` | `np.mean()` |
| `MIN()` | `np.min()` |
| `MAX()` | `np.max()` |
| `COUNT()` | `size` / count logic |
| grouped `SUM()` | `bincount` / coded groups |
| percentile | `percentile` / `quantile` |

This is conceptual rather than a claim that NumPy replaces a database.

In SQL, the grouping key is often explicit:

```sql
GROUP BY store_id
```

In NumPy, you may represent the same idea through:

```text
group IDs
+
aggregation function
```

That distinction is important.

---

# 98. Common mistakes

## Mistake 1 — confusing which axis disappears

**Why it happens:** memorizing `axis=0` and `axis=1` instead of reasoning about dimensions.

**Prevention:**

```text
Which dimension do I want to collapse?
```

Ask that question first.

---

## Mistake 2 — summing a narrow dtype

**Why it happens:** individual values fit, so the total seems safe.

**Prevention:**

Estimate the maximum aggregate and choose an appropriate accumulation dtype.

---

## Mistake 3 — using `ddof=0` automatically

**Why it happens:** it is the default.

**Prevention:**

Define whether you are describing the observed population or estimating from a sample.

---

## Mistake 4 — averaging chunk means

**Why it happens:** chunk means look like summaries you can average.

**Prevention:**

Track total sum and total count.

---

## Mistake 5 — averaging percentiles

**Why it happens:** percentile values look like ordinary averages.

**Prevention:**

Remember that percentiles depend on global rank.

---

## Mistake 6 — confusing `min` and `argmin`

```text
min
→ value

argmin
→ position
```

---

## Mistake 7 — forgetting `keepdims`

The result loses the reduced axis unless you preserve it.

---

## Mistake 8 — aggregating the wrong business dimension

A mathematically correct reduction can still produce the wrong business metric.

---

## Mistake 9 — assuming `np.diff` preserves length

It usually reduces the length by one along the selected axis.

---

## Mistake 10 — forgetting tuple-axis semantics

For:

```python
sales.sum(axis=(0, 2))
```

both axes are collapsed.

---

## Mistake 11 — using exact equality for floating-point metrics

Use an appropriate tolerance-based assertion when exact binary equality is not the intended contract.

---

## Mistake 12 — assuming all statistics are equally mergeable

Count, sum, min, and max are simple. Mean, variance, and percentiles require more care.

---

# 99. Hands-on exercise: `metrics_engine.py`

This exercise is the proof that you understand the chapter.

## Scenario

Generate:

```text
365 days
50 stores
200 products
```

of sales data.

Represent the data as:

```text
sales.shape == (365, 50, 200)
```

Interpretation:

```text
axis 0 → day
axis 1 → store
axis 2 → product
```

The exercise should be designed as if this were a numerical batch-processing component inside a larger Data Engineering pipeline.

---

## Task 1 — total sales per store

Requirements:

```text
one value per store
```

Question:

```text
Which axes should be reduced?
```

Before coding, write:

```text
Input shape:
Business output:
Axes to collapse:
Expected output shape:
```

Then implement it.

---

## Task 2 — total sales per product

Requirements:

```text
one value per product
```

Again write the shape reasoning first.

Expected output shape:

```text
(200,)
```

---

## Task 3 — total sales per day

Requirements:

```text
one value per day
```

Expected output shape:

```text
(365,)
```

---

## Task 4 — overall sales

Requirements:

```text
one value for the entire array
```

Use an all-axis reduction.

Expected result shape:

```text
()
```

---

## Task 5 — each store's share of total store sales

For each store, calculate:

```python
store_totals = sales.sum(
    axis=(0, 2),
    keepdims=True,
)

store_share = sales / store_totals
```

with:

```text
sales.shape        = (365, 50, 200)
store_totals.shape = (1, 50, 1)
store_share.shape  = (365, 50, 200)
```

Axes `0` (day) and `2` (product) are collapsed, leaving the store axis `1`. `keepdims=True` keeps the aggregate broadcast-compatible.

Your implementation should make the shape relationship obvious.

---

## Task 6 — API latency p50/p95/p99

Generate:

```text
10,000,000
```

simulated latency values using:

```python
rng = np.random.default_rng(42)
```

Compute:

```text
p50
p95
p99
```

using explicit percentile semantics.

Record:

```text
metric
value
method
```

Do not average chunk p95 values and call that the global p95.

---

## Task 7 — revenue per customer

Generate:

```text
customer_idx
amount
```

where `customer_idx` contains compact non-negative integer group IDs.

Compute:

```python
np.bincount(
    customer_idx,
    weights=amount,
)
```

Verify a small hand-computed example separately.

---

## Task 8 — rolling 7-day totals

Create daily totals and calculate rolling seven-day totals using:

```text
cumsum
+
difference
```

Test:

```text
first complete window
middle window
last window
```

and verify the result manually on a tiny example.

---

## Task 9 — chunked latency metrics

Process the ten-million latency values in chunks of:

```text
1,000,000
```

For each chunk calculate:

```text
count
sum
min
max
```

Merge them correctly.

Then compute:

```text
global mean
```

from merged sum and count.

Compare the chunked results with the full-array results.

---

## Task 10 — shape and value tests

Create small deterministic examples and assert:

```text
shape
values
axis meaning
keepdims behavior
chunk merging
```

Use:

```python
np.testing.assert_array_equal
```

for exact integer outputs and:

```python
np.testing.assert_allclose
```

for floating-point results where appropriate.

---

# 100. Starter structure for `metrics_engine.py`

A production-oriented organization could use functions such as:

```python
def total_sales_per_store(sales):
    ...

def total_sales_per_product(sales):
    ...

def total_sales_per_day(sales):
    ...

def overall_sales(sales):
    ...

def store_shares(sales):
    ...

def latency_percentiles(latency):
    ...

def revenue_per_customer(customer_idx, amount):
    ...

def rolling_total(values, window):
    ...

def aggregate_in_chunks(values, chunk_size):
    ...
```

The function signatures are a starting point, not a mandatory architecture.

The important requirement is separation of:

```text
calculation
validation
testing
benchmarking
```

---

# 101. Exercise edge cases

Your implementation should define behavior for:

```text
empty sales arrays
zero totals
one-day input
window > number of observations
one customer
missing group IDs where applicable
equal values
overflow-prone integer inputs
```

For percentile calculations also consider:

```text
one element
two elements
repeated values
```

The exact business response to invalid input should be explicit rather than accidental.

---

# 102. Mini benchmark design

Use a realistic benchmark instead of timing only:

```python
np.array([1, 2, 3])
```

A performance test might look like:

```python
import time

start = time.perf_counter()
result = values.sum()
elapsed = time.perf_counter() - start

print(f"{elapsed:.6f} seconds")
```

For fair comparisons:

- keep input data identical,
- separate data generation from the timed section,
- repeat measurements when comparing alternatives,
- report the environment when results matter.

The goal is not to chase a magic number. The goal is to verify that an engineering change actually helps.

---

# 103. Prediction-first aggregation worksheet

For every important aggregation in your own work, write:

```text
Input shape:
Axis semantics:
Reduction axis:
Collapsed dimensions:
Output shape:
Output meaning:
Output dtype:
Potential overflow:
Potential numerical error:
Can it be chunked?
Can chunk summaries be merged exactly?
```

Example:

```text
Input:
(365, 50, 200)

Question:
daily total sales

Axes:
day=0
store=1
product=2

Collapse:
store + product
= axes (1, 2)

Output:
(365,)

Meaning:
one sales total per day
```

This is the kind of reasoning expected in production pipeline design.

---

# 104. Final mental model

Use this hierarchy:

```text
ARRAY
  ↓
SHAPE
  ↓
AXES HAVE BUSINESS MEANING
  ↓
REDUCTION COLLAPSES DIMENSIONS
  ↓
CHOOSE AXIS
  ↓
PREDICT OUTPUT SHAPE
  ↓
CHOOSE keepdims WHEN NEEDED
  ↓
CHOOSE THE CORRECT STATISTIC
  ↓
CHECK DTYPE / NUMERICAL SAFETY
  ↓
CHUNK WHEN DATA IS LARGE
  ↓
MERGE PARTIAL STATISTICS CORRECTLY
  ↓
VERIFY WITH TESTS
```

The key mental shift is:

> **An axis is not just a number. It represents a dimension of meaning.**

For example:

```text
(days, stores, products)
```

means:

```text
axis 0 → days
axis 1 → stores
axis 2 → products
```

Then every reduction becomes a business question:

```text
per day?
per store?
per product?
overall?
```

---

# 105. Production aggregation checklist

Before aggregating, ask:

```text
1. What does each axis represent?
2. Which axis should be reduced?
3. What shape should the result have?
4. Should keepdims=True be used?
5. What dtype is being accumulated?
6. Could integer overflow occur?
7. Is ddof correct?
8. Is a percentile required instead of a mean?
9. Can the computation fit safely in memory?
10. Can the computation be processed chunk-by-chunk?
11. Can the partial results be merged exactly?
12. Have I tested the result against a tiny known example?
```

This checklist should become automatic.

---

# 106. Final review questions

Do not look back at the chapter on your first attempt.

## Core questions

### 1. What is a reduction?

Explain it in your own words.

### 2. What dimension disappears in:

```python
a.sum(axis=0)
```

### 3. What is the result shape for:

```python
a.shape == (4, 5, 6)
a.sum(axis=1)
```

### 4. What is `keepdims=True` for?

### 5. What is the difference between:

```text
min
argmin
```

### 6. What is the difference between:

```text
mean
p95
```

for API latency?

### 7. Why might `ddof=1` be appropriate for a sample?

### 8. Why can an integer reduction overflow even when every individual value fits the dtype?

### 9. Why should chunk means not simply be averaged when chunk sizes differ?

### 10. Why can variance not be merged by simply averaging chunk variances?

### 11. Why can exact p95 not be calculated by averaging chunk p95 values?

### 12. How does `np.bincount` perform group-style aggregation?

### 13. When is `np.add.at` useful?

### 14. What problem does `np.add.reduceat` solve?

### 15. What is the difference between `np.histogram` and `np.digitize`?

### 16. What does `np.diff` do to the length of a 1-D input?

### 17. What is the difference between correlation and covariance?

### 18. Why does the output shape matter as much as the output value?

---

# 107. Advanced checkpoint

Explain this without running it first:

```python
sales.shape == (365, 50, 200)

store_total = sales.sum(axis=(0, 2))
```

Your answer must include:

```text
axis 0 meaning:
axis 1 meaning:
axis 2 meaning:
collapsed axes:
remaining axis:
output shape:
business meaning:
```

Then explain:

```python
store_total = sales.sum(
    axis=(0, 2),
    keepdims=True,
)
```

and state its output shape.

Finally explain why the second form may be useful for later broadcasting.

---

# 108. Connection to Topic 05

The module now moves from:

```text
01 ndarray / dtype / memory layout
          ↓
02 vectorization / broadcasting
          ↓
03 indexing / masks / fancy indexing
          ↓
04 aggregations / axis semantics
          ↓
05 NaN / missing values / sentinels
          ↓
06 views / copies / memory efficiency
```

You now know how to summarize numerical data.

The next question is:

> **What happens when the values being summarized contain missing or invalid observations?**

That is the purpose of Topic 05.

You will need to understand:

```text
NaN
NaT
sentinels
missingness
NaN-safe reductions
```

The axis knowledge from this chapter carries directly into that work.

---

# 109. A final production example

Imagine a banking or IoT pipeline receives ten million records.

A production numerical stage might need:

```text
1. Select valid records
2. Group/partition by business dimension
3. Sum amounts safely
4. Compute means
5. Compute p95/p99 latency
6. Check min/max bounds
7. Track invalid-rate metrics
8. Process chunks when necessary
9. Merge partial statistics correctly
10. Persist metrics and run metadata
```

A strong engineer does not begin with:

```python
np.sum(...)
```

They begin with:

```text
What is the business grain?
What does each axis represent?
What is the required statistic?
What can overflow?
What precision is required?
What can be merged?
What must remain exact?
What output shape should I expect?
How will I prove the result is correct?
```

That is the difference between knowing a NumPy function and engineering a reliable numerical data pipeline.

---

# 110. One-page summary

```text
REDUCTION
→ summarize many values into fewer values

AXIS
→ identifies the dimension being collapsed

axis=0
→ collapse first dimension

axis=1
→ collapse second dimension

axis=None
→ collapse everything

tuple axes
→ collapse multiple dimensions

keepdims=True
→ keep reduced axes as size-1 dimensions

sum / mean / min / max
→ common numerical summaries

argmin / argmax
→ return positions

std / var
→ measure spread
→ ddof changes statistical denominator

percentile / quantile / median
→ distribution position
→ p50 / p95 / p99

cumsum
→ running total

cumprod
→ running product

diff
→ period-over-period difference

bincount
→ compact integer group aggregation

unique(return_inverse=True)
→ convert arbitrary keys into group IDs

add.at
→ repeated indexed accumulation

add.reduceat
→ segmented reductions

histogram
→ distribution counts per bin

digitize
→ assign observations to bins

dtype
→ controls accumulation safety

chunking
→ process large data incrementally

count + sum
→ enough for correct global mean

variance
→ requires richer sufficient statistics

percentile
→ cannot be merged by averaging chunk percentiles
```

---

# 111. Final engineering rule

The most important rule in this chapter is:

> **Never perform an aggregation until you can explain what each axis means and what the result shape should be.**

Then extend that rule:

```text
Correct axis
+
correct dtype
+
correct statistical definition
+
correct chunk-merging logic
+
correct output shape
+
tests
=
trustworthy numerical metric
```

That is the foundation for reliable numerical processing in Data Engineering.
