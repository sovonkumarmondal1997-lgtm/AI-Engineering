# NaN, Missing Values, and Sentinels

> **Stage 2 — Python for Data Engineering**  
> **Module 2.2 — Numerical Computing with NumPy**  
> **Topic 05 — NaN, Missing Values, and Sentinels**  
> **Target:** NumPy 2.x

---

## Learning goals

By the end of this chapter, you should be able to:

- Explain what "missing" means as a data-semantic concept.
- Distinguish missing, zero, unknown, not applicable, invalid, not-yet-received, and corrupted data.
- Use `np.nan` correctly with floating-point arrays.
- Explain why `NaN != NaN`.
- Detect NaN with `np.isnan`.
- Explain how NaN affects ordinary NumPy aggregations.
- Use the `np.nan*` family when ignoring NaNs is actually the correct business rule.
- Explain why normal integer NumPy dtypes cannot directly represent NaN.
- Demonstrate why converting large integer identifiers to `float64` can lose exactness around `2**53`.
- Understand sentinel values such as `-1`, `0`, `999`, and `-9999`.
- Decide when a sentinel is acceptable and when it becomes dangerous.
- Detect and process `NaT`, `inf`, and `-inf`.
- Use `np.isnat`, `np.isfinite`, `np.isinf`, and `np.nan_to_num`.
- Design an explicit `values + validity mask` representation.
- Understand the conceptual connection between validity masks and Arrow-style validity bitmaps.
- Understand NumPy masked arrays and their trade-offs.
- Choose between dropping, constant filling, mean/median imputation, and forward fill.
- Implement forward fill with `np.maximum.accumulate`.
- Prevent forward filling across entity boundaries such as devices.
- Explain when imputation becomes a data-quality lie.
- Build missingness reports with counts and rates.
- Enforce configurable missingness thresholds.
- Understand NaN behavior in comparisons, sorting, and `np.unique`.
- Use `np.testing.assert_array_equal` and `np.testing.assert_allclose(..., equal_nan=True)`.
- Debug real missing-data bugs systematically.
- Build the production-style `missing_values_report.py` exercise.

The central engineering question is:

> **How should a Data Engineer represent, detect, clean, aggregate, and govern missing or invalid data without silently corrupting information?**

---

# 1. Introduction: missing data is a data-semantics problem

Real production data is rarely complete.

A pipeline can receive:

- a sensor record with no measurement,
- a transaction with an unavailable amount,
- a customer whose age was never collected,
- an event without a timestamp,
- a failed API result,
- an infinite numerical result,
- a legacy value such as `-9999`,
- a record that is not applicable to a particular field,
- a record that has not arrived yet.

At first glance, all of these may look like "empty data."

They are not necessarily the same thing.

Consider:

```text
0
-1
999
-9999
NaN
NaT
validity=False
```

Each can represent a very different business meaning.

For example:

```text
quantity = 0
```

may be a perfectly valid order.

But:

```text
temperature = -9999
```

may be a legacy sentinel meaning:

```text
"sensor reading unavailable"
```

Therefore the first production rule is:

> **Missing is a meaning, not merely a particular number.**

A technically correct pipeline preserves that meaning.

---

# 2. Why missing-value handling matters in Data Engineering

Missing and invalid data can affect:

```text
ingestion
→ transformation
→ aggregation
→ reporting
→ machine learning
→ monitoring
→ downstream decisions
```

Examples:

### Customer data

```text
customer_age = missing
```

Possible meanings:

```text
not collected
unknown
not applicable
redacted
```

These should not automatically become:

```text
0
```

### Financial data

```text
transaction_amount = missing
```

Replacing it with zero can falsely indicate:

```text
a real zero-value transaction
```

instead of:

```text
amount unavailable
```

### Sensor data

```text
temperature = missing
```

A descriptive monitoring metric may reasonably ignore missing observations.

But a missing reading may also indicate:

```text
sensor failure
connectivity problem
device outage
```

So the pipeline may need to both:

```text
compute a metric
+
report the missingness rate
```

### API monitoring

A missing latency is not:

```text
0 ms
```

and should not be converted into zero just to make an average calculation run.

The engineering problem is therefore:

```text
represent
→ detect
→ classify
→ normalize
→ validate
→ aggregate safely
→ report
→ decide
```

---

# 3. What does "missing" actually mean?

Before using a NumPy API, define the semantic category.

Useful distinctions include:

| State | Example | Possible meaning |
|---|---|---|
| Valid zero | `0` | Real measured/observed zero |
| Unknown | missing | Value exists conceptually but is not known |
| Not applicable | missing | Field does not apply to this record |
| Not yet received | missing | Upstream data has not arrived |
| Invalid | `inf`, impossible range | A value was produced but cannot be trusted |
| Corrupted | malformed/raw bad value | Storage or transmission problem |
| Deleted/redacted | missing | Value existed but is unavailable now |
| Sensor unavailable | sentinel/NaN | Measurement could not be obtained |

The same numeric marker can have different meanings in different systems.

For example:

```text
0
```

might mean:

```text
zero balance
```

in one column and:

```text
missing sensor reading
```

in another legacy feed.

Never infer semantics from the marker alone.

---

# 4. The missing-data decision principle

Before cleaning a missing value, ask:

```text
What did the source intend this value to mean?
```

Then ask:

```text
How should downstream consumers interpret it?
```

A good pipeline does not simply ask:

> "How can I remove NaN?"

It asks:

> "What information would be lost if I removed or replaced this value?"

This is the recurring theme of the chapter.

---

# 5. NaN fundamentals

NumPy uses:

```python
np.nan
```

as the standard floating-point representation for a missing/undefined numeric value in many workflows.

Start with:

```python
import numpy as np

a = np.array(
    [1.0, 2.0, np.nan, 4.0],
)

print(a)
print(a.dtype)
```

Output:

```text
[ 1.  2. nan  4.]
float64
```

The array is floating-point because ordinary NumPy integer dtypes do not directly represent NaN.

---

# 6. What is NaN?

`NaN` means:

```text
Not a Number
```

It is a special floating-point value.

It can arise from:

- invalid numerical operations,
- undefined results,
- missing numerical observations,
- explicit conversion of a missing value into floating representation.

For data engineering, it is useful to distinguish:

```text
NaN caused by missing source data
```

from:

```text
NaN caused by a numerical computation
```

The representation is the same, but the cause is not.

That distinction may matter for incident diagnosis and data-quality reporting.

---

# 7. The most important NaN rule: `NaN != NaN`

Run:

```python
import numpy as np

x = np.nan

print(x == np.nan)
print(x != np.nan)
```

Output:

```text
False
True
```

This is surprising at first.

Why?

IEEE floating-point NaN has special comparison behavior: it is unordered and does not compare equal to itself.

So this is wrong for missing-value detection:

```python
a == np.nan
```

and this is also wrong as a detection rule:

```python
a != np.nan
```

The correct approach is:

```python
np.isnan(a)
```

### NaN in ordered comparisons

Ordered comparisons with NaN are also `False`:

```python
import numpy as np

a = np.array(
    [3.0, 7.0, np.nan],
)

print(a > 5)
print(a <= 5)
print(~(a > 5))
print(np.nan > 5)
print(np.nan == 5)
print(np.nan != 5)
```

Output:

```text
[False  True False]
[ True False False]
[ True False  True]
False
False
True
```

The trap: `~(a > 5)` is **not** equivalent to `a <= 5` when NaN exists. `NaN > 5` is `False`, and negating that makes it `True`, while `NaN <= 5` is still `False`.

State the validity rule explicitly:

```python
le_5_and_valid = (a <= 5) & ~np.isnan(a)
```

This matters for filtering, range checks, quality rules, metric classification, and production validation: a NaN can silently pass a negated condition or silently fail a direct one.

---

# 8. Detecting NaN with `np.isnan`

Use:

```python
import numpy as np

a = np.array(
    [10.0, 20.0, np.nan, 40.0],
)

mask = np.isnan(a)

print(mask)
```

Output:

```text
[False False  True False]
```

The relationship is:

```text
values
  ↓
np.isnan(...)
  ↓
Boolean mask
  ↓
selection / counting / reporting
```

This connects directly to Topic 03.

---

# 9. NaN detection on multidimensional arrays

`np.isnan` works element-by-element.

```python
import numpy as np

a = np.array(
    [
        [10.0, np.nan, 30.0],
        [np.nan, 50.0, 60.0],
    ],
)

print(np.isnan(a))
```

Output:

```text
[[False  True False]
 [ True False False]]
```

You can then count missing values:

```python
missing_count = np.count_nonzero(np.isnan(a))

print(missing_count)
```

Output:

```text
2
```

---

# 10. Missing count and missing rate

A Boolean mask gives you a simple missing-data report.

```python
import numpy as np

a = np.array(
    [10.0, np.nan, 20.0, np.nan, 30.0],
)

missing = np.isnan(a)

missing_count = missing.sum()
missing_rate = missing.mean()
valid_count = np.count_nonzero(~missing)

print(missing_count)
print(missing_rate)
print(valid_count)
```

Output:

```text
2
0.4
3
```

Interpretation:

```text
total rows   = 5
missing      = 2
valid        = 3
missing rate = 40%
```

This is a foundational production metric.

---

# 11. NaN propagation

Ordinary numerical aggregations generally propagate NaN when NaN participates in the calculation.

Example:

```python
import numpy as np

a = np.array(
    [10.0, 20.0, np.nan, 40.0],
)

print(a.sum())
print(a.mean())
print(a.max())
```

Typical results are:

```text
nan
nan
nan
```

The important lesson is:

> A single missing value can make an ordinary aggregate unusable.

That is why NumPy provides a separate NaN-aware function family.

---

# 12. Ordinary reductions versus NaN-aware reductions

NumPy provides pairs such as:

```text
sum        ↔ nansum
mean       ↔ nanmean
median     ↔ nanmedian
percentile ↔ nanpercentile
max        ↔ nanmax
argmax     ↔ nanargmax
```

Comparison:

| Ordinary | NaN-aware | Main idea |
|---|---|---|
| `np.sum` | `np.nansum` | Sum while ignoring NaN |
| `np.mean` | `np.nanmean` | Mean while ignoring NaN |
| `np.median` | `np.nanmedian` | Median while ignoring NaN |
| `np.percentile` | `np.nanpercentile` | Percentile while ignoring NaN |
| `np.max` | `np.nanmax` | Maximum while ignoring NaN |
| `np.argmax` | `np.nanargmax` | Position of max while ignoring NaN |

But there is an important engineering warning:

> **Do not automatically use `np.nan*` just because NaN exists. First decide what missingness means.**

---

# 13. `np.nansum`

```python
import numpy as np

a = np.array(
    [10.0, 20.0, np.nan, 40.0],
)

print(np.nansum(a))
```

Output:

```text
70.0
```

The NaN observation is excluded from the numerical sum.

This may be appropriate when:

```text
missing reading
→ should not contribute to the sum
```

For example, if an IoT device sends no reading for one minute, a daily descriptive sum of valid measurements may ignore the absent reading.

But the missing count should still be reported.

Otherwise, the system could say:

```text
sum = 70
```

without revealing:

```text
one observation was missing
```

---

# 14. `np.nanmean`

```python
import numpy as np

a = np.array(
    [10.0, 20.0, np.nan, 40.0],
)

print(np.nanmean(a))
```

Output:

```text
23.333333333333332
```

The mean is calculated from valid values:

```text
(10 + 20 + 40) / 3
```

This is different from treating the missing observation as zero.

If you used:

```text
(10 + 20 + 0 + 40) / 4
```

you would get a different business meaning.

---

# 15. `np.nanmedian`

```python
import numpy as np

a = np.array(
    [10.0, 20.0, np.nan, 40.0, 100.0],
)

print(np.nanmedian(a))
```

Output:

```text
30.0
```

Only valid values contribute to the median calculation.

Median is often more robust to extreme values than the mean, but it still needs an explicit missingness policy.

---

# 16. `np.nanpercentile`

For latency:

```python
import numpy as np

latency = np.array(
    [100.0, 120.0, np.nan, 150.0, 500.0],
)

p95 = np.nanpercentile(
    latency,
    95,
)

print(p95)
```

The percentile is calculated over valid observations.

This can be appropriate for descriptive latency monitoring, but you should report:

```text
p95
+
number of missing observations
+
missing rate
```

A p95 alone can hide an upstream data-collection problem.

---

# 17. `np.nanmax`

```python
import numpy as np

temperature = np.array(
    [20.0, 25.0, np.nan, 35.0],
)

print(np.nanmax(temperature))
```

Output:

```text
35.0
```

Useful for:

- maximum temperature,
- maximum valid latency,
- maximum valid amount.

Again, NaN-aware aggregation answers:

> "What is the metric among valid observations?"

It does not answer:

> "Was the source complete?"

Those are separate questions.

---

# 18. `np.nanargmax`

`np.nanargmax` returns the position of the maximum while ignoring NaN values.

```python
import numpy as np

temperature = np.array(
    [20.0, np.nan, 35.0, 30.0],
)

position = np.nanargmax(temperature)

print(position)
print(temperature[position])
```

Output:

```text
2
35.0
```

Compare the mental model:

```text
nanmax
→ maximum value

nanargmax
→ position of maximum valid value
```

### Important edge case

If there are no valid values to choose from, a `nanargmax`-style operation cannot produce a meaningful position. Production code should define how all-missing groups are handled.

---

# 19. All-NaN and empty inputs

Missing-aware functions still need edge-case policy.

Suppose:

```python
a = np.array([np.nan, np.nan])
```

What should the metric mean?

There are no valid observations.

This is not the same thing as:

```text
metric = 0
```

It may be:

```text
undefined
not available
data-quality failure
```

Similarly, an empty input has no observations at all.

The exact warnings and return values of individual NumPy functions can differ, so production code should test the relevant edge case rather than relying on memory.

A concrete trap:

```python
import numpy as np

a = np.array(
    [np.nan, np.nan],
)

print(np.nansum(a))
```

Output:

```text
0.0
```

With all observations missing, `np.nansum` returns `0.0`. That does **not** prove there was a real zero-valued aggregate. A production pipeline should separately retain:

```text
valid_count
missing_count
missing_rate
```

so that "sum = 0 from 0 valid observations" can be distinguished from "sum = 0 from real data".

Engineering rule:

> **Define the meaning of "no valid observations" explicitly.**

---

# 20. Integer arrays cannot directly represent NaN

Consider:

```python
import numpy as np

a = np.array(
    [1, 2, np.nan],
)
```

The presence of `np.nan` requires a representation that can contain NaN, so NumPy will not retain an ordinary integer dtype for those values.

Check:

```python
print(a)
print(a.dtype)
```

The resulting dtype is floating-point.

The reverse direction is also a trap:

```python
values = np.array([np.nan])
converted = values.astype(np.int64)

print(converted)
```

Converting NaN directly to an integer is invalid. On common 64-bit NumPy builds it may produce `-9223372036854775808` together with an invalid-value warning (warning and result details may be platform-dependent). That cast result must never be interpreted as a legitimate missing-value representation or used as an intentional sentinel.

The production-safe alternatives are `float + NaN`, or `integer values + validity mask`.

This creates a serious risk for identifiers.

---

# 21. Why float conversion can be dangerous for integer IDs

Suppose you have:

```text
customer_id
order_id
transaction_id
account_id
event_id
```

These are identifiers.

Their exact bit pattern matters.

Now imagine converting:

```text
int64
→ float64
```

just so that the column can hold NaN.

That can lose integer precision.

---

# 22. The `2**53` precision boundary

A `float64` has 53 bits of significand precision, including the implicit leading bit in the normal representation.

The important practical boundary is:

```python
2**53
```

which is:

```text
9007199254740992
```

Float64 cannot represent every integer exactly above this point.

It is therefore possible for two distinct large integers to map to the same representable `float64` value.

That means:

```text
different IDs
    ↓
float64 conversion
    ↓
same representable value
```

The exact identity of the identifier can be lost.

---

# 23. Demonstrating large-ID precision loss

Use adjacent integers around the boundary:

```python
import numpy as np

base = 2**53

a = np.array(
    [base, base + 1],
    dtype=np.int64,
)

b = a.astype(np.float64)

print(a)
print(b)
print(b[0] == b[1])
```

The integer array contains two distinct integer values.

The floating representation cannot preserve every integer at this scale, so the two values can become indistinguishable.

The engineering lesson is much more important than the exact printed representation:

> **Do not convert large identifiers to `float64` merely to make room for missing values.**

---

# 24. Safer pattern: integer values plus validity mask

Instead of:

```text
float64 + NaN
```

use:

```text
int64 values
+
Boolean validity mask
```

Example:

```python
import numpy as np

customer_id = np.array(
    [9007199254740992, 9007199254740993, 9007199254740994],
    dtype=np.int64,
)

is_valid = np.array(
    [True, False, True],
)
```

Now:

```text
customer_id
→ remains exact integer storage

is_valid
→ tells you which values are valid
```

This preserves identifier precision.

---

# 25. Why validity masks are powerful

A validity mask separates:

```text
what value is stored
```

from:

```text
whether that value is valid
```

This is often a better conceptual model for integer data.

For example:

```text
values:
[101, 102, 103, 104]

is_valid:
[ T,   F,   T,   F]
```

The logical column is:

```text
101
missing
103
missing
```

without changing the integer representation.

---

# 26. Sentinel values

A sentinel is an ordinary stored value that the system has assigned a special meaning.

Common examples:

```text
-1
0
999
-9999
```

For example:

```text
temperature = -9999
```

might mean:

```text
sensor unavailable
```

The critical point is:

> A sentinel is not intrinsically missing. The pipeline has to know that it means missing.

---

# 27. Why systems use sentinels

Sentinels commonly appear in:

- legacy databases,
- CSV exports,
- telemetry protocols,
- fixed-width files,
- systems without native null representations,
- old ETL interfaces.

The source system may be constrained to an ordinary numeric field:

```text
integer
```

while still needing a way to communicate:

```text
no value
```

A sentinel can be the historical solution.

---

# 28. When a sentinel is acceptable

A sentinel can be a reasonable interface when it is:

```text
documented
+
outside the legitimate domain
+
consistently produced
+
consistently interpreted
```

For example, if a temperature feed has a formally documented sentinel:

```text
-9999
```

and real temperatures can never be anywhere near that value, the sentinel is unambiguous.

A controlled ingestion pipeline can then:

```text
raw sentinel
→ detect
→ normalize
→ validate
```

But keep the source semantics visible until the conversion point is intentional.

---

# 29. When a sentinel is dangerous

Suppose:

```text
quantity = 0
```

Is zero valid?

Usually, yes.

Therefore this would be dangerous:

```text
0 = missing
```

unless the source contract explicitly says so.

Similarly:

```text
status = -1
```

may be a valid status code in one system.

The same sentinel cannot be assumed to mean missing across all domains.

---

# 30. Sentinel failure mode: aggregation corruption

Consider:

```python
import numpy as np

temperature = np.array(
    [20.0, 21.0, -9999.0, 22.0],
)
```

If you calculate:

```python
print(temperature.mean())
```

you get a meaningless result because the sentinel is treated as a real measurement.

The problem is not that NumPy is wrong.

NumPy correctly averaged the four numbers it was given.

The problem is that the pipeline failed to translate:

```text
-9999
```

from source semantics into the appropriate internal representation.

---

# 31. Normalize sentinels explicitly

A controlled cleaning step could convert:

```text
-9999
→ NaN
```

for a floating numeric column.

For example:

```python
import numpy as np

temperature = np.array(
    [20.0, 21.0, -9999.0, 22.0],
)

clean = temperature.copy()
clean[clean == -9999.0] = np.nan

print(clean)
```

Output:

```text
[20. 21. nan 22.]
```

Then:

```python
print(np.nanmean(clean))
```

Output:

```text
21.0
```

The transformation is explicit.

---

# 32. Why "sentinel → NaN" is not always the final answer

Converting a sentinel to NaN is convenient for floating-point calculations.

But you may instead prefer:

```text
value array
+
validity mask
```

because:

- the source dtype may need to remain integer,
- an identifier must remain exact,
- downstream systems may have explicit null support,
- you may need to distinguish different invalid reasons.

For example:

```text
value = 999
is_valid = False
reason = "source_timeout"
```

contains more semantic information than simply:

```text
value = NaN
```

Missingness handling should preserve information rather than erase it.

---

# 33. `NaT`: missing datetime/timedelta values

Datetime-like NumPy arrays use:

```text
NaT
```

for a missing time value.

`NaT` means:

```text
Not a Time
```

Example:

```python
import numpy as np

timestamps = np.array(
    [
        "2026-01-01T00:00",
        "NaT",
        "2026-01-01T02:00",
    ],
    dtype="datetime64[m]",
)

print(timestamps)
```

Output:

```text
['2026-01-01T00:00'                 'NaT'
 '2026-01-01T02:00']
```

Use:

```python
np.isnat(timestamps)
```

to detect missing datetime values.

---

# 34. Detecting `NaT`

```python
import numpy as np

timestamps = np.array(
    [
        "2026-01-01",
        "NaT",
        "2026-01-03",
    ],
    dtype="datetime64[D]",
)

mask = np.isnat(timestamps)

print(mask)
```

Output:

```text
[False  True False]
```

This gives you a Boolean validity signal just like `np.isnan` does for floating data.

---

# 35. Why missing timestamps are operationally important

A missing timestamp can break or distort:

- event ordering,
- time-window assignment,
- daily partitioning,
- incremental extraction,
- freshness calculations,
- late-arriving-data logic,
- time-series aggregation.

Suppose a pipeline asks:

```text
Which events arrived in the previous hour?
```

An event without a valid timestamp cannot reliably answer the question.

That record may need:

```text
quarantine
+
quality alert
```

rather than silent removal.

---

# 36. `datetime64` units and NaT

NumPy datetime arrays can use units such as:

```text
s
ms
us
ns
```

For example:

```python
import numpy as np

timestamps = np.array(
    ["2026-01-01T00:00:00.000", "NaT"],
    dtype="datetime64[ms]",
)

print(timestamps)
print(np.isnat(timestamps))
```

The important production rule is:

> **Missingness and timestamp resolution are separate concerns.**

A timestamp can be:

```text
valid + millisecond precision
```

or:

```text
missing + millisecond dtype
```

Do not confuse the dtype's time unit with whether the value exists.

---

# 37. Infinity: `inf` and `-inf`

NumPy also supports positive and negative infinity:

```python
np.inf
-np.inf
```

Example:

```python
import numpy as np

a = np.array(
    [10.0, np.inf, -np.inf, np.nan],
)

print(a)
```

Output:

```text
[ 10.  inf -inf  nan]
```

These values are different.

```text
finite
inf
-inf
nan
```

---

# 38. NaN is not infinity

Consider:

```python
import numpy as np

print(np.isnan(np.inf))
print(np.isinf(np.inf))
print(np.isfinite(np.inf))
```

Output:

```text
False
True
False
```

For NaN:

```python
print(np.isnan(np.nan))
print(np.isinf(np.nan))
print(np.isfinite(np.nan))
```

Output:

```text
True
False
False
```

So:

```text
NaN
→ use isnan

inf / -inf
→ use isinf

finite number
→ use isfinite
```

---

# 39. `np.isfinite`

`np.isfinite` gives you a broad validity check for finite numerical values.

```python
import numpy as np

a = np.array(
    [10.0, np.inf, np.nan, -np.inf, 20.0],
)

print(np.isfinite(a))
```

Output:

```text
[ True False False False  True]
```

This is useful when the desired rule is:

> Keep only finite numerical observations.

It can be simpler than separately combining `isnan` and `isinf`.

---

# 40. `np.isinf`

Use:

```python
import numpy as np

a = np.array(
    [10.0, np.inf, -np.inf, np.nan],
)

print(np.isinf(a))
```

Output:

```text
[False  True  True False]
```

This is especially useful for diagnosing calculations that produced an overflow or infinite result.

---

# 41. Where infinity can come from

Infinity may result from numerical operations such as:

```text
division by a value approaching zero
overflow in exponentials or multiplications
```

The important question is:

```text
Was infinity expected?
```

Usually in ordinary business metrics:

```text
inf
```

is a signal to investigate.

Do not silently convert it to a normal value without a documented rule.

---

# 42. `np.nan_to_num`

`np.nan_to_num` can replace non-finite values.

Start simply:

```python
import numpy as np

a = np.array(
    [1.0, np.nan, np.inf, -np.inf],
)

result = np.nan_to_num(a)

print(result)
```

This converts special values to finite numerical representations according to the function's rules/defaults.

You can also supply explicit replacements:

```python
result = np.nan_to_num(
    a,
    nan=0.0,
    posinf=999.0,
    neginf=-999.0,
)

print(result)
```

Now the replacements are explicit.

---

# 43. `nan_to_num` is not universal cleaning

This is critical.

Suppose:

```text
missing revenue
→ NaN
```

and you run:

```python
np.nan_to_num(revenue, nan=0.0)
```

You have changed:

```text
unknown
```

into:

```text
known zero
```

That may be semantically false.

Similarly:

```text
sensor failure
→ 0°C
```

is not the same as:

```text
sensor measured 0°C
```

Therefore:

> **Use `nan_to_num` only when the replacement values are justified by the data contract.**

---

# 44. Explicit validity masks

A validity mask is a separate Boolean array.

Example:

```python
import numpy as np

values = np.array(
    [10, 20, 30, 40],
    dtype=np.int64,
)

is_valid = np.array(
    [True, False, True, False],
)
```

The logical column is:

```text
values    validity
  10        True
  20        False
  30        True
  40        False
```

Meaning:

```text
10   valid
20   missing/invalid
30   valid
40   missing/invalid
```

---

# 45. Working with a validity mask

Select valid values:

```python
valid_values = values[is_valid]

print(valid_values)
```

Output:

```text
[10 30]
```

Count valid values:

```python
valid_count = np.count_nonzero(is_valid)
```

Count missing values:

```python
missing_count = np.count_nonzero(~is_valid)
```

Missing rate:

```python
missing_rate = (~is_valid).mean()
```

This preserves the original integer dtype.

---

# 46. Validity mask and aggregation

Suppose:

```python
values = np.array(
    [100, 200, 300, 400],
    dtype=np.int64,
)

is_valid = np.array(
    [True, False, True, True],
)
```

Then:

```python
valid = values[is_valid]

total = valid.sum(dtype=np.int64)
mean = valid.mean()
```

This makes the policy explicit:

```text
invalid/missing observations
→ excluded from the numerical metric
```

But you can also report:

```text
valid_count = 3
missing_count = 1
missing_rate = 25%
```

That is much better than hiding the missing observation.

---

# 47. Validity masks and different invalid reasons

A Boolean mask is useful when you only need:

```text
valid / invalid
```

But production systems sometimes need more detail:

```text
missing
invalid_range
parse_error
source_timeout
redacted
```

Then you may need:

```text
reason_code
+
validity mask
```

The lesson is:

> Start with the simplest representation that preserves the business meaning, but do not throw away information that downstream consumers need.

---

# 48. Arrow-style validity bitmap concept

Columnar systems often separate:

```text
values
+
validity metadata
```

Conceptually:

```text
values buffer
+
validity bitmap
```

A bitmap can use one bit per logical value to indicate whether the value is valid.

Visual:

```text
values:
[10][20][30][40][50][60]

validity bits:
 1   0   1   1   0   1
```

This is a powerful design because the validity state does not need to be encoded into the data value itself.

You do not need to implement Arrow in this chapter.

The important concept is:

> **Value storage and validity are separate concerns.**

This prepares you for the Arrow/Polars/DuckDB module later in the roadmap.

---

# 49. NumPy masked arrays

NumPy also provides masked arrays through:

```python
numpy.ma
```

Example:

```python
import numpy as np

a = np.array(
    [10.0, 20.0, 30.0, 40.0],
)

masked = np.ma.masked_array(
    a,
    mask=[False, True, False, True],
)

print(masked)
print(masked.mean())
```

The masked elements are excluded from masked-array calculations.

---

# 50. Masked arrays: mental model

A masked array can be thought of as:

```text
data
+
mask
```

which is closely related conceptually to:

```text
values
+
validity
```

For example:

```text
values:
10 20 30 40

mask:
 F  T  F  T
```

The masked result logically contains:

```text
10
missing
30
missing
```

---

# 51. Masked-array trade-offs

Masked arrays can be useful, but they introduce additional abstraction.

Consider:

```text
plain ndarray
+
explicit Boolean mask
```

versus:

```text
masked array
```

Potential trade-offs include:

- extra mask state,
- more complex interaction with ordinary arrays,
- interoperability considerations,
- learning overhead,
- behavior that differs from plain ndarray operations.

They are not universally bad.

They are simply one design option.

Many modern data pipelines prefer:

```text
explicit validity state
```

or a columnar null representation when interoperability and schema-level semantics matter.

---

# 52. Compare missing-value representations

A practical comparison:

| Representation | Typical values/types | Detection | Main strength | Main risk |
|---|---|---|---|---|
| NaN | floating numeric | `np.isnan` | Simple numeric missingness | Normal integers cannot directly hold it |
| Sentinel | domain-dependent | explicit comparison | Works with constrained/legacy interfaces | Can be mistaken for a real value |
| NaT | datetime/timedelta | `np.isnat` | Native temporal missing marker | Only for temporal dtypes |
| `inf` / `-inf` | floating numeric | `np.isinf` / `np.isfinite` | Explicit infinite numerical state | Often indicates invalid/overflow behavior |
| Values + validity mask | many dtypes | Boolean mask | Preserves original integer representation and explicit validity | Requires coordinated state |
| Masked array | NumPy masked arrays | mask semantics | Integrated masking abstraction | Added complexity/interoperability cost |

There is no universal winner.

Choose based on:

```text
source semantics
+
dtype requirements
+
downstream consumers
+
memory
+
interoperability
```

---

# 53. Imputation

**Imputation** means replacing a missing value with a chosen or estimated value.

Common strategies include:

```text
drop
constant fill
mean fill
median fill
forward fill
```

Each changes the data in a different way.

A good engineering rule is:

> **Imputation is a transformation of information, not merely cleanup.**

---

# 54. Dropping missing values

The simplest strategy is:

```text
missing
→ remove
```

For a numeric array:

```python
import numpy as np

a = np.array(
    [10.0, np.nan, 20.0, 30.0],
)

clean = a[~np.isnan(a)]

print(clean)
```

Output:

```text
[10. 20. 30.]
```

This is reasonable when:

- missing observations are rare,
- records with missing values are not needed,
- the downstream metric is defined over valid observations.

But dropping can introduce selection bias.

If missingness is systematic, removing those observations can distort the dataset.

Always measure:

```text
rows before
rows dropped
rows remaining
missingness rate
```

---

# 55. Constant imputation

A constant replacement may be valid when the domain semantics justify it.

Example:

```text
missing count
→ 0
```

can be correct if a missing count truly means:

```text
no events occurred
```

But it is not automatically correct.

For example:

```text
missing temperature
→ 0
```

does not mean:

```text
measured temperature = 0
```

unless the source contract says so.

---

# 56. Mean imputation

Mean imputation replaces missing values with the mean of valid observations.

```python
import numpy as np

a = np.array(
    [10.0, 20.0, np.nan, 40.0],
)

fill_value = np.nanmean(a)

filled = a.copy()
missing = np.isnan(filled)
filled[missing] = fill_value

print(filled)
```

Output:

```text
[10.         20.         23.33333333 40.        ]
```

This is easy to implement, but it changes the distribution.

For example, mean imputation can alter:

- variance,
- quantiles,
- correlations,
- downstream model features.

It may be suitable in some analytical or ML contexts, but the policy must be explicit.

---

# 57. Median imputation

Median imputation uses the median of valid values.

```python
import numpy as np

a = np.array(
    [10.0, 20.0, np.nan, 1000.0],
)

fill_value = np.nanmedian(a)

filled = a.copy()
filled[np.isnan(filled)] = fill_value

print(filled)
```

Median can be preferable to mean when the distribution contains strong outliers.

But it still changes the data.

It is not a way to "recover the true missing value."

It creates an estimated replacement.

---

# 58. Forward fill

Forward fill means:

```text
use the most recent valid value
```

Example:

```text
10
missing
missing
14
missing
```

becomes:

```text
10
10
10
14
14
```

This can make sense for slowly changing measurements.

But it can be dangerous when a value becomes stale.

A production rule may therefore need:

```text
forward-fill at most 15 minutes
```

rather than:

```text
carry the last value forever
```

---

# 59. Forward fill using `np.maximum.accumulate`

The roadmap requires understanding forward fill without a Python loop.

The core idea is to track the most recent valid index.

Start with:

```python
import numpy as np

values = np.array(
    [10.0, np.nan, np.nan, 14.0, np.nan],
)

valid = ~np.isnan(values)

positions = np.arange(values.size)
last_valid_position = np.where(
    valid,
    positions,
    -1,
)

last_valid_position = np.maximum.accumulate(
    last_valid_position,
)

print(valid)
print(last_valid_position)
```

Output:

```text
[ True False False  True False]
[ 0  0  0  3  3]
```

The cumulative maximum keeps the most recent valid position.

---

# 60. Completing the forward fill

Now:

```python
import numpy as np

values = np.array(
    [10.0, np.nan, np.nan, 14.0, np.nan],
)

valid = ~np.isnan(values)
positions = np.arange(values.size)

last_valid = np.where(
    valid,
    positions,
    -1,
)

last_valid = np.maximum.accumulate(last_valid)

filled = values.copy()

has_previous_valid = last_valid >= 0

filled[has_previous_valid] = values[
    last_valid[has_previous_valid]
]

print(filled)
```

Output:

```text
[10. 10. 10. 14. 14.]
```

The algorithm is:

```text
valid positions
      ↓
invalid positions → -1
      ↓
maximum.accumulate
      ↓
latest valid position for every row
      ↓
index into values
      ↓
forward-filled result
```

---

# 61. Why `np.maximum.accumulate` works

Suppose valid positions are:

```text
0
3
```

and invalid positions are:

```text
-1
```

The sequence becomes:

```text
[0, -1, -1, 3, -1]
```

A cumulative maximum produces:

```text
[0,  0,  0, 3,  3]
```

Therefore every missing position can look up the most recent valid position.

This is a useful example of using NumPy operations to replace a Python stateful loop.

---

# 62. Leading missing values

Consider:

```python
values = np.array(
    [np.nan, np.nan, 10.0, np.nan],
)
```

There is no previous valid value for the first two positions.

The forward-fill algorithm should therefore leave those positions missing.

A robust implementation must distinguish:

```text
has previous valid observation
```

from:

```text
no previous observation
```

Do not accidentally index position `-1` as though it were a valid previous record.

---

# 63. Forward fill per device

Now consider real sensor data:

```text
device_id
timestamp
temperature
```

Example:

```text
device 1: 20, missing, 21
device 2: 30, missing, 31
```

You must not allow:

```text
device 1's last reading
```

to fill:

```text
device 2's missing reading
```

The rule is:

> **Forward fill within each entity boundary.**

---

# 64. Device-aware forward fill: conceptual algorithm

A reliable design is:

```text
1. Order records by device + timestamp.
2. Identify valid temperature values.
3. Identify positions where device changes.
4. Carry the latest valid position only within the same device.
5. Leave leading missing values missing.
6. Optionally enforce a maximum staleness period.
```

The important part is not a clever one-liner.

The important part is preserving the boundary:

```text
device A
-------
fill only inside A

device B
-------
fill only inside B
```

### Concrete vectorized algorithm (no Python loop)

First sort by `(device_id, timestamp)` and mark where each device starts:

```python
order = np.lexsort((timestamp, device_id))

sorted_device = device_id[order]
sorted_temperature = temperature[order]
positions = np.arange(sorted_temperature.size)

is_first_of_device = np.r_[
    True,
    sorted_device[1:] != sorted_device[:-1],
]

seg_start = np.maximum.accumulate(
    np.where(is_first_of_device, positions, 0)
)
```

Then track the latest valid position, exactly as in the single-series version:

```python
valid = ~np.isnan(sorted_temperature)

last_valid = np.where(
    valid,
    positions,
    -1,
)

last_valid = np.maximum.accumulate(last_valid)
```

The critical boundary condition is:

```python
fillable = last_valid >= seg_start
```

Fill only positions whose latest valid observation is inside the same device, then restore the original row order:

```python
filled = sorted_temperature.copy()

filled[fillable] = sorted_temperature[
    last_valid[fillable]
]

filled_original_order = np.empty_like(filled)
filled_original_order[order] = filled
```

How it works:

- `seg_start` holds the sorted position where the current device began.
- `last_valid` holds the latest valid position seen so far in the whole sorted array, which may belong to the previous device.
- `last_valid >= seg_start` rejects a `last_valid` that lies before the current device began, so a previous device's value cannot cross the boundary.
- Leading NaNs of a device stay NaN, because no valid position at or after `seg_start` exists yet (`-1` and earlier-device positions both fail the test).
- Consecutive NaNs are handled because `last_valid` keeps pointing at the same valid position until a new one appears.
- No Python loop is used; every step is a whole-array operation.
- Stale-value limits (for example "at most 15 minutes") still need an explicit business/data-quality policy, for example by also comparing timestamps at `last_valid` and at each row.

---

# 65. Why ordering matters

Forward fill assumes the rows are ordered in time.

If the input is:

```text
device 1
timestamp 12:00 → 20
timestamp 10:00 → missing
```

then "previous value" is ambiguous unless the data is first sorted chronologically.

Therefore:

> **Forward fill is a temporal rule, so ordering is part of correctness.**

---

# 66. When forward fill becomes dangerous

Suppose:

```text
10:00 → 20°C
10:01 → missing
10:02 → missing
...
12:00 → missing
```

Carrying `20°C` forward for two hours may be misleading.

Production systems may need:

```text
maximum fill age
```

such as:

```text
do not carry forward beyond 10 minutes
```

This is another example of missing-data logic being a business/data-quality rule rather than only a NumPy trick.

---

# 67. When imputation becomes a data-quality lie

This is one of the most important concepts in the chapter.

Suppose:

```text
source: missing revenue
```

and you replace it with:

```text
0
```

The downstream system may now report:

```text
revenue = 0
```

That looks like a real financial fact.

But the source actually said:

```text
we do not know the revenue
```

You have changed uncertainty into certainty.

That is a data-quality lie.

---

# 68. Example: API latency

Suppose the source sends:

```text
120 ms
140 ms
missing
160 ms
```

Replacing missing with:

```text
0 ms
```

produces a false implication:

```text
the API responded instantly
```

The real meaning is:

```text
no latency observation exists
```

These are fundamentally different.

---

# 69. Example: financial amount

Suppose:

```text
transaction_amount = missing
```

and you replace it with:

```text
0
```

You have potentially converted:

```text
amount unavailable
```

into:

```text
known zero amount
```

That can corrupt:

- totals,
- reconciliation,
- fraud analysis,
- accounting,
- downstream reports.

Financial pipelines should be particularly cautious.

---

# 70. Example: sensor data

Forward filling can be appropriate for a slowly changing operational setting, but:

```text
previous temperature = 20
```

does not prove:

```text
current temperature = 20
```

The longer the gap, the less defensible the imputation may become.

A robust pipeline may preserve:

```text
imputed = True
fill_age = 7 minutes
```

so downstream consumers know the value was not directly observed.

---

# 71. Example: customer attributes

Suppose customer age is missing.

Mean imputation:

```text
age = average age
```

may be useful in a specific analytical model, but it does not mean:

```text
the customer is exactly that age.
```

The imputed value should therefore be treated as an analytical transformation, not a recovered fact.

---

# 72. Imputation decision framework

Before imputing, ask:

```text
1. What does the missing value mean?
2. What downstream question am I answering?
3. Is the replacement value domain-valid?
4. Will imputation change the distribution?
5. Can users distinguish observed from imputed values?
6. Should an imputation flag be preserved?
7. Should the record instead be dropped or quarantined?
```

A strong pipeline makes this policy explicit.

---

# 73. Missingness reporting

A production pipeline should measure missingness rather than silently handling it.

For each important column, track:

```text
total_rows
missing_count
missing_rate
valid_count
```

A useful conceptual output is:

| column | total_rows | missing_count | valid_count | missing_rate |
|---|---:|---:|---:|---:|
| temperature | 1,000,000 | 30,000 | 970,000 | 3.0% |
| device_id | 1,000,000 | 0 | 1,000,000 | 0.0% |
| timestamp | 1,000,000 | 2,000 | 998,000 | 0.2% |

The exact reporting columns depend on the pipeline contract.

---

# 74. Missingness with floating-point columns

For a float column:

```python
missing = np.isnan(values)

report = {
    "total_rows": values.size,
    "missing_count": np.count_nonzero(missing),
    "valid_count": np.count_nonzero(~missing),
    "missing_rate": missing.mean(),
}
```

This is small enough for a pipeline utility and explicit enough to test.

---

# 75. Missingness with validity masks

For integer data:

```python
is_valid = np.array(
    [True, False, True, True],
)
```

use:

```python
missing_count = np.count_nonzero(~is_valid)
missing_rate = np.mean(~is_valid)
valid_count = np.count_nonzero(is_valid)
```

The metric logic is the same even though the representation is different.

That is one of the strengths of making validity explicit.

---

# 76. Missingness thresholds

A pipeline may define:

```text
missing_rate > threshold
→ fail
```

Example:

```python
allowed_missing_rate = 0.05

if missing_rate > allowed_missing_rate:
    raise SystemExit(1)
```

The threshold is not a NumPy rule.

It is a:

```text
data-quality policy
```

informed by:

- data contracts,
- downstream tolerance,
- historical baselines,
- business criticality,
- freshness/SLO requirements.

---

# 77. Fail, warn, or quarantine?

A practical model is:

```text
acceptable
   ↓
continue

unexpected but recoverable
   ↓
warn + report

unacceptable
   ↓
quarantine / fail
```

For example:

```text
temperature missing rate = 3%
→ maybe continue

temperature missing rate = 8%
→ policy violation

device_id missing rate = 0.5%
→ potentially severe because IDs are required for grouping
```

There is no universal threshold.

The correct response depends on the field's role.

---

# 78. Why the denominator matters

Suppose:

```text
missing_count = 100
```

That number alone is not enough.

It means something very different when:

```text
total_rows = 1,000
```

versus:

```text
total_rows = 10,000,000
```

Therefore always report:

```text
missing_count
+
total_count
+
missing_rate
```

When records have already been filtered, be explicit about whether the denominator is:

```text
raw input rows
```

or:

```text
rows after filtering
```

Otherwise teams can report different missingness rates from the same source.

---

# 79. NaN sorting behavior

When sorting floating-point values containing NaN, NumPy's sorting behavior places NaNs toward the end for the relevant standard sorting operations.

Example:

```python
import numpy as np

a = np.array(
    [30.0, np.nan, 10.0, 20.0],
)

print(np.sort(a))
```

The valid values are ordered first, with NaN placed toward the end.

The production lesson is:

> **Sorting does not remove missing values. It only orders them according to the operation's semantics.**

This matters when:

- ranking,
- selecting extremes,
- deduplicating,
- applying threshold logic.

Do not assume:

```text
sorted
→ complete
```

---

# 80. `np.unique` and NaN equality

NumPy 1.21 changed `np.unique` so that NaN values are treated as equal for uniqueness and collapse to a single NaN by default. The explicit `equal_nan` parameter was added in NumPy 1.24, so `equal_nan=True` is available in the NumPy 2.x target of this chapter.

Conceptually:

```python
import numpy as np

a = np.array(
    [1.0, np.nan, np.nan, 1.0],
)

print(np.unique(a, equal_nan=True))
```

Multiple NaN values can be treated as one unique missing category under this behavior.

This is useful when answering:

```text
What distinct values occur, treating all NaNs as the same missing state?
```

Because missing values have unusual equality semantics, it is important to make this rule explicit.

---

# 81. Equality testing with NaN

Ordinary array equality is awkward when NaN is expected.

For exact array tests:

```python
import numpy as np

expected = np.array(
    [1.0, np.nan, 3.0],
)

actual = np.array(
    [1.0, np.nan, 3.0],
)

np.testing.assert_array_equal(
    actual,
    expected,
)
```

This testing API can account for NaN in the expected/actual arrays.

For floating-point calculations with tolerance:

```python
np.testing.assert_allclose(
    actual,
    expected,
    equal_nan=True,
)
```

The important distinction is:

```text
array correctness
+
floating-point tolerance
+
explicit NaN policy
```

---

# 82. `assert_array_equal` versus `assert_allclose`

Use:

```python
np.testing.assert_array_equal(...)
```

when exact element-wise equality is the intended contract.

Use:

```python
np.testing.assert_allclose(...)
```

when floating-point calculations may differ by a small numerical tolerance.

When NaN should count as matching:

```python
np.testing.assert_allclose(
    actual,
    expected,
    equal_nan=True,
)
```

Do not use exact equality just because the values "look equal."

---

# 83. Debugging missing-value problems

When a metric unexpectedly changes, inspect:

```python
print(values.dtype)
print(values.shape)
print(np.isnan(values))
```

for floating arrays.

For infinities:

```python
print(np.isinf(values))
print(np.isfinite(values))
```

For datetime arrays:

```python
print(np.isnat(timestamps))
```

For validity-mask designs:

```python
print(values)
print(is_valid)
```

The debugging workflow is:

```text
unexpected metric
      ↓
identify representation
      ↓
inspect dtype
      ↓
detect missing/invalid states
      ↓
measure counts/rates
      ↓
check conversion history
      ↓
check aggregation policy
      ↓
check imputation
      ↓
test tiny example
```

---

# 84. Debugging bug 1: detecting NaN with equality

Broken:

```python
import numpy as np

a = np.array([1.0, np.nan, 3.0])

mask = a == np.nan

print(mask)
```

The comparison does not identify the NaN element.

### Root cause

NaN does not compare equal to itself.

### Correct approach

```python
mask = np.isnan(a)
```

### Prevention

Never use `== np.nan` as a missing-value check.

---

# 85. Debugging bug 2: ordinary mean returns NaN

Broken:

```python
import numpy as np

temperature = np.array(
    [20.0, 21.0, np.nan, 22.0],
)

mean = temperature.mean()
```

### Symptom

The mean is NaN.

### Root cause

The ordinary mean propagates NaN.

### Correct approach

When business semantics say:

```text
ignore missing observations for this descriptive metric
```

use:

```python
mean = np.nanmean(temperature)
```

and separately report:

```text
missing_count
missing_rate
```

---

# 86. Debugging bug 3: large integer ID converted to float

Broken conceptual pipeline:

```text
int64 customer IDs
→ add NaN
→ float64
```

### Symptom

Distinct large IDs no longer remain distinct.

### Root cause

Float64 cannot represent every integer exactly above the `2**53` boundary.

### Correct approach

Use:

```text
int64 values
+
validity mask
```

or a downstream null representation that preserves integer identity.

---

# 87. Debugging bug 4: sentinel included in the metric

Broken:

```python
temperature = np.array(
    [20.0, 21.0, -9999.0, 22.0],
)

mean = temperature.mean()
```

### Root cause

The pipeline treated a source sentinel as a real measurement.

### Fix

Explicitly detect the sentinel:

```python
clean = temperature.copy()
clean[clean == -9999.0] = np.nan

mean = np.nanmean(clean)
```

Also report how many sentinel values were found.

---

# 88. Debugging bug 5: NaT treated as a normal timestamp

Broken conceptual logic:

```text
timestamp
→ sort
→ time window
```

without first defining what happens to NaT.

### Symptom

Records with missing timestamps are ordered or filtered in ways the business rule did not intend.

### Fix

Detect:

```python
missing_time = np.isnat(timestamp)
```

Then define policy:

```text
quarantine
or
exclude from time-based metrics
or
route to an exception workflow
```

---

# 89. Debugging bug 6: infinity mistaken for NaN

Broken:

```python
np.isnan(np.inf)
```

This is:

```text
False
```

because infinity is not NaN.

### Correct tools

```python
np.isinf(value)
```

or:

```python
~np.isfinite(value)
```

depending on whether you want to distinguish the exact invalid state.

---

# 90. Debugging bug 7: `nan_to_num` changes meaning

Broken:

```python
revenue = np.nan_to_num(
    revenue,
    nan=0.0,
)
```

### Symptom

Missing revenue suddenly appears as real zero revenue.

### Root cause

Technical convenience replaced a missing semantic state with a valid numeric state.

### Fix

Decide first:

```text
Should missing revenue be:
drop?
quarantine?
remain missing?
impute from a defensible model?
```

Only then perform the transformation.

---

# 91. Debugging bug 8: forward fill crosses devices

Imagine:

```text
device A → 20, missing
device B → 30, missing
```

A global forward fill could accidentally produce:

```text
device A → 20, 20
device B → 30, 30
```

only if the ordering happens to preserve boundaries.

But a bad ordering could propagate values across entities.

### Fix

Group the logic by device identity.

The valid state must reset at:

```text
device change
```

---

# 92. Debugging bug 9: threshold not enforced

Suppose:

```text
missing_rate = 0.08
allowed = 0.05
```

but the pipeline continues.

### Root cause

The quality rule was measured but not enforced.

### Correct behavior

```python
if missing_rate > allowed:
    raise SystemExit(1)
```

In a real pipeline, the failure may instead trigger a framework-specific task failure or quarantine.

The key requirement is:

```text
quality rule
→ explicit decision
```

---

# 93. Hands-on exercise: `missing_values_report.py`

This exercise is the proof that you understand the topic.

## Scenario

A fleet of devices sends sensor readings.

Use:

```text
temperature → float64
device_id   → int64
timestamp   → datetime64[ms]
```

Create a test dataset and inject:

```text
3% NaN
1% -9999 sentinel
0.5% inf
0.2% NaT
```

The exercise is designed to simulate a messy production input rather than a clean classroom array.

---

# 94. Exercise setup

Use deterministic random generation:

```python
import numpy as np

rng = np.random.default_rng(42)

n_rows = 1_000_000

device_id = rng.integers(
    1,
    2_001,
    size=n_rows,
    dtype=np.int64,
)

temperature = rng.normal(
    loc=22.0,
    scale=5.0,
    size=n_rows,
).astype(np.float64)
```

Create deterministic timestamps:

```python
base = np.datetime64(
    "2026-01-01T00:00:00.000",
    "ms",
)

timestamp = (
    base
    + np.arange(n_rows).astype("timedelta64[ms]")
)
```

The exact generation strategy may be adjusted to your machine, but the exercise requirements remain fixed.

---

# 95. Exercise: inject 3% NaN

Create a deterministic selection of positions:

```python
nan_count = int(
    0.03 * n_rows
)

nan_idx = rng.choice(
    n_rows,
    size=nan_count,
    replace=False,
)

temperature[nan_idx] = np.nan
```

Then verify:

```python
actual_nan_rate = np.isnan(temperature).mean()
```

Because the selected positions are not controlled to avoid overlap with later categories, the final category counts should be reported carefully.

A stronger production implementation should assign mutually exclusive problem categories if the target rates are intended to be exact.

---

# 96. Exercise: sentinel injection

Inject:

```text
1% -9999
```

You may first select positions that are not already NaN if you want exactly one category per record.

Conceptually:

```python
sentinel_idx = ...
temperature[sentinel_idx] = -9999.0
```

Then detect:

```python
sentinel_mask = temperature == -9999.0
```

Report:

```text
sentinel_count
sentinel_rate
```

---

# 97. Exercise: infinity injection

Inject:

```text
0.5% inf
```

Use:

```python
inf_mask = ...
temperature[inf_mask] = np.inf
```

Then detect:

```python
np.isinf(temperature)
```

Remember:

```text
NaN
and
inf
```

are distinct categories.

---

# 98. Exercise: NaT injection

Create a timestamp mask:

```python
nat_mask = ...
timestamp[nat_mask] = np.datetime64("NaT")
```

Then detect:

```python
np.isnat(timestamp)
```

Report the count and rate.

---

# 99. Exercise Task 1 — detect and count

For each problem type, report:

```text
NaN count
sentinel count
inf count
NaT count
```

Also report:

```text
total rows
valid temperature count
valid timestamp count
```

Do not merely print values.

Create a structured report such as:

```python
report = {
    "temperature_nan_count": ...,
    "temperature_sentinel_count": ...,
    "temperature_inf_count": ...,
    "timestamp_nat_count": ...,
}
```

---

# 100. Exercise Task 2 — clean

Create a clean copy of the temperature data.

Convert:

```text
-9999 → NaN
inf   → NaN
```

Conceptually:

```text
raw temperature
       ↓
detect sentinel
       ↓
detect inf
       ↓
clean copy
       ↓
NaN-safe metrics
```

Do not modify the source array accidentally.

Example pattern:

```python
clean_temperature = temperature.copy()

sentinel_mask = clean_temperature == -9999.0
clean_temperature[sentinel_mask] = np.nan

inf_mask = np.isinf(clean_temperature)
clean_temperature[inf_mask] = np.nan
```

Then test that the original `temperature` array is unchanged.

---

# 101. Exercise Task 3 — NaN-safe daily/device metrics

Calculate per-device metrics for valid temperature values:

```text
mean
min
max
p95
```

A pure NumPy solution should not silently combine values from different devices.

The exercise is deliberately challenging because grouping is not the focus of this topic.

Use the group-style patterns from earlier topics where necessary, but concentrate on:

```text
missing representation
+
validity
+
NaN-safe statistics
```

For every metric record, also preserve:

```text
valid observation count
missing count/rate
```

### Recipe: NaN-safe p95 per device and day

`np.bincount` and `np.add.reduceat` are not percentile functions. A percentile must be computed on the values that belong to each group, and the day key must be derived explicitly.

First exclude records whose timestamp is `NaT`, because a missing timestamp cannot be assigned to a real calendar day (report how many were excluded):

```python
known_timestamp = ~np.isnat(timestamp)

ts = timestamp[known_timestamp]
devices = device_id[known_timestamp]
values = clean_temperature[known_timestamp]
```

Derive the day key and sort into device/day groups:

```python
day = ts.astype("datetime64[D]")

order = np.lexsort((day, devices))

sorted_devices = devices[order]
sorted_days = day[order]
sorted_values = values[order]
```

Identify group boundaries:

```python
is_first_group = np.r_[
    True,
    (sorted_devices[1:] != sorted_devices[:-1])
    | (sorted_days[1:] != sorted_days[:-1]),
]

starts = np.flatnonzero(is_first_group)
ends = np.r_[starts[1:], sorted_values.size]
```

Compute p95 per group (the loop runs over groups, not over rows):

```python
p95 = np.array([
    (
        np.nanpercentile(
            sorted_values[start:end],
            95,
        )
        if np.any(
            ~np.isnan(sorted_values[start:end])
        )
        else np.nan
    )
    for start, end in zip(starts, ends)
])
```

Preserve the group keys:

```python
group_device = sorted_devices[starts]
group_day = sorted_days[starts]
```

`group_device[i]`, `group_day[i]` and `p95[i]` form one logical metric record.

For a group where every value is missing:

```text
all values missing
→ p95 remains NaN
→ do not invent zero
→ report missing/valid counts separately
```

---

# 102. Exercise Task 4 — integer precision demonstration

Create large IDs around:

```python
2**53
```

For example:

```python
ids = np.array(
    [
        2**53,
        2**53 + 1,
        2**53 + 2,
    ],
    dtype=np.int64,
)
```

Convert to float:

```python
float_ids = ids.astype(np.float64)
```

Compare:

```text
original int64 values
versus
float64 representation
```

Then show the safer design:

```python
is_valid = np.array(
    [True, False, True],
)
```

and keep:

```text
ids = int64
```

unchanged.

The goal is to demonstrate that missingness support should not destroy identifier identity.

---

# 103. Exercise Task 5 — forward fill per device

Sort your data conceptually by:

```text
device_id
+
timestamp
```

Then forward fill temperature within each device.

Requirements:

- do not cross device boundaries,
- preserve leading missing values,
- use `np.maximum.accumulate`,
- test consecutive missing values,
- define what happens to stale values.

The core algorithm should use valid-position tracking.

---

# 104. Exercise Task 6 — missingness threshold

Define:

```python
allowed_missing_rate = 0.05
```

Calculate missingness after your classification/normalization policy.

Then:

```python
if missing_rate > allowed_missing_rate:
    raise SystemExit(1)
```

The program must produce a non-zero process exit code when the threshold is exceeded.

The important engineering behavior is:

```text
quality breach
→ non-zero status
```

so an orchestrator can detect failure.

---

# 105. Exercise validation checklist

Before calling the exercise complete, verify:

```text
[ ] NaN detected with np.isnan
[ ] sentinel detected explicitly
[ ] inf detected with np.isinf
[ ] NaT detected with np.isnat
[ ] sentinel converted intentionally
[ ] inf converted intentionally
[ ] clean copy does not mutate source
[ ] NaN-aware metrics are used where justified
[ ] missingness counts are reported
[ ] missingness rates are reported
[ ] large integer IDs remain exact
[ ] validity-mask alternative is demonstrated
[ ] forward fill respects device boundaries
[ ] threshold failure produces non-zero exit
```

---

# 106. Required exercise edge cases

Your implementation must test:

```text
no missing values
all values missing
one missing value
all values NaN
sentinel-only data
infinity-only invalid values
missing timestamps
one device
multiple devices
device with no valid values
leading missing values
consecutive missing values
empty input
large IDs above 2**53
```

These are not optional extras.

They are where hidden assumptions are exposed.

---

# 107. Testing missing-value behavior

Use explicit tests.

## Exact comparison

```python
import numpy as np

expected = np.array(
    [10.0, np.nan, 30.0],
)

actual = np.array(
    [10.0, np.nan, 30.0],
)

np.testing.assert_array_equal(
    actual,
    expected,
)
```

## Floating-point comparison with NaN

```python
np.testing.assert_allclose(
    actual,
    expected,
    equal_nan=True,
)
```

The test contract should make the NaN expectation explicit.

---

# 108. Test sentinel conversion

Example:

```python
import numpy as np

raw = np.array(
    [10.0, -9999.0, 20.0],
)

clean = raw.copy()
clean[clean == -9999.0] = np.nan

expected = np.array(
    [10.0, np.nan, 20.0],
)

np.testing.assert_array_equal(
    clean,
    expected,
)
```

Also test:

```python
np.testing.assert_array_equal(
    raw,
    np.array([10.0, -9999.0, 20.0]),
)
```

to prove the source was not modified.

---

# 109. Test infinity handling

```python
import numpy as np

values = np.array(
    [10.0, np.inf, -np.inf],
)

assert np.count_nonzero(
    np.isinf(values)
) == 2
```

This proves your detection rule distinguishes infinity from finite data.

---

# 110. Test NaT handling

```python
import numpy as np

timestamps = np.array(
    ["2026-01-01", "NaT"],
    dtype="datetime64[D]",
)

expected = np.array(
    [False, True],
)

np.testing.assert_array_equal(
    np.isnat(timestamps),
    expected,
)
```

This keeps temporal missingness separate from floating NaN.

---

# 111. Test missingness threshold

```python
def enforce_missingness(
    missing_rate: float,
    allowed_rate: float,
) -> None:
    if missing_rate > allowed_rate:
        raise SystemExit(1)
```

Tests should verify both cases:

```text
rate <= threshold
→ continues

rate > threshold
→ non-zero failure
```

This is a data-quality gate, not just a numerical calculation.

---

# 112. Production data-engineering pattern

A robust missing-data pipeline often looks like:

```text
Source
  ↓
Raw ingestion
  ↓
Detect special values
  ↓
Classify missing / invalid / valid
  ↓
Normalize representation
  ↓
Validate
  ↓
Continue / Warn / Quarantine / Fail
  ↓
Aggregate safely
  ↓
Publish metrics
```

The order is important.

Do not aggregate first and ask what the missing values meant afterward.

---

# 113. APIs and missing fields

An API may return:

```json
{
  "customer_id": 123,
  "exchange_rate": null
}
```

The pipeline should not blindly convert:

```text
null
→ 0
```

Ask:

```text
Was the rate unavailable?
Was the field not applicable?
Did the provider fail?
```

Different causes can lead to different quality policies.

---

# 114. Legacy CSV sentinel feeds

A CSV may contain:

```text
device_id,temperature
101,20.4
102,-9999
103,21.1
```

The ingestion layer should know:

```text
-9999
→ sentinel
```

and not treat it as a real temperature.

A clean internal representation could be:

```text
temperature = float64 + NaN
```

if floating storage is acceptable.

Or:

```text
temperature integer/encoded value
+
validity mask
```

if preserving the original representation matters.

---

# 115. Sensor telemetry

Sensor systems often have multiple failure states:

```text
missing packet
invalid reading
sensor timeout
out-of-range reading
```

A single NaN may be insufficient if root-cause reporting matters.

A stronger design might preserve:

```text
value
validity
quality_code
```

The current chapter only requires the first two concepts, but the engineering principle is worth remembering.

---

# 116. CDC records and missingness

Change Data Capture pipelines can contain records where:

```text
updated_at = missing
```

or:

```text
field = NULL
```

Do not assume:

```text
missing timestamp
→ newest
```

or:

```text
missing field
→ zero
```

CDC semantics are part of the source contract and may require explicit handling before aggregation or deduplication.

---

# 117. Performance considerations

Missing-value handling itself consumes resources.

Potential costs include:

```text
Boolean masks
+
clean copies
+
validity arrays
+
repeated scans
+
masked-array metadata
```

For example:

```python
mask = np.isnan(values)
```

creates a Boolean result.

Cleaning into a new array creates another storage requirement.

That does not mean:

> "Never create masks."

Masks are often the cleanest and safest representation.

The real question is:

> **Is the memory cost justified by the correctness and semantics required?**

---

# 118. NaN versus validity mask: engineering trade-off

A floating array with NaN:

```text
simple
+
one array
+
easy numerical functions
```

but:

```text
requires floating representation
```

A value + validity mask:

```text
preserves integer dtype
+
explicit validity
+
separate semantics
```

but:

```text
requires coordinated arrays/state
```

Neither is universally better.

---

# 119. Why missingness should be observable

A pipeline that silently ignores missing values can produce dashboards that look healthy while data quality deteriorates.

For example:

```text
p95 latency = 500 ms
```

looks normal.

But if:

```text
40% of latency observations are missing
```

the metric should be treated differently.

Therefore a useful operational output is:

```text
metric_value
+
valid_count
+
missing_count
+
missing_rate
```

This turns data completeness into an observable property.

---

# 120. Missingness is not always random

A subtle production risk is **systematic missingness**.

Suppose sensor readings are missing whenever:

```text
temperature is extremely high
```

Then:

```text
np.nanmean(...)
```

may calculate the average only from ordinary conditions and systematically underestimate the real average.

Or suppose:

```text
high-value transactions
```

are more likely to be missing than low-value transactions.

Dropping missing records can bias financial metrics.

The important lesson is:

> **The missingness mechanism can matter as much as the missingness rate.**

This is why "just ignore NaN" is not a complete data-quality policy.

---

# 121. Missingness reporting by column

For a production report, calculate:

```python
def missing_report(values: np.ndarray) -> dict:
    missing = np.isnan(values)

    total = values.size
    missing_count = np.count_nonzero(missing)

    return {
        "total_rows": total,
        "missing_count": missing_count,
        "valid_count": total - missing_count,
        "missing_rate": (
            missing_count / total
            if total
            else 0.0
        ),
    }
```

This example intentionally defines empty input:

```text
missing_rate = 0
```

as a reporting convention.

Whether that is the correct production policy depends on the pipeline contract.

That is why edge-case semantics must be documented.

---

# 122. Production policy: preserve source semantics

A strong normalization pipeline often follows:

```text
raw value
+
source interpretation
        ↓
canonical representation
        ↓
quality metadata
```

For example:

```text
-9999
→ source sentinel
→ missing temperature
→ NaN
```

But keep enough metadata to explain the transformation when required.

This is especially important for:

- financial records,
- compliance data,
- healthcare-like telemetry,
- operational incident investigation,
- audit-sensitive systems.

---

# 123. Comparing representations: a decision table

| Question | NaN | Sentinel | NaT | Validity mask | Masked array |
|---|---|---|---|---|---|
| Supports ordinary float column? | Yes | Yes | No | Yes | Yes |
| Preserves integer ID exactly? | No if converted to float64 | Yes | No | Yes | Yes if underlying dtype supports it |
| Easy detection? | `isnan` | explicit rule | `isnat` | Boolean mask | mask semantics |
| Clear missing semantics? | Usually | Only if documented | Usually | Very explicit | Explicit |
| Legacy interoperability? | Sometimes | Often | Depends | Depends | Depends |
| Main risk | dtype conversion | sentinel collision | temporal misuse | extra state | complexity |

This is an engineering decision, not a preference contest.

---

# 124. SQL / DataFrame connection

The ideas connect to relational systems, but implementations differ.

| Data concept | NumPy idea |
|---|---|
| SQL `NULL` | missing-value representation |
| `IS NULL` | `isnan` or validity-mask check depending on dtype |
| null-aware average | `nanmean` or explicit masking |
| valid row count | mask/count logic |
| quality threshold | missing-rate policy |

Important:

```text
SQL NULL
pandas pd.NA
Arrow validity
NumPy NaN
```

are related concepts, but they are **not identical implementations or semantics**.

Do not carry assumptions from one system into another without checking the actual behavior.

---

# 125. Common mistakes

## Mistake 1 — testing NaN with equality

**Broken:**

```python
a == np.nan
```

**Correct:**

```python
np.isnan(a)
```

**Prevention:** Remember that NaN is not equal to itself.

---

## Mistake 2 — treating sentinels as real values

**Broken:**

```python
mean = np.mean(values)
```

when:

```text
-9999
```

means missing.

**Prevention:** Detect and normalize the sentinel before aggregation.

---

## Mistake 3 — silently imputing

**Broken:**

```text
missing revenue → 0
```

without a documented rule.

**Prevention:** Make imputation explicit and auditable.

---

## Mistake 4 — converting large IDs to float64

**Symptom:** distinct IDs become indistinguishable.

**Prevention:** preserve integer IDs and use validity metadata.

---

## Mistake 5 — treating zero as missing without evidence

```text
0
```

may be a perfectly valid measurement.

**Prevention:** determine the domain of valid values first.

---

## Mistake 6 — confusing NaN and infinity

Use:

```python
np.isnan(...)
```

for NaN and:

```python
np.isinf(...)
```

for infinity.

---

## Mistake 7 — confusing NaT and NaN

Use:

```python
np.isnat(...)
```

for datetime/timedelta missingness.

---

## Mistake 8 — blindly using `nan_to_num`

It may transform:

```text
unknown
→ known number
```

without business justification.

---

## Mistake 9 — measuring the wrong denominator

Always know whether your missing rate is relative to:

```text
raw input
```

or:

```text
post-filter data
```

---

## Mistake 10 — forward filling across entities

Never carry:

```text
device A
```

into:

```text
device B
```

because the data was not correctly segmented.

---

## Mistake 11 — forward filling indefinitely

A previous value can become stale.

Define a maximum acceptable fill age where appropriate.

---

## Mistake 12 — ignoring all-NaN groups

An all-missing device/day cannot produce a meaningful numerical mean merely because a function returned something.

Define the all-missing policy.

---

## Mistake 13 — assuming a missing timestamp is harmless

A missing timestamp may break:

```text
ordering
windows
freshness
partitioning
```

---

## Mistake 14 — hiding quality problems behind NaN-aware functions

`nanmean` can make a pipeline continue.

That does not mean the data-quality problem has been resolved.

Always report the missingness.

---

# 126. Prediction-first exercises

Before running each example, write:

```text
Input dtype:
Representation:
Detection method:
Aggregation behavior:
Potential risk:
Semantic meaning:
```

## Example A — NaN

```python
import numpy as np

a = np.array(
    [1.0, np.nan, 3.0],
)
```

Predict:

```text
dtype:
np.isnan(a):
a.mean():
np.nanmean(a):
```

---

## Example B — integer plus NaN

```python
a = np.array(
    [1, 2, np.nan],
)
```

Predict:

```text
Can an ordinary integer dtype hold all three values?
What dtype will NumPy choose?
What production risk might follow?
```

---

## Example C — sentinel

```python
a = np.array(
    [100, 200, -9999],
)
```

Predict:

```text
Is -9999 missing automatically?
What should the pipeline know before aggregating?
```

---

## Example D — NaT

```python
timestamps = np.array(
    [
        "2026-01-01",
        "NaT",
    ],
    dtype="datetime64[D]",
)
```

Predict:

```text
dtype:
np.isnat(timestamps):
```

---

## Example E — infinity

```python
a = np.array(
    [1.0, np.inf, np.nan, -np.inf],
)
```

Predict:

```text
np.isnan(a)
np.isinf(a)
np.isfinite(a)
```

The purpose of these exercises is to develop a reliable mental model before relying on the API.

---

# 127. Final decision framework

Use this decision tree:

```text
Is the value missing?
        |
        +-- No
        |    |
        |    +-- Is it invalid/infinite?
        |          |
        |          +-- No → keep
        |          |
        |          +-- Yes → classify invalid
        |
        +-- Yes
             |
             +-- Floating numeric
             |      ↓
             |    NaN may be appropriate
             |
             +-- Integer
             |      ↓
             |    validity mask / null-capable representation
             |
             +-- Datetime/timedelta
             |      ↓
             |    NaT
             |
             +-- Legacy sentinel
                    ↓
               detect → normalize
```

Then ask:

```text
1. What does missing mean in this source?
2. Is this actually missing or invalid?
3. Is zero a valid domain value?
4. Is the sentinel documented?
5. What dtype must be preserved?
6. Could float conversion damage identifiers?
7. Should the value be excluded, retained, quarantined, failed, or imputed?
8. If imputed, can consumers distinguish observed from imputed?
9. What missingness threshold is acceptable?
10. What happens when that threshold is exceeded?
```

---

# 128. Final mental model

Use this hierarchy:

```text
SOURCE DATA
    ↓
SEMANTIC MEANING
    ↓
MISSING / INVALID CLASSIFICATION
    ↓
CHOOSE REPRESENTATION
    ├── NaN
    ├── NaT
    ├── Sentinel
    ├── Validity mask
    └── Masked array
    ↓
DETECT
    ↓
NORMALIZE
    ↓
VALIDATE
    ↓
AGGREGATE SAFELY
    ↓
MEASURE MISSINGNESS
    ↓
DECIDE
    ├── CONTINUE
    ├── WARN
    ├── QUARANTINE
    └── FAIL
    ↓
OPTIONAL IMPUTATION
    ↓
PUBLISH
```

The key principle is:

> **Missing-value handling is not just a cleaning problem. It is a data semantics, correctness, and pipeline-quality problem.**

---

# 129. A production example from raw data to metric

Imagine an IoT pipeline receives:

```text
device_id
timestamp
temperature
```

A raw record may contain:

```text
device_id = 101
timestamp = 2026-01-01T10:02:00
temperature = -9999
```

The pipeline should think:

```text
-9999
    ↓
is this a documented sentinel?
    ↓
yes
    ↓
missing temperature
    ↓
normalize to NaN
    ↓
report missingness
    ↓
exclude from descriptive mean
```

But also:

```text
missing temperature count++
```

The final metric might be:

```text
mean_temperature = 22.7
valid_count = 9,700
missing_rate = 3.0%
```

This communicates both:

```text
what was observed
+
how complete the observation set was
```

That is much stronger than a single number.

---

# 130. Production quality-gate example

Suppose:

```python
allowed_missing_rate = 0.05
missing_rate = 0.08
```

The data-quality contract says:

```text
temperature missingness must be <= 5%
```

Then:

```text
8% > 5%
```

so the pipeline should not silently publish a metric as though the input were healthy.

Conceptually:

```text
metric calculation
        +
quality status
```

could become:

```text
status = "FAILED_QUALITY_GATE"
```

and the orchestrator receives:

```text
non-zero exit status / task failure
```

The exact mechanism depends on the pipeline framework, but the quality decision must be explicit.

---

# 131. Why missingness should travel with metrics

A good metric record may look conceptually like:

```text
device_id
metric_name
metric_value
valid_count
missing_count
missing_rate
quality_status
```

For example:

```text
device=101
metric=temperature_mean
value=22.7
valid=970
missing=30
missing_rate=3.0%
status=PASS
```

Now the consumer can distinguish:

```text
22.7 from 970 observations
```

from:

```text
22.7 from 10 observations
```

This is a major production-quality improvement.

---

# 132. Practical engineering rules to remember

```text
Rule 1
→ NaN is not detected with equality.

Rule 2
→ Integer IDs should not be converted to float casually.

Rule 3
→ Sentinels require a source contract.

Rule 4
→ NaT is for datetime/timedelta missingness.

Rule 5
→ inf is not the same as NaN.

Rule 6
→ nan-aware aggregation does not replace data-quality monitoring.

Rule 7
→ Validity masks preserve integer representations cleanly.

Rule 8
→ Imputation changes information.

Rule 9
→ Forward fill must respect entity and time boundaries.

Rule 10
→ Missingness thresholds are policy decisions.

Rule 11
→ Test pathological cases explicitly.

Rule 12
→ Publish metric values together with completeness information.
```

---

# 133. Final review questions

Do not look back at the chapter for your first attempt.

## Core questions

### 1. Why does this fail as a missing-value check?

```python
a == np.nan
```

### 2. How should NaN be detected?

### 3. Why do ordinary `sum()` and `mean()` behave differently from `nansum()` and `nanmean()` when NaN exists?

### 4. What does `nanmean` actually mean semantically?

### 5. Why can't ordinary NumPy integers directly represent NaN?

### 6. Why is converting a large integer ID to `float64` dangerous?

### 7. What is the significance of `2**53`?

### 8. When can a sentinel like `-9999` be acceptable?

### 9. Why can `0` be a dangerous sentinel?

### 10. What is the difference between:

```text
NaN
NaT
inf
-inf
```

### 11. Which detection function should you use for each?

### 12. What does `np.nan_to_num` do, and why should it not be treated as universal cleaning?

### 13. What is a validity mask?

### 14. Why is `values + validity mask` useful for integer identifiers?

### 15. What is the conceptual idea of an Arrow-style validity bitmap?

### 16. What is a NumPy masked array?

### 17. What are the trade-offs of masked arrays?

### 18. What are the main imputation strategies?

### 19. Why can mean imputation change the distribution?

### 20. How does forward fill work conceptually?

### 21. Why is `np.maximum.accumulate` useful for implementing forward fill?

### 22. Why must forward fill respect device boundaries?

### 23. Why can imputation become a data-quality lie?

### 24. What should a missingness report contain?

### 25. Why is a missing count alone insufficient?

### 26. How should a pipeline respond when missingness exceeds an allowed threshold?

### 27. How should all-NaN data be handled?

### 28. How does NaN behave in sorting?

### 29. What is the purpose of `equal_nan=True` in relevant `np.unique` behavior?

### 30. When should you use `assert_array_equal` versus `assert_allclose(..., equal_nan=True)`?

---

# 134. Advanced checkpoint

Explain this pipeline without running it first:

```text
raw sensor temperature
        ↓
3% NaN
1% sentinel
0.5% inf
        ↓
normalize sentinel and inf
        ↓
NaN-safe daily mean
        ↓
missingness report
        ↓
quality threshold
```

Your explanation must answer:

```text
1. Which representations are detected first?
2. Which values are converted?
3. Which values are excluded from the mean?
4. How is missingness still reported?
5. What happens if missingness exceeds the threshold?
6. Why is this more reliable than simply calling nanmean?
```

---

# 135. Connection to Topic 06

The module progression is:

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

You now understand how missing and invalid values are represented, detected, normalized, aggregated, and governed.

The next topic asks:

> **How do views and copies affect memory usage, mutation, and correctness?**

This is a natural next step because missing-value cleaning often involves:

```text
masks
+
temporary arrays
+
copies
+
in-place transformations
```

Topic 06 will turn those memory and aliasing concerns into a complete system for efficient NumPy code.

---

# 136. Final one-page summary

```text
MISSING
→ a semantic condition, not automatically a number

NaN
→ floating-point missing/undefined value
→ NaN != NaN
→ detect with isnan

NaN-aware aggregation
→ nansum
→ nanmean
→ nanmedian
→ nanpercentile
→ nanmax
→ nanargmax

INTEGER LIMIT
→ ordinary integer dtypes do not directly represent NaN
→ careless float conversion can damage IDs

2**53
→ float64 cannot represent every integer exactly above this boundary

SENTINELS
→ ordinary values with special source meaning
→ valid only when documented and outside the real domain

NaT
→ missing datetime/timedelta value
→ detect with isnat

INF / -INF
→ infinite numerical values
→ detect with isinf
→ finite check with isfinite

nan_to_num
→ explicit numerical replacement tool
→ not universal data cleaning

VALIDITY MASK
→ values + Boolean validity state
→ preserves integer representation

MASKED ARRAY
→ data + mask abstraction
→ useful, but with interoperability/complexity trade-offs

IMPUTATION
→ drop
→ constant
→ mean
→ median
→ forward fill

FORWARD FILL
→ latest valid value
→ maximum.accumulate can track latest valid position
→ must respect entity/time boundaries

DATA-QUALITY GOVERNANCE
→ count
→ rate
→ threshold
→ continue / warn / quarantine / fail

TESTING
→ assert_array_equal
→ assert_allclose(equal_nan=True)
→ pathological edge cases are mandatory
```

---

# 137. Final engineering principle

When a pipeline encounters a strange value, do not immediately ask:

> "How do I replace it?"

Ask:

```text
What does it mean?
Is it missing?
Is it invalid?
Is it a sentinel?
Can my dtype represent the intended state?
Will conversion destroy information?
Should this observation contribute to the metric?
Should the pipeline continue?
Should the record be quarantined?
Can downstream consumers tell that the value was imputed?
How will I measure the impact?
```

The strongest Data Engineering implementations make those answers explicit.

> **Preserve meaning first. Transform second. Measure quality continuously.**
