# Topic 06 — Views, Copies, and Memory Efficiency

> **Stage 2 — Python for Data Engineering**  
> **Module 2.2 — Numerical Computing with NumPy**  
> **Final Topic: Views, Copies, and Memory Efficiency**

---

## Learning objective

The central engineering question for this chapter is:

> **How can I write NumPy code that is memory-safe, mutation-safe, and performant when processing large datasets?**

By the end of this chapter, you should be able to reason about a NumPy array in terms of:

```text
ndarray
  ↓
data buffer
  ↓
shape + dtype + strides
  ↓
view or copy?
  ↓
who owns the buffer?
  ↓
who can mutate it?
  ↓
what temporary arrays are allocated?
  ↓
what is peak memory?
  ↓
can I reuse storage with in-place operations or out=?
  ↓
should I chunk the work?
  ↓
should I memory-map the data?
  ↓
is the layout contiguous?
  ↓
will another library copy it?
  ↓
can the data cross an API boundary without copying?
  ↓
is NumPy still the right execution model?
```

This is the final topic of the NumPy module because it integrates the ideas learned earlier:

| Topic | Question it answered |
|---|---|
| 01 — ndarray, dtypes, memory layout | What is the array and how is it stored? |
| 02 — vectorization and broadcasting | How can I compute efficiently on arrays? |
| 03 — indexing and masks | How do I select data? |
| 04 — aggregations and axis semantics | How do I summarize data correctly? |
| 05 — NaN, missing values, and sentinels | How do I represent invalid or missing observations? |
| **06 — views, copies, and memory efficiency** | **How do I do all of that without corrupting data or exhausting memory?** |

---

# 1. Introduction

When a NumPy program processes a tiny array, it is easy to ignore how memory is being handled.

When the same program processes 10 million rows, 50 million rows, or hundreds of millions of numeric values, memory behavior becomes part of correctness.

Two broad categories of failure appear:

```text
Correctness failure
→ accidental mutation through a shared view

Scalability failure
→ unnecessary copies and temporary arrays consume too much memory
```

A production Data Engineering pipeline can fail even when every mathematical formula is correct.

For example:

- A transformation function receives a view and mutates it.
- A downstream stage unexpectedly sees changed raw data.
- A Boolean filter materializes a large selected array.
- A transpose creates a non-contiguous layout and a native library silently copies it.
- A tiny returned slice keeps a multi-gigabyte parent allocation alive.
- An innocent expression creates several full-size temporary arrays at once.
- A batch job reaches its memory limit because peak memory, not final output size, is too high.
- A memory-mapped file is accessed randomly and performs poorly because storage access cannot compete with RAM.

These are engineering problems, not merely NumPy syntax problems.

## Why this matters at data-engineering scale

Suppose a dataset contains:

```text
50,000,000 values
```

A single `float64` value occupies 8 bytes:

```text
50,000,000 × 8
= 400,000,000 bytes
≈ 381.47 MiB
≈ 0.40 GB
```

The array itself is already large.

Now imagine a transformation such as:

```python
result = (a - a.mean()) / a.std() * 100 + 5
```

Depending on the implementation and lifetime of intermediate results, more than one additional array can exist.

The right question is therefore not only:

> "How many bytes is my final result?"

It is:

> **"What is the maximum amount of storage that can be live at one time?"**

That quantity is **peak memory**.

---

# 2. The ndarray memory model recap

A NumPy array is a data structure that describes a block of typed data.

Conceptually:

```text
ndarray
├── data buffer
├── dtype
├── shape
└── strides
```

The **data buffer** contains bytes.

The **dtype** tells NumPy how to interpret those bytes.

The **shape** tells NumPy the logical dimensions.

The **strides** tell NumPy how many bytes to move in the underlying buffer when moving one element along each axis.

## Why strides matter for views

A view can often reuse the same data buffer while changing only the metadata:

```text
same buffer
+
different shape
+
different strides
=
another logical array view
```

A copy generally does this instead:

```text
original
  ↓
buffer A

copy
  ↓
buffer B
```

The two buffers are independent.

This distinction drives almost everything in this chapter.

---

# 3. What is a view?

A **view** is another NumPy array object that accesses the same underlying data storage as another array.

A useful mental model is:

> A view is another way of looking at the same bytes.

Visual:

```text
Original array ─────┐
                    ↓
              shared buffer
                    ↑
View ───────────────┘
```

A view can have:

- the same dtype or a different interpretation in advanced cases,
- a different shape,
- different strides,
- different axis order,
- a different starting offset into the buffer.

The important property is shared storage.

## Simple one-dimensional example

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50])

view = a[1:4]

print("a:", a)
print("view:", view)
print("shares memory:", np.shares_memory(a, view))

view[0] = 999

print("a after mutation:", a)
print("view after mutation:", view)
```

Output:

```text
a: [10 20 30 40 50]
view: [20 30 40]
shares memory: True
a after mutation: [ 10 999  30  40  50]
view after mutation: [999  30  40]
```

The assignment changed both arrays because they refer to overlapping storage.

## What did not happen?

NumPy did **not** copy the values `[20, 30, 40]` into a new buffer when the slice was created.

The slice was cheap to create because it changed how the same storage was accessed.

---

# 4. What is a copy?

A **copy** allocates independent storage for the result.

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50])

copy = a[1:4].copy()

print("shares memory:", np.shares_memory(a, copy))

copy[0] = 999

print("a:", a)
print("copy:", copy)
```

Output:

```text
shares memory: False
a: [10 20 30 40 50]
copy: [999 30 40]
```

The important difference is:

```text
View
→ shared memory
→ cheap to create
→ mutation can affect the source

Copy
→ independent storage
→ costs memory and copying time
→ mutation is isolated
```

Neither is universally better.

Good engineering means making the ownership choice deliberately.

---

# 5. Memory ownership

NumPy arrays expose flags that describe important storage properties.

```python
import numpy as np

a = np.arange(6)

print(a.flags)
print("owns data:", a.flags["OWNDATA"])
print("writeable:", a.flags["WRITEABLE"])
```

For an array created directly by NumPy, `OWNDATA` is commonly `True`.

A slice usually does not own the underlying buffer itself:

```python
import numpy as np

a = np.arange(6)
view = a[1:5]

print("a owns data:", a.flags["OWNDATA"])
print("view owns data:", view.flags["OWNDATA"])
print("view.base is a:", view.base is a)
```

A typical result is:

```text
a owns data: True
view owns data: False
view.base is a: True
```

## What does ownership mean?

Ownership means:

> This array is the owner of the memory buffer associated with its data.

A view can use storage owned by another object.

This is why a view can outlive the expression that created it while still keeping the underlying storage alive.

## `.base`

The `.base` attribute can help you inspect the relationship:

```python
import numpy as np

a = np.arange(10)
view = a[2:7]

print(type(view.base))
print(view.base is a)
```

Often, `.base` points to the object that supplied the storage.

However:

> `.base` is an inspection aid, not a definitive general-purpose memory-sharing test.

Why?

Because array relationships can be indirect. A result can be derived through several array objects, and `.base` is not intended to answer the complete question:

> "Do these two arrays overlap in memory?"

For that question, use `np.shares_memory`.

---

# 6. `np.shares_memory`

Use:

```python
np.shares_memory(a, b)
```

to ask whether two arrays actually share memory.

Example:

```python
import numpy as np

a = np.arange(10)

view = a[2:7]
copy = a[2:7].copy()

print("slice shares memory:", np.shares_memory(a, view))
print("copy shares memory:", np.shares_memory(a, copy))
```

Output:

```text
slice shares memory: True
copy shares memory: False
```

## Why it is useful

This is particularly valuable when a transformation has conditional behavior.

For example, `reshape` can return a view when possible and may need a copy for another layout.

Instead of guessing:

```python
result = a.reshape(...)
```

verify:

```python
np.shares_memory(a, result)
```

## Memory sharing versus object identity

These are different concepts.

```python
import numpy as np

a = np.arange(5)
b = a

print("same Python object:", a is b)
print("share memory:", np.shares_memory(a, b))
```

Output:

```text
same Python object: True
share memory: True
```

Now compare a view:

```python
import numpy as np

a = np.arange(5)
b = a[:]

print("same Python object:", a is b)
print("share memory:", np.shares_memory(a, b))
```

Output:

```text
same Python object: False
share memory:", np.shares_memory(a, b))
```

The second line contains an accidental syntax typo if written that way; the correct code is:

```python
print("share memory:", np.shares_memory(a, b))
```

Output:

```text
same Python object: False
share memory: True
```

So:

```text
a is b
```

answers identity, while:

```text
np.shares_memory(a, b)
```

answers actual storage overlap.

---

# 7. `np.may_share_memory`

NumPy also provides:

```python
np.may_share_memory(a, b)
```

This is a **conservative** check.

Its job is to determine whether there is a possibility that two arrays share memory.

Conceptually:

```text
shares_memory
→ actual overlap?

may_share_memory
→ could there be overlap?
```

A `True` result from `may_share_memory` does **not** necessarily prove that the arrays overlap.

This distinction is important.

```python
import numpy as np

a = np.arange(10)

even = a[::2]
odd = a[1::2]

print("actual overlap:", np.shares_memory(even, odd))
print("possible overlap:", np.may_share_memory(even, odd))
```

For strided arrays, `may_share_memory` can be conservative.

Use the functions for their intended purposes:

| Tool | Meaning | Good use |
|---|---|---|
| `.base` | Inspect an array-storage relationship | Exploration and debugging |
| `np.shares_memory` | Determine actual memory overlap | Correctness reasoning |
| `np.may_share_memory` | Determine whether overlap is possible | Conservative checks and fast reasoning |

---

# 8. Basic slicing returns views

The fundamental rule to remember is:

> **Basic slicing returns a view.**

Examples:

```python
import numpy as np

a = np.arange(12).reshape(3, 4)

row_slice = a[1:]
column_slice = a[:, 1:3]
step_slice = a[::2, ::2]

print("row shares:", np.shares_memory(a, row_slice))
print("column shares:", np.shares_memory(a, column_slice))
print("step shares:", np.shares_memory(a, step_slice))
```

Each basic slice can reuse the original buffer.

Common patterns:

```python
a[1:5]
a[::2]
a[:, 1:4]
a[1:, ::2]
```

## Why slicing is cheap

A slice usually changes metadata rather than allocating all selected values into a new buffer.

That is a major reason NumPy can manipulate large arrays efficiently.

## But a cheap slice can still retain expensive memory

Consider:

```text
huge array
    ↓
small slice
    ↓
returned from function
    ↓
caller keeps slice
```

If the slice still points into the huge parent allocation:

```text
tiny result
    ↓
shared with
    ↓
large underlying buffer
```

The small array's `nbytes` does not reveal the retained parent allocation.

This is one of the most counterintuitive memory-retention behaviors in NumPy.

---

# 9. Small-view retention: when copying saves memory

Suppose a service reads a 2 GiB array and wants to return only 10 values.

This:

```python
return data[:10]
```

may return a tiny view that still keeps the full underlying allocation alive.

A deliberate copy can instead do:

```python
return data[:10].copy()
```

Now the returned result owns independent small storage.

Conceptually:

```text
2 GB source
    ↓
tiny slice
    ↓
returned to caller
    ↓
2 GB source remains alive
```

versus:

```text
2 GB source
    ↓
tiny slice
    ↓
small copy
    ↓
source can be released
```

This leads to an important rule:

> **A copy is not always the memory-expensive choice at the system level.**

A small copy can reduce retained memory by allowing a much larger source allocation to become reclaimable.

Use `.copy()` when the resulting ownership and lifetime make that trade-off worthwhile.

---

# 10. Reshape: view when possible

`reshape` changes an array's logical shape:

```python
a.reshape(...)
```

It can return a view **when the existing memory layout makes the requested interpretation possible**.

Otherwise it may need to allocate a copy.

Example:

```python
import numpy as np

a = np.arange(12)

reshaped = a.reshape(3, 4)

print("shares memory:", np.shares_memory(a, reshaped))
print("original:", a)
print("reshaped:\n", reshaped)
```

For a contiguous one-dimensional array, the reshape commonly shares storage.

## Why does layout matter?

Imagine a contiguous one-dimensional sequence:

```text
0 1 2 3 4 5 6 7 8 9 10 11
```

A `(3, 4)` view can interpret those elements as:

```text
0  1  2  3
4  5  6  7
8  9 10 11
```

No data movement is necessary.

But consider a non-contiguous input:

```python
import numpy as np

base = np.arange(24).reshape(4, 6)
transposed = base.T

result = transposed.reshape(-1)

print("transposed contiguous:", transposed.flags["C_CONTIGUOUS"])
print("result shares memory:", np.shares_memory(transposed, result))
```

Do not assume what `reshape` will do from the expression alone. Verify.

## Engineering habit

Whenever a transformation can be layout-dependent:

```python
result = transform(a)
```

and memory behavior matters:

```python
print(np.shares_memory(a, result))
print(result.flags)
```

Prediction first, verification second.

---

# 11. Transpose and `.T`

For a two-dimensional array:

```python
a.T
```

swaps the axes.

Example:

```python
import numpy as np

a = np.arange(12).reshape(3, 4)
t = a.T

print("a shape:", a.shape)
print("t shape:", t.shape)
print("a strides:", a.strides)
print("t strides:", t.strides)
print("shares memory:", np.shares_memory(a, t))
print("a C-contiguous:", a.flags["C_CONTIGUOUS"])
print("t C-contiguous:", t.flags["C_CONTIGUOUS"])
print("t F-contiguous:", t.flags["F_CONTIGUOUS"])
```

A common outcome is:

```text
a shape: (3, 4)
t shape: (4, 3)
shares memory: True
```

The transpose often creates a view by changing shape and stride metadata.

## Why a cheap transpose can have an expensive downstream effect

The array may become non-contiguous:

```text
contiguous input
      ↓
transpose
      ↓
non-contiguous view
      ↓
downstream library expects contiguous storage
      ↓
possible hidden copy
```

So:

> **Cheap view creation does not guarantee cheap downstream computation.**

A transpose is a useful example of why memory behavior must be considered across API boundaries, not only inside NumPy.

---

# 12. `ravel`

Use:

```python
np.ravel(a)
```

to obtain a one-dimensional representation.

`ravel` **can return a view when possible**.

Example:

```python
import numpy as np

a = np.arange(12).reshape(3, 4)
r = np.ravel(a)

print("shape:", r.shape)
print("shares memory:", np.shares_memory(a, r))
```

A contiguous input will commonly allow a shared-memory result.

For a non-contiguous layout, `ravel` may allocate a copy.

## `ravel` versus `flatten`

```text
np.ravel(a)
→ view when possible
→ copy when necessary

a.flatten()
→ independent 1-D copy
```

This is not a stylistic difference.

It is an ownership and memory decision.

---

# 13. `view(dtype)`: reinterpret bytes

This is one of the most advanced view operations in the chapter.

```python
a.view(new_dtype)
```

changes how existing bytes are interpreted.

It does **not** mean:

> "Convert these numeric values to another dtype."

That is the job of `astype`.

Consider a simple byte-level example:

```python
import numpy as np

a = np.array([1, 2, 3], dtype=np.uint32)
raw = a.view(np.uint8)

print("a:", a)
print("a dtype:", a.dtype)
print("raw dtype:", raw.dtype)
print("raw shape:", raw.shape)
print("shares memory:", np.shares_memory(a, raw))
```

A `uint32` uses 4 bytes per element, so three elements occupy 12 bytes. A `uint8` view sees those same 12 bytes as twelve one-byte elements.

The exact displayed byte values depend on byte order, but memory sharing is the key point:

```text
same bytes
+
different dtype interpretation
=
dtype view
```

## Why this is powerful

This is useful in low-level binary processing, protocol parsing, and interoperability.

It is also dangerous because you are not converting values.

You are reinterpreting bytes.

The distinction is:

```text
astype
→ convert numeric representation
→ generally allocates converted storage

view(dtype)
→ reinterpret existing bytes
→ shared storage
```

## Byte-size constraints

Changing dtype interpretation changes the number of elements that fit in the same byte region.

For simple 1-D examples, a `uint32` array of length 3 contains 12 bytes, while viewing it as `uint8` exposes 12 elements.

Trying a dtype with incompatible item-size relationships on dimensions that do not permit the reinterpretation can raise an error.

Never use `view(dtype)` as a substitute for numeric conversion.

---

# 14. Boolean indexing returns copies

Recall the Topic 03 operation:

```python
selected = a[a > threshold]
```

Boolean indexing produces a new selected result.

Example:

```python
import numpy as np

a = np.array([5, 10, 15, 20, 25])
selected = a[a > 12]

print("selected:", selected)
print("shares memory:", np.shares_memory(a, selected))

selected[0] = -1

print("a:", a)
print("selected:", selected)
```

Output:

```text
selected: [15 20 25]
shares memory: False
a: [ 5 10 15 20 25]
selected: [-1 20 25]
```

This independence is good for mutation safety, but the selection has a memory cost.

For a large array:

```text
500 million values
      ↓
boolean selection
      ↓
selected subset allocated
```

The selected data occupies its own storage.

The Boolean mask also consumes memory.

This matters in large ETL and feature-engineering jobs.

---

# 15. Fancy integer indexing returns copies

Integer-array or "fancy" indexing also materializes selected values.

```python
import numpy as np

a = np.arange(10)

selected = a[[1, 4, 7]]

print("selected:", selected)
print("shares memory:", np.shares_memory(a, selected))
```

Output:

```text
selected: [1 4 7]
shares memory: False
```

For matrix data:

```python
import numpy as np

data = np.arange(20).reshape(5, 4)

rows = data[[0, 3, 4]]

print("rows:\n", rows)
print("shares memory:", np.shares_memory(data, rows))
```

The selected rows are independently stored.

## Why this matters

Suppose:

```text
100,000,000 rows
```

and fancy indexing selects 80,000,000 rows.

The operation is no longer a cheap metadata transformation.

It is a large materialization.

That may be exactly what you need, but it should be recognized as an allocation.

---

# 16. `flatten` always copies

`flatten` guarantees an independent one-dimensional result.

```python
import numpy as np

a = np.arange(12).reshape(3, 4)

flat = a.flatten()

print("shares memory:", np.shares_memory(a, flat))
print("owns data:", flat.flags["OWNDATA"])
```

The result is a copy.

Use:

```text
ravel
```

when view semantics are acceptable and you want a one-dimensional representation with copying avoided when possible.

Use:

```text
flatten
```

when independent storage is explicitly desired.

---

# 17. `astype`

`astype` converts values to another dtype.

```python
import numpy as np

a = np.array([1.0, 2.0, 3.0], dtype=np.float64)

b = a.astype(np.float32)

print("a dtype:", a.dtype)
print("b dtype:", b.dtype)
print("shares memory:", np.shares_memory(a, b))
print("a nbytes:", a.nbytes)
print("b nbytes:", b.nbytes)
```

Typical output:

```text
a dtype: float64
b dtype: float32
shares memory: False
a nbytes: 24
b nbytes: 12
```

The new dtype uses a different representation.

## Conversion versus reinterpretation

Compare:

```text
a.astype(np.uint8)
```

with:

```text
a.view(np.uint8)
```

The first asks NumPy:

> "Convert the values to uint8."

The second asks:

> "Interpret the same bytes as uint8."

These operations solve different problems.

## Memory consequences

A dtype conversion can:

- allocate a second full-size array,
- reduce memory if the new dtype is smaller,
- increase memory if the new dtype is larger,
- reduce precision,
- reduce integer range,
- change overflow behavior.

From Topic 01, dtype selection should already be deliberate.

## `copy=False`

Modern NumPy also supports:

```python
b = a.astype(np.float32, copy=False)
```

This means NumPy may avoid copying when possible, but it cannot avoid allocation if an actual conversion is required.

So:

> `copy=False` is not a guarantee that no new storage will ever be needed.

---

# 18. `np.copy`

Use:

```python
np.copy(a)
```

or:

```python
a.copy()
```

when independent storage is part of correctness.

Example:

```python
import numpy as np

source = np.arange(6)
isolated = np.copy(source)

isolated[0] = 999

print("source:", source)
print("isolated:", isolated)
print("shares memory:", np.shares_memory(source, isolated))
```

Output:

```text
source: [0 1 2 3 4 5]
isolated: [999   1   2   3   4   5]
shares memory: False
```

## Why not copy everywhere?

Because a copy has real costs:

```text
copy
→ allocate memory
→ read source bytes
→ write destination bytes
→ potentially stress cache/memory bandwidth
```

Calling `.copy()` on every intermediate result can turn an otherwise efficient pipeline into a memory-heavy one.

Use:

> **Copy when ownership or independence is part of correctness—not automatically.**

---

# 19. Aliasing: the hidden correctness hazard

**Aliasing** means two names or array objects can reach the same underlying data.

This is an important distinction:

```python
a = np.arange(6)
b = a
```

Here `a` and `b` are literally the same array object.

But aliasing can also happen through views:

```python
a = np.arange(6)
b = a[1:5]
```

Now the objects differ, but the data storage overlaps.

Visual:

```text
name A ──┐
         ├──→ same data buffer
name B ──┘
```

## Production bug scenario

Suppose:

```python
def normalize(batch):
    view = batch[:, :3]
    view *= 0.001
    return view
```

A caller might assume the function returns a transformed result.

But the function also mutates the first three columns of `batch`.

That can corrupt:

- raw input data,
- cached data,
- another pipeline stage's input,
- data retained for audit,
- model features reused later.

## Safer API design

If the function must return an isolated result:

```python
def normalize(batch):
    result = batch[:, :3].copy()
    result *= 0.001
    return result
```

If mutation is intentional, make that contract explicit.

The bug is not "using views."

The bug is **using shared memory without understanding ownership and mutation**.

---

# 20. When should you call `.copy()`?

Use a copy intentionally when one of these is true:

1. You need independent ownership.
2. You will mutate the result and shared mutation is unsafe.
3. You need to protect a source array from downstream modification.
4. You are intentionally breaking an alias.
5. A small returned subset must not keep a huge source allocation alive.
6. A downstream interface requires independent storage for a correctness or lifetime reason.
7. You need a contiguous independent buffer and have decided the allocation is worth it.

Do not copy indiscriminately.

A useful decision:

```text
Will I mutate the result?
        |
        +-- No
        |    |
        |    +-- Is shared storage safe and useful?
        |           |
        |           +-- Yes → use a view when appropriate
        |           +-- No  → copy if isolation/retention requires it
        |
        +-- Yes
             |
             +-- Is shared mutation explicitly safe?
                    |
                    +-- Yes → view/in-place may be appropriate
                    +-- No  → copy
```

Then ask an additional question:

> **Will this result keep a huge source buffer alive?**

If yes, a small copy can be the memory-efficient decision.

---

# 21. Read-only arrays

NumPy arrays can be marked read-only.

```python
import numpy as np

a = np.arange(5)
a.flags.writeable = False

print("writeable:", a.flags.writeable)
```

An attempted mutation:

```python
a[0] = 100
```

raises an error such as:

```text
ValueError: assignment destination is read-only
```

## Why this is valuable

If mutation would be a bug, one useful API design principle is:

> **Make accidental mutation impossible where practical.**

This is particularly useful when:

- shared arrays cross function boundaries,
- multiple pipeline stages consume the same data,
- a cached array should be immutable,
- an input should be treated as read-only,
- you want an early failure instead of silent corruption.

## Read-only views

A view can itself be read-only:

```python
import numpy as np

a = np.arange(6)
view = a[::2]

view.flags.writeable = False

print(view)
print(view.flags.writeable)
print(np.shares_memory(a, view))
```

The view still shares storage, but attempts to write through that view are blocked.

This does not mean the underlying storage is globally immutable. Another writeable alias can potentially still modify the same data.

So read-only state is an important guardrail, not a replacement for ownership reasoning.

---

# 22. NumPy 2 copy semantics

NumPy 2 changed an important edge case around:

```python
np.array(x, copy=False)
```

In current NumPy 2.x, `copy=False` means:

> **Do not copy.**

If satisfying the requested dtype/order/device/etc. would require a copy, NumPy can raise rather than silently copying.

Example:

```python
import numpy as np

data = [1, 2, 3]

try:
    array = np.array(data, copy=False)
    print(array)
except ValueError as exc:
    print(type(exc).__name__)
```

The precise exception text can vary by NumPy version, but the engineering point is stable:

```text
copy=False
→ no-copy requirement
→ if the requested representation cannot be produced without copying,
  the call may fail
```

## Why this matters for old code

Code written under older assumptions may have treated:

```python
np.array(x, copy=False)
```

as:

> "Please avoid a copy if practical."

That is not the right mental model for NumPy 2.

When you need to normalize an API input to an ndarray while allowing NumPy to choose whether conversion requires a copy, `np.asarray` is often the more natural API.

---

# 23. `np.asarray`

Use:

```python
np.asarray(x)
```

at many API boundaries.

Example:

```python
import numpy as np

def transform(x):
    x = np.asarray(x)
    return x * 2
```

The intent is:

> "Give me an ndarray representation of this input, without copying when the existing array is already compatible."

Examples:

```python
import numpy as np

a = np.arange(5)

b = np.asarray(a)

print("same object:", a is b)
print("shares memory:", np.shares_memory(a, b))
```

Output:

```text
same object: True
shares memory: True
```

For a Python list:

```python
import numpy as np

x = [1, 2, 3]
a = np.asarray(x)

print(type(a).__name__)
```

The list cannot be used as an ndarray without materializing array storage.

## Why this is useful in production APIs

Suppose your function accepts:

- a Python list,
- a tuple,
- a NumPy array,
- another array-like object.

You can normalize the boundary once:

```python
def transform(x):
    x = np.asarray(x)
    ...
```

This avoids unnecessary copying of an already-compatible ndarray.

But do not assume `np.asarray` can never allocate.

It may copy when:

- conversion is required,
- dtype conversion is requested,
- a compatible ndarray representation cannot be returned directly,
- layout requirements force materialization.

---

# 24. In-place operations

In-place operations reuse existing storage where possible.

Examples:

```python
a += 1
a *= 2
```

Compare:

```python
a = a + 1
```

with:

```python
a += 1
```

The first computes a new result and then rebinds the Python name.

The second requests mutation of the existing array.

Visual:

```text
normal operation
input buffer
    ↓
new result buffer

in-place operation
input buffer
    ↓
same buffer updated
```

Example:

```python
import numpy as np

a = np.array([1, 2, 3])

before = a

a += 10

print("a:", a)
print("same object:", a is before)
```

Output:

```text
a: [11 12 13]
same object: True
```

## Why in-place operations can reduce allocation pressure

For a large array:

```text
100 million values
```

avoiding an additional full-size result can be significant.

## But in-place operations have a major trade-off

They mutate.

If another alias shares the buffer:

```python
a = np.arange(5)
b = a[1:4]

a += 10
```

then `b` can observe the mutation.

So:

> **In-place optimization is safe only when the ownership and aliasing contract is understood.**

---

# 25. `out=` and explicit destination storage

Many NumPy ufuncs accept an output array.

For example:

```python
import numpy as np

a = np.array([1.0, 2.0, 3.0])
b = np.array([10.0, 20.0, 30.0])
result = np.empty_like(a)

np.multiply(a, b, out=result)

print(result)
```

Output:

```text
[10. 40. 90.]
```

Compare:

```python
result = a * b
```

with:

```python
result = np.empty_like(a)
np.multiply(a, b, out=result)
```

Both produce a result array, but `out=` gives you explicit control over the destination buffer.

## Reusing a buffer

You can reuse a buffer across repeated operations:

```python
import numpy as np

a = np.arange(5, dtype=np.float64)
buffer = np.empty_like(a)

np.multiply(a, 2.0, out=buffer)
np.add(buffer, 5.0, out=buffer)

print(buffer)
```

Output:

```text
[ 5.  7.  9. 11. 13.]
```

The same destination storage is reused for both transformations.

## Why `out=` matters

It can reduce:

- allocation count,
- temporary arrays,
- memory-bandwidth pressure,
- peak memory.

But `out=` is not magic.

The destination must be compatible with the operation's shape, dtype, casting rules, and overlap requirements.

Not every complicated expression can be converted into one `out=` call.

---

# 26. In-place dtype pitfalls

This is a classic production mistake:

```python
import numpy as np

int_array = np.array([1, 2, 3], dtype=np.int64)

int_array += 0.5
```

This does not simply turn the `int64` array into a float array.

The destination already has dtype `int64`, and an in-place operation must write into that storage under the applicable casting rules.

A floating-point result cannot be safely written into an integer destination without a permitted cast.

NumPy therefore raises a casting error.

The non-in-place expression is different:

```python
import numpy as np

int_array = np.array([1, 2, 3], dtype=np.int64)

result = int_array + 0.5

print(result)
print(result.dtype)
```

Output is a floating-point result with a dtype appropriate for the operation.

The production lesson is:

```text
normal operation
→ may allocate a new array with a new dtype

in-place operation
→ destination dtype remains fixed
→ casting must be permitted
```

---

# 27. Temporary arrays and peak memory

Consider:

```python
result = a * b + c
```

A conceptual execution can look like:

```text
a * b
  ↓
temporary 1

temporary 1 + c
  ↓
result
```

If `a`, `b`, and `c` are all large, `temporary 1` can be another large allocation.

Now consider:

```python
result = (a - a.mean()) / a.std() * 100 + 5
```

There are potentially several full-size intermediates:

```text
a - mean
     ↓
temporary
     ↓
/ std
     ↓
temporary
     ↓
* 100
     ↓
temporary
     ↓
+ 5
     ↓
result
```

Exact allocation behavior depends on implementation details, expression structure, reuse opportunities, and lifetimes, but the important engineering idea is:

> **A mathematically short expression can create a large peak-memory footprint.**

---

# 28. Reducing peak memory

Optimize memory from simple strategies to advanced ones.

## Strategy 1 — Use the smallest safe dtype

If `float32` provides sufficient range and precision:

```python
data = data.astype(np.float32)
```

may cut raw storage relative to `float64`.

Do this only when the reduced precision/range is safe for the application.

## Strategy 2 — Avoid unnecessary copies

Before:

```python
selected = large_array[...].copy()
```

ask whether the copy is needed for ownership, mutation safety, or retention.

If not, a view may be sufficient.

## Strategy 3 — Reduce temporary arrays

Break a computation into steps that reuse buffers rather than creating several full-size arrays.

## Strategy 4 — Use `out=`

```python
np.multiply(a, scale, out=buffer)
```

can write directly into a prepared destination.

## Strategy 5 — Use in-place operations where safe

```python
buffer *= scale
buffer += offset
```

This can be effective for owned work buffers.

## Strategy 6 — Drop references

```python
del temporary
```

This removes a Python reference.

Memory is not automatically freed just because `del` was executed.

The buffer becomes reclaimable when no relevant references remain and the Python/NumPy/allocator/OS layers can release or reuse it.

So:

```text
del name
→ drop one reference

no references remain
→ storage may become reclaimable
```

## Strategy 7 — Chunk the work

Instead of:

```text
10 GB input
→ one full-memory operation
```

process:

```text
10 GB input
→ 100 MB chunk
→ 100 MB chunk
→ ...
```

Chunking reduces peak working memory.

## Strategy 8 — Memory-map large file-backed arrays

If the data is stored in a compatible file format, `memmap` can avoid loading the entire array eagerly.

---

# 29. Measuring memory with `tracemalloc`

Do not optimize memory by intuition alone.

Python provides:

```python
import tracemalloc
```

A simple pattern:

```python
import tracemalloc

tracemalloc.start()

# call the function you want to measure

current, peak = tracemalloc.get_traced_memory()

print("current:", current)
print("peak:", peak)

tracemalloc.stop()
```

A reusable helper:

```python
import tracemalloc


def measure_peak_memory(func, *args, **kwargs):
    tracemalloc.start()
    try:
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        return result, current, peak
    finally:
        tracemalloc.stop()
```

## What `tracemalloc` measures

`tracemalloc` is useful for tracing memory allocations visible to Python's allocation tracing system.

It is excellent for comparing allocation behavior between two Python implementations.

## What it does not mean

Do not interpret:

```python
peak
```

as:

> "This is exactly the operating-system RSS peak of my whole process."

It is not a complete OS-level process-memory monitor.

Native libraries, allocator behavior, memory mappings, and external buffers can make total process memory larger or behave differently.

The engineering rule is:

> **Use `tracemalloc` as one measurement tool, not as a universal definition of process memory.**

For production capacity planning, OS-level/container-level metrics such as RSS and cgroup memory are also relevant.

---

# 30. `sliding_window_view`

Rolling and windowed calculations often tempt engineers to physically construct every window.

NumPy provides:

```python
np.lib.stride_tricks.sliding_window_view
```

which can create an overlapping window representation without first copying every window's values into new storage.

Example:

```python
import numpy as np

a = np.array([1, 2, 3, 4, 5])

windows = np.lib.stride_tricks.sliding_window_view(a, window_shape=3)

print(windows)
print("shape:", windows.shape)
print("shares memory:", np.shares_memory(a, windows))
```

Conceptually the windows are:

```text
[1, 2, 3]
[2, 3, 4]
[3, 4, 5]
```

The representation can reuse the original data through stride metadata.

## Rolling mean

```python
import numpy as np

a = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

windows = np.lib.stride_tricks.sliding_window_view(a, 3)
rolling_mean = windows.mean(axis=-1)

print(rolling_mean)
```

Output:

```text
[2. 3. 4.]
```

The window view itself does not require copying every overlapping window.

But `rolling_mean` is a new output.

This is an important distinction:

```text
window representation
→ may be a view

result of computation on windows
→ may allocate output
```

---

# 31. `sliding_window_view`: avoiding a copy does not make computation free

A view can be memory-efficient while the total computation remains expensive.

Consider a large sequence and a large window.

The logical window array can have many overlapping elements.

For example:

```text
input length = N
window = W

number of windows ≈ N - W + 1
```

Each logical window contains `W` values.

A downstream operation may therefore process approximately:

```text
(N - W + 1) × W
```

logical values.

That can be much larger than `N`.

So remember:

```text
view creation cost
≠
total computation cost
```

For production workloads, compare:

- a stride-based window algorithm,
- a cumulative-sum method where appropriate,
- specialized rolling implementations,
- chunked computation,
- the downstream library implementation.

The goal is not merely to eliminate a copy. The goal is to optimize the complete computation.

---

# 32. Why raw `as_strided` is dangerous

NumPy exposes lower-level stride construction through:

```python
np.lib.stride_tricks.as_strided
```

This lets you construct an array with arbitrary shape and strides.

That power comes with responsibility.

A conceptual view of what you are controlling:

```text
shape
+
strides
+
data pointer
=
memory interpretation
```

If you create an invalid layout, you can produce an array whose logical indices do not correspond to valid source storage.

Problems can include:

- reading outside the intended buffer,
- overlapping writable elements,
- surprising writes,
- invalid memory interpretations,
- undefined or unintuitive behavior.

A bounded example can illustrate the concept without asking you to write unsafe code:

```python
import numpy as np

a = np.arange(5, dtype=np.int64)

safe = np.lib.stride_tricks.as_strided(
    a,
    shape=(3,),
    strides=(a.strides[0],),
)

print(safe)
print(np.shares_memory(a, safe))
```

This happens to describe a valid view because the requested shape stays within the source allocation.

The deeper lesson is:

> **Low-level stride manipulation is powerful precisely because NumPy stops protecting you from many mistakes.**

For common rolling-window use cases, prefer:

```python
np.lib.stride_tricks.sliding_window_view(...)
```

because it expresses the intent and applies safer boundary logic.

---

# 33. Memory-mapped arrays

A memory-mapped array provides file-backed access to array data.

The core object is:

```python
np.memmap
```

For `.npy` files, the easiest interface is often:

```python
np.load(path, mmap_mode="r")
```

The conceptual flow is:

```text
large file on disk
       ↓
memory map
       ↓
OS virtual memory
       ↓
OS page cache / file-backed pages
       ↓
requested pages
       ↓
NumPy computation
```

## Why it helps

A normal load:

```python
a = np.load("large.npy")
```

materializes the array for ordinary in-memory processing.

A memory-mapped load:

```python
a = np.load("large.npy", mmap_mode="r")
```

provides an array-like view onto the file-backed data.

The process can access only the pages it actually needs rather than eagerly materializing the entire array into its own anonymous heap allocation.

This makes it useful for datasets larger than comfortable RAM capacity.

---

# 34. Memory mapping is not "free RAM"

Memory mapping does **not** mean the storage device became RAM.

The file still exists on storage.

When a page is accessed:

- the CPU encounters a virtual-memory access,
- the OS may find the page in memory already,
- or it may need to fetch the page from storage,
- page faults and I/O have costs,
- frequently reused pages can benefit from the OS page cache.

Therefore:

```text
memmap
≠
all data is already in RAM
```

Random access can still be expensive.

Sequential access is often much friendlier to file-backed data.

A useful production principle is:

> **Memory mapping controls how data is brought into the process address space; it does not eliminate the cost of storage access.**

---

# 35. `np.load(..., mmap_mode="r")`

For a large `.npy` file:

```python
import numpy as np

data = np.load("sensor_values.npy", mmap_mode="r")

print(type(data))
print(data.shape)
print(data.dtype)
```

You can then process ranges:

```python
chunk_size = 1_000_000

for start in range(0, data.shape[0], chunk_size):
    stop = min(start + chunk_size, data.shape[0])
    chunk = data[start:stop]

    # Process one manageable chunk.
    chunk_mean = chunk.mean()
```

The exact memory behavior of a downstream operation on the chunk still matters.

For example:

```python
chunk = data[start:stop]
```

is a view-like slicing operation on the mapped array, but:

```python
selected = chunk[chunk > 0]
```

creates a selected result.

Memory mapping solves one problem:

> avoiding eager full-file materialization.

It does not make every subsequent operation allocation-free.

---

# 36. Chunked processing with memory-mapped data

A production-style aggregation pattern is:

```python
import numpy as np


def summarize_memmap(data, chunk_size=1_000_000):
    total = 0.0
    count = 0
    minimum = np.inf
    maximum = -np.inf

    for start in range(0, data.shape[0], chunk_size):
        stop = min(start + chunk_size, data.shape[0])
        chunk = data[start:stop]

        total += float(chunk.sum())
        count += chunk.size
        minimum = min(minimum, float(chunk.min()))
        maximum = max(maximum, float(chunk.max()))

    mean = total / count
    return count, mean, minimum, maximum
```

The key point is not the exact implementation. It is the memory model:

```text
large file
→ map
→ one chunk
→ aggregation state
→ next chunk
→ ...
```

The working set stays bounded by the chunk plus the small aggregation state.

For numerical quality, choose accumulation dtypes deliberately when the input range and precision require it.

---

# 37. `.npy`, `.npz`, and CSV

Three common storage choices have very different properties.

## `.npy`

`.npy` is NumPy's native array serialization format.

It stores array metadata such as:

- dtype,
- shape,
- array contents.

Advantages include:

- efficient numeric loading,
- direct interoperability with NumPy,
- preserved dtype and shape,
- support for memory mapping of suitable arrays.

Example:

```python
import numpy as np

a = np.arange(10, dtype=np.int32)

np.save("values.npy", a)

loaded = np.load("values.npy", allow_pickle=False)

print(loaded)
print(loaded.dtype)
```

## `.npz`

`.npz` is an archive containing multiple NumPy arrays.

Example:

```python
import numpy as np

features = np.arange(6, dtype=np.float32)
labels = np.array([0, 1, 0], dtype=np.int8)

np.savez("dataset.npz", features=features, labels=labels)

loaded = np.load("dataset.npz", allow_pickle=False)

print(loaded["features"])
print(loaded["labels"])
```

It is convenient when several arrays belong together.

## CSV

CSV is text-oriented and human-readable.

It is useful when:

- interoperability with simple systems matters,
- humans need to inspect the data,
- the pipeline source or contract is naturally textual.

For dense numeric arrays, CSV is usually:

- larger on disk,
- slower to parse,
- more expensive to convert into binary numeric representations,
- less explicit about dtype.

But:

> **CSV is not universally bad.**

It is often the correct interchange format for simple, human-oriented workflows.

The engineering question is what storage and interchange guarantees the workload requires.

| Format | Main strength | Main trade-off | Typical use |
|---|---|---|---|
| `.npy` | Fast NumPy-native numeric storage | NumPy-centric | Intermediate arrays, experiments, batch numeric jobs |
| `.npz` | Multiple arrays in one archive | Archive overhead and less direct random access per array | Small groups of related arrays |
| CSV | Simple and human-readable | Parsing, size, dtype ambiguity | Interchange and simple tabular exports |

---

# 38. `np.save` and `np.load`

Basic persistence:

```python
import numpy as np

a = np.array([1.5, 2.5, 3.5], dtype=np.float32)

np.save("values.npy", a)

loaded = np.load("values.npy", allow_pickle=False)

print("equal:", np.array_equal(a, loaded))
print("dtype preserved:", a.dtype == loaded.dtype)
```

Output:

```text
equal: True
dtype preserved: True
```

## Why `allow_pickle=False` matters

NumPy object arrays can use Python pickle serialization.

Pickle is a general code-capable serialization mechanism and should not be treated as safe for untrusted input.

For ordinary numeric arrays, use:

```python
np.load(path, allow_pickle=False)
```

as a security-conscious default.

The rule is:

> **Do not enable pickle merely to make an unfamiliar file load.**

If an application genuinely requires object arrays, make the trust boundary explicit and understand the security implications.

---

# 39. Contiguity

A contiguous array has a memory layout that lets a consumer traverse its elements according to a consistent stride pattern without jumping through unrelated regions.

NumPy commonly distinguishes:

- **C-contiguous**,
- **Fortran-contiguous**,
- non-contiguous layouts.

Inspect flags:

```python
import numpy as np

a = np.arange(12).reshape(3, 4)
t = a.T

print("a C:", a.flags["C_CONTIGUOUS"])
print("a F:", a.flags["F_CONTIGUOUS"])

print("t C:", t.flags["C_CONTIGUOUS"])
print("t F:", t.flags["F_CONTIGUOUS"])
```

A typical result is:

```text
a C: True
a F: False
t C: False
t F: True
```

The exact flag combination depends on the shape and construction, but transpose commonly turns a C-contiguous array into a Fortran-contiguous view.

## Simple mental picture

Contiguous:

```text
logical order:
A B C D E F G H

memory:
[A][B][C][D][E][F][G][H]
```

Non-contiguous view:

```text
logical order:
A C E G

memory access:
[A] -> skip -> [C] -> skip -> [E] -> skip -> [G]
```

This does not make the logical result invalid.

It changes how the CPU reaches the values.

---

# 40. Non-contiguous views can be slower

Non-contiguous access can reduce memory locality.

CPU caches are most effective when access patterns exhibit useful spatial locality.

A stride-heavy pattern can force the CPU to fetch memory that is not adjacent in the way the computation expects.

But avoid the blanket claim:

> "Non-contiguous arrays are always slow."

That is inaccurate.

Performance depends on:

- the operation,
- access pattern,
- array shape,
- stride size,
- CPU cache behavior,
- implementation,
- downstream library,
- whether the library copies first.

Sometimes a non-contiguous view is entirely adequate.

Measure before deciding to materialize a contiguous copy.

---

# 41. `np.ascontiguousarray`

Use:

```python
np.ascontiguousarray(a)
```

when a C-contiguous representation is an explicit requirement.

Example:

```python
import numpy as np

a = np.arange(12).reshape(3, 4)
t = a.T

contiguous = np.ascontiguousarray(t)

print("t C-contiguous:", t.flags["C_CONTIGUOUS"])
print("contiguous C-contiguous:", contiguous.flags["C_CONTIGUOUS"])
print("shares memory:", np.shares_memory(t, contiguous))
```

Because `t` is typically non-C-contiguous, the operation generally needs a copy.

When input is already C-contiguous:

```python
a = np.arange(12).reshape(3, 4)
same_layout = np.ascontiguousarray(a)

print(same_layout is a)
print(np.shares_memory(a, same_layout))
```

An already suitable array can often be returned without a copy.

## Why this matters

A deliberate copy can be better than an invisible copy because it makes memory behavior explicit.

For a very large array:

```text
non-contiguous input
→ explicit ascontiguousarray
→ known one-time allocation
```

can be preferable to:

```text
non-contiguous input
→ library silently copies
→ engineer does not know why peak memory increased
```

---

# 42. Hidden library copies

Real data-engineering systems use libraries beyond NumPy.

A common interoperability pattern is:

```text
non-contiguous NumPy array
        ↓
library requires contiguous input
        ↓
library makes a copy
        ↓
peak memory increases
```

Not every library behaves this way.

The contract depends on the library, API, dtype, layout, and native backend.

Before passing a huge array across an API boundary, inspect:

```python
array.dtype
array.shape
array.strides
array.flags
```

and, when relevant:

```python
np.shares_memory(...)
```

## Practical example

Suppose you transpose a matrix:

```python
matrix_for_model = matrix.T
```

The transpose may be a cheap view.

But if a downstream native routine expects C-contiguous data, it may materialize a contiguous copy internally.

The result:

```text
visible NumPy allocation
+
hidden downstream allocation
=
higher peak memory
```

This is why memory engineering must include the whole pipeline.

---

# 43. Zero-copy interoperability

**Zero-copy** means another component can use the same underlying data representation without allocating another full buffer.

Conceptually:

```text
Component A
    ↓
shared buffer
    ↑
Component B
```

Instead of:

```text
Component A
    ↓
copy
    ↓
Component B
```

Benefits can include:

- lower latency,
- lower memory consumption,
- less memory bandwidth pressure,
- fewer opportunities for large temporary allocations.

But zero-copy is conditional.

The consumer must be able to accept the producer's:

- dtype,
- shape,
- layout,
- lifetime,
- ownership model,
- supported memory representation.

## Why this matters in the data ecosystem

This concept appears around:

- pandas,
- Apache Arrow,
- Polars,
- PyTorch,
- native extension APIs.

Do not assume every combination is zero-copy.

For example, a library might share the buffer for one numeric dtype and copy for another, or share only when layout constraints are satisfied.

The engineering goal is:

> **Preserve zero-copy opportunities where they are supported and useful, but verify the actual contract.**

---

# 44. Python buffer protocol

The Python buffer protocol provides a standard way for objects to expose raw memory to other Python components.

Conceptually:

```text
producer
→ exposes memory buffer
→ consumer requests a buffer view
→ consumer can read/write according to the contract
```

This can make copies unnecessary.

Common memory-exporting objects include:

- `bytes`,
- `bytearray`,
- memory views,
- some native-backed arrays.

You do not need to implement a custom buffer exporter for this chapter.

What matters is the system-design idea:

> **A memory-sharing protocol allows components to exchange data by reference to existing storage rather than by serializing and copying all bytes.**

This is one of the conceptual foundations behind efficient Python/native interoperability.

---

# 45. `__array_interface__`

NumPy arrays expose metadata through:

```python
a.__array_interface__
```

Example:

```python
import numpy as np

a = np.arange(6, dtype=np.float32).reshape(2, 3)

info = a.__array_interface__

print("shape:", info["shape"])
print("strides:", info["strides"])
print("typestr:", info["typestr"])
print("data:", info["data"])
```

The metadata describes aspects such as:

- shape,
- strides,
- type string,
- data pointer metadata.

This is useful for understanding how array memory can be described to compatible consumers.

Do not treat `__array_interface__` as the only interoperability mechanism.

Modern ecosystems also use:

- the buffer protocol,
- Arrow interfaces,
- DLPack,
- library-specific protocols.

The key lesson is the abstraction:

```text
memory address
+
shape
+
dtype/format
+
strides
=
enough metadata to describe how a consumer can interpret the data
```

---

# 46. NumPy's practical limits

NumPy is extremely powerful for dense numerical arrays.

It is not designed to be every possible data-engineering engine.

The roadmap highlights several practical limits.

## Mostly in-memory computation

A NumPy array normally represents a logical dataset that is expected to be accessed as an array in memory.

Memory mapping and chunking extend this model, but the core abstraction is still a dense numerical array.

## Execution model is not a distributed data engine

NumPy does not provide a distributed cluster execution model comparable to Spark.

It can use optimized native kernels, and some operations/backends can involve multithreading, but you should not reduce NumPy's execution behavior to the inaccurate statement:

> "NumPy can never use multiple CPU cores."

The more accurate statement is:

> **Parallelism depends on the operation and the underlying implementation; NumPy itself is not a general distributed execution framework.**

## Nullability is not NumPy's strongest model

NumPy has tools for:

- NaN,
- NaT,
- masks,
- masked arrays.

But modern columnar systems provide explicit validity representations and richer nullable semantics that are often better suited to analytics pipelines with heterogeneous columns.

## Strings are not NumPy's strongest analytics representation

NumPy can represent strings, including modern string support, but large-scale string analytics are generally better served by specialized dataframe and columnar systems.

## Distributed processing is outside NumPy's core purpose

Once the dataset and workload demand:

- distributed execution,
- sophisticated query optimization,
- large-scale joins,
- columnar storage,
- predicate pushdown,
- SQL planning,
- cluster scheduling,

other systems become valuable.

---

# 47. Why Arrow, Polars, DuckDB, and Spark exist

These technologies address different limitations.

```text
NumPy
→ dense numerical arrays
→ excellent low-level numerical foundation
```

Then:

```text
Arrow
→ columnar memory format + interoperability

Polars
→ dataframe execution + columnar engine + parallel query execution

DuckDB
→ analytical SQL engine optimized for local analytical workloads

Spark
→ distributed data processing and cluster-scale execution
```

This is not an argument against NumPy.

The correct message is:

> **NumPy is extremely powerful for dense numerical arrays, but production Data Engineering often requires different execution and storage models.**

---

# 48. Debugging views, copies, and memory problems

For memory-sensitive NumPy bugs, use a consistent pattern:

```text
Symptom
→ Root cause
→ How to inspect
→ Correct code
→ Prevention rule
```

## Bug 1 — Slice mutation modifies source

### Symptom

Raw input changes after a transformation.

### Broken example

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50])

view = a[1:5]
view[...] = 0

print(a)
```

Output:

```text
[10  0  0  0  0]
```

### Root cause

The slice is a view.

### Inspect

```python
print(np.shares_memory(a, view))
```

### Correct approach

When independent mutation is required:

```python
copy = a[1:5].copy()
copy[...] = 0
```

### Prevention rule

Before mutating a derived array, know whether it shares the source buffer.

---

## Bug 2 — Boolean selection unexpectedly increases memory

### Symptom

Memory jumps after filtering a large array.

### Example

```python
selected = data[data > threshold]
```

### Root cause

Boolean indexing materializes selected values in a new array.

### Inspect

```python
print(selected.nbytes)
print(np.shares_memory(data, selected))
```

### Correct approach

If selection is genuinely required, account for the allocation.

If possible, restructure the computation to reduce the size or number of materialized intermediates.

### Prevention rule

Treat Boolean selection as a potentially large allocation.

---

## Bug 3 — Tiny view keeps a huge array alive

### Symptom

A function returns a tiny result, but process memory does not fall as expected.

### Example

```python
def first_values(data):
    return data[:10]
```

### Root cause

The returned view can retain the original buffer.

### Inspect

```python
result = first_values(data)

print(result.nbytes)
print(np.shares_memory(data, result))
```

### Correct approach

When the result should outlive the parent and is tiny relative to it:

```python
def first_values(data):
    return data[:10].copy()
```

### Prevention rule

Consider dataset lifetime, not just result size.

---

## Bug 4 — `reshape` unexpectedly copies

### Symptom

A shape change creates more memory than expected.

### Root cause

The source layout does not allow the requested reshape as a view.

### Inspect

```python
reshaped = source.reshape(new_shape)

print(np.shares_memory(source, reshaped))
print(source.strides)
print(reshaped.strides)
```

### Correct approach

If necessary, decide whether an explicit contiguous representation is preferable:

```python
contiguous = np.ascontiguousarray(source)
reshaped = contiguous.reshape(new_shape)
```

### Prevention rule

Treat `reshape` as "view when possible," not "always a view."

---

## Bug 5 — Transpose creates a non-contiguous array

### Symptom

A downstream operation is slower or uses extra memory.

### Inspect

```python
transposed = data.T

print(transposed.flags)
print(transposed.strides)
```

### Root cause

Transpose changes axis order and typically produces a non-C-contiguous view.

### Correct approach

Only materialize a contiguous copy when the downstream operation benefits from or requires it:

```python
contiguous = np.ascontiguousarray(transposed)
```

### Prevention rule

Separate "view creation is cheap" from "all future operations are cheap."

---

## Bug 6 — Downstream library triggers hidden copy

### Symptom

Peak memory increases during a function call that appears not to allocate a large NumPy result.

### Root cause

A consumer may require a particular dtype or contiguous layout and copy internally.

### Inspect

Before the call:

```python
print(data.dtype)
print(data.strides)
print(data.flags)
```

### Correct approach

Meet the library's documented contract explicitly when appropriate:

```python
data_for_consumer = np.ascontiguousarray(data)
```

### Prevention rule

Treat library boundaries as potential allocation boundaries.

---

## Bug 7 — `int_array += 0.5`

### Symptom

An in-place floating-point update raises a casting error.

### Root cause

The integer destination cannot accept the floating result under the allowed in-place casting rules.

### Correct approach

Use a floating destination:

```python
import numpy as np

int_array = np.array([1, 2, 3], dtype=np.int64)
result = int_array.astype(np.float64)
result += 0.5

print(result)
```

### Prevention rule

In-place operations preserve the existing storage contract, including dtype.

---

## Bug 8 — `np.array(copy=False)` assumptions fail in NumPy 2

### Symptom

Code that used to "just work" now raises a `ValueError`.

### Root cause

NumPy 2 treats `copy=False` as a no-copy requirement.

### Correct approach

Use `np.asarray` when the intent is:

```text
give me an ndarray
→ avoid copying if already compatible
→ allow conversion when necessary
```

### Prevention rule

Use APIs according to their current semantic contract, not an old approximation.

---

## Bug 9 — Large expression produces high peak memory

### Symptom

The final result fits in memory, but the job still exceeds its memory limit.

### Example

```python
result = (a - a.mean()) / a.std() * 100 + 5
```

### Root cause

Intermediate results can coexist during evaluation.

### Inspect

Measure:

```python
import tracemalloc
```

and compare alternative implementations.

### Correct approach

Use reusable buffers and in-place operations where safe.

### Prevention rule

Optimize for peak live storage, not just final output size.

---

## Bug 10 — Unsafe stride trick

### Symptom

Unexpected values, overlapping writes, or unsafe behavior.

### Root cause

Manual shape/stride construction can describe memory outside the intended allocation.

### Correct approach

Use `sliding_window_view` for common rolling-window use cases.

### Prevention rule

Do not use `as_strided` casually. Treat it as a low-level systems primitive.

---

## Bug 11 — Treating memmap as ordinary RAM

### Symptom

A memory-mapped computation becomes unexpectedly slow.

### Root cause

Pages may need to be fetched from storage, and random access can cause expensive page faults.

### Correct approach

Prefer sequential or locality-friendly access patterns and process data in chunks.

### Prevention rule

A memory map changes the loading model; it does not change disk latency into RAM latency.

---

# 49. Peak-memory optimization: a measurable exercise

The roadmap requires a real optimization target:

> **Reduce peak memory of one pipeline by at least 40% through measured optimization.**

This is a learning benchmark, not a universal production requirement.

The process must be evidence-based:

```text
1. Implement straightforward version
2. Measure peak memory
3. Identify temporary arrays
4. Reduce unnecessary allocations
5. Measure again
6. Calculate improvement
7. Verify numerical correctness
```

Use:

```text
reduction_percent
=
(peak_before - peak_after)
/
peak_before
× 100
```

Do not claim success without measurements.

---

# 50. Hands-on exercise — `memory_tuning.py`

> **Important safety constraint:** Adjust the dataset size to your available RAM. The goal is to work with a dataset that is larger than is comfortable to load fully, but **do not intentionally destabilize the machine**.

The exercise specification belongs in this chapter. Create the actual `memory_tuning.py` file in your project when you begin the exercise; this chapter does not create it for you.

## Exercise objectives

You will combine:

- `.npy` storage,
- memory mapping,
- chunked processing,
- rolling windows,
- `out=`,
- in-place operations,
- `tracemalloc`,
- mutation-safety testing.

---

## Task 1 — Create a large `.npy` dataset

Create a sufficiently large `float32` dataset and save it with:

```python
np.save(...)
```

A reference pattern:

```python
from pathlib import Path

import numpy as np


path = Path("large_dataset.npy")

rng = np.random.default_rng(2026)

# Choose a safe size for your machine.
data = rng.standard_normal(10_000_000).astype(np.float32)

np.save(path, data, allow_pickle=False)

print(path)
print(data.shape)
print(data.dtype)
print(data.nbytes)
```

For a production-style exercise, scale the row count until loading the full array is uncomfortable but still safe.

A roughly 2 GiB `float32` array contains approximately:

```text
2 GiB / 4 bytes
≈ 536,870,912 elements
```

That is intentionally large and may not be appropriate for every learner's machine.

Your exercise should adapt the size.

---

## Task 2 — Memory-map the dataset

Load the `.npy` using:

```python
data = np.load(path, mmap_mode="r", allow_pickle=False)
```

Then compute:

- global mean,
- global minimum,
- global maximum,
- count,

without eagerly loading the full array into ordinary in-memory storage.

A useful observation:

```python
print(type(data).__name__)
print(data.shape)
print(data.dtype)
print(data.flags)
```

Verify that your code is working on a memory-mapped representation.

---

## Task 3 — Chunked aggregation

Process the mapped array in chunks.

Maintain:

```text
count
sum
min
max
```

Reference structure:

```python
import numpy as np


def summarize(data: np.ndarray, chunk_size: int) -> tuple[int, float, float, float]:
    total_sum = 0.0
    total_count = 0
    minimum = np.inf
    maximum = -np.inf

    for start in range(0, data.shape[0], chunk_size):
        stop = min(start + chunk_size, data.shape[0])
        chunk = data[start:stop]

        total_sum += float(chunk.sum())
        total_count += chunk.size
        minimum = min(minimum, float(chunk.min()))
        maximum = max(maximum, float(chunk.max()))

    mean = total_sum / total_count
    return total_count, mean, minimum, maximum
```

Your final mean is:

```text
total_sum / total_count
```

### What to reason about

Ask:

```text
How large is one chunk?
How many bytes does it contain?
What other arrays are simultaneously live?
Does the memory map itself represent the entire file in physical RAM?
```

---

## Task 4 — 60-sample rolling window

Use:

```python
np.lib.stride_tricks.sliding_window_view
```

on one manageable chunk.

For:

```python
window_size = 60
```

compute a 60-sample rolling mean.

Example:

```python
import numpy as np

chunk = np.arange(100, dtype=np.float32)

windows = np.lib.stride_tricks.sliding_window_view(
    chunk,
    window_shape=60,
)

rolling_mean = windows.mean(axis=-1)

print("chunk shape:", chunk.shape)
print("window shape:", windows.shape)
print("result shape:", rolling_mean.shape)
```

For a one-dimensional input of length `100`, the logical window shape is:

```text
(41, 60)
```

and the rolling result shape is:

```text
(41,)
```

Your task is to explain why:

- the window representation can share memory,
- every logical window overlaps the previous one,
- the mean output is still a real computed result,
- the computational workload grows with the window size.

---

## Task 5 — Temporary-memory optimization

Start from:

```python
result = (a - a.mean()) / a.std() * 100 + 5
```

Measure its peak memory.

Then create a lower-allocation version using some combination of:

- `out=`,
- in-place operations,
- reusable buffers.

A reusable-buffer pattern can look like:

```python
import numpy as np


def optimized_transform(a: np.ndarray) -> np.ndarray:
    result = np.empty_like(a, dtype=np.float64)

    mean = float(a.mean())
    std = float(a.std())

    np.subtract(a, mean, out=result)
    np.divide(result, std, out=result)
    np.multiply(result, 100.0, out=result)
    np.add(result, 5.0, out=result)

    return result
```

Then compare it to the straightforward implementation.

Important:

> An "optimized" version is not automatically better. Measure both memory and runtime and verify the outputs match.

---

## Task 6 — Mutation safety

Write a function that should not modify its input.

A simple test pattern:

```python
import numpy as np


def transform_without_mutating_input(a: np.ndarray) -> np.ndarray:
    # Implement your transformation.
    return a * 2


original = np.arange(10, dtype=np.float64)
before = original.copy()

result = transform_without_mutating_input(original)

np.testing.assert_array_equal(original, before)
```

The test proves:

```text
input before
==
input after
```

Also experiment with:

```python
original.flags.writeable = False
```

and confirm that a function that attempts in-place mutation fails early rather than silently modifying input.

---

# 51. Measuring peak memory in `memory_tuning.py`

A practical helper:

```python
import tracemalloc


def measure_peak_memory(func, *args, **kwargs):
    tracemalloc.start()
    try:
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        return result, current, peak
    finally:
        tracemalloc.stop()
```

Use it to compare:

```text
straightforward implementation
vs
optimized implementation
```

Record:

```text
peak_before
peak_after
reduction_percent
```

For example:

```python
reduction_percent = (
    (peak_before - peak_after)
    / peak_before
    * 100.0
)

print("peak_before:", peak_before)
print("peak_after:", peak_after)
print("reduction_percent:", reduction_percent)
```

### Important measurement caveat

Do not interpret these values as the entire OS process RSS.

`tracemalloc` is most useful here for comparing Python-visible allocation behavior between implementations.

For serious production benchmarking, also inspect:

- process RSS,
- container memory usage,
- native allocations where relevant,
- runtime,
- I/O,
- page-fault behavior for memory mapping.

---

# 52. Required 40% peak-memory reduction benchmark

Your exercise is complete only when you have attempted a genuine measured reduction.

Required workflow:

```text
Straightforward pipeline
        ↓
measure peak memory
        ↓
identify large temporary arrays
        ↓
replace avoidable allocations
        ↓
reuse storage
        ↓
use out= where appropriate
        ↓
use in-place updates where safe
        ↓
re-measure
        ↓
verify correctness
```

Your report should record:

| Metric | Before | After |
|---|---:|---:|
| Peak traced memory | measured | measured |
| Runtime | measured | measured |
| Output correctness | baseline | equivalent |
| Temporary buffers | identified | reduced |
| Peak reduction | — | computed |

The benchmark target is:

```text
reduction_percent >= 40%
```

But a failure to reach 40% is not a failure of the learning process.

The important requirement is:

> **Show the measurements, explain why memory changed, and demonstrate that correctness was preserved.**

A target like 40% is a pedagogical benchmark, not a universal production threshold.

---

# 53. Memory-budget thinking

Before launching a large NumPy computation, estimate the raw data size.

The fundamental calculation is:

```text
elements
×
bytes per element
=
raw array bytes
```

For:

```text
50 million float64 values
```

the raw array size is:

```text
50,000,000 × 8
= 400,000,000 bytes
≈ 381.47 MiB
```

For:

```text
50 million float32 values
```

it is:

```text
50,000,000 × 4
= 200,000,000 bytes
≈ 190.73 MiB
```

So changing dtype from `float64` to `float32` approximately halves the raw storage.

But the full process budget is larger:

```text
input
+
temporaries
+
output
+
Python overhead
+
library/native buffers
+
allocator effects
+
other process memory
```

`array.nbytes` tells you about the array's raw data bytes.

It does not tell you the total process footprint.

---

# 54. Dataset lifetime and memory retention

Memory engineering includes object lifetime.

Imagine:

```text
2 GB source array
      ↓
small slice
      ↓
function returns slice
      ↓
caller retains slice
      ↓
source buffer remains alive
```

The result may have:

```python
result.nbytes
```

of only a few dozen bytes while keeping a multi-gigabyte allocation reachable.

This matters in:

- long-running services,
- batch jobs with many retained objects,
- notebook sessions,
- caches,
- feature stores,
- in-process queues.

## Intentional small copy

Sometimes:

```python
small = huge[:10].copy()
```

is more memory-efficient over the object's lifetime than:

```python
small = huge[:10]
```

because:

```text
copy costs a few bytes now
→ huge parent becomes reclaimable
→ much larger allocation can disappear
```

This is one of the most useful counterintuitive rules in the chapter.

---

# 55. View/copy decision framework

Use this decision tree in code review.

```text
Do I need to modify the result?
        |
        +-- Yes
        |     |
        |     +-- Is shared mutation safe?
        |            |
        |            +-- Yes → view may be appropriate
        |            +-- No  → copy
        |
        +-- No
              |
              +-- Can sharing reduce memory safely?
                     |
                     +-- Yes → view
                     +-- No → copy if ownership/retention requires it
```

Then ask:

```text
Will this small result keep a huge source buffer alive?
```

If yes:

```text
small copy
→ independent ownership
→ parent buffer can be released
```

The right decision depends on the lifetime and ownership contract, not a simplistic "views are good" or "copies are bad" rule.

---

# 56. Prediction-first exercises

For every important operation, predict before executing:

```text
Operation:
Result shape:
View or copy?
Memory owner?
Can modifying it mutate the source?
Contiguous?
Potential hidden allocation?
```

Try these without running them first:

```python
b = a[1:5]
b = a[a > 10]
b = a[[1, 3, 5]]
b = a.reshape(...)
b = a.T
b = np.ravel(a)
b = a.flatten()
b = a.astype(np.float32)
b = a.view(np.uint8)
b = np.ascontiguousarray(a)
```

Then verify with:

```python
b.base
np.shares_memory(a, b)
np.may_share_memory(a, b)
b.flags
```

Remember that not every answer can be predicted from the operation name alone.

Layout matters.

---

# 57. View-versus-copy operation matrix

The following matrix is intentionally phrased carefully. Some NumPy operations have layout-dependent behavior.

| Operation / pattern | Typical behavior | Why | How to verify | Memory implication |
|---|---|---|---|---|
| `a[1:5]` | **View** | Basic slicing changes offset/shape/strides | `np.shares_memory` | Usually no data copy |
| `a[:]` | **View** | Basic slice of all elements | `np.shares_memory` | Usually no data copy |
| `a[::2]` | **View** | Strided slice reuses storage | `np.shares_memory` | No full selection copy; may be non-contiguous |
| `a[:, 1:4]` | **View** | Basic multidimensional slicing | `np.shares_memory` | Cheap creation; source retained |
| `a[1, :]` | **View-like array result** | Basic indexing does not use fancy indexing | `np.shares_memory` | Usually shared storage |
| `a.reshape(...)` | **View when possible; may copy** | Depends on strides/layout/order | `np.shares_memory` | Conditional |
| `a.transpose(...)` | **Usually view** | Reorders axes by metadata/strides | `np.shares_memory` | Often no copy; may become non-contiguous |
| `a.T` | **Usually view** | Shorthand transpose | `np.shares_memory` | Same buffer, changed layout |
| `np.ravel(a)` | **View when possible; may copy** | Depends on layout and requested order | `np.shares_memory` | Conditional |
| `a.view()` | **View** | New array object, same data | `np.shares_memory` | No data copy |
| `a.view(np.uint8)` | **View** | Reinterprets same bytes | `np.shares_memory` | No conversion copy; dtype/item-size changes |
| `a[a > 0]` | **Copy** | Boolean selection materializes values | `np.shares_memory` | Additional selected-data allocation |
| `a[[1, 4, 7]]` | **Copy** | Fancy integer indexing materializes selection | `np.shares_memory` | Additional selected-data allocation |
| `a.flatten()` | **Copy** | Guarantees independent 1-D storage | `np.shares_memory` | Full 1-D copy |
| `a.astype(np.float32)` | **Typically copy** | Values must be converted | `np.shares_memory` | May halve or increase storage depending on dtype |
| `a.astype(a.dtype)` | **May avoid copy depending on arguments/version semantics** | No dtype conversion is needed | `np.shares_memory` | Conditional |
| `a.copy()` | **Copy** | Explicit independent storage | `np.shares_memory` | Full copy |
| `np.copy(a)` | **Copy** | Explicit independent storage | `np.shares_memory` | Full copy |
| `a + b` | **New result** | Arithmetic produces result storage | `a is result` / memory checks | Additional output allocation |
| `np.add(a, b)` | **New result by default** | Ufunc creates result if `out` absent | inspect result | Additional output allocation |
| `np.add(a, b, out=result)` | **Writes destination** | Explicit reuse of supplied buffer | compare `result` identity | Can avoid result allocation |
| `np.multiply(a, b)` | **New result by default** | Ufunc output | inspect result | Additional allocation |
| `np.multiply(a, b, out=result)` | **Writes destination** | Explicit output reuse | compare `result` | Lower allocation pressure |
| `np.concatenate((a, b))` | **Copy / new array** | Values from multiple arrays must be assembled | `np.shares_memory` | New combined storage |
| `np.stack((a, b))` | **New array** | Adds a new axis and materializes result | `np.shares_memory` | New storage |
| `np.repeat(a, repeats)` | **New array** | Values are duplicated | `np.shares_memory` | Can be substantially larger than input |
| `np.tile(a, reps)` | **New array** | Pattern is materialized | `np.shares_memory` | Can multiply memory footprint |
| `np.asarray(a)` | **Same array when already compatible** | Avoids unnecessary conversion/copy | `a is result` | Often zero-copy for ndarray input |
| `np.asarray(list)` | **New array** | List must be represented as ndarray storage | inspect `OWNDATA` | Allocation required |
| `np.array(a)` | **Usually independent array** unless copy can be avoided by options | Constructor semantics | `np.shares_memory` | Can create a copy |
| `np.array(a, copy=False)` | **No-copy requirement in NumPy 2** | Raises if requirements cannot be met without copying | execute / catch error | Avoids silent fallback copying |
| `np.take(a, indices)` | **New selected array** | Selection is materialized | `np.shares_memory` | Allocation proportional to selection |
| `np.ascontiguousarray(a)` | **Original or copy** | Ensures C-contiguous layout | `np.shares_memory` | Copy only when needed |
| `a[...]` | **View-like indexing operation** | Basic indexing | `np.shares_memory` | Usually shared storage |
| `a + scalar` | **New result** | Arithmetic creates output | inspect | Full result allocation |
| `a *= scalar` | **In-place when supported** | Reuses existing destination | `id(a)` and aliases | Lower allocation; mutates |
| `a[:] = value` | **No new result array for assignment itself** | Writes existing storage | inspect source | Mutates target; alias effects possible |
| `np.lib.stride_tricks.sliding_window_view(a, W)` | **View-like overlapping windows** | Uses stride metadata | `np.shares_memory` | Low creation cost; logical output can be large |
| `np.memmap(...)` | **File-backed mapping** | Maps storage into virtual address space | inspect type | Physical pages loaded on demand |
| `np.load(path, mmap_mode="r")` | **Memory-mapped `.npy` access** | File-backed array representation | `type(...)` | Avoids eager full-file materialization |

### Important caveat

The matrix is about typical behavior and common patterns, not a promise that every combination of arguments has identical behavior.

Use:

```python
np.shares_memory
```

to verify actual overlap when correctness depends on it.

---

# 58. Testing strategy for memory-sensitive code

Memory optimization is meaningless if the result becomes numerically wrong.

Tests should verify:

- output correctness,
- input non-mutation,
- intended view/copy behavior,
- chunked versus full-result equivalence,
- memmap result correctness,
- rolling-window correctness,
- dtype preservation,
- shape correctness.

## Integer equality

Use:

```python
np.testing.assert_array_equal(actual, expected)
```

Example:

```python
import numpy as np

expected = np.array([2, 4, 6])
actual = np.array([2, 4, 6])

np.testing.assert_array_equal(actual, expected)
```

## Floating-point comparison

Use:

```python
np.testing.assert_allclose(actual, expected)
```

when floating-point computation can differ by a small rounding error.

Example:

```python
import numpy as np

expected = np.array([1.0, 2.0, 3.0])
actual = expected + 1e-12

np.testing.assert_allclose(actual, expected, rtol=1e-10, atol=1e-12)
```

## Proving non-mutation

The standard pattern is:

```text
save input
→ call function
→ compare current input to saved copy
```

Example:

```python
import numpy as np


def transform(a):
    return a * 2


x = np.arange(5, dtype=np.float64)
before = x.copy()

_ = transform(x)

np.testing.assert_array_equal(x, before)
```

## Testing view/copy contracts

If a function intentionally promises a view:

```python
assert np.shares_memory(source, result)
```

If it intentionally promises isolation:

```python
assert not np.shares_memory(source, result)
```

These tests make the ownership contract executable.

---

# 59. Performance measurement

Keep four different questions separate:

```text
runtime
vs
peak memory
vs
allocation count
vs
I/O cost
```

## Runtime

Use:

```python
import time

start = time.perf_counter()

# operation

elapsed = time.perf_counter() - start
```

`time.perf_counter()` is designed for high-resolution elapsed-time measurement.

## Peak memory

Use:

```python
import tracemalloc
```

when comparing Python-visible allocation behavior.

## Allocation count

Allocation count can matter because repeated allocation can add overhead even when the final memory usage is modest.

## I/O cost

For `memmap` workloads, runtime can be dominated by storage access.

An optimization that reduces memory but creates random I/O may be slower.

Therefore:

> **Do not assume that reducing memory always improves runtime.**

For example:

```text
fewer allocations
→ may improve speed

more chunking
→ may reduce memory
→ may add loop overhead

memory mapping
→ may reduce eager loading
→ may add page-fault / storage latency
```

Measure the real workload.

---

# 60. Production memory-tuning workflow

A reusable production workflow is:

```text
1. Observe
2. Measure
3. Identify allocations
4. Determine ownership and aliasing
5. Reduce unnecessary copies
6. Reuse buffers
7. Choose safe dtypes
8. Chunk when necessary
9. Memory-map when appropriate
10. Re-measure
11. Test correctness
12. Document trade-offs
```

## 1. Observe

Find the operation associated with the memory increase.

## 2. Measure

Measure runtime and memory instead of guessing.

## 3. Identify allocations

Look for:

- Boolean selections,
- fancy indexing,
- `astype`,
- arithmetic chains,
- concatenation,
- stack operations,
- explicit copies,
- hidden library conversions.

## 4. Determine ownership and aliasing

Ask:

```text
Which arrays share the same buffer?
Who can mutate it?
How long is the source allocation kept alive?
```

## 5. Reduce unnecessary copies

Do not remove copies blindly. Preserve correctness contracts.

## 6. Reuse buffers

Use `out=` and preallocated work arrays where appropriate.

## 7. Choose safe dtypes

Reduce raw storage only when numerical correctness permits it.

## 8. Chunk when necessary

Bound the working set.

## 9. Memory-map when appropriate

Use file-backed access for suitable large arrays.

## 10. Re-measure

Confirm the optimization actually changed the relevant metric.

## 11. Test correctness

Numerical equivalence and non-mutation are part of the definition of success.

## 12. Document trade-offs

Explain why a view, copy, chunk size, dtype, or buffer reuse strategy exists.

Optimization without an ownership explanation becomes future technical debt.

---

# 61. Production Data Engineering applications

## ETL transformations

A pipeline can accidentally produce multiple full-size intermediates during numeric transformations.

Memory reasoning helps you:

- fuse operations where appropriate,
- reuse buffers,
- avoid unnecessary copies,
- choose safe dtypes.

## Large file processing

Use:

```text
.npy
+
memmap
+
chunking
```

when the workload is a good fit.

## Feature engineering

Views can reduce memory when features are naturally represented as slices of a larger matrix and ownership is safe.

## ML preprocessing

Large feature matrices can be copied unexpectedly when they cross boundaries between libraries.

Inspect:

- dtype,
- contiguity,
- ownership,
- layout.

## Sensor processing

Rolling operations can use:

```python
sliding_window_view
```

on manageable chunks, with awareness of overlapping-computation cost.

## API and ingestion boundaries

Normalize array-like inputs with:

```python
np.asarray(x)
```

when avoiding unnecessary copies is part of the contract.

## Native and Arrow interoperability

A compatible contiguous buffer may sometimes be consumed without another full copy.

## Container workloads

In containerized data pipelines, peak memory can determine whether the process is killed by the runtime.

A pipeline that "fits" based on final output size can still fail because of its peak live allocations.

---

# 62. Common mistakes

## Mistake 1 — Returning a slice and allowing caller mutation

### Why it happens

The author thinks "slice" means "new data."

### Broken example

```python
def extract(data):
    return data[:100]
```

### Correct approach

Choose intentionally:

```python
return data[:100].copy()
```

when isolation is required.

### Prevention rule

Document mutation expectations.

---

## Mistake 2 — Calling `.copy()` everywhere

### Why it happens

The developer is trying to eliminate aliasing risk.

### Problem

Repeated copies can double or triple working memory.

### Correct approach

Copy at ownership boundaries, not randomly.

### Prevention rule

Every deliberate `.copy()` in a memory-sensitive path should answer:

> "What correctness or lifetime requirement does this copy satisfy?"

---

## Mistake 3 — Loading pickled data from untrusted sources

### Why it happens

The loader fails without pickle support and the developer enables it.

### Correct approach

Use:

```python
np.load(path, allow_pickle=False)
```

for ordinary numeric data.

### Prevention rule

Treat serialized input as untrusted unless the trust boundary is explicit.

---

## Mistake 4 — Assuming `reshape` always returns a view

### Why it happens

Contiguous examples work in notebooks.

### Correct approach

Verify:

```python
np.shares_memory(source, reshaped)
```

### Prevention rule

Use "view when possible."

---

## Mistake 5 — Assuming transpose has no performance consequences

### Why it happens

The transpose itself is cheap.

### Problem

A downstream consumer may need contiguous storage.

### Correct approach

Inspect flags and the consumer's contract.

---

## Mistake 6 — Assuming `ravel` always returns a view

### Why it happens

Simple contiguous examples do.

### Correct approach

Treat it as:

```text
view when possible
```

and verify when it matters.

---

## Mistake 7 — Confusing `view(dtype)` with numeric conversion

### Why it happens

Both operations mention dtype.

### Correct approach

Remember:

```text
astype
→ convert values

view(dtype)
→ reinterpret bytes
```

---

## Mistake 8 — In-place operations on shared arrays

### Why it happens

They reduce allocations.

### Problem

Aliases observe the mutation.

### Correct approach

Use in-place updates only when the ownership contract makes mutation safe.

---

## Mistake 9 — Assuming `np.asarray` always avoids copies

### Why it happens

The phrase "without unnecessary copying" is remembered as "never copies."

### Correct approach

Treat `np.asarray` as:

```text
avoid copy when compatible
→ copy when conversion is required
```

---

## Mistake 10 — Misunderstanding NumPy 2 `copy=False`

### Why it happens

Old code assumes it means "prefer no copy."

### Correct approach

In NumPy 2:

```text
copy=False
→ do not copy
→ can raise when no-copy construction is impossible
```

---

## Mistake 11 — Measuring only `.nbytes`

### Why it happens

`.nbytes` is easy to inspect.

### Problem

It excludes:

- other arrays,
- temporary allocations,
- Python/process overhead,
- native allocations,
- mapped-file behavior,
- allocator effects.

### Correct approach

Measure the workload.

---

## Mistake 12 — Treating memmap as equivalent to RAM

### Why it happens

The array feels like an ndarray in Python.

### Problem

Storage access still has latency.

### Correct approach

Design for locality and chunking.

---

## Mistake 13 — Huge `sliding_window_view` output without considering computation

### Why it happens

No-copy representation sounds free.

### Problem

The logical window space can be large.

### Correct approach

Evaluate both memory and total operation count.

---

## Mistake 14 — Using `as_strided` without deep stride knowledge

### Why it happens

It can express sophisticated layouts compactly.

### Problem

Incorrect strides can create unsafe interpretations.

### Correct approach

Prefer `sliding_window_view` for common rolling windows.

---

## Mistake 15 — Ignoring downstream contiguous-layout requirements

### Why it happens

The NumPy array itself works fine.

### Problem

Another library may copy it.

### Correct approach

Inspect the complete data path.

---

## Mistake 16 — Optimizing memory without measurement

### Why it happens

The code "looks" lighter.

### Correct approach

Measure before and after.

---

# 63. Memory-budget drills

## Drill 1

Calculate the raw storage for:

```text
25 million float64 values
```

Formula:

```text
25,000,000 × 8 bytes
```

Then calculate the same dataset in `float32`.

## Drill 2

Suppose:

```text
input = 800 MiB
one temporary = 800 MiB
output = 800 MiB
```

Ignoring other process overhead, the logical live memory could approach approximately:

```text
2.4 GiB
```

Now ask:

> Can the computation reuse one of these buffers safely?

## Drill 3

Suppose a 2 GiB array returns a 100-element slice.

Compare:

```python
small = large[:100]
```

with:

```python
small = large[:100].copy()
```

Which one retains the source buffer?

Which one allows the source allocation to be reclaimed once no other references remain?

---

# 64. Prediction-first verification lab

Use a small deterministic array:

```python
import numpy as np

a = np.arange(24, dtype=np.int64).reshape(6, 4)
```

For each operation, write your prediction before executing:

### Case A

```python
b = a[1:5]
```

Predict:

```text
Result shape:
View/copy:
Shares memory:
Owner:
Contiguity:
Mutation risk:
```

### Case B

```python
b = a[a[:, 0] > 10]
```

### Case C

```python
b = a[[1, 3, 5]]
```

### Case D

```python
b = a.reshape(3, 8)
```

### Case E

```python
b = a.T
```

### Case F

```python
b = np.ravel(a)
```

### Case G

```python
b = a.flatten()
```

### Case H

```python
b = a.astype(np.float32)
```

### Case I

```python
b = a.view(np.uint8)
```

### Case J

```python
b = np.ascontiguousarray(a.T)
```

Then verify:

```python
print("base:", b.base)
print("shares:", np.shares_memory(a, b))
print("may share:", np.may_share_memory(a, b))
print("flags:\n", b.flags)
```

---

# 65. A practical code-review checklist

Before approving memory-sensitive NumPy code, ask:

### Ownership

- Is the returned object allowed to share storage?
- Is mutation allowed?
- Is the source expected to remain unchanged?

### Shape and layout

- What are the strides?
- Is the result contiguous?
- Is a layout conversion likely later?

### Allocations

- Does Boolean/fancy indexing materialize a large subset?
- Does `astype` allocate?
- Are there arithmetic temporaries?
- Could `out=` reuse storage?

### Lifetime

- Could a small view keep a huge array alive?
- When do large references disappear?
- Are caches holding onto old arrays?

### Scaling

- Does the workload fit in RAM?
- Would chunking bound peak memory?
- Would memmap reduce eager loading?
- Does the access pattern suit storage-backed pages?

### Interoperability

- Does the consumer require a specific dtype?
- Does it require C-contiguous input?
- Does it support zero-copy for this layout?

### Evidence

- Did the engineer measure peak memory?
- Did they measure runtime?
- Did they verify correctness after optimization?

---

# 66. Testing the `memory_tuning.py` exercise

Your tests should include at least these properties.

## Property 1 — Correctness

The optimized transformation matches the baseline:

```python
np.testing.assert_allclose(optimized, baseline)
```

## Property 2 — Non-mutation

```python
before = input_array.copy()

_ = function(input_array)

np.testing.assert_array_equal(input_array, before)
```

## Property 3 — View/copy expectation

If a helper is documented to return an independent copy:

```python
assert not np.shares_memory(source, result)
```

If it is documented to return a view:

```python
assert np.shares_memory(source, result)
```

## Property 4 — Chunked equivalence

Compute a small dataset both ways:

```text
full computation
vs
chunked computation
```

and compare results.

## Property 5 — Memmap correctness

Compare:

```text
normal load
vs
memory-mapped load
```

on the same test file.

## Property 6 — Rolling window

Compare a small rolling result against a simple reference implementation.

---

# 67. Runtime versus memory trade-off examples

## More memory, less code

```python
result = (a * scale) + offset
```

This can be concise but may create a temporary.

## More explicit memory management

```python
result = np.empty_like(a)

np.multiply(a, scale, out=result)
np.add(result, offset, out=result)
```

This adds code but gives stronger control over allocation.

## Lower memory, possible extra loop overhead

```python
for chunk in chunks:
    process(chunk)
```

may reduce peak memory but increase Python-level loop overhead.

## Lower retained memory, immediate copy cost

```python
small = huge[:100].copy()
```

spends memory-bandwidth now to potentially free gigabytes later.

Production optimization is therefore a trade-off analysis, not a collection of magic syntax patterns.

---

# 68. Designing safe NumPy APIs

A function signature does not tell the caller whether an array will be mutated.

A robust API design should make the contract clear.

For a read-only transformation:

```python
def normalize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values)
    result = values * 2
    return result
```

For a deliberate in-place operation, a name or documentation should make mutation explicit.

For example:

```python
def scale_in_place(values: np.ndarray, factor: float) -> None:
    values *= factor
```

The caller needs to understand:

```text
This function mutates the array.
```

For an immutable boundary, a defensive copy may be justified:

```python
def isolated_features(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values)
    return values[:, :5].copy()
```

The key principle:

> **Memory ownership is part of an API contract.**

---

# 69. A deeper look at aliasing across pipeline stages

Consider:

```text
raw_data
    ↓
stage_a
    ↓
stage_b
    ↓
feature_builder
```

Suppose `stage_a` creates a view:

```python
working = raw_data[:, :20]
```

Then `stage_b` performs:

```python
working *= 0.001
```

Now:

```text
raw_data
    ↑
    │ shared buffer
    │
working
    ↓
mutation
```

The "working" stage has effectively modified the raw data.

This can break:

- replayability,
- audit trails,
- idempotence,
- debugging,
- data lineage assumptions.

The NumPy rule becomes a Data Engineering rule:

> **Do not mutate shared buffers unless the pipeline contract explicitly permits it.**

---

# 70. Interaction with earlier NumPy topics

The earlier module topics now combine into one engineering model.

## From Topic 01

You know:

```text
dtype
shape
strides
contiguity
memory layout
```

These determine whether views are possible and how expensive accesses can be.

## From Topic 02

You know vectorized operations are efficient, but now add:

```text
vectorization
+
temporary allocation control
```

An elegant vectorized expression can still create unnecessary peak memory.

## From Topic 03

You know:

```text
basic slicing → view
Boolean/fancy indexing → materialized selection
```

Now connect that distinction to memory budgets and aliasing.

## From Topic 04

Aggregations often produce small results, which is useful.

But reductions can also require intermediate working storage depending on the operation.

## From Topic 05

Missing values and validity masks introduce more arrays and therefore more memory planning.

The broader lesson is:

> **A production NumPy pipeline is not merely a sequence of correct formulas. It is a sequence of storage transformations.**

---

# 71. Final checkpoint

Do not move on until you can answer these without looking up the chapter.

## Core requirements

You should be able to:

1. State at least five operations that often return views.
2. State at least five operations that materialize copies.
3. Explain how a view can cause a data-corruption bug.
4. Explain how to prevent that bug.
5. Process a file larger than RAM using memory mapping and chunks.
6. Reduce peak memory and prove the reduction with measurements.
7. Explain at least two practical limitations of NumPy that motivate other engines.

## Self-test questions

### Question 1

What is the difference between:

```python
a is b
```

and:

```python
np.shares_memory(a, b)
```

### Question 2

Why is `.base` useful but insufficient as a universal memory-sharing test?

### Question 3

What is the difference between:

```python
np.shares_memory
```

and:

```python
np.may_share_memory
```

### Question 4

Why can `reshape` sometimes return a copy?

### Question 5

Why is transpose often cheap to create?

### Question 6

Why can `ravel` return a view while `flatten` always copies?

### Question 7

Why is:

```python
a.view(np.uint8)
```

not equivalent to:

```python
a.astype(np.uint8)
```

### Question 8

Why does Boolean indexing allocate?

### Question 9

Why does:

```python
a += 1
```

carry a different correctness risk from:

```python
a = a + 1
```

### Question 10

Why can `out=` reduce peak memory?

### Question 11

Why can:

```python
int_array += 0.5
```

fail?

### Question 12

Why can `del temporary` reduce memory pressure without directly "freeing memory"?

### Question 13

Why can a tiny view retain a huge source array?

### Question 14

Why is `sliding_window_view` memory-efficient when creating overlapping windows?

### Question 15

Why can a rolling-window computation still be expensive even though the window representation does not copy all input data?

### Question 16

Why is raw `as_strided` dangerous?

### Question 17

Why does memory mapping not turn disk into RAM?

### Question 18

When is `.npy` preferable to CSV for a NumPy-heavy pipeline?

### Question 19

Why is:

```python
np.load(path, allow_pickle=False)
```

a useful default?

### Question 20

Why can non-contiguous arrays sometimes trigger hidden library copies?

### Question 21

What does zero-copy mean?

### Question 22

What is the role of the Python buffer protocol?

### Question 23

What does `__array_interface__` describe?

### Question 24

Why do Arrow, Polars, DuckDB, and Spark exist if NumPy is so capable?

### Question 25

Why is peak memory usually more important than final output size for a memory-limited batch job?

Do not immediately reveal the answers. First explain your reasoning in your own words.

---

# 72. Final mental model

Keep this hierarchy in your head:

```text
DATA
 ↓
NDARRAY BUFFER
 ↓
SHAPE + STRIDES + DTYPE
 ↓
VIEW OR COPY?
 ↓
MEMORY OWNERSHIP
 ↓
MUTATION SAFETY
 ↓
CONTIGUITY
 ↓
TEMPORARY ALLOCATIONS
 ↓
PEAK MEMORY
 ↓
IN-PLACE / out=
 ↓
CHUNKING
 ↓
MEMMAP
 ↓
ZERO-COPY INTEROP
 ↓
PRODUCTION SCALABILITY
```

Before creating or transforming a large NumPy array, ask:

```text
1. Will this operation return a view or copy?
2. Does the result share memory with the input?
3. Who owns the underlying buffer?
4. Could mutation affect another stage?
5. Could a small view keep a huge array alive?
6. Could a dtype conversion allocate another full array?
7. How many temporary arrays are created?
8. What is the peak memory?
9. Can I use out= safely?
10. Can I use an in-place operation safely?
11. Would chunking reduce memory?
12. Would memmap help?
13. Is the array contiguous?
14. Could a downstream library copy it?
15. Can zero-copy interoperability be preserved?
16. Have I measured both runtime and peak memory?
17. Have I tested for unintended mutation?
```

This checklist is more valuable than memorizing a list of NumPy methods.

---

# 73. Connection to the next Data Engineering modules

The ideas in this topic lead directly into later parts of the roadmap:

```text
views/copies
→ pandas copy-on-write

validity masks
→ Arrow / Polars / DuckDB

columnar memory
→ Parquet

chunked and memory-mapped processing
→ larger-scale data processing

vectorized numeric batches
→ Arrow-backed execution and pandas UDF patterns

hot loops
→ Numba / Cython

numeric arrays
→ ML / AI feature and embedding pipelines
```

Do not try to master those systems here.

The purpose of this section is to understand why memory semantics at the NumPy level matter in the systems that come later.

---

# 74. Final module integration

The complete module now has a coherent progression:

```text
Topic 01
→ What is the array?

Topic 02
→ How do I compute on it efficiently?

Topic 03
→ How do I select data from it?

Topic 04
→ How do I summarize it?

Topic 05
→ How do I handle missing/invalid data?

Topic 06
→ How do I do all of that without corrupting data
  or exhausting memory?
```

This is the point of the final topic.

NumPy expertise for Data Engineering is not just knowing array syntax.

It is knowing:

```text
what memory exists
+
where it lives
+
who owns it
+
who can mutate it
+
when a copy occurs
+
when a copy is worth paying for
+
what the peak working set is
+
when to reuse storage
+
when to chunk
+
when to memory-map
+
when to preserve contiguity
+
when to demand zero-copy interoperability
+
when NumPy should hand the workload to another engine
```

That is the memory-engineering mindset required for production numeric data processing.
