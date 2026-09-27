# 09 — Time Series, Resampling, and Rolling Windows

> **Stage 2 — Python for Data Engineering → Module 2.3 — DataFrames with pandas**
>
> **Topic 09:** Time series: resampling and rolling windows  
> **Progression:** Basic → Intermediate → Advanced → Production-oriented
>
> **Core mental model**
>
> ```text
> Timestamp
>     ↓
> Timezone
>     ↓
> Ordering
>     ↓
> Frequency
>     ↓
> Time bins
>     ↓
> Aggregation
>     ↓
> Windows
>     ↓
> Validation
> ```
>
> **Core production principle**
>
> > Time-series correctness depends on knowing what a timestamp means, which timezone it belongs to, how it is ordered, which time boundaries define a period/window, and what missing periods actually mean.

---

## 1. Why Time Series Matters in Data Engineering

A large portion of production data is time-based:

- website events;
- application logs;
- transactions;
- orders;
- API metrics;
- system metrics;
- IoT sensor readings;
- financial market data;
- customer activity;
- operational monitoring.

A time-series pipeline does more than group records by a date.

It must answer:

```text
What instant does this timestamp represent?
Which timezone gives that timestamp meaning?
Is the data ordered?
What calendar defines a period?
Which observations belong to the same bin?
What does a rolling window contain?
What does a missing period mean?
What happens when events arrive late?
```

A mistake can produce:

- incorrect daily totals;
- shifted dates;
- missing local hours;
- duplicate local hours;
- incorrect rolling metrics;
- incorrect month/quarter reporting;
- incorrect timezone conversions;
- silently wrong business metrics.

### A concrete example

Suppose the same event arrives as:

```text
2026-01-10 23:30 UTC
```

For a UTC report, its date is:

```text
2026-01-10
```

In `Asia/Kolkata`, the same instant is:

```text
2026-01-11 05:00+05:30
```

The event therefore belongs to a different **local calendar date**.

Neither date is inherently "the correct date."

The correct date depends on the business definition of the report.

### Production lesson

> Define timestamp meaning before aggregating timestamps.

---

## 2. Time-Series Mental Model

Use this sequence:

```text
raw timestamp
      ↓
interpret timezone
      ↓
normalize / convert
      ↓
sort
      ↓
define frequency/calendar
      ↓
aggregate/resample
      ↓
calculate windows
      ↓
validate
```

### Stage 1 — Timestamp meaning

Determine whether the source timestamp means:

```text
event occurrence
event ingestion
database update
message arrival
business effective time
```

These can be different timestamps.

### Stage 2 — Timezone

Determine whether timestamps are:

```text
naive
or
timezone-aware
```

### Stage 3 — Ordering

Order-dependent calculations require chronological ordering.

### Stage 4 — Frequency

Decide whether the analysis is:

```text
minute
hour
day
week
month
quarter
```

or something more specialized.

### Stage 5 — Bins and windows

A resampling bin answers:

> Which observations belong to this fixed calendar/time bucket?

A rolling window answers:

> Which recent observations contribute to this moving calculation?

### Stage 6 — Validation

A time transformation is incomplete until you can prove:

```text
expected period count
expected timezone
expected order
expected missingness
expected business totals
```

---

# 3. What Is a `DatetimeIndex`?

A `DatetimeIndex` is an index whose labels are datetime-like values.

Start with:

```python
import pandas as pd

dates = pd.to_datetime(
    [
        "2025-01-01",
        "2025-01-02",
        "2025-01-03",
    ]
)

df = pd.DataFrame(
    {"revenue": [100, 200, 150]},
    index=dates,
)

print(df)
print(type(df.index))
print(df.index.dtype)
```

Conceptually:

```text
             revenue
2025-01-01       100
2025-01-02       200
2025-01-03       150
```

The index is not merely a label.

It gives pandas time-aware operations a structured representation of:

```text
year
month
day
hour
minute
timezone
frequency
```

### Why it matters

A normal integer index can tell you:

```text
row 0
row 1
row 2
```

A `DatetimeIndex` can tell pandas:

```text
this observation happened at this point in time
```

That enables operations such as:

```python
df.resample("D")
```

and partial datetime selection.

### Production use

A `DatetimeIndex` is useful when the time axis itself is the natural index.

You can also keep the timestamp as a normal column and use:

```python
resample(..., on="timestamp")
```

when an index-based representation is not the desired schema.

---

# 4. `pd.date_range()`

`pd.date_range()` creates a regular sequence of timestamps.

Basic form:

```python
rng = pd.date_range(
    start="2025-01-01",
    periods=24,
    freq="h",
)

print(rng)
```

Important inputs include:

```text
start
end
periods
freq
```

For example:

```python
rng = pd.date_range(
    start="2025-01-01",
    end="2025-01-02 00:00",
    freq="h",
)
```

Or:

```python
rng = pd.date_range(
    start="2025-01-01",
    periods=10,
    freq="h",
)
```

### Why it matters

It can generate the **expected calendar**.

For example:

```text
expected hourly timestamps
vs
actual observed timestamps
```

This becomes a central technique for gap detection.

### Prediction exercise

```text
start = 2025-01-01 00:00
periods = 24
freq = h
```

Question:

> How many timestamps should be created?

Answer:

```text
24
```

---

# 5. Sorting Time

Time-dependent operations should use deliberate ordering.

For an index:

```python
df = df.sort_index()
```

For a timestamp column:

```python
df = df.sort_values(
    "timestamp"
)
```

### Shuffled example

```python
df = pd.DataFrame(
    {
        "timestamp": pd.to_datetime(
            [
                "2025-01-03 10:00",
                "2025-01-01 10:00",
                "2025-01-02 10:00",
            ]
        ),
        "revenue": [300, 100, 200],
    }
)
```

Sort:

```python
df = df.sort_values(
    "timestamp"
)
```

### Why sorting matters

These operations have order-dependent meaning:

```text
shift
diff
pct_change
cumsum
rolling
grouped rolling
```

If the rows are not in the intended chronological order, "previous" may mean:

```text
previous row in the file
```

rather than:

```text
previous observation in time
```

### Production rule

> When a calculation has a temporal meaning, make the temporal ordering explicit.

---

# 6. Partial-String Datetime Selection

With an appropriate `DatetimeIndex`, pandas supports partial-string selection.

Example:

```python
dates = pd.date_range(
    "2025-03-01",
    periods=31,
    freq="D",
)

df = pd.DataFrame(
    {"revenue": range(31)},
    index=dates,
)

march = df.loc["2025-03"]
```

This selects the March portion of the index.

A date range can also be selected:

```python
period = df.loc[
    "2025-03-10":"2025-03-20"
]
```

### Why this is useful

It lets engineers work naturally with:

```text
year
year-month
date interval
```

without manually creating string filters.

### Important condition

The index must actually represent datetime-like values.

### Production caution

Time index ordering and timezone semantics still matter.

Do not treat partial selection as a substitute for defining the report timezone.

---

# 7. Naive vs Timezone-Aware Datetimes

## Naive timestamp

A naive timestamp has no timezone context.

```text
2025-03-10 10:00
```

This tells you the clock reading.

It does not tell you whether the intended instant is:

```text
10:00 UTC
10:00 Asia/Kolkata
10:00 America/New_York
```

## Timezone-aware timestamp

A timezone-aware timestamp carries timezone information.

Example:

```text
2025-03-10 10:00+05:30
```

This identifies the instant relative to UTC.

### Why this matters

A naive timestamp is not automatically wrong.

It is incomplete until the source contract tells you what timezone it represents.

### Production question

Before processing a timestamp column, ask:

```text
Is it UTC?
Is it local time?
Is timezone encoded elsewhere?
Is this an ingestion timestamp or business timestamp?
```

---

# 8. `tz_localize()`

`tz_localize` attaches timezone meaning to a timezone-naive timestamp/index.

Example:

```python
import pandas as pd

ts = pd.to_datetime(
    [
        "2025-01-01 10:00",
        "2025-01-02 10:00",
    ]
)

localized = ts.tz_localize(
    "UTC"
)

print(localized)
```

Before:

```text
2025-01-01 10:00
```

After:

```text
2025-01-01 10:00+00:00
```

The local clock reading stays:

```text
10:00
```

What changed?

```text
timezone meaning was attached
```

### Mental model

```text
naive local clock
      ↓
tz_localize
      ↓
timezone-aware instant interpretation
```

### Critical distinction

Localization is not the same as conversion.

If the source actually meant:

```text
2025-01-01 10:00 Asia/Kolkata
```

then this is correct:

```python
ts.tz_localize(
    "Asia/Kolkata"
)
```

Calling:

```python
ts.tz_localize("UTC")
```

would give the timestamp a different meaning.

---

# 9. `tz_convert()`

`tz_convert` changes the timezone representation of an already timezone-aware timestamp while preserving the underlying instant.

Example:

```python
utc = pd.to_datetime(
    [
        "2025-01-01 10:00",
        "2025-01-02 10:00",
    ]
).tz_localize("UTC")

new_york = utc.tz_convert(
    "America/New_York"
)

print(new_york)
```

Conceptually:

```text
UTC:
2025-01-01 10:00+00:00

New York:
2025-01-01 05:00-05:00
```

The clock changes.

The instant does not.

### Mental model

```text
aware instant
      ↓
tz_convert
      ↓
same instant
different local representation
```

---

# 10. `tz_localize` vs `tz_convert`

| Operation | Starting data | What it does | Clock time |
|---|---|---|---|
| `tz_localize` | timezone-naive | attaches timezone meaning | stays the same |
| `tz_convert` | timezone-aware | converts the same instant to another timezone | changes |

Memorize:

```text
naive → tz_localize()

aware → tz_convert()
```

Typical mistake:

```python
aware.tz_localize("America/New_York")
```

when the timestamp is already timezone-aware.

That is an operation-order problem.

---

# 11. UTC-First Production Pattern

A strong production pattern is:

```text
ingest
  ↓
interpret source timestamp correctly
  ↓
normalize to UTC
  ↓
store/compute in UTC
  ↓
convert to local timezone at reporting/presentation boundaries
```

Why this helps:

- distributed systems have one canonical timeline;
- cross-region comparisons are simpler;
- ordering is easier to reason about;
- joins use a common time reference;
- storage semantics are clearer;
- reproducibility improves.

Example:

```python
events["timestamp"] = (
    pd.to_datetime(
        events["timestamp"],
        utc=True,
    )
)
```

### Important qualification

UTC is a strong production pattern, not the only possible architecture.

A domain may require preserving a source-local timestamp for audit or regulatory reporting.

The key is to store enough information to preserve the original meaning.

---

# 12. `shift()`

`shift(1)` moves values by one row position.

Example:

```python
df = pd.DataFrame(
    {
        "revenue": [100, 120, 150],
    },
    index=pd.date_range(
        "2025-01-01",
        periods=3,
        freq="D",
    ),
)

df["previous"] = (
    df["revenue"].shift(1)
)
```

Expected conceptually:

```text
            revenue  previous
2025-01-01      100       NaN
2025-01-02      120     100.0
2025-01-03      150     120.0
```

The first row has no previous observation.

### Time-series meaning

If sorted chronologically:

```text
current row
    ↓
previous chronological row
```

If unsorted:

```text
current row
    ↓
previous file row
```

Those are not necessarily the same.

---

# 13. Grouped `shift()`

For independent time series per group:

```python
df = df.sort_values(
    ["country", "timestamp"]
)

df["previous_revenue"] = (
    df.groupby("country")["revenue"]
    .shift(1)
)
```

Now each country has its own previous value.

Example:

```text
country | date | revenue | previous
IN      | D1   | 100     | NaN
IN      | D2   | 120     | 100
US      | D1   | 200     | NaN
US      | D2   | 220     | 200
```

There is no accidental cross-country previous value.

---

# 14. `diff()`

`diff()` calculates:

```text
current value - previous value
```

Example:

```python
df["change"] = (
    df["revenue"].diff()
)
```

For:

```text
100
120
150
```

the differences are:

```text
NaN
20
30
```

Grouped:

```python
df = df.sort_values(
    ["country", "timestamp"]
)

df["revenue_change"] = (
    df.groupby("country")["revenue"]
    .diff()
)
```

### Use cases

- revenue change;
- sensor change;
- latency change;
- inventory movement;
- account balance movement.

The first observation in each group has no previous value, so its difference is naturally missing.

---

# 15. `pct_change()`

`pct_change()` calculates fractional change relative to a previous observation.

Example:

```python
df["growth"] = (
    df["revenue"].pct_change()
)
```

If revenue changes:

```text
100 → 120
```

then:

```text
(120 - 100) / 100
=
0.20
```

The fractional result is:

```text
0.20
```

If you want a displayed percent:

```python
df["growth_pct"] = (
    df["revenue"].pct_change() * 100
)
```

### Important edge cases

If the previous value is:

```text
0
```

the ratio is not a normal finite growth rate.

Treat such cases explicitly.

Also remember:

> In current pandas usage, `pct_change` should not rely on the older fill-method behavior; fill missing values explicitly before the calculation when that is actually part of the business logic. citeturn586412search3

---

# 16. `shift` vs `diff` vs `pct_change`

| Operation | Meaning | Example |
|---|---|---|
| `shift` | previous value | previous day's revenue |
| `diff` | absolute difference | change in balance |
| `pct_change` | relative/fractional difference | growth rate |

Mental model:

```text
shift
→ previous value

diff
→ current - previous

pct_change
→ (current - previous) / previous
```

---

# 17. Resampling — What It Means

Resampling changes observations from one time frequency to another.

Examples:

```text
minute → hour
hour   → day
day    → month
```

A useful mental model is:

```text
resample
=
time-based grouping
+
aggregation
```

For example:

```python
df.resample("D").sum()
```

means:

```text
put timestamps into daily time bins
then sum each bin
```

This is different from:

```text
ordinary categorical groupby
```

because the groups are defined by time intervals.

---

# 18. Basic `resample()`

Suppose:

```python
idx = pd.date_range(
    "2025-01-01 00:00",
    periods=6,
    freq="h",
)

df = pd.DataFrame(
    {"revenue": [10, 20, 30, 40, 50, 60]},
    index=idx,
)
```

Daily aggregation:

```python
daily = df.resample("D").sum()
```

Hourly aggregation:

```python
hourly = df.resample("h").sum()
```

Minute aggregation:

```python
minute = df.resample("min").sum()
```

### Important

`resample()` returns a resampling object and then the aggregation determines the resulting value.

Current pandas documents `resample()` as a time-based grouping operation; the input needs a datetime-like index or a datetime-like column supplied through `on=`/`level=`. citeturn683881search0turn683881search1

---

# 19. Weekly Resampling

Use:

```python
weekly = df.resample(
    "W"
).sum()
```

But do not interpret:

```text
"W"
```

as merely:

```text
every seven arbitrary days
```

Weekly frequency follows calendar-week semantics.

### Production question

Ask:

```text
Which weekday anchors the week?
What timezone defines the day?
Does the reporting organization use calendar weeks or fiscal weeks?
```

For an ordinary calendar-week report, `W` can be appropriate.

For specialized retail/fiscal calendars, use the appropriate calendar design.

---

# 20. Month-End vs Month-Start

Current pandas uses:

```text
ME
```

for month-end frequency, and:

```text
MS
```

for month-start frequency. citeturn586412search0

Example:

```python
month_end = (
    df.resample("ME")
    .sum()
)
```

Month start:

```python
month_start = (
    df.resample("MS")
    .sum()
)
```

Mental model:

```text
ME
→ bins represented at month-end labels

MS
→ bins represented at month-start labels
```

These are different reporting conventions.

---

# 21. Frequency Aliases

Useful current aliases include:

| Alias | Meaning |
|---|---|
| `D` | calendar day |
| `h` | hour |
| `min` | minute |
| `W` | week |
| `ME` | month end |
| `MS` | month start |
| `B` | business day |
| `C` | custom business day |
| `QE` | quarter end |
| `QS` | quarter start |

The exact set of aliases is larger; the important point for this chapter is to use explicit, current frequency strings.

Current pandas documentation lists `h` for hourly, `ME` for month end, `MS` for month start, and business/custom-business offsets. citeturn586412search0

### Version awareness

Frequency aliases have evolved across pandas versions.

When writing new production code:

```text
use current documented aliases
+
pin/test the pandas version
```

---

# 22. Resampling Bins

A resampling operation assigns observations to time intervals.

Imagine hourly bins:

```text
00:00        01:00        02:00        03:00
 |------------|------------|------------|
     bin 1         bin 2         bin 3
```

The timestamp:

```text
01:15
```

belongs to the interval containing:

```text
01:00 → 02:00
```

But boundary timestamps such as:

```text
01:00
```

require a rule.

That is what:

```text
closed
label
```

help define.

---

# 23. `label=`

`label` chooses which boundary timestamp names the resulting bin.

```python
left_labeled = df.resample(
    "h",
    label="left",
).sum()
```

or:

```python
right_labeled = df.resample(
    "h",
    label="right",
).sum()
```

Mental model:

```text
label
=
what timestamp represents the bin in the output
```

It does not by itself determine which observations belong to the bin.

---

# 24. `closed=`

`closed` chooses which side of the interval is included.

```python
left_closed = df.resample(
    "h",
    closed="left",
).sum()
```

or:

```python
right_closed = df.resample(
    "h",
    closed="right",
).sum()
```

Mental model:

```text
closed
=
which boundary belongs to the interval
```

### Interval notation

Left-closed:

```text
[10:00, 11:00)
```

means:

```text
10:00 included
11:00 excluded
```

Right-closed:

```text
(10:00, 11:00]
```

means:

```text
10:00 excluded
11:00 included
```

---

# 25. `label` vs `closed`

Memorize:

```text
label
→ how the bin is named

closed
→ which boundary belongs to the bin
```

| Parameter | Question |
|---|---|
| `label` | Which boundary timestamp labels this result? |
| `closed` | Which boundary is included in the interval? |

Current pandas documents separate defaults for these parameters depending on the frequency; for example, weekly/month-end-style frequencies use different defaults than fixed tick frequencies. Therefore, specify them explicitly when bin semantics are important. citeturn683881search0

---

# 26. Boundary Prediction Exercise

Create:

```python
idx = pd.to_datetime(
    [
        "2025-01-01 10:00",
        "2025-01-01 10:30",
        "2025-01-01 11:00",
    ]
)

df = pd.DataFrame(
    {"value": [1, 2, 3]},
    index=idx,
)
```

Now predict:

```python
result = df.resample(
    "h",
    closed="left",
    label="left",
).sum()
```

Question:

```text
Which bin receives 10:00?
Which bin receives 11:00?
What labels the first bin?
```

Then run.

Repeat with:

```python
result = df.resample(
    "h",
    closed="right",
    label="right",
).sum()
```

The point is not memorizing one answer.

The point is understanding interval boundaries.

---

# 27. `asfreq()`

`asfreq()` changes frequency/alignment without performing the same general grouped aggregation as `resample()`.

Example:

```python
series = pd.Series(
    [10, 20],
    index=pd.to_datetime(
        [
            "2025-01-01",
            "2025-01-03",
        ]
    ),
)

hourly = series.asfreq(
    "D"
)
```

The requested daily frequency creates the expected date labels and leaves missing positions as missing when no source observation exists.

### Mental distinction

```text
asfreq
→ re-express/select at a frequency

resample
→ form time bins + aggregate
```

They are not interchangeable.

---

# 28. `resample()` vs `asfreq()`

| Operation | Main purpose |
|---|---|
| `resample` | group observations into time bins and reduce/transform |
| `asfreq` | align a series to a specified frequency |
| `reindex` | align explicitly to a chosen set of labels |

For example:

```python
daily_sum = df.resample(
    "D"
).sum()
```

asks:

> What is the sum in each day?

While:

```python
daily_values = df.asfreq(
    "D"
)
```

asks:

> What value exists at each daily frequency point?

---

# 29. Upsampling

Upsampling moves to a finer frequency.

Examples:

```text
day → hour
hour → minute
minute → second
```

Example:

```python
daily = pd.Series(
    [100, 200],
    index=pd.to_datetime(
        [
            "2025-01-01",
            "2025-01-02",
        ]
    ),
)

hourly = daily.resample(
    "h"
).asfreq()
```

The new timestamps did not necessarily exist in the source.

Therefore they are naturally missing.

### Production question

> What should newly created timestamps mean?

Possible answers:

```text
unknown
not measured
carry previous state
true zero
```

The pipeline must decide.

---

# 30. Upsampling with `ffill`

A common state-carrying pattern is:

```python
hourly = (
    daily
    .resample("h")
    .ffill()
)
```

This means:

> Carry the last observed value forward into newly created positions.

Current pandas documents `resample(...).ffill()` as a supported upsampling pattern. citeturn683881search1

### Appropriate example

A device configuration state:

```text
09:00 → config=A
```

and no new configuration appears until:

```text
13:00
```

Carrying `A` into the intervening hours may be meaningful.

### Dangerous example

For transaction revenue:

```text
09:00 → revenue=100
```

does not mean:

```text
10:00 revenue=100
11:00 revenue=100
12:00 revenue=100
```

Forward filling transactional measures would invent observations.

### Production rule

> Use `ffill` after upsampling only when the measure represents a state that legitimately persists.

---

# 31. Rolling Windows

A rolling window calculates a metric over a moving set of observations.

Example:

```python
df["rolling_mean"] = (
    df["revenue"]
    .rolling(7)
    .mean()
)
```

As the current row advances, the window advances.

Mental model:

```text
row 1
row 2
row 3
...
       [window moves]
```

Rolling windows are often used for:

- trend smoothing;
- monitoring;
- anomaly detection;
- recent averages;
- trailing business metrics.

---

# 32. `rolling(7)` — Count-Based Window

```python
df["rolling_mean"] = (
    df["revenue"]
    .rolling(7)
    .mean()
)
```

means:

> Use seven observations/rows in the rolling calculation.

It does **not** inherently mean:

```text
seven calendar days
```

If data is daily and complete, the two meanings may coincide.

If data is irregular, they can differ sharply.

---

# 33. `rolling("7D")` — Time-Based Window

A time-based rolling window uses elapsed time.

```python
df["rolling_7d"] = (
    df["revenue"]
    .rolling("7D")
    .mean()
)
```

This means the window is defined by:

```text
seven days of time
```

rather than:

```text
seven rows
```

This is critical for irregular event data.

---

# 34. `rolling(7)` vs `rolling("7D")`

Use irregular data:

```python
idx = pd.to_datetime(
    [
        "2025-01-01",
        "2025-01-02",
        "2025-01-08",
        "2025-01-09",
        "2025-01-10",
    ]
)

df = pd.DataFrame(
    {
        "revenue": [
            100,
            120,
            180,
            200,
            220,
        ]
    },
    index=idx,
)
```

Compare:

```python
count_window = (
    df["revenue"]
    .rolling(7)
    .mean()
)

time_window = (
    df["revenue"]
    .rolling("7D")
    .mean()
)
```

### Why they differ

At:

```text
2025-01-10
```

the count-based window may include all available recent rows because there are fewer than seven rows total.

The time-based window considers only observations within the defined elapsed-time interval.

### Mental model

```text
rolling(7)
→ "last 7 observations"

rolling("7D")
→ "observations in the recent 7-day interval"
```

---

# 35. Why Count-Based Windows Can Mislead

Suppose:

```text
Day 1
Day 2
Day 8
Day 9
Day 10
```

A seven-row window is not a seven-day business window.

It is a seven-observation window.

For irregular event streams:

```text
web events
IoT events
logs
transactions
```

there may be no observation on every day.

### Production rule

> Define the window using the same unit as the business question.

---

# 36. `min_periods`

`min_periods` controls how many observations are required before pandas returns a rolling result.

Example:

```python
rolling = (
    df["revenue"]
    .rolling(
        "7D",
        min_periods=3,
    )
    .mean()
)
```

Interpretation:

```text
fewer than 3 valid observations
→ result is missing
```

### Why it matters

Without a minimum:

```text
one observation
```

can produce an apparently meaningful average.

But the business rule might require:

```text
at least 3 observations
```

before exposing a metric.

Current pandas rolling documentation describes `min_periods` as the minimum number of observations required for a value. citeturn370811search3

---

# 37. `center`

By default, rolling results are aligned toward the current/trailing position.

Use:

```python
centered = (
    df["revenue"]
    .rolling(
        7,
        center=True,
    )
    .mean()
)
```

Mental model:

```text
default:
[older values ... current]

center=True:
[older ... current ... newer]
        ^
      result
```

### Use cases

Centered windows can be useful for:

```text
smoothing
retrospective analysis
signal processing
```

But they are often inappropriate for real-time dashboards because centered windows can depend on future observations relative to the result timestamp.

---

# 38. Rolling Aggregations

Common examples:

```python
df["mean_7"] = (
    df["revenue"]
    .rolling(7)
    .mean()
)

df["sum_7"] = (
    df["revenue"]
    .rolling(7)
    .sum()
)

df["min_7"] = (
    df["revenue"]
    .rolling(7)
    .min()
)

df["max_7"] = (
    df["revenue"]
    .rolling(7)
    .max()
)

df["std_7"] = (
    df["revenue"]
    .rolling(7)
    .std()
)
```

The important skill is not memorizing every reducer.

It is understanding:

```text
window definition
+
ordering
+
minimum observations
+
alignment
```

---

# 39. `expanding`

An expanding window grows from the beginning of the series.

```python
df["expanding_mean"] = (
    df["revenue"]
    .expanding()
    .mean()
)
```

Mental model:

```text
row 1
[1]

row 2
[1, 2]

row 3
[1, 2, 3]

row 4
[1, 2, 3, 4]
```

Compare:

```text
rolling
→ fixed/moving window

expanding
→ growing historical window
```

Typical use:

```text
cumulative average
historical baseline
running statistics
```

---

# 40. `ewm`

Exponentially weighted calculations assign more weight to recent observations.

Example:

```python
df["ewm_mean"] = (
    df["revenue"]
    .ewm(span=7)
    .mean()
)
```

High-level idea:

```text
older observations
→ lower weight

recent observations
→ higher weight
```

This can react more quickly to recent changes than a simple rolling average.

Keep the statistical parameters tied to a business meaning.

Do not choose:

```text
span=7
```

merely because the report is called "7-day."

An EWM parameter is not automatically a seven-calendar-day window.

---

# 41. `rolling` vs `expanding` vs `ewm`

| Operation | Window concept | Typical use |
|---|---|---|
| `rolling` | moving fixed/count or time-based window | trailing metrics |
| `expanding` | all history accumulated up to current point | cumulative statistics |
| `ewm` | weighted history, recent observations weighted more | smoothing/fast-reacting trend |

The business question should drive the choice.

---

# 42. Per-Group Time Series

Many pipelines contain independent time series:

```text
country
device
customer
branch
service
```

The operations should remain separated by group.

Example pattern:

```python
df.groupby(
    "country"
).resample("D")["revenue"].sum()
```

or:

```python
df.groupby(
    "country"
).rolling("7D")["revenue"].mean()
```

The key principle is:

> Do not allow one entity's time series to leak into another entity's window.

---

# 43. `groupby(...).resample(...)`

Example:

```python
df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    utc=True,
)

daily = (
    df.groupby("country")
    .resample(
        "D",
        on="timestamp",
    )["revenue"]
    .sum()
)
```

Conceptually the grouping is:

```text
country
+
daily time bucket
```

So:

```text
IN + Day 1
IN + Day 2
US + Day 1
US + Day 2
```

are separate time series.

### Result structure

Depending on the exact expression, the result can contain a MultiIndex such as:

```text
(country, timestamp)
```

Inspect it before using it downstream.

---

# 44. `groupby(...).rolling(...)`

Example:

```python
df = df.sort_values(
    ["country", "timestamp"]
)

rolling = (
    df.groupby("country")
    .rolling(
        "7D",
        on="timestamp",
    )["revenue"]
    .mean()
)
```

This calculates rolling statistics independently inside each country.

### Critical requirement

The timestamp ordering must be intentional within each group.

### Avoid cross-group leakage

Do not compute one global rolling series and then label the rows by country afterward.

The grouping must be part of the rolling computation itself.

---

# 45. Detecting Gaps

A gap is an expected time period for which no observation exists.

Example:

```text
Expected:
01:00
02:00
03:00
04:00
05:00

Observed:
01:00
02:00
04:00
05:00
```

Missing:

```text
03:00
```

The core pattern is:

```text
expected calendar
vs
actual timestamps
```

---

# 46. Complete Calendar with `pd.date_range()`

Build the expected range:

```python
expected = pd.date_range(
    start="2025-01-01 00:00",
    end="2025-01-01 05:00",
    freq="h",
)
```

Then compare to actual:

```python
actual = pd.DatetimeIndex(
    [
        "2025-01-01 00:00",
        "2025-01-01 01:00",
        "2025-01-01 03:00",
        "2025-01-01 04:00",
        "2025-01-01 05:00",
    ]
)
```

Missing:

```python
missing = expected.difference(
    actual
)
```

Expected:

```text
2025-01-01 02:00
```

---

# 47. Missing Period vs No Event

This distinction is critical.

## No event occurred

The system is healthy, and:

```text
zero events
```

is a valid state.

## Missing data

An event should have been present, but it was not received.

## Unknown

The pipeline cannot determine whether the absence means:

```text
zero
or
missing
```

### Example

A website may legitimately have:

```text
0 orders at 03:00
```

But if the event collector stopped sending data at:

```text
03:00
```

then:

```text
03:00 missing
```

is not the same as:

```text
03:00 zero
```

---

# 48. Building a Complete Calendar with `reindex()`

For a time series:

```python
full_index = pd.date_range(
    start=df.index.min(),
    end=df.index.max(),
    freq="h",
)

complete = df.reindex(
    full_index
)
```

Now timestamps absent from the source appear as:

```text
NaN
```

### Why this is useful

It makes calendar gaps visible.

### Important warning

`reindex()` creates labels.

It does not tell you whether a missing label means:

```text
no event
missing data
closed period
system outage
```

That interpretation still comes from the business/source contract.

---

# 49. Missing Hours Per Country

Suppose:

```text
country
timestamp
```

define separate event streams.

A conceptual procedure is:

```text
1. define expected hourly calendar
2. create each country's expected timestamps
3. compare actual timestamps
4. identify missing hours
5. classify the absence
```

One practical pattern is:

```python
expected = pd.date_range(
    start="2025-01-01 00:00",
    end="2025-01-03 23:00",
    freq="h",
)

countries = df["country"].unique()

expected_index = pd.MultiIndex.from_product(
    [
        countries,
        expected,
    ],
    names=["country", "timestamp"],
)

actual_index = pd.MultiIndex.from_frame(
    df[
        ["country", "timestamp"]
    ].drop_duplicates()
)

missing = expected_index.difference(
    actual_index
)
```

This is a calendar-completeness diagnostic.

For large production workloads, the size of the constructed index must be budgeted carefully.

---

# 50. Detecting Gaps with Frequency

Suppose:

```text
regular:
00:00
01:00
02:00
03:00
```

versus:

```text
irregular:
00:00
01:00
03:00
06:00
```

The irregular series has multiple gaps.

A first diagnostic:

```python
deltas = (
    df.index
    .sort_values()
    .to_series()
    .diff()
)
```

Inspect:

```python
print(
    deltas.value_counts(
        dropna=False
    )
)
```

If the intended frequency is hourly, unexpected values such as:

```text
2 hours
3 hours
```

are gap signals.

---

# 51. DST — Why It Matters

Daylight-saving time changes local clock representations in some timezones.

Two major cases:

```text
spring forward
→ a local hour does not exist

fall back
→ a local hour occurs twice
```

Not every timezone observes DST.

Do not assume:

```text
local time always has 24 unique clock hours per day
```

---

# 52. Non-Existent Local Times

During spring-forward, clocks can jump forward.

For example, a local time such as:

```text
02:30
```

may not exist in a particular timezone on a particular date.

When localizing naive timestamps, pandas allows explicit policies through:

```python
nonexistent=...
```

Example:

```python
naive = pd.to_datetime(
    [
        "2015-03-29 02:30",
        "2015-03-29 03:30",
    ]
)

localized = naive.tz_localize(
    "Europe/Warsaw",
    nonexistent="shift_forward",
)
```

Pandas supports policies such as:

```text
raise
shift_forward
shift_backward
NaT
timedelta
```

for nonexistent local times. citeturn370811search0turn370811search2

### Production rule

Choose a policy based on what the source timestamp means.

Do not silently shift a timestamp unless the business rule permits it.

---

# 53. Ambiguous Local Times

During fall-back, a wall-clock hour can occur twice.

For example:

```text
01:30 DST
01:30 standard time
```

have:

```text
same local clock reading
different instants
```

When localizing a naive series, use:

```python
ambiguous=...
```

Example:

```python
naive = pd.to_datetime(
    [
        "2018-10-28 02:00",
        "2018-10-28 02:30",
    ]
)

localized = naive.tz_localize(
    "CET",
    ambiguous="NaT",
)
```

Pandas supports strategies including:

```text
raise
infer
NaT
boolean values/arrays
```

for ambiguous local times. citeturn370811search0

---

# 54. `nonexistent=` and `ambiguous=`

| Parameter | Problem | Typical strategies |
|---|---|---|
| `nonexistent` | local time never occurred | raise, shift, `NaT`, timedelta |
| `ambiguous` | local time occurred twice | raise, infer, `NaT`, explicit flags |

### Production lesson

A timezone conversion library cannot decide your business meaning.

It can only apply a policy you specify.

---

# 55. UTC Storage + Local Reporting

A strong architecture is:

```text
store/compute → UTC
report/display → local timezone
```

For example:

```python
utc = pd.to_datetime(
    df["timestamp"],
    utc=True,
)

df["new_york_time"] = (
    utc.dt.tz_convert(
        "America/New_York"
    )
)

df["kolkata_time"] = (
    utc.dt.tz_convert(
        "Asia/Kolkata"
    )
)
```

The same UTC instant can have different local dates/hours.

### Important

`Asia/Kolkata` does not follow the same DST transitions as `America/New_York`.

Timezone behavior is geographic and rule-based.

---

# 56. Why Local-Time Aggregation Can Produce Errors

Suppose a UTC event series is:

```text
2026-03-08 06:30 UTC
2026-03-08 07:30 UTC
...
```

When converted to New York around the spring transition, local clock hours do not map one-to-one to UTC hours.

If you aggregate:

```text
first in UTC
vs
first in local time
```

the day and hour buckets can differ.

Therefore define:

```text
report timezone
```

before computing:

```text
daily
weekly
monthly
```

metrics.

---

# 57. `Period` and `to_period()`

A `Timestamp` represents a point in time.

A `Period` represents a span/calendar period.

Examples:

```text
Timestamp:
2025-03-15 10:32

Period:
2025-03
```

Use:

```python
period = pd.Period(
    "2025-03",
    freq="M",
)
```

Or convert a datetime value:

```python
df["month"] = (
    df["timestamp"]
    .dt.to_period("M")
)
```

The purpose is to represent:

```text
calendar period
```

rather than an exact instant.

---

# 58. Timestamp vs Period

| Type | Meaning | Example |
|---|---|---|
| Timestamp | specific instant | `2025-03-15 10:32` |
| Period | calendar/time span | `2025-03` |
| Period | fiscal quarter | `2025Q4` under a chosen fiscal convention |

Use `Timestamp` for:

```text
event time
transaction time
log time
```

Use `Period` when the business question is explicitly about:

```text
month
quarter
fiscal period
reporting span
```

---

# 59. Fiscal Months and Quarters

Fiscal calendars differ from calendar calendars.

For example, an organization may define:

```text
fiscal year ends in March
```

Then:

```text
Q1
```

does not necessarily mean:

```text
January–March
```

Pandas supports anchored quarterly periods such as:

```python
quarter = pd.Period(
    "2011Q4",
    freq="Q-MAR",
)
```

`Q-MAR` means a fiscal year ending in March. Other year-end months can be represented using other anchored quarterly frequencies. citeturn586412search0

### Important

Never assume one fiscal calendar applies everywhere.

Document:

```text
fiscal-year start/end
quarter boundaries
timezone
```

---

# 60. Business Days

A business-day calendar is not necessarily:

```text
Monday–Friday
```

Some organizations observe:

```text
regional holidays
market holidays
special closures
non-standard weekends
```

Pandas has a business-day frequency:

```python
business_days = pd.date_range(
    "2025-01-01",
    periods=10,
    freq="B",
)
```

`B` represents business days under the standard weekday convention. citeturn586412search0

### Production question

Ask:

> What calendar does the business actually use?

---

# 61. Custom Calendars

For specialized schedules, pandas provides custom business-day concepts.

Example:

```python
custom_day = pd.offsets.CustomBusinessDay(
    weekmask="Sun Mon Tue Wed Thu",
    holidays=[
        "2025-05-01",
    ],
)
```

Then:

```python
next_day = (
    pd.Timestamp("2025-04-30")
    + custom_day
)
```

A custom calendar might be required for:

- financial markets;
- banking;
- manufacturing;
- regional operations.

Pandas documents `CustomBusinessDay` for custom weekmasks and holiday calendars. citeturn586412search0turn586412search2

Do not assume a custom calendar is needed merely because a dataset is financial.

---

# 62. Late-Arriving Events

A late event has:

```text
event timestamp = historical time
arrival timestamp = later time
```

Example:

```text
Event time:
2026-01-10 12:00

Arrival time:
2026-01-12 08:00
```

The event belongs to the historical period:

```text
January 10
```

but arrived two days later.

### Why this matters

It can change:

```text
daily aggregates
rolling metrics
reports
alerts
backfills
```

---

# 63. Out-of-Order Events

Events can arrive in:

```text
arrival order
```

that differs from:

```text
event-time order
```

Example:

```text
arrives first:
event at 10:00

arrives second:
event at 09:00
```

For event-time calculations, sort by event time.

```python
df = df.sort_values(
    "event_time"
)
```

This matters for:

```text
shift
diff
cumsum
rolling
gap detection
```

---

# 64. Rolling Recalculation After Late Data

Suppose:

```text
Day 10 rolling metric
depends on Days 4–10
```

A late Day 7 event arrives.

Then:

```text
Day 7 metric changes
Day 8 may change
Day 9 may change
Day 10 may change
```

Therefore:

> A late-arriving event can invalidate previously computed rolling metrics.

This does not necessarily mean recomputing the entire dataset.

The engineering problem is to identify:

```text
earliest affected point
+
window width
+
latest impacted output
```

---

# 65. Time-Series Recalculation Boundaries

Conceptually determine:

```text
earliest affected timestamp
latest affected timestamp
window width
impacted periods
```

Example:

```text
late event:
2026-01-07 10:00

rolling window:
7 days

possible affected output range:
2026-01-07 → later periods whose windows include Jan 7
```

The exact range depends on:

```text
window semantics
aggregation
alignment
late-event policy
```

Detailed incremental/orchestration architecture is covered later in the broader roadmap.

---

# 66. Resampling vs Rolling

| Operation | Core question |
|---|---|
| Resampling | How much happened in each fixed time bucket? |
| Rolling | What is the metric over the recent moving window? |

Example:

```text
daily revenue
```

comes from:

```python
df.resample("D").sum()
```

A seven-day trailing average can come from:

```python
daily["revenue"].rolling("7D").mean()
```

Resampling produces fixed calendar buckets.

Rolling produces overlapping windows.

---

# 67. Resample vs Groupby

Ordinary `groupby`:

```python
df.groupby("country")
```

creates groups from category values.

Resampling:

```python
df.resample("h")
```

creates groups from time intervals.

They can be combined:

```python
df.groupby("country").resample(
    "h",
    on="timestamp",
)["revenue"].sum()
```

Mental model:

```text
country dimension
+
time bucket
```

This is common for per-entity time-series metrics.

---

# 68. Resample vs `asfreq` vs `reindex`

| Operation | Purpose |
|---|---|
| `resample` | time-based grouping + aggregation |
| `asfreq` | align/select at a target frequency |
| `reindex` | explicitly align to a specified index/calendar |

Examples:

```python
daily = df.resample(
    "D"
).sum()
```

```python
daily_points = df.asfreq(
    "D"
)
```

```python
expected = pd.date_range(
    df.index.min(),
    df.index.max(),
    freq="D",
)

complete = df.reindex(
    expected
)
```

Use the one matching the question.

---

# 69. Time-Series Production Decision Framework

Before executing:

```text
1. Is my timestamp naive or aware?
2. What timezone does it represent?
3. Should it be normalized to UTC?
4. Is the data sorted?
5. Is the series regular or irregular?
6. What frequency is required?
7. Am I aggregating or reindexing?
8. Is my window row-count-based or time-based?
9. What does missing time mean?
10. Is zero different from missing?
11. Are DST transitions relevant?
12. Is this calendar time or fiscal/business time?
13. Can late events change historical calculations?
```

This is the production decision framework.

---

# 70. HANDS-ON EXERCISE — `timeseries_metrics.py`

> **Do not create `timeseries_metrics.py` for this Markdown task.**
>
> This section is the complete implementation specification.

## Exercise objective

Build a production-style time-series metrics pipeline over:

```text
90 days of per-minute website events in UTC
```

The learner should demonstrate:

```text
DatetimeIndex
date_range
sorting
resampling
rolling
gap detection
timezone conversion
DST reasoning
month-end reporting
fiscal periods
hand-computed validation
```

---

# 71. Exercise Dataset

Use fields such as:

```text
timestamp
country
event_type
revenue
```

Recommended meaning:

```text
timestamp
→ event occurrence time in UTC

country
→ country associated with the event

event_type
→ page_view / purchase / login / etc.

revenue
→ monetary value for revenue-producing events
```

Generate deterministic data.

For reproducible learning:

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(
    42
)

timestamps = pd.date_range(
    "2025-01-01",
    periods=90 * 24 * 60,
    freq="min",
    tz="UTC",
)
```

Then construct a DataFrame.

The exact synthetic distributions are less important than making the timestamp semantics explicit.

---

# 72. Exercise Task 1 — Hourly and Daily Event Counts

Count events using `resample`.

Example:

```python
events = events.sort_values(
    "timestamp"
)

hourly_counts = (
    events.set_index("timestamp")
    .resample("h")
    .size()
)

daily_counts = (
    events.set_index("timestamp")
    .resample("D")
    .size()
)
```

### Prediction requirements

Before running:

```text
90 days × 24 hours
=
2,160 expected hourly buckets

90 days
=
90 expected daily buckets
```

This assumes the exercise covers exactly 90 complete calendar days in UTC.

Then inspect:

```python
print(hourly_counts.shape)
print(daily_counts.shape)
```

### Validation

Check expected start/end boundaries and determine whether the generated range includes exactly the intended period.

---

# 73. Exercise Task 2 — 7-Day Rolling Average of Daily Revenue

First calculate daily revenue:

```python
daily_revenue = (
    events.set_index("timestamp")
    .groupby("country")
    .resample("D")["revenue"]
    .sum()
)
```

Then calculate a seven-day time-based rolling mean per country.

One explicit approach is:

```python
daily_df = (
    daily_revenue
    .rename("daily_revenue")
    .reset_index()
    .sort_values(
        ["country", "timestamp"]
    )
)

daily_df["rolling_7d"] = (
    daily_df
    .groupby("country")
    .rolling(
        "7D",
        on="timestamp",
        min_periods=1,
    )["daily_revenue"]
    .mean()
    .reset_index(
        level=0,
        drop=True,
    )
)
```

The final implementation should be tested carefully because grouped rolling can produce index structures that require deliberate alignment back to the original DataFrame.

### Why `rolling("7D")`?

The roadmap specifically requires:

```text
seven elapsed days
```

rather than:

```text
seven rows
```

The exercise should make the business meaning explicit.

---

# 74. Exercise Task 3 — Detect Missing Hours per Country

For each country:

```text
1. build expected hourly calendar
2. compare with observed hours
3. report missing hours
```

Start by normalizing events to unique observed hours:

```python
observed = (
    events.assign(
        hour=events["timestamp"].dt.floor("h")
    )
    [
        ["country", "hour"]
    ]
    .drop_duplicates()
)
```

Build the expected calendar:

```python
expected_hours = pd.date_range(
    start=events["timestamp"].min().floor("h"),
    end=events["timestamp"].max().floor("h"),
    freq="h",
    tz="UTC",
)
```

Then use a complete country × hour index:

```python
countries = (
    events["country"]
    .dropna()
    .unique()
)

expected_index = (
    pd.MultiIndex.from_product(
        [
            countries,
            expected_hours,
        ],
        names=["country", "hour"],
    )
)

observed_index = (
    pd.MultiIndex.from_frame(
        observed
        .rename(
            columns={"hour": "hour"}
        )
    )
)

missing = expected_index.difference(
    observed_index
)
```

### Required report

Produce:

```text
country
missing_hour
```

### Important

Classify missing hours:

```text
no events
vs
missing data
vs
unknown
```

Do not automatically label them as zeros.

---

# 75. Exercise Task 4 — Timezone Reporting

Convert UTC events into:

```text
America/New_York
Asia/Kolkata
```

Example:

```python
events["timestamp"] = pd.to_datetime(
    events["timestamp"],
    utc=True,
)

events["new_york_time"] = (
    events["timestamp"]
    .dt.tz_convert(
        "America/New_York"
    )
)

events["kolkata_time"] = (
    events["timestamp"]
    .dt.tz_convert(
        "Asia/Kolkata"
    )
)
```

### DST demonstration

Use a known New York transition date.

Spring-forward example:

```python
utc_times = pd.date_range(
    "2025-03-09 05:00",
    "2025-03-09 10:00",
    freq="h",
    tz="UTC",
)

ny_times = utc_times.tz_convert(
    "America/New_York"
)
```

Inspect the local timestamps.

You should observe that the local clock jumps over a DST hour.

### Explain

```text
UTC has continuous hourly instants.

Local New York time has a spring-forward clock transition.

Therefore local wall-clock hours are not always a one-to-one mapping
to UTC hourly labels.
```

Then separately convert to:

```text
Asia/Kolkata
```

and explain that its local-time behavior is not the same as New York's DST behavior.

---

# 76. Exercise Task 5 — Month-End Revenue

Use:

```python
month_end_revenue = (
    events.set_index("timestamp")
    .resample("ME")["revenue"]
    .sum()
)
```

### Prediction

Determine:

```text
number of months represented
first month-end
last month-end
```

### Validation

Compare:

```python
events["revenue"].sum()
```

with:

```python
month_end_revenue.sum()
```

when no filtering/deduplication has occurred and the aggregation semantics are compatible.

---

# 77. Exercise Task 6 — Fiscal Quarters with Periods

Make the fiscal calendar explicit.

Example:

```text
fiscal year ends in March
```

Then:

```python
periods = (
    events["timestamp"]
    .dt.to_period("Q-MAR")
)
```

The final exercise can aggregate by:

```python
fiscal_revenue = (
    events.assign(
        fiscal_quarter=periods
    )
    .groupby("fiscal_quarter")[
        "revenue"
    ]
    .sum()
)
```

### Important

The business must define the fiscal year.

Do not assume:

```text
Q1 = January–March
```

for every organization.

---

# 78. Exercise Task 7 — Hand-Computed Validation

Create a tiny frame:

```python
small = pd.DataFrame(
    {
        "timestamp": pd.to_datetime(
            [
                "2025-01-01 10:00",
                "2025-01-01 10:30",
                "2025-01-01 11:00",
                "2025-01-01 11:30",
            ],
            utc=True,
        ),
        "revenue": [10, 20, 30, 40],
    }
)
```

Manually calculate:

```text
hourly counts
hourly revenue
differences
rolling values
```

Then compare to pandas.

Example:

```python
expected_counts = pd.Series(
    [2, 2],
    index=pd.to_datetime(
        [
            "2025-01-01 10:00",
            "2025-01-01 11:00",
        ],
        utc=True,
    ),
)

actual_counts = (
    small
    .set_index("timestamp")
    .resample("h")
    .size()
)

pd.testing.assert_series_equal(
    actual_counts,
    expected_counts,
)
```

Use hand-computed examples before running the larger exercise.

---

# 79. Prediction-First Learning

Before every important time-series operation, predict:

```text
number of timestamps
timezone state
sorted order
number of resampling bins
bin membership
bin labels
output frequency
rolling-window membership
minimum observations
missing periods
DST behavior
late-event effect
```

Then:

```text
Predict
  ↓
Execute
  ↓
Inspect
  ↓
Assert
  ↓
Explain
```

This is not a cosmetic learning trick.

It trains you to catch:

```text
wrong timezone
wrong frequency
wrong boundary
wrong window
wrong missingness
```

before they become production bugs.

---

# 80. Bin-Drawing Exercise

Draw the hourly bins for:

```python
df.resample(
    "h",
    closed="left",
    label="left",
).sum()
```

and:

```python
df.resample(
    "h",
    closed="right",
    label="right",
).sum()
```

Use observations at:

```text
10:00
10:30
11:00
```

### Questions

```text
1. Which interval contains 10:00?
2. Which interval contains 11:00?
3. What timestamp labels the interval?
4. How do the answer and output labels change when label changes?
5. How do they change when closed changes?
```

Then execute both versions.

---

# 81. Rolling Comparison Exercise

Use irregular dates:

```text
Jan 1
Jan 2
Jan 8
Jan 9
Jan 10
```

Calculate:

```python
count_based = (
    df["value"]
    .rolling(7)
    .mean()
)

time_based = (
    df["value"]
    .rolling("7D")
    .mean()
)
```

For at least two output timestamps, list:

```text
rows included
calendar span covered
result
```

### Required explanation

State:

> `rolling(7)` is seven observations, while `rolling("7D")` is a seven-day time window.

---

# 82. Debugging Section

Time-series bugs are often semantic rather than syntactic.

Each diagnostic should follow:

```text
buggy code
→ expected behavior
→ actual behavior
→ root cause
→ corrected code
→ prevention rule
```

---

# 83. Debug 1 — Naive Timestamps Treated as UTC

### Buggy

```python
ts = pd.to_datetime(
    "2025-01-01 10:00"
)

utc = ts.tz_localize(
    "UTC"
)
```

### Expected

Source timestamp actually meant:

```text
Asia/Kolkata local time
```

### Actual

It was interpreted as:

```text
10:00 UTC
```

### Root cause

Timezone semantics were assumed instead of verified.

### Correct

```python
utc = (
    ts
    .tz_localize("Asia/Kolkata")
    .tz_convert("UTC")
)
```

### Prevention

Document the source timezone.

---

# 84. Debug 2 — `tz_convert` on Naive Data

### Buggy

```python
ts = pd.to_datetime(
    ["2025-01-01 10:00"]
)

converted = ts.tz_convert(
    "UTC"
)
```

### Actual

The data is timezone-naive.

### Correct

```python
converted = (
    ts
    .tz_localize("UTC")
    .tz_convert("America/New_York")
)
```

### Prevention

Check:

```python
print(ts.tz)
```

---

# 85. Debug 3 — `tz_localize` When Conversion Was Intended

### Buggy

```python
aware = pd.to_datetime(
    ["2025-01-01 10:00"],
    utc=True,
)

wrong = aware.tz_localize(
    "America/New_York"
)
```

### Root cause

The timestamp is already aware.

### Correct

```python
right = aware.tz_convert(
    "America/New_York"
)
```

### Prevention

Use:

```text
naive → localize
aware → convert
```

---

# 86. Debug 4 — Mixing Naive and Aware Timestamps

### Symptom

Comparisons or alignment fail.

### Root cause

One object is:

```text
timezone-naive
```

while another is:

```text
timezone-aware
```

### Correct

Normalize both according to the source contract, commonly into UTC.

```python
left = pd.to_datetime(
    left,
    utc=True,
)

right = pd.to_datetime(
    right,
    utc=True,
)
```

---

# 87. Debug 5 — Failing to Sort

### Buggy

```python
df["previous"] = (
    df["revenue"].shift()
)
```

### Expected

Previous chronological observation.

### Actual

Previous physical row.

### Correct

```python
df = df.sort_values(
    "timestamp"
)

df["previous"] = (
    df["revenue"].shift()
)
```

---

# 88. Debug 6 — Partial Selection on the Wrong Index

### Buggy

```python
df.loc["2025-03"]
```

### Root cause

The index is not a suitable datetime index.

### Correct

Convert and use:

```python
df = df.set_index(
    "timestamp"
)

df.index = pd.to_datetime(
    df.index,
    utc=True,
)
```

Then select.

---

# 89. Debug 7 — Incorrect Frequency Alias

### Symptom

Code uses an obsolete or ambiguous alias.

### Correct approach

Use current documented aliases such as:

```text
h
min
ME
MS
```

and test against the pinned pandas version.

Current pandas 3.0 documentation lists these current frequency representations. citeturn586412search0

---

# 90. Debug 8 — Wrong Resampling Frequency

### Buggy

```python
daily = df.resample(
    "h"
).sum()
```

### Expected

Daily report.

### Actual

Hourly report.

### Correct

```python
daily = df.resample(
    "D"
).sum()
```

### Prevention

Include expected frequency in the output contract.

---

# 91. Debug 9 — Incorrect `label`

### Symptom

The values are right but report timestamps represent the wrong side of the bin.

### Correct

Choose:

```python
label="left"
```

or:

```python
label="right"
```

according to the reporting convention.

---

# 92. Debug 10 — Incorrect `closed`

### Symptom

Boundary observations land in the wrong bin.

### Root cause

Interval closure was misunderstood.

### Correct

Use a boundary fixture and explicitly test:

```python
closed="left"
```

and:

```python
closed="right"
```

---

# 93. Debug 11 — Confusing Label and Closed

### Buggy assumption

```text
label controls inclusion
```

### Actual

```text
label = output label
closed = included boundary
```

### Prevention

Draw interval notation:

```text
[10:00, 11:00)
```

before executing.

---

# 94. Debug 12 — Confusing `asfreq` with `resample`

### Buggy expectation

```python
df.asfreq("D")
```

should sum all rows in each day.

### Correct

Use:

```python
df.resample("D").sum()
```

because the business question is aggregation.

---

# 95. Debug 13 — Using `ffill` for Transactions

### Buggy

```python
df.resample("h").ffill()
```

on transaction revenue.

### Root cause

A transactional measure was treated like state.

### Correct

Usually keep missing values or define an explicit zero policy.

### Prevention

Ask:

```text
Is this value a state or an event/measure?
```

---

# 96. Debug 14 — `rolling(7)` Called "7 Days"

### Buggy

```python
df["rolling_7d"] = (
    df["value"]
    .rolling(7)
    .mean()
)
```

### Root cause

Row count was confused with elapsed time.

### Correct

For a time-based rule:

```python
df["rolling_7d"] = (
    df["value"]
    .rolling("7D")
    .mean()
)
```

---

# 97. Debug 15 — Wrong `min_periods`

### Symptom

Early values appear when the metric should require a minimum data depth.

### Correct

```python
rolling = (
    df["value"]
    .rolling(
        "7D",
        min_periods=3,
    )
    .mean()
)
```

---

# 98. Debug 16 — Wrong `center`

### Symptom

A centered result is used in a real-time metric.

### Root cause

The calculation can depend on future observations relative to the result timestamp.

### Correct

For trailing production metrics, use the default trailing alignment unless the business definition explicitly calls for centering.

---

# 99. Debug 17 — Rolling Across Groups

### Buggy

```python
df["rolling"] = (
    df["revenue"]
    .rolling("7D")
    .mean()
)
```

### Expected

Separate rolling values per country.

### Correct

Group first:

```python
df = df.sort_values(
    ["country", "timestamp"]
)

df["rolling"] = (
    df.groupby("country")
    .rolling(
        "7D",
        on="timestamp",
    )["revenue"]
    .mean()
)
```

The final alignment should be validated carefully.

---

# 100. Debug 18 — Missing Hours Interpreted as Zero

### Symptom

An outage looks like:

```text
0 events
```

instead of:

```text
unknown / missing
```

### Correct

Detect the missing period separately using a complete calendar.

Do not apply:

```python
fillna(0)
```

until the business meaning has been established.

---

# 101. Debug 19 — No Events Interpreted as Missing Data

### Symptom

Legitimate quiet periods trigger an outage.

### Root cause

The pipeline assumed:

```text
no row = system failure
```

### Correct

Use business/source evidence to distinguish:

```text
zero activity
vs
missing collection
```

---

# 102. Debug 20 — Incorrect Calendar Construction

### Symptom

Too many "missing" periods are reported.

### Root causes

```text
wrong start
wrong end
wrong timezone
wrong frequency
```

### Correct

Build the expected calendar from the explicit reporting contract.

---

# 103. Debug 21 — Ignoring DST

### Symptom

A local-day report expects exactly 24 unique hourly labels on every day.

### Actual

Some timezones have:

```text
23-hour local days
25-hour local days
```

around DST transitions.

### Correct

Define whether the metric is based on:

```text
UTC elapsed time
or
local wall-clock calendar time
```

---

# 104. Debug 22 — Incorrect `nonexistent=`

### Symptom

A local timestamp during spring-forward is silently shifted.

### Root cause

Policy was chosen without business meaning.

### Correct

Use an explicit policy:

```python
nonexistent="raise"
```

when ambiguity should stop the pipeline.

Or another documented strategy when appropriate.

---

# 105. Debug 23 — Incorrect `ambiguous=`

### Symptom

Two identical wall-clock timestamps are treated as one instant.

### Root cause

Fall-back ambiguity was ignored.

### Correct

Use:

```python
ambiguous="raise"
```

or an explicit/inferred strategy appropriate to the source.

---

# 106. Debug 24 — Aggregating Local Time Without Defining Zone

### Symptom

Two daily reports disagree.

### Root cause

One report used:

```text
UTC day
```

and another used:

```text
local day
```

### Correct

Name the timezone in the metric contract.

---

# 107. Debug 25 — Month-End vs Month-Start Confusion

### Symptom

The monthly value is correct but the period label is not.

### Correct

Choose explicitly:

```python
resample("ME")
```

or:

```python
resample("MS")
```

---

# 108. Debug 26 — Treating Fiscal Quarters as Calendar Quarters

### Symptom

Financial report quarters disagree with business reporting.

### Root cause

The pipeline used calendar quarter logic.

### Correct

Represent the fiscal calendar explicitly with anchored periods.

---

# 109. Debug 27 — Incorrect Business-Day Assumption

### Symptom

Holiday dates are counted as business days.

### Root cause

The pipeline assumed Monday–Friday was the entire calendar.

### Correct

Use a defined custom business calendar where required.

---

# 110. Debug 28 — Ignoring Late Events

### Symptom

Historical metrics remain wrong after backfill.

### Root cause

The calculation assumed data was complete.

### Correct

Identify affected periods and recompute them.

---

# 111. Debug 29 — Failing to Recompute Affected Rolling Windows

### Symptom

Source data is corrected, but rolling outputs remain stale.

### Root cause

Only the event's own period was recalculated.

### Correct

Recompute all output windows that include the corrected timestamp.

---

# 112. Debug 30 — Rolling Before Sorting

### Buggy

```python
df["rolling"] = (
    df["value"]
    .rolling("7D")
    .mean()
)
```

while timestamps are unsorted.

### Correct

```python
df = df.sort_values(
    "timestamp"
)

df["rolling"] = (
    df["value"]
    .rolling("7D")
    .mean()
)
```

---

# 113. Debug 31 — Incorrect Grouped Resampling

### Symptom

Countries have unexpected totals.

### Root cause

Timestamp was not supplied correctly or grouping was performed at the wrong grain.

### Correct

Use an explicit country + timestamp definition:

```python
result = (
    df.groupby("country")
    .resample(
        "D",
        on="timestamp",
    )["revenue"]
    .sum()
)
```

Then inspect the resulting MultiIndex.

---

# 114. Debug 32 — Incorrect Grouped Rolling Alignment

### Symptom

The rolling Series does not line up with the original rows.

### Root cause

Grouped rolling often returns an index structure representing:

```text
group
+
time/index
```

### Correct

Reset/re-align deliberately, then assert the final relationship.

Do not assume positional assignment is safe.

---

# 115. Debug 33 — Period Conversion with Wrong Frequency

### Buggy

```python
df["period"] = (
    df["timestamp"]
    .dt.to_period("M")
)
```

when the business question requires:

```text
fiscal quarter ending March
```

### Correct

Use an appropriate fiscal frequency such as:

```python
df["fiscal_quarter"] = (
    df["timestamp"]
    .dt.to_period("Q-MAR")
)
```

---

# 116. Debug 34 — Losing Timezone Information Unintentionally

### Buggy

```python
local = (
    aware.tz_localize(None)
)
```

### Root cause

Timezone was removed while preserving local wall-clock values.

### Correct

If you need a different timezone, convert:

```python
local = aware.tz_convert(
    "America/New_York"
)
```

Then retain timezone awareness unless the source contract explicitly requires a naive representation.

---

# 117. Testing Section

A serious time-series test suite should test **semantics**, not just whether the function ran.

Tests should cover:

```text
timestamp parsing
timezone state
ordering
frequency
bin membership
window membership
missingness
DST
calendar logic
late-event effects
```

---

# 118. Testing `DatetimeIndex`

Test creation:

```python
idx = pd.to_datetime(
    [
        "2025-01-01",
        "2025-01-02",
    ]
)

assert isinstance(
    idx,
    pd.DatetimeIndex,
)
```

Test sorting:

```python
df = df.sort_index()

assert df.index.is_monotonic_increasing
```

Test partial selection using a known fixture.

---

# 119. Testing Timezones

Test naive data:

```python
naive = pd.to_datetime(
    ["2025-01-01 10:00"]
)

assert naive.tz is None
```

Test localization:

```python
aware = naive.tz_localize(
    "UTC"
)

assert str(aware.tz) == "UTC"
```

Test conversion:

```python
converted = aware.tz_convert(
    "Asia/Kolkata"
)

assert converted.tz is not None
```

---

# 120. Testing UTC Normalization

A production-normalization test can assert:

```python
normalized = pd.to_datetime(
    source_timestamps,
    utc=True,
)

assert str(normalized.dtype).endswith(
    ", UTC]"
)
```

More robustly, inspect individual values and the timezone.

The important contract is:

```text
all canonical event times represent UTC instants
```

---

# 121. Testing DST

Use deterministic timestamps around a known transition.

For a naive local-time fixture:

```python
naive = pd.to_datetime(
    ["2015-03-29 02:30"]
)

localized = naive.tz_localize(
    "Europe/Warsaw",
    nonexistent="NaT",
)

assert localized.isna().all()
```

For ambiguous times:

```python
naive = pd.to_datetime(
    ["2018-10-28 02:30"]
)

localized = naive.tz_localize(
    "CET",
    ambiguous="NaT",
)

assert localized.isna().all()
```

---

# 122. Testing `shift`, `diff`, `pct_change`

Given:

```text
100
120
150
```

expected:

```text
shift → NaN, 100, 120
diff → NaN, 20, 30
pct_change → NaN, 0.20, 0.25
```

Example:

```python
series = pd.Series(
    [100, 120, 150]
)

expected_diff = pd.Series(
    [float("nan"), 20.0, 30.0]
)

actual_diff = series.diff()

pd.testing.assert_series_equal(
    actual_diff,
    expected_diff,
)
```

---

# 123. Testing Resampling

Create hand-computed hourly data:

```python
idx = pd.to_datetime(
    [
        "2025-01-01 10:15",
        "2025-01-01 10:45",
        "2025-01-01 11:05",
    ],
    utc=True,
)

df = pd.DataFrame(
    {"value": [1, 2, 3]},
    index=idx,
)

actual = df.resample(
    "h"
).sum()
```

Expected:

```text
10:00 → 3
11:00 → 3
```

Assert the exact Series/DataFrame.

---

# 124. Testing Weekly/Monthly Frequencies

Test that:

```text
W
ME
MS
```

produce the intended labels.

Do not only assert:

```python
len(result) > 0
```

Assert:

```text
specific expected period labels
specific expected aggregates
```

---

# 125. Testing `label` and `closed`

Construct boundary fixtures:

```text
10:00
11:00
```

Then test both:

```python
left_closed = (
    df.resample(
        "h",
        closed="left",
        label="left",
    ).sum()
)

right_closed = (
    df.resample(
        "h",
        closed="right",
        label="right",
    ).sum()
)
```

The tests should explicitly encode which boundary belongs to which bin.

---

# 126. Testing `asfreq`

Use a series with missing frequency points:

```python
series = pd.Series(
    [10, 30],
    index=pd.to_datetime(
        [
            "2025-01-01",
            "2025-01-03",
        ]
    ),
)

actual = series.asfreq(
    "D"
)
```

Assert that:

```text
Jan 2 is present in the new frequency
Jan 2 has no observed source value
```

---

# 127. Testing Upsampling + `ffill`

```python
series = pd.Series(
    [10, 20],
    index=pd.date_range(
        "2025-01-01 00:00",
        periods=2,
        freq="h",
    ),
)

actual = (
    series.resample("30min")
    .ffill()
)
```

Assert the expected propagated values.

Also write a business-level test proving `ffill` is only being used for state-like data.

---

# 128. Testing Rolling Windows

Test count-based:

```python
actual = (
    series
    .rolling(3)
    .mean()
)
```

Test time-based:

```python
actual = (
    series
    .rolling("3D")
    .mean()
)
```

Use irregular timestamps so the distinction is actually exercised.

---

# 129. Testing `min_periods`

```python
actual = (
    series
    .rolling(
        "7D",
        min_periods=3,
    )
    .mean()
)
```

Assert:

```text
fewer than three valid observations → NaN
```

---

# 130. Testing `center`

Create a tiny frame and compare:

```python
trailing = (
    series
    .rolling(3)
    .mean()
)

centered = (
    series
    .rolling(
        3,
        center=True,
    )
    .mean()
)
```

The test should prove that the result alignment differs.

---

# 131. Testing Grouped Time Series

Test:

```text
groupby + resample
groupby + rolling
```

with at least two countries.

Then assert that:

```text
Country A never uses Country B's observations
```

This is a semantic test.

---

# 132. Testing Gap Detection

Build:

```text
00:00
01:00
03:00
```

Expected:

```text
02:00 missing
```

Example:

```python
expected = pd.date_range(
    "2025-01-01 00:00",
    "2025-01-01 03:00",
    freq="h",
)

actual = pd.DatetimeIndex(
    [
        "2025-01-01 00:00",
        "2025-01-01 01:00",
        "2025-01-01 03:00",
    ]
)

missing = expected.difference(
    actual
)

assert missing.tolist() == [
    pd.Timestamp(
        "2025-01-01 02:00"
    )
]
```

---

# 133. Testing Periods

Test calendar month:

```python
period = pd.Period(
    "2025-01",
    freq="M",
)

assert str(period) == "2025-01"
```

Test fiscal quarter:

```python
fiscal = pd.Period(
    "2025Q1",
    freq="Q-MAR",
)
```

Assert the intended boundaries for your chosen fiscal convention.

---

# 134. Testing Late Events

Create a baseline rolling calculation:

```text
Jan 1
Jan 3
Jan 5
```

Then insert a late Jan 2 event.

Recalculate.

Assert that affected rolling outputs changed.

The test proves:

```text
event-time windows depend on historical data completeness
```

---

# 135. pandas Testing Utilities

Use:

```python
from pandas.testing import (
    assert_frame_equal,
    assert_series_equal,
)
```

These are preferable to ad hoc string comparison for structured pandas results.

Example:

```python
assert_series_equal(
    actual,
    expected,
)
```

For DataFrames:

```python
assert_frame_equal(
    actual,
    expected,
)
```

---

# 136. Edge Cases

Time-series code should explicitly handle unusual conditions.

## Empty DataFrame

```text
0 timestamps
```

Decide:

```text
empty result
schema-only result
```

and test it.

## One timestamp

A one-point series has:

```text
no previous observation
```

so:

```text
shift
diff
pct_change
```

naturally begin with missing values.

## Duplicate timestamps

Ask:

```text
Are duplicates legitimate multiple events?
Or is a unique timestamp expected?
```

Do not deduplicate automatically.

## Unsorted timestamps

Sort before order-dependent calculations.

## Timezone-naive data

Require explicit source interpretation.

## Timezone-aware data

Preserve/convert intentionally.

---

# 137. DST Edge Cases

Test both:

```text
spring-forward
fall-back
```

and verify:

```text
nonexistent local hour
ambiguous local hour
```

Do not test only ordinary days.

---

# 138. Missing Days and Hours

Include:

```text
missing whole day
missing one hour
multiple missing hours
```

For each, ask:

```text
Is this expected no activity?
Is the source incomplete?
Is the system down?
```

---

# 139. Irregular Intervals

Create:

```text
00:00
00:30
03:00
04:15
```

This is useful for proving that:

```python
rolling(7)
```

and:

```python
rolling("7D")
```

have different meanings.

---

# 140. Rolling with Insufficient Observations

Test:

```python
series.rolling(
    "7D",
    min_periods=5,
).mean()
```

when only three observations exist.

Expected:

```text
NaN
```

for positions without sufficient data.

---

# 141. One-Row Group

A group with one observation has:

```text
shift → NaN
diff → NaN
```

and may have:

```text
rolling
```

values depending on `min_periods`.

Test explicitly.

---

# 142. No Events in a Period

A complete calendar can expose:

```text
no event row
```

But the correct label is a business decision.

Do not automatically turn it into:

```text
zero
```

---

# 143. Constant Values

For:

```text
100
100
100
100
```

rolling standard deviation may become:

```text
0
```

where sufficient observations exist.

This is a useful baseline test.

---

# 144. All-Null Values

A rolling aggregation over all missing measurements can remain missing.

Test:

```text
input validity
+
min_periods
```

rather than assuming the operation produces zeros.

---

# 145. Month-End Boundaries

Test:

```text
February
March
April
```

because month lengths differ.

Do not assume:

```text
every month = 30 days
```

---

# 146. Fiscal Quarter Boundary

Test dates immediately before/after the fiscal quarter boundary.

Example:

```text
March 31
April 1
```

under:

```text
Q-MAR
```

This confirms the fiscal calendar.

---

# 147. Business-Day Boundary

Test:

```text
Friday
weekend
Monday
holiday
```

under the chosen business calendar.

---

# 148. Empty Resample Result

An empty time series should not cause the reporting layer to invent data.

Test:

```text
empty input
→ expected schema
```

explicitly.

---

# 149. Missing Calendar Periods

The absence of a timestamp is not evidence of zero activity by itself.

Test your pipeline's missingness policy.

---

# 150. Performance Engineering

Time-series performance depends on:

```text
rows
frequency
number of groups
window size
sorting
timezone conversions
calendar construction
columns
memory
```

Do not state:

```text
method X is always fastest
```

Instead:

> Time-series performance must be measured on the actual data volume, frequency, number of groups, and window sizes.

---

# 151. Sorting Cost

Sorting:

```python
df.sort_values(
    "timestamp"
)
```

can be expensive for large datasets.

But skipping required sorting is worse if it changes semantics.

### Production approach

```text
measure sorting cost
+
ensure time-dependent correctness
```

If source data is already guaranteed sorted, preserve that contract rather than sorting blindly.

---

# 152. Resampling Cost

Resampling cost depends on:

```text
input row count
frequency
number of bins
number of groups
aggregation
```

A minute-level dataset converted to:

```text
hour
day
month
```

creates different output sizes.

Estimate:

```text
input rows
→ output bins
```

before large transformations.

---

# 153. Grouped Resampling Cost

Grouped resampling introduces another multiplicative dimension:

```text
number of groups
×
time range
×
frequency
```

A request for:

```text
50,000 devices
×
hourly buckets
×
365 days
```

can create a very large expected calendar if every device is materialized for every hour.

Do shape budgeting first.

---

# 154. Rolling Window Cost

Rolling operations revisit overlapping observations.

Costs depend on:

```text
number of rows
window type
window size
number of groups
aggregation
```

A grouped rolling calculation can be substantially larger than one global rolling series.

Benchmark realistic workloads.

---

# 155. Repeated Timezone Conversions

Repeated conversions:

```text
UTC → local
UTC → local
UTC → local
```

can become unnecessary work.

A useful pattern is:

```text
keep canonical UTC
convert once at the reporting boundary
```

This is not a guarantee that timezone conversion will dominate runtime.

Measure the actual workload.

---

# 156. Repeated Calendar Construction

Do not repeatedly construct the exact same expected calendar inside large loops.

Prefer:

```text
construct once where practical
reuse when semantics are identical
```

but do not trade away correctness when each group has different bounds/timezones.

---

# 157. Large Time-Series Indexes

An index containing:

```text
millions of timestamps
```

has memory cost.

Inspect:

```python
print(
    df.memory_usage(
        deep=True
    )
)
```

and:

```python
print(
    df.shape
)
```

The appropriate representation depends on the workload.

---

# 158. Wide vs Narrow Time-Series DataFrames

A time-series table with:

```text
timestamp
country
revenue
```

is narrow.

A table with:

```text
timestamp
temperature
pressure
humidity
battery
cpu
memory
latency
...
```

is wider.

Wide tables can simplify certain analytics.

Narrow tables can make schema evolution easier.

Neither is universally faster.

---

# 159. Reducing Columns Before Expensive Time Operations

If only one measure is needed:

```python
daily = (
    df.set_index("timestamp")[
        ["revenue"]
    ]
    .resample("D")
    .sum()
)
```

rather than carrying unrelated large columns through the operation.

This can reduce:

```text
memory
data movement
intermediate size
```

when appropriate.

---

# 160. Benchmarking Time-Series Operations

Use:

```python
from time import perf_counter

start = perf_counter()

result = (
    df.set_index("timestamp")
    .resample("h")
    .sum()
)

elapsed = (
    perf_counter() - start
)

print(
    f"{elapsed:.3f} seconds"
)
```

Record:

```text
input rows
input frequency
output frequency
number of groups
columns
window
runtime
memory
pandas version
Python version
```

Do not fabricate benchmark numbers.

---

# 161. Frequency and Data Volume Thinking

For:

```text
90 days
×
24 hours/day
×
60 minutes/hour
```

you get:

```text
129,600 minute timestamps
```

for one continuous series.

```text
90 × 24 × 60 = 129,600
```

If you have:

```text
100 countries
```

a fully populated minute calendar would be:

```text
12,960,000 country-minute combinations
```

This is why grouped calendar construction needs a shape budget.

---

# 162. Shape Budget for Time Series

Before generating a complete calendar, estimate:

```text
groups
×
periods
```

Example:

```text
50,000 devices
×
8,760 hourly periods/year
```

equals:

```text
438,000,000 device-hour combinations
```

That is a major intermediate dataset.

The calendar may be logically useful but operationally expensive.

---

# 163. Timezone Performance Considerations

A practical pattern:

```text
ingest/normalize
→ UTC

compute
→ UTC

report
→ local conversion
```

This reduces repeated local-time transformations.

But:

> Do not claim timezone conversion is always the dominant bottleneck.

Measure it.

---

# 164. Production Time-Series Patterns

## Website analytics

```text
minute events
→ hourly counts
→ daily metrics
→ rolling trends
```

Key questions:

```text
What timezone?
What event time?
What does missing mean?
```

---

# 165. IoT

```text
sensor readings
→ hourly summaries
→ missing-period detection
→ rolling operating metrics
```

Important:

```text
sensor state vs measurement
```

may determine whether forward filling is valid.

---

# 166. Banking

Illustrative example:

```text
transactions
→ daily/monthly reporting
→ fiscal period analysis
```

Critical dimensions:

```text
transaction time
business timezone
calendar
fiscal period
late corrections
```

This is an illustrative scenario, not a universal banking architecture.

---

# 167. API Monitoring

```text
requests
→ minute latency metrics
→ hourly aggregates
→ rolling SLO indicators
```

The window definition must be explicit:

```text
last 5 minutes
last 7 calendar days
last 1,000 requests
```

Those are different questions.

---

# 168. Operational Logs

```text
events
→ hourly counts
→ gap detection
→ incident analysis
```

A missing hour can indicate:

```text
zero activity
ingestion failure
clock problem
system outage
```

Do not assume which one without evidence.

---

# 169. SQL / Data-Warehouse Connection

Time-series pandas operations often correspond conceptually to:

```text
DATE_TRUNC / date bucketing
window functions
LAG / LEAD
running aggregates
calendar tables
```

Conceptual mapping:

| Time-series idea | pandas pattern |
|---|---|
| previous row | `shift()` |
| absolute change | `diff()` |
| relative change | `pct_change()` |
| time bucket + aggregate | `resample()` |
| moving aggregate | `rolling()` |
| cumulative history | `expanding()` |
| weighted history | `ewm()` |

Exact SQL syntax differs by database.

---

# 170. Resampling Report Design

A production time-series output might contain:

```text
timestamp_bucket
country
event_count
revenue
rolling_7d_revenue
missing_period_flag
```

Define each field.

Example:

| Field | Definition |
|---|---|
| `timestamp_bucket` | UTC daily bucket boundary |
| `country` | country dimension |
| `event_count` | count of observed events |
| `revenue` | sum of revenue values in bucket |
| `rolling_7d_revenue` | seven elapsed-day rolling statistic |
| `missing_period_flag` | whether expected data was absent |

Output schemas should be explicit and stable.

---

# 171. Reconciliation After Resampling

For a pure additive aggregation with no filtering/deduplication:

```python
source_revenue = (
    df["revenue"].sum()
)

resampled_revenue = (
    df.set_index("timestamp")
    .resample("D")["revenue"]
    .sum()
    .sum()
)
```

Then:

```python
assert (
    source_revenue
    == resampled_revenue
)
```

when the numeric representation and missing-value semantics make exact equality appropriate.

### Event-count reconciliation

For a pure grouping:

```text
raw event count
=
sum of valid resampled event counts
```

This check can catch:

```text
unexpected filtering
dropped timestamps
duplicate handling
```

---

# 172. Reconciliation Caveats

Totals can legitimately differ when you introduce:

```text
filtering
deduplication
invalid-row removal
timezone boundary changes
different measure definitions
```

For example, converting an event stream into local calendar days does not necessarily change the total number of events, but the distribution across daily buckets changes.

The validation must match the transformation's semantics.

---

# 173. Hand-Computed Small Examples

Use at least these manually solved examples.

## Example 1 — `shift`

```text
100
120
150
```

Expected:

```text
NaN
100
120
```

## Example 2 — `diff`

Expected:

```text
NaN
20
30
```

## Example 3 — `pct_change`

Expected:

```text
NaN
0.20
0.25
```

## Example 4 — hourly resampling

Two events in hour 10 and two in hour 11.

Expected hourly counts:

```text
10:00 → 2
11:00 → 2
```

## Example 5 — label/closed

Boundary timestamps:

```text
10:00
11:00
```

Draw the bins before executing.

## Example 6 — `rolling(7)`

Seven observations:

```text
1 2 3 4 5 6 7
```

the seventh result has all seven observations under default minimum behavior.

## Example 7 — `rolling("7D")`

Use sparse timestamps and manually list which dates fall inside the time window.

## Example 8 — missing hour

```text
00:00
01:00
03:00
```

Missing:

```text
02:00
```

## Example 9 — timezone conversion

Convert:

```text
2025-01-01 00:00 UTC
```

to:

```text
Asia/Kolkata
America/New_York
```

and compare the local clock/date.

## Example 10 — period conversion

Convert:

```text
2025-03-31
2025-04-01
```

into a fiscal quarter ending in March.

---

# 174. Time-Series Data Quality Checklist

```text
[ ] Timestamp meaning is documented
[ ] Timestamp timezone is known
[ ] Naive/aware state is intentional
[ ] UTC strategy is defined
[ ] Time data is sorted before order-dependent calculations
[ ] Frequency is explicit
[ ] Resampling bins are understood
[ ] label is intentional
[ ] closed is intentional
[ ] Missing periods have defined semantics
[ ] Zero vs missing is distinguished
[ ] Rolling window is row-count or time-based intentionally
[ ] min_periods is justified
[ ] DST behavior is tested where relevant
[ ] Fiscal/calendar definitions are explicit
[ ] Business-day assumptions are documented
[ ] Late-arriving events are considered
[ ] Affected rolling metrics can be recomputed
[ ] Results are validated against hand-computed examples
```

---

# 175. Time-Series Anti-Patterns

## Anti-pattern 1 — Treating every naive timestamp as UTC

Why it seems reasonable:

```text
UTC is convenient.
```

Risk:

```text
wrong instant
wrong date
wrong report
```

Safer:

```text
verify source timezone first
```

## Anti-pattern 2 — `tz_convert()` on naive timestamps

Risk:

```text
operation is conceptually wrong
```

Safer:

```text
localize first
```

## Anti-pattern 3 — `tz_localize()` when conversion was intended

Risk:

```text
same clock time is assigned a new meaning
```

Safer:

```text
convert an aware instant
```

## Anti-pattern 4 — Resampling unsorted data

Risk:

```text
order assumptions become unclear
```

Safer:

```text
sort or prove source order
```

## Anti-pattern 5 — Calling `rolling(7)` a seven-day metric on irregular data

Risk:

```text
seven rows ≠ seven elapsed days
```

Safer:

```text
rolling("7D")
```

when the business meaning is elapsed time.

## Anti-pattern 6 — Filling every missing bucket with zero

Risk:

```text
no observation
→ falsely reported as zero
```

Safer:

```text
define missingness semantics first
```

## Anti-pattern 7 — Ignoring DST

Risk:

```text
local hour counts become wrong
```

Safer:

```text
test transition dates when local time matters
```

## Anti-pattern 8 — Aggregating local time without defining the zone

Risk:

```text
two pipelines use different day boundaries
```

Safer:

```text
name the reporting timezone
```

## Anti-pattern 9 — Treating fiscal periods as calendar periods

Risk:

```text
financial reports are assigned to wrong quarter
```

Safer:

```text
use the explicit fiscal calendar
```

## Anti-pattern 10 — Assuming late events cannot change history

Risk:

```text
historical rolling metrics become stale
```

Safer:

```text
define affected-period recomputation
```

---

# 176. Production Time-Series Decision Tree

```text
Do I need fixed time buckets?
        |
       YES
        ↓
     resample()

Do I need the same frequency without general aggregation?
        |
       YES
        ↓
      asfreq()

Do I need an explicit expected calendar?
        |
       YES
        ↓
      reindex()

Do I need a moving time window?
        |
       YES
        ↓
   rolling("...")

Do I need a fixed number of observations?
        |
       YES
        ↓
     rolling(...)

Do timestamps need timezone interpretation?
        |
       naive
        ↓
    tz_localize()

Are timestamps already aware and need another timezone?
        |
       YES
        ↓
    tz_convert()
```

---

# 177. Time-Series Output Contract

Production outputs should define:

```text
timestamp meaning
timezone
frequency
window definition
missingness semantics
aggregation
calendar convention
fiscal convention
late-event policy
```

Example:

```text
Dataset:
country_daily_metrics

timestamp:
UTC daily bucket boundary

frequency:
daily

revenue:
sum of event revenue

missing period:
reported separately; not automatically zero

rolling metric:
seven elapsed days

report timezone:
America/New_York

fiscal convention:
year ending in March
```

---

# 178. Production Join/Time Boundary Connection

Time-series calculations often interact with later enrichment operations.

The key questions are:

```text
What timezone defines the time?
What timestamp is the business event?
What timestamp is the reference value valid for?
```

Do not jump ahead into detailed as-of joins here.

The important lesson is:

> Timestamp semantics must be correct before a later point-in-time join can be correct.

---

# 179. Reproducibility

Time-series pipelines should be reproducible.

Record or fix:

```text
timezone rules
pandas version
frequency definitions
fiscal calendar
business calendar
input cutoff
late-data cutoff
```

A result computed today may differ from a result computed after late events arrive.

Therefore reproducibility includes:

```text
data completeness
+
time semantics
+
calculation rules
```

---

# 180. Production Backfill Thinking

A batch backfill might need to answer:

```text
Which event-time interval is being recomputed?
Which local calendar applies?
Are rolling windows allowed to look outside the target interval?
```

For a seven-day trailing metric, recomputing only one day may be insufficient if the prior six days are also needed.

This is a key production reasoning skill.

---

# 181. Rolling Window Dependency Example

Suppose:

```text
output date = Jan 10
window = previous 7 elapsed days
```

Then the result depends on observations in a time range around:

```text
Jan 3 → Jan 10
```

If Jan 6 changes, Jan 10 can change.

That is why a late historical event has an **impact radius**.

---

# 182. Frequency vs Duration

Do not confuse:

```text
7 rows
```

with:

```text
7 days
```

or:

```text
7 business days
```

or:

```text
7 calendar periods
```

These are different definitions.

A production metric should use the exact unit required by the business.

---

# 183. Calendar Day vs Elapsed 24 Hours

A calendar day:

```text
midnight → next midnight
```

does not always correspond to:

```text
exactly 24 local-clock hours
```

around DST transitions.

An elapsed duration:

```text
24 hours
```

is a fixed amount of time.

This distinction matters when choosing:

```text
calendar periods
vs
elapsed-time windows
```

---

# 184. Local Time vs UTC Time in Reporting

A daily report can be defined as:

```text
UTC midnight → next UTC midnight
```

or:

```text
America/New_York midnight → next New York midnight
```

The two reports can contain different events.

Therefore:

```text
daily revenue
```

is incomplete as a metric definition unless the reporting timezone is known.

---

# 185. Current pandas 3.x Notes

For this chapter's current pandas 3.x target:

- use current documented frequency aliases such as `h`, `min`, `ME`, and `MS`;
- `resample()` provides time-based grouping and aggregation;
- timezone localization/conversion distinguishes naive interpretation from aware-instant conversion;
- rolling supports fixed-count and offset/time-based windows;
- DST localization policies are explicit through `nonexistent` and `ambiguous`.

These details should be checked against the pandas version pinned by the project. citeturn683881search0turn683881search1turn370811search0turn370811search3

---

# 186. Final Validation Checklist

## Basics

- [ ] `DatetimeIndex`
- [ ] `pd.date_range`
- [ ] sorting by time
- [ ] partial-string selection
- [ ] naive timestamps
- [ ] timezone-aware timestamps
- [ ] `tz_localize`
- [ ] `tz_convert`
- [ ] UTC-first strategy
- [ ] `shift`
- [ ] `diff`
- [ ] `pct_change`

## Resampling

- [ ] `resample`
- [ ] daily `D`
- [ ] hourly `h`
- [ ] minute `min`
- [ ] weekly `W`
- [ ] month-end `ME`
- [ ] month-start `MS`
- [ ] newer/current lowercase frequency aliases
- [ ] time bins
- [ ] `label`
- [ ] `closed`
- [ ] `asfreq`
- [ ] upsampling
- [ ] `ffill`

## Rolling

- [ ] rolling windows
- [ ] `rolling(7)`
- [ ] `rolling("7D")`
- [ ] `min_periods`
- [ ] `center`
- [ ] expanding
- [ ] ewm

## Grouped time series

- [ ] groupby + resample
- [ ] groupby + rolling

## Advanced

- [ ] gap detection
- [ ] complete calendar
- [ ] `reindex`
- [ ] missing period vs no events
- [ ] DST
- [ ] non-existent local times
- [ ] ambiguous local times
- [ ] `nonexistent=`
- [ ] `ambiguous=`
- [ ] UTC storage and local reporting
- [ ] periods
- [ ] `to_period`
- [ ] fiscal months
- [ ] fiscal quarters
- [ ] business days
- [ ] custom calendars
- [ ] late-arriving events
- [ ] out-of-order events
- [ ] rolling recomputation
- [ ] affected-period recalculation
- [ ] performance considerations

## Required learning activities

- [ ] bin-drawing exercise
- [ ] `rolling(7)` vs `rolling("7D")` exercise
- [ ] output-shape prediction
- [ ] hand-computed examples
- [ ] `timeseries_metrics.py` fully specified
- [ ] 90 days of per-minute UTC events
- [ ] hourly event counts
- [ ] daily event counts
- [ ] 7-day rolling average per country
- [ ] missing-hour detection per country
- [ ] `America/New_York` conversion
- [ ] `Asia/Kolkata` conversion
- [ ] DST transition demonstration
- [ ] month-end revenue
- [ ] fiscal quarters with periods
- [ ] small-frame validation

## Quality

- [ ] debugging
- [ ] testing
- [ ] edge cases
- [ ] performance
- [ ] reconciliation
- [ ] production patterns
- [ ] anti-patterns
- [ ] checklist
- [ ] checkpoint
- [ ] common mistakes
- [ ] cheat sheet

---

# 187. Checkpoint

The roadmap checkpoint is the minimum completion standard.

## 1. Explain `tz_localize` vs `tz_convert`

You should be able to say:

```text
tz_localize
→ attach timezone meaning to naive timestamps

tz_convert
→ represent an already-aware instant in another timezone
```

---

## 2. Explain `rolling(7)` vs `rolling("7D")`

You should be able to say:

```text
rolling(7)
→ seven observations

rolling("7D")
→ a seven-day elapsed-time window
```

and explain why they diverge on irregular data.

---

## 3. Control bin edges with `label` and `closed`

You should be able to say:

```text
label
→ names the resulting time bin

closed
→ selects which boundary is included
```

---

## 4. Detect missing periods

You should be able to:

```text
build an expected calendar
compare expected vs observed timestamps
report missing periods
classify their meaning
```

---

# 188. Advanced Self-Check Questions

Answer these without looking at the chapter.

1. What does a timezone-naive timestamp fail to tell you?
2. Why can the same UTC instant belong to different local calendar dates?
3. What does `pd.date_range()` provide in gap detection?
4. Why must order-dependent calculations be sorted?
5. What does `shift()` return for the first row?
6. Why can `pct_change()` be undefined when the previous value is zero?
7. Why is `resample()` more than string formatting?
8. What do `label` and `closed` control independently?
9. When would `asfreq()` be more appropriate than `resample()`?
10. When is `ffill` semantically valid after upsampling?
11. Why can `rolling(7)` be misleading on irregular data?
12. What does `min_periods` protect against?
13. Why can centered rolling windows be unsuitable for real-time metrics?
14. How does grouped rolling avoid cross-entity leakage?
15. How do you distinguish no events from missing data?
16. Why does DST produce non-existent and ambiguous local times?
17. What does `nonexistent="NaT"` do conceptually?
18. What does `ambiguous="NaT"` do conceptually?
19. Why are fiscal quarters different from calendar quarters?
20. Why can a late event force rolling recomputation?
21. What is an affected-period boundary?
22. Why is a complete device-hour calendar potentially enormous?
23. Why might UTC-first storage improve reproducibility?
24. Why should daily metrics name their reporting timezone?
25. What should be benchmarked for a time-series pipeline?

---

# 189. Cheat Sheet

## DatetimeIndex

```python
pd.to_datetime(...)
```

```python
pd.date_range(...)
```

```python
df.sort_index()
```

```python
df.sort_values("timestamp")
```

---

## Partial-string selection

```python
df.loc["2025-03"]
```

```python
df.loc[
    "2025-03-10":"2025-03-20"
]
```

---

## Timezones

```python
ts.tz_localize("UTC")
```

```python
ts.tz_convert(
    "America/New_York"
)
```

Mental rule:

```text
tz_localize = attach timezone meaning
tz_convert  = change timezone representation
```

---

## Change calculations

```python
shift(...)
```

```python
diff(...)
```

```python
pct_change(...)
```

Mental rule:

```text
shift
→ previous value

diff
→ absolute change

pct_change
→ relative/fractional change
```

---

## Resampling

```python
df.resample("D").sum()
```

```python
df.resample("h").sum()
```

```python
df.resample("min").sum()
```

```python
df.resample("W").sum()
```

```python
df.resample("ME").sum()
```

```python
df.resample("MS").sum()
```

---

## Bin control

```python
label="left"
```

```python
label="right"
```

```python
closed="left"
```

```python
closed="right"
```

Mental rule:

```text
label  = output bin label
closed = included boundary
```

---

## Frequency alignment

```python
df.asfreq(...)
```

```python
df.reindex(...)
```

Mental rule:

```text
resample = bucket + aggregation
asfreq   = frequency alignment
reindex  = explicit calendar alignment
```

---

## Upsampling

```python
df.resample(
    "h"
).asfreq()
```

```python
df.resample(
    "h"
).ffill()
```

Use `ffill` only when carrying the previous state is semantically valid.

---

## Rolling

```python
df["mean_7"] = (
    df["value"]
    .rolling(7)
    .mean()
)
```

```python
df["mean_7d"] = (
    df["value"]
    .rolling("7D")
    .mean()
)
```

```python
df["mean_7d"] = (
    df["value"]
    .rolling(
        "7D",
        min_periods=3,
    )
    .mean()
)
```

```python
df["centered"] = (
    df["value"]
    .rolling(
        7,
        center=True,
    )
    .mean()
)
```

---

## Expanding

```python
df["expanding_mean"] = (
    df["value"]
    .expanding()
    .mean()
)
```

---

## Exponential weighting

```python
df["ewm_mean"] = (
    df["value"]
    .ewm(span=7)
    .mean()
)
```

---

## Grouped time series

```python
df.groupby(
    "country"
).resample(
    "D",
    on="timestamp",
)["revenue"].sum()
```

```python
df.groupby(
    "country"
).rolling(
    "7D",
    on="timestamp",
)["revenue"].mean()
```

---

## Gap detection

```python
expected = pd.date_range(
    start="2025-01-01",
    end="2025-01-03",
    freq="h",
    tz="UTC",
)
```

```python
missing = expected.difference(
    actual_index
)
```

---

## Periods

```python
df["month"] = (
    df["timestamp"]
    .dt.to_period("M")
)
```

```python
df["fiscal_quarter"] = (
    df["timestamp"]
    .dt.to_period("Q-MAR")
)
```

---

# 190. SQL / Data Engineering Quick Reference

| SQL/data-warehouse idea | pandas pattern |
|---|---|
| Date bucketing | `resample()` |
| `LAG`-like previous value | `shift()` |
| Difference from previous row | `diff()` |
| Relative change | `pct_change()` |
| Windowed aggregate | `rolling()` |
| Running aggregate | `expanding()` / cumulative methods |
| Calendar alignment | `reindex()` |
| Frequency alignment | `asfreq()` |
| Period representation | `Period` / `to_period()` |

Exact database syntax varies.

---

# 191. Production Time-Series Decision Tree

```text
Need fixed calendar/time buckets?
        |
       YES
        ↓
    resample()

Need frequency alignment without grouped aggregation?
        |
       YES
        ↓
     asfreq()

Need an explicit expected calendar?
        |
       YES
        ↓
    reindex()

Need moving elapsed-time metric?
        |
       YES
        ↓
  rolling("7D")

Need moving observation-count metric?
        |
       YES
        ↓
   rolling(7)

Need timezone meaning for naive timestamps?
        |
       YES
        ↓
  tz_localize()

Need another display timezone for aware timestamps?
        |
       YES
        ↓
   tz_convert()
```

---

# 192. Final Production Mental Model

```text
                     TIME SERIES
                          |
          +---------------+---------------+
          |                               |
      TIMESTAMP                        CALENDAR
          |                               |
      timezone                        frequency
          |                               |
      UTC/local                         bins
          |                               |
      ordering                       aggregation
          |                               |
      previous/change                    windows
          |                               |
      shift/diff/pct                    rolling
                                          |
                                   missing periods
                                          |
                                         DST
                                          |
                                   fiscal calendars
                                          |
                                   late-arriving data
                                          |
                                    recomputation
```

The engineering sequence is:

```text
DEFINE TIMESTAMP MEANING
        ↓
DEFINE TIMEZONE
        ↓
NORMALIZE / CONVERT
        ↓
SORT
        ↓
DEFINE FREQUENCY
        ↓
DEFINE CALENDAR
        ↓
PREDICT SHAPE
        ↓
RESAMPLE / ALIGN
        ↓
DEFINE WINDOW
        ↓
CALCULATE
        ↓
CHECK MISSINGNESS
        ↓
RECONCILE TOTALS
        ↓
TEST EDGE CASES
        ↓
BENCHMARK
        ↓
PUBLISH EXPLICIT OUTPUT CONTRACT
```

---

# 193. Final Exit Criteria

Do not consider Topic 09 complete because you can remember:

```python
df.resample("D").sum()
```

Consider it complete when you can take an unfamiliar time-series dataset and explain:

```text
What does this timestamp mean?

Which timezone does it represent?

Is it naive or aware?

Should it be normalized to UTC?

Is the series correctly ordered?

What calendar is relevant?

What is the desired frequency?

Which observations belong to each resampling bin?

Which side of the bin is closed?

What timestamp labels the bin?

Is this an aggregation or an alignment problem?

Does the dataset require upsampling?

Is forward filling semantically valid?

Is the rolling window row-count-based or time-based?

How many observations are required?

Should the window be centered?

Are the time series independent by group?

How are missing periods detected?

Does missing mean zero, no event, or missing data?

Are DST transitions relevant?

Is the business calendar calendar-based or fiscal?

What business-day definition applies?

Can late events alter historical rolling metrics?

Which periods need recomputation?

How will I validate the output?

How will I reconcile totals?

How will I benchmark the workload?
```

That is the production-level time-series skill this topic is designed to build.

---

# 194. Official pandas References

The examples target current pandas 3.x APIs. Verify the exact pinned project version when reproducing examples.

- Time series/date functionality:  
  https://pandas.pydata.org/docs/user_guide/timeseries.html

- `DataFrame.resample`:  
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html

- `Series.rolling`:  
  https://pandas.pydata.org/docs/reference/api/pandas.Series.rolling.html

- `Series.dt.tz_localize`:  
  https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.tz_localize.html

- `DataFrame.tz_localize`:  
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.tz_localize.html

- General DataFrame time-series methods:  
  https://pandas.pydata.org/docs/reference/frame.html

Current pandas documentation covers resampling, timezone handling, rolling windows, business-day offsets, and fiscal/anchored periods. citeturn683881search0turn683881search1turn370811search0turn586412search0

---

# 195. Final Master Checklist

## Fundamentals

- [ ] `DatetimeIndex`
- [ ] `pd.date_range`
- [ ] sorting
- [ ] partial-string selection
- [ ] naive timestamps
- [ ] timezone-aware timestamps
- [ ] `tz_localize`
- [ ] `tz_convert`
- [ ] UTC-first strategy
- [ ] `shift`
- [ ] `diff`
- [ ] `pct_change`

## Resampling

- [ ] resampling concept
- [ ] `resample`
- [ ] `D`
- [ ] `h`
- [ ] `min`
- [ ] `W`
- [ ] `ME`
- [ ] `MS`
- [ ] current/lowercase aliases
- [ ] bins
- [ ] `label`
- [ ] `closed`
- [ ] `asfreq`
- [ ] upsampling
- [ ] `ffill`

## Rolling

- [ ] rolling windows
- [ ] `rolling(7)`
- [ ] `rolling("7D")`
- [ ] `min_periods`
- [ ] `center`
- [ ] expanding
- [ ] ewm

## Grouped time series

- [ ] grouped resampling
- [ ] grouped rolling
- [ ] cross-group leakage prevention

## Advanced

- [ ] gap detection
- [ ] complete calendars
- [ ] `reindex`
- [ ] no-events vs missing
- [ ] DST
- [ ] non-existent local times
- [ ] ambiguous local times
- [ ] `nonexistent=`
- [ ] `ambiguous=`
- [ ] UTC storage/local reporting
- [ ] periods
- [ ] `to_period`
- [ ] fiscal months
- [ ] fiscal quarters
- [ ] business days
- [ ] custom calendars
- [ ] late events
- [ ] out-of-order events
- [ ] rolling recomputation
- [ ] recalculation boundaries
- [ ] performance

## Exercises

- [ ] `timeseries_metrics.py` fully specified
- [ ] 90-day per-minute UTC dataset
- [ ] hourly counts
- [ ] daily counts
- [ ] per-country seven-day rolling metric
- [ ] missing hours per country
- [ ] New York conversion
- [ ] Kolkata conversion
- [ ] DST demonstration
- [ ] month-end revenue
- [ ] fiscal quarters
- [ ] hand-computed validation
- [ ] bin-drawing exercise
- [ ] irregular rolling comparison

## Quality

- [ ] debugging
- [ ] testing
- [ ] edge cases
- [ ] performance
- [ ] reconciliation
- [ ] production scenarios
- [ ] anti-patterns
- [ ] output contract
- [ ] checkpoint
- [ ] common mistakes
- [ ] cheat sheet

---

# 196. Common Mistakes Summary

| Mistake | Why it happens | Correct approach |
|---|---|---|
| Naive timestamps treated as UTC | UTC feels like a safe default | Verify source semantics, then localize/convert explicitly |
| Resampling unsorted data | Time order is assumed to be obvious | Sort/prove chronological ordering before order-dependent calculations |
| Count-based windows on irregular data | `rolling(7)` sounds like seven days | Use `rolling("7D")` when the business definition is elapsed time |
| Daily aggregates computed in local time without specifying the zone | "Day" seems unambiguous | Define the reporting timezone explicitly |
| Confusing `tz_localize` and `tz_convert` | Both mention timezones | Naive → localize; aware → convert |
| Using the wrong frequency | Frequency strings look like formatting options | Define and test the required frequency |
| Misunderstanding `label` | Label sounds like interval membership | `label` names the bin; `closed` controls inclusion |
| Confusing `asfreq` and `resample` | Both change apparent frequency | Use `asfreq` for alignment; `resample` for time-bucket aggregation |
| Forward-filling event measures | `ffill` is convenient | Use only when the value is a legitimately persistent state |
| Treating missing periods as zeros | Reports look cleaner | Define whether absence means zero, missing, or unknown |
| Ignoring DST | Most dates behave normally | Test non-existent and ambiguous local times where relevant |
| Treating fiscal quarters as calendar quarters | Calendar quarters are familiar | Use the organization's explicit fiscal calendar |
| Assuming Monday–Friday is every business calendar | Standard weekdays are convenient | Use the documented business/custom calendar |
| Assuming historical metrics never change | Batch jobs appear final | Recompute affected periods after late events |
| Rolling before sorting | The code still executes | Sort by event time first |
| Rolling across entities | One global series is easier | Group before rolling |
| Building huge complete calendars blindly | Calendar completeness is useful | Estimate `groups × periods` before materializing |
| Repeated timezone conversions | Each report does its own conversion | Keep canonical UTC and convert intentionally at reporting boundaries |

The four primary roadmap mistakes are explicitly included here. fileciteturn20file0

---

# 197. Final One-Page Memory Anchor

```text
TIMESTAMP
= what happened when?

TIMEZONE
= which instant does the clock reading represent?

UTC
= a strong canonical storage/computation reference

tz_localize
= attach timezone meaning

tz_convert
= convert an aware instant to another timezone

SHIFT
= previous value

DIFF
= current - previous

PCT_CHANGE
= relative/fractional change

RESAMPLE
= time buckets + aggregation

ASfreq
= frequency alignment

REINDEX
= explicit calendar alignment

LABEL
= output bin name

CLOSED
= boundary inclusion

ROLLING(7)
= seven observations

ROLLING("7D")
= seven elapsed days

MIN_PERIODS
= minimum observations required

CENTER
= align around the center of the window

EXPANDING
= growing historical window

EWM
= weighted history

GROUPBY + RESAMPLE
= independent time buckets per entity

GROUPBY + ROLLING
= independent moving windows per entity

GAP DETECTION
= expected calendar - observed timestamps

MISSING
≠
ZERO

DST
= local time may skip or repeat wall-clock hours

PERIOD
= calendar/reporting span

FISCAL PERIOD
= business-defined calendar

LATE EVENT
= historical event arriving later

ROLLING RECOMPUTATION
= recalculate every affected output window
```

The core production loop:

```text
Timestamp
→ Timezone
→ Ordering
→ Frequency
→ Bins
→ Aggregation
→ Window
→ Missingness
→ Calendar
→ Reconciliation
→ Performance
```
