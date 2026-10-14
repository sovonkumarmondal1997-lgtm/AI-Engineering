# 12 — Copy-on-Write and Chained Assignment Pitfalls

> **Stage 2 — Python for Data Engineering · Module 2.3 — DataFrames with pandas**

> **Central production principle:** Write DataFrame transformations so that mutation is explicit, ownership is understandable, and functions do not unexpectedly modify caller-owned inputs.

This chapter uses the **modern pandas 3.x Copy-on-Write (CoW)** model as the primary context. In pandas 3.0, CoW is the default and only mode. Indexing results behave as copies from the user's perspective, chained assignment cannot update the original pandas object, and pandas may defer physical copying until a write requires storage separation. 

The most important assignment rule is:

> **When you intend to conditionally mutate a parent DataFrame, use one explicit `.loc[...] = ...` operation.**

For example:

```python
df.loc[mask, "y"] = 1
```

This chapter is not about banning mutation. It is about making **ownership, mutation, and independence predictable**.

---

## 1. Why Copy-on-Write Matters

After writing enough pandas code, you will create subsets, helper Series, temporary DataFrames, and NumPy representations. The dangerous question is:

> “When I modify this object, which other objects can change?”

In legacy pandas, views and copies could make that answer difficult to predict. Modern CoW gives a stronger user-facing rule: derived pandas objects behave independently, even when pandas can avoid an immediate physical copy. 

Start with a prediction:

```python
import pandas as pd

df = pd.DataFrame(
    {
        "x": [-1, 1, 2],
        "y": [10, 20, 30],
    }
)

subset = df[df["x"] > 0]
subset["y"] = 1
```

**Prediction:** Does `df` change?

Under modern CoW:

```python
assert df["y"].tolist() == [10, 20, 30]
assert subset["y"].tolist() == [1, 1]
```

The subset changes. The parent does not.

That difference matters in:

- ETL pipelines;
- batch jobs;
- notebooks;
- tests;
- reusable transformation functions;
- data-quality workflows;
- incident debugging.

---

## 2. Parent DataFrame and Subset Mental Model

Think of the relationship this way:

```text
Original DataFrame
        |
        | indexing
        v
Subset / derived object
        |
        | modification
        v
Copy-on-Write rules
        |
        +--> parent remains logically independent
        |
        +--> physical separation occurs when required
```

Two concepts must stay separate:

| Concept | Meaning |
| --- | --- |
| Logical independence | Mutating the derived object does not unexpectedly mutate the source |
| Physical sharing | pandas may temporarily reuse underlying storage internally |
| Physical separation | pandas creates or materializes separate storage when a write requires it |

The first is a user-facing behavior. The second and third are storage mechanics.

**Do not infer physical memory behavior from the word “copy.”**

---

## 3. What Is Aliasing?

**Aliasing** means that multiple Python-level objects can provide access to the same underlying storage.

Conceptually:

```text
Object A
   |
   +---- shared storage ----+
                            |
Object B <------------------+
```

Aliasing becomes dangerous when code relies on accidental mutation propagation.

Modern CoW changes the practical rule:

> A derived DataFrame or Series behaves as an independent object from the user's point of view.

This removes the need to reason about many historical “is this slice a view?” cases merely to predict whether a mutation will leak into the parent. 

---

## 4. View vs Copy — Historical Vocabulary

A **view** is traditionally described as an object that refers to the same underlying storage.

A **copy** is traditionally described as an independently stored object.

That vocabulary remains useful for understanding older pandas and NumPy behavior, but it is **not** the modern pandas user-facing prediction rule.

Modern CoW is better summarized as:

> Indexing or other operations that produce a new pandas object behave like a copy with respect to subsequent mutation.

This does **not** mean:

> “A full physical copy is always allocated immediately.”

Instead, pandas can delay physical copying where safe. 

---

## 5. The Core Chained-Assignment Problem

Consider:

```python
df["y"][df["x"] > 0] = 1
```

The expression has two conceptual indexing steps:

```python
temp = df["y"]
temp[df["x"] > 0] = 1
```

The second assignment targets `temp`, an intermediate object.

Under pandas 3.x CoW, this cannot update the parent `df`. pandas reports a `ChainedAssignmentError` warning for this pattern. 

### Another chained form

```python
df[df["x"] > 0]["y"] = 1
```

Here the first indexing operation produces a derived DataFrame and the second targets a column on that derived object.

### Correct replacement

```python
mask = df["x"] > 0
df.loc[mask, "y"] = 1
```

The target is now explicit.

---

## 6. Why `df["col"][mask] = value` Is Chained Assignment

Read the dangerous expression as:

```python
df["col"]
```

followed by:

```python
[mask]
```

The first operation returns an intermediate object. The second assignment operates on that intermediate object.

The problem is therefore not string length or syntax style. The problem is **the assignment target is not the parent DataFrame itself**.

The key question is:

> Can I point to the actual owner of the mutation in the left-hand side?

For parent mutation, write:

```python
df.loc[mask, "col"] = value
```

This makes the owner, row selection, and column selection explicit in one operation.

---

## 7. Modern Copy-on-Write Behavior

Under modern CoW, pandas prevents one statement from unexpectedly mutating multiple pandas objects.

A simple demonstration:

```python
import pandas as pd

df = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})
subset = df["foo"]

subset.iloc[0] = 100

assert subset.iloc[0] == 100
assert df["foo"].iloc[0] == 1
```

The derived Series changes. The parent DataFrame does not.

This is exactly the kind of behavior CoW was designed to make predictable. 

---

## 8. The Correct Pattern — Single `.loc` Assignment

Use:

```python
df.loc[mask, "y"] = value
```

Read this as:

1. `df` — the owner to mutate;
2. `.loc[...]` — one explicit selection;
3. `mask` — rows;
4. `"y"` — target column;
5. `= value` — intentional mutation.

### Side-by-side

```python
# Chained assignment: do not use for parent mutation.
df["y"][mask] = value

# Correct direct assignment.
df.loc[mask, "y"] = value
```

The second form is the pattern to standardize across production code.

---

## 9. Multiple-Column Assignment with `.loc`

A single `.loc` operation can target multiple columns:

```python
mask = df["x"] > 0
df.loc[mask, ["flag", "priority"]] = [True, "high"]
```

When using multiple columns:

- verify the right-hand-side shape;
- test the result;
- verify that non-target rows were unchanged.

A correct ownership pattern does not automatically make every right-hand-side shape correct.

---

## 10. Conditional Assignment and Business Semantics

Mechanically correct mutation can still encode the wrong business rule.

```python
mask = df["amount"] > 10_000
df.loc[mask, "high_value"] = True
```

This is only correct if the business definition of `high_value` is actually “amount > 10,000.”

Another example:

```python
df.loc[df["status"] == "cancelled", "revenue"] = 0
```

That may be valid in one accounting pipeline and wrong in another.

Separate:

- **assignment mechanics** — how rows and columns are targeted;
- **business semantics** — why those rows should change.

### Conditional-assignment checklist

1. Which DataFrame should change?
2. Which rows should change?
3. Which columns should change?
4. Is the target expressed in one explicit operation?
5. Is the mutation intentional?
6. What invariant proves the result is correct?

---

## 11. Copy-on-Write: the Two-Layer Model

A useful deep mental model is:

```text
LOGICAL BEHAVIOR
Parent and derived object
        |
        +--> behave independently

PHYSICAL STORAGE
Storage may be shared
        |
        +--> write requires separation
        |
        +--> separation/copy is materialized as needed
```

pandas documents that CoW makes derived DataFrames and Series behave like copies and delays copies where possible. 

This explains why:

- user-facing behavior can be predictable;
- eager copying is not required for every derived object;
- a later mutation can still have a physical memory cost.

---

## 12. Lazy / Deferred Physical Copying

“Lazy copy” here means:

> pandas can defer physical data copying until a write requires it.

Conceptual diagram:

```text
Before mutation

Parent  -----------+
                   |
                   +---- storage may be shared
                   |
Subset  -----------+


After subset mutation

Parent  ---------------- original storage

Subset  ---------------- separated storage
```

This is a conceptual model, not a guarantee about one exact internal layout for every DataFrame operation.

Do not say:

- “every subset is physically copied immediately”;
- “no copy ever happens.”

Both are wrong as universal claims.

---

## 13. Why CoW Reduces Defensive Copies

A common legacy defensive pattern was:

```python
subset = df.loc[mask].copy()
```

used everywhere simply because the developer feared view behavior.

Modern CoW reduces the need for **defensive copying solely for mutation isolation**. Derived objects already have predictable logical semantics. 

But `.copy()` is still a valid tool when it expresses a real ownership decision.

The balanced rule is:

> **Do not copy everything. Do not never copy. Copy intentionally.**

---

## 14. Legacy pandas 1.x / 2.x Behavior

Older pandas versions used a more complicated view/copy model.

Depending on the exact operation, a derived object could be a view or a copy, and code could become dependent on behavior that was difficult to reason about.

This history explains why older resources often discuss:

- `SettingWithCopyWarning`;
- “is this a view?”;
- adding `.copy()` to silence warnings;
- chained assignment folklore.

Modern pandas 3.x uses CoW as the default and only mode. Code should be migrated to the modern semantics. 

---

## 15. `SettingWithCopyWarning` — Historical Context

A classic older example:

```python
df[df["x"] > 0]["y"] = 1
```

could generate:

```text
SettingWithCopyWarning
```

Historically, the warning tried to communicate that the developer might be assigning into a copy rather than the intended parent.

The difficulty was that developers had to reason about an ambiguous view/copy model.

In modern pandas 3.x, this historical warning is no longer the primary model. Chained assignment is instead incompatible with CoW and produces the modern `ChainedAssignmentError` warning. 

---

## 16. `ChainedAssignmentError` in Modern pandas

Modern pandas explicitly describes chained assignment as something that can never update the original object under CoW. 

Example:

```python
import pandas as pd

df = pd.DataFrame(
    {"foo": [1, 1, 1, 2, 2]}
)

df["foo"][df["foo"] == 1] = 5
```

The modern repair is:

```python
df.loc[df["foo"] == 1, "foo"] = 5
```

Treat this warning as a **migration signal**, not as something to silence.

---

## 17. Legacy Migration — Before and After

### Example A — filtered rows

Legacy:

```python
df[df["amount"] > 1000]["flag"] = True
```

Modern:

```python
df.loc[df["amount"] > 1000, "flag"] = True
```

### Example B — selected Series first

Legacy:

```python
df["status"][df["status"] == "pending"] = "review"
```

Modern:

```python
mask = df["status"].eq("pending")
df.loc[mask, "status"] = "review"
```

### Example C — subset intentionally owned by a function

Legacy-style:

```python
active = df[df["status"] == "active"]
active["score"] = active["score"].fillna(0)
```

Explicit independent ownership:

```python
active = df.loc[df["status"].eq("active")].copy()
active["score"] = active["score"].fillna(0)
```

Parent mutation instead:

```python
mask = df["status"].eq("active")
df.loc[mask, "score"] = df.loc[mask, "score"].fillna(0)
```

The right migration depends on the intended owner.

---

## 18. Legacy Code That Relied on View Mutation

Some old code intentionally or accidentally relied on this style:

```python
subset = df["amount"]
subset.iloc[0] = 999
```

and then expected `df["amount"]` to change.

Modern CoW does not support that propagation pattern.

Rewrite the actual business operation explicitly:

```python
df.loc[df.index[0], "amount"] = 999
```

Migration principle:

> **Preserve business intent, not accidental aliasing.**

---

## 19. When `.copy()` Is Still Useful

`.copy()` remains useful when it serves one of these engineering purposes:

### 1. Explicit ownership boundary

```python
def prepare_subset(df: pd.DataFrame) -> pd.DataFrame:
    work = df.loc[df["status"].eq("active")].copy()
    return work
```

### 2. Deliberately independent working object

You want the function or downstream code to own a distinct working frame.

### 3. Large-parent / small-subset memory scenario

A small retained object may be worth copying when the large parent is going to be discarded and memory lifetime matters.

`.copy()` should therefore communicate intent, not fear.

---

## 20. `.copy()` at Function Boundaries

A function can use `.copy()` to make its ownership contract explicit:

```python
def prepare_active_orders(df: pd.DataFrame) -> pd.DataFrame:
    work = df.loc[df["status"].eq("active")].copy()
    work["priority"] = "normal"
    return work
```

The function is saying:

> “From this point forward, `work` is an independently owned working object.”

That copy is not necessarily required for basic correctness under CoW; the value is the explicit ownership boundary.

---

## 21. `.copy()` and Memory Release

Consider:

```text
Parent frame:          ~10 GB
Retained subset:       ~10 MB
```

If the small object keeps storage associated with the larger parent alive, an explicit independent copy can sometimes help a pipeline retain only what it needs after discarding the parent.

This is a memory-lifetime decision.

Do not claim:

> “Every small slice keeps the full 10 GB allocation alive.”

The actual storage relationship depends on the DataFrame layout and operation.

Measure the real case.

```python
bytes_used = df.memory_usage(deep=True).sum()
print(f"{bytes_used:,} bytes")
```

`memory_usage(deep=True)` provides DataFrame memory accounting; it is not a complete process-level memory profiler.

---

## 22. Explicit Ownership Model

Use this mental model:

```text
Need only to inspect/derive?
        |
        v
Create a derived object
        |
        v
Transform / return result


Need independent working ownership?
        |
        v
.copy()
        |
        v
Mutate the owned object
```

The question is not “Should I always copy?”

The question is:

> **Where is the ownership boundary?**

---

## 23. CoW and Performance

CoW is primarily about predictable semantics and controlled copying.

Potential costs and benefits depend on:

- DataFrame size;
- number of columns;
- dtype layout;
- number of derived objects;
- when writes occur;
- how many temporary objects exist;
- how long parent objects remain alive.

Do not make absolute statements such as:

- “CoW always makes it faster”;
- “CoW always reduces memory”;
- “method chaining is faster.”

Benchmark equivalent workloads:

```python
from time import perf_counter

start = perf_counter()
result = transform(df)
elapsed = perf_counter() - start

print(f"{elapsed:.6f} seconds")
```

Measure actual workloads rather than arguing from folklore.

---

## 24. Memory Behavior

The memory cost of a transformation can depend on:

- which columns are accessed;
- when a mutation happens;
- number and size of columns;
- extension dtypes;
- temporary results;
- retained references.

A useful experiment:

```python
before = df.memory_usage(deep=True).sum()

subset = df.loc[mask]

after = subset.memory_usage(deep=True).sum()

print({"parent_bytes": before, "subset_bytes": after})
```

Interpret the numbers cautiously.

The final size of `subset` is not the same thing as process peak memory.

---

## 25. NumPy Interoperability

Pandas and NumPy have different ownership rules.

Two APIs you will encounter are:

```python
arr1 = df.to_numpy()
arr2 = df.values
```

For new code, `to_numpy()` is the clearer explicit conversion API.

Its `copy=False` default does **not** guarantee zero-copy. pandas documents that conversion may still allocate or coerce to a common NumPy dtype; `copy=True` guarantees a copy. 

The key question for this chapter is:

> **If I mutate the NumPy array, can I accidentally mutate pandas-owned data?**

Under CoW, pandas can return a read-only array to prevent this. 

---

## 26. Read-Only NumPy Arrays Under CoW

Try:

```python
import pandas as pd

df = pd.DataFrame(
    {
        "a": [1, 2],
        "b": [3, 4],
    }
)

arr = df.to_numpy()
print(arr.flags.writeable)
```

Depending on the DataFrame representation, the result may be a read-only array when it shares data with pandas.

An attempted mutation can then fail:

```python
if not arr.flags.writeable:
    print("Array is read-only")
```

The official pandas documentation demonstrates this protection with a `ValueError` from an attempted write to a read-only shared array. 

Do not assume every mixed-dtype DataFrame produces the same physical array. `to_numpy()` may coerce or allocate. 

---

## 27. Copy Before Mutating a NumPy Array

If you need an independent mutable array:

```python
arr = df.to_numpy().copy()
arr[0, 0] = 999
```

Now `arr` has independent NumPy storage.

The important distinction is:

```text
df.to_numpy()
    ↓
may share storage
    ↓
may be read-only

df.to_numpy().copy()
    ↓
independent NumPy storage
    ↓
safe to mutate
```

pandas also documents that manually overriding the writeable flag is possible but bypasses CoW protection and should therefore be treated cautiously. 

---

## 28. `to_numpy()` vs `.values`

Prefer:

```python
arr = df.to_numpy()
```

over:

```python
arr = df.values
```

when you are intentionally crossing from pandas into NumPy.

The reason is clarity of intent.

Neither API should be treated as a universal guarantee that the returned array is writable.

Check:

```python
arr.flags.writeable
```

when mutation matters.

---

## 29. Writing Non-Mutating Transformation Functions

A reusable transformation can avoid surprising caller-owned mutation:

```python
def add_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(
        revenue=lambda d: d["quantity"] * d["unit_price"]
    )
```

Benefits:

- caller keeps the original;
- output is easy to assert;
- composition is straightforward;
- unit tests can compare before and after state;
- ownership is easier to reason about.

This is especially useful for reusable Data Engineering transformations.

---

## 30. Mutating vs Non-Mutating Functions

### Mutating

```python
def add_revenue_mutating(df: pd.DataFrame) -> pd.DataFrame:
    df["revenue"] = df["quantity"] * df["unit_price"]
    return df
```

### Non-mutating

```python
def add_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(
        revenue=lambda d: d["quantity"] * d["unit_price"]
    )
```

Do not turn this into “mutation is forbidden.”

Instead ask:

- Is mutation part of the documented contract?
- Will callers expect the input to remain unchanged?
- Is this function being reused in a pipeline?
- Is independent testing important?

Non-mutating transformations are often easier to compose and test.

---

## 31. Function Contracts

Every reusable transformation function should have a clear contract.

A useful template is:

```text
Function:
  transform_orders

Input:
  DataFrame containing order_id, quantity, unit_price

Output:
  DataFrame containing the original columns plus revenue

Mutation:
  Does not modify the caller-owned input

Invariants:
  Input values and schema are unchanged
```

The contract answers a production question before anyone has to inspect implementation details.

A function that intentionally mutates can also have a contract:

```text
Mutation:
  Intentionally updates the supplied DataFrame in-place.

Owner:
  Caller retains ownership of the same DataFrame object.

Tests:
  Targeted values change; unrelated values remain unchanged.
```

The important lesson is not that one contract is always superior. The important lesson is that **the contract is explicit**.

---

## 32. Testing Input Immutability

The roadmap requires proving that a transformation function does not mutate its input.

Use a deep-copy snapshot in the test:


```python
import pandas as pd

def add_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(
        revenue=lambda d: d["quantity"] * d["unit_price"]
    )

df = pd.DataFrame(
    {
        "quantity": [2, 3],
        "unit_price": [10.0, 5.0],
    }
)

original = df.copy(deep=True)
result = add_revenue(df)

pd.testing.assert_frame_equal(df, original)
assert result["revenue"].tolist() == [20.0, 15.0]
```

The assertion proves that the **observable DataFrame content** of `df` is unchanged by this transformation.

Why `deep=True` here?

Because the test wants an independent snapshot for comparison. That is a test-fixture technique. It is not a rule that every production DataFrame must be deep-copied.

---

## 33. Why `copy(deep=True)` Is Useful in Tests

A mutation test can fail to detect a problem if its baseline is also affected.

Bad conceptual test:

```python
before = df
transform(df)
assert df is before
```

This only checks object identity. It says nothing about content changes.

Better:


```python
before = df.copy(deep=True)

transform(df)

pd.testing.assert_frame_equal(df, before)
```

The baseline represents the expected pre-call state.

The distinction is:

| Test idea | What it proves |
| --- | --- |
| `df is before` | Object identity |
| `assert_frame_equal(df, before)` | DataFrame content equality |
| Deep-copy baseline + equality | Strong input-preservation test for test fixtures |

---

## 34. Pytest Fixture for Input Immutability

A small deterministic fixture keeps the test easy to understand:


```python
import pandas as pd
import pytest

@pytest.fixture
def source_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "quantity": [2, 3],
            "unit_price": [10.0, 5.0],
        }
    )
```

Then:


```python
def test_add_revenue_does_not_mutate_input(source_df):
    original = source_df.copy(deep=True)

    result = add_revenue(source_df)

    pd.testing.assert_frame_equal(source_df, original)
    assert result["revenue"].tolist() == [20.0, 15.0]
```

For unit tests, tiny fixtures are preferable. Use larger integration tests when you need scale characteristics.

---

## 35. Testing Legitimate Mutation

Do not build a test suite that treats every mutation as an error. Direct mutation can be intentional.

Test the exact contract:


```python
def test_loc_assignment_changes_only_target_rows():
    df = pd.DataFrame(
        {
            "x": [-1, 1, 2],
            "flag": [False, False, False],
        }
    )

    mask = df["x"] > 0
    df.loc[mask, "flag"] = True

    expected = pd.DataFrame(
        {
            "x": [-1, 1, 2],
            "flag": [False, True, True],
        }
    )

    pd.testing.assert_frame_equal(df, expected)
```

The test verifies:

- intended rows changed;
- non-target rows did not change;
- the shape remained valid;
- the assignment happened on the intended owner.

---

## 36. Ten Parent / Subset / Array Experiments

The roadmap asks for ten small experiments. Use the learning loop:

> **Predict → Execute → Inspect → Assert → Explain**

Do not start by running the snippet. First write down the expected parent, subset, and array state.

### Experiment 1 — Filtered subset modification


```python
import pandas as pd

df = pd.DataFrame(
    {
        "x": [-1, 1, 2],
        "y": [10, 20, 30],
    }
)

subset = df[df["x"] > 0]
subset["y"] = 999

assert df["y"].tolist() == [10, 20, 30]
assert subset["y"].tolist() == [999, 999]
```

**Prediction:** the subset changes; the parent remains unchanged.

### Experiment 2 — Subset column assignment


```python
df = pd.DataFrame(
    {
        "x": [-1, 1, 2],
        "y": [10, 20, 30],
    }
)

subset = df.loc[df["x"] > 0]
subset["flag"] = True

assert "flag" not in df.columns
assert subset["flag"].tolist() == [True, True]
```

**Prediction:** adding the new column affects only the derived object.

### Experiment 3 — Chained assignment


```python
df = pd.DataFrame(
    {
        "x": [-1, 1, 2],
        "y": [10, 20, 30],
    }
)

df["y"][df["x"] > 0] = 0

assert df["y"].tolist() == [10, 20, 30]
```

Under pandas 3.x, the chained assignment cannot update the parent. A `ChainedAssignmentError` warning is expected from the operation. 

### Experiment 4 — Direct `.loc` assignment


```python
df = pd.DataFrame(
    {
        "x": [-1, 1, 2],
        "y": [10, 20, 30],
    }
)

mask = df["x"] > 0
df.loc[mask, "y"] = 0

assert df["y"].tolist() == [10, 0, 0]
```

**Prediction:** the parent changes because it is the explicit target.

### Experiment 5 — Multiple-column assignment


```python
df = pd.DataFrame(
    {
        "x": [-1, 1, 2],
        "a": [0, 0, 0],
        "b": [0, 0, 0],
    }
)

mask = df["x"] > 0
df.loc[mask, ["a", "b"]] = [1, 2]

assert df.loc[1, "a"] == 1
assert df.loc[2, "b"] == 2
assert df.loc[0, "a"] == 0
```

**Prediction:** only the selected rows receive the two assigned values.

### Experiment 6 — Slice-derived object


```python
df = pd.DataFrame(
    {
        "x": [0, 1, 2, 3],
        "y": [10, 20, 30, 40],
    }
)

subset = df.iloc[:2]
subset["y"] = 999

assert df["y"].tolist() == [10, 20, 30, 40]
```

**Prediction:** the parent stays unchanged under CoW.

### Experiment 7 — NumPy conversion


```python
df = pd.DataFrame(
    {
        "a": [1, 2],
        "b": [3, 4],
    }
)

arr = df.to_numpy()

assert arr.shape == (2, 2)
```

**Prediction:** a NumPy array is returned, but its writability depends on its representation and sharing relationship.

### Experiment 8 — Read-only NumPy mutation attempt


```python
df = pd.DataFrame(
    {
        "a": [1, 2],
        "b": [3, 4],
    }
)

arr = df.to_numpy()

if not arr.flags.writeable:
    try:
        arr[0, 0] = 999
    except ValueError:
        pass
```

Do not make your lab depend on every DataFrame representation being read-only. The point is to observe the flag and understand why pandas may protect a shared representation.

### Experiment 9 — Copy before NumPy mutation


```python
df = pd.DataFrame(
    {
        "a": [1, 2],
        "b": [3, 4],
    }
)

arr = df.to_numpy().copy()
arr[0, 0] = 999

assert df.loc[0, "a"] == 1
assert arr[0, 0] == 999
```

**Prediction:** only the independent NumPy array changes.

### Experiment 10 — Non-mutating transformation


```python
def add_total(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(total=lambda d: d["a"] + d["b"])

df = pd.DataFrame({"a": [1, 2], "b": [10, 20]})
original = df.copy(deep=True)

result = add_total(df)

pd.testing.assert_frame_equal(df, original)
assert result["total"].tolist() == [11, 22]
```

**Prediction:** output changes; input does not.

---

## 37. Hands-On Exercise — `cow_lab.py`

This is the complete roadmap exercise. **Create `cow_lab.py` in your study project; this chapter does not create it.**

### Task 1 — Reproduce a chained-assignment bug

Use a small DataFrame and reproduce:


```python
import pandas as pd

df = pd.DataFrame(
    {
        "x": [-1, 1, 2],
        "y": [10, 20, 30],
    }
)

mask = df["x"] > 0
df["y"][mask] = 999
```

Record:

- your prediction;
- the modern pandas warning;
- the final parent DataFrame;
- why the parent did not change.

Then repair it:


```python
df.loc[mask, "y"] = 999
assert df["y"].tolist() == [10, 999, 999]
```

### Task 2 — Modify a filtered subset


```python
df = pd.DataFrame(
    {
        "x": [-1, 1, 2],
        "y": [10, 20, 30],
    }
)

subset = df[df["x"] > 0]
subset["y"] = 0

assert df["y"].tolist() == [10, 20, 30]
assert subset["y"].tolist() == [0, 0]
```

Explain why the subset changing does not imply that the parent changed.

### Task 3 — NumPy interoperability


```python
arr = df.to_numpy()
print("writeable:", arr.flags.writeable)
```

When the array is read-only, attempting an in-place write is expected to fail:


```python
if not arr.flags.writeable:
    try:
        arr[0, 0] = 123
    except ValueError as exc:
        print(type(exc).__name__, str(exc))
```

Then create an independent mutable array:


```python
arr_copy = df.to_numpy().copy()
arr_copy[0, 0] = 123
```

### Task 4 — Input non-mutation test

Write a helper:


```python
def assert_does_not_mutate(transform, input_df):
    original = input_df.copy(deep=True)
    transform(input_df)
    pd.testing.assert_frame_equal(input_df, original)
```

Use it against at least one intentionally non-mutating transformation.

### Task 5 — Refactor `inplace=True` and unnecessary `.copy()`

Start with:


```python
def prepare_orders_legacy(df: pd.DataFrame) -> pd.DataFrame:
    work = df.loc[df["status"].eq("active")].copy()
    work.drop(columns=["debug"], inplace=True)
    work.reset_index(drop=True, inplace=True)
    work = work.copy()
    return work
```

Refactor:


```python
def prepare_orders(df: pd.DataFrame) -> pd.DataFrame:
    work = df.loc[df["status"].eq("active")]
    work = work.drop(columns=["debug"])
    work = work.reset_index(drop=True)
    return work
```

Explain why the defensive `.copy()` can be removed under pandas 3.x Copy-on-Write: `df.loc[...]` already returns an object that behaves as an independent copy, `drop` and `reset_index` return new objects, and nothing in the function modifies `df` or a view of it.

### Task 6 — Measure memory before and after

Compare the legacy and refactored functions from Task 5 on the same input DataFrame:


```python
import gc
import tracemalloc


def measure_peak_traced_memory(fn, df):
    gc.collect()
    tracemalloc.start()

    before_current, before_peak = tracemalloc.get_traced_memory()
    result = fn(df)
    after_current, after_peak = tracemalloc.get_traced_memory()

    tracemalloc.stop()

    return result, {
        "before_current_bytes": before_current,
        "before_peak_bytes": before_peak,
        "after_current_bytes": after_current,
        "peak_bytes": after_peak,
    }


_, legacy_memory = measure_peak_traced_memory(
    prepare_orders_legacy,
    df,
)

_, refactored_memory = measure_peak_traced_memory(
    prepare_orders,
    df,
)

print(
    {
        "legacy": legacy_memory,
        "refactored": refactored_memory,
    }
)
```

Compare the traced peak allocations of the legacy and refactored implementations.

- The comparison must use equivalent input data: the same `df` for both functions.
- Record actual measurements. Never fabricate benchmark values.
- `tracemalloc` measures traceable Python allocations. It is not the same as OS-level RSS/process-memory measurement, and memory allocated outside Python's allocator may not appear in it.

---

## 38. Legacy Migration Exercise

Take a legacy snippet such as:


```python
df[df["amount"] > 1000]["flag"] = True
```

Migrate it:


```python
df.loc[df["amount"] > 1000, "flag"] = True
```

Then add a regression test that proves:

- intended rows changed;
- unrelated rows did not change;
- the operation targets the parent explicitly.

### Migration procedure

1. Identify the intended owner.
2. Identify every indexing operation.
3. Replace chained assignment with direct assignment to the owner.
4. Decide whether `.copy()` is actually required.
5. Review Series derived from DataFrames.
6. Review code that uses `inplace=True` on derived Series.
7. Review NumPy array mutation.
8. Run the test suite under pandas 3.x.
9. Record any migration-specific failures.

pandas' migration guidance states that chained assignment will never work under CoW and recommends `loc` as the alternative. 

---

## 39. Debugging Section

For every debugging problem, follow:

**Buggy code → Expected behavior → Actual behavior → Root cause → Corrected code → Prevention rule**

### 1. Assuming filtered-subset mutation changes the parent

**Bug:**


```python
subset = df[df["x"] > 0]
subset["y"] = 1
```

**Root cause:** the derived object is logically independent under CoW.

**Correction when the parent should change:**


```python
df.loc[df["x"] > 0, "y"] = 1
```

**Prevention:** state the intended owner before assignment.

### 2. Using `df["col"][mask] = value`


```python
df["y"][df["x"] > 0] = 1
```

**Root cause:** two indexing operations create an intermediate target.

**Correction:**


```python
df.loc[df["x"] > 0, "y"] = 1
```

**Prevention:** one explicit parent assignment.

### 3. Using `df[mask]["col"] = value`


```python
df[df["x"] > 0]["y"] = 1
```

**Root cause:** assignment targets a derived DataFrame.

**Correction:**


```python
df.loc[df["x"] > 0, "y"] = 1
```

### 4. Copying everywhere


```python
a = df.copy()
b = a.copy()
c = b.loc[mask].copy()
```

**Root cause:** copying is used as fear-driven protection rather than a documented ownership decision.

**Correction:** retain only copies with a concrete purpose.

### 5. Trusting an old Stack Overflow answer

**Root cause:** the answer may target pre-CoW behavior.

**Correction:** inspect the target pandas version and migrate code to current semantics.

### 6. Expecting `SettingWithCopyWarning`

**Root cause:** historical warning model.

**Correction:** in pandas 3.x, chained assignment is incompatible with CoW and produces `ChainedAssignmentError` warnings. 

### 7. Ignoring `ChainedAssignmentError`

**Root cause:** treating a correctness signal as cosmetic.

**Correction:** replace chained assignment with a direct assignment.

### 8. Mutating a subset when parent was intended


```python
active = df[df["status"].eq("active")]
active["flag"] = True
```

**Correction:**


```python
mask = df["status"].eq("active")
df.loc[mask, "flag"] = True
```

### 9. Mutating parent when independent object was intended

**Correction:**


```python
active = df.loc[df["status"].eq("active")].copy()
active["flag"] = True
```

### 10. Missing `.copy()` at a deliberate ownership boundary

If the API contract says “this function owns an independent working frame,” make that contract explicit.

### 11. Keeping a tiny object with a huge parent

**Root cause:** memory lifetime can differ from final result size.

**Correction:** measure the actual relationship and copy the retained subset when that memory-lifetime decision is justified.

### 12. Assuming every copy happens immediately

**Root cause:** confusing CoW logical semantics with physical storage.

**Correction:** distinguish logical independence from deferred physical copying.

### 13. Assuming no copy ever happens

**Root cause:** interpreting CoW as “zero-copy.”

**Correction:** writes can require separation.

### 14. Treating CoW as a free performance optimization

**Root cause:** assuming fewer eager copies guarantees faster code.

**Correction:** benchmark equivalent workloads.

### 15. Mutating a read-only `to_numpy()` result


```python
arr = df.to_numpy()

if not arr.flags.writeable:
    arr = arr.copy()

arr[0, 0] = 100
```

### 16. Assuming `.values` is always writable

**Correction:** use `to_numpy()` intentionally and inspect `flags.writeable`.

### 17. Calling `.copy()` indiscriminately

**Correction:** identify the ownership reason for every copy.

### 18. Silently mutating a function input

**Bug:**


```python
def clean(df):
    df["status"] = df["status"].str.upper()
    return df
```

**Preferred non-mutating form:**


```python
def clean(df):
    return df.assign(
        status=lambda d: d["status"].str.upper()
    )
```

### 19. Testing only output

**Root cause:** an output assertion cannot prove the input stayed unchanged.

**Correction:** snapshot and compare the input.

### 20. Deep-copying gigantic test fixtures unnecessarily

**Root cause:** using unit-test isolation at production scale.

**Correction:** use small deterministic fixtures for unit tests and separately measure large-scale behavior.

### 21. Confusing logical and physical independence

**Root cause:** “behaves like a copy” is interpreted as “must be physically copied now.”

**Correction:** preserve the two-layer mental model.

### 22. Migrating code while preserving accidental aliasing

**Correction:** preserve the intended business operation, not the old alias relationship.

---

## 40. Testing Section

### Chained assignment

Test the replacement, not the invalid mechanism.


```python
def test_direct_assignment_updates_parent():
    df = pd.DataFrame(
        {
            "x": [-1, 1, 2],
            "y": [10, 20, 30],
        }
    )

    df.loc[df["x"] > 0, "y"] = 0

    assert df["y"].tolist() == [10, 0, 0]
```

### Subset independence


```python
def test_subset_mutation_does_not_change_parent():
    df = pd.DataFrame(
        {
            "x": [-1, 1, 2],
            "y": [10, 20, 30],
        }
    )

    subset = df.loc[df["x"] > 0]
    subset["y"] = 0

    assert df["y"].tolist() == [10, 20, 30]
```

### Non-mutating function


```python
def test_add_revenue_preserves_input():
    df = pd.DataFrame(
        {
            "quantity": [2, 3],
            "unit_price": [10.0, 5.0],
        }
    )
    original = df.copy(deep=True)

    result = add_revenue(df)

    pd.testing.assert_frame_equal(df, original)
    assert result["revenue"].tolist() == [20.0, 15.0]
```

### NumPy copy-before-mutation


```python
def test_numpy_copy_is_independent():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    arr = df.to_numpy().copy()
    arr[0, 0] = 999

    assert arr[0, 0] == 999
    assert df.loc[0, "a"] == 1
```

### Test matrix

| Area | Required checks |
| --- | --- |
| Chained assignment | Parent stays unchanged; corrected `.loc` changes target |
| Subset | Derived object can change independently |
| `.copy()` | Deliberate working copy behaves as expected |
| NumPy | Conversion succeeds; writeability is inspected |
| NumPy copy | Mutation affects only copied array |
| Input immutability | Deep-copy baseline matches after transformation |
| Edge cases | Empty, one row, no matches, all matches, duplicates, missing values |
| Migration | Legacy behavior is not relied upon |

---

## 41. Edge Cases

### Empty DataFrame


```python
empty = pd.DataFrame({"x": pd.Series(dtype="int64")})
result = empty.assign(y=1)

assert result.empty
assert "y" in result.columns
```

Test the resulting schema intentionally if a new column is introduced.

### Zero-row subset


```python
subset = df.loc[df["x"] > 999]
assert subset.empty
```

The parent is unaffected.

### All-row subset

Selecting every row still produces a derived object. Do not assume parent mutation through subset assignment.

### One-row subset

Useful for testing code that accidentally assumes at least two rows.

### Duplicate index labels

Duplicate labels do not change the basic CoW ownership rule, but they can change the meaning of a label-based assignment. Test selection semantics separately.

### Non-default integer indexes

Do not confuse label `0` with position `0`.

### Boolean mask with no matches


```python
mask = df["x"] > 10_000
assert not mask.any()
df.loc[mask, "y"] = 0
```

The assignment is still structurally valid; no target rows are changed.

### Nullable boolean masks

When masks contain missing values, test the intended semantics explicitly rather than assuming missing means `False`.

### Missing values

Test whether the business rule should preserve missingness or replace it.

### Multiple-column assignment

Check right-hand-side shape and resulting columns.

### Large parent + small subset

Treat this as a memory-lifetime experiment. Measure rather than generalize.

### Mixed-dtype `to_numpy()`

`to_numpy()` may coerce to a common NumPy dtype and may allocate. 

### Read-only array

Inspect:


```python
arr.flags.writeable
```

### Independent NumPy copy


```python
arr = df.to_numpy().copy()
```

### Intentional mutation functions

If a function intentionally mutates, document and test the mutation contract.

---

## 42. Production Data Engineering Use Cases

### Data cleaning

Conditionally update invalid records:


```python
invalid = df["amount"].lt(0)
df.loc[invalid, "amount"] = pd.NA
```

### Silver transformations

Use explicit transformations rather than hidden mutation:


```python
def standardize_status(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(
        status=lambda d: d["status"].astype("string").str.strip().str.lower()
    )
```

### Reusable pipeline functions

Prefer functions whose mutation contract is easy to state.

### Large datasets

Avoid “copy everything” patterns. Copy cost becomes increasingly important as DataFrames grow.

### Data quality

Inspect or transform derived frames without assuming changes propagate backward.

### NumPy interoperability

When a downstream numerical step requires mutable storage:


```python
features = df[["feature_a", "feature_b"]].to_numpy().copy()
```

Then mutate the owned NumPy buffer as required.

---

## 43. Memory and Performance Experiment

The roadmap requires comparing:

### Strategy A — defensive copying at every step


```python
a = df.copy(deep=True)
b = a.loc[mask].copy(deep=True)
c = b.copy(deep=True)
```

### Strategy B — modern CoW with deliberate copying


```python
a = df.loc[mask]
b = a.assign(flag=True)
c = b
```

Measure:


```python
from time import perf_counter

start = perf_counter()
result = transform(df)
elapsed = perf_counter() - start

memory_bytes = df.memory_usage(deep=True).sum()

print(
    {
        "elapsed_seconds": elapsed,
        "dataframe_bytes": memory_bytes,
    }
)
```
### Questions

- Which strategy creates more intermediate objects?
- When does a physical copy happen?
- Which columns are involved?
- What happens when the mutation touches only one column?
- How does the result change with a wider DataFrame?
- What is final DataFrame memory versus process peak memory?
- Is the measured difference large enough to matter operationally?

pandas itself notes that CoW can improve average performance and memory usage by delaying copies, but this is not a guarantee for every workload. 

---

## 44. Why “Copy Everywhere” Is Not a Strategy

Consider this pattern:


```python
df = df.copy()
df = df.loc[mask].copy()
df = df.copy()
df = df.reset_index(drop=True).copy()
```

The code is difficult to review because every copy looks equally important.

Possible consequences:

- unnecessary memory allocations;
- higher memory traffic;
- additional runtime;
- harder ownership reasoning;
- increased peak memory;
- no explanation of why the copies exist.

A better standard is:

> **Every `.copy()` in production code should have a reason that a reviewer can understand.**

Typical reasons are:

- explicit ownership;
- deliberate isolation;
- test fixture protection;
- memory lifetime;
- an API contract.

---

## 45. Why “Never Copy” Is Not a Strategy

The opposite rule is equally dangerous:

```python
# "CoW means I never need copy."
```

That is also an oversimplification.

A deliberate copy can still be useful when:

- a function promises an independent working object;
- a caller wants to keep a small result after discarding a large parent;
- a NumPy consumer needs independent writable storage;
- a test needs a stable baseline;
- a boundary requires explicit ownership.

The engineering rule is:

> **Copy when the design requires independent ownership, not merely because historical pandas code was confusing.**

---

## 46. Code Review Checklist

Use this checklist during production review.

### Mutation

- [ ] No chained assignment.
- [ ] Conditional assignments use `.loc`.
- [ ] The intended DataFrame owner is obvious.
- [ ] Target rows and columns are explicit.
- [ ] Mutation is intentional.

### `.copy()`

- [ ] Every meaningful `.copy()` has a reason.
- [ ] No copy is present only to silence an obsolete warning.
- [ ] Large copies have been considered for memory impact.
- [ ] Ownership boundaries are documented where useful.

### Functions

- [ ] Mutation behavior is part of the function contract.
- [ ] Non-mutating transformations preserve input content.
- [ ] Mutating transformations are tested as mutating.
- [ ] Functions do not rely on accidental aliasing.

### NumPy

- [ ] `to_numpy()` is used intentionally.
- [ ] `flags.writeable` is checked when mutation matters.
- [ ] Independent mutable buffers use `.copy()` when required.
- [ ] Code does not assume `.values` is always writable.

### Testing

- [ ] Input immutability is tested where promised.
- [ ] Direct mutation is tested where promised.
- [ ] Edge cases are covered.
- [ ] Migration changes have regression tests.

### Performance

- [ ] Copy-heavy paths have been measured.
- [ ] DataFrame memory has been inspected when relevant.
- [ ] Peak process memory has been considered for large jobs.
- [ ] CoW claims are based on measurements.

---

## 47. pandas 1.x / 2.x → Modern pandas Migration Checklist

Use this when upgrading old code.

1. Search for `df[...][...] = ...`.
2. Search for `df[mask][column] = ...`.
3. Search for mutation of Series derived from DataFrames.
4. Search for code that expects derived objects to update parents.
5. Search for `SettingWithCopyWarning` suppression.
6. Identify the actual owner of each intended mutation.
7. Rewrite parent updates using `.loc` or `.iloc`.
8. Add `.copy()` only where independent ownership is intentional.
9. Review small-subset/large-parent memory lifetime.
10. Review `to_numpy()` and `.values` mutation.
11. Add input-immutability tests.
12. Run the full suite under pandas 3.x.
13. Remove assumptions that depended on legacy view/copy behavior.
14. Keep a short migration note for any intentional behavioral change.

pandas' migration guidance states that Copy-on-Write is the default and only mode in pandas 3.0. 

---

## 48. Safe Mutation Decision Tree

```text
Do I intend to modify the parent DataFrame?
        |
       YES
        |
        v
Can I target the rows and columns in one explicit operation?
        |
       YES
        |
        v
df.loc[mask, "column"] = value


Do I instead want an independent working object?
        |
       YES
        |
        v
Consider .copy()
        |
        v
Mutate the owned object


Am I only deriving/translating data?
        |
       YES
        |
        v
Prefer returning a DataFrame


Am I converting pandas data to NumPy?
        |
       YES
        |
        v
Need to mutate the array?
        |
       YES
        |
        v
Check writeability
        |
        +--> writable and safe to mutate
        |
        +--> read-only / shared
                 |
                 v
              .copy()
```

The decision tree separates four different questions:

1. parent mutation;
2. independent ownership;
3. non-mutating transformation;
4. NumPy buffer ownership.

---

## 49. CoW Mental Model Diagram

```text
                 ┌──────────────────────┐
                 │   Parent DataFrame   │
                 └──────────┬───────────┘
                            |
                         indexing
                            |
                            v
                 ┌──────────────────────┐
                 │ Derived / Subset     │
                 └──────────┬───────────┘
                            |
                   logical independence
                            |
                         mutation
                            |
                            v
                 ┌──────────────────────┐
                 │ CoW protects the     │
                 │ other pandas object  │
                 │ and separates        │
                 │ storage when needed  │
                 └──────────────────────┘
```

This is a conceptual model.

It should **not** be interpreted as a promise about the exact storage layout of every pandas operation.

The user-facing contract is more important:

> A derived pandas object must not unexpectedly modify its source through an ordinary mutation operation.

---

## 50. Common Misconceptions

### Misconception 1 — “Every subset is physically copied immediately.”

**Correction:** CoW can defer physical copying.

### Misconception 2 — “Every subset is a view that can modify the parent.”

**Correction:** modern CoW gives derived pandas objects independent user-facing mutation semantics.

### Misconception 3 — “`.copy()` is always required.”

**Correction:** not for ordinary logical isolation under CoW.

### Misconception 4 — “`.copy()` is never required.”

**Correction:** explicit ownership and memory-lifetime decisions can justify it.

### Misconception 5 — “If I do not see a warning, the code is correct.”

**Correction:** pandas warnings are not a substitute for business-rule and ownership tests.

### Misconception 6 — “`to_numpy()` is always writable.”

**Correction:** pandas may return a read-only array when a writable view would violate CoW. 

### Misconception 7 — “CoW guarantees better performance everywhere.”

**Correction:** performance depends on workload, data layout, mutation patterns, and memory pressure.

### Misconception 8 — “`df.values` always behaves like an independent NumPy copy.”

**Correction:** conversion may expose shared storage or require coercion; inspect and copy when independent mutable storage is needed.

---

## 51. Functional-Style Transformation Connection

A non-mutating transformation can resemble:

```text
input
  ↓
transform
  ↓
transform
  ↓
output
```

For example:


```python
def standardize_status(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(
        status=lambda d: d["status"].astype("string").str.strip().str.lower()
    )

def add_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(
        revenue=lambda d: d["quantity"] * d["unit_price"]
    )

result = (
    source
    .pipe(standardize_status)
    .pipe(add_revenue)
)
```

This style helps make each function's input/output contract explicit.

Pandas is **not** a purely functional system. Direct mutation remains valid when intentional.

---

## 52. Reproducibility and Hidden Mutation

Predictable mutation matters because a hidden state change can alter what a later operation sees.

Imagine:

```text
load data
   ↓
create subset
   ↓
mutate subset
   ↓
aggregate parent
   ↓
unexpected result
```

The difficult debugging problem is often:

> “Which earlier step changed this DataFrame?”

CoW removes an entire class of accidental parent mutations from derived pandas objects. But code can still mutate the parent directly, so engineering contracts and tests remain necessary.

---

## 53. Production Incident Scenario

### Scenario

An engineer writes:


```python
active = orders[orders["status"] == "active"]
active["priority"] = "high"
```

They later expect `orders["priority"]` to contain `"high"` for active orders.

### Investigation

1. Inspect `orders`.
2. Inspect `active`.
3. Find the assignment statement.
4. Identify whether the intended owner was the parent or the subset.
5. Reproduce the operation on three rows.
6. Confirm modern CoW behavior.
7. Replace with an explicit `.loc` assignment if the parent should change.
8. Add a regression test.

### Correct parent update


```python
mask = orders["status"].eq("active")
orders.loc[mask, "priority"] = "high"
```

### Correct independent subset


```python
active = orders.loc[orders["status"].eq("active")].copy()
active["priority"] = "high"
```

The code is correct only after the ownership decision is clear.

---

## 54. `inplace=True` Under Modern CoW

`inplace=True` is especially problematic when it is called on an object derived from another pandas object.

For example:


```python
df = pd.DataFrame({"foo": [1, 2, 3]})
df["foo"].replace(1, 5, inplace=True)
```

This is another chained-operation pattern. Under CoW it does not provide a mechanism for changing the parent through the derived Series. pandas documents this as a pattern that does not work under CoW. 

Prefer a direct parent operation:


```python
df = df.replace({"foo": {1: 5}})
```

or:


```python
df["foo"] = df["foo"].replace(1, 5)
```

The larger principle is:

> **Do not use `inplace=True` as a way to hide the identity of the object being changed.**

---

## 55. `.copy()` and Deep vs Shallow Concepts

For this chapter, distinguish two ideas.

### Deep copy in tests


```python
snapshot = df.copy(deep=True)
```

This is useful when a test wants a stable comparison baseline.

### Production ownership

A production `.copy()` is a design choice about independence and memory lifetime.

Do not conclude:

> “Because my test uses `deep=True`, every production step should use `deep=True`.”

Test isolation and production memory strategy are different engineering problems.

---

## 56. NumPy Conversion and Mixed Dtypes

`to_numpy()` must sometimes find a common NumPy representation.

For example:


```python
df = pd.DataFrame(
    {
        "count": [1, 2],
        "price": [2.5, 3.5],
    }
)

arr = df.to_numpy()
print(arr)
print(arr.dtype)
```

The result may be a floating-point array because a common numeric dtype is needed.

For numeric plus datetime/object-like data:


```python
df = pd.DataFrame(
    {
        "count": [1, 2],
        "created_at": pd.date_range("2026-01-01", periods=2),
    }
)

arr = df.to_numpy()
print(arr.dtype)
```

The returned representation can differ from the column-level pandas dtypes. pandas explicitly notes that conversion can require coercion and copying. 

This matters because the NumPy array is now a different representation with its own mutability rules.

---

## 57. Ten Prediction Prompts for Review

Use these without running code first.

### Prompt 1

```python
subset = df[df["x"] > 0]
subset["y"] = 1
```

Predict parent and subset.

### Prompt 2

```python
df["y"][df["x"] > 0] = 1
```

Predict whether the parent updates under CoW.

### Prompt 3

```python
df.loc[df["x"] > 0, "y"] = 1
```

Predict which rows change.

### Prompt 4

```python
subset = df.loc[mask]
subset["new_col"] = 1
```

Predict which object receives the new column.

### Prompt 5

```python
subset = df.loc[mask].copy()
subset["y"] = 0
```

Predict parent and subset.

### Prompt 6

```python
arr = df.to_numpy()
arr.flags.writeable
```

Predict whether the result can be writable, and explain why the answer depends on representation.

### Prompt 7

```python
arr = df.to_numpy().copy()
arr[0, 0] = 9
```

Predict whether `df` changes.

### Prompt 8

```python
result = transform(df)
```

Predict whether the input changes from the function's contract.

### Prompt 9

```python
original = df.copy(deep=True)
transform(df)
pd.testing.assert_frame_equal(df, original)
```

Predict what a mutating function would cause.

### Prompt 10

```python
df["foo"].replace(1, 5, inplace=True)
```

Predict the modern CoW behavior and identify the migration pattern.

Use:

> **Predict → Execute → Inspect → Assert → Explain**

---

## 58. Reusable Ownership Contract Template

```text
Function/API:
  _______________________________

Input:
  _______________________________

Output:
  _______________________________

Does input mutate?
  yes / no

If yes:
  which columns / rows?

If no:
  how is this tested?

Ownership boundary:
  _______________________________

`.copy()` reason, if any:
  _______________________________

NumPy conversion:
  _______________________________

Writeability requirement:
  _______________________________

Invariants:
  _______________________________

Regression tests:
  _______________________________
```

This turns an implicit assumption into a reviewable contract.

---

## 59. Production Style Guide

### Prefer


```python
def normalize_orders(df: pd.DataFrame) -> pd.DataFrame:
    result = df.assign(
        status=lambda d: d["status"].astype("string").str.strip()
    )
    return result
```

### Prefer direct parent mutation


```python
mask = df["amount"].lt(0)
df.loc[mask, "amount"] = pd.NA
```

### Prefer explicit independent ownership


```python
work = df.loc[df["status"].eq("active")].copy()
```

### Avoid


```python
df[df["amount"] < 0]["amount"] = 0
```

### Avoid


```python
df["amount"][df["amount"] < 0] = 0
```

### Avoid


```python
df["amount"].replace(-1, 0, inplace=True)
```

The style guide is not “never mutate.” It is “never make mutation ownership accidental.”

---

## 60. Final Hands-On Workflow

The complete `cow_lab.py` exercise should be run in this order:

```text
1. Reproduce chained assignment
        ↓
2. Observe parent remains unchanged
        ↓
3. Fix with .loc
        ↓
4. Modify a filtered subset
        ↓
5. Explain subset independence
        ↓
6. Inspect to_numpy() writeability
        ↓
7. Copy NumPy array before mutation
        ↓
8. Build input immutability test
        ↓
9. Refactor inplace-heavy code
        ↓
10. Remove unjustified copies
        ↓
11. Measure memory
        ↓
12. Add regression tests
        ↓
13. Document ownership
```

---

## 61. Checkpoint — Roadmap Requirements

### Required checkpoint

#### 1. Explain Copy-on-Write in two sentences.

A strong answer:

> Copy-on-Write gives derived pandas objects independent user-facing mutation semantics. Physical data copying can be deferred until a write requires separation.

#### 2. Explain why chained assignment does not update the parent under CoW.

A strong answer:

> Chained assignment mutates an intermediate object produced by indexing. Under CoW, that intermediate behaves independently, so the statement cannot update the original pandas object. pandas surfaces the operation with a `ChainedAssignmentError` warning. 

#### 3. Write every conditional assignment as a single `.loc` call.

Example:


```python
mask = df["amount"] > 1000
df.loc[mask, "flag"] = True
```

#### 4. Prove that a function does not mutate its input.

Use a deep-copy snapshot:


```python
original = df.copy(deep=True)

result = transform(df)

pd.testing.assert_frame_equal(df, original)
```

### Advanced self-check

Answer these without looking at the previous sections:

1. What is the difference between logical and physical independence?
2. Why does CoW reduce the need for defensive copies?
3. Why is `.copy()` still useful?
4. What is the large-parent/small-subset memory scenario?
5. Why can `to_numpy()` be read-only?
6. Why should a NumPy array sometimes be copied before mutation?
7. What is the difference between `SettingWithCopyWarning` and `ChainedAssignmentError`?
8. How would you migrate code that relied on view mutation?
9. How would you test an input-immutability contract?
10. Why is “copy everything” a poor engineering policy?
11. Why is “never copy” also a poor policy?
12. Why is CoW not a guaranteed performance optimization?

---

## 62. Cheat Sheet

### Dangerous chained assignment


```python
df["y"][mask] = value
```

### Another dangerous form


```python
df[mask]["y"] = value
```

### Correct direct assignment


```python
df.loc[mask, "y"] = value
```

### Derived object


```python
subset = df[df["x"] > 0]
```

### Explicit independent copy


```python
subset = df.loc[mask].copy()
```

### NumPy conversion


```python
arr = df.to_numpy()
```

### Check writeability


```python
arr.flags.writeable
```

### Independent NumPy array


```python
arr = df.to_numpy().copy()
```

### Input immutability test


```python
original = df.copy(deep=True)
result = transform(df)
pd.testing.assert_frame_equal(df, original)
```

### Core rules

```text
CoW
→ derived pandas objects behave independently
→ physical separation can be deferred

Conditional mutation
→ use one explicit .loc operation

.copy()
→ intentional ownership / isolation / memory-lifetime decision

NumPy
→ inspect writeability
→ copy before mutation when independent storage is required

Functions
→ prefer non-mutating transformations when practical

Tests
→ prove the function's input contract
```

---

## 63. Production Checklist

### Mutation and ownership

- [ ] No chained assignment.
- [ ] Conditional updates use `.loc`.
- [ ] Intended owner is clear.
- [ ] Derived-object mutation is not expected to update a parent.
- [ ] `.copy()` has an explicit reason.
- [ ] Legacy view-dependent behavior has been removed.

### Testing

- [ ] Input immutability is tested where required.
- [ ] Intended parent mutations are tested.
- [ ] Subset independence is tested.
- [ ] NumPy writeability behavior is tested where relevant.
- [ ] Regression tests cover migrated legacy code.
- [ ] Edge cases are covered.

### NumPy

- [ ] `to_numpy()` conversion is intentional.
- [ ] `flags.writeable` is checked when needed.
- [ ] Mutable independent arrays use `.copy()` where required.

### Memory and performance

- [ ] Large copies are measured.
- [ ] `memory_usage(deep=True)` is used for DataFrame-level inspection.
- [ ] Process peak memory is considered when needed.
- [ ] Runtime claims are benchmarked.
- [ ] CoW is not treated as a universal optimization.

### Version migration

- [ ] pandas 1.x/2.x view/copy assumptions have been reviewed.
- [ ] `SettingWithCopyWarning`-driven patterns have been migrated.
- [ ] `ChainedAssignmentError` is understood.
- [ ] Tests run against the target pandas 3.x version.

---

## 64. Learning Order

Follow this progression exactly.

### Basic

1. Why mutation semantics matter
2. Parent DataFrame and subset
3. Aliasing
4. View vs copy
5. Chained assignment
6. `df["col"][mask] = value`
7. `df[mask]["col"] = value`
8. Correct `.loc` assignment
9. Conditional assignment

### Intermediate

10. Copy-on-Write
11. Logical independence vs physical storage sharing
12. Deferred physical copying
13. Why CoW reduces defensive copies
14. pandas 1.x/2.x legacy behavior
15. `SettingWithCopyWarning`
16. `ChainedAssignmentError`
17. Legacy migration
18. Code that relied on views
19. `.copy()` use cases
20. Ownership boundaries

### Advanced

21. CoW performance
22. CoW memory behavior
23. Lazy copies
24. Avoiding unnecessary copies
25. NumPy interoperability
26. `to_numpy()`
27. `.values`
28. Read-only arrays
29. Copy before NumPy mutation
30. Non-mutating functions
31. Input immutability
32. Deep-copy test strategy
33. Memory measurement
34. Migration strategy
35. Production ownership design

Then:

36. Ten experiments
37. Legacy migration exercise
38. `cow_lab.py`
39. Debugging
40. Testing
41. Edge cases
42. Performance
43. Code review
44. Checkpoint
45. Common mistakes
46. Cheat sheet

---

## 65. Common Mistakes Summary

| Mistake | Why it happens | Correct approach |
| --- | --- | --- |
| `df["col"][mask] = value` | It looks compact | Use `df.loc[mask, "col"] = value` |
| `df[mask]["col"] = value` | Reads like “filter then assign” | Perform one explicit parent selection with `.loc` |
| Assuming subset mutation changes the parent | Legacy view behavior is remembered | Treat derived objects as independent under modern CoW |
| Trusting old Stack Overflow answers | The source targets an older pandas model | Check the target version and migrate to current semantics |
| Expecting `SettingWithCopyWarning` in pandas 3.x | Historical terminology is still common | Understand `ChainedAssignmentError` as the modern signal |
| Ignoring `ChainedAssignmentError` | Warning is treated as cosmetic | Rewrite the operation |
| Sprinkling `.copy()` everywhere | Fear of hidden aliasing | Copy only for an explicit ownership/memory/test reason |
| Never using `.copy()` | Overcorrecting for CoW | Use it at deliberate ownership boundaries |
| Assuming every copy happens immediately | “Copy-on-Write” is misread as eager copy | Separate logical behavior from physical allocation |
| Assuming no copy ever happens | CoW is mistaken for zero-copy | Understand that writes can trigger separation |
| Assuming `to_numpy()` is always writable | NumPy arrays are assumed mutable | Check `flags.writeable` |
| Assuming `.values` is always writable | Old code often does this | Prefer `to_numpy()` and inspect mutability |
| Mutating a read-only NumPy result | Pandas protected shared storage | Use `.to_numpy().copy()` when independent mutation is needed |
| Hidden function mutation | Mutation is convenient to write | Prefer non-mutating transformation functions when practical |
| Testing only output | Input side effects are ignored | Compare input with a deep-copy snapshot |
| Deep-copying huge fixtures | Unit isolation is confused with scale testing | Keep unit fixtures small; benchmark large data separately |
| Preserving accidental aliasing during migration | Old code “worked” accidentally | Preserve business intent, not implementation accidents |
| Treating CoW as guaranteed faster | Fewer eager copies sounds like guaranteed speed | Benchmark actual workloads |
| Treating `memory_usage()` as process memory | DataFrame memory is mistaken for RSS | Use it as DataFrame accounting and profile process memory separately |

---

## 66. Production Review Questions

Before merging pandas code, ask:

### Ownership

- Which object is the owner of each intended mutation?
- Is that owner explicit in the assignment?
- Could a reviewer misunderstand which object changes?

### Chained assignment

- Is there any `df["col"][mask] = ...`?
- Is there any `df[mask]["col"] = ...`?
- Is any derived Series being mutated in an attempt to update a parent?

### `.copy()`

- Why is this copy present?
- Is it required for correctness, ownership clarity, test isolation, or memory lifetime?
- Could it be removed without changing the contract?

### Functions

- Does this transformation mutate its input?
- Is that behavior documented?
- Can the function be tested as an independent transformation?

### NumPy

- Is a NumPy conversion happening?
- Does downstream code require writable storage?
- Has `flags.writeable` been considered?
- Should the array be copied?

### Tests

- Is the intended mutation tested?
- Is unintended mutation tested?
- Are edge cases included?
- Is there a regression test for any migrated legacy behavior?

---

## 67. Final Roadmap Coverage Checklist

### Basics

- [x] Parent/subset problem
- [x] `subset = df[df.x > 0]`
- [x] `subset["y"] = 1`
- [x] Parent remains unchanged under modern CoW
- [x] Chained assignment
- [x] `df["col"][mask] = value`
- [x] `df[mask]["col"] = value`
- [x] Correct `.loc`
- [x] `df.loc[mask, "col"] = value`

### Intermediate

- [x] Copy-on-Write
- [x] Derived pandas objects behave like copies from the user perspective
- [x] Physical copying may be deferred
- [x] Hidden aliasing
- [x] Fewer unnecessary defensive copies
- [x] pandas 1.x/2.x legacy behavior
- [x] `SettingWithCopyWarning`
- [x] `ChainedAssignmentError`
- [x] Legacy migration
- [x] Code relying on views
- [x] `.copy()` at function boundaries
- [x] Large-parent/small-subset memory scenario

### Advanced

- [x] CoW performance
- [x] Avoiding unnecessary copies
- [x] Lazy/deferred copies
- [x] NumPy interoperability
- [x] `df.to_numpy()`
- [x] `.values`
- [x] Read-only NumPy arrays
- [x] Copy before NumPy mutation
- [x] Non-mutating transformation functions
- [x] Deep-copy input tests
- [x] Memory measurement

### Required exercises

- [x] Ten small parent/subset/array experiments
- [x] Prediction-first workflow
- [x] Legacy migration exercise
- [x] Three or more migration examples
- [x] `cow_lab.py`
- [x] Reproduce chained assignment
- [x] `.loc` fix
- [x] Filtered subset independence
- [x] NumPy read-only experiment
- [x] NumPy copy-before-mutation
- [x] pytest fixture
- [x] Input immutability helper
- [x] `inplace=True` refactor
- [x] Unnecessary `.copy()` refactor
- [x] Memory before/after experiment
- [x] No fabricated benchmark numbers

### Quality

- [x] Debugging
- [x] Testing
- [x] Edge cases
- [x] Performance
- [x] Memory reasoning
- [x] Production use cases
- [x] Incident scenario
- [x] Migration checklist
- [x] Code-review checklist
- [x] Ownership contract
- [x] Decision tree
- [x] Common misconceptions
- [x] Checkpoint
- [x] Cheat sheet
- [x] Production checklist
- [x] Common mistakes summary

---

## 68. Technical Accuracy Rules

This chapter intentionally avoids universal claims.

### Do not say

```text
Every indexing result is physically copied immediately.
```

### Prefer

```text
Derived pandas objects behave independently from the parent's perspective;
physical copying may be deferred.
```

### Do not say

```text
Every indexing result shares physical storage.
```

### Prefer

```text
Physical sharing is an implementation detail and depends on the operation
and representation.
```

### Do not say

```text
.copy() is always necessary.
```

### Prefer

```text
Use .copy() when independent ownership, isolation, testing, or memory
lifetime is part of the design.
```

### Do not say

```text
.copy() is never necessary with CoW.
```

### Prefer

```text
CoW removes many defensive-copy requirements, but deliberate copies remain
useful.
```

### Do not say

```text
CoW always improves performance.
```

### Prefer

```text
CoW can reduce unnecessary eager copying; measure the workload.
```

### Do not say

```text
to_numpy() is always writable.
```

### Prefer

```text
to_numpy() may return a read-only array when protecting shared pandas data;
check writeability when mutation matters.
```

### Do not say

```text
method chaining improves performance automatically.
```

### Prefer

```text
Method chaining primarily improves composition and readability; runtime
depends on the operations performed.
```

---

## 69. Current pandas Documentation Notes

The chapter's version-sensitive statements are aligned with the current pandas documentation consulted for this topic.

- The pandas 3.0 Copy-on-Write user guide states that CoW is the default and only mode, makes derived objects behave like copies, and delays copies where possible. 
- The pandas 3.0.6 `ChainedAssignmentError` documentation states that chained assignment can never update the original Series/DataFrame under CoW. 
- The pandas `to_numpy()` documentation states that `copy=False` does not guarantee that no copy is made, while `copy=True` ensures a copy. 
- The pandas CoW guide documents read-only NumPy arrays as a protection against mutating pandas-owned data through the returned array. 
- pandas 3.0 release documentation describes the user-facing copy/view behavior as consistent: indexing results and methods returning pandas objects behave as copies. 

---

## 70. Final Mental Model

When you see a pandas operation, stop and ask:

```text
What object do I have?
        ↓
Was it derived from another object?
        ↓
What object do I intend to mutate?
        ↓
Can I target that object explicitly?
        ↓
Am I using chained assignment?
        |
        +--> YES → rewrite with .loc
        |
        +--> NO
              ↓
       Is independent ownership required?
              |
              +--> YES → consider .copy()
              |
              +--> NO
                    ↓
             continue with CoW semantics
```

For NumPy:

```text
pandas DataFrame
      ↓
  to_numpy()
      ↓
Is the array writable?
      |
      +--> YES → verify ownership before mutation
      |
      +--> NO
            ↓
       .copy()
            ↓
    independently mutable array
```

For functions:

```text
Input DataFrame
      ↓
transform
      ↓
Does input change?
      |
      +--> NO → easy to compose and test
      |
      +--> YES → document and test intentional mutation
```

The mature pandas engineer does not memorize view/copy folklore.

The mature engineer can state:

> **Who owns the state, what should change, what must not change, and what test proves that contract?**
