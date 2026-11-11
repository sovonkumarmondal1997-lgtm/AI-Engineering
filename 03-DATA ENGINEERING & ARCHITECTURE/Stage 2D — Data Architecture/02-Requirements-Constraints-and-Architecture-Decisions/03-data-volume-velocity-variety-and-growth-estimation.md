# 03 — Data Volume, Velocity, Variety and Growth Estimation

> **Scenario and number policy:** Northbridge Bank is fictional. Every Northbridge system detail and every numeric input in a worked example, exercise answer, or worksheet is an **illustrative assumption**, not a real requirement, measured fact, vendor guarantee, or universal recommendation. Replace assumptions with evidence before making a production commitment. This lesson uses decimal units by default: **1 kB = 10³ bytes, 1 MB = 10⁶ bytes, 1 GB = 10⁹ bytes, 1 TB = 10¹² bytes, and 1 PB = 10¹⁵ bytes**. Binary units are explicitly labelled KiB, MiB, GiB, TiB, and PiB.

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Estimate current and future data volumes with formulas, explicit units, assumptions, and evidence labels.
2. Characterise arrival rates, peak rates, bursts, and seasonality rather than sizing from daily averages alone.
3. Distinguish raw, processed, replicated, retained, and archived data without double-counting copies or layers.
4. Classify structured, semi-structured, and unstructured data and explain how format and schema affect size and processing.
5. Calculate daily, monthly, annual, and multi-year volumes, including compound growth and retention windows.
6. Estimate average and peak event rates, and characterise batch and streaming workloads.
7. Express material estimates as low, expected, and high cases; identify sensitive inputs and explain what could change an architecture decision.
8. Distinguish data at rest, data in motion, and data in processing; understand why storage volume alone does not size compute or networks.
9. Label inputs as measured, sampled, vendor-stated, estimated, or guessed; sanity-check results against independent evidence.
10. Translate estimates into architecture implications—such as partitioning, storage tiering, ingestion capacity, compression testing, and validation priorities—without prematurely selecting a product.

**Definition of done:** another reviewer can reproduce the calculations, understand their assumptions and confidence, and see what the results imply for the architecture.

## 2. Why the topic matters in real-world Data Architecture

Capacity estimation connects business requirements to physical and operational consequences. A platform that stores a few gigabytes per day has different storage, network, recovery, and processing needs from one that stores several terabytes per day. A workload with modest daily volume can still be difficult if most events arrive in a short burst, each event is large, ordering is required, or a backlog must be replayed after an outage.

A data architect does not need false precision. The goal is a **defensible order-of-magnitude estimate and a range**, with the evidence and assumptions visible. Estimates influence:

- **Storage:** primary capacity, retained history, archive tiers, replicas, indexes, metadata, and safety headroom.
- **Ingestion:** average and peak records per second, bytes per second, file sizes, batch windows, and backlog recovery.
- **Processing:** parsing, validation, joins, sorting, shuffles, intermediate results, and memory pressure.
- **Networking:** transfer volume, throughput, burst duration, and replication traffic.
- **Cost:** storage class, compute hours, data transfer, query scans, replication, and retention.
- **Operational design:** partitioning, compaction, backfills, recovery, monitoring, and capacity alarms.

Northbridge Bank illustrates the issue. In the fictional scenario, core banking, cards, CRM, and loan origination data are copied into separate analytical environments. Risk, finance, marketing, and compliance report different customer counts; fraud analysts receive card transactions hours after the event. Capacity estimates help the team reason about a consolidated customer-and-transaction view. They do **not** establish the correct customer definition or solve data ownership; those require the earlier stakeholder and requirements work.

A number without a unit is incomplete. A number without an evidence label can be misleading. A daily average without a peak profile can produce an under-sized ingestion path. A raw-data estimate without retention and copy policy can understate storage by multiples. Conversely, blindly multiplying every layer by every copy can overstate capacity by counting the same bytes twice. This lesson teaches a repeatable method to avoid both errors.

## 3. Prerequisite concepts

### 3.1 Required prior learning

- **Topics 1–2 in this module:** stakeholder discovery and functional/non-functional requirements. These identify the workload, scope, consumers, and what “enough capacity” means.
- **Stage 2–2C data engineering experience:** a working understanding of batch jobs, streaming events, storage, transformations, and serving paths.
- **Basic arithmetic and unit handling:** multiplication, percentages, powers of ten and two, rates, and unit conversion.
- **Structured writing:** ability to document assumptions, formulas, results, and limitations in a worksheet.

### 3.2 Helpful prior knowledge

SQL and common data formats such as CSV, JSON, Parquet, and Avro help when estimating record size. Familiarity with compression, partitioning, indexes, percentiles, and simple statistics is useful but is not a prerequisite for the first calculations.

### 3.3 Essential vocabulary

| Term | Meaning | Example or caution |
|---|---|---|
| Record | A logical row or item in a dataset | A customer profile row; physical storage may add overhead. |
| Event | A fact that something happened at a point in time | A card authorisation event; it may be larger than a compact table row. |
| Average record size | Mean bytes per logical record under a defined representation | Must state whether it is JSON bytes, CSV bytes, or stored bytes. |
| Logical volume | Size of the chosen data representation before physical copies and storage-engine overhead | A logical 1 GB/day feed is not necessarily 1 GB/day of physical storage. |
| Physical storage consumption | Actual occupied bytes after compression, metadata, indexes, replicas, and other relevant effects | Measure or estimate each factor separately. |
| Retention window | Duration for which data must remain available in a particular tier or system | A seven-year retention rule does not automatically mean seven years in the most expensive tier. |
| Replication/copy factor | Number of stored copies of a defined dataset or layer | Count only copies actually required by the design. |
| Compression ratio | Uncompressed bytes divided by compressed bytes | A ratio of 3:1 means compressed size is one-third of original size; results vary by data and codec. |
| Arrival rate | Number of events arriving per unit time | Events/s; must specify average or peak and the time window. |
| Growth rate | Rate at which volume or event count changes over time | Compound growth differs from adding a fixed amount each year. |

## 4. Beginner-level learning sequence

### 4.1 Bits, bytes, and unit systems

A **bit** is a binary digit, either 0 or 1. A **byte** is eight bits. Storage file sizes are commonly expressed in bytes; network rates are often expressed in bits per second. Confusing these units creates an eightfold error before any other assumptions are considered.

| Decimal unit | Bytes | Binary unit | Bytes (exact) |
|---|---:|---|---:|
| kB | 1,000 | KiB | 1,024 |
| MB | 1,000,000 | MiB | 1,048,576 |
| GB | 1,000,000,000 | GiB | 1,073,741,824 |
| TB | 1,000,000,000,000 | TiB | 1,099,511,627,776 |
| PB | 1,000,000,000,000,000 | PiB | 1,125,899,906,842,624 |

Use one convention throughout a worksheet. The roadmap uses decimal multiples unless explicitly stated otherwise. Do not label a value “GB” if the calculation actually uses GiB. For a network conversion, bytes/s × 8 = bits/s. For example, an illustrative transfer rate of 10 MB/s equals 80 Mb/s (decimal units), before protocol overhead.

### 4.2 The three Vs

- **Volume:** how much data is produced, moved, stored, or retained.
- **Velocity:** how quickly data arrives and must be processed. Describe both the average and the peak/burst profile.
- **Variety:** the forms and structures of data, from regular tables to nested events, documents, images, and audio.

These are complementary, not interchangeable. A high-volume nightly file is not automatically a high-velocity streaming workload. A low-volume set of nested documents may still impose substantial parsing and schema-management work.

### 4.3 Data forms and size implications

| Form | Description | Examples | Estimation considerations |
|---|---|---|---|
| Structured | Fixed or strongly defined fields and types | Relational table, CSV with a known schema | Field widths, null representation, delimiters, encoding, keys, row overhead. |
| Semi-structured | Has structure but fields may be nested or optional | JSON, XML, application logs, Avro events | Field names, nesting, repeated keys, optional fields, schema evolution, serialization. |
| Unstructured | Content is not naturally represented as a simple row/field schema | PDF documents, images, audio recordings | File-size distribution, metadata, thumbnails/derivatives, indexing, content retention. |

The same business record can occupy different sizes in a database row, CSV file, JSON event, and compressed columnar file. A CSV row repeats delimiters and textual values; JSON repeats field names; a database may store indexes and page overhead; a columnar format can compress repeated values and store metadata. Measure the representation that matches the workload instead of assuming the logical fields determine physical bytes exactly.

### 4.4 Basic daily volume formula

```text
daily_volume_bytes = records_per_day × average_record_size_bytes
```

The record count and record size must refer to the same source and scope. The formula gives a logical byte volume in the chosen representation. It does not yet include copies, indexes, metadata, compression, or retained history.

**Worked example (illustrative inputs):**

- Input: 2,000,000 transactions/day (**illustrative estimate**).
- Average record size: 500 bytes/transaction (**illustrative estimate**; assume a defined serialized representation).
- Formula: `daily_volume = records/day × bytes/record`.
- Substitution: `2,000,000 records/day × 500 bytes/record = 1,000,000,000 bytes/day`.
- Conversion: `1,000,000,000 bytes/day ÷ 10^9 bytes/GB = 1.0 GB/day`.
- Result: **1.0 GB/day logical volume** in the assumed representation.
- Architecture interpretation: this is the daily source volume before processing layers, copies, physical overhead, and retention. It is not a complete storage budget.
- Uncertainty: the result changes linearly with transaction count and average record size. Validate both using source counts and a representative sample.

### 4.5 Beginner exercise: explain the representation

**Question:** Why might the same logical transaction occupy different sizes in a database, CSV, JSON, and compressed columnar file?

**Answer guidance:** The schema and values may be the same, but representations encode fields differently. CSV uses delimiters and textual values; JSON repeats keys and syntax; a database adds page, index, and engine structures; compressed columnar files exploit repeated values and column-specific encodings but have file and row-group metadata. No single representation is universally smallest for every workload. State whether your estimate is logical serialized volume or physical stored volume.

### 4.6 Beginner check: classify the inputs

For each input, label its evidence quality and unit before calculating:

| Input | Example label | Why it matters |
|---|---|---|
| Events/day from a production counter | Measured, if counter scope is validated | Stronger evidence, but still verify exclusions and duplicate counting. |
| Average event bytes from a representative sample | Sampled | Valid only if the sample reflects the workload and serialization. |
| Future growth percentage from a planning meeting | Estimated or guessed | Must be tested as a range. |
| File-size guarantee in a vendor document | Vendor-stated | Check whether the statement applies to this workload and configuration. |

**Beginner exit condition:** compute daily logical volume with correct units, classify data form, and state the assumptions and evidence labels without notes.

## 5. Intermediate-level learning sequence

### 5.1 Estimate record, event, and file sizes

Use a field-by-field estimate when samples are not yet available, then replace it with measured sample data as soon as possible.

1. List fields, data types, maximum and typical lengths, null rates, and encoding assumptions.
2. Include keys, timestamps, schema/version fields, event envelope, delimiters or serialization syntax.
3. For files, account for headers, compression, file-level metadata, and the distribution of file sizes.
4. Distinguish a theoretical maximum from a typical mean and a high-percentile size. Large outliers may matter for memory and processing even if they barely affect the average.
5. Label the method: measured, sampled, vendor-stated, estimated, or guessed.

**Illustrative field-sizing sketch:** a compact event may contain a transaction identifier, account token, timestamp, amount, currency, status, and envelope metadata. A field-by-field sum gives an initial estimate only; actual serialized size depends on encoding, optional fields, field names, escaping, and compression. Do not report a hand-calculated estimate as measured evidence.

### 5.2 Distinguish logical layers, copies, and physical storage

Common data layers include:

- **Raw:** received from a source with limited alteration, preserving source evidence where required.
- **Processed:** validated, standardized, enriched, or modelled data.
- **Replicated:** copies maintained for availability, isolation, or distribution. A replica is a copy, not a new logical business event.
- **Retained:** historical data held for a specified window. Retention describes time, not a separate copy by itself.
- **Archived:** data moved to a lower-cost or different-access tier for long-term preservation.

Avoid double-counting. If processed data is derived from raw data and both are retained, they are two distinct stored representations and may both count. If “retained volume” is simply the same raw dataset over seven years, do not add it again as a separate layer. Define each row in the estimate as a distinct physical representation or copy.

A useful worksheet-level formula is:

```text
physical_storage = Σ [layer_logical_volume × copies × (1 + overhead_factor)]
```

This formula is appropriate only when `layer_logical_volume` is already the volume **after the compression assumption for that layer**, or when compression is handled separately before applying the formula. If the input is uncompressed logical bytes, calculate compressed bytes first. Do not apply compression twice. `overhead_factor` must describe what is not already included (for example, storage metadata or indexes) and must not silently include replicas already counted in `copies`.

A more explicit calculation is:

```text
compressed_layer_bytes = logical_layer_bytes / compression_ratio
stored_layer_bytes = compressed_layer_bytes × copies × (1 + overhead_factor)
total_physical_bytes = Σ stored_layer_bytes
```

Here, a compression ratio of 2.5 means uncompressed/compressed = 2.5; compressed bytes are logical bytes divided by 2.5. If the measured compression ratio is 1.2, compression saves much less. Some data may expand or compress poorly. Treat each layer's ratio and overhead as assumptions until tested.

### 5.3 Daily, monthly, annual, and multi-year volume

For a stable daily volume:

```text
monthly_volume = daily_volume × days_in_month
annual_volume  = daily_volume × 365
```

For rough planning, a 30-day month may be used if labelled as an approximation. For an exact calendar estimate, use the actual days in each month and account for leap years where relevant. State whether the volume is an average-day forecast or an actual calendar-period count.

**Worked example (illustrative):** if the assumed transaction stream is 1.0 GB/day:

- 30-day planning month: `1.0 GB/day × 30 days = 30 GB`.
- 365-day year: `1.0 GB/day × 365 days = 365 GB/year`.
- Unit check: days cancel, leaving GB. This is logical volume, not physical retained storage.
- Interpretation: a year of one representation is approximately 365 GB before compression, copies, overhead, or retention policy. If actual daily volume varies, use daily or monthly profiles instead of multiplying a single average blindly.

### 5.4 Compound growth

When a volume grows by a constant percentage each year, use compound growth:

```text
volume_at_year_n = V0 × (1 + g)^n
```

- `V0`: starting volume at the defined baseline date and scope.
- `g`: annual growth rate as a decimal (for example, 15% = 0.15).
- `n`: number of annual growth intervals.

**Worked example (illustrative):** a dataset has an annual volume of 365 GB at baseline and assumed annual growth of 15%.

- Year 1: `365 GB × 1.15 = 419.75 GB/year`.
- Year 2: `365 GB × 1.15^2 = 482.7125 GB/year`.
- Year 3: `365 GB × 1.15^3 = 555.119375 GB/year`.
- Rounded for planning: approximately 419.8, 482.7, and 555.1 GB/year respectively.
- Interpretation: these are **annual generation rates at each year**, not cumulative retained totals. If all years are retained, cumulative volume is the sum of each year's generated volume, subject to retention and the chosen model for within-year growth.
- Sensitivity: a small change in `g` compounds over time. Test low/expected/high rates instead of treating one forecast as certain.

For an explicit annual-step model, define `V_i = V_0(1+g)^i` as the volume generated in year `i`. Then:

```text
cumulative_n = Σ V_i, for i = 0..n-1, subject to retention
```

If `V0` is the first year's generated volume, a three-year total is `V0 + V0(1+g) + V0(1+g)^2`. If `V0` is a baseline rate before the first growth interval, state that convention and use it consistently. Do not confuse year-n annual volume with the cumulative sum.

### 5.5 Retention windows

A retention window determines how much historical data remains in a tier. For a stable daily generation rate `D` and a retention window of `R` days, a simple logical retained-volume approximation is:

```text
retained_logical_volume = D × R
```

This approximation assumes a stable daily rate, no deletions before the window, and a clearly defined dataset/layer. With growth, seasonality, backfills, or tier movement, sum the actual or forecast daily volumes for the dates inside the window.

**Seven-year versus ten-year retention example (illustrative):** with a stable 1.0 GB/day logical stream and 365 days/year for a planning approximation:

- 7 years: `1.0 GB/day × 365 days/year × 7 years = 2,555 GB` (2.555 TB decimal).
- 10 years: `1.0 GB/day × 365 × 10 = 3,650 GB` (3.650 TB decimal).
- Increment: `3,650 − 2,555 = 1,095 GB` (1.095 TB decimal), a 42.86% increase over the seven-year logical retained volume because `10/7 − 1 ≈ 0.4286`.
- Interpretation: all else equal, ten-year retention stores about 43% more of this stable stream than seven-year retention. This is not yet a cost estimate; tier, compression, copies, metadata, growth, and actual retention rules matter.

### 5.6 Estimate average and peak arrival rates

The roadmap's basic formula is:

```text
average_rate = daily_events / 86,400 seconds
peak_rate    = average_rate × peak_factor
```

The 86,400 denominator is seconds per 24-hour day: `24 hours × 60 minutes/hour × 60 seconds/minute = 86,400 seconds`. The formula assumes events are spread over the full day. If a source only emits during a 10-hour window, average rate during that window is `daily_events / (10 × 3,600 seconds)`, not the full-day rate.

**Worked example (illustrative):** 2,000,000 transactions/day, evenly distributed over 24 hours:

- Average rate: `2,000,000 events/day ÷ 86,400 seconds/day = 23.148... events/s`, approximately **23.15 events/s**.
- Assume, for illustration only, a peak factor of 4 based on a hypothetical measured profile: `23.148... × 4 = 92.592... events/s`, approximately **92.6 events/s**.
- If the average serialized event is also assumed to be 500 bytes (the illustrative size from Section 4.4), average payload throughput is `23.148... events/s × 500 bytes/event = 11,574 bytes/s`, approximately **11.57 kB/s** decimal. At the same assumed 4× peak factor and unchanged event size, peak payload throughput is approximately `46,296 bytes/s`, or **46.30 kB/s**. These are payload rates before protocol, framing, encryption, and retry overhead; do not treat them as a network capacity target without measuring those factors.
- Interpretation: the daily average alone would hide the assumed peak. Validate the peak factor from time-bucketed production history and test burst duration, not just a single maximum.
- Sensitivity: a peak factor of 10 would imply about 231.5 events/s under the same full-day average. At the same illustrative 500 bytes/event, that is about **115.74 kB/s** of payload. These rates may affect buffering, concurrency, partitioning, and back-pressure decisions.

A peak factor is not a universal industry constant. Define whether it is peak-to-average over one second, one minute, fifteen minutes, or another window. Different windows answer different design questions.

### 5.7 Characterise batch and streaming workloads

| Dimension | Batch workload | Streaming workload |
|---|---|---|
| Primary rate expression | GB/file, files/window, GB/batch, window duration | events/s and bytes/s, plus burst duration |
| Timing | Scheduled or triggered window | Continuous or event-triggered arrivals |
| Capacity concern | Complete within the batch window; handle late or oversized files | Sustain peaks, buffer bursts, control lag, and recover from backlog |
| Data shape | File-size distribution, rows/file, compression | Event-size distribution, key distribution, ordering and schema evolution |
| Retention concern | Staging files and replay history | Log/topic retention and replay capacity in addition to downstream storage |

Do not call a batch source “streaming” merely because it produces files frequently. For a batch that must ingest `B` GB in `T` seconds, the required average transfer rate is `B/T` GB/s over that window, converted to bytes/s or bits/s consistently. Include protocol overhead and processing time when designing a timing budget; this lesson's estimate is only the first capacity calculation.

### 5.8 Intermediate exercise: three-year storage estimate

Estimate storage for transactions, card events, and customer-profile changes using stated assumptions for event count, record size, retention, growth, compression, and copies. A complete worked example appears in Section 7; the blank worksheet is in Section 9. Do not invent source facts: label all illustrative values and list which inputs require measurement.

**Intermediate exit condition:** produce a worksheet with formulas, units, assumptions, evidence labels, and an interpretation sentence for each result; a reviewer should find no unlabelled arithmetic or ambiguous storage multiplier.

## 6. Advanced-level learning sequence

### 6.1 Peaks, bursts, seasonality, and recovery backlog

Daily average is a weak predictor when the workload is seasonal. Payroll days, month-end close, holidays, business opening hours, and post-outage catch-up can create peaks. Use historical time buckets when available and retain enough detail to see duration and recurrence.

A robust peak worksheet records:

- event counts per time bucket (for example, 1 second, 1 minute, 15 minutes, and 1 hour where relevant);
- average, p95/p99 or maximum rates for the chosen window;
- peak-to-average ratio and the window used;
- event-size distribution, not just event count;
- burst duration and frequency;
- expected backlog after a disruption and the required drain time.

If a system receives `λ` events/s while down and later processes `μ` events/s, the backlog accumulated during downtime `t` is approximately `λt` events under a constant-arrival assumption. To drain while new events continue arriving, the net drain rate is `μ − λ`, which must be positive; approximate drain time is `backlog/(μ−λ)`. This is an analytical extension, not a replacement for testing actual replay and processing behaviour.

### 6.2 Low, expected, and high estimates

Represent uncertainty explicitly. A low/expected/high estimate is not a statistical confidence interval unless a probability model supports that interpretation. It is a scenario range built from named assumptions.

For compound growth:

```text
low_volume  = V0 × (1 + g_low)^n
expected    = V0 × (1 + g_expected)^n
high_volume = V0 × (1 + g_high)^n
```

For total storage, apply the same scenario discipline to event counts, event size, retention, copies, compression, and overhead. Do not choose every low input for one scenario and every high input for another without explaining whether those combinations are plausible. Record correlations: growth and event size may rise together if the source adds fields.

**Illustrative sensitivity example:** if a three-year annual volume forecast is sensitive to growth rate, compare 5%, 15%, and 25% rather than treating 15% as known. Using an illustrative baseline of 365 GB/year and the formula above, the year-three annual generation rates are:

- 5%: `365 × 1.05^3 = 422.533125 GB/year` (about 422.5 GB/year).
- 15%: `365 × 1.15^3 = 555.119375 GB/year` (about 555.1 GB/year).
- 25%: `365 × 1.25^3 = 712.890625 GB/year` (about 712.9 GB/year).

The high case is about 1.69 times the low case. If that difference changes storage tier, partitioning strategy, or commercial commitment, growth deserves validation. If the decision is unchanged across the range, a rough estimate may be sufficient at this stage.

### 6.3 Capacity is not the same as stored data size

- **Data at rest:** bytes held on disk/object storage/database volumes, including retained layers, replicas, indexes, metadata, and safety headroom as applicable.
- **Data in motion:** bytes transferred over a network or through a pipeline. Estimate throughput and burst rates; include protocol and encryption overhead where material and known.
- **Data in processing:** memory and temporary capacity used for parsing, decompression, joins, sorts, indexes, caches, and distributed shuffle. These depend on algorithms, concurrency, partition skew, and execution plans, not just input size.

A 1 TB dataset does not imply that a job needs exactly 1 TB of memory, nor that a network must transfer it in a particular time. Processing can expand compressed inputs and create multiple intermediate copies. Conversely, streaming can have a modest retained volume but a demanding peak rate. Size each resource from its own workload model.

### 6.4 Variety, schema management, and storage layout

Structured data supports explicit columns and predictable type handling, but nulls, variable strings, indexes, and engine overhead still matter. Semi-structured data can be flexible, but repeated keys and nested arrays may increase serialized size and parsing cost. Unstructured files vary widely in size and may require derivatives or indexes for search. Schema evolution can change record size and break assumptions; capture version distributions and measure before/after changes.

Storage format affects compression, scan efficiency, metadata, and write/read patterns. It is appropriate to compare representative data in candidate formats, but do not turn an estimate into a premature product or format mandate. The later storage-architecture module owns detailed technology selection.

### 6.5 Evidence quality and confidence

| Label | Meaning | How to use it |
|---|---|---|
| Measured | Observed from a system counter, logs, billing data, or production sample with known scope | Strongest starting point; verify counter definitions, time period, missing data, and duplication. |
| Sampled | Calculated from a sample of records/files | Record sample size, time window, selection method, and representativeness. |
| Vendor-stated | Supplied by a vendor or provider | Verify configuration, workload, unit, exclusions, and whether it is a guarantee or example. |
| Estimated | Derived from explicit assumptions or a field-by-field model | Keep formula and assumptions visible; replace with evidence when possible. |
| Guessed | Intuition without sufficient evidence | Low confidence; do not use as a firm commitment without a validation plan. |

Confidence and impact are separate. A low-confidence input with little decision impact can wait; a low-confidence input that could change the design should be validated early. Record an owner and a date for high-impact validation work.

### 6.6 Independent sanity checks

Use at least two methods for material estimates:

- **Bottom-up:** record count × measured average bytes × time, then apply explicit retention and physical factors.
- **Top-down:** compare with source file totals, storage inventory, billing records, or observed daily transfer volume.
- **Cross-system check:** reconcile producer event counts with consumer counts and account for filtering, duplicates, and retries.
- **Capacity check:** compare required peak throughput with known network, source, and processing limits; do not assume advertised maximums are sustained throughput.

When two estimates differ by a factor of five, do not average them blindly. Compare scope, time window, bytes-versus-bits, decimal-versus-binary units, compression state, duplicate counting, retention, and whether one estimate counts raw plus processed layers while the other counts only one layer.

### 6.7 Translate estimates into architecture implications

The estimate should identify what the numbers imply, not pretend that a single number chooses the architecture. Examples:

- A large retained volume may justify separating frequently queried data from long-term archive tiers.
- High peak rate or bursts may require buffering, partitioning, concurrency, and back-pressure testing.
- A batch that cannot fit the source's available window may require changing the schedule, parallelising extraction, or negotiating the target.
- Large intermediate data or skew may make shuffle and memory behaviour more important than final stored bytes.
- Variable event size or evolving schemas may require stronger schema controls and representative load testing.
- A tenfold uncertainty range that crosses a technology or cost threshold is a reason to validate inputs before committing.

Do not choose a named platform solely from volume. Requirements, data locality, governance, latency, team capabilities, cost, and constraints also matter.

**Advanced exit condition:** present a range, sensitivity ranking, evidence label for every material input, independent sanity check, and architecture implications. Defend which estimates must be validated before commitment.

## 7. Industry-application exercises

All values in the examples below are illustrative. These exercises use the fictional Northbridge Bank scenario from the module roadmap: about 3 million retail customers; about 2 million card transactions/day on average; card files emitted every 15 minutes today; and a seven-year transaction retention assumption. The roadmap does not supply actual event sizes, card-event counts, profile-change rates, compression ratios, overhead percentages, or replication counts. Those must remain labelled assumptions until evidence is collected.

### 7.1 Exercise A — Northbridge volume and growth worksheet

Build a worksheet for at least these logical feeds:

1. Card transactions.
2. Other card events (define exactly which event types are included).
3. Customer-profile changes.

For each feed, include: source/system, scope, record/event definition, daily count, average size, unit convention, daily logical volume, monthly/annual volume, growth assumptions, retention, raw/processed/archive layers, copies, compression, overhead, physical estimate, low/expected/high cases, evidence label, confidence, owner, validation action, and architecture implication.

**Answer guidance:** The 2 million transactions/day value is an illustrative scenario input. A 500-byte average transaction record is used in the earlier worked example solely to demonstrate the calculation; do not imply the roadmap provides this size. The roadmap does not provide enough information to produce a fact-based total platform estimate. A valid submission explicitly labels assumed event counts and sizes, calculates the results consistently, and lists which assumptions must be sampled or confirmed.

### 7.2 Exercise B — Retention change from seven to ten years

Using the stable 1.0 GB/day illustrative stream from Section 5.5, compute logical volume for seven and ten years, the difference, and the percentage increase. Then explain how the result changes if daily volume grows, if older data moves to archive, or if compression differs by age.

**Answer:** Under the stated stable-volume, 365-day-year approximation, seven years = 2.555 TB, ten years = 3.650 TB, difference = 1.095 TB, and percentage increase = `(10−7)/7 × 100 ≈ 42.86%`. These are logical volumes for one representation. Physical cost requires tier, compression, copy, and overhead assumptions.

### 7.3 Exercise C — Decide what is ready and what needs validation

Write a half-page note separating:

- estimates adequate for early architecture exploration;
- estimates whose uncertainty could change the design or budget;
- evidence needed to improve confidence;
- an owner and due date for each critical validation.

**Answer guidance:** A rough daily order of magnitude may be enough to compare broad approaches. Peak event size/rate, retention obligations, and high-impact compression/copy assumptions usually deserve validation before a capacity or cost commitment if their ranges cross a decision threshold. State the basis for your conclusion rather than declaring every estimate “good enough.”

### 7.4 Exercise D — Streaming peak-load and three-year capacity

Choose a hypothetical streaming feed. State average events/day, average event bytes, peak factor and time window, growth range, retention, copies, compression, and overhead. Calculate daily logical bytes, average events/s, peak events/s, bytes/s, and a three-year capacity range. Rank the three inputs that most affect the result.

**Answer guidance:** Show every formula and unit. If the peak factor is applied to event rate, do not apply it to the whole day's retained volume unless the daily event count also changes. Distinguish annual generation rate from cumulative retained volume.

### 7.5 Reusable worksheet fields

Use the blank worksheet in Section 9. At minimum, every material estimate must contain formula, units, assumptions, source/evidence label, confidence, interpretation, and next validation action. A reviewer must be able to recompute it independently.

## 8. Practical scenarios and case-based reasoning

### 8.1 Scenario: “About a million events a day”

A source team reports “about a million events a day.” Identify at least five questions before using the number.

**Model questions:**

1. What counts as an event, and which event types are included or excluded?
2. Is the count measured, sampled, vendor-stated, estimated, or guessed—and over which dates?
3. Is it an average day, a peak day, a business day, or a full 24-hour period?
4. Are retries, duplicates, late arrivals, rejected events, and replayed events counted?
5. What is the average and high-percentile serialized event size, and in which format?
6. Is the number source-side produced events or successfully ingested downstream events?
7. What are the burst windows, seasonality, and expected post-outage backlog?
8. What retention, replay, and downstream copy requirements apply?

The first five questions satisfy the roadmap exercise; the additional questions strengthen the evidence and scope.

### 8.2 Scenario: month-end is four times average for three days

Assume (illustratively) a normal average of 2,000,000 events/day and a month-end volume of four times that average for three days.

- Normal daily count: 2,000,000 events/day.
- Month-end daily count: `2,000,000 × 4 = 8,000,000 events/day`.
- For three days: `8,000,000 × 3 = 24,000,000 events`.
- Baseline three-day volume at normal rate: `2,000,000 × 3 = 6,000,000 events`.
- Increment above baseline over those three days: `24,000,000 − 6,000,000 = 18,000,000 events`.

If the fourfold increase is spread uniformly across 24 hours, the average during each peak day is `8,000,000 / 86,400 ≈ 92.59 events/s`. Real traffic may be more concentrated; this daily rate is not a peak-second rate.

**Architecture reasoning:** report the peak period and burst window, not just the annual or daily average. Check whether source extraction, network transfer, validation, downstream writes, and recovery can handle the extra count. If the data arrives in a fixed batch window, calculate required throughput within that window. Use historical time buckets to estimate the real peak profile.

### 8.3 Scenario: two estimates differ by a factor of five

Do not pick the larger number “to be safe” or average them before diagnosing the difference.

1. Write each estimate's scope and date range side by side.
2. Check units (bits/bytes, GB/GiB), per-day versus per-second, and decimal versus binary conventions.
3. Check whether sizes are compressed or uncompressed and whether averages or maxima were used.
4. Check event count definitions, duplicates, retries, rejected events, and replay.
5. Check retention, processed layers, replicas, indexes, and overhead; identify double-counted layers.
6. Recalculate independently from raw counts and representative files.
7. Document the reconciled estimate, residual uncertainty, and which source of evidence is trusted and why.

### 8.4 Northbridge Bank: three-year logical and physical capacity

The following is a **fully illustrative teaching example**, not a fact-based forecast. It demonstrates a transparent method while making clear that the roadmap supplies only some scenario facts. Assumptions below are intentionally explicit so they can be replaced with measured values.

| Feed | Illustrative daily count | Illustrative average serialized size | Daily logical volume | Assumption status |
|---|---:|---:|---:|---|
| Card transactions | 2,000,000/day | 500 bytes | 1.0 GB/day | Count comes from the roadmap's illustrative scenario; size is an additional illustrative assumption. |
| Other card events | 5,000,000/day | 700 bytes | 3.5 GB/day | Entirely illustrative; event types and counts must be validated. |
| Customer-profile changes | 100,000/day | 1,000 bytes | 0.1 GB/day | Entirely illustrative; change frequency and serialized size must be validated. |
| **Total** | **7,100,000/day** | — | **4.6 GB/day** | Sum of the illustrative feeds above. |

**Arithmetic:**

- Transactions: `2,000,000 × 500 = 1,000,000,000 bytes/day = 1.0 GB/day`.
- Other card events: `5,000,000 × 700 = 3,500,000,000 bytes/day = 3.5 GB/day`.
- Profile changes: `100,000 × 1,000 = 100,000,000 bytes/day = 0.1 GB/day`.
- Total: `1.0 + 3.5 + 0.1 = 4.6 GB/day`.
- Stable annual volume: `4.6 GB/day × 365 = 1,679 GB/year = 1.679 TB/year`.

For a simple three-year estimate, assume illustrative annual growth of 15%, no intra-year change beyond the annual-step model, and retain all three annual generations. Treat the first year as 1.679 TB, the second as `1.679 × 1.15 = 1.93085 TB`, and the third as `1.679 × 1.15² = 2.2204775 TB`. The three-year cumulative logical generation is `1.679 + 1.93085 + 2.2204775 = 5.8303275 TB`, approximately **5.830 TB**. The year-three annual generation rate is about **2.220 TB/year**; it is not the cumulative total.

Now apply explicit physical assumptions solely to show the mechanics:

- Assume one raw representation and one processed representation are both retained, each with the same logical volume. This makes total uncompressed logical layer volume `5.8303275 TB × 2 = 11.660655 TB` across three years. This assumption is a simplified teaching model, not a recommendation that all data must be stored twice.
- Assume compression ratio 2.0:1 for both layers. Compressed volume = `11.660655 TB ÷ 2 = 5.8303275 TB`.
- Assume two physical copies per layer after compression. Copy-adjusted volume = `5.8303275 × 2 = 11.660655 TB`.
- Assume a 10% overhead factor on top of those copies for defined metadata/index overhead not already counted. Physical estimate = `11.660655 × 1.10 = 12.8267205 TB`, approximately **12.827 TB**.

This estimate assumes the two layers are distinct and retained, compression is actually 2:1 for both, there are two copies of each compressed layer, and the 10% overhead excludes replicas and compression. It excludes any other unlisted copies, temporary processing space, logs, backups, safety headroom, and archive-tier-specific overhead. It also uses a simplified annual-step generation model and does not model seven-year retention fully because the example horizon is three years. A production worksheet must model the actual retention window and age-tier movement explicitly.

**Interpretation:** the three-year logical feed generation is about 5.830 TB under the illustrative growth model; the simplified physical-layer estimate is about 12.827 TB under the stated layer/copy/compression/overhead assumptions. The physical result is driven by architectural choices, not merely the feed size. Validate event counts, sampled sizes, growth, retention, compression, and copy policy before using it for budget or capacity commitments.

### 8.5 Scenario: which input would change the decision if it were ten times larger?

For each input, ask whether a tenfold change alters the architecture class, operational design, or cost decision. Examples include event size, peak rate, retention duration, and number of separately retained layers. Rank inputs by (1) uncertainty, (2) impact if wrong, and (3) cost/time to validate. A low-confidence, high-impact input should be validated first. An uncertain input can remain rough if all plausible values lead to the same decision and the assumption is recorded.

## 9. Expected outputs and deliverables

Produce the following artefacts. The examples above are completed references; the blank templates below are reusable.

### 9.1 Volume, velocity, variety, and growth worksheet — blank template

| Field | Value / notes |
|---|---|
| Dataset/feed name and owner |  |
| Business purpose / consumer |  |
| Source system and scope |  |
| Record/event definition |  |
| Data form (structured / semi-structured / unstructured) |  |
| Representation measured (CSV / JSON / database / Parquet / other) |  |
| Count and time window |  |
| Average / p95 / maximum record size |  |
| Unit convention (decimal or binary) |  |
| Evidence label and source |  |
| Confidence and known limitations |  |
| Daily logical volume formula and result |  |
| Monthly / annual volume and calendar assumption |  |
| Growth low / expected / high |  |
| Retention window and tier policy |  |
| Raw / processed / archive representations |  |
| Copies/replicas and what each represents |  |
| Compression ratio by layer and evidence |  |
| Overhead factor and what it includes |  |
| Physical storage formula and result |  |
| Average rate and peak factor/window |  |
| Batch window or streaming burst/replay behaviour |  |
| Low / expected / high scenario results |  |
| Sensitivity ranking |  |
| Independent sanity check |  |
| Architecture implications |  |
| Open questions / validation action / owner / due date |  |

### 9.2 Range and sensitivity table — blank template

| Input | Low | Expected | High | Evidence/confidence | Result affected | Sensitivity rank | Validation action |
|---|---:|---:|---:|---|---|---:|---|
| Daily event count |  |  |  |  |  |  |  |
| Average event size |  |  |  |  |  |  |  |
| Annual growth |  |  |  |  |  |  |  |
| Retention |  |  |  |  |  |  |  |
| Compression ratio |  |  |  |  |  |  |  |
| Copies/replicas |  |  |  |  |  |  |  |
| Overhead |  |  |  |  |  |  |  |
| Peak factor / window |  |  |  |  |  |  |  |

**Sensitivity method:** hold all other inputs constant, vary one input across its plausible range, recalculate the result, and record the change. This is a one-at-a-time screening method; it does not capture interactions. If two inputs are correlated or jointly determine the design, also test plausible combined scenarios.

### 9.3 Architecture implications note — template

- **Decision or question being supported:**
- **Best current estimate and range:**
- **Most influential assumptions:**
- **Evidence quality and unresolved uncertainty:**
- **Implications for storage, ingestion, network, processing, and retention:**
- **What is safe to decide now:**
- **What must be validated before commitment:**
- **Validation owner, method, and due date:**
- **Trigger that would cause the estimate or decision to be revisited:**

### 9.4 Example evidence log

| Input | Value | Evidence label | Source/method | Confidence | Limitation | Next action |
|---|---:|---|---|---|---|---|
| Transactions/day | 2,000,000/day | Illustrative scenario input | Northbridge teaching scenario | Not production evidence | No source measurement supplied | Confirm from source counters over representative dates. |
| Transaction size | 500 bytes/event | Estimated illustrative assumption | Worked example only | Low until sampled | Format and overhead scope must be defined | Sample representative serialized records and compute mean/p95. |
| Other card events/day | 5,000,000/day | Guessed illustrative assumption | Teaching example | Low | Event taxonomy and count unknown | Define included event types and query producer logs. |
| Compression ratio | 2.0:1 | Assumed illustrative value | Teaching calculation | Low until benchmarked | Dataset and codec dependent | Test representative data and measure ratio. |

### 9.5 Answers to Topic 3 practice questions — self-check

1. **Why can one record have different sizes in a database, CSV, and compressed columnar file?** Different serialization, metadata, indexes, page layout, repeated values, and compression behaviour; define the representation and measure it.
2. **What changes if retention doubles?** Under a stable rate and unchanged tier/copy policy, logical retained volume approximately doubles. With growth, tiering, or age-dependent compression, calculate the retained dates/layers explicitly.
3. **Which input has the widest uncertainty?** There is no universal answer. Identify it from the evidence log and plausible range; it is often a guessed growth rate, peak factor, or unmeasured size distribution.
4. **Is storage or ingestion rate the binding limit?** Compare independent requirements: retained physical bytes versus peak events/s and bytes/s over the required window. The binding constraint is whichever approaches its practical capacity or misses a target; it cannot be inferred from daily volume alone.
5. **Why is a peak factor insufficient by itself?** It must identify the averaging window and be supported by a profile; a 4× one-hour peak differs from a 4× one-second burst.
6. **What does a 10× sensitivity test tell you?** Whether an uncertain input could cross an architectural, performance, or cost threshold and therefore needs validation before commitment.

## 10. Common mistakes and misconceptions

1. **Mixing GB and GiB.** Label decimal/binary units and convert explicitly.
2. **Mixing bits and bytes.** Network rates in bits/s are eight times bytes/s before protocol overhead.
3. **Mixing per-day and per-second values.** Write units at every step; use 86,400 seconds for a full day.
4. **Sizing for the average only.** Include peaks, bursts, seasonality, and backlog recovery.
5. **Ignoring replication, indexes, and retention.** Include them explicitly, but do not count them twice.
6. **Treating retention as an extra layer automatically.** Retention is a time policy. Add volume only for distinct stored representations/copies.
7. **Applying compression twice or using a universal ratio.** State whether input bytes are compressed and test the ratio per data type/layer.
8. **Using one point estimate as certainty.** Give ranges and sensitivity for material inputs.
9. **Treating growth as linear when it compounds.** Use the correct model and define whether a value is annual generation or cumulative retained volume.
10. **Using a peak factor without a time window.** State whether the factor applies to one second, one minute, or another period.
11. **Presenting guesses as facts.** Label evidence quality and confidence; assign validation work.
12. **Sizing compute from stored bytes alone.** Include memory expansion, intermediate results, shuffle, indexes, concurrency, and algorithm behaviour.
13. **Ignoring data variety and schema evolution.** A field added to every event can affect serialized size, parsing, and downstream compatibility.
14. **Comparing incompatible estimates.** Align scope, time window, unit, representation, retention, and copy assumptions before reconciliation.
15. **Reporting a precise result from imprecise inputs.** Arithmetic can be exact while the estimate remains uncertain. Round outputs to a precision justified by the inputs.

## 11. Mastery criteria

You have mastered this topic when you can:

- calculate daily, monthly, annual, and multi-year volume with correct formulas, units, and explicit calendar assumptions;
- distinguish structured, semi-structured, and unstructured data and explain representation-dependent size effects;
- model raw, processed, replicated, retained, and archived data without double-counting;
- estimate average and peak rates with a justified time window and explain batch versus streaming consequences;
- model growth, retention, compression, copies, and overhead while distinguishing logical volume from physical storage;
- provide low/expected/high scenarios and rank material inputs by sensitivity;
- label each important input's evidence quality and confidence, and perform at least one independent sanity check;
- explain which architectural decisions are affected and what evidence is required before commitment;
- produce a worksheet another reviewer can recompute with the same results.

A polished worksheet is not sufficient if units are inconsistent or assumptions are hidden. A short, reproducible estimate with explicit uncertainty is better than a detailed but unauditable spreadsheet.

## 12. Completion gate

Do not mark this topic complete until every check passes:

- [ ] The volume/growth worksheet is complete and independently recomputed by a reviewer with the same results.
- [ ] Units are consistent throughout; conversions are shown, and decimal versus binary units are explicit.
- [ ] Every material input has a source/evidence label and confidence level.
- [ ] Daily/monthly/annual growth, retention, peak-rate, compression, replication, and overhead arithmetic has been checked.
- [ ] Logical volume and physical storage are clearly distinguished; no layer, replica, or compression factor is double-counted.
- [ ] Low/expected/high estimates and a sensitivity ranking accompany material estimates.
- [ ] Architecture implications and assumptions needing validation are documented.
- [ ] Topic 3 practice questions have been answered and corrected.

**Completion decision:** pass only when the worksheet is reproducible, units and conversions are consistent, evidence quality is visible, and the estimates are appropriately qualified. If a material input is still guessed, record the validation action and do not present the resulting estimate as a production commitment.
