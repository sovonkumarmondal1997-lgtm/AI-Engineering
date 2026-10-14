---
title: "Property-Based Testing with Hypothesis"
module: "Stage 2 — Python for Data Engineering"
topic: "2.19.04"
filename: "04-property-based-testing-with-hypothesis.md"
level: "Beginner → Intermediate → Advanced → Production"
stack: "Python 3.12+, uv, pytest, Hypothesis, pandas, Polars, DuckDB, PySpark where relevant"
---

# 04 — Property-Based Testing with Hypothesis

> **Production principle:** Example-based tests prove that selected examples work. Property-based tests prove that a behavior remains correct across a large, systematically generated space of valid and invalid inputs.

This module teaches **property-based testing with Hypothesis** as a production technique for Data Engineering. The focus is not on generating random data for its own sake. The focus is on expressing **properties, invariants, and contracts** that must remain true across many possible inputs.

The progression is:

```text
Example-based testing
        ↓
Property-based testing mental model
        ↓
Hypothesis strategies
        ↓
Generated records and DataFrames
        ↓
Invariants and transformation properties
        ↓
Shrinking and minimal counterexamples
        ↓
Edge cases and invalid data
        ↓
Metamorphic / differential properties
        ↓
Stateful pipeline behavior
        ↓
Database + serialization properties
        ↓
CI + debugging + reproducibility
        ↓
Production-grade property testing
```

## Learning Outcomes

By the end of this module, you should be able to:

- explain the difference between examples and properties;
- identify behaviors that are suitable for property-based testing;
- install and configure Hypothesis with pytest;
- compose Hypothesis strategies;
- generate valid and deliberately invalid records;
- generate DataFrames without creating meaningless random noise;
- express invariants for transformations and pipelines;
- test idempotency, ordering, conservation, uniqueness, and schema properties;
- understand shrinking and use minimal counterexamples to debug defects;
- reproduce a failing Hypothesis example;
- test nulls, duplicates, empty inputs, extreme values, Unicode, timestamps, time zones, and decimals;
- test serialization/deserialization round trips;
- use metamorphic and differential testing where a direct oracle is difficult;
- reason about stateful workflows and rule-based state machines where appropriate;
- use Hypothesis safely in CI without turning the suite into a performance problem;
- distinguish useful properties from weak or tautological assertions;
- build a production-oriented property-based testing project.

---

## 1. Example-Based Testing vs Property-Based Testing

An example-based test says:

```text
For this input:
    [specific rows]

I expect:
    [specific output]
```

A property-based test says:

```text
For every valid input satisfying these assumptions:
    the system must preserve this invariant.
```

### Example

Suppose a transformation removes cancelled orders.

An example test might be:

```python
def test_removes_cancelled_orders():
    rows = [
        {"order_id": 1, "status": "paid"},
        {"order_id": 2, "status": "cancelled"},
    ]

    result = remove_cancelled(rows)

    assert result == [
        {"order_id": 1, "status": "paid"},
    ]
```

A property can be stronger:

```python
@given(orders=order_strategy())
def test_result_contains_no_cancelled_orders(orders):
    result = remove_cancelled(orders)

    assert all(row["status"] != "cancelled" for row in result)
```

The generated input space can contain:

- zero rows;
- one row;
- many rows;
- repeated IDs;
- Unicode values;
- unusual amounts;
- many cancelled records;
- no cancelled records.

The test does not need to enumerate those examples manually.

### The key distinction

```text
Example-based:
    "Does this known case work?"

Property-based:
    "What must always be true?"
```

Both belong in a production test suite.


## 2. What Makes a Good Property?

A good property describes behavior that must remain true regardless of the specific generated input.

Useful categories include:

### Validity

```text
Output contains no records violating the contract.
```

### Conservation

```text
Every input record that should survive still exists.
```

### Idempotency

```text
f(f(x)) == f(x)
```

### Round trip

```text
decode(encode(x)) == x
```

### Monotonicity

```text
Increasing an input quantity must not decrease a derived quantity.
```

### Ordering

```text
Output is sorted by the declared ordering key.
```

### Uniqueness

```text
Primary-key output is unique.
```

### Schema stability

```text
Every output row satisfies the declared schema.
```

### Partition invariance

When a transformation is designed to be independent of batch boundaries:

```text
f(batch1 + batch2) == combine(f(batch1), f(batch2))
```

The exact property depends on the transformation. Do not assert partition invariance for operations whose semantics genuinely depend on global ordering or global state.

### Why this matters

A property is an executable statement of a business or engineering invariant.

That makes property-based testing especially valuable for pipelines because many pipeline requirements are naturally expressed as invariants.


## 3. Hypothesis Mental Model

Hypothesis has four important ideas:

```text
Strategy
   ↓
Generated example
   ↓
Property execution
   ↓
Failure
   ↓
Shrinking
   ↓
Minimal counterexample
```

A strategy describes **how valid test inputs can be generated**.

A property is the assertion about those inputs.

When Hypothesis finds a failure, it attempts to shrink the input toward a smaller example that still fails.

That last step is one of Hypothesis's most valuable features for Data Engineering: large randomly generated datasets can be reduced to a tiny counterexample that reveals the defect.

---

## 4. Installation and Setup

Install Hypothesis as a development dependency:

```bash
uv add --dev hypothesis pytest
```

Run the suite with:

```bash
pytest
```

A minimal test:

```python
from hypothesis import given
from hypothesis import strategies as st


@given(st.integers())
def test_absolute_value_is_non_negative(value: int) -> None:
    assert abs(value) >= 0
```

Hypothesis generates many integers automatically.

### Configuration

Keep repository-wide configuration explicit. A `pyproject.toml` may contain pytest settings, while Hypothesis settings can be defined near tests or through a project-wide profile.

Example:

```python
from hypothesis import settings

settings.register_profile(
    "ci",
    max_examples=100,
)

settings.load_profile("ci")
```

Do not blindly copy a large `max_examples` value into every test. The correct value depends on the cost of the system under test.

---

## 5. Strategies — The Input Generation Language

Hypothesis strategies define the input domain.

Common strategies include:

```python
from hypothesis import strategies as st

st.integers()
st.floats(allow_nan=False, allow_infinity=False)
st.text()
st.booleans()
st.dates()
st.datetimes()
st.decimals()
st.lists(st.integers())
st.sets(st.text())
st.dictionaries(st.text(), st.integers())
```

### Constrained values

Production tests should usually constrain the domain deliberately.

```python
amounts = st.decimals(
    min_value="0.00",
    max_value="1000000.00",
    places=2,
    allow_nan=False,
    allow_infinity=False,
)
```

This is better than generating arbitrary floating-point values if the business domain is money represented with decimal precision.

### Strategy principle

Do not ask:

> “What random data can I generate?”

Ask:

> “What inputs are valid for this contract, and what edge cases are important inside that domain?”


## 6. Compositional Strategies

Real pipeline records are structured objects.

Use `st.builds()` or `st.fixed_dictionaries()` to compose smaller strategies.

```python
from dataclasses import dataclass
from hypothesis import strategies as st


@dataclass
class Order:
    order_id: int
    amount: int
    status: str


order_strategy = st.builds(
    Order,
    order_id=st.integers(min_value=1, max_value=1_000_000),
    amount=st.integers(min_value=0, max_value=1_000_000),
    status=st.sampled_from(["pending", "paid", "cancelled"]),
)
```

Then:

```python
@given(order=order_strategy)
def test_order_amount_is_non_negative(order: Order) -> None:
    assert order.amount >= 0
```

### Structured records

For dictionary-based pipeline inputs:

```python
order_dicts = st.fixed_dictionaries(
    {
        "order_id": st.integers(min_value=1, max_value=1_000_000),
        "amount": st.integers(min_value=0, max_value=1_000_000),
        "status": st.sampled_from(
            ["pending", "paid", "cancelled"]
        ),
    }
)
```

Composition makes the generated domain explicit and reviewable.

---

## 7. Generating Data Engineering Datasets

Property tests become useful when generated datasets resemble the **shape and semantics** of production data.

Start with row strategies:

```python
order_row = st.fixed_dictionaries(
    {
        "order_id": st.integers(min_value=1, max_value=1000),
        "amount": st.decimals(
            min_value="0.00",
            max_value="100000.00",
            places=2,
        ),
        "status": st.sampled_from(
            ["pending", "paid", "cancelled"]
        ),
    }
)
```

Then generate collections:

```python
orders = st.lists(
    order_row,
    min_size=0,
    max_size=100,
)
```

This deliberately allows the empty dataset.

### Duplicate-heavy datasets

Do not accidentally exclude duplicates when duplicates are part of the production risk:

```python
order_ids = st.lists(
    st.integers(min_value=1, max_value=10),
    min_size=0,
    max_size=100,
)
```

The small ID domain intentionally creates collisions.

This is often more valuable than generating one hundred uniformly unique IDs.

---

## 8. DataFrame Strategies

Hypothesis does not automatically understand the semantics of your pipeline. You must construct DataFrames from meaningful strategies.

Example:

```python
import pandas as pd
from hypothesis import given, strategies as st


@st.composite
def order_frames(draw):
    rows = draw(
        st.lists(
            st.fixed_dictionaries(
                {
                    "order_id": st.integers(
                        min_value=1,
                        max_value=100,
                    ),
                    "amount": st.decimals(
                        min_value="0.00",
                        max_value="10000.00",
                        places=2,
                    ),
                    "status": st.sampled_from(
                        ["paid", "cancelled"]
                    ),
                }
            ),
            max_size=50,
        )
    )

    return pd.DataFrame(rows)


@given(frame=order_frames())
def test_filter_never_returns_cancelled(frame):
    result = frame.loc[
        frame["status"].eq("paid")
    ]

    assert not (result["status"] == "cancelled").any()
```

### Important design principle

Generated DataFrames should target the **risk surface**.

If the defect concerns:

- duplicate keys → generate duplicates;
- null handling → generate nulls;
- date boundaries → generate boundary dates;
- decimal rounding → generate values near rounding thresholds;
- Unicode → generate non-ASCII text;
- empty input → allow zero rows.

Randomness without a risk model produces noise, not high-value tests.


## 9. `assume()` — Filtering Generated Examples

Sometimes a generated value is syntactically valid but outside the scenario under test.

Hypothesis provides `assume()`:

```python
from hypothesis import assume, given
from hypothesis import strategies as st


@given(
    numerator=st.integers(),
    denominator=st.integers(),
)
def test_ratio_property(numerator, denominator):
    assume(denominator != 0)

    result = numerator / denominator

    assert result * denominator == numerator
```

Use `assume()` carefully.

### Why excessive `assume()` is a problem

Suppose the strategy generates mostly invalid values and the test discards almost all of them:

```text
generate
  ↓
reject
  ↓
generate
  ↓
reject
  ↓
generate
  ↓
reject
```

The test becomes inefficient and may hit Hypothesis health limits.

Prefer constructing a strategy that generates the desired domain directly.

Instead of:

```python
values = st.integers()
assume(value > 0)
```

prefer:

```python
values = st.integers(min_value=1)
```

### Rule

> Use strategy constraints to define the domain; use `assume()` for relationships that are awkward or expensive to encode directly.


## 10. Shrinking — The Most Important Debugging Feature

Suppose a property fails on a large generated dataset:

```text
500 rows
12 duplicate keys
17 null values
9 unusual Unicode strings
3 extreme amounts
```

Hypothesis attempts to shrink it.

The final failure might become:

```text
2 rows
same key
one null
```

That minimal counterexample is much easier to understand.

### Conceptual process

```text
Generated example
        ↓
Property fails
        ↓
Remove data
        ↓
Simplify values
        ↓
Reduce collection size
        ↓
Keep checking failure
        ↓
Minimal counterexample
```

### Example

```python
@given(values=st.lists(st.integers(), min_size=1))
def test_sorted(values):
    result = sorted(values)

    assert result == values
```

The property is intentionally wrong. Hypothesis will reduce the failing input to a small example that demonstrates that the original list was not sorted.

### Engineering lesson

Do not fear shrinking. A small counterexample is often the fastest route from:

```text
"CI found a random failure"
```

to:

```text
"the defect is caused by this exact two-value input."
```


## 11. Reproducing a Hypothesis Failure

A property-based test is only useful if a developer can reproduce its failure.

When Hypothesis reports a failing example, capture the minimal input from the test output.

Typical workflow:

```text
CI failure
   ↓
copy failing example
   ↓
re-run targeted test
   ↓
debug implementation
   ↓
add explicit regression test if useful
   ↓
keep property test
```

A property test should not be replaced by an example regression test automatically. The property explains the broader rule; the regression example documents a particularly important discovered case.

### Determinism

Hypothesis is designed to reproduce failures. Do not undermine that by injecting unrelated randomness into the test:

```python
import random
random.random()
```

Prefer Hypothesis-generated values.

If the system under test uses randomness, inject a deterministic random source or seed through the application's dependency boundary where the contract allows it.


## 12. Testing Invariants

An invariant is something that must remain true after a transformation.

### Example: row-level validity

```python
@given(frame=order_frames())
def test_paid_orders_have_non_negative_amount(frame):
    result = transform(frame)

    assert (result["amount"] >= 0).all()
```

### Example: uniqueness

```python
@given(frame=order_frames())
def test_output_keys_are_unique(frame):
    result = deduplicate(frame)

    assert result["order_id"].is_unique
```

### Example: no unexpected rows

```python
@given(frame=order_frames())
def test_filter_only_removes_cancelled(frame):
    result = remove_cancelled(frame)

    assert set(result["order_id"]) <= set(frame["order_id"])
```

Be careful with sets if duplicate multiplicity is meaningful. For multiset semantics, compare counts rather than membership alone.

### Invariant quality

A useful invariant is:

- derived from the business contract;
- independent of one particular implementation;
- strong enough to detect defects;
- not so broad that it passes incorrect outputs.


## 13. Idempotency Properties

Idempotency is one of the highest-value properties in Data Engineering.

For an idempotent operation:

```text
f(f(x)) = f(x)
```

Example:

```python
@given(frame=order_frames())
def test_normalization_is_idempotent(frame):
    once = normalize_orders(frame)
    twice = normalize_orders(once)

    assert_frame_equal(once, twice)
```

Typical candidates:

- normalization;
- canonicalization;
- deduplication;
- cleanup;
- schema normalization;
- certain merge operations.

Do not assert idempotency for operations that are intentionally accumulative, such as:

```text
append_event(x)
```

The property must reflect the actual contract.


## 14. Commutativity and Associativity

Some data transformations should not depend on processing order or partitioning.

### Commutativity

For an operation `f` over two inputs:

```text
combine(a, b) == combine(b, a)
```

For example, a set-like aggregation may be commutative.

### Associativity

```text
combine(combine(a, b), c)
==
combine(a, combine(b, c))
```

This is particularly relevant to distributed processing.

### Warning

Do not force these properties onto operations where ordering is semantically meaningful.

For example:

```text
first_event
```

is not generally commutative.

The property must follow the intended semantics, not a mathematical preference.


## 15. Partition and Batch-Invariance Properties

Distributed pipelines frequently process data in batches or partitions.

A transformation may be expected to produce the same logical result whether the input arrives as:

```text
one batch
```

or:

```text
batch A + batch B
```

For an appropriate operation:

```python
@given(
    left=st.lists(order_row, max_size=20),
    right=st.lists(order_row, max_size=20),
)
def test_batch_partition_invariance(left, right):
    whole = transform(left + right)

    separate = combine(
        transform(left),
        transform(right),
    )

    assert equivalent(whole, separate)
```

This property is powerful for distributed systems because it tests an important assumption:

> Processing boundaries should not change the logical result when the transformation is designed to be partition-independent.

Do not use this property for operations that depend on global ordering, cross-batch windows, or state that intentionally spans batches.


## 16. Monotonicity and Conservation

### Monotonicity

If increasing an input cannot decrease an output metric, test that relationship.

Example:

```python
@given(
    base=st.integers(min_value=0, max_value=1000),
    extra=st.integers(min_value=0, max_value=1000),
)
def test_total_is_monotonic(base, extra):
    assert total(base + extra) >= total(base)
```

### Conservation

If a transformation partitions data into categories without dropping records:

```text
input_count == sum(output_partition_counts)
```

Example:

```python
@given(frame=order_frames())
def test_partitioning_conserves_rows(frame):
    partitions = partition_orders(frame)

    assert sum(len(part) for part in partitions) == len(frame)
```

If deduplication intentionally removes records, the conservation property must be changed to the correct business invariant.


## 17. Schema and Type Properties

Data pipelines must preserve or intentionally transform schemas.

Useful properties include:

```text
required columns exist
required columns have expected types
primary key is non-null
enumerated fields stay inside the allowed domain
decimal precision is preserved
timestamps are timezone-aware where required
```

Example:

```python
@given(frame=order_frames())
def test_output_has_required_columns(frame):
    result = transform(frame)

    assert {"order_id", "amount", "status"} <= set(result.columns)
```

For stronger type checks:

```python
assert str(result["status"].dtype) == "object"
```

or use the framework's schema tooling where available.

Do not assert implementation-specific dtypes if the contract intentionally allows multiple equivalent representations. Test the contract, not accidental internal details.


## 18. Nulls, Duplicates, and Empty Inputs

Property-based testing is excellent for systematically exercising edge conditions.

### Empty

```python
empty_frames = st.just(
    pd.DataFrame(
        columns=["order_id", "amount", "status"]
    )
)
```

Also let general list strategies generate zero rows naturally.

### Duplicates

Use a deliberately small key domain:

```python
duplicate_ids = st.lists(
    st.integers(min_value=1, max_value=5),
    max_size=100,
)
```

### Nulls

Build optional values:

```python
nullable_amount = st.one_of(
    st.none(),
    st.decimals(
        min_value="0.00",
        max_value="10000.00",
        places=2,
    ),
)
```

### Why this matters

Many production pipeline defects hide in:

```text
empty input
null key
duplicate key
all-null column
single row
single distinct value
```

These cases should be deliberately represented in generated data.


## 19. Extreme Numeric Values and Decimals

Numeric edge cases include:

- zero;
- negative values where allowed;
- very large values;
- values near thresholds;
- decimal rounding boundaries;
- integer overflow boundaries;
- `NaN` and infinity where the domain permits them.

For financial data, prefer domain-appropriate decimal strategies:

```python
money = st.decimals(
    min_value="-1000000.00",
    max_value="1000000.00",
    places=2,
    allow_nan=False,
    allow_infinity=False,
)
```

Avoid unrestricted floating-point generation when the business contract is defined in decimal currency units.

A useful property is:

```text
round_trip(decimal_value) == decimal_value
```

when the serialization format supports the declared precision.

If the system intentionally rounds to cents, test the documented rounding rule instead of asserting exact identity.


## 20. Unicode and Text Edge Cases

Text properties should not assume ASCII.

Generate:

- accented characters;
- non-Latin scripts;
- combining characters;
- emoji;
- whitespace;
- empty strings;
- long strings.

Example:

```python
text_values = st.text(
    min_size=0,
    max_size=200,
)
```

A transformation that trims whitespace might have:

```python
@given(value=text_values)
def test_trimmed_output_has_no_outer_whitespace(value):
    result = normalize_text(value)

    assert result == result.strip()
```

Be careful: Unicode normalization and visible characters are different concepts. If the application contract requires Unicode normalization, test the specific normalization form explicitly.


## 21. Dates, Timestamps, Time Zones, and Boundaries

Generate temporal values intentionally.

Important boundaries include:

```text
midnight
month end
year end
leap day
DST transition
timezone conversion
UTC/local representation
```

Hypothesis:

```python
timestamps = st.datetimes(
    min_value=datetime(2020, 1, 1),
    max_value=datetime(2030, 12, 31),
    timezones=st.timezones(),
)
```

A property should distinguish:

```text
same instant
```

from:

```text
same textual representation
```

For example, two timezone-aware timestamps may represent the same instant while displaying different local times.

Do not compare timestamp strings if the actual contract is about temporal instants.


## 22. Round-Trip Serialization Properties

Round-trip properties are ideal for data engineering.

The general form is:

```text
decode(encode(x)) == x
```

Examples:

- JSON;
- CSV where the schema permits lossless representation;
- Parquet;
- Avro/Protobuf;
- database serialization;
- configuration formats.

Example:

```python
@given(record=order_strategy)
def test_json_round_trip(record):
    encoded = encode_order(record)
    restored = decode_order(encoded)

    assert restored == record
```

For formats that intentionally transform representation, assert semantic equivalence rather than byte-for-byte equality.

For example:

```text
DataFrame → Parquet → DataFrame
```

should generally be compared according to the declared schema and semantic values.


## 23. Metamorphic Testing

Sometimes the correct output for a generated input is difficult to calculate directly.

Metamorphic testing solves this by asserting how the output should change when the input is transformed.

### Example

Suppose sorting an input should not change the result of a set-like aggregation:

```python
@given(frame=order_frames())
def test_sorting_input_does_not_change_total(frame):
    result_a = aggregate(frame)
    result_b = aggregate(
        frame.sort_values("order_id")
    )

    assert_equivalent(result_a, result_b)
```

Another example:

```text
duplicate an input record
        ↓
result should increase by exactly one record
```

if and only if the operation is intentionally non-deduplicating.

### Metamorphic pattern

```text
input x
   ↓
f(x)

transform x → x'
   ↓
f(x')

assert known relationship between f(x) and f(x')
```

This is especially useful for complex transformations where constructing an exact oracle is expensive.


## 24. Differential Testing

Differential testing compares two independently implemented paths.

For example:

```text
pandas implementation
        vs
DuckDB implementation
```

or:

```text
reference implementation
        vs
optimized implementation
```

Example:

```python
@given(frame=order_frames())
def test_pandas_and_duckdb_agree(frame):
    expected = reference_transform(frame)
    actual = optimized_transform(frame)

    assert_equivalent(actual, expected)
```

The implementations must be sufficiently independent. Comparing an implementation against a near-identical copy of itself does not provide strong evidence.

Differential testing is valuable during:

- SQL engine migration;
- pandas → Polars migration;
- batch → Spark migration;
- optimized query rewrites;
- refactoring of complex transformations.


## 25. Stateful Testing

Some Data Engineering behavior is inherently stateful:

```text
event arrives
  ↓
state changes
  ↓
next event observes state
  ↓
state changes again
```

Examples include:

- deduplication state;
- incremental ingestion;
- checkpoint tracking;
- consumer offsets;
- slowly changing dimensions;
- stateful aggregations.

Hypothesis provides stateful testing facilities, including rule-based state machines.

Conceptually:

```text
initial state
   ↓
rule A
   ↓
rule B
   ↓
rule C
   ↓
invariant
```

A state-machine test should model the allowed operations rather than random method calls that violate every precondition.

### Example model

```text
insert event
update event
replay event
checkpoint
restart
```

Then assert:

```text
state remains valid
```

and:

```text
replaying an idempotent event does not corrupt state
```

Stateful testing is more advanced. Start with stateless properties and introduce state machines when the system's correctness genuinely depends on event sequences.


## 26. Database Properties

Property-based testing can generate database inputs while the real database provides the execution semantics.

Useful properties include:

### Insert/read round trip

```text
insert(records)
    ↓
select(records)
    ↓
semantic equality
```

### Uniqueness

```text
database rejects duplicate primary key
```

### Idempotent load

```text
load(x)
load(x)
```

should produce the same state when the load contract is idempotent.

### Constraint preservation

Generated invalid records should be rejected by real constraints.

### Query equivalence

Compare:

```text
SQL implementation
```

with:

```text
reference transformation
```

on generated datasets.

Keep the generated dataset bounded. A property test is not a benchmark of PostgreSQL.


## 27. Pipeline-Level Properties

Useful pipeline properties include:

### No data loss

For a pipeline whose contract is lossless:

```text
input logical records
=
output logical records
```

after accounting for documented filtering.

### No duplicate outputs

```text
output primary key is unique
```

when uniqueness is required.

### Idempotent rerun

```text
run(input)
run(input)
```

produces the same logical state as one run.

### Partition invariance

```text
run(A + B)
=
combine(run(A), run(B))
```

when the pipeline is designed for partition independence.

### Schema contract

Every output satisfies the required schema.

### Monotonic watermark

For a pipeline with a monotonic progress marker:

```text
new watermark >= previous watermark
```

These properties are often more durable than example assertions because they encode the pipeline's intended behavior.


## 28. Performance and Health Properties

Property-based testing should not become a fragile performance benchmark.

Prefer **bounded health properties**:

```text
operation terminates
output size is bounded
memory-sensitive input is handled
```

For example:

```python
@given(values=st.lists(st.integers(), max_size=1000))
def test_normalization_terminates_and_preserves_count(values):
    result = normalize(values)

    assert len(result) <= len(values)
```

Do not write:

```python
assert transform(values) < 0.010
```

unless the timing threshold is a deliberately managed performance test.

CI machines vary. Property tests should primarily prove correctness. Dedicated performance tests should measure performance.


## 29. CI Settings and Example Budgets

Hypothesis test cost depends on:

```text
strategy complexity
×
max_examples
×
system-under-test cost
```

A unit-level property can often afford many examples.

A test that starts a database transaction or runs Spark should use a much smaller, deliberately selected budget or a separate integration strategy.

Example:

```python
settings.register_profile(
    "ci",
    max_examples=50,
    deadline=None,
)
```

The exact settings should be based on observed suite behavior.

### Separate test layers

```text
fast property tests
        ↓
unit CI gate

expensive integration properties
        ↓
integration CI gate
```

Do not hide expensive external infrastructure inside every fast property test.


## 30. Debugging a Failing Property

Use this sequence:

```text
1. Capture the counterexample
2. Re-run the exact test
3. Understand the smallest failing input
4. Identify the violated invariant
5. Trace the implementation
6. Decide whether the property or implementation is wrong
7. Fix the defect
8. Add a focused regression example if valuable
9. Keep the broader property
```

### Ask five questions

1. Is the generated input actually valid?
2. Is the property mathematically/business correct?
3. Is the implementation violating the property?
4. Did the test accidentally depend on ordering, timezone, or representation?
5. Is there hidden nondeterminism outside Hypothesis?

Never “fix” a property failure by weakening the assertion without first determining why the property failed.


## 31. Common Hypothesis Mistakes

### Mistake 1 — Random data without a property

Generating random values is not property-based testing.

**Better:** start with a contract.

### Mistake 2 — Overusing `assume()`

Excessive filtering wastes generated examples.

**Better:** encode constraints in strategies.

### Mistake 3 — Weak properties

This:

```python
assert result is not None
```

may pass incorrect outputs.

**Better:** assert meaningful invariants.

### Mistake 4 — Testing implementation details

A property tied to an internal algorithm can make harmless refactoring painful.

**Better:** test externally meaningful behavior.

### Mistake 5 — Overly broad domains

Generating every possible Python value can make failures difficult to interpret.

**Better:** model the actual data contract.

### Mistake 6 — Ignoring shrinking

A large failure is often easier to understand after Hypothesis shrinks it.

### Mistake 7 — Hidden randomness

Calling unrelated random generators can reduce reproducibility.

### Mistake 8 — Excessive example counts

More examples are not automatically better. Cost must match risk.

### Mistake 9 — Treating Hypothesis as a replacement for examples

Keep important concrete regression tests alongside properties.

### Mistake 10 — Using a tautological oracle

This is weak:

```python
assert optimized(x) == optimized(x)
```

Differential testing requires independent reference behavior.


## 32. Hands-On Project — Property-Based Data Quality Lab

Build a property-based test suite for an order pipeline.

### Input contract

```text
order_id       positive integer
customer_id    positive integer
amount         decimal with 2 places
status         pending | paid | cancelled
created_at     timezone-aware timestamp
```

### Required properties

1. normalization is idempotent;
2. output order IDs remain valid;
3. deduplication produces unique keys;
4. cancellation filtering never emits cancelled rows;
5. serialization round trip preserves semantic values;
6. valid schema is preserved;
7. empty input is handled;
8. duplicate keys are handled;
9. null handling follows the contract;
10. Unicode customer metadata survives normalization;
11. decimal amounts obey the declared precision;
12. timestamp behavior is correct across time zones;
13. batch partitioning produces equivalent output where the transformation is partition-independent;
14. a deliberately introduced bug is found by Hypothesis;
15. the failure shrinks to an understandable counterexample.

### Suggested structure

```text
property-testing-lab/
├── pyproject.toml
├── src/
│   └── pipeline/
│       ├── normalize.py
│       ├── deduplicate.py
│       ├── serialize.py
│       └── aggregate.py
├── tests/
│   ├── test_examples.py
│   └── test_properties.py
└── README.md
```

### Acceptance criteria

The project is complete when the learner can explain:

```text
strategy
→ generated input
→ property
→ failure
→ shrinking
→ minimal counterexample
→ defect fix
```

and can demonstrate that a deliberate defect is automatically discovered.


## 33. Deliberate Failure Lab

Introduce bugs one at a time.

### Failure 1 — Broken deduplication

Change deduplication so one duplicate survives.

Expected property:

```text
output keys are unique
```

Hypothesis should discover an input containing the smallest useful duplicate.

### Failure 2 — Non-idempotent normalization

Make normalization append a marker every time:

```text
normalize("A") → "a!"
normalize("a!") → "a!!"
```

Expected property:

```text
normalize(normalize(x)) == normalize(x)
```

### Failure 3 — Decimal rounding defect

Introduce a floating-point conversion that changes a boundary amount.

Expected property:

```text
declared monetary precision is preserved
```

### Failure 4 — Timestamp representation bug

Introduce an incorrect timezone conversion.

Expected property:

```text
same instant remains the same instant
```

### Failure 5 — Partition-sensitive aggregation

Introduce an implementation that produces a different answer depending on how input is split.

Expected property:

```text
whole-batch result == combined partition result
```

For every failure, record:

```text
generated input
shrunk counterexample
violated property
root cause
code fix
regression example
```


## 34. Checkpoint

You should now be able to answer:

- What is a property?
- How is it different from an example?
- What is a Hypothesis strategy?
- Why compose strategies?
- How do you generate meaningful DataFrames?
- When should you use `assume()`?
- Why is excessive `assume()` harmful?
- What is shrinking?
- Why are minimal counterexamples valuable?
- How do you reproduce a Hypothesis failure?
- What is an invariant?
- What is idempotency?
- When is commutativity valid?
- When is associativity valid?
- What is partition invariance?
- What is conservation?
- What is monotonicity?
- How do you test schema properties?
- How do you generate nulls and duplicates?
- How do you test Unicode?
- How do you test time zones?
- How do you test decimals?
- What is a round-trip property?
- What is metamorphic testing?
- What is differential testing?
- When should you use stateful testing?
- How can properties be applied to databases and pipelines?
- How do you avoid brittle performance assertions?
- How do you control CI cost?
- What makes a property weak or tautological?

### Practical checkpoint

1. Write one strategy for an order.
2. Generate a DataFrame from that strategy.
3. Write an invariant.
4. Write an idempotency property.
5. Write a round-trip property.
6. Add duplicates and nulls.
7. Add a timezone-aware timestamp strategy.
8. Intentionally introduce a defect.
9. Observe Hypothesis shrink the failure.
10. Fix the defect and preserve the property.


## 35. Production Interview Preparation

### 1. What is property-based testing?

Testing a general property over many systematically generated inputs rather than asserting only a small set of manually selected examples.

### 2. Why is it useful for Data Engineering?

Data pipelines have huge input spaces and many combinations of nulls, duplicates, timestamps, schemas, values, and partitions. Properties can exercise that space efficiently.

### 3. What is a strategy?

A Hypothesis object describing how test values should be generated.

### 4. What is shrinking?

The process of simplifying a failing generated input into a smaller counterexample that still violates the property.

### 5. Why is shrinking important?

A small counterexample is easier to diagnose, reproduce, and turn into a focused regression test.

### 6. Why not generate unrestricted random data?

Unrestricted randomness may generate mostly irrelevant or invalid cases. High-value strategies model the actual contract and risk surface.

### 7. When should you use `assume()`?

For relationships or conditions that are difficult to encode directly in a strategy. Prefer strategy constraints when practical.

### 8. What is idempotency?

Applying the operation multiple times produces the same logical result as applying it once.

```text
f(f(x)) = f(x)
```

### 9. What is a metamorphic property?

A property describing how output should change when a known transformation is applied to the input.

### 10. What is differential testing?

Comparing independent implementations or execution engines and asserting semantic agreement.

### 11. What is stateful property testing?

Generating sequences of operations against a stateful system and checking invariants across the resulting states.

### 12. How do you test distributed transformations?

Use properties such as partition invariance, associativity where valid, idempotency, conservation, and differential comparisons.

### 13. How do you control CI cost?

Bound generated dataset sizes, tune `max_examples`, separate fast properties from expensive integration properties, and measure suite duration.

### 14. What makes a property weak?

It does not meaningfully constrain output, duplicates the implementation logic, or can pass obviously incorrect results.

### 15. Should property tests replace example tests?

No. They complement examples. Concrete regression tests are still useful for known production incidents and important business cases.

### 16. What is the most important design step?

Define the invariant before choosing the strategy.


## 36. Final Assessment

### Scenario

A pipeline receives orders from multiple sources and must normalize, deduplicate, serialize, and aggregate them reliably.

A previous production incident involved:

- duplicate records;
- timezone conversion errors;
- monetary rounding;
- non-idempotent normalization;
- batch-dependent aggregation.

Design a property-based test suite.

### Required implementation

```text
Hypothesis strategies
        +
generated records
        +
generated DataFrames
        +
invariants
        +
idempotency
        +
schema properties
        +
null / duplicate / empty cases
        +
decimal properties
        +
timezone properties
        +
round-trip serialization
        +
partition invariance
        +
metamorphic property
        +
differential property
        +
deliberate failure
```

### Required demonstrations

**Data generation**

- valid order strategy;
- invalid/edge-case strategy;
- duplicates;
- nulls;
- empty datasets;
- Unicode;
- timestamps;
- decimals.

**Properties**

- normalization idempotency;
- deduplication uniqueness;
- filtering correctness;
- schema validity;
- serialization round trip;
- partition invariance where valid;
- timestamp semantic correctness;
- decimal precision.

**Advanced**

- one metamorphic test;
- one differential test;
- stateful testing if the selected pipeline component has meaningful state.

**Failure**

Introduce at least two defects and demonstrate that Hypothesis finds and shrinks them.

### Assessment standard

A written explanation is insufficient. The learner must implement executable properties and demonstrate that the properties detect deliberately introduced defects.


## 37. Final Self-Review Checklist

```text
[ ] Example-based vs property-based testing
[ ] Property definition
[ ] Hypothesis installation
[ ] pytest integration
[ ] Strategies
[ ] Compositional strategies
[ ] Constrained strategies
[ ] DataFrame generation
[ ] Risk-driven data generation
[ ] assume()
[ ] Avoiding excessive assume()
[ ] Shrinking
[ ] Minimal counterexamples
[ ] Reproducibility
[ ] Invariants
[ ] Idempotency
[ ] Commutativity where valid
[ ] Associativity where valid
[ ] Partition invariance
[ ] Monotonicity
[ ] Conservation
[ ] Schema properties
[ ] Null handling
[ ] Duplicate handling
[ ] Empty inputs
[ ] Extreme numeric values
[ ] Decimal precision
[ ] Unicode
[ ] Dates
[ ] Time zones
[ ] Timestamp boundaries
[ ] Serialization round trips
[ ] Metamorphic testing
[ ] Differential testing
[ ] Stateful testing
[ ] Database properties
[ ] Pipeline properties
[ ] Performance/health properties
[ ] CI budgets
[ ] Debugging
[ ] Failure replay
[ ] Common mistakes
[ ] Hands-on project
[ ] Deliberate failure lab
[ ] Checkpoint
[ ] Interview preparation
[ ] Final assessment
[ ] Production self-review
```


## 38. Production Quality Gate

### Correctness

Every property must correspond to an actual business or engineering contract.

### Strategy quality

Generated values should represent the production risk surface rather than arbitrary randomness.

### Shrinking

Failures should produce understandable counterexamples.

### Reproducibility

A developer should be able to reproduce a CI failure and diagnose the minimal failing input.

### Layering

Fast property tests should remain separate from expensive integration tests when infrastructure startup or network calls are involved.

### Data Engineering relevance

The suite should cover the realities of pipelines:

```text
nulls
duplicates
empty data
schema changes
timestamps
time zones
decimal values
serialization
partitioning
idempotency
```

### CI discipline

Generated examples and dataset sizes must be bounded according to test cost.

### Scope

This module remains focused on:

```text
Property-Based Testing with Hypothesis
```

It complements the preceding integration-testing topic rather than replacing it.


## 39. Connection to Module 2.19

The testing layers now form a complementary system:

```text
Transformation fixtures
        ↓
DataFrame equality / tolerance
        ↓
Real dependency integration
        ↓
Property-based testing
        ↓
Schema / contract regression
        ↓
End-to-end smoke
```

Topic 04 adds a different testing dimension:

> **Instead of asking whether a few selected examples are correct, ask which properties must remain true across a broad generated input space.**

This makes property-based testing particularly useful for discovering edge cases that humans did not explicitly enumerate.


## 40. Final Engineering Principle

The strongest property-based tests begin with a precise invariant.

```text
Production risk
      ↓
Business / engineering invariant
      ↓
Input domain
      ↓
Hypothesis strategy
      ↓
Generated example
      ↓
Property assertion
      ↓
Failure
      ↓
Shrinking
      ↓
Minimal counterexample
      ↓
Defect fix
```

The goal is not:

```text
"Generate as much random data as possible."
```

The goal is:

```text
"Express what must always be true,
then systematically search for inputs that violate it."
```

That is what turns Hypothesis from a random-data generator into a production testing tool.


## Appendix A — Practical Command Reference

```bash
# Install
uv add --dev hypothesis pytest

# Run all tests
pytest

# Run property tests
pytest tests/test_properties.py -q

# Run one property
pytest tests/test_properties.py::test_normalization_is_idempotent -q

# Show slowest tests
pytest --durations=20

# Run integration/property tests separately
pytest tests/integration
pytest tests/properties
```

Keep expensive infrastructure-based property tests in an explicit test layer. The fastest properties should remain suitable for rapid developer feedback.


## Appendix B — Property Design Template

Use this template before writing a property:

```text
Property name:
    ______________________________________

Production risk:
    ______________________________________

Input domain:
    ______________________________________

Valid inputs:
    ______________________________________

Important edge cases:
    ______________________________________

Invariant:
    ______________________________________

Why the invariant is correct:
    ______________________________________

Strategy:
    ______________________________________

Expected failure if implementation is broken:
    ______________________________________

How shrinking would help:
    ______________________________________

CI cost:
    ______________________________________
```

This prevents the common mistake of writing a Hypothesis test before understanding the contract.


## Appendix C — Source Alignment

This module was produced from the supplied Topic 04 specification and is intended to preserve its required scope, terminology, progression, tooling, practical exercises, failure lab, checkpoint, interview preparation, final assessment, and production-quality expectations.

The module deliberately uses model-generated teaching examples to turn the specification into a usable learning artifact. Exact library APIs and behavior should be validated against the versions pinned by the repository before executable examples are treated as version-specific reference code.
