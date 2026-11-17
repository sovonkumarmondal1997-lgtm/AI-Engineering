# Sampling and Approximate Algorithms: HyperLogLog and Sketches

> **Stage 2C — Data Engineering_3 · Module 09 — Analytics Foundations for Data Engineers · Lesson 02 of 09**
>
> **Scope:** sampling, approximate summaries, mergeable sketches, error budgeting, and production use. This lesson follows `01-descriptive-statistics-and-distributions-at-scale.md` and precedes hypothesis testing. It does not teach the later lessons on inference, experimentation, cohorts, time series, or dashboards.

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Distinguish a population, a sample, sampling error, selection bias, and representativeness.
- Choose among simple random, systematic, stratified, deterministic hash, reservoir, and weighted sampling.
- Explain why exact distinct counts, quantiles, and heavy hitters may require substantial state, shuffling, sorting, or memory.
- Explain HyperLogLog (HLL), quantile sketches, Bloom filters, and count-min sketches, including their distinct error properties.
- Merge compatible sketches across partitions and reporting periods without adding or averaging estimates incorrectly.
- Implement and test reproducible sampling and simple probabilistic data structures in Python.
- Use SQL and Apache DataSketches where supported, while checking engine- and version-specific APIs.
- Define an error budget and validate approximate outputs against exact calculations on representative data.
- Distinguish computational approximation from differential privacy.

## 2. Why sampling and sketches matter in Data Engineering

A product platform may ingest billions of events each month. Analysts still ask ordinary questions: How many unique users visited? What is the p99 latency? Which event names dominate traffic? Is a key likely to exist in a large reference set?

An exact answer can be appropriate, but it may require retaining or shuffling large amounts of state. A sample reduces the amount of data processed, while a **sketch** is a compact summary designed to answer a particular class of questions approximately. They solve different problems:

| Method | Stores/processes | Typical question | Main caveat |
|---|---|---|---|
| Sample | A subset of records | What does this population look like? | Can be biased or noisy |
| HyperLogLog | Compact hashed-cardinality state | How many distinct values? | Approximate cardinality, not identities |
| Quantile sketch | Compact distribution summary | What are p50/p95/p99? | Error definition depends on algorithm |
| Bloom filter | Bit array | Is this item possibly present? | False positives are possible |
| Count-min sketch | Small counter arrays | How frequent is this key? | Frequency estimates overestimate under standard assumptions |
| Exact aggregation | Exact values/state needed by query | What is the exact result? | Can cost more time, memory, or data movement |

A sketch is not a compressed copy of the source table. It intentionally preserves enough information for specific operations and discards the rest. An HLL sketch cannot answer arbitrary quantiles; a Bloom filter cannot return the matching rows; a quantile sketch cannot generally answer exact membership.

**Engineering principle:** choose the data structure from the question and required error contract—not from the label “approximate.”

## 3. Prerequisites and environment setup

You should be comfortable with Python functions, iterables, sets, basic probability, SQL aggregation, and partitioned data processing. Lesson 01 introduces descriptive statistics and percentiles.

Create an isolated environment with Python 3.12 or later. The examples below use NumPy and optionally DuckDB, Polars, and Apache DataSketches.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install numpy pandas duckdb polars datasketches
```

Some sections use only the Python standard library and NumPy. Install packages only for the sections you run. SQL examples are illustrative across engines; syntax and available functions vary by engine and version. The Apache DataSketches Python API examples target the `datasketches` package family; confirm the installed version's API documentation before adopting them in a production job.

**Reproducibility rule:** fix random seeds in experiments, record dependency versions, and record the hash function, encoding, seed, sketch parameters, and serialization format in persisted metadata.

## 4. Sampling fundamentals

### 4.1 Population, sample, parameter, and estimate

The **population** is the complete set of units relevant to the question. A **sample** is the subset actually observed or selected. A population quantity such as the true mean or proportion is a **parameter**; a value computed from the sample is an **estimate**.

Suppose a service processed 1,000,000 requests and we inspect a simple random sample of 10,000. The full population p99 latency is a fixed quantity for that request set; the sample p99 is an estimate and varies from sample to sample.

Sampling is useful when reading or processing the whole population is too expensive, or when a smaller representative subset is sufficient for debugging, exploration, or quality checks. It is not automatically suitable for exact billing, compliance counts, or rare-event detection.

### 4.2 Simple random sampling

In simple random sampling without replacement, each possible sample of a fixed size has equal probability of selection. With replacement, each draw is independent and an item can be selected more than once. The distinction affects variance formulas and duplicate handling.

For a population of size \(N\), a sample of size \(n\), and a sample mean \(\bar{x}\), the standard error under simple random sampling without replacement is

\[
SE(\bar{x}) \approx \frac{s}{\sqrt{n}}\sqrt{1-\frac{n}{N}},
\]

where \(s\) is the sample standard deviation computed with denominator \(n-1\). The square-root term is the estimated finite-population correction for simple random sampling without replacement. This is an estimated standard error, not an exact value because the population variance is unknown. When the sample is a small fraction of a very large population, the correction is close to 1, so the standard error is approximately \(s/\sqrt{n}\). If the population standard deviation is defined with denominator \(N\), the exact variance expression uses \( (N-n)/(N-1) \) in the corresponding correction.

For an estimated proportion \(\hat p\), a common approximate standard error is \(\sqrt{\hat p(1-\hat p)/n}\), with a finite-population correction when sampling without replacement from a finite population. This approximation relies on probability sampling and sufficiently suitable sample size; it can be poor for tiny samples or extreme proportions. A confidence interval adds a critical-value multiplier and has its own assumptions. These are sampling-error formulas, not guarantees against bias.

**Inverse-square-root intuition:** to halve the standard error, you generally need about four times as many independent observations. Increasing sample size reduces random error slowly. It does not repair a systematically biased sample.

Example: if a mean estimate has an approximate standard error of 4 units at \(n=1,000\), a comparable design with \(n=4,000\) has standard error around 2 units, all else equal. Do not interpret this as a universal promise for correlated, clustered, weighted, or biased data.

### 4.3 Sampling error versus bias

- **Sampling error** is random variation caused by observing a sample rather than the entire population.
- **Selection bias** occurs when selection probabilities or inclusion mechanisms systematically favour some units.
- **Nonresponse bias** occurs when selected units fail to provide data in a way related to the measured outcome.
- **Coverage bias** occurs when the sampling frame omits part of the target population.

A million records from the wrong population can be less useful than a thousand records selected correctly. A deterministic sample is reproducible, but reproducibility alone does not establish representativeness.

### 4.4 Sampling without replacement, with replacement, and duplicates

Sampling without replacement selects unique rows. Sampling with replacement can select the same row multiple times. Bootstrap resampling commonly samples with replacement to approximate the variability of an estimator; ordinary audit sampling often aims to select unique units.

If events are sampled but the question concerns users, many events from a small number of users can dominate the sample. Select at the unit that matches the estimand (for example, users rather than events), or account for the clustered design. This lesson focuses on sampling design; formal inferential procedures belong to later material.

## 5. Sampling strategies and bias

### 5.1 Random, systematic, and stratified sampling

**Simple random sampling:** select units uniformly from a well-defined frame. It is easy to reason about, but may under-sample rare segments by chance.

**Systematic sampling:** select every \(k\)-th record after a random start. It is cheap for ordered files or streams, but periodicity can bias results if the data order has a pattern aligned with \(k\). “Every 100th row” is not inherently random.

**Stratified sampling:** partition the population into meaningful strata (region, device, plan, event class), then sample within each stratum. This guarantees representation of selected strata. If the sample fractions differ across strata, an unweighted overall sample mean generally does not estimate the population mean correctly; use inclusion-probability weights or combine stratum estimates using population sizes.

For stratum \(h\), let population size be \(N_h\), sample size \(n_h\), sample mean \(\bar{x}_h\). The population mean estimate under stratified sampling is

\[
\hat{\mu}_{st}=\sum_h \frac{N_h}{N}\bar{x}_h, \quad N=\sum_h N_h.
\]

Hand example: Region A contains 900 records with mean spend 10; Region B contains 100 records with mean spend 50. The population mean is \((900\cdot10+100\cdot50)/1000=14\). The unweighted mean of the two regional means is 30 and is wrong for the population. Stratification can deliberately oversample B for analysis, but weights are needed to recover population-level summaries.

**When stratification helps:** quality audits where rare event types matter, regional comparisons, fraud reviews, or ensuring a small but important customer segment is represented. It does not remove bias inside a stratum.

### 5.2 Database sampling: `TABLESAMPLE` and DuckDB `USING SAMPLE`

SQL sampling syntax is not portable. `TABLESAMPLE` can use row-based or block/page-based methods depending on the engine. A block sample can be much faster but may be less representative if records are clustered by time, customer, or event type. Some engines apply sampling before or after other operations differently; consult the engine's documented semantics.

Example pattern (supported syntax varies):

```sql
-- Illustrative only: TABLESAMPLE syntax and semantics vary by engine.
SELECT *
FROM events TABLESAMPLE BERNOULLI (1);
```

DuckDB supports `USING SAMPLE`; exact options depend on version and sample method. Example:

```sql
-- DuckDB example; verify syntax for the installed DuckDB version.
SELECT *
FROM read_parquet('data/events/*.parquet')
USING SAMPLE 10 PERCENT;
```

A table sample is excellent for quick exploration, query prototyping, and checking schema/content. Do not assume it is deterministic or a statistically valid sample for every query. Verify whether the engine samples rows or storage blocks and whether repeated queries produce the same sample.

### 5.3 DataFrame sampling

Pandas and Polars expose sampling APIs, but defaults and options differ. In pandas, `df.sample(frac=0.1, random_state=42)` gives a reproducible sample for a stable DataFrame and library version. In Polars, use the documented `sample` API for the installed version and set a seed if supported. A DataFrame sample normally requires the data to have been read into or represented by that engine; it is not automatically a scalable substitute for storage-level sampling.

```python
import pandas as pd

frame = pd.DataFrame({"user_id": range(10_000), "value": range(10_000)})
sample = frame.sample(frac=0.10, random_state=42)
assert len(sample) == 1_000
assert sample["user_id"].is_unique
```

Expected behaviour: 1,000 unique rows and the same selection for repeated runs using the same input, pandas behavior, and seed. This does not promise stable membership after row ordering or library behavior changes.

### 5.4 Deterministic hash-based sampling

A common scalable pattern selects rows when a stable hash of a key falls into a bucket:

```python
import hashlib

def sample_bucket(key: str, *, buckets: int = 100, selected: int = 5) -> bool:
    if buckets <= 0 or not 0 <= selected <= buckets:
        raise ValueError("invalid bucket configuration")
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    bucket = int.from_bytes(digest[:8], "big") % buckets
    return bucket < selected

assert sample_bucket("user-42") == sample_bucket("user-42")
```

This selects approximately 5% if hash buckets are well distributed over the actual key population. Membership is stable only while the hash algorithm, key encoding and normalization, seed/configuration, bucket count, and selection rule remain stable. If the number of buckets changes, membership can change. A cryptographic hash is generally well-distributed, but modulo reduction can have tiny unevenness unless the mapping is designed carefully; for ordinary bucket counts this is typically negligible, not mathematically zero.

Do not hash a mutable field such as event timestamp if the goal is to keep the same user in the sample. Do not use Python's built-in `hash()` for persisted cross-process sampling: its string hash is randomized by default between processes. If selecting by user ID, the sample represents users more directly than events only if the sampling unit is one stable user ID and all that user's records are consistently included.

### 5.5 Weighted sampling and inclusion probabilities

When units have unequal selection probabilities, unweighted summaries can be biased. If unit \(i\) has known inclusion probability \(\pi_i\), a Horvitz–Thompson total estimator is

\[
\hat{T}_{HT}=\sum_{i\in s}\frac{y_i}{\pi_i}.
\]

For a population mean, a common ratio-style estimator divides the weighted total by the corresponding weighted count, \(\sum_{i\in s}1/\pi_i\); this is often called a Hájek estimator and is not exactly unbiased in every finite-sample design. Weighted estimates can have higher variance, especially with extreme weights. Report the design and weighting assumptions.

Weighted sampling can mean two different things: (1) selecting units with probabilities proportional to importance/weight, or (2) using sampling weights to estimate population quantities after unequal-probability selection. Do not conflate these. For reservoir sampling with weights, algorithms such as weighted reservoir schemes are needed; simply assigning each incoming record a random integer weight is not a correct general solution.

### 5.6 Rare events, stratification, and importance sampling

A uniform 0.1% sample may contain no examples of a rare failure mode. If an event has prevalence \(p\), the probability of seeing at least one event in \(n\) independent draws is \(1-(1-p)^n\). For \(p=0.0001\) and \(n=1,000\), this probability is only about 9.5%. The approximation \(1-(1-p)^n\approx1-e^{-np}\) is useful for small \(p\).

Oversampling rare events is useful for debugging and model/data-quality inspection, but it distorts raw prevalence. Preserve stratum sizes or inclusion probabilities and reweight if estimating population rates. **Importance sampling** samples according to a proposal distribution chosen to observe important or rare outcomes, then uses weights to correct estimates. It can greatly reduce variance for a well-designed target, but poor weights can increase variance dramatically.

## 6. HyperLogLog in depth

### 6.1 Problem and representation

Exact distinct counting conceptually needs to distinguish all distinct values. An exact hash set can consume memory proportional to cardinality and may require distributed shuffle/deduplication. HyperLogLog (HLL) estimates cardinality using a compact array of registers derived from hashes. Its memory is controlled mainly by precision, not directly by the number of distinct values.

The algorithm hashes each item to a sufficiently uniform bit string, uses some bits to choose one of \(m=2^p\) registers, and examines the remaining bits for the position of the first set bit (or equivalent leading-zero statistic). Each register stores the maximum observed rank for its bucket. Intuitively, seeing a long run of zero bits is rare; the maximum rank provides evidence about how many distinct hashes were observed.

A classical HLL estimator has relative standard error approximately

\[
RSE \approx \frac{1.04}{\sqrt{m}} = \frac{1.04}{\sqrt{2^p}},
\]

under the algorithm's usual large-cardinality assumptions and idealized hash behaviour. This is an expected/standard-error approximation, not a strict per-query error bound. Real implementations may use bias corrections, linear counting for small cardinalities, and different register encodings. Do not promise that every answer lies within one RSE.

For intuition, \(p=10\) gives \(m=1024\) registers and an RSE near 3.25%; \(p=14\) gives 16,384 registers and an RSE near 0.81%. Higher precision generally costs more memory. Actual memory depends on implementation, representation, and serialization.

### 6.2 Four-register hand example

Use these ten **toy 8-bit hash strings** to simulate the register updates (they are illustrative hash outputs, not hashes of real IDs). With four registers, the first two bits choose register 0–3. The remaining six bits determine rank: the 1-based position of the first `1`, or 7 if all six bits are zero.

| Value | Toy hash | Register | Suffix | Rank | Register after update |
|---|---|---:|---|---:|---|
| v1 | `00010000` | 0 | `010000` | 2 | `[2, 0, 0, 0]` |
| v2 | `00000110` | 0 | `000110` | 4 | `[4, 0, 0, 0]` |
| v3 | `01001000` | 1 | `001000` | 3 | `[4, 3, 0, 0]` |
| v4 | `01110000` | 1 | `110000` | 1 | `[4, 3, 0, 0]` |
| v5 | `10000010` | 2 | `000010` | 5 | `[4, 3, 5, 0]` |
| v6 | `10101000` | 2 | `101000` | 1 | `[4, 3, 5, 0]` |
| v7 | `11000100` | 3 | `000100` | 4 | `[4, 3, 5, 4]` |
| v8 | `11010000` | 3 | `010000` | 2 | `[4, 3, 5, 4]` |
| v9 | `00100100` | 0 | `100100` | 1 | `[4, 3, 5, 4]` |
| v10 | `10110000` | 2 | `110000` | 1 | `[4, 3, 5, 4]` |

The final toy registers are `[4, 3, 5, 4]`: each register keeps the maximum rank seen in its bucket, not the number of values in that bucket. This demonstrates the update rule only, not a reliable cardinality estimate. With four registers, estimates are extremely noisy and small-range corrections dominate; real systems use far more registers and implementation-specific estimators.

### 6.3 Mergeability and limits

Compatible HLL sketches merge by taking the register-wise maximum. This is why daily sketches can be merged to estimate weekly or monthly unique users. Do **not** sum daily unique counts: a user active on seven days would be counted seven times. Do not average daily HLL estimates: the overlap between days is not encoded in those scalar estimates.

Compatibility matters. Sketches may require matching family, hash function, seed, target type, and compatible precision. Some libraries support downsampling to a common lower precision; not every engine exposes the same rules. Keep sketches in a typed/serialized form with metadata rather than assuming any blob is interchangeable.

HLL estimates cardinality only. It cannot list the distinct IDs, provide arbitrary intersections, or recover exact counts. For set operations, consider theta sketches where supported.

### 6.4 SQL distinct-count examples

Function names are platform-specific:

```sql
-- BigQuery: approximate count; exact COUNT(DISTINCT ...) is also available.
SELECT APPROX_COUNT_DISTINCT(user_id) AS approx_users
FROM `project.dataset.events`;

-- Snowflake: approximate distinct count (alias availability may vary by context/version).
SELECT APPROX_COUNT_DISTINCT(user_id) AS approx_users
FROM events;

-- Spark SQL: syntax and optional relative standard deviation parameter vary by version.
SELECT approx_count_distinct(user_id) AS approx_users
FROM events;

-- ClickHouse: several uniq* aggregate functions have different algorithms and trade-offs.
SELECT uniq(user_id) AS approx_users
FROM events;
```

BigQuery also exposes HLL++ functions such as `HLL_COUNT.INIT`, `HLL_COUNT.MERGE`, and `HLL_COUNT.EXTRACT` for persisted/mergeable sketches. Snowflake has HLL functions including `HLL`, `HLL_ACCUMULATE`, `HLL_COMBINE`, and `HLL_ESTIMATE` in supported contexts. ClickHouse offers aggregate states such as `uniqState`/`uniqMerge` for supported aggregate functions. Spark's `approx_count_distinct` is an aggregate estimate; do not assume its result is a portable HLL serialized sketch. Verify exact function names, signatures, and compatibility in the target engine version.

### 6.5 Python with Apache DataSketches

Install `datasketches` as shown in setup. API details can evolve; this example uses the common Python API shape and should be checked against the installed package documentation.

```python
from datasketches import hll_sketch, tgt_hll_type, hll_union

users = [f"user-{i}" for i in range(100_000)]
exact = len(set(users))

sketch = hll_sketch(lg_k=12, tgt_type=tgt_hll_type.HLL_4)
for user in users:
    sketch.update(user)
estimate = sketch.get_estimate()

print({"exact": exact, "estimate": estimate,
       "relative_error": abs(estimate - exact) / exact})
# Expected behaviour: estimate is near exact; the precise error is run- and
# implementation-dependent. Do not assert an invented fixed output.
assert estimate > 0
assert abs(estimate - exact) / exact < 0.10  # deliberately loose smoke test

left = hll_sketch(lg_k=12, tgt_type=tgt_hll_type.HLL_4)
right = hll_sketch(lg_k=12, tgt_type=tgt_hll_type.HLL_4)
for user in users[:60_000]:
    left.update(user)
for user in users[40_000:]:
    right.update(user)
union = hll_union(lg_max_k=12)
union.update(left)
union.update(right)
merged_estimate = union.get_result().get_estimate()
assert abs(merged_estimate - len(set(users))) / len(set(users)) < 0.10
```

The two input sets overlap on 20,000 users. The merged estimate targets the union cardinality, 100,000, not the sum of input cardinalities (120,000). The loose threshold is a smoke test, not a production service-level guarantee. For rigorous validation, repeat many seeded trials across cardinalities and overlap patterns and compare empirical error with the documented estimator characteristics.

## 7. Quantile sketches

### 7.1 Why exact quantiles can be expensive

An exact median or p99 generally requires enough ordering information to locate the requested rank. A database may sort, partition, or otherwise retain substantial state. Distributed exact quantiles can require expensive data movement. An approximate quantile sketch summarizes observations so quantiles can be estimated with less memory.

Quantile algorithms differ in their error model. **Rank error** asks how far the returned item's rank is from the target rank. **Value error** asks how far the numeric value differs from the true quantile. These are not interchangeable: in a heavy-tailed distribution, a small rank error can correspond to a large value difference.

### 7.2 KLL, t-digest, and DDSketch

| Sketch | Main idea / error lens | Typical strengths | Cautions |
|---|---|---|---|
| KLL (Karnin–Lang–Liberty) | Compacts retained items at levels; commonly provides probabilistic rank-error guarantees with memory/accuracy trade-offs | Strong general-purpose quantile sketch; mergeable variants; well-studied rank error | Parameter and implementation determine guarantees; merge may affect accuracy within documented rules |
| t-digest | Clusters nearby values into weighted centroids; allocates resolution more finely near tails in common implementations | Often effective for tail quantiles such as p99; compact and mergeable implementations exist | Formal error guarantees vary; empirical accuracy depends on distribution, compression, merge order, and implementation |
| DDSketch | Logarithmic mapping of values into bins; relative-value accuracy for positive magnitudes in supported configurations | Useful for latency/size metrics where relative error matters across orders of magnitude | Requires handling zero/negative values according to implementation; mapping and collapse rules matter |

No single sketch is best for every distribution or error contract. Choose based on whether the SLO is rank error, relative value error, tail accuracy, mergeability, memory, or interoperability. Verify whether the implementation supports negative values, NaNs, infinities, weighted observations, and serialization.

### 7.3 Hand example: rank error versus value error

Consider sorted values `[1, 2, 3, 4, 5, 6, 7, 8, 9, 1000]`. The 90th percentile is near the upper tail under common quantile conventions. Returning a neighbouring rank may change the value from 9 to 1000—a huge value difference even if rank error is small. Conversely, in a dense region where adjacent values are 100.0 and 100.1, the same rank error may have tiny value error.

Always validate the quantile sketch using the business metric's relevant error measure. For latency SLOs, absolute or relative error around p99 may matter more than average rank error.

### 7.4 Apache DataSketches KLL example

```python
import numpy as np
from datasketches import kll_floats_sketch

rng = np.random.default_rng(2026)
values = rng.lognormal(mean=2.0, sigma=1.2, size=100_000).astype("float32")

sketch = kll_floats_sketch(k=200)
for value in values:
    sketch.update(float(value))

for q in (0.50, 0.95, 0.99):
    approximate = sketch.get_quantile(q)
    exact = float(np.quantile(values, q, method="linear"))
    relative_error = abs(approximate - exact) / max(abs(exact), 1e-12)
    print(q, approximate, exact, relative_error)
    assert np.isfinite(approximate)
```

Expected behaviour: finite estimates close to exact quantiles in many runs, with no fixed exact printed values promised here. This comparison uses NumPy's `linear` quantile convention; a sketch's returned quantile convention can differ. For a rank-error evaluation, compare the rank of each returned value against the target rank, rather than relying only on relative value error. The loop is intentionally clear, not necessarily the fastest ingestion strategy.

### 7.5 Merge quantile sketches correctly

When compatible KLL or t-digest sketches are merged, the merged sketch represents the union of their observations, subject to the implementation's merge semantics and error guarantees. Scalar quantiles cannot generally be merged. If daily p95 values are 100 ms and 500 ms, their average 300 ms is not the p95 of all requests in the month. Persist the sketch (or raw observations if exact recomputation is required), merge sketches, then query p50/p95/p99.

A mergeable sketch is not necessarily bit-for-bit associative in serialized output, and not all libraries' formats are interoperable. Test merge trees and version compatibility in the target implementation.

## 8. Bloom filters

### 8.1 Membership with one-sided error

A Bloom filter is a bit array of \(m\) bits plus \(k\) hash-derived positions per item. Inserting an item sets those bits to 1. A query checks the same positions:

- If any checked bit is 0, the item is **definitely absent** from the inserted set under the standard operation model.
- If all checked bits are 1, the item is **possibly present**; this may be a false positive.

For a standard Bloom filter with correctly inserted items and no unsupported mutations, there are no false negatives. False positives occur because different items can set the same bits. Deletion is not supported by a standard Bloom filter; counting Bloom filters are a different design with their own trade-offs.

The approximate false-positive probability after inserting \(n\) items is

\[
p \approx \left(1-e^{-kn/m}\right)^k,
\]

and the approximately optimal number of hash probes is \(k\approx(m/n)\ln 2\). These are idealized estimates; hash quality and implementation details matter.

Example: a Bloom filter can screen whether an incoming customer ID might already exist in a large remote key set. If it says “definitely absent,” the pipeline can skip a remote membership lookup. If it says “possibly present,” the pipeline must verify against the authoritative store. Never use a positive Bloom result as proof of existence.

### 8.2 Runnable Bloom filter implementation

This pedagogical implementation uses double hashing from SHA-256-derived values to generate positions. It is not a substitute for a reviewed production library.

```python
import hashlib
import math

class BloomFilter:
    def __init__(self, expected_items: int, false_positive_rate: float = 0.01):
        if expected_items <= 0:
            raise ValueError("expected_items must be positive")
        if not 0 < false_positive_rate < 1:
            raise ValueError("false_positive_rate must be between 0 and 1")
        self.m = max(1, math.ceil(-expected_items * math.log(false_positive_rate) / math.log(2) ** 2))
        self.k = max(1, round((self.m / expected_items) * math.log(2)))
        self.bits = bytearray((self.m + 7) // 8)

    def _positions(self, item: str):
        digest = hashlib.sha256(item.encode("utf-8")).digest()
        h1 = int.from_bytes(digest[:16], "big")
        h2 = int.from_bytes(digest[16:], "big") | 1
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, item: str) -> None:
        for pos in self._positions(item):
            self.bits[pos // 8] |= 1 << (pos % 8)

    def __contains__(self, item: str) -> bool:
        return all(self.bits[pos // 8] & (1 << (pos % 8))
                   for pos in self._positions(item))

inserted = [f"known-{i}" for i in range(20_000)]
bloom = BloomFilter(expected_items=len(inserted), false_positive_rate=0.01)
for item in inserted:
    bloom.add(item)
assert all(item in bloom for item in inserted)  # no false negatives in this test

queries = [f"unknown-{i}" for i in range(20_000)]
false_positives = sum(item in bloom for item in queries)
observed_rate = false_positives / len(queries)
print("bits:", bloom.m, "hashes:", bloom.k, "observed FPR:", observed_rate)
# Observed FPR is random/data-dependent; do not expect exactly 1%.
assert 0 <= observed_rate <= 1
```

The empirical false-positive rate fluctuates. For a meaningful evaluation, run multiple independent trials and compare the observed rate with the theoretical target and its binomial uncertainty. The filter's expected capacity matters: inserting far more than `expected_items` raises false-positive probability. Persist the parameters and hash scheme with the bit array. Bloom filters cannot be merged by naïvely OR-ing bit arrays unless their dimensions and hash configuration are compatible; even then, the resulting false-positive rate depends on total insertions.

## 9. Count-min sketch and heavy hitters

### 9.1 What it estimates

A count-min sketch maintains a \(d\times w\) table of counters. Each row has a hash function. To add key \(x\) with increment \(c\), increment one counter in each row. To estimate frequency, take the minimum counter among the key's hashed positions.

With non-negative updates and suitable independent hash functions, collisions can only add extra counts, so the estimate does not undercount the true frequency in the standard model; it overestimates because unrelated keys collide. A common parameterization for additive error \(\epsilon N\) and failure probability \(\delta\) uses \(w=\lceil e/\epsilon\rceil\), \(d=\lceil\ln(1/\delta)\rceil\), where \(N\) is total update weight. Under the assumptions of the classic analysis, the estimate is within additive \(\epsilon N\) with probability at least \(1-\delta\). This is a probabilistic bound, not a guarantee for arbitrary implementations or negative updates.

A count-min sketch answers approximate frequency queries, but it does not automatically identify all heavy hitters. To find candidate keys, maintain a candidate set (for example, a bounded heap or frequent-items algorithm), then estimate candidate frequencies with the sketch. A sketch alone has no dictionary of every key.

### 9.2 Small example

Suppose the stream is `A, A, A, B, B, C`. If `A` hashes to counters `[2, 4]` and `B` collides in one row, some counters include contributions from both keys. Querying `A` takes the minimum of its row counters, reducing (but not eliminating) collision overcount. Increasing width reduces collision probability at higher memory cost; increasing depth lowers failure probability with additional counters and hash work.

### 9.3 Runnable count-min sketch

```python
import hashlib
import math
from collections import Counter

class CountMinSketch:
    def __init__(self, epsilon: float = 0.01, delta: float = 0.01):
        if not 0 < epsilon < 1 or not 0 < delta < 1:
            raise ValueError("epsilon and delta must be between 0 and 1")
        self.width = math.ceil(math.e / epsilon)
        self.depth = math.ceil(math.log(1 / delta))
        self.table = [[0] * self.width for _ in range(self.depth)]
        self.total = 0

    def _index(self, item: str, row: int) -> int:
        payload = f"{row}:{item}".encode("utf-8")
        digest = hashlib.blake2b(payload, digest_size=8).digest()
        return int.from_bytes(digest, "big") % self.width

    def update(self, item: str, count: int = 1) -> None:
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError("count must be a non-negative integer")
        for row in range(self.depth):
            self.table[row][self._index(item, row)] += count
        self.total += count

    def estimate(self, item: str) -> int:
        return min(self.table[row][self._index(item, row)]
                   for row in range(self.depth))

stream = ["item-A"] * 1000 + ["item-B"] * 500 + [f"tail-{i % 100}" for i in range(5000)]
exact = Counter(stream)
cm = CountMinSketch(epsilon=0.005, delta=0.01)
for item in stream:
    cm.update(item)
for item, true_count in exact.items():
    estimate = cm.estimate(item)
    assert estimate >= true_count
assert cm.estimate("item-A") >= cm.estimate("item-B")
print("A exact/estimated:", exact["item-A"], cm.estimate("item-A"))
```

Expected behaviour: `item-A` remains a high-frequency candidate and standard estimates are at least the true non-negative frequencies. Exact numeric estimates depend on collisions and should not be hard-coded. The assertion is valid for this implementation because it uses non-negative increments and the same counters for updates and queries.

### 9.4 Mergeability

Two count-min sketches can be added cell by cell only if dimensions and hash functions/configuration are compatible. The resulting table corresponds to the sum of update streams. Different seeds or key encodings make direct merging invalid. Mergeability of the frequency table still does not solve candidate discovery; merge candidate summaries or use a frequent-items sketch designed for that task.

## 10. Reservoir and weighted sampling

### 10.1 Reservoir sampling for streams

Reservoir sampling selects a fixed-size uniform sample from a stream whose final length is not known in advance. For reservoir size \(k\), fill the first \(k\) slots. For the \(i\)-th item (1-indexed) after the reservoir is full, draw \(j\) uniformly from \(1\) through \(i\); if \(j\leq k\), replace slot \(j\). Each item in a finite stream of length \(N\) then has inclusion probability \(k/N\), assuming uniform random draws.

```python
import random

def reservoir_sample(items, k: int, seed: int = 42):
    if k < 0:
        raise ValueError("k must be non-negative")
    rng = random.Random(seed)
    reservoir = []
    for i, item in enumerate(items, start=1):
        if i <= k:
            reservoir.append(item)
        elif k > 0:
            j = rng.randint(1, i)
            if j <= k:
                reservoir[j - 1] = item
    return reservoir

sample = reservoir_sample(range(1_000_000), k=100, seed=42)
assert len(sample) == 100
assert len(set(sample)) == 100
assert all(0 <= x < 1_000_000 for x in sample)
assert sample == reservoir_sample(range(1_000_000), k=100, seed=42)
```

The algorithm uses O(k) memory and O(N) time. It gives a uniform sample of stream elements, not necessarily a uniform sample of users if users emit different numbers of events. For distributed streams, combining local reservoirs correctly requires a mergeable reservoir algorithm or weighted combination that accounts for partition sizes; concatenating each partition's reservoir and sampling it uniformly is generally wrong when partitions have different sizes.

### 10.2 Weighted sampling

If each record has a non-negative weight and high-weight records should be more likely to appear, use a documented weighted-reservoir algorithm (for example, exponential-race or priority-key methods under their stated assumptions). Weighted sampling is useful for prioritizing expensive examples for manual review or sampling rare/high-risk records. It changes the inclusion probabilities; if the goal is a population estimate, record the probabilities and use a suitable estimator. Zero, negative, or highly variable weights require explicit policy.

For a small **weighted sample with replacement**, Python's `random.choices` is a clear baseline:

```python
import random

items = ["routine", "warning", "critical"]
weights = [90, 9, 1]
rng = random.Random(42)
draws = rng.choices(items, weights=weights, k=20)
assert len(draws) == 20
assert set(draws) <= set(items)
```

The draw probabilities are proportional to the supplied weights and the same item may appear more than once. This is not a weighted reservoir and does not by itself supply the inclusion probabilities needed for an unbiased population estimator. If you need a fixed-size sample without replacement, choose a documented weighted-reservoir/PPS design and use that design's inclusion probabilities for estimation.

## 11. Apache DataSketches and mergeable aggregation pipelines

Apache DataSketches provides multiple sketch families, each designed for specific queries. Common families include:

- **HLL:** distinct cardinality.
- **Theta:** approximate set cardinality and set operations such as union, intersection, and difference.
- **KLL:** quantiles with documented rank-error behaviour.
- **Frequent items:** approximate frequent-item identification with implementation-specific error bounds.

These families are not interchangeable. HLL estimates the size of a set but does not generally provide intersections; theta sketches preserve information for approximate set operations. A frequent-items sketch is a more direct choice for candidate heavy hitters than trying to recover keys from a count-min table. Apache DataSketches' Python package includes `frequent_strings_sketch` and `frequent_items_sketch`; the latter uses Python objects' `__hash__`/`__eq__`, and its serialization requires a matching `PyObjectSerDe`. For the string variant, `get_frequent_items(...)` exposes a choice between `NO_FALSE_POSITIVES` (may miss heavy hitters) and `NO_FALSE_NEGATIVES` (may include false positives). Check the installed version's signature and returned tuple schema before production integration.

### 11.1 Theta set operations

Suppose daily active-user sets are A and B. The union answers “unique users active on either day,” while the intersection answers “users active on both days.” Adding `|A| + |B|` double-counts overlap. Theta sketches retain a sampled/hash-threshold representation that supports approximate set operations with documented error behavior.

Pseudocode for the operation is:

```text
sketch_A = build_theta_sketch(user_ids_day_A)
sketch_B = build_theta_sketch(user_ids_day_B)
union_sketch = theta_union(sketch_A, sketch_B)
intersection_sketch = theta_intersection(sketch_A, sketch_B)
weekly_unique_estimate = estimate(union_sketch)
repeat_users_estimate = estimate(intersection_sketch)
```

The pseudocode is intentionally API-neutral. In the current Apache DataSketches Python API family, the update-sketch class is named `update_theta_sketch`, with `theta_union` and `theta_intersection` operators; constructor arguments and serialization contracts should still be checked against the installed version. Do not copy pseudocode as if it were a guaranteed runnable API contract.

### 11.2 Persisting sketches in aggregate tables

A daily aggregate table may contain `event_date`, `country`, exact counts/sums, and serialized sketch columns such as `unique_users_hll` and `latency_kll`. A weekly job merges compatible daily sketches and extracts estimates. This allows rollups without storing every raw observation for every dashboard query.

Production metadata should include:

- Sketch family and implementation/library version.
- Precision or accuracy parameters.
- Hash algorithm, seed, and canonical key encoding where applicable.
- Serialization/version format.
- Time window, timezone, filters, dimensions, and source-data snapshot/version.
- Whether nulls, invalid values, duplicates, and late-arriving events were included.
- Merge compatibility rules and expected error metric.

Incremental updates need idempotency. If a daily sketch is merged twice into a monthly result, cardinality sketches often behave idempotently for the same register state, but not every sketch family or aggregate state has identical behavior. Do not rely on idempotency without verifying the family and pipeline semantics. Prefer recomputing a partition or storing versioned partition sketches and rebuilding the rollup deterministically.

### 11.3 Sketches and late data

If a late event arrives for yesterday, update or rebuild yesterday's sketch and recompute dependent weekly/monthly aggregates. Appending a second “corrected” sketch to the old sketch may double-count updates for some sketch families. Define a correction strategy: replace the partition sketch and recompute the affected rollups, or use a supported update/merge architecture with clear deduplication semantics.

## 12. Error budgeting and validation

### 12.1 Different meanings of “error”

Never compare error claims without checking their definition:

- **Standard error / RSE:** variability or typical relative error under a model; not a worst-case bound.
- **Rank error:** difference between target quantile rank and returned item's rank.
- **Value error:** numeric distance from the true quantile or count.
- **False-positive rate:** probability an absent item is reported as possibly present.
- **Additive frequency error:** difference between estimated and true frequency, often expressed as a fraction of total stream weight.
- **Empirical error:** observed error on a particular dataset or experiment; not a universal guarantee.
- **Worst-case or high-probability bound:** formal statement under stated assumptions, parameters, and probability level.

A reported “1% error” is meaningless unless the numerator, denominator, metric, and probability statement are clear.

### 12.2 Choose an error budget from the decision

If a dashboard only needs to distinguish 10 million users from 10.5 million, an HLL estimate with a suitable error profile may be acceptable. If the value feeds invoicing, regulatory reporting, or a threshold that triggers expensive actions, exact computation or independent reconciliation may be required.

Set a budget before choosing the algorithm:

1. Define the decision and its tolerance.
2. Specify the error metric (relative cardinality error, rank error, relative quantile value error, false-positive rate, etc.).
3. Specify confidence/probability level if the algorithm has a probabilistic guarantee.
4. Account for data-quality errors, sampling bias, late data, and semantic-definition errors separately. A sketch's algorithmic error does not cover bad event instrumentation.
5. Choose parameters and memory limits, then validate on representative distributions and cardinalities.
6. Monitor estimate drift, serialized size, merge failures, and exact-vs-approximate discrepancies on controlled samples.

### 12.3 Validation protocol

For each sketch family:

- Test small known sets, duplicates, empty input, null handling, and high cardinality.
- Test partitioned processing against a single-pass sketch built from the same observations.
- Test overlapping and disjoint partitions, because overlap is a major cardinality edge case.
- Test serialization/deserialization and version upgrades.
- Compare with exact results on manageable representative samples and across synthetic distributions.
- Measure memory, CPU, network/shuffle, and latency on the actual engine; do not extrapolate a small benchmark linearly without checking data layout and engine behavior.
- Record many trial results where randomness matters. A single successful estimate is not a validation of the error contract.

### 12.4 Approximation is not privacy

Approximation reduces retained state or computation; it does not inherently protect personal data. A sketch built from sensitive identifiers may still reveal information depending on the representation and access model. **Differential privacy (DP)** is a formal privacy framework that bounds how much the output distribution can change when one person's data is added or removed, using calibrated randomization and a privacy budget (commonly expressed using epsilon and delta). An ordinary HLL, Bloom filter, quantile sketch, or sample is not automatically differentially private. DP also introduces utility loss and requires careful composition/accounting. Treat privacy guarantees as a separate design requirement.

## 13. Python and SQL implementations

### 13.1 Deterministic sample versus full-population estimate

The next experiment compares the mean and positive rate from the full population with a deterministic hash sample. The population is generated from a known distribution and sampling uses a stable key. Results vary with the generated dataset but are reproducible under the fixed seed and algorithm.

```python
import hashlib
import numpy as np

rng = np.random.default_rng(2026)
n = 200_000
ids = np.arange(n)
values = rng.normal(loc=10.0, scale=3.0, size=n)


def keep_id(i: int, sample_percent: int = 10) -> bool:
    raw = str(int(i)).encode("ascii")
    h = hashlib.sha256(raw).digest()
    bucket = int.from_bytes(h[:8], "big") % 100
    return bucket < sample_percent

mask = np.fromiter((keep_id(i) for i in ids), dtype=bool, count=n)
full_mean = float(values.mean())
sample_mean = float(values[mask].mean())
full_positive_rate = float((values > 12).mean())
sample_positive_rate = float((values[mask] > 12).mean())
print({"sample_fraction": float(mask.mean()), "full_mean": full_mean,
       "sample_mean": sample_mean, "full_positive_rate": full_positive_rate,
       "sample_positive_rate": sample_positive_rate})
assert 0.08 < mask.mean() < 0.12
assert np.array_equal(mask, np.fromiter((keep_id(i) for i in ids), dtype=bool, count=n))
```

Interpretation: the hash sample is repeatable and should usually produce estimates near the full values, but it will not match exactly. The sample fraction can deviate from 10%. Here the stable integer ID and SHA-256 hash are independent of the generated values; if IDs were assigned in a way correlated with `values`, or the selection key were correlated with the outcome, the estimate could be biased. Do not infer “unbiased” solely from a deterministic implementation.

### 13.2 Exact distinct versus HLL and precision trials

This example is a benchmark **design**, not a claim of measured results. It reports measurements when run in your environment. It compares exact Python-set cardinality with DataSketches HLL precision settings, while using the same generated IDs. A Python set can be memory-intensive; keep `n` moderate first. For large production data, benchmark the engine-native implementation and account for serialization and distributed shuffle.

```python
import time
import tracemalloc
from datasketches import hll_sketch, tgt_hll_type

N = 500_000  # increase only after measuring available RAM
ids = [f"user-{i % 350_000}" for i in range(N)]
exact_start = time.perf_counter()
exact = len(set(ids))
exact_seconds = time.perf_counter() - exact_start
print("exact count:", exact, "seconds:", exact_seconds)

for lg_k in (10, 12, 14):
    tracemalloc.start()
    start = time.perf_counter()
    sketch = hll_sketch(lg_k=lg_k, tgt_type=tgt_hll_type.HLL_4)
    for item in ids:
        sketch.update(item)
    estimate = sketch.get_estimate()
    elapsed = time.perf_counter() - start
    _, peak_python_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    relative_error = abs(estimate - exact) / exact
    serialized_bytes = len(sketch.serialize_compact())
    print({"lg_k": lg_k, "estimate": estimate, "relative_error": relative_error,
           "seconds": elapsed, "peak_tracemalloc_bytes": peak_python_bytes,
           "serialized_bytes": serialized_bytes})
    assert estimate > 0
```

`hll_sketch` in the Apache DataSketches Python API exposes `serialize_compact()` and `serialize_updatable()`; use the documented method rather than assuming a generic `serialize()` exists. `tracemalloc` measures Python-tracked allocations, not all native memory allocated by compiled extensions; it may under-report DataSketches memory. Serialized size is useful but is not the same as peak resident memory. Runtime depends on CPU, package version, input generation, and Python loop overhead. Do not publish a benchmark without recording hardware, OS, dependency versions, repetitions, warm-up policy, data cardinality, and whether input generation is included. HLL relative error should generally improve with larger precision, but individual trial errors need not monotonically decrease.

### 13.3 Daily sketches rolled up to weekly/monthly

Conceptually, store one compatible HLL sketch per day and merge sketches over the requested range. This pseudocode illustrates the data flow; use the target engine's documented API for persistent sketch columns.

```text
for each date D:
    daily_sketch[D] = HLL(user_id for events on D)

weekly_sketch = merge(daily_sketch[D] for D in the week)
monthly_sketch = merge(daily_sketch[D] for D in the month)
weekly_unique = estimate(weekly_sketch)
monthly_unique = estimate(monthly_sketch)
```

Do not write `SUM(daily_unique_users)` for weekly unique users. Validate by comparing the merged sketch to exact `COUNT(DISTINCT user_id)` on a manageable dataset containing users who appear on multiple days.

### 13.4 SQL sampling and approximate functions

```sql
-- DuckDB: illustrative row-sample query; validate options against your version.
SELECT *
FROM read_parquet('data/events/*.parquet')
USING SAMPLE 5 PERCENT;

-- BigQuery approximate cardinality.
SELECT APPROX_COUNT_DISTINCT(user_id) AS approx_users
FROM `project.dataset.events`;

-- BigQuery deterministic 5% bucket sample by a stable key.
-- Canonicalize the key consistently; the same hash rule/configuration repeats.
SELECT *
FROM `project.dataset.events`
WHERE MOD(MOD(FARM_FINGERPRINT(CAST(user_id AS STRING)), 100) + 100, 100) < 5;
-- This is repeatable, not automatically representative: inspect key/outcome
-- relationships and choose the sampling unit to match the question.

-- BigQuery persisted HLL++ sketch pattern (functions are engine-specific).
SELECT HLL_COUNT.MERGE(sketch) AS approx_users
FROM daily_user_sketches
WHERE event_date BETWEEN DATE '2026-10-01' AND DATE '2026-10-31';

-- Exact baseline for validation on a manageable slice.
SELECT COUNT(DISTINCT user_id) AS exact_users
FROM `project.dataset.events`
WHERE event_date BETWEEN DATE '2026-10-01' AND DATE '2026-10-07';
```

The sketch-building query and the exact baseline must use identical filters, identity semantics, and time boundaries. Exact function signatures differ among BigQuery, Snowflake, ClickHouse, Spark, and DuckDB. Some `APPROX_*` aggregates return only scalar estimates, while sketch APIs return mergeable state. Do not assume a scalar approximate count can be merged correctly.

### 13.5 Exact and approximate quantiles

```sql
-- BigQuery supports APPROX_QUANTILES with engine-specific output semantics.
SELECT APPROX_QUANTILES(latency_ms, 100)[OFFSET(95)] AS approx_p95
FROM `project.dataset.requests`;

-- DuckDB supports quantile_cont in supported versions; this is an exact
-- aggregate over the values processed by the query.
SELECT quantile_cont(latency_ms, 0.95) AS p95
FROM read_parquet('data/requests/*.parquet');
```

Function names and interpolation semantics vary. Exactness is relative to the engine's numeric type, quantile definition, and data processed. Approximate SQL aggregates may not expose mergeable sketch state; consult documentation if you need persisted rollups.

## 14. Hands-on lab: `experiments/02_sketches/`

Build a small project with these components:

```text
experiments/02_sketches/
├── README.md
├── data/                  # generated data or small fixtures
├── src/
│   ├── deterministic_sample.py
│   ├── bloom_filter.py
│   └── count_min.py
├── sql/
│   ├── sample_events.sql
│   └── distinct_users.sql
└── tests/
    ├── test_sampling.py
    ├── test_bloom.py
    └── test_count_min.py
```

### Lab A — Exact count versus HLL

1. Generate event user IDs with deliberate duplicates and known distinct cardinality.
2. Compute exact cardinality using a set or SQL `COUNT(DISTINCT)` for a dataset that fits comfortably in memory.
3. Compute HLL estimates at several precision settings.
4. Record estimate, relative error, serialized bytes, runtime, and environment details.
5. Repeat over multiple cardinalities and overlap patterns. Do not expect every trial to fall within a single standard error.
6. For the roadmap's 100-million-event exercise, run only on a suitable machine or distributed engine after the smaller tests pass. Compare exact distinct count with HLL at multiple precision settings and record elapsed time, peak resident memory (not only Python `tracemalloc`), serialized sketch size, relative error, hardware, versions, and repeated-trial results. Treat this as a proposed experiment until actually run; do not extrapolate a benchmark result from the 500,000-row example.

### Lab B — Merge daily sketches

1. Generate 30 days of events where a portion of users recur across dates.
2. Build one sketch per day.
3. Merge daily sketches for weeks and months.
4. Compare the merged estimate with exact unique users over the same full time window.
5. Demonstrate that summing daily distinct counts overcounts recurring users.

### Lab C — Quantile sketches

1. Generate a log-normal latency distribution and a distribution with a large tail.
2. Compute exact p50, p95, and p99 using NumPy.
3. Compute KLL or t-digest estimates, depending on the chosen library.
4. Compare both relative value error and rank error; note where the two tell different stories.
5. Merge sketches built from separate partitions and compare with a single sketch built over the full data.

### Lab D — Bloom false-positive rate

1. Insert a known set of keys into a Bloom filter.
2. Assert all inserted keys test positive.
3. Query a disjoint set of absent keys and measure false positives.
4. Repeat with different filter sizes and expected item counts.
5. Compare observed rates with the approximate formula and explain random variation.

### Lab E — Heavy hitters

1. Generate a Zipf-like stream, for example by sampling integer ranks with probabilities proportional to \(1/r^s\), where \(s>1\).
2. Track exact counts in a `Counter` for validation.
3. Update a count-min sketch and maintain a candidate list or heap.
4. Compare estimated frequencies with exact frequencies for top keys.
5. Repeat with a narrower sketch to observe more collision overestimation.

### Lab F — Deterministic sampling and bias

1. Sample records by a stable key using SHA-256 and a fixed bucket rule.
2. Run twice and assert membership is identical.
3. Compare the sample mean/proportion with the full-population value.
4. Introduce a selection key correlated with the target, or use systematic sampling on periodically ordered data.
5. Explain why reproducibility and representativeness are separate properties.

### Lab G — Scale plan

Do not start with 100 million rows on a laptop. First benchmark at 100 thousand and 1 million rows, observe peak RSS and runtime, and increase only if the machine has adequate memory. For large data, stream from Parquet or use DuckDB/Polars/Spark to avoid building a Python list of all IDs. Record storage layout, partitioning, row count, distinct cardinality, and engine versions. A scale claim requires an executed measurement, not extrapolation from a small test.

## 15. Exercises with solutions

### Exercise 1 — Which method?

Choose a method for each requirement:

1. Count unique users by month from daily partitions without retaining all user IDs in the monthly rollup.
2. Screen whether a key might exist in a large remote store.
3. Estimate p99 latency with a bounded-memory mergeable summary.
4. Find likely top event names in a high-volume stream.
5. Inspect a reproducible 5% sample for debugging.

**Solution:** (1) compatible HLL sketches or theta sketches if set operations are required; (2) Bloom filter followed by authoritative verification for positive results; (3) a quantile sketch selected for the required rank/value error contract; (4) frequent-items sketch or candidate tracking with count-min estimates; (5) stable hash-based sampling or a seeded DataFrame sample, with the selection unit and representativeness checked.

### Exercise 2 — Why not add daily distinct counts?

Day 1 has users `{A, B, C}` and day 2 has `{B, C, D}`. Daily distinct counts are 3 and 3.

**Solution:** the sum is 6, but the union is `{A, B, C, D}` with cardinality 4. The two repeated users are counted twice by addition. Merge compatible sketches or compute exact distinct users over the combined records.

### Exercise 3 — Sampling error scaling

A simple random sample has approximate standard error 5. If all else is comparable and sample size is multiplied by 9, what is the approximate new standard error?

**Solution:** standard error scales approximately as \(1/\sqrt{n}\), so it becomes \(5/\sqrt{9}=1.67\). This assumes the same sampling design and variance structure; it does not account for bias or clustering.

### Exercise 4 — Bloom filter semantics

A Bloom filter says a key is absent. Can the pipeline safely skip a remote lookup? What if it says the key is present?

**Solution:** under standard assumptions, a negative result means the key was not inserted and the lookup can be skipped if the filter is current and correctly built. A positive result means only “possibly present”; verify against the source of truth. Stale filters, incompatible hashes, corrupted serialization, or unsupported deletion can break operational assumptions.

### Exercise 5 — Approximation versus privacy

A team says its HLL output is anonymous because it is approximate. Is this a valid privacy claim?

**Solution:** no. Approximation is not differential privacy. A privacy claim requires an explicit threat model and a mechanism with a documented privacy guarantee, including budget/composition considerations where DP is used.

## 16. Common mistakes and production failure modes

1. **Adding daily unique counts.** Use mergeable sketches or exact distinct aggregation over the union of source records.
2. **Averaging approximate counts.** Scalar estimates discard overlap and internal sketch state; merge compatible sketches instead.
3. **Treating all sketches alike.** HLL, KLL, theta, Bloom, and count-min answer different questions and have different error semantics.
4. **Calling a sample representative because it is large.** Check coverage, selection key, unit of analysis, and correlations with the target.
5. **Using Python `hash()` for stable cross-run samples.** Use a documented stable hash and canonical encoding.
6. **Confusing sample error with bias.** Larger samples reduce random error but do not automatically remove selection bias.
7. **Using quantile value error when the contract is rank error, or vice versa.** Choose and test the right metric.
8. **Treating a count-min estimate as exact.** Under non-negative updates, collisions create overestimation; candidate identification requires a separate strategy.
9. **Treating Bloom positives as proof.** Positives must be verified if correctness depends on membership.
10. **Merging incompatible sketch blobs.** Check family, version, precision, hash scheme, seed, serialization, and dimensions.
11. **Ignoring late-arriving events or duplicate partition processing.** Define correction, replacement, and idempotency behavior explicitly.
12. **Trusting one benchmark or one random trial.** Repeat measurements, include environment details, and validate against exact baselines.
13. **Extrapolating memory from serialized bytes.** Native structures and runtime overhead can dominate.
14. **Using an approximate answer for a legally or financially exact requirement without approval.** Match the computation to the data contract and decision risk.
15. **Assuming approximation gives privacy.** Treat privacy guarantees separately.

## 17. Knowledge checkpoint and competency checklist

You are ready to continue when you can explain and demonstrate all of the following without relying on memorized slogans:

- [ ] Population, sample, sampling error, coverage/selection bias, and representativeness.
- [ ] Random, systematic, stratified, deterministic hash, reservoir, and weighted sampling; when weights are needed.
- [ ] Why standard errors often scale as \(1/\sqrt{n}\), and the assumptions behind common formulas.
- [ ] HLL registers, cardinality estimation, approximate RSE, precision/memory trade-off, and register-wise merge.
- [ ] Why daily unique counts cannot be added to obtain monthly unique users.
- [ ] KLL, t-digest, and DDSketch differences, including rank versus value error.
- [ ] Bloom filter false positives, standard no-false-negative operating assumption, and membership verification.
- [ ] Count-min overestimation under non-negative updates and why candidate tracking matters.
- [ ] Reservoir sampling's fixed memory and uniform-inclusion goal.
- [ ] DataSketches HLL, theta, KLL, and frequent-items families; when theta set operations are useful.
- [ ] A versioned sketch aggregation pipeline with late-data correction and merge compatibility.
- [ ] An error budget and an exact-vs-approximate validation plan.
- [ ] Why deterministic sampling can still be biased and why approximation is not differential privacy.

## 18. References to authoritative documentation

Use the documentation matching your deployed engine/library version; function names and serialization contracts change over time.

- Apache DataSketches, project and algorithm documentation: <https://datasketches.apache.org/> and <https://datasketches.apache.org/docs/Architecture/Overview.html>
- Apache DataSketches Python package documentation/source: <https://github.com/apache/datasketches-python>
- HyperLogLog paper, Flajolet et al., *HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm*: <https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf>
- KLL paper, Karnin, Lang, Liberty, *Optimal Quantile Approximation in Streams*: <https://arxiv.org/abs/1603.05346>
- t-digest project and documentation: <https://github.com/tdunning/t-digest>
- DDSketch paper/project: <https://arxiv.org/abs/1908.10693> and <https://github.com/DataDog/sketches-py>
- Bloom, *Space/Time Trade-offs in Hash Coding with Allowable Errors* (1970): <https://doi.org/10.1145/362686.362692>
- Count-min sketch, Cormode and Muthukrishnan: <https://dimacs.rutgers.edu/~graham/pubs/papers/cm-full.pdf>
- DuckDB sampling documentation: <https://duckdb.org/docs/stable/sql/samples>
- BigQuery approximate aggregate functions: <https://cloud.google.com/bigquery/docs/reference/standard-sql/approximate_aggregate_functions>
- BigQuery HLL++ functions: <https://cloud.google.com/bigquery/docs/reference/standard-sql/hll_functions>
- Snowflake approximate functions: <https://docs.snowflake.com/en/sql-reference/functions/approx_count_distinct>
- ClickHouse aggregate functions: <https://clickhouse.com/docs/sql-reference/aggregate-functions/reference/uniq>
- Apache Spark SQL functions: <https://spark.apache.org/docs/latest/api/sql/index.html>
- Differential privacy overview, NIST: <https://www.nist.gov/itl/applied-cybersecurity/privacy-engineering/collaboration-space/focus-areas/education-and-awareness-pets>

---

**Lesson completion rule:** do not move on until you can choose a method from the query's error contract, implement a reproducible small example, validate it against a known answer, and explain what information the method discards.
