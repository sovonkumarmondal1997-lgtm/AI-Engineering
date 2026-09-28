# Topic 01 — `ndarray`, dtypes, and Memory Layout

> **Stage 2 — Python for Data Engineering**  
> **Module 2.2 — Numerical Computing with NumPy**  
> **Topic 01 of 06**

---

## 1. Introduction: Why a Data Engineer Needs NumPy

NumPy is the foundational numerical-array library in the Python data ecosystem. It gives Python a compact, typed, n-dimensional array structure and a large set of operations that run in optimized native code rather than executing a Python-level loop for every element.

For a Data Engineer, NumPy matters even when the visible day-to-day tools are pandas, Polars, Spark, SQL, Arrow, or machine-learning libraries.

A useful mental model is:

```text
Python code
   ↓
NumPy ndarray + dtype + memory layout
   ↓
Pandas / Polars / Arrow / Spark batches / ML pipelines
   ↓
Storage + analytics + ML/AI systems
```

The same engineering questions appear repeatedly:

- How much memory will this dataset consume?
- Is the numeric type large enough for every valid value?
- Can an intermediate arithmetic result overflow?
- Is the value represented exactly enough for the business requirement?
- Is a timestamp stored with the correct resolution?
- Did a transformation unexpectedly create another large allocation?
- Is the array contiguous or strided?
- Could a downstream library copy it because it prefers a different memory layout?
- Does a binary file use the same dtype and byte order that the reader assumes?

Those are not merely NumPy syntax questions. They are production data-engineering questions.

### What this chapter teaches

By the end of this topic, you should be able to reason about an ndarray as a combination of:

```text
ndarray
├── data buffer
├── dtype
├── shape
└── strides
```

You will also learn how to:

- inspect array size, shape, dtype, item size, and memory footprint;
- create arrays intentionally;
- choose safe numeric dtypes instead of blindly using `int64` or `float64`;
- detect and prevent integer overflow;
- understand floating-point precision and why exact money values need another representation;
- understand `datetime64` and `timedelta64`;
- calculate strides by hand;
- distinguish C-order and Fortran-order layout;
- inspect array flags and contiguity;
- connect memory layout to CPU cache locality;
- understand structured dtypes, NumPy strings, and endianness;
- read raw binary data with `fromfile` and `frombuffer`;
- perform production-style dtype and memory planning.

---

## 2. The `ndarray` Fundamentals

### 2.1 What is an `ndarray`?

`ndarray` means **N-dimensional array**.

It is NumPy's core array object: a homogeneous collection of fixed-size elements arranged according to a shape and interpreted using a dtype and strides.

Consider this array:

```python
import numpy as np

sales = np.array(
    [
        [100, 200, 300, 400],
        [150, 250, 350, 450],
        [175, 275, 375, 475],
    ],
    dtype=np.int32,
)
```

This is a 2-dimensional ndarray:

```text
rows    → 3
columns → 4
values  → 12
```

Its shape is `(3, 4)`.

### 2.2 Why is it called N-dimensional?

"N-dimensional" means the same array abstraction works for one, two, three, or many axes.

```python
one_d = np.array([10, 20, 30])

two_d = np.array([
    [10, 20, 30],
    [40, 50, 60],
])

three_d = np.array([
    [
        [1, 2],
        [3, 4],
    ],
    [
        [5, 6],
        [7, 8],
    ],
])
```

Their dimensions are:

```text
one_d   → 1 dimension
two_d  → 2 dimensions
three_d → 3 dimensions
```

You can inspect this with `.ndim`.

### 2.3 Homogeneous data

A fundamental difference from a normal Python list is that a regular NumPy numeric array is designed around a single dtype for its elements.

For example:

```python
import numpy as np

x = np.array([10, 20, 30], dtype=np.int32)
print(x.dtype)
```

Expected output:

```text
int32
```

Every element uses the same element representation.

That uniformity is powerful because NumPy can know exactly how many bytes each element occupies and can perform optimized operations over the buffer.

### 2.4 Fixed-size elements

If `dtype=np.int32`, each array element occupies 4 bytes.

If `dtype=np.int64`, each element occupies 8 bytes.

That means the array's raw element storage is predictable:

```text
number of elements × bytes per element
```

For a `(3, 4)` `int32` array:

```text
12 elements × 4 bytes = 48 bytes
```

### 2.5 Shape, axes, and dimensions

The **shape** tells you how many elements exist along each axis.

```python
x = np.zeros((3, 4, 2), dtype=np.int16)

print(x.ndim)
print(x.shape)
print(x.size)
```

Expected output:

```text
3
(3, 4, 2)
24
```

Interpretation:

```text
axis 0 → 3 positions
axis 1 → 4 positions
axis 2 → 2 positions

3 × 4 × 2 = 24 elements
```

### 2.6 The data buffer

At a conceptual level, think of an ndarray as a typed window onto a memory buffer.

For a compact numeric array, the values are stored in a raw memory region. Metadata tells NumPy how to interpret that region.

```text
Memory buffer
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ 10 │ 20 │ 30 │ 40 │ 50 │ 60 │ 70 │ 80 │ ...
└────┴────┴────┴────┴────┴────┴────┴────┘
        ↑
      dtype
      shape
      strides
      tell NumPy how to interpret the bytes
```

The ndarray is therefore not equivalent to "a list of numbers stored one after another". The metadata determines what positions mean and how NumPy moves through the buffer.

This becomes extremely important when we discuss strides, slicing, transposition, and memory order.

---

## 3. Python Lists vs NumPy Arrays

### 3.1 Why a Python list uses a different memory model

A Python list primarily stores references to Python objects.

Conceptually:

```text
Python list
┌──────────┬──────────┬──────────┐
│ pointer  │ pointer  │ pointer  │
└────┬─────┴────┬─────┴────┬─────┘
     ↓          ↓          ↓
 Python int  Python int  Python int
 object      object      object
```

A NumPy `int64` array is conceptually closer to:

```text
NumPy int64 array
┌────────┬────────┬────────┬────────┐
│ 8-byte │ 8-byte │ 8-byte │ 8-byte │ ...
│ value  │ value  │ value  │ value  │
└────────┴────────┴────────┴────────┘
```

The exact full memory footprint of Python objects contains interpreter/object overhead, allocator behavior, and other implementation details. The important engineering difference is that a homogeneous NumPy numeric array has a compact, fixed-size representation for its elements.

### 3.2 Measuring what each object owns

```python
import sys
import numpy as np

values = [10, 20, 30, 40]
array = np.array(values, dtype=np.int64)

print("list container:", sys.getsizeof(values))
print("one Python int:", sys.getsizeof(values[0]))
print("NumPy element storage:", array.nbytes)
```

The list's `sys.getsizeof()` result measures the list object/container itself. It does **not** include the complete recursive footprint of all referenced integer objects.

By contrast, `.nbytes` reports the total bytes consumed by the array elements themselves.

For serious memory measurement, especially at scale, use tools such as `tracemalloc` and controlled experiments rather than assuming a single `getsizeof()` value represents the entire dataset.

### 3.3 Why this matters at Data Engineering scale

A design that is harmless at 1,000 values can become expensive at 50 million values.

Always ask:

```text
How many values?
×
How many bytes per value?
=
raw element storage
```

For a 50-million-row numeric column:

```text
int64 → 50,000,000 × 8 bytes  ≈ 400 MB
int32 → 50,000,000 × 4 bytes  ≈ 200 MB
int16 → 50,000,000 × 2 bytes  ≈ 100 MB
```

That is before accounting for the other columns, temporary arrays, process overhead, object storage, or downstream copies.

This is why dtype planning is an engineering decision rather than a cosmetic optimization.

---

## 4. ndarray Attributes You Must Know

The roadmap requires the following attributes:

- `.ndim`
- `.shape`
- `.size`
- `.dtype`
- `.itemsize`
- `.nbytes`

Use this inspection pattern constantly:

```python
import numpy as np

x = np.arange(12, dtype=np.int32).reshape(3, 4)

print("ndim:", x.ndim)
print("shape:", x.shape)
print("size:", x.size)
print("dtype:", x.dtype)
print("itemsize:", x.itemsize)
print("nbytes:", x.nbytes)
```

Expected output:

```text
ndim: 2
shape: (3, 4)
size: 12
dtype: int32
itemsize: 4
nbytes: 48
```

### 4.1 `.ndim`

**What it is:** the number of axes/dimensions.

```python
x = np.zeros((3, 4, 5))
print(x.ndim)
```

Output:

```text
3
```

**Why it matters:** many operations depend on which axis you are talking about.

**Data Engineering use case:** a `(days, stores, products)` tensor needs a clear axis model before you perform aggregations.

### 4.2 `.shape`

**What it is:** a tuple containing the length of each axis.

```python
x = np.zeros((3, 4))
print(x.shape)
```

Output:

```text
(3, 4)
```

**Data Engineering use case:** validate that an incoming batch has the expected structure before processing.

### 4.3 `.size`

**What it is:** the total number of elements.

```python
x = np.zeros((3, 4))
print(x.size)
```

Output:

```text
12
```

For a multidimensional array:

```text
size = product of all shape dimensions
```

### 4.4 `.dtype`

**What it is:** the data type used to interpret each element.

```python
x = np.array([1, 2, 3], dtype=np.int32)
print(x.dtype)
```

Output:

```text
int32
```

The dtype controls more than labels. It affects memory usage, representable range, numerical precision, and arithmetic behavior.

### 4.5 `.itemsize`

**What it is:** number of bytes used by one element.

```python
x = np.array([1, 2, 3], dtype=np.int32)
print(x.itemsize)
```

Output:

```text
4
```

### 4.6 `.nbytes`

**What it is:** total number of bytes occupied by the array's elements.

```python
x = np.arange(12, dtype=np.int32).reshape(3, 4)
print(x.nbytes)
```

Output:

```text
48
```

Remember:

```text
nbytes = size × itemsize
```

This does not mean it is the total process memory of a Python program. It is the byte count for the array's element data.

### 4.7 Production inspection helper

A small inspection helper is useful while debugging a pipeline:

```python
import numpy as np


def inspect_array(name: str, array: np.ndarray) -> None:
    print(f"{name}")
    print(f"  shape:    {array.shape}")
    print(f"  ndim:     {array.ndim}")
    print(f"  size:     {array.size}")
    print(f"  dtype:    {array.dtype}")
    print(f"  itemsize: {array.itemsize}")
    print(f"  nbytes:   {array.nbytes}")
    print(f"  strides:  {array.strides}")
    print(f"  flags:    {array.flags}")


orders = np.arange(12, dtype=np.int32).reshape(3, 4)
inspect_array("orders", orders)
```

This style is valuable when debugging production data because a surprising dtype or shape is often the first clue to a problem.

---

## 5. Array Creation

NumPy gives you several ways to construct arrays. The correct choice depends on whether you are converting existing data, allocating a known shape, generating ranges, or creating reproducible test data.

### 5.1 `np.array`

**What it is:** converts array-like input into a NumPy array.

Basic example:

```python
import numpy as np

orders = np.array([101, 102, 103], dtype=np.int32)
print(orders)
print(orders.dtype)
```

Output:

```text
[101 102 103]
int32
```

Common uses:

- converting Python lists to ndarrays;
- explicitly choosing a dtype;
- constructing small test arrays.

Important idea: `np.array` generally creates a new array representation when needed and can be instructed about dtype and other construction details.

### 5.2 `np.asarray`

**What it is:** converts an array-like object to an ndarray while avoiding a copy when an existing compatible ndarray can be reused.

```python
import numpy as np

original = np.arange(5, dtype=np.int32)
converted = np.asarray(original)

print(converted is original)
```

Output:

```text
True
```

For NumPy 2.x migration work, `np.asarray(...)` is generally the appropriate expression when your intent is "give me an ndarray, and copy only if necessary." NumPy's 2.x migration guidance specifically recommends `np.asarray()` in places where older code used `np.array(..., copy=False)` for this intent.

### 5.3 `np.array` vs `np.asarray`

Think about intent rather than memorizing a slogan:

| Function | Typical intent | Key idea |
|---|---|---|
| `np.array(x)` | Construct an array representation | New representation may be allocated |
| `np.asarray(x)` | Obtain an ndarray view/reference where possible | Avoid unnecessary copying |

Example:

```python
import numpy as np

x = np.arange(4, dtype=np.int32)
a = np.asarray(x)
b = np.array(x)

print(a is x)
print(b is x)
```

Typical output:

```text
True
False
```

The exact copy behavior also depends on dtype, order, and the input object.

### 5.4 `np.zeros`

Allocates an array initialized to zero.

```python
import numpy as np

mask_scores = np.zeros(5, dtype=np.float32)
print(mask_scores)
```

Output:

```text
[0. 0. 0. 0. 0.]
```

Common Data Engineering uses:

- preallocating output arrays;
- counters;
- buffers;
- initialized feature columns.

### 5.5 `np.ones`

Allocates and initializes with ones.

```python
weights = np.ones((2, 3), dtype=np.float64)
print(weights)
```

Output:

```text
[[1. 1. 1.]
 [1. 1. 1.]]
```

### 5.6 `np.full`

Allocates and fills with a chosen value.

```python
status = np.full(5, fill_value=-1, dtype=np.int16)
print(status)
```

Output:

```text
[-1 -1 -1 -1 -1]
```

Useful for explicit initialization with a sentinel or business default.

Be careful: a sentinel must be a deliberate data-quality design choice, not an accidental substitute for missing-value handling.

### 5.7 `np.empty`

`np.empty` allocates the memory but does **not** initialize the values.

```python
x = np.empty(5, dtype=np.int32)
print(x)
```

The output is intentionally not deterministic. It may contain whatever bit patterns were already present in the allocated memory.

That does **not** mean NumPy is returning random numbers. It means you have not been promised meaningful initial values.

#### Correct usage pattern

```python
import numpy as np

result = np.empty(5, dtype=np.int64)
result[:] = [10, 20, 30, 40, 50]
print(result)
```

The array is safe because every element is written before being read.

#### Dangerous pattern

```python
import numpy as np

result = np.empty(5, dtype=np.int64)
print(result.mean())  # BUG: reads uninitialized values
```

**Rule:** use `np.empty()` only when you know the whole output will be overwritten before it is read.

### 5.8 `np.arange`

Creates evenly spaced values within a half-open interval.

```python
x = np.arange(0, 10, 2)
print(x)
```

Output:

```text
[0 2 4 6 8]
```

It is useful for:

- integer ranges;
- indexes;
- synthetic keys;
- deterministic test data.

For floating-point steps, be cautious about accumulated representation effects; `linspace` is often clearer when you know the desired number of samples.

### 5.9 `np.linspace`

Creates a specified number of evenly spaced values between a start and end value.

```python
x = np.linspace(0.0, 1.0, num=5)
print(x)
```

Output:

```text
[0.   0.25 0.5  0.75 1.  ]
```

Typical uses:

- simulations;
- benchmark inputs;
- numerical experiments;
- test data where the number of samples matters more than a step size.

### 5.10 `np.random.default_rng()`

Modern NumPy code should use the `Generator` API created by `np.random.default_rng()` rather than relying on the legacy global random state.

```python
import numpy as np

rng = np.random.default_rng(42)
values = rng.integers(0, 100, size=5)
print(values)
```

Expected output is deterministic for a given NumPy release and generator algorithm, but you should not hard-code random output in production tests unless the exact reproducibility contract is intentional.

The key point is that a seed makes the experiment reproducible.

```python
rng1 = np.random.default_rng(42)
rng2 = np.random.default_rng(42)

print(np.array_equal(rng1.integers(0, 10, size=8), rng2.integers(0, 10, size=8)))
```

Output:

```text
True
```

Use this for deterministic test data and benchmark input generation.

A realistic Data Engineering example:

```python
rng = np.random.default_rng(2026)

quantity = rng.integers(1, 501, size=1_000_000, dtype=np.int16)
unit_price_cents = rng.integers(100, 10_000_001, size=1_000_000, dtype=np.int32)
```

This allows you to build repeatable large-scale experiments without loading external data.

---

## 6. Core NumPy Dtypes

A dtype determines how each element is represented.

The main families required for this module are:

- boolean;
- signed integers;
- unsigned integers;
- floating point;
- complex numbers;
- strings and bytes;
- Python objects;
- date/time types.

### 6.1 Boolean

`bool` / `np.bool_` represents `True` or `False`.

```python
flags = np.array([True, False, True], dtype=np.bool_)
print(flags.dtype)
print(flags.itemsize)
```

On typical NumPy builds, boolean elements occupy one byte. Treat the dtype as compact storage, but remember that a boolean array is still stored as an array of elements rather than a bit-packed bitmap. Later technologies such as Arrow may use different validity/bit-level representations.

### 6.2 Signed integers

Required signed integer types:

```text
int8
int16
int32
int64
```

A signed integer can represent negative and positive values.

The number of representable values grows as the bit width increases.

For an N-bit two's-complement signed integer:

```text
minimum = -2^(N-1)
maximum =  2^(N-1) - 1
```

### 6.3 Unsigned integers

Required types:

```text
uint8
uint16
uint32
uint64
```

Unsigned integers represent non-negative values only.

For N bits:

```text
minimum = 0
maximum = 2^N - 1
```

### 6.4 Integer range table

| dtype | bytes | range | Typical use | Main risk |
|---|---:|---:|---|---|
| `int8` | 1 | -128 to 127 | small signed codes | overflow very easily |
| `uint8` | 1 | 0 to 255 | byte-like codes | cannot represent negatives |
| `int16` | 2 | -32,768 to 32,767 | compact counters/measurements | overflow if range underestimated |
| `uint16` | 2 | 0 to 65,535 | bounded non-negative values | negative values impossible |
| `int32` | 4 | -2,147,483,648 to 2,147,483,647 | common IDs/counters | arithmetic may overflow even when inputs fit |
| `uint32` | 4 | 0 to 4,294,967,295 | large non-negative codes | interoperability and signed math issues |
| `int64` | 8 | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 | general integer data | may waste memory if range is small |
| `uint64` | 8 | 0 to 18,446,744,073,709,551,615 | very large non-negative integers | mixed signed arithmetic can be surprising |

### 6.5 Floating-point types

Required types:

```text
float16
float32
float64
```

Floating-point numbers approximate real numbers using sign, exponent, and significand/fraction bits.

A wider type generally provides greater precision and a larger representable range, but it costs more memory.

| dtype | bytes | Typical role | Trade-off |
|---|---:|---|---|
| `float16` | 2 | specialized ML/numeric workloads | very limited precision/range |
| `float32` | 4 | ML features, large numeric batches | lower precision than `float64` |
| `float64` | 8 | general scientific/data analysis | higher memory cost |

#### Precision checkpoints

Inspect machine epsilon (the gap between 1.0 and the next representable value) with:

```python
np.finfo(np.float32).eps
np.finfo(np.float64).eps
```

```text
float32 eps → 1.1920929e-07
float64 eps → 2.2204460e-16
```

| dtype | eps | Every integer is exactly representable through |
|---|---:|---:|
| `float32` | ≈ 1.1920929e-07 | 2^24 = 16,777,216 |
| `float64` | ≈ 2.2204460e-16 | 2^53 = 9,007,199,254,740,992 |

Above 2^24 for `float32`, or 2^53 for `float64`, not every integer is exactly representable.

The exact finite-range limits are less useful than learning to ask whether your domain values, intermediate operations, and error tolerance fit the dtype.

### 6.6 Complex types

NumPy supports complex numbers with real and imaginary components.

```python
x = np.array([1 + 2j, 3 + 4j], dtype=np.complex128)
print(x)
print(x.real)
print(x.imag)
```

Complex types are useful in scientific and signal-processing workloads. They are not a normal choice for business dimensions or ordinary warehouse metrics.

### 6.7 Strings, bytes, and objects

Required concepts:

```text
str_
bytes_
object
```

Strings require special attention because unlike fixed-size numeric values, real-world text has variable length.

We will cover string representations in detail later in this chapter.

### 6.8 `datetime64` and `timedelta64`

These are NumPy's native date/time dtypes.

```python
created_at = np.array(
    ["2026-01-01T12:00:00.000", "2026-01-01T12:00:01.250"],
    dtype="datetime64[ms]",
)

print(created_at.dtype)
```

Output:

```text
datetime64[ms]
```

`timedelta64` represents a duration rather than an absolute timestamp.

---

## 7. Choosing a dtype: A Data Engineering Decision

The wrong dtype can cause:

- memory pressure;
- integer overflow;
- precision loss;
- incorrect timestamps;
- expensive conversions;
- downstream incompatibility.

The right question is not:

> "What dtype is the default?"

The right questions are:

```text
What values can this column actually contain?
        ↓
What range must be represented safely?
        ↓
What precision is required?
        ↓
What arithmetic will be performed?
        ↓
What systems consume the result?
```

### Example: order table

Suppose you have:

```text
order_id          0 … 3,000,000,000
quantity          0 … 500
unit_price_cents  0 … 10,000,000
is_gift           True / False
status_code       0 … 20
created_at        millisecond precision
```

A possible first-pass design is:

| Column | Candidate dtype | Why |
|---|---|---|
| `order_id` | `uint32` | 3 billion fits within the unsigned 32-bit range |
| `quantity` | `uint16` | 0–500 fits comfortably |
| `unit_price_cents` | `uint32` | up to 10,000,000 fits |
| `is_gift` | `bool` | two logical states |
| `status_code` | `uint8` | 0–20 fits |
| `created_at` | `datetime64[ms]` | millisecond precision required |

This is only a candidate design. The final choice must also account for arithmetic, null representation, file formats, downstream APIs, and schema interoperability.

### Interoperability matters

A smaller dtype is not automatically better.

A downstream system may require a particular type, may serialize values differently, or may not handle unsigned integers consistently.

Therefore:

```text
smallest safe dtype
≠
best dtype in every situation
```

Engineering means balancing range, precision, memory, semantics, and interoperability.

---

## 8. Integer Ranges and Silent Overflow

### 8.1 Signed vs unsigned

For signed 8-bit integers:

```text
-128 … 127
```

For unsigned 8-bit integers:

```text
0 … 255
```

You can confirm limits programmatically:

```python
import numpy as np

print(np.iinfo(np.int8).min)
print(np.iinfo(np.int8).max)
print(np.iinfo(np.uint8).min)
print(np.iinfo(np.uint8).max)
```

### 8.2 The classic overflow example

```python
import numpy as np

x = np.int8(127)
print(x)
print(x + 1)
```

On NumPy 2.x, this produces an overflowed `int8` result rather than the mathematically expected 128:

```text
127
-128
```

You may also see an overflow warning depending on the exact operation and environment.

The critical lesson is:

> A fixed-width integer does not magically grow to accommodate a value just because the mathematical result is larger.

### 8.3 Why this is dangerous in pipelines

Overflow can create a plausible-looking number.

Imagine:

```python
quantity = np.array([500], dtype=np.int16)
price = np.array([30_000], dtype=np.int16)
```

Both inputs fit in `int16`, but:

```text
500 × 30,000 = 15,000,000
```

does not fit in the `int16` range (-32,768 to 32,767).

A common mistake is to validate only the input columns and forget to validate the arithmetic result.

### 8.4 Deliberate upcasting

When the operation needs a larger range, make the conversion explicit.

```python
import numpy as np

quantity = np.array([500], dtype=np.int32)
price = np.array([100_000], dtype=np.int32)

line_total = quantity.astype(np.int64) * price.astype(np.int64)

print(line_total)
print(line_total.dtype)
```

Expected result:

```text
[50000000]
int64
```

The principle is more important than the exact dtype:

```text
Input dtype must be safe for the data.
Intermediate dtype must be safe for the arithmetic.
Output dtype must be safe for the downstream contract.
```

### 8.5 Inspect ranges before designing a dtype

For dynamic datasets, collect real range statistics when possible:

```python
minimum = values.min()
maximum = values.max()
print(minimum, maximum)
```

Then compare the observed range to a contract-defined safe range.

Do not infer safety from one sample file if production data can contain larger values.

---

## 9. Floating-Point Precision

### 9.1 What is floating point?

Floating-point representation stores numbers using a finite number of binary digits.

This is efficient and fast, but not every decimal number can be represented exactly in binary floating point.

### 9.2 Why `0.1 + 0.2 != 0.3`

Try:

```python
result = 0.1 + 0.2
print(result)
print(result == 0.3)
```

Typical output:

```text
0.30000000000000004
False
```

The important point is not that Python is "bad at arithmetic". The values 0.1 and 0.2 are represented approximately in binary floating point. The addition then operates on those binary approximations.

### 9.3 Precision vs range

A wider floating dtype generally gives you:

- more precision;
- more representable range;
- more memory cost.

The choice is workload-dependent.

```text
float16 → smaller, much less precise
float32 → smaller, common for large ML/numeric data
float64 → more precision, common for general analytical computation
```

### 9.4 Rounding error and accumulated error

If an operation is repeated many times, small representation errors can accumulate.

Examples include:

- summing millions of floating values;
- repeated transformations;
- financial calculations;
- statistics derived from transformed values.

This is why numerical pipelines should define acceptable tolerances instead of expecting bit-for-bit equality for every floating calculation.

### 9.5 Money: do not casually use floating point

When exact currency representation is required, do not store money as floating point merely because it is numeric.

Two common strategies are:

#### Strategy A — integer minor units

Store cents or another smallest currency unit:

```python
amount_cents = np.array([1299, 5000, 735], dtype=np.int64)
```

Then:

```text
$12.99 → 1299 cents
$50.00 → 5000 cents
```

This is often practical in data pipelines because integer arithmetic is exact within the chosen range.

#### Strategy B — `Decimal`

Python's `decimal.Decimal` is useful when decimal arithmetic semantics are required.

It is often used outside NumPy's homogeneous numeric array model, particularly at financial-system boundaries.

### 9.6 Financial example

Bad conceptual design:

```python
prices = np.array([10.10, 20.20, 30.30], dtype=np.float64)
```

Possible production design:

```python
prices_cents = np.array([1010, 2020, 3030], dtype=np.int64)
```

The second representation makes the business rule explicit: these are exact minor-unit amounts.

---

## 10. Casting and `astype`

Casting means converting data from one dtype to another.

### 10.1 Basic `astype`

```python
import numpy as np

x = np.array([1, 2, 3], dtype=np.int32)
y = x.astype(np.float64)

print(x.dtype)
print(y.dtype)
```

Output:

```text
int32
float64
```

`astype` is an important boundary because the conversion may create a new array and may lose information.

### 10.2 Integer → float

```python
x = np.array([1, 2, 3], dtype=np.int32)
y = x.astype(np.float32)
```

The small values are exactly representable here.

But not every large integer is exactly representable in `float32` or `float64`.

### 10.3 Float → integer

```python
x = np.array([1.9, 2.8, -3.2], dtype=np.float64)
y = x.astype(np.int32)

print(y)
```

Typical output:

```text
[ 1  2 -3]
```

The fractional part is discarded; this is not rounding to the nearest integer.

### 10.4 Larger → smaller integer

```python
x = np.array([1000], dtype=np.int16)
y = x.astype(np.int8)
print(y)
```

The value does not fit safely in `int8`, so a lossy conversion can occur.

### 10.5 `casting="safe"`

NumPy exposes explicit casting rules in APIs that support the `casting=` parameter.

For example:

```python
import numpy as np

source = np.array([1, 2, 3], dtype=np.int8)

safe = source.astype(np.int16, casting="safe")
print(safe)
```

This is valid because every `int8` value can be represented as `int16`.

Trying to safely narrow the representation should fail:

```python
import numpy as np

source = np.array([100, 120], dtype=np.int16)

try:
    result = source.astype(np.int8, casting="safe")
except TypeError as exc:
    print(type(exc).__name__)
```

The purpose of `safe` is to request that NumPy reject conversions that are not safely representable under NumPy's casting rules.

### 10.6 `casting="same_kind"`

`same_kind` is less restrictive than `safe` but still tries to prevent arbitrary cross-kind conversions.

Example:

```python
import numpy as np

source = np.array([1, 2, 3], dtype=np.int32)
result = source.astype(np.float64, casting="same_kind")
print(result)
```

This follows the same general numeric kind progression.

Use it when the operation should allow compatible kind conversions without allowing every possible lossy conversion.

### 10.7 `casting="unsafe"`

`unsafe` explicitly permits conversions that may lose information.

```python
import numpy as np

source = np.array([1.9, 2.8], dtype=np.float64)
result = source.astype(np.int8, casting="unsafe")
print(result)
```

Output:

```text
[1 2]
```

The conversion is allowed, but the information loss is your responsibility.

### 10.8 Engineering rule for casting

Before converting a production column, ask:

```text
Will every valid value fit?
Will arithmetic still be safe?
Will precision remain adequate?
Is the cast part of an explicit schema contract?
```

Do not use `unsafe` merely to make an error disappear. If a conversion is intentionally lossy, make that decision visible in the code and tests.

---

## 11. NumPy 2.x Type Promotion and NEP 50

### 11.1 What is type promotion?

When two values with different dtypes participate in an operation, NumPy must decide what dtype the result should have.

For example:

```python
import numpy as np

x = np.array([1, 2, 3], dtype=np.int32)
y = np.array([0.5, 1.5, 2.5], dtype=np.float64)

result = x + y

print(result)
print(result.dtype)
```

Expected output:

```text
[1.5 3.5 5.5]
float64
```

The integer input cannot remain an integer without losing the fractional part, so the operation needs a compatible floating representation.

### 11.2 Why NumPy 2 changed promotion behavior

Older NumPy versions had value-based promotion rules in which the value of a Python scalar could affect the resulting dtype. NEP 50 moved NumPy toward simpler, more predictable rules: Python `int`, `float`, and `complex` scalars are treated as weakly typed during promotion, so the array dtype generally determines how the scalar participates rather than inspecting the scalar's magnitude to choose a wider result type.

This is important when maintaining or migrating code because assumptions based on older NumPy versions can be wrong.

For example, in NumPy 2.x:

```python
import numpy as np

values = np.array([1, 2, 3], dtype=np.uint8)
result = values + 1

print(result.dtype)
```

The Python integer literal `1` is not automatically treated as a request to upcast the array to `int64`. It participates as a weak scalar, and the result can remain `uint8`.

That convenience has a critical implication: if the chosen dtype cannot represent the arithmetic result, you can still get overflow.

```python
import numpy as np

values = np.array([250], dtype=np.uint8)
result = values + 10

print(result)
print(result.dtype)
```

The result remains in the `uint8` domain and can wrap around rather than becoming a wider integer automatically.

### 11.3 Explicitly control promotion when correctness requires it

Use an explicit dtype when the arithmetic requires a known range:

```python
import numpy as np

values = np.array([250], dtype=np.uint8)
result = values.astype(np.uint16) + 10

print(result)
print(result.dtype)
```

Expected output:

```text
[260]
uint16
```

### 11.4 NumPy scalar vs Python scalar

Promotion rules can also differ when you deliberately provide a NumPy scalar with a dtype.

```python
import numpy as np

values = np.array([1, 2, 3], dtype=np.uint8)

python_scalar_result = values + 1
numpy_scalar_result = values + np.int64(1)

print(python_scalar_result.dtype)
print(numpy_scalar_result.dtype)
```

The second expression gives NumPy an explicitly typed scalar, so the type of that scalar participates in promotion.

This is a good production lesson:

> Do not guess what dtype an expression will produce. Inspect it, test it, and make important casts explicit.

### 11.5 Version-sensitive behavior

NEP 50 is a NumPy 2.x-era change. If a codebase supports multiple major NumPy versions, test dtype-sensitive expressions across the supported versions.

When you are diagnosing a migration issue, record:

```python
import numpy as np

print(np.__version__)
```

and then inspect:

```python
result = expression
print(result.dtype)
```

This avoids debugging a "mysterious" production mismatch without knowing the runtime version.

### 11.6 Practical promotion checklist

Before a critical numeric expression, ask:

```text
What are the input dtypes?
What dtype will the operation produce?
Can the intermediate result overflow?
Can precision be lost?
Do I need an explicit cast before the operation?
```

That habit is especially important for financial amounts, counters, IDs, and large aggregation pipelines.

---

## 12. `datetime64` and `timedelta64`

### 12.1 Why a dedicated datetime dtype exists

A timestamp is not just an arbitrary text string.

This:

```text
"2026-09-26 12:30:00"
```

is text.

A `datetime64` value is a typed NumPy value representing a date/time at a selected unit.

Typed timestamps allow you to perform comparisons and arithmetic without repeatedly parsing strings.

### 12.2 Creating `datetime64`

```python
import numpy as np

created_at = np.datetime64("2026-09-26T12:30:00", "s")
print(created_at)
print(created_at.dtype)
```

Typical output:

```text
2026-09-26T12:30:00
datetime64[s]
```

### 12.3 Millisecond precision

The roadmap's production example requires millisecond precision.

```python
created_at = np.datetime64("2026-09-26T12:30:00.125", "ms")
print(created_at)
print(created_at.dtype)
```

Output:

```text
2026-09-26T12:30:00.125
datetime64[ms]
```

### 12.4 Datetime units

Important units include:

| Unit | Meaning |
|---|---|
| `Y` | year |
| `M` | month |
| `D` | day |
| `h` | hour |
| `m` | minute |
| `s` | second |
| `ms` | millisecond |
| `us` | microsecond |
| `ns` | nanosecond |

For data engineering pipelines, the important principle is to choose a resolution that matches the source contract and downstream requirements.

### 12.5 Arrays of timestamps

```python
import numpy as np

timestamps = np.array(
    [
        "2026-09-26T12:00:00.000",
        "2026-09-26T12:00:00.250",
        "2026-09-26T12:00:00.500",
    ],
    dtype="datetime64[ms]",
)

print(timestamps)
print(timestamps.dtype)
```

### 12.6 Timestamp arithmetic

```python
import numpy as np

start = np.datetime64("2026-09-26T12:00:00", "s")
end = start + np.timedelta64(90, "s")

duration = end - start

print(end)
print(duration)
```

Output:

```text
2026-09-26T12:01:30
90 seconds
```

### 12.7 `timedelta64`

A `timedelta64` represents an amount of time rather than a timestamp.

```python
import numpy as np

delay = np.timedelta64(250, "ms")
print(delay)
print(delay.dtype)
```

Use it for:

- event durations;
- latency windows;
- batch intervals;
- scheduling calculations.

### 12.8 Comparing timestamps

```python
import numpy as np

events = np.array(
    [
        "2026-09-26T10:00:00",
        "2026-09-26T11:00:00",
        "2026-09-26T12:00:00",
    ],
    dtype="datetime64[s]",
)

cutoff = np.datetime64("2026-09-26T10:30:00", "s")

print(events > cutoff)
```

Output:

```text
[False  True  True]
```

This is preferable to lexicographically comparing timestamp strings because the dtype expresses the temporal semantics directly.

### 12.9 Converting datetime units

You can explicitly request another unit:

```python
import numpy as np

value = np.datetime64("2026-09-26T12:30:00.123456", "us")
value_ms = value.astype("datetime64[ms]")

print(value)
print(value_ms)
```

When converting to a coarser unit, information finer than that unit can be discarded. Treat time-resolution changes like any other potentially lossy conversion.

### 12.10 `NaT`

`NaT` means **Not A Time** and represents a missing datetime/timedelta value.

```python
import numpy as np

values = np.array(
    ["2026-09-26T12:00:00", "NaT"],
    dtype="datetime64[s]",
)

print(values)
print(np.isnat(values))
```

Typical output:

```text
['2026-09-26T12:00:00' 'NaT']
[False  True]
```

The missing-value behavior of datetime types will matter later when you process real DataFrames.

---

## 13. The Timezone Limitation of `datetime64`

NumPy's `datetime64` is **timezone-naive**. It does not carry full timezone-aware semantics such as an attached IANA timezone or a specific civil-time-zone interpretation.

The mental model is:

```text
datetime64
    ↓
calendar date/time value + resolution
    ↓
no embedded timezone identity
```

### Why this matters

Suppose one source sends:

```text
2026-09-26 12:00 Europe/London
```

and another sends:

```text
2026-09-26 12:00 Asia/Kolkata
```

Those are not the same instant.

A timezone-naive array alone cannot preserve that distinction.

This is why a production pipeline should define a clear timestamp contract, commonly by normalizing event instants to UTC at an appropriate system boundary and separately retaining business-local timezone information when it has semantic value.

Do not casually treat a timezone-naive `datetime64` as "local time" without knowing what the source means.

### Important NumPy behavior

NumPy documentation describes `datetime64` as a naive time with no explicit timezone or time-scale semantics. Parsing timezone-offset strings has also been deprecated. Treat timezone normalization as an explicit boundary concern rather than expecting `datetime64` to provide a complete timezone model.

### Data Engineering connection

Later DataFrame and data-platform tooling adds richer timestamp and timezone handling. The important lesson here is to understand what information your NumPy dtype actually stores so you do not silently lose timezone semantics during ingestion.

---

## 14. Memory Layout: The Foundation of the ndarray

At this point, you understand values, shapes, and dtypes. Now we need to understand how NumPy maps an index to memory.

The core mental model is:

```text
ndarray
├── data buffer
├── dtype
├── shape
└── strides
```

These pieces work together.

### Data buffer

The buffer contains the underlying element bytes.

### dtype

The dtype tells NumPy how to interpret each element and how many bytes the element occupies.

### shape

The shape tells NumPy how many positions exist along each axis.

### strides

The strides tell NumPy how many bytes it must move in memory when the index changes along each axis.

The important idea is:

> An ndarray is a data buffer plus metadata describing how to interpret that buffer.

That is why two arrays can refer to the same data but have different shapes or traversal patterns.

---

## 15. Strides

### 15.1 What is a stride?

A stride is the number of **bytes to step in memory** to move to the next element along a particular axis.

NumPy exposes it through:

```python
a.strides
```

### 15.2 Start with a 3 × 4 `int32` array

```python
import numpy as np

A = np.arange(12, dtype=np.int32).reshape(3, 4)

print(A)
print(A.shape)
print(A.dtype)
print(A.itemsize)
print(A.strides)
```

Output:

```text
[[ 0  1  2  3]
 [ 4  5  6  7]
 [ 8  9 10 11]]
(3, 4)
int32
4
(16, 4)
```

### 15.3 Why are the strides `(16, 4)`?

Each `int32` uses 4 bytes.

A row contains 4 elements:

```text
4 elements × 4 bytes = 16 bytes
```

Therefore:

```text
Move along axis 0 → skip 16 bytes
Move along axis 1 → skip 4 bytes
```

That gives:

```text
strides = (16, 4)
```

### 15.4 Visualizing the memory

Think of the raw storage as:

```text
48 bytes total

row 0                 row 1                 row 2
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│  0 │  1 │  2 │  3 │  4 │  5 │  6 │  7 │  8 │  9 │ 10 │ 11 │
└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
 4 B   4 B   4 B   4 B   4 B ...
```

The next column is 4 bytes away.

The next row begins 16 bytes away.

### 15.5 Calculating a byte offset manually

For an array with strides `(16, 4)`, the element at index `(2, 3)` has offset:

```text
offset = 2 × 16 + 3 × 4
       = 32 + 12
       = 44 bytes
```

The element at `(2, 3)` is therefore the 12th logical element, value `11`.

This formula generalizes:

```text
offset = i0 × stride0 + i1 × stride1 + ... + in × striden
```

### 15.6 Why shape and dtype are not enough

Imagine two arrays with the same shape and dtype. They can still have different strides.

That means:

```text
same shape
+
same dtype
≠
same memory traversal
```

This is one of the most important ideas in NumPy internals.

---

## 16. Transpose and Stride Reinterpretation

Take the previous array and transpose it:

```python
import numpy as np

A = np.arange(12, dtype=np.int32).reshape(3, 4)
B = A.T

print(B)
print(B.shape)
print(B.strides)
```

Output:

```text
[[ 0  4  8]
 [ 1  5  9]
 [ 2  6 10]
 [ 3  7 11]]
(4, 3)
(4, 16)
```

Notice what happened:

```text
A.shape    = (3, 4)
A.strides  = (16, 4)

B.shape    = (4, 3)
B.strides  = (4, 16)
```

The data does not need to be rearranged simply to change the interpretation.

The transpose changes the metadata describing how indices map to the same underlying storage.

This is why transpose can be cheap from a data-copy perspective while producing a non-C-contiguous result.

### Data Engineering lesson

A transformation that looks small in Python syntax can have a large consequence for downstream performance if a library later decides it needs a contiguous representation.

---

## 17. C Order vs Fortran Order

### 17.1 C order / row-major

C-order layout stores the last axis contiguously.

For a 2-D array:

```text
row 0 values
then row 1 values
then row 2 values
```

For our 3 × 4 example:

```text
0 1 2 3 4 5 6 7 8 9 10 11
```

The last axis, columns, moves fastest in memory.

### 17.2 Fortran order / column-major

Fortran-order layout stores the first axis contiguously.

A 3 × 4 array conceptually has memory traversal like:

```text
column 0 values
then column 1 values
then column 2 values
then column 3 values
```

### 17.3 Creating each order

```python
import numpy as np

C = np.arange(12, dtype=np.int32).reshape(3, 4, order="C")
F = np.arange(12, dtype=np.int32).reshape(3, 4, order="F")

print(C.strides)
print(F.strides)
```

Typical output:

```text
(16, 4)
(4, 12)
```

The exact values follow from the shape and four-byte `int32` elements.

### 17.4 Inspecting flags

```python
print(C.flags.c_contiguous)
print(C.flags.f_contiguous)

print(F.flags.c_contiguous)
print(F.flags.f_contiguous)
```

Typical output:

```text
True
False
False
True
```

### 17.5 Do not say “C is always faster”

That statement is incorrect.

Performance depends on the operation and access pattern.

If an algorithm walks along the contiguous dimension, it can benefit from sequential memory access. An algorithm that accesses the other dimension may not get the same benefit.

Also remember that Python-level loops are often much more expensive than the underlying cache effect. A fully vectorized operation can dominate the comparison even when the array is not laid out in your preferred order.

### 17.6 When memory order matters

Memory order can matter when:

- calling native numerical libraries;
- performing large matrix operations;
- passing arrays to extension code;
- repeatedly traversing one specific axis;
- avoiding hidden copies.

Your production question should be:

> What access pattern will this workload use, and what layout does the downstream operation prefer?

---

## 18. Array Flags

NumPy exposes memory-layout and mutability information through `.flags`.

```python
import numpy as np

x = np.arange(12, dtype=np.int32).reshape(3, 4)
print(x.flags)
```

The roadmap requires four flags.

### 18.1 `C_CONTIGUOUS`

True when the array is stored as one C-style contiguous segment.

```python
print(x.flags.c_contiguous)
```

### 18.2 `F_CONTIGUOUS`

True when the array is stored as one Fortran-style contiguous segment.

```python
print(x.flags.f_contiguous)
```

A 1-D array can satisfy both C and Fortran contiguity conditions because there is only one logical axis.

### 18.3 `OWNDATA`

Indicates whether the ndarray owns the memory it uses rather than borrowing its data from another object.

```python
print(x.flags.owndata)
```

Ownership is useful when reasoning about the lifetime and aliasing of storage.

### 18.4 `WRITEABLE`

Indicates whether the array's data area may be modified through that array.

```python
print(x.flags.writeable)
```

You can intentionally make an array read-only:

```python
x.flags.writeable = False
```

Then attempting to modify it raises an error.

This can be useful as a defensive technique when a function must not mutate shared input.

### 18.5 Why flags matter

Flags help answer:

```text
Is this array contiguous?
Does it own its storage?
Can I write through this reference?
Could a downstream library need a copy?
```

These are operational questions, not just debugging curiosities.

---

## 19. CPU Cache Locality and Memory Access

### 19.1 The basic idea

CPU access is not a uniform-cost operation. Modern systems use layers of fast cache memory between the CPU and main RAM.

A simplified hierarchy is:

```text
CPU registers
   ↓
L1 cache
   ↓
L2 cache
   ↓
L3 cache
   ↓
RAM
   ↓
Storage
```

The farther down the hierarchy the CPU must go, the more expensive access generally becomes.

### 19.2 Spatial locality

If code reads one memory location and then nearby locations, the CPU can often benefit from fetching a larger cache line containing neighboring bytes.

This is why sequential memory access is generally friendly to caches.

### 19.3 Connecting this to strides

Suppose an array is C-contiguous:

```python
x = np.arange(12, dtype=np.int32).reshape(3, 4)
```

Its last axis has stride 4 bytes.

Walking like this:

```python
x[0, 0]
x[0, 1]
x[0, 2]
x[0, 3]
```

moves through adjacent memory.

Walking down the first axis:

```python
x[0, 0]
x[1, 0]
x[2, 0]
```

jumps 16 bytes at each step.

Both are valid. The access patterns are different.

### 19.4 Why Data Engineers should care

For very large arrays, a poor memory-access pattern can reduce throughput and increase cache misses.

However, cache locality is only one part of NumPy performance.

This:

```python
for value in values:
    result.append(value * 2)
```

still pays Python-loop overhead.

The larger performance win usually comes from doing work in optimized native operations:

```python
result = values * 2
```

The engineering model is therefore:

```text
vectorization
+
appropriate dtype
+
reasonable memory layout
+
cache-friendly access pattern
=
strong numerical throughput
```

Do not optimize cache behavior while ignoring a much larger Python-level bottleneck.

---

## 20. Non-Contiguous Arrays and Possible Hidden Copies

A slice or transpose can produce an array whose elements are not laid out in one simple contiguous sequence.

For example:

```python
import numpy as np

A = np.arange(12, dtype=np.int32).reshape(3, 4)
B = A.T

print(A.flags.c_contiguous)
print(B.flags.c_contiguous)
print(B.flags.f_contiguous)
```

Typical output:

```text
True
False
True
```

A downstream library may prefer C-contiguous input. If it cannot efficiently operate on the existing layout, it may create a contiguous copy.

That can matter when `B` is hundreds of megabytes or several gigabytes.

Useful inspection tools include:

```python
print(B.strides)
print(B.flags)
print(B.nbytes)
```

and, when aliasing is relevant:

```python
print(np.shares_memory(A, B))
```

Do not try to solve every copy question in this topic. Topic 06 will develop the full view/copy and memory-efficiency model. Here, the key lesson is simply:

> A non-contiguous array is still a valid ndarray, but its layout can influence downstream performance and copying.

---

## 21. Structured Arrays

### 21.1 What is a structured dtype?

A structured dtype defines multiple named fields inside one element.

Conceptually, each element acts like a small record:

```text
record 0 → order_id + quantity + price
record 1 → order_id + quantity + price
record 2 → order_id + quantity + price
```

### 21.2 Defining a structured dtype

```python
import numpy as np

order_dtype = np.dtype([
    ("order_id", "<i8"),
    ("quantity", "<i2"),
    ("price_cents", "<i8"),
])

print(order_dtype)
```

The result is a dtype describing the layout of one record.

### 21.3 Creating structured records

```python
orders = np.array(
    [
        (1001, 3, 1299),
        (1002, 1, 2599),
        (1003, 5, 999),
    ],
    dtype=order_dtype,
)

print(orders)
print(orders["order_id"])
print(orders["price_cents"])
```

The fields can be accessed by name.

### 21.4 Why this resembles row-oriented storage

Each structured-array element behaves like a record containing multiple fields.

Conceptually:

```text
row 0 → order_id | quantity | price
row 1 → order_id | quantity | price
row 2 → order_id | quantity | price
```

That resembles row-oriented records.

Contrast it with separate arrays:

```text
order_ids   → [1001, 1002, 1003]
quantities  → [3, 1, 5]
prices      → [1299, 2599, 999]
```

This is more column-like.

### 21.5 Why columnar representation is attractive for analytics

Analytics often operates on only a subset of columns:

```text
SUM(price)
WHERE quantity > 2
```

A column-oriented representation makes it natural to process only the necessary columns and can improve memory locality for operations over one field.

This idea connects directly to later topics:

```text
NumPy arrays
    ↓
column-oriented analytical thinking
    ↓
Arrow
    ↓
Parquet
    ↓
Polars / pandas / analytical engines
```

Do not treat structured arrays as a replacement for a modern analytical table format. They are useful for understanding record-oriented layouts and for some specialized binary/data interchange workloads.

---

## 22. Strings in NumPy

Strings are more complicated than fixed-width numbers because their lengths vary.

NumPy supports multiple representations.

### 22.1 Fixed-width Unicode strings

A NumPy array can infer a fixed-width Unicode dtype:

```python
import numpy as np

names = np.array(["Ana", "Robert", "Mei"])
print(names)
print(names.dtype)
```

A result may look like:

```text
<U6
```

The `<` indicates little-endian Unicode storage representation in the dtype description, `U` represents Unicode strings, and `6` is the fixed maximum width for the elements.

### 22.2 The truncation risk

Fixed-width strings reserve a bounded width.

```python
import numpy as np

codes = np.array(["ABC"], dtype="<U3")
codes[0] = "ABCDEFG"

print(codes)
```

Output:

```text
['ABC']
```

The longer value cannot fit the declared fixed width, so assigning it can truncate the value.

This is a serious ingestion risk if you select a width from a small sample and later receive a larger string.

### 22.3 `bytes_`

NumPy also supports fixed-width byte strings.

```python
values = np.array([b"ABC", b"XYZ"], dtype="S3")
print(values)
print(values.dtype)
```

Byte strings are useful when the data contract is explicitly byte-oriented. Do not confuse bytes with Unicode text.

### 22.4 `object` arrays

An object array stores references to Python objects.

```python
import numpy as np

values = np.array(["short", "much longer text"], dtype=object)
print(values.dtype)
```

The array itself is homogeneous with respect to being an object array, but the referenced Python objects can have arbitrary types and sizes.

This makes object arrays flexible but often much less memory- and performance-efficient than compact numeric arrays.

For example:

```text
object array
→ pointer/reference
→ Python string object
→ variable memory + interpreter overhead
```

Use `object` intentionally. Accidental `object` dtype is a common data-ingestion bug because mixed input can push data out of a compact typed representation.

### 22.5 NumPy 2 `StringDType`

NumPy 2 introduced a variable-width `StringDType`.

```python
import numpy as np
from numpy.dtypes import StringDType

values = np.array(
    ["short string", "this is a much longer string"],
    dtype=StringDType(),
)

print(values)
print(values.dtype)
```

Unlike fixed-width strings, the elements do not need to reserve the same maximum string width.

A critical implementation detail is that `StringDType` does not store the actual string bytes in the main ndarray data buffer in the same way fixed-width string dtypes do. The array buffer stores metadata associated with the variable-width string storage.

That means code that assumes "the ndarray data pointer always contains the actual string characters" is not generally correct for `StringDType`.

### 22.6 Comparing the representations

| Representation | Width | Storage model | Main advantage | Main risk |
|---|---|---|---|---|
| fixed-width `str_` / `<U...` | fixed | string data in array element storage | simple, compact for bounded widths | truncation/padding |
| `bytes_` / `S...` | fixed | bytes in fixed-width storage | binary-oriented fixed-size values | wrong encoding/width assumptions |
| `object` | variable | Python object references | flexible | high overhead, slower object operations |
| `StringDType` | variable | variable-width string storage with array metadata | avoids fixed-width padding/truncation model | newer representation with different memory assumptions |

### 22.7 Data Engineering decision

Do not choose a string representation from aesthetics.

Ask:

```text
Are values truly bounded?
Is exact byte representation required?
Is the data Unicode text?
Will downstream systems understand the dtype?
Do I need compact numeric-style storage?
```

For most analytical pipelines, strings are generally better handled by purpose-built table/columnar systems rather than forcing arbitrary business text into an object-heavy NumPy representation.

---

## 23. Endianness

### 23.1 What is byte order?

Suppose a value occupies four bytes:

```text
0x01 02 03 04
```

A machine must decide which byte comes first in memory for the multi-byte value.

Two common conventions are:

```text
little-endian → least-significant byte first
big-endian    → most-significant byte first
```

### 23.2 Why this exists

Different processors and binary file formats can use different byte orders.

If a file writes a 32-bit integer in one order and you interpret it in another, you can decode the wrong number while still obtaining a syntactically valid numeric value.

### 23.3 NumPy dtype markers

You may encounter:

```text
<i8
>i8
```

Interpretation:

```text
<  → little-endian
>  → big-endian
 i8 → 8-byte signed integer
```

For example:

```python
import numpy as np

little = np.dtype("<i8")
big = np.dtype(">i8")

print(little)
print(big)
```

### 23.4 Why Data Engineers care

Endianness matters when handling:

- legacy binary formats;
- device telemetry;
- binary data exchange between systems;
- memory dumps;
- interoperability with systems written in other languages.

A binary file specification should state its byte order explicitly.

Do not assume the machine reading the data uses the same endianness as the producer.

---

## 24. Reading Raw Binary Data

NumPy can interpret bytes as typed arrays using `frombuffer` and `fromfile`.

### 24.1 `np.frombuffer`

Use `frombuffer` when the bytes are already available in memory.

```python
import numpy as np

raw = bytes([1, 0, 2, 0, 3, 0])
values = np.frombuffer(raw, dtype="<i2")

print(values)
```

Expected output:

```text
[1 2 3]
```

Why?

```text
<i2 → little-endian signed 2-byte integer

01 00 → 1
02 00 → 2
03 00 → 3
```

### 24.2 `np.fromfile`

Use `fromfile` to read raw binary values directly from a file.

A simplified example:

```python
import numpy as np

values = np.fromfile("readings.bin", dtype="<f4")
```

Here:

```text
<f4
```

means little-endian 4-byte floating-point values.

### 24.3 The contract you need before parsing bytes

Raw binary interpretation requires agreement about:

```text
dtype
+
byte order
+
element size
+
file structure
```

For example, if the producer writes:

```text
uint32 timestamp
float32 temperature
uint16 status
```

you need the file structure and field boundaries, not merely the statement "this is a binary file."

### 24.4 Why blindly using `fromfile` is dangerous

This is not a valid ingestion strategy:

```python
values = np.fromfile("unknown.dat", dtype=np.int64)
```

unless you know that the file is a raw sequence of 8-byte signed integers in the expected byte order.

Many binary formats contain headers, metadata, checksums, compression, variable-length records, or multiple field types.

### 24.5 `frombuffer` and ownership considerations

`frombuffer` can expose a view over a buffer object rather than allocating a second copy of the underlying bytes.

This can be memory-efficient, but it also means you should understand the lifetime and mutability characteristics of the original buffer.

For a read-only source such as `bytes`, the resulting array is read-only. If writes are needed, use `.copy()`:

```python
values = np.frombuffer(raw, dtype="<i2").copy()
```

Topic 06 will go deeper into view/copy and aliasing behavior.

---

## 25. Production Data Engineering Examples

The concepts in this chapter become easier when you repeatedly connect them to realistic columns.

### 25.1 Order IDs

If order IDs can reach 3 billion and never become negative, an unsigned 32-bit representation may be sufficient from a range perspective.

But ask:

```text
Will IDs ever be used in signed arithmetic?
Does the target file format support unsigned integers?
Does a downstream database expect BIGINT?
Will missing IDs need representation?
```

Range alone does not finish the design.

### 25.2 Quantities

For a quantity from 0 to 500:

```text
uint16 → safe range and compact storage
```

But if the pipeline later multiplies quantity by price, the **result** may require a wider dtype.

### 25.3 Financial amounts

Use exact minor-unit integers when the business model permits:

```python
amount_cents = np.array([1099, 2500, 99999], dtype=np.int64)
```

The important idea is not "int64 because money." It is:

```text
choose a representation that preserves exact business semantics
```

### 25.4 Customer identifiers

An identifier is not necessarily something you should use floating point for.

Avoid designs like:

```python
customer_id = np.array([10**16], dtype=np.float64)
```

Large integers can lose exactness when represented as floating point.

IDs should generally remain in an integer/string representation appropriate to the identifier contract.

### 25.5 Status codes

A small bounded code set can fit in a compact integer dtype.

```python
status_code = np.array([0, 1, 2, 3], dtype=np.uint8)
```

The semantic mapping should remain part of the schema rather than relying on undocumented numeric assumptions.

### 25.6 Country codes

A two-letter country code is textual data, not a number.

Do not invent numeric dtypes simply because they are compact.

If you encode country codes as integer lookup codes internally for a numerical operation, preserve the mapping and make the encoding explicit.

### 25.7 Timestamps

If the source guarantees millisecond precision:

```python
created_at = np.array(
    ["2026-09-26T12:00:00.123"],
    dtype="datetime64[ms]",
)
```

Do not store timestamps as arbitrary strings when the pipeline needs temporal arithmetic and comparison.

### 25.8 Sensor data

Sensor pipelines can contain millions of readings.

A compact design such as:

```text
device_id → uint32/int64 depending on contract
reading   → float32/float64 depending on precision requirement
timestamp → datetime64[ms] or another required resolution
status    → uint8
```

can substantially reduce memory compared with an object-heavy design.

### 25.9 Large batch datasets

For very large arrays, the difference between 4 and 8 bytes per value becomes large.

For 100 million values:

```text
float32 → ~400 MB
float64 → ~800 MB
```

Then remember that a transformation can create another array of similar size.

A pipeline can therefore run out of memory even when the input itself fits in RAM.

---

## 26. Production Exercise — `dtype_planner.py`

This exercise is intentionally designed to force engineering reasoning rather than memorization.

### Scenario

You are loading **50 million order rows**.

The columns are:

| Column | Domain |
|---|---|
| `order_id` | up to 3,000,000,000 |
| `quantity` | 0–500 |
| `unit_price_cents` | up to 10,000,000 |
| `country_code` | 2 letters |
| `is_gift` | yes/no |
| `created_at` | millisecond precision |

### Requirements

You must design an in-memory NumPy representation that:

1. safely represents the stated values;
2. does not waste memory unnecessarily;
3. leaves enough range for the required arithmetic;
4. makes timestamp resolution explicit;
5. is testable;
6. can be explained to another engineer.

### Part A — Reason before coding

For each column, write:

```text
Column:
Allowed values:
Chosen dtype:
Why it fits:
Why a smaller dtype would be unsafe:
What arithmetic may require a wider dtype:
Downstream interoperability concerns:
```

Do not start with `int64` for every integer column. Start from the data contract.

### Part B — Estimate memory

Calculate:

```text
rows × itemsize
```

for each fixed-width column.

Then calculate:

```text
total raw element storage
```

Compare this with an intentionally inefficient design using:

```text
int64 for numeric integer columns
object for country_code
```

Be explicit about what `object` means: the array itself contains references to Python objects; those Python objects have additional memory costs beyond the pointer/reference storage.

#### Worked reference calculation (50 million rows)

One reasonable fixed-width candidate:

| Column | Candidate dtype | Bytes/row |
|---|---|---:|
| `order_id` | `uint32` | 4 |
| `quantity` | `uint16` | 2 |
| `unit_price_cents` | `uint32` | 4 |
| `country_code` | `S2` | 2 |
| `is_gift` | `bool` | 1 |
| `created_at` | `datetime64[ms]` | 8 |
| **Total** | | **21** |

```text
50,000,000 × 21
= 1,050,000,000 bytes
≈ 1.05 GB
```

`S2` is only a reference design for two fixed-width bytes; it is not a universal text-storage recommendation.

Intentionally inefficient design: `int64` for the four integer columns (32 bytes), an 8-byte timestamp, and `object` for `country_code` (8-byte reference):

```text
48 bytes/row
50,000,000 × 48
= 2,400,000,000 bytes
≈ 2.40 GB
```

The `object` figure is only the array's reference storage. It does **not** include the additional memory consumed by the referenced Python string objects.

### Part C — Generate a realistic sample

Create a deterministic 1,000,000-row synthetic dataset using `np.random.default_rng()`.

Requirements:

- use a fixed seed;
- stay within the stated business ranges;
- use the candidate dtypes;
- make timestamp values millisecond precision;
- represent the country information in an intentionally documented way.

### Part D — Validate memory with NumPy

For every array print:

```python
array.shape
array.dtype
array.itemsize
array.nbytes
```

Verify:

```text
nbytes == size × itemsize
```

### Part E — Observe allocations

Use `tracemalloc` around the synthetic-data generation step.

Do not assume `tracemalloc` and `.nbytes` measure exactly the same thing.

Record:

```text
array element storage
peak Python-traced allocation
```

Explain why the values can differ.

### Part F — Demonstrate an overflow bug

Choose a calculation such as:

```python
line_total_cents = quantity * unit_price_cents
```

Design one intentionally unsafe version where the chosen intermediate dtype can overflow.

Then implement a deliberate upcast before arithmetic.

Your explanation must include:

```text
input range
×
input range
→
maximum possible product
→
required safe dtype
```

### Part G — Testing requirements

Write pytest tests that verify:

- every chosen dtype is exactly the expected dtype;
- each array has the expected shape;
- each array's memory usage stays within the planned budget;
- generated values are within the declared business ranges;
- the safe arithmetic version does not overflow for boundary values.

### Edge cases

Test at least:

```text
minimum valid values
maximum valid values
single-row dataset
empty dataset
boundary arithmetic result
country code longer than the intended fixed width
```

The final edge case should force you to reason about whether a fixed-width string design is safe for the actual ingestion contract.

### Deliverables

Inside the target learning project, your exercise implementation should contain:

```text
src/
└── dtype_planner.py

tests/
└── test_dtype_planner.py
```

This chapter intentionally does **not** provide the complete solution. The goal is to make you reason about dtype design before reading an answer.

### Validation checklist

Before considering the exercise complete, you should be able to answer:

```text
Why did I choose this dtype?
What is the maximum legal value?
What is the maximum intermediate arithmetic result?
How much memory does 1 million rows consume?
How much would 50 million rows consume?
What part of that estimate is raw element storage?
Which conversions create additional allocations?
What downstream system constraints could change my choice?
```

---

## 27. Debugging `ndarray` and dtype Problems

When a numerical pipeline behaves unexpectedly, do not guess. Inspect the array.

A strong first diagnostic is:

```python
print("shape:", a.shape)
print("dtype:", a.dtype)
print("itemsize:", a.itemsize)
print("nbytes:", a.nbytes)
print("strides:", a.strides)
print("flags:", a.flags)
```

When memory representation is relevant, you can also inspect:

```python
print(a.__array_interface__)
```

This exposes low-level array-interface metadata such as shape, strides, data pointer information, and dtype description. It is useful for understanding representation, but it should not be treated as an everyday business-logic API.

### Bug 1 — dtype changes after an operation

#### Broken code

```python
import numpy as np

ids = np.array([1, 2, 3])
print(ids.dtype)
```

An arithmetic operation may change a result dtype:

```python
values = np.array([1, 2, 3], dtype=np.int32)
result = values / 2

print(result.dtype)
```

Division produces floating-point results.

#### Detection

```python
print(result.dtype)
```

#### Engineering lesson

Do not assume an operation preserves the input dtype. Test important expressions and inspect result dtypes.

### Bug 2 — Integer overflow

#### Broken code

```python
import numpy as np

value = np.int8(127)
result = value + 1
print(result)
```

#### Why it is broken

`int8` cannot represent 128.

#### Fix

```python
result = np.int16(value) + 1
print(result)
```

The engineering lesson is to widen the dtype **before** the arithmetic when the intermediate range requires it.

### Bug 3 — Unexpected string truncation

#### Broken code

```python
import numpy as np

codes = np.array(["IN"], dtype="<U2")
codes[0] = "IND"
print(codes)
```

#### Why it is broken

The declared width is 2 Unicode characters.

#### Fix

Choose a width consistent with the real data contract or use a suitable variable-width representation when fixed-width storage is inappropriate.

### Bug 4 — Unexpected timestamp unit

#### Broken code

```python
import numpy as np

value = np.datetime64("2026-09-26T12:30:00.123", "s")
print(value)
```

The requested unit is seconds, so sub-second information is not preserved at that resolution.

#### Fix

```python
value = np.datetime64("2026-09-26T12:30:00.123", "ms")
print(value)
```

#### Engineering lesson

Timestamp precision is part of the data contract.

### Bug 5 — Unexpected memory usage

#### Symptom

A pipeline expects a 200 MB numeric array but the process consumes much more memory.

#### Inspection

```python
print(a.dtype)
print(a.nbytes)
print(a.shape)
```

Then look for:

- unintended `object` dtype;
- an unnecessary float64 representation;
- temporary arrays;
- explicit copies;
- duplicated batches.

#### Engineering lesson

`.nbytes` tells you the element storage for one array. Process-level memory can be much larger because of Python objects, multiple arrays, temporaries, allocator behavior, and other process resources.

### Bug 6 — Unexpected non-contiguous layout

#### Symptom

A downstream library behaves slower than expected or creates another large allocation.

#### Inspect

```python
print(a.strides)
print(a.flags.c_contiguous)
print(a.flags.f_contiguous)
```

#### Engineering lesson

A transpose or other stride-changing operation may produce a valid but non-C-contiguous view. If a downstream operation requires another layout, a hidden copy may appear.

---

## 28. Common Mistakes

### Mistake 1 — Accidentally creating `object` dtype

**Symptom:** arithmetic is slow and memory usage is unexpectedly high.

**Cause:** mixed input or explicit object construction.

**Detection:**

```python
print(a.dtype)
```

**Fix:** establish a consistent data type at the ingestion boundary when the domain supports it.

**Prevention:** validate dtypes after loading and before expensive transformations.

### Mistake 2 — Ignoring integer overflow

**Symptom:** a valid-looking but incorrect number appears after arithmetic.

**Cause:** the fixed-width dtype cannot represent the intermediate result.

**Detection:** compare the maximum possible intermediate value with `np.iinfo(dtype).max`.

**Fix:** deliberately upcast before the operation.

**Prevention:** include boundary-value tests and arithmetic-range analysis in the schema design.

### Mistake 3 — Storing timestamps as strings

**Symptom:** temporal calculations become cumbersome or inconsistent.

**Cause:** timestamp semantics were treated as text rather than data.

**Detection:**

```python
print(a.dtype)
```

**Fix:** use a documented datetime representation when NumPy datetime semantics are suitable.

**Prevention:** parse and validate timestamps at the ingestion boundary.

### Mistake 4 — Using `np.empty()` and reading before initialization

**Symptom:** unexplained values appear in output.

**Cause:** memory was allocated but not initialized.

**Detection:** review where every element is first written.

**Fix:** use `zeros`, `ones`, `full`, or fully overwrite the `empty` array before reading.

**Prevention:** use `empty` only in controlled preallocation code.

### Mistake 5 — Assuming `float64` is always safer

**Symptom:** memory consumption doubles compared with float32 but business precision does not improve materially.

**Cause:** defaulting to a larger dtype without a precision analysis.

**Fix:** choose a dtype based on required numerical accuracy and range.

**Prevention:** document dtype requirements in the pipeline contract.

### Mistake 6 — Assuming every NumPy scalar behaves like a Python scalar

**Symptom:** result dtypes change after a NumPy upgrade.

**Cause:** NumPy 2 type-promotion rules differ from older value-based assumptions.

**Fix:** inspect and explicitly cast where dtype is business-critical.

**Prevention:** test dtype-sensitive expressions under the supported NumPy versions.

### Mistake 7 — Assuming transpose means data was physically copied

**Symptom:** memory analysis shows less allocation than expected, but downstream performance changes.

**Cause:** transpose can change strides without copying the data.

**Fix:** inspect `.strides`, flags, and memory-sharing relationships.

**Prevention:** develop the habit of asking "what changed in the metadata?" before assuming the bytes moved.

---

## 29. Checkpoint — Self-Test Before Moving On

Do not look at notes or the roadmap while answering these questions.

### Fundamentals

1. What is an `ndarray`?
2. Why is homogeneous fixed-size storage useful?
3. What is the difference between `ndim`, `shape`, and `size`?
4. What does `.dtype` tell you?
5. What is the difference between `.itemsize` and `.nbytes`?

### Memory model

6. Why does a NumPy `int64` array generally use much less raw element storage than a Python list of Python integers?
7. Why does `sys.getsizeof(my_list)` not give the full recursive memory footprint of all integer objects referenced by the list?
8. If an array has shape `(3, 4)` and dtype `int32`, how many values are there and how many bytes of raw element storage are required?

### Integer correctness

9. State the range of `int8`.
10. State the range of `uint8`.
11. State the range of `int32`.
12. State the range of `int64`.
13. Why can an operation overflow even when both individual inputs fit in their dtypes?
14. Why is an explicit upcast sometimes required before multiplication?

### Floating-point correctness

15. Why can `0.1 + 0.2` differ from `0.3`?
16. What is the difference between precision and range for floating-point types?
17. Why should exact monetary values not be casually stored as floating point?
18. When might integer cents be a good representation?

### Casting and promotion

19. What does `astype()` do?
20. What is the purpose of `casting="safe"`?
21. What is the role of `casting="same_kind"`?
22. What does `casting="unsafe"` permit?
23. What changed with NumPy 2 and NEP 50 at a high level?
24. Why should dtype-sensitive production code test its actual result dtype?

### Datetime

25. What is `datetime64`?
26. What is `timedelta64`?
27. What does `datetime64[ms]` communicate?
28. What is `NaT`?
29. Why is NumPy `datetime64` called timezone-naive?

### Memory layout

30. What is a stride?
31. For a `(3, 4)` `int32` C-order array, why are the typical strides `(16, 4)`?
32. If the shape is `(3, 4)` and `int32` has a 4-byte item size, how many bytes are required to move from one row to the next in C order?
33. What happens to shape and strides after a transpose?
34. What is C order?
35. What is Fortran order?
36. Why is it incorrect to say that C order is always faster?
37. What does `C_CONTIGUOUS` mean?
38. What does `F_CONTIGUOUS` mean?
39. What does `OWNDATA` tell you?
40. What does `WRITEABLE` tell you?

### Advanced representation

41. What is cache locality?
42. Why can contiguous access be friendlier to CPU caches?
43. Why can a downstream library create a copy from a non-contiguous array?
44. What is a structured dtype?
45. Why do structured arrays resemble row-oriented records?
46. Why are separate columns often attractive for analytical workloads?
47. What is the difference between fixed-width NumPy strings, `object` strings, and `StringDType`?
48. What does `<i8` mean?
49. What does `>i8` mean?
50. When should you use `np.frombuffer` instead of `np.fromfile`?

### Production reasoning

51. Before choosing a dtype for a production column, what questions should you ask?
52. Why is "smallest dtype possible" not sufficient as an engineering rule?
53. Why must downstream interoperability be considered?
54. What information do `.shape`, `.dtype`, `.itemsize`, `.nbytes`, `.strides`, and `.flags` collectively tell you?
55. You receive 50 million rows. Why should you think about temporary arrays even if the input array fits in RAM?

### Checkpoint rule

You are ready for Topic 02 only when you can answer these without memorized wording and can demonstrate the key claims with code.

Minimum practical proof:

```text
I can inspect an array.
I can calculate its memory footprint.
I can choose a safe dtype.
I can demonstrate integer overflow.
I can explain floating-point precision.
I can use datetime64 intentionally.
I can calculate strides.
I can explain C/F order.
I can diagnose contiguity.
I can explain structured/string representations.
I can interpret endianness.
I can read documented raw binary data correctly.
```

---

## 30. Final Mental Model

Keep this hierarchy in your head:

```text
Python object
      ↓
ndarray
      ↓
data buffer
      ↓
dtype
      ↓
shape
      ↓
strides
      ↓
memory order / contiguity
      ↓
CPU cache + access pattern
      ↓
performance + memory behavior
```

A second model is useful for production decisions:

```text
Business data contract
        ↓
valid value range
        ↓
required precision
        ↓
arithmetic requirements
        ↓
dtype choice
        ↓
memory footprint
        ↓
layout / interoperability
        ↓
production behavior
```

### Before creating a large NumPy array, ask

```text
1. What values can exist?
2. What dtype safely represents them?
3. How much memory will it consume?
4. Can arithmetic overflow?
5. What precision is required?
6. What timestamp resolution is required?
7. What memory layout will downstream code prefer?
8. Could binary data have a specific endianness?
```

### The central lesson

A NumPy array is not just "a bunch of Python numbers".

It is a typed memory representation whose behavior follows from its:

```text
data buffer
+ dtype
+ shape
+ strides
```

Once you can reason about those four pieces, many behaviors that otherwise feel mysterious become predictable.

---

## 31. Connection to the Next Topics

This topic is deliberately first because later NumPy behavior depends on the array model you have learned here.

```text
01 ndarray / dtypes / memory layout
        ↓
02 vectorization / broadcasting
        ↓
03 indexing / masks / fancy indexing
        ↓
04 aggregations / axis semantics
        ↓
05 missing values / NaN / sentinels
        ↓
06 views / copies / memory efficiency
```

### Why Topic 01 comes first

**Vectorization and broadcasting** need you to understand shape and dtype before you can predict results.

**Indexing** changes which positions are selected, so you need a basic mental model of array structure and memory access.

**Aggregations** depend on dimensions and axes, which are parts of the array shape.

**Missing-value handling** interacts with dtype rules, especially the difference between floating-point NaN and integer representations.

**Views, copies, and memory efficiency** depend directly on the underlying buffer, dtype, shape, strides, and contiguity concepts developed here.

The sequence is therefore not arbitrary:

```text
understand the representation
        ↓
understand computation
        ↓
understand selection
        ↓
understand summarization
        ↓
understand missing data
        ↓
optimize memory safely
```

Do not move forward by memorizing individual APIs. Carry the memory model with you.

---

## 32. Reference Implementation Patterns

The following small patterns are worth keeping as reusable habits while studying this topic.

### Pattern 1 — Inspect before operating

```python
import numpy as np


def inspect(name: str, a: np.ndarray) -> None:
    print(f"{name}: shape={a.shape}, dtype={a.dtype}, "
          f"itemsize={a.itemsize}, nbytes={a.nbytes}, "
          f"strides={a.strides}")
```

Use this when a result surprises you.

### Pattern 2 — Check range before narrowing

```python
import numpy as np

values = np.array([0, 10, 200], dtype=np.int64)
limits = np.iinfo(np.uint8)

if values.min() >= limits.min and values.max() <= limits.max:
    compact = values.astype(np.uint8)
else:
    raise ValueError("Values do not fit in uint8")
```

### Pattern 3 — Upcast before risky arithmetic

```python
safe_left = left.astype(np.int64)
safe_right = right.astype(np.int64)
result = safe_left * safe_right
```

### Pattern 4 — Make timestamp resolution explicit

```python
created_at = np.array(
    ["2026-09-26T12:00:00.123"],
    dtype="datetime64[ms]",
)
```

### Pattern 5 — Verify layout when it matters

```python
print(a.shape)
print(a.strides)
print(a.flags.c_contiguous)
print(a.flags.f_contiguous)
```

### Pattern 6 — Never trust a binary file without its schema

Before:

```python
np.fromfile(path, dtype=...)
```

write down:

```text
element type
byte order
element size
header length
record structure
version
```

Then implement the parser.

---

## 33. Production Review Checklist

Use this checklist in code review for NumPy-heavy data pipelines.

### Representation

- Is every major numeric array's dtype intentional?
- Are ranges documented?
- Are timestamps represented with an explicit unit?
- Are strings being handled deliberately rather than accidentally becoming `object`?

### Correctness

- Are maximum intermediate arithmetic values safe?
- Are floating-point tolerances defined where appropriate?
- Is money represented exactly when required?
- Are lossy casts explicit and tested?

### Memory

- Is `.nbytes` known for large arrays?
- Could transformations create additional full-size arrays?
- Could a downstream library require a contiguous copy?
- Is an inefficient dtype causing avoidable memory pressure?

### Layout

- Are strides understood for performance-sensitive sections?
- Is the chosen C/F order appropriate for the workload?
- Are non-contiguous arrays passed into libraries that may copy them?

### Binary ingestion

- Is dtype explicitly specified?
- Is byte order documented?
- Is the binary file structure documented?
- Is the producer/consumer contract tested with known bytes?

### Operational safety

- Are array shapes validated at ingestion boundaries?
- Are dtypes validated before expensive processing?
- Are edge cases tested?
- Are version-sensitive NumPy behaviors covered by tests?

---

## 34. Practice: Predict Before You Run

The most valuable habit from this chapter is prediction.

For every important NumPy expression, write down:

```text
Input shape:
Input dtype:
Expected output shape:
Expected output dtype:
Expected strides/layout:
Potential overflow/precision issue:
Potential allocation/copy issue:
```

Then execute the code and compare your prediction with reality.

Example:

```python
import numpy as np

A = np.arange(12, dtype=np.int32).reshape(3, 4)
B = A.T
```

Before running, predict:

```text
A.shape   → (3, 4)
A.dtype   → int32
A.strides → (16, 4)

B.shape   → (4, 3)
B.dtype   → int32
B.strides → (4, 16)
```

Then verify:

```python
print(A.shape, A.dtype, A.strides)
print(B.shape, B.dtype, B.strides)
```

The objective is not to memorize `(16, 4)`. It is to learn how to derive it.

---

## 35. What You Should Be Able to Explain to Another Engineer

Imagine a senior engineer asks:

> Why did you choose this dtype?

A strong answer is not:

> "It seemed small enough."

A strong answer is:

> "The column contract is 0–500, so `uint16` is sufficient for the stored quantity. The multiplication with price can exceed that range, so the calculation explicitly upcasts to a wider integer dtype before arithmetic. The chosen representation cuts raw element storage compared with `int64` while preserving the required range."

Imagine they ask:

> Why is this transpose unexpectedly slower downstream?

A strong answer is:

> "The transpose changed the shape and strides. The resulting array is not C-contiguous, so the downstream operation may traverse memory less efficiently or allocate a contiguous copy. I inspected `.strides` and `.flags` to verify the layout."

Imagine they ask:

> Why did this timestamp lose milliseconds?

A strong answer is:

> "The array was created at seconds resolution, so the representation did not preserve millisecond information. The timestamp contract requires `datetime64[ms]`, so the conversion boundary needs to use that unit explicitly."

That level of explanation is the target of this topic.

---

## 36. Key Takeaways

1. `ndarray` is NumPy's core homogeneous N-dimensional array structure.
2. `shape` describes logical dimensions; `dtype` describes element representation; `strides` describe memory movement.
3. `.size × .itemsize = .nbytes` for the array's raw element storage.
4. NumPy numeric arrays can be much more compact than lists of Python numeric objects.
5. Smaller dtypes save memory, but only when range, precision, arithmetic, and interoperability remain safe.
6. Integer overflow can produce incorrect results without looking obviously invalid.
7. Floating-point values are approximate binary representations; exact monetary semantics usually require integer minor units or `Decimal` at appropriate boundaries.
8. NumPy 2 uses the NEP 50 promotion model, so old value-based promotion assumptions can be misleading.
9. `datetime64` carries a selected time resolution but is timezone-naive.
10. Strides are byte steps along axes; they explain how the same buffer can be viewed with different shapes and traversal orders.
11. C and Fortran order describe different contiguous layouts; neither is universally faster.
12. Array flags expose contiguity, ownership, and writeability information.
13. Memory layout can affect CPU cache behavior and can cause downstream libraries to create copies.
14. Structured arrays describe record-like data; column-wise arrays align more naturally with analytical columnar processing.
15. Fixed-width strings, object strings, and NumPy 2 `StringDType` have different memory and behavioral trade-offs.
16. Endianness is part of a binary-data contract.
17. `frombuffer` works with bytes already in memory; `fromfile` reads raw binary data from a file.
18. Production NumPy work starts with a data contract, not with a default dtype.

---

## 37. Official References

Use the official documentation to verify version-sensitive details and API behavior:

- [NumPy User Guide — NumPy 2.x](https://numpy.org/doc/stable/user/)
- [The N-dimensional array (`ndarray`)](https://numpy.org/doc/stable/reference/arrays.ndarray.html)
- [NumPy data types](https://numpy.org/doc/stable/user/basics.types.html)
- [NumPy NEP 50 — Promotion rules for Python scalars](https://numpy.org/neps/nep-0050-scalar-promotion.html)
- [NumPy 2.0 migration guide](https://numpy.org/devdocs/numpy_2_0_migration_guide.html)
- [NumPy datetimes and timedeltas](https://numpy.org/doc/stable/reference/arrays.datetime.html)
- [NumPy array strides](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.strides.html)
- [NumPy array flags](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.flags.html)
- [NumPy strings and bytes](https://numpy.org/doc/stable/user/basics.strings.html)

For floating-point background, see David Goldberg's classic paper:

- *What Every Computer Scientist Should Know About Floating-Point Arithmetic*

For broader NumPy practice:

- Wes McKinney, *Python for Data Analysis*, 3rd edition
- Nicolas P. Rougier, *From Python to NumPy*

---

## 38. Completion Standard for Topic 01

Do not mark Topic 01 complete merely because you have read the chapter.

You should have produced evidence:

```text
[ ] ndarray attributes inspected on multiple arrays
[ ] dtype ranges tested with real code
[ ] integer overflow demonstrated
[ ] deliberate upcast demonstrated
[ ] floating-point precision example reproduced
[ ] money representation decision explained
[ ] astype and casting rules exercised
[ ] NumPy 2 promotion behavior tested
[ ] datetime64 units exercised
[ ] timezone-naive limitation explained
[ ] stride calculations done by hand
[ ] C/F order inspected
[ ] flags inspected
[ ] contiguity behavior observed
[ ] structured dtype example implemented
[ ] fixed-width string truncation reproduced
[ ] object string overhead discussed
[ ] StringDType example tested on NumPy 2.x
[ ] endianness decoded from explicit bytes
[ ] frombuffer example completed
[ ] fromfile example completed against a known raw binary file
[ ] dtype_planner exercise completed
[ ] pytest validation written
[ ] checkpoint questions answered without notes
```

When these are complete, Topic 01 has served its purpose: you can now reason about NumPy arrays as typed memory rather than treating them as mysterious Python containers.

---

> **End of Topic 01 — `ndarray`, dtypes, and Memory Layout**
