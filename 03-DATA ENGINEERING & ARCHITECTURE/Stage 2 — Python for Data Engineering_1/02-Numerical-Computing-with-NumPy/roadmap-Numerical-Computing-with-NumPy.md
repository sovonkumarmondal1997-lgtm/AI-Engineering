# Roadmap — Module 2.2: Numerical Computing with NumPy

This is the learning roadmap for the second module of Stage 2, **Python for
Data Engineering**. It tells you **what** to learn about NumPy, **in what
order**, **how** to learn each topic, and **how to prove to yourself** that
you have learned it before you move on.

Why does a data engineer need NumPy, when most daily work happens in pandas,
Polars, Spark, or SQL? Because NumPy is the foundation underneath much of
that stack. A pandas column is backed by a NumPy array (or, increasingly, an
Arrow array). Spark's pandas UDFs hand you NumPy-backed batches.
scikit-learn, PyTorch data loaders, and embedding pipelines all speak NumPy.
When a pandas job is slow, eats all the memory, silently turns integers into
floats, or corrupts data through a view you did not know existed, the
explanation almost always lives at the NumPy level. This module gives you
that level.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain what an `ndarray` is in memory: one contiguous buffer, a dtype,
  a shape, and strides.
- Choose the right **dtype** for a column of data and predict its memory
  cost, overflow limits, and precision loss.
- Replace Python loops with **vectorized** expressions and ufuncs, and
  predict the result shape of any **broadcasting** operation.
- Select data with **basic slicing**, **boolean masks**, and **fancy
  indexing**, and know which of these return a view and which return a copy.
- Compute **aggregations** along the correct **axis** — sums, means,
  percentiles, counts, group-style aggregates — and keep shapes aligned.
- Handle **missing values** correctly: `NaN` for floats, sentinels and masks
  for integers, and the `nan*` function family.
- Control **memory**: views vs copies, in-place operations, `out=`,
  chunking, and memory-mapped files for data larger than RAM.
- Benchmark a pure-Python data transformation against its NumPy version and
  explain the speed-up.

---

## 2. Prerequisites

This module builds on earlier stages and Module 2.1. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Binary, bits, bytes, RAM, cache | Stage 0 — How Computers Work | dtypes are bytes; vectorization is fast because of contiguous memory and CPU caches |
| Lists, mutation, copying, aliasing | Stage 1 — Module 1.2 | Views are aliasing at array scale |
| Big-O time and space complexity | Stage 1 — Module 1.4 | Reasoning about memory and cost of large arrays |
| Generators and memory trade-offs; object model | Stage 1 — Module 1.9 | Why a list of Python ints costs far more than an `int64` array |
| Profiling and measuring before optimizing | Stage 1 — Module 1.10 | Every performance claim in this module must be measured |
| Pytest | Stage 1 — Module 1.7 | Testing numerical code with tolerances |
| Batch processing, OLAP, columnar storage | Stage 2 — Module 2.1 | NumPy is a columnar, in-memory batch engine |

**Tools needed:**

- Python 3.12+ in a `uv` project; add NumPy with `uv add numpy` (NumPy 2.x).
- `pytest` for tests, `timeit` / `time.perf_counter` for benchmarks.
- `tracemalloc` (standard library) for memory measurements.
- A REPL or Jupyter/IPython for exploration — but every exercise's final
  version must be a `.py` script with tests.

---

## 3. How the module is organised

The six topics are grouped into four phases. Work through them **in order**.

```text
Phase A — The Array Itself              (Basics)
  01 ndarray, dtypes, and memory layout

Phase B — Computing and Selecting        (Basics → Intermediate)
  02 Vectorization and broadcasting
  03 Indexing, boolean masks, and fancy indexing

Phase C — Summarising Real, Dirty Data  (Intermediate → Advanced)
  04 Aggregations and axis semantics
  05 NaN, missing values, and sentinels

Phase D — Memory and Performance        (Advanced)
  06 Views, copies, and memory efficiency

Consolidate
  practice-questions.md
  Module mini-project: vectorized data-quality and metrics engine
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06
what    how to   how to  how to    how to   how to do it
an      compute  select  summarise handle   all without
array   on it    from it it        gaps     wasting memory
is
```

Topic 06 is last on purpose. You meet views early (Topic 01 introduces
strides, Topic 03 shows that slicing returns views), but you can only reason
about memory efficiency as a whole once you have seen every operation that
creates or avoids a copy.

---

## 4. Suggested schedule

About **2.5–3 weeks at 8–10 hours per week**.

| Week | Days | Work |
| --- | --- | --- |
| 1 | 1–2 | Topic 01 — ndarray, dtypes, memory layout |
| 1 | 3–5 | Topic 02 — Vectorization and broadcasting |
| 2 | 1–2 | Topic 03 — Indexing, masks, fancy indexing |
| 2 | 3–4 | Topic 04 — Aggregations and axis semantics |
| 2 | 5 | Topic 05 — NaN, missing values, sentinels |
| 3 | 1 | Topic 05 (finish) + Topic 06 — Views, copies, memory |
| 3 | 2 | Topic 06 (finish) |
| 3 | 3 | `practice-questions.md` |
| 3 | 4–5 | Mini-project and module self-assessment |

---

## 5. How to study every topic (the numerical engineering loop)

```text
Read → Predict shape & dtype → Run in REPL → Write the loop version
→ Write the vectorized version → Assert they match → Break it
→ Measure time & memory → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Predict** the output **shape**, **dtype**, and whether the result is a
   **view or a copy** before running anything. This is the single most
   important habit in NumPy. Most NumPy bugs are wrong predictions here.
3. **Run** it in the REPL and inspect `.shape`, `.dtype`, `.strides`,
   `.flags`, and `np.shares_memory(a, b)`.
4. **Write the loop version** in plain Python first, so you know the
   correct answer.
5. **Write the vectorized version.**
6. **Assert they match** with `np.testing.assert_array_equal` (integers)
   or `np.testing.assert_allclose` (floats).
7. **Break it on purpose** — empty arrays, a single element, all `NaN`,
   integer overflow, mismatched shapes.
8. **Measure** with `timeit` and `tracemalloc` on realistic sizes (10⁶ to
   10⁷ elements), not on 10 elements.
9. **Write down** the rule you learned in one sentence in your notes file,
   `module-2.2-notes.md`.
10. **Explain aloud** why the vectorized version is faster or uses less
    memory.

Keep a single `numpy_lab/` `uv` project for every exercise, with
`src/` for code and `tests/` for pytest files.

---

## 6. Phase A — The Array Itself (Basics)

### Topic 01 — [ndarray, dtypes, and memory layout](01-ndarray-dtypes-and-memory-layout.md)

**Why it comes first:** Every later topic — broadcasting, views, NaN rules,
memory efficiency — is a consequence of how an array is laid out in memory.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What an `ndarray` is: a homogeneous, fixed-size, N-dimensional grid of values; attributes `ndim`, `shape`, `size`, `dtype`, `itemsize`, `nbytes` |
| Basics | Creating arrays: `np.array`, `np.asarray`, `np.zeros`, `np.ones`, `np.full`, `np.empty`, `np.arange`, `np.linspace`, `np.random.default_rng()` |
| Basics | Core dtypes: `bool`, `int8`–`int64`, `uint8`–`uint64`, `float16`/`float32`/`float64`, `complex`, `str_` / `bytes_`, `object`, `datetime64`, `timedelta64` |
| Basics | Why a Python `list` of ints is an array of pointers to objects, while an `int64` array is raw 8-byte values side by side |
| Intermediate | Integer ranges and **silent overflow** in arrays (e.g. `np.int8(127) + 1` wraps); choosing the smallest safe dtype |
| Intermediate | Float precision: `float32` vs `float64`, why `0.1 + 0.2 != 0.3`, why money should not be stored as floats (use integer cents or `Decimal` outside NumPy) |
| Intermediate | Casting with `astype`, `casting=` rules (`"safe"`, `"same_kind"`, `"unsafe"`), and NumPy 2 type promotion rules (NEP 50: Python scalars no longer upcast arrays) |
| Intermediate | `datetime64` / `timedelta64` units (`s`, `ms`, `us`, `ns`), arithmetic on timestamps, and why they are time-zone naive |
| Advanced | Memory layout: contiguous buffer, **strides**, C order (row-major) vs Fortran order (column-major), `.flags` (`C_CONTIGUOUS`, `F_CONTIGUOUS`, `OWNDATA`, `WRITEABLE`) |
| Advanced | Why layout matters: cache locality, iterating along the fast axis, and costly copies when a library needs a different order |
| Advanced | Structured arrays (record dtypes) as a row-oriented table, and why columnar arrays (one array per column) usually win for analytics — connecting to OLTP vs OLAP in Module 2.1 |
| Advanced | Strings in NumPy: fixed-width `str_` (`<U10`) truncation risk, `object` arrays of Python strings, and the NumPy 2 variable-width `StringDType` |
| Advanced | Endianness (`<i8` vs `>i8`) and reading raw binary files with `np.fromfile` / `np.frombuffer` |

**How to learn it**

1. Read the topic file.
2. For 15 different arrays, write down `shape`, `dtype`, `nbytes`, and
   `strides` **before** printing them.
3. Draw a 3×4 `int32` array as a strip of 48 bytes, and mark how strides
   `(16, 4)` step through it. Then draw its transpose and its strides
   `(4, 16)`.

**Hands-on exercise — `dtype_planner.py`**

You are loading 50 million order rows. Columns: `order_id` (up to 3
billion), `quantity` (0–500), `unit_price_cents` (up to 10,000,000),
`country_code` (2 letters), `is_gift` (yes/no), `created_at`
(millisecond precision).

1. Choose a dtype for each column and justify it.
2. Compute total memory with your dtypes vs "everything `int64` / `object`".
3. Generate 1,000,000 rows with `default_rng` in both layouts and verify
   your estimates with `nbytes` and `tracemalloc`.
4. Demonstrate one overflow bug you avoided (e.g. `quantity * unit_price`
   in `int32`) and fix it with a deliberate upcast.
5. Write pytest tests that assert the chosen dtypes and memory budget.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain why an `int64` array uses far less memory than a list of
      Python ints.
- [ ] State the range of `int8`, `uint8`, `int32`, and `int64`.
- [ ] Explain what strides are and compute them for a given shape and
      dtype.
- [ ] Explain C vs Fortran order and when it matters.
- [ ] Explain why money should not be stored as `float64`.

**Common mistakes:** using `object` dtype by accident (from mixed input);
ignoring silent integer overflow; storing timestamps as strings; using
`np.empty` and forgetting it contains garbage.

---

## 7. Phase B — Computing and Selecting (Basics → Intermediate)

### Topic 02 — [Vectorization and broadcasting](02-vectorization-and-broadcasting.md)

**Why here:** Once you know what an array is, you learn how to compute on
it without Python loops — the reason NumPy exists.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Vectorization: whole-array expressions (`a * b + c`) executed in compiled loops, not Python bytecode |
| Basics | Universal functions (ufuncs): arithmetic, comparison, `np.sqrt`, `np.exp`, `np.log`, `np.abs`, `np.round`, `np.clip` |
| Basics | Element-wise conditional logic with `np.where`, `np.select`, and `np.clip` instead of `if` inside a loop |
| Intermediate | **Broadcasting rules**: align shapes from the right; each dimension must be equal or 1; missing dimensions are treated as 1 |
| Intermediate | Adding axes with `np.newaxis` / `None` and `reshape` to make broadcasting do what you want (e.g. column-wise normalisation) |
| Intermediate | Common broadcast patterns: centring columns, min-max scaling, pairwise differences, applying per-category rates via lookup arrays |
| Intermediate | Ufunc methods: `reduce`, `accumulate`, `outer`, `at` (e.g. `np.add.at` for unbuffered scatter-add) |
| Advanced | Hidden memory cost of broadcasting: `a[:, None] - b[None, :]` materialises an N×M result; when to chunk instead |
| Advanced | Temporaries: `a * b + c` creates intermediate arrays; reducing them with `out=` and in-place operators (`+=`) |
| Advanced | Why `np.vectorize` and `np.apply_along_axis` are *not* real vectorization (they are loops) |
| Advanced | Floating-point behaviour in vectorized code: `np.errstate` for divide-by-zero and invalid operations; `inf` and `nan` propagation |

**How to learn it**

1. Read the topic file.
2. Write out the broadcasting result shape for 20 shape pairs by hand, e.g.
   `(5, 1, 3)` with `(4, 3)`, then verify with `np.broadcast_shapes`.
3. Convert five loop-based functions from your Stage 1 projects into
   vectorized versions.

**Hands-on exercise — `vectorized_transforms.py`**

Using 5,000,000 generated orders (reuse `dtype_planner.py`):

1. Compute `line_total_cents = quantity * unit_price_cents` — loop vs
   vectorized.
2. Apply a tax rate per country using a lookup array indexed by an integer
   country code (broadcasting + fancy indexing preview).
3. Bucket orders into `small` / `medium` / `large` with `np.select`.
4. Min-max scale a `(n_rows, 4)` matrix of numeric features column-wise
   using broadcasting.
5. Benchmark every loop vs vectorized pair; record speed-ups in a table.
6. Test that loop and vectorized versions return identical results.

**Checkpoint:**

- [ ] State the three broadcasting rules without looking.
- [ ] Predict the result shape of `(8, 1, 6, 1)` combined with `(7, 1, 5)`.
- [ ] Explain why `np.vectorize` is not faster than a loop.
- [ ] Explain how to avoid a huge temporary array in a pairwise
      computation.

**Common mistakes:** accidental broadcasting that silently produces an N×N
result; shape `(n,)` vs `(n, 1)` confusion; assuming `np.vectorize` is
fast.

---

### Topic 03 — [Indexing, boolean masks, and fancy indexing](03-indexing-boolean-masks-and-fancy-indexing.md)

**Why here:** Computation is half of data work; the other half is
*selecting* the right rows — filtering, lookups, reordering, and sampling.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Basic indexing and slicing in N dimensions: `a[i]`, `a[i, j]`, `a[start:stop:step]`, `a[:, 0]`, `a[..., -1]` |
| Basics | Boolean masks: `a[a > 100]`, combining with `&`, `\|`, `~` (and why `and` / `or` fail); parentheses around conditions |
| Basics | Counting and testing masks: `mask.sum()`, `mask.mean()`, `np.any`, `np.all`, `np.count_nonzero` |
| Intermediate | Fancy (integer-array) indexing: `a[[3, 0, 7]]`, lookup tables, reordering rows, `np.take` |
| Intermediate | `np.nonzero`, `np.flatnonzero`, `np.argwhere` — turning masks into positions |
| Intermediate | Sorting and ranking: `np.sort`, `np.argsort` (and `kind="stable"`), `np.lexsort` for multi-key sorts, `np.argpartition` for top-k |
| Intermediate | Set-like operations: `np.unique` (`return_counts`, `return_inverse`), `np.isin`, `np.intersect1d`, `np.setdiff1d` |
| Advanced | **View vs copy rule:** basic slicing returns a view; boolean and fancy indexing always return copies — and assigning through them (`a[mask] = 0`) still modifies the original |
| Advanced | `np.searchsorted` for binning, as-of lookups, and joining sorted keys (a vectorized join) |
| Advanced | Combining fancy indices across axes (`a[rows[:, None], cols]`) and `np.ix_` |
| Advanced | Deduplication and "keep latest record per key" with `argsort` + `unique` — a pattern you will reuse in silver layers |

**How to learn it**

1. Read the topic file.
2. For every indexing expression you write, record: result shape, and view
   or copy. Check with `np.shares_memory`.
3. Re-implement three SQL queries (`WHERE`, `ORDER BY ... LIMIT`,
   `SELECT DISTINCT`) using only NumPy indexing.

**Hands-on exercise — `select_and_dedupe.py`**

Given arrays `order_id`, `customer_id`, `updated_at`, `status_code`,
`amount_cents` (with duplicates — the same order updated several times):

1. Filter paid orders over 10,000 cents in the last 7 days with a combined
   boolean mask.
2. Return the top 100 orders by amount with `argpartition` then sort only
   those 100.
3. Keep only the **latest version of each order** using `lexsort` and
   `np.unique(return_index=True)`.
4. Map `status_code` integers to labels with a lookup array.
5. Assign each order a price band with `np.searchsorted` on band edges.
6. Test every function against a pure-Python reference implementation.

**Checkpoint:**

- [ ] Explain why `a[(a > 1) and (a < 5)]` raises an error and fix it.
- [ ] State which indexing styles return views and which return copies.
- [ ] Explain why `a[mask] = 0` changes `a` even though `a[mask]` is a
      copy.
- [ ] Implement "latest record per key" in NumPy.

**Common mistakes:** chained indexing that assigns to a temporary copy
(`a[mask][0] = 5` does nothing to `a`); unstable sorts in deduplication;
`argsort` on the whole array when `argpartition` is enough.

---

## 8. Phase C — Summarising Real, Dirty Data (Intermediate → Advanced)

### Topic 04 — [Aggregations and axis semantics](04-aggregations-and-axis-semantics.md)

**Why here:** Data engineers produce aggregates — daily totals, percentiles,
per-group counts. Getting the axis wrong is one of the most common silent
bugs in numerical code.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Reductions: `sum`, `mean`, `min`, `max`, `argmin`, `argmax`, `std`, `var`, `prod`, `any`, `all` |
| Basics | The `axis` argument: `axis=0` collapses rows (one result per column), `axis=1` collapses columns (one result per row); `axis=None` reduces everything |
| Basics | `keepdims=True` to keep results broadcast-compatible with the input |
| Intermediate | Percentiles and quantiles: `np.percentile`, `np.quantile`, `np.median`, and the `method=` option (e.g. `"linear"`, `"nearest"`) — p50/p95/p99 latency |
| Intermediate | Cumulative operations: `cumsum`, `cumprod`, `np.diff`, running totals and period-over-period change |
| Intermediate | Group-style aggregation without pandas: `np.bincount` with `weights`, `np.unique(return_inverse=True)` + `np.add.at`, sort-then-`np.add.reduceat` |
| Intermediate | Histograms and binning: `np.histogram`, `np.digitize` |
| Advanced | Numerical accuracy: pairwise summation in `np.sum`, catastrophic cancellation in variance, `ddof=0` vs `ddof=1`, and accumulating in a wider dtype (`dtype=np.float64` / `np.int64` on `sum`) |
| Advanced | Integer overflow in reductions on small dtypes (summing a large `int32` array) |
| Advanced | Correlation and covariance: `np.corrcoef`, `np.cov` for quick data profiling |
| Advanced | Streaming / chunked aggregation: combining partial sums, counts, mins, and maxes across chunks; why mean and variance need care when merging chunks and exact percentiles cannot be merged |

**How to learn it**

1. Read the topic file.
2. Draw a 3×4 matrix and shade what `axis=0` and `axis=1` collapse. Do this
   again for a 3-D array of shape `(days, stores, products)`.
3. For each aggregation you write, predict the result shape first.

**Hands-on exercise — `metrics_engine.py`**

Generate a 3-D array of sales with shape `(365 days, 50 stores, 200
products)`:

1. Total sales per store, per product, per day, and overall (use the right
   axis each time; tuple axes like `axis=(0, 2)` where needed).
2. Each store's share of total sales with `keepdims=True` and
   broadcasting.
3. p50, p95, and p99 of 10,000,000 simulated API latencies.
4. Revenue per customer with `np.bincount(customer_idx, weights=amount)`.
5. Rolling 7-day totals with `cumsum` differencing.
6. Chunked version: process the latencies in chunks of 1,000,000 and
   produce the same count, sum, mean, min, and max as the full version.
7. Test shapes and values against small hand-computed examples.

**Checkpoint:**

- [ ] Predict the result shape of `a.sum(axis=1)` for `a.shape == (4, 5,
      6)`.
- [ ] Explain what `keepdims=True` is for.
- [ ] Compute a per-group sum without a Python loop.
- [ ] Explain why exact percentiles cannot be merged across chunks while
      sums and counts can.

**Common mistakes:** confusing which axis "disappears"; summing small
integer dtypes and overflowing; using `ddof=0` when a sample standard
deviation was intended; averaging per-chunk means without weighting by
count.

---

### Topic 05 — [NaN, missing values, and sentinels](05-nan-missing-values-and-sentinels.md)

**Why here:** Real data is never complete. You must know how NumPy
represents "missing" before pandas and Arrow add their own (different)
rules in Modules 2.3 and 2.4.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `np.nan` as the float missing value; `NaN != NaN`; detect with `np.isnan`, never with `==` |
| Basics | NaN propagation: `np.sum`, `np.mean`, `np.max` return `nan` when any value is `nan` |
| Basics | The `nan*` family: `np.nansum`, `np.nanmean`, `np.nanmedian`, `np.nanpercentile`, `np.nanmax`, `np.nanargmax` |
| Intermediate | **Integers cannot hold NaN** — inserting a missing value forces a cast to `float64` (and loses precision above 2⁵³); this is exactly why pandas historically turned integer columns into floats |
| Intermediate | Sentinel values (`-1`, `0`, `999`, `-9999`) — when they are acceptable and the bugs they cause in aggregations |
| Intermediate | `NaT` for `datetime64` / `timedelta64`; `np.isnat` |
| Intermediate | `inf` and `-inf` vs `nan`; `np.isfinite`, `np.isinf`; `np.nan_to_num` |
| Intermediate | Separate validity masks: a value array plus a boolean `is_valid` array — the design Arrow uses (validity bitmaps) |
| Advanced | `numpy.ma` masked arrays: how they work, their cost, and why most pipelines prefer explicit masks or Arrow |
| Advanced | Imputation strategies: drop, fill with constant, fill with mean/median, forward fill (implemented with `np.maximum.accumulate` on indices) — and when imputation is a data-quality lie |
| Advanced | Missingness reporting: counting missing per column, missing rate thresholds, and failing a pipeline when a rate is exceeded |
| Advanced | NaN in comparisons, sorting (`nan` sorts to the end), `np.unique` behaviour (`equal_nan=True` by default in NumPy 2), and equality testing with `assert_array_equal` / `assert_allclose(equal_nan=True)` |

**How to learn it**

1. Read the topic file.
2. Build a table: for each representation (NaN, sentinel, masked array,
   value + validity mask), list supported dtypes, memory cost, and what
   `sum` / `mean` / `==` do.
3. Take one aggregation from Topic 04 and rewrite it to be NaN-safe.

**Hands-on exercise — `missing_values_report.py`**

Generate sensor readings (`float64` temperature, `int64` device id,
`datetime64[ms]` timestamp) with 3% NaN, 1% `-9999` sentinels, 0.5% `inf`,
and 0.2% `NaT`:

1. Detect and count each kind of problem per column.
2. Convert sentinels to NaN, and `inf` to NaN, into a clean copy.
3. Produce NaN-safe daily mean, min, max, and p95 per device.
4. Store an integer column with missing values two ways — as `float64` with
   NaN and as `int64` + validity mask — and show the precision loss for an
   id above 2⁵³ in the float version.
5. Forward-fill gaps per device without a Python loop.
6. Exit with a non-zero code if any column's missing rate exceeds a
   configured threshold (connecting to SLOs from Module 2.1).

**Checkpoint:**

- [ ] Explain why `np.nan == np.nan` is `False` and how to test for NaN.
- [ ] Explain why an integer column with missing values becomes float, and
      the risk that creates.
- [ ] Choose between NaN, a sentinel, and a validity mask for a given
      column.
- [ ] Compute NaN-safe aggregates and a missingness report.

**Common mistakes:** filtering NaN with `a != np.nan`; treating sentinels
as real values in averages; silently imputing without recording that you
did; losing large integer ids to float conversion.

---

## 9. Phase D — Memory and Performance (Advanced)

### Topic 06 — [Views, copies, and memory efficiency](06-views-copies-and-memory-efficiency.md)

**Why last:** Every earlier topic created views or copies. This topic
turns those scattered facts into a system for writing NumPy code that fits
in memory and does not corrupt data by accident.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | A **view** shares the same buffer with different shape/strides; a **copy** owns new memory; `.base`, `np.shares_memory`, `np.may_share_memory` |
| Basics | Operations that return views: basic slicing, `reshape` (when possible), `.T`, `ravel` (when possible), `.view(dtype)` |
| Basics | Operations that return copies: boolean/fancy indexing, `flatten`, `astype` (by default), `np.copy`, most arithmetic |
| Intermediate | The aliasing bug: modifying a slice changes the original; when to call `.copy()` explicitly, and read-only arrays (`a.flags.writeable = False`) as protection |
| Intermediate | NumPy 2 copy semantics: `np.array(x, copy=False)` raises if a copy is needed; use `np.asarray` when you mean "copy only if necessary" |
| Intermediate | In-place operations: `a += 1`, `np.multiply(a, 2, out=a)`, and in-place dtype pitfalls (`int_array += 0.5` raises a casting error) |
| Intermediate | Reducing peak memory: fewer temporaries, smaller dtypes, `del` + dropping references, processing in chunks |
| Advanced | Stride tricks: `np.lib.stride_tricks.sliding_window_view` for rolling windows without copying — and why the raw `as_strided` is dangerous |
| Advanced | Memory-mapped arrays: `np.memmap` and `np.load(..., mmap_mode="r")` for data larger than RAM; the OS page cache (Stage 0 virtual memory) |
| Advanced | Saving and loading: `.npy` / `.npz` vs CSV; `np.save`, `np.load`, and `allow_pickle=False` for safety |
| Advanced | Contiguity and performance: `np.ascontiguousarray`, why operations on non-contiguous views can be slower, and why some libraries silently copy them |
| Advanced | Zero-copy interop and the buffer protocol / `__array_interface__` — the idea behind handing data between NumPy, pandas, Arrow, and PyTorch without copying (Module 2.4 goes deeper) |
| Advanced | Knowing NumPy's limits: single-threaded for most operations, in-memory only, no native nulls or strings for analytics — the reasons Polars, DuckDB, Arrow, and Spark exist |

**How to learn it**

1. Read the topic file.
2. Build a "view or copy?" table covering at least 25 operations; verify
   each with `np.shares_memory`.
3. Profile peak memory of one pipeline from Topic 04 with `tracemalloc`,
   then reduce it by at least 40%.

**Hands-on exercise — `memory_tuning.py`**

1. Create a 2 GB `float32` `.npy` file of readings on disk (adjust size to
   your machine's RAM so it is larger than comfortable to load).
2. Open it with `mmap_mode="r"` and compute the global mean, min, max, and
   count in chunks — never loading the whole file.
3. Compute a 60-sample rolling mean with `sliding_window_view` on one chunk
   and confirm it allocates no copy of the input window.
4. Rewrite `result = (a - a.mean()) / a.std() * 100 + 5` to minimise
   temporaries using `out=` and in-place operations; measure peak memory
   before and after.
5. Write a test that proves a function does **not** modify its input array
   (compare against a saved copy, or pass a read-only array).

**Checkpoint:**

- [ ] State five operations that return views and five that return copies.
- [ ] Explain how a view can cause a data-corruption bug and how to prevent
      it.
- [ ] Process a file larger than RAM with `memmap` in chunks.
- [ ] Reduce the peak memory of a computation and prove it with
      measurements.
- [ ] Explain two limits of NumPy that motivate columnar engines.

**Common mistakes:** returning a slice from a function and letting the
caller mutate the source; calling `.copy()` everywhere "to be safe" and
doubling memory; loading pickled `.npy` files from untrusted sources.

---

## 10. Consolidate — practice questions

When all six topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Write down the input shapes and dtypes.
2. Predict the output shape, dtype, and whether any step creates a view.
3. Write a pure-Python reference solution for a tiny input.
4. Write the vectorized NumPy solution.
5. Assert both match, including edge cases (empty, single element, all
   NaN, overflow-prone values).
6. Measure time and peak memory on a large input.

Do not look at answers until you have a working, tested attempt.

---

## 11. Module mini-project — vectorized data-quality and metrics engine

This is the proof that you have finished the module.

**Scenario:** A fleet of 2,000 IoT devices sends one reading per minute
(device id, timestamp, temperature, battery level, status code). You
receive a daily `.npy` dump of about 2.9 million rows per column, with
duplicates, late records, NaN, sentinels, and occasional `inf`.

Build `sensor_metrics/`, a `uv` project with:

1. **Loader** — memory-maps the daily files; chooses compact dtypes;
   validates shapes and dtypes on load.
2. **Cleaner** — converts sentinels and `inf` to NaN; deduplicates to the
   latest reading per `(device_id, timestamp)`; quarantines invalid rows
   into a separate file (bronze → silver thinking from Module 2.1).
3. **Metrics** — per-device and per-hour NaN-safe mean, min, max, and p95
   temperature; battery drain per day using `np.diff`; percentage of
   missing readings per device.
4. **Alerts** — devices whose missing rate exceeds 5% or whose temperature
   exceeds a threshold for 10 consecutive minutes (use
   `sliding_window_view`).
5. **Report** — writes metrics to CSV and a `run_metadata.json` with row
   counts, runtime, and peak memory.
6. **Benchmarks** — a pure-Python version of the metrics step, with a table
   comparing runtime and memory to the NumPy version.
7. **Tests** — pytest tests for every function, including NaN, empty, and
   duplicate edge cases, and a test that no function mutates its inputs.

**Grading yourself:** the pipeline runs on a full day of data within your
machine's memory, the NumPy version is at least 20× faster than the
pure-Python version, every test passes, and you can explain every dtype,
axis, and view/copy decision in the code.

---

## 12. Module self-assessment — exit criteria

Only move to Module 2.3 (pandas) when you can tick every box without
looking at your notes:

- [ ] I can explain an array's memory layout (buffer, dtype, shape,
      strides).
- [ ] I can choose dtypes for real columns and predict memory and overflow
      risk.
- [ ] I can predict broadcasting result shapes and vectorize loop code.
- [ ] I can filter, sort, deduplicate, and look up values with masks and
      fancy indexing.
- [ ] I can aggregate along the correct axis, including group-style
      aggregation and percentiles.
- [ ] I can handle NaN, NaT, `inf`, and sentinels correctly.
- [ ] I can predict views vs copies and reduce peak memory.
- [ ] I have finished all practice questions and the mini-project.

---

## 13. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| NumPy official documentation — "NumPy: the absolute basics for beginners" and the User Guide | All topics |
| NumPy docs — "Broadcasting", "Indexing on ndarrays", "Copies and views" | 02, 03, 06 |
| NumPy 2.0 migration guide (NEP 50 promotion, copy semantics, `StringDType`) | 01, 06 |
| *Python for Data Analysis*, 3rd edition — Wes McKinney (O'Reilly), NumPy chapters and appendix on advanced NumPy | 01–06 |
| *From Python to NumPy* — Nicolas P. Rougier (free online book) | 02, 06 |
| *What Every Computer Scientist Should Know About Floating-Point Arithmetic* — David Goldberg | 01, 04 |

---

## 14. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| dtypes, nullable ints, NaN vs sentinels | 2.3 pandas — nullable dtypes, `pd.NA`, categoricals |
| Views vs copies | 2.3 pandas — copy-on-write and chained assignment |
| Validity masks, columnar buffers, zero-copy | 2.4 Arrow, Polars, and DuckDB |
| Columnar vs row-oriented (structured arrays) | 2.5 Data Formats — Parquet internals |
| Chunked and memory-mapped processing | 2.3 chunked processing, 2.21 Performance and Scaling |
| Vectorized UDFs on batches | 2.14 PySpark — pandas UDFs and Arrow |
| Hot loops that cannot be vectorized | 2.21 Performance — Numba and Cython |
| Numeric arrays for features and embeddings | 2.22 Serving Data for Analytics, ML, and AI |

Everything you learn about shapes, dtypes, missing values, and memory here
carries directly into every DataFrame engine you meet next. When pandas or
Spark surprises you later, come back to this module's notes first.
