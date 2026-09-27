# 05 — Cleaning Missing Values, Duplicates, and Outliers

This chapter teaches production-oriented pandas data cleaning from intermediate foundations through advanced Data Engineering practice. The goal is not to delete everything that looks unusual. The goal is to detect problems, understand their meaning, choose a justified rule, apply it reproducibly, prove what changed, reconcile row movement, and preserve enough evidence to investigate later.

The central question is:

> **What is wrong with this data, what evidence proves the problem, what action is justified, and how do I prove that cleaning did not silently damage the dataset?**

The recurring engineering loop is:

```text
Raw/Bronze
    ↓
Profile
    ↓
Detect
    ↓
Classify
    ↓
Choose a rule
    ↓
Drop / Fill / Fix / Flag / Quarantine
    ↓
Validate
    ↓
Reconcile
    ↓
Audit
    ↓
Silver
```

For cleaning work, practice:

```text
Read → Profile → Predict → Run → Inspect → Break → Debug → Assert → Measure → Explain

Detect → Understand → Decide → Apply → Validate → Reconcile → Audit
```

The five common actions are **drop, fill, fix, flag, and quarantine**. They are different decisions, not synonyms.


## 1. Why Data Cleaning Matters in Data Engineering

This topic follows selection and typing. Before cleaning a dataset, you need to know what a row represents, what each column means, and what its dtype represents.

Poor cleaning can cause:

- incorrect revenue and other metrics
- duplicate business activity
- distorted aggregates
- false anomaly detection
- silent row loss
- weak auditability
- impossible incident reconstruction

A source can emit multiple versions of the same order. This is why a blanket `drop_duplicates()` is not enough: the pipeline must first define the business key and the version rule.

```text
Cleaning ≠ deletion

Cleaning =
detection
+ classification
+ justified transformation
+ validation
+ reconciliation
+ auditability
```

**Production principle:** do not modify or delete data simply because it looks unusual. Determine what is known, what is unknown, what rule is justified, and what should happen when the evidence is uncertain.


## 2. Cleaning Mental Model

| Stage | Question | Evidence |
|---|---|---|
| Profile | What does the dataset look like? | row count, dtypes, null rate, duplicate rate |
| Detect | Which values or rows violate a known rule? | boolean masks, duplicate flags, IQR/domain checks |
| Classify | What kind of problem is this? | missingness, duplication, standardization, anomaly |
| Decide | What action is justified? | source contract, domain rule, evidence |
| Apply | How should data change? | drop, fill, fix, flag, quarantine |
| Validate | Did the output satisfy invariants? | assertions, uniqueness, value checks |
| Reconcile | Can every row be accounted for? | row counts, reason counts |
| Audit | Can the run be explained later? | cleaning report, rule identifiers |

Bronze should preserve raw source values. Silver is where deliberate cleaning, standardization, deduplication, validation, and quarantine belong. Gold should consume clean, business-ready data.


## 3. Profile Before Cleaning

The first question is not “how do I remove this row?” It is “what is actually happening in this dataset?”

Start with shape and schema:


```python
import pandas as pd

df = pd.DataFrame({
    "order_id": ["A1", "A2", "A2", None],
    "customer_id": [101, 102, 102, 103],
    "amount_cents": [1000, None, 1000, 999999],
    "country": ["IN", "US", "US", None],
})

print("shape:", df.shape)
print(df.dtypes)
print(df.isna().sum())
print(df.isna().mean())
```


**Interpretation:** The baseline gives you row count, schema, missing counts, and missing rates before any transformation.


### Missing-rate reasoning

`isna().sum()` answers “how many missing values?” and `isna().mean()` answers “what fraction is missing?” because the boolean mask is aggregated across rows.


```python
missing_count = df.isna().sum()
missing_rate = df.isna().mean()
missing_percent = missing_rate.mul(100)

print(missing_count)
print(missing_percent.round(2))
```


Profile other suspicious patterns too:

- duplicate rate for the business key
- unusual labels
- impossible values
- unexpected distributions
- patterns concentrated in one source file or time interval

Do not fix the data before writing down the baseline.


## 4. Detecting Missing Values

`isna()` identifies missing values. `notna()` identifies values that are present.


```python
missing_rows = df.loc[df.isna().any(axis=1)]
all_missing_rows = df.loc[df.isna().all(axis=1)]

print("rows with any missing value:")
print(missing_rows)
print("rows with every value missing:")
print(all_missing_rows)
```


**Interpretation:** `axis=1` means the check is performed across columns for each row.


Useful questions:

1. Which columns contain missing values?
2. What is the missing rate per column?
3. Are missing values expected?
4. Are required fields affected?
5. Does the source contract define special missing tokens?
6. Are missing values concentrated in one source or period?

Missingness is not automatically an error.


## 5. Missingness by Business Importance

Consider an orders table with:

```text
order_id
customer_id
country
amount_cents
created_at
optional_note
```

A missing `optional_note` may be normal, while a missing `order_id` may make the record impossible to trace. The correct action therefore depends on the data contract.

| Field | Illustrative concern | Possible action |
|---|---|---|
| `order_id` | row identity | quarantine/fail if required |
| `customer_id` | relationship | quarantine or investigate |
| `amount_cents` | financial measure | do not blindly fill |
| `created_at` | event time | quarantine/investigate if required |
| `country` | classification | fill only from a justified source |
| `optional_note` | non-critical text | often leave missing |

These are examples, not universal business rules.


## 6. `dropna()`

`dropna()` removes rows or columns containing missing values according to a rule. Because it can delete information, use it only with an explicit reason.

### `subset=`

Use `subset` when only selected fields determine whether a row can survive.


```python
df = pd.DataFrame({
    "order_id": ["A1", "A2", None, "A4"],
    "customer_id": [101, None, 103, 104],
    "note": ["ok", None, None, "ok"],
})

required = df.dropna(subset=["order_id", "customer_id"])
print(required)
```


### `how=`

- `how="any"` removes a row when any checked value is missing.
- `how="all"` removes a row only when all checked values are missing.

### `thresh=`

`thresh` keeps rows containing at least the requested number of non-missing values.

Always predict the surviving rows before executing the rule.


```python
df = pd.DataFrame({
    "a": [1, None, 3],
    "b": [None, 2, 3],
    "c": [1, 2, None],
})

print(df.dropna(how="any"))
print(df.dropna(how="all"))
print(df.dropna(thresh=2))
```


## 7. `fillna()`

`fillna(value)` replaces missing values with one value. `fillna(dict_per_column)` allows different rules per column.


```python
df = pd.DataFrame({
    "country": ["IN", None, "US"],
    "quantity": [2, None, 5],
})

filled = df.fillna({
    "country": "UNKNOWN",
    "quantity": 0,
})

print(filled)
```


A blanket `fillna(0)` is risky because zero and missing are different semantic states. Use zero only when the source/business rule says it is a valid representation of the missing value.

### Drop vs fill

| Situation | Possible action | Reasoning |
|---|---|---|
| required identifier missing | quarantine/fail | record may not be traceable |
| optional text missing | leave missing | absence may be valid |
| documented default | fill | contract defines replacement |
| deterministic correction | fix | rule is provable |
| unusual but possibly valid | flag | preserve the observation |
| unsafe for Silver | quarantine | separate handling is required |


## 8. Forward Fill, Backward Fill, and Interpolation

`ffill()` carries the last known value forward. `bfill()` carries the next known value backward. Both rely on a valid ordering assumption.


```python
df = pd.DataFrame({
    "updated_at": pd.to_datetime([
        "2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"
    ]),
    "country": ["IN", None, None, "US"],
}).sort_values("updated_at")

df["country_ffill"] = df["country"].ffill()
df["country_bfill"] = df["country"].bfill()

print(df)
```


Interpolation estimates a missing numeric value between known observations. It is not the same as copying a neighbor.


```python
series = pd.Series([10.0, 20.0, None, 40.0])
print(series.interpolate())
```


Use forward/backward fill or interpolation only when their assumptions are valid. In particular, backward fill can introduce future information into historical records, and interpolation can invent values for events that are not continuous measurements.


## 9. Group-Wise Forward Fill

Entity boundaries matter. A customer's country must not be filled from another customer.


```python
orders = pd.DataFrame({
    "customer_id": [1, 1, 2, 2],
    "updated_at": pd.to_datetime([
        "2026-01-01", "2026-01-02", "2026-01-01", "2026-01-02"
    ]),
    "country": ["IN", None, "US", None],
}).sort_values(["customer_id", "updated_at"])

orders["country_filled"] = (
    orders.groupby("customer_id")["country"]
    .ffill()
)

print(orders)
```


**Interpretation:** Each customer's value is propagated only within that customer.


For time-dependent fills, sort first. Otherwise “previous” may not mean previous in business time. Test explicit group boundaries so values cannot leak between entities.


## 10. Duplicate Detection

`duplicated()` creates a boolean mask. `drop_duplicates()` removes rows according to the same duplicate definition.


```python
df = pd.DataFrame({
    "order_id": ["A1", "A2", "A2", "A3", "A3"],
    "amount_cents": [1000, 2000, 2000, 3000, 3100],
})

print(df.duplicated())
print(df.duplicated(subset=["order_id"]))
print(df.duplicated(subset=["order_id"], keep=False))
```


`keep=False` marks every member of a duplicate key group, which is useful for inspection before deciding which record should survive.


## 11. Business Keys

A duplicate is defined by business meaning, not only by identical row contents.

A business key is the field or combination of fields identifying the logical record for the operation being performed.

For example:

```text
order_id              → logical order
order_id + version    → one version of the order
customer_id + date    → one customer snapshot, if that is the grain
```

Compare whole-row and key-based deduplication:


```python
df = pd.DataFrame({
    "order_id": ["A1", "A1", "B1"],
    "updated_at": pd.to_datetime([
        "2026-01-02 10:00",
        "2026-01-03 10:00",
        "2026-01-01 09:00",
    ]),
    "status": ["paid", "shipped", "paid"],
})

print("whole-row:", len(df.drop_duplicates()))
print("business-key:", len(df.drop_duplicates(subset=["order_id"])))
```


These are different business operations. Never define duplicates solely by choosing whichever call returns fewer rows.


## 12. Latest Record per Business Key

The roadmap requires:

```text
define key
→ define ordering/version field
→ sort
→ keep latest
→ validate uniqueness
```


```python
df = pd.DataFrame({
    "order_id": ["A1", "A1", "A2", "A2"],
    "updated_at": pd.to_datetime([
        "2026-01-02 10:00",
        "2026-01-03 10:00",
        "2026-01-01 08:00",
        "2026-01-02 08:00",
    ]),
    "status": ["paid", "shipped", "paid", "cancelled"],
})

latest = (
    df.sort_values(["order_id", "updated_at"])
      .drop_duplicates(subset=["order_id"], keep="last")
)

assert latest["order_id"].is_unique
print(latest)
```


**Interpretation:** The latest timestamp per `order_id` survives.


If two records have tied timestamps, “latest” is ambiguous. Add a deterministic tie-breaker such as a source sequence/version field when the source provides one. If no trustworthy tie-breaker exists, investigate or quarantine rather than silently guessing.


## 13. Deduplication Validation

After deduplication, validate the expected key and account for row movement.


```python
rows_before = len(df)
rows_after = len(latest)
rows_removed = rows_before - rows_after

assert latest["order_id"].is_unique

print({
    "rows_before": rows_before,
    "rows_after": rows_after,
    "rows_removed": rows_removed,
})
```


Row removal should be measurable. A pipeline should be able to explain why the count decreased.


## 14. Standardising Values with `replace()` and `map()`

Standardization turns multiple source representations into a documented canonical representation.


```python
df = pd.DataFrame({
    "status": ["PAID", "paid ", "Paid", "SHIPPED", "shipped"],
})

df["status"] = (
    df["status"]
    .str.strip()
    .str.casefold()
)

print(df)
```


Use `replace()` for explicit substitutions and `map()` for dictionary-driven mapping.


```python
country_map = {
    "India": "IN",
    "IND": "IN",
    "in": "IN",
}

countries = pd.Series(["India", "IND", "in", "US"])
mapped = countries.map(country_map)

print(mapped)
```


Unmapped values can become missing in a simple `map` pattern. Treat that as a useful signal that the mapping contract is incomplete, not as proof that the source value was wrong.


## 15. Country and Status Standardization

Do not assume that strings such as `India`, `IND`, and `in` are equivalent without a documented domain mapping.

```text
raw source
→ normalization
→ controlled mapping
→ canonical value
```

String trimming and case-folding are deterministic transformations. Domain mappings should be explicit and auditable.

Keep the original value when auditability matters. This allows the pipeline to answer both “what arrived?” and “what did we publish?”.


## 16. Outliers — What Are They?

An outlier is an observation that is unusually far from the rest of the data under a chosen rule.

An outlier is **not automatically invalid**.

Possible interpretations include:

- legitimate large order
- data-entry error
- system defect
- fraud/anomaly candidate
- rare but valid event

Separate three ideas:

| Concept | Meaning |
|---|---|
| Statistical outlier | unusual relative to a distribution |
| Domain-invalid value | violates a known business rule |
| Business anomaly | unusual and deserves investigation |

Statistical unusualness and validity are different questions.


## 17. IQR Rule

The interquartile range is:

```text
IQR = Q3 - Q1
Lower bound = Q1 - 1.5 × IQR
Upper bound = Q3 + 1.5 × IQR
```


```python
values = pd.Series([10, 11, 12, 12, 13, 14, 100])

q1 = values.quantile(0.25)
q3 = values.quantile(0.75)
iqr = q3 - q1
lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr

outlier_mask = (values < lower) | (values > upper)

print({
    "q1": q1,
    "q3": q3,
    "iqr": iqr,
    "lower": lower,
    "upper": upper,
})
print(values.loc[outlier_mask])
```


Prediction exercise: before running the code, calculate which values you expect to be outside the bounds. Then compare your reasoning with the actual result.


## 18. IQR Outliers Per Group

A global threshold can be misleading when groups have different normal ranges. The roadmap requires an IQR rule per country for `amount_cents`.


```python
orders = pd.DataFrame({
    "country": ["IN", "IN", "IN", "IN", "US", "US", "US", "US"],
    "amount_cents": [1000, 1100, 1200, 5000, 10000, 10500, 11000, 50000],
})

q1 = orders.groupby("country")["amount_cents"].transform("quantile", 0.25)
q3 = orders.groupby("country")["amount_cents"].transform("quantile", 0.75)
iqr = q3 - q1

lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr

orders["is_outlier"] = (
    (orders["amount_cents"] < lower) |
    (orders["amount_cents"] > upper)
)

print(orders)
```


For production use, define edge-case policies for small groups, missing group keys, and groups where IQR is zero. Do not invent a statistical rule silently.


## 19. Small-Group and Zero-IQR Edge Cases

For a group with constant values, Q1 and Q3 may be equal and the IQR becomes zero. Very small groups may also provide too little evidence for a useful statistical threshold.


```python
values = pd.Series([100, 100, 100])

q1 = values.quantile(0.25)
q3 = values.quantile(0.75)
iqr = q3 - q1

print({"q1": q1, "q3": q3, "iqr": iqr})
```


A production rule should specify what to do with such groups: require a minimum group size, use a domain rule, flag for review, or apply another justified method.


## 20. Z-Scores

A z-score expresses distance from the mean in standard-deviation units:

```text
z = (x - mean) / standard_deviation
```


```python
values = pd.Series([10.0, 11.0, 12.0, 13.0, 30.0])

mean = values.mean()
std = values.std(ddof=0)
z = (values - mean) / std

print(z.round(2))
```


A large absolute z-score can identify an unusual observation. However, thresholds are workload- and domain-dependent, and z-scores can be sensitive to the data distribution and to extreme values that influence the mean and standard deviation.


## 21. Domain Rules

A domain rule encodes what the system says is allowed.

Illustrative examples:

- quantity cannot be negative
- an event timestamp cannot be beyond an allowed business cutoff
- amount cannot be negative
- a status must belong to an approved vocabulary
- age must fall within a documented domain range

A domain-invalid value can be common and still invalid. A rare statistical outlier can be valid.

Use evidence, not frequency alone.


## 22. `clip()`

`clip()` caps values at a chosen boundary.


```python
df = pd.DataFrame({
    "amount_cents": [-100, 500, 1000, 200000]
})

df["amount_capped"] = df["amount_cents"].clip(
    lower=0,
    upper=100000,
)

print(df)
```


Clipping changes the representation. It does not prove the original value was wrong. Preserve the original or add an audit/flag field when the transformation matters.


## 23. Fuzzy Duplicates and Normalized Keys

Two records may describe the same entity even when raw strings differ. A normalized key helps find candidate matches.


```python
df = pd.DataFrame({
    "name": [
        "Shoun Kumar",
        " shoun kumar ",
        "SHOUN KUMAR",
        "Shoun-Kumar",
        "Shawn Kumar",
    ]
})

df["normalized_name"] = (
    df["name"]
    .str.casefold()
    .str.strip()
    .str.replace("-", " ", regex=False)
)

print(df)
```


Normalization can include case-folding, whitespace stripping, and punctuation handling. A normalized match is a **candidate**, not proof of identity.


### False-positive safety

Aggressive normalization can merge different entities. Treat normalized collisions as candidates for stronger evidence or review.

```text
raw equality
→ exact duplicate

business-key rule
→ deterministic duplicate

normalized-key equality
→ fuzzy candidate

additional evidence/review
→ confirmed duplicate
```

Do not silently merge two people merely because their names normalize to the same string.


## 24. Flagging Instead of Deleting

A flag preserves the observation while making the quality issue visible.

Common fields include:

```text
is_outlier
is_duplicate
dq_reason
```


```python
df = pd.DataFrame({
    "order_id": ["A1", "A2", "A3"],
    "amount_cents": [1000, -50, 500000],
})

df["is_outlier"] = df["amount_cents"] > 100000
df["is_duplicate"] = df["order_id"].duplicated(keep=False)

print(df)
```


A reason field can contain values such as `missing_customer_id`, `negative_quantity`, `duplicate_order_id`, `amount_outlier`, `invalid_country`, or `future_created_at`. These are illustrative labels, not universal standards.


## 25. Clean vs Quarantine

Quarantine separates records that should not enter the clean dataset yet but should remain available for review or reprocessing.


```python
df = pd.DataFrame({
    "order_id": ["A1", "A2", "A3"],
    "is_outlier": [False, True, False],
    "dq_reason": [None, "amount_outlier", None],
})

dq_mask = df["is_outlier"] | df["dq_reason"].notna()

quarantine = df.loc[dq_mask].copy()
clean = df.loc[~dq_mask].copy()

print("clean:", len(clean))
print("quarantine:", len(quarantine))
```


The explicit `.copy()` communicates independent working outputs. Quarantine is not a trash can; it is a controlled path for records requiring separate handling.


## 26. Designing `dq_reason`

A quality reason should make the decision explainable.

Examples:

| Reason | Meaning |
|---|---|
| `missing_customer_id` | required relationship is absent |
| `duplicate_order_id` | business key appeared more than once |
| `negative_quantity` | violates an illustrative domain rule |
| `amount_outlier` | statistical rule flagged the value |
| `invalid_country` | value is outside the accepted vocabulary |
| `future_created_at` | timestamp violates an allowed-time rule |

If a row can fail multiple rules, decide whether to keep multiple flags or a structured/combined reason. There is no universal representation; the chosen design must support audit and reprocessing.


## 27. Cleaning Reports

A cleaning report describes what happened during a run.

Recommended fields include:

```text
rows_in
rows_out
rows_quarantined
rows_removed
missing_values_filled
duplicate_rows_flagged
outliers_flagged
status_values_standardized
counts_by_reason
```


```python
rows_in = 1000
rows_out = 940
rows_quarantined = 60

assert rows_in == rows_out + rows_quarantined

report = {
    "rows_in": rows_in,
    "rows_out": rows_out,
    "rows_quarantined": rows_quarantined,
}

print(report)
```


**Interpretation:** The numbers are illustrative. The invariant is the important part.


## 28. Reconciliation

The roadmap requires the core row-accounting invariant:

```text
rows_in == rows_out + rows_quarantined
```


```python
rows_in = len(df)
rows_out = len(clean)
rows_quarantined = len(quarantine)

assert rows_in == rows_out + rows_quarantined
```


This catches accidental row loss when the design guarantees every incoming row belongs either to the clean output or to quarantine. Pipelines that intentionally delete data need a more detailed reconciliation category for those rows.


## 29. Before/After Comparisons

For each cleaning rule, measure:

- input count
- affected count
- output count

Do not hard-code expected counts from an example dataset.


```python
rows_before = len(df)
duplicate_mask = df["order_id"].duplicated(keep=False)
duplicate_count = int(duplicate_mask.sum())

print({
    "rows_before": rows_before,
    "duplicate_rows_affected": duplicate_count,
})
```


When values are changed, compare the before and after values where practical. This gives you an auditable statement of exactly what the rule changed.


## 30. When Not to Clean

The roadmap explicitly requires preserving raw data.

```text
Bronze
→ preserve source truth

Silver
→ apply explicit cleaning rules

Gold
→ publish business-ready outputs
```

Do not:

- infer an unknown country because another value seems plausible
- delete a large order only because it is rare
- merge customer identities from weak fuzzy evidence
- overwrite the only raw copy
- use statistical thresholds as if they were business truth

If you do not understand a value, preserve it and route it for investigation or quarantine.


## 31. Decision Framework — Drop, Fill, Fix, Flag, Quarantine

| Action | Use when | Question to ask |
|---|---|---|
| Drop | removal is explicitly justified | Why is losing the row acceptable? |
| Fill | a valid replacement is defined | Why does the replacement preserve meaning? |
| Fix | a deterministic correction exists | Can the correction be proven? |
| Flag | value may be valid but deserves attention | Can we preserve it and surface the issue? |
| Quarantine | data should not enter Silver yet | Can it be reviewed or reprocessed later? |

A production rule should explain both the selected action and the rejected alternatives.


## 32. Hands-On Exercise — `clean_orders.py`

The roadmap requires a complete production-oriented exercise. The exercise belongs here as a specification. Do not create `clean_orders.py` or a separate test file as part of this chapter.

### Scenario

You receive orders containing repeated order versions, missing country values, inconsistent status labels, and unusual monetary values.

The target outputs are:

- `silver_orders`
- `quarantine_orders`
- a cleaning report

### Task 1 — Latest record per order

Define `order_id` as the business key if the source contract says one logical order has one identifier. Sort by `order_id` and `updated_at`, then keep the latest.


```python
sorted_orders = orders.sort_values(["order_id", "updated_at"])
latest_orders = sorted_orders.drop_duplicates(
    subset=["order_id"],
    keep="last",
)

assert latest_orders["order_id"].is_unique
```


If timestamps tie, define a deterministic tie-breaker. Never pretend a tie is unambiguous.

### Task 2 — Missing country

Fill the missing `country` value from the customer's last known country using group-wise forward fill. Sort by customer and time first.


```python
orders = orders.sort_values(["customer_id", "updated_at"])

orders["country"] = (
    orders.groupby("customer_id")["country"]
    .ffill()
)
```


Test a boundary case where customer 1 has `IN` and customer 2 has `US`. The fill must never cross the boundary.

### Task 3 — Standardise status

Normalize values such as `PAID`, `paid `, and `Paid` to `paid`. Measure how many values changed.

### Task 4 — IQR outliers per country

Calculate Q1, Q3, IQR, lower bound, and upper bound for `amount_cents` by country. Store an `is_outlier` flag. Do not automatically delete the outliers.

### Task 5 — Silver and quarantine

Create the clean and quarantine outputs. Store `dq_reason` for excluded rows. Keep the raw source available.

### Task 6 — Cleaning report

Report `rows_in`, `rows_out`, `rows_quarantined`, and counts by reason. Prove:


```python
assert rows_in == rows_out + rows_quarantined
```


### Required exercise checks

Before running each rule, predict:

- how many rows will be affected
- which records will survive
- which values will change
- how many rows should be quarantined
- whether the reconciliation will hold

The exercise is complete only when the result is explainable and testable.


## 33. Prediction-First Cleaning

Use prediction before execution.

| Situation | Prediction |
|---|---|
| `dropna` | which rows disappear? |
| `fillna` | which values change, and what do they mean? |
| deduplication | which key defines a duplicate? |
| `keep="last"` | which record survives after sorting? |
| forward fill | what is the previous valid value for this entity? |
| normalization | which labels become canonical? |
| IQR | which observations fall outside the bounds? |
| quarantine | how many rows move and for what reasons? |
| reconciliation | do row counts still balance? |

The loop is:

```text
Predict
→ Run
→ Inspect
→ Assert
→ Explain
```


## 34. Debugging Cleaning Problems

For every incident use:

```text
Symptom
→ Root cause
→ How to inspect
→ Correct approach
→ Prevention rule
```


### Bug 1 — `drop_duplicates()` used without the business key

**Root cause:** `df.drop_duplicates()` compares whole-row equality, not the logical record definition.

**Correct approach:** Define the business key and the grain before deduplicating.

**Prevention:** Write the deduplication contract first.


### Bug 2 — `keep='last'` used without sorting

**Root cause:** The last physical row is not automatically the latest business version.

**Correct approach:** Sort by key and version/order columns.

**Prevention:** Make ordering explicit and deterministic.


### Bug 3 — Tied timestamps

**Root cause:** Two versions have the same timestamp and different content.

**Correct approach:** Inspect all candidate rows for the key.

**Prevention:** Add a source sequence/version tie-breaker or quarantine the ambiguity.


### Bug 1 — `drop_duplicates()` used without the business key

**Root cause:** `df.drop_duplicates()` compares whole-row equality, not the logical record definition.

**Correct approach:** Define the business key and the grain before deduplicating.

**Prevention:** Write the deduplication contract first.


### Bug 2 — `keep='last'` used without sorting

**Root cause:** The last physical row is not automatically the latest business version.

**Correct approach:** Sort by key and version/order columns.

**Prevention:** Make ordering explicit and deterministic.


### Bug 3 — Tied timestamps

**Root cause:** Two versions have the same timestamp and different content.

**Correct approach:** Inspect all candidate rows for the key.

**Prevention:** Add a source sequence/version tie-breaker or quarantine the ambiguity.


### Bug 1 — `drop_duplicates()` used without the business key

**Root cause:** `df.drop_duplicates()` compares whole-row equality, not the logical record definition.

**Correct approach / inspection:** Define the business key and the grain before deduplicating.

**Prevention:** Write the deduplication contract first.


### Bug 2 — `keep='last'` used without sorting

**Root cause:** The last physical row is not automatically the latest business version.

**Correct approach / inspection:** Sort by key and version/order columns.

**Prevention:** Make ordering explicit and deterministic.


### Bug 3 — Tied timestamps

**Root cause:** Two versions have the same timestamp and different content.

**Correct approach / inspection:** Inspect all candidate rows for the key.

**Prevention:** Add a source sequence/version tie-breaker or quarantine the ambiguity.


### Bug 4 — Forward fill leaks across customers

**Root cause:** A global `ffill()` uses a value from another entity.

**Correct approach / inspection:** Inspect entity boundaries. Correct approach: Use `groupby(entity)[column].ffill()`.

**Prevention:** Test cross-entity cases.


### Bug 5 — Forward fill uses incorrect order

**Root cause:** The data is not sorted by the business-time field.

**Correct approach / inspection:** Compare row order to the timestamp/order column.

**Prevention:** Sort before filling.


### Bug 6 — `fillna(0)` changes meaning

**Root cause:** Unknown becomes known zero.

**Correct approach / inspection:** Compare domain semantics before and after.

**Prevention:** Fill only when zero is a documented semantic replacement.


### Bug 7 — `dropna()` removes too many rows

**Root cause:** A missing optional field deletes the whole record.

**Correct approach / inspection:** Compare broad `dropna()` with `subset=` using required fields.

**Prevention:** Define required fields explicitly.


### Bug 8 — `thresh` misunderstood

**Root cause:** The threshold counts non-missing values, not missing values.

**Correct approach / inspection:** Count non-null fields row by row on a tiny frame.

**Prevention:** Test exact boundary cases.


### Bug 9 — every IQR outlier is deleted

**Root cause:** Statistical unusualness is confused with invalidity.

**Correct approach / inspection:** Inspect examples and domain rules.

**Prevention:** Flag or quarantine unless invalidity is established.


### Bug 10 — global threshold across groups

**Root cause:** Normal ranges differ by country/device/customer segment.

**Correct approach / inspection:** Inspect group distributions.

**Prevention:** Use a group-specific rule when justified.


### Bug 11 — constant group has zero IQR

**Root cause:** Q1 equals Q3, so the interval collapses.

**Correct approach / inspection:** Print Q1, Q3, and IQR.

**Prevention:** Define a minimum-size/zero-IQR policy.


### Bug 12 — clipping destroys evidence

**Root cause:** Original values are overwritten.

**Correct approach / inspection:** Compare source and transformed columns.

**Prevention:** Preserve original values where auditability matters.


### Bug 13 — fuzzy matching creates false duplicates

**Root cause:** Normalized strings are treated as proof of identity.

**Correct approach / inspection:** Inspect normalized-key collisions and original values.

**Prevention:** Treat matches as candidates until confirmed.


### Bug 14 — normalization is undocumented

**Root cause:** Future engineers cannot explain changed values.

**Correct approach / inspection:** Record source/output examples and affected counts.

**Prevention:** Document/version the rule.


### Bug 15 — multiple quality issues are overwritten

**Root cause:** One reason field hides other failed rules.

**Correct approach / inspection:** Evaluate each rule independently.

**Prevention:** Use multiple flags or a deliberate combined representation.


### Bug 16 — quarantine rows vanish

**Root cause:** Rows are filtered away without preserving them.

**Correct approach / inspection:** Compare input and output counts.

**Prevention:** Persist quarantine with `dq_reason`.


### Bug 17 — reconciliation fails

**Root cause:** Rows were lost, duplicated, or routed inconsistently.

**Correct approach / inspection:** Log counts at each stage and inspect quality masks.

**Prevention:** Make row movement explicit.


### Bug 18 — raw data is overwritten

**Root cause:** Source evidence is destroyed.

**Correct approach / inspection:** Inspect layer boundaries and file paths.

**Prevention:** Keep Bronze/raw unchanged and write separate Silver outputs.


The debugging habit is to prove a rule on a tiny deterministic example before applying it to a production-sized DataFrame.


## 35. Production Data Engineering Patterns

### Bronze → Silver → Gold

Cleaning belongs primarily in Silver:

```text
Bronze
→ preserve source truth

Silver
→ standardize
→ deduplicate
→ validate
→ quarantine

Gold
→ publish business-ready outputs
```

### Orders

Define the logical grain and version semantics before deduplicating. Preserve source order/version information when it supports auditability.

### Customer records

Standardize labels deliberately, but do not infer identity from weak fuzzy evidence.

### Sensor data

Missing values, interpolation, and outlier rules depend on time ordering and the meaning of the measurement.

### API events

Retries may create repeated records. Deduplication should use the source event identity or idempotency semantics where available.

### Transactions

A high-value transaction should not be deleted merely because it is unusual. Use documented domain rules and retain an audit trail.

### Silver-layer quality

```text
raw source
→ profile
→ standardize
→ deterministic deduplication
→ quality rules
→ clean + quarantine
→ reconcile
→ audit
```


## 36. Data Quality Rule Catalog

The following rule IDs are illustrative:

| Rule ID | Rule | Detection | Possible action |
|---|---|---|---|
| DQ001 | missing required `order_id` | `order_id.isna()` | quarantine |
| DQ002 | duplicate `order_id` | business-key duplicate mask | dedup/quarantine |
| DQ003 | negative quantity | `quantity < 0` | flag/quarantine |
| DQ004 | invalid status | outside controlled vocabulary | standardize/quarantine |
| DQ005 | future timestamp | timestamp beyond permitted cutoff | flag/quarantine |
| DQ006 | amount IQR outlier | outside group-specific bounds | flag/quarantine |
| DQ007 | missing customer | `customer_id.isna()` | quarantine |

These examples are not universal policies. Actual rules must come from the source contract and business domain.


## 37. Testing Strategy

Cleaning tests should verify both transformation correctness and preservation of important information.

### Missing-value test


```python
import pandas as pd

df = pd.DataFrame({
    "id": [1, 2, 3],
    "value": [10.0, None, 30.0],
})

assert int(df["value"].isna().sum()) == 1
assert int(df["value"].notna().sum()) == 2
```


### Latest-record test


```python
df = pd.DataFrame({
    "order_id": ["A1", "A1", "B1"],
    "updated_at": pd.to_datetime([
        "2026-01-02",
        "2026-01-03",
        "2026-01-01",
    ]),
})

latest = (
    df.sort_values(["order_id", "updated_at"])
      .drop_duplicates("order_id", keep="last")
)

assert latest["order_id"].is_unique
assert latest.loc[
    latest["order_id"] == "A1",
    "updated_at",
].iloc[0] == pd.Timestamp("2026-01-03")
```


### Standardization test


```python
statuses = pd.Series(["PAID", "paid ", "Paid"])
normalized = statuses.str.strip().str.casefold()

expected = pd.Series(["paid", "paid", "paid"])

pd.testing.assert_series_equal(
    normalized.reset_index(drop=True),
    expected,
    check_names=False,
)
```


### Reconciliation test


```python
rows_in = 10
rows_out = 8
rows_quarantined = 2

assert rows_in == rows_out + rows_quarantined
```


### Required edge-case tests

Test at least:

- empty DataFrame
- all-missing column
- all rows missing
- no duplicates
- every row duplicated
- one record per business key
- duplicate records with tied timestamps
- no outliers
- all rows flagged
- very small groups
- zero-IQR groups
- missing group key
- missing ordering timestamp
- missing status
- null values during normalization
- ambiguous fuzzy matches
- one row with multiple quality issues
- zero rows quarantined
- all rows quarantined

Use deterministic examples so failures explain the business rule rather than fixture randomness.


## 38. Performance Considerations

Cleaning operations can scan data, sort it, group it, and allocate intermediate DataFrames.

| Operation | Main cost consideration | Engineering habit |
|---|---|---|
| `isna()` | column scans | profile deliberately and reuse masks where useful |
| `dropna()` | row filtering | restrict to required fields when appropriate |
| `sort_values()` | sorting and temporary memory | sort only on required key/order fields |
| `duplicated()` | key comparison | use the smallest meaningful business key |
| group-wise rules | grouping + transformation | prefer clear vectorized operations |
| clean/quarantine split | DataFrame allocations | measure memory on large inputs |
| string normalization | text processing | benchmark representative data |
| IQR by group | grouped quantile work | define small-group behavior |

Performance is a measurement problem. A transformation that is fast on 10,000 rows can behave differently at millions of rows.


```python
import time

start = time.perf_counter()

mask = df["value"].notna() & (df["value"] >= 0)
result = df.loc[mask]

elapsed = time.perf_counter() - start
print(f"elapsed_seconds={elapsed:.6f}")
```


Do not optimize merely because an operation looks expensive. Measure representative data, keep the rule correct, and document the trade-off.


## 39. Auditability

A cleaning run should be able to answer:

- how many rows came in?
- how many rows were emitted to Silver?
- how many were quarantined?
- why were rows quarantined?
- how many values were filled?
- how many values were standardized?
- how many duplicate records were detected or removed?
- how many outliers were flagged?
- which rule/configuration applied?

This information supports debugging, reproducibility, operations, data-quality investigation, stakeholder communication, and environments where data changes need to be explained.


## 40. Cleaning Anti-Patterns

## 48. Common Mistakes Summary

| Mistake | Why it happens | Better approach |
|---|---|---|
| `drop_duplicates()` on all columns | Whole-row equality is mistaken for business identity | Define the business key first |
| Forgetting to sort before `keep="last"` | Physical row order is mistaken for business recency | Sort by key and version/order fields |
| Filling with `0` indiscriminately | Missing is confused with known zero | Use zero only when the semantic contract supports it |
| Deleting every outlier | Unusual is confused with invalid | Preserve, flag, or quarantine unless invalidity is established |
| Forward-filling across groups | Entity boundaries are ignored | Use group-wise fill with correct ordering |
| Aggressive fuzzy matching | Normalized equality is treated as identity | Treat matches as candidates and investigate ambiguity |
| Cleaning raw data destructively | Convenience is prioritized over traceability | Preserve Bronze/raw source data |
| Quarantining without reasons | Rows are separated without explanation | Store `dq_reason` and reconcile counts |


### Blanket `dropna()`

Danger: optional missing fields can delete otherwise valid rows.

Better: define required fields and use `subset`, `how`, or `thresh` intentionally.

### Blanket `drop_duplicates()`

Danger: whole-row equality is not necessarily the business definition of a duplicate.

Better: define the business key and ordering/version rule.

### Blanket `fillna(0)`

Danger: unknown becomes known zero.

Better: fill only when the replacement has documented meaning.

### Delete every outlier

Danger: unusual values can be legitimate.

Better: distinguish statistical unusualness from domain invalidity and flag/quarantine when evidence is uncertain.

### Aggressive fuzzy matching

Danger: different entities can normalize to the same key.

Better: use normalization to find candidates, then require stronger evidence.

### Destructive raw-data cleaning

Danger: source evidence disappears.

Better: preserve Bronze and write separate Silver outputs.

### Quarantine without reasons

Danger: excluded rows cannot be understood or reviewed.

Better: add `dq_reason` and a cleaning report.


## 41. Cleaning Decision Exercises

For each scenario answer:

1. What is the data problem?
2. Is it missingness, duplication, standardization, or anomaly?
3. What evidence supports the classification?
4. Should you drop, fill, fix, flag, or quarantine?
5. What audit information should be recorded?
6. How would you test the rule?

### Scenario A — Optional notes

5% of optional notes are missing.

### Scenario B — Missing customer IDs

0.2% of orders have missing customer IDs.

### Scenario C — Three versions

The same order ID appears three times with different update timestamps.

### Scenario D — 100× larger amount

One order amount is dramatically larger than typical orders.

### Scenario E — Name variants

A customer name differs only in case, whitespace, and punctuation.

### Scenario F — Future timestamp

A record contains a timestamp beyond the permitted business cutoff.

There is intentionally no universal answer. The objective is to justify the decision from the data contract and evidence.


## 42. Edge Cases

### Empty input

A cleaning function should produce a predictable empty result rather than fail because there are no rows.

### All-missing column

The column may be optional, required, or unusable. Decide from schema semantics.

### Every row duplicated

Deduplication may remove most of the input. Validate the business key and report the removal.

### Tied timestamps

Latest-record selection is ambiguous without a deterministic tie-breaker.

### Small IQR groups

Statistics can be too weak to justify a strong conclusion.

### Constant group

Q1 and Q3 may be equal, producing IQR = 0. Define a policy rather than guessing.

### Missing group key

A group-specific rule needs an explicit policy for missing keys.

### Missing ordering timestamp

Latest-record logic cannot safely rely on physical row order.

### Multiple issues on one row

A row may be both duplicated and an outlier. Preserve enough information to explain both where required.

### All rows quarantined

This can be legitimate, but it must be visible, audited, and reconciled.


## 43. Production Checklist

Before approving a cleaning stage:

- [ ] I know the row grain.
- [ ] I know the business key.
- [ ] I profiled the data first.
- [ ] Missingness is interpreted by field meaning.
- [ ] Drop/fill/fix/flag/quarantine rules are explicit.
- [ ] Deduplication uses a justified key.
- [ ] Latest-record logic uses the correct ordering fields.
- [ ] Group-wise fills cannot cross entity boundaries.
- [ ] Normalization rules are documented.
- [ ] Statistical outliers are not automatically treated as invalid.
- [ ] Domain rules are explicit.
- [ ] Fuzzy matching handles false-positive risk.
- [ ] `dq_reason` or equivalent quality metadata is available.
- [ ] Clean and quarantine outputs are independently inspectable.
- [ ] Row reconciliation is asserted.
- [ ] Cleaning counts are reported.
- [ ] Bronze/raw data remains preserved.
- [ ] Normal and edge cases are tested.
- [ ] Representative performance is measured.


## 44. Cheat Sheet

### Missing values


```python
df.isna().sum()
df.isna().mean()
df.dropna(subset=["required_column"])
df.dropna(how="all")
df.dropna(thresh=2)
df.fillna("UNKNOWN")
df.fillna({"country": "UNKNOWN", "quantity": 0})
df.ffill()
df.bfill()
df.interpolate()
```


### Duplicates


```python
df.duplicated()
df.duplicated(subset=["order_id"], keep=False)
df.drop_duplicates(subset=["order_id"], keep="last")
```


### Standardization


```python
df["status"] = df["status"].str.strip().str.casefold()

df["country"] = df["country"].replace({
    "India": "IN",
    "IND": "IN",
})
```


### Outliers

```text
IQR
Z-score
domain rules
clip
```


### Quality flags


```python
df["is_duplicate"] = df["order_id"].duplicated(keep=False)
df["is_outlier"] = outlier_mask
df["dq_reason"] = reasons
```


### Quarantine and reconciliation


```python
quarantine = df.loc[dq_mask].copy()
clean = df.loc[~dq_mask].copy()

assert len(df) == len(clean) + len(quarantine)
```


## 45. Checkpoint

The roadmap checkpoint requires that you can:

1. Keep the latest record per business key correctly.
2. Choose between dropping, filling, and flagging for a given column.
3. Detect outliers using the IQR rule per group.
4. Produce a reconciliation proving that no row was silently lost.

Additional self-checks:

- When is `ffill` justified?
- When is `bfill` dangerous?
- What is the difference between interpolation and carrying a known value?
- Why is business-key deduplication different from whole-row deduplication?
- Why is sorting essential before `keep="last"`?
- How can fuzzy matching create false positives?
- Why is quarantine different from dropping?
- What does `dq_reason` provide?
- Why should Bronze remain unchanged?
- What policy would you choose for a zero-IQR group?
- What should happen when all rows are quarantined?


## 46. Final Mental Model

```text
DIRTY DATA
   ↓
PROFILE
   ↓
UNDERSTAND
   ↓
CLASSIFY
   ↓
CHOOSE RULE
   ↓
DROP / FILL / FIX / FLAG / QUARANTINE
   ↓
VALIDATE
   ↓
RECONCILE
   ↓
AUDIT
   ↓
SILVER
```

The durable engineering habit is:

> **Make every cleaning decision explicit, measurable, testable, and explainable.**

A correct cleaning stage is not the one that removes the most suspicious rows. It is the one that preserves valid information, enforces justified rules, explains every intentional change, and provides a reliable audit trail.


## 47. Roadmap Coverage Checklist

### Missing values

- [ ] `isna().sum()`
- [ ] `isna().mean()`
- [ ] rows with any missing values
- [ ] rows with all missing values
- [ ] `dropna(subset=...)`
- [ ] `dropna(how=...)`
- [ ] `dropna(thresh=...)`
- [ ] `fillna(value)`
- [ ] `fillna(dict_per_column)`
- [ ] `ffill`
- [ ] `bfill`
- [ ] `interpolate`
- [ ] group-wise forward fill

### Duplicates

- [ ] business key
- [ ] `duplicated()`
- [ ] `duplicated(subset=...)`
- [ ] `duplicated(keep=...)`
- [ ] `drop_duplicates()`
- [ ] latest record per business key
- [ ] `sort_values`
- [ ] `drop_duplicates(keep="last")`
- [ ] uniqueness validation

### Standardization

- [ ] `replace`
- [ ] `map`
- [ ] trimming
- [ ] case-folding
- [ ] country standardization
- [ ] status standardization

### Outliers

- [ ] IQR
- [ ] per-group IQR
- [ ] z-score
- [ ] domain rules
- [ ] negative quantity example
- [ ] future timestamp example
- [ ] `clip`
- [ ] statistical outlier vs domain-invalid value
- [ ] small-group and zero-IQR reasoning

### Advanced cleaning

- [ ] fuzzy duplicates
- [ ] normalized keys
- [ ] lowercase/case-folding
- [ ] whitespace stripping
- [ ] punctuation handling
- [ ] false-positive discussion
- [ ] `is_outlier`
- [ ] `is_duplicate`
- [ ] `dq_reason`
- [ ] clean/quarantine split
- [ ] cleaning report
- [ ] rows removed
- [ ] values filled
- [ ] values changed per rule
- [ ] rows quarantined
- [ ] Bronze preservation
- [ ] “do not fix what you do not understand”

### Exercise and engineering

- [ ] `clean_orders.py`
- [ ] latest order by `order_id` + `updated_at`
- [ ] customer-level country forward fill
- [ ] status normalization
- [ ] per-country IQR
- [ ] `silver_orders`
- [ ] `quarantine_orders`
- [ ] `dq_reason`
- [ ] cleaning report
- [ ] row reconciliation
- [ ] prediction-first learning
- [ ] debugging
- [ ] testing
- [ ] edge cases
- [ ] performance considerations
- [ ] auditability
- [ ] common anti-patterns
- [ ] production checklist
- [ ] checkpoint
- [ ] cheat sheet

